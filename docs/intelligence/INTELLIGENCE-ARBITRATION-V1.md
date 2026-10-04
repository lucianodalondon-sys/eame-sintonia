# ARBITRAGEM DA INTELLIGENCE CANÓNICA — V1

```
MISSAO            C-INT-ARB-01 · 2026-09-13
BASE              o censo C-INT-CENSUS-01
FUNCTIONAL_HEAD   f888776d  (o censo mediu 84186dfa · DRIFT = YES)
CENSUS_FACTS_DRIFT = NO
```

> **ARBITRAGEM.** Não autoriza implementação. Nenhum motor foi construído,
> nenhuma lei nova foi inventada onde já havia autoridade.

---

## 0 · O DRIFT, E POR QUE ELE NÃO INVALIDOU NADA

A linha funcional andou um commit desde o censo — `o READY social passa a nomear
a observacao que o originou`. Reexecutado o instrumento do censo contra
`f888776d`, os onze factos usados nesta arbitragem **holdem**:

```
12 pecas de Intelligence          HOLD
V2 antigo orfao                   HOLD
cadeia V2.1 fail-closed  exit=2   HOLD
build-gate exit=0 · stale 9/9     HOLD
INTELLIGENCE_RUN     0 ficheiros  HOLD
COLLECTION_GAP       0 ficheiros  HOLD
normalize_agro -> eppo_gd, 0 callers  HOLD
50 funcoes de teste invisiveis    HOLD
colisao do gerador  55c2674 x 5101073  HOLD
```

A peça nova foi para a Collection. `F-INTELIGENCIA` continua em 12.

---

## 1 · A CONSTITUIÇÃO — E ELA JÁ SE TINHA PROPOSTO

```
BIBLE_STATUS    = CANDIDATE_FOR_CANONICAL_REVIEW   (inalterado)
MOTOR_V2_STATUS = SUBORDINATE_IMPLEMENTATION_CONTRACT   (ARBITRADO AQUI)
```

A missão manda testar a relação `BIBLE = constituição / MOTOR V2 = contrato
subordinado` **sem assumir que está correta**. Testada, sobrevive — e a Bíblia
§30 já a tinha proposto, deixando-a «a decidir». Esta missão decide.

### O que cada documento diz de si próprio

| | diz ser | diz **não** ser |
|---|---|---|
| **Bíblia V0.2** | leis, fronteiras, identidade conceitual; `IMPLEMENTATION_AUTHORIZED = NO` | relatório, backlog, handoff, design de portal, prova de implementação |
| **Motor V2** | contrato de requisitos, fonte de verdade sobre gates e proibições, base do `MOTOR_V2_READY` | relatório de execução, inventário, documentação de portal, promessa de implementação |

Nenhum dos dois reivindica o lugar do outro. O Motor V2 diz «declara a **lei**
que vale para as próximas rodadas» — mas escopada a um motor, e julgada por
`MOTOR_V2_READY`. Isso é contrato de implementação, não constituição.

### O teste de conflito, conceito a conceito

| conceito | BÍBLIA diz | MOTOR V2 diz | conflito? | owner | prova |
|---|---|---|---|---|---|
| identidade de CLAIM | `INT-LAW-031`: exigir identidade global, **mas não fabricá-la** se o upstream não a tem — vira gap | §6: identidade única, determinística, reproduzível; `CLAIM_ID_COLLISIONS = 0` | **NÃO** | Bíblia, que **cita e preserva** o Motor V2 | linha 221 da Bíblia |
| zero / universos | `INT-LAW-110..114` | §14, §15 | **NÃO** — mesma direção | Bíblia | ambos exigem universo declarado |
| convergência | `INT-LAW-070..077`, `090..095` | §4 | **NÃO** | Bíblia | independência antes de contagem |
| gates que sabem falhar | `INT-LAW-012` | §17 | **NÃO** | Bíblia | `UNKNOWN` declarado é resultado válido |
| radar futuro | `INT-LAW-001` (governa) | §5 (estados concretos) | **NÃO** | Bíblia governa, Motor detalha | — |
| casos-testemunha | não trata | §3 (VITE, EXELGROW, MAIS) | **NÃO** | Motor V2 | a Bíblia não desce a casos |

