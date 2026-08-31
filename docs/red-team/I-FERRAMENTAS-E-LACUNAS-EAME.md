# I–Q · FERRAMENTAS, LACUNAS E CAPACIDADES LATENTES

**PASSAGEM 1 — FECHADA.** Este documento é análise **estrutural**: depende do casco e do
acervo já congelados, **não** das quatro coletas em curso.

**Data:** 2026-08-30 · `SNAPSHOT_FROZEN_AT = 2026-08-30` · casco SHA-256
`a31ea184…87c6a`

> **O que este documento NÃO faz:** não decide ferramenta nova, não desenha mangueira, não
> altera casco, não promove estado. Candidatos finais de ferramenta e o mapa de mangueiras
> ficam para a PASSAGEM 2, depois do refresh único.

---

# I · SUPERFÍCIES EXISTENTES — KEEP / IMPROVE / NEEDS_DATA / REVIEW

> **Taxonomia aplicada** (definida em `A-BASELINE-DO-CASCO-EAME.md`, seção 0.2):
> `NAVIGATION_ITEM` · `SURFACE` · `TOOL` · `CAPABILITY` · `VIEW` · `DATASET` · `QUESTION`
> são coisas diferentes. **A tabela abaixo classifica SUPERFÍCIES e ITENS DE NAVEGAÇÃO —
> não ferramentas.** Uma superfície pode conter várias capacidades; uma ferramenta pode
> viver em duas superfícies (MT1 está em `Análises` **e** em `Radar/Casos`); e uma
> capacidade pode não merecer superfície nenhuma.
>
> **Quantas ferramentas o casco realmente tem é decisão da PASSAGEM 2.** Não é 15, e não é
> 12.

Classificação por superfície. A pergunta que decide não é *"está bonita?"* — é
**"o acervo de hoje enche esta superfície, e ela responde melhor do que quando foi
desenhada?"**

| # | superfície / item de navegação | veredito | o que o acervo já enche hoje |
|---|---|---|---|
| 6 | **Acervo** | **READY_TO_FEED** | ES 147 documentos · IT 163 etichette oficiais · FR 122 documentos + **234 objetos RAW com SHA verificado** |
| 7 | **Fontes** | **READY_TO_FEED** | 37 SOURCE_IDs · 26 fichas · 16 GREEN · 4 YELLOW · 0 RED · 16 NÃO SEI |
| 3 | **Radar / Casos** (lista) | **READY_WITH_LIMITATIONS** | 6 casos reais (3 IT + 3 ES) + 1 pergunta de ativação FR — contra 8 slots |
| 4 | **Caso** (detalhe) | **READY_WITH_LIMITATIONS** | **4 das 7 camadas** enchem: Regulatório, Ciência, Portfólio local, Campo (ES e IT) |
| 12 | **Camada EAME** | **READY_WITH_LIMITATIONS** | a **matriz de comparabilidade** enche inteira, com estado medido por dimensão |
| 1 | **Visão Geral** | **READY_WITH_LIMITATIONS** | estado da fundação por país · estado da coleta (Data Clock + portões) · fila de 4 itens |
| 9 | **Relatórios** | **READY_WITH_LIMITATIONS** | snapshot e freeze têm lastro real: `DATA-CLOCK-manifest.json` com SHA-256 e `scripts/auditoria.py --congelar` |
| 2 | **Radar do Futuro** | **NEEDS_DATA** + **NEEDS_SEMANTIC_IMPROVEMENT** | falta a camada TEMA; e um rótulo contradiz a lei — abaixo |
| 5 | **Janelas da Cultura** | **NEEDS_DATA** | o relógio vivo da lavoura não existe em país nenhum. FR tem 376/414 linhas com BBCH — mas isso é `LABEL_USE_STAGE`, restrição de rótulo, **não** janela de aplicação (ver J7) |
| 15 | **Display layer / idioma** | **NEEDS_DATA** | o dicionário não existe; `DISPLAY-LAYER-V1.json` está no acervo, desligado |
| 8 | **Análises** | **NEEDS_PRODUCT_REVIEW** | é a tela mais rasa (5,4 KB) onde mora o valor — e **duplica** as classes de caso |
| 13 | **Ask Sintonia** | **NEEDS_PRODUCT_REVIEW** | **entrada sem saída** — há campo de busca e nenhuma tela de resposta |
| 14 | **Seletor de país** | **IMPROVE** | badges de IT e FR dizem `EM COLETA`; as branches dizem `COMPLETE` |
| 10 | **Sistema** (lib) | **KEEP_AS_IS** | pronta e correta — o dado dela é a marca |
| 11 | **Config** | **KEEP_AS_IS** | estrutura certa; só espera o dicionário |

