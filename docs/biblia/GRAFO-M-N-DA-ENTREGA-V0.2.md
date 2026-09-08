# GRAFO M:N DA ENTREGA — SINTONIA EAME

```
DOCUMENT_STATUS   DRAFT
DOCUMENT_TYPE     CORE CONSTITUTION §44 · detalhe das arestas
DATE              2026-09-08
IMPLEMENTATION    NONE
```

> **`L-GRAPH-01` · As ferramentas PARTILHAM OBJECTOS, não copiam dados.**
> Duas cópias do mesmo objecto são duas verdades — o defeito que `D-021` já recusou
> («só APONTA … marca é texto num evento, não tabela»).

---

## §1 · A DISTINÇÃO QUE SALVA A CADEIA LINEAR

O benchmark propõe que «a cadeia linear é uma ilusão». **Aceite para o consumo,
rejeitado para a origem** (`ADJUDICACAO §5 R-01`).

```
NA ORIGEM — linear, e é a lei fundadora do repositório
   SOURCE → EVIDENCE → DATA → CROSSING → CAPABILITY → TOOL → PORTAL
   «Nunca o contrário.»  É esta cadeia que impede DATASET → MENU.

NO CONSUMO — M:N
   um produto alimenta muitas superfícies;
   uma superfície consome muitos produtos;
   e nenhuma das duas coisas altera quem é dono do facto.
```

**As duas coexistem sem se contradizerem** porque respondem a perguntas diferentes:
a primeira pergunta *«de onde é que isto pode nascer?»*; a segunda, *«quem é que isto
serve?»*.

---

## §2 · OS OBJECTOS PARTILHADOS

```
CROP ↔ PROBLEM ↔ GEOGRAPHY ↔ WINDOW ↔ PRODUCT ↔ LABEL_USE ↔
ACTIVE_SUBSTANCE ↔ COMPETITOR ↔ CLAIM ↔ SOURCE ↔ HORIZON
```

**Nem todos existem hoje com dono único. Medido:**

| objecto | dono medido | estado |
|---|---|---|
| `CROP` | `AM.cropResolve`, dona única da tabela `CROP_BY_TOKEN` | **ÚNICO** — e foi decisão explícita: *«não se escreveu uma segunda tabela de sinónimos»* |
| `PRODUCT` | `AM.products` (173) · `productByKey` · `findProduct` | ÚNICO |
| `LABEL_USE` | `ITALY_LABEL_INTELLIGENCE` (166 · selado) | ÚNICO |
| `SOURCE` | `AM.sourceById` (194) | ÚNICO |
| `WINDOW` | `cropWindows` (29) | **ÚNICO E SEM PROVENIÊNCIA** — `SOURCE_IDS` vazio 29/29 |
| `PROBLEM` | `AM.issueResolve` | ÚNICO na resolução; **`issueIds` vazio em 577/577** no concorrente |
| `GEOGRAPHY` | `AM.regionResolve` | ÚNICO; `FACT_LOCATION` ausente em 45 de 66 no caso medido |
| `CLAIM` | **não existe como objecto** | `UNKNOWN` |
| `HORIZON` | `ITALY_CASA.RADAR_FUTURO` | parcial |
| `COMPETITOR` | `competitorCompanies` (11) | ÚNICO |
| `ACTIVE_SUBSTANCE` | `activeIngredients` (53) | ÚNICO |

> **`CLAIM` é o objecto em falta, e é o que a `§37 · Evidence Drawer` exige.**
> Sem um objecto `CLAIM`, «evidência ligada ao claim» não tem a que se ligar.
> É a dependência mais concreta que este ficheiro identifica.

---

## §3 · AS ARESTAS

Formato exigido por `L-GRAPH-02`. `AUTORIDADE` responde a *«quem manda quando os dois
discordam?»*. `PROMOVE?` responde a *«esta aresta pode fazer o alvo mudar de estado
epistemológico?»*.

---

### E-01 · `LABEL_AUTHORISED_USE` → `PORTFOLIO`

