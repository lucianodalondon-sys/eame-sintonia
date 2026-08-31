# CONTRATO MULTILÍNGUE — SINTONIA EAME

**Data:** 2026-08-30 · **Branch:** `claude/sintonia-eame-portal-baseline`
**Modo:** contrato + modelo executável. **Nenhuma tradução em massa foi executada.**

```
ONE SHELL  +  ONE CANONICAL CORPUS  +  MULTIPLE LANGUAGE REPRESENTATIONS

PRODUCT_IMPLEMENTATION_MODE = NOT_ENTERED
CASCO_V7_MODIFIED           = NO
MASS_TRANSLATION_EXECUTED   = NO
```

| | |
|---|---|
| modelo executável | [`scripts/multilingual_contract.py`](../../scripts/multilingual_contract.py) |
| provas | [`tests/test_multilingual.py`](../../tests/test_multilingual.py) — **38 provas** |

> **Por que o contrato é código e não só texto.** Um contrato que vive só em documento não
> impede nada. As sete regras abaixo têm prova que **reprova** quem as quebrar — inclusive
> eu, daqui a três semanas.

---

## 0 · O QUE JÁ EXISTE — medido, não suposto

Metade deste contrato já está no repositório. Medi antes de propor.

| peça | estado medido |
|---|---|
| **`ORIGINAL_LANGUAGE` como lei** | **78 de 81** arquivos de `data/samples` já declaram (96 %) |
| **`SOURCE_LOCATION` ≠ `FACT_LOCATION`** | 704 ocorrências de cada — a separação geográfica já é hábito |
| **Ontologia com ID próprio** | `eppo-dictionary.json`: **492 culturas · 1.381 pragas**, chaveadas por **código EPPO** — `OLVEU` = *Olea europaea*, `SEPTTR` = *Zymoseptoria tritici* |
| **Camada de exibição** | `DISPLAY-LAYER-V1.json`: **103 regras**, 33 campos de origem, cada uma com `SEMANTIC_RULE` própria |
| **Casco V7** | seletor de idioma com **5 línguas** (PT · EN · ES · IT · FR) e a lei escrita: *"as strings da interface saem de dicionário, não do conteúdo"* |

### 0.1 · E as três lacunas que a medição encontrou

**① O vocabulário de língua está aberto.** 78 arquivos usam **15 grafias diferentes** para
o que deveria ser um conjunto fechado de 5:

```
'ES' 18 · 'pt' 15 · 'es' 11 · 'EN' 9 · 'multi' 8 · 'FR' 4 · 'IT' 3
'FR/ES' 2 · 'FR/ES/IT' 2 · 'FR/ES/IT/EN' · 'en (majoritario)' · 'ES / EN' · 'EN / FR' · 'FR/IT' · 'en'
```

**17 de 78 (22 %) não são uma língua** — são `MULTI` disfarçado de código.

**② E o `pt` denuncia uma confusão real.** Quinze artefatos declaram
`ORIGINAL_LANGUAGE: pt`. Nenhuma fonte espanhola, francesa ou italiana é portuguesa —
esses arquivos são **análises derivadas escritas em português**. O campo está registrando
*"a língua em que eu escrevi"*, não *"a língua da fonte"*. **É exatamente a confusão que
a seção 1 existe para acabar.**

**③ A camada de exibição cobre 3 das 5 línguas do casco.** `DISPLAY-LAYER-V1` tem
`DISPLAY_TEXT_PT`, `_EN` e `_ES`. **Não tem `_FR` nem `_IT`.** Para fechar as cinco línguas
que o casco oferece faltam **206 strings** (103 regras × 2 línguas).

**④ Não existe ícone oficial de doença no casco.** Medido: o único SVG embutido é a forma
**"A"** da marca ADAMA, e `disease-control` é **cor de linha de produto** (`#00a0df`), não
ícone. Ver seção `ONTOLOGY_MODEL`.

---

# 1 · A SEPARAÇÃO QUE MANDA EM TUDO

Três coisas, três campos, nenhum herda do outro:

| campo | o que é | quem decide | muda com tradução? |
|---|---|---|---|
| **`SOURCE_LANGUAGE`** | a língua em que a fonte publicou | **a fonte** | **NUNCA** |
| **`UI_LANGUAGE`** | a língua dos menus, botões, filtros e estados | o usuário | não se aplica |
| **`DISPLAY_LANGUAGE`** | a língua em que o conteúdo é apresentado | o usuário | é ela que muda |

