# ADJUDICAÇÃO DO BENCHMARK — BÍBLIA DA ENTREGA V0.2

```
DOCUMENT_STATUS   DRAFT
DOCUMENT_TYPE     CORE CONSTITUTION · registo de deliberação
DATE              2026-09-08
INPUT             research/product-tools-benchmark-v1 @ 6ef8e70
                  16 sistemas · 26 fontes primárias · 7 artefactos · 3.200 linhas
IMPLEMENTATION    NONE
```

> **REGRA DESTE FICHEIRO.**
> `O BENCHMARK NÃO ESCREVE A CONSTITUIÇÃO. ELE TRAZ EVIDÊNCIA.`
> Nada foi canonizado por vir do benchmark. Cada recomendação foi julgada uma a uma,
> com veredito, destino e motivo. Um `ACCEPT` sem motivo escrito não é um `ACCEPT`.

**Vereditos:** `ACCEPT` (entra como está) · `REFINE` (entra alterado, e diz-se o quê) ·
`MERGE` (funde-se com artigo existente) · `REJECT` (não entra, e diz-se porquê).

**Destinos:** `CONSTITUTION` (Partes I e V — muda raramente) ·
`REGISTRY` (Registo Vivo — muda normalmente) · `OPEN` (fica como pergunta).

---

## §1 · OS 19 PRINCÍPIOS DE PRODUTO

