#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O CENSO DAS PORTAS DE GASTO — quem consegue COMPRAR, e por onde.

    py provas/censo_das_portas_de_gasto.py
    py provas/censo_das_portas_de_gasto.py --escrever

    TOCAR NA APIFY NAO E COMPRAR NA APIFY.

A SR-01 mediu «32 entrypoints que tocam Apify» e usou esse numero para baixar o
seu proprio veredito a PARTIAL. O numero estava certo para a pergunta que ele
fazia — quantos ficheiros mencionam a plataforma e vao a rede — e essa NAO e a
pergunta do dinheiro.

    GET /v2/acts/{ator}          le o contrato do ator. Sem credencial. Zero dolares.
    GET /v2/actor-runs/{id}      le o estado de uma execucao que ja existe.
    GET /v2/datasets/{id}/items  le o que ja foi colhido e ja foi pago.
    POST /v2/acts/{ator}/runs    ACENDE UMA EXECUCAO. E so isto custa.

Este censo separa as duas coisas, ficheiro a ficheiro, seguindo o grafo de
importacoes REAL — nao a mencao textual.

    A PERGUNTA NAO E «QUEM FALA COM A APIFY?».
    E «QUEM CONSEGUE CRIAR UMA EXECUCAO PAGA?».

⚠️ E ELE NAO PROCURA SO `apify`. Um POST pago pode nascer de `curl`, de
`urllib`, de `requests`, de um wrapper de fornecedor ou de um subprocesso. O
censo varre as primitivas, e depois pergunta quais delas apontam a um endpoint
que cria execucao.
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(_HERE)
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401

SAIDA = os.path.join('data', 'derivados', 'CENSO-PORTAS-DE-GASTO-V1.json')

# As gavetas onde vive codigo que pode ir a rede.
GAVETAS = ('coleta', 'ferramentas', 'fontes', 'guarda', 'leis', 'medidas',
           'motor', 'orquestrador', 'pacote', 'pedido', 'portoes', 'provas',
           'regras', 'superficie', 'admissao', 'candidatas')

# ── AS PRIMITIVAS DE REDE, e nenhuma delas e «apify» ────────────────────────
# Procurar a palavra «apify» encontraria o ficheiro que a REDIGE dos logs e
# perderia um POST feito por `requests` a um fornecedor novo.
PRIMITIVAS_DE_REDE = {
    'curl': re.compile(r"""['"]curl['"]|\bcurl\s+-"""),
    'urllib': re.compile(r'urllib\.request|urlopen\('),
    'requests': re.compile(r'\brequests\.(get|post|put|request)\('),
    'httpx': re.compile(r'\bhttpx\.'),
    'fetch': re.compile(r'\bfetch\('),
    'subprocess_rede': re.compile(r'subprocess\.(run|Popen|check_output)'),
}

# ── O QUE CRIA EXECUCAO, e o que so le ──────────────────────────────────────
# O endpoint de criacao e um so, e o metodo importa: `GET /acts/{x}` le o
# contrato do ator e nao custa nada; `POST /acts/{x}/runs` acende a execucao.
CRIA_EXECUCAO = re.compile(
    r"""/acts/[^'"\s]*/runs|run-sync|/actor-tasks/[^'"\s]*/runs""")
METODO_POST = re.compile(r"""metodo\s*=\s*['"]POST['"]|method\s*=\s*['"]POST['"]"""
                         r"""|-X['"]?\s*,?\s*['"]?POST|\.post\(""")

# O fornecedor pago que esta casa usa hoje. A lista e aberta de proposito: se
# amanha entrar outro, ele aparece aqui e o censo nao finge que nao viu.
FORNECEDORES_PAGOS = {
    'api.apify.com': 'APIFY',
}


def _ficheiros():
    fs = []
    for g in GAVETAS:
        d = os.path.join(RAIZ, g)
        if not os.path.isdir(d):
            continue
        for base, _, nomes in os.walk(d):
            if any(p in base for p in ('/__pycache__', '/node_modules')):
                continue
            for n in sorted(nomes):
                if n.endswith(('.py', '.mjs', '.js', '.sh')):
                    fs.append(os.path.relpath(os.path.join(base, n), RAIZ))
    return sorted(fs)


def _ler(rel):
    try:
        with open(os.path.join(RAIZ, rel), encoding='utf-8', errors='replace') as f:
            return f.read()
    except OSError:
        return ''


