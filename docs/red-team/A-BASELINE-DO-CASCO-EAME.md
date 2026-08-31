# A · BASELINE DO CASCO + B · INVENTÁRIO DAS SUPERFÍCIES ATUAIS

**Data:** 2026-08-30 · **Branch:** `claude/sintonia-eame-portal-baseline`

```
CASCO_V7                = CANONICAL_PILOT_SHELL
CANONICAL_STATUS        = FROZEN_PILOT_SHELL   (congelado DURANTE a análise — ver 0.3)
ORIGINAL_FILENAME       = index (7).html
CANONICAL_FILE          = casco/canonical/SINTONIA-EAME-PILOT-V7.html
BYTE_SIZE               = 1.397.724
SHA256                  = a31ea1848a99e48cbfcdd2574a284eaeba9017110fb6ea107c6e4f39d4187c6a
CAPTURED_AT             = 2026-08-30
CASCO_SHA_MATCH         = YES  (original, cópia em disco e blob do Git — os três batem)
```

> **Esta rodada não altera o casco.** O casco é **entrada canônica congelada**, não hipótese
> e não tela temporária. O que segue é leitura dele — extraída do próprio arquivo, não de
> documento que o descreve.
>
> **Congelado não é imutável.** O congelamento serve à análise, não à eternidade — ver 0.3.

Evidência preservada: `casco/canonical/` (a testemunha byte-a-byte + o registro de custódia)
e `data/samples/CASCO-EAME/` — `CASCO-BASELINE-V7.json` (inventário), `app-logic.jsx`
(a camada de dados do casco, 21.592 bytes) e `screens/*.txt` (o texto visível de cada uma
das doze telas).

---

## 0 · CANONICIDADE — qual artefato manda, e sobre o quê

**Existem três artefatos que alguém pode confundir com "o portal", e só um é o casco.**

| artefato | o que é | autoridade |
|---|---|---|
| **`casco/canonical/SINTONIA-EAME-PILOT-V7.html`** | **o casco do piloto** — app React, 12 superfícies, três países mais camada EAME, cinco idiomas | **`CANONICAL_PILOT_SHELL`** — manda sobre a interface |
| `prototype/portal/index.html` (38 KB) | protótipo das MISSÕES 02–03 (Home · ADAMA radar · Pest & Disease · Crops & Climate · Regulatory · Country pulse · Opportunities · Evidence) | **CONGELADO** desde 2026-08-28 por D-007. O próprio `CONGELADO.md` diz: *"não é base de decisão"* |
| `build/sintonia-es.html` (49 KB) | três casos espanhóis gerados do freeze | histórico |

**Custódia resolvida nesta passagem.** O casco vivia apenas na entrega do cliente, e quem o
procurasse no Git encontrava o protótipo congelado — artefato diferente, navegação diferente,
conclusão errada. Agora ele está versionado, byte a byte, com prova de que o Git não o
alterou (ver `casco/canonical/CASCO-CANONICO.json`).

### 0.1 · O documento antigo de arquitetura — como lê-lo

`docs/piloto/ARQUITETURA-DE-PRODUTO-ATUAL.md` (2026-08-29) descreve o produto como
*"duas ferramentas e uma pergunta"* (MT1 · MT2 · MT3 + Ask) e proíbe *"desenhar um menu de
módulos independentes"*.

**Esse documento não tem autoridade sobre a interface.** Ele é:

```
PRODUCT_ARCHITECTURE_HYPOTHESIS  /  HISTORICAL_PRODUCT_CONTRACT
```

e **não** `UI_CANONICAL_AUTHORITY`. Continua valioso — e muito — pelo que realmente contém:
as leis de saída (`FACT / INTERPRETATION / ACTION`), os limites do que não se pode afirmar,
os estados de prova e os contratos de dado. **Isso permanece inteiro.** O que ele não decide
é quantas superfícies o portal tem.

**Não há disputa a resolver, e o red team não recebe licença para jogar fora o casco.**
A pergunta correta, que vai para `U`, é outra:

> **Dentro do casco que já existe, quais superfícies realmente entregam as capacidades
> centrais do produto, quais podem ser simplificadas, e quais merecem evolução?**

E há uma boa notícia estrutural: **MT1, MT2 e MT3 não sumiram no casco.** Estão vivas como
os três modelos de leitura de `Análises` (ver A.11), com MT3 corretamente rotulada
exploratória. A hipótese antiga e o casco atual **se encaixam**; não se contradizem.

---

## 0.2 · TAXONOMIA — sete coisas que não são a mesma coisa

Correção de vocabulário aplicada a toda a PASSAGEM 1. **Contar itens de menu e chamar o
total de "ferramentas" é o erro que embaralha o red team.**

| termo | definição operacional | exemplo neste casco |
|---|---|---|
| **NAVIGATION_ITEM** | uma entrada clicável no rail ou na barra | `Radar do Futuro` · `Acervo` · seletor de país |
| **SURFACE / SCREEN** | uma região de tela com markup próprio | 12 — inclui `caso` e `eame`, que **não** estão no rail |
| **TOOL** | um instrumento que responde uma pergunta de decisão, e que **pode aparecer em mais de uma superfície** | MT1 aparece em `Análises` (como modelo) **e** em `Radar/Casos` (como classe `REGULATORY DEADLINE`) |
| **CAPABILITY** | algo que o acervo permite saber — **pode não merecer superfície própria** | "quem trabalha repetidamente neste problema" |
| **VIEW** | um recorte de uma ferramenta | `EAME` · `ES` · `IT` · `FR` são views do mesmo motor |
| **DATASET** | o artefato de dado por baixo | `ES-T4-005` (ROPF) · `SPEAKER-UNIVERSE-PILOT-V1` |
| **QUESTION** | a pergunta de decisão que justifica tudo acima | *"ainda há tempo para agir?"* |

**Contagem correta do casco V7:**

```
NAVIGATION_ITEMS ....... 10 no rail  +  4 na barra superior (país, pergunta, idioma, perfil)
SURFACES ............... 12
TOOLS .................. a definir — não é 1:1 com superfície, e a PASSAGEM 2 é que decide
CAPABILITIES ........... inventariadas em I e J, não contadas aqui
```

Uma superfície pode conter várias capacidades (`caso` contém pelo menos cinco). Uma
ferramenta pode aparecer em mais de uma superfície (MT1). Uma capacidade pode não precisar
de superfície nenhuma (crosswalk de identidade). **Onde a PASSAGEM 1 escreveu "ferramenta"
para se referir a um item de navegação, leia-se `SURFACE`.**

---

## 0.3 · POLÍTICA DE VERSÃO — V7 é baseline, não é jaula

**`CASCO PRONTO` significa: não começar do zero.** Não significa *"nada pode melhorar"*.

O V7 entrega cinco coisas que não se refazem: `VISUAL IDENTITY` · `NAVIGATION BASE` ·
`INTERACTION LANGUAGE` · `INFORMATION ARCHITECTURE BASE` · `COMPONENT BASE`.
**Tudo isso pode evoluir quando a inteligência justificar.**

```
V7  =  BASELINE PRESERVADA   — byte a byte, para sempre, nunca destruída
V8  =  PRODUTO EVOLUÍDO      — construído SOBRE o V7, em versão nova
```

O congelamento de hoje existe para quatro coisas, e só para elas:
preservar uma baseline · medir o produto real · não mexer na interface antes de entender a
inteligência · permitir comparação antes/depois.

### Quando a evolução é autorizada

```
RODADA DE INTELIGÊNCIA → REFRESH FINAL → RED TEAM EXTERNO → ARBITRAGEM
                                                                 ↓
                                                    PRODUCT IMPLEMENTATION MODE
```

