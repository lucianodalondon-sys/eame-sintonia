#!/usr/bin/env python3
"""
CREATORS / FARMFLUENCERS — a pessoa como CANAL, e o portão que impede que ela
seja confundida com a pessoa como SENSOR.

    python3 scripts/creators.py                 # contrato, taxonomias, portões
    python3 scripts/creators.py cobertura       # campo a campo, sobre a base real
    python3 scripts/creators.py veredito        # crop protection: PROVED/PARTIAL/NOT_PROVED

O QUE ESTE ARQUIVO NÃO É, E POR QUE ISSO PRECISA ESTAR EM CÓDIGO
-----------------------------------------------------------------
O EARLY SIGNAL pergunta *"quem enxerga o problema primeiro?"* — pessoa como
**sensor técnico**. Esta missão pergunta *"quem já fala com esse público?"* —
pessoa como **canal de comunicação**.

A mesma pessoa pode ter os dois papéis. Os papéis **nunca** se colapsam, e o
motivo é operacional, não filosófico: um pesquisador com âncora ORCID é um
sensor excelente e pode ser um canal inútil (200 seguidores, zero vídeo); um
creator com 400 mil seguidores pode ser um canal excelente e um sensor
inútil (nenhuma observação de campo verificável). Somar os dois num "score de
pessoa" produziria uma lista que não serve a nenhuma das duas perguntas.

Por isso `SENSOR_ROLE_LINK` é um **ponteiro**, nunca uma fusão: aponta para a
identidade no universo de sensores quando ela existe, e fica `NÃO SEI` quando
não existe. Nenhum campo desta ficha herda valor de lá.

AS SEIS LEIS QUE ESTE ARQUIVO EXECUTA
--------------------------------------
Todas já custaram uma medição nesta casa, e estão em `REGRA-DE-COLETA-EXTERNA`:

  1. `NAME != HANDLE != PROFILE != PERSON`. Handle não se infere de nome.
     Medido: `linkedin.com/company/adama/` devolve uma incorporadora
     imobiliária romena. Aqui `checar()` recusa handle sem `SOURCE_URL`.

  2. **CULTURA SE PROVA.** "É agro" não prova "é olivar". `CROP_STATE` só vai a
     `PROVED` com `CROP_EVIDENCE` apontando conteúdo, atividade ou histórico
     público. Sem isso, `NOT_PROVED` — e `NOT_PROVED` não entra em ranking de
     cultura.

  3. **CREATOR RURAL != PRODUTOR.** `ACTUAL_FARMER` é campo próprio, com
     evidência própria. Um agrônomo que filma lavoura alheia não vira produtor
     porque o conteúdo é de campo.

  4. **MENÇÃO != PATROCÍNIO.** A escada de marca tem cinco degraus e só sobe
     com evidência do degrau. `promover_marca()` recusa o salto.

  5. **CATEGORIA NÃO TRANSFERE.** Colaboração em maquinaria não prova
     colaboração em defensivo. `veredito_crop_protection()` só conta registro
     cuja `PRODUCT_CATEGORY` é de proteção de cultivo — e separa o caso em que
     a empresa é de defensivos mas a peça é institucional.

  6. **SEM AUTHORITY SCORE.** A casa já proibiu ordenar pessoas por número
     (`REGRA-DE-COLETA-EXTERNA` §6). `relevancia()` devolve um ESTADO derivado
     de evidência, não uma nota. Seguidor alto com cultura `NOT_PROVED` não
     sobe.

O PORTÃO QUE O BRIEFING PEDIU EXPLICITAMENTE
---------------------------------------------
`ACTIVATION_READY` **não** significa "autorizado para campanha". Significa
"há evidência suficiente para o Marketing avaliar". A autorização de campanha
de produto fitossanitário depende de quatro checagens que esta base **não**
faz e que `pendencias_de_compliance()` devolve sempre que a cultura entra em
conversa com defensivo. PORTFÓLIO GLOBAL != PORTFÓLIO LOCAL.
"""
import datetime
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SAMPLES = os.path.join(ROOT, 'data', 'samples')
BASE = os.path.join(SAMPLES, 'CREATOR-MAP-EAME')

NAO_SEI = 'NÃO SEI'

