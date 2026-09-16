# PRIMEIRA COLETA CONTROLADA — ITÁLIA V1

> **Este ficheiro é o PLANO OPERACIONAL de UMA execução.** Não é Bíblia, não é
> registo de fontes, não é contrato. A lei da coleta vive em
> [`BIBLIA-CANONICA-DA-COLETA.md`](../../BIBLIA-CANONICA-DA-COLETA.md); o registo
> canónico de fontes é [`docs/fontes/ATLAS-DE-FONTES-EAME.md`](../fontes/ATLAS-DE-FONTES-EAME.md);
> os contratos executáveis vivem em [`regras/italy_contracts.mjs`](../../regras/italy_contracts.mjs).
> Este documento **aponta** para eles e não os repete.

```
MISSÃO QUE O PRODUZIU   C-IT-FIRST-CONTROLLED-COLLECTION-PLAN-V1
BRANCH                  claude/it-collection-sala-v1
MEDIDO EM               2026-09-16
HEAD MEDIDO             9d6dcbbd08210b0c463b1cb25222edc4f8d45d9b
COLETAS EXECUTADAS      ZERO — esta missão mediu e planeou; não adquiriu nada
```

---

## 1 · OBJETIVO

Levar **um conjunto pequeno de fontes italianas já registadas** pela estrada
inteira da Collection, **numa aquisição real pela rede**, e provar onde cada uma
chega:

```
SOURCE → REQUEST → ORCHESTRATOR → COLLECTOR → RUN → RAW OBSERVATION
       → STORAGE OBJECT → DERIVED → STRUCTURED → ADMISSION → SALA DE ESPERA
```

`READY` significa **chegou à Sala de Espera**. Não significa que a Intelligence
processou. A Intelligence está **fora** desta execução.

### A pergunta que ainda não foi respondida, e que é a razão deste piloto

Duas provas existem, e **nenhuma das duas faz as duas coisas ao mesmo tempo**:

| prova | adquiriu da rede? | chegou à Sala? |
|---|:-:|:-:|
| `provas/a_fonte_t4_italiana_atravessa.py` (15/09) | **SIM** | **NÃO** — para em `DERIVED = NOT_APPLICABLE`, porque `text/csv` não tem derivador |
| `provas/o_material_italiano_chega_a_sala.py` (14/09) | **NÃO** — reprocessou bytes já colhidos | **SIM** — 3 unidades pousaram |

```
AQUISIÇÃO REAL + CHEGADA À SALA, NA MESMA CORRIDA  =  AINDA NÃO ACONTECEU.
```

É isso, e só isso, que a execução seguinte existe para produzir.

---

## 2 · O CENSO DA MÁQUINA — o que existe hoje

Medido no HEAD acima. `MODULE EXISTS ≠ EDGE EXISTS ≠ FLOW EXISTS`.

| elo | dono | implementado | provado | estado |
|---|---|:-:|:-:|---|
| `SOURCE REQUEST` | `pedido/pedido.py` · `pedido/receitas.py` | SIM | SIM | **PROVEN** — o pedido resolve plano e executor |
| `ORCHESTRATOR` | `orquestrador/orquestrador.py` | SIM | SIM | **PROVEN** — cunha `RUN_ID`, assina o recibo, leva à porta |
| `COLLECTOR` | `coleta/italy_executor.py` → `coleta/italy_pilot_collect.mjs` | SIM | SIM | **PROVEN** para 7 fontes italianas |
| `RUN` | `guarda/preservar_coleta.py` · `collection_run` | SIM | SIM | **PROVEN** — `ONE RUN = ONE RUN_ID`, o coletor não cunha |
| `RAW OBSERVATION` | `coleta/ingresso.py` · `raw_asset` | SIM | SIM | **PROVEN** — `RAW_OBSERVATION_ID = raw_asset.id`, sequência do banco |
| `STORAGE OBJECT` | `coleta/ingresso.py::ArmazemLocal` · `storage_object` | SIM | SIM | **PROVEN** — sha256 dos bytes, chave estrangeira para o RAW |
| `DERIVED` | `coleta/derivacao_forward.py` | SIM | **PARCIAL** | abre **PDF** e **mídia**. Não abre CSV, HTML, ODS, ZIP |
| `STRUCTURED` | `guarda/preservar_documento.py` | SIM | **PARCIAL** | atravessa na classe DOCUMENTAL; a classe PLATAFORMA espera dono |
| `ADMISSION` | `admissao/admissao.py` | SIM | SIM | **PROVEN** — `SIM · NAO · NAO_SEI · NAO_SE_APLICA · ERRO` |
| `SALA DE ESPERA` | `admissao/sala_de_espera.py` | SIM | SIM | **PROVEN** em PostgreSQL; o backend `FICHEIRO` existe e **não é canónico** |

**A costura entre eles** é `coleta/rota_forward_documento.py`, e ela vai até à
Sala: chama `espera.pousar()`, distingue `PASSED` de `REUSED`, e escreve
`NOT_RUN` — nunca `FAIL` — quando a Admissão não diz `SIM`.

