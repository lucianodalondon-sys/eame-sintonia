# ADDENDUM 02 — COLLECTION FOUNDATION GATE CLOSURE
# INCORPORAR À MISSÃO JÁ EM EXECUÇÃO — NÃO CRIAR MISSÃO PARALELA

Este addendum ACRESCENTA objetivo à missão. NÃO reinicie. NÃO recrie worktree.
Ordem de precedência: ADDENDUM-02 > ADDENDUM-01 > MISSAO-...md

==================================================
0. O OBJETIVO ADICIONAL
==================================================

Além de maximizar `SOURCE_COLLECTION_READY`, esta missão deve produzir a medição
necessária para saber **se a fundação da Collection pode ou não fechar**.

NÃO alterar o gate para fazê-lo passar.
NÃO editar generated JSON.

==================================================
1. AUTORIDADES — EXISTÊNCIA JÁ VERIFICADA
==================================================

Todas verificadas presentes em `d915f85a` (`git cat-file -e`):

```
leis/fundacao_da_coleta.py                            EXISTE
docs/operacao/TRAVA-DA-INTELIGENCIA.json              EXISTE
system-map/data/estradas-it.generated.json            EXISTE
system-map/scripts/censo_das_estradas_it.py           EXISTE
docs/operacao/MAPA-DE-FECHAMENTO-DA-COLETA-ITALIANA.md EXISTE
BIBLIA-CANONICA-DA-COLETA.md                          EXISTE
provas/trava_da_inteligencia_morde.py                 EXISTE
```

CONSTANTE MEDIDA — `leis/fundacao_da_coleta.py:55`:

```python
COLLECTION_FOUNDATION_CLOSED = False
```

Consumida em `pode_implementar_inteligencia()` (linha 93). Confirmado: é
**constante literal**, não cálculo de runtime. O caminho legítimo é
estado real → censo → estado gerado → critérios → só então mudança explícita.

==================================================
2. ⚠️ ACHADO DO COORDENADOR — DENOMINADOR ERRADO
==================================================

**Este é o achado mais importante deste addendum. Leia antes de medir as 23.**

O censo de estradas declara a sua própria proveniência:

```json
PROVENANCE.CATALOGO = "candidatas/ITALY-SOURCE-MASTER-V1.json"
```

Medido nesse catálogo:

```
sources_in_catalog = 54     (artifact ITALY-SOURCE-MASTER-V1, created_at 2026-09-07)
```

⚠️ **NÚMERO CORRIGIDO PELO `ADDENDUM-03`.** O valor `162` escrito abaixo na versão
original deste ficheiro estava ERRADO: vinha de regex sobre qualquer menção textual,
e contava exemplos, IDs gastos e IDs reservados como se fossem fontes.

Valor correto, verificado por igualdade de conjuntos contra o gerador canónico:

```
ATLAS_IT_CURRENT = 157
```

Portanto:

```
FONTES_IT (censo de estradas)  =  54
FONTES_IT (Atlas, correto)     = 157
UNIVERSE_GAP                   = 103      ← NÃO 108
```

> **O GATE DA FUNDAÇÃO ESTÁ A SER MEDIDO SOBRE 54 FONTES,
> ENQUANTO O ATLAS REGISTA 157 FONTES ITALIANAS.**

Leia `ADDENDUM-03-DENOMINADOR-IT-CORRIGIDO.md` antes de usar qualquer número desta
secção. A CONCLUSÃO não muda — o denominador continua inválido — mas o blocker
correto chama-se `FOUNDATION_DENOMINATOR_STALE`, não `..._UNPROVEN`.

Consequência direta e não negociável:

`COLLECTION_FOUNDATION_CLOSED = SIM` calculado sobre 54 fontes **não prova** que a
fundação fecha para o universo real. Fechar sobre o denominador menor seria o erro
mais caro possível nesta missão — e passaria despercebido, porque todos os
contadores internos do censo batem certo entre si (24+7+14+9 = 54 ✓).

COERÊNCIA INTERNA NÃO É COBERTURA. Um censo pode estar perfeitamente consistente
sobre o universo errado.

OBRIGAÇÃO:

```
CENSUS_UNIVERSE_SIZE        =
ATLAS_IT_UNIVERSE_SIZE      =
UNIVERSE_GAP                =
UNIVERSE_GAP_EXPLAINED      = YES / NO
UNIVERSE_GAP_REASON         =
FOUNDATION_DENOMINATOR_VALID = YES / NO / UNKNOWN
```

Descobrir POR QUE o catálogo tem 54: é recorte legítimo (ex.: só as fontes de uma
missão específica de 2026-09-07) ou é catálogo **stale** face ao Atlas?
São respostas diferentes com consequências diferentes.

Se `FOUNDATION_DENOMINATOR_VALID = NO` ou `UNKNOWN`, então
`COLLECTION_FOUNDATION_CLOSED_CURRENT = NAO`, independentemente dos critérios A..N,
e o blocker chama-se `FOUNDATION_DENOMINATOR_UNPROVEN`.

Não "resolver" isto alargando o catálogo por conta própria: medir, reportar, nomear
o owner.

==================================================
3. AS 23 FONTES UNKNOWN — REMEDIR
==================================================

Números do último censo, JÁ CONFIRMADOS pelo coordenador em `d915f85a`:

```
ROUTE_RESOLUTION_COUNTS
  ONLY_CANDIDATE_ROUTE     24
  HAS_PROVEN_ROUTE          7
  REACHABLE_ROUTE_UNKNOWN  14
  ROUTE_UNKNOWN             9
  ------------------------------
  TOTAL                    54   ✓ fecha
```

As "23 sem rota conhecida" = `REACHABLE_ROUTE_UNKNOWN 14` + `ROUTE_UNKNOWN 9`.
Confirmado: 14+9 = 23. E note que são **dois estados diferentes**, não um:
"alcançável mas rota desconhecida" ≠ "rota desconhecida". Não os colapse.

Para cada fonte UNKNOWN, produzir:

```
SOURCE_ID =
ACCESS_SHAPE =
ROUTE_CLASS =
ROUTE_STATE =
OWNER =
BLOCKER =
```

Não deixar `ROUTE_CLASS = UNKNOWN` se houver prova suficiente para classificar.
Não inventar classe para fazer contador fechar.
`UNKNOWN` sem prova permanece `UNKNOWN`.

==================================================
4. NÃO CONFUNDIR FONTE COM CLASSE
==================================================

23 fontes UNKNOWN ≠ 23 route classes.

20 fontes podem ser todas `HTML → PDF` e pertencer a UMA classe.
Agrupar por forma REAL de aquisição. Isto liga-se diretamente ao §4/§5 da missão
(ACCESS_SHAPE) — é a mesma pergunta vista do lado do gate.

==================================================
5. AS 12 CLASSES — ESTADO JÁ MEDIDO
==================================================

Medido pelo coordenador em `estradas-it.generated.json`:

```
ROUTE_CLASSES_MODELED            12
ROUTE_CLASSES_ARCHITECTURE_CLOSED []      ← ZERO classes fechadas
ROUTE_CLASSES_OBSERVED           [RC-1, RC-2]
ROUTE_CLASSES_DB_TESTED          [RC-5]
ROUTE_CLASSES_BLOCKED            [RC-6, RC-7, RC-8]
ROUTE_CLASSES_DEBT               [RC-9]
ROUTE_CLASSES_REQUIRED_TOTAL     UNKNOWN
  PORQUE: "23 fonte(s) sem rota conhecida. Ate a M1 provar, nenhuma delas
           garante caber nas 12 classes modeladas."

AS 12: OFFICIAL_HTTP_DOCUMENT · YOUTUBE_OFFICIAL_API · PUBLIC_NATIVE_API ·
SCIENCE_METADATA_API · REGULATORY_BULK_IMPORT · PUBLIC_BROWSER · LOCAL_SESSION ·
PAID_FALLBACK · GIT_LEDGER · OFFICIAL_HTTP_DATASET · OFFICIAL_STATISTICAL_API ·
SYNDICATED_FEED

Todas com ARCHITECTURE_CLOSED = False.
```

Para cada RC, medir e declarar:

