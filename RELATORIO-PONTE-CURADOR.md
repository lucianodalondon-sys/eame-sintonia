# RELATÓRIO — PONTE SOURCE CURATOR → COLLECTION V1

**Missão:** `MISSAO-PONTE-CURADOR.md` + reforço do dono (8 pontos).
**Base:** `ponte-curador-v1` @ `42708647`.
**Modelo:** `ACTUAL_LLM_MODEL = claude-opus-5`.
**Data da medição:** 2026-09-22.

> **Objetivo único:** o trabalho do bot de fontes passar a chegar à linha que
> colhe. Ligar o encanamento, não construir cano novo.

---

## 0 · O QUADRO

| chave | valor |
|---|---|
| `EXISTING_BRIDGE_FOUND` | **YES** — `curadoria/reconciliar_livros.py` |
| `DIVERGENTES_RESOLVIDOS` | **63 / 63** |
| `POLICY_BLOCK_PRESERVADOS` | **69** |
| `CAPABILITY_BLOCK_PRESERVADOS` | **28** (17 desta linha + 11 só do bot) |
| `SOURCE_ID_DUPLICATES` | **0** |
| `COLLECTION_ELIGIBLE_ANTES` | **8** |
| `COLLECTION_ELIGIBLE_DEPOIS` | **8** |
| `LEGACY_LEAK` | **0** |
| `RECOLLECTION_UNKNOWN_LEAK` | **0** |
| `RED_TEAM_ATAQUES` / `RED_TEAM_SURVIVORS` | **15 / 0** |
| `PONTE_VIVA` (prova de runtime) | **TRUE** |
| `IDEMPOTENCIA_NO_OP` | **TRUE** |
| `NEW_FAILURES` | **0** (base 377 vermelhos → final 376) |
| `SYSTEM_MAP_CHECK` | **PASS** (a base chegava `FAIL` com 2) |
| `BIG_COLLECTION_ALLOWED` | **NO** — a missão proíbe; nada foi corrido |

---

## 1 · FASE 0 — ANTI-COLISÃO

O supervisor do bot **está vivo e não foi tocado**:

```
PID 111952  py.exe curadoria/supervisor.py         (pai)
PID 107504  python.exe curadoria/supervisor.py     (filho)
nascidos    2026-09-21 21:43:34
```

Confirmado o que o dono mediu: **pai e filho, um só serviço, um só lock**. Não
há concorrência e nada foi morto.

O livro do bot leu-se **sempre por cópia congelada** (`git show`), nunca o
ficheiro vivo — que pode estar a meio de uma gravação. Verificado: o ficheiro
vivo e o commit são idênticos (1008 transições nos dois).

### O corte lógico (ponto 2 do reforço)

```
BOT_SNAPSHOT_HEAD           216dd6db   (branch source-curator-service-v1)
BOT_SNAPSHOT_TIME           2026-09-22T05:19:45.589187+00:00
BOT_SNAPSHOT_TRANSITION_MAX_ID  1008
BOT_SNAPSHOT_SOURCES        437
```

O que o supervisor escrever **depois** deste corte não entra retroativamente:
atravessa na volta seguinte da ponte.

---

## 2 · FASE 1 — A PONTE JÁ EXISTIA

`EXISTING_BRIDGE_FOUND = YES`.

`curadoria/reconciliar_livros.py` (795 linhas) já reconciliava três livros por
`SOURCE_ID`, preservava bloqueios pela evidência e evoluía o livro canónico por
acréscimo via `lifecycle.registar`. **Não se construiu ponte nova.** O que
faltava era o bot estar ligado a ela.

| dono | quem escreve / quem lê |
|---|---|
| `BOT_LEDGER_OWNER` | `curadoria/supervisor.py` → `worker.py` → `lifecycle.registar`, na worktree do bot |
| `COLLECTION_LEDGER_OWNER` | `collection_gate.avaliar()`, que lê **o livro e o manifesto de provas desta árvore** |
| `ROTA_EXISTENTE` | `reconciliar_livros.py`, com livros `A` (aqui), `B` (`f98f234c`), `B2` (`63b71421`) — **nenhum deles o bot** |

**O enxerto:** o bot entrou como **livro `C`**, pelas mesmas leis dos outros.
Trazido ficheiro a ficheiro, aditivo, sem um único `git merge` — a direção
travada foi respeitada: `collection_gate.py`, `ready_split.py`,
`reconciliar_livros.py`, `incrementalidade.mjs` e `executor_texto_de_html.py`
continuam intactos e só existem deste lado.

