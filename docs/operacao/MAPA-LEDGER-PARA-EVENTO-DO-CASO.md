# MAPA — DO LEDGER DA COLETA ATÉ O EVENTO DA LINHA DO TEMPO DO CASO

**Dono da coleta:** @sintonia-scrap-engineer · **Dono do evento/ORIGEM:** @sintonia-intelligence-owner
**Contrato do Casco:** `CASE_ID` · `DOCUMENT_ID` · `ORIGEM` · `EVIDENCE_REQUEST_ID` · `SOURCE_CONTRACT_ID` · as três datas
**Base medida:** `data/collection-ledger/italy/observations.ndjson` (registos reais) · `coleta/italy_pilot_collect.mjs`

Este documento existe para que a tela, a Intelligence e a coleta **não inventem três nomes para o mesmo dado**.
A regra é: o campo **nasce onde pode ser provado**, e viaja com o nome que já tem.

---

## 1 · O que o ledger JÁ entrega (medido, não proposto)

Exemplo real de um registo (`IT-T3-005`, primeira captura):

```json
{"RUN_ID":"PILOT_RUN_20260907153737_4c34b3",
 "SOURCE_ID":"IT-T3-005",
 "SOURCE_URL":"https://www.terretruria.it/monitoraggio",
 "DOCUMENT_ID":"TERRETRURIA:31-08-2026:06-09-2026",
 "DOCUMENT_VERSION_ID":"v1_2e488a8232ba",
 "RAW_SHA256":"2e488a8232ba980fa46f7dbca28478fdac0e30e4440d9675823c5f3479d2d122",
 "BYTES":274247, "MIME_ASSINATURA":"HTML",
 "SOURCE_DATE":"31-08-2026 a 06-09-2026", "SOURCE_DATE_ISO":"2026-09-06",
 "FACT_TIME":"por ponto — cada ponto traz sua propria data de campionamento",
 "CAPTURED_AT":"2026-09-07T15:37:40.362Z",
 "COLLECTION_RUN_STARTED_AT":"2026-09-07T15:37:37.137Z",
 "OBSERVATION_RESULT":"BASELINE_DOCUMENT", "HEALTH_STATE":"HEALTHY",
 "RAW_OBJECT_CREATED":true,
 "RAW_PATH":"data/collection-store/italy/IT-T3-005/.../monitoraggio.html",
 "RAW_PRESERVED_BEFORE_PARSE":true}
```

## 2 · Campo a campo até o evento da linha do tempo

| evento do Casco | vem de | estado | regra |
|---|---|---|---|
| `CASE_ID` | **não existe no ledger** | **A CRIAR (Intelligence)** | pertence ao caso, não à captura. A coleta não pode adivinhar a que caso um documento serve. |
| `DOCUMENT_ID` | `DOCUMENT_ID` | **EXISTE** quando a fonte prova | `TERRETRURIA:31-08-2026:06-09-2026`, `ARPAV:Z01:<CreationDate>`, `MINSALUTE:FTS6:<AAAAMMDD>`… Sem prova, o registo é `IDENTITY_FAILED` e **não há DOCUMENT_ID**. Nunca fabricar com SHA, URL ou filename. |
| `ORIGEM` | **derivado** | **A DERIVAR (Intelligence)** | `EVIDENCE_REQUEST_ID` presente e ligado ⇒ `BUSCA_ATIVA`. Ausente ⇒ `ACHADO_POR_ACASO_ANTES_DO_CASE_ID`. Sem `EVIDENCE_REQUEST_ID` não há como dizer "Investigado". |
| `EVIDENCE_REQUEST_ID` | **não existe no ledger** | **A CRIAR (rota sob demanda, §b bloqueada)** | nasce no `EVIDENCE_REQUEST` do caso; só a rota sob demanda o grava no evento de captura. |
| `SOURCE_CONTRACT_ID` | **não existe por evento** | **A CRIAR** | hoje o ledger traz `SOURCE_ID` (= `IT-T3-005`) + `SOURCE_CONTRACT_VERSION` (= `"italy-contracts-v1"`, do run). É **versão do contrato**, não ID por evento. |
| `DATA_FONTE` | `SOURCE_DATE_ISO` (ISO) · `SOURCE_DATE` (texto legível) | **EXISTE** | data que a própria fonte declara para aquele documento. |
| `DATA_FATO` | `FACT_TIME` | **EXISTE, e frequentemente `UNKNOWN`** | ⚠️ **NUNCA copiar de `SOURCE_DATE`.** Medido: na ARPAV o valor é `"UNKNOWN — o PDF nao expoe a data do fato medido, so a de geracao"`. `FACT_TIME ≠ PUBLICATION_TIME`. |
| `DATA_CAPTURA` | `CAPTURED_AT` | **EXISTE** | quando a nossa coleta tocou a fonte. Não é data da fonte nem do fato. |

## 3 · Campos de prova que o evento devia carregar (e o ledger já tem)

Não são exigidos pelo Casco, mas sem eles a linha do tempo não é re-verificável:

| campo | para que serve |
|---|---|
| `RAW_SHA256` | prova de **bytes**. **SHA256 identifica bytes, não documento.** |
| `DOCUMENT_VERSION_ID` | qual versão do mesmo documento foi vista (`v1_<sha12>`), distinguindo `SEEN_AGAIN` de `DOCUMENT_CHANGED_IN_PLACE`. |
| `RAW_PATH` + `RAW_PRESERVED_BEFORE_PARSE` | o RAW foi guardado **antes** de interpretar. |
| `OBSERVATION_RESULT` | `BASELINE_DOCUMENT` / `NEW_DOCUMENT` / `SEEN_AGAIN` / `DOCUMENT_CHANGED_IN_PLACE` / `SKIPPED_OUT_OF_COHORT`. |
| `HEALTH_STATE` | `HEALTHY` / `DEGRADED` / `FAILED` / `NOT_MEASURED` — saúde da captura ≠ veredito da fonte. |
| `SOURCE_URL` / `SOURCE_ID` | de onde veio. `SOURCE_LOCATION ≠ FACT_LOCATION`. |

## 4 · Leis que este mapa não pode deixar quebrar

```
RAW_SHA256      != DOCUMENT_ID       bytes nao sao identidade semantica
SOURCE_DATE     != FACT_TIME         publicacao nao e o momento do fato
SOURCE_LOCATION != FACT_LOCATION     sede nao e o lugar do fato
CAPTURED_AT     != SOURCE_DATE       quando colhemos nao e quando a fonte publicou
ORIGEM por acaso != ORIGEM investigada
```

## 5 · Estado dos 5 documentos que já existem

Entram como `ACHADO_POR_ACASO_ANTES_DO_CASE_ID` — foram capturados **antes** de haver `CASE_ID`/`EVIDENCE_REQUEST_ID`.
O selo *Investigado pelo Sintonia* só aparece quando existir, no evento, a cadeia completa:
`CASE_ID` + `EVIDENCE_REQUEST_ID` + `SOURCE_CONTRACT_ID` + captura + `DOCUMENT_ID`.

## 6 · Nota operacional (por ordem do coordenador)

O Teste 1 pode correr a partir da worktree `scrap-ondemand-route-v1`, desde que grave num **ledger identificado como teste**.
Nada deste mapa altera o ledger de produção nem a coleta contínua, que sai de `origin/servico-20260923-0923`.
