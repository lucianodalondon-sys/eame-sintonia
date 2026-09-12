#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCRAP-RC-01 — O CANÁRIO DA RELEASE V1 ATRAVESSA A ÁRVORE INTEIRA.

    python3 provas/o_canario_do_scrap_v1.py

§8 pede UMA rota gratuita, permitida, sem credencial paga, sem navegador
autenticado e sem fornecedor pago. Medidas as candidatas em vez de assumidas:

    instagram.profile.discovery   PARTIAL · LOCAL · DATACENTER_BLOCKED
    bluesky.author.incremental    PROVEN  · ONLINE · grátis · sem credencial

A primeira era a única que o caminho canônico sabia pedir — e é a única que
este ambiente não consegue correr. O canário é a segunda.

    O CANÁRIO EXISTE PARA PROVAR A MÁQUINA, NÃO A PLATAFORMA MAIS IMPORTANTE.

ISTO NÃO É OPERAÇÃO AO VIVO, E O §10 É QUEM O DIZ
--------------------------------------------------
Nenhuma fonte do atlas está aprovada para nenhum propósito, e nenhuma ficha do
atlas é uma conta Bluesky. Sem isso não há canário REAL — há a árvore provada
offline, que é o que esta prova é, e que não se chama operação normal.

    SCRAP_ENGINE_READY != SCRAP_OPERATIONAL_READY.

O SOURCE_ID daqui é o do PEDIDO e serve para provar que ele desce inteiro até à
porta. Ele NÃO é uma decisão de relevância, e esta prova não escreve nenhuma.

O QUE É FALSO AQUI, E SÓ ISSO
-------------------------------
`urllib.request.urlopen` — o socket. Ver `provas/_rc01_mundo_falso.py`. São
reais o orquestrador, o plano, o adapter, o executor, o portão do `robots`, o
teto de rede, o roteador, a política de rota, o adaptador, a guarda de gasto,
o contrato de retorno, o ingresso e a admissão.

    REAL_NETWORK = 0 · APIFY_RUNS = 0 · PROVIDER_RUNS = 0 · COST_USD = 0
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in ('orquestrador', 'pedido', 'coleta', 'leis', 'regras', 'ferramentas',
           'medidas', 'guarda', ''):
    sys.path.insert(0, os.path.join(RAIZ, _p) if _p else RAIZ)

import pedido as pd                 # noqa: E402
import receitas as rec              # noqa: E402
import relevancia_da_fonte as rl    # noqa: E402
import retorno_da_coleta as rc      # noqa: E402
import scrap_capacidades as cap     # noqa: E402
import scrap_colheita as sc         # noqa: E402

FALHAS = []

FASE = 'canario-bluesky'
CAPACIDADE = 'bluesky.author.incremental'
FONTE = 'IT-T9-001'
PROPOSITO = 'comunicacao publica de concorrente'
HANDLE = 'canario-do-scrap.exemplo.invalido'

MUNDO = os.path.join(RAIZ, 'provas', '_rc01_mundo_falso.py')
PESADAS = {'.git', 'data', 'node_modules', 'italia-portale', '__pycache__',
           '.tmp', 'build'}


def diz(ok, titulo, detalhe=''):
    print('  %-5s %-54s %s' % ('ok' if ok else 'FALHA', titulo[:54],
                               str(detalhe)[:54]))
    if not ok:
        FALHAS.append(titulo)


def arvore(destino):
    """Cópia leve da árvore, com o mundo falso lá dentro. → a raiz da cópia."""
    for nome in os.listdir(RAIZ):
        if nome in PESADAS:
            continue
        o, a = os.path.join(RAIZ, nome), os.path.join(destino, nome)
        if os.path.isdir(o):
            shutil.copytree(o, a, symlinks=True,
                            ignore=shutil.ignore_patterns('__pycache__',
                                                          'node_modules'))
        else:
            shutil.copy2(o, a)
    os.symlink(os.path.join(RAIZ, '.git'), os.path.join(destino, '.git'))
    # `data/` é COPIADO e não ligado: o ingresso escreve RAW, e uma prova não
    # escreve no acervo verdadeiro.
    shutil.copytree(os.path.join(RAIZ, 'data'), os.path.join(destino, 'data'),
                    symlinks=True)
    return destino