---

## 3 · FASE 2 — OS 63 DIVERGENTES, UM A UM

Medição confirmada exatamente como o dono a tinha feito (437/1008 contra
278/754; só-bot 277, só-aqui 118, ambos 160, divergentes 63).

| Collection → Bot | n | régua usada | estado final | porquê |
|---|---|---|---|---|
| `READY` → `RECONCILIATION_REQUIRED` | 41 | razão da linha + prova dos 4 passos | **READY (mantém)** | o bot **pediu** remedição às 20/09 22:45; esta árvore remediu às 21/09 15:20 |
| `RETRY_AFTER` → `RECONCILIATION_REQUIRED` | 9 | idem | **RETRY (mantém)** | o mesmo pedido, já cumprido |
| `READY` → `CAPABILITY_BLOCK` | 4 | superação na própria história | **READY (mantém)** | bloqueio de 20/09 22:54 **superado** por contrato escrito + canário a 21/09 |
| `CANARY_PENDING` → `READY` | 6 | prova de canário exigida | **CANARY_PENDING (mantém)** | promoção do bot **sem prova** |
| `CONTRACTED_CANARY_FAILED` → `READY` | 2 | idem | **CANARY_FAILED (mantém)** | idem |
| `UNKNOWN` → `RETRY_AFTER` | 1 | formato de identidade | **UNKNOWN** | `IT-PROVA-RETRY` não é fonte: é linha de prova |

**Resultado: nenhum dos 63 mudou o estado desta linha** — e isso não é
teimosia, é o que a prova diz. Em todos os casos esta árvore mediu **depois**,
e nos 8 em que o bot mediu uma promoção, a prova não existe.

### Os 41 — o caso central

O `RECONCILIATION_REQUIRED` do bot não era um veredito contrário. Era um
**pedido**, com a razão escrita na linha:

> *«bloqueio medido contra `feeds/videos.xml`; a integração deu rota nova —
> remedir lá»*

Esta árvore remediu 16 h depois. Um estado que pede trabalho não contradiz
quem fez o trabalho.

### Os 4 `CAPABILITY_BLOCK` — bloqueio que cede, sem ser por omissão

A lei «bloqueio provado não desaparece por omissão» ficou inteira. Estes 4
não cederam por omissão: cederam a **prova posterior na própria história da
fonte**. O bloqueio do bot nasceu de um defeito do worker dele (*«contrato
reprovado: campos em falta»*, marcado por ele como `RETIFICACAO`); depois o
contrato foi escrito em condições e o canário abriu um item real.

Registado em `BLOCKS_SUPERSEDED_BY_LATER_EVIDENCE` (8 linhas).
`IT-T5-041` é o caso vivo: é uma das 8 elegíveis e o bot chamava-lhe bloqueada.

### As 8 promoções do bot — prova que não resolve

Todas citam o mesmo identificador:

```
MISSAO-04:curadoria/READY-FOR-COLLECTION-V1.json@959ae46a
```

Que **não é uma linha do manifesto de canários do próprio bot** (1135 provas).
Resolve para nada: zero campos, nenhum item aberto, nenhum gate. Recusadas, e
nomeadas uma a uma na telemetria:

```
IT-T10-020 · IT-T12-009 · IT-T12-013 · IT-T2-030
IT-T5-039  · IT-T7-031  · IT-T7-041  · IT-T8-008
```

---

## 4 · FASE 3 — AS 277 QUE SÓ O BOT CONHECIA

Não entraram em bloco: entraram com a **cadeia inteira de transições** e
proveniência (`IMPORTADO_DE`: livro, commit, chave original, instante original).

```
NOVAS_LEGITIMAS         277 (211 com SOURCE_ID · 66 candidatas CAND-*)
JA_CONHECIDAS_OUTRO_ID    0   — SOURCE_ID_DUPLICATES = 0
SEM_EVIDENCIA           registadas no estado que o bot lhes deu, nunca READY
```

Estados com que chegaram:

```
CONTRACTED_CANARY_FAILED  107      SEMANTIC_REVIEW              55
RETRY_AFTER                69      READY_FOR_COLLECTION         22
CONTRACT_READY_ROUTE_BLOCKED 13    CAPABILITY_BLOCK             11
```

As 66 candidatas `CAND-*` não criaram identidades novas: quem já tinha
`SOURCE_ID` no Atlas entrou como alias da mesma fonte.

