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
               più redatta" — competência transferida à ARIF, que hoje É a editora
               do notiziario e mesmo assim não restaurou a seção.

               ATENÇÃO AO ALCANCE DESTA LINHA: ela mede a CAMADA REGIONAL. O sinal
               de olivo da Puglia existe fora dela — a APOL, de Lecce, mantém série
               semanal numerada com edições de 2026. `SOURCE_LAYER ≠ SIGNAL_ABSENCE`.
               Ver `italia_camada_op.py`. A inversão contra o Vêneto sobrevive como
               comparação entre SERVIÇOS REGIONAIS; a leitura "não há sinal de olivo
               na Puglia", não.

    MILHO      FVG tem 6,7% da área e publica 10 boletins de MAIS em 2026.
               Vêneto tem 24,8% e o serviço fitossanitário publica ZERO — seus dois
               boletins de herbáceas de 2026 são trigo (março) e beterraba (junho).
               Mas a AVISP publica outra série, que trata de milho, e da qual duas
               edições foram lidas. Sem índice enumerável, o Vêneto não entra nem
               na cobertura nem no denominador: fica nomeado, fora dos dois.

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
         'ALTERNATIVE_ROUTE': ('organizações de produtores. CORRIGIDO em 2026-08-30: eu '
                               'tinha registrado que as edições em HTML alcançável '
                               'paravam em 2024. Isso vale para a Assoproli Bari '
                               '(mais recente 10/06/2024, rota legível), mas NÃO para a '
                               'APOL de Lecce, que mantém série numerada semanal de '
                               'mosca-da-azeitona com edições de 2026 (n.1 de 13–19/07, '
                               'n.2 de 20–26/07). O conteúdo da APOL não foi lido — '
                               'apol.it devolve 503 daqui —, então isto é '
                               'EXISTS_ROUTE_NOT_READABLE e NÃO entra em cobertura. '
                               'Ver IT-T3-OP em ITALY-OP-FIELD-LAYER.json.'),
         'NOTE': ('CORREÇÃO. Eu tinha anotado a competência como "em fase de '
                  'transferência". Medido em 2026-08-30: a ARIF É a editora do '
                  'notiziario, publicado semanalmente às quartas. A transferência se '
                  'completou E a seção de fitopatologia continua não redigida, oito anos '
                  'depois — não é transição em curso, é ausência estabilizada. '
                  'A linha continua com 0 boletins porque o que se mede aqui é a rota '
                  'REGIONAL; o sinal existe fora dela, e SOURCE_LAYER ≠ SIGNAL_ABSENCE.'),
         'STATE_LAYER': 'REGIONAL_SERVICE',
         'SIGNAL_EXISTS_IN_ANOTHER_LAYER': True},
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
         'BULLETINS_2026_MEASURED': None,
         'ROUTE_TRIED': ('regione.veneto.it (serviço fitossanitário) E '
                         'venetoagricoltura.org (Avisp) — duas rotas, dois resultados'),
         'STATE': 'BULLETIN_EXISTS_ROUTE_NOT_READABLE',
         'NOTE': ('CORREÇÃO EM DOIS TEMPOS. (1) A rota do SERVIÇO FITOSSANITÁRIO publica 2 '
                  'boletins de herbáceas em 2026 — frumento (n.01, 06/03) e beterraba '
                  '(n.02, 05/06) —, nenhum de milho, contra 28 de olivo e 16 de vite. '
                  '(2) Existe uma SEGUNDA rota: a AVISP/Veneto Agricoltura publica o '
                  '"Bollettino Colture Erbacee", numerado e semanal, com edições dedicadas '
                  'à PIRALIDE DO MILHO (n.42 de 15/07/2022, n.40 de 19/07/2024, n.4 de '
                  '20/01/2025) e página de tópico atualizada em 20/05/2026. O portal é um '
                  'SPA Angular que não renderiza no servidor, mas o endpoint de download '
                  'por ID (ver DOWNLOAD_ROUTE) devolve o PDF real, e DUAS edições foram '
                  'lidas nesta branch. O que continua faltando NÃO é o conteúdo de uma '
                  'edição — é o ÍNDICE: não há listagem enumerável, então o número de '
                  'edições de milho de 2026 permanece não medido, e a linha fica fora da '
                  'cobertura E fora do denominador. Ler duas edições não é medir uma série.'),
         'EXISTENCE_EVIDENCE': ('títulos e datas indexados de edições que tratam de '
                                'piralide do mais, MAIS o conteúdo integral de duas '
                                'edições lidas por ID'),
         'CONTENT_STATE': 'PARTIALLY_READ_TWO_EDITIONS_NO_ENUMERABLE_INDEX',
         'DOWNLOAD_ROUTE': ('venetoagricoltura.org/myportal/AVPISP/api/content/download'
                            '?id=<id> — devolve o PDF; o <id> só aparece em resultado de '
                            'busca pública, não há endpoint de listagem alcançável'),
         'EDITIONS_READ': [
             {'TITLE': 'Bollettino n. 53 — MICOTOSSINE NEL MAIS',
              'YEAR': 'NÃO SEI — o ano não foi registrado na leitura',
              'CONTENT': ('risco sazonal de micotoxina calculado pelo DSS Mais.net da Horta '
                          'sobre as estações das aziende da Veneto Agricoltura; risco de '
                          'AFLATOSSINA declarado ALTO em todas as estações e de FUMONISINA '
                          'de médio-alto a alto; projeto com o CREA-CI verificando o nível '
                          'de infecção das sedas (stigmi)'),
              'WHY_IT_MATTERS': ('é sinal de campo de MILHO no Vêneto, georreferenciado por '
                                 'estação e ligado a um DSS nomeado — exatamente a classe '
                                 'de sinal que eu havia declarado ausente na região')},
             {'TITLE': 'Bollettino n. 18/2025 — NOTTUE',
              'YEAR': '2025',
              'CONTENT': ('primeira captura de Agrotis ipsilon em Cartura (PD) em '
                          '03/03/2025; modelo de graus-dia (Tmax−Tmin)/2 − 10,4 °C'),
              'WHY_IT_MATTERS': ('confirma série numerada, contínua e com limiar fenológico '
                                 '— não é boletim ocasional')}],
         'RAW_EVIDENCE_STATE': 'NOT_PRESERVED',
         'RAW_EVIDENCE_CONFESSION': ('os dois PDFs foram lidos em sessão e NÃO foram '
                                     'gravados em data/raw antes de a rota deixar de estar '
                                     'disponível neste ambiente. Segundo o contrato de '
                                     'scripts/proveniencia.py, NOT_PRESERVED é confissão: '
                                     'o dado existiu e não foi guardado. O resumo acima é '
                                     'testemunho de leitura, não evidência re-verificável, '
                                     'e por isso NÃO sustenta nenhuma métrica. Re-obter e '
                                     'preservar está no handoff de navegador local.')},
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
    """Mede se o sinal está onde a cultura está. Só compara linhas MEDIDAS.

    TRÊS estados, não dois. A rodada de coleta nacional forçou a distinção: o Vêneto
    NÃO publica boletim de milho pelo serviço fitossanitário, mas a AVISP publica um
    — e o conteúdo não é legível daqui. Contá-lo como "sem sinal" seria repetir, com
    outro nome, o erro do FVG: confundir rota não lida com ausência.

        publica              entra na cobertura
        não publica          entra no denominador, fora da cobertura
        existe e não lido    fica FORA DOS DOIS, e nomeado
    """
    todos = [x for x in ls if x['CROP'] == cultura]
    med = [x for x in todos if x['BULLETINS_2026_MEASURED'] is not None]
    naolido = [x for x in todos
               if x.get('STATE') == 'BULLETIN_EXISTS_ROUTE_NOT_READABLE']
    if not med:
        return None
    com = [x for x in med if x['BULLETINS_2026_MEASURED'] > 0]
    sem = [x for x in med if x['BULLETINS_2026_MEASURED'] == 0]
    return {
        'REGIONS_MEASURED': len(med),
        'REGIONS_BULLETIN_EXISTS_NOT_READ': [x['REGION'] for x in naolido],
        'PCT_NATIONAL_EXISTS_NOT_READ': round(sum(x['PCT_NATIONAL'] for x in naolido), 1),
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
        'LAW_ADDED_2026_08_30': ('EDIÇÃO LIDA ≠ SÉRIE MEDIDA. Ter lido duas edições da série '
                                 'da AVISP prova que a série existe e é sobre milho; não '
                                 'diz quantas edições de 2026 existem. Sem índice '
                                 'enumerável não há denominador, e sem denominador não há '
                                 'cobertura. A tentação de promover o Vêneto a '
                                 '"coberto" porque agora eu li algo é exatamente o erro '
                                 'que COBERTURA ALTA ≠ COBERTURA CORRETA nomeia.'),
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
