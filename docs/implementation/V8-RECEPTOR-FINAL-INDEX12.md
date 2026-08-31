# V8 · MEDIÇÃO FINAL DE RECEPTORES — CASCO INDEX (12)

**Data:** 2026-08-31 · medição executável em `data/implementation/V8-RECEPTOR-FINAL.json`

```
READ ONLY · NO COLLECTION · NO REAL DATA · NO SUPABASE WIRING
NO HTML PATCH · NO DESIGN CHANGE
```

> Antecessores: `V8-RECEPTOR-COVERAGE-AUDIT.md` (index 10) e
> `V8-RECEPTOR-REAUDIT-INDEX11.md` (index 11). Os três documentos ficam: sem eles não
> há como mostrar o que mudou.

---

## 0 · O CASCO MEDIDO

```
arquivo ... casco/canonical/SINTONIA-EAME-V8-FINAL.html
origem .... index (12).html · 1.521.561 bytes
sha-256 ... b12ad20ebba85277e32819f3a7f35279c6af22c870c3c956ae10ff8eb42d8a66
camada de dados ... 89.176 bytes
telas ..... home · radar · obj · acervo · fontes · relatorios · eame · lib · config
```

**Quatro testemunhas coexistem byte a byte:** V7, index (10), index (11), index (12).

---

## 1 · O QUE FECHOU

Nove dos doze bloqueadores do index (11) foram fechados. Não é elogio de cortesia — é o
que os bytes mostram.

**As nove mangueiras têm receptor com nome canônico. `9/9`.**

| # | `HOSE_ID` | `CANONICAL_PAYLOAD_TYPE` |
|---|---|---|
| H1 | `H1` | `TERRITORIAL_OBSERVATION` |
| H2 | `H2` | `REGISTRATION_DEADLINE` |
| H3 | `H3` | `COMPETITOR_PRODUCT_IDENTITY` |
| H4 | `H4` | `OBSERVED_PAID_ACTIVITY` |
| H5 | `H5` | `FIELD_PRESSURE_SERIES` |
| H6 | `H6` | `PERSON_CREATOR \| FARM_BUSINESS_ENTITY \| CREATOR_CONTENT_PROFILE` |
| H7 | `H7` | `SCIENTIFIC_PERSON` |
| H8 | `H8` | `COMPANY_LOCAL_ACCOUNT` |
| H9 | `H9` | `CONTENT_ENTITY \| CONTENT_TRANSLATION \| ONTOLOGY_TERM` |

**Os oito aliases do index (11) sumiram como tipo.** `TERRITORIAL_ATTENTION_OBJECT`,
`PAID_ACTIVITY_EVIDENCE`, `LONGITUDINAL_FIELD_SERIES`, `ISSUE_EXPERT`,
`COMPANY_PUBLIC_ACCOUNT`, `MULTILINGUAL_CONTENT_REPRESENTATION` não existem mais. E os
dois `OBJECT_TYPE` que tinham sido usados como payload voltaram ao lugar certo.

**H6 ganhou receptor formal.** `R-H6-CREATOR`, `HOSE_ID = H6`, os três payloads canônicos,
`ENTRY_PATH` com os dois valores, `ROW_COUNT` e `ENTITY_COUNT` separados, e a lei escrita
no `failClosed`: *"nunca somam pessoas com negócios agrícolas"*.

**A gaveta alcança as nove.** Dez evidências, `EV-0001` a `EV-0010`, nove fontes distintas,
os dois backends exercidos, três com tradução. `EV-0007` e `EV-0009` chegam com
`lang: 'UNKNOWN'` — que é o valor certo, não um traço.

**Zero handlers mortos.** O `openDrawer` órfão saiu. O Radar abre evidência pelo mesmo
`l.openEvidence` do Object Detail.

**Radar e Object Detail têm paridade de convergência.** Os oito campos, iguais nas duas
telas. E a conta continua derivada:

```js
const independentCount = CONV_LEGS.filter(l => l.independence === 'INDEPENDENT').length;
```

Duas pernas — `TERRITORIAL` independente, `FIELD_HISTORICAL` dependente por
`SOURCE_DEPENDENCY` — produzem **`SINGLE SIGNAL · 1 FAMÍLIA`** nas duas superfícies.

**`ACTION_TYPE` separou canônico de exibição:**

```js
const KIND = {
  business: { canonical: 'BUSINESS_DECISION', display: 'BUSINESS', ... },
  invest:   { canonical: 'INVESTIGATION',     display: 'INVESTIGATION', ... },
  system:   { canonical: 'SYSTEM_DECISION',   display: 'SYSTEM', ... }
};
...
actionType: KIND[a.kind].canonical,   kind: KIND[a.kind].display,   objectId: base.id,
```

