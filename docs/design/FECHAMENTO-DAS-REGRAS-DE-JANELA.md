# Fechar as onze regras de janela — e descobrir que «ausente» dizia quatro coisas

```
WINDOW_RULE_CLOSURE = PASS

HEAD inicial   e7c154c   ·   BUILD_ID V21-cc9e5ce20da2dab6
HEAD final     este commit
```

Os onze `WINDOW_RULE_MISSING` foram trabalhados um a um. Dez ganharam regra.
Um continua sem — e o motivo dele não é falta de coleta.

Mas o achado da rodada não é o dez. É que **`WINDOW_RULE_MISSING` dizia uma
coisa só e o mundo dizia quatro**:

| o que a fonte fez | estado novo | pede coleta? |
|---|---|---|
| declarou a condição agronômica | `RULE_DECLARED` | não |
| fixou o momento por **norma** | `RULE_ADMINISTRATIVE_ONLY` | não |
| mandou **medir no pomar** | `RULE_DELEGATED_TO_FARM` | não |
| não declarou nada | `RULE_NOT_DECLARED` | **sim** |

    «NÃO ACHAMOS A REGRA» E «A REGRA DIZ OUTRA COISA» SÃO RESPOSTAS DIFERENTES.
    UMA PEDE MAIS COLETA; AS OUTRAS TRÊS FECHAM A PERGUNTA.

Chamar as três primeiras de «ausente» é mandar uma equipe atrás de um documento
que ninguém vai escrever.

---

## A tabela veio antes da busca

`python3 scripts/v21_regras_de_janela_ausentes.py` ordena por **defensabilidade
comercial**, em cinco degraus declarados — SALES_READY, portfólio ADAMA
defensável, capacidade de mover a ação comercial, fonte regional disponível, e o
resto. Nunca por facilidade da fonte.

O terceiro degrau merece a frase que o justifica:

    SABER QUANDO AGIR NUM CASO ONDE A FONTE MANDA NÃO AGIR
    É CONHECIMENTO VERDADEIRO E DECISÃO NENHUMA.

E a pergunta de cada linha ficou escrita **antes** de qualquer busca:

> **QUAL REGRA AGRONÔMICA DEFINE QUANDO AGIR contra este alvo, nesta cultura,
> nesta região?**

Não se procurou se a condição está aberta hoje. Não se sabia ainda qual era a
condição.

---

## Os onze, um a um

Tudo o que segue sai de `data/samples/AUDITORIA-SOMBRA/V116-FECHAMENTO-DAS-REGRAS.json`,
produzido por `python3 scripts/v21_fechamento_das_regras.py`. O ANTES sai de
`V116-ANTES-DAS-REGRAS.json`, gerado repondo a árvore de `e7c154c` e rodando a
cadeia real — nunca de lembrança.

### 1 · videira × peronospora · Friuli-Venezia Giulia — `OPP_D9B21D005CC3`

| | ANTES | DEPOIS |
|---|---|---|
| `WINDOW_DEFINED` | NO | **YES** |
| `WINDOW_TYPE` | — | `PHENOLOGY_WINDOW` |
| `WINDOW_OPEN_NOW` | UNKNOWN | UNKNOWN |
| `STATUS` | WATCH | WATCH |
| falta | `WINDOW_RULE_MISSING` | `WINDOW_STATE_UNKNOWN` |

**Fonte** · Disciplinare di produzione integrata FVG, anno 2025 (Decreto n. 115
del 06/03/2025) · `REGION_FRIULI_VENEZIA_GIULIA` · papel `DECLARA_A_CONDICAO_AGRONOMICA`

> «Effettuare due trattamenti cautelativi con antiperonosporici dotati di
> persistenza di almeno 10-12 giorni: - subito prima della fioritura - a fine
> fioritura allo scadere del periodo di persistenza del prodotto impiegato. […]
> È necessario mantenere costantemente sotto controllo la situazione utilizzando
> le previsioni meteorologiche e, in previsione del verificarsi e del perdurare
> di condizioni favorevoli alla malattia, intervenire preventivamente.»

