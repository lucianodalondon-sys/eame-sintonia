# ADR — A PARTICIPAÇÃO NUMA DERIVAÇÃO PRECISA DE LINHA PRÓPRIA

**Data:** 2026-09-12 · **Estado:** DECIDIDO, NÃO IMPLEMENTADO
**Missões:** `C-DECIDE-DERIVED-REUSE-LINEAGE-V1` (mediu o buraco) ·
`C-DECIDE-DERIVED-PARTICIPATION-GRAIN-V1` (fechou o conceito e a identidade)
**Medição:** [`provas/a_linhagem_do_reaproveitamento.py`](../../provas/a_linhagem_do_reaproveitamento.py)
**Artefato:** `system-map/data/linhagem.observada.json`

> Nada foi implementado: não há migration nova, não há tabela nova, não há
> coluna nova, e nenhum writer produtivo mudou.
>
> O que mudou é que **já não falta decidir nada** para a escrever — a
> secção 7.10 lista as dez perguntas fechadas.

---

## 1 · A PERGUNTA

Quando duas observações diferentes têm os **mesmos bytes** e a mesma receita
reaproveita um único `derived_artifact`, o que fica escrito a dizer que a
segunda observação participou daquela derivação?

---

## 2 · O QUE JÁ ESTAVA DECIDIDO, E NÃO SE REABRE

A migration `022` fixou o grão do derivado e escreveu o porquê:

```
DERIVED_ARTIFACT grain = CONTEÚDO POR RECEITA
duas capturas dos mesmos bytes + mesma receita = UMA linha
```

E a assimetria é deliberada: em `raw_asset` o grão é a **ocorrência**, porque
duas capturas são dois factos sobre o mundo; no derivado não há dois factos,
há um — a nossa ferramenta, sobre estes bytes, com esta régua, dá este
resultado.

**Essa decisão está certa e fica.** O que esta ADR mede é a frase que ela
deixou ao lado.

---

## 3 · A FRASE QUE NÃO SE SUSTENTA

A `022` escreveu, sobre as capturas irmãs:

> «E A PROCEDÊNCIA DA CAPTURA NÃO SE PERDE... Todas as irmãs encontram-se com
> `select * from raw_asset where sha256 = <parent_sha256>`»

Essa consulta responde **«que observações têm os mesmos bytes»**. Não responde
**«que observações passaram por esta derivação»**.

```
    CAN INFER ≠ OBSERVED EDGE.
    TER OS MESMOS BYTES NÃO É TER PARTICIPADO DA MESMA EXECUÇÃO.
```

Medido: para o derivado `1`, a consulta devolve as observações `[3, 7]` — e as
duas chegam **iguais**. Uma foi lida e derivada; a outra pode ter sido derivada
e reaproveitada, ou pode nunca ter sido processada. A consulta não as separa,
porque não é sobre isso que ela pergunta.

---

## 4 · O QUE FOI MEDIDO

Estado construído pela rota REAL, com o executor real a ir à fonte real, em
PostgreSQL descartável: duas corridas da mesma fonte, oito observações, quatro
conteúdos, quatro derivados.

| pergunta | resposta |
|---|---|
| A · o derivado prova de qual cópia nasceu? | **SIM** |
| A2 · e o parentesco é travado pelo banco? | **SIM** — chave estrangeira composta |
| B · há relação persistida dizendo que a observação de B usou X? | **NÃO** |
| C · sem inferir por SHA, sobra alguma coisa? | **NÃO** |
| D · o ledger nomeia quais observações foram reaproveitadas? | **NÃO** |

A busca de B **não foi por memória**: foi pelo catálogo do próprio Postgres,
que sabe que colunas apontam para cada tabela.

```
UM CENSO ESTÁ CERTO DENTRO DO UNIVERSO QUE DECLARA.
```

Dez tabelas apontam para `raw_asset`. **Nenhuma tabela do esquema inteiro
aponta para `derived_artifact`.** Não há ponte porque não há nada do outro
lado da ponte.