## I.1 · As quatro que podem receber dado real primeiro

**Acervo e Fontes são as portas de entrada mais baratas do produto.** Não exigem
inteligência nova: exigem ligar o que já está medido. Juntas, elas realizam sozinhas metade
da promessa do Sintonia — *toda resposta leva de volta à evidência*.

**Radar/Casos e Caso** exigem uma decisão de escopo, não de dado: **os 6 casos reais estão
em duas branches diferentes e nenhuma foi mesclada.**

## I.2 · `SEMANTIC_UX_RISK` — o rótulo de recorrência

Dentro de `Radar do Futuro`, bloco *"Palavra dos pesquisadores"*:

```
linha 1   "Recorrência não é autoridade. Pessoas identificadas exigem tratamento GDPR..."
linha 3   [elemento]  Abrir ranking de recorrência
```

**O que foi medido, e o que não foi.** O elemento é um `<div>` **sem manipulador de clique,
sem destino e sem tela de chegada**; as três barras acima (DISEASE · WEED · PEST) estão
vazias — sem nome, sem contagem, sem ordem. **Não existe ranking implementado, portanto não
existe contradição provada.**

Ordenar por recorrência pode significar apenas **ordenar por frequência observada**, e isso
é legítimo. O risco se realiza **só se** a interface converter recorrência em
`AUTORIDADE` · `QUALIDADE` · `IMPORTÂNCIA` · `VERDADE` · `INFLUÊNCIA`.

**Veredito: `SEMANTIC_UX_RISK` — a reavaliar quando o destino existir.** Não é
`NEEDS_SEMANTIC_IMPROVEMENT` provado, porque não há comportamento a corrigir ainda.

Por que vale registrar mesmo assim: o repositório já pagou caro por esta fronteira. Sem
vocabulário controlado a lista de pesquisadores muda por completo (**2.627 contra 27
trabalhos**, medido), e um único ID conflacionado apareceu **em primeira posição** com 58
organizações contra mediana 2. **A lei permanece, e vale para quem construir o destino:**

```
RECURRENCE ≠ AUTHORITY        FOLLOWERS ≠ AUTHORITY        ENGAGEMENT ≠ INFLUENCE
```

## I.3 · A redundância a examinar

`Análises` oferece três *modelos de leitura* — Revisão regulatória, Prioridade geográfica,
Pergunta de ativação. `Radar / Casos` oferece cinco *classes de caso* — `REGULATORY
DEADLINE`, `GEOGRAPHIC PRIORITY`, `ACTIVATION QUESTION`, `INVESTIGATE`, `CHANGE DETECTED`.

**Os três primeiros são o mesmo objeto com dois nomes.** MT1, MT2 e MT3 aparecem duas vezes
no casco: uma como *lente de leitura*, outra como *tipo de item na fila*.

Isto **pode** ser deliberado e bom (a fila mostra instâncias; a análise mostra o método).
Também pode ser duplicação que fará o usuário procurar a mesma coisa em dois lugares.
**Esta rodada não decide.** É a pergunta nº 4 do red team.

---

# N · DATA GAPS — *não temos o dado*

| # | lacuna | estado medido | o que destravaria |
|---|---|---|---|
| N1 | **`APPLICATION_WINDOW` — janela agronômica real por cultura × região** | `NÃO CONECTADA` em ES, IT e FR. O que existe é `LABEL_USE_STAGE` (FR 376/414), que **é restrição, não janela** | fonte fenológica **datada e por região**. O rótulo entra como um dos lados; sozinho não fecha |
| N2 | **Campo francês** — Bulletins de Santé du Végétal | **`READ_FAILURE`, não ZERO**: índice oficial responde 200 e lista **17 rotas regionais**; todos os `draaf.*` dão timeout | **outro IP de saída** (runner) |
| N3 | **Catálogo ADAMA Itália** | `ROUTE_BLOCKED_WAF` — 403 uniforme, inclusive no `robots.txt` | Chrome **com janela** na máquina local — foi assim que ES e FR abriram |
| N4 | **Cultura × alvo · dose · janela italianas** | `CROP_ISSUE = 0`; a tabela do PDF não foi reconstruída. **9.746 pares cartesianos recusados** | parse da tabela do rótulo |
| N5 | **Meta Ads Library** (`EU-T9-002`) | **`NÃO TESTADO`** — nunca aberta. **Não** é `AUSENTE_MEDIDO` | testar a rota |
| N6 | **Comunicação de concorrente** | 1 rota provada de 5 majors; 4 devolvem 403/502/404 | rota alternativa; **403 não é ausência de comunicação** |
| N7 | **Agreste** (estatística agrícola FR) | `BLOCKED_ON_TESTED_ROUTES` | outro IP de saída |
| N8 | **Rendimento por região** | **não existe** na fonte — medido, não suposto | nenhuma rota conhecida |
| N9 | **Audiência dos creators** | `AUDIENCE_TYPE = NOT_KNOWN` em todos menos um | rota de audiência |
| N10 | **34 de 43 hubs de creators** | `PEOPLE_EXTRACTED = 0`; os 66 nomeados do AgroInfluye não extraídos | rota do runner |
| N11 | **Dados internos da ADAMA** | **permanente, por decisão do cliente** | nada. `ECONOMIC_VALUE` nunca será provado |

