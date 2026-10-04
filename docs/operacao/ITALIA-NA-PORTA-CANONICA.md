# A ITÁLIA ENTRA NA PORTA CANÓNICA — o encaixe do coletor (B1)

**C-PLAN-B1 · 2026-09-10 · ramo `claude/raw-observation-identity-3jbwco`**

> **Nada foi implementado.** Zero runtime, zero `receitas.py`, zero orquestrador, zero
> `italy_pilot_collect.mjs`, zero `ingresso.py`, zero banco, zero migration, zero T-32, zero
> Admission, zero READY, zero System Map, zero Bíblia.

```
LOCAL_HEAD = REMOTE_HEAD = ea7a95b1dcaff06724c89e2de979b5e8e9123252
WORKTREE   = limpa   ·   DIVERGENCE = 0
```

---

## 1 · OS CONTRATOS, MEDIDOS

```
EXECUTOR_REGISTRY_CURRENT_CONTRACT     pedido/receitas.py::EXECUTORES
  { universo: [ { id, roda:[argv], larga_em:[paths], rotas, o_que_traz, custo,
                  argumentos_de_filtros?, filtros_por_omissao? } ] }

ORCHESTRATOR_EXPECTED_EXECUTOR_CALL    orquestrador.py:248
  subprocess.run([sys.executable, *comando], cwd=RAIZ, timeout=1800)

EXECUTOR_EXPECTED_RETURN_SHAPE         nenhum. O executor NÃO devolve — ele LARGA.
  a_colheita(e) lê `larga_em`:  alvo.glob("*.json") se pasta, senão [alvo]
  de cada ficheiro: uma lista, ou o primeiro campo que seja lista de dicts

INGRESSO_RECEBER_EXPECTED_INPUT        ingresso.receber(itens, corrida=…, armazem=…, raiz=…)
  itens    lista de dicts. `ficha()` usa item["STORAGE_LOCATION"] ou item["_de"];
           se o ficheiro existe, PRESERVA OS BYTES DELE.
           Transporta 13 campos declarados (DO_COLETOR): SOURCE_ID · SOURCE_URL ·
           PUBLISHER · COUNTRY_SCOPE · SOURCE_LOCATION · FACT_LOCATION ·
           ITEM_LANGUAGE · FACT_TIME · PUBLISHED_AT · OBSERVED_AT ·
           EXECUTOR_ID · EXECUTOR_VERSION · PIPELINE_VERSION
  corrida  RUN_ID + (PLATFORM, ACTOR, ACTOR_VERSION, RULE_VERSION,
           SOURCE_COUNTRY, STARTED_AT) — o que faltar vira NOT_PRESERVED

ITALY_COLLECTOR_CURRENT_CALL_SIGNATURE  node coleta/italy_pilot_collect.mjs [--dry|--negativos]
ITALY_COLLECTOR_CURRENT_OUTPUT          NDJSON append-only no livro + bytes em
                                        data/collection-store/italy/…
```

---

## 2 · ONDE AS FORMAS NÃO ENCAIXAM — cinco desencontros e duas armadilhas

| # | o desencontro | medido em |
|---|---|---|
| **I1** | o orquestrador corre `[sys.executable, *comando]` — **interpretador Python fixo**. O coletor é `.mjs`, corre em Node | `orquestrador.py:248` |
| **I2** | a colheita lê `glob("*.json")` e faz `json.loads` do ficheiro inteiro. O livro é **NDJSON** | `orquestrador.py:84` |
| **I3** | o livro é **append-only e guarda 6 corridas**. A colheita traria as **144** observações, não as desta corrida | livro: 144 linhas, 6 `RUN_ID` |
| **I4** | **a identidade da corrida nasce DEPOIS do executor correr**: `subprocess.run` na linha 248, `novo_run_id(p)` na 256. E o coletor mint a sua própria | `orquestrador.py:248` e `:256` |
| **I5** | `pela_entrada` **não passa `memoria=`**. Sem banco, `preservar()` não escreve `raw_asset` — o próprio recibo diz `"NAO MEDIDO — sem banco ligado"` | `orquestrador.py:116-117` |

E duas armadilhas que só aparecem quando se liga o cabo:

| # | a armadilha | consequência se não for tratada |
|---|---|---|
| **T1** | o orquestrador faz `x.setdefault("_de", <ficheiro lido>)`, e `ficha()` usa `STORAGE_LOCATION` **ou** `_de`. Sem `STORAGE_LOCATION`, os bytes preservados seriam **os do próprio livro** | as 144 observações partilhariam um sha — o do ledger |
| **T2** | `RAW_PATH` é `null` em **109 de 144** (as `SEEN_AGAIN`): o coletor nem chama `guardarRaw` quando reencontra | sem caminho, `ficha()` preservaria o **JSON da observação** em vez do documento |

> ## O `I4` É O MAIS FUNDO, E ACUSA A NOSSA PRÓPRIA CASA.
> A lei está escrita no comentário de `collection_run`: *«PROVENIÊNCIA É PROSPECTIVA: não se
> preenche elo de execução passada.»* E o orquestrador mint o `RUN_ID` **oito linhas depois**
> de o executor já ter corrido. **Não é culpa do coletor italiano.**

---

## 3 · O PAPEL DO COLETOR

```
ITALY_COLLECTOR_ROLE = EXECUTOR
```

Ele busca, valida bytes antes de qualquer parse, preserva no seu armazém e escreve um
recibo. É a forma de um executor, e a casa já tem executores em `.mjs`.

O que ele **não** pode fazer, e uma coisa que ele **faz hoje e terá de deixar de fazer**:

```
não escolhe quando correr · não decide universo · não escolhe a próxima fonte
não chama Admission · não chama READY · não orquestra outros executores
✖ HOJE ELE MINT O PRÓPRIO RUN_ID  (italy_pilot_collect.mjs:266)  →  passa a RECEBER
```

---

## 4 · QUEM O CHAMA — os dois «?» fechados

```
T-04  orquestrador/orquestrador.py::correr
  ↓   mint o RUN_ID canónico ANTES de correr o executor  (corrige I4)
T-06  pedido/receitas.py::EXECUTORES  resolve o executor
  ↓
 ➊  coleta/italy_executor.py          ← O ADAPTER  (o primeiro «?»)
  ↓   corre o coletor e traduz a saída
     coleta/italy_pilot_collect.mjs
  ↓
 ➋  larga_em: a colheita DESTA corrida, em JSON, na língua da porta  (o segundo «?»)
  ↓
     coleta/ingresso.py::receber
  ↓
     guarda/preservar_coleta.py::preservar   ← único writer RAW
  ↓
     collection_run  +  raw_asset
```

Os dois «?» são **um ficheiro e um ficheiro de saída**. Nenhum componente novo de
orquestração nasce.

---

## 5 · O REGISTO E O ADAPTER

```
ITALY_EXECUTOR_ADAPTER_REQUIRED = YES
```

**Porquê**: sem adapter, o `I1` sozinho já impede (Python a correr Node), e o `I2`/`I3`
entregariam zero itens ou 144. Um adapter escrito em Python resolve os três **sem tocar no
contrato do registo e sem tocar no coletor**.

```
ITALY_EXECUTOR_REGISTRY_ENTRY_TARGET

  EXECUTORES["T2"] += [{
      id: "italia-recorrente",
      roda: ["coleta/italy_executor.py"],          ← Python, logo sys.executable serve
      larga_em: ["data/colheita/italia/"],         ← pasta de colheita POR CORRIDA
      argumentos_de_filtros: ["fonte"],            ← precedente: T9 já usa este campo
      filtros_por_omissao: {fonte: "IT-T2-002"},
      rotas: ["HTTP direto"], custo: "gratuito",
      o_que_traz: "o boletim agrometeorológico da zona, como PDF, com a versão do documento"
  }]

ADAPTER_OWNER_TARGET = coleta/italy_executor.py
```

⚠️ **Um executor, sete fontes, vários universos.** O coletor cobre `IT-T2-002` (T2),
`IT-T3-002/005/008/010` (T3) e `IT-T4-001` (T4), e `EXECUTORES` é indexado por **universo**.
Para o primeiro slice regista-se **numa entrada só, com filtro de fonte**, exactamente como
a A5.2 recomendou (`IT-T2-002` sozinha). **Como um executor multi-universo se declara é
pergunta do registo (T-06), não do B1** — e fica registada, não resolvida.