11 bloqueios do bot ficaram marcados `BLOCKS_REJECTED_AS_STALE` — candidatas
ausentes da porta desta árvore, logo sem prova local. Importou-se o **estado**
do bot com proveniência, mas nunca como prova desta casa.

---

## 5 · FASE 4 — O ENCANAMENTO, LIGADO E PROVADO

### O defeito que quase passou: o estado sem a prova não atravessa

A ponte importava os estados corretamente — e teria ficado verde na mesma
assim. Mas `collection_gate` **não lê o livro do bot**: lê o manifesto de
provas desta árvore. Uma fonte importada como `READY` cuja prova ficou do
outro lado é lida como `NUNCA_PROMOVIDA` e nunca seria elegível.

Corrigido: a ponte passa a trazer a prova junto com o estado.

```
PROVAS_CITADAS_DE_C              485
PROVAS_IMPORTADAS                485
COLISOES_NAO_IMPORTADAS            0   (35 refs comuns, todas iguais byte a byte)
PROVAS_NO_MANIFESTO   65  ->     550
```

### O que o livro canónico ficou

```
                        ANTES     VOLTA 1    VOLTA 2 (trabalho novo do bot)
fontes no livro           278         555        555
transições                754        1450       1523
acrescentadas               —        +696        +73
cadeias ilegais             —           0          0
segunda passagem planeia    —           0          0   ← idempotente
```

Tudo por **acréscimo**: nenhuma linha existente foi reescrita, e cada linha
importada leva `IMPORTADO_DE` (livro, commit, chave original, instante
original) ou `RECONCILIACAO` (a decisão, a prova e o commit dela).

### A prova ao vivo, nos dois sentidos (ponto 7 do reforço)

`curadoria/provar_ponte_curador.py`, em bancada descartável — o livro real não
foi tocado por esta prova:

```
BOT_HEAD_LIDO_AGORA   216dd6db   (descoberto, não escrito à mão: TRUE)

POSITIVA  IT-T99-001  ausente -> READY_FOR_COLLECTION | régua DETAIL/v1
                      COLLECTION_ELIGIBLE = True | ATRAVESSOU = True
NEGATIVA  IT-T99-002  CAPABILITY_BLOCK  -> NÃO ATRAVESSOU
NEGATIVA  IT-T99-003  READY sem prova   -> UNKNOWN -> NÃO ATRAVESSOU

PORTÃO    ANTES 8  DEPOIS 9  ENTRARAM ['IT-T99-001']
PONTE_VIVA = TRUE
```

**O trabalho futuro do bot passa a chegar sozinho.** E a ponte lê o `HEAD` da
branch dele em cada corrida — não um commit escrito à mão, que estaria morto
no dia seguinte.

### O número honesto

```
COLLECTION_ELIGIBLE_ANTES  = 8
COLLECTION_ELIGIBLE_DEPOIS = 8
```

**Não subiu, e não foi forçado a subir.** `READY_TOTAL` passou de 87 para 109,
mas nenhuma das 22 `READY` que o bot trouxe tem `DETAIL_GATE_PASSED` na prova:
todas entraram como `READY_LEGACY`, que não é elegível por omissão. O portão
mordeu — que é o que ele existe para fazer.

As 8 são as mesmas de antes:
`IT-T10-018 · IT-T10-022 · IT-T5-041 · IT-T5-049 · IT-T7-017 · IT-T7-033 · IT-T7-042 · IT-T7-043`

### Telemetria do funil (ponto 6 do reforço) — recusas não escondidas

```
BOT_READY                40
CANONICAL_RECONCILED    437
BOT_READY_ACEITES        32
BOT_READY_RECUSADAS       8
RECUSAS_POR_MOTIVO   { PROMOCAO_SEM_PROVA_DE_CANARIO: 8 }
LEGACY_LEAK               0
```

### As duas leis do reforço, medidas

**`SOURCE_CURATOR_READY != COLLECTION_ELIGIBLE`** — o bot nunca escreve
elegibilidade. Medido por AST: um teste reprova se `COLLECTION_ELIGIBLE` for
atribuído em qualquer ponto da reconciliação.

**`RECOLLECTION_UNKNOWN_LEAK = 0`** — a recollection é um **segundo portão**,
e nenhuma fonte ganhou passagem por o bot a aprovar. A ponte não escreve em
`regras/` nem em contrato nenhum (só no livro e no manifesto de provas), e isso
está travado por teste. Prova de que os portões são mesmo independentes: das
8 elegíveis, **só 3** passam também a recollection —

