# CONTRATO-44 · as elegíveis sem contrato de coleta — 25/09/2026

Ramo `contrato-44-v1`, a partir de `integra-onda2-v1` @ `e2f47ed3`. **NÃO instalado.** Motor: `claude-opus-5-5`.

## Em palavras simples

Das 73 fontes que o portão deixa colher, 44 estavam paradas só porque o coletor não tinha a ficha delas.
O pacote integrado (PONTE-ONBOARD) já resolve 17. Eu provei a rota de mais 16 (as fontes que ficaram
prontas com a R1 depois da prova da PONTE) e, numa cópia do vivo, **entram 33 no coletor**. O plano da
coleta passa de **18 prontas para 41**. Ficam 11 por resolver, cada uma com o motivo.

```
ANTES (plano do coordenador, 06:40)      PRONTAS 18 · BLOQUEADAS 55 · sem contrato 44
DEPOIS (cópia, pacote integrado + C44)   PRONTAS 41 · BLOQUEADAS 32 · sem contrato 11
das 44: pacote integrado 17 · CONTRATO-44 16 · por resolver 11
das 33 que entram, 10 continuam bloqueadas por SEM_RECEITA_WEB (T8/T12) — outro bloqueio, não desta missão
```

## 1 · As 44 (`LISTA-44.json`: SOURCE_ID, universo, domínio, janela D29, quem resolve, prova)

- **17 — pacote integrado** (prova da PONTE, 25/09 06:38Z): IT-T12-024, 117, 129, 130, 131; IT-T2-032, 037, 050, 145, 146; IT-T5-160, 167, 185, 186, 187; IT-T7-172; IT-T8-062.
- **16 — CONTRATO-44** (prova nova, 25/09 ~09:46–09:50Z): IT-T3-023; IT-T5-056, 080, 111, 113; IT-T7-019, 048, 049, 103, 125, 139, 163; IT-T8-022, 024, 041, 042.
- **11 — por resolver**, com a prova:

| fonte | porque não entra | de quem é |
|---|---|---|
| IT-T5-101, IT-T7-053, IT-T7-058 | robots ilegível desta saída (cnr.it, unaprol.it, veneto.coldiretti.it) — `UNKNOWN`, tratado como barrado | rede/egresso; repetir a prova noutra hora |
| IT-T12-104, IT-T3-045, IT-T7-115, IT-T7-120 | o canário do coletor abre capa/navegação (`CAPA_NAO_E_MATERIA`, MIXED) — o contrato aponta para a página errada | reparo do contrato (Curator), não prova de rota |
| IT-T2-056, IT-T2-106, IT-T7-100, IT-T8-068 | DUPLICADA (mesmo documento ou mesmo site+padrão de outra fonte já contratada) | decisão de identidade (dono) |

Janela D29 (T1/T2/T3 — leitura desta missão): 9 das 44; por resolver só 3 (IT-T2-056, IT-T2-106 duplicadas; IT-T3-045 capa).

## 2 · Porque as 16 não tinham contrato

Nenhuma tinha prova de rota (`SEM_CANARIO`): ficaram READY pela R1 (instalada 25/09 01:50) **depois**
da prova da PONTE; o contrato do Curator existe e é o do disco do vivo — faltava só a prova do coletor.

## 3 · A cópia (rede fechada por omissão, D41.3)

- `C:/c44` = `git archive` do ramo + os 14 livros sujos do vivo (`SHA-SUJOS.txt`), proxies `127.0.0.1:9`.
- Rede aberta **só** para `medidas/canario_rotas_elegiveis.py --juntar`, das 19 que faltavam (16 sem canário + 3 robots),
  em **4 rondas, 1 fonte por domínio por ronda (D38)**, portão por consenso = PASS IT antes de cada ronda (`RONDAS.log`).
  Até 4 pedidos por fonte (robots, entrada, ≤2 matérias). Resultado: 16 ROUTE_PROVEN, 3 UNKNOWN (robots).
- Onboarding (`curadoria/onboardar_rotas_provadas.py --aplicar`, na cópia): **ENTRA=33 FICA=11**; o livro do Curator ficou igual (`b53743af`).
- Plano (`scripts/micro_coleta/micro_coleta.py plano`, numa worktree descartável com o mesmo estado): **PRONTAS 41 / BLOQUEADAS 32**, nenhuma pronta perdida.
- Desfazer ensaiado: tabela e provas repostas ao Git → `ENTRA=0 FICA=44`, livro igual.

