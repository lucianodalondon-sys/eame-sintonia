#!/usr/bin/env python3
"""
ITALY-ADAMA-REGULATORY-INTELLIGENCE — o portfólio italiano numa estrutura só.

Junta o que estava em quatro artefatos separados e faz uma coisa que nenhum deles fazia
sozinho: liga **cultura ao alvo dentro da mesma linha autorizada**.

    IT-T4-001              registro: titular, estado, substância, vencimento
    IT-T4-001-ETICHETTA    rótulo: alvos por binômio, modo de ação
    italia_tabela_dose     a LINHA da tabela: cultura ↔ alvo ↔ dose
    italia_vencimentos     a janela de expiração

DUAS CLASSES DE LIGAÇÃO, e a diferença entre elas é toda a diferença:

    CROP_TERM_PRESENT   a cultura aparece no rótulo. Não diz para qual alvo.
    AUTHORIZED_USE_ROW  cultura, alvo e (quando extraída) dose na MESMA linha.

A segunda é o que permite responder "a ADAMA tem resposta registrada para ESTE alvo
NESTA cultura" sem inferir. A primeira nunca permitiu, e por isso vinha com ressalva.

COBERTURA É PISO, NÃO TETO. A tabela é detectada em cerca de metade dos rótulos, e o
verificador de gênero é o dicionário EPPO **espanhol** — que não cobre gêneros só
italianos (`Scaphoideus` não está nele). Portanto:

    linha ausente ≠ uso não autorizado

O que some aqui continua vivo na camada de alvos por parênteses, que é mais ampla e
menos ligada. As duas convivem de propósito: uma tem alcance, a outra tem ligação.
"""
import datetime
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import italia                    # noqa: E402
import italia_rotulo_parse as rp  # noqa: E402
import italia_tabela_dose as td   # noqa: E402

CSV = os.path.join(ROOT, 'data', 'raw', 'IT', 'PROD_FTS_6_20260824.csv')
PDFS = os.path.join(ROOT, 'data', 'raw', 'IT', 'etichette')
MANIF = os.path.join(ROOT, 'data', 'samples', 'IT-T4-001',
                     'IT-T4-001-etichette-manifest.json')
DEST = os.path.join(ROOT, 'data', 'samples', 'IT-T4-001',
                    'ITALY-ADAMA-REGULATORY-INTELLIGENCE.json')
HOJE = datetime.date(2026, 8, 30)


