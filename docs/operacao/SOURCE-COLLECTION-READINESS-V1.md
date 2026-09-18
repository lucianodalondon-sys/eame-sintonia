# SOURCE COLLECTION READINESS V1 — DAS FONTES CONHECIDAS, QUANTAS SÃO COLETÁVEIS AGORA

**Missão:** SOURCE-COLLECTION-READINESS-V1 · **Data:** 2026-09-18 · **Branch:** `it-source-collection-readiness-v1`
**BASE_HEAD:** `d915f85a86a7ef0d310859f7380159dbed65b48a` (claude/it-trunk-v1)

> Este ficheiro é escrito à mão e explica. Os números vivem no censo **gerado**
> [`SOURCE-COLLECTION-READINESS-CENSO-V1.md`](SOURCE-COLLECTION-READINESS-CENSO-V1.md) e no seu JSON
> (`data/derivados/SOURCE-COLLECTION-READINESS-V1.json`), produzidos por
> `provas/medir_source_collection_readiness.py`. Um teste reprova se o censo gravado divergir do
> que o código e o runtime produzem hoje (`tests/test_source_collection_readiness.py`).

(O relatório completo, com os números finais, está no fim deste ficheiro — secção «ENTREGA».
Esta secção de abertura foi escrita enquanto os canários corriam; os números finais mandam.)

---

## 1 · A PERGUNTA, E OS CINCO UNIVERSOS QUE NÃO SE MISTURAM

```
DECLARED_CONTRACT            != CAPABILITY EXISTS != COLLECTION WIRED != FLOW OBSERVED
                             != SOURCE_COLLECTION_READY != BIG_COLLECTION_EXECUTABLE
```

O índice gerado (`docs/fontes/INDICE-DE-FONTES.md`, coluna «a máquina busca?») **não é owner do
readiness**. Medido no gerador: `scan_sources.py::dos_contratos()` lê **só**
`docs/operacao/CONTRATOS-DAS-FONTES-EAME.md`. Não lê `regras/italy_contracts.mjs`, não lê o coletor,
não lê o ledger. Contraprova: das 6 fontes que a primeira Big Collection executou com corridas
HEALTHY (commit `d915f85a`), o índice marca «sim» em **1** (IT-T4-001, que tem bloco nos dois
documentos). `INDEX_COLLECTION_READINESS_STALE = YES`.

O readiness desta missão nasce de quatro autoridades, e só delas:

| pergunta | autoridade |
|---|---|
| o coletor sabe percorrer? | `coleta/italy_pilot_collect.mjs::FONTES_PERCORRIVEIS` (7 com código próprio + tabela declarativa) |
| a receita despacha? | `pedido/receitas.py::EXECUTORES[território]` → `italia-recorrente` |
| houve corrida real? | `data/collection-ledger/italy/observations.ndjson` (HEALTHY com `RAW_SHA256`) |
| o canário atravessou até à porta? | `data/samples/RUN-MANIFEST.json` (recibo da corrida: INGRESSO · DERIVAÇÃO · ADMISSÃO · persistência) |

## 2 · OS QUATRO CONTADORES — QUATRO OWNERS

| contador | valor | o que mede de verdade | owner | stale? |
|---|---|---|---|---|
| `ATLAS_FICHAS` | 210 | fichas do Atlas com `SOURCE_ID` válido; ficha multinacional conta por SOURCE_ID | `scan_sources.py` → `sources.generated.json` | não |
| `ATLAS_HEADER_STAMP` | 190 | o carimbo `SOURCE_ID_COUNT` no cabeçalho do Atlas | `docs/fontes/ATLAS-DE-FONTES-EAME.md` linha 9, à mão | **sim** — o índice regista a divergência (190 vs 210) como decisão humana |
| `ESCADA_REGISTADA` | 173 | fichas com exemplo real guardado (degrau 2) | `scan_sources.py` (escada) | NÃO SEI — lê a ficha, não a evidência em disco |
| `CONTRATOS_DECLARADOS` | 5 | blocos `SOURCE_ID` em `CONTRATOS-DAS-FONTES-EAME.md` | `scan_sources.py::dos_contratos()` | **sim** como medida de readiness |

Nenhum foi «acertado» para bater com outro. O que cada um mede é diferente, e o teste guarda a
separação. O universo desta missão é **IT (157) + EU (13) = 170** fichas — 157 confere com o
ADDENDUM-03 (156 fichas com `SOURCE_ID` + a ficha agrupada `FR/ES/IT-T9-001`), medido pelo
gerador canónico, nunca por regex sobre menção.

## 3 · AS FORMAS DE AQUISIÇÃO (§4 · §5) — O QUE A SONDAGEM MEDIU

Sondagem read-only de 2026-09-18 (egresso Itália, Proton), fonte a fonte: abrir a página de
entrada, procurar um documento a partir dela, abrir o documento, ler a assinatura dos bytes.
Resultado bruto: 70 fontes com documento aberto à primeira, 33 sem link de documento pela regra
genérica, 13 com documento que não abriu como esperado, 10 sem URL/entrada e 9 com entrada
inacessível daqui. Três formas cobrem quase tudo o que abre por HTTP:

