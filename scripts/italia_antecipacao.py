#!/usr/bin/env python3
"""
O teste que impede o caso de trapacear com o tempo.

`IT-CASE-DURUM-FUSARIUM-001` afirma que houve uma convergência real em **23/04/2026**.
Um caso assim só prova antecipação se puder ser fechado **com o que existia naquele dia**.
Se qualquer peça publicada depois for necessária para justificar o alerta, o caso não
mostra antecipação — mostra retrospectiva bem escrita, que é outra coisa e vale muito
menos.

    FUTURE_EVIDENCE_CANNOT_CLOSE_PAST_CASE

A REGRA OPERACIONAL
--------------------
Toda peça de evidência declara `SOURCE_DATE` e um papel:

    SUSTAINS_ALERT   entra na justificativa do alerta daquele dia
    CONTEXT_ONLY     ajuda a descrever ou auditar o caso hoje, e NÃO o sustenta

Nenhuma peça com `SOURCE_DATE > CASE_DATE` pode ter papel `SUSTAINS_ALERT`. O teste é
mecânico de propósito: julgamento sobre "mas isso já se sabia" é exatamente o lugar onde
a contaminação entra.

O CUIDADO QUE QUASE PASSOU
---------------------------
Os PDFs dos rótulos foram baixados em **agosto de 2026**, depois do caso. Isso por si só
não os torna evidência futura — um decreto de 2022 dizia em abril o que diz hoje. Mas o
rótulo italiano **é modificável** sob o art. 7 do D.P.R. 55/2012, e uma cópia de agosto
pode carregar uma modificação de junho. Então a data que importa não é a do download: é a
**data de vigência declarada dentro do documento**.

Conferido, um a um:

    BLAISE ULTRA     Decreto Dirigenziale del 29/04/2022
    CUSTODIA ULTRA   Decreto Dirigenziale del 29/04/2022
    MIRADOR TURBO    Decreto Dirigenziale del 29/04/2022
    MAXENTIS         decreto 14.06.2024, modificata con validità dal 18/03/2026
    KOJAMI           decreto 29 settembre 2025, modificata con validità dal 18/03/2026

Todas ≤ 23/04/2026. A versão que eu tenho é a versão que estava em vigor no dia.

O QUE **NÃO** ESTAVA DISPONÍVEL, E FICA DE FORA
------------------------------------------------
O instantâneo do registro ministerial que eu uso é o `PROD_FTS_6_20260824.csv`, de
**24/08/2026**. Dele vêm `data_scadenza_autorizzazione` e `stato_amministrativo` — ou
seja, **saber que CUSTODIA ULTRA e BLAISE ULTRA vencem em 15/08/2026 é conhecimento
posterior ao caso**. Provavelmente o registro já dizia isso em abril; eu não tenho
instantâneo de abril, e "provavelmente" não fecha caso.

Consequência: o vencimento entra como `CONTEXT_ONLY`. Ele descreve o estado de hoje, não
sustenta o alerta de então — e o alerta não precisa dele, porque o alerta é
`campo + rótulo`, não `campo + rótulo + vencimento`.
"""
import datetime
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DEST = os.path.join(ROOT, 'data', 'samples', 'IT-CASOS',
                    'IT-CASE-DURUM-FUSARIUM-001-antecipacao.json')

CASE_DATE = datetime.date(2026, 4, 23)
SUSTAINS = 'SUSTAINS_ALERT'
CONTEXT = 'CONTEXT_ONLY'


