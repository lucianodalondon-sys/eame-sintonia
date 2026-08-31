# V8 · REAUDITORIA DE RECEPTORES — CASCO DATA-READY

**Data:** 2026-08-31 · medição executável em `data/implementation/V8-RECEPTOR-REAUDIT.json`

```
READ_ONLY = SIM    COLETA = NENHUMA    DADO REAL LIGADO = NÃO
SUPABASE IMPLEMENTADO = NÃO    DESIGN ALTERADO = NÃO    HTML EDITADO À MÃO = NÃO
```

> A auditoria anterior (`V8-RECEPTOR-COVERAGE-AUDIT.md`) mediu o `index (10)` e pediu treze
> patches. Este documento mede o `index (11)`, que é o export **depois** do patch.

---

## 0 · O CASCO MEDIDO

```
arquivo ... casco/canonical/SINTONIA-EAME-V8-DATA-READY.html
origem .... index (11).html · 1.513.823 bytes
sha-256 ... 774ce0fbf3cdc567d95df872bd4299c89f5f46dfcede977a68387021abe6968a
camada de dados ... 84.203 bytes (era 53.786 — cresceu 57%)
telas ..... home · radar · obj · acervo · fontes · relatorios · eame · lib · config
```

**As três testemunhas coexistem** e nenhuma foi tocada: V7, `index (10)` (o antes) e
`index (11)` (o depois). Apagar o anterior apagaria a prova de que o patch mudou alguma
coisa.

---

## 1 · O QUE MUDOU DE VERDADE

O patch foi aplicado, e a maior parte dele **funciona**. Isto não é elogio de cortesia —
é o que os bytes mostram:

- **Existe envelope de receptor.** Uma função `receptor()` produz `RECEPTOR_ID`, `HOSE_ID`,
  `CANONICAL_PAYLOAD_TYPE`, `LOAD_STATE`, `NO_DATA_REASON`, `PROVENANCE`,
  `EVIDENCE_POINTERS`, `AS_OF_DATE` e `FAIL_CLOSED_REASON`. **Onze receptores** usam.
- **Os oito estados de carga existem**, cada um com definição própria e traço distinto.
- **Proveniência é registro, não frase.** `provGithub` e `provSupabase` com os campos
  exatos, e **um único componente** `r.prov` renderiza os dois.
- **A gaveta virou por evidência.** `drawerRef: {objectId, hoseId, evidenceId}`, seis
  evidências com fonte e backend próprios. **`showOriginal` e `showTranslation` têm
  handler de verdade** — os botões desenhados viraram botões.
- **`DEPENDENCY_RELATION` entrou**, e o cálculo funciona: duas pernas, uma independente,
  resultado `SINGLE SIGNAL`.
- **`EVIDENCE_BASIS` entrou como guard executável**, não como texto fixo.
- **O portão de expertise virou código:** sem prova, o rótulo é `PESSOA RELACIONADA`.
- **H8 existe** com `CONTENT_COLLECTION_STAGE = NOT_STARTED` e a lei escrita no motivo.
- **O guard do mapa é real** — e está no asset `crop-map.js`, não no casco:
  `points.filter(p => p.GEO_RESOLUTION === 'POINT' && Array.isArray(p.LOCALITY_OR_GEOMETRY))`,
  com o comentário *"LOCALITY_TEXT nunca é geocodificado silenciosamente"* e um contador de
  não-desenháveis na tela. Todos os pontos estão em `NOT_KNOWN`: **nenhum é desenhado.**

**Oito das nove mangueiras têm envelope completo.** Isso é a distância real percorrida.

---

## 2 · E POR QUE MESMO ASSIM O VEREDITO É 0/9

Pela regra que o próprio briefing fixou: **alias sem mapa é FAIL.**

```
HOSES_WITH_COMPLETE_ENVELOPE ......... 8 / 9
HOSES_WITH_CANONICAL_PAYLOAD_NAME .... 0 / 9
HOSES_WITH_COMPLETE_RECEIVER ......... 0 / 9
```

**Os três números medem coisas diferentes e nenhum substitui o outro.** Publicar só o
primeiro esconderia que duas ontologias passaram a coexistir; publicar só o terceiro
esconderia que falta uma linha de código para oito delas.

### 2.1 · Os oito nomes que driftaram

