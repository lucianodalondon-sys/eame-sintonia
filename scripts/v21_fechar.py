#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FECHA O V2.1 — registro central, manifesto do app e arquivo interno.

    python3 scripts/v21_fechar.py

§16 · O REGISTRO CENTRAL
-------------------------
`CANONICAL-INTELLIGENCE-MASTER.json` indexa TUDO — o que veio do handoff
anterior e o que veio da last-mile. O V2 falhou aqui: o mestre dele tinha só os
319 da last-mile, e o Design teria de descobrir sozinho que o resto morava
noutra pasta.

    O DESIGN NÃO PODE PRECISAR ESCOLHER ENTRE ARQUIVO VELHO E ARQUIVO NOVO.

§17 · O MANIFESTO
------------------
`APP-MANIFEST.json` diz, sem ambiguidade, qual arquivo carregar para cada
coleção e qual arquivo antigo ele SUBSTITUI. Se o Design carregar os dois, ele
conta o mesmo fato duas vezes.

§15 · O QUE NÃO PODE ESTAR NO INGEST
-------------------------------------
Histórias de demo, planos «fake-to-real», auditorias, relatórios de pesquisa e
quarentena vão para `INTERNAL-ARCHIVE/`. Não é lixo: é o rastro do trabalho. Mas

    O PACOTE DE DESIGN É UM CONTRATO DE DADO, NÃO UM ARQUIVO DE PAPÉIS DE
    TRABALHO.
