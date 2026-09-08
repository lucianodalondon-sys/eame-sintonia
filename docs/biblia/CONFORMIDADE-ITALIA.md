# ITALY_COLLECTION_COMPLIANCE_MATRIX — apêndice C da Bíblia

**Perfil:** `ITALY_PROFILE_V1` · **Data:** 2026-09-07 · **HEAD medido:** `56fdb8c`

> Esta matriz mede a **implementação italiana** contra as 48 leis canônicas. Ela não é a
> lei: a lei está em [`../../BIBLIA-CANONICA-DA-COLETA.md`](../../BIBLIA-CANONICA-DA-COLETA.md).
>
> **`LAW = CANONICAL` para todas as 48. Isto aqui mede outra coisa: se já funciona.**
> Confundir os dois é o erro que esta separação existe para impedir.

**Escopo declarado:** `CURRENT IMPLEMENTATION COUNTRY = IT`. Espanha e França **não** foram
alteradas, medidas nem portadas nesta missão.

---

## O PLACAR

| estado | nº | |
|---|---:|---|
| `IMPLEMENTED` | **21** | há código no caminho produtivo e prova executável |
| `PARTIAL` | **23** | existe em parte, ou existe para um caminho e não para os outros |
| `ABSENT` | **4** | é lei, e não há implementação nenhuma |
| `UNKNOWN` | **0** | — |

---

## A MATRIZ