```
ADMISSION PASS  ≠  READY PASS.        Só o SIM faz a unidade pousar.
ETAPA REGISTADA ≠  UNIDADE PRODUZIDA. A etapa READY corre sem nenhum READY existir.
```

### O ambiente desta bancada, medido hoje

| | medido | consequência |
|---|---|---|
| egresso | `EGRESS_COUNTRY_CODE = IT` · `EGRESS_GATE = PASS` | pode adquirir das fontes italianas |
| `node` · `curl` · `pdftotext` | v24.18.0 · 8.21.0 · 4.06 | o coletor e o derivador de PDF correm |
| `psql` · `psycopg` · PostgreSQL | **ausentes** | a Sala canónica **não** existe aqui |
| portão da Sala | `SALA_DE_ESPERA=BLOCKED`, sai com **1** | o portão funciona, e fecha — corretamente |

---

## 3 · AS FONTES SELECIONADAS

```
PILOT_SOURCE_COUNT = 6
```

Todas com `SOURCE_ID` no **Atlas** (registo canónico), todas `VERDICT = GREEN`,
todas com contrato executável em `regras/italy_contracts.mjs`, todas com rota
implementada em `coleta/italy_pilot_collect.mjs`, todas gratuitas e sem
autenticação.

| | SOURCE_ID | que capacidade da máquina ela prova |
|---|---|---|
| `PILOT_01` | **IT-T4-001** | que a casa descobre um **nome de ficheiro datado** na página em vez de o adivinhar — e que `DERIVED = NOT_APPLICABLE` não é `FAIL` |
| `PILOT_02` | **IT-T3-002** | a **cadeia inteira até à Sala**, com volta por chave e não por posição de lista — a única que já pousou |
| `PILOT_03` | **IT-T3-008** | que um índice em **JavaScript** vira `DISCOVERY_DEGRADED` declarado, e não um resultado falseado |
| `PILOT_04` | **IT-T3-010** | o **caminho do erro** honesto: `EMPTY_LIST ≠ ZERO_DOCUMENTS`, e 19 `DISCOVERY_FAILED` já registados provam que ela falha de verdade |
| `PILOT_05` | **IT-T2-002** | que **`SOURCE ≠ ENDPOINT`**: uma fonte, 29 endereços, 29 documentos independentes — e que uma zona falhar não contamina as outras |
| `PILOT_06` | **IT-T2-004** | que **`MOVING_WINDOW ≠ NEW_DATASET_EVERY_DAY`**: uma URL fixa com janela móvel, normalizada em observações estação×dia |

### O que foi recusado, e porquê

| fonte | classe | decisão | motivo medido |
|---|---|---|---|
| `IT-T3-005` | HTML oficial | **BLOCKED — não entra** | **não existe no Atlas.** Zero menções. Vive só em `candidatas/ITALY-SOURCE-MASTER-V1.json` com `status = NEW` e `verdict = NAO SEI`. É **candidata**, e §8 proíbe |
| `IT-T1-001` | A · API estatística | **BLOCKED** | idem: no Atlas só aparece numa tabela de «não alcançadas», sem ficha. Sem executor |
| `IT-T5-002` | D · ciência | `GAP_D` | contrato existe; **nenhum executor desta casa a percorre** |
| `IT-T9-008` | F · concorrente/navegador | `GAP_F` | contrato existe; a rota é `BROWSER`, a classe `RC-6 PUBLIC_BROWSER` está `BLOCKED` por robots/termos, e a ADAMA recusa quem não é janela gráfica |
| T10 · mercado | G · mercado | `GAP_G` | **nenhuma** fonte T10 italiana tem contrato nem executor |
| `IT-T2-001` · `IT-T7-002` · `IT-T3-011` | B · C | `NOT_SELECTED` | contrato existe, executor **não**. Entrar exigiria código novo, e isto é um piloto, não uma obra |

```
DECLARAR GAP É MELHOR DO QUE PREENCHER A TABELA.
UMA CLASSE SEM FONTE PRONTA NÃO GANHA UMA FONTE INVENTADA.
```

---

## 4 · A MATRIZ

Campos idênticos em todas as seis, declarados uma vez:

```
TERRITORY suporte     SOURCE_LOCATION = SIM (o publicador é conhecido e nomeado)
                      FACT_LOCATION   = PARCIAL — ver coluna própria
AUTH_REQUIRED         não            COST_EXPECTED        FREE
ACQUISITION_TOOL      coleta/italy_executor.py  →  coleta/italy_pilot_collect.mjs
TOOL_OWNER            a rota do orquestrador                TOOL_PROVEN  SIM
RAW_OBSERVATION_OWNER coleta/ingresso.py                    STORAGE_OWNER  ArmazemLocal
ADMISSION_PATH        admissao/admissao.py                  SALA_PATH  admissao/sala_de_espera.py
CONTRACT_PATH         regras/italy_contracts.mjs
RATE_LIMIT_KNOWN      NÃO SEI — nenhuma das seis declara limite, e nenhum foi medido
```

### PILOT_01 · `IT-T4-001` — Ministero della Salute, prodotti fitosanitari

