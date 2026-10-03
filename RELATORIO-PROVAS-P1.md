# RELATÓRIO — PROVAS-P1: as três provas do Source Curator

Missão: `C:/Users/London1/auditoria-madrugada/MISSAO-PROVAS-P1.md`.
Worktree: `provas-p1`, base `candidate-feeder-v1` (9d3d7461). Sem merge, sem
rebase, sem cherry-pick, sem rede, sem tocar noutras worktrees.
Data: 2026-09-21. Ambiente: Windows 11, bash MSYS, `py` = Python 3.12.

```
BASELINE_TESTES        = 154 OK   (medido aqui: "Ran 154 tests in 10.003s / OK")
TESTES_FINAIS          = 166 OK   ("Ran 166 tests in 11.377s / OK")
NOVOS_TESTES           = 12  (5 em test_supervisor.py · 3 em test_zz_guarda_isolamento.py
                              · 4 em test_worker_volta_sobrevive.py)
DEFEITO_1_MUTACAO_MATA_VERDE = SIM  (4 passos abaixo, saída real)
DEFEITO_2_SUITE_ISOLADA      = SIM  (diff -q e md5 abaixo, nesta árvore e nas 3 lanes)
DEFEITO_3_VOLTA_SOBREVIVE    = SIM  (mutação reprova 3 de 4; restaurado, verde)
FILA_INALTERADA        = SIM  md5 87be1ef3daf531f992b02c6a40963409 antes do baseline e no fim
LEDGER_INALTERADO      = SIM  md5 9e475db922ce22ce739b60c8c0975a89 antes do baseline e no fim
WORKTREE_CLEAN         = SIM  (git status --porcelain vazio depois de cada commit)
HEAD_INICIAL           = 9d3d74616c042caaeaf56d6b29b07dfe7caa28cf
HEAD_FINAL             = 4821e2934a61dac92ad53d6a87e9b59a4317abe8  (código + relatório + mapa)
REMOTE_HEAD            = 4821e2934a61dac92ad53d6a87e9b59a4317abe8  (git ls-remote origin provas-p1;
                          o commit que fecha este relatório fica por cima e é o último push)
NEW_FAILURES           = 0 nesta árvore
NAO_SEI                = (lista na secção própria)
```

Legenda usada em todo o relatório: **FATO MEDIDO** = saída de comando que
corri; **INFERÊNCIA** = o que concluo a partir dos fatos; **NÃO SEI** = sem
prova. `CAN DO != DID DO`.

---

## 0. Baseline (FATO MEDIDO)

Antes de tocar em nada: cópia da fila e do ledger para `$TEMP/provas-p1/`,
md5 dos dois, suíte completa.

```
87be1ef3daf531f992b02c6a40963409 *LIFECYCLE-QUEUE-V1.json
9e475db922ce22ce739b60c8c0975a89 *LIFECYCLE-LEDGER-V1.json
Ran 154 tests in 10.003s
OK
```

md5 dos dois ficheiros **igual** depois da corrida; `git status --porcelain`
vazio. Mas o diário real ficou com as marcas da suíte (FATO MEDIDO, conteúdo
de `SOURCE-CURATOR-RUN-LOG.ndjson` às 09:40):

```
SUPERVISOR_BLOCKED ... ORIGEM SUPERVISOR
TESTE
WORKER_MORTO PID 99999 PROGREDIU true
WORKER_RELANCADO PID 102432
WORKER_RELANCADO PID 57616
WORKER_RELANCADO PID 99324
ARRANQUE VOLTAS_PEDIDAS 0        <- linha escrita por um ciclo_continuo.py REAL
```

Três `ciclo_continuo.py` reais foram lançados pela suíte de baseline. O
`SUPERVISOR-STATE.json` real ficou a dizer `RUNNING` com `WORKER_PID 99324`,
um processo que já não existe.

