#!/usr/bin/env python3
"""
ITÁLIA — a camada de campo não cobre onde a cultura está.

Este arquivo mede uma coisa só, e ela é estrutural: **a cobertura pública de sinal de
campo na Itália não é proporcional à área da cultura.** Não é uma impressão — é a
comparação entre duas medições que já existiam separadas, a área regional (`IT-T1-001`) e
os boletins publicados por cada serviço regional em 2026.

O resultado inverte a intuição em duas culturas ao mesmo tempo:

    OLIVEIRA   Vêneto tem 0,5% da área e publica 28 boletins de olivo em 2026.
               Puglia tem 31,2% e o portal agrometeo regional declara, desde
               11/04/2018, que "la sezione dedicata alla Fitopatologia non viene
               più redatta" — competência em transferência para a ARIF.

    MILHO      FVG tem 6,7% da área e publica 10 boletins de MAIS em 2026.
               Vêneto tem 24,8% e publica ZERO — seus dois boletins de herbáceas
               de 2026 são trigo (março) e beterraba (junho).

A LEI QUE ESTE ARQUIVO OBEDECE, e que já foi violada uma vez nesta branch:

    `NOT_OBTAINED ≠ DOES NOT EXIST`

O caso do milho do FVG é a prova: eu publiquei `MAIZE_FIELD_SIGNAL = NOT_FOUND` porque
tinha lido a página-mãe das *colture erbacee* e não a subpágina `bollettini-2026`. Existia,
com 10 números. Por isso aqui **nada** é declarado inexistente: cada linha diz qual rota
foi tentada e o que ela devolveu.

O que isto significa para quem usa: um sistema de inteligência que dependa só de boletim
oficial vai enxergar bem a cultura errada. A Itália obriga a declarar, junto com o sinal,
**qual fatia da cultura aquele sinal representa**.
"""
import datetime
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DEST = os.path.join(ROOT, 'data', 'samples', 'IT-T3-LOTTA',
                    'IT-cobertura-campo-vs-area.json')


def linhas():
    return [
        # ---------------------------------------------------------------- OLIVEIRA
        {'CROP': 'Oliveira', 'REGION': 'Puglia', 'NUTS2': 'ITF4',
         'AREA_THS_HA': 347.8, 'PCT_NATIONAL': 31.2, 'AREA_RANK': 1,
         'BULLETINS_2026_MEASURED': 0,
         'ROUTE_TRIED': 'agrometeopuglia.it/bollettini (portal agrometeo regional)',
         'WHAT_THE_SOURCE_SAYS': ('"Dal Notiziario Agrometeorologico Regionale n. 15 del '
                                  '11/04/2018, la sezione dedicata alla Fitopatologia non '
                                  'viene più redatta poiché le competenze sono in fase di '
                                  'trasferimento all\'Agenzia Regionale Attività Irrigue e '
                                  'Forestali (ARIF)" — Legge Regionale n. 33'),
         'STATE': 'NO_PHYTOPATHOLOGY_IN_REGIONAL_NEWSLETTER_SINCE_2018',
         'ALTERNATIVE_ROUTE': ('organizações de produtores (Assoproli Bari, A.P.OL, Aproli) '
                               'publicam boletins de mosca-da-azeitona; os expostos em HTML '
                               'alcançável estão datados de 2024'),
         'NOTE': ('a transferência de competência ainda é descrita como "in fase di" na '
                  'página tal como obtida hoje, oito anos depois')},
        {'CROP': 'Oliveira', 'REGION': 'Calabria', 'NUTS2': 'ITF6',
         'AREA_THS_HA': 184.7, 'PCT_NATIONAL': 16.6, 'AREA_RANK': 2,
         'BULLETINS_2026_MEASURED': None, 'ROUTE_TRIED': None,
         'STATE': 'NOT_MEASURED'},
        {'CROP': 'Oliveira', 'REGION': 'Sicilia', 'NUTS2': 'ITG1',
         'AREA_THS_HA': 161.7, 'PCT_NATIONAL': 14.5, 'AREA_RANK': 3,
         'BULLETINS_2026_MEASURED': None, 'ROUTE_TRIED': None,
         'STATE': 'NOT_MEASURED'},
        {'CROP': 'Oliveira', 'REGION': 'Veneto', 'NUTS2': 'ITH3',
         'AREA_THS_HA': 5.3, 'PCT_NATIONAL': 0.5, 'AREA_RANK': 12,
         'BULLETINS_2026_MEASURED': 28,
         'ROUTE_TRIED': 'regione.veneto.it/web/fitosanitario/bollettini-fitosanitari-2026',
         'STATE': 'PUBLISHED_WEEKLY',
         'NOTE': ('o boletim n. 28 de 26/08/2026 traz fenologia observada e pressão de '
                  'Bactrocera em 11 sub-áreas nomeadas — é o sinal mais fino do país')},
        # ------------------------------------------------------------------- MILHO
        {'CROP': 'Milho grão', 'REGION': 'Veneto', 'NUTS2': 'ITH3',
         'AREA_THS_HA': 122.9, 'PCT_NATIONAL': 24.8, 'AREA_RANK': 1,
         'BULLETINS_2026_MEASURED': 0,
         'ROUTE_TRIED': 'regione.veneto.it/web/fitosanitario/bollettini-fitosanitari-2026',
         'STATE': 'NO_MAIZE_BULLETIN_IN_ROUTE_MEASURED',
         'NOTE': ('os dois boletins de "colture erbacee ed industriali" de 2026 são '
                  'frumento (n. 01, 06/03) e barbabietola/Cercospora (n. 02, 05/06). '
                  'A mesma região publicou 28 de olivo, 25 de frutícola, 21 de hortícola '
                  'e 16 de vite.')},
        {'CROP': 'Milho grão', 'REGION': 'Lombardia', 'NUTS2': 'ITC4',
         'AREA_THS_HA': 115.8, 'PCT_NATIONAL': 23.4, 'AREA_RANK': 2,
         'BULLETINS_2026_MEASURED': 0,
         'ROUTE_TRIED': 'fitosanitario.regione.lombardia.it — bollettini fitosanitari',
         'STATE': 'NO_MAIZE_BULLETIN_IN_ROUTE_MEASURED',
         'NOTE': 'a rota medida publica apenas vite (6) e melo (4) em 2026'},
        {'CROP': 'Milho grão', 'REGION': 'Piemonte', 'NUTS2': 'ITC1',
         'AREA_THS_HA': 115.7, 'PCT_NATIONAL': 23.4, 'AREA_RANK': 3,
         'BULLETINS_2026_MEASURED': None,
         'ROUTE_TRIED': 'regione.piemonte.it — bacheca dei bollettini',
         'STATE': 'NOT_OBTAINED',
         'NOTE': ('a bacheca é renderizada por JavaScript: o HTML obtido não traz PDF nem '
                  'nome de cultura. NÃO é ausência — é rota não lida.')},
        {'CROP': 'Milho grão', 'REGION': 'Friuli-Venezia Giulia', 'NUTS2': 'ITH4',
         'AREA_THS_HA': 33.1, 'PCT_NATIONAL': 6.7, 'AREA_RANK': 5,
         'BULLETINS_2026_MEASURED': 10,
         'ROUTE_TRIED': ('difesafitosanitaria.ersa.fvg.it — colture-erbacee-orticole/'
                         'bollettini-2026'),
         'STATE': 'PUBLISHED_REGULARLY',
         'NOTE': ('série dedicada ao MAIS sob difesa integrata obbligatoria (art. 19 '
                  'D.lgs. 150/2012); último n. 15 de 12/08/2026, com BBCH e limiar')},
    ]


