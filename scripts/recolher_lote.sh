#!/usr/bin/env bash
# Move o pacote que o navegador acabou de gravar no Downloads para dentro do repo.
# O Chrome grava blob grande com nome temporario (<uuid>.tmp); o nome do lote vem por
# argumento porque o navegador nao consegue escrever direto no projeto.
set -euo pipefail
LOTE="$1"
DEST="data/raw/ES/adama-website/lotes"
mkdir -p "$DEST"
# O Chrome as vezes finaliza o download com o nome pedido (LOTE-XX.json) e as vezes
# deixa o temporario (<uuid>.tmp). Aceitar os dois evita perder pacote ja baixado.
ARQ="/c/Users/London1/Downloads/LOTE-$LOTE.json"
if [ ! -f "$ARQ" ]; then
  ARQ=$(ls -t /c/Users/London1/Downloads/*.tmp 2>/dev/null | head -1 || true)
fi
if [ -z "${ARQ:-}" ] || [ ! -f "$ARQ" ]; then echo "SEM_ARQUIVO lote=$LOTE"; exit 1; fi
mv "$ARQ" "$DEST/LOTE-$LOTE.json"
echo "OK lote=$LOTE bytes=$(stat -c%s "$DEST/LOTE-$LOTE.json")"