```
CONFLITOS ESTRUTURAIS ENCONTRADOS = 0
```

A Bíblia cita o Motor V2 três vezes, e a citação decisiva é `INT-LAW-031`:
«**Preservar** a exigência do Motor Intelligence V2». Ela não o revoga — herda-o
e acrescenta a fronteira de propriedade.

```
UMA CONSTITUICAO QUE PRESERVA O CONTRATO ANTERIOR
NAO ESTA A COMPETIR COM ELE: ESTA A ENQUADRA-LO.
```

---

## 2 · FACT / CLAIM — O ATAQUE OBRIGATÓRIO

```
FACT_CLAIM_COLLISION = NAME_COLLISION
```

O censo escreveu `FACT / CLAIM → v21_dominio_da_alegacao.py`. Lido o
**comportamento**, e não o nome:

| pergunta | resposta medida |
|---|---|
| cria SOURCE FACT/CLAIM? | **não** |
| cunha `CLAIM_ID`? | **não** — `grep CLAIM_ID motor/*.py` = **vazio** |
| gera sha/uuid/hash de identidade? | **não** |
| opera sobre que ids? | ids upstream já existentes (`IT-CAN-4DAA0F9889`, …) |
| o que decide, então? | se a alegação é **sobre o mundo** ou **sobre o nosso encanamento** |

O próprio ficheiro diz:

> SABER COMO ABRIR A PORTA NÃO É SABER O QUE HÁ NA SALA.
> `CLIENT_SAFE` = a evidência aguenta **E** a alegação é sobre o mundo.

Ele estende um portão de visibilidade sobre claims que já existem. **Não fabrica
uma segunda identidade factual** — que é exatamente o que `INT-LAW-000` proíbe.

### Vocabulário canónico proposto

```
SOURCE_FACT / SOURCE_CLAIM     COLLECTION   o facto extraido do artefacto
CLAIM_DOMAIN_JUDGMENT          INTELLIGENCE o claim e sobre o mundo, ou sobre
                                            a nossa infraestrutura de coleta
```

A palavra «alegação» no nome do ficheiro refere-se ao **domínio de** um claim, e
não à sua criação. Colisão de nome, não de dono.

### ⚠️ E uma correção ao censo

O censo atribuiu esse ficheiro a `C-V21-INGEST`. O mapa põe-no em
`C-V21-OPORTUNIDADE`. **Erro meu**, corrigido no documento do censo.

---

## 3 · OPPORTUNITY — RESOLVIDO

```
OPPORTUNITY_OWNER = C-V21-OPORTUNIDADE  ·  motor/v21_oportunidades.py
STATUS            = CANONICAL_OWNER_PROVEN
```

O censo deixou `NÃO SEI` porque contou ficheiros. Contar ficheiros mede **massa**,
e massa não é propriedade. Separadas as quatro funções:

| função | quem | prova |
|---|---|---|
| **CREATOR** | `motor/v21_oportunidades.py` | descobre convergências, aplica **oito portões**, decide `OPPORTUNITY_STATE`, escreve `OPPORTUNITIES.json` |
| **STORAGE** | `build/…/OPPORTUNITIES.json` | artefacto congelado — guarda, não decide |
| **PROJECTION** | `italy-handoff-v21.js` | transporte |
| **UI** | `portale.html` + `italy-app-model.js` | **lê** `CLIENT_SAFE` e `RENDERABLE_WITH_METHOD`; 1 ocorrência de cálculo em 5 124 linhas |

E há autoridade prévia a dizer o mesmo, em dois sítios:

- `INT-LAW-039` — «Opportunity é objeto analítico, **não card visual**»
- `INT-LAW-023` — «Portal não reconstrói Intelligence»

