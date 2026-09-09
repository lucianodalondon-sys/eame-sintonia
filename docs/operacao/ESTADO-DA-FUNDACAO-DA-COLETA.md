# ESTADO DA FUNDAÇÃO DA COLETA — SINTONIA EAME

```
MISSAO            C-FINAL · fechamento arquitetural da Collection
BRANCH            claude/collection-foundation-integration-v1
BASE_HEAD         1c99a48b
DATA              2026-09-09
VEREDITO          COLLECTION_FOUNDATION_V1 = PARTIAL
```

> **Este documento é DERIVADO de medições.** Cada número aqui tem, ao lado, o
> comando que o produz. Um número sem comando não entra.

---

## 1 · O VEREDITO, EM UMA FRASE

A coleta **tem** uma fronteira canônica declarada, com um dono e um contrato
de 11 campos — e **ninguém entrega nela nem recolhe dela**. Tudo o que era
resolvível por engenharia nesta linha foi resolvido; o que resta são dívidas
de **dados já gravados** e **uma decisão de arquitetura** que não é de
engenharia.

```
ENGINEERING_BLOCKERS       0
ARCHITECTURE_DECISIONS     1   (ligar a rota forward ao READY)
HUMAN_DECISION_BLOCKERS    1   (a autoridade da fonte IT-T2-002)
DATA_DEBT_BLOCKERS         1   (10 de 20 manifestos incompletos)
NEW_FAILURES               0
PRODUCTION_MUTATION        0
```

---

## 2 · A FRONTEIRA COLEÇÃO → INTELIGÊNCIA

`python3 provas/a_fronteira_da_coleta.py`

```
CONTRATO       COL-LAW-043 · 11 campos, fixos
DONO           admissao/admissao.py :: pronto_para_inteligencia()
PRODUTORES     2  — orquestrador/orquestrador.py (CLI, em workflow nenhum)
                    provas/testa_coleta_canonica.py (prova)
CONSUMIDORES   0
DESTINO        data/samples/PRONTO-PARA-INTELIGENCIA/   ·   NÃO EXISTE
```

**READY é um conceito legítimo da coleta.** Está na Bíblia (COL-LAW-043), tem
dono, tem contrato, e o código devolve exatamente os campos que a lei declara.
Não se criou `ready.py` nenhum: ele já existia.

O que falta são duas coisas diferentes, e confundi-las foi o que fez três
documentos desta casa dizerem coisas incompatíveis:

1. **CAMINHO.** A rota forward (`DERIVED → STRUCTURED → ADMISSION`) termina em
   ADMISSION e não chega ao READY, porque o dono recebe um `item` e a rota
   produz um `derived_artifact`. Ligá-los é **decisão de arquitetura**, não
   remendo de código.
2. **CONSUMIDOR.** Nenhum. A própria Bíblia já diagnosticou isto (`:288`):
   *uma porta por onde ninguém passa não é uma porta; é uma parede com maçaneta.*

`provas/a_fronteira_da_coleta.py` **não falha** por não haver consumidor. Fazer
essa prova ficar verde inventando um consumidor seria a doença que ela veio
diagnosticar.

---

## 3 · A ROTA, MEDIDA

`BANCO_DESCARTAVEL_URL=... python3 provas/a_rota_m2_atravessa.py` → **PASS**

A **mesma** rota (`IT-T2-002` / `RC-1`) atravessa `DERIVED → STRUCTURED →
ADMISSION` numa corrida só, com o artefato a viajar e as duas arestas com os
**dois topos** no banco. 23 migrations aplicadas num PostgreSQL 16 real.
17 casos, três deles mutações que fazem a prova morder.

```
ARESTA OBSERVADA     DERIVED  → STRUCTURED
ARESTA OBSERVADA     STRUCTURED → ADMISSION
ARESTA DECLARADA E SEM TOPO     RAW → DERIVED   (gap RAW_FORWARD_NAO_EMITE)
```

