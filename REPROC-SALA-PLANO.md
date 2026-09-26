# REPROC-SALA-PLANO · reprocessar o tempo e o lugar da Sala depois dos lotes 1 e 2

Ramo `reproc-sala-plano-v1`, a partir do vivo `83de0ccd`, juntado depois ao vivo `69b0e23f` (lote 1 da
INTEGRA-NOITE) e ao vivo **`278cd489`** (lote 2, instalado 13:55), com os três ramos juntos: `conserto-regua-v1` (`a139caad`) · `leitor-data-yt-v1` (`4dd00308`) ·
`dedup-doc-v1` (`79091f73`).

⚠️ **O lote 2 instalado (`278cd489`) tem o `conserto-regua-v1` (`a139caad`) e o `leitor-data-yt-v1`, mas NÃO o
`dedup-doc-v1`.** Para o reprocesso isto não muda nada: o dedup só decide se uma coleta NOVA ganha linha na Sala
(`pousar`); o reprocesso só acrescenta revisões às linhas que já existem (`rever`), e `admissao/sala_de_espera.py`
não entra na versão do extrator. Por isso o ensaio corre com o **código exato do vivo** (`278cd489`), não com este
ramo. **Nada instalado. A Sala real só foi lida.** O ensaio correu em
Postgres **descartável**, desligado no fim.

**Nenhuma migração nova.** Os três ramos não trazem SQL: o caderno de revisões é o da 033, já
aplicada na Sala (`APLICADA b980c76e…`). O reprocesso só **acrescenta** revisões; a linha
original da Sala não muda; o RAW não é aberto para escrita (só se leem os bytes, e só com o
sha256 certo).

<!-- ENSAIO -->

## PARTE B · LOTE 1 já instalado (vivo `69b0e23f`) · passo (d): reprocessar o TEMPO/LUGAR da Sala com o leitor-data-yt

⚠️ **Desde as 13:55 o vivo é `278cd489` (lote 2).** Se a Parte B **não** correu na Sala, **não a corras agora**:
o ROTEIRO abaixo, uma vez, com o vivo `278cd489`, faz as duas coisas (leitor-data-yt e régua) numa só versão.
Se a Parte B **já** correu, o ROTEIRO abaixo corre por cima, sem problema (as revisões só se acrescentam). O ensaio
mede os dois caminhos.

O lote 1 (INTEGRA-NOITE) já pôs no vivo o `leitor-data-yt-v1` (`4dd00308`): a data de publicação lê
`<meta itemprop="datePublished">` (as páginas do YouTube) e a versão que carimba cada revisão passou a
incluir `coleta/executor_texto_de_html.py`. Do lote 1, só três ficheiros da versão mudaram:
`admissao/reprocessar_tempo_lugar.py`, `coleta/executor_texto_de_html.py` e `orquestrador/orquestrador.py`
(este na rota do bruto, que o reprocesso não usa). Os consertos da régua (lote 2) **não** estão no vivo.

O vivo não tem o roteiro. Corre-se o roteiro **deste ramo** com o **código do vivo** (`CODIGO=`): cada revisão
fica carimbada com a versão do que está instalado, e não com a deste ramo.

```bash
# as mesmas variáveis do ROTEIRO abaixo (S, VIVA, PATH, PGPASSFILE, SINTONIA_SALA_*), e ainda:
R=/c/Users/London1/orca/workspaces/eame-sintonia/tempo-lugar-v1       # esta pasta, com reproc-sala-plano-v1
git -C $R fetch -q origin reproc-sala-plano-v1 && git -C $R status --short   # vazio
git -C $R log --oneline -1                                            # o SHA do PRONTO desta missão
git -C $VIVA log --oneline -1                                         # 69b0e23f (ou depois, sem o lote 2)
O=$S/reproc-lote1-$(date +%Y%m%d-%H%M%S)
```

**d.1 · preflight** e **d.2 · backup** — os passos 1 e 2 do ROTEIRO (`PREFLIGHT=PASS`, `BACKUP=PASS`, anotar `B=` e o sha256).

**d.3 · robô parado** — o passo 3 do ROTEIRO (`PARAR.flag` no vivo).

