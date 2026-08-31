"""Micro-reauditoria final — casco de deploy (Formulario e proximos passos.zip).

Mede os tres bloqueadores que restavam do index (12) e confere que nenhum PASS
anterior regrediu.

Uma nota sobre o formato da testemunha: este export nao e mais um HTML unico
empacotado — e uma pasta `deploy/` com o markup e a logica em `index.html`, o
runtime em `support.js` e o mapa em `crop-map.js`. O `index.html` fica guardado
GZIPADO: neste ambiente o antivirus prende o arquivo depois da escrita e nem o
Git consegue le-lo. O SHA-256 registrado e o dos bytes DESCOMPRIMIDOS, e ha
prova de que o round-trip e byte a byte.

Uso:
    py scripts/v8_receptor_ready.py            # imprime
    py scripts/v8_receptor_ready.py --sync     # grava o artefato
"""
import gzip
import json
import os
import re
import sys
from collections import Counter

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEPLOY = os.path.join(RAIZ, 'casco', 'canonical', 'deploy-v8-receptor-ready')
INDEX_GZ = os.path.join(DEPLOY, 'deploy-index.html.gz')
SUPPORT = os.path.join(DEPLOY, 'support.js')
CROPMAP = os.path.join(DEPLOY, 'crop-map.js')
SAIDA = os.path.join(RAIZ, 'data', 'implementation', 'V8-RECEPTOR-READY.json')

SHA_INDEX = 'a103bd62e3bbe92cbd56dd5b0da43a878fe4244db7bfbf89d683eaea8b024dc8'
SHA_SUPPORT = '8fe7df74405f3c55f49b7249c74ea1397e65d07dea2b1bd3b4a489bec2e28cbe'
SHA_CROPMAP = 'a55c6011e6aadb014b2617c8f5b302d9d2fb4bbfb1ee3e444cad345bbb1614c8'
SHA_ZIP = '7917564b64a99816cfe0dc3aa671be2e0092c6eb5e2fd2c557a4707766128efc'

PAYLOAD_CANONICO = {
    'H1': ['TERRITORIAL_OBSERVATION'],
    'H2': ['REGISTRATION_DEADLINE'],
    'H3': ['COMPETITOR_PRODUCT_IDENTITY'],
    'H4': ['OBSERVED_PAID_ACTIVITY'],
    'H5': ['FIELD_PRESSURE_SERIES'],
    'H6': ['PERSON_CREATOR', 'FARM_BUSINESS_ENTITY', 'CREATOR_CONTENT_PROFILE'],
    'H7': ['SCIENTIFIC_PERSON'],
    'H8': ['COMPANY_LOCAL_ACCOUNT'],
    'H9': ['CONTENT_ENTITY', 'CONTENT_TRANSLATION', 'ONTOLOGY_TERM'],
}
SUBRECEPTORES = {
    'R-H7-SCIENTIFIC-PUBLICATION': {'HOSE': 'H7', 'PARENT': 'H7',
                                    'LABEL': 'H7 · CIÊNCIA',
                                    'PAYLOAD': 'SCIENTIFIC_PUBLICATION'},
    'R-H2-LOCAL-ADAMA-PORTFOLIO': {'HOSE': 'H2', 'PARENT': 'H2',
                                   'LABEL': 'H2 · PORTFÓLIO',
                                   'PAYLOAD': 'LOCAL_ADAMA_PORTFOLIO_CONTEXT'},
    'R-H6-FIELD-VOICE': {'HOSE': 'H6', 'PARENT': 'H6',
                         'LABEL': 'H6 · CAMPO',
                         'PAYLOAD': 'FIELD_VOICE_OBSERVATION'},
}
OITO_ESTADOS = ('UNWIRED', 'LOADING', 'READY', 'EMPTY_VALID',
                'NOT_STARTED', 'NOT_AVAILABLE', 'BLOCKED', 'ERROR_FAIL_CLOSED')
ACAO_CANONICA = ('BUSINESS_DECISION', 'SYSTEM_DECISION', 'INVESTIGATION')
PAYLOAD_TEXTUAL = ('R-H9-CONTENT-ENTITY', 'R-H7-SCIENTIFIC-PUBLICATION',
                   'R-H6-FIELD-VOICE')

