# CUTOVER-RUNBOOK — trocar o serviço vivo para a linha unificada

> Missões X1 e X2 (23/09/2026). Escrito para o **coordenador executar** no vivo; a M5D
> adoptou-o como o plano da troca (`RELATORIO-UNIFICACAO.md`, 4.ª passagem).
> **Ensaio final (X2)**: este ficheiro corrido à letra numa cópia (`C:/x2`, já apagada) sobre
> `516132fe` (= `origin/unificacao-v1`, 4.ª passagem FINAL) junto com `cutover-ensaio-v1`,
> com os livros do vivo fotografados no pré-voo. Ensaios anteriores (X1): `5a16d077`,
> `fe61a34b`, `8d2344bd`, `e752c3da`. Prova: `ferramentas/cutover/CUTOVER-ENSAIO-V1.json`
> (`PRE_VOO_X2`, `ENSAIO_FINAL_X2`). Relatório: `RELATORIO-CUTOVER-ENSAIO.md`. Folha de uma
> página: `CUTOVER-CHECKLIST.md`.
>
> **O plano da M5 (`RELATORIO-UNIFICACAO.md`, «SWITCH_PLAN — actualizado na 3.ª passagem»),
> seguido à letra, pára no passo 6** (a reconciliação recusa o corte, rc 3) e, se se
> contornar isso, perde 430 candidatas, 302 SOURCE_ID, 6 marcas D10 e deixa 7 fontes
> presas sem tarefa. Este runbook é esse plano com as seis correcções que o ensaio provou.

## ⚠️ O que depende da M5 — medir NA HORA, não copiar daqui

| o quê | valor no ensaio | porque muda |
|---|---|---|
| `FINAL_HEAD` | `516132fe` = `origin/unificacao-v1` (4.ª passagem FINAL), ensaiado junto com `cutover-ensaio-v1`. **Recomendado:** a M5 avança `unificacao-v1` para incluir `cutover-ensaio-v1` (traz o `--lane` e a trava) | vem uma 5.ª passagem pequena (T1, A2, SOC1, YT1) |
| correcções idempotentes a correr depois do 5b | `aplicar_d13_capacidade`, `aplicar_d15_politica` (só em `e752c3da`+), `corrigir_pais_das_candidatas` | cada decisão nova da M5 que reescreve linhas de candidatas traz a sua ferramenta |
| reconciliar ×2 | 145 s no ensaio final (114 s em `8d2344bd`) | cresce com o livro |
| elegíveis no portão | 29 (19 antes) | depende do estado do bot no corte |
| passos 5b, 5c, 7b | ferramentas desta bancada (`ferramentas/cutover/`) | até a M5 os pôr no SWITCH_PLAN |
| `--lane` no observador | só se o FINAL_HEAD contiver `cutover-ensaio-v1` ≥ `2c08451d` (passo 0 imprime `LANE=SIM`) | a M5D não juntou a X1 de propósito |

A regra de tudo o resto: **se um número medido na hora não bater com o esperado, pare
no ponto de abortar seguinte.**

## Variáveis (Git Bash)

```bash
VIVA=/c/Users/London1/orca/workspaces/eame-sintonia/source-curator-service-v1   # o bot
PONTE=/c/Users/London1/orca/workspaces/eame-sintonia/ponte-curador-v1           # o observador de hoje
CASA=/c/Users/London1/orca/workspaces/eame-sintonia/ponte-viva               # pasta PROPRIA da troca e, depois, do observador
C=/c/cutover/$(date +%Y%m%d-%H%M)       # corte + registos; caminho CURTO (o TEMP longo rebenta o git)
D=$(basename $C)
w(){ cygpath -w "$1"; }
export PYTHONUTF8=1
mkdir -p $C
# as ferramentas do ensaio, tiradas do Git (nao dependem de nenhuma bancada):
git -C $VIVA fetch -q origin              # so mexe no .git partilhado, nao na arvore do bot
git -C $VIVA archive origin/cutover-ensaio-v1 ferramentas/cutover | tar -x -C $C
F=$C/ferramentas/cutover
```

