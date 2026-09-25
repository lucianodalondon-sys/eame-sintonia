# Plano de instalação — INTEGRA-ONDA2 (executa: o coordenador; um escritor no vivo)

Instala de uma vez: CONTRATOS-12 (54c98fe4, contém ONDA2-G3) + CONTRATOS-AJUSTE (ca923030, contém CAPA-MATERIA)
+ PONTE-ONBOARD (7e3fed2c) + PROVA-TETO (ed29f2d6). Números do ensaio final (`RELATORIO-INTEGRA-ONDA2.md`, `final/`):
**17 entram no coletor · coorte 28 (ISTAT fora, D45) · 2.ª onda 22 correm, 80 pedidos, máximo 5 por domínio.**

Comandos em Git Bash. Definir primeiro:
```bash
VIVO=/c/Users/London1/orca/workspaces/eame-sintonia/source-curator-service-v1
INTEGRA=<SHA entregue como INTEGRADO PRONTO>
D=$(date +%Y%m%d-%H%M); CORTE=/c/cutover/integra-onda2-$D; mkdir -p $CORTE
LIVROS="candidatas/FONTES-CANDIDATAS.json curadoria/BRIDGE-LEDGER-V1.json curadoria/DISCOVERY-SIGNAL-V1.json curadoria/DISCOVERY-VISITED.json curadoria/LIFECYCLE-EVIDENCE-V1.json curadoria/LIFECYCLE-LEDGER-V1.json curadoria/LIFECYCLE-QUEUE-V1.json curadoria/READY-BATCHES-V1.json curadoria/SOURCE-ID-ALLOCATION-V1.json curadoria/italy_contracts_curator.json data/collection-ledger/italy/observations.ndjson data/collection-ledger/italy/runs.ndjson data/samples/LIVRO-DE-DECISOES.json data/samples/RUN-MANIFEST.json"
MUDAM="regras/italy_contracts_onboarded.json curadoria/ROTAS-ELEGIVEIS-V1.json ferramentas/big_collection/COORTE-BIG-COLLECTION-V1.json"
```

## 1 · Parar o robô (⏱️ começa o tempo parado)
```bash
tasklist //V | grep -i -E "supervisor|worker|ponte_automatica|observador"      # anotar os PID
echo "integra-onda2 $(date -Iseconds)" > $VIVO/curadoria/PARAR.flag
for i in $(seq 1 60); do tasklist //FI "PID eq <PID_SUPERVISOR>" | grep -q <PID_SUPERVISOR> || break; sleep 1; done
taskkill //PID <PID_LANCADOR_OBSERVADOR> //T //F
# confirmar: nenhum supervisor|worker|ponte_automatica|observador vivo
```
🛑 Se algum processo não sair em 60 s: `rm $VIVO/curadoria/PARAR.flag`, relançar como estava, investigar.

## 2 · Backup dos livros e dos ficheiros que o merge muda (com sha256)
```bash
git -C $VIVO rev-parse --short HEAD          # TEM de dar 7cdb7ea4 — senão PARAR (refazer a integração)
git -C $VIVO status --short | grep -v '^??'  # só os 14 LIVROS sujos; nenhum ficheiro de código
for f in $LIVROS $MUDAM; do mkdir -p $CORTE/$(dirname $f); cp $VIVO/$f $CORTE/$f; done
( cd $CORTE && sha256sum $LIVROS $MUDAM > SHA256-ANTES.txt )
```
(esperado nos 3 que mudam: iguais ao Git de 7cdb7ea4 — a tabela `856f833f…`.)

## 3 · Merge do SHA integrado
```bash
git -C $VIVO fetch origin integra-onda2-v1
git -C $VIVO merge --ff-only $INTEGRA          # 7cdb7ea4 é antepassado: fast-forward
git -C $VIVO rev-parse HEAD                    # = $INTEGRA
```
O ramo só muda, dos ficheiros vivos, `regras/italy_contracts_onboarded.json` e `ferramentas/big_collection/COORTE-BIG-COLLECTION-V1.json`
(os dois limpos no vivo). Nenhum dos 14 livros.

