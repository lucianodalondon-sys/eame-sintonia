# STRUCTURED POR ESPÉCIE · DISPATCH SEM SEGUNDO CÉREBRO · CONTRATO DE `NOT_APPLICABLE`

**C-PLAN-A3 · decisão pré-implementação · 2026-09-10 · ramo `claude/raw-observation-identity-3jbwco`**

> **Nada foi implementado.** Zero runtime, zero `admissao.py`, zero schema, zero migration,
> zero banco, zero Bíblia, zero System Map.

Pergunta central:

> **Se STRUCTURED é etapa obrigatória, quem decide qual espécie de STRUCTURED uma unidade
> deve virar, e quem é o dono dessa espécie?**

Continua a [`TRAVESSIA-GENERICA-DA-UNIDADE.md`](TRAVESSIA-GENERICA-DA-UNIDADE.md).

---

## 0 · PRECHECK

```
BASE_CHECKPOINT_PRESENT = YES   1d707d31 é ancestor do remoto (é o próprio)
REMOTE_ADVANCED         = NO
FAST_FORWARD_DONE       = NO    não foi preciso
DIVERGENCE              = NO    0 commits locais à frente do remoto
LOCAL_HEAD  = REMOTE_HEAD = 1d707d31ea3142c51fcb7a073ccb291c0933ac27
WORKTREE    = limpa
```

---

## 1 · O ACHADO — a etapa STRUCTURED não é uma; são cinco, e só uma está ligada

O censo, limitado aos writers que a rota forward toca e aos seus imports imediatos:

| `CONCEPT_ID` | unidade | store | writer | identidade | pai declarado | ligado ao T-32? |
|---|---|---|---|---|---|---|
| `SOCIAL_CONTENT` | item de canal (vídeo, post) | `public.conteudo` | `coleta/social_persistencia.py::persistir_video` | `UNIQUE (canal_id, content_id)` | `raw_asset_id` ✔ | **SIM** — o único |
| `SOCIAL_COMMENT` | comentário | `public.comentario` | `social_persistencia.py` | — | `conteudo_id` | não |
| `SOCIAL_TRANSCRIPT` | legenda de um item | `public.transcricao` | ✖ **nenhum writer nesta casa** | `UNIQUE NULLS NOT DISTINCT (conteudo_id, idioma, caption_source)` | `raw_asset_id` ✔ **e** `conteudo_id` **not null** | não |
| `REGULATORY_REGISTRATION` | registro oficial | `public.registro_regulatorio` | `guarda/importar_italia.py` | `UNIQUE (pais, registration_id, fonte_versao)` | `raw_asset_id` ✔ | não |
| `CATALOG_PRODUCT_DOCUMENT` | documento de produto de fabricante | `public.catalogo_produto_documento` | `guarda/catalogo_importar.py` | — | `raw_asset_id` ✔ | não |
| **`OFFICIAL_BULLETIN`** (classe A) | boletim regional | ✖ **não existe** | ✖ | — | — | — |
| **`TABULAR_MEASUREMENT`** (classe D) | linha estação-data-variável | ✖ **não existe** | ✖ | — | — | — |

> ## O T-32 ESTÁ LIGADO A UMA ESPÉCIE DE CINCO,
> ## E É A ÚNICA QUE EXIGE CANAL.

**Correcção a uma suspeita minha:** `conteudo` **tem** `raw_asset_id` (`003:21`). Ele
consegue declarar a linhagem para o RAW. O problema não é linhagem — é `canal_id bigint
not null references public.canal(id)`. **O canal é estruturalmente obrigatório**, e é isso,
e só isso, que obriga a inventar uma organização para um boletim da ARPAV.

E `public.observacao` (`005`) **não** serve à classe D: é a camada analítica, tem
`base_denominador not null` e aponta para `conteudo`. É a jusante da inteligência, não o
STRUCTURED da coleta.

**`AUTHORITY_CONFLICT` encontrado, e a expansão pára aqui:** `guarda/catalogo_importar.py`
escreve `raw_asset` **e** `collection_run` directamente, além do catálogo — e o dono
canónico do RAW é `guarda/preservar_coleta.py`. Fica registado; não é pergunta desta missão.

---

## 2 · QUEM ESCOLHE A ESPÉCIE — os candidatos, medidos

