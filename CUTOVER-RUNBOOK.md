# CUTOVER-RUNBOOK — trocar o serviço vivo para a linha unificada

> Missão X1 (ensaio geral, 23/09/2026). Escrito para o **coordenador executar** no vivo.
> Cada passo foi corrido numa cópia isolada (`C:/x1`, já apagada) sobre três HEADs da
> linha: `5a16d077` (ensaio 1), `fe61a34b` (FINAL da 3.ª passagem, ensaio 2),
> `8d2344bd` (4.ª passagem, ensaio 3) e, só para os livros de candidatas, `e752c3da`
> (ensaio 4, ainda não empurrado quando foi medido). Prova: `ferramentas/cutover/CUTOVER-ENSAIO-V1.json`.
> Relatório: `RELATORIO-CUTOVER-ENSAIO.md`.
>
> **O plano da M5 (`RELATORIO-UNIFICACAO.md`, «SWITCH_PLAN — actualizado na 3.ª passagem»),
> seguido à letra, pára no passo 6** (a reconciliação recusa o corte, rc 3) e, se se
> contornar isso, perde 430 candidatas, 302 SOURCE_ID, 6 marcas D10 e deixa 7 fontes
> presas sem tarefa. Este runbook é esse plano com as seis correcções que o ensaio provou.

## ⚠️ O que depende da M5 — medir NA HORA, não copiar daqui

| o quê | valor no ensaio | porque muda |
|---|---|---|
| `FINAL_HEAD` | `77077dee` = `origin/unificacao-v1` no fecho do ensaio (= `e752c3da` + mapa; o código novo dele, a D15, foi o que o ensaio 4 cobriu). Às 06:56 era `8d2344bd` | a M5 continua a juntar |
| correcções idempotentes a correr depois do 5b | `aplicar_d13_capacidade`, `aplicar_d15_politica` (só em `e752c3da`+), `corrigir_pais_das_candidatas` | cada decisão nova da M5 que reescreve linhas de candidatas traz a sua ferramenta |
| reconciliar | 114 s em `8d2344bd` (66 s em `5a16d077`) | cresce com o livro |
| elegíveis no portão | 29 (19 antes) | depende do estado do bot no corte |
| passos 5b, 5c, 7b | ferramentas desta bancada (`ferramentas/cutover/`) | até a M5 os pôr no SWITCH_PLAN |

A regra de tudo o resto: **se um número medido na hora não bater com o esperado, pare
no ponto de abortar seguinte.**

## Variáveis (Git Bash)

```bash
VIVA=/c/Users/London1/orca/workspaces/eame-sintonia/source-curator-service-v1   # o bot
PONTE=/c/Users/London1/orca/workspaces/eame-sintonia/ponte-curador-v1           # o observador de hoje
UNI=/c/Users/London1/orca/workspaces/eame-sintonia/unificacao-v1                # linha unificada (worktree da M5)
C=/c/cutover/$(date +%Y%m%d-%H%M)       # corte + registos; caminho CURTO (o TEMP longo rebenta o git)
w(){ cygpath -w "$1"; }
export PYTHONUTF8=1
mkdir -p $C
# as ferramentas do ensaio, tiradas do Git (nao dependem desta bancada):
git -C $UNI fetch -q origin cutover-ensaio-v1
git -C $UNI archive origin/cutover-ensaio-v1 ferramentas/cutover | tar -x -C $C
F=$C/ferramentas/cutover
```

## 0 · Antes de parar nada (serviço a correr) — ~1 min

```bash
git -C $UNI fetch -q origin && git -C $UNI status --short     # TEM de estar vazio
FINAL=$(git -C $UNI rev-parse origin/unificacao-v1); echo $FINAL
git -C $UNI switch -q unificacao-v1 && git -C $UNI merge --ff-only -q origin/unificacao-v1
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

**🛑 ABORTAR-0** se: `pre` rc 2 (A1: o HEAD vivo não está na linha → a troca tiraria
código de produção; A3: há código sujo de verdade na viva) · `$UNI` sujo · mais de um
supervisor ou observador. Nada foi tocado.

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
py $UNI/ferramentas/unificacao/congelar_livros_do_servico.py --origem "$(w $VIVA/curadoria)" --destino "$(w $C/servico)" --intervalo 30
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
git -C $VIVA worktree add -q -b cutover-corte-$(basename $C) $C/wt-corte HEAD
for f in LIFECYCLE-LEDGER-V1.json LIFECYCLE-EVIDENCE-V1.json LIFECYCLE-QUEUE-V1.json italy_contracts_curator.json RED-TEAM-TELEMETRIA-V1.json; do cp $C/servico/$f $C/wt-corte/curadoria/; done
for f in BRIDGE-LEDGER-V1.json DISCOVERY-VISITED.json READY-BATCHES-V1.json SOURCE-ID-ALLOCATION-V1.json; do cp $C/servico-extras/$f $C/wt-corte/curadoria/; done
cp $C/servico-extras/FONTES-CANDIDATAS.json $C/wt-corte/candidatas/
git -C $C/wt-corte add -A curadoria candidatas && git -C $C/wt-corte commit -q -m "cutover: corte dos livros do servico vivo"
```

## 4 · Reconciliar (a ponte aprende o que o bot fez) — ~2 min

```bash
cd $UNI
py curadoria/reconciliar_livros.py --livro-servico "$(w $C/servico)" --livro-ponte curadoria/LIFECYCLE-LEDGER-V1.json --aplicar > $C/reconciliar.log 2>&1; echo rc=$?
py curadoria/reconciliar_livros.py --livro-servico "$(w $C/servico)" --livro-ponte curadoria/LIFECYCLE-LEDGER-V1.json --aplicar > $C/reconciliar-2.log 2>&1   # tem de APENDER 0
git add -A curadoria && git commit -q -m "cutover: reconciliar com o corte do servico vivo"
```

