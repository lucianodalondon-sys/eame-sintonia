# C10.6C — O CONTRATO DURÁVEL É DO SCRAP INTEIRO, NÃO DE UM REEL

`C10_6C_RUNTIME_CONVERGENCE = BLOCKED_ARCHITECTURE_DECISION`

> O runtime durável comum existe, está no boundary certo e está provado em três
> classes de execução. O que **não** está resolvido, e não podia ser resolvido
> aqui sem improvisar, são **15 portas de produção** que não passam por ele.
>
> ```
> UMA INFRAESTRUTURA COMUM NÃO É PROVADA POR UM ÚNICO ADAPTER USANDO-A.
> E TAMBÉM NÃO É COMUM SE QUINZE PORTAS A CONTORNAM.
> ```

---

## 1 · A PERGUNTA, E A RESPOSTA MEDIDA

«O estado durável provado na C10.6B pertence ao runtime comum do SCRAP, ou ficou
implementado como um caso especial de Instagram/Reel?»

**Ficou como caso especial.** Medido em chamadas, não em alcance:

```
WIRED_CAPABILITIES = 13
COM DURABILIDADE   =  3   (as três de Reel, pelo adaptador do Instagram)
SEM DURABILIDADE   = 10   (5 do YouTube, 5 do adaptador aberto)
```

E o executor, o roteador, o registo e o orquestrador **não conheciam** nenhum
dos donos de durabilidade — nenhum importa `coleta_checkpoint` nem
`rastro_da_coleta`.

### O censo dos adapters

| adapter | declaradas | wired | papel | classe |
|---|---|---|---|---|
| `adaptador_aberto` | 5 | 5 | `rota` | JSON |
| `adaptador_instagram` | 7 | 3 | `executa` | MEDIA |
| `adaptador_youtube` | 7 | 5 | `rota` + `executa` | API |
| `adaptador_facebook` | 4 | **0** | — | — |
| `adaptador_linkedin` | 7 | **0** | — | — |
| `adaptador_x` | 5 | **0** | — | — |
| **total** | **35** | **13** | | |

Vinte e duas capacidades declaradas não têm rota. Não se inventou fluxo para
nenhuma delas.

    DECLARED CAPABILITY != WIRED CAPABILITY != OBSERVED FLOW.

**A primeira versão deste censo mediu alcance transitivo de `import`** e disse
que o YouTube tinha durabilidade. Tinha `import coleta_checkpoint` — para
`hash_da_entrada` e `identidade_valida`, dois ajudantes de identidade. Nunca
chamou `coletar`, `executar_unidade` nem o driver durável.

    UMA SONDA QUE MEDE ALCANCE TRANSITIVO MEDE O QUE PODE, NÃO O QUE FAZ.

---

## 2 · O BOUNDARY, E POR QUE É ESTE

```
COMMON_DURABILITY_BOUNDARY = coleta/scrap_executor.py :: COLLECT()
```

Os cinco critérios, um a um:

| critério | `COLLECT` |
|---|---|
| conhece a execução real | sim — é ele que corre o `CHECK` e decide se despacha |
| não inventa semântica de plataforma | sim — só dispacha; a unidade de trabalho **pergunta** ao adapter |
| cobre todas as capacidades canônicas | sim — `executa` e `rota` passam os dois por aqui |
| não cria um segundo owner | sim — chama `coleta_checkpoint` e `rastro_da_coleta` |
| não regista etapa que nunca ocorreu | sim — escreve **uma** etapa: o `CHECK` que ele próprio atravessa |

O quinto é o que decidiu o desenho. `COLLECT` não sabe se houve `FETCH` — logo
não o escreve.

    NÃO SE FABRICA ETAPA. QUEM NÃO ATRAVESSOU NÃO RELATA.

O que ele faz é entregar o **relator** a quem o saiba receber — medido na
assinatura, nunca suposto. Quem o recebe reporta os seus degraus; quem não o
recebe não produz linhas, e essa ausência é honesta.

---

## 3 · O QUE FICOU DE CADA LADO

| do lado do adapter | do lado da casa |
|---|---|
| `unidade_do_pedido` — o que é uma unidade retomável desta plataforma | abrir a RUN |
| o `etapa=` que a cadeia dele usa para relatar | abrir o checkpoint, quando há unidade |
| o veredito da unidade, em `CANONICAL_STATE` | escrever o `CHECK` |
| | fechar a RUN com o estado medido |

    A UNIDADE DE TRABALHO É A ÚNICA COISA QUE SÓ O DONO DA PLATAFORMA
    PODE DIZER. O RESTO DA DURABILIDADE É DA CASA.

### Checkpoint só quando há metade feita

`RUN_REQUIRED`, `STAGE_TRACE_REQUIRED` e `CHECKPOINT_REQUIRED` são três coisas
diferentes. «Resolver um canal pelo nome» não tem metade feita: ou resolveu, ou
não. Um checkpoint `CONCLUIDO` numa operação repetível trancá-la-ia para sempre
com `JA_CONCLUIDO_NAO_PAGAR_DUAS_VEZES`.

    FABRICAR RETOMADA ONDE NÃO HÁ NADA A RETOMAR NÃO AUMENTA COBERTURA.
    TRANCA A PORTA.