| candidato | sabe ANTES da execução? | tem autoridade? | veredito |
|---|---|---|---|
| **Pedido** (T-02) | sabe o `alvo` (universo) | sobre o universo, sim | ✖ universo ≠ espécie: `T3` traz PDF (`IT-T3-002`), HTML (`IT-T3-005`) e social (`T9`) |
| **Receita/Plano** (T-03) | declara `larga_em`, `o_que_traz`, `rotas` | sobre o executor | ✖ é indexada por universo e descreve o **executor**, não a fonte |
| **Contrato de Fonte** | **sim** — 60+ campos por fonte, escritos antes | **sim** — é a autoridade sobre a fonte | ✅ **é este** |
| **Orquestrador** (T-04) | não | coordena, não interpreta | ✖ |
| **Executor** (T-1x) | só depois de correr | declara capacidades | ✖ tarde demais |
| **T-32** | recebe | nenhuma | ✖ **proibido** |
| **Writer do STRUCTURED** | é o destino | — | ✖ não se elege a si próprio |

```
STRUCTURED_TARGET_SELECTION_OWNER = O CONTRATO DE FONTE
                                    regras/italy_contracts.mjs (e irmãos por país)
```

**Por que ele e não outro:** é o único artefacto que existe **por fonte**, é escrito
**antes** de qualquer execução, e já declara as duas perguntas vizinhas — `OUTPUT_TYPE` (a
forma física) e `EVIDENCE_CLASS` (a espécie probatória). E a casa **já enforça declaração
obrigatória nesse ficheiro**: `regras/italy_contract_test.mjs:188` reprova qualquer contrato
sem `DOCUMENT_ID_RULE`. O padrão de «campo obrigatório no contrato de fonte, com guarda»
existe e está a correr.

### O que já lá está, medido nos 13 contratos

```
OUTPUT_TYPE      PDF(7) · HTML(3) · CSV(2) · ODS(1) · BROWSER_RENDERED_EXTRACT(1)
EVIDENCE_CLASS   AGROCLIMATIC_SIGNAL · REGULATORY_AUTHORIZATION · TECHNICAL_GUIDELINE
                 OBSERVED_FIELD_SIGNAL + COOPERATIVE · SCIENTIFIC_EVIDENCE
                 COMPANY_CLAIM · OFFICIAL_ORGANIZATION_REGISTRY · SERIE_OFICIAL_DE_PRODUCAO
```

`OUTPUT_TYPE` decide a **derivação** — não a espécie: `IT-T2-002` e `IT-T4-001` são ambos
documentos oficiais e vão para espécies diferentes. `EVIDENCE_CLASS` é o campo mais próximo
da espécie, e **medi-o antes de o adoptar**:

```
53 ficheiros de amostra declaram EVIDENCE_CLASS · ~20 valores distintos
e o valor e TEXTO LIVRE:
  "OBSERVED_FIELD_SIGNAL + COOPERATIVE"                      ← composto com " + "
  "SERIE_OFICIAL_DE_PRODUCAO (nem sinal de campo, nem preco)" ← prosa dentro do valor
  "SCIENTIFIC_EVIDENCE / retrospectiva oficial de campanha"   ← prosa dentro do valor
```

> **`EVIDENCE_CLASS` não serve como chave de dispatch, e a razão é medida:** ele responde
> «que peso probatório isto tem», não «que registo isto vira», e não é lista fechada.
> Despachar por texto livre seria adivinhar com um campo respeitável.

### A decisão

```
DISPATCH_INPUT      STRUCTURED_TARGET — declarado no CONTRATO DE FONTE, ao lado de
                    OUTPUT_TYPE e DOCUMENT_ID_RULE, com lista FECHADA e guarda
                    no mesmo sítio onde DOCUMENT_ID_RULE já e exigido.

DISPATCH_AUTHORITY  o contrato de fonte. O T-32 RECEBE e TRANSPORTA.

DISPATCH_REGISTRY   STRUCTURED_TARGET -> writer. NAO EXISTE.
                    Precedente de forma: pedido/receitas.py::EXECUTORES (T-06),
                    que ja e um registo de «id -> quem executa». Mesma forma,
                    outra pergunta. Nao se implementa nesta missao.

DISPATCH_FAILURE_IF_UNKNOWN
                    DOIS fracassos diferentes, e NENHUM fallback:
                    · contrato nao declara alvo  -> recusa nomeada
                      STRUCTURED_TARGET_NOT_DECLARED, estado FAIL.
                      NAO ha codigo equivalente em leis/diagnostico.py — e novo.
                    · alvo declarado, writer nao ligado -> OWNER_NOT_CONNECTED,
                      que JA EXISTE e diz exactamente isto:
                      «ha dono declarado para a etapa e ele nao toca o artefato.
                       OWNER EXISTS != EDGE EXISTS.»
```

