#!/bin/bash
# RT4-02  Environment sweep. Each condition is ONE fresh process; all launched CONCURRENTLY,
# which also exercises parallel __pycache__ writes and concurrent reads of the same inputs.
# NOTE: the script path must be a WINDOWS path - the interpreter is native Windows python.
cd "$(dirname "$0")" || exit 1
S="rt4_01_repro.py"
mkdir -p .sweep && rm -f .sweep/*
run(){ label="$1"; shift; ( env "$@" py "$S" 2>/dev/null | grep '^{' > ".sweep/$label.json" ) & }
for s in 0 1 2 3 7 42 4294967295 random random random; do run "HASHSEED_$s$RANDOM" PYTHONHASHSEED=$s; done
run "UTF8MODE_1"      PYTHONUTF8=1
run "UTF8MODE_0"      PYTHONUTF8=0
run "LC_ALL_C"        LANG=C LC_ALL=C
run "LC_ALL_tr_TR"    LANG=tr_TR.UTF-8 LC_ALL=tr_TR.UTF-8
run "LC_ALL_de_latin1" LANG=de_DE.ISO-8859-1 LC_ALL=de_DE.ISO-8859-1
run "IOENC_cp1252"    PYTHONIOENCODING=cp1252
run "TZ_Kiritimati"   TZ=Pacific/Kiritimati
run "TZ_GMTminus12"   TZ=Etc/GMT+12
run "NO_BYTECODE"     PYTHONDONTWRITEBYTECODE=1
run "OPTIMIZE_2"      PYTHONOPTIMIZE=2
run "INTMAXSTR"       PYTHONINTMAXSTRDIGITS=640
wait
echo "== per-condition CORE hash (the one the tool publishes) =="
for f in .sweep/*.json; do
  b=$(basename "$f" .json)
  h=$(py -c "import json,sys;d=json.load(open(sys.argv[1]));print(d['CORE_HASH_the_one_the_tool_publishes'],d['EXT_REPORT_HASH_with_adama_and_provenance'][:16],d['EXT_RENDERED_TEXT_HASH'][:16],d['ADAMA_RELEVANCE'])" "$f" 2>/dev/null)
  printf "  %-22s %s\n" "$b" "${h:-EMPTY_OR_CRASHED}"
done
echo "== distinct CORE hashes =="
for f in .sweep/*.json; do py -c "import json,sys;print(json.load(open(sys.argv[1]))['CORE_HASH_the_one_the_tool_publishes'])" "$f" 2>/dev/null; done | sort -u
