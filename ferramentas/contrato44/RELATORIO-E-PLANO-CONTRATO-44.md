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

## 6 · v2 (ramo `contrato-44-v2`, 25/09): as 4 capas, as 3 com robots ilegível, as duplicadas

Cópia `C:/c44b` (ramo + os 14 livros do vivo `7cdb7ea4`; provas da PONTE e da C44 juntadas; rede
fechada por omissão). Rede só nas rondas abaixo, portão por consenso = PASS IT antes de cada uma, 1 fonte
por domínio por ronda, robots pela casa. **Nada entra a mais: continuam 33.**

**Capas (4) → 0 entram** (`CAPAS-4-PROVAS.json`, `REPARO-3-RONDA-B.json`)

| fonte | o que se fez | resultado |
|---|---|---|
| IT-T7-115 (cia.it Agenda) | prova de rota com o coletor de hoje (já tem o filtro de páginas institucionais da CAPA-MATERIA) | ROUTE_PROVEN — **mas o onboarding recusa: DUPLICADA de IT-T7-112** (mesmo site, mesmo padrão genérico) → vai para a pergunta das duplicadas |
| IT-T7-120 (INAC-CIA) | reparo pela R1 (`reparar_contrato.inferir`: família `/news/notizie/<slug>`, 1.º item matéria com 4236 caracteres) aplicado na cópia pela porta da R1, e prova de rota | CAPABILITY_BLOCK: o coletor abre «sei-un-pensionato» (página de serviço) — o padrão novo também a apanha. **O reparo não resolve**; contrato reposto. SUSPEITA |
| IT-T12-104 (geoportale Lombardia) | reparo propõe o MESMO contrato que já tem | o coletor abre «valore-agricolo-dei-suoli-2023», notícia curta que o juiz chama capa (erro conhecido do juiz; não se afrouxa). **NÃO SEI** |
| IT-T3-045 (AMAP Marche) | reparo | RECUSA: só há famílias de menu (amministrazione trasparente) — FAMILIA_E_MENU. **SUSPEITA** |

⚠️ O `reparar_contrato.aplicar` desta linha ainda não tem o parâmetro `decisao` (vem com a D44, ainda fora
de `integra-onda2-v1`); por isso o ensaio usou a porta como está (DECISAO = R1). Não se gravou nada.

**Robots ilegível (3) → continuam fora, e NÃO são casos da D39** (`ROBOTS-3-RONDA-A.json`, 25/09 ~10:2xZ)

| fonte | leitor da casa | leitura crua | classificação |
|---|---|---|---|
| IT-T5-101 cnr.it | inacessível | TLS recusado: `DH_KEY_TOO_SMALL` (o servidor usa uma chave Diffie-Hellman fraca demais para o nosso cliente) | falha de ligação — NÃO SEI |
| IT-T7-053 veneto.coldiretti.it | inacessível | ligação cortada pelo servidor (WinError 10054) | falha de ligação — NÃO SEI |
| IT-T7-058 unaprol.it | inacessível | ligação cortada pelo servidor (WinError 10054) | falha de ligação — NÃO SEI |

A D39 fala de HTML no robots (`ROBOTS_INVALID_CONTENT`) e de 403 (`ROBOTS_ACCESS_DENIED`); aqui não houve
resposta nenhuma. Ficam fora como NÃO SEI, sem estado inventado. O cnr.it só abriria afrouxando a
segurança TLS do cliente — decisão do dono, não se contorna. (Memória da casa: a Coldiretti já recusava a saída Proton.)

**Duplicadas (5) → pergunta ao bot Luciano** (`PERGUNTA-DUPLICADAS-BOT-LUCIANO.md`): IT-T2-056 e IT-T2-106
(seletores de língua da arpae) vs IT-T2-051; IT-T7-100 vs IT-T7-043 (a prova abriu o mesmo documento);
IT-T8-068 (revista inteira) vs IT-T8-021 (secção); IT-T7-115 vs IT-T7-112 (mesmo padrão genérico da cia.it).
Nada fundido.
