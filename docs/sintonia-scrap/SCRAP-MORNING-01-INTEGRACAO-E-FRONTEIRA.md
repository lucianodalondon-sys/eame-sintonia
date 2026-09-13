# SCRAP-MORNING-01 — A INTEGRAÇÃO, E ONDE O SCRAP ACABA

> A NIGHT-SHIFT-01 entrou na Release Candidate por fast-forward. Os gates foram
> reprovados na árvore resultante. E o E7 — a única coisa que a madrugada não
> conseguiu atravessar — deixa de ser «um defeito do SCRAP por resolver» e passa
> a ser o que realmente é: **uma decisão de contrato da Collection**.

---

## 1 · A INTEGRAÇÃO

```
RC_INITIAL_HEAD  = 081316fc
NIGHT_HEAD       = 3581c471
MERGE_BASE       = 081316fc        ← igual ao RC_HEAD
RC...NIGHT       = 0 ↔ 10          ← nada na RC que a NIGHT não tenha
NIGHT descende da RC = SIM
```

As três condições do §1 batiam antes de tocar em nada, e por isso a integração
foi **fast-forward**: sem squash, sem cherry-pick, sem merge commit.

```
NIGHT = RC + correções provadas da madrugada
```

Um squash apagaria dez mensagens que explicam propriedades; um merge commit
inventaria uma bifurcação que nunca existiu.

```
MERGE COMMITS CRIADOS = 0
```

---

## 2 · O QUE SE REPROVOU NA ÁRVORE RESULTANTE

### A — uma rota recusada não produz observação

```
RESULT        ROUTE_NOT_ALLOWED
COST_STATE    NOT_RUN
PROVIDER_USED None
SOCKETS       0
objetos crus  1          ← a cadeia de Reel devolve o esqueleto, e está certa

COLHEITA             0
RAW_OBSERVATION      0
SOURCE_ID atribuído  0
contrato             sem reparos

DENIED_ROUTE_CAN_CREATE_OBSERVATION = NO
```

### B — o ambiente sem Chrome tem estado próprio, e ele CHEGA A QUEM LÊ

⚠️ **Este gate falhou na primeira medição, e o achado é próprio desta missão.**

A madrugada consertou o *trace*: sem Chrome, `instagram.profile.discovery`
passou a dizer `EXECUTOR_UNAVAILABLE` em vez de `UNKNOWN_ERROR`. Mas o que
atravessa a fronteira não é o trace — é o **recibo**. E o recibo levava cinco
chaves:

```
RESULT · EXECUTOR_ID · EXECUTION_MODE · NETWORK_REQUESTS_USED · COST_STATE
```

Nenhuma delas é a recuperação, e nenhuma é a frase. Quem lesse o envelope via um
estado sem saber de quem era a culpa nem o que fazer a seguir.

```
CONSERTAR O TRACE É CONSERTAR O TRACE. O QUE ATRAVESSA É O RECIBO.
UM ESTADO QUE SABE, NUM RECIBO QUE NÃO O LEVA,
VOLTA A SER «NÃO SEI» PARA QUEM LÊ.
```

O recibo passou a levar três eixos mais a frase — e nenhum deles é inventado
aqui: `leis/falhas.py` já os deriva todos, e `social_rotas.selar()` já os
escreve. Este ficheiro apenas deixou de os deitar fora.

```
RESULT           EXECUTOR_UNAVAILABLE
FAILURE_LAYER    EXECUTOR              ← ROTA CAÍDA NÃO É FONTE CAÍDA
RECOVERY_ACTION  NEEDS_HUMAN_FIX
NATIVE_REASON    BROWSER_NOT_REACHED
PORQUE           «sem Chrome nesta máquina: nenhum Chrome ou Chromium…»

KNOWN_ENVIRONMENT_FAILURE_AS_UNKNOWN = 0
```

E a frase viaja **ao lado** do nome, nunca dentro dele: `NATIVE_REASON` é
procurado numa tabela por `falhas.recuperacao`, e enfiar prosa lá faria a
refinação deixar de bater.

```
UM NOME E UMA FRASE NÃO CABEM NO MESMO CAMPO.
```

A frase vem de `ROUTER_RECORD.ERRO`, que `social_rotas` já **redigiu** — um
traceback de `urllib` carrega a URL, e a URL pode carregar o token.

### C — a autorização paga é atomicamente consumível

Pela porta REAL, com o provider falso abaixo do gate:

```
AUTH MAX_RUNS = 3 ·  5 concorrentes  →  POST = 3
AUTH MAX_RUNS = 3 · 16 concorrentes  →  POST = 3

AUTHORIZATION_DOUBLE_SPEND = 0
REAL_PAID_POSTS = 0
```

Nunca 4.

### D — a máquina de prova

```
ATTACKS = 56 · SURVIVORS = 0
MUTANTS = 37 · SURVIVORS = 0
```

Com as três regras que a madrugada aprendeu a cumprir: âncora em comentário não
vale (o guarda de `ALVO_AMBIGUO` recusa-se a correr), mutante em caminho morto
não vale (M20 foi re-ancorado no ramo que corre), e sentinela que não observa
mudança não vale (a que o vigiava corria sobre a única capacidade onde a
mutação não mudava nada).