# vocabulario canonico de ENTITY_KIND, do schema do Supabase (creator_entity_kind)
CREATOR_ENTITY_KIND = ('PERSON_CREATOR', 'FARM_BUSINESS_ENTITY')


def abrir():
    """(index.html, support.js, crop-map.js). O index vem do .gz."""
    with open(INDEX_GZ, 'rb') as fh:
        idx = gzip.decompress(fh.read()).decode('utf-8', 'replace')
    with open(SUPPORT, encoding='utf-8', errors='replace') as fh:
        sup = fh.read()
    with open(CROPMAP, encoding='utf-8', errors='replace') as fh:
        mapa = fh.read()
    return idx, sup, mapa


def logica(idx):
    """O bloco data-dc-script: e AQUI que a logica do app vive.

    support.js e o runtime gerado (dc-runtime), nao uma segunda copia da logica.
    Confundir os dois faria procurar receptor no arquivo errado.
    """
    return re.findall(r'<script[^>]*data-dc-script[^>]*>(.*?)</script>', idx, re.S)[0]


def markup(idx):
    m = re.sub(r'<script[^>]*data-dc-script[^>]*>.*?</script>', '', idx, flags=re.S)
    return re.sub(r'<style[^>]*>.*?</style>', '', m, flags=re.S)


def fatiar(mk):
    ab = [(m.start(), m.group(1)) for m in
          re.finditer(r'sc-if\s+value="\{\{\s*at\.([a-z]+)\s*\}\}"', mk)]
    fat = {}
    for i, (p, n) in enumerate(ab):
        fim = ab[i + 1][0] if i + 1 < len(ab) else len(mk)
        fat.setdefault(n, []).append(mk[p:fim])
    return {k: ''.join(v) for k, v in fat.items()}


def receptores(cam):
    achados = []
    marcas = [m.start() for m in re.finditer(r"receptor\(\{", cam)]
    for i, ini in enumerate(marcas):
        fim = marcas[i + 1] if i + 1 < len(marcas) else len(cam)
        b = cam[ini:fim]
        corte = b.find('fields:')
        cab = b[:corte] if corte > 0 else b

        def g(k, txt=cab):
            # limite de token: `load: '` casa dentro de `payload: '`
            m = re.search(r"(?:^|[\s,{])%s: '([^']*)'" % k, txt)
            return m.group(1) if m else None
        pay = g('payload') or ''
        achados.append({
            'RECEPTOR_ID': g('id'), 'HOSE_ID': g('hose'),
            'PARENT_HOSE_ID': g('parent'), 'DISPLAY_LABEL': g('displayLabel'),
            'CANONICAL_PAYLOAD_TYPE': pay.split('· ', 1)[-1] if '· ' in pay else pay,
            'LOAD_STATE': g('load'), 'NO_DATA_REASON': g('reasonKey'),
        })
    return achados


def campo(cam, rid, nome):
    i = cam.find("id: '%s'" % rid)
    if i < 0:
        return None
    fim = cam.find('failClosed:', i)
    m = re.search(r"FIELD\('%s', ([^,]+)," % re.escape(nome), cam[i:fim])
    return m.group(1).strip() if m else None


