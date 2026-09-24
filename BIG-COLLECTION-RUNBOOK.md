# BIG-COLLECTION-RUNBOOK — o dia da Big Collection, passo a passo

> Missão BC1, 23/09/2026. Para o coordenador. Construído sobre o `MICRO-RUNBOOK.md` (a
> mesma estrada, com a coorte inteira do portão) e o `CUTOVER-RUNBOOK.md` (a produção de
> hoje). Medições em `BIG-COLLECTION-GATES.md` (os gates do §25) e em
> `ferramentas/big_collection/BC1-ENSAIO.json`.
>
> **Estado em 23/09, ~15 h: NÃO CORRER AINDA.** Pelo §25: 12/20 gates YES
> (`BIG-COLLECTION-GATES.md`). Faltam três bloqueios, cada um com dono (secção 1). O resto
> está medido e ensaiado. A linha andou durante a missão: `940f3b14` → **`de4dec2b`** (6.ª
> passagem: A4, V1A, D1, A3). A instalação (passo I) foi provada sobre as duas.

## 1 · Bloqueios (cada um fecha antes do passo 5)

| # | o quê | medido | o que falta | dono |
|---|---|---|---|---|
| B1 | a produção não tem a linha | bot em `cd4203db` e ponte em `5c02bbe4`: fora de `origin/unificacao-v1` @ `de4dec2b` (5.ª e 6.ª passagens: T1, A2, SOC1, YT1, A4, V1A, D1, A3). O `micro_coleta.py` da produção ainda é o de antes da A2 | passo I (instalar), provado em cópia sobre `940f3b14` e sobre `de4dec2b`: 13 conflitos, todos no mapa gerado; **11/11 livros = produção**; `italy_contracts_onboarded.json` com as duas mudanças e JSON válido | coordenador (bot quieto) |
| B2 | robots e ritmo | o coletor Node da linha não lê robots nem espaça pedidos (0 ocorrências em `coleta/italy_pilot_collect.mjs`). A A4 (`micro_rede_real.py`, já na linha em `de4dec2b`) lê robots **por fora**, mas só trabalha com Sala descartável. A A5 (`cortesia-coleta-v1`) põe o robots no coletor, mas o único commit dela é um checkpoint do coordenador **não testado, não aceite** | A5 testada, aceite e juntada à linha; ou a A4 com modo Sala real. Sem isto, a corrida viola o §27 («violations de policy/robots») | A5 → M5 |
| B3 | cobertura | **fechado pela D25** (a Big Collection não espera pelas fontes; a coorte são as READY do portão com rota provada, sem mínimo). BC2: canário real + o dono (`onboardar_rotas_provadas.py`) levaram **18** ao contrato: **PRONTAS 10 → 19**; as 18 de fora têm cada uma o seu `FALTA` (`ferramentas/big_collection/BC2-FONTES-27.json`) | ondas seguintes: receitas web T8/T12/T9 (10 fontes), 4 robots/rede desta saída, 3 rotas que caem em capa | receitas / curador |

⚠️ **Não correr `provar_ponte_curador.py` na `ponte-viva`.** Medido hoje numa cópia: a
prova diz trabalhar numa cópia descartável, mas escreve as fontes de mentira IT-T99-001 e
IT-T99-003 no `italy_contracts_curator.json` da árvore onde corre (`R.CONTRATOS_A` não é
redirecionado). Dono: M5 (ponte).

A V1A (régua capa/matéria ligada) e a D1 entraram na linha na 6.ª passagem; **ninguém mediu
a V1A no gabarito depois disso** (gate 10). O C8 do relatório (0 SIM errado no gabarito)
continua a ser a trava.

## 2 · Quem corre o quê

