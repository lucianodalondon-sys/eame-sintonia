#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A LINHAGEM DO READY SOCIAL — do item pousado de volta ao byte do SCRAP.

    BANCO_DESCARTAVEL_URL=postgresql://postgres@127.0.0.1:5433/descartavel \\
        python3 provas/a_linhagem_do_ready_social.py

A PERGUNTA
----------
    UM ITEM QUE CHEGA COMO READY PELA ROTA SOCIAL CONSEGUE CARREGAR O
    `RAW_OBSERVATION_ID` REAL DA OBSERVACAO QUE O ORIGINOU — E, POR ELE,
    VOLTAR DETERMINISTICAMENTE AO RAW E AO STORAGE?

A rota documental ja fechava esta volta (`provas/a_linhagem_do_ready.py`). A
social nao, e o motivo era TEMPORAL e nao arquitectural — medido no HEAD antes
desta missao, com a rota SCRAP inteira contra PostgreSQL 16 descartavel:

    SCRAP_RAW_OBSERVATION_CREATED  = YES
    SCRAP_RAW_OBSERVATION_ID       = 1        (o banco cunhou-o)
    SCRAP_READY_CREATED            = YES
    SCRAP_READY_RAW_OBSERVATION_ID = 'NAO SEI'

O id existia. O item que chegava a Admissao e que nao o levava.

    O QUE O DONO SABE E NAO DEVOLVE, PARA QUEM ESTA DO OUTRO LADO
    NUNCA ACONTECEU.

A FRONTEIRA, MEDIDA E NAO SUPOSTA
----------------------------------
`coleta/ingresso.py::receber` monta `PARA_A_PORTA` ANTES de chamar
`preservar()`; o `raw_asset.id` so existe DEPOIS. Dentro de `preservar()`,
`conferir_o_que_ficou_escrito()` tem as duas coisas em mao ao mesmo tempo — a
observacao PLANEADA (que veio do artefato do chamador) e a LINHA lida de volta
(que traz o `id`) — e deitava o par fora, guardando so o caminho.

    ESSE PAR E A PONTE. ELE NAO PRECISA DE SER DESCOBERTO: PRECISA DE
    ATRAVESSAR.

O QUE ESTA PROVA NAO FAZ
------------------------
Nao procura o RAW por `sha256`, por `storage_path`, por `SOURCE_ID`, por
`RUN_ID` nem por posicao na lista. A volta e SEMPRE uma consulta por
`raw_asset.id`, e ela comeca no ficheiro pousado na sala — nunca na variavel
que o setup ja conhecia.

    REAL_NETWORK = 0 · META_REQUESTS = 0 · APIFY_RUNS = 0 · PAID_USD = 0
    LIVE_READS = 0 · LIVE_WRITES = 0 · SALA REAL INTOCADA