# ─────────────────────────────────────────────────────────── contrato de campos
# Um campo que some do registro é indistinguível de um campo que nunca existiu.
# `registro_vazio()` garante que todas as chaves existam sempre.
CAMPOS_CREATOR = [
    # identidade — resolvida ANTES de olhar conteúdo
    'CREATOR_ID', 'ORIGIN_ID', 'NAME', 'DISPLAY_NAME', 'COUNTRY', 'REGION',
    'LANGUAGE', 'OCCUPATION', 'FARM_OR_INSTITUTION', 'ENTITY_KIND',
    'IDENTITY_EVIDENCE', 'IDENTITY_STATE',
    # Estes quatro viviam nos registros sem estar no contrato desde a rodada 2:
    # `checar()` só acusa campo AUSENTE, então um campo extra passava calado —
    # e a garantia de que nenhum campo some em silêncio não os cobria.
    'HANDLE_EXISTS', 'PROFILE_URL', 'NAME_MATCH', 'ACTIVATION_ENTITY_TYPE',
    # papel — canal, e o ponteiro (nunca a fusão) para o papel de sensor
    'CREATOR_TYPE', 'ACTUAL_FARMER', 'ACTUAL_FARMER_EVIDENCE', 'SENSOR_ROLE_LINK',
    'FARM_TYPE', 'FARM_SCALE',
    # os QUATRO papéis, lado a lado e nunca somados nem herdados um do outro
    'ACTIVATION_CREATOR', 'TECHNICAL_SENSOR_CANDIDATE',
    'FIELD_VOICE_SOURCE', 'FARMER_CREATOR_ROLE',
    # cultura e assunto — provados, nunca inferidos de "é agro"
    'CROPS', 'CROP_STATE', 'CROP_EVIDENCE', 'REGIONS', 'TECHNICAL_TOPICS',
    # o que a SEED alegou vs o que o CONTEÚDO provou — nunca o mesmo campo
    'CROP_CLAIMED_BY_SEED', 'CROP_PROVED_BY_CONTENT', 'CROP_PROOF_URLS',
    # §2 — a prova, com a sua natureza declarada
    'CROP_PROOF_TYPE', 'CROP_PROOF_URL', 'CROP_PROOF_DATE', 'CROP_PROOF_TEXT',
    'CROP_PROOF_STRENGTH', 'N_CONTENT_ITEMS_REVIEWED', 'CONTENT_TYPES_OBSERVED',
    # suspeita derivada do handle != medição. Nunca colapsar em CROP_STATE.
    'SUSPECTED_CHAIN_MISMATCH', 'SUSPECTED_CHAIN_MISMATCH_REASON',
    # a separação que impede sommelier de virar viticultor
    'WINE_RELEVANCE', 'VITICULTURE_RELEVANCE',
    'OLIVE_OIL_RELEVANCE', 'OLIVE_GROWING_RELEVANCE',
    # plataformas e alcance
    'PLATFORMS', 'INSTAGRAM', 'TIKTOK', 'YOUTUBE', 'FACEBOOK', 'LINKEDIN', 'X',
    'FOLLOWERS_BY_PLATFORM', 'AS_OF_DATE',
    # atividade
    'POSTING_FREQUENCY', 'RECENT_ACTIVITY', 'LAST_CONTENT_DATE',
    'AVERAGE_VISIBLE_ENGAGEMENT', 'ACTIVITY_STATE',
    'POSTS_LAST_30D', 'POSTS_LAST_90D', 'VIDEOS_LAST_90D', 'LAST_ACTIVITY_DATE',
    # forma de conteúdo e audiência
    'VIDEO_ORIENTED', 'SHORT_FORM', 'LONG_FORM', 'FIELD_CONTENT',
    'TECHNICAL_CONTENT', 'AUDIENCE_TYPE',
    'FACING', 'CROP_CONTENT', 'MACHINERY_CONTENT', 'PRODUCT_CONTENT',
    'FIELD_CONTENT_RATE', 'TECHNICAL_CONTENT_RATE', 'PRODUCT_CONTENT_RATE',
    'CONSUMER_CONTENT_RATE', 'CONTENT_RATE_N',
    'RURAL_LIFESTYLE_CONTENT', 'FOOD_WINE_CONTENT',
    'AGRICULTURAL_RELEVANCE', 'TECHNICAL_RELEVANCE',
    # marca — FORÇA da evidência e TIPO da relação são dimensões separadas
    'BRAND_RELATIONSHIP_STATE', 'BRAND_RELATION_TYPE', 'BRAND_COLLABORATIONS',
    'COMPETITOR_COLLABORATION', 'ADAMA_COLLABORATION_OBSERVED',
    # contato público profissional
    'PUBLIC_CONTACT_ROUTE', 'CONTACT_KIND',
    'BUSINESS_EMAIL', 'MANAGEMENT', 'AGENCY', 'CONTACT_FORM', 'PUBLIC_DM_ROUTE',
    # como chegamos até esta pessoa. Uma pessoa achada em cinco lugares é UMA
    # pessoa com cinco rotas — nunca cinco creators.
    'DISCOVERY_ROUTES',
    # relevância — DERIVADA, nunca digitada
    'AUDIENCE_FIT_FOR_ADAMA',
    'WHY_RELEVANT', 'AUDIENCE_FIT', 'CROP_FIT', 'TECHNICAL_FIT', 'CONTENT_FIT',
    'ACTIVITY_RECENCY', 'RELEVANCE_STATE',
    # §11 · chaves de junção com as missões vizinhas (Meta, Convergência).
    # Existem para que um dia OUTRA missão possa dizer "vi esta pessoa num
    # anúncio" — e para que esse achado entre como APARIÇÃO, nunca como relação
    # paga. `PAID_CREATOR_RELATION` só sobe com prova adicional, e por isso nasce
    # e permanece NOT_KNOWN aqui.
    'PERSON_ID', 'ENTITY_ID', 'OBSERVED_AT',
    'CREATOR_APPEARANCE_OBSERVED', 'PAID_CREATOR_RELATION',
    # proveniência
    'SOURCE_URL', 'SOURCE_ID', 'CAPTURE_DATE', 'RUN_ID', 'EVIDENCE_PATH',
    'COLLECTION_ROUTE',
]

CAMPOS_COLABORACAO = [
    'COLLAB_ID', 'CREATOR_ID', 'CREATOR_NAME', 'COUNTRY', 'BRAND', 'BRAND_KIND',
    'DATE', 'CAMPAIGN', 'PRODUCT_CATEGORY', 'PRODUCT_NAME', 'PLATFORM',
    'SPONSORED_DISCLOSURE', 'RELATIONSHIP_STATE', 'RELATION_TYPE', 'MESSAGE_KIND',
    'SOURCE_URL', 'SOURCE_KIND', 'CAPTURE_DATE', 'EVIDENCE_PATH', 'NOTE',
]

# ──────────────────────────────────────────────────────────────── taxonomias
TIPOS_CREATOR = (
    'FARMER_CREATOR', 'AGRONOMIST_CREATOR', 'TECHNICAL_CREATOR',
    'RESEARCHER_CREATOR', 'CONTRACTOR_CREATOR', 'MACHINERY_CREATOR',
    'RURAL_LIFESTYLE_CREATOR', 'INSTITUTIONAL_CREATOR', 'AG_MEDIA_CREATOR',
    # os dois que a seed italiana obrigou a existir: quem fala do PRODUTO FINAL
    # não é quem fala da LAVOURA, e forçá-los para dentro de FARMER_CREATOR
    # seria entregar ao Marketing uma audiência que não existe.
    'WINE_MEDIA_CREATOR', 'FOOD_CREATOR',
    'OTHER',
)

# Categoria de produto. `CROP_PROTECTION` é a única que responde à pergunta do
# briefing — as outras existem para que ninguém a responda com elas.
CATEGORIAS = (
    'MACHINERY', 'SEEDS', 'FERTILIZER', 'BIOLOGICALS', 'CROP_PROTECTION',
    'BIOCONTROL', 'BIOSTIMULANTS', 'IRRIGATION',
    'AGTECH', 'FOOD_COMMODITY', 'INSTITUTIONAL_SECTOR', 'OTHER', NAO_SEI,
)

