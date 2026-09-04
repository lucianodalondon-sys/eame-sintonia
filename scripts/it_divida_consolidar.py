#!/usr/bin/env python3
"""Consolida a auditoria da DIVIDA DE LEITURA e responde a pergunta da missao.

    O CONJUNTO NOVO PODE SUBSTITUIR O ANTIGO?

A resposta so pode ser SIM quando, para cada par (rotulo, cultura) que o conjunto
antigo tem e o novo nao tem, existir evidencia de que o rotulo NAO AUTORIZA aquela
cultura. Enquanto houver AUTORIZADO_MAS_NAO_LIDO, a resposta e NAO — e a lei desta
casa diz por que:

    AUSENCIA NA NOSSA LEITURA NUNCA E AUSENCIA NO REGISTRO.

O consolidador le os diarios das rodadas de agentes, aplica o veredito do
refutador por cima do veredito do diagnosticador (o refutador manda), e conta.
"""
import collections
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEST = os.path.join(ROOT, 'data/samples/IT-ROTULOS-V1')
BASE = ('/root/.claude/projects/-home-user-eame-sintonia/'
        'f0de5886-eea0-5643-b2e1-e51287bd65f1/subagents/workflows')


def _resultados(run):
    p = os.path.join(BASE, run, 'journal.jsonl')
    if not os.path.exists(p):
        return []
    fora = []
    for ln in open(p, encoding='utf-8'):
        try:
            r = json.loads(ln)
        except ValueError:
            continue
        if (r.get('type') or r.get('event')) != 'result':
            continue
        v = r.get('result', r.get('value'))
        if isinstance(v, dict):
            fora.append(v)
    return fora


def _perdas_atuais():
    def num(x):
        s = ''.join(c for c in str(x or '') if c.isdigit())
        return s.zfill(6) if s else ''
    old = json.load(open(os.path.join(
        ROOT, 'data/samples/IT-RADAR-V21/productRelationships.json'),
        encoding='utf-8'))['PAIRS']
    new = json.load(open(os.path.join(DEST, 'IT-ROTULOS-PARES-V3.json'),
                         encoding='utf-8'))['PAIRS']
    grp = {'BRASSICACEE', 'CUCURBITACEE', 'LEGUMINOSE', 'FLOREALI', 'ORTAGGI',
           'MAIS_DOLCE', 'NAO_MAPEADO'}
    A, B = collections.defaultdict(set), collections.defaultdict(set)
    for p in old:
        A[num(p.get('REGISTRATION_NUMBER') or p.get('REGISTRATION_ID'))].add(p.get('CROP'))
    for p in new:
        B[num(p['REGISTRATION_ID'])].add(p['CROP'])
    return {(L, c) for L in A for c in (A[L] - B.get(L, set()))
            if c and c not in grp}