| mangueira | canônico (FINAL-HOSE-MAP) | declarado no casco |
|---|---|---|
| **H1** | `TERRITORIAL_OBSERVATION` | `TERRITORIAL_ATTENTION_OBJECT` |
| **H2** | `REGISTRATION_DEADLINE` | `REGULATORY_DEADLINE` |
| **H3** | `COMPETITOR_PRODUCT_IDENTITY` | `COMPETITOR_IDENTITY_CHAIN` |
| **H4** | `OBSERVED_PAID_ACTIVITY` | `PAID_ACTIVITY_EVIDENCE` |
| **H5** | `FIELD_PRESSURE_SERIES` | `LONGITUDINAL_FIELD_SERIES` |
| **H7** | `SCIENTIFIC_PERSON` | `ISSUE_EXPERT` |
| **H8** | `COMPANY_LOCAL_ACCOUNT` | `COMPANY_PUBLIC_ACCOUNT` |
| **H9** | `CONTENT_ENTITY` + `CONTENT_TRANSLATION` + `ONTOLOGY_TERM` | `MULTILINGUAL_CONTENT_REPRESENTATION` |

**`ADAPTER_ALIAS_MAP` não existe** — nem no casco, nem no markup. Sem ele, o nome do tipo
do produto e o nome do tipo do casco divergem **em silêncio**, e um adapter futuro liga o
cano errado sem ninguém perceber.

Note o padrão: `H2`, `H3` e `H4` não inventaram nomes — pegaram o **OBJECT_TYPE** e o
usaram como **CANONICAL_PAYLOAD_TYPE**. São coisas diferentes: `REGULATORY_DEADLINE` é o
tipo do objeto de atenção; `REGISTRATION_DEADLINE` é o que a mangueira carrega.

> **Uma linha resolve oito:** um `ADAPTER_ALIAS_MAP` explícito e unívoco, ou os nomes
> canônicos direto. Qualquer um dos dois; não os dois pela metade.

---

## 3 · H6 — A ÚNICA MANGUEIRA SEM RECEPTOR NENHUM

`H6_RECEPTOR_IMPLEMENTED = **FAIL**`

O casco tem tudo o que foi pedido em `voices[]`:

```
ENTITY_KIND · PERSON_CREATOR        ENTITY_KIND · FARM_BUSINESS
ENTITY_ID · DISPLAY_NAME · RELATION_TO_CROP_REGION
ENTRY_PATH (comutável entre FROM_ATTENTION_OBJECT e FROM_CROP_REGION_SEARCH)
GDPR_TREATMENT_STATE · ROW_COUNT / ENTITY_COUNT · CONTENT_PROFILE_REF · LAST_OBSERVED_AT
```

**E `voices[]` não é um receptor.** Não tem `RECEPTOR_ID`, `LOAD_STATE`, `NO_DATA_REASON`,
`PROVENANCE`, `EVIDENCE_POINTERS`, `AS_OF_DATE` nem `FAIL_CLOSED_REASON`. **Nenhum
receptor no casco declara `HOSE_ID = H6`.**

A diferença não é burocrática: uma lista com os campos certos **não sabe dizer por que está
vazia**. Não distingue "nunca liguei" de "consultei e não há" de "a coleta não começou" —
e essa distinção é a razão de o envelope existir.

Os três payloads canônicos de H6 continuam sem destino:

```
PERSON_CREATOR · FARM_BUSINESS_ENTITY · CREATOR_CONTENT_PROFILE
```

`FARM_BUSINESS_ENTITY` aparece como `FARM_BUSINESS` (abreviado) e `CREATOR_CONTENT_PROFILE`
não aparece em lugar nenhum — só `CONTENT_PROFILE_REF`, que é um ponteiro, não o tipo.

---

## 4 · OS TRÊS SUBRECEPTORES: PAYLOAD CERTO, MANGUEIRA ERRADA

Os **nomes de payload estão canônicos** — `SCIENTIFIC_PUBLICATION`,
`LOCAL_ADAMA_PORTFOLIO_CONTEXT`, `FIELD_VOICE_OBSERVATION`. Este é o único lugar do casco
onde os nomes não driftaram, e é justamente onde o drift seria mais perigoso.

E as duas leis estão escritas dentro dos próprios receptores:

```
SCIENTIFIC_PERSON ≠ SCIENTIFIC_PUBLICATION
REGISTRATION_DEADLINE ≠ LOCAL_ADAMA_PORTFOLIO_CONTEXT
```

**O `HOSE_ID` é que saiu do vocabulário:**

