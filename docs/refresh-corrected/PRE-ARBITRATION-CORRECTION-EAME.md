# PASSAGEM DE CORREÇÃO PRÉ-ARBITRAGEM

**Data:** 2026-08-31 · **Branch:** `claude/eame-refresh-correction-pre-arbitration`
**Testemunha V1 preservada:** `eb18c87c7e75a3fe0f186c43ff5e60a83b28b0f1` — não reescrita.

```
NEW_COLLECTION = NO       NETWORK_REQUESTS = 0
CASCO_V7_MODIFIED = NO    V8_IMPLEMENTATION_STARTED = NO
```

> Tudo foi **re-derivado**. Nenhum número deste documento veio do texto do briefing:
> onde o valor derivado difere do que o red team estimou, **o artefato ganha** — e a
> diferença está anotada.

---

## 0 · OS SETE ERROS CORRIGIDOS

| # | erro | quem achou | estado |
|---|---|---|---|
| 1 | **parser de recorte quebrava por `_`** | red team | **confirmado e corrigido** |
| 2 | **o card do CASE 001 exibia a citação de SEPTORIA** para um caso de FUSARIUM | red team | **confirmado e corrigido** |
| 3 | *"o míldio francês veio de barra lateral"* — afirmação **larga demais** | red team | **confirmado e corrigido** |
| 4 | **`LAST_90D` do Deep Corpus errado** | red team | **confirmado** — eu copiei do briefing |
| 5 | **RAIF fora do escopo** | coordenador | **corrigido** — `FIELD_HISTORICAL_SCOPE = IN` |
| 6 | `ACT_NOW = 0` publicado **sem escopo** | coordenador | corrigido |
| 7 | julgamento editorial apresentado como medição | coordenador | corrigido |

E **dois erros que só apareceram nesta passagem**, ambos meus:

| # | erro | como apareceu |
|---|---|---|
| 8 | **o corpo dos documentos não está preservado** | minha primeira execução devolveu `fenologia = 0` em 22 de 22, e o zero parecia resultado |
| 9 | **o teste de "sem rede" confundia menção com uso** | reprovou o próprio script por causa de um comentário que dizia *"nenhum Apify"* |

---

## 1 · O PARSER DE RECORTE — bug confirmado, **um** recorte afetado

```
FR_VINE_DOWNY_MILDEW
  parser ingênuo (split "_") →  CROP = VINE_DOWNY   ISSUE = MILDEW      ← impossível
  schema explícito           →  CROP = VINE         ISSUE = DOWNY_MILDEW
```

**Auditei os seis.** Cinco funcionavam **por sorte**: só um tem `ISSUE` de dois tokens.
Sorte não é schema.

A correção não é um caso especial: o par agora vem do **contrato explícito** em
`PILOT-SCOPE-MATRIX-V1.json`, que já guardava `COUNTRY`, `CROP` e `ISSUE` em campos
separados. O split nunca deveria ter existido.

`MULTI_TOKEN_CROP_ISSUE_SLICE_GUARD = PASS`, com o parser ingênuo preservado no teste
como testemunha do erro.

---

## 2 · CASE 001 — auditado, e **sobrevive** com a citação certa

O documento LAMMA de Grosseto (23/04/2026) contém **dois boletins**: um de cereal e um de
videira. Rótulos do item: `CROP = [CEREAL, VINE]`, `ISSUE = [SEPTORIA, FUSARIUM,
DOWNY_MILDEW]`.

**O produto cartesiano daria 6 pares. Três foram recusados.** Os quatro que fecham:

| par | prova |
|---|---|
| `CEREAL × SEPTORIA` | *"...sia per il frumento tenero che per il duro. **Septoria** rimane la patologia principale"* |
| `CEREAL × FUSARIUM` | *"**Fusariosi** Si segnala la comparsa di sintomi lievi nel frumento duro"* |
| `VINE × DOWNY_MILDEW` | *"Le fasi fenologiche prevalenti sono 'grappoli visibili'... **Peronospora**"* |
| **`DURUM_WHEAT × FUSARIUM`** | **a mesma passagem de fusariose nomeia `frumento duro`** |