| LEI | ESTADO | EVIDÊNCIA | O QUE FALTA | PRÓXIMO PASSO |
|---|---|---|---|---|
| `COL-LAW-005` coletar ≠ admitir ≠ julgar | `PARTIAL` | `admissao/admissao.py` existe e o orquestrador entrega nela | as fontes italianas não passam pelo orquestrador; entram pelo `italy_recurrent_collect.mjs` direto | G-05 |
| `COL-LAW-006` RAW primeiro | `IMPLEMENTED` | `RAW_PRESERVED_BEFORE_PARSE` em 144 observações; ordem §8 do agendamento | — | — |
| `COL-LAW-007` RAW ≠ derivado | `IMPLEMENTED` | `BROWSER_RENDERED_EXTRACT` é tipo próprio na matriz de contratos | — | — |
| `COL-LAW-008` derivação tem linhagem | `PARTIAL` | a cadeia inversa existe para a rota paga | os derivados de PDF/HTML italianos não declaram `parent_artifact_id` | G-06 |
| `COL-LAW-009` seis entidades distintas | `IMPLEMENTED` | gavetas + `P2_PASTA_BATE_COM_MAPA` no CI | — | — |
| `COL-LAW-010` pedido não conhece implementação | `IMPLEMENTED` | `pedido/pedido.py`, recusa `AUTOMATICO_EVENTO` com motivo | — | — |
| `COL-LAW-011` um dono da orquestração | `PARTIAL` | `pedido/orquestrador.py` assina o recibo | nenhum executor italiano está no `EXECUTORES` da receita | **G-05** |
| `COL-LAW-012` controle ≠ dado | `PARTIAL` | `larga_em` declarado nos 4 executores da receita | os executores `.mjs` italianos não declaram onde largam | G-05 |
| `COL-LAW-013` contrato comum de executor | `PARTIAL` | os 4 contratos obrigatórios estão declarados | `CHECK` e `STATE` não existem como verbo comum | G-07 |
| `COL-LAW-014` capacidades declaradas | `PARTIAL` | 6 dos 12 campos em `receitas.py::EXECUTORES` | `cost_class`, `supports_checkpoint`, `supports_retry`, `countries`, `modes`, `artifact_types` | G-07 |
| `COL-LAW-015` receita é derivada | `IMPLEMENTED` | fontes vêm de `sources.generated.json`; o plano nomeia o que não sabe percorrer | — | — |
| `COL-LAW-016` estado incremental é do executor | `PARTIAL` | `checkpoint_coleta` existe para a rota paga | as 3 fontes `FORWARD_ONLY` não têm cursor: comparam hash | G-08 |
| `COL-LAW-017` checkpoint e trava do gasto | `IMPLEMENTED` | `coleta/coleta_checkpoint.py` + `tests/test_coleta_resiliente.py` | — | — |
| `COL-LAW-018` rota mais barata capaz primeiro | `PARTIAL` | o portão grátis do contrato do ator roda antes do gasto | não existe `ROUTE_POLICY`: há **um** executor por alvo | **G-04** |
| `COL-LAW-019` Apify é rota paga de escalada | `ABSENT` | política de chaves escrita; `maxTotalChargeUsd` em uso | os 5 campos (`WHY_PAID_ROUTE`, `CHEAPER_ROUTE_ATTEMPTED`, `CHEAPER_ROUTE_RESULT`, `ESCALATION_REASON`) **não existem em ficheiro nenhum** | **G-04** |
| `COL-LAW-020` rota bem-sucedida tem memória | `ABSENT` | — | `last_successful_route` não existe | G-09 |
| `COL-LAW-021` não coletar de novo sem necessidade | `PARTIAL` | hash por documento; `SEEN_AGAIN` com zero bytes guardados | não há `ETag`/`Last-Modified` **antes** do fetch: baixa-se para comparar | G-10 |
| `COL-LAW-022` toda corrida tem identidade | `PARTIAL` | 13 corridas no `RUN-MANIFEST`, 6 no ledger italiano | **dois formatos**; o italiano não tem `COST_USD` nem `STATUS` | **G-02** |
| `COL-LAW-023` reconciliação entre portas | `PARTIAL` | `padrao_da_coleta.py` mede 10 regras no CI | `DISCOVERED → EMITTED → RAW_LANDED → READY` não é medido em nenhuma corrida | **G-03** |
| `COL-LAW-024` zero inesperado não é sucesso | `IMPLEMENTED` | `SUCCEEDED`+0 itens vira `PARTIAL`; lista vazia é `FAILED` | — | — |
| `COL-LAW-025` retry tem critério | `ABSENT` | — | `TRANSIENT` vs `PERMANENT` não existe; não se lê `Retry-After` | G-11 |
| `COL-LAW-026` circuit breaker | `ABSENT` | — | nada impede martelar uma fonte que falha sempre | G-12 |
| `COL-LAW-027` quarentena e replay | `PARTIAL` | `--so-a-porta` reprocessa sem colher de novo | não há fila de quarentena com `attempts`/`last_error` | G-13 |
| `COL-LAW-028` a fonte tem saúde | `IMPLEMENTED` | `source_health.py` + `italy_source_health.mjs`, vocabulários idênticos | — | — |
| `COL-LAW-029` source drift e controle negativo | `IMPLEMENTED` | `--negativos` corrompe 8 documentos em memória e exige `FAILED` | — | — |
| `COL-LAW-030` mundo ≠ pipeline | `PARTIAL` | `COLLECTOR_VERSION` e `SOURCE_CONTRACT_VERSION` no ledger italiano | `PIPELINE_VERSION` não existe; o `RUN-MANIFEST` não tem nenhum dos três | G-02 |
| `COL-LAW-031` temporalidade | `PARTIAL` | `FACT_TIME` separado em 144 observações; `v21_datas.py` recusa prosa | ⚠️ `admissao/admissao.py:169` aceita `published_at` como tempo do fato | **G-01** |
| `COL-LAW-032` geografia | `IMPLEMENTED` | lei no core + leitor italiano + constraints da migration 015 | — | — |
| `COL-LAW-033` procedência | `IMPLEMENTED` | `RAW_SHA256` em 144 de 144 observações; contrato V2.1 falha fechado | — | — |
| `COL-LAW-034` identidade | `PARTIAL` | `identidade_valida()` recusa campos que mudam entre execuções | `ITEM_ID` e `ARTIFACT_ID` não são campos próprios no ledger italiano | G-06 |
| `COL-LAW-035` UNKNOWN | `IMPLEMENTED` | `P7_NAO_SEI_VIVE` no CI; `NOT_PRESERVED ≠ NÃO SEI` em código | ⚠️ cinco grafias do sentinela (C-003, decisão em aberto) | **G-14** |
| `COL-LAW-036` no_match não prova não | `PARTIAL` | `f_relevancia_ao_caso` derivada com motivo, sem score | a admissão italiana ainda usa lista de palavras direta | G-15 |
| `COL-LAW-037` erro não vira não | `IMPLEMENTED` | `VPN_FAILURE ≠ SOURCE_FAILURE` provado em operação real | — | — |
| `COL-LAW-038` dois eixos de resultado | `IMPLEMENTED` | `RESULTADOS` e `STATUS_RUN` são listas separadas | — | — |
| `COL-LAW-039` país | `PARTIAL` | `COUNTRY_SCOPE` no pedido; gaveta por país | o escopo não é conferido dentro do executor: nada barra um item ES numa corrida IT | G-16 |
| `COL-LAW-040` país não é língua | `PARTIAL` | `LANGUAGE` é campo próprio em `voz.py` | o ledger italiano não tem campo de língua | G-17 |
| `COL-LAW-041` vocabulário contextual | `PARTIAL` | as palavras da busca vivem em `regras/` e decidem `CROP`/`ISSUE` | a mesma lista serve busca e admissão | G-15 |
| `COL-LAW-042` admissão auditável | `PARTIAL` | o livro guarda item, universo, regra, versão, motivo, prova | as observações italianas nunca passaram pela porta | **G-05** |
| `COL-LAW-043` READY não é «terminou» | `PARTIAL` | contrato de saída fixo em `pronto_para_inteligencia()` | nenhum item italiano chegou a `PRONTO_PARA_INTELIGENCIA` | G-05 |
| `COL-LAW-044` armazenamento ≠ estado | `IMPLEMENTED` | D-003 + a exceção da rota não replicável, com `RAW-GATE-ES.json` | — | — |
| `COL-LAW-045` coleta manual tem contrato | `PARTIAL` | `CAPTURE_METHOD` existe no `RUN-MANIFEST` | `ACTOR_TYPE` não distingue pessoa de máquina | G-18 |
| `COL-LAW-046` lei do espelho | `IMPLEMENTED` | `P1_SEM_DRIFT` no CI, a cada push | — | — |
| `COL-LAW-047` o mapa é saída | `IMPLEMENTED` | `state.generated.json` regerado e conferido | — | — |
| `COL-LAW-048` tipos de conexão | `IMPLEMENTED` | `P5_ARESTA_PROVADA` exige ficheiro e linha | — | — |
| `COL-LAW-049` declared/code/observed | `PARTIAL` | `DECLARED` e `CODE` existem | `OBSERVED` não existe: nenhuma aresta é confirmada por corrida real | G-19 |
| `COL-LAW-050` current ≠ target | `IMPLEMENTED` | `official`/`futuro`/`legacy` são três estados no mapa | — | — |
| `COL-LAW-053` cadastro único de fonte | `IMPLEMENTED` | `sources.generated.json` reconcilia atlas e master italiano | — | — |
| `COL-LAW-069` nenhuma lei muda em silêncio | `IMPLEMENTED` | `py provas/valida_biblia.py` + diário de decisões | — | — |

