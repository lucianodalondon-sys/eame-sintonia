# CENSO ATUAL DA INTELLIGENCE — a população vem do mapa, a prova vem da árvore

```
MISSAO       C-INT-CENSUS-01
MEDIDO_EM    2026-09-13
INSTRUMENTO  provas/censo_da_inteligencia.py
```

> **EVIDÊNCIA DE AUDITORIA.** Este documento não é arquitetura, não é contrato,
> e não governa nada. Ele descreve o que foi medido num commit.

---

## ⚠️ ANTES DA TABELA: NÃO EXISTE «O» SYSTEM MAP

A missão pergunta o que o System Map atual coloca dentro de Intelligence. Medido,
**três linhas carregam três mapas diferentes**, e a resposta muda 2,5× conforme a
linha que se abrir:

| linha | último commit em `system-map/` | peças | `F-INTELIGENCIA` |
|---|---|---|---|
| `claude/raw-observation-identity-3jbwco` | 2026-09-13 21:42 | 181 | **12** |
| `claude/funny-hypatia-y7ho5s` | 2026-09-13 21:29 | 139 | 30 |
| `origin/main` | 2026-09-07 17:56 | 97 | 29 |

As duas primeiras divergiram a **2026-09-07** e são paralelas: 452 commits de um
lado, 19 do outro, nenhuma contém a outra.

```
UM NUMERO DE PECAS SEM A LINHA EM QUE FOI MEDIDO NAO E UM NUMERO.
```

**Nenhuma delas diz 58.** O `58` do enunciado não corresponde a nenhum mapa atual.

### Qual foi escolhida, e por quê

`claude/raw-observation-identity-3jbwco @ 84186dfa` — a mais recente **e** a linha
funcional. Por isso:

```
INTELLIGENCE_MAP_COUNT = 12
CENSUSED               = 12/12
```

### E a queda de 29 para 12 não é perda: é reclassificação

O mapa atribui família assim: `componente.territory → territory.family`.

| | territórios de `F-INTELIGENCIA` |
|---|---|
| `main` e a minha linha | `Z-MOTOR` · `Z-LINEAGE` · `Z-REGUAS` · `Z-PROVA` |
| linha funcional | `Z-MOTOR` · `Z-LINEAGE` |

A funcional criou a família `F-GOVERNANCA` e mudou `Z-REGUAS` e `Z-PROVA` para lá
— onde hoje vivem **73** peças (censos, contratos, réguas, workflows). Nenhuma peça
foi apagada. **Elas deixaram de se chamar Intelligence.**

### O mapa commitado estava desatualizado

`validate_system_map.py` reprovava no HEAD funcional: um documento novo entrara sem
o mapa ser regerado. Regerado pela cadeia canónica, `SYSTEM_MAP_CHECK=PASS`, e a
contagem de peças não mudou (181). **O censo corre sobre o mapa regerado.**

---

## A TABELA — 12 de 12

`E` = estático · `R` = runtime · `—` = não medido

| # | peça | conceito | tipo | ficheiros | inbound prov. | outbound prov. | chamador | runtime | teste | estado | duplicidade | colisão | continua? |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `C-CADEIA-V21` | ordem da cadeia | chain | 2 | 4 | 13 | 7 (E) | **recusa-se** (R) | sim | `PARTIAL` | não | **SIM** | sim, dividida |
| 2 | `C-V2-LEGADO` | motor V2 antigo | engine | 7 | 0 | 0 | **0** | não corre | não | `ORPHAN_LEGACY` | legado ainda referido | não | não |
| 3 | `C-V21-COMERCIAL` | leitura comercial | engine | 9 | — | — | 5 (E) | — | sim | `CONNECTED_STATIC` | não | não | sim |
| 4 | `C-V21-CONTRATO` | contrato do pacote | contract | 3 | — | — | 6 (E) | parcial (R) | sim | `CONNECTED_STATIC` | não | não | sim |
| 5 | `C-V21-CRUZAMENTO` | crossing/convergência | engine | 4 | — | — | 2 (E) | — | não | `CONNECTED_STATIC` | não | não | sim |
| 6 | `C-V21-FONTES` | religação de fontes | engine | 3 | — | — | 3 (E) | — | não | `CONNECTED_STATIC` | não | não | sim |
| 7 | `C-V21-INGEST` | ingestão | engine | 7 | — | — | 13 (E) | — | sim | **`PARTIAL` + caminho direto** | não | não | sim, com conserto |
| 8 | `C-V21-OPORTUNIDADE` | opportunity | engine | 3 | — | — | 5 (E) | — | sim | `CONNECTED_STATIC` | não | **SIM** | sim |
| 9 | `lineage_consumer` | esta linha consome | branch | **0** | — | — | 0 | N/A | não | **`ASSERCAO_SEM_FICHEIRO`** | não | não | sim, como facto |
| 10 | `lineage_generator` | gerador canónico | branch | 1 | — | — | 3 (E) | **PASS** (R) | sim | `PROVEN_OPERATIONAL` | possível | **SIM** | sim |
| 11 | `lineage_package` | pacote esperado | artefato | 1 | — | — | 3 (E) | **PASS** (R) | sim | possível | **SIM** | sim |
| 12 | `lineage_stale` | safras vencidas | artefato | 1 | — | — | 3 (E) | **PASS** (R) | sim | possível | **SIM** | sim |

