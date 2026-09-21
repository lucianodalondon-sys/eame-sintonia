# MISSÃO — AQUISIÇÃO REAL: LISTING → DETALHE

**Base:** `source-curator-integration-v1` @ `907ccd70`
**Bancada:** worktree própria. **NÃO trabalhar em `main` nem na bancada do Source Curator.**

> **HARD GATE: `BIG_COLLECTION_ALLOWED = NO`.** Não rodar Big Collection nesta missão.
> Não coletar em massa. Não baixar vídeo.

---

## 0 · O QUE A COORDENAÇÃO MEDIU — confirme, não confie

Medido em `907ccd70`, worktree limpa, antes de abrir esta bancada.
**Reconfirme cada linha. Se divergir, o seu número manda e diga-o.**

```text
MOTOR          regras/motor_de_rota.mjs — declarativo, sem switch por SOURCE_ID
links[0] em coleta/ + regras/                    = 0   (JÁ RESOLVIDO na linha viva)
MAX_TARGETS respeitado pelo motor (linha 356)    = SIM
```

### 0.1 · ⚠️ O BRIEFING DO DONO ESTAVA CERTO NO SINTOMA E ERRADO NA ETAPA

O briefing dizia `PRIMARY_LOSS_STAGE = ENUMERATION`. **A medição refuta isso.**

Medido no canário real da casa, `curadoria/CANARY-LOTE-HTML-ARTIGO.json`
(27 fontes, corrido 2026-09-20T15:27:35Z):

```text
LISTING_FOUND                18
DETAIL_LINKS_DISCOVERED     185   ← o motor ENCONTRA os itens. A enumeração FUNCIONA.
DETAIL_ITEMS_SELECTED        18   ← MAX_TARGETS: 1 descarta 167
PERDA                       167   na SELEÇÃO
```

```text
PRIMARY_LOSS_STAGE = SELECTION, não ENUMERATION.
```

**O truncamento deixou de ser código e passou a ser DADO DO CONTRATO.**
Mexer no motor não resolve nada. O `1` está escrito nas fichas.

### 0.2 · O UNIVERSO É 4× MAIOR DO QUE O BRIEFING SUPÕE

Medido em `curadoria/ESTADO-ACTUAL-DAS-FONTES-V1.json` (186 contratos):

```text
HTML_LINK_DISCOVERY total                        126
  destes SUCCESS na BCR-2026-09-20               105
  destes com EXATAMENTE 1 observação             104   ← o universo real do defeito
     dos quais ROTA = homepage (capa nua)         49
     dos quais ROTA = caminho específico          55
MAX_TARGETS: 1 nos contratos do curator        27/27
MAX_TARGETS: 1 no núcleo regras/italy_contracts.mjs  5/6
```

### 0.3 · ⚠️ SEGUNDA CAUSA, NÃO PREVISTA NO BRIEFING — A ROTA APONTA PARA O SÍTIO ERRADO

25 dos 27 contratos do curator têm `INDEX_URL` na **raiz do domínio**.
Descobre-se a partir da capa institucional, escolhe-se 1, e o 1 é lixo. Medido:

```text
IT-T5-039  →  .../avvisi/bacheca-laureati/esami-di-stato1      (avisos de exames)
IT-T12-009 →  .../progetti-europei/progetti-europei-conclusi   (projetos encerrados)
```

E há pior — uma rota que aponta para **um artigo individual**, não para uma listagem:

```text
IT-T1-021 (Agronotizie/Image Line)
  ROUTE = https://agronotizie.imagelinenetwork.com/eventi-agricoltura/agora-fertilizzanti-2026/89672
```

```text
DUAS CAUSAS INDEPENDENTES:
  (A) MAX_TARGETS: 1          — seleciona 1 de N
  (B) INDEX_URL = capa        — o N já nasce errado
Corrigir só (A) faz colher 20 páginas institucionais em vez de 1.
```

### 0.4 · ⚠️ O PERIGO CENTRAL — `MAX_TARGETS: 1` ESTÁ CERTO NALGUMAS FONTES

**Não é um defeito universal. É um defeito de família.**

