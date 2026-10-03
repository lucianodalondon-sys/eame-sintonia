# RELEVANCE E PRIORITY — PACOTE DE DECISÃO V1

```
MISSAO      C-INT-OWNER-01
ESPECIE     ARBITRAGEM. NAO IMPLEMENTA, NAO DECIDE, NAO PROMOVE.
MEDIDO_EM   2026-09-14
DECISAO     AWAITING_HUMAN_DECISION
```

> A pergunta do enunciado era «quem deve possuir `RELEVANCE` e `PRIORITY`?».
>
> **A medição respondeu outra coisa: nenhum dos dois é um conceito.**
> `RELEVANCE` são cinco perguntas diferentes e `PRIORITY` são quatro — e **sete
> das nove já têm dono, escrito em lei, a correr em código.**
>
> A decisão que falta não é «escolher um dono». É **o que fazer com os dois
> nomes**, agora que se sabe que eles não designam nada sozinhos.

---

# 0 · GIT MEDIDO

```
BRANCH        claude/intelligence-atomicity-v1
INITIAL_HEAD  90abc6511d94cdc43ddf3a8c5520cc9d0264779b
REMOTE_STATE  sincronizado
WORKTREE      limpo
SHALLOW       false
```

O HEAD bate com o fechamento anterior. Nada mudou no remoto.

---

# 1 · POR QUE A ARBITRAGEM V2 DISSE `HUMAN_DECISION_REQUIRED`

```
RELEVANCE  105 ficheiros · COLLECTION 8 · INTELLIGENCE 3 · DELIVERY 32 · OUTRA 38
PRIORITY   114 ficheiros · COLLECTION 6 · INTELLIGENCE 5 · DELIVERY 21 · OUTRA 66
```

Um conceito espalhado por quatro camadas não tem dono. **Mas a medição estava a
contar a palavra, não o conceito** — e a palavra cobre coisas que nunca foram a
mesma.

```
E O MESMO DEFEITO DE `COLLECTION_GAP`, PELA TERCEIRA VEZ:
UM NOME A COBRIR VARIOS CONCEITOS PARECE UM CONCEITO SEM DONO.
```

---

# 2 · `RELEVANCE` — CINCO CONCEITOS, QUATRO JÁ COM DONO

## ⚠️ A lei da Collection já tinha feito metade desta arbitragem

`leis/relevancia_da_fonte.py` escreve, no próprio cabeçalho, **sete fronteiras
com o dono de cada uma**:

```
SOURCE_RELEVANCE != ITEM_RELEVANCE       -> admissao/admissao.py
SOURCE_RELEVANCE != SOURCE_HEALTH        -> medidas/source_health.py · COL-LAW-028
SOURCE_RELEVANCE != ACCESSIBILITY        -> pedido/receitas.py · coleta/social_rotas.py
SOURCE_RELEVANCE != SOURCE_RELIABILITY   -> COL-LAW-216
SOURCE_RELEVANCE != COST                 -> COL-LAW-018 · COL-LAW-019
SOURCE_RELEVANCE != COLLECTION_PRIORITY  -> leis/politica_da_coleta.py
SOURCE_RELEVANCE != CASE_RELEVANCE       -> leis/adama_relevance.py
```

Ninguém leu isto quando se escreveu `OWNER = HUMAN_DECISION_REQUIRED`.

## A matriz

