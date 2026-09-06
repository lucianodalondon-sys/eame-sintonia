#!/usr/bin/env python3
"""
ITÁLIA — expansão do painel de campo do trigo duro. Três regiões novas, zero cobertura nova.

A crítica de painel disse qual era o trabalho: `PANEL_EXPANSION`, começando pelas duas
maiores regiões nunca perguntadas. Perguntei. **E o resultado honesto é que nenhuma das
três moveu a cobertura para cima** — porque em nenhuma delas eu li um boletim de trigo
duro.

Isso não é fracasso: é a diferença entre *abrir a rota* e *ler o sinal*. As três estão
agora com órgão nomeado, rota medida e estado declarado, que é o que faltava. A cobertura
medida de trigo duro continua sendo a Toscana — **3,7 % da área nacional**.

O QUE CADA REGIÃO RESPONDEU
----------------------------
**Sicília — 23,6 % do trigo duro italiano, a maior nunca perguntada.**
O Servizio Fitosanitario Regionale **existe e está ativo em 2026**: aprovou as *Norme
tecniche di difesa integrata* pelo DDG n. 2428 de 16/04/2026 e publica derrogações
datadas. Tem **ficha por cultura, e uma delas é Frumento** (atualizada 23/09/2024). Mas
ficha técnica **não é sinal de campo**: é o que se pode fazer, não o que está
acontecendo esta semana. Nenhum índice de boletim periódico apareceu nas rotas medidas.
O SIAS (agrometeo regional) devolveu **503 em duas tentativas** — parei ali.

    NORMA TÉCNICA ≠ SINAL DE CAMPO

**Basilicata — 9,8 %.**
A ALSIA é o órgão, e o serviço de boletins **foi retomado em janeiro de 2026**
(Metapontino, com Val d'Agri prevista). A página pública de boletins expõe edições até
**2022**, com morango, videira, pêssego, cítricos e tomate — **cereais não aparecem**. E
o acesso às edições correntes é **por cadastro gratuito**: *"Iscrivendosi ai Servizi di
Consulenza on-line dell'Agenzia, è possibile accedere gratuitamente ai Bollettini"*.

Não criei cadastro. Abrir conta em serviço de terceiro é ação para fora, não sondagem de
dado público, e não estava autorizada nesta missão. Fica handoff, com o contato que a
própria página publica.

**Campânia — 4,5 %, achada de passagem e a mais viva das três.**
O Servizio Fitosanitario Regionale publica boletim **por província** — Avellino,
Benevento, Caserta, Napoli, Salerno — e o mais recente é de **26/08/2026**, quatro dias
antes desta medição. É a melhor resolução geográfica achada fora da Toscana. Mas a
lista de culturas não está exposta no índice, e o SIMFITO (a plataforma que permite
escolher ano × área × cultura) **não renderiza no servidor** — mesma classe da bacheca
do Piemonte.

AS TRÊS LEIS QUE ESTE ARQUIVO OBEDECE
--------------------------------------
    ROUTE FAILURE ≠ SIGNAL ABSENCE   — o 503 do SIAS não diz nada sobre a Sicília
    SOURCE ABSENCE ≠ FIELD ABSENCE   — não achar índice não é não haver doença
    ONE REGION ≠ COUNTRY             — a Toscana continua sendo 3,7 %, não a Itália

E a que a Basilicata acrescenta:

    GATED ≠ BLOCKED ≠ ABSENT — conteúdo atrás de cadastro gratuito não é bloqueio nem
    ausência. É uma porta que existe e que eu escolhi não abrir sozinho.
"""
import datetime
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DEST = os.path.join(ROOT, 'data', 'samples', 'IT-T3-LOTTA', 'IT-durum-field-panel.json')

AS_OF = '2026-08-30'