#: ⚠️ O FALSO TEM DE VIVER NO ARRANQUE DO INTERPRETADOR, E NÃO NO DRIVER.
#: A primeira versão desta prova instalava o mundo falso dentro do driver e
#: mediu ZERO idas ao mundo — porque o orquestrador corre o adapter como
#: PROCESSO SEPARADO, e esse neto arranca com o `urlopen` verdadeiro.
#:
#:     A `SCRAP-FLOW-01` já tinha pago esta lição UM ANDAR ACIMA:
#:     UM FALSO QUE VIVE NA MEMÓRIA DO PAI NÃO EXISTE PARA O FILHO.
#:
#: `sitecustomize` é o ponto que o próprio Python abre para isto: o `site`
#: importa-o ANTES de qualquer linha da árvore correr, em TODO processo que
#: leve este diretório no `PYTHONPATH`. Assim o socket é falso desde o
#: primeiro instante, em todos os andares, e nada acima dele sabe disso.
GANCHO = """
import importlib.util, sys
spec = importlib.util.spec_from_file_location('_rc01_mundo_falso', %r)
mundo = importlib.util.module_from_spec(spec)
sys.modules['_rc01_mundo_falso'] = mundo
spec.loader.exec_module(mundo)
mundo.instalar()
"""

DRIVER = """
import json, os, sys
RAIZ = os.path.dirname(os.path.abspath(__file__))
for p in ('orquestrador','pedido','coleta','leis','regras',
          'ferramentas','medidas','guarda',''):
    sys.path.insert(0, os.path.join(RAIZ, p) if p else RAIZ)
import orquestrador as orq, pedido as pd
fonte = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] != '-' else None
handle = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] != '-' else None
p = pd.de_uma_frase('colete concorrentes')
p.filtros.update({'fase': '%s', 'pais': 'IT'})
if fonte:
    p.filtros['fonte'] = fonte
if handle:
    p.filtros['handle'] = handle
recibo = orq.correr(p)
recibo.pop('_plano', None)
print('<<<RECIBO>>>' + json.dumps(recibo, ensure_ascii=False, default=str))
""" % FASE


def correr(base, fonte=FONTE, handle=HANDLE):
    """Corre o caminho inteiro DENTRO da cópia. → (recibo, envelope, idas)."""
    driver = os.path.join(base, '_rc01_driver.py')
    with open(driver, 'w', encoding='utf-8') as f:
        f.write(DRIVER)
    marca = os.path.join(base, 'IDAS-AO-MUNDO.json')
    if os.path.isfile(marca):
        os.remove(marca)
    gancho = os.path.join(os.path.dirname(base), 'gancho')
    os.makedirs(gancho, exist_ok=True)
    with open(os.path.join(gancho, 'sitecustomize.py'), 'w',
              encoding='utf-8') as f:
        f.write(GANCHO % MUNDO)
    amb = dict(os.environ, RC01_MARCA=base, PYTHONIOENCODING='utf-8',
               PYTHONPATH=gancho)
    r = subprocess.run([sys.executable, driver, fonte or '-', handle or '-'],
                       cwd=base, capture_output=True, text=True, env=amb,
                       timeout=600)
    recibo = {}
    for linha in (r.stdout or '').splitlines():
        if linha.startswith('<<<RECIBO>>>'):
            recibo = json.loads(linha[len('<<<RECIBO>>>'):])
    if not recibo:
        print((r.stdout or '')[-1500:])
        print((r.stderr or '')[-1500:])
    env = {}
    alvo = os.path.join(base, sc.ENVELOPE)
    if os.path.isfile(alvo):
        with open(alvo, encoding='utf-8') as f:
            env = json.load(f)
    idas = []
    if os.path.isfile(marca):
        with open(marca, encoding='utf-8') as f:
            idas = json.load(f)
    return recibo, env, idas