---

## 3 · E7 — O QUE ELE É, E O QUE ELE NÃO É

A cadeia liga inteira. Com o código da Collection sobre os dados do SCRAP,
storage inteiramente descartável, e **zero ficheiros escritos no checkout que
está a ser lido**:

```
E1  o contrato aceita o envelope        PASSA
E2  a lei deixa passar a colheita       PASSA
E3  o ingresso aceita a unidade         PASSA
E4  o RAW foi preservado                PASSA
E5  a fronteira devolve a canónica      PASSA
E6  a admissão julga                    PASSA   → NAO_SEI · regra=legivel
E7  a unidade leva texto                PARA

FIRST_LOST_EDGE = E7
FILES_WRITTEN_IN_COLLECTION_CHECKOUT = 0
```

### Não basta `texto = TEXT`

`social_envelope` guarda o texto em `TEXT`; quem julga lê `texto`. A ligação
parece uma linha — e é exactamente por isso que é perigosa. Escrevê-la **apaga a
espécie do texto**: uma legenda escrita pelo autor e uma fala reconhecida por
máquina chegariam ao mesmo campo, indistinguíveis.

```
CAPTION != TRANSCRIPT
ORIGINAL != TRANSLATED
```

E essa é a primeira pergunta que a inteligência faz sobre qualquer classificação:
*o que sustentou isto — o que a pessoa escreveu, ou o que a máquina ouviu?*

### As quatro perguntas, e o estado de cada uma

```
1 · TEXT atravessa esta fronteira?                    SEM RESPOSTA CANÓNICA
2 · se atravessa, qual é o campo canónico?            SEM RESPOSTA CANÓNICA
3 · qual espécie ele carrega?                         SEM RESPOSTA CANÓNICA
      CAPTION_ORIGINAL · CAPTION_TRANSLATED ·
      TRANSCRIPT · ASR · OUTRO
4 · quem é o OWNER dessa tradução?                    COLLECTION / CONTRATO
```

Medido na linha da Collection mais recente (`82266600`), e não suposto:
`ingresso.PARA_A_PORTA` tem dez entradas e **nenhuma** é `TEXT`; não há
`TEXT_KIND`, nem `CAPTION`, nem `TRANSCRIPT` em `ingresso.py`, `admissao.py` ou
`retorno_da_coleta.py`. A decisão não foi tomada lá.

```
E7 = BLOCKED_BY_CONTRACT_DECISION
E7_OWNER = COLLECTION / CONTRACT DECISION
```

**Isto não reprova o SCRAP.**

---

## 4 · A FRONTEIRA DE RESPONSABILIDADE

```
SCRAP RESPONSIBILITY
    REQUEST → ORCHESTRATOR → ACQUISITION → RUN → RAW
            → RETURN CONTRACT → COLLECTION BOUNDARY
```

O SCRAP **não é dono** de:

```
DERIVED → STRUCTURED textual semantics
ADMISSION judgment
WAITING ROOM
```

E1–E6 passam; E7 é contrato downstream. Portanto:

```
SCRAP_TO_COLLECTION_BOUNDARY = PASS
```

O SCRAP entrega uma unidade que o contrato aceita, que o ingresso preserva, que
a fronteira devolve canónica e que a admissão consegue julgar. Que o veredito
seja `NÃO SEI` é a resposta **certa** de quem julga um item sem conteúdo — e a
razão de não haver conteúdo é uma palavra de vocabulário que ainda ninguém
decidiu, do lado de lá.

```
A CADEIA LIGAR E A ADMISSÃO DIZER SIM SÃO DUAS PERGUNTAS.
```

---

## 5 · O QUE CONTINUA A NÃO SER DO SCRAP

Dívidas já medidas e **declaradas na própria linha da Collection** — no ficheiro
de gates dela, na prova dela e no documento dela:

```
G-ENV-02   os envelopes acumulam-se, um por corrida, para sempre
G-RUN-02   uma corrida que morre antes de derivar continua a dizer «concluída»

DOWNSTREAM_COLLECTION_DEBTS = [G-ENV-02, G-RUN-02]
```

Não se corrigem nesta branch, e não contaminam o veredito do SCRAP.

---

## 6 · A DECISÃO HUMANA, INTACTA

```
SOURCE_ACCOUNT_BINDING = HUMAN_DECISION
```

Candidatos já medidos e **não inferidos**: `bayer_italia`, `syngentaitalia`,
`basf_global`. Nenhum deles foi tratado como `IT-T9-001`, e a primeira colheita
canónica não foi executada.

```
PLAUSIBLE != PROVEN
```

---

## 7 · O VEREDITO

```
SCRAP_ENGINE_READY           = PASS
SCRAP_TO_COLLECTION_BOUNDARY = PASS
SCRAP_OPERATIONAL_READY      = NO
SCRAP_V1                     = READY_PENDING_SOURCE_APPROVAL
```

O terceiro não é um defeito do motor. Ele diz uma coisa só:

> **motor pronto; fonte operacional ainda não autorizada nem ligada
> canonicamente.**
