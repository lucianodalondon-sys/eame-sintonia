#!/usr/bin/env bash
# COMENTARIOS-V1 — espera a vez (LOCK-PESADO, respeitando a LOCK-PRIORIDADE e >= 5 GB livres), corre a
# bateria por nome na BASE (2ef6fef8, pasta C:/nuvem/_com_base) e no RAMO, e solta a vez no fim.
L=C:/Users/London1/auditoria-madrugada/LOCK-PESADO.txt
P=C:/Users/London1/auditoria-madrugada/LOCK-PRIORIDADE.txt
MEM=C:/Users/London1/AppData/Local/Temp/mem.ps1
livre() { powershell -File "$MEM" 2>/dev/null | head -1 | sed 's/[^0-9.,]*\([0-9][0-9]*[.,][0-9]\).*/\1/' | tr ',' '.'; }
n=0
while true; do
  if [ ! -e "$P" ] && awk -v g="$(livre)" 'BEGIN{exit !(g>=5.0)}'; then
    if ( set -C; echo "COMENTARIOS-V1 (comentarios-v1) $(date '+%F %T') — bateria por nome base/ramo (48 modulos, rede fechada)" > "$L" ) 2>/dev/null; then
      break
    fi
  fi
  sleep 10; n=$((n+1))
  if [ $n -ge 1080 ]; then echo "DESISTI 3 h $(date +%T)"; head -1 "$L" "$P" 2>/dev/null; exit 3; fi
done
trap 'rm -f "$L"; echo "LOCK solta $(date +%T)"' EXIT
echo "LOCK pega $(date +%T)"
R=C:/nuvem/comentarios-v1
cp "$R/provas/comentarios_v1/testes_por_nome.py" C:/nuvem/_com_base/_tpn.py
(cd C:/nuvem/_com_base && timeout 2400 py _tpn.py . "$R/provas/comentarios_v1/antes.json" > /dev/null 2>&1); echo "BASE RC=$?"
(cd "$R" && timeout 2400 py provas/comentarios_v1/testes_por_nome.py . provas/comentarios_v1/depois.json > /dev/null 2>&1); echo "RAMO RC=$?"
rm -f C:/nuvem/_com_base/_tpn.py
cd "$R" && py - <<'EOF'
import json
a = json.load(open('provas/comentarios_v1/antes.json', encoding='utf-8'))
b = json.load(open('provas/comentarios_v1/depois.json', encoding='utf-8'))
N = H = 0
for k in b:
    fa, fb = set(a.get(k, {}).get('FALHAS', [])), set(b[k].get('FALHAS', []))
    N += len(fb - fa); H += len(fb & fa)
    if fb - fa or fa - fb:
        print(k, 'NOVAS', sorted(fb - fa), 'SUMIRAM', sorted(fa - fb))
print('novas', N, 'herdadas', H, 'corridos antes', sum(v.get('CORRIDOS') or 0 for v in a.values()),
      'depois', sum(v.get('CORRIDOS') or 0 for v in b.values()))
EOF
