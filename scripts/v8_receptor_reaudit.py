"""Reauditoria de recepcao contra o casco DATA-READY (index 11).

Mede o casco novo e emite data/implementation/V8-RECEPTOR-REAUDIT.json.
Nenhum numero e digitado: tudo sai da leitura dos bytes.

O casco anterior (index 10) continua versionado e continua sendo medido pelas
provas antigas — ele e a testemunha do "antes".

Uso:
    py scripts/v8_receptor_reaudit.py            # imprime
    py scripts/v8_receptor_reaudit.py --sync     # grava o artefato
"""
import base64
import gzip
import json
import os
import re
import sys
from collections import Counter

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CASCO11 = os.path.join(RAIZ, 'casco', 'canonical', 'SINTONIA-EAME-V8-DATA-READY.html')
SAIDA = os.path.join(RAIZ, 'data', 'implementation', 'V8-RECEPTOR-REAUDIT.json')

# ── nomes canonicos, do FINAL-HOSE-MAP. Nao se negocia por semelhanca. ──
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

ENVELOPE = ('receptorId', 'hoseId', 'payloadType', 'loadState', 'reasonKey',
            'prov', 'pointers', 'asOf', 'failClosed')

OITO_ESTADOS = ('UNWIRED', 'LOADING', 'READY', 'EMPTY_VALID',
                'NOT_STARTED', 'NOT_AVAILABLE', 'BLOCKED', 'ERROR_FAIL_CLOSED')

ACAO_CANONICA = ('BUSINESS_DECISION', 'SYSTEM_DECISION', 'INVESTIGATION')


# ── leitura do bundle ──────────────────────────────────────────────────────

def abrir(caminho=CASCO11):
    """(markup sem codigo e sem estilo, camada de dados, assets js)."""
    with open(caminho, encoding='utf-8', errors='replace') as fh:
        bruto = fh.read()
    documento = json.loads(
        re.search(r'<script type="__bundler/template">(.*?)</script>', bruto, re.S).group(1).strip())
    scripts = re.findall(r'<script[^>]*data-dc-script[^>]*>(.*?)</script>', documento, re.S)
    camada = scripts[0] if scripts else ''
    # o markup precisa sair SEM a camada de dados: o HTML embute o proprio codigo,
    # e contar um nome dentro do codigo-fonte e confundir mencao com renderizacao.
    markup = re.sub(r'<script[^>]*data-dc-script[^>]*>.*?</script>', '', documento, flags=re.S)
    markup = re.sub(r'<style[^>]*>.*?</style>', '', markup, flags=re.S)
    ativos = {}
    manifesto = re.search(r'<script type="__bundler/manifest">(.*?)</script>', bruto, re.S)
    if manifesto:
        for chave, item in json.loads(manifesto.group(1).strip()).items():
            if 'javascript' not in item.get('mime', ''):
                continue
            dados = base64.b64decode(item['data'])
            if item.get('compressed'):
                dados = gzip.decompress(dados)
            ativos[chave] = dados.decode('utf-8', 'replace')
    return markup, camada, ativos


def fatiar(markup):
    """{tela: markup}. Todas as ocorrencias de at.<tela>, nao so a primeira."""
    aberturas = [(m.start(), m.group(1)) for m in
                 re.finditer(r'sc-if\s+value="\{\{\s*at\.([a-z]+)\s*\}\}"', markup)]
    fatias = {}
    for i, (pos, nome) in enumerate(aberturas):
        fim = aberturas[i + 1][0] if i + 1 < len(aberturas) else len(markup)
        fatias.setdefault(nome, []).append(markup[pos:fim])
    return {k: ''.join(v) for k, v in fatias.items()}


def receptores(camada):
    """Receptores declarados via receptor({...}) na camada de dados."""
    achados = []
    for m in re.finditer(
            r"id: '([A-Z_0-9]+)', hose: '([^']+)'.*?payload: '[^·]*· ([^']+)'"
            r".*?load: '([A-Z_]+)'.*?reasonKey: '([^']*)'"
            r".*?pointers: ([^,]+),\s*failClosed: '([^']*)'", camada, re.S):
        achados.append({
            'RECEPTOR_ID': m.group(1), 'HOSE_ID': m.group(2),
            'CANONICAL_PAYLOAD_TYPE': m.group(3), 'LOAD_STATE': m.group(4),
            'NO_DATA_REASON': m.group(5), 'EVIDENCE_POINTERS': m.group(6).strip(),
            'FAIL_CLOSED_BEHAVIOR': m.group(7),
        })
    return achados


