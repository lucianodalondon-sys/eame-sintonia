# MATRIZ INTELIGÊNCIA → PRODUTO → ENTREGA

```
DOCUMENT_STATUS      DRAFT
DOCUMENT_TYPE        LIVING PRODUCT REGISTRY
MEASURED_AT          2026-09-08
PORTAL_HEAD          a4fb6d8 · claude/visible-intelligence-v1 · 2026-09-07 21:11 UTC
IMPLEMENTATION       NONE
```

> Esta matriz **recomenda**. Não decide.
> Toda recomendação carrega `CONFIANÇA` e `O QUE TEM DE SER MEDIDO`.
> Onde a prova não existe, a coluna diz `PRECISA DE MEDIÇÃO` — e isso é a resposta,
> não um adiamento.

---

## §1 · A MATRIZ PRINCIPAL — as 13 superfícies

Legenda de `CONFIANÇA`: **A** = alta (prova documental + medição) · **M** = média
(uma das duas) · **B** = baixa (hipótese com fundamento) · **—** = não classificável.

| # | SUPERFÍCIE | PAPEL ATUAL | AUTORIDADE ATUAL | DECISION QUESTION | DADO | INTELIGÊNCIA | DUPLICAÇÃO | CONTRATO | RISCO | VALOR POTENCIAL | PAPEL FUTURO RECOMENDADO | CONF. | O QUE TEM DE SER MEDIDO |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| S-01 | **Opportunity Radar** (17) | ferramenta principal | **YES** · ARQUITETURA §MT2 | **SIM** · «onde um problema medido está a ficar mais relevante — e a ADAMA tem resposta registada?» | opportunities 43 | `ADAMA-RELEVANCE-LAW-V1` · 8 elos · 5 classes · `SO_A_PUBLICA` | resolvida (era 2×43) | **PARCIAL** — lei sim, contrato de ferramenta não | o ecrã chama-se «OPPORTUNITÀ» e o contrato manda dizer `PRIORITY TO INVESTIGATE`; 5 de 13 cartões imprimiam `SALES READY` | **ALTO** — é o único juízo com lei, portão e classe negada | `CANONICAL_TOOL` | **A** | `DECISION_PROVED` com utilizador · resolver Linha A × Linha B (`surface-contract 3/8`) |
| S-02 | **Portfolio** (173) | ferramenta principal *(promovido 07/09, sem registo)* | **UNKNOWN → disputada** | **NÃO** declarada. §MT1 dá-lhe uma; o ecrã responde «que produtos temos?» | products 173 · relationships 5402 | `STRENGTH` 4 níveis | aliases regulatory/commercial/regulatoryLinks | **NÃO** | catálogo lido como disponibilidade comercial (`CONTRATO-DE-DESIGN §2.4`) | **ALTO** — INPUT declarado de MT1 **e** MT2 | **duas hipóteses vivas:** (a) face de MT1 → `CANONICAL_TOOL`; (b) `REFERENCE_SURFACE` + projeção | **B** | **quem abre esta tela e para quê.** Sem isso não se escolhe entre (a) e (b) |
| S-03 | **Future Radar** (44) | exploratória | **PARCIAL** — contrato de dado que recusa definir UI | **SIM** · «o que pode importar depois?» | ITFC 44 de 45 | régua de maturidade 0–5 · momentum · promoção | com S-13 (declarada e agora verificável) | **PARCIAL** — o melhor contrato de DADO do repositório | 44 identificadores lidos como 44 fichas; 12 dos 13 campos obrigatórios não viajam | **ALTO na intenção · BAIXO na entrega** | `EXPLORATORY_TOOL` → `CANONICAL_TOOL` **se** os campos viajarem | **A** | quem é o dono a montante dos 12 campos |
| S-04 | **Label Intelligence** (166) | evidência (por decisão de código) | **UNKNOWN** por documento · **YES por selo** | **SIM** · «o que o rótulo oficial ADAMA autoriza, como está estruturado e o que mudou» | 166 produtos · 210 objetos · 54 versões | 22 regras versionadas · `REGRAS.md@5` · sha selado | com S-02: 166 × 173 **não reconciliados** | **SIM — o único completo** | nenhum interno; o risco é **externo**: outras superfícies re-lerem o rótulo | **MUITO ALTO** | **`CANONICAL_TOOL` + `DELIVERY_PROJECTION`, em simultâneo** | **A** *(tool)* / **A** *(projeção)* | a relação 166 × 173 · nomear o público |
| S-05 | **Crop Windows** (29) | ferramenta | **UNKNOWN** | **NÃO** | 29 canónicas + 7 leituras | nenhuma: `NOT_EXTERNALLY_OBSERVABLE` 29/29 | alias windows/cropWindows | **NÃO** | **ALTO** — `SOURCE_IDS` vazio 29/29, `CURRENT_STATUS` é aritmética, `LAST_VALIDATED` é carimbo de geração; **gerador ausente de 979 commits** | ALTO **se** ganhar proveniência | `CONTEXT_VIEW` / componente temporal de S-01 e S-04 | **M** | **o gerador.** É o UNKNOWN mais caro do inventário |
| S-06 | **Market Pulse** (157) | ferramenta | **NO** · duas provas | **NÃO** | 157 observações UE | séries de preço | — | **NÃO** | `HISTORICAL` lido como `CURRENT` (azeite de Salerno €630 era de 2015) | MÉDIO como contexto | `CONTEXT_VIEW` / `DELIVERY_PROJECTION` de S-01 e Ask | **M-A** | se alguém a abre para decidir. **PRECISA DE MEDIÇÃO** |
| S-07 | **Field Voices** (79) | ferramenta | **NO** — mas a recusa era de **FONTE**, não de ideia | **NÃO** — candidata forte por escrever | 79 vozes · 62 canais · **184 transcrições invisíveis** | resolução de cultura (missPct 1,3 %) | aliases voices/channels · `people` com S-09 e S-11 | **NÃO** | sentimento agregado sem denominador; GDPR aberto | **O MAIOR POTENCIAL NÃO REALIZADO** — 5,03 M ch de fala no acervo, 0 no pacote | **três hipóteses vivas:** `SENSOR` · `EVIDENCE_EXPLORER` · `CANONICAL_TOOL` | **B** | baseline · denominador · GDPR P-008/P-009. **PRECISA DE MEDIÇÃO** |
| S-08 | **Competitor Watch** (577) | ferramenta | **NO, textual** | **NÃO** como ferramenta · **SIM** como camada | 577 (414 pagos · 147 orgânicos · 16 nota) | crosswalk 1.683 cadeias · 126 recusadas | — | **NÃO** — e o contrato de dado proíbe-o em voz alta | **ALTO** — a barra imprime `577`, que é o número único que o contrato proíbe; 27 selos ATTIVO com `ACTIVE_ADS_PROVED = 0` | ALTO como camada | `CROSS-CUTTING LAYER` + `INVESTIGATION_VIEW` + projeção | **M-A** | resolver o contador · fazer a data de verificação viajar |
| S-09 | **Scientific Intelligence** (88) | ferramenta | **NO** *(mas a reavaliação de 08/09 obriga a reabrir — ver §3)* | **PARCIAL** · CAP-017 é decision question, mas **não cobre a Itália** | 88 servidos de **763 no acervo** | recorrência · caseAdherence · countryOfFact | `researchers` com S-11 | **NÃO** | **ALTO** — 39/88 são `OFF_CASE`; 87/88 batem `QUERY_*`, 37/88 batem `PROVED_*` | ALTO e crescente | **`CANONICAL_TOOL` para R&D/TEC é hipótese VIVA, não descartada** | **M** | utilizador, não dado · GDPR P-008 · resolver `OFF_CASE` |
| S-10 | **Archive** (1114) | ferramenta | **UNKNOWN** — ausência, não permissão | **NENHUMA** — não existe ficha, contrato ou decisão | índice derivado | **nenhuma** — não traz facto próprio | **quádrupla**: Archive 1114 · Sources 194 · Signal Archive 3 · `searchIndex` 1655 sem menu | **NÃO** | `1114` é um contador de linhas, proibido pelo nome na home | MÉDIO como investigação | `INVESTIGATION_VIEW` **ou** `ADMIN/DIAGNOSTIC` | **M-A** *(não é ferramenta)* / **B** *(qual das duas)* | **quem a abre.** É o que separa as duas |
| S-11 | **Source Register** (194) | ferramenta | **NO** por um contrato · **nível 2** por outro → **conflito C-02** | **PARCIAL** · «de onde vem cada coisa?» **incluindo as bloqueadas, com motivo** | 194 fontes + 66 pessoas + 8 news | `version_state` 5 estados; só um autoriza evento | `people` com S-09 · a palavra «arquivo» com S-10/S-13 | **NÃO** | `sourceGroup` vazio em 84 % | **ALTO** — é o chão de auditabilidade de tudo o resto | **`EVIDENCE_EXPLORER`** — e é por causa dela que a classe passa a existir | **A** | `sourceGroup`: lacuna de dado ou enum errado? |
| S-12 | **Field Sales Channel** (18) | integração · DEMO | UNKNOWN | n/a | 18 fabricadas · `SYNTHETIC_DEMO` | **nenhuma** | — | **NÃO** | nenhum — **4 camadas de honestidade** | ALTO como **direção**, zero como conteúdo | `INTEGRATION`. **Continua corretamente DEMO: SIM** | **A** | a rota `#field` fora de `AMMESSE`: intenção ou defeito? |
| S-13 | **Signal Archive** (3) *fora do menu* | vista de apoio | UNKNOWN | herda de S-03 | 3 sinais | OpenAlex 2 + CELLAR 1 | com S-03, declarada e verificável | partilha o de S-03 | nenhum | prova que **retirar da vista ≠ retirar do produto** | `SUPPORTING_VIEW` | **A** | — |

