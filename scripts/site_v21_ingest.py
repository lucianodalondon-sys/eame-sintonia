#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O INGEST DO SITE — a fronteira entre o pacote V2.1 e o portal.

    python3 scripts/site_v21_ingest.py

    le : build/ITALY-REALITY-HANDOFF-V2.1/DESIGN-INGEST/*.json
    escreve: italia-portale/client/italy-handoff-v21.js
             (window.ITALY_HANDOFF_V21 = { referenceDate, buildId, <familia>: [...] })

POR QUE ESTA CAMADA EXISTE
---------------------------
O portal ja tem o gancho: `italy-app-model.js` procura `window.ITALY_HANDOFF_V21`
em primeiro lugar, com precedencia CANONICAL, em toda familia. O que faltava era
alguem que pusesse o pacote la dentro — e que decidisse O QUE dele pode atravessar.

    O QUE NAO ATRAVESSA ESTA LINHA NAO PRECISA SER FILTRADO NA TELA.

Esta e a diferenca entre este ingest e um `JSON.stringify` do pacote inteiro. O
V2.1 foi pesquisado em portugues: 10.832 campos tem par IT/EN aprovado, e os que
nao tem continuam sendo prosa de pesquisa. O modelo do portal ja sabe recusar
prosa nao aprovada (`narrative()` devolve NOT_APPROVED_FOR_DISPLAY), mas recusar
na tela significa que o portugues VIAJOU ATE O NAVEGADOR do cliente italiano
para so entao ser escondido. Uma cor de CSS trocada, um `title=` esquecido, um
`JSON.stringify` num painel de depuracao, e ele aparece.

    PROSA QUE NAO EMBARCA NAO VAZA.

Por isso o filtro e uma LISTA DE PERMISSAO, campo a campo, e nao uma lista de
proibicao. Campo que ninguem declarou fica de fora — inclusive campo novo que um
build futuro venha a inventar. O custo disso e ter de declarar o campo aqui
quando uma tela passar a precisar dele; o beneficio e que o silencio e o padrao.

TRES ESTADOS, NAO DOIS
-----------------------
Para cada campo localizavel o pacote pode estar em tres estados, e eles NAO se
colapsam em "tem texto" / "nao tem":

    CAMPO_IT + CAMPO_EN   ->  atravessa
    so prosa em portugues ->  atravessa `CAMPO__PT_ONLY: true`, sem o texto
    nada                  ->  nao atravessa nada

O estado do meio existe porque "a fonte nao estabeleceu isto" e "a fonte
escreveu isto e nao esta aprovado para exibicao" sao fatos DIFERENTES sobre o
estado do conhecimento, e o painel de divida de traducao (`AM.ingest.narrativeDebt`)
conta o segundo. Jogar a prosa fora sem deixar marca faria a divida sumir do
relatorio — o defeito ficaria invisivel em vez de resolvido.

O QUE ESTE SCRIPT NAO FAZ
--------------------------
Nao normaliza. Nao resolve cultura, avversita nem regiao. Nao calcula dia
nenhum. Isso e trabalho do `italy-app-model.js`, que ja tem os resolvedores e o
relogio unico — e ter DOIS lugares resolvendo cultura e como o projeto acabaria
com duas telas discordando sobre a mesma videira.

    ESTE SCRIPT ESCOLHE O QUE ATRAVESSA. QUEM DA FORMA E O MODELO.
"""
import hashlib
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ING = os.path.join(ROOT, 'build', 'ITALY-REALITY-HANDOFF-V2.1', 'DESIGN-INGEST')
OUT = os.path.join(ROOT, 'italia-portale', 'client', 'italy-handoff-v21.js')

# Campos que TODO registro do V2.1 carrega (§8 do contrato) e que o portal usa
# para procedencia, rastreio e cruzamento. Passam em toda colecao.
COMUNS = (
    'ID', 'ENTITY_TYPE', 'PROVENANCE', 'QA_STATUS', 'CLIENT_SAFE',
    'SOURCE_IDS', 'SOURCE_URLS', 'REFERENCE_DATE',
    'CROP_IDS', 'ISSUE_IDS', 'REGION_IDS', 'GEOGRAPHIC_SCOPE',
    'ORIGIN_LAYER', 'EVIDENCE_STATUS',
)

# familia do modelo -> (arquivo do pacote, fatos que atravessam, campos localizaveis)
#
# Fato e data, enum, nome proprio, numero, URL ou citacao publica original: passa
# como esta. Localizavel e prosa: passa so o par IT/EN aprovado.
FAMILIAS = {
    'productsRegulatory': ('PRODUCTS-REGULATORY.json', (
        'NAME', 'REGISTRATION_NUMBER', 'AUTHORIZATION_HOLDER', 'ACTIVE_INGREDIENTS',
        'FORMULATION', 'REGULATORY_CATEGORY', 'LINE', 'STATUS', 'EXPIRY',
        'MODE_OF_ACTION_DECLARED', 'LABEL_URL', 'IN_PUBLIC_CATALOG_FLAG',
    ), ('EVIDENCE_STATUS_WHY',)),

    'productsCommercial': ('PRODUCTS-COMMERCIAL.json', (
        'NAME', 'CATEGORY', 'CATEGORY_SOURCE', 'PUBLIC_CATALOG_URL',
        'CROPS_DECLARED_ON_SITE', 'ACTIVE_INGREDIENTS', 'REGISTRATION_NUMBER_ON_PAGE',
        'CATALOG_EVIDENCE', 'CATALOG_STATUS', 'AUTHORIZATION_HOLDER', 'HOLDER_IS_ADAMA',
        'MATCHED_REGULATORY_ID', 'NOT_A_PLANT_PROTECTION_PRODUCT', 'IS_SYSTEM_NOT_PRODUCT',
        'COMMERCIAL_CONTRACT',
    ), ('COMMERCIAL_CONTRACT_WHY',)),

    # As 2.030 duplas de uso de rotulo. E a colecao mais pesada do pacote e a
    # mais citada pelas outras: e dela que saem CULTURAS = 35 e ALVOS = 78.
    'productRelationships': ('PRODUCT-RELATIONSHIPS.json', (
        'PRODUCT_NAME', 'REGISTRATION_NUMBER', 'CROP_ON_LABEL', 'TARGET_ON_LABEL',
        'TARGET_AS_WRITTEN', 'TARGET_KIND', 'WEED_GROUP', 'LINK_STRENGTH',
        'QUOTE_FROM_LABEL',
    ), ('LINK_MEANS', 'WHAT_IT_DOES_NOT_PROVE', 'EVIDENCE_STATUS_WHY')),

    'activeIngredients': ('ACTIVE-INGREDIENTS.json', (
        'NAME', 'NORMALIZED_NAME', 'ITALIAN_REGISTRATION_COUNT',
        'HRAC', 'HRAC_WSSA', 'CHEMICAL_FAMILY', 'IRAC', 'IRAC_SUBGROUP',
        'FRAC', 'FRAC_SOURCE_VERSION', 'MOA_STATE',
        'EU_STATE', 'EU_DATE_OF_APPROVAL', 'EU_EXPIRATION_OF_APPROVAL', 'EU_CELEX',
        'EU_RENEWAL_STATE', 'CAS', 'CIPAC',
    ), ('WHAT_IT_DOES_NOT_PROVE',)),

    'productActiveIngredients': ('PRODUCT-ACTIVE-INGREDIENTS.json', (
        'PRODUCT_ID', 'PRODUCT_NAME', 'REGISTRATION_NUMBER',
        'ACTIVE_INGREDIENT_ID', 'ACTIVE_INGREDIENT', 'IS_MIXTURE_COMPONENT',
        'COMPONENTS_IN_PRODUCT', 'COMMERCIAL_CATALOG_PRODUCTS',
    ), ('WHAT_IT_DOES_NOT_PROVE', 'EVIDENCE_STATUS_WHY')),

    # As 7 leituras por cultura x avversita. O arquivo chama-se CROP-WINDOWS,
    # mas os IDs (IT-WIN-001..007) sao os mesmos que alimentavam
    # currentFieldSignals — as 29 janelas canonicas sao outra coisa e continuam
    # vindo de ITALY_CANONICAL, que o V2.1 nao substitui.
    'currentFieldSignals': ('CROP-WINDOWS.json', (
        'CROP', 'REGION', 'ISSUE', 'REGULATORY_ACT', 'REGULATORY_ACT_STATE',
        'COVERAGE_STATE', 'SOURCE_ID', 'PROVENANCE_STATE', 'PROVENANCE_STRENGTH',
    ), (
        'EXPECTED_CYCLE', 'OBSERVED_STAGE', 'FIELD_REPORTED_STAGE',
        'REGULATORY_WINDOW', 'MONITORING_WINDOW', 'APPLICATION_WINDOW_2026',
        'NEXT_IMPORTANT_WINDOW', 'PREPARATION_WINDOW', 'ADAMA_PRODUCTS_NOTE',
        'WHAT_IT_DOES_NOT_PROVE', 'EVIDENCE_STATUS_WHY',
    )),

    # Os 122 boletins regionais. Familia nova: o modelo nao tinha slot para
    # leitura de boletim, so para a sintese por cultura.
    'fieldBulletins': ('CURRENT-FIELD-SIGNALS.json', (
        'BULLETIN_TITLE', 'BULLETIN_NUMBER', 'PHENOLOGICAL_STAGE_DECLARED',
        'PESTS_AND_DISEASES_CITED', 'CROP_STATE', 'CROPS_DECLARED', 'CITATION',
        'OBSERVATION_CLASS', 'PROVINCE_IDS', 'AREAL_IDS', 'GEOGRAPHY_STATE',
        'REGION_REPRESENTS', 'GEOGRAPHY_EVIDENCE', 'GEOGRAPHY_BATCH_LABEL',
    ), ('INTERVENTION_GUIDANCE', 'EVIDENCE_STATUS_WHY')),

    # Peso economico por cultura x geografia x ano. NAO e o "alcance no corpus
    # de rotulos" que a familia cropEconomicWeight mostrava: aquilo se remede
    # das 2.030 duplas, no modelo. Este e um fato de mercado, e entra como tal.
    'cropEconomics': ('CROP-ECONOMIC-WEIGHT.json', (
        'CROP_LITERAL', 'CROP_CODE', 'GEOGRAPHY', 'GEOGRAPHY_CODE', 'GEOGRAPHY_LEVEL',
        'YEAR', 'INDICATOR', 'VALUE', 'UNIT', 'IS_DERIVED_BY_SINTONIA',
        'DERIVATION_FORMULA', 'DATASET', 'OBSERVATION_CLASS',
    ), ('CAVEAT',)),

    'marketObservations': ('MARKET-OBSERVATIONS.json', (
        'GROUP', 'PRODUCT', 'MARKET', 'PRICE_RAW', 'PRICE_NUM', 'UNIT', 'STAGE',
        'REFERENCE_PERIOD', 'PUBLICATION_DATE', 'GEOGRAPHY', 'PREV_PRICE_NUM',
        'CHANGE_VS_PREV_PCT', 'YEAR_AGO_PRICE_NUM', 'CHANGE_VS_YEAR_AGO_PCT',
        'SERIES_STATE', 'OBSERVATIONS_IN_SERIES', 'SOURCE_ID', 'COMMODITY_STAGE',
        'PROVENANCE_PUBLISHER_URL', 'PROVENANCE_STATE', 'PROVENANCE_STRENGTH',
    ), ('SERIES_WARNING', 'EVIDENCE_STATUS_WHY')),

    # A FAMILIA TEM DUAS FORMAS, E A LISTA SO CONHECIA UMA.
    # 561 registros sao ANUNCIOS observados: tem anunciante, plataforma, peca.
    # Os outros 16 sao NOTAS DE OBSERVACAO: nao tem nenhum desses campos e
    # trazem, no lugar, OBSERVATION_CLASS, CONFIDENCE, CLAIM_DOMAIN e um par
    # WHAT_IT_PROVES / WHAT_IT_DOES_NOT_PROVE ja traduzido e aprovado.
    # A lista antiga nao guardava nenhum desses campos, entao os 16 chegavam
    # como envelope vazio e o modelo os recusava por «no company» — 8 deles
    # CLIENT_SAFE e com QA aprovado, invisiveis sem que tela alguma dissesse.
    # WHAT_IT_IS fica DE FORA de proposito: e a nota de pesquisa em portugues.
    'competitorActivities': ('COMPETITOR-ACTIVITIES.json', (
        'ACTIVITY_TYPE', 'PLATFORM', 'COMPANY', 'PAGE', 'PAGE_ID',
        'COUNTRY_REACHED', 'COUNTRY_SEMANTICS', 'START_DATE', 'END_DATE',
        'ACTIVE_STATUS', 'MEDIA_TYPE', 'PRODUCTS_PROVED', 'CROP_TERMS', 'ISSUE_TERMS',
        'CREATIVE_TEXT', 'AD_URL', 'SOURCE_ID',
        'PROVENANCE_STATE', 'PROVENANCE_STRENGTH',
        'OBSERVATION_CLASS', 'CONFIDENCE', 'CLAIM_DOMAIN', 'SOURCE_SCOPE',
    ), ('EVIDENCE_STATUS_WHY', 'WHAT_IT_PROVES', 'WHAT_IT_DOES_NOT_PROVE')),

    'scienceRecords': ('SCIENCE.json', (
        'TITLE', 'DOI', 'AUTHOR', 'ORCID', 'INSTITUTION', 'PUBLISHED_AT', 'VENUE',
        'MATERIAL_TYPE', 'MATERIAL_ROLE', 'CROP', 'ISSUE', 'COUNTRY_OF_FACT',
        'SOURCE_URL', 'SOURCE_ID',
    ), ('EVIDENCE_STATUS_WHY',)),

    'researchers': ('RESEARCHERS.json', (
        'CATEGORY', 'PERSON', 'ORCID', 'OPENALEX_ID', 'INSTITUTIONS', 'THEME',
        'WORKS_IN_SCOPE', 'LAST_ACTIVITY', 'IDENTITY_STATUS', 'ROLE', 'FACT_REGION',
        'SOURCE_ID', 'PROVENANCE_STATE', 'PROVENANCE_STRENGTH',
    ), ('EVIDENCE_STATUS_WHY',)),

    'resistance': ('RESISTANCE.json', (
        'SPECIES', 'SPECIES_IT', 'FAMILY', 'CROP_DECLARED', 'FIRST_CASE_YEAR',
        'REGIONS', 'CITATION', 'AUTHORITY', 'SOURCE_URL', 'SOURCE_ID',
    ), ('MECHANISM', 'MULTIPLE_RESISTANCE', 'EVIDENCE_STATUS_WHY')),

    'publicVoices': ('PUBLIC-VOICES.json', (
        'KIND', 'CHANNEL_AUDIENCE_KIND', 'CHANNEL_AUDIENCE_EVIDENCE',
        'PERSON', 'PERSON_IDENTITY_STATE', 'ROLE', 'ORGANIZATION', 'PLATFORM',
        'CHANNEL', 'CONTENT_TITLE', 'DATE', 'DATE_RELATIVE', 'DATE_NOTE',
        'CROP', 'ISSUE', 'CASE_ID', 'REGION', 'COUNTRY_OF_FACT',
        'TEXT_ORIGINAL', 'SOURCE_URL', 'SOURCE_ID', 'VOICE_ID', 'PERSON_ID',
        'SOURCE_DOCUMENT_ID', 'VOICE_KIND', 'ROLE_EVIDENCE',
    ), ('WHAT_IT_PROVES', 'WHAT_IT_DOES_NOT_PROVE')),

    'publicChannels': ('PUBLIC-CHANNELS.json', (
        'CHANNEL', 'CHANNEL_URL', 'IDENTITY_STATE', 'CONTENT_TYPE_EXAMPLE',
        'EXAMPLE_TITLE', 'EXAMPLE_URL', 'EXAMPLE_PUBLISHED_AT', 'VIEWS', 'CASE_ID',
        'PROVENANCE_STATE',
    ), ('EVIDENCE_STATUS_WHY',)),

    'sources': ('SOURCES.json', (
        'SOURCE_ID', 'NAME', 'TYPE', 'COUNTRY', 'GEOGRAPHY', 'URL', 'FREQUENCY',
        'LATEST_OBSERVATION', 'ACCESS_STATUS', 'RUNTIME_DEPENDENCY',
        'ID_ANTERIOR', 'ID_ALIASES', 'PROVENANCE_STATE',
        'ACCESS_EVIDENCE', 'ACCESS_EVIDENCE_MEASURED',
        'REQUIRES_ITALIAN_ROUTE', 'ROUTE_EVIDENCE_NOTE',
    ), ('ROLE', 'LIMITATIONS', 'EVIDENCE_STATUS_WHY')),

    'futureEvents': ('FUTURE-EVENTS.json', (
        'EVENT', 'DATE', 'LOCATION', 'SECTOR', 'CROP_RELEVANCE', 'ORGANIZER',
        'OFFICIAL_URL', 'EXHIBITOR_LIST_STATE', 'TIME_STATE', 'CONFIRMED_PARTICIPATION',
        'START_DATE', 'END_DATE', 'DATE_PRECISION', 'DATE_SOURCE', 'DATE_PARSE_STATE',
    ), ('PARTICIPATION_LAW', 'NOTE', 'EVIDENCE_STATUS_WHY')),

    'events': ('EVENTS.json', (
        'EVENT', 'DATE', 'LOCATION', 'SECTOR', 'CROP_RELEVANCE', 'ORGANIZER',
        'OFFICIAL_URL', 'EXHIBITOR_LIST_STATE', 'TIME_STATE', 'CONFIRMED_PARTICIPATION',
    ), ('PARTICIPATION_LAW', 'NOTE', 'EVIDENCE_STATUS_WHY')),

    'news': ('NEWS.json', (
        'PUBLISHER', 'TITLE', 'AUTHOR', 'DATE', 'CROP', 'ISSUE', 'REGION',
        'CONTENT_KIND', 'SOURCE_URL',
    ), ('CONTENT_KIND_MEANING', 'SINTONIA_SUMMARY', 'CAVEAT', 'EVIDENCE_STATUS_WHY')),

    'regulatoryFuture': ('REGULATORY-FUTURE.json', (
        'OBSERVATION_CLASS', 'CONFIDENCE', 'SOURCE_SCOPE', 'CLAIM_DOMAIN',
    ), ('WHAT_IT_IS', 'WHAT_IT_PROVES', 'WHAT_IT_DOES_NOT_PROVE')),

    'regulatoryFutureFacts': ('REGULATORY-FUTURE-FACTS.json', (
        'ACTIVE_INGREDIENT', 'ACTIVE_INGREDIENT_ID', 'EU_STATE',
        'EU_EXPIRATION_OF_APPROVAL', 'EU_CELEX', 'ITALIAN_REGISTRATIONS',
        'ITALIAN_REGISTRATION_COUNT', 'COMMERCIAL_CATALOG_PRODUCTS',
        'VERIFIED_LABEL_CROPS', 'VERIFIED_LABEL_CROPS_STATE',
        'IS_OPPORTUNITY', 'IS_RISK',
    ), ('WHAT_IT_PROVES', 'WHAT_IT_DOES_NOT_PROVE')),

    'futureSignals': ('FUTURE-SIGNALS.json', (
        'LEGACY_ID', 'CROP', 'ISSUE', 'REGION', 'PROMOTED_TO_RADAR',
    ), (
        'WHO_IS_TALKING', 'WHAT_CHANGED', 'WHY_WATCH', 'HOW_SINTONIA_GOT_HERE',
        'OBSERVED_FACTS', 'SINTONIA_INTERPRETATION', 'UNKNOWN', 'NEXT_WINDOW',
        'PORTFOLIO_CONNECTION', 'WHAT_WOULD_MAKE_IT_AN_OPPORTUNITY',
        'EVIDENCE_STATUS_WHY',
    )),

    # O motor de oportunidades. RENDERABLE_WITH_METHOD e CLIENT_SAFE atravessam
    # porque o modelo precisa deles para DECIDIR o rotulo — e sao removidos do
    # objeto que chega a tela, no proprio modelo. Ver a nota em italy-app-model.js.
    'opportunities': ('OPPORTUNITIES.json', (
        'RENDERABLE_WITH_METHOD', 'OPPORTUNITY_STATE', 'ARCHETYPE', 'STATUS',
        'CROP', 'TARGET', 'GEOGRAPHY', 'WINDOW_START', 'WINDOW_END',
        'DAYS_REMAINING', 'WINDOW_STATE', 'SIGNAL_DATE', 'SIGNAL_AGE_DAYS',
        'NUMBERS', 'PRODUCT_LINK_STATE', 'PRODUCT_RELATIONSHIPS',
        'EVIDENCE_IDS', 'EVIDENCE_FAMILIES', 'EVIDENCE_COUNT',
        'CONFIDENCE', 'OPPORTUNITY_SCORE', 'SCORE_DIMENSIONS', 'ACTION_MAP',
        'IDENTITY_KEY', 'MERGED_FROM',
        # ── A CAMADA COMERCIAL V1.1 ATRAVESSA A FRONTEIRA ────────────────────
        # Ate aqui o portal mantinha a SUA PROPRIA regua de material externo
        # (`rtvEligibility`, em italy-app-model.js), derivada do que a tela via.
        # O motor passou a decidir a mesma coisa com mais dado do que a tela
        # tem — catalogo publico, oracao de meio da fonte, portoes de evidencia.
        #
        #     UMA REGUA DUPLICADA SAO DUAS REGUAS QUE VAO DIVERGIR.
        #
        # Entao o veredito do motor atravessa, e a regua do portal passa a ser a
        # RESERVA para quando o registro nao o traz. Sao CODIGOS e listas de
        # codigos, nunca prosa de pesquisa: as frases correspondentes vivem no
        # dicionario de lingua do portal, do lado de ca.
        'COMMERCIAL_PRIORITY', 'WHY_COMMERCIAL_CODES',
        'EXTERNAL_MATERIAL_READY', 'EXTERNAL_BLOCKER_CODES',
        # ⚠️ `SOURCE_PRESCRIBED_MEANS` NAO atravessa: e um pedaco literal do
        # NEED_EXCERPT, e o V2.1 foi pesquisado em PORTUGUES. Quem precisa da
        # frase inteira le a ficha do caso do lado de ca da fronteira; a tela
        # nomeia a substancia do NOSSO produto, que e fato e nao prosa.
        'CASE_ACTIVE_INGREDIENTS',
        'NEED_DIRECTION', 'NEED_EVIDENCE_ID', 'NEED_METHOD',
    ), ('WHAT_IT_PROVES', 'WHAT_IT_DOES_NOT_PROVE')),

    'agrometConditions': ('AGROMET-CONDITIONS.json', (
        'OBSERVATION_CLASS', 'CONFIDENCE', 'SOURCE_SCOPE',
    ), ('WHAT_IT_IS', 'WHAT_IT_PROVES', 'WHAT_IT_DOES_NOT_PROVE')),

    'clientSafeCrossings': ('CLIENT-SAFE-CROSSINGS.json', (
        'CROSSING_TYPE', 'CROP_ID', 'GEOGRAPHIC_CLAIM', 'GEOGRAPHIC_CLAIM_SCOPE',
        'GEOGRAPHIC_COVERAGE_PROVINCES', 'GEOGRAPHIC_COVERAGE_REGIONS',
        'SUPPORTING_IDS', 'SUPPORTING_QA', 'ALL_SUPPORT_CLIENT_SAFE',
        'RENDERABLE_WITH_METHOD', 'INVARIANTS_PROVEN', 'INVARIANTS_NOT_APPLICABLE',
        'LABEL_LINK_STRENGTHS',
    ), ('WHAT_IT_LETS_YOU_ASK', 'WHAT_IT_DOES_NOT_PROVE')),

    'relationships': ('RELATIONSHIPS.json', (
        'CROSSING_TYPE', 'CROP_ID', 'LINKS', 'RENDERABLE_WITH_METHOD',
    ), ()),
}

# Colecoes que o pacote traz e que NAO viram familia de tela. Declaradas aqui
# para que "nao entrou" seja uma decisao registrada e nao um esquecimento.
FORA = {
    'APP-MANIFEST.json': 'cabecalho do pacote; entra como meta, nao como familia',
    'CANONICAL-INTELLIGENCE-MASTER.json':
        'indice mestre de 6.876 registros. O portal ja constroi o seu proprio '
        'indice (APP.archive) sobre as familias normalizadas; embarcar o mestre '
        'seria a mesma verdade duas vezes, e as duas envelheceriam separado.',
    'OPPORTUNITY-EVIDENCE.json': 'entra achatado em opportunityEvidence',
    'OPPORTUNITY-REJECTIONS.json':
        'as 17 derrubadas pelo red team. NAO embarcam: oportunidade rejeitada '
        'que viaja ate o navegador e uma que alguem ainda pode renderizar.',
    'OPPORTUNITY-RULES.json': 'entra achatado em opportunityRules',
}


# ── O DETECTOR DE PORTUGUES, LIDO DA REGUA ─────────────────────────────────
# A lista de marcadores mora em `italia-portale/audit/lang.mjs` e e a mesma que
# a regua usa em PT1. Ela e LIDA daqui, nao copiada: duas listas com o mesmo
# proposito divergem, e a que diverge em silencio e sempre a que nao falha.
#
#     UMA LEI, UM LUGAR. COPIA DE LEI E LEI QUE VAI ENVELHECER SOZINHA.
def _marcadores():
    src = io.open(os.path.join(ROOT, 'italia-portale', 'audit', 'lang.mjs'),
                  encoding='utf-8').read()
    bloco = src[src.index('export const PT_MARKERS'):]
    bloco = bloco[bloco.index('['):bloco.index(']')]
    # ⚠️ O COMENTARIO NAO E A LISTA.
    # A primeira versao deste leitor pegava toda palavra entre aspas simples no
    # bloco — inclusive as que estao DENTRO dos comentarios, que e onde aquele
    # arquivo explica quais tokens foram deliberadamente DEIXADOS DE FORA por
    # serem ambiguos. Resultado medido: o comentario que diz «'epoca' saiu desta
    # lista, como 'mais' e 'per'» reintroduziu exatamente 'epoca', 'mais' e
    # 'per' como marcadores. 'MAIS' e milho em italiano, entao a cultura sumiu
    # do corpus de rotulo: 35 culturas viraram 34, e nada acusou.
    #
    #     LER A EXPLICACAO COMO SE FOSSE A REGRA E COMO
    #     EXECUTAR A NOTA DE RODAPE.
    #
    # Os comentarios saem primeiro; so entao as aspas contam.
    bloco = re.sub(r'/\*.*?\*/', ' ', bloco, flags=re.S)
    bloco = re.sub(r'//[^\n]*', ' ', bloco)
    return [m.group(1) for m in re.finditer(r"'([^']+)'", bloco)]