| SHAPE | como se chega | quem percorre | contrato de entrada | contrato de saída |
|---|---|---|---|---|
| `PDF_DISCOVERY_PAGE` | ENTRY_URL → primeiro link que casa com LINK_PATTERN → `%PDF` | coletor genérico (`ACQUISITION` no contrato) | ENTRY_URL · LINK_PATTERN · SAME_HOST · STRIP_SUFFIX · MAX_ITEMS | observação do ledger: RAW preservado antes do parse, sha256, `DOCUMENT_ID = NAO SEI` declarado |
| `HTML_ARTICLE_DISCOVERY` | ENTRY_URL → primeiro link de artigo (sob o caminho do exemplo, ou palavra-chave + slug) → HTML ≠ entrada | idem | idem | idem (derivação NOT_APPLICABLE: a casa não deriva HTML) |
| `PDF_DIRECT` | GET no documento fixo observado | idem | ENTRY_URL | idem |
| `CSV_DATASET` · `HTML_STATIC` | código próprio do piloto | `case` por fonte | contrato à mão | idem, com identidade semântica |
| `JSON_API` (ORCID ×36, EU) | API pública | `corpus_pesquisador.py` (T6), `agrifood_ue.py` | — | devolve **CATALOG** — não atravessa |
| `OFFICIAL_API` (CELLAR, EPPO) | SPARQL / REST | `eu_regulatorio_executor.py` (só EU-T4-001) | celex | ENVELOPE |
| `BROWSER_PUBLIC` | só com janela | nenhuma rota honesta | — | BROWSER_RENDERED_EXTRACT ≠ RAW |
| `DATASET_ODS` | ODS descoberto | nenhum | — | — |

**Uma ferramenta, N linhas de configuração.** A tabela `regras/italy_contracts_onboarded.json`
declara, por fonte, `SHAPE · ENTRY_URL · LINK_PATTERN · EXPECTED · EVIDENCE · SONDAGEM`; o ficheiro
de contratos (`regras/italy_contracts.mjs`, o **único** export `CONTRACTS`) expande cada linha num
contrato completo com as regras que a guarda exige (`DOCUMENT_ID_RULE`, `FAIL_CLOSED_RULE`,
`NEGATIVE_CONTROL`, `ROUTE_TYPE`). Fonte que já tinha contrato à mão (ARPAE, AGRIOS, FEM) recebe
**só** a forma de aquisição; o contrato à mão manda no resto.

O que a forma genérica **não inventa**: a identidade semântica. Sem regra medida por fonte, o
`DOCUMENT_ID` sai `NAO SEI` (a lei permite, COL-LAW-505), a observação identifica-se por
`SOURCE_ID + SOURCE_URL + bytes`, nunca se afirma «mudou no lugar», e o alvo estruturado **não** se
resolve — o campo fica ausente, com `DOCUMENT_ID_BASE` a dizer porquê.

## 4 · O QUE MUDOU NO CÓDIGO (mínimo, e onde)

| ficheiro | o quê |
|---|---|
| `regras/italy_contracts_onboarded.json` | **novo** — a tabela declarativa (uma linha por fonte, com a sondagem como evidência) |
| `regras/italy_contracts.mjs` | `aquisicaoDe()` · `contratoGenerico()` · merge da tabela no export `CONTRACTS`; `ONBOARDED_IDS` |
| `coleta/italy_pilot_collect.mjs` | `linksDaEntrada()` · `alvosGenericos()` · `identidadeGenerica()`; versionamento sem identidade (só SEEN_AGAIN/NEW); pasta `_SEM_IDENTIDADE`; `FONTES_PERCORRIVEIS`; assinatura reconhece BOM, GZIP e XML; `Accept-Encoding: identity`; exclui paginação e ativos estáticos |
| `coleta/italy_executor.py` | observação FAILED sem bytes vai para `ERROS` (ESTADO FAILED/PARTIAL), nunca para COLHEITA |
| `pedido/receitas.py` | `italia-recorrente` registado em T1, T5, T7, T9 (último), T10, T11, T12 — sem `filtros_por_omissao` |
| `regras/italy_pilot_guards.mjs` | guarda 21 mede a capacidade inteira (7 + tabela), e nenhuma fonte fora dela |
| `regras/italy_source_health.mjs` | manifesto sem amostra → `UNKNOWN`, nunca `FAILED` |
| `provas/medir_source_collection_readiness.py` · `tests/test_source_collection_readiness.py` | o censo e as suas guardas |

`NEW_CAPABILITIES = 0` · `NEW_COLLECTORS = 0` · `REUSED_COLLECTORS = 1` (o coletor italiano,
ampliado sem quebrar contrato — passo 4 da ordem do §6).

## 5 · ACHADOS (o que a estrada revelou)

