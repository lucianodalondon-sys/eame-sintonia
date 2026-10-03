#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════
# A TRAVA DO DESVIO — migration aplicada é artefato imutável
#
# O aplicador sabia que «a 022 já rodou». Não sabia se **o ficheiro 022 ainda
# era o mesmo**. Uma migration aplicada e depois editada continuava a dar SKIP,
# para sempre, e o desvio ficava invisível.
#
#     SKIP CEGO É PROIBIDO.
#     VERSÃO IGUAL COM SHA DIFERENTE É DRIFT.
#
# Este ficheiro REPRODUZ o defeito e prova o conserto, num Postgres 16 que
# morre no fim do job. Não toca produção: a URL vem do banco descartável, e a
# tranca de `preservar_coleta_no_postgres.py` recusa qualquer outra.
# ═══════════════════════════════════════════════════════════════════════
set -uo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
URL="${BANCO_DESCARTAVEL_URL:?falta BANCO_DESCARTAVEL_URL}"

case "$URL" in
  *@localhost:*|*@127.0.0.1:*) ;;
  *) echo "RECUSADO: '$URL' nao e local. Esta prova nunca corre contra producao."
     exit 1;;
esac

falhou=0
ok() { printf '  PASS  %-50s %s\n' "$1" "${2:-}"; }
mal() { printf '  FAIL  %-50s %s\n' "$1" "${2:-}"; falhou=1; }

# Um sitio proprio, para nao mexer nas migrations de verdade.
LAB="$(mktemp -d)/migrations"
mkdir -p "$LAB"
trap 'rm -rf "$(dirname "$LAB")"' EXIT

cat > "$LAB/900_fixture.sql" <<'SQL'
create table if not exists public.fixture_do_teste (id integer);
SQL

# O aplicador so sabe olhar para `$RAIZ/supabase/migrations`. Em vez de o
# reescrever para aceitar um caminho — o que mudaria o codigo de producao para
# caber num teste — reproduz-se AQUI a mesma decisao, com o mesmo SQL.
livro() { psql "$URL" -X -q -A -t -v ON_ERROR_STOP=1 -c "$1"; }

livro "create table if not exists public.schema_migracao (
         versao text primary key, aplicada_em timestamptz not null default now(),
         resultado text not null, sha256 text not null);" >/dev/null

sha_a=$(sha256sum "$LAB/900_fixture.sql" | cut -d' ' -f1)
psql "$URL" -X -q -v ON_ERROR_STOP=1 -f "$LAB/900_fixture.sql" >/dev/null
livro "insert into public.schema_migracao (versao, resultado, sha256)
       values ('900','APLICADA','$sha_a')
       on conflict (versao) do update set sha256 = excluded.sha256;" >/dev/null
ok "arranjo · a 900 esta aplicada e no livro" "sha=${sha_a:0:12}"

# ── A DECISAO, COMO O APLICADOR A TOMA HOJE ───────────────────────────
decidir() {  # decidir <ficheiro>
  local num sha guardado
  num=$(basename "$1" | cut -c1-3)
  sha=$(sha256sum "$1" | cut -d' ' -f1)
  guardado=$(livro "select sha256 from public.schema_migracao where versao='$num'")
  if [ -n "$guardado" ]; then
    [ "$guardado" = "$sha" ] && { echo "SKIP"; return 0; }
    echo "DRIFT"; return 1
  fi
  echo "APPLY"
}

# ── CASO POSITIVO · ficheiro intacto ──────────────────────────────────
r=$(decidir "$LAB/900_fixture.sql")
[ "$r" = "SKIP" ] && ok "ficheiro intacto da SKIP legitimo" "$r" \
                  || mal "ficheiro intacto devia dar SKIP" "$r"

# ── CASO CENTRAL · o ficheiro mudou depois de aplicado ────────────────
# Era aqui que o aplicador antigo dizia SKIP e seguia em frente.
echo "-- comentario acrescentado depois de a migration ter sido aplicada" \
  >> "$LAB/900_fixture.sql"
sha_b=$(sha256sum "$LAB/900_fixture.sql" | cut -d' ' -f1)

r=$(decidir "$LAB/900_fixture.sql") || true
if [ "$r" = "DRIFT" ]; then
  ok "ficheiro alterado e apanhado como DRIFT" "${sha_a:0:8} -> ${sha_b:0:8}"
else
  mal "ficheiro alterado passou como $r — e o defeito antigo" "$r"
fi

# ── E O APLICADOR REAL FALHA FECHADO, ANTES DE QUALQUER DDL ───────────
# Aponta-se a cadeia canonica para um livro onde a 001 tem um SHA que nao e o
# do ficheiro. Ela tem de parar sem aplicar nada.
livro "insert into public.schema_migracao (versao, resultado, sha256)
       values ('001','APLICADA','$(printf 'f%.0s' {1..64})')
       on conflict (versao) do update set sha256 = excluded.sha256;" >/dev/null
antes=$(livro "select count(*) from information_schema.tables
               where table_schema='public'")
saida=$(bash "$RAIZ/motor/cadeia_canonica.sh" migrations "$URL" 2>&1) && rc=0 || rc=$?
depois=$(livro "select count(*) from information_schema.tables
                where table_schema='public'")

[ "$rc" != "0" ] && ok "a cadeia canonica falha fechado" "rc=$rc" \
                 || mal "a cadeia canonica NAO falhou" "rc=$rc"
echo "$saida" | grep -q "MIGRATION_APLICADA_MUDOU=001" \
  && ok "e diz qual migration mudou" \
  || mal "nao nomeou a migration" "$(echo "$saida" | head -2)"
[ "$antes" = "$depois" ] \
  && ok "nenhuma tabela nova · nao houve DDL depois do drift" "$antes" \
  || mal "houve DDL depois do drift" "$antes -> $depois"

echo
if [ "$falhou" = "0" ]; then
  echo "TRAVA_DE_DRIFT=PASS"; exit 0
fi
echo "TRAVA_DE_DRIFT=FAIL"; exit 1
