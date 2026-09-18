# SOURCE COLLECTION READINESS V1 — CENSO (gerado)

> **Gerado** por `provas/medir_source_collection_readiness.py`. Nao editar a mao: o JSON irmao
> (`data/derivados/SOURCE-COLLECTION-READINESS-V1.json`) e a fonte, e um teste reprova se divergirem.

```
TOTAL_SOURCES                        170
IT_SOURCES                           157
EU_APPLICABLE                        13
DECLARED_CONTRACT                    2
COLLECTION_WIRED                     114
FLOW_OBSERVED                        95
SOURCE_COLLECTION_READY_BEFORE       6
SOURCE_COLLECTION_READY_AFTER        95
NEW_SOURCE_COLLECTION_READY          89
STILL_NOT_READY                      75
RELEVANCE_SIM                        6
RELEVANCE_PENDING                    164
BIG_COLLECTION_EXECUTABLE_BEFORE     6
BIG_COLLECTION_EXECUTABLE_AFTER      6
SOURCES_CONFIGURED                   107
SOURCES_CANARY_PASS                  88
SOURCES_CANARY_FAIL                  19
SOURCES_CANARY_NOT_RUN               0
INDEX_COLLECTION_READINESS_STALE     YES
```

## Os quatro contadores — quatro owners, nenhum acertado para bater

| contador | valor | o que mede | owner | como | stale? |
|---|---|---|---|---|---|
| `ATLAS_FICHAS` | **210** | fichas do Atlas com campo SOURCE_ID valido (ficha multinacional conta por SOURCE_ID) | `system-map/scripts/scan_sources.py -> system-map/data/sources.generated.json` | gerado | NAO — regenerado pela cadeia do mapa |
| `ATLAS_HEADER_STAMP` | **190** | o numero que o cabecalho do Atlas declara (marcador SOURCE_ID_COUNT) | `docs/fontes/ATLAS-DE-FONTES-EAME.md linha 9 (a mao)` | carimbo escrito a mao | SIM — o proprio indice regista a divergencia (190 vs 210); decisao humana, nao correcao automatica |
| `ESCADA_REGISTADA` | **173** | fichas com exemplo real guardado (degrau 2 da escada) | `system-map/scripts/scan_sources.py (escada) -> docs/fontes/INDICE-DE-FONTES.md` | gerado | NAO SEI — o degrau le a ficha, nao a evidencia em disco; nao medido nesta missao |
| `CONTRATOS_DECLARADOS` | **5** | fontes com bloco SOURCE_ID em docs/operacao/CONTRATOS-DAS-FONTES-EAME.md — e SO isso | `scan_sources.py::dos_contratos() le CONTRATOS-DAS-FONTES-EAME.md` | gerado de um documento a mao | SIM como medida de readiness — nao le regras/italy_contracts.mjs nem o coletor; 1 das 6 fontes da Big Collection esta «sim» |

## A contraprova — as seis da primeira Big Collection

| SOURCE_ID | indice «a maquina busca?» | FLOW_OBSERVED | observacoes HEALTHY com bytes |
|---|---|---|---|
| `IT-T2-002` | nao | YES | 128 |
| `IT-T2-004` | nao | YES | 7 |
| `IT-T3-002` | nao | YES | 3 |
| `IT-T3-008` | nao | YES | 3 |
| `IT-T3-010` | nao | YES | 3 |
| `IT-T4-001` | sim | YES | 3 |

## Por forma de aquisicao

| SHAPE | FONTES | READY | BLOCKED | TOOL | NEW CODE? | blockers |
|---|---|---|---|---|---|---|
| `PDF_DISCOVERY_PAGE` | 41 | 39 | 2 | coleta/italy_pilot_collect.mjs (case proprio); coleta/italy_pilot_collect.mjs (forma generica ACQUISITION) | coletor generico (forma lida do contrato) — SOURCE-COLLECTION-READINESS-V1 | CAPABILITY_MISSING 1, CANARY_FAILED 1 |
| `HTML_ARTICLE_DISCOVERY` | 67 | 49 | 18 | coleta/italy_pilot_collect.mjs (forma generica ACQUISITION) | coletor generico (forma lida do contrato) — SOURCE-COLLECTION-READINESS-V1 | CANARY_FAILED 18 |
| `PDF_DIRECT` | 4 | 4 | 0 | coleta/italy_pilot_collect.mjs (case proprio); coleta/italy_pilot_collect.mjs (forma generica ACQUISITION) | coletor generico (forma lida do contrato) — SOURCE-COLLECTION-READINESS-V1 | — |
| `HTML_STATIC` | 1 | 1 | 0 | coleta/italy_pilot_collect.mjs (case proprio) | nenhum | — |
| `CSV_DATASET` | 1 | 1 | 0 | coleta/italy_pilot_collect.mjs (case proprio) | nenhum | — |
| `JSON_API` | 43 | 0 | 43 | coleta/agrifood_ue.py (nao registado em pedido/receitas.py); coleta/corpus_pesquisador.py (ORCID/OpenAlex); coleta/corpus_pesquisador.py (corpus-pesquisador, T6; retorno LEGADO/CATALOG) | nenhum | CAPABILITY_MISSING 5, NOT_WIRED 38 |
| `OFFICIAL_API` | 3 | 1 | 2 | coleta/cellar.sh + coleta/eu_regulatorio_executor.py (SOURCE_ID fixo = EU-T4-001); coleta/eppo_gd.py (eppo, T3; nunca correu; API exige token); coleta/eu_regulatorio_executor.py (regulatorio-eu, T4) | nenhum | NOT_WIRED 1, AUTH_REQUIRED 1 |
| `BROWSER_PUBLIC` | 4 | 0 | 4 | — | nenhum | BROWSER_REQUIRED 4 |
| `DATASET_ODS` | 1 | 0 | 1 | — | nenhum | CAPABILITY_MISSING 1 |
| `ROUTE_UNKNOWN` | 5 | 0 | 5 | — | nenhum | ROUTE_UNKNOWN 5 |

