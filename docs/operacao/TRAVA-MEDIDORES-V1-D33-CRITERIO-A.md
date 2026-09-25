# TRAVA-MEDIDORES-V1 · BLOCOS (b) e (c) — critério A sobre as 716 do Curator, e a classe de cada fonte

> D33 (bot Luciano, delegação do dono, `DECISOES-DONO-2026-09-23.md`). A trava não foi editada.
> **Não integrado nem instalado**: o coordenador instala os medidores depois. Trabalho **offline**:
> zero pedidos de rede.

## 0 · O resultado (25/09, depois da 2.ª passagem)

```text
CRITÉRIO A (716 identidades italianas do Curator)  =  NAO
  CLASSE_PROVADA          98   (97 RC-1 · 1 RC-10)
  BLOQUEADA_COM_RAZAO     29   (13 CONTRACT_READY_ROUTE_BLOCKED · 11 CAPABILITY_BLOCK · 5 AUTH_BLOCK)
  NAO_SEI                589   (483 sem contrato no livro do coletor · 106 só contrato/canário)
```

`COLLECTION_FOUNDATION_CLOSED` continua `NAO` (a constante é da lei; este medidor não a muda).

**Correção da 1.ª passagem (`c888f683`, 90/29/597):** eu tratei como «livro do coletor» só o
`regras/italy_contracts_onboarded.json` (193). **Errado.** O coletor
(`coleta/italy_pilot_collect.mjs`) importa `CONTRACTS` de `regras/italy_contracts.mjs` — as 193
linhas **mais 13 contratos feitos à mão** (ARPAV, ARIF, portfólio ADAMA…) = **206**. Com o livro
certo, as 8 fontes que tinham «resultado real sem executor determinável» ganharam classe:
`IT-T2-001`, `IT-T2-002`, `IT-T2-004`, `IT-T3-002`, `IT-T3-008`, `IT-T3-010`, `IT-T3-011` → RC-1;
`IT-T4-001` (CSV) → RC-10.

## 1 · Bloco (b) — o medidor do critério A mede as 716

Dono: `system-map/scripts/censo_das_estradas_it.py` → `estradas-it.generated.json`, secção
`CRITERIO_A_NO_CURADOR`.

- **Denominador**: `curadoria/LIFECYCLE-LEDGER-V1.json`, último estado de cada `SOURCE_ID IT-`
  → **716** (D33: 54 não é denominador; 193 é o recorte executado).
- `UNIVERSO_DO_VEREDITO` diz `DECISAO = D33`; as secções antigas sobre o catálogo de 54 ficam
  publicadas como **histórico**.
- `CRITERIO_A = SIM` só quando **nenhuma** das 716 fica `NAO_SEI`.

## 2 · Bloco (c) — SOURCE_ID → RC-*, pelo caminho/executor/resultado reais

Regra (função pura `classificar_fonte`), por esta ordem:

| pergunta | se sim |
|---|---|
| resultado real **e** caminho HTTP **e** saída de dataset (CSV/ODS/XLSX)? | **RC-10**, com a prova |
| resultado real **e** caminho HTTP **e** saída de documento (PDF/HTML)? | **RC-1**, com a prova |
| o Curator bloqueou **com razão escrita**? | `BLOQUEADA_COM_RAZAO` |
| senão | **`NAO_SEI`**, com o porquê |

«Caminho HTTP» = contrato com estratégia `HTML_LINK_DISCOVERY`/`STATIC_ENDPOINT`, **ou** contrato
feito à mão que declara `ACCESS_INSTRUMENT` HTTP **e** `BROWSER_REQUIRED = false`. O YouTube
(`CUSTOM_ADAPTER`, vai pelo Scrap) nunca entra.

**O caminho real** (lido no código): orquestrador → `coleta/italy_executor.py` →
`coleta/italy_pilot_collect.mjs` → `coleta/ingresso.py` → `guarda/preservar_coleta.py` (**RAW** —
o dono que a D33 confirma) → `executor_texto_de_pdf/html` (**DERIVED**).

