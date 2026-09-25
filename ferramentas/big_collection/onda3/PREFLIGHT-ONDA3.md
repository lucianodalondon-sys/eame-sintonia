# PREFLIGHT-ONDA3 — o roteiro da 3.ª onda web, adaptado a `e5cd691f`

Ramo `preflight-onda3-v1`, nascido do vivo `origin/servico-20260923-0923 @ e5cd691f`
(PACOTE-TEMPO-LUGAR; migração 033 na Sala real). **Só leitura, sem rede.** Nada instalado,
nada corrido, nada congelado. Medido em 25/09/2026 ~18:20 (-03).

> Este ficheiro é um roteiro, não uma autorização. Cada passo com 🔐 precisa de ordem do
> coordenador (regra D65: nenhuma instalação no vivo sem o coordenador).

---

## 0. O que já está medido (ponto de partida)

| o quê | valor medido | como |
|---|---|---|
| vivo (bot) | `source-curator-service-v1` @ `e5cd691f` = `origin/servico-20260923-0923` | `git rev-parse` |
| supervisor | 1 vivo (PID 55664), worker `IDLE` | `py curadoria/supervisor.py --estado` na pasta do bot |
| Sala real (SELECT, `default_transaction_read_only=on`) | `sala_de_espera` 78 · `raw_asset` 1474 · `storage_object` 1166 · `derived_artifact` 976 · `collection_run` 421 | psql, opções **antes** da DSN |
| Sala vs fim da 2.ª onda | **igual** ao `SALA_FIM` de `ONDA2-WEB-20260925-0812` → nada escrito desde então | `ONDA-WEB-ESTADO.json` |
| coorte oficial no commit | `ESTADO=CONGELADA`, **28 fontes, é a da 2.ª onda** (instalação `d235c32a`, B5 «ninguém sai») | `COORTE-BIG-COLLECTION-V1.json` |
| sha256 da coorte no commit | `06f87b97761d73281bc341d87d7a644ec0c5014a291265db2b8372732bf4977f` (blob; o disco com CRLF dá `5401845a…`) | `git show HEAD:… \| sha256sum` |
| `?` no nome da pasta (IT-T2-050) | **consertado em `e5cd691f`**: `guardarRaw` → `pastaDoDocumento` codifica `* ? " < > \|` (FECHAR-ONDA2-B, D60 c) | `coleta/italy_pilot_collect.mjs:155` |
| corrida que rebenta a meio | escreve a sua linha `ABORTED` + `PEDIDOS_POR_HOST` (FECHAR-ONDA2, `9e8a25f1`) | idem, `executarRodada` |
| RETORNO.json | deixa de dizer SUCCESS quando o coletor falha (`b523ac79`, D60 b) | `coleta/italy_executor.py` |
| egresso | consenso de 3 verificadores (ipwho.is, ip-api.com, ifconfig.co) em `superficie/rede.py` | código |
| PROVA-TETO da 2.ª onda | **NAO_SEI definitivo** (21 corridas, 79 pedidos, máx. 5/domínio, 0 acima; IT-T2-050 sem linha) | `provas/prova_teto_dominio.py` |

Consequência para a 3.ª onda: com os dois consertos, **uma corrida que falha já não pode deixar a
PROVA-TETO cega**. Na 3.ª onda, NAO_SEI deixa de ser aceitável: é FAIL a investigar.

---

## 1. As decisões que o roteiro NÃO toma (para o coordenador)

1. **🔐 A coorte nova tem de entrar no commit do vivo.** `onda_web.py --correr` lê a coorte de
   `ferramentas/big_collection/COORTE-BIG-COLLECTION-V1.json` **desta árvore** e confere com
   `git show HEAD:`. Congelar só no disco não chega: o ficheiro tem de ser commitado no ramo do
   vivo (como na 2.ª onda, `290e7349`). Isso é uma instalação.
2. **Reutilizar a coorte da 2.ª onda ou congelar uma nova?** A missão pede `--congelar`; se o
   plano de hoje der as mesmas 28, a coorte nova só muda `INSTALACAO` e a data.
3. **A referência B5** para `--demotion=`: a da 2.ª onda era «B5: ninguem sai (bot Luciano,
   24/09 00:30; mantida na 2.a onda)». Manter ou mudar é do dono.
4. **Ordem da coorte e o D38.** Quem vem primeiro gasta o teto do domínio (na 2.ª onda: 7 fontes
   ficaram `TETO_DOMINIO`, p. ex. IT-T2-146 depois de IT-T2-145 no `arpa.veneto.it`). Rodar a
   ordem entre ondas continua em aberto.
