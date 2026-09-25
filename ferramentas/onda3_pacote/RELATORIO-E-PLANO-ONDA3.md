# PACOTE-ONDA3 — as peças da 3.ª onda juntas, o ensaio integrado e o plano de instalação — 25/09/2026

Ramo `onda3-pacote-v1`, a partir da produção `servico-20260923-0923 @ 290e7349`, depois alinhado com a
produção nova **`df0865e6`** (MICRO-V3: `onda_web --fontes/--lote`) e depois **`88ee046f`** (FECHAR-ONDA2:
a corrida que rebenta a meio também escreve a sua linha em runs.ndjson).
**NÃO instalado. NÃO disparado.** Ensaio com rede FECHADA; **0 pedidos de rede** nesta missão.

## Em palavras simples

Juntei cinco peças: a CONTRATO-44 (provas de rota + entrada no coletor), a v3 dela (as duplicadas D49),
a REVISAO-15, a HR-6 e a ORDENS-63 v2 (D52: 62 ordens de agrónomos saem por decisão), e apliquei a D51.1 (a
CONAF página inicial sai como duplicada da CONAF comunicados). Só a ORDENS deu conflito de código, num ponto,
resolvido por ordem do coordenador e guardado por um teste novo (§8). Numa cópia fiel do vivo **com os 16 livros do disco**: a tabela do coletor
passa de **210 para 226 fontes (entram 16)**, as prontas para colher passam de **29 para 41**, a coorte
PROVISÓRIA da 3.ª onda tem **40** fontes, **30 correm**, **120 pedidos, no máximo 5 por domínio**, prova do
teto **PASS**. O pacote **não muda nenhum livro no Git**. O desfazer volta tudo ao vivo, provado.
Falta: **RECEITA-T8** (bancada a trabalhar). **Fora deste pacote, por ordem do coordenador:** a
receitas-182-v1 e o reenfileirar dos reparos dela (a JANELAS-68 mediu que o reparo geral aprova páginas
fixas como notícia, 6 casos; entra só depois de uma trava de notícia datada, na janelas-68-v2).

> ⚠️ **Correção (25/09 ~11:10Z):** a 1.ª versão deste relatório dizia «entram 33» e «as 17 da PONTE não estão
> no coletor da produção». **Estava errado.** O ensaio copiava uma lista FIXA de 14 livros e leu a tabela do
> coletor do Git (193 fontes) em vez da do disco do vivo (210, com as 17 da PONTE, entradas ~07:50 pelo
> supervisor). O script agora lê os ficheiros sujos do vivo na hora e para se o pacote tocar algum.

## 1 · A junção

| ordem | ramo | commit | conflitos |
|---|---|---|---|
| 1 | contrato-44-v1 | 0d56bb95 | nenhum |
| 2 | contrato-44-v3 (contém a v1 e a v2) | 34cb3e61 | nenhum |
| 3 | reparo-fontes-v3 (REVISAO-15) | 3384c57d | nenhum |
| 4 | hr6-v1 | e5825dc0 | nenhum |
| + | D51.1 (commit próprio `1f086968`) | — | — |
| + | produção nova df0865e6 (MICRO-V3) | — | nenhum |
| + | produção nova 88ee046f (FECHAR-ONDA2) | — | nenhum (teste da corrida abortada 1/1 + 7/7) |
| 5 | ordens-63-v2 (D52) | 9260aa2e | **1 conflito de código** em `curadoria/gatilho_discovery.py` — resolvido por ordem (§8) |
| ⏳ | receita-t8-v1 (D48) | 75947e77 | à espera do PRONTO da bancada |

**D51.1:** `curadoria/retirar_duplicadas_d49.py` passa a guardar, por linha, a decisão e o ficheiro da prova.
As 4 da D49 ficam iguais; entra `IT-T7-170 → fica IT-T7-174`, `DECISAO = D51`, reversível, sem apagar.
9 testes (2 novos).

## 2 · O ensaio integrado (`ensaio/`, script `ensaio_onda3.sh`)

Cópia = worktree destacada no **HEAD do vivo (88ee046f)** + os **16 ficheiros sujos do vivo, lidos na hora**
(foto tirada com a 2.ª onda a correr no vivo — só leitura; o desfazer repõe desta foto, não do vivo; sha256 em `ensaio/0-FOTO-DOS-LIVROS.txt`); o pacote
entra por `git merge --no-ff`, como na instalação. Rede fechada, conferida (www.cia.it recusado). O robô não correu.