**Só depois desse comando.** A partir dele fica autorizado alterar, ampliar, combinar e
dividir ferramentas; criar capacidades e ferramentas novas; mudar texto, semântica, cards,
hierarquia de informação, fluxos e navegação; acrescentar views, filtros, cruzamentos,
Action Map, Time/Window, Meta Competition, Creator/Activation, contexto de especialista e
timelines de concorrente; melhorar Radar do Futuro, Radar/Casos, Acervo, Fontes e Análises;
e **demover ou eliminar superfícies que se provarem redundantes**.

**Hoje, nada disso.** `PRODUCT_IMPLEMENTATION_MODE = NOT_ENTERED`.

### O que qualifica uma mudança no V8

**Nenhuma alteração nasce de gosto.** Cada mudança futura precisa apontar para uma destas
quatro origens:

```
INTELLIGENCE FINDING  ·  USER / DEPARTMENT NEED  ·  NEW PROVED CAPABILITY
·  RED TEAM FINDING + ARBITRATION APPROVAL
```

E registrar oito campos — este é o contrato de mudança do V8:

```
CURRENT_STATE  ·  PROBLEM  ·  EVIDENCE  ·  PROPOSED_CHANGE
WHO_BENEFITS   ·  DECISION_HELPED  ·  DAILY_VALUE  ·  ESSENCE_ALIGNMENT
```

### O limite que nenhuma versão pode cruzar

Qualquer V8 continua tendo de responder:

> **O SINTONIA não resolve falta de informação. Resolve excesso de informação
> desconectada.**

E a experiência tem de continuar levando de:

```
MUITAS OBSERVAÇÕES → CONVERGÊNCIAS → POUCOS ASSUNTOS QUE MERECEM ATENÇÃO
→ EVIDÊNCIA → CONTEXTO LOCAL → TEMPO → QUEM DEVERIA OLHAR → POSSÍVEL DECISÃO
```

**`ESSENCE_RISK` — o que o V8 não pode virar:** dashboard regulatório · biblioteca de
documentos · feed de notícias · ranking de pessoas · painel de anúncios · coleção de KPIs.

---

# A · CASCO BASELINE

## A.1 · O que o casco é, tecnicamente

Página React empacotada (runtime próprio `dc-runtime` + React 18.3.1 UMD embutido).
17 ativos internos: 10 fontes (LL Brown e Aleo), 2 imagens, os scripts de runtime e um SVG.
A lógica de aplicação são **21.592 bytes** (`app-logic.jsx`); o markup são **257 KB**.

Não há `package.json`, build de projeto, servidor, banco nem chamada de rede no repositório.
**O casco é um arquivo só, que abre com dois cliques.**

## A.2 · CURRENT_NAVIGATION

Rail lateral fixo, em três blocos rotulados, mais barra superior.

```
INTEL       Visão Geral · Radar do Futuro · Radar / Casos · Janelas da Cultura
EVIDÊNCIA   Acervo · Fontes
LEITURA     Análises · Relatórios
(sem rótulo) Sistema · Config.
```

Duas telas **não** aparecem no rail e existem:

- **`caso`** — o detalhe de um caso, alcançado a partir de `Radar / Casos`;
- **`eame`** — a camada cross-market, alcançada pelo seletor de país.

**Total: 12 telas com markup real.** Nenhuma é fachada: cada uma tem entre 5 KB e 49 KB de
estrutura própria.

**Barra superior:** marca `Sintonia / EAME INTELLIGENCE` · seletor de país
(`COUNTRY PORTAL`: ES · IT · FR — e `CAMADA CROSS-MARKET`: EAME) · campo
*"Perguntar ao Sintonia — temas, moléculas, fontes, casos"* · seletor de idioma
(PT · EN · ES · IT · FR) · Perfil.

**A lei de país está escrita na própria interface**, dentro do seletor:

> *Dados de um país nunca aparecem dentro de outro. Cruzamentos só na camada EAME, e apenas
> nas dimensões declaradas comparáveis.*

## A.3 · O dicionário de estados — a peça mais forte do casco

Quinze estados, com cor e traço próprios, e nenhum deles é score:

```
PROVADO · PARCIAL · MEDIDO · EM COLETA · EM CONSTRUÇÃO
NÃO CONECTADO · NÃO MEDIDO · NÃO INICIADA · CONGELADO
NÃO SEI · NÃO SE APLICA · NÃO DETERMINADO
AINDA NÃO COMPARÁVEL · COMPARÁVEL · BLOQUEADO
```

Estados negativos usam **borda tracejada**; positivos, borda sólida. A ausência tem forma
visual própria. Isto realiza, em interface, a regra que o repositório paga caro desde a
MISSÃO 01: `SOURCE FAILURE ≠ ZERO`, `NOT COLLECTED ≠ DOES NOT EXIST`.

## A.4 · A gramática — seis perguntas, e elas mandam na home

```
1 O que merece atenção          4 Quem deve olhar?
2 Ainda há tempo para agir?     5 Qual evidência sustenta?
3 Por que está no radar?        6 O que ainda não sabemos?
```

E a gramática regional, na camada EAME:

```
1 Onde existe questão regional?   4 Onde o portfólio local difere?
2 Onde os mercados divergem?      5 O que investigar regionalmente?
3 Qual a sequência de janelas?    6 Onde falta cobertura?
```

## A.5 · CURRENT_ACTION_MAP

**Oito áreas no portal do país**, com Market Development marcada `ÁREA CENTRAL`:

| área | papel escrito no casco |
|---|---|
| **Market Development** | avalia e programa a investigação |
| Regulatório | verifica condições e rótulo |
| Portfólio | confirma resposta registrada |
| Técnico / Agronomia | valida no campo |
| Marketing | prepara comunicação |
| Comercial | prepara equipe e território |
| Ciência & P&D | investiga a hipótese |
| Supply | planeja disponibilidade |

Estado de todas hoje: **NÃO DETERMINADO**. Cada uma tem quatro campos preparados —
*por que esta área · ação possível · janela de ação · evidência exigida*.

**Sete áreas na camada EAME**, com `Market Development regional` central, e saída em cinco
estados: `COORDENAR` · `PREPARAR` · `OBSERVAR` · `SOMENTE LOCAL` · `NÃO SEI`.

**Nota de conformidade:** o briefing desta missão pede SUPPLY *"somente quando houver
evidência que torne a área relevante"*. O casco já lista Supply sempre, com estado
`NÃO DETERMINADO`. Como estado, é honesto; como lista fixa, convida ao preenchimento.

## A.6 · CURRENT_RADAR_STRUCTURE (`Radar do Futuro`)

Três degraus declarados — **Sinais → Temas → Casos de convergência** — e seis contadores,
todos em `—`: temas em watchlist · sinais científicos · sinais de especialistas ·
observações de campo · temas evoluindo · horizontes mapeados.

Quatro painéis de sinal emergente, um por linha ADAMA (Disease · Weed · Pest · Crop
Enhancement), cada um com *"Série de sinal — sem dado conectado"*.
**A cor é a linha do assunto, nunca decoração** — escrito na tela.

Horizonte de oportunidades em quatro faixas: `Agir agora 0–30d` · `Preparar 30–90d` ·
`Planejar 90–180d` · `Próximo ciclo >180d`.

Contrato do item de radar — **14 campos**, sem score numérico:

```
country · crop · issue/theme · region · why_on_radar · first_observed · last_observed ·
source_date · current_evidence · missing_evidence · agronomic_window · decision_window ·
who_should_look · next_checkpoint
```

Cinco estados: `EARLY SIGNAL` · `CONVERGENCE FORMING` · `DECISION POTENTIALLY OPEN` ·
`FUTURE PLANNING` · `NÃO SEI`.

E há um bloco **"Palavra dos pesquisadores"** com a ressalva certa já escrita:
*"Recorrência não é autoridade. Pessoas identificadas exigem tratamento GDPR antes de
qualquer exposição."*

## A.7 · CURRENT_CASE_STRUCTURE

