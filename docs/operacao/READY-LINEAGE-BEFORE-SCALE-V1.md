# A LINHAGEM DO READY, ANTES DA ESCALA

> **Missão:** `C-READY-LINEAGE-BEFORE-SCALE-V1`
> **Medição:** `provas/a_linhagem_do_ready.py` · `provas/mutacao_da_linhagem_do_ready.py`
> **Guardas sem banco:** `tests/test_a_linhagem_do_ready.py`
> **Lei alterada:** `COL-LAW-043` — 11 → **12** campos

---

## EM PORTUGUÊS FÁCIL — as cinco respostas

**1 · O READY agora consegue voltar ao arquivo bruto que o originou?**

**Sim.** O contrato passou a levar `RAW_OBSERVATION_ID`, que é `raw_asset.id` —
a identidade canônica da observação. Uma consulta, por id, um resultado.

**2 · Consegue chegar também ao Storage?**

**Sim, e sem segundo campo.** `raw_asset` já aponta para a cópia por chave
estrangeira **composta** `(storage_object_id, sha256)`. O armazém sai do mesmo
join. Duplicar `STORAGE_OBJECT_ID` no READY daria duas declarações do mesmo
parentesco, livres para divergir.

**3 · Essa ligação funciona mesmo com duas coletas parecidas e retries?**

**Sim, e foi atacada para se saber.** Duas observações com o **mesmo sha256**,
duas corridas da mesma fonte, um sha no lugar do id, um `storage_path` no lugar
do id, um `SOURCE_ID` no lugar do id, um bruto inexistente, um READY sem link —
sete ataques, nenhum passou. E o retry da mesma corrida continua a apontar para
a **mesma** observação, sem duplicar bruto nem cópia.

**4 · Precisamos colocar tipo/língua/relação do texto dentro do READY?**

**Não — e não porque não importem, mas porque não se perdem.**
`coleta/ingresso.py::_bytes_do_item` serializa o **item inteiro** como bytes da
observação, então as `TEXT_UNITS` ficam **dentro do bruto preservado**. Medido
dos bytes reais, pela mesma ponte: `NATIVE_CAPTION` · `ORIGINAL` · `it`.

> **NÃO VIAJAR ≠ PERDER-SE.**
> Mas «resolvível pela linhagem» só era verdade **depois** de a linhagem
> resolver. Antes desta missão, era uma frase.

**5 · Estamos liberados para o gate final da Big Collection?**

**Sim.** `READY_LINEAGE_FOR_SCALE = PASS` e `TEXT_METADATA_FOR_SCALE = PASS`.
Isto **não** inicia a Big Collection: libera a próxima missão de gate final.

---

## O QUE A MEDIÇÃO ENCONTROU — e era pior do que «partido»

O censo levantou a hipótese de que `READY` não sabia o seu RAW. Ele estava
certo, e a medição achou a forma exata do defeito.

Na rota forward, `READY.ITEM_ID` é o **`sha256` do texto derivado**
(`rota_forward_documento.py:467`). A única volta possível era procurar
`derived_artifact` por esse sha — e `derived_sha_idx` **não é único**. A
identidade de uma derivação é `derivacao_e_unica_por_regua`, sobre
`(parent_sha256, kind, producer, producer_version, parameters_hash,
serie_posicao)`. **Dois pais diferentes dão duas linhas legítimas.**

Medido contra PostgreSQL 16 com a cadeia canônica inteira — dois PDFs
diferentes cujo texto extraído é o mesmo:

```
procurar derived pelo sha do ITEM_ID:
    1 candidato  antes do gémeo existir
    2 candidatos depois
    → 2 derivados · 2 observações · 2 objetos de armazém
```

```
READY_TO_RAW (antes)   AMBIGUOUS
READY_TO_RAW (depois)  PROVEN
```

