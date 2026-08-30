# A · BASELINE DO CASCO + B · INVENTÁRIO DAS FERRAMENTAS ATUAIS

**Data:** 2026-08-30 · **Branch:** `claude/sintonia-eame-portal-baseline`
**Entrada congelada:** `index (7).html`, entregue pelo cliente em 2026-08-30
· 1.397.724 bytes · SHA-256 `a31ea1848a99e48cbfcdd2574a284eaeba9017110fb6ea107c6e4f39d4187c6a`

> **Esta rodada não altera o casco.** O casco é entrada congelada. O que segue é leitura
> dele — extraída do próprio arquivo, não de documento que o descreve.

Evidência preservada: `data/samples/CASCO-EAME/` — `CASCO-BASELINE-V7.json` (inventário),
`app-logic.jsx` (a camada de dados do casco, 21.592 bytes) e `screens/*.txt` (o texto
visível de cada uma das doze telas).

---

## 0 · O ACHADO QUE MUDA A LEITURA DE TUDO

**Existem dois artefatos chamados "protótipo" neste projeto, e eles não são a mesma coisa.**

| artefato | o que é | estado |
|---|---|---|
| `prototype/portal/index.html` (repo, 38 KB) | protótipo das MISSÕES 02–03: Home · ADAMA radar · Pest & Disease · Crops & Climate · Regulatory · Country pulse · Opportunities · Evidence | **CONGELADO desde 2026-08-28** por D-007. O próprio arquivo `CONGELADO.md` diz: *"não é base de decisão"* |
| `build/sintonia-es.html` (repo, 49 KB) | três casos espanhóis gerados do freeze | histórico |
| **`index (7).html` (entrega do cliente)** | **o casco atual** — app React de 12 telas, três países mais camada EAME, cinco idiomas | **é este o baseline desta rodada** |

Quem procurar o casco dentro do repositório encontra o artefato errado. **O casco atual não
está versionado em lugar nenhum do Git** — ele vive na entrega do cliente. Isto é uma lacuna
de custódia, não de produto, e está registrada em `Q · CASCO GAPS`.

**Segunda divergência, e maior:** o documento que hoje manda na arquitetura de produto,
`docs/piloto/ARQUITETURA-DE-PRODUTO-ATUAL.md` (2026-08-29), diz textualmente que o design
**não pode** *"desenhar um menu de módulos independentes"* — são *"duas ferramentas e uma
pergunta"* (MT1 · MT2 · MT3 + Ask). **O casco entregue é um menu de dez itens.**

Isso **não** é erro do casco. É uma decisão de produto tomada depois daquele documento, e o
casco é a evidência mais recente. Mas os dois não podem continuar valendo ao mesmo tempo:
ou o documento sobe para descrever o casco, ou o casco desce para as três ferramentas.
**Esta é a primeira pergunta que o red team deve atacar** — e está em `U`.

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

**Esta é a ponte entre o casco e o documento canônico** — e ela já existe. MT1/MT2/MT3 não
sumiram no casco: viraram *modelos de leitura* dentro de `Análises`, com MT3 corretamente
rotulada exploratória.

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

⚠️ **`Abrir ranking de recorrência` é o único rótulo do casco que contradiz uma lei do
repositório.** `FOLLOWERS ≠ AUTHORITY` e *"recorrência não é autoridade"* estão escritos na
mesma tela, duas linhas acima do botão. Ranking de recorrência **é** um ranking de
autoridade por outro nome. Registrado em `L · FERRAMENTAS: KEEP/IMPROVE/QUESTION`.

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

## A.16 · A MEDIDA QUE IMPORTA

```
TELAS COM ESTRUTURA .................. 12
TELAS COM DADO REAL ..................  0
VALORES DE NEGÓCIO LIGADOS ...........  0
CASOS CONECTADOS .....................  0  (8 slots estruturais)
CONTRATOS DE ENTRADA DECLARADOS ......  9  (radar, acervo, fonte, calendário curto e
                                            longo, resposta ADAMA, EAME radar, ação
                                            regional, camadas de caso)
```

**O casco está completo como contrato e vazio como produto.** Para esta rodada, isso é a
melhor notícia possível: não há nada a desfazer — há o que ligar.

---

# B · CURRENT TOOLS INVENTORY

Para cada ferramenta: o que é · que pergunta tenta responder · que dado espera · estado.

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
