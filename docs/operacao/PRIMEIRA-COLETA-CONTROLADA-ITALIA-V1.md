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

> ⚠️ **FECHADOS EM 2026-09-16 — e a execução aconteceu.** Ver **§7-B · O FECHO**
> e **§10-C · EXECUÇÃO REAL**. O texto original de cada portão fica por baixo,
> datado: é o retrato do problema que justificou o conserto.

### 7-B · O FECHO DOS SEIS, MEDIDO

| gate | antes | correção | prova | final |
|---|---|---|---|---|
| `BG-01` | nenhuma fase italiana no workflow | fase `italia-documento`: bancada 5a-IT antes dos portões 5b/5c, ramo que deriva o alvo do SOURCE_ID e chama **só** o orquestrador, teardown 9z-IT `always()` | `tests/test_fase_italiana_no_workflow` (15) | **PASS** |
| `BG-02` | sem ambiente com egresso IT + Sala não-produção | bancada = runner `eame-sintonia-local` + PostgreSQL 16.4 portátil; cluster nasce e morre com o job | migrations 31/31 `PASS` · `SALA_DE_ESPERA=PASS` (saída 0) · `EGRESS=IT PASS` na mesma máquina e sessão | **PASS** |
| `BG-03` | `import "C:/…"` lido como protocolo — 14+10 vermelhos | `pathToFileURL` nos dois drivers, o mesmo conserto do próprio coletor | `test_italia_na_porta_canonica` 22/22 · `test_alvo_estruturado` 17→1 (a 1 é pré-existente) · provado com espaço e acento | **PASS** |
| `BG-04` | DSN antes das opções: `rc=0` sem executar, leitura e escrita | DSN por último em **43 sítios** de 30 ficheiros + Sala (447/486) + `cadeia_canonica.sh` (6) — **e** dado por stdin em UTF-8 explícito (ver §7-C) | guarda AST `tests/test_psql_argv` + prova observada: `_consultar`→`42`, `_executar`→escreveu e releu, controle negativo confirmado | **PASS** |
| `BG-05` | `T4+fonte=IT-T4-001` colhia `EU-T4-001`, filtro morria calado | resolver promove quem consome os filtros declarados; entrada T4 do `italia-recorrente`; portão `FILTRO_NAO_CONSUMIDO` antes da rede | `tests/test_o_pedido_nao_mente` (14) — e a corrida **real** de T4 colheu `MINSALUTE:FTS6:20260914` | **PASS** |
| `BG-06` | corrida sem fontes nomeadas colhia as 7, com a candidata dentro | sem conjunto por omissão: `FONTES_AUSENTES` no runtime, `--fonte` obrigatório na CLI; `PILOT_SOURCES` fica como capacidade | `tests/test_fontes_explicitas_no_coletor` (8) | **PASS** |

### 7-C · O SÉTIMO DEFEITO, QUE NENHUM PLANO TINHA VISTO

Fechar o BG-04 revelou um irmão dele: **texto acentuado em argv atravessa a
conversão ANSI do Windows e chega em CP1252 ao banco UTF-8** (o `ã` vira
`0xE3`, a aspa curva vira `0x92`) — e `text=True` sem `encoding` no
`subprocess` faz o mesmo estrago no stdin. O canário italiano rebentou
exactamente aí, no STRUCTURED, com o texto do boletim da Campânia.

```
TEXTO ACENTUADO NÃO VIAJA EM ARGV NO WINDOWS.
DADO VIAJA POR STDIN, DECLARADO UTF-8 DOS DOIS LADOS.
```

Corrigido em: `coleta/coleta_checkpoint.py::Banco.executa` ·
`admissao/sala_de_espera.py::_consultar/_executar` ·
`provas/preservar_coleta_no_postgres.py::_psql/aplicar` ·
`provas/a_sala_sobrevive_ao_processo.py::_psql` · o bootstrap de
`motor/cadeia_canonica.sh` (heredoc em vez de `-c`). E a trava do backend
FICHEIRO da Sala ganhou o `msvcrt` que a admissão já tinha (`fcntl` não
existe no Windows).

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

