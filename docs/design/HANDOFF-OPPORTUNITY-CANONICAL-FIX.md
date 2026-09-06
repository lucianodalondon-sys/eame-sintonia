# Handoff · as correções de Opportunity para a linhagem que gera o pacote

```
SOURCE_BRANCH  claude/auditoria-acervo-inteligencia-2nknje
SOURCE_HEAD    b7ba9115f02187d7d5f9ff09a63a820b63601b72
TARGET_BRANCH  claude/opportunity-commercial-priority-v1
TARGET_BASE    55c2674b785a3a373ef0bad2812c244ed80c31eb
```

`55c2674` é exatamente o SHA que `scripts/v21_cadeia.sh` já nomeia como gerador
canónico. Ele não se moveu desde então: o alvo deste handoff é o mesmo que o
repositório declara há semanas.

> **ESTE HANDOFF NÃO FOI ESCRITO CONTRA UM ALVO IMAGINADO.**
> O gerador canónico foi trazido, corrido, corrigido e corrido outra vez. Tudo
> o que se segue está medido contra ele, não contra a nossa cópia.

---

## 0 · O que já foi provado contra o alvo real

O gerador canónico foi extraído para uma árvore descartável, alimentado com o
`DESIGN-INGEST` reconstruído do ZIP versionado, e corrido **antes e depois** da
correção:

| | antes | depois |
|---|---:|---:|
| registos emitidos | 83 | **83** |
| mesmos IDs | — | **sim** |
| cartões com mudança em `PORTFOLIO_MATCHES`, `PRODUCT_RELATIONSHIPS`, `PRIMARY_MATCH`, `STATUS`, `OPPORTUNITY_STATE` ou `OPPORTUNITY_SCORE` | — | **0** |
| a conta do portfólio fecha | não existia | **83 / 83** |
| famílias consultadas por cartão | 14 carregadas, 13 usadas | **24 consultadas** |
| cartões que declaram a própria omissão | 0 | **10** |

E os 8 testes de motor correm **verdes contra o gerador canónico corrigido**.

`CHERRY_PICK_SAFE` deixou de ser opinião: é resultado.

---

## 1 · O que deve ser transportado

### A · Código que vai direto

| | |
|---|---|
| **`CHANGE_ID`** | `OPP-01` · varredura de portfólio declarada |
| `SOURCE_FILE` | `scripts/v21_oportunidades.py` |
| `SOURCE_COMMIT` | `40539e0` |
| `TARGET_OWNER` | o mesmo ficheiro, em `55c2674` |
| `TARGET_FILE` | `scripts/v21_oportunidades.py` (linha 1365, `produtos[:12]`) |
| `WHY` | o corte existe nos dois lados e não declara nada. Um total sem contador lê-se como total. |
| `FACT_PROVED_BY` | 10 cartões cortados, 81 produtos removidos — reconstruindo a entrada arquétipo a arquétipo |
| `BEHAVIOR_BEFORE` | `PRODUCT_RELATIONSHIPS` traz ≤12 nomes e nenhum campo diz que houve corte |
| `BEHAVIOR_AFTER` | mais `PORTFOLIO_SCAN_{FOUND,LINKED,NOT_LINKED,UNKNOWN}` + `PORTFOLIO_LIST_{CAP,TOTAL_BEFORE_CAP,OMITTED,OMITTED_NAMES}`; a lista servida **não muda** |
| `RISK` | baixo — só acrescenta chaves; um `assert` falha alto se a conta não fechar |
| **`CHERRY_PICK_SAFE`** | **SIM — aplicado e corrido em `55c2674`, zero drift** |

| | |
|---|---|
| **`CHANGE_ID`** | `OPP-02` · consulta a todas as famílias do pacote |
| `SOURCE_FILE` · `SOURCE_COMMIT` | `scripts/v21_oportunidades.py` · `40539e0` |
| `TARGET_FILE` | mesmo ficheiro; a lista de 14 coleções é **byte-idêntica** nas duas linhagens |
| `WHY` | onze famílias existiam no pacote e nunca eram lidas; `PUBLIC-VOICES` era lida e deitada fora. Sem consulta, «não encontrei» é indistinguível de «não olhei». |
| `FACT_PROVED_BY` | 14 carregadas / 13 usadas → 24 consultadas; `MOTOR_CARREGA_E_NAO_TOCA` passa de 12 para 0 |
| `BEHAVIOR_BEFORE` | nenhum registo de consulta |
| `BEHAVIOR_AFTER` | `CROSS_INTELLIGENCE_SCAN` com `MATCH` / `CROP_ONLY` / `NOT_FOUND` / `NO_CROP_KEY` por família |
| `RISK` | baixo — **não entra** em `EVIDENCE_IDS`, no score, nos portões nem no estado. Um teste guarda isso. |
| **`CHERRY_PICK_SAFE`** | **SIM — mesma prova** |