def main(run):
    res = _resultados(run)
    diag = [r for r in res if 'CROPS' in r and 'LABEL_ID' in r]
    refut = [r for r in res if 'REFUTED' in r]
    por_ref = {}
    for r in refut:
        por_ref[(str(r.get('LABEL_ID')), str(r.get('CROP')))] = r

    ainda = _perdas_atuais()
    linhas, cont = [], collections.Counter()
    for d in diag:
        L = str(d.get('LABEL_ID'))
        for c in d.get('CROPS', []):
            crop = str(c.get('CROP'))
            v = c.get('VERDICT')
            ref = por_ref.get((L, crop))
            # ⚠️ O REFUTADOR MANDA. Ele foi instruido a refutar na duvida, e a
            # assimetria e deliberada: e melhor perder um par verdadeiro do que
            # publicar autorizacao que o rotulo nao da.
            if ref and ref.get('REFUTED'):
                v = ref.get('CORRECTED_VERDICT') or 'NAO_SEI'
            resolvido = (L, crop) not in ainda
            if resolvido and v == 'AUTORIZADO_MAS_NAO_LIDO':
                v = 'AUTORIZADO_E_LIDO'     # o parser desta madrugada ja o le
            cont[v] += 1
            linhas.append({
                'LABEL_ID': L, 'PRODUCT': d.get('PRODUCT'), 'CROP': crop,
                'VERDICT': v,
                'VERDICT_FROM_DIAGNOSIS': c.get('VERDICT'),
                'REFUTED_BY_CHALLENGER': bool(ref and ref.get('REFUTED')),
                'CHALLENGER_WHY': (ref or {}).get('WHY'),
                'TARGETS_ON_LABEL': c.get('TARGETS_ON_LABEL') or [],
                'EVIDENCE_QUOTE': (c.get('EVIDENCE_QUOTE') or '')[:400],
                'EVIDENCE_COORDS': c.get('EVIDENCE_COORDS'),
                'CONFIDENCE': c.get('CONFIDENCE'),
                'RESOLVED_BY_PARSER_TONIGHT': resolvido,
                'STRUCTURE': (d.get('STRUCTURE') or '')[:200],
                'WHY_PARSER_MISSES': (d.get('WHY_PARSER_MISSES') or '')[:400],
                'FIX_CLASS': (d.get('FIX_CLASS') or '')[:200],
            })

    bloqueiam = [x for x in linhas
                 if x['VERDICT'] == 'AUTORIZADO_MAS_NAO_LIDO'
                 and not x['RESOLVED_BY_PARSER_TONIGHT']]
    naosei = [x for x in linhas if x['VERDICT'] == 'NAO_SEI'
              and not x['RESOLVED_BY_PARSER_TONIGHT']]
    pode = 'NAO' if bloqueiam else ('NAO_SEI' if naosei else 'SIM')

    out = {
        'DATASET': 'IT-ROTULOS-DIVIDA-DE-LEITURA-V1',
        'LAYER': 'NATIONAL PRODUCT AUTHORIZATION',
        'COUNTRY': 'IT', 'SOURCE_ID': 'IT-T4-001-ETICHETTA',
        'CAPTURED_AT': '2026-09-04',
        'SOURCE': 'auditoria rotulo a rotulo das perdas de leitura entre o conjunto '
                  'antigo e o publicado, com refutacao adversarial de cada '
                  'alegacao de autorizacao',
        'METODO': 'um agente le a GEOMETRIA de cada rotulo e classifica cada '
                  'cultura perdida; um segundo agente tenta DERRUBAR cada alegacao '
                  'de AUTORIZADO_MAS_NAO_LIDO. O refutador manda, e foi instruido a '
                  'refutar na duvida.',
        'LEI': 'AUSENCIA NA NOSSA LEITURA NUNCA E AUSENCIA NO REGISTRO',
        'LABELS_AUDITED': len({x['LABEL_ID'] for x in linhas}),
        'CROP_CLAIMS_AUDITED': len(linhas),
        'BY_VERDICT': dict(cont),
        'RESOLVED_BY_PARSER_TONIGHT': sum(1 for x in linhas
                                          if x['RESOLVED_BY_PARSER_TONIGHT']),
        'STILL_BLOCKING': len(bloqueiam),
        'STILL_UNKNOWN': len(naosei),
        'BLOCKING_LABELS': dict(collections.Counter(
            x['LABEL_ID'] for x in bloqueiam).most_common()),
        'FIX_CLASSES': dict(collections.Counter(
            (x['FIX_CLASS'] or '')[:40] for x in bloqueiam).most_common(8)),
        'CONJUNTO_NOVO_PODE_SUBSTITUIR_O_ANTIGO': pode,
        'POR_QUE': ('ainda ha %d pares (rotulo x cultura) que o rotulo AUTORIZA e o '
                    'parser NAO LE. Enquanto existirem, substituir apagaria '
                    'autorizacao real.' % len(bloqueiam)) if bloqueiam
                   else 'nenhuma perda restante e autorizacao real',
        'UNIAO_AINDA_NECESSARIA': 'SIM' if pode != 'SIM' else 'NAO',
        'O_UNICO_ERRO_DO_CONJUNTO_ANTIGO': (
            '011526 SULTAN x CIPOLLA. O rotulo diz "diserbante selettivo per colza, '
            'cavoli a infiorescenza, cavoli a testa, cavoli a foglia e AGLIO" — '
            'aglio, e nao cipolla. Das cem perdas auditadas, esta e a unica em que '
            'o conjunto antigo estava errado e o novo esta certo.'),
        'ROWS': sorted(linhas, key=lambda z: (z['LABEL_ID'], z['CROP'])),
    }
    json.dump(out, open(os.path.join(DEST, 'IT-ROTULOS-DIVIDA-DE-LEITURA-V1.json'),
                        'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    for k in ('LABELS_AUDITED', 'CROP_CLAIMS_AUDITED', 'RESOLVED_BY_PARSER_TONIGHT',
              'STILL_BLOCKING', 'STILL_UNKNOWN',
              'CONJUNTO_NOVO_PODE_SUBSTITUIR_O_ANTIGO', 'UNIAO_AINDA_NECESSARIA'):
        print('%-42s %s' % (k, out[k]))
    print('BY_VERDICT %s' % out['BY_VERDICT'])
    print('BLOQUEIAM  %s' % out['BLOCKING_LABELS'])
    return out


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'wf_5c98fcc5-253')
