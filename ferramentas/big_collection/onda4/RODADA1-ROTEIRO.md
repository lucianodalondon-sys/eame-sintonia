# RODADA 1 DA 4.ª ONDA — o roteiro de hoje (26/09, a partir das 19:58:33)

Para o coordenador. Ramo `rodada1-comando-v1` = o vivo `278cd489` (lote 2) + a ordem pelo rendimento
(`29092399`). Tudo o que está aqui foi corrido a seco numa cópia do vivo, com 0 pedidos à rede.

## ⚠️ ANTES DE TUDO: o vivo `278cd489` NÃO tem a ordem pelo rendimento

O lote 2 instalou o disparador como `rodadas-v1` (`bc77648e`). A ordem pelo rendimento e a janela que lê
os recibos das outras missões (`29092399`, aceite às 14:00) **ficaram de fora**. Medido a seco, às 14:1x,
com o comando real `--correr --rodada=1` nas duas versões:

| versão | a rodada 1 | IT-T7-172 (georgofili) | pedidos a seco |
|---|---|---|---|
| **V**: o vivo `278cd489` | 38 fontes, 174 pedidos (ordem justa) | **está**: às 19:58 pediria `georgofili.it` menos de 24 h depois de VOZES (14:21Z), e a janela desta versão não vê o recibo de VOZES | 0 |
| **N**: `rodada1-comando-v1` | **33 fontes, 152 pedidos** (T5 no fim) | fica para a rodada 2 (abre 27/09 11:22) | 0 |

**Recomendo instalar `rodada1-comando-v1` antes das 19:58.** É fast-forward do vivo: o vivo é antepassado
direto, e o conflito é 0. Mexe em 4 ficheiros de código, `rodadas.py`, `tests/test_rodadas.py`,
`provas/rodadas_mutacao.py` e `ensaio_rodada.py` (novo, não corre sozinho), e em 3 documentos.
O mapa tem de ser regerado (a INTEGRA).
Sem isto, o comando abaixo recusa `--rendimento`/`--recibos` (o vivo não os conhece) e só corre a
versão V, **com a colisão**.

## O comando exato (do vivo, depois de instalado o ramo)

```
cd /d %USERPROFILE%\orca\workspaces\eame-sintonia\source-curator-service-v1
set O=%USERPROFILE%\sintonia-sala-italia\ondas
set SI=%USERPROFILE%\sintonia-sala-italia
py ferramentas\big_collection\rodadas.py --correr --rodada=1 ^
   --sha256=eb7b6ab75056cff37b892cb7e9e59a553f6b9048ff8a5db961c532e643f0b9e4 ^
   --base=%O%\ONDA4-RODADAS ^
   --historico=%O%\ONDA2-WEB-20260925-0812\ONDA-WEB-ESTADO.json,%O%\ONDA3-WEB-20260925-1934\ONDA-WEB-ESTADO.json ^
   --livros-do-dia=%O% ^
   --rendimento=%SI%\intelligence-experimental\EXPD78-R2-20260926T135653Z\R1-X-R2-E-FONTES.json ^
   --recibos=%SI%\vozes-agronomos,%SI%\micro-prova,%SI%\pesquisadores-t6 ^
   --inicio=2026-09-26T19:58:33-03:00
```

- A primeira execução grava `%O%\ONDA4-RODADAS\RODADAS-PLANO.json` (com o sha256 da coorte). As rodadas
  seguintes (amanhã em diante) usam **o mesmo comando** com `--rodada=2`, `--rodada=3`… e leem esse plano.
- **Antes das 19:58:33 o comando PARA sozinho** (`JANELA_24H`, `ABRE_EM=2026-09-26T22:58:33+00:00`) sem
  chamar o portão nem pedir nada. Medido a seco: 0 tentativas de rede nas duas versões.

## Os passos, por ordem