**O patch pronto, já rebasado para o alvo:**
`docs/design/handoff/01-opportunity-scan-para-55c2674.patch`
`sha256 042415fa99ede733c78841d19e2d88080e89210b32eaedabdd7a1abd737f0b05`

Cinco hunks. Aplicado com `git apply` sobre `55c2674` sem conflito nem fuzz.
(O diff cru de `40539e0` aplica 4 de 5; o quinto falhava só por contexto de
cauda — `estado_temporal` aqui, `estado_de_acao` lá. Este patch já traz a cauda
canónica.)

### B · Código que precisa ser reimplementado no dono canónico

| | |
|---|---|
| **`CHANGE_ID`** | `OPP-03` · O5 associa produto de outra cultura ao cartão |
| `TARGET_FILE` | `scripts/v21_oportunidades.py:1663` — `crops[0] if len(crops) == 1 else None` |
| `WHY` | o cartão recebe uma cultura quando a substância toca **uma só**, mas lista **todos** os produtos que a contêm, venham da cultura que vierem |
| `FACT_PROVED_BY` | 4 cartões, 6 produtos: VINETO (videira) num cartão POMODORO; POSTSCRIPT 80 e 80 XL (milho/arroz/girassol) num cartão SOIA; STAVENTO (frumento) e SOLOFOL AP (sem cultura) num cartão **VITE**; ANTARKTIS (sem cultura) num cartão ORZO |
| `BEHAVIOR_AFTER` (proposto) | ou o cartão O5 **não** recebe cultura, ou `PRODUCT_RELATIONSHIPS` é filtrado pela cultura do cartão e os excluídos vão para `EXCLUDED_WITH_REASON` |
| `RISK` | **médio — muda a lista servida.** Não foi corrigido aqui de propósito. |
| **`CHERRY_PICK_SAFE`** | **NÃO** — não existe patch; existe a medição e o sítio exato |

> **Onde isto aparece e onde não:** os 6 estão em `PRODUCT_RELATIONSHIPS` (logo em
> `portale.html`), e **nenhum** chega a `PORTFOLIO_MATCHES` (logo nenhum aparece em
> `casa.html`). O casamento com o catálogo apanha-os **por acidente, não por
> regra** — é o mesmo filtro que apaga produtos legítimos a apagar estes.
> **UM FILTRO QUE ACERTA POR ACIDENTE NÃO É UM PORTÃO: É SORTE COM SINTAXE.**

| | |
|---|---|
| **`CHANGE_ID`** | `OPP-04` · catálogo perde 656 pares produto × cultura |
| `TARGET_OWNER` | `scripts/adama_catalogo_montar.py` (produz) → `scripts/v21_ingest.py:292` (transporta) |
| `RISK` | **alto — muda `CROP_FIT` e portanto o que o ecrã mostra** |
| **`CHERRY_PICK_SAFE`** | **NÃO** — ver §4 |

### C · Medidores e testes que podem acompanhar

| `CHANGE_ID` | ficheiro | nota |
|---|---|---|
| `OPP-05` | `tests/test_completude_oportunidade.py` — classes `TestVarreduraDoMotor` e `TestCruzamentoDeInteligencia` | **8 testes, verdes contra `55c2674` corrigido.** Vão direto. |
| `OPP-06` | mesma classe `TestMedidaPublicada` (4 testes) | depende de `data/samples/IT-COMPLETUDE/…json`. Portar **só** se o medidor for junto. |
| `OPP-07` | `scripts/v21_completude_oportunidade.py` | lê o pacote **servido**, não o motor. Útil como régua independente; opcional. |

### D · Achados que NÃO devem virar código ainda

| | achado | porquê fica |
|---|---|---|
| `OPP-08` | **duas telas vivas, duas listas** — `casa.html` mostra `PORTFOLIO_MATCHES` (65 lugares nos 43 cartões), `portale.html` cai em `PRODUCT_RELATIONSHIPS` (280). Divergem nos 43. | é decisão de produto, não defeito de motor: qual das duas é a lista verdadeira? |
| `OPP-09` | `PUBLIC-VOICES` continua sem fundar caso | promovê-la muda vereditos publicados |
| `OPP-10` | a régua de red team «voz isolada tratada como incidência» é inalcançável enquanto `OPP-09` não mudar | corrigir a régua sem a causa seria mexer no sintoma |

---

## 2 · Requisitos que o handoff carrega