**d.4 · o roteiro, com o código do vivo:**
```bash
cd $R && CODIGO=$VIVA bash scripts/reproc_sala/reprocessar_sala.sh "$O" --sala-real 2>&1 | tee "$O.log"
```
A primeira linha tem de dizer `codigo que reprocessa: …source-curator-service-v1 @ 69b0e23f`. Última linha:
`REPROC_SALA=PASS`. Os mesmos oito passos (0–7) e as mesmas paragens da tabela do ROTEIRO.

**d.5 · religar** — o passo 5 do ROTEIRO.

**O que muda na vista** (previsão do `LEITOR-DATA-YOUTUBE.md` §4, 94 linhas; ensaio abaixo):
- **nenhum valor** dos quatro campos muda: publicação 44 → 44, lugar da fonte 4 → 4, data do facto 20 → 20,
  lugar do facto 18 → 18. O leitor novo só acha data em páginas do YouTube, e as da Sala já tinham data pelo
  contrato ou pela página;
- muda **só o texto da base** (o porquê) onde a publicação continua `NAO SEI`: passa a dizer também
  `meta itemprop datePublished: ausente` — previsão de ~30 linhas. Em `comparacao.json` aparecem como
  `SO_A_BASE` no campo `published_at`;
- a evidência (`tempo_lugar_evidencia`) dessas linhas também ganha uma revisão, pelo mesmo texto.

<!-- ENSAIO-PARTE-B -->

**Desfazer (Parte B).** Não há valor para desfazer: os quatro valores ficam iguais. As revisões de base não se
apagam (o banco recusa). Para voltar a ler a base antiga, reprocessar com o código de antes (`CODIGO=` uma árvore
em `83de0ccd`) grava uma revisão nova com o texto antigo. Tudo de uma vez: **R2** (o backup do passo d.2),
em § DESFAZER abaixo.

**Decisão do coordenador** (vinha em `LEITOR-DATA-YOUTUBE.md` passo 12): aplicar agora grava ~30 revisões que
só mudam o porquê. Não aplicar também é seguro: quando o lote 2 for instalado, o ROTEIRO grava essas mesmas
bases junto com as mudanças da régua, carimbadas com a versão do lote 2.

## ROTEIRO para a Sala real (para o coordenador)

Em Git Bash. O **código que reprocessa** é o do vivo **depois** do lote 2 — hoje `278cd489` — (`CODIGO=$VIVA`); o **roteiro** vem
desta pasta (`$R`), porque o vivo pode não o ter. Nada disto corre sem o LOCK-PESADO livre e ≥5 GB de memória.

```bash
S=$HOME/sintonia-sala-italia
VIVA=$HOME/orca/workspaces/eame-sintonia/source-curator-service-v1   # o vivo, JÁ com os lotes 1 e 2
R=/c/Users/London1/orca/workspaces/eame-sintonia/tempo-lugar-v1        # esta pasta (reproc-sala-plano-v1)
export PATH="$HOME/orca/pgtmp/pgsql/bin:$PATH"
export PGPASSFILE="$S/pgpass.conf"
export SINTONIA_SALA_DSN="$(tr -d '\r\n' < $S/SALA_DSN.txt)"
export SINTONIA_SALA_BACKEND=POSTGRES
export SINTONIA_PSQL_EXE="$HOME/orca/pgtmp/pgsql/bin/psql.exe"
O=$S/reproc-lotes-1-2-$(date +%Y%m%d-%H%M%S)
```

**0 · o código certo.** Os lotes 1 e 2 têm de estar instalados, e o roteiro tem de existir lá:
```bash
cd $VIVA && git log --oneline -1
for c in 4dd00308 a139caad; do git merge-base --is-ancestor $c HEAD && echo "$c OK" || echo "$c FALTA"; done   # o dedup-doc (79091f73) NÃO é preciso
ls $R/scripts/reproc_sala/reprocessar_sala.sh
```
Se a INTEGRA juntou os ramos por outra via (commits reescritos), conferir pelo conteúdo — os três
têm de dar ≥1:
```bash
grep -c TERMO_DE_COMPARACAO leis/fato_do_texto.py             # lote 2 · conserto-regua
grep -c TIPOS_QUE_PUBLICAM coleta/executor_texto_de_html.py   # lote 2 · conserto-regua
grep -c 'itemprop' coleta/executor_texto_de_html.py           # lote 1 · leitor-data-yt
grep -c executor_texto_de_html admissao/reprocessar_tempo_lugar.py   # a versão carimba o leitor
```
Dois `OK` (ou os greps ≥1) e o ficheiro existe. Um `FALTA` → **PARAR**: reprocessar com o código de antes grava
revisões com a versão antiga (e a próxima passada, com o código novo, grava outra vez).