`OBJECT_ID` entrou. O guard de `EVIDENCE_BASIS` continua executável.

**Timeline tipada por inteiro.** Nove campos, `STATE_BEFORE` e `STATE_AFTER` separados,
`SOURCE_ID` tipado, e **nenhuma seta concatenada** no armazenamento.

**`SOURCE_CLOCKS` deixou de ser `H0`** e virou `INFRA` — infraestrutura transversal, como
devia.

**Mapa, proveniência e segredo:** o guard do `crop-map.js` continua, todos os pontos em
`NOT_KNOWN`, nenhum desenhado. Os dois envelopes de proveniência íntegros, renderizados
pelo mesmo componente. Nenhum segredo nos bytes.

---

## 2 · O QUE NÃO FECHOU — TRÊS ITENS

### 2.1 · O helper ainda expõe o rótulo no lugar do `HOSE_ID`

O briefing nomeou esta linha como reprovação explícita. Ela continua:

```js
const receptor = (r) => ({
  receptorId: r.id, hoseId: r.displayLabel || r.hose, ...
```

**E ela morde.** Os três subreceptores definem `displayLabel`, então `{{ r.hoseId }}` —
que é o que o markup renderiza, três vezes — entrega:

```
H7 · CIÊNCIA        em vez de   H7
H2 · PORTFÓLIO      em vez de   H2
H6 · CAMPO          em vez de   H6
```

O `HOSE_ID` canônico **existe no dado** (`hose: 'H7'`) e **não é o que o receptor expõe**.
Um adapter que leia `hoseId` recebe a etiqueta da porta, não o número dela — e ninguém
casa `"H7 · CIÊNCIA"` com `"H7"` sem fatiar uma string.

> A correção é uma linha: `hoseId: r.hose` e `displayLabel: r.displayLabel || r.hose` como
> campo separado.

### 2.2 · `PARENT_HOSE_ID` é texto dentro de `note`

```js
note: r.typeNote ? r.note + ' · ' + r.typeNote
                 : (r.parent ? r.note + ' · PARENT_HOSE_ID · ' + r.parent : r.note),
```

O campo `parentHoseId` **não existe** — nem na camada de dados, nem no markup. O valor
correto (`H7`, `H2`, `H6`) está lá, concatenado numa frase de prosa.

O briefing foi literal: *"PARENT_HOSE_ID precisa ser campo estrutural, não texto dentro de
note."*

### 2.3 · `SOURCE_LANGUAGE` cai em `—` em dois dos três payloads textuais

A regra global vale em **1 de 3**:

| receptor | expressão | resultado |
|---|---|---|
| `R-H9-CONTENT-ENTITY` | `(base.srcLang \|\| 'unknown').toUpperCase()` | ✅ `UNKNOWN` |
| `R-H7-SCIENTIFIC-PUBLICATION` | `null` | ❌ `—` |
| `R-H6-FIELD-VOICE` | `null` | ❌ `—` |

A causa é uma linha só, e é a mesma para os dois:

```js
const FIELD = (k, v, st) => ({ k, v: v == null ? '—' : v, ... });
```

`null` vira traço por padrão. **O briefing nomeou exatamente estes dois payloads.** E o
traço não está no vocabulário fechado — `pt · en · es · fr · it · MULTILINGUAL · UNKNOWN`.

> Um traço diz *"não tem valor aqui"*. `UNKNOWN` diz *"não sabemos qual é"*. São coisas
> diferentes, e o produto inteiro depende dessa diferença.

---

## 3 · ÓRFÃS: ZERO, E O QUE ZERO NÃO SIGNIFICA

```
ORPHAN_CANONICAL_INTELLIGENCE_OUTPUTS ....... 0
OUTPUTS_WITH_ABSENT_RECEPTOR ................ 0    (eram 10, depois 2)
```

**Nenhuma saída canônica aponta para receptor ausente.** O estado `ABSENT` saiu do
inventário.

E nenhuma classificação foi mexida para chegar lá: as quatro classes têm exatamente as
mesmas contagens das duas rodadas anteriores — **21 / 8 / 5 / 1**. Há teste que reprova se
alguma se mover.

**Mas zero órfã não é casco pronto.** Três receptores têm o dado canônico e **expõem a
etiqueta errada**. O destino existe; a placa na porta está trocada. Isso está escrito no
próprio inventário, no campo `O_QUE_ZERO_AQUI_NAO_SIGNIFICA`, para que ninguém leia o zero
sozinho.

---

## 4 · A DISTÂNCIA REAL

```
index (10)   0/9 receptores · 6 receptores ausentes · gaveta global
index (11)   0/9 pelo nome · 8/9 envelope · H6 ausente · Radar atrasado
index (12)   9/9 · gaveta 9/9 · zero handler morto · zero órfã
             e três itens: uma linha de helper, um campo, e um default
```