Não é string mágica: é um campo de contrato, no ficheiro que já é dono das declarações por
fonte, com a guarda que já lá existe para o campo vizinho. **Medi o campo existente, disse
por que não serve, e a adição é a menor possível.**

### Os portões

```
T32_SELECTS_STRUCTURED_CONCEPT      = NO
T32_GUESSES_STRUCTURED_FROM_FIELDS  = NO
T32_GUESSES_SOCIAL_FROM_CHANNEL     = NO
```

Nunca `«tem title logo é social»`, `«tem PDF logo é documento»`, `«tem channel_id logo é
conteúdo»`. A casa já recusa este tipo de inferência noutro sítio, e com as mesmas palavras:
*«IDENTIDADE NUNCA POR SIMILARIDADE TEXTUAL»* (COL-LAW-034).

---

## 3 · AS QUATRO CLASSES

### A · DOCUMENTO / PDF — boletim agrometeorológico

```
SOURCE_FORM                          PDF numa URL de zona (IT-T2-002, ARPAV)
RAW_FORM                             bytes em raw_asset
DERIVED_REQUIRED                     YES · TEXT_EXTRACTION
LAST_REAL_ARTIFACT_BEFORE_STRUCTURED derived_artifact (sha do texto)
STRUCTURED_CONCEPT                   OFFICIAL_BULLETIN
STRUCTURED_OWNER                     ✖ NAO EXISTE
STRUCTURED_STORE                     ✖ NAO EXISTE
STRUCTURED_IDENTITY                  proposta: (source_id, document_id, document_version_id)
                                     — que o livro do coletor JA produz, 144/144
WHO_SELECTS_THIS_TARGET              contrato de fonte
WHO_TRANSFORMS                       executor de texto-de-PDF (ja existe)
WHO_PERSISTS                         ✖ NAO EXISTE
CAN_REACH_ADMISSION_WITHOUT_FAKE_IDENTITY = NO  (hoje)
```

**Não se reutiliza `conteudo`.** Um boletim não tem canal, e `canal_id` é `not null`. E não
se reutiliza `registro_regulatorio`: um boletim não é um registo, e a chave dele
(`pais, registration_id, fonte_versao`) não descreve um boletim.

### B · SOCIAL COM TEXTO NATIVO

```
SOURCE_FORM                          vídeo/post com TITLE + DESCRIPTION
RAW_FORM                             payload preservado em raw_asset
DERIVED_REQUIRED                     NO — NOT_APPLICABLE, com razão escrita
LAST_REAL_ARTIFACT_BEFORE_STRUCTURED a observação RAW
STRUCTURED_CONCEPT                   SOCIAL_CONTENT
STRUCTURED_OWNER                     coleta/social_persistencia.py
STRUCTURED_STORE                     public.conteudo
STRUCTURED_IDENTITY                  UNIQUE (canal_id, content_id)
WHO_SELECTS_THIS_TARGET              contrato de fonte
WHO_TRANSFORMS                       ninguém — corpo_canonico(titulo=, descricao=) é serialização, não derivação
WHO_PERSISTS                         social_persistencia.py
CAN_REACH_ADMISSION_WITHOUT_FAKE_IDENTITY = YES
```

Aqui o canal é **legítimo**: um vídeo tem mesmo um canal. Nada se inventa.

### C · LEGENDA BUSCADA NA PLATAFORMA

```
SOURCE_FORM                          legenda servida pela plataforma
RAW_FORM                             a legenda, preservada — é FETCH, não derivação nossa
DERIVED_REQUIRED                     NO — NOT_APPLICABLE. Nenhum pai DERIVED se cria.
LAST_REAL_ARTIFACT_BEFORE_STRUCTURED a observação RAW da legenda
STRUCTURED_CONCEPT                   SOCIAL_TRANSCRIPT
STRUCTURED_OWNER                     ✖ NÃO SEI — nenhum ficheiro desta casa escreve `transcricao`
STRUCTURED_STORE                     public.transcricao
STRUCTURED_IDENTITY                  UNIQUE NULLS NOT DISTINCT (conteudo_id, idioma, caption_source)
WHO_SELECTS_THIS_TARGET              contrato de fonte
WHO_PERSISTS                         ✖ não ligado
CAN_REACH_ADMISSION_WITHOUT_FAKE_IDENTITY = NO  (sem writer)
```

