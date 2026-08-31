# V8 · MICRO-REAUDITORIA FINAL — CASCO DE DEPLOY

**Data:** 2026-08-31 · medição executável em `data/implementation/V8-RECEPTOR-READY.json`

```
READ ONLY · NO COLLECTION · NO SUPABASE WIRING · NO REAL DATA
NO HTML PATCH · NO DESIGN CHANGE
```

> Antecessores: index (10), index (11), index (12). Os quatro documentos ficam: sem eles
> não há como mostrar o caminho.

---

## 0 · O CASCO MUDOU DE FORMATO

Este export **não é mais um HTML único empacotado**. É uma pasta de deploy:

```
deploy/index.html      372.418 bytes   markup + lógica (data-dc-script)
deploy/support.js       69.150 bytes   runtime gerado (dc-runtime)
deploy/crop-map.js      10.156 bytes   componente do mapa
deploy/vercel.json          23 bytes
deploy/_ds/ · deploy/assets/           design system, fontes, ícones
```

**Verifiquei se a lógica está duplicada — não está.** `support.js` é o runtime gerado
(*"GENERATED from dc-runtime/src/*.ts — do not edit"*), sem `const receptor`, sem
`CONV_LEGS`, sem o mapa de evidências. A lógica do app vive **só** no bloco
`data-dc-script` do `index.html`. Duas cópias divergiriam; não há duas.

### Custódia

```
zip ............ 7917564b64a99816cfe0dc3aa671be2e0092c6eb5e2fd2c557a4707766128efc
index.html ..... a103bd62e3bbe92cbd56dd5b0da43a878fe4244db7bfbf89d683eaea8b024dc8
support.js ..... 8fe7df74405f3c55f49b7249c74ea1397e65d07dea2b1bd3b4a489bec2e28cbe
crop-map.js .... a55c6011e6aadb014b2617c8f5b302d9d2fb4bbfb1ee3e444cad345bbb1614c8
```

⚠️ **O `index.html` está guardado GZIPADO**, como `deploy-index.html.gz`. Neste ambiente o
antivírus prende o arquivo logo após a escrita — `ls` mostra, `sha256sum` responde
*"Permission denied"*, e nem o Git conseguiria lê-lo. O SHA-256 registrado é o dos bytes
**descomprimidos**, e há teste que descomprime e confere. Guardei o `.gz` em vez de
inventar um contorno silencioso.

**Fora da testemunha, de propósito:** fontes e imagens do design system (1,2 MB). Não são
receptores, e nenhum byte delas prova algo sobre recepção.

---

## 1 · OS TRÊS BLOQUEADORES FECHARAM

### 1.1 · `HOSE_ID` canônico, `DISPLAY_LABEL` separado

```js
const receptor = (r) => ({
  receptorId: r.id,
  hoseId: r.hose,                          // HOSE_ID estrutural/canônico
  parentHoseId: r.parent || null,          // PARENT_HOSE_ID estrutural
  displayLabel: r.displayLabel || r.hose,  // apenas apresentação
  ...
```

`hoseId: r.displayLabel || r.hose` **não existe mais**. Os três subreceptores agora expõem:

| receptor | `HOSE_ID` | `DISPLAY_LABEL` |
|---|---|---|
| `R-H7-SCIENTIFIC-PUBLICATION` | `H7` | `H7 · CIÊNCIA` |
| `R-H2-LOCAL-ADAMA-PORTFOLIO` | `H2` | `H2 · PORTFÓLIO` |
| `R-H6-FIELD-VOICE` | `H6` | `H6 · CAMPO` |

O rótulo bonito continua na tela; o número casa com o contrato. **`PASS`**

### 1.2 · `PARENT_HOSE_ID` estrutural

`parentHoseId: r.parent || null` é campo do receptor. E vai além do pedido — o helper
também injeta uma linha de campo visível:

```js
fields: (r.parent ? [{ k: 'PARENT_HOSE_ID', v: r.parent, ... }] : []).concat(r.fields)
```

A concatenação em `note` sumiu. Ninguém precisa fatiar uma frase para achar o pai. **`PASS`**

### 1.3 · `SOURCE_LANGUAGE = UNKNOWN` nos três payloads textuais

| receptor | expressão | resultado |
|---|---|---|
| `R-H9-CONTENT-ENTITY` | `(base.srcLang \|\| 'unknown').toUpperCase()` | `UNKNOWN` |
| `R-H7-SCIENTIFIC-PUBLICATION` | `'UNKNOWN'` | `UNKNOWN` |
| `R-H6-FIELD-VOICE` | `'UNKNOWN'` | `UNKNOWN` |

Nenhum cai em `—`. **`PASS`**

---

## 2 · NENHUMA REGRESSÃO

Todos os `PASS` do index (12) foram medidos de novo e continuam:

```
HOSES_WITH_COMPLETE_RECEIVER .......... 9/9
EVIDENCE_DRAWER_HOSES_COVERED ......... 9/9
DEAD_HANDLERS .........................   0
RADAR_CONVERGENCE_PARITY .............. PASS
ACTION_TYPE_CANONICAL ................. PASS
ACTION_MAP_OBJECT_ID .................. PASS
TIMELINE_TYPED (9 campos, sem seta) ... PASS
GITHUB_PROVENANCE ..................... PASS
SUPABASE_PROVENANCE ................... PASS
CROP_MAP_GUARD ........................ PASS
NO_FRONTEND_SECRET .................... PASS
```

A convergência continua derivada, e as duas telas continuam produzindo o mesmo resultado:
`TERRITORIAL` independente + `FIELD_HISTORICAL` dependente por `SOURCE_DEPENDENCY` =
**`SINGLE SIGNAL · 1 FAMÍLIA`**.

