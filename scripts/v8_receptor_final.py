"""Medicao final de recepcao — casco index (12).

Mede o casco contra o MODELO CANONICO, nao contra o que o casco chama as coisas.
Emite data/implementation/V8-RECEPTOR-FINAL.json.

Os medidores anteriores continuam existindo e continuam medindo os cascos
anteriores: index (10) em v8_receptor_audit.py e index (11) em
v8_receptor_reaudit.py. Apagar um medidor apagaria a prova de que algo mudou.

Uso:
    py scripts/v8_receptor_final.py            # imprime
    py scripts/v8_receptor_final.py --sync     # grava o artefato
"""
import base64
import gzip
import json
import os
import re
import sys
from collections import Counter

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CASCO12 = os.path.join(RAIZ, 'casco', 'canonical', 'SINTONIA-EAME-V8-FINAL.html')
SAIDA = os.path.join(RAIZ, 'data', 'implementation', 'V8-RECEPTOR-FINAL.json')

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
VOCABULARIO_HOSE = tuple(PAYLOAD_CANONICO)

SUBRECEPTORES = {
    'R-H7-SCIENTIFIC-PUBLICATION': {'HOSE': 'H7', 'PARENT': 'H7',
                                    'PAYLOAD': 'SCIENTIFIC_PUBLICATION'},
    'R-H2-LOCAL-ADAMA-PORTFOLIO': {'HOSE': 'H2', 'PARENT': 'H2',
                                   'PAYLOAD': 'LOCAL_ADAMA_PORTFOLIO_CONTEXT'},
    'R-H6-FIELD-VOICE': {'HOSE': 'H6', 'PARENT': 'H6',
                         'PAYLOAD': 'FIELD_VOICE_OBSERVATION'},
}

OITO_ESTADOS = ('UNWIRED', 'LOADING', 'READY', 'EMPTY_VALID',
                'NOT_STARTED', 'NOT_AVAILABLE', 'BLOCKED', 'ERROR_FAIL_CLOSED')

ACAO_CANONICA = ('BUSINESS_DECISION', 'SYSTEM_DECISION', 'INVESTIGATION')

LINGUA_FECHADA = ('pt', 'en', 'es', 'fr', 'it', 'MULTILINGUAL', 'UNKNOWN')

# payloads textuais onde a regra global de SOURCE_LANGUAGE tem de valer
PAYLOAD_TEXTUAL = ('R-H9-CONTENT-ENTITY', 'R-H7-SCIENTIFIC-PUBLICATION',
                   'R-H6-FIELD-VOICE')


def abrir(caminho=CASCO12):
    """(markup sem codigo e sem estilo, camada de dados, assets js)."""
    with open(caminho, encoding='utf-8', errors='replace') as fh:
        bruto = fh.read()
    documento = json.loads(
        re.search(r'<script type="__bundler/template">(.*?)</script>', bruto, re.S).group(1).strip())
    camada = re.findall(r'<script[^>]*data-dc-script[^>]*>(.*?)</script>', documento, re.S)[0]
    markup = re.sub(r'<script[^>]*data-dc-script[^>]*>.*?</script>', '', documento, flags=re.S)
    markup = re.sub(r'<style[^>]*>.*?</style>', '', markup, flags=re.S)
    ativos = {}
    man = re.search(r'<script type="__bundler/manifest">(.*?)</script>', bruto, re.S)
    if man:
        for chave, item in json.loads(man.group(1).strip()).items():
            if 'javascript' not in item.get('mime', ''):
                continue
            dados = base64.b64decode(item['data'])
            if item.get('compressed'):
                dados = gzip.decompress(dados)
            ativos[chave] = dados.decode('utf-8', 'replace')
    return markup, camada, ativos


def fatiar(markup):
    ab = [(m.start(), m.group(1)) for m in
          re.finditer(r'sc-if\s+value="\{\{\s*at\.([a-z]+)\s*\}\}"', markup)]
    fat = {}
    for i, (p, n) in enumerate(ab):
        fim = ab[i + 1][0] if i + 1 < len(ab) else len(markup)
        fat.setdefault(n, []).append(markup[p:fim])
    return {k: ''.join(v) for k, v in fat.items()}