O próprio motor declara a sua lei: «Uma oportunidade é LEITURA NOSSA sobre factos
de terceiros. `CLIENT_SAFE = false, SEMPRE`.»

```
QUEM DECIDE QUE UMA OPPORTUNITY EXISTE E QUEM CORRE OS OITO PORTOES.
O PORTAL NAO VIRA DONO POR TER MAIS FICHEIROS.
```

---

## 4 · O GERADOR CANÓNICO

```
GENERATOR_OWNER = CONTRACT_WINS
CANONICAL_GENERATOR = claude/acervo-to-package-intelligence-v1 @ 51010733
```

Revalidado neste HEAD:

```
build-gate.mjs           exit 0   ARTEFACTO_SERVIDO_E_CANONICO [V21-06c6421d001ea52a]
stale-generator-gate.mjs 9/9 PASS com controlos negativos
motor/v21_cadeia.sh      exit 2   (recusa-se nesta linhagem)
```

`motor/v21_cadeia.sh:35,47` continua a nomear `55c2674`, cuja safra o contrato
lista como **velha** (`V21-69bf448ac934a6d9`).

```
ENTRE DOIS DOCUMENTOS QUE DISCORDAM, GANHA O QUE UM PORTAO LE.
```

O contrato é executado por dois portões; o cabeçalho da cadeia é prosa. A
autoridade documental subordinada que ficou stale é o **cabeçalho da cadeia**, e
corrigi-lo é uma edição de comentário na linha funcional — **não feita aqui**,
porque esta missão não altera a linha funcional. Fica na migração.

Nenhuma cadeia histórica foi corrida com override. Nenhum pacote foi gerado.

---

## 5 · AS 12 PEÇAS — DESTINO ARQUITETURAL

| peça | destino | porquê |
|---|---|---|
| `C-CADEIA-V21` | **NEEDS_SPLIT** | agrupa `v21_cadeia.sh` (Intelligence) e `cadeia_canonica.sh` (migrations de banco) |
| `C-V21-INGEST` | KEEP_CANONICAL | mas carrega o caminho directo — ver §8 |
| `C-V21-CRUZAMENTO` | KEEP_CANONICAL | dono provado de CROSSING e CONVERGENCE |
| `C-V21-OPORTUNIDADE` | KEEP_CANONICAL | dono provado de OPPORTUNITY e de `CLAIM_DOMAIN_JUDGMENT` |
| `C-V21-CONTRATO` | KEEP_SUBORDINATE | lado Python de um contrato cujo dono é o JSON |
| `C-V21-COMERCIAL` | KEEP_SUBORDINATE | leitura comercial subordinada ao motor |
| `C-V21-FONTES` | KEEP_SUBORDINATE | religação de fontes do pacote |
| `C-V2-LEGADO` | **LEGACY** | ver §6 |
| `lineage_generator` | MOVE_TO_GOVERNANCE | é facto de linhagem e portão, não motor analítico |
| `lineage_package` | MOVE_TO_GOVERNANCE | idem |
| `lineage_stale` | MOVE_TO_GOVERNANCE | idem |
| `lineage_consumer` | **ASSERTION_NOT_COMPONENT** | zero ficheiros, e o mapa apresenta-a como `PROVEN` |

```
KEEP_CANONICAL 3 · KEEP_SUBORDINATE 3 · MOVE_TO_GOVERNANCE 3
NEEDS_SPLIT 1 · LEGACY 1 · ASSERTION_NOT_COMPONENT 1 · UNKNOWN 0
```

⚠️ **`MOVE_TO_GOVERNANCE` dos três `lineage_*` é proposta, não execução.** Mover
território entre famílias é edição do mapa declarado na linha funcional, e esta
missão não lhe toca.

---

## 6 · O MOTOR LEGADO

```
LEGACY_STATUS = CONFIRMED_LEGACY
```

7 ficheiros, 0 chamadores, 0 runtime. Quem ainda aponta para ele, medido:

```
handoff/paused-v2/auditoria-pacote.json
```

Um único artefacto, e o próprio caminho diz `paused-v2`. Não apagar nesta missão.