# A escada de marca. A ordem é o portão: `promover_marca()` só sobe com
# evidência do degrau, e mencionar produto nunca vira patrocínio.
ESCADA_MARCA = (
    'NOT_KNOWN',
    'ORGANIC_MENTION',
    'PRODUCT_USE_OBSERVED',
    'BRAND_COLLABORATION_PROVED',
    'PAID_PARTNERSHIP_PROVED',
)

# ─────────────────────────────────────── TIPO de relação (§11) — SEM ORDEM
# Estes cinco NÃO são degraus e NÃO são equivalentes: são COISAS DIFERENTES que
# uma marca pode fazer. Patrocinar a categoria de um prêmio, aparecer num evento
# com um creator, colaborar com ele, pagar-lhe e ativar um PRODUTO com ele são
# cinco fatos distintos, e o erro caro é tratá-los como um contínuo — porque aí
# "a Syngenta patrocinou uma categoria" vira, três leituras depois, "a Syngenta
# ativa produto com creators".
#
# Por isso este campo é uma LISTA FECHADA SEM ÍNDICE, e `test_tipo_de_relacao_
# nao_e_escada` proíbe qualquer comparação de ordem sobre ele. A força da
# EVIDÊNCIA continua em `BRAND_RELATIONSHIP_STATE`, que é outra dimensão.
TIPOS_DE_RELACAO = frozenset((
    'BRAND_ECOSYSTEM_SPONSORSHIP',   # patrocina o ecossistema: categoria, prêmio
    'BRAND_EVENT_COLLABORATION',     # colabora num evento
    'BRAND_COLLABORATION_PROVED',    # colabora com a pessoa
    'PAID_PARTNERSHIP_PROVED',       # paga a pessoa
    'PRODUCT_ACTIVATION_PROVED',     # ativa um PRODUTO com a pessoa
    'NOT_KNOWN',
))

# O que a peça COMUNICA. Separado de PRODUCT_CATEGORY de propósito: uma empresa
# de defensivos pode patrocinar conteúdo que não promove defensivo nenhum, e
# tratar os dois casos como um só é exatamente a extrapolação que o briefing
# proíbe.
TIPOS_MENSAGEM = (
    'PRODUCT_PROMOTION', 'TECHNICAL_EDUCATION', 'CORPORATE_IMAGE',
    'SECTOR_ADVOCACY', 'EVENT_PRESENCE', 'RECRUITMENT', 'OTHER', NAO_SEI,
)

TIPOS_ATIVACAO = (
    'BRAND_COLLABORATION', 'PAID_PARTNERSHIP', 'SPONSORED_CONTENT',
    'EVENT_ACTIVATION', 'PRODUCT_DEMO', 'FIELD_DAY', 'BRAND_AMBASSADOR',
    'LAUNCH', 'TECHNICAL_CAMPAIGN',
)

CONCORRENTES = (
    'Bayer', 'Syngenta', 'BASF', 'Corteva', 'FMC', 'UPL', 'Nufarm', 'Albaugh',
    'Certis', 'Gowan', 'Sipcam', 'Rovensa',
)

AUDIENCIAS = ('FARMERS', 'AGRONOMISTS', 'TECHNICIANS', 'GENERAL_PUBLIC', 'STUDENTS',
              'WINE_CONSUMERS', 'FOOD_CONSUMERS', 'MIXED', 'NOT_KNOWN')

# Para quem a pessoa FALA. Separado de AUDIENCE_TYPE de propósito: o primeiro é o
# público observado, este é o lado do balcão. Um agrônomo de empresa fala para
# produtor; um chef fala para consumidor — e os dois podem ter o mesmo número.
FACING = ('FARMER_FACING', 'AGRONOMIST_FACING', 'TECHNICAL_FACING',
          'GENERAL_CONSUMER', 'WINE_CONSUMER', 'FOOD_CONSUMER', 'MIXED', 'NOT_KNOWN')

# Quão perto essa audiência está de quem COMPRA defensivo. É o campo que impede
# um chef com 2 milhões de seguidores de parecer melhor que um cerealicultor com
# 20 mil, e ele é derivado — nunca digitado.
FIT_ADAMA = ('HIGH', 'MEDIUM', 'LOW', 'NOT_KNOWN')

# Um hub NÃO é um creator. Universidade, feira, associação e prêmio entram aqui
# e nunca no ranking de creators — eles são onde se DESCOBRE gente.
TIPOS_HUB = (
    'TECHNICAL_SPEAKER_HUB', 'CREATOR_DISCOVERY_HUB', 'FARMER_NETWORK_HUB',
    'FIELD_EVENT', 'AWARD', 'SCIENCE_HUB', 'PLANT_PROTECTION_SCIENCE_HUB',
    'AGTECH_SOURCE', 'INDUSTRY_SOURCE', 'BRAND_ACTIVATION_OBSERVER',
    'GLOBAL_MARKET_INTELLIGENCE', 'OTHER',
)
PRIORIDADES = ('VERY_HIGH', 'HIGH', 'MEDIUM', 'MEDIUM_LOW', 'LOW')
PROVA = ('PROVED', 'NOT_PROVED', 'NOT_KNOWN')

# Cultura tem cinco estados, não três. `WRONG_ASSIGNMENT` é o que a seed
# italiana tornou obrigatório: o candidato existe, o conteúdo existe, e a
# cultura que a lista lhe atribuiu está ERRADA. Sem esse estado, um garden
# designer catalogado em "fruticultura" só teria como sair da tabela virando
# `NOT_PROVED` — que diria "não consegui provar", quando o que foi medido é
# "provei que não é".
CROP_ESTADOS = ('PROVED', 'PARTIAL', 'NOT_PROVED', 'WRONG_ASSIGNMENT',
                'CONTRADICTED', 'NOT_KNOWN')