---

## §2 · A MATRIZ INTELIGÊNCIA → PRODUTO → PROJEÇÃO → SUPERFÍCIE

A leitura que a Bíblia exige: **não** «uma tela por dataset», mas **produtos que
alimentam potes que alimentam superfícies**, em M:N.

### Os Intelligence Products que o repositório já produz (medidos)

| PRODUCT_ID *(proposto)* | o que é | selo? | estado | superfícies que alimenta hoje | poderia alimentar |
|---|---|---|---|---|---|
| `LABEL_AUTHORISED_USE` | 166 produtos · 210 objetos · 54 versões · 22 regras | **SIM** `CONTENT_SHA256` | `ACTIVE` | S-04 | S-01 (elo rótulo) · S-02 (`STRENGTH`) · Ask (B11/B35 e recusas B10/B28) |
| `COMMERCIAL_PRIORITY_CASE` | 43 casos, 17 publicáveis | portão `7/7 + 19` | `ACTIVE` | S-01 | Home · Ask |
| `FUTURE_THEME` | 44 temas ITFC | não | `DEGRADED` — 12 de 13 campos não viajam | S-03 · S-13 | S-01 (porta `CURRENT_FIELD_CONFIRMATION`) |
| `REGULATORY_EXPOSURE` | 163 registos + 47 factos regulatórios + 28 futuros | não | `CANDIDATE` — **sem superfície própria** | (dentro de S-02) | uma ferramenta MT1 própria |
| `COMPETITOR_OBSERVATION` | 577 atividades · 5 estados que não se somam · 5º relógio | não | `ACTIVE` como camada | S-08 | S-01 · S-02 |
| `SCIENCE_CORPUS` | **763** no acervo, 88 servidos, 93.933 ch de abstract que não viajam | não | `DISCOVERED` — atravessava a cadeia com **0 referências** | S-09 (parcial) | S-01 · S-03 |
| `FIELD_VOICE_CORPUS` | 79 vozes · 62 canais · **184 transcrições · 5,03 M ch** | não | `DISCOVERED` | S-07 (parcial) | S-01 · S-03 |
| `CROP_WINDOW` | 29 canónicas · **PROVED 0** | não | `DEGRADED` — origem não auditável | S-05 | S-01 (`SEASONAL TIMING` é INPUT de MT2) |
| `MARKET_PRICE_SERIES` | 157 observações UE | não | `ACTIVE` | S-06 | S-01 |
| `SOURCE_PROVENANCE` | 194 fontes com estado, **incluindo as bloqueadas** | `DATA-CLOCK-manifest` | `ACTIVE` | S-11 | **todas** — é o chão da cadeia |
| `PRODUCT_PORTFOLIO` | 173 produtos · 5402 relações | não | `ACTIVE` | S-02 | S-01 · S-04 · Ask |

