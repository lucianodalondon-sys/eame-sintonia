#!/usr/bin/env python3
"""
ONDE OS SENSORES REALMENTE PUBLICAM — o sensor é a pessoa, a plataforma é a porta.

O LinkedIn foi medido e rendeu quase nada: quatro perfis, três posts em um ano,
um na janela, e esse um era um anúncio de vaga. A conclusão errada seria "os
pesquisadores italianos não publicam". A pergunta certa é outra: **onde eles
publicam?**

    LINKEDIN_NOT_PRODUCTIVE_IN_MEASURED_PANEL
    ≠ HUMAN_SENSOR_LAYER_NOT_PRODUCTIVE

O QUE A BUSCA DE PORTAS ENCONTROU
-----------------------------------
Não é rede social. É **evento técnico relatado pela imprensa técnica**. Os mesmos
pesquisadores que não publicam nada no LinkedIn aparecem, com nome, citação
direta e número, em reportagens de AgroNotizie, Terra e Vita e Informatore
Agrario — sempre a reboque de um convegno.

    CANAL = EVENTO → IMPRENSA TÉCNICA

E ISSO TEM UMA CONSEQUÊNCIA QUE NENHUMA FERRAMENTA CONSERTA
-------------------------------------------------------------
O calendário desses eventos é preso à safra FECHADA, não à janela de risco:

    Giornata del Mais   30/01/2026   relata a safra de milho encerrada em outubro
    Durum Days          19/05/2026   relata estimativas de pré-colheita

A fusariose do trigo duro se decide na floração — abril. O congresso nacional do
trigo duro acontece em maio. Não é atraso de publicação: é o desenho do
calendário. O canal do pesquisador é **retrospectivo por construção**.

Ele é excelente para caracterizar risco crônico e estrutural — "as fumonisinas
são um risco crônico, e desde 2022 a frequência é preocupante" é uma frase que
nenhum boletim semanal produz. E é estruturalmente incapaz de avisar sobre a
safra que está correndo.

    RESEARCHER_CHANNEL_IS_RETROSPECTIVE_BY_CALENDAR
    PUBLICATION_BEFORE_CASE ≠ EARLY_WARNING

Por isso os vereditos são separados. Um canal ruim para antecipação pode ser
ótimo para contexto, e fundir os dois esconde as duas coisas.
"""
import datetime
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import fato_local as fl  # noqa: E402

DEST = os.path.join(ROOT, 'data', 'samples', 'IT-CASOS', 'IT-PORTAS-SENSORES.json')
EVID = os.path.join(ROOT, 'data', 'samples', 'IT-T5-SENSORES')

CASE_DATE = datetime.date(2026, 4, 23)
JANELA = (datetime.date(2026, 1, 1), datetime.date(2026, 5, 31))

# Tipos de sinal de pesquisador. Um artigo científico é evidência científica e
# NÃO é, por isso, um sensor precoce; uma apresentação de congresso pode datar
# melhor; um laboratório de diagnóstico pode localizar melhor. Não se somam.
RESEARCH_FINDING, FIELD_OBSERVATION = 'RESEARCH_FINDING', 'FIELD_OBSERVATION'
DIAGNOSTIC_RESULT, TECHNICAL_WARNING = 'DIAGNOSTIC_RESULT', 'TECHNICAL_WARNING'
EVENT_PRESENTATION, WEBINAR, INTERVIEW = 'EVENT_PRESENTATION', 'WEBINAR', 'INTERVIEW'
PROJECT_UPDATE, PUBLICATION = 'PROJECT_UPDATE', 'PUBLICATION'
RETROSPECTIVE_ANALYSIS = 'RETROSPECTIVE_ANALYSIS'