H6 preservado: `R-H6-CREATOR`, `HOSE_ID = H6`, os três payloads canônicos, `ENTRY_PATH` com
os dois valores.

---

## 3 · O QUE SOBROU — UM ITEM, E É O QUE VOCÊ MANDOU MEDIR LITERALMENTE

`FIELD_VOICE_ENTITY_KIND_CANONICAL = **FAIL**`

```
R-H6-CREATOR       ENTITY_KIND = PERSON_CREATOR | FARM_BUSINESS_ENTITY   ✅
R-H6-FIELD-VOICE   ENTITY_KIND = PERSON_CREATOR | FARM_BUSINESS          ❌
```

**Não assumi equivalência.** Fui procurar a autoridade, como o briefing pediu.

### A autoridade

`data/supabase/SUPABASE-CANONICAL-SCHEMA.json`:

```json
"creator_entity_kind": ["PERSON_CREATOR", "FARM_BUSINESS_ENTITY"]
```

E a coluna que recebe esse vocabulário é exatamente a de `FIELD_VOICE_OBSERVATION`:

```json
{"name": "entity_kind", "type": "creator_entity_kind", "null": false}
```

### E `FARM_BUSINESS`?

Aparece **uma vez** no repositório inteiro como valor — no `UI_ALIAS_MAP`, marcado como
alias de apresentação do index (11):

```json
{"CANONICAL": "FARM_BUSINESS_ENTITY", "HOSE_ID": "H6", "UI_ALIAS_INDEX11": "FARM_BUSINESS"}
```

**Não existe autoridade que faça `FARM_BUSINESS` um enum canônico distinto.** É o alias, e
o alias não substitui o tipo.

> Vale notar o que **já** foi corrigido: a lista visível de vozes (`voices[]`) usa
> `ENTITY_KIND · FARM_BUSINESS_ENTITY`. A divergência ficou só no receptor de observação —
> um lugar, uma string.

### Por que isso importa e não é implicância

A separação pessoa / negócio é a coisa mais difícil que este produto acertou, e é ela que
impede a soma proibida. Se o receptor de observação aceitar um nome e o receptor de
entidade aceitar outro, o adapter que ligar os dois vai precisar traduzir — e é numa
tradução dessas que `PERSON_CREATOR` e `FARM_BUSINESS_ENTITY` voltam a virar um número só
chamado *creators*.

---

## 4 · PROVAS

`tests/test_v8_receptor_ready.py` — **27 provas**, dentro das
<!--M:TEST_COUNT_CURRENT-->924<!--/M--> da suíte, 0 falhas. As 759 anteriores preservadas.

Inclui prova de que o `.gz` devolve os bytes originais, e de que `support.js` é runtime e
não uma segunda cópia da lógica.

---

## 5 · SAÍDA

```
CASCO_WITNESS = casco/canonical/deploy-v8-receptor-ready/
                deploy-index.html.gz · support.js · crop-map.js · vercel.json
SHA256 (index.html descomprimido) =
                a103bd62e3bbe92cbd56dd5b0da43a878fe4244db7bfbf89d683eaea8b024dc8
SHA256 (zip) =  7917564b64a99816cfe0dc3aa671be2e0092c6eb5e2fd2c557a4707766128efc

H1 = PASS   H2 = PASS   H3 = PASS   H4 = PASS   H5 = PASS
H6 = PASS   H7 = PASS   H8 = PASS   H9 = PASS

HOSES_WITH_COMPLETE_RECEIVER = 9/9

SUBRECEPTOR_HOSE_ID_CANONICAL = PASS
DISPLAY_LABEL_SEPARATE        = PASS
PARENT_HOSE_ID_STRUCTURAL     = PASS

SOURCE_LANGUAGE_UNKNOWN_GLOBAL = PASS

FIELD_VOICE_ENTITY_KIND_CANONICAL = FAIL

RADAR_CONVERGENCE_PARITY = PASS
DEAD_HANDLERS = 0

EVIDENCE_DRAWER_HOSES_COVERED = 9/9

ACTION_TYPE_CANONICAL = PASS
ACTION_MAP_OBJECT_ID  = PASS

TIMELINE_TYPED      = PASS
GITHUB_PROVENANCE   = PASS
SUPABASE_PROVENANCE = PASS
CROP_MAP_GUARD      = PASS

ORPHAN_CANONICAL_INTELLIGENCE_OUTPUTS = 0
OUTPUTS_WITH_ABSENT_RECEPTOR          = 0

TESTS_TOTAL = 786      TESTS_FAILED = 0

DESIGN_PATCH_REQUIRED = YES
CASCO_RECEPTOR_READY  = NO

READY_TO_CREATE_SUPABASE_INSTANCE_SCHEMA = YES
READY_FOR_FIRST_SHADOW_LOAD = NO
READY_TO_WIRE_REAL_DATA     = NO
```

### `EXACT_BLOCKERS`

```
1  R-H6-FIELD-VOICE :: ENTITY_KIND = 'PERSON_CREATOR | FARM_BUSINESS'
   → 'PERSON_CREATOR | FARM_BUSINESS_ENTITY'
   autoridade: SUPABASE-CANONICAL-SCHEMA.json :: VOCABULARIES.creator_entity_kind
```

**Um item. Uma string.** Nenhum desenho, nenhuma tela, nenhuma cor.

E `READY_FOR_FIRST_SHADOW_LOAD` continua `NO` por motivo próprio, que não tem nada a ver
com o casco: o commit de H2 ainda é uma branch e a migration não foi aplicada.