### 4.1 · A aritmética da corrida homogénea não é uma aresta

Na corrida B o ledger diz `input_count=4` e `reused=4`. Daí **deduz-se** que as
quatro observações de B foram reaproveitadas — e a dedução funciona porque
todos os itens caíram no mesmo balde.

Medido no caso misto: a mesma passagem devolveu `{ERROR: 1, REUSED: 1}` para
duas observações. A linha guarda os números e não os nomes, e as duas leituras
possíveis são simétricas.

```
    CONTAGEM POR ETAPA ≠ DESTINO POR ITEM.
```

E a única coluna de observação que o ledger tem — `raw_asset_id`, da `028` — é
**proibida** fora da etapa RAW, por `check` declarativo. Não é uma ponte por
acaso: é uma ponte deliberadamente fechada.

### 4.2 · O runtime sabe, e não escreve

`guarda/preservar_derivado.py`, no reencontro, devolve os **dois lados da
aresta**:

```
TESTEMUNHA_NO_BANCO       o raw_asset que a linha existente nomeia   (A)
TESTEMUNHA_DESTA_CHAMADA  o raw_asset que esta passagem trouxe        (B)
```

Ele distingue os dois casos de reencontro por escrito, em prosa, na explicação
que devolve. E não persiste nenhum deles.

```
    RUNTIME SABE ≠ O SISTEMA GUARDA.
    O QUE MORRE COM O PROCESSO NÃO É LINHAGEM.
```

**Este é o achado.** Não falta descobrir a aresta: ela é calculada, nomeada, e
deitada fora.

---

## 5 · VEREDITO

```
DERIVED_REUSE_LINEAGE = GAP_CONFIRMED
DURABLE_EDGE_A_TO_X   = YES
DURABLE_EDGE_B_TO_X   = NO
```

---

## 6 · AS OPÇÕES DO OBJETO MATERIAL, MEDIDAS

> Primeira pergunta: **duplica-se o derivado por observação?**
> A segunda — que grão tem a relação — está na secção 6B.

### A · um `derived_artifact` por observação

| | |
|---|---|
| OWNER | `guarda/preservar_derivado.py` + alteração de `derived_artifact` |
| GRAIN | observação × receita |
| IDENTITY | `raw_asset_id` teria de entrar em `derivacao_e_unica_por_regua` |
| PROVENANCE | resolvida |
| RETRY | inalterada |
| REUSE | deixa de existir: passa a inserir sempre |
| CONCURRENCY | inalterada |
| COST | **duplica bytes** — `storage_path` é `UNIQUE` e nasce da receita, logo dois blobs idênticos em dois endereços |
| MIGRATION_IMPACT | chave nova, backfill, duplicação material |
| LIVE_IMPACT | nenhum hoje |
| LAW_COMPATIBILITY | **contradiz a `022`**, que decidiu o contrário com a razão escrita |

**Rejeitada.** Duplicar o material para facilitar uma consulta é pagar em bytes
o que se devia registar numa linha. E reabre uma decisão que não apresentou
defeito.

### B · manter o derivado único e criar a relação de participação

| | |
|---|---|
| OWNER | `guarda/preservar_derivado.py` — já calcula os dois lados |
| GRAIN | **uma linha por participação material**: (observação, derivado) |
| IDENTITY | chave natural `(raw_asset_id, derived_artifact_id)` — sem surrogate |
| PROVENANCE | a corrida da passagem que a viu primeiro, **fora da chave**; o resultado não mora aqui — ver 7.5 |
| RETRY | idempotente por `on conflict do nothing` sobre a chave natural |
| REUSE | é exactamente o caso que ela existe para registar |
| CONCURRENCY | a chave única resolve a corrida, como já faz `REUSED_AFTER_RACE` |
| COST | uma linha pequena por observação derivada; **zero bytes duplicados** |
| MIGRATION_IMPACT | **aditivo** — tabela nova, nenhuma coluna alterada, nenhum dado movido |
| LIVE_IMPACT | nenhum; a `022` também nunca foi executada em produção |
| LAW_COMPATIBILITY | `COL-LAW-008` continua satisfeita e fica mais forte; `022` fica intacta |

