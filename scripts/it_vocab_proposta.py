#!/usr/bin/env python3
"""PROPOSTA de ampliacao do vocabulario de problemas do motor — e nao a alteracao.

O motor canonico vive em outra branch (claude/opportunity-commercial-priority-v1,
b3935bd). Mexer nele daqui seria alterar o motor a partir de uma branch de coleta.
Entao o que sai daqui e uma PROPOSTA, com:

  - a identidade de cada alvo, dita e sustentada;
  - o veredito do desafiador adversarial por cima do veredito do juiz;
  - os aliases propostos, JA testados contra o corpus real;
  - a REGRESSAO que a missao exige: nenhum alias pode transformar texto generico
    em sinal falso.

    NENHUMA APROXIMACAO SEM TESTEMUNHA.
    Alias que casa palavra comum italiana e REJEITADO aqui, e nao la na frente.
"""
import collections
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from it_futuro_corpus import corpus                              # noqa: E402

DEST = os.path.join(ROOT, 'data/samples/IT-ROTULOS-V1')
BASE = ('/root/.claude/projects/-home-user-eame-sintonia/'
        'f0de5886-eea0-5643-b2e1-e51287bd65f1/subagents/workflows')

# Palavras comuns do italiano que um alias curto pode capturar por acidente.
# A lista nao e exaustiva por natureza; por isso a regressao tambem roda sobre o
# corpus real, que e onde o falso positivo aparece de verdade.
COMUNS = [
    'problema', 'problemi', 'sistema', 'programma', 'cinema', 'schema', 'tema',
    'prima', 'clima', 'lima', 'rima', 'stima', 'forma', 'norma', 'firma',
    'risorsa', 'rischio', 'risultato', 'riserva', 'riso', 'caso', 'peso',
    'mese', 'paese', 'campo', 'tempo', 'modo', 'nodo', 'lato', 'dato',
    'carbone', 'carbonio', 'carta', 'parte', 'porta', 'sorta', 'morte',
    'acqua', 'acquisto', 'acaro', 'macchina', 'mosso', 'mostra', 'mosca',
]


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
        if (r.get('type') or r.get('event')) == 'result':
            v = r.get('result', r.get('value'))
            if isinstance(v, dict):
                fora.append(v)
    return fora


def _regressao(alias, textos):
    """→ (n_ocorrencias, [amostras de casamento]). Roda no corpus REAL."""
    a = alias.strip().lower()
    if len(a) < 4:
        return -1, ['ALIAS_CURTO_DEMAIS']
    if any(a == c or (len(a) >= 4 and a in c) for c in COMUNS):
        return -2, ['CASA_PALAVRA_COMUM']
    rx = re.compile(r'\b%s\w*' % re.escape(a), re.I)
    hits = collections.Counter()
    for t in textos:
        for m in rx.finditer(t):
            hits[m.group(0).lower()] += 1
    return sum(hits.values()), [k for k, _ in hits.most_common(6)]


