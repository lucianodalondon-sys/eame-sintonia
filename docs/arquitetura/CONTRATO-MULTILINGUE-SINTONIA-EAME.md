# CONTRATO MULTILÍNGUE — SINTONIA EAME

**Data:** 2026-08-30 · **Branch:** `claude/sintonia-eame-portal-baseline`
**Revisão:** **RED TEAM + FREEZE** — sete correções sobre a versão anterior deste documento.

```
MULTILINGUAL_CONTRACT_V1 = FROZEN

ONE SHELL  +  ONE CANONICAL CORPUS  +  MULTIPLE LANGUAGE REPRESENTATIONS
```

> **`FROZEN` congela o desenho arquitetural. E só isso.**
> Não significa `CORPUS_MIGRATED`, não significa `ALL_TRANSLATIONS_READY`, não significa
> `SEARCH_INDEX_IMPLEMENTED`, não significa `DISEASE_ICON_BINDING_IMPLEMENTED`.

| | |
|---|---|
| modelo executável | [`scripts/multilingual_contract.py`](../../scripts/multilingual_contract.py) |
| provas | [`tests/test_multilingual.py`](../../tests/test_multilingual.py) — **68 provas** |

---

## 0 · O QUE ESTE RED TEAM CORRIGIU — no meu próprio contrato

| # | eu tinha escrito | está errado porque | agora |
|---|---|---|---|
| 1 | `ORIGINAL_LANGUAGE` como campo único | está sobrecarregado: mistura fonte, artefato e apresentação | **cinco papéis** distintos |
| 2 | *"78 de 81 declaram língua — 96 %"* | isso é **convenção de arquivo**, não propriedade da evidência | dois números separados |
| 3 | `ACTIVE_INGREDIENT` entre os imutáveis | obrigaria mostrar grafia francesa a leitor italiano | **ID canônico + rótulo local** |
| 4 | `SOURCE_QUOTE` como identificador | citação não é chave | `ORIGINAL_QUOTE` / `TRANSLATED_QUOTE` / `SOURCE_REFERENCE` |
| 5 | EPPO como espinha da ontologia inteira | EPPO cobre planta e organismo, **não** molécula, evento nem departamento | `EPPO_BACKED_ENTITY_ID` declarado |
| 6 | `PENDING_OFFICIAL_ICON` | soa como *"o ícone oficial não existe"* — **ele existe** | três estados separados |
| 7 | `SOURCE_LANGUAGE_PRESERVED = YES` | misturava o selo do **contrato** com o do **acervo** | `CONTRACT_GUARD` ≠ `CORPUS_AUDIT_RESULT` |

### 0.1 · A correção nº 2, medida — e ela é dura

Eu afirmei cobertura de **96 %**. Fui medir o nível que importa — o **registro**, não o
arquivo:

```
registros identificáveis varridos ................. 5.998
com CAMPO de língua ................................. 283   (4,7 %)
com um VALOR de língua de verdade ..................... 0   (0,00 %)
```

**Os 283 dizem `NÃO SEI`. Todos.**

O número `78/81` era real, mas media **os artefatos que eu e as outras missões escrevemos**
— um cabeçalho de convenção. **Nenhum registro de fonte no acervo tem língua de origem
declarada.** Transformar convenção de arquivo em propriedade da evidência era exatamente o
erro que o red team apontou, e ele estava certo.

```
ARTIFACTS_WITH_LEGACY_LANGUAGE_DECLARATION = 78/81
SOURCE_RECORDS_WITH_LANGUAGE_FIELD         = 283 / 5.998
SOURCE_RECORDS_WITH_DECLARED_VALUE         = 0
SOURCE_RECORD_LANGUAGE_COVERAGE            = MEASURED_ZERO_DECLARED
SOURCE_RECORD_LANGUAGE_PROOF               = NOT_MEASURED
```

---

# 1 · OS CINCO PAPÉIS DE LÍNGUA

Cinco coisas, cinco campos, **nenhum herda do outro**:

| papel | o que é | quem decide | muda com tradução? |
|---|---|---|---|
| **`SOURCE_LANGUAGE`** | a língua da **evidência / fonte original** | a fonte | **NUNCA** |
| **`ARTIFACT_LANGUAGE`** | a língua em que um relatório, handoff ou análise do SINTONIA foi escrito | quem escreveu | não |
| **`UI_LANGUAGE`** | menus, botões, filtros, estados | o usuário | não se aplica |
| **`DISPLAY_LANGUAGE`** | a língua escolhida para apresentar o conteúdo | o usuário | é ela que muda |
| **`TRANSLATION_TARGET_LANGUAGE`** | a língua de uma representação traduzida | o pipeline | — |