### As projeções que já existem (e ninguém lhes chamou isso)

| PROJECTION_ID *(proposto)* | ficheiro real | regenerada por | prova de regeneração | consumida por |
|---|---|---|---|---|
| `PORTAL_MODEL_V21` | `italy-handoff-v21.js` (11,2 MB) | `scripts/site_v21_ingest.py` | **byte-idêntico, portão ligado** | S-01…S-13 |
| `MEETING_SNAPSHOT` | `meeting-intelligence-snapshot.js` | `scripts/meeting_snapshot.py --cutoff` | `meeting-gate 23/23` | S-01 |
| `RELEVANCE_VERDICT` | `adama-relevance.js` | `scripts/adama_relevance.py` (a lei) + `it_casa_dados.py` (o transporte) | `adama-relevance-gate 7/7` | S-01 |
| `CASA_LEDGER` | `italy-casa.js` (495 KB) | `scripts/it_casa_dados.py` | `casa-gate 30/30` | S-03 |
| `LABEL_PAYLOAD` | `italy-label-intelligence.js` (3,8 MB) | `v1/inteligencia/payload.py`, **copiado byte a byte** | `etichette-gate.mjs` recalcula o sha | S-04 |
| `DISPLAY_LAYER` | `italy-i18n.js` + `meeting-labels.js` | 103 regras em `DISPLAY-LAYER-V1.json` | `SEMANTIC_DRIFT_ERRORS = 0` | todas |

