# SINTONIA EAME — SOURCE PACK ESPANHA
## Ciência → pesquisadores → voz pública + APIs + creators
Curadoria: 2026-08-29

REGRA CENTRAL
1. Primeiro identificar CROP × ISSUE × REGION relevantes.
2. Encontrar estudos científicos sobre esses pares.
3. Extrair autores recorrentes/recentes.
4. Resolver identidade por OpenAlex + ORCID + instituição.
5. Só depois procurar LinkedIn / YouTube / Instagram / outras redes da MESMA pessoa.
6. Rede social é canal; não é prova de autoridade científica.
7. Seguidores = alcance, nunca autoridade.
8. Um pesquisador em 3 redes = uma ORIGIN com 3 CHANNELS.
9. Não inventar @ ou perfil ausente.

==================================================
A. APIs / ROTAS ESTRUTURADAS — PRIORIDADE
==================================================

### SCIENCE / RESEARCHER DISCOVERY

1. OpenAlex API
STATUS: API OFICIAL / RECOMENDADA
BASE: https://api.openalex.org
DOCS: https://help.openalex.org/api/
USO:
- works
- authors
- institutions
- sources
- topics
- filtros e group_by
VALOR SINTONIA:
- descobrir estudos
- descobrir autores
- medir recorrência por CROP × ISSUE
- cruzar autor ↔ instituição
NOTA:
- OpenAlex ID não equivale automaticamente a uma pessoa; preservar conflation/fragmentation.

2. Crossref REST API
STATUS: API PÚBLICA / SEM CADASTRO PARA USO BÁSICO
BASE: https://api.crossref.org/
DOCS: https://www.crossref.org/documentation/retrieve-metadata/rest-api/
USO:
- DOI
- works
- ORCID/ROR quando depositados
- funding
- metadata
VALOR:
- segunda fonte bibliográfica
- confirmação de DOI, autoria, datas e metadados.

3. ORCID Public API
STATUS: API OFICIAL
INFO: https://info.orcid.org/what-is-orcid/services/public-api/
USO:
- buscar registro público
- recuperar dados públicos
VALOR:
- resolver identidade do pesquisador depois que o autor foi descoberto pelos estudos.

4. OpenAIRE Graph API v3
STATUS: API OFICIAL
DOCS: https://graph.openaire.eu/docs/apis/graph-api/overview/
USO:
- research-products
- persons
- organizations
- datasources
VALOR:
- pesquisa europeia, autores, organizações, projetos e produtos científicos.
NOTA:
- usar como fonte independente, não como duplicação cega do OpenAlex.

==================================================
B. DADOS PÚBLICOS ESPANHA — API / MACHINE-READABLE
==================================================

5. AEMET OpenData
STATUS: API REST OFICIAL; exige API key
DOCS: https://opendata.aemet.es/dist/
VALOR:
- observações
- previsões
- climatologia
- município/estação
USO SINTONIA:
- clima nacional fora do alcance da RAIF
- observation clock / agronomic context.

6. datos.gob.es API
STATUS: API OFICIAL
DOCS: https://datos.gob.es/es/apidata
FORMATS: JSON, XML, RDF, TTL, CSV
VALOR:
- discovery programático de datasets públicos espanhóis
- catálogo + geografia + temas
NOTA:
- é catálogo de dados; não substitui o dataset de origem.

7. RAIF — Junta de Andalucía
STATUS: MACHINE-READABLE OFICIAL; download ZIP/XML; catálogo acessível por dados abertos
DATASET:
https://www.juntadeandalucia.es/datosabiertos/portal/dataset/raif
COBERTURA:
- 2006–2026 dependendo da cultura
- parcelas
- amostragens
- tratamentos fitossanitários
- >650 técnicos de campo
CULTURAS PUBLICADAS:
- algodón
- almendro
- arroz
- cereales de invierno
- cítricos
- fresa
- hortícolas
- olivar
- remolacha
- vid
NOTA:
- olivar declarado com atualização semanal; último dataset visto atualizado em 24/08/2026.
- não chamar de "API RAIF" se estivermos consumindo ZIP/XML; é dado estruturado oficial.

8. RAIF clima
STATUS: MACHINE-READABLE OFICIAL / ZIP
DATASET:
https://www.juntadeandalucia.es/datosabiertos/portal/dataset/raif-clima
COBERTURA:
- 79 estações
- histórico desde 2002
VALOR:
- temperatura
- chuva
- umidade
- radiação
- vento
- contexto fitossanitário.