**Por que `ARTIFACT_LANGUAGE` teve de nascer:** quinze arquivos do acervo declaram `pt`.
Nenhuma fonte espanhola, francesa ou italiana é portuguesa — são **análises escritas em
português sobre fontes estrangeiras**. O campo estava guardando *"a língua de quem
escreveu"*. Um boletim francês resumido num relatório em português tem
`SOURCE_LANGUAGE = fr` **e** `ARTIFACT_LANGUAGE = pt`, e os dois são verdade ao mesmo tempo.

## 1.1 · Vocabulário fechado — sete valores, e dois deles não são línguas

```
en · es · fr · it · pt          ← línguas
MULTILINGUAL · UNKNOWN          ← ESTADOS
```

**`MULTILINGUAL` não é uma língua.** Um documento multilíngue não tem língua de origem:
tem várias, e cada trecho tem a sua. Por isso:

> **`SOURCE_LANGUAGE = MULTILINGUAL` exige `SEGMENT_LANGUAGE` por trecho, ou a declaração
> explícita de que alguém decidiu.** Deixar `"FR/ES/IT"` virar `MULTILINGUAL` em silêncio
> seria trocar um dado ruim por um estado bonito.

**`UNKNOWN` é preservado quando não foi medido.** Não vira chute, e não vira `en`.

**Uma string como `"FR/ES/IT/EN"` não é um language code** — e é recusada.

---

# 2 · CANONICAL_ENTITY_MODEL

```
CONTENT_ENTITY
  CONTENT_ID                chave canônica — sobrevive a toda tradução
  SOURCE_LANGUAGE           pt|en|es|fr|it   ·  None quando MULTILINGUAL
  SOURCE_LANGUAGE_STATE     OK | MULTILINGUAL | UNKNOWN
  ARTIFACT_LANGUAGE         a língua de quem escreveu sobre isto
  SEGMENTS[]                SEGMENT_ID · SEGMENT_LANGUAGE · TEXT
  ORIGINAL_TEXT             o texto como a fonte publicou
  ORIGINAL_TEXT_HASH        SHA-256 — o gatilho de invalidação do cache
  ORIGINAL_QUOTE            o trecho citado, byte a byte
  SOURCE_REFERENCE          URL · DOI · registro · document ID
  SOURCE                    SOURCE_ID + URL
  PUBLISHED_AT · FACT_COUNTRY
  IDENTITIES{}              apenas o grupo A da seção 3
  TRANSLATIONS{ lang: … }
```

```
CONTENT_TRANSLATION
  CONTENT_ID                     o MESMO id — nunca um id novo
  TRANSLATION_TARGET_LANGUAGE
  TRANSLATED_TEXT · TRANSLATED_QUOTE
  TRANSLATION_METHOD             MACHINE | HUMAN | SOURCE_PROVIDED
  TRANSLATION_VERSION · TRANSLATED_AT
  QUALITY_STATE                  ver seção 9
  SOURCE_TEXT_HASH               o hash do original NO MOMENTO da tradução
  IS_EVIDENCE                    sempre false
```

---

# 3 · IDENTIDADE CANÔNICA ≠ RÓTULO TRADUZIDO

## Grupo A — identidade que **nunca** se traduz

```
TRADEMARK_ID · TRADEMARK_CANONICAL_NAME
COMPANY_ID   · COMPANY_LEGAL_NAME
REGISTRATION_ID
SCIENTIFIC_NAME
PRODUCT_COMMERCIAL_NAME
```

Traduzir qualquer um **destrói a chave**. `ES-00211` não tem tradução; `MAXENTIS` é
`MAXENTIS` em toda parte; razão social é identidade jurídica.

## Grupo B — ID canônico invariante, **rótulo local legítimo**

```
ACTIVE_INGREDIENT_ID · CROP_ID · ISSUE_ID
MOLECULE_ID · EVENT_TYPE_ID · DEPARTMENT_ID
```

**A correção que eu precisava fazer:** `ACTIVE_INGREDIENT` estava no grupo A. Errado.

```
CAS-178928-70-6
  LABEL_FR = prothioconazole      LABEL_ES = protioconazol
  LABEL_IT = protioconazolo       LABEL_EN = prothioconazole
```

São **três grafias diferentes da mesma molécula**. Exigir igualdade byte a byte obrigaria a
mostrar a grafia francesa a um leitor italiano. **A invariância é do ID, nunca do rótulo** —
e há prova de que o ID sobrevive às três grafias.

