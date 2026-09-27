# MIGRACAO-SALA (D68) · a 033 única · ramo `migracao-sala-v1`

**Quem aplica na Sala real é o coordenador.** Esta bancada NÃO tocou na Sala real: leu-a só
com `default_transaction_read_only=on` e com um `pg_dump` (que é só leitura), e testou tudo
em Postgres **descartáveis**, incluindo o ensaio geral numa **cópia** da Sala real.

## 1. O que a 033 faz — só acrescenta

`supabase/migrations/033_a_sala_guarda_a_base_as_chaves_e_as_revisoes.sql`

```
sha256 no checkout desta máquina (CRLF, autocrlf=true)   b980c76e6b164d93fc7d293d7e7399aa0b6faa575bdbfb2ea03468095458a938
sha256 no repositório / Linux (LF)                       6329261b3fca05cb…
desfazer: supabase/desfazer/033_desfazer.sql (CRLF)       d9ce56fc5be0ed808064d835757700c53c9ee0acd04528417067c3e713692302
```

A Sala real guarda o sha **CRLF** (a 032 está lá como `218082f5…`, o sha do ficheiro CRLF).
Aplicar a partir de um checkout NESTA máquina.

| | objeto | de quem |
|---|---|---|
| A | `sala_de_espera.published_at_basis`, `source_location_basis` (text, default `'NAO SEI'`) | TEMPO-E-LUGAR (D61) |
| A | `sala_de_espera.completude_tempo_lugar` (json: PROVADA/CALCULADA/NAO SEI das 4 perguntas) | D62 |
| A | `sala_de_espera.tempo_lugar_evidencia` (json: espécie, precisão, cálculo, expressão e trecho do facto; precisão e 2.ª fonte da publicação, CONFLITO; precisão da sede) | DA-7/D70 LUGAR-FATO + DA-9 |
| B | `sala_de_espera.janela_declarada` + trava da forma | 4 chaves — copiado tal e qual do desenho `6c65c57a` |
| C | tabela `sala_de_espera_gaveta` (vazia; D66: ninguém a escreve) | REROUTE |
| D | tabela `sala_de_espera_revisao` (só acrescenta — UPDATE/DELETE/TRUNCATE recusados por gatilho) + vista `sala_de_espera_atual` (última revisão, senão o original) | TEMPO-E-LUGAR §7 C |

**Não entraram:** colunas próprias de precisão (vão dentro de `tempo_lugar_evidencia`, como
a D62 da nuvem das 4 chaves já faz dentro de `janela_declarada`); a `033_a_lapide_da_retencao`
(YouTube — não foi pedida na D68; se entrar, é **034**).

⚠️ **ORDEM: MIGRAÇÃO PRIMEIRO, CÓDIGO DEPOIS.** O código deste ramo (e do `tempo-lugar-v1`,
que aponta para o mesmo commit) escreve as colunas novas: contra uma Sala SEM a 033, o 1.º
`pousar` FALHA ALTO (não grava calado). O código velho contra a Sala COM a 033 continua a
funcionar — as colunas têm default e as linhas antigas leem «não medido».

⚠️ **A nuvem das 4 chaves**: quando a linha dela juntar, o `033_a_sala_guarda_as_quatro_chaves.sql`
dela **deixa de existir** e o teste do default dela passa a ler ESTE ficheiro (o DDL e o default
são os dela, byte a byte).

## 2. O que foi provado (Postgres descartável; nunca a Sala real)

| prova | resultado |
|---|---|
| `tests/test_migracao_033_sala.py` (14+1): sobe; escritor antigo lê o default; `pousar` escreve as bases; retry ≠ conflito; revisão não muda a linha; vista lê a ÚLTIMA; 2× não duplica; UPDATE/DELETE/TRUNCATE recusados; só campos da lista; linha inexistente recusada; DESFAZER + subir de novo | **15/15** |
| `tests/mutacao_migracao_033.py` — trava desligada · vista lê a 1.ª · dedupe desligado · leitura ignora revisões · desfazer esquece o livro-razão · banco aceita rever o TEXTO | **6/6 pegas** |
| `tests/test_tempo_e_lugar_atravessa.py` + mutação do encanamento | 43 · **17/17** |
| **ensaio geral na CÓPIA da Sala real** (`provas/migracao_033_ensaio_copia.py`, dump só-leitura `179b7633…` de 25/09 13:58) | abaixo |

### O ensaio geral, passo a passo, na cópia (78 linhas, última migração 032)

| passo | resultado |
|---|---|
| UP pela cadeia | 001–032: **31 × SKIP HASH=MATCH**; **MIGRATION_033=PASS**; nenhuma outra aplicada |
| validação | 5 colunas · revisão/gaveta/vista existem · 2 gatilhos · livro-razão `033 APLICADA b980c76e…` · vista = tabela nas 78 |
| reprocessar as 78 pela porta | 78 linhas, 0 sem livro, 60 com página (sha conferido) · **455 revisões** |
| reprocessar outra vez | **0 inseridas**, 468 já eram assim |
| **as 78 linhas originais** | **iguais** (md5 das 24 colunas antes = depois) |
| contagem pela vista | publicação **36** · lugar da fonte **5** · data do facto **18** (1 calculada) · lugar do facto **12** |
| DESFAZER | código 0 · **esquema igual ao da cópia, byte a byte** · 78 linhas |
| UP de novo | 31 × MATCH · 033 PASS |