## 4 · Plano para o vivo (DEPOIS de a INTEGRA-ONDA2 estar instalada; um escritor; NÃO instalado)

As provas valem 7 dias: PONTE até **02/10 06:38Z**; CONTRATO-44 até **02/10 ~09:46Z**. Se o bot reescrever
algum destes contratos antes, o onboarding recusa essa fonte sozinho («o canário provou OUTRA aquisição»).

```bash
cd C:/Users/London1/orca/workspaces/eame-sintonia/source-curator-service-v1
# 0. bot quieto
touch curadoria/PARAR.flag                     # esperar o supervisor sair; 0 worker
# 1. foto e copia de seguranca (antes de mexer)
B=C:/cutover/c44-$(date -u +%Y%m%dT%H%MZ); mkdir -p $B
git status --short > $B/status.txt; git diff > $B/diff.txt
cp regras/italy_contracts_onboarded.json curadoria/ROTAS-ELEGIVEIS-V1.json curadoria/LIFECYCLE-LEDGER-V1.json $B/
sha256sum regras/italy_contracts_onboarded.json curadoria/ROTAS-ELEGIVEIS-V1.json curadoria/LIFECYCLE-LEDGER-V1.json > $B/sha-antes.txt
# 2. trazer as provas (so ficheiros de prova; nenhum codigo novo)
git fetch origin contrato-44-v1
git show origin/contrato-44-v1:ferramentas/contrato44/ROTAS-PROVADAS-C44.json > $B/c44.json
# 3. juntar as provas da PONTE e da C44 as que ja la estao (rede fechada)
HTTPS_PROXY=http://127.0.0.1:9 HTTP_PROXY=http://127.0.0.1:9 PYTHONUTF8=1 py -B - <<'EOF'
import json, sys; sys.path.insert(0, "medidas"); import canario_rotas_elegiveis as C
v = json.load(open("curadoria/ROTAS-ELEGIVEIS-V1.json", encoding="utf-8"))
for p in ("ferramentas/ponte_onboard/ENSAIO-2-rotas-provadas-3rondas.json", r"$B/c44.json"):
    v["LINHAS"] = C.juntar(v.get("LINHAS", []), json.load(open(p, encoding="utf-8"))["LINHAS"])
json.dump(v, open("curadoria/ROTAS-ELEGIVEIS-V1.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
EOF
# 4. mostrar, conferir ENTRA=33, e so entao aplicar
py -B curadoria/onboardar_rotas_provadas.py | tail -1          # esperado ENTRA=33 FICA=11
py -B curadoria/onboardar_rotas_provadas.py --aplicar
sha256sum curadoria/LIFECYCLE-LEDGER-V1.json                  # igual a sha-antes (o livro nao se toca)
py -B scripts/micro_coleta/micro_coleta.py plano | grep -E '"PRONTAS"|"BLOQUEADAS"'   # esperado 41 / 32
# 5. commit so da tabela e das provas; push; relancar
git add regras/italy_contracts_onboarded.json curadoria/ROTAS-ELEGIVEIS-V1.json
git commit -m "instalar CONTRATO-44: 33 fontes no coletor (17 PONTE + 16 C44), provas de rota <= 7 dias"
rm curadoria/PARAR.flag                         # relancar o supervisor como hoje
```

(`$B/c44.json` no passo 3: substituir pelo caminho real da pasta `$B`, o heredoc não expande variáveis.)

**DESFAZER:** `PARAR.flag` → `cp $B/italy_contracts_onboarded.json regras/ ; cp $B/ROTAS-ELEGIVEIS-V1.json curadoria/` →
conferir com `$B/sha-antes.txt` → `git commit` → relançar. O livro do Curator não muda em nenhum dos sentidos.

⚠️ Se a INTEGRA-ONDA2 já estiver instalada **com** o gancho do supervisor (`onboardar_se_mudou`, PONTE-ONBOARD),
basta o passo 3 com o bot parado: ao religar, o próprio supervisor onboarda. Conferir `ENTRA=33` antes de religar.

## 5 · Ressalvas

- O plano mediu-se com os livros do vivo `7cdb7ea4` de 09:4xZ; o bot pode mudar estados até à instalação — repetir o passo 4 (mostrar) antes de aplicar.
- As 3 com robots ilegível podem entrar noutra hora com a mesma prova (`canario_rotas_elegiveis.py --fontes=IT-T5-101,IT-T7-053,IT-T7-058 --juntar`), rede pelo portão.
- As 4 de capa pedem reparo do contrato (não é prova de rota); as 4 duplicadas pedem decisão de identidade.