**N11 é diferente de todos os outros:** não é lacuna a fechar, é **fronteira do produto**.
Nenhuma saída pode afirmar `REVENUE`, `MARGIN`, `SALES` ou `ROI REALIZED`.

---

# O · INTELLIGENCE GAPS — *temos o dado, não sabemos produzir inteligência*

**Esta é a lista mais valiosa deste documento.** Cada item é dado pago, coletado e
preservado, que hoje não vira nada que mude decisão.

| # | dado que existe | o que ainda não sabemos fazer com ele |
|---|---|---|
| **O1** | **1.771 documentos científicos ES · 9.958 autores · 380 instituições** | **nenhum vira item de radar.** Sabemos quem publica; não sabemos dizer *"esta linha de pesquisa está virando problema de campo"* |
| **O2** | **991 comentários · 196 perguntas técnicas (19,8 %)** | não há taxonomia de **o que o campo não entende**. A pergunta está classificada como tipo, não por assunto |
| **O3** | **148.964 leituras RAIF · 23 safras · 10 culturas** | **só uma coorte, de uma doença, foi usada.** Nove culturas do RAIF nunca entraram em análise nenhuma |
| **O4** | **X-006 · substância normalizada, 82,1 % do uso** | a ponte cross-market mais forte do projeto **nunca foi executada** para `cereal × septória ES ↔ FR`, que é o par espelhado do piloto |
| **O5** | **13 pessoas com ORCID resolvido, em 6 recortes, 3 países** | **`IDENTITY_LINKAGE_BARRIER_REDUCED`** — a causa registrada do bloqueio era *"falta identificador declarado que atravesse camadas"*, e ele agora existe. **Isso não fecha o cruzamento** — ver O5.1 |
| **O6** | **7 canais `PROVED` + 12 `PLAUSIBLE`** de 44 candidatos | os 12 `PLAUSIBLE` não têm régua de promoção escrita |
| **O7** | **Coorte RAIF + densidade institucional (380 instituições com afiliação)** | o **confundidor de Córdoba** continua aberto. O dado para separá-lo **está no acervo** e nunca foi usado |
| **O8** | **Vereditos arbitrados do EARLY SIGNAL** | **não existem como artefato.** As strings `TECHNICAL_PERSON_AS_EXPERT_DIRECTORY`, `FIELD_VOICE_DENSITY`, `AUDIENCE_TECHNICAL_QUESTION` e as demais **não aparecem em nenhuma branch**. A medição existe; o veredito escrito, não |
| **O9** | **34 registros ES + 8 IT `vigente` com caducidade anterior ao snapshot** (31 ES na mesma data) | **`STATUS_DATE_CONFLICT_OBSERVED` · `INVESTIGATE_CANDIDATE`** — ver O9.1 |
| **O10** | **`MISSING_PROOFS` em 18 fichas de creator** | é o campo mais operacional já produzido no projeto — *diz a alguém o que buscar* — e não tem superfície nenhuma |

## O5.1 · ORCID abre a porta; não fecha o cruzamento

A ponte `SCIENCE → PUBLIC VOICE` tem **três degraus**, e eles não se substituem:

| degrau | estado hoje | evidência |
|---|---|---|
| **1 · identidade científica** | **PROVADA para 13 pessoas** | ORCID resolvido em `pub.orcid.org`, instituição declarada, obra em 2024+ |
| **2 · `PERSON ↔ PUBLIC CHANNEL`** | **PROVADO para 5 pessoas** | `CANAL-IDENTIDADE.json`: 44 candidatos → **7 canais `PROVED`**, cobrindo **5 pessoas**; 12 `PLAUSIBLE`; 25 `NOT_PROVED`. Método: nome completo normalizado veta, cidade declarada no ORCID confirma |
| **3 · `PUBLIC CONTENT ↔ SAME PERSON`** | **NÃO PROVADO para ninguém** | o modo usado do ator **não devolve cargo nem empresa**, e o papel declarado — a evidência mais forte — não foi lido. Nenhum conteúdo foi amarrado à pessoa |