```
RELAÇÃO            GATES — autoriza ou bloqueia
AUTORIDADE         LABEL. Em conflito, o rótulo vence o catálogo.
PROMOVE?           NÃO promove. BLOQUEIA.
QUEM PROMOVE       n/a
EVIDÊNCIA EXIGIDA  registo + PDF com sha + linha de uso verificada (R-14/R-18)
UNKNOWN            NUNCA vira «não autorizado». Vira LABEL_CHECK_NEEDED.
ESTADO MEDIDO      já implementado como STRENGTH: VERIFIED_LABEL_MATCH →
                   RELATED_PORTFOLIO → LABEL_CHECK_NEEDED →
                   NO_CONFIRMED_MATCH_CURRENT_READING
ABERTO             166 rótulos × 173 produtos não reconciliados (C-08)
```

### E-02 · `LABEL_AUTHORISED_USE` → `OPPORTUNITY`

```
RELAÇÃO            GATES — é o elo «RELAÇÃO produto × alvo (rótulo ministerial)»
AUTORIDADE         LABEL
PROMOVE?           NÃO. É condição necessária, nunca suficiente.
EVIDÊNCIA EXIGIDA  o elo da CADEIA_EXIGIDA de 8
UNKNOWN            o caso não sobe. Fica em classe B (radar), não em A.
LEI                USO AUTORIZADO NÃO É OPORTUNIDADE COMERCIAL
                   — escrita no payload, com portão G-01 fechado
```

### E-03 · `CROP_WINDOW` → `OPPORTUNITY`

```
RELAÇÃO            TIMES — dá o estado temporal
AUTORIDADE         CROP WINDOWS, como SHARED AGRONOMIC CLOCK (§34)
PROMOVE?           SIM — pode mover um caso entre estados de ação no tempo,
                   e é a única aresta do grafo que o pode fazer sozinha
QUEM PROMOVE       a régua temporal, que vive na INTELLIGENCE
EVIDÊNCIA EXIGIDA  janela com proveniência
UNKNOWN            WINDOW_OPEN_NOW = UNKNOWN → o caso NÃO entra em AGIR AGORA.
                   Um estado de urgência sem relógio é urgência inventada.
ESTADO MEDIDO      ⚠️ WINDOW_OPEN_NOW UNKNOWN em 41/43 · WINDOW_DEFINED NO em 27/43
                   SOURCE_IDS vazio em 29/29 · CROP_WINDOWS_TRUSTED = NÃO
BLOQUEADOR         esta é a aresta mais importante do grafo e a menos sustentada.
                   §34 depende dela inteiro.
```

### E-04 · `CROP_WINDOW` → `PORTFOLIO`

```
RELAÇÃO            CONTEXTUALISES — quando uma resposta é aplicável
AUTORIDADE         CROP WINDOWS para o tempo · LABEL para o que é permitido
PROMOVE?           NÃO
UNKNOWN            janela desconhecida ≠ produto inaplicável
LEI                WINDOW_OPEN ≠ CURRENT_NEED  (CONTRATO-DE-DESIGN §2.1)
                   CALENDAR ≠ OBSERVED PHENOLOGY  (AP-22)
```

### E-05 · `PRODUCT_PORTFOLIO` → `OPPORTUNITY`

```
RELAÇÃO            ANSWERS — fornece a resposta ADAMA defensável
AUTORIDADE         PORTFOLIO, montado sobre LABEL
PROMOVE?           SIM — sem resposta ADAMA ligável, o caso é classe C (sinal bruto)
QUEM PROMOVE       ADAMA-RELEVANCE-LAW-V1, que exige «pelo menos UM produto a fechar
                   a cadeia inteira»
EVIDÊNCIA EXIGIDA  produto + relação com cultura (catálogo) + relação com alvo (rótulo)
UNKNOWN            NO_CONFIRMED_MATCH_CURRENT_READING — e a ficha di-lo
LEI                PRODUCT ON CROP ≠ COMMERCIAL SOLUTION  (AP-21)
                   E a lei que a evita ser vazia: BASTA_UM_PRODUTO — «os outros
                   produtos ligados não são a prova e não a estragam; o cartão
                   nomeia qual deles a carrega»
```

### E-06 · `SCIENCE_CORPUS` → `FUTURE_THEME`