```
RC_ID = · NAME =
DISCOVER = · FETCH = · RUN = · RAW = · CHECKPOINT = · DERIVED = ·
STRUCTURED = · ADMISSION =
ARCHITECTURE_CLOSED = YES/NO
BLOCKING_STEPS =
```

`OWNER_EXISTS` != `OWNER_CONNECTED`.
`MODULE_EXISTS` != `FLOW_EXISTS`.

Produzir: `ROUTE_CLASSES_REQUIRED` / `NOT_REQUIRED` / `UNKNOWN`.
`ROUTE_CLASSES_REQUIRED_TOTAL` só deixa de ser UNKNOWN quando o conjunto estiver
PROVADO — e note que, pelo §2, prová-lo sobre 54 não o prova sobre 157.

==================================================
6. BIG COLLECTION COMO PROVA — HIPÓTESE JÁ PARCIALMENTE REFUTADA
==================================================

O addendum original supunha que o mapa poderia estar a dizer `NO_DIRECT_REFERENCE`
onde a corrida real provou a aresta. MEDIDO — a suposição não se confirma assim:

```
As 6 fontes da Big Collection, em ROUTE_MEMBERSHIPS:
  IT-T2-002  STATE=PROVEN (×2)
  IT-T2-004  STATE=PROVEN + CANDIDATE
  IT-T3-002  STATE=PROVEN + CANDIDATE
  IT-T3-008  STATE=PROVEN + CANDIDATE
  IT-T3-010  STATE=PROVEN + CANDIDATE
  IT-T4-001  STATE=PROVEN + CANDIDATE

STATE geral:      DECLARED 4 · CANDIDATE 34 · PROVEN 8
PROOF_KIND geral: DECLARED 4 · EXPECTED 8 · LIVE_FETCH_PROVEN 1 ·
                  HISTORICALLY_OBSERVED 13 · LIVE_METADATA_PROVEN 20
BLOCKER:          None em 46/46
```

O censo **já reconhece** as 6 como PROVEN. A aresta não está perdida.

MAS restam contradições reais a investigar, e são suas:

- `ROUTE_CLASSES_ARCHITECTURE_CLOSED = []` — zero classes fechadas, apesar de
  `ROUTE_CLASSES_OBSERVED = [RC-1, RC-2]` e de 6 runs HEALTHY. Porquê?
  Observação de fluxo não fecha arquitetura — mas então **o que falta**, passo a passo?
- `NO_DIRECT_REFERENCE` aparece 3× e `NOT_OBSERVED` 5× no ficheiro. Onde,
  e contradizem a corrida real? Medir caso a caso.
- `PROOF_KIND = EXPECTED` em 8 memberships. EXPECTED não é prova. Confirmar que
  nenhuma delas está a sustentar um PROVEN.

Se houver causa (scanner stale / owner errado / flow diferente / mapa não observa
runtime), CORRIGIR A CAUSA — e apenas se estiver dentro do escopo.
NUNCA editar generated JSON.

==================================================
7. CRITÉRIOS A..N — REMEDIR TODOS
==================================================

Não copiar o estado antigo da trava. Cada um com PASS / FAIL / UNKNOWN + PROOF.

```
A  toda fonte IT tem route class conhecida ou BLOCKED explícito
B  nenhuma fonte depende de writer improvisado
C  RAW tem um dono
D  corrida tem contrato
E  checkpoint tem dono
F  derived tem dono
G  persistência estruturada tem dono por espécie
H  escolha de rota não vive espalhada
I  Apify não é rota por omissão
J  Git não é estado operacional
K  retry/queda não fabrica sucesso
L  UNKNOWN continua UNKNOWN
M  System Map representa tudo
N  Intelligence continua congelada até o fim
```

AVISO sobre o critério A: ele diz "toda fonte IT". Pelo §2, "toda fonte IT" são
**157**, não 54. Se A for avaliado sobre 54, declare isso explicitamente —
`A = PASS (sobre 54) / UNKNOWN (sobre 157)` é resultado honesto; `A = PASS` sozinho
não é.

Lembrete do §8 do ADDENDUM-01: verificar também a observação com
`RAW_OBJECT_CREATED = False` (1 das 9) ao medir o critério C.

==================================================
8. NÃO DECLARAR FUNDAÇÃO FECHADA CEDO
==================================================

