# HR-6 + CATANIA — relatório e plano para o vivo

Ramo `hr6-v1`, a partir de `integra-onda2-v1` @ `d235c32a` (o mesmo HEAD do vivo em 25/09 ~10:10Z).
Cópia fiel em `C:/hr6` (git archive do ramo + os 14 livros sujos do vivo, sha em `SHA-SUJOS-VIVO.txt`),
rede FECHADA por omissão (proxies 127.0.0.1:9). Rede só nas rondas, com o portão de consenso
`superficie/rede.py --portao-de-egresso IT` = PASS antes de CADA ronda, 1 fonte por domínio por ronda,
robots lido, ≤ 5 pedidos por domínio por corrida (D38). **NÃO instalado.**

## 1 · Resposta curta

| | antes | depois (na cópia) |
|---|---|---|
| elegíveis no portão (`COLLECTION_ELIGIBLE`) | 73 | **75** (+IT-T7-170, +IT-T7-174) |
| READY com HUMAN_REVIEW_REQUIRED | 9 (6 current + 3 legacy) | 7 |
| prontas no plano da coleta (`micro_coleta plano`) | 18 | **19** (+IT-T7-174) · perdidas: 0 |
| IT-T5-049 (Catania) | BLOQUEADA `ROTA:CAPABILITY_BLOCK` | igual — re-medida hoje, continua |

Das 6 HR, **2 saem da suspeita pelo caminho canónico** (as duas CONAF). Destas, **1 entra no coletor**
(IT-T7-174); a IT-T7-170 é **duplicada** dela (mesmo site, mesmo padrão, o canário do coletor abriu a
mesma notícia nas duas) — decisão de identidade, como a D49. As outras 4 ficam como estão, com motivo.

## 2 · Porque re-medir sozinho não chegava

O canário do Curator (`canario.canario_html`) abria sempre `alvos[0]`, o **primeiro por ordem
alfabética**. Re-medir abria o mesmo endereço (ronda B1/B2: os 6 itens iguais aos da promoção).
Não há "item mais fundo" sem mudar QUAL item o canário tenta.

**Mudança de código (a única):** `canario.escolher_alvo(alvos, index_url)` — o canário TENTA
primeiro o 1.º alvo cujo endereço não tem cara de secção pela regra do portão
(`collection_gate.revisao_humana_do_url`, a mesma função, sem cópia). **Se esse item não passar,
abre `alvos[0]` como antes** (`ALVO_FUNDO_TENTADO` fica na evidência). Medido na ronda C1 sem a volta:
o item fundo da ARPAS e da Úmbria era PDF, o de Pádua navegação — 3 READY cairiam. Com a volta
(ronda C2) as 3 ficam exatamente como hoje. Custo: no máximo +1 pedido (≤ 4 por fonte).
Quem julga continua a ser o gate de detalhe + a régua dos 4 passos. `reparar_contrato` NÃO mudou.

Testes: 5 novos em `curadoria/test_canario_detalhe.py`; 122 testes dos 10 ficheiros que usam o canário
ou o worker passam; mutação (escolha desligada → 3 vermelhos; volta desligada → 1 vermelho).
`ferramentas/hr6/test_remedir_hr6.py`: 4 testes.

## 3 · As 6, uma a uma

| fonte | item da promoção | reparo R1 (ronda A) | canário novo (C1/C2) | fica |
|---|---|---|---|---|
| IT-T7-174 CONAF comunicati | `news/assemblea-agronomi-udine/` (notícia real, 3 palavras) | RECUSA (não correu: 1 por domínio; a T7-170 correu) | abre `news/benessere-animale-decreto-ue/` CONTENT, 1341 car. | **ELEGÍVEL + ENTRA no coletor** |
| IT-T7-170 CONAF home | `news/conaf-crea-accordo/` (notícia real) | RECUSA ITEM_NAO_E_MATERIA (famílias de menu) | abre `news/decreto-pa-periti-catastrofali/` CONTENT, 1236 car. | **ELEGÍVEL**, fora do coletor: DUPLICADA de T7-174 |
| IT-T2-143 ARPAS Sardegna | `…/2000/01.A/riepilogo.asp` (relatório real, de 2000) | RECUSA SEM_FAMILIA_DE_ITENS | todos os 348 itens acabam em `riepilogo.asp`; o fundo era PDF → volta ao 1.º | HR (a regra olha só o último pedaço do endereço; decisão do dono) |
| IT-T3-053 Umbria fitosanitari | `agricoltura/servizio-fitosanitario-regionale` (secção) | RECUSA ITEM_NAO_E_MATERIA (menu) | o fundo é o boletim PDF «NOCCIOLO n.10 del 17/07/2026» → volta | HR — o conteúdo bom é PDF; precisa de receita PDF, não de HTML |
| IT-T5-064 DAFNAE Padova | `ricerca/assegni-di-ricerca` (secção) | RECUSA (item 404) | fundo = navegação → volta | HR, com razão |
| IT-T8-050 Noi Siamo Agricoltura | `categorie/blog/curiosita-dalla-natura/` (categoria) | RECUSA SEM_FAMILIA_DE_ITENS | os 3 alvos têm cara de secção → igual | HR, com razão |