> **Seis potes já existem, com gerador e portão. Nenhum se chama pote.**
> A Bíblia não inventa a ponte: **nomeia a que já está construída** e diz o que lhe falta —
> `DROPPED_FIELDS`, `IS_SOURCE_OF_TRUTH = false` explícito, e um `PUBLICATION_MANIFEST`.

### O grafo M:N, medido

```
LABEL_AUTHORISED_USE ──┬──▶ LABEL_PAYLOAD ─────────▶ S-04 Label Intelligence
                       ├──▶ PORTAL_MODEL_V21 ──┬───▶ S-02 Portfolio (STRENGTH)
                       │                       └───▶ S-01 Opportunity Radar (elo)
                       └──▶ (futuro) ASK_INDEX ─────▶ Ask Sintonia

PRODUCT_PORTFOLIO ─────┬──▶ PORTAL_MODEL_V21 ──┬───▶ S-02
                       │                       └───▶ S-01
                       └──▶ (futuro) ─────────────▶ MT1 regulatório

COMMERCIAL_PRIORITY ───┬──▶ RELEVANCE_VERDICT ─────▶ S-01
                       └──▶ MEETING_SNAPSHOT ──────▶ S-01 · Home
```

**Um produto → várias projeções → várias superfícies. Zero recálculos no casco.**

---

## §3 · REAVALIAÇÃO DAS SUPERFÍCIES QUE UM CONTRATO ANTIGO RECUSOU

A correção de 08/09 é explícita: **não matar ferramenta por contrato antigo.**
Cada superfície com `AUTHORITY = NO` foi reavaliada contra os seis testes.

