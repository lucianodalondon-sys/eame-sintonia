# PORTAL-CAPABILITY-INVENTORY — o que a navegação mostra hoje, e com que autoridade

```
PORTAL_PREVIEW_STATE  = DIAGNOSTIC_ONLY
PRODUCTION_PROMOTION  = BLOCKED
PORTAL_READY_FOR_MEETING = NO
CURRENT_PRODUCT_SCOPE = ITALY_ONLY
```

**Data da medição:** 2026-09-06
**Medido em:** `claude/auditoria-acervo-inteligencia-2nknje` @ `e4f3e8b`, árvore limpa
**Superfície medida:** `italia-portale/client/portale.html` + `casa.html`, renderizados
no Chromium e lidos pelo modelo (`window.ITALY_APP_MODEL`), em italiano e inglês.

**Este ficheiro NÃO corrige nada.** Não renomeia, não apaga, não reorganiza, não
remove nada da navegação. Só mede e nomeia.

---

## LEI ZERO APLICADA A ESTE INVENTÁRIO

Uma coleção existente não autoriza uma ferramenta. Uma inteligência disponível não
autoriza uma aba. Por isso `APPROVED_CAPABILITY` aqui **não é opinião minha** — tem
de apontar para um documento nomeado e datado no repositório.

| valor | significado exacto |
|---|---|
| `YES` | existe documento nomeado e datado que autoriza este item como superfície do portal |
| `NO` | existe documento nomeado e datado que o **recusa** como ferramenta ou como item de menu |
| `UNKNOWN` | **nenhum documento** o aprova nem o recusa — não é permissão, é ausência |

`UNAPPROVED_CAPABILITY` = `NO` + `UNKNOWN`.

---

## A CADEIA DE AUTORIDADE — onde é que "aprovado" mora

Medido: a expressão `APPROVED_CAPABILITY` aparece **0 vezes** em todo o repositório.
Não existe registo de capacidades aprovadas para o portal. Existem, sim, quatro
documentos que decidem, e um deles declara-se vencedor:

| documento | data | o que decide |
|---|---|---|
| **`docs/piloto/ARQUITETURA-DE-PRODUTO-ATUAL.md`** | 2026-08-29 · MISSÃO 10 | **PORTA ÚNICA.** «Se dois documentos discordarem sobre o que é o produto, **este vence**.» |
| `docs/capacidades/ATLAS-DE-CAPACIDADES-EAME.md` | 2026-08-28 · MISSÃO 07 | 22 capacidades `COMPROVADO`. **ITALY = 1** (EUROPE 11 · FRANCE 3 · SPAIN 7) |
| `docs/ferramentas/CATALOGO-DE-FERRAMENTAS-EAME.md` | 2026-08-28 | auto-declarado **OBSOLETO para desenho de produto**: «o SINTONIA deixou de ser um menu de ferramentas na MISSÃO 09» |
| `docs/ferramentas/ARQUITETURA-DE-INFORMACAO-EAME.md` | 2026-08-28 | «As nove áreas **NÃO são nove telas nem nove módulos**» |

### O que a porta única aprova

```
MT1 · REGULATORY & EXPIRY EXPOSURE      ferramenta principal
MT2 · GEOGRAPHIC COMMERCIAL PRIORITY    ferramenta principal
MT3 · PUBLIC ACTIVATION GAP             exploratória
Ask Sintonia                            «Não é uma quarta ferramenta»
HOME                                    cinco classes de item
SUPPORTING ENGINE                       «por baixo, NÃO NO MENU»
```

O motor de suporte, textualmente: *science · experts · climate context · entity
identity · market/crop context · data clock · change events · normalizações ·
camada de evidência e proveniência*.

### O que a porta única proíbe

| proibição | texto |
|---|---|
| menu de módulos | «desenhar um **menu de módulos independentes**» está na tabela **O QUE O DESIGN NÃO PODE FAZER** |
| DO NOT BUILD | «distribution network · supply watch · **crop pulse genérico**» |
| na home | «Proibido na home: **contador de fontes**, **contador de linhas**, buzz, score de influência, ou qualquer número que não mude uma decisão» |
| MT2 | OUTPUT é `PRIORITY TO INVESTIGATE` — «**nunca** SALES OPPORTUNITY» |