> **Uma tradução francês→espanhol NÃO transforma a fonte em espanhola.**
> Há prova disso: traduzir uma entidade para quatro línguas deixa `SOURCE_LANGUAGE`,
> `ORIGINAL_TEXT` e o hash do original **byte a byte idênticos**.

**Regra de vocabulário.** `SOURCE_LANGUAGE` aceita apenas `pt · en · es · fr · it`, em
minúsculo. Qualquer outra coisa vira **estado**, não língua:

- `MULTI` — o documento tem mais de uma língua. **`MULTI` não é uma língua**: um documento
  multilíngue não tem língua de origem, tem várias, e cada trecho tem a sua.
- `UNKNOWN` — não foi possível decidir. **Falha fechada**: `content_entity()` recusa criar
  o objeto.

**Traduzir para a própria língua de origem é recusado** — o estado correto é
`SOURCE_ORIGINAL`, e chamar isso de tradução criaria uma versão que ninguém produziu.

---

# 2 · CANONICAL_ENTITY_MODEL

**Um objeto. Várias línguas. Nunca vários objetos.**

```
CONTENT_ENTITY
  CONTENT_ID              chave canônica — sobrevive a toda tradução
  SOURCE_LANGUAGE         pt|en|es|fr|it  ·  None quando MULTI
  SOURCE_LANGUAGE_STATE   OK | MULTI | UNKNOWN
  ORIGINAL_TEXT           o texto como a fonte publicou
  ORIGINAL_TEXT_HASH      SHA-256 — é o gatilho de reversão do cache
  SOURCE                  SOURCE_ID + URL
  PUBLISHED_AT            data da fonte
  FACT_COUNTRY            onde o fato acontece (≠ onde a fonte está)
  NON_TRANSLATABLE        os sete identificadores da seção 5
  TRANSLATIONS            { lang: CONTENT_TRANSLATION }
```

```
CONTENT_TRANSLATION
  CONTENT_ID              o MESMO id — nunca um id novo
  TRANSLATION_LANGUAGE    pt|en|es|fr|it
  TRANSLATED_TEXT
  TRANSLATION_METHOD      MACHINE | HUMAN | SOURCE_PROVIDED
  TRANSLATION_VERSION     inteiro
  TRANSLATED_AT
  QUALITY_STATE           ver seção 9
  SOURCE_TEXT_HASH        o hash do original NO MOMENTO da tradução
  IS_EVIDENCE             sempre false — ver seção 4
```

**Por que `SOURCE_TEXT_HASH` mora na tradução e não na entidade:** é ele que responde
*"esta tradução ainda vale?"* sem precisar guardar o texto antigo. Ver seção 10.

---

# 3 · ONTOLOGY_MODEL — a identidade não muda com a língua

```
ONTOLOGY_TERM
  TERM_ID                 EPPO quando existir; interno quando não
  KIND                    CROP | ISSUE | MOLECULE | EVENT_TYPE | DEPARTMENT
  SCIENTIFIC_NAME         o ancoradouro entre línguas
  LABELS                  { es, en, fr, it, pt }
  ALIASES                 { lang: [...] }   ← é o que faz a busca funcionar de verdade
  ADAMA_DISEASE_ICON_ID   ver abaixo
  ICON_BINDING_STATE      BOUND | PENDING_OFFICIAL_ICON | NOT_APPLICABLE
```

**O ancoradouro já existe.** `SEPTTR` é `Zymoseptoria tritici` em qualquer língua. Um caso
francês e um caso espanhol de septória apontam para **o mesmo `TERM_ID`** — e é por isso
que a camada EAME pode comparar sem traduzir nada.

**Cadeia de fallback, sempre declarada:**

```
rótulo na língua pedida  →  SCIENTIFIC_NAME  →  rótulo em EN  →  qualquer rótulo  →  TERM_ID
```

**Nunca devolve vazio, e nunca esconde o desvio.** Pedir o rótulo italiano de *Plasmopara
viticola* devolve o nome científico **com `FALLBACK = SCIENTIFIC_NAME`** — a tela precisa
poder dizer por que está mostrando latim.

**Lacuna medida:** o dicionário EPPO tem `es` e `scientific`. **Não tem `fr`, `it` nem
`en`.** São 1.873 termos sem rótulo em 3 das 5 línguas do casco. Isso não impede a
identidade — impede o rótulo bonito, e o fallback declarado cobre o intervalo.