**Enunciado correto:**

```
IDENTITY_LINKAGE_BARRIER_REDUCED   = YES
PERSON_TO_PUBLIC_CHANNEL           = PROVED para 5 de 13
PUBLIC_CONTENT_TO_SAME_PERSON      = NOT_PROVED
SCIENCE_TO_PUBLIC_VOICE_LINK       = CAPABILITY_NOW_TESTABLE   ← e não PROVED
```

**Identidade não vira conteúdo sem a ponte.** Provar que Blanca B. Landa tem um perfil
público **não** prova que aquele perfil fala de repilo, nem que o que ele fala é sinal.
O que mudou é que o teste, antes impossível por falta de chave, **agora é executável**.

## O9.1 · O que "vigente com data vencida" ainda não significa

**Classificação: `STATUS_DATE_CONFLICT_OBSERVED`.** O que está medido é apenas isto: existem
34 linhas no registro espanhol e 8 no italiano cujo campo de estado diz *vigente* e cujo
campo de data de caducidade é anterior à data do snapshot. **31 das 34 espanholas
compartilham a mesma data**, o que por si só sugere um evento único, não 31 casos
independentes.

**O que ainda NÃO foi verificado — e sem isso não se publica nada:**

- o que exatamente a coluna de validade significa naquele registro;
- o que exatamente `Vigente` significa naquela fonte;
- se existe renovação, prorrogação ou período de transição que a coluna não mostra;
- se a data lida é de autorização, de documento ou de outra coisa;
- se o snapshot estava desatualizado em relação à fonte viva.

**Até que isso seja verificado, o achado NÃO é:** produto vencido · registro irregular ·
erro regulatório · risco · oportunidade.

**Este é o melhor exemplo existente de por que a gaveta `INVESTIGATE` existe no casco:**
um fato observado, real, com evidência oficial, cuja interpretação ainda não foi ganha.

---

# P · TOOL GAPS — *temos inteligência, nenhuma ferramenta responde bem*

| # | inteligência que existe | por que nenhuma ferramenta atual serve |
|---|---|---|
| **P1** | **A recusa fundamentada** — `ASK_WRONG = 0`, com **14 recusas em 35 perguntas** | é descrito no handoff como *"o ativo mais forte do produto"* e **não tem tela**. O casco tem entrada de pergunta e nenhuma saída |
| **P2** | **O que buscar em seguida** (`MISSING_PROOFS`, filas de descoberta, 132 pesquisadores `NOT_TESTED`) | nenhuma ferramenta mostra a **fila de trabalho da própria inteligência**. Fontes mostra estado da fonte, não o que falta provar |
| **P3** | **Creator map inteiro** — 18 fichas, 6 farmer creators provados, 4 casos de concorrente | **zero superfície no casco.** Nenhuma tela, nenhum bloco, nenhum campo |
| **P4** | **Anomalia de fonte** (O9) | não é caso, não é análise, não é fonte. É um quarto tipo de objeto sem casa |
| **P5** | **Assimetria de portfólio entre países** — ES 44 `LOCAL_REGISTERED`, IT crosswalk em **0**, FR 111 com alegação de AMM | a camada EAME tem o slot (`asymRows`) e o dado dos três países **não é comparável no mesmo eixo** — cada país mediu coisa diferente |
| **P6** | **"Quem viu primeiro"** — o `COMPETITOR OBSERVATION CLOCK`, quinto relógio | está no documento canônico desde 2026-08-30 e **não existe no casco**, que só tem os quatro relógios agronômicos |

---

# Q · CASCO GAPS — *a capacidade é legítima, o casco não tem lugar adequado*