| campo | valor |
|---|---|
| `SOURCE_OWNER_ENTITY` | Ministero della Salute (Itália) |
| `TERRITORY` · `SOURCE_TYPE` | T4 · registo oficial de autorizações, dados abertos |
| `ENDPOINT` | `dati.salute.gov.it/it/dataset/fitosanitari/` → `…/opendata/PROD_FTS_6_<AAAAMMDD>.csv` |
| `ROUTE_TYPE` · `DISCOVERY` · `RETRIEVAL` | `PREDICTABLE_ROUTE` · o nome datado é **lido na página** · `GET` no CSV |
| `EXPECTED_ARTIFACT` | CSV `;`, ≥ 3 MB (medido: 4.594.254 bytes) |
| `NATIVE_DOCUMENT_ID` | **SIM** — `MINSALUTE:FTS6:{AAAAMMDD}`; por linha, `num_registrazione` |
| `DERIVATION_EXPECTED` | **`NOT_APPLICABLE`** — nenhum derivador abre `text/csv` |
| `STRUCTURED` · `ADMISSION` · `SALA` | não chamado · `NAO_SEI` (item sem texto) · **0** |
| `FACT_LOCATION` | PAÍS. A sede da empresa é `SOURCE_LOCATION`, **nunca** local do facto |
| `PUBLICATION_TIME` · `FACT_TIME` | SIM (data no nome do ficheiro) · **UNKNOWN** para o ficheiro; por linha há datas de registo |
| `KNOWN_DEBT` | duas ferramentas declaradas (ver §7 `CW-05`); só se alcança por `alvo=T3` (ver `BG-05`) |
| `KNOWN_RISK` | o regex de descoberta depende do HTML da página, não do dado |
| `PILOT_STATUS` | **READY** |

### PILOT_02 · `IT-T3-002` — Regione Campania, bollettini fitosanitari

| campo | valor |
|---|---|
| `SOURCE_OWNER_ENTITY` | Regione Campania — Servizio Fitosanitario Regionale |
| `TERRITORY` · `SOURCE_TYPE` | T3 · boletim fitossanitário regional |
| `ENDPOINT` | `…/bollettini_{ANO}/pdf/{PROV}-{DD}-{MM}.pdf` (`AV BN CE NA SA`) |
| `ROUTE_TYPE` · `DISCOVERY` · `RETRIEVAL` | `PREDICTABLE_ROUTE` · página do ano lista por província · `GET` no PDF |
| `EXPECTED_ARTIFACT` | PDF ≥ 100 KB, assinatura `%PDF` conferida **antes** de qualquer parse |
| `NATIVE_DOCUMENT_ID` | **SIM** — `CAMPANIA:{PROV}:{DD-MM-ANO}` |
| `DERIVATION_EXPECTED` | **texto de PDF** → `STRUCTURED` → `ADMISSION = SIM` → **Sala** |
| `FACT_LOCATION` | província (`SA`) — declarada pelo documento |
| `PUBLICATION_TIME` · `FACT_TIME` | SIM (data no nome) · **UNKNOWN** — o boletim não data a observação de campo |
| `HISTORICAL_OR_FORWARD` | `HISTORICAL` · `ARCHIVE_REQUIREMENT = NORMAL` · `7D` provado por 14 edições |
| `KNOWN_RISK` | 404 em data sem edição é **facto da fonte**, não falha nossa |
| `PILOT_STATUS` | **READY** |

### PILOT_03 · `IT-T3-008` — ARIF Puglia, notiziario agrometeorologico

| campo | valor |
|---|---|
| `SOURCE_OWNER_ENTITY` | ARIF Puglia — Agenzia Regionale per le Attività Irrigue e Forestali |
| `ENDPOINT` | `…/settimanale/{ANO}/Notiziario_Agrometeorologico_N{N}_{DD-MM-AAAA}.pdf` |
| `ROUTE_TYPE` · `DISCOVERY` | `PREDICTABLE_ROUTE` · **o índice é renderizado por JavaScript**; o `curl` não vê os links |
| o que a casa faz | cai para a rota previsível do contrato e **marca `DISCOVERY_DEGRADED`** no livro |
| `EXPECTED_ARTIFACT` | PDF ≥ 1 MB |
| `NATIVE_DOCUMENT_ID` | **SIM** — `ARIF:SETTIMANALE:{ANO}:N{N}` |
| `DERIVATION_EXPECTED` | texto de PDF → `STRUCTURED` → `ADMISSION` → Sala |
| `FACT_LOCATION` | região (Puglia) |
| `PUBLICATION_TIME` · `FACT_TIME` | SIM · **UNKNOWN** |
| `KNOWN_RISK` | se a rota previsível não achar edição em 10 dias, a corrida diz **porquê** e falha fechada |
| `PILOT_STATUS` | **READY** |

### PILOT_04 · `IT-T3-010` — A.P.OL. Lecce, Bollettino Mosca delle Olive

