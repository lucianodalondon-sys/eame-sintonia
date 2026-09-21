# RELATÓRIO — BRIDGE + FEEDER: integração aditiva

Missão: `C:/Users/London1/auditoria-madrugada/MISSAO-BRIDGE-FEEDER.md`.
Worktree: `bridge-feeder-v1`, base `provas-p1` @ `c3204e2a`. Peça trazida:
`candidate-bridge-v1` @ `63b71421`. Sem merge, sem rebase, sem cherry-pick, sem
rede, sem tocar noutras worktrees, sem tocar no supervisor vivo (PID 86172).
Data: 2026-09-21. Ambiente: Windows 11, bash MSYS, `py` = Python 3.12.

```
INITIAL_HEAD                   = c3204e2a8b326521897242641f13ae13f0e54983
FINAL_HEAD                     = f20aee15  (mapa regerado; o commit que fecha este
                                 relatório fica por cima, ver §9)
REMOTE_HEAD                    = (ver §9 — preenchido depois do push)
WORKTREE_CLEAN                 = YES  (git status --porcelain vazio depois de cada commit)
BRIDGE_INTEGRATED              = YES  (6 ficheiros inteiros + 2 testes isolados + 2 enxertos)
FEEDER_INTEGRATED              = YES  (base = esta árvore; nada do feeder foi removido)
CANDIDATE_TO_QUEUE_PROVEN      = YES  (G1: 3 candidatas -> 2 tarefas QUALIFY -> 2 elegíveis)
QUEUE_TO_WORKER_PROVEN         = YES, COM RESSALVA (o worker apanha e BLOQUEIA: «sem
                                 contrato nesta arvore»; QUALIFY não tem executor;
                                 o livro não recebe nada nesse ramo — §3.1)
WORKER_RECOVERY_PROVEN         = YES  (G3: PID 90964 morto -> PID 98496 relançado)
DEDUP_PROVEN                   = YES  (G2 + T1; mutação B reprova 3 testes)
TEST_ISOLATION_PROVEN          = YES  (md5 antes/depois; guarda estática; mutações E1/E2)
REAL_QUEUE_UNCHANGED_BY_TESTS  = YES  md5 87be1ef3daf531f992b02c6a40963409 antes e depois
REAL_LEDGER_UNCHANGED_BY_TESTS = YES  md5 9e475db922ce22ce739b60c8c0975a89 antes e depois
BASELINE_TESTES = 166   TESTES_FINAIS = 234   NOVOS = 68
NEW_FAILURES = 0        ALL_GATES_GREEN = YES (com a ressalva de G1 declarada)
SYSTEM_MAP_CHECK = PASS (22 provas; PORTOES_POS_COMMIT: IMPRESSAO_DO_CARIMBO=IGUAL)
SOURCE_BOOK_A = esta árvore  · porta 241 (241 EM_ANALISE) · ledger 263 transições / 85 fontes
                · fila 68 tarefas / PROXIMO_ID 128
SOURCE_BOOK_B = bridge 63b71421 · porta 271 (196 EM_ANALISE, 75 RECUSADA)
                · ledger 312 transições / 160 fontes · fila 110 tarefas / PROXIMO_ID 198
DIFF_COUNT    = porta: +30 só no bridge, 0 só aqui, 75 comuns com ESTADO/MOTIVO diferentes
                · ledger: 237 comuns, 26 só aqui, 75 só no bridge
                · fila: 40 TASK_IDs comuns (2 com fonte DIFERENTE), 28 só aqui, 70 só no bridge
SOURCE_BOOK_RECONCILIATION = NOT_DONE_BY_DESIGN
BIG_COLLECTION_ALLOWED = NO
NAO_SEI = (lista em §8)
```

Legenda: **FATO MEDIDO** = saída de comando que corri; **INFERÊNCIA** = o que
concluo dos fatos; **NÃO SEI** = sem prova.

---

## 0. Baseline e o que a missão dizia que confirmei (FATO MEDIDO)

```
cd curadoria && py -m unittest discover -s . -p "test_*.py"
Ran 166 tests in 12.983s
OK
git status --porcelain -> vazio
merge-base(63b71421, HEAD) = 8bbea01c
```