| # | passo | comando | conferir | PARAR se |
|---|---|---|---|---|
| 0 | vivo certo | `git -C <vivo> rev-parse HEAD` e `git ls-remote origin servico-20260923-0923` | = o commit instalado (o de `rodada1-comando-v1`), local == remoto; `grep -c rendimento ferramentas\big_collection\rodadas.py` > 0 | outro commit, ou 0 |
| 1 | VPN pelo portão de consenso | `py superficie\rede.py --portao-de-egresso IT --sem-cache` | `EGRESS_GATE: PASS`, país IT, ≥ 2 votos | BLOCKED, outro país, ou menos de 2 votos |
| 2 | backup da Sala | `py scripts\micro_coleta\provar_backup_da_sala.py --saida=%O%\ONDA4-RODADAS\backup-r1` (com as variáveis do passo 3a) | `PROVA_VALE: true`, `IGUAL_A_SALA_REAL: true`; anotar caminho e sha256 do dump e o SALA_BEFORE (5 contagens) | qualquer `false` |
| 3 | parar o robô | `type nul > curadoria\PARAR.flag`; `py curadoria\supervisor.py --estado` | 0 processos `supervisor.py`/`ciclo_continuo` no SO (`Get-CimInstance Win32_Process`) | o worker não pára |
| 3a | variáveis da Sala | `set SINTONIA_SALA_BACKEND=POSTGRES` · `set /p SINTONIA_SALA_DSN=<%SI%\SALA_DSN.txt` · `set SINTONIA_COLLECTION_DSN=%SINTONIA_SALA_DSN%` · `set SINTONIA_PSQL_EXE=%USERPROFILE%\orca\pgtmp\pgsql\bin\psql.exe` · `set SINTONIA_ARMAZEM_RAIZ=%SI%\armazem` · `set BANCO_DESCARTAVEL_URL=` | as seis definidas; a DSN **não** se imprime | falta alguma |
| 4 | so-plano | o comando acima com `--so-plano` no lugar de `--correr --rodada=1` | RODADA 01: **33 fontes, 152 pedidos, máx. 5/domínio, janela ABERTA** (depois das 19:58:33); `PODE_CORRER: true`; `COORTE_ESTADO: CONGELADA` | outro número, janela com data, ou PODE_CORRER false |
| 5 | correr a rodada 1 | o comando acima | o disparador faz: portão antes → onda (`RODADA-01`) → portão depois → PROVA-TETO → relatório `--estado=`; fim com `PAROU_NA_RODADA: null` e `"1": "FECHADA"` | PARADA (ver o `PORQUE` em `RODADAS-ESTADO.json`) |
| 6 | prova-teto (independente) | `py provas\prova_teto_dominio.py --livro data\collection-ledger\italy\runs.ndjson --onda %O%\ONDA4-RODADAS\RODADA-01\ONDA-WEB-ESTADO.json --json %O%\ONDA4-RODADAS\RODADA-01\PROVA-TETO.json` | **PASS**; máx. ≤ 5 por domínio; `TETO-ONDA.json` = `runs.ndjson` domínio a domínio | FAIL ou NAO_SEI |
| 7 | relatório | ler `%O%\ONDA4-RODADAS\RODADA-01\relatorio\RELATORIO-PASSAGEM.md` (o disparador já correu `micro_coleta relatorio --estado=`) | C1..C9; C1/C3 lidos pelo `--estado`; C2 com a V2 | C6 ≠ PASS, C4 com cadeia partida |
| 8 | reconciliar a Sala (só SELECT) | ver abaixo | `collection_run` = corridas com documento; `raw_asset` e `sala_de_espera` destas corridas = o delta da Sala | não bate |
| 9 | religar o robô | `del curadoria\PARAR.flag`; `powershell -c "Start-Process powershell -ArgumentList '-NoLogo','-NoExit','-Command',\"Set-Location '<vivo>'; & 'C:\Users\London1\AppData\Local\Programs\Python\Launcher\py.exe' curadoria/supervisor.py\""` | exatamente 1 supervisor no SO; `--estado` RUNNING | 0 ou 2 |

**Reconciliar (passo 8), só leitura:**
```
set PGOPTIONS=-c default_transaction_read_only=on
py -c "import json,subprocess,os;e=json.load(open(r'%O%\ONDA4-RODADAS\RODADA-01\ONDA-WEB-ESTADO.json',encoding='utf-8'));ids=','.join(\"'%%s'\"%%f['RUN_ID'] for f in e['FONTES'] if f.get('RUN_ID'));print(e['SALA_INICIO'],e['SALA_FIM']);[print(t,subprocess.run([os.environ['SINTONIA_PSQL_EXE'],'-X','-A','-t','-c','select count(*) from %%s where run_id in (%%s)'%%(t,ids),os.environ['SINTONIA_SALA_DSN']],capture_output=True,text=True).stdout.strip()) for t in ('collection_run','raw_asset','sala_de_espera')]"
```

## O que a 1.ª rodada vai fazer (N): 33 fontes, 152 pedidos, 33 domínios

A lista, fonte a fonte, está em `ORDEM-RENDIMENTO-ONDA4.md` (secção «As 15 rodadas», rodada 1). Resumo:
A 1 (IT-T10-018) · T10 2 · T3 1 (IT-T3-023) · T2 6 · sem medida 19 · D 4 · **T5 0**. Colisão com
VOZES / MICRO-PROVA 2B / T6: **0**, por todos os domínios que cada fonte toca.

## Rollback

`MICRO-RUNBOOK.md` passo R: `dropdb` + `createdb` com `--maintenance-db`, e `pg_restore` do dump do passo 2.
Nunca `pg_restore` por cima da base.

## EM PALAVRAS SIMPLES

- O comando da rodada de hoje está pronto e foi testado **sem visitar nenhum site**. Nas duas versões
  que testei, ele parou sozinho porque ainda não eram 19:58.
- **Problema:** a versão instalada agora (`278cd489`) não tem a nova ordem. Se rodar assim, visita 38 sites
  em vez de 33 e bate no site georgofili.it, que outra missão já visitou hoje às 11:21. Isso quebra a
  regra de 24 horas.
- **Solução:** instalar o ramo `rodada1-comando-v1` antes das 19:58. É uma atualização simples, sem
  conflito.
- Na hora, a ordem é: conferir a VPN → fazer backup da Sala → parar o robô → ver o plano → rodar →
  conferir as visitas por outro caderno → ler o relatório → conferir a Sala → ligar o robô de novo.
