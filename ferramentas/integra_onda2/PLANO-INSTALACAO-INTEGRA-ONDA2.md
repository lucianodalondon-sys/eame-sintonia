# Plano de instalação — INTEGRA-ONDA2 (quem executa: o coordenador; um escritor no vivo)

Instala de uma vez: ONDA2-G3 (a55c667f) + CAPA-MATERIA/ALVOS-NOVOS (a1dbebcc) + PONTE-ONBOARD (7e3fed2c)
+ PROVA-TETO (ed29f2d6). Ensaiado em cópia fiel do vivo com a rede fechada (`RELATORIO-INTEGRA-ONDA2.md`).

`<VIVO>` = `C:\Users\London1\orca\workspaces\eame-sintonia\source-curator-service-v1`
`<CORTE>` = uma pasta nova de backup, ex.: `C:\cutover\integra-onda2-<data>`
`<INTEGRA>` = o SHA entregue como `INTEGRADO PRONTO`.

## 0 · Antes (sem rede)

1. **Bot quieto:** parar o supervisor e o worker (procedimento habitual); confirmar que nenhum `py curadoria/supervisor.py` corre.
2. **Vivo na base certa:**
   ```
   git -C <VIVO> rev-parse --short HEAD        → tem de dar 7cdb7ea4
   git -C <VIVO> status --short                → só livros sujos (curadoria/*.json, candidatas/, data/); nenhum ficheiro de código
   ```
   Se o HEAD não for 7cdb7ea4: PARAR — refazer a integração contra o vivo novo.
3. **Corte (backup) com sha256:**
   ```
   mkdir <CORTE>
   copy <VIVO>\regras\italy_contracts_onboarded.json               <CORTE>\
   copy <VIVO>\curadoria\ROTAS-ELEGIVEIS-V1.json                   <CORTE>\
   copy <VIVO>\ferramentas\big_collection\COORTE-BIG-COLLECTION-V1.json <CORTE>\
   certutil -hashfile <CORTE>\italy_contracts_onboarded.json SHA256   → no ensaio: 856f833f…
   ```

## 1 · Instalar o código (bot quieto)

```
cd <VIVO>
git fetch origin integra-onda2-v1
git merge --ff-only <INTEGRA>                 # 7cdb7ea4 é antepassado: fast-forward
git rev-parse --short HEAD                    → <INTEGRA>
```

## 2 · Conferir o mapa e os testes da junção (sem rede)

```
py system-map/scripts/correr_a_cadeia.py VALIDAR     → SYSTEM_MAP_CHECK=PASS
py -B tests/test_onda_web.py                          → 12 OK
py -B tests/test_teto_dominio.py                      → 1 OK
py -B tests/test_canario_rotas_contrato_certo.py      → 6 OK
py -B tests/test_onboardar_rotas_provadas.py          → 29 OK
py -B tests/test_prova_teto_dominio.py                → 19 OK
node regras/motor_de_rota_test.mjs                    → PASSOU 60 · FALHOU 0
node provas/teto_dominio_local.mjs                    → passou=7 FALHAS=0
```

## 3 · Religar o supervisor

Tarefa `SINTONIA-Arranque` (ou o procedimento habitual). Ele só carrega o código novo ao arrancar.
No diário do supervisor aparece `ONBOARDING` com `NINGUEM_ENTROU` (as provas antigas não têm impressão).

## 4 · Prova de rota — a ÚNICA etapa com rede (D41.3; D38)

- **Portão de consenso** antes e depois de cada ronda: `py superficie/rede.py --portao-de-egresso IT` → `EGRESS_GATE=PASS`.
- **Lista filtrada:** só o `FICA` de
  ```
  py curadoria/onboardar_rotas_provadas.py
  ```
  (no ensaio: 44 antes da prova; 17 entram com a prova). **≤ 1 fonte por domínio por ronda**, como no `ENSAIO-2` da PONTE.
- Por ronda:
  ```
  py medidas/canario_rotas_elegiveis.py --fontes=<ronda 1, separadas por vírgula> --juntar
  py medidas/canario_rotas_elegiveis.py --fontes=<ronda 2> --juntar
  ...
  ```

## 5 · Ver entrar no coletor (sem mais comandos)

Em ≤ 10 min o supervisor anota `ONBOARDING` / `ONBOARDOU` com `ESCRITAS` (ensaio: **17**). Conferir:
```
py curadoria/onboardar_rotas_provadas.py        → ENTRA=0
certutil -hashfile regras\italy_contracts_onboarded.json SHA256   → mudou (ensaio: 6255cd27…)
```

## 6 · Congelamento REAL da coorte (sem rede)

```
py scripts/micro_coleta/micro_coleta.py plano > <CORTE>\PLANO-RUNBOOK.json
py ferramentas/big_collection/coorte_unica.py --plano=<CORTE>\PLANO-RUNBOOK.json --congelar ^
   --instalacao=<INTEGRA> --demotion=<referencia B5> ^
   --saida=ferramentas/big_collection/COORTE-BIG-COLLECTION-V1.json
```
⚠️ Sem `--saida=` a ferramenta só imprime. Depois, **commit no ramo do vivo** (o disparador confere `git show HEAD:`):
```
git add ferramentas/big_collection/COORTE-BIG-COLLECTION-V1.json
git commit -m "coorte da 2.a onda CONGELADA (instalacao <INTEGRA>, demotion <ref B5>)"
```
(ensaio: CONGELADA **29**.)

## 7 · Planos da 2.ª onda e do MICRO (sem rede) e a prova do teto sobre eles

```
py ferramentas/big_collection/onda_web.py --so-plano --saida=<CORTE>\onda2 > <CORTE>\ONDA2-SO-PLANO.json
     → PODE_CORRER=true; guardar COORTE_SHA256_DO_COMMIT (é o --sha256= do passo de correr)
py provas/prova_teto_dominio.py --plano <CORTE>\ONDA2-SO-PLANO.json --coorte ferramentas/big_collection/COORTE-BIG-COLLECTION-V1.json
     → PROVA_TETO_DOMINIO_PLANO=PASS (ensaio: 83 previstos, máximo 5)
py -c "import sys,json; sys.path[:0]=['scripts/micro_coleta','.']; import micro_coleta as M; lote=json.load(open(r'<caminho do LOTE-MICRO-V2.json>',encoding='utf-8')); print(json.dumps(M.plano([x['SOURCE_ID'] for x in lote['LOTE']]),ensure_ascii=False,indent=1))" > <CORTE>\MICRO-SO-PLANO.json
     → ensaio: 1 PRONTA de 6 — DECIDIR antes de correr o MICRO (ver RELATORIO §⚠️)
```

## 8 · Depois de CADA corrida real (MICRO e 2.ª onda): a prova independente do teto

```
py provas/prova_teto_dominio.py --livro data/collection-ledger/italy/runs.ndjson --onda <relatório/JSON da onda com os RUN_ID>
     → 0 = PASS · 1 = FAIL (domínio acima de 5, com hosts e corridas) · 2 = NAO_SEI (corrida sem linha no livro)
```

## Desfazer

- **Só as fontes que entraram:** `copy <CORTE>\italy_contracts_onboarded.json <VIVO>\regras\` → sha256 volta (ensaio: 856f833f). Provado na cópia.
- **Só o congelamento:** `git revert <commit da coorte>` → volta PROVISORIA (ensaio: 18). Provado na cópia.
- **O código:** `git reset --keep 7cdb7ea4` e religar o supervisor.
- Nenhum livro do Curator é escrito por esta instalação (LIFECYCLE-LEDGER igual no ensaio).