1. **Uma observação falhada chegava à porta como item.** Antes desta missão o adaptador declarava
   toda observação do livro como COLHEITA — inclusive `DISCOVERY_FAILED` sem bytes — e a Admissão
   respondia `NAO_SEI` a um erro. O envelope dizia `SUCCESS` com `ERROS = []`. Corrigido: erro vai
   em `ERROS`, e o estado diz `FAILED`/`PARTIAL` (COL-LAW-037 · COL-LAW-505).
2. **`RAW_OBJECT_CREATED = False` na primeira Big Collection (IT-T3-010).** Causa medida: o
   ficheiro já existia no disco da worktree que correu (`guardarRaw` é idempotente) e o livro
   commitado não tinha observação com esse sha — uma captura anterior não chegou ao ledger. Nenhum
   dos 9 brutos dessa corrida está nesta árvore: `data/collection-store` não é rastreado além de 11
   ficheiros antigos. «Observação registada ≠ objeto bruto guardado» continua verdade.
3. **SEEN_AGAIN contra banco vazio dá `RAW_PERSISTENCE_FAILED`.** A ARPAE (IT-T2-001) foi colhida
   duas vezes hoje (a primeira corrida abortou por `SINTONIA_PSQL_EXE` ausente **depois** de o
   coletor escrever no livro); a segunda veio `SEEN_AGAIN` com `RAW_OBJECT_CREATED = False`, o
   banco recebeu a linha (`raw_asset.id = 1`, run_id da corrida) e o ingresso não a reconheceu
   (`RUN_STATE PARTIAL`, `PARA_A_DERIVACAO = []`). Fresh PDFs (`NEW_DOCUMENT`) atravessam inteiros
   (RAW → DERIVED PASS → ADMISSÃO). Fica como dívida nomeada do ingresso, não como blocker da
   fonte.
4. **A trava da inteligência congela um contrato de coleta.** `censo_do_congelamento.py::_especie`
   classifica `regras/italy_contracts.mjs` como `IMPLEMENTATION` porque o texto contém
   `RECOMMENDATION` (um campo a extrair dos boletins). A lista `DE_COLETA` está declarada e não é
   usada; a espécie `COLLECTION_ONLY` que o gerado descreve não existe no código. E os dois testes
   da trava **já falhavam na base** d915f85a nesta máquina (baseline, linhas 24284 e 24309). Ver §7.
5. **Descoberta genérica escolhe «o primeiro link que casa».** Para algumas fontes isso é o
   documento certo (boletim na pasta do exemplo real, 30 fontes); para outras é o primeiro PDF da
   home (um tarifário na ARPA Marche). O censo mostra o **documento observado** por fonte, para
   ninguém ler «READY» como «traz o boletim certo». Refinar `LINK_PATTERN` por fonte é configuração,
   não código — e é o próximo passo natural.

## 6 · RED TEAM (§19)

| ataque | resultado |
|---|---|
| duas fontes com o mesmo SOURCE_ID | a tabela recusa repetição e o merge recusa sobrepor contrato à mão; `SOURCE_ID` só entra se tiver ficha no Atlas (teste 4) |
| URL usada como SOURCE_ID · SHA como DOCUMENT_ID | `DOCUMENT_ID = NAO SEI` declarado; `_fabricado()` do envelope continua a recusar sha/caminho; guarda 26 do piloto continua verde |
| collector engolindo parâmetro sem usar | `--fonte` obrigatório; fonte fora de `FONTES_PERCORRIVEIS` sai com 2; `FILTRO_NAO_CONSUMIDO` no orquestrador |
| PDF linkado mas nunca baixado | o canário baixa e valida `%PDF`; HTML servido como PDF é `BYTE_VALIDATION_FAILED` |
| landing page registada como documento | a entrada nunca é alvo; paginação (`/page/2`) e ativos (`.css/.xml`) excluídos (teste 6); descoberta vazia é `EMPTY_LIST → FAILED` |
| CATALOG contado como COLHEITA · SUPPORT na Admission | T6/ORCID fica `NOT_WIRED`: o executor declara CATALOG e não atravessa |
| canário de uma fonte usado para declarar outra pronta | um canário por fonte, pela porta canónica; `CANARY_STATE` por SOURCE_ID no censo |
| paginação inexistente declarada como total | `MAX_ITEMS = 1`: canário, não Big Collection; nada afirma total |
| erro 403 tratado como zero resultados | `entrada inacessivel: 403` → observação FAILED → `ERROS` do envelope (achado 1) |
| rota paga sem autorização | `COST_USD = 0` em todas as corridas; nenhuma rota Apify tocada |
| browser fallback escondido | `BROWSER_PUBLIC` fica `BROWSER_REQUIRED`, sem tentativa |
| fact location / fact time inferidos | `FACT_TIME = UNKNOWN`, `FACT_LOCATION_RULE = UNKNOWN por padrão — NUNCA inferir` |
| mesmo conteúdo em duas fontes colapsando | sem identidade, versão só por (SOURCE_ID, URL, sha); nunca `CHANGED_IN_PLACE` (teste 9) |

