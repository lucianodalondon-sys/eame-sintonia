#!/bin/bash
# ENSAIO INTEGRADO (ONDA3-REBASE, onda3-pacote-v2) numa copia fiel do vivo, REDE FECHADA (D41.3). O robo NAO corre.
# uso: bash ensaio_onda3.sh <commit do pacote> <pasta de saida, forma C:/...>
# A copia e uma worktree destacada no HEAD do VIVO + os 14 livros sujos do vivo; o pacote entra
# por `git merge --no-ff`, como na instalacao. Nenhuma escrita no vivo (so leitura dos livros).
set -u
PACOTE=$1; OUT=$2
REPO=C:/Users/London1/orca/workspaces/eame-sintonia/reparo-fontes-v1
VIVO=C:/Users/London1/orca/workspaces/eame-sintonia/source-curator-service-v1
C=C:/ens-o3v2
export HTTPS_PROXY=http://127.0.0.1:9 HTTP_PROXY=http://127.0.0.1:9 https_proxy=http://127.0.0.1:9 http_proxy=http://127.0.0.1:9 ALL_PROXY=http://127.0.0.1:9 NO_PROXY= PYTHONUTF8=1
# ⚠️ OS LIVROS SAO OS FICHEIROS SUJOS DO VIVO, LIDOS NA HORA — nunca uma lista fixa.
# Medido (25/09): a lista fixa tinha 14; o vivo tinha 16 (+ a tabela do coletor e a prova de
# rotas, escritas pelo onboarding do supervisor). A copia leu a tabela do Git (193) em vez da
# do disco (210) e o ensaio disse «as 17 da PONTE nao entraram» — falso.
# Leitura sem trancar o indice do vivo (--no-optional-locks).
LIVROS=$(git -C $VIVO --no-optional-locks status --short | grep '^ M' | awk '{print $2}' | tr '
' ' ')
G="git -c user.name=ensaio -c user.email=ensaio@local -C $C"
rm -rf "$OUT"; mkdir -p "$OUT"
git -C $REPO worktree remove --force $C 2>/dev/null; rm -rf $C
HEAD_VIVO=$(git -C $VIVO rev-parse HEAD)
git -C $REPO worktree add -q --detach $C $HEAD_VIVO || exit 1
echo "COPIA: worktree destacada no HEAD do vivo $(git -C $VIVO rev-parse --short HEAD) ($(git -C $VIVO branch --show-current)); pacote $PACOTE" | tee $OUT/0-copia.txt
git -C $VIVO --no-optional-locks status --short | grep -v '^??' > $OUT/0-vivo-status.txt
echo "FOTO $(date -u '+%F %TZ') dos $(echo $LIVROS | wc -w) livros (ficheiros sujos) do vivo" > $OUT/0-FOTO-DOS-LIVROS.txt
# o pacote NAO pode mudar nenhum livro no Git (senao o merge recusa ou pisa o livro vivo)
TOCA=$(git -C $REPO diff --name-only $(git -C $VIVO rev-parse HEAD) $PACOTE -- $LIVROS | wc -l)
echo "livros que o pacote muda no Git: $TOCA" | tee $OUT/0-pacote-toca-livros.txt; [ "$TOCA" = 0 ] || { echo "PACOTE TOCA LIVROS - PARAR"; exit 3; }
# a FOTO fica guardada fora da copia: o desfazer repoe DESTA foto, como o plano repoe do $CORTE
# (o vivo continua a escrever — a 2.a onda corria durante o ensaio de 25/09 — e reler o vivo nao prova nada)
FOTO=C:/ens-o3v2-foto; rm -rf $FOTO
for f in $LIVROS; do mkdir -p $FOTO/$(dirname $f); cp $VIVO/$f $FOTO/$f; cp $FOTO/$f $C/$f; echo "$(sha256sum $FOTO/$f | cut -c1-64) $f" >> $OUT/0-FOTO-DOS-LIVROS.txt; done
cd $C
py -c "import urllib.request;urllib.request.urlopen('https://www.cia.it',timeout=5)" >/dev/null 2>&1 && { echo "REDE ABERTA - PARAR"; exit 2; } || echo "rede fechada: confirmada (www.cia.it recusado)" | tee -a $OUT/0-copia.txt

# ── A: ANTES (vivo de hoje) ─────────────────────────────────────────────────
py -B curadoria/collection_gate.py --json 2>/dev/null | py -c "import json,sys;d=json.load(sys.stdin);print('PAINEL ANTES',json.dumps(d['PAINEL']))" | tee $OUT/A-antes.txt
py -B curadoria/onboardar_rotas_provadas.py 2>/dev/null | tail -1 | sed 's/^/onboarding ANTES: /' | tee -a $OUT/A-antes.txt
py -B scripts/micro_coleta/micro_coleta.py plano > $OUT/A-PLANO-ANTES.json 2>$OUT/A-PLANO-ANTES.err
py -c "import json;p=json.load(open(r'$OUT/A-PLANO-ANTES.json',encoding='utf-8'));print('plano ANTES: PRONTAS',p['PRONTAS'],'BLOQUEADAS',p['BLOQUEADAS'])" | tee -a $OUT/A-antes.txt

# ── 1: merge do pacote, livros iguais ───────────────────────────────────────
T0=$(sha256sum regras/italy_contracts_onboarded.json | cut -c1-8)
py -c "import json;print('tabela do coletor (disco do vivo):',len(json.load(open('regras/italy_contracts_onboarded.json',encoding='utf-8'))['FONTES']),'fontes')" | tee -a $OUT/A-antes.txt
( for f in $LIVROS; do sha256sum $f; done ) > $OUT/1-livros-antes.sha
$G merge --no-ff -q $PACOTE -m "ENSAIO: merge do pacote" > $OUT/1-merge.txt 2>&1; echo "merge rc=$? conflitos=$($G diff --name-only --diff-filter=U | wc -l)" | tee -a $OUT/1-merge.txt
( for f in $LIVROS; do sha256sum $f; done ) > $OUT/1-livros-depois.sha
diff -q $OUT/1-livros-antes.sha $OUT/1-livros-depois.sha >/dev/null && echo "livros IGUAIS depois do merge" | tee -a $OUT/1-merge.txt || echo "LIVROS MUDARAM - PARAR" | tee -a $OUT/1-merge.txt
echo "tabela do coletor: vivo $T0 -> depois do merge $(sha256sum regras/italy_contracts_onboarded.json | cut -c1-8)" | tee -a $OUT/1-merge.txt

# ── 2: D49 + D51 (duplicadas) ───────────────────────────────────────────────
C0=$(sha256sum curadoria/italy_contracts_curator.json | cut -c1-8)
py -B curadoria/retirar_duplicadas_d49.py 2>/dev/null | tee $OUT/2-duplicadas-mostrar.txt
py -B curadoria/retirar_duplicadas_d49.py --aplicar 2>/dev/null | tail -1 | tee -a $OUT/2-duplicadas-mostrar.txt
py -B curadoria/retirar_duplicadas_d49.py 2>/dev/null | sed 's/^/2.a passagem: /' | tee -a $OUT/2-duplicadas-mostrar.txt
echo "livro de contratos $C0 -> $(sha256sum curadoria/italy_contracts_curator.json | cut -c1-8)" | tee -a $OUT/2-duplicadas-mostrar.txt

# ── 2b: D52 (62 ordens institucionais, RETIRADA_POR_DECISAO) — depois da D49/D51 ──
C1=$(sha256sum curadoria/italy_contracts_curator.json | cut -c1-64)
py -B curadoria/retirar_por_decisao.py --decisao D52 2>/dev/null | head -3 | sed 's/^/D52 mostrar: /' | tee $OUT/2b-d52.txt
py -B curadoria/retirar_por_decisao.py --decisao D52 --escrever 2>/dev/null | grep -E "APLICA|escrito" | head -2 | sed 's/^/D52 escrever: /' | tee -a $OUT/2b-d52.txt
py -B curadoria/retirar_por_decisao.py --decisao D52 2>/dev/null | head -1 | sed 's/^/D52 2.a passagem: /' | tee -a $OUT/2b-d52.txt
C2=$(sha256sum curadoria/italy_contracts_curator.json | cut -c1-64)
py -B - <<'EOF' | tee -a $OUT/2b-d52.txt
import json
d52 = {x.get("SOURCE_ID") for x in json.load(open("curadoria/DECISAO-D52-RETIRAR-V1.json", encoding="utf-8")).get("FONTES", [])}
dup = {"IT-T2-056", "IT-T2-106", "IT-T7-100", "IT-T7-170", "IT-T8-068"}
print("D52 x D49/D51 em comum:", sorted(d52 & dup) or "nenhuma", "| Palermo IT-T7-226 na D52:", "IT-T7-226" in d52)
EOF

# ── 3: provas de rota (0 pedidos: PONTE 06:38Z + C44 09:46Z + HR6 10:42Z) e onboarding ─────
py -B - <<'EOF' | tee $OUT/3-onboarding.txt
import json, sys
sys.path[:0] = ["medidas", "."]
import canario_rotas_elegiveis as C
v = json.load(open("curadoria/ROTAS-ELEGIVEIS-V1.json", encoding="utf-8"))
for p in ("ferramentas/ponte_onboard/ENSAIO-2-rotas-provadas-3rondas.json",
          "ferramentas/contrato44/ROTAS-PROVADAS-C44.json",
          "ferramentas/hr6/ROTAS-PROVADAS-HR6.json"):
    e = json.load(open(p, encoding="utf-8"))
    v["LINHAS"] = C.juntar(v.get("LINHAS", []), e["LINHAS"])
    print("juntada %s (%d linhas)" % (p, len(e["LINHAS"])))
json.dump(v, open("curadoria/ROTAS-ELEGIVEIS-V1.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("prova de rotas: 0 pedidos de rede")
EOF
py -B curadoria/onboardar_rotas_provadas.py 2>/dev/null > $OUT/3-onboarding-mostrar.txt
tail -1 $OUT/3-onboarding-mostrar.txt | sed 's/^/onboarding COM as provas: /' | tee -a $OUT/3-onboarding.txt
py -B curadoria/onboardar_rotas_provadas.py --aplicar 2>/dev/null | grep -E "ENTRA=|escritas" | tee -a $OUT/3-onboarding.txt
py -c "import json;print('tabela do coletor depois:',len(json.load(open('regras/italy_contracts_onboarded.json',encoding='utf-8'))['FONTES']),'fontes')" | tee -a $OUT/3-onboarding.txt

# ── 4: o que o robo vai medir (sem rede: so a lista) ────────────────────────
py -B - <<'EOF' | tee $OUT/4-robo-vai-medir.txt
import sys
from datetime import datetime, timezone
sys.path.insert(0, "curadoria")
import gatilho_discovery as GD
c = GD.candidatas_a_reparar(datetime.now(timezone.utc))
r15 = [x["SOURCE_ID"] for x in c if x["MOTIVO"].startswith("revisao nova")]
print("REVISAO-15: re-medir UMA vez (VALIDATE_ROUTE):", len(r15), r15)
print("outras tarefas do gatilho nesta volta:", len(c) - len(r15))
EOF
py -B ferramentas/hr6/remedir_hr6.py --fontes=IT-T7-174 --aplicar 2>/dev/null | grep -E "APLICADO|MOSTRAR" | tee -a $OUT/4-robo-vai-medir.txt

# ── 5: DEPOIS (sem rede) ────────────────────────────────────────────────────
py -B curadoria/collection_gate.py --json 2>/dev/null | py -c "import json,sys;d=json.load(sys.stdin);print('PAINEL DEPOIS',json.dumps(d['PAINEL']))" | tee $OUT/5-depois.txt
py -B scripts/micro_coleta/micro_coleta.py plano > $OUT/5-PLANO-DEPOIS.json 2>$OUT/5-PLANO-DEPOIS.err
py -c "import json;p=json.load(open(r'$OUT/5-PLANO-DEPOIS.json',encoding='utf-8'));print('plano DEPOIS: PRONTAS',p['PRONTAS'],'BLOQUEADAS',p['BLOQUEADAS'])" | tee -a $OUT/5-depois.txt

# ── 6: coorte da 3.a onda PROVISORIA (ficheiro proprio; commit SO na copia) + so-plano + prova-teto ──
py -B ferramentas/big_collection/coorte_unica.py --plano="$OUT/5-PLANO-DEPOIS.json" --saida=ferramentas/big_collection/COORTE-ONDA3-PROVISORIA.json 2>/dev/null | tee $OUT/6-coorte.txt
$G add ferramentas/big_collection/COORTE-ONDA3-PROVISORIA.json && $G commit -q -m "ENSAIO so na copia: coorte da 3.a onda PROVISORIA"
cp ferramentas/big_collection/COORTE-ONDA3-PROVISORIA.json $OUT/6-COORTE-ONDA3-PROVISORIA.json
py -B ferramentas/big_collection/onda_web.py --so-plano --coorte=ferramentas/big_collection/COORTE-ONDA3-PROVISORIA.json --saida="$OUT/onda3" > $OUT/6-ONDA3-SO-PLANO.json 2>$OUT/6-ONDA3-SO-PLANO.err
py -B provas/prova_teto_dominio.py --plano "$OUT/6-ONDA3-SO-PLANO.json" --coorte ferramentas/big_collection/COORTE-ONDA3-PROVISORIA.json --json "$OUT/6-PROVA-TETO-ONDA3.json" 2>&1 | head -8 | tee $OUT/6-prova-teto.txt

# ── 7: testes da juncao (sem rede) ──────────────────────────────────────────
py -B -m unittest curadoria.test_retirar_por_decisao curadoria.test_gatilho_discovery curadoria.test_gatilho_ocioso curadoria.test_retirar_duplicadas_d49 curadoria.test_canario_detalhe curadoria.test_reparar_contrato curadoria.test_revisao_ready curadoria.test_um_so_canario_promove curadoria.test_ready_split 2>&1 | tail -3 | tee $OUT/7-testes.txt
echo "hr6/test_remedir_hr6: $(cd ferramentas/hr6 && py -B -m unittest test_remedir_hr6 2>&1 | grep -E '^Ran|^OK|FAILED' | tr '
' ' ')" | tee -a $OUT/7-testes.txt
for t in tests/test_onda3_b_inerte.py tests/test_importar_do_coletor.py tests/test_legacy_recheck.py tests/test_legacy_colchetes.py tests/test_onda_web.py tests/test_onda_web_fontes.py tests/test_teto_dominio.py tests/test_canario_rotas_contrato_certo.py tests/test_onboardar_rotas_provadas.py tests/test_prova_teto_dominio.py; do echo "$t: $(py -B $t 2>&1 | grep -E '^Ran|^OK|FAILED' | tr '
' ' ')"; done | tee -a $OUT/7-testes.txt
echo "motor_de_rota_test.mjs: $(node regras/motor_de_rota_test.mjs 2>&1 | grep -E 'PASSOU' | tail -1)" | tee -a $OUT/7-testes.txt
echo "teto_dominio_local.mjs: $(node provas/teto_dominio_local.mjs 2>&1 | tail -1)" | tee -a $OUT/7-testes.txt


# ── V2: bloco A da LEGACY-99 (codigo ja no pacote), so as 21 paginas web, pelos lotes do plano ──
py -B - <<'EOF' | tee $OUT/V2-A-b-inerte-antes.txt
import json
c = json.load(open("curadoria/italy_contracts_curator.json", encoding="utf-8"))["FONTES"]
n = [x["SOURCE_ID"] for x in c if (x.get("ACQUISITION") or {}).get("ADAPTER_ID") == "CANAL_PUBLICO_YOUTUBE_V1"]
print("contratos do Curator com a rota do B (CANAL_PUBLICO_YOUTUBE_V1) ANTES:", len(n), n[:5])
EOF
py -B curadoria/importar_do_coletor.py > $OUT/V2-A-importar-mostrar.txt 2>&1
tail -1 $OUT/V2-A-importar-mostrar.txt | sed 's/^/bloco A mostrar: /'
L1=$(py -c "import json;print(','.join(json.load(open('ferramentas/onda3_pacote/LOTES-A-HTML.json',encoding='utf-8'))['LOTES'][0]))")
L2=$(py -c "import json;print(','.join(json.load(open('ferramentas/onda3_pacote/LOTES-A-HTML.json',encoding='utf-8'))['LOTES'][1]))")
py -B curadoria/importar_do_coletor.py --aplicar --ids=$L1 > $OUT/V2-A-importar-lote1.txt 2>&1; tail -2 $OUT/V2-A-importar-lote1.txt | sed 's/^/lote A1: /'
py -B curadoria/importar_do_coletor.py --aplicar --ids=$L2 > $OUT/V2-A-importar-lote2.txt 2>&1; tail -2 $OUT/V2-A-importar-lote2.txt | sed 's/^/lote A2: /'
py -B - "$L1,$L2" <<'EOF' | tee $OUT/V2-A-condicoes.txt
import json, sys
from unittest import mock
sys.path.insert(0, "curadoria")
import lifecycle as LC, worker as W, canario as CAN
ids = sys.argv[1].split(",")
c = {x["SOURCE_ID"]: x for x in json.load(open("curadoria/italy_contracts_curator.json", encoding="utf-8"))["FONTES"]}
b = [s for s, x in c.items() if (x.get("ACQUISITION") or {}).get("ADAPTER_ID") == "CANAL_PUBLICO_YOUTUBE_V1"]
print("(1) contratos com a rota do B DEPOIS da importacao:", len(b), b[:5])
yt = [s for s in ids if "youtube" in json.dumps(c.get(s, {})).lower()]
print("(1) do lote, com YouTube no contrato:", len(yt), yt)
est = {s: LC.estado_de(s) for s in ids}
print("estados depois da importacao:", dict(__import__("collections").Counter(est.values())))
ok, outros, perg = 0, [], []
with mock.patch.object(W.GATE, "robots_de", return_value=(object(), "lido")), \
     mock.patch.object(W.GATE, "permitido", side_effect=lambda u, rp: perg.append(u) or True), \
     mock.patch.object(CAN, "url_da_rota", side_effect=AssertionError("rota do B")):
    for s in ids:
        r, info = W.etapa_validate_route(s, c[s])
        if r == "OK" and perg and perg[-1] == c[s]["ACQUISITION"].get("INDEX_URL"):
            ok += 1
        else:
            outros.append((s, r, str(info)[:80]))
print("(2) paginas web do bloco A que validam pela producao (INDEX_URL, robots simulado):", ok, "de", len(ids), outros)
EOF

# ── BC: a tabela pedida (uniao por SOURCE_ID) ──
py -B - "$OUT" <<'EOF' | tee $OUT/BC-TABELA.txt
import json, sys, collections
o = sys.argv[1]
L = lambda f: json.load(open(o + "/" + f, encoding="utf-8"))
a, b = L("A-PLANO-ANTES.json"), L("5-PLANO-DEPOIS.json")
c, s = L("6-COORTE-ONDA3-PROVISORIA.json"), L("6-ONDA3-SO-PLANO.json")
def ids(linhas):
    x = [l["SOURCE_ID"] for l in linhas]
    return x, len(x) - len(set(x))
pa, da = ids([l for l in a["LINHAS"] if l["ESTADO"] == "PRONTA"])
pb, db = ids([l for l in b["LINHAS"] if l["ESTADO"] == "PRONTA"])
co, dc = ids(c["COORTE"])
salta = set(s["SALTAM_POR_TETO_DOMINIO"])
corre = [x for x in co if x not in salta]
uni = lambda sid: sid.split("-")[1]
D29 = {"T2", "T3"}
print("REPETIDOS por SOURCE_ID: prontas antes %d · depois %d · coorte %d" % (da, db, dc))
print("PRONTAS antes %d -> depois %d (+%d novas, %d perdidas: %s)" % (len(set(pa)), len(set(pb)), len(set(pb) - set(pa)), len(set(pa) - set(pb)), sorted(set(pa) - set(pb))))
print("COORTE congelavel %d · CORREM %d (saltam por teto %d, parciais %d) · pedidos previstos %s · max por dominio %s"
      % (len(set(co)), s["CORREM"], len(salta), len(s["PARCIAIS"]), s["PEDIDOS_TOTAL_PREVISTO"], s["MAXIMO_POR_DOMINIO"]))
print("%-5s %8s %8s %7s %7s" % ("univ", "p.antes", "p.depois", "coorte", "correm"))
U = sorted({uni(x) for x in set(pa) | set(pb)}, key=lambda u: int(u[1:]))
for u in U:
    f = lambda xs: sum(1 for x in set(xs) if uni(x) == u)
    print("%-5s %8d %8d %7d %7d" % (u, f(pa), f(pb), f(co), f(corre)))
f = lambda xs: sum(1 for x in set(xs) if uni(x) in D29)
print("%-5s %8d %8d %7d %7d" % ("D29", f(pa), f(pb), f(co), f(corre)))
print("TOTAL %8d %8d %7d %7d" % (len(set(pa)), len(set(pb)), len(set(co)), len(corre)))
json.dump({"PRONTAS_ANTES": sorted(set(pa)), "PRONTAS_DEPOIS": sorted(set(pb)), "COORTE": sorted(set(co)),
           "CORREM": sorted(corre), "SALTAM": sorted(salta), "PARCIAIS": s["PARCIAIS"],
           "PEDIDOS": s["PEDIDOS_TOTAL_PREVISTO"], "PEDIDOS_POR_DOMINIO": s["PEDIDOS_POR_DOMINIO"]},
          open(o + "/BC-LISTAS.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
EOF

# ── 8: DESFAZER provado ─────────────────────────────────────────────────────
git status --short > $OUT/8-antes-de-desfazer-status.txt
# D52 --reverter devolve o livro de contratos aos mesmos bytes de antes da D52
py -B curadoria/retirar_por_decisao.py --decisao D52 --reverter --escrever 2>/dev/null | head -1 | sed 's/^/D52 reverter: /' | tee $OUT/8-d52-reverter.txt
[ "$(sha256sum curadoria/italy_contracts_curator.json | cut -c1-64)" = "$C1" ] && echo "D52 reverter: livro de contratos = antes da D52 (byte a byte)" | tee -a $OUT/8-d52-reverter.txt || echo "D52 reverter: DIFERENTE" | tee -a $OUT/8-d52-reverter.txt
# como no vivo: o codigo volta por reset --keep (o pacote nao toca livros, por isso nada recusa),
# e os livros escritos (contratos pela D49/D51; tabela e prova pelo onboarding; livro e fila pela HR-6) voltam da foto
$G reset -q --keep $HEAD_VIVO; echo "reset --keep rc=$?" | tee $OUT/8-desfazer-reset.txt
for f in $LIVROS; do cp $FOTO/$f $C/$f; done
( for f in $LIVROS; do sha256sum $f; done ) > $OUT/8-livros-desfeito.sha
diff -q $OUT/1-livros-antes.sha $OUT/8-livros-desfeito.sha >/dev/null && echo "DESFAZER: livros = foto do vivo" | tee $OUT/8-desfazer.txt || echo "DESFAZER: livros DIFERENTES" | tee $OUT/8-desfazer.txt
# o codigo compara-se SEM os 14 livros (esses estao sujos no proprio vivo, por desenho)
DIF=$($G diff --name-only $HEAD_VIVO | grep -v -x -F -f <(echo "$LIVROS" | tr ' ' '
') | wc -l)
echo "tabela $(sha256sum regras/italy_contracts_onboarded.json | cut -c1-8) (vivo $T0) · ficheiros de codigo diferentes do vivo: $DIF · HEAD = vivo: $([ "$($G rev-parse HEAD)" = "$HEAD_VIVO" ] && echo SIM || echo NAO)" | tee -a $OUT/8-desfazer.txt
py -B scripts/micro_coleta/micro_coleta.py plano 2>/dev/null | py -c "import json,sys;p=json.load(sys.stdin);print('plano depois de desfazer: PRONTAS',p['PRONTAS'])" | tee -a $OUT/8-desfazer.txt
cd /c
git -C $REPO worktree remove --force $C; rm -rf $FOTO
echo "copia removida"
