#!/usr/bin/env python3
"""
ITÁLIA — a matriz REGIÃO × CAMADA, porque "fonte ITALY" não decide nada.

A Itália é regionalmente fragmentada: 20 regiões, cada uma com serviço fitossanitário
próprio, calendário próprio e política de publicação própria. Uma fonte marcada
`COUNTRY = ITALY` esconde exatamente a informação que decide — **em qual região aquela
camada existe.**

Esta matriz cruza o que já foi medido separadamente:

    ÁREA        IT-T1-001 (ISTAT) — quanto de cada cultura a região tem
    CAMPO       IT-T3-* — a região publica boletim? de qual cultura?
    NORMA       IT-T3-LOTTA — a região tem obrigação legal datada?
    REDE        ITALY-ORIGIN-UNIVERSE — há nó técnico identificado?
    CIÊNCIA     IT-T5-001 — há instituição do recorte ali?

E publica a coluna que a rodada anterior provou ser a mais importante:

    SIGNAL_COVERS_PCT_OF_CROP

porque o achado estrutural desta branch é que **a camada de campo não cobre onde a
cultura está**. Sem essa coluna, um sinal do Vêneto para oliveira parece cobertura
nacional — e cobre 0,5 %.

`NOT_MEASURED` e `NOT_OBTAINED` NÃO viram zero. Região sem linha é região não medida.
"""
import datetime
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
S = os.path.join(ROOT, 'data', 'samples')
DEST = os.path.join(S, 'IT-FONTES', 'ITALY-REGIONAL-COVERAGE-MATRIX.json')


def _ler(rel):
    p = os.path.join(S, rel)
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else None


def matriz():
    istat = _ler('IT-T1/IT-T1-001-istat-area-regional.json') or {}
    porcrop = istat.get('BY_CROP', {})

    def area(cultura, regiao):
        d = porcrop.get(cultura) or {}
        for r in d.get('BY_REGION', []):
            if r['REGION'].startswith(regiao):
                return r['AREA_THS_HA'], round(100.0 * r['AREA_THS_HA'] /
                                               (d['NUTS2_SUM_THS_HA'] or 1), 1)
        return None, None

    linhas = []
    for regiao, campo in [
        ('Veneto', {
            'FIELD_STATE': 'PUBLISHED_WEEKLY',
            'FIELD_CROPS': ['Videira', 'Oliveira', 'Frutícolas', 'Hortícolas',
                            'Trigo', 'Beterraba'],
            'FIELD_CROPS_ABSENT': ['Milho'],
            'FIELD_NOTE': ('2026: 28 olivo · 25 frutícola · 21 hortícola · 16+ vite · '
                           '2 erbacee (trigo em março, beterraba em junho). ~30 % dos '
                           'boletins de vite são digitalizados sem camada de texto.'),
            'MANDATORY_CONTROL': 'SIM — DDR 13645/2026 (flavescência); datas via boletim',
            'NETWORK_NODES': ['IT-ORG-VENETO-FITO'],
            'SCIENCE_INSTITUTIONS': ['Dafnae-UniPD', 'CREA-VE'],
        }),
        ('Lombardia', {
            'FIELD_STATE': 'PUBLISHED',
            'FIELD_CROPS': ['Videira', 'Macieira'], 'FIELD_CROPS_ABSENT': ['Milho'],
            'FIELD_NOTE': '2026: 6 vite · 4 melo · nenhum de herbáceas',
            'MANDATORY_CONTROL': ('SIM — Comunicato Giunta 25/05/2026 n. 39; datas NO ato '
                                  '(2–14/06 e 17–29/06)'),
            'NETWORK_NODES': ['IT-ORG-LOMBARDIA-SFR'],
            'SCIENCE_INSTITUTIONS': ['Università Cattolica (Piacenza, limítrofe)',
                                     'University of Milan'],
        }),
        ('Piemonte', {
            'FIELD_STATE': 'NOT_OBTAINED',
            'FIELD_CROPS': [], 'FIELD_CROPS_ABSENT': [],
            'FIELD_NOTE': ('a *bacheca dei bollettini* é renderizada por JavaScript; o HTML '
                           'obtido não traz PDF nem nome de cultura. NÃO é ausência.'),
            'MANDATORY_CONTROL': 'SIM (flavescência) — ato não obtido nesta rodada',
            'NETWORK_NODES': [], 'SCIENCE_INSTITUTIONS': ['University of Turin'],
        }),
        ('Emilia-Romagna', {
            'FIELD_STATE': 'PARTIAL',
            'FIELD_CROPS': ['Milho (página de avversità)', 'Videira', 'Tomate'],
            'FIELD_CROPS_ABSENT': [],
            'FIELD_NOTE': ('Consorzio Fitosanitario Provinciale di Piacenza publica página '
                           'de diabrotica, bollettini territoriais e modelos previsionais; '
                           'os bollettini em si ficaram NOT_OBTAINED (sem PDF no HTML lido)'),
            'MANDATORY_CONTROL': 'NÃO MEDIDO',
            'NETWORK_NODES': ['IT-ORG-CONSFITO-PC'],
            'SCIENCE_INSTITUTIONS': ['Università Cattolica del Sacro Cuore (Piacenza)',
                                     'University of Bologna'],
        }),
        ('Friuli-Venezia Giulia', {
            'FIELD_STATE': 'PUBLISHED_REGULARLY',
            'FIELD_CROPS': ['Milho', 'Soja', 'Trigo', 'Cevada', 'Colza', 'Videira'],
            'FIELD_CROPS_ABSENT': [],
            'FIELD_NOTE': ('única série de boletim de MILHO medida na Itália — 10 números '
                           'em 2026, último n.15 de 12/08, com BBCH e limiar publicado'),
            'MANDATORY_CONTROL': 'difesa integrata obbligatoria (art. 19 D.lgs. 150/2012)',
            'NETWORK_NODES': ['IT-ORG-ERSA-FVG'],
            'SCIENCE_INSTITUTIONS': ['University of Udine'],
        }),
        ('Puglia', {
            'FIELD_STATE': 'NO_PHYTOPATHOLOGY_SINCE_2018',
            'FIELD_CROPS': [], 'FIELD_CROPS_ABSENT': ['Oliveira', 'Trigo duro'],
            'FIELD_NOTE': ('o portal agrometeo declara que desde 11/04/2018 "la sezione '
                           'dedicata alla Fitopatologia non viene più redatta" — competência '
                           'em transferência para a ARIF, ainda descrita como em curso'),
            'MANDATORY_CONTROL': 'NÃO MEDIDO',
            'NETWORK_NODES': ['IT-ORG-ASSOPROLI'],
            'SCIENCE_INSTITUTIONS': ['CNR-ISPA (Bari)'],
        }),
        ('Sicilia', {
            'FIELD_STATE': 'NOT_MEASURED', 'FIELD_CROPS': [], 'FIELD_CROPS_ABSENT': [],
            'FIELD_NOTE': 'não medida nesta rodada', 'MANDATORY_CONTROL': 'NÃO MEDIDO',
            'NETWORK_NODES': [], 'SCIENCE_INSTITUTIONS': [],
        }),
        ('Calabria', {
            'FIELD_STATE': 'NOT_MEASURED', 'FIELD_CROPS': [], 'FIELD_CROPS_ABSENT': [],
            'FIELD_NOTE': 'não medida nesta rodada', 'MANDATORY_CONTROL': 'NÃO MEDIDO',
            'NETWORK_NODES': [], 'SCIENCE_INSTITUTIONS': [],
        }),
    ]:
        l = {'REGION': regiao}
        for cultura, chave in (('MAIZE', 'Milho'), ('VINE', 'Videira'),
                               ('OLIVE', 'Oliveira'), ('DURUM_WHEAT', 'Trigo duro')):
            ha, pct = area(cultura, regiao)
            l['AREA_%s_THS_HA' % cultura] = ha
            l['PCT_NATIONAL_%s' % cultura] = pct
        l.update(campo)
        linhas.append(l)
    return linhas