| passo | antes (vivo de hoje) | depois |
|---|---|---|
| livros que o pacote muda no Git | — | **0** (dos 16) |
| merge | — | rc=0, 0 conflitos, **16 livros iguais** |
| duplicadas D49 + D51 | — | **5 APLICA** (IT-T2-056, IT-T2-106, IT-T7-100, IT-T7-170, IT-T8-068), nenhuma na tabela do coletor; 2.ª passagem 5 JA_APLICADA |
| D52 (depois da D49/D51) | — | **APLICA 62**; 2.ª passagem 62 JA_APLICADA; 0 em comum com a D49/D51; Palermo IT-T7-226 fica ativa |
| provas de rota (0 pedidos) | — | PONTE (59 linhas) + C44 (19) + HR6 (1) |
| tabela do coletor (disco) | **210** fontes · ENTRA=0 FICA=27 | **226** · **ENTRA=16** (as da C44) · FICA=7 |
| portão: READY / elegíveis | 183 / 73 | 182 / **69** (−4 da D49; −1 READY = a T7-174 à espera do canário do robô) |
| plano da coleta: prontas | **29** | **41** (+12, perdidas 0) |
| o que o robô vai medir | — | REVISAO-15: **15** VALIDATE_ROUTE; HR-6: IT-T7-174 |
| coorte 3.ª onda (PROVISÓRIA) | 2.ª onda congelada: 28 | **40** (ISTAT fora, D45) |
| `onda_web --so-plano` | — | **30 de 40 correm** · 120 pedidos · máximo 5 por domínio · PODE_CORRER=false (PROVISÓRIA) |
| prova-teto sobre o plano | — | **PASS** · 120 previstos · 0 domínios acima de 5 |
| testes | — | 118 (9 ficheiros do Curator, com a D52 e os gatilhos) + 4 (hr6) + 17 + 10 + 1 + 6 + 29 + 19 (tests/) + motor 62/62 + teto local 7/7 — **todos OK** |
| desfazer | — | D52 `--reverter` = livro de contratos byte a byte · `reset --keep` rc=0 · 0 ficheiros de código diferentes · HEAD = vivo · 16 livros = foto · prontas 29 |

**Saltam por teto nesta onda (10):** IT-T2-146, IT-T5-080, IT-T5-111, IT-T5-113, IT-T5-167, IT-T5-186,
IT-T5-187, IT-T7-121, IT-T7-123, IT-T7-135; parcial IT-T7-118 (cia.it).

**Fora da coorte (29), por motivo:** 20 por `SEM_RECEITA_WEB` em T8/T9/T12 (**é o que a RECEITA-T8 abre**);
6 sem contrato no coletor (IT-T3-045, IT-T5-101 cnr.it, IT-T7-053, IT-T7-058, IT-T7-115, IT-T7-120 — os casos
já explicados na CONTRATO-44 v2/v3); IT-T12-104 (sem contrato + sem receita); IT-T5-049 Catania
(`ROTA:CAPABILITY_BLOCK`, fica fora); IT-T5-090 ISTAT (D45).

## 3 · O que só o vivo pode dar (rede, pelo robô)

- **IT-T7-174 (HR-6):** a ferramenta põe-na a re-medir; o robô faz ~3 pedidos a conaf.it; se passar, fica
  elegível e o gancho do supervisor dá-lhe entrada no coletor (a prova do coletor já está junta) → **+1 pronta (42)**.
- **REVISAO-15:** 15 re-medidas uma vez. **+3 READY** se o canário ainda passar (IT-T2-157, IT-T7-171,
  IT-T8-064); 12 ficam retidas com o motivo no livro. Essas 3 **não** ficam prontas para colher: não têm
  contrato no coletor.

## 4 · A tabela do coletor é um livro vivo (as duas perguntas do coordenador)

**(1) Como tratar `regras/italy_contracts_onboarded.json` na instalação — escolhi: o pacote NÃO muda o
ficheiro no Git; quem escreve as 16 novas é o onboarding, no disco, como o supervisor já faz.**
Porquê:
- medido, o pacote muda **0** dos 16 livros no Git, por isso o `merge --ff-only` não recusa nem pisa nada;
- a escrita fica na porta que já existe (`onboardar_rotas_provadas.py`, a mesma do supervisor), com «mostrar»
  antes de «aplicar»;