# ─────────────────────────────── §0 · QUE TIPO DE COISA ESTÁ POR TRÁS DA CONTA
# `ENTITY_KIND` diz PERSON/ORGANIZATION. Isso não bastou: uma conta de EMPRESA
# AGRÍCOLA e uma conta de MÍDIA são as duas `ORGANIZATION`, e a relação comercial
# que cada uma permite é completamente diferente. Este campo diz com QUEM o
# Marketing estaria falando.
#
# Nasceu de um erro meu: `@biocampojoyma` foi corretamente medido como conta de
# empresa e mesmo assim apareceu numa frase minha como "três produtores reais".
# A conta não estava errada no dado — estava errada na CONTAGEM.
ENTIDADES_DE_ATIVACAO = (
    'PERSON_CREATOR',          # uma pessoa, com rosto e voz próprios
    'FARM_BUSINESS',           # a conta da exploração/empresa agrícola
    'FARMER_FAMILY_ACCOUNT',   # conta de família/exploração sem um creator individual
    'MEDIA_ACCOUNT',           # site, revista, canal de mídia
    'ORGANIZATION',            # associação, instituto, evento
    'OTHER', NAO_SEI,
)

# §2 · as QUATRO classes de prova de cultura. Nada fora destas quatro promove.
CLASSES_DE_PROVA_DE_CULTURA = {
    'A_OWN_CROP_DECLARED': 'cultivo próprio declarado pela pessoa',
    'B_RECURRING_PROFESSIONAL_WORK': 'trabalho profissional recorrente naquela cultura',
    'C_RECURRING_FIELD_CONTENT': 'conteúdo de campo recorrente e inequívoco na cultura',
    'D_FARM_PRODUCTION_PROVED': 'exploração/empresa cuja produção da cultura é provada',
}

# O que explicitamente NÃO prova cultura. Lista fechada, porque cada uma delas já
# pareceu prova para alguém.
NAO_PROVA_CULTURA = (
    'usar hashtag', 'aparecer em evento', 'repostar notícia',
    'falar uma vez da cultura', 'estar numa categoria de prêmio',
)

FORCA_DA_PROVA = ('STRONG', 'MODERATE', 'WEAK', NAO_SEI)

# Relevância de cadeia. A lei: falar de vinho != ser relevante para o produtor
# de uva; falar de azeite != ser relevante para o olivicultor.
CADEIA = ('PROVED', 'PARTIAL', 'NOT_PROVED', 'NOT_KNOWN')

DUPLO_PAPEL = ('YES', 'NO', 'NOT_KNOWN')
ADAMA_ESTADOS = ('PROVED', 'NOT_OBSERVED', 'NOT_TESTED')
RELEVANCIA = ('ACTIVATION_READY', 'PROMISING', 'RESEARCH_NEEDED', 'NOT_RELEVANT')
ATIVIDADE = ('ACTIVE_RECENT', 'ACTIVE_STALE', 'DORMANT', 'NOT_MEASURED')

# As quatro checagens que esta base NÃO faz e que precedem qualquer campanha de
# produto fitossanitário. Devolvidas por `pendencias_de_compliance()`.
COMPLIANCE_PPP = (
    'COUNTRY_SPECIFIC_ADVERTISING_CHECK',
    'LOCAL_REGISTRATION_CHECK',
    'PLATFORM_POLICY_CHECK',
    'SPONSORED_CONTENT_DISCLOSURE_CHECK',
)


def hoje():
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + 'Z'


def registro_vazio(campos=None):
    """Todo campo existe, sempre. Ausência é `NÃO SEI`, nunca chave faltando."""
    return {c: NAO_SEI for c in (campos or CAMPOS_CREATOR)}


# ─────────────────────────────────────────────────────────────────── portões
def checar(reg):
    """Devolve a lista de violações. Lista vazia = o registro pode ser gravado.

    Não corrige nada em silêncio: recusar é barato, um registro plausível e
    falso passa pela revisão.
    """
    faltas = []

    ausentes = [c for c in CAMPOS_CREATOR if c not in reg]
    if ausentes:
        faltas.append('CAMPOS_AUSENTES: %s' % ', '.join(sorted(ausentes)))

    if not reg.get('NAME') or reg.get('NAME') == NAO_SEI:
        faltas.append('NAME_AUSENTE: sem nome não há identidade a atribuir')

    # LEI 1 — handle não se infere de nome. Todo handle declarado precisa de
    # uma URL que o tenha mostrado.
    handles = [p for p in ('INSTAGRAM', 'TIKTOK', 'YOUTUBE', 'FACEBOOK', 'LINKEDIN', 'X')
               if reg.get(p) and reg.get(p) != NAO_SEI]
    if handles and (not reg.get('SOURCE_URL') or reg.get('SOURCE_URL') == NAO_SEI):
        faltas.append('HANDLE_SEM_FONTE: %s declarado sem SOURCE_URL — handle não se infere '
                      'de nome (NAME != HANDLE != PROFILE)' % ', '.join(sorted(handles)))

    # LEI 2 — cultura se prova.
    if reg.get('CROP_STATE') == 'PROVED':
        if not reg.get('CROP_EVIDENCE') or reg.get('CROP_EVIDENCE') == NAO_SEI:
            faltas.append('CROP_PROVED_SEM_EVIDENCIA: "é agro" não prova cultura')
        if not reg.get('CROPS') or reg.get('CROPS') == NAO_SEI:
            faltas.append('CROP_PROVED_SEM_CULTURA: CROP_STATE=PROVED e CROPS vazio')
    if reg.get('ACTIVATION_ENTITY_TYPE') not in ENTIDADES_DE_ATIVACAO:
        faltas.append('ACTIVATION_ENTITY_TYPE_INVALIDO: %r'
                      % reg.get('ACTIVATION_ENTITY_TYPE'))
    if reg.get('CROP_PROOF_TYPE') not in (None, NAO_SEI) and \
            reg.get('CROP_PROOF_TYPE') not in CLASSES_DE_PROVA_DE_CULTURA:
        faltas.append('CROP_PROOF_TYPE_INVALIDO: %r — fora das quatro classes'
                      % reg.get('CROP_PROOF_TYPE'))
    if reg.get('CROP_STATE') not in CROP_ESTADOS and reg.get('CROP_STATE') != NAO_SEI:
        faltas.append('CROP_STATE_INVALIDO: %r' % reg.get('CROP_STATE'))

    # LEI 7 — a cadeia não transfere para a lavoura.
    faltas.extend(_lei_da_cadeia(reg))

    for campo, lista in (('ACTIVATION_CREATOR', DUPLO_PAPEL),
                         ('TECHNICAL_SENSOR_CANDIDATE', DUPLO_PAPEL),
                         ('WINE_RELEVANCE', CADEIA), ('VITICULTURE_RELEVANCE', CADEIA),
                         ('OLIVE_OIL_RELEVANCE', CADEIA), ('OLIVE_GROWING_RELEVANCE', CADEIA)):
        if reg.get(campo) not in lista and reg.get(campo) != NAO_SEI:
            faltas.append('%s_INVALIDO: %r' % (campo, reg.get(campo)))

    # LEI 3 — creator rural != produtor.
    if reg.get('ACTUAL_FARMER') == 'PROVED' and (
            not reg.get('ACTUAL_FARMER_EVIDENCE')
            or reg.get('ACTUAL_FARMER_EVIDENCE') == NAO_SEI):
        faltas.append('FARMER_PROVED_SEM_EVIDENCIA: creator rural não é automaticamente produtor')
    if reg.get('ACTUAL_FARMER') not in PROVA and reg.get('ACTUAL_FARMER') != NAO_SEI:
        faltas.append('ACTUAL_FARMER_INVALIDO: %r' % reg.get('ACTUAL_FARMER'))

    if reg.get('CREATOR_TYPE') not in TIPOS_CREATOR and reg.get('CREATOR_TYPE') != NAO_SEI:
        faltas.append('CREATOR_TYPE_INVALIDO: %r' % reg.get('CREATOR_TYPE'))
    if reg.get('AUDIENCE_TYPE') not in AUDIENCIAS and reg.get('AUDIENCE_TYPE') != NAO_SEI:
        faltas.append('AUDIENCE_TYPE_INVALIDO: %r' % reg.get('AUDIENCE_TYPE'))
    if reg.get('BRAND_RELATIONSHIP_STATE') not in ESCADA_MARCA and \
            reg.get('BRAND_RELATIONSHIP_STATE') != NAO_SEI:
        faltas.append('BRAND_STATE_INVALIDO: %r' % reg.get('BRAND_RELATIONSHIP_STATE'))
    if reg.get('ADAMA_COLLABORATION_OBSERVED') not in ADAMA_ESTADOS and \
            reg.get('ADAMA_COLLABORATION_OBSERVED') != NAO_SEI:
        faltas.append('ADAMA_ESTADO_INVALIDO: %r — NOT_OBSERVED e NOT_TESTED não são a mesma '
                      'coisa' % reg.get('ADAMA_COLLABORATION_OBSERVED'))
    return faltas