## 4 · Conferência dos livros (sha256 IGUAL antes e depois)
```bash
( cd $VIVO && sha256sum $LIVROS ) > $CORTE/SHA256-LIVROS-DEPOIS.txt
diff <(grep -F -f <(echo "$LIVROS" | tr ' ' '\n') $CORTE/SHA256-ANTES.txt) $CORTE/SHA256-LIVROS-DEPOIS.txt && echo "LIVROS IGUAIS"
```
🛑 Se algum livro mudou: DESFAZER.

## 5 · Testes da junção (sem rede)
```bash
cd $VIVO
py -B tests/test_onda_web.py                         # 17 OK
py -B tests/test_teto_dominio.py                     # 1 OK
py -B tests/test_canario_rotas_contrato_certo.py     # 6 OK
py -B tests/test_onboardar_rotas_provadas.py         # 29 OK
py -B tests/test_prova_teto_dominio.py               # 19 OK
node regras/motor_de_rota_test.mjs                   # PASSOU 62 · FALHOU 0
node provas/teto_dominio_local.mjs                   # passou=7 FALHAS=0
```

## 6 · Mapa (carimbo IGUAL) — com a LOCK-PESADO
```bash
echo "INSTALAR integra-onda2 $(date -Iseconds)" > /c/Users/London1/auditoria-madrugada/LOCK-PESADO.txt   # se livre
py system-map/scripts/correr_a_cadeia.py VALIDAR     # SYSTEM_MAP_CHECK=PASS (o mapa foi regerado no ramo)
rm /c/Users/London1/auditoria-madrugada/LOCK-PESADO.txt
```
Se o validador deixar ficheiros gerados sujos só com carimbo: `git status > $CORTE/validar-status.txt; git diff > $CORTE/validar-diff.txt; git stash push -m "carimbo-validar-integra"`.

## 7 · Push
```bash
git -C $VIVO push origin HEAD:servico-20260923-0923
git -C $VIVO fetch origin && git -C $VIVO rev-parse HEAD origin/servico-20260923-0923   # iguais
```

## 8 · Religar o robô (⏱️ acaba o tempo parado)
```bash
rm $VIVO/curadoria/PARAR.flag
# supervisor pelo meio de sempre (Tarefa SINTONIA-Arranque; cwd $VIVO; py curadoria/supervisor.py); observador depois
```
O diário do supervisor mostra `ONBOARDING` com `NINGUEM_ENTROU` (as provas do vivo não têm impressão).

## 9 · Prova de rota — escolher UMA forma

**9A (recomendada, 0 pedidos):** reaproveitar a prova da PONTE de 25/09 06:38:58Z (vale até **02/10 06:38Z**) — foi o que o ensaio fez:
```bash
cd $VIVO && py -B - <<'EOF'
import json, sys; sys.path[:0] = ["medidas", "."]
import canario_rotas_elegiveis as C
v = json.load(open("curadoria/ROTAS-ELEGIVEIS-V1.json", encoding="utf-8"))
e = json.load(open("ferramentas/ponte_onboard/ENSAIO-2-rotas-provadas-3rondas.json", encoding="utf-8"))
v["LINHAS"] = C.juntar(v.get("LINHAS", []), e["LINHAS"]); v["GERADO_EM"] = e.get("GERADO_EM")
json.dump(v, open("curadoria/ROTAS-ELEGIVEIS-V1.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
EOF
```

**9B (rede; D41.3, D38):** refazer as rondas no vivo, SÓ as 17, ≤ 1 fonte por domínio por ronda, portão de consenso antes e depois de cada ronda:
```bash
py superficie/rede.py --portao-de-egresso IT        # EGRESS_GATE=PASS antes de CADA ronda e no fim
py medidas/canario_rotas_elegiveis.py --fontes=IT-T12-024,IT-T12-117,IT-T12-129,IT-T12-130,IT-T2-032,IT-T2-037,IT-T2-050,IT-T2-145,IT-T5-160,IT-T5-167,IT-T5-185,IT-T7-172,IT-T8-062 --juntar
py medidas/canario_rotas_elegiveis.py --fontes=IT-T12-131,IT-T2-146,IT-T5-186 --juntar
py medidas/canario_rotas_elegiveis.py --fontes=IT-T5-187 --juntar
```
(domínios repetidos: edagricole.it ×2, arpa.veneto.it ×2, enea.it ×3 → por isso 3 rondas.)

