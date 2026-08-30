#!/usr/bin/env python3
"""
ITÁLIA — o calendário da LOTTA OBBLIGATORIA contra o vetor da flavescência dourada.

Este arquivo responde a pergunta que a rodada anterior deixou aberta e que ela mesma
apontou como o menor passo seguinte: **quando, exatamente, a obrigação acontece.**

Por que a resposta não podia ser inventada a partir do boletim: o boletim de campo dá a
janela de RECONHECIMENTO DE SINTOMA. A obrigação de tratar o vetor é outro ato, com outra
data, e está em decreto regional. As duas coisas foram medidas separadamente e as duas
entram separadas.

AS DUAS REGIÕES NÃO PUBLICAM DO MESMO JEITO, e isso é o achado estrutural:

    LOMBARDIA  as datas estão DENTRO do decreto. Um documento resolve.
    VÊNETO     o decreto NÃO traz datas: delega ao boletim semanal, que as fixa pela
               fenologia observada dos estádios juvenis do inseto. Dois documentos, e o
               segundo muda toda semana.

Quem tratar "o calendário italiano" como uma coisa só vai errar em uma das duas.

RECORRÊNCIA — o que se pode e o que não se pode dizer sobre 2027:

    A OBRIGAÇÃO recorre: vem do Reg. (UE) 2022/1630 art. 4 e do estatuto de organismo
    de quarentena. Isso é norma permanente, não decisão anual.

    As DATAS não recorrem: são fixadas a cada ano pelo monitoramento. O decreto lombardo
    de 2026 diz explicitamente que a estação **antecipou** o ciclo do escafoide — ou seja,
    a própria fonte avisa que 2026 não é régua para 2027.

Por isso `NEXT_2027_WINDOW = TO_BE_CONFIRMED`, e projetar as datas de 2026 sobre 2027
seria exatamente o erro que a fonte adverte.
"""
import datetime
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DEST = os.path.join(ROOT, 'data', 'samples', 'IT-T3-LOTTA',
                    'IT-lotta-obbligatoria-flavescenza-2026.json')

HOJE = datetime.date(2026, 8, 30)