def main():
    print(__doc__.strip().splitlines()[0])
    print('=' * 74)
    tmp = tempfile.mkdtemp(prefix='rc01-')
    base = os.path.join(tmp, 'arvore')
    os.makedirs(base)
    ficha = {}
    try:
        arvore(base)

        print('\n1 · A ESCOLHA DO CANÁRIO FOI MEDIDA, NÃO ASSUMIDA')
        diz(cap.estado(CAPACIDADE) == 'PROVEN', 'a capacidade está PROVEN',
            cap.estado(CAPACIDADE))
        alvo, porque = cap.onde(CAPACIDADE)
        diz(alvo == 'ONLINE', 'e corre ONLINE — não exige máquina residencial',
            '%s %s' % (alvo, porque or ''))
        outro, porque2 = cap.onde('instagram.profile.discovery')
        diz(outro != 'ONLINE',
            'a fase que já existia era a que este ambiente não corre',
            '%s %s' % (outro, porque2 or ''))

        print('\n2 · O PEDIDO ESCOLHE O EXECUTOR CANÔNICO, E LEVA O ALVO')
        p = pd.de_uma_frase('colete concorrentes')
        p.filtros.update({'fase': FASE, 'fonte': FONTE, 'handle': HANDLE})
        e = rec.resolver(p).executores[0]
        diz(e['id'] == 'scrap-colheita', 'o plano escolhe o executor do SCRAP',
            e['id'])
        diz(FASE in (e.get('serve_fases') or []),
            'e a receita serve esta fase', e.get('serve_fases'))
        diz('handle' in (e.get('filtros_nomeados') or []),
            'o alvo desce como filtro NOMEADO, não como posicional',
            e.get('filtros_nomeados'))
        diz('handle' not in json.dumps(p.para_json()).lower().split('fonte')[0]
            or p.filtros.get('handle') != p.filtros.get('fonte'),
            'e o alvo NÃO é a fonte — são dois campos',
            '%s != %s' % (p.filtros.get('handle'), p.filtros.get('fonte')))

        print('\n3 · O PORTÃO DA RELEVÂNCIA RESPONDE — E NÃO BARRA O GRÁTIS')
        livro = rl.ler_livro(RAIZ)
        v = rl.portao(FONTE, PROPOSITO, livro, custo=rl.CUSTO_DECLARADO_GRATUITO,
                      acionamento='PONTUAL', escopo='PONTUAL')
        diz(v['VEREDITO'] == rl.EXIGE_AVALIACAO,
            'sem decisão no livro o veredito é EXIGE_AVALIACAO', v['VEREDITO'])
        diz(v['FORMAS_DE_GASTO_ABERTAS'] == [],
            'uma rota grátis e pontual não abre forma de gasto nenhuma',
            v['FORMAS_DE_GASTO_ABERTAS'])
        diz(v['BLOQUEIA_A_CORRIDA'] is False,
            'e por isso ela não bloqueia a corrida (COL-LAW-018)',
            'BLOQUEIA_A_CORRIDA=%s' % v['BLOQUEIA_A_CORRIDA'])
        diz(v['PODE_GASTAR'] is False,
            'mas continua a não autorizar gasto nenhum', 'PODE_GASTAR=False')

        print('\n4 · A ÁRVORE INTEIRA CORRE, COM O SOCKET FALSO')
        recibo, env, idas = correr(base)
        diz(recibo.get('STATUS') == 'SUCCESS', 'a corrida correu',
            recibo.get('STATUS'))
        diz(bool(recibo.get('RUN_ID')), 'o orquestrador cunhou o RUN_ID',
            recibo.get('RUN_ID'))
        diz(env.get('RUN_ID') == recibo.get('RUN_ID'),
            'e o adapter usou ESSE, e não outro', env.get('RUN_ID'))
        diz(recibo.get('ACTOR') == 'coleta/scrap_colheita.py',
            'o recibo nomeia o executor do SCRAP', recibo.get('ACTOR'))
        diz(env.get('CAPABILITY') == CAPACIDADE,
            'e a capacidade que correu é a do canário', env.get('CAPABILITY'))

        print('\n5 · O PORTÃO DO ROBOTS E A ROTA FORAM MESMO AO MUNDO')
        robots = [u for u in idas if u.endswith('/robots.txt')]
        rota = [u for u in idas if 'getAuthorFeed' in u]
        diz(len(robots) >= 1, 'o portão do robots foi consultado', robots[:1])
        diz(len(rota) == 1, 'a rota foi pedida UMA vez', len(rota))
        diz(all('public.api.bsky.app' in u for u in idas),
            'e nenhum endereço fora da AppView pública foi tocado', len(idas))
        diz(('actor=%s' % HANDLE) in (rota[0] if rota else ''),
            'o alvo do pedido chegou inteiro à rota', HANDLE)

        print('\n6 · RAW ANTES DE NORMALIZAR, COM O BYTE NO DISCO')
        u = (env.get('COLHEITA') or [{}])[0]
        obs = u.get('OBSERVACAO') or {}
        raw = obs.get('RAW_REFERENCE') or {}
        caminho = os.path.join(base, raw.get('PATH') or '')
        diz(bool(raw.get('SHA256')), 'a observação traz o SHA do bruto',
            (raw.get('SHA256') or '')[:20])
        diz(os.path.isfile(caminho), 'e o byte está no disco', raw.get('PATH'))
        # ⚠️ O CAMPO CHAMA-SE `PRESERVATION`, E NÃO `ESTADO`. A primeira versão
        # desta sonda adivinhou o nome, leu `None`, e acusou de ausente um
        # campo que estava lá — pelo nome do dono, não pelo que eu imaginei.
        #
        #     UMA SONDA QUE ADIVINHA O VOCABULÁRIO DE OUTRO DONO
        #     MEDE O QUE ELA IMAGINOU QUE ELE DIRIA.
        diz(raw.get('PRESERVATION') == 'NOT_PRESERVED',
            'e diz-se NÃO PRESERVADO, porque o disco do runner morre',
            raw.get('PRESERVATION'))
        diz(bool(raw.get('PRESERVATION_OWNER')),
            'nomeando quem ainda tem de receber o byte',
            raw.get('PRESERVATION_OWNER'))

        print('\n7 · O RETORNO É DECLARADO (COL-LAW-505) E ATRAVESSA A PORTA')
        mal = rc.conferir(env, base)
        diz(not mal, 'o envelope respeita o contrato', mal[:1] or 'sem reparos')
        especies = {x.get('ESPECIE') for x in (env.get('SUPORTE') or [])}
        diz(rc.RUN_RECEIPT in especies,
            'o trace viaja como RUN_RECEIPT, não como observação', especies)
        diz(u.get('SOURCE_ID') == FONTE, 'a fonte veio do PEDIDO',
            u.get('SOURCE_ID'))
        diz(u.get('DOCUMENT_ID') == rc.NAO_SEI,
            'e o DOCUMENT_ID não foi fabricado', u.get('DOCUMENT_ID'))
        diz(HANDLE not in str(u.get('SOURCE_ID')),
            'o handle NÃO virou SOURCE_ID', u.get('SOURCE_ID'))
        ing = recibo.get('INGRESSO') or {}
        diz(bool(ing), 'o ingresso correu', ', '.join(list(ing)[:4]) or 'não correu')
        diz((ing.get('PRESERVADOS') or 0) > 0, 'e preservou a observação',
            {k: v for k, v in ing.items() if isinstance(v, int)})

        print('\n8 · ZERO DINHEIRO, ZERO FORNECEDOR')
        trace = [s for s in (env.get('SUPORTE') or [])
                 if s.get('ESPECIE') == rc.RUN_RECEIPT]
        resumo = (trace[0].get('RESUMO') if trace else {}) or {}
        diz(str(resumo.get('COST_STATE') or 'FREE_ROUTE') != 'PAID',
            'a rota do canário não é paga', resumo.get('COST_STATE'))
        diz(not any('apify' in u.lower() for u in idas),
            'nenhuma ida à Apify', 0)

        print('\n9 · O QUE FALTA PARA O CANÁRIO SER REAL — MEDIDO, NÃO OPINADO')
        # Os TRÊS eixos de gasto da COL-LAW-018, cada um medido contra o livro
        # vazio. Só os que abrem uma forma de gasto é que barram — e é isso que
        # separa «a máquina não anda» de «a máquina anda de graça e pontual».
        so_atlas = rl.portao(FONTE, PROPOSITO, livro,
                             custo=rl.CUSTO_DECLARADO_GRATUITO,
                             acionamento='PONTUAL', escopo='PONTUAL')
        agendado = rl.portao(FONTE, PROPOSITO, livro,
                             custo=rl.CUSTO_DECLARADO_GRATUITO,
                             acionamento='AGENDADO', escopo='PONTUAL')
        pago = rl.portao(FONTE, PROPOSITO, livro, custo='pago',
                         acionamento='PONTUAL', escopo='PONTUAL')
        total = rl.portao(FONTE, PROPOSITO, livro,
                          custo=rl.CUSTO_DECLARADO_GRATUITO,
                          acionamento='PONTUAL', escopo='TOTAL')
        diz(so_atlas['BLOQUEIA_A_CORRIDA'] is False,
            'grátis + pontual: o livro vazio NÃO barra', 'corre')
        diz(agendado['BLOQUEIA_A_CORRIDA'] is True,
            'grátis + AGENDADO: barra — recorrência é forma de gasto',
            agendado['FORMAS_DE_GASTO_ABERTAS'])
        diz(pago['BLOQUEIA_A_CORRIDA'] is True,
            'PAGO: barra', pago['FORMAS_DE_GASTO_ABERTAS'])
        diz(total['BLOQUEIA_A_CORRIDA'] is True,
            'volume TOTAL: barra', total['FORMAS_DE_GASTO_ABERTAS'])
        # E o eixo que NÃO é relevância: o atlas não tem conta em plataforma
        # aberta, logo não há par (SOURCE_ID, handle) que alguém tenha
        # declarado. O canário desta prova usa um SOURCE_ID real com um handle
        # inventado — e é POR ISSO que ele não é o canário ao vivo.
        diz(HANDLE.endswith('.invalido'),
            'o alvo desta prova é reservado por norma, e não uma conta real',
            HANDLE)

        ficha = {
            'CANARY_SOURCE_ID': FONTE,
            'CANARY_PURPOSE': PROPOSITO,
            'CANARY_CAPABILITY': CAPACIDADE,
            'CANARY_TARGET': HANDLE,
            'RUN_ID': recibo.get('RUN_ID'),
            'RAW_OBSERVATION_ID': obs.get('NATIVE_ID'),
            'STORAGE_OBJECT': raw.get('PATH'),
            'STORAGE_STATE': raw.get('PRESERVATION'),
            'STORAGE_OWNER': raw.get('PRESERVATION_OWNER'),
            'RETURN_SPECIES': sorted({x.get('ESPECIE') for x in
                                      (env.get('COLHEITA') or [])}
                                     | especies),
            'INGRESS_RESULT': {k: v for k, v in ing.items()
                               if isinstance(v, int)},
            'REAL_CANARY': 'NOT_RUN',
            'FREE_PONTUAL_BLOCKED_BY_RELEVANCE': so_atlas['BLOQUEIA_A_CORRIDA'],
            'SCHEDULED_BLOCKED_BY_RELEVANCE': agendado['BLOQUEIA_A_CORRIDA'],
            'PAID_BLOCKED_BY_RELEVANCE': pago['BLOQUEIA_A_CORRIDA'],
            'TOTAL_SCOPE_BLOCKED_BY_RELEVANCE': total['BLOQUEIA_A_CORRIDA'],
            'WHY': ('nenhuma ficha do atlas e uma conta Bluesky e nenhuma fonte '
                    'tem decisao de relevancia: a arvore esta provada, a '
                    'operacao ao vivo nao.'),
            'MODE': 'OFFLINE_FAKE_SOCKET',
        }
        diz(bool(ficha['RAW_OBSERVATION_ID']),
            'o RAW_OBSERVATION_ID é o id nativo, e não o SHA nem o RUN_ID',
            ficha['RAW_OBSERVATION_ID'])
        diz(ficha['RAW_OBSERVATION_ID'] != ficha['RUN_ID'],
            'RUN_ID != RAW_OBSERVATION_ID', 'distintos')

        print('\n' + '=' * 74)
        print('FICHA DO CANÁRIO (§9)')
        for k, v in ficha.items():
            print('  %-22s %s' % (k, v))
        print('=' * 74)
        print('REAL_NETWORK = 0 · APIFY_RUNS = 0 · PROVIDER_RUNS = 0 · COST_USD = 0')
        print('FALHAS = %d' % len(FALHAS))
        for f in FALHAS:
            print('  · %s' % f)
        return 0 if not FALHAS else 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == '__main__':
    sys.exit(main())