"""
import glob
import json
import os
import shutil
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V21 = os.path.join(ROOT, 'build', 'ITALY-REALITY-HANDOFF-V2.1')
ING = os.path.join(V21, 'DESIGN-INGEST')
ARQ = os.path.join(V21, 'INTERNAL-ARCHIVE')
V2 = os.path.join(ROOT, 'build', 'ITALY-REALITY-HANDOFF-V2')

# o que o Design carrega, e o que cada arquivo aposenta
CONTRATO = [
    ('products.regulatory', 'PRODUCTS-REGULATORY.json'),
    ('products.commercial', 'PRODUCTS-COMMERCIAL.json'),
    ('products.relationships', 'PRODUCT-RELATIONSHIPS.json'),
    # A camada de substancia ativa. `activeIngredients` e ENTIDADE e entra no
    # mestre; `products.activeIngredients` e LIGACAO produto-substancia e nao entra,
    # pela mesma lei que ja mantinha RELATIONSHIPS fora: ligacao aponta para o
    # registro, nao e o registro.
    ('activeIngredients', 'ACTIVE-INGREDIENTS.json'),
    ('products.activeIngredients', 'PRODUCT-ACTIVE-INGREDIENTS.json'),
    ('regulatoryFutureFacts', 'REGULATORY-FUTURE-FACTS.json'),
    ('windows', 'CROP-WINDOWS.json'),
    ('fieldSignals', 'CURRENT-FIELD-SIGNALS.json'),
    ('cropEconomicWeight', 'CROP-ECONOMIC-WEIGHT.json'),
    ('market', 'MARKET-OBSERVATIONS.json'),
    ('competitors', 'COMPETITOR-ACTIVITIES.json'),
    ('science', 'SCIENCE.json'),
    ('researchers', 'RESEARCHERS.json'),
    ('resistance', 'RESISTANCE.json'),
    ('voices', 'PUBLIC-VOICES.json'),
    ('channels', 'PUBLIC-CHANNELS.json'),
    ('regulatoryFuture', 'REGULATORY-FUTURE.json'),
    ('agromet', 'AGROMET-CONDITIONS.json'),
    ('events', 'EVENTS.json'),
    ('futureEvents', 'FUTURE-EVENTS.json'),
    ('opportunities', 'OPPORTUNITIES.json'),
    ('futureSignals', 'FUTURE-SIGNALS.json'),
    ('sources', 'SOURCES.json'),
    ('news', 'NEWS.json'),
    ('relationships', 'RELATIONSHIPS.json'),
    ('crossings', 'CLIENT-SAFE-CROSSINGS.json'),
]


def main():
    # ── §16 · o registro central ─────────────────────────────────────────────
    # ⚠️ O MESTRE INDEXA ENTIDADE. Vista e ligacao NAO entram.
    #
    # A primeira versao indexou tudo e produziu 62 IDs duplicados:
    #   · FUTURE-EVENTS e um RECORTE de EVENTS — o mesmo evento, duas vezes
    #   · RELATIONSHIPS carrega os IDs dos cruzamentos — o mesmo cruzamento, duas
    #
    # Nao sao duplicatas de dado: sao a mesma entidade vista de dois angulos. Mas
    # num REGISTRO CENTRAL isso e ambiguidade, e ambiguidade e o que este arquivo
    # existe para acabar.
    #
    #     UM ID, UM LUGAR. Vista e ligacao apontam para o registro; nao sao ele.
    NAO_ENTRA_NO_MESTRE = {'FUTURE-EVENTS.json', 'RELATIONSHIPS.json',
                           'PRODUCT-ACTIVE-INGREDIENTS.json'}

    mestre, por_col = [], {}
    for chave, arq in CONTRATO:
        p = os.path.join(ING, arq)
        if not os.path.exists(p):
            continue
        d = json.load(open(p, encoding='utf-8'))
        por_col[chave] = d
        if arq in NAO_ENTRA_NO_MESTRE:
            continue
        for r in d.get('RECORDS') or []:
            if not isinstance(r, dict) or not r.get('ID'):
                continue
            mestre.append({
                'ID': r['ID'],
                'FAMILY': d['COLLECTION'],
                'ENTITY_TYPE': r.get('ENTITY_TYPE') or r.get('CROSSING_TYPE'),
                'FILE': arq,
                'PROVENANCE': r.get('PROVENANCE'),
                'QA_STATUS': r.get('QA_STATUS'),
                'EVIDENCE_STATUS': r.get('EVIDENCE_STATUS'),
                'CLIENT_SAFE': bool(r.get('CLIENT_SAFE')),
                # ⚠️ SEM DEFAULT. Aqui havia `or 'DERIVED_V2_1'`, e ele apagou a
                # origem de 2.945 linhas do ISTAT: dado coletado de fora passou a
                # aparecer como deducao minha.
                #
                #     O DEFAULT SILENCIOSO E PIOR QUE O CAMPO VAZIO.
                #     O VAZIO SE VE. O DEFAULT MENTE COM CONFIANCA.
                #
                # Quem chega sem carimbo agora aparece como SEM_CARIMBO e o
                # fechamento reclama. Carimbar e trabalho do v21_carimbar_origem.
                'ORIGIN_LAYER': r.get('ORIGIN_LAYER') or 'SEM_CARIMBO',
                'SOURCE_IDS': r.get('SOURCE_IDS') or [],
                'CROP_IDS': r.get('CROP_IDS') or [],
                'REGION_IDS': r.get('REGION_IDS') or [],
                'GEOGRAPHIC_SCOPE': r.get('GEOGRAPHIC_SCOPE'),
            })
    dup = [k for k, v in Counter(x['ID'] for x in mestre).items() if v > 1]
    json.dump({
        'COLLECTION': 'CANONICAL_INTELLIGENCE_MASTER',
        'FILE': 'CANONICAL-INTELLIGENCE-MASTER.json',
        'SCHEMA_VERSION': 'V2.1', 'BUILT_AT': '2026-09-02', 'PRIMARY_KEY': 'ID',
        'WHAT_IT_IS': 'o registro central de TODA a inteligencia — a do handoff '
                      'anterior e a da last-mile, no mesmo indice.',
        'LAW': 'o Design nao pode precisar escolher entre arquivo velho e arquivo '
               'novo. Aqui todo ID tem um lugar so.',
        'COUNT_TOTAL': len(mestre),
        'COUNT_CLIENT_SAFE': sum(1 for x in mestre if x['CLIENT_SAFE']),
        'DUPLICATE_IDS': dup,
        'VIEWS_NOT_INDEXED': sorted(NAO_ENTRA_NO_MESTRE),
        'VIEWS_NOT_INDEXED_WHY':
            'FUTURE-EVENTS e um recorte de EVENTS; RELATIONSHIPS carrega os IDs '
            'dos cruzamentos. Os dois APONTAM para registros que ja estao aqui. '
            'Indexa-los criaria dois lugares para o mesmo ID.',
        'BY_ORIGIN': dict(Counter(x['ORIGIN_LAYER'] for x in mestre)),
        'BY_FAMILY': dict(Counter(x['FAMILY'] for x in mestre)),
        'BY_QA': dict(Counter(x['QA_STATUS'] for x in mestre)),
        'RECORDS': mestre,
    }, open(os.path.join(ING, 'CANONICAL-INTELLIGENCE-MASTER.json'), 'w',
            encoding='utf-8'), ensure_ascii=False, indent=1)

    # ── §17 · o manifesto ────────────────────────────────────────────────────
    cols = []
    for chave, arq in CONTRATO:
        d = por_col.get(chave)
        if not d:
            continue
        cols.append({
            'APP_KEY': 'APP.%s' % chave,
            'FILE': arq,
            'COLLECTION_NAME': d['COLLECTION'],
            'COUNT_TOTAL': d['COUNT_TOTAL'],
            'COUNT_CLIENT_SAFE': d['COUNT_CLIENT_SAFE'],
            'PRIMARY_KEY': d.get('PRIMARY_KEY'),
            'SCHEMA_VERSION': d.get('SCHEMA_VERSION'),
            'SOURCE_OF_TRUTH': d.get('SOURCE_OF_TRUTH'),
            'REPLACES_OLD_FILES': d.get('REPLACES_OLD_FILES') or [],
            'LAW': d.get('LAW'),
        })
    json.dump({
        'PACKAGE': 'ITALY-REALITY-HANDOFF-V2.1',
        'SCHEMA_VERSION': 'V2.1', 'BUILT_AT': '2026-09-02',
        'HOW_TO_LOAD': (
            'carregue SO os arquivos de DESIGN-INGEST/. Nao abra INTERNAL-ARCHIVE/: '
            'ele e o rastro do trabalho, nao o contrato.'),
        'MASTER_INDEX': 'CANONICAL-INTELLIGENCE-MASTER.json',
        'CLIENT_SAFE_RULE': {
            'true': 'QA_PASS · QA_CORRECTED · EVIDENCE_DOCUMENTED · EVIDENCE_SOURCED',
            'false': 'QA_UNREVIEWED · QA_REJECTED · EVIDENCE_DERIVED',
            'LEI': 'so CLIENT_SAFE=true sustenta afirmacao visivel ao cliente. '
                   'CLIENT_SAFE=false vive no corpus e aparece como RESEARCH_LEADS.',
        },
        'LANGUAGE_RULE': {
            'RESEARCH': 'as notas de pesquisa ficam em portugues dentro de RESEARCH — '
                        'o Design NUNCA precisa le-las.',
            'CLIENT_FIELDS': 'os campos interpretativos client-safe trazem *_IT e '
                             '*_EN prontos, com ORIGINAL_RESEARCH_TEXT ao lado.',
            'QUOTES': 'citacao publica permanece no idioma da fonte, sempre.',
        },
        'DOUBLE_COUNT_WARNING': (
            'FUTURE-EVENTS.json e um RECORTE de EVENTS.json. Carregar os dois soma o '
            'mesmo evento duas vezes.'),
        'COLLECTIONS': cols,
    }, open(os.path.join(ING, 'APP-MANIFEST.json'), 'w', encoding='utf-8'),
        ensure_ascii=False, indent=1)

    # ── §15 · o arquivo interno ──────────────────────────────────────────────
    for nome, origem in (
            ('V2-QUARANTINE', os.path.join(V2, 'QUARANTINED-RECORDS.json')),
            ('V2-VALIDATION', os.path.join(V2, 'VALIDATION-MANIFEST.json')),
            ('V2-CONFLICTS', os.path.join(V2, 'CONFLICT-RESOLUTION.json')),
            ('V2-REPORT', os.path.join(V2, 'HANDOFF-V2-REPORT.md')),
            ('V2-README', os.path.join(V2, 'README-FIRST.md'))):
        if os.path.exists(origem):
            shutil.copy2(origem, os.path.join(ARQ, os.path.basename(origem)))
    # a prosa e a pesquisa do handoff anterior
    prev = os.path.join(V2, 'PREVIOUS-HANDOFF')
    if os.path.isdir(prev):
        alvo = os.path.join(ARQ, 'PREVIOUS-HANDOFF-RAW')
        if os.path.isdir(alvo):
            shutil.rmtree(alvo)
        shutil.copytree(prev, alvo)
    for f in glob.glob(os.path.join(ROOT, 'research', 'italy-lastmile', '*')):
        shutil.copy2(f, os.path.join(ARQ, os.path.basename(f)))

    # ⚠️ O RASCUNHO DE CONSTRUÇÃO TAMBÉM É PAPEL DE TRABALHO.
    #
    # `_COLECOES.json` é um índice intermediário que o ingest escreve para si
    # mesmo. Ficou no pacote por não ter «AUDIT» nem «REPORT» no nome — e ali
    # dentro ele vira um SEGUNDO índice ao lado do APP-MANIFEST.
    #
    #     DOIS ÍNDICES É EXATAMENTE A AMBIGUIDADE QUE ESTE PACOTE EXISTE PARA
    #     ACABAR. Quem lê escolhe um, e um dia escolhe o desatualizado.
    #
    # Arquivo começado por `_` é de dentro da obra: sai do ingest, fica no
    # arquivo interno.
    for f in list(os.listdir(ING)):
        if f.startswith('_'):
            shutil.move(os.path.join(ING, f), os.path.join(ARQ, f))
            print('rascunho de build movido para o arquivo interno: %s' % f)

    # ⚠️ a prova de que o ingest nao tem papel de trabalho
    proibido = []
    for f in os.listdir(ING):
        if not f.endswith('.json'):
            proibido.append({'ARQUIVO': f, 'MOTIVO': 'so JSON no ingest'})
        if f.startswith('_'):
            proibido.append({'ARQUIVO': f, 'MOTIVO': 'rascunho de build'})
    for pat in ('DEMO', 'FAKE-TO-REAL', 'STORIES', 'AUDIT', 'RESEARCH-ARCHIVE',
                'GAPS', 'README', 'REPORT'):
        proibido += [{'ARQUIVO': f, 'MOTIVO': 'papel de trabalho: %s' % pat}
                     for f in os.listdir(ING) if pat in f.upper()]
    json.dump({
        'WHAT_IT_IS': 'o rastro do trabalho: quarentena, auditoria, historias de '
                      'demo, relatorios e o handoff anterior em forma bruta.',
        'LAW': 'o Design NAO precisa disto para renderizar o portal. Se precisar, o '
               'contrato falhou.',
        'FILES': sorted(os.listdir(ARQ)),
    }, open(os.path.join(ARQ, '_WHAT-IS-THIS.json'), 'w', encoding='utf-8'),
        ensure_ascii=False, indent=1)

    print('MASTER: %d registros · %d client-safe · IDs duplicados: %d'
          % (len(mestre), sum(1 for x in mestre if x['CLIENT_SAFE']), len(dup)))
    print('  por origem:', dict(Counter(x['ORIGIN_LAYER'] for x in mestre)))
    print()
    print('MANIFESTO: %d colecoes' % len(cols))
    print('INGEST: %d arquivos · papel de trabalho dentro dele: %d'
          % (len(os.listdir(ING)), len(proibido)))
    if proibido:
        print('  ⚠️', proibido[:4])
    # ⚠️ A PORTA DE ENTRADA VEM DO CODIGO, NAO DA PASTA.
    #
    # `v21_ingest.py` faz rmtree(OUT) antes de reescrever. O README-FIRST.md ja
    # foi escrito uma vez direto aqui dentro e desapareceu no build seguinte,
    # sem erro nenhum.
    #
    #     ARQUIVO ESCRITO A MAO DENTRO DA PASTA DE BUILD E ARQUIVO EMPRESTADO.
    readme = os.path.join(ROOT, 'docs', 'design', 'ITALY-V2.1-README-FIRST.md')
    if os.path.exists(readme):
        shutil.copy2(readme, os.path.join(V21, 'README-FIRST.md'))
        print('README-FIRST.md copiado do codigo para o pacote')
    else:
        print('ATENCAO: %s nao existe — o pacote vai sem porta de entrada'
              % readme)

    print('ARQUIVO INTERNO: %d itens' % len(os.listdir(ARQ)))


if __name__ == '__main__':
    main()
