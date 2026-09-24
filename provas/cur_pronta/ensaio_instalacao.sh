#!/bin/bash
# Ensaio da instalacao M5G numa COPIA FIEL do vivo (bot + ponte). So LE o vivo.
# uso: ensaio_instalacao.sh <FINAL_sha> <saida_dir>
set -u
ORCA=${ORCA:?defina ORCA = pasta das worktrees (a que contem source-curator-service-v1)}; SINTONIA_LIBS=${SINTONIA_LIBS:?defina SINTONIA_LIBS}
FINAL=$1; OUT=$2; mkdir -p $OUT
REPO=$ORCA/unificacao-v1-f
VIVA=$ORCA/source-curator-service-v1
PONTE=$ORCA/ponte-viva
EB=C:/ens2-bot; EP=C:/ens2-ponte
log(){ echo "$*" | tee -a $OUT/ensaio.log; }
: > $OUT/ensaio.log
shas(){ (cd $1 && for f in $(git status --short | grep "^ M" | awk '{print $2}'); do sha256sum $f; done) ; }

copiar_sujos(){ # $1 vivo  $2 copia  -> copia os ficheiros sujos do vivo, confere JSON
  local n=0
  for f in $(git -C $1 status --short | grep "^ M" | awk '{print $2}'); do
    for t in 1 2 3; do
      cp "$1/$f" "$2/$f"
      case "$f" in *.json) py -c "import json,sys;json.load(open(sys.argv[1],encoding='utf-8'))" "$2/$f" 2>/dev/null && break;; *) break;; esac
      log "  $f lido a meio de uma escrita, tentativa $t"; sleep 5
    done
    n=$((n+1))
  done
  log "  $n ficheiros sujos copiados de $1"
}

for d in $EB $EP; do git -C $REPO worktree remove --force $d 2>/dev/null; done
HB=$(git -C $VIVA rev-parse HEAD); HP=$(git -C $PONTE rev-parse HEAD)
log "VIVO bot   $(git -C $VIVA branch --show-current) @ ${HB:0:8}  sujos=$(git -C $VIVA status --short | wc -l)"
log "VIVO ponte $(git -C $PONTE branch --show-current) @ ${HP:0:8}  sujos=$(git -C $PONTE status --short | wc -l)"
log "FINAL      ${FINAL:0:8}"