```
ADAPTER_MINIMUM_RESPONSIBILITY   quatro traduções, e nada mais

  1  corre o coletor em Node, com o RUN_ID recebido           (I1, I4)
  2  lê do livro APENAS as observações desta corrida           (I3)
  3  converte NDJSON → uma lista JSON na pasta de colheita     (I2)
  4  renomeia RAW_PATH → STORAGE_LOCATION                      (T1, T2)

  E NÃO PODE inventar: SOURCE_ID · DOCUMENT_ID · DOCUMENT_VERSION_ID · RUN_ID
                       sha256 · captured_at
```

Tradução de nome e de forma é o que um adapter faz. **Preencher um campo que a observação
não trouxe é outra coisa, e está proibido.**

---

## 6 · A COLHEITA ITALIANA PODE ALIMENTAR A PORTA DIRECTAMENTE?

```
CAN_CURRENT_ITALY_OUTPUT_FEED_INGRESSO_DIRECTLY = NO
```

Por `I2` (NDJSON), `I3` (todas as corridas) e `T1`/`T2` (bytes errados). O conteúdo
semântico, esse, **já é suficiente**: dos 13 campos que a porta transporta, a observação já
traz `SOURCE_ID`, `SOURCE_URL` e `FACT_TIME`, e o resto fica `NÃO SEI` — que é a resposta
honesta, não um buraco.

⚠️ **Medido e registado para depois:** `DO_COLETOR` **não** transporta `DOCUMENT_ID` nem
`DOCUMENT_VERSION_ID`. A porta deixa cair a identidade documental. **Não é bloqueio do B1**
— o B1 termina em `raw_asset` — mas é dependência da ponte (A5.5).

---

## 7 · A CORRIDA CANÓNICA

```
COLLECTION_RUN_CREATOR_TARGET

  a IDENTIDADE   T-04, orquestrador/orquestrador.py::correr, ANTES de correr o executor
  a LINHA        guarda/preservar_coleta.py, que já escreve
                 `insert into public.collection_run (…) values (…, 'rodando')`
```

**Dois papéis, um dono cada, e nenhuma sobreposição.** O T-04 diz qual é a corrida; o dono do
RAW escreve a linha e é o único que o faz. Nenhuma outra camada abre corrida.

```
ITALY_RUN_ID_CAN_BE_CANONICAL_RUN_ID = NO
```

**E não é por formato** — `collection_run.run_id` é `text` livre, e `PILOT_RUN_…` caberia.
É por **propriedade**: se o coletor mint o identificador, a corrida passa a existir antes de
o T-04 saber dela, e duas camadas passam a ser donas da mesma corrida. É exactamente o que a
missão proíbe, e é o que a lei já dizia.

**Nenhuma tradução silenciosa entre dois IDs.** O coletor deixa de gerar e passa a receber.

---

## 8 · UMA ÚNICA ENTRADA RAW

```
ITALY_RAW_WRITER_TARGET = guarda/preservar_coleta.py
```

Confirmado, e já há guarda a correr que o protege:

```
provas/o_encanamento_tem_uma_porta.py
  P2  a porta delega ao dono do raw e NÃO conhece a tabela
  P3  NENHUM COLETOR PRESERVA POR FORA — um coletor que chame preservar() ou
      enderece o armazém sozinho abre uma segunda entrada
```

`italy collector → raw_asset` directo: **proibido**. Segundo writer RAW: **proibido**. O
coletor continua a guardar bytes no seu armazém local, e isso **não é escrever RAW** — é o
que a porta vai ler.

E há um sexto passo que o `I5` obriga: **`pela_entrada` tem de passar `memoria=`**. Sem
banco ligado, tudo o resto encaixa e `raw_asset` continua a zero. O próprio ficheiro já
prevê: *«Quando houver banco, ele entra por `memoria=` sem esta função mudar.»*

---

## 9 · DEPENDÊNCIAS

```
B1_DEPENDS_ON_B3 = NO
```

Os dois armazéns **não competem no B1** — eles cooperam, e em sentidos opostos:

```
data/collection-store/italy/…   é de ONDE a porta LÊ os bytes  (ficha → raw_do_disco)
o armazém do dono do RAW        é para ONDE ele os ESCREVE, com o seu próprio esquema
                                (caminho_do_objeto: PAIS/FONTE/TIPO/sha16-nativo-nome)
```

Um é origem, o outro é destino. **Decidir qual sobrevive é o B3**, e o B1 fecha sem essa
decisão.

```
B1_DEPENDS_ON_RAW_ID_RETURN = NO
```