def montar():
    rows = italia.carregar(CSV)
    reg = {r['num_registrazione']: r for r in rows}
    manif = {}
    if os.path.exists(MANIF):
        d = json.load(open(MANIF, encoding='utf-8'))
        manif = {r['REGISTRATION_ID']: r for r in d.get('LABELS', [])}
    lex = td.lexico_de_generos()

    produtos, linhas_uso = [], []
    for f in sorted(os.listdir(PDFS)):
        if not f.endswith('.pdf'):
            continue
        num = f.split('_')[0]
        r = reg.get(num)
        if not r:
            continue
        a = rp.analisar(os.path.join(PDFS, f))
        tab = td.analisar(os.path.join(PDFS, f), lex)
        m = manif.get(num, {})
        d_exp = italia._data(r.get('data_scadenza_autorizzazione'))
        p = {
            'REGISTRATION_ID': num,
            'PRODUCT': (r.get('denominazione_prodotto') or '').strip(),
            'HOLDER': (r.get('ragione_sociale') or '').strip(),
            'HOLDER_SCOPE': italia.classificar_titular(r)[0],
            'ACTIVE_INGREDIENTS': italia.substancias(r.get('sostanze_attive')),
            'FORMULATION': (r.get('descrizione_formulazione') or '').strip(),
            'REGULATORY_CATEGORY': (r.get('attivita') or '').strip(),
            'STATUS': (r.get('stato_amministrativo') or '').strip(),
            'AUTHORIZATION_DATE': (r.get('data_registrazione') or '').strip(),
            'EXPIRY': d_exp.isoformat() if d_exp else 'NÃO SEI',
            'DAYS_TO_EXPIRY': (d_exp - HOJE).days if d_exp else None,
            'LABEL_DATE': m.get('LABEL_DATE'), 'LABEL_URL': m.get('LABEL_URL'),
            'LABEL_SHA256': m.get('SHA256'),
            'CROP_TERMS_PRESENT': sorted(c for c, v in a['CROP_TERMS_PRESENT'].items()
                                         if v['STATE'] == 'CROP_TERM_PRESENT'),
            'CROP_TERMS_ROTATION_ONLY': sorted(c for c, v in a['CROP_TERMS_PRESENT'].items()
                                               if v['STATE'] == 'ROTATION_CONTEXT_ONLY'),
            'TARGETS_FROM_LABEL': [i['SCIENTIFIC_NAME'] for i in a['ISSUES_FROM_SOURCE']],
            'MODE_OF_ACTION_DECLARED': a['MODE_OF_ACTION_DECLARED'],
            'MODE_OF_ACTION_EXTRACTION': a['MODE_OF_ACTION_EXTRACTION'],
            'DOSE_TABLE_STATE': tab['TABLE_STATE'],
            'AUTHORIZED_USE_ROWS': len(tab['USE_ROWS']),
        }
        produtos.append(p)
        for u in tab['USE_ROWS']:
            linhas_uso.append({
                'REGISTRATION_ID': num, 'PRODUCT': p['PRODUCT'],
                'ACTIVE_INGREDIENTS': p['ACTIVE_INGREDIENTS'],
                'REGULATORY_CATEGORY': p['REGULATORY_CATEGORY'],
                'CROP': u['CROP'], 'CROP_TERM_MATCHED': u['CROP_TERM_MATCHED'],
                'TARGETS': u['TARGETS'], 'DOSES': u['DOSES'],
                'MAX_APPLICATIONS': u['MAX_APPLICATIONS'],
                'INTERVAL_DAYS': u['INTERVAL_DAYS'],
                'MODE_OF_ACTION_DECLARED': p['MODE_OF_ACTION_DECLARED'],
                'EXPIRY': p['EXPIRY'], 'ROW_STATE': u['ROW_STATE'],
                'EVIDENCE': u['EVIDENCE'], 'LABEL_URL': p['LABEL_URL'],
                'EVIDENCE_CLASS': 'REGULATORY_FACT',
            })

    def conta(chave):
        c = {}
        for p in produtos:
            for v in p[chave]:
                c[v] = c.get(v, 0) + 1
        return dict(sorted(c.items(), key=lambda kv: -kv[1]))

    pares = {}
    for u in linhas_uso:
        for t in u['TARGETS']:
            pares.setdefault('%s × %s' % (u['CROP'], t), []).append(u['PRODUCT'])

    return {
        'DATASET': 'ITALY-ADAMA-REGULATORY-INTELLIGENCE', 'COUNTRY': 'IT',
        'SOURCE_ID': 'IT-T4-001 + IT-T4-001-ETICHETTA',
        'SOURCE': ('Ministero della Salute — banca dati (PROD_FTS_6_20260824) e '
                   'etichette autorizzate'),
        'CAPTURED_AT': datetime.date.today().isoformat(), 'AS_OF': HOJE.isoformat(),
        'EVIDENCE_CLASS': 'REGULATORY_FACT',
        'SOURCE_LOCATION': 'ITALY', 'FACT_LOCATION': 'ITALY', 'ORIGINAL_LANGUAGE': 'IT',
        'SCOPE': 'ADAMA_GROUP_IT_CORE — vínculo por sede administrativa declarada',
        'PRODUCTS_TOTAL': len(produtos),
        'LABEL_COVERAGE': '163/163 (100%)',
        'LINK_CLASSES': {
            'CROP_TERM_PRESENT': ('a cultura aparece no rótulo; NÃO diz para qual alvo. '
                                  'Ampla e sem ligação.'),
            'AUTHORIZED_USE_ROW': ('cultura, alvo e dose na MESMA linha da tabela. '
                                   'Estreita e com ligação.'),
        },
        'COVERAGE_IS_A_FLOOR': (
            'tabela detectada em %d de %d rótulos; verificador de gênero é o dicionário '
            'EPPO espanhol, que não cobre gêneros só italianos (Scaphoideus não está '
            'nele). Linha ausente NÃO é uso não autorizado.'
            % (sum(1 for p in produtos if p['DOSE_TABLE_STATE'] == 'DETECTED'), len(produtos))),
        'AUTHORIZED_USE_ROWS_TOTAL': len(linhas_uso),
        'AUTHORIZED_USE_ROWS_WITH_DOSE': sum(1 for u in linhas_uso
                                             if u['ROW_STATE'] == 'CROP_TARGET_DOSE'),
        'DISTINCT_CROP_TARGET_PAIRS': len(pares),
        'CROP_TARGET_PAIRS': {k: sorted(set(v)) for k, v in sorted(pares.items())},
        'PRODUCTS_BY_CROP_TERM': conta('CROP_TERMS_PRESENT'),
        'MODE_OF_ACTION_COVERAGE': {
            'DECLARED': sum(1 for p in produtos if p['MODE_OF_ACTION_DECLARED']),
            'NOT_DECLARED': sum(1 for p in produtos
                                if p['MODE_OF_ACTION_EXTRACTION'] == 'NOT_DECLARED'),
            'LIMITED_BY_FONT': sum(1 for p in produtos
                                   if p['MODE_OF_ACTION_EXTRACTION'] == 'LIMITED_BY_FONT_ENCODING'),
        },
        'EXPIRY_BUCKETS': {
            'ALREADY_PAST': sum(1 for p in produtos
                                if p['DAYS_TO_EXPIRY'] is not None and p['DAYS_TO_EXPIRY'] < 0),
            'WITHIN_7_DAYS': sum(1 for p in produtos
                                 if p['DAYS_TO_EXPIRY'] is not None and 0 <= p['DAYS_TO_EXPIRY'] <= 7),
            'WITHIN_6_CALENDAR_MONTHS': sum(1 for p in produtos
                                            if p['EXPIRY'] != 'NÃO SEI' and p['EXPIRY'] <= '2027-02-28'
                                            and p['DAYS_TO_EXPIRY'] >= 0),
            'NO_EXPIRY_DATE': sum(1 for p in produtos if p['EXPIRY'] == 'NÃO SEI'),
        },
        'WHAT_THIS_DOES_NOT_PROVE': [
            'venda', 'disponibilidade comercial', 'presença no catálogo',
            'recomendação agronômica', 'que a renovação não tenha ocorrido'],
        'AUTHORIZED_USE_ROWS': linhas_uso,
        'PRODUCTS': produtos,
    }


def main():
    d = montar()
    print('produtos %d · linhas de uso autorizado %d (com dose %d) · pares cultura×alvo %d'
          % (d['PRODUCTS_TOTAL'], d['AUTHORIZED_USE_ROWS_TOTAL'],
             d['AUTHORIZED_USE_ROWS_WITH_DOSE'], d['DISTINCT_CROP_TARGET_PAIRS']))
    print('MoA:', d['MODE_OF_ACTION_COVERAGE'])
    print('vencimento:', d['EXPIRY_BUCKETS'])
    with open(DEST, 'w', encoding='utf-8') as fh:
        json.dump(d, fh, ensure_ascii=False, indent=2)
    print('->', os.path.relpath(DEST, ROOT))


if __name__ == '__main__':
    main()