def _lei_da_cadeia(reg):
    """LEI 7 — PRODUTO FINAL != LAVOURA.

    Nasceu da seed italiana, onde críticos de vinho e sommeliers de azeite
    vieram catalogados como candidatos de VITICULTURA e OLIVICULTURA.

        falar muito de vinho        != ser relevante para o produtor de uva
        ser sommelier de azeite     != ter audiência de olivicultor

    A consequência prática é comercial, não semântica: uma ativação de
    fungicida de videira entregue a uma audiência de consumidores de vinho
    fala com pessoas que nunca comprarão o produto — e o número de seguidores
    faria essa entrega parecer um sucesso.
    """
    faltas = []
    crops = reg.get('CROPS') or []
    if isinstance(crops, str):
        crops = [] if crops == NAO_SEI else [crops]

    if 'GRAPEVINE' in crops and reg.get('CROP_STATE') == 'PROVED':
        if reg.get('VITICULTURE_RELEVANCE') not in ('PROVED', 'PARTIAL'):
            faltas.append(
                'UVA_SEM_VITICULTURA: CROPS inclui GRAPEVINE com CROP_STATE=PROVED, mas '
                'VITICULTURE_RELEVANCE=%r. Vinho não prova videira.'
                % reg.get('VITICULTURE_RELEVANCE'))
    if 'OLIVE' in crops and reg.get('CROP_STATE') == 'PROVED':
        if reg.get('OLIVE_GROWING_RELEVANCE') not in ('PROVED', 'PARTIAL'):
            faltas.append(
                'OLIVA_SEM_OLIVICULTURA: CROPS inclui OLIVE com CROP_STATE=PROVED, mas '
                'OLIVE_GROWING_RELEVANCE=%r. Azeite não prova olivar.'
                % reg.get('OLIVE_GROWING_RELEVANCE'))

    # Tipo de creator de mídia de produto final não pode carregar cultura PROVED.
    if reg.get('CREATOR_TYPE') in ('WINE_MEDIA_CREATOR', 'FOOD_CREATOR') and \
            reg.get('CROP_STATE') == 'PROVED':
        faltas.append(
            'MIDIA_DE_PRODUTO_COM_CULTURA_PROVADA: %s não sustenta CROP_STATE=PROVED — '
            'use PARTIAL com evidência agronômica, ou WRONG_ASSIGNMENT'
            % reg.get('CREATOR_TYPE'))
    return faltas


def promover_marca(estado_atual, estado_novo, *, evidencia):
    """LEI 4 — a escada de marca só sobe com evidência do degrau.

    Devolve (estado, motivo). Nunca lança: rebaixar e recusar são resultados
    válidos, e um pipeline que morre aqui viraria coleta perdida.
    """
    if estado_novo not in ESCADA_MARCA:
        return estado_atual, 'ESTADO_INVALIDO: %r' % estado_novo
    atual = estado_atual if estado_atual in ESCADA_MARCA else 'NOT_KNOWN'
    if ESCADA_MARCA.index(estado_novo) <= ESCADA_MARCA.index(atual):
        # Rebaixar é sempre permitido e nunca é retrocesso (README da casa).
        return estado_novo, 'REBAIXADO_OU_IGUAL'
    if not evidencia or evidencia == NAO_SEI:
        return atual, ('SUBIDA_RECUSADA: %s -> %s exige evidência do degrau. '
                       'Falar de produto não é ser patrocinado por ele.'
                       % (atual, estado_novo))
    return estado_novo, 'PROMOVIDO_COM_EVIDENCIA'


def _sim(v):
    return str(v).upper() in ('YES', 'TRUE', 'SIM', '1')


# As SEIS provas de `ACTIVATION_READY` (§10). Note o que NÃO está na lista:
# histórico de marca e número de seguidores. Nenhum dos dois é requisito — um
# creator sem nenhuma campanha anterior pode ser exatamente o que o Marketing
# procura, e seguidor alto sem cultura provada já mostrou, nesta missão, entregar
# audiência de consumidor de vinho no lugar de produtor de uva.
PROVAS_DE_ATIVACAO = (
    'IDENTITY_PROVED', 'COUNTRY_PROVED', 'CROP_FIT_PROVED',
    'ROLE_PROVED', 'RECENT_ACTIVITY_PROVED', 'PUBLIC_CHANNEL_PROVED',
)