> **UMA CADEIA PARTIDA VÊ-SE. UMA QUE DEVOLVE DOIS CANDIDATOS PLAUSÍVEIS
> RESPONDE COM CONFIANÇA À PERGUNTA ERRADA.**

E a prova teve de **construir** o gémeo para o medir: na árvore limpa a procura
devolve 1 e pareceria suficiente.

> **UMA PONTE QUE ACERTA ENQUANTO HOUVER UM SÓ NÃO É UMA PONTE.**

⚠️ **E as duas rotas usavam chaves diferentes para `ITEM_ID`:** a rota forward o
`sha256` do derivado; o orquestrador `derived:<derived_artifact_id>`
(`orquestrador.py:533`). `ITEM_ID` nunca foi uma chave de linhagem confiável
entre rotas — e ninguém tinha medido isso.

---

## A CURA — um campo, e ele já estava em mãos

O valor **não** precisou de ser descoberto. As **duas** rotas canônicas já o
põem no item que entregam à porta:

```
coleta/rota_forward_documento.py:212   'raw_asset_id': unidade.get('RAW_ASSET_ID')
orquestrador/orquestrador.py:534       "raw_asset_id": estruturado.get("RAW_ASSET_ID")
```

E `admissao.pronto_para_inteligencia()` deitava-o fora, exatamente ali.

> **RUNTIME SABE ≠ O SISTEMA GUARDA** (know-how `§86.4`).
> **O QUE MORRE COM O PROCESSO NÃO É LINHAGEM.**

```
COL-LAW-043      11 → 12 campos, com RAW_OBSERVATION_ID
valor            raw_asset.id
ausente          NAO SEI — nunca derivado de sha, URL, path, filename ou RUN_ID
storage          NÃO viaja: sai do join canônico
texto            NÃO viaja: fica nos bytes do bruto
```

### Isto não é lei nova

`COL-LAW-033` **já exigia** linhagem de todo artefato, e já tinha escrito o
prazo:

> *«A PROCEDÊNCIA SÓ VALE SE FOR POSTA NA COLETA. Depois é tarde: o dado já
> entrou sem ela e ninguém recupera a origem.»*

Enquanto os dois textos divergiram, o `isto e mais nada` da `COL-LAW-043` venceu
na prática e a linhagem ficou de fora. A emenda resolve o conflito a favor da
lei que estava a ser violada.

```
BIBLE_CHANGE     = YES — COL-LAW-043 enumera os campos, e agora enumera 12
CONTRACT_CHANGE  = YES — 11 → 12
LEI_JA_EXIGIA    = YES — COL-LAW-033 (linhagem) e COL-LAW-008 (cadeia inversa)
```

### E por que só este id

```
READY → RAW_OBSERVATION_ID → raw_asset → storage_object → bytes
                                       → collection_run
                                       → source_id
```

**A MENOR IDENTIDADE QUE FECHA A ESTRADA É A CERTA.** Nenhuma tabela nova,
nenhum segundo ledger, nenhuma segunda identidade, nenhum lookup heurístico.
`participacao_na_derivacao` (029) continua a ser o dono de «que observações
participaram desta derivação» — esta ponte não o duplica nem o contradiz.

---

## A TABELA