def inversao(ls, cultura):
    """Mede se o sinal está onde a cultura está. Só compara linhas MEDIDAS."""
    med = [x for x in ls if x['CROP'] == cultura and x['BULLETINS_2026_MEASURED'] is not None]
    if not med:
        return None
    com = [x for x in med if x['BULLETINS_2026_MEASURED'] > 0]
    sem = [x for x in med if x['BULLETINS_2026_MEASURED'] == 0]
    return {
        'REGIONS_MEASURED': len(med),
        'REGIONS_PUBLISHING': [x['REGION'] for x in com],
        'REGIONS_NOT_PUBLISHING': [x['REGION'] for x in sem],
        'PCT_NATIONAL_COVERED_BY_SIGNAL': round(sum(x['PCT_NATIONAL'] for x in com), 1),
        'PCT_NATIONAL_MEASURED_WITHOUT_SIGNAL': round(sum(x['PCT_NATIONAL'] for x in sem), 1),
        'INVERTED': bool(com and sem
                         and max(x['PCT_NATIONAL'] for x in sem)
                         > max(x['PCT_NATIONAL'] for x in com)),
    }


def main():
    ls = linhas()
    out = {
        'COUNTRY': 'IT', 'SOURCE_ID': 'DERIVED/IT-FIELD-COVERAGE',
        'SOURCE': ('IT-T1-001 (área regional ISTAT) × IT-T3-002/003/005/006 e portal '
                   'agrometeo da Puglia (boletins publicados em 2026)'),
        'CAPTURED_AT': datetime.date.today().isoformat(),
        'AS_OF': '2026-08-30',
        'EVIDENCE_CLASS': 'DERIVED_INTERPRETATION',
        'QUESTION': 'a camada pública de sinal de campo cobre onde a cultura está?',
        'ANSWER': 'não, e a inversão é medida em duas culturas',
        'LAW_OBEYED': ('NOT_OBTAINED ≠ DOES NOT EXIST — cada linha declara a rota tentada. '
                       'Nada aqui é declarado inexistente.'),
        'BY_CROP': {c: inversao(ls, c) for c in ('Oliveira', 'Milho grão')},
        'ROWS': ls,
        'CONSEQUENCE': ('um sistema que dependa só de boletim oficial enxerga bem a cultura '
                        'errada. Todo sinal de campo italiano tem de ser publicado junto '
                        'com a fatia da cultura que ele representa.'),
        'WHAT_THIS_DOES_NOT_PROVE': [
            'que não exista sinal nas regiões não medidas',
            'que a ausência de boletim signifique ausência de problema',
            'que as regiões que publicam tenham mais pressão'],
    }
    os.makedirs(os.path.dirname(DEST), exist_ok=True)
    with open(DEST, 'w', encoding='utf-8') as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    for c, d in out['BY_CROP'].items():
        print('%s: sinal cobre %.1f%% da área medida; %.1f%% medido sem sinal · invertido=%s'
              % (c, d['PCT_NATIONAL_COVERED_BY_SIGNAL'],
                 d['PCT_NATIONAL_MEASURED_WITHOUT_SIGNAL'], d['INVERTED']))
        print('   publicam: %s' % ', '.join(d['REGIONS_PUBLISHING']))
        print('   não publicam: %s' % ', '.join(d['REGIONS_NOT_PUBLISHING']))
    print('->', os.path.relpath(DEST, ROOT))


if __name__ == '__main__':
    main()
