#!/bin/bash
# RT4-02  Environment sweep, run in a FRESH CLONE pinned at 8efec08 (the commit whose
# artifact publishes sha256 61ac20d6...). Each condition is ONE fresh process. Batches of 7
# run concurrently, which also exercises concurrent __pycache__ writes and concurrent reads.
cd "$(dirname "$0")" || exit 1
mkdir -p .sweep && rm -f .sweep/*
i=0
run(){ label="$1"; shift; ( env "$@" py rt4_01_repro.py 2>/dev/null | grep '^{' > ".sweep/$label.json" ) &
       i=$((i+1)); if [ $((i % 7)) -eq 0 ]; then wait; fi; }
n=0
for s in 0 1 2 3 7 42 4294967295; do n=$((n+1)); run "A_hashseed_$s" PYTHONHASHSEED=$s; done
for k in 1 2 3; do run "A_hashseed_random_$k" PYTHONHASHSEED=random; done
run "B_utf8mode_on"    PYTHONUTF8=1
run "B_utf8mode_off"   PYTHONUTF8=0
run "B_ioenc_cp1252"   PYTHONIOENCODING=cp1252
run "C_locale_C"       LANG=C LC_ALL=C LC_NUMERIC=C
run "C_locale_tr_TR"   LANG=tr_TR.UTF-8 LC_ALL=tr_TR.UTF-8
run "C_locale_de_comma" LANG=de_DE.UTF-8 LC_ALL=de_DE.UTF-8 LC_NUMERIC=de_DE.UTF-8
run "D_tz_kiritimati"  TZ=Pacific/Kiritimati
run "D_tz_gmt_minus12" TZ=Etc/GMT+12
run "E_no_bytecode"    PYTHONDONTWRITEBYTECODE=1
run "E_optimize_2"     PYTHONOPTIMIZE=2
run "E_intmaxstr"      PYTHONINTMAXSTRDIGITS=640
run "F_cwd_root"       RT4_DUMMY=1
wait
echo "== condition -> CORE hash | EXT report | EXT rendered | adama =="
for f in .sweep/*.json; do
  b=$(basename "$f" .json)
  h=$(py -c "import json,sys;d=json.load(open(sys.argv[1]));print(d['CORE_HASH_the_one_the_tool_publishes'][:24],d['EXT_REPORT_HASH_with_adama_and_provenance'][:12],d['EXT_RENDERED_TEXT_HASH'][:12],d['ADAMA_RELEVANCE'])" "$f" 2>/dev/null)
  printf "  %-22s %s\n" "$b" "${h:-EMPTY_OR_CRASHED}"
done
echo "== DISTINCT CORE hashes over all conditions =="
for f in .sweep/*.json; do py -c "import json,sys;print(json.load(open(sys.argv[1]))['CORE_HASH_the_one_the_tool_publishes'])" "$f" 2>/dev/null; done | sort | uniq -c
echo "== DISTINCT EXT RENDERED-TEXT hashes =="
for f in .sweep/*.json; do py -c "import json,sys;print(json.load(open(sys.argv[1]))['EXT_RENDERED_TEXT_HASH'])" "$f" 2>/dev/null; done | sort | uniq -c