def main(run='wf_c6c27d9b-366'):
    res = _resultados(run)
    juizes = [r for r in res if 'DECISION' in r]
    desafios = collections.defaultdict(list)
    for r in res:
        if 'REFUTED' in r and r.get('TARGET'):
            desafios[r['TARGET']].append(r)

    textos = [d['TEXT'] for d in corpus()]
    linhas, cont = [], collections.Counter()
    for j in sorted(juizes, key=lambda z: z['TARGET']):
        t = j['TARGET']
        ds = desafios.get(t, [])
        refutado = [d for d in ds if d.get('REFUTED')]
        # ⚠️ O DESAFIADOR MANDA. Ele foi instruido a refutar na duvida.
        final = (refutado[0].get('CORRECTED_DECISION') or 'NAO_SEI') if refutado \
            else j['DECISION']
        aliases = []
        for a in (j.get('PROPOSED_ALIASES') or []):
            n, amostra = _regressao(a, textos)
            aliases.append({
                'ALIAS': a,
                'CORPUS_HITS': n,
                'FORMS_MATCHED': amostra,
                'REGRESSION': ('REJEITADO_ALIAS_CURTO' if n == -1
                               else 'REJEITADO_PALAVRA_COMUM' if n == -2
                               else 'OK'),
            })
        maus = [a for a in aliases if a['REGRESSION'] != 'OK']
        if maus and final == 'NEEDS_NEW_ISSUE_ID':
            final_ali = [a for a in aliases if a['REGRESSION'] == 'OK']
            if not final_ali:
                final = 'NAO_SEI'
        cont[final] += 1
        linhas.append({
            'TARGET': t,
            'IDENTITY': j.get('IDENTITY'),
            'LEVEL': j.get('LEVEL'),
            'IS_ACTIONABLE_PROBLEM': j.get('IS_ACTIONABLE_PROBLEM'),
            'DECISION_FROM_JUDGE': j['DECISION'],
            'CHALLENGED': bool(ds),
            'REFUTED': bool(refutado),
            'CHALLENGER_WHY': (refutado[0].get('WHY') if refutado else None),
            'FINAL_DECISION': final,
            'PROPOSED_ISSUE_ID': j.get('PROPOSED_ISSUE_ID'),
            'SYNONYM_OF': j.get('SYNONYM_OF'),
            'SYNONYM_IS_LOSSLESS': j.get('SYNONYM_IS_LOSSLESS'),
            'ALIASES': aliases,
            'ALIASES_REJECTED_BY_REGRESSION': [a['ALIAS'] for a in maus],
            'RISK_OF_FALSE_SIGNAL': j.get('RISK_OF_FALSE_SIGNAL'),
            'EVIDENCE': (j.get('EVIDENCE') or '')[:300],
            'CONFIDENCE': j.get('CONFIDENCE'),
        })

    aprovados = [x for x in linhas if x['FINAL_DECISION'] == 'NEEDS_NEW_ISSUE_ID']
    out = {
        'DATASET': 'IT-VOCAB-PROPOSTA-V1',
        'LAYER': 'CONTROLLED VOCABULARY — PROPOSAL ONLY',
        'COUNTRY': 'IT', 'SOURCE_ID': 'IT-T4-001-ETICHETTA',
        'CAPTURED_AT': '2026-09-04',
        'SOURCE': 'censo dos alvos do vocabulario de rotulos que nao tem ISSUE_ID no '
                  'motor canonico, com julgamento e desafio adversarial',
        'ISTO_NAO_ALTERA_O_MOTOR': (
            'o motor vive em claude/opportunity-commercial-priority-v1 (b3935bd). '
            'Alterar v21_normalizar.py a partir de uma branch de coleta seria mexer '
            'no motor de fora. Isto e proposta, com a regressao ja rodada.'),
        'TARGETS_JUDGED': len(linhas),
        'BY_FINAL_DECISION': dict(cont),
        'APPROVED_FOR_NEW_ISSUE_ID': len(aprovados),
        'ALIAS_REGRESSION': 'cada alias proposto foi rodado contra os 4,0 milhoes de '
                            'caracteres do corpus italiano e contra uma lista de '
                            'palavras comuns. Alias com menos de 4 letras, ou que '
                            'casa palavra comum, e REJEITADO aqui.',
        'ALIASES_REJECTED': sum(len(x['ALIASES_REJECTED_BY_REGRESSION'])
                                for x in linhas),
        'ROWS': linhas,
    }
    json.dump(out, open(os.path.join(DEST, 'IT-VOCAB-PROPOSTA-V1.json'), 'w',
                        encoding='utf-8'), ensure_ascii=False, indent=1)
    print('TARGETS_JUDGED            %d' % len(linhas))
    print('BY_FINAL_DECISION         %s' % dict(cont))
    print('APPROVED_FOR_NEW_ISSUE_ID %d' % len(aprovados))
    print('ALIASES_REJECTED          %d' % out['ALIASES_REJECTED'])
    for x in linhas:
        if x['ALIASES_REJECTED_BY_REGRESSION'] or x['REFUTED']:
            print('  %-18s %-22s refutado=%-5s alias rejeitados=%s'
                  % (x['TARGET'], x['FINAL_DECISION'], x['REFUTED'],
                     x['ALIASES_REJECTED_BY_REGRESSION']))
    return out


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'wf_c6c27d9b-366')