## 0 · Antes de parar nada (serviço a correr) — ~1 min

```bash
FINAL=$(git -C $VIVA rev-parse origin/unificacao-v1); echo $FINAL      # ou o HEAD que o coordenador escolher
git -C $VIVA worktree add -q -b cutover-$D $CASA $FINAL                # a CASA: nem a pasta da M5, nem a do bot
grep -q -- '"--lane"' $CASA/curadoria/ponte_automatica.py && echo "LANE=SIM" || echo "LANE=NAO"   # ver passo 10
git -C $VIVA rev-parse --short HEAD; git -C $VIVA branch --show-current        # anotar: HEAD_VIVO, RAMO_VIVO
git -C $PONTE rev-parse --short HEAD
powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter \"Name='python.exe' or Name='py.exe'\" | Where-Object { \$_.CommandLine -match 'supervisor|worker|ponte_automatica' } | ForEach-Object { '{0} {1} {2} {3}' -f \$_.ProcessId,\$_.ParentProcessId,\$_.CreationDate,\$_.CommandLine }"
py $F/medir_cutover.py pre --viva "$(w $VIVA)" --final $FINAL > $C/pre.json; echo rc=$?
```

Medido às 06:56 de 23/09: supervisor **98512** (lançador `py.exe` 80772), observador
**14960** (lançador 98996, em `$PONTE` @ `20c06500`, ramo `unificacao-plano-v1`), viva
`075501a0` no ramo `source-curator-service-v1`, 11 ficheiros sujos (10 livros +
`telemetria.py` só com fim de linha). `pre`: rc 0 · A1 OK · A2 `LEVAR_NO_5B` 430
candidatas / 302 SOURCE_ID · A3 OK.

**Pré-voo da X2, 23/09 às 07:41 (só leitura).** Os mesmos PIDs e o mesmo HEAD. `pre` rc 0
com os mesmos vereditos. Serviço RUNNING, worker IDLE, fila elegível 0, `PID_CHECK_NAO_SEI`
vazio. As três fotografias do passo 2, gravadas só em cópias fora do serviço, congelaram
à primeira (33, 34 e 34 s). Os 12 livros tinham o mesmo sha256 do corte do ensaio das 06:30:
o bot não escreveu nada nesse intervalo. **Nenhum ABORTAR-0 nem ABORTAR-2 dispararia.**

**🛑 ABORTAR-0** se: `pre` rc 2 (A1: o HEAD vivo não está na linha → a troca tiraria
código de produção; A3: há código sujo de verdade na viva) · `$CASA` já existe · mais de um
supervisor ou observador. Nada foi tocado no bot; apagar a `$CASA`
(`git -C $VIVA worktree remove $CASA; git -C $VIVA branch -D cutover-$D`).

## 1 · Parar o bot e o observador — ~10 s  ⏱️ começa o TEMPO PARADO

```bash
date +%s > $C/t0
echo "cutover $(date -Iseconds)" > $VIVA/curadoria/PARAR.flag
# esperar o supervisor (PID do passo 0) sair: 3-6 s no ensaio
for i in $(seq 1 60); do tasklist //FI "PID eq <PID_SUPERVISOR>" | grep -q <PID_SUPERVISOR> || break; sleep 1; done
taskkill //PID <PID_LANCADOR_OBSERVADOR> //T //F      # a arvore: py.exe + python.exe
# confirmar: a consulta do passo 0 nao devolve NADA com supervisor|worker|ponte_automatica
```

O observador não tem `PARAR.flag`: mata-se. Não faz mal a meio de uma escrita, porque o
corte do passo 2 lê duas vezes e só grava se as duas leituras forem iguais.

**🛑 ABORTAR-1** se algum processo não sair em 60 s → `rm $VIVA/curadoria/PARAR.flag`,
relançar o observador como estava (ver DESFAZER), investigar.

## 2 · Corte dos livros vivos — ~1,5 min

