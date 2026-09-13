# SCRAP-FLOW-01 — UM FLUXO OPERACIONAL REAL PELO ORQUESTRADOR CANÔNICO

`SCRAP_FLOW_01 = PASS`

> A SR-02 provou que nenhum módulo compra sem autorização, e deixou escrito o
> que isso **não** provava.
>
> ```
> MODULE CAN'T SPEND != FLOW IS CANONICAL.
> ```
>
> Agora um caminho operacional real atravessa a Collection inteira, do pedido à
> admissão, sem tocar rede e sem gastar nada.

---

## 1 · O QUE NÃO EXISTIA ERA A ARESTA

Medido antes desta missão:

```
orquestrador/orquestrador.py    dono único da orquestração          EXISTE
coleta/scrap_executor.py        executor canônico do SCRAP          EXISTE
ARESTA ENTRE OS DOIS                                                NÃO EXISTE
```

O disparador ia direto a `coleta/social_scrap.py`, que corria o `COLLECT` e
parava ali. `coleta/ingresso.py` existia, a admissão existia, e o que a corrida
colhia nunca chegava a nenhuma das duas.

```
MODULE EXISTS != EDGE EXISTS != FLOW EXISTS.
```

---

## 2 · AS DUAS LINHAGENS, MEDIDAS E NÃO JUNTADAS

```
FIRST_PAID_HEAD   3c34a4fc4f6f920c526fc0188b80e381366f2bd8
MAGICAL_HEAD      b64259a940c41e9a4b7dcf8f492788ef9a175786
SAME_HEAD         NO
MERGE_BASE        00a6aa35b4a8770a3d48c143e6aa0a47354102a1
COMMITS_ONLY_FIRST_PAID   153
COMMITS_ONLY_MAGICAL       68
FULL_SR01_MERGE   NO
```

As duas são **complementares**, não duplicadas: esta linha tem o teto de rede,
o C10.8B-R e a guarda de gasto; a outra tem a relevância da fonte e o
`COL-LAW-505`. E as duas têm um `leis/autorizacao_de_gasto.py` — escrito duas
vezes, com bytes diferentes (20.572 e 18.236), por duas frentes que não se
viram. Está medido e **não** foi resolvido aqui.

Portou-se **um** ficheiro, byte a byte: `leis/retorno_da_coleta.py`.

```
sha portado = sha na origem = 4453b738a918b0677dfff5b00d3068a90ad4b2ef
```

Duas cópias da mesma lei são duas leis, e a segunda aprende a responder o que a
primeira recusa.

---

## 3 · O CENSO, REMEDIDO

Não se herdou o «quatro».

```
WORKFLOWS_COM_ALVO_PY   14
WORKFLOWS_CANONICAL      1   comunicacao-publica.yml
WORKFLOWS_DIRECT (pago)  5   apify-sensores · banco-descartavel ·
                             scrap-evidencia · scrap-social · sintonia-scrap
```

Dos cinco, dois não são coleta de produção: `banco-descartavel` corre provas e
`scrap-evidencia` é o diagnóstico da C10.8B-R, sem provider e sem segredo.

---

## 4 · O CAMINHO ESCOLHIDO, E PORQUÊ

```
SELECTED_ENTRYPOINT   .github/workflows/sintonia-scrap.yml · fase `janela`
CURRENT_CHAIN (antes) workflow → social_scrap.py coletar → COLLECT → ✗
WHY_THIS_ONE          é a fase que o próprio workflow rotula «ENTRADA
                      CANÔNICA» e que, apesar disso, nunca chegava à
                      Collection. É gratuita, e o raio de alcance é uma fase.
```

Depois:

```
workflow → COLLECTION_REQUEST → orquestrador → scrap_colheita (subprocesso)
  → COLLECT → roteador → adaptador → provider → RAW
  → envelope COL-LAW-505 → ingresso → admissão
```

---

## 5 · MODULE / EDGE / FLOW

| aresta | módulo | declarada | observada | fluxo provado |
|---|---|---|---|---|
| ENTRYPOINT → REQUEST | sim | sim | sim | sim |
| REQUEST → ORCHESTRATOR | sim | sim | sim | sim |
| ORCHESTRATOR → SCRAP_EXECUTOR | sim | **não existia** | sim | sim |
| SCRAP_EXECUTOR → ROUTER | sim | sim | sim | sim |
| ROUTER → ADAPTER | sim | sim | sim | sim |
| ADAPTER → PROVIDER | sim | sim | sim (falso) | sim |
| OUTPUT → RAW | sim | sim | sim | sim |
| EXECUTOR RETURN → INGRESSO | sim | **adivinhada** | sim | sim |
| INGRESSO → ADMISSION | sim | sim | **item errado** | sim |

As três linhas a negrito são o que esta missão consertou.

---

