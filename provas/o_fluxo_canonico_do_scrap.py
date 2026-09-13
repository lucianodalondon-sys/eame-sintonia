#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCRAP-FLOW-01 — UM FLUXO OPERACIONAL REAL ATRAVESSA O ORQUESTRADOR CANÔNICO.

    py provas/o_fluxo_canonico_do_scrap.py

A SR-02 fechou o dinheiro e deixou escrita a diferença que faltava:

    MODULE CAN'T SPEND != FLOW IS CANONICAL.

Nenhum módulo consegue comprar sem autorização. Isso não diz nada sobre o
caminho: o disparador ia direto a `coleta/social_scrap.py`, corria `COLLECT`, e
o que colhia parava ali. `coleta/ingresso.py` existia, a admissão existia, e
entre o SCRAP e as duas não havia aresta nenhuma.

    MODULE EXISTS != EDGE EXISTS != FLOW EXISTS.

O QUE É FALSO AQUI, E SÓ ISSO
-------------------------------
UM ficheiro: `coleta/instagram_janela.py` — o cliente que abre o NAVEGADOR
contra o mundo externo. Nada acima dele. São reais o orquestrador, o plano, o
executor do SCRAP, o roteador, o adaptador, a guarda de gasto, os dois tetos, o
contrato de retorno, o ingresso e a admissão.

    UM FAKE ACIMA DO GATE MEDE O FAKE.

⚠️ E ELE TEM DE SER UM FICHEIRO, E NÃO UM `monkeypatch`. A primeira versão desta
prova substituiu `instagram_janela.perfis` em memória e mediu ZERO idas ao
navegador — porque o orquestrador corre o executor como PROCESSO SEPARADO, e o
processo filho importa o módulo verdadeiro.

    UM FALSO QUE VIVE NA MEMÓRIA DO PAI NÃO EXISTE PARA O FILHO.
    E UM ORQUESTRADOR QUE CORRE MESMO UM SUBPROCESSO É O QUE SE QUERIA PROVAR.

Por isso copia-se a árvore (leve; `data/` e `.git` ficam ligados), troca-se
AQUELE ficheiro, e corre-se lá dentro.

    REAL_NETWORK = 0 · META_REQUESTS = 0 · APIFY_RUNS = 0 · COST_USD = 0
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

import orquestrador as orq          # noqa: E402
import pedido as pd                 # noqa: E402
import receitas as rec              # noqa: E402
import retorno_da_coleta as rc      # noqa: E402
import scrap_colheita as sc         # noqa: E402

FALHAS = []
FONTE = 'IT-T9-001'


def diz(ok, titulo, detalhe=''):
    print('  %-5s %-54s %s' % ('ok' if ok else 'FALHA', titulo[:54],
                               str(detalhe)[:54]))
    if not ok:
        FALHAS.append(titulo)


SHIM = os.path.join(RAIZ, 'provas', '_flow01_janela_falsa.py')
PESADAS = {'.git', 'data', 'node_modules', 'italia-portale', '__pycache__',
           '.tmp', 'build'}


def arvore_com_o_falso(destino):
    """Uma cópia leve da árvore, com UM ficheiro trocado. → a raiz da cópia."""
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
    for nome in ('.git',):
        os.symlink(os.path.join(RAIZ, nome), os.path.join(destino, nome))
    # `data/` é COPIADO e não ligado: o ingresso escreve RAW, e uma prova não
    # escreve no acervo verdadeiro.
    shutil.copytree(os.path.join(RAIZ, 'data'), os.path.join(destino, 'data'),
                    symlinks=True)
    shutil.copy2(SHIM, os.path.join(destino, 'coleta', 'instagram_janela.py'))
    return destino


DRIVER = """
import json, os, sys
RAIZ = os.path.dirname(os.path.abspath(__file__))
for p in ('orquestrador','pedido','coleta','leis','regras','ferramentas',
          'medidas','guarda',''):
    sys.path.insert(0, os.path.join(RAIZ, p) if p else RAIZ)
import orquestrador as orq, pedido as pd
fonte = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] != '-' else None
p = pd.de_uma_frase('colete concorrentes')
p.filtros.update({'fase': 'janela-perfis', 'pais': 'IT'})
if fonte:
    p.filtros['fonte'] = fonte
recibo = orq.correr(p)
recibo.pop('_plano', None)
print('<<<RECIBO>>>' + json.dumps(recibo, ensure_ascii=False, default=str))
"""