E `data/samples/EAME-COMPETITOR-CONTRACT-V1.json` (2026-08-30), sobre a camada de
concorrência: *«não é um painel de concorrência, não é um ranking, não é um score
de ameaça, **não é uma ferramenta isolada**. **Não existe tela nem número único
saindo daqui**»* — reforçado por `D-021` no diário de decisões: *«A camada de
concorrente é derivada e não vira dona de nada»*.

---

## NAVEGAÇÃO MEDIDA — 11 itens na barra + 1 integração + 2 entradas de ecrã

Medido nas duas línguas. Os números são os que a barra imprime.

| # | IT | EN | contador | destino |
|---|---|---|---|---|
| 0 | OPPORTUNITÀ ATTUALI | CURRENT OPPORTUNITIES | 13 | página `casa.html` |
| 1 | Radar delle Opportunità | Opportunity Radar | 13 | vista `meeting` |
| 2 | Archivio segnali V21 | V21 Signal Archive | 3 | vista `future` |
| 3 | Finestre Colturali | Crop Windows | 29 | vista `windows` |
| 4 | Polso di Mercato | Market Pulse | 157 | vista `market` |
| 5 | Voci dal Campo | Field Voices | 79 | vista `voices` |
| 6 | Concorrenza | Competitor Watch | 577 | vista `competitors` |
| 7 | Intelligence Scientifica | Scientific Intelligence | 88 | vista `science` |
| 8 | Portafoglio | Portfolio | 173 | vista `portfolio` |
| 9 | Archivio | Archive | 1114 | vista `archive` |
| 10 | Archivio fonti V21 | V21 Source Archive | 189 | vista `sources` |
| I1 | Rete Commerciale di Campo | Field Sales Channel | 18 | vista `field` · rótulo **INTEGRAZIONI · DEMO** |
| E1 | *(linha no radar)* RADAR · DA VALIDARE | RADAR · TO VALIDATE | 21 | filtro dentro de `meeting` |
| E2 | *(linha no radar)* SEGNALI GREZZI | RAW SIGNALS | 8 | filtro dentro de `meeting` |

---

## FICHAS

### 0 · OPPORTUNITÀ ATTUALI

```
MENU_LABEL            = OPPORTUNITÀ ATTUALI · CURRENT OPPORTUNITIES  (13)
CAPABILITY_ID         = HOME  (ARQUITETURA-DE-PRODUTO-ATUAL §HOME)
SOURCE_OF_DEFINITION  = docs/piloto/ARQUITETURA-DE-PRODUTO-ATUAL.md, 2026-08-29
DATA_INPUT            = window.ITALY_CASA (italy-casa.js), gerado por scripts/it_casa_dados.py
INTELLIGENCE_INPUT    = pacote V21-69bf448ac934a6d9 · 43 casos · lei ADAMA de relevancia
CURRENT_OWNER         = italia-portale/client/casa.html + italy-casa.js
LEGACY_OR_CURRENT     = CURRENT
DUPLICATES_WITH       = item 1 (mesmo numero 13, mesma populacao, medido)
APPROVED_CAPABILITY   = YES  (a HOME e aprovada como superficie)
```
**Ressalva medida:** a HOME é aprovada; a sua presença **como item de menu ao lado
do Radar, com o mesmo contador**, não está definida em documento nenhum. As cinco
classes que a porta única manda a home responder são `REGULATORY DEADLINE`,
`GEOGRAPHIC AGRONOMIC PRIORITY`, `ACTIVATION QUESTION`, `CHANGE DETECTED`,
`INVESTIGATE` — a correspondência entre estas cinco e o que `casa.html` desenha
**não foi medida neste inventário**: `NÃO SEI`.

### 1 · Radar delle Opportunità