### Os seis testes

```
T1  o contrato antigo ainda é autoridade?
T2  a capacidade evoluiu depois?
T3  surgiu inteligência nova?
T4  a ferramenta ganhou decision question real?
T5  há valor que não existia quando o contrato foi escrito?
T6  o contrato precisa de ser atualizado?
```

### S-06 · MARKET PULSE

| teste | resposta |
|---|---|
| T1 | **SIM.** `ARQUITETURA-DE-PRODUTO-ATUAL` é porta única e diz duas coisas: «market/crop context» está no SUPPORTING ENGINE, e `DO NOT BUILD` inclui «crop pulse genérico» |
| T2 | pouco — 157 observações, mesma fonte |
| T3 | **NÃO** — nenhuma inteligência nova sobre preço desde 29/08 |
| T4 | **NÃO** |
| T5 | não medido |
| T6 | não |

> **VEREDITO: a recusa mantém-se, e não por inércia.**
> É o único caso em que o contrato antigo e a medição de hoje **concordam**.
> `CONTEXT_VIEW`. **Confiança M-A.**
> Ressalva: `CAP-019` cobre FRANCE e SPAIN e **não cobre a Itália**, que é o país do
> portal. A superfície existe sem capacidade provada para o seu próprio país.

### S-07 · FIELD VOICES

| teste | resposta |
|---|---|
| T1 | **NÃO, e é decisivo.** A ficha dizia `CONCEPT — sem fonte de dado`; a arquitetura dizia **`NOT REACHED / NÃO SEI, não KILL`** e acrescentava «Apify não foi testado. É preciso testar antes de decidir» |
| T2 | **SIM, radicalmente.** 79 vozes canónicas · 62 canais · 184 transcrições · 5.033.374 ch de fala |
| T3 | **SIM** — resolução de cultura a 98,7 %, `factCountry`, a escada de 5 degraus |
| T4 | **AINDA NÃO ESCRITA**, mas há candidata forte |
| T5 | **SIM** |
| T6 | **SIM, urgentemente** |

> **VEREDITO: A RECUSA ERA DE FONTE, NÃO DE IDEIA — E A FONTE CHEGOU.**
> Manter `AUTHORITY = NO` hoje seria aplicar a um mundo com dado uma recusa escrita para
> um mundo sem dado.
> **A ficha tem de ser reaberta.** Isso não a promove a ferramenta: põe-na em
> `CANDIDATE`, que é o estado correto.
> Bloqueadores reais e mensuráveis: baseline (a régua de alerta não abre a porta
> BASELINE em nenhuma família de conversa pública) · denominador (79 de quantos?) ·
> GDPR (P-008 e P-009 ABERTAS). **Confiança B.**

### S-08 · COMPETITOR WATCH

| teste | resposta |
|---|---|
| T1 | **SIM** — `EAME-COMPETITOR-CONTRACT-V1` (30/08) + `D-021`, ambos explícitos |
| T2 | **SIM** — 414 → 577; crosswalk de 1.683 cadeias em 3 países |
| T3 | **SIM** — o 5º relógio, os 5 estados de ativação, 36 cadeias de 3 camadas prontas |
| T4 | **NÃO** como ferramenta; **SIM** como camada |
| T5 | **SIM** |
| T6 | **SIM, mas para PRECISAR, não para afrouxar** |

> **VEREDITO: o contrato não proíbe a superfície. Proíbe o NÚMERO ÚNICO e o RANKING.**
> Ler «não é uma ferramenta isolada» como «não pode haver ecrã» é uma leitura mais dura
> do que o texto. Um `INVESTIGATION_VIEW` sobre uma camada transversal é legítimo:
> permite varrer, não emite juízo, não tem autoridade própria.
> **O que viola o contrato hoje é o `577` no menu.** É um contador, não uma superfície.
> **Confiança M-A.**

### S-09 · SCIENTIFIC INTELLIGENCE