```bash
py $CASA/ferramentas/unificacao/congelar_livros_do_servico.py --origem "$(w $VIVA/curadoria)" --destino "$(w $C/servico)" --intervalo 30
py $F/congelar_extras.py "$(w $C/servico-extras)" 30 \
  "FONTES-CANDIDATAS.json=$(w $VIVA/candidatas/FONTES-CANDIDATAS.json)" \
  "BRIDGE-LEDGER-V1.json=$(w $VIVA/curadoria/BRIDGE-LEDGER-V1.json)" \
  "DISCOVERY-VISITED.json=$(w $VIVA/curadoria/DISCOVERY-VISITED.json)" \
  "READY-BATCHES-V1.json=$(w $VIVA/curadoria/READY-BATCHES-V1.json)" \
  "SOURCE-ID-ALLOCATION-V1.json=$(w $VIVA/curadoria/SOURCE-ID-ALLOCATION-V1.json)"
py $F/congelar_extras.py "$(w $C/ponte)" 30 \
  "LIFECYCLE-LEDGER-V1.json=$(w $PONTE/curadoria/LIFECYCLE-LEDGER-V1.json)" \
  "LIFECYCLE-EVIDENCE-V1.json=$(w $PONTE/curadoria/LIFECYCLE-EVIDENCE-V1.json)"
git -C $VIVA status --short > $C/sujos-da-viva.txt
```

Cada pasta ganha `CORTE.json` com o sha256 de cada ficheiro. **É isto que o DESFAZER repõe.**

**🛑 ABORTAR-2** se alguma fotografia disser `NAO CONGELOU` (com tudo parado, nada devia
mudar) → DESFAZER (só relançar; nada foi trocado).

## 3 · O corte vira um ramo (o `unir` lê refs do Git) — ~10 s

```bash
git -C $VIVA worktree add -q -b cutover-corte-$D $C/wt-corte HEAD
for f in LIFECYCLE-LEDGER-V1.json LIFECYCLE-EVIDENCE-V1.json LIFECYCLE-QUEUE-V1.json italy_contracts_curator.json RED-TEAM-TELEMETRIA-V1.json; do cp $C/servico/$f $C/wt-corte/curadoria/; done
for f in BRIDGE-LEDGER-V1.json DISCOVERY-VISITED.json READY-BATCHES-V1.json SOURCE-ID-ALLOCATION-V1.json; do cp $C/servico-extras/$f $C/wt-corte/curadoria/; done
cp $C/servico-extras/FONTES-CANDIDATAS.json $C/wt-corte/candidatas/
git -C $C/wt-corte add -A curadoria candidatas && git -C $C/wt-corte commit -q -m "cutover: corte dos livros do servico vivo"
```

## 4 · Reconciliar (a ponte aprende o que o bot fez) — ~2 min

```bash
cd $CASA
py curadoria/reconciliar_livros.py --livro-servico "$(w $C/servico)" --livro-ponte curadoria/LIFECYCLE-LEDGER-V1.json --aplicar > $C/reconciliar.log 2>&1; echo rc=$?
py curadoria/reconciliar_livros.py --livro-servico "$(w $C/servico)" --livro-ponte curadoria/LIFECYCLE-LEDGER-V1.json --aplicar > $C/reconciliar-2.log 2>&1   # tem de APENDER 0
git add -A curadoria && git commit -q -m "cutover: reconciliar com o corte do servico vivo"
```

Ensaio 3: 1882 → 2687 linhas; a 2.ª corrida apende 0. As «707 colisões» que ele reporta
são a mesma prova com proveniência diferente: não se perde nada.

**🛑 ABORTAR-4** se rc ≠ 0 (rc 3 = `CORTE DO SERVICO RECUSADO`: alguém escreveu dentro de
`$C/servico`) ou se a 2.ª corrida apender > 0 → `git -C $CASA reset -q --hard $FINAL`; DESFAZER.

## 5 · Unir livros, 5b, G1, 5c, D13 — ~30 s