```
MENU_LABEL            = Radar delle Opportunità · Opportunity Radar  (13)
CAPABILITY_ID         = MT2 · GEOGRAPHIC COMMERCIAL PRIORITY
SOURCE_OF_DEFINITION  = docs/piloto/ARQUITETURA-DE-PRODUTO-ATUAL.md §MT2
DATA_INPUT            = AM.collections.opportunities (43, CANONICAL, HANDOFF_V21)
INTELLIGENCE_INPUT    = adama-relevance.js (scripts/adama_relevance.py) · meeting-surface.js
CURRENT_OWNER         = portale.html vista 'meeting' + meeting-surface.js
LEGACY_OR_CURRENT     = CURRENT
DUPLICATES_WITH       = item 0 (contador identico) · vista legacy 'case' (detalhe paralelo)
APPROVED_CAPABILITY   = YES
```
**Conflito de nome com o contrato:** MT2 manda dizer `PRIORITY TO INVESTIGATE` e
proíbe `SALES OPPORTUNITY`. O ecrã chama-se «OPPORTUNITÀ» e um dos estados
impressos na ficha é `PRONTO PER LA VENDITA` / `SALES READY` (medido em 5 dos 13
cartões). **Não corrigido aqui** — nomeado.

### 2 · Archivio segnali V21

```
MENU_LABEL            = Archivio segnali V21 · V21 Signal Archive  (3)
CAPABILITY_ID         = FUTURE_THEME  (data/samples/RADAR-DO-FUTURO-CONTRACT-V1.json)
SOURCE_OF_DEFINITION  = contrato de DADO, 2026-08-30 — «define a entidade
                        FUTURE_THEME, a regua de maturidade e as regras de
                        promocao. NAO HA UI AQUI.»
DATA_INPUT            = AM.collections.futureSignals (3, CANONICAL)
INTELLIGENCE_INPUT    = OpenAlex (2 sinais) + CELLAR/actos UE (1 sinal)
CURRENT_OWNER         = portale.html vista 'future'
LEGACY_OR_CURRENT     = CURRENT
DUPLICATES_WITH       = E2 «SEGNALI GREZZI» (8, dentro do radar) ·
                        futureScenarios (56, DEMO_SCENARIO)
APPROVED_CAPABILITY   = UNKNOWN  (o contrato define o motor e recusa-se a definir UI)
```
**Medido:** três populações usam a palavra «sinal» — 3 canónicos, 8 do radar,
56 de demonstração.

### 3 · Finestre Colturali

```
MENU_LABEL            = Finestre Colturali · Crop Windows  (29)
CAPABILITY_ID         = calendario agronomico
SOURCE_OF_DEFINITION  = data/samples/AGRONOMIC-CALENDAR-DESIGN-DATA-CONTRACT-V1.json,
                        2026-08-30 — «e o contrato de DADO. NAO DIZ COMO DESENHAR.»
                        FACT_LOCATION = ES  (contrato espanhol; o portal e italiano)
DATA_INPUT            = AM.collections.cropWindows (29, CANONICAL, ITALY_CANONICAL.windows)
INTELLIGENCE_INPUT    = janelas canonicas italianas
CURRENT_OWNER         = portale.html vistas 'windows' + 'window' · italy-canonical-windows.js
LEGACY_OR_CURRENT     = CURRENT
DUPLICATES_WITH       = coleccao 'windows' == 'cropWindows' (alias no modelo, ambas 29)
APPROVED_CAPABILITY   = UNKNOWN
```
**Nota estrutural medida:** `SEASONAL TIMING` é um **INPUT declarado de MT2**, não
uma ferramenta. Candidato a viver dentro de MT2.

### 4 · Polso di Mercato

```
MENU_LABEL            = Polso di Mercato · Market Pulse  (157)
CAPABILITY_ID         = CAP-019 (preco semanal de cereal) — COUNTRY: FRANCE · SPAIN
SOURCE_OF_DEFINITION  = ATLAS-DE-CAPACIDADES-EAME.md. Nao cobre ITALIA.
DATA_INPUT            = AM.collections.marketObservations (157, CANONICAL)
INTELLIGENCE_INPUT    = italy-market-pulse.js + HANDOFF_V21.marketObservations
CURRENT_OWNER         = portale.html vista 'market'
LEGACY_OR_CURRENT     = CURRENT
DUPLICATES_WITH       = —
APPROVED_CAPABILITY   = NO
```
**Prova da recusa:** «market/crop context» está nomeado no **SUPPORTING ENGINE —
por baixo, não no menu**. E `DO NOT BUILD` inclui «crop pulse genérico».

### 5 · Voci dal Campo