# Relevância. `CONTROL_POSITIVE` existe para que um acerto em OUTRO par
# cultura×problema não seja lido como acerto no caso principal.
EXACT_CASE_SIGNAL = 'EXACT_CASE_SIGNAL'
NEIGHBOURING_SIGNAL = 'NEIGHBOURING_SIGNAL'
CONTROL_POSITIVE = 'CONTROL_POSITIVE'
RETROSPECTIVE = 'RETROSPECTIVE'
GENERAL_RESEARCH, UNRELATED = 'GENERAL_RESEARCH', 'UNRELATED'

NOT_OBSERVED = 'NOT_OBSERVED_IN_MEASURED_SAMPLE'


# ------------------------------------------------------------------- portas
# Medido em 2026-08-30 por busca pública, sem gastar chave nenhuma. `NOT_FOUND`
# aqui é sempre "não achei nesta busca", nunca "não existe".
PORTAS = [
    {
        'RESEARCHER': 'Sabrina Locatelli',
        'INSTITUTION': 'CREA Cerealicoltura e Colture Industriali — Bergamo',
        'PRIMARY_PUBLIC_CHANNEL': 'EVENTO TÉCNICO → IMPRENSA TÉCNICA',
        'PRIMARY_CHANNEL_INSTANCE': 'Giornata del Mais (CREA Bergamo) → AgroNotizie',
        'SECONDARY_PUBLIC_CHANNEL': 'apresentações em PDF hospedadas por terceiros (CRPA)',
        'DATED_CONTENT_AVAILABLE': 'YES',
        'FIELD_OR_TECHNICAL_SIGNAL_AVAILABLE': 'YES',
        'LINKEDIN_IDENTITY': 'IDENTITY_NOT_ENOUGH_EVIDENCE',
        'NOTE': ('o alvo que o LinkedIn NÃO resolveu é o que mais publica fora dele '
                 '— a plataforma errada produziu o pior retrato da pessoa certa'),
    },
    {
        'RESEARCHER': 'Pasquale De Vita',
        'INSTITUTION': 'CREA Cerealicoltura e Colture Industriali — Foggia',
        'PRIMARY_PUBLIC_CHANNEL': 'EVENTO TÉCNICO → IMPRENSA TÉCNICA',
        'PRIMARY_CHANNEL_INSTANCE': 'Durum Days (Foggia) → AgroNotizie / Terra e Vita',
        'SECONDARY_PUBLIC_CHANNEL': 'feiras e convegni regionais (Agripuglia Show)',
        'DATED_CONTENT_AVAILABLE': 'YES',
        'FIELD_OR_TECHNICAL_SIGNAL_AVAILABLE': 'PARTIAL — produção e mercado, não doença',
        'LINKEDIN_IDENTITY': 'IDENTITY_CONFIRMED',
    },
    {
        'RESEARCHER': 'Nicola Pecchioni',
        'INSTITUTION': 'CREA Cerealicoltura e Colture Industriali — diretor',
        'PRIMARY_PUBLIC_CHANNEL': 'EVENTO TÉCNICO → IMPRENSA TÉCNICA',
        'PRIMARY_CHANNEL_INSTANCE': 'Durum Days 2026 (TEA4IT, variedades resistentes)',
        'SECONDARY_PUBLIC_CHANNEL': 'creafuturo.crea.gov.it (divulgação, página de autor)',
        'DATED_CONTENT_AVAILABLE': 'YES',
        'FIELD_OR_TECHNICAL_SIGNAL_AVAILABLE': 'NO — melhoramento e divulgação',
        'LINKEDIN_IDENTITY': 'IDENTITY_PLAUSIBLE_NOT_PROVED',
        'NOTE': ('o canal institucional próprio existe e é datado, mas rendeu 2 textos '
                 'em 3 anos, nenhum sobre doença: PORTA ABERTA, VOLUME BAIXO'),
    },
    {
        'RESEARCHER': 'Francesca Nocente',
        'INSTITUTION': 'CREA Cerealicoltura e Colture Industriali',
        'PRIMARY_PUBLIC_CHANNEL': 'NOT_FOUND_IN_THIS_SEARCH',
        'PRIMARY_CHANNEL_INSTANCE': None,
        'SECONDARY_PUBLIC_CHANNEL': 'literatura científica (via co-autoria CREA)',
        'DATED_CONTENT_AVAILABLE': 'NOT_KNOWN',
        'FIELD_OR_TECHNICAL_SIGNAL_AVAILABLE': 'NOT_KNOWN',
        'LINKEDIN_IDENTITY': 'IDENTITY_PLAUSIBLE_NOT_PROVED',
        'NOTE': 'busca por nome não devolveu canal público próprio; OpenAlex esgotado no dia',
    },
    {
        'RESEARCHER': 'Daniela Pacifico',
        'INSTITUTION': 'CREA Cerealicoltura e Colture Industriali',
        'PRIMARY_PUBLIC_CHANNEL': 'NOT_FOUND_IN_THIS_SEARCH',
        'PRIMARY_CHANNEL_INSTANCE': None,
        'SECONDARY_PUBLIC_CHANNEL': 'literatura científica (via co-autoria CREA)',
        'DATED_CONTENT_AVAILABLE': 'NOT_KNOWN',
        'FIELD_OR_TECHNICAL_SIGNAL_AVAILABLE': 'NOT_KNOWN',
        'LINKEDIN_IDENTITY': 'IDENTITY_NOT_ENOUGH_EVIDENCE',
        'NOTE': 'busca por nome não devolveu canal público próprio; OpenAlex esgotado no dia',
    },
]