5. **`--historico=`**: `onda_web.py` aceita os `ONDA-WEB-ESTADO.json` das ondas anteriores para
   prever pedidos. Recomendo passar o da 2.ª onda. **NÃO SEI** se a 2.ª onda o recebeu (o
   `ONDA-WEB-ESTADO.json` dela não o regista).

---

## 2. O roteiro (Windows `cmd`, na pasta do bot)

```
set BOT=%USERPROFILE%\orca\workspaces\eame-sintonia\source-curator-service-v1
set ONDA=%USERPROFILE%\sintonia-sala-italia\ondas\ONDA3-WEB-<AAAAMMDD-HHMM>
set BC=C:\bc\onda3
cd /d %BOT%
```

### P0 · Pré-condições (tudo verde, ou não se começa)

```
git rev-parse HEAD                              & rem = e5cd691f... (ou o commit da coorte, se o 🔐 1 já entrou)
git fetch origin & git rev-parse origin/servico-20260923-0923   & rem local == remoto
powershell -File %LOCALAPPDATA%\Temp\mem.ps1    & rem >= 5 GB livres
py curadoria\supervisor.py --estado             & rem worker IDLE, PID_CHECK_NAO_SEI vazio
git status --porcelain > %BC%\status-antes.txt  & rem fotografia dos livros sujos (não commitar)
```

### P1 · Parar o robô (PARAR.flag)

```
type nul > curadoria\PARAR.flag
py curadoria\supervisor.py --estado             & rem esperar PARA_FLAG / worker parado
powershell -c "Get-CimInstance Win32_Process | ? { $_.CommandLine -match 'supervisor.py|ciclo_continuo' -and $_.Name -match 'python|py.exe' } | select ProcessId,CommandLine"
```
Esperar **0** processos do supervisor/worker. ⚠️ No Git Bash, `taskkill //PID` falha: usar
`powershell Stop-Process` se for mesmo preciso matar. Anotar a hora: começa a paragem.

### P2 · Egresso pelo portão (VPN IT)

```
py superficie\rede.py --portao-de-egresso IT    & rem EGRESS_GATE aberto, país IT por consenso
```
🛑 outro país, `BLOCKED` ou sem consenso → não seguir. Nunca correr pela rede do Brasil.

### P3 · 🔐 Plano e coorte congelada (sem rede, sem banco)

```
py scripts\micro_coleta\micro_coleta.py plano > %BC%\plano.json
py ferramentas\big_collection\coorte_unica.py --plano=%BC%\plano.json --congelar ^
   --instalacao=<commit instalado no vivo> --demotion="<referência B5 decidida>" ^
   --saida=%BC%\COORTE-BIG-COLLECTION-V1.json
```
Conferir: `ESTADO=CONGELADA`, `COORTE` > 0, `DUPLICADAS_NA_COORTE` vazio, nenhuma PRONTA em `FORA`
com `PROVAS`. 🛑 `FILTRO_AUSENTE` (código 3) ou coorte 0.
Depois, **pelo coordenador**: copiar para `ferramentas\big_collection\COORTE-BIG-COLLECTION-V1.json`,
`git add` **só esse ficheiro** (os livros sujos ficam fora), commit, push, e cadeia do mapa sob
LOCK-PESADO. O sha256 a declarar é o do blob:
```
git show HEAD:ferramentas/big_collection/COORTE-BIG-COLLECTION-V1.json | sha256sum
```

### P4 · Backup da Sala real (IMEDIATAMENTE antes)

```
py scripts\micro_coleta\provar_backup_da_sala.py --saida=%BC%\backup
```
🛑 `PROVA_VALE: false`, `IGUAL_A_SALA_REAL: false` ou `INDICE_TEM_SALA_DE_ESPERA: false`.
Anotar o caminho e o sha256 do dump: é o único caminho de volta. SALA_BEFORE esperado hoje:
78 / 1474 / 1166 / 976 / 421.

### P5 · As variáveis da Sala (as cinco + uma vazia)

```
set SINTONIA_SALA_BACKEND=POSTGRES
set /p SINTONIA_SALA_DSN=<%USERPROFILE%\sintonia-sala-italia\SALA_DSN.txt
set SINTONIA_COLLECTION_DSN=%SINTONIA_SALA_DSN%
set SINTONIA_PSQL_EXE=%USERPROFILE%\orca\pgtmp\pgsql\bin\psql.exe
set SINTONIA_ARMAZEM_RAIZ=%USERPROFILE%\sintonia-sala-italia\armazem
set BANCO_DESCARTAVEL_URL=
```

### P6 · O plano da onda (`--so-plano`, sem rede e sem Sala)