```
MENU_LABEL            = Voci dal Campo · Field Voices  (79)
CAPABILITY_ID         = FIELD VOICES
SOURCE_OF_DEFINITION  = CATALOGO-DE-FERRAMENTAS: «CONCEPT — sem fonte de dado»,
                        TECHNICAL_FEASIBILITY BAIXA, ADAMA_ALIGNMENT UNKNOWN.
                        ARQUITETURA-DE-PRODUTO-ATUAL: «field voices —
                        NOT REACHED / NAO SEI, nao KILL»
DATA_INPUT            = AM.collections.publicVoices (79, CANONICAL, HANDOFF_V21)
INTELLIGENCE_INPUT    = comentarios publicos YouTube; identidade nunca promovida
CURRENT_OWNER         = portale.html vista 'voices'
LEGACY_OR_CURRENT     = CURRENT
DUPLICATES_WITH       = coleccoes 'voices' == 'publicVoices' (alias, ambas 79) ·
                        'channels' == 'publicChannels' (alias, ambas 62)
APPROVED_CAPABILITY   = NO
```
**O caso mais claro de dataset a virar ferramenta:** a última definição escrita
diz `CONCEPT, sem fonte`. Depois apareceram 79 vozes no pacote, e a aba nasceu.
Ninguém reabriu a ficha. **A LEI ZERO desta missão nomeia exactamente isto.**

### 6 · Concorrenza

```
MENU_LABEL            = Concorrenza · Competitor Watch  (577)
CAPABILITY_ID         = camada COMPETITOR da convergencia
SOURCE_OF_DEFINITION  = data/samples/EAME-COMPETITOR-CONTRACT-V1.json, 2026-08-30
DATA_INPUT            = AM.collections.competitorActivities (577, CANONICAL)
INTELLIGENCE_INPUT    = registo nacional + comunicacao publica + actividade tecnica
CURRENT_OWNER         = portale.html vistas 'competitors','company','event','cproduct'
LEGACY_OR_CURRENT     = CURRENT
DUPLICATES_WITH       = —
APPROVED_CAPABILITY   = NO
```
**Prova da recusa, textual:** «não é um painel de concorrência… **não é uma
ferramenta isolada**. **Não existe tela nem número único saindo daqui**.» A barra
imprime `577` — que é, literalmente, o número único que o contrato proíbe.
Reforço: `D-021`, «a camada de concorrente é derivada e não vira dona de nada».

### 7 · Intelligence Scientifica

```
MENU_LABEL            = Intelligence Scientifica · Scientific Intelligence  (88)
CAPABILITY_ID         = CAP-017 (quem trabalha repetidamente um problema) — FRANCE · SPAIN
SOURCE_OF_DEFINITION  = ATLAS-DE-CAPACIDADES. Nao cobre ITALIA.
DATA_INPUT            = scienceRecords 88 · researchers 60 · resistance 34 ·
                        scienceThemes 5 · scienceInstitutions 6
CURRENT_OWNER         = portale.html vistas 'science' + 'theme' · italy-science-business.js
LEGACY_OR_CURRENT     = CURRENT
DUPLICATES_WITH       = 'researchers' tambem alimenta o directorio de pessoas
                        do ecra Fontes (people = 66, derivado)
APPROVED_CAPABILITY   = NO
```
**Prova:** «science · experts» está nomeado no **SUPPORTING ENGINE — por baixo,
não no menu**.

### 8 · Portafoglio

```
MENU_LABEL            = Portafoglio · Portfolio  (173)
CAPABILITY_ID         = CAP-007 (calendario de vencimento IT) — a UNICA capacidade
                        COMPROVADA para ITALIA no atlas
SOURCE_OF_DEFINITION  = ATLAS-DE-CAPACIDADES CAP-007 · ARQUITETURA §MT1
DATA_INPUT            = products 173 (= productsRegulatory 163 + productsCommercial 51,
                        deduplicado) · productRelationships 2030 · activeIngredients 53
CURRENT_OWNER         = portale.html vistas 'portfolio' + 'product'
LEGACY_OR_CURRENT     = CURRENT
DUPLICATES_WITH       = 'regulatory' == 'productsRegulatory' (alias, 163) ·
                        'commercial' == 'productsCommercial' (alias, 51) ·
                        'regulatoryLinks' == 'productRelationships' (alias, 2030)
APPROVED_CAPABILITY   = UNKNOWN
```
**Leitura medida:** o portfólio é `INPUT` declarado de MT1 **e** de MT2, e
«entity identity» está no motor de suporte. Como **ferramenta autónoma** não tem
definição. É o candidato mais forte a ser a face de MT1, não uma aba de catálogo.