MARCADORES = _marcadores()
PT = re.compile('(^|[^^\\w])(' + '|'.join(map(re.escape, MARCADORES)) + ')([^\\w]|$)',
                re.IGNORECASE | re.UNICODE)
# A LISTA DE MARCADORES DECIDE O QUE EMBARCA, ENTAO ELA FAZ PARTE DA ENTRADA.
# Medido em 2026-09-03: tirar um unico marcador ambiguo ('epoca', que e italiano
# corrente) mudou 16 das 26 familias do arquivo gerado. Quem edita lang.mjs e
# nao roda este script de novo fica com um pacote embarcado que obedece a uma lei
# que ja nao existe — e nada quebra, porque o arquivo continua valido.
#
#     ENTRADA QUE NAO APARECE NO ARTEFATO E ENTRADA QUE VAI FICAR PARA TRAS.
#
# Por isso a assinatura da lista viaja dentro do arquivo, e o portao a confere.
ASSINATURA = hashlib.sha256('\n'.join(MARCADORES).encode('utf-8')).hexdigest()[:16]

# A fonte diz "nao estabelecido" de nove maneiras, e todas as nove vem com uma
# explicacao em portugues colada atras. O ESTADO e um fato e sobrevive; a
# explicacao e nota de pesquisa e fica.
NAO_ESTABELECIDO = 'NOT_ESTABLISHED'
SENTINELA = re.compile(
    r'^\s*(N[AÃ]O[ _]?SEI|N[AÃ]O[ _]SE[ _]APLICA|N[AÃ]O[ _]CONSULTADA|'
    r'N[AÃ]O[ _]ATRIBUIVEL|NENHUMA?|SEM[ _]NUMERO|NOT[ _]KNOWN|UNKNOWN|'
    r'FONTE[ _]N[AÃ]O[ _]DECLARADA)\b', re.IGNORECASE)
