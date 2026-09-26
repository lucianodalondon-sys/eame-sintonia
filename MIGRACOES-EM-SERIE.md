# MIGRACOES-EM-SERIE — 034 → 035 → 036, uma por vez (DA-19)

Missão MIGRACOES-EM-SERIE · 26/09/2026 · ramo `migracoes-em-serie-v1` = `dedup-doc-v1 @ 05aa35c7`
(036 + dedup) **+** `acervo-tempo-lugar-v1 @ 745247d2` (034 lápide, 035 acervo), sem conflito.
**NÃO aplicado na Sala real.** Só o coordenador aplica. Sala real só lida (`pg_dump`/`SELECT` com
`default_transaction_read_only = on`).

## 0 · As três migrações

| nº | ficheiro | o que faz | desfazer |
|---|---|---|---|
| 034 | `034_a_lapide_da_retencao.sql` | tabela nova `lapide_de_retencao` (D20, retenção 30 d YouTube API) | recusa se já houver lápides |
| 035 | `035_o_acervo_guarda_tempo_e_lugar_como_derivado.sql` | troca a regra `derived_artifact_kind_check` para aceitar `TEMPO_LUGAR` | recusa se já houver derivados `TEMPO_LUGAR` |
| 036 | `036_a_sala_guarda_as_versoes_do_documento.sql` | tabela nova `sala_de_espera_versao`, só acrescenta (D79) | apaga a tabela de versões |

⚠️ O `745247d2` **renomeia** a 034 do vivo (`034_o_acervo_guarda_tempo_e_lugar_como_derivado`) para
**035**. A Sala real está na **033** (medido), por isso nenhuma das duas numerações foi aplicada lá — não
há livro-razão a corrigir. Mas **qualquer cópia ou banco onde a 034 antiga já correu** passa a ver
`MIGRATION_034` com outro sha → a cadeia pára (`MIGRATION_APLICADA_MUDOU=034`). Medir antes.

## 1 · Uma por vez: `ferramentas/cadeia_ate.sh NNN`

A cadeia canónica aplica todas as pendentes de uma vez. `ferramentas/cadeia_ate.sh NNN <DSN>` corre a
**mesma** `motor/cadeia_canonica.sh`, numa pasta de etapa com só as migrações ≤ NNN, copiadas byte a
byte (o sha no livro-razão é o mesmo que a cadeia inteira gravaria). Não muda a ordem nem a lei.

## 2 · Runbook para a Sala real — comando exato por passo

**Uma vez, antes de tudo:**

```bash
# LOCK-PESADO + >= 5 GB; robo, supervisor e observador PARADOS
cd <vivo com este ramo instalado>
S=$HOME/sintonia-sala-italia
export PATH="$HOME/orca/pgtmp/pgsql/bin:$PATH" PGPASSFILE="$S/pgpass.conf"
DSN="$(tr -d '\r\n' < $S/SALA_DSN.txt)"
RO="-c default_transaction_read_only=on"
IMP="select 'SALA', count(*)||' '||md5(string_agg(t::text,'' order by run_id,ordem)) from public.sala_de_espera t
     union all select 'REVISOES', count(*)||' '||md5(string_agg(t::text,'' order by run_id,ordem,campo,revisao)) from public.sala_de_espera_revisao t
     union all select 'DERIVADOS', count(*)||' '||md5(string_agg(t::text,'' order by id)) from public.derived_artifact t
     union all select 'RAW', count(*)||' '||md5(string_agg(t::text,'' order by id)) from public.raw_asset t"
B=/c/inst/$(date +%Y%m%d-%H%M)-serie-034-035-036; mkdir -p $B
PGOPTIONS="$RO" psql -X -A -t -c "select max(versao) from schema_migracao" "$DSN"   # tem de dizer 033
```

**Para cada NNN em 034, 035, 036 — nesta ordem, uma de cada vez:**

```bash
N=034   # depois 035, depois 036

# 1 · backup + sha256
PGOPTIONS="$RO" pg_dump -Fc --no-owner --no-privileges -f $B/antes-$N.dump "$DSN"
sha256sum $B/antes-$N.dump | tee $B/antes-$N.dump.sha256

# 2 · impressao ANTES
PGOPTIONS="$RO" psql -X -A -t -c "$IMP" "$DSN" | tee $B/antes-$N.txt

# 3 · aplicar SO esta: MIGRATION_$N=PASS e todas as outras SKIP — senao PARAR
bash ferramentas/cadeia_ate.sh $N "$DSN" | tee $B/up-$N.txt

# 4 · idempotente: MIGRATION_$N=SKIP (ja no livro-razao) HASH=MATCH
bash ferramentas/cadeia_ate.sh $N "$DSN" | tee $B/up2-$N.txt

# 5 · conteudo igual (Sala 94 linhas, revisoes, derivados, RAW)
PGOPTIONS="$RO" psql -X -A -t -c "$IMP" "$DSN" | tee $B/depois-$N.txt
diff $B/antes-$N.txt $B/depois-$N.txt && echo CONTEUDO_IGUAL_$N

# 6 · validacao propria (ver §3 para o esperado)
```

Validação do passo 6:
- **034** — `select to_regclass('public.lapide_de_retencao') is not null` → `t`; `select count(*) from public.lapide_de_retencao` → `0`
- **035** — `select pg_get_constraintdef(oid) like '%TEMPO_LUGAR%' from pg_constraint where conname='derived_artifact_kind_check'` → `t`
- **036** — `select to_regclass('public.sala_de_espera_versao') is not null` → `t`; `select count(*) from pg_trigger where tgname like 'sala_de_espera_versao_%'` → `2`

**No fim:** `bash motor/cadeia_canonica.sh migrations "$DSN"` → tudo `SKIP HASH=MATCH`. Religar robô,
supervisor e observador.

**Desfazer uma NNN** (sempre a última aplicada primeiro — 036, depois 035, depois 034):

```bash
psql -X -v ON_ERROR_STOP=1 --single-transaction -f supabase/desfazer/${N}_desfazer.sql "$DSN"
```

Caminho completo de volta: `pg_restore` do `$B/antes-$N.dump` desse passo.

## 3 · Ensaio completo numa cópia da Sala

ENSAIO_PENDENTE

## 4 · As 2 falhas antigas

As mesmas na base (`d899f09e`, antes de qualquer mudança minha) e depois de juntar o vivo `278cd489`
(medido 26/09 ~14:10, sem rede):

1. `tests/test_lingua_da_porta.py` → **FAIL** `ORuntimeUsaOTradutorEUmSo.test_o_mapa_da_porta_vive_num_sitio_so`
2. `tests/test_estagio_atravessa_a_fronteira.py` → **ERROR** `ACorridaInteiraProvadaACorrer.test_correr_julga_a_unidade_da_fronteira`
   (já registada como falha de base em 25/09, na instalação da régua T2)

Nenhuma das duas toca a Sala, as migrações ou o dedup. Não investiguei a causa: fora desta missão.

Depois de juntar `278cd489`, os testes leves continuam iguais: `test_a_receita_tem_versao` 4/4,
`test_versao_do_documento` 11/11, `test_quem_pousa_entrega_o_armazem` 4/4, `test_a_rota_do_html` 30/30,
`test_forward_instrumentado` 21/21, `test_o_pedido_atravessa` 19/19, `test_a_linhagem_do_reaproveitamento`
30/30, `test_a_ponte_do_derived` 33/33, `test_fonte_atravessa` 21/21; e só as 2 acima falham.