`RED_TEAM_BLOCKERS = 0` — o único ataque que **encontrou** um defeito (403/erro como item) foi
corrigido nesta missão (achado 1).

## 7 · A FUNDAÇÃO DA COLLECTION PODE FECHAR? (ADDENDUM-02 · 03)

### 7.1 Denominador

```
FOUNDATION_CENSUS_UNIVERSE    54    candidatas/ITALY-SOURCE-MASTER-V1.json (censo_das_estradas_it.py:33-40)
CURRENT_ATLAS_IT_UNIVERSE    157    sources.generated.json (gerador canónico) — igualdade de conjuntos com o índice
UNIVERSE_GAP                 103
UNIVERSE_GAP_EXPLAINED       YES    o master é a fotografia ADITIVA de uma missão de 2026-09-07
                                    (4 pré-existentes + 1 redefinida + 49 candidatas novas; 10 territórios;
                                    não toca o Atlas — `canonical_artifacts_touched.modified = []`).
                                    Dos 54, 39 não têm ficha no Atlas; 140 fichas IT do Atlas não estão nos 54.
FOUNDATION_DENOMINATOR_VALID  NO
BLOCKER                      FOUNDATION_DENOMINATOR_STALE (54 / 157)
```

O censo de estradas **não lê o Atlas** (nenhuma referência em `censo_das_estradas_it.py`); itera
só a chave `sources` do master. Coerência interna (24+7+14+9 = 54) não é cobertura.

### 7.2 As 23 sem rota conhecida — dois estados, não um

`REACHABLE_ROUTE_UNKNOWN` (14, a porta abre; `censo_das_estradas_it.py:660-673`): IT-T2-005,
IT-T3-004 (corpo pequeno demais → OFFICIAL_SITEMAP), IT-T3-006, IT-T3-007, IT-T3-012, IT-T5-004,
IT-T7-001, IT-T7-004, IT-T7-006, IT-T7-011, IT-T9-004, IT-T9-007, IT-T10-001, IT-T11-004
(BROWSER_PUBLIC_HEAD). `ROUTE_UNKNOWN` (9): IT-T3-003, IT-T7-012 (porta não medida); IT-T5-002,
IT-T7-003, IT-T9-006, IT-T10-003 (erro de transporte); IT-T9-002, IT-T9-003, IT-T9-008 (curl
recusado → navegador italiano).

Destas 23, **só 3 estão no universo do Atlas** (IT-T5-002, IT-T9-002, IT-T9-008); as outras 20 são
IDs do master sem ficha. Pelo lado desta missão: IT-T5-002 ficou configurada na forma genérica
(canário decide), IT-T9-002/IT-T9-008 são `BROWSER_REQUIRED`. Para as 20 sem ficha esta missão não
mede nada — não são fonte do Atlas, e o §3 da missão proíbe promover candidata a fonte.

### 7.3 As 12 classes de estrada

Nenhuma fecha (`ARCHITECTURE_CLOSED = []`, `rotas_medidas()` :383-385 exige zero passos UNKNOWN,
zero bloqueio, zero dívida). O que falta, passo a passo:

| RC | passos que bloqueiam | estado |
|---|---|---|
| RC-1 OFFICIAL_HTTP_DOCUMENT | STRUCTURED, ADMISSION (`CODE`, `NO_DIRECT_REFERENCE`) | REQUIRED — é a classe dos canários desta missão; 1 PROVEN + 26 CANDIDATE |
| RC-2 YOUTUBE_OFFICIAL_API | RUN, ADMISSION (`NO_DIRECT_REFERENCE`) | REQUIRED (T8/T9 social) |
| RC-3 PUBLIC_NATIVE_API | RUN, CK, ST, ADM UNKNOWN | UNKNOWN |
| RC-4 SCIENCE_METADATA_API | RAW..ADM UNKNOWN | REQUIRED (36 fontes T6 ORCID dependem dela) |
| RC-5 REGULATORY_BULK_IMPORT | D, F, RAW, ADM UNKNOWN | REQUIRED (IT-T4-001 CSV) |
| RC-6/7/8 PUBLIC_BROWSER · LOCAL_SESSION · PAID_FALLBACK | BLOCKED por lei | NOT_REQUIRED enquanto a lei os barrar |
| RC-9 GIT_LEDGER | DEBT (P-011: estado operacional em Git) | REQUIRED até migrar; as 6 da Big Collection são PROVEN aqui |
| RC-10 OFFICIAL_HTTP_DATASET | D, F, CK, ST, ADM UNKNOWN | REQUIRED (CSV/ODS) |
| RC-11 OFFICIAL_STATISTICAL_API | tudo UNKNOWN | UNKNOWN (ISTAT não está no Atlas) |
| RC-12 SYNDICATED_FEED | D, F, CK, DER, ST, ADM UNKNOWN | UNKNOWN (nenhuma fonte do Atlas configurada por feed) |

