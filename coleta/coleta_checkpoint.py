#!/usr/bin/env python3
"""SEM CHECKPOINT, NÃO GASTA — e um processo que morre não perde a coleta.

A rotação de chave NÃO é escrita aqui. Ela vem de `apify_pool.py`, portado
sem alteração do piloto italiano, e continua sendo o único dono de "quando
trocar de chave e quando não trocar". Reimplementar aquilo aqui criaria duas
verdades sobre rotação, e a segunda divergiria na primeira pressa.

O que falta lá, e é o motivo deste arquivo existir: **durabilidade**. O pool
guarda progresso em memória — `itens`, `vistos`, `feitas`, `pendentes`. Um
processo que morre no meio perde tudo o que já foi pago.

    PROCESS_CRASH != LOST_COLLECTION

A extensão entra pelo ponto que o próprio pool deixou aberto: `trabalho` é
uma função do chamador, e é dentro dela que a persistência acontece — item
salvo e checkpoint atualizado ANTES de a função retornar. Assim o pool
continua sem saber o que é um banco, e a durabilidade não depende de ele
mudar.

AS DUAS RECUSAS
---------------
    SEM_CHECKPOINT_NAO_GASTEI          não há linha aberta -> não chama o ator
    JA_CONCLUIDO_NAO_PAGAR_DUAS_VEZES  já concluiu -> não chama de novo

A segunda é a lei brasileira do `CONCLUIDOS = ("concluida","vazia")`: quem
está lá não é perguntado outra vez, porque seria pagar duas vezes.

IDENTIDADE
----------
A identidade do item é do CHAMADOR, e a regra é dura: `PLATFORM +
EXTERNAL_ID`, ou chave natural declarada. `TOKEN`, `RUN_ID`, `DATASET_ID` e
`CAPTURED_AT` nunca entram — se entrassem, retomar por outra chave
duplicaria a coleta inteira. `identidade_valida()` recusa antes de gastar.
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))   # a raiz
import _gavetas  # noqa: E402,F401 — poe as gavetas do processo no caminho
import apify_pool as ap  # noqa: E402  — dono único da rotação

PROIBIDO_NA_IDENTIDADE = ('token', 'run_id', 'runid', 'dataset', 'captured_at',
                          'capturado', 'coletado_em', 'pool_position')

SEM_CHECKPOINT = 'SEM_CHECKPOINT_NAO_GASTEI'
JA_CONCLUIDO = 'JA_CONCLUIDO_NAO_PAGAR_DUAS_VEZES'
ENCERRADO = 'CHECKPOINT_ENCERRADO_ABRIR_OUTRO'
ABERTO = 'CHECKPOINT_ABERTO'


# ── conversa com o banco, no padrão da casa: psql, sem driver novo ────
class Banco:
    def __init__(self, dsn):
        self.dsn = dsn

    def executa(self, sql, *args):
        # ⚠️ `-q` NÃO É COSMÉTICO. SEM ELE O `psql` FALA, E A FALA VIRA DADO.
        # Um `update ... returning` que não casa com linha nenhuma imprime o
        # SEU PRÓPRIO RECIBO em stdout — `UPDATE 0` — e este leitor devolvia-o
        # como se fosse uma linha de resultado. Medido na C10.6B: o `compare-
        # and-set` do checkpoint lia `[['UPDATE 0']]`, achava que tinha ganho, e
        # os DOIS processos concorrentes diziam «avancei».
        #
        #     ZERO LINHAS NÃO É UMA LINHA QUE DIZ ZERO.
        #
        # É a mesma família do defeito que `pode_gastar` já carrega escrito no
        # corpo: ler a conversa do cliente de banco como se fosse a resposta do
        # banco.
        cmd = ['psql', self.dsn, '-q', '-v', 'ON_ERROR_STOP=1',
               '-tAF', '\x1f', '-c', sql]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError(ap.redigir(r.stderr.strip())[:400])
        return [l.split('\x1f') for l in r.stdout.strip().split('\n') if l]


def hash_da_entrada(entrada):
    """sha256 da entrada REAL, canônica. Duas entradas iguais são o mesmo trabalho."""
    return hashlib.sha256(
        json.dumps(entrada, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def identidade_valida(campos):
    """A identidade não pode conter nada que mude entre execuções."""
    ruins = [c for c in campos
             if any(p in str(c).lower() for p in PROIBIDO_NA_IDENTIDADE)]
    return (not ruins), ruins


# ── o checkpoint ─────────────────────────────────────────────────────
def abrir(banco, *, target, entrada, actor, platform, pais='NAO_SEI',
          unidades_totais=0, rule_version='v1'):
    """Cria ou recupera a unidade de trabalho. Idempotente por (target, hash)."""
    h = hash_da_entrada(entrada)
    banco.executa(
        "insert into public.checkpoint_coleta (collection_target, input_hash, actor, "
        "platform, pais, started_at, updated_at, estado, unidades_totais, rule_version) "
        "values (%s, %s, %s, %s, %s, now(), now(), 'ABERTO', %s, %s) "
        "on conflict (collection_target, input_hash) do nothing"
        % tuple(_lit(x) for x in (target, h, actor, platform, pais,
                                  unidades_totais, rule_version)))
    return h


def pode_gastar(banco, target, input_hash):
    """A guarda. Devolve (pode, porque, checkpoint_id, retomar_de)."""
    # Campo final vazio some no recorte do psql. Em vez de contar colunas,
    # a consulta devolve um marcador que nunca e vazio.
    r = banco.executa(
        # `pode::text` devolve 'true'/'false' e nao 't'/'f' — a primeira versao
        # comparou com 't' e a guarda RECUSOU tudo. Falhar fechado e a direcao
        # certa para uma trava de gasto, mas continua sendo defeito.
        "select case when pode then 't' else 'f' end, porque, "
        "coalesce(checkpoint_id::text,'-'), "
        "coalesce(retomar_de,'-') from public.pode_gastar(%s, %s)"
        % (_lit(target), _lit(input_hash)))
    if not r or len(r[0]) < 4:
        return False, SEM_CHECKPOINT, None, None
    pode, porque, cid, retomar = r[0][:4]
    return (pode == 't', porque,
            (int(cid) if cid not in ('-', '') else None),
            (retomar if retomar not in ('-', '') else None))


def unidades_pendentes(banco, checkpoint_id, unidades):
    """Retoma: as unidades já feitas não voltam a ser pagas."""
    r = banco.executa(
        "select coalesce(ultima_unidade,'-'), unidades_feitas::text "
        "from public.checkpoint_coleta where id = %d" % checkpoint_id)
    if not r or len(r[0]) < 2:
        return list(unidades)
    ultima, feitas = r[0][0], int(r[0][1])
    if ultima == '-' or ultima not in unidades:
        return list(unidades)[feitas:] if feitas else list(unidades)
    return list(unidades)[unidades.index(ultima) + 1:]


def _lit(v):
    if v is None:
        return 'null'
    if isinstance(v, bool):
        return 'true' if v else 'false'
    if isinstance(v, (int, float)):
        return str(v)
    return "'" + str(v).replace("'", "''") + "'"


# ── o caminho produtivo ──────────────────────────────────────────────
def coletar(banco, *, target, entrada, actor, platform, unidades, trabalho,
            identidade, persistir, campos_da_identidade, pais='NAO_SEI',
            env=None, teto_itens=None, rule_version='v1'):
    """O ÚNICO caminho até uma chamada paga.

    `trabalho(unidade, token) -> (itens, estado)` e `identidade(item) -> chave`
    são do chamador, exatamente como no pool. `persistir(itens, unidade)` é o
    que este arquivo acrescenta: ele roda ANTES de a unidade ser dada por
    feita, e é ele que torna a retomada possível.
    """
    ok, ruins = identidade_valida(campos_da_identidade)
    if not ok:
        return {'STATE': 'IDENTIDADE_INVALIDA', 'CAMPOS_PROIBIDOS': ruins,
                'PAID_CALLS': 0,
                'PORQUE': 'TOKEN, RUN_ID, DATASET_ID e CAPTURED_AT não entram na '
                          'identidade: retomar por outra chave duplicaria a coleta'}

    h = abrir(banco, target=target, entrada=entrada, actor=actor, platform=platform,
              pais=pais, unidades_totais=len(unidades), rule_version=rule_version)
    pode, porque, cid, _ = pode_gastar(banco, target, h)
    if not pode:
        return {'STATE': porque, 'PAID_CALLS': 0, 'CHECKPOINT_ID': cid,
                'ITEMS': [], 'PORQUE': porque}

    pendentes = unidades_pendentes(banco, cid, list(unidades))
    banco.executa("update public.checkpoint_coleta set estado='EM_CURSO', "
                  "updated_at=now() where id=%d" % cid)

    chamadas = {'n': 0}
    posicao = {'tokens': []}

    def trabalho_duravel(unidade, token):
        chamadas['n'] += 1
        if token not in posicao['tokens']:
            posicao['tokens'].append(token)
        pos = posicao['tokens'].index(token) + 1
        itens, estado = trabalho(unidade, token)
        # Persistir ANTES de dar a unidade por feita. Se o processo morrer
        # entre as duas coisas, a unidade volta a ser tentada — o que é
        # certo. Morrer DEPOIS de dar por feita e ANTES de salvar seria o
        # oposto, e é isso que esta ordem impede.
        if estado not in ap.ROTACIONAM and estado not in ap.NAO_ROTACIONAM:
            n = persistir(itens or [], unidade)
            banco.executa(
                "update public.checkpoint_coleta set unidades_feitas = unidades_feitas + 1, "
                "itens_persistidos = itens_persistidos + %d, ultima_unidade = %s, "
                "pool_position = %d, updated_at = now() where id = %d"
                % (int(n or 0), _lit(unidade), pos, cid))
        else:
            banco.executa("update public.checkpoint_coleta set pool_position=%d, "
                          "updated_at=now() where id=%d" % (pos, cid))
        return itens, estado

    r = ap.executar_com_pool(pendentes, trabalho_duravel, identidade=identidade,
                             env=env, teto_itens=teto_itens)

    estado = {'DONE': 'CONCLUIDO', 'STOPPED': 'PARCIAL',
              ap.POOL_EMPTY: 'FALHOU'}.get(r['STATE'], 'PARCIAL')
    banco.executa(
        "update public.checkpoint_coleta set estado=%s, updated_at=now(), "
        "finished_at=case when %s='CONCLUIDO' then now() else null end, motivo=%s "
        "where id=%d" % (_lit(estado), _lit(estado), _lit(r['STATE']), cid))

    r['CHECKPOINT_ID'] = cid
    r['INPUT_HASH'] = h
    r['PAID_CALLS'] = chamadas['n']
    r['CHECKPOINT_STATE'] = estado
    return r


if __name__ == '__main__':
    print('SEM_CHECKPOINT_NAO_GASTEI é uma trava, não um comentário.')
    print('Rotação de chave: ferramentas/apify_pool.py (portado do piloto italiano).')


# ══════════════════════════════════════════════════════════════════════════
# A ESTRADA OFICIAL — mesma tabela, mesmo dono, sem o pool de chaves
# ══════════════════════════════════════════════════════════════════════════
# `coletar()` acima é a estrada PAGA: ele passa por `ap.executar_com_pool`, que
# roda chave a chave e classifica falha de token. Uma rota de API oficial não tem
# pool para rodar — tem UMA chave e uma quota — e forçá-la por dentro do pool só
# para poder dizer «reutilizei código» seria emprestar a semântica errada.
#
#     REUTILIZAR O DONO NÃO É REUTILIZAR UMA FUNÇÃO
#     QUE TEM OUTRA SEMÂNTICA.
#
# Então a operação genérica nasce AQUI, ao lado da que já existia, sobre a MESMA
# tabela e com as MESMAS travas. O que muda é só quem executa a unidade.
#
# A ORDEM É A LEI, E ELA TEM UM NOME
# -----------------------------------
#     PERSIST FIRST, THEN ADVANCE CHECKPOINT.
#
# `unidades_feitas` e `itens_persistidos` só sobem DEPOIS que `persistir()`
# devolveu. Se o processo morrer entre buscar e salvar, o checkpoint continua
# apontando para antes — e a próxima execução refaz a unidade. Refazer é barato;
# pular o que ninguém salvou é perda silenciosa.
#
#     SEEN NÃO É PERSISTED.
#     PROCESS_CRASH NÃO É LOST_COLLECTION.

UNIDADE_FEITA = 'UNIDADE_FEITA'
UNIDADE_VAZIA = 'UNIDADE_VAZIA'
UNIDADE_FALHOU = 'UNIDADE_FALHOU'


def executar_unidade(banco, *, target, entrada, actor, platform, unidade,
                     trabalho, persistir, campos_da_identidade,
                     pais='NAO_SEI', rule_version='v1'):
    """UMA unidade de trabalho da rota oficial, com checkpoint de verdade.

    `trabalho(unidade) -> (itens, estado)` não recebe token: quem tem chave é o
    executor da rota, e ele a guarda. `persistir(itens, unidade) -> n` roda ANTES
    de o checkpoint avançar, e o `n` que ele devolve é o que entra em
    `itens_persistidos` — o que foi SALVO, nunca o que voltou da API.

    Devolve um dicionário com `STATE`, `CHECKPOINT_ID`, `ITENS_PERSISTIDOS`.
    """
    ok, ruins = identidade_valida(campos_da_identidade)
    if not ok:
        return {'STATE': 'IDENTIDADE_INVALIDA', 'CAMPOS_PROIBIDOS': ruins,
                'ITENS_PERSISTIDOS': 0,
                'PORQUE': 'TOKEN, RUN_ID, DATASET_ID e CAPTURED_AT não entram na '
                          'identidade: retomar por outra chave duplicaria a coleta'}

    h = abrir(banco, target=target, entrada=entrada, actor=actor, platform=platform,
              pais=pais, unidades_totais=1, rule_version=rule_version)
    pode, porque, cid, _ultima = pode_gastar(banco, target, h)
    if not pode:
        # `JA_CONCLUIDO_NAO_PAGAR_DUAS_VEZES` chegando aqui é a trava funcionando:
        # esta MESMA unidade já foi feita. Uma janela NOVA tem outra `entrada`,
        # logo outro `input_hash`, logo outro checkpoint — e não colide.
        return {'STATE': porque, 'CHECKPOINT_ID': cid, 'ITENS_PERSISTIDOS': 0,
                'INPUT_HASH': h, 'PORQUE': porque}

    banco.executa("update public.checkpoint_coleta set estado='EM_CURSO', "
                  "updated_at=now() where id=%d" % int(cid))
    try:
        itens, estado = trabalho(unidade)
    except Exception as e:                                        # noqa: BLE001
        banco.executa("update public.checkpoint_coleta set estado='PARCIAL', "
                      "motivo=%s, updated_at=now() where id=%d"
                      % (_lit(('%s: %s' % (type(e).__name__, e))[:400]), int(cid)))
        raise

    # ── AQUI, E SÓ AQUI, O CHECKPOINT ANDA ────────────────────────────────
    n = persistir(itens or [], unidade)
    banco.executa(
        "update public.checkpoint_coleta set unidades_feitas = unidades_feitas + 1, "
        "itens_persistidos = itens_persistidos + %d, ultima_unidade = %s, "
        "estado = 'CONCLUIDO', finished_at = now(), updated_at = now() "
        "where id = %d" % (int(n or 0), _lit(str(unidade)), int(cid)))
    return {'STATE': UNIDADE_FEITA if n else UNIDADE_VAZIA,
            'CHECKPOINT_ID': cid, 'INPUT_HASH': h,
            'ITENS_PERSISTIDOS': int(n or 0), 'EXECUTOR_STATE': estado}


def conteudo_persistido(banco, *, platform, external_ids):
    """Quais destes `external_id` JÁ ESTÃO SALVOS em `public.conteudo`?

    Esta é a resposta canônica para «o que é CONHECIDO» na parada incremental —
    e ela é sobre o que foi SALVO, não sobre o que foi visto.

        «VI NA API» NÃO TORNA UM VÍDEO CONHECIDO.

    Se o processo morrer depois de ver e antes de salvar, o id NÃO aparece aqui,
    e a próxima execução o reencontra. É exatamente o que se quer.
    """
    ids = [str(i) for i in external_ids if i]
    if not ids:
        return set()
    lista = ', '.join(_lit(i) for i in ids)
    r = banco.executa(
        # A coluna é `plataforma`, não `platform`. Medido no schema aplicado, não
        # decorado: escrever o nome errado aqui daria zero CONHECIDOS em silêncio,
        # e a coleta refaria tudo todo dia sem ninguém perceber.
        "select c.content_id from public.conteudo c "
        "join public.canal k on k.id = c.canal_id "
        "where k.plataforma = %s and c.content_id in (%s)"
        % (_lit(platform.upper()), lista))
    return {linha[0] for linha in r if linha and linha[0]}


# ══════════════════════════════════════════════════════════════════════════
# A EXECUÇÃO DURÁVEL — RUN, CHECKPOINT E RASTRO NA MESMA ORDEM
# ══════════════════════════════════════════════════════════════════════════
# A C10.6 provou que a cadeia de Reel sobrevive a um `os._exit()`: o RAW
# preservado é reusado, o retry consulta `leis/falhas.py`, o parcial não é
# publicado. O que ela NÃO provou, e por isso ficou `PARTIAL`:
#
#     RUN_STATE_PERSISTENCE = NOT_IMPLEMENTED
#
# O processo seguinte não sabia, de forma durável, que houve uma execução
# anterior, em que etapa ela morreu, qual tentativa era, nem qual foi o último
# artefato bom. Sabia ler a GAVETA — e uma gaveta diz o que existe, nunca o que
# aconteceu.
#
#     UM FICHEIRO NO DISCO É UM RESULTADO. NÃO É UMA EXECUÇÃO.
#
# TRÊS GRÃOS, TRÊS DONOS, UMA ORDEM
# -----------------------------------
#     RUN          `public.collection_run`     UMA execução de um ator
#     CHECKPOINT   `public.checkpoint_coleta`  a UNIDADE DE TRABALHO
#     RASTRO       `public.etapa_da_corrida`   uma passagem de etapa numa
#                                              tentativa de uma RUN
#
# A migration 016 escreve a relação com todas as letras: «o checkpoint é a
# UNIDADE DE TRABALHO, e ela pode atravessar várias execuções (...). Por isso
# collection_run aponta para cá, e não o contrário.»
#
#     RUN != CHECKPOINT.
#     UM CHECKPOINT, VÁRIAS RUNS. A DIREÇÃO CANÔNICA DA HISTÓRIA É
#     `collection_run.checkpoint_id`.
#
# `checkpoint_coleta.run_id` existe no schema e NINGUÉM o escreve — medido no
# HEAD desta missão. Escrevê-lo seria dizer que um checkpoint tem UMA run, que
# é o contrário do que a 016 declara. Fica como está: nulo, e declarado nulo.
#
# POR QUE ISTO VIVE AQUI
# -----------------------
# Este ficheiro já é o dono da durabilidade — `PROCESS_CRASH != LOST_COLLECTION`
# é a primeira linha dele. O rastro tem dono próprio (`medidas/rastro_da_coleta`)
# e é ELE que escreve `etapa_da_corrida`: aqui só se chama.
#
#     ONE CONCEPT → ONE OWNER. CHAMAR O DONO NÃO É VIRAR O DONO.
#
# O QUE ESTE FICHEIRO NÃO PASSA A SER
# -------------------------------------
# Não passa a cunhar `RUN_ID`. Ele REGISTA o que o chamador canônico já cunhou.
# Registar não é cunhar, e a diferença importa: um `run_id` inventado aqui seria
# uma execução que ninguém pediu.
import time as _time

CORRIDA_ABERTA = 'rodando'
CORRIDA_CONCLUIDA = 'concluida'
CORRIDA_VAZIA = 'vazia'
CORRIDA_PARCIAL = 'parcial'
CORRIDA_FALHOU = 'falhou'
#: Os cinco nomes são os do enum `run_status` da migration 001. Escrevê-los aqui
#: é uma cópia — e uma cópia que ninguém obriga a concordar acaba a discordar.
#: Por isso `corrida_estados_do_banco()` existe: ela pergunta ao banco.
CORRIDA_ESTADOS = (CORRIDA_ABERTA, CORRIDA_CONCLUIDA, CORRIDA_VAZIA,
                   CORRIDA_PARCIAL, CORRIDA_FALHOU)


def corrida_estados_do_banco(banco):
    """O vocabulário de `run_status`, lido do banco. A cópia acima confere-se."""
    return tuple(l[0] for l in banco.executa(
        "select enumlabel from pg_enum e join pg_type t on t.oid = e.enumtypid "
        "where t.typname = 'run_status' order by enumsortorder") if l and l[0])


def abrir_corrida(banco, *, run_id, platform, actor, rule_version='v1',
                  actor_version=None, source_country='NAO_SEI', mission=None,
                  capture_method=None, checkpoint_id=None, entrada=None):
    """A execução passa a existir no banco ANTES do trabalho. → run_id.

    `on conflict do nothing` torna a re-entrada barata e NÃO cala nada: um
    `run_id` repetido é a MESMA execução a ser reaberta, e reabrir uma execução
    não é começar outra. Quem quer outra execução cunha outro `run_id`.
    """
    colunas = {
        'run_id': run_id, 'platform': platform, 'actor': actor,
        'actor_version': actor_version, 'mission': mission,
        'source_country': source_country, 'rule_version': rule_version,
        'capture_method': capture_method, 'checkpoint_id': checkpoint_id,
        'input': (json.dumps(entrada, sort_keys=True, ensure_ascii=False)
                  if entrada is not None else None),
    }
    nomes = [k for k, v in colunas.items() if v is not None]
    banco.executa(
        "insert into public.collection_run (%s, started_at, status) "
        "values (%s, now(), 'rodando') on conflict (run_id) do nothing"
        % (', '.join(nomes),
           ', '.join(_lit(colunas[k]) + ('::jsonb' if k == 'input' else '')
                     for k in nomes)))
    return run_id


def ligar_ao_checkpoint(banco, *, run_id, checkpoint_id):
    """`collection_run.checkpoint_id` — a direção canônica da 016.

    De qual unidade de trabalho esta execução nasceu. Várias execuções podem
    apontar para o mesmo checkpoint, e é isso que uma retomada é.
    """
    banco.executa("update public.collection_run set checkpoint_id = %d "
                  "where run_id = %s" % (int(checkpoint_id), _lit(run_id)))


def fechar_corrida(banco, *, run_id, status, error=None, item_count_raw=None,
                   cost_usd=None):
    """A execução acaba. `finished_at` só entra quando ela realmente acabou.

    `rodando` não fecha nada: é o estado de quem está de pé. Passá-lo aqui é
    erro do chamador e levanta, porque uma execução «fechada como aberta» é
    exactamente o que faz um crash parecer um sucesso.
    """
    if status == CORRIDA_ABERTA:
        raise ValueError('fechar_corrida com `rodando` não fecha execução '
                         'nenhuma. Um estado de quem está de pé não é um fecho.')
    if status not in CORRIDA_ESTADOS:
        raise ValueError('status fora do enum `run_status`: %s' % status)
    extra = []
    if error is not None:
        extra.append('error = %s' % _lit(str(error)[:400]))
    if item_count_raw is not None:
        extra.append('item_count_raw = %d' % int(item_count_raw))
    if cost_usd is not None:
        extra.append('cost_usd = %s' % _lit(cost_usd))
    banco.executa(
        "update public.collection_run set status = %s::run_status, "
        "finished_at = now()%s where run_id = %s"
        % (_lit(status), (', ' + ', '.join(extra)) if extra else '',
           _lit(run_id)))


def corridas_do_checkpoint(banco, checkpoint_id):
    """Todas as execuções que nasceram desta unidade de trabalho, em ordem.

    É aqui que a retomada se vê: a run que morreu continua na lista, com o seu
    estado, ao lado da que a substituiu.

        A RUN MORTA NÃO SOME. ELA É A EVIDÊNCIA.
    """
    return [{'RUN_ID': l[0], 'STATUS': l[1], 'STARTED_AT': l[2],
             'FINISHED_AT': None if l[3] == '-' else l[3],
             'ERROR': None if l[4] == '-' else l[4]}
            for l in banco.executa(
                "select run_id, status::text, started_at::text, "
                "coalesce(finished_at::text,'-'), coalesce(error,'-') "
                "from public.collection_run where checkpoint_id = %d "
                "order by started_at, id" % int(checkpoint_id))
            if l and l[0]]


def estado_duravel(banco, *, target, entrada):
    """TUDO o que um processo NOVO consegue saber, lendo só o banco.

    Nenhuma linha daqui vem de RAM, de ficheiro temporário, de variável global
    nem de lock. É uma pergunta ao Postgres, e a resposta é o que o processo
    anterior deixou escrito antes de morrer.

    Devolve `None` em `CHECKPOINT` quando nunca houve trabalho — que é
    diferente de «houve e falhou».

        SEM LINHA NÃO É FALHA. É AUSÊNCIA, E ELA TEM NOME PRÓPRIO.
    """
    import rastro_da_coleta as rastro
    h = hash_da_entrada(entrada)
    linhas = banco.executa(
        "select id::text, estado, coalesce(ultima_unidade,'-'), "
        "unidades_feitas::text, itens_persistidos::text, coalesce(motivo,'-') "
        "from public.checkpoint_coleta where collection_target = %s "
        "and input_hash = %s" % (_lit(target), _lit(h)))
    if not linhas or not linhas[0] or not linhas[0][0]:
        return {'INPUT_HASH': h, 'CHECKPOINT': None, 'CORRIDAS': [],
                'ETAPAS_PENDURADAS': [], 'PASSAGENS': {},
                'PORQUE': SEM_CHECKPOINT}
    l = linhas[0]
    cid = int(l[0])
    corridas = corridas_do_checkpoint(banco, cid)
    penduradas = [e for e in rastro.etapas_penduradas(banco)
                  if e['RUN_ID'] in {c['RUN_ID'] for c in corridas}]
    passagens = {c['RUN_ID']: rastro.passagens(banco, run_id=c['RUN_ID'])
                 for c in corridas}
    return {
        'INPUT_HASH': h,
        'CHECKPOINT': {'ID': cid, 'ESTADO': l[1],
                       'ULTIMA_UNIDADE': None if l[2] == '-' else l[2],
                       'UNIDADES_FEITAS': int(l[3]),
                       'ITENS_PERSISTIDOS': int(l[4]),
                       'MOTIVO': None if l[5] == '-' else l[5]},
        'CORRIDAS': corridas,
        'ETAPAS_PENDURADAS': penduradas,
        'PASSAGENS': passagens,
        'PORQUE': ABERTO,
    }


# ── QUEM SABE ONDE AS ETAPAS COMEÇAM NÃO É QUEM SABE ESCREVÊ-LAS ─────────
# A cadeia de Reel sabe onde estão os seus degraus: ela é que os tem. O que ela
# não sabe — e não pode saber sem virar outra coisa — é que existe um Postgres,
# uma `etapa_da_corrida` e uma tentativa a numerar.
#
#     O RELATOR É A JUNTA ENTRE AS DUAS.
#
# A cadeia recebe um objeto e diz «abri FETCH», «fechei FETCH em PASS». Quem o
# escreve no banco é o dono do rastro. Quem não recebe relator nenhum continua a
# correr exactamente como antes — e é por isso que os 47 testes da cadeia não
# precisam de saber que isto existe.
#
#     INSTRUMENTAR NÃO PODE SER CONDIÇÃO PARA FUNCIONAR.
class RelatorDeEtapas:
    """Escreve as passagens de UMA corrida, pelo dono do rastro.

    Não decide vocabulário, não decide estado, não decide tentativa a partir do
    nada: a tentativa é MEDIDA no banco, e o estado vem de quem correu a etapa.
    """

    def __init__(self, banco, *, run_id, checkpoint_id=None, actor=None,
                 actor_version=None, source_id=None, route_class_id=None,
                 policy_version=None):
        import rastro_da_coleta as rastro
        self._r, self.banco, self.run_id = rastro, banco, run_id
        self.checkpoint_id = checkpoint_id
        self.actor, self.actor_version = actor, actor_version
        self.source_id, self.route_class_id = source_id, route_class_id
        self.policy_version = policy_version
        self.ultimo_bom = None
        self.anterior = None
        self.abertas = []

    def abrir(self, etapa, **kw):
        """→ o `id` da linha. A etapa passa a existir ANTES do trabalho."""
        t = kw.pop('tentativa', None)
        if t is None:
            t = self._r.proxima_tentativa(self.banco, run_id=self.run_id, etapa=etapa)
        linha = self._r.abrir_etapa(
            self.banco, run_id=self.run_id, etapa=etapa, tentativa=t,
            edge_from=kw.pop('edge_from', self.anterior),
            actor=kw.pop('actor', self.actor), actor_version=self.actor_version,
            source_id=self.source_id, route_class_id=self.route_class_id,
            policy_version=self.policy_version,
            checkpoint_before=(str(self.checkpoint_id)
                               if self.checkpoint_id is not None else None),
            last_good_artifact=self.ultimo_bom, **kw)
        self.abertas.append((linha, etapa, t))
        return linha

    def fechar(self, linha, estado, **kw):
        """A MESMA linha fecha. `LAST_GOOD_ARTIFACT` novo sobe e fica."""
        bom = kw.pop('last_good_artifact', None)
        if bom:
            self.ultimo_bom = bom
        etapa = next((e for (i, e, _t) in self.abertas if i == linha), None)
        fora = self._r.fechar_etapa(
            self.banco, linha_id=linha, etapa=etapa, estado=estado,
            last_good_artifact=self.ultimo_bom,
            checkpoint_after=(str(self.checkpoint_id)
                              if self.checkpoint_id is not None else None), **kw)
        if etapa:
            self.anterior = etapa
        self.abertas = [x for x in self.abertas if x[0] != linha]
        return fora


class _SemRelato:
    """O relator de quem não pediu rastro. Cada chamada é um `no-op`.

    Existe para que a cadeia tenha UM caminho de código, e não dois com um `if`
    em cada degrau. Um `if` por degrau é onde um degrau fica de fora.
    """

    def abrir(self, etapa, **kw):
        return None

    def fechar(self, linha, estado, **kw):
        return None


SEM_RELATO = _SemRelato()


# ── O DRIVER GENÉRICO ─────────────────────────────────────────────────────
# Ele não sabe o que é um Reel, um vídeo, uma legenda ou uma API. Sabe que há
# etapas, que cada uma pode falhar, e em que ordem as coisas duráveis andam:
#
#     ABRE RUN → ABRE CHECKPOINT → LIGA → [ ABRE ETAPA → TRABALHO →
#     PERSISTE → FECHA ETAPA ] × n → AVANÇA CHECKPOINT → FECHA RUN
#
# `PERSIST FIRST, THEN ADVANCE CHECKPOINT` continua a valer, e agora tem uma
# irmã: `ABRIR A ETAPA ANTES DO TRABALHO`. Sem ela, quem morre a meio não
# deixa linha — e uma morte sem linha é indistinguível de uma corrida que nunca
# começou.
# ⚠️ AQUI VIVEU UM SEGUNDO DRIVER, E ELE FOI RETIRADO ANTES DE NASCER PARA A
# PRODUÇÃO. `executar_etapas` recebia uma LISTA de etapas; `executar_unidade_duravel`
# recebe UMA função que relata as suas. Os dois abriam RUN, ligavam checkpoint,
# escreviam rastro e fechavam — a mesma sequência, escrita duas vezes.
#
# Zero chamadores, e mesmo assim perigoso: uma mutação desta missão trocou o
# bloco de abertura e a suíte não caiu, porque tinha trocado o do driver que
# ninguém chama. Duas cópias da mesma ordem divergem, e a que diverge em
# silêncio é sempre a que ninguém corre.
#
#     ONE CONCEPT → ONE OWNER — E UM OWNER COM DUAS CÓPIAS DA MESMA ORDEM
#     JÁ É DOIS.
#
# A forma que ficou é a que a cadeia real precisa: ela não sabe quantos degraus
# existem, e por isso não os pode listar de fora.


def executar_unidade_duravel(banco, *, run_id, target, entrada, actor, platform,
                             trabalho, campos_da_identidade, unidade=None,
                             pais='NAO_SEI', rule_version='v1',
                             actor_version=None, source_country='NAO_SEI',
                             mission=None, source_id=None, route_class_id=None,
                             policy_version=None):
    """UMA unidade de trabalho durável, com a cadeia a relatar as suas etapas.

    `trabalho(relator, contexto) -> dict` é do chamador. Ele recebe um
    `RelatorDeEtapas` e usa-o nos degraus que REALMENTE atravessa. Este ficheiro
    não sabe quantos degraus existem nem como se chamam — quem sabe é quem corre.

        NÃO SE FABRICA ETAPA. QUEM NÃO ATRAVESSOU NÃO RELATA.

    A ORDEM DURÁVEL, E ELA NÃO NEGOCEIA
    -------------------------------------
        ABRE CHECKPOINT → ABRE RUN → LIGA → TRABALHO (que relata) →
        PERSISTE → AVANÇA CHECKPOINT → FECHA RUN

    Um `os._exit()` em qualquer ponto deixa no banco exactamente o que já tinha
    sido escrito, e nada do que não tinha. É essa a prova.
    """
    ok, ruins = identidade_valida(campos_da_identidade)
    if not ok:
        return {'STATE': 'IDENTIDADE_INVALIDA', 'CAMPOS_PROIBIDOS': ruins,
                'PORQUE': 'TOKEN, RUN_ID, DATASET_ID e CAPTURED_AT não entram na '
                          'identidade: retomar por outra chave duplicaria a coleta'}

    h = abrir(banco, target=target, entrada=entrada, actor=actor,
              platform=platform, pais=pais, unidades_totais=1,
              rule_version=rule_version)
    pode, porque, cid, _ = pode_gastar(banco, target, h)
    if not pode:
        return {'STATE': porque, 'CHECKPOINT_ID': cid, 'INPUT_HASH': h,
                'RUN_ID': None, 'PORQUE': porque}

    abrir_corrida(banco, run_id=run_id, platform=platform, actor=actor,
                  actor_version=actor_version, source_country=source_country,
                  rule_version=rule_version, mission=mission,
                  checkpoint_id=cid, entrada=entrada)
    ligar_ao_checkpoint(banco, run_id=run_id, checkpoint_id=cid)
    banco.executa("update public.checkpoint_coleta set estado='EM_CURSO', "
                  "updated_at=now() where id=%d" % int(cid))

    relator = RelatorDeEtapas(banco, run_id=run_id, checkpoint_id=cid,
                              actor=actor, actor_version=actor_version,
                              source_id=source_id, route_class_id=route_class_id,
                              policy_version=policy_version)
    contexto = {'RUN_ID': run_id, 'CHECKPOINT_ID': cid, 'INPUT_HASH': h,
                'UNIDADE': unidade}
    try:
        saida = trabalho(relator, dict(contexto)) or {}
    except Exception as e:                                        # noqa: BLE001
        # ⚠️ UMA ETAPA ABERTA QUE NINGUÉM FECHOU É UMA LINHA A MENTIR.
        # Ela diz `RUNNING` para sempre, e um processo VIVO não pode deixar
        # isso atrás de si: só a morte de processo tem esse direito, porque só
        # ela não teve como fechar.
        for linha, nome, _t in list(relator.abertas):
            try:
                relator.fechar(linha, 'FAIL', canonical_state='UNKNOWN_ERROR',
                               error_class=type(e).__name__, error_message=str(e))
            except Exception:                                     # noqa: BLE001
                pass
        banco.executa(
            "update public.checkpoint_coleta set estado='PARCIAL', motivo=%s, "
            "updated_at=now() where id=%d"
            % (_lit(('%s: %s' % (type(e).__name__, e))[:400]), int(cid)))
        fechar_corrida(banco, run_id=run_id, status=CORRIDA_FALHOU,
                       error='%s: %s' % (type(e).__name__, e))
        raise

    # ── PERSIST FIRST, THEN ADVANCE CHECKPOINT ──────────────────────────────
    n = int(saida.get('PERSISTIU') or 0)
    falhou = bool(saida.get('FALHOU'))
    if falhou:
        banco.executa(
            "update public.checkpoint_coleta set estado='PARCIAL', motivo=%s, "
            "itens_persistidos = itens_persistidos + %d, updated_at=now() "
            "where id=%d" % (_lit(str(saida.get('PORQUE') or 'ETAPA_FALHOU')[:400]),
                             n, int(cid)))
        fechar_corrida(banco, run_id=run_id,
                       status=CORRIDA_PARCIAL if n else CORRIDA_FALHOU,
                       error=str(saida.get('PORQUE') or '')[:400],
                       item_count_raw=n)
    else:
        avanco = avancar_checkpoint(
            banco, checkpoint_id=cid, itens=n,
            unidade=str(unidade if unidade is not None else target))
        fechar_corrida(banco, run_id=run_id,
                       status=CORRIDA_CONCLUIDA if n else CORRIDA_VAZIA,
                       item_count_raw=n)
    fora = dict(saida)
    fora.update({'STATE': ('ETAPA_FALHOU' if falhou else
                           UNIDADE_FEITA if n else UNIDADE_VAZIA),
                 'RUN_ID': run_id, 'CHECKPOINT_ID': cid, 'INPUT_HASH': h,
                 'ITENS_PERSISTIDOS': n,
                 'CHECKPOINT_ADVANCE': ('NAO_APLICAVEL' if falhou else avanco),
                 'LAST_GOOD_ARTIFACT': relator.ultimo_bom})
    return fora


# ── O AVANÇO É DE UM SÓ, E QUEM DECIDE ISSO É O POSTGRES ───────────────
# MEDIDO NA C10.6B, com dois processos de verdade contra um Postgres de verdade,
# vinte rodadas: **as vinte** avançaram o checkpoint DUAS vezes. `pode_gastar` é
# uma função `stable` — uma leitura pura — e entre a leitura e a escrita não há
# nada. Os dois liam «podes», os dois faziam, os dois somavam `+1`, e um
# checkpoint de UMA unidade acabava a dizer `unidades_feitas = 2`.
#
#     LER «PODES» NÃO É TER TOMADO.
#     ENTRE A PERGUNTA E A ESCRITA CABE OUTRO PROCESSO INTEIRO.
#
# A correção não é um lock novo nem uma coluna nova: é fazer a pergunta e a
# escrita na MESMA instrução. `where estado <> 'CONCLUIDO'` é o `compare-and-set`
# que a tabela já permitia — quem chegar segundo não escreve, e SABE que não
# escreveu, porque o `returning` volta vazio.
#
# O QUE ISTO NÃO CONSERTA, E É PRECISO DIZÊ-LO
# ----------------------------------------------
# Os dois processos continuam a FAZER o trabalho. O que deixa de acontecer é o
# checkpoint MENTIR sobre quantas unidades foram feitas. Impedir o trabalho
# duplicado exigiria saber se o dono anterior ainda está vivo — e `EM_CURSO` não
# distingue «alguém está a correr» de «alguém morreu a correr». Essa distinção
# precisa de contrato novo (lease/heartbeat) e está declarada como tal.
JA_AVANCADO = 'JA_CONCLUIDO_POR_OUTRA_CORRIDA'
AVANCOU = 'AVANCOU'


def avancar_checkpoint(banco, *, checkpoint_id, itens=0, unidade=None):
    """Uma unidade feita, contada UMA vez. -> `AVANCOU` ou `JA_AVANCADO`.

    A condição e a escrita viajam juntas. Duas chamadas concorrentes: uma
    escreve, a outra volta de mãos vazias — e devolver de mãos vazias é uma
    resposta, não um erro.
    """
    r = banco.executa(
        "update public.checkpoint_coleta set unidades_feitas = unidades_feitas + 1, "
        "itens_persistidos = itens_persistidos + %d, ultima_unidade = %s, "
        "estado = 'CONCLUIDO', finished_at = now(), updated_at = now() "
        "where id = %d and estado <> 'CONCLUIDO' returning unidades_feitas::text"
        % (int(itens or 0), _lit(unidade), int(checkpoint_id)))
    return AVANCOU if (r and r[0] and r[0][0]) else JA_AVANCADO


# ══════════════════════════════════════════════════════════════════════════
# A EXECUÇÃO DURÁVEL SEM UNIDADE RETOMÁVEL — E POR QUE ELA PRECISA DE EXISTIR
# ══════════════════════════════════════════════════════════════════════════
# `executar_unidade_duravel` exige uma UNIDADE DE TRABALHO: um `target` e uma
# `entrada` que identifiquem o que se está a fazer, para que outra execução
# possa retomá-lo. Nem toda capacidade tem isso.
#
#     «RESOLVER UM CANAL PELO NOME» NÃO TEM METADE FEITA.
#     OU RESOLVEU, OU NÃO RESOLVEU.
#
# Criar um checkpoint para uma operação atómica só para poder dizer
# `CHECKPOINT = YES` seria fabricar retomada onde não há nada a retomar — e um
# checkpoint `CONCLUIDO` numa operação que se deve poder repetir trancá-la-ia
# para sempre com `JA_CONCLUIDO_NAO_PAGAR_DUAS_VEZES`.
#
#     TRÊS COISAS DIFERENTES, E SÓ A PRIMEIRA É SEMPRE VERDADE:
#         RUN_REQUIRED            toda execução real existiu
#         STAGE_TRACE_REQUIRED    toda etapa atravessada deixa rasto
#         CHECKPOINT_REQUIRED     só quando há unidade retomável
class Execucao:
    """Uma execução durável aberta: a RUN existe, e há por onde relatar.

    Devolvida por `abrir_execucao`. `fechar()` fecha a RUN com o estado que o
    chamador mediu — e nunca com `rodando`, que é o estado de quem está de pé.
    """

    def __init__(self, banco, *, run_id, checkpoint_id=None, relator=None,
                 input_hash=None):
        self.banco, self.run_id = banco, run_id
        self.checkpoint_id, self.input_hash = checkpoint_id, input_hash
        self.relator = relator
        self.fechada = False

    def fechar(self, status, **kw):
        if self.fechada:
            return
        fechar_corrida(self.banco, run_id=self.run_id, status=status, **kw)
        self.fechada = True

    def avancar(self, *, itens=0, unidade=None):
        """Só faz sentido quando há checkpoint. Sem ele, não há o que avançar."""
        if self.checkpoint_id is None:
            return None
        return avancar_checkpoint(self.banco, checkpoint_id=self.checkpoint_id,
                                  itens=itens, unidade=unidade)

    def falhar_checkpoint(self, motivo):
        if self.checkpoint_id is None:
            return
        self.banco.executa(
            "update public.checkpoint_coleta set estado='PARCIAL', motivo=%s, "
            "updated_at=now() where id=%d"
            % (_lit(str(motivo)[:400]), int(self.checkpoint_id)))


def abrir_execucao(banco, *, run_id, platform, actor, unidade=None,
                   actor_version=None, source_country='NAO_SEI',
                   rule_version='v1', mission=None, pais='NAO_SEI',
                   source_id=None, route_class_id=None, policy_version=None):
    """A RUN existe ANTES do trabalho. O checkpoint, só se houver unidade.

    `unidade` é `(target, entrada, campos_da_identidade)` — o que só o dono da
    plataforma sabe dizer. `None` significa «esta operação não tem metade
    feita», e não «esqueci-me».

    Devolve `(Execucao, porque)`. `porque` só não é None quando o checkpoint
    RECUSOU — e aí a `Execucao` vem sem RUN, porque não houve execução nenhuma.

        UMA RECUSA DE CHECKPOINT NÃO É UMA EXECUÇÃO QUE FALHOU.
        É UMA EXECUÇÃO QUE NÃO COMEÇOU.
    """
    cid = h = None
    if unidade is not None:
        target, entrada, campos = unidade
        ok, ruins = identidade_valida(campos)
        if not ok:
            return None, ('IDENTIDADE_INVALIDA: %s' % ruins)
        h = abrir(banco, target=target, entrada=entrada, actor=actor,
                  platform=platform, pais=pais, unidades_totais=1,
                  rule_version=rule_version)
        pode, porque, cid, _ = pode_gastar(banco, target, h)
        if not pode:
            return None, porque
        banco.executa("update public.checkpoint_coleta set estado='EM_CURSO', "
                      "updated_at=now() where id=%d" % int(cid))

    abrir_corrida(banco, run_id=run_id, platform=platform, actor=actor,
                  actor_version=actor_version, source_country=source_country,
                  rule_version=rule_version, mission=mission, checkpoint_id=cid,
                  entrada=(unidade[1] if unidade is not None else None))
    if cid is not None:
        ligar_ao_checkpoint(banco, run_id=run_id, checkpoint_id=cid)

    relator = RelatorDeEtapas(banco, run_id=run_id, checkpoint_id=cid,
                              actor=actor, actor_version=actor_version,
                              source_id=source_id, route_class_id=route_class_id,
                              policy_version=policy_version)
    return Execucao(banco, run_id=run_id, checkpoint_id=cid, relator=relator,
                    input_hash=h), None