Leitura à mão (uma pessoa, pelos trechos — pode ter erro de um item): data do facto **16 certas
/ 2 erradas** («luglio» é conselho; um «2025» é ano de comparação); lugar do facto **~10
plausíveis / 2 imprecisos** («Italy» para um evento em Roma; 5 cidades para o Popdays, que foi em
Roma). O falso «oggi = hoje em dia» da 1.ª medição desapareceu (D64 da LUGAR-FATO).

## 3. ROTEIRO para a Sala real (numerado, comandos exatos)

Em Git Bash, a partir de uma cópia do ramo `migracao-sala-v1` **nesta máquina** (chamada `$M`).
Nada disto corre sem o LOCK-PESADO livre e ≥5 GB de memória.

```bash
M=/c/Users/London1/orca/workspaces/eame-sintonia/<pasta com migracao-sala-v1 @ SHA>
S=$HOME/sintonia-sala-italia
VIVA=$HOME/orca/workspaces/eame-sintonia/source-curator-service-v1
export PATH="$HOME/orca/pgtmp/pgsql/bin:$PATH"
export PGPASSFILE="$S/pgpass.conf"
export SINTONIA_SALA_DSN="$(tr -d '\r\n' < $S/SALA_DSN.txt)"
export SINTONIA_SALA_BACKEND=POSTGRES
export SINTONIA_PSQL_EXE="$HOME/orca/pgtmp/pgsql/bin/psql.exe"
```

**0 · o ficheiro certo.** `sha256sum $M/supabase/migrations/033_*.sql` → tem de ser
`b980c76e6b164d93…`. Outro valor → **PARAR** (é outro ficheiro; o livro-razão ficaria a
apontar para ele para sempre).

**1 · preflight.** `cmd //c "$(cygpath -w $S/preflight_sala.cmd)"` → última linha
`PREFLIGHT=PASS`. Outra → PARAR.

**2 · backup.** `cmd //c "$(cygpath -w $S/backup_sala.cmd)"` → `BACKUP=PASS` e o caminho
`$S/backups/sala_italia-AAAAMMDD-HHMMSS.dump`. Anotar em `B=` e `sha256sum "$B"`.

**3 · parar o robô.** `echo "migracao-033 $(date -Iseconds)" > $VIVA/curadoria/PARAR.flag`;
esperar o supervisor sair e matar o observador **como no `CUTOVER-RUNBOOK.md` passo 1**
(a consulta do passo 0 de lá não pode devolver `supervisor|worker|ponte_automatica`).

**4 · fotografia antes.**
```bash
psql -X -A -t -c "select count(*) from sala_de_espera" "$SINTONIA_SALA_DSN"          # anotar: linhas
psql -X -A -t -c "select max(versao) from schema_migracao" "$SINTONIA_SALA_DSN"      # 032
```

**5 · aplicar a 033 (UP).**
```bash
cd $M && bash motor/cadeia_canonica.sh migrations "$SINTONIA_SALA_DSN"
```
Esperado: 31 linhas `SKIP (ja no livro-razao) HASH=MATCH` e `MIGRATION_033=PASS`.
`MIGRATION_APLICADA_MUDOU=…` → **PARAR** (nada foi aplicado: a cadeia falha antes do DDL).
`MIGRATION_033=FAIL` → nada ficou meio aplicado (`--single-transaction`); PARAR e ler o erro.

**6 · SELECTs de validação.**
```bash
psql -X -A -t "$SINTONIA_SALA_DSN" <<'SQL'
select string_agg(column_name, ',' order by column_name) from information_schema.columns
 where table_name='sala_de_espera' and column_name in ('published_at_basis','source_location_basis',
 'completude_tempo_lugar','tempo_lugar_evidencia','janela_declarada');        -- 5 nomes
select to_regclass('public.sala_de_espera_revisao') is not null,
       to_regclass('public.sala_de_espera_gaveta') is not null,
       to_regclass('public.sala_de_espera_atual') is not null;                -- t|t|t
select count(*) from pg_trigger where tgname like 'sala_de_espera_revisao_%'; -- 2
select resultado, sha256 from schema_migracao where versao='033';             -- APLICADA|b980c76e…
select count(*) from sala_de_espera_atual;                                    -- = passo 4
SQL
```

**7 · reprocessar pela porta — primeiro SEM escrever.**
```bash
cd $M
LIV="$VIVA/data/collection-ledger/italy/observations.ndjson;$HOME/orca/workspaces/eame-sintonia/*/data/collection-ledger/italy/observations.ndjson"
RZ="$S/armazem;$HOME/orca/workspaces/eame-sintonia/*"
PYTHONUTF8=1 py admissao/reprocessar_tempo_lugar.py --livros "$LIV" --raizes "$RZ" --saida /tmp/plano-033.json
```
Esperado (se a Sala ainda tiver as 78): `SAEM_DE_NAO_SEI` 36 / 5 / 18 / 12. Se a Sala tiver
mais linhas, os números sobem — anotar.