# `ESTADO — explicacao`: o token controlado a frente, a prosa atras.
TOKEN_E_GLOSA = re.compile(r'^\s*([A-Z][A-Z0-9_]{2,})\s*[—–\-:·(]')
ISO = re.compile(r'^(\d{4}-\d{2}-\d{2})')

# Citacao publica original e identidade taxonomica nao se julgam e nao se
# cortam: sao a prova, e `L3` proibe entregar um nome de especie pela metade.
LITERAIS = frozenset((
    'QUOTE_FROM_LABEL', 'CREATIVE_TEXT', 'TEXT_ORIGINAL', 'CITATION',
    'SPECIES', 'SPECIES_IT', 'DERIVATION_FORMULA',
))
DATAS = frozenset((
    'REFERENCE_DATE', 'DATE', 'START_DATE', 'END_DATE', 'PUBLICATION_DATE',
    'EXPIRY', 'LAST_ACTIVITY', 'PUBLISHED_AT', 'EXAMPLE_PUBLISHED_AT',
    'EU_DATE_OF_APPROVAL', 'EU_EXPIRATION_OF_APPROVAL', 'SIGNAL_DATE',
    'WINDOW_START', 'WINDOW_END', 'FIRST_CASE_YEAR', 'LATEST_OBSERVATION',
))


