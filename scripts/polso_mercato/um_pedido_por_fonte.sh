#!/usr/bin/env bash
# POLSO-FONTES · 1 pedido por fonte, SO para quem o DONO da rede (a coordenacao) corre, com a VPN IT e o
# portao de egresso em PASS. Nada aqui corre sozinho, nem em teste.
#
#   bash scripts/polso_mercato/um_pedido_por_fonte.sh            # confere os livros e pede aos livres
#   bash scripts/polso_mercato/um_pedido_por_fonte.sh --so-conferir   # so a conferencia, sem rede
#
# 1. CONFERE nos livros vivos (robo + ponte) se cada dominio esta livre ha 24 h
#    (scripts/polso_mercato/dominio_livre_24h.py, so leitura). Dominio OCUPADO nao e pedido: sai a hora em
#    que fica livre.
# 2. PEDE uma vez a cada dominio livre (curl, so GET, sem login, User-Agent de navegador, 60 s), guarda os bytes
#    e o sha256. 5 dominios, 1 pedido cada (teto D38: 5/dominio/rodada). Nenhum na lista proibida
#    (CNR, Coldiretti, ANGA, Unaprol).
# 3. LE sem rede cada ficheiro com o leitor de preco (leis/preco_de_mercado.py).
set -u
# `pwd -W` (Git Bash) da C:/...; o Python do Windows nao le /c/... (medido: «C:\c\nuvem\...»)
RAIZ="$(cd "$(dirname "$0")/../.." && (pwd -W 2>/dev/null || pwd))"
VIVO="${VIVO:-C:/Users/London1/orca/workspaces/eame-sintonia/source-curator-service-v1}"
PONTE="${PONTE:-C:/Users/London1/orca/workspaces/eame-sintonia/ponte-viva}"
OUT="${OUT:-C:/Users/London1/auditoria-madrugada/polso-fontes/$(date +%Y%m%d-%H%M%S)}"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36"
mkdir -p "$OUT"
export PYTHONIOENCODING=utf-8

# dominio | ficheiro | URL (os tres ultimos NAO VERIFICADOS: o repo nao os conhece)
FONTES="ismeamercati.it|ismea-853.html|https://www.ismeamercati.it/flex/cm/pages/ServeBLOB.php/L/IT/IDPagina/853
bmti.it|bmti-cereali.json|https://www.bmti.it/wp-json/wp/v2/posts?categories=30&per_page=1
granariamilano.it|granaria-listino.html|https://www.granariamilano.it/listino/
italmercati.it|italmercati.html|https://www.italmercati.it/
clal.it|clal.html|https://www.clal.it/"

echo "== 1 · conferir os livros vivos (ultimas 24 h) -> $OUT"
# FALHA FECHADA: sem a conferencia do robo, nenhum pedido (medido: com o caminho errado a conferencia morria e
# o resto seguia — e um livro ausente contava como livre).
rm -f "$OUT/livre-robo.json" "$OUT/livre-ponte.json"     # nunca decidir por uma conferencia velha
py "$RAIZ/scripts/polso_mercato/dominio_livre_24h.py" "$VIVO" "$OUT/livre-robo.json" || true
[ -s "$OUT/livre-robo.json" ] || { echo "PARADO: a conferencia dos livros do robo falhou — nenhum pedido feito"; exit 2; }
if [ -d "$PONTE" ]; then
  py "$RAIZ/scripts/polso_mercato/dominio_livre_24h.py" "$PONTE" "$OUT/livre-ponte.json" || true
  [ -s "$OUT/livre-ponte.json" ] || { echo "PARADO: a conferencia dos livros da ponte falhou — nenhum pedido feito"; exit 2; }
fi

livre() {  # o dominio tem de estar LIVRE nos dois livros
  py - "$1" "$OUT/livre-robo.json" "$OUT/livre-ponte.json" <<'PY'
import json, os, sys
d = sys.argv[1]
for f in sys.argv[2:]:
    if os.path.exists(f):
        r = json.load(open(f, encoding="utf-8"))["DOMINIOS"][d]
    elif f.endswith("livre-robo.json"):
        print("SEM CONFERENCIA DO ROBO"); sys.exit(1)
    else:
        continue
    if r["VEREDITO"] != "LIVRE_NOS_LIVROS":
        print("OCUPADO ate %s (%s)" % (r.get("LIVRE_A_PARTIR_DE"), os.path.basename(f))); sys.exit(1)
print("LIVRE")
PY
}

[ "${1:-}" = "--so-conferir" ] && { echo "so conferir: nenhum pedido feito"; exit 0; }

echo "== 2 · um pedido por dominio livre"
echo "$FONTES" | while IFS='|' read -r dom fich url; do
  estado="$(livre "$dom" 2>&1)"
  if [ "$estado" != "LIVRE" ]; then echo "SALTA $dom · $estado"; continue; fi
  curl -sS -L -A "$UA" --max-time 60 -o "$OUT/$fich" \
       -w "$dom HTTP=%{http_code} BYTES=%{size_download} URL=%{url_effective}\n" "$url" | tee -a "$OUT/PEDIDOS.txt"
  [ -f "$OUT/$fich" ] && sha256sum "$OUT/$fich" | tee -a "$OUT/SHA256.txt"
done

echo "== 3 · o leitor de preco, sem rede"
for f in "$OUT"/*.html "$OUT"/*.json; do
  case "$f" in *livre-*.json|*.precos.json) continue;; esac
  [ -f "$f" ] || continue
  echo "-- $(basename "$f")"
  py "$RAIZ/leis/preco_de_mercado.py" "$f" > "$f.precos.json" && py - "$f.precos.json" <<'PY'
import json, sys
r = json.load(open(sys.argv[1], encoding="utf-8"))
o = r["OBSERVACOES"]
print("  %d observacoes · %d com praca+periodo+unidade · %d recusados" % (
    len(o), sum(all(x[k] != "NAO SEI" for k in ("PRACA", "PERIODO", "UNIDADE")) for x in o), len(r["RECUSADOS"])))
for x in o[:5]:
    print("   ", x["COMMODITY"], "|", x["PRACA"], "|", x["PERIODO"], "|", x["PRECO_TEXTO"], "|", x["ESTAGIO"])
PY
done
echo "== fim · bytes, sha256 e leituras em $OUT"