**Lista (`casos`):** filtros de linha ADAMA, estado e janela — que funcionam de verdade,
filtrando 8 slots. Cabeçalho honesto: *"Nenhum caso conectado nesta versão."*
Cinco classes já nomeadas: `REGULATORY DEADLINE` · `GEOGRAPHIC PRIORITY` · `INVESTIGATE` ·
`ACTIVATION QUESTION` · `CHANGE DETECTED`.

**Detalhe (`caso`):** seis abas — `síntese` · `evidências` · `convergência` ·
`cruzamentos` · `áreas` · `histórico`.

Dentro da síntese, quatro blocos que são o coração do produto:

1. **Camadas de evidência** — sete: Campo · Ciência · Clima · Regulatório ·
   Portfólio local ADAMA · Competição · Tempo. Rótulo explícito: *"estado de evidência —
   não é score"*.
2. **Camadas que não se fundem** — Resposta local registrada · Janela agronômica ·
   Janela de decisão · Disponibilidade comercial · Prioridade interna.
3. **Resposta local ADAMA**, com contrato de 8 campos e a lei escrita:
   *"Produto global nunca vira resposta local."*
4. **FATO / INTERPRETAÇÃO / AÇÃO POSSÍVEL**, em campos separados.

A aba `convergência` implementa a régua de seis passos do Market Development
(`SINAL APARECE → É REAL? → ONDE MAIS? → O QUE SUSTENTA? → RESPOSTA ADAMA REGISTRADA →
O QUE VALIDAR`) e trata **competição como camada do caso, não como aba própria** — decisão
já tomada em `ARQUITETURA-DE-PRODUTO-ATUAL.md` e corretamente refletida.

Dentro do caso há ainda o **calendário de quatro relógios** (ciclo da cultura · janela do
issue · janela registrada · idade da evidência) com a leitura escrita:
*"janela aberta nunca confirma necessidade"*.

## A.8 · `Janelas da Cultura` — a ferramenta que o repositório ainda não tinha

Tela inteira dedicada a tempo, com o que nenhum documento canônico do repo havia formalizado:
**resolução temporal declarada**.

```
DATA EXATA · SEMANA · MÊS · FASE FENOLÓGICA · ESTAÇÃO/APROXIMADO · NÃO CONHECIDA (sem barra)
```

> *"A interface nunca desenha precisão que o dado não tem. Se sabemos 'primavera', a barra
> é uma estação — não duas datas."*

E a semântica de ação em quatro combinações: janela registrada aberta + campo não confirmado
→ `VERIFICAR AGORA`; janela se encerrando + evidência sustentada → `AGIR AGORA`;
janela encerrada + próximo ciclo mapeado → `PREPARAR`; janela não conhecida → `NÃO SEI`.

Contrato de entrada de 16 campos, nenhum preenchido.

## A.9 · CURRENT_ACERVO_STRUCTURE

Filtros (cultura · linha ADAMA · período · proveniência), busca, cinco abas
(todos · regulatório · ciência · campo · mercado), tabela e paginação.
Contrato de 13 colunas, com `sha_verified` e `evidence_level` entre elas.
Ações por linha: **Abrir original** · **Ver proveniência**.

## A.10 · CURRENT_SOURCE_STRUCTURE

Quatro abas por estado de acesso: `todas` · `operando` · `com ressalva` · `bloqueadas`.
E um quinto estado, fora das abas e correto: **`NÃO COLETADA AINDA`** —
*"Fonte identificada, rota não testada. Estado próprio: existe, é conhecida, e ainda não
entrou na coleta."*

Contrato de 11 campos + quatro blocos de contrato semântico: `GATILHO` ·
`EVIDÊNCIA MÍNIMA` · `REGRA DE CONFIANÇA` · `O QUE NÃO PODE DIZER`.

## A.11 · CURRENT_ANALYSIS_STRUCTURE

Três modelos de leitura, e eles são **exatamente** as três ferramentas canônicas:

| modelo no casco | ferramenta canônica | estado no casco |
|---|---|---|
| Revisão regulatória | MT1 · REGULATORY & EXPIRY EXPOSURE | ESTRUTURA PRONTA |
| Prioridade geográfica | MT2 · GEOGRAPHIC COMMERCIAL PRIORITY | ESTRUTURA PRONTA |
| Pergunta de ativação | MT3 · PUBLIC ACTIVATION GAP | **EXPLORATÓRIA** |

**Esta é a ponte entre o casco e a hipótese de arquitetura de 2026-08-29** — e ela já existe.
MT1/MT2/MT3 são `TOOL` na taxonomia de 0.2, e aparecem em **duas** superfícies: como
*modelos de leitura* em `Análises` e como *classes de item* em `Radar/Casos`. É o exemplo
mais claro de que **ferramenta ≠ tela**.

## A.12 · CURRENT_REPORT_STRUCTURE

Três abas: `snapshots` · `freezes` · `dossiês`. Snapshot congela o estado do portal numa
data com fontes e versões; freeze é base imutável para apresentação; dossiê agrega casos
com evidência, limite e mapa de ação. Histórico: *"Nenhuma exportação registrada."*

## A.13 · CURRENT_ASK_SINTONIA

Existe como **campo de busca na barra superior**, não como tela. É a leitura correta:
`ARQUITETURA-DE-PRODUTO-ATUAL.md` diz que Ask *"não é uma quarta ferramenta"*.
**Não há tela de resposta no casco** — o contrato de resposta
(`FACTS · CONNECTIONS · UNKNOWN · WHY IT MAY MATTER · EVIDENCE`) não tem superfície.

## A.14 · CURRENT_EXPERT / CREATOR / PEOPLE AREAS

**Não existe tela de especialistas.** Existe **um bloco** — *"Palavra dos pesquisadores"*,
dentro do `Radar do Futuro`, com filtros DISEASE/WEED/PEST e um botão
*"Abrir ranking de recorrência"*.

⚠️ **`Abrir ranking de recorrência` — `SEMANTIC_UX_RISK`, não contradição provada.**

**O que foi medido no markup:** o elemento é um `<div>` **sem manipulador de clique**
(`sc-camel-on-click` ausente), **sem destino** e **sem tela de chegada**. As três linhas
acima dele (DISEASE · WEED · PEST) são barras vazias — sem nome, sem contagem, sem ordem.
**Não existe ranking implementado.**

Ordenar por **recorrência** significa, em si, apenas *ordenar por frequência observada* — e
isso é legítimo. O risco só se realiza se a interface converter recorrência em
**autoridade · qualidade · importância · verdade · influência**.

Como o destino não existe, **não há o que medir ainda**. Fica registrado como risco de
rótulo, a reavaliar quando a superfície de chegada existir. A lei permanece intacta e vale
para quem construir esse destino:

```
RECURRENCE ≠ AUTHORITY        FOLLOWERS ≠ AUTHORITY        ENGAGEMENT ≠ INFLUENCE
```

**Não existe nenhuma área de creators.** Zero telas, zero blocos, zero campos.

## A.15 · A CAMADA EAME

A tela mais elaborada depois do detalhe de caso (29,9 KB). Nove blocos:
overview por mercado · convergências cross-market · onde os mercados diferem ·
sequência de janelas locais · assimetria de portfólio · Radar EAME (sete tipos A–G) ·
mapa de coordenação regional · **matriz de comparabilidade** · caso cross-market
(dez partes) · cadeia de origem `EAME → país → caso → evidência → fonte`.

Leis escritas na própria tela:

> *A EAME não é a soma dos países.*
> *mesmo termo ≠ mesmo problema ≠ mesma decisão*
> *SEQUÊNCIA OBSERVADA ≠ PROPAGAÇÃO*
> *Números não se comparam só porque existem.*

## A.16 · A MEDIDA QUE IMPORTA — e como enunciá-la corretamente

```
SURFACES WITH STRUCTURE ............................. 12 / 12
SURFACES CURRENTLY WIRED TO CANONICAL REAL DATA .....  0 / 12
BUSINESS VALUES BOUND ...............................  0
CASES CONNECTED .....................................  0   (8 slots estruturais)
INPUT CONTRACTS DECLARED ............................  9   (radar, acervo, fonte,
                                                            calendário curto e longo,
                                                            resposta ADAMA, EAME radar,
                                                            ação regional, camadas de caso)
```

