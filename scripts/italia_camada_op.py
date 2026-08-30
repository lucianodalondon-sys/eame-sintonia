#!/usr/bin/env python3
"""
ITÁLIA — o sinal de campo do olivo mudou de dono, e eu estava olhando o dono antigo.

A frase que eu publiquei e que precisa ser corrigida:

    "Puglia tem 31,2 % da área de oliveira e publica ZERO boletins."

O que é verdade é mais estreito e mais interessante:

    O SERVIÇO REGIONAL da Puglia não publica fitopatologia desde 11/04/2018 — e a ARIF,
    a agência para a qual a competência foi transferida, HOJE É A EDITORA do notiziario
    e MESMO ASSIM não restaurou a seção. Oito anos.

    Mas o sinal existe. Ele migrou para as ORGANIZAÇÕES DE PRODUTORES.

O QUE FOI MEDIDO
----------------
`Assoprol Umbria` publica *Bollettino Fitosanitario Olivo 2026 — Monitoraggio mosca
delle olive n. 3*, válido de 6 a 10 de julho de 2026, e o conteúdo **foi lido**:

  · capturas em armadilha ("i primi voli degli adulti della mosca delle olive, seppur
    ancora con catture limitate sull'intero territorio regionale");
  · **fase fenológica BBCH 71-75**, "drupe in accrescimento e indurimento del nocciolo
    non ancora completato";
  · recomendação condicional — caolino para o biológico; adulticida se as capturas
    subirem;
  · e, o que mais vale, **o boletim declara o próprio limite**: "in questa fase non sono
    ancora stati effettuati i campionamenti per la verifica dell'infestazione attiva".
    Uma fonte que separa o que mediu do que ainda não mediu é fonte de qualidade alta.

`APOL` (Lecce, **Puglia**) publica série numerada semanal de mosca-da-azeitona com
edições de **2026** (n.1 de 13–19/07, n.2 de 20–26/07) e de 2025. A **existência** está
provada pelo índice de busca, com número e período de validade. O **conteúdo não foi
lido**: `apol.it` devolve 503 de forma consistente deste ambiente.

A LEI QUE ISTO OBRIGA A APLICAR CONTRA UM ACHADO MEU
-----------------------------------------------------
    SOURCE_LAYER ≠ SIGNAL_ABSENCE

Medir a camada estatal e concluir "não há sinal" é o mesmo erro de painel do trigo duro,
um nível acima: lá eu tinha perguntado às regiões erradas; aqui eu perguntei à
**instituição errada** dentro da região certa.

A inversão olivícola **não morre — ela se estreita**. Continua verdade que o serviço
regional do Vêneto publica 28 boletins de olivo com 0,5 % da área enquanto o serviço
regional da Puglia, com 31,2 %, publica zero. O que deixa de ser verdade é a leitura
"na Puglia não há sinal de olivo". Há, e sai da OP.

E o que isso **não** autoriza a dizer: que a Puglia esteja bem coberta. Eu não li o
conteúdo do APOL. `EXISTS_ROUTE_NOT_READABLE` não entra em cobertura — nem como zero.
"""
import datetime
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DEST = os.path.join(ROOT, 'data', 'samples', 'IT-FONTES', 'ITALY-OP-FIELD-LAYER.json')


def fontes():
    return [
        {'ORG': 'Assoprol Umbria', 'ORG_KIND': 'ORGANIZACAO_DE_PRODUTORES',
         'REGION': 'Umbria', 'CROP': 'Oliveira', 'ISSUE': 'Bactrocera oleae',
         'ROUTE': 'assoprol.it — bollettino fitosanitario olivo',
         'STATE': 'CONTENT_READ',
         'MOST_RECENT_READ': {'TITLE': 'Bollettino Fitosanitario Olivo 2026 — '
                                       'Monitoraggio mosca delle olive n. 3',
                              'VALIDITY': 'dal 6 al 10 luglio 2026',
                              'AREA': 'intero territorio regionale (Umbria)'},
         'SIGNAL_FIELDS': ['catture in trappola', 'fase fenologica BBCH 71-75',
                           'raccomandazione condizional'],
         'BBCH': '71-75',
         'DECLARES_OWN_LIMIT': True,
         'DECLARED_LIMIT_IT': ('in questa fase non sono ancora stati effettuati i '
                               'campionamenti per la verifica dell\'infestazione attiva'),
         'WHY_THAT_MATTERS': ('separa o que mediu do que ainda não mediu. Fonte que '
                              'declara o próprio limite é fonte de qualidade alta.'),
         'RAW_EVIDENCE_STATE': 'NOT_PRESERVED'},
        {'ORG': 'APOL', 'ORG_KIND': 'ORGANIZACAO_DE_PRODUTORES',
         'REGION': 'Puglia', 'PROVINCE': 'Lecce', 'CROP': 'Oliveira',
         'ISSUE': 'Bactrocera oleae',
         'ROUTE': 'apol.it — Bollettino Mosca dell\'Olivo, série numerada semanal',
         'STATE': 'EXISTS_ROUTE_NOT_READABLE',
         'EXISTENCE_EVIDENCE': ('índice de busca com número E período de validade: '
                                'n.1 de 13–19/07/2026, n.2 de 20–26/07/2026; série de '
                                '2025 com URL de PDF por edição '
                                '(n.11 de 29-09-2025, n.2 de 28-07-2025)'),
         'WHY_NOT_READ': 'apol.it devolve HTTP 503 de forma consistente deste ambiente',
         'ROUTE_FAILURE_IS_NOT_ABSENCE': True},
        {'ORG': 'Assoproli Bari', 'ORG_KIND': 'ORGANIZACAO_DE_PRODUTORES',
         'REGION': 'Puglia', 'PROVINCE': 'Bari', 'CROP': 'Oliveira',
         'ISSUE': 'Bactrocera oleae, Prays oleae',
         'ROUTE': 'assoproli.it/bollettini-fitosanitari',
         'STATE': 'ARCHIVE_READ_BUT_STALE',
         'MOST_RECENT': '10/06/2024',
         'NOTE': ('arquivo alcançável e legível; a edição mais recente exposta é de '
                  'junho de 2024. Isto É medição: a rota respondeu.')},
        {'ORG': 'ARIF Puglia', 'ORG_KIND': 'AGENCIA_REGIONAL',
         'REGION': 'Puglia', 'CROP': '—',
         'ROUTE': 'agrometeopuglia.it/bollettini',
         'STATE': 'PUBLISHES_BUT_NO_PHYTOPATHOLOGY',
         'VERBATIM_IT': ('Dal Notiziario Agrometeorologico Regionale n. 15 del '
                         '11/04/2018, la sezione dedicata alla Fitopatologia non viene '
                         'più redatta'),
         'SHARPENED_2026_08_30': (
             'CORREÇÃO DO MEU PRÓPRIO REGISTRO. Eu tinha anotado a competência como '
             '"em fase de transferência". Medido agora: a ARIF É a editora do '
             'notiziario, publicado semanalmente às quartas — ou seja, a transferência '
             'se completou E a seção de fitopatologia continua não redigida, oito anos '
             'depois. Não é uma transição em curso; é uma ausência estabilizada.'),
         'LEGAL_BASIS': 'Legge Regionale 33/2017'},
    ]