Na cópia, as duas CONAF foram re-medidas pelo **worker** (`remedir_hr6.py --aplicar` → VALIDATE_ROUTE →
CANARY → régua DETAIL/v1): READY com evidência nova, portão ELIGIBLE. Ninguém marcou "visto por pessoa".

## 4 · IT-T5-049 (Catania)

- No Curator já é READY DETAIL/v1 e **ELEGÍVEL**; já está na tabela do coletor.
- O bloqueio vem do filtro M3 do plano (`origin/rotas-elegiveis-v1`, medido a 22/09): CAPABILITY_BLOCK.
- Re-medida hoje pelo canário do coletor (`canario_rotas_elegiveis.py --fontes=IT-T5-049`): **CAPABILITY_BLOCK
  outra vez** — abriu «colloquio-di-ammissione…LM-69» (504 car. em parágrafos, MIXED) e «avvisi-lezioni»
  (1214, MIXED).
- Os 4 itens na Sala são avisos a alunos: `avvisi-esami-e-prove-itinere`, `avvisi-lezioni`,
  `kit-di-sopravvivenza…ansia`, `welcome-day-1`. **Não é matéria agronómica.** Fica fora; nada a instalar.

## 5 · Plano para o vivo (um escritor; DEPOIS da INTEGRA e das instalações já na fila; NÃO instalado)

A prova do coletor da IT-T7-174 vale 7 dias: **até 02/10 10:42Z** (`ROTAS-PROVADAS-HR6.json`,
`PROVADO_EM 2026-09-25T10:42:25Z`). O contrato não muda (o canário não o toca), logo o
`CONTRATO_SHA256` da prova continua a bater.

```bash
cd C:/Users/London1/orca/workspaces/eame-sintonia/source-curator-service-v1
# 0. bot quieto
touch curadoria/PARAR.flag                     # esperar o supervisor sair; 0 worker
# 1. foto e copia de seguranca
B=C:/cutover/hr6-$(date -u +%Y%m%dT%H%MZ); mkdir -p $B
git rev-parse HEAD > $B/head-antes.txt; git status --short > $B/status.txt; git diff > $B/diff.txt
for f in curadoria/LIFECYCLE-LEDGER-V1.json curadoria/LIFECYCLE-QUEUE-V1.json curadoria/LIFECYCLE-EVIDENCE-V1.json \
         regras/italy_contracts_onboarded.json curadoria/ROTAS-ELEGIVEIS-V1.json; do cp $f $B/; done
sha256sum curadoria/LIFECYCLE-*.json regras/italy_contracts_onboarded.json curadoria/ROTAS-ELEGIVEIS-V1.json > $B/sha-antes.txt
# 2. codigo (canario.escolher_alvo + ferramentas/hr6)
git fetch origin hr6-v1 && git merge --no-ff origin/hr6-v1 -m "instalar HR-6: canario tenta o item mais fundo"
# 3. re-medir SO a IT-T7-174 (mostrar, conferir ACCAO=REMEDIR, aplicar)
py -B ferramentas/hr6/remedir_hr6.py --fontes=IT-T7-174
py -B ferramentas/hr6/remedir_hr6.py --fontes=IT-T7-174 --aplicar
# 4. o bot faz VALIDATE_ROUTE -> CANARY (portao IT PASS antes; ~3 pedidos a conaf.it)
rm curadoria/PARAR.flag                        # relancar; esperar a T7-174 voltar a READY
py -B curadoria/collection_gate.py --ids=IT-T7-174 --json   # esperado COLLECTION_ELIGIBLE_IDS=["IT-T7-174"]
touch curadoria/PARAR.flag
# 5. juntar a prova do coletor e onboardar
HTTPS_PROXY=http://127.0.0.1:9 HTTP_PROXY=http://127.0.0.1:9 PYTHONUTF8=1 py -B - <<'EOF'
import json, sys; sys.path.insert(0, "medidas"); import canario_rotas_elegiveis as C
v = json.load(open("curadoria/ROTAS-ELEGIVEIS-V1.json", encoding="utf-8"))
v["LINHAS"] = C.juntar(v.get("LINHAS", []), json.load(open("ferramentas/hr6/ROTAS-PROVADAS-HR6.json", encoding="utf-8"))["LINHAS"])
json.dump(v, open("curadoria/ROTAS-ELEGIVEIS-V1.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
EOF
py -B curadoria/onboardar_rotas_provadas.py | grep IT-T7-174      # esperado: ENTRA  IT-T7-174
py -B curadoria/onboardar_rotas_provadas.py --aplicar
py -B scripts/micro_coleta/micro_coleta.py plano | grep -E '"PRONTAS"|IT-T7-174'   # esperado +1 e ESTADO PRONTA
# 6. commit da tabela e das provas; relancar
git add regras/italy_contracts_onboarded.json curadoria/ROTAS-ELEGIVEIS-V1.json
git commit -m "HR-6: IT-T7-174 (CONAF comunicati) no coletor — prova de rota <= 7 dias"
rm curadoria/PARAR.flag
```

