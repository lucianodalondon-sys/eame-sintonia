# CONTRATO DOS STRUCTURED TARGETS — cardinalidade, conceitos e donos

**C-PLAN-A4 · último fechamento antes do plano de implementação · 2026-09-10**
**ramo `claude/raw-observation-identity-3jbwco`**

> **Nada foi implementado.** Zero runtime, zero migration, zero tabela, zero contrato de
> fonte alterado, zero T-32, zero Admission, zero Bíblia, zero System Map, zero coleta.

Continua [`TRAVESSIA-GENERICA-DA-UNIDADE.md`](TRAVESSIA-GENERICA-DA-UNIDADE.md) (A2) e
[`STRUCTURED-POR-ESPECIE-E-NOT-APPLICABLE.md`](STRUCTURED-POR-ESPECIE-E-NOT-APPLICABLE.md) (A3).

---

## 0 · PRECHECK

```
LOCAL_HEAD = REMOTE_HEAD = 2498b7e89d1d1170761bd99a27f0c354dd73117d
WORKTREE   = limpa
2498b7e8 é ancestor do remoto = SIM (é o próprio)   ·   DIVERGENCE = NO
```

---

## 1 · CORREÇÃO DE LINGUAGEM DA A3

A A3 publicou `ONE_STRUCTURED_OWNER_PER_CONCEPT = YES`. **Isso descreve o alvo, não o que
existe**, e a própria A3 media três conceitos sem dono. Fica corrigido:

```
TARGET_ONE_STRUCTURED_OWNER_PER_CONCEPT  = YES
CURRENT_ONE_STRUCTURED_OWNER_PER_CONCEPT = NO
```

Prova: `OFFICIAL_BULLETIN` sem dono · `TABULAR_MEASUREMENT` sem dono · `SOCIAL_TRANSCRIPT`
com store e sem writer. Um alvo escrito no presente lê-se como estado, e a partir daí
ninguém procura o buraco.

---

## 2 · A CARDINALIDADE — medida, não deduzida

> ## UMA FONTE PRODUZ MAIS DE UMA ESPÉCIE.
> ## E OS CONTRATOS DESTA CASA JÁ O DIZEM — EM TRÊS NOTAÇÕES DIFERENTES.

### Medição A · o livro italiano

```
SOURCE_ID     forma   documento   registos extraídos na MESMA observação
IT-T2-004     HTML    1           1045 linhas, com OBSERVATION_KEY (estação·data·variável)
IT-T3-005     HTML    1            139 pontos de monitorização, com lat/lon/data
IT-T2-002     PDF     1              0
IT-T4-001     CSV     1              0 extraídos — mas o contrato declara a linha
```

`IT-T2-004` e `IT-T3-005` produzem **duas espécies numa única ida à fonte**: o documento
que foi buscado, e os registos que estavam dentro dele.

### Medição B · os contratos já carregam a segunda identidade

| notação | onde | o que diz |
|---|---|---|
| campo separado | `IT-T3-005` | `IDENTITY_KEYS = ["periodo_do_bollettino"]` **e** `IDENTITY_KEYS_DO_PONTO = ["point_id","lat","lon","sampling_date"]` |
| prosa dentro do campo | `IT-T4-001` | `DOCUMENT_ID_RULE = "MINSALUTE:FTS6:{AAAAMMDD} · **por linha**: {num_registrazione}"` |
| prosa dentro do campo | `IT-T7-002` | `DOCUMENT_ID_RULE = "MASAF:OP:{DATA_DA_EDICAO} · **por linha**: {CODICE_IT}"` |
| chave da linha ocupando o campo do documento | `IT-T2-004` | `SIAS:{TABLE_TYPE}:{STATION}:{WINDOW_END}` — `STATION` é linha, não documento |
| idem | `IT-T1-001` | `ISTAT:{DATAFLOW}:{REF_AREA}:{TYPE_OF_CROP}:{TIME_PERIOD}` |

