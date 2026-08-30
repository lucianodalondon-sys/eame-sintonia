#!/usr/bin/env python3
"""
PILOTO DA CAMADA DE SENSORES HUMANOS — IT-CASE-DURUM-FUSARIUM-001.

A pergunta não era "quantos influencers achamos". Era: **pessoas deram sinal útil antes,
durante ou logo após a convergência que as fontes institucionais mostraram?**

Medi. A resposta curta é que **na amostra medida, não** — e o resultado mais interessante
é a FORMA do não.

O QUE A MEDIÇÃO ENCONTROU
--------------------------
1 · **A camada de voz deste crop×issue é majoritariamente CORPORATIVA.** Em 54 vídeos
    distintos recuperados no YouTube para trigo/fusariose, os canais são Bayer, Syngenta,
    Sumitomo, BASF, Corteva, Sipcam, Yara, Adama e consórcios agrários. Voz de pesquisador
    independente ou de técnico de campo publicando observação própria: **não apareceu**.

2 · **O único sinal ANTERIOR ao caso é institucional e é de outra doença.** A Corteva
    publicou em **29/03/2026** — 25 dias antes do boletim do LaMMA — uma página que traz
    observação de campo real: *"In diversi areali, la presenza della malattia sulle foglie
    basali è già stata rilevata in campo"*. Mas é **Septoria**, não fusariose; não nomeia
    região; e é conteúdo comercial que promove um produto próprio. Antecedência existe;
    sobre o issue do caso, não.

3 · **A camada de pesquisa convoca DEPOIS.** O *Durum Days 2026*, convênio nacional de
    referência do grano duro, aconteceu em **19/05/2026**, quatro semanas DEPOIS da
    convergência, e a página que o anuncia é de 13/05. A ciência italiana do trigo duro se
    reúne para olhar a safra quando a janela já fechou.

4 · **A voz do produtor falou de PREÇO, não de doença.** A manifestação da Confagricoltura
    (Umbria, Marche, Abruzzo, Lazio) é de **03/07/2026** e é inteiramente econômica —
    "i prezzi... ben al di sotto dei costi di produzione". Nenhuma menção a fusariose,
    septoria, chuva ou condição de campo.

5 · **Creator: zero.** Nenhum criador com audiência própria produzindo conteúdo sobre
    grano duro × fusariose apareceu. É o terceiro crop×issue seguido nesta branch em que
    a rota de creator devolve nada — depois de flavescência e piralide.

A ARMADILHA QUE ESTA MISSÃO QUASE ENGOLIU
------------------------------------------
O artigo mais parecido com "voz de campo" que apareceu — *"Grano, spigatura in anticipo
tra pioggia e trattamenti in corso"*, com o agrônomo **Stefano Biagetti** do Consorzio
Agrario di Ancona citado nominalmente, falando de spigatura adiantada, chuva e
fusariose — é de **20/04/2024**. Data quase igual no calendário, **dois anos antes**.
Encaixaria perfeitamente na narrativa e seria falso.

    CLASSE CERTA ≠ JANELA CERTA

O QUE NÃO PODE SER DITO
------------------------
Que a camada humana não existe. **Duas das três plataformas estão fechadas**: LinkedIn e
Instagram devolvem HTTP 200 com **muro de login** — 487 KB e 661 KB de casca para ~750
caracteres de texto útil, todo ele interface de acesso. Isso é `ACCESS_FAILURE`, e
`ACCESS_FAILURE ≠ NO_SIGNAL`. Perfis do LinkedIn são indexados publicamente; o CONTEÚDO
datado não é — e `PERFIL ≠ CONTEÚDO`.

E as páginas de vídeo do YouTube devolveram **429 em duas tentativas**, então dos dois
itens de 2026 eu tenho apenas a data RELATIVA ("6 mesi fa", "2 mesi fa"). Data aproximada
**não coloca nada antes do caso**: o webinar da Adama provavelmente é anterior a 23/04,
e "provavelmente" não fecha afirmação temporal. Fica `NOT_DATED_PRECISELY`.
"""
import datetime
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DEST = os.path.join(ROOT, 'data', 'samples', 'IT-CASOS', 'IT-HUMAN-SENSOR-PILOT.json')