```text
BOLETIM SERIADO      ARPAE, APOL, Campania, Puglia, salute.gov
                     O índice lista o ARQUIVO (30 edições).
                     A edição corrente é a única que interessa.
                     MAX_TARGETS: 1 está CORRETO. NÃO TOCAR.
                     Subir o limite = recoletar anos de arquivo.

LISTAGEM DE NOTÍCIAS as 99 TABELA_ONBOARDED + Agronotizie + OlivoNews
                     O índice lista itens NOVOS, distintos, todos úteis.
                     MAX_TARGETS: 1 está ERRADO. Perde N-1.
```

**Classificar ANTES de corrigir. Correção em bloco é regressão.**

---

## 1 · ENTRADA OBRIGATÓRIA

```bash
BIBLIA-CANONICA-DA-COLETA.md        # a lei
AGENTS.md                           # lei do System Map — ela aplica-se a si
regras/LEIA-ANTES-DE-COLETAR.md     # as réguas vivas
```

Leia antes de escrever a primeira linha. Se uma régua já existir, **use-a**;
não reinvente a lei — a lei reinventada nunca é igual à que já existia.

---

## 2 · O TRABALHO

### PASSO 1 — CLASSIFICAR (read-only, sem rede, sem tocar em contrato)

Classifique as **104** fontes `HTML_LINK_DISCOVERY` com 1 observação em:

```text
BOLETIM_SERIADO        índice = arquivo de edições da mesma série
LISTAGEM_DE_NOTICIAS   índice = itens distintos e novos
NAO_SEI                não deu para decidir pela evidência disponível
```

Regras:

- classifique **pela evidência já guardada** (contrato, `LINK_PATTERN`, `IDENTITY`,
  `OUTPUT_TYPE`, `ROUTE_TYPE`, o que a BCR trouxe). Rede só no PASSO 3;
- `NAO_SEI` é resultado **válido e obrigatório** quando é o caso. Não force o balde;
- a classificação é **dado derivado e auditável**: grave-a em ficheiro, com o
  critério que decidiu cada uma. Ninguém deve ter de adivinhar porquê.

**Entregue a tabela e PARE para a coordenação ver antes do PASSO 2.**
Se a classificação parecer óbvia, ela não é: foi este passo que o briefing saltou.

### PASSO 2 — CORRIGIR SÓ A FAMÍLIA DE NOTÍCIAS

Para as classificadas `LISTAGEM_DE_NOTICIAS`, e **só** para essas:

**(A) `INDEX_URL`** — apontar para a página de listagem real, não para a capa
nem para um artigo. A rota tem de ser **provada**, não suposta.

**(B) `MAX_TARGETS`** — subir para um limite declarado, dentro da cadência canónica.
O número é **decisão sua, justificada e escrita**. Não invente um número redondo
porque parece simpático; derive-o do que a fonte publica.

**(C)** `BOLETIM_SERIADO` e `NAO_SEI` **não se tocam.** Zero diff nelas.

Restrições:

- **não criar motor novo.** `HTML_LINK_DISCOVERY` existe e funciona — foi medido;
- **não criar switch por SOURCE_ID.** O contrato despacha, não o id;
- mudança é **de contrato**, não de código, salvo se o motor provadamente não
  suportar o que o contrato precisa declarar — e aí diga-o pelo nome antes de mexer.

### PASSO 3 — CANÁRIO CONTRA A REALIDADE (rede autorizada, pequeno)

5–10 fontes sentinela, já localizadas pela coordenação:

```text
IT-T1-021   Agronotizie / Image Line   ⚠️ rota aponta para 1 ARTIGO
IT-T1-022   OlivoNews                  https://olivonews.it/category/bollettino-olivicolo/
IT-T3-010   APOL                       ⚠️ provável BOLETIM_SERIADO — trate como controlo negativo
IT-T2-001   ARPAE                      ⚠️ provável BOLETIM_SERIADO — trate como controlo negativo
IT-T3-005   Terre dell'Etruria         STATIC_ENDPOINT — sem corrida na BCR
```

Complete até 10 com fontes `LISTAGEM_DE_NOTICIAS` que você classificou.