| # | lacuna | gravidade |
|---|---|---|
| **Q1** | ~~O casco não está versionado~~ → **FECHADA nesta passagem.** O casco vive agora em `casco/canonical/SINTONIA-EAME-PILOT-V7.html`, byte a byte, com `.gitattributes` impedindo o Git de tocar nos fins de linha e prova de que o blob guardado tem o mesmo SHA-256 do original | **resolvida** |
| **Q2** | **O acervo não existe inteiro em nenhuma branch.** Seis branches vivas, nenhuma mesclada. **E isso NÃO pede merge geral agora** — o refresh final consome os *handoffs canônicos* de cada missão, não a árvore dela. Integração vem depois de RED TEAM → ARBITRAGEM | **média — custódia, não bloqueio** |
| **Q3** | **O casco tem 10 itens de navegação; a hipótese de arquitetura de 2026-08-29 descreve "duas ferramentas e uma pergunta".** Não é disputa: o casco é `CANONICAL_PILOT_SHELL`, o documento é `PRODUCT_ARCHITECTURE_HYPOTHESIS`. **A lacuna real é que MT1/MT2/MT3 aparecem em duas superfícies** (`Análises` e `Radar/Casos`) sem que nada diga ao usuário que são a mesma ferramenta | **média — semântica** |
| **Q4** | **Ask Sintonia: entrada sem saída** | média |
| **Q5** | **Nenhuma superfície para creators nem para especialistas** — só um bloco com rótulo problemático | média |
| **Q6** | **Badges de país desatualizados** (IT e FR `EM COLETA`; branches dizem `COMPLETE`) | baixa — mas é exatamente o tipo de número velho que o repositório combate com marcadores de sync |
| **Q7** | **SUPPLY listada sempre**, com estado `NÃO DETERMINADO` | baixa — convida ao preenchimento |
| **Q8** | **`Análises` é a tela mais rasa onde mora o valor** | média |

---

# J · CAPACIDADES LATENTES — **hipóteses**, não decisões

> **Nenhuma delas é candidata a ferramenta nesta passagem.** A regra de economia vale:
> **aprimorar ferramenta existente antes de criar nova.** Cada ficha diz onde a capacidade
> caberia hoje.

---

### J1 · CROSSWALK ORCID/ROR ↔ CANAL PÚBLICO

```
OBSERVED_NEED     ligar ciência a voz pública sem casar por nome
DATA_SUPPORTING   13 pessoas com ORCID resolvido em pub.orcid.org, 6 recortes, 3 países
                  + 44 candidatos de canal com 7 PROVED e 12 PLAUSIBLE
USER              CIÊNCIA & P&D · TÉCNICO · MARKET DEVELOPMENT
DECISION          quem chamar para explicar um problema de campo, com identidade provada
EXISTING_TOOL     Caso → aba "Ciência e pessoas"  ·  Radar do Futuro → "Palavra dos
                  pesquisadores"
NEW_TOOL_NEEDED   NÃO
WHY_NOT_NEW       é um crosswalk de identidade — infraestrutura, não tela
ESSENCE_ALIGNMENT alta — conecta fontes independentes, que é a promessa
ESSENCE_RISK      virar diretório de influência. Mitigação: sem ordem, sem score
DATA_READINESS    MÉDIA — degrau 1 provado (13 pessoas), degrau 2 provado (5), degrau 3
                  não provado. Ver O5.1
STATE             IDENTITY_LINKAGE_BARRIER_REDUCED · CAPABILITY_NOW_TESTABLE
```

**Por que isto é o achado mais importante da PASSAGEM 1:** a rota `SCIENCE → PUBLIC VOICE`
foi marcada `NOT_REACHED` com a causa escrita — *"ela não se constrói com nome; falta um
identificador declarado que atravesse camadas"*. O piloto produziu esse identificador para
13 pessoas, e provou canal público para 5 delas. **A barreira caiu; o cruzamento não fechou.**
O que era impossível virou **testável** — e nunca foi testado. Isso é diferente, e menor, do
que "está provado".

---

### J2 · MAPA DE PERGUNTAS TÉCNICAS DA AUDIÊNCIA

```
OBSERVED_NEED     saber o que o campo não entende, por cultura e problema
DATA_SUPPORTING   196 perguntas em 991 comentários (19,8 %), 6 recortes, 3 países;
                  + 148 perguntas na rodada espanhola anterior
USER              MARKETING (o que comunicar) · TÉCNICO (o que explicar)
DECISION          que material técnico produzir, e para qual dúvida
EXISTING_TOOL     Caso → camada Campo  ·  Radar do Futuro → sinal
NEW_TOOL_NEEDED   NÃO SEI — depende de a pergunta se agrupar por assunto, o que não foi
                  testado
ESSENCE_RISK      **alto** — vira "radar de buzz" com facilidade. A pergunta mede
                  DEMANDA POR INFORMAÇÃO, nunca estado do campo
DATA_READINESS    MÉDIA — o dado existe; a taxonomia por assunto não
```

---

### J3 · DIRETÓRIO DE ESPECIALISTAS POR CASO

```
DATA_SUPPORTING   13 pessoas, instituição declarada, obra em 2024+, ORCID resolvido,
                  distribuídas exatamente nos 6 recortes congelados
EXISTING_TOOL     Caso → "Ciência e pessoas". **Cabe inteiro dentro do caso.**
NEW_TOOL_NEEDED   NÃO
WHY_NOT_NEW       fora do caso, uma lista de pesquisadores é um diretório; dentro do caso,
                  é a resposta a "quem pode explicar isto?"
ESSENCE_RISK      ranking de autoridade. Mitigação: sem ordem de mérito; GDPR antes de
                  qualquer exposição
DATA_READINESS    ALTA
```