**Por que o md5 da fila não mudou aqui, ao contrário do que a missão mediu
no feeder (INFERÊNCIA a partir de código lido):** `test_lifecycle.py` faz
`importlib.reload(F)` no `setUp` e não restaura `F.FILA` no `tearDown`;
quando o último teste dele acaba, `F.FILA` fica a apontar para uma pasta
descartável **já apagada**. Os módulos seguintes (`test_nivel...`,
`test_painel...`, `test_ready_split`, `test_supervisor`) guardam esse
caminho morto como "o original". Na suíte **completa**, o
`test_supervisor.py` antigo escrevia numa pasta ressuscitada pelo `mkdir` de
`F._gravar`; só a corrida **isolada** batia na fila real. O estrago na suíte
completa vinha pelo outro canal: o subprocesso real, que precisa de tarefas
PENDING para fazer estrago (aqui a fila não tinha nenhuma).

---

## 1. DEFEITO 2 — a suíte escrevia na fila real (P0) — CORRIGIDO

### O que mudou

`curadoria/test_supervisor.py` (commit 0169d2de):

- classe base `Isolado` com o molde de `test_ready_split.py:44-48`:
  `TemporaryDirectory`, `_antes` guarda `(F.FILA, LC.LIVRO, S.LOCK, S.ESTADO,
  S.PARAR, S.DIARIO)`, restauro no `tearDown`. Não se inventou um segundo molde.
- `TestLock` deixa de ter `unlink` nenhum: o lock é o da pasta descartável.
  Dois testes novos afirmam-no: `test_lock_dos_testes_nao_e_o_real` e
  `test_lock_real_sobrevive_ao_ciclo_adquirir_libertar`.
- **o lançador de worker é substituído** (`mock.patch.object(S,
  "_lancar_worker", ...)`) por um `python -c "time.sleep(60)"`. Razão:
  `uma_volta_sup` lança `ciclo_continuo.py` como processo separado, e esse
  processo importa `fila` por conta própria com o caminho real —
  redirecionar `F.FILA` no processo de teste não o alcança. A adenda
  9d3d7461 já tinha registado este lançamento como dívida.
- cada teste tira o sha256 da fila, do livro, do lock e da bandeira REAIS no
  `setUp` e compara no `tearDown`; se algum mudou, o teste reprova.

`curadoria/test_zz_guarda_isolamento.py` (novo, mesmo commit) — a guarda
permanente:

- **dinâmica**: sha256 de `LIFECYCLE-QUEUE-V1.json`, `LIFECYCLE-LEDGER-V1.json`,
  `LIFECYCLE-EVIDENCE-V1.json`, `italy_contracts_curator.json`,
  `READY-BATCHES-V1.json`, `DISCOVERY-SIGNAL-V1.json`, `SUPERVISOR.lock`,
  `PARAR.flag` tirado **no import** (o `discover` importa todos os módulos
  antes de correr o primeiro teste) e comparado no fim; o `zz` no nome faz
  o módulo correr em último.
- **estática**: lê cada `test_*.py`; quem chama o que escreve na fila tem de
  ter `F.FILA =`; quem chama `LC.registar` tem de ter `LC.LIVRO =`; quem dá
  voltas ao supervisor tem de redirecionar `ESTADO`, `DIARIO` e `F.FILA`;
  quem usa o lock tem de redirecionar `LOCK`; todos com `TemporaryDirectory`.
  A regra é provada contra uma amostra do `test_supervisor.py` antigo
  (`test_2_estatico_a_regra_apanha_o_defeito_original`).

### Gate — nesta worktree (FATO MEDIDO)

`test_supervisor.py` isolado, depois da correção:

```
Ran 24 tests in 11.810s
OK
FILA identica          (diff -q contra $TEMP/provas-p1/q.ante)
LEDGER identico        (diff -q contra $TEMP/provas-p1/l.ante)
87be1ef3daf531f992b02c6a40963409 *LIFECYCLE-QUEUE-V1.json
9e475db922ce22ce739b60c8c0975a89 *LIFECYCLE-LEDGER-V1.json
```