**Controlo positivo primeiro** (lei da casa, já praticada no canário existente):
se o leitor falhar, nenhuma fonte é condenada.

**Inclua pelo menos um `BOLETIM_SERIADO` como controlo negativo:** ele tem de
continuar a trazer **1** e só 1. Se subir, a correção vazou para a família errada.

Por canário, meça e escreva:

```text
SOURCE_ID
CLASSIFICACAO
REAL_ITEMS_VISIBLE         =
DETAIL_LINKS_DISCOVERED    =
DETAIL_ITEMS_SELECTED      =
DETAIL_ITEMS_COLLECTED     =
RAW_CORRECT_PAGE           =    é a matéria, ou é a capa?
DERIVED_HAS_BODY           =
PUBLISHED_AT_PRESERVED     =
```

Contraprova exigida: se o listing de Agronotizie mostra 20+ notícias reais,
o canário **não pode** terminar na página índice.

### PASSO 4 — INCREMENTALIDADE

A Collection não pode recolher a mesma capa eternamente.

**Meça primeiro o que já existe.** `data/collection-ledger/` e o mecanismo de
`SEEN_AGAIN` da BCR já respondem parte disto — medido: a BCR classificou
observações como `SEEN_AGAIN`. **Não construa cursor novo antes de provar que
o existente não chega.**

Se faltar, implemente o **mínimo necessário** (`LAST_SEEN` / cursor equivalente).

```text
item já conhecido e byte idêntico  → não volta como conteúdo útil novo
mudança real                       → nova observação, pelas leis da Collection
NÃO QUEBRAR: RUN ≠ OBSERVATION ≠ CONTENT ≠ STORAGE OBJECT
```

Meça `WASTEFUL_REOBSERVATION` antes e depois.

### PASSO 5 — YOUTUBE: NÃO FINGIR QUE HTML É O VÍDEO

**Confirmado pela coordenação no acervo real**
(`%USERPROFILE%\sintonia-sala-italia\acervo-coletor-bcr`):

```text
612 páginas HTML de vídeo · 714,6 MB · média 1.196 KB por item
0 transcrições
derivação HTML→texto devolve «item veio sem texto nenhum» (RELATORIO-BCR §B2)
```

(O briefing do dono dizia 737 / 715 MB; medi 612 / 714,6 MB. Mesma doença,
número diferente — reconfirme e escreva o seu.)

Nesta missão:

1. **meça** a capability de áudio/transcrição que já existe
   (`coleta/executor_transcricao_midia.py`, `coleta/adaptador_youtube.py`).
   **CAN DO ≠ DID DO** — existir não é funcionar;
2. se a capability estiver provada: **um** canário isolado, um vídeo;
3. se não estiver: YouTube fica `READY` para descoberta/metadata e
   **NÃO** para tratar watch HTML como conteúdo final. Diga-o pelo nome.

**Não baixar vídeo em massa.**

### PASSO 6 — `PUBLISHED_AT`

Onde a fonte de detalhe publica a data **explicitamente**: preservar.

```text
PUBLISHED_AT ≠ FACT_TIME.   Não criar FACT_TIME. UNKNOWN continua UNKNOWN.
```

O motor já defende isto (`motor_de_rota.mjs`: *«FACT_TIME NÃO TEM FALLBACK, e
isso é deliberado»*). **Não afrouxar essa defesa** para preencher um campo.

### PASSO 7 — GATE: CAPA ≠ MATÉRIA

Gate executável: `LISTING_PAGE` não pode ser tratada como conteúdo final
quando o contrato declara itens de detalhe.

O gate precisa de um caso que o faça **falhar** — sonda sem contraprova não é sonda.

### PASSO 8 — SOURCE CURATOR: O GATE DE `READY`

Este trabalho entra no gate. Uma fonte de notícia/boletim **não** vira
`READY_FOR_COLLECTION` só porque a homepage respondeu com 200.

Para capability de detalhe, `READY` exige: listing acessível **+** enumeração de
detalhe comprovada **+** identidade **+** canário em item real **+** procedência.

