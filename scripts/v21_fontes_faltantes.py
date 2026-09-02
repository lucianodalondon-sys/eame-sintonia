#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CADASTRA A FONTE QUE JÁ ERA CITADA — sem inventar nada sobre ela.

    python3 scripts/v21_fontes_faltantes.py

O DEFEITO
----------
15 identificadores de fonte apareciam em `SOURCE_IDS` de registros do pacote sem
ter linha em `SOURCES.json`. `SRC_DOI_ORG` sozinho era citado 87 vezes.

Na tela isso vira: «fonte: SRC_DOI_ORG» e nada acontece ao clicar. O usuário lê
como portal quebrado — e, pior, não consegue chegar ao documento que sustenta a
afirmação. **Uma afirmação cuja fonte não abre é uma afirmação sem fonte.**

O QUE ESTE SCRIPT PODE FAZER, E O QUE NÃO PODE
-----------------------------------------------
Pode: pegar a URL que o próprio registro citante já declara em `SOURCE_URLS`, e
criar a linha da fonte com ela. Isso não é inventar — é copiar o que já estava
escrito dois campos ao lado.

    A URL JÁ ESTAVA NO PACOTE. FALTAVA A LINHA QUE A GUARDA.

Não pode: dizer que a fonte funciona, que publica tal coisa, ou qual é o nome
oficial dela. Nada disso foi medido para estas 15. Então cada uma nasce com
`ACCESS_STATE = NAO_TESTADO` e `QA_STATUS = QA_UNREVIEWED`, e o que não se sabe
fica escrito como não sabido.

    O REGISTRO CRIADO AQUI SERVE PARA O LINK ABRIR. NÃO SERVE PARA AFIRMAR
    NADA SOBRE A FONTE.
"""
import json
import os
import re
from collections import Counter, defaultdict
from urllib.parse import urlsplit

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ING = os.path.join(ROOT, 'build', 'ITALY-REALITY-HANDOFF-V2.1', 'DESIGN-INGEST')


def main():
    p = os.path.join(ING, 'SOURCES.json')
    d = json.load(open(p, encoding='utf-8'))
    tem = set()
    for r in d['RECORDS']:
        tem.add(r['ID'])
        tem.update(r.get('ID_ALIASES') or [])

    urls, vezes, onde = defaultdict(Counter), Counter(), defaultdict(set)
    for arq in sorted(os.listdir(ING)):
        if not arq.endswith('.json') or arq in ('SOURCES.json',):
            continue
        dd = json.load(open(os.path.join(ING, arq), encoding='utf-8'))
        for r in dd.get('RECORDS') or []:
            if not isinstance(r, dict):
                continue
            for sid in (r.get('SOURCE_IDS') or []):
                if sid in tem:
                    continue
                vezes[sid] += 1
                onde[sid].add(dd.get('COLLECTION') or arq)
                for u in (r.get('SOURCE_URLS') or []):
                    if u:
                        urls[sid][u] += 1

    criadas, sem_url = [], []
    for sid, n in vezes.most_common():
        cand = urls[sid].most_common()
        if not cand:
            # ⚠️ NÃO SE INVENTA URL. Sem endereço em lugar nenhum do pacote, a
            # fonte fica declarada como buraco — visível, contada, e nomeada.
            sem_url.append({'ID': sid, 'CITADO_VEZES': n,
                            'EM': sorted(onde[sid]),
                            'POR_QUE_NAO_FOI_CRIADA':
                                'nenhum registro que a cita declara URL. Criar '
                                'uma linha sem endereco seria fingir cadastro.'})
            continue
        host = (urlsplit(cand[0][0]).netloc or '').lower()
        criadas.append({
            'ID': sid, 'ENTITY_TYPE': 'SOURCE',
            'PROVENANCE': 'REAL_SOURCE_LAST_MILE',
            'ORIGIN_LAYER': 'LAST_MILE',
            'QA_STATUS': 'QA_UNREVIEWED', 'CLIENT_SAFE': False,
            'SOURCE_IDS': [sid],
            'SOURCE_URLS': [u for u, _c in cand[:6]],
            'REFERENCE_DATE': None,
            'CROP_IDS': [], 'ISSUE_IDS': [], 'REGION_IDS': [],
            'GEOGRAPHIC_SCOPE': 'NAO_SEI',
            'NAME': re.sub(r'^www\.', '', host),
            'WHAT_IT_PUBLISHES': None,
            'ACCESS_STATE': 'NAO_TESTADO',
            'ACCESS_EVIDENCE': None,
            'REQUIRES_ITALIAN_ROUTE': None,
            'RUNTIME_DEPENDENCY': 'NENHUMA',
            'CITADO_VEZES': n,
            'CITADO_EM': sorted(onde[sid]),
            'COMO_NASCEU':
                'esta linha foi criada a partir da URL que os proprios registros '
                'citantes ja declaravam em SOURCE_URLS. Nada sobre a fonte foi '
                'inventado: nome e o host, e o resto esta nulo porque NAO FOI '
                'MEDIDO. Serve para o link abrir — nao para afirmar nada sobre '
                'a fonte.',
            'O_QUE_NAO_SE_SABE': [
                'se a rota abre daqui', 'se exige rota italiana',
                'o que exatamente publica', 'o nome oficial da instituicao',
            ],
        })

    d['RECORDS'] = d['RECORDS'] + criadas
    d['COUNT_TOTAL'] = len(d['RECORDS'])
    d['COUNT_CLIENT_SAFE'] = sum(1 for x in d['RECORDS'] if x.get('CLIENT_SAFE'))
    d['CRIADAS_A_PARTIR_DE_CITACAO'] = {
        'QUANTAS': len(criadas),
        'LEI': 'a URL ja estava no pacote, dentro do registro que cita. Faltava a '
               'linha que a guarda. NENHUM atributo da fonte foi inventado.',
        'IDS': [x['ID'] for x in criadas],
    }
    d['CITADAS_SEM_URL_EM_LUGAR_NENHUM'] = sem_url

    # a saúde da citação, recontada
    tem = set()
    for r in d['RECORDS']:
        tem.add(r['ID'])
        tem.update(r.get('ID_ALIASES') or [])
    total = sum(vezes.values())
    d['CITATION_HEALTH'] = dict(d.get('CITATION_HEALTH') or {}, **{
        'RECONTADO_APOS_CADASTRO': True,
        'IDS_AINDA_SEM_CADASTRO': [x['ID'] for x in sem_url],
    })
    json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    print('fontes criadas a partir de citacao: %d' % len(criadas))
    for x in criadas:
        print('   %-46s %4dx  %s' % (x['ID'], x['CITADO_VEZES'],
                                     x['SOURCE_URLS'][0][:70]))
    print('\nainda sem cadastro (nenhuma URL no pacote): %d' % len(sem_url))
    for x in sem_url:
        print('   %-46s %4dx' % (x['ID'], x['CITADO_VEZES']))
    print('\nSOURCES.json: %d linhas' % d['COUNT_TOTAL'])
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