Suíte completa, no fim de tudo:

```
Ran 166 tests in 11.377s
OK
FILA identica · LEDGER identico
87be1ef3daf531f992b02c6a40963409 *LIFECYCLE-QUEUE-V1.json
9e475db922ce22ce739b60c8c0975a89 *LIFECYCLE-LEDGER-V1.json
git status --porcelain: []
```

Prova adicional (FATO MEDIDO): `SOURCE-CURATOR-RUN-LOG.ndjson` e
`SUPERVISOR-STATE.json` reais têm mtime 09:40:56 / 09:40:58 — a hora do
baseline. Nenhuma das corridas posteriores (mais de dez) lhes tocou.

### Gate — as três lanes (FATO MEDIDO, sem escrever nas lanes)

Regra da missão: **não escrever lá**. Correr o `test_supervisor.py` antigo
numa lane é exatamente o ato que a contamina (e lança um worker real que
pode sair à rede). Por isso medi assim: copiei `curadoria/` de cada lane
para `$TEMP/provas-p1/lane-<nome>/`, pus lá o `test_supervisor.py` e a guarda
desta árvore, corri isolado e suíte completa **na cópia**, e comparei a
fila e o ledger da cópia com a cópia de antes. As lanes reais só foram
lidas (md5 antes/depois, `git status`).

| lane | HEAD | real antes → depois | cópia: isolado | cópia: suíte | fila/ledger da cópia |
|---|---|---|---|---|---|
| candidate-feeder-v1 | 9d3d7461 | q `87be1ef3` / l `9e475db9` → **iguais**; git status `[]` | 24 testes, 3 FAIL (os 3 do Defeito 1) | 162 testes, 3 FAIL + 1 ERROR (`test_nivel_da_fila.test_5` lê o disco real fora de `curadoria/`) | **IDÊNTICOS** nas duas corridas |
| candidate-bridge-v1 | 63b71421 | q `4d03d545` / l `94bfd894` → **iguais**; git status `[]` | 24 testes, 3 FAIL (os 3 do Defeito 1) | 119 testes, 3 FAIL + 2 ERROR (`test_discovery`, `test_ponte_candidatas` não importam fora da árvore) | **IDÊNTICOS** nas duas corridas |
| source-curator-supervisor-v1 | 8bbea01c | q `5f3ab0f0` / l `c4df0035` → **iguais**; git status `[]` | 24 testes, 3 FAIL (os 3 do Defeito 1) | 117 testes, 3 FAIL, **0 erros** | **IDÊNTICOS** nas duas corridas |

O supervisor vivo em `source-curator-supervisor-v1` (FATO MEDIDO por
`tasklist`): `python.exe` PID 86172, lock `STARTED_AT
2026-09-21T02:00:13Z`, `TOKEN 6b485703-…`. Vivo antes, vivo depois, lock
com os mesmos bytes.

**A lane `source-curator-supervisor-v1` torna-se mensurável com esta
correção?** INFERÊNCIA a partir da cópia: os 11 `PermissionError WinError 32`
desapareceram (0 erros em 117 testes); ficam 3 FAIL, que são os testes de
acumulação do Defeito 1 a dizer que o `supervisor.py` daquela lane tem o
mesmo defeito do eco no diário. Não alterei a lane. `FAILURE_CLASS = TEST`
continua a valer lá até alguém aplicar a correção **lá**.

### O que a correção NÃO cobre (declarado)

- Os testes deixam de exercitar o lançamento real de `ciclo_continuo.py`.
  Cobertura perdida de propósito; a adenda 9d3d7461 já a tinha classificado
  como dívida, não como prova.
- `test_lifecycle.py` continua a fazer `reload` sem restaurar (ver §0). Não é
  desta missão; a guarda estática passa-lhe porque ele redireciona `F.FILA`;
  a guarda dinâmica apanharia qualquer escrita real que isso viesse a causar.