**WHY_CHANGED** — a regra existe, é regional, e entrou pela mesma porta e pela
mesma cadeia dos boletins.

### 2 · videira × escafoide · Umbria — `OPP_48C2731BAFD1`

| | ANTES | DEPOIS |
|---|---|---|
| `WINDOW_DEFINED` | NO | **YES** |
| `WINDOW_TYPE` | — | `PEST_STAGE_WINDOW` |
| `WINDOW_OPEN_NOW` | UNKNOWN | UNKNOWN |
| `STATUS` | WATCH | WATCH |

**Fonte** · Servizio Fitosanitario Regionale dell'Umbria — scheda «Controllo
degli organismi nocivi: Scaphoideus titanus» · papel `DECLARA_A_CONDICAO_AGRONOMICA`

> «Un programma di lotta contro lo Scafoideo si giustifica quando esso è presente
> in vigneti affetti da flavescenza dorata. L'eventuale lotta chimica va condotta
> nei confronti delle forme giovanili.» · «I dati del monitoraggio 2020 non hanno
> rilevato la presenza di tali organismi nocivi.»

A regra é dupla e a segunda metade é comercialmente decisiva: o próprio serviço
regional declara que **não encontrou o vetor**. A ficha não traz data de
publicação; a data de referência usa o último facto que ela declara — o
monitoramento de 2020 — como **convenção nossa, escrita no registro**.

### 3 · arroz × giavone · Itália — `OPP_4C39CCC05EEB` · **não fechou**

| | ANTES | DEPOIS |
|---|---|---|
| `WINDOW_DEFINED` | NO | NO |
| falta | `WINDOW_RULE_MISSING`, `DIRECTION_UNKNOWN`, `SIGNAL_NOT_RECENT`, `REGION_NOT_DECLARED` | idem |

**WHY_NOT_CHANGED** — e a razão não é falta de fonte. Este caso **não tem
região**: nasce de registros de resistência (`IT-RES-*`) com escopo nacional,
sem sinal de campo e sem direção. As regras de arroz existem, e existem **por
região e por época** — o disciplinare da Lombardia tabela o diserbo por
presemina, falsa semina e pós-emergência, para «Graminacee», não para
*Echinochloa* nomeada.

Colher a regra da Lombardia e colá-la num caso `GEO_ITALY` seria exatamente o
defeito de geografia que a missão 4 fechou.

    ESTE NÃO É UM VÃO DE JANELA. É UM VÃO DE GEOGRAFIA COM NOME ERRADO.
    ENQUANTO O CASO NÃO TIVER REGIÃO, NENHUMA REGRA REGIONAL PODE ALCANÇÁ-LO.

### 4 · videira × peronospora · Umbria — `OPP_DF0C3648893A`

`NO` → **`YES` · `PHENOLOGY_WINDOW`**. Fonte: Disciplinari di produzione
integrata 2025-2026, Regione Umbria.

> «Fino alla pre fioritura: - intervenire preventivamente sulla base della
> previsione delle piogge. Dalla pre fioritura alla allegagione: - anche in
> assenza di macchie d'olio intervenire cautelativamente con cadenze in base
> alle caratteristiche dei prodotti utilizzati.»

`STATUS` continua `WATCH`: a direção do par é `NO_ACTION_RECOMMENDED`, e quem
manda parar continua a mandar parar. **Saber quando agir não abre a porta que a
fonte fechou.**

### 5 · videira × peronospora · Emilia-Romagna — `OPP_E138ECDFD7D2`

`NO` → **`YES` · `PHENOLOGY_WINDOW`**. Fonte: Difesa integrata VITE, DPI 2026,
Regione Emilia-Romagna (Determinazione n. 3130 del 16/02/2026).

> «Fino alla prefioritura: - iniziare la difesa seguendo le indicazioni dei
> Bollettini tecnici territoriali. Fino alla allegagione: - intervenire
> preventivamente sulla base della previsione delle piogge […] entro il 25% del
> periodo di incubazione della presunta infezione. Dall'allegagione in poi: -
> impiegare prodotti di copertura (rameici).»