### 9 · Archivio

```
MENU_LABEL            = Archivio · Archive  (1114)
CAPABILITY_ID         = (nenhum)
SOURCE_OF_DEFINITION  = NENHUM. Nao existe ficha, contrato ou decisao sobre um Arquivo.
DATA_INPUT            = AM.collections.archive (1114, REAL_DERIVED, 'derived')
INTELLIGENCE_INPUT    = indice sobre as outras coleccoes — nao traz facto proprio
CURRENT_OWNER         = portale.html vista 'archive'
LEGACY_OR_CURRENT     = CURRENT
DUPLICATES_WITH       = itens 2 e 10 (tres entradas com a palavra «Archivio») ·
                        e com a pesquisa (searchIndex, 1655 entradas, 17 familias)
APPROVED_CAPABILITY   = UNKNOWN
```
**Medido:** 1114 é um índice derivado, não uma família de facto. É um **contador
de linhas** — a home proíbe-o explicitamente; a barra imprime-o.

### 10 · Archivio fonti V21

```
MENU_LABEL            = Archivio fonti V21 · V21 Source Archive  (189)
CAPABILITY_ID         = camada de evidencia e proveniencia
SOURCE_OF_DEFINITION  = ARQUITETURA §SUPPORTING ENGINE
DATA_INPUT            = AM.collections.sources (189, CANONICAL) + people 66 + news 8
CURRENT_OWNER         = portale.html vistas 'sources','source','person'
LEGACY_OR_CURRENT     = CURRENT
DUPLICATES_WITH       = itens 2 e 9 (a palavra «Archivio») ·
                        directorio de pessoas partilhado com Ciencia
APPROVED_CAPABILITY   = NO
```
**Prova dupla:** é motor de suporte («camada de evidência e proveniência», por
baixo, não no menu) **e** a home proíbe textualmente «**contador de fontes**».

### I1 · Rete Commerciale di Campo

```
MENU_LABEL            = Rete Commerciale di Campo · Field Sales Channel  (18)
                        sob o cabecalho INTEGRAZIONI · DEMO
CAPABILITY_ID         = (nenhum)
SOURCE_OF_DEFINITION  = NENHUM
DATA_INPUT            = AM.collections.fieldMessages — 18, proveniencia SYNTHETIC_DEMO
INTELLIGENCE_INPUT    = nenhum: sao mensagens fabricadas
CURRENT_OWNER         = portale.html vista 'field'
LEGACY_OR_CURRENT     = CURRENT (rotulado DEMO no ecra)
DUPLICATES_WITH       = —
APPROVED_CAPABILITY   = UNKNOWN
```
**Medido:** é a única entrada de navegação cuja fonte é `SYNTHETIC_DEMO`. Está
honestamente rotulada; não está aprovada.

### E1/E2 · entradas dentro do radar

```
E1 RADAR · DA VALIDARE (21) · E2 SEGNALI GREZZI (8)
```
São **filtros da mesma população de 43**, apresentados como linhas dentro do
ecrã e não como abas. Medido: 13 + 21 + 8 + 1 erro = 43. **Esta é a forma
correcta** — ficam registados como o contra-exemplo do resto do menu.

---

## AS OITO LISTAS PEDIDAS

### 1 · Capacidades duplicadas

| duplicação | prova medida |
|---|---|
| **OPPORTUNITÀ ATTUALI ↔ Radar delle Opportunità** | duas entradas, **contador idêntico 13**, mesma população, mesmo `BUILD_ID`. Uma abre uma página, a outra uma vista |
| **detalhe de oportunidade: `mcase` ↔ `case`** | dois ecrãs de detalhe. `mcase` lê o motor (43 casos); `case` lê a fixture `D.CASES` (29, `DEMO_SCENARIO`) |
| **sinal: `futureSignals` ↔ `SEGNALI GREZZI` ↔ `futureScenarios`** | 3 canónicos · 8 do radar · 56 de demonstração — três populações, uma palavra |
| **pessoas: Ciência ↔ Fontes** | `researchers` 60 alimenta o ecrã Ciência **e** o directório de pessoas do ecrã Fontes (`people` 66, derivado de researchers + publicPeople) |

### 2 · Nomes diferentes para a mesma função — aliases dentro do próprio modelo