⚠️ **Divergências declaradas:** o FETCH do modelo da RC-1 é `coleta/texto_fonte.py`, o real é
`italy_pilot_collect.mjs`; o nome `OFFICIAL_*` não foi verificado fonte a fonte; e o modelo da
RC-10 não declara FETCH nem DERIVED. Ficam em `PORQUE_RC1`, para o dono do modelo.

**Provas aceites** (só do mundo do Curator): o livro do Curator («corrida real com sucesso na Big
Collection (N observações)», N > 0 — com `EVIDENCE_REF` da corrida canónica), `BC5-…-1A-ONDA.json`
(RAW > 0 e DERIVED > 0), `BC4D-MICRO-FINAL-RESULTADO.json` (linha nova na Sala real, C4 PASS).
**Recusadas**: o ledger em Git e o canário do modelo (SOURCE_ID do catálogo antigo — colisão
possível), e as 100 menções de «corrida real» dentro de texto de reconciliação.

**A tabela, fonte a fonte**: `data/derivados/TRAVA-MEDIDORES-V1/MAPA-SOURCE-RC-716.tsv` (716
linhas; sha256 `b24786612b02024c…`).

Das 98 com classe provada, a maior parte **não** está `READY_FOR_COLLECTION` hoje (recuaram na
reconciliação). **Estrada provada ≠ fonte pronta agora.**

## 3 · Testes e mutação

| | resultado |
|---|---|
| antes da D33 (`testes-D33-ANTES.txt`) | FAILED — `criterio_a_no_curador` não existia |
| antes dos contratos à mão (`testes-CONTRATOS-A-MAO-ANTES.txt`) | FAILED — `contratos_do_coletor` não existia; IT-T2-002 e IT-T4-001 sem classe |
| depois (`testes-CONTRATOS-A-MAO-DEPOIS.txt`) | **OK — 20 de 20** |
| mutação (`mutacao-RESULTADO.txt`) | **15 de 15 mortos** |
| vizinhos `test_estradas_it` + `test_trava_da_inteligencia` | as mesmas 2 falhas da base (as violações reais do congelamento) |

Dois mutantes sobreviveram à 1.ª volta e obrigaram a testes melhores: «YouTube como documento»
(nenhum canal tem resultado real hoje) e «contrato à mão com navegador conta como HTTP» (o exemplo
do teste falhava por outra razão). Os dois morreram depois de acrescentar exemplos inventados à
regra pura.

## 4 · D35 — o que medir quando a Sala crescer (preparação no papel)

A MICRO (lote fixo) e, se passar, a 2.ª onda web vão trazer material novo. **Nada de nova
Intelligence**: sem crossing, finding, oportunidade nem leitura para pontuar; a trava fica como
está. O que muda na **medição da trava**, critério a critério:

| critério | muda com a coleta? | como o medidor consertado o vai ver | cuidado |
|---|---|---|---|
| **A** | **sim** — é o que mais mexe | cada fonte com corrida nova que grave RAW + DERIVED sai de `NAO_SEI` para RC-1/RC-10 | ⚠️ o medidor só lê provas **que estão no Git**: o livro do Curator commitado e a lista `PROVAS_DE_RESULTADO` (hoje BC5 e BC4D). **Um relatório novo da MICRO/2.ª onda só conta se for acrescentado a essa lista** (mudança de código pequena, com teste) **ou** se o Curator gravar a transição «corrida real com sucesso» no livro commitado. Sem isso, a coleta corre e A não se mexe — e isso seria o medidor, não a coleta |
| **A** (denominador) | pode | 716 muda se o Curator ganhar/retirar identidades `IT-` | o medidor lê o último estado, recalcula sozinho |
| **J** (Git não é estado operacional) | pode piorar | `GIT_COMO_BANCO_OPERACIONAL`: contar linhas dos `ndjson` antes e depois | se crescerem, a coleta escreveu estado no Git |
| **K** (retry/queda não fabricam sucesso) | não tem medidor | — | os relatórios da onda (C4, falhas registadas) são o material para um medidor futuro; não o invento agora |
| **N** (congelamento) | **não** — é sobre código | o vigia compara com a foto de 08/09 | se N mudar depois da coleta, alguém mexeu em código de inteligência |
| **C, E, H** (donos) | não | o censo `donos` mede escritores por grep | a D33 já decidiu os donos; falta pô-los no medidor (trabalho seguinte) |
| **B, G, M** | não diretamente | — | — |