def main():
    fs = fontes()
    lidas = [f for f in fs if f['STATE'] == 'CONTENT_READ']
    existe = [f for f in fs if f['STATE'] == 'EXISTS_ROUTE_NOT_READABLE']

    out = {
        'COUNTRY': 'IT',
        'SOURCE_ID': 'IT-T3-OP',
        'SOURCE': ('organizações de produtores olivícolas — camada de sinal de campo '
                   'fora do serviço regional'),
        'CAPTURED_AT': datetime.date.today().isoformat(),
        'AS_OF': '2026-08-30',
        'SOURCE_LOCATION': 'Umbria e Puglia',
        'FACT_LOCATION': 'ITALY',
        'ORIGINAL_LANGUAGE': 'it',
        'EVIDENCE_CLASS': 'PRIMARY_SOURCE_PROBE',
        'QUESTION': ('quando o serviço regional para de publicar fitopatologia, o sinal '
                     'de campo desaparece ou muda de dono?'),
        'ANSWER': ('muda de dono. Na Puglia a ARIF publica o notiziario e não redige '
                   'fitopatologia desde 2018, e é a APOL — organização de produtores de '
                   'Lecce — que mantém série numerada semanal de mosca-da-azeitona, com '
                   'edições de 2026.'),
        'LAW_ADDED': 'SOURCE_LAYER ≠ SIGNAL_ABSENCE',
        'LAW_NOTE': ('medir a camada estatal e concluir "não há sinal" é o erro de painel '
                     'do trigo duro um nível acima: lá eu perguntei às regiões erradas, '
                     'aqui à INSTITUIÇÃO errada dentro da região certa.'),
        'CORRECTION_TO_MY_OWN_FINDING': {
            'WHAT_I_PUBLISHED': ('Puglia tem 31,2% da área de oliveira e publica ZERO '
                                 'boletins'),
            'WHAT_SURVIVES': ('o SERVIÇO REGIONAL da Puglia publica zero, e a inversão '
                              'contra o Vêneto (28 boletins com 0,5% da área) continua '
                              'de pé como comparação entre serviços regionais'),
            'WHAT_DOES_NOT_SURVIVE': ('a leitura "na Puglia não há sinal de olivo". Há, '
                                      'e sai da organização de produtores'),
            'WHAT_THIS_STILL_DOES_NOT_LICENSE': (
                'dizer que a Puglia está bem coberta. O conteúdo do APOL não foi lido. '
                'EXISTS_ROUTE_NOT_READABLE não entra em cobertura — nem como zero.'),
        },
        'SOURCES': fs,
        'COUNTS': {'TOTAL_PROBED': len(fs), 'CONTENT_READ': len(lidas),
                   'EXISTS_NOT_READABLE': len(existe)},
        'WHAT_THIS_DOES_NOT_PROVE': [
            'que a camada OP cubra a Puglia inteira — a APOL monitora a área de Lecce',
            'que exista camada OP equivalente para trigo duro, milho ou videira; '
            'só a oliveira foi sondada nesta rodada',
            'nada sobre venda, disponibilidade comercial ou prioridade interna',
        ],
    }
    os.makedirs(os.path.dirname(DEST), exist_ok=True)
    with open(DEST, 'w', encoding='utf-8') as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    for f in fs:
        print('%-18s %-9s %-32s %s' % (f['ORG'], f['REGION'], f['STATE'],
                                       f.get('MOST_RECENT') or
                                       (f.get('MOST_RECENT_READ') or {}).get('VALIDITY', '')))
    print('->', os.path.relpath(DEST, ROOT))


if __name__ == '__main__':
    main()