| # | conceito | pergunta que possui | writer | readers | lei | owner medido | estado |
|---|---|---|---|---|---|---|---|
| **R-1** | `SOURCE_RELEVANCE` | *esta **fonte** vale ser acompanhada **para este propósito**?* | `leis/relevancia_da_fonte.py` | `coleta/coletor.py` (guarda de gasto) | `RELEVANCIA_DA_FONTE/v1` | **COLLECTION** | implementado; livro vazio |
| **R-2** | `ITEM_RELEVANCE` | *este **item** presta para **este universo**?* | `admissao/admissao.py` | Sala de Espera | COL-LAW-038 | **COLLECTION** | implementado |
| **R-3** | `CASE_RELEVANCE` | *este **caso** liga a um produto ADAMA de forma defensável?* | `leis/adama_relevance.py` | `superficie/it_casa_dados.py`, portal | — | **INTELLIGENCE** | implementado |
| **R-4** | `CROP_RELEVANCE` | *a que **culturas** este evento se refere?* | a **fonte** (é dado colhido) | portal | — | **COLLECTION** (rótulo, não juízo) | 5 de 18 em `UNKNOWN` |
| **R-5** | `f_relevancia_ao_caso` | *este **lugar/conteúdo** é relevante ao caso?* | `supabase/` migration 015 | derivações | COL-LAW-036 | **COLLECTION** | implementado, com motivo escrito |
| **R-6** | `USER_DECISION_RELEVANCE` | *o achado importou para a **decisão de quem o leu**?* | ninguém | — | `INT-LAW-251` (métrica candidata) | **sem dono** | `NOT_MEASURED` |

## Os vocabulários não se tocam

```
R-1   AUTORIZA · BARRA · EXIGE_AVALIACAO
      sobre SIM · NAO · NAO_SEI · NAO_SE_APLICA · ERRO · NAO_AVALIADA
R-3   A · B · C · D · E    (A = OPPORTUNITA, B = RADAR, C = SEGNALI)
R-5   derivada com MOTIVO ESCRITO, e a lei proíbe coluna `score`
```

Três escalas, zero sobreposição. **Não são o mesmo conceito com granularidade
diferente: são perguntas diferentes.**

## E as três leis dizem a mesma coisa, sozinhas

```
relevancia_da_fonte.py   «NAO EXISTE relevante = true NUMA FONTE»
admissao.py              «RELEVANCIA NAO E UM BOOLEANO UNIVERSAL»
                         «a decisao e sempre do PAR (item, universo)»
```

```
RELEVANCE_ONE_CONCEPT = NO
E A RELEVANCIA NUNCA E PROPRIEDADE DA COISA:
E SEMPRE DO PAR (COISA, PERGUNTA).
```

Isto responde ao teste **R4** do enunciado antes de ele ser corrido: sim, a
relevância muda por contexto — e as três leis já o escreveram.

---

# 3 · `PRIORITY` — QUATRO CONCEITOS, TRÊS JÁ COM DONO

| # | conceito | pergunta que possui | writer | readers | lei | owner medido | estado |
|---|---|---|---|---|---|---|---|
| **P-1** | `REQUIREMENT_PRIORITY` | *entre as **necessidades** que faltam, qual primeiro?* | `leis/gestao_da_coleta.py` | o gestor da coleta | `GESTAO_DA_COLETA/v1` | **COLLECTION** | contrato |
| **P-2** | `PRIORITY_TIER` | *que **ação** esta fonte merece agora?* | `leis/politica_da_coleta.py` | orquestrador | — | **COLLECTION** | contrato |
| **P-3** | `COMMERCIAL_PRIORITY` | *isto é **oportunidade comercial defensável** para o portfólio ADAMA?* | `motor/v21_comercial.py::prioridade` | `v21_oportunidades.py` grava · portal **lê** | — | **INTELLIGENCE** escreve | implementado |
| **P-4** | `WATCHLIST_PRIORITY` | *este **tema emergente** merece ficar em vigia?* | ninguém | — | Radar do Futuro | **INTELLIGENCE** | `DEFINED_ONLY` |

## P-1 e P-2 não são o mesmo, e prova-se por consumo

```
politica_da_coleta.DIMENSOES = ('REQUIREMENT_PRIORITY', 'GAP_SEVERITY', ...)
```

`P-2` **consome** `P-1` como uma de dez dimensões. Um conceito que entra noutro
como insumo não é o mesmo conceito — é a matéria-prima dele.