**5 dos 13 contratos já declaram um segundo grão**, e nenhum dos cinco o faz da mesma
maneira. A casa sabe há muito que a fonte produz duas coisas; **o que ela não tem é campo
onde o dizer**, e por isso escreveu-o na margem.

### Medição C · o lado social

Um único canal (`@agronotizietv`) chama, na mesma corrida:
`channels.list · playlistItems.list · videos.list · commentThreads.list` — e produz
`conteudo` **e** `comentario`. E o mesmo tipo de fonte produz `transcricao`
(15 reais em `ES-T8-001-transcricoes.json`).

```
SOURCE_TO_STRUCTURED_CARDINALITY = ONE_TO_MANY
```

**Consequência directa:** o campo singular `STRUCTURED_TARGET` proposto pela A3 é
**insuficiente**. Fica corrigido para uma lista.

---

## 3 · AS DUAS AUTORIDADES, E A PASSAGEM ENTRE ELAS

São duas perguntas, e confundi-las é o que faria o T-32 virar cérebro:

```
A) «QUE ALVOS ESTA FONTE PODE PRODUZIR?»    → antes da execução, por fonte
B) «QUE ALVO ESTA UNIDADE PRODUZIU?»        → só existe depois de a unidade existir
```

| candidato | sabe antes? | tem autoridade? | veredito |
|---|---|---|---|
| Contrato de Fonte | **sim** — já declara os dois grãos | **sim**, é dono da fonte | ✅ **(A)** |
| Pedido (T-02) | só o universo | sobre o universo | ✖ universo ≠ espécie |
| Plano/Receita (T-03) | indexado por universo, descreve o executor | sobre o executor | ✖ |
| **Executor** (T-1x) | é quem **cria** a unidade | sobre o que acabou de produzir | ✅ **(B)**, com trava |
| T-32 | recebe | nenhuma | ✖ **proibido** |

```
ALLOWED_STRUCTURED_TARGETS_OWNER = CONTRATO DE FONTE
RESOLVED_STRUCTURED_TARGET_OWNER = EXECUTOR, e SÓ dentro da lista permitida
```

**Por que o executor não vira segundo cérebro.** Ele não escolhe semântica: ele **rotula o
que acabou de produzir**, com um valor que o contrato já autorizou. É a mesma forma que
`derivacao_forward` já usa ao declarar `DERIVATION_TYPE` — o executor diz o que fez, não
decide o que devia ter feito. E a lista fechada é a trava: um alvo fora dela não tem
fallback.

```
RESOLVED_STRUCTURED_TARGET ∉ ALLOWED_STRUCTURED_TARGETS
  →  FAILURE = STRUCTURED_TARGET_NOT_ALLOWED · estado FAIL · sem fallback
ALLOWED_STRUCTURED_TARGETS ausente no contrato
  →  FAILURE = STRUCTURED_TARGET_NOT_DECLARED · estado FAIL · sem fallback
```

### O contrato da unidade que chega ao T-32

Só campos com equivalente medido nesta casa — nenhum nome novo por gosto:

| campo | equivalente que já existe | onde |
|---|---|---|
| `SOURCE_ID` | `SOURCE_ID` | livro do coletor, 144/144 · `_identidade()` do T-32 |
| `RUN_ID` | `run_id` | `collection_run`, todas as espécies |
| `RAW_OBSERVATION_ID` | `raw_asset.id` | fechado na C-PLAN-0 |
| `LAST_REAL_STAGE` | `etapa_da_corrida.edge_from` | `024:141`, enum já inclui `RAW` |
| `LAST_REAL_ARTIFACT_ID` | `etapa_da_corrida.last_good_artifact` | `024:204` |
| `RESOLVED_STRUCTURED_TARGET` | ✖ **não existe** | — |
| `STRUCTURED_CONTRACT_VERSION` | `rule_version` · `CORPO_VERSAO` | `conteudo`, `transcricao`, `registro_regulatorio` |