### 6 · milho × piralide · Lombardia — `OPP_81C053E9DCD3`

`NO` → **`YES` · `THRESHOLD_WINDOW`**. Fonte: Difesa Integrata di Mais, DPI 2026,
Regione Lombardia.

> «Piralide (Ostrinia nubilalis) — Interventi agronomici: Sfibratura degli
> stocchi e aratura tempestiva. Soglia: Solo in caso di presenza accertata sulla
> II e III generazione.»

⚠️ O valor do limiar foi lido **reconstruindo as colunas da tabela do PDF**,
onde a linha «Soglia:» e a do seu valor aparecem separadas pela coluna das
substâncias ativas. A linha das *nottue terricole* tem a mesma forma e serviu de
controlo. **O método está escrito no próprio registro**, em
`WHAT_IT_DOES_NOT_PROVE` — quem discordar da leitura lê o método e decide.

### 7 · videira × escafoide · Toscana — `OPP_D11664591168` · **regra administrativa**

| | ANTES | DEPOIS |
|---|---|---|
| `WINDOW_DEFINED` | NO | **NO** (a lei não mudou) |
| `WINDOW_RULE_STATE` | `RULE_NOT_DECLARED` | **`RULE_ADMINISTRATIVE_ONLY`** |
| falta | `WINDOW_RULE_MISSING` | **`WINDOW_RULE_ADMINISTRATIVE_ONLY`** |

> «SCAFOIDEO — Scaphoideus titanus. Nelle aree delimitate dal Servizio
> Fitosanitario, in base a quanto stabilito nel Piano di azione regionale con le
> misure obbligatorie contro Flavescenza dorata, eseguire gli interventi
> obbligatori.» · «Efficacia limitata alle forme giovanili (fino alla II e III
> età).»

A regra existe e **não é agronômica**: é obrigação de norma. `ADMINISTRATIVE_WINDOW`
continua fora de `AGRONOMICOS` — essa lei é de julho e não se toca. O que mudou
é que o cartão parou de dizer que ninguém declarou nada.

### 8 · milho × diabrótica · Lombardia — `OPP_F6EEF5B32F65`

`NO` → **`YES` · `THRESHOLD_WINDOW`**.

> «Soglia: Catture di 50 adulti settimanali consecutive per due settimane e solo
> nel caso si preveda la coltura del mais anche nell'anno successivo.»

O caso é `TREATMENT_PROHIBITED` e continua `WATCH`. A regra agora está no cartão
e não move nada — que é o comportamento certo.

### 9, 10 e 11 · videira × oídio · Friuli, Umbria e Toscana

Os três `NO` → **`YES` · `PHENOLOGY_WINDOW`**, cada um da sua região:

- **FVG** — «nelle fasi comprese fra risveglio vegetativo e fioritura,
  intervenire con Zolfo […] nelle fasi comprese fra post-allegagione e
  invaiatura, alternare le sostanze attive a diverso meccanismo d'azione,
  adottando intervalli inferiori (max 10 giorni)».
- **Umbria** — «Zone ad alto rischio: Fino alla pre fioritura: intervenire
  preventivamente con antioidici di copertura. Dalla pre fioritura
  all'invaiatura: intervenire alternando prodotti sistemici e di copertura.»
- **Toscana** — «Cadenzare gli interventi dal germogliamento all'invaiatura in
  funzione della pressione infettiva esercitata dal patogeno e della
  suscettibilità varietale.»

Os três mantêm `COMMERCIAL_PRODUCT_MISSING`: não há produto do catálogo ADAMA com
rótulo ministerial no par. **A regra não inventa portfólio.**

---

## O que a coleta de REGRAS obrigou a construir

### A regra diz quando agir. Ela não diz que se deve agir agora.

Um disciplinare escreve «intervenire preventivamente». Lida como direção, essa
frase faz um documento de **março de 2025** declarar pressão de campo em
setembro de 2026.

    UM DISCIPLINARE É UMA REGRA PERMANENTE. UM BOLETIM É UMA NOTÍCIA.
    A REGRA DIZ QUANDO AGIR; SÓ A NOTÍCIA DIZ QUE CHEGOU A HORA.