def _importa(texto, rel):
    """Os modulos curtos que este ficheiro importa. `_gavetas` achata o caminho."""
    nomes = set()
    if rel.endswith('.py'):
        try:
            arvore = ast.parse(texto)
        except SyntaxError:
            return nomes
        for n in ast.walk(arvore):
            if isinstance(n, ast.Import):
                for a in n.names:
                    nomes.add(a.name.split('.')[0])
            elif isinstance(n, ast.ImportFrom) and n.module:
                nomes.add(n.module.split('.')[0])
    else:
        for m in re.finditer(r"""from\s+['"]([^'"]+)['"]""", texto):
            nomes.add(os.path.basename(m.group(1)).split('.')[0])
    return nomes


def medir(raiz=RAIZ) -> dict:
    fs = _ficheiros()
    info = {}
    for rel in fs:
        t = _ler(rel)
        mod = os.path.splitext(os.path.basename(rel))[0]
        prims = sorted(k for k, rx in PRIMITIVAS_DE_REDE.items() if rx.search(t))
        cria = bool(CRIA_EXECUCAO.search(t)) and bool(METODO_POST.search(t))
        fornecedor = next((v for k, v in FORNECEDORES_PAGOS.items() if k in t), None)
        info[rel] = {
            'MODULO': mod,
            'TEXTO_LEN': len(t),
            'IMPORTA': _importa(t, rel),
            'PRIMITIVAS_DE_REDE': prims,
            'CRIA_EXECUCAO_DIRECTAMENTE': cria,
            'FORNECEDOR_PAGO_CITADO': fornecedor,
            'TEM_MAIN': '__main__' in t or 'process.argv' in t,
            'MENCIONA_APIFY': 'apify' in t.lower(),
        }

    # ── QUEM CRIA EXECUCAO PAGA, DIRECTAMENTE ───────────────────────────────
    primitivas = sorted(r for r, d in info.items() if d['CRIA_EXECUCAO_DIRECTAMENTE'])
    mod_primitiva = {info[r]['MODULO'] for r in primitivas}

    # ── E QUEM CHEGA LA POR IMPORTACAO (fecho transitivo) ───────────────────
    por_modulo = {}
    for rel, d in info.items():
        por_modulo.setdefault(d['MODULO'], []).append(rel)

    alcanca = set(mod_primitiva)
    mudou = True
    while mudou:
        mudou = False
        for rel, d in info.items():
            if d['MODULO'] in alcanca:
                continue
            if d['IMPORTA'] & alcanca:
                alcanca.add(d['MODULO'])
                mudou = True

    linhas = []
    for rel in fs:
        d = info[rel]
        directo = d['CRIA_EXECUCAO_DIRECTAMENTE']
        via = bool(d['IMPORTA'] & alcanca) and not directo
        linhas.append({
            'ENTRYPOINT': rel,
            'TEM_MAIN': d['TEM_MAIN'],
            'PRIMITIVAS_DE_REDE': d['PRIMITIVAS_DE_REDE'],
            'MENCIONA_APIFY': d['MENCIONA_APIFY'],
            'FORNECEDOR': d['FORNECEDOR_PAGO_CITADO'],
            'CRIA_EXECUCAO_DIRECTAMENTE': directo,
            'ALCANCA_CRIACAO_POR_IMPORT': via,
            'PODE_CRIAR_EXECUCAO_PAGA': directo or via,
            'CALLS_COLETOR': 'coletor' in d['IMPORTA'],
            'CALLS_APIFY_POOL': 'apify_pool' in d['IMPORTA'],
            'CALLS_ORQUESTRADOR': 'orquestrador' in d['IMPORTA'],
        })

    # ── OS WORKFLOWS, E O QUE CADA UM ALCANCA ───────────────────────────────
    # ⚠️ NAO SE LE O NOME DO WORKFLOW. Le-se o que ele CORRE, e cruza-se com
    # quem consegue criar execucao paga. Um workflow chamado «apify-alguma-coisa»
    # pode nao comprar nada, e um sem «apify» no nome pode comprar tudo.
    import re as _re
    alcanca_gasto = {l['ENTRYPOINT'] for l in linhas if l['PODE_CRIAR_EXECUCAO_PAGA']}
    workflows = []
    d_wf = os.path.join(raiz, '.github', 'workflows')
    for nome in sorted(os.listdir(d_wf)) if os.path.isdir(d_wf) else []:
        if not nome.endswith(('.yml', '.yaml')):
            continue
        with open(os.path.join(d_wf, nome), encoding='utf-8', errors='replace') as f:
            texto = f.read()
        corre = sorted(set(_re.findall(
            r'([A-Za-z0-9_]+(?:/[A-Za-z0-9_.-]+)+\.(?:py|mjs|js))', texto)))
        pagos = [c for c in corre if c in alcanca_gasto]
        workflows.append({
            'WORKFLOW': '.github/workflows/' + nome,
            'CORRE': corre,
            'CHAMA_ORQUESTRADOR': 'orquestrador/orquestrador.py' in texto,
            'CHAMA_SCRIPT_DIRECTAMENTE': bool([c for c in corre
                                               if not c.startswith('orquestrador/')]),
            'ALCANCA_CRIACAO_PAGA': pagos,
            'PODE_CRIAR_EXECUCAO_PAGA': bool(pagos),
        })
    wf_pagos = [w for w in workflows if w['PODE_CRIAR_EXECUCAO_PAGA']]

    podem = [l for l in linhas if l['PODE_CRIAR_EXECUCAO_PAGA']]
    mencionam = [l for l in linhas if l['MENCIONA_APIFY']]
    com_rede = [l for l in linhas if l['PRIMITIVAS_DE_REDE']]
    entry_podem = [l for l in podem if l['TEM_MAIN']]

    return {
        'SCHEMA': 'sintonia.censo-portas-de-gasto/1',
        'PERGUNTA': 'quem consegue CRIAR uma execucao paga, e nao quem fala com a plataforma',
        'TOTAIS': {
            'FICHEIROS_VARRIDOS': len(fs),
            'COM_PRIMITIVA_DE_REDE': len(com_rede),
            'MENCIONAM_APIFY': len(mencionam),
            'PAID_CREATION_PRIMITIVES': len(primitivas),
            'PODEM_CRIAR_EXECUCAO_PAGA': len(podem),
            'DESTES, COM __main__': len(entry_podem),
            'WORKFLOWS_TOTAIS': len(workflows),
            'WORKFLOWS_QUE_PODEM_COMPRAR': len(wf_pagos),
        },
        'WORKFLOWS_QUE_PODEM_COMPRAR': [
            {'WORKFLOW': w['WORKFLOW'],
             'CHAMA_ORQUESTRADOR': w['CHAMA_ORQUESTRADOR'],
             'CHAMA_SCRIPT_DIRECTAMENTE': w['CHAMA_SCRIPT_DIRECTAMENTE'],
             'ALCANCA': w['ALCANCA_CRIACAO_PAGA']} for w in wf_pagos],
        'WORKFLOWS': workflows,
        'PAID_CREATION_PRIMITIVES': primitivas,
        'PODEM_CRIAR_EXECUCAO_PAGA': [l['ENTRYPOINT'] for l in podem],
        'ENTRYPOINTS_QUE_PODEM_CRIAR': [l['ENTRYPOINT'] for l in entry_podem],
        'MENCIONAM_APIFY_MAS_NAO_COMPRAM': [
            l['ENTRYPOINT'] for l in mencionam if not l['PODE_CRIAR_EXECUCAO_PAGA']],
        'FICHEIROS': linhas,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--escrever', action='store_true')
    a = ap.parse_args()
    c = medir()

    print('CENSO DAS PORTAS DE GASTO')
    print('=' * 70)
    for k, v in c['TOTAIS'].items():
        print('  %-30s %s' % (k, v))
    print()
    print('  PRIMITIVAS QUE CRIAM EXECUCAO PAGA:')
    for p in c['PAID_CREATION_PRIMITIVES']:
        print('      %s' % p)
    print()
    print('  PODEM CRIAR EXECUCAO PAGA (directo ou por import):')
    for p in c['PODEM_CRIAR_EXECUCAO_PAGA']:
        print('      %s' % p)
    print()
    print('  MENCIONAM APIFY E NAO COMPRAM: %d'
          % len(c['MENCIONAM_APIFY_MAS_NAO_COMPRAM']))
    print()
    print('  WORKFLOWS QUE ALCANCAM CRIACAO PAGA:')
    for w in c['WORKFLOWS_QUE_POD' 'EM_COMPRAR']:
        print('      %-44s orquestrador=%s' % (w['WORKFLOW'], w['CHAMA_ORQUESTRADOR']))
        print('          alcanca: %s' % ', '.join(w['ALCANCA']))
    if a.escrever:
        caminho = os.path.join(RAIZ, SAIDA)
        os.makedirs(os.path.dirname(caminho), exist_ok=True)
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(json.dumps(c, ensure_ascii=False, indent=2, default=list) + '\n')
        print('\n  escrito: %s' % SAIDA)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