| # | princípio | veredito | destino | motivo |
|---|---|---|---|---|
| 1 | **DECISION FIRST** | `MERGE` | CONSTITUTION §8 | Já é a pergunta 1 do Tool Admission Gate e o critério `HAS_OWN_DECISION_QUESTION` de §10. Não precisa de artigo novo — precisa de ser aplicado às 7 superfícies `UNKNOWN` |
| 2 | **WHY NOW BEFORE DETAIL** | `ACCEPT` | CONSTITUTION §36.1 | Entra como a camada de 3 segundos. E ganha aqui uma prova que o benchmark não tinha: `WHY_NOW` **já é campo do motor**, com dono declarado (Linha A) |
| 3 | **TIME IS FIRST-CLASS** | `ACCEPT` | CONSTITUTION §34 | É a mudança estrutural desta versão. Doze campos temporais, com dono por campo |
| 4 | **LOCATION IS FIRST-CLASS WHEN IT CHANGES ACTION** | `REFINE` | CONSTITUTION §40.1 | Aceite, mas o «when it changes action» é fraco demais para este repositório. A regra daqui é mais dura e já existe: `SOURCE_LOCATION ≠ FACT_LOCATION`, **sempre**, e a ausência é `UNKNOWN`. Medido: `luogo del fatto` em Vite × Peronospora dá `NÃO ESTABELECIDO` em 45 de 66 |
| 5 | **ACTION VISIBLE** | `ACCEPT` | CONSTITUTION §36 `C-CARD-01`, §41 | Uma ação primária por card |
| 6 | **ONE TRUTH, MANY ROLE PROJECTIONS** | `MERGE` | CONSTITUTION §40, L-23 | Confirma e **estende** `L-16 · USER ROLE ≠ TOOL` de V0.1. V0.1 impedia a ferramenta por departamento; não impedia o **brief** por departamento, porque não tinha o objecto brief. Ver o contraexemplo em §33 L-23 |
| 7 | **EVIDENCE ONE CLICK AWAY** | `REFINE` | CONSTITUTION §37, L-21 | Aceite **com uma trava que o benchmark não tem**: a prova dobra-se, **a lacuna não**. `CONTRATO-DE-DESIGN §3` proíbe colapsar `NÃO SEI` por omissão, e essa proibição vence a *progressive disclosure* |
| 8 | **UNKNOWN AND CONTRADICTION VISIBLE** | `MERGE` | CONSTITUTION §2 L-17, §5 | Já é lei em V0.1 e no modelo (`AM.ABSENCE_RULE`). O que o benchmark acrescenta é a **contradição** como estado próprio, e isso entra em `C-03 CONFLICT_STATE` |
| 9 | **NO MAGIC SCORE** | `REFINE` | CONSTITUTION §33 L-19 | Aceite e **endurecido**. Proibir o número na tela não chega: um ranking ordenado por um campo interno único e não exposto é o mesmo defeito sem o número. A lei tem de ser sobre a **ordem** |
| 10 | **NO FALSE CERTAINTY / FAKE PREDICTION** | `MERGE` | CONSTITUTION §36 `C-CARD-04`, §43 AP-20 | Já é o `RADAR-DO-FUTURO-CONTRACT-V1` («nenhum estado deste contrato afirma que algo VAI acontecer», `PALAVRAS_PROIBIDAS`). E já é o resultado do *backtest*: 1 safra no melhor caso, zero em dois de três |
| 11 | **STATE TRANSITIONS, NOT CARD VOLUME, DRIVE ALERTS** | `ACCEPT` | CONSTITUTION §39, L-22 | Com a trava herdada: hoje a porta `BASELINE` não abre em nenhuma família de conversa pública, logo o sistema **não pode emitir `ALERT`** |
| 12 | **EXTERNAL SIGNAL ≠ FIELD FACT** | `MERGE` | CONSTITUTION §36 `C-CARD-07` | É `FIELD VOICE ≠ FIELD INCIDENCE`. Já medido e declarado: `TRANSCRIPT_USED_AS_EVIDENCE = false` em 184/184 |
| 13 | **LABEL TRUTH GATES RESPONSE** | `ACCEPT` | CONSTITUTION §35, §44.1 | Já implementado com selo: `FORBIDDEN_CLAIMS` no payload + portão `G-01` fechado. V0.2 eleva-o a artigo |
| 14 | **WINDOW ≠ DATE; PHENOLOGY ≠ CALENDAR** | `ACCEPT` | CONSTITUTION §34, §43 AP-22 | E ganha um número: `WINDOW_OPEN_NOW = UNKNOWN` em **41 de 43** |
| 15 | **PRODUCTS ARE RESPONSES, NOT CATALOG ITEMS** | `ACCEPT` | REGISTRY | É `OWNER_INTENT` + `BENCHMARK_EVIDENCE` sobre **uma superfície**. Não é uma lei de fronteira: é uma decisão de produto sobre o Portfolio, e vive no Registo |
| 16 | **TOOLS SHARE OBJECTS, NOT COPIED DATA** | `ACCEPT` | CONSTITUTION §44 `L-GRAPH-01` | Confirma `D-021` («só APONTA … marca é texto num evento, não tabela») |
| 17 | **MOBILE IS DELIVERY, NOT MINI-DESKTOP** | `ACCEPT` | CONSTITUTION §33 L-24, §40.4 | |
| 18 | **MEASURE DECISION CHANGE, NOT ENGAGEMENT** | `REFINE` | CONSTITUTION §42 | Aceite com **três** níveis em vez de dois: `USAGE SIGNAL` · `DECISION SIGNAL` · `BUSINESS OUTCOME`. O terceiro é hoje `UNKNOWN` e tem de ser publicado como `UNKNOWN`, não estimado |
| 19 | **THE HUMAN REMAINS THE DECISION OWNER** | `ACCEPT` | CONSTITUTION §41 | É a única forma compatível com `EXTERNAL-ONLY`, e com «WHAT ONLY ADAMA CAN DECIDE», que já é campo obrigatório de MT2 |

```
ACCEPT   10        REFINE   4        MERGE   5        REJECT   0
```

### Por que zero `REJECT` nos princípios — e por que isso não é complacência

Os 19 princípios são **de nível cognitivo**, não de produto. Nenhum propõe uma tela, um
número ou uma promessa. **A rejeição concentra-se onde o benchmark desce ao concreto** —
§2 e §3 abaixo têm quatro `REJECT` e onze `REFINE`.

E cinco dos 19 já eram lei aqui antes do benchmark existir. **Isso é o resultado mais
importante desta adjudicação:** a convergência independente entre um repositório que
aprendeu por cicatriz e 16 produtos que aprenderam por mercado é evidência mais forte do
que qualquer um dos dois isolado.

---

## §2 · OS 16 PULOS DO GATO