md5 dos livros reais antes de tocar em qualquer coisa (cópia em `$TEMP/bridge-feeder-v1/`):

```
87be1ef3daf531f992b02c6a40963409 *curadoria/LIFECYCLE-QUEUE-V1.json
9e475db922ce22ce739b60c8c0975a89 *curadoria/LIFECYCLE-LEDGER-V1.json
9742ed246bbd7fdefb91543f77791ffb *candidatas/FONTES-CANDIDATAS.json
```

**Correção ao mapa da missão.** A missão listava 10 ficheiros de código
«tocados pelos dois lados». Medido com `git diff --name-status 8bbea01c 63b71421`:
o bridge só tocou em **dois** — `supervisor.py` e `status_live.py`. Os outros
oito (`worker.py`, `test_supervisor.py`, `ciclo_continuo.py`, `canario.py`,
`interface_collection.py`, `lotes.py`, `atribuir_source_id.py`,
`emparelhar_com_atlas.py`) só mudaram do lado do feeder. Não houve nada a
enxertar neles.

**Correção ao «facto importante» da missão.** `ponte_candidatas.py` guarda a
sua memória de idempotência no `BRIDGE-LEDGER-V1.json` próprio — isso confirma-se
(`P.LEDGER = BRIDGE-LEDGER-V1.json`). Mas a ponte **escreve em quatro sítios**,
não num: além do ledger próprio, chama `LC.registar(...)` (livro canónico, para
as sociais barradas), `F.enfileirar(...)` (fila canónica, para as QUALIFY) e
`FN.gravar(...)` (a porta, para mudar o ESTADO das candidatas). Logo a ponte
**colide com os livros congelados se for corrida a sério**. Nesta missão só
correu em pastas descartáveis. Isto está escrito no cabeçalho do
`test_ponte_candidatas.py` e é a razão de o `BRIDGE-LEDGER-V1.json` ser um risco
(§8, item 1).

---

## 1. O que foi trazido inteiro (commit 5b6068cf)

`git checkout 63b71421 -- <6 ficheiros>`, byte a byte:

| ficheiro | linhas | o que é |
|---|---|---|
| `curadoria/ponte_candidatas.py` | 240 | a ponte CANDIDATA -> TAREFA |
| `curadoria/descobrir.py` | 1067 | o motor de descoberta (catálogo de 74 URLs) |
| `curadoria/BRIDGE-LEDGER-V1.json` | — | 147 PROCESSADAS: 72 QUALIFY · 69 POLICY_BLOCK · 6 CAPABILITY_BLOCK |
| `curadoria/BRIDGE-PROOF-V1.json` | — | corrida do bridge: 271 lidas, 72 enfileiradas, 75 barradas |
| `curadoria/DISCOVERY-PROOF-V1.json` | — | corrida de 21/09 02:11Z: 51 pedidos, 30 novas, 8 dedup |
| `curadoria/DISCOVERY-VISITED.json` | — | memória de dedup da descoberta |

Nenhum livro de fontes foi tocado: md5 idênticos depois do commit.

---

## 2. Os enxertos de código (um commit cada)

### 2.1 `supervisor.py` — `hook_fila_vazia` (commit b6f92e1c)

Base = esta árvore (mantém `_proc_e_python()`, os 6 estados de paragem, e os
consertos P1). Enxertado do bridge: parâmetro `hook_fila_vazia=None` em
`uma_volta_sup()` e, no ramo IDLE, a chamada dentro de `try/except` com anotação
`DISCOVERY_HOOK_ERRO` no diário (com o nome da exceção). Padrão `None` =
comportamento de antes. Como no bridge, **ninguém passa o hook em `_loop`** —
ligá-lo ao `descobrir.py` faria o supervisor sair à rede, e isso não se decide
aqui (§8, item 2).

Testes (`TestHookFilaVazia`, 5): sem hook a volta é a de antes; fila vazia chama
o hook uma vez por volta; com trabalho elegível o hook não é chamado; hook que
rebenta mantém IDLE, escreve `DISCOVERY_HOOK_ERRO` com `ORIGEM=SUPERVISOR`, e
não conta como batimento; rebentar 4 vezes não conta como morte do worker.

