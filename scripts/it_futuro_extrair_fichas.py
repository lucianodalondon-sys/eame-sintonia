#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AS FICHAS, GRAVADAS INTEIRAS — para o refutador as poder ler todas.

    python3 scripts/it_futuro_extrair_fichas.py

POR QUE ESTE FICHEIRO PRECISOU DE EXISTIR
------------------------------------------
Na primeira montagem eu passava a ficha ao refutador DENTRO DO PROMPT, cortada
em 12.000 caracteres. Medi depois: as 53 fichas escritas tem mediana de 27.000
caracteres e NENHUMA cabe. Como a ordem das chaves segue o esquema, o corte caia
sempre no mesmo sitio — o refutador via o TITULO, o FACTO e a CONFIANCA, e nunca
via a janela, o portfolio, o mapa de accao, o horizonte nem a autoavaliacao.

Dos sete testes que eu lhe dava, so o primeiro — a citacao existe literalmente? —
corria sobre dados que ele tinha. Os outros corriam sobre campos ausentes, e o
esquema obrigava-o a responder na mesma: saiu JANELA_INVENTADA=NAO e
PORTFOLIO_ERRADO=NAO sobre campos que nunca lhe chegaram.

    UM REFUTADOR QUE CERTIFICA O QUE NAO LEU E PIOR DO QUE NENHUM:
    ELE ASSINA POR BAIXO DA COISA QUE DEVIA APANHAR.

A correccao nao e um prompt maior. E parar de entregar evidencia por prompt: a
ficha passa a viver num ficheiro e o refutador le a dele, inteira, como ja fazia
com o registo julgado.
"""
import json
import os
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.expanduser(
    '~/.claude/projects/-home-user-eame-sintonia/'
    'f0de5886-eea0-5643-b2e1-e51287bd65f1/subagents/workflows')
JULGADOS = 'data/samples/IT-FUTURO-V1/IT-FUTURO-JULGADOS-V1.json'
SAIDA = 'data/samples/IT-FUTURO-V1/IT-FUTURO-FICHAS-V1.json'
RUNS = ['wf_e5e03bcc-487', 'wf_3d483e10-13c', 'wf_e4c83732-977', 'wf_4a1ab40f-f02']


def main(runs=None):
    runs = runs or RUNS
    fichas, duplicadas = {}, Counter()
    for run in runs:
        p = os.path.join(BASE, run, 'journal.jsonl')
        if not os.path.exists(p):
            continue
        for linha in open(p):
            try:
                r = json.loads(linha)
            except Exception:
                continue
            if r.get('type') != 'result':
                continue
            x = r['result']
            if not isinstance(x, dict) or 'CAND_ID' not in x or 'VEREDITO' in x:
                continue
            cid = x['CAND_ID']
            if cid in fichas:
                duplicadas[cid] += 1
                # fica a mais longa: quem escreveu mais, mediu mais
                if len(json.dumps(x)) <= len(json.dumps(fichas[cid])):
                    continue
            x['_RUN'] = run
            fichas[cid] = x

    jul = json.load(open(os.path.join(ROOT, JULGADOS)))
    universo = [r['CAND_ID'] for r in jul['RULED'] if r.get('CAND_ID')]
    tam = {c: len(json.dumps(f, ensure_ascii=False, indent=1)) for c, f in fichas.items()}

    saida = {
        'DATASET': 'IT-FUTURO-FICHAS-V1',
        'LAYER': 'FUTURE INTELLIGENCE — fichas operacionais, antes da refutacao',
        'COUNTRY': 'IT',
        'SOURCE_ID': 'IT-FUTURO-JULGADOS-V1',
        'CAPTURED_AT': '2026-09-04',
        'SOURCE': 'fichas escritas pelos agentes das corridas %s, lidas do journal de cada uma '
                  'e nao do resultado da ferramenta' % ', '.join(runs),
        'PORQUE_ESTE_FICHEIRO_EXISTE': (
            'o refutador recebia a ficha dentro do prompt, cortada em 12.000 caracteres, e '
            'nenhuma das fichas cabe nesse corte (mediana %d). Ele via o facto e a confianca, e '
            'nunca via a janela, o portfolio, o mapa de accao nem o horizonte — mas o esquema '
            'obrigava-o a julgar tudo. A ficha passa a viver aqui, e o refutador le a dele '
            'inteira.' % (sorted(tam.values())[len(tam) // 2] if tam else 0)),
        'UNIVERSO': len(universo),
        'FICHAS': len(fichas),
        'EM_FALTA': sorted(set(universo) - set(fichas)),
        'ESCRITAS_MAIS_DE_UMA_VEZ': dict(duplicadas),
        'REGRA_NA_DUPLICACAO': 'fica a ficha mais longa. Quem escreveu mais, mediu mais.',
        'TAMANHO_MEDIANO': sorted(tam.values())[len(tam) // 2] if tam else 0,
        'TAMANHO_MAXIMO': max(tam.values()) if tam else 0,
        'ROWS': [fichas[c] for c in universo if c in fichas],
    }
    with open(os.path.join(ROOT, SAIDA), 'w') as f:
        json.dump(saida, f, ensure_ascii=False, indent=1)
    print('FICHAS       ', len(fichas), 'de', len(universo))
    print('EM FALTA     ', saida['EM_FALTA'])
    print('DUPLICADAS   ', dict(duplicadas))
    print('MEDIANA      ', saida['TAMANHO_MEDIANO'], 'chars  (o corte do prompt era 12000)')
    print('->', SAIDA)


if __name__ == '__main__':
    main(sys.argv[1:] or None)
