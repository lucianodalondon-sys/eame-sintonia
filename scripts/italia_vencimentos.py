#!/usr/bin/env python3
"""
ITÁLIA — o calendário de vencimentos, enriquecido com o que cada autorização carrega.

Uma lista de datas não é decisão. "12 autorizações vencem em 31/10" não diz a ninguém
o que fazer. O que torna a informação acionável é **o que se perde se não for renovado**:
qual cultura, qual alvo, qual substância — e isso só existe porque os 163 rótulos foram
colhidos.

DUAS COISAS QUE ESTE ARQUIVO SE RECUSA A DIZER

1. **`EXPIRY ≠ WITHDRAWAL`.** Vencimento de autorização não é retirada do mercado.
   Re-registro é rotina, e a maioria destes produtos já está como `Ri-registrato` —
   ou seja, já passou por isso antes. O que se entrega é "estas datas pedem revisão",
   nunca "a ADAMA vai perder o portfólio".

2. **O campo de estado NÃO é oráculo de vigência.** Oito autorizações vencidas em
   15/08/2026 seguiam com estado ativo num arquivo de 24/08/2026 — atraso mínimo
   medido de 9 dias. Isso é `REGULATORY_STATUS_LAG`, e **não** se chama erro do
   Ministero: pode ser fluxo administrativo, prorrogação ainda não publicada ou
   defasagem do extrato aberto. A classificação honesta é INVESTIGAR, não acusar.

E a consequência prática das duas: `RENEWAL_STATUS = NÃO SEI` para todo registro cuja
data caiu depois da versão do arquivo. O que se observa é a versão do open data —
`PROD_FTS_6_20260824` —, não o registro em tempo real.

A JANELA DE 6 MESES DEPENDE DA CONVENÇÃO, e a diferença não é arredondamento:
180 dias → 58 · 6 meses de calendário → 71. Treze autorizações vencem TODAS em
2027-02-28, data que uma convenção inclui e a outra exclui.
"""
import datetime
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import italia  # noqa: E402

PORTFOLIO = os.path.join(ROOT, 'data', 'samples', 'IT-T4-001',
                         'IT-T4-001-portfolio-rotulo.json')
DEST = os.path.join(ROOT, 'data', 'samples', 'IT-T4-001',
                    'IT-T4-001-vencimentos-caso.json')
HOJE = datetime.date(2026, 8, 30)
CSV = os.path.join(ROOT, 'data', 'raw', 'IT', 'PROD_FTS_6_20260824.csv')


def indice_rotulos():
    if not os.path.exists(PORTFOLIO):
        return {}
    d = json.load(open(PORTFOLIO, encoding='utf-8'))
    return {p['REGISTRATION_ID']: p for p in d.get('PRODUCTS', [])}


