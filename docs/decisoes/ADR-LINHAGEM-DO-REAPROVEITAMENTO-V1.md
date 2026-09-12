# ADR — A PARTICIPAÇÃO NUMA DERIVAÇÃO PRECISA DE LINHA PRÓPRIA

**Data:** 2026-09-12 · **Estado:** RECOMENDADO, NÃO IMPLEMENTADO
**Missão:** `C-DECIDE-DERIVED-REUSE-LINEAGE-V1`
**Medição:** [`provas/a_linhagem_do_reaproveitamento.py`](../../provas/a_linhagem_do_reaproveitamento.py)
**Artefato:** `system-map/data/linhagem.observada.json`

> Esta missão é de **medição + contrato**. Nada foi implementado: não há
> migration nova, não há tabela nova, não há coluna nova.

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

## 6 · AS OPÇÕES, MEDIDAS

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
| GRAIN | **uma linha por participação**: (observação, derivado, passagem) |
| IDENTITY | chave natural `(raw_asset_id, derived_artifact_id, run_id)` — sem surrogate |
| PROVENANCE | `run_id` referencia `collection_run`, `NOT NULL`, e o resultado (`INSERTED`/`REUSED`) fica na linha |
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

## 7 · A RECOMENDAÇÃO

```
RECOMMENDED_ARCHITECTURE = B
RECOMMENDED_OWNER        = guarda/preservar_derivado.py
RECOMMENDED_GRAIN        = uma linha por (observação, derivado, passagem)
MIGRATION_REQUIRED       = YES — aditiva, e de outra missão
```

**Por que o dono é o writer, e não o runner.** Os dois candidatos sabem alguma
coisa, e só um sabe a coisa certa. `coleta/derivacao_forward.py` tem o `run_id`
e vê o resultado. `guarda/preservar_derivado.py` é quem **decide** se houve
reencontro, contra que linha existente, e já calcula `TESTEMUNHA_NO_BANCO` e
`TESTEMUNHA_DESTA_CHAMADA`. Pôr a escrita no runner faria uma segunda peça
deduzir o que a primeira decidiu.

```
    ONE CONCEPT → ONE OWNER.
    QUEM DECIDE A ARESTA É QUEM A ESCREVE.
```

### 7.1 · A sub-decisão que fica aberta, e não se resolve aqui

O writer **não recebe `run_id` hoje**. A missão que implementar tem de escolher:

- passar `run_id` ao writer, mantendo-o dono da aresta; **ou**
- provar que a participação não precisa da corrida, e então a chave natural é
  só `(raw_asset_id, derived_artifact_id)`.

A recomendação é a primeira — uma participação sem corrida não diz **quando**
aconteceu, e a mesma observação pode ser reprocessada mais tarde. Mas isso é
uma decisão de contrato, e esta missão não a toma por antecipação.

⚠️ **E o `run_id` não se fabrica.** Se ele não chegar ao writer, a resposta é
recusar a linha, nunca inventá-la a partir de `raw_asset.run_id` — a corrida
que *observou* não é necessariamente a corrida que *derivou*.

### 7.2 · O que a implementação não vai conseguir

**Não há backfill possível** para as participações que já aconteceram. A aresta
nunca foi escrita, e a inferência por SHA não distingue quem participou de quem
apenas tem os mesmos bytes. Uma migration que preenchesse a tabela por SHA
escreveria como facto exactamente aquilo que esta ADR mede como não sabido.

```
    PREENCHER O PASSADO POR INFERÊNCIA
    É FABRICAR A EVIDÊNCIA QUE FALTAVA.
```

O que se pode declarar é o começo: a relação vale a partir da migration, e o
que é anterior fica `UNKNOWN` — que é a verdade.

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