`ROUTE_CLASSES_REQUIRED_TOTAL = UNKNOWN` continua — e continuará enquanto o denominador for 54.
`NO_DIRECT_REFERENCE` (3×: RC-1/STRUCTURED, RC-2/RUN, RC-2/ADMISSION) e `NOT_OBSERVED` (5×: RC-3,
4, 10, 11, 12) não contradizem a corrida real: as 6 estão `PROVEN` em RC-9 e IT-T2-002 em RC-1. Os
8 `PROOF_KIND = EXPECTED` são todos `CANDIDATE`; nenhum sustenta um `PROVEN`.

**Contradição real, medida:** o censo de estradas declara RC-1/STRUCTURED e ADMISSION como `CODE`
sem referência direta — mas os canários desta missão e a Big Collection atravessaram RAW → DERIVED
→ ADMISSÃO com decisões escritas no `LIVRO-DE-DECISOES.json`. O mapa não observa o runtime aqui:
lê `ROUTE_MEMBERSHIPS` do master (54) e não o `RUN-MANIFEST`. Causa: scanner sobre o universo
errado; a correção do gerador é dívida do owner do censo, não desta missão.

### 7.4 Critérios A..N

| crit. | texto | estado | prova | denominador / nível |
|---|---|---|---|---|
| A | toda fonte IT tem route class conhecida ou BLOCKED | **FAIL (sobre 54)** · **UNKNOWN (sobre 157)** | 23 UNKNOWN em `RESOLUCAO_POR_FONTE` | implementação, universo errado |
| B | nenhuma fonte depende de writer improvisado | FAIL | RC-1/RC-2 `NO_DIRECT_REFERENCE` | implementação |
| C | RAW tem um dono | PASS | `guarda/preservar_coleta.py`; canários: `raw_asset` por run_id (54329) | implementação; ressalva achado 2/3 |
| D | a corrida tem um contrato | PASS | RC-1 RUN=OBSERVED; `collection_run` no banco | implementação |
| E | o checkpoint tem um dono | FAIL | CK UNKNOWN em RC-3/10/12 | implementação |
| F | o derivado tem um dono | PASS | `coleta/executor_texto_de_pdf.py`; canários DERIVED PASS | implementação |
| G | persistência estruturada por espécie | FAIL | STRUCTURED CODE/UNKNOWN; genéricos não resolvem alvo | implementação |
| H | escolha de rota não vive espalhada | FAIL | `social_matriz.py` + orquestrador | implementação |
| I | Apify não é rota por omissão | **PASS medido** (`APIFY.DEFAULT = 0`) mas listado em «faltam» | inconsistência contrato↔gerado (DEFECT-06) |
| J | Git não é estado operacional | FAIL | RC-9 DEBT; ledger NDJSON cresceu nesta missão | implementação |
| K | retry/queda não fabrica sucesso | PASS | envelope FAILED/PARTIAL com erros (achado 1 reforça) | implementação |
| L | UNKNOWN continua UNKNOWN | PASS | `test_estradas_it.py`; este censo escreve UNKNOWN/NAO SEI | implementação |
| M | System Map representa tudo | FAIL/UNKNOWN | cadeia do mapa; censo de estradas sobre 54 | implementação |
| N | inteligência congelada até ao fim | **FAIL (medido)** | `test_trava_da_inteligencia` já vermelho na base; manifesto gerado em 78f8fcdc ≠ árvore | medição por SHA; decisão documental |

`docs/operacao/TRAVA-DA-INTELIGENCIA.json` não anexa prova por critério — só classifica
cumprido/falta à mão (`:49-83`). DEFECT-06 **CONFIRMED**: classificação documental desligada da
medição (I), e o classificador do congelamento conta a palavra em vez da gaveta (achado 4).

### 7.5 Veredito proposto (não alterado)

```
COLLECTION_FOUNDATION_CLOSED_CURRENT = NAO
BLOCKERS_REMAINING = FOUNDATION_DENOMINATOR_STALE (54/157) · A · B · E · G · H · J · M · N
DEFECT_05 = CONFIRMED   (provas/trava_da_inteligencia_morde.py deixa
                         system-map/data/congelamento.generated.json modificado: FROZEN_AT_HEAD e o
                         blob de italy_contracts.mjs; e TRAVA_MORDE=FAIL porque a base já diverge)
DEFECT_06 = CONFIRMED   (critérios sem prova ligada; espécie por palavra, não por gaveta)
```

`leis/fundacao_da_coleta.py:55` continua `COLLECTION_FOUNDATION_CLOSED = False` — **não tocado**.
`DIRECT_INTELLIGENCE_CHANGES = 0`.

---

## 8 · ENTREGA (§28 da missão + §11 do ADDENDUM-02)