```
T32_STRUCTURED_DISPATCH_INPUT  = a unidade, já com RESOLVED_STRUCTURED_TARGET dentro
TARGET_WAS_RESOLVED_BY         = o executor
TARGET_ALLOWED_BY_SOURCE_CONTRACT = verificado pelo T-32 antes de despachar — ele CONFERE,
                                    não escolhe. Conferir não é decidir.
```

---

## 4 · OS NOMES DA A3 NÃO SOBREVIVERAM À MEDIÇÃO

### `OFFICIAL_BULLETIN` — **NÃO é conceito durável**

`OFFICIAL_BULLETIN_IS_DURABLE_CONCEPT = NO`

O coletor trata **os 7 tipos de fonte exactamente da mesma maneira** ao nível do documento:
144/144 observações têm `SOURCE_ID` + `DOCUMENT_ID` + `DOCUMENT_VERSION_ID`, seja um
boletim agrometeo, um guia técnico da AGRIOS, um CSV do Ministero ou uma página da ADAMA.
**«Boletim» é género, não unidade.**

E a casa já resolveu género assim, uma vez, e bem: `catalogo_produto_documento.tipo` é uma
**coluna com lista fechada** — `ADAMA_COMMERCIAL_LABEL · SDS · TECHNICAL_SHEET ·
REGISTRATION_SHEET · BROCHURE · CATALOG · GUIDE · TRIAL_DOCUMENT · OTHER_TECHNICAL_DOCUMENT`
— **dentro de UM conceito**. Nove géneros, um conceito. Precedente medido, não escolhido.

```
PROPOSED_CANONICAL_CONCEPT = SOURCE_DOCUMENT
```

**Por que é mais geral sem virar `STRUCTURED_GENERIC`:** tem uma unidade só (uma versão de
um documento de uma fonte), uma identidade só, e responde a **uma** pergunta —
*«que documento vimos, em que versão»*. E exclui explicitamente: registos extraídos,
comentários, transcrições e registos regulatórios, que têm grão próprio. Um conceito que
exclui quatro vizinhos não é genérico.

### `TABULAR_MEASUREMENT` — **NÃO é conceito durável**

`TABULAR_MEASUREMENT_IS_DURABLE_CONCEPT = NO`. É o nome do fixture SIAS.

A refutação é medida, e vem de dentro da mesma família:

- `IT-T4-001` é tabular, e as suas linhas **são registos regulatórios** —
  `REGULATORY_REGISTRATION`, conceito que **já existe, com store e writer**.
- `IT-T3-005` **não é tabular** e produz registos na mesma: 139 pontos de monitorização.

> **«Tabular» descreve o transporte, não a unidade.** Um conceito nomeado pelo formato de
> chegada é a mesma família de erro que nomear pela ferramenta ou pelo país.

```
PROPOSED_CANONICAL_CONCEPT = não é um; é a família RECORD, e a espécie decide-se
                             pelo que o registo É — nunca por como chegou.
```

Espécies de registo com identidade **já declarada no contrato**:

| espécie candidata | identidade declarada | onde | tem dono? |
|---|---|---|---|
| `REGULATORY_REGISTRATION` | `(pais, registration_id, fonte_versao)` | `006` | ✔ `importar_italia.py` |
| `AGROCLIMATIC_MEASUREMENT` | `["table_type","station","window_end"]` | contrato `IT-T2-004` | ✖ |
| `FIELD_MONITORING_POINT` | `["point_id","lat","lon","sampling_date"]` | contrato `IT-T3-005` | ✖ |

**As duas últimas não nascem nesta missão.** Têm unidade e identidade; não têm dono, store
nem consumidor — e a REGRA ZERO desta casa diz que não se constrói para caso que a medição
não obriga. Ficam **candidatas nomeadas**, não conceitos criados.

---

## 5 · A REGRA PARA NASCER UM CONCEITO — aplicada