### C · usar estrutura existente

**Não existe.** Medido pelo catálogo: nenhuma tabela liga os dois.

⚠️ E há um falso amigo que tem de ficar nomeado. `public.derivacao_observacao`,
da migration `005`, **parece** a resposta e é outra espécie: ela liga
`public.derivacao` (uma *conclusão analítica*, com pergunta, resposta, estado e
limitação) a `public.observacao` (um *facto medido com denominador*, numa
camada FIELD/SCIENCE/VOICE/...). Nada disso é `raw_asset` nem
`derived_artifact`.

```
    DOIS NOMES IGUAIS EM CAMADAS DIFERENTES SÃO DOIS CONCEITOS.
    USAR UM PELO OUTRO PORQUE O NOME BATE É O PIOR TIPO DE REUSO.
```

### D · outras consideradas, e por que caíram

- **`derived_artifact_id` em `etapa_da_corrida`, relaxando o `check` da `028`.**
  O grão do ledger é a **passagem**, uma linha por `(run_id, etapa, tentativa)`.
  Ele não tem onde pôr N pares. Fazê-lo caber mudaria o grão dele — e
  telemetria não é material de linhagem.
- **Um array de observações em `derived_artifact`.** Arrays não têm integridade
  referencial, e o derivado voltaria a crescer por captura: o grão que a `022`
  tirou entrava pela porta das traseiras.
- **Não registar nada e viver da inferência por SHA.** Medido em §3 e §4.1: não
  distingue participação de coincidência, e a aritmética falha na passagem
  mista.

---

## 6B · AS OPÇÕES DO GRÃO DA PARTICIPAÇÃO

> Segunda pergunta, e é a desta missão: **o que a relação representa?**
> As opções são comparadas contra os quatro casos medidos em 7.1.

| | **A** só linhagem | **B** só execução | **C** dois conceitos | **D** estrutura existente |
|---|---|---|---|---|
| CONCEPT | facto material | evento de passagem | os dois, separados | reusar o que há |
| OWNER | writer do derivado | runner / ledger | writer + `etapa_da_corrida` | `etapa_da_corrida` |
| GRAIN | (observação, derivado) | (observação, derivado, run, tentativa) | material + passagem | passagem |
| IDENTITY | `(raw_asset_id, derived_artifact_id)` | inclui `run_id` e `tentativa` | material sem run; passagem já tem chave | `(run_id, etapa, tentativa)` |
| RUN_ROLE | proveniência | identidade | proveniência de um lado, identidade do outro | identidade |
| ATTEMPT_ROLE | ausente | identidade | ausente no material | identidade |
| RESULT_ROLE | ausente | atributo da linha | só do lado da execução | baldes agregados |
| TIME_ROLE | primeira vez | hora do evento | um de cada | hora da passagem |
| RETRY | não cria linha | **cria linha** | material não, execução sim | cria linha |
| REPROCESS | não cria linha | **cria linha** | material não, execução sim | cria linha |
| CONCURRENCY | chave natural + `do nothing` | idem | idem | `UNIQUE` já existente |
| LINEAGE_PROOF | **sim** | sim, mas diluída em N linhas por passagem | **sim** | **não** |
| EXECUTION_PROOF | não (fica com a `024`) | sim | sim | sim, agregada |
| OVERLAP_WITH_ETAPA | nenhum | **alto** — repete a semântica da `024` | nenhum no material | é ela própria |
| MIGRATION_IMPACT | 1 tabela aditiva | 1 tabela aditiva | **2 tabelas** | 0, mas não responde |
| LAW_COMPATIBILITY | `COL-LAW-008` reforçada | colide com `STAGE STATE != ITEM DESTINATION` | ok | não responde a pergunta |