```
RELAÇÃO            SUPPORTS — sustenta uma camada de sinal
AUTORIDADE         SCIENCE para o claim · FUTURE para a maturidade do tema
PROMOVE?           SIM, mas SÓ POR TRANSIÇÃO GOVERNADA
QUEM PROMOVE       a RÉGUA DE MATURIDADE 0–5 do RADAR-DO-FUTURO-CONTRACT-V1
EVIDÊNCIA EXIGIDA  «0→1: uma publicação com DOI e vínculo ao país FORA da afiliação
                   do autor»  ·  «1→2: uma segunda camada de tipo diferente»
                   e «cada transição exige evidência NOVA — nenhum tema sobe de estado
                   por releitura do que já está escrito»
UNKNOWN            AUSENTE_MEDIDO ≠ NAO_TESTADO. O campo de sinal aceita três valores.
RISCO MEDIDO       ⚠️ 39/88 papers são OFF_CASE · 87/88 batem QUERY_*, 37/88 PROVED_*
                   AP-17 · o termo da busca não é o achado
```

### E-07 · `FUTURE_THEME` → `OPPORTUNITY`

```
RELAÇÃO            PROMOTES — a única porta entre os dois
AUTORIDADE         FUTURE até à porta · OPPORTUNITY depois dela
PROMOVE?           SIM
QUEM PROMOVE       CURRENT_FIELD_CONFIRMATION — «é a única», textual no contrato
EVIDÊNCIA EXIGIDA  confirmação de campo corrente, datada por observação
UNKNOWN            o tema fica no Radar do Futuro. E o contrato acrescenta:
                   «um tema pode ficar anos no Radar do Futuro sem nunca virar caso,
                   e isso NÃO É FALHA do tema nem do motor»
NOTA               é a aresta mais bem definida do grafo inteiro, e a única com uma
                   porta nomeada, unívoca e escrita antes de existir superfície
```

### E-08 · `FIELD_VOICE_CORPUS` → `FUTURE` · `OPPORTUNITY` · `SCIENCE`

```
RELAÇÃO            OPENS_INVESTIGATION — nunca CONFIRMS
AUTORIDADE         NENHUMA sobre o facto agronómico
PROMOVE?           NÃO. Pode abrir investigação; não pode promover.
QUEM PROMOVE       ninguém, por esta aresta
EVIDÊNCIA EXIGIDA  para abrir investigação: voz + canal + data + local da fonte
                   para confirmar incidência: outra fonte, de outra natureza
UNKNOWN            é o estado por omissão
LEI                FIELD VOICE ≠ FIELD INCIDENCE  ·  ATTENTION ≠ AGRONOMIC FACT
                   E a escada de 5 degraus, nenhum implicando o seguinte
ESTADO MEDIDO      TRANSCRIPT_USED_AS_EVIDENCE = false em 184/184
                   0 das 43 oportunidades cita voz, canal ou vídeo como evidência
BLOQUEADORES       baseline · denominador (79 de quantos?) · GDPR P-008/P-009
```

### E-09 · `COMPETITOR_OBSERVATION` → `OPPORTUNITY` · `PORTFOLIO` · `MARKET`

```
RELAÇÃO            CONTEXTUALISES — camada transversal
AUTORIDADE         COMPETITOR sobre a observação · NENHUMA sobre a conclusão
PROMOVE?           NÃO
EVIDÊNCIA EXIGIDA  registo (para resposta registada) · anúncio com data de verificação
                   (para ativação observada) — e as duas colunas NUNCA se fundem
UNKNOWN            NOT_KNOWN é o quinto estado e está sempre disponível.
                   «Dizer que um concorrente está silencioso» é proibido;
                   o correto é NO PUBLIC ACTIVITY FOUND IN SEARCHED SOURCES
LEI                não somar registo + anúncio + comunicação + atividade técnica
ESTADO MEDIDO      ⚠️ issueIds vazio em 577/577 → liga-se SÓ por cultura, e di-lo.
                   Ligar por texto livre seria AP-27 · CROSS-LINK-BY-KEYWORD
                   ⚠️ 27 selos ATTIVO com ACTIVE_ADS_PROVED = 0
```

### E-10 · `MARKET_PRICE_SERIES` → `OPPORTUNITY` · `FUTURE`