| teste | resposta |
|---|---|
| T1 | **SIM para produto** — «science · experts» está no SUPPORTING ENGINE. Mas foi escrito quando o corpus era 88, não 763 |
| T2 | **SIM** — 88 → 763 no acervo; 88/88 ganharam link para o paper |
| T3 | **SIM** — `caseAdherence`, `countryOfFact`, o bloco «Cosa si sa oltre il caso» |
| T4 | `CAP-017` **é** uma decision question de R&D e TEC — **mas cobre FR e ES, não IT** |
| T5 | **SIM** — ligar ciência a caso com *luogo del fatto* declarado por linha |
| T6 | **SIM** |

> **VEREDITO: NÃO É KILL. É UM CONTRATO POR ESCREVER.**
> A instrução de 08/09 é explícita e aplica-se inteira aqui: não descartar a
> possibilidade de ser ferramenta legítima só porque um documento antigo lhe chamou
> motor de suporte.
> Requisitos para promover: contrato próprio · estender `CAP-017` à Itália · resolver
> os **39/88 `OFF_CASE`** · fechar GDPR P-008.
> **Confiança M. Precisa de medição de UTILIZADOR, não de dado.**

### S-11 · SOURCE REGISTER

| teste | resposta |
|---|---|
| T1 | **EM CONFLITO** — a porta única põe-na no motor de suporte e a home proíbe «contador de fontes»; o `DESIGN-DATA-CONTRACT` (um dia depois) dá-lhe nível 2, ordem 4, com estados GREEN/PARTIAL/BLOCKED |
| T2 | 189 → 194 |
| T3 | `version_state` com 5 estados |
| T4 | **SIM, e é de outra natureza:** «de onde vem cada coisa?» **incluindo as fontes bloqueadas, com motivo** |
| T5 | **SIM** |
| T6 | **SIM** |

> **VEREDITO: a proibição da HOME não é uma proibição da SUPERFÍCIE.**
> «Contador de fontes» é proibido na home. A superfície de proveniência é outra coisa —
> e o contrato de design dá-lhe entrada de nível 2 no dia seguinte.
> **Foram lidas como a mesma coisa e não são.**
> `EVIDENCE_EXPLORER`. **Confiança A.** Conflito C-02 registado, não resolvido.

### Resumo da reavaliação

```
SUPERFÍCIES COM AUTHORITY = NO REAVALIADAS ......... 5
RECUSAS CONFIRMADAS ................................ 1   S-06 (e o contrato concorda com a medição)
RECUSAS QUE TÊM DE SER REABERTAS ................... 3   S-07 · S-09 · S-11
RECUSA MAL LIDA (o contrato dizia menos) ........... 1   S-08

FERRAMENTAS DESCARTADAS SÓ PORQUE UM CONTRATO ANTIGO
NÃO GOSTAVA DELAS .................................. 0
```

---

## §4 · A MATRIZ DOS QUATRO PÚBLICOS

O teste do §16 da Bíblia aplicado. **A parte comum é o produto. A parte que difere é o
pote.**

### `LABEL_AUTHORISED_USE`

| público | o que precisa | projeção | superfície |
|---|---|---|---|
| REG | o que mudou no rótulo, com decreto e citação literal | `versions` 54 + `by_type` | S-04 |
| TEC | que cultura × alvo está autorizada, com prova geométrica | `uses` + `pair_check` + `crop_check` | S-04 |
| MD | se há resposta ADAMA registada para um par | o elo da cadeia | **S-01** |
| COM | o que se pode dizer ao produtor sem exceder o rótulo | `FORBIDDEN_CLAIMS` + `ceilings` | *(por construir)* |

**Quatro públicos · um produto · quatro potes · zero ferramentas novas.**

### `COMMERCIAL_PRIORITY_CASE`