```
P-1   P1_BLOQUEIA_OUTRAS · P2_NECESSARIA · P3_DESEJAVEL · P4_OPORTUNISTA · UNKNOWN
P-2   P0..P4, sobre a AÇÃO (lacuna crítica · velho · na hora · exploração · adiável)
P-3   SALES_READY · SALES_PREPARE · COMMERCIAL_WATCH · STRATEGIC_OPPORTUNITY · TO_VALIDATE
```

## ⚠️ O que NÃO foi encontrado, e é um achado

```
DISPLAY_ORDER   NAO EXISTE.
```

O portal lê `commercialPriority` em **2 linhas** de `italy-app-model.js` e não
há nenhuma função de ordenação por prioridade. **Ninguém está a usar prioridade
para decidir ordem de tela** — o ataque 8 do red team morre por ausência, não
por argumento.

```
PRIORITY_ONE_CONCEPT = NO
```

---

# 4 · A TENSÃO REAL QUE A MEDIÇÃO ENCONTROU

Não é de ownership. É de **nome**.

```
P-3 chama-se SALES_READY.
O que ele mede, declarado pelo proprio codigo:

  «necessidade externa corrente e positiva, produto do catalogo comercial com
   rotulo no par cultura x alvo, geografia que se sustenta e tempo para agir»

Os portoes: NEED_DIRECTION · COMMERCIAL_PRODUCT_COUNT · PRODUCT_LINK_STATE ·
CLAIM_GEOGRAPHY_HOLDS · COMMERCIAL_WINDOW.   TODOS de dado publico.
```

E o benchmark agro fixou o tecto:

```
NIVEL B  OPORTUNIDADE DE PORTFOLIO REGISTADO   publico: SIM
NIVEL C  OPORTUNIDADE COMERCIAL                publico: NAO — exige dado interno
```

```
O SIGNIFICADO DECLARADO E NIVEL B, E ESTA CERTO.
O NOME DIZ NIVEL C.
```

Nenhuma lei foi quebrada — o campo `COMMERCIAL_PRIORITY_MEANS` viaja ao lado e
diz a verdade. Mas um nome que promete mais do que o dado sustenta é o defeito
que o benchmark chamou **«o pior erro possível desta casa»**. Fica registado
aqui, e é parte da opção **[C]** do §6.

---

# 5 · OPÇÕES PARA `RELEVANCE`

```
CONCEITO:  RELEVANCE (o nome nu)
PERGUNTA QUE ELE POSSUI:  nenhuma — sao cinco, e quatro ja tem dono
```

## OPÇÃO A · APOSENTAR O NOME NU

```
OWNER        = NENHUM. `RELEVANCE` sozinho passa a ser vocabulario proibido.
POR QUE      = porque nao designa nada. Cada uso tem de ser um dos cinco nomes
               qualificados, e cada um ja tem dono a correr em codigo.
VANTAGEM     = zero conceitos novos, zero donos novos, zero migracao.
               A arbitragem fecha com o que ja existe.
RISCO        = `USER_DECISION_RELEVANCE` (R-6) fica sem dono, declarado.
               E a pergunta «esta evidencia importa para ESTA pergunta
               analitica?» continua sem sitio — porque hoje nao existe
               INTELLIGENCE_RUN para a fazer.
CONSEQUENCIA = a Biblia ganha uma lei de vocabulario. Nenhum codigo muda.
               A missao do INTELLIGENCE_RUN nasce SEM um campo relevance,
               e tera de justificar se precisa de um.
```

## OPÇÃO B · INTELLIGENCE HERDA O NOME PARA A PERGUNTA ANALÍTICA

```
OWNER        = INTELLIGENCE
POR QUE      = a unica das cinco perguntas que NAO tem dono e a analitica:
               «esta evidencia importa para ESTA INTELLIGENCE_REQUEST?».
               `INT-LAW-013` (TRUE != RELEVANT != ACTIONABLE) ja a nomeia, e
               nenhum modulo a responde.
VANTAGEM     = a espinha ganha o campo que lhe falta, com dono, antes de
               alguem o improvisar dentro do INTELLIGENCE_RUN.
RISCO        = cria um SEXTO conceito com o nome mais ambiguo da casa.
               Quem ler `relevance` num ficheiro passa a ter de saber qual dos
               seis. E o campo nasce sem implementacao nem prova.
CONSEQUENCIA = os outros cinco mantem nome qualificado obrigatorio.
               A proxima missao do INTELLIGENCE_RUN fica OBRIGADA a
               implementa-lo — deixa de ser opcional.
```