Mesmo que `ROUTE_CLASSES_REQUIRED_TOTAL` deixe de ser UNKNOWN, **isso não basta**.

Só propor `COLLECTION_FOUNDATION_CLOSED = SIM` se TODOS os critérios materiais
exigidos passarem E `FOUNDATION_DENOMINATOR_VALID = YES`.

Caso contrário: `NAO` + lista de blockers.

PROPOR != ALTERAR. A mudança da constante em `leis/fundacao_da_coleta.py` exige
autorização explícita do coordenador. Nesta missão: **apenas propor, com prova**.

==================================================
9. NÃO MEXER NA INTELLIGENCE
==================================================

```
DIRECT_INTELLIGENCE_CHANGES = 0
```

Não alterar: `motor/`, signals, opportunity, scoring, recommendations,
portal intelligence wiring.

A Collection fecha a fundação. Outra missão abre a Intelligence.

==================================================
10. DEFEITOS DA TRAVA — REMEDIR
==================================================

```
DEFECT-05  provas/trava_da_inteligencia_morde.py deixa sujeira (teardown sujo)
DEFECT-06  censo confunde documentação/desenho com implementação
```

Ambos ainda não verificados pelo coordenador: estado = `NÃO MEDIDO`.

Se confirmados, corrigir SOMENTE se pertencer ao owner da Collection e houver prova
clara. Exigir teardown limpo e testes que distingam
`DOCUMENTATION / DESIGN` de `IMPLEMENTATION / CONTRACT / PORTAL_UI`.

NÃO relaxar a trava. Um teste que passa por ter sido afrouxado é pior que um teste
vermelho.

DEFECT-06 tem parentesco direto com o §2 deste addendum: confundir desenho com
implementação e medir sobre o universo errado são o mesmo tipo de erro — contar a
coisa errada com precisão.

==================================================
11. ENTREGA (ACRESCE AO §28 DA MISSÃO)
==================================================

```
UNIVERSO E DENOMINADOR
CENSUS_UNIVERSE_SIZE =
ATLAS_IT_UNIVERSE_SIZE =
UNIVERSE_GAP =
UNIVERSE_GAP_EXPLAINED =
FOUNDATION_DENOMINATOR_VALID =

ROTAS
TOTAL_IT_SOURCES =
SOURCES_WITH_ROUTE_CLASS =
SOURCES_ROUTE_UNKNOWN =
  REACHABLE_ROUTE_UNKNOWN =
  ROUTE_UNKNOWN =

CLASSES
ROUTE_CLASSES_MODELED =
ROUTE_CLASSES_REQUIRED =
ROUTE_CLASSES_NOT_REQUIRED =
ROUTE_CLASSES_UNKNOWN =
ARCHITECTURE_CLOSED_CLASSES =
ARCHITECTURE_OPEN_CLASSES =

CRITERIA_A_TO_N   (cada um: PASS/FAIL/UNKNOWN + PROOF + denominador usado)
A = · B = · C = · D = · E = · F = · G =
H = · I = · J = · K = · L = · M = · N =

COLLECTION_FOUNDATION_CLOSED_CURRENT = SIM / NAO
BLOCKERS_REMAINING =

DEFECT_05 = CONFIRMED / DISPROVED / FIXED
DEFECT_06 = CONFIRMED / DISPROVED / FIXED

SOURCE_COLLECTION_READY_BEFORE =
SOURCE_COLLECTION_READY_AFTER =

SYSTEM_MAP_CHECK =
RED_TEAM_BLOCKERS =
NEW_FAILURES =
KNOW_HOW_DELTA =
NEXT_MINIMUM_STEP =
```

Mais a secção EM LINGUAGEM SIMPLES do §29 da missão, obrigatória.

==================================================
HARD STOP
==================================================

Não iniciar Intelligence automaticamente, **mesmo se
`COLLECTION_FOUNDATION_CLOSED` passar**. A abertura da Intelligence é missão
separada, com autorização separada.

Não iniciar Big Collection. Não iniciar Portal. Não descobrir novas fontes.
Não fazer merge para o trunk sem autorização do coordenador.
Não alterar a constante `COLLECTION_FOUNDATION_CLOSED` — apenas propor.