# ------------------------------------------------------------------ leituras
# Conteúdo EFETIVAMENTE LIDO. Não "encontrado": lido, com texto preservado ou
# com o que a página devolveu. Cada um traz a data de publicação da fonte.
LEITURAS = [
    {
        'ID': 'AGRONOTIZIE/88873',
        'ARQUIVO': 'agronotizie-88873-mais-micotossine-2026-02-13.txt',
        'URL': ('https://agronotizie.imagelinenetwork.com/difesa-e-diserbo/2026/02/13/'
                'mais-e-micotossine-un-2025-da-dimenticare/88873'),
        'SHA256_HTML': '08a76e1ab459744fdfa1cecad0af0383110bb01f8d423b6c6a29e849dcec2a8e',
        'PUBLISHED_AT': '2026-02-13',
        'CHANNEL': 'IMPRENSA TÉCNICA (relato de evento)',
        'EVENT': 'Giornata del Mais 2026, CREA Bergamo, 30/01/2026',
        'RESEARCHER': 'Sabrina Locatelli',
        'CROP': 'mais', 'ISSUE': 'micotossine',
        'SIGNAL_TYPES': [EVENT_PRESENTATION, DIAGNOSTIC_RESULT, RETROSPECTIVE_ANALYSIS,
                         INTERVIEW],
        'RELEVANCE': CONTROL_POSITIVE,
        'RELEVANCE_EVIDENCE': ('cultura e problema certos para o CONTROLE — mais × '
                               'micotossine —, não para o caso principal, que é '
                               'grano duro × fusariosi'),
        'QUANTITATIVE': {
            'FBs_ACIMA_4_MG_KG_PCT': 72, 'FBs_ACIMA_10_MG_KG_PCT': 44,
            'AFB1_NAO_CONFORME_PCT': 15, 'AFB1_LIMITE_UG_KG': 20,
            'ZONA_OVEST_FBs_ACIMA_4_PCT': 94,
            'SERIE_HISTORICA': '2011-2025',
        },
        'INTERPRETATION_OFFERED': ('as fumonisinas são risco crônico e estrutural; a '
                                   'aflatoxina depende de clima quente e árido, e desde '
                                   '2022 esse padrão é recorrente'),
    },
    {
        'ID': 'CREA/DURUM-DAYS-2026',
        'ARQUIVO': None,
        'URL': ('https://www.crea.gov.it/web/cerealicoltura-e-colture-industriali/-/'
                'durum-days-2026-a-foggia-il-convegno-di-riferimento-nazionale-sul-grano-duro'),
        'PUBLISHED_AT': '2026-05-13',
        'EVENT_DATE': '2026-05-19',
        'CHANNEL': 'SITE INSTITUCIONAL (CREA)',
        'RESEARCHER': 'Pasquale De Vita / Nicola Pecchioni',
        'CROP': 'grano duro', 'ISSUE': None,
        'SIGNAL_TYPES': [EVENT_PRESENTATION, PROJECT_UPDATE],
        'RELEVANCE': GENERAL_RESEARCH,
        'RELEVANCE_EVIDENCE': ('a página do convegno nacional do trigo duro não menciona '
                               'fusariosi, micotossine nem DON — cultura certa, problema '
                               'ausente'),
    },
]