## OPÇÃO C · CONSOLIDAR EM `CASE_RELEVANCE`

```
OWNER        = INTELLIGENCE, via leis/adama_relevance.py
POR QUE      = a Intelligence ja possui UMA relevancia implementada (R-3).
               Dar-lhe o nome nu junta dono e implementacao no mesmo sitio.
VANTAGEM     = o unico dono da Intelligence para relevancia passa a ser
               visivel pelo nome.
RISCO        = `adama_relevance` responde «isto liga a um produto ADAMA?»,
               que e uma pergunta de PORTFOLIO, nao de pertinencia analitica.
               Herdar o nome nu faz a pergunta analitica parecer respondida
               quando nao esta — e e o unico dos tres caminhos que pode
               ESCONDER uma lacuna em vez de a declarar.
CONSEQUENCIA = R-6 continua sem dono e fica mais dificil de ver.
```

## RECOMENDAÇÃO TÉCNICA — `RELEVANCE`

```
RECOMENDACAO = OPCAO A
```

```
PROVA
  · cinco conceitos medidos, quatro com lei e codigo a correr
  · tres leis independentes ja escrevem que relevancia e do PAR, nunca da coisa
  · a pergunta analitica (R-6) nao tem hoje onde ser feita: nao ha
    INTELLIGENCE_RUN, e um campo sem quem o escreva e um campo que envelhece
  · `USER_DECISION_RELEVANCE` esta na Biblia como METRICA candidata
    (INT-LAW-251), nao como propriedade de um objeto

O QUE ESTA ESCOLHA NAO AUTORIZA
  · nao autoriza apagar nem renomear nenhum dos cinco
  · nao autoriza a Intelligence a escrever SOURCE_RELEVANCE nem ITEM_RELEVANCE
  · nao decide se o INTELLIGENCE_RUN vai ter um campo de pertinencia analitica
    — adia essa pergunta para quando houver um RUN que a possa fazer
```

A opção **B** fica correta no dia em que `INTELLIGENCE_RUN` existir. Hoje ela
cria um campo que ninguém escreve.

---

# 6 · OPÇÕES PARA `PRIORITY`

```
CONCEITO:  PRIORITY (o nome nu)
PERGUNTA QUE ELE POSSUI:  nenhuma — sao quatro, e tres ja tem dono
```

## OPÇÃO A · APOSENTAR O NOME NU

```
OWNER        = NENHUM. Cada uso usa um dos quatro nomes qualificados.
POR QUE      = P-1 e P-2 sao da Collection por lei; P-3 tem writer unico no
               motor; P-4 e da Intelligence e esta DEFINED_ONLY.
VANTAGEM     = zero conceitos novos. A fronteira
               COLLECTION != INTELLIGENCE != DELIVERY fica intacta e visivel.
RISCO        = nao resolve a tensao de NOME do §4: `SALES_READY` continua a
               prometer nivel C com dado de nivel B.
CONSEQUENCIA = a Biblia ganha uma lei de vocabulario. Nenhum codigo muda.
```

## OPÇÃO B · INTELLIGENCE GANHA UMA PRIORIDADE ANALÍTICA

```
OWNER        = INTELLIGENCE
POR QUE      = nenhum dos quatro responde «entre estes achados, qual merece
               atencao analitica primeiro?». P-3 responde a pergunta COMERCIAL.
VANTAGEM     = separa, de vez, ordem analitica de ordem comercial — que hoje
               so nao colidem porque a analitica nao existe.
RISCO        = cria um QUINTO conceito sem implementacao, e o enunciado
               proibe resolve-lo com score. Nasceria como vocabulario puro.
CONSEQUENCIA = P-3 deixa de poder ser lido como «o que ver primeiro», e o
               portal perde a unica ordenacao implicita que tem hoje
               (que, medido, ele NAO usa).
```