### 2.2 `status_live.py` — os campos da descoberta, LIDOS (commit 50353c6a)

Base = esta árvore (READY_LEGACY/READY_CURRENT calculados, `NAO SEI` no erro).
Enxertado: `_status_discovery()` lê `DISCOVERY-PROOF-V1.json` e devolve
`DISCOVERY_SERVICE` (`NOT_RUN` / `RAN` — nunca `ACTIVE`: a descoberta é uma
corrida com prova, não um serviço com processo), `LAST_DISCOVERY_RUN`,
`LAST_DISCOVERY_RUN_AGE_H` (a idade ao lado do número), `CANDIDATES_NEW`,
`DEDUP_REJECTED`. Sem prova: `NUNCA`. Prova ilegível ou sem campo:
`NAO SEI: <Excecao>`. **Nem o `'READY_LEGACY': 18` nem o `CANDIDATES_TOTAL: 0`
do bridge entraram.** Leitura real nesta árvore:

```
{'DISCOVERY_SERVICE': 'RAN', 'LAST_DISCOVERY_RUN': '2026-09-21T02:11:34.874702+00:00',
 'LAST_DISCOVERY_RUN_AGE_H': 11.7, 'CANDIDATES_NEW': 30, 'DEDUP_REJECTED': 8}
```

Testes (`test_painel_discovery.py`, 6), incluindo uma guarda estática: nenhum
campo do painel pode ter número literal no código.

### 2.3 Os testes do bridge, no molde da casa (commits 98b7770e, 8b2e0fa2)

- `test_ponte_candidatas.py`: os 20 casos do bridge + 2. Sem `importlib.reload`
  (o bridge recarregava os módulos e nunca restaurava os caminhos). Caminhos em
  `_antes`, restauro em `tearDown`, sha256 dos 4 ficheiros reais em cada teste.
- `test_discovery.py`: os 26 casos do bridge + 2. **A versão do bridge escrevia
  na porta REAL e no `DISCOVERY-VISITED.json` real** e «limpava» reescrevendo os
  ficheiros. Aqui `FN.FILA`, `D.VISITADOS_JSON` e `D.PROOF_JSON` vão para a
  pasta descartável, e `urllib.request.urlopen` rebenta em todos os testes (o
  único que simula HTTP põe o seu `mock` por cima). ZERO rede, provado por
  construção: um caminho que tentasse a internet reprovaria.

### 2.4 A guarda de isolamento (commit 879d7db2)

`test_zz_guarda_isolamento.py` passa a medir também a porta
(`../candidatas/FONTES-CANDIDATAS.json`), o `BRIDGE-LEDGER-V1.json`, o
`DISCOVERY-VISITED.json` e o `DISCOVERY-PROOF-V1.json`; e ganha 3 regras
estáticas (quem chama `FN.registar/FN.gravar/P.processar/D.descobrir` tem de
redirecionar `FN.FILA`; quem chama `D._marcar_*` tem de redirecionar
`D.VISITADOS_JSON`; quem chama `P.processar` tem de redirecionar `P.LEDGER`,
`F.FILA` e `LC.LIVRO`). Duas amostras provam que a regra apanha o
`test_discovery.py` do bridge e uma ponte sem ledger redirecionado.

---

## 3. G1 — a cadeia real, ponta a ponta (FATO MEDIDO, `test_ponte_cadeia.py`)

Tudo em pasta descartável: porta, ledger da ponte, fila, livro, evidência,
contratos, estado e diário do supervisor. Lançador do supervisor = worker
inerte; o worker que processa = o **real** (`worker.correr`), em processo.

```
G1 CADEIA: candidatas=3 -> ponte: tarefas_criadas=2 barradas=1 -> fila: elegiveis=2
-> supervisor: RELANCADO pid=100484 -> worker: feitos=2 resultado=['BLOCK']
-> livro: POLICY_BLOCK=1 QUALIFY=0 -> IDLE hook=1
```

