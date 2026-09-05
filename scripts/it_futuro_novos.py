#!/usr/bin/env python3
"""Consolida os sinais futuros propostos a partir dos documentos nunca lidos.

So entra o que a REGUA aprovou. A regua e a mesma que cortou 3.035 candidatos a
dez sinais, e ela e aplicada por um agente DIFERENTE do que propos — quem propoe
nao se aprova.

O teste que mais derruba e o primeiro: A CITACAO EXISTE NO DOCUMENTO DECLARADO?
Nesta rodada ele sozinho reprovou cinco sinais de um mesmo leitor, que atribuiu a
um documento frases que estavam em outro. Sem esse teste, cinco proveniencias
falsas teriam entrado no radar com aparencia perfeita.
"""
import collections
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEST = os.path.join(ROOT, 'data/samples/IT-FUTURO-V1')
BASE = ('/root/.claude/projects/-home-user-eame-sintonia/'
        'f0de5886-eea0-5643-b2e1-e51287bd65f1/subagents/workflows')


def _res(run):
    p = os.path.join(BASE, run, 'journal.jsonl')
    fora = []
    if not os.path.exists(p):
        return fora
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


def main(run='wf_7451c864-4da'):
    os.makedirs(DEST, exist_ok=True)
    res = _res(run)
    props = [x for x in res if 'SIGNALS' in x]
    regua = [x for x in res if 'PASSES' in x]

    # casa veredito com sinal pelo resumo — o julgador ecoa o sinal que julgou
    aprov, reprov = [], []
    for v in regua:
        (aprov if v['PASSES'] else reprov).append(v)

    por_doc = collections.defaultdict(lambda: {'propostos': 0, 'aprovados': 0})
    for p in props:
        por_doc[p['SOURCE_ID']]['propostos'] += len(p.get('SIGNALS') or [])
    for v in aprov:
        por_doc[v['SOURCE_ID']]['aprovados'] += 1

    sinais = []
    for p in props:
        ap = [v for v in aprov if v['SOURCE_ID'] == p['SOURCE_ID']]
        for v in ap:
            match = None
            for s in (p.get('SIGNALS') or []):
                blob = (s.get('FUTURE_SIGNAL') or '')[:60].lower()
                if blob and blob[:30] in (v.get('SIGNAL_SUMMARY') or '').lower():
                    match = s
                    break
            sinais.append({
                'SOURCE_ID': p['SOURCE_ID'],
                'SIGNAL_SUMMARY': v.get('SIGNAL_SUMMARY'),
                'EVIDENCE_TIME_STATE': (v.get('CORRECTED_TIME_STATE')
                                        or (match or {}).get('EVIDENCE_TIME_STATE')),
                'CROP': (match or {}).get('CROP'),
                'TARGET': (match or {}).get('TARGET'),
                'REGION': (match or {}).get('REGION'),
                'QUOTE_IT': ((match or {}).get('QUOTE_IT') or '')[:420],
                'TRIGGER': (match or {}).get('TRIGGER'),
                'INVALIDATION_TRIGGER': (match or {}).get('INVALIDATION_TRIGGER'),
                'CONFIDENCE': (match or {}).get('CONFIDENCE'),
                'ADAMA_PAIR_EXISTS': v.get('ADAMA_PAIR_EXISTS'),
                'ADAMA_LABELS': v.get('ADAMA_LABELS') or [],
                'RULED_BY': 'agente independente do que propos',
                'STATE': 'APPROVED_CANDIDATE_NOT_YET_HAND_WRITTEN',
            })

    out = {
        'DATASET': 'IT-FUTURO-NOVOS-CANDIDATOS-V1',
        'LAYER': 'FUTURE INTELLIGENCE — approved candidates',
        'COUNTRY': 'IT', 'SOURCE_ID': 'IT-FUTURO-V1', 'CAPTURED_AT': '2026-09-04',
        'SOURCE': 'sinais futuros lidos nos documentos do acervo que nunca tinham '
                  'sido lidos, e julgados por um agente diferente do que os propos',
        'A_REGUA': ['a citacao existe LITERALMENTE no documento declarado?',
                    'o estado do tempo e sustentado pelo paragrafo?',
                    'cultura e alvo saem do contexto da citacao?',
                    'existe gatilho de invalidacao?',
                    'nao e duplicata de um dos dez ja existentes?'],
        'DOCS_READ': len(props),
        'SIGNALS_PROPOSED': sum(len(x.get('SIGNALS') or []) for x in props),
        'SIGNALS_RULED': len(regua),
        'SIGNALS_APPROVED': len(aprov),
        'SIGNALS_REJECTED': len(reprov),
        'REJECTION_REASONS': dict(collections.Counter(v['FAIL_REASON']
                                                      for v in reprov)),
        'O_TESTE_QUE_MAIS_DERRUBA': (
            'QUOTE_NOT_IN_DOCUMENT. Um mesmo leitor atribuiu a um documento cinco '
            'frases que estavam em OUTRO. Sem esse teste, cinco proveniencias '
            'falsas teriam entrado no radar com aparencia perfeita. E a razao de '
            'quem propoe nunca se aprovar.'),
        'BY_DOCUMENT': {k: v for k, v in sorted(por_doc.items())},
        'STATE': 'CANDIDATOS APROVADOS PELA REGUA, ainda NAO promovidos a sinal do '
                 'radar: promover exige a ficha completa (janela, mapa de acao por '
                 'departamento, portfolio), que se escreve a mao.',
        'APPROVED': sinais,
        'REJECTED': [{'SOURCE_ID': v['SOURCE_ID'], 'REASON': v['FAIL_REASON'],
                      'WHY': (v.get('WHY') or '')[:300],
                      'SIGNAL': (v.get('SIGNAL_SUMMARY') or '')[:200]}
                     for v in reprov],
    }
    json.dump(out, open(os.path.join(DEST, 'IT-FUTURO-NOVOS-CANDIDATOS-V1.json'),
                        'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    for k in ('DOCS_READ', 'SIGNALS_PROPOSED', 'SIGNALS_RULED', 'SIGNALS_APPROVED',
              'SIGNALS_REJECTED'):
        print('%-24s %s' % (k, out[k]))
    print('REJECTION_REASONS        %s' % out['REJECTION_REASONS'])
    return out


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'wf_7451c864-4da')