9. Junta de Andalucía — API Estudos e Informes
STATUS: OpenAPI 3
SPEC:
https://datos.juntadeandalucia.es/api/v0/study-reports/openapi.json
USO:
- pesquisar estudos e relatórios oficiais por filtros.

10. SiAR
STATUS: CONSULTA WEB OFICIAL CONFIRMADA
URL:
https://servicio.mapa.gob.es/siarweb/consultaDatos/consultaDatos
NOTA:
- não considerar API documentada até confirmarmos endpoint oficial estável.
- investigar rota estruturada antes de scraping.

11. Eurostat Statistics API
STATUS: API OFICIAL
BASE:
https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/
VALOR:
- escala/área/produção comparável entre Espanha e futuros países EAME.

12. Copernicus Climate Data Store API
STATUS: API OFICIAL
DOCS:
https://cds.climate.copernicus.eu/en/how-to-api
VALOR:
- ERA5/reanalysis
- séries históricas
- camada climática comparável cross-market.

==================================================
C. SOCIAL — O QUE TEM API E O QUE NÃO TEM
==================================================

### YouTube
STATUS: API OFICIAL MUITO ÚTIL
DOCS:
https://developers.google.com/youtube/v3/docs
PODE:
- search
- channels
- videos
- playlists
- comments / commentThreads
- estatísticas públicas
LIMITAÇÃO:
- captions são recurso da API, mas obter o texto da legenda de vídeo de terceiros não deve ser presumido; testar autorização/rota.
DECISÃO:
- usar API oficial primeiro para discovery, IDs, metadata e comentários.
- transcript: rota separada se necessário.

### LinkedIn
STATUS: API OFICIAL NÃO SERVE PARA DISCOVERY AMPLO DO SINTONIA
DOCS:
https://learn.microsoft.com/en-us/linkedin/shared/integrations/people/profile-api
LIMITAÇÕES:
- acesso restrito/aprovado
- perfil depende de autorização e permissões
- armazenamento de dados de terceiros é altamente restrito
DECISÃO:
- não desenhar coleta de pesquisadores/technical voices em cima da API oficial do LinkedIn.
- usar discovery público / rota já testada / Apify quando economicamente útil e dentro das regras.

### Instagram
STATUS: API OFICIAL PARCIAL
DOCS DE REFERÊNCIA META/POSTMAN:
https://www.postman.com/meta/instagram/documentation/6yqw8pt/instagram-api
PODE:
- contas profissionais
- mídia da conta autorizada
- insights
- comments
- hashtagged media em condições específicas
LIMITAÇÕES:
- não acessa contas pessoais/consumer
- exige app/permissões
- não é crawler amplo de todos os creators
DECISÃO:
- API oficial pode complementar.
- para discovery amplo de creators, não contar com ela como solução total.

### TikTok
STATUS: RESEARCH API EXISTE, MAS NÃO É ROTA COMERCIAL PARA O SINTONIA
DOCS:
https://developers.tiktok.com/products/research-api/
LIMITAÇÃO:
- acesso voltado a pesquisadores acadêmicos / organizações elegíveis e pesquisa não comercial.
DECISÃO:
- não planejar pipeline comercial usando TikTok Research API.
- usar discovery público/actor quando houver utilidade medida.

==================================================
D. PESQUISADORES — SEEDS JÁ EXISTENTES NO ACERVO
==================================================

O repositório EAME já contém universo científico espanhol e fila olive-biased.
NÃO tratar esta fila como seleção nacional final.

Seeds de alto interesse já existentes:
- Jesús Mercado-Blanco — IAS-CSIC
- Blanca B. Landa — IAS-CSIC
- Antonio Trapero Casas — Universidad de Córdoba
- Carlos Agustí-Brisach — Universidad de Córdoba
- Juan Moral — Universidad de Córdoba
- Francisco Javier López-Escudero — Universidad de Córdoba
- Raúl de la Rosa — IFAPA
- Angjelina Belaj — IFAPA
- Antonio Valverde-Corredor — IAS-CSIC
- Carmen Gómez-Lama Cabanás — IAS-CSIC
- Jorge Poveda — UPNA
- Francisco Luque — Universidad de Jaén

REGRA:
Esses nomes entram como SEED.
A seleção final deve nascer de:
CROP×ISSUE×REGION → trabalhos → autores → identidade → canais.

==================================================
E. LINKEDIN — VOZ TÉCNICA / PESQUISADORES ENCONTRADOS
==================================================

Perfis públicos encontrados como candidatos; papel deve permanecer separado de alcance.

- Jesús Jiménez Castillo
  https://es.linkedin.com/in/jesús-jiménez-castillo-1b4a207b
  agronomia / olivar / Andalucía