Um conceito só existe separado se tiver `UNIT` · `IDENTITY` · `CONTRACT` · `OWNER` ·
`STORE` · `CONSUMER_OR_DECLARED_BOUNDARY`, e responder a pergunta própria.

### `SOURCE_DOCUMENT` — o único conceito que esta missão faz nascer

```
CONCEPT              SOURCE_DOCUMENT
UNIT                 uma VERSÃO de um documento de uma fonte
WHY_DISTINCT         responde «que documento vimos, em que versão» — que nenhum
                     registo, comentário, transcrição ou registo regulatório responde.
                     E a pergunta já é feita 144 vezes no livro do coletor.
IDENTITY             (SOURCE_ID, DOCUMENT_ID, DOCUMENT_VERSION_ID)
                     medida: 144/144, zero sentinelas, zero colisões (C-PLAN-0 §1.2)
OWNER_TARGET         novo dono de STRUCTURED documental
STORE_TARGET         nova tabela  ·  NUNCA public.conteudo
PARENT_RELATION      parent_stage = DERIVED quando houve derivação (parent = derived sha)
                     parent_stage = RAW      quando não houve  (parent = RAW_OBSERVATION_ID)
ADMISSION_RELEVANCE  é a unidade que a porta julga: artifact_type + texto + origem + pai
```

### E a pergunta crítica da §10 — **C: dois conceitos, e a casa já decidiu assim três vezes**

`o documento canónico + texto` **ou** `campos semânticos extraídos`?

```
catalogo_produto_documento   guarda o DOCUMENTO (url, tipo, bytes, sha, raw_asset_id,
                             download_state) — e NADA de semântica
catalogo_produto_*           guarda a SEMÂNTICA (agente, cultivo, dose, claim, modo_acao)
                             em tabelas irmãs

registro_regulatorio         guarda o REGISTO
registro_uso                 guarda os USOS dele

conteudo                     guarda o item
comentario · transcricao     guardam o que está ligado a ele
```

**Três famílias independentes, a mesma decisão.** Leitura documental e extracção semântica
são duas perguntas, logo dois conceitos. `SOURCE_DOCUMENT` guarda o documento e o texto
lido; o que se extrair dele é `RECORD`, com espécie própria.

---

## 6 · `SOCIAL_TRANSCRIPT` — a persistência é comum, a aquisição não

```
FETCH PLATFORM CAPTION  ≠  MACHINE TRANSCRIPTION  ≠  PERSIST SOCIAL TRANSCRIPT
```

As duas primeiras são aquisições diferentes (uma é `FETCH`, outra é `DERIVED` — A2 mediu:
15/15 legendas reais são buscadas, 0 transcrições de máquina). A terceira é **uma só**, e a
tabela já reflecte isso: `transcricao.caption_source` distingue a proveniência **dentro da
mesma linha**, e `raw_asset_id` aponta para os bytes de onde ela veio, sejam de que rota
forem.

```
SOCIAL_TRANSCRIPT_UNIT   o texto falado de UM item de canal, numa língua, com uma proveniência
OWNER_TARGET             o dono da persistência social — o mesmo de SOCIAL_CONTENT
                         (coleta/social_persistencia.py). NÃO é do transcritor:
                         quem adquire não é quem persiste, e a casa já separa isso
                         em todas as outras espécies.
STORE_TARGET             public.transcricao (já existe)
WRITER_TARGET            uma função nova em social_persistencia.py — não um módulo novo
IDENTITY_TARGET          UNIQUE NULLS NOT DISTINCT (conteudo_id, idioma, caption_source)
                         (já existe)

DEPENDS_ON_SOCIAL_CONTENT = YES — `conteudo_id` é `not null`
IF_SOCIAL_CONTENT_MISSING = NA, com razão escrita
```