| medida | valor |
|---|---|
| `FUNCTIONAL_HEAD_START` | `247fbf25958da5bb66a0316b43b73dc80c699d0b` |
| `FUNCTIONAL_HEAD_FINAL` | `247fbf25` — intocado; a missão vive na sua branch |
| `FUNCTIONAL_HEAD_DRIFT` | **NO** |
| `CENSUS_HEAD` · `KNOW_HOW_HEAD` | `b67e6f07` · `39e685fc` |
| | |
| `READY_FIELDS_BEFORE` / `AFTER` | **11 / 12** |
| | |
| `READY_TO_RAW` | **PASS** |
| `RAW_TO_STORAGE` | **PASS** |
| `READY_TO_STORAGE` | **PASS** |
| `READY_WRONG_RAW_MATCHES` | **0** |
| `READY_AMBIGUOUS_RAW_MATCHES` | **0** |
| `RUN_LINEAGE` · `SOURCE_LINEAGE` | **PASS** · **PASS** |
| | |
| `RAW_OBSERVATION_ID_FABRICATION` | **0** |
| `DOCUMENT_ID_FABRICATION` | **0** |
| `SOURCE_ID_FABRICATION` | **0** |
| | |
| `TEXT_KIND_AFTER_READY` | **RESOLVABLE_BY_LINEAGE** |
| `TEXT_RELATION_AFTER_READY` | **RESOLVABLE_BY_LINEAGE** |
| `LANGUAGE_AFTER_READY` | **RESOLVABLE_BY_LINEAGE** |
| `TEXT_METADATA_FOR_SCALE` | **PASS** |
| | |
| `READY_TO_RAW_AFTER_RETRY` | **PASS** |
| `RAW_DUPLICATION_ON_RETRY` | **0** |
| `STORAGE_DUPLICATION_ON_RETRY` | **0** |
| | |
| `JUDGMENT_DIFF_COUNT` | **0** — 129 decisões, 4 vereditos representados |
| | |
| `TESTS_BEFORE` / `TESTS_AFTER` | **3.867 / 3.880** (+13 guardas) |
| `FAILURES_BEFORE` / `AFTER` | **34 / 34** (conjunto idêntico, nome a nome) |
| `NEW_FAILURES` | **0** |
| `FIXED_FAILURES` · `DISAPPEARED_TESTS` | **0** · **0** |
| | |
| `RED_TEAM_ATTACKS` / `SURVIVORS` | **18 / 0** |
| `MUTANTS` / `MUTANT_SURVIVORS` | **5 / 0** (+1 contraprova no-op, sobreviveu) |
| | |
| `REAL_WAITING_ROOM_ITEMS_BEFORE` | **0** |
| `REAL_WAITING_ROOM_ITEMS_AFTER` | **0** |
| `REAL_WAITING_ROOM_ITEMS_CREATED` | **0** |
| | |
| `SYSTEM_MAP_PARALLEL_DRIFT` | duas peças declaradas · `SYSTEM_MAP_CHECK=PASS` |
| `LIVE_READS` / `LIVE_WRITES` | **0 / 0** |
| | |
| `READY_LINEAGE_FOR_SCALE` | **PASS** |
| `SCALE_GATE_READY_FOR_FINAL_CHECK` | **YES** |

---

## RED TEAM — 18 ataques, 0 sobreviventes

Sete correm dentro da prova, contra o banco. Onze são guardas de contrato e
de forma, e correm sem banco.

| # | ataque | como morre |
|---|---|---|
| 1 | READY aponta para RUN em vez de RAW | mutante M2 — morre em 10 casos |
| 2 | SHA usado como RAW id | `A3` recusa por forma · mutante M3 morre em 10 |
| 3 | `storage_path` usado como identidade | `A4` recusa |
| 4 | `SOURCE_ID` usado para escolher RAW | `A5` recusa |
| 5 | dois RAW com o mesmo SHA | `A1` — existem, e a ponte devolve 1 e 3 |
| 6 | duas corridas da mesma fonte | `A2` — 2 corridas distintas, não colapsam |
| 7 | READY sem link aceito como linhagem | `A7` recusa · `L1` diz `NAO SEI` |
| 8 | RAW inexistente | `A6` — 0 candidatos, e não o vizinho |
| 9 | RAW aponta para storage inexistente | `L5` exige o join e o sha a bater |
| 10 | storage com hash divergente | chave composta `(storage_object_id, sha256)` |
| 11 | retry muda READY para o RAW errado | `L11` — mesma observação depois do retry |
| 12 | social `NOT_APPLICABLE` como derivação em falta | `S2` — lê o motivo, não a ausência |
| 13 | `TEXT_KIND` preenchido por inferência | `S4` — vem do byte preservado |
| 14 | `LANGUAGE` herdado da publicação | `S6` — da unidade, nunca da publicação |
| 15 | `TEXT_RELATION` apagado | `S5` — `ORIGINAL` recuperado do bruto |
| 16 | consumer antigo quebra em silêncio | `READY_CONSUMER_COUNT = 0`, medido |
| 17 | READY com chave extra não versionada | 12 campos exatos, e a lei enumera-os |
| 18 | segunda tabela/ledger para conceito já possuído | zero migrations nesta missão |