Hoje só o Instagram declara unidade. As dez do YouTube e do adaptador aberto
ganham RUN e rastro, e **não** ganham checkpoint — porque nenhuma declarou uma
unidade retomável, e declarar por elas seria inventar.

### O veredito sobe na língua do dono

Um objeto ter voltado não quer dizer que a unidade ficou feita. O executor não
sabe ler `TRANSCRIPT_STATE`, e adivinhar seria inventar semântica de plataforma.
Então o adapter escreve `trace['CANONICAL_STATE']` com uma palavra de
`leis/falhas.py`, e o executor **recusa** qualquer palavra que o dono não
declare.

| o que o Reel mediu | palavra canônica | estado da corrida |
|---|---|---|
| texto com pai preservado | `OK` | `concluida` |
| texto sem pai preservado | `PARTIAL_RESULTS` | `parcial` |
| ouviu e não havia fala | `ZERO_RESULTS` | `vazia` |
| não conseguiu ouvir | `ITEM_ERROR` | `parcial` / `falhou` |

---

## 4 · UM PORTÃO QUE RECUSA NÃO FALHOU

O `CHECK` fecha em `SKIPPED`, não em `FAIL`. `FAIL` diria que o próprio CHECK
rebentou; o que houve foi ele correr, medir e responder «não dá».

E há prova disso no schema, não na opinião: `falha_tem_codigo` exige
`diagnostic_code` em toda linha `FAIL`, e `leis/diagnostico.py` **não tem código
para `CHECK`**. Não tem porque `CHECK` não falha — ele responde.

    UM PORTÃO QUE RECUSA NÃO FALHOU. ELE FEZ O SEU TRABALHO.

O estado da corrida, nesse caso, sai de `leis/falhas.e_falha()`: «não tenho
credencial» é falha; «esta rota não é permitida» não é — é a política a
funcionar, e uma corrida que a respeitou não falhou.

---

## 5 · A PROVA — TRÊS CLASSES, UM BOUNDARY

PostgreSQL 16.13 descartável, migrations 001–026, **zero rede**.

| capacidade | classe | RUN | checkpoint | etapas |
|---|---|---|---|---|
| `instagram.reel.capture` | MEDIA (`executa`) | `concluida` | sim | `CHECK/PASS · FETCH/SKIPPED · RAW/PASS · DERIVED/…` |
| `youtube.search` | API (`rota`) | `concluida` | não | `CHECK/PASS` |
| `mastodon.hashtag.search` | JSON (`rota`) | `concluida` | não | `CHECK/PASS` |

### Crash cross-adapter

As três mortas no mesmo ponto, com `os._exit(97)`:

```
MEDIA  exit=97 · RUN=rodando · checkpoint=sim · CHECK/PASS
API    exit=97 · RUN=rodando · checkpoint=—   · CHECK/PASS
JSON   exit=97 · RUN=rodando · checkpoint=—   · CHECK/PASS

CROSS_ADAPTER_CRASH_PROOF = PROVEN
```

    A PROVA DE QUE A INFRAESTRUTURA É COMUM É ELA PARTIR-SE IGUAL EM TODAS.

### Isolamento e concorrência

Cada plataforma na sua RUN, zero checkpoints partilhados entre plataformas. Vinte
rondas de dois processos: zero linhas de etapa duplicadas, zero corridas por
fechar, zero deadlocks, zero falhas de serialização.

---

## 6 · O QUE BLOQUEIA — E É UMA DECISÃO DE GENTE

O censo de bypass mediu **27 caminhos** que executam capacidade sem passar pelo
boundary. Separando invocação de menção, como a C10.4C obriga:

```
BYPASS_PATHS                 27
  invocações vivas           15   (workflow_dispatch → implementação)
  verificações de presença    4   (`[ -f ... ]`, não são portas)
  CLI próprio das implementações  8
PRODUCTION_BYPASSES_REMAINING = 15
```

Os 15 são as fases do `sintonia-scrap.yml` e do `scrap-social.yml`: `janela`,
`diario`, `yt-canais`, `yt-objetos`, `yt-legendas`, `yt-relevancia`,
`yt-transcrever` e companhia. Elas correm `coleta/instagram_janela.py`,
`coleta/youtube_janela.py`, `coleta/youtube_oficial.py` — as **implementações** —
e nunca tocam em `scrap_executor.COLLECT`.

    A C10.4B JÁ TINHA ESCRITO: ZERO IMPORTADORES PYTHON NÃO SIGNIFICA ZERO
    PORTAS. AQUI É O INVERSO E A MESMA LEI: UM BOUNDARY COM TRÁFEGO NÃO
    SIGNIFICA UM BOUNDARY ÚNICO.