| onde | o quê | porquê |
|---|---|---|
| **esta máquina, um processo só**, a partir da árvore do serviço (`source-curator-service-v1`) | a corrida (passo 5) | a Sala real (`127.0.0.1:54330/sala_italia`), o armazém `~/sintonia-sala-italia/armazem` e a VPN IT estão aqui. O portão lê os livros da pasta de onde corre: medido, o bot e a casa da ponte dão os mesmos 37 |
| runner `SINTONIA-EAME-LOCAL` (`C:\actions-runner-eame`, a escutar) | nada durante a corrida; antes, pode correr as provas locais (passo 0) | o checkout do runner vem do GitHub, com livros velhos, e a mesma saída de rede: colher lá era colher duas vezes do mesmo IP |
| runner `SINTONIA-EAME-LOCAL-2` (`C:\actions-runner-eame-2`, a escutar) | reserva; parado durante a corrida | dois colectores com o mesmo IP dobram os pedidos por site (§27, «requests repetidos em massa») |
| GitHub-hosted (`ubuntu-latest` + `postgres:16`) | `banco-descartavel.yml`, job `portao-big-collection` (`provas/o_portao_da_big_collection.py`) sobre o HEAD instalado | prova que o READY pousa na Sala num Postgres 16 limpo, sem nada desta máquina |
| VPN IT (ProtonVPN) | a saída de TODA a corrida | medida antes e depois de cada fonte (`superficie/rede.py --portao-de-egresso IT`); se cair, pára tudo |

⚠️ Os runners `LUCIANO` e `LUCIANO-2` (`C:\actions-runner`, `-2`) são do **portal-sintonia**,
não deste repositório. Não usar.

## 3 · Os passos

### I · Instalar a linha na produção (bot quieto) — ~15 min

Ensaiado em cópias (apagadas): `git merge origin/unificacao-v1` sobre
`origin/cutover-20260923-0923`, com a linha em `940f3b14` e outra vez em `de4dec2b`. Os 11 livros ficaram iguais byte a byte aos da produção; o
código ficou igual ao da linha; `regras/italy_contracts_onboarded.json` recebeu as duas
mudanças (TTL da T1 + D9 do G1), com JSON válido. Os 13 conflitos são só no mapa gerado.

```bash
VIVA=$HOME/orca/workspaces/eame-sintonia/source-curator-service-v1
CASA=$HOME/orca/workspaces/eame-sintonia/ponte-viva
# 1. esperar o worker ocioso; PARAR.flag; parar o observador (como no CUTOVER-RUNBOOK passo 1)
# 2. na CASA: gravar os livros sujos da ponte, e juntar a linha
cd $CASA && git add -A curadoria candidatas && git commit -q -m "ponte: livros antes de instalar a linha"
git fetch -q origin && git merge --no-ff --no-commit origin/unificacao-v1
git diff --name-only --diff-filter=U        # esperado: so docs/operacao/CENSO... e *.generated.json
for f in $(git diff --name-only --diff-filter=U); do git checkout -q --theirs -- "$f"; git add "$f"; done
git commit -q -m "instala unificacao-v1 na producao (livros = producao)"
# 3. conferir: nenhum livro mudou
for f in candidatas/FONTES-CANDIDATAS.json curadoria/LIFECYCLE-LEDGER-V1.json curadoria/italy_contracts_curator.json; do
  git diff --quiet HEAD~1 HEAD -- $f && echo "igual $f" || echo "MUDOU $f  <- ABORTAR"; done
# 4. no bot: os livros vivos dele estao sujos; gravar numa copia, trocar, repor
#    (mesma mecanica do CUTOVER-RUNBOOK passos 2, 7 e o DESFAZER)
# 5. cadeia do mapa na CASA, push, relancar bot e observador
```

🛑 se algum livro «MUDOU», ou se aparecer conflito fora do mapa gerado → `git merge --abort`, relançar.

### 0 · Pré-condições (tudo verde, ou não se começa)

| # | o quê | comando | abortar se |
|---|---|---|---|
| 0.1 | B1, B2, B3 fechados | este ficheiro, secção 1 | algum aberto |
| 0.2 | gates do §25 | `BIG-COLLECTION-GATES.md`, medido no dia | algum ≠ YES/SAFE |
| 0.3 | ensaio offline na árvore instalada | `py scripts/micro_coleta/ensaio_offline.py --fontes=<3 PRONTAS> --duas-passagens --provar-rollback` | C6/C8 FAIL, REFETCH ≠ 0, ROLLBACK ≠ igual |
| 0.4 | portão num Postgres 16 limpo | GitHub: `banco-descartavel.yml` → `portao-big-collection` verde no HEAD instalado | vermelho |
| 0.5 | egresso IT | `py superficie/rede.py --portao-de-egresso IT` → `EGRESS_GATE` aberto, `IT` | outro país / BLOCKED |
| 0.6 | um só bot | `py curadoria/supervisor.py --estado` → worker IDLE, `PID_CHECK_NAO_SEI` vazio | worker a trabalhar: esperar |
| 0.7 | memória livre | o dono pode estar a editar vídeo | falta de memória: **esperar e repetir**, nunca reduzir a coorte |
| 0.8 | tudo de pé depois de um reinício | a tela azul das ~13 h de 23/09 deixou **desligados** o supervisor do bot, o observador da ponte e **a Sala real (54330)**; nada disso volta sozinho. Religar pelo dono: `~\sintonia-sala-italia\ligar_sala.cmd`, o supervisor e o observador como no `CUTOVER-RUNBOOK.md` passo 8/10. Os livros sobreviveram (75 e 73 JSON válidos) | algum em baixo |