---

## 2. DEFEITO 1 — o anti-crashloop era verde falso (P1) — CORRIGIDO, e era pior

### O que os testes novos mostraram (FATO MEDIDO)

Escrevi `test_crashloop_tres_mortes_reais_sem_progresso_bloqueia`: o
supervisor lança workers **reais** (`python -c pass`) que morrem sem escrever
no diário; o teste conta "três" por extenso, sem ler `S.CRASH_MAX`. Primeira
corrida, contra o `supervisor.py` original:

```
FAIL: test_crashloop_tres_mortes_reais_sem_progresso_bloqueia
AssertionError: Lists differ:
  ['RELANCADO', 'RELANCADO', 'RELANCADO', 'RELANCADO',
   'RELANCADO', 'RELANCADO', 'RELANCADO', 'RELANCADO']
  != ['RELANCADO', 'RELANCADO', 'RELANCADO', 'BLOQUEADO']
```

**8 mortes seguidas sem progresso, 8 relançamentos, nenhum bloqueio.** A
proteção não estava só mal testada: **não funcionava**.

Causa, lida no código e confirmada por
`test_diario_do_supervisor_nao_e_batimento_do_worker` (FATO MEDIDO: `uma
linha do proprio supervisor contou como batimento`): `_anotar()` escreve
`WORKER_MORTO` e `WORKER_RELANCADO` no **mesmo** `SOURCE-CURATOR-RUN-LOG.ndjson`
que `_ultimo_heartbeat()` lê como batimento do worker. Na morte seguinte, a
última linha do diário é o `WORKER_RELANCADO` anterior — mais novo que
`LAST_PROGRESS_AT` — logo `progrediu = True`, contador a zero, relança.

Correção (commit 78db6886, `supervisor.py`): `_ultimo_heartbeat()` ignora as
linhas com `"ORIGEM": "SUPERVISOR"`. Batimento é só o que o worker escreveu.

Testes novos em `test_supervisor.py`:

- `test_crashloop_tres_mortes_reais_sem_progresso_bloqueia` — sequência
  exata `RELANCADO ×3, BLOQUEADO`; 3 entradas em `CRASHES_SEM_PROGRESSO`;
  `BLOCKED` no ficheiro de estado (descartável).
- `test_crashloop_morte_com_progresso_no_meio_nao_bloqueia` — A e B morrem
  mudos (2), C escreve um batimento e morre (0), D e E morrem mudos (2):
  quatro mortes mudas, nenhum bloqueio, porque nunca foram três seguidas.
- `test_diario_do_supervisor_nao_e_batimento_do_worker`.
- o antigo `test_bloqueado_apos_crash_sem_progresso` passou a
  `test_bloqueado_com_tres_crashes_ja_no_estado` com o número por extenso.

### Gate — os 4 passos (FATO MEDIDO, original guardado em `$TEMP/provas-p1/supervisor.orig.py`)

```
===== PASSO 1: CRASH_MAX 3 -> 99999
57:CRASH_MAX      = 99999
[gate1-passo1] Ran 162 tests in 11.081s -> FAILED (failures=2)
     FAIL: test_bloqueado_com_tres_crashes_ja_no_estado
     FAIL: test_crashloop_tres_mortes_reais_sem_progresso_bloqueia
===== PASSO 2: restaurar
57:CRASH_MAX      = 3
[gate1-passo2] Ran 162 tests in 8.594s -> OK
===== PASSO 3: remover o append a CRASHES_SEM_PROGRESSO
410:            estado.setdefault("CRASHES_SEM_PROGRESSO", []); _descartado = ({
[gate1-passo3] Ran 162 tests in 8.685s -> FAILED (failures=2)
     FAIL: test_crashloop_morte_com_progresso_no_meio_nao_bloqueia
     FAIL: test_crashloop_tres_mortes_reais_sem_progresso_bloqueia
===== PASSO 4: restaurar
144a9ee0976d4b6bdc73d9dbadccebe9 *supervisor.py   (= md5 do original guardado)
[gate1-passo4] Ran 162 tests in 15.500s -> OK
git status --porcelain: só os ficheiros desta missão, ainda por commitar
```