---

### J4 · "WHO COULD MARKETING CALL?" — creators como camada, não como aba

```
DATA_SUPPORTING   18 fichas · 2 ACTIVATION_READY · 4 PROMISING · 12 RESEARCH_NEEDED ·
                  6 farmer creators PROVED · 4 casos de concorrente com creator
USER              MARKETING (primário) · MARKET DEVELOPMENT
DECISION          quem já tem relevância real junto ao público daquela cultura e região
EXISTING_TOOL     nenhuma — é o P3
NEW_TOOL_NEEDED   **NÃO SEI** — quatro formas possíveis, e a escolha é de negócio:
                  (a) ferramenta própria · (b) visão dentro de Radar/Casos ·
                  (c) camada contextual do caso · (d) combinação
ESSENCE_ALIGNMENT média — responde "quem pode agir", não "o que merece atenção"
ESSENCE_RISK      **alto** — ranking de influencer é o oposto da essência.
                  `FOLLOWERS ≠ AUTHORITY`, e a ordenação já é por ESTADO
DATA_READINESS    MÉDIA — 2 de 18 acionáveis; audiência não medida; só Instagram
```

**Pergunta que o red team deve responder, e não esta rodada:** um creator só interessa
**ligado a um caso**? Hoje o único `ACTIVATION_READY` italiano é de **milho**, e não há
caso italiano de milho aberto no radar. Se a resposta for "sim", a camada (c) vence e a
ferramenta própria morre.

---

### J5 · FILA DE PROVAS QUE FALTAM (`MISSING_PROOFS`)

```
OBSERVED_NEED     transformar "não sei" em tarefa
DATA_SUPPORTING   MISSING_PROOFS nas 18 fichas · 132 pesquisadores NOT_TESTED ·
                  34 de 43 hubs com PEOPLE_EXTRACTED = 0 · 16 fontes NÃO SEI ·
                  47 achados NAO_ATENDIDO da auditoria
USER              todas as áreas, e principalmente quem opera o Sintonia
EXISTING_TOOL     Fontes (parcialmente) — mas Fontes mostra estado da FONTE, não da PROVA
NEW_TOOL_NEEDED   NÃO SEI
ESSENCE_ALIGNMENT **muito alta** — "o que ainda não sabemos" é uma das seis perguntas da
                  gramática do próprio casco, e é a única sem superfície própria
ESSENCE_RISK      virar backlog de engenharia exposto ao cliente
DATA_READINESS    ALTA — o dado existe em quatro artefatos diferentes
```

---

### J6 · CONFLITO ENTRE ESTADO E DATA COMO CLASSE DE ITEM

```
DATA_SUPPORTING   ES: 34 `Vigente` com caducidade anterior ao snapshot, 31 na MESMA data
                  IT: 8 EXPIRED_BUT_ACTIVE_STATUS
                  ES: ES-01717 renomeado MAXENTIS -> SORATEL MAX (change event real)
USER              REGULATÓRIO · PORTFÓLIO
EXISTING_TOOL     Radar/Casos já tem as classes `INVESTIGATE` e `CHANGE DETECTED`
NEW_TOOL_NEEDED   **NÃO** — a classe já existe no casco e está vazia
ESSENCE_ALIGNMENT alta — é literalmente "o que merece atenção", com evidência oficial
STATE             STATUS_DATE_CONFLICT_OBSERVED · INVESTIGATE_CANDIDATE
DATA_READINESS    ALTA para a OBSERVAÇÃO · NULA para a INTERPRETAÇÃO
WHAT_MUST_COME_FIRST  o que significa a coluna de validade; o que significa `Vigente`;
                  se há renovação, prorrogação ou transição; que data é aquela; se o
                  snapshot estava velho. Ver O9.1
```

**É a capacidade latente mais barata do inventário — e a que mais exige disciplina.** O
casco já tem a caixa e o dado já existe; o que **não** existe é a interpretação. Ligar os
dois sem responder as cinco perguntas acima publicaria "34 registros irregulares" a partir
de um conflito de metadados que pode ser rotina administrativa.

---

### J7 · `LABEL_USE_STAGE` FRANCÊS COMO PRIMEIRA RESTRIÇÃO TEMPORAL REAL