Usar um campo do grupo B como identidade imutável é **recusado em código**.

---

# 4 · CITAÇÃO — três coisas, não uma

| campo | o que é | pode ser traduzido? |
|---|---|---|
| **`ORIGINAL_QUOTE`** | o trecho original, byte a byte como capturado | **não** |
| **`TRANSLATED_QUOTE`** | representação para leitura | sim, **marcada** |
| **`SOURCE_REFERENCE`** | URL · DOI · registro · document ID | não |

> **`TRANSLATED_QUOTE ≠ ORIGINAL_QUOTE`.** A tradução **pode** ser apresentada — desde que
> claramente marcada como tradução. O que **não** pode é **substituir** o original.

Toda exibição carrega, em qualquer língua: `ORIGINAL_QUOTE` · `QUOTE_IS_TRANSLATION` ·
`QUOTE_IS_EVIDENCE` · `VIEW ORIGINAL` · `SOURCE` · `SOURCE_REFERENCE` · `SOURCE_LANGUAGE`.

Há prova de que a citação original sai idêntica nas cinco línguas, mesmo quando a traduzida
está na tela.

---

# 5 · ONTOLOGY_MODEL

```
ONTOLOGY_TERM
  TERM_ID                  EPPO quando existir; CANONICAL_ID explícito quando não
  KIND                     CROP | ISSUE | MOLECULE | EVENT_TYPE | DEPARTMENT
  EPPO_BACKED_ENTITY_ID    YES | NO | NOT_MEASURED   ← declarado, nunca adivinhado
  SCIENTIFIC_NAME          o ancoradouro entre línguas
  LABELS{ es, en, fr, it, pt }
  ALIASES{ lang: [...] }
  ADAMA_DISEASE_ICON_ID
```

## 5.1 · O que o EPPO cobre — e o que não cobre

Medido no `eppo-dictionary.json`:

| | total | chave em forma EPPO | fora da forma |
|---|---:|---:|---:|
| **culturas** | 492 | **484 (98,4 %)** | 8 |
| **pragas / doenças** | 1.381 | **1.347 (97,5 %)** | 34 |

As 42 chaves fora da forma são texto solto usado como chave — `"only annual species"`,
`"sunflower"`, `"rice"`, `"perennial species"`. **Rótulo nunca pode ser chave primária**, e
essas 42 são o exemplo vivo disso dentro do próprio acervo.

**E EPPO só existe para planta e organismo.** `MOLECULE`, `EVENT_TYPE` e `DEPARTMENT`
**não têm e não terão** código EPPO — declarar `EPPO_BACKED = YES` para eles é recusado em
código. Precisam de outro identificador canônico explícito: CAS para molécula, enum próprio
para tipo de evento e departamento.

## 5.2 · Fallback declarado, nunca silencioso

```
rótulo na língua pedida → SCIENTIFIC_NAME → rótulo EN → qualquer rótulo → TERM_ID
```

Pedir o rótulo italiano de *Plasmopara viticola* devolve o nome científico **com
`FALLBACK = SCIENTIFIC_NAME`** — a tela precisa poder dizer por que está mostrando latim.

---

# 6 · ÍCONE OFICIAL DE DOENÇA — três estados, não um

**Correção de estado.** O casco V7 não carregar os ícones **não** significa que eles não
existam. Eles existem, no **design system da ADAMA disponível no Claude Design**.

```
OFFICIAL_ADAMA_DISEASE_ICON_ASSET = EXISTS_EXTERNALLY_IN_DESIGN_SYSTEM
DISEASE_ICON_CROSSWALK            = NOT_MEASURED
TECHNICAL_ICON_BINDING            = NOT_IMPLEMENTED
```

São **três perguntas diferentes**, e `PENDING_OFFICIAL_ICON` confundia as três:

1. **o ativo existe?** — sim, fora daqui;
2. **existe o mapa `DISEASE_ID ↔ ADAMA_DISEASE_ICON_ID`?** — não foi medido;
3. **o vínculo técnico está feito?** — não implementado.

**Contrato:** `ISSUE_ID / DISEASE_ID → ADAMA_DISEASE_ICON_ID`. A implementação futura
**consulta e reutiliza o asset oficial** do Claude Design.

> **Não desenhar ícone substituto. Não extrair nem recriar manualmente agora. Não modificar
> o V7.** Há prova de que o estado nunca sai como *missing*.

---

# 7 · SEARCH_MODEL — modelo pronto, índice não

```
CROSS_LANGUAGE_SEARCH_MODEL = READY          ← desenho, provado em teste
CROSS_LANGUAGE_SEARCH_INDEX = NOT_IMPLEMENTED
```