CASE_DATE = datetime.date(2026, 4, 23)

RESEARCHER = 'RESEARCHER'
TECH = 'TECHNICAL_FIELD_VOICE'
PROD = 'PRODUCER_COOP_VOICE'
CREATOR = 'CREATOR_INFLUENCER'
INST = 'INSTITUTIONAL_VOICE'


def perfis():
    """Pessoas e entidades achadas, com a evidência que sustenta a classificação."""
    return [
        {'NAME': 'Pasquale De Vita', 'VOICE_CLASS': RESEARCHER,
         'ROLE': 'ricercatore', 'INSTITUTION': 'CREA Cerealicoltura e Colture Industriali',
         'COUNTRY': 'IT', 'REGION': 'Puglia (Foggia)', 'SPECIALTY': 'genética e agronomia do grano duro',
         'CROP': 'grano duro', 'ISSUE': 'NÃO ESPECÍFICO',
         'EVIDENCE_FOR_CLASSIFICATION': 'citado como ricercatore do CREA de Foggia em fonte pública',
         'LINKEDIN_URL': 'NÃO PROVADO', 'INSTAGRAM_URL': 'NÃO PROVADO',
         'DATED_SIGNAL_IN_WINDOW': None},
        {'NAME': 'Nicola Pecchioni', 'VOICE_CLASS': RESEARCHER,
         'ROLE': 'Direttore', 'INSTITUTION': 'CREA Cerealicoltura e Colture Industriali',
         'COUNTRY': 'IT', 'REGION': 'Puglia (Foggia)', 'SPECIALTY': 'cerealicoltura',
         'CROP': 'grano duro', 'ISSUE': 'NÃO ESPECÍFICO',
         'EVIDENCE_FOR_CLASSIFICATION': 'citado como diretor do centro em fonte pública',
         'LINKEDIN_URL': 'NÃO PROVADO', 'DATED_SIGNAL_IN_WINDOW': None},
        {'NAME': 'Sabrina Locatelli', 'VOICE_CLASS': RESEARCHER,
         'ROLE': 'ricercatrice', 'INSTITUTION': 'CREA — sede di Bergamo',
         'COUNTRY': 'IT', 'REGION': 'Lombardia', 'SPECIALTY': 'epidemiologia de fungos, DON',
         'CROP': 'frumento', 'ISSUE': 'fusariosi / micotossine',
         'EVIDENCE_FOR_CLASSIFICATION': ('descrita como ricercatrice do CREA de Bergamo com '
                                         'pesquisa de fusariose e contaminação por DON'),
         'LINKEDIN_URL': 'NÃO PROVADO', 'DATED_SIGNAL_IN_WINDOW': None,
         'NOTE': 'a mais próxima do issue do caso; nenhum conteúdo datado dela na janela'},
        {'NAME': 'Francesca Nocente', 'VOICE_CLASS': RESEARCHER,
         'ROLE': 'ricercatrice', 'INSTITUTION': 'CREA', 'COUNTRY': 'IT',
         'REGION': 'NÃO PROVADO', 'SPECIALTY': 'qualidade do grão, micotossinas',
         'CROP': 'frumento', 'ISSUE': 'fusariosi da espiga × micotossinas',
         'EVIDENCE_FOR_CLASSIFICATION': 'autora de trabalho sobre relação fusariose × micotoxinas',
         'DATED_SIGNAL_IN_WINDOW': None},
        {'NAME': 'Daniela Pacifico', 'VOICE_CLASS': RESEARCHER,
         'ROLE': 'CREA — contato científico do Durum Days 2026', 'INSTITUTION': 'CREA',
         'COUNTRY': 'IT', 'REGION': 'NÃO PROVADO', 'CROP': 'grano duro',
         'EVIDENCE_FOR_CLASSIFICATION': 'contato institucional publicado na página do evento',
         'DATED_SIGNAL_IN_WINDOW': None},

        {'NAME': 'Stefano Biagetti', 'VOICE_CLASS': TECH,
         'ROLE': 'agronomo e tecnico', 'INSTITUTION': 'Consorzio Agrario di Ancona',
         'COUNTRY': 'IT', 'REGION': 'Marche', 'CROP': 'grano', 'ISSUE': 'fusariosi, septoria, oidio',
         'EVIDENCE_FOR_CLASSIFICATION': 'citado nominalmente, com cargo, em matéria técnica regional',
         'DATED_SIGNAL_IN_WINDOW': False,
         'WHY_NOT': ('o conteúdo dele que achei é de 20/04/2024 — dois anos antes. '
                     'CLASSE CERTA ≠ JANELA CERTA.')},
        {'NAME': 'Giovanni Drei', 'VOICE_CLASS': TECH,
         'ROLE': 'tecnico', 'INSTITUTION': 'Bayer Crop Science Italia',
         'COUNTRY': 'IT', 'REGION': 'NÃO PROVADO', 'CROP': 'grano',
         'ISSUE': 'trattamenti in spigatura',
         'EVIDENCE_FOR_CLASSIFICATION': 'apresentado como técnico Bayer em vídeo próprio',
         'DATED_SIGNAL_IN_WINDOW': False,
         'NOTE': 'conteúdo de 28/04/2025; e é voz de fabricante, não independente'},
        {'NAME': 'Federico Cavina', 'VOICE_CLASS': TECH,
         'ROLE': 'Coordinatore Centro di Saggio', 'INSTITUTION': 'Terremerse Soc. Coop.',
         'COUNTRY': 'IT', 'REGION': 'Emilia-Romagna', 'CROP': 'NÃO PROVADO',
         'EVIDENCE_FOR_CLASSIFICATION': 'cargo declarado em perfil público do LinkedIn',
         'DATED_SIGNAL_IN_WINDOW': None,
         'LIMIT': 'PERFIL ≠ CONTEÚDO — o perfil é indexado, os posts datados não'},

        {'NAME': 'Confagricoltura (Umbria, Marche, Abruzzo, Lazio)', 'VOICE_CLASS': PROD,
         'ROLE': 'associação de produtores', 'COUNTRY': 'IT',
         'REGION': 'Umbria, Marche, Abruzzo, Lazio', 'CROP': 'grano duro',
         'ISSUE': 'preço e custo de produção',
         'EVIDENCE_FOR_CLASSIFICATION': 'manifestação conjunta publicada em 03/07/2026',
         'DATED_SIGNAL_IN_WINDOW': True, 'SIGNAL_DATE': '2026-07-03'},
        {'NAME': 'Consorzio Agrario Parma', 'VOICE_CLASS': PROD,
         'ROLE': 'consórcio agrário', 'COUNTRY': 'IT', 'REGION': 'Emilia-Romagna',
         'CROP': 'cereali', 'EVIDENCE_FOR_CLASSIFICATION': 'canal próprio no YouTube',
         'DATED_SIGNAL_IN_WINDOW': True, 'SIGNAL_DATE': 'APROXIMADA — "2 mesi fa"',
         'DATE_STATE': 'NOT_DATED_PRECISELY'},

        {'NAME': 'Corteva Agriscience', 'VOICE_CLASS': INST,
         'ROLE': 'empresa falando como entidade', 'COUNTRY': 'IT', 'REGION': 'NÃO NOMEADA',
         'CROP': 'cereali (inclui frumento duro)', 'ISSUE': 'Septoria',
         'EVIDENCE_FOR_CLASSIFICATION': 'página técnica assinada pela empresa, datada',
         'DATED_SIGNAL_IN_WINDOW': True, 'SIGNAL_DATE': '2026-03-29',
         'COMPETITOR_CONTEXT_ONLY': True},
        {'NAME': 'ADAMA Italia', 'VOICE_CLASS': INST,
         'ROLE': 'empresa falando como entidade', 'COUNTRY': 'IT',
         'CROP': 'cereali', 'ISSUE': 'difesa',
         'EVIDENCE_FOR_CLASSIFICATION': 'canal próprio; webinar de difesa dei cereali',
         'DATED_SIGNAL_IN_WINDOW': None, 'SIGNAL_DATE': 'APROXIMADA — "6 mesi fa"',
         'DATE_STATE': 'NOT_DATED_PRECISELY',
         'WHY': ('as páginas de vídeo do YouTube devolveram 429 em duas tentativas; só '
                 'tenho a data relativa. "Provavelmente anterior a 23/04" não fecha '
                 'afirmação temporal.')},
        {'NAME': 'CREA — Durum Days 2026', 'VOICE_CLASS': INST,
         'ROLE': 'instituto de pesquisa convocando o setor', 'COUNTRY': 'IT',
         'REGION': 'Puglia (Foggia)', 'CROP': 'grano duro',
         'EVIDENCE_FOR_CLASSIFICATION': 'página oficial do CREA anunciando o evento',
         'DATED_SIGNAL_IN_WINDOW': True, 'SIGNAL_DATE': '2026-05-19',
         'PAGE_DATE': '2026-05-13'},
        {'NAME': 'Consorzio LaMMA', 'VOICE_CLASS': INST,
         'ROLE': 'serviço técnico regional', 'COUNTRY': 'IT', 'REGION': 'Toscana',
         'CROP': 'grano duro', 'ISSUE': 'fusariosi',
         'EVIDENCE_FOR_CLASSIFICATION': 'é a fonte do próprio caso, preservada com hash',
         'DATED_SIGNAL_IN_WINDOW': True, 'SIGNAL_DATE': '2026-04-23',
         'NOTE': 'referência, não achado desta missão'},
    ]