| # | pulo | veredito | destino | motivo |
|---|---|---|---|---|
| 1 | Home como **Decision Inbox**, não dashboard | `ACCEPT` | CONSTITUTION §38 | Como **hipótese forte** (`OWNER_INTENT` + `BENCHMARK_EVIDENCE`), com `H-06` a endurecer a trava: a Home não calcula prioridade |
| 2 | Opportunity por **time-to-act**, não score | `ACCEPT` | CONSTITUTION §34 | E com o achado que o benchmark não podia ter: **a partição por estado de ação já existe no motor** (`ACT_NOW 2 · VALIDATE_NOW 4 · FUTURE_PREPARATION 7 · WATCH 21 · TO_VALIDATE 9`) e **não é a que o menu conta** |
| 3 | **Janela comercial abre antes da agronómica** | `ACCEPT` | CONSTITUTION §33 L-18 | Com `COUNTEREXAMPLE` escrito. É a emenda mais substantiva de V0.2 |
| 4 | One Intelligence Product → N Delivery Projections | `MERGE` | CONSTITUTION §40 | Confirma e estende `L-16` |
| 5 | O grafo é **M:N**; a cadeia linear é ilusão | `REFINE` | CONSTITUTION §44 | Aceite **para o consumo**, recusado para a origem. A cadeia `SOURCE → EVIDENCE → … → PORTAL` continua correta e é o princípio fundador do README: *«Nunca o contrário»*. As duas coexistem: **linear na origem, M:N no consumo.** Dizer «a cadeia linear é uma ilusão» sem esta distinção revogaria a lei fundadora do repositório |
| 6 | Future/Science/Field precisam de **promoção epistémica explícita** | `ACCEPT` | CONSTITUTION §44 `L-GRAPH-03` | Já existe uma implementação exemplar: a `REGUA_DE_MATURIDADE` 0–5 do `RADAR-DO-FUTURO-CONTRACT-V1`, com «cada transição exige evidência NOVA» e rebaixamento permitido |
| 7 | Portfolio = **memória de resposta** | `ACCEPT` | REGISTRY | `OWNER_INTENT` + `BENCHMARK_EVIDENCE`. Reclassificação de superfície, não lei |
| 8 | Label é mais importante como **fundação** do que como menu | `REFINE` | CONSTITUTION §44.1 + REGISTRY | Aceite como **camada de verdade**. **Refinado** num ponto: «do que como menu» sugere demoção, e a medição não a sustenta — Label é a **única** superfície do portal com Product Contract completo, selo e claim proibido. Ver §4 |
| 9 | Evidence **claim-linked e progressiva** | `ACCEPT` | CONSTITUTION §37 | Com a trava da lacuna que não se dobra |
| 10 | Mobile/Share Brief é produto; **PDF é derivado** | `ACCEPT` | CONSTITUTION §40.4 | |
| 11 | Alerta por **transição de decisão** | `ACCEPT` | CONSTITUTION §39 | |
| 12 | Field Sales pode fechar o *loop* sem virar motor de verdade | `ACCEPT` | REGISTRY | `RTV FEEDBACK ≠ FIELD INCIDENCE`. Continua `EXPERIMENT`/`DEMO` |
| 13 | Archive e Source Register podem deixar de ser «ferramentas» | `MERGE` | CONSTITUTION §10 | É exatamente a §10 de V0.1, que criou `INVESTIGATION_VIEW` e `EVIDENCE_EXPLORER` — a segunda **por causa** do Source Register. Convergência independente |
| 14 | Opportunity é uma **interseção**, não um tipo de conteúdo | `ACCEPT` | CONSTITUTION §35 | Já é lei executável (`CADEIA_EXIGIDA`, 8 elos, `NAO_ACEITE`). V0.2 eleva-a a artigo |
| 15 | A família visual **não pode apagar a epistemologia** | `ACCEPT` | CONSTITUTION §36.2 | |
| 16 | Market Pulse **só é pulse se existe decisão afetada** | `ACCEPT` | CONSTITUTION §36 `C-CARD-06` | Com uma consequência que o benchmark não tira: se a porta `SO WHAT` fechar para a maioria dos 157, a superfície não é «má» — é `CONTEXT_VIEW`, que é o que V0.1 já recomendava por outro caminho |