O B1 termina quando a linha existe. **Ler o `id` de volta é o B4**, e a leitura já tem porta
(`memoria.objeto_em`).

```
B1_IMPLIES_HISTORICAL_BACKFILL = NO
```

Esta missão é sobre **a rota nova**. As 144 observações antigas ficam onde estão. Fazer a
rota funcionar e reconstruir história são dois trabalhos, e misturá-los faria o teste do
primeiro depender do sucesso do segundo.

---

## 10 · A PROVA QUE A IMPLEMENTAÇÃO DO B1 TERÁ DE PASSAR

```
FUTURE_B1_TEST_FIXTURE

  fonte      IT-T2-002  (ARPAV Veneto — autorizada pela A5.2)
  documento  ARPAV:Z01:20260903160930 · v1_f88c89d73d6a
  bytes      data/collection-store/italy/IT-T2-002/ARPAV_Z01_20260903160930/…/agro_01.pdf
             (463 630 bytes, presente na árvore)
  modo       o coletor tem `--dry` — «usa so o que ja esta no disco».
             A prova corre OFFLINE, sem rede e sem gastar nada.
  banco      descartável (guarda/memoria_descartavel.py), como em toda esta série
```

```
FUTURE_B1_SUCCESS_CRITERIA

  1  T-04 mint o RUN_ID ANTES de chamar o executor, e passa-o
  2  T-06 resolve `italia-recorrente` a partir do pedido
  3  o adapter corre o coletor e larga a colheita DESTA corrida — nem 0, nem 144
  4  ingresso.receber recebe os itens com STORAGE_LOCATION a apontar para o PDF
     — e o sha preservado é o do PDF, NUNCA o do livro                   (mata T1)
  5  preservar_coleta é o ÚNICO writer RAW da prova
  6  collection_run existe, com o RUN_ID do T-04
  7  raw_asset existe, com o sha256 f88c89d73d6a… e o tamanho 463630

  E SEGUNDA EXECUÇÃO do mesmo caso:
  8  não nasce duplicata falsa
  9  o captured_at da primeira observação NÃO muda
  10 continua a haver um único writer RAW

  E o que a prova NÃO toca: T-32 · SOURCE_DOCUMENT · Admission · READY
```

Os pontos 8 a 10 não redesenham nada: são as leis já fechadas pela C-PLAN-0 aplicadas a esta
prova.

---

## 11 · ENTREGA

| | |
|---|---|
| **A** `BRANCH` | `claude/raw-observation-identity-3jbwco` |
| **B** `INITIAL_HEAD` | `ea7a95b1dcaff06724c89e2de979b5e8e9123252` |
| **D** `WORKTREE` | limpa |
| **E** `ITALY_COLLECTOR_ROLE` | **EXECUTOR** — e deixa de mint o próprio `RUN_ID` |
| **F** `EXECUTOR_REGISTRY_CURRENT_CONTRACT` | `{universo: [{id, roda, larga_em, rotas, o_que_traz, custo, …}]}` · corrido com `sys.executable` |
| **G** `ITALY_EXECUTOR_REGISTRY_ENTRY_TARGET` | uma entrada em `EXECUTORES["T2"]`, com filtro de fonte |
| **H** `ITALY_EXECUTOR_ADAPTER_REQUIRED` | **YES** |
| **I** `ADAPTER_OWNER_TARGET` | `coleta/italy_executor.py` |
| **J** `ADAPTER_MINIMUM_RESPONSIBILITY` | 4 traduções: Node · âmbito da corrida · NDJSON→JSON · `RAW_PATH`→`STORAGE_LOCATION`. Nada mais |
| **K** `CAN_CURRENT_ITALY_OUTPUT_FEED_INGRESSO_DIRECTLY` | **NO** |
| **L** `INGRESSO_EXPECTED_INPUT` | lista de dicts com `STORAGE_LOCATION` + os 13 de `DO_COLETOR`; `corrida` com `RUN_ID` e 6 campos |
| **M** `COLLECTION_RUN_CREATOR_TARGET` | identidade: **T-04**, antes do executor · linha: **`preservar_coleta`** |
| **N** `ITALY_RUN_ID_CAN_BE_CANONICAL_RUN_ID` | **NO** — por propriedade, não por formato |
| **O** `ITALY_RAW_WRITER_TARGET` | **`guarda/preservar_coleta.py`**, único |
| **P** `B1_DEPENDS_ON_B3` | **NO** — um armazém é origem, o outro é destino |
| **Q** `B1_DEPENDS_ON_RAW_ID_RETURN` | **NO** — é o B4 |
| **R** `B1_IMPLIES_HISTORICAL_BACKFILL` | **NO** |
| **S** `FUTURE_B1_TEST_FIXTURE` | `IT-T2-002` · `ARPAV:Z01:20260903160930`, offline com `--dry` |
| **T** `FUTURE_B1_SUCCESS_CRITERIA` | 7 critérios + 3 de segunda execução |
| **U** `RUNTIME_FILES_CHANGED` | **0** |
| **V** `DATABASE_MUTATIONS` | **0** |
| **W** `SYSTEM_MAP_CHANGED` | **0** |
| **X** `BIBLE_CHANGED` | **0** |
| **Y** `UNRESOLVED_CRITICAL_B1_QUESTIONS` | **0** |