def provas_de_ativacao(reg):
    """Devolve as seis provas, uma a uma, com o valor que as sustenta.

    Devolver o detalhe — e não só o veredito — é o que permite ao Marketing ver
    QUAL prova falta em cada pessoa, que é a pergunta operacional real: "o que
    preciso descobrir para poder avaliar este nome?".
    """
    canais = [p for p in ('INSTAGRAM', 'TIKTOK', 'YOUTUBE', 'FACEBOOK', 'LINKEDIN', 'X')
              if reg.get(p) not in (None, '', NAO_SEI)]
    contato = [c for c in ('PUBLIC_CONTACT_ROUTE', 'BUSINESS_EMAIL', 'MANAGEMENT',
                           'AGENCY', 'CONTACT_FORM', 'PUBLIC_DM_ROUTE')
               if reg.get(c) not in (None, '', NAO_SEI, 'NOT_KNOWN')]
    return {
        'IDENTITY_PROVED': reg.get('IDENTITY_STATE') == 'PROVED',
        'COUNTRY_PROVED': reg.get('COUNTRY') not in (None, '', NAO_SEI, 'NOT_KNOWN'),
        # §2 — `PARTIAL` significa menção única, e "falar uma vez da cultura" está
        # na lista fechada do que NÃO prova cultura. Aceitá-lo aqui contradiria a
        # própria régua e inflaria `ACTIVATION_READY` com gente cuja lavoura
        # ninguém viu. Só `PROVED` passa.
        'CROP_FIT_PROVED': reg.get('CROP_STATE') == 'PROVED',
        'ROLE_PROVED': reg.get('CREATOR_TYPE') not in (None, '', NAO_SEI),
        'RECENT_ACTIVITY_PROVED': reg.get('ACTIVITY_STATE') == 'ACTIVE_RECENT',
        'PUBLIC_CHANNEL_PROVED': bool(canais),
        '_CANAIS': canais,
        '_ROTAS_DE_CONTATO': contato,
    }


# §11 — o motivo pendente, em código de uma palavra. `PROMISING` sozinho manda a
# pessoa de volta para a fila; `PROMISING + MISSING_RECENT_ACTIVITY` diz a alguém
# exatamente o que buscar amanhã de manhã.
MOTIVO_PENDENTE = {
    'IDENTITY_PROVED': 'IDENTITY_PARTIAL',
    'COUNTRY_PROVED': 'MISSING_COUNTRY',
    'CROP_FIT_PROVED': 'MISSING_CROP_PROOF',
    'ROLE_PROVED': 'MISSING_ROLE',
    'RECENT_ACTIVITY_PROVED': 'MISSING_RECENT_ACTIVITY',
    'PUBLIC_CHANNEL_PROVED': 'MISSING_PUBLIC_CHANNEL',
}
MISSING_REGIAO = 'MISSING_REGION'
MISSING_CONTATO = 'MISSING_PUBLIC_CONTACT'


def pendencias(reg):
    """Devolve os códigos do que falta — a lista que o Marketing lê."""
    p = provas_de_ativacao(reg)
    fora = [MOTIVO_PENDENTE[k] for k in PROVAS_DE_ATIVACAO if not p[k]]
    if reg.get('REGION') in (None, '', NAO_SEI, 'NOT_KNOWN'):
        fora.append(MISSING_REGIAO)
    if not p['_ROTAS_DE_CONTATO']:
        fora.append(MISSING_CONTATO)
    return fora


def relevancia(reg, *, colaboracoes=()):
    """LEI 6 — estado DERIVADO de evidência, nunca nota, nunca ordenação por
    seguidores.

    Devolve (estado, porques). `porques` é a lista de motivos legíveis: é ela
    que vai para a ficha "WHO COULD MARKETING CALL?", não o estado sozinho.
    """
    p = provas_de_ativacao(reg)
    faltando = [k for k in PROVAS_DE_ATIVACAO if not p[k]]
    porques = ['%s=%s' % (k, 'OK' if p[k] else 'FALTA') for k in PROVAS_DE_ATIVACAO]

    # Conflito com concorrente é INFORMAÇÃO para o Marketing, não desqualificação.
    conc = [c for c in colaboracoes
            if c.get('CREATOR_ID') == reg.get('CREATOR_ID')
            and c.get('BRAND') in CONCORRENTES
            and c.get('RELATIONSHIP_STATE') in ('BRAND_COLLABORATION_PROVED',
                                                'PAID_PARTNERSHIP_PROVED')]
    if conc:
        porques.append('CONFLITO_CONCORRENTE: %s'
                       % ', '.join(sorted({c['BRAND'] for c in conc})))

    pend = pendencias(reg)
    if not faltando:
        # A sétima condição: uma rota de contato OU presença profissional pública
        # bastante para o Marketing avaliar. Canal público resolvido conta.
        if p['_ROTAS_DE_CONTATO'] or p['_CANAIS']:
            return 'ACTIVATION_READY', porques + (
                ['PENDENTE_NAO_BLOQUEANTE: %s' % ', '.join(pend)] if pend else [])
        return 'PROMISING', porques + ['PENDENTE: %s' % ', '.join(pend)]

    if reg.get('CROP_STATE') == 'WRONG_ASSIGNMENT':
        return 'NOT_RELEVANT', porques + [
            'CULTURA_REFUTADA: a cultura atribuída foi medida como errada — não '
            'entra no recorte desta cultura (pode servir a outro)']

    # Quantas faltam decide entre "quase lá" e "pesquisar".
    if len(faltando) <= 2 and p['IDENTITY_PROVED']:
        return 'PROMISING', porques + ['PENDENTE: %s' % ', '.join(pend)]
    return 'RESEARCH_NEEDED', porques + ['PENDENTE: %s' % ', '.join(pend)]


