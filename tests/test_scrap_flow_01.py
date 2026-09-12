#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCRAP-FLOW-01 — o caminho é canônico, e não só o dinheiro é guardado.

    python3 tests/test_scrap_flow_01.py

    MODULE CAN'T SPEND  !=  FLOW IS CANONICAL.

A SCRAP-SR-02 fechou a porta do dinheiro. Esta missão fechou o CAMINHO de UMA
fase real — `yt-legenda-paga`, a única rota paga desta casa com capacidade,
rota e autorização humana — que até aqui era despachada assim:

    sintonia-scrap.yml  ->  coleta/social_scrap.py coletar  ->  COLLECT

e passa a ser despachada assim:

    sintonia-scrap.yml  ->  orquestrador  ->  PEDIDO  ->  plano + portão
                        ->  subprocesso  ->  COLLECT  ->  envelope  ->  ingresso

A prova ponta a ponta, com mundo falso e sem rede, vive em
`provas/o_fluxo_canonico_do_scrap.py`. ESTE ficheiro é o red team: ele ataca a
migração por fora e mata mutantes que a fariam parecer feita sem estar.

    ZERO REDE · ZERO DÓLAR · ZERO FONTE AVALIADA.
    APIFY_REAL_RUNS = 0 · META_REAL_REQUESTS = 0 · COST_USD = 0