⚠️ O Source Curator é o **único** dono do `READY` (provado em `907ccd70`: a
Collection é recusada pelo nome ao tentar promover). Respeite essa fronteira.

---

## 3 · BASELINE DE RECALL — LEIA ANTES DE PROMETER O NÚMERO

O briefing cita uma auditoria externa:

```text
REAL_RELEVANT_ITEMS = 326   COLLECTED = 2   MISSED = 324
```

**A coordenação procurou esse documento em todas as refs locais e remotas e no
disco. NÃO FOI ENCONTRADO.** O dono vai fornecê-lo.

- **se o documento chegar:** use-o como baseline e meça contra ele;
- **se não chegar até ao fecho:** `RECALL_VS_BASELINE_EXTERNO = NOT_MEASURABLE`,
  dito por esse nome. **Não invente o denominador.** Meça e entregue o recall do
  seu próprio canário (antes/depois, mesmas fontes), que é prova real e suficiente
  para esta missão.

```text
NÃO EXISTE META DE 100%. Existe melhoria real e explicável.
Número parcial vira NOT_MEASURABLE, nunca um zero calado.
```

---

## 4 · BLOCO DE ENTREGA

```text
SOURCES_CLASSIFIED            =
  BOLETIM_SERIADO             =
  LISTAGEM_DE_NOTICIAS        =
  NAO_SEI                     =

CONTRACTS_FIXED               =
CONTRACTS_DELIBERATELY_UNTOUCHED =

SOURCES_CANARIED              =
LISTINGS_FOUND                =
DETAIL_LINKS_DISCOVERED       =
DETAIL_ITEMS_SELECTED         =
DETAIL_ITEMS_COLLECTED        =
CONTROLO_NEGATIVO_MANTEVE_1   = YES/NO   ← se NO, a correção vazou

WASTEFUL_REOBSERVATION_BEFORE =
WASTEFUL_REOBSERVATION_AFTER  =

YOUTUBE_WATCH_HTML_AS_CONTENT = YES/NO
YOUTUBE_TRANSCRIPTION_CAPABILITY = PROVEN / EXISTS_UNPROVEN / ABSENT

PUBLISHED_AT_PRESERVED        =
FACT_TIME_CONTAMINATED        = NO   ← tem de ser NO

RECALL_VS_BASELINE_EXTERNO    =   (ou NOT_MEASURABLE + porquê)
RECALL_CANARIO_ANTES          =
RECALL_CANARIO_DEPOIS         =

DETAIL_COLLECTION_PROVEN      =
NEW_FAILURES                  =   (por NOME, contra baseline da mesma árvore)
SYSTEM_MAP_CHECK              =
KNOW_HOW_DELTA                =
BIG_COLLECTION_ALLOWED        = NO
PAID_USD                      =
```

---

## 5 · COMO FECHAR

**HARD STOP** no limite desta missão. Não continuar para Big Collection,
Intelligence ou Portal.

Achado não bloqueante vira **dívida registada**, não missão nova.

Se um gate falhar: **reporte a falha.** Não conserte silenciosamente para obter PASS.
Um PASS comprado é pior do que um FAIL honesto — o FAIL a coordenação consegue ler.

### 5.1 · O RELATÓRIO TEM DUAS PARTES, NESTA ORDEM

1. **RELATÓRIO MEDIDO** — estado, evidência, problema, próxima ação, com commits e gates.
2. **EM LINGUAGEM SIMPLES** — secção final **obrigatória**, sem jargão. O dono do
   projeto não é engenheiro: a parte técnica é a prova, a parte simples é o que ele lê
   para decidir. Termo técnico inevitável vem traduzido na mesma frase.
   `NÃO SEI` diz-se em português claro: «isto ainda não foi medido, portanto não sei».

Responda lá, em palavras simples:

1. antes colhíamos capa ou matéria?
2. que fontes foram corrigidas, e quais **deliberadamente não**?
3. quantas matérias reais o Sintonia passou a encontrar?
4. o mesmo conteúdo deixou de ser buscado repetidamente?
5. o YouTube continua a guardar HTML inútil?
6. a data de publicação passou a sobreviver?
7. a Collection já merece nova rodada pequena de prova?
