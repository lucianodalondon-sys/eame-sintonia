# MISSÃO 14 · RODADA 5 — CAPACIDADE FECHADA PARA O PILOTO · ENTREGA A–T

**Data:** 2026-08-30 · **92 provas na missão** · `FULL_SUITE_NEW_FAILURES = 0`

> **Fechamento.** As duas pendências mais baratas fecharam (Forge e Enovitis), as
> shortlists saíram, e a capacidade tem agora artefato consultável, fichas de decisão,
> handoff e proposta de Supabase. **Nenhum hub novo foi aberto, nenhum país expandido.**

---

## §0 · A CORREÇÃO DE NOME — aplicada

**Não existe mais `ACTIVATION_READY = 9` publicado como creators.** Três métricas, com os
nomes que dizem o que são:

| métrica | valor |
|---|---|
| **`PERSON_CREATOR_ACTIVATION_READY`** | **8** |
| **`FARM_BUSINESS_PARTNER_READY`** | **2** |
| `MARKETING_CONTACTABLE_ENTITIES_READY` | 10 |

`CREATORS_READY` é **métrica proibida**, com teste que varre os documentos. A separação
viaja no JSON, nas fichas, no artefato de capacidade e nos testes.

## A · `PERSON_CREATOR_ACTIVATION_READY` = 8

| país | região | cultura provada | creator | atividade |
|---|---|---|---|---|
| IT | Limena, Padova | milho, alfafa, soja, forragem | **Davide Gomiero** `@gomierofarm` | 6/30d |
| FR | Indre-et-Loire | trigo, cevada, colza, girassol | **David Forge** `@chaineagricole` | 1/30d · 4/90d |
| FR | Loiret | trigo, colza, cevada, milho, semente de cebola | **Gilles Van Kempen** | 4/30d · 10/90d |
| ES | Almería | pimento, hortícolas protegidas | **Germán Fernández** `@germanagrolife` | 12/30d |
| ES | Níjar, Almería | tomate | **AgroSamanta** `@agrosamanta_` | 10/30d |
| ES | — | olivo, alfarroba, hortaliças | **Marc** `@huerto_ecologico.marc` | 10/30d |
| ES | — | olivo, vide | **Fco. Fernández Barroso** `@chicurri_agro` | 4/30d |
| ES | — | vide | **Oliverio Rodríguez** `@oliverio_rodfer` | 12/30d |

## B · `FARM_BUSINESS_PARTNER_READY` = 2

**Bio Campojoyma** `@biocampojoyma` (Níjar — pimento, tomate) · **Pistachos Terruza**
`@terruzapistachos` (Benamaurel, Granada — pistacho). Ficha própria, papéis próprios:
`FIELD_CONTENT_PARTNER`, `FARM_VISIT`, `CASE_STUDY_CANDIDATE`. **Nenhuma é chamada de
influencer.**

## C · `PROMISING` = 15 · D · MOTIVOS

`MISSING_CROP_PROOF` **13** · `MISSING_PUBLIC_CONTACT` 10 · `MISSING_REGION` 8 ·
`MISSING_RECENT_ACTIVITY` 2. **A prova de cultura continua a ser o gargalo** — e é trabalho
de análise de conteúdo, não de mais coleta de perfil.

## E · DAVID FORGE — **fechado**

`PERSON_CREATOR_ACTIVATION_READY`. Canal resolvido **por fonte**: `@chaineagricole`
(`UC3l2JpG0vN8xMkvvfCwavcQ`), não o `@DavidForge` que eu havia inferido. 29 vídeos lidos,
último 2026-08-04. As culturas saem do **conteúdo**: *"Semis du blé sans travailler le sol"*,
*"Engrais sur un colza"*, *"préparer le sol au tournesol"*.

## F · ENOVITIS — **fechado, e o resultado é um NÃO útil**

`ENOVITIS_SOCIAL_IDENTITY = PROVED`. Conta oficial `@enovitis_` confirmada pelo site
`enovitisincampo.it`, 1.110 seguidores. **Rendimento: ZERO pessoas em 12 publicações.**

`DEMOTED_AS_CREATOR_HUB`, mantendo o valor técnico. **Uma tentativa dirigida, como pedido;
não se perseguiu handle.**

## G · SHORTLIST · ES × ALMERÍA × HORTÍCOLAS ✅

**Pessoas (2):** `@germanagrolife` (pimento, 12 posts/30d, podcast próprio) ·
`@agrosamanta_` (tomate, 10 posts/30d, **e-mail publicado pela própria**).
**Parceiro de negócio (1):** Bio Campojoyma.

## H · SHORTLIST · FR × GRANDES CULTURES ✅

**Duas pessoas prontas**, ambas com culturas provadas por conteúdo do próprio canal:
David Forge e Gilles Van Kempen. Cobre trigo, cevada, colza, milho, girassol e semente de
cebola.

## I · IT × VITE — **`NOT_READY`**, com causa medida

1. Zero creators **pessoa** italianos com viticultura provada.
2. Os candidatos de vide da seed eram **mídia de vinho** → `WRONG_ASSIGNMENT`.
3. Enovitis: conta **provada**, rendimento **zero**.
4. Padrão consistente: **prémios mencionam pessoas, feiras mencionam empresas.**

**Falta uma porta italiana de pessoas em viticultura.** Nenhuma shortlist foi fabricada com
creator de vinho consumer-facing.