**Nove caminhos de recuperação, todos declarados.** O consumidor precisa saber **por que** o
item apareceu — achar pelo `REGISTRATION_ID` é uma confiança; achar por texto traduzido por
máquina é outra:

```
CANONICAL_ID_MATCH                 REGISTRATION_ID_MATCH
ORIGINAL_TEXT_MATCH                OFFICIAL_ALIAS_MATCH
HUMAN_REVIEWED_TRANSLATION_MATCH   MACHINE_TRANSLATION_MATCH
SEMANTIC_MATCH                     ← declarado, NÃO implementado
ONTOLOGY_LABEL_MATCH               ← acrescentado: rótulo oficial não é apelido
SCIENTIFIC_NAME_MATCH              ← acrescentado: atravessa as 5 línguas sem tradução
```

Os dois últimos são acréscimos meus aos sete nomeados pelo coordenador, e estão marcados
como acréscimo: encaixá-los à força em `OFFICIAL_ALIAS_MATCH` diria que um rótulo oficial é
apelido, o que é falso.

**Um índice, não um acervo por língua.** Provado: buscar *"mildiu"* em espanhol encontra um
boletim publicado **em francês**, e o caminho vem junto. Há prova de que máquina e humano
saem como caminhos **diferentes**, e de que `SEMANTIC_MATCH` está no vocabulário e **não**
no índice.

---

# 8 · UI_I18N_MODEL

| | UI | CONTEÚDO |
|---|---|---|
| o que é | menus, botões, filtros, estados, departamentos, rótulos | boletins, posts, documentos, citações |
| quantidade | finita e pequena | cresce sem parar |
| método | **i18n tradicional**, dicionário versionado | pipeline com proveniência |
| runtime | **nunca** chama IA | traduz uma vez, guarda, reusa |

> **Proibido usar IA em runtime para traduzir menu, botão, filtro, estado, departamento ou
> rótulo.** Um botão que muda de texto entre duas sessões destrói a confiança em tudo o que
> está ao redor dele.

O `DISPLAY-LAYER-V1` (103 regras, 33 campos de origem) é exatamente essa fronteira: traduz
**valores de enum canônico**, que é UI. Entra no dicionário de i18n, com a `SEMANTIC_RULE`
viajando junto como nota do tradutor — e com a lei que ela já carrega:

> *"Nenhuma tradução pode mudar o que o campo afirma. Uma frase de exibição só pode ser
> **mais explícita** que o enum, nunca menos."*

---

# 9 · TRANSLATION_PROVENANCE

Seis perguntas, sempre: `SOURCE_LANGUAGE` · `DISPLAY_LANGUAGE` · `TRANSLATION_METHOD` ·
`TRANSLATION_VERSION` · `TRANSLATED_AT` · `QUALITY_STATE`.

| método | qualidades que **pode** declarar |
|---|---|
| `MACHINE` | `MACHINE_TRANSLATED` · `HUMAN_REVIEWED` (só depois de alguém revisar) |
| `HUMAN` | `HUMAN_REVIEWED` |
| `SOURCE_PROVIDED` | `SOURCE_PROVIDED_TRANSLATION` |

> **Máquina não vira revisada sozinha.** É o único erro desta camada que **o usuário não
> consegue detectar lendo**. Todos os outros ele percebe.

---

# 10 · CACHE_VERSIONING

```
TRANSLATE_ONCE → STORE → VERSION → REUSE

FRESH    hash igual ao original de hoje       → reusar
STALE    o texto canônico mudou               → retraduzir, VERSION + 1
MISSING  nunca traduzido nesta língua         → traduzir
```

**Reexibir não envelhece nada** — cinco aberturas seguidas continuam `FRESH`, e há prova.
**A versão antiga não se apaga:** se alguém citou a v1 numa apresentação, essa citação
precisa continuar resolvível.

---

# 11 · KNOWN_GAPS — backlog medido, não preenchido