def cobertura_por_cultura(linhas):
    """Quanto da cultura fica coberto por região que PUBLICA aquela cultura."""
    out = {}
    for cultura, nome in (('MAIZE', 'Milho'), ('VINE', 'Videira'),
                          ('OLIVE', 'Oliveira'), ('DURUM_WHEAT', 'Trigo duro')):
        cob = med = 0.0
        regs_cob, regs_sem = [], []
        for l in linhas:
            pct = l.get('PCT_NATIONAL_%s' % cultura)
            if pct is None or l['FIELD_STATE'] in ('NOT_MEASURED', 'NOT_OBTAINED'):
                continue
            med += pct
            if nome in l['FIELD_CROPS'] or any(nome in c for c in l['FIELD_CROPS']):
                cob += pct
                regs_cob.append(l['REGION'])
            else:
                regs_sem.append(l['REGION'])
        out[cultura] = {
            'CROP': nome,
            'PCT_MEASURED': round(med, 1),
            'SIGNAL_COVERS_PCT_OF_CROP': round(cob, 1),
            'REGIONS_WITH_SIGNAL': regs_cob,
            'REGIONS_MEASURED_WITHOUT_SIGNAL': regs_sem,
        }
    return out


def main():
    linhas = matriz()
    cob = cobertura_por_cultura(linhas)
    out = {
        'DATASET': 'ITALY-REGIONAL-COVERAGE-MATRIX', 'COUNTRY': 'IT',
        'SOURCE_ID': 'DERIVED/IT-REGIONAL-MATRIX',
        'SOURCE': 'IT-T1-001 (ISTAT) × IT-T3-* (campo) × IT-T3-LOTTA × ITALY-ORIGIN-UNIVERSE',
        'CAPTURED_AT': datetime.date.today().isoformat(),
        'EVIDENCE_CLASS': 'DERIVED_INTERPRETATION',
        'WHY': ('"fonte ITALY" esconde a informação que decide. A Itália publica por '
                'região, e cada região decide o que publicar.'),
        'REGIONS_IN_MATRIX': len(linhas),
        'REGIONS_TOTAL_ITALY': 20,
        'COVERAGE_NOTE': ('8 regiões na matriz, escolhidas por peso nas culturas dos casos. '
                          'Região fora da matriz é NÃO MEDIDA, nunca sem sinal.'),
        'SIGNAL_COVERAGE_BY_CROP': cob,
        'MATRIX': linhas,
    }
    os.makedirs(os.path.dirname(DEST), exist_ok=True)
    with open(DEST, 'w', encoding='utf-8') as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    print('REGIÃO               MILHO   VIDEIRA  OLIVEIRA  CAMPO')
    for l in linhas:
        print('%-20s %6s %8s %9s  %s' % (
            l['REGION'][:20], l.get('PCT_NATIONAL_MAIZE'), l.get('PCT_NATIONAL_VINE'),
            l.get('PCT_NATIONAL_OLIVE'), l['FIELD_STATE'][:30]))
    print()
    for k, v in cob.items():
        print('%-12s sinal cobre %5s%% de %5s%% medido · com sinal: %s'
              % (k, v['SIGNAL_COVERS_PCT_OF_CROP'], v['PCT_MEASURED'],
                 ', '.join(v['REGIONS_WITH_SIGNAL']) or '—'))
    print('->', os.path.relpath(DEST, ROOT))


if __name__ == '__main__':
    main()