`OBSERVATION_CLASS = STANDING_RULE` passa a excluir o registro de
`pares_observados`. Consequências, todas medidas:

1. um disciplinare **nunca** declara `NEED_DIRECTION`;
2. um disciplinare **nunca cria oportunidade** — ele informa o caso que o
   boletim já criou;
3. ele **continua** a declarar janela, que é para o que foi coletado;
4. `PEST_STAGE_STATE` e `ACTION_RECOMMENDATION_STATE` também deixam de sair
   dele: «il primo volo inizia verso la metà di aprile» é biologia, não é o
   estado do campo hoje.

`T60` quebra se algum cartão apontar uma regra como dona da direção.

### A fonte que respondeu tem de estar na lista que se audita

Um disciplinare não observa par nenhum — e por isso **nunca entrava em
`EVIDENCE_IDS`**. O cartão citava-o em `WINDOW_EVIDENCE_ID` e não o listava.

    CITAR NUM CAMPO E NÃO LISTAR NA EVIDÊNCIA É ESCONDER A FONTE
    ONDE SÓ QUEM JÁ SABE VAI OLHAR.

Agora a evidência da janela e a da regra entram em `EVIDENCE_IDS` e recebem
papel `SUPPORTS_WINDOW`. Foi o próprio `T43` que apanhou isto: quatro regras
tinham entrado no acervo e não eram apoio de caso nenhum.

### O léxico da janela conhecia a redação de um boletim, não a de quatro disciplinari

Os quatro disciplinari lidos escrevem o mesmo gatilho com quatro redações — e
**nenhuma casava**:

```
«intervenire preventivamente sulla base della previsione delle piogge»
«in previsione … di condizioni favorevoli alla malattia»
«fino alla pre fioritura» / «dalla pre fioritura all'invaiatura»
«dal germogliamento all'invaiatura»
```

    UM LÉXICO QUE SÓ CONHECE A REDAÇÃO DE UM BOLETIM CHAMA DE «SEM JANELA»
    O DISCIPLINARE QUE DECLARA A JANELA — E A LACUNA É NOSSA, NÃO DA FONTE.

O léxico foi estendido com as redações **medidas nos documentos reais**, e o
efeito no acervo de então foi medido antes de qualquer coleta: **16 candidatas →
17**, uma só entrada (a Toscana × botrite ganha também
`WEATHER_TRIGGERED_WINDOW`), **nenhuma saída**, e o cartão da Toscana inalterado
porque a fenológica continua a ganhar por estar aberta.

### `RULE_DELEGATED_TO_FARM` virou tipo de janela

Conforme decidido: a regra é conhecida — «medir no pomar» — logo
`WINDOW_DEFINED = YES`. E a medição não é regional, logo `WINDOW_OPEN_NOW =
UNKNOWN`, com método próprio:
`REGRA_EXIGE_MEDICAO_DO_POMAR_QUE_NENHUMA_FONTE_REGIONAL_TEM`.

Ele entra **por último** em `AGRONOMICOS`: havendo condição regional declarada
para o mesmo par, é ela que responde.

E o método deste tipo — como o do ato administrativo — passou a ser respondido
**antes** da guarda de idade do documento: o manual do Veneto é de 2020, e
responder `DOCUMENTO_NAO_CORRENTE` a uma regra que manda medir no pomar seria
dar a razão errada outra vez.

---

## Três donos separados, ainda separados

O contrato de setembro continua de pé, e os testes seguram:

| a fonte diz | prova | **não** prova |
|---|---|---|
| «continuare la difesa» | `ACTION_RECOMMENDATION_STATE` | limiar, fenologia, `WINDOW_OPEN_NOW` |
| «terzo volo terminato» | `PEST_STAGE_STATE` | janela fechada, recomendação encerrada |
| «fino alla pre fioritura» | `WINDOW_DEFINED` + `WINDOW_TYPE` | que a fase esteja acontecendo agora |

`T61` quebra se uma regra sozinha abrir uma janela.

---

## Backfill dos 43