**Recusados:** `VINE × FUSARIUM`, `VINE × SEPTORIA`, `CEREAL × DOWNY_MILDEW`.

### O que o V1 errou, e o que estava certo por baixo

O card do V1 carregava a passagem de **SEPTORIA** — a primeira do dicionário de evidência —
num caso de **FUSARIUM**. Erro real de apresentação.

**Mas o caso em si sobrevive**, e por um motivo mais fino do que o V1 sabia: `DURUM_WHEAT`
**não está no rótulo do item** (que diz `CEREAL`). Ele aparece **dentro da passagem** que
sustenta a fusariose. O par fecha pela passagem, não pela etiqueta.

`FUSARIUM_QUOTE_MATCHES_ISSUE = PASS` · `CROP_ISSUE_PAIRING_NOT_PROVEN` implementado ·
`MULTI_BULLETIN_DOCUMENT_GUARD = PASS`.

**Seis documentos multi-boletim** entre os 22, e **6 pares cartesianos evitados** no total.

---

## 3 · FRANÇA — a minha afirmação era larga demais

O V1 disse: *"o `DOWNY_MILDEW` francês veio de barra lateral, e o guard o removeu"*.
Derivando item a item:

```
FR_VINE_DOWNY_MILDEW
  itens no país ............. 11
  com cultura ................ 9
  com problema NO CORPO ...... 4     ← o míldio SOBREVIVE em quatro itens
  com tempo .................. 7
  com localidade ............. 4
  com o par provado .......... 2
  com chave completa ......... 0
```

**Bloqueador exato, item a item:** `FALTA REGION` em 3 · `FALTA REGION + ISSUE` em 2 ·
`FALTA REGION + ISSUE + TIME` em 2 · `FALTA ISSUE` em 2 · `FALTA ISSUE + TIME` em 1 ·
`FALTA TIME` em 1.

**O guard removeu o míldio de alguns itens — não de todos.** Onde ele sobreviveu, o
bloqueador é **localidade**, não o problema. Minha frase do V1 apagava essa diferença.

```
FR_FULL_CASE_KEYS_V2 = 0    — mas por LOCALIDADE, e não porque o país não tem sinal
```

---

## 4 · DEEP CORPUS — eu tinha copiado o número errado

```
V1  ..... "442 materiais · 280 nos últimos 90 dias"
FREEZE .. LAST_90D = 164        (a509c12, CORPUS-DELIVERY.json)
```

**Os 280 vieram do texto do briefing anterior, não do artefato.** É exatamente o erro que
esta passagem foi mandada corrigir — e ele estava no meu documento. `CREATOR_LAST_90D = 164`,
derivado.

---

## 5 · RAIF ENTRA — sem comprar uma segunda perna

`FIELD_HISTORICAL_SCOPE = IN`, por decisão do coordenador. O que foi derivado:

```
amostragens 2026 .................. 20.970 · 7 províncias da Andaluzia
série preservada ................... 11 safras · 44.584 leituras
backtest: disparos ................. 14
backtest: falsos positivos ......... 11 dos 14 não precedem evento de escala 2026
conclusão do próprio artefato ...... não é motor de aviso de 6 a 12 meses
```

⚠️ **Divergência declarada, não resolvida:** o artefato de série preservado diz **11
safras**; o backtest diz *"série completa de 23 safras (2003-2026)"*. São unidades
diferentes e **não se escolhe a mais conveniente**.

### A independência que eu **não** comprei

O RAIF aparece **também como fonte territorial** (`ES-RAIF`, 4 itens). Portanto:

```
FIELD_HISTORICAL_RAIF ↔ TERRITORIAL_RAIF  =  SOURCE_DEPENDENCY
INDEPENDENCE_FROM_TERRITORIAL_RAIF        =  NOT_PROVED
```

`SAME_PUBLISHER` não prova `INDEPENDENT_OBSERVATION`, e a linhagem parcela-a-parcela não
está preservada. **Entrar no escopo não vira perna independente por decreto.**