"""
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in ('orquestrador', 'pedido', 'coleta', 'leis', 'regras', 'ferramentas',
           'medidas', 'guarda', 'admissao', ''):
    sys.path.insert(0, os.path.join(RAIZ, _p) if _p else RAIZ)
import _gavetas                                        # noqa: E402,F401

import admissao                                        # noqa: E402
import artefato as art                                 # noqa: E402
import coleta_checkpoint as cc                         # noqa: E402
import proveniencia as pv                              # noqa: E402
import sala_de_espera as espera                        # noqa: E402
from coleta import ingresso as ing                     # noqa: E402

import importlib.util as _u                            # noqa: E402

_sp = _u.spec_from_file_location(
    'e2e01', os.path.join(RAIZ, 'provas', 'o_scrap_chega_ao_acervo.py'))
_e2e = _u.module_from_spec(_sp)
_sp.loader.exec_module(_e2e)

FONTE = 'IT-T9-001'
UNIVERSO = 'T9'
_SO_VERIFICA = ('008',)

#: A legenda italiana do universo T9. A MESMA do falso canonico
#: (`provas/_e2e01_janela_admissivel.py`), porque medir a admissao com outro
#: texto mediria outro dicionario.
LEGENDA = ('Nuovo prodotto per la difesa del frumento: la campagna parte '
           'dalla fiera di Bologna.')

fora = []

#: ⚠️ O ARMAZEM DESTA PROVA E DESCARTAVEL, E ISSO NAO E ASSEIO: E A LEI.
#: `ArmazemLocal(RAIZ)` escreveria os brutos das seccoes em processo DENTRO
#: da arvore real — `IT/it-t9-001/OBSERVATION/...` — e uma prova que deixa
#: bytes no repositorio mistura evidencia com trabalho.
#:
#:     UMA PROVA QUE SUJA A ARVORE MEDE A ARVORE QUE ELA PROPRIA SUJOU.
#:
#: A raiz de LEITURA continua a ser a real (`raiz=RAIZ`): e de la que a ficha
#: resolve um `STORAGE_LOCATION` declarado pelo item.
_ARMAZEM = []


def armazem():
    if not _ARMAZEM:
        _ARMAZEM.append(ing.ArmazemLocal(
            tempfile.mkdtemp(prefix='armazem-social-')))
    return _ARMAZEM[0]


def caso(nome, condicao, detalhe=''):
    fora.append((nome, bool(condicao), detalhe))


# ═════════════════════════════════════════════════════════════════════════
# O BANCO, E O QUE SE LHE PERGUNTA
# ═════════════════════════════════════════════════════════════════════════
def cadeia_de_migrations():
    pasta = os.path.join(RAIZ, 'supabase', 'migrations')
    return [f.split('_', 1)[0] for f in sorted(os.listdir(pasta))
            if f.endswith('.sql') and f.split('_', 1)[0] not in _SO_VERIFICA]


def aplicar_migrations(url):
    pasta = os.path.join(RAIZ, 'supabase', 'migrations')
    for n in cadeia_de_migrations():
        achados = [f for f in sorted(os.listdir(pasta)) if f.startswith(n + '_')]
        r = subprocess.run(['psql', url, '-v', 'ON_ERROR_STOP=1', '-q', '-f',
                            os.path.join(pasta, achados[0])],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print('FALHOU a aplicar %s\n%s' % (achados[0], r.stderr[:900]))
            raise SystemExit(1)


def _memoria(url):
    sp = _u.spec_from_file_location(
        'prova_pg', os.path.join(RAIZ, 'provas',
                                 'preservar_coleta_no_postgres.py'))
    m = _u.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m.MemoriaPostgres(url)


def _ou_ausente(v):
    """O NULL do banco, do lado de ca da porta de texto.

    ⚠️ `coleta_checkpoint.Banco` fala com o Postgres por `psql -tA`, e ali um
    NULL chega como string VAZIA. Ler `''` como valor faria «esta observacao
    nao tem copia» parecer «tem uma copia chamada nada».

        AUSENCIA QUE CHEGA COMO TEXTO VAZIO CONTINUA A SER AUSENCIA.
    """
    return None if v is None or str(v) == '' else v


# ── A VOLTA. UMA CONSULTA, POR ID CANONICO, E MAIS NADA ──────────────────
def resolver(sql, unidade):
    """Do item pousado ate ao byte. NENHUMA heuristica, NENHUM sha, NENHUM path.

    ⚠️ A ENTRADA E A UNIDADE DA SALA. Ela nao recebe `raw_id` de fora: se o
    recebesse, esta funcao provaria que uma variavel do teste bate consigo
    propria.

    `storage_object` sai do MESMO join, pela chave estrangeira composta
    `(storage_object_id, sha256)` que `raw_asset` ja tem — e por isso o
    contrato READY nao precisa de carregar um segundo campo.

        A MENOR IDENTIDADE QUE FECHA A ESTRADA E A CERTA.
    """
    ident = unidade.get('RAW_OBSERVATION_ID')
    if ident is None or str(ident).strip().upper() in (
            'NAO SEI', 'NÃO SEI', 'UNKNOWN', ''):
        return {'RESOLVIDO': False, 'CANDIDATOS': 0,
                'PORQUE': 'a unidade nao nomeia observacao'}
    if not str(ident).isdigit():
        return {'RESOLVIDO': False, 'CANDIDATOS': 0,
                'PORQUE': 'RAW_OBSERVATION_ID nao e um id de raw_asset: %r'
                          % ident}
    linhas = sql.executa(
        'select r.id, r.run_id, r.source_id, r.sha256, r.storage_object_id,'
        '       s.id, s.storage_path, s.sha256, r.media_type'
        '  from public.raw_asset r'
        '  left join public.storage_object s on s.id = r.storage_object_id'
        ' where r.id = %d' % int(ident))
    if len(linhas) != 1:
        return {'RESOLVIDO': False, 'CANDIDATOS': len(linhas),
                'PORQUE': 'a observacao nomeada nao existe' if not linhas
                          else 'mais de uma linha para um id — impossivel'}
    x = [_ou_ausente(v) for v in linhas[0]]
    return {'RESOLVIDO': True, 'CANDIDATOS': 1,
            'RAW_OBSERVATION_ID': int(x[0]), 'RUN_ID': x[1],
            'SOURCE_ID': x[2], 'RAW_SHA256': x[3],
            'STORAGE_OBJECT_ID': x[4], 'STORAGE_PATH': x[6],
            'STORAGE_SHA256': x[7], 'MEDIA_TYPE': x[8]}


# ═════════════════════════════════════════════════════════════════════════
# 1 · A ESTRADA INTEIRA DO SCRAP, DO PEDIDO A SALA
# ═════════════════════════════════════════════════════════════════════════
def a_estrada_do_scrap(url):
    """REQUEST → ORCHESTRATOR → SCRAP EXECUTOR → INGRESS → RUN → RAW →
    STORAGE → ADMISSION → READY → SALA, e depois a volta, SO pelo pousado.

    A arvore e uma COPIA descartavel, e o unico ficheiro falso e o cliente do
    navegador — o mesmo que `o_scrap_chega_ao_acervo.py` usa, e pela mesma
    razao: um falso acima do portao mediria o falso.
    """
    base = tempfile.mkdtemp(prefix='linhagem-social-')
    arvore = os.path.join(base, 'arvore')
    os.makedirs(arvore)
    try:
        _e2e.com_este_falso(
            arvore, os.path.join(RAIZ, 'provas', '_e2e01_janela_admissivel.py'))
        recibo, env, idas = _e2e.correr_com_banco(arvore, FONTE, url)
        run_id = (recibo or {}).get('RUN_ID') or ''
        caso('E0_a_corrida_do_SCRAP_correu_e_cunhou_RUN_ID',
             bool(run_id) and recibo.get('STATUS') == 'SUCCESS',
             'RUN_ID=%s · STATUS=%s' % (run_id, (recibo or {}).get('STATUS')))
        if not run_id:
            return None
        caso('E1_e_o_executor_e_o_do_SCRAP_e_a_rede_real_nao_foi_tocada',
             recibo.get('ACTOR') == 'coleta/scrap_colheita.py' and len(idas) >= 1,
             'ACTOR=%s · idas ao falso=%d · REAL_NETWORK=0'
             % (recibo.get('ACTOR'), len(idas)))

        # ⚠️ DAQUI PARA BAIXO SO SE LE O FICHEIRO DA SALA. O `recibo` fica
        # para CONFERIR no fim — nunca para alcancar coisa nenhuma.
        alvo = os.path.join(arvore, 'data', 'samples',
                            'PRONTO-PARA-INTELIGENCIA', '%s.json' % run_id)
        pousado = {}
        if os.path.isfile(alvo):
            pousado = json.loads(io.open(alvo, encoding='utf-8').read())
        itens = list(pousado.get('ITENS') or [])
        caso('E2_a_unidade_social_POUSOU_na_sala_desta_corrida',
             len(itens) == 1 and pousado.get('RUN_ID') == run_id,
             '%d item(s) · RUN_ID bate=%s'
             % (len(itens), pousado.get('RUN_ID') == run_id))
        if not itens:
            return None
        ready = itens[0]

        # ── O CONTRATO, MEDIDO NO QUE ATERROU ───────────────────────────
        caso('E3_SCRAP_READY_FIELDS_sao_DOZE_e_nao_onze',
             len(ready) == 12,
             '%d campos: %s' % (len(ready), ', '.join(sorted(ready))))
        caso('E4_SCRAP_READY_HAS_RAW_OBSERVATION_ID',
             str(ready.get('RAW_OBSERVATION_ID')).isdigit(),
             'RAW_OBSERVATION_ID=%r' % ready.get('RAW_OBSERVATION_ID'))

        sql = cc.Banco(url)
        res = resolver(sql, ready)
        caso('E5_SCRAP_READY_TO_RAW_resolve_a_UMA_observacao',
             res['RESOLVIDO'] and res['CANDIDATOS'] == 1,
             'candidatos=%d · raw=%s' % (res['CANDIDATOS'],
                                         res.get('RAW_OBSERVATION_ID')))
        caso('E6_SCRAP_RAW_TO_STORAGE_pela_chave_composta',
             res.get('STORAGE_OBJECT_ID') is not None
             and res.get('STORAGE_SHA256') == res.get('RAW_SHA256'),
             'storage=%s · sha bate=%s'
             % (res.get('STORAGE_OBJECT_ID'),
                res.get('STORAGE_SHA256') == res.get('RAW_SHA256')))
        caso('E7_SCRAP_READY_TO_STORAGE_sem_segundo_campo_no_contrato',
             bool(res.get('STORAGE_PATH'))
             and 'STORAGE_OBJECT_ID' not in ready
             and 'STORAGE_PATH' not in ready,
             'o READY nao carrega armazem: sai do join · %s'
             % res.get('STORAGE_PATH'))

        # ── OS BYTES, RELIDOS — E TEM DE SER OS QUE O CRIARAM ───────────
        arm = ing.ArmazemLocal(arvore)
        corpo = None
        try:
            corpo = arm.ler(res['STORAGE_PATH']) if res.get('RESOLVIDO') else None
        except Exception:                              # noqa: BLE001
            corpo = None
        sha_lido = hashlib.sha256(corpo).hexdigest() if corpo else None
        caso('E8_READBACK_PASS_e_BYTES_PRESERVED',
             bool(corpo) and len(corpo) > 0,
             '%d byte(s) relidos do armazem' % (len(corpo or b'')))
        caso('E9_HASH_MATCH_o_byte_relido_e_o_byte_registado',
             sha_lido is not None and sha_lido == res.get('RAW_SHA256'),
             'sha relido == raw_asset.sha256: %s' % (sha_lido
                                                     == res.get('RAW_SHA256')))
        guardado = {}
        try:
            guardado = json.loads((corpo or b'').decode('utf-8'))
        except Exception:                              # noqa: BLE001
            guardado = {}
        # ⚠️ NAO BASTA EXISTIR UM RAW VALIDO: TEM DE SER O RAW CERTO.
        # O byte preservado e a OBSERVACAO SERIALIZADA — e por isso o texto
        # que a porta julgou e o endereco que a fonte deu estao os dois la
        # dentro. Se o id apontasse para outra observacao, os dois seriam
        # outros. Comparam-se os DOIS: um so poderia bater por coincidencia
        # de conteudo entre dois posts.
        #
        #     UM RAW VALIDO NAO E O RAW CERTO.
        textos = [t.get('TEXT') for t in
                  (guardado.get(pv.CAMPO_DAS_UNIDADES) or [])]
        caso('E10_READY_RAW_ID_POINTS_TO_THE_BYTES_THAT_CREATED_IT',
             bool(ready.get('TEXTO'))
             and str(ready.get('TEXTO')) in [str(t) for t in textos]
             and str(guardado.get('SOURCE_URL') or '')
             == str(ready.get('ITEM_ID') or ''),
             'texto e endereco do READY vivem DENTRO do byte que o id nomeia')

        # ── RUN E SOURCE, PELA OBSERVACAO ───────────────────────────────
        caso('E11_SCRAP_RUN_LINEAGE_pela_observacao',
             res.get('RUN_ID') == run_id and ready.get('CORRIDA') == run_id,
             'raw.run_id=%s · READY.CORRIDA=%s' % (res.get('RUN_ID'),
                                                   ready.get('CORRIDA')))
        caso('E12_SCRAP_SOURCE_LINEAGE_declarada_e_nao_inferida',
             res.get('SOURCE_ID') == FONTE and ready.get('SOURCE_ID') == FONTE,
             'raw.source_id=%s · READY.SOURCE_ID=%s'
             % (res.get('SOURCE_ID'), ready.get('SOURCE_ID')))

        # ── O TEXTO, RESOLVIDO PELA LINHAGEM E NAO COPIADO PARA O READY ──
        unidades = guardado.get(pv.CAMPO_DAS_UNIDADES) or []
        u0 = unidades[0] if unidades else {}
        caso('E13_TEXT_KIND_RESOLVABLE_pela_linhagem',
             u0.get('TEXT_KIND') == pv.NATIVE_CAPTION,
             'do byte: TEXT_KIND=%s (NATIVE_CAPTION != TRANSCRIPT)'
             % u0.get('TEXT_KIND'))
        caso('E14_TEXT_RELATION_RESOLVABLE_pela_linhagem',
             u0.get('TEXT_RELATION') == pv.ORIGINAL,
             'TEXT_RELATION=%s (ORIGINAL != TRANSLATED)'
             % u0.get('TEXT_RELATION'))
        caso('E15_LANGUAGE_RESOLVABLE_e_nao_herdada_da_publicacao',
             u0.get('LANGUAGE') == 'it',
             'LANGUAGE=%s — da unidade de texto, nunca da publicacao'
             % u0.get('LANGUAGE'))
        caso('E16_e_nada_disto_viaja_no_contrato_READY',
             not any(k in ready for k in ('TEXT_KIND', 'TEXT_RELATION',
                                          'LANGUAGE', 'TEXT_UNITS')),
             'o contrato continua com 12 campos; a especie fica no bruto')

        # ── DERIVED: NAO SE APLICA, E CONTINUA A NAO SE APLICAR ─────────
        d = recibo.get('DERIVACAO') or {}
        caso('E17_DERIVED_APPLICABILITY_continua_NOT_APPLICABLE',
             d.get('ESTADO_DA_ETAPA') == 'NOT_APPLICABLE'
             and not (recibo.get('ESTRUTURACAO') or {}).get('CHAMADO'),
             'DERIVED=%s · STRUCTURED_CHAMADO=%s'
             % (d.get('ESTADO_DA_ETAPA'),
                (recibo.get('ESTRUTURACAO') or {}).get('CHAMADO')))

        # E o que o recibo disse tem de bater com o que a sala tem. Isto e
        # CONFERENCIA, e nao caminho: a volta ja foi feita acima.
        obs_do_recibo = [
            o.get('RAW_OBSERVATION_ID')
            for o in ((recibo.get('INGRESSO') or {}).get('PARA_A_DERIVACAO')
                      or [])] or None
        caso('E18_RAW_OBSERVATION_ID_FABRICATION_zero',
             res.get('RAW_OBSERVATION_ID') in [
                 int(x[0]) for x in sql.executa(
                     "select id from public.raw_asset where run_id = '%s'"
                     % run_id.replace("'", "''"))],
             'o id do READY e uma linha REAL desta corrida (recibo: %s)'
             % obs_do_recibo)
        return {'RUN_ID': run_id, 'RAW': res.get('RAW_OBSERVATION_ID'),
                'SQL': sql}
    finally:
        shutil.rmtree(base, ignore_errors=True)


# ═════════════════════════════════════════════════════════════════════════
# 2 · A CARDINALIDADE HOSTIL — RECUSAS NO MEIO, E NADA ESCORREGA
# ═════════════════════════════════════════════════════════════════════════
def _item(n, *, texto=LEGENDA, fonte=FONTE, nativo=None, local=None):
    """Uma observacao social, na lingua que um coletor larga."""
    d = {'SOURCE_ID': fonte,
         'SOURCE_URL': 'https://social.example/p/%s' % n,
         'SOURCE_NATIVE_ID': nativo or ('post-%s' % n),
         'MEDIA_TYPE': 'application/json',
         'TEXT': texto,
         'PUBLISHED_AT': '2026-09-01T10:00:00Z',
         'COUNTRY_SCOPE': 'IT', 'SOURCE_LOCATION': 'IT',
         pv.CAMPO_DAS_UNIDADES: [pv.unidade_de_texto(
             texto=texto, kind=pv.NATIVE_CAPTION,
             kind_basis=pv.DECLARED_BY_PROVIDER, relation=pv.ORIGINAL,
             language='it', unit_id='TU-1')]}
    if fonte is None:
        d.pop('SOURCE_ID')
    if local is not None:
        d['STORAGE_LOCATION'] = local
    return d


def _corrida(run_id):
    return {'RUN_ID': run_id, 'PLATFORM': 'INSTAGRAM',
            'ACTOR': 'coleta/adaptador_instagram.py', 'ACTOR_VERSION': 'v1',
            'SOURCE_COUNTRY': 'IT', 'RULE_VERSION': '1',
            'STARTED_AT': '2026-09-10T00:00:00Z'}


def _julgar_e_pousar(unidades, run_id):
    """A porta e a sala, como o orquestrador as corre. → as unidades pousadas.

    Nao ha atalho aqui: `admissao.decidir` e `pronto_para_inteligencia` sao os
    da arvore, e a sala e a real — so a MORADA e que e descartavel.
    """
    prontos = []
    for x in unidades:
        d = admissao.decidir(x, UNIVERSO, corrida=run_id)
        if d.resultado == admissao.SIM:
            prontos.append(admissao.pronto_para_inteligencia(x, d))
    espera.pousar(run_id, prontos)
    corpo = espera.ler(run_id) or {}
    return list(corpo.get('ITENS') or [])


def a_cardinalidade(url, sql):
    """CINCO itens, e so TRES chegam. Os ids nao podem escorregar.

    ⚠️ ESTE E O ATAQUE CENTRAL DA MISSAO, e ele e sobre POSICAO.
    A colheita e feita de proposito para que a lista de entrada, a lista que
    `preservar()` recebe e a lista de observacoes confirmadas tenham TODAS
    tamanhos diferentes e ordens que nao se correspondem:

        #1  aceite
        #2  RECUSADO NA PORTA          unidade de texto malformada
        #3  aceite
        #4  RECUSADO POR `preservar()` sem SOURCE_ID real
        #5  aceite

    Entrada = 5 · artefatos = 4 · observacoes = 3 · READY = 3. Quatro numeros
    diferentes, e nenhuma correspondencia por indice sobrevive a isso.

        POSICAO NAO E LIGACAO. UM ITEM RECUSADO NO MEIO
        DESLOCA TUDO O QUE VEM DEPOIS DELE.
    """
    run = 'RUN-SOCIAL-CARD'
    mau = _item(2)
    mau[pv.CAMPO_DAS_UNIDADES] = [{'TEXT_UNIT_ID': 'TU-1', 'TEXT': 'x'}]
    itens = [_item(1), mau, _item(3), _item(4, fonte=None), _item(5)]
    r = ing.receber(itens, corrida=_corrida(run),
                    armazem=armazem(), memoria=_memoria(url),
                    raiz=RAIZ, banco_do_rastro=sql)
    porta = r.get('PARA_A_PORTA') or []
    recusas = r.get('RECUSAS') or []
    sem_fonte = (r.get('RAW') or {}).get('RECUSADOS_SEM_IDENTIDADE') or []
    obs = (r.get('RAW') or {}).get('RAW_OBSERVATIONS') or []
    caso('C1_a_colheita_hostil_tem_as_quatro_contagens_DIFERENTES',
         len(itens) == 5 and len(recusas) == 1 and len(porta) == 4
         and len(sem_fonte) == 1 and len(obs) == 3,
         'entrada=5 · recusa na porta=%d · a porta=%d · sem fonte=%d · obs=%d'
         % (len(recusas), len(porta), len(sem_fonte), len(obs)))

    # ⚠️ E A ORDEM DE `RAW_OBSERVATIONS` NAO E A ORDEM DA ENTRADA — MEDIDO.
    # `objetos_da_corrida()` le `order by storage_path`, e o caminho comeca
    # pelo sha do conteudo. A lista que volta do banco sai por ordem de HASH.
    #
    #     A LISTA QUE VOLTA NAO E A LISTA QUE FOI. QUEM LIGASSE POR INDICE
    #     DARIA A CADA ITEM A OBSERVACAO DE OUTRO, E COM CARA DE CERTO.
    ordem_entrada = [u.get('url') for u in porta]
    ordem_volta = [o['RAW_OBSERVATION_ID'] for o in obs]
    caso('C1b_a_ordem_do_banco_NAO_e_a_ordem_da_entrada',
         ordem_volta != sorted(ordem_volta),
         'ids na ordem em que o banco os devolveu: %s (entrada: %d itens)'
         % (ordem_volta, len(ordem_entrada)))

    pousadas = _julgar_e_pousar(porta, run)
    com_id = [u for u in pousadas
              if str(u.get('RAW_OBSERVATION_ID')).isdigit()]
    caso('C2_so_os_TRES_com_observacao_chegam_a_sala_com_linhagem',
         len(pousadas) == 4 and len(com_id) == 3,
         '%d READY · com id: %s' % (len(pousadas),
                                    [u.get('RAW_OBSERVATION_ID')
                                     for u in pousadas]))
    # ⚠️ O QUARTO NAO DESAPARECE, E TAMBEM NAO MENTE. Ele foi recusado por
    # `preservar()` — sem fonte nao ha observacao — e chega a sala a dizer
    # exactamente isso. Um id emprestado do vizinho seria pior do que o
    # `NAO SEI` honesto que ele leva.
    #
    #     AUSENCIA DE OBSERVACAO E AUSENCIA. ELA DIZ-SE, NAO SE PREENCHE.
    sem_obs = [u for u in pousadas
               if not str(u.get('RAW_OBSERVATION_ID')).isdigit()]
    caso('C2b_o_item_sem_fonte_diz_NAO_SEI_e_nao_pede_emprestado',
         len(sem_obs) == 1
         and sem_obs[0].get('RAW_OBSERVATION_ID') == 'NAO SEI',
         'RAW_OBSERVATION_ID=%r' % (sem_obs[0].get('RAW_OBSERVATION_ID')
                                    if sem_obs else '-'))

    # ── E CADA UM APONTA PARA O SEU, E NAO PARA O DO VIZINHO ────────────
    # A CONFERENCIA E PELO TEXTO DENTRO DO BYTE: cada item tem uma `SOURCE_URL`
    # diferente, e por isso o byte preservado de cada um e distinguivel.
    errados, ambiguos = 0, 0
    arm = armazem()
    for u in com_id:
        res = resolver(sql, u)
        if not res['RESOLVIDO'] or res['CANDIDATOS'] != 1:
            ambiguos += 1
            continue
        try:
            guardado = json.loads(arm.ler(res['STORAGE_PATH']).decode('utf-8'))
        except Exception:                              # noqa: BLE001
            guardado = {}
        # A CONFERENCIA E PELO CONTEUDO DO BYTE, e nao por um campo que a
        # porta tenha copiado: cada item traz a sua `SOURCE_URL`, e ela esta
        # DENTRO do bruto preservado. Se o id apontasse para o vizinho, este
        # endereco seria o do vizinho.
        if str(guardado.get('SOURCE_URL') or '') != str(u.get('ITEM_ID') or ''):
            errados += 1
    caso('C3_READY_WRONG_RAW_MATCHES_zero', errados == 0,
         'cada READY resolve para o byte que o originou (%d errado(s))'
         % errados)
    caso('C4_READY_AMBIGUOUS_RAW_MATCHES_zero', ambiguos == 0,
         '%d resolucao(oes) ambigua(s) ou partida(s)' % ambiguos)
    ids = [u.get('RAW_OBSERVATION_ID') for u in com_id]
    caso('C5_tres_READY_tres_observacoes_DISTINTAS',
         len(set(ids)) == len(ids) == 3,
         'ids=%s — nenhum emprestado' % ids)
    caso('C6_um_item_RECUSADO_NA_PORTA_nao_deixa_READY_nem_id',
         len(pousadas) == 4 and len(porta) == 4,
         'o item malformado nao pousou, e nao empurrou ninguem')
    return [int(x) for x in ids]


# ═════════════════════════════════════════════════════════════════════════
# 3 · MESMOS BYTES, DUAS OBSERVACOES
# ═════════════════════════════════════════════════════════════════════════
def os_mesmos_bytes(url, sql):
    """DOIS enderecos, UM conteudo, DUAS observacoes — e cada READY no seu.

    ⚠️ O CASO E REAL E ESTA MEDIDO NO CODIGO DE PRODUCAO: a ADAMA publicou o
    MESMO PDF em `media/731` e em `media/6321`. Dois factos sobre o mundo, um
    conteudo so. Aqui o mesmo, na rota social: o mesmo ficheiro observado sob
    dois identificadores nativos.

        SHA256 IDENTIFICA BYTES. NAO IDENTIFICA OBSERVACAO.
        READY_A NAO PODE RESOLVER PARA «QUALQUER RAW COM O MESMO SHA».
    """
    run = 'RUN-SOCIAL-MESMOS-BYTES'
    corpo = json.dumps({'observacao': 'a mesma, vista duas vezes'},
                       ensure_ascii=False).encode('utf-8')
    pasta = tempfile.mkdtemp(prefix='bytes-iguais-', dir=os.path.join(RAIZ, 'data'))
    caminho = os.path.join(pasta, 'observacao.json')
    io.open(caminho, 'wb').write(corpo)
    rel = os.path.relpath(caminho, RAIZ)
    try:
        a = _item('A', nativo='media-731', local=rel)
        b = _item('B', nativo='media-6321', local=rel)
        r = ing.receber([a, b], corrida=_corrida(run),
                        armazem=armazem(), memoria=_memoria(url),
                        raiz=RAIZ, banco_do_rastro=sql)
        obs = (r.get('RAW') or {}).get('RAW_OBSERVATIONS') or []
        caso('B1_duas_observacoes_distintas_para_o_MESMO_sha',
             len(obs) == 2
             and obs[0]['RAW_OBSERVATION_ID'] != obs[1]['RAW_OBSERVATION_ID']
             and obs[0]['SHA256'] == obs[1]['SHA256'],
             'RAW_A.id=%s != RAW_B.id=%s · sha igual=%s'
             % (obs[0]['RAW_OBSERVATION_ID'] if obs else '-',
                obs[1]['RAW_OBSERVATION_ID'] if len(obs) > 1 else '-',
                obs[0]['SHA256'] == obs[1]['SHA256'] if len(obs) > 1 else '-'))
        porta = r.get('PARA_A_PORTA') or []
        # O texto destes dois nao e do lexico T9 — o conteudo e o ficheiro —,
        # e por isso a admissao nao os deixaria pousar. A pergunta desta
        # seccao e sobre a PONTE, e ela mede-se no item que vai a porta.
        levados = [u.get('raw_asset_id') for u in porta]
        caso('B2_cada_item_leva_a_SUA_observacao_e_nao_a_do_gemeo',
             len(levados) == 2 and len(set(levados)) == 2
             and set(levados) == {o['RAW_OBSERVATION_ID'] for o in obs},
             'item A -> %s · item B -> %s' % tuple(levados[:2] or ['-', '-']))
        por_url = {}
        for u in porta:
            res = resolver(sql, {'RAW_OBSERVATION_ID': u.get('raw_asset_id')})
            por_url[u.get('url')] = res.get('STORAGE_PATH')
        caso('B3_e_os_dois_enderecos_de_armazem_sao_DIFERENTES',
             len(set(por_url.values())) == 2,
             'duas moradas para um conteudo: %s'
             % ' · '.join(sorted(os.path.basename(str(v))[:34]
                                 for v in por_url.values())))
        return [o['RAW_OBSERVATION_ID'] for o in obs]
    finally:
        shutil.rmtree(pasta, ignore_errors=True)


# ═════════════════════════════════════════════════════════════════════════
# 4 · DUAS CORRIDAS DA MESMA FONTE
# ═════════════════════════════════════════════════════════════════════════
def as_duas_corridas(url, sql):
    """RUN_A e RUN_B, a MESMA fonte. Cada READY na observacao da SUA corrida.

        A CORRIDA E PROVENIENCIA, E NAO IDENTIDADE.
        MAS UM READY DA CORRIDA A A APONTAR PARA O RAW DA B E LINHAGEM
        PARTIDA COM CARA DE INTEIRA.
    """
    fora_ids = {}
    for run in ('RUN-SOCIAL-A', 'RUN-SOCIAL-B'):
        r = ing.receber([_item('mesma-fonte')], corrida=_corrida(run),
                        armazem=armazem(), memoria=_memoria(url),
                        raiz=RAIZ, banco_do_rastro=sql)
        porta = r.get('PARA_A_PORTA') or []
        pousadas = _julgar_e_pousar(porta, run)
        fora_ids[run] = [u.get('RAW_OBSERVATION_ID') for u in pousadas]
    a = fora_ids['RUN-SOCIAL-A']
    b = fora_ids['RUN-SOCIAL-B']
    caso('R1_as_duas_corridas_produzem_READY_com_observacoes_DISTINTAS',
         len(a) == 1 and len(b) == 1 and a[0] != b[0],
         'READY_A -> %s · READY_B -> %s' % (a[:1], b[:1]))
    erros = 0
    for run, ids in fora_ids.items():
        for i in ids:
            res = resolver(sql, {'RAW_OBSERVATION_ID': i})
            if res.get('RUN_ID') != run:
                erros += 1
    caso('R2_CROSS_RUN_LINEAGE_ERRORS_zero', erros == 0,
         'cada READY resolve para o RAW da SUA corrida (%d erro(s))' % erros)
    return (a + b), erros


# ═════════════════════════════════════════════════════════════════════════
# 5 · O RETRY — A MESMA CORRIDA, OUTRA VEZ
# ═════════════════════════════════════════════════════════════════════════
def o_retry(url, sql):
    """A MESMA corrida entra pela MESMA porta. Nada duplica, nada muda de dono.

    ⚠️ `RETRY_SAME_LOGICAL_RUN` mede-se e nao se presume: o segundo `receber()`
    leva o MESMO `RUN_ID`, e e por isso que a observacao tem de ser REENCONTRADA
    — e nunca cunhada outra vez.
    """
    run = 'RUN-SOCIAL-RETRY'
    item = _item('retry')
    r1 = ing.receber([item], corrida=_corrida(run),
                     armazem=armazem(), memoria=_memoria(url),
                     raiz=RAIZ, banco_do_rastro=sql)
    ready1 = _julgar_e_pousar(r1.get('PARA_A_PORTA') or [], run)
    brutos_antes = int(sql.executa(
        'select count(*) from public.raw_asset')[0][0])
    obj_antes = int(sql.executa(
        'select count(*) from public.storage_object')[0][0])

    r2 = ing.receber([item], corrida=_corrida(run),
                     armazem=armazem(), memoria=_memoria(url),
                     raiz=RAIZ, banco_do_rastro=sql)
    ready2 = _julgar_e_pousar(r2.get('PARA_A_PORTA') or [], run)
    brutos_depois = int(sql.executa(
        'select count(*) from public.raw_asset')[0][0])
    obj_depois = int(sql.executa(
        'select count(*) from public.storage_object')[0][0])

    id1 = ready1[0].get('RAW_OBSERVATION_ID') if ready1 else None
    id2 = ready2[0].get('RAW_OBSERVATION_ID') if ready2 else None
    caso('T1_RETRY_SAME_LOGICAL_RUN', bool(id1) and id1 == id2,
         'mesmo RUN_ID, mesma observacao: %s -> %s' % (id1, id2))
    res = resolver(sql, ready2[0] if ready2 else {})
    caso('T2_SCRAP_READY_TO_RAW_AFTER_RETRY',
         res['RESOLVIDO'] and res['RAW_OBSERVATION_ID'] == id1
         and res['RUN_ID'] == run,
         'o READY do retry resolve para a observacao da corrida (%s)'
         % res.get('RAW_OBSERVATION_ID'))
    caso('T3_RAW_DUPLICATION_ON_RETRY_zero', brutos_depois == brutos_antes,
         'raw_asset: %d -> %d' % (brutos_antes, brutos_depois))
    caso('T4_STORAGE_DUPLICATION_ON_RETRY_zero', obj_depois == obj_antes,
         'storage_object: %d -> %d' % (obj_antes, obj_depois))
    return id1


# ═════════════════════════════════════════════════════════════════════════
# 6 · RED TEAM — VINTE MANEIRAS DE A PONTE SE ENGANAR
# ═════════════════════════════════════════════════════════════════════════
def o_red_team(url, sql, raw_id, ids_mesmo_sha, ids_corridas):
    """Cada ataque tem de morrer, e morrer PELA LEI QUE ELE VISA."""
    linha = sql.executa(
        'select run_id, source_id, sha256, storage_path from public.raw_asset'
        ' where id = %d' % int(raw_id))[0]
    run_id, source_id, sha, caminho = linha[0], linha[1], linha[2], linha[3]

    caso('RT01_o_SHA_no_lugar_do_id_NAO_resolve',
         not resolver(sql, {'RAW_OBSERVATION_ID': sha})['RESOLVIDO'],
         'sha256 identifica BYTES, e nunca observacao')
    caso('RT02_o_RUN_ID_no_lugar_do_id_NAO_resolve',
         not resolver(sql, {'RAW_OBSERVATION_ID': run_id})['RESOLVIDO'],
         'RUN != OBSERVATION')
    caso('RT03_o_SOURCE_ID_no_lugar_do_id_NAO_resolve',
         not resolver(sql, {'RAW_OBSERVATION_ID': source_id})['RESOLVIDO'],
         'SOURCE != OBSERVATION')
    caso('RT04_o_STORAGE_PATH_no_lugar_do_id_NAO_resolve',
         not resolver(sql, {'RAW_OBSERVATION_ID': caminho})['RESOLVIDO'],
         'endereco fisico != identidade')
    # 5 · POSICAO NA LISTA. O ataque e ao CODIGO, e nao ao banco: se a ponte
    # usasse indice, um item recusado no meio deslocaria os ids — e a seccao 2
    # ja mediu que nao desloca. Aqui prova-se que o transporte e por ALCA.
    fonte_ing = io.open(os.path.join(RAIZ, 'coleta', 'ingresso.py'),
                        encoding='utf-8').read()
    caso('RT05_a_ponte_nao_liga_por_POSICAO_na_lista',
         '_a_observacao_volta_ao_item' in fonte_ing
         and 'por_passagem[alca]' in fonte_ing
         and 'RAW_OBSERVATIONS'in fonte_ing,
         'a ligacao e por alca de passagem, e o mapa guarda o PROPRIO item')
    caso('RT06_dois_itens_com_os_MESMOS_bytes_nao_colapsam',
         len(set(ids_mesmo_sha)) == 2,
         'duas observacoes, um conteudo: %s' % ids_mesmo_sha)
    caso('RT07_duas_corridas_da_mesma_fonte_nao_colapsam',
         len(set(ids_corridas)) == len(ids_corridas) and len(ids_corridas) >= 2,
         'ids por corrida: %s' % ids_corridas)
    # 8 · o item recusado no meio ja foi medido na seccao 2 (C3/C5/C6).
    caso('RT08_um_item_recusado_entre_dois_aceites_nao_desloca_a_ligacao',
         all(ok for n, ok, _ in fora if n.startswith(('C3', 'C5', 'C6'))),
         'medido na colheita hostil de cinco itens')
    caso('RT09_READY_sem_id_NAO_conta_como_linhagem_completa',
         not resolver(sql, {'RAW_OBSERVATION_ID': 'NAO SEI'})['RESOLVIDO'],
         'ausencia continua ausencia, e nao se promove a resolvida')
    caso('RT10_um_RAW_inexistente_devolve_NADA_e_nao_o_vizinho',
         not resolver(sql, {'RAW_OBSERVATION_ID': 999999})['RESOLVIDO']
         and resolver(sql, {'RAW_OBSERVATION_ID': 999999})['CANDIDATOS'] == 0,
         'candidatos=0')
    # 11 · RAW DE OUTRA CORRIDA / 12 · DE OUTRA FONTE.
    outros = sql.executa(
        "select id, run_id, source_id from public.raw_asset"
        " where run_id <> '%s' order by id limit 1"
        % str(run_id).replace("'", "''"))
    caso('RT11_um_RAW_de_OUTRA_corrida_resolve_para_a_corrida_DELE',
         bool(outros)
         and resolver(sql, {'RAW_OBSERVATION_ID': outros[0][0]})['RUN_ID']
         == outros[0][1],
         'o id nomeia a observacao, e ela traz a corrida dela')
    caso('RT12_e_a_fonte_que_volta_e_a_DELE_e_nao_a_nossa',
         bool(outros)
         and resolver(sql, {'RAW_OBSERVATION_ID': outros[0][0]})['SOURCE_ID']
         == outros[0][2],
         'nenhuma fonte e emprestada pela consulta')
    # 13 · STORAGE INEXISTENTE — a observacao resolve, os bytes nao, e a
    # diferenca tem de ser visivel.
    orfao = sql.executa(
        "insert into public.raw_asset (run_id, storage_path, media_type,"
        " bytes, sha256, captured_at, identity_state, source_id, preserved,"
        " not_preserved_reason)"
        " values ('%s','it/orfao/nao-existe.json','application/json', 10,"
        " '%s', now(), 'FORWARD_IDENTITY_UNPROVEN', '%s', false,"
        " 'NOT_PRESERVED') returning id"
        % (str(run_id).replace("'", "''"), 'e' * 64, FONTE))
    r_orfao = resolver(sql, {'RAW_OBSERVATION_ID': orfao[0][0]})
    caso('RT13_um_RAW_sem_STORAGE_resolve_o_RAW_e_NAO_finge_bytes',
         r_orfao['RESOLVIDO'] and r_orfao.get('STORAGE_OBJECT_ID') is None
         and r_orfao.get('STORAGE_PATH') is None,
         'a observacao existe e a copia esta ausente — e diz-se')
    arm = armazem()
    faltou = False
    try:
        arm.ler('it/orfao/nao-existe.json')
    except Exception:                                  # noqa: BLE001
        faltou = True
    caso('RT14_e_os_bytes_ausentes_LEVANTAM_em_vez_de_devolver_vazio',
         faltou, 'ler um endereco que nao existe nao devolve b""')
    # 15 · HASH DO STORAGE DIVERGENTE.
    res_bom = resolver(sql, {'RAW_OBSERVATION_ID': raw_id})
    caso('RT15_o_sha_do_RAW_e_o_sha_do_STORAGE_sao_CONFERIDOS_e_batem',
         res_bom.get('RAW_SHA256') == res_bom.get('STORAGE_SHA256'),
         'a chave estrangeira composta (objeto, sha256) nao deixa divergir')
    # 16/17 · RETRY.
    caso('RT16_o_retry_NAO_muda_a_observacao_do_item',
         all(ok for n, ok, _ in fora if n.startswith('T1')),
         'medido na seccao do retry')
    caso('RT17_o_retry_NAO_cria_RAW_nem_STORAGE_duplicado',
         all(ok for n, ok, _ in fora if n.startswith(('T3', 'T4'))),
         'medido na seccao do retry')
    # 18 · TEXT_KIND INFERIDO.
    u_inferida = pv.unidade_de_texto(texto='x', kind=pv.TEXTO_DESCONHECIDO,
                                     kind_basis=pv.NOT_DECLARED,
                                     relation=pv.TEXTO_DESCONHECIDO,
                                     unit_id='TU-9')
    caso('RT18_TEXT_KIND_nao_declarado_continua_UNKNOWN_e_nao_se_infere',
         u_inferida.get('TEXT_KIND') == pv.TEXTO_DESCONHECIDO
         and not pv.conferir_unidades_de_texto([u_inferida]),
         'UNKNOWN continua UNKNOWN: %s' % u_inferida.get('TEXT_KIND'))
    # 19 · LANGUAGE HERDADA DA PUBLICACAO.
    sem_lingua = pv.unidade_de_texto(texto='x', kind=pv.NATIVE_CAPTION,
                                     kind_basis=pv.DECLARED_BY_PROVIDER,
                                     relation=pv.ORIGINAL, unit_id='TU-9')
    item_com_lingua = dict(_item('lingua'), LANGUAGE='it')
    item_com_lingua[pv.CAMPO_DAS_UNIDADES] = [sem_lingua]
    naporta = ing.para_a_porta(item_com_lingua)
    caso('RT19_LANGUAGE_nao_se_herda_da_publicacao',
         sem_lingua.get('LANGUAGE') == pv.TEXTO_DESCONHECIDO
         and naporta.get('texto_lingua') == pv.TEXTO_DESCONHECIDO,
         'publicacao diz it · a unidade continua %r'
         % naporta.get('texto_lingua'))
    # 20 · NOT_APPLICABLE VIRAR PASS.
    import telemetria as tel
    caso('RT20_NOT_APPLICABLE_nao_e_PASS_no_vocabulario_canonico',
         'NOT_APPLICABLE' in tel.ESTADOS_DE_ETAPA
         and 'NOT_APPLICABLE' not in tel.ETAPA_ACONTECEU,
         'ETAPA_ACONTECEU=%s' % (tel.ETAPA_ACONTECEU,))
    # 21 · O CONTRATO SCRAP AINDA A VALIDAR ONZE CAMPOS.
    fonte_e2e = io.open(os.path.join(RAIZ, 'provas',
                                     'o_scrap_chega_ao_acervo.py'),
                        encoding='utf-8').read()
    caso('RT21_a_prova_do_SCRAP_nao_valida_ONZE_campos',
         'READY_TODOS_COM_11' not in fonte_e2e
         and 'len(i) == 11' not in fonte_e2e,
         'a lei mudou para 12: 11 == PASS seria um portao a dormir')
    # 22 · A ALCA NAO VIRA IDENTIDADE EXTERNA.
    caso('RT22_a_alca_da_passagem_NAO_e_escrita_em_lado_nenhum',
         'PASSAGEM_ID' not in io.open(
             os.path.join(RAIZ, 'supabase', 'migrations',
                          '026_a_observacao_ganha_identidade.sql'),
             encoding='utf-8').read()
         and int(sql.executa(
             "select count(*) from information_schema.columns where"
             " table_name = 'raw_asset' and column_name ilike '%passagem%'"
         )[0][0]) == 0,
         'efemera: nenhuma coluna, nenhum insert, nenhum ledger')
    # 23 · NAO NASCEU SEGUNDO LEDGER DE LINHAGEM.
    tabelas = int(sql.executa(
        "select count(*) from information_schema.tables where table_schema ="
        " 'public' and (table_name ilike '%linhagem%' or table_name ilike"
        " '%lineage%' or table_name ilike '%ready_raw%')")[0][0])
    caso('RT23_NENHUM_segundo_ledger_de_linhagem_foi_criado',
         tabelas == 0,
         'a Collection ja tem o dono do RAW; transporta-se, nao se duplica')


def _fechar():
    print('')
    maus = [n for n, ok, _ in fora if not ok]
    for nome, ok, det in fora:
        print('  %s  %-58s %s' % ('PASS' if ok else 'FAIL', nome, det[:66]))
    print('')
    print('=' * 74)
    print('RED_TEAM_ATTACKS  = %d'
          % len([n for n, _, _ in fora if n.startswith('RT')]))
    print('RED_TEAM_SURVIVORS= %d'
          % len([n for n, ok, _ in fora if n.startswith('RT') and not ok]))
    print('LINHAGEM_DO_READY_SOCIAL=%s · %d casos · %d falha(s)'
          % ('PASS' if not maus else 'FAIL', len(fora), len(maus)))
    print('=' * 74)
    return 0 if not maus else 1


def main():
    url = os.environ.get('BANCO_DESCARTAVEL_URL')
    if not url:
        print('SEM BANCO DESCARTAVEL — e SKIP != PASS.')
        print('LINHAGEM_DO_READY_SOCIAL=NOT_MEASURED')
        return 2
    print(__doc__.strip().splitlines()[0])
    print('=' * 74)
    print('%d migrations · sala descartavel · banco descartavel'
          % len(cadeia_de_migrations()))
    aplicar_migrations(url)

    # ⚠️ A SALA REAL NAO SE TOCA. A morada e trocada por uma temporaria ANTES
    # de qualquer escrita, e o modulo `sala_de_espera` continua a ser o real.
    #
    #     REAL_WAITING_ROOM_ITEMS_CREATED = 0.
    sala = tempfile.mkdtemp(prefix='espera-social-')
    morada_real = espera.MORADA
    espera.MORADA = sala
    try:
        estrada = a_estrada_do_scrap(url)
        sql = cc.Banco(url)
        ids_card = a_cardinalidade(url, sql)
        ids_sha = os_mesmos_bytes(url, sql)
        ids_runs, _erros = as_duas_corridas(url, sql)
        id_retry = o_retry(url, sql)
        # ⚠️ O RED TEAM PRECISA DE UM ALVO REAL, E ELE NAO SE INVENTA.
        # Uma arvore com a ponte partida chega aqui sem observacao nenhuma
        # nomeada por um READY — e nesse caso a bateria tem de dizer isso em
        # VERMELHO, e nao morrer com um traceback a meio.
        #
        #     UMA PROVA QUE REBENTA NAO DIZ O QUE FALHOU: DIZ QUE REBENTOU.
        alvo = ([x for x in [(estrada or {}).get('RAW'), id_retry]
                 if str(x).isdigit()] or [x for x in (ids_card or [])
                                          if str(x).isdigit()] or [None])[0]
        caso('X0_ha_uma_observacao_nomeada_por_um_READY_para_atacar',
             alvo is not None,
             'alvo do red team: %s' % alvo)
        if alvo is not None:
            o_red_team(url, sql, alvo, ids_sha, ids_runs)
        return _fechar()
    finally:
        espera.MORADA = morada_real
        shutil.rmtree(sala, ignore_errors=True)
        for a in _ARMAZEM:
            shutil.rmtree(a.raiz, ignore_errors=True)


if __name__ == '__main__':
    raise SystemExit(main())
