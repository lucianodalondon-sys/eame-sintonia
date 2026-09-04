#!/usr/bin/env python3
"""Serializa o Radar Futuro e mede o que ele TEM e o que lhe FALTA.

O censo existe por uma razao so: "sem informacao" nao pode ser caixa preta. Para
cada campo vazio o artefato diz a CAUSA, e a causa distingue as duas coisas que
importam — a informacao existe e o pipeline perdeu, ou a fonte realmente nao diz.
"""
import collections
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from it_futuro_corpus import candidatos, corpus                 # noqa: E402
from it_futuro_inteligencia import SINAIS                       # noqa: E402

DEST = os.path.join(ROOT, 'data/samples/IT-FUTURO-V1')

# Os nove elementos que o item 9 da missao exige para um item virar
# FUTURE_INTELLIGENCE. Nao e checklist decorativa: e o que decide COMPLETE.
ESSENCIAIS = [
    ('WHAT', 'FUTURE_SIGNAL'), ('WHERE', 'REGION'), ('CROP', 'CROP'),
    ('TARGET', 'TARGET'), ('WHEN', 'TIME_HORIZON_DAYS'), ('WHY', 'CONFIDENCE_WHY'),
    ('TRIGGER', 'TRIGGER'), ('ADAMA_RESPONSE', 'ADAMA_LOCAL_RESPONSE'),
    ('ACTION_TIMING', 'ACTION_MAP'),
]

VAZIO = {None, '', 'UNKNOWN', 'NOT_IN_SOURCE', 'NOT_COLLECTED',
         'NOT_APPLICABLE', 'NOT_EXTRACTED'}


def _tem(s, campo):
    v = s.get(campo)
    if isinstance(v, (list, dict)):
        return bool(v)
    return v not in VAZIO


def completude(s):
    faltam = [nome for nome, campo in ESSENCIAIS if not _tem(s, campo)]
    return faltam