Oito colecções são a mesma colecção sob dois nomes. Medido campo a campo (mesma
contagem, mesma `source`):

| alias | canónica | n |
|---|---|---|
| `windows` | `cropWindows` | 29 |
| `voices` | `publicVoices` | 79 |
| `channels` | `publicChannels` | 62 |
| `regulatory` | `productsRegulatory` | 163 |
| `commercial` | `productsCommercial` | 51 |
| `events` | `futureEvents` | 2 |
| `upstreamOpportunities` | `opportunities` | 43 |
| `regulatoryLinks` | `productRelationships` | 2030 |

### 3 · Archives duplicados

**Três** itens de menu com a palavra «Archivio/Archive», sem relação entre si:

| item | n | o que é realmente |
|---|---|---|
| Archivio segnali V21 | 3 | sinais de antecipação — **não é um arquivo** |
| Archivio | 1114 | índice derivado sobre todas as colecções |
| Archivio fonti V21 | 189 | registo de fontes — camada de proveniência |

E um quarto acervo sem entrada de menu: **`searchIndex`, 1655 entradas em 17
famílias** — que já indexa tudo o que os três dizem arquivar.

### 4 · Ferramentas criadas porque existe um dataset

| item | prova |
|---|---|
| **Voci dal Campo** | última ficha escrita: `CONCEPT — sem fonte de dado`. Chegaram 79 vozes ao pacote; a aba apareceu; a ficha nunca foi reaberta |
| **Archivio** (1114) | não existe ficha nenhuma. O número é um índice derivado — existe porque se podia contar |
| **Archivio fonti V21** (189) | a home proíbe «contador de fontes» pelo nome; está na barra |
| **Concorrenza** (577) | o contrato proíbe «número único saindo daqui»; 577 é esse número |

### 5 · Menu legado ainda visível

Nenhum item da barra é legado. O legado está **atrás** dela:

| superfície legada | estado medido |
|---|---|
| vista `case` | **renderiza** (`isCase = true`), lê `D.CASES` = 29 casos `DEMO_SCENARIO` |
| vista `brief` | renderiza; é onde vivem `[data-brief-dept]` e o **único** `[data-download-pdf]` |
| ponte para as duas | **`legacyCaseId` é null em 43 de 43 casos do motor** — nenhuma oportunidade real lá chega |
| ids de vista `radar`, `mradar` | continuam aceites e desenham a superfície da reunião (aliases) |

### 6 · Capacidades sem contrato

`APPROVED_CAPABILITY = UNKNOWN` — **5**: Archivio segnali V21 · Finestre Colturali ·
Portafoglio · Archivio · Rete Commerciale di Campo.
`APPROVED_CAPABILITY = NO` — **4**: Polso di Mercato · Voci dal Campo · Concorrenza ·
Intelligence Scientifica · *(e Archivio fonti V21)* = **5**.

### 7 · Itens que deveriam ser vista/filtro e não ferramenta

| item | leitura medida |
|---|---|
| Archivio segnali V21 (3) | 3 registos numa aba de primeiro nível, ao lado de uma de 1114 |
| Archivio (1114) | índice — é o que a pesquisa já faz, com 1655 entradas |
| Archivio fonti V21 (189) | proveniência: pertence a cada facto, não a uma aba |
| OPPORTUNITÀ ATTUALI (13) | é a home, não um item ao lado do radar |

### 8 · Itens que deveriam viver dentro de outra capacidade

| item | dentro de quê, e porquê |
|---|---|
| Finestre Colturali | `SEASONAL TIMING` é **INPUT declarado de MT2** |
| Portafoglio | `ADAMA REGISTERED RESPONSE` é INPUT de MT2 e o objecto de MT1 |
| Concorrenza | `COMPETITOR REGISTERED RESPONSE` é INPUT de MT2; camada da convergência |
| Intelligence Scientifica | motor de suporte |
| Polso di Mercato | motor de suporte (`market/crop context`) |
| Archivio fonti V21 | motor de suporte (evidência e proveniência) |

---

## PLACAR