def regioes():
    return [
        {
            'REGION': 'Sicilia', 'NUTS2': 'ITG1',
            'DURUM_THS_HA': 277.5, 'PCT_NATIONAL_DURUM': 23.6, 'DURUM_RANK': 2,
            'BODY': 'Servizio Fitosanitario Regionale — Assessorato Regionale '
                    'dell\'Agricoltura, dello Sviluppo Rurale e della Pesca Mediterranea',
            'ROUTES_TRIED': [
                {'ROUTE': 'regione.sicilia.it — servizio fitosanitario / difesa fitosanitaria',
                 'HTTP': 200,
                 'WHAT_IT_HAS': ('fichas técnicas por cultura (24 culturas, entre elas '
                                 'Frumento, atualizada 23/09/2024), Norme tecniche di '
                                 'difesa integrata aprovadas pelo DDG n. 2428 de '
                                 '16/04/2026, derrogações datadas'),
                 'WHAT_IT_LACKS': 'nenhum índice ou arquivo de boletim periódico'},
                {'ROUTE': 'sias.regione.sicilia.it (agrometeo regional)',
                 'HTTP': 503, 'ATTEMPTS': 2,
                 'WHAT_IT_HAS': 'NÃO SEI — não respondeu',
                 'STOPPED_BECAUSE': 'duas tentativas razoáveis numa rota que falha; '
                                    'não se insiste contra proteção ou indisponibilidade'},
            ],
            'FIELD_SIGNAL_STATE': 'BULLETIN_NOT_FOUND_ON_MEASURED_ROUTES',
            'HAS_2026_REGULATORY_ACTIVITY': True,
            'CROP_NAMED': 'Frumento (em ficha técnica, não em boletim)',
            'ISSUE': 'NÃO SEI — a ficha técnica lista ativos permitidos, não pressão',
            'GEOGRAPHIC_RESOLUTION': 'NÃO SEI',
            'TEMPORAL_RESOLUTION': 'NÃO SEI',
            'SERIES_OR_ISOLATED': 'NÃO SEI',
            'EVIDENCE_STATE': 'NOT_FOUND_ON_MEASURED_ROUTES',
            'RAW_EVIDENCE_STATE': 'NOT_PRESERVED',
            'LAW': 'NORMA TÉCNICA ≠ SINAL DE CAMPO',
            'NOTE': ('a ficha de Frumento prova que a região trata a cultura na sua '
                     'disciplina de produção integrada. Não prova que publique estado '
                     'de lavoura. São coisas diferentes e a segunda é a que falta.'),
        },
        {
            'REGION': 'Basilicata', 'NUTS2': 'ITF5',
            'DURUM_THS_HA': 115.2, 'PCT_NATIONAL_DURUM': 9.8, 'DURUM_RANK': 3,
            'BODY': 'ALSIA — Agenzia Lucana di Sviluppo e di Innovazione in Agricoltura, '
                    'Servizio di Difesa Integrata (SeDI)',
            'ROUTES_TRIED': [
                {'ROUTE': 'alsia.it — tag "ufficio fitosanitario"', 'HTTP': 200,
                 'WHAT_IT_HAS': ('boletins expostos até 2022 (ex.: "Bollettino '
                                 'fitopatologico n. 01/2022 del Metapontino"), culturas '
                                 'morango, videira, pêssego, cítricos, tomate de indústria'),
                 'WHAT_IT_LACKS': 'cereais não aparecem; nada de 2026'},
                {'ROUTE': 'alsia.it — Temi / Difesa Integrata delle colture (SeDI)',
                 'HTTP': 200,
                 'WHAT_IT_HAS': ('serviço ATIVO: "Riparte il servizio dell\'ALSIA di '
                                 'diffusione dei Bollettini fitosanitari" (janeiro de '
                                 '2026), Metapontino com Val d\'Agri prevista; sistema '
                                 'FitoSPA de previsão e aviso'),
                 'WHAT_IT_LACKS': 'lista de culturas sem cereais; sem link direto'},
                {'ROUTE': 'alsia.it — Servizi / Bollettini Fitosanitari', 'HTTP': 200,
                 'WHAT_IT_HAS': ('a porta: "Iscrivendosi ai Servizi di Consulenza '
                                 'on-line dell\'Agenzia, è possibile accedere '
                                 'gratuitamente ai Bollettini"'),
                 'WHAT_IT_LACKS': 'as edições, que ficam atrás do cadastro'},
            ],
            'FIELD_SIGNAL_STATE': 'EXISTS_BEHIND_FREE_REGISTRATION',
            'HAS_2026_ACTIVITY': True,
            'CROP_NAMED': ('NÃO para cereais nas páginas públicas — as culturas nomeadas '
                           'são fruteiras, videira, cítricos, morango e tomate'),
            'ISSUE': 'NÃO SEI para trigo duro',
            'GEOGRAPHIC_RESOLUTION': 'comprensório (Metapontino; Val d\'Agri prevista)',
            'TEMPORAL_RESOLUTION': 'periódico, frequência não declarada publicamente',
            'SERIES_OR_ISOLATED': 'série numerada (n. 01/2022 etc.)',
            'EVIDENCE_STATE': 'GATED_BY_FREE_REGISTRATION',
            'RAW_EVIDENCE_STATE': 'NOT_PRESERVED',
            'LAW': 'GATED ≠ BLOCKED ≠ ABSENT',
            'WHY_I_DID_NOT_OPEN_IT': (
                'criar cadastro em serviço de terceiro é ação para fora, não sondagem de '
                'dado público, e não estava autorizada nesta missão. A porta existe, é '
                'gratuita, e a própria página publica o contato responsável.'),
        },
        {
            'REGION': 'Campania', 'NUTS2': 'ITF3',
            'DURUM_THS_HA': 52.6, 'PCT_NATIONAL_DURUM': 4.5, 'DURUM_RANK': 6,
            'BODY': 'Servizio Fitosanitario Regionale della Campania',
            'FOUND_HOW': 'de passagem, na busca pela Sicília — não era alvo desta rodada',
            'ROUTES_TRIED': [
                {'ROUTE': 'agricoltura.regione.campania.it/difesa/bollettini/'
                          'bollettini_2026.html', 'HTTP': 200,
                 'WHAT_IT_HAS': ('série 2026 viva, boletim POR PROVÍNCIA — Avellino, '
                                 'Benevento, Caserta, Napoli, Salerno — com edição de '
                                 '26/08/2026, quatro dias antes desta medição; declara '
                                 'reportar "lo stato fenologico e lo stato fitosanitario '
                                 'delle diverse colture"'),
                 'WHAT_IT_LACKS': 'a lista de culturas não está exposta no índice'},
                {'ROUTE': 'simfito.regione.campania.it/bollettini/ (plataforma '
                          'ano × área × cultura)', 'HTTP': 200,
                 'WHAT_IT_HAS': 'apenas o cabeçalho; a aplicação não renderiza no servidor',
                 'WHAT_IT_LACKS': 'as opções de cultura — mesma classe da bacheca do Piemonte'},
            ],
            'FIELD_SIGNAL_STATE': 'SERIES_LIVE_CROP_LIST_NOT_READABLE',
            'CROP_NAMED': 'NÃO SEI — o índice diz "diverse colture" sem enumerar',
            'ISSUE': 'NÃO SEI',
            'GEOGRAPHIC_RESOLUTION': 'PROVÍNCIA (5 províncias) — a melhor achada fora da Toscana',
            'TEMPORAL_RESOLUTION': 'edição mais recente 26/08/2026',
            'SERIES_OR_ISOLATED': 'série 2026 com índice próprio',
            'EVIDENCE_STATE': 'INDEX_READ_CONTENT_NOT_READ',
            'RAW_EVIDENCE_STATE': 'NOT_PRESERVED',
            'NOTE': ('é a rota mais promissora das três: série viva, fresca e provincial. '
                     'Falta só saber se o cereal está entre as culturas — e isso está a '
                     'um PDF de distância, não a uma barreira.'),
        },
    ]