| salto | número real |
|---|---|
| CANDIDATA existe | 3 (BASE_OFICIAL, LINKEDIN, ORGANIZACAO) |
| ponte reconhece | CANDIDATAS_LIDAS=3, ENFILEIRADAS=2, CLASSIFICADAS_BARRADAS=1, SOCIAIS_ENFILEIRADAS=0 |
| tarefa criada | TAREFAS_CRIADAS=2, ambas QUALIFY / PENDING |
| entra na fila | QUEUE_DEPTH 0 -> 2; `F.elegiveis()` = 2 |
| supervisor deteta | `uma_volta_sup` -> RELANCADO, `LAST_RESTART_REASON` = «2 tarefas elegiveis» |
| worker processa | feitos=2, RESULTADO=BLOCK, PORQUE=«sem contrato»; fila: 2 BLOCKED |
| lifecycle recebe | LINKEDIN -> POLICY_BLOCK (pela ponte); as 2 QUALIFY -> **nada** |
| volta seguinte | worker morto + 0 elegíveis -> IDLE, hook chamado 1 vez |

### 3.1 A ressalva, dita pelo nome

O worker desta árvore (idêntico ao do bridge — `worker.py` não foi tocado em
63b71421) **não tem executor para QUALIFY** (`ETAPAS` tem VALIDATE_ROUTE,
CANARY, REVALIDATE, REPAIR, BUILD_CONTRACT) e, sem contrato, bloqueia a tarefa
com «sem contrato nesta arvore» **antes** de chegar ao livro. INFERÊNCIA: as 72
tarefas QUALIFY que o bridge deixou na sua fila seriam todas bloqueadas assim
pelo worker real. Não inventei um executor para a cadeia parecer completa —
quem qualifica uma candidata é decisão de outra missão (§8, item 3).

---

## 4. G2 — idempotência (FATO MEDIDO)

- mesma candidata duas vezes (mesma URL com e sem `/`): a porta dedupa para
  UM `CANDIDATA_ID`; `P.processar()` duas vezes -> 1 tarefa; `F.enfileirar` da
  mesma (SOURCE_ID, TASK_TYPE) aberta devolve a existente.
- retry legítimo: `F.adiar(tid, retry_after_s=0, erro="429 simulado")` ->
  ATTEMPTS=1, LAST_ERROR preservado; a ponte outra vez não cria segunda tarefa
  nem apaga a primeira; a tarefa continua elegível com o histórico.
- tarefa bloqueada não trava o resto: com A bloqueada, `F.elegiveis()` = [C]; o
  worker processa só C; A fica como estava.

---

## 5. G3 — recuperação (FATO MEDIDO, `TestRecuperacaoDoWorker`)

```
G3 WORKER_RECOVERY: PID_ANTES=90964 morto -> PID_DEPOIS=98496 relancado
```

Volta 1 RELANCADO (PID 90964, `_pid_no_so` = True); volta 2 VIVO; `kill` +
`wait`; volta 3 RELANCADO com PID 98496 ≠ 90964; `RESTARTS_TOTAL` = 2;
`CRASHES_SEM_PROGRESSO` = 1 (não bloqueia); diário: `WORKER_MORTO` [90964],
`WORKER_RELANCADO` [90964, 98496]. O supervisor de produção (PID 86172,
`C:\actions-runner-2\...\python.exe curadoria/supervisor.py --poll 30`, noutra
pasta) não foi tocado.

---

## 6. G4 — isolamento (FATO MEDIDO)

Cada teste do bridge corrido **sozinho**, md5 antes e depois:

```
test_ponte_candidatas  Ran 22 tests OK
  87be1ef3daf531f992b02c6a40963409 LIFECYCLE-QUEUE-V1.json     (antes = depois)
  9e475db922ce22ce739b60c8c0975a89 LIFECYCLE-LEDGER-V1.json    (antes = depois)
  9742ed246bbd7fdefb91543f77791ffb FONTES-CANDIDATAS.json      (antes = depois)
  422856aa50aef8b33131acd6cb91bf5c BRIDGE-LEDGER-V1.json       (antes = depois)
test_discovery         Ran 28 tests OK
  (os três acima iguais) + 00c0a1098594a3af49ae5fa0f0306693 DISCOVERY-VISITED.json
  + eb0cc5eeaeee5bfbc5ad67bd767c7ec5 DISCOVERY-PROOF-V1.json  (antes = depois)
test_ponte_cadeia      Ran 4 tests OK  (os três livros iguais)
suíte completa         Ran 234 tests OK (os cinco ficheiros iguais; git status vazio)
```