## Por blocker

| BLOCKER | FONTES |
|---|---|
| `NOT_WIRED` | 39 |
| `CANARY_FAILED` | 19 |
| `CAPABILITY_MISSING` | 7 |
| `ROUTE_UNKNOWN` | 5 |
| `BROWSER_REQUIRED` | 4 |
| `AUTH_REQUIRED` | 1 |

## Fonte a fonte

| SOURCE_ID | T | SHAPE | wired | canario | fluxo | indice | relev. | READY | EXEC | blocker | documento observado |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `EU-T1-001` | T1 | JSON_API | NO | NOT_RUN | NO | nao | NAO_AVALIADA | NO | NO | `CAPABILITY_MISSING` nenhum coletor desta casa percorre a forma JSON_API para esta fonte |  |
| `EU-T1-002` | T1 | JSON_API | NO | NOT_RUN | NO | nao | NAO_AVALIADA | NO | NO | `CAPABILITY_MISSING` nenhum coletor desta casa percorre a forma JSON_API para esta fonte |  |
| `EU-T10-001` | T10 | JSON_API | NO | NOT_RUN | NO | nao | NAO_AVALIADA | NO | NO | `NOT_WIRED` capacidade existe, mas nenhuma receita despacha esta fonte |  |
| `EU-T12-001` | T12 | OFFICIAL_API | NO | NOT_RUN | NO | nao | NAO_AVALIADA | NO | NO | `NOT_WIRED` capacidade existe, mas nenhuma receita despacha esta fonte |  |
| `EU-T2-001` | T2 | JSON_API | NO | NOT_RUN | NO | nao | NAO_AVALIADA | NO | NO | `CAPABILITY_MISSING` nenhum coletor desta casa percorre a forma JSON_API para esta fonte |  |
| `EU-T2-002` | T2 | JSON_API | NO | NOT_RUN | NO | nao | NAO_AVALIADA | NO | NO | `CAPABILITY_MISSING` nenhum coletor desta casa percorre a forma JSON_API para esta fonte |  |
| `EU-T2-003` | T2 | JSON_API | NO | NOT_RUN | NO | nao | NAO_AVALIADA | NO | NO | `CAPABILITY_MISSING` nenhum coletor desta casa percorre a forma JSON_API para esta fonte |  |
| `EU-T3-001` | T3 | OFFICIAL_API | NO | NOT_RUN | NO | nao | NAO_AVALIADA | NO | NO | `AUTH_REQUIRED` ficha: API REST devolve 403 sem token EPPO |  |
| `EU-T4-001` | T4 | OFFICIAL_API | YES | FAIL | YES | sim | NAO_AVALIADA | YES | NO | — | https://eur-lex.europa.eu/legal-content/IT/TXT/PDF/?uri=CELEX:32026R1696 |
| `EU-T4-002` | T4 | BROWSER_PUBLIC | NO | NOT_RUN | NO | nao | NAO_AVALIADA | NO | NO | `BROWSER_REQUIRED` ficha: aplicacao Angular (SPA) + API interna — observado, nao obtido |  |
| `EU-T5-001` | T5 | JSON_API | NO | NOT_RUN | NO | nao | NAO_AVALIADA | NO | NO | `NOT_WIRED` capacidade existe, mas nenhuma receita despacha esta fonte |  |
| `EU-T8-001` | T8 | ROUTE_UNKNOWN | NO | NOT_RUN | NO | nao | NAO_AVALIADA | NO | NO | `ROUTE_UNKNOWN` ficha sem URL |  |
| `EU-T9-002` | T9 | BROWSER_PUBLIC | NO | NOT_RUN | NO | nao | NAO_AVALIADA | NO | NO | `BROWSER_REQUIRED` ficha: Meta Ads Library — rota nao executada; so abre com janela grafi |  |
| `IT-T1-002` | T1 | HTML_ARTICLE_DISCOVERY | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | https://www.provincia.tn.it/News/Comunicati-stampa |
| `IT-T1-003` | T1 | HTML_ARTICLE_DISCOVERY | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | https://www.regione.toscana.it/-/posta-elettronica-certificata-pec |
| `IT-T1-004` | T1 | HTML_ARTICLE_DISCOVERY | YES | FAIL | NO | nao | NAO_AVALIADA | NO | NO | `CANARY_FAILED` EMPTY_LIST — a entrada nao listou nenhum documento que case com LINK_P |  |
| `IT-T1-005` | T1 | HTML_ARTICLE_DISCOVERY | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | https://www.regione.umbria.it/in-evidenza/-/asset_publisher/iIpCxObecPVe/content/invio-com |
| `IT-T1-006` | T1 | HTML_ARTICLE_DISCOVERY | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | https://arsac.calabria.it/arsac-chi-siamo/ |
| `IT-T1-007` | T1 | HTML_ARTICLE_DISCOVERY | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | https://www.arsial.it/pubblicazioni-e-ricerche |
| `IT-T1-008` | T1 | PDF_DISCOVERY_PAGE | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | https://www.ersaf.lombardia.it/wp-content/uploads/2024/08/SEO31_31-07-20241.pdf |
| `IT-T1-009` | T1 | HTML_ARTICLE_DISCOVERY | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | https://www.regione.lazio.it/notizie/agricoltura/intervento-settoriale-vitivinicolo-della- |
| `IT-T1-010` | T1 | HTML_ARTICLE_DISCOVERY | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | http://www.regione.abruzzo.it/notizie/economia-l-abruzzo-da-record-export-pil-ed-occupazio |
| `IT-T1-011` | T1 | HTML_ARTICLE_DISCOVERY | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | https://www.regione.umbria.it/agricoltura/notizia/-/asset_publisher/PVUq7ammJALj/content/l |
| `IT-T1-012` | T1 | HTML_ARTICLE_DISCOVERY | YES | FAIL | NO | nao | NAO_AVALIADA | NO | NO | `CANARY_FAILED` EMPTY_LIST — a entrada nao listou nenhum documento que case com LINK_P |  |
| `IT-T1-013` | T1 | HTML_ARTICLE_DISCOVERY | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | https://www.sementi.it/eventi/criticita-e-opportunita-della-coltura-del-girasole/ |
| `IT-T1-014` | T1 | HTML_ARTICLE_DISCOVERY | YES | FAIL | NO | nao | NAO_AVALIADA | NO | NO | `CANARY_FAILED` EMPTY_LIST — a entrada nao listou nenhum documento que case com LINK_P |  |
| `IT-T1-015` | T1 | HTML_ARTICLE_DISCOVERY | YES | FAIL | NO | nao | NAO_AVALIADA | NO | NO | `CANARY_FAILED` EMPTY_LIST — a entrada nao listou nenhum documento que case com LINK_P |  |
| `IT-T1-016` | T1 | HTML_ARTICLE_DISCOVERY | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | https://www.italiaolivicola.it/consiglio-di-amministrazione/ |
| `IT-T1-017` | T1 | HTML_ARTICLE_DISCOVERY | YES | FAIL | NO | nao | NAO_AVALIADA | NO | NO | `CANARY_FAILED` status 400 / 155 bytes | https://olivoeolio.edagricole.it/notizie-dalle-aziende/evolio-expo-conquista-usa-buyer-pro |
| `IT-T1-018` | T1 | HTML_ARTICLE_DISCOVERY | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | https://www.rivistadiagraria.org/news/produttori-zafferano-proviene-miglior-zafferano-del- |
| `IT-T1-019` | T1 | PDF_DISCOVERY_PAGE | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | https://siagr.it/wp-content/uploads/2025/01/Statuto-della-Societa-Italiana-di-Agronomia19. |
| `IT-T1-020` | T1 | HTML_ARTICLE_DISCOVERY | YES | FAIL | NO | nao | NAO_AVALIADA | NO | NO | `CANARY_FAILED` EMPTY_LIST — a entrada nao listou nenhum documento que case com LINK_P |  |
| `IT-T1-021` | T1 | HTML_ARTICLE_DISCOVERY | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | https://agronotizie.imagelinenetwork.com/interessi/eventi/16434 |
| `IT-T1-022` | T1 | HTML_ARTICLE_DISCOVERY | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | https://olivonews.it/contatti-lolivo-news/ |
| `IT-T1-023` | T1 | HTML_ARTICLE_DISCOVERY | YES | FAIL | NO | nao | NAO_AVALIADA | NO | NO | `CANARY_FAILED` EMPTY_LIST — a entrada nao listou nenhum documento que case com LINK_P |  |
| `IT-T10-002` | T10 | HTML_ARTICLE_DISCOVERY | YES | FAIL | NO | nao | NAO_AVALIADA | NO | NO | `CANARY_FAILED` EMPTY_LIST — a entrada nao listou nenhum documento que case com LINK_P |  |
| `IT-T10-006` | T10 | HTML_ARTICLE_DISCOVERY | YES | FAIL | NO | nao | NAO_AVALIADA | NO | NO | `CANARY_FAILED` EMPTY_LIST — a entrada nao listou nenhum documento que case com LINK_P |  |
| `IT-T10-007` | T10 | HTML_ARTICLE_DISCOVERY | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | https://www.ismea.it/istituto-di-servizi-per-il-mercato-agricolo-alimentare |
| `IT-T10-008` | T10 | HTML_ARTICLE_DISCOVERY | YES | FAIL | NO | nao | NAO_AVALIADA | NO | NO | `CANARY_FAILED` EMPTY_LIST — a entrada nao listou nenhum documento que case com LINK_P |  |
| `IT-T10-009` | T10 | HTML_ARTICLE_DISCOVERY | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | https://www.bo.camcom.gov.it/it/blog/un-milione-di-euro-trattenere-i-giovani-bologna-doman |
| `IT-T10-010` | T10 | PDF_DIRECT | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | https://www.csoservizi.com/wp-content/uploads/2025/03/AGRIPAT_SCH_SINTESI_INIZIALE_DEF.pdf |
| `IT-T10-011` | T10 | HTML_ARTICLE_DISCOVERY | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | https://www.ruminantia.it/borse-merci-e-non-solo/ |
| `IT-T10-012` | T10 | PDF_DISCOVERY_PAGE | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | https://www.vinidabruzzo.it/wp-content/uploads/2024/04/QN-ITINERARI-1.pdf |
| `IT-T10-013` | T10 | HTML_ARTICLE_DISCOVERY | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | https://www.tutelaaranciarossa.it/la-storia-arancia/ |
| `IT-T10-014` | T10 | PDF_DISCOVERY_PAGE | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | https://granapadano.kleecks-cdn.com/wp-content/uploads/2023/02/Programma-sviluppo-rurale-l |
| `IT-T10-015` | T10 | PDF_DISCOVERY_PAGE | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | https://www.prosecco.it/wp-content/uploads/2023/07/Pagina-per-sito-web.pdf |
| `IT-T10-016` | T10 | HTML_ARTICLE_DISCOVERY | YES | FAIL | NO | nao | NAO_AVALIADA | NO | NO | `CANARY_FAILED` EMPTY_LIST — a entrada nao listou nenhum documento que case com LINK_P |  |
| `IT-T11-001` | T11 | ROUTE_UNKNOWN | NO | NOT_RUN | NO | nao | NAO_AVALIADA | NO | NO | `ROUTE_UNKNOWN` ficha sem URL |  |
| `IT-T11-005` | T11 | HTML_ARTICLE_DISCOVERY | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | https://www.simei.it/news-media/news/venerdivino-oltre-400-professionisti-del-vino-insieme |
| `IT-T12-003` | T12 | PDF_DISCOVERY_PAGE | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | https://ciaprod.s3.amazonaws.com/media/filer_public/a6/9e/a69ed547-c7c8-405e-bfa4-5dfbcbab |
| `IT-T12-004` | T12 | HTML_ARTICLE_DISCOVERY | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | https://www.confagricoltura.it/ita/confagricoltura/la-nostra-storia |
| `IT-T12-005` | T12 | PDF_DISCOVERY_PAGE | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | https://aiab.it/wp-content/uploads/2023/01/AIAB-Aiuti-di-Stato.pdf |
| `IT-T12-006` | T12 | PDF_DISCOVERY_PAGE | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | https://www.ciatoscana.eu/home/wp-content/uploads/2026/02/inn-pratica_volume_il-futuro-del |
| `IT-T2-001` | T2 | PDF_DISCOVERY_PAGE | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | https://www.arpae.it/it/temi-ambientali/meteo/report-meteo/bollettini-e-rapporti-agrometeo |
| `IT-T2-002` | T2 | PDF_DIRECT | YES | PASS | YES | nao | SIM | YES | YES | — | https://www.arpa.veneto.it/risorse/data-agrometeo/agrometeo/32zone/agro_01.pdf |
| `IT-T2-004` | T2 | HTML_STATIC | YES | PASS | YES | nao | SIM | YES | YES | — | http://www.sias.regione.sicilia.it/NHEOWL0530_00.html |
| `IT-T2-006` | T2 | HTML_ARTICLE_DISCOVERY | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | https://www.arpacampania.it/news/-/asset_publisher/UJfyqynXQe0y/content/asi-caivano-esiti- |
| `IT-T2-007` | T2 | HTML_ARTICLE_DISCOVERY | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | https://www.arpa.sicilia.it/temi-ambientali/aria/bollettino-qualita-dellaria-isola-di-vulc |
| `IT-T2-008` | T2 | HTML_ARTICLE_DISCOVERY | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | https://www.arpat.toscana.it/evento/toscana-stati-generali-dellambiente/ |
| `IT-T2-009` | T2 | PDF_DISCOVERY_PAGE | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | https://www.isprambiente.gov.it/it/files/iso_9001-ita-c859101-2-20260709.pdf |
| `IT-T2-010` | T2 | HTML_ARTICLE_DISCOVERY | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | https://www.appa.provincia.tn.it/News/Comunicati-stampa |
| `IT-T2-011` | T2 | PDF_DISCOVERY_PAGE | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | https://www.arpalombardia.it/media/3filtsmf/la-montagna-che-cambia-crnv-ottobre-2026.pdf |
| `IT-T2-012` | T2 | HTML_ARTICLE_DISCOVERY | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | https://www.arpa.fvg.it/news/ufficio-stampa/ |
| `IT-T2-013` | T2 | HTML_ARTICLE_DISCOVERY | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | https://www.arpalazio.it/web/guest/rete-micro-meteorologica |
| `IT-T2-014` | T2 | PDF_DIRECT | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | https://www.arpamolise.it/Comunicazione/Pubblicazioni/pdf/cartaservizi.pdf |
| `IT-T2-015` | T2 | PDF_DISCOVERY_PAGE | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | http://www.agrometeorologia.it/wp-content/uploads/2021/03/2021_brochure_it.pdf |
| `IT-T2-016` | T2 | PDF_DISCOVERY_PAGE | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | https://www.arpa.marche.it/images/pdf/agenzia/TARIFFARIO_2026.pdf |
| `IT-T2-017` | T2 | HTML_ARTICLE_DISCOVERY | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | https://www.iret.cnr.it/sede/sesto-fiorentino-fi/ |
| `IT-T2-018` | T2 | HTML_ARTICLE_DISCOVERY | YES | FAIL | NO | nao | NAO_AVALIADA | NO | NO | `CANARY_FAILED` EMPTY_LIST — a entrada nao listou nenhum documento que case com LINK_P |  |
| `IT-T2-019` | T2 | HTML_ARTICLE_DISCOVERY | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | https://www.arpa.piemonte.it/notizia/intervento-arpa-piemonte-sul-torrente-scrivia-seguito |
| `IT-T2-020` | T2 | PDF_DISCOVERY_PAGE | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | https://www.artaabruzzo.it/download/aree/qualita/MIP_07_01_01_modulo_reclami_rev_01.pdf |
| `IT-T2-021` | T2 | HTML_ARTICLE_DISCOVERY | YES | FAIL | NO | nao | NAO_AVALIADA | NO | NO | `CANARY_FAILED` EMPTY_LIST — a entrada nao listou nenhum documento que case com LINK_P |  |
| `IT-T2-022` | T2 | HTML_ARTICLE_DISCOVERY | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | https://www.arpa.vda.it/notizie/acqua/tronchi-e-rami-nei-fiumi-dal-cielo-lintelligenza-art |
| `IT-T2-023` | T2 | HTML_ARTICLE_DISCOVERY | YES | FAIL | NO | nao | NAO_AVALIADA | NO | NO | `CANARY_FAILED` status 404 / 362228 bytes | https://www.arpab.it/articoli/news/arpa-informa/itemDataObject.url |
| `IT-T2-024` | T2 | PDF_DISCOVERY_PAGE | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | https://www.anbi.it/public/sezioni/def-indagine-conoscitiva-ix-commissione-anbi-imp---copi |
| `IT-T3-001` | T3 | ROUTE_UNKNOWN | NO | NOT_RUN | NO | nao | NAO_AVALIADA | NO | NO | `ROUTE_UNKNOWN` ficha sem URL |  |
| `IT-T3-002` | T3 | PDF_DISCOVERY_PAGE | YES | PASS | YES | nao | SIM | YES | YES | — | https://agricoltura.regione.campania.it/difesa/bollettini/bollettini_2026/pdf/SA-16-09.pdf |
| `IT-T3-008` | T3 | PDF_DISCOVERY_PAGE | YES | PASS | YES | nao | SIM | YES | YES | — | https://www.agrometeopuglia.it/bollettino-elettronico/settimanale/2026/Notiziario_Agromete |
| `IT-T3-010` | T3 | PDF_DISCOVERY_PAGE | YES | PASS | YES | nao | SIM | YES | YES | — | http://www.apol.it/documenti/notizie/Bollettino_Mosca_dellOlivo_n_10_del_14_09_2026.pdf |
| `IT-T3-011` | T3 | PDF_DISCOVERY_PAGE | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | https://www.agrios.it/wp-content/uploads/Requisiti-concimi-AGRIOS-2026.pdf |
| `IT-T3-013` | T3 | HTML_ARTICLE_DISCOVERY | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | https://agricoltura.regione.emilia-romagna.it/piani-programmi-progetti |
| `IT-T3-014` | T3 | HTML_ARTICLE_DISCOVERY | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | https://www.protezionedellepiante.it/account-area-riservata |
| `IT-T3-015` | T3 | HTML_ARTICLE_DISCOVERY | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | https://www.regione.toscana.it/-/posta-elettronica-certificata-pec |
| `IT-T3-016` | T3 | HTML_ARTICLE_DISCOVERY | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | https://www.regione.veneto.it/web/programmi-comunitari/pr-fesr-2021-2027 |
| `IT-T3-017` | T3 | HTML_ARTICLE_DISCOVERY | YES | FAIL | NO | nao | NAO_AVALIADA | NO | NO | `CANARY_FAILED` EMPTY_LIST — a entrada nao listou nenhum documento que case com LINK_P |  |
| `IT-T3-018` | T3 | HTML_ARTICLE_DISCOVERY | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | https://www.ispa.cnr.it/sede-ispa-di-bari |
| `IT-T3-019` | T3 | HTML_ARTICLE_DISCOVERY | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | https://www.agroinnova.unito.it/it/ricerca/progetti-di-ricerca/progetti-corso |
| `IT-T3-020` | T3 | PDF_DISCOVERY_PAGE | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | https://www.societaentomologicaitaliana.it/wp-content/uploads/2026/06/Locandina-SEI_-Romit |
| `IT-T3-021` | T3 | HTML_ARTICLE_DISCOVERY | YES | FAIL | NO | nao | NAO_AVALIADA | NO | NO | `CANARY_FAILED` EMPTY_LIST — a entrada nao listou nenhum documento que case com LINK_P |  |
| `IT-T4-001` | T4 | CSV_DATASET | YES | PASS | YES | sim | SIM | YES | YES | — | https://www.dati.salute.gov.it/sites/default/files/opendata/PROD_FTS_6_20260914.csv |
| `IT-T5-002` | T5 | HTML_ARTICLE_DISCOVERY | YES | FAIL | NO | nao | NAO_AVALIADA | NO | NO | `CANARY_FAILED` EMPTY_LIST — a entrada nao listou nenhum documento que case com LINK_P |  |
| `IT-T5-003` | T5 | PDF_DISCOVERY_PAGE | NO | NOT_RUN | NO | nao | NAO_AVALIADA | NO | NO | `CAPABILITY_MISSING` nenhum coletor desta casa percorre a forma PDF_DISCOVERY_PAGE para est |  |
| `IT-T5-006` | T5 | HTML_ARTICLE_DISCOVERY | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | https://www.cnr.it/it/cnr-in-numeri |
| `IT-T5-007` | T5 | PDF_DISCOVERY_PAGE | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | https://www.iaraosta.it/wp-content/uploads/2026/07/Carta-della-qualita-FIRMATA.pdf |
| `IT-T5-008` | T5 | PDF_DISCOVERY_PAGE | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | https://www.agrion.it/2021/wp-content/uploads/2023/04/09-WEB-Informativa-newsletter.pdf |
| `IT-T5-009` | T5 | PDF_DISCOVERY_PAGE | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | https://www.fondazioneminoprio.it/wp-content/uploads/2025/04/REGOLAMENTO-FM-2025-26.pdf |
| `IT-T5-010` | T5 | PDF_DISCOVERY_PAGE | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | https://www.fondazionenavarra.it/images/pdf/la_pianura_n_3_2010_copertina.pdf |
| `IT-T5-011` | T5 | PDF_DISCOVERY_PAGE | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | https://www.uniba.it/it/ricerca/dipartimenti/processi-e-subprocessi-dei-dipartimenti-di-ri |
| `IT-T5-012` | T5 | PDF_DISCOVERY_PAGE | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | https://www.agr.unipi.it/wp-content/uploads/2026/07/ad-agraria.pdf |
| `IT-T5-013` | T5 | PDF_DISCOVERY_PAGE | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | https://www.crpa.it/media/crpa_www/images/contattaci/QRCode_01253030355_CRPA.pdf |
| `IT-T5-014` | T5 | PDF_DISCOVERY_PAGE | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | https://www.unitus.it/wp-content/uploads/2024/02/Linee-guida-con-allegati_2023.24-2.pdf |
| `IT-T5-015` | T5 | HTML_ARTICLE_DISCOVERY | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | https://www.ibbr.cnr.it/ibbr/news/iscrizioni-aperte-per-il-6-maria-ciaramella |
| `IT-T5-016` | T5 | PDF_DISCOVERY_PAGE | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | https://air.unimi.it/sr/static/DS6/AIR-nuova_interfaccia.pdf |
| `IT-T5-017` | T5 | PDF_DISCOVERY_PAGE | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | https://www.unifi.it/sites/default/files/migrated/documents/flore_faq.pdf |
| `IT-T5-018` | T5 | PDF_DIRECT | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | https://www.unibo.it/it/allegati/policy-di-ateneo-per-l2019accesso-aperto-alle-pubblicazio |
| `IT-T5-019` | T5 | PDF_DISCOVERY_PAGE | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | https://wwwassets.unipd.it/sites/default/files/2026-04/IRIS%20GUIDA%20RAPIDA%20PER%20UTENT |
| `IT-T5-020` | T5 | PDF_DISCOVERY_PAGE | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | https://iris.unito.it/sr/htm/pdf/Desktop_prodotti_v3.pdf |
| `IT-T5-021` | T5 | HTML_ARTICLE_DISCOVERY | YES | FAIL | NO | nao | NAO_AVALIADA | NO | NO | `CANARY_FAILED` EMPTY_LIST — a entrada nao listou nenhum documento que case com LINK_P |  |
| `IT-T5-022` | T5 | PDF_DISCOVERY_PAGE | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | https://journals.fupress.net/wp-content/uploads/2025/10/Call-N31.pdf |
| `IT-T5-023` | T5 | PDF_DISCOVERY_PAGE | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | https://www.ssica.it/wp-content/uploads/2025/03/PROGETTO-ACTION.pdf |
| `IT-T5-024` | T5 | HTML_ARTICLE_DISCOVERY | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | https://disaa.unimi.it/index.php/it/eventi/festival-del-parco-di-monza-le-attivita-e-i-lab |
| `IT-T5-025` | T5 | HTML_ARTICLE_DISCOVERY | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | http://www.santannapisa.it/it/news/progetto-innoflorenerg |
| `IT-T5-026` | T5 | PDF_DISCOVERY_PAGE | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | https://www.unipa.it/dipartimenti/saaf/.content/documenti/Bando-Tutor-alla-pari-per-studen |
| `IT-T5-027` | T5 | HTML_ARTICLE_DISCOVERY | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | https://www.dafnae.unipd.it/news/termine/node/18429 |
| `IT-T5-028` | T5 | HTML_ARTICLE_DISCOVERY | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | https://di4a.uniud.it/it/organi/delegati-di-dipartimento |
| `IT-T5-029` | T5 | PDF_DISCOVERY_PAGE | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | https://cdn.docs.univr.it/documenti/Documento/allegati/allegati375197.pdf |
| `IT-T5-030` | T5 | HTML_ARTICLE_DISCOVERY | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | https://www.unite.it/UniTE/Bioscienze_e_Tecnologie_Agro-Alimentari_e_Ambientali/News_ed_Ev |
| `IT-T5-031` | T5 | ROUTE_UNKNOWN | NO | NOT_RUN | NO | nao | NAO_AVALIADA | NO | NO | `ROUTE_UNKNOWN` manifesto: exemplo TEXTO numa pasta de ficheiros; sem documento identi |  |
| `IT-T5-032` | T5 | HTML_ARTICLE_DISCOVERY | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | https://dsa3.unipg.it/home/news/news-studenti?view=elenco |
| `IT-T5-033` | T5 | HTML_ARTICLE_DISCOVERY | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | https://distal.unibo.it/it/notizie/vii-giornata-internazionale-di-sensibilizzazione-sulle- |
| `IT-T5-034` | T5 | HTML_ARTICLE_DISCOVERY | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | https://georgofili.it/elenco-atti-georgofili |
| `IT-T5-035` | T5 | HTML_ARTICLE_DISCOVERY | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | https://georgofili.it/elenco-atti-georgofili |
| `IT-T5-036` | T5 | HTML_ARTICLE_DISCOVERY | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | https://georgofili.it/elenco-atti-georgofili |
| `IT-T6-001` | T6 | JSON_API | NO | NOT_RUN | NO | nao | NAO_AVALIADA | NO | NO | `NOT_WIRED` o executor devolve LEGADO/CATALOG — a unidade de colheita de T6 nao es |  |
| `IT-T6-002` | T6 | JSON_API | NO | NOT_RUN | NO | nao | NAO_AVALIADA | NO | NO | `NOT_WIRED` o executor devolve LEGADO/CATALOG — a unidade de colheita de T6 nao es |  |
| `IT-T6-003` | T6 | JSON_API | NO | NOT_RUN | NO | nao | NAO_AVALIADA | NO | NO | `NOT_WIRED` o executor devolve LEGADO/CATALOG — a unidade de colheita de T6 nao es |  |
| `IT-T6-004` | T6 | JSON_API | NO | NOT_RUN | NO | nao | NAO_AVALIADA | NO | NO | `NOT_WIRED` o executor devolve LEGADO/CATALOG — a unidade de colheita de T6 nao es |  |
| `IT-T6-005` | T6 | JSON_API | NO | NOT_RUN | NO | nao | NAO_AVALIADA | NO | NO | `NOT_WIRED` o executor devolve LEGADO/CATALOG — a unidade de colheita de T6 nao es |  |
| `IT-T6-006` | T6 | JSON_API | NO | NOT_RUN | NO | nao | NAO_AVALIADA | NO | NO | `NOT_WIRED` o executor devolve LEGADO/CATALOG — a unidade de colheita de T6 nao es |  |
| `IT-T6-007` | T6 | JSON_API | NO | NOT_RUN | NO | nao | NAO_AVALIADA | NO | NO | `NOT_WIRED` o executor devolve LEGADO/CATALOG — a unidade de colheita de T6 nao es |  |
| `IT-T6-008` | T6 | JSON_API | NO | NOT_RUN | NO | nao | NAO_AVALIADA | NO | NO | `NOT_WIRED` o executor devolve LEGADO/CATALOG — a unidade de colheita de T6 nao es |  |
| `IT-T6-009` | T6 | JSON_API | NO | NOT_RUN | NO | nao | NAO_AVALIADA | NO | NO | `NOT_WIRED` o executor devolve LEGADO/CATALOG — a unidade de colheita de T6 nao es |  |
| `IT-T6-010` | T6 | JSON_API | NO | NOT_RUN | NO | nao | NAO_AVALIADA | NO | NO | `NOT_WIRED` o executor devolve LEGADO/CATALOG — a unidade de colheita de T6 nao es |  |
| `IT-T6-011` | T6 | JSON_API | NO | NOT_RUN | NO | nao | NAO_AVALIADA | NO | NO | `NOT_WIRED` o executor devolve LEGADO/CATALOG — a unidade de colheita de T6 nao es |  |
| `IT-T6-012` | T6 | JSON_API | NO | NOT_RUN | NO | nao | NAO_AVALIADA | NO | NO | `NOT_WIRED` o executor devolve LEGADO/CATALOG — a unidade de colheita de T6 nao es |  |
| `IT-T6-013` | T6 | JSON_API | NO | NOT_RUN | NO | nao | NAO_AVALIADA | NO | NO | `NOT_WIRED` o executor devolve LEGADO/CATALOG — a unidade de colheita de T6 nao es |  |
| `IT-T6-014` | T6 | JSON_API | NO | NOT_RUN | NO | nao | NAO_AVALIADA | NO | NO | `NOT_WIRED` o executor devolve LEGADO/CATALOG — a unidade de colheita de T6 nao es |  |
| `IT-T6-015` | T6 | JSON_API | NO | NOT_RUN | NO | nao | NAO_AVALIADA | NO | NO | `NOT_WIRED` o executor devolve LEGADO/CATALOG — a unidade de colheita de T6 nao es |  |
| `IT-T6-016` | T6 | JSON_API | NO | NOT_RUN | NO | nao | NAO_AVALIADA | NO | NO | `NOT_WIRED` o executor devolve LEGADO/CATALOG — a unidade de colheita de T6 nao es |  |
| `IT-T6-017` | T6 | JSON_API | NO | NOT_RUN | NO | nao | NAO_AVALIADA | NO | NO | `NOT_WIRED` o executor devolve LEGADO/CATALOG — a unidade de colheita de T6 nao es |  |
| `IT-T6-018` | T6 | JSON_API | NO | NOT_RUN | NO | nao | NAO_AVALIADA | NO | NO | `NOT_WIRED` o executor devolve LEGADO/CATALOG — a unidade de colheita de T6 nao es |  |
| `IT-T6-019` | T6 | JSON_API | NO | NOT_RUN | NO | nao | NAO_AVALIADA | NO | NO | `NOT_WIRED` o executor devolve LEGADO/CATALOG — a unidade de colheita de T6 nao es |  |
| `IT-T6-020` | T6 | JSON_API | NO | NOT_RUN | NO | nao | NAO_AVALIADA | NO | NO | `NOT_WIRED` o executor devolve LEGADO/CATALOG — a unidade de colheita de T6 nao es |  |
| `IT-T6-021` | T6 | JSON_API | NO | NOT_RUN | NO | nao | NAO_AVALIADA | NO | NO | `NOT_WIRED` o executor devolve LEGADO/CATALOG — a unidade de colheita de T6 nao es |  |
| `IT-T6-022` | T6 | JSON_API | NO | NOT_RUN | NO | nao | NAO_AVALIADA | NO | NO | `NOT_WIRED` o executor devolve LEGADO/CATALOG — a unidade de colheita de T6 nao es |  |
| `IT-T6-023` | T6 | JSON_API | NO | NOT_RUN | NO | nao | NAO_AVALIADA | NO | NO | `NOT_WIRED` o executor devolve LEGADO/CATALOG — a unidade de colheita de T6 nao es |  |
| `IT-T6-024` | T6 | JSON_API | NO | NOT_RUN | NO | nao | NAO_AVALIADA | NO | NO | `NOT_WIRED` o executor devolve LEGADO/CATALOG — a unidade de colheita de T6 nao es |  |
| `IT-T6-025` | T6 | JSON_API | NO | NOT_RUN | NO | nao | NAO_AVALIADA | NO | NO | `NOT_WIRED` o executor devolve LEGADO/CATALOG — a unidade de colheita de T6 nao es |  |
| `IT-T6-026` | T6 | JSON_API | NO | NOT_RUN | NO | nao | NAO_AVALIADA | NO | NO | `NOT_WIRED` o executor devolve LEGADO/CATALOG — a unidade de colheita de T6 nao es |  |
| `IT-T6-027` | T6 | JSON_API | NO | NOT_RUN | NO | nao | NAO_AVALIADA | NO | NO | `NOT_WIRED` o executor devolve LEGADO/CATALOG — a unidade de colheita de T6 nao es |  |
| `IT-T6-028` | T6 | JSON_API | NO | NOT_RUN | NO | nao | NAO_AVALIADA | NO | NO | `NOT_WIRED` o executor devolve LEGADO/CATALOG — a unidade de colheita de T6 nao es |  |
| `IT-T6-029` | T6 | JSON_API | NO | NOT_RUN | NO | nao | NAO_AVALIADA | NO | NO | `NOT_WIRED` o executor devolve LEGADO/CATALOG — a unidade de colheita de T6 nao es |  |
| `IT-T6-030` | T6 | JSON_API | NO | NOT_RUN | NO | nao | NAO_AVALIADA | NO | NO | `NOT_WIRED` o executor devolve LEGADO/CATALOG — a unidade de colheita de T6 nao es |  |
| `IT-T6-031` | T6 | JSON_API | NO | NOT_RUN | NO | nao | NAO_AVALIADA | NO | NO | `NOT_WIRED` o executor devolve LEGADO/CATALOG — a unidade de colheita de T6 nao es |  |
| `IT-T6-032` | T6 | JSON_API | NO | NOT_RUN | NO | nao | NAO_AVALIADA | NO | NO | `NOT_WIRED` o executor devolve LEGADO/CATALOG — a unidade de colheita de T6 nao es |  |
| `IT-T6-033` | T6 | JSON_API | NO | NOT_RUN | NO | nao | NAO_AVALIADA | NO | NO | `NOT_WIRED` o executor devolve LEGADO/CATALOG — a unidade de colheita de T6 nao es |  |
| `IT-T6-034` | T6 | JSON_API | NO | NOT_RUN | NO | nao | NAO_AVALIADA | NO | NO | `NOT_WIRED` o executor devolve LEGADO/CATALOG — a unidade de colheita de T6 nao es |  |
| `IT-T6-035` | T6 | JSON_API | NO | NOT_RUN | NO | nao | NAO_AVALIADA | NO | NO | `NOT_WIRED` o executor devolve LEGADO/CATALOG — a unidade de colheita de T6 nao es |  |
| `IT-T6-036` | T6 | JSON_API | NO | NOT_RUN | NO | nao | NAO_AVALIADA | NO | NO | `NOT_WIRED` o executor devolve LEGADO/CATALOG — a unidade de colheita de T6 nao es |  |
| `IT-T7-002` | T7 | DATASET_ODS | NO | NOT_RUN | NO | nao | NAO_AVALIADA | NO | NO | `CAPABILITY_MISSING` nenhum coletor desta casa percorre a forma DATASET_ODS para esta fonte |  |
| `IT-T7-013` | T7 | HTML_ARTICLE_DISCOVERY | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | https://www.conaf.it/consiglio-dellordine-nazionale/ |
| `IT-T7-014` | T7 | PDF_DISCOVERY_PAGE | YES | FAIL | NO | nao | NAO_AVALIADA | NO | NO | `CANARY_FAILED` entrada inacessivel: curl: (35) Recv failure: Connection was reset
 |  |