## J · COBERTURA `COUNTRY × REGION × CROP`

**18 combinações `COUNTRY|CROP` com resposta `READY`.** Quatro dos cinco recortes declarados
fecham; o quinto (IT × vide) devolve `NOT_READY` **com causa**.

## K · ROTAS PÚBLICAS DE CONTATO

Das 8 pessoas prontas: **5 com rota pública** (e-mail próprio, podcast próprio, presença em
stand `#agridemain`, rota de imprensa/Coldiretti). **3 sem rota resolvida** — declarado
`MISSING_PUBLIC_CONTACT` na ficha, não escondido.

## L · MARCA E CONCORRENTES

Sem alteração de estado. BASF · Seipasa · Syngenta (ES) · Bayer (FR).
`PRODUCT_ACTIVATION_PROVED` continua **sem nenhum caso** — e continua a chamar-se
`NOT_OBSERVED_IN_MEASURED_CORPUS`, nunca "faixa vazia".

## M · CASOS-OURO — 7, cada um com a sua lei

| caso | lei que provou |
|---|---|
| Davide Gomiero | `HANDLE_DA_SEED ≠ HANDLE_REAL` |
| Leonardo Leggieri | `NOME_DA_SEED ≠ NOME_REAL` e `CONTA_PESSOAL ≠ CONTA_DA_COMUNIDADE` |
| Fernando Giraldo | `DISPLAY_NAME ≠ LEGAL/PUBLIC IDENTITY` |
| Bio Campojoyma | `ACCOUNT_OF_FARM_COMPANY ≠ PERSON_CREATOR` |
| **David Forge** | `NOME_DA_PESSOA ≠ NOME_DO_CANAL` |
| **ironfarmer** | `IDIOMA ≠ PAÍS` e `SUBSTRING ≠ TERMO` |
| **riz** | `SHORT_AMBIGUOUS_TOKEN ≠ CROP_PROOF` |

## N · TESTES DO MATCHER — as quatro desigualdades

`SUBSTRING_MATCH ≠ CROP_PROOF` · `SHORT_AMBIGUOUS_TOKEN ≠ CROP_PROOF` ·
`QUERY_CROP ≠ OBSERVED_CROP` · `ONE_MENTION ≠ RECURRING_CROP_FIT`. **Todas com teste.**

E fica registado como **ganho**: a correção 8 → 2 removeu seis afirmações falsas.

## O · `CREATOR-CAPABILITY-EAME.json`

Consulta por `COUNTRY | CROP`, com expansão de culturas guarda-chuva (perguntar por
`CEREALS` encontra `WHEAT` e `BARLEY`). Devolve `READY` / `NOT_READY` **com causa**, e
distingue `NOT_READY` de **`NOT_ASKED`** — "não temos" e "não procurámos" são respostas
diferentes.

## P · SUPABASE — proposta, nenhuma tabela criada

Verificação primeiro: **5 workflows `supabase-*` registados no Actions e nenhum ficheiro na
árvore do branch padrão**; zero `.sql`, zero migração. **Não há destino canónico visível.**

Proposta mínima de **7 entidades** separadas por ritmo de mudança e por dono, em
`SUPABASE-READINESS-CREATOR-MAP.md`, obedecendo a regra: **não criar um segundo dono da
pessoa**. Nada derivado vai para o banco.

## Q · HANDOFF DE INTELIGÊNCIA

`docs/creators/HANDOFF-INTELLIGENCE-CREATOR-MAP-EAME.md` — autocontido, com o que provou, o
que não provou, onde responde, cruzamentos com Meta/Radar/Cases/Experts/Field/Time, o que
muda diariamente e o valor por área.

**A superfície no portal não foi decidida**, por instrução.

## R · APIFY

| métrica | valor |
|---|---|
| execuções no manifesto da missão | **7** |
| itens coletados | **154** |
| **custo acumulado** | **US$ 0,3224** |
| custo desta rodada | ≈ US$ 0,03 |

## S · LACUNAS EXATAS

1. **`MISSING_CROP_PROOF` em 13** — análise de conteúdo, não mais coleta.
2. **IT × VITE sem porta.** Abrir mais feiras não resolve; o padrão está medido.
3. **39 hubs por abrir** — deliberadamente não abertos.
4. **43 dos 66 nomeados do AgroInfluye** por recuperar.
5. **Audiência nunca medida** — `FACING` é o lado do balcão, não a composição.
6. **Taxas de conteúdo não publicadas.** Proposta `CONTENT_RATE_MIN_N = 30` **aguarda
   arbitragem** — não foi tornada canónica.
7. **Só Instagram e YouTube.** TikTok e LinkedIn por usar.
8. **`FIELD_VOICE` e mapa de pecuária** não iniciados (3 creators à espera).

## T · `FULL_SUITE_NEW_FAILURES = 0`

Medido por **diferença de conjuntos**, não por impressão. A suíte da casa está em 11+1
falhas, todas anteriores e da missão Early Signal — **nenhuma referencia ficheiro desta
missão**. Duas falhas que eu introduzi durante a rodada foram detetadas e removidas, e a
classe ficou travada por dois testes novos meus.

---

**Casco intacto. Sem ranking. Sem score. Sem expansão de países. Capacidade entregue à
Rodada de Inteligência.**