Ensaio 3: 1882 → 2687 linhas; a 2.ª corrida apende 0. As «707 colisões» que ele reporta
são a mesma prova com proveniência diferente: não se perde nada.

**🛑 ABORTAR-4** se rc ≠ 0 (rc 3 = `CORTE DO SERVICO RECUSADO`: alguém escreveu dentro de
`$C/servico`) ou se a 2.ª corrida apender > 0 → `git -C $UNI reset -q --hard $FINAL`; DESFAZER.

## 5 · Unir livros, 5b, G1, 5c, D13 — ~30 s

```bash
py ferramentas/unificacao/unir_livros_do_servico.py HEAD cutover-corte-$(basename $C) --escrever --relatorio "$(w $C/unir.json)" > $C/unir.log 2>&1; echo rc=$?

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
py $F/medir_cutover.py livros --pasta "$(w $UNI)" --corte "$(w $C/servico)" > $C/livros.json; echo rc=$?
```

Aqui o esperado é **rc 2, e só por `B4_D10_SEM_TAREFA`** (as 7 da D10 presas: o 7b
resolve, e tem de ser com o bot parado e já na pasta viva). Tudo o resto OK: B1 corte
íntegro · B2 0 do corte faltam na linha · B3 ≥ 6 marcadas · B5 retiradas todas
recusadas. Anotar `B5_PORTAO.ELEGIVEIS` (ensaio: 29; eram 19).

**🛑 ABORTAR-6** se qualquer outro veredito for PARAR → `git -C $UNI reset -q --hard $FINAL`; DESFAZER.

```bash
git add -A && git commit -q -m "cutover: G1 + 5c + D13 + interface sobre o corte" ; CUT=$(git rev-parse --short HEAD); echo $CUT
```

## 7 · Trocar o código na pasta viva — ~5 s

```bash
git -C $VIVA checkout -q -- .                         # deita fora os 11 sujos (estao no corte, com sha256)
git -C $VIVA switch -q -c cutover-$(basename $C) $CUT
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
# observador: a partir da linha unificada (le a pasta viva: LANE_DO_BOT e fixo), cwd $UNI:
#             py curadoria/ponte_automatica.py --servir --intervalo 20
echo "parado $(( $(date +%s) - $(cat $C/t0) )) s"
```

⚠️ Com o observador a correr a partir de `$UNI`, **essa worktree passa a ser a casa viva da
ponte**: os livros dela ficam sujos a cada volta. A M5 não pode continuar a trabalhar lá.
Se o coordenador preferir uma worktree própria para o observador, criá-la em `$CUT` antes
do passo 8 e lançar de lá (o ensaio não mediu essa variante).

## 9 · Medir depois — 2 a 5 min

```bash
sleep 120; py $F/medir_cutover.py pos --viva "$(w $VIVA)" > $C/pos.json; echo rc=$?
```

C1: um só worker de cada vez, saídas com rc 0 · C2: `RUNNING` ou `IDLE`,
`PID_CHECK_NAO_SEI` vazio. Com rede, as 7 da D10 devem sair de CANARY_PENDING nas
primeiras voltas (sem rede, no ensaio, foram para RETRY «robots não pode ser lido»,
como deviam). No diário da ponte: `PORTAO` perto do anotado no passo 6.

**🛑 ABORTAR-9** se C1 ou C2 derem PARAR → DESFAZER.

## 10 · Mapa e publicação (com o bot já a correr)

```bash
cd $UNI
py system-map/scripts/correr_a_cadeia.py REGERAR && py system-map/scripts/correr_a_cadeia.py VALIDAR
git add -A docs system-map italia-portale/client/system-map && git commit -q -m "mapa: regerado pela cadeia sobre o cutover"
py system-map/scripts/correr_a_cadeia.py PORTOES_POS_COMMIT
git push -q origin HEAD:unificacao-v1 && git fetch -q && git rev-parse --short HEAD origin/unificacao-v1   # LOCAL == REMOTO
git -C $VIVA worktree remove $C/wt-corte     # o ramo cutover-corte-* fica como registo local
```

A cadeia demorou **245 s + 73 s** no ensaio 1. Correr isto **antes** do passo 8 junta ~5 min
ao tempo parado sem ganho para o bot: o mapa é documentação, o serviço não o lê. A pasta
viva fica um commit atrás (só o mapa); não faz mal.

## ⏱️ TEMPO PARADO (do passo 1 ao 8)

| passo | ensaio | nota |
|---|---|---|
| 1 parar | 3–6 s | pelo PARAR.flag |
| 2 corte | ~95 s | 3 fotografias × 30 s de intervalo |
| 3 ramo do corte | 7 s | |
| 4 reconciliar ×2 | 114 + 3 s | em `8d2344bd` |
| 5 unir, 5b+correcções, G1×2, 5c, D13, interface | 4 + 4 + 6 + 1 + 2 + 8 s | |
| 6 medir livros + commit | ~15 s | |
| 7 trocar | 4 s | |
| 7b | 2 s | |
| 8 relançar | 4 s | |
| **total** | **≈ 4,5 a 5 min** | mapa depois do relançamento |
| com o mapa antes do relançamento | ≈ 10 min | +245 s +73 s |

O maior peso é a reconciliação (cresce com o livro) e as fotografias (baixar o intervalo
para 10 s tira ~1 min; **não ensaiado**).

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
git -C $UNI reset -q --hard $FINAL                # se ainda nao houve push
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
