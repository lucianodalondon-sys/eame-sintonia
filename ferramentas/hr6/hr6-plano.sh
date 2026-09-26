set -e
R=C:/Users/London1/orca/workspaces/eame-sintonia/reparo-fontes-v1
VIVO=C:/Users/London1/orca/workspaces/eame-sintonia/source-curator-service-v1
W=C:/wt-hr6-plano
git -C $R worktree remove --force $W 2>/dev/null || true
git -C $R worktree add -q --detach $W HEAD
cd $W
# ANTES: os livros sujos do vivo, tal como estao
while read f; do cp "$VIVO/$f" "$W/$f"; done < /c/hr6/SUJOS.txt
HTTPS_PROXY=http://127.0.0.1:9 HTTP_PROXY=http://127.0.0.1:9 PYTHONUTF8=1 py -B scripts/micro_coleta/micro_coleta.py plano > /c/hr6/prova/PLANO-ANTES.txt 2>&1 || true
# DEPOIS: o estado da copia (livros apos o worker + onboarding + canario novo)
for f in $(cat /c/hr6/SUJOS.txt) regras/italy_contracts_onboarded.json curadoria/ROTAS-ELEGIVEIS-V1.json curadoria/canario.py; do cp "/c/hr6/$f" "$W/$f"; done
HTTPS_PROXY=http://127.0.0.1:9 HTTP_PROXY=http://127.0.0.1:9 PYTHONUTF8=1 py -B scripts/micro_coleta/micro_coleta.py plano > /c/hr6/prova/PLANO-DEPOIS.txt 2>&1 || true
cd /c
git -C $R worktree remove --force $W
grep -a -i "PRONTAS\|BLOQUEADAS\|IT-T7-17[04]\|IT-T5-049" /c/hr6/prova/PLANO-ANTES.txt | head -8
echo ---
grep -a -i "PRONTAS\|BLOQUEADAS\|IT-T7-17[04]\|IT-T5-049" /c/hr6/prova/PLANO-DEPOIS.txt | head -8