def limpar(chave, v):
    """(valor que atravessa, ha prosa retida?) para UM campo de fato.

    Um campo de fato pode chegar em quatro estados, e so o primeiro atravessa
    inteiro:

        fato limpo              -> atravessa
        ESTADO + glosa em pt    -> atravessa so o ESTADO
        sentinela de nao-saber  -> atravessa NOT_ESTABLISHED
        prosa de pesquisa       -> nao atravessa; fica a marca

    O quarto caso e o que apanhou o titulo do boletim de Puglia, que e italiano
    limpo com «(NAO e fitossanitario)» colado no fim. Cortar o parenteses seria
    editar a evidencia; embarcar a frase seria por portugues na tela do cliente.
    Entao o titulo nao vai, a marca vai, e a divida aparece no painel — que e
    onde ela pode ser resolvida a montante, que e onde ela nasceu.
    """
    if not isinstance(v, str) or not v.strip():
        return v, False
    t = v.strip()
    if SENTINELA.match(t):
        return NAO_ESTABELECIDO, False
    if chave in DATAS:
        m = ISO.match(t)
        if m:
            return m.group(1), False
        if re.fullmatch(r'\d{4}', t):
            return t, False
        return NAO_ESTABELECIDO, False
    if chave in LITERAIS:
        return t, False
    if PT.search(t):
        m = TOKEN_E_GLOSA.match(t)
        if m and not PT.search(m.group(1)):
            return m.group(1), False
        return None, True
    return t, False