## 6 · DOIS ACHADOS QUE NÃO ESTAVAM NO GUIÃO

### O SCRAP não conhece `SOURCE_ID`

O envelope canônico tem `PLATFORM`, `SOURCE_ACCOUNT`, `NATIVE_ID` e `URL` —
quatro campos verdadeiros, e nenhum é uma fonte provada.

```
URL NÃO É SOURCE_ID. HANDLE NÃO É SOURCE_ID. PLATAFORMA NÃO É FONTE.
A IDENTIDADE DESCE COM O PEDIDO, E NUNCA SOBE DA OBSERVAÇÃO.
```

Sem `fonte` no pedido, o adapter declara **zero colheita e escreve porquê**.
É a resposta certa, não uma falha.

### O estágio não atravessava o ingresso

`pela_entrada(itens)` e `pela_porta(itens)` recebiam **a mesma lista**. A
observação era julgada sem levar nada do que a porta acabara de provar.

```
O ITEM QUE SAI DO INGRESSO NÃO É O ITEM QUE ENTROU.
```

E o defeito era invisível: as duas listas têm o mesmo tamanho e o mesmo aspecto.

```
UMA TROCA QUE NÃO MUDA NENHUM NÚMERO NÃO SE CONSEGUE VIGIAR.
```

O conserto incluiu **criar o número**: `COM_CARIMBO_DA_PORTA`.

---

## 7 · A HEURÍSTICA, E POR QUE ELA NÃO MORREU TODA

`a_colheita` adivinhava: «uma lista, ou o primeiro campo do ficheiro que seja
lista de fichas». Medido nesta árvore, ela emite **281 itens** — e quase todos
são `MANIFEST`, `CATALOG`, `PLAN` ou `RUN_RECEIPT`.

Aplicar o contrato inteiro de uma vez calava quatro executores que entregam
colheita real. Uma missão que migra **um** caminho não cala cinco.

```
UMA DÍVIDA MEDIDA É UMA DÍVIDA. UMA DÍVIDA CALADA É UM BUG.
```

Para quem declara envelope, a espécie manda. Para quem não declara, a
adivinhação continua — contada no recibo, com `RETORNO_ADIVINHADO` e
`RETORNO_DECLARADO` a dizer sempre qual das duas foi.

---

## 8 · MEDIDO

```
FALSE_HARVEST no caminho migrado        0
RETURN CONTRACT                         COLHEITA · MANIFEST · CATALOG ·
                                        RUN_RECEIPT · PLAN · UNKNOWN
ENTRAM_NO_INGRESSO                      só COLHEITA
RUN_ID_BORN_AT                          orquestrador (o adapter recusa cunhar)
SOURCE_ID_PRESERVATION                  vem do pedido; sem ele, zero colheita
FABRICATED_DOCUMENT_ID                  NO
RAW_OBSERVATION_ID                      raw_asset.id — não escrito aqui
PARALLEL_RUN_MODEL                      NO
PARALLEL_RAW_MODEL                      NO
THEMATIC_CLASSIFICATION_IN_SCRAPER      NO

SELECTED_ENTRYPOINT_DIRECT_BYPASS       NO
OTHER_BYPASSES_MAY_REMAIN               YES

RED_TEAM 31 · MUTANTS 18 · SURVIVORS 0
BASE 2.673 testes · 20 falhas   →   FINAL 2.704 · 18 falhas
NEW_FAILURES 0

REAL_NETWORK 0 · META_REQUESTS 0 · APIFY_RUNS 0 · PAID_REAL_RUNS 0 · COST_USD 0
```

---

## 9 · O QUE NÃO MUDOU

A guarda de gasto, o teto financeiro, o teto de rede, a política da rota, o
`maxTotalChargeUsd`, o POST único e a transferência de evidência da C10.8B-R
continuam intactos e continuam a vir **antes** do provider. A rota
`apify:transcricao` continua `PARTIAL`. `coleta/social_scrap.py` continua a
existir: ele deixou de ser o caminho da fase migrada, e não deixou de ser CLI.

```
BIBLE_CHANGE_STILL_REQUIRED = YES
BIBLE_CHANGED_IN_THIS_MISSION = NO
```

---

## 10 · RISCO RESTANTE

Quatro workflows continuam a correr scripts diretos, e quatro executores
continuam a entregar por adivinhação declarada. Nenhum deles foi tocado.

```
SPEND ENFORCEMENT resolvido != CANONICAL ORCHESTRATION resolvida.
MODULE CAN'T SPEND != FLOW IS CANONICAL — e agora UM fluxo é canônico,
o que é diferente de o sistema o ser.
```

`READY_TO_FANOUT_REMAINING_BYPASSES = YES` — o padrão é reutilizável: um
adapter fino por frente, `envelope_em` na receita, e a fonte a descer com o
pedido. O fan-out **não** foi executado.