| receptor | `HOSE_ID` declarado | deveria ser |
|---|---|---|
| `RECEPTOR_SCIENTIFIC_PUBLICATION` | `H7·CIÊNCIA` | `HOSE_ID` em H1..H9 + `PARENT_HOSE_ID = H7` |
| `RECEPTOR_LOCAL_ADAMA_PORTFOLIO` | `H2·PORTFÓLIO` | `PARENT_HOSE_ID = H2` |
| `RECEPTOR_FIELD_VOICE_OBSERVATION` | `H6·CAMPO` | `PARENT_HOSE_ID = H6` |
| `RECEPTOR_SOURCE_CLOCKS` | `H0` | `H0` não existe no mapa de mangueiras |

**`PARENT_HOSE_ID` não existe no casco.** O briefing aceitava `H7·CIÊNCIA` *só* com o
campo pai separado. Sem ele, `H7·CIÊNCIA` é uma string que nenhum adapter consegue casar
com `H7`.

`SUBRECEPTOR_PARENT_HOSE_DRIFT = **FAIL**`

---

## 5 · O RADAR FICOU PARA TRÁS DO OBJECT DETAIL

Esta é a descoberta que mais importa desta rodada, porque não estava na lista de patches.

**O patch foi aplicado ao Object Detail e não ao Radar.** Os dois renderizam a mesma
convergência, com leis diferentes:

| campo | Object Detail | Radar |
|---|---|---|
| `conv.propositionId` | ✅ | ❌ |
| `conv.kind` (`CONVERGENCE_KIND`) | ✅ | ❌ |
| `conv.independentCount` | ✅ | ❌ |
| `l.dependency` (`DEPENDENCY_RELATION`) | ✅ | ❌ |
| `l.dependencyNote` | ✅ | ❌ |
| abrir evidência | `l.openEvidence` ✅ | `openDrawer` ❌ **morto** |

**`openDrawer` foi removido de `renderVals()` e continua no markup do Radar.** É um `<span>`
com `cursor:pointer`, texto *"ver evidência original"* e nenhuma ação. Um usuário no Radar
clica e nada acontece.

> É a mesma classe de defeito do *ranking de recorrência* do V7 e dos botões de tradução do
> `index (10)`: parece vivo e não está ligado. **Terceira vez.** Vale uma verificação de
> handlers mortos antes de cada export — está automatizada em
> `scripts/v8_receptor_reaudit.py`, comparando o que o markup chama com o que `renderVals()`
> devolve.

`BLOCK_PARITY_RADAR_OBJ = **FAIL**` · `DEAD_HANDLERS = **FAIL**`

---

## 6 · A GAVETA ALCANÇA CINCO DAS NOVE

O defeito antigo **foi corrigido**: a gaveta agora é por evidência, e abrir `EV-0001` e
`EV-0002` muda `OBJECT_ID`, `HOSE_ID`, `EVIDENCE_ID`, `CLAIM_TEXT`, `SOURCE_ID` e
`SOURCE_BACKEND`.

```
EV-0001 · H1 · SRC-0001 · GITHUB   · ES · sem tradução
EV-0002 · H2 · SRC-0002 · GITHUB   · ES · COM tradução
EV-0003 · H3 · SRC-0003 · SUPABASE · EN
EV-0004 · H4 · SRC-0004 · SUPABASE · ES
EV-0005 · H1 · SRC-0005 · GITHUB   · ES
EV-0006 · H5 · SRC-0001 · GITHUB   · ES   ← mesma fonte de EV-0001: é a dependência
```

Os dois backends são exercidos, e a mesma UI renderiza os dois. `ORIGINAL_TEXT` e
`TRANSLATED_TEXT` são campos separados, com `TRANSLATION_PROVENANCE` próprio e o rótulo
*"TRADUÇÃO — NÃO SUBSTITUI O ORIGINAL"*.

**Mas o mapa de evidências só cobre H1 a H5.** H6, H7, H8 e H9 não têm nenhuma entrada —
nenhuma afirmação dessas quatro mangueiras chega ao original.

`EVIDENCE_DRAWER_TRACES_ALL_HOSES = **FAIL** (5/9)`

---

## 7 · AÇÕES: O GUARD ENTROU, O VOCABULÁRIO NÃO

O guard é código executável e está certo:

```js
action: (a.kind === 'business' && (!a.basis || !a.basis.length))
  ? 'SEM AÇÃO DEFENSÁVEL AINDA' : a.action
```