```
RELAÇÃO            CONTEXTUALISES
AUTORIDADE         MARKET sobre o preço · NENHUMA sobre a procura
PROMOVE?           NÃO
PORTA              SO WHAT · WHO CARES · WHICH DECISION MAY CHANGE
                   Sem as três: SUPPORTING CONTEXT, não item de pulse (C-CARD-06)
UNKNOWN            classe temporal obrigatória: CURRENT · OUTLOOK · HISTORICAL
CICATRIZ           azeite de Salerno a €630 como preço corrente; a cotação era de 2015
```

### E-11 · `SOURCE_PROVENANCE` → **todas**

```
RELAÇÃO            PROVES — é o chão de toda a cadeia
AUTORIDADE         SOURCE REGISTER sobre a proveniência
PROMOVE?           NÃO. Mas pode DESPROMOVER: SOURCE_FAILED derruba o que dela depende.
QUEM DESPROMOVE    version_state — 5 estados, e só NEW_VERSION_CHANGED autoriza evento
UNKNOWN            BASELINE_ESTABLISHED → NOT ENOUGH VERSIONS, nunca NO_CHANGE
                   SOURCE_FAILED → jamais apresentado como «nada mudou»
ESTADO MEDIDO      ⚠️ sourceGroup preenchido em 31 de 194 — missPct 84%
ABERTO             não foi medido se cada facto das outras superfícies consegue
                   saltar para aqui. É o que o EvidenceLink de §37 exige.
```

### E-12 · `*` → `HOME`

```
RELAÇÃO            QUEUES — enfileira o que já é elegível
AUTORIDADE         NENHUMA PRÓPRIA. A Home não calcula prioridade (H-06).
PROMOVE?           NUNCA
EVIDÊNCIA EXIGIDA  a que o produto de origem já carrega
UNKNOWN            um item sem estado de ação no tempo NÃO entra na fila.
                   E não entrar não é desaparecer: continua na sua superfície.
LEI                HOME PROJECTION ≠ INTELLIGENCE ENGINE
```

### E-13 · `*` → `ASK SINTONIA`

```
RELAÇÃO            ANSWERS_OVER — responde sobre, nunca acima
AUTORIDADE         a MENOR dos produtos que cita (§5.3 L-CONF)
PROMOVE?           NUNCA
EVIDÊNCIA EXIGIDA  toda resposta devolve FACTS · CONNECTIONS · UNKNOWN ·
                   WHY_IT_MAY_MATTER · EVIDENCE
UNKNOWN            «NÃO SEI», com o motivo. Recusa correta é resultado positivo.
CONFLITO           dois produtos discordam → mostra os dois e diz que discordam.
                   Escolher em silêncio é criar autoridade nova.
REGRESSÃO          as 10 recusas do benchmark são teste. Responder B03, B06, B10,
                   B13, B19, B23 ou B25 sem fonte nova é REGREDIR, mesmo parecendo
                   mais capaz.
```

### E-14 · `*` → `BRIEF` → `USER ROLE`

```
RELAÇÃO            PROJECTS
AUTORIDADE         a do produto de origem, INTEGRALMENTE herdada
PROMOVE?           NUNCA. Um brief não cria facto (AP-26 · BRIEF-AS-NEW-TRUTH).
IMUTÁVEL           §40.1 — factos, evidência, fonte, tempos, locais, limitações,
                   estado de confiança, UNKNOWN, contradição, verdade de rótulo,
                   ID + versão + AS_OF
VARIÁVEL           §40.2 — língua, título, ordem, ênfase, detalhe, contexto,
                   próxima ação, comprimento
UNKNOWN            viaja em todos os briefs, com o mesmo peso. Um brief de Sales sem
                   a limitação técnica é o contraexemplo de L-23.
```

### E-15 · `ACTION RECORD` → `INTELLIGENCE`

```
RELAÇÃO            FEEDS_BACK
AUTORIDADE         NENHUMA. Volta como FACTO NOVO, com fonte «utilizador X, data Y».
PROMOVE?           NÃO automaticamente.
LEI                RTV FEEDBACK ≠ FIELD INCIDENCE
                   T-03 — feedback nunca volta como juízo
                   T-04 — a telemetria não reordena a Home sem lei declarada
ESTADO MEDIDO      TELEMETRY_EXISTS = NO. Esta aresta não existe.
```