| campo | valor |
|---|---|
| `SOURCE_OWNER_ENTITY` | A.P.OL. — Associazione tra Produttori Olivicoli, Lecce |
| `ENDPOINT` | `apol.it` → link `Bollettino_Mosca*.pdf` descoberto no índice |
| `ROUTE_TYPE` · `DISCOVERY` | **`DISCOVERED_ROUTE`** · o índice é lido e os links extraídos |
| `EXPECTED_ARTIFACT` | PDF ≥ 300 KB |
| `NATIVE_DOCUMENT_ID` | **SIM** — `APOL:{ANO}:N{N}:{COMPRENSORIO}`, extraído do **texto** do PDF |
| `DERIVATION_EXPECTED` | texto de PDF → `STRUCTURED` → `ADMISSION` → Sala |
| `FACT_LOCATION` | comprensório (extraído do documento) |
| `PUBLICATION_TIME` · `FACT_TIME` | SIM · **UNKNOWN** — o período é de validade, não de observação |
| `KNOWN_RISK` | **a mais frágil das seis**: 19 de 21 observações no livro são `DISCOVERY_FAILED` |
| porque fica | é exatamente por isso que fica — ela é o `ERROR_PATH` que não precisa de ser simulado |
| `PILOT_STATUS` | **READY** |

### PILOT_05 · `IT-T2-002` — ARPAV Veneto, bollettini agrometeo zonais

| campo | valor |
|---|---|
| `SOURCE_OWNER_ENTITY` | ARPAV — Agenzia Regionale per la Prevenzione e Protezione Ambientale del Veneto |
| `ENDPOINT` | `…/32zone/agro_{NN}.pdf` — **29 endereços publicados** (17, 18 e 19 devolvem 404 consistente: facto da fonte) |
| `ROUTE_TYPE` · `DISCOVERY` | `BROWSER_DISCOVERED_ROUTE` para **descobrir**; `HTTP` simples para **baixar** |
| `EXPECTED_ARTIFACT` | PDF ≥ 200 KB por zona |
| `NATIVE_DOCUMENT_ID` | **SIM** — `ARPAV:Z{NN}:{CreationDate do PDF}` |
| `DERIVATION_EXPECTED` | texto de PDF → `STRUCTURED` → `ADMISSION` → Sala |
| `FACT_LOCATION` | zona agrometeorológica (`Z01`..`Z32`) |
| `PUBLICATION_TIME` · `FACT_TIME` | SIM (`CreationDate`) · **UNKNOWN** — o PDF expõe a data de geração, não a do facto medido |
| `UPDATE_BEHAVIOR` | **`SOBRESCRITA`** · `FORWARD_ONLY` · `ARCHIVE_REQUIREMENT = CRITICAL` |
| `KNOWN_DEBT` | as 29 zonas **só** se alcançam por `italy_recurrent_collect.mjs`; `italy_executor.py` corre as 4 do piloto (ver `CW-09`) |
| `PILOT_STATUS` | **READY** — com 4 zonas pela rota canónica |

### PILOT_06 · `IT-T2-004` — SIAS Sicilia, precipitazione giornaliera

| campo | valor |
|---|---|
| `SOURCE_OWNER_ENTITY` | SIAS — Servizio Informativo Agrometeorologico Siciliano |
| `ENDPOINT` | `sias.regione.sicilia.it/NHEOWL0530_00.html` (site em *frameset*) |
| `ROUTE_TYPE` · `DISCOVERY` · `RETRIEVAL` | `STATIC_ROUTE` · caminho de frames documentado no contrato · `GET` na página |
| `EXPECTED_ARTIFACT` | HTML ≥ 30 KB, tabela estação × dia |
| `NATIVE_DOCUMENT_ID` | **SIM** — `SIAS:{TABLE}:WINDOW_END_{ISO}` |
| `DERIVATION_EXPECTED` | **NÃO SEI.** O coletor **normaliza** em observações (`ESTAÇÃO|DIA|VARIÁVEL`), mas nenhum derivador da casa abre `text/html`. Ver `RISCO_03` |
| `FACT_LOCATION` | **estação meteorológica** — o grão mais fino das seis |
| `PUBLICATION_TIME` · `FACT_TIME` | janela declarada · **por linha** — cada célula tem a sua própria data |
| `UPDATE_BEHAVIOR` | **`SOBRESCRITA`** — janela móvel de 11 dias na mesma URL · `ARCHIVE_REQUIREMENT = CRITICAL` |
| `PILOT_STATUS` | **READY** |

---

## 5 · COBERTURA

### Por classe de aquisição

| | classe | coberta | por quem |
|---|---|:-:|---|
| A | oficial estruturada / dataset | **SIM** | `IT-T4-001` |
| B | oficial HTML | **SIM** | `IT-T2-004` |
| C | PDF / boletim | **SIM** | `IT-T3-002` · `IT-T3-008` · `IT-T3-010` · `IT-T2-002` |
| D | ciência / repositório | **GAP** | contrato existe (`IT-T5-002`), executor não |
| E | clima / dado temporal | **SIM** | `IT-T2-002` · `IT-T2-004` |
| F | concorrência / navegador | **GAP** | rota `BROWSER` bloqueada por robots/termos |
| G | mercado | **GAP** | nem contrato nem executor |

