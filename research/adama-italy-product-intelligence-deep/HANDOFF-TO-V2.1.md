# HANDOFF PARA O V2.1 — ADAMA ITALY PRODUCT INTELLIGENCE

**Rodada 2 · 2026-09-02** — fechar os três gaps medidos. Dois fecharam, um não.

Este pacote **não** entra no portal e **não** cria oportunidade.

---
## Contagem exigida
```
LABEL_DOCUMENTS_INVENTORIED            = 141
LABEL_DOCUMENTS_RECOVERED              = 0
CURRENT_LABELS_VERIFIED                = 0
LABEL_USE_PAIRS                        = 0
HERBICIDE_USE_PAIRS                    = 0
FUNGICIDE_USE_PAIRS                    = 0
INSECTICIDE_USE_PAIRS                  = 0
CROPS_COVERED                          = 0
TARGETS_COVERED                        = 0
FRAC_CLASSIFIED                        = 29
FRAC_UNKNOWN                           = 93
EU_ACTIVE_INGREDIENTS_CHECKED          = 122
EU_STATES_RESOLVED                     = 60
EU_STATES_UNKNOWN                      = 59
PRODUCT_EU_RELATIONSHIPS               = 60
QA_SAMPLE_SIZE                         = 48
QA_PASS                                = 46
QA_CORRECTED                           = 1
QA_REJECTED                            = 0
MEASURED_ERROR_RATE                    = 0.0
CLIENT_SAFE_LABEL_USE_PAIRS            = 0
SYNTHETIC_RECORDS                      = 0
BLOCKERS_REMAINING                     = 3
READY_FOR_V2.1_INGEST                  = YES_FOR_REGULATORY_AND_MOA_LAYERS / NO_FOR_LABEL_USE_LAYER
```

---
## O que mudou desde a rodada 1

| Camada | Antes | Agora |
|---|---:|---:|
| FRAC classificados | 0 | **29** |
| Estados EU resolvidos | 0 | **60** |
| Relações substância → produto IT → catálogo | 0 | **60** |
| Substâncias ativas reais | 169 (falsas) | **122** |
| Pares de uso de rótulo | 0 | 0 |

### A correção que importa mais que os gaps

O baseline separava mistura por `+`. O registro italiano separa por `|` e **nunca** por `+` —
em 148 dos 602 registros. Resultado: **nenhuma mistura tinha sido separada**, e cada uma virava um
MoA artificial — o oposto exato da regra declarada. Corrigido. As 169 "substâncias" eram 122 reais
mais 47 strings de mistura coladas. O QA anterior não pegou porque não olhava isso; agora olha.

---
## Aprovações EU expirando até 2028, com produto no catálogo comercial

Fato, não risco. Expiração de aprovação **não é** retirada, restrição nem perda comercial,
e estado EU **não é** comercialização na Itália.

| Expira | Substância ativa | Registros IT | Produtos no catálogo |
|---|---|---:|---|
| 2026-09-30 | FLUDIOXONIL | 1 | Seedron® |
| 2026-09-30 | PHENMEDIPHAM | 12 | Contatto® 320 |
| 2026-10-31 | METAZACHLOR | 2 | Sultan® |
| 2026-10-31 | PIRIMICARB | 8 | Pirimor® 50 |
| 2026-11-30 | METAMITRON | 18 | Brevis®, Goltix®, Goltix® TOP |
| 2026-11-30 | FLONICAMID (IKI-220) | 2 | Apyza® WG |
| 2026-11-30 | SULCOTRIONE | 3 | Sulcotrek® |
| 2027-01-15 | PENDIMETHALIN | 18 | Activus® ME, Stopper P |
| 2027-01-31 | BUPIRIMATE | 6 | Nimrod® 250 EW |
| 2027-01-31 | TAU-FLUVALINATE | 12 | Mavrik® Smart |
| 2027-02-15 | FLUROXYPYR | 3 | Tomigan |
| 2027-02-28 | QUIZALOFOP-P-ETHYL | 9 | Highcard®, Leopard® 5 EC, Max-Ace® Rice Cropping Solution |
| 2027-02-28 | PROPAQUIZAFOP | 5 | Agil® |
| 2027-03-31 | PROTHIOCONAZOLE | 5 | Avastel®, Maganic®, Maxentis® |
| 2027-03-31 | BIFENOX | 11 | Sonavio®, Valley |
| 2027-03-31 | NICOSULFURON | 8 | Nicogan® V.O. |
| 2027-05-31 | AZOXYSTROBIN | 7 | Maxentis® |
| 2027-05-31 | CHLORANTRANILIPROLE | 1 | Cosayr® 200 SC |
| 2027-05-31 | TEFLUTHRIN | 2 | Schermo® 0.5 G |
| 2027-05-31 | TERBUTHYLAZINE | 19 | Sulcotrek® |
| 2027-06-30 | IMAZAMOX | 4 | Davai®, FullPage® Rice Cropping Solution |
| 2027-08-31 | DIFLUFENICAN | 8 | Stopper P |
| 2027-10-31 | FLUXAPYROXAD | 1 | Avastel® |
| 2027-11-30 | FLUAZINAM | 3 | Banjo® |
| 2027-12-15 | CLETHODIM | 1 | Arrodim® |

---
## Bloqueios que restam

| Bloqueio | Evidência | O que desbloqueia |
|---|---|---|
| conteudo das etichette | adama.com/media 403; fitosanitari.salute.gov.it gateway 502 no CONNECT; sem credencial do bucket; nada no Git nem no disco | maquina com janela grafica, ou credencial de execucao do bucket |
| RENEWAL_UNDER_REVIEW, DRAFT_NON_RENEWAL, ARTICLE_21_REVIEW, SCoPAFF, EFSA | EU Pesticides Database: 307 -> sorry.ec.europa.eu com e sem cabecalho de navegador | navegador com janela |
| FRAC de 93 substancias | nao tem linha na tabela FRAC 2026 — em boa parte herbicida e inseticida, que nao pertencem a ela | nada a fazer: HRAC e IRAC ja cobrem o que e deles |

---
## Pronto para ingestão?

**`YES` para as camadas regulatória e de MoA.** `PRODUCT-IDENTITY-MAP`, `PRODUCTS-REGULATORY`,
`ACTIVE-INGREDIENTS`, `FRAC-CLASSIFICATIONS`, `EU-ACTIVE-SUBSTANCE-STATUS`, `REGULATORY-FUTURE-DEEP`
e `EXPIRY-CLUSTERS` têm origem, método e confiança em cada linha.

**`NO` para a camada de uso de rótulo.** Ela não existe, e não deve ser simulada. Sete rotas de
recuperação foram tentadas e registradas com o HTTP de cada uma em `LABEL-MANIFEST.json`.