**D cai primeiro,** e por medição: a `028` põe um `check` que só deixa
`etapa_da_corrida.raw_asset_id` ser preenchido na etapa `RAW`. Não é uma ponte
por acaso — é uma ponte deliberadamente fechada. E o grão dela é a passagem:
não tem onde pôr N pares.

**B cai a seguir.** Uma linha por passagem e por item repete o que a `024` já
possui, e mistura as duas perguntas na mesma chave. Quem quisesse saber se a
observação participou teria de varrer o histórico de execuções — e a resposta
mudaria de forma consoante o número de retries.

**C é o conceito certo e o desenho errado para hoje.** Os dois conceitos existem
(7.1), mas um deles **já tem dono**. Criar as duas tabelas seria construir por
antecipação a que falta necessidade provada (7.2).

**A é a escolhida** — uma tabela nova para o conceito que não tem casa, e a
execução fica onde já mora.

```
    DOIS CONCEITOS, DOIS DONOS — E SÓ UM DELES PRECISA DE NASCER.
```

---

## 7 · A DECISÃO

> **Estado desta secção:** DECIDIDA em `C-DECIDE-DERIVED-PARTICIPATION-GRAIN-V1`.
> A versão anterior dizia, ao mesmo tempo, que o grão incluía a passagem
> **e** que a entrada do `run_id` na chave estava em aberto. Eram duas
> respostas para a mesma pergunta, e por isso nenhuma valia.
>
> O erro não foi de redação. Foi ter escolhido **a chave antes do conceito**.

### 7.1 · SÃO DOIS CONCEITOS, E ISSO FOI MEDIDO

Duas perguntas parecidas que não são a mesma:

```
L · LINHAGEM   esta observação participou deste derivado?
E · EXECUÇÃO   em que passagem isso aconteceu, e com que resultado?
```

Se as duas contagens andassem sempre juntas, seriam um conceito só e uma
tabela chegaria. Medido em `provas/a_linhagem_do_reaproveitamento.py`, com os
quatro casos:

| caso | o que aconteceu | arestas | eventos |
|---|---|---|---|
| 1 · `RUN A` → `RAW A` → `X` | `INSERTED` | 1 | 1 |
| 2 · retry na **mesma** corrida | `REUSED`, aresta `(1,3)` outra vez | +0 | +1 |
| 3 · `RUN B`, `RAW B`, mesmos bytes | `REUSED`, aresta `(5,3)` — **outra** aresta | +1 | +1 |
| 4 · rederivar `RAW A` numa passagem de **outra** corrida | `REUSED`, aresta `(1,3)` outra vez | +0 | +1 |

```
ARESTAS MATERIAIS DISTINTAS   1
EVENTOS DE EXECUCAO DERIVED   6
```

Um número não explica o outro, e a divergência não é de escala: é de
**espécie**. A mesma aresta `(1,3)` foi tocada por três passagens, e nenhuma
delas mudou o facto material.

```
    PARTICIPATION_CONCEPT = TWO_DISTINCT_CONCEPTS
```

### 7.2 · MAS SÓ NASCE **UM** DONO NOVO

Dois conceitos não são automaticamente duas tabelas novas. O conceito de
execução **já tem dono**: `public.etapa_da_corrida`, da `024`, onde uma linha é
uma passagem `(run_id, etapa, tentativa)`.

```
MATERIAL LINEAGE   dono NOVO, e é o que falta
EXECUTION EVENT    dono EXISTENTE — etapa_da_corrida
```

Criar uma segunda tabela de execução por item seria repetir a semântica que a
`024` já possui. O limite dela está medido e fica **declarado, não consertado**:
ela conta por passagem e não nomeia itens, e num resultado misto
(`{ERROR: 1, REUSED: 1}`) não há por onde saber qual foi qual. Nenhuma
necessidade provada exige hoje resolver isso — e a pergunta que a motivou
(«esta observação foi processada ou não?») passa a ter resposta pela **existência
da aresta**.