```
ACCEPT   12        REFINE   2        MERGE   2        REJECT   0
```

---

## §3 · AS RECOMENDAÇÕES POR SUPERFÍCIE

Comparadas com a recomendação de V0.1, que veio de medição do código.
**As duas pesquisas não se coordenaram.** Onde convergem, a confiança sobe; onde
divergem, a divergência fica escrita.

| superfície | benchmark | V0.1 (medição) | veredito V0.2 | destino |
|---|---|---|---|---|
| Opportunity Radar | `IMPROVE` — produto de decisão principal | `CANONICAL_TOOL` (conf. A) | **`ACCEPT` · convergem** | REGISTRY |
| Portfolio | `RETHINK` → memória de resposta | `UNKNOWN` — duas hipóteses, precisa de medição | **`REFINE`** — a hipótese (a) do benchmark é adotada como `OWNER_INTENT`; a exigência de medição de V0.1 **mantém-se**. Intenção declarada não substitui `OBSERVED_USAGE` | REGISTRY |
| Future Radar | `IMPROVE` — aviso estratégico | `EXPLORATORY_TOOL` (conf. A) | **`ACCEPT` · convergem** | REGISTRY |
| Label Intelligence | `SUPPORTING LAYER + REFERENCE` | `CANONICAL_TOOL + DELIVERY_PROJECTION` (conf. A) | **`REFINE` — a única divergência real.** Ver §4 | REGISTRY |
| Crop Windows | `FOUNDATIONAL LAYER + SURFACE` | `CONTEXT_VIEW` / componente temporal (conf. M) | **`REFINE`** — o benchmark tem razão no **papel** (relógio partilhado, e §34 precisa dele). V0.1 tem razão no **estado**: `PROVED 0`, `SOURCE_IDS` vazio 29/29, gerador ausente de 979 commits. Papel: `FOUNDATIONAL`. Estado: `DEGRADED`. **As duas coisas ao mesmo tempo** | REGISTRY + CONSTITUTION §34 |
| Market Pulse | `RETHINK` — só mudança que afeta decisão | `CONTEXT_VIEW` (conf. M-A) | **`ACCEPT`** — chegam ao mesmo por caminhos diferentes: a porta `SO WHAT` é o mecanismo que V0.1 não tinha | REGISTRY |
| Field Voices | `RETHINK` → *newswire*/sensor curado | `UNKNOWN` — 3 hipóteses, `CANDIDATE` reaberto | **`REFINE`** — a direção é adotada como `OWNER_INTENT`; **os três bloqueadores medidos por V0.1 continuam a valer**: baseline, denominador, GDPR. Nenhum é resolvido por formato de card | REGISTRY |
| Competitor Watch | `KEEP + IMPROVE`, sem score universal | camada transversal + `INVESTIGATION_VIEW` (conf. M-A) | **`ACCEPT` · convergem** — e o `577` no menu continua a violar o contrato | REGISTRY |
| Scientific Intelligence | `IMPROVE` — *science calls*, papers como evidência | `CANDIDATE` reaberto (conf. M) | **`ACCEPT` · convergem** — o benchmark dá a forma; V0.1 dá os bloqueadores (`CAP-017` não cobre a Itália, 39/88 `OFF_CASE`, GDPR P-008) | REGISTRY |
| Archive | `RECLASSIFY` — evidência/história/investigação | `INVESTIGATION_VIEW` ou `ADMIN` | **`ACCEPT` · convergem** — e a pergunta que separa as duas continua a mesma: **quem o abre** | REGISTRY |
| Source Register | `SUPPORTING LAYER / GOVERNANCE` | `EVIDENCE_EXPLORER` (conf. A) | **`REFINE`** — o benchmark diz «para analistas/admin, não ferramenta comum de utilizador». **A medição diz o contrário**: o `DESIGN-DATA-CONTRACT-V1` dá-lhe nível 2 com «inclui as fontes BLOQUEADAS, com motivo», que é conteúdo de produto. Fica `EVIDENCE_EXPLORER`, e `C-02` continua aberto | REGISTRY |
| Field Sales Channel | `EXPERIMENT / DELIVERY + FEEDBACK LOOP` | `INTEGRATION` · `EXPERIMENT` (conf. A) | **`ACCEPT` · convergem** — e falta-lhe a data de revisão `LC-04` | REGISTRY |