## OPÇÃO C · APOSENTAR O NOME **E** RENOMEAR `SALES_READY`

```
OWNER        = igual a opcao A (nenhum para o nome nu)
               + o vocabulario de P-3 passa a dizer o nivel que prova
POR QUE      = `SALES_READY` e derivado de dado publico, e dado publico prova
               no maximo NIVEL B. O significado declarado ja e nivel B; o nome
               nao.
VANTAGEM     = fecha a unica tensao real que esta missao encontrou, e fecha-a
               no sitio certo: o nome.
RISCO        = toca vocabulario JA IMPLEMENTADO e lido pelo portal em 8
               ficheiros de auditoria. Exige missao propria, com migracao de
               vocabulario e prova de que nada quebra.
               NAO E UMA MISSAO PEQUENA.
CONSEQUENCIA = o portal, as auditorias e os testes de prioridade comercial
               passam a exigir atualizacao coordenada.
```

## RECOMENDAÇÃO TÉCNICA — `PRIORITY`

```
RECOMENDACAO = OPCAO A agora · OPCAO C como missao propria, depois
```

```
PROVA
  · quatro conceitos medidos, tres com dono
  · P-2 CONSOME P-1 como dimensao: sao insumo e resultado, nao sinonimos
  · nao existe DISPLAY_ORDER: o portal LE `commercialPriority` em 2 linhas e
    nao ordena por ele
  · `COMMERCIAL_PRIORITY_MEANS` viaja ao lado e declara a verdade — a lei
    NAO esta quebrada, o nome e que promete demais

O QUE ESTA ESCOLHA NAO AUTORIZA
  · nao autoriza o portal a recalcular prioridade nenhuma
  · nao autoriza a Intelligence a escrever REQUIREMENT_PRIORITY nem PRIORITY_TIER
  · nao autoriza criar score, peso, ranking nem formula para nada disto
  · nao renomeia SALES_READY nesta missao
```

---

# 7 · RED TEAM

| # | ataque | veredito | como caiu |
|---|---|---|---|
| 1 | relevance é apenas confidence com outro nome | **KILLED** | `CONFIDENCE` é conceito separado na V2, com escala própria (`ALTA/MEDIA/BAIXA` em `v21_oportunidades`); R-1 usa `AUTORIZA/BARRA`, R-3 usa `A–E`. Zero sobreposição de vocabulário |
| 2 | relevance pertence à Collection | **PARTIAL** | **verdade para R-1, R-2, R-4, R-5** — quatro dos cinco. Falso para R-3 (`adama_relevance`, Intelligence) e para R-6 (sem dono). É o núcleo que fica: a maioria É da Collection |
| 3 | relevance pertence ao Portal | **KILLED** | o portal só lê. `adama_relevance` declara «o avaliador é um; o resto transporta», e `meeting-surface.js` lê o veredito impresso sem recalcular |
| 4 | relevance muda conforme `INTELLIGENCE_REQUEST` | **KILLED como objeção, CONFIRMADO como facto** | as três leis escrevem-no: é sempre do par. Isso não derruba a proposta — é a razão de ela existir |
| 5 | priority é relevance com peso | **KILLED** | `politica_da_coleta` proíbe explicitamente: «`SOURCE_SCORE = 87` NÃO EXISTE AQUI». `v21_comercial.prioridade` é «portões, não soma de pontos» |
| 6 | priority é apenas urgency | **KILLED** | P-3 separa `COMMERCIAL_WINDOW` (tempo) de `NEED_DIRECTION` (necessidade). `SALES_PREPARE` existe precisamente para «fecha, mas o momento é de preparação» |
| 7 | priority é commercial value | **PARTIAL** | verdade **só para P-3**. P-1 e P-2 são de coleta e não têm eixo comercial nenhum. O núcleo que fica é o §4: o nome de P-3 promete valor comercial que dado público não prova |
| 8 | priority pertence ao Portal | **KILLED** | medido: `commercialPriority` aparece em 2 linhas de `italy-app-model.js`, sem ordenação. Não há `DISPLAY_ORDER` nesta árvore |
| 9 | um mesmo campo priority usado por dois departamentos | **KILLED** | são campos **diferentes**: `PRIORITY` (gestão da coleta), `PRIORITY_TIER` (política), `COMMERCIAL_PRIORITY` (motor). Nenhum atravessa departamento mudando de significado |
| 10 | um split foi inventado sem evidência | **KILLED** | o split não foi inventado: `leis/relevancia_da_fonte.py` já declarava sete fronteiras com dono, escritas antes desta missão |
| 11 | um owner foi escolhido só porque já tem código perto | **KILLED** | a recomendação é **não escolher owner nenhum** para os nomes nus. Os donos citados já estavam declarados em lei |
| 12 | o conceito está a ser definido pela UI antiga | **PARTIAL** | `adama_relevance.SUPERFICIE` mapeia classe → tela (`A→OPPORTUNITA`, `B→RADAR`, `C→SEGNALI`). Uma lei de relevância a nomear superfícies é a UI a entrar na lei. **Não afeta as opções**, e fica declarado no §8 |

