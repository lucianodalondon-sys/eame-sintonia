#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════
# AUDITORIA DA PRODUÇÃO — SÓ SELECT, E É ESSE O PONTO
#
# Substitui o `canario-022`, que era uma porta de MISSÃO ÚNICA e ficou com
# capacidade de escrever produção depois de a missão ter terminado.
#
#     MISSÃO ONE-SHOT TERMINOU → PORTA ONE-SHOT É FECHADA.
#     Não vira daemon. Não vira coletor. Não vira caminho permanente.
#
# O que sobrou tem valor operacional e nenhum poder: ler o livro-razão das
# migrations, comparar cada SHA com o ficheiro do repositório, e conferir que o
# canário continua a ser UM.
#
# Ele recebe `SUPABASE_DB_URL` e mais nada. Sem `SUPABASE_SECRET_KEY`, sem
# `SUPABASE_URL` — aquilo só existia para escrever no Storage, e já não há o
# que escrever.
# ═══════════════════════════════════════════════════════════════════════
set -uo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
URL="${SUPABASE_DB_URL:?falta SUPABASE_DB_URL}"
falhou=0

sanitiza() { sed -E 's#postgres(ql)?://[^ ]*#<URL_OMITIDA>#g'; }
q() { psql "$URL" -X -q -A -t -F '|' -v ON_ERROR_STOP=1 -c "$1" 2>/tmp/e \
        || { echo "ERRO"; sanitiza </tmp/e | head -2; }; }

ok()  { printf '  PASS  %-46s %s\n' "$1" "${2:-}"; }
mal() { printf '  FAIL  %-46s %s\n' "$1" "${2:-}"; falhou=1; }

echo "=== AUDITORIA LIVE · SOMENTE SELECT ==="
echo "medida_em=$(date -u +%Y-%m-%dT%H:%M:%SZ)"

# ── A · CADA MIGRATION APLICADA CONTINUA A SER O MESMO FICHEIRO ───────
# É a lei nova: versão no livro não basta; versão E SHA têm de bater.
echo
echo "-- A · livro-razao x ficheiros do repositorio"
printf '  %-6s %-12s %-18s %-18s %s\n' VERSAO RESULTADO LEDGER_SHA REPO_SHA BATE
divergentes=0
ausentes=0
while IFS='|' read -r versao resultado ledger_sha; do
  [ -z "$versao" ] && continue
  f=$(ls "$RAIZ"/supabase/migrations/${versao}_*.sql 2>/dev/null | head -1)
  if [ -z "$f" ]; then
    printf '  %-6s %-12s %-18s %-18s %s\n' "$versao" "$resultado" \
      "${ledger_sha:0:16}" "-" "FICHEIRO_AUSENTE"
    ausentes=$((ausentes + 1)); continue
  fi
  repo_sha=$(sha256sum "$f" | cut -d' ' -f1)
  if [ "$repo_sha" = "$ledger_sha" ]; then
    bate=SIM
  else
    bate=NAO; divergentes=$((divergentes + 1))
  fi
  printf '  %-6s %-12s %-18s %-18s %s\n' "$versao" "$resultado" \
    "${ledger_sha:0:16}" "${repo_sha:0:16}" "$bate"