E o `adama_link` do artefato — *"Neptune — fungicida ADAMA para repilo"* — é
`ADAMA_CONTEXT_DECLARED_IN_ARTIFACT`. **Não** é autorização local provada, nem encaixe de
produto, nem janela. `LOCAL_PRODUCT_AUTHORIZATION_PROVED = NOT_MEASURED`.

---

## 6 · O CORPO NÃO ESTÁ PRESERVADO — achado desta passagem

O coordenador autorizou *"reprocessar somente os 22 corpos já preservados"*. **Os corpos
não estão preservados.**

```
DOCUMENT_TEXT_PRESERVED  →  é um INTEIRO (11.333), a contagem de caracteres lidos
DOCUMENT_EXCERPT         →  3.000 caracteres
+ as passagens de CROP_EVIDENCE e ISSUE_EVIDENCE
```

Minha primeira execução procurou termos de fenologia **dentro de um inteiro** e devolveu
zero em 22 de 22 — e o zero parecia resultado. Corrigido: mede-se sobre o trecho, com o
escopo declarado em cada item (`TEXT_SCOPE = DOCUMENT_EXCERPT + EVIDENCE_PASSAGES`).

```
CROP_STAGE_AT_OBSERVATION ................ PROVADO em 3 de 22
APPLICATION_TRIGGER_AT_OBSERVATION ....... PROVADO em 5 de 22
CURRENT_CROP_STAGE_TODAY ................. NOT_PROVED em 22 de 22
CURRENT_APPLICATION_WINDOW ............... NOT_PROVED em 22 de 22
```

**E a janela de 2027 do V1 foi removida.** Eu havia escrito *"abril–maio de 2027"* porque
foi assim em 2026. Isso é fabricar calendário. `FUTURE_SEASON_WINDOW = NOT_ENOUGH_TIME_CONTEXT`.

---

## 7 · LATÊNCIA — medida, e com o limite na frente

```
fonte           n   dias entre publicação e captura
ES-RAIF         4   7 · 3.006 · 3.386 · 3.386
IT-LAMMA        1   130
FR-VIGNEVIN     7   56 · 56 · 75 · 95 · 103 · 110 · 172
                    medidos em 12 de 22 itens
```

⚠️ **O limite vem antes da leitura:** todos os itens têm o **mesmo** `CAPTURED_AT`
(2026-08-31) — foi uma captura única. Por construção, `SOURCE_LATENCY == AGE_OF_OBSERVATION`
em toda linha. Isto mede **idade do documento na primeira captura**, não latência de regime
de um pipeline com cadência. Separar as duas exige uma segunda captura, e não há coleta
autorizada.

**O que ainda assim se pode dizer:** para o CASE 001, a fonte publicou em **23/04** e o
sistema leu em **31/08**. O problema é de **captura**, não necessariamente de um sinal que
nasceu tarde. Os três itens RAIF de 3.000+ dias são documentos históricos numa listagem —
não atraso de pipeline.

---

## 8 · GRAFO DE DEPENDÊNCIAS V2 — tipado

O red team estimou **12 relações / 8 dependentes / 4 independentes**. O derivado:

```
RELATIONS_TOTAL ........ 17
RELATIONS_DEPENDENT .... 13
RELATIONS_INDEPENDENT ... 4     ← este bate
```

**O artefato ganha.** A diferença é que o V2 acrescentou relações que o V1 não tinha:
`REGULATORY_DEADLINE → registro nacional`, `SCIENCE_CORPUS → OPENALEX_INDEX`,
`FIELD_HISTORICAL_RAIF → TERRITORIAL_RAIF`, `MULTI_BULLETIN_DOCUMENT → CROP_ISSUE_PAIRING`
e `NATIONAL_REGISTRATION → FIELD_OBSERVATION`.

**Cinco tipos de dependência**, no lugar de um rótulo genérico:

```
SOURCE_DEPENDENCY · OBSERVATION_DEPENDENCY · ENTITY_DEPENDENCY
DERIVATION_DEPENDENCY · SEMANTIC_DEPENDENCY · INDEPENDENT_SOURCE
```