```
CONVERGEM ................. 7 de 12
DIVERGEM E FORAM REFINADAS  5 de 12
DIVERGÊNCIA REAL DE PAPEL .. 1 de 12   (Label Intelligence — §4)
```

> **Sete convergências entre duas pesquisas que não se falaram** — uma que mediu o código
> e outra que estudou 16 produtos — **é o resultado mais forte deste ficheiro.**

---

## §4 · A ÚNICA DIVERGÊNCIA REAL — Label Intelligence

| | posição | fundamento |
|---|---|---|
| benchmark | `SUPPORTING LAYER + REFERENCE SURFACE` — *«maior valor arquitetural é bloquear/autorizar afirmações; Label é mais importante como fundação do que como menu»* | 16 sistemas: camadas de verdade não são ferramentas de utilizador |
| V0.1 | `CANONICAL_TOOL + DELIVERY_PROJECTION`, em simultâneo, confiança **A** | é a **única** superfície do portal com Product Contract completo, `CONTENT_SHA256`, 22 regras versionadas e `FORBIDDEN_CLAIMS` escritos no payload |

### O veredito: `REFINE` — e as duas estão certas sobre coisas diferentes

**A confusão é a mesma que V0.1 já tinha nomeado como o pulo do gato mais caro:**

> **`PG-08` · `IS_INPUT_TO_ANOTHER_TOOL` NÃO É UM CRITÉRIO DE CLASSIFICAÇÃO.
> O critério é `HAS_OWN_DECISION_QUESTION`.**

O benchmark classifica Label como camada de suporte **porque ela alimenta Portfolio e
Opportunity**. Esse é exatamente o critério que a arquitetura antiga usou para empurrar
ciência, mercado e fontes «para baixo, não no menu» — e que a medição de V0.1 mostrou ser
o critério errado.

**Label Intelligence é as duas coisas ao mesmo tempo, e isso é precisamente o que a
cardinalidade M:N torna possível:**

```
COMO TRUTH LAYER   é dona da pergunta «o que é oficialmente permitido?» (§44.1)
                   e a sua resposta GATEIA Portfolio, Opportunity e briefs (princípio 13)

COMO TOOL          tem decision question própria — «o que o rótulo autoriza, como está
                   estruturado e o que mudou» — utilizador próprio (REGULATORY),
                   evidência própria (PDF → fios geométricos → citação verificada)
                   e claim proibido próprio, escrito no payload
```

```
VEREDITO   TRUTH LAYER  +  CANONICAL_TOOL  +  DELIVERY_PROJECTION
           As três em simultâneo. Confiança A.
           Onde a superfície vive no menu é DECISÃO DE PRODUTO, não de arquitetura.
```

**A evolução prioritária é a mesma nas duas pesquisas, e nenhuma a discute:**
`WHAT CHANGED SINCE LAST LABEL` + que produtos, oportunidades e briefs são impactados —
com a trava de §34.2: **o casco não calcula o impacto se ele exigir juízo.**

---

## §5 · O QUE NÃO ENTRA

Quatro `REJECT`, e o motivo de cada um.

### R-01 · `REJECT` · *«a cadeia linear é uma ilusão»*, na forma absoluta

**Rejeitado como formulado; aceite como distinção.** A cadeia
`SOURCE → EVIDENCE → DATA → CROSSING → CAPABILITY → TOOL → PORTAL` é o princípio
fundador deste repositório, com a frase **«Nunca o contrário»** na primeira página do
README, e é ela que impede `DATASET → MENU`. Ela descreve a **origem**.
O grafo M:N descreve o **consumo**. **Linear na origem, M:N no consumo** (§44).

Aceitar a formulação absoluta revogaria `L-01` sem contraexemplo — o que §20 proíbe.

### R-02 · `REJECT` · `Brief Hub` como ferramenta

O próprio benchmark já o rejeita («deve ser delivery layer, não nova verdade»), e V0.2
confirma-o: um *hub* de briefs seria uma superfície cuja *decision question* é o formato,
não a decisão. Falha a pergunta 1 do Gate. **Briefs são `DELIVERY_PROJECTION` (§40).**