`git status` vazio **não** foi a prova; o md5 foi. E a guarda estática cobre
agora os testes novos (§2.4).

---

## 7. G5 — red team (FATO MEDIDO, saída real; originais em `$TEMP`, `__pycache__` limpo entre mutações, restauro conferido por md5)

| # | mutação aplicada | resultado |
|---|---|---|
| A | `ponte_candidatas.py`: `F.enfileirar(` -> lambda que devolve `{"TASK_ID": "FINGIDA"}` sem tocar a fila | **FAILED (failures=2, errors=2)** — `test_g1...: AssertionError: 0 != 2` (elegíveis), `test_g2_a_mesma...: 0 != 1`; a ponte não consegue fingir que enfileirou |
| B | `ja_ledger = set()` (guarda de idempotência desligada) | **FAILED (failures=3)** — `test_segunda_corrida_cria_zero_tarefas: 2 != 0`, `test_red_team_restaurada_passa: 1 != 0`, `test_g2_a_mesma_candidata: 1 != 0` |
| C | `supervisor.py`: `if n_elegiveis == 0:` -> `if True:` (nunca relança) | **FAILED (failures=6)** — `test_worker_morto_e_relancado: 'IDLE' != 'RELANCADO'`, `test_relanca_com_trabalho`, os dois crashloop reais (`['IDLE',...] != ['RELANCADO',...]`), `test_g1` |
| D | `worker.py`: `except Exception` -> `except ZeroDivisionError` (a volta deixa de sobreviver) | **FAILED (errors=3)** — `RuntimeError: a fonte rebentou a meio da etapa` em `test_1`, `test_2`, `test_3` de `test_worker_volta_sobrevive` |
| E1 | `test_ponte_cadeia.py`: apagar `F.FILA = d / "QUEUE.json"` (fila REAL); **só a guarda estática corre, o teste mutado não é executado** | **FAILED** — `test_ponte_cadeia.py: falta \`F.FILA =\` (corre a ponte -> P.LEDGER, F.FILA e LC.LIVRO redirecionados)` |
| E2 | `test_discovery.py`: apagar `FN.FILA = ...` (porta REAL) | **FAILED** — `test_discovery.py: falta \`FN.FILA =\` (escreve na porta -> FN.FILA redirecionada)` |

Restauro: `md5sum -c` OK nos 5 ficheiros; `git status --porcelain` vazio; md5
dos três livros iguais; 56 testes verdes outra vez. Nota de método: as
primeiras tentativas de A e C não se aplicaram porque o padrão tinha várias
linhas e os ficheiros vindos do Git têm CRLF; repeti com padrão de uma linha e
`grep -c` da marca de mutação = 1 antes de correr.

---

## 8. NÃO SEI, riscos e o que NÃO foi feito de propósito

1. **`BRIDGE-LEDGER-V1.json` descreve a fila do bridge, não esta.** Refere 72
   `TASK_ID`s; 70 não existem nesta fila; os 2 que existem (`T00126`, `T00127`)
   são aqui `IT-T9-015 CANARY DONE` e `IT-T9-019 CANARY DONE`, não
   `CAND-0253`/`CAND-0013`. Trazido inteiro por ordem da missão. **Se alguém
   correr `ponte_candidatas.py` a sério nesta árvore com este ledger, 147
   candidatas são saltadas em silêncio como «já processadas».** Repor ou
   reconciliar este ledger é parte da reconciliação congelada — não aqui.
2. **Ninguém passa `hook_fila_vazia` em `_loop`** (igual ao bridge). O ciclo
   ainda não se realimenta sozinho. Ligar o hook ao `descobrir.py` põe o
   supervisor a sair à rede; ligá-lo ao `nivel_da_fila.escrever()` (o sinal do
   feeder, sem rede) é a ligação óbvia — mas é decisão, não enxerto.