**Ordem da medição depois da coleta** (quando o coordenador disser «volumes reconciliados»):
1. confirmar que as provas novas estão no Git (livro do Curator commitado e/ou relatório da onda);
2. se o relatório da onda tiver formato novo, acrescentá-lo a `PROVAS_DE_RESULTADO` **com teste e
   mutação**, antes de medir;
3. correr `censo_das_estradas_it.py` e `censo_do_congelamento.py` (offline, sem rede);
4. comparar `CRITERIO_A_NO_CURADOR.POR_RESOLUCAO` antes/depois, fonte a fonte, e publicar a
   diferença com a prova de cada fonte que mudou.

## 5 · O que a D33 decidiu e este medidor NÃO usa ainda

Os donos únicos (RAW = `guarda/preservar_coleta.py`; persistência do checkpoint =
`coleta/coleta_checkpoint.py`; escolha de rota = `orquestrador/orquestrador.py`) mudam **C, E, H**.
O censo `donos` continua a dizer `DONO_DUPLICADO`. Pô-los no medidor é trabalho seguinte.

## 6 · PROVA-DA-ONDA (25/09) — o passo da secção 4, implementado

**O que mudou no medidor:** a lista de provas escrita à mão (`BC5` e `BC4D` pelo nome) saiu.
O medidor lê **a pasta oficial inteira**, `ferramentas/big_collection/`, e reconhece uma prova
pelo **formato** do registo que o disparador (`bc5_big_collection.py`) escreve por fonte —
`SOURCE_ID, STATUS, RUN_ID, RAW, DERIVED, C4` — e pelo formato da micro
(`LINHAS_NOVAS_NA_SALA` + `CORRIDAS`). **O registo da 2.ª onda conta sem mexer no medidor**,
desde que entre no Git nesta pasta.

**Quando uma fonte conta:** `STATUS = SUCCESS` **e** `RAW ≥ 1` **e** `DERIVED ≥ 1` **e**
`C4.SALA_LINHAS == C4.SALA_COM_CADEIA_INTEIRA` (proveniência não partida). `SUCCESS` com 0
documentos novos **não** conta: correu, mas não trouxe byte.

**Conferido:** o registo no Git (`BC5-BIG-COLLECTION-1A-ONDA.json`) é igual, fonte a fonte, ao que
o disparador gravou em `C:/bc5/big/BIG-COLLECTION-ESTADO.json` (sha256 `35be3056f90cde6c…`).

**Teste com a prova REAL da 1.ª onda:** conta **exatamente** 5 — `IT-T10-018`, `IT-T7-021`,
`IT-T7-042`, `IT-T7-117`, `IT-T7-135` — das 18 que correram com `SUCCESS` (as outras 13 não
gravaram documento novo). E um registo inventado, com nome qualquer, na pasta, conta só a linha
que cumpre as quatro condições.

**Quanto o A sobe SÓ com a 1.ª onda** (`A-COM-E-SEM-A-1A-ONDA.txt`):

```text
sem a 1.a onda   CLASSE_PROVADA 94 · BLOQUEADA 29 · NAO_SEI 593
com a 1.a onda   CLASSE_PROVADA 98 · BLOQUEADA 29 · NAO_SEI 589      (+4)
```

As 4 que mudaram: `IT-T7-021`, `IT-T7-042`, `IT-T7-117`, `IT-T7-135` (NAO_SEI → RC-1). A
`IT-T10-018` já estava provada pela micro BC4D. **A continua NAO.**

**Testes e mutação:** 23 de 23; **21 de 21 mutantes mortos** (6 novos: SUCCESS, RAW, DERIVED,
proveniência partida, formato do registo, nome fixo da pasta). O mutante «RAW deixa de ser
exigido» sobreviveu à 1.ª volta — nenhum exemplo tinha DERIVED sem RAW novo; acrescentado.

**Não mexido:** o disparador e o vivo.