# §0 · OS NOMES DAS MÉTRICAS SÃO PARTE DO CONTRATO
# `ACTIVATION_READY = 9` foi publicado como se os nove fossem creators. Não eram:
# sete são pessoas e dois são contas de empresa. O nome errado da métrica fez o
# trabalho que o dado recusava fazer.
#
# A soma existe e pode ser útil — mas só com o nome que diz o que ela é.
METRICAS_DE_PRONTIDAO = {
    'PERSON_CREATOR_ACTIVATION_READY': 'pessoas creators prontas para avaliação',
    'FARM_BUSINESS_PARTNER_READY': 'contas de exploração/empresa prontas como parceiro',
    'MARKETING_CONTACTABLE_ENTITIES_READY':
        'a SOMA das duas — e só pode ser chamada assim. Nunca "CREATORS_READY".',
}
METRICA_PROIBIDA = 'CREATORS_READY'


def metricas_de_prontidao(registros):
    """Devolve as três métricas com os nomes certos. Nunca uma só."""
    prontos = [r for r in registros if r.get('RELEVANCE_STATE') == 'ACTIVATION_READY'
               or r.get('ACTIVATION_STATE') == 'ACTIVATION_READY']
    pessoas = [r for r in prontos if r.get('ACTIVATION_ENTITY_TYPE') == 'PERSON_CREATOR']
    negocios = [r for r in prontos if r.get('ACTIVATION_ENTITY_TYPE') in
                ('FARM_BUSINESS', 'FARMER_FAMILY_ACCOUNT')]
    return {
        'PERSON_CREATOR_ACTIVATION_READY': len(pessoas),
        'FARM_BUSINESS_PARTNER_READY': len(negocios),
        'MARKETING_CONTACTABLE_ENTITIES_READY': len(prontos),
        'NOTE': 'a soma NÃO se chama CREATORS_READY. Pessoa != empresa, e o nome da '
                'métrica é onde essa distinção se perde primeiro.',
    }


def e_pessoa_creator(reg):
    """§0 — a conta é de uma PESSOA creator?

    `ACCOUNT_OF_FARM_COMPANY != PERSON_CREATOR`. Uma exploração com canal forte
    pode ser um parceiro comercial excelente — e essa é **outra** relação, com
    outro contrato, outro interlocutor e outro preço. Contá-la como creator-pessoa
    infla o número que o Marketing usa para planear elenco.
    """
    return reg.get('ACTIVATION_ENTITY_TYPE') == 'PERSON_CREATOR'


def fit_para_adama(reg):
    """Deriva `AUDIENCE_FIT_FOR_ADAMA`. Nunca digitado, nunca por seguidores.

    A pergunta não é "quantos ouvem?", é "quantos dos que ouvem COMPRAM
    defensivo?". Um crítico de vinho com 200 mil seguidores e um cerealicultor
    com 20 mil não são comparáveis, e ordená-los pelo mesmo número inverteria a
    resposta.
    """
    consumidor = ('WINE_CONSUMERS', 'FOOD_CONSUMERS', 'GENERAL_PUBLIC')
    tipo = reg.get('CREATOR_TYPE')
    aud = reg.get('AUDIENCE_TYPE')
    cultura_ok = reg.get('CROP_STATE') in ('PROVED', 'PARTIAL')

    if tipo in ('WINE_MEDIA_CREATOR', 'FOOD_CREATOR') or aud in consumidor:
        return 'LOW', ('audiência de consumidor final — pode servir a B2C, não a '
                       'ativação junto a quem aplica defensivo')
    if reg.get('CROP_STATE') == 'WRONG_ASSIGNMENT':
        return 'LOW', 'cultura atribuída pela seed foi refutada pela evidência'
    if aud in ('FARMERS', 'AGRONOMISTS', 'TECHNICIANS') and cultura_ok:
        return 'HIGH', 'audiência declarada de campo e cultura provada'
    if tipo in ('FARMER_CREATOR', 'AGRONOMIST_CREATOR', 'TECHNICAL_CREATOR') and cultura_ok:
        return 'MEDIUM', 'perfil de campo com cultura provada; audiência ainda não medida'
    if tipo in ('FARMER_CREATOR', 'AGRONOMIST_CREATOR', 'TECHNICAL_CREATOR'):
        return 'MEDIUM', 'perfil de campo; cultura ainda não provada'
    return 'NOT_KNOWN', 'sem tipo, audiência ou cultura suficientes'


def pendencias_de_compliance(reg=None):
    """A base é para DESCOBERTA E PLANEJAMENTO. Ela não autoriza campanha."""
    return {
        'BASE_AUTORIZA_CAMPANHA': 'NO',
        'SIGNIFICADO_DE_ACTIVATION_READY':
            'há evidência suficiente para o Marketing avaliar — não é autorização legal',
        'CHECAGENS_PENDENTES': list(COMPLIANCE_PPP),
        'PORTFOLIO': 'PORTFOLIO GLOBAL != PORTFOLIO LOCAL — não sugerir produto não '
                     'autorizado naquele país/cultura',
    }


# O estado que substitui `NOT_PROVED` — e o motivo de ele ser longo de propósito.
# `NOT_PROVED` é curto, e por ser curto foi lido como "não existe". Este nome não
# cabe numa manchete, que é exatamente o ponto: ele obriga quem o cita a carregar
# junto o escopo em que a ausência foi observada.
AUSENTE_NO_CORPUS = 'NOT_OBSERVED_IN_MEASURED_CORPUS'

# O que este estado NÃO autoriza dizer. Viaja junto do veredito, no próprio JSON,
# para que a ressalva não se perca entre o dado e o slide.
NAO_SIGNIFICA = [
    'não significa "ninguém faz"',
    'não significa "white space de mercado"',
    'não significa "oportunidade comercial"',
    'não significa que o país não usa creators agrícolas — só que, no corpus '
    'medido, não se observou uso ligado especificamente a crop protection',
]


