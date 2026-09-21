# CIRURGIA CROP END-TO-END — a cultura atravessa por onde já havia estrada

> **Missão:** `C-CROP-E2E-V1` · SOURCE BYTES → DERIVED → SALA → INTELLIGENCE, **sem recoleta**.
> **Bancada:** `crop-e2e-v1` · base `claude/int-pilot-sala-v1` · `INITIAL_HEAD d51ea98aea74ddec0b0e96c3e638cc789adf42b5`
> **Regras que mandaram:** Git + runtime + banco vencem qualquer handoff · CAN DO ≠ DID DO · ausência de prova = NÃO SEI · `NETWORK = OFF`.
> **Peças novas:** `coleta/executor_secoes_por_cultura.py` · `provas/a_cultura_atravessa.py` · `tests/test_a_cultura_atravessa.py`
> **Peças mexidas:** `leis/regua_italia.py` (14 culturas a mais) · `provas/o_piloto_da_sala.py` (v3)
> **Artefatos:** `data/derivados/A-CULTURA-ATRAVESSA.json` · `data/derivados/O-PILOTO-DA-SALA-R3-CROP.json`

---

## A RESPOSTA, ANTES DA PROVA

```text
T3_TOTAL                 5      (3 documentos: 2 estão pousados duas vezes)
T3_REDERIVED             4      pelo dono canónico do derivado; 3 INSERTED + 1 REUSED
T3_CROP_RECOVERED        3      Salerno (obs 7 e 26) · APOL (obs 1)
T3_CROP_UNKNOWN          1      ARIF N38 (obs 36): a cultura é um ÍCONE, não texto
T3_FAILED                1      ARIF N37 (obs 9): não há bytes locais; rede fechada

NEW_OBSERVATIONS_CREATED 0      raw_asset 1072 → 1072
NEW_COLLECTION_RUNS      0      collection_run 369 → 369
NEW_STORAGE_OBJECTS      0      storage_object 938 → 938
NEW_DERIVED_ARTIFACTS    3      derived_artifact 755 → 758 (ids 756, 757, 758)
SALA_ROWS_DELTA          0      a Sala não foi tocada: 46 → 46
NETWORK_REQUESTS         0      · PAID_USD 0
```

E o gate regulatório, que na R2 só sabia dizer `NOT_POSSIBLE`:

```text
CROSSINGS_TENTADOS            4
CROSSINGS_BLOCKED_BY_CROP     2   azoxystrobin × OLIVO (APOL) — o rótulo ADAMA não lista OLIVO
CROSSINGS_NOT_POSSIBLE        2   tau-fluvalinate no ARIF — cultura desconhecida
CROSSINGS_CROP_GATE_PASSED    0   na Sala real, nenhuma secção com cultura autorizada cita substância ADAMA
CROSSINGS_POSSIVEIS           0   REGION e FACT_TIME continuam sem chave
OPPORTUNITY_CANDIDATES        0
```

**A cultura chegou onde faltava sem mudar a Sala, sem mudar o contrato READY e sem um byte novo de fora.** O que não chegou está com nome e motivo.

---

## FASE 0 · ESTADO REAL

```text
COLLECTION_BRANCH  crop-e2e-v1
HEAD               d51ea98aea74ddec0b0e96c3e638cc789adf42b5   (= INITIAL_HEAD)
REMOTE_HEAD        a branch não existia no origin; origin/claude/int-pilot-sala-v1 = d51ea98a
WORKTREE           C:/Users/London1/orca/workspaces/eame-sintonia/crop-e2e-v1
DIRTY              0 rastreados · 1 não-rastreado (MISSAO-CROP-E2E.md, o brief)
ACTIVE_WRITERS     0 — os únicos processos com este caminho eram a minha shell
SALA               127.0.0.1:54330/sala_italia · LISTENING · pid 53588 · confirmado
                   cluster C:/Users/London1/sintonia-sala-italia/cluster · 46 linhas, 46 WAITING
```

Nenhuma das 14 worktrees activas listadas no brief foi aberta. Trabalho só nesta.

### O que a medição corrigiu no brief

