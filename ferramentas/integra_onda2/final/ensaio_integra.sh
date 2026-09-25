#!/bin/bash
# ENSAIO INTEGRADO (INTEGRA-ONDA2) numa copia fiel do vivo, REDE FECHADA (D41.3). O robo NAO corre.
# uso: bash _ensaio_integra.sh <ramo> <pasta-de-saida>
set -u
RAMO=$1; OUT=$2
VIVO=/c/Users/London1/orca/workspaces/eame-sintonia/source-curator-service-v1
C=/c/integra/copia2; CW="C:/integra/copia2"
export HTTPS_PROXY=http://127.0.0.1:9 HTTP_PROXY=http://127.0.0.1:9 https_proxy=http://127.0.0.1:9 http_proxy=http://127.0.0.1:9 ALL_PROXY=http://127.0.0.1:9 NO_PROXY= PYTHONUTF8=1
rm -rf $C $OUT; mkdir -p $OUT
git -c core.longpaths=true clone -q --no-hardlinks --branch $RAMO "C:/Users/London1/orca/workspaces/eame-sintonia/integra-onda2-v1" "$CW" || exit 1
git -C "$CW" config core.longpaths true
echo "COPIA de $RAMO @ $(git -C "$CW" rev-parse --short HEAD)" | tee $OUT/0-copia.txt
# os 14 livros do vivo (a tabela do coletor e a prova de rotas NAO: vem do ramo, como ficam depois do merge)
LIVROS="candidatas/FONTES-CANDIDATAS.json curadoria/BRIDGE-LEDGER-V1.json curadoria/DISCOVERY-SIGNAL-V1.json curadoria/DISCOVERY-VISITED.json curadoria/LIFECYCLE-EVIDENCE-V1.json curadoria/LIFECYCLE-LEDGER-V1.json curadoria/LIFECYCLE-QUEUE-V1.json curadoria/READY-BATCHES-V1.json curadoria/SOURCE-ID-ALLOCATION-V1.json curadoria/italy_contracts_curator.json data/collection-ledger/italy/observations.ndjson data/collection-ledger/italy/runs.ndjson data/samples/LIVRO-DE-DECISOES.json data/samples/RUN-MANIFEST.json"
echo "FOTO $(date '+%F %T') do vivo @ $(git -C "C:/Users/London1/orca/workspaces/eame-sintonia/source-curator-service-v1" rev-parse --short HEAD)" > $OUT/0-FOTO-DOS-LIVROS.txt
for f in $LIVROS; do cp $VIVO/$f $C/$f; echo "$(sha256sum $VIVO/$f | cut -c1-64) $f" >> $OUT/0-FOTO-DOS-LIVROS.txt; done
for f in regras/italy_contracts_onboarded.json curadoria/ROTAS-ELEGIVEIS-V1.json; do echo "vivo  $(sha256sum $VIVO/$f | cut -c1-64) $f" >> $OUT/0-FOTO-DOS-LIVROS.txt; echo "ramo  $(sha256sum $C/$f | cut -c1-64) $f" >> $OUT/0-FOTO-DOS-LIVROS.txt; done
cd $C
py -c "import urllib.request;urllib.request.urlopen('https://www.cia.it',timeout=5)" >/dev/null 2>&1 && { echo "REDE ABERTA - PARAR"; exit 2; } || echo "rede fechada: confirmada" | tee -a $OUT/0-copia.txt
T0=$(sha256sum regras/italy_contracts_onboarded.json | cut -c1-8); L0=$(sha256sum curadoria/LIFECYCLE-LEDGER-V1.json | cut -c1-8)
echo "== 1 onboarding ANTES" | tee $OUT/1-onboarding.txt
py -B curadoria/onboardar_rotas_provadas.py 2>/dev/null | tail -1 | tee -a $OUT/1-onboarding.txt
py -B - <<'EOF' | tee -a $OUT/1-onboarding.txt
import json, sys
sys.path[:0] = ["medidas", "."]
import canario_rotas_elegiveis as C
v = json.load(open("curadoria/ROTAS-ELEGIVEIS-V1.json", encoding="utf-8"))
e = json.load(open("ferramentas/ponte_onboard/ENSAIO-2-rotas-provadas-3rondas.json", encoding="utf-8"))
v["LINHAS"] = C.juntar(v.get("LINHAS", []), e["LINHAS"]); v["GERADO_EM"] = e.get("GERADO_EM")
json.dump(v, open("curadoria/ROTAS-ELEGIVEIS-V1.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("prova de rotas: juntada a da PONTE (%s), 0 pedidos de rede" % e.get("GERADO_EM"))
EOF
echo "== 1 onboarding COM a prova" | tee -a $OUT/1-onboarding.txt
py -B curadoria/onboardar_rotas_provadas.py --aplicar 2>/dev/null | grep -E "^ENTRA |ENTRA=|escritas" | tee -a $OUT/1-onboarding.txt
echo "tabela $T0 -> $(sha256sum regras/italy_contracts_onboarded.json | cut -c1-8) | LIFECYCLE-LEDGER $L0 -> $(sha256sum curadoria/LIFECYCLE-LEDGER-V1.json | cut -c1-8)" | tee -a $OUT/1-onboarding.txt
echo "== 2 plano do runbook"
py -B scripts/micro_coleta/micro_coleta.py plano > $OUT/2-PLANO-RUNBOOK.json 2>/dev/null
py -c "import json;p=json.load(open(r'$OUT/2-PLANO-RUNBOOK.json'.replace('/c/','C:/'),encoding='utf-8'));print('PRONTAS',p['PRONTAS'],'BLOQUEADAS',p['BLOQUEADAS'])" 2>/dev/null
echo "== 3 congelar (ENSAIO) + commit so na copia"
py -B ferramentas/big_collection/coorte_unica.py --plano="$(echo $OUT | sed 's#^/c/#C:/#')/2-PLANO-RUNBOOK.json" --congelar --instalacao=ENSAIO-$RAMO-$(git rev-parse --short HEAD) --demotion=ENSAIO-sem-B5 --saida=ferramentas/big_collection/COORTE-BIG-COLLECTION-V1.json 2>/dev/null
git add ferramentas/big_collection/COORTE-BIG-COLLECTION-V1.json && git -c user.name=ensaio -c user.email=ensaio@local commit -q -m "ENSAIO so na copia: coorte congelada" && git show HEAD:ferramentas/big_collection/COORTE-BIG-COLLECTION-V1.json > $OUT/3-COORTE-CONGELADA-NA-COPIA.json
echo "== 4 onda2 --so-plano"
py -B ferramentas/big_collection/onda_web.py --so-plano --saida="$(echo $OUT | sed 's#^/c/#C:/#')/onda2" > $OUT/4-ONDA2-SO-PLANO.json 2>/dev/null
echo "== 5 MICRO LOTE-MICRO-V2"
git -C "C:/Users/London1/orca/workspaces/eame-sintonia/integra-onda2-v1" show 727bd0aa:ferramentas/rendimento/LOTE-MICRO-V2.json > $OUT/LOTE-MICRO-V2.json
py -B - "$(echo $OUT | sed 's#^/c/#C:/#')" <<'EOF'
import json, sys
o = sys.argv[1]; sys.path[:0] = ["scripts/micro_coleta", "."]
import micro_coleta as M
ids = [x["SOURCE_ID"] for x in json.load(open(o + "/LOTE-MICRO-V2.json", encoding="utf-8"))["LOTE"]]
p = M.plano(ids); json.dump(p, open(o + "/5-MICRO-SO-PLANO.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for l in p["LINHAS"]: print(l["SOURCE_ID"], l.get("ESTADO"), l.get("FALTA"))
EOF
echo "== 6 prova-teto sobre os dois planos"
py -B provas/prova_teto_dominio.py --plano "$(echo $OUT | sed 's#^/c/#C:/#')/4-ONDA2-SO-PLANO.json" --coorte ferramentas/big_collection/COORTE-BIG-COLLECTION-V1.json --json "$(echo $OUT | sed 's#^/c/#C:/#')/6-PROVA-TETO-ONDA2.json" 2>/dev/null | head -8
py -B - "$(echo $OUT | sed 's#^/c/#C:/#')" <<'EOF'
import json, sys
o = sys.argv[1]; sys.path.insert(0, "provas")
import prova_teto_dominio as T
p = json.load(open(o + "/5-MICRO-SO-PLANO.json", encoding="utf-8"))
ind = T.indices_dos_contratos(open("regras/italy_contracts_onboarded.json", encoding="utf-8").read(), open("regras/italy_contracts.mjs", encoding="utf-8").read())
pr = [l["SOURCE_ID"] for l in p["LINHAS"] if l.get("ESTADO") == "PRONTA"]
plano = {"PEDIDOS_POR_DOMINIO": {}}
for s in pr:
    d = T.dominio_registavel(ind[s]); plano["PEDIDOS_POR_DOMINIO"][d] = plano["PEDIDOS_POR_DOMINIO"].get(d, 0) + 5
r = T.verificar_plano(plano, pr, ind); r["BASE"] = "pior caso: 5 pedidos por fonte PRONTA"; r["PRONTAS"] = pr
json.dump(r, open(o + "/6-PROVA-TETO-MICRO.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("PROVA_TETO_DOMINIO_PLANO(MICRO)=%s %s" % (r["ESTADO"], r["PEDIDOS_PREVISTOS_POR_DOMINIO"]))
EOF
echo "== 7 desfazer"
git status > $OUT/7-antes-de-desfazer-status.txt
git -c user.name=ensaio -c user.email=ensaio@local revert --no-edit HEAD >/dev/null 2>&1
git show HEAD:regras/italy_contracts_onboarded.json > regras/italy_contracts_onboarded.json
echo "tabela reposta: $(sha256sum regras/italy_contracts_onboarded.json | cut -c1-8) (antes $T0) | LIFECYCLE-LEDGER $(sha256sum curadoria/LIFECYCLE-LEDGER-V1.json | cut -c1-8) (antes $L0)" | tee $OUT/7-desfazer.txt
py -c "import json;c=json.load(open('ferramentas/big_collection/COORTE-BIG-COLLECTION-V1.json',encoding='utf-8'));print('coorte depois de desfazer:',c['ESTADO'],c['COORTE_BIG_COLLECTION'])" 2>/dev/null | tee -a $OUT/7-desfazer.txt