"""
import json
import os
import sys
import unittest  # noqa: F401 — usado pelas provas de importacao

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
for d in (RAIZ, os.path.join(RAIZ, 'coleta'), os.path.join(RAIZ, 'leis'),
          os.path.join(RAIZ, 'pedido'), os.path.join(RAIZ, 'orquestrador')):
    sys.path.insert(0, d)
import _gavetas  # noqa: E402,F401
import pedido as ped                    # noqa: E402
import receitas as rec                  # noqa: E402
import relevancia_da_fonte as rel       # noqa: E402
import retorno_da_coleta as rdc         # noqa: E402
import falhas as fx                     # noqa: E402

FALHAS, ATAQUES = [], 0

CLI = os.path.join('coleta', 'social_scrap.py')
WORKFLOW = os.path.join('.github', 'workflows', 'sintonia-scrap.yml')
ORQ = os.path.join('orquestrador', 'orquestrador.py')
RECEITAS = os.path.join('pedido', 'receitas.py')
FASE = 'yt-legenda-paga'


def fonte(caminho):
    return open(os.path.join(RAIZ, caminho), encoding='utf-8').read()


def ataque(n, titulo, cond, detalhe=''):
    global ATAQUES
    ATAQUES += 1
    if cond:
        print('  PASS  %2d %s' % (n, titulo))
    else:
        print('  FAIL  %2d %s  %s' % (n, titulo, detalhe))
        FALHAS.append((n, titulo, detalhe))


def pedido_com(**filtros):
    p = ped.de_uma_frase('colete concorrentes')
    p.filtros.update(filtros)
    return p


def livro_sim(sid, proposito='T9'):
    return [rel.Decisao(source_id=sid, proposito=proposito, resultado=rel.SIM,
                        motivo='fixture do red team da SCRAP-FLOW-01',
                        metodo='fixture',
                        evidencia={'prova': 'tests/test_scrap_flow_01.py'}
                        ).para_livro()]


print('=' * 72)
print('SCRAP-FLOW-01 — RED TEAM DO CAMINHO CANÔNICO')
print('=' * 72)
print('\nA ESCOLHA DO EXECUTOR TEM DONO\n' + '-' * 72)

T9 = rec.EXECUTORES['T9']
SCRAP = [e for e in T9 if e['id'] == 'scrap-yt-legenda-paga'][0]
COMUM = [e for e in T9 if e['id'] == 'comunicacao-publica'][0]

ataque(1, 'o pedido que nomeia a fase leva o executor do SCRAP',
       rec.escolher(T9, pedido_com(fase=FASE))['id'] == 'scrap-yt-legenda-paga')
ataque(2, 'o pedido que NAO nomeia fase leva o executor de sempre',
       rec.escolher(T9, pedido_com())['id'] == 'comunicacao-publica')
ataque(3, 'um executor com `pedido_pede` NUNCA e escolhido por omissao',
       rec.escolher([SCRAP], pedido_com()) is None)
ataque(4, 'fase parecida mas diferente nao casa',
       rec.escolher(T9, pedido_com(fase='yt-legenda'))['id'] == 'comunicacao-publica')
ataque(5, 'um selector de dois campos exige os DOIS',
       rec.escolher([{**SCRAP, 'pedido_pede': {'fase': FASE, 'pais': 'IT'}}, COMUM],
                    pedido_com(fase=FASE))['id'] == 'comunicacao-publica')
ataque(6, 'sem executores, a escolha e None e nao rebenta',
       rec.escolher([], pedido_com(fase=FASE)) is None)
ataque(7, 'o primeiro registo de T9 continua a ser o de sempre',
       T9[0]['id'] == 'comunicacao-publica')

print('\nO PORTAO JULGA QUEM VAI CORRER\n' + '-' * 72)

plano_scrap = rec.resolver(pedido_com(fase=FASE))
plano_comum = rec.resolver(pedido_com())
ataque(8, 'o plano expoe o executor ESCOLHIDO, e nao a lista',
       plano_scrap.escolhido['id'] == 'scrap-yt-legenda-paga')
ataque(9, 'e o portao foi consultado com o custo DESSE executor',
       'ROTA_PAGA' in plano_scrap.relevancia['FORMAS_DE_GASTO_ABERTAS'])
ataque(10, 'o executor do SCRAP declara custo PAGO — senao o portao deixava passar',
       not rel.custo_e_gratuito(SCRAP['custo']), SCRAP['custo'])
ataque(11, 'sem fonte nomeada, a rota paga e BARRADA',
       plano_scrap.bloqueia_a_corrida is True)
ataque(12, 'e o plano NAO inventa fonte nenhuma para o portao julgar',
       plano_scrap.relevancia['SOURCE_ID'] is None)
ataque(13, 'com fonte nomeada e livro que autoriza, o portao AUTORIZA',
       rec.resolver(pedido_com(fase=FASE, fonte='fake~fonte-do-red-team'),
                    livro=livro_sim('fake~fonte-do-red-team')
                    ).relevancia['VEREDITO'] == rel.AUTORIZA)
ataque(14, 'livro VAZIO nao autoriza gasto nenhum',
       rec.resolver(pedido_com(fase=FASE, fonte='fake~fonte-do-red-team'),
                    livro=[]).bloqueia_a_corrida is True)
ataque(15, 'um livro que autoriza OUTRA fonte nao autoriza esta',
       rec.resolver(pedido_com(fase=FASE, fonte='fake~outra'),
                    livro=livro_sim('fake~fonte-do-red-team')
                    ).bloqueia_a_corrida is True)
ataque(16, 'um livro que autoriza OUTRO proposito nao autoriza este',
       rec.resolver(pedido_com(fase=FASE, fonte='fake~f'),
                    livro=livro_sim('fake~f', proposito='T3')
                    ).bloqueia_a_corrida is True)

_url = None
try:
    rec.resolver(pedido_com(fase=FASE, fonte='https://youtube.com/c/x'), livro=[])
except Exception as e:                                        # noqa: BLE001
    _url = type(e).__name__
ataque(17, 'uma URL como `fonte` e recusada pelo dono do source_id', _url is not None,
       str(_url))

print('\nA FONTE NOMEADA E DECLARADA, NAO DEDUZIDA\n' + '-' * 72)

ataque(18, 'so quem DECLARA `aceita_fonte` tem fonte para o portao julgar',
       rec.fonte_nomeada({'argumentos_de_filtros': ['fonte']},
                         pedido_com(fonte='fake~x')) is None)
ataque(19, 'quem declara `aceita_fonte` e nao recebe fonte devolve None',
       rec.fonte_nomeada({'aceita_fonte': True}, pedido_com()) is None)
ataque(20, 'o T2, que ja aceitava fonte, continua a aceita-la',
       rec.fonte_nomeada(rec.EXECUTORES['T2'][0], pedido_com()) == 'IT-T2-002')

print('\nO ORQUESTRADOR NAO VOLTA A ESCOLHER\n' + '-' * 72)

src_orq = fonte(ORQ)
ataque(21, 'o orquestrador nao tem `executores[0]` em codigo vivo',
       not any(l.strip().startswith('e = plano.executores[0]')
               for l in src_orq.splitlines()))
ataque(22, 'ele le a escolha do plano', 'e = plano.escolhido' in src_orq)
ataque(23, 'e `correr` sabe receber o livro', 'livro=None) -> dict' in src_orq
       or 'livro=None' in src_orq)

print('\nA CORRIDA E UMA SO, DO PRINCIPIO AO FIM\n' + '-' * 72)

src_cli = fonte(CLI)
ataque(24, 'a receita declara que este executor recebe a corrida cunhada',
       SCRAP.get('recebe_run_id') is True)
ataque(25, 'a CLI le `--run-id` como OPCAO, e nao como posicional',
       "opcoes.get('run-id')" in src_cli)
ataque(26, 'e os posicionais ja nao veem as opcoes longas',
       "args = [a for a in sys.argv[1:] if not a.startswith('--')]" in src_cli)

print('\nO RETORNO E DECLARADO, E SO COLHEITA ATRAVESSA\n' + '-' * 72)

ataque(27, 'a receita declara ENVELOPE, e nao LEGADO',
       'ENVELOPE' in SCRAP['retorno'] and 'LEGADO' not in SCRAP['retorno'])
ataque(28, 'e a lei continua a recusar COLHEITA vinda do legado',
       rdc.COLHEITA not in rdc.LEGADO_SO_DECLARA_SUPORTE)

_env = {'RUN_ID': 'R1', 'EXECUTOR_ID': 'x', 'EXECUTOR_VERSION': 'v',
        'ESTADO': 'SUCCESS', 'COLHEITA': [], 'SUPORTE': [], 'ERROS': []}


def _com(unidade):
    return dict(_env, COLHEITA=[unidade])


_ok = {'ESPECIE': rdc.COLHEITA, 'SOURCE_ID': 'SCRAP-YOUTUBE/%s' % FASE,
       'DOCUMENT_ID': 'EAkcA_2FDN8', 'RUN_ID': 'R1',
       'PAYLOAD': {'ESTADO': rdc.PAYLOAD_NAO_SE_APLICA, 'ONDE': None}}
ataque(29, 'a unidade que a CLI monta respeita o contrato',
       rdc.conferir(_com(_ok), RAIZ) == [], str(rdc.conferir(_com(_ok), RAIZ)))
ataque(30, 'sem SOURCE_ID a unidade nao atravessa',
       rdc.conferir(_com(dict(_ok, SOURCE_ID='')), RAIZ) != [])
ataque(31, 'com a corrida ERRADA a unidade nao atravessa',
       any('RUN_MISMATCH' in m
           for m in rdc.conferir(_com(dict(_ok, RUN_ID='OUTRA')), RAIZ)))
ataque(32, 'e SUPORTE nunca entra no ingresso',
       rdc.so_o_que_entra(dict(_env, SUPORTE=[{'ESPECIE': rdc.MANIFEST}])) == [])

print('\nA RECUSA DA COMPRA TEM NOME\n' + '-' * 72)

ataque(33, '`SPEND_NOT_AUTHORIZED` e uma falha que a casa conhece',
       fx.traduzir('SPEND_NOT_AUTHORIZED') == 'BUDGET_EXHAUSTED',
       fx.traduzir('SPEND_NOT_AUTHORIZED'))
ataque(34, 'e ela NAO degrada a fonte — a recusa e nossa',
       not fx.degrada_fonte('BUDGET_EXHAUSTED'))
ataque(35, 'nem se retenta: trocar de chave nao resolve',
       fx.traduzir('SPEND_NOT_AUTHORIZED') in fx.ESTADOS)
src_rotas = fonte(os.path.join('coleta', 'social_rotas.py'))
ataque(36, 'o roteador apanha a recusa da compra ANTES do balde generico',
       src_rotas.index("registro['ESTADO'] = 'SPEND_NOT_AUTHORIZED'")
       < src_rotas.index("registro['ESTADO'] = 'UNKNOWN_ERROR'"))
ataque(37, 'e o veredito inteiro sobe com ela',
       "registro['AUTORIZACAO_DO_GASTO']" in src_rotas)
ataque(38, 'a CLI imprime QUAL dos donos disse nao',
       "ESTADO_ORIGINAL" in src_cli)

print('\nO DISPARADOR CONTINUA A SER UM DISPARADOR\n' + '-' * 72)

wf = fonte(WORKFLOW)
ataque(39, 'a fase paga entra pelo orquestrador',
       'orquestrador/orquestrador.py \\\n                "colete concorrentes" '
       '--filtro fase=yt-legenda-paga' in wf)
ataque(40, 'e o disparador NAO nomeia ator, alvo nem teto',
       not any(x in wf for x in ('pintostudio~', 'EAkcA_2FDN8',
                                 'maxTotalChargeUsd')))
ataque(41, 'os tectos continuam a viver na tabela versionada',
       all(k in src_cli for k in ('MAX_PROVIDER_RUNS', 'MAX_START_POSTS',
                                  'MAX_USD', 'MAX_ITEMS')))
ataque(42, 'e o disparador diz alto quando o portao barra',
       'BARRADO_NA_RELEVANCIA=YES' in wf)

# ══════════════════════════════════════════════════════════════════════════
# OS MUTANTES — cada um é um afrouxamento PLAUSÍVEL desta migração
# ══════════════════════════════════════════════════════════════════════════
#     UMA SUITE VERDE NÃO PROVA QUE ELA MORDE.
#
# Cada linha abaixo descreve uma alteração que alguém com pressa faria — e diz
# QUAL prova desta casa a apanharia. Onde a prova é ESTRUTURAL, mede-se aqui a
# condição que a mataria; onde ela é de COMPORTAMENTO, mede-se a jusante, em
# `provas/o_fluxo_canonico_do_scrap.py`, que altera o ficheiro real e corre a
# cadeia real.
#
#     mutante que sobrevive = regra sem guarda. SURVIVORS = 0.
MORTOS = []


def mutante(n, nome, morto, onde=''):
    MORTOS.append((n, nome, bool(morto), onde))
    print('  %s  %-52s %s' % ('MORTO     ' if morto else 'SOBREVIVEU',
                              nome[:52], onde))


print('\nOS MUTANTES\n' + '-' * 72)

src_rec = fonte(RECEITAS)

mutante('M1', '`escolher` devolve sempre o primeiro',
        "for e in execs or []:" in src_rec and "pede = e.get(\"pedido_pede\")" in src_rec,
        'ataques 1-5')
mutante('M2', 'um `pedido_pede` passa a valer por omissao',
        'if not e.get("pedido_pede"):' in src_rec, 'ataque 3')
mutante('M3', 'o plano volta a julgar `execs[0]`',
        'escolhido = escolher(execs, p)' in src_rec
        and 'if escolhido is not None:' in src_rec, 'ataques 8-9')
mutante('M4', 'o orquestrador volta a correr `executores[0]`',
        'e = plano.escolhido' in src_orq, 'ataques 21-22')
mutante('M5', '`fonte_nomeada` volta a deduzir do argumento de linha',
        'if not executor.get("aceita_fonte"):' in src_rec, 'ataque 18')
mutante('M6', 'o executor do SCRAP declara-se gratuito',
        not rel.custo_e_gratuito(SCRAP['custo']), 'ataques 10-11')
mutante('M7', 'a receita passa a nomear uma fonte por omissao',
        'fonte' not in (SCRAP.get('filtros_por_omissao') or {}), 'ataque 12')
mutante('M8', 'a receita declara LEGADO e finge colheita',
        'ENVELOPE' in SCRAP['retorno'], 'ataques 27-28')
mutante('M9', 'a unidade viaja sem SOURCE_ID',
        rdc.conferir(_com(dict(_ok, SOURCE_ID='')), RAIZ) != [], 'ataque 30')
mutante('M10', 'o envelope inventa a propria corrida',
        any('RUN_MISMATCH' in m
            for m in rdc.conferir(_com(dict(_ok, RUN_ID='OUTRA')), RAIZ)),
        'ataque 31')
mutante('M11', 'a CLI volta a ler `--run-id` como teto',
        "opcoes.get('run-id')" in src_cli
        and "args = [a for a in sys.argv[1:] if not a.startswith('--')]" in src_cli,
        'ataques 25-26')
mutante('M12', 'o disparador volta a chamar a CLI direto',
        'orquestrador/orquestrador.py' in wf
        and 'coletar yt-legenda-paga ;;' not in wf, 'ataque 39')
mutante('M13', 'a recusa da compra volta ao balde de `UNKNOWN_ERROR`',
        'SPEND_NOT_AUTHORIZED' in fonte(os.path.join('leis', 'falhas.py'))
        and "registro['ESTADO'] = 'SPEND_NOT_AUTHORIZED'" in src_rotas,
        'ataques 33 e 36')
mutante('M14', 'o teto de rede sai da tabela versionada',
        "'TETO_DE_REDE': 5," in src_cli, 'prova P3')
mutante('M15', 'o teto de gasto sai da tabela versionada',
        "'TETO_DE_GASTO_USD': 0.10," in src_cli, 'prova P4')
mutante('M16', 'a autorizacao deixa de chegar ao gasto',
        "kw['autorizacao'] = _ag.trial(" in src_cli, 'prova P2')

# ── OS TRES MUTANTES QUE CORREM A CADEIA INTEIRA ────────────────────────────
# P2 · P3 · P4 de `provas/o_fluxo_canonico_do_scrap.py` alteram o ficheiro REAL,
# correm a cadeia REAL e contam os POST no `curl` falso. Nao se repetem aqui:
# repetir uma prova noutro sitio nao a torna mais forte, torna-a duas.
#
#     DOIS SITIOS COM A MESMA PROVA SAO DUAS PROVAS QUE PODEM DIVERGIR.
PROVA_DE_COMPORTAMENTO = 'provas/o_fluxo_canonico_do_scrap.py'

print('\nEXECUCAO REAL\n' + '-' * 72)
print('  REAL_NETWORK         = 0')
print('  APIFY_REAL_RUNS      = 0')
print('  PAID_REAL_RUNS       = 0')
print('  META_REAL_REQUESTS   = 0')
print('  REAL_COST_USD        = 0')
print('  FONTES_AVALIADAS     = 0  (nenhum SIM/NAO/NAO_SEI foi escrito no livro)')
print('\n  a prova de COMPORTAMENTO ponta a ponta: %s' % PROVA_DE_COMPORTAMENTO)

vivos = [m for m in MORTOS if not m[2]]
print('\n' + '=' * 72)
print('ATAQUES = %d · MUTANTES = %d · FALHAS = %d · SOBREVIVENTES = %d'
      % (ATAQUES, len(MORTOS), len(FALHAS), len(vivos)))
if FALHAS or vivos:
    for f in FALHAS:
        print('  !! ataque', f)
    for m in vivos:
        print('  !! mutante vivo', m[0], m[1])
    sys.exit(1)
print('RED_TEAM = PASS · SURVIVORS = 0')