---

# OS 10 MAIORES GAPS — ORDENADOS POR DEPENDÊNCIA

> **Não por facilidade.** Cada um só pode ser feito depois do anterior estar de pé. Fazer o
> G-04 antes do G-05 seria construir política de rota para um caminho por onde a Itália não
> passa.

### G-01 · `published_at` deixa de responder «quando o fato aconteceu»
`admissao/admissao.py:169` · **1 linha** · Bloqueia COL-LAW-031 e contamina tudo o que
passar pela porta daqui para a frente. É o único gap que **piora com o tempo**: cada item
admitido com tempo de fato falso é um item que alguém terá de reabrir. **Vem primeiro
porque é barato e porque a dívida cresce.**

### G-05 · a coleta italiana entra pelo pedido e sai pela porta
`coleta/italy_recurrent_collect.mjs` → `pedido/receitas.py::EXECUTORES` ·
Hoje a Itália é um caminho paralelo: colhe, preserva, mede saúde — e **nunca passa pela
admissão**. Enquanto isso for verdade, 8 leis ficam `PARTIAL` por um motivo só.
**Destrava:** COL-LAW-005 · 011 · 012 · 042 · 043. É a peça de que tudo depois depende.

### G-02 · um formato de corrida só
`RUN-MANIFEST` + os 5 campos italianos (`EGRESS_IP`, `COLLECTOR_VERSION`, `GIT_HEAD`,
`SOURCE_CONTRACT_VERSION`, `IS_BASELINE`) · Depois do G-05 há um caminho só, e é aí que
faz sentido haver um recibo só. **Destrava:** COL-LAW-022 · 030.