---

## OS SEIS ACHADOS QUE IMPORTAM

### 1 · DOIS DOCUMENTOS NOMEIAM GERADORES CANÓNICOS DIFERENTES

```
motor/v21_cadeia.sh:35,47
  «O gerador canonico e claude/opportunity-commercial-priority-v1 @ 55c2674»

italia-portale/audit/CANONICAL-PACKAGE-CONTRACT.json
  CANONICAL_GENERATOR = claude/acervo-to-package-intelligence-v1 @ 51010733
```

E o contrato lista a safra de `55c2674` (`V21-69bf448ac934a6d9`) como **VELHA**.

```
A CADEIA MANDA REGENERAR NUMA LINHAGEM
CUJA SAFRA O CONTRATO CLASSIFICA COMO VENCIDA.
```

`COLLISION = YES` no conceito **gerador canónico**. Quem seguisse a cadeia
produziria um pacote que o próprio portão recusa.

### 2 · A CADEIA DA INTELLIGENCE RECUSA-SE A CORRER, E ISSO É O CERTO

`motor/v21_cadeia.sh` sai com `exit 2` a menos que se passe
`SINTONIA_CADEIA_HISTORICA=eu-sei-que-esta-atrasada`. Ele diz de si próprio:

> Esta branch é CONSUMIDORA da inteligência, não geradora.

**Esta é a única prova runtime positiva do motor nesta árvore: a prova de que ele
se recusa.** Fail-closed, medido.

### 3 · A MESMA PEÇA CARREGA DUAS COISAS QUE NÃO SE PARECEM

`C-CADEIA-V21` declara dois ficheiros:

| ficheiro | o que faz de verdade |
|---|---|
| `motor/v21_cadeia.sh` | a cadeia de 16 passos do pacote — Intelligence |
| `motor/cadeia_canonica.sh` | aplica **migrations e importações de banco** |

O segundo não é Intelligence nenhuma, e é o único dos dois que workflows correm.
A descrição da peça no mapa fala apenas do primeiro.

### 4 · UM CAMINHO DIRETO ATÉ UM COLETOR — QUE NINGUÉM ANDA

```
motor/normalize_agro.py:29   from eppo_gd import names as eppo_names
coleta/eppo_gd.py:28         https://gd.eppo.int/taxon/{code}   ← HTTP ao vivo
```

`SEVERITY = ARCHITECTURAL`. É `INTELLIGENCE → COLETOR DIRETO`, sem passar por
`COLLECTION → SALA DE ESPERA → INTELLIGENCE`.

⚠️ **E aqui a medição corrigiu-me.** A primeira varredura acusou **18** ficheiros do
motor de tocarem Collection. Medidas as **importações** em vez das menções, restou
**uma**. As outras 17 só escreviam a palavra.

```
NOMEAR UMA GAVETA NAO E IMPORTAR DELA.
```

E `normalize_agro.py` é um CLI sem chamador: nenhuma cadeia, nenhum workflow.

```
DIRECT_COLLECTION_PATHS = 1   (existe em codigo)
EXERCIDOS POR ALGUMA ROTA = 0 (CAN DO != DID DO)
```

### 5 · 50 TESTES QUE NÃO CORREM, E DIZEM `OK`

| módulo | funções `def test_` | o `unittest` vê | workflow que o corre |
|---|---|---|---|
| `tests/test_v21_traducao_trava.py` | 23 | **0** | nenhum |
| `tests/test_v21_geografia.py` | 14 | **0** | nenhum |
| `tests/test_v21_datas.py` | 7 | **0** | nenhum |
| `tests/test_v21_mercado.py` | 6 | **0** | nenhum |

São testes em estilo **pytest** (funções soltas, sem `TestCase`). O CI desta casa
corre `python3 -m unittest`, e o pytest **não está instalado**. Sob `unittest` cada
módulo reporta `Ran 0 tests ... OK`.