def txt(v):
    return v if isinstance(v, str) and v.strip() else None


def projetar(rec, fatos, localizaveis):
    """Um registro, reduzido ao que pode atravessar."""
    out = {}
    for k in COMUNS + tuple(fatos):
        if k not in rec or rec[k] is None:
            continue
        v = rec[k]
        if isinstance(v, str):
            v, retida = limpar(k, v)
            if retida:
                out[k + '__PT_ONLY'] = True
                continue
            if v is None:
                continue
        elif isinstance(v, dict) and any(isinstance(x, str) for x in v.values()):
            # UM CAMPO ANINHADO CONTINUA A SER UM CAMPO.
            # CONFIRMED_PARTICIPATION chega como {'ADAMA': 'CONFIRMADO — a propria
            # ADAMA publica ...'}: o portao lia o dicionario como um todo, nao via
            # texto nenhum e deixava passar a glosa em portugues inteira. Cada
            # valor de dentro passa agora pela mesma regra dos campos planos, que
            # ja sabe manter o ESTADO e deixar a prosa para tras.
            limpos, retida = {}, False
            for kk, x in v.items():
                if not isinstance(x, str):
                    limpos[kk] = x
                    continue
                y, r = limpar(kk if kk in DATAS else k, x)
                retida = retida or r
                if not r and y is not None:
                    limpos[kk] = y
            if retida:
                out[k + '__PT_ONLY'] = True
            if limpos:
                out[k] = limpos
            continue
        elif isinstance(v, list) and any(isinstance(x, str) for x in v):
            limpos, retida = [], False
            for x in v:
                if isinstance(x, str):
                    y, r = limpar(k, x)
                    retida = retida or r
                    if y is not None:
                        limpos.append(y)
                else:
                    limpos.append(x)
            if retida:
                out[k + '__PT_ONLY'] = True
            v = limpos
        out[k] = v
    for base in localizaveis:
        it, en = txt(rec.get(base + '_IT')), txt(rec.get(base + '_EN'))
        if it or en:
            out[base + '_IT'] = it or en
            out[base + '_EN'] = en or it
        elif txt(rec.get(base)) or txt(rec.get(base + '_ORIGINAL_RESEARCH_TEXT')):
            # A fonte escreveu, e nao ha versao aprovada. O texto fica para tras;
            # a DIVIDA atravessa, para o painel de traducao continuar a conta-la.
            out[base + '__PT_ONLY'] = True
    return out