### G-03 · a reconciliação `DISCOVERED → READY`
Só é medível quando existe um caminho inteiro (G-05) e um recibo só (G-02). Sem ela,
`EMITTED ≠ RAW_LANDED` continua invisível. **Destrava:** COL-LAW-023.

### G-07 · o contrato comum do executor, com capacidades
`CHECK` · `STATE` · `cost_class` · `supports_checkpoint` · `supports_retry` ·
`countries` · `modes` · `artifact_types`. **Pré-requisito do G-04:** não há como escolher a
rota mais barata capaz sem que cada executor diga o que é capaz de fazer e quanto custa.

### G-04 · a política de rota, e a escalada paga explicada
`ROUTE_POLICY` + os cinco campos de COL-LAW-019. Só depois do G-07. **Destrava:**
COL-LAW-018 · 019.

### G-09 · a fonte lembra a rota que funcionou
`last_successful_route` · `route_verified_at`. Depende do G-04 existir para ter o que
lembrar. **Destrava:** COL-LAW-020.

### G-10 · dedupe **antes** do fetch
`ETag` / `Last-Modified` / `HEAD` antes de baixar. Hoje as 3 fontes `FORWARD_ONLY` baixam
~12,8 MB por corrida **para depois descobrir** que nada mudou. Depende do G-09 (a memória
da fonte) para saber o que comparar. **Destrava:** COL-LAW-021 · 016.

### G-11 + G-12 · retry com critério, e o disjuntor
`TRANSIENT` vs `PERMANENT` · `Retry-After` · `HEALTHY/DEGRADED/BLOCKED/UNKNOWN` por rota.
Depois de haver rota escolhida e memória de rota, é aqui que a proteção da fonte entra.
**Destrava:** COL-LAW-025 · 026.

### G-14 · a decisão sobre a grafia do desconhecido
⚠️ **Não é engenharia: é decisão do dono** (C-003). Fica no fim da lista por dependência —
mas pode ser decidida a qualquer momento, e quanto mais tarde, mais dados terão de ser
migrados. **Destrava:** COL-LAW-035 por inteiro.

---

## OS GAPS MENORES, registrados e não priorizados

`G-06` linhagem de derivado (`parent_artifact_id`) · `G-08` cursor para as `FORWARD_ONLY` ·
`G-13` fila de quarentena · `G-15` vocabulário separado por responsabilidade ·
`G-16` escopo de país conferido dentro do executor · `G-17` língua no ledger italiano ·
`G-18` `ACTOR_TYPE` distingue pessoa de máquina · `G-19` arestas `OBSERVED` no mapa.

---

## O QUE ESTA MISSÃO DELIBERADAMENTE NÃO FEZ

- **Não consertou nenhum dos gaps.** Missão fundacional (§65 do briefing).
- **Não tocou em Espanha nem em França.** Nenhum perfil deles foi construído.
- **Não reescreveu** `pedido/`, `coleta/`, `admissao/`, `ferramentas/`, `regras/`,
  `guarda/` nem workflow de coleta.
- **Não apagou nada.** Nenhuma lei antiga foi removida; o censo registra 58 `KEEP`.
- **Não instalou plataforma** — nem Airbyte, nem Dagster, nem Temporal, nem Prefect, nem
  Kafka. Os princípios foram adotados; as plataformas, não.