def _sha(caminho):
    with open(caminho, 'rb') as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def relativo(data_iso):
    """Onde a PUBLICAÇÃO cai em relação ao caso. Não diz nada sobre o fato."""
    if not data_iso:
        return 'NOT_DATED_PRECISELY'
    d = datetime.date.fromisoformat(data_iso)
    if d < CASE_DATE - datetime.timedelta(days=7):
        return 'BEFORE_CASE'
    if d <= CASE_DATE + datetime.timedelta(days=7):
        return 'AROUND_CASE'
    return 'AFTER_CASE'


def antecipa(publicado_em, tempo_do_fato):
    """Publicar antes do caso NÃO é avisar antes do caso.

    A reportagem das micotoxinas saiu em 13/02/2026, dez semanas antes do caso.
    E fala da safra de 2025, encerrada. Chamar isso de antecipação seria contar
    como aviso um relatório sobre o ano passado.

        PUBLICATION_BEFORE_CASE ≠ EARLY_WARNING
    """
    posicao = relativo(publicado_em)
    ft = (tempo_do_fato or {}).get('FACT_TIME')
    precisao = (tempo_do_fato or {}).get('FACT_TIME_PRECISION')
    if posicao != 'BEFORE_CASE':
        return posicao, 'NOT_EARLY_WARNING', 'publicado no caso ou depois dele'
    if ft in (None, 'NOT_KNOWN'):
        return posicao, 'NOT_EARLY_WARNING', 'o texto não datou o acontecimento'
    if precisao in (fl.SEASON, fl.YEAR):
        return (posicao, 'RETROSPECTIVE_FINDING',
                'publicado antes do caso, mas sobre uma safra já encerrada (%s)' % ft)
    return posicao, 'CANDIDATE_EARLY_WARNING', 'fato datado dentro da estação corrente'


def ler_evidencia():
    fora = []
    for L in LEITURAS:
        reg = dict(L)
        texto = None
        if L.get('ARQUIVO'):
            caminho = os.path.join(EVID, L['ARQUIVO'])
            if os.path.exists(caminho):
                with open(caminho, encoding='utf-8') as fh:
                    texto = fh.read()
                reg['SHA256_TEXTO'] = _sha(caminho)
                reg['EVIDENCE_STATE'] = 'PRESERVED'
                reg['EVIDENCE_PATH'] = 'data/samples/IT-T5-SENSORES/' + L['ARQUIVO']
            else:
                reg['EVIDENCE_STATE'] = 'NOT_PRESERVED'
        else:
            reg['EVIDENCE_STATE'] = 'READ_NOT_PRESERVED'

        if texto:
            aceitas, recusadas = fl.localizacoes_do_fato(texto, origem=L['ID'])
            tempo = fl.tempo_do_fato(texto, L['PUBLISHED_AT'])
            reg['FACT_LOCATIONS'] = aceitas
            reg['FACT_LOCATIONS_COUNT'] = len(aceitas)
            reg['PLACE_MENTIONS_REJECTED'] = [
                {'PLACE': r['PLACE'], 'WHY': r['WHY']} for r in recusadas]
            reg['TIME'] = tempo
            reg['OCCURRENCE_NOT_INCIDENCE'] = fl.ocorrencia_nao_e_incidencia(
                [a['TYPE_OF_EVIDENCE'] for a in aceitas])
        else:
            reg['FACT_LOCATIONS'] = []
            reg['FACT_LOCATIONS_COUNT'] = 0
            reg['TIME'] = {'FACT_TIME': 'NOT_KNOWN',
                           'PUBLISHED_AT': L['PUBLISHED_AT']}
        pos, aviso, porque = antecipa(L['PUBLISHED_AT'], reg['TIME'])
        reg['PUBLICATION_RELATIVE_TO_CASE'] = pos
        reg['EARLY_WARNING_STATE'] = aviso
        reg['EARLY_WARNING_WHY'] = porque
        fora.append(reg)
    return fora