### 1 · Parar a escrita concorrente

`PARAR.flag` no bot (esperar o supervisor sair) e parar o observador. O portão fica
congelado: a coorte do passo 2 é a que corre. Anotar a hora: começa a paragem do bot.

### 2 · A coorte (sem rede, sem banco)

```
py scripts/micro_coleta/micro_coleta.py plano > C:\bc\plano.json
py ferramentas/big_collection/coorte_unica.py --plano=C:\bc\plano.json --saida=C:\bc\COORTE-BIG-COLLECTION.json
```

⚠️ **G3 (23/09 ~21:00Z): a coorte é UMA, e está num só ficheiro.** Havia três tabelas do
coletor (`regras/italy_contracts_onboarded.json`): a da linha (173), a da produção (176, com
IT-T2-034, IT-T2-051, IT-T9-021) e a da BC2 (191, com 18 novas) — nenhuma continha as outras, e
instalar só a linha **perdia as 18 da BC2**. `origin/coorte-unica-v1` = produção + linha + BC2,
com a tabela juntada **pelo dono** (`onboardar_rotas_provadas.py --aplicar`, livros vivos de
20:55Z): 176 → **193** (+17; IT-T7-100 fica, duplicada de IT-T7-043; 2.ª passagem 0).
`COORTE-BIG-COLLECTION.json` só aceita a PRONTA do plano que TAMBÉM tem contrato executável
(aquisição igual à do portão), régua DETAIL/v1 e canário com prova ≤ 7 dias, fonte a fonte.
Medido às 21:00Z: **COORTE_BIG_COLLECTION = 18**, 0 duplicadas
(`ferramentas/big_collection/COORTE-BIG-COLLECTION-V1.json`). **No passo I, instalar
`origin/coorte-unica-v1` em vez de `origin/unificacao-v1`** até a linha a absorver.
🛑 abortar se `COORTE_BIG_COLLECTION = 0` ou se alguma PRONTA sair em `FORA` com `PROVAS`.

**Provisória até ao cutover (bot Luciano, 23/09 19:20).** As 18 de hoje são a lista
PROVISÓRIA (`ESTADO: PROVISORIA`). A coorte FINAL só se congela **depois** da instalação (passo
I) e da demotion (B5), com os livros já instalados:

```
py scripts/micro_coleta/micro_coleta.py plano > C:\bc\plano.json
py ferramentas/big_collection/coorte_unica.py --plano=C:\bc\plano.json --congelar ^
   --instalacao=<commit instalado na CASA> --demotion=<referencia da B5> --saida=C:\bc\COORTE-BIG-COLLECTION.json
```

Sem os dois o `--congelar` recusa. **Nunca** usar a contagem de READY do livro (143) como coorte:
a coorte é só a lista `COORTE` do ficheiro.

✅ **CONGELADA em 24/09 03:29Z (1.ª onda, sem a R1 — D25; B5 = ninguém sai, bot Luciano 00:30).**
Sobre o vivo instalado: bot `source-curator-service-v1` @ **`8eec2e2a`** (M5G), supervisor
STOPPED e worker DOWN durante a leitura, egresso IT PASS antes e depois. Os 4 livros tinham o
mesmo sha256 antes e depois (os do `LIVROS_SHA256` do ficheiro). Plano do vivo: 37 ELIGIBLE →
18 PRONTAS / 19 BLOQUEADAS. **COORTE_BIG_COLLECTION = 18**, 0 duplicadas, `ESTADO: CONGELADA`
(`ferramentas/big_collection/COORTE-BIG-COLLECTION-V1.json` = `C:\bc\COORTE-BIG-COLLECTION.json`).
IT-T5-049 fica FORA pelo próprio plano (`ROTA:CAPABILITY_BLOCK`). Nenhuma Veterinária/IZS (D26);
fronteira listada: IT-T10-022 (Zootecnica International, imprensa de avicultura = produção animal,
não vet/IZS) — fica, o Curator decide.