def veredito_crop_protection(colaboracoes, *, paises=('ES', 'IT', 'FR'), testados=None):
    """LEI 5 — categoria não transfere, e empresa de defensivo não é peça de defensivo.

    Quatro estados por país:

        PROVED       há ativação de PRODUTO fitossanitário com creator.
        PARTIAL      empresa de crop protection usando creator para
                     ecossistema, evento, imagem ou setor — nunca produto.
        NOT_OBSERVED_IN_MEASURED_CORPUS
                     o país foi testado e nada apareceu DENTRO DO CORPUS MEDIDO.
                     Ausência observada num corpus não é ausência no mercado.
        NOT_TESTED   o país não foi pesquisado. Nunca confundir com o anterior.
    """
    testados = set(testados if testados is not None else paises)
    fora = {}
    provados = ('BRAND_COLLABORATION_PROVED', 'PAID_PARTNERSHIP_PROVED')
    mensagem_produto = ('PRODUCT_PROMOTION', 'TECHNICAL_EDUCATION')

    for pais in paises:
        if pais not in testados:
            fora[pais] = {'ESTADO': 'NOT_TESTED', 'CASOS': [], 'MOTIVO':
                          'país não pesquisado nesta rodada — ausência de busca não é ausência de fato',
                          'ESTE_ESTADO_NAO_SIGNIFICA': NAO_SIGNIFICA}
            continue
        do_pais = [c for c in colaboracoes if c.get('COUNTRY') == pais]
        pleno = [c for c in do_pais
                 if c.get('PRODUCT_CATEGORY') == 'CROP_PROTECTION'
                 and c.get('RELATIONSHIP_STATE') in provados
                 and c.get('MESSAGE_KIND') in mensagem_produto]
        parcial = [c for c in do_pais
                   if c not in pleno
                   and c.get('RELATIONSHIP_STATE') in provados
                   and (c.get('PRODUCT_CATEGORY') == 'CROP_PROTECTION'
                        or c.get('BRAND_KIND') == 'CROP_PROTECTION_COMPANY')]
        if pleno:
            estado, casos = 'PROVED', pleno
            motivo = ('%d peça(s) de categoria CROP_PROTECTION com colaboração/patrocínio '
                      'provado e mensagem de produto' % len(pleno))
        elif parcial:
            estado, casos = 'PARTIAL', parcial
            motivo = ('%d caso(s) de empresa de crop protection usando creator, sem peça de '
                      'produto fitossanitário provada — institucional/advocacy/evento não é '
                      'ativação de produto' % len(parcial))
        else:
            estado, casos = AUSENTE_NO_CORPUS, []
            motivo = ('testado nesta rodada; nenhuma evidência encontrada DENTRO DO '
                      'CORPUS MEDIDO — que é pequeno e enviesado pelas fontes que '
                      'alcançamos')
        fora[pais] = {
            'ESTADO': estado,
            'MOTIVO': motivo,
            'ESTE_ESTADO_NAO_SIGNIFICA': NAO_SIGNIFICA,
            'CORPUS_MEDIDO': 'pesquisa aberta por buscador + 1 rota Apify de Instagram; '
                             'NÃO inclui varredura sistemática de posts patrocinados, '
                             'nem arquivos de campanha das marcas, nem plataformas de '
                             'influencer marketing',
            'CASOS': [{k: c.get(k) for k in
                       ('BRAND', 'CREATOR_NAME', 'DATE', 'PRODUCT_CATEGORY', 'MESSAGE_KIND',
                        'RELATIONSHIP_STATE', 'PLATFORM', 'SOURCE_URL')} for c in casos],
        }
    return fora


def cobertura(registros, campos=None):
    """Quantos registros DECLARAM cada campo. É isto que impede a lista de
    encolher em silêncio (mesma disciplina de `voz.cobertura()`)."""
    campos = campos or CAMPOS_CREATOR
    n = len(registros) or 1
    fora = {}
    for c in campos:
        d = sum(1 for r in registros
                if r.get(c) not in (None, '', NAO_SEI, [], {}))
        fora[c] = {'DECLARADOS': d, 'DE': len(registros), 'PCT': round(100.0 * d / n, 1)}
    return fora


def carregar(nome):
    caminho = os.path.join(BASE, nome)
    if not os.path.exists(caminho):
        return []
    with open(caminho, encoding='utf-8') as f:
        d = json.load(f)
    # A lista de chaves precisa acompanhar os artefatos. Quando `SEED-IT-
    # CANDIDATES.json` chegou com `CANDIDATES`, esta função devolveu [] e a
    # fase paga rodou com ZERO handles — falhou fechado, como deve, mas gastou
    # uma execução para descobrir. Chave nova de artefato entra AQUI.
    for chave in ('CREATORS', 'COLLABORATIONS', 'REGISTROS', 'CANDIDATES',
                  'PROFILES', 'ACTORS', 'MARKET_EVIDENCE', 'VALIDATIONS', 'HUBS',
                  'MENTIONS', 'YIELD', 'FICHAS', 'RUNS', 'CHANNELS',
                  'PERSON_CREATOR_FICHES'):
        if isinstance(d, dict) and chave in d:
            return d[chave]
    return d if isinstance(d, list) else []


def _cli():
    arg = sys.argv[1] if len(sys.argv) > 1 else ''
    if arg == 'cobertura':
        regs = carregar('CREATORS-ES-IT-FR.json')
        if not regs:
            print('BASE_VAZIA: nenhum creator gravado ainda'); return
        print('CREATORS=%d' % len(regs))
        for c, v in cobertura(regs).items():
            print('  %-32s %3d/%-3d  %5.1f%%' % (c, v['DECLARADOS'], v['DE'], v['PCT']))
        return
    if arg == 'veredito':
        colabs = carregar('BRAND-COLLABORATIONS-EU.json')
        print(json.dumps(veredito_crop_protection(colabs), ensure_ascii=False, indent=2))
        return
    print('CREATORS / FARMFLUENCERS — pessoa como CANAL (nunca como sensor)')
    print('  campos por creator .......... %d' % len(CAMPOS_CREATOR))
    print('  campos por colaboração ...... %d' % len(CAMPOS_COLABORACAO))
    print('  tipos de creator ............ %d' % len(TIPOS_CREATOR))
    print('  degraus da escada de marca .. %d  %s' % (len(ESCADA_MARCA), ' < '.join(ESCADA_MARCA)))
    print('  categorias de produto ....... %d' % len(CATEGORIAS))
    print('  checagens de compliance ..... %d' % len(COMPLIANCE_PPP))
    print()
    print('LEIS EXECUTADAS: handle não se infere · cultura se prova · creator != produtor')
    print('                 menção != patrocínio · categoria não transfere · sem authority score')


if __name__ == '__main__':
    _cli()