```bash
py ferramentas/unificacao/unir_livros_do_servico.py HEAD cutover-corte-$D --escrever --relatorio "$(w $C/unir.json)" > $C/unir.log 2>&1; echo rc=$?

# 5b — candidatas + alocacao: a viva e a dona; so copia se CONTEM a linha
py $F/passos_do_cutover.py 5b --extras "$(w $C/servico-extras)" --escrever; echo rc=$?
# ... e DEPOIS as correccoes idempotentes da linha (as que existirem no FINAL_HEAD):
py ferramentas/unificacao/aplicar_d13_capacidade.py --escrever
[ -f ferramentas/unificacao/aplicar_d15_politica.py ] && py ferramentas/unificacao/aplicar_d15_politica.py --escrever
py curadoria/corrigir_pais_das_candidatas.py --aplicar
git add -A curadoria candidatas && git commit -q -m "cutover: unir livros + 5b (candidatas e alocacao da viva) + correccoes"

# G1 — o livro do bot numa COPIA FORA do corte (dentro, invalida o CORTE.json)
cp $C/servico/italy_contracts_curator.json $C/livro-bot-copia.json
for i in 1 2; do py scripts/desbloqueio/aplicar_desbloqueio.py --livro=curadoria/italy_contracts_curator.json \
  --tabela=regras/italy_contracts_onboarded.json --livro-bot="$(w $C/livro-bot-copia.json)" --d10=A \
  --ledger="$(w $C/desbloqueio-ledger.jsonl)" --escrever > $C/g1-$i.log 2>&1; grep -a "ESCRITO\|INVARIANTE" $C/g1-$i.log; done   # 2.a: ESCRITO 0

# 5c — a marca D10 do livro do bot para o livro unido (so onde a aquisicao e igual)
py $F/passos_do_cutover.py 5c --livro-bot "$(w $C/livro-bot-copia.json)" --escrever       # ensaio: 6; 2.a corrida 0
py ferramentas/unificacao/aplicar_d13_capacidade.py --escrever                              # 2.a: 0
py curadoria/interface_collection.py > $C/interface.log 2>&1
```

Ensaio 3: `unir` 42 conflitos resolvidos pela regra dele · 5b leva 430 candidatas e
302 SOURCE_ID · G1 77 → 0 · 5c 6 · D13 6 → 0. Ensaio 4 (`e752c3da`): depois do 5b e das
três correcções, candidatas = viva + as 75 decididas (6 CAPABILITY_BLOCK, 69
POLICY_BLOCK), e as 76 correcções de país da viva ficam intactas.

## 6 · Conferir os livros antes de trocar — ~15 s

```bash
py $F/medir_cutover.py livros --pasta "$(w $CASA)" --corte "$(w $C/servico)" > $C/livros.json; echo rc=$?
```

Aqui o esperado é **rc 2, e só por `B4_D10_SEM_TAREFA`** (as 7 da D10 presas: o 7b
resolve, e tem de ser com o bot parado e já na pasta viva). Tudo o resto OK: B1 corte
íntegro · B2 0 do corte faltam na linha · B3 ≥ 6 marcadas · B5 retiradas todas
recusadas. Anotar `B5_PORTAO.ELEGIVEIS` (ensaio final: 29; eram 19).

⚠️ **Não esperar que o REVALIDAR automático trate das 7.** A M5 mediu «6 CONTRATO_NOVO» no
livro do bot antes da reconciliação, onde as 7 estão READY. Depois da reconciliação, no
livro que o bot vai correr, estão CANARY_PENDING, e o REVALIDAR (que só olha READY) dá 0.
As duas medidas estão certas, cada uma no seu livro. Quem as põe na fila é o 7b.

**🛑 ABORTAR-6** se qualquer outro veredito for PARAR → `git -C $CASA reset -q --hard $FINAL`; DESFAZER.

```bash
git add -A && git commit -q -m "cutover: G1 + 5c + D13 + interface sobre o corte" ; CUT=$(git rev-parse --short HEAD); echo $CUT
```

## 7 · Trocar o código na pasta viva — ~5 s

```bash
git -C $VIVA checkout -q -- .                         # deita fora os 11 sujos (estao no corte, com sha256)
git -C $VIVA switch -q -c servico-$D $CUT        # ramo proprio: cutover-$D esta na CASA
git -C $VIVA rev-parse --short HEAD; git -C $VIVA status --short | wc -l   # = $CUT ; 0
```