def evidencias():
    return [
        {'ITEM': 'Bollettino LaMMA Grosseto — frumento',
         'SOURCE_ID': 'IT-T3-LAMMA', 'SOURCE_DATE': '2026-04-23', 'ROLE': SUSTAINS,
         'WHAT_IT_GIVES': ('grano duro entrando em fioritura no sul; sintomas leves de '
                           'fusariose observados no duro; chuva ocorrida e prevista; '
                           'recomendação condicional de tratamento'),
         'PRESERVED': True,
         'SHA256_IN': 'IT-T3-LAMMA-grosseto-2026-04-23.json'},
        {'ITEM': 'Etichetta MAXENTIS', 'SOURCE_ID': 'IT-T4-001-ETICHETTA',
         'SOURCE_DATE': '2026-03-18', 'ROLE': SUSTAINS,
         'IN_DOCUMENT_VALIDITY_IT': ('decreto dirigenziale del 14.06.2024 e modificata '
                                     'ai sensi dell\'art. 7, comma 1, D.P.R. n. 55/2012, '
                                     'con validità dal 18/03/2026'),
         'WHAT_IT_GIVES': ('"Frumento tenero e duro" contra Fusarium spp. e Microdochium '
                           'spp., janela até fine fioritura'),
         'PRESERVED': True,
         'CAPTURE_NOTE': ('o PDF foi baixado em agosto; o que datei é a vigência '
                          'declarada DENTRO do documento, não o download')},
        {'ITEM': 'Etichetta KOJAMI', 'SOURCE_ID': 'IT-T4-001-ETICHETTA',
         'SOURCE_DATE': '2026-03-18', 'ROLE': SUSTAINS,
         'IN_DOCUMENT_VALIDITY_IT': ('decreto dirigenziale del 29 settembre 2025 e '
                                     'modificata ai sensi dell\'art.7, comma 1, D.P.R. '
                                     'n. 55/2012, con validità dal 18/03/2026'),
         'WHAT_IT_GIVES': 'idem MAXENTIS', 'PRESERVED': True},
        {'ITEM': 'Etichetta CUSTODIA ULTRA', 'SOURCE_ID': 'IT-T4-001-ETICHETTA',
         'SOURCE_DATE': '2022-04-29', 'ROLE': SUSTAINS,
         'IN_DOCUMENT_VALIDITY_IT': 'Etichetta Autorizzata con Decreto Dirigenziale del 29/04/2022',
         'WHAT_IT_GIVES': 'fungicida foliar de cereais autorizado em frumento tenero e duro',
         'PRESERVED': True},
        {'ITEM': 'Etichetta BLAISE ULTRA', 'SOURCE_ID': 'IT-T4-001-ETICHETTA',
         'SOURCE_DATE': '2022-04-29', 'ROLE': SUSTAINS,
         'IN_DOCUMENT_VALIDITY_IT': 'Etichetta autorizzata con Decreto Dirigenziale del 29/04/2022',
         'WHAT_IT_GIVES': 'idem', 'PRESERVED': True},
        {'ITEM': 'Etichetta MIRADOR TURBO', 'SOURCE_ID': 'IT-T4-001-ETICHETTA',
         'SOURCE_DATE': '2022-04-29', 'ROLE': SUSTAINS,
         'IN_DOCUMENT_VALIDITY_IT': 'Etichetta Autorizzata con Decreto Dirigenziale del 29/04/2022',
         'WHAT_IT_GIVES': 'idem', 'PRESERVED': True},
        {'ITEM': 'ISTAT — área regional de trigo duro', 'SOURCE_ID': 'IT-T1-001',
         'SOURCE_DATE': '2025-12-31', 'ROLE': CONTEXT,
         'WHAT_IT_GIVES': 'a Toscana é 3,7% da cultura — dimensiona o caso, não o alerta',
         'PRESERVED': True},

        # ---------------------------------------------------------------- POSTERIORES
        {'ITEM': 'Instantâneo do registro ministerial (PROD_FTS_6_20260824.csv)',
         'SOURCE_ID': 'IT-T4-001', 'SOURCE_DATE': '2026-08-24', 'ROLE': CONTEXT,
         'WHAT_IT_GIVES': ('data_scadenza_autorizzazione e stato_amministrativo — donde '
                           'sai que CUSTODIA ULTRA e BLAISE ULTRA vencem em 15/08/2026'),
         'WHY_CONTEXT_ONLY': ('é posterior ao caso. O registro provavelmente já dizia '
                              'isso em abril, mas eu não tenho instantâneo de abril, e '
                              '"provavelmente" não fecha caso. O alerta é campo+rótulo e '
                              'não precisa do vencimento.'),
         'PRESERVED': True},
        {'ITEM': 'Correção do extrator (elisão de cabeça) e a contagem de 26 produtos',
         'SOURCE_ID': 'DERIVED/IT-COORDINATION-SWEEP', 'SOURCE_DATE': '2026-08-30',
         'ROLE': CONTEXT,
         'WHAT_IT_GIVES': ('a capacidade de EU enxergar que os rótulos autorizam grano '
                           'duro'),
         'WHY_CONTEXT_ONLY': (
             'é ferramenta minha, de agosto, não fato do mundo de abril. Distinção que '
             'importa: o RÓTULO já dizia "Frumento tenero e duro" em março; o que faltava '
             'era eu saber ler. A limitação era do observador, não da evidência — e por '
             'isso o alerta continua sustentável em 23/04/2026 por quem soubesse ler.'),
         'PRESERVED': True},
        {'ITEM': 'Crítica de viés de painel e cobertura nacional de campo',
         'SOURCE_ID': 'DERIVED/IT-PANEL-BIAS', 'SOURCE_DATE': '2026-08-30',
         'ROLE': CONTEXT,
         'WHAT_IT_GIVES': '57,9% do trigo duro sem sonda — limita o ESCOPO, não o alerta',
         'PRESERVED': True},
    ]