Quatro fontes na classe C parecem muitas, e não são: cada uma percorre um
`ROUTE_TYPE` diferente — previsível, previsível-com-queda-declarada, descoberta,
e multi-endereço.

```
MESMO FORMATO ≠ MESMA ROTA.
```

### Por elo da estrada

| elo | testado? | por quem |
|---|:-:|---|
| `REQUEST` | **SIM** | seis pedidos, `alvo=T2` e `alvo=T3`, filtro `fonte` |
| `ORCHESTRATOR` | **SIM** | cunha o `RUN_ID`, escolhe o executor, assina o recibo |
| `MULTIPLE_COLLECTOR_TYPES` | **NÃO** | **um** executor para as seis. Ver `RISCO_01` |
| `RUN` | **SIM** | `collection_run` por corrida |
| `RAW_OBSERVATION` | **SIM** | uma linha em `raw_asset` por observação |
| `STORAGE` | **SIM** | `storage_object` com sha256 e bytes |
| `DERIVED` | **SIM** | PDF nas quatro de classe C; `NOT_APPLICABLE` em `IT-T4-001` |
| `STRUCTURED` | **SIM** | pelas quatro de classe C |
| `ADMISSION` | **SIM** | `SIM` esperado nas de PDF; `NAO_SEI` em `IT-T4-001` |
| `SALA` | **SIM** | pelas de PDF, **se** `BG-01` e `BG-02` estiverem fechados |

---

## 6 · O QUE A EXECUÇÃO SEGUINTE TEM DE PROVAR

Nada aqui foi simulado. Cada linha diz **quem** produzirá a prova.

| # | comportamento | quem o produz | como se lê |
|---:|---|---|---|
| 1 | primeira coleta | as seis | `BASELINE_DOCUMENT` ou `NEW_DOCUMENT` no livro |
| 2 | retry na **mesma** corrida | qualquer falha de transporte | `retries > 1` na observação, **mesmo `RUN_ID`** |
| 3 | nova corrida da mesma fonte | correr `IT-T3-002` duas vezes | dois `RUN_ID`, **um** `DOCUMENT_ID` |
| 4 | conteúdo igual | `IT-T3-002` na segunda corrida | `SEEN_AGAIN` + `RAW_OBJECT_CREATED = false` + `RAW_PATH` preenchido |
| 5 | conteúdo alterado | `IT-T2-002` ou `IT-T2-004` (ambas `SOBRESCRITA`) | `DOCUMENT_CHANGED_IN_PLACE` + `DOCUMENT_VERSION_ID = v2_…` |
| 6 | erro de transporte | `IT-T3-010` (19 falhas históricas) | `HEALTH_STATE = FAILED` · `OBSERVATION_RESULT = DISCOVERY_FAILED` |
| 7 | erro de parser | `IT-T3-010` (identidade vem do texto do PDF) | `PARSE_ERROR` preenchido **com o RAW já guardado** |
| 8 | `UNKNOWN` | `IT-T4-001` | `ADMISSION = NAO_SEI`, e a Sala fica vazia sem isso ser falha |
| 9 | reuso de storage object | `IT-T2-002`, duas zonas, dois dias | `guardarRaw` devolve o sítio sem reescrever |
| 10 | crash / restart | matar a corrida entre `RAW` e `DERIVED` | `etapa_da_corrida` mostra onde parou; o RAW sobrevive |
| 11 | admissão aceita | as quatro de PDF | `SIM` no livro de decisões |
| 12 | admissão rejeita | **NÃO PLANEADO** — nenhuma das seis produz `NAO` hoje | declarado como gap desta execução, e não fabricado |
| 13 | material chega à Sala | `IT-T3-002` · `IT-T3-008` · `IT-T3-010` | `select count(*) from public.sala_de_espera where run_id=…` **e** depois `espera.ler()` **noutro processo** |

```
PERGUNTAR À TABELA NÃO É PERGUNTAR AO DONO.
```

---

## 7 · OS PORTÕES

### MUST_FIX_BEFORE_PILOT

#### `BG-01` · O workflow canónico não tem fase italiana

| | |
|---|---|
| `PROBLEM` | `.github/workflows/sintonia-scrap.yml` é o único sítio onde o portão da Sala e o portão do egresso correm **antes** da aquisição. As suas fases são todas sociais; **nenhuma** despacha o orquestrador para a Itália. O ramo de omissão foi retirado: fase não nomeada sai com `exit 2` |
| `OWNER` | `.github/workflows/sintonia-scrap.yml` |
| `WHY_BLOCKS` | sem fase, ou a execução corre à mão **sem os dois portões**, ou não corre |
| `EVIDENCE` | as 30 opções de `inputs.fase`; o `case` do passo 6; `provas/o_egresso_antes_da_aquisicao.py` §D |
| `MINIMUM_FIX` | uma fase (ex.: `italia-documento`) que chame `orquestrador/orquestrador.py` com `--filtro pais=IT` e `--filtro fonte=`. A condição dos passos `5b`/`5c` é **lista de exclusão** — a fase nova nasce com os dois portões ligados, sem se mexer neles |
| `TEST_REQUIRED` | `tests/test_preflight_de_egresso.py` (já reprova se a fase nova nascer sem portão) |