**8 · reprocessar — ESCREVER as revisões** (a linha original não muda):
```bash
PYTHONUTF8=1 py admissao/reprocessar_tempo_lugar.py --livros "$LIV" --raizes "$RZ" --aplicar --saida $S/reprocesso-033-1.json
PYTHONUTF8=1 py admissao/reprocessar_tempo_lugar.py --livros "$LIV" --raizes "$RZ" --aplicar --saida $S/reprocesso-033-2.json
```
A 1.ª: `INSERIDAS` ≈ 455 (78 linhas). A 2.ª: **`INSERIDAS: 0`** — se não for 0, PARAR.

**9 · contagem por campo, pela vista.**
```bash
psql -X -A -t -F' | ' "$SINTONIA_SALA_DSN" -c "select count(*),
  count(*) filter (where published_at <> 'NAO SEI'), count(*) filter (where source_location <> 'NAO SEI'),
  count(*) filter (where fact_time <> 'NAO SEI'), count(*) filter (where fact_location <> 'NAO SEI'),
  count(*) filter (where revisoes > 0) from sala_de_espera_atual"
```

**10 · religar.** `rm $VIVA/curadoria/PARAR.flag`; relançar supervisor e observador **como no
`CUTOVER-RUNBOOK.md` passos 8/10**. O código que está no robô continua a funcionar com a 033
(os defaults). Instalar o código deste ramo no robô é **outro passo, depois**, pelo processo de
instalação de sempre.

### DESFAZER (dois níveis)

**D1 · só o esquema** (apaga as revisões e as colunas novas; as linhas da Sala ficam):
```bash
psql -X -v ON_ERROR_STOP=1 --single-transaction -f $M/supabase/desfazer/033_desfazer.sql "$SINTONIA_SALA_DSN"
psql -X -A -t -c "select count(*) from schema_migracao where versao='033'" "$SINTONIA_SALA_DSN"   # 0
```
Provado na cópia: o esquema volta **byte a byte** ao de antes, e a 033 volta a subir depois.

**D2 · tudo, pelo backup do passo 2** (robô parado; ninguém ligado à base):
```bash
ADMIN="${SINTONIA_SALA_DSN%/*}/postgres"
dropdb --if-exists --maintenance-db="$ADMIN" sala_italia
createdb --maintenance-db="$ADMIN" sala_italia
pg_restore --no-owner --no-privileges -d "$SINTONIA_SALA_DSN" "$B"
cmd //c "$(cygpath -w $S/preflight_sala.cmd)"                                  # PREFLIGHT=PASS
```
(É a mesma sequência de `scripts/micro_coleta/ensaio_offline.py::Base.restaurar`.)

## 4. Provas fora do Git (caminho + sha256)

Pasta `C:/Users/London1/auditoria-madrugada/tempo-lugar/`:
```
179b76339560fc21b3a38a196c892ebc4e44162ed2f3620c3c6e25b9f40d0b20  sala-real-copia.dump        (pg_dump só-leitura, 13:58)
46d7fe0235f3c8812cd947e378a9f4d6f37a7d4089c6d59270e77d6148933e82  ensaio-033.json
defc94515a74fbaf518015d229a827b5c6b29616eead8b99a1784828239530c4  ensaio-033-reprocesso-1.json
7d084bfb7eed5323f9ddff8b18e3f444b4707731c5a21bda7f5b24b9736033be  ensaio-033-reprocesso-2.json
b1e5db0293a906780ddacb66d9bb68b5745dfc002d61667b7f5b5fb50d0815c2  mutacao-033.log
```
⚠️ O dump e os reprocessos têm o TEXTO das 78 da Sala: ficam fora do Git de propósito.

## EM PALAVRAS SIMPLES

- **O que é:** uma "reforma" do banco da Sala que só **acrescenta gavetas**, nunca tira nem troca
  nada. As gavetas novas guardam de onde veio cada data e cada lugar, quão certo é cada um, as 4
  chaves da outra equipe, e um **caderno de correções**.
- **O caderno de correções** só aceita páginas novas. Apagar ou rasurar é recusado pelo próprio
  banco. A notícia original nunca muda; quem lê vê a última correção.
- **Testei numa cópia da Sala real**, não na Sala. Na cópia, as 78 notícias passaram de nada para:
  data de publicação em **36**, lugar de quem publica em **5**, data do fato em **18** e lugar do
  fato em **12**. Rodar duas vezes não duplica nada. E o "desfazer" deixou o banco exatamente
  como estava.
- **O que muda para você:** o coordenador pode aplicar seguindo o roteiro. Primeiro faz o backup,
  depois para o robô, aplica, confere e religa. Se algo der errado, há dois jeitos de voltar, os
  dois testados.