⚠️ **`0/12` mede ligação, não existência de inteligência.** A leitura correta é
**`DELIVERY / INTEGRATION GAP`**, e nada além disso.

O SINTONIA **tem** inteligência hoje — ela só vive **fora do casco**: 23 safras de campo
andaluz, 1.771 documentos científicos, três registros nacionais, 13 pessoas com ORCID
resolvido, 18 fichas de creator, 6 casos escritos. Dizer *"o portal não tem dado"* e deixar
o leitor concluir *"o projeto não tem inteligência"* seria inverter o diagnóstico e mandar
a próxima rodada coletar o que já está coletado.

**O casco está completo como contrato e desligado como entrega.** Para esta rodada, isso é a
melhor notícia possível: não há nada a desfazer — há o que ligar.

---

# B · INVENTÁRIO DAS SUPERFÍCIES ATUAIS

> **Leia com a taxonomia de 0.2.** O que segue são **superfícies e itens de navegação**,
> não uma contagem de ferramentas. Quantas *ferramentas* o casco realmente tem é decisão da
> PASSAGEM 2 — e a resposta **não** será 15.

Para cada superfície: o que é · que pergunta tenta responder · que dado espera · estado.

### 1 · VISÃO GERAL (`home`) — `ESTRUTURA COMPLETA / SEM DADO`
- **É:** a fila do país. Gramática de seis perguntas, estado da fundação em seis camadas,
  janela de decisão em cinco faixas, atalhos para as seis ferramentas, estado da coleta,
  áreas ADAMA impactadas, porta da camada EAME.
- **Pergunta:** *o que merece atenção agora?*
- **Espera:** itens classificados nas cinco classes + estado por camada de fundação +
  contadores de coleta (última coleta, portões, freeze, change events).
- **Estado:** todos os contadores em `—`; `Portões de coleta: aguardando`.

### 2 · RADAR DO FUTURO (`futuro`) — `ESTRUTURA COMPLETA / SEM DADO`
- **É:** inteligência antecipatória antes de virar caso. Sinais → Temas → Casos.
- **Pergunta:** *onde a evidência está se acumulando?*
- **Espera:** o contrato de 14 campos, séries de sinal por linha ADAMA, watchlist científica
  com SOURCE_ID e licença por linha, temas em formação com `EVIDÊNCIAS QUE FALTAM`.
- **Estado:** seis contadores em `—`; quatro séries *"sem dado conectado"*.

### 3 · RADAR / CASOS (`casos`) — `ESTRUTURA COMPLETA / 8 SLOTS`
- **É:** a lista de casos de convergência, com filtros funcionais.
- **Pergunta:** *que casos existem, e até onde cada um pode ir?*
- **Espera:** casos com país, cultura, issue, linha, estado, janela.
- **Estado:** 8 slots, todos Espanha, todos rotulados slot.

### 4 · CASO (`caso`) — `A FERRAMENTA MAIS COMPLETA DO CASCO`
- **É:** seis abas cobrindo evidência, convergência, cruzamentos, áreas e histórico.
- **Pergunta:** *o que sustenta este caso, o que falta, e quem deve olhar?*
- **Espera:** 7 camadas de evidência + 5 camadas que não se fundem + 4 camadas de competição
  + resposta ADAMA local (8 campos) + 4 relógios + fato/interpretação/ação + fontes.
- **Estado:** 6 camadas `NÃO MEDIDO`, Tempo `NÃO CONECTADO`, competição toda `NÃO SEI`.

### 5 · JANELAS DA CULTURA (`calendario`) — `ESTRUTURA COMPLETA / RELÓGIOS NÃO CONECTADOS`
- **É:** calendário agronômico por país × cultura × região, com zoom ano/trimestre/mês.
- **Pergunta:** *a cultura, o problema ou o produto ainda permitem ação?*
- **Espera:** 16 campos, incluindo `time_resolution` e `evidence_freshness`.
- **Estado:** quatro slots de região ilustrando quatro estados; nenhum calendário real.

