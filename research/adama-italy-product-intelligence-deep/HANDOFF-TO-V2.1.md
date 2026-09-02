# HANDOFF PARA O V2.1 — ADAMA ITALY PRODUCT INTELLIGENCE

**Data:** 2026-09-02 · **Pacote:** `research/adama-italy-product-intelligence-deep/`

Este pacote **não** entra no portal e **não** cria oportunidade. Ele entrega camadas factuais e
relações candidatas. Quem decide se um cruzamento vira oportunidade é o V2.1.

---
## Contagem exigida
```
NEW_COMMERCIAL_PRODUCT_ENTITIES        = 0
NEW_REGULATORY_PRODUCT_ENTITIES        = 602
IDENTITY_MATCHES                       = 49
IDENTITY_CONFLICTS                     = 2
OFFICIAL_LABELS_READ                   = 0
LABEL_USE_PAIRS                        = 0
HERBICIDE_USE_PAIRS                    = 0
FUNGICIDE_USE_PAIRS                    = 0
INSECTICIDE_USE_PAIRS                  = 0
CROPS_COVERED                          = 0
TARGETS_COVERED                        = 0
ACTIVE_INGREDIENTS                     = 169
HRAC_CLASSIFIED                        = 35
FRAC_CLASSIFIED                        = 0
IRAC_CLASSIFIED                        = 22
COMMERCIAL_PRODUCTS_WITH_OTHER_HOLDER  = 7
EXPIRIES_WITHIN_180_DAYS               = 64
EXPIRY_STATE_CONFLICTS                 = 8
EU_REGULATORY_FUTURE_SIGNALS           = 0
QA_SAMPLE_SIZE                         = 36
QA_PASS                                = 35
QA_CORRECTED                           = 0
QA_REJECTED                            = 0
MEASURED_ERROR_RATE                    = 0.0
CLIENT_SAFE_PRODUCT_RECORDS            = 35
CLIENT_SAFE_LABEL_RELATIONSHIPS        = 0
SYNTHETIC_RECORDS                      = 0
EXPECTED (SYNTHETIC_RECORDS)           = 0
```

## Os zeros são medidos, não esquecidos

| Zero | Motivo exato |
|---|---|
| `OFFICIAL_LABELS_READ = 0` | nenhum PDF de etichetta e alcancavel deste ambiente; sem rotulo lido nao ha par cultura x alvo defensavel — mas **51 etichette estão inventariadas** com URL e sha256 |
| `LABEL_USE_PAIRS = 0` | idem: sem rótulo lido não há par defensável |
| `FRAC_CLASSIFIED = 0` | PDF oficial baixado mas a extracao perde digitos ('M 04' -> 'M 0'); nao se publica o defeito do extrator como fonte |
| `EU_REGULATORY_FUTURE_SIGNALS = 0` | EU Pesticides Database: 307 -> sorry.ec.europa.eu em toda rota de dados |
| `CLIENT_SAFE_LABEL_RELATIONSHIPS = 0` | consequência dos anteriores |
| `NEW_COMMERCIAL_PRODUCT_ENTITIES = 0` | os 51 ja existiam no censo de 2026-08-30; esta missao nao recoletou, reconciliou |

## O que o V2.1 pode usar imediatamente

- **`PRODUCT-IDENTITY-MAP.json`** — 612 entidades com `PRODUCT_ID` estável, aliases separados, `JOIN_METHOD` e `JOIN_CONFIDENCE` em cada linha.
- **`PRODUCTS-REGULATORY.json`** — os três estados separados: administrativo, validade formal e comercializável (`UNKNOWN`).
- **`EXPIRY-CLUSTERS.json`** — 58 agrupamentos data × substância ativa, com sobreposição de catálogo, **sem chamar vencimento de risco**.
- **`ACTIVE-INGREDIENTS.json`** — 169 ingredientes, cada componente de mistura separado, com HRAC/IRAC e URL de origem.
- **`LABEL-MANIFEST.json`** — 141 documentos com URL, tipo e sha256: a lista de compras exata para a próxima captura local.

## O que desbloqueia a próxima camada

1. **Rodar a extração de etichetta na máquina local** (a que tem janela gráfica e o acervo em `C:\eame-sintonia-it`) — ou expor `SUPABASE_URL`/`SUPABASE_SECRET_KEY`, já que os 195 brutos estão preservados e com hash conferido no bucket.
2. **Ler a EU Pesticides Database de navegador com janela**, do mesmo jeito que o catálogo ADAMA foi lido.
3. **Reler o FRAC Code List com extrator que preserve dígitos** — o PDF já está identificado e a URL registrada.

As três são a mesma classe de bloqueio: **fonte existe, rota daqui não**. Nenhuma é fonte inexistente.
