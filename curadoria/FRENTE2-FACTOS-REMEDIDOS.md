# FRENTE 2 — OS 5 FACTOS, REMEDIDOS ANTES DE USAR

Medição própria em 2026-09-22 ~19:30 local (UTC−3), na bancada `ponte-curador-v1`.
O briefing pediu para remedir. **Dois factos não confirmam.**

> ⚠️ **ARMADILHA DE FUSO, que quase me fez concluir mal.** O `OBSERVED_AT` dos
> livros está em **UTC**; o `LastWriteTime` do sistema de ficheiros está em
> **local (UTC−3)**. Li transições «das 19:11» num ficheiro «escrito às 16:15» e
> por um momento pareceu haver um escritor fantasma a gravar no passado. Não
> havia: 19:11 UTC *é* 16:11 local. **Comparar dois relógios sem os converter
> inventa um fantasma** — e um fantasma inventado leva a procurar um processo
> que não existe.

---

## FACTO 1 — ⚠️ NÃO CONFIRMA: o supervisor está MORTO

O briefing diz «Supervisor vivo PID 110748».

```
SUPERVISOR.lock   {"PID": 110748, "STARTED_AT": "2026-09-22T21:58:49Z"}
PID 110748 existe?  FALSE
processos python a correr supervisor.py:  NENHUM
```

Arrancou às 18:58:49 local e **a última linha que escreveu foi às 19:03:51**
(`SOURCE-CURATOR-RUN-LOG.ndjson`). Depois disso, nada — e já passaram ~27 min.
Não há linha de paragem, não há erro, não há `PARAR.flag`. **Morreu a meio de
um tick normal, calado, e deixou o lock órfão.**

O último evento registado é um `REALIMENTACAO` vulgar:

```json
{"EVENTO":"REALIMENTACAO","QUEUE_ELIGIBLE":0,
 "FEEDER":{"CANDIDATAS_LIDAS":476,"ENFILEIRADAS":0,"JA_PROCESSADAS_IGNORADAS":476},
 "DECISAO":"DISCOVERY_EM_INTERVALO","AT":"2026-09-22T22:03:51.611585+00:00"}
```

> A lição do briefing era «COMMIT DO CONSERTO != PROCESSO VIVO COM O CONSERTO».
> O que está medido aqui é o degrau seguinte: **RELANÇADO != VIVO AGORA.**
> Ninguém estava a vigiar se ele continuava de pé, e o lock — a única coisa que
> afirma quem é o dono — diz um PID que já não existe.

⚠️ Consequência para esta missão: **não há bot vivo a decidir.** A prova ao vivo
exige relançá-lo (o briefing autoriza: «Relançar e provar PID novo pelo SO»).

## FACTO 2 — confirma: sem combustível, não avariado

Lido no log do próprio supervisor: `CANDIDATAS_POR_QUALIFICAR: 0`,
`DECISAO: DISCOVERY_EM_INTERVALO`, `ENFILEIRADAS: 0` de 476 lidas.
Fila: `DONE 903 · BLOCKED 80 · FAILED 74 · elegíveis 0`.
**Só registo — não é escopo desta missão.**

## FACTO 3 — confirma: ruído de realimentação

`REALIMENTACAO` a cada ~15 s, sempre idêntico: lê 476, enfileira 0.
Contados no log 3 eventos em 30 s → ~5.760/dia. Mesmo padrão do
`DISCOVERY_HOOK_ERRO`: **repetição sem condição nova**.
**Só registo — não é escopo.** Mas é a lição que o desenho desta missão tem de
NÃO repetir (ver ponto C do briefing).

## FACTO 4 — ✅ CONFIRMA, e é o elo a fechar

```
livro do bot NO DISCO  : 1275 transições
livro do bot NO COMMIT : 1270 transições
INVISÍVEL PARA A PONTE :    5 decisões
```

As cinco, todas reais:

```
IT-T7-050  CANARY_PENDING -> RETRY_AFTER   (16:11 local)
IT-T7-051  CANARY_PENDING -> RETRY_AFTER
IT-T7-052  CANARY_PENDING -> RETRY_AFTER
IT-T7-053  CANARY_PENDING -> RETRY_AFTER
IT-T7-058  CANARY_PENDING -> RETRY_AFTER   (16:15 local)
```

Último commit do bot: `41655f3a`, **15:51:35** — há ~3 h 40.

    A PONTE LÊ PELO GIT. O BOT ESCREVE NO DISCO E NÃO COMMITA.
    ENTÃO A PONTE SÓ ATRAVESSA O QUE ALGUÉM GUARDOU À MÃO.

⚠️ **Correção ao briefing (menor):** os ficheiros sujos são **3 de conteúdo**
(`LIFECYCLE-LEDGER`, `LIFECYCLE-EVIDENCE`, `LIFECYCLE-QUEUE`, +131 linhas), mais
`RED-TEAM-TELEMETRIA-V1.json`. `supervisor.py` e `telemetria.py` aparecem no
`git status` mas **o diff é vazio**: mudou-lhes a data, não o conteúdo. Não
houve edição de código do supervisor por baixo dele.

## FACTO 5 — confirma: as lanes divergiram

```
merge-base      8bbea01c  (supervisor: corrigir offset de fuso no boot time)
só na ponte          114 commits
só no service         20 commits
curadoria/supervisor.py   DIFERENTE: +98 / −77 linhas
```

E o ponto de partida desta missão, medido: os únicos que importam
`reconciliar_livros` são **`medir_fila_do_bot.py`, `provar_ponte_curador.py` e
dois ficheiros de teste**. **Zero chamadores de produção.** A ponte só corre se
alguém a mandar correr.

---

## O QUE ISTO MUDA NO DESENHO

1. **Um hook dentro do supervisor do service está fora**, e não por preferência:
   o `supervisor.py` das duas lanes difere em 175 linhas, a lane do bot tem 20
   commits próprios, e o processo **nem sequer está vivo** para ser instrumentado.
   Pôr código desta lane lá dentro seria o merge cego que o briefing proíbe.
2. **O transporte não pode ser só Git**, porque o Git só vê o que foi commitado
   e ninguém commita o livro do bot. Ou alguém passa a commitar — e isso é
   decisão do dono sobre uma lane viva — ou o transporte muda.
3. **A ponte tem de sobreviver ao bot estar morto.** Hoje o bot morre calado;
   um observador que só funcione com o bot de pé herda o mesmo silêncio.