```
    DOIS CONCEITOS != DUAS TABELAS NOVAS.
    UM DELES JÁ TEM CASA.
```

### 7.3 · A IDENTIDADE, E POR QUE O `run_id` FICA DE FORA

```
MATERIAL_LINEAGE_NATURAL_KEY = (raw_asset_id, derived_artifact_id)
RUN_ID_IN_MATERIAL_LINEAGE_KEY = NO
ATTEMPT_IN_KEY = NOT_APPLICABLE
```

**Prova do `NO`:** os casos 2 e 4. A mesma aresta `(1,3)` foi estabelecida numa
passagem da corrida A e re-tocada numa passagem da corrida B. Com o `run_id` na
chave, o mesmo facto material teria **duas linhas** — e a segunda seria uma
linhagem nova inventada por uma execução repetida.

E há uma pergunta que a chave com `run_id` nem consegue formular: **qual** run?
A que capturou a observação, ou a da passagem que derivou? O caso 4 mostra que
podem ser diferentes, e que o banco aceita as duas.

```
    UMA CHAVE QUE NÃO SABE RESPONDER «QUAL DOS DOIS?»
    NÃO É UMA IDENTIDADE: É UMA AMBIGUIDADE COM ÍNDICE.
```

**Prova do `NOT_APPLICABLE` da tentativa:** o caso 2 é um retry, e não produziu
aresta nova. A tentativa já é chave **da passagem**, em
`UNIQUE (run_id, etapa, tentativa)`. E a casa já decidiu isto uma vez, um andar
abaixo: `raw_asset.attempts` é «TELEMETRIA, e fora da chave de idempotência».

### 7.4 · O `run_id` COMO PROVENIÊNCIA, E SÓ ISSO

```
RUN_ID_AS_PROVENANCE = YES  —  um campo, fora da chave
```

A aresta carrega **a corrida da passagem em que foi vista pela primeira vez**.
Não é identidade, não se reescreve nas passagens seguintes, e o nome tem de
dizer isso — um `run_id` seco seria lido como «a corrida desta aresta», que não
existe.

⚠️ **E não se herda.** `raw_asset.run_id` é a corrida que **capturou**; a aresta
precisa da corrida que **derivou**. Copiar uma para a outra por conveniência
escreveria como facto uma coisa que o caso 4 mostra ser falsa.

```
    A CORRIDA QUE CAPTUROU NÃO É NECESSARIAMENTE A QUE DERIVOU.
```

Sem prova da corrida da passagem, recusa-se a linha — nunca se preenche com a
do pai. Hoje isso é sempre possível: `derivacao_forward.correr()` exige `run_id`
como parâmetro obrigatório, sem valor por omissão.

### 7.5 · `INSERTED` / `REUSED` NÃO É DA ARESTA

```
INSERTED_REUSED_BELONGS_TO = EXECUTION_EVENT
```

Medido: a aresta `(1,3)` teve `INSERTED` na primeira passagem e `REUSED` nas
duas seguintes. O facto material não mudou; o resultado mudou três vezes.

```
    UMA RELAÇÃO QUE SE REESCREVE A CADA PASSAGEM NÃO É UMA RELAÇÃO.
```

E a casa já tinha a regra, na `024`: `STAGE STATE != ITEM DESTINATION`. Uma
etapa não é «reaproveitada» — um item é. Os destinos de item vivem nos baldes
da contabilidade da passagem, e é lá que `REUSED` já mora.

### 7.6 · O TEMPO

```
TIME_SEMANTICS = um só carimbo, e ele diz QUANDO A ARESTA FOI VISTA PELA
                 PRIMEIRA VEZ — nunca quando a derivação aconteceu, nunca
                 quando a passagem correu
```