**1 · preflight.** `cmd //c "$(cygpath -w $S/preflight_sala.cmd)"` → `PREFLIGHT=PASS`. Outra → PARAR.

**2 · backup.** `cmd //c "$(cygpath -w $S/backup_sala.cmd)"` → `BACKUP=PASS` e o caminho
`$S/backups/sala_italia-AAAAMMDD-HHMMSS.dump`. Anotar em `B=` e `sha256sum "$B"`.

**3 · parar o robô.** `echo "reproc-lotes-1-2 $(date -Iseconds)" > $VIVA/curadoria/PARAR.flag`;
esperar o supervisor sair e matar o observador **como no `CUTOVER-RUNBOOK.md` passo 1**. O roteiro
recusa-se a correr na Sala real sem este ficheiro.

**4 · o roteiro inteiro, num comando.**
```bash
cd $R && CODIGO=$VIVA bash scripts/reproc_sala/reprocessar_sala.sh "$O" --sala-real 2>&1 | tee "$O.log"
```
O que ele faz, e onde PARA sozinho:

| passo | faz | PARA se |
|---|---|---|
| 0 | confere que a DSN é a 54330 **e** que veio `--sala-real` **e** que há `PARAR.flag` | falta um dos três |
| 1 | 5 colunas da 033 · revisão/gaveta/vista · gatilho `BEFORE DELETE OR UPDATE` e `BEFORE TRUNCATE` (pela definição) · livro-razão `APLICADA b980c76e6b164d93` | algum difere |
| 2 | fotografia ANTES: nº de linhas + md5 de **todas** as linhas originais · nº de revisões · a vista inteira (`vista-antes.json`) | — |
| 3 | reprocesso **sem escrever** (`plano.json`) e confere que o nº de revisões não mexeu | escreveu |
| 4 | passadas com `--aplicar` até `INSERIDAS = 0` (`passada-N.json`) | 5 passadas e ainda insere |
| 5 | a vista DEPOIS e a comparação campo a campo (`comparacao.json`) | — |
| 6 | as linhas originais: nº + md5 iguais aos do passo 2 | mudaram |
| 7 | tenta UPDATE e DELETE numa revisão, dentro de `BEGIN … ROLLBACK`; o banco tem de recusar os dois, e o caderno fica com o mesmo nº | algum passou |

Última linha: **`REPROC_SALA=PASS`**. Qualquer `PARAR:` → ler a linha, não seguir para o 5.

**5 · religar.** `rm $VIVA/curadoria/PARAR.flag`; relançar supervisor e observador **como no
`CUTOVER-RUNBOOK.md` passos 8/10**.

**6 · guardar a prova.** `sha256sum "$O"/*.json "$O.log"` e anotar no relatório de instalação.

### DESFAZER

As revisões **não se apagam** (o banco recusa). Desfazer é:

- **R1 · voltar a ler o valor de antes:** reprocessar com o código anterior grava uma revisão nova
  com o valor antigo (a vista lê a última). A história fica inteira.
- **R2 · tudo, pelo backup do passo 2** (robô parado; ninguém ligado à base) — a mesma sequência de
  `MIGRACAO-SALA.md` § DESFAZER D2:
```bash
ADMIN="${SINTONIA_SALA_DSN%/*}/postgres"
dropdb --if-exists --maintenance-db="$ADMIN" sala_italia
createdb --maintenance-db="$ADMIN" sala_italia
pg_restore --no-owner --no-privileges -d "$SINTONIA_SALA_DSN" "$B"
cmd //c "$(cygpath -w $S/preflight_sala.cmd)"                                  # PREFLIGHT=PASS
```