Se a INTEGRA estiver instalada com o gancho do supervisor (`onboardar_se_mudou`), o passo 5 pode ficar
para o supervisor; conferir `ENTRA` antes de religar. Se a CONAF mudar a página e o canário do vivo abrir
outro item, o resultado do passo 4 manda — conferir o `ITEM_ABERTO` da evidência nova.

**DESFAZER:** `touch curadoria/PARAR.flag` →
- código: `git reset --keep $(cat $B/head-antes.txt)`;
- livros: `cp $B/LIFECYCLE-*.json curadoria/ ; cp $B/italy_contracts_onboarded.json regras/ ; cp $B/ROTAS-ELEGIVEIS-V1.json curadoria/`
  (só com o bot parado desde o passo 0 — senão perde-se trabalho do bot: nesse caso NÃO repor o livro,
  basta tirar a T7-174 da tabela do coletor repondo só `italy_contracts_onboarded.json`; o READY dela é
  legítimo e append-only);
- conferir com `$B/sha-antes.txt` → relançar.

## 6 · Decisões que ficam para o dono

1. **IT-T7-170 × IT-T7-174** (CONAF home × CONAF comunicati): as duas chegam às mesmas notícias. Proposta:
   fica a T7-174 (29 itens na lista contra 3), a T7-170 sai por `retirar_duplicadas_d49.py` (acrescentar à
   tabela D49). Não re-medir a T7-170 no vivo antes da decisão.
2. **IT-T2-143 ARPAS**: o relatório mensal é item verdadeiro, mas a regra só olha o último pedaço do endereço
   (`riepilogo.asp`). Mudar a regra do portão é lei, não é deste ramo.
3. **IT-T3-053 Úmbria**: o conteúdo real são boletins em PDF; precisa de contrato PDF, não de HTML.

## 7 · Rede usada (todas com portão IT PASS antes)

| ronda | o quê | domínios (pedidos) |
|---|---|---|
| A1 | `reparar_contrato.inferir` (não escreve) | sar(1), umbria(2), dafnae(2), conaf(4), noisiamo(2) + robots |
| B1 | canário do Curator, código de hoje | sar, umbria, dafnae, noisiamo, conaf(T7-174): robots+2 cada |
| B2 | canário T7-170; canário do coletor T5-049 | conaf(3), di3a.unict(4) |
| C1 | canário novo SEM volta | 5 domínios, robots+2 cada |
| C2 | canário novo COM volta | conaf(3), sar(4), umbria(4), dafnae(4) |
| W1/W2 | worker T7-174, depois T7-170 (corridas separadas) | conaf ~3 cada |
| K1/K2 | canário do coletor T7-174, depois T7-170 | conaf 4 cada |

Nenhuma corrida passou 5 pedidos por domínio. A conaf.it levou ~30 pedidos no dia, em 9 corridas.

## 8 · Ficheiros (sha256 em `SHA256.txt`)

`RONDA-A1/B1/B2/C1/C2.json` · `CANARIO-COLETOR-HR6-TODAS.json` · `ROTAS-PROVADAS-HR6.json` (só T7-174) ·
`ONBOARD-MOSTRAR.txt` / `ONBOARD-APLICAR.txt` (cópia) · `PLANO-ANTES.txt` / `PLANO-DEPOIS.txt` ·
`SHA-SUJOS-VIVO.txt` · scripts das rondas (`ronda_*.py`, `hr6-copia.sh`, `hr6-plano.sh`).

Mapa do sistema: NÃO regerado neste ramo — `LOCK-PRIORIDADE.txt` (INTEGRA-ONDA2) presente. Fica pendente
com os ramos contrato-44-v1/v2/v3 e reparo-fontes-v3.