### R-03 · `REJECT` · `Evidence Portal` como ferramenta nova

Archive e Source Register já cobrem investigação e governança (§10 de V0.1). Criar uma
terceira seria `AP-01 · DATASET BECOMES MENU` com nome nobre — e o repositório já tem
**quatro** acervos, três com a palavra «arquivo» e um `searchIndex` de 1655 entradas sem
menu (`AD-14`).

### R-04 · `REJECT` · `Score Center` e portais por departamento

Contrariam `L-19` e `L-16` diretamente. Nem chegam ao Gate.

### E um que **não é rejeitado, e também não é admitido**

`Validation Queue / Investigation Workspace`:

```
ESTADO           WORKFLOW_CANDIDATE
NÃO É            CANONICAL_TOOL · nem 13ª ferramenta
GATE             NÃO PASSOU — e a pergunta que falha é a 2 e a 13, não a 1
UTILIZADORES     Market Development · Technical · Regulatory
BLOQUEADOR       U-20 — ninguém mediu como a ADAMA valida isto hoje, fora do SINTONIA
```

**A pergunta que ela responde é boa e é real** — como validar sinais, `UNKNOWN`,
contradições e hipóteses **antes** de os promover. O repositório tem a matéria-prima
medida: `VALIDATION_REQUIRED = 37 de 43`, `TO_VALIDATE = 9`, `WATCH = 21`, e a régua de
promoção do `RADAR-DO-FUTURO-CONTRACT-V1`.

**O que falta não é ideia: é o *workflow* real da ADAMA.** Construir a fila antes de saber
como eles já validam seria desenhar o processo em vez de o servir.

E `Decision Inbox` **não é uma 13ª ferramenta**: é a Home (§38). As duas pesquisas
concordam nisto sem se terem falado.

---

## §6 · PLACAR DA ADJUDICAÇÃO

```
PRINCÍPIOS (19)      ACCEPT 10 · REFINE 4 · MERGE 5 · REJECT 0
PULOS DO GATO (16)   ACCEPT 12 · REFINE 2 · MERGE 2 · REJECT 0
SUPERFÍCIES (12)     convergem 7 · refinadas 5 · divergência real de papel 1
CANDIDATAS (2)       Decision Inbox → é a HOME  ·  Validation Queue → WORKFLOW_CANDIDATE
REJEITADAS (4)       R-01 · R-02 · R-03 · R-04

ENTRARAM NA CONSTITUIÇÃO ......... 8 leis novas (L-18…L-25)
                                   + 15 artigos (§32…§46)
ENTRARAM SÓ NO REGISTO VIVO ...... 12 reclassificações de superfície
                                   + 1 princípio (nº 15, produtos são respostas)
FICARAM EM ABERTO ................ 10 UNKNOWN novos (U-15…U-24)
LINHAS DE CONSTITUIÇÃO REMOVIDAS . 0
```

### As três frases desta adjudicação

**Primeira.** Cinco dos 19 princípios já eram lei aqui antes de o benchmark existir, e
sete das 12 recomendações por superfície coincidem com o que a medição do código tinha
concluído sozinha. **Duas pesquisas que não se falaram convergiram** — uma por cicatriz,
outra por mercado. É a evidência mais forte que qualquer uma delas produziu.

**Segunda.** As quatro rejeições e as onze refinações estão todas no mesmo sítio: **onde o
benchmark desce ao concreto e a medição local sabe mais.** O benchmark não conhecia
`WINDOW_OPEN_NOW = UNKNOWN` em 41 de 43, nem que a partição temporal já existia no motor,
nem que Label tinha selo criptográfico. **Evidência externa é forte sobre forma e fraca
sobre estado.**

**Terceira.** A única divergência real — Label Intelligence — resolveu-se por uma lei que
V0.1 já tinha escrito: **ser input de outra ferramenta não rebaixa ninguém.** Foi preciso
o benchmark tropeçar nela para se ver que `PG-08` não era uma observação sobre o passado:
é um erro que se repete sempre que alguém classifica por dependência em vez de por
pergunta.