```
GIT
BRANCH                         it-source-collection-readiness-v1
BASE_HEAD                      d915f85a86a7ef0d310859f7380159dbed65b48a
FINAL_HEAD / REMOTE_HEAD       no relatório da entrega (o commit não conhece o próprio SHA)

UNIVERSO
TOTAL_SOURCES                  170   (fichas do Atlas IT + EU, pelo gerador canónico)
IT_SOURCES                     157
EU_APPLICABLE                   13

ANTES  (capacidade que existia antes desta missão E corrida HEALTHY antes de 2026-09-18T18:00Z)
SOURCE_COLLECTION_READY_BEFORE   6   IT-T2-002 · IT-T2-004 · IT-T3-002 · IT-T3-008 · IT-T3-010 · IT-T4-001
BIG_COLLECTION_EXECUTABLE_BEFORE 6

DEPOIS
SOURCE_COLLECTION_READY_AFTER   95
NEW_SOURCE_COLLECTION_READY     89   (88 pela tabela declarativa + EU-T4-001, cujo primeiro canário nesta árvore correu hoje)
STILL_NOT_READY                 75
BIG_COLLECTION_EXECUTABLE_AFTER  6   (READY × RELEVANCE SIM × policy × custo — a relevância não mudou)

RELEVÂNCIA
RELEVANCE_SIM                    6   (as seis decisões humanas do Livro de Relevância)
RELEVANCE_PENDING              164   (NAO_AVALIADA — nada foi decidido pela máquina)

SHAPES
ACQUISITION_SHAPES              11   PDF_DISCOVERY_PAGE · HTML_ARTICLE_DISCOVERY · PDF_DIRECT · HTML_STATIC ·
                                     CSV_DATASET · JSON_API · OFFICIAL_API · BROWSER_PUBLIC · DATASET_ODS ·
                                     ROUTE_UNKNOWN (SOCIAL_PUBLIC modelada, sem fonte no universo)
SHAPES_ALREADY_SUPPORTED         5   PDF_DISCOVERY_PAGE (case) · PDF_DIRECT (case) · HTML_STATIC · CSV_DATASET · OFFICIAL_API (EU-T4-001)
SHAPES_NEWLY_SUPPORTED           3   PDF_DISCOVERY_PAGE (genérica) · HTML_ARTICLE_DISCOVERY · PDF_DIRECT (genérica)
SHAPES_BLOCKED                   5   JSON_API (NOT_WIRED/CAPABILITY_MISSING) · BROWSER_PUBLIC · DATASET_ODS · ROUTE_UNKNOWN · OFFICIAL_API (EPPO/CELLAR-T12)

IMPLEMENTAÇÃO
SOURCES_CONFIGURED             107   (regras/italy_contracts_onboarded.json)
SOURCES_CANARY_PASS             88
SOURCES_CANARY_FAIL             19   (15 EMPTY_LIST · 1 HTTP 400 · 1 HTTP 404 · 1 transporte · 1 XML no lugar de HTML → 400)
NEW_CAPABILITIES                 0
NEW_COLLECTORS                   0
REUSED_COLLECTORS                1   (coleta/italy_pilot_collect.mjs, ampliado para ler a forma do contrato)

BLOCKERS (por fonte, §18)
SOURCE_ID_MISSING                0
ROUTE_UNKNOWN                    5   IT-T3-001 · IT-T11-001 · IT-T9-001 · IT-T5-031 · EU-T8-001
CAPABILITY_MISSING               7   EU-T1-001 · EU-T1-002 · EU-T2-001 · EU-T2-002 · EU-T2-003 · IT-T5-003 · IT-T7-002
NOT_WIRED                       39   36 × T6 ORCID (executor devolve CATALOG) · EU-T5-001 · EU-T10-001 · EU-T12-001
POLICY_BLOCKED                   0
PAID_BLOCKED                     0
BROWSER_REQUIRED                 4   IT-T9-002 · IT-T9-008 · EU-T4-002 · EU-T9-002
AUTH_REQUIRED                    1   EU-T3-001
CANARY_FAILED                   19
RELEVANCE_PENDING              164   (eixo separado: não impede TECHNICALLY_READY)
UNKNOWN                          0

PROVAS
TESTS                          suíte inteira antes/depois nesta máquina — ver §9; guardas Node dos contratos
                               352 passaram · 72 falharam, e as 72 são as mesmas da base (NEW = 0);
                               tests/test_source_collection_readiness.py 10/10
NEW_FAILURES                   ver §9
RED_TEAM_BLOCKERS                0
SYSTEM_MAP_CHECK               ver §9

RESULTADO
SOURCE_COLLECTION_READINESS_V1 PASS   (universo medido · fontes agrupadas por aquisição · ferramentas existentes primeiro ·
                                       107 configuradas · gaps separados · canários por fonte · wiring canónico ·
                                       identidade preservada · nenhuma rota bloqueada aberta por atalho)
KNOW_HOW_DELTA                 ATUALIZAÇÃO NECESSÁRIA — §147 em SINTONIA-EAME-KNOW-HOW.md
BIBLIA_CONTRACT_CHANGE         NO
NEXT_MINIMUM_STEP              (1) decisão humana de relevância para as 89 novas — sem ela BIG_COLLECTION_EXECUTABLE fica em 6;
                               (2) LINK_PATTERN por fonte nas 19 CANARY_FAILED e nas 30 com regra «slug»;
                               (3) decidir a unidade de colheita de T6 (36 fontes) — CATALOG ou documento;
                               (4) owner do censo de estradas: denominador 54 → 157 (FOUNDATION_DENOMINATOR_STALE).

FUNDAÇÃO (ADDENDUM-02/03)
CENSUS_UNIVERSE_SIZE            54     ATLAS_IT_UNIVERSE_SIZE  157     UNIVERSE_GAP  103     UNIVERSE_GAP_EXPLAINED  YES
FOUNDATION_DENOMINATOR_VALID    NO
TOTAL_IT_SOURCES               157     SOURCES_WITH_ROUTE_CLASS  (no censo: 31 de 54)   SOURCES_ROUTE_UNKNOWN  23  (REACHABLE 14 · ROUTE_UNKNOWN 9)
ROUTE_CLASSES_MODELED           12     REQUIRED  RC-1 RC-2 RC-4 RC-5 RC-9 RC-10     NOT_REQUIRED  RC-6 RC-7 RC-8 (barradas por lei)
                                       UNKNOWN  RC-3 RC-11 RC-12       ARCHITECTURE_CLOSED  0 / 12
CRITERIA_A_TO_N                 A FAIL(54)/UNKNOWN(157) · B FAIL · C PASS · D PASS · E FAIL · F PASS · G FAIL · H FAIL ·
                                I PASS-medido/FALTA-no-contrato · J FAIL · K PASS · L PASS · M FAIL · N FAIL(medido)
COLLECTION_FOUNDATION_CLOSED_CURRENT  NAO
BLOCKERS_REMAINING              FOUNDATION_DENOMINATOR_STALE · A · B · E · G · H · J · M · N
DEFECT_05                       CONFIRMED      DEFECT_06  CONFIRMED
DIRECT_INTELLIGENCE_CHANGES     0
```