1. **Varredura completa por Opportunity** — `OPP-01`, feito e provado.
2. **Contabilidade explícita** — `FOUND` / `LINKED_TO_TARGET` / `CROP_ONLY` /
   `UNKNOWN` / `SHOWN` estão em `OPP-01`. **`EXCLUDED_WITH_REASON` ainda não
   existe como campo**: hoje a razão da exclusão vive em
   `PORTFOLIO_SCAN_NOT_LINKED_REASON` (uma frase por cartão), não produto a
   produto. **Fica como requisito por cumprir.**
3. **Nenhum corte silencioso** — `OPP-01` cobre `produtos[:12]`. **Ficam por
   cobrir**, medidos e não corrigidos: `SOURCE_URLS[:12]`, `prods[:6] + rot[:4]`
   no O5, e a fusão primeiro-facto-ganha.
4. **Normalização VITE / Vite da vino / Vite da tavola / VINE** — **não feita**,
   e de propósito: a ponte que a medição usa
   (`v21_completude_oportunidade.py`, tabelas `CATALOGO_CROP` e `VIDEO_CROP`)
   serve para **medir** o que a falta de normalização esconde. Promovê-la a
   normalizador do pacote é `OPP-04`, e exige a prova produto a produto.
5. **Defeito O5** — `OPP-03`, sítio exato entregue, correção não feita.
6. **Ausência no catálogo rastreado ≠ ausência no catálogo ADAMA** — `OPP-04`.
7. **Consultar todas as famílias e registar** — `OPP-02`, feito. Nota honesta:
   os quatro estados servidos são `MATCH` / `CROP_ONLY` / `NOT_FOUND` /
   `NO_CROP_KEY`. **`MATERIAL_EXISTENTE_NAO_UTILIZAVEL` não aparece no motor**
   porque as famílias que o justificam (vídeo, transcrição, censo) **não estão
   no pacote** — não há família para perguntar. O estado existe no medidor.
8. **Não promover vídeo/transcrição como evidência** — cumprido por construção:
   nenhuma das duas está no pacote, e `CROP_ISSUE_BASIS` diz que o par vem do
   termo de busca. Se um dia forem ingeridas, este requisito passa a ter dentes.
9. **Catálogo/rótulo nunca como campo independente** — já é lei em `55c2674`
   (`TIPOS_QUE_OBSERVAM` vs `TIPOS_DE_AUTORIZACAO`). `OPP-02` **não** a afrouxa:
   o scan não entra na evidência.
10. **Preservar `CLIENT_SAFE` e os portões** — preservado. O scan lê de `cs`,
    que já é o conjunto filtrado, e não toca em portão nenhum.

---

## 3 · Testemunhas obrigatórias

### A · VITE DA VINO

```
VITE_DA_VINO_TOTAL_PRODUCTS = 71
  registo ministerial 61 · rótulo 25 · censo «Vite da vino» 15 · catálogo no pacote 10
```

O que o teste tem de provar, e o estado de cada parte:

| exigência | estado |
|---|---|
| o motor encontra o universo relevante | **parcial** — `PORTFOLIO_SCAN_FOUND` cobre o rótulo (25). As outras três casas ficam fora até `OPP-04`. O campo declara esse limite na própria lei. |
| explica cada redução | **feito** — `PORTFOLIO_LIST_*` explica o corte; a redução do catálogo é de `OPP-04` |
| não apresenta 1 produto como se só 1 existisse | **feito no motor** (o cartão passa a dizer quantos achou); **não feito no ecrã** — é `OPP-08` |
| produto para VITE ≠ produto para o alvo | **feito** — `LINKED` exige o par no rótulo; sem alvo é `UNKNOWN`, nunca `LINKED` |

`VITE_WITNESS_READY = PARCIAL`. O teste de regressão que falta é o que fixa
**71** como universo das quatro casas — e ele só pode existir depois de `OPP-04`,
porque hoje o motor não vê três das casas. Escrevê-lo agora seria fixar um
número que o motor não pode produzir.

### B · MAIS × PIRALIDE × FRIULI-VENEZIA GIULIA

```
cartão      OPP_9C600748BB1B
sinal       IT-PHEN-048 (ERSA FVG, 2026-08-12)
limiar      «trattamento giustificato oltre 3 ovideposizioni / 100 piante»
produtos    5 no par — DURAVIS · ELTIRA · FORZA · LAMDEX EXTRA · NINJA
no ecrã     1 (Lamdex® Extra, único que casa com o catálogo)
janela      NÃO SEI — o pacote tem 7 janelas, nenhuma de milho
anúncios    70 peças de milho, 2 ativas, ambas institucionais → NÃO entram
```

