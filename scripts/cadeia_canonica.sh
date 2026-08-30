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
    for f in $(ls "$RAIZ"/supabase/migrations/*.sql | grep -v '/008_' | sort); do
      num=$(basename "$f" | cut -c1-3)
      if psql "$URL" -v ON_ERROR_STOP=1 -q -f "$f" >/tmp/cc.out 2>/tmp/cc.err; then
        echo "MIGRATION_$num=PASS"
      elif grep -qiE "already exists|ja existe|já existe" /tmp/cc.err; then
        # Reaplicar uma migration já aplicada sai como SKIP: objeto que já
        # existe é RESPOSTA, não defeito. Qualquer outro erro para tudo.
        echo "MIGRATION_$num=SKIP (objetos ja existem)"
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