```
DATA_SUPPORTING   E-Phy: 582 linhas de uso ADAMA · 562 com dose · 376 com BBCH mínimo ·
                  414 com BBCH máximo · 367 linhas ancoradas em cultura x alvo
USER              TÉCNICO · MARKET DEVELOPMENT · MARKETING
EXISTING_TOOL     Janelas da Cultura — hoje 100 % vazia nos três países
NEW_TOOL_NEEDED   NÃO
STATE             WINDOW_CONSTRAINT_DATA_EXISTS_FR
NOT_STATE         APPLICATION_WINDOW_READY_FR  ← não afirmar sem prova
ESSENCE_RISK      **confundir estágio de rótulo com janela agronômica.** São dois dos
                  quatro relógios e o casco já os separa. Fundir seria erro grave
DATA_READINESS    ALTA para a RESTRIÇÃO em FR · BAIXA em ES (3) · NULA em IT (0)
                  NULA, nos três, para a JANELA REAL
```

**O que as 376 linhas dizem, e o que não dizem.** Elas dizem **em que estágio da planta o
uso é autorizado** — é uma restrição escrita no rótulo. Não dizem em que estágio a lavoura
está hoje, em que região, nem se ainda dá tempo.

```
LABEL_STAGE  ≠  REAL-TIME CROP WINDOW  ≠  CURRENT FIELD STAGE  ≠  COMMERCIAL WINDOW
```

**Consequência honesta:** o rótulo francês ajuda a *construir* a janela, e sozinho não a
fecha. **`Janelas da Cultura` continua sem relógio vivo da lavoura em país nenhum** — falta
o componente temporal e local. O que a França permite hoje é preencher **um** dos quatro
relógios, e só a metade dele que é restrição.

---

### J8 · MATRIZ DE COMPARABILIDADE COMO PEÇA CENTRAL DA EAME

```
DATA_SUPPORTING   X-008 mediu: só ÁREA DE CULTURA e PREÇO são comparáveis entre os três.
                  O casco já declara as 8 dimensões com estado por país
EXISTING_TOOL     Camada EAME — o bloco existe e enche hoje
NEW_TOOL_NEEDED   NÃO
ESSENCE_ALIGNMENT altíssima — "três mercados observados, dois comparáveis, um não
                  comparável — e não uma média regional"
DATA_READINESS    ALTA
```

---

### J9 · RELÓGIO DE OBSERVAÇÃO — "quem viu primeiro?"

```
DATA_SUPPORTING   FIRST_OBSERVED / LAST_OBSERVED / CHANGE_OBSERVED / SOURCE_DATE /
                  AS_OF_DATE existem no contrato; boletim IT 13/08/2026; ROPF 29/08/2026;
                  E-Phy 25/08/2026; RAIF safra 2026
USER              MARKET DEVELOPMENT · MARKETING
EXISTING_TOOL     Caso → 4 relógios. **O quinto relógio não existe no casco**
NEW_TOOL_NEEDED   NÃO — é um relógio a mais dentro do caso
ESSENCE_RISK      **`OBSERVATION_START != ACTIVITY_START`** e
                  `SEQUÊNCIA OBSERVADA != PROPAGAÇÃO`. Sem isso vira narrativa de corrida
DATA_READINESS    MÉDIA — as datas existem; a comparação entre camadas nunca foi montada
```

---

## J.10 · Capacidades que a PASSAGEM 2 pode criar, e que hoje não existem

Registro antecipado, sem antecipar veredito:

| missão em paralelo | cruzamento que ela **pode** abrir |
|---|---|
| **EARLY SIGNAL TERRITORIAL** | `FIELD VOICE × CAMPO MEDIDO` num segundo território; e a promoção dos 12 canais `PLAUSIBLE` |
| **CREATOR MAP · fechamento** | `CREATOR × CULTURA × CASO ABERTO` — o teste que decide entre ferramenta e camada (J4) |
| **META COMPETITOR INTELLIGENCE** | fecha `N5`. É a **única** coluna de ativação observada que o contrato de competição prevê e nunca teve dado |
| **COMPETITOR FORESIGHT (IP/regulatório/timeline)** | `VENCIMENTO × TITULAR × MOLÉCULA` deixa de ser só ADAMA e vira mapa competitivo — o eixo que X-005 já provou |

**Duas dessas quatro atacam diretamente o ponto mais fraco do produto**
(`COMPETIÇÃO · ativação observada`, hoje `PLANNED` em todos os países). Se entregarem,
a camada de competição sai de uma coluna para duas — e a convergência ganha uma perna
independente real.

---

# REFRESH ÚNICO — o que reler na PASSAGEM 2

**Ler uma vez. Não perseguir HEAD. Incorporar só o que muda materialmente a inteligência.**