**O que os canários deixaram, e onde.** 180 corridas pela porta canónica hoje (107 fontes, com
repetições após afinar a regra de descoberta); no banco descartável 54329: 94 corridas, 94 `raw_asset`,
94 `storage_object`, 35 `derived_artifact`, 35 `documento_estruturado` (os PDFs atravessam
RAW → DERIVED → STRUCTURED; HTML fica em RAW: a casa não deriva HTML — `NOT_APPLICABLE`, honesto).
Admissão dos 88 canários que abriram documento: `SIM` 13 · `NAO` 3 · `NAO_SEI` 57 · `NAO_SE_APLICA` 15.
Os 13 `SIM` pousaram no backend de ficheiro da Sala (`data/samples/PRONTO-PARA-INTELIGENCIA/`, 13 corridas)
porque nenhuma Sala operacional (`SINTONIA_SALA_DSN`) foi declarada — de propósito: canário não é Big
Collection. Esses ficheiros e os 101 brutos (77 MB em `data/collection-store/italy/`) **não são
commitados**, como nunca foram em ramo nenhum; o que viaja é o livro (`observations.ndjson` +175,
`runs.ndjson` +175), o recibo (`RUN-MANIFEST.json` +180 corridas) e o livro de decisões da Admissão
(+2588 linhas). `COST_USD = 0` em todas.

---

## 9 · REGRESSÃO E MAPA — MEDIDOS NESTA MÁQUINA, POR NOME

Suíte inteira (`py -m unittest discover -s tests`, PyYAML emprestado), três vezes: base `d915f85a`
antes de qualquer alteração, árvore alterada, e árvore commitada `12e66456`. Comparação por
**nome** de teste, deduplicando subTests (contar linhas inventa «falhas novas» que já existiam).

```
BASE d915f85a           Ran 4764 tests · 100 FAIL/ERROR · 73 nomes distintos
FINAL 12e66456          Ran 4774 tests · 101 FAIL/ERROR · 72 nomes distintos
NEW_FAILURES            0    (nenhum nome só na final)
FIXED                   1    test_M5_o_ponto_fixo_existe_e_esta_alcancado_nesta_arvore
                             (o mapa regerado e commitado alcança o ponto fixo)
TESTES NOVOS            10   tests/test_source_collection_readiness.py (10/10)
```

O que a suíte da árvore alterada (antes do commit) apanhou, e o que se fez com cada coisa:

| falha (nome) | causa | o que se fez |
|---|---|---|
| `test_C1_a_sala_desta_arvore_esta_vazia` · `test_R3_a_sala_de_espera_real_continua_vazia` · `test_a_suite_nao_deixou_nada_no_acervo` (×2) · `test_rt7b_…` · `test_rt14_…` | os canários deixaram no disco 88 pastas de bruto (77 MB) e 13 corridas na Sala em ficheiro (`data/samples/PRONTO-PARA-INTELIGENCIA/`) | movidos para fora da árvore (`%TEMP%\sc-readiness\acervo-canarios\`); a lei «a Sala desta árvore está vazia» é a trava da inteligência, e os canários não a abrem |
| `test_T5_raw_imutavel` · `test_T6_ocorrencias_batem_com_a_corrida` · `test_sao_53_fichas` · `test_as_46_…` · `test_9_e_10_…` · `test_nao_revisavel_…` · `test_o_frame_e_maior_…` | os mesmos brutos no disco entravam na população do pacote de revisão T3 | idem — voltam a 53 / 49 sem tocar no pacote |
| `test_T8_o_markdown_nao_contradiz_o_estado_gerado` | o censo de estradas passou a reconhecer IT-T2-001 e IT-T3-011 como PROVEN pelo livro; `SOURCES_ROUTE_UNKNOWN` 23 → 22 | números do markdown `MAPA-DE-FECHAMENTO-DA-COLETA-ITALIANA.md` atualizados ao gerado, com nota datada |
| `test_reobservacao_nunca_guarda_objecto_novo` | a primeira `SEEN_AGAIN` com `RAW_PATH` no livro (IT-T2-001); o coletor escreve o caminho de propósito desde a correção «NAO CRIEI O OBJECTO AGORA != NAO HA BYTES» | teste alinhado à lei escrita: reobservação nunca cria objeto, e o caminho, se existe, é o de uma observação anterior com os mesmos bytes |
| `test_toda_decisao_do_livro_veio_das_keywords_de_hoje` | canários T2 no universo T2 escreveram `NAO_SE_APLICA`/`NAO_SEI` no livro; o teste exigia zero decisões de T2 | teste alinhado: zero **juízos** (SIM/NAO) de T2; `NAO_SE_APLICA` tem de dizer «nao ha regra escrita» |
| `test_quem_criou_objecto_tem_caminho_e_quem_nao_criou_nao_tem` | já falhava na base (IT-T3-010 da Big Collection, `RAW_OBJECT_CREATED = False` com caminho); ganhou dois subTests | pré-existente — não tocado |
| `test_o_ficheiro_bate_com_o_gerador` · `test_os_publicadores_ausentes_entraram` · `test_o_json_no_disco_…` | já falhavam na base nesta máquina (CRLF em `data/samples/PIEMONTE-FD/pagina.html`) | pré-existente — não tocado |

**Guardas Node dos contratos** (`node regras/italy_contract_test.mjs`): base 350 ok / 72 falhas;
final 352 ok / 72 falhas, **os mesmos 72 nomes** (as 72 são fichas GREEN sem amostra preservada e o
placar do JSON mestre — de outra missão). Uma guarda nova foi apanhada e refinada no caminho: bytes
recusados pela validação de assinatura são hashados como evidência e nunca preservados
(`RAW_PRESERVED_BEFORE_PARSE: false`), e a guarda diz isso em vez de os confundir com RAW.

**Provas do COLETA CHECK do CI**, corridas na árvore final e numa cópia descartável da base:
`valida_biblia` PASS · `paridade_da_lingua` PASS · `fluxo_no_seco` PASS · `o_dedupe_tem_constraint`
PASS · `o_executor_conta_se` PASS. Falham **igual** na base e na final (mesmos nomes):
`testa_coleta_canonica` (item e2e-1 → NAO) · `testa_golden_path_pdf` (T25) ·
`o_encanamento_tem_uma_porta` (P3, P11) · `a_fronteira_da_coleta` · `o_mapa_nao_mente`. E
`padrao_da_coleta::DOCUMENTO_TEM_IMPRESSAO_DIGITAL` (observações sem sha256) já era FAIL na base
com 31 e passa a 110: são as observações **FAILED** dos canários — sem bytes, sem sha —, que o
livro guarda de propósito. O número piorou porque a coleta tentou 107 fontes; a métrica não
distingue «falhou a olhar» de «documento sem impressão».

**System Map.** `py system-map/scripts/correr_a_cadeia.py REGERAR` + `VALIDAR`:
`SYSTEM_MAP_CHECK=PASS`. Carimbo pós-commit: `IMPRESSAO_DO_CARIMBO=IGUAL` (2247 ficheiros-fonte).
Bateria de testes do mapa, na final e na base: `test_freshness.mjs` PASS (49) ·
`test_impressao_da_arvore` PASS na árvore commitada · `test_papel_e_leitura_humana` PASS ·
`test_system_map` 6 reprovadas ⊂ 7 na base · `test_verdade_da_collection_actual` 2 = 2 ·
`test_base_da_auditoria` 1 = 1 · `test_quatro_planos` 2 = 2 · `test_cadeia_declara_io` 2 = 2.
**Nenhuma reprovação nova no mapa.** Peças relidas e recarimbadas uma a uma em
`architecture.declared.json` (nunca `--stamp` de tudo): C-IT-COLETA, C-IT-CONTRATOS, C-RECEITAS,
C-PROVA-COLETA.