def main():
    rs = regioes()
    coberto_novo = [r for r in rs if r['FIELD_SIGNAL_STATE'] == 'DURUM_BULLETIN_READ']
    out = {
        'COUNTRY': 'IT',
        'SOURCE_ID': 'DERIVED/IT-DURUM-FIELD-PANEL',
        'SOURCE': 'sondagem direta dos serviços fitossanitários regionais',
        'CAPTURED_AT': datetime.date.today().isoformat(),
        'AS_OF': AS_OF,
        'SOURCE_LOCATION': 'Sicilia · Basilicata · Campania',
        'FACT_LOCATION': 'ITALY',
        'ORIGINAL_LANGUAGE': 'it',
        'EVIDENCE_CLASS': 'PRIMARY_SOURCE_PROBE',
        'CROP': 'Trigo duro',
        'QUESTION': ('as duas maiores regiões de trigo duro nunca perguntadas publicam '
                     'sinal de campo para a cultura?'),
        'ANSWER': ('não foi possível dizer que sim em nenhuma das três. A Sicília tem '
                   'atividade regulatória viva em 2026 e ficha técnica de Frumento, mas '
                   'nenhum boletim nas rotas medidas; a Basilicata retomou o serviço em '
                   'janeiro de 2026 e o conteúdo está atrás de cadastro gratuito; a '
                   'Campânia publica série provincial fresca cuja lista de culturas não '
                   'é legível. NENHUMA moveu a cobertura para cima.'),
        'COVERAGE_MOVED': False,
        'WHY_COVERAGE_DID_NOT_MOVE': (
            'abrir a rota não é ler o sinal. Em nenhuma das três eu li um boletim de '
            'trigo duro, então nenhuma entra como coberta. A cobertura medida da cultura '
            'continua sendo a Toscana: 3,7% da área nacional.'),
        'PCT_NATIONAL_PROBED_THIS_ROUND': round(
            sum(r['PCT_NATIONAL_DURUM'] for r in rs), 1),
        'PCT_NATIONAL_NOW_COVERED': 3.7,
        'REGIONS': rs,
        'LAWS_OBEYED': [
            'ROUTE FAILURE ≠ SIGNAL ABSENCE — o 503 do SIAS não diz nada sobre a Sicília',
            'SOURCE ABSENCE ≠ FIELD ABSENCE — não achar índice não é não haver doença',
            'ONE REGION ≠ COUNTRY — a Toscana continua sendo 3,7%, não a Itália',
            'GATED ≠ BLOCKED ≠ ABSENT — cadastro gratuito é porta, não barreira',
            'NORMA TÉCNICA ≠ SINAL DE CAMPO — ficha de cultura diz o que se pode fazer, '
            'não o que está acontecendo',
        ],
        'HANDOFF': [
            {'REGION': 'Basilicata', 'ACTION': (
                'cadastrar-se nos Servizi di Consulenza on-line da ALSIA (gratuito) e '
                'verificar se há boletim de cereais; a página publica o responsável'),
             'STATUS': 'READY_TO_RUN'},
            {'REGION': 'Campania', 'ACTION': (
                'abrir um dos 5 boletins provinciais de 26/08/2026 em navegador e ler a '
                'lista de culturas; se houver cereal, é a melhor resolução geográfica '
                'de trigo duro do país fora da Toscana'),
             'STATUS': 'READY_TO_RUN'},
            {'REGION': 'Sicilia', 'ACTION': (
                'reabrir o SIAS de outra rede (503 em duas tentativas daqui) e procurar '
                'boletim agrometeo com seção de cultura'),
             'STATUS': 'READY_TO_RUN'},
        ],
        'WHAT_THIS_DOES_NOT_PROVE': [
            'que a Sicília não publique sinal de campo de trigo duro — não achei nas '
            'rotas medidas, o que é diferente',
            'que a Basilicata não cubra cereais — as páginas públicas não nomeiam, e as '
            'edições correntes não foram lidas',
            'que a Campânia cubra ou não cubra cereais — a lista não é legível daqui',
            'qualquer coisa sobre venda, estoque ou prioridade interna',
        ],
    }
    os.makedirs(os.path.dirname(DEST), exist_ok=True)
    with open(DEST, 'w', encoding='utf-8') as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    for r in rs:
        print('%-12s %5.1f%%  %-38s %s' % (r['REGION'], r['PCT_NATIONAL_DURUM'],
                                           r['FIELD_SIGNAL_STATE'], r['EVIDENCE_STATE']))
    print('area sondada nesta rodada: %.1f%% · cobertura medida continua: %.1f%%'
          % (out['PCT_NATIONAL_PROBED_THIS_ROUND'], out['PCT_NATIONAL_NOW_COVERED']))
    print('->', os.path.relpath(DEST, ROOT))


if __name__ == '__main__':
    main()
