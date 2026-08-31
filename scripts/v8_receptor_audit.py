"""Auditoria de recepcao do casco V8.

Deriva todos os numeros dos artefatos e do proprio casco. Nada e digitado a mao:
se um numero aparece num documento, ele saiu daqui.

Uso:
    py scripts/v8_receptor_audit.py            # imprime a medicao
    py scripts/v8_receptor_audit.py --sync     # regrava os blocos SUMMARY
"""
import json
import os
import re
import sys
from collections import Counter

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CASCO = os.path.join(RAIZ, 'casco', 'canonical', 'SINTONIA-EAME-V8-RECEPTOR-CANDIDATE.html')
MATRIZ = os.path.join(RAIZ, 'data', 'implementation', 'V8-RECEPTOR-MATRIX.json')
COMPONENTES = os.path.join(RAIZ, 'data', 'implementation', 'V8-COMPONENT-DATA-CONTRACTS.json')
ORFAOS = os.path.join(RAIZ, 'data', 'implementation', 'ORPHAN-INTELLIGENCE-OUTPUTS.json')


def carregar(caminho):
    with open(caminho, encoding='utf-8') as fh:
        return json.load(fh)


def gravar(caminho, dados):
    with open(caminho, 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(dados, fh, ensure_ascii=False, indent=2)
        fh.write('\n')


# ── o casco ────────────────────────────────────────────────────────────────

def desempacotar_casco(caminho=CASCO):
    """Devolve (markup_sem_estilo, camada_de_dados) do bundle do Claude Design.

    O bundle guarda o documento como string JSON dentro de <script
    type="__bundler/template">. Dentro dele, a logica vive num <script
    data-dc-script>.
    """
    with open(caminho, encoding='utf-8', errors='replace') as fh:
        bruto = fh.read()
    achado = re.search(r'<script type="__bundler/template">(.*?)</script>', bruto, re.S)
    if not achado:
        raise ValueError('template do bundler nao encontrado em %s' % caminho)
    documento = json.loads(achado.group(1).strip())
    scripts = re.findall(r'<script[^>]*data-dc-script[^>]*>(.*?)</script>', documento, re.S)
    camada = scripts[0] if scripts else ''
    markup = re.sub(r'<style[^>]*>.*?</style>', '', documento, flags=re.S)
    return markup, camada


def chaves_expostas(camada):
    """Chaves que renderVals() devolve ao markup — a superficie de recepcao."""
    bloco = re.search(r'return \{(.*?)\n    \};', camada, re.S)
    if not bloco:
        return set()
    chaves = set()
    for linha in bloco.group(1).split('\n'):
        linha = re.sub(r'//.*$', '', linha)
        for parte in linha.split(','):
            parte = parte.strip()
            achado = re.match(r'^([a-zA-Z_][a-zA-Z0-9_]*)\s*(?::|$)', parte)
            if achado:
                chaves.add(achado.group(1))
    return chaves


def telas(markup):
    return sorted(set(re.findall(r'sc-if\s+value="\{\{\s*at\.([a-z]+)\s*\}\}"', markup)))


def fatiar_por_tela(markup):
    """Devolve {tela: markup da tela}.

    Cuidado que custou um teste: `at.radar` aparece duas vezes — uma no item do
    menu lateral, outra no bloco da tela. Fatiar pela PRIMEIRA ocorrencia entrega
    o botao do menu, nao a tela. Aqui todas as ocorrencias entram, concatenadas.
    """
    aberturas = [(m.start(), m.group(1)) for m in
                 re.finditer(r'sc-if\s+value="\{\{\s*at\.([a-z]+)\s*\}\}"', markup)]
    fatias = {}
    for i, (pos, nome) in enumerate(aberturas):
        fim = aberturas[i + 1][0] if i + 1 < len(aberturas) else len(markup)
        fatias.setdefault(nome, []).append(markup[pos:fim])
    return {k: ''.join(v) for k, v in fatias.items()}


def handlers(markup):
    return Counter(re.findall(r'sc-camel-on-click="\{\{\s*([^}]+?)\s*\}\}"', markup))


# ── a medicao ──────────────────────────────────────────────────────────────

def medir():
    markup, camada = desempacotar_casco()
    expostas = chaves_expostas(camada)
    matriz = carregar(MATRIZ)
    componentes = carregar(COMPONENTES)
    orfaos = carregar(ORFAOS)

    receptores = matriz['RECEPTORS'] + matriz['SUBRECEPTORS']
    estados = Counter(r['CASCO_MEASURED']['STATE'] for r in receptores)

    # uma mangueira so tem receptor COMPLETO se o estado medido for COMPLETE
    completos = [r['HOSE_ID'] for r in matriz['RECEPTORS']
                 if r['CASCO_MEASURED']['STATE'] == 'COMPLETE']

    classes = Counter(o['CLASS'] for o in orfaos['OUTPUTS'])
    ausentes = [o for o in orfaos['OUTPUTS']
                if str(o.get('CASCO_RECEPTOR_STATE', '')).startswith('ABSENT')]

    comp_estados = Counter(c['CASCO_MEASURED']['STATE'] for c in componentes['COMPONENTS'])

    return {
        'CASCO': {
            'TELAS': telas(markup),
            'CHAVES_EXPOSTAS': len(expostas),
            'HANDLERS_DISTINTOS': len(handlers(markup)),
            'MARKUP_CHARS': len(markup),
            'CAMADA_DADOS_CHARS': len(camada),
        },
        'RECEPTORES': {
            'DECLARADOS': len(matriz['RECEPTORS']),
            'SUBRECEPTORES_DECLARADOS': len(matriz['SUBRECEPTORS']),
            'ESTADOS_NO_CASCO': dict(estados),
            'HOSES_WITH_COMPLETE_RECEIVER': len(completos),
            'HOSES_TOTAL': len(matriz['RECEPTORS']),
        },
        'COMPONENTES': {
            'AUDITADOS': len(componentes['COMPONENTS']),
            'ESTADOS_NO_CASCO': dict(comp_estados),
        },
        'ORFAOS': {
            'INVENTARIADAS': len(orfaos['OUTPUTS']),
            'CLASSES': dict(classes),
            'ORPHAN_CANONICAL_INTELLIGENCE_OUTPUTS': classes.get('ORPHAN_INTELLIGENCE_OUTPUT', 0),
            'RECEPTOR_AUSENTE_NO_CASCO': len(ausentes),
        },
        'EXPOSTAS': sorted(expostas),
    }


def sincronizar(m):
    matriz = carregar(MATRIZ)
    matriz['SUMMARY'] = {
        'RECEPTORS_DECLARED': m['RECEPTORES']['DECLARADOS'],
        'SUBRECEPTORS_DECLARED': m['RECEPTORES']['SUBRECEPTORES_DECLARADOS'],
        'CASCO_STATE_COUNTS': m['RECEPTORES']['ESTADOS_NO_CASCO'],
        'HOSES_WITH_COMPLETE_RECEIVER_IN_CASCO': m['RECEPTORES']['HOSES_WITH_COMPLETE_RECEIVER'],
        'NOTE': matriz['SUMMARY']['NOTE'],
    }
    gravar(MATRIZ, matriz)

    componentes = carregar(COMPONENTES)
    componentes['SUMMARY'] = {
        'COMPONENTS_AUDITED': m['COMPONENTES']['AUDITADOS'],
        'COMPONENTS_WITH_COMPLETE_CONTRACT_IN_CASCO': m['COMPONENTES']['ESTADOS_NO_CASCO'].get('COMPLETE', 0),
        'COMPONENTS_WITH_CORRECT_SEMANTICS_IN_CASCO': componentes['SUMMARY']['COMPONENTS_WITH_CORRECT_SEMANTICS_IN_CASCO'],
        'NOTE': componentes['SUMMARY']['NOTE'],
    }
    gravar(COMPONENTES, componentes)

    orfaos = carregar(ORFAOS)
    orfaos['SUMMARY'] = {
        'OUTPUTS_INVENTORIED': m['ORFAOS']['INVENTARIADAS'],
        'ORPHAN_CANONICAL_INTELLIGENCE_OUTPUTS': m['ORFAOS']['ORPHAN_CANONICAL_INTELLIGENCE_OUTPUTS'],
        'OUTPUTS_WHOSE_RECEPTOR_IS_ABSENT_IN_THE_CASCO': m['ORFAOS']['RECEPTOR_AUSENTE_NO_CASCO'],
        'CLASS_COUNTS': m['ORFAOS']['CLASSES'],
    }
    orfaos['TWO_DIFFERENT_NUMBERS']['ORPHAN_CANONICAL_INTELLIGENCE_OUTPUTS'] = \
        m['ORFAOS']['ORPHAN_CANONICAL_INTELLIGENCE_OUTPUTS']
    orfaos['TWO_DIFFERENT_NUMBERS']['OUTPUTS_WHOSE_RECEPTOR_IS_ABSENT_IN_THE_CASCO'] = \
        m['ORFAOS']['RECEPTOR_AUSENTE_NO_CASCO']
    gravar(ORFAOS, orfaos)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    medida = medir()
    if '--sync' in sys.argv:
        sincronizar(medida)
        print('SUMMARY regravado nos tres artefatos.')
    medida.pop('EXPOSTAS')
    print(json.dumps(medida, ensure_ascii=False, indent=2))