done < <(q "select versao, resultado, sha256 from public.schema_migracao
            order by versao")

echo
[ "$divergentes" = "0" ] \
  && ok "nenhuma migration aplicada mudou de conteudo" \
  || mal "LEGACY_APPLIED_MIGRATION_DRIFT" "$divergentes versao(oes)"
[ "$ausentes" = "0" ] \
  && ok "todo registo do livro tem ficheiro no repositorio" \
  || mal "ha registo sem ficheiro" "$ausentes"

# ── B · A 022, NOMEADAMENTE ───────────────────────────────────────────
echo
echo "-- B · a 022"
sha_022=$(q "select sha256 from public.schema_migracao where versao='022'")
repo_022=$(sha256sum "$RAIZ/supabase/migrations/022_o_derivado_ganha_casa.sql" \
           | cut -d' ' -f1)
echo "  LEDGER=$sha_022"
echo "  REPO  =$repo_022"
[ "$sha_022" = "$repo_022" ] \
  && ok "a 022 continua byte a byte a que foi aplicada" \
  || mal "a 022 MUDOU desde que foi aplicada"
[ "$(q "select resultado from public.schema_migracao where versao='022'")" \
  = "APLICADA" ] && ok "a 022 esta como APLICADA no livro" \
                 || mal "a 022 nao esta APLICADA"

# ── C · O CANARIO CONTINUA A SER UM ───────────────────────────────────
echo
echo "-- C · o estado do canario"
n_run=$(q "select count(*) from public.collection_run where run_id like 'IT-CANARY-%'")
n_it=$(q "select count(*) from public.collection_run where source_country='IT'")
n_raw=$(q "select count(*) from public.raw_asset a
           join public.collection_run r on r.run_id=a.run_id
           where r.source_country='IT'")
n_der=$(q "select count(*) from public.derived_artifact")
echo "  IT-CANARY runs=$n_run · collection_run IT=$n_it · raw_asset IT=$n_raw"
echo "  derived_artifact=$n_der"
[ "$n_run" = "1" ] && ok "existe UMA corrida canario, e so uma" \
                   || mal "numero de corridas canario" "$n_run"
[ "$n_raw" = "1" ] && ok "um bruto italiano" || mal "brutos italianos" "$n_raw"
[ "$n_der" = "1" ] && ok "um derivado" || mal "derivados" "$n_der"

q "select 'run='||run_id||' status='||status from public.collection_run
   where run_id like 'IT-CANARY-%'" | sed 's/^/  /'
q "select 'derived id='||id||' raw_asset_id='||raw_asset_id||
          ' sha='||substring(sha256,1,16)||' bytes='||bytes
   from public.derived_artifact" | sed 's/^/  /'

# ── D · A SAUDE DO ACERVO, E OS IDS QUE NAO SE MEXEM ──────────────────
# Nasceu na C-LIVE-025, onde foi preciso congelar o estado antes de escrever e
# prova-lo igual depois. Fica permanente porque a pergunta e permanente:
#
#     COUNT IGUAL NAO E CONJUNTO IGUAL.
#
# Nove chaves estrangeiras de cinco migrations apontam para `raw_asset.id`. Um
# id que se mexe leva todas atras dele, e uma contagem certa nao ve isso. O
# `md5` do CONJUNTO ordenado ve.
echo
echo "-- D · o acervo bruto"
for par in \
  "RAW_ASSET_COUNT|select count(*) from public.raw_asset" \
  "RAW_ASSET_MIN_ID|select coalesce(min(id)::text,'-') from public.raw_asset" \
  "RAW_ASSET_MAX_ID|select coalesce(max(id)::text,'-') from public.raw_asset" \
  "RAW_ASSET_DISTINCT_IDS|select count(distinct id) from public.raw_asset" \
  "RAW_ASSET_DISTINCT_STORAGE_PATHS|select count(distinct storage_path) from public.raw_asset" \
  "PRESERVED_RAW_ASSETS|select count(*) from public.raw_asset where preserved" \
  ; do
  echo "  ${par%%|*}=$(q "${par#*|}")"
done
echo "  RAW_ASSET_ID_SET_MD5=$(q "select coalesce(md5(string_agg(id::text, ',' order by id)),'-') from public.raw_asset")"

# O ENDERECO E O HASH TEM DE SER AFIRMAVEIS. Um caminho em branco ou um hash
# malformado nao e «quase certo»: e uma linha que diz onde esta sem dizer onde.
sem_endereco=$(q "select count(*) from public.raw_asset where storage_path is null or btrim(storage_path) = ''")
sem_hash=$(q "select count(*) from public.raw_asset where sha256 is null or btrim(sha256) !~ '^[0-9a-f]{64}\$'")
[ "$sem_endereco" = "0" ] && ok "todo bruto tem endereco" \
                          || mal "bruto sem endereco" "$sem_endereco"
[ "$sem_hash" = "0" ] && ok "todo bruto tem hash com forma de sha256" \
                      || mal "hash ausente ou malformado" "$sem_hash"

# As colunas que a tabela REALMENTE tem. Sem lista fixa: uma lista fixa
# envelhece a cada migration e passa a reprovar o estado esperado.
echo "  RAW_ASSET_COLUNAS=$(q "select string_agg(column_name, ',' order by ordinal_position) from information_schema.columns where table_schema='public' and table_name='raw_asset'")"

# ── E · O OBJETO E A OBSERVACAO, DEPOIS DA 025 ────────────────────────
# A 025 separou as duas especies. Estas contas sao o contrato dela, e sao
# cobradas — nao apenas impressas.
echo
echo "-- E · o objeto e a observacao"
tem_obj=$(q "select count(*) from pg_class c join pg_namespace n on n.oid=c.relnamespace where n.nspname='public' and c.relname='storage_object' and c.relkind='r'")
tem_col=$(q "select count(*) from information_schema.columns where table_schema='public' and table_name='raw_asset' and column_name='storage_object_id'")
echo "  STORAGE_OBJECT_EXISTS=$tem_obj"
echo "  RAW_ASSET_TEM_storage_object_id=$tem_col"
if [ "$tem_obj" = "1" ] && [ "$tem_col" = "1" ]; then
  echo "  STORAGE_OBJECT_ROWS=$(q "select count(*) from public.storage_object")"
  echo "  STORAGE_OBJECT_RLS=$(q "select relrowsecurity::text from pg_class c join pg_namespace n on n.oid=c.relnamespace where n.nspname='public' and c.relname='storage_object'")"
  echo "  LINKED_RAW_ASSETS=$(q "select count(*) from public.raw_asset where storage_object_id is not null")"
  orfaos=$(q "select count(*) from public.raw_asset where preserved and storage_object_id is null")
  # A LIGACAO E PELO ENDERECO, e nunca pelo sha: dois objetos podem carregar os
  # mesmos bytes, e um join por hash ligaria a copia errada com ar de certa.
  fora_caminho=$(q "select count(*) from public.raw_asset a join public.storage_object o on o.id = a.storage_object_id where o.storage_path is distinct from a.storage_path")
  fora_sha=$(q "select count(*) from public.raw_asset a join public.storage_object o on o.id = a.storage_object_id where o.sha256 is distinct from a.sha256")
  sem_obs=$(q "select count(*) from public.storage_object o where not exists (select 1 from public.raw_asset a where a.storage_object_id = o.id)")
  echo "  PRESERVED_WITHOUT_OBJECT=$orfaos"
  echo "  RAW_STORAGE_PATH_MISMATCHES=$fora_caminho"
  echo "  RAW_STORAGE_SHA_MISMATCHES=$fora_sha"
  echo "  OBJETOS_SEM_OBSERVACAO=$sem_obs"
  [ "$orfaos" = "0" ] && ok "nenhum preservado sem copia" || mal "preservado sem copia" "$orfaos"
  [ "$fora_caminho" = "0" ] && ok "observacao e copia no mesmo endereco" \
                            || mal "ENDERECO DIVERGENTE" "$fora_caminho"
  [ "$fora_sha" = "0" ] && ok "observacao e copia com o mesmo conteudo" \
                        || mal "SHA DIVERGENTE entre observacao e copia" "$fora_sha"
else
  echo "  (a 025 ainda nao esta neste banco — nada a conferir aqui)"
fi

# As travas, lidas de `pg_constraint`. `convalidated` importa: uma trava criada
# NOT VALID e uma promessa sobre o futuro e um silencio sobre o passado.
echo "  CONSTRAINTS_DE_RAW_ASSET:"
q "select '    '||conname||' | '||contype::text||' | convalidated='||convalidated::text
   from pg_constraint where conrelid='public.raw_asset'::regclass order by conname"

# ⚠️ A SENTINELA DA FASE 10 VIROU-SE AO CONTRARIO, E ESSE E O PONTO DELA.
#
# Ela dizia: «esta trava fica — e se um dia desaparecer sem missao que o
# declare, a auditoria grita». A `027` e a missao que o declarou, e a trava
# saiu. A sentinela nao se apaga: inverte-se.
#
#     UMA SENTINELA APAGADA NAO GUARDA NADA.
#     UMA SENTINELA INVERTIDA GUARDA O LADO NOVO.
#
# A partir daqui, o que a auditoria grita e a trava VOLTAR — porque volta-la
# seria juntar outra vez as duas especies que a 025 separou, e nenhuma
# migration desta casa a recria.
uniq_path=$(q "select count(*) from pg_indexes where schemaname='public' and tablename='raw_asset' and indexdef ilike '%unique%' and indexdef ilike '%storage_path%'")
[ "$uniq_path" = "0" ] && ok "o endereco ja nao e identidade da observacao (fase 10)" \
                       || mal "UNIQUE(storage_path) VOLTOU" "duas observacoes no mesmo endereco voltariam a ser uma"

# ── F · A IDENTIDADE DA OBSERVACAO, DEPOIS DA 026 ─────────────────────
# A 026 dá identidade à observação. O contrato dela é cobrado aqui, e não
# apenas impresso — do mesmo modo que o da 025 acima.
echo
echo "-- F · a identidade da observacao"
tem_estado=$(q "select count(*) from information_schema.columns where table_schema='public' and table_name='raw_asset' and column_name='identity_state'")
echo "  RAW_ASSET_TEM_identity_state=$tem_estado"
if [ "$tem_estado" = "1" ]; then
  echo "  IDENTITY_STATE_NOT_NULL=$(q "select attnotnull::text from pg_attribute where attrelid='public.raw_asset'::regclass and attname='identity_state'")"
  com_default=$(q "select count(*) from pg_attrdef d join pg_attribute a on a.attrelid=d.adrelid and a.attnum=d.adnum where d.adrelid='public.raw_asset'::regclass and a.attname='identity_state'")
  echo "  IDENTITY_STATE_TEM_DEFAULT=$com_default"
  sem_estado=$(q "select count(*) from public.raw_asset where identity_state is null")
  echo "  LEGACY_ROWS=$(q "select count(*) from public.raw_asset where identity_state = 'LEGACY_PRE_IDEMPOTENCY'")"
  # O LEGADO NAO PODE TER GANHO IDENTIDADE. Ninguem lhe inventou fonte nem
  # documento na migration, e ninguem lho pode acrescentar depois sem missao.
  legado_com_id=$(q "select count(*) from public.raw_asset where identity_state = 'LEGACY_PRE_IDEMPOTENCY' and (source_id is not null or document_key is not null or document_key_basis is not null)")
  echo "  LEGACY_COM_IDENTIDADE=$legado_com_id"
  echo "  FORWARD_IDENTIFIED_ROWS=$(q "select count(*) from public.raw_asset where identity_state = 'FORWARD_IDENTIFIED'")"
  echo "  FORWARD_IDENTITY_UNPROVEN_ROWS=$(q "select count(*) from public.raw_asset where identity_state = 'FORWARD_IDENTITY_UNPROVEN'")"
  corte=$(q "select coalesce(substring(pg_get_constraintdef(oid) from 'id <= ([0-9]+)'),'-') from pg_constraint where conname='legado_e_anterior_ao_corte'")
  echo "  LEGACY_CUTOFF_VALUE=$corte"
  idx=$(q "select count(*) from pg_index i join pg_class c on c.oid=i.indexrelid where c.relname='raw_identidade_forward_idx' and i.indisvalid and i.indisunique")
  echo "  FORWARD_IDEMPOTENCY_INDEX_VALID=$idx"
  [ "$sem_estado" = "0" ] && ok "nenhuma observacao sem estado de identidade" \
                          || mal "OBSERVACAO SEM ESTADO" "$sem_estado"
  [ "$com_default" = "0" ] && ok "identity_state continua SEM default" \
                           || mal "identity_state GANHOU default" "o esquecimento voltaria a classificar"
  [ "$legado_com_id" = "0" ] && ok "nenhuma identidade inventada no legado" \
                             || mal "LEGADO COM IDENTIDADE" "$legado_com_id"
  [ "$idx" = "1" ] && ok "indice de idempotencia forward valido" \
                   || mal "indice de idempotencia forward" "ausente ou invalido"
  # As seis travas da 026, pelo nome. Uma trava criada e nao validada e uma
  # promessa sobre o futuro e um silencio sobre o passado.
  faltam=""
  for c in estado_de_identidade_tem_vocabulario fonte_real_em_qualquer_estado_forward \
           forward_identificado_exige_identidade forward_sem_prova_nao_finge_chave \
           base_da_chave_tem_vocabulario a_observacao_e_a_copia_falam_do_mesmo_conteudo \
           legado_e_anterior_ao_corte; do
    [ "$(q "select count(*) from pg_constraint where conrelid='public.raw_asset'::regclass and conname='$c' and convalidated")" = "1" ] \
      || faltam="$faltam $c"
  done
  [ -z "$faltam" ] && ok "as sete travas da 026 estao presentes e validadas" \
                   || mal "TRAVA DA 026 AUSENTE OU NAO VALIDADA" "$faltam"
else
  echo "  (a 026 ainda nao esta neste banco — nada a conferir aqui)"
fi

# ── G · A FASE 10, DEPOIS DA 027 ──────────────────────────────────────
# A 026 deu identidade a observacao; a 027 tirou-lhe o endereco de cima. O
# contrato dela e cobrado aqui — e nao apenas impresso.
echo
echo "-- G · a fase 10"
tem_027=$(q "select count(*) from public.schema_migracao where versao='027'")
echo "  LEDGER_TEM_A_027=$tem_027"
if [ "$tem_027" = "1" ]; then
  # A CHAVE DA TENTATIVA SEM PROVA. Sem ela, a fase 10a teria aberto um buraco
  # em vez de uma porta: o indice da fase 9 tem predicado FORWARD_IDENTIFIED, e
  # uma linha sem prova nao o satisfaz. Enquanto o endereco foi unico era ELE
  # que a segurava por acidente.
  idxu=$(q "select count(*) from pg_index i join pg_class c on c.oid=i.indexrelid where c.relname='raw_tentativa_sem_prova_idx' and i.indisvalid and i.indisunique")
  echo "  UNPROVEN_INDEX_VALID=$idxu"
  defu=$(q "select coalesce(max(indexdef),'-') from pg_indexes where indexname='raw_tentativa_sem_prova_idx'")
  echo "  UNPROVEN_INDEXDEF=$defu"
  # ⚠️ `NULLS NOT DISTINCT` NAO E AFINACAO. Uma observacao NAO preservada tem
  # `storage_object_id` nulo, e em Postgres dois nulos sao DISTINTOS num indice
  # unico: sem esta clausula a chave deixaria passar todas as tentativas nao
  # preservadas, em silencio.
  nnd=$(q "select count(*) from pg_indexes where indexname='raw_tentativa_sem_prova_idx' and upper(indexdef) like '%NULLS NOT DISTINCT%'")
  echo "  UNPROVEN_NULLS_NOT_DISTINCT=$nnd"
  # E ela e sobre o OBJETO, e nao sobre o endereco: a fase 11 retira a coluna
  # `storage_path`, e uma chave construida sobre ela nasceria com divida.
  sobre_objeto=$(q "select count(*) from pg_indexes where indexname='raw_tentativa_sem_prova_idx' and indexdef like '%storage_object_id%' and indexdef not like '%storage_path%'")
  echo "  UNPROVEN_SOBRE_O_OBJETO=$sobre_objeto"
  trig=$(q "select count(*) from pg_trigger where tgname='a_identidade_da_observacao_nao_se_reescreve' and not tgisinternal")
  echo "  IDENTITY_IMMUTABILITY_TRIGGER=$trig"
  # ⚠️ SENTINELA DA FASE 11. A COLUNA fica; so a UNICIDADE dela saiu. Se a
  # coluna desaparecer sem missao que o declare, a auditoria grita — que e o
  # mesmo servico que a sentinela anterior prestou a fase 10.
  col=$(q "select count(*) from information_schema.columns where table_schema='public' and table_name='raw_asset' and column_name='storage_path'")
  echo "  COLUNA_STORAGE_PATH_AINDA_EXISTE=$col"
  [ "$idxu" = "1" ] && ok "indice da tentativa sem prova valido" \
                    || mal "indice da tentativa sem prova" "ausente ou invalido"
  [ "$nnd" = "1" ] && ok "a chave da tentativa trata dois nulos como iguais" \
                   || mal "UNPROVEN SEM NULLS NOT DISTINCT" "destranca para toda observacao nao preservada"
  [ "$sobre_objeto" = "1" ] && ok "a chave da tentativa fala do objeto, nao do endereco" \
                            || mal "CHAVE DA TENTATIVA SOBRE O ENDERECO" "nasceria com divida para a fase 11"
  [ "$trig" = "1" ] && ok "a identidade da observacao nao se reescreve" \
                    || mal "TRAVA DE IMUTABILIDADE AUSENTE" "a identidade voltaria a poder ser reescrita"
  [ "$col" = "1" ] && ok "a coluna do endereco fica (a fase 11 e que a retira)" \
                   || mal "COLUNA storage_path DESAPARECEU" "fase 11 nao foi autorizada"
else
  echo "  (a 027 ainda nao esta neste banco — nada a conferir aqui)"
fi

# ── G · O QUE A CADEIA VERIA COMO PENDENTE ────────────────────────────
# O aplicador salta o que esta no livro-razao. Aqui faz-se a mesma conta sem
# escrever nada: saber o que FALTA e tao operacional como saber o que entrou.
echo
echo "-- F · migrations que o livro-razao ainda nao tem"
pendentes=""
for f in "$RAIZ"/supabase/migrations/*.sql; do
  n=$(basename "$f" | cut -c1-3)
  [ "$n" = "008" ] && continue
  [ "$(q "select count(*) from public.schema_migracao where versao='$n'")" = "0" ] \
    && pendentes="$pendentes $n"
done
echo "  MIGRATIONS_PENDENTES=${pendentes:-nenhuma}"

# ── H · PREFLIGHT DE APLICACAO — SOMENTE LEITURA, E PROVADA ───────────
# Nasceu na C-LIVE-PREFLIGHT-READONLY-V1. As seccoes acima medem as leis que
# a casa ja instalou; esta responde a UMA pergunta diferente:
#
#     O LIVE ESTA EM ESTADO CONHECIDO O SUFICIENTE PARA QUE UMA MISSAO
#     POSTERIOR POSSA PEDIR AUTORIZACAO DE APPLY?
#
# Ela NAO aplica nada. Nao e um aplicador com a coragem baixa: e um censo.
#
# E COMECA POR PROVAR QUE NAO PODE ESCREVER. O resto do ficheiro e so
# `select` por disciplina e por guarda de teste — o que faltava era o banco
# CONFIRMAR isso do lado dele. Uma sessao que so escreve `select` por
# convencao e uma sessao que escreve o que lhe mandarem.
#
#     SO USEI SELECT != A SESSAO NAO PODIA ESCREVER.
#
# Se a prova nao vier `on`, esta seccao NAO corre. Nao por medo das queries
# — sao as mesmas — mas porque um preflight que ignora o proprio portao
# nao e um preflight.
echo
echo "-- H · preflight de aplicacao (somente leitura, provada)"

# COMO SE FECHA O PORTAO, E PORQUE NAO E COM PGOPTIONS.
#
# A primeira versao usava `PGOPTIONS='-c default_transaction_read_only=on'`.
# Contra um Postgres descartavel local funcionou a primeira: `on`, e a escrita
# recusada. Contra o banco vivo devolveu isto, medido na corrida 29:
#
#     READ_ONLY_SESSION=off
#
# Nao deu erro. Nao pendurou. Nao avisou. O parametro foi SILENCIOSAMENTE
# IGNORADO, e a sessao veio de escrita — exactamente a sessao que o pedido
# dizia trancar.
#
#     PEDIR NAO E OBTER.
#     UM PORTAO QUE NAO SE CONFERE E UMA CONVENCAO COM AR DE TRANCA.
#
# Se a seccao confiasse no pedido em vez de conferir a resposta, teria corrido
# o preflight inteiro numa ligacao de escrita a chamar-lhe somente leitura. Foi
# a CONFERENCIA que salvou isto, e nao o pedido — e e por isso que ela vem
# antes de qualquer pergunta, e nao depois.
#
# `PGOPTIONS` e parametro de ARRANQUE da ligacao, e um pooler no meio (e o
# Supabase tem um) pode simplesmente nao o encaminhar. `begin read only` e SQL
# comum: atravessa pooler, nao depende de arranque, e quem o faz cumprir e o
# servidor — a mesma garantia por um caminho que existe em toda a parte.
#
# E tudo leva prazo, que e barato e evita a classe de problema em que uma
# ligacao remota fica a espera sem ninguem saber: `PGCONNECT_TIMEOUT` para a
# ligacao, `timeout` para a pergunta inteira.
export PGCONNECT_TIMEOUT=10

ro() { timeout 30 psql "$URL" -X -q -A -t -F '|' -v ON_ERROR_STOP=1 \
         -c "begin read only; $1; commit;" 2>/tmp/ero \
         || { echo "ERRO"; sanitiza </tmp/ero | head -2; }; }

READ_ONLY=$(ro "show transaction_read_only")
echo "  READ_ONLY_SESSION=$READ_ONLY"

if [ "$READ_ONLY" != "on" ]; then
  echo "  READ_ONLY_PROVEN=NO"
  echo "  PREFLIGHT=NOT_MEASURED — a sessao nao provou ser somente leitura."
  echo "  Nenhuma pergunta do preflight foi feita. Isto NAO reprova a"
  echo "  auditoria: as seccoes A-G mediram o que sempre mediram."
else
  echo "  READ_ONLY_PROVEN=YES"

  # ── H1 · O LIVRO-RAZAO EXISTE? ──────────────────────────────────────
  # Primeira pergunta, e eliminatoria. Um banco sem livro-razao nao tem
  # historia do aplicador canonico: reaplicar por cima seria adivinhar.
  ledger=$(ro "select coalesce(to_regclass('public.schema_migracao')::text,'-')")
  echo "  LIVE_SCHEMA_LEDGER_EXISTS=$([ "$ledger" != "-" ] && echo YES || echo NO)"

  if [ "$ledger" = "-" ]; then
    echo "  LIVE_CANONICAL_APPLICATOR_HISTORY=NO"
    echo "  PREFLIGHT=STOP — sem livro-razao nao se decide apply."
  else
    # ── H2 · SAUDE DO LIVRO-RAZAO ────────────────────────────────────
    # Quatro doencas que uma listagem bonita nao mostra: a versao repetida,
    # o resultado fora do vocabulario, o sha em falta, e a versao que o
    # repositorio nao conhece.
    echo "  LEDGER_ROWS=$(ro "select count(*) from public.schema_migracao")"
    echo "  LEDGER_DUPLICATES=$(ro "select count(*) from (select versao from public.schema_migracao group by versao having count(*)>1) d")"
    echo "  LEDGER_INVALID_RESULTS=$(ro "select count(*) from public.schema_migracao where resultado not in ('APLICADA','JA_EXISTIA')")"
    echo "  LEDGER_MISSING_SHA=$(ro "select count(*) from public.schema_migracao where sha256 is null or length(sha256)<>64")"
    echo "  LEDGER_VERSIONS=$(ro "select coalesce(string_agg(versao,',' order by versao),'-') from public.schema_migracao")"

    # ── H3 · O INVENTARIO DAS TABELAS DA COLLECTION ──────────────────
    # EXISTE e QUANTAS LINHAS, por tabela. Estrutura e contagem; nunca
    # corpus. Nenhuma linha de documento e lida aqui.
    echo "  -- tabelas"
    for t in collection_run raw_asset storage_object derived_artifact \
             etapa_da_corrida participacao_na_derivacao \
             documento_estruturado schema_migracao; do
      existe=$(ro "select coalesce(to_regclass('public.$t')::text,'-')")
      if [ "$existe" = "-" ]; then
        printf '  TABELA %-28s EXISTS=NO   ROWS=-\n' "$t"
      else
        printf '  TABELA %-28s EXISTS=YES  ROWS=%s\n' "$t" \
          "$(ro "select count(*) from public.$t")"
      fi
    done

    # ── H4 · AS TRAVAS DE CADA UMA ───────────────────────────────────
    # `convalidated=false` e uma trava que existe no catalogo e NAO foi
    # conferida contra as linhas que ja la estavam. Ela parece uma trava e
    # nao garante o passado.
    echo "  -- travas por tabela (tipo|nome|convalidada)"
    ro "select c.relname||'|'||con.contype::text||'|'||con.conname||'|'||con.convalidated
        from pg_constraint con join pg_class c on c.oid=con.conrelid
        join pg_namespace n on n.oid=c.relnamespace
        where n.nspname='public' and c.relname in
          ('collection_run','raw_asset','storage_object','derived_artifact',
           'etapa_da_corrida','participacao_na_derivacao',
           'documento_estruturado','schema_migracao')
        order by c.relname, con.contype, con.conname" | sed 's/^/    /'
    echo "  CONSTRAINTS_NAO_CONVALIDADAS=$(ro "select count(*) from pg_constraint con join pg_class c on c.oid=con.conrelid join pg_namespace n on n.oid=c.relnamespace where n.nspname='public' and not con.convalidated")"
    # UM NUMERO NAO DIZ EM QUE TABELA. Uma trava por convalidar e uma trava
    # que nao garante o passado, e quem a vai ler precisa do nome dela.
    echo "  QUAIS_NAO_CONVALIDADAS=$(ro "select coalesce(string_agg(c.relname||'.'||con.conname,',' order by c.relname,con.conname),'nenhuma') from pg_constraint con join pg_class c on c.oid=con.conrelid join pg_namespace n on n.oid=c.relnamespace where n.nspname='public' and not con.convalidated")"

    # ── H5 · MIGRATION REGISTADA != TABELA EXISTE ────────────────────
    # As duas perguntas sao diferentes, e a diferenca entre elas E o
    # achado. Uma tabela que existe sem registo no livro significa que
    # alguem a criou por fora do aplicador canonico — e o aplicador vai
    # tentar cria-la outra vez.
    #
    #     REGISTADA SEM TABELA  = o livro mente sobre o que correu
    #     TABELA SEM REGISTO    = o aplicador vai tropecar nela
    echo "  -- a 029 e a 030, pelas DUAS perguntas"
    for par in "029|participacao_na_derivacao" "030|documento_estruturado"; do
      v="${par%%|*}"; t="${par##*|}"
      no_livro=$(ro "select count(*) from public.schema_migracao where versao='$v'")
      a_tabela=$(ro "select coalesce(to_regclass('public.$t')::text,'-')")
      printf '  MIGRATION_%s_IN_LEDGER=%s  %s_EXISTS=%s\n' \
        "$v" "$([ "$no_livro" = "1" ] && echo YES || echo NO)" \
        "$(echo "$t" | tr 'a-z' 'A-Z')" \
        "$([ "$a_tabela" != "-" ] && echo YES || echo NO)"
      if [ "$no_livro" != "1" ] && [ "$a_tabela" != "-" ]; then
        mal "TABELA_SEM_REGISTO_NO_LIVRO" "$t existe e a $v nao esta no livro"
      fi
    done

    # ── H6 · O QUE O LIVRO TEM E O REPOSITORIO NAO ───────────────────
    # A seccao A ja grita se um registo nao tiver ficheiro. Aqui diz-se o
    # conjunto, porque um preflight precisa do conjunto e nao do alarme.
    echo "  EXTRA_IN_LIVE=$(ro "select coalesce(string_agg(versao,',' order by versao),'nenhuma') from public.schema_migracao where versao not in ($(for f in "$RAIZ"/supabase/migrations/*.sql; do printf "'%s'," "$(basename "$f" | cut -c1-3)"; done | sed 's/,$//'))")"
  fi
fi

echo
if [ "$falhou" = "0" ]; then
  echo "AUDITORIA_LIVE=PASS"; exit 0
fi
echo "AUDITORIA_LIVE=FAIL"; exit 1