def registros():
    return [
        {
            'REGION': 'Lombardia', 'NUTS2': 'ITC4', 'YEAR': 2026,
            'TARGET': 'Scaphoideus titanus (vetor de Grapevine flavescence dorée phytoplasma)',
            'OBLIGATION_SCOPE': 'tutto il territorio vitato regionale',
            'LEGAL_TECHNICAL_BASIS': [
                'Reg. (UE) 2016/2031', 'Reg. Esecuzione (UE) 2019/2072',
                'Reg. Esecuzione (UE) 2022/1630, art. 4',
                'D.lgs. 2/02/2021 n. 19', 'D.lgs. 2/02/2021 n. 16',
                'Ordinanza Direttore Servizio Fitosanitario Centrale n. 4 del 22/06/2023',
                'd.d.s. 16/06/2023 n. 9055 (Lombardia)'],
            'ACT': 'Comunicato Regionale Giunta 25 maggio 2026 - n. 39',
            'PUBLICATION': 'BURL Serie Ordinaria n. 22 — 28 maggio 2026',
            'PUBLICATION_DATE': '2026-05-28',
            'NUMBER_OF_TREATMENTS': {
                '2_TRATTAMENTI': 'tutti i restanti vigneti del territorio regionale',
                '3_TRATTAMENTI': ('vigneti a produzione biologica (Reg. UE 2018/848) e '
                                  'aziende non biologiche che usino solo prodotti ammessi '
                                  'in biologico')},
            'MANDATORY_TREATMENT_WINDOWS': [
                {'REGIME': '2 trattamenti', 'N': 1, 'START': '2026-06-02', 'END': '2026-06-14'},
                {'REGIME': '2 trattamenti', 'N': 2, 'START': '2026-06-17', 'END': '2026-06-29',
                 'NOTE': 'intervallo di circa 14 giorni tra i due'},
                {'REGIME': '3 trattamenti', 'N': 1, 'START': '2026-06-02', 'END': '2026-06-14'},
                {'REGIME': '3 trattamenti', 'N': '2-3', 'START': None, 'END': None,
                 'NOTE': 'i successivi ogni 10-14 giorni'}],
            'DATES_IN_ACT': True,
            'PRODUCT_ELIGIBILITY_RULE': (
                'sono ammessi ESCLUSIVAMENTE i prodotti fitosanitari che riportano come '
                'target in etichetta la dicitura generica «cicaline della vite» oppure '
                '«Scaphoideus titanus»'),
            'ADDITIONAL_CONSTRAINT': (
                'divieto di applicazione degli insetticidi durante la fioritura della '
                'coltura e della vegetazione sottostante, a tutela dei pronubi'),
            'SEASON_NOTE_FROM_SOURCE': (
                "l'atto registra che l'andamento stagionale ha ANTICIPATO il ciclo "
                'biologico dello scafoideo — a própria fonte adverte contra usar 2026 '
                'como régua'),
            'SOURCE_URL': ('https://www.fitosanitario.regione.lombardia.it/wps/wcm/connect/'
                           '70acc4d9-a288-47a7-ae3a-7be791482aa6/Comunicato+Regionale+'
                           'Giunta+25+maggio+2026+-+n.+39.pdf'),
        },
        {
            'REGION': 'Veneto', 'NUTS2': 'ITH3', 'YEAR': 2026,
            'TARGET': 'Scaphoideus titanus (vetor de Grapevine flavescence dorée phytoplasma)',
            'OBLIGATION_SCOPE': ('Area Delimitata in eradicazione, confermata dal DDR n. 35 '
                                 "dell'8 maggio 2024 (Allegati A, B, C); obbligo dal primo "
                                 "anno di impianto del vigneto"),
            'LEGAL_TECHNICAL_BASIS': [
                'Reg. (UE) 2016/2031', 'Reg. (UE) 2017/625',
                'Reg. Esecuzione (UE) 2019/2072', 'Reg. Esecuzione (UE) 2022/1630',
                'D.M. 6 giugno 2023 (G.U. 11/08/2023 n. 187)',
                'Ordinanza Direttore SFC n. 4 del 22/06/2023 (G.U. 12/08/2023 n. 188)',
                'Documento tecnico ufficiale del Servizio Fitosanitario Nazionale n. 29 '
                'del 23/12/2022', 'L.R. Veneto n. 1 del 10/01/1997'],
            'ACT': 'Decreto Direttoriale (DDR) n. 13645 del 14 maggio 2026',
            'PUBLICATION_DATE': '2026-05-14',
            'NUMBER_OF_TREATMENTS': {
                '2_INTERVENTI': ('vigneti in gestione integrata, se entrambi con sostanze '
                                 'attive DI SINTESI ammesse'),
                '3_INTERVENTI': ('gestione integrata con sostanze non di sintesi; e gestione '
                                 'biologica (Reg. UE 2018/848)')},
            'ADMITTED_SYNTHETIC_ACTIVES': [
                'Acetamiprid', 'Deltametrina', 'Esfenvalerate', 'Etofenprox',
                'Flupyradifurone', 'Lambda-cialotrina', 'Sulfoxaflor', 'Tau-fluvalinate'],
            'ADMITTED_ORGANIC_ACTIVES': [
                'Azadiractina', 'Beauveria bassiana', 'Olio essenziale di arancio',
                'Maltodestrina', 'Piretrine', 'Sali potassici di acidi grassi',
                'Silicato di alluminio'],
            'RESISTANCE_STRATEGY_RECOMMENDED': {
                '1_TRATTAMENTO': ['Acetamiprid', 'Deltametrina', 'Esfenvalerate',
                                  'Etofenprox', 'Flupyradifurone', 'Lambda-cialotrina',
                                  'Sulfoxaflor', 'Tau-fluvalinate'],
                '2_TRATTAMENTO': ['Deltametrina', 'Esfenvalerate', 'Etofenprox',
                                  'Lambda-cialotrina', 'Tau-fluvalinate']},
            'DATES_IN_ACT': False,
            'DATE_MECHANISM': (
                "le tempistiche sono stabilite dall'U.O. Fitosanitario in base "
                "all'evoluzione della fenologia degli stadi giovanili dell'insetto e "
                'comunicate nei Bollettini settimanali di Difesa Integrata della vite'),
            'MANDATORY_TREATMENT_WINDOWS': [
                {'REGIME': '3 trattamenti (biologica e mista)', 'N': 1,
                 'START': '2026-06-01', 'END': '2026-06-11',
                 'SOURCE': 'Bollettino vite n. 8 del 28/05/2026'},
                {'REGIME': '3 trattamenti (biologica e mista)', 'N': '2-3',
                 'NOTE': 'entro 7-12 giorni dal precedente',
                 'SOURCE': 'Bollettino vite n. 8 del 28/05/2026'},
                {'REGIME': '2 trattamenti (integrata, sostanze di sintesi)', 'N': 1,
                 'START': '2026-06-08', 'END': '2026-06-19',
                 'SOURCE': 'Bollettino vite n. 10 del 10/06/2026'},
                {'REGIME': '2 trattamenti (integrata, sostanze di sintesi)', 'N': 2,
                 'NOTE': 'entro 10-15 giorni dal primo trattamento',
                 'SOURCE': 'Bollettino vite n. 10 del 10/06/2026'}],
            'WINDOWS_DEFINED_WITH': ('Referenti scientifici della Regione: Dafnae-UniPD, '
                                     'DB-UniVR, CREA-VE'),
            'SOURCE_URL': ('https://www.regione.veneto.it/documents/11979050/14370880/'
                           'DDR_13645+14-05-2026.pdf'),
        },
    ]