3. **QUALIFY não tem executor** (§3.1). Quem qualifica, e como, não está nesta
   árvore nem no bridge.
4. **`descobrir.py` desliga a verificação TLS** (`CTX.check_hostname = False`,
   `CTX.verify_mode = ssl.CERT_NONE`). Trazido verbatim; não corrigido (fora do
   escopo; ZERO rede aqui). Observação de segurança para quem for ligar a
   descoberta.
5. **`FONTES-CANDIDATAS.json` do bridge NÃO foi adotado.** É superconjunto de
   IDs (241 + 30 = 271), mas 75 das 241 comuns têm `ESTADO=RECUSADA` +
   `MOTIVO_DA_RECUSA`, cujo par (POLICY_BLOCK/CAPABILITY_BLOCK) vive no ledger
   congelado do bridge. Adotar a porta sem o ledger poria os dois livros a
   contradizer-se. Não é «sem perda». As 30 novas (`CAND-0242..0271`) ficam
   preservadas em `63b71421` e em `DISCOVERY-PROOF-V1.json` -> `CANDIDATOS_REGISTADOS`
   (que já está nesta árvore). Preservados ambos; `NOT_DONE_BY_DESIGN`.
6. **Os livros congelados divergem** (§0 e cabeçalho: ledger 26 só aqui / 75 só
   no bridge; fila 28 só aqui / 70 só no bridge; 2 TASK_IDs com fonte diferente).
   Ficaram como estavam. Não escolhi vencedor.
7. **Traceback de codificação no `tasklist`, pré-existente.** Com `PYTHONUTF8=1`
   (o ambiente da suíte), `_pid_no_so()`/`_proc_e_python()` para um PID
   inexistente leem «INFORMAÇÕES: nenhuma tarefa…» em cp850 (byte 0x80 = Ç) e
   o leitor do `subprocess` imprime `UnicodeDecodeError`; o `except` devolve
   False — a resposta certa, por acidente. Medido em `c3204e2a`
   (`test_lock_orfao_pid_morto`: 2 tracebacks; 0 sem `PYTHONUTF8`). Não é desta
   missão; fica registado.
8. **O supervisor vivo (PID 86172) corre código de outra pasta**
   (`C:\actions-runner-2\_work\...`). Esta integração não lhe chega até essa
   árvore ser atualizada. Não lhe toquei.
9. **`hook_fila_vazia` em produção** — não sei o que deve acontecer quando a
   fila esvazia: pedir descoberta (rede), escrever o sinal (sem rede), ou nada.

---

## 9. Commits, mapa e push

```
5b6068cf bridge-feeder: trazer a ponte e o motor de descoberta inteiros (de 63b71421)
98b7770e bridge-feeder: test_ponte_candidatas.py no molde de isolamento da casa
8b2e0fa2 bridge-feeder: test_discovery.py isolado e sem rede
b6f92e1c supervisor: enxertar hook_fila_vazia em uma_volta_sup (de 63b71421) + G3
50353c6a status_live: os campos da descoberta LIDOS da prova (de 63b71421, sem literais)
efdbae73 provas: G1 e G2 — a cadeia ponta a ponta em pasta descartavel
879d7db2 guarda do isolamento: cobrir a porta, a ponte e a descoberta
f20aee15 mapa: regerado pela cadeia canonica sobre a arvore do bridge-feeder (879d7db2)
```

G7: `correr_a_cadeia.py REGERAR` 20/20 `CADEIA=OK`; `VALIDAR` 22 provas PASS,
`SYSTEM_MAP_CHECK=PASS`; `PORTOES_POS_COMMIT` `IMPRESSAO_DO_CARIMBO=IGUAL`
(carimbo `214a3acc…`). Peças novas reivindicadas pelo mapa: os 6 ficheiros do
bridge e os 3 testes novos. O censo de endereços subiu de 319 para 439 porque
`descobrir.py` traz um catálogo de 74 URLs — não porque alguém tenha chamado
mais endereços.

