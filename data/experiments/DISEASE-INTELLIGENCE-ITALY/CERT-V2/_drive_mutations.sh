#!/usr/bin/env bash
cd "$(dirname "$0")"
mkdir -p MUTANTS
ALL="M01 M02 M03 M04 M05 M06 M07 M08 M09 M10 M11 M12 M13 M14 M15 M16 M17 M18 M19 M20 M21 M22 M23 M24 M25 M26"
i=0
for m in $ALL; do
  py p3_mutation.py "$m" >"MUTANTS/$m.log" 2>&1 &
  i=$((i+1))
  if [ $((i % 6)) -eq 0 ]; then wait; echo "--- batch done after $m ---"; fi
done
wait
echo "ALL MUTATIONS DONE"