```
KILLED    9
PARTIAL   3
SURVIVED  0
```

Nenhum ataque sobreviveu como argumento estrutural. Os três `PARTIAL` têm
núcleo verdadeiro e os três estão escritos: a maioria da relevância É da
Collection (2), o nome de `P-3` promete demais (7), e uma lei nomeia
superfícies de UI (12).

---

# 8 · DÍVIDAS DECLARADAS, NÃO RESOLVIDAS AQUI

```
D-1  leis/adama_relevance.py::SUPERFICIE mapeia classe de relevancia -> tela.
     Uma lei da Intelligence a nomear `OPPORTUNITA`, `RADAR` e `SEGNALI` e a
     Delivery a entrar na lei. Nao foi tocado.

D-2  `SALES_READY` promete nivel C com dado de nivel B. O significado
     declarado esta certo; o nome nao. Ver opcao C do §6.

D-3  `LIVRO-DE-RELEVANCIA-DE-FONTE.json` esta VAZIO — divida ja nomeada no
     know-how, e reconfirmada aqui. A lei R-1 existe e nao tem decisoes
     escritas: o portao existe e ainda nao julgou nada.

D-4  `USER_DECISION_RELEVANCE` e `WATCHLIST_PRIORITY` nao tem dono nem
     implementacao. Sao os dois unicos dos nove nessa situacao.
```

---

# 9 · EM PALAVRAS FÁCEIS

## `RELEVANCE`

**O que a palavra significa hoje, na prática:** cinco coisas diferentes.

```
1. «vale a pena ir buscar dados a esta fonte, para este assunto?»   — da Coleta
2. «este item que chegou presta para este assunto?»                 — da Coleta
3. «este caso liga a um produto ADAMA?»                             — da Intelligence
4. «de que cultura este evento fala?»                               — vem da propria fonte
5. «o lugar citado interessa a este caso?»                          — da Coleta, no banco
```

E falta uma sexta, que ninguém responde hoje:

```
6. «esta evidencia importa para a PERGUNTA que estamos a fazer agora?»
```

**Se escolher A:** não muda nada no código. A palavra sozinha passa a ser
proibida — quem escrever `relevance` tem de dizer *qual* dos cinco. A pergunta
6 fica declarada como aberta, para quando existir o motor.

**Se escolher B:** a Intelligence fica dona da pergunta 6, e a próxima missão
fica **obrigada** a construí-la. Ganha-se um lugar para ela; arrisca-se ter um
campo que ninguém preenche durante meses.

**Se escolher C:** a Intelligence fica com a palavra, mas ligada à pergunta 3
(produto ADAMA). O risco é parecer que a pergunta 6 foi respondida quando não
foi.