```
DECLARADA (MUTABLE)          3   IT-T10-022 · IT-T7-017 · IT-T7-042
BLOCKED_FOR_BIG_COLLECTION   5   DETAIL_CONTENT = UNKNOWN
```

---

## 6 · FASE 5 — RED TEAM

`curadoria/red_team_ponte_curador.py`. Protocolo `§165` cumprido à letra:
`PYTHONDONTWRITEBYTECODE=1`, `__pycache__` limpo **ao aplicar e ao restaurar**,
diff provado em bytes, execução do mutante provada relendo o ficheiro, e
âncoras **sem `\n`** (os ficheiros estão em CRLF — um padrão com `\n` nunca
casaria e o ataque «passaria» sem ter acontecido).

```
ATAQUES 15   MORTOS 15   SURVIVORS 0
```

| ataque | lei desligada | morto por |
|---|---|---|
| RT-A1 | o bot sobrescreve o canónico | suite |
| RT-A2 | promoção sem prova de canário passa | suite |
| RT-A3 | `READY_LEGACY` lavada para `CURRENT` | suite |
| RT-A4 | `POLICY_BLOCK` some por omissão | suite |
| RT-A5 | fonte só do bot desaparece | suite |
| RT-A6 | fonte só da Collection desaparece | suite |
| RT-A7 | `SOURCE_ID` duplicado passa | suite |
| RT-A8 | a ponte apaga em vez de acrescentar | suite |
| RT-A9 | reconciliação sem proveniência | suite |
| RT-A10 | o portão deixa de morder | suite |
| RT-A11 | o portão ignora revisão humana | suite |
| RT-A12 | a régua aceita capa como item | suite |
| RT-A13 | **ponte presa a um commit fixo** | suite |
| RT-A14 | **a prova do bot não atravessa** | prova ao vivo |
| RT-A15 | colisão de prova sobrepõe a local | suite |

### Os três que sobreviveram à primeira volta

Nenhum foi dispensado como «equivalente»:

1. **RT-A13** — congelar o `HEAD` do bot numa constante **não parte nada hoje**,
   porque a constante e o `HEAD` real são o mesmo valor. Seria um mutante
   equivalente *até o bot avançar* — e nesse dia a ponte deixaria de ver
   trabalho novo em silêncio, com tudo verde. Corrigido (lê a branch) e o teste
   novo pergunta o `HEAD` de outra referência: se devolvesse a constante,
   morria.
2. **RT-A15** — faltava a guarda de colisão de provas. Escrita, com teste que
   força uma colisão sintética.
3. **RT-A2** — âncora ambígua: o ataque **não tinha acontecido**. Reportado como
   `ANCORA_AMBIGUA`, nunca como passe. Depois de a tornar única, sobreviveu
   outra vez — porque há uma segunda barreira a jusante. Mediu-se então a lei
   onde ela vive: `veredito_c`, por si, não pode dizer `READY` sem prova.

---

## 7 · FASE 6 — REGRESSÃO, MAPA

### `NEW_FAILURES = 0`

Comparado **por nome**, nunca por contagem — a contagem engana (módulos que nem
carregam somam 1 cada). Base medida numa worktree limpa do commit `42708647`, e
o estado final medido depois de tudo entregue. **Nunca em paralelo:** duas
medições ao mesmo tempo mentem.

```
BASE  (42708647)   2946 testes corridos   377 vermelhos
FINAL              2961 testes corridos   376 vermelhos

NEW_FAILURES  0
CURADOS       1   (test_o_controle_separa_lei_de_mencao::M5 — ponto fixo do
                   carimbo, alcançado pela regeneração da cadeia)
```

> Os 377 vermelhos da base são pré-existentes de ambiente e **não** foram
> tocados por esta missão. O número que interessa é o conjunto de nomes: não
> apareceu nenhum nome novo.

Houve **um** vermelho novo a meio do trabalho, e era meu: o teste dos livros
reais afirmava `TRANSITION_MAX_ID == 1008`. O supervisor do bot escreveu mais
119 transições durante a missão e o número passou a 1127 — fixar a fotografia
de um serviço que está a correr garante um vermelho no dia seguinte que não
significa defeito nenhum. Reescrito para afirmar **leis** (append-only nunca
encolhe; nenhum `READY_CURRENT` sem `BODY_UTIL` provado) em vez de contagens.