- **não** faço commit do estado vivo antes do merge: seria fotografar no Git um livro que o supervisor volta a
  sujar em minutos, e cada ramo feito antes dessa foto passaria a colidir com ela. O backup com sha256
  (passo 2) faz o papel de «estado antes».

**(2) Devia ser livro (fora do Git)? — Sim, é um livro:** é escrito em tempo de corrida pelo supervisor
(onboarding) e pelas portas de decisão, como os outros 15. Hoje já vive no mesmo regime deles (rastreado e
sujo). O perigo que isto mostrou: **ramos que mudam um livro no Git** (a PONTE-ONBOARD e a CONTRATOS-AJUSTE
mudaram esta tabela no Git) e **leituras do HEAD em vez do disco** (o meu erro). Opções para o bot Luciano:
- **A (recomendo agora):** fica rastreado, com a regra escrita «nenhum ramo muda um livro no Git; a mudança é
  por porta, no vivo» — e a guarda que o ensaio já tem (`livros que o pacote muda no Git: 0`, senão PARA).
- **B (desenho, depois):** tirar do Git (`.gitignore` + semente). Custa: um clone novo (bancadas, nuvem, CI)
  fica sem tabela e o coletor não colhe nada; `regras/italy_contracts.mjs` e os testes leem-na.

A mesma pergunta vale para `curadoria/ROTAS-ELEGIVEIS-V1.json` (também escrita no vivo pela junção de provas).

## 5 · Plano de instalação (executa: o coordenador; um escritor no vivo)

> ⛔ **D61 (dono real): a 3.ª onda está EM ESPERA** até ao conserto de data e local das notícias
> (bancada TEMPO-E-LUGAR). **Nenhum passo abaixo corre sem ordem expressa do coordenador.**

Comandos em Git Bash. Definir primeiro:
```bash
VIVO=/c/Users/London1/orca/workspaces/eame-sintonia/source-curator-service-v1
PACOTE=<SHA entregue como PACOTE-ONDA3 PRONTO>
D=$(date +%Y%m%d-%H%M); CORTE=/c/cutover/onda3-$D; mkdir -p $CORTE
# os livros = os ficheiros sujos do vivo, lidos na hora (hoje 16: os 14 + a tabela do coletor + a prova de rotas)
LIVROS=$(git -C $VIVO --no-optional-locks status --short | grep '^ M' | awk '{print $2}' | tr '\n' ' ')
```

**1 · Parar o robô** (⏱️ começa o tempo parado) — como na INTEGRA, passo 1: `PARAR.flag`, esperar o supervisor
sair (≤ 60 s), fechar o observador; confirmar 0 processos `supervisor|worker|ponte_automatica|observador`.

**2 · Backup com sha256**
```bash
git -C $VIVO rev-parse --short HEAD          # TEM de dar 88ee046f — senão PARAR (juntar a produção nova e refazer o ensaio)
echo $LIVROS | wc -w                         # 16 (se aparecer código sujo: PARAR)
git -C $VIVO fetch origin onda3-pacote-v1
git -C $VIVO diff --name-only HEAD $PACOTE -- $LIVROS | wc -l   # TEM de dar 0: o pacote não toca livros
for f in $LIVROS; do mkdir -p $CORTE/$(dirname $f); cp $VIVO/$f $CORTE/$f; done
( cd $CORTE && sha256sum $LIVROS > SHA256-ANTES.txt )
git -C $VIVO rev-parse HEAD > $CORTE/HEAD-ANTES.txt
```

**3 · Merge** — `git -C $VIVO merge --ff-only $PACOTE` (88ee046f é antepassado: avanço direto).
Nenhum dos 16 livros muda (o git não recusa: não os toca).

**4 · Livros iguais** — `( cd $VIVO && sha256sum $LIVROS ) | diff - $CORTE/SHA256-ANTES.txt && echo LIVROS IGUAIS`
🛑 se mudou: DESFAZER.

**5 · Testes (sem rede)**
```bash
cd $VIVO
py -B -m unittest curadoria.test_retirar_duplicadas_d49 curadoria.test_canario_detalhe curadoria.test_reparar_contrato curadoria.test_revisao_ready curadoria.test_um_so_canario_promove curadoria.test_ready_split   # 89 OK
(cd ferramentas/hr6 && py -B -m unittest test_remedir_hr6)                                     # 4 OK
for t in tests/test_onda_web.py tests/test_onda_web_fontes.py tests/test_teto_dominio.py tests/test_canario_rotas_contrato_certo.py tests/test_onboardar_rotas_provadas.py tests/test_prova_teto_dominio.py; do py -B $t; done   # 17·10·1·6·29·19 OK
node regras/motor_de_rota_test.mjs ; node provas/teto_dominio_local.mjs                          # 62/62 · 7/7
```