- Antonio Martín de Oliva Ferraro
  https://es.linkedin.com/in/antonio-martín-de-oliva-ferraro-15b02367
  engenheiro agrônomo / consultor / olivar, almendro

- Francisco Fernández Barroso
  https://es.linkedin.com/in/francisco-fernández-barroso
  agrônomo / cultivos leñosos

- Eugenia Díaz
  https://es.linkedin.com/in/eugeniadiazmkycom
  olivicultura de precisão / Andalucía

- Luiza Sánchez
  https://es.linkedin.com/in/luizasanchez
  pesquisadora predoctoral / fitopatologia / BIOLIVE / UCO

- Juan Moral
  https://es.linkedin.com/in/juan-moral-19272235
  pesquisador UCO / doenças do olivo

- Zakaria Janfi
  https://es.linkedin.com/in/zakaria-janfi-73aa25169
  fitopatologia / biocontrole / melhoramento do olivo

- Juan Sánchez Llanes
  https://es.linkedin.com/in/juan-sánchez-llanes-851016231
  agronomia / olivar / irrigação / modelagem

NOTA:
O repo já possui 67 vozes técnicas elegíveis e uma fila de 20, mas 13/20 vieram de TITLE_SEARCH com viés andaluz e o conteúdo público ainda estava NOT_TESTED. Reusar como seed, não como verdade nacional.

==================================================
F. AGROCREATORS / INFLUENCERS ESPANHA — SEEDS PÚBLICOS
==================================================

### Current / recent verified seeds
- @agripilar — Pilar Pascual
- @agro_blog86 — Guillermo Asín
- @elguardiandelatierra — Lander de Bevere
  YouTube: @ElGuardiandelaTierra
- @agrofamily_moralesperez — Lucía Morales Pérez, El Ejido / Almería
- @agrololas — Miguel Lolas, Antequera
- @luciiaacasal — Lucía Casal
- @nitofrutasyverduras — Sergio Rodríguez
- @agriproduccion — Alberto Rojas
- @laura.agrodg — Laura Domínguez
- @valdelmazo — Marta García
- @oliverio_rodfer — Oliverio Rodríguez
- @huerto_ecologico.marc — Marc Miralles
- @angel_illescas_ — Ángel Illescas
- @la_fuina_de_los_monegros — Eduardo Luna
- @marcosgt9 — Marc Guilanyà
- @marioagrario — Mario Rojo

### Scientific study seed (2024; REVALIDATE before collection)
Study:
"Acercándonos a la Figura del Agroinfluencer en España"
DOI: 10.62161/revvisual.v16.5312

Handles listed in the study included:
- @angelocromatto
- @jovenes_agricultoras
- @lucia_velasco_rodriguez_
- @fincalamaye_
- @agricola_lorew
- @agripilar
- @agrijoven
- @agricbv
- @doydasdavid
- @valdelmazo
- @repoblando
- @alex130493
- @ganaderia_cambureru
- @tomy_rohde
- @agrodiosle

IMPORTANT:
- This is a 2024 sample, not a 2026 authority ranking.
- Revalidate whether account still exists, platform(s), declared occupation, crops, geography and recent activity.
- Do not select by follower count alone.

==================================================
G. ORDEM DE COLETA RECOMENDADA — ESPANHA
==================================================

1. NATIONAL PRIORITY
   MAPA / Eurostat / official sources
   -> crops / regions / scale

2. CROP × ISSUE
   RAIF / official fitosanitary / regulatory
   -> what matters where

3. SCIENCE
   OpenAlex + Crossref + OpenAIRE
   -> works for selected pairs

4. RESEARCHERS
   recurring/recent authors
   -> ORCID + institution
   -> LinkedIn / YouTube / public channels only after identity

5. TECHNICAL VOICES
   LinkedIn + institutions + technical media

6. PRODUCER / CREATOR VOICE
   Instagram + YouTube + TikTok
   -> only creators linked to relevant crops/regions/issues

7. COMMENTS / AUDIENCE
   classify questions, problems, field observations, technical discussion
   -> do not convert comments into "field truth"

8. SATURATION
   20 people = first batch only
   Continue only while marginal intelligence gain remains material.

==================================================
H. WHAT NOT TO DO
==================================================

- do not search "20 researchers" before crop/issue priority.
- do not search "20 influencers" by follower count.
- do not infer profession from bio fragments without evidence.
- do not count organization as technical person.
- do not count same person across networks as multiple origins.
- do not infer country of a fact from country of the author/channel.
- do not treat failed read / 403 / no transcript as zero/silence.