> ⚠️ **REVISTO EM 2026-09-16 — a parte do AMBIENTE está fechada.** A premissa
> abaixo era falsa por falta de procura: o runner italiano é **esta bancada**, e
> o PostgreSQL 16.4 portátil já estava no disco, fora do repositório. Foi
> arrancado, ligado, consultado e destruído na mesma sessão em que o portão do
> egresso deu `PASS`. Ver **§10-B · BANCADA DE EXECUÇÃO**.
>
> O que sobra nesta bancada **não é ambiente, é código**, e chama-se `BG-04`.
> O texto original fica por baixo, datado, porque apagar a premissa apagaria a
> razão de se ter ido medir.

| | |
|---|---|
| `PROBLEM` | três ambientes, e nenhum serve: **(a)** esta bancada tem `EGRESS=IT` e **nenhum** PostgreSQL; **(b)** o `ubuntu-latest` tem Postgres descartável e egresso **US** — e o portão bloqueia, corretamente; **(c)** o runner Windows auto-hospedado tem a Sala por `SUPABASE_DB_URL`, que é **produção** |
| `OWNER` | quem provisiona o runner + `docs/operacao/PREFLIGHT-LIVE-COLLECTION-V1.md` |
| `WHY_BLOCKS` | sem Sala canónica não há `READY`; com Sala de produção a execução deixa de ser controlada |
| `EVIDENCE` | `psql: command not found` e `psycopg` ausente nesta máquina; `SALA_DE_ESPERA=BLOCKED` (sai com 1); `LIVE_DB_REACHABLE = NO` e `MIGRATION_029/030_LIVE = UNKNOWN` no pré-voo; **32** migrations em Git, das quais **031** e **032** (a Sala durável) não foram sequer medidas em produção |
| `MINIMUM_FIX` | PostgreSQL descartável **no runner com egresso italiano**, com `SINTONIA_SALA_BACKEND=POSTGRES` e `SINTONIA_SALA_DSN` a apontar para ele — ao **nível do job**, nunca do passo. **Ou** decisão explícita do dono de escrever na Supabase de produção |
| `TEST_REQUIRED` | `admissao/sala_de_espera.py --portao` a sair com **0**, e `motor/cadeia_canonica.sh` a aplicar 001..032 |
| ⚠️ **e o caminho Windows está bloqueado DUAS vezes** | pôr Postgres no runner Windows **não chega**: `BG-04` diz que a própria dona da Sala não fala com ele nesse sistema. Os dois fecham-se juntos, ou não se fecha nenhum |

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

#### `BG-04` · A **dona da Sala** chama o `psql` com a DSN antes do `-c` e do `-f`

| | |
|---|---|
| `PROBLEM` | `admissao/sala_de_espera.py` passa `self.url` **antes** de `-c` (linha 447, leitura) e **antes** de `-f` (linha 486, escrita). O `getopt` do Windows **não permuta**: parado o primeiro posicional, `-c` e `-f` deixam de ser opções. A Sala canónica **não lê e não escreve** no Windows |
| `OWNER` | `admissao/sala_de_espera.py` — e depois as provas |
| `WHY_BLOCKS` | é o dono do `READY`. Sem ele, no runner que tem o egresso italiano, `pousar()` não pousa |
| `EVIDENCE` | medido por AST, comparando a **posição** da DSN com a de `-c`/`-f` na chamada inteira: **38 erradas contra 3 certas**. Entre as 38: as duas da Sala, `provas/o_material_italiano_chega_a_sala.py` (73 e 96), `o_portao_da_big_collection.py:120`, `a_rota_m2_atravessa.py:175`, `a_unidade_pousa_na_espera.py:89`, `a_sala_sobrevive_ao_processo.py:84`, `mutacao_da_sala_duravel.py` (198 e 201) e `guarda/portas_live.py:115`. **Toda prova da Sala está na lista.** As 3 certas são `coleta/coleta_checkpoint.py:116` e as duas de `provas/a_fonte_t4_italiana_atravessa.py` |
| como falha | **não é sempre igual, e não se finge que é.** Sobrando um posicional, o `psql` aceita-o como utilizador e ignora o resto; sobrando dois, reclama. Há um caso **medido** (15/09) em que o aplicador de migrations disse OK e o banco ficou com **zero tabelas**. Em nenhum dos casos faz o que diz |
| `MINIMUM_FIX` | opções primeiro, DSN no fim — como em `coleta/coleta_checkpoint.py`, que já foi consertado pela mesma razão |
| `TEST_REQUIRED` | uma guarda que meça a **posição** da DSN na lista inteira. ⚠️ Ler só o início da linha dá a resposta errada: foi assim que esta medição já saiu invertida uma vez |

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