def campos_do_receptor(camada, receptor_id):
    """Nomes passados a FIELD(...) dentro do bloco daquele receptor."""
    i = camada.find("id: '%s'" % receptor_id)
    if i < 0:
        return []
    fim = camada.find('failClosed:', i)
    return re.findall(r"FIELD\('([^']+)'", camada[i:fim])


# ── a medicao ──────────────────────────────────────────────────────────────

def medir(caminho=CASCO11):
    markup, camada, ativos = abrir(caminho)
    telas = fatiar(markup)
    decl = receptores(camada)
    por_hose = {r['HOSE_ID']: r for r in decl}

    # 1 · uma mangueira so tem receptor se houver um receptor com HOSE_ID EXATO
    hoses_com_receptor = [h for h in VOCABULARIO_HOSE if h in por_hose]
    hoses_sem_receptor = [h for h in VOCABULARIO_HOSE if h not in por_hose]

    # 2 · deriva de nome canonico
    alias_map_existe = 'ADAPTER_ALIAS_MAP' in camada or 'ADAPTER_ALIAS_MAP' in markup
    drift_payload = []
    for h in VOCABULARIO_HOSE:
        r = por_hose.get(h)
        if not r:
            continue
        if r['CANONICAL_PAYLOAD_TYPE'] not in PAYLOAD_CANONICO[h]:
            drift_payload.append({
                'HOSE_ID': h, 'DECLARADO': r['CANONICAL_PAYLOAD_TYPE'],
                'CANONICO': PAYLOAD_CANONICO[h],
            })

    # 3 · HOSE_ID de subreceptor fora do vocabulario, sem PARENT_HOSE_ID
    parent_existe = 'PARENT_HOSE_ID' in camada or 'PARENT_HOSE_ID' in markup
    drift_hose = [{'RECEPTOR_ID': r['RECEPTOR_ID'], 'HOSE_ID': r['HOSE_ID']}
                  for r in decl if r['HOSE_ID'] not in VOCABULARIO_HOSE]

    # 4 · ACTION_TYPE persistido
    kind = re.search(r"const KIND = \{(.*?)\};", camada, re.S)
    acao_persistida = re.findall(r"t: '([A-Z_]+)'", kind.group(1)) if kind else []
    drift_acao = [v for v in acao_persistida if v not in ACAO_CANONICA]
    display_acao = 'DISPLAY_ACTION_TYPE' in camada

    # 5 · gaveta: quantas mangueiras alcanca
    mapa_ev = re.search(r"const EVIDENCE = \{(.*?)\n    \};", camada, re.S)
    hoses_gaveta = sorted(set(re.findall(r"hose: '(H\d)'", mapa_ev.group(1)))) if mapa_ev else []
    handlers_gaveta = sorted(set(re.findall(
        r'sc-camel-on-click="\{\{\s*(drawer\.[a-zA-Z]+)\s*\}\}"', markup)))

    # 6 · handlers mortos: usados no markup e ausentes do retorno de renderVals
    i = camada.rindex('\n    return {')
    retorno = camada[i:]
    usados = set(re.findall(r'sc-camel-on-click="\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\}\}"', markup))
    mortos = sorted(h for h in usados
                    if not re.search(r'(^|[\s,{])' + h + r'\s*[:,\n]', retorno))

    # 7 · o mesmo bloco em duas telas com conteudo diferente
    def conta(tela, chave):
        return telas.get(tela, '').count('{{ %s }}' % chave)
    conv_obj = [c for c in ('conv.propositionId', 'conv.kind', 'conv.independentCount',
                            'l.dependency', 'l.dependencyNote') if conta('obj', c)]
    conv_radar = [c for c in ('conv.propositionId', 'conv.kind', 'conv.independentCount',
                              'l.dependency', 'l.dependencyNote') if conta('radar', c)]

    # 8 · o guard do mapa vive no asset, nao no casco
    mapa_js = next((t for t in ativos.values() if 'pointsjson' in t), '')
    guard_mapa = "p.GEO_RESOLUTION === 'POINT'" in mapa_js
    declara_nao_desenhavel = 'SEM GEO_RESOLUTION = POINT' in mapa_js

    # 9 · convergencia executada
    pernas = re.findall(r"family: '([A-Z_]+)'.*?independence: '([A-Z]+)'"
                        r"(?:, dependency: '([A-Z_]+)'|, dependency: null)", camada, re.S)
    independentes = sum(1 for p in pernas if p[1] == 'INDEPENDENT')

    # 10 · vereditos, DERIVADOS. Nenhum PASS/FAIL e digitado.
    vereditos = {}
    for h in VOCABULARIO_HOSE:
        r = por_hose.get(h)
        if r is None:
            vereditos[h] = {'VERDICT': 'FAIL', 'MISSING': 'nenhum receptor com HOSE_ID = %s' % h}
            continue
        # o envelope e uma coisa; o nome canonico e outra. Somar os dois num unico
        # veredito esconderia que uma mangueira sem receptor nenhum (H6) e uma
        # mangueira completa com o nome errado estao a distancias muito diferentes.
        faltando_envelope = [c for c in ('RECEPTOR_ID', 'CANONICAL_PAYLOAD_TYPE', 'LOAD_STATE',
                                         'NO_DATA_REASON', 'FAIL_CLOSED_BEHAVIOR') if not r.get(c)]
        for campo, exigido in (('EVIDENCE_POINTERS', r.get('EVIDENCE_POINTERS')),):
            if exigido in (None, ''):
                faltando_envelope.append(campo)
        faltando = list(faltando_envelope)
        if r['CANONICAL_PAYLOAD_TYPE'] not in PAYLOAD_CANONICO[h] and not alias_map_existe:
            faltando.append('CANONICAL_PAYLOAD_TYPE canonico ou ADAPTER_ALIAS_MAP '
                            '(declarado: %s)' % r['CANONICAL_PAYLOAD_TYPE'])
        vereditos[h] = {
            'VERDICT': 'FAIL' if faltando else 'PASS',
            'ENVELOPE': 'COMPLETE' if not faltando_envelope else 'INCOMPLETE',
            'PAYLOAD_NAME': ('CANONICAL' if r['CANONICAL_PAYLOAD_TYPE'] in PAYLOAD_CANONICO[h]
                             else 'ALIAS_WITHOUT_MAP'),
            'MISSING': faltando,
        }

    sub = {}
    for rid, esperado in (('RECEPTOR_SCIENTIFIC_PUBLICATION', 'H7'),
                          ('RECEPTOR_LOCAL_ADAMA_PORTFOLIO', 'H2'),
                          ('RECEPTOR_FIELD_VOICE_OBSERVATION', 'H6')):
        r = next((x for x in decl if x['RECEPTOR_ID'] == rid), None)
        if r is None:
            sub[rid] = {'VERDICT': 'FAIL', 'MISSING': ['receptor ausente']}
            continue
        faltando = []
        if r['HOSE_ID'] not in VOCABULARIO_HOSE and not parent_existe:
            faltando.append('HOSE_ID fora de H1..H9 (%s) sem PARENT_HOSE_ID separado; '
                            'esperado PARENT_HOSE_ID = %s' % (r['HOSE_ID'], esperado))
        sub[rid] = {'VERDICT': 'FAIL' if faltando else 'PASS', 'MISSING': faltando,
                    'CANONICAL_PAYLOAD_TYPE': r['CANONICAL_PAYLOAD_TYPE']}

    return {
        'VERDICTS': {
            'HOSES': vereditos,
            'SUBRECEPTORES': sub,
            'HOSES_WITH_COMPLETE_RECEIVER': sum(1 for v in vereditos.values()
                                                if v['VERDICT'] == 'PASS'),
            'HOSES_WITH_COMPLETE_ENVELOPE': sum(1 for v in vereditos.values()
                                                if v.get('ENVELOPE') == 'COMPLETE'),
            'HOSES_WITH_CANONICAL_PAYLOAD_NAME': sum(1 for v in vereditos.values()
                                                     if v.get('PAYLOAD_NAME') == 'CANONICAL'),
            'NOTA_DAS_DUAS_MEDIDAS': ('Envelope e nome sao coisas diferentes. Uma mangueira sem '
                                      'receptor nenhum e uma mangueira completa com o nome errado '
                                      'nao estao a mesma distancia, e um unico numero esconderia isso.'),
            'CANONICAL_PAYLOAD_TYPE_DRIFT': 'FAIL' if (drift_payload and not alias_map_existe) else 'PASS',
            'SUBRECEPTOR_PARENT_HOSE_DRIFT': 'FAIL' if (drift_hose and not parent_existe) else 'PASS',
            'ACTION_TYPE_CANONICAL_DRIFT': 'FAIL' if (drift_acao and not display_acao) else 'PASS',
            'EVIDENCE_DRAWER_TRACES_ALL_HOSES': 'PASS' if len(hoses_gaveta) == 9 else 'FAIL',
            'DEAD_HANDLERS': 'FAIL' if mortos else 'PASS',
            'BLOCK_PARITY_RADAR_OBJ': 'PASS' if conv_radar == conv_obj else 'FAIL',
        },
        'CASCO': {
            'PATH': os.path.relpath(caminho, RAIZ).replace('\\', '/'),
            'MARKUP_CHARS': len(markup), 'DATA_LAYER_CHARS': len(camada),
            'TELAS': sorted(telas),
            'ASSETS_JS': len(ativos),
        },
        'RECEPTORES_DECLARADOS': decl,
        'HOSES': {
            'TOTAL': len(VOCABULARIO_HOSE),
            'COM_RECEPTOR': hoses_com_receptor,
            'SEM_RECEPTOR': hoses_sem_receptor,
            'HOSES_WITH_COMPLETE_RECEIVER': len(hoses_com_receptor),
        },
        'DRIFT': {
            'ADAPTER_ALIAS_MAP_EXISTE': alias_map_existe,
            'CANONICAL_PAYLOAD_TYPE_DRIFT': drift_payload,
            'PARENT_HOSE_ID_EXISTE': parent_existe,
            'SUBRECEPTOR_PARENT_HOSE_DRIFT': drift_hose,
            'ACTION_TYPE_PERSISTIDO': acao_persistida,
            'ACTION_TYPE_CANONICAL_DRIFT': drift_acao,
            'DISPLAY_ACTION_TYPE_EXISTE': display_acao,
        },
        'GAVETA': {
            'HOSES_ALCANCADAS': hoses_gaveta,
            'HANDLERS': handlers_gaveta,
        },
        'HANDLERS_MORTOS': mortos,
        'BLOCO_DIVERGENTE': {
            'CONVERGENCIA_NO_OBJ': conv_obj,
            'CONVERGENCIA_NO_RADAR': conv_radar,
        },
        'MAPA': {
            'GUARD_NO_ASSET': guard_mapa,
            'DECLARA_NAO_DESENHAVEIS': declara_nao_desenhavel,
        },
        'CONVERGENCIA': {
            'PERNAS': [{'SIGNAL_FAMILY': p[0], 'INDEPENDENCE_STATE': p[1],
                        'DEPENDENCY_RELATION': p[2] or 'INDEPENDENT_SOURCE'} for p in pernas],
            'INDEPENDENT_FAMILY_COUNT': independentes,
            'CONVERGENCE_STATE': 'MULTI_SIGNAL' if independentes >= 2 else 'SINGLE_SIGNAL',
        },
        'LOAD_STATES': {
            'DECLARADOS': [e for e in OITO_ESTADOS if ("%s:" % e) in camada],
            'EXERCIDOS': dict(Counter(re.findall(r"load: '([A-Z_]+)'", camada))),
        },
    }


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    m = medir()
    if '--sync' in sys.argv:
        with open(SAIDA, 'w', encoding='utf-8', newline='\n') as fh:
            json.dump(m, fh, ensure_ascii=False, indent=2)
            fh.write('\n')
        print('gravado em', os.path.relpath(SAIDA, RAIZ))
    print(json.dumps(m, ensure_ascii=False, indent=2))