A ferramenta do vivo (`8eec2e2a`) ainda é a de antes do `--congelar`; correu-se a deste ramo
(`0bb7eafd`) sobre os livros do vivo, trocando só a linha `RAIZ`, sem `.pyc` e com `--saida` fora
do vivo (nada escrito no vivo; `git status` do vivo: os mesmos 10 livros sujos):

```
# C:\bc\g3\correr_no_vivo.py <coorte_unica.py> <raiz do vivo> <args...>
src = Path(sys.argv[1]).read_text(encoding="utf-8")
src = src.replace("RAIZ = Path(__file__).resolve().parents[2]", "RAIZ = Path(%r)" % sys.argv[2])
sys.argv = [sys.argv[1]] + sys.argv[3:]; exec(compile(src, sys.argv[0], "exec"), {"__name__": "__main__"})

(no vivo) PYTHONDONTWRITEBYTECODE=1 py scripts/micro_coleta/micro_coleta.py plano > C:\bc\g3\plano.json
PYTHONDONTWRITEBYTECODE=1 py C:\bc\g3\correr_no_vivo.py ferramentas/big_collection/coorte_unica.py <vivo> ^
   --plano=C:\bc\g3\plano.json --congelar --instalacao=8eec2e2a ^
   --demotion="B5: ninguem sai (bot Luciano, 24/09 00:30)" --saida=C:\bc\g3\COORTE-BIG-COLLECTION.json
```

Medido na BC2 (23/09 ~15:30), depois do onboardar: portão **37** → **19 PRONTAS**
(IT-T10-018, -021, -022, IT-T2-034, IT-T2-051, IT-T5-090, IT-T7-017, -021, -033, -042,
-043, -100, -112, -117, -118, -121, -123, -135, -141), **18 bloqueadas** com motivo. (BC1,
~12:59: 10 PRONTAS.) **Abortar** se `FILTRO_AUSENTE` (código 3).

### 3 · Checkpoint da Sala real (IMEDIATAMENTE antes)

```
py scripts/micro_coleta/provar_backup_da_sala.py --saida=C:\bc\backup
```

Faz o dump (só leitura), confere que a Sala não mudou durante o dump, restaura numa base
descartável e compara o md5 das 5 tabelas. **Provado hoje** (23/09 15:50Z): dump 2 166 408
bytes (sha256 `e6388fc09970…`), `IGUAL_A_SALA_REAL: true`. SALA_BEFORE: `sala_de_espera`
61 · `raw_asset` 1405 · `storage_object` 1097 · `derived_artifact` 908 · `collection_run`
389. **Anotar o caminho do dump**: é o único caminho de volta.

🛑 `PROVA_VALE: false`, `IGUAL_A_SALA_REAL: false` ou `INDICE_TEM_SALA_DE_ESPERA: false`.

### 4 · As variáveis da Sala

As quatro do `MICRO-RUNBOOK.md` passo 4, e `BANCO_DESCARTAVEL_URL` vazia. Sem
`SINTONIA_SALA_BACKEND=POSTGRES`, a Sala cai calada num ficheiro.

### 5 · Correr (só com B2 fechado)

Com a A5 na linha: `py scripts/micro_coleta/micro_coleta.py correr --autorizado-pelo-dono
--saida=C:\bc\corrida`, uma fonte de cada vez, pela porta canónica, com a coorte do
portão no instante. O comando exato é o que a A5 entregar (robots lido antes de cada
fonte, ritmo dentro da fonte, teto de pedidos por site).

### 6 · Circuit breakers (§27) — o que se olha e o que se faz