## 10-B · BANCADA DE EXECUÇÃO

> Medido em **2026-09-16**, missão `C-IT-PILOT-ENVIRONMENT-GATE-V1`, HEAD `774e1e6d`.
> Esta secção responde a **uma** pergunta: em que máquina corre a primeira coleta
> controlada. Não corrige portão nenhum.

```
PILOT_ENVIRONMENT_DECISION = OPTION_A
SELECTED_PILOT_ENVIRONMENT = runner auto-hospedado `eame-sintonia-local`
                             (+ `-local-2`), com PostgreSQL 16.4 portátil
PRODUCTION_TOUCHED         = NO
```

### O achado que decide

O `BG-02` dizia que **nenhum** ambiente tinha egresso italiano e Sala não-produção
ao mesmo tempo. A medição de hoje mostra que a premissa estava errada por um
detalhe que ninguém tinha ido ver:

> **O runner italiano é esta bancada.** `SINTONIA-EAME-LOCAL` e
> `SINTONIA-EAME-LOCAL-2` não são máquinas remotas — são dois processos de runner
> **nesta máquina**, ligados ao repositório `eame-sintonia`, com as etiquetas
> `eame-sintonia-local` e `eame-sintonia-local-2` que o `sintonia-scrap.yml` pede.

E o PostgreSQL que faltava **também já cá estava**, fora do repositório, em
`C:\Users\London1\orca\pgtmp\pgsql` — binários portáteis 16.4, sem instalação,
sem serviço e sem administrador.

```
EGRESSO IT  e  POSTGRES DESCARTÁVEL  ESTÃO NA MESMA MÁQUINA.
E ISSO FOI PROVADO NA MESMA SESSÃO, NÃO INFERIDO DE DUAS.
```

### Os ambientes medidos

| | `ENV_A` · runner italiano | `ENV_B` · GitHub hosted | `ENV_C` · Supabase produção |
|---|---|---|---|
| `OS` · `ARCH` | Windows 10.0.22000 · AMD64 | Ubuntu · x64 | — (serviço) |
| `RUNNER_TYPE` | self-hosted, **processo à mão** (não é serviço) | hosted, efémero | — |
| `EGRESS_COUNTRY` | **IT** | **NÃO É IT** | — |
| `EGRESS_PROOF` | `superficie/rede.py --portao-de-egresso IT` → `PASS`, sai com **0** | `banco-descartavel.yml` **não tem um único passo que ligue VPN** — medido | — |
| `DOCKER_AVAILABLE` | **NÃO** (`docker: command not found`) | sim (serviços de job) | — |
| `WSL_AVAILABLE` | **NÃO** — `wsl.exe` existe como stub; `wsl -l` imprime a ajuda, não há distro | n/a | — |
| `PSQL_AVAILABLE` | **SIM**, portátil, fora do `PATH` | sim | sim |
| `POSTGRES_SERVER_AVAILABLE` | **SIM** — 16.4 portátil | sim, via `services:` | — |
| `PYTHON` · `NODE` · `CURL` · `PDFTOTEXT` | 3.12.10 · v24.18.0 · 8.21.0 · 4.06 | presentes | — |
| `DISK_AVAILABLE` | **271 GB** livres | efémero | — |
| `CAN_RUN_DISPOSABLE_POSTGRES` | **SIM — PROVADO** | SIM | — |
| `CAN_REACH_PRODUCTION` | só com `SUPABASE_DB_URL`, **ausente nesta sessão** | idem | sim |
| `PRODUCTION_ACCESS_REQUIRED` | **NÃO** | NÃO | **SIM** |
| `STATUS` | ✅ **ESCOLHIDO** | ❌ sem egresso italiano, e sem mecanismo para o ter | ⛔ **PROIBIDO como laboratório** |