O brief dizia «5 itens T3». São **5 linhas da Sala e 3 documentos**: `IT-T3-002` está pousado duas vezes (obs 7 e 26, os MESMOS bytes, `derived:6` nas duas), e `IT-T3-008` são dois boletins diferentes (N37, obs 9; N38, obs 36). E **nenhum dos três é o PDF que está no Git**: o repositório guarda as edições anteriores (SA-02-09, N36, n.9); a Sala aponta para SA-16-09, N37/N38 e n.10, no armazém operacional fora da árvore.

---

## FASE 1 · ONDE EXATAMENTE A CULTURA SE PERDE — por item, nunca por média

| item | `RAW_ASSET_ID` | `STORAGE_OBJECT` | `DERIVED_ID` | `SALA_ID` (run, ordem) | bytes locais |
|---|---|---|---|---|---|
| `IT-T3-002` SA-16-09 | 7 | `XX/it-t3-002/DOCUMENT/c5ae3bfe…SA-16-09.pdf` | 6 | `XX-T3-2026-09-18-171909-…`, 0 | SIM, sha bate |
| `IT-T3-002` SA-16-09 | 26 | o mesmo objecto (storage_object 7) | 6 | `IT-T3-2026-09-19-234958-…`, 0 | SIM, sha bate |
| `IT-T3-008` N37 | 9 | `XX/it-t3-008/DOCUMENT/a8d9c53a…N37_09-09-2026.pdf` | 7 | `XX-T3-2026-09-18-171937-…`, 0 | **NÃO** (dívida §161) |
| `IT-T3-008` N38 | 36 | `XX/it-t3-008/DOCUMENT/85cb86eb…N38_16-09-2026.pdf` | 11 | `IT-T3-2026-09-20-110656-…`, 0 | SIM, sha bate |
| `IT-T3-010` n.10 | 1 | `XX/it-t3-010/DOCUMENT/2ba23d22…n_10_del_14_09_2026.pdf` | 1 | `XX-T3-2026-09-18-134205-…`, 0 | SIM, sha bate |

`SOURCE_ID`, `ITEM_ID` (`derived:N`) e `RAW_OBSERVATION_ID` vêm da linha da Sala; o resto de `raw_asset`, `storage_object` e `derived_artifact` — lidos, não deduzidos.

