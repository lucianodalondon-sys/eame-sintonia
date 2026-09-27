# KNOW-HOW DELTA — O CICLO DE VIDA DA FONTE TEM DONO, E O DONO NÃO DORME

    ENTREGUE COMO DELTA. NÃO ESCRITO NA RAIZ DE PROPÓSITO.

Esta branch nasce de `376c0d9b`, cujo know-how vai até **§158**. A
`big-collection-release-v1` já emitiu **§162** entretanto. Escrever `§159`
aqui criaria dois conhecimentos diferentes a disputar o mesmo número, e o
merge não acusaria. O Coordinator atribui o número na integração.

---

## O QUE MUDOU

O Source Curator deixa de ser uma sequência de missões manuais e passa a ter
um **motor**: estado por fonte, fila durável e um worker que trabalha sozinho.

    ANTES:  a Collection recebia uma fonte e fazia o onboarding dela
            no meio da coleta — validar, contratar, canariar, reparar.
    AGORA:  a Collection recebe READY_FOR_COLLECTION e coleta.

A fronteira ficou executável, não escrita em prosa:

```
CURATOR   entrega   READY_SOURCES
COLLECTION devolve  SOURCE_REPAIR_NEEDED
```

`transicao_permitida()` recusa qualquer outra coisa, e um teste tenta violá-la.

---

## AS QUATRO LIÇÕES DURÁVEIS

### 1. Esperar não é bloquear — e o erro mora num `sleep`

O modo natural de tratar um 429 é `time.sleep(retry_after)`. Isso adormece o
**processo**, e com ele toda a fila: 50 fontes ficam paradas porque uma pediu
tempo. É exatamente o que se via nas 50 YouTube da Big Collection.

```
UMA TAREFA ADIADA ESTÁ A ESPERAR.
UM WORKER ADORMECIDO ESTÁ A BLOQUEAR.
```

A correção não é um scheduler: é marcar `NEXT_ATTEMPT_AT` no disco e a tarefa
deixar de ser **elegível**. O worker pega a seguinte. Quando o relógio passa,
ela volta sozinha, sem ninguém a acordar.

**Injetar o relógio (`agora=`) é o que torna isto provável.** Uma prova de
backoff que exigisse esperar 3600 s reais não se corre — e uma prova que não
se corre não prova nada. Medido: A adiada, B/C/D correram na mesma volta, A
reapareceu a `+61 min`.

### 2. Um timeout não é um Disallow — e chegam pela mesma porta

`gate_de_rota.robots_de()` devolve Disallow-total em dois casos muito
diferentes: o host proibiu mesmo, **ou** a rede não deixou ler o ficheiro (e
então condena «por prudência», dizendo-o no texto que devolve).

Prudência é a decisão certa para não bater à porta. Mas gravar
`CONTRACT_READY_ROUTE_BLOCKED` por um timeout **condena uma fonte boa por
defeito nosso** — o mesmo erro que o próprio `gate_de_rota` documenta ter
cometido com `nomisma.it`.

```
NÃO SEI != PROIBIDO.
rede em baixo   -> RETRY (volta depois, por conta própria)
Disallow lido   -> BLOCK (para, e chama o dono da política)
```

Quem consome uma função que colapsa dois motivos num só valor tem de reabrir
a distinção do seu lado. O valor de retorno mente por omissão, não por erro.

### 3. READY é uma consequência, nunca um carimbo

`ready_sources()` deriva do livro **a cada chamada**. Um snapshot guardado
envelhece em silêncio: uma fonte marcada `DEGRADED` continuaria a aparecer
como pronta até alguém regenerar o ficheiro — e a Collection iria colhê-la.

```
UMA FONTE DEGRADADA SAI DE READY NO MESMO INSTANTE.
```

O livro é append-only pela mesma razão: o estado é a última transição, nunca
um campo que alguém sobrescreve. Guardar só o estado atual perde a razão pela
qual ele mudou — e a razão é o que permite auditar uma promoção meses depois.

Corolário provado: **de `DEGRADED` não se volta a `READY` por decreto.** O
caminho é `REPAIRING` + canário novo, e a ficha passa a apontar a evidência
do canário novo, não a do velho.

### 4. Um processo que morre a sério é outra prova

Uma suíte que apanha exceções prova que o `try` funciona. Para provar que o
**trabalho sobrevive**, o processo tem de morrer de verdade — `os._exit(97)`,
que não desenrola pilha, não corre `finally` e não corre `atexit`. Quem
responde a seguir é outro processo, que só vê o disco.

Marcar `IN_PROGRESS` **antes** de executar é o que torna a recuperação
honesta: quem reabre o ficheiro vê uma tarefa começada e não fechada, que é a
verdade. Fingir que nunca começou seria mentir sobre o passado.

Medido: processo 1 morreu a meio de `SRC-C`; o disco guardou
`{A:WAITING_RETRY, B:DONE, C:IN_PROGRESS, D:PENDING}`; o processo 2 recuperou
`C` e terminou `C` e `D`; `A` voltou sozinha a `+61 min`. 7/7.

---

## O QUE ESTA MISSÃO **NÃO** FEZ

```
NÃO coletou. NÃO cunhou RUN_ID. NÃO escreveu RAW.
NÃO tocou big-collection-release-v1 (viva durante toda a missão, HEAD f93ee597).
NÃO tocou Sala, Admission, Intelligence nem Portal.
NÃO integrou nada na linha operacional.
```

O canário abre **um** documento para provar que a rota resolve. Isso é prova
sobre a fonte, não aquisição de conteúdo: nada foi preservado como acervo.

    VALIDAR != COLETAR.

---

## DÍVIDA HERDADA, MEDIDA E DEVOLVIDA AO DONO

`P9_CODIGO_DECLARADO` falha com `regras/motor_de_rota.mjs` e
`regras/motor_de_rota_test.mjs`. Medido na base intocada com
`git worktree --detach 376c0d9b`: **já falhava lá**. `NEW_FAILURES = 0`. A
peça é de outra frente e não se conserta fora de escopo.