NUL = '\x00'
POOL_MIN = 16   # abaixo disto o indice custa mais do que a string


def internar(payload):
    """As frases da LEI repetem-se por registro; o texto delas nao e um fato do registro.

    `LINK_MEANS` tem TRES valores distintos e 2.030 registros. `CAVEAT` tem
    poucos e 2.978. Gravar a mesma sentenca milhares de vezes fez o pacote sair
    com 9,1 MB, dos quais a maior parte era a mesma frase copiada — e um arquivo
    que o navegador tem de baixar inteiro antes de a primeira tela existir.

        FRASE DE LEI NAO E DADO DO REGISTRO: E DADO DA REGRA QUE ELE OBEDECE.

    Entao cada string longa que aparece mais de uma vez vai para um cesto e o
    registro guarda o indice. A troca e SEM PERDA e desfeita no proprio arquivo
    gerado, antes de qualquer outro script correr: quem le
    `window.ITALY_HANDOFF_V21` recebe um objeto comum, com as strings no lugar.
    Nenhum modelo e nenhuma tela sabe que isto aconteceu.

    O marcador e um NUL a frente do indice. Nenhum texto do pacote comeca com
    NUL, entao a decodificacao nao tem como confundir conteudo com referencia.
    """
    contagem = {}

    def contar(v):
        if isinstance(v, str):
            if len(v) >= POOL_MIN:
                contagem[v] = contagem.get(v, 0) + 1
        elif isinstance(v, list):
            for x in v:
                contar(x)
        elif isinstance(v, dict):
            for x in v.values():
                contar(x)

    contar(payload)
    pool = sorted(s for s, n in contagem.items() if n > 1)
    idx = {s: i for i, s in enumerate(pool)}

    def trocar(v):
        if isinstance(v, str):
            return NUL + str(idx[v]) if v in idx else v
        if isinstance(v, list):
            return [trocar(x) for x in v]
        if isinstance(v, dict):
            return {k: trocar(x) for k, x in v.items()}
        return v

    corpo = json.dumps(trocar(payload), ensure_ascii=False, sort_keys=True,
                       separators=(',', ':'))
    return corpo, pool