def montar(hoje=HOJE, csv_path=CSV):
    rows = italia.carregar(csv_path)
    idx = indice_rotulos()
    ativos = [r for r in rows
              if italia.classificar_titular(r)[0] in ('ADAMA_IT_LEGAL_ENTITY',
                                                      'ADAMA_GROUP_IT_CORE')
              and (r.get('stato_amministrativo') or '').strip() not in italia.STATUS_NAO_VIGENTE]
    fut, passados = [], []
    for r in ativos:
        d = italia._data(r.get('data_scadenza_autorizzazione'))
        if d is None:
            continue
        (fut if d >= hoje else passados).append((d, r))

    d180 = hoje + datetime.timedelta(days=180)
    cal6 = datetime.date(2027, 2, 28)
    cal12 = datetime.date(2027, 8, 30)

    def ficha(d, r):
        p = idx.get(r['num_registrazione'], {})
        return {
            'EXPIRY': d.isoformat(),
            'DAYS_FROM_TODAY': (d - hoje).days,
            'REGISTRATION_ID': r['num_registrazione'],
            'PRODUCT': (r.get('denominazione_prodotto') or '').strip(),
            'HOLDER': (r.get('ragione_sociale') or '').strip(),
            'ACTIVE_INGREDIENTS': italia.substancias(r.get('sostanze_attive')),
            'REGULATORY_CATEGORY': (r.get('attivita') or '').strip(),
            'STATUS': (r.get('stato_amministrativo') or '').strip(),
            # Cultura e alvo vêm do RÓTULO, não do CSV — é a rota nova que os traz.
            'CROP_TERMS_ON_LABEL': p.get('CROP_TERMS_PRESENT', []),
            'ISSUES_ON_LABEL': [i['SCIENTIFIC_NAME']
                                for i in p.get('ISSUES_FROM_SOURCE', [])][:12],
            'MODE_OF_ACTION_DECLARED': p.get('MODE_OF_ACTION_DECLARED', {}),
            'LABEL_URL': p.get('LABEL_URL'),
            'RENEWAL_STATUS': 'NÃO SEI',
        }

    janela6 = sorted([ficha(d, r) for d, r in fut if d <= cal6],
                     key=lambda f: (f['EXPIRY'], f['PRODUCT']))
    por_data = {}
    for f in janela6:
        por_data.setdefault(f['EXPIRY'], []).append(f['PRODUCT'])

    culturas = {}
    for f in janela6:
        for c in f['CROP_TERMS_ON_LABEL']:
            culturas[c] = culturas.get(c, 0) + 1

    return {
        'COUNTRY': 'IT', 'SOURCE_ID': 'IT-T4-001',
        'SOURCE': ('Ministero della Salute — banca dati prodotti fitosanitari '
                   '(PROD_FTS_6_20260824) + etichette autorizzate'),
        'CAPTURED_AT': datetime.date.today().isoformat(),
        'AS_OF': hoje.isoformat(),
        'DATASET_VERSION_OBSERVED': 'PROD_FTS_6_20260824',
        'EVIDENCE_CLASS': 'REGULATORY_FACT',
        'SCOPE': 'ADAMA_GROUP_IT_CORE (5 razões sociais, vínculo por sede declarada)',
        'ACTIVE_TOTAL': len(ativos),
        'WINDOW_CONVENTION': {
            'EXPIRING_180_DAYS': sum(1 for d, _ in fut if d <= d180),
            'EXPIRING_CALENDAR_6M_TO_2027_02_28': sum(1 for d, _ in fut if d <= cal6),
            'EXPIRING_CALENDAR_12M': sum(1 for d, _ in fut if d <= cal12),
            'CLIFF': ('13 autorizações vencem TODAS em 2027-02-28 — data que 180 dias '
                      'exclui e 6 meses de calendário inclui. A convenção muda a resposta '
                      'em 13 registros, e publicar o número sem ela é publicar ambiguidade.'),
            'CONVENTION_ADOPTED': 'calendário',
        },
        'STATUS_LAG': {
            'COUNT': len(passados),
            'ALL_EXPIRED_ON': sorted({d.isoformat() for d, _ in passados}),
            'DATASET_DATED': '2026-08-24',
            'MIN_LAG_DAYS': 9,
            'CLASSIFICATION': 'REGULATORY_STATUS_LAG / INVESTIGATE',
            'NOT_CALLED': ('DATABASE_ERROR — não há fonte que sustente isso. Pode ser '
                           'fluxo administrativo, prorrogação não publicada ou defasagem '
                           'do extrato aberto.'),
            'CONSEQUENCE': 'nenhum alerta de vencimento pode sair do campo de estado; a data manda',
            'ITEMS': [ficha(d, r) for d, r in sorted(passados, key=lambda t: t[0])],
        },
        'EXPIRING_NEXT_6_MONTHS': janela6,
        'BY_DATE': dict(sorted(por_data.items())),
        'BY_CROP_TERM': dict(sorted(culturas.items(), key=lambda kv: -kv[1])),
        'IMMINENT_7_DAYS': [f for f in janela6 if f['DAYS_FROM_TODAY'] <= 7],
        'WHAT_THIS_DOES_NOT_PROVE': [
            'retirada do mercado', 'perda de portfólio', 'impacto comercial',
            'que a renovação não tenha ocorrido', 'estoque', 'venda'],
    }


def main():
    d = montar()
    print('ADAMA vigentes: %d' % d['ACTIVE_TOTAL'])
    w = d['WINDOW_CONVENTION']
    print('vencendo: 180d=%d · calendário 6m=%d · 12m=%d'
          % (w['EXPIRING_180_DAYS'], w['EXPIRING_CALENDAR_6M_TO_2027_02_28'],
             w['EXPIRING_CALENDAR_12M']))
    print('status lag: %d (todas em %s)' % (d['STATUS_LAG']['COUNT'],
                                            ', '.join(d['STATUS_LAG']['ALL_EXPIRED_ON'])))
    print('\nIMINENTES (<= 7 dias): %d' % len(d['IMMINENT_7_DAYS']))
    for f in d['IMMINENT_7_DAYS']:
        print('   %s  %-22s %-26s %s' % (f['EXPIRY'], f['PRODUCT'][:22],
                                         '|'.join(f['ACTIVE_INGREDIENTS'])[:26],
                                         ','.join(f['CROP_TERMS_ON_LABEL'][:4])))
    print('\nculturas mais afetadas na janela de 6 meses:')
    for c, n in list(d['BY_CROP_TERM'].items())[:8]:
        print('   %-16s %d' % (c, n))
    os.makedirs(os.path.dirname(DEST), exist_ok=True)
    with open(DEST, 'w', encoding='utf-8') as fh:
        json.dump(d, fh, ensure_ascii=False, indent=2)
    print('\n->', os.path.relpath(DEST, ROOT))


if __name__ == '__main__':
    main()