#### `BG-02` · Não há ambiente com egresso italiano **e** Sala canónica não-produção

| | |
|---|---|
| `PROBLEM` | três ambientes, e nenhum serve: **(a)** esta bancada tem `EGRESS=IT` e **nenhum** PostgreSQL; **(b)** o `ubuntu-latest` tem Postgres descartável e egresso **US** — e o portão bloqueia, corretamente; **(c)** o runner Windows auto-hospedado tem a Sala por `SUPABASE_DB_URL`, que é **produção** |
| `OWNER` | quem provisiona o runner + `docs/operacao/PREFLIGHT-LIVE-COLLECTION-V1.md` |
| `WHY_BLOCKS` | sem Sala canónica não há `READY`; com Sala de produção a execução deixa de ser controlada |
| `EVIDENCE` | `psql: command not found` e `psycopg` ausente nesta máquina; `SALA_DE_ESPERA=BLOCKED` (sai com 1); `LIVE_DB_REACHABLE = NO` e `MIGRATION_029/030_LIVE = UNKNOWN` no pré-voo; **32** migrations em Git, das quais **031** e **032** (a Sala durável) não foram sequer medidas em produção |
| `MINIMUM_FIX` | PostgreSQL descartável **no runner com egresso italiano**, com `SINTONIA_SALA_BACKEND=POSTGRES` e `SINTONIA_SALA_DSN` a apontar para ele — ao **nível do job**, nunca do passo. **Ou** decisão explícita do dono de escrever na Supabase de produção |
| `TEST_REQUIRED` | `admissao/sala_de_espera.py --portao` a sair com **0**, e `motor/cadeia_canonica.sh` a aplicar 001..032 |

> `MIGRATION EM GIT NÃO É MIGRATION APLICADA.`
> `UM PORTÃO QUE MEDE UM AMBIENTE E DEIXA PASSAR PARA OUTRO NÃO MEDIU NADA.`

#### `BG-03` · O teste de contrato do coletor italiano não corre no Windows

| | |
|---|---|
| `PROBLEM` | `tests/test_italia_na_porta_canonica.py` monta `import … from "C:/…/italy_pilot_collect.mjs"`. O Node lê `c:` como **protocolo** e levanta `ERR_UNSUPPORTED_ESM_URL_SCHEME`. **14 falhas, uma causa só** |
| `OWNER` | `tests/test_italia_na_porta_canonica.py::_driver` |
| `WHY_BLOCKS` | o runner com egresso italiano **é Windows**. A prova que guarda a porta da Itália é exatamente a que não corre lá |
| `EVIDENCE` | `Received protocol 'c:'`; 14/22 vermelhas nesta bancada, **0** no CI Linux |
| `MINIMUM_FIX` | `pathToFileURL(...).href` — a **mesma** conversão que o próprio coletor já usa na linha 543 pela **mesma** razão |
| `TEST_REQUIRED` | o próprio, a passar no Windows |

#### `BG-04` · Duas provas do caminho até à Sala chamam o `psql` com a DSN à frente

| | |
|---|---|
| `PROBLEM` | `provas/o_material_italiano_chega_a_sala.py:96` e `provas/o_portao_da_big_collection.py:120` passam a URL **antes** das opções. O `getopt` do Windows não permuta: o `psql` liga-se, **não corre a migration** e sai com **zero** |
| `OWNER` | os dois ficheiros |
| `WHY_BLOCKS` | no runner Windows, a preparação do banco **não acontece** e o silêncio parece sucesso |
| `EVIDENCE` | **40** chamadas com DSN à frente contra **15** corretas. `admissao/sala_de_espera.py` **já está certo**; `provas/a_fonte_t4_italiana_atravessa.py` também |
| `MINIMUM_FIX` | mover as opções para antes da URL, como nos outros dois |
| `TEST_REQUIRED` | a prova a correr no Windows e a **reprovar** quando o banco está vazio |

#### `BG-05` · `IT-T4-001` só se alcança pedindo `alvo=T3`

| | |
|---|---|
| `PROBLEM` | `IT-T4-001` é **T4**; o único executor que a alcança está registado em `pedido/receitas.py` só em **T2** e **T3**. E pedir `alvo=T4` com `filtros={"fonte":"IT-T4-001"}` abre o `regulatorio-eu`, que colhe **`EU-T4-001`** — outra fonte, outro país — porque ele declara `argumentos_de_filtros: ["celex"]` e o filtro `fonte` é **descartado em silêncio** |
| `OWNER` | `pedido/receitas.py` |
| `WHY_BLOCKS` | o pedido certo devolve a fonte errada sem avisar ninguém |
| `EVIDENCE` | `system-map/data/fonte-t4-italiana.observado.json` → `ALVO_DO_PEDIDO: "T3"` |
| `MINIMUM_FIX` | **o mínimo é gritar, não reencaminhar**: um filtro que um executor não conhece tem de aparecer no recibo |
| `TEST_REQUIRED` | um pedido com filtro desconhecido a deixar rasto |