Rewirear 15 fases operacionais para entrarem por `COLLECT` muda a superfície
operacional inteira da casa. É exactamente o que a missão manda **não**
improvisar — e por isso o veredito não é `PASS`.

```
C10_6C_RUNTIME_CONVERGENCE = BLOCKED_ARCHITECTURE_DECISION

O QUE FALTA DECIDIR    as 15 fases do workflow passam a entrar por COLLECT?
QUEM DECIDE            gente
O QUE JÁ ESTÁ PRONTO   o boundary, os três donos ligados, a prova nas três
                       classes, o crash cross-adapter, a concorrência
O QUE NÃO É PRECISO    migration nenhuma, contrato novo nenhum
```

**A primeira versão do ataque 6 procurou adapters nos workflows e achou zero** —
porque os workflows não chamam adapters, chamam implementações.

    UM ZERO SÓ VALE SE A SONDA ESTIVER A OLHAR PARA O SÍTIO.

---

## 7 · MUTAÇÃO E RED TEAM

```
MUTANTS = 12   SURVIVORS = 0
ATTACKS = 25   POSITIVE_FINDINGS = 15   (todos o mesmo bypass da §6)
```

Quatro mutações sobreviveram à primeira bateria, e cada uma pagou uma sentinela:

| mutação | por que sobreviveu | o que a mata agora |
|---|---|---|
| M2 · `CHECK` corre antes de a etapa abrir | nada exigia a ordem | `test_4b`, que mede a posição na árvore |
| M4 · excepção fecha a RUN como sucesso | a prova nunca levantava | `test_15`, que lê o ramo `except` |
| M7 · sobrescrever a tentativa 0 | eu corria só a prova nova | a bateria passou a exigir **as duas** provas |
| M10 · unidade para capacidade sem rota | `test_8` só olhava a plataforma | `test_8b`, que exige rota |

    UMA MISSÃO NOVA NÃO DISPENSA A PROVA DA ANTERIOR.

E o ataque 18 encontrou um defeito real: o ramo de excepção fechava a etapa em
`FAIL` com o erro e o código certos, e sem tocar em balde nenhum — entrada 1,
destino zero. O conserto lê o número da própria linha, não o adivinha.

    NÃO É OBRIGATÓRIO QUE 100% CHEGUE AO FIM.
    É OBRIGATÓRIO QUE 100% TENHA EXPLICAÇÃO.

---

## 8 · O QUE NÃO MUDOU

- `leis/social_matriz.py` intocado. `INSTAGRAM/FETCH_TRANSCRIPT` continua
  `ROUTE_NOT_ALLOWED` — e é por isso que a classe MEDIA se prova por
  `instagram.reel.capture`, que tem `executa`, e não por `transcribe`, que o
  roteador recusa. **Isso é a política a funcionar**;
- nenhuma migration, nenhum checkpoint paralelo, nenhuma segunda telemetria,
  nenhum segundo dono de falha;
- Admission, Source Relevance, Intelligence, Portal e Supabase LIVE intocados;
- nenhuma relevância temática entrou no SCRAP;
- `SOURCE_ID`, `DOCUMENT_ID`, SHA e `RUN_ID` continuam a não ser identidade um
  do outro.

### Dívidas declaradas

1. **Os 15 bypasses da §6** — a decisão de arquitetura que bloqueia esta missão.
2. **Liveness de uma RUN** — herdada da C10.6B, §8 daquele documento. Continua a
   exigir migration.
3. **`COLLECT` não passa o relator às implementações que os workflows correm** —
   consequência da 1, não causa: elas não entram por aqui.

---

## 9 · VEREDITO

```
C10_6C_RUNTIME_CONVERGENCE = BLOCKED_ARCHITECTURE_DECISION

ADAPTERS = 6   DECLARED = 35   WIRED = 13   OBSERVED_OFFLINE_FLOWS = 3
COMMON_DURABILITY_BOUNDARY = coleta/scrap_executor.py :: COLLECT
BYPASSES_BEFORE = 27   BYPASSES_AFTER = 27   PRODUCTION_BYPASSES_REMAINING = 15
POSTGRES 16.13 · DISPOSABLE = YES · LIVE_TOUCHED = NO
CROSS_ADAPTER_CRASH = PROVEN (3 classes, exit 97, mesma forma)
CONCURRENCY: 20 rondas · 0 corridas duplicadas · 0 deadlock
MUTANTS = 12 · SURVIVORS = 0
ATTACKS = 25 · 15 achados, todos o mesmo bypass
TESTS_BEFORE = 2341 · TESTS_AFTER = 2359 · NEW_FAILURES = 0
SYSTEM_MAP: 7 REGERAR + 1 VALIDAR (lidos do ficheiro) · PASS
NETWORK_REAL = 0 em todas as plataformas · COST_USD = 0
```

**O runtime durável comum existe e está provado. A convergência não está
fechada, e fechá-la é uma decisão de gente.**