```
                         ANTES (e7c154c)      DEPOIS
CASES                        43                 43
SALES_READY                   5                  5
ACT_NOW                       2                  2
VALIDATE_NOW                  3                  3
WATCH                        22                 22
TO_VALIDATE                   9                  9
FUTURE_PREPARATION            7                  7

WINDOW_DEFINED                6                 16
WINDOW_OPEN_NOW = YES         2                  2
WINDOW_OPEN_NOW = UNKNOWN    41                 41
WINDOW_OPEN_NOW = NO          0                  0

RULE_DELEGATED_TO_FARM        1                  1
RULE_ADMINISTRATIVE_ONLY      0                  1
WINDOW_RULE_MISSING          11                  1
```

**Nenhum estado comercial se moveu.** `STATUS`, `COMMERCIAL_PRIORITY`,
`EXTERNAL_MATERIAL_READY` e `NEED_DIRECTION` são idênticos nos 43 — e
`v21_fechamento_das_regras.py` **reprova sozinho** se qualquer um deles mudar,
porque a regra não tem esse direito:

    A REGRA DECLARA QUANDO AGIR. SE ELA MEXER NO NÚMERO COMERCIAL,
    NÃO FOI REGRA QUE ENTROU — FOI PRESSÃO INVENTADA.

O que mudou foi só o que devia: dez cartões passaram de «ninguém declarou a
condição» para «a condição é esta, e falta saber se está satisfeita».

---

## ISTAT — carimbar por ano é possível, e continua não carimbado

`python3 scripts/v21_qa_do_istat.py`

```
QA_PASS = PARTIAL        2024 = YES · 2025 = YES · 2026 = UNKNOWN
CARIMBO = NÃO APLICADO
```

**É possível carimbar por ano?** Sim. `QA_STATUS` é campo por registro, e o
`YEAR` já está em cada linha: nada no encanamento obriga a tratar as 2 945 como
um bloco. As provas de coerência rodam por ano e passam nos três.

**O impacto, medido:**

| ano | linhas | das quais AREA | pares cultura × geografia | dos 43 casos |
|---|---|---|---|---|
| 2024 | 1 000 | 334 | 311 | **33** |
| 2025 | 1 006 | 336 | 313 | **33** |
| 2026 | 939 | 313 | 293 | 29 |

- **liberadas se carimbar 2024+2025:** 2 006 linhas
- **permanecem UNKNOWN:** 939 (as de 2026)
- **cartões que perderiam `OFFICIAL_AREA_NOT_CLIENT_SAFE`:** 43

**Muda algum resultado comercial? NÃO — e é verificável.** `AREA_OFICIAL_HA`
alimenta `COMMERCIAL_MAGNITUDE` e a lista `WHAT_IS_MISSING`. Nenhum portão de
`v21_comercial.prioridade` a lê: os portões são semânticos, e área não é portão.

> ⚠️ **Item aberto nomeado, medido nesta rodada.** O motor escolhe `area[0]` —
> a primeira linha AREA da cultura × geografia — **sem escolher o ano**. Com um
> ano só client-safe isso é determinístico; com 2024 **e** 2025 liberados, passa
> a depender da ordem do arquivo. Carimbar dois anos sem antes declarar qual
> ano o cartão cita é criar um número que muda de significado sem avisar.
> Isto é uma linha de código e uma decisão — e a decisão é de vocês.

2026 fica `UNKNOWN` porque o próprio ISTAT o publica como estimativa provisória
(`OBSERVATION_CLASS = OUTLOOK`), e coerência interna não torna provisório em
definitivo.

    CARIMBAR PROVISÓRIO COMO DEFINITIVO É ERRAR EM SILÊNCIO SEIS MESES DEPOIS.

---

## O que ainda depende de observação local, e o que exige coleta nova

**Dependem de medição que nenhuma fonte regional publica — 14 casos**
(`WINDOW_STATE_UNKNOWN` 13 + `WINDOW_RULE_DELEGATED_TO_FARM` 1). A regra está no
cartão; falta o número do talhão: percentagem de cachos, capturas por armadilha,
estádio corrente, evento meteorológico. Nenhuma coleta de fonte oficial fecha
isto — é dado de campo.