def medir():
    leituras = ler_evidencia()
    exatos = [L for L in leituras if L['RELEVANCE'] == EXACT_CASE_SIGNAL]
    controles = [L for L in leituras if L['RELEVANCE'] == CONTROL_POSITIVE]
    retro = [L for L in leituras if L['EARLY_WARNING_STATE'] == 'RETROSPECTIVE_FINDING']

    com_canal = [p for p in PORTAS
                 if p['PRIMARY_PUBLIC_CHANNEL'] != 'NOT_FOUND_IN_THIS_SEARCH']
    com_datado = [p for p in PORTAS if p['DATED_CONTENT_AVAILABLE'] == 'YES']

    # Vereditos SEPARADOS. Fundi-los esconderia as duas coisas.
    linkedin = 'LOW_IN_MEASURED_PANEL'
    if controles or exatos:
        pesquisador = 'PROVED_IN_CONTROL' if not exatos else 'PROVED'
    elif com_datado:
        pesquisador = 'PROMISING'
    else:
        pesquisador = 'NOT_PROVED'
    if exatos:
        camada = 'ADDS_DECISION_VALUE'
    elif controles:
        camada = 'PROMISING_BUT_NOT_PROVED'
    else:
        camada = 'NOT_PROVED'

    return {
        'CASE_ID': 'IT-CASE-DURUM-FUSARIUM-001',
        'SOURCE_ID': 'DERIVED/IT-PORTAS-SENSORES',
        'source': 'busca pública de canais — nenhuma execução paga',
        'SOURCE_LOCATION': 'web pública italiana',
        'FACT_LOCATION': 'NOT_KNOWN — nenhuma leitura sustentou localização de fato',
        'ORIGINAL_LANGUAGE': 'it',
        'EVIDENCE_CLASS': 'PRIMARY_SOURCE_PROBE',
        'captured_at': datetime.date.today().isoformat(),
        'CAPTURED_AT': datetime.date.today().isoformat(),
        'CASE_DATE': CASE_DATE.isoformat(),
        'WINDOW': [JANELA[0].isoformat(), JANELA[1].isoformat()],
        'APIFY_RUNS': 0, 'APIFY_COST_USD': 0,

        'LINKEDIN_PANEL': 'LINKEDIN_THIS_PANEL_MEASURED_LOW_YIELD — congelado, sem novas execuções',

        'CHANNELS_BY_RESEARCHER': PORTAS,
        'RESEARCHERS_WITH_A_PUBLIC_CHANNEL': len(com_canal),
        'RESEARCHERS_WITH_DATED_CONTENT': len(com_datado),
        'CONTENTS_READ': leituras,
        'CONTENTS_READ_COUNT': len(leituras),

        'FIRST_RESEARCHER_SIGNAL': {
            'DATE': '2026-02-13', 'RESEARCHER': 'Sabrina Locatelli',
            'CHANNEL': 'AgroNotizie (relato da Giornata del Mais de 30/01/2026)',
            'CROP_ISSUE': 'mais × micotossine'},
        'FIRST_TECHNICAL_SIGNAL': {
            'DATE': '2026-02-13', 'SAME_AS_RESEARCHER_SIGNAL': True,
            'WHY': 'o primeiro sinal técnico e o primeiro sinal de pesquisador são o mesmo'
                   ' conteúdo — no canal medido, o pesquisador fala PELA imprensa técnica'},
        'FIRST_EXACT_CASE_SIGNAL': NOT_OBSERVED,

        'SIGNALS_BEFORE_CASE': [L['ID'] for L in leituras
                                if L['PUBLICATION_RELATIVE_TO_CASE'] == 'BEFORE_CASE'],
        'SIGNALS_AROUND_CASE': [L['ID'] for L in leituras
                                if L['PUBLICATION_RELATIVE_TO_CASE'] == 'AROUND_CASE'],
        'SIGNALS_AFTER_CASE': [L['ID'] for L in leituras
                               if L['PUBLICATION_RELATIVE_TO_CASE'] == 'AFTER_CASE'],
        'EXACT_CASE_SIGNAL': NOT_OBSERVED,
        'CONTROL_POSITIVE': [L['ID'] for L in controles],
        'RETROSPECTIVE': [L['ID'] for L in retro],

        'FACT_LOCATIONS_FOUND': [a for L in leituras for a in L['FACT_LOCATIONS']],
        'FACT_LOCATIONS_COUNT': sum(L['FACT_LOCATIONS_COUNT'] for L in leituras),
        'WHY_NO_FACT_LOCATION': (
            'no controle positivo, os quatro topônimos do texto são: a sede do CREA '
            '(Bergamo), a universidade parceira (Torino), a universidade da outra '
            'palestrante (Piacenza) e uma menção histórica (Italia). Nenhuma frase liga '
            'o acontecimento a um lugar. A própria geografia da fonte é uma zona da rede '
            'de monitoramento — "l\'Ovest" —, que não é unidade administrativa e não tem '
            'entrada no gazetteer. SOURCE_GEOGRAPHY ≠ ADMIN_GEOGRAPHY.'),

        'WHAT_RESEARCHERS_ADDED': {
            'CHRONIC_RISK_CHARACTERIZATION': (
                'quinze anos de série sistemática, e a leitura de que as fumonisinas '
                'deixaram de ser evento e viraram risco estrutural — uma afirmação que '
                'nenhum boletim semanal produz'),
            'CAUSAL_MECHANISM': (
                'junho acima de 35 °C na segunda metade e estresse hídrico coincidindo '
                'com floração e enchimento de grão: o porquê, não só o quanto'),
            'QUANTIFIED_SEVERITY': '72% acima de 4 mg/kg, 44% acima de 10, 15% de AFB1 não conforme',
            'WHAT_THE_OFFICIAL_LAYER_DID_NOT_HAVE': (
                'a camada oficial dá ocorrência e limite; o pesquisador deu a série, o '
                'mecanismo e a leitura de tendência'),
            'WHAT_THEY_DID_NOT_ADD': (
                'nada sobre o caso principal, e nenhuma localização de fato'),
        },
        'CHANNEL_THAT_PRODUCED_THE_VALUE': 'EVENTO TÉCNICO → IMPRENSA TÉCNICA',

        'STRUCTURAL_FINDING': {
            'STATE': 'RESEARCHER_CHANNEL_IS_RETROSPECTIVE_BY_CALENDAR',
            'EVIDENCE': ('Giornata del Mais em 30/01 relata a safra de milho encerrada em '
                         'outubro; Durum Days em 19/05 relata estimativas de pré-colheita. '
                         'A fusariose do trigo duro se decide na floração, em abril.'),
            'CONSEQUENCE': ('não é atraso de publicação, é o desenho do calendário. Nenhuma '
                            'ferramenta de coleta conserta isso.'),
            'WHAT_IT_IS_GOOD_FOR': 'risco crônico, mecanismo, tendência, contexto de safra',
            'WHAT_IT_CANNOT_DO': 'avisar sobre a safra que está correndo',
        },

        'LAWS': [
            'LINKEDIN_NOT_PRODUCTIVE_IN_MEASURED_PANEL ≠ HUMAN_SENSOR_LAYER_NOT_PRODUCTIVE',
            'PUBLICATION_BEFORE_CASE ≠ EARLY_WARNING',
            'RESEARCHER_CHANNEL_IS_RETROSPECTIVE_BY_CALENDAR',
            'CONTROL_POSITIVE ≠ EXACT_CASE_SIGNAL',
            'SOURCE_GEOGRAPHY ≠ ADMIN_GEOGRAPHY',
            'NOT_FOUND_IN_THIS_SEARCH ≠ DOES_NOT_EXIST',
            'PLACE_MENTION ≠ FACT_LOCATION',
            'PUBLISHED_AT ≠ FACT_TIME',
        ],

        'LINKEDIN_SENSOR_CAPABILITY': linkedin,
        'RESEARCHER_SENSOR_CAPABILITY': pesquisador,
        'HUMAN_SENSOR_LAYER': camada,

        'RECOMMENDATION': {
            'COLLECT': ('imprensa técnica italiana (AgroNotizie, Terra e Vita, '
                        'Informatore Agrario) filtrada por cultura×problema, e os '
                        'calendários de convegni do CREA e das universidades'),
            'WHY': ('é onde o pesquisador realmente fala, com nome, número e citação '
                    'direta — e é gratuito e datado'),
            'DO_NOT_COLLECT': ('mais LinkedIn deste painel; e nenhuma rede social '
                               'escolhida por existir Actor'),
            'EXPECT': ('contexto e risco estrutural, não antecipação. Para antecipação, '
                       'a porta continua sendo o boletim regional oficial.'),
            'STILL_UNMEASURED': ('Francesca Nocente e Daniela Pacifico sem canal próprio '
                                 'achado; OpenAlex esgotado no dia da medição'),
        },

        'STILL_FORBIDDEN_TO_WRITE': ['ITALY OPPORTUNITY', 'SALES OPPORTUNITY',
                                     'ADAMA SHOULD ACT', 'MARKET GAP'],
    }