## `PRIORITY`

**O que a palavra significa hoje:** quatro coisas.

```
1. «de tudo o que nos falta, o que ir buscar primeiro?»      — da Coleta
2. «que accao esta fonte merece agora?»                      — da Coleta
3. «isto da para vender, e quando?»                          — da Intelligence
4. «este tema emergente fica em vigia?»                      — da Intelligence, so no papel
```

E não existe uma quinta: **ninguém está a usar prioridade para decidir o que
aparece primeiro no ecrã.** Isso foi medido, não suposto.

**Se escolher A:** não muda nada. Cada um passa a usar o nome inteiro.

**Se escolher B:** a Intelligence ganha uma quinta — «entre estes achados, qual
olhar primeiro» — separada da comercial. Útil quando o motor existir; hoje
nasce vazia.

**Se escolher C:** faz-se A agora **e** marca-se uma missão futura para
renomear `SALES_READY`, que promete «pronto para vender» quando o que o dado
público prova é «temos produto registado e há janela». O significado escrito ao
lado já diz a verdade — é só o nome que exagera.

---

# 10 · DECISÃO NECESSÁRIA

```
RELEVANCE:
[A] APOSENTAR O NOME NU — cinco nomes qualificados, donos que ja existem,
    zero codigo alterado.                                   ← recomendado
[B] INTELLIGENCE fica dona da pergunta analitica («isto importa para ESTA
    pergunta?»), e a proxima missao fica obrigada a construi-la.
[C] INTELLIGENCE fica com o nome, ligado a relevancia de caso ADAMA que ja
    existe em `leis/adama_relevance.py`.

PRIORITY:
[A] APOSENTAR O NOME NU — quatro nomes qualificados, donos que ja existem,
    zero codigo alterado.                                   ← recomendado agora
[B] INTELLIGENCE ganha uma prioridade ANALITICA, separada da comercial.
[C] [A] agora + missao futura para renomear `SALES_READY`, que promete mais
    do que dado publico prova.                              ← recomendado depois
```

Pode responder em duas linhas:

```
RELEVANCE = [ ]
PRIORITY  = [ ]
```

---

# 11 · VEREDITOS

```
OWNER_DECISION_PACKAGE_READY     = YES

RELEVANCE_ONE_CONCEPT            = NO   (5 conceitos; 4 com dono)
PRIORITY_ONE_CONCEPT             = NO   (4 conceitos; 3 com dono)

RELEVANCE_OWNER                  = HUMAN_DECISION_REQUIRED
PRIORITY_OWNER                   = HUMAN_DECISION_REQUIRED

BIBLE_CANONICAL_PROMOTION_READY  = NO
INTELLIGENCE_RUNTIME_IMPLEMENTED = NO
OWNERS_CHANGED                   = NENHUM
```

## Como a decisão afeta o portão de promoção da Bíblia

A §31 da Bíblia exige `owner collision count = 0`. Medido:

```
COLISOES REAIS DE DONO = 0
```

Não havia colisão. Havia **sobrecarga de nome** — nove conceitos a partilhar
duas palavras. A condição nº3 fecha com **qualquer** das opções, porque
nenhuma delas cria um segundo dono para um conceito existente.

```
DEPOIS DESTA DECISAO, DAS NOVE CONDICOES DE PROMOCAO
RESTA UMA: A APROVACAO HUMANA.
```

---

# 12 · O QUE NÃO MUDOU

```
motor/           INTACTO      leis/          INTACTO
admissao/        INTACTO      coleta/        INTACTO
Portal · UI      INTACTOS     migrations     INTACTAS
LIVE             0 leituras · 0 escritas
Biblia           NAO PROMOVIDA · STATUS = CANDIDATE_FOR_CANONICAL_REVIEW
OWNERSHIP-V2     NAO ALTERADO — nenhum owner mudou em silencio
```

Nenhum score, peso, ranking ou fórmula foi criado. Nenhum algoritmo de
relevância ou prioridade foi escrito.