# O desfazer do cesto, embutido no proprio arquivo gerado. Roda uma vez, antes
# de qualquer outro script tocar em `window.ITALY_HANDOFF_V21`, e devolve um
# objeto comum — nenhum consumidor precisa saber que houve compressao.
REIDRATA = (
    "  function R(v) {\n"
    "    if (typeof v === 'string') return v.charCodeAt(0) === 0 ? P[+v.slice(1)] : v;\n"
    "    if (Array.isArray(v)) { for (var i = 0; i < v.length; i++) v[i] = R(v[i]); return v; }\n"
    "    if (v && typeof v === 'object') { for (var k in v) v[k] = R(v[k]); return v; }\n"
    "    return v;\n"
    "  }\n"
)


def carregar(arq):
    p = os.path.join(ING, arq)
    if not os.path.exists(p):
        raise SystemExit('pacote V2.1 ausente: %s\n'
                         'rode antes: bash scripts/v21_cadeia.sh' % p)
    return json.load(io.open(p, encoding='utf-8'))


CONTRATO = os.path.join(ROOT, 'italia-portale', 'audit',
                        'CANONICAL-PACKAGE-CONTRACT.json')


def recusas_de_proveniencia(manifesto, oportunidades):
    """Por que este pacote NAO pode virar o artefacto servido.

    A regra nao nasce aqui: le-se de CANONICAL-PACKAGE-CONTRACT.json, o mesmo
    ficheiro que o portao em JS le. Uma regra escrita em duas linguas diverge na
    terceira vez que alguem a muda.

    Esta e a porta por onde a safra velha entrava: a cadeia local desta linhagem
    esta atrasada, e este script transformava o que ela produzisse no ficheiro
    que o browser carrega, sem perguntar de onde vinha.

        INGERIR SEM VERIFICAR NAO E CONFIAR NA ORIGEM. E NAO TER ORIGEM.
    """
    C = json.load(io.open(CONTRATO, encoding='utf-8'))
    build_id = manifesto.get('BUILD_ID')
    regra = manifesto.get('MEETING_SURFACE_RULE')
    estados = {}
    for r in oportunidades:
        v = r.get('STATUS')
        if v:
            estados[v] = estados.get(v, 0) + 1

    r = []
    if build_id != C['EXPECTED_BUILD_ID']:
        r.append('BUILD_ID %s != %s' % (build_id or '(ausente)', C['EXPECTED_BUILD_ID']))
    if len(oportunidades) != C['EXPECTED_CASES']:
        r.append('CASOS %d != %d' % (len(oportunidades), C['EXPECTED_CASES']))
    if not regra:
        r.append('MEETING_SURFACE_RULE ausente — a superficie teria de adivinhar a faixa')
    else:
        for f in C['SURFACE_RULE_FIELDS']:
            if f not in regra:
                r.append('MEETING_SURFACE_RULE sem %s' % f)
    for e in C['REVOKED_STATES']:
        if estados.get(e):
            r.append('ESTADO REVOGADO %s em %d casos' % (e, estados[e]))
    conhecido = C.get('STALE_KNOWN_BUILD_IDS', {}).get(build_id)
    if conhecido:
        r.append('safra conhecida como velha: %s' % conhecido)
    return r, C