## 3.1 · `ADAMA_DISEASE_ICON_ID`

O design system da ADAMA tem ícones oficiais de doença, e o casco futuro deve usar o ícone
oficial correspondente.

**Estado medido hoje:** o casco V7 **não traz nenhum**. O único SVG embutido é a forma "A"
da marca; `disease-control` é a **cor** da linha de produto, não um ícone de doença.

**Contrato, sem inventar ID:**

```
ISSUE com ícone oficial vinculado   →  BOUND
ISSUE sem ícone oficial ainda       →  PENDING_OFFICIAL_ICON
CROP / MOLECULE / DEPARTMENT        →  NOT_APPLICABLE
```

> **Regra: não criar ícone genérico quando existir o oficial.** Enquanto o conjunto oficial
> não chegar, o estado é `PENDING_OFFICIAL_ICON` e a tela mostra a cor da linha — que é
> oficial — em vez de um desenho inventado que depois teria de ser desfeito.

---

# 4 · EVIDENCE_RULES

> **`TRANSLATED_EVIDENCE ≠ ORIGINAL_EVIDENCE`**

Tradução é **representação para leitura**. Nunca é a prova.

**Toda exibição carrega a porta de volta** — inclusive quando não houve tradução nenhuma:

```
TRANSLATED FROM <LANGUAGE>     ·  presente só quando houve tradução
VIEW ORIGINAL                  ·  SEMPRE
SOURCE                         ·  SEMPRE
IS_EVIDENCE                    ·  true apenas no texto original
```

**Sem tradução, mostra o original — nunca vazio.** Pedir um boletim francês em português
sem tradução registrada devolve o texto francês com `QUALITY_STATE = SOURCE_ORIGINAL` e
`TRANSLATED_FROM = None`. Tela vazia seria pior que língua errada: sugeriria ausência de
conteúdo onde há conteúdo.

**Claim regulatório, científico ou técnico nunca perde a ligação com o original.** Isto não
é preferência de UX: um vencimento de registro, uma dose de rótulo ou uma citação de
boletim são afirmações que alguém vai defender numa reunião. Defende-se o original.

---

# 5 · O QUE NÃO SE TRADUZ

Sete campos são **identidade**, não texto. Traduzir qualquer um destrói a chave:

| campo | por quê |
|---|---|
| `PRODUCT_COMMERCIAL_NAME` | MAXENTIS é MAXENTIS em toda parte |
| `COMPANY_NAME` | razão social é identidade jurídica |
| `TRADEMARK` | é a chave nova que o Foresight traz — `BRAND` |
| `ACTIVE_INGREDIENT` | tem nome por língua, mas quem manda é o CAS |
| `SCIENTIFIC_NAME` | é justamente o ancoradouro entre línguas |
| `REGISTRATION_ID` | `ES-00211` não tem tradução |
| `SOURCE_QUOTE` | citação traduzida deixa de ser citação |

**Há prova de que os sete saem idênticos em todas as línguas de exibição**, e de que um
campo fora da lista é recusado na criação da entidade.

**Nota sobre `ACTIVE_INGREDIENT`:** *prothioconazole* / *protioconazol* / *protioconazolo*
são a mesma molécula. A tradução do **rótulo** é legítima e vive na ontologia
(`KIND = MOLECULE`); o **campo de identidade** do conteúdo preserva a grafia da fonte. São
duas coisas, e o modelo as separa.

---

# 6 · SEARCH_MODEL — um índice, não um acervo por língua

Uma busca em ES precisa achar material originalmente em FR, IT ou EN — **e devolver o mesmo
objeto canônico**.

**Seis caminhos, todos apontando para o mesmo ID:**

```
CANONICAL ENTITY IDS   →  CONTENT_ID · TERM_ID
IDENTIFICADORES        →  marca, registro, nome comercial, nome científico
SCIENTIFIC_NAME        →  atravessa as cinco línguas sem tradução
MULTILINGUAL LABELS    →  o rótulo da ontologia em cada língua
ALIASES                →  "mildiu", "mildiou", "peronospora" → PLASVI
ORIGINAL TEXT          →  o texto da fonte
TRANSLATED TEXT        →  o texto traduzido
```