**Esta prova não era chamada por workflow nenhum.** Passou a ser
(`banco-descartavel.yml`, passo 2g), junto com os ficheiros que ela atravessa —
que também não acordavam portão nenhum quando alguém lhes mexia.

---

## 4 · OS OITO BURACOS DECLARADOS

Todos continuam **ABERTOS**. Nenhum foi fechado a inventar informação.

| gap | onde é declarado | o que mudou nesta missão |
|---|---|---|
| `RAW_FORWARD_NAO_EMITE` | `coleta/derivacao_forward.py` GAPS | — |
| `STRUCTURED_SEM_DONO_LIGADO` | idem | — |
| `ADMISSION_SEM_DONO_LIGADO` | idem | — |
| `READY_NAO_TEM_DONO` | idem | **texto corrigido** — o nome dizia mais do que se mediu |
| `TELEMETRY_FAILURE_SEM_POLITICA` | idem | **passou a ser declarado** — vivia só num `print` |
| `CHANNEL_IDENTITY_NOT_RESOLVED` | `system-map/data/provas-de-execucao.json` | — |
| `GAP_DECLARADO` | idem | — |
| `LINEAGE_PROOF_GAP` | idem | — |

`GAPS_ANTES = 8 · GAPS_DEPOIS = 8`. O que mudou foi **poderem ser lidos**: o
oitavo podia desaparecer sem dar erro em sítio nenhum.

---

## 5 · IDENTIDADE — M2I CONTINUA PARCIAL

`BANCO_DESCARTAVEL_URL=... python3 provas/a_autoridade_da_fonte.py`
→ `SOURCE_AUTHORITY[IT-T2-002] = UNRESOLVED`

As cinco faltas foram **remedidas** e as cinco continuam verdadeiras:

1. `IT-T2-002` não tem ficha no Atlas canônico (`grep -c` → 0)
2. não tem contrato canônico com OWNER
3. não há tradução declarada de `OWNER_KIND` → `organizacao.tipo`
   (schema aceita 9 tipos, o catálogo fala 12, **zero coincidem**)
4. `IT-OWN-003` (catálogo) × `IT-OWN-ARPAV` (contrato de acesso) — sem árbitro
5. **zero escritores de identidade em runtime**

Atlas: `37 / 42 / 23` (declarados no cabeçalho / mencionados / fichas completas).
Inalterado.

> **HUMAN_DECISION_REQUIRED.** Qual catálogo tem autoridade sobre o dono de
> `IT-T2-002`? A engenharia **detecta** o conflito; não pode inventar a
> autoridade. Menor passo possível: alguém com autoridade de conteúdo escolhe
> entre `IT-OWN-003` e `IT-OWN-ARPAV`, e essa escolha entra num contrato de fonte.
> **Nada nesta lista impede o resto da fundação de funcionar.**

---

## 6 · O BANCO

```
MIGRATIONS        24, aplicadas até a 024 num PostgreSQL 16 descartável
MIGRATION_024     DESIGNED · DB_TESTED · NOT LIVE
PRODUCAO          INTOCADA
```

`decisao_de_coleta` (024), `canal`, `organizacao` e `origem` (002) têm
**RUNTIME_WRITER: NONE** — só testes e provas escrevem neles. Isto é a mesma
falta do §5 vista pelo lado do banco, não uma quinta descoberta.

`provas/o_dedupe_tem_constraint.py` (novo) confronta as **61** cláusulas
`on conflict` da árvore com a chave única que as arbitra. Todas cobertas.

---

## 7 · O QUE FICA VERMELHO, E POR QUE NÃO SE PINTOU DE VERDE

`for f in tests/test_*.py; do python3 -m unittest "tests.$(basename $f .py)"; done`

```
BASE_FAILURES    10   (worktree real em 1c99a48b)
FINAL_FAILURES    6
NEW_FAILURES      0
RESOLVED          4
```