`MAIZE_WITNESS_READY = SIM` — as cinco exigências são verificáveis com o que já
existe: o sinal e o limiar estão em `IT-PHEN-048`; os 5 produtos saem de
`rot_por_par`; a janela é `WINDOW_STATE = UNKNOWN` sem registo; e nenhum campo
do motor lê contagem de anúncio (o O4 usa concorrência, este cartão é O1).

---

## 4 · O catálogo, e os 656 pares

```
CATALOG_OWNER   scripts/adama_catalogo_montar.py  (CULTURA_PAGINA → linha 238)
                → scripts/v21_ingest.py:292       (transporta para o pacote)
                → scripts/v21_comercial.py:293    catalogo_declara_cultura()
                → CROP_FIT em PORTFOLIO_MATCHES

CURRENT_FIELD       CROPS_DECLARED_ON_SITE
CURRENT_SEMANTICS   «em que PÁGINA DE CULTURA encontrei este produto»,
                    e só sete páginas de cultura foram lidas
WRONG_DOWNSTREAM_INTERPRETATION
                    «que culturas a ficha do produto declara»
                    → e daí «o produto não pertence a esta cultura»

FULL_CENSUS_PAIRS   711     (CROPS_DECLARED_ON_PAGE, 149 culturas distintas)
PACKAGE_PAIRS        55     (7 culturas: CEREALI MAIS POMACEE POMODORO RISO SOIA VITE)
LOST_PAIRS          656
```

**Onde a correção precisa acontecer:** em `adama_catalogo_montar.py`, alimentando
`CULTURAS_DECLARADAS_NO_SITE` a partir de `CROPS_DECLARED_ON_PAGE` do censo —
que já está versionado em
`data/samples/IT-CATALOGO/IT-ADAMA-CATALOG-CENSUS-2026-09-02.json` — em vez de
`CULTURA_PAGINA`. Nada a jusante muda de forma; muda de conteúdo.

O próprio ficheiro já declara o limite, e com todas as letras:

> `CULTURA_LEIA_ASSIM`: «chegamos a este produto por link de outra ficha, não por
> página de cultura. Não ter cultura aqui **NÃO significa** que ele não tenha.»

> **A DECLARAÇÃO ESTAVA CERTA. O CONSUMIDOR A JUSANTE É QUE NÃO A LEU.**
> «não encontrei o produto por esta página de cultura» **não pode** virar
> «o produto não pertence à cultura».

Cinco produtos que declaram «Vite da vino» na própria ficha e nunca chegaram
como videira: Activus® ME (chega com MAIS/POMODORO/RISO/SOIA), Leopard® 5 EC e
Taifun® MK CL PFNPE (`CROP_IDS = []`), Nimrod® 250 EW e Cosayr® 200 SC (sem
`CROP_IDS`).

**Não corrigido aqui**: mexe em `CROP_FIT`, logo em `PORTFOLIO_MATCHES`, logo no
ecrã. Precisa de decisão sobre o que fazer com as 142 culturas que entrariam.

---

## 5 · `PORTFOLIO_MATCHES` e `PRIMARY_MATCH`

```
PORTFOLIO_MATCHES_OWNER  portfolio()  em scripts/v21_oportunidades.py:535
                         do gerador canónico 55c2674 — NÃO existe nesta linhagem
PRIMARY_MATCH_OWNER      a mesma função (devolve matches, primário, razão)
GENERATOR_FILE           scripts/v21_oportunidades.py @ 55c2674, atribuído em :1438-1440

INPUTS   o (o cartão) · rotulos (linhas de rótulo do caso)
         casados  ← CM.casar(rotulos, ix_comercial), v21_comercial.py:191
                    junta por NÚMERO DE REGISTO contra o catálogo de 51 produtos
         ai_por_prod · ai_por_id · ativos_da_fonte
         CM.catalogo_declara_cultura(CROP, [p])  → CROP_FIT

OUTPUTS  PORTFOLIO_MATCHES · PRIMARY_MATCH · PRIMARY_MATCH_REASON
         → meeting_snapshot.py (lista de permissão, campo a campo, linha 74)
         → it_casa_dados.py:617-630  → italy-casa.js PRODOTTI  → casa.html
```

`meeting_snapshot.py` e `it_casa_dados.py` **copiam verbatim**. Não há filtro de
tela: a redução 280 → 65 acontece **dentro do motor**, no casamento por número de
registo.

**Correção da redução errada, sem mexer no significado regulatório/comercial:**

1. A regra «só se oferece o que está no catálogo» **fica**. É comercialmente
   correta e é o que separa autorização de oferta.