### O mutante que tinha de sobreviver

`M6` é um comentário — um no-op de propósito. Ele **sobreviveu**, e é isso que
prova que a bateria não morre por qualquer mudança, só pelas que partem a ponte.

> **UMA BATERIA QUE MORRE COM TUDO NÃO ESTÁ A GUARDAR NADA.**

---

## O QUE ESTA MISSÃO NÃO FECHOU

**A rota SCRAP social não está integrada, e isso é medido, não suposto.**
`data/derivados/COLLECTION-V1-CLOSE-GATES.json` diz
`SCRAP.INTEGRATED = NO`. A rota que hoje leva uma observação social ao READY é
a de ingresso direto (`INGRESSO.PARA_A_PORTA`), e nela o item chega à porta
**sem** `raw_asset_id`: `DA_FICHA_PARA_A_PORTA` exclui `RAW_OBSERVATION_ID` de
propósito, porque a ficha é montada **antes** de o banco cunhar o id.

Nessa rota, `RAW_OBSERVATION_ID` sai `NAO SEI` — honestamente.

**E não foi ligada por correlação**, porque as correlações disponíveis seriam
todas proibidas: por `sha256` (bytes, não observação), por `storage_path`
(endereço, não identidade) ou por posição na lista. A observação confirmada
existe e carrega o id — `SEM_BYTES_PARA_DERIVAR[].RAW_ASSET_ID`, provado em
`S3` — mas ligá-la ao item aceito exige uma ponte no ingresso, e essa é uma
missão de código própria.

```
ROTA DOCUMENTAL (canônica, provada)   READY_TO_RAW = PASS
ROTA SOCIAL POR INGRESSO DIRETO       RAW_OBSERVATION_ID = NAO SEI
```

> **UMA PONTE QUE EU NÃO CONSIGO CONSTRUIR SEM HEURÍSTICA NÃO SE CONSTRÓI
> COM HEURÍSTICA.**

Isto **não** bloqueia a escala da rota canônica — ela atravessa e resolve. Fica
nomeado porque o dia em que o SCRAP for integrado é o dia em que esta ponte tem
de existir, e a `COL-LAW-033` já diz que depois é tarde.

---

## KNOW-HOW

```
KNOW_HOW_HEAD (início)  = 39e685fc
KNOW_HOW_HEAD (fim)     = 0de9dd95   ·  claude/sintonia-eame-know-how-v1
KNOW_HOW_DRIFT          = YES — durante esta missão
KNOW_HOW_DELTA          = ATUALIZAÇÃO NECESSÁRIA
```

⚠️ **O know-how andou enquanto esta missão corria**, e o que entrou toca-lhe
directamente: `know-how/daily/2026-09-13-ready-address-and-admission-correction.md`.
Foi lido antes de fechar. Ele **confirma** o desenho — *«`RAW_OBSERVATION_ID`
existe e é canonicamente `raw_asset.id`»* — e deixa duas linhas que esta missão
acabou de mover:

1. Ele escreve **«11 campos fixos conforme `COL-LAW-043`»**. Passaram a ser
   **12**. A linha ficou stale pelo commit desta missão, e não por idade.
2. Ele trata `G-READY-02` como *«decisão arquitetural em aberto»* entre ficheiro
   e armazenamento transacional. `docs/decisoes/ADR-SALA-DE-ESPERA-V1.md` já
   decidiu **FILESYSTEM**, e o censo anterior mediu a morada com **um** dono.
   Quem reabrir a pergunta reabre-a contra o ADR, não contra o vazio.