| módulo | por que continua vermelho |
|---|---|
| `test_proveniencia` | **dívida de dados**: 10 de 20 manifestos sem 4 campos do contrato; 3 com `STATUS=OK` fora do vocabulário; 1 com hora de escrita promovida a hora de execução. Nenhum escritor vivo emite `OK` — é registro passado. Preencher seria adivinhar o que aquelas corridas fizeram. |
| `test_evidence` | mesma família: amostras que declaram `SOURCE_LOCATION` e não declaram `FACT_LOCATION` |
| `test_operacao` | proveniência de claim numa amostra publicada |
| `test_comunicacao` | «nenhuma casa nasce autorizada» — esperado `{'NO'}`, obtido `set()` |
| `test_canonico`, `test_handoff` | **formato** do mesmo número: o `--sync` escreve `1.648`, dois casos querem `1648`. Decisão de escrita sobre documentos de apresentação, fora da fundação da coleta. |

**REQUIRED FIELD ≠ PERMISSION TO FABRICATE.**

---

## 8 · O QUE ESTA MISSÃO LIGOU

Nove provas não eram chamadas por workflow nenhum. Não eram código morto —
eram **portões desligados**, que é pior: parecem cobertura e não cobrem nada.

```
banco-descartavel.yml   2f · o_forward_conta_se
                        2g · a_rota_m2_atravessa      ← a única prova ponta-a-ponta
                        2h · a_autoridade_da_fonte
                        2i · o_dedupe_tem_constraint
system-map.yml          4k · paridade_da_lingua
                        4l · fluxo_no_seco
                        4m · testa_golden_path_pdf
                        4n · o_mapa_nao_mente
                        4o · o_dedupe_tem_constraint
                        4p · o_executor_conta_se
                        4q · a_fronteira_da_coleta
```

Ao ligá-las, uma estava **vermelha** (`fluxo_no_seco`, dois defeitos reais) e
outra **passava sem medir** (`o_executor_conta_se`, com e sem `pdftotext`, saída
byte a byte igual).

---

## 9 · PARA A LINHA DO SYSTEM MAP

Esta missão **não** tocou em `system-map/`. Dois itens medidos aqui pertencem
àquela linha e ficam como entrega:

1. `system-map/data/donos.generated.json` está **desatualizado** em relação ao
   próprio gerador (`python3 system-map/scripts/censo_dos_donos.py` produz um
   diff de 42 inserções / 36 remoções). Nenhum teste apanha essa defasagem.
   A branch `claude/system-map-freshness-v1` já trabalha exatamente nisso.
2. `M2_ROUTE_OBSERVABILITY_READY` é derivado de literais escritos à mão em
   `system-map/data/provas-de-execucao.json`. A única medição que pergunta ao
   **banco** é `provas/a_rota_m2_atravessa.py`, e nada compara as duas. Um red
   team apontou; a correção pertence ao dono daquele ficheiro.

Ao regenerar o mapa nesta árvore, ele passa a enxergar as duas provas novas.

---

## 10 · COMO CONTINUAR

```bash
git fetch --all --prune
git checkout claude/collection-foundation-integration-v1

# as provas de banco (PostgreSQL 16 descartável, banco VIRGEM a cada uma)
BANCO_DESCARTAVEL_URL=postgresql://postgres@127.0.0.1:5433/descartavel \
  python3 provas/a_rota_m2_atravessa.py

# as provas sem banco
python3 provas/a_fronteira_da_coleta.py
python3 provas/o_dedupe_tem_constraint.py

# a linha de base honesta
for f in tests/test_*.py; do
  python3 -m unittest "tests.$(basename "$f" .py)" >/dev/null 2>&1 || echo "$f"
done
```

> ⚠️ A cadeia de migrations **não é idempotente**: a segunda aplicação morre em
> `type "pais" already exists`. Toda prova de banco precisa de um banco **virgem**.
