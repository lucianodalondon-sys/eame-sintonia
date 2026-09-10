#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════
# A TRAVA DO ESCRITOR ANTIGO — só leitura, e é essa a única coisa que faz
#
# A migration 026 dá identidade à observação: `identity_state` passa a ser
# NOT NULL e SEM DEFAULT, e os dois estados forward exigem uma fonte real.
# Quem escreve `raw_asset` no formato anterior deixa de conseguir escrever.
#
# ISSO JÁ É SEGURO — o banco recusa a linha. O que NÃO é seguro é descobri-lo
# a meio de uma execução, com metade do Storage já escrito e um erro de
# constraint como única explicação:
#
#     FALHAR TARDE COM UMA MENSAGEM DE SCHEMA
#     NÃO É A MESMA COISA QUE RECUSAR CEDO COM O MOTIVO.
#
# Esta trava pergunta uma coisa só: **este banco já conhece a 026?** Se
# conhecer, o caminho antigo para. Não conserta nada, não escreve nada, e
# sobretudo NÃO INVENTA IDENTIDADE para caber — fabricar um `SOURCE_ID` que a
# casa nunca registou seria pior do que não escrever.
#
#   uso:  SUPABASE_DB_URL=... bash guarda/trava_do_escritor_antigo.sh <quem>
#
#   saída 0   o banco é anterior à 026 — o caminho antigo pode correr
#   saída 1   o banco já tem a 026 — o caminho antigo NÃO corre
#
# QUANDO ESTA TRAVA SAI: quando o caminho em causa aprender a declarar
# identidade comprovada, ou quando alguém provar que ele não precisa de
# escrever `raw_asset`. Sair antes disso é reabrir o buraco com outro nome.
# ═══════════════════════════════════════════════════════════════════════
set -uo pipefail

QUEM="${1:-caminho nao identificado}"
URL="${SUPABASE_DB_URL:?falta SUPABASE_DB_URL}"

# Nunca ecoar a URL: um erro do psql pode traze-la dentro da mensagem.
sanitiza() { sed -E 's#postgres(ql)?://[^ ]*#<URL_OMITIDA>#g'; }

tem=$(psql "$URL" -X -q -A -t -v ON_ERROR_STOP=1 -c \
      "select count(*) from information_schema.columns
        where table_schema='public' and table_name='raw_asset'
          and column_name='identity_state'" 2>/tmp/trava.err)
if [ -z "$tem" ]; then
  echo "ESCRITOR_ANTIGO=NAO_SEI — a leitura do schema falhou"
  sanitiza < /tmp/trava.err | head -3
  exit 1
fi

if [ "$tem" = "0" ]; then
  echo "ESCRITOR_ANTIGO=PERMITIDO ($QUEM) — este banco ainda nao conhece a 026"
  exit 0
fi

cat <<FIM
ESCRITOR_ANTIGO=RECUSADO ($QUEM)

  Este banco ja tem a migration 026: raw_asset.identity_state existe, e uma
  observacao nova tem de declarar de QUEM ela e. Este caminho escreve no
  formato anterior — sem source_id, sem document_key, sem estado.

  NAO se inventa identidade para o desbloquear:
    · um SOURCE_ID fabricado seria uma fonte que a casa nunca registou;
    · um DOCUMENT_ID fabricado seria uma identidade que a fonte nao deu;
    · o sha256 nao serve de DOCUMENT_KEY — bytes iguais nao provam
      documento igual, e a ADAMA publicou o mesmo PDF em dois sitios;
    · e LEGACY_PRE_IDEMPOTENCY e para quem ja la estava no corte, nunca
      para uma linha escrita hoje.

  Para este caminho voltar a escrever, ele precisa de um contrato que prove
  a identidade do que traz. Ate la, para aqui — de proposito.
FIM
exit 1