**Por que `NA` e não `FAIL` nem `WAIT`:** a legenda não falhou e o pipeline não quebrou — a
etapa não se aplica *a esta unidade nesta corrida*, porque o item de que ela é filha não foi
estruturado. `WAIT` exigiria uma fila que esta casa não tem, e inventá-la aqui seria
construir para um caso não medido. **E não se fabrica `conteudo` para a legenda ter pai.**

⚠️ Medido e registado: as 15 legendas reais declaram `PLATFORM_CAPTIONS via Apify`, que
**não é** nenhum dos quatro valores do enum `caption_source ('AUTO','MANUAL','MIXED','NAO_SEI')`.

---

## 7 · REGULATORY E CATALOG — os dois controlos

```
REGULATORY_CONCEPT_CONFORMS_TO_TARGET_MODEL = PARTIAL
  identidade      ✔ UNIQUE (pais, registration_id, fonte_versao)
  pai             ✔ raw_asset_id
  fonte           ~ `fonte` é texto, não SOURCE_ID
  corrida         ✖ NÃO HÁ run_id — as 14 colunas não o incluem
  alvo explícito  ✖
  um dono         ✔ guarda/importar_italia.py

CATALOG_CONCEPT_CONFORMS_TO_TARGET_MODEL = PARTIAL
  identidade      ✔ UNIQUE (produto_id, document_id)
  pai             ✔ raw_asset_id, com DUAS travas que recusam «preservei» como opinião
  fonte/corrida   ✔ indirecto, via catalogo_captura (run_id · fonte_versao · rule_version)
  alvo explícito  ✖
  um dono         ~ guarda/catalogo_importar.py, que TAMBÉM escreve raw_asset e
                    collection_run — AUTHORITY_CONFLICT já registado na A3
```

> **`catalogo_produto_documento` é o melhor modelo que esta casa tem**, e é dele que
> `SOURCE_DOCUMENT` deve copiar a forma: identidade natural, pai por `raw_asset_id`, e
> travas que impedem um estado de download de mentir. Não se inventa modelo novo quando o
> bom já está escrito.

**Gap registado, não corrigido:** `registro_regulatorio` sem `run_id`.

---

## 8 · O REGISTO ALVO → DONO

A pergunta *«para o conceito X, que dono executa?»* é **lookup**, não política.

| candidato | veredito |
|---|---|
| contratos de fonte | ✖ são por FONTE; o registo é por CONCEITO — ficaria repetido 13 vezes |
| PLAN / POLICY | ✖ política decide; registo consulta |
| `receitas.py::EXECUTORES` | ✖ mesma **forma**, outra **pergunta** — não se misturam duas chaves numa tabela |
| **registo próprio** | ✅ |

```
STRUCTURED_OWNER_REGISTRY_OWNER  T-06, a mesma autoridade que já é dona do registo de
                                 executores — um dono de registos, dois registos
REGISTRY_UNIT                    uma linha por STRUCTURED_CONCEPT
REGISTRY_KEY                     STRUCTURED_CONCEPT
REGISTRY_VALUE                   writer + STRUCTURED_CONTRACT_VERSION + store
VERSIONED                        YES — precedente: rule_version, CORPO_VERSAO, VERSAO_DA_REGRA
ESCREVE                          gente, por commit — como EXECUTORES, «entra quando prova
                                 que percorre a rota; sai quando deixa de a percorrer»
LÊ                               T-04 e T-32.  T-32 SÓ LÊ.
NEW_COMPONENT_NEEDED             YES (não se cria aqui)
```

---

## 9 · `NOT_APPLICABLE` — o contrato semântico do código

O padrão de código de razão **já existe** nesta casa: `leis/diagnostico.py::CODIGOS` é um
registo fechado, com `valido()`, `dono()` e `explicar()`, e 17 códigos. Não se inventa
formato novo.