(162 = estado da árvore antes do Defeito 3; `__pycache__` limpo em cada passo.)

---

## 3. DEFEITO 3 — exceção numa etapa matava a volta (P1) — CORRIGIDO

### O que mudou (commit 44751a69)

`worker.py`, `executar_uma`: `try/except Exception` à volta de
`fn(sid, contrato)`. A exceção vira `RETRY` com `PORQUE = "excecao na etapa
<tipo>: <Classe>: <msg>"`, `EXCECAO` e `FONTE_FALHOU` na evidência; o ramo
`RETRY` existente chama `F.adiar(tid, erro=...)` (assinatura confirmada em
`fila.py:201`: `adiar(task_id, *, retry_after_s=None, erro="", agora=None)`),
que incrementa `ATTEMPTS`, marca `NEXT_ATTEMPT_AT` com o backoff da casa e
fecha em `FAILED` ao teto `MAX_ATTEMPTS = 5`. O desfecho devolvido leva
`FONTE_FALHOU`. `BLOCK` continua a ser um resultado devolvido pela etapa,
não uma exceção: `NAO_INSISTIR = {POLICY, AUTH, ROBOTS}` intacto.

`ciclo_continuo.py`, `uma_volta`: a linha `VOLTA` do diário ganha
`FONTES_REBENTARAM` — a separação visível entre FONTE FALHOU e SERVIÇO MORREU.

### Teste novo — `test_worker_volta_sobrevive.py` (tudo em pasta descartável)

1. `test_1_as_tarefas_seguintes_da_mesma_volta_continuam` — chamadas =
   `[IT-X-001, IT-BOOM, IT-X-003]`; 001 e 003 `DONE` e promovidas; BOOM
   `WAITING_RETRY` com `RuntimeError` no `LAST_ERROR` e `EXCECAO` na evidência.
2. `test_2_a_venenosa_incrementa_attempts_e_acaba_failed` — relógio injetado
   (+1 dia por volta): `ATTEMPTS` = 1,2,3,4,5; nunca `IN_PROGRESS`; `FAILED`
   com "teto de 5 tentativas"; uma volta depois, não volta a ser chamada.
3. `test_3_a_volta_com_veneno_e_progresso_para_o_supervisor` —
   `ciclo_continuo.uma_volta` inteira: `TAREFAS_EXECUTADAS 3`,
   `FONTES_REBENTARAM 1`; a seguir o worker morre e `S.uma_volta_sup` lê
   `PROGREDIU true`, `CRASHES_SEM_PROGRESSO == []`, ação `IDLE` (nada
   elegível), sem relançar.
4. `test_4_block_continua_sem_tentativas_novas` — `BLOCK/AUTH` → `BLOCKED`,
   `ATTEMPTS 0`, livro `AUTH_BLOCK`, não reentra.

### Gate — mutação (FATO MEDIDO, original em `$TEMP/provas-p1/worker.fixed.py`)

```
===== COM a correcao
[gate3-com-fix] Ran 4 tests in 1.014s -> OK
===== MUTACAO: tirar o try/except (chamada nua)
297:    resultado, detalhe = fn(sid, contrato)
[gate3-mutado] Ran 4 tests in 0.484s -> FAILED (errors=3)
     ERROR: test_1_as_tarefas_seguintes_da_mesma_volta_continuam   RuntimeError: a fonte rebentou a meio da etapa
     ERROR: test_2_a_venenosa_incrementa_attempts_e_acaba_failed   RuntimeError: a fonte rebentou a meio da etapa
     ERROR: test_3_a_volta_com_veneno_e_progresso_para_o_supervisor RuntimeError: a fonte rebentou a meio da etapa
===== RESTAURAR
e520360b0a06b40efabe82dcdb7f332e *worker.py   (= md5 do corrigido guardado)
[gate3-restaurado] Ran 4 tests in 1.036s -> OK
```

