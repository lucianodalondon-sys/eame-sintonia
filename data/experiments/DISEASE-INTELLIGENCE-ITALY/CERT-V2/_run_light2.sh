#!/usr/bin/env bash
cd "$(dirname "$0")"
for s in p12_negative_controls p9_geography p7_code_vs_value p6_refresh_and_clock; do
  echo "=============== $s ==============="
  py "$s.py" 2>&1 | grep -v "platform independent"
  echo "--- exit=$? ---"
done
echo "LIGHT2 DONE"