## 7b · Quem volta a medir as 7 da D10 — ~2 s

```bash
cd $VIVA && py $F/passos_do_cutover.py 7b --escrever      # ensaio 3: 7 VALIDATE_ROUTE; 2.a corrida 0
py $F/medir_cutover.py livros --pasta "$(w $VIVA)" --corte "$(w $C/servico)" > $C/livros-viva.json; echo rc=$?   # TEM de ser 0
```

São 7, não «as 6 marcadas»: IT-T5-049 não tem marca e fica presa na mesma (despromovida
pela reconciliação porque o bot media outra rota). Os ensaios 1 e 2 deixaram-na esquecida.

**🛑 ABORTAR-7** se rc ≠ 0 → DESFAZER.

## 8 · Relançar — ~5 s  ⏱️ acaba o TEMPO PARADO

```bash
rm $VIVA/curadoria/PARAR.flag
# supervisor: pelo mesmo meio de hoje, cwd $VIVA, linha de comando medida: py curadoria/supervisor.py
# observador: NAO aqui — no passo 10, depois do mapa (fica uns minutos a mais parado; ele
#             apanha tudo na 1.a volta, porque compara o sha256 do livro do bot)
echo "parado $(( $(date +%s) - $(cat $C/t0) )) s"
```

O bot volta aqui. O observador fica parado mais uns minutos, de propósito: ele volta no
passo 10, a partir da `$CASA`.

## 9 · Medir depois — 2 a 5 min

```bash
sleep 120; py $F/medir_cutover.py pos --viva "$(w $VIVA)" > $C/pos.json; echo rc=$?
```

C1: um só worker de cada vez, saídas com rc 0 · C2: `RUNNING` ou `IDLE`,
`PID_CHECK_NAO_SEI` vazio. Com rede, as 7 da D10 devem sair de CANARY_PENDING nas
primeiras voltas (sem rede, no ensaio, foram para RETRY «robots não pode ser lido»,
como deviam). No diário da ponte: `PORTAO` perto do anotado no passo 6.

**🛑 ABORTAR-9** se C1 ou C2 derem PARAR → DESFAZER.

## 10 · Mapa, publicação e o observador (com o bot já a correr)

```bash
cd $CASA
py system-map/scripts/correr_a_cadeia.py REGERAR && py system-map/scripts/correr_a_cadeia.py VALIDAR
git add -A docs system-map italia-portale/client/system-map && git commit -q -m "mapa: regerado pela cadeia sobre o cutover"
py system-map/scripts/correr_a_cadeia.py PORTOES_POS_COMMIT
git push -q origin HEAD:cutover-$D && git fetch -q && git rev-parse --short HEAD origin/cutover-$D   # LOCAL == REMOTO
git -C $VIVA worktree remove $C/wt-corte     # o ramo cutover-corte-* fica como registo local

# o observador: da CASA, a olhar para o bot (so leitura). Linha de comando:
#   LANE=SIM (passo 0):  py curadoria/ponte_automatica.py --servir --intervalo 20 --lane "$(w $VIVA)"
#   LANE=NAO:            py curadoria/ponte_automatica.py --servir --intervalo 20
#                        (o LANE_DO_BOT fixo no codigo ja e $VIVA; falta so a trava)
py curadoria/ponte_automatica.py --saude      # depois de 1 min: A_TRABALHAR true
```

A cadeia demorou **245 s + 73 s** no ensaio 1. Com o bot já a correr, isso não conta como
tempo parado: o mapa é documentação, e o serviço não o lê. O HEAD do bot fica um commit
atrás da `$CASA` (só o mapa), o que não faz mal. **A M5 decide** se `unificacao-v1` avança
para `cutover-$D` (é um avanço directo, sem junção).