E a lição que ele próprio registou vale nos dois sentidos, incluindo contra
este relatório:

> *«UM RELATÓRIO DE GOVERNANÇA PODE ENVELHECER ENQUANTO A LINHA FUNCIONAL
> CONTINUA A EVOLUIR; PARA ESTADO ATUAL, REMEDIR A LINHA FUNCIONAL.»*

⚠️ **E a primeira lição é sobre o censo anterior, que estava errado.** Ele
declarou `KNOW_HOW_HEAD = não está neste repositório` — porque procurou em
`origin/main` e na linha funcional, e não na branch canônica do know-how. O
documento existe, tem **12.510 linhas** e vai até ao `§108`; a branch tem 1.582
ficheiros e uma pasta `know-how/` inteira.

> **FONTE DE VERDADE EM BRANCH CANÔNICA NÃO É AUSÊNCIA SÓ POR NÃO ESTAR NO
> HEAD FUNCIONAL.**
> E `§86.2` já ensinava a forma do erro — *«PROCURAR O DONO NA MINHA MEMÓRIA
> NÃO É PROCURAR»* — para tabelas. Vale para branches.

Lições duráveis novas, e nenhuma delas é um número:

1. **`AMBIGUOUS` é pior do que `BROKEN`.** Uma cadeia partida vê-se; uma que
   devolve dois candidatos legítimos responde com confiança à pergunta errada.
   E **uma ponte que acerta enquanto houver um só não é uma ponte** — por isso a
   prova constrói o gémeo antes de medir.
2. **`NÃO VIAJAR ≠ PERDER-SE`** — mas «resolvível pela linhagem» só é verdade
   depois de a linhagem resolver. Antes, é uma frase que dispensa a prova.
3. O `§104.6` disse *«texto que atravessa fronteira viaja com a espécie, ou não
   viaja»*. Há uma terceira saída, e é esta: **fica preservado no bruto, e
   resolve-se pelo id da observação.**

O `§13`/`LOTE 05` já registava *«READY não carrega parent lineage completo»* —
o **achado** não é novo; o **fecho** é. Nada foi escrito na branch do know-how:
ela é paralela, e a missão declara o delta, não o funde.

---

## VEREDITO

```
READY_LINEAGE_FOR_SCALE          = PASS
TEXT_METADATA_FOR_SCALE          = PASS
SCALE_GATE_READY_FOR_FINAL_CHECK = YES
```

### RESIDUAL_RISKS

1. **A rota social por ingresso direto não nomeia a observação** (acima). O
   campo diz `NAO SEI`, e a próxima missão de integração do SCRAP tem de o
   fechar **antes** do volume.
2. **`LINEAGE_FULL` de um item pousado depende do banco estar ao lado.** A ponte
   é um id; resolver exige `raw_asset`. Um READY exportado sozinho continua a
   saber **de quem** veio, e não **o quê** era o byte.
3. **A `008` fica fora da cadeia aplicada** nas provas — ela confere, e o
   ambiente descartável aplica 29 das 30 migrations. Herdado, não introduzido.
4. **`pdftotext` teve de ser instalado neste ambiente** para a travessia real
   correr. A baseline de regressão foi **re-medida depois** disso, no mesmo
   ambiente, para a comparação ser justa — e é por isso que o número de falhas
   base (34) não bate com o do censo anterior (18): lá, 3 provas saltavam.

> **SKIP ≠ PASS, E UMA BASELINE MEDIDA NOUTRO AMBIENTE NÃO É UMA BASELINE.**

---

## HARD STOP

Big Collection não começou. Intelligence não foi chamada. A Sala real continua
vazia — todas as provas usam morada descartável. LIVE não foi tocado. Nenhuma
migration foi criada. Nenhuma tabela nova.

**A decisão volta ao coordenador.**