**`SEMANTIC SEARCH` fica de fora por enquanto**, e a razão é medida: busca semântica traz
resultado sem caminho auditável, e este produto tem por lei mostrar de onde veio cada
coisa. Entra depois, como **caminho adicional declarado**, nunca substituindo os outros.

**O caminho do achado viaja com o resultado.** Achar pelo `REGISTRATION_ID` é uma confiança;
achar pelo texto traduzido por máquina é outra. Quem lê precisa poder distinguir — há prova
de que o caminho sai declarado e de que pelo menos três caminhos diferentes funcionam.

**Provado:** buscar *"mildiu"* (espanhol) encontra um boletim publicado **em francês**, e
`Plasmopara viticola` encontra os dois lados sem passar por tradução nenhuma.

---

# 7 · INTELIGÊNCIA GERADA — uma decisão, várias narrativas

**A estrutura do caso é independente de língua. A narrativa não.**

```
ESTRUTURAL (uma só)                       NARRATIVA (uma por língua)
  COUNTRY · REGION                          título legível
  CROP_ID · ISSUE_ID    ← ontologia         síntese do caso
  TIME / WINDOW                             "por que está no radar"
  ATTENTION_STATE                           "o que não sabemos"
  ACTION_OWNER                              rótulo de estado (DISPLAY-LAYER)
  CONVERGENCE_LEGS
  EVIDENCE POINTERS
```

> **`ONE INTELLIGENCE OBJECT → MULTIPLE LANGUAGE PRESENTATIONS`.**
> Nunca quatro decisões diferentes. Se a versão italiana de um caso disser algo que a
> francesa não diz, **não é tradução — é outro caso**, e isso é defeito.

O `DISPLAY-LAYER-V1` já implementa a lei que protege isso, e ela é a melhor frase deste
contrato inteiro:

> *"Nenhuma tradução pode mudar o que o campo afirma. Uma frase de exibição só pode ser
> **mais explícita** que o enum, nunca menos."*

E o teste de deriva que vem junto: *"um leitor que só viu a frase de exibição chegaria a uma
conclusão que o campo não sustenta? Se sim, a regra está errada."*

---

# 8 · UI_I18N_MODEL — interface e conteúdo são coisas diferentes

| | UI | CONTEÚDO |
|---|---|---|
| o que é | menus, botões, filtros, estados, departamentos, rótulos | boletins, posts, documentos, citações |
| quantidade | finita e pequena | cresce sem parar |
| método | **i18n tradicional** — dicionário de chaves, versionado no repositório | pipeline de tradução com proveniência |
| runtime | **nunca** chama IA | traduz uma vez, guarda, reusa |
| quem revisa | uma vez, por pessoa | ver seção 9 |

> **Proibido usar IA em runtime para traduzir menu, botão, filtro, estado, departamento ou
> rótulo.** É caro, é lento, é não-determinístico — e um botão que muda de texto entre duas
> sessões destrói a confiança em tudo o que está ao redor dele.

**O casco já está do lado certo:** *"as strings da interface saem de dicionário, não do
conteúdo"*. O dicionário é que ainda não existe.