```
CURRENT_MENU_ITEMS = 12    (11 na barra + 1 em INTEGRAZIONI · DEMO)
                           + 2 entradas de filtro dentro do radar, que nao contam
                             como item de menu

APPROVED           = 2     OPPORTUNITÀ ATTUALI (HOME) · Radar delle Opportunità (MT2)

UNAPPROVED         = 10    dos quais
                     NO      = 5   Polso di Mercato · Voci dal Campo · Concorrenza ·
                                   Intelligence Scientifica · Archivio fonti V21
                     UNKNOWN = 5   Archivio segnali V21 · Finestre Colturali ·
                                   Portafoglio · Archivio · Rete Commerciale di Campo

DUPLICATES         = 4 duplicacoes de capacidade
                   + 8 aliases de coleccao dentro do modelo
                   + 3 itens de menu chamados «Archivio»

LEGACY             = 0 na barra
                   + 4 superficies legadas atras dela (case, brief, radar, mradar),
                     com a ponte legacyCaseId null em 43/43

UNKNOWN            = 5 itens sem qualquer definicao
                   + 1 pergunta em aberto: se casa.html responde as cinco classes
                     que a porta unica manda a home responder — NAO MEDIDO
```

### As duas frases que o placar quer dizer

**Das doze entradas de navegação, duas têm autoridade escrita.** As outras dez
existem porque havia dado, não porque houve decisão.

**A porta única proíbe, com estas palavras, «desenhar um menu de módulos
independentes».** A barra tem onze módulos independentes.

---

## O QUE ESTE INVENTÁRIO NÃO FEZ

Não redesenhou, não renomeou, não apagou, não reorganizou, não acrescentou
ferramenta, não alterou dado nem inteligência, não promoveu produção.

Não mediu: se `casa.html` responde às cinco classes da home aprovada; se os 79
registos de `publicVoices` sustentam ou não uma capacidade nova (isso exige
abrir uma ficha de capacidade, que é decisão, não medição); nem se as vistas
legadas `case`/`brief` devem ser escondidas ou religadas.

---

## ADENDA · O QUE MUDOU DEPOIS DESTA MEDIÇÃO

Este inventário foi medido em `e4f3e8b`. A missão seguinte — **demo no ar hoje** —
agiu sobre ele. Fica registado aqui para o ficheiro não passar a mentir.

| medido acima | estado em `4413b07` |
|---|---|
| 12 itens de navegação, 11 ao mesmo nível | **dois grupos**: `STRUMENTI` (Radar, Portafoglio) e `EVIDENZA E CONTESTO` (as outras oito) |
| item 0 «OPPORTUNITÀ ATTUALI» duplicava o contador do item 1 | **saiu da barra** — `casa.html` é agora a primeira página |
| entrada = `portale.html` | entrada = **`casa.html`**, com seis portas nomeadas para `portale.html#vista` |
| «Archivio segnali V21» · «Archivio fonti V21» | «Archivio segnali» · «Registro delle fonti» |

**Nada foi apagado.** As dez destinações continuam todas a um clique; mudou o
nível, não o acesso. As dez fichas acima continuam válidas quanto a
`CAPABILITY_ID`, `SOURCE_OF_DEFINITION`, `DATA_INPUT` e `APPROVED_CAPABILITY` —
a demoção para o segundo grupo **não** converte um `UNKNOWN` em `YES`.

### O ganho, medido nos bytes publicados

| | página de entrada | blocos de `ITALY_CASA` que lê |
|---|---|---|
| **antes** (apex, `cfbd8a4`) | `portale.html` | **2 de 15** |
| **depois** (antevisão, `4413b07`) | `casa.html` | **12 de 15** |

Os dez blocos que passaram a ser lidos na entrada: `RADAR_FUTURO` (44 ITFC),
`SINAIS_DE_CAMPO`, `SENSORES`, `COBERTURA`, `FONTES`, `EVIDENCIA`,
`AUTORIZACOES`, `REVOGADO_X_SCADUTO`, `DESTAQUE`, `DO_NOT_SHOW`.

### O que continua sem poder ser mostrado

Os 44 ITFC **não podem virar 44 cartões**: `RENDERIZAVEIS` em
`italia-portale/client/upstream/IT-FUTURO-HANDOFF-LINHA-B-V1.json` são apenas
identificadores, e o conteúdo do cartão — cultura, alvo, região, evidência,
janela — não existe neste repositório. O agregado que a casa mostra (23 preparar
· 21 monitorar · 0 agir agora) é o máximo que o dado sustenta. LEI ZERO.