def estado_da_janela(regs, hoje=HOJE):
    ult = []
    for r in regs:
        fins = [w.get('END') for w in r['MANDATORY_TREATMENT_WINDOWS'] if w.get('END')]
        ult.append(max(fins) if fins else None)
    fim = max([u for u in ult if u] or [None])
    return {
        'AS_OF': hoje.isoformat(),
        'LAST_MANDATORY_WINDOW_END_OBSERVED': fim,
        'VECTOR_CONTROL_WINDOW_2026': 'CLOSED' if fim and fim < hoje.isoformat() else 'NOT_KNOWN',
        'WHY': ('todas as janelas obrigatórias medidas nas duas regiões terminam em junho '
                'de 2026. Em 30/08 a janela de aplicação ao vetor está fechada — e é nela '
                'que o produto atua.'),
    }


def main():
    regs = registros()
    out = {
        'COUNTRY': 'IT', 'SOURCE_ID': 'IT-T3-LOTTA-OBBLIGATORIA',
        'SOURCE': ('decretos/comunicados regionais de lotta obbligatoria + bollettini '
                   'settimanali di difesa integrata (Lombardia, Veneto)'),
        'CAPTURED_AT': datetime.date.today().isoformat(),
        'EVIDENCE_CLASS': 'REGULATORY_FACT',
        'SOURCE_LOCATION': 'ITALY', 'FACT_LOCATION': 'ITALY', 'ORIGINAL_LANGUAGE': 'IT',
        'PUBLICATION_MODEL_DIFFERS_BY_REGION': {
            'LOMBARDIA': 'datas DENTRO do decreto',
            'VENETO': 'decreto delega ao boletim semanal, que fixa pela fenologia observada',
            'CONSEQUENCE': ('não existe "o calendário italiano": existe um por região, e '
                            'com mecanismos de publicação diferentes')},
        'REGIONS': regs,
        'WINDOW_STATE': estado_da_janela(regs),
        'CURRENT_MANDATORY_ACTION_AUGUST': {
            'ACTION': ('capitozzatura o estirpazione tempestiva delle viti con sintomi da '
                       'Giallumi (FD e LN)'),
            'SOURCE': 'Bollettino vite Veneto n. 19 del 13/08/2026',
            'NATURE': ('obrigação em vigor AGORA, mas NÃO é ação de produto: é remoção de '
                       'planta sintomática. Nenhum produto da ADAMA responde a ela.')},
        'RECURRENCE': {
            'OBLIGATION': 'SUSTAINED — Reg. (UE) 2022/1630 art. 4 + estatuto de quarentena',
            'DATES': 'NOT_RECURRENT — fixadas a cada ano pelo monitoramento',
            'NEXT_2027_WINDOW': 'TO_BE_CONFIRMED',
            'WHY_NOT_PROJECTED': ('o próprio ato lombardo de 2026 registra que a estação '
                                  'ANTECIPOU o ciclo do escafoide. Projetar 2026 sobre 2027 '
                                  'seria ignorar o aviso da fonte.'),
            'DEFENSIBLE_ANCHOR': ('em 2026 as janelas caíram na PRIMEIRA METADE DE JUNHO nas '
                                  'duas regiões. Isso permite dizer PREPARE_BY, não '
                                  'EXPECTED_CONTROL_WINDOW com data.'),
            'PREPARE_BY': '2027-05-31',
            'PREPARE_BY_BASIS': ('as duas regiões publicaram o ato em maio (Lombardia '
                                 '28/05, Vêneto 14/05); estar pronto antes do fim de maio '
                                 'é condição para acompanhar a janela, não previsão dela')},
    }
    os.makedirs(os.path.dirname(DEST), exist_ok=True)
    with open(DEST, 'w', encoding='utf-8') as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    print('LOTTA OBBLIGATORIA — flavescência dourada, 2026')
    for r in regs:
        print('\n%s (%s) · ato: %s · datas no ato: %s' % (
            r['REGION'], r['NUTS2'], r['ACT'], r['DATES_IN_ACT']))
        for w in r['MANDATORY_TREATMENT_WINDOWS']:
            print('   %-42s %s → %s %s' % (w['REGIME'] + ' n.' + str(w['N']),
                                           w.get('START') or '—', w.get('END') or '—',
                                           w.get('NOTE', '')[:44]))
    print('\n%s' % out['WINDOW_STATE']['VECTOR_CONTROL_WINDOW_2026'])
    print('->', os.path.relpath(DEST, ROOT))


if __name__ == '__main__':
    main()