---

## §4 · MATRIZ DE PROMOÇÃO — quem pode fazer o quê mudar de estado

| aresta | promove? | quem promove | porta nomeada? |
|---|---|---|---|
| E-01 Label → Portfolio | **bloqueia** | — | sim (`STRENGTH`) |
| E-02 Label → Opportunity | não (necessária, não suficiente) | — | sim (elo da cadeia) |
| E-03 Crop Window → Opportunity | **SIM** | régua temporal | **NÃO — em falta** |
| E-04 Crop Window → Portfolio | não | — | — |
| E-05 Portfolio → Opportunity | **SIM** | `ADAMA-RELEVANCE-LAW-V1` | sim |
| E-06 Science → Future | **SIM** | régua de maturidade 0–5 | sim |
| E-07 Future → Opportunity | **SIM** | `CURRENT_FIELD_CONFIRMATION` | **sim, e é a melhor do grafo** |
| E-08 Field Voices → * | não | — | — (abre investigação) |
| E-09 Competitor → * | não | — | — |
| E-10 Market → * | não | — | porta `SO WHAT` |
| E-11 Source → * | **despromove** | `version_state` | sim |
| E-12 * → Home | nunca | — | — |
| E-13 * → Ask | nunca | — | — |
| E-14 * → Brief | nunca | — | — |
| E-15 Action → Intelligence | não automaticamente | — | não existe |

```
ARESTAS QUE PROMOVEM ................ 4   (E-03 · E-05 · E-06 · E-07)
DESSAS, COM PORTA NOMEADA ........... 3
SEM PORTA NOMEADA ................... 1   E-03 · CROP WINDOW → OPPORTUNITY
```

> **E-03 é a lacuna estrutural do grafo.**
> É a única aresta que pode promover **e** não tem porta escrita — e é precisamente a
> que o modelo temporal de §34 exige. Sem ela, `AGIR AGORA` não tem quem o decida, e
> `WINDOW_OPEN_NOW` continua `UNKNOWN` em 41 de 43.

---

## §5 · ARESTAS QUE DEPENDEM DA BÍBLIA DA INTELIGÊNCIA

`DEPENDENCY_ON_INTELLIGENCE_BIBLE = OPEN` para tudo o que exija **autoridade semântica**
sobre um campo de juízo. A Bíblia da Entrega pode definir o **contrato de apresentação**
desses campos hoje; **não pode nomear quem os produz.**

| aresta | campo em disputa | por que a Entrega não pode decidir |
|---|---|---|
| **E-03** | `TIME_TO_ACT` · `TIME_TO_PREPARE` · `WINDOW_STATE` | são juízo agronómico e comercial, não formato |
| **E-05** | `ADAMA RESPONSE` · `WHAT TO DO` | são recomendação; exigem dono com autoridade técnica e regulatória |
| **E-06** | `EVIDENCE MATURITY` · `SCIENCE MATURITY` | a régua 0–5 existe para `FUTURE_THEME`; **não existe para ciência** |
| **E-07** | o que conta como `CURRENT_FIELD_CONFIRMATION` | está nomeada, não está operacionalizada |
| **E-09** | o que conta como evento «material» de concorrente | decide o alerta (§39) |
| **E-15** | quando é que feedback de campo passa a evidência | é a lei que impede `RTV FEEDBACK = FIELD INCIDENCE` |
| **todas** | o objecto `CLAIM` | sem ele, `§37` não tem a que se ligar |

> **Sete dependências abertas, e nenhuma é de desenho.**
> Esta é a lista que o próximo ponto de reconciliação
> `COLLECTION → INTELLIGENCE → DELIVERY` tem de fechar.

---

## §6 · O QUE ESTE GRAFO NÃO FEZ

Não implementou nenhuma aresta. Não alterou o modelo, o pacote, o portal nem o schema.
Não inventou um objecto `CLAIM` — **nomeou a sua ausência**. Não decidiu nenhuma das sete
dependências de §5: **elas pertencem à Bíblia da Inteligência, que ainda não existe como
ficheiro** (`U-12`).

**`NÃO MEDIDO ≠ NÃO EXISTE`. `UNKNOWN` continua `UNKNOWN`.**