| `IT-T9-001` | T9 | ROUTE_UNKNOWN | NO | NOT_RUN | NO | nao | NAO_AVALIADA | NO | NO | `ROUTE_UNKNOWN` ficha sem URL |  |
| `IT-T9-002` | T9 | BROWSER_PUBLIC | NO | NOT_RUN | NO | nao | NAO_AVALIADA | NO | NO | `BROWSER_REQUIRED` regras/italy_contracts.mjs / manifesto — servidor recusa cliente sem n |  |
| `IT-T9-008` | T9 | BROWSER_PUBLIC | NO | NOT_RUN | NO | nao | NAO_AVALIADA | NO | NO | `BROWSER_REQUIRED` regras/italy_contracts.mjs IT-T9-008 — BROWSER_DISCOVERED_ROUTE, WAF_O |  |
| `IT-T9-009` | T9 | HTML_ARTICLE_DISCOVERY | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | https://www.cifo.it/newsroom/cifo-a-tomato-world-2026-innovazione-e-strategie-nutrizionali |
| `IT-T9-010` | T9 | PDF_DISCOVERY_PAGE | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | https://www.serbios.it/docs/documents/codice-etico.pdf |
| `IT-T9-011` | T9 | HTML_ARTICLE_DISCOVERY | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | https://www.koppert.it/notizia/trasformare-la-protezione-delle-colture-con-gli-acari-preda |
| `IT-T9-012` | T9 | PDF_DISCOVERY_PAGE | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | https://www.biogard.it/wp-content/uploads/2026/08/Report-Curve_30.07.26.pdf |
| `IT-T9-013` | T9 | PDF_DISCOVERY_PAGE | YES | PASS | YES | nao | NAO_AVALIADA | YES | NO | — | https://certisbelchim.co.uk/pdf/GENERAL%20TERMS%20AND%20CONDITIONS%20OF%20SALE.pdf |

