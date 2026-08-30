#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════
# A CADEIA CANÔNICA — uma ordem só, para o CI e para a produção.
#
# Este arquivo existe porque a missão exigiu, com todas as letras: "se
# workflow e fresh-db usarem ordens diferentes: PARAR. Uma ordem só."
# Duas listas de passos em dois arquivos divergem — é a mesma doença de
# dois donos da mesma lei, aplicada a um procedimento.
#
#   uso:  cadeia_canonica.sh migrations <PSQL_URL>
#         cadeia_canonica.sh importacoes <PSQL_URL>
#
# `migrations` aplica 001–007 e 009–018 na ordem numérica, deixando a 008
# de FORA: ela confere, não cria, e só faz sentido depois de todas. Quem
# roda a 008 é o chamador, para poder tratar a falha dela como falha de
# conferência e não de aplicação.
#
# `importacoes` aplica o regulatório ANTES do catálogo. A ordem não é
# estética: as 52 linhas ROPF_ONLY do crosswalk não têm lado de produto e
# precisam de um registro regulatório existente para satisfazer a trava
# `crosswalk_tem_pelo_menos_um_lado`. Invertida, a cadeia para.
#
# O ensaio ES-ROPF-PRE-REQUISITO-DO-CATALOGO.sql NÃO entra aqui, nem
# nunca: ele é banco descartável e existe para medir, não para importar.
# ═══════════════════════════════════════════════════════════════════════
set -euo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ETAPA="${1:?uso: cadeia_canonica.sh <migrations|importacoes> <PSQL_URL>}"
URL="${2:?falta a URL do banco}"

# Nunca ecoar a URL. Um erro de psql pode trazê-la dentro da mensagem.
sanitiza() {
  sed -E 's#postgres(ql)?://[^ ]*#<URL_OMITIDA>#g; s#at "[^"]*"#at "<HOST_OMITIDO>"#g'
}

case "$ETAPA" in
  migrations)
    # ── O LIVRO-RAZÃO ─────────────────────────────────────────────────
    # A produção parou aqui, e o diagnóstico foi mais fundo do que a
    # primeira causa. A cadeia reaplicava TODAS as migrations desde a 001 a
    # cada execução, e isso não é seguro neste repositório:
    #
    #   · a 007 cria views que a 009 e a 018 redefinem com outra forma —
    #     `create or replace view` recusa, e foi o que a produção viu;
    #   · pior, a 015 tem `add column if not exists fact_geografia_origem`,
    #     e a 018 APOSENTA essa coluna. Reaplicar a 015 a RESSUSCITARIA.
    #
    # Consertar cada caso seria remendo, e o segundo caso mostra o perigo:
    # um replay pode desfazer uma aposentadoria. A solução é a padrão, e é
    # a que todo migrador sério usa — não reaplicar o que já foi aplicado.
    #
    # O livro-razão é infraestrutura do aplicador, não schema de domínio:
    # por isso ele nasce aqui e não numa migration, e por isso o inventário
    # do pré-voo o conhece pelo nome.
    #
    # Bootstrap: num banco que já tem migrations aplicadas e nenhum
    # registro, a primeira execução aplica o que falta e ANOTA o que já
    # existia — a anotação vem da resposta do banco ("already exists"), não
    # de suposição sobre até onde alguém foi.
    psql "$URL" -v ON_ERROR_STOP=1 -q -c "
      create table if not exists public.schema_migracao (
        versao      text primary key,
        aplicada_em timestamptz not null default now(),
        resultado   text not null check (resultado in ('APLICADA','JA_EXISTIA')),
        sha256      text not null);
      comment on table public.schema_migracao is
        'Infraestrutura do aplicador de migrations, não schema de domínio. '
        'Existe para que a cadeia NÃO reaplique o que já foi aplicado — '
        'reaplicar pode ressuscitar coluna que uma migration posterior '
        'aposentou, e foi por isso que ele nasceu.';" >/dev/null

    for f in $(ls "$RAIZ"/supabase/migrations/*.sql | grep -v '/008_' | sort); do
      num=$(basename "$f" | cut -c1-3)
      sha=$(sha256sum "$f" | cut -d' ' -f1)
      ja=$(psql "$URL" -tAc "select 1 from public.schema_migracao where versao='$num'")
      if [ -n "$ja" ]; then
        echo "MIGRATION_$num=SKIP (ja no livro-razao)"
        continue
      fi
      if psql "$URL" -v ON_ERROR_STOP=1 -q -f "$f" >/tmp/cc.out 2>/tmp/cc.err; then
        psql "$URL" -q -c "insert into public.schema_migracao (versao, resultado, sha256)
          values ('$num','APLICADA','$sha') on conflict (versao) do nothing" >/dev/null
        echo "MIGRATION_$num=PASS"
      elif grep -qiE "already exists|ja existe|já existe" /tmp/cc.err; then
        # O banco respondeu que os objetos já estão lá. Isso é RESPOSTA, e
        # é ela que entra no livro — não uma suposição sobre o histórico.
        psql "$URL" -q -c "insert into public.schema_migracao (versao, resultado, sha256)
          values ('$num','JA_EXISTIA','$sha') on conflict (versao) do nothing" >/dev/null
        echo "MIGRATION_$num=SKIP (objetos ja existem; anotado no livro-razao)"
      else
        echo "MIGRATION_$num=FAIL"; sanitiza < /tmp/cc.err | head -8; exit 1
      fi
    done
    ;;
  importacoes)
    # A ordem É a lei. Regulatório primeiro.
    for f in supabase/importacoes/ES-REGULATORIO-ROPF-2026-08-29.sql \
             supabase/importacoes/ADAMA-ES-CATALOGO-2026-08-30.sql; do
      nome=$(basename "$f")
      if psql "$URL" -v ON_ERROR_STOP=1 -q -f "$RAIZ/$f" >/tmp/cc.out 2>/tmp/cc.err; then
        echo "IMPORT_${nome%%.sql}=PASS"
      else
        echo "IMPORT_${nome%%.sql}=FAIL"; sanitiza < /tmp/cc.err | head -8; exit 1
      fi
    done
    ;;
  *) echo "etapa desconhecida: $ETAPA"; exit 2 ;;
esac