| público | o que precisa | projeção | superfície |
|---|---|---|---|
| MD | os 17 com cadeia fechada, ordenados por relevância | `RELEVANCE_VERDICT` classe A | S-01 |
| COM | o que fazer, onde, com que produto | *(por construir — é o que o `brief` legado tentava)* | — |
| MKT | que par cultura × alvo merece comunicação e o que **não** se pode dizer | `FORBIDDEN_CLAIMS` + `ACTIVATION_QUESTION` | *(por construir)* |
| LEAD | quantos, de que classe, e o que ficou de fora e porquê | `PER_CLASSE` + as 611 justificações de exclusão | Home |
| CTRL | o que é comparável entre países | **`EAME_CROSS_MARKET_READY = NO`, 0 relações** | *(vazia, e tem de aparecer vazia)* |

> **Cinco públicos, uma inteligência, cinco projeções — e duas ainda não existem.**
> Nenhuma delas exige uma ferramenta nova. Exigem um Product Contract e um pote.

---

## §5 · A MATRIZ DE RISCO

Ordenada por custo do erro, não por probabilidade.

| # | risco | superfícies | por que dói | guarda hoje | executável? |
|---|---|---|---|---|---|
| R-01 | dizer que o cliente **não tem produto** para um alvo quando tem | S-02 · S-04 · S-01 | é o pior erro possível do sistema; foi pago no Brasil (Nimitz EC: 3 culturas no catálogo, 19 no registo) | `EXPLICIT_SPECIES_RESPONSE = NONE` não pode ler-se «a ADAMA não tem produto» (`CONTRATO-DE-DESIGN §7.4`) | **prosa** |
| R-02 | uso autorizado lido como oportunidade comercial | S-04 → S-01 | é a junção que parece óbvia e é falsa | **`FORBIDDEN_CLAIMS` no payload + portão G-01 fechado** | **SIM** |
| R-03 | contador lido como valor | S-08 (577) · S-10 (1114) · S-11 (194) | a home proíbe pelo nome; a barra imprime | proibição em prosa | **prosa** |
| R-04 | `HISTORICAL` lido como `CURRENT` | S-06 · S-08 | azeite de 2015 como preço corrente; 27 selos ATTIVO sem data | classe temporal obrigatória (migration 021, **não executada**) | **não** |
| R-05 | ausência lida como conclusão | todas | «não achámos em 102 de 163» ≠ «0 de 163» | `AM.ABSENCE_RULE` + 5 estados de desconhecimento | **parcial** |
| R-06 | termo de busca lido como achado | S-09 | 39/88 `OFF_CASE`; 87/88 `QUERY_*` vs 37/88 `PROVED_*` | medido e declarado | **medido, não travado** |
| R-07 | duas telas, duas listas, mesmo cartão | S-01 | `casa.html` 65 × `portale.html` 280 | nenhuma | **não** |
| R-08 | janela aberta lida como necessidade de aplicação | S-05 | `WINDOW_OPEN ≠ CURRENT_NEED` | pastilha verde removida (6 promessas falsas → 0) | **SIM** |
| R-09 | build publicado sem manifesto | todas | duas linhagens vivas e nada declara qual é o portal | nenhuma | **não** |
| R-10 | pessoa nomeada em ecrã público | S-09 · S-07 | GDPR | `NAMED_RESEARCHER_PUBLIC_SCREEN = BLOCKED_PENDING_LEGAL_REVIEW` | **prosa; e não é parecer jurídico** |

**Placar dos guardas:** 3 executáveis · 1 parcial · 6 em prosa ou ausentes.

---

## §6 · O QUE PRECISA DE MEDIÇÃO ANTES DE SE DECIDIR

Sete das treze superfícies. **Não é indecisão: é o estado correto de um repositório sem
telemetria.**