---

## 7 · SYSTEM MAP — O QUE `PROVEN` PASSA A SIGNIFICAR

O censo mediu, nas 82 arestas das 12 peças:

```
co-acesso a ficheiro   56
linha de workflow      45
import                 34
chamada de funcao       0
```

E as 82 estão marcadas `technical/PROVEN`. Isso colide com `INT-LAW-042` —
«Participar do mesmo run não cria edge» — e com `DECLARED EDGE ≠ OBSERVED EDGE`.

### Vocabulário canónico de aresta (definido, não implementado)

```
DECLARED            alguem escreveu que a seta existe
STATIC_REFERENCE    um ficheiro nomeia o outro          ← o mais fraco
IMPORT_OBSERVED     ha um import                        ← nao e fluxo
CALL_OBSERVED       ha uma chamada                      ← hoje: ZERO
WORKFLOW_OBSERVED   um workflow invoca                  ← invocacao real
RUNTIME_OBSERVED    correu, e ha saida medida
```

```
SYSTEM_MAP_EDGE_SEMANTICS = DEFINED_NOT_IMPLEMENTED
```

**Por que não implementei:** `"kind": "technical", "status": VERDE` está fixo em
**7 sítios** do gerador, e existem **dois geradores divergentes** (linha funcional
e linha de governança). Mudar num só cria a fragmentação que esta missão existe
para reduzir. `§15` prevê exatamente este caso: documentar, e deixar para missão
própria.

---

## 8 · O CAMINHO DIRETO À COLLECTION

```
motor/normalize_agro.py:29  →  coleta/eppo_gd.py:28  →  https://gd.eppo.int
CLASSIFICACAO = KEEP_BUT_BLOCK
```

Existe em código, alcança a rede, e **nenhuma rota o anda** (0 chamadores; é um
CLI `build`/`evaluate`).

`KEEP_BUT_BLOCK` e não `REMOVE_CANDIDATE` porque o dicionário agronómico que ele
constrói é trabalho real; o que não pode sobreviver é a rota. A arquitetura
canónica proíbe-o por `INT-LAW-020`: falta de evidência vira `COLLECTION_GAP` e
volta pela Collection — nunca um coletor chamado de dentro do motor.

Nada foi alterado em `coleta/`.

---

## 9 · POLÍTICA DE TESTES

```
INTELLIGENCE_TEST_RUNNER_DECISION = UNITTEST
NATUREZA = AUDITORIA DE DECISAO EXISTENTE, E NAO DECISAO NOVA
```

Medido, e não escolhido por gosto:

| evidência | valor |
|---|---|
| workflows que correm `python3 -m unittest` | **5** |
| workflows que correm pytest | **0** |
| pytest declarado em requirements/pyproject | **não** |
| pytest instalado no ambiente | **não** |
| decisão prévia da casa (`DIARIO-DE-DECISOES`, D-009) | conta a suíte com `unittest.defaultTestLoader.discover` |
| testes que o loader canónico vê | **3 892** em 152 ficheiros |
| ficheiros em estilo pytest | **4**, com **50** funções invisíveis |

148 de 152 ficheiros seguem a convenção. A Intelligence é a **única** área que a
quebra.

```
CONSEQUENCIA: converter os 4 ficheiros para unittest.
NAO: trocar o runner da casa por causa de quatro ficheiros.
```

Não executado aqui — é alteração na linha funcional.

```
E «Ran 0 tests ... OK» NAO E PASS.
```

---

## 10 · TOPOLOGIA

Ver `INTELLIGENCE-CANONICAL-TOPOLOGY-V1.md`.

---

## 11 · PROMOÇÃO DA BÍBLIA

```
BIBLE_PROMOTION_READY = NO
```

A Bíblia fixa **nove** condições próprias (§31). Medidas:

| # | condição | estado |
|---|---|---|
| 1 | reconciliação com a Bíblia da Collection | ✅ `INT-LAW-000` dá `CLAIM/FACT` à Collection |
| 2 | reconciliação com Motor V2 | ✅ **feita nesta missão** — 0 conflitos |
| 3 | owner collision count = 0 | ⚠️ **2 pendentes**: `RELEVANCE` e `PRIORITY` (`OWNER_NEEDS_HUMAN_DECISION`) |
| 4 | registo no Control Plane | ✅ **feito nesta missão** |
| 5 | **integração em snapshot onde a autoridade não fique invisível numa branch lateral** | ❌ **BLOQUEADOR** |
| 6 | governance gate | ✅ passa |
| 7 | System Map pela cadeia canónica | ✅ |
| 8 | know-how delta aplicado ao owner canónico | ⚠️ delta escrito, integração pendente |
| 9 | aprovação explícita da promoção | ❌ **é humana, e não é minha** |

### O bloqueador, medido

```
Biblia V0.2      research/intelligence-bible-engineering-v1  7ae1b510
Motor V2         claude/intelligence-backlog-canonical       4df24aa9
Censo + Controle claude/funny-hypatia-y7ho5s                 a885769c
Know-how         claude/sintonia-eame-know-how-v1            7b5e50cf
Runtime + Coleta claude/raw-observation-identity-3jbwco      f888776d

NENHUM COMMIT CONTEM TODAS.  CONTROL_PLANE_ATOMICITY = FAIL
```

```
UMA CONSTITUICAO QUE VIVE NUMA BRANCH QUE NINGUEM CLONA
GOVERNA EXATAMENTE NINGUEM.
```

**Mover a Bíblia da minha branch lateral para outra branch lateral não resolve
isto** — só muda de qual ramo ela é invisível. Por isso não a movi.

### O que **foi** feito, e é o mínimo correto

Registei as duas autoridades em `controle/AUTORIDADES-CANONICAS.json`. O registo
existe precisamente para tornar a fragmentação **visível e contável** sem fingir
que a conserta.

E resolveu-se uma dúvida que parecia colisão: o registo já continha
`A-BIBLIA-INTELIGENCIA` como `RECOVERY_PENDING`, apontando para
`docs/biblia/BIBLIA-DA-INTELIGENCIA-EAME.md`. Lido, esse ficheiro **recusa o
título**: chama-se «INVENTÁRIO DAS LEIS — **entrada para** a Bíblia», e o seu §7
lista 12 blocos que lhe faltam.

A V0.2 cobre **9 desses 12**. Não cobre `KIT/KIQ`, `FIELD_VOICES` e
`DECISION_TELEMETRY`.

```
NAO HA DUAS BIBLIAS. HA UM INVENTARIO QUE PEDIU UMA BIBLIA,
E A BIBLIA QUE CHEGOU DEPOIS.
```

---

## 12 · O QUE NÃO MUDOU

```
Collection            INTACTA — nenhum ficheiro de coleta/, guarda/, admissao/
READY · Sala de Espera INTACTOS
migrations            INTACTAS
Portal                INTACTO
motor/                INTACTO — nenhuma linha alterada
linha funcional       INTACTA — nada empurrado para la
LIVE                  0 leituras · 0 escritas
pacote                nenhum gerado; cadeia historica nao corrida com override
```

---

## 13 · O QUE FICA EM NÃO SEI

```
NAO_SEI  quem possui RELEVANCE e PRIORITY. Ha 157 e 126 ficheiros a toca-los
         e nenhuma lei a nomear dono. Precisa de decisao humana.

NAO_SEI  se KIT/KIQ, FIELD_VOICES e DECISION_TELEMETRY devem entrar na Biblia
         antes da promocao. O inventario pediu-os; a V0.2 nao os tem; e as
         condicoes de promocao da propria Biblia nao os exigem.

NAO_SEI  quantas das 82 arestas sobreviveriam ao vocabulario novo. Para saber,
         e preciso mudar o classificador — e isso e missao propria.

NAO_SEI  se `handoff/paused-v2/auditoria-pacote.json` ainda e consultado por
         alguem, ou se e residuo.
```
