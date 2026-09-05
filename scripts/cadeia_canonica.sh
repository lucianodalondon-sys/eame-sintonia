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

    # ── TRAVA DE NUMERO REPETIDO ──────────────────────────────────────
    # A chave do livro-razao sao os TRES PRIMEIROS CARACTERES do nome. Dois
    # arquivos com o mesmo numero viram UM: o segundo e pulado com SKIP,
    # que no log parece normal. Aconteceu em 02/09/2026 -- uma migration
    # nova nasceu 017 ao lado de uma 017 de 30/08, e a antiga teria sumido
    # em silencio, com a 018 dependendo dela.
    #
    #     DUAS MIGRATIONS COM O MESMO NUMERO NAO SAO DUAS. SAO UMA.
    #
    # Falhar aqui e barato. Descobrir em producao que uma migration nunca
    # rodou, nao.
    dup=$(for f in "$RAIZ"/supabase/migrations/*.sql; do
            basename "$f" | cut -c1-3; done | sort | uniq -d)
    if [ -n "$dup" ]; then
      echo "MIGRATION_NUMERO_REPETIDO=$(echo $dup | tr '
' ' ')"
      for n in $dup; do
        echo "  os arquivos com o numero $n:"
        ls "$RAIZ"/supabase/migrations/${n}_*.sql | sed 's#.*/#    #'
      done
      echo "  renumere um deles. O aplicador aplicaria so o primeiro."
      exit 1
    fi

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
    #
    # A IT-LASTMILE entra POR ULTIMO, e nao e preferencia: ela referencia
    # `substancia_ativa` (migration 019) e cria as proprias `fonte_externa`
    # antes de cada fato. Roda-la antes do catalogo espanhol nao quebraria --
    # mas a regra da casa e uma ordem so, escrita num lugar so, e quem chega
    # depois entra no fim.
    for f in supabase/importacoes/ES-REGULATORIO-ROPF-2026-08-29.sql \
             supabase/importacoes/ADAMA-ES-CATALOGO-2026-08-30.sql \
             supabase/importacoes/IT-LASTMILE-2026-09-02.sql; do
      # ── CONFERENCIA DE SINTAXE, ANTES DE TOCAR O BANCO ──────────────
      # O arquivo da last-mile tem 2,8 MB e 3.798 inserts gerados por
      # script. Uma apostrofe nao escapada num texto italiano («dell'olivo»)
      # transforma o resto do arquivo em lixo, e o erro do psql aponta para
      # uma linha centenas de statements adiante. Conferir custa 2 segundos
      # e nao precisa de banco.
      if command -v python3 >/dev/null 2>&1; then
        if ! python3 "$RAIZ/scripts/sql_conferir.py" "$RAIZ/$f"; then
          echo "IMPORT_$(basename "${f%%.sql}")=FAIL_NA_CONFERENCIA"; exit 1
        fi
      fi
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
