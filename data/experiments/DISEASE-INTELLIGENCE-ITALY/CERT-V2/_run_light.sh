#!/usr/bin/env bash
cd "$(dirname "$0")"
for s in p9_geography p8_crop_semantics p7_code_vs_value p13_independent_reproduction p4_date_and_floor; do
  echo "=============== $s ==============="
  py "$s.py" 2>&1 | grep -v "platform independent"
  echo "--- exit=$? ---"
done
echo "LIGHT SCRIPTS DONE"