### As duas leis novas

**`SAME_INDEX ≠ SAME_EVIDENCE`.** OpenAlex é infraestrutura de **descoberta**. Dois artigos
achados pelo mesmo índice continuam sendo dois artigos. O que **é** dependência ali é o
`RESEARCHER_CORPUS` herdar a identidade resolvida pelo `EXPERT_DIRECTORY` — e essa é
`ENTITY_DEPENDENCY`, não de fonte.

**`SEMANTIC_MISMATCH_NOT_CORROBORATION`.** *"Fusarium observado em trigo duro em Grosseto"*
e *"produto autorizado para trigo duro × Fusarium"* são **fatos diferentes**. O segundo
oferece contexto de portfólio; **não confirma que o fenômeno de campo existe**. Não podem
somar como duas pernas da mesma proposição.

```
CONVERGENCE_REQUIRES = SAME_PROPOSITION + INDEPENDENT_EVIDENCE
```

E três tipos que **nunca entram no mesmo número**: `PHENOMENON_CONVERGENCE` ·
`IDENTITY_CONVERGENCE` · `CONTEXTUAL_ALIGNMENT`.

---

## 9 · RÓTULOS ITALIANOS — só medida de disponibilidade

```
LABEL_MANIFEST_TARGET ................ 163
LABELS_HASHED_IN_MANIFEST ............ 163   (manifesto declara COMPLETE, 100 %)
LOCAL_LABEL_PDFS_AVAILABLE_NOW ....... 139   (C:\eame-sintonia-it\data\raw\IT)
LOCAL_LABEL_PDFS_MISSING_NOW .......... 24
CROP_ISSUE_RECONSTRUCTION_MODE ....... LOCAL_REPROCESSING_POSSIBLE_PARTIAL
RECONSTRUCTION_EXECUTED .............. NO
```

**Manifesto completo com PDF ausente não é reprocessamento possível.** O SHA-256 preservado
prova que o arquivo existiu; **não substitui o arquivo**. Para os 24 ausentes o modo é
`RECOLLECTION_REQUIRED` — e nenhuma reconstrução foi executada.

---

## 10 · MEDIDO ≠ ESCRITO

Os intermediários legíveis por máquina agora existem, e cada linha separa três coisas:

```
EVIDENCE_INPUTS · DERIVATION_RULE · FACTS · INFERENCES · JUDGMENT_REQUIRED
```

`data/refresh-corrected/ATTENTION-CANDIDATES.json` e `ACTION-CANDIDATES.json`. A prosa dos
outros documentos consome isto — e não pode mais fingir que julgamento de produto é fato de
fonte.

**`CENTRAL_USER_ABSORPTION_GUARD`:** Market Development é usuário central **por decisão
arquitetônica**, não porque ocupou todas as linhas da tabela. Há prova de que existe ação
cujo dono não é MD.

**`ACTION_TYPE`** passa a separar `BUSINESS_DECISION` de `SYSTEM_DECISION` de
`INVESTIGATION`. Decidir reconstruir a tabela cultura × alvo é decisão **sobre o Sintonia**,
não ação de negócio de um departamento — e o V1 as misturava.

---

## 11 · O QUE NÃO MUDOU

```
CASE_MULTI_SIGNAL_CONVERGENCES ......... 0        (continua permitido, e continua sendo)
FULL_CASE_KEYS_V1 ...................... 1
FULL_CASE_KEYS_V2 ...................... 1        IT_DURUM_WHEAT_FUSARIUM
IDENTITY_CHAIN_CONVERGENCES ............ 36 tuplas · 29 produtos
URBOLE_GUARD ........................... PASS
```

O caso italiano **não caiu**. Ele mudou de fundamento: antes estava certo por acidente,
agora está certo por prova de passagem.

---

## 12 · SUÍTE

**504 provas, 0 falhas.** As 44 novas travam, uma a uma, os erros desta passagem —
inclusive o parser ingênuo, preservado no teste como testemunha.