> ⚠️ **Medido, e é uma dependência real:** `transcricao.conteudo_id` é `not null`. A legenda
> exige que o `conteudo` do vídeo já exista. **A classe C depende da classe B.** Isso é
> ordem, não fabricação — e nada obriga a inventar um `conteudo` para uma legenda órfã: se
> o vídeo não foi estruturado, a legenda não atravessa, e diz-se porquê.

E `caption_source` já tem enum `('AUTO','MANUAL','MIXED','NAO_SEI')` — as 15 legendas reais
são `PLATFORM_CAPTIONS via Apify`, que não é nenhum dos quatro. Fica registado.

### D · TABULAR NORMALIZADO

```
SOURCE_FORM                          HTML/CSV/ODS tabular (IT-T2-004, SIAS)
RAW_FORM                             bytes preservados ANTES de qualquer parse
DERIVED_REQUIRED                     NO — o parse produz REGISTOS, não um artefato-texto
LAST_REAL_ARTIFACT_BEFORE_STRUCTURED a observação RAW
STRUCTURED_CONCEPT                   TABULAR_MEASUREMENT
STRUCTURED_OWNER                     ✖ NÃO EXISTE
STRUCTURED_STORE                     ✖ NÃO EXISTE  (`public.observacao` é camada analítica, não serve)
STRUCTURED_IDENTITY                  já existe no dado: `OBSERVATION_KEY` = estação · data · variável,
                                     6 observações do livro carregam-na
WHO_SELECTS_THIS_TARGET              contrato de fonte
WHO_TRANSFORMS                       o normalizador da fonte (já existe: `normalizarSias`)
WHO_PERSISTS                         ✖ NÃO EXISTE
CAN_REACH_ADMISSION_WITHOUT_FAKE_IDENTITY = NO
```

**Preservar RAW primeiro continua obrigatório**, mesmo quando a fonte entrega estrutura: o
coletor já o faz (`RAW_PRESERVED_BEFORE_PARSE: true` em 144/144 observações).

### O placar honesto

```
CLASSES COM CAMINHO STRUCTURED LIGADO HOJE:  1 de 4   (só B)
CLASSES SEM CONCEITO NENHUM:                 2 de 4   (A e D)
CLASSES COM CONCEITO E SEM WRITER:           1 de 4   (C)
```

---

## 4 · `CHANNEL_ID` — a classificação formal

```
CURRENT_STRUCTURED_PATH_IS_SOCIAL_SPECIFIC   = YES
CURRENT_PDF_TEST_FABRICATES_SOCIAL_IDENTITY  = YES
CHANNEL_ID_REQUIRED_FOR_DOCUMENT (hoje)      = YES, estruturalmente
CHANNEL_ID_REQUIRED_FOR_DOCUMENT (alvo)      = NO
```

A prova está no próprio teste que faz a M2 passar
(`tests/test_m2_rota_forward.py:129-160`): ele insere uma `organizacao` «ARPAV» e uma
`origem` no banco descartável para o boletim ter canal, e o comentário diz
`CHANNEL_ID PROVA O CANAL, NAO PROVA A ORIGEM` e **«Nenhum dono forward resolve isto hoje»**.

**O conserto não é relaxar `conteudo`.** `canal_id not null` está certo para a espécie
dele. O conserto é o documento ter a sua própria espécie. Reutilizar o canal seria a
fabricação, não a solução.

---

## 5 · LINHAGEM DA TRANSIÇÃO PARA STRUCTURED

```
STRUCTURED_ID              a chave natural da espécie (não um id novo e universal)
STRUCTURED_PARENT_STAGE    RAW | DERIVED — a última etapa que ACONTECEU (PASS ou PARTIAL)
STRUCTURED_PARENT_ID       RAW_OBSERVATION_ID  se PARENT_STAGE = RAW
                           DERIVED_ID          se PARENT_STAGE = DERIVED
STRUCTURED_CONCEPT         o CONCEPT_ID da espécie
STRUCTURED_CONTRACT_VERSION  a versão da regra do writer
SOURCE_ID                  da unidade
RUN_ID                     da corrida
```

**Onde cada campo mora, e não se duplica:**