E `EVIDENCE_BASIS` viaja em cada linha, com `EVIDENCE_BASIS VAZIO` quando não há.

**O que persiste é o rótulo, não o valor canônico:**

```
persistido no casco ... BUSINESS · INVESTIGATION · SYSTEM
canônico .............. BUSINESS_DECISION · SYSTEM_DECISION · INVESTIGATION
DISPLAY_ACTION_TYPE ... não existe
```

`INVESTIGATION` coincide; `BUSINESS` e `SYSTEM` não. `ACTION_TYPE_CANONICAL_DRIFT = **FAIL**`

E **`OBJECT_ID` não chega ao mapa de ações**: nenhuma ação diz a que objeto pertence.

---

## 8 · TIMELINE E MAPA

**Timeline — tipada, com duas ressalvas.** Entraram `EVENT_ID`, `EVENT_TYPE`, `EVENT_AT`
(ISO real, `null` quando não há), `EVENT_AT_RESOLUTION`, `OBSERVATION_ID` e `GAP_REASON`. O
vazio temporal continua sendo um evento, com trilho tracejado — está certo.

- `STATE_BEFORE` e `STATE_AFTER` existem no dado e chegam **concatenados** numa linha só
  (`FORMING → ATTENTION_CANDIDATE_TEST`). Não dá para renderizar os dois separados.
- `SOURCE_ID` aparece como texto de exibição, não como campo tipado.

**Mapa — tipado e com o guard no lugar certo.** Os doze campos por ponto existem, e o
`crop-map.js` recusa qualquer ponto que não tenha `GEO_RESOLUTION = POINT` **e** geometria
em array. Com todos os pontos em `NOT_KNOWN`, nenhum é desenhado, e a tela declara quantos
ficaram de fora. `mapHoles` continua intacto.

---

## 9 · ÓRFÃS

```
ORPHAN_CANONICAL_INTELLIGENCE_OUTPUTS ........  0
SAÍDAS COM RECEPTOR AUSENTE ..................  2   (eram 10)
RECEPTORES AUSENTES ..........................  1   (eram 6)
```

**As duas saídas restantes apontam para o mesmo receptor: H6.** São `CREATOR_LAST_90D +
CREATOR_READINESS` e `SPEAKER_UNIVERSE + filas de voz pública`.

Nenhuma classificação foi mexida para chegar a zero: as quatro classes têm exatamente as
mesmas contagens do inventário anterior (21 / 8 / 5 / 1). **Só o estado do receptor mudou.**
Há teste que reprova se alguma classe se mover.

---

## 10 · PROVAS

`tests/test_v8_receptors_impl.py` — **55 provas** novas, dentro das
<!--M:TEST_COUNT_CURRENT-->859<!--/M--> da suíte, 0 falhas. As 589 anteriores foram
preservadas.

**Estas provas travam a medição, não aprovam o casco.** Quando o Claude Design corrigir um
item, a prova correspondente vai reprovar — e isso é o comportamento desejado: obriga a
remedir em vez de deixar um veredito velho passar por novo.

---

## 11 · SAÍDA