def receptores(camada):
    """Cada chamada receptor({...}), com hose, parent e displayLabel separados.

    Duas armadilhas que custaram uma rodada:
    - `load: '` casa DENTRO de `payload: '`. A chave precisa comecar em limite
      de token, senao o estado de carga vira o nome do payload.
    - a indentacao do bloco varia entre objReceptors, sourceReceptors e
      systemReceptors. Fatiar por `\\n      fields:` perdia o receptor de H9.
    """
    achados = []
    marcas = [m.start() for m in re.finditer(r"receptor\(\{", camada)]
    for i, ini in enumerate(marcas):
        fim = marcas[i + 1] if i + 1 < len(marcas) else len(camada)
        b = camada[ini:fim]
        corte = b.find('fields:')
        cabeca = b[:corte] if corte > 0 else b

        def g(k, texto=cabeca):
            achado = re.search(r"(?:^|[\s,{])%s: '([^']*)'" % k, texto)
            return achado.group(1) if achado else None
        payload = g('payload') or ''
        achados.append({
            'RECEPTOR_ID': g('id'), 'HOSE_ID': g('hose'),
            'PARENT_HOSE_ID': g('parent'), 'DISPLAY_LABEL': g('displayLabel'),
            'CANONICAL_PAYLOAD_TYPE': payload.split('· ', 1)[-1] if '· ' in payload else payload,
            'LOAD_STATE': g('load'), 'NO_DATA_REASON': g('reasonKey'),
        })
    return achados


def campos_do_receptor(camada, receptor_id):
    i = camada.find("id: '%s'" % receptor_id)
    if i < 0:
        return []
    fim = camada.find('failClosed:', i)
    return re.findall(r"FIELD\('([^']+)'", camada[i:fim])


def valor_do_campo(camada, receptor_id, campo):
    i = camada.find("id: '%s'" % receptor_id)
    if i < 0:
        return None
    fim = camada.find('failClosed:', i)
    m = re.search(r"FIELD\('%s', ([^,]+)," % re.escape(campo), camada[i:fim])
    return m.group(1).strip() if m else None