Os outros dois tempos já têm dono: `derived_artifact.derived_at` é do artefato,
e `etapa_da_corrida.comecou_em` é da passagem. Um campo temporal de **evento**
dentro de uma relação estável, sem dizer o que significa, é a maneira mais
silenciosa de a relação passar a ser lida como histórico.

### 7.7 · O DONO DA ESCRITA

```
RECOMMENDED_OWNER = guarda/preservar_derivado.py
```

Os dois candidatos sabem alguma coisa, e só um sabe a coisa certa.
`coleta/derivacao_forward.py` tem o `run_id` e vê o resultado.
`guarda/preservar_derivado.py` **decide** se houve reencontro, contra que linha
existente, e já calcula `TESTEMUNHA_NO_BANCO` e `TESTEMUNHA_DESTA_CHAMADA` — os
dois lados da aresta. Pôr a escrita no runner faria uma segunda peça deduzir o
que a primeira decidiu.

```
    ONE CONCEPT → ONE OWNER.
    QUEM DECIDE A ARESTA É QUEM A ESCREVE.
```

O writer passa a precisar do `run_id` da passagem — parâmetro novo, e é a
única mudança de contrato que esta decisão exige.

### 7.8 · O APAGAMENTO

```
DELETE_POLICY = RESTRICT dos dois lados
```

Não é preferência: é a convenção **medida** no esquema. As ligações materiais
restringem e a telemetria cascateia:

```
raw_asset        -> collection_run    RESTRICT
derived_artifact -> raw_asset         RESTRICT
raw_asset        -> storage_object    RESTRICT
etapa_da_corrida -> collection_run    CASCADE
etapa_da_corrida -> raw_asset         CASCADE
```

A aresta é material, logo restringe. Apagar uma observação que participou de
uma derivação tem de doer — proveniência não desaparece em silêncio.

### 7.9 · O QUE A IMPLEMENTAÇÃO NÃO VAI CONSEGUIR

```
BACKFILL_POLICY = NENHUM. Histórico sem aresta fica UNKNOWN.
```

A aresta nunca foi escrita, e a inferência por `sha256` não distingue quem
participou de quem apenas tem os mesmos bytes.

```
    PREENCHER O PASSADO POR INFERÊNCIA
    É FABRICAR A EVIDÊNCIA QUE FALTAVA.
```

A relação vale a partir da migration. O que é anterior fica `UNKNOWN`, que é a
verdade.

### 7.10 · O QUE FICA FECHADO PARA QUEM IMPLEMENTAR

```
CONCEITO      relação material de participação
GRÃO          uma linha por (observação, derivado)
IDENTIDADE    (raw_asset_id, derived_artifact_id)
RUN           proveniência, fora da chave, da passagem e nunca herdada
TENTATIVA     não entra — é chave da passagem
RESULTADO     não entra — é destino de item, e já mora nos baldes
TEMPO         um carimbo de primeira vez, e nada mais
RETRY         não cria linha; a existente fica
REPROCESSO    não cria linha; a existente fica
CONCORRÊNCIA  a chave natural resolve, com `on conflict do nothing`
DELETE        RESTRICT dos dois lados
BACKFILL      nenhum
MIGRATION     aditiva — tabela nova, nenhuma coluna alterada
```

Nenhuma destas perguntas volta a abrir-se na missão que escrever a migration.

## 7B · RED TEAM DO GRÃO

Vinte ataques à decisão de 7. Onde diz **medido**, há caso a correr em
`provas/a_linhagem_do_reaproveitamento.py`.