########## BOT ##########
git -C $REPO worktree add -q -b ens-bot-$$ $EB $HB
copiar_sujos $VIVA $EB
shas $EB > $OUT/bot-antes.sha
log "BOT 1. merge --no-ff $FINAL (com os livros sujos no sitio)"
git -C $EB merge --no-ff --no-commit $FINAL > $OUT/bot-merge.txt 2>&1; rc=$?
CONF=$(git -C $EB diff --name-only --diff-filter=U)
log "   rc=$rc  conflitos=$(echo -n "$CONF" | grep -c .)"
echo "$CONF" | sed 's/^/     /' | tee -a $OUT/ensaio.log
FORA=$(echo "$CONF" | grep -v '\.generated\.json$' | grep -v '^docs/operacao/CENSO' | grep -c .)
log "   conflitos fora do mapa gerado = $FORA"
for f in $CONF; do git -C $EB checkout -q --theirs -- "$f"; git -C $EB add "$f"; done
git -C $EB commit -q -m "ENSAIO: instala unificacao-v1 ${FINAL:0:8} (livros = producao)"
shas $EB > $OUT/bot-depois.sha
diff -q $OUT/bot-antes.sha $OUT/bot-depois.sha >/dev/null && log "BOT 2. livros sujos: IGUAIS byte a byte ($(wc -l < $OUT/bot-antes.sha))" || log "BOT 2. livros sujos: MUDARAM  <- ABORTAR"
ND=$(git -C $EB diff --name-only $FINAL HEAD | wc -l)
log "BOT 3. arvore commitada vs FINAL: $ND ficheiros diferentes"
git -C $EB diff --name-only $FINAL HEAD | sed 's/^/     /' | tee -a $OUT/ensaio.log
log "BOT 4. testes na copia instalada:"
(cd $EB/curadoria && PYTHONPATH="$SINTONIA_LIBS" py -m unittest test_collection_gate test_zz_guarda_isolamento test_avancar_fontes test_onda_em_curso test_reparar_contrato > $OUT/bot-testes.txt 2>&1; grep '^FAIL:\|^ERROR:\|^Ran\|^OK\|^FAILED' $OUT/bot-testes.txt | sed 's/^/     /' | tee -a $OUT/ensaio.log)
(cd $EB && PYTHONPATH="$SINTONIA_LIBS" py -c "
import sys; sys.path.insert(0,'curadoria')
import collection_gate as CG
inv=CG.inventario(); e=[l for l in inv if l['COLLECTION_ELIGIBLE']]
print('     portao com os livros vivos: elegiveis =', len(e), 'de', len(inv))" 2>&1 | grep -v platf | tee -a $OUT/ensaio.log)
(cd $EB && git status --short | grep -v -f <(sed 's/^[0-9a-f]* [ *]//' $OUT/bot-antes.sha) | sed 's/^/     residuo: /' | tee -a $OUT/ensaio.log)
log "BOT 5. DESFAZER: git reset --keep ${HB:0:8}"
git -C $EB reset -q --keep $HB; rc=$?
shas $EB > $OUT/bot-desfeito.sha
log "   rc=$rc  HEAD=$(git -C $EB rev-parse --short HEAD)  arvore vs vivo: $(git -C $EB diff --name-only $HB | grep -v -f <(sed 's/^[0-9a-f]* [ *]//' $OUT/bot-antes.sha) | wc -l) codigo diferente"
diff -q $OUT/bot-antes.sha $OUT/bot-desfeito.sha >/dev/null && log "   livros sujos depois do desfazer: IGUAIS" || log "   livros sujos depois do desfazer: MUDARAM <- FALHA DO ROLLBACK"

########## PONTE ##########
git -C $REPO worktree add -q -b ens-ponte-$$ $EP $HP
copiar_sujos $PONTE $EP
shas $EP > $OUT/ponte-antes.sha
git -C $REPO merge-base --is-ancestor $HP $FINAL && log "PONTE 1. ${HP:0:8} esta na linha: avanco rapido (ff-only)" || log "PONTE 1. ${HP:0:8} NAO esta na linha <- ABORTAR"
git -C $EP merge -q --ff-only $FINAL > $OUT/ponte-merge.txt 2>&1; rc=$?
log "   rc=$rc HEAD=$(git -C $EP rev-parse --short HEAD)"
shas $EP > $OUT/ponte-depois.sha
diff -q $OUT/ponte-antes.sha $OUT/ponte-depois.sha >/dev/null && log "PONTE 2. livros sujos: IGUAIS ($(wc -l < $OUT/ponte-antes.sha))" || log "PONTE 2. livros sujos: MUDARAM <- ABORTAR"
grep -q -- '"--lane"' $EP/curadoria/ponte_automatica.py && log "PONTE 3. --lane presente (LANE=SIM)" || log "PONTE 3. LANE=NAO"
git -C $EP reset -q --keep $HP; rc=$?
shas $EP > $OUT/ponte-desfeito.sha
diff -q $OUT/ponte-antes.sha $OUT/ponte-desfeito.sha >/dev/null && log "PONTE 4. DESFAZER rc=$rc HEAD=$(git -C $EP rev-parse --short HEAD) livros IGUAIS" || log "PONTE 4. DESFAZER: livros MUDARAM <- FALHA"

########## VIVO nao foi tocado ##########
log "VIVO depois: bot @ $(git -C $VIVA rev-parse --short HEAD), ponte @ $(git -C $PONTE rev-parse --short HEAD)"
for d in $EB $EP; do git -C $REPO worktree remove --force $d; done
git -C $REPO branch -q -D ens-bot-$$ ens-ponte-$$
log "copias apagadas"