```
UM MODULO DE TESTE QUE CORRE ZERO TESTES E VERDE SOBRE NADA.
```

E `tests/test_prioridade_comercial.py` corre 58 com **21 saltados** — o pacote não
está construído. `SKIP != PASS`.

### 6 · TRÊS PEÇAS, UM FICHEIRO — E UMA PEÇA COM NENHUM

```
italia-portale/audit/CANONICAL-PACKAGE-CONTRACT.json
  reclamado por lineage_generator, lineage_package e lineage_stale
```

Três peças de Intelligence apontam para o **mesmo e único** ficheiro. São três
factos diferentes (quem gera, o que se espera, o que está vencido) a partilhar um
documento — defensável, mas é `ONE CONCEPT → ONE OWNER` a pedir arbitragem.

E `lineage_consumer` tem **zero** ficheiros e o mapa apresenta-a como `PROVEN`.

```
UMA PECA SEM FICHEIRO NAO TEM O QUE PROVAR.
```

---

## O QUE NÃO ESTÁ NA INTELLIGENCE, E TALVEZ DEVESSE

Os conceitos da Intelligence **não vivem** nas 12 peças. Medida a massa por gaveta:

| conceito | ficheiros | onde está a maior massa |
|---|---|---|
| `EVIDENCE` | 327 | `data` 49 · `tests` 39 · `docs` 37 |
| `SIGNAL` | 301 | `data` 54 · `docs` 53 · `build` 45 |
| `LABEL` | 267 | `data` 45 · `italia-portale` 38 |
| `PORTFOLIO` | 218 | **`italia-portale` 85** |
| `OPPORTUNITY` | 186 | **`italia-portale` 50** · `build` 29 |
| `SCIENCE` | 179 | **`italia-portale` 51** |
| `CROSSING` | 120 | `docs` 23 · **`motor` 16** |

```
A INTELLIGENCE DO MAPA TEM 12 PECAS.
OS CONCEITOS DA INTELLIGENCE VIVEM SOBRETUDO NA ENTREGA E EM DADOS CONGELADOS.
```

E dois conceitos que o enunciado pede **não existem em lado nenhum da árvore**:

```
COLLECTION_GAP   = 0 ficheiros
INTELLIGENCE_RUN = 0 ficheiros
```

A Intelligence não tem noção de corrida própria nem de buraco de coleta.

---

## LLM E SEGURANÇA

```
LLM DENTRO DAS 12 PECAS        = 0
segredos literais na arvore    = 0
pecas com chamada de rede      = 0
pecas com execucao de processo = 1   (motor/pacote_normalizar.py, subprocess)
```

Os 42 ficheiros da árvore com marca de LLM são documentos, handoffs e amostras de
dados — **nenhum** é código de Intelligence. Não há inferência de modelo no motor,
e por isso não há superfície de prompt injection dentro destas 12 peças.

```
SECURITY_STATE = MEDIDO PARA ESTAS 12 PECAS, E NAO PARA A ARVORE INTEIRA.
```

---

## RESUMO QUANTITATIVO

```
SYSTEM_MAP_SOURCE_BRANCH = claude/raw-observation-identity-3jbwco @ 84186dfa
MAP_INTELLIGENCE_COUNT   = 12
CENSUSED                 = 12/12

PROVEN_OPERATIONAL                  = 3
CONNECTED_NOT_RUNTIME_PROVEN        = 5
PARTIAL                             = 2
ORPHAN / LEGACY                     = 1
ASSERCAO_SEM_FICHEIRO               = 1
BROKEN                              = 0
FUTURE                              = 0
UNKNOWN                             = 0

PROVEN_DUPLICATE                    = 0
POSSIBLE_DUPLICATE                  = 3   (o trio lineage, um ficheiro)
LEGACY_STILL_REFERENCED             = 1

CONCEPT_OWNER_COLLISIONS            = 2   (gerador canonico · opportunity)
DIRECT_COLLECTION_PATHS             = 1   (em codigo; 0 exercidos)
RUNTIME_PROVEN_FLOWS                = 2   (build-gate 2/2 · stale-gate 9/9)
DECLARED_ONLY_EDGES                 = ver INTELLIGENCE-OBSERVED-FLOWS.md
FALSE_CONVERGENCE_RISKS             = 1   (artefacto orfao italy-v21.js)
SECURITY_FINDINGS                   = 0 criticos · 1 a registar (subprocess)
TESTES_QUE_NAO_CORREM               = 50
```