```
NOT_APPLICABLE_REASON_CODE_CONTRACT = REGISTRY   (a forma de leis/diagnostico.py)
REASON_TEXT_REQUIRED                = YES
UNKNOWN_REASON_ALLOWED              = NO
NOT_APPLICABLE_WITHOUT_CODE         = INVALID
NOT_APPLICABLE_WITHOUT_TEXT         = INVALID
```

**Um `NOT_APPLICABLE` cuja razão é desconhecida não é um `NOT_APPLICABLE` — é um `UNKNOWN`.**
A lei já separa as duas ausências (`artefato.py:71-73`), e deixar `UNKNOWN` entrar por aqui
apagaria a separação por dentro.

### Os códigos, e só os que a medição justifica

| código | quando | caso medido |
|---|---|---|
| `STAGE_NOT_REQUIRED_FOR_SPECIES` | a etapa não pertence a esta espécie | classe D: o parse produz registos, não artefato-texto |
| `SOURCE_ALREADY_PROVIDES_NATIVE_FORM` | a fonte já entregou a forma que a etapa produziria | classe B (título+descrição) e C (legenda buscada) |
| `UPSTREAM_SPECIES_NOT_STRUCTURED` | a etapa exige um pai estruturado que não existe | `SOCIAL_TRANSCRIPT` sem `conteudo` |
| `ADMISSION_NOT_SIM` | `READY` depois de um veredito que não é `SIM` | `pronto_para_inteligencia` já levanta `ValueError` |

**`NO_DERIVATION_NEEDED` foi descartado**: os casos que ele cobriria já estão nos dois
primeiros, vistos de ângulos diferentes. Um código que não separa nada é ruído com nome.

---

## 10 · CURRENT vs TARGET

| `STRUCTURED_CONCEPT` | `CURRENT_OWNER` | `CURRENT_STORE` | `TARGET_OWNER` | `TARGET_STORE` | `TARGET_STATUS` |
|---|---|---|---|---|---|
| `SOCIAL_CONTENT` | `social_persistencia.py` | `public.conteudo` | o mesmo | o mesmo | **KEEP** |
| `SOCIAL_COMMENT` | `social_persistencia.py` | `public.comentario` | o mesmo | o mesmo | **KEEP** |
| `SOCIAL_TRANSCRIPT` | ✖ nenhum | `public.transcricao` | `social_persistencia.py` | o mesmo | **OWNER_NEEDED** |
| `REGULATORY_REGISTRATION` | `importar_italia.py` | `registro_regulatorio` | o mesmo | o mesmo + `run_id` | **KEEP** (gap de proveniência) |
| `CATALOG_PRODUCT_DOCUMENT` | `catalogo_importar.py` | `catalogo_produto_documento` | o mesmo | o mesmo | **KEEP** (conflito de autoridade registado) |
| `SOURCE_DOCUMENT` *(era `OFFICIAL_BULLETIN`)* | ✖ | ✖ | a criar | a criar | **RENAME_CONCEPT + OWNER_AND_STORE_NEEDED** |
| `AGROCLIMATIC_MEASUREMENT` *(era `TABULAR_MEASUREMENT`)* | ✖ | ✖ | a decidir | a decidir | **SPLIT_CONCEPT** — candidata, não nascida |
| `FIELD_MONITORING_POINT` *(idem)* | ✖ | ✖ | a decidir | a decidir | **SPLIT_CONCEPT** — candidata, não nascida |

---

## 11 · PORTABILIDADE

| conceito | `PORTABILITY` | `COUNTRY_DELTA` |
|---|---|---|
| `SOURCE_DOCUMENT` | **CORE** | nenhum — a identidade é `(source, document, version)`, sem nada de italiano |
| `SOCIAL_CONTENT` · `COMMENT` · `TRANSCRIPT` | **CORE** | plataforma é dado, não estrutura |
| `REGULATORY_REGISTRATION` | **CORE** | já tem coluna `pais`; país é dado |
| `CATALOG_PRODUCT_DOCUMENT` | **CORE** | idem |
| `AGROCLIMATIC_MEASUREMENT` · `FIELD_MONITORING_POINT` | **CORE candidato** | por decidir com o segundo país — não se declara CORE com um caso só |
| valores dos contratos de fonte | **COUNTRY** | é o que muda por país, por construção |
| parser SIAS · parser TerreTruria | **COUNTRY adapter** | a espécie é CORE, o leitor é do país |