def main():
    if not os.path.isdir(ING):
        raise SystemExit('pacote V2.1 ausente em %s\n'
                         'a cadeia canonica NAO e a desta linhagem — ver '
                         'italia-portale/audit/CANONICAL-PACKAGE-CONTRACT.json' % ING)

    manifesto = carregar('APP-MANIFEST.json')
    build_id = manifesto.get('BUILD_ID')

    # FAIL-CLOSED. Antes de projetar uma unica linha, o pacote prova de onde vem.
    _opp = carregar('OPPORTUNITIES.json')
    _opp = _opp.get('RECORDS') if isinstance(_opp, dict) else _opp
    _recusas, _C = recusas_de_proveniencia(manifesto, _opp or [])
    if _recusas:
        g = _C['CANONICAL_GENERATOR']
        raise SystemExit(
            'INGESTAO RECUSADA — o pacote nao prova a sua proveniencia:\n'
            + '\n'.join('  · ' + x for x in _recusas)
            + '\n\n  O gerador canonico e %s @ %s.\n'
              '  A cadeia local desta linhagem esta atrasada e nao deve regenerar.\n'
            % (g['LINHAGEM'], g['COMMIT'][:7]))

    saida = {}
    medido = {}
    for familia, (arq, fatos, loc) in sorted(FAMILIAS.items()):
        d = carregar(arq)
        recs = d.get('RECORDS') or []
        saida[familia] = [projetar(r, fatos, loc) for r in recs]
        medido[familia] = len(recs)
        declarado = d.get('COUNT_TOTAL')
        if declarado is not None and declarado != len(recs):
            raise SystemExit('%s: COUNT_TOTAL declara %s, o corpo tem %d'
                             % (arq, declarado, len(recs)))

    # A referencia de data e UMA, e sai do pacote — nunca do relogio da maquina
    # que rodou este script.
    ref = None
    for f in saida.values():
        for r in f:
            if r.get('REFERENCE_DATE'):
                ref = r['REFERENCE_DATE']
                break
        if ref:
            break

    # As regras e a evidencia do motor de oportunidades entram achatadas: sao
    # tabela de consulta, nao colecao de registros.
    regras = carregar('OPPORTUNITY-RULES.json')
    evid = carregar('OPPORTUNITY-EVIDENCE.json')

    payload = {
        'buildId': build_id,
        'referenceDate': ref,
        'languageGate': ASSINATURA,
        'packageBuiltAt': manifesto.get('BUILT_AT'),
        'opportunityRules': {
            'ARQUETIPOS': regras.get('ARQUETIPOS'),
            'ESTADOS_DE_PRODUTO': regras.get('ESTADOS_DE_PRODUTO'),
            'ESTADOS_TEMPORAIS': regras.get('ESTADOS_TEMPORAIS'),
        },
        'opportunityEvidence': evid.get('POR_OPORTUNIDADE'),
    }
    payload.update(saida)

    corpo, pool = internar(payload)

    cab = (
        '/* SINTONIA ITALIA · O PACOTE V2.1, NA FRONTEIRA DO SITE\n'
        '   ---------------------------------------------------------------------------\n'
        '   GERADO. Nao edite: `python3 scripts/site_v21_ingest.py` reescreve o arquivo\n'
        '   inteiro a partir de build/ITALY-REALITY-HANDOFF-V2.1/DESIGN-INGEST/.\n'
        '\n'
        '   BUILD_ID  %s\n'
        '   data de referencia  %s\n'
        '   assinatura da lista de marcadores  %s\n'
        '\n'
        '   Estes registros ainda estao no CONTRATO DO V2.1 (campos em maiuscula), nao\n'
        '   na forma que as telas leem. Quem lhes da forma e `italy-app-model.js`, que\n'
        '   e o unico lugar do portal que resolve cultura, avversita, regiao e data.\n'
        '\n'
        '   Nenhuma prosa de pesquisa em portugues atravessou. Onde a fonte escreveu e\n'
        '   nao havia par IT/EN aprovado, ficou `CAMPO__PT_ONLY: true` sem o texto — a\n'
        '   divida de traducao continua contada, o texto nao embarcou.\n'
        '   --------------------------------------------------------------------------- */\n'
        % (build_id, ref, ASSINATURA)
    )

    io.open(OUT, 'w', encoding='utf-8').write(
        cab
        + '(function () {\n'
        + '  var P = ' + json.dumps(pool, ensure_ascii=False,
                                    separators=(',', ':')) + ';\n'
        + REIDRATA
        + '  window.ITALY_HANDOFF_V21 = R(' + corpo + ');\n'
        + '}());\n')

    print('== INGEST DO SITE ==')
    print('  BUILD_ID        : %s' % build_id)
    print('  data de ref.    : %s' % ref)
    print('  familias        : %d' % len(saida))
    for f in sorted(medido):
        print('     %-26s %6d' % (f, medido[f]))
    print('  fora, por decisao: %d' % len(FORA))
    for f in sorted(FORA):
        print('     %-34s %s' % (f, FORA[f][:70]))
    print('  escrito         : %s (%.1f MB)'
          % (OUT, os.path.getsize(OUT) / 1048576.0))
    return 0


if __name__ == '__main__':
    sys.exit(main())