def main():
    out = medir()
    os.makedirs(os.path.dirname(DEST), exist_ok=True)
    with open(DEST, 'w', encoding='utf-8') as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    print('pesquisadores com canal público :', out['RESEARCHERS_WITH_A_PUBLIC_CHANNEL'], '/ 5')
    print('com conteúdo datado             :', out['RESEARCHERS_WITH_DATED_CONTENT'], '/ 5')
    print('conteúdos lidos                 :', out['CONTENTS_READ_COUNT'])
    for L in out['CONTENTS_READ']:
        print('   %-24s %s  %-12s %-22s %s' % (
            L['ID'][:24], L['PUBLISHED_AT'], L['PUBLICATION_RELATIVE_TO_CASE'],
            L['EARLY_WARNING_STATE'], L['RELEVANCE']))
    print('FACT_LOCATIONS                  :', out['FACT_LOCATIONS_COUNT'])
    print('FIRST_EXACT_CASE_SIGNAL         :', out['FIRST_EXACT_CASE_SIGNAL'])
    print()
    print('LINKEDIN_SENSOR_CAPABILITY   =', out['LINKEDIN_SENSOR_CAPABILITY'])
    print('RESEARCHER_SENSOR_CAPABILITY =', out['RESEARCHER_SENSOR_CAPABILITY'])
    print('HUMAN_SENSOR_LAYER           =', out['HUMAN_SENSOR_LAYER'])
    print('->', os.path.relpath(DEST, ROOT))


if __name__ == '__main__':
    main()