| disjuntor | detector concreto | acção |
|---|---|---|
| dois workers | processos `orquestrador`/`italy_executor` > 1 ao mesmo tempo; o bot tem de estar parado (passo 1) | Ctrl+C → R |
| corrupção / banco inconsistente | alguma contagem da Sala **desce**; erro do Postgres; `ModosEmConflito`, `SalaIndisponivel` | parar → R |
| bypass de gate | `CRITERIOS.C6` ≠ PASS no relatório; fonte sem veredito do portão no instante | parar → R |
| perda de proveniência | `C4.PROVENANCE_FAILURES` > 0 | parar; ler antes de R |
| INSERT manual na Sala | proibido: só o orquestrador escreve. Qualquer `psql` com escrita = R | R |
| runaway de erro | 3 fontes seguidas FAILED, ou uma corrida > 30 min | parar |
| pedidos em massa | pedidos por site > teto da A5 (A4 usava 5 por passagem); > 3 × MAX_TARGETS | parar |
| robots/policy | robots proíbe a entrada ou o caminho das matérias e a fonte correu | parar → R |
| custo | alguma rota não `italia-recorrente` (paga) | parar |
| source of truth divergente | o veredito do portão no instante ≠ o plano do passo 2 | parar essa fonte |
| egresso | o país sai de IT a meio | parar TUDO; nunca continuar pela rede do Brasil |
| não explicado em larga escala | SIM ou NÃO_SEI muito fora do ensaio | parar, medir |

Ao parar: **PRESERVAR → MEDIR → BÍBLIA → KNOW-HOW → SYSTEM MAP → GIT → DADOS → CORRIGIR
→ TESTAR → RED TEAM → RETOMAR** (§27).

### 7 · Depois

SALA_AFTER (mesma fotografia do passo 3); retirar o `PARAR.flag`; relançar o observador;
guardar `C:\bc\` fora do TEMP. O defeito conhecido dos duplicados na Sala
(`SALA_ITENS_JA_NA_SALA_POR_OUTRA_CORRIDA`) lê-se como no `MICRO-RUNBOOK.md` passo 6.

### R · Rollback

O do `MICRO-RUNBOOK.md` passo R: `dropdb` + `createdb` com `--maintenance-db`, e
`pg_restore` do dump do passo 3. **Nunca** `pg_restore` por cima da base existente.
Provado duas vezes: com o dump real restaurado numa base descartável (passo 3, md5 igual
nas 5 tabelas) e no ensaio (secção 4).

## 4 · O ensaio (BC1)

Três ensaios offline (`scripts/micro_coleta/ensaio_offline.py`) sobre a árvore da
instalação (passo I) com os livros vivos do bot das 13:01, e as mesmas 3 fontes PRONTAS:
IT-T10-018, IT-T10-022 e IT-T7-033. Sem internet: um servidor local serve 304 páginas
guardadas. Postgres descartável com o nome `sala_italia`. Prova completa em
`ferramentas/big_collection/BC1-ENSAIO.json`; relatório do ensaio 3 em
`ferramentas/big_collection/BC1-RELATORIO-PASSAGEM-ENSAIO.md`.

| ensaio | o que prova | resultado |
|---|---|---|
| 1 · livros do commit da troca | o coletor recusa quem o portão não aprova | as 3 **recusadas pelo próprio coletor** (`ESTADO_NAO_READY`: no commit das 09:36 ainda estavam CANARY_PENDING), 0 pedidos |
| 2 · `--duas-passagens --provar-rollback` | o rollback desfaz uma corrida que mudou algo | Sala 8 → 12 → **8**; raw 30 → 55 → **30**; as 5 tabelas com o **mesmo md5** de antes; `dropdb` + `createdb` + `pg_restore`, todos com código 0 |
| 3 · `--duas-passagens` | a estrada inteira, e o relatório C1..C9 | abaixo |

Ensaio 3, 1.ª passagem: 3/3 HEALTHY · 55 documentos = 55 RAW = 55 DERIVED · Admission
**SIM 12 / NÃO 10 / NÃO SEI 33** · Sala **+12** · proveniência **0 falhas** · 61 pedidos,
todos ao servidor local (0 à internet) · 134 + 50 + 62 s por fonte · US$ 0.
C3, C4, C5, C6 (zero bypass), C7, C8 (0 SIM errado no gabarito) e C9: **PASS**. C2:
PENDENTE_HUMANO (alguém lê as capas a confirmar). C1: **FAIL, esperado offline**: o egresso
fica NÃO SEI, e o ensaio nunca finge um IT.

2.ª passagem: **0** re-pedidos desnecessários, **0** «mudou» falso, **0** «novo» falso, 55
conhecidas puladas, 6 pedidos (só os índices), 0 RAW novos, Sala +0, **0 itens em dobro
na Sala**.

**Não provado pelo ensaio:** a rede real (robots, ritmo, egresso IT), a Sala real (só foi
lida pelo `pg_dump`) e a coorte inteira (10 PRONTAS). Estimativa sem rede: ~80 s por fonte;
com a rede e a pausa entre fontes, **NÃO SEI**.