def conteudos():
    """Só o que foi LIDO substantivamente, com data própria."""
    return [
        {'PLATFORM': 'WEB', 'PERSON_OR_ORGANIZATION': 'Corteva Agriscience',
         'VOICE_CLASS': INST, 'COUNTRY': 'IT', 'REGION': 'NÃO NOMEADA',
         'CONTENT_URL': 'https://www.corteva.com/it/Agronomia/agronomia0059.html',
         'PUBLISHED_AT': '2026-03-29', 'OBSERVED_AT': '2026-08-30',
         'CROP': 'cereali, frumento duro citado', 'ISSUE': 'Septoria',
         'SIGNAL_TYPE': ['FIELD_OBSERVATION', 'MANAGEMENT_RECOMMENDATION'],
         'TEXT_IT': ('In diversi areali, la presenza della malattia sulle foglie basali è '
                     'già stata rilevata in campo | le piogge ricorrenti e le bagnature '
                     'fogliari diffuse stanno creando condizioni favorevoli alla Septoria'),
         'RELATIVE_TO_CASE': 'BEFORE_CASE', 'DAYS_BEFORE_CASE': 25,
         'ADDS_WHAT': 'antecedência de 25 dias e observação de campo real',
         'DOES_NOT_ADD': ('não é o issue do caso (Septoria, não fusariose), não nomeia '
                          'região, e é conteúdo comercial que promove produto próprio'),
         'SOURCE_STATE': 'READ'},
        {'PLATFORM': 'WEB', 'PERSON_OR_ORGANIZATION': 'Stefano Biagetti / marcheagricole',
         'VOICE_CLASS': TECH, 'COUNTRY': 'IT', 'REGION': 'Marche',
         'CONTENT_URL': 'https://www.marcheagricole.it/grano-spigatura-in-anticipo-tra-pioggia-e-trattamenti-in-corso/',
         'PUBLISHED_AT': '2024-04-20', 'OBSERVED_AT': '2026-08-30',
         'CROP': 'grano', 'ISSUE': 'fusariosi, septoria, oidio',
         'SIGNAL_TYPE': ['FIELD_OBSERVATION', 'PHENOLOGY_OBSERVATION',
                         'MANAGEMENT_RECOMMENDATION'],
         'TEXT_IT': ('fase fenologica di spigatura del grano ... Il ciclo biologico è in '
                     'anticipo di 10-15 giorni rispetto alla media ... Il trattamento '
                     'previene infine anche la Fusariosi'),
         'RELATIVE_TO_CASE': 'OUT_OF_WINDOW',
         'WHY_EXCLUDED': ('é de 2024, dois anos antes do caso. É o exemplo mais próximo '
                          'de voz técnica de campo que achei, e por isso mesmo o mais '
                          'perigoso: encaixaria na narrativa e seria falso.'),
         'SOURCE_STATE': 'READ'},
        {'PLATFORM': 'WEB', 'PERSON_OR_ORGANIZATION': 'Confagricoltura (4 regiões)',
         'VOICE_CLASS': PROD, 'COUNTRY': 'IT',
         'REGION': 'Umbria, Marche, Abruzzo, Lazio',
         'CONTENT_URL': 'https://www.confagricolturaumbria.it/quadro-preoccupante-per-la-campagna-grano-duro-2026/',
         'PUBLISHED_AT': '2026-07-03', 'OBSERVED_AT': '2026-08-30',
         'CROP': 'grano duro', 'ISSUE': 'preço, custo de produção',
         'SIGNAL_TYPE': ['OTHER'],
         'TEXT_IT': ('I prezzi di valorizzazione continuano infatti a mantenersi ben al '
                     'di sotto dei costi di produzione'),
         'RELATIVE_TO_CASE': 'AFTER_CASE',
         'ADDS_WHAT': 'nada sobre campo — a voz do produtor falou de PREÇO, não de doença',
         'SOURCE_STATE': 'READ'},
        {'PLATFORM': 'WEB', 'PERSON_OR_ORGANIZATION': 'CREA — Durum Days 2026',
         'VOICE_CLASS': INST, 'COUNTRY': 'IT', 'REGION': 'Puglia (Foggia)',
         'CONTENT_URL': ('https://www.crea.gov.it/web/cerealicoltura-e-colture-industriali/'
                         '-/durum-days-2026-a-foggia-il-convegno-di-riferimento-nazionale-'
                         'sul-grano-duro'),
         'PUBLISHED_AT': '2026-05-13', 'EVENT_DATE': '2026-05-19',
         'OBSERVED_AT': '2026-08-30', 'CROP': 'grano duro',
         'SIGNAL_TYPE': ['GENERAL_EDUCATION'],
         'RELATIVE_TO_CASE': 'AFTER_CASE', 'DAYS_AFTER_CASE': 26,
         'ADDS_WHAT': ('mostra QUANDO a camada de pesquisa se reúne: quatro semanas depois '
                       'da janela de campo'),
         'SOURCE_STATE': 'READ'},
        {'PLATFORM': 'WEB', 'PERSON_OR_ORGANIZATION': 'Horta srl (spin-off UCSC Piacenza)',
         'VOICE_CLASS': INST, 'COUNTRY': 'IT',
         'CONTENT_URL': 'https://www.horta-srl.it/news/rassegna-stampa/',
         'PUBLISHED_AT': 'último item 2023-01-27', 'OBSERVED_AT': '2026-08-30',
         'CROP': 'grano duro', 'SIGNAL_TYPE': ['OTHER'],
         'RELATIVE_TO_CASE': 'OUT_OF_WINDOW',
         'NOTE': ('opera o DSS granoduro.net, que é exatamente a camada de modelo por trás '
                  'de boletins como o do LaMMA; a rassegna stampa pública está parada em '
                  '2023'),
         'SOURCE_STATE': 'READ_BUT_STALE'},
        {'PLATFORM': 'YOUTUBE', 'PERSON_OR_ORGANIZATION': 'busca por trigo × fusariose',
         'VOICE_CLASS': 'MISTO', 'COUNTRY': 'IT',
         'CONTENT_URL': 'youtube.com/results (3 consultas)',
         'OBSERVED_AT': '2026-08-30',
         'ITEMS_SCREENED': 54,
         'SIGNAL_TYPE': ['GENERAL_EDUCATION'],
         'WHAT_THE_SAMPLE_SHOWS': ('canais dominados por fabricantes — Bayer, Syngenta, '
                                   'Sumitomo, BASF, Corteva, Sipcam, Yara, Adama — e por '
                                   'consórcios agrários. Nenhum pesquisador independente '
                                   'ou técnico de campo publicando observação própria.'),
         'ITEMS_IN_2026': 2,
         'SOURCE_STATE': 'METADATA_READ_DATES_APPROXIMATE'},
    ]