**Dois dos três blockers são a mesma linha do helper `receptor()`.** O terceiro é o default
do helper `FIELD()` aplicado a dois campos.

---

## 5 · PROVAS

`tests/test_v8_receptors_final.py` — **46 provas**, dentro das
<!--M:TEST_COUNT_CURRENT-->913<!--/M--> da suíte, 0 falhas. As 713 anteriores preservadas.

As provas travam a medição, não aprovam o casco. Quando um item for corrigido, a prova
correspondente reprova — obrigando a remedir.

### Dois erros meus, nesta rodada

**No extrator:** `load: '` casava **dentro** de `payload: '`, e o estado de carga virava o
nome do payload — o que fez as nove mangueiras aparecerem como FAIL numa primeira leitura.
E a indentação do bloco de H9 escapava do regex, sumindo com o receptor. Corrigidos, com a
armadilha escrita no código.

**No teste:** procurei `ISSUE_EXPERT` como pedaço de texto e casei com
`ISSUE_EXPERTISE_PROVED` — que é o portão **certo** e tem de ficar. **Quarta vez** que
confundo menção com uso (antes: `apify`, `READY`, `key`). O teste agora compara o **valor**
do payload, e o motivo está escrito nele.

---

## 6 · SAÍDA

```
CASCO_WITNESS = casco/canonical/SINTONIA-EAME-V8-FINAL.html
SHA256 = b12ad20ebba85277e32819f3a7f35279c6af22c870c3c956ae10ff8eb42d8a66

H1 = PASS    H4 = PASS    H7 = PASS
H2 = PASS    H5 = PASS    H8 = PASS
H3 = PASS    H6 = PASS    H9 = PASS

HOSES_WITH_COMPLETE_RECEIVER = 9/9

H6_RECEIVER = PASS · R-H6-CREATOR · HOSE_ID = H6
H6_THREE_CANONICAL_PAYLOADS = PASS

SCIENCE_PUBLICATION_RECEIVER   = PRESENTE · payload e hose canônicos · exposição FAIL
LOCAL_ADAMA_PORTFOLIO_RECEIVER = PRESENTE · payload e hose canônicos · exposição FAIL
FIELD_VOICE_RECEIVER           = PRESENTE · payload e hose canônicos · exposição FAIL

SUBRECEPTOR_HOSE_ID_CANONICAL = PASS no dado · FAIL no que o receptor expõe
PARENT_HOSE_ID_STRUCTURAL     = FAIL · concatenado em note

RADAR_CONVERGENCE_PARITY = PASS
DEAD_HANDLERS = 0

EVIDENCE_DRAWER_HOSES_COVERED = 9/9

ACTION_TYPE_CANONICAL = PASS
ACTION_MAP_OBJECT_ID  = PASS

TIMELINE_STATE_BEFORE_TYPED = PASS
TIMELINE_STATE_AFTER_TYPED  = PASS
TIMELINE_SOURCE_ID_TYPED    = PASS

CREATOR_ENTITY_KIND_CANONICAL  = PASS
SOURCE_LANGUAGE_UNKNOWN_GLOBAL = FAIL · 1 de 3 payloads textuais

GITHUB_PROVENANCE   = PASS
SUPABASE_PROVENANCE = PASS
CROP_MAP_GUARD      = PASS

ORPHAN_CANONICAL_INTELLIGENCE_OUTPUTS = 0
OUTPUTS_WITH_ABSENT_RECEPTOR          = 0

TESTS_TOTAL = 759      TESTS_FAILED = 0

DESIGN_PATCH_REQUIRED = YES
CASCO_RECEPTOR_READY  = NO

READY_TO_CREATE_SUPABASE_INSTANCE_SCHEMA = YES
READY_FOR_FIRST_SHADOW_LOAD = NO
READY_TO_WIRE_REAL_DATA     = NO
```

### `EXACT_BLOCKERS`

```
1  helper receptor(): hoseId: r.displayLabel || r.hose
   → hoseId: r.hose, e displayLabel como campo separado

2  PARENT_HOSE_ID concatenado em note
   → campo parentHoseId no receptor, renderizado como campo

3  SOURCE_LANGUAGE = null em R-H7-SCIENTIFIC-PUBLICATION e R-H6-FIELD-VOICE
   → 'UNKNOWN', como já faz R-H9-CONTENT-ENTITY
```

**Os três são no helper, não no desenho.** Nenhum pede tela nova, cor nova ou hierarquia
nova. E `READY_FOR_FIRST_SHADOW_LOAD` continua `NO` por motivo próprio, independente do
casco: o commit de H2 ainda é uma branch e a migration não foi aplicada.