**Exige coleta nova — 1 caso.** Arroz × giavone, e a coleta que ele precisa
**não é de janela**: é de geografia e de direção. Enquanto o caso for
`GEO_ITALY` sem sinal de campo, nenhuma regra regional o alcança.

**Fechado por norma — 1 caso.** Toscana × escafoide: a delimitação é ato do
Servizio Fitosanitario e muda por decreto, não por safra.

---

## Regressões

Nenhuma. Suíte: **763 descobertos · 758 executados · 6 falhas · 2 erros · 14
pulados** — as mesmas 8 de sempre, todas anteriores a esta linha de missões.
Provas da camada comercial: **100/100**.

Contratos: geografia **0 violações**, procedência **0 violações**, língua
**10 981 campos com IT+EN · 0 ainda só em português**.

Testemunhas da rodada anterior, todas verdes de novo:
`SEMANTIC_RED_TEAM = PASS` · `REGRESSAO_DO_RED_TEAM = PASS`.

> Uma correção no próprio red team: `item_3` verificava «nenhum registro
> `IT-COL-2609-FVG*` foi criado» — e o lote desta rodada usou esse prefixo para
> uma **regra do Friuli com fonte, data e citação**. O teste acusou quem
> cumpriu a regra.
>
>     UM TESTE QUE OLHA O NOME DO ARQUIVO EM VEZ DO CONTEÚDO
>     ACUSA QUEM CUMPRIU A REGRA.
>
> Passou a verificar o que a missão de facto proibiu: nenhuma **medição** de
> milho no Friuli com data posterior a 12/08/2026.

---

## Custo

| | |
|---|---|
| documentos oficiais lidos | 6 (5 disciplinari regionais + 1 ficha do SFR) |
| páginas de PDF processadas | ~2 700 |
| registros novos no acervo | 6 |
| frases novas traduzidas (PT→IT+EN) | 12 · memória 1 090 → 1 102 |
| linhas de motor alteradas | ~120, em 3 arquivos |
| testes novos | 5 (`T59`–`T63`) |
| execuções da cadeia completa | 9 |
| coleta indiscriminada aberta | **nenhuma** |

---

## Resposta

```
WINDOW_RULE_CLOSURE = PASS

HEAD inicial              e7c154c
HEAD final                este commit
gaps iniciais             11
ganharam regra            10
  agronomica              9
  administrativa          1
  delegada ao pomar       0 (o unico ja existia, do lote anterior)
continuam WINDOW_RULE_MISSING   1

tipos encontrados   PHENOLOGY_WINDOW 6 · THRESHOLD_WINDOW 2
                    PEST_STAGE_WINDOW 1 · ADMINISTRATIVE (nao agronomica) 1

fontes              DPI FVG 2025 (Decreto 115 de 06/03/2025)
                    DPI Emilia-Romagna 2026 (Determinazione 3130 de 16/02/2026)
                    DPI Umbria 2025-2026 · DPI Toscana 2026 · DPI Lombardia 2026
                    Scheda Scaphoideus titanus, SFR Umbria

estados comerciais  identicos nos 43, antes e depois
backfill            43/43 · WINDOW_DEFINED 6 -> 16 · WINDOW_RULE_MISSING 11 -> 1
ISTAT por ano       possivel · 2024 e 2025 liberariam 2006 linhas e 33 casos cada
                    · 2026 fica UNKNOWN · NENHUM resultado comercial muda
                    · CARIMBO NAO APLICADO
dependem do pomar   14 casos
exigem coleta nova  1 caso — e de geografia, nao de janela
regressoes          nenhuma

CANONICAL_BRANCH = claude/opportunity-commercial-priority-v1
AUDIT_BRANCH     = FROZEN

PORTAL = NAO TOCADO       DESIGN = NAO TOCADO      VERCEL = NAO TOCADO
PRODUCAO = NAO TOCADA     THRESHOLDS = NAO ALTERADOS
SEGUNDO MOTOR = NAO CRIADO   merge = NAO   publicacao = NAO
```
