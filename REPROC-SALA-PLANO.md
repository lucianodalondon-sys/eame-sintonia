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

**Vivo `dc0de726` (17:35, ff de `278cd489`) juntado também.** Não mexe em nenhum dos 10 ficheiros que fazem a
versão do extrator (`CODIGO_DA_VERSAO`) nem em `admissao/sala_de_espera.py`: o reprocesso com `dc0de726` grava
a mesma versão que com `278cd489`, e o ensaio com a cópia de `278cd489` vale para ele.

**Nenhuma migração nova.** Os três ramos não trazem SQL: o caderno de revisões é o da 033, já
aplicada na Sala (`APLICADA b980c76e…`). O reprocesso só **acrescenta** revisões; a linha
original da Sala não muda; o RAW não é aberto para escrita (só se leem os bytes, e só com o
sha256 certo).

## ENSAIO 1 (26/09 22:25–22:31, 3.º da FILA-PESADO) — o ensaio travou o roteiro, e ainda bem

Backup `sala_italia-20260925-193339.dump` (sha256 `a05beb22…`, **80 linhas**, 478 revisões), Postgres descartável,
código do vivo `554c1ec1` (cópia fora do vivo). O que correu bem: 033 validada (5 colunas, 2 gatilhos pela definição,
livro `APLICADA b980c76e…`), passadas até 0 (309 → **0**; na Parte B+vivo 207 → 0), originais: nº e md5 conferidos.

**O que correu mal — e é um defeito do roteiro, não dos consertos:** `plano: 80 linhas · SEM LIVRO 80 · COM PÁGINA 0`.
O Git Bash dá caminhos `/c/Users/…`; o Python do Windows não os abre, e o glob devolveu **zero livros, calado**.
Sem livro nem página, o reprocesso grava `NAO SEI`: na cópia, a vista passou **publicação 38 → 0** (as 38 datas
conhecidas apagadas da leitura; a linha original ficou intacta, como manda a 033). A mesma causa derrubou a comparação
da vista (`PARAR: comparar a vista`). **Na Sala real teria acontecido o mesmo.**

Consertado (`scripts/reproc_sala/reprocessar_sala.sh`): todo caminho que vai para o Python passa por `win` (`/c/x` →
`C:/x`, sem comer o `*` dos globs — o `cygpath` comia); medido: 154 livros achados contra 0. E **dois travões novos
antes de escrever** (passo 3): `SEM_LIVRO` ≤ `SEM_LIVRO_ACEITE` (0) e `PERDAS` — valores conhecidos que o plano poria em
`NAO SEI` (`scripts/reproc_sala/perdas_do_plano.py`) — ≤ `PERDAS_ACEITES` (0). Sobre a saída deste ensaio, o travão
dá `PERDAS=38` e teria parado antes de escrever.

⚠️ O roteiro da MIGRACAO-SALA (passo 7) usava os mesmos caminhos `$HOME/…`. As corridas de 25/09 do coordenador deram
`SEM_LIVRO 0`, logo não foram por este caminho; mas quem o seguir à letra no Git Bash cai no mesmo buraco.

`test_migracao_033_sala` + `test_sala_dedup_por_document_key` no descartável: 31 testes, **1 erro, herdado**
(`test_3_repousar_o_mesmo_e_retry_e_nao_conflito`, já na lista de falhas da BASE do EXTRATORES-V2-JUNTOS).

**Falta:** um 2.º turno de ~15 min na FILA-PESADO para o ensaio com os caminhos consertados — os números da vista
antes → depois saem daí.

## A corrida do coordenador na Sala REAL (27/09 10:35, vivo `2ef6fef8`) — o travão parou antes de escrever

`REPROC_SALA=FAIL` no passo 3: **204 linhas · 100 sem livro · 86 com página** · revisões 478 → **478** (nada escrito).
As 100 são **todas** `IT-T6-2026-09-27-…` da fonte `EU-T5-001` (os estudos do OpenAlex pousados hoje por
`pousar_na_sala.py`, T6-PARA-SALA): não passaram pelo coletor, e o livro deles não é o do coletor.

Contado sobre o `plano.json` dele (sem escrever; `perdas_do_plano.py`, saída em
`C:/Users/London1/auditoria-madrugada/tempo-lugar/perdas-coordenador-1035.json`): **PERDAS = 107**.
- **100 = a data de publicação das 100 T6** (a do OpenAlex, que o contrato não sabe). **Não subir
  `SEM_LIVRO_ACEITE` para 100** — seria apagar da vista as 100 datas.
- **7 nas 104 do coletor**, cada uma com a base nova na lista:
  - 5 × publicação de páginas só-WebPage (IT-T7-013 ×2 «2009-12-18», IT-T5-160 ×3 «2020-02-20») → `NAO SEI`:
    **o conserto da régua a fazer o que devia** (CONSERTO-REGUA, erro 4, lidos à mão);
  - IT-T5-186 lugar do facto «Brindisi ; Roma» → `NAO SEI` («só mencionados»: extratores v2 do lote 3);
  - IT-T3-023 data do facto «2013» → `NAO SEI` (o ano de início de uma atividade não é o tempo do facto:
    DATA-DO-FATO, `2ef6fef8`). **Estas duas são de outros donos: ler antes de aceitar.**

**Conserto neste ramo:** `admissao/reprocessar_tempo_lugar.py --so-com-livro` — uma linha sem livro do coletor
**fica como está** (nenhuma revisão, contada em `SALTADAS_SEM_LIVRO`); sem a opção, tudo como antes.
`tests/test_reproc_sala_so_com_livro.py` 2/2 (e vermelho com o salto desligado). O roteiro usa a opção **sozinho**
quando o código que reprocessa a tem, e o travão passa a contar só as linhas **revistas** sem livro.

**Para correr na Sala real:** instalar este ficheiro (a versão do extrator muda, porque o ficheiro faz parte dela), e
depois o ROTEIRO com `PERDAS_ACEITES=7`, **só** depois de lidas as 2 de outros donos. Esperado pelo plano de 10:35:
100 saltadas, 0 revistas sem livro, perdas 7.

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