```
READY_FOR_B1_RUNTIME_IMPLEMENTATION = YES
```

### O que continua `NÃO SEI` — e nenhum bloqueia o B1

1. Como um executor **multi-universo** se declara no registo (T-06) — o slice usa uma fonte.
2. Se `DO_COLETOR` ganha `DOCUMENT_ID`/`DOCUMENT_VERSION_ID` — dependência da **ponte**, não do B1.
3. Qual dos dois armazéns sobrevive — **B3**.

---

## 12 · VEREDITO

```
ITALY_EXECUTOR_ROLE        = CLOSED   EXECUTOR
ITALY_REGISTRY_ENTRY       = CLOSED   EXECUTORES["T2"], com filtro de fonte
ITALY_ADAPTER_REQUIREMENT  = CLOSED   YES · coleta/italy_executor.py · 4 traduções
ITALY_TO_INGRESS_CONTRACT  = CLOSED   lista JSON, STORAGE_LOCATION a apontar para o PDF
CANONICAL_RUN_OWNERSHIP    = CLOSED   T-04 mint antes · preservar_coleta escreve
RAW_WRITER                 = CLOSED   preservar_coleta, único
B1_DEPENDENCIES            = CLOSED   não depende do B3 nem do B4 nem de backfill

C-PLAN-B1 = PASS
```

Um programador implementa a rota **sem decidir outra vez** quem chama, quem adapta, que
contrato atravessa, quem cria a corrida e quem é o único writer RAW.

---

## 13 · EM PALAVRAS FÁCEIS

1. **Por que a coleta italiana está fora?** Porque nunca foi inscrita na lista de executores.
   Quem manda correr só corre o que está na lista, e ela não está — por isso a porta nunca vê
   o que ela colhe.

2. **Onde precisa ser conectada?** Na porta de entrada, `ingresso.receber`, que é por onde
   toda a coleta desta casa entra.

3. **Quem manda ela rodar?** O orquestrador, depois de perguntar ao registo qual executor
   serve aquele pedido.

4. **Precisa de adaptador?** Precisa. O orquestrador corre Python e o coletor é Node; o livro
   é NDJSON e guarda seis corridas juntas; e o caminho dos bytes tem outro nome. São quatro
   traduções, e um ficheiro em Python resolve as quatro.

5. **Quem cria a corrida?** O orquestrador decide qual é, **antes** de correr o coletor — e
   hoje ele decide depois, o que é a coisa mais errada que encontrei aqui. Quem escreve a
   linha no banco continua a ser o dono do RAW.

6. **Quem guarda o RAW?** `preservar_coleta`, e mais ninguém. Já há guarda a reprovar
   qualquer coletor que tente guardar por fora.

7. **Precisamos resolver os dois armazéns agora?** Não. Um é de onde se lê, o outro é para
   onde se escreve. Escolher qual sobrevive é outra missão.

8. **Precisamos do retorno do identificador?** Não. O B1 acaba quando a linha existe.

9. **Precisamos importar as 144 antigas?** Não. Fazer a rota nova andar e reconstruir
   história são dois trabalhos.

10. **A próxima missão já pode programar?** Pode. Nada ficou por decidir — e há uma prova
    definida que corre offline, sobre um PDF que já está na árvore.

> **HARD STOP.** Papel, registo, adapter, contrato, corrida, writer e dependências fechados.
> Não se implementa o B1.