| item | nos BYTES | no TEXTO extraído | na ESTRUTURA de tabela | no DERIVED (antes) | na ADMISSÃO | na SALA | visível à Intelligence (antes) | **`CROP_LOSS_STAGE`** |
|---|---|---|---|---|---|---|---|---|
| 002 / obs 7 | SIM — cabeçalho na camada de texto | SIM (12 culturas) | SIM (coluna «COLTURA») | NÃO | NÃO SE APLICA | NÃO SE APLICA | NÃO | **STRUCTURED** — o cabeçalho sobreviveu ao `TEXT_EXTRACTION`; ninguém o lia |
| 002 / obs 26 | idem | idem | idem | NÃO | idem | idem | NÃO | **STRUCTURED** |
| 008 / obs 9 | **NÃO SEI** — sem bytes | SÓ CONTEXTO («mosca dell'olivo») | NÃO | NÃO | idem | idem | NÃO | **DERIVED (por inferência)** — o texto da Sala mostra o padrão ARIF; os bytes não estão cá para confirmar |
| 008 / obs 36 | **NÃO SEI** — ícone | SÓ CONTEXTO | NÃO | NÃO | idem | idem | NÃO | **DERIVED** — o cabeçalho não está na camada de texto |
| 010 / obs 1 | SIM — título do anexo | SIM (OLIVO) | SIM (título da tabela) | NÃO | idem | idem | NÃO | **STRUCTURED** |

Três pontos de perda diferentes, como o brief avisou que podia acontecer:

- **Salerno e APOL:** a cultura ESTÁ no texto que a Sala tem (o `md5` do `texto` da Sala é byte a byte o `pdftotext` dos bytes guardados). Perde-se depois: nenhuma derivação, nenhuma etapa STRUCTURED ligava o cabeçalho ao bloco. **O dado chegou; a estrutura não** — exactamente o que a R2 escreveu.
- **ARIF:** a cultura de cada bloco é um **ícone** (14 imagens de 124×129 no PDF, uma por bloco). Zero cabeçalhos de cultura em maiúsculas na camada de texto, em quatro modos do `pdftotext` (`-raw`, `-table`, `-simple`, `-layout`) e no leitor próprio da casa (`coleta/pdf_text.py`). Aqui a perda é **no DERIVED**, e não é defeito da ferramenta: o texto nunca teve o cabeçalho.
- **ARIF N37 (obs 9):** não há bytes locais — é um dos sete históricos sem ficheiro do know-how §161 — e a rede está fechada. Fica **NÃO SEI**: a inferência pelo texto da Sala aponta para o mesmo padrão do N38, e uma inferência não é uma medição.

`CROP_PRESENT_IN_ADMISSION` e `CROP_PRESENT_IN_SALA` saem **NÃO SE APLICA**, não «NÃO»: medi o contrato READY perguntando ao dono (`admissao.pronto_para_inteligencia()` — 0 campos de cultura) e a tabela perguntando ao `information_schema` (0 colunas). É por desenho, e a FASE 2 diz porquê.

---

## FASE 2 · O OWNER CANÓNICO — o que já existia, e o que foi criado

| conceito | owner encontrado | o que se fez |
|---|---|---|
| vocabulário de cultura (IT) | `leis/regua_italia.py::CULTURAS` — 20 chaves com regex e quarentena por âncora | **reutilizado**; +14 chaves que os boletins escrevem e a régua não conhecia (ACTINIDIA, CILIEGIO, ALBICOCCO, SUSINO, MANDORLO, FRAGOLA, NOCCIOLO, NOCE, CASTAGNO, MELANZANA, CAROTA, CIPOLLA, LATTUGA, CARCIOFO), com os nomes do rótulo ADAMA onde ele os tem |
| cultura do rótulo | `referencia/adama/AUTHORIZED-USES.json::CROP_ON_LABEL` — 35 chaves, 2.030 usos | lido e citado; **nada escrito** |
| esquema do derivado | `supabase/migrations/022` (`derived_artifact`, `kind` fechado) · writer `guarda/preservar_derivado.py` | **reutilizado**: `kind = TABLE_EXTRACTION`, `producer = secoes-por-cultura`. Nenhum `kind` inventado |
| esquema da Sala / contrato READY | `031`+`032` · `admissao.pronto_para_inteligencia()` (19 campos) · COL-LAW-043 | **intacto** |
| Claim/Fact | `FATO` só para `ESTAGIO = FATO`; COL-LAW-202 diz que a Collection **não extrai** claim | não tocado — a cultura de uma secção não é claim, é estrutura declarada pelo documento |
| tabelas antigas `crop`, `conteudo_crop_issue`, `boletim_fitossanitario` (migrations 004, 021) | existem no banco com **0 linhas**; nenhuma ligada à estrada forward | não usadas: seriam um segundo vocabulário e um segundo dono |

### Por que a Sala NÃO ganhou coluna `crop`

Porque o grão está errado. Um boletim de Salerno tem **doze** culturas, uma por secção; o item da Sala é o documento. Uma coluna por item teria de escolher uma cultura ou virar lista — e o gate precisa de saber **em que secção** a substância foi recomendada. A cultura é da SECÇÃO. Por isso ela mora no DERIVED (uma derivação-irmã do mesmo original) e a Intelligence chega lá pela referência que a Sala já carregava:

```text
sala.item_id = "derived:N"
  → derived_artifact.id = N            (o texto que a porta julgou)
  → derived_artifact.parent_sha256     (os bytes do original)
  → derived_artifact WHERE kind = TABLE_EXTRACTION AND producer = secoes-por-cultura
  → storage_path no armazém            (as secções, cada uma com cultura, âncora e certeza)
```

Nada disto relê RAW nem redefine a Admissão: lê uma derivação do item **admitido**, a partir da linha da Sala.

---

## FASE 3 · MENÇÃO NÃO É CULTURA DO FACTO

Cada secção sai com cinco coisas, e os três estados são mesmo três:

| campo | o que diz |
|---|---|
| `STATUS` | `EXPLICIT` (um cabeçalho nomeia a cultura) · `CONTEXT_ONLY` (há termo de cultura no corpo, ninguém a declarou) · `UNKNOWN` (nada) |
| `CROP_EXPLICIT` / `CROP_TERM_AS_WRITTEN` | a chave da régua e a palavra tal como está no documento — só em `EXPLICIT` |
| `CROP_CONTEXT` | o texto do cabeçalho, a janela lida, e os **candidatos** do corpo, contados |
| `EVIDENCE_ANCHOR` | linha e carácter de início e fim no texto do `pdftotext` — o mesmo texto que a Sala tem |
| `PRECISION` / `CERTEZA` | `SECTION_HEADER` · `TABLE_TITLE` · `BODY_MENTION` · `NONE` / `OBSERVADO_NO_CABECALHO` · `OBSERVADO_NO_CORPO` · `NAO_SEI` |

«olivo» no corpo do ARIF é `CONTEXT_ONLY` com candidato `OLIVO` — e o gate trata-o como `UNKNOWN`. Não há regex solta a produzir certeza: no cabeçalho exige-se **palavra inteira** («Viterbo» não vira VITE), e a janela é o próprio anúncio «COLTURA» ou «Difesa integrata».

Medido nos bytes reais e nas edições anteriores do Git — o padrão repete-se de edição para edição:

```text
Salerno  SA-16-09 (Sala)   13 secções · 12 EXPLICIT · 0 CONTEXT_ONLY · 1 UNKNOWN
         SA-02-09 (Git)    idem
APOL     n.10 (Sala)        7 secções ·  6 EXPLICIT (título do anexo) · 1 CONTEXT_ONLY (monitorização)
         n.9  (Git)        idem
ARIF     N38 (Sala)        31 secções ·  0 EXPLICIT · 16 CONTEXT_ONLY · 15 UNKNOWN
         N36 (Git)         32 secções ·  0 EXPLICIT · 19 CONTEXT_ONLY · 13 UNKNOWN
```

---

## FASE 4 · PDFs E TABELAS — a causa, medida

| hipótese do brief | Salerno | APOL | ARIF |
|---|---|---|---|
| flattening destrói coluna | **sim, parcialmente** — o `pdftotext` corrido parte a linha da tabela: a célula «cultura» cai 0 a 8 linhas abaixo de «COLTURA», misturada com «N°», «Comune», «UTM»; em `-layout` fica na mesma linha | não | não |
| cabeçalho deixa de acompanhar linha | não — o cabeçalho antecede o bloco | **sim** na tabela do disciplinare (AVVERSITÀ / CRITERI / S.A.): as substâncias saem em bloco, separadas da linha; a cultura está no **título** da tabela, e o título sobrevive | não |
| tabela vira texto sem contexto | **sim** — e ninguém ligava cabeçalho a bloco | idem | — |
| parser ignora estrutura | **sim** — `TEXT_EXTRACTION` é texto corrido e não há etapa que leia estrutura | idem | — |
| outro motivo | — | — | **o cabeçalho é imagem** (ícone 124×129) — não há texto para extrair |

Resolvido o padrão real e comprovado: `CABEÇALHO DE CULTURA → BLOCO`, para dois tipos de cabeçalho («COLTURA …» em coluna; «Difesa integrata <cultura> …» em título). Não se construiu parser universal: as linhas de substância dentro da tabela do disciplinare continuam texto, e é o piloto quem as procura dentro da secção certa.

---

## FASE 5 · REDERIVAÇÃO LOCAL — só os bytes que já existem

```text
NETWORK = OFF · nenhum socket aberto; só psql local e disco
backup antes de escrever:  sala_italia-20260920-205142.dump (1.855.947 bytes, BACKUP=PASS)

raw 7   (SA-16-09)  INSERTED   derived 756  · 37.583 bytes · NOVO_UPLOAD
raw 26  (SA-16-09)  REUSED     derived 756  · reencontro pela outra captura dos MESMOS bytes
raw 9   (N37)       NAO_REDERIVADO — bytes ausentes; sem rede não há como os obter
raw 36  (N38)       INSERTED   derived 757  · 83.763 bytes · NOVO_UPLOAD
raw 1   (n.10)      INSERTED   derived 758  · 31.542 bytes · NOVO_UPLOAD
```

Cada linha foi escrita pelo dono (`guarda/preservar_derivado.py`): lida de volta e conferida campo a campo; o sha256 do ficheiro no armazém bate com a linha (conferido depois, à mão). `parent_sha256` é o do original; `parameters` é a receita e só ela — o sha do texto **não** entra nos parâmetros de propósito, para um `pdftotext` diferente dar `DERIVATION_DRIFT` e não uma segunda receita calada.

⚠️ **Um buraco declarado:** a rederivação não tem corrida (`collection_run`) — e não devia ter, o brief proíbe — e a `migration 029` exige `run_id NOT NULL` com chave estrangeira em `participacao_na_derivacao`. O writer respondeu `PARTICIPACAO_SEM_CORRIDA` e não escreveu a aresta (785 → 785 linhas). A linhagem existe na própria linha (`raw_asset_id` + `parent_sha256`); o que falta é a aresta «a obs 26 também participou». Decisão do dono da 029, não desta missão.

---

## FASE 6 · PROPAGAÇÃO — por item

| item | `DERIVED_CROP` | `ADMISSION_CROP` | `SALA_CROP` | `INTELLIGENCE_INPUT_CROP` |
|---|---|---|---|---|
| 002 / obs 7 | derived 756 · 12 EXPLICIT | NÃO SE APLICA (grão) | NÃO SE APLICA (grão); referência por `derived:6` | **PRESENT** — ACTINIDIA, AGRUMI, CASTAGNO, CILIEGIO, FRAGOLA, MELANZANA, NOCCIOLO, NOCE, OLIVO, PESCO, POMODORO, VITE |
| 002 / obs 26 | derived 756 (o mesmo) | idem | idem | **PRESENT** — os mesmos 12 |
| 008 / obs 9 | — | idem | idem | LOST_IN_DERIVATION (sem bytes) |
| 008 / obs 36 | derived 757 · 0 EXPLICIT | idem | idem | **UNKNOWN_IN_DERIVED** — 16 secções só com contexto |
| 010 / obs 1 | derived 758 · 6 EXPLICIT | idem | idem | **PRESENT** — OLIVO |

A referência canónica está provada em dois sítios que fazem a mesma consulta e não partilham código: `provas/a_cultura_atravessa.py::irmao_de_seccoes` e `provas/o_piloto_da_sala.py::ler_secoes_por_cultura`. O piloto (v3) mede, na Sala real:

```text
ITEMS_EXPECTING_CROP     5
ITEMS_WITH_CROP          3      (era 0)
CROP_LOST_IN_DERIVATION  1      (era 5) — o N37 sem bytes
CROP_UNKNOWN_IN_DERIVED  1      — o ARIF N38, com honestidade em vez de zero
```

---

## FASE 7 · O GATE REGULATÓRIO DISTINGUE — e o D-01 fecha

`cruzar()` passou a trabalhar por **(item, secção, substância)**, e `gate_de_cultura()` tem três respostas:

| caso | material | resultado | prova |
|---|---|---|---|
| **UNAUTHORIZED_CROP_CASE** | **real** — azoxystrobin no disciplinare do olivo (APOL, secções 1 e 2, `EXPLICIT OLIVO`); rótulos ADAMA com azoxystrobin: CIPOLLA, CUCURBITACEE, FRUMENTO, ORZO, POMODORO, SEGALE, TRITICALE, VITE | `BLOCKED_BY_CROP` | `O-PILOTO-DA-SALA-R3-CROP.json`, `XC-IT-T3-010-0-s1-AZOXYSTROBIN` |
| **UNKNOWN_CROP_CASE** | **real** — tau-fluvalinate no ARIF N38 (secção 13, `UNKNOWN`) | `NOT_POSSIBLE`, `CROP_GATE = UNKNOWN` | idem, `XC-IT-T3-008-0-s13-TAUFLUVALINA` |
| **AUTHORIZED_CROP_CASE** | **contraprova com o rótulo real**: a mesma substância (azoxystrobin, os mesmos registos e produtos ADAMA) sob um cabeçalho «COLTURA / VITE» — a secção é sintética, porque nenhum boletim da Sala junta azoxystrobin a uma cultura que o rótulo lista | `CROP_GATE_PASSED`, com `JOIN_KEYS_MISSING = [REGION, FACT_TIME]` | `tests/test_a_cultura_atravessa.py::AContraprovaComORotuloReal` |

A mesma substância, o mesmo rótulo, só a cultura muda — e o veredito muda. **`CROP_GATE_PASSED` não é oportunidade**: REGION e FACT_TIME continuam por chegar, `OPPORTUNITY_CANDIDATES = 0`, e o artefato diz porquê.

---

## FASE 8 · REGRESSÕES

| # | prova | onde |
|---|---|---|
| 1 | UNKNOWN não vira CROP — «olivo» no corpo é candidato; secção sem cabeçalho sai `NOT_POSSIBLE` | `UmMencaoNaoViraCrop` |
| 2 | PUBLISHED_AT não vira FACT_TIME — a derivação não emite tempo; com a cultura certa, FACT_TIME continua em falta | `OQueNaoSeMistura` |
| 3 | SOURCE_LOCATION não vira FACT_LOCATION — idem, REGION em falta | `OQueNaoSeMistura` |
| 4 | rederivar duas vezes = 1 derivado, 0 observações novas (banco real SQLite com as travas da 022) | `ARederivacaoNaoDuplica` |
| 5 | a segunda captura dos mesmos bytes REENCONTRA: 2 `raw_asset`, 1 `derived_artifact` | `ARederivacaoNaoDuplica` |
| 6 | CROP errado bloqueia (`BLOCKED_BY_CROP`) | `OGateDistingue` · `AContraprovaComORotuloReal` |
| 7 | CROP certo altera o resultado (`CROP_GATE_PASSED` ≠ `BLOCKED_BY_CROP`) | idem |

Mais: a porta continua a mandar `application/pdf` ao `texto-de-pdf` (o executor novo não rouba a rota); os bytes do artefato são determinísticos; o vocabulário é o da régua e não um segundo. **28 testes, 28 OK.** Sem `--armazem`, o piloto v3 reproduz a R2 número a número (46 · 8 · 26 · 5 · 0 · 3 crossings `NOT_POSSIBLE`).

```text
BASELINE (d51ea98a, esta máquina)   Ran 4937 · failures=115 · errors=16 · skipped=190 · 131 nomes
FINAL    (esta árvore)              Ran 4965 · failures=116 · errors=16 · skipped=190 · 132 nomes
NEW_FAILURES                        0 reais · 1 transitório · 4 subtestes com o mesmo nome e outro parâmetro
```

Comparação por **nome** (`comm` sobre as listas ordenadas), não por total:

- **1 nome novo, transitório:** `test_c4_gpu_local…test_rt7b_o_ficheiro_partido_nao_deixou_nada_no_acervo` — o teste exige `git status` limpo em `data/derivados/` e viu os dois artefatos desta missão **ainda não commitados**. Passa no commit; a mensagem de fecho traz a corrida isolada depois do commit.
- **4 subtestes de `test_metricas…test_todo_numero_publicado_vem_do_dono`** com o mesmo nome e o parâmetro `valor` mudado de `4.989` para `5.017`: é a contagem de testes, que subiu com os 28 novos; o teste já falhava na base por outro motivo (o documento não bate com o dono). Mesmo nome, mesma causa, número diferente.
- `Ran` subiu 28 = os 28 testes de `tests/test_a_cultura_atravessa.py`, todos OK dentro da suíte.

A base já chega vermelha nesta máquina (know-how: `fcntl`, DSNs ausentes, `TEST_COUNT` não mensurável); comparam-se **nomes**, não totais.

---

## FASE 9 · SYSTEM MAP

Houve elo novo — `DERIVED (secções por cultura) → Intelligence (piloto v3)` — e duas peças novas. Declaradas em `architecture.declared.json` (`C-EXECUTOR-SECOES-POR-CULTURA` em Z-ACOES, `C-PROVA-CULTURA-ATRAVESSA` em Z-PROVA); a descrição do `C-PROVA-PILOTO-SALA` foi relida e reescrita para a v3; os carimbos dos quatro ficheiros tocados foram actualizados um a um (não com `--stamp` global, que recarimbaria drift alheio).

```text
SYSTEM_MAP_CHECK = PASS   (22 de 22 provas, P1_SEM_DRIFT incluída — medido com a cadeia
                           canónica `correr_a_cadeia.py REGERAR · VALIDAR` sobre esta árvore;
                           o mapa regerado entra no commit seguinte ao das fontes, e o portão
                           pós-commit `--conferir-carimbo` fecha a prova)
```

---

## FASE 10 · NÃO RECOLETAR ARIF

Não se buscou boletim novo. O N37 sem bytes fica como está: dívida de SOURCE/CADENCE/SELECTION (GAP-07 da R2), do Source Curator/Auditor. E o que esta missão descobriu sobre o ARIF vai para lá também: **mesmo com o N39 colhido, a cultura do ARIF continuará `UNKNOWN`** enquanto o cabeçalho for ícone e esta casa não fizer OCR. Colher mais ARIF não resolve o ARIF.

---

## GAPS QUE FICAM (registados, não despachados)

| id | gap | dono |
|---|---|---|
| `CROP-GAP-01` | ARIF: cabeçalho de cultura é imagem; só OCR/leitura de imagem o alcança | capacidade nova — decisão arquitetural, não desta missão |
| `CROP-GAP-02` | N37 (obs 9) sem bytes locais; a Sala tem só a cópia do texto | Source Curator / Auditor (§161, GAP-07) |
| `CROP-GAP-03` | rederivação sem corrida não escreve `participacao_na_derivacao` (029 exige `run_id`) | dono da 029 |
| `CROP-GAP-04` | os ficheiros `TEXT_EXTRACTION` dos 4 derivados T3 não estão no armazém (a linha existe, o byte não) | dono do armazém |
| `CROP-GAP-05` | o executor novo não está na estrada forward automática (`_DONOS_DA_DERIVACAO`); corre por quem rederiva | HARD STOP do brief: automação é outra decisão |
| `CROP-GAP-06` | equivalência cultura-da-régua ↔ cultura-do-rótulo é igualdade de chave; `GRANO_GEN`/`ORTICOLE` nunca casam | Intelligence (INT-LAW-080..084) |

---

## ENTREGA

```text
INITIAL_HEAD                 d51ea98aea74ddec0b0e96c3e638cc789adf42b5
FINAL_HEAD                   o 2.º commit desta missão em crop-e2e-v1 («mapa: …»), a seguir ao
                             commit que contém este relatório — um ficheiro não pode conhecer
                             o SHA do próprio commit (AGENTS.md); o SHA vai na mensagem de fecho
REMOTE_HEAD                  = FINAL_HEAD depois de `git push -u origin crop-e2e-v1`
                             (conferido com `git rev-parse origin/crop-e2e-v1` na mensagem de fecho)
WORKTREE_CLEAN               SIM — `git status` vazio antes do push (conferido no fecho)
T3_TOTAL                     5
T3_REDERIVED                 4
CROP_PRESENT_IN_SOURCE       3 SIM (Salerno ×2, APOL) · 1 NÃO SEI (ARIF N38: ícone) · 1 NÃO SEI (N37: sem bytes)
CROP_RECOVERED               3
CROP_STILL_UNKNOWN           2   (N38 ícone · N37 sem bytes)
CROP_LOSS_ROOT_CAUSE         Salerno/APOL: STRUCTURED — o cabeçalho sobreviveu ao texto e nenhuma
                             derivação ligava cabeçalho a bloco (tabela virou texto corrido).
                             ARIF: DERIVED — o cabeçalho é imagem; o texto nunca o teve.
DERIVED_CROP_AVAILABLE       SIM — derived_artifact 756, 757, 758 (TABLE_EXTRACTION / secoes-por-cultura)
INTELLIGENCE_CAN_CONSUME_CROP SIM — pela referência canónica sala.item_id=derived:N → parent_sha256 → irmã;
                             provado por duas consultas independentes e pelo piloto v3 na Sala real
AUTHORIZED_CROP_CASE         PASS — contraprova com rótulo ADAMA real (azoxystrobin × VITE); 0 casos na Sala real
UNAUTHORIZED_CROP_CASE       PASS — real: azoxystrobin × OLIVO (APOL) → BLOCKED_BY_CROP
UNKNOWN_CROP_CASE            PASS — real: tau-fluvalinate no ARIF → NOT_POSSIBLE
NEW_OBSERVATIONS_CREATED     0
NEW_COLLECTION_RUNS          0
NETWORK_REQUESTS             0
PAID_USD                     0
NEW_FAILURES                 0 reais (1 transitório por artefato não commitado; 4 subtestes
                             iguais com outro parâmetro) — ver FASE 8
SYSTEM_MAP_CHECK             PASS (22/22)
KNOW_HOW_DELTA               §162
```

---

## EM PALAVRAS SIMPLES

**1 · Onde exatamente a cultura estava a perder-se?**
Em dois sítios diferentes, e não num só. Nos boletins de Salerno e da APOL a palavra da cultura («OLIVO», «VITE», «ACTINIDIA») **estava escrita** no texto que a Sala guarda — como o título de cada gaveta. O problema é que ninguém tinha feito a etiqueta que diz «este texto pertence à gaveta OLIVO». O texto do documento vinha todo corrido, e a etiqueta perdia-se nesse corrido. No boletim da ARIF é diferente: a cultura de cada bloco é um **desenho**, um ícone, não uma palavra. Quando se tira o texto do PDF, o desenho fica para trás — e fica para trás em qualquer ferramenta, porque não há letra nenhuma para ler.

**2 · Quantos dos 5 documentos recuperaram a cultura?**
Três de cinco. Os dois de Salerno (que são o mesmo boletim guardado duas vezes) e o da APOL. Dos outros dois, um é o ARIF com o ícone — a ferramenta olhou, encontrou só menções («mosca da oliveira») e disse honestamente «não sei qual é a cultura». O outro é um ARIF mais antigo cujo ficheiro **não existe nesta máquina**: só sobrou a cópia do texto na Sala, e sem o ficheiro não há o que refazer.

**3 · Foi preciso recoletar alguma coisa?**
Não. Zero pedidos à internet, zero euros. Usei só os três ficheiros PDF que já estavam guardados no armazém. Não nasceu nenhuma observação nova, nenhuma corrida nova, nenhum ficheiro repetido. O que nasceu foram três «índices de gavetas» — um por documento — escritos pelo mesmo mecanismo que já escreve os textos, com a mesma prova de que ficou bem escrito. Antes de escrever, fiz uma cópia de segurança da Sala.

**4 · A Intelligence agora consegue enxergar a cultura?**
Sim, para os três documentos recuperados. E consegue sem que a Sala tenha mudado uma vírgula. Cada linha da Sala já tinha um número de referência do texto que ela guarda; esse número leva ao ficheiro original, e o original leva ao índice de gavetas novo. É como o índice no fim de um livro: não está na página, mas a página diz onde ele está. Um boletim de Salerno tem doze culturas, por isso a cultura não podia ser uma casinha na linha da Sala — é por gaveta, e é por isso que mora ao lado do texto e não dentro da Sala.

**5 · O gate regulatório finalmente distingue cultura autorizada, não autorizada e desconhecida?**
Sim, e foi testado com um caso real: a APOL recomenda azoxystrobin para a oliveira, e a ADAMA tem esse produto registado para videira, tomate, trigo — **não para oliveira**. Antes, o sistema dizia «não sei» para tudo. Agora diz «**bloqueado**: cultura fora do rótulo». Para a mesma substância numa gaveta «VITE» (videira), o gate diz «passou» — e isto foi provado com o rótulo real da ADAMA, mas com um pedaço de boletim inventado para o teste, porque nenhum dos boletins da Sala junta essa substância a uma cultura autorizada. E para o ARIF, onde a cultura é desconhecida, continua a dizer «não sei» — que é a resposta certa. Atenção: «passou» **não** é oportunidade. Faltam ainda duas peças (a região e a data do facto), e enquanto faltarem não há oportunidade nenhuma. O contador continua em zero, de propósito.

**6 · Esses 5 itens podem ser reprocessados pela Intelligence?**
Os cinco podem entrar; três trazem a cultura. O piloto já correu sobre a Sala inteira com a versão nova (versão 3): 46 itens, 5 boletins, 3 com cultura, 4 cruzamentos tentados, 2 bloqueados pela cultura, 2 impossíveis por cultura desconhecida, 0 oportunidades. Reprocessar com a versão antiga daria o resultado antigo; a versão mudou, e por isso o piloto obriga a reprocessar tudo — é assim que ele foi desenhado.

**O que não ficou feito, dito claro:** o ícone do ARIF só se lê com leitura de imagem, que esta casa não faz; o ARIF antigo sem ficheiro depende de quem cuida das fontes; e ligar o índice de gavetas à estrada automática de cada coleta nova é uma decisão que o brief mandou não tomar aqui.

**HARD STOP.**
