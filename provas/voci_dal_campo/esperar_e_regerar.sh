#!/usr/bin/env bash
# VOCI-DAL-CAMPO — espera a vez (LOCK-PESADO, respeitando a LOCK-PRIORIDADE), confere a memoria (>= 5 GB livres),
# regera o System Map pela cadeia e SOLTA a LOCK no fim, aconteca o que acontecer.
L=C:/Users/London1/auditoria-madrugada/LOCK-PESADO.txt
P=C:/Users/London1/auditoria-madrugada/LOCK-PRIORIDADE.txt
MEM=C:/Users/London1/AppData/Local/Temp/mem.ps1
n=0
livre() { powershell -File "$MEM" 2>/dev/null | head -1 | sed 's/[^0-9.,]*\([0-9][0-9]*[.,][0-9]\).*/\1/' | tr ',' '.'; }
while true; do
  if [ ! -e "$P" ]; then
    g=$(livre)
    if awk -v g="$g" 'BEGIN{exit !(g>=5.0)}'; then
      if ( set -C; echo "VOCI-DAL-CAMPO (nuvem-voci-campo-v1) $(date '+%F %T') — correr_a_cadeia REGERAR do mapa" > "$L" ) 2>/dev/null; then
        break
      fi
    fi
  fi
  sleep 10
  n=$((n+1))
  if [ $n -ge 1080 ]; then echo "DESISTI 3 h $(date +%T)"; cat "$L" "$P" 2>/dev/null; exit 3; fi
done
trap 'rm -f "$L"; echo "LOCK solta $(date +%T)"' EXIT
echo "LOCK pega $(date +%T) · RAM livre $(livre) GB"
cd C:/nuvem/nuvem-voci-campo-v1 || exit 4
PYTHONIOENCODING=utf-8 PYTHONUTF8=1 timeout 2400 py system-map/scripts/correr_a_cadeia.py REGERAR > provas/voci_dal_campo/_regerar.log 2>&1
echo "REGERAR RC=$?"
tail -12 provas/voci_dal_campo/_regerar.log
git status --short | head -40