```
CASCO_WITNESS = casco/canonical/SINTONIA-EAME-V8-DATA-READY.html
SHA256 = 774ce0fbf3cdc567d95df872bd4299c89f5f46dfcede977a68387021abe6968a

HOSES_TOTAL = 9

H1 = FAIL · envelope COMPLETO · alias TERRITORIAL_ATTENTION_OBJECT sem mapa
H2 = FAIL · envelope COMPLETO · alias REGULATORY_DEADLINE sem mapa
H3 = FAIL · envelope COMPLETO · alias COMPETITOR_IDENTITY_CHAIN sem mapa
H4 = FAIL · envelope COMPLETO · alias PAID_ACTIVITY_EVIDENCE sem mapa
H5 = FAIL · envelope COMPLETO · alias LONGITUDINAL_FIELD_SERIES sem mapa
H6 = FAIL · NENHUM RECEPTOR com HOSE_ID = H6; voices[] não é receptor
H7 = FAIL · envelope COMPLETO · alias ISSUE_EXPERT sem mapa
H8 = FAIL · envelope COMPLETO · alias COMPANY_PUBLIC_ACCOUNT sem mapa
H9 = FAIL · envelope COMPLETO · alias MULTILINGUAL_CONTENT_REPRESENTATION sem mapa

HOSES_WITH_COMPLETE_RECEIVER = 0/9
HOSES_WITH_COMPLETE_ENVELOPE = 8/9

SCIENCE_PUBLICATION_RECEIVER = PRESENTE · payload canônico · HOSE_ID H7·CIÊNCIA sem PARENT
LOCAL_ADAMA_PORTFOLIO_RECEIVER = PRESENTE · payload canônico · HOSE_ID H2·PORTFÓLIO sem PARENT
FIELD_VOICE_RECEIVER = PRESENTE · payload canônico · HOSE_ID H6·CAMPO sem PARENT

CANONICAL_PAYLOAD_TYPE_DRIFT = FAIL   (8 aliases, nenhum ADAPTER_ALIAS_MAP)
SUBRECEPTOR_PARENT_HOSE_DRIFT = FAIL  (4 fora de H1..H9, nenhum PARENT_HOSE_ID)
ACTION_TYPE_CANONICAL_DRIFT = FAIL    (BUSINESS e SYSTEM persistidos)

CONVERGENCE_COMPONENT = PASS no Object Detail · FAIL no Radar
                        SINGLE SIGNAL calculado corretamente com 1 de 2 pernas independentes
TIMELINE_COMPONENT = PARCIAL · falta STATE_BEFORE/STATE_AFTER separados e SOURCE_ID tipado
CROP_MAP_COMPONENT = PASS · guard no asset, nenhum ponto desenhado sem GEO_RESOLUTION
ACTION_MAP_COMPONENT = PARCIAL · guard executável, falta OBJECT_ID e ACTION_TYPE canônico
EVIDENCE_DRAWER_COMPONENT = PARCIAL · por evidência, mas alcança 5 das 9 mangueiras

ORIGINAL_HANDLER = PASS
TRANSLATION_HANDLER = PASS

GITHUB_PROVENANCE = PASS (estrutura completa, UNWIRED como esperado)
SUPABASE_PROVENANCE = PASS (estrutura completa, UNWIRED como esperado)

ORPHAN_CANONICAL_INTELLIGENCE_OUTPUTS = 0
OUTPUTS_WITH_ABSENT_RECEPTOR = 2   (em 1 receptor: H6)

TESTS_TOTAL = 644
TESTS_FAILED = 0

DESIGN_PATCH_REQUIRED = YES
CASCO_RECEPTOR_READY = NO
READY_FOR_SUPABASE_ARCHITECTURE = YES
READY_TO_WIRE_REAL_DATA = NO
```

**Por que `READY_FOR_SUPABASE_ARCHITECTURE = YES`:** o envelope de proveniência está
completo para os dois backends, com um único componente de UI, e o casco não carrega
nenhum segredo — há teste que varre os bytes. Desenhar o schema já é possível; **ligar
ainda não**, porque o adapter não saberia para que nome escrever em oito das nove.

### `EXACT_BLOCKERS`

```
1  ADAPTER_ALIAS_MAP ausente — 8 mangueiras com nome de payload divergente e sem mapa
2  H6 sem receptor: voices[] tem os campos e não tem envelope; nenhum HOSE_ID = H6
3  PARENT_HOSE_ID ausente — H7·CIÊNCIA, H2·PORTFÓLIO, H6·CAMPO e H0 fora do vocabulário
4  bloco de convergência do Radar ficou na versão anterior (5 campos a menos que o obj)
5  openDrawer morto no Radar: chamado no markup, ausente de renderVals()
6  gaveta não alcança H6, H7, H8 e H9 — sem entradas no mapa de evidências
7  ACTION_TYPE persistido como BUSINESS/SYSTEM, sem DISPLAY_ACTION_TYPE
8  OBJECT_ID ausente no mapa de ações
9  STATE_BEFORE e STATE_AFTER concatenados numa string na timeline
10 SOURCE_ID da timeline é texto de exibição, não campo tipado
11 CREATOR_CONTENT_PROFILE e FARM_BUSINESS_ENTITY sem nome canônico em lugar nenhum
12 SOURCE_LANGUAGE ausente renderiza '—' em vez de UNKNOWN
```

**Os blocos 1 e 3 são o mesmo tipo de trabalho e resolvem sete dos doze.** O bloco 2 é o
único que exige um receptor novo. Os blocos 4 e 5 são o Radar que ficou para trás — e são
os únicos que hoje o usuário enxerga como defeito.