def correr_fluxo(arvore, fonte):
    """Corre o caminho inteiro DENTRO da cópia. → (recibo, envelope, idas)."""
    driver = os.path.join(arvore, '_flow01_driver.py')
    with open(driver, 'w', encoding='utf-8') as f:
        f.write(DRIVER)
    marca = os.path.join(arvore, 'IDAS-AO-MUNDO.json')
    if os.path.isfile(marca):
        os.remove(marca)
    amb = dict(os.environ, FLOW01_MARCA=arvore, PYTHONIOENCODING='utf-8')
    r = subprocess.run([sys.executable, driver, fonte or '-'], cwd=arvore,
                       capture_output=True, text=True, env=amb, timeout=600)
    recibo = {}
    for linha in (r.stdout or '').splitlines():
        if linha.startswith('<<<RECIBO>>>'):
            recibo = json.loads(linha[len('<<<RECIBO>>>'):])
    if not recibo:
        print((r.stdout or '')[-1200:])
        print((r.stderr or '')[-1200:])
    env = {}
    alvo = os.path.join(arvore, sc.ENVELOPE)
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
    base = tempfile.mkdtemp(prefix='flow01-')
    arvore = os.path.join(base, 'arvore')
    os.makedirs(arvore)
    try:
        arvore_com_o_falso(arvore)

        print('\n1 · O PEDIDO CHEGA AO EXECUTOR DO SCRAP, E NÃO AO SCRIPT')
        p = pd.de_uma_frase('colete concorrentes')
        p.filtros.update({'fase': 'janela-perfis', 'fonte': FONTE})
        e = rec.resolver(p).executores[0]
        diz(e['id'] == 'scrap-colheita', 'o plano escolhe o executor do SCRAP',
            e['id'])
        diz(e['roda'] == ['coleta/scrap_colheita.py'],
            'e ele corre o adapter, não `social_scrap.py`', e['roda'][0])
        diz(e.get('recebe_run_id') is True,
            'o adapter recebe a corrida — não a cunha', 'recebe_run_id=True')

        print('\n2 · O CAMINHO INTEIRO, COM O CLIENTE DO NAVEGADOR FALSO')
        recibo, env, idas = correr_fluxo(arvore, FONTE)
        diz(recibo.get('STATUS') == 'SUCCESS', 'a corrida correu',
            recibo.get('STATUS'))
        diz(bool(recibo.get('RUN_ID')), 'o orquestrador cunhou o RUN_ID',
            recibo.get('RUN_ID'))
        diz(env.get('RUN_ID') == recibo.get('RUN_ID'),
            'e o adapter usou ESSE, e não outro', env.get('RUN_ID'))
        diz(len(idas) >= 1, 'o cliente do navegador foi mesmo chamado', idas)
        diz(recibo.get('ACTOR') == 'coleta/scrap_colheita.py',
            'o recibo nomeia o executor do SCRAP', recibo.get('ACTOR'))

        print('\n3 · O RETORNO É DECLARADO, NÃO ADIVINHADO (COL-LAW-505)')
        diz(isinstance(env.get('COLHEITA'), list)
            and isinstance(env.get('SUPORTE'), list),
            'o envelope separa COLHEITA de SUPORTE',
            'colheita=%d suporte=%d' % (len(env.get('COLHEITA') or []),
                                        len(env.get('SUPORTE') or [])))
        mal = rc.conferir(env, arvore)
        diz(not mal, 'e ele respeita o contrato', mal[:1] or 'sem reparos')
        especies = {u.get('ESPECIE') for u in (env.get('SUPORTE') or [])}
        diz(rc.RUN_RECEIPT in especies,
            'o trace viaja como RUN_RECEIPT, e não como observação', especies)

        print('\n4 · A COLHEITA ATRAVESSA O INGRESSO')
        diz(len(env.get('COLHEITA') or []) > 0, 'houve colheita declarada',
            len(env.get('COLHEITA') or []))
        diz(recibo.get('COLHEITA_ENCONTRADA') == len(env.get('COLHEITA') or []),
            'o orquestrador recebeu o que o executor declarou',
            recibo.get('COLHEITA_ENCONTRADA'))
        u = (env.get('COLHEITA') or [{}])[0]
        diz(u.get('SOURCE_ID') == FONTE, 'a fonte veio do PEDIDO', u.get('SOURCE_ID'))
        diz(u.get('DOCUMENT_ID') == rc.NAO_SEI,
            'e o DOCUMENT_ID não foi fabricado', u.get('DOCUMENT_ID'))
        ing = recibo.get('INGRESSO') or {}
        diz(bool(ing), 'o ingresso correu', ', '.join(list(ing)[:4]) or 'não correu')
        numeros = {k: v for k, v in ing.items() if isinstance(v, int)}
        diz(any(v > 0 for v in numeros.values()),
            'e preservou a observação', numeros)

        print('\n5 · SEM FONTE PROVADA NÃO HÁ COLHEITA — E ISSO NÃO É ERRO')
        recibo2, env2, _i2 = correr_fluxo(arvore, None)
        diz(len(env2.get('COLHEITA') or []) == 0,
            'zero colheita quando o pedido não nomeia fonte',
            'colheita=%d' % len(env2.get('COLHEITA') or []))
        diz(bool(env2.get('PORQUE_ZERO_COLHEITA')), 'e o porquê fica escrito',
            (env2.get('PORQUE_ZERO_COLHEITA') or '')[:44])
        diz(len(env2.get('SUPORTE') or []) > 0,
            'o que se observou sai como SUPORTE, que não atravessa',
            len(env2.get('SUPORTE') or []))
        diz(not recibo2.get('COLHEITA_ENCONTRADA'),
            'e o ingresso não recebeu nada', recibo2.get('COLHEITA_ENCONTRADA'))

        print('\n' + '=' * 74)
        print('REAL_NETWORK = 0 · META_REQUESTS = 0 · APIFY_RUNS = 0 · COST_USD = 0')
        print('FALHAS = %d' % len(FALHAS))
        for f in FALHAS:
            print('  · %s' % f)
        return 0 if not FALHAS else 1
    finally:
        shutil.rmtree(base, ignore_errors=True)


if __name__ == '__main__':
    sys.exit(main())