### 6 · ACERVO (`acervo`) — `ESTRUTURA COMPLETA / SEM DADO`
- **É:** o bruto coletado, com proveniência. *"A leitura vive em Análises."*
- **Pergunta:** *o que já foi coletado sobre isto, e de onde veio?*
- **Espera:** 13 colunas por registro.
- **Estado:** 4 linhas `ID —`.

### 7 · FONTES (`fontes`) — `ESTRUTURA COMPLETA / SEM DADO`
- **É:** ficha de fonte por estado de acesso, com contrato semântico.
- **Pergunta:** *de onde nasce a evidência, e a rota está viva?*
- **Espera:** 11 campos + gatilho + evidência mínima + regra de confiança + limite.
- **Estado:** um slot por estado.

### 8 · ANÁLISES (`analises`) — `ESTRUTURA MÍNIMA / SEM DADO`
- **É:** três modelos de leitura (= MT1, MT2, MT3) + leitor `FATO/INTERPRETAÇÃO/AÇÃO`.
- **Pergunta:** *o que este conjunto de evidências permite afirmar, e até onde?*
- **Espera:** uma leitura estruturada por modelo.
- **Estado:** a tela mais rasa do casco (5,4 KB) para a camada onde vive o valor.

### 9 · RELATÓRIOS (`relatorios`) — `ESTRUTURA COMPLETA / SEM DADO`
- **É:** snapshot, freeze e dossiê exportáveis.
- **Pergunta:** *o que eu levo para a reunião, e com que rastro?*
- **Espera:** data de versão, escopo, casos incluídos, formato.
- **Estado:** *"Nenhuma exportação registrada."*

### 10 · SISTEMA (`lib`) — `COMPLETA E FUNCIONAL`
- **É:** biblioteca visual — cor, tipografia, botões, chips, estados, marca.
- **Estado:** **a única ferramenta do casco que está pronta e correta hoje**, porque o dado
  dela é a própria marca ADAMA.

### 11 · CONFIG (`config`) — `ESTRUTURA COMPLETA / SEM DADO`
- **É:** ambiente, idioma/display layer, filtros padrão, usuários e times por país e camada.

### 12 · CAMADA EAME (`eame`) — `ESTRUTURA COMPLETA / SEM DADO`
- **É:** comparação, convergência e coordenação entre mercados.
- **Pergunta:** *onde os mercados convergem, divergem e exigem atenção regional?*
- **Espera:** contrato de 6 campos por item + matriz de comparabilidade + sequência de
  janelas locais + assimetria de portfólio.
- **Estado:** *"NENHUMA CONVERGÊNCIA CONECTADA"*; toda divergência `NÃO MEDIDA`.

### 13 · ASK SINTONIA (barra superior) — `ENTRADA SEM SAÍDA`
- **É:** um campo de busca.
- **Estado:** **não há tela de resposta.** O contrato de resposta existe em
  `scripts/ask_sintonia.py` (5 perguntas executáveis, 35 de contrato) e não tem superfície.

### 14 · SELETOR DE PAÍS (barra superior) — `FUNCIONAL`
- **É:** o isolamento de país, implementado como navegação.
- **Estado:** funciona; troca país e leva a `eame` quando a camada é escolhida.
  **Os badges de IT e FR estão desatualizados** — ver A.5 / `CASCO-BASELINE-V7.json`.

### 15 · DISPLAY LAYER / IDIOMA (barra superior) — `ESTRUTURA / DICIONÁRIO VAZIO`
- **É:** cinco idiomas e a separação entre artefato técnico e rótulo legível.
- **Estado:** *"as strings da interface saem de dicionário, não do conteúdo"* — o dicionário
  não existe. O repositório tem `data/samples/DISPLAY-LAYER-V1.json`, ainda não ligado.