Testes por ficheiro (234): supervisor 30 (24 + 6) · discovery 28 · ponte 22 ·
painel_discovery 6 · ponte_cadeia 4 · zz_guarda 5 (3 + 2) · os restantes 139
como no baseline. Nenhum dos 12 testes P1 morreu (suíte verde, 0 falhas).

O commit que fecha este relatório fica por cima de `f20aee15`; o carimbo do mapa
aponta para `f20aee15` de propósito (só este ficheiro muda). `REMOTE_HEAD` é
escrito depois do push, no fecho.

---

## EM PALAVRAS SIMPLES

Imagina três coisas na cozinha do Source Curator.

**A caixa de pistas.** É a porta de candidatas: uma caixa cheia de bilhetes a
dizer «olha, existe este site agrícola italiano». Só bilhetes. Ninguém abriu o
site ainda. Nesta árvore há 241 bilhetes; na árvore do bridge havia 271.

**A lista de tarefas.** É a fila do Curator: o papel na parede com «abrir este
site», «testar aquele». Um trabalhador (o worker) vai riscando a lista, e um
capataz (o supervisor) fica de olho: se o trabalhador desmaia, o capataz chama
outro.

**A ponte** era o que faltava: alguém que pega nos bilhetes da caixa e os
transforma em tarefas na lista. Existia noutra bancada (o bridge) e nunca tinha
sido trazida para esta. Agora está cá — o código dela, os testes dela e o
caderno dela. **O alimentador** (o feeder, que já estava aqui) é a parte que
conta os bilhetes que sobram e avisa «está a acabar» — e o capataz melhorado,
que pergunta ao Windows se o trabalhador está mesmo vivo em vez de acreditar
num papel velho.

**Como ficaram ligados.** O capataz ganhou uma campainha: quando a lista de
tarefas fica vazia, ele toca-a. Por enquanto ninguém está do outro lado da
campainha — decidir quem atende (o explorador que vai à internet buscar
bilhetes novos, ou só um aviso escrito) é decisão tua, não minha. E o painel
passou a mostrar a última vez que o explorador saiu (21/09 às 02:11, 30 bilhetes
novos, 8 repetidos), lido do recibo dele, não escrito à mão.

**O que provei.** Pus 3 bilhetes de mentira numa caixa de mentira, corri a
ponte: 2 viraram tarefas, 1 (LinkedIn) foi barrado com o motivo escrito. O
capataz viu as 2 tarefas e chamou o trabalhador. O trabalhador pegou nelas e…
**devolveu-as com «não sei fazer isto»**. É verdade e está escrito: o
trabalhador sabe abrir sites com contrato, mas «qualificar um bilhete» ainda não
é um trabalho que ele saiba fazer. Não fingi que sabia. Matei o trabalhador de
propósito (um de mentira, PID 90964) e o capataz chamou outro (PID 98496). Corri
a ponte duas vezes com os mesmos bilhetes: uma tarefa só, não duas. E
estraguei o código de propósito seis vezes — de cada vez, os testes ficaram
vermelhos, como deviam.

**Por que os dois livros de fontes ficaram intocados.** O livro (o registo do
que cada fonte já passou) e a lista de tarefas foram escritos pelas duas
bancadas ao mesmo tempo, com coisas diferentes: aqui entraram 26 linhas que o
bridge não tem, lá entraram 75 que aqui não há; na lista, dois números de
tarefa (T00126 e T00127) apontam para fontes diferentes em cada lado. Juntar
isso à mão, ou deixar o Git «resolver», apagaria um dos lados sem ninguém
reparar — ficheiro de dados não dá erro vermelho. Então: trouxe o código e o
caderno próprio da ponte, medi as diferenças (estão todas no cabeçalho), e
**parei**. Os números dos dois lados estão aqui para tu decideres.

**O que pode dar problema depois.** O caderno da ponte que trouxe (o
BRIDGE-LEDGER) foi escrito na outra bancada: diz que 147 bilhetes já foram
tratados, mas as tarefas que ele cita não existem nesta lista. Se alguém correr
a ponte a sério aqui sem limpar esse caderno, ela salta 147 bilhetes calada.
Está escrito no ponto 1 dos NÃO SEI. Não corri coleta, não corri inteligência,
não toquei no portal.