#### `BG-06` · O coletor corre **sete** fontes por omissão, e uma não está no registo

| | |
|---|---|
| `PROBLEM` | `PILOT_SOURCES` em `italy_pilot_collect.mjs` tem 7 entradas; `IT-T3-005` **não está no Atlas**. Sem `--fonte=`, uma corrida colhe uma **candidata** |
| `OWNER` | o procedimento da execução |
| `WHY_BLOCKS` | §8 proíbe candidata no piloto, e o padrão do coletor inclui uma |
| `EVIDENCE` | zero menções de `IT-T3-005` no Atlas; `status=NEW`, `verdict=NAO SEI` no master de candidatas; **6** observações já no livro |
| `MINIMUM_FIX` | a execução **nomeia as seis**, uma a uma. Não se confia na memória de quem dispara |
| `TEST_REQUIRED` | conferir que o `RUN_ID` da execução não produz nenhuma observação de `IT-T3-005` |

### CAN_WAIT_AFTER_PILOT

| id | dívida | porque não bloqueia |
|---|---|---|
| `CW-01` | nenhum derivador abre CSV | é **capacidade ausente**, não etapa partida. Construí-lo é decisão de arquitetura: o contrato de `IT-T4-001` declara **duas** granularidades (o ficheiro e a linha), e escolher uma é projeto |
| `CW-02` | `ITEM_COUNT_RAW = "NAO SEI"` no recibo do orquestrador | impede **ler** o que aconteceu, não executar nem preservar (`G-TEL-01`) |
| `CW-03` | o plano conta a mesma fonte **duas vezes** | `receitas._fontes()` soma Atlas + master de candidatas. Cinco fontes de T3 IT aparecem **ao mesmo tempo** em «com caminho escrito» e em «NÃO SEI como se chega». Confunde quem lê; não desvia byte nenhum |
| `CW-04` | dois registos de contrato | o Atlas-ladder lê `docs/operacao/CONTRATOS-DAS-FONTES-EAME.md` (**5** fontes); os contratos executáveis vivem em `regras/italy_contracts.mjs` (**13**). Doze contratos reais são invisíveis ao registo canónico |
| `CW-05` | duas ferramentas para `IT-T4-001` | o contrato canónico diz `provas/chain.py run it-prothioconazole`; quem atravessa a estrada é `coleta/italy_executor.py`. **O dono canónico da aquisição é o executor**; `chain.py` é prova de recorrência, e vive em `provas/` |
| `CW-06` | chave de dono divergente | decidido em 16/09 (know-how §127-5b.2): o SINTONIA **não tem** `SOURCE_OWNER_STABLE_ID`. O facto é a **entidade**. Medidas divergências de chave de catálogo: `IT-T2-004` (`IT-OWN-005` vs `IT-OWN-SIAS`), `IT-T2-001` (`002` vs `ARPAE`), `IT-T3-008` (`010` vs `ARIF`). **A entidade é a mesma nas três** |
| `CW-07` | `G-ENV-02` — envelopes acumulam sem fim | inerte, e a pasta está no `.gitignore` |
| `CW-08` | `G-RUN-02` — a corrida diz `concluida` antes do fim da estrada | a verdade está em `etapa_da_corrida`. Confunde quem opera; não corrompe dado |
| `CW-09` | as 29 zonas ARPAV só pelo corredor agendado | `italy_executor.py` não passa `arpavZonas`. Quatro zonas provam a capacidade; 29 é operação |

---

## 8 · OWNER DEBT

| SOURCE_ID | `OWNER_ENTITY_PROVEN` | `OWNER_KEY_DEBT` |
|---|:-:|:-:|
| `IT-T4-001` | SIM — Ministero della Salute | NÃO (o Atlas não usa chave) |
| `IT-T3-002` | SIM — Regione Campania, Servizio Fitosanitario Regionale | NÃO |
| `IT-T3-008` | SIM — ARIF Puglia | **SIM** — `IT-OWN-010` (Atlas) vs `IT-OWN-ARIF` (contrato) |
| `IT-T3-010` | SIM — A.P.OL. Lecce | NÃO |
| `IT-T2-002` | SIM — ARPAV Veneto | NÃO (o Atlas não usa chave) |
| `IT-T2-004` | SIM — SIAS Sicília | **SIM** — `IT-OWN-005` (Atlas) vs `IT-OWN-SIAS` (contrato) |

**Nenhuma bloqueia.** Nos dois casos a **entidade** é a mesma e está provada; o
que diverge é a chave do catálogo candidato — e essa chave **não é identidade**.
`PILOT_BLOCKER = nenhum`.

---

## 9 · CUSTO

```
COST_MEASUREMENT_AVAILABLE = SIM, para este piloto
```

As seis são `EXPECTED_COST_MODEL = FREE`. O orquestrador escreve
`COST_USD = 0` quando o executor declara `custo: "gratuito"` — não é
arredondamento, é a rota ser gratuita. Nenhuma passa por Apify, navegador pago
ou API com chave.