**Ponte com o `DISPLAY-LAYER-V1`:** as 103 regras são exatamente a fronteira entre os dois
mundos — traduzem **valores de enum canônico** (`VERIFY_FIELD_NOW` → *"Verificar o campo
agora"*), que é UI, não conteúdo. Elas entram no dicionário de i18n, com a `SEMANTIC_RULE`
viajando junto como comentário do tradutor.

---

# 9 · TRANSLATION_PROVENANCE

Toda tradução de conteúdo responde seis perguntas, sempre:

```
ORIGINAL_LANGUAGE =        DISPLAY_LANGUAGE =        TRANSLATION_METHOD =
TRANSLATION_VERSION =      TRANSLATED_AT =           QUALITY_STATE =
```

**Quatro estados, e o método não escolhe sozinho:**

| estado | significa |
|---|---|
| `SOURCE_ORIGINAL` | não é tradução: é o texto da fonte |
| `MACHINE_TRANSLATED` | máquina, **sem** revisão humana |
| `HUMAN_REVIEWED` | pessoa leu e aprovou |
| `SOURCE_PROVIDED_TRANSLATION` | a própria fonte publicou nesta língua |

**Máquina não vira revisada sozinha.** O método restringe o que pode ser declarado:

```
MACHINE          →  MACHINE_TRANSLATED  ou  HUMAN_REVIEWED (só depois de alguém revisar)
HUMAN            →  HUMAN_REVIEWED
SOURCE_PROVIDED  →  SOURCE_PROVIDED_TRANSLATION
```

Declarar `MACHINE_TRANSLATED` num método `HUMAN` é recusado, e há prova.

> **Por que esta é a regra mais importante da seção:** afirmar revisão humana onde não houve
> é o único erro desta camada que **o usuário não consegue detectar**. Todos os outros ele
> percebe lendo. Este, não.

---

# 10 · CACHE_VERSIONING

```
TRANSLATE_ONCE  →  STORE  →  VERSION  →  REUSE
```

Três estados, decididos por hash e não por data:

| estado | quando | o que fazer |
|---|---|---|
| `FRESH` | `SOURCE_TEXT_HASH` == hash atual do original | **reusar** |
| `STALE` | o texto canônico mudou depois da tradução | retraduzir, `VERSION + 1` |
| `MISSING` | nunca traduzido para esta língua | traduzir |

**Reexibir não envelhece nada.** Abrir o mesmo caso cinco vezes em espanhol continua
`FRESH` — há prova disso, e é o teste que evita a conta absurda.

**A versão antiga não se apaga.** `TRANSLATION_VERSION` cresce e as anteriores ficam: se
alguém citou a versão 1 numa apresentação, essa citação precisa continuar resolvível.

**O que dispara nova versão:** mudança no **texto canônico**. Não dispara: mudança de
layout, de rótulo de UI, de idioma da interface, nem reexibição.

---

# 11 · KNOWN_GAPS

| # | lacuna | tamanho medido |
|---|---|---|
| **K1** | `ORIGINAL_LANGUAGE` com vocabulário aberto | **15 grafias** em 78 arquivos; **17 (22 %)** não são língua única |
| **K2** | `ORIGINAL_LANGUAGE: pt` em análises derivadas | **15 arquivos** confundem língua da fonte com língua do documento |
| **K3** | Camada de exibição só em PT/EN/ES | faltam **206 strings** (103 regras × FR e IT) |
| **K4** | Ontologia sem rótulo em FR/IT/EN | **1.873 termos** (492 culturas + 1.381 pragas) com `es` + `scientific` apenas |
| **K5** | Chaves não-EPPO no dicionário | há entradas como `"only annual species"` usadas como chave |
| **K6** | Sem ícones oficiais de doença | o casco V7 não traz nenhum; `ICON_BINDING_STATE = PENDING_OFFICIAL_ICON` |
| **K7** | `ALIASES` não existem no acervo | são o que faz a busca cross-language funcionar; hoje só o modelo os prevê |
| **K8** | Nenhuma tradução de conteúdo existe | zero `CONTENT_TRANSLATION` no repositório — o contrato precede o pipeline |
| **K9** | Busca semântica fora | por decisão: falta caminho auditável |
| **K10** | Custo de tradução não medido | nenhum orçamento, nenhuma rota escolhida, nenhum teste de volume |

**K1 e K2 são os únicos que dá para fechar sem coletar nada** — são um passe de
normalização sobre 78 arquivos, com o portão `normalizar_lingua()` já escrito e testado.
**Não os fechei nesta rodada:** mexer em 78 artefatos de outras missões é integração, e
integração está fora deste modo.

---

# ENTREGA

```
ONE_CANONICAL_CORPUS               = YES
SEPARATE_DATABASE_PER_LANGUAGE     = NO
SOURCE_LANGUAGE_PRESERVED          = YES
ONTOLOGY_LANGUAGE_INDEPENDENT      = YES
ORIGINAL_EVIDENCE_PRESERVED        = YES
CROSS_LANGUAGE_SEARCH_DESIGN       = READY
ADAMA_DISEASE_ICON_BINDING_PLANNED = YES

PRODUCT_IMPLEMENTATION_MODE = NOT_ENTERED
CASCO_V7_MODIFIED           = NO
MASS_TRANSLATION_EXECUTED   = NO
```

**`CROSS_LANGUAGE_SEARCH_DESIGN = READY`** é sobre o **desenho**, e o desenho está provado
ponta a ponta com dado de fixture: busca em espanhol acha material francês, e o nome
científico atravessa tudo. **Não** significa que o índice exista — `K7` e `K8` continuam
abertos.

**O que este contrato deliberadamente não faz:** não traduz o acervo, não cria banco por
idioma, não escolhe fornecedor de tradução, não mede custo e não toca no casco.