(`test_4` sobrevive à mutação porque `BLOCK` não passa pelo `try` — é
exatamente o que ele afirma.)

---

## 4. Commits

```
0169d2de provas p1: DEFEITO 2 — a suite do supervisor deixa de escrever na fila real
78db6886 provas p1: DEFEITO 1 — o anti-crashloop e provado com mortes reais, e estava morto
44751a69 provas p1: DEFEITO 3 — uma fonte que rebenta nao mata a volta
```

Cada commit foi verificado verde por si: o do Defeito 2 correu contra o
`supervisor.py` original (159 testes OK); o do Defeito 1, 162 OK; o do
Defeito 3, 166 OK. `git status --porcelain` vazio depois de cada um.

Depois destes três:

```
276ede21 provas p1: relatorio — baseline 154, final 166, tres gates com a saida real
4821e293 mapa: regerado pela cadeia canonica sobre a arvore das provas P1 (276ede21)
```

Cadeia do System Map (lei do projeto), FATO MEDIDO: `REGERAR` → `CADEIA=OK`
(20 passos); `VALIDAR` → `SYSTEM_MAP_CHECK=PASS`, P1..P10 PASS, com a
observação já conhecida de `architecture.declared.json` ter dois autores;
`PORTOES_POS_COMMIT` → `CADEIA=OK`. O mapa passou a conhecer os dois
ficheiros de teste novos (40 menções no diff dos gerados).

Push: `git push -u origin provas-p1` criou a branch remota;
`git ls-remote --heads origin provas-p1` = `4821e293…`. O commit que fecha
este relatório (preenche `HEAD_FINAL`/`REMOTE_HEAD`) é o último push.

---

## 5. NÃO SEI

1. **Se o anti-crashloop alguma vez disparou em produção, em qualquer lane.**
   O eco no diário (INFERÊNCIA a partir do código + FATO na pasta
   descartável) diz que não podia; não li os diários reais das lanes para
   confirmar. O `SUPERVISOR_BLOCKED` que aparece no diário desta árvore foi
   escrito pelo teste antigo com a lista injetada, não por mortes reais.
2. **`UnicodeDecodeError` nas threads de leitura do `tasklist`** (aparece no
   baseline e depois): `subprocess.run(..., text=True)` sem `encoding`, com
   `PYTHONUTF8=1` e saída em cp850. Quando acontece, `_pid_no_so` e
   `_proc_e_python` devolvem `False` pela exceção. Não medi o efeito prático;
   não é desta missão.
3. **Por que a missão mediu `PROXIMO_ID 128→133` no feeder e eu não.** A
   explicação em §0 é INFERÊNCIA; o feeder real está hoje a 128, com o mesmo
   md5 desta árvore.
4. **As cópias das lanes** trouxeram só `curadoria/`: 1 ERROR no feeder
   (`test_nivel_da_fila.test_5` lê fora da pasta) e 2 no bridge (módulos que
   não importam fora da árvore) são artefactos da cópia. Não os investiguei.
5. **`test_lifecycle.py` deixa `F.FILA` numa pasta apagada** (§0). Sei que
   acontece por ler o código; não medi que teste, se algum, escreve por causa
   disso — a guarda dinâmica diz que, nesta suíte, ninguém escreveu.
6. Perdi de propósito a prova de que o supervisor consegue lançar o
   `ciclo_continuo.py` verdadeiro. Ninguém a tem agora dentro da suíte.

---

## EM PALAVRAS SIMPLES

Imagina uma padaria com três coisas: um **caderno de encomendas** (a fila),
um **funcionário** que faz as encomendas uma a uma (o worker), e um **chefe**
que fica à porta a ver se o funcionário está vivo e o manda entrar de novo
quando ele desmaia (o supervisor).