2. O que muda é **contra que catálogo** ela corre: hoje corre contra 55 pares;
   deve correr contra 711 (`OPP-04`). Dos 65 sobreviventes atuais, **24 já são
   `LABEL_ONLY` com `CROP_FIT: UNKNOWN`** — o catálogo tem o produto e não
   declara a cultura. Esses 24 são a medida do defeito a chegar ao ecrã.
3. O que falta é **contador**: `portfolio()` deve devolver também
   `PORTFOLIO_EXCLUDED_COUNT` e `PORTFOLIO_EXCLUDED_WITH_REASON`, para que
   «1 produto» nunca mais se leia como «existe 1 produto».
4. `PRIMARY_MATCH_REASON` já é honesto — `SEM_REGRA_DEFENSAVEL_PARA_ESCOLHER`
   em 26 dos 43. **Isso não é defeito e não deve ser «corrigido».**

---

## 6 · O que NÃO entra

`DO_NOT_PORT`: reconstrução do Radar Futuro · novos 45 casos futuros ·
promoção de `PUBLIC-VOICES` a evidência · ingestão dos 1.115 vídeos ·
ingestão das 48 transcrições · qualquer mudança de veredito publicado sem
prova nova.

Também não entra a alteração da outra missão nesta branch
(`italia-portale/audit/casco/…`, `italy-app-model.js`, `portale.html`,
`CASCO-CLIENT-DEMO.md`) — é casco, não motor, e foi rebasada, não sobreposta.

---

## 7 · Sequência recomendada

```
1  git checkout claude/opportunity-commercial-priority-v1     # em 55c2674
2  git apply docs/design/handoff/01-opportunity-scan-para-55c2674.patch
3  copiar tests/test_completude_oportunidade.py
   e remover a classe TestMedidaPublicada (depende do medidor)
4  python3 -m unittest tests.test_completude_oportunidade -v   → 8 verdes
5  correr a cadeia e comparar o pacote com o anterior:
   esperado ZERO diferença em PORTFOLIO_MATCHES, PRODUCT_RELATIONSHIPS,
   PRIMARY_MATCH, STATUS, OPPORTUNITY_STATE e OPPORTUNITY_SCORE
   — só chaves novas. Se houver diferença, PARAR: o patch não é isso.
6  commit  «o corte passa a ter contador, e as familias a ser perguntadas»
--- só depois, e cada um com a sua decisão ---
7  OPP-03  o defeito O5                     (muda a lista servida)
8  OPP-04  o catálogo, 656 pares            (muda CROP_FIT e o ecrã)
9  OPP-08  qual das duas telas é a verdadeira
```

Os passos 1–6 são um commit só e não mudam nada do que se vê. Os 7–9 são
decisões, não transportes.

---

## 8 · Veredito

```
OPPORTUNITY_AUDIT_COMPLETE = SIM
HANDOFF_READY              = SIM

TARGET_BRANCH     claude/opportunity-commercial-priority-v1
TARGET_BASE_HEAD  55c2674b785a3a373ef0bad2812c244ed80c31eb

DIRECT_CHERRY_PICK_COMMITS
  nenhum commit inteiro — 40539e0 mistura motor, relatório e testes.
  Em vez disso: docs/design/handoff/01-opportunity-scan-para-55c2674.patch
  (OPP-01 + OPP-02), já rebasado para o alvo, aplicado e corrido nele.

REIMPLEMENT_REQUIRED
  OPP-03  defeito O5, v21_oportunidades.py:1663 do alvo
  OPP-04  catálogo, adama_catalogo_montar.py (656 pares)
  requisito 2  EXCLUDED_WITH_REASON produto a produto
  requisito 3  os outros três cortes silenciosos

TESTS_TO_REUSE
  TestVarreduraDoMotor (4) e TestCruzamentoDeInteligencia (4)
  — 8 testes, JÁ CORRIDOS VERDES contra 55c2674 corrigido
  TestMedidaPublicada (4) só com o medidor junto

VITE_WITNESS_READY   PARCIAL — o número 71 exige OPP-04 para ser produzível
MAIZE_WITNESS_READY  SIM

CATALOG_656_FIX_OWNER_IDENTIFIED   SIM · adama_catalogo_montar.py:238
PORTFOLIO_MATCHES_OWNER_IDENTIFIED SIM · portfolio() @ 55c2674:535
PRIMARY_MATCH_OWNER_IDENTIFIED     SIM · a mesma função, :1438-1440

RADAR_FUTURO_DEFERRED = SIM
PORTAL_TOUCHED        = NÃO
DEPLOY                = NÃO
```