| # | lacuna | tamanho | triagem |
|---|---|---|---|
| **K1** | vocabulário de língua aberto no legado | 15 grafias · 17/78 não são língua | `MUST_HAVE_FOR_PILOT` |
| **K2** | `pt` confundindo artefato com fonte | 15 arquivos | `MUST_HAVE_FOR_PILOT` |
| **K3** | registros de fonte sem língua | **0 de 5.998 declarados** | `MUST_HAVE_FOR_PILOT` (só para os recortes do piloto) |
| **K4** | `DISPLAY_STRINGS_MISSING_FR_IT` | **206** (103 × 2) | `MUST_HAVE_FOR_PILOT` — o casco oferece 5 línguas |
| **K5** | `ONTOLOGY_TERMS_WITHOUT_FULL_MULTILINGUAL_LABELS` | **1.873** | **`CAN_FALLBACK_TO_ORIGINAL_LABEL`** |
| **K6** | chaves não-EPPO no dicionário | 42 | `NICE_TO_HAVE` |
| **K7** | `DISEASE_ICON_CROSSWALK` | não medido | `MUST_HAVE_FOR_PILOT` (só para os issues do piloto) |
| **K8** | `ALIASES` não existem no acervo | — | `MUST_HAVE_FOR_PILOT` — é o que faz a busca cross-language funcionar |
| **K9** | nenhuma `CONTENT_TRANSLATION` existe | zero | `NICE_TO_HAVE` |
| **K10** | custo de tradução não medido | — | `NICE_TO_HAVE` |

> **Não traduzir 1.873 termos só porque estão vazios.** O fallback declarado
> (`SCIENTIFIC_NAME`) cobre o intervalo, e o piloto consome uma fração mínima desses termos.
> **Prioridade é o que o piloto realmente usa** — hoje, seis recortes.

**Nada disto foi fechado nesta rodada.** K1 e K2 seriam um passe de normalização com o
portão já escrito e testado — mas mexer em 78 artefatos de outras missões é **migração**, e
migração está fora deste modo.

---

# ENTREGA

```
MULTILINGUAL_CONTRACT_V1 = FROZEN

── contrato (o que as provas garantem) ──────────────────────────────
ONE_CANONICAL_CORPUS                   = YES
SEPARATE_DATABASE_PER_LANGUAGE         = NO
ONTOLOGY_LANGUAGE_INDEPENDENT          = YES
SOURCE_LANGUAGE_PRESERVATION_RULE      = PROVED_BY_TESTS
ORIGINAL_EVIDENCE_PRESERVATION_RULE    = PROVED_BY_TESTS
SOURCE_LANGUAGE_NE_ARTIFACT_LANGUAGE   = PROVED_BY_TESTS
CANONICAL_ONTOLOGY_MODEL               = FROZEN
ORIGINAL_QUOTE_MODEL                   = FROZEN — byte a byte, nunca substituível
TRANSLATED_QUOTE_MODEL                 = FROZEN — permitida, sempre marcada
ACTIVE_INGREDIENT_IDENTITY_MODEL       = CANONICAL_ID + LOCAL_LABELS
CROSS_LANGUAGE_SEARCH_MODEL            = READY

── acervo legado (o que foi medido) ─────────────────────────────────
ARTIFACTS_WITH_LEGACY_LANGUAGE_DECLARATION = 78/81
SOURCE_RECORD_LANGUAGE_COVERAGE            = MEASURED_ZERO_DECLARED (0 / 5.998)
LEGACY_LANGUAGE_FIELD_INTEGRITY            = NOT_PROVED
LEGACY_SOURCE_LANGUAGE_INTEGRITY           = NOT_PROVED
LEGACY_CORPUS_EVIDENCE_INTEGRITY           = NOT_MEASURED
LEGACY_CORPUS_MULTILINGUAL_COMPLIANCE      = NOT_MEASURED

── ontologia ────────────────────────────────────────────────────────
EPPO_CROPS                  = 492  (484 em forma de código, 98,4 %)
EPPO_ISSUES                 = 1.381 (1.347 em forma de código, 97,5 %)
NON_EPPO_ENTITY_STRATEGY    = CANONICAL_ID explícito por tipo — CAS para molécula,
                              enum próprio para EVENT_TYPE e DEPARTMENT

── ícone ────────────────────────────────────────────────────────────
OFFICIAL_ADAMA_DISEASE_ICON_ASSET = EXISTS_EXTERNALLY_IN_DESIGN_SYSTEM
DISEASE_ICON_CROSSWALK            = NOT_MEASURED
TECHNICAL_ICON_BINDING            = NOT_IMPLEMENTED

── implementação ────────────────────────────────────────────────────
CROSS_LANGUAGE_SEARCH_INDEX  = NOT_IMPLEMENTED
DISPLAY_STRINGS_MISSING_FR_IT = 206
ONTOLOGY_LABEL_GAPS           = 1.873
PRODUCT_IMPLEMENTATION_MODE   = NOT_ENTERED
CASCO_V7_MODIFIED             = NO
CORPUS_MIGRATION_EXECUTED     = NO
MASS_TRANSLATION_EXECUTED     = NO

MISSION_STATE = PARKED
```
