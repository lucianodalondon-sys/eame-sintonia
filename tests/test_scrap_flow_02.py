#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCRAP-FLOW-02 — uma rota GRATUITA atravessa o fluxo canônico.

    python3 tests/test_scrap_flow_02.py

    FREE != CANONICAL.  ROUTE WORKS != FLOW WORKS.  FREE_ROUTE != NO_GATES.

A SCRAP-FLOW-01 levou a fase PAGA ao caminho canônico e deixou escrito o que
ficava por fechar: `janela*` continuava a saltar o orquestrador. Esta missão
fechou-a — e só ela.

A prova de COMPORTAMENTO, ponta a ponta e com um navegador falso que fala CDP
por socket real, vive em `provas/o_fluxo_gratuito_do_scrap.py`. ESTE ficheiro é
o red team: ataca a migração por fora e mata mutantes que a fariam parecer
feita sem estar.

    ZERO REDE · ZERO DÓLAR · ZERO FONTE AVALIADA.
    REAL_NETWORK = 0 · META_REAL_REQUESTS = 0 · COST_USD = 0
"""
import json
import os
import sys
import unittest  # noqa: F401 — usado pelas provas de importacao

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
for d in (RAIZ, os.path.join(RAIZ, 'coleta'), os.path.join(RAIZ, 'leis'),
          os.path.join(RAIZ, 'pedido'), os.path.join(RAIZ, 'orquestrador'),
          os.path.join(RAIZ, 'ferramentas')):
    sys.path.insert(0, d)
import _gavetas  # noqa: E402,F401
import pedido as ped                    # noqa: E402
import receitas as rec                  # noqa: E402
import relevancia_da_fonte as rel       # noqa: E402
import retorno_da_coleta as rdc         # noqa: E402
import falhas as fx                     # noqa: E402
import social_matriz as mz              # noqa: E402

FALHAS, ATAQUES = [], 0

CLI = os.path.join('coleta', 'social_scrap.py')
WORKFLOW = os.path.join('.github', 'workflows', 'sintonia-scrap.yml')
ORQ = os.path.join('orquestrador', 'orquestrador.py')
RECEITAS = os.path.join('pedido', 'receitas.py')
ROTAS = os.path.join('coleta', 'social_rotas.py')
ADAPTER = os.path.join('coleta', 'adaptador_instagram.py')
FASES = ('janela', 'janela-perfis', 'janela-objetos')


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


def livro(sid, resultado, proposito='T9'):
    return [rel.Decisao(source_id=sid, proposito=proposito, resultado=resultado,
                        motivo='fixture do red team da SCRAP-FLOW-02',
                        metodo='fixture',
                        evidencia={'prova': 'tests/test_scrap_flow_02.py'}
                        ).para_livro()]


T9 = rec.EXECUTORES['T9']
JANELA = [e for e in T9 if e['id'] == 'scrap-janela'][0]
PAGA = [e for e in T9 if e['id'] == 'scrap-yt-legenda-paga'][0]
COMUM = [e for e in T9 if e['id'] == 'comunicacao-publica'][0]
src_cli, src_orq = fonte(CLI), fonte(ORQ)
src_rec, src_rotas = fonte(RECEITAS), fonte(ROTAS)
src_adp, wf = fonte(ADAPTER), fonte(WORKFLOW)

print('=' * 72)
print('SCRAP-FLOW-02 — RED TEAM DA SEGUNDA ROTA, A GRATUITA')
print('=' * 72)
print('\nO DISPARADOR NÃO É O MOTOR\n' + '-' * 72)

ramo = wf.split('janela|janela-perfis|janela-objetos)', 1)
_ramo = ramo[1].split(';;', 1)[0] if len(ramo) == 2 else ''
ataque(1, 'o workflow NAO chama o adaptador direto',
       not any(x in _ramo for x in ('adaptador_', 'instagram_janela', 'cdp.py')))
ataque(2, 'o workflow NAO chama a CLI do SCRAP',
       'coleta/social_scrap.py' not in _ramo, _ramo.strip()[:60])
ataque(3, 'ele entra pelo orquestrador',
       'orquestrador/orquestrador.py' in _ramo)
ataque(4, 'e diz AO PEDIDO qual e a fase, em vez de a executar',
       '--filtro fase=' in _ramo)
ataque(5, 'o disparador NAO conhece o nome do executor',
       'scrap-janela' not in wf)
ataque(6, 'nem o nome do ficheiro que colhe',
       'instagram_janela' not in _ramo)
ataque(7, 'e o caminho antigo desapareceu do ramo',
       'coletar "${{ inputs.fase }}"' not in wf)

print('\nO PEDIDO ESCOLHE, E A ORDEM NÃO DECIDE\n' + '-' * 72)

for i, f in enumerate(FASES):
    ataque(8 + i, 'a fase «%s» abre o executor da janela' % f,
           rec.escolher(T9, pedido_com(fase=f))['id'] == 'scrap-janela')
ataque(11, 'quem NAO nomeia fase leva o executor de sempre',
       rec.escolher(T9, pedido_com())['id'] == 'comunicacao-publica')
ataque(12, 'uma fase parecida mas diferente NAO abre a janela',
       rec.escolher(T9, pedido_com(fase='janela-de-sotao'))['id']
       == 'comunicacao-publica')

_falso = {'id': 'falso', 'roda': ['x'], 'rotas': [], 'custo': 'gratuito',
          'o_que_traz': '', 'pedido_pede': {'fase': 'nunca-pedida'}}
_ordens = {
    'antes': [_falso] + list(T9),
    'depois': list(T9) + [_falso],
    'invertida': list(reversed(T9)),
    'baralhada': [T9[1], _falso, T9[2], T9[0]] if len(T9) >= 3 else list(T9),
}
ataque(13, 'a escolha NAO depende da ordem da lista',
       len({rec.escolher(l, pedido_com(fase='janela'))['id']
            for l in _ordens.values()}) == 1,
       str({k: rec.escolher(l, pedido_com(fase='janela'))['id']
            for k, l in _ordens.items()}))
ataque(14, 'um executor com selector NUNCA e escolhido por omissao',
       rec.escolher([JANELA, PAGA], pedido_com()) is None)
ataque(15, 'e o dono da escolha e UM: nao ha `executores[0]` vivo',
       'e = plano.escolhido' in src_orq
       and not any(l.strip().startswith('e = plano.executores[0]')
                   for l in src_orq.splitlines()))
ataque(16, 'o adaptador NAO escolhe executor nenhum',
       'escolher(' not in src_adp and 'EXECUTORES' not in src_adp)

print('\nGRÁTIS NÃO É SEM PORTÃO\n' + '-' * 72)

plano = rec.resolver(pedido_com(fase='janela'))
ataque(17, 'o executor declara-se gratuito na lingua do dono da lei',
       rel.custo_e_gratuito(JANELA['custo']), JANELA['custo'])
ataque(18, 'e a rota gratuita NAO abre forma de gasto nenhuma',
       plano.relevancia['FORMAS_DE_GASTO_ABERTAS'] == [])
ataque(19, 'o portao e consultado na mesma',
       plano.relevancia['VEREDITO'] == rel.EXIGE_AVALIACAO)
ataque(20, 'e NAO barra quem ninguem avaliou — observar barato continua livre',
       plano.bloqueia_a_corrida is False and plano.barra_a_observacao is False)
_barrado = rec.resolver(pedido_com(fase='yt-legenda-paga', fonte='fake~barrada'),
                        livro=livro('fake~barrada', rel.NAO))
ataque(21, 'um NAO explicito barra a observacao, mesmo sem gasto',
       _barrado.barra_a_observacao is True)
ataque(22, 'e o orquestrador OBEDECE esse campo, e nao so o do gasto',
       'plano.barra_a_observacao' in src_orq)
ataque(23, 'NAO_SE_APLICA tambem barra — a pergunta nao faz sentido',
       rec.resolver(pedido_com(fase='yt-legenda-paga', fonte='fake~na'),
                    livro=livro('fake~na', rel.NAO_SE_APLICA)
                    ).barra_a_observacao is True)
ataque(24, 'a rota gratuita NAO exige orcamento financeiro para correr',
       'teto_de_gasto' not in _ramo and 'FASES_PAGAS' not in _ramo)
ataque(25, 'e a fase da janela NAO esta na tabela das fases pagas',
       all(f not in src_cli.split('FASES_PAGAS = {', 1)[1].split('\n}', 1)[0]
           for f in FASES))

print('\nA FONTE NÃO É INVENTADA\n' + '-' * 72)

ataque(26, 'o executor da janela DECLARA que nao aceita fonte',
       JANELA.get('aceita_fonte') is False)
ataque(27, 'e por isso o plano nao nomeia fonte nenhuma',
       plano.relevancia['SOURCE_ID'] is None)
ataque(28, 'a receita NAO escreve nenhuma das 77 fontes para esta rota',
       'IT-T9-0' not in json.dumps(JANELA, ensure_ascii=False))
_url = None
try:
    rel.conferir_source_id('https://www.instagram.com/basf_agroes/')
except Exception as e:                                        # noqa: BLE001
    _url = type(e).__name__
ataque(29, 'uma URL continua a ser recusada como SOURCE_ID', _url is not None,
       str(_url))
ataque(30, 'a origem de cada unidade sai do ARTEFATO, nao deste codigo',
       "origem = str(d.get('SOURCE_ID') or '').strip()" in src_adp)
ataque(31, 'e quem chega sem origem NAO recebe uma inventada',
       "sem_origem += 1" in src_cli and "'SOURCE_ID': origem," in src_cli)
ataque(32, 'o literal da origem paga vive num sitio so',
       src_cli.count("'%s/%s' % (os.path.basename(GAVETA_PAGA), fase)") == 1
       and "'SCRAP-YOUTUBE/%s' % fase" not in src_cli)

print('\nA CORRIDA É UMA SÓ, E O RETORNO É DECLARADO\n' + '-' * 72)

ataque(33, 'a receita declara que este executor recebe a corrida cunhada',
       JANELA.get('recebe_run_id') is True)
ataque(34, 'a CLI le `--run-id` como OPCAO, e nao como posicional',
       "opcoes.get('run-id')" in src_cli)
# ⚠️ A ANCORA E A CHAMADA DO EXECUTOR, e nao a primeira `subprocess.run` do
# ficheiro — essa e a do `git log` que carimba a versao, e vem muito antes.
# Uma ancora que apanha a chamada errada passa por acidente.
ataque(35, 'o RUN_ID nasce ANTES de o executor correr',
       src_orq.index('run_id = novo_run_id(p)')
       < src_orq.index('subprocess.run([sys.executable, *comando]'))
ataque(36, 'a receita declara ENVELOPE, e nao LEGADO',
       'ENVELOPE' in JANELA['retorno'] and 'LEGADO' not in JANELA['retorno'])
ataque(37, 'e a lei continua a recusar COLHEITA vinda do legado',
       rdc.COLHEITA not in rdc.LEGADO_SO_DECLARA_SUPORTE)

_env = {'RUN_ID': 'R1', 'EXECUTOR_ID': 'x', 'EXECUTOR_VERSION': 'v',
        'ESTADO': 'SUCCESS', 'COLHEITA': [], 'SUPORTE': [], 'ERROS': []}
_ok = {'ESPECIE': rdc.COLHEITA, 'SOURCE_ID': 'INSTAGRAM-JANELA/PERFIS',
       'DOCUMENT_ID': 'basf_agroes', 'RUN_ID': 'R1',
       'PAYLOAD': {'ESTADO': rdc.PAYLOAD_NAO_SE_APLICA, 'ONDE': None}}


def _com(u):
    return dict(_env, COLHEITA=[u])


ataque(38, 'a unidade que esta rota monta respeita o contrato',
       rdc.conferir(_com(_ok), RAIZ) == [], str(rdc.conferir(_com(_ok), RAIZ)))
ataque(39, 'com a corrida ERRADA a unidade nao atravessa',
       any('RUN_MISMATCH' in m
           for m in rdc.conferir(_com(dict(_ok, RUN_ID='OUTRA')), RAIZ)))
ataque(40, 'um caminho de saida NAO vira identidade',
       any('fabricado' in m.lower() for m in rdc.conferir(_com(dict(
           _ok, DOCUMENT_ID='data/samples/INSTAGRAM-JANELA/PERFIS.json',
           PAYLOAD={'ESTADO': rdc.AUSENTE,
                    'ONDE': 'data/samples/INSTAGRAM-JANELA/PERFIS.json'})), RAIZ))
       or rdc.conferir(_com(dict(
           _ok, DOCUMENT_ID='data/samples/INSTAGRAM-JANELA/PERFIS.json',
           PAYLOAD={'ESTADO': rdc.AUSENTE,
                    'ONDE': 'data/samples/INSTAGRAM-JANELA/PERFIS.json'})),
           RAIZ) != [])
ataque(41, 'ausencia de ficheiro NAO se declara PRESENTE',
       rdc.estado_do_payload('data/nao-existe.gz', RAIZ) == rdc.AUSENTE)
ataque(42, 'e um envelope que afirma preservado sem bytes e recusado',
       rdc.conferir(_com(dict(_ok, PAYLOAD={'ESTADO': rdc.PRESENTE,
                                            'ONDE': 'data/nao-existe.gz'})),
                    RAIZ) != [])

print('\nA RECUSA TEM NOME, E NÃO TOCA NO MUNDO\n' + '-' * 72)

ataque(43, '«a ferramenta nao esta la» tem familia propria',
       fx.traduzir('BROWSER_NOT_REACHED') == 'EXECUTOR_UNAVAILABLE',
       fx.traduzir('BROWSER_NOT_REACHED'))
ataque(44, 'e ela NAO degrada a fonte — nada foi medido sobre ela',
       not fx.degrada_fonte('EXECUTOR_UNAVAILABLE'))
ataque(45, 'o roteador apanha-a ANTES do balde generico',
       src_rotas.index("registro['ESTADO'] = 'BROWSER_NOT_REACHED'")
       < src_rotas.index("registro['ESTADO'] = 'UNKNOWN_ERROR'"))
ataque(46, 'ERRO e REJEITADO continuam a ser palavras diferentes',
       'REJEITADO' in ped.ESTADOS and 'ERRO' in ped.ESTADOS
       and ped.REJEITADO != ped.ERRO)
ataque(47, 'a politica continua soberana sobre esta rota',
       mz.decisao('INSTAGRAM', 'INCREMENTAL')['PERMITIDA'] in
       ('CONDICIONAL', 'SIM', 'NAO'))
ataque(48, 'e o teto de acessos continua a ser dono do seu eixo',
       'orcamento_de_rede' in fonte(os.path.join('coleta', 'scrap_http.py')))

print('\nO CAMINHO ANTIGO MORREU\n' + '-' * 72)

ataque(49, 'nenhum workflow desta casa chama `coletar janela`',
       not any('coletar janela' in fonte(os.path.join('.github', 'workflows', n))
               for n in os.listdir(os.path.join(RAIZ, '.github', 'workflows'))
               if n.endswith('.yml')))
ataque(50, 'e `janela` deixou de estar na lista de desvios declarados',
       all(f not in src_cli.split('FASES_QUE_NAO_ATRAVESSAM_O_BOUNDARY = {', 1)[1]
           .split('}', 1)[0] for f in FASES))
ataque(51, 'a fase paga da FLOW-01 continua canonica',
       'orquestrador/orquestrador.py' in wf.split('yt-legenda-paga)', 1)[1]
       .split(';;', 1)[0])

# ══════════════════════════════════════════════════════════════════════════
# OS MUTANTES — cada um é um afrouxamento PLAUSÍVEL desta migração
# ══════════════════════════════════════════════════════════════════════════
#     UMA SUITE VERDE NÃO PROVA QUE ELA MORDE.
#
# Onde a defesa é ESTRUTURAL, mede-se aqui a condição que a mataria. Onde ela é
# de COMPORTAMENTO — política, relevância, navegador —, ela corre a jusante, em
# `provas/o_fluxo_gratuito_do_scrap.py`, que altera o ficheiro REAL, corre a
# cadeia REAL contra o navegador falso e conta os pedidos CDP.
#
#     DOIS SÍTIOS COM A MESMA PROVA SÃO DUAS PROVAS QUE PODEM DIVERGIR.
MORTOS = []


def mutante(n, nome, morto, onde=''):
    MORTOS.append((n, nome, bool(morto), onde))
    print('  %s  %-50s %s' % ('MORTO     ' if morto else 'SOBREVIVEU',
                              nome[:50], onde))


print('\nOS MUTANTES\n' + '-' * 72)

mutante('M1', 'o disparador volta a chamar a CLI direto',
        'coleta/social_scrap.py' not in _ramo
        and 'orquestrador/orquestrador.py' in _ramo, 'ataques 2-3')
mutante('M2', 'o disparador salta o pedido e nomeia a rota',
        '--filtro fase=' in _ramo and 'instagram_janela' not in _ramo,
        'ataques 4 e 6')
mutante('M3', 'a escolha volta a ser o indice zero',
        'e = plano.escolhido' in src_orq, 'ataque 15')
mutante('M4', 'a escolha passa a depender da ordem da lista',
        'def escolher(' in src_rec and 'def _casa(' in src_rec, 'ataque 13')
mutante('M5', 'um selector passa a valer por omissao',
        'if not e.get("pedido_pede"):' in src_rec, 'ataque 14')
mutante('M6', 'nasce um segundo RUN dentro do SCRAP',
        "opcoes.get('run-id')" in src_cli
        and JANELA.get('recebe_run_id') is True, 'ataques 33-34')
mutante('M7', 'o RUN_ID passa a nascer depois do executor',
        src_orq.index('run_id = novo_run_id(p)')
        < src_orq.index('subprocess.run([sys.executable, *comando]'), 'ataque 35')
mutante('M8', 'uma URL vira SOURCE_ID',
        _url is not None, 'ataque 29')
mutante('M9', 'a receita nomeia uma das 77 para o portao ter o que julgar',
        JANELA.get('aceita_fonte') is False
        and 'IT-T9-0' not in json.dumps(JANELA, ensure_ascii=False),
        'ataques 26-28')
mutante('M10', 'a origem passa a ser deduzida da fase',
        "'SCRAP-YOUTUBE/%s' % fase" not in src_cli, 'ataque 32')
mutante('M11', 'o retorno deixa de ser declarado',
        'ENVELOPE' in JANELA['retorno']
        and '_declarar_o_retorno(' in src_cli, 'ataque 36')
mutante('M12', 'output ausente passa por payload preservado',
        rdc.conferir(_com(dict(_ok, PAYLOAD={'ESTADO': rdc.PRESENTE,
                                             'ONDE': 'data/nao-existe.gz'})),
                     RAIZ) != [], 'ataque 42')
mutante('M13', 'a rota gratuita passa a exigir orcamento pago',
        all(f not in src_cli.split('FASES_PAGAS = {', 1)[1].split('\n}', 1)[0]
            for f in FASES), 'ataques 24-25')
mutante('M14', 'a recusa explicita da fonte deixa de ser obedecida',
        'plano.barra_a_observacao' in src_orq
        and 'PODE_OBSERVAR_BARATO' in src_rec, 'ataques 21-23')
mutante('M15', '«sem navegador» volta ao balde de UNKNOWN_ERROR',
        "registro['ESTADO'] = 'BROWSER_NOT_REACHED'" in src_rotas
        and fx.traduzir('BROWSER_NOT_REACHED') == 'EXECUTOR_UNAVAILABLE',
        'ataques 43 e 45')
mutante('M16', 'o caminho legado continua executavel a par do novo',
        not any('coletar janela' in fonte(os.path.join('.github', 'workflows', n))
                for n in os.listdir(os.path.join(RAIZ, '.github', 'workflows'))
                if n.endswith('.yml')), 'ataque 49')
mutante('M17', 'o adaptador passa a escolher executor',
        'EXECUTORES' not in src_adp, 'ataque 16')
mutante('M18', 'a fase paga da FLOW-01 volta a saltar o orquestrador',
        'orquestrador/orquestrador.py' in wf.split('yt-legenda-paga)', 1)[1]
        .split(';;', 1)[0], 'ataque 51')

PROVA_DE_COMPORTAMENTO = 'provas/o_fluxo_gratuito_do_scrap.py'

print('\nEXECUCAO REAL\n' + '-' * 72)
print('  REAL_NETWORK         = 0')
print('  META_REAL_REQUESTS   = 0')
print('  APIFY_REAL_RUNS      = 0')
print('  PAID_REAL_RUNS       = 0')
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
