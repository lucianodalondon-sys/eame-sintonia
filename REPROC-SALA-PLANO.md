# REPROC-SALA-PLANO · reprocessar o tempo e o lugar da Sala depois dos lotes 1 e 2

Ramo `reproc-sala-plano-v1`, a partir do vivo `83de0ccd`, com os três ramos juntos
(sem conflito): `conserto-regua-v1` (`a139caad`) · `leitor-data-yt-v1` (`4dd00308`) ·
`dedup-doc-v1` (`79091f73`). **Nada instalado. A Sala real só foi lida.** O ensaio correu em
Postgres **descartável**, desligado no fim.

**Nenhuma migração nova.** Os três ramos não trazem SQL: o caderno de revisões é o da 033, já
aplicada na Sala (`APLICADA b980c76e…`). O reprocesso só **acrescenta** revisões; a linha
original da Sala não muda; o RAW não é aberto para escrita (só se leem os bytes, e só com o
sha256 certo).

<!-- ENSAIO -->

## ROTEIRO para a Sala real (para o coordenador)

Em Git Bash, a partir de uma cópia **do código instalado** (vivo depois dos lotes 1 e 2), chamada
`$M`. Nada disto corre sem o LOCK-PESADO livre e ≥5 GB de memória.

```bash
M=/c/Users/London1/orca/workspaces/eame-sintonia/source-curator-service-v1   # o vivo, JÁ com os lotes 1 e 2
S=$HOME/sintonia-sala-italia
VIVA=$M
export PATH="$HOME/orca/pgtmp/pgsql/bin:$PATH"
export PGPASSFILE="$S/pgpass.conf"
export SINTONIA_SALA_DSN="$(tr -d '\r\n' < $S/SALA_DSN.txt)"
export SINTONIA_SALA_BACKEND=POSTGRES
export SINTONIA_PSQL_EXE="$HOME/orca/pgtmp/pgsql/bin/psql.exe"
O=$S/reproc-lotes-1-2-$(date +%Y%m%d-%H%M%S)
```

**0 · o código certo.** Os lotes 1 e 2 têm de estar instalados, e o roteiro tem de existir lá:
```bash
cd $M && git log --oneline -1
for c in 4dd00308 a139caad 79091f73; do git merge-base --is-ancestor $c HEAD && echo "$c OK" || echo "$c FALTA"; done
ls scripts/reproc_sala/reprocessar_sala.sh
```
Se a INTEGRA juntou os ramos por outra via (commits reescritos), conferir pelo conteúdo — os três
têm de dar ≥1:
```bash
grep -c TERMO_DE_COMPARACAO leis/fato_do_texto.py             # lote 2 · conserto-regua
grep -c TIPOS_QUE_PUBLICAM coleta/executor_texto_de_html.py   # lote 2 · conserto-regua
grep -c 'itemprop' coleta/executor_texto_de_html.py           # lote 1 · leitor-data-yt
grep -c executor_texto_de_html admissao/reprocessar_tempo_lugar.py   # a versão carimba o leitor
```
Três `OK` (ou os greps ≥1) e o ficheiro existe. Um `FALTA` → **PARAR**: reprocessar com o código de antes grava
revisões com a versão antiga (e a próxima passada, com o código novo, grava outra vez).

**1 · preflight.** `cmd //c "$(cygpath -w $S/preflight_sala.cmd)"` → `PREFLIGHT=PASS`. Outra → PARAR.

**2 · backup.** `cmd //c "$(cygpath -w $S/backup_sala.cmd)"` → `BACKUP=PASS` e o caminho
`$S/backups/sala_italia-AAAAMMDD-HHMMSS.dump`. Anotar em `B=` e `sha256sum "$B"`.

**3 · parar o robô.** `echo "reproc-lotes-1-2 $(date -Iseconds)" > $VIVA/curadoria/PARAR.flag`;
esperar o supervisor sair e matar o observador **como no `CUTOVER-RUNBOOK.md` passo 1**. O roteiro
recusa-se a correr na Sala real sem este ficheiro.

**4 · o roteiro inteiro, num comando.**
```bash
cd $M && bash scripts/reproc_sala/reprocessar_sala.sh "$O" --sala-real 2>&1 | tee "$O.log"
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