```
CHEGARAM  1 de 4      ►  CREATOR MAP (2026-08-30)
FALTAM    3 de 4      ►  EARLY SIGNAL TERRITORIAL
                      ►  META COMPETITOR EAME
                      ►  COMPETITOR FORESIGHT · IP / REGULATORY / PRODUCT
REFRESH_EXECUTADO = NÃO   — o refresh é ÚNICO e só roda com as quatro na mesa
```

**Chegar não é ser integrado.** O que chega é registrado como ponteiro e como aviso de
obsolescência sobre a PASSAGEM 1 — nada mais. Integrar entrega por entrega gastaria quatro
leituras onde o combinado é uma, e reabriria a análise a cada commit.

```
1 · EARLY SIGNAL TERRITORIAL
    docs/**/HANDOFF*  ·  data/samples/SENSOR-PILOT/MEDICAO.json (recontar)
    procurar: os vereditos escritos (O8) e FIELD_VOICE por território

2 · CREATOR MAP · fechamento do piloto        ►►► CHEGOU em 2026-08-30 · NÃO INTEGRADO
    branch  claude/eame-agro-creators-map-77c4ld   HEAD 248bd27   PUSHED, sem merge
    HANDOFF     docs/creators/HANDOFF-INTELLIGENCE-CREATOR-MAP-EAME.md
    CAPACIDADE  data/samples/CREATOR-MAP-EAME/CREATOR-CAPABILITY-EAME.json
    CONGELAMENTO data/samples/CREATOR-MAP-EAME/PILOT-FREEZE-STATE.json
    STATE = FROZEN_WAITING_FOR_INTELLIGENCE · custo total US$ 0,3224 · 106 provas
    procurar: os cinco eixos de lookup (country, region, crop, entity_type,
    activation_state); os dez campos por resultado, com WHAT_IS_NOT_KNOWN;
    CAPABILITY_COVERAGE_GAP italiano e suas seis causas; a regra de revalidação
    (REVALIDATION_NEEDED_AFTER = NOT_YET_DEFINED, deliberadamente)

3 · META COMPETITOR INTELLIGENCE
    procurar: EU-T9-002 saindo de NÃO TESTADO; COMPETITOR_PAID_META_ACTIVITY com dado

4 · COMPETITOR FORESIGHT · IP / REGULATORY / PRODUCT TIMELINE
    procurar: BY_HOLDER / TOP_HOLDERS / BY_SUBSTANCE (hoje ausentes da rota canônica);
    vencimento por titular além da ADAMA

DEPOIS — e só depois — fechar:
    E CONVERGENCES · F ATTENTION QUEUE · G DAILY VALUE · H ACTION MAP
    K TOOL IMPROVEMENTS · L NEW TOOL CANDIDATES · M NOT-A-TOOL
    R INTELLIGENCE -> TOOL MAP · S HOSE MAP · T RED-TEAM-PACK · U PERGUNTAS
```

**A regra do refresh, escrita para quem executar:** consumir o **handoff canônico** de cada
missão — o documento que ela escreveu para ser lido de fora. **Não** fundir as seis branches
para criar "um repo com tudo". Código experimental de uma missão não entra em outra sem
arbitragem.

---

# ESTADO DESTA PASSAGEM

```
PASSAGEM_1 ....................... FECHADA
PASSAGEM_2 ....................... WAITING_FOR_FINAL_REFRESH  (4 entregas)

CASCO_V7 ......................... CANONICAL_PILOT_SHELL · FROZEN_PILOT_SHELL
CASCO_CANONICAL_FILE ............. casco/canonical/SINTONIA-EAME-PILOT-V7.html
CASCO_SHA_MATCH .................. YES
CASCO_ALTERADO ................... NÃO

PRODUCT_IMPLEMENTATION_MODE ...... NOT_ENTERED
MANGUEIRA_LIGADA ................. NÃO
READ_MODEL_CRIADO ................ NÃO
SUPABASE_LIGADO .................. NÃO
NAVEGAÇÃO_ALTERADA ............... NÃO
FERRAMENTA_CRIADA_OU_REMOVIDA .... NÃO
ESTADO_PROMOVIDO ................. NENHUM
BRANCHES_MESCLADAS ............... NENHUMA (e nenhuma deve ser, agora)
```

**Depois do refresh vem o red team externo, depois a arbitragem, e só então
`PRODUCT_IMPLEMENTATION_MODE`.** A partir dali o V8 pode evoluir sobre o V7 — mudando
ferramentas, superfícies, textos, fluxos e navegação quando houver evidência — e o V7
permanece preservado byte a byte como testemunha. A política completa está em
`A-BASELINE-DO-CASCO-EAME.md`, seção 0.3.