**6 · Mapa** — com a LOCK-PESADO: `py system-map/scripts/correr_a_cadeia.py VALIDAR` → `SYSTEM_MAP_CHECK=PASS`.

**7 · Duplicadas D49 + D51, depois a D52 (robô parado; as duas escrevem o livro de contratos)**
```bash
py -B curadoria/retirar_duplicadas_d49.py            # esperado 5 × APLICA
py -B curadoria/retirar_duplicadas_d49.py --aplicar  # «livro de contratos escrito»
py -B curadoria/retirar_duplicadas_d49.py            # esperado 5 × JA_APLICADA
sha256sum curadoria/italy_contracts_curator.json > $CORTE/CONTRATOS-ANTES-D52.txt
py -B curadoria/retirar_por_decisao.py --decisao D52             # esperado {'APLICA': 62}
py -B curadoria/retirar_por_decisao.py --decisao D52 --escrever  # «escrito: …italy_contracts_curator.json»
py -B curadoria/retirar_por_decisao.py --decisao D52             # esperado {'JA_APLICADA': 62}
```
Desfazer só da D52: `py -B curadoria/retirar_por_decisao.py --decisao D52 --reverter --escrever` → conferir
com `$CORTE/CONTRATOS-ANTES-D52.txt` (no ensaio: igual byte a byte).

**8 · HR-6: pôr a IT-T7-174 a re-medir**
```bash
py -B ferramentas/hr6/remedir_hr6.py --fontes=IT-T7-174            # ACCAO=REMEDIR
py -B ferramentas/hr6/remedir_hr6.py --fontes=IT-T7-174 --aplicar  # FEITO=true, 1 tarefa VALIDATE_ROUTE
```

**9 · Provas de rota (0 pedidos)** — válidas: PONTE até **02/10 06:38Z**, C44 até **02/10 ~09:46Z**, HR6 até **02/10 10:42Z**
(juntar a da PONTE outra vez é inofensivo: `juntar` fica com a linha mais nova de cada fonte)
```bash
cd $VIVO && HTTPS_PROXY=http://127.0.0.1:9 HTTP_PROXY=http://127.0.0.1:9 PYTHONUTF8=1 py -B - <<'EOF'
import json, sys; sys.path[:0] = ["medidas", "."]
import canario_rotas_elegiveis as C
v = json.load(open("curadoria/ROTAS-ELEGIVEIS-V1.json", encoding="utf-8"))
for p in ("ferramentas/ponte_onboard/ENSAIO-2-rotas-provadas-3rondas.json",
          "ferramentas/contrato44/ROTAS-PROVADAS-C44.json", "ferramentas/hr6/ROTAS-PROVADAS-HR6.json"):
    v["LINHAS"] = C.juntar(v.get("LINHAS", []), json.load(open(p, encoding="utf-8"))["LINHAS"])
json.dump(v, open("curadoria/ROTAS-ELEGIVEIS-V1.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
EOF
```

**10 · Entrada no coletor (no DISCO — é livro; sem commit)**
```bash
py -B curadoria/onboardar_rotas_provadas.py | tail -1    # esperado ENTRA=16 FICA=7 (a tabela já tem 210)
py -B curadoria/onboardar_rotas_provadas.py --aplicar    # escritas na tabela: 16 → 226 fontes
py -B scripts/micro_coleta/micro_coleta.py plano | grep -E '"PRONTAS"|"BLOQUEADAS"'   # esperado 41 / 28
git -C $VIVO push origin HEAD:servico-20260923-0923     # só o código do pacote (o merge do passo 3)
```
(Também se pode deixar este passo para o gancho do supervisor, que corre a mesma porta ao religar; o
«mostrar» continua a ser a conferência.)

**11 · Religar o robô** (⏱️ acaba o tempo parado) — `rm $VIVO/curadoria/PARAR.flag`; supervisor pelo meio de sempre.
O robô mede, com rede e pelo portão de egresso: as **15 da REVISAO-15** e a **IT-T7-174**.
Conferir depois: `py -B curadoria/collection_gate.py --ids=IT-T7-174 --json` (ELIGIBLE) e o diário do supervisor
com `ONBOARDING` a dar entrada à IT-T7-174 → plano **42** prontas.