`ENV_C'` — os runners `LUCIANO` e `LUCIANO-2` correm na mesma máquina mas estão
ligados a **outro repositório** (`portal-sintonia`). Não servem esta missão.

### A prova de infraestrutura (§6), passo a passo

```
DISPOSABLE_POSTGRES_STARTED = YES
    initdb 16.4 · cluster novo e vazio · md5 · UTF8
    fora do repositório: C:\Users\London1\orca\pgtmp\proof-bancada
    pg_ctl start · porta 54329 · a ouvir SÓ em 127.0.0.1

CONNECTION_PROVED = YES
    create database descartavel;          -> ok
    select 1;                             -> 1        rc=0
    select version();                     -> PostgreSQL 16.4, 64-bit

DESTROYED_AFTER_TEST = YES
    pg_ctl stop -m fast  ->  "server stopped"
    pasta apagada · 0 processos postgres · porta 54329 sem LISTENING

PRODUCTION_TOUCHED = NO
    SUPABASE_DB_URL · SUPABASE_URL · SUPABASE_SERVICE_ROLE_KEY ·
    SUPABASE_ANON_KEY · SINTONIA_SALA_DSN · SINTONIA_SALA_BACKEND
    = todas AUSENTES nesta sessão. Nenhuma ligação foi tentada.

NENHUMA migration do SINTONIA foi aplicada.
A Sala NÃO foi chamada. Nenhuma coleta correu.
```

### E o `BG-04` deixou de ser inferência: foi medido no metal

Aproveitou-se o banco de pé para medir o defeito **sem tocar em código do
SINTONIA**. O mesmo `select 1;` foi pedido de duas maneiras:

| ordem dos argumentos | saída | código de saída |
|---|---|---|
| `psql -X -q -A -t -c 'select 1;' <DSN>` | `1` | **0** |
| `psql <DSN> -X -q -A -t -c 'select 1;'` | seis avisos `extra command-line argument … ignored` | **0** |
| `psql <DSN> -X … -f ficheiro.sql` (o caminho de **escrita** da Sala) | idem | **0** |

```
ELE NÃO FALHA. ELE SAI COM ZERO SEM TER FEITO NADA —
NA LEITURA E NA ESCRITA.
```

E há um segundo desfecho, apanhado por acidente: numa primeira tentativa **sem o
stdin fechado**, o `psql` ficou **preso à espera de senha** — porque com a DSN à
frente o próprio `-w` («nunca perguntes») deixa de ser opção. Num passo de CI
isso não é um erro: é um job pendurado até ao teto de tempo.

> `BG_04_CONTINUES_BLOCKING = YES` — e agora com prova de hardware, não com
> leitura de código.

### O que ainda falta na bancada — pequeno, e escrito

| `REQUIREMENT` | porquê | tamanho |
|---|---|---|
| `REQ-01` · pôr `C:\Users\London1\orca\pgtmp\pgsql\bin` no `PATH` do job, ou usar caminho absoluto | os binários existem e **não estão no `PATH`** | uma linha de `env:` |
| `REQ-02` · o job arranca e destrói o cluster (`initdb` → `pg_ctl start` → … → `pg_ctl stop` → apagar) | `_work` do self-hosted **persiste entre jobs** — medido: pastas de 30/08 e 11/09 ainda lá. Um cluster esquecido vira estado partilhado | um passo de setup e um de `always()` |
| `REQ-03` · `SINTONIA_SALA_BACKEND=POSTGRES` + `SINTONIA_SALA_DSN=postgresql://postgres:descartavel@localhost:54329/descartavel` ao **nível do job** | a trava aceita **qualquer porta**; exige host local e nome na lista curta (`descartavel`, `derivado`, `social`, `objeto`) — lido em `provas/preservar_coleta_no_postgres.py` | duas linhas de `env:` |
| `REQ-04` · alguém tem de deixar o runner ligado | ele **não é serviço**: é um processo iniciado à mão. Estava online e a ouvir hoje às 15:34Z, com 31 jobs no histórico | operacional, não código |