- `STRUCTURED_PARENT_ID` quando o pai é RAW já tem coluna: `raw_asset_id`, e **as cinco
  espécies medidas têm-na** — `conteudo`, `transcricao`, `registro_regulatorio`,
  `catalogo_produto_documento`. Nada de novo.
- `STRUCTURED_PARENT_STAGE` **não mora no objecto**: mora na passagem, em
  `etapa_da_corrida.edge_from`, que é do tipo `etapa_da_coleta` e já aceita `'RAW'`.
- `STRUCTURED_CONTRACT_VERSION` já existe como `rule_version` nas espécies medidas.
- `RUN_ID` já existe em `conteudo`, `transcricao`, `registro_regulatorio`.

> **Nunca se cria um DERIVED só para manter a coluna preenchida.** Sem derivação, o pai é a
> observação RAW, e a aresta di-lo.

---

## 6 · O CONTRATO DE `NOT_APPLICABLE`

### O que está medido

```
NOT_APPLICABLE_STATE_SUPPORTED           = YES
    leis/telemetria.py:88-96          sete estados, e o significado escrito
    migrations/024:74-75              create type etapa_estado as enum (..., 'NOT_APPLICABLE')

NOT_APPLICABLE_REASON_SUPPORTED          = NO
    38 colunas em etapa_da_corrida, e NENHUMA e razao
    diagnostic_code   so e forcado no FAIL (rastro:105-106) e o registo de 17
                      codigos nao tem nenhum que signifique «nao se aplica»
    error_message_redacted  e para ERRO. Um N/A nao e erro.

NOT_APPLICABLE_REASON_CURRENT_LOCATION   = nenhuma, em etapa_da_corrida.
    O unico sitio onde a casa exige a razao e um CENSO, sobre JSON:
    system-map/scripts/censo_das_estradas_it.py:355-358  «N/A sem razao NAO vale»
```

E a assimetria está escrita na própria tabela:

```sql
CONSTRAINT falha_tem_codigo CHECK (estado <> 'FAIL' OR diagnostic_code IS NOT NULL)
-- e nao ha o par para NOT_APPLICABLE
```

### O contrato alvo mínimo — 2 campos novos, 2 já existentes

| campo | onde vive no alvo | existe? |
|---|---|---|
| `STAGE` | `etapa_da_corrida.etapa` | ✔ |
| `STATE = NOT_APPLICABLE` | `etapa_da_corrida.estado` | ✔ |
| `REASON_CODE` | lista fechada, no mesmo registo de `leis/diagnostico.py` | ✖ **novo** |
| `REASON_TEXT` | coluna nova | ✖ **novo** |
| `EVIDENCE` | cabe em `REASON_TEXT`; **não se cria terceiro campo** | — |
| `PREVIOUS_REAL_STAGE` | `etapa_da_corrida.edge_from` | ✔ |
| `PREVIOUS_REAL_ARTIFACT_ID` | `etapa_da_corrida.last_good_artifact` | ✔ |

```
NOT_APPLICABLE_WITHOUT_REASON_VALID = NO

NOT_APPLICABLE != NOT_RUN     N/A nao pertence a rota; NOT_RUN pertence e nao chegou a vez
NOT_APPLICABLE != FAIL        FAIL exige codigo de diagnostico; N/A nao e diagnostico
NOT_APPLICABLE != UNKNOWN     N/A e constatacao; UNKNOWN e ausencia de prova
NOT_APPLICABLE != SKIPPED     SKIPPED e escolha DESTA corrida; N/A e propriedade da ESPECIE
```

E `output_count` de uma etapa `NOT_APPLICABLE` é **`NULL`, nunca `0`** — `UNKNOWN != ZERO`
já é lei (`telemetria.py:323`), e `0` significaria «correu e não trouxe».

---

## 7 · PODE `NOT_APPLICABLE` AVANÇAR — por etapa, não por regra vaga

| `STAGE` | `MAY_BE_NOT_APPLICABLE` | `MAY_ADVANCE_AFTER_NA` | `NEXT_STAGE` | `REQUIRED_REASON` | prova |
|---|---|---|---|---|---|
| `DERIVED` | **YES** | **YES** | `STRUCTURED` | **YES** | `EXIGE_QUEM_ASSINE` só lista `READY`; nada faz de `DERIVED` assinante de `STRUCTURED` |
| `STRUCTURED` | **NO** | — | `ADMISSION` | — | **decisão, não lei medida** — ver abaixo |
| `ADMISSION` | **NO** | — | `READY` | — | `EXIGE_QUEM_ASSINE = {'READY': ('ADMISSION',)}` e `ETAPA_ACONTECEU = ('PASS','PARTIAL')`: N/A não é «aconteceu» |
| `READY` | **YES** | terminal | — | **YES** | `pronto_para_inteligencia` levanta `ValueError` para qualquer resultado != `SIM` (`admissao.py:433`) |