## 10 · Onboarding (≤ 10 min, sem comandos)
O supervisor anota `ONBOARDING` / `ONBOARDOU` com **ESCRITAS = 17** (ensaio). Conferir:
```bash
py -B curadoria/onboardar_rotas_provadas.py          # ENTRA=0 (já estão todas na tabela)
sha256sum regras/italy_contracts_onboarded.json      # mudou em relação ao passo 3
sha256sum curadoria/LIFECYCLE-LEDGER-V1.json         # (só o robô o muda; o onboarding não)
```

## 11 · Congelar a coorte REAL (sem rede)
```bash
py -B scripts/micro_coleta/micro_coleta.py plano > $CORTE/PLANO-RUNBOOK.json
py -B ferramentas/big_collection/coorte_unica.py --plano=$(cygpath -w $CORTE)/PLANO-RUNBOOK.json --congelar \
   --instalacao=$INTEGRA --demotion=<referencia B5> \
   --saida=ferramentas/big_collection/COORTE-BIG-COLLECTION-V1.json
#   → {"COORTE_BIG_COLLECTION": 28, ...}   (ensaio: 28; a ISTAT IT-T5-090 fica FORA por CONTRATO_EXECUTAVEL, D45)
git -C $VIVO add ferramentas/big_collection/COORTE-BIG-COLLECTION-V1.json
git -C $VIVO commit -m "coorte da 2.a onda CONGELADA: 28 (instalacao $INTEGRA; D45 ISTAT fora)"
git -C $VIVO push origin HEAD:servico-20260923-0923
```
⚠️ Sem `--saida=` a ferramenta só imprime.

## 12 · Plano da 2.ª onda + prova-teto (sem rede)
```bash
py -B ferramentas/big_collection/onda_web.py --so-plano --saida=$(cygpath -w $CORTE)/onda2 > $CORTE/ONDA2-SO-PLANO.json
#   → PODE_CORRER=true · FONTES 28 · CORREM 22 · MAXIMO_POR_DOMINIO 5 · PEDIDOS_TOTAL_PREVISTO 80
#   guardar COORTE_SHA256_DO_COMMIT: é o --sha256= do --correr
py -B provas/prova_teto_dominio.py --plano $(cygpath -w $CORTE)/ONDA2-SO-PLANO.json --coorte ferramentas/big_collection/COORTE-BIG-COLLECTION-V1.json
#   → PROVA_TETO_DOMINIO_PLANO=PASS · previstos=80
```

## 13 · Plano do MICRO-V3 + prova-teto (sem rede)
```bash
py -B ferramentas/integra_onda2/prova_teto_micro.py --lote <LOTE-MICRO-V3.json da APOIO-INTEGRA> \
   --saida $(cygpath -w $CORTE)/MICRO-V3-SO-PLANO.json --json $(cygpath -w $CORTE)/PROVA-TETO-MICRO-V3.json
#   → PROVA_TETO_MICRO=PASS e a lista das BLOQUEADAS com o FALTA de cada uma (V2 no ensaio: 1 PRONTA de 6)
```

## 14 · Depois de CADA corrida real (MICRO e 2.ª onda)
```bash
py -B provas/prova_teto_dominio.py --livro data/collection-ledger/italy/runs.ndjson --onda <relatório/JSON da onda com os RUN_ID>
#   0 = PASS · 1 = FAIL (domínio acima de 5) · 2 = NAO_SEI (corrida sem linha no livro)
```

## DESFAZER
- **As 17 fontes:** `cp $CORTE/regras/italy_contracts_onboarded.json $VIVO/regras/` (provado na cópia).
- **O congelamento:** `git -C $VIVO revert <commit da coorte>` → PROVISORIA (provado na cópia).
- **O código:** `echo desfazer > $VIVO/curadoria/PARAR.flag`; esperar o supervisor sair; `git -C $VIVO reset --keep 7cdb7ea4`;
  `cp $CORTE/<os 3 de MUDAM> …`; conferir `SHA256-ANTES.txt`; `rm PARAR.flag`; religar.
- Nenhum livro do Curator é escrito por esta instalação (LIFECYCLE-LEDGER igual no ensaio).
