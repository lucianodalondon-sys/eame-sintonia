# TRAVA-MEDIDORES-V1 · BLOCOS (b) e (c) — critério A sobre as 716 do Curator, e a classe de cada fonte

> D33 (bot Luciano, delegação do dono, `DECISOES-DONO-2026-09-23.md`). A trava não foi editada.
> **Não integrado nem instalado**: o coordenador instala os medidores depois.

## 0 · O resultado

```text
CRITÉRIO A (716 identidades italianas do Curator)  =  NAO
  CLASSE_PROVADA          90   (todas RC-1)
  BLOQUEADA_COM_RAZAO     29   (13 CONTRACT_READY_ROUTE_BLOCKED · 11 CAPABILITY_BLOCK · 5 AUTH_BLOCK)
  NAO_SEI                597   (488 sem contrato · 101 só contrato/canário · 8 resultado real sem executor determinável)
```

`COLLECTION_FOUNDATION_CLOSED` continua `NAO` (a constante é da lei; este medidor não a muda).

## 1 · Bloco (b) — o medidor do critério A mede as 716

Dono: `system-map/scripts/censo_das_estradas_it.py` → `estradas-it.generated.json`, secção nova
`CRITERIO_A_NO_CURADOR`.

- **Denominador**: `curadoria/LIFECYCLE-LEDGER-V1.json`, o último estado de cada `SOURCE_ID IT-`
  → **716**. É o que a D33 manda: 54 não é denominador; 193 é o recorte executado.
- `UNIVERSO_DO_VEREDITO` passa a dizer `DECISAO = D33` e aponta A para o livro do Curator. As
  secções antigas (`FONTES_IT`, `RESOLUCAO_POR_FONTE`, 54 do catálogo) continuam publicadas como
  **histórico**, com essa palavra.
- `CRITERIO_A = SIM` só quando **nenhuma** das 716 fica `NAO_SEI` (cada uma tem classe provada ou
  bloqueio com razão escrita).

## 2 · Bloco (c) — SOURCE_ID → RC-*, pelo caminho/executor/resultado reais

A regra (função pura `classificar_fonte`, a mesma para as 716):

| pergunta, por esta ordem | se sim |
|---|---|
| houve **resultado real** pela porta canónica (RAW + DERIVED gravados) **e** o contrato do coletor é de documento HTTP (`HTML_LINK_DISCOVERY` ou `STATIC_ENDPOINT`)? | **RC-1**, `CLASSE_PROVADA`, com a prova |
| o Curator bloqueou (`POLICY/AUTH/CAPABILITY_BLOCK`, `CONTRACT_READY_ROUTE_BLOCKED`) **com razão escrita**? | `BLOQUEADA_COM_RAZAO`, com a razão |
| senão | **`NAO_SEI`**, com o porquê |

**O caminho real das corridas que provam RC-1** (lido no código): orquestrador →
`coleta/italy_executor.py` → `coleta/italy_pilot_collect.mjs` (busca) → `coleta/ingresso.py` →
`guarda/preservar_coleta.py` (**RAW** — o dono que a D33 confirma) → `executor_texto_de_pdf` /
`executor_texto_de_html` (**DERIVED**). RAW e DERIVED são os do modelo da RC-1.

⚠️ **Divergência declarada, não escondida:** o FETCH do modelo da RC-1 é `coleta/texto_fonte.py`;
o FETCH real é `italy_executor` → `italy_pilot_collect.mjs`. E o nome `OFFICIAL_HTTP_DOCUMENT` não
foi verificado fonte a fonte (há revistas e associações entre as 90). Fica em `PORQUE_RC1`, para
o dono do modelo corrigir o modelo ou a classe — não eu.

**Provas aceites** (só do mundo do Curator):
- o próprio livro do Curator: transição com `REASON` «corrida real com sucesso na Big Collection
  (N observações)», N > 0, e o `EVIDENCE_REF` da corrida → **84** fontes;
- `ferramentas/big_collection/BC5-BIG-COLLECTION-1A-ONDA.json` (RAW > 0 e DERIVED > 0) → **5**;
- `ferramentas/big_collection/BC4D-MICRO-FINAL-RESULTADO.json` (linha nova na Sala real, C4 PASS) → **1**.

**Provas recusadas:** o ledger em Git e o canário do modelo. Falam de `SOURCE_ID` do catálogo
antigo, e o mesmo código pode nomear outra fonte noutro livro. Uma prova de outro livro não
atravessa. (100 transições do Curator dizem «corrida real» dentro de texto de reconciliação —
também não contam: não são sucesso.)

**Os 8 com resultado real e sem classe**: `IT-T2-001`, `IT-T2-002`, `IT-T2-004`, `IT-T3-002`,
`IT-T3-008`, `IT-T3-010`, `IT-T3-011`, `IT-T4-001`. Correram de verdade, mas não têm contrato no
livro do coletor que diga que executor correu → `NAO_SEI`. O próximo passo é ler o executor da
corrida no `EVIDENCE_REF` de cada uma.

**A tabela, fonte a fonte**: `data/derivados/TRAVA-MEDIDORES-V1/MAPA-SOURCE-RC-716.tsv` (716
linhas; sha256 `c8a3b07467ed1281…`), gerada do `estradas-it.generated.json`.

### O que isto mostra e não é critério A

Das 90 com classe provada, **só 28** estão hoje `READY_FOR_COLLECTION` no Curator; 33 estão
`UNKNOWN` e 29 `CANARY_PENDING` (recuaram na reconciliação dos livros). **Estrada provada ≠ fonte
pronta agora.** A pergunta A é a primeira.

## 3 · Testes e mutação

| | resultado |
|---|---|
| antes (`testes-D33-ANTES.txt`) | FAILED — `criterio_a_no_curador` não existia; o veredito dizia `PENDENTE_DO_DONO` |
| depois (`testes-D33-DEPOIS.txt`) | **OK — 17 de 17** |
| mutação (`mutacao-RESULTADO.txt`) | **12 de 12 mortos** (os 6 do vigia/coletor + 6 do critério A: só canário prova classe · YouTube como documento · A diz SIM sempre · classe sem prova · bloqueio sem razão conta · denominador volta ao catálogo) |
| vizinhos `test_estradas_it` + `test_trava_da_inteligencia` | as mesmas 2 falhas da base (as violações reais do congelamento) |

O mutante «YouTube como documento» **sobreviveu** na 1.ª volta: nenhum canal tem resultado real
hoje, e o teste sobre o livro não tinha como o ver. Consertado com um teste da regra pura com
fontes inventadas; na 2.ª volta morreu.

## 4 · O que a D33 decidiu e este medidor NÃO usa ainda

Os donos únicos (RAW = `guarda/preservar_coleta.py`; persistência do checkpoint =
`coleta/coleta_checkpoint.py`; escolha de rota = `orquestrador/orquestrador.py`) mudam os critérios
**C, E, H**. O censo `donos` mede escritores por grep e continua a dizer `DONO_DUPLICADO`. Pôr a
decisão da D33 dentro desse censo é trabalho seguinte — não foi pedido nesta ordem e não o fiz.