> **Honestidade sobre a linha do `STRUCTURED`.** Nenhuma lei desta casa proíbe
> `STRUCTURED = NOT_APPLICABLE`. É **decisão**, e a razão é esta: sem registo estruturado
> nada consegue responder depois «que unidade foi admitida», e o `ITEM_ID` do READY
> apontaria para algo que não persiste. `STRUCTURED_ALWAYS_REQUIRED = YES` continua a valer
> como decisão declarada, não como medição — e está escrito assim para ninguém a citar como
> lei.

---

## 8 · O T-32 DEPOIS DESTA DECISÃO

```
T32_OWNS_QUESTION   «esta unidade atravessou as etapas autorizadas, e o que ficou registado?»

T32_INPUT           unidade + universo + STRUCTURED_TARGET + run_id     (tudo RECEBIDO)
T32_OUTPUT          o recibo por etapa + a decisão da porta

T32_DECIDES         a ORDEM das chamadas · quando parar · o que escrever no rastro
T32_MUST_NOT_DECIDE a espécie do STRUCTURED · o universo · como derivar ·
                    como transcrever · se o item entra

T32_MAY_SKIP_STAGE_WHEN_CONTRACT_SAYS_NA        = YES, com razão escrita
T32_MAY_CREATE_FAKE_PARENT                      = NO
T32_MAY_CHOOSE_STRUCTURED_OWNER                 = NO
T32_MAY_CALL_ADMISSION_WITHOUT_STRUCTURED       = NO
T32_MAY_CALL_ADMISSION_WITHOUT_RAW_LINEAGE      = NO
```

---

## 9 · O QUE A ADMISSION RECEBE — e `admissao.py` não muda

```
ADMISSION_RECEIVES        um item, e os argumentos da chamada. Nao o registo do store.

  contrato da UNIDADE
    ITEM_ID               obrigatorio
    ARTIFACT_TYPE         obrigatorio  ← era o que faltava
    TEXTO                 obrigatorio
    SOURCE_ID             obrigatorio  (aceita `fonte` ou `url` em alternativa)
    PARENT                obrigatorio SO SE ARTIFACT_TYPE = DERIVED

  argumentos da CHAMADA
    UNIVERSE              vem do T-02, transportado
    RUN                   a corrida
```

```
STRUCTURED_ID_REQUIRED   = NO — a porta nao o le. A ligacao item->registo vive no
                           rastro (etapa_da_corrida), nao dentro do item.
ARTIFACT_TYPE_REQUIRED   = YES
PARENT_REQUIRED_WHEN     = ARTIFACT_TYPE = DERIVED
SOURCE_ID_REQUIRED       = YES
TEXT_REQUIRED_WHEN       = sempre — `_legivel` e a primeira pergunta das duas reguas
```

---

## 10 · AS QUATRO ROTAS COMPLETAS

Sem organização falsa, canal falso, derivado falso, pai falso ou fallback silencioso.