### `SYSTEM_MAP_CHECK = PASS`

Pela cadeia (`REGERAR` → `VALIDAR` → `PORTOES_POS_COMMIT`), nunca à mão.

```
CADEIA=OK · REGERAR            (20 passos)
SYSTEM_MAP_CHECK=PASS · o mapa corresponde ao repositorio
IMPRESSAO_DO_CARIMBO=IGUAL · sobre 2611 ficheiros-fonte
```

⚠️ **A base já chegava vermelha aqui:** `42708647` dava
`SYSTEM_MAP_CHECK=FAIL` com **2** provas reprovadas, por código sem peça no
mapa (`provas/recollection_red_team_estrito.mjs`, da missão anterior). Ficou a
**0** — a pendência herdada foi declarada, não contornada.

Não partidos: `collection_gate` · incrementalidade · recollection · Admissão ·
Sala · contratos. A ponte só escreve em dois caminhos —
`curadoria/LIFECYCLE-LEDGER-V1.json` e `curadoria/LIFECYCLE-EVIDENCE-V1.json` —
e isso está travado por teste.

---

## 7-B · A PONTE APANHOU TRABALHO NOVO REAL, SOZINHA

O melhor resultado desta missão não foi planeado. **A meio do trabalho, o
supervisor do bot voltou a produzir**: o `HEAD` dele passou de `216dd6db` para
`e26de5e2`, e o livro de 1008 para **1127 transições**.

Como a ponte lê o `HEAD` da branch em cada corrida — e não um commit escrito à
mão — a volta seguinte **apanhou esse trabalho sem ninguém lhe tocar**:

```
volta 1   livro 754 -> 1450   (+696)   snapshot 216dd6db · 1008 transições
volta 2   livro 1450 -> 1523  (+73)    snapshot e26de5e2 · 1127 transições
```

Isto não é a prova sintética: é trabalho real do bot a atravessar. O que a
missão pedia no ponto 7 do reforço está cumprido com dados verdadeiros.

Depois da volta 2:

```
READY_TOTAL           109 -> 123        (o bot promoveu mais 14)
READY_CURRENT_TOTAL    10 ->  10
COLLECTION_ELIGIBLE     8 ->   8        as mesmas 8
LEGACY_LEAK                    0
BOT_READY              40 ->  54 · ACEITES 46 · RECUSADAS 8
```

---

## 7-C · UMA NOTA DE HONESTIDADE SOBRE ESTE WORKTREE

A meio da missão apareceu um commit que **não fui eu a fazer**:

```
14e4d4fb  wip: ponte curador — checkpoint antes de virar para materia-prima
          2026-09-22 13:32, mesmo autor configurado
```

Outra sessão a trabalhar **na mesma pasta** congelou o meu trabalho em
progresso num commit intermédio. Conferido ficheiro a ficheiro: **nada foi
alterado nem perdido** — o conteúdo entregue é o mesmo, e está todo em `HEAD`.
Fica dito porque é um risco real desta bancada, não uma curiosidade.

---

## 8 · O QUE FICOU ESCRITO

| ficheiro | o quê |
|---|---|
| `curadoria/reconciliar_livros.py` | livro `C` (o bot), `veredito_c`, `_degrau_c`, corte lógico, telemetria, importação de provas |
| `curadoria/test_reconciliar_livros.py` | 36 testes (13 novos: `RT-C1`..`RT-C15`) |
| `curadoria/provar_ponte_curador.py` | prova de runtime nos dois sentidos |
| `curadoria/red_team_ponte_curador.py` | 15 ataques, protocolo `§165` |
| `curadoria/LIFECYCLE-LEDGER-V1.json` | 754 → 1450 linhas, por acréscimo |
| `curadoria/LIFECYCLE-EVIDENCE-V1.json` | 65 → 550 provas |
| `SINTONIA-EAME-KNOW-HOW.md` | `§168`, 10 subsecções |

---

## EM PALAVRAS SIMPLES

**Havia um robô a trabalhar sozinho, e ninguém lia o caderno dele.**

O robô anda há dias a procurar sítios na Internet onde se pode ir buscar
informação agrícola italiana. Cada vez que encontra um, escreve no caderno
dele. Tinha **437 sítios** apontados.

Do outro lado da casa está a equipa que vai mesmo buscar as coisas. Essa equipa
tem o **seu** caderno, com **278 sítios**. E nunca ninguém tinha aberto o
caderno do robô ao lado do caderno da equipa.