**Porque é uma pasta própria.** O livro canónico da ponte vive onde o código dela corre:
`curadoria/LIFECYCLE-LEDGER-V1.json`, e as provas e os contratos, na pasta de onde se
lança. Na pasta da M5, ela sujava os livros a cada volta, onde a M5 trabalha. Na pasta do
bot, era pior: o livro da ponte e o do bot passavam a ser **o mesmo ficheiro**, com dois
processos a escrever nele. Com `--lane`, a ponte recusa isso (rc 2,
`LANE_E_A_CASA_DA_PONTE`) sem escrever nada.

## ⏱️ TEMPO PARADO (do passo 1 ao 8) — ensaio final X2

| passo | segundos |
|---|---|
| 1 parar (supervisor + observador) | 16 |
| 2 três fotografias (30 s de intervalo) | 96 |
| 3 ramo do corte | 12 |
| 4 reconciliar ×2 | 145 |
| 5 unir, 5b + correcções, G1 ×2, 5c, D13, interface | 39 |
| 6 medir livros + commit | 16 |
| 7 trocar | 6 |
| 7b pôr as 7 na fila + medir | 18 |
| 8 relançar o bot | 5 |
| **só comandos** | **353 s ≈ 5,9 min** |
| **no relógio, com as pausas entre passos** | **429 s ≈ 7,2 min** |

Depois disso, e com o bot já a correr: mapa (passo 10) 468 s e, só então, o observador.
O maior peso é a reconciliação e as fotografias. Baixar o intervalo das fotografias para
10 s tiraria ~1 min; isso **não foi ensaiado**.

## ↩️ DESFAZER (de qualquer ponto depois do passo 1)

```bash
echo "desfazer" > $VIVA/curadoria/PARAR.flag      # se ja tiver sido relancado; esperar sair; matar o observador novo
git -C $VIVA checkout -q -- . 2>/dev/null
git -C $VIVA switch -q <RAMO_VIVO>                # anotado no passo 0 (ensaio: source-curator-service-v1 @ 075501a0)
for f in $(ls $C/servico | grep -v CORTE.json); do cp $C/servico/$f $VIVA/curadoria/; done
for f in BRIDGE-LEDGER-V1.json DISCOVERY-VISITED.json READY-BATCHES-V1.json SOURCE-ID-ALLOCATION-V1.json; do cp $C/servico-extras/$f $VIVA/curadoria/; done
cp $C/servico-extras/FONTES-CANDIDATAS.json $VIVA/candidatas/
for f in LIFECYCLE-LEDGER-V1.json LIFECYCLE-EVIDENCE-V1.json; do cp $C/ponte/$f $PONTE/curadoria/; done
# conferir: sha256sum de cada ficheiro reposto = o do CORTE.json da pasta dele
git -C $VIVA worktree remove --force $CASA; git -C $VIVA branch -D cutover-$D   # se ainda nao houve push
rm $VIVA/curadoria/PARAR.flag
# relancar como estava: supervisor em $VIVA (py curadoria/supervisor.py); observador em $PONTE
#   (py curadoria/ponte_automatica.py --servir --intervalo 20)
```

`telemetria.py` volta ao conteúdo do commit; a diferença que ele tinha na viva era só o
fim de linha (medido: `git diff --ignore-cr-at-eol` vazio). Se já tiver havido push do
passo 10, o desfazer da pasta viva é o mesmo; a linha fica com o commit do cutover e a M5
decide se o reverte.

## O que o ensaio NÃO provou

- **Rede.** Tudo correu com a rede cortada (`HTTP(S)_PROXY=http://127.0.0.1:9`). Que as 7
  da D10 passam com o site de hoje só se vê no vivo (passo 9).
- **PASS_PARCIAL** só pelos testes (`test_um_so_canario_promove`, 2 OK): nenhuma volta
  real o produziu sem rede.
- **Quarentena (Q1)** vive na porta da admissão (`admissao/admissao.py`), não no portão.
  `test_politica_nao_sei` 6/6 OK em `8d2344bd`. Não foi exercitada: NADA NA SALA.
- **Observador a partir de uma worktree própria** (a variante do aviso do passo 8).
- O tempo com `--intervalo 10` nas fotografias.