```
A · DOCUMENTO/PDF
  SOURCE ──[T-1x fetch]──▶ RAW ──[executor texto-de-pdf]──▶ DERIVED ──[?]──▶ STRUCTURED:OFFICIAL_BULLETIN ──▶ ADMISSION
   OWNER        executor            preservar_coleta         executor de texto      ✖ SEM DONO              admissao
   IDENTITY_IN  URL                 bytes                    raw sha256             derived sha256          item
   IDENTITY_OUT bytes               RAW_OBSERVATION_ID       derived sha256         (source,document,version) decisao
   LINEAGE      —                   run+source+document      parent_sha256 = raw    parent_stage=DERIVED    artifact_type=DERIVED
   STATE        PASS                PASS                     PASS                   ✖ BLOQUEADO             —

B · SOCIAL TEXTO NATIVO
  SOURCE ──▶ RAW ──[NOT_APPLICABLE]──▶ ( ) ──▶ STRUCTURED:SOCIAL_CONTENT ──▶ ADMISSION
   OWNER        preservar_coleta      —          social_persistencia          admissao
   IDENTITY_IN  payload               —          RAW_OBSERVATION_ID           conteudo
   IDENTITY_OUT RAW_OBSERVATION_ID    —          (canal_id, content_id)       decisao
   LINEAGE      run+source+content_id razao escrita  raw_asset_id · edge_from='RAW'  artifact_type=RAW, sem pai
   STATE        PASS                  NOT_APPLICABLE  PASS                    PASS

C · LEGENDA DE PLATAFORMA
  SOURCE ──▶ RAW ──[NOT_APPLICABLE]──▶ ( ) ──▶ STRUCTURED:SOCIAL_TRANSCRIPT ──▶ ADMISSION
   OWNER        preservar_coleta      —          ✖ SEM WRITER                 admissao
   IDENTITY_IN  legenda               —          RAW_OBSERVATION_ID + conteudo_id
   IDENTITY_OUT RAW_OBSERVATION_ID    —          (conteudo_id, idioma, caption_source)
   LINEAGE      run+source            razao escrita  raw_asset_id · edge_from='RAW'
   STATE        PASS                  NOT_APPLICABLE  ✖ BLOQUEADO             —
   ⚠️ depende de B: conteudo_id e not null

D · TABULAR
  SOURCE ──▶ RAW ──[NOT_APPLICABLE]──▶ ( ) ──▶ STRUCTURED:TABULAR_MEASUREMENT ──▶ ADMISSION
   OWNER        preservar_coleta      —          ✖ SEM DONO                   admissao
   IDENTITY_IN  bytes                 —          RAW_OBSERVATION_ID
   IDENTITY_OUT RAW_OBSERVATION_ID    —          OBSERVATION_KEY (estacao·data·variavel)
   LINEAGE      run+source+document   razao escrita  edge_from='RAW'
   STATE        PASS                  NOT_APPLICABLE  ✖ BLOQUEADO             —
```

---

## 11 · OS BLOQUEIOS, SEPARADOS

```
TRAVERSAL_CONTRACT_BLOCKERS
  NENHUM. A C-PLAN-A2 fechou a semantica e esta missao nao a reabriu.

STRUCTURED_CONTRACT_BLOCKERS
  1. STRUCTURED_TARGET nao e declarado em contrato de fonte nenhum
  2. nao ha registo STRUCTURED_TARGET -> writer
  3. OFFICIAL_BULLETIN  (classe A) nao existe como conceito
  4. TABULAR_MEASUREMENT (classe D) nao existe como conceito
  5. SOCIAL_TRANSCRIPT   (classe C) existe como tabela e nao tem writer

SCHEMA_BLOCKERS
  6. etapa_da_corrida nao tem REASON_CODE nem REASON_TEXT, e nao tem a trava
     simetrica de falha_tem_codigo
  7. leis/diagnostico.py nao tem codigo para STRUCTURED_TARGET_NOT_DECLARED
  8. tabela para OFFICIAL_BULLETIN e para TABULAR_MEASUREMENT

RUNTIME_BLOCKERS
  9.  T-32 indexa unidade['PDF'] direto
  10. T-32 fixa edge_from='DERIVED' em estruturar()
  11. T-32 chama sp.persistir_video sempre, sem despacho
  12. T-32 nunca emite NOT_APPLICABLE
  13. UNIVERSO_PADRAO='T3' (ja registado na C-PLAN-A)

NON_BLOCKING_MEASUREMENTS
  · machine transcription com 0 artefatos reais — NAO bloqueia a primeira
    implementacao documental/tabular
  · caption_source real («PLATFORM_CAPTIONS via Apify») fora do enum dos quatro
  · guarda/catalogo_importar.py escreve raw_asset e collection_run directamente,
    fora do dono canonico — AUTHORITY_CONFLICT = YES, registado e nao expandido
```

**A primeira implementação possível é a classe A**, e ela precisa de: 1 · 2 · 3 · 6 · 7 ·
8(parcial) · 9 · 10 · 11 · 12. Nada disto depende de transcrição.

---

## 12 · MACHINE TRANSCRIPTION