| # | ataque | veredito |
|---|---|---|
| 1 | mesma linhagem duplicada só porque houve corrida nova | **medido** · G4: aresta `(1,3)` re-tocada numa passagem de B, e continua uma |
| 2 | duas corridas colapsadas quando o objetivo era histórico | o histórico fica em `etapa_da_corrida`, que **não** colapsa: 6 eventos para 1 aresta |
| 3 | retry virar linhagem nova | **medido** · G2: retry na mesma corrida, `+0` arestas |
| 4 | retry desaparecer quando o objetivo era histórico | não desaparece: cada retry é uma linha em `(run_id, etapa, tentativa)` |
| 5 | `INSERTED`/`REUSED` guardado no conceito errado | **medido** · G6: a mesma aresta teve os dois. Fica na passagem |
| 6 | carimbo do evento guardado como se fosse da relação | 7.6 · um só carimbo, e o nome diz «primeira vez» |
| 7 | `raw_asset.run_id` herdado como corrida da derivação | **medido** · G4: podem ser diferentes. Herdar é proibido em 7.4 |
| 8 | `collection_run` esticada para semântica que não tem | a `022` já recusou: «esticar `collection_run` para algo que não é coleta seria pior do que não ter nada» |
| 9 | um `flow_run` paralelo | a `024` já recusou: «duas corridas divergem na primeira pressa» |
| 10 | tabela nova duplicar `etapa_da_corrida` | 6B · é exactamente por isso que a opção B cai |
| 11 | `etapa_da_corrida` usada como linhagem material | **medido** · D2: a `028` fecha `raw_asset_id` fora da etapa RAW |
| 12 | SHA usado como participação | **medido** · C: a consulta devolve `[3, 7]` e não as separa |
| 13 | mesma observação + nova versão do produtor | **outra** receita → **outro** `derived_artifact` → **outra** aresta. A `022` põe `producer_version` na identidade |
| 14 | mesma observação + mesma receita em nova execução | **medido** · G4: mesma aresta, novo evento |
| 15 | duas observações + mesmo conteúdo na **mesma** corrida | duas arestas, um derivado — a chave é por observação, e `raw_asset` distingue-as |
| 16 | duas observações + mesmo conteúdo em corridas diferentes | **medido** · G3: aresta `(5,3)` nasce ao lado de `(1,3)` |
| 17 | tentativa ignorada num modelo que diz representar passagem | o modelo material **não** representa passagem; quem a representa já tem a tentativa na chave |
| 18 | tentativa incluída num modelo que diz representar linhagem estável | 7.3 · fica de fora, com o precedente de `raw_asset.attempts` |
| 19 | backfill por inferência | 7.9 · proibido, e o histórico fica `UNKNOWN` |
| 20 | delete apagar proveniência | 7.8 · `RESTRICT` dos dois lados, pela convenção medida no esquema |

---

## 8 · O QUE ESTA ADR NÃO DECIDE

- **`canal_id`.** Fora do âmbito, e a distinção fica registada em §9.
- **`STRUCTURED`.** Não foi ligado.
- **A régua de unicidade da `022`.** Fica como está.
- **Produção.** Nenhuma migration foi executada, aqui ou em qualquer sítio.

---

## 9 · REGISTO SOBRE `canal_id`, SEM O RESOLVER

A missão anterior escreveu que o dono da identidade de canal «não existe». A
medição obriga a ser mais preciso, porque há duas coisas e só uma falta:

```
SCHEMA OWNER                    EXISTE
  public.origem · public.canal, migration 002, com chave natural
  (plataforma, channel_id) e a trava «origem é pessoa OU organização»

RUNTIME RESOLVER (ler + recusar) EXISTE
  coleta/social_persistencia.canal_canonico / exigir_canal
  — lê o que já existe, nunca cria, e recusa com QUEM_RESOLVE por escrito

RUNTIME OWNER (decidir + criar)  NÃO EXISTE
  medido: inserem em `origem`/`canal` apenas dois testes e uma prova.
  Nenhum ficheiro de produção cria origem ou canal.
```

```
    O QUE FALTA NÃO É A TABELA, NEM QUEM A LÊ.
    É QUEM DECIDE DE QUEM É O CANAL.
```

E a razão de a decisão ser de gente está escrita no próprio código:
`CHANNEL_ID PROVA O CANAL, NÃO PROVA A ORIGEM`.