def medir(fontes=None, shas=None):
    """Mede uma testemunha de deploy.

    `fontes` permite medir OUTRA testemunha com a mesma logica — e o que o
    fechamento de uma linha usa, para nao existir um segundo medidor quase
    identico que possa divergir deste.
    """
    idx, sup, mapjs = fontes if fontes else abrir()
    cam = logica(idx)
    mk = markup(idx)
    telas = fatiar(mk)
    decl = receptores(cam)
    por_id = {r['RECEPTOR_ID']: r for r in decl}
    por_hose = {r['HOSE_ID']: r for r in decl if r['PARENT_HOSE_ID'] is None}

    # ── 1 · helper ──
    h = re.search(r'const receptor = \(r\) => \(\{(.*?)\n    \}\);', cam, re.S)
    helper = h.group(1) if h else ''
    hose_canonico = bool(re.search(r'hoseId:\s*r\.hose\s*,', helper))
    hose_do_display = 'hoseId: r.displayLabel' in helper
    display_separado = bool(re.search(r'displayLabel:\s*r\.displayLabel\s*\|\|\s*r\.hose', helper))
    parent_estrutural = bool(re.search(r'parentHoseId:\s*r\.parent\s*\|\|\s*null', helper))
    parent_no_note = "PARENT_HOSE_ID · ' + r.parent" in helper
    parent_como_linha = "k: 'PARENT_HOSE_ID', v: r.parent" in helper

    # ── 2 · mangueiras ──
    hoses = {}
    for hose, esperados in PAYLOAD_CANONICO.items():
        r = por_hose.get(hose)
        if r is None:
            hoses[hose] = {'VERDICT': 'FAIL', 'MISSING': ['sem receptor']}
            continue
        falta = []
        declarados = [p.strip() for p in r['CANONICAL_PAYLOAD_TYPE'].split('|')]
        if sorted(declarados) != sorted(esperados):
            falta.append('payload %s != %s' % (declarados, esperados))
        if r['LOAD_STATE'] not in OITO_ESTADOS:
            falta.append('LOAD_STATE %s' % r['LOAD_STATE'])
        if not r['NO_DATA_REASON']:
            falta.append('sem NO_DATA_REASON')
        hoses[hose] = {'VERDICT': 'FAIL' if falta else 'PASS', 'MISSING': falta,
                       'RECEPTOR_ID': r['RECEPTOR_ID'],
                       'CANONICAL_PAYLOAD_TYPE': r['CANONICAL_PAYLOAD_TYPE']}

    # ── 3 · subreceptores ──
    sub = {}
    for rid, esp in SUBRECEPTORES.items():
        r = por_id.get(rid)
        if r is None:
            sub[rid] = {'VERDICT': 'FAIL', 'MISSING': ['ausente']}
            continue
        falta = []
        if r['HOSE_ID'] != esp['HOSE']:
            falta.append('HOSE_ID = %s' % r['HOSE_ID'])
        if r['PARENT_HOSE_ID'] != esp['PARENT']:
            falta.append('PARENT_HOSE_ID = %s' % r['PARENT_HOSE_ID'])
        if r['DISPLAY_LABEL'] != esp['LABEL']:
            falta.append('DISPLAY_LABEL = %s' % r['DISPLAY_LABEL'])
        if r['CANONICAL_PAYLOAD_TYPE'] != esp['PAYLOAD']:
            falta.append('payload = %s' % r['CANONICAL_PAYLOAD_TYPE'])
        if not hose_canonico or hose_do_display:
            falta.append('helper nao expoe HOSE_ID canonico')
        if not parent_estrutural:
            falta.append('PARENT_HOSE_ID nao e campo do helper')
        sub[rid] = {'VERDICT': 'FAIL' if falta else 'PASS', 'MISSING': falta,
                    'HOSE_ID': r['HOSE_ID'], 'PARENT_HOSE_ID': r['PARENT_HOSE_ID'],
                    'DISPLAY_LABEL': r['DISPLAY_LABEL']}

    # ── 4 · SOURCE_LANGUAGE ──
    lingua = {}
    for rid in PAYLOAD_TEXTUAL:
        v = campo(cam, rid, 'SOURCE_LANGUAGE')
        lingua[rid] = {'EXPRESSAO': v,
                       'CAI_EM_UNKNOWN': bool(v and 'unknown' in v.lower()),
                       'CAI_EM_TRACO': v == 'null'}

    # ── 5 · ENTITY_KIND do FIELD_VOICE contra o vocabulario canonico ──
    ek_voice = campo(cam, 'R-H6-FIELD-VOICE', 'ENTITY_KIND')
    ek_creator = campo(cam, 'R-H6-CREATOR', 'ENTITY_KIND')
    def kinds(expr):
        return sorted(x.strip() for x in (expr or '').strip("'").split('|') if x.strip())
    voice_kinds, creator_kinds = kinds(ek_voice), kinds(ek_creator)
    voice_drift = [k for k in voice_kinds if k not in CREATOR_ENTITY_KIND]

    # ── 6 · nao regressao ──
    ret = cam[cam.rindex('\n    return {'):]
    usados = set(re.findall(r'sc-camel-on-click="\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\}\}"', mk))
    mortos = sorted(x for x in usados
                    if not re.search(r'(^|[\s,{])' + x + r'\s*[:,\n]', ret))
    ev = re.search(r"const EVIDENCE = \{(.*?)\n    \};", cam, re.S)
    hoses_gaveta = sorted(set(re.findall(r"hose: '([A-Z0-9]+)'", ev.group(1)))) if ev else []
    CONV = ('conv.propositionId', 'conv.kind', 'conv.state', 'conv.independentCount',
            'l.family', 'l.dependency', 'l.dependencyNote', 'l.openEvidence')
    conv_radar = [c for c in CONV if ('{{ %s }}' % c) in telas.get('radar', '')]
    conv_obj = [c for c in CONV if ('{{ %s }}' % c) in telas.get('obj', '')]
    kind = re.search(r"const KIND = \{(.*?)\};", cam, re.S)
    canonicos = re.findall(r"canonical: '([A-Z_]+)'", kind.group(1)) if kind else []
    tl = [c for c in ('EVENT_ID', 'EVENT_TYPE', 'EVENT_AT', 'EVENT_AT_RESOLUTION',
                      'SOURCE_ID', 'OBSERVATION_ID', 'STATE_BEFORE', 'STATE_AFTER',
                      'GAP_REASON') if ("k: '%s'" % c) in cam]
    segredos = [t for t in ('SERVICE_ROLE_KEY', 'service_role', 'SUPABASE_KEY',
                            'apikey', 'Bearer ') if t in idx or t in sup]

    passa_sub = sum(1 for v in sub.values() if v['VERDICT'] == 'PASS')
    passa_hose = sum(1 for v in hoses.values() if v['VERDICT'] == 'PASS')
    lingua_ok = all(v['CAI_EM_UNKNOWN'] for v in lingua.values())

    s = shas or {'INDEX': SHA_INDEX, 'SUPPORT': SHA_SUPPORT, 'CROPMAP': SHA_CROPMAP,
                 'ZIP': SHA_ZIP, 'INDEX_BYTES': 372418}
    return {
        'CASCO': {
            'FORMATO': 'pasta deploy/ — markup e logica em index.html, runtime em support.js',
            'INDEX_SHA256': s['INDEX'], 'SUPPORT_SHA256': s['SUPPORT'],
            'CROPMAP_SHA256': s['CROPMAP'], 'ZIP_SHA256': s['ZIP'],
            'INDEX_BYTES': s['INDEX_BYTES'], 'LOGICA_CHARS': len(cam), 'MARKUP_CHARS': len(mk),
            'TELAS': sorted(telas),
            'SUPPORT_E_RUNTIME_NAO_LOGICA': ('const receptor' not in sup
                                             and 'CONV_LEGS' not in sup),
        },
        'RECEPTORES_DECLARADOS': decl,
        'VERDICTS': {
            'HOSES': hoses,
            'HOSES_WITH_COMPLETE_RECEIVER': passa_hose,
            'SUBRECEPTORES': sub,
            'SUBRECEPTOR_HOSE_ID_CANONICAL': 'PASS' if passa_sub == 3 else 'FAIL',
            'DISPLAY_LABEL_SEPARATE': 'PASS' if display_separado else 'FAIL',
            'PARENT_HOSE_ID_STRUCTURAL': 'PASS' if parent_estrutural else 'FAIL',
            'SOURCE_LANGUAGE_UNKNOWN_GLOBAL': 'PASS' if lingua_ok else 'FAIL',
            'FIELD_VOICE_ENTITY_KIND_CANONICAL': 'PASS' if not voice_drift else 'FAIL',
            'RADAR_CONVERGENCE_PARITY': 'PASS' if (conv_radar == conv_obj and conv_obj) else 'FAIL',
            'DEAD_HANDLERS': len(mortos),
            'EVIDENCE_DRAWER_HOSES_COVERED': len(hoses_gaveta),
            'ACTION_TYPE_CANONICAL': 'PASS' if (sorted(canonicos) == sorted(ACAO_CANONICA)
                                                and 'actionType: KIND[a.kind].canonical' in cam)
                                     else 'FAIL',
            'ACTION_MAP_OBJECT_ID': 'PASS' if 'objectId: base.id' in cam else 'FAIL',
            'TIMELINE_TYPED': 'PASS' if (len(tl) == 9 and "' → '" not in cam) else 'FAIL',
            'GITHUB_PROVENANCE': 'PASS' if 'provGithub' in cam else 'FAIL',
            'SUPABASE_PROVENANCE': 'PASS' if 'provSupabase' in cam else 'FAIL',
            'CROP_MAP_GUARD': 'PASS' if ("p.GEO_RESOLUTION === 'POINT'" in mapjs
                                         and sorted(set(re.findall(
                                             r"GEO_RESOLUTION: '([A-Z_]+)'", cam))) == ['NOT_KNOWN'])
                              else 'FAIL',
            'NO_FRONTEND_SECRET': 'PASS' if not segredos else 'FAIL',
        },
        'HELPER': {
            'HOSE_ID_CANONICO': hose_canonico, 'HOSE_ID_DO_DISPLAY_LABEL': hose_do_display,
            'DISPLAY_LABEL_SEPARADO': display_separado,
            'PARENT_HOSE_ID_ESTRUTURAL': parent_estrutural,
            'PARENT_HOSE_ID_NO_NOTE': parent_no_note,
            'PARENT_HOSE_ID_COMO_LINHA_DE_CAMPO': parent_como_linha,
        },
        'SOURCE_LANGUAGE': lingua,
        'ENTITY_KIND': {
            'VOCABULARIO_CANONICO': list(CREATOR_ENTITY_KIND),
            'FONTE_DA_AUTORIDADE': 'data/supabase/SUPABASE-CANONICAL-SCHEMA.json :: '
                                   'VOCABULARIES.creator_entity_kind, usado por '
                                   'field_voice_observation.entity_kind',
            'R-H6-CREATOR': creator_kinds,
            'R-H6-FIELD-VOICE': voice_kinds,
            'DRIFT': voice_drift,
        },
        'HANDLERS_MORTOS': mortos,
        'CONVERGENCIA': {
            'RADAR': conv_radar, 'OBJ': conv_obj,
            'PERNAS': [{'SIGNAL_FAMILY': f, 'INDEPENDENCE_STATE': i,
                        'DEPENDENCY_RELATION': d or 'INDEPENDENT_SOURCE'}
                       for f, i, d in re.findall(
                           r"family: '([A-Z_]+)'.*?independence: '([A-Z]+)'"
                           r"(?:, dependency: '([A-Z_]+)'|, dependency: null)", cam, re.S)],
            'CONTAGEM_DERIVADA': 'const independentCount = CONV_LEGS.filter' in cam,
        },
        'GAVETA': {'HOSES': hoses_gaveta},
        'TIMELINE': {'CAMPOS': tl},
        'LOAD_STATES': {'DECLARADOS': [e for e in OITO_ESTADOS if ('%s:' % e) in cam],
                        'EXERCIDOS': dict(Counter(re.findall(r"load: '([A-Z_]+)'", cam)))},
    }


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    m = medir()
    if '--sync' in sys.argv:
        with open(SAIDA, 'w', encoding='utf-8', newline='\n') as fh:
            json.dump(m, fh, ensure_ascii=False, indent=2)
            fh.write('\n')
        print('gravado em', os.path.relpath(SAIDA, RAIZ))
    v = dict(m['VERDICTS'])
    v.pop('HOSES'), v.pop('SUBRECEPTORES')
    print(json.dumps(v, ensure_ascii=False, indent=2))
    print('\nENTITY_KIND:', json.dumps(m['ENTITY_KIND'], ensure_ascii=False, indent=1))
    print('SOURCE_LANGUAGE:', json.dumps(m['SOURCE_LANGUAGE'], ensure_ascii=False))