```
MACHINE_TRANSCRIPTION_IS_DERIVED    = YES
TRANSCRIPTION_PARENT                = o sha256 dos bytes do media (raw_asset.sha256)
TRANSCRIPTION_OUTPUT_ID             = derived_artifact.id, kind='TRANSCRIPTION',
                                      com producer + producer_version obrigatorios (022)
TRANSCRIPTION_STRUCTURED_TARGET     = SOCIAL_TRANSCRIPT quando o pai e um item de canal;
                                      para media que nao e de canal, NAO SEI — nao ha caso real
TRANSCRIPTION_OWNER                 = NAO SEI — nao ha autoridade runtime.
                                      Existem ferramentas (ferramentas/youtube_transcrever.py,
                                      ferramentas/instagram_transcrever.py) e zero artefatos.
                                      `T-61` nao existe como cartao neste repositorio.
```

Caminho conceitual, e só isso: `MEDIA RAW → TRANSCRIPTION DERIVED → STRUCTURED → ADMISSION`.

---

## 13 · O QUE JÁ EXISTIA vs O QUE FALTA

| | já existia | falta |
|---|---|---|
| estado `NOT_APPLICABLE` | lei + enum do Postgres | runtime que o escreva |
| razão do `NOT_APPLICABLE` | — | coluna, código e trava |
| linhagem sem derivação | `edge_from` · `last_good_artifact` · `raw_asset_id` nas 5 espécies | usá-los |
| espécie do item na porta | `estagio()` e a régua do DOCUMENTO | o T-32 declarar |
| autoridade sobre a fonte | contrato de fonte com 60+ campos e guarda | o campo `STRUCTURED_TARGET` |
| registo executor→id | `receitas.py::EXECUTORES` (T-06) | o análogo para STRUCTURED |
| espécie social | `conteudo` + writer ligado | nada |
| espécie documento e tabular | nada | tudo |

---

## 14 · PERGUNTAS QUE CONTINUAM `NÃO SEI`

1. Quem escreve `public.transcricao`. Nenhum ficheiro desta casa o faz.
2. Qual o dono runtime da transcrição por máquina. Ferramentas há; autoridade não.
3. Se `OFFICIAL_BULLETIN` e `TABULAR_MEASUREMENT` são duas espécies ou uma com dois grãos.
   **Não decido sem caso que obrigue** — a REGRA ZERO desta casa.
4. Se `EVIDENCE_CLASS` deve virar lista fechada ao lado de `STRUCTURED_TARGET`, ou fundir-se
   nele. São perguntas diferentes hoje; podem não ser amanhã.
5. Se `caption_source` ganha `PLATFORM_FETCHED` ou se as 15 legendas reais são `NAO_SEI`.

---

## 15 · VEREDITO

```
STRUCTURED_ALWAYS_REQUIRED              = YES   (decisão declarada, §7)
ONE_STRUCTURED_OWNER_PER_CONCEPT        = YES
STRUCTURED_TARGET_SELECTION_OWNER       = CONTRATO DE FONTE
T32_SELECTS_STRUCTURED_CONCEPT          = NO
T32_GUESSES_STRUCTURED_FROM_FIELDS      = NO
CHANNEL_ID_REQUIRED_FOR_DOCUMENT        = NO   (alvo)

PDF_STRUCTURED_PATH_DEFINED             = YES
SOCIAL_NATIVE_STRUCTURED_PATH_DEFINED   = YES
PLATFORM_CAPTION_STRUCTURED_PATH_DEFINED = YES
TABULAR_STRUCTURED_PATH_DEFINED         = YES

NOT_APPLICABLE_REASON_CONTRACT_DEFINED  = YES
NOT_APPLICABLE_WITHOUT_REASON_VALID     = NO

FAKE_DERIVED_REQUIRED       = NO
FAKE_PARENT_REQUIRED        = NO
FAKE_CHANNEL_REQUIRED       = NO
FAKE_ORGANIZATION_REQUIRED  = NO

ADMISSION_CHANGED = NO   RUNTIME_CHANGED = NO   DATABASE_CHANGED = NO

STRUCTURED_DISPATCH_CONTRACT_CLOSED = YES
NOT_APPLICABLE_CONTRACT_CLOSED      = YES
UNRESOLVED_CRITICAL_A3_QUESTIONS    = 0

C-PLAN-A3 = PASS
```

**Definido não é implementado.** Os quatro caminhos estão desenhados; três deles terminam
hoje num dono que não existe, e isso está escrito em cada um em vez de ficar subentendido.

> **HARD STOP.** O despacho por espécie e o contrato de `NOT_APPLICABLE` estão fechados.
> Não se altera código.