def auditar(evs, case_date=CASE_DATE):
    """A regra mecânica. Devolve (ok, violacoes)."""
    viol = []
    for e in evs:
        d = datetime.date.fromisoformat(e['SOURCE_DATE'])
        if e['ROLE'] == SUSTAINS and d > case_date:
            viol.append({'ITEM': e['ITEM'], 'SOURCE_DATE': e['SOURCE_DATE'],
                         'WHY': 'posterior a %s e mesmo assim marcada como %s'
                                % (case_date.isoformat(), SUSTAINS)})
    return (not viol), viol


def main():
    evs = evidencias()
    ok, viol = auditar(evs)
    por_dia = [e for e in evs if e['ROLE'] == SUSTAINS]
    depois = [e for e in evs
              if datetime.date.fromisoformat(e['SOURCE_DATE']) > CASE_DATE]

    out = {
        'CASE_ID': 'IT-CASE-DURUM-FUSARIUM-001',
        'SOURCE_ID': 'DERIVED/IT-CASE-ANTICIPATION',
        'source': 'auditoria temporal das evidências do caso',
        'SOURCE_LOCATION': 'interno — auditoria sobre artefatos próprios',
        'FACT_LOCATION': 'ITALY — Toscana',
        'ORIGINAL_LANGUAGE': 'pt',
        'EVIDENCE_CLASS': 'DERIVED_INTERPRETATION',
        'captured_at': datetime.date.today().isoformat(),
        'CAPTURED_AT': datetime.date.today().isoformat(),
        'CASE_DATE': CASE_DATE.isoformat(),
        'LAW': 'FUTURE_EVIDENCE_CANNOT_CLOSE_PAST_CASE',
        'QUESTION': ('se o Sintonia estivesse operando em 23/04/2026, quais sinais já '
                     'estavam disponíveis naquele dia?'),
        'ANSWER': ('os dois que formam o alerta: o boletim do LaMMA, publicado NO dia, e '
                   'os cinco rótulos, todos com vigência declarada anterior. O alerta '
                   'fecha sem nenhuma peça posterior.'),
        'RULE': {SUSTAINS: 'entra na justificativa do alerta daquele dia',
                 CONTEXT: 'descreve ou audita o caso hoje, e NÃO o sustenta'},
        'AVAILABLE_BY_CASE_DATE': por_dia,
        'AVAILABLE_ONLY_LATER': depois,
        'AUDIT_PASSES': ok,
        'VIOLATIONS': viol,
        'THE_SUBTLETY_THAT_ALMOST_SLIPPED': (
            'os PDFs dos rótulos foram baixados em agosto. Isso NÃO os torna evidência '
            'futura — mas o rótulo italiano é modificável sob o art. 7 do D.P.R. '
            '55/2012, e uma cópia de agosto pode carregar modificação de junho. Por isso '
            'a data usada não é a do download: é a VIGÊNCIA DECLARADA DENTRO do '
            'documento, conferida um a um. Todas ≤ 23/04/2026.'),
        'OBSERVER_LIMITATION_IS_NOT_EVIDENCE_LIMITATION': (
            'a correção do extrator é de 30/08 e entra como CONTEXT_ONLY. Mas o rótulo '
            'já dizia "Frumento tenero e duro" desde março: o que faltava era eu saber '
            'ler. A limitação era do OBSERVADOR, não da evidência — e por isso o alerta '
            'continuava sustentável em 23/04/2026 por quem soubesse ler.'),
        'WHAT_THIS_PROVES': (
            'que o Sintonia TERIA conseguido enxergar a convergência enquanto ela '
            'existia, com fonte pública disponível no dia'),
        'WHAT_THIS_DOES_NOT_PROVE': [
            'que a convergência ainda exista hoje — a janela agronômica de 2026 fechou',
            'que alguém tenha agido, comprado ou tratado',
            'que haja oportunidade comercial: a janela comercial é NOT_KNOWN',
            'nada fora da Toscana',
        ],
    }
    os.makedirs(os.path.dirname(DEST), exist_ok=True)
    with open(DEST, 'w', encoding='utf-8') as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)

    print('CASE_DATE %s' % CASE_DATE)
    print('AVAILABLE_BY_CASE_DATE (%d):' % len(por_dia))
    for e in por_dia:
        print('   %s  %s' % (e['SOURCE_DATE'], e['ITEM']))
    print('AVAILABLE_ONLY_LATER (%d):' % len(depois))
    for e in depois:
        print('   %s  %-58s ROLE=%s' % (e['SOURCE_DATE'], e['ITEM'][:58], e['ROLE']))
    print('AUDITORIA: %s%s' % ('PASSA' if ok else 'FALHA', '' if ok else ' -> %s' % viol))
    print('->', os.path.relpath(DEST, ROOT))


if __name__ == '__main__':
    main()