def relogio_por_classe():
    return {
        'OFFICIAL_FIELD_SIGNAL': CASE_DATE.isoformat(),
        'FIRST_RESEARCHER_SIGNAL': {
            'DATE': None, 'STATE': 'NOT_OBSERVED_IN_MEASURED_SAMPLE',
            'NOTE': ('cinco pesquisadores identificados por rota pública, nenhum com '
                     'conteúdo datado na janela. O item de pesquisa mais próximo é o '
                     'Durum Days, de 19/05/2026 — depois do caso, e é convocação de '
                     'evento, não observação de campo.')},
        'FIRST_TECHNICAL_SIGNAL': {
            'DATE': None, 'STATE': 'NOT_OBSERVED_IN_MEASURED_SAMPLE',
            'NOTE': ('a melhor voz técnica achada, Stefano Biagetti, tem conteúdo de '
                     '2024. Na janela de 2026, nada.')},
        'FIRST_PRODUCER_SIGNAL': {
            'DATE': '2026-07-03', 'STATE': 'AFTER_CASE',
            'NOTE': 'e é econômico, não agronômico'},
        'FIRST_CREATOR_SIGNAL': {
            'DATE': None, 'STATE': 'NOT_OBSERVED_IN_MEASURED_SAMPLE',
            'NOTE': ('terceiro crop×issue seguido desta branch em que a rota de creator '
                     'devolve nada, depois de flavescência e piralide')},
        'FIRST_INSTITUTIONAL_SIGNAL': {
            'DATE': '2026-03-29', 'STATE': 'BEFORE_CASE', 'DAYS_BEFORE': 25,
            'WHO': 'Corteva Agriscience',
            'NOTE': ('antecedência real com observação de campo real — mas sobre Septoria, '
                     'não fusariose, sem região, e em conteúdo comercial')},
    }


