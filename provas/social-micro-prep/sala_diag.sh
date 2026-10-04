L=C:/Users/London1/auditoria-madrugada/LOCK-PESADO.txt
for i in $(seq 1 360); do
  if [ ! -e $L ] && [ ! -e C:/Users/London1/auditoria-madrugada/LOCK-PRIORIDADE.txt ]; then echo "SOC-MICRO-DIAG (C:/ens-sm) $(date -Iseconds): Salas descartaveis para 2 itens sociais (rede fechada)" > $L; sleep 2; grep -q SOC-MICRO $L && break; fi
  sleep 20
done
grep -q SOC-MICRO $L || { echo SEM_LOCK; exit 3; }
powershell -NoProfile -Command "\$o=Get-CimInstance Win32_OperatingSystem; 'RAM {0:N1} GB livres' -f (\$o.FreePhysicalMemory/1MB)"
export ENS='C:\ens-sm' PYTHONUTF8=1
cd C:/ens-sm
echo "=== ARPA VdA IT-T2-170 com universo T5 (DIAGNOSTICO)"; timeout 1200 py C:/soc2/sala_social.py IT-T2-2026-09-26-013122-d2a62bb995556b9c IT-T2-170 T5 arpa-valle-d-aosta 2>&1 | grep -v "platform indep"
grep -q SOC-MICRO $L && rm $L && echo LIBERTADO