⚠️ **O que não se mede:** `ITEM_COUNT_RAW` sai `"NAO SEI"` (ver `CW-02`), e
**nenhuma das seis declara limite de taxa** — `RATE_LIMIT_KNOWN = NÃO SEI` nas
seis. O custo de **rede** está medido só para `IT-T2-002`: ~12,8 MB por execução
das 32 tentativas.

```
NÃO SE INVENTA CUSTO. ZERO PORQUE A ROTA É GRATUITA ≠ ZERO POR OMISSÃO.
```

---

## 10 · RISCOS

| id | risco | o que fazer |
|---|---|---|
| `RISCO_01` | **um só tipo de coletor.** As seis passam pelo mesmo executor. O piloto prova seis *rotas*, e **uma** implementação de coletor | declarado. Um segundo tipo exige executor novo, e isso é obra, não piloto |
| `RISCO_02` | **`ADMISSION = NAO` não é provado.** Nenhuma das seis o produz hoje | declarado como gap. Fabricar um item para o forçar seria fabricar a prova |
| `RISCO_03` | `IT-T2-004` é HTML, e **nenhum derivador abre `text/html`**. Ela pode parar em `DERIVED = NOT_APPLICABLE` como o CSV | é resultado válido e **esperado**, não falha. Se parar, escreve-se onde parou |
| `RISCO_04` | correr o coletor contra a árvore viva **engorda o livro versionado** e reprova guardas congeladas de outras missões (medido: 175 → 182) | apontar `ITALY_OPS_ROOT` para um `mkdtemp()` **e** atribuir `italy_executor.OPS_ROOT` — o módulo lê o `os.environ` no import, tarde demais |
| `RISCO_05` | `IT-T2-002` e `IT-T2-004` são `FORWARD_ONLY` com `ARCHIVE_REQUIREMENT = CRITICAL`: **o que não for preservado hoje desaparece** | não adiar a execução destas duas |
| `RISCO_06` | o egresso italiano desta bancada vem de VPN. `VPN_LOCATION ≠ SOURCE_LOCATION ≠ FACT_LOCATION` | o portão prova o **ambiente**, nunca a geografia do dado |

---

## 11 · CRITÉRIOS DE PASS DA EXECUÇÃO SEGUINTE

`FIRST_CONTROLLED_COLLECTION = PASS` só se, tudo na **mesma** corrida:

1. `EGRESS_GATE = PASS` e `SALA_DE_ESPERA` a sair com **0**, **antes** de qualquer aquisição;
2. aquisição **real** pela rede — sem `forcarBuf`, sem reprocessamento;
3. uma linha em `collection_run` por corrida, com o `RUN_ID` que o orquestrador cunhou;
4. uma linha em `raw_asset` por observação, com `media_type` declarado;
5. `storage_object` com `sha256` e bytes, ligado ao RAW por chave estrangeira;
6. cada etapa com estado **nomeado** — `PASS`, `NOT_APPLICABLE` ou `FAIL`, nunca ausência;
7. pelo menos **uma** unidade a pousar na Sala, contada por `select` **e** relida por `espera.ler()` **noutro processo**;
8. `IT-T4-001` a parar em `DERIVED = NOT_APPLICABLE` — se chegar à Sala sem ninguém instalar um derivador, é **FAIL**;
9. zero observações de `IT-T3-005`;
10. o livro versionado **inalterado**: 175 observações antes, 175 depois;
11. cada `UNKNOWN` com o motivo escrito ao lado.

```
SKIP ≠ PASS.  «Ran 0 tests» ≠ PASS.  SALA VAZIA COM NOT_RUN ≠ BURACO.
```

---

## 12 · HARD STOP

A execução seguinte **não pode**:

- coletar fora das seis nomeadas;
- promover candidata, criar `SOURCE_ID` ou inventar `DOCUMENT_ID`;
- correr Big Collection;
- escrever na Sala de produção sem autorização explícita do dono;
- consertar os gates que este plano nomeia sem os nomear na entrega;
- usar `SHA256` como `DOCUMENT_ID`, `source location` como `fact location`, ou
  `publication time` como `fact time`;
- deixar a Intelligence tocar em nada.

---

## 13 · ONDE ESTÃO OS NÚMEROS

| afirmação | onde se confere |
|---|---|
| fichas e vereditos das seis | `docs/fontes/ATLAS-DE-FONTES-EAME.md` |
| os 13 contratos executáveis | `regras/italy_contracts.mjs` |
| o livro de observações (175) e as corridas (28) | `data/collection-ledger/italy/` |
| a estrada com aquisição real, parada em `DERIVED` | `system-map/data/fonte-t4-italiana.observado.json` |
| a estrada até à Sala, por reprocessamento | `system-map/data/material-italiano-na-sala.observado.json` |
| o estado dos portões da Collection V1 | `docs/operacao/COLLECTION-V1-CLOSE-GATES.md` |
| o estado LIVE das migrations | `docs/operacao/PREFLIGHT-LIVE-COLLECTION-V1.md` |
| a leitura derivada das fontes | `system-map/data/sources.generated.json` |