def main():
    ps, cs = perfis(), conteudos()
    por_classe = {}
    for p in ps:
        por_classe.setdefault(p['VOICE_CLASS'], []).append(p['NAME'])

    out = {
        'CASE_ID': 'IT-CASE-DURUM-FUSARIUM-001',
        'SOURCE_ID': 'DERIVED/IT-HUMAN-SENSOR-PILOT',
        'source': 'sondagem pública de LinkedIn, Instagram, YouTube e web técnica italiana',
        'SOURCE_LOCATION': 'Itália', 'FACT_LOCATION': 'ITALY',
        'ORIGINAL_LANGUAGE': 'it',
        'EVIDENCE_CLASS': 'PRIMARY_SOURCE_PROBE',
        'captured_at': datetime.date.today().isoformat(),
        'CAPTURED_AT': datetime.date.today().isoformat(),
        'CASE_DATE': CASE_DATE.isoformat(),
        'QUESTION': ('pesquisadores, técnicos, produtores, cooperativas ou creators deram '
                     'sinal útil antes, durante ou logo após a convergência que as fontes '
                     'institucionais mostraram?'),
        'ANSWER': ('na amostra medida, não. Nenhuma das quatro classes humanas produziu '
                   'sinal datado ANTES do caso sobre o issue do caso. O único item '
                   'anterior é institucional-corporativo e é sobre outra doença.'),
        'PROFILES_BY_CLASS': {k: {'COUNT': len(v), 'NAMES': v}
                              for k, v in sorted(por_classe.items())},
        'PROFILES': ps,
        'CONTENTS_READ': cs,
        'COUNTS': {
            'PROFILES_OR_ENTITIES': len(ps),
            'DOCUMENTS_READ_IN_FULL': len([c for c in cs if c['PLATFORM'] == 'WEB']),
            'YOUTUBE_ITEMS_SCREENED': 54,
            'LIMIT_PROFILES': 40, 'LIMIT_CONTENTS': 300,
            'STOPPED_EARLY_BECAUSE': ('o sinal ficou provado com esta amostra: quatro '
                                      'classes medidas, nenhuma com antecedência sobre o '
                                      'issue. Procurar 40 perfis só porque o teto é 40 '
                                      'seria coletar volume, não fechar pergunta.'),
        },
        'CLOCK_BY_CLASS': relogio_por_classe(),
        'PLATFORM_STATE': {
            'LINKEDIN': {'HTTP': 200, 'STATE': 'ACCESS_FAILURE_LOGIN_WALL',
                         'MEASURED': ('487 KB de casca para ~750 caracteres de texto útil, '
                                      'todo interface de login'),
                         'WHAT_IS_VISIBLE': 'perfis são indexados publicamente',
                         'WHAT_IS_NOT': 'conteúdo datado — PERFIL ≠ CONTEÚDO',
                         'LAW': 'ACCESS_FAILURE ≠ NO_SIGNAL'},
            'INSTAGRAM': {'HTTP': 200, 'STATE': 'ACCESS_FAILURE_LOGIN_WALL',
                          'MEASURED': '661 KB de casca para ~712 caracteres, todo login',
                          'API_PROBE': 'HTTP 429',
                          'LAW': 'ACCESS_FAILURE ≠ NO_SIGNAL'},
            'YOUTUBE': {'SEARCH': 'OK — 54 itens com título, canal e data relativa',
                        'WATCH_PAGES': 'HTTP 429 em duas tentativas — THROTTLED',
                        'OEMBED': 'OK, mas não devolve data',
                        'CONSEQUENCE': ('dos dois itens de 2026 só tenho data relativa; '
                                        'data aproximada NÃO coloca nada antes do caso')},
        },
        'WHAT_HUMAN_LAYER_ADDED_OVER_LAMMA': [
            ('antecedência de 25 dias, uma vez, e de uma empresa: a observação de Septoria '
             'em folhas basais da Corteva em 29/03/2026'),
        ],
        'WHAT_ONLY_REPEATED': [
            ('os vídeos de fabricante — Bayer, Syngenta, Sumitomo, BASF, Sipcam — repetem '
             'conteúdo educativo de calendário, sem observação datada da safra corrente'),
            ('as páginas técnicas perenes (Terra e Vita, Fitogest, granoitaliano) explicam '
             'a fusariose corretamente e sem data de safra — não são sensor'),
        ],
        'LAWS_APPLIED': [
            'ACCESS_FAILURE ≠ NO_SIGNAL',
            'PERFIL ≠ CONTEÚDO',
            'CLASSE CERTA ≠ JANELA CERTA — o artigo de Biagetti é de 2024 e encaixaria',
            'DATA APROXIMADA NÃO COLOCA NADA ANTES DO CASO',
            'FOLLOWERS ≠ AUTORIDADE — nenhum ranking de audiência foi feito',
        ],
        'CONTROLS': {
            'STATE': 'NOT_RUN',
            'WHY': ('os controles de milho×piralide e olivo×Bactrocera dependiam de '
                    'orçamento restante depois do caso principal. As duas plataformas '
                    'sociais estão fechadas e o YouTube está estrangulado, então rodar os '
                    'controles mediria a mesma limitação de acesso, não o comportamento '
                    'da camada humana.'),
            'PARTIAL_EVIDENCE_ALREADY_IN_BRANCH': (
                'as rodadas anteriores já mediram creator = zero para flavescência e para '
                'piralide/diabrotica. Com grano duro × fusariose, são três.'),
        },
        'APIFY': {
            'TOKEN_1_USED': False, 'TOKEN_2_USED': False,
            'TOTAL_ACTOR_RUNS': 0, 'TOTAL_ITEMS': 0, 'TOTAL_COST': 0,
            'DUPLICATES_REMOVED': 0,
            'WHY_NOT_USED': (
                'duas razões. Primeira, §16: rota pública primeiro, e a rota pública '
                'respondeu o suficiente para o veredito. Segunda, §15 exige que as chaves '
                'venham do AMBIENTE como APIFY_TOKEN_1/2 e proíbe escrever o valor em log; '
                'o ambiente não tem essas variáveis, e injetar o valor numa linha de '
                'comando o gravaria justamente num log.'),
            'WHAT_IT_WOULD_BUY': (
                'exatamente a pergunta que ficou aberta: conteúdo DATADO de LinkedIn e '
                'Instagram, que é onde agrônomos e produtores italianos publicariam '
                'observação de campo, e que é a única porta fechada desta medição.'),
        },
        'VERDICT': 'HUMAN_SENSOR_LAYER_NOT_PROVED_IN_SAMPLE',
        'VERDICT_WHY': (
            'nenhuma das quatro classes humanas — pesquisador, técnico, produtor, creator '
            '— produziu sinal datado antes de 23/04/2026 sobre fusariose em grano duro. O '
            'único sinal anterior é de uma EMPRESA, sobre outra doença, sem região. Mas o '
            'veredito é NOT_PROVED_IN_SAMPLE e não NOT_EXISTS, porque duas das três '
            'plataformas estavam fechadas por login.'),
        'RECOMMENDATION': 'MANTER PEQUENO',
        'RECOMMENDATION_WHY': (
            'não escalar sobre uma medição em que 2 de 3 portas estavam fechadas, e não '
            'despriorizar sobre a mesma medição. O próximo passo é barato e decide: abrir '
            'LinkedIn e Instagram com credencial autorizada para ESTE crop×issue e ver se '
            'a camada aparece. Se com as portas abertas ela continuar vazia, aí sim a '
            'resposta é despriorizar.'),
        'WHAT_THIS_DOES_NOT_PROVE': [
            'que não exista voz humana útil na Itália — duas plataformas não foram lidas',
            'que os cinco pesquisadores identificados não tenham falado: só que não achei '
            'conteúdo datado deles na janela',
            'nada sobre venda, prioridade interna ou concorrência — a Corteva aparece '
            'aqui como CONTEXTO incidental, não como coleta de concorrente',
        ],
    }
    os.makedirs(os.path.dirname(DEST), exist_ok=True)
    with open(DEST, 'w', encoding='utf-8') as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)

    print('PERFIS POR CLASSE')
    for k, v in sorted(out['PROFILES_BY_CLASS'].items()):
        print('  %-24s %d' % (k, v['COUNT']))
    print('RELOGIO POR CLASSE (caso = %s)' % CASE_DATE)
    for k, v in out['CLOCK_BY_CLASS'].items():
        if isinstance(v, dict):
            print('  %-28s %-34s %s' % (k, v['STATE'], v.get('DATE') or ''))
    print('PLATAFORMAS')
    for k, v in out['PLATFORM_STATE'].items():
        print('  %-10s %s' % (k, v.get('STATE') or v.get('WATCH_PAGES')))
    print('VEREDITO: %s' % out['VERDICT'])
    print('RECOMENDACAO: %s' % out['RECOMMENDATION'])
    print('->', os.path.relpath(DEST, ROOT))


if __name__ == '__main__':
    main()
