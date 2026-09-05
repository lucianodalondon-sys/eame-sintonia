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
sys.path.insert(0, HERE)
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
        cmd = ['psql', self.dsn, '-v', 'ON_ERROR_STOP=1', '-tAF', '\x1f', '-c', sql]
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
    print('Rotação de chave: scripts/apify_pool.py (portado do piloto italiano).')