Antes desta missão havia três coisas partidas.

**1. O ensaio escrevia no caderno verdadeiro.** Para testar a padaria, alguém
escrevia encomendas de mentira no caderno de encomendas de verdade, e
depois apagava. Só que às vezes o funcionário de verdade lia as encomendas
de mentira e ia mesmo fazê-las — noutra loja igual a esta, 10 encomendas
verdadeiras (em 70) ficaram marcadas como "não dá para fazer" por causa de
um ensaio. E o ensaio ainda arrancava o crachá do chefe da porta, mesmo com
o chefe lá dentro a trabalhar.
**Agora** o ensaio tem um caderno de brincar, numa gaveta à parte, que é
deitado fora no fim. E há um fiscal que tira uma fotografia do caderno
verdadeiro antes do ensaio começar e compara no fim: se um único traço mudou,
o ensaio reprova e diz qual foi a página. Medi isto aqui e em três lojas
irmãs: o caderno verdadeiro ficou igual, traço por traço, todas as vezes.

**2. O chefe nunca ia fechar a loja.** A regra diz: se o funcionário desmaiar
3 vezes seguidas sem ter feito nada, o chefe fecha a loja e chama alguém.
O ensaio antigo "provava" isto entregando ao chefe um papel já a dizer
"desmaiou 3 vezes" — e como o ensaio copiava o número 3 da própria regra,
se alguém mudasse a regra para 99999 o ensaio continuava a dizer que estava
tudo bem. Fiz um ensaio novo em que o funcionário desmaia **a sério** e
contei pelos dedos. E descobri o pior: **o chefe nunca fechava a loja.**
Porquê: o chefe e o funcionário escrevem no mesmo diário. Sempre que o chefe
escrevia "mandei-o entrar de novo", na vez seguinte ele lia essa linha, achava
que tinha sido o funcionário a escrever, e concluía "afinal ele trabalhou".
8 desmaios seguidos, 8 vezes mandado entrar, loja nunca fechada.
**Agora** o chefe só conta como sinal de vida o que o **funcionário**
escreveu. Ensaio: 3 desmaios, loja fechada; 3 desmaios com um bocadinho de
trabalho pelo meio, loja aberta. E testei ao contrário: mudei a regra para
99999 e o ensaio reprovou; tirei o contador e o ensaio reprovou; repus e
voltou a passar.

**3. Uma encomenda estragada parava o dia inteiro.** Se uma encomenda
rebentasse nas mãos do funcionário, ele desmaiava, deixava as encomendas
seguintes por fazer, e a estragada ficava marcada "a fazer" para sempre. Como
ele desmaiava sem escrever nada no diário, o chefe contava isso como
"desmaiou sem trabalhar" — três encomendas estragadas num par de minutos e a
loja fechava por culpa das encomendas, não do funcionário.
**Agora** a encomenda estragada é posta de lado com uma nota ("rebentou:
tal motivo"), ganha um risco na contagem de tentativas, e depois de 5 riscos
é dada como perdida. O funcionário segue para a seguinte e o dia acaba com o
diário escrito. Ensaio: 3 encomendas, a do meio estragada — as outras duas
ficaram feitas, a estragada foi posta de lado, e o chefe leu o dia como um
dia trabalhado. Tirei a proteção e o ensaio rebentou; repus e passou.

**O que continua sem prova:** não fui ler os diários das outras lojas para
confirmar que a loja nunca fechou lá; e os ensaios já não experimentam
mandar entrar o funcionário verdadeiro — usam um boneco que só fica de pé.
Isso foi de propósito, para o ensaio não fazer encomendas verdadeiras, mas
quer dizer que essa parte já ninguém testa.

**O que NÃO fiz, de propósito (HARD STOP):** não juntei lojas, não mexi no
livro das fontes, não fui à rede, não promovi fonte nenhuma. Os três
consertos estão em três "guardar versão com bilhete" separados, nesta
worktree, e enviados para o GitHub.