| superfície | a pergunta que só a medição responde | como se mede |
|---|---|---|
| S-02 Portfolio | ferramenta MT1 ou superfície de referência? | quem a abre, vindo de onde, e o que faz a seguir |
| S-05 Crop Windows | ferramenta ou componente temporal? | **primeiro o gerador.** Sem proveniência não há o que decidir |
| S-06 Market Pulse | alguém decide algo aqui? | `INVESTIGATED` e `ACTIONED`, nunca cliques |
| S-07 Field Voices | sensor, explorador de evidência, ou ferramenta? | se uma voz alguma vez muda uma decisão — hoje `USED_AS_EVIDENCE = false` em 184/184 |
| S-09 Scientific Int. | ferramenta de R&D ou visualização da coleta? | se R&D/TEC a abrem sozinhos ou só a partir de um caso |
| S-10 Archive | investigação ou admin? | **quem é o público.** É o que separa as duas |
| S-11 Source Register | quantos factos permitem saltar para aqui? | cobertura de `EvidenceLink` por superfície |

> **`TELEMETRY_EXISTS = NO`.**
> Enquanto for `NO`, nenhuma superfície pode entrar em `PILOT` (§9 LC-02) e nenhuma
> destas sete perguntas tem resposta. **É a dívida nº 1 da entrega.**

---

## §7 · O PLACAR DA MATRIZ

```
SUPERFÍCIES MEDIDAS ................................ 13   (12 no menu + 1 fora)

RECOMENDADAS COMO CANONICAL_TOOL ................... 2    S-01 · S-04
RECOMENDADAS COMO EXPLORATORY_TOOL ................. 1    S-03
RECOMENDADAS COMO CONTEXT_VIEW ..................... 2    S-05 · S-06
RECOMENDADAS COMO SUPPORTING_VIEW .................. 1    S-13
RECOMENDADAS COMO EVIDENCE_EXPLORER ................ 1    S-11
RECOMENDADAS COMO INVESTIGATION_VIEW / ADMIN ....... 1    S-10
RECOMENDADAS COMO CROSS-CUTTING LAYER + VIEW ....... 1    S-08
RECOMENDADAS COMO INTEGRATION (DEMO) ............... 1    S-12
SEM RECOMENDAÇÃO — precisam de medição ............. 3    S-02 · S-07 · S-09

CONFIANÇA ALTA ..................................... 5    S-01 · S-03 · S-04 · S-11 · S-12 · S-13
CONFIANÇA MÉDIA-ALTA ............................... 3    S-06 · S-08 · S-10
CONFIANÇA MÉDIA .................................... 2    S-05 · S-09
CONFIANÇA BAIXA .................................... 2    S-02 · S-07

INTELLIGENCE PRODUCTS IDENTIFICADOS ................ 11
    ACTIVE 6 · CANDIDATE 1 · DEGRADED 2 · DISCOVERED 2
DELIVERY PROJECTIONS QUE JÁ EXISTEM ................ 6   (com gerador e portão)
PROJEÇÕES COM PROVA DE REGENERAÇÃO ................. 6/6
PROJEÇÕES COM `DROPPED_FIELDS` DECLARADO ........... 1/6  (as 611 justificações)

FERRAMENTAS DESCARTADAS POR CONTRATO ANTIGO ........ 0
TELAS PROMOVIDAS AUTOMATICAMENTE A FERRAMENTA ...... 0
```

### As três frases desta matriz

**Primeira.** Duas superfícies de treze são recomendadas como ferramenta canónica — e uma
delas nasceu anteontem. **A doutrina antiga acertou no número e errou no critério:** o
critério não é «quantas», é `HAS_OWN_DECISION_QUESTION`.

**Segunda.** Seis potes já existem, com gerador e portão, e nenhum se chama pote. A ponte
`INTELLIGENCE → DELIVERY` **não é para construir: é para nomear e completar.** Falta-lhe
`DROPPED_FIELDS`, `IS_SOURCE_OF_TRUTH = false` explícito, e um manifesto de publicação.

**Terceira.** Três superfícies não recebem recomendação, e isso é o resultado, não uma
falha. Sem telemetria, `Portfolio`, `Field Voices` e `Scientific Intelligence` são
decisões que ninguém — nem esta pesquisa — tem prova para tomar.
**`UNKNOWN` continua `UNKNOWN`.**