def medir(caminho=CASCO12):
    markup, camada, ativos = abrir(caminho)
    telas = fatiar(markup)
    decl = receptores(camada)
    por_hose = {}
    for r in decl:
        if r['PARENT_HOSE_ID'] is None:
            por_hose[r['HOSE_ID']] = r
    por_id = {r['RECEPTOR_ID']: r for r in decl}

    # ── 1 · uma mangueira por receptor, com payload canonico ──
    vereditos = {}
    for h in VOCABULARIO_HOSE:
        r = por_hose.get(h)
        if r is None:
            vereditos[h] = {'VERDICT': 'FAIL', 'MISSING': ['nenhum receptor com HOSE_ID = %s' % h]}
            continue
        falta = [c for c in ('RECEPTOR_ID', 'CANONICAL_PAYLOAD_TYPE', 'LOAD_STATE',
                             'NO_DATA_REASON') if not r.get(c)]
        declarados = [p.strip() for p in r['CANONICAL_PAYLOAD_TYPE'].split('|')]
        if sorted(declarados) != sorted(PAYLOAD_CANONICO[h]):
            falta.append('payload declarado %s != canonico %s'
                         % (declarados, PAYLOAD_CANONICO[h]))
        if r['LOAD_STATE'] not in OITO_ESTADOS:
            falta.append('LOAD_STATE fora do vocabulario: %s' % r['LOAD_STATE'])
        vereditos[h] = {'VERDICT': 'FAIL' if falta else 'PASS', 'MISSING': falta,
                        'RECEPTOR_ID': r['RECEPTOR_ID'],
                        'CANONICAL_PAYLOAD_TYPE': r['CANONICAL_PAYLOAD_TYPE']}

    # ── 2 · o helper: hoseId sai de displayLabel? ──
    helper = re.search(r'const receptor = \(r\) => \(\{(.*?)\n    \}\);', camada, re.S)
    helper_txt = helper.group(1) if helper else ''
    hose_id_do_display = bool(re.search(r'hoseId:\s*r\.displayLabel\s*\|\|\s*r\.hose', helper_txt))
    parent_estrutural = 'parentHoseId' in helper_txt or 'parentHoseId' in markup
    parent_no_note = "PARENT_HOSE_ID · ' + r.parent" in helper_txt

    # ── 3 · subreceptores ──
    sub = {}
    for rid, esperado in SUBRECEPTORES.items():
        r = por_id.get(rid)
        if r is None:
            sub[rid] = {'VERDICT': 'FAIL', 'MISSING': ['receptor ausente']}
            continue
        falta = []
        if r['HOSE_ID'] != esperado['HOSE']:
            falta.append('HOSE_ID = %s, esperado %s' % (r['HOSE_ID'], esperado['HOSE']))
        if r['PARENT_HOSE_ID'] != esperado['PARENT']:
            falta.append('PARENT_HOSE_ID = %s, esperado %s'
                         % (r['PARENT_HOSE_ID'], esperado['PARENT']))
        if r['CANONICAL_PAYLOAD_TYPE'] != esperado['PAYLOAD']:
            falta.append('payload = %s' % r['CANONICAL_PAYLOAD_TYPE'])
        if not parent_estrutural:
            falta.append('PARENT_HOSE_ID nao e campo estrutural do receptor: '
                         'e concatenado em note')
        if hose_id_do_display and r['DISPLAY_LABEL']:
            falta.append('hoseId exposto e o DISPLAY_LABEL "%s", nao o HOSE_ID canonico'
                         % r['DISPLAY_LABEL'])
        sub[rid] = {'VERDICT': 'FAIL' if falta else 'PASS', 'MISSING': falta,
                    'HOSE_ID': r['HOSE_ID'], 'PARENT_HOSE_ID': r['PARENT_HOSE_ID'],
                    'DISPLAY_LABEL': r['DISPLAY_LABEL'],
                    'CANONICAL_PAYLOAD_TYPE': r['CANONICAL_PAYLOAD_TYPE']}

    # ── 4 · handlers mortos ──
    i = camada.rindex('\n    return {')
    retorno = camada[i:]
    usados = set(re.findall(r'sc-camel-on-click="\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\}\}"', markup))
    mortos = sorted(h for h in usados
                    if not re.search(r'(^|[\s,{])' + h + r'\s*[:,\n]', retorno))

    # ── 5 · paridade radar / obj na convergencia ──
    CAMPOS_CONV = ('conv.propositionId', 'conv.kind', 'conv.state', 'conv.independentCount',
                   'l.family', 'l.dependency', 'l.dependencyNote', 'l.openEvidence')

    def presentes(tela):
        t = telas.get(tela, '')
        return [c for c in CAMPOS_CONV if ('{{ %s }}' % c) in t]
    conv_radar, conv_obj = presentes('radar'), presentes('obj')

    # ── 6 · gaveta ──
    ev = re.search(r"const EVIDENCE = \{(.*?)\n    \};", camada, re.S)
    entradas = re.findall(r"'(EV-\d+)': \{ hose: '([A-Z0-9]+)'", ev.group(1)) if ev else []
    hoses_gaveta = sorted({h for _, h in entradas})
    linguas_gaveta = sorted(set(re.findall(r"lang: '([A-Za-z_]+)'", ev.group(1)))) if ev else []

    # ── 7 · acao ──
    kind = re.search(r"const KIND = \{(.*?)\};", camada, re.S)
    kind_txt = kind.group(1) if kind else ''
    canonicos = re.findall(r"canonical: '([A-Z_]+)'", kind_txt)
    displays = re.findall(r"display: '([A-Z_]+)'", kind_txt)
    action_type_persistido = 'actionType: KIND[a.kind].canonical' in camada
    action_object_id = 'objectId: base.id' in camada
    guard_acao = ("a.kind === 'business' && (!a.basis || !a.basis.length)" in camada)

    # ── 8 · timeline ──
    tl_campos = [c for c in ('EVENT_ID', 'EVENT_TYPE', 'EVENT_AT', 'EVENT_AT_RESOLUTION',
                             'SOURCE_ID', 'OBSERVATION_ID', 'STATE_BEFORE', 'STATE_AFTER',
                             'GAP_REASON') if ("k: '%s'" % c) in camada]
    seta_concatenada = "' → '" in camada

    # ── 9 · SOURCE_LANGUAGE, regra global ──
    lingua = {}
    for rid in PAYLOAD_TEXTUAL:
        v = valor_do_campo(camada, rid, 'SOURCE_LANGUAGE')
        lingua[rid] = {'EXPRESSAO': v,
                       'CAI_EM_UNKNOWN': bool(v and 'unknown' in v.lower()),
                       'CAI_EM_TRACO': v == 'null'}

    # ── 10 · creator ──
    creator = {
        'FARM_BUSINESS_ENTITY_PRESENTE': 'FARM_BUSINESS_ENTITY' in camada,
        'CREATOR_CONTENT_PROFILE_PRESENTE': 'CREATOR_CONTENT_PROFILE' in camada,
        'ENTRY_PATH_VALORES': sorted(set(re.findall(
            r"'(FROM_ATTENTION_OBJECT|FROM_CROP_REGION_SEARCH)'", camada))),
    }

    # ── 11 · mapa ──
    mapa_js = next((t for t in ativos.values() if 'pointsjson' in t), '')
    mapa = {
        'GUARD_NO_ASSET': "p.GEO_RESOLUTION === 'POINT'" in mapa_js,
        'DECLARA_NAO_DESENHAVEIS': 'SEM GEO_RESOLUTION = POINT' in mapa_js,
        'RESOLUCOES_NOS_PONTOS': sorted(set(re.findall(r"GEO_RESOLUTION: '([A-Z_]+)'", camada))),
    }

    # ── 12 · proveniencia e segredo ──
    prov = {
        'GITHUB': bool(re.search(r"provGithub = \['SOURCE_BACKEND','REPOSITORY','PATH',"
                                 r"'COMMIT_SHA','HASH','SOURCE_ID','AS_OF_DATE'\]", camada)),
        'SUPABASE': bool(re.search(r"provSupabase = \['SOURCE_BACKEND','SCHEMA','TABLE_OR_VIEW',"
                                   r"'PRIMARY_KEY','SNAPSHOT_ID','CAPTURED_AT','SOURCE_ID',"
                                   r"'AS_OF_DATE'\]", camada)),
        'SEGREDOS': [t for t in ('SERVICE_ROLE_KEY', 'service_role', 'SUPABASE_KEY',
                                 'apikey', 'Bearer ') if t in markup or t in camada],
    }

    completos = sum(1 for v in vereditos.values() if v['VERDICT'] == 'PASS')
    sub_ok = sum(1 for v in sub.values() if v['VERDICT'] == 'PASS')

    return {
        'CASCO': {
            'PATH': os.path.relpath(caminho, RAIZ).replace('\\', '/'),
            'MARKUP_CHARS': len(markup), 'DATA_LAYER_CHARS': len(camada),
            'TELAS': sorted(telas), 'ASSETS_JS': len(ativos),
        },
        'RECEPTORES_DECLARADOS': decl,
        'VERDICTS': {
            'HOSES': vereditos,
            'HOSES_WITH_COMPLETE_RECEIVER': completos,
            'SUBRECEPTORES': sub,
            'SUBRECEPTORES_PASS': sub_ok,
            'HELPER_HOSE_ID_VEM_DO_DISPLAY_LABEL': hose_id_do_display,
            'PARENT_HOSE_ID_ESTRUTURAL': parent_estrutural,
            'PARENT_HOSE_ID_NO_NOTE': parent_no_note,
            'DEAD_HANDLERS': len(mortos),
            'RADAR_CONVERGENCE_PARITY': 'PASS' if conv_radar == conv_obj and conv_obj else 'FAIL',
            'EVIDENCE_DRAWER_HOSES_COVERED': len(hoses_gaveta),
            'ACTION_TYPE_CANONICAL': 'PASS' if (sorted(canonicos) == sorted(ACAO_CANONICA)
                                                and action_type_persistido) else 'FAIL',
            'ACTION_MAP_OBJECT_ID': 'PASS' if action_object_id else 'FAIL',
            'TIMELINE_STATES_SEPARATE': 'PASS' if ('STATE_BEFORE' in tl_campos
                                                   and 'STATE_AFTER' in tl_campos
                                                   and not seta_concatenada) else 'FAIL',
            'TIMELINE_SOURCE_ID_TYPED': 'PASS' if 'SOURCE_ID' in tl_campos else 'FAIL',
            'CREATOR_ENTITY_KIND_CANONICAL': 'PASS' if (
                creator['FARM_BUSINESS_ENTITY_PRESENTE']
                and creator['CREATOR_CONTENT_PROFILE_PRESENTE']) else 'FAIL',
            'SOURCE_LANGUAGE_UNKNOWN_GLOBAL': 'PASS' if all(
                v['CAI_EM_UNKNOWN'] for v in lingua.values()) else 'FAIL',
            'CROP_MAP_GUARD': 'PASS' if (mapa['GUARD_NO_ASSET']
                                         and mapa['RESOLUCOES_NOS_PONTOS'] == ['NOT_KNOWN']) else 'FAIL',
            'GITHUB_PROVENANCE': 'PASS' if prov['GITHUB'] else 'FAIL',
            'SUPABASE_PROVENANCE': 'PASS' if prov['SUPABASE'] else 'FAIL',
            'NO_FRONTEND_SECRET': 'PASS' if not prov['SEGREDOS'] else 'FAIL',
        },
        'HANDLERS_MORTOS': mortos,
        'CONVERGENCIA': {
            'RADAR': conv_radar, 'OBJ': conv_obj,
            'PERNAS': [{'SIGNAL_FAMILY': f, 'INDEPENDENCE_STATE': i2,
                        'DEPENDENCY_RELATION': d or 'INDEPENDENT_SOURCE'}
                       for f, i2, d in re.findall(
                           r"family: '([A-Z_]+)'.*?independence: '([A-Z]+)'"
                           r"(?:, dependency: '([A-Z_]+)'|, dependency: null)", camada, re.S)],
            'CONTAGEM_DERIVADA': "const independentCount = CONV_LEGS.filter" in camada,
        },
        'GAVETA': {'ENTRADAS': entradas, 'HOSES': hoses_gaveta, 'LINGUAS': linguas_gaveta,
                   'HANDLERS': sorted(set(re.findall(
                       r'sc-camel-on-click="\{\{\s*(drawer\.[a-zA-Z]+)\s*\}\}"', markup)))},
        'ACAO': {'CANONICOS': canonicos, 'DISPLAYS': displays,
                 'PERSISTE_CANONICO': action_type_persistido,
                 'OBJECT_ID': action_object_id, 'GUARD_EVIDENCE_BASIS': guard_acao},
        'TIMELINE': {'CAMPOS': tl_campos, 'SETA_CONCATENADA': seta_concatenada},
        'SOURCE_LANGUAGE': lingua,
        'CREATOR': creator,
        'MAPA': mapa,
        'PROVENIENCIA': prov,
        'LOAD_STATES': {'DECLARADOS': [e for e in OITO_ESTADOS if ('%s:' % e) in camada],
                        'EXERCIDOS': dict(Counter(re.findall(r"load: '([A-Z_]+)'", camada)))},
    }


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    m = medir()
    if '--sync' in sys.argv:
        with open(SAIDA, 'w', encoding='utf-8', newline='\n') as fh:
            json.dump(m, fh, ensure_ascii=False, indent=2)
            fh.write('\n')
        print('gravado em', os.path.relpath(SAIDA, RAIZ))
    print(json.dumps(m['VERDICTS'], ensure_ascii=False, indent=2))