Nenhum conceito alvo é italiano por construção. O que é italiano são os **valores** e os
**leitores**, e ambos já vivem em ficheiros por país.

---

## 12 · O PRIMEIRO SLICE — remedido, e a A3 estava certa por uma razão que ela não deu

A A3 sugeriu a classe A. **Remedi contra a alternativa**, e o resultado inverte o critério
de «menos mudanças»:

| | slice A · `SOURCE_DOCUMENT` | slice B · social nativo |
|---|---|---|
| tabela nova | **SIM** | não |
| dono novo | **SIM** | não |
| colunas de razão do `NOT_APPLICABLE` | **não precisa** — a derivação corre (`PASS`) | **precisa** |
| fixture real | 10 PDF + 43 textos + 144 observações | 221 itens |
| bloqueio que sobra | engenharia | **`CHANNEL_IDENTITY_NOT_RESOLVED`** |

> ## O SLICE B PARECE MAIS BARATO E NÃO É.
> Ele não precisa de tabela nova, mas precisa que **uma pessoa decida de quem é cada canal**
> — `origem` exige pessoa **ou** organização, e `exigir_canal` recusa-se a inventá-la. Um
> primeiro slice que espera por uma decisão humana não é um primeiro slice.
> **O slice A só espera por trabalho.**

```
FIRST_IMPLEMENTATION_SLICE = classe A · SOURCE_DOCUMENT, de RAW a ADMISSION

WHY   único cuja identidade já está completa e medida (144/144), sem identidade falsa,
      sem decisão humana pendente, com pai declarável nos dois sentidos, e que prova o
      despacho por espécie ao mandar um documento para um dono que NÃO é o social.
      Termina em ADMISSION — nunca em READY, que continua sem consumidor.

REQUIRES_NEW_TABLE              YES   source_document
REQUIRES_MIGRATION              YES   a tabela; as colunas de razão do NA NÃO entram aqui
REQUIRES_SOURCE_CONTRACT_CHANGE YES   ALLOWED_STRUCTURED_TARGETS (lista, não campo singular)
REQUIRES_T32_CHANGE             YES   despachar por alvo · declarar artifact_type e pai ·
                                      parar de indexar unidade['PDF'] · edge_from real
REQUIRES_ADMISSION_CHANGE       NO
REQUIRES_SYSTEM_MAP_REGEN       YES   tabela e dono novos são arquitectura
```

---

## 13 · BLOQUEIOS

```
DISPATCH_BLOCKERS
  D1  ALLOWED_STRUCTURED_TARGETS não existe em contrato nenhum   slice A   MUST=YES
  D2  RESOLVED_STRUCTURED_TARGET não existe na unidade           slice A   MUST=YES
  D3  registo CONCEITO→DONO não existe                           slice A   MUST=YES

CONCEPT_MODEL_BLOCKERS
  C1  espécie do RECORD por fonte por decidir (SIAS, TerreTruria) slice futuro  MUST=NO
  C2  caption_source real fora do enum dos quatro                 slice C       MUST=NO

OWNER_BLOCKERS
  O1  SOURCE_DOCUMENT sem dono                                   slice A   MUST=YES
  O2  SOCIAL_TRANSCRIPT sem writer                               slice C   MUST=NO
  O3  catalogo_importar escreve raw_asset fora do dono canónico  nenhum    MUST=NO

STORE_BLOCKERS
  S1  não há tabela para SOURCE_DOCUMENT                         slice A   MUST=YES

SCHEMA_BLOCKERS
  E1  etapa_da_corrida sem REASON_CODE/REASON_TEXT e sem trava   slice B/C/D  MUST=NO p/ A
  E2  registo de códigos de razão não existe                     slice B/C/D  MUST=NO p/ A
  E3  registro_regulatorio sem run_id                            nenhum       MUST=NO

RUNTIME_BLOCKERS
  R1  T-32 indexa unidade['PDF'] direto                          slice A   MUST=YES
  R2  T-32 fixa edge_from='DERIVED'                              slice A   MUST=YES
  R3  T-32 chama persistir_video sempre, sem despacho            slice A   MUST=YES
  R4  T-32 não declara artifact_type nem pai no item             slice A   MUST=YES
  R5  T-32 nunca emite NOT_APPLICABLE                            slice B/C/D  MUST=NO p/ A
  R6  UNIVERSO_PADRAO='T3'                                       slice A   MUST=YES
```

