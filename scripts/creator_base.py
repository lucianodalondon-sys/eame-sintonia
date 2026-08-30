#!/usr/bin/env python3
"""
BASE DE CREATORS — deriva os artefatos a partir da TABELA DE EVIDÊNCIA.

    python3 scripts/creator_base.py montar
    python3 scripts/creator_base.py resumo

POR QUE UMA TABELA DE EVIDÊNCIA E NÃO UM JSON ESCRITO À MÃO
-------------------------------------------------------------
Um JSON digitado carrega estado digitado, e estado digitado é onde a
plausibilidade entra sem passar pelo portão. Aqui o que se escreve é **o que a
fonte disse**; o ESTADO é derivado por `creators.checar()` e
`creators.relevancia()`. Se a evidência não sustenta `PROVED`, nenhuma
digitação faz o registro subir.

O LIMITE DESTA RODADA, DECLARADO NO PRÓPRIO DADO
--------------------------------------------------
O contêiner desta sessão tem egresso restrito: `WebSearch` responde, mas
`WebFetch` é bloqueado pela política de saída para praticamente todo domínio
europeu do setor (medido: plataformatierra.es, revistamercados.com,
cibotoday.it, reporterre.net, desmog.com — todos `EGRESS_BLOCKED`).

Consequência honesta, e ela está em cada registro:

    o buscador SURFOU o fato e nomeou a página; a PÁGINA não foi aberta.

Por isso `IDENTITY_STATE` sai `NOT_PROVED` para todo candidato desta rodada, e
`SOURCE_KIND = SEARCH_SUMMARY_NOT_OPENED`. Não é pessimismo: é a diferença
entre "li a fonte" e "um resumo me disse o que a fonte diz", e essa diferença é
exatamente a que o `ES-01717` ensinou a não apagar.

A promoção para `PROVED` é trabalho da rota Apify (`creator_coleta.py`), que
roda no runner residencial — a mesma máquina que já foi a única rota capaz de
abrir o catálogo ADAMA quando a borda Akamai devolvia 403 ao contêiner.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import creators as cr                                        # noqa: E402

MISSION = '14-MAPA-DE-CREATORS-EAME'
CAPTURA = '2026-08-30'
ROTA = 'WEB_SEARCH (contêiner) — WebFetch bloqueado por política de egresso'

# ═══════════════════════════════════════════════════════════════════════════
# TABELA DE EVIDÊNCIA — o que a fonte disse, não o que concluímos.
# Cada linha: o fato bruto + a URL que o buscador nomeou.
# ═══════════════════════════════════════════════════════════════════════════
CANDIDATOS = [
  # ─────────────────────────────────────────────────────────────────── ESPANHA
  dict(id='ES-CR-001', nome='Fernando Giraldo', display='Tomy Rohde',
       pais='ES', regiao='Córdoba (Andalucía)', idioma='es',
       ocupacao='olivarero', tipo='FARMER_CREATOR',
       produtor='PROVED', produtor_ev='fonte o descreve como olivarero de Córdoba',
       crops=['OLIVE'], crop_ev='descrito como olivarero (olivar) de Córdoba',
       cadeia={'OLIVE_GROWING_RELEVANCE': 'PROVED', 'OLIVE_OIL_RELEVANCE': 'NOT_KNOWN'},
       handles={'X': '@Tomy_Rohde'},
       seguidores={'X': 52000, 'INSTAGRAM': 9600},
       url='https://www.eldebate.com/espana/andalucia/20260619/olivar-redes-sociales-campo-andaluz-viraliza-fenomeno-agroinfluencers_430188.html'),

  dict(id='ES-CR-002', nome='Alberto Rojas', display='Agriproducción',
       pais='ES', regiao='Córdoba (Andalucía)', idioma='es',
       ocupacao='agricultor de 4ª geração — olivar e cultivos extensivos',
       tipo='FARMER_CREATOR',
       produtor='PROVED', produtor_ev='agricultor de quarta geração, explora olivar próprio',
       crops=['OLIVE', 'EXTENSIVE_CROPS'],
       crop_ev='fonte declara olivar e cultivos extensivos em Córdoba',
       cadeia={'OLIVE_GROWING_RELEVANCE': 'PROVED', 'OLIVE_OIL_RELEVANCE': 'NOT_KNOWN'},
       handles={}, seguidores={'TOTAL_DECLARADO': 100000},
       url='https://www.eldebate.com/espana/andalucia/20260619/olivar-redes-sociales-campo-andaluz-viraliza-fenomeno-agroinfluencers_430188.html'),

  dict(id='ES-CR-003', nome='Caterina Pak', display='AgroComunidad',
       pais='ES', regiao='Almería (Andalucía)', idioma='es',
       ocupacao='técnica agrícola', tipo='AGRONOMIST_CREATOR',
       produtor='NOT_PROVED',
       produtor_ev='descrita como técnica agrícola que divulga o invernadero; '
                   'nenhuma fonte a declara titular de exploração',
       crops=['PROTECTED_HORTICULTURE'],
       crop_ev='conteúdo sobre agricultura de invernadero de Almería',
       handles={'INSTAGRAM': '@agrocomunidad.es'},
       seguidores={'TIKTOK': 14800, 'INSTAGRAM': 14100},
       url='https://www.plataformatierra.es/actualidad/agroinfluencers-mas-moda-agricultura-2024'),

  dict(id='ES-CR-004', nome='Francisco Jesús Montoya', display='biocampojoyma',
       pais='ES', regiao='Almería (Andalucía)', idioma='es',
       ocupacao='horticultor', tipo='FARMER_CREATOR',
       produtor='PROVED', produtor_ev='fonte o descreve como horticultor de Almería',
       crops=['PROTECTED_HORTICULTURE'], crop_ev='horticultor de Almería (invernadero)',
       handles={'INSTAGRAM': '@biocampojoyma'}, seguidores={'INSTAGRAM': 10400},
       url='https://www.plataformatierra.es/actualidad/agroinfluencers-mas-moda-agricultura-2024'),

  dict(id='ES-CR-005', nome='Esther Molina', display=cr.NAO_SEI,
       pais='ES', regiao='Almería (Andalucía)', idioma='es',
       ocupacao='agricultora em invernadero solar', tipo='FARMER_CREATOR',
       produtor='PROVED', produtor_ev='fonte a descreve cultivando em invernadero próprio',
       crops=['PEPPER', 'TOMATO', 'MELON', 'WATERMELON'],
       crop_ev='cultiva pimento, tomate, melão e melancia com fauna auxiliar',
       handles={}, seguidores={},
       url='https://www.plataformatierra.es/actualidad/agroinfluencers-mas-moda-agricultura-2024'),

  # ───────────────────────────────────────────────────────────────────── ITÁLIA
  dict(id='IT-CR-001', nome='Paolo Nenci', display=cr.NAO_SEI,
       pais='IT', regiao='Chiusi, Toscana', idioma='it',
       ocupacao='viticultor e produtor', tipo='FARMER_CREATOR',
       produtor='PROVED', produtor_ev='conduz a empresa agrícola familiar; vinha própria',
       crops=['GRAPEVINE', 'SPELT', 'OLIVE'],
       crop_ev='fonte declara que CONDUZ as vinhas e produz vinho, azeite, mel e espelta '
               '— produção agrícola própria, não crítica de produto',
       cadeia={'VITICULTURE_RELEVANCE': 'PROVED', 'WINE_RELEVANCE': 'PARTIAL',
               'OLIVE_GROWING_RELEVANCE': 'PARTIAL', 'OLIVE_OIL_RELEVANCE': 'PARTIAL'},
       handles={}, seguidores={},
       url='https://www.cibotoday.it/storie/agricoltura/influencer-agricoltura-italiani-chi-sono.html'),

  dict(id='IT-CR-002', nome='Maria Pezone', display=cr.NAO_SEI,
       pais='IT', regiao=cr.NAO_SEI, idioma='it',
       ocupacao='formada em Ciências Agrárias; gere a empresa familiar Egiziaca',
       tipo='FARMER_CREATOR',
       produtor='PROVED', produtor_ev='gere empresa familiar de 130 ha',
       crops=['LETTUCE', 'MELON'],
       crop_ev='130 ha de alface Iceberg e melão retato, declarados pela fonte',
       handles={}, seguidores={'INSTAGRAM': 21000},
       url='https://www.cibotoday.it/storie/agricoltura/influencer-agricoltura-italiani-chi-sono.html'),

  dict(id='IT-CR-003', nome='Yuliya Pyliavska', display=cr.NAO_SEI,
       pais='IT', regiao='Lombardia (Vigevano)', idioma='it',
       ocupacao='agri-blogger', tipo='MACHINERY_CREATOR',
       produtor='NOT_KNOWN', produtor_ev='fonte a trata como blogger de agricultura e tratores',
       crops=[], crop_ev='conteúdo geral de coltivazioni e tratores — nenhuma cultura provada',
       handles={}, seguidores={'INSTAGRAM': 109000, 'TIKTOK': 209000},
       url='https://www.informatorevigevanese.it/attualita/2023/04/04/news/trecentomila-followers-yuliya-la-blogger-che-parla-di-agricoltura-e-trattori-556068/'),

  dict(id='IT-CR-004', nome='Tommaso Rossi Razzini', display='The Roman Farmer',
       pais='IT', regiao='Roma, Lazio', idioma='it',
       ocupacao='content creator agrícola', tipo='MACHINERY_CREATOR',
       produtor='NOT_KNOWN',
       produtor_ev='começou com vídeos "in azienda"; a fonte não prova titularidade',
       crops=[], crop_ev='conteúdo de máquinas e empresas visitadas — cultura não provada',
       handles={}, seguidores={},
       url='https://www.cibotoday.it/citta/roma/the-roman-farmer-agroinfluencer-rossi-razzini.html'),

  dict(id='IT-CR-005', nome='Beatrice Scrocchi', display=cr.NAO_SEI,
       pais='IT', regiao=cr.NAO_SEI, idioma='it',
       ocupacao='trabalha em empresa agrícola', tipo='FARMER_CREATOR',
       produtor='NOT_KNOWN', produtor_ev='fonte diz que fala do próprio trabalho agrícola',
       crops=[], crop_ev='cultura não declarada pela fonte',
       handles={}, seguidores={},
       url='https://www.influenxer.it/influencer/agricoltura-social-coltivatori'),

  # ─────────────────────────────────────────────────────────────────── FRANÇA
  dict(id='FR-CR-001', nome='Thierry Bailliet', display="Thierry agriculteur d'aujourd'hui",
       pais='FR', regiao='Pas-de-Calais (Hauts-de-France)', idioma='fr',
       ocupacao='agriculteur', tipo='FARMER_CREATOR',
       produtor='PROVED', produtor_ev='agricultor no Pas-de-Calais, explora própria',
       crops=[], crop_ev='cultura específica não declarada nas fontes lidas',
       handles={}, seguidores={'AGREGADO_DECLARADO': 100000},
       url='https://www.pleinchamp.com/actualite/l-agriculture-merite-d-etre-expliquee-la-mission-sans-relache-de-thierry-bailliet'),

  dict(id='FR-CR-002', nome='Marc-Antoine Dumoulin', display='Agricoolteur',
       pais='FR', regiao=cr.NAO_SEI, idioma='fr',
       ocupacao='agriculteur', tipo='FARMER_CREATOR',
       produtor='NOT_PROVED', produtor_ev='descrito como agricultor; titularidade não provada',
       crops=[], crop_ev='conteúdo de vida diária na fazenda — cultura não provada',
       handles={'TIKTOK': '@agricoolteur'}, seguidores={'TIKTOK': 413600},
       url='https://www.tiktok.com/@agricoolteur'),

  dict(id='FR-CR-003', nome='Océane', display='Océane Agricultrice',
       pais='FR', regiao=cr.NAO_SEI, idioma='fr',
       ocupacao='agricultrice', tipo='FARMER_CREATOR',
       produtor='NOT_PROVED', produtor_ev='descrita como agricultrice; titularidade não provada',
       crops=[], crop_ev='ensilagem, colheita e semeadura — sugere grandes culturas, não provado',
       handles={'YOUTUBE': 'UCfadEVaW_44cJOlN5m0xkEQ'}, seguidores={'YOUTUBE': 43300},
       url='https://www.youtube.com/channel/UCfadEVaW_44cJOlN5m0xkEQ'),

  dict(id='FR-CR-004', nome='Jean-Baptiste De Wever', display=cr.NAO_SEI,
       pais='FR', regiao=cr.NAO_SEI, idioma='fr',
       ocupacao='agri-influenceur', tipo='FARMER_CREATOR',
       produtor='NOT_KNOWN', produtor_ev='tratado como agri-influenceur pela fonte',
       crops=[], crop_ev='cultura não declarada',
       handles={}, seguidores={},
       url='https://www.reech.com/fr/blog/les-influenceurs/qui-sont-sont-les-agri-youtubeurs'),
]

# ═══════════════════════════════════════════════════════════════════════════
# COLABORAÇÕES creator × marca. Só pares NOMEADOS entram aqui.
# "Marcas colaboram com agri-influenceurs" é evidência de MERCADO, não par.
# ═══════════════════════════════════════════════════════════════════════════
COLABORACOES = [
  dict(id='COL-FR-001', creator_id=cr.NAO_SEI, creator='Jenny Letellier', pais='FR',
       marca='Bayer', marca_tipo='CROP_PROTECTION_COMPANY', data='2023-03',
       campanha="Stories patrocinadas no Salon de l'Agriculture 2023",
       categoria='INSTITUTIONAL_SECTOR', produto=cr.NAO_SEI, plataforma='INSTAGRAM',
       disclosure='DISCLOSED_SPONSORED', estado='PAID_PARTNERSHIP_PROVED',
       mensagem='CORPORATE_IMAGE',
       url='https://www.tiktok.com/@vakitamedia/video/7207500313941544197',
       fonte_tipo='INVESTIGATIVE_MEDIA',
       nota='A creator NÃO é agro: é YouTuber generalista. A peça é imagem corporativa '
            'de uma empresa de defensivos, não ativação de produto fitossanitário. '
            'A parceria foi encerrada pela creator após repercussão pública. '
            'Corroborado por DeSmog e Reporterre.'),

  dict(id='COL-FR-002', creator_id='FR-CR-004', creator='Jean-Baptiste De Wever', pais='FR',
       marca='Manitou France', marca_tipo='MACHINERY_COMPANY', data=cr.NAO_SEI,
       campanha='Concurso em parceria com agri-influenceur',
       categoria='MACHINERY', produto=cr.NAO_SEI, plataforma=cr.NAO_SEI,
       disclosure=cr.NAO_SEI, estado='BRAND_COLLABORATION_PROVED',
       mensagem='PRODUCT_PROMOTION',
       url='https://www.reech.com/fr/blog/les-influenceurs/qui-sont-sont-les-agri-youtubeurs',
       fonte_tipo='INDUSTRY_MEDIA',
       nota='Fonte declara engajamento 12x acima da média. Categoria MAQUINARIA — '
            'não transfere para defensivo.'),

  dict(id='COL-IT-001', creator_id='IT-CR-004', creator='Tommaso Rossi Razzini (The Roman Farmer)',
       pais='IT', marca=cr.NAO_SEI, marca_tipo=cr.NAO_SEI, data=cr.NAO_SEI,
       campanha='Cria conteúdo para empresas do setor, viajando pela Itália',
       categoria=cr.NAO_SEI, produto=cr.NAO_SEI, plataforma=cr.NAO_SEI,
       disclosure=cr.NAO_SEI, estado='BRAND_COLLABORATION_PROVED',
       mensagem=cr.NAO_SEI,
       url='https://www.cibotoday.it/citta/roma/the-roman-farmer-agroinfluencer-rossi-razzini.html',
       fonte_tipo='MEDIA',
       nota='A fonte prova a PRÁTICA de colaboração comercial; NÃO nomeia a marca. '
            'Marca fica NÃO SEI — inventar a marca seria o erro que a escada existe para impedir.'),

  # ── ESPANHA · empresa de CROP PROTECTION usando creators. Três casos.
  dict(id='COL-ES-001', creator_id=cr.NAO_SEI,
       creator='Lorena Guerra (@agricola_lorew); irmãos Tribaldos (@twinsfarmblog2); '
               'Miriam Delgado (@jovenes_agricultoras); Angel Caralt (@angelocromatto); '
               'Carlos Águila (@Carlos7alella); José Antonio Arcos e Ana Rubio (@khalatea)',
       pais='ES', marca='BASF Agro', marca_tipo='CROP_PROTECTION_COMPANY',
       data='2020-02',
       campanha='#YoSoyAgricultor — concurso de fotografia para agricultores, com '
                'influencers agrícolas como parceiros e jurados',
       categoria='INSTITUTIONAL_SECTOR', produto=cr.NAO_SEI, plataforma='INSTAGRAM',
       disclosure=cr.NAO_SEI, estado='BRAND_COLLABORATION_PROVED',
       mensagem='CORPORATE_IMAGE',
       url='https://www.basf.com/basf/www/es/es/media/Noticias/Noticias2020/basf-agro-lanza--yosoyagricultor--el-concurso-de-fotografia-dest',
       fonte_tipo='BRAND_PRIMARY_RELEASE',
       nota='Release da PRÓPRIA BASF nomeia os influencers com quem se associou. '
            'Empresa de defensivos usando creators agrícolas na Espanha — mas a peça '
            'é IMAGEM DO AGRICULTOR, não promoção de produto fitossanitário. '
            'É exatamente a fronteira que o veredito separa.'),

  dict(id='COL-ES-002', creator_id=cr.NAO_SEI, creator='Sergio Rodríguez (@nitofrutadyverduras)',
       pais='ES', marca='Seipasa', marca_tipo='CROP_PROTECTION_COMPANY', data='2026-03-03',
       campanha='Patrocínio da categoria "Tomatito" dos Premios AgroInfluye 2026',
       categoria='BIOCONTROL', produto=cr.NAO_SEI, plataforma=cr.NAO_SEI,
       disclosure='CATEGORY_SPONSORSHIP_DISCLOSED', estado='BRAND_COLLABORATION_PROVED',
       mensagem='EVENT_PRESENCE',
       url='https://seipasa.com/en/news/seipasa-at-the-agroinfluye-2026-awards/',
       fonte_tipo='BRAND_PRIMARY_RELEASE',
       nota='Empresa de bioprotecção patrocinando uma categoria de prêmio LIGADA A '
            'UMA CULTURA (tomate). É ativação de marca sobre creators, não promoção '
            'de produto. Seipasa é aqui fonte E objeto — não conta como observador '
            'independente do próprio patrocínio.'),

  dict(id='COL-ES-003', creator_id=cr.NAO_SEI, creator=cr.NAO_SEI,
       pais='ES', marca='Syngenta', marca_tipo='CROP_PROTECTION_COMPANY', data='2026-03-03',
       campanha='Patrocínio da categoria "Embajador del AOVE" dos Premios AgroInfluye 2026',
       categoria='INSTITUTIONAL_SECTOR', produto=cr.NAO_SEI, plataforma=cr.NAO_SEI,
       disclosure='CATEGORY_SPONSORSHIP_DISCLOSED', estado='BRAND_COLLABORATION_PROVED',
       mensagem='EVENT_PRESENCE',
       url='https://premiosagroinfluye.com/categorias/',
       fonte_tipo='EVENT_PRIMARY',
       nota='O nome do premiado desta categoria não foi recuperado nesta rodada — '
            'fica NÃO SEI, não preenchido por plausibilidade. O patrocínio, esse, '
            'está declarado pela própria fonte do prêmio.'),

  dict(id='COL-ES-004', creator_id=cr.NAO_SEI, creator='Laura Domínguez (@laura.agrodg)',
       pais='ES', marca='Kuhn Ibérica', marca_tipo='MACHINERY_COMPANY', data='2026-03-03',
       campanha='Patrocínio da categoria "Espiga Dorada" dos Premios AgroInfluye 2026',
       categoria='MACHINERY', produto=cr.NAO_SEI, plataforma=cr.NAO_SEI,
       disclosure='CATEGORY_SPONSORSHIP_DISCLOSED', estado='BRAND_COLLABORATION_PROVED',
       mensagem='EVENT_PRESENCE',
       url='https://premiosagroinfluye.com/categorias/',
       fonte_tipo='EVENT_PRIMARY',
       nota='Maquinaria. Entra no mapa de marcas e NÃO conta para o veredito de '
            'crop protection — categoria não transfere.'),
]

# Evidência de MERCADO (país), separada dos pares creator × marca.
MERCADO = [
  dict(pais='ES', afirmacao='Fenômeno agroinfluencer consolidado; Andalucía concentra '
       '1 em cada 4 criadores de conteúdo agrário do país, com dois polos: olivar '
       '(Jaén/Córdoba/Sevilla) e horticultura de Almería.',
       categoria='INSTITUTIONAL_SECTOR', estado_mercado='CREATOR_MARKET_PROVED',
       url='https://revistamercados.com/andalucia-lidera-el-fenomeno-de-los-agroinfluencers-en-espana/'),
  dict(pais='ES', afirmacao='AGROLAND: encontro que conecta agroinfluencers, agricultores '
       'e MARCAS — existe infraestrutura de intermediação comercial.',
       categoria='INSTITUTIONAL_SECTOR', estado_mercado='BRAND_USE_PROVED',
       url='https://www.plataformatierra.es/innovacion/agroinfluencers-la-nueva-cara-de-la-agricultura-en-las-redes-sociales'),
  dict(pais='IT', afirmacao='Marcas contratam farm-influencer para publicitar produtos; '
       'a Regione Veneto recruta creators agrícolas desde 2023.',
       categoria='INSTITUTIONAL_SECTOR', estado_mercado='BRAND_USE_PROVED',
       url='https://www.influenxer.it/influencer/i-giovani-che-hanno-riscoperto-lagricoltura-e-i-farm-influencer/'),
  dict(pais='IT', afirmacao='Syngenta lança a campanha multimídia "Agcelerators: People '
       'Transforming Agriculture", narrando histórias de inovadores do campo.',
       categoria='INSTITUTIONAL_SECTOR', estado_mercado='BRAND_CONTENT_PROVED',
       url='https://startupitalia.eu/impact/green-economy/nasce-agcelerators-people-transforming-agriculture-per-raccontare-le-storie-di-successo-di-chi-ogni-giorno-innova-in-agricoltura/'),
  dict(pais='FR', afirmacao='New Holland, Kuhn France, Sencrop e Ifor Williams colaboram '
       'com agri-influenceurs para ancorar e promover inovações.',
       categoria='MACHINERY', estado_mercado='BRAND_USE_PROVED',
       url='https://www.reech.com/fr/blog/les-influenceurs/qui-sont-sont-les-agri-youtubeurs'),
  dict(pais='FR', afirmacao='Monetização declarada pelos próprios creators: parcerias são '
       'mais rentáveis que visualizações; ~1.200 € para 4 vídeos/mês a 70.000 visualizações.',
       categoria='INSTITUTIONAL_SECTOR', estado_mercado='MONETISATION_PROVED',
       url='https://www.web-agri.fr/diversification/article/873448/les-agri-influenceurs-levent-le-voile-sur-la-monetisation-de-leurs-contenus'),
  dict(pais='ES', afirmacao='Premios AgroInfluye: 2ª edição em Sevilha com +300 '
       'presentes e ~1.500 por streaming; categorias POR CULTURA patrocinadas por '
       'empresas de insumo — Seipasa (Tomatito), Syngenta (AOVE), Kuhn (Espiga Dorada).',
       categoria='INSTITUTIONAL_SECTOR', estado_mercado='BRAND_USE_PROVED',
       url='https://premiosagroinfluye.com/categorias/'),
  dict(pais='FR', afirmacao='Intercéréales (interprofissão) paga parcerias com creators; '
       'a interprofissão leiteira comunica com personalidades web há anos.',
       categoria='FOOD_COMMODITY', estado_mercado='BRAND_USE_PROVED',
       url='https://reporterre.net/Au-Salon-de-l-agriculture-les-influenceurs-au-service-de-l-agro-industrie'),
]

# A quase-colisão medida nesta rodada. Fica no artefato porque é prova viva da
# lei NAME_MATCH != ENTITY, e porque a próxima busca por ADAMA vai reencontrá-la.
COLISOES = [
  dict(buscado='ADAMA (crop protection)', devolvido='Adamo (operadora de telecom espanhola), '
       'em campanha de embaixador com Jesús Calleja',
       url='https://www.vipnet360.com/newsroom/vipnet360-consolida-reconocimiento-marca-adamo-la-colaboracion-jesus-calleja',
       licao='Uma letra separa a empresa de defensivos de uma operadora de telecom. '
             'Casar por nome teria criado uma "colaboração ADAMA com influencer" inexistente.'),
]


def _creator(c):
    r = cr.registro_vazio()
    r.update({
        'CREATOR_ID': c['id'], 'ORIGIN_ID': c['id'],
        'NAME': c['nome'], 'DISPLAY_NAME': c['display'],
        'COUNTRY': c['pais'], 'REGION': c['regiao'], 'LANGUAGE': c['idioma'],
        'OCCUPATION': c['ocupacao'], 'ENTITY_KIND': 'PERSON',
        'CREATOR_TYPE': c['tipo'],
        'ACTUAL_FARMER': c['produtor'], 'ACTUAL_FARMER_EVIDENCE': c['produtor_ev'],
        # O ponteiro para o outro papel. Nunca uma fusão.
        'SENSOR_ROLE_LINK': 'NOT_LINKED — universo EARLY SIGNAL não consultado nesta rodada',
        'CROPS': c['crops'] or cr.NAO_SEI,
        'CROP_EVIDENCE': c['crop_ev'],
        'REGIONS': [c['regiao']] if c['regiao'] != cr.NAO_SEI else cr.NAO_SEI,
        'SOURCE_URL': c['url'],
        'SOURCE_KIND': 'SEARCH_SUMMARY_NOT_OPENED',
        'SOURCE_ID': MISSION, 'CAPTURE_DATE': CAPTURA, 'COLLECTION_ROUTE': ROTA,
        'AS_OF_DATE': CAPTURA,
        'BRAND_RELATIONSHIP_STATE': 'NOT_KNOWN',
        'ADAMA_COLLABORATION_OBSERVED': 'NOT_OBSERVED',
        'AUDIENCE_TYPE': 'NOT_KNOWN',
        'ACTIVITY_STATE': 'NOT_MEASURED',
        'LAST_ACTIVITY_DATE': cr.NAO_SEI,
        'POSTS_LAST_30D': cr.NAO_SEI, 'POSTS_LAST_90D': cr.NAO_SEI,
        'VIDEOS_LAST_90D': cr.NAO_SEI,
        # Descoberto por pesquisa aberta, não por lista externa.
        'CROP_CLAIMED_BY_SEED': 'NOT_FROM_SEED',
        'CROP_PROVED_BY_CONTENT': cr.NAO_SEI,
        'CROP_PROOF_URLS': [c['url']],
        # O duplo papel: declarado, nunca deduzido um do outro.
        'ACTIVATION_CREATOR': 'NOT_KNOWN',
        'TECHNICAL_SENSOR_CANDIDATE': 'NOT_KNOWN',
        'AGRICULTURAL_RELEVANCE': cr.NAO_SEI, 'TECHNICAL_RELEVANCE': cr.NAO_SEI,
        'HANDLE_EXISTS': 'NOT_TESTED', 'PROFILE_URL': cr.NAO_SEI,
        'NAME_MATCH': 'NOT_TESTED',
    })
    # Relevância de cadeia: default NOT_KNOWN, sobrescrito só com evidência.
    for campo in ('WINE_RELEVANCE', 'VITICULTURE_RELEVANCE',
                  'OLIVE_OIL_RELEVANCE', 'OLIVE_GROWING_RELEVANCE'):
        r[campo] = 'NOT_KNOWN'
    r.update(c.get('cadeia') or {})

    # CULTURA — só sobe a PROVED com evidência que nomeie a cultura.
    r['CROP_STATE'] = 'PROVED' if c['crops'] else 'NOT_PROVED'

    # IDENTIDADE — a página não foi aberta nesta rodada. O estado diz isso.
    r['IDENTITY_STATE'] = 'NOT_PROVED'
    r['IDENTITY_EVIDENCE'] = (
        'nome, região e atividade surfados por WebSearch a partir de %s; '
        'a PÁGINA NÃO FOI ABERTA (egresso do contêiner bloqueia o domínio). '
        'Resolução de perfil e medição pendem da rota Apify no runner.' % c['url'])

    for plataforma, h in (c['handles'] or {}).items():
        r[plataforma] = h
    r['PLATFORMS'] = sorted(c['handles']) if c['handles'] else cr.NAO_SEI
    r['FOLLOWERS_BY_PLATFORM'] = c['seguidores'] or cr.NAO_SEI

    estado, porques = cr.relevancia(r, colaboracoes=[_colab(x) for x in COLABORACOES])
    r['RELEVANCE_STATE'] = estado
    r['WHY_RELEVANT'] = porques
    r['CROP_FIT'] = 'CROP_PROVED' if c['crops'] else 'CROP_NOT_PROVED'
    r['ACTIVITY_RECENCY'] = 'NOT_MEASURED'
    return r


def _colab(c):
    r = {k: cr.NAO_SEI for k in cr.CAMPOS_COLABORACAO}
    r.update({
        'COLLAB_ID': c['id'], 'CREATOR_ID': c['creator_id'], 'CREATOR_NAME': c['creator'],
        'COUNTRY': c['pais'], 'BRAND': c['marca'], 'BRAND_KIND': c['marca_tipo'],
        'DATE': c['data'], 'CAMPAIGN': c['campanha'], 'PRODUCT_CATEGORY': c['categoria'],
        'PRODUCT_NAME': c['produto'], 'PLATFORM': c['plataforma'],
        'SPONSORED_DISCLOSURE': c['disclosure'], 'RELATIONSHIP_STATE': c['estado'],
        'MESSAGE_KIND': c['mensagem'], 'SOURCE_URL': c['url'],
        'SOURCE_KIND': c['fonte_tipo'], 'CAPTURE_DATE': CAPTURA, 'NOTE': c['nota'],
    })
    return r


def montar():
    os.makedirs(cr.BASE, exist_ok=True)
    creators = [_creator(c) for c in CANDIDATOS]
    colabs = [_colab(c) for c in COLABORACOES]

    problemas = []
    for r in creators:
        for f in cr.checar(r):
            problemas.append('%s: %s' % (r['CREATOR_ID'], f))
    if problemas:
        print('PORTAO_BARROU:'); [print('  ' + p) for p in problemas]
        raise SystemExit(1)

    testados = ('ES', 'IT', 'FR')
    veredito = cr.veredito_crop_protection(colabs, paises=testados, testados=testados)

    _grava('CREATORS-ES-IT-FR.json', {
        'SOURCE_ID': MISSION, 'CAPTURED_AT': CAPTURA, 'COLLECTION_ROUTE': ROTA,
        'STATE': 'CANDIDATES — identidade não resolvida nesta rodada',
        'NOTE': 'IDENTITY_STATE=NOT_PROVED em todos: o buscador surfou o fato, a página '
                'não foi aberta. Promoção depende da rota Apify no runner residencial.',
        'COUNT': len(creators), 'CREATORS': creators})
    _grava('BRAND-COLLABORATIONS-EU.json', {
        'SOURCE_ID': MISSION, 'CAPTURED_AT': CAPTURA,
        'NOTE': 'Só pares creator × marca NOMEADOS. Afirmação de mercado vive em '
                'MARKET-EVIDENCE-EU.json e não conta como par.',
        'COUNT': len(colabs), 'COLLABORATIONS': colabs})
    _grava('MARKET-EVIDENCE-EU.json', {
        'SOURCE_ID': MISSION, 'CAPTURED_AT': CAPTURA,
        'CROP_PROTECTION_VERDICT': veredito,
        'MARKET_EVIDENCE': MERCADO,
        'NAME_COLLISIONS_MEASURED': COLISOES,
        'COMPLIANCE': cr.pendencias_de_compliance()})

    print('CREATORS=%d  COLABORACOES=%d  EVIDENCIA_DE_MERCADO=%d'
          % (len(creators), len(colabs), len(MERCADO)))
    for p, v in veredito.items():
        print('  CROP_PROTECTION %s = %-10s %s' % (p, v['ESTADO'], v['MOTIVO'][:70]))


def _grava(nome, corpo):
    with open(os.path.join(cr.BASE, nome), 'w', encoding='utf-8') as f:
        json.dump(corpo, f, ensure_ascii=False, indent=2)
    print('gravado: data/samples/CREATOR-MAP-EAME/%s' % nome)


def resumo():
    regs = cr.carregar('CREATORS-ES-IT-FR.json')
    print('CREATORS=%d' % len(regs))
    for pais in ('ES', 'IT', 'FR'):
        do = [r for r in regs if r['COUNTRY'] == pais]
        com_cultura = [r for r in do if r['CROP_STATE'] == 'PROVED']
        produtores = [r for r in do if r['ACTUAL_FARMER'] == 'PROVED']
        print('  %s  total=%-3d cultura_provada=%-3d produtor_provado=%-3d'
              % (pais, len(do), len(com_cultura), len(produtores)))
    from collections import Counter
    print('  RELEVANCE_STATE:', dict(Counter(r['RELEVANCE_STATE'] for r in regs)))


if __name__ == '__main__':
    {'montar': montar, 'resumo': resumo}.get(
        sys.argv[1] if len(sys.argv) > 1 else 'montar', montar)()