**Nada disto é instalação nova.** Não foi instalado Docker, não foi instalado WSL,
não foi instalado PostgreSQL, não foi mexido no runner e não foi alterada
arquitetura nenhuma.

### Os portões, recalculados contra o ambiente escolhido

| | antes | agora | porquê |
|---|---|---|---|
| `BG-01` workflow sem fase italiana | MUST_FIX | **MUST_FIX** | independente do ambiente. É o único sítio onde os dois portões correm antes de adquirir |
| `BG-02` não há bancada | MUST_FIX | **AMBIENTE RESOLVIDO** | a bancada existe, está escolhida e foi provada. ⚠️ O que resta nela é `BG-04`, que é **código**, não ambiente |
| `BG-03` `pathToFileURL` no Windows | MUST_FIX | **MUST_FIX, e agora certo** | o ambiente escolhido **é** Windows. Deixou de ser hipótese |
| `BG-04` ordem do `psql` | MUST_FIX | **MUST_FIX, provado no metal** | ver acima: `rc=0` sem executar, leitura e escrita |
| `BG-05` `IT-T4-001` só por `alvo=T3` | MUST_FIX | **MUST_FIX** | independente do ambiente |
| `BG-06` sete fontes por omissão | MUST_FIX | **MUST_FIX** | independente do ambiente |

```
MÁQUINA TEM POSTGRES  ≠  CÓDIGO SABE USAR POSTGRES.
E é exactamente aí que a bancada acaba e o BG-04 começa.
```

### O ambiente proibido

`ENV_C` — Supabase de produção — **não foi usado, não foi tocado e não é
laboratório**. Não foi preciso rejeitá-lo por princípio: `ENV_A` funciona, e por
isso a pergunta de autorização **não chega a ser feita** ao dono.

```
PRODUÇÃO NÃO É LABORATÓRIO.
DESCARTÁVEL -> PROVA -> depois LIVE.
```

### Próximo passo mínimo

Fechar, **por esta ordem**, e só isto:

1. `BG-04` — a ordem dos argumentos do `psql` em `admissao/sala_de_espera.py`
   (447 e 486). Sem isto, a bancada provada não serve para nada;
2. `BG-03` — `pathToFileURL` na prova do coletor italiano;
3. `BG-01` — a fase italiana no `sintonia-scrap.yml`, com `REQ-01..REQ-03`;
4. `BG-05` e `BG-06` — o filtro que se perde em silêncio, e as sete fontes.

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

## 10-C · EXECUÇÃO REAL — 2026-09-16

> A primeira coleta controlada **aconteceu**. Aquisição real pela rede, egresso
> IT medido por corrida, pela porta canónica (Pedido → orquestrador → executor),
> contra PostgreSQL 16.4 descartável nesta máquina. Produção intocada; o livro
> versionado inalterado (mesmo sha, 175 observações). O observado integral vive
> em `system-map/data/primeira-coleta-controlada.observado.json`; o corredor é
> `provas/primeira_coleta_controlada_italia.py`.

```
SOURCE_TO_SALA_REAL_OBSERVED = YES     — pela primeira vez na história do projeto
CANARY (IT-T3-002)           = PASS    — RAW→STORAGE→DERIVED→STRUCTURED→SIM→SALA,
                                         1 linha, relida por OUTRO processo
PILOT_SOURCES_EXECUTED       = 6/6     — cada uma até à SUA verdade
```

