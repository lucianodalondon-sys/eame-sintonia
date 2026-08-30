#!/usr/bin/env python3
"""
SEED ITALIANA — a lista externa, gravada como ALEGAÇÃO e nunca como fato.

    python3 scripts/creator_seed_it.py montar
    python3 scripts/creator_seed_it.py resumo

POR QUE A SEED ENTRA NUM ARQUIVO SEPARADO
-------------------------------------------
Porque ela é de outra natureza. `CREATORS-ES-IT-FR.json` guarda o que ALGUMA
fonte pública afirmou; a seed guarda o que uma LISTA afirmou. Misturar os dois
faria a lista herdar, por vizinhança, a credibilidade da pesquisa — que é
exatamente o mecanismo pelo qual uma planilha vira verdade sem nunca ter sido
verificada.

Por isso todo campo de prova nasce fechado:

    HANDLE_EXISTS = NOT_TESTED       CROP_STATE = NOT_KNOWN
    NAME_MATCH    = NOT_TESTED       ACTUAL_FARMER = NOT_KNOWN

`CROP_CLAIMED_BY_SEED` preserva o que a lista disse. `CROP_PROVED_BY_CONTENT`
começa vazio e só se preenche com conteúdo observado. Os dois nunca são o
mesmo campo — se fossem, a alegação viraria prova na primeira gravação.

A SUSPEITA QUE A PRÓPRIA SEED LEVANTA, E QUE NÃO PODE SER RESOLVIDA POR PALPITE
-------------------------------------------------------------------------------
Vinte e cinco handles chegaram distribuídos por sete culturas. Os blocos de
UVA e AZEITE trazem handles cujo próprio nome sugere PRODUTO FINAL, não
lavoura: `@doctor.wine`, `@thewinekiller`, `@enoblogger`, `@italianwinelover`
no bloco de viticultura; `@evolovers`, `@tastevo`, `@ilsommolier`,
`@oiltogether` no de olivicultura. E `@mircocolzani_gardendesigner` chegou no
bloco de FRUTICULTURA.

Isso é SUSPEITA DERIVADA DO HANDLE, e ela vale exatamente o que vale: um sinal
para priorizar a checagem, nunca um veredito. O campo que carrega isso é
`SUSPECTED_CHAIN_MISMATCH`, e ele é deliberadamente distinto de
`CROP_STATE = WRONG_ASSIGNMENT` — o primeiro é uma hipótese nossa, o segundo
seria uma medição. Promover um no outro sem abrir o perfil seria cometer, do
lado cético, o mesmo erro que a seed cometeu do lado otimista.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import creators as cr                                        # noqa: E402

MISSION = '14-MAPA-DE-CREATORS-EAME'
SEED_ID = 'SEED-EXTERNO-IT-2026-08-30'
CAPTURA = '2026-08-30'

# ═══════════════════════════════════════════════════════════════════════════
# A LISTA, VERBATIM. (handle, nome, cultura alegada pelo bloco da seed)
# A ordem e a grafia são as da lista — normalizar aqui apagaria o que ela disse.
# ═══════════════════════════════════════════════════════════════════════════
SEED = [
    ('@italianwinelover',            'Francesco Saverio Russo', 'GRAPEVINE'),
    ('@enoblogger',                  'Emanuele Trono',          'GRAPEVINE'),
    ('@doctor.wine',                 'Daniele Cernilli',        'GRAPEVINE'),
    ('@giulia_sattin',               'Giulia Sattin',           'GRAPEVINE'),
    ('@thewinekiller',               'Luca Gardini',            'GRAPEVINE'),

    ('@evolovers',                   'Leonardo Leggeri',        'OLIVE'),
    ('@tastevo',                     'Gabriele Sabatino',       'OLIVE'),
    ('@ilsommolier',                 'Dario Masciaga',          'OLIVE'),
    ('@oiltogether',                 'Giuseppe Salone',         'OLIVE'),
    ('@mariaclaratiberi',            'Maria Clara Tiberi',      'OLIVE'),

    ('@davide_gomiero',              'Davide Gomiero',          'WHEAT'),
    ('@filippoballardin',            'Filippo Ballardin',       'WHEAT'),
    ('@federicovalgoi',              'Federico Valgoi',         'WHEAT'),
    ('@agromoderni',                 'Agromoderni / Italian Farm', 'WHEAT'),

    ('@yuliyapyliavska',             'Yuliya Pyliavska',        'MAIZE'),
    ('@giulia_tonello',              'Giulia Tonello',          'MAIZE'),
    ('@pedro.pastore',               'Pedro Pastore',           'MAIZE'),
    ('@nicolo.polo',                 'Nicolò Polo',             'MAIZE'),

    ('@maria.pezone',                'Maria Pezone',            'TOMATO_HORTICULTURE'),
    ('@mattthefarmer',               'Matt The Farmer',         'TOMATO_HORTICULTURE'),
    ('@theyoungnonno',               'The Young Nonno',         'TOMATO_HORTICULTURE'),
    ('@the_pleasure_garden',         'Gaetano Zoccali',         'TOMATO_HORTICULTURE'),

    ('@alexfarmer_it',               'Alex Farmer',             'FRUIT_ORCHARD'),
    ('@giacomolepri',                'Giacomo Lepri',           'FRUIT_ORCHARD'),
    ('@mircocolzani_gardendesigner', 'Mirco Colzani',           'FRUIT_ORCHARD'),

    ('@yuliyapyliavska',             'Yuliya Pyliavska',        'RICE'),
    ('@davide_gomiero',              'Davide Gomiero',          'RICE'),
    ('@agromoderni',                 'Agromoderni / Italian Farm', 'RICE'),
]

# Sinais lexicais que levantam SUSPEITA de cadeia — produto final, não lavoura.
# Lista fechada e explícita: um heurístico que ninguém consegue ler vira magia.
LEXICO_PRODUTO_FINAL = {
    'wine': 'vinho (produto final)', 'eno': 'enologia/vinho',
    'sommolier': 'sommelier', 'sommelier': 'sommelier',
    'evo': 'EVO = azeite extra virgem (produto final)',
    'oil': 'azeite (produto final)', 'taste': 'degustação',
    'gardendesigner': 'design de jardim — não é produção agrícola',
    'garden': 'jardim/ornamental',
}


def _suspeita(handle, cultura):
    h = handle.lower().lstrip('@').replace('_', '').replace('.', '')
    achados = [d for termo, d in LEXICO_PRODUTO_FINAL.items() if termo in h]
    if not achados:
        return 'NO', cr.NAO_SEI
    return 'YES', ('handle sugere %s, enquanto a seed o atribuiu a %s — '
                   'CHECAR ANTES DE USAR. Suspeita derivada do handle, não medição.'
                   % (' / '.join(sorted(set(achados))), cultura))


def _registro(handle, nome, cultura, idx):
    r = cr.registro_vazio()
    r.update({
        'CREATOR_ID': 'IT-SEED-%03d' % idx,
        'ORIGIN_ID': handle,
        'NAME': nome,
        'DISPLAY_NAME': handle,
        'COUNTRY': 'IT',
        'LANGUAGE': 'it',
        'ENTITY_KIND': 'NOT_KNOWN',
        'INSTAGRAM': handle,
        'PLATFORMS': ['INSTAGRAM'],
        'SOURCE_URL': 'SEED_EXTERNO — lista fornecida pelo dono da missão',
        'SOURCE_ID': SEED_ID,
        'SOURCE_KIND': 'EXTERNAL_SEED_LIST',
        'CAPTURE_DATE': CAPTURA,
        'COLLECTION_ROUTE': 'SEED — nenhuma coleta executada sobre este registro ainda',

        # ── nada foi verificado. Estes quatro campos são o coração do arquivo.
        'HANDLE_EXISTS': 'NOT_TESTED',
        'PROFILE_URL': cr.NAO_SEI,
        'NAME_MATCH': 'NOT_TESTED',
        'IDENTITY_STATE': 'NOT_PROVED',
        'IDENTITY_EVIDENCE': 'a lista afirmou nome e handle; nada foi aberto nem conferido',

        # ── a alegação e a prova, em campos diferentes e para sempre
        'CROP_CLAIMED_BY_SEED': cultura,
        'CROP_PROVED_BY_CONTENT': cr.NAO_SEI,
        'CROP_PROOF_URLS': [],
        'CROPS': cr.NAO_SEI,
        'CROP_STATE': 'NOT_KNOWN',
        'CROP_EVIDENCE': 'nenhum conteúdo observado — a seed não é conteúdo',

        'CREATOR_TYPE': cr.NAO_SEI,
        'ACTUAL_FARMER': 'NOT_KNOWN',
        'ACTUAL_FARMER_EVIDENCE': 'não testado',
        'SENSOR_ROLE_LINK': 'NOT_LINKED',
        'ACTIVATION_CREATOR': 'NOT_KNOWN',
        'TECHNICAL_SENSOR_CANDIDATE': 'NOT_KNOWN',

        'WINE_RELEVANCE': 'NOT_KNOWN', 'VITICULTURE_RELEVANCE': 'NOT_KNOWN',
        'OLIVE_OIL_RELEVANCE': 'NOT_KNOWN', 'OLIVE_GROWING_RELEVANCE': 'NOT_KNOWN',

        'ACTIVITY_STATE': 'NOT_MEASURED',
        'AUDIENCE_TYPE': 'NOT_KNOWN',
        'BRAND_RELATIONSHIP_STATE': 'NOT_KNOWN',
        'ADAMA_COLLABORATION_OBSERVED': 'NOT_TESTED',
        'RELEVANCE_STATE': 'RESEARCH_NEEDED',
    })
    suspeita, motivo = _suspeita(handle, cultura)
    r['SUSPECTED_CHAIN_MISMATCH'] = suspeita
    r['SUSPECTED_CHAIN_MISMATCH_REASON'] = motivo
    r['WHY_RELEVANT'] = ['SEED_NAO_VALIDADA: nenhum campo desta ficha foi verificado']
    return r


def montar():
    os.makedirs(cr.BASE, exist_ok=True)
    regs, vistos, dups = [], {}, []
    for i, (handle, nome, cultura) in enumerate(SEED, 1):
        if handle in vistos:
            # A duplicata NÃO é erro da lista: é a mesma pessoa alegada em duas
            # culturas. Preservar as duas alegações, num registro só.
            alvo = vistos[handle]
            atual = alvo['CROP_CLAIMED_BY_SEED']
            alvo['CROP_CLAIMED_BY_SEED'] = (
                atual if isinstance(atual, list) else [atual]) + [cultura]
            dups.append({'HANDLE': handle, 'CULTURAS': alvo['CROP_CLAIMED_BY_SEED']})
            continue
        r = _registro(handle, nome, cultura, i)
        vistos[handle] = r
        regs.append(r)

    problemas = []
    for r in regs:
        for f in cr.checar(r):
            problemas.append('%s: %s' % (r['CREATOR_ID'], f))
    if problemas:
        print('PORTAO_BARROU:'); [print('  ' + p) for p in problemas]; raise SystemExit(1)

    suspeitos = [r for r in regs if r['SUSPECTED_CHAIN_MISMATCH'] == 'YES']
    corpo = {
        'SOURCE_ID': SEED_ID, 'MISSION': MISSION, 'CAPTURED_AT': CAPTURA,
        'STATE': 'CLAIMS_ONLY — nenhum campo verificado',
        'LAW': 'A seed é ALEGAÇÃO. CROP_CLAIMED_BY_SEED != CROP_PROVED_BY_CONTENT, '
               'e os dois nunca ocupam o mesmo campo.',
        'SEED_ROWS': len(SEED),
        'UNIQUE_HANDLES': len(regs),
        'DUPLICATE_ROWS': dups,
        'SUSPECTED_CHAIN_MISMATCH_COUNT': len(suspeitos),
        'SUSPECTED_CHAIN_MISMATCH_NOTE':
            'Suspeita derivada do HANDLE, para priorizar checagem. NÃO é veredito: '
            'promover isto a WRONG_ASSIGNMENT sem abrir o perfil cometeria, do lado '
            'cético, o mesmo erro que a seed cometeu do lado otimista.',
        'CANDIDATES': regs,
    }
    with open(os.path.join(cr.BASE, 'SEED-IT-CANDIDATES.json'), 'w', encoding='utf-8') as f:
        json.dump(corpo, f, ensure_ascii=False, indent=2)
    print('gravado: data/samples/CREATOR-MAP-EAME/SEED-IT-CANDIDATES.json')
    print('SEED_ROWS=%d  UNIQUE_HANDLES=%d  DUPLICATAS=%d  SUSPEITA_DE_CADEIA=%d'
          % (len(SEED), len(regs), len(dups), len(suspeitos)))
    for r in suspeitos:
        print('  SUSPEITA %-30s %s' % (r['ORIGIN_ID'], r['SUSPECTED_CHAIN_MISMATCH_REASON'][:64]))


def resumo():
    d = cr.carregar('SEED-IT-CANDIDATES.json')
    print('CANDIDATOS=%d' % len(d))
    from collections import Counter
    print('CROP_STATE:', dict(Counter(r['CROP_STATE'] for r in d)))
    print('HANDLE_EXISTS:', dict(Counter(r['HANDLE_EXISTS'] for r in d)))


if __name__ == '__main__':
    {'montar': montar, 'resumo': resumo}.get(
        sys.argv[1] if len(sys.argv) > 1 else 'montar', montar)()