**12 · Coorte da 3.ª onda — PROVISÓRIA (sem rede)**
```bash
py -B scripts/micro_coleta/micro_coleta.py plano > $CORTE/PLANO-ONDA3.json
py -B ferramentas/big_collection/coorte_unica.py --plano=$(cygpath -w $CORTE)/PLANO-ONDA3.json \
   --saida=ferramentas/big_collection/COORTE-ONDA3-PROVISORIA.json      # ensaio: 40 (41 com a T7-174)
git -C $VIVO add ferramentas/big_collection/COORTE-ONDA3-PROVISORIA.json && git -C $VIVO commit -m "coorte da 3.a onda PROVISORIA"
py -B ferramentas/big_collection/onda_web.py --so-plano --coorte=ferramentas/big_collection/COORTE-ONDA3-PROVISORIA.json --saida=$(cygpath -w $CORTE)/onda3 > $CORTE/ONDA3-SO-PLANO.json
py -B provas/prova_teto_dominio.py --plano $(cygpath -w $CORTE)/ONDA3-SO-PLANO.json --coorte ferramentas/big_collection/COORTE-ONDA3-PROVISORIA.json
#   ensaio: CORREM 30 de 40 · 120 pedidos · máximo 5 por domínio · PROVA_TETO_DOMINIO_PLANO=PASS
```
Congelar (para correr) só por decisão, depois da 2.ª onda e com a RECEITA-T8 dentro: o mesmo
comando com `--congelar --instalacao=<commit> --demotion=<ref>`, como o passo 11 da INTEGRA.

### DESFAZER (provado na cópia: 0 ficheiros de código diferentes, livros = foto, prontas 29)
```bash
echo desfazer > $VIVO/curadoria/PARAR.flag      # esperar o supervisor sair
cd $VIVO && git reset --keep $(cat $CORTE/HEAD-ANTES.txt)      # o pacote não toca livros: nada recusa
for f in $LIVROS; do cp $CORTE/$f $VIVO/$f; done
( cd $VIVO && sha256sum $LIVROS ) | diff - $CORTE/SHA256-ANTES.txt && echo "IGUAL AO ANTES"
rm $VIVO/curadoria/PARAR.flag
# se o passo 10 JÁ fez push: NÃO forçar o push; a origem fica à frente do vivo e o coordenador decide
# (revert na origem, ou apontar o ramo de produção de volta a 88ee046f com ordem explícita)
```
⚠️ Repor os livros só se o robô esteve parado desde o passo 1. Se já correu (passo 11), NÃO repor os livros
(perdia-se trabalho dele): repor só a tabela do coletor e a prova de rotas e, para a D49/D51, tirar a marca
`ESTADO_CATALOGO` das 5 (reversível por desenho).

## 6 · O que falta para «PRONTO»

1. **RECEITA-T8 (D48):** o ramo existe (75947e77), mas a bancada ainda diz TRABALHANDO; entra quando disser
   PRONTO, e o ensaio repete-se com o mesmo script.

## 8 · ordens-63-v2: o conflito de código e como foi resolvido

`git merge --no-ff origin/ordens-63-v2` → **CONFLICT em `curadoria/gatilho_discovery.py`**, função
`candidatas_a_reparar`, no mesmo ponto: a REVISAO-15 acrescentou «fonte CONTRACTED_CANARY_FAILED com leitura
nova → re-medir uma vez»; a D52 acrescentou «fonte RETIRADA_POR_DECISAO → saltar» antes do mesmo `if`.
1.ª tentativa: parei e desfiz (`git merge --abort`), como manda a missão. Depois veio a ordem explícita do
coordenador («junta o ordens-63-v2») e resolvi assim — **as duas, com a D52 primeiro**:
```python
        c = contratos.get(sid)
        if RPD.retirada(c):          # D52: retirada por decisão não volta a ser trabalho
            continue
        if e == LC.CONTRACTED_CANARY_FAILED and _leitura_nova(sid):   # REVISAO-15
            ...
        elif e == LC.CONTRACTED_CANARY_FAILED:
```
Assim uma fonte retirada nunca é re-medida, nem pela REVISAO-15. Teste novo do encontro das duas
(`test_revisao_ready.test_retirada_por_decisao_nao_re_mede_nem_com_leitura_nova`); o mutante sem a trava
D52 fica vermelho. Gatilho + revisão + D52 + D49: 57 testes OK.