| fonte | rede | RAW | DERIVED | STRUCTURED | ADMISSION | SALA | leitura |
|---|:-:|:-:|:-:|:-:|:-:|:-:|---|
| `IT-T4-001` | IT ✓ | 1 csv | `NOT_APPLICABLE` | 0 | `NAO_SEI` | 0 | **como o plano previu** — CSV sem derivador; chegar à Sala seria FAIL |
| `IT-T3-002` | IT ✓ | 1 pdf | 1 | 1 | `SIM` | **1** | o canário — a estrada inteira numa corrida |
| `IT-T3-002` 2ª | IT ✓ | 1 (mesmos bytes) | `reused=1` | 0 novos | `SIM` | **1** | §25: novo RUN, nova observação, **um** storage_object, derivado reutilizado |
| `IT-T3-008` | IT ✓ | 1 pdf 2,7 MB | 1ª corrida: `RAW=FAIL` transiente (`RAW_PERSISTENCE_FAILED`), Sala **0** — é o que a linha dela mostra. 2ª corrida (`…234734`, medida por consulta directa ao banco, fora do corredor): `RAW PASS` · `DERIVED PASS` · **1 na Sala**; a leitura noutro processo **não foi medida** para ela (a bancada morreu antes) | | | | | duas corridas, cada uma com a sua prova e os seus limites — ver a linha própria no observado |
| `IT-T3-010` | IT ✓ | 1 pdf | 1 | 1 | `SIM` | **1** | a fonte das 19 falhas históricas respondeu `HEALTHY` — `APOL:2026:N10:BR-COLLINA` |
| `IT-T2-002` | IT ✓ | 4 zonas pdf | 4 | 4 | `NAO_SE_APLICA` ×4 | 0 | T2 não tem regra de admissão, por decisão registada — verdade, não avaria |
| `IT-T2-004` | IT ✓ | 1 html | `NOT_APPLICABLE` | 0 | `NAO_SEI` | 0 | HTML sem derivador — a paragem declarada |

**Reexecução (§25), medida no banco:** `SAME_BYTES=YES` (sha `d5aa781c…` nas
duas corridas) · `STORAGE_REUSED=YES` (as duas observações apontam para o
storage_object **1**; um único objeto para o sha) · `NEW_RUN=YES` ·
`NEW_OBSERVATION=YES` (raw_asset 1 e 3) · `DOCUMENT_ID_RULE` = nome nativo
(`CAMPANIA:SA:09-09-2026`), nunca o SHA.

**Retry (§26):** `RETRY_PROOF = NOT_OBSERVED` — nenhuma falha de transporte
ocorreu naturalmente, e não se fabrica falha contra fonte real.
**Crash (§27):** `CRASH_RECOVERY = NOT_RUN_WITH_REASON` — sem mecanismo de
injeção seguro nesta janela; fica como dívida antes da Big Collection.
**Custo (§30):** `COST_USD = 0` em todas, escrito pelo orquestrador porque a
rota é declarada gratuita; `ITEM_COUNT` veio preenchido (1 e 4).

**Riscos residuais desta bancada:** spawns de psql sob tempestade de processos
falham intermitentemente no Windows (`rc≠0` com stderr vazio) — o rastro
regista honesto e a corrida seguinte recupera; o teardown `9z-IT` com `|| true`
pode deixar a porta 54329 presa se o `stop` falhar (a corrida seguinte falha
fechada, sem tocar produção).

**Limites desta execução manual, ditos em voz alta:** o corredor foi disparado
à mão, e por isso os portões pré-aquisição do **workflow** não correram por ele
— o egresso foi provado pelo portão canónico na mesma sessão **antes** do
canário, e medido por corrida no ledger; a Sala foi provada por `--portao` +
microprova antes de autorizar. A fase `italia-documento` é quem os corre em
produção de processo. E o corredor aceita qualquer `SOURCE_ID` por argv — a
defesa contra candidata é o BG-06 no coletor mais a disciplina de nomear as
seis; nenhuma candidata entrou (medido no observado). O piloto também escreveu
544 decisões no `LIVRO-DE-DECISOES.json` versionado — **revertidas**, porque
referiam artefactos de um banco descartável já destruído; o livro da admissão
não é redirecionável por ambiente, e essa dívida fica nomeada.

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
