# S2A-R · RECONCILIAÇÃO SEMÂNTICA — handoff

`claude/security-s2-topology-reconcile-v1`, sobre `8625b1cb` (topologia canónica).
**Não promovido. Não mergeado.**

---

## 0 · O QUE MUDOU A FORMA DA MISSÃO

A missão pedia para portar **um commit** (S2A) sobre a topologia. A primeira
medição mostrou outra coisa:

```
security/ NÃO EXISTE na base da topologia.
```

A linha de segurança inteira — S1-1 a S1-7, e a S2A no topo — nasceu de
`1c99a48b`, anterior às duas missões de topologia. Portar só a S2A daria uma
árvore partida: `ratchet.py` sem ficheiro para receber o merge,
`checar_projeccao` a importar um `projeccao` inexistente, e o SECURITY CHECK sem
workflow que o corra.

**Então o porte é da LINHA, e a S2A é o topo dela.** É a mesma lei da missão —
preservar as duas semânticas — aplicada ao que a árvore realmente tem.

---

## 1 · O DELTA, CLASSIFICADO

```
76 ficheiros tocados pela linha de segurança desde a base comum

  54  SÓ a segurança mexeu        -> porte directo
  12  as duas linhas mexeram      -> merge a TRÊS pontas, ficheiro a ficheiro
  10  gerados                     -> NUNCA viajam; regeneram-se
```

**Nenhum `git merge` com «ours/theirs».** Os 12 partilhados foram fundidos com
`git merge-file` contra a base comum. **Sete** fundiram limpos. **Quatro**
tinham conflito — e os quatro eram *os dois lados a acrescentar no mesmo sítio*,
nunca a contradizer-se:

| ficheiro | o que se guardou |
|---|---|
| `generate_system_map.py` | `CANONICAL_OWNERS` (topologia) **+** `BURACOS` (segurança) |
| `test_system_map.py` | as provas da topologia **+** as provas SMF da frescura |
| `o_forward_conta_se.py` | o comentário de um lado **+** o tuplo `GAPS` legível por AST |
| `system-map.yml` | os 15 censos da topologia **+** os três jobs da cadeia |

---

## 2 · A DECLARAÇÃO NÃO FOI COPIADA

Aplicou-se só a semântica: **seis peças novas** de segurança
(`C-SECURITY-CHECK`, `C-IMPRESSAO-DA-ARVORE`, `C-CENSO-DOS-BURACOS`,
`C-DERIVA-DA-BASE`, `C-MAPA-DEPLOY`, `C-REGRESSAO-NAVEGADOR`) e **cinco peças
partilhadas** que a segurança actualizou — com o território e a família da
topologia a mandar sempre.

**E `C-GESTAO-COLETA` não voltou.** Ela existe na árvore da segurança porque de
lá ninguém a partiu. Aqui foi partida em `C-POLITICA-COLETA` + `C-DIAGNOSTICO`.

```
NUNCA DEIXAR UMA BRANCH ANTIGA ENSINAR AO MAPA
UMA ARQUITETURA QUE JÁ FOI CORRIGIDA.
```

---

## 3 · OS DERIVADOS FORAM REGENERADOS, NÃO TRANSPORTADOS

`adama-relevance.js` e `italy-casa.js` dizem na primeira linha «GERADO por
`superficie/it_casa_dados.py` — não editar à mão». O diff de **15.416 linhas**
do `italy-casa.js` na S2A é **saída**, não autoria: a autoria são as **41
linhas** do `it_casa_dados.py`.

**E isso provou-se sozinho.** Com o derivado velho ainda em árvore, o ratchet
portado reprovou de imediato:

```
RATCHET = FALHA · italia-portale/client/italy-casa.js · marcador LEI
```

porque o ficheiro gerado *antes* da S2A ainda levava o texto da lei. Regenerado
a partir da fonte portada: `RATCHET = PASSA`.

---

## 4 · O ATAQUE QUE PASSOU

O red team repôs o texto integral da lei no payload para ver o ratchet reprovar.
**Ele passou.** `checar_projeccao` só vê campos que aparecem **duas ou mais**
vezes — e `LEGGE` aparece uma vez só.

```
UM PORTÃO QUE NÃO REPROVA O ATAQUE QUE O ORIGINOU NÃO É UM PORTÃO.
```

Nasceu `RELEVANCE_LAW_TEXT_PUBLIC`: lê as frases da lei no dono e procura-as nos
bytes servidos. Repetido o ataque, reprova.

---

## 5 · ENTREGA