def censo():
    docs = list(corpus())
    cands = list(candidatos())
    fortes = [c for c in cands if c['CROPS'] and c['ISSUES']]

    est = collections.Counter(s['FUTURE_INTELLIGENCE_STATE'] for s in SINAIS)
    hz = collections.Counter(s['HORIZON_BUCKET'] for s in SINAIS)
    tempo = collections.Counter(s['EVIDENCE_TIME_STATE'] for s in SINAIS)

    def com(campo):
        return sum(1 for s in SINAIS if _tem(s, campo))

    # acoes por departamento, contadas por ESTADO — nunca promovidas a ACT_NOW
    dept = collections.defaultdict(collections.Counter)
    for s in SINAIS:
        for d, a in (s.get('ACTION_MAP') or {}).items():
            dept[d][a['ACTION_STATE']] += 1

    # causa de campo vazio, agregada
    causas = collections.Counter()
    for s in SINAIS:
        for campo, causa in (s.get('MISSING_FIELDS') or {}).items():
            causas[causa.split(' —')[0].strip()] += 1

    ausentes = collections.Counter()
    for s in SINAIS:
        for nome, campo in ESSENCIAIS:
            if not _tem(s, campo):
                ausentes['MISSING_' + nome] += 1

    return {
        'DATASET': 'IT-FUTURO-RADAR-V1',
        'LAYER': 'FUTURE INTELLIGENCE',
        'COUNTRY': 'IT',
        'SOURCE_ID': 'IT-FUTURO-V1',
        'CAPTURED_AT': '2026-09-04',
        'SOURCE': 'sinais antecipatorios lidos a mao no acervo italiano versionado; '
                  'o varredor entregou candidatos, a classificacao saiu da leitura '
                  'do paragrafo',
        'LEI_DO_TEMPO': ['TENDENCIA nao vira PREVISAO',
                         'PREVISAO nao vira OCORRENCIA',
                         'EVENTO MARCADO nao significa RESULTADO CONHECIDO',
                         'PORTFOLIO RELATION nao vira LABEL AUTHORIZATION'],
        # ── censo (item 11) ────────────────────────────────────────────────
        'NEW_EVIDENCE_SCANNED': len(docs),
        'NEW_EVIDENCE_CHARS': sum(len(d['TEXT']) for d in docs),
        'FUTURE_CANDIDATES_RAW': len(cands),
        'FUTURE_CANDIDATES_WITH_CROP_AND_TARGET': len(fortes),
        'FUTURE_PROMOTED': len(SINAIS),
        'FUTURE_COMPLETE': est.get('COMPLETE', 0),
        'FUTURE_PARTIAL': est.get('PARTIAL', 0),
        'EVIDENCE_ONLY': est.get('EVIDENCE_ONLY', 0),
        'UNKNOWN': est.get('UNKNOWN', 0),
        'PROMOCAO_E_BAIXA_DE_PROPOSITO': (
            '3.035 candidatos brutos viraram 8 sinais. A missao pede para nao '
            'otimizar por quantidade: candidato e expressao de futuro, sinal e '
            'expressao SUSTENTADA pelo contexto, com cultura, alvo, regiao, '
            'horizonte, gatilho e resposta ADAMA. Encher o radar seria facil e '
            'seria pior.'),
        'WITH_COUNTRY': com('COUNTRY'), 'WITH_REGION': com('REGION'),
        'WITH_CROP': com('CROP'), 'WITH_TARGET': com('TARGET'),
        'WITH_TIME_HORIZON': com('TIME_HORIZON_DAYS'),
        'WITH_TRIGGER': com('TRIGGER'),
        'WITH_INVALIDATION_TRIGGER': com('INVALIDATION_TRIGGER'),
        'WITH_EXPECTED_WINDOW': sum(1 for s in SINAIS
                                    if s.get('WINDOW_EXPECTED') == 'YES'),
        'WITH_ADAMA_RESPONSE': sum(1 for s in SINAIS
                                   if s.get('ADAMA_LOCAL_RESPONSE') in ('YES', 'NO')),
        'WITH_PORTFOLIO_MATCH': sum(1 for s in SINAIS if s.get('PORTFOLIO_MATCHES')),
        'WITH_ACTION_MAP': com('ACTION_MAP'),
        'BY_HORIZON': dict(hz),
        'BY_EVIDENCE_TIME_STATE': dict(tempo),
        'HORIZON_0_30_DAYS': hz.get('HORIZON_0_30_DAYS', 0),
        'HORIZON_31_90_DAYS': hz.get('HORIZON_31_90_DAYS', 0),
        'HORIZON_91_180_DAYS': hz.get('HORIZON_91_180_DAYS', 0),
        'HORIZON_181_365_DAYS': hz.get('HORIZON_181_365_DAYS', 0),
        'NEXT_SEASON': hz.get('NEXT_SEASON', 0),
        'NO_HORIZON': sum(1 for s in SINAIS if not s.get('TIME_HORIZON_DAYS')),
        # ── por que falta o que falta (item 10) ────────────────────────────
        'MISSING_BY_ESSENTIAL_FIELD': dict(ausentes),
        'MISSING_FIELD_CAUSES': dict(causas),
        # ── acoes por departamento (item 12) ───────────────────────────────
        'ACTIONS_BY_DEPARTMENT': {d: dict(c) for d, c in sorted(dept.items())},
        'MARKET_DEVELOPMENT_ACTIONS': sum(dept['MARKET_DEVELOPMENT'].values()),
        'COMMERCIAL_ACTIONS': sum(dept['COMMERCIAL'].values()),
        'MARKETING_ACTIONS': sum(dept['MARKETING'].values()),
        'TECHNICAL_ACTIONS': sum(dept['TECHNICAL_SCIENTIFIC'].values()),
        'SUPPLY_ACTIONS': sum(dept['SUPPLY'].values()),
        'ACT_NOW_CREATED': 0,
        'ACT_NOW_LAW': 'nenhum estado foi promovido a ACT_NOW. Os estados usados sao '
                       'de PREPARACAO e de OBSERVACAO, que e o que sinal futuro '
                       'sustenta.',
        'SIGNALS': SINAIS,
    }


def main():
    os.makedirs(DEST, exist_ok=True)
    c = censo()
    json.dump(c, open(os.path.join(DEST, 'IT-FUTURO-RADAR-V1.json'), 'w',
                      encoding='utf-8'), ensure_ascii=False, indent=1)
    for k in ('NEW_EVIDENCE_SCANNED', 'NEW_EVIDENCE_CHARS', 'FUTURE_CANDIDATES_RAW',
              'FUTURE_CANDIDATES_WITH_CROP_AND_TARGET', 'FUTURE_PROMOTED',
              'FUTURE_COMPLETE', 'FUTURE_PARTIAL', 'WITH_REGION', 'WITH_CROP',
              'WITH_TARGET', 'WITH_TIME_HORIZON', 'WITH_TRIGGER',
              'WITH_EXPECTED_WINDOW', 'WITH_ADAMA_RESPONSE', 'WITH_PORTFOLIO_MATCH',
              'WITH_ACTION_MAP', 'MARKET_DEVELOPMENT_ACTIONS', 'COMMERCIAL_ACTIONS',
              'MARKETING_ACTIONS', 'TECHNICAL_ACTIONS', 'SUPPLY_ACTIONS'):
        print('%-42s %s' % (k, c[k]))
    print()
    print('BY_HORIZON              ', c['BY_HORIZON'])
    print('BY_EVIDENCE_TIME_STATE  ', c['BY_EVIDENCE_TIME_STATE'])
    print('MISSING_BY_ESSENTIAL    ', c['MISSING_BY_ESSENTIAL_FIELD'] or '(nenhum)')
    print('MISSING_FIELD_CAUSES    ', c['MISSING_FIELD_CAUSES'])
    return c


if __name__ == '__main__':
    main()