**Nove bloqueios obrigatórios para o primeiro slice.** Nenhum deles é decisão em aberto:
todos são trabalho.

---

## 14 · O QUE CONTINUA `NÃO SEI`

1. Espécie canónica do registo de SIAS e de TerreTruria. Têm identidade declarada; não têm
   dono, store nem consumidor. **Não nascem sem caso que obrigue.**
2. Se `AGROCLIMATIC_MEASUREMENT` é CORE ou EAME. Um país só não decide portabilidade.
3. Quem persiste a transcrição na prática — decidi o **dono alvo**; o writer não existe.
4. Se `caption_source` ganha `PLATFORM_FETCHED` ou se as 15 legendas são `NAO_SEI`.
5. Se `SOURCE_DOCUMENT` guarda o texto lido ou aponta para o derivado que o contém.
   **Decisão do desenho da tabela**, no plano do slice — não muda o conceito.

---

## 15 · VEREDITO

```
SOURCE_TO_STRUCTURED_CARDINALITY          = ONE_TO_MANY
ALLOWED_STRUCTURED_TARGETS_OWNER          = CONTRATO DE FONTE
RESOLVED_STRUCTURED_TARGET_OWNER          = EXECUTOR, dentro da lista permitida
T32_RECEIVES_EXPLICIT_TARGET              = YES
T32_SELECTS_STRUCTURED_CONCEPT            = NO
STRUCTURED_OWNER_REGISTRY_DEFINED         = YES  (T-06; componente novo, não criado aqui)

TARGET_ONE_STRUCTURED_OWNER_PER_CONCEPT   = YES
CURRENT_ONE_STRUCTURED_OWNER_PER_CONCEPT  = NO

DOCUMENT_STRUCTURED_CONCEPT               = SOURCE_DOCUMENT
TABULAR_STRUCTURED_CONCEPT                = não é um conceito; é a família RECORD,
                                            com espécie por registo
SOCIAL_TRANSCRIPT_OWNER_TARGET            = coleta/social_persistencia.py

NOT_APPLICABLE_REASON_CODE_CONTRACT       = REGISTRY, fechado e versionado
FIRST_IMPLEMENTATION_SLICE                = classe A · SOURCE_DOCUMENT

STRUCTURED_CARDINALITY_CONTRACT_CLOSED    = YES
STRUCTURED_CONCEPT_MODEL_CLOSED           = YES
STRUCTURED_OWNER_MODEL_CLOSED             = YES
UNRESOLVED_CRITICAL_A4_QUESTIONS          = 0

READY_FOR_IMPLEMENTATION_PLAN_OF_FIRST_SLICE = YES
READY_FOR_RUNTIME_IMPLEMENTATION             = NO

RUNTIME_CHANGED = NO   DATABASE_CHANGED = NO   BIBLE_CHANGED = NO   SYSTEM_MAP_CHANGED = NO

C-PLAN-A4 = PASS
```

> **HARD STOP.** Cardinalidade, conceitos e donos estão fechados. O que segue é **plano** do
> primeiro slice — não implementação.