```
GIT
  A. BRANCH                     claude/security-s2-topology-reconcile-v1
  B. TOPOLOGY_BASE_HEAD         8625b1cb
  C. SECURITY_S2_SOURCE_HEAD    8bae5ef3  (S2A = 1 commit sobre 0cdcbe03)
  D. FINAL_HEAD                 a37f298e
  E. COMMITS                    2
  F. PUSHED                     SIM · sem force push

PORTE S2A / LINHA DE SEGURANÇA
  G. S2A_FILES_TOTAL            20  (a linha inteira: 76)
  H. PORTED_SEMANTICALLY        66  (54 directos + 12 fundidos a três pontas)
  I. REGENERATED                10  (nenhum gerado viajou)
  J. REJECTED_AS_STALE          C-GESTAO-COLETA · Z-PROVA/Z-REGUAS em F-INTELIGENCIA

MAPA
  K. Z_PROVA_FAMILY             F-GOVERNANCA
  L. Z_REGUAS_FAMILY            F-GOVERNANCA
  M. COLLECTION_INTELLIGENCE_TOTAL   6   (igual à topologia canónica)
  N. COLLECTION_INTELLIGENCE_DATA    0
     COLLECTION_GOVERNANCE          146  (143 + 3 das peças novas)
  O. SYSTEM_MAP_CHECK           PASS
  P. MAP_RULES_CHECK            PASS  (TESTES_SYSTEM_MAP)
     NODES 149 -> 155 · EDGES 567 -> 588 · UNKNOWN 0

SEGURANÇA
  Q. PUBLIC_FILES               87
  R. PUBLIC_BYTES               30.430.652
  S. PUBLIC_FIELDS_TOTAL        1946 -> 1935
  T. UNREAD_INTERNAL_FIELDS      586 ->  585
  U. FULL_RELEVANCE_LAW_TEXT_PUBLIC   NÃO
  V. LEGGE_SHA256_PUBLIC              SIM  (LEGGE_CLAUSULAS 9)
  W. VERDICT_DIFFERENCES              0    (43 casos, idênticos)
     PUBLIC_CORPUS_BYTES        21.442.219 -> 21.437.624

MOTOR
  X.  SCORE_FUNCTIONS_PUBLIC            1  (ordenador de busca, não o motor)
  Y.  WEIGHTS_PUBLIC                    0
  Z.  THRESHOLDS_PUBLIC                 0
  AA. CLASSIFICATION_ARITHMETIC_PUBLIC  0

RATCHET
  AB. NEW_INTERNAL_FIELD_RATCHET  portado, e morde
  AC. LAW_TEXT_RATCHET            NOVO — nasceu do ataque que passou
  AD. MUTATIONS_PASS              7 de 7

BROWSER
  AE. PAGES_TESTED   5  (/ · /accesso · /casa · /portale · /system-map/)
  AF. JS_ERRORS      4 pré-existentes, nenhum bloqueia render:
                     1 placeholder SVG em /portale · 2 404 de artefactos de build
                     (deployment.generated.json, favicon) · 1 recusa de iframe
                     que é o cabeçalho a funcionar
  AG. REGRESSIONS    0 · «SEM REGRESSAO — 5 páginas carregam e renderizam»

OUTRAS LINHAS
  AH. COLLECTION_FUNCTIONAL_TOUCHED   NÃO  (coleta/ admissao/ orquestrador/
                                            pedido/ candidatas/ fontes/ regras/
                                            leis/ medidas/ = 0 ficheiros)
  AI. SCRAP_TOUCHED                   NÃO  (0)
  AJ. STORIES_TOUCHED                 NÃO  (0)
  AK. INTELLIGENCE_ENGINE_TOUCHED     NÃO  (motor/ pacote/ = 0 ficheiros)

TESTES — as duas bases, porque uma só esconderia metade
  topologia 8625b1cb    63 PASS ·  6 FAIL
  segurança 8bae5ef3    60 PASS · 12 FAIL
  reconciliada          63 PASS ·  9 FAIL
  NEW_FAILURES          0   (os 9 são subconjunto dos 12 da segurança)
  CORRIGIDAS PELA JUNÇÃO 3  test_coleta_externa · test_migrations · test_portao
```

---

## 6 · O RED TEAM

| ataque | esperado | medido |
|---|---|---|
| A · `Z-PROVA` volta para `F-INTELIGENCIA` | reprova | **7 provas reprovam** |
| B · texto integral da lei volta ao payload | reprova | passou → **portão novo** → reprova |
| C · campo interno novo, não lido | reprova | `NEW_INTERNAL_FIELD_EXPOSED_TO_CLIENT` |
| D · identificador/caso novo legítimo | **não** reprova | `RATCHET = PASSA` |
| E · campo novo realmente lido pela UI | **não** reprova | `RATCHET = PASSA` |
| F · aresta `DATA` Collection→Intelligence | reprova | `T5b` + a prova do rehome |
| §44 · mexer numa fonte depois de regenerar | vermelho, depois verde | `P1_SEM_DRIFT` FAIL → regenerar → PASS |

---

## 7 · O QUE FICA ABERTO, E DE QUEM É

**Três falhas herdadas da linha de segurança**, que falham identicamente em
`8bae5ef3` e **não** foram mascaradas:

| módulo | o que diz | de quem é |
|---|---|---|
| `test_trava_da_inteligencia` | dois artefactos congelados mudaram de sha: `adama-relevance.js` e `italy-casa.js` | **decisão humana** — a S2A mudou-os para RETIRAR exposição, o oposto de «a inteligência avançou». Actualizar `docs/operacao/TRAVA-DA-INTELIGENCIA.json` é de quem é dono da trava, não de quem reconcilia |
| `test_fundacao_da_coleta` | os mesmos dois ficheiros são portal fora de `/system-map/` | mesma causa, mesma decisão |
| `test_metricas` | os documentos publicam `TEST_COUNT_CURRENT = 1.651`; a suíte tem 1.706 | **dívida de dado** — o número cresce sempre que alguém acrescenta testes, e as duas linhas acrescentaram |

**As seis da topologia** continuam como estavam, e estão documentadas em
`docs/operacao/TOPOLOGIA-DA-COLETA.md`.

---

## 8 · O QUE NÃO SE FEZ, DE PROPÓSITO

- **Não** se tornou o repositório privado (§29). Fica só a conclusão medida na
  S2A: a integração Git da Vercel e as GitHub Actions sobrevivem; a frescura do
  System Map passaria a precisar de leitura autenticada.
- **Não** se activou Preview Protection (§30).
- **Não** se criou backend nem serverless para provar que o motor não está no
  browser (§10) — ele já não estava.
- **Não** se promoveu nem se mergeou (§58).