**277 sítios que o robô conhecia não existiam para a equipa.** O robô não
estava parado — estava a escrever para uma gaveta.

### O que fizemos

Não juntámos os dois cadernos à bruta. Juntar cadernos à bruta é como misturar
duas listas de compras e ficar com coisas a dobrar e outras a menos.

Fomos **sítio a sítio**. Em 63 deles os dois cadernos diziam coisas diferentes.
Em cada um perguntámos a mesma coisa: **quem tem aqui uma prova?**

- Em **50**, o robô tinha escrito «isto precisa de ser verificado outra vez».
  Não era o robô a discordar — era um **recado a pedir trabalho**. E esse
  trabalho já tinha sido feito por esta equipa, 16 horas depois do recado. O
  recado estava cumprido.
- Em **4**, o robô dizia «não conseguimos ir buscar isto». Mas depois disso,
  aqui, alguém conseguiu mesmo — e há a prova de uma página aberta a sério.
  Uma porta que estava fechada e foi aberta não continua fechada porque o
  papel antigo diz que estava.
- Em **8**, o robô dizia «isto está pronto». Fomos ver a prova que ele citava…
  **e a prova não existe**. Ele apontou para o nome de um ficheiro antigo, não
  para uma verificação feita. Um carimbo não é uma prova. Esses 8 ficaram como
  estavam.

### Quantos estão prontos agora

**Oito.** Exatamente os mesmos oito de antes.

Isto parece mau e não é. Os 277 sítios novos entraram todos — mas para um sítio
poder ser recolhido, não basta alguém dizer que está bom: é preciso ter havido
uma verificação a sério, em que se abriu uma página real e se confirmou que
tinha texto com conteúdo. **Nenhum dos 22 que o robô dizia prontos tem essa
verificação.** Entraram todos como «ainda por confirmar».

Podíamos ter feito o número subir. Bastava aceitar o carimbo do robô. Seria
mentira, e daqui a um mês alguém descobria que metade não servia.

### O trabalho futuro dele passa a chegar sozinho?

**Sim — e não ficámos pela promessa: aconteceu mesmo, durante o trabalho.**

A meio da missão, o robô voltou a trabalhar por conta dele e escreveu mais
**119 linhas** no caderno. Não fizemos nada. Na passagem seguinte, a ponte foi
ver o caderno **atual** dele — não a fotografia antiga — e trouxe esse trabalho
novo. É a prova de que o cano fica aberto, não uma demonstração montada.

Fizemos também a experiência controlada: pusemos o robô a escrever um sítio
novo, com a verificação completa, e fomos ver se chegava ao fim da linha.
**Chegou** — a lista de prontos passou de 8 para 9 nessa experiência.

E fizemos a experiência ao contrário, que é igualmente importante: pusemos o
robô a escrever um sítio **bloqueado**, e outro com um carimbo sem prova.
**Nenhum dos dois passou.** Uma ponte que deixa passar tudo não é uma ponte, é
um buraco na parede.

### Duas coisas que quase nos escaparam

**A primeira.** Estávamos a trazer o *nome* de cada sítio, mas não a *prova*
dele. É como mudar de casa e levar as etiquetas das caixas sem levar as caixas.
Tudo pareceria certo no papel, e nenhum sítio novo poderia ser recolhido — para
sempre, sem ninguém perceber porquê. Trouxemos as **485 provas** junto.

**A segunda.** A ponte estava a olhar para uma fotografia do caderno do robô,
tirada hoje. Amanhã o robô escreve mais, e a ponte continuaria a olhar para a
fotografia de hoje — **calada, com todos os testes verdes**. Agora ela vai ver
o caderno atual, sempre.

### O robô continua a trabalhar

Não o desligámos em momento nenhum. Lemos uma **fotografia** do caderno dele,
tirada às 05:19 da manhã, e trabalhámos sobre essa fotografia. O que ele
escrever depois disso será recolhido na próxima passagem — não se perde.

E fica uma regra clara: **o robô não decide o que se vai buscar.** Ele traz
conhecimento; quem dá a ordem final continua a ser o porteiro desta casa, que
verifica a prova antes de deixar entrar. Das 8 prontas, aliás, só 3 passam
*também* no segundo porteiro — o que trata de «quando é preciso voltar cá».
Isso não mudou, e o robô aprovar não compra essa passagem.