```
py ferramentas\big_collection\onda_web.py --so-plano ^
   --historico=%USERPROFILE%\sintonia-sala-italia\ondas\ONDA2-WEB-20260925-0812\ONDA-WEB-ESTADO.json ^
   --saida=%BC%\so-plano
```
Conferir: `PODE_CORRER=true`, coorte `CONGELADA`, máximo previsto por domínio ≤ 5, lista de
`TETO_DOMINIO` previstos. 🛑 `COORTE_FORA_DO_GIT` ou `COORTE_ALTERADA_FORA_DO_COMMIT`.

### P7 · Correr (uma onda, uma pasta nova)

```
py ferramentas\big_collection\onda_web.py --correr --sha256=<sha do blob, P3> ^
   --historico=%USERPROFILE%\sintonia-sala-italia\ondas\ONDA2-WEB-20260925-0812\ONDA-WEB-ESTADO.json ^
   --saida=%ONDA%
```
O disparador nomeia o livro `%ONDA%\TETO-ONDA.json` (D38) e recusa reaproveitar o de outra onda.
`--retomar` **só** para a mesma onda. Disjuntores (os da BC5 + domínio acima de 5 → PARA TUDO):
egresso sai de IT · Sala desce · corrida > 30 min · 3 FAILED seguidas · C6 ≠ PASS · C4 com cadeia
partida · pedidos por site acima do teto.

### P8 · PROVA-TETO (depois, só leitura)

```
py provas\prova_teto_dominio.py --livro data\collection-ledger\italy\runs.ndjson ^
   --onda %ONDA%\ONDA-WEB-ESTADO.json --json %ONDA%\PROVA-TETO.json
```
Tem de dar **PASS**. Conferir também, domínio a domínio, `runs.ndjson` contra `%ONDA%\TETO-ONDA.json`
(na 2.ª onda: 79 = 79 em 21 de 22 domínios). NAO_SEI agora é defeito a investigar.

### P9 · Religar

```
"%SINTONIA_PSQL_EXE%" -X -A -t -c "set default_transaction_read_only=on; select ..." "%SINTONIA_SALA_DSN%"   & rem SALA_AFTER: nenhuma contagem desce
del curadoria\PARAR.flag
powershell -c "Start-Process powershell -ArgumentList '-NoLogo','-NoExit','-Command',\"Set-Location '%BOT%'; & 'C:\Users\London1\AppData\Local\Programs\Python\Launcher\py.exe' curadoria/supervisor.py\""
py curadoria\supervisor.py --estado             & rem SUPERVISOR_ALIVE true
```
Confirmar no SO **exatamente um** supervisor (um `py.exe` + o seu `python.exe` filho).
Guardar `%BC%` fora do TEMP e listar no relatório com sha256.

### R · Rollback (só se for preciso desfazer a Sala)

`MICRO-RUNBOOK.md` passo R: `dropdb` + `createdb` com `--maintenance-db`, e `pg_restore` do dump
do P4. **Nunca** `pg_restore` por cima da base existente.

---

## 3. Lista de verificação (15 pontos)

| # | ponto | verde quando |
|---|---|---|
| 1 | vivo no commit certo | `HEAD` do bot = commit autorizado; local == `origin/servico-20260923-0923` |
| 2 | memória | ≥ 5 GB livres; LOCK-PESADO livre para a cadeia do mapa (P3) |
| 3 | livros fotografados | `git status` + sha256 dos livros sujos guardados antes do P1 |
| 4 | robô parado | `PARAR.flag` posto; 0 supervisor/worker no SO |
| 5 | Sala de pé | porta 54330 responde; SELECT read-only devolve as 5 contagens |
| 6 | egresso IT | `rede.py --portao-de-egresso IT` aberto, país IT por consenso |
| 7 | coorte congelada | `ESTADO=CONGELADA`, `INSTALACAO` = commit do vivo, B5 declarada |
| 8 | coorte no commit | disco == `git show HEAD:` (JSON) e sha256 do blob anotado |
| 9 | backup da Sala | `PROVA_VALE` e `IGUAL_A_SALA_REAL` true; caminho + sha256 do dump anotados |
| 10 | variáveis | as cinco definidas, `BANCO_DESCARTAVEL_URL` vazia, armazém fora do repo |
| 11 | plano da onda | `--so-plano`: `PODE_CORRER=true`, máx. previsto ≤ 5 por domínio |
| 12 | pasta nova | `%ONDA%` não existe antes (sem `TETO-ONDA.json` de outra onda) |
| 13 | disjuntores | nenhum disparou; nenhuma contagem da Sala desceu |
| 14 | PROVA-TETO | **PASS** (nenhuma corrida sem linha); livro do teto = `runs.ndjson` por domínio |
| 15 | religado | `PARAR.flag` retirado; exatamente 1 supervisor no SO; livros não perdidos |

---

## O que NÃO fiz

Não instalei, não congelei, não corri, não abri rede, não parei o robô. A Sala foi só lida
(`SELECT count(*)` com `default_transaction_read_only=on`).
