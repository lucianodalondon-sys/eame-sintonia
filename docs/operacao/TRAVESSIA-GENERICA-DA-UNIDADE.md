# T-32 — A TRAVESSIA GENÉRICA DA UNIDADE — C-PLAN-A2

**Decisão contratual · 2026-09-10 · ramo `claude/raw-observation-identity-3jbwco`**

> **Nada foi implementado.** Zero runtime, zero `admissao.py`, zero schema, zero migration,
> zero banco, zero Bíblia, zero System Map. Este documento **mede e decide**.

Pergunta única:

> **Como o T-32 atravessa uma unidade legítima até à Admission quando ela NÃO é PDF e
> alguma etapa intermediária não se aplica?**

---

## 0 · O ESTADO MEDIDO

| | |
|---|---|
| `BRANCH` | `claude/raw-observation-identity-3jbwco` |
| `INITIAL_HEAD` | `0958d514355ab183b4b979b79291aee57849c322` |
| `WORKTREE` | limpa |

> ⚠️ **O `KNOWN HEAD` da missão estava desactualizado.** Ela deu `4019d433`. O `origin` já ia
> em `0958d514` — outra sessão publicou `docs/operacao/IDEIAS-E-PENDENCIAS.md`, 330 linhas,
> só documento. Fiz `fast-forward`, não `force`: **o trabalho do outro não se atropela.**

---

## 1 · A RESPOSTA CURTA, E ELA É MELHOR DO QUE SE ESPERAVA

> ## O CONTRATO DE TRAVESSIA GENÉRICA JÁ EXISTE.
> ## ESTÁ EM TRÊS LEIS DESTA CASA, ESCRITO ANTES DESTA MISSÃO.
> ## O T-32 É A ÚNICA PEÇA QUE NÃO O FALA.

```
leis/telemetria.py:88-96     ESTADOS_DE_ETAPA — sete estados, e um deles e NOT_APPLICABLE
leis/telemetria.py:110-113   ETAPAS_DA_COLETA — nove etapas canonicas, dono e a LEI
leis/artefato.py:71-73       NAO_SEI vs NAO_SE_APLICA — a definicao, ja escrita
supabase/migrations/024:74   create type etapa_estado as enum (... 'NOT_APPLICABLE')
```

E o T-32 emite, hoje, **apenas dois** desses estados:

```
$ grep -o "estado='[A-Z_]*'" coleta/rota_forward_documento.py | sort -u
  :126 estado='FAIL'      :194 estado='FAIL'
  :215 estado='FAIL'      :328 estado='NOT_RUN'
```

**`NOT_APPLICABLE` nunca é escrito por nenhum ficheiro de runtime desta casa.** O vocabulário
está no contrato, no enum do Postgres, e não sai da gaveta.

---

## 2 · POR QUE O T-32 SÓ FUNCIONA COM PDF — e a razão é dupla

### 2.1 A derivação tem forma de PDF

```python
# coleta/rota_forward_documento.py:252
return deriv.correr(
    [{'RAW_ASSET_ID': unidade['RAW_ASSET_ID'], 'PDF': unidade['PDF']}], ...)
```

`unidade['PDF']` é indexação directa: uma unidade sem PDF levanta `KeyError` antes de
qualquer etapa. E `derivacao_forward.correr` desagua em `executor_texto_de_pdf`.

### 2.2 A estruturação tem forma de REDE SOCIAL — e este é o problema maior

```python
# coleta/rota_forward_documento.py:117
recibo = sp.persistir_video(banco, canal_id=canal_id, ..., texto_canonico=unidade['TEXTO'])
```

`persistir_video` escreve `public.conteudo`, cuja identidade é `UNIQUE (canal_id, content_id)`
(`003:57`). `canal_id` exige uma `origem`, que tem `constraint` a exigir **pessoa OU
organização**. Um boletim da ARPAV não tem canal.

E a casa **já mediu isto e já o chamou pelo nome** — está no próprio teste que faz a M2 passar:

> *«`exigir_canal` devolve `CHANNEL_IDENTITY_NOT_RESOLVED` porque criar um canal exige
> decidir DE QUEM ele é … **Nenhum dono forward resolve isto hoje.** Aqui a identidade é
> resolvida NO BANCO DESCARTÁVEL»*
> — `tests/test_m2_rota_forward.py:129-146`

> ## O T-32 É UMA QUIMERA.
> ## A ETAPA DE CIMA TEM FORMA DE PDF. A DE BAIXO TEM FORMA DE CANAL.
> E ele não «funciona com PDF»: ele funciona porque **um teste inventou uma organização**
> para o PDF ter canal.

Há uma terceira marca da mesma costura: `estruturar()` fixa `edge_from='DERIVED'`
(`:151, :191`) sem perguntar se a derivação aconteceu. Para uma unidade sem derivação, essa
aresta **mentiria**.

---

## 3 · AS QUATRO CLASSES — com fixture real, medida

Nenhum exemplo é fictício. Cada classe abaixo aponta um ficheiro que existe nesta árvore.

| classe | fixture real | n |
|---|---|---|
| **A** documento/PDF | `data/derivados/REGISTO-DE-ARTEFATOS.json` · `data/collection-store/italy/` | 43 derivados · 10 PDF |
| **B** publicação social com texto nativo | `data/samples/SENSOR-PILOT/VIDEOS-A.json` | 221 itens, **221** com `TITLE` **e** `DESCRIPTION` |
| **C** mídia que vira texto | `data/samples/ES-T8-001-transcricoes.json` | 15 transcrições |
| **D** tabular/estruturado já parseado | `data/collection-ledger/italy/observations.ndjson` · `IT-T2-004` | 6 observações com `OBSERVATION_KEYS` |

### A medição que parte a classe C em duas

```
CAPTION_SOURCE       {'PLATFORM_CAPTIONS via Apify (rota paga)': 15}
DERIVATION_TYPE      {'TEXT_EXTRACTION': 43}      ← zero TRANSCRIPTION
TRANSCRIPT_AVAILABLE {'NOT_TESTED': 221}
```

**As 15 transcrições que esta casa tem não são derivações nossas: são legendas buscadas na
plataforma.** Uma legenda que se vai buscar é um `FETCH` — é RAW, com a sua própria
observação, não um filho dos nossos bytes. Transcrição por máquina existe no esquema
(`022`: `kind='TRANSCRIPTION'`, `producer='whisper'`, `producer_version` obrigatório) e nas
ferramentas (`ferramentas/youtube_transcrever.py`) — e tem **zero** artefatos reais.

E `TRANSCRIPT_AVAILABLE = NOT_TESTED` em 221 de 221 é o exemplo perfeito do §17: é `UNKNOWN`
**sobre o conteúdo**, não estado de pipeline. Ninguém foi ver. Não é falha de etapa nenhuma.

---

## 4 · A SONDA — as quatro classes contra a porta, sem tocar na porta

Montei um item por classe **a partir dos fixtures acima**, declarando a espécie, e perguntei
ao `admissao.py` tal como ele está hoje:

```
A · PDF -> texto derivado     ESTAGIO DOCUMENTO   LINHAGEM SIM «o pai esta declarado»
B · social, texto nativo      ESTAGIO DOCUMENTO   LINHAGEM SIM «e o original: nao tem pai, e nao devia ter»
C · legenda de plataforma     ESTAGIO DOCUMENTO   LINHAGEM SIM «e o original: nao tem pai, e nao devia ter»
D · tabular normalizado       ESTAGIO DOCUMENTO   LINHAGEM SIM «e o original: nao tem pai, e nao devia ter»
```

> ## AS QUATRO CLASSES JÁ PASSAM A PERGUNTA DA LINHAGEM.
> ## COM ZERO ALTERAÇÃO EM `admissao.py`.
> ## E NENHUMA PRECISA DE UM PAI INVENTADO.

A chave está numa linha que já lá estava (`admissao.py:189-190`):

```python
if item.get("artifact_type") == "RAW":
    return SIM, "e o original: nao tem pai, e nao devia ter", {}
```

**A porta já sabe que um original não tem pai.** Declarar `artifact_type='RAW'` não é um
truque para passar: é dizer a verdade sobre a espécie. O que o T-32 faz hoje — omitir a
espécie — é que produz `ESTAGIO_DESCONHECIDO`, régua do FATO e `NAO_SEI` (medido na C-PLAN-A).

**Honestidade sobre esta sonda.** Ela prova o **estágio** e a **linhagem**. Os vereditos de
universo que saíram (`NAO_SEI`, `NAO`, `SIM`, `NAO_SE_APLICA`) são respostas sobre o
**conteúdo** de cada fixture, e o texto da classe D foi por mim resumido em vez de trazer as
linhas normalizadas inteiras. **Não uso nenhum desses vereditos como prova de nada.**

---

## 5 · AS QUATRO TRAVESSIAS

### A · DOCUMENTO / PDF

```
SOURCE FORM         PDF publicado numa URL
RAW FORM            os bytes do PDF, em raw_asset
DERIVED NEEDED?     YES   — TEXT_EXTRACTION (leis/artefato.py:85)
DERIVED OUTPUT      texto, com parent_sha256 = sha do PDF
STRUCTURED NEEDED?  YES
STRUCTURED OUTPUT   um registo com o texto canónico
ADMISSION ITEM      artifact_type = DERIVED · parent_artifact_id declarado
LINEAGE REQUIRED    SIM — um derivado sem pai não se confere contra o original
CURRENT PATH        funciona, com um canal inventado por um teste
TARGET T32 PATH     RAW → DERIVED(PASS) → STRUCTURED → ADMISSION
```

### B · PUBLICAÇÃO SOCIAL COM TEXTO NATIVO

```
SOURCE FORM         post/vídeo com TITLE + DESCRIPTION
RAW FORM            o payload preservado, em raw_asset
DERIVED NEEDED?     NAO_SE_APLICA
DERIVED OUTPUT      nenhum — e nenhum se fabrica
STRUCTURED NEEDED?  YES
STRUCTURED OUTPUT   corpo_canonico(titulo=, descricao=)  ← social_persistencia.py:150
ADMISSION ITEM      artifact_type = RAW · sem pai, e sem pai é o correcto
LINEAGE REQUIRED    SIM, e é a do próprio RAW
CURRENT PATH        impossível: unidade['PDF'] levanta KeyError
TARGET T32 PATH     RAW → DERIVED(NOT_APPLICABLE, com razão) → STRUCTURED → ADMISSION
```

O texto canónico **não precisa de ser inventado**: o dono do STRUCTURED já o define, com
versão (`CORPO_VERSAO = 'v1:titulo+descricao'`) e já explica o que fica de fora — contadores
que mudam sozinhos, e qualquer marca da corrida.

### C · MÍDIA QUE VIRA TEXTO — dois caminhos, e a medição separa-os

```
C1 · LEGENDA DE PLATAFORMA          (15 de 15 casos reais)
  SOURCE FORM       legenda servida pela plataforma
  RAW FORM          a legenda, preservada — é um FETCH, não uma derivação nossa
  DERIVED NEEDED?   NAO_SE_APLICA
  ADMISSION ITEM    artifact_type = RAW
  TARGET T32 PATH   RAW → DERIVED(NOT_APPLICABLE) → STRUCTURED → ADMISSION

C2 · TRANSCRIÇÃO POR MÁQUINA        (0 casos reais — NÃO SEI como prática)
  SOURCE FORM       áudio/vídeo
  RAW FORM          os bytes do media
  DERIVED NEEDED?   YES — kind = 'TRANSCRIPTION', parent_sha256 = sha do media
  DERIVED OUTPUT    o transcript, com producer + producer_version obrigatórios
  ADMISSION ITEM    artifact_type = DERIVED · parent declarado
  TARGET T32 PATH   RAW → DERIVED(PASS) → STRUCTURED → ADMISSION
```

> **Ir buscar não é derivar.** Uma legenda que a plataforma serve é outra observação da
> mesma fonte, por outro endpoint. Tratá-la como derivada faria a casa dizer que produziu um
> texto que nunca produziu.

### D · TABULAR / API / JÁ ESTRUTURADO

```
SOURCE FORM         CSV, ODS, HTML tabular, payload de API
RAW FORM            os bytes, preservados antes de qualquer parse
DERIVED NEEDED?     NAO_SE_APLICA — o parse produz REGISTOS, não um artefato-texto
DERIVED OUTPUT      nenhum
STRUCTURED NEEDED?  YES — é aqui que o normalizador entrega
STRUCTURED OUTPUT   linhas com chave própria (IT-T2-004: OBSERVATION_KEY por estação-data-variável)
ADMISSION ITEM      artifact_type = RAW; e se a linha trouxer sujeito e predicado, a porta
                    reconhece-a como FATO sozinha (MARCAS_DE_FATO, admissao.py:214)
CURRENT PATH        `guarda/catalogo_importar.py` normaliza direto, sem etapa DERIVED nenhuma
TARGET T32 PATH     RAW → DERIVED(NOT_APPLICABLE) → STRUCTURED → ADMISSION
```

---

## 6 · `NAO_SE_APLICA` — a definição já estava escrita

```
leis/artefato.py:71-73

  «Não sei» é uma confissão: o valor existe algures e eu não o alcancei.
  «Não se aplica» é uma constatação: a pergunta não faz sentido para isto.
  Juntá-las apaga a diferença entre um buraco a tapar e um campo que está certo.
```

E os sete estados de etapa, cada um com o seu significado (`leis/telemetria.py:88-96`):

| estado | significa |
|---|---|
| `NOT_RUN` | nunca começou — a montante falhou, ou não chegou a vez |
| `RUNNING` | a correr |
| `PASS` | correu e entregou |
| `PARTIAL` | correu e trouxe parte, com o resto explicado |
| `FAIL` | correu e quebrou |
| `SKIPPED` | **decidido** não correr, com razão escrita |
| `NOT_APPLICABLE` | **não existe nesta rota**, com razão escrita |

`SKIPPED` e `NOT_APPLICABLE` não são sinónimos: o primeiro é uma escolha desta corrida
(orçamento, política), o segundo é uma propriedade da espécie. Um vídeo sem legenda é
`SKIPPED` se decidimos não transcrever agora; é `NOT_APPLICABLE` se a etapa não pertence
àquela rota.

### Quando é que `NAO_SE_APLICA` pode avançar — `CONDITIONAL`

A regra também já existe, e é estreita de propósito:

```
leis/telemetria.py:127-131   EXIGE_QUEM_ASSINE = {'READY': ('ADMISSION',)}
leis/telemetria.py:135       ETAPA_ACONTECEU  = ('PASS', 'PARTIAL')
```

Só **uma** etapa tem assinante obrigatório: `READY` exige `ADMISSION`. Nenhuma lei faz da
`DERIVED` assinante da `STRUCTURED`. Logo:

- `DERIVED = NOT_APPLICABLE` **avança**, porque nada exige que ela tenha assinado.
- `ADMISSION = NOT_APPLICABLE` **nunca deixa emitir READY**, porque `NOT_APPLICABLE` não está
  em `ETAPA_ACONTECEU`. A trava já está escrita e já tem função (`ready_sem_quem_assine`).

**A razão escrita é obrigatória** — e é aqui que está o único buraco medido, na §9.

### `ERROR` nunca avança — e isto já está implementado

Medido em `atravessar()`:

- derivação sem texto → devolve com `STRUCTURED: None`, `ADMISSION: None` e `PORQUE_PAROU`
  (`:308-311`);
- `STRUCTURED` fora de `('OK', REOBSERVADO)` → `ADMISSION` recebe `estado='NOT_RUN'` com
  `diagnostic_code = UPSTREAM_NOT_RUN` (`:326-334`).

```
ERROR_CAN_ADVANCE = NO   — e não é decisão nova: é comportamento que já lá está,
                           e que esta missão manda preservar.
```

Um `FAIL` também não pode ser reescrito como `NOT_APPLICABLE` para a cadeia seguir: são
estados diferentes, e o banco exige código de diagnóstico no `FAIL`
(`CONSTRAINT falha_tem_codigo`, `024:218`) — que o `NOT_APPLICABLE` não tem nem deve ter.

---

## 7 · A LINHAGEM QUANDO UMA ETAPA NÃO SE APLICA

> ## NÃO SE FABRICA `DERIVED_ID`.

A regra da casa para quem é o pai já está escrita, em `022`:

> *«O PAI DE VERDADE SÃO OS BYTES. … O `raw_asset_id` desta tabela diz apenas DE QUAL CÓPIA
> SE LEU. É testemunha, e está escrito assim na coluna — não se finge que é a identidade do
> pai.»*

Aplicada à travessia:

```
A continuidade da linhagem é carregada por DOIS campos que JÁ EXISTEM:

  edge_from            nomeia a ÚLTIMA etapa que aconteceu de verdade (PASS ou PARTIAL)
  last_good_artifact   nomeia o artefato dessa etapa

  supabase/migrations/024:141   edge_from  etapa_da_coleta   -- e o enum inclui 'RAW'
  supabase/migrations/024:204   last_good_artifact text
```

Portanto, com `DERIVED = NOT_APPLICABLE`:

```
etapa      = STRUCTURED
edge_from  = 'RAW'          ← e NAO 'DERIVED', que e o que o codigo fixa hoje
parent     = a observacao RAW: o seu id (ocorrencia) + o seu sha256 (conteudo)
```

Isto encaixa, campo a campo, no que a C-PLAN-0 fechou: `RAW_OBSERVATION_ID` é o surrogate da
ocorrência, `CONTENT_SHA256` é a identidade dos bytes. **Nenhum identificador novo nasce, e
nenhum identificador falso se inventa.** A aresta simplesmente diz a verdade sobre de onde
veio.

E `output_count` de uma etapa `NOT_APPLICABLE` é **`NULL`, nunca `0`** — porque
`UNKNOWN != ZERO` já é lei (`telemetria.py:323`), e zero significaria «correu e não trouxe».

---

## 8 · O CONTRATO MÍNIMO QUE O T-32 ENTREGA À T-50

Medido campo a campo contra `admissao.py`, e **só o que é realmente lido**:

| campo | lido por | obrigatório? |
|---|---|---|
| `id` | `Decisao.item` | **sim** |
| `artifact_type` | `estagio()` `:217-227` | **sim** — é o que faltava e produzia a régua errada |
| `parent_artifact_id` **ou** `parent_sha256` | `_tem_pai()` `:183-195` | **só se** `artifact_type = DERIVED` |
| `texto` | `_legivel()` · `_do_universo()` | **sim** |
| `source_id` | `_tem_origem()` `:166` | **sim** (aceita `fonte` ou `url` em alternativa) |

E **dois argumentos de chamada, que não são campos do item**:

```
universo   ← recebido do T-04, que o recebeu do T-02. O T-32 TRANSPORTA.
corrida    ← o RUN_ID
```

Os campos que a C-PLAN-A tinha listado como candidatos e que a medição **rejeitou**:
`STAGE`, `RAW_OBSERVATION_ID`, `DERIVED_ID`, `STRUCTURED_ID`, `LINEAGE_STATE` — a porta não
lê nenhum deles. Eles pertencem ao rastro (`etapa_da_corrida`), não ao item.

> **`ITEM_TYPE` e `artifact_type` são o mesmo campo com dois nomes.** Fica `artifact_type`,
> que é o que o código já lê. Um nome novo para um campo existente é drift com boas intenções.

Campos como `fact_time`, `source_location`, `fact_location` e `captured_at` **não** entram no
mínimo: a régua do DOCUMENTO não os pergunta, e a construção do READY é do T-52 — fora desta
missão, por instrução.

---

## 9 · O QUE FALTA, E É PEQUENO E EXACTO

O `NOT_APPLICABLE` exige razão escrita. E **não há onde a escrever**.

As 38 colunas de `etapa_da_corrida` (`024:133-224`) não têm campo de motivo. O que existe:

- `diagnostic_code` — só é forçado no `FAIL` (`rastro:105-106`), e o registo de códigos não
  tem nenhum que signifique «não se aplica». **Um N/A não é um diagnóstico.**
- `error_message_redacted` — é para erro. Um N/A não é erro.

E a assimetria fica visível na própria tabela:

```sql
CONSTRAINT falha_tem_codigo CHECK (estado <> 'FAIL' OR diagnostic_code IS NOT NULL)
-- ... e NAO ha o par:
-- CONSTRAINT nao_se_aplica_tem_razao
```

A casa já enforça isto noutro sítio — `censo_das_estradas_it.py:355-358` recusa um
`NOT_APPLICABLE` sem `NOT_APPLICABLE_REASON` — mas no censo, não na tabela da corrida.

```
SCHEMA_IMPACT_FUTURO (sem SQL, e não para esta missão):
  · etapa_da_corrida ganha uma coluna de razão para NOT_APPLICABLE e SKIPPED
  · e a trava simétrica de falha_tem_codigo
```

---

## 10 · O BLOQUEIO REAL PARA O 3→1 — e não é a travessia

A regra de travessia fecha. O que **não** fecha, e já não fechava antes desta missão:

```
TOPOLOGIA-DA-COLETA.md:89   STRUCTURED | 5 escritores, nenhum dono unico
                            gap STRUCTURED_SEM_DONO_LIGADO
```

O único escritor a que o T-32 está ligado é `persistir_video`, que exige canal. Enquanto
`STRUCTURED` não tiver um dono que aceite uma unidade sem canal, **a classe A precisa de uma
organização inventada e as classes B/C/D não têm por onde entrar**.

Isto é uma pergunta de **propriedade de etapa**, já registada, e não uma pergunta de
travessia. Mas é o bloqueio que a implementação do 3→1 encontra primeiro, e por isso está
aqui escrito em vez de ser descoberto depois.

---

## 11 · ENTREGA

| | |
|---|---|
| **A** `BRANCH` | `claude/raw-observation-identity-3jbwco` |
| **B** `INITIAL_HEAD` | `0958d514355ab183b4b979b79291aee57849c322` *(a missão declarou `4019d433`; o remoto já ia à frente)* |
| **D** `WORKTREE` | limpa |
| **E** `T32_CURRENT_SUPPORTED_UNIT_TYPES` | **1** — documento com PDF, e só com canal fabricado |
| **F** `T32_TARGET_SUPPORTED_UNIT_TYPES` | **4** — A · B · C · D, todas medidas com fixture real |
| **G** `PDF_PATH` | `RAW → DERIVED(TEXT_EXTRACTION, PASS) → STRUCTURED → ADMISSION` |
| **H** `NATIVE_TEXT_PATH` | `RAW → DERIVED(NOT_APPLICABLE) → STRUCTURED(corpo_canonico) → ADMISSION` |
| **I** `AUDIO_VIDEO_TRANSCRIPTION_PATH` | **dois**: legenda de plataforma = `FETCH`, logo RAW, `DERIVED = NOT_APPLICABLE` (15/15 casos reais) · transcrição por máquina = `DERIVED kind='TRANSCRIPTION'`, pai = sha do media (**0 casos reais → NÃO SEI como prática**) |
| **J** `STRUCTURED_API_PATH` | `RAW → DERIVED(NOT_APPLICABLE) → STRUCTURED(normalizador) → ADMISSION` |
| **K** `DERIVED_ALWAYS_REQUIRED?` | **NO** |
| **L** `STRUCTURED_ALWAYS_REQUIRED?` | **YES** como etapa — com o bloqueio da §10 declarado |
| **M** `NAO_SE_APLICA_DEFINITION` | constatação de que a pergunta não faz sentido para esta espécie (`artefato.py:71-73`); na etapa, «não existe nesta rota, **com razão escrita**» (`telemetria.py:95`) |
| **N** `NAO_SE_APLICA_CAN_ADVANCE` | **CONDITIONAL** — avança quando nenhuma lei faz daquela etapa assinante da seguinte. Hoje só `READY` exige assinante (`ADMISSION`) |
| **O** `ERROR_CAN_ADVANCE` | **NO** — já implementado em `atravessar()`; a jusante fica `NOT_RUN` com `UPSTREAM_NOT_RUN` |
| **P** `LINEAGE_WHEN_STAGE_NA` | `edge_from` nomeia a última etapa que **aconteceu** (`PASS`/`PARTIAL`) e `last_good_artifact` o artefato dela. Com `DERIVED` N/A: `edge_from='RAW'`, pai = a observação RAW (id de ocorrência + `sha256`). Nenhum `DERIVED_ID` fabricado |
| **Q** `ADMISSION_ITEM_MINIMUM_CONTRACT` | item: `id` · `artifact_type` · `texto` · `source_id` · e `parent_artifact_id`/`parent_sha256` **só se** `DERIVED`. Argumentos: `universo` · `corrida` |
| **R** `UNIVERSE_SOURCE` | **T-02** `Pedido.alvo` |
| **S** `T32_CREATES_UNIVERSE` | **NO** no alvo — hoje cria, via `UNIVERSO_PADRAO = 'T3'`, já registado na C-PLAN-A |
| **T** `TRANSCRIPTION_OWNER` | o executor de transcrição. **`T-61` não existe como cartão neste repositório** — existem `ferramentas/youtube_transcrever.py`, `ferramentas/instagram_transcrever.py` e `derived_artifact.kind='TRANSCRIPTION'`. Identificador: **NÃO SEI**. Posição: **fechada** — é `DERIVED`, antes de `STRUCTURED` |
| **U** `T32_TRANSCRIPTION_ROLE` | **chamador, nunca decisor**. Não escolhe modelo, idioma nem parâmetro — tal como não decide como se extrai texto de um PDF |

### V · `UNRESOLVED_GENERIC_TRAVERSAL_QUESTIONS`

`UNRESOLVED_CRITICAL_TRAVERSAL_QUESTIONS = 0` — nenhuma das abertas é sobre **como uma
unidade atravessa**.

1. **`STRUCTURED` sem dono único** (`STRUCTURED_SEM_DONO_LIGADO`) e `CHANNEL_IDENTITY_NOT_RESOLVED`.
   Anterior a esta missão. É o **bloqueio prático do 3→1** — §10.
2. **Onde se escreve a razão de um `NOT_APPLICABLE`.** Coluna e trava em falta — §9.
3. **Transcrição por máquina tem zero casos reais.** A posição fecha; a prática é `NÃO SEI`
   até existir o primeiro.
4. **Duas casas para um transcript:** `transcricao` (`003`, filho de `conteudo`, **depois** do
   STRUCTURED) e `derived_artifact` (`022`, filho dos bytes, **antes**). Pergunta de esquema,
   não de travessia.
5. **`edge_from='DERIVED'` fixo** em `estruturar()`. Consequência directa desta decisão, e
   entra na lista de chamadas a corrigir da C-PLAN-A.

---

## 12 · VEREDITO

```
T32_GENERIC_UNIT_CONTRACT     = CLOSED
PDF_PATH                      = CLOSED
TEXT_NATIVE_PATH              = CLOSED
TRANSCRIPTION_PATH_POSITION   = CLOSED
STRUCTURED_INPUT_PATH         = CLOSED
NAO_SE_APLICA_SEMANTICS       = CLOSED
ADMISSION_ITEM_CONTRACT       = CLOSED

T32_CAN_REPRESENT_NON_PDF        = YES
T32_DOES_NOT_FABRICATE_LINEAGE   = YES
NAO_SE_APLICA != ERROR           = YES
ERROR_CANNOT_BYPASS_STAGE        = YES
ADMISSION_RECEIVES_EXPLICIT_STAGE = YES
UNIVERSE_IS_INPUT                = YES
T32_REMAINS_EXECUTOR_NOT_SECOND_BRAIN = YES

UNRESOLVED_CRITICAL_TRAVERSAL_QUESTIONS = 0

C-PLAN-A2 = PASS
```

```
RUNTIME_FILES_CHANGED = 0
MIGRATIONS_CHANGED    = 0
DATABASE_MUTATIONS    = 0
BIBLE_CHANGED         = 0
SYSTEM_MAP_CHANGED    = 0
```

---

## 13 · EM PALAVRAS FÁCEIS

1. **Por que o T-32 hoje só funciona direito com PDF?** Porque não funciona direito nem com
   PDF. A etapa de cima exige um ficheiro PDF; a de baixo exige um canal de rede social. Só
   passa porque um teste inventou uma organização para o boletim ter canal.

2. **Como um post de Instagram com texto atravessa?** O texto nativo já é o texto. Não se
   deriva nada: a etapa de derivação fica `NAO_SE_APLICA`, com a razão escrita, e o título
   mais a descrição viram o corpo canónico que o dono do STRUCTURED já sabe montar.

3. **Como um vídeo com áudio atravessa?** Depende de onde vem o texto. Se a legenda foi
   buscada à plataforma, foi uma ida à fonte: é RAW, e não há derivação nossa. Se o áudio foi
   transcrito por nós, aí sim é um derivado, com o modelo e a versão declarados.

4. **Em que ponto acontece a transcrição?** Em `DERIVED`, antes do `STRUCTURED`. Filha dos
   bytes do media, nunca de um registo.

5. **Se uma etapa não serve para aquele tipo de conteúdo, o que acontece?** Escreve-se
   `NOT_APPLICABLE` com a razão. A etapa deixa linha, e a cadeia segue.

6. **Isso é diferente de erro?** Completamente, e a casa já tinha a frase: *«não sei» é uma
   confissão; «não se aplica» é uma constatação*. Erro pára a cadeia. Não se aplica não pára.

7. **Como mantemos a linhagem sem inventar um ficheiro que não existe?** A aresta passa a
   nomear a última etapa que aconteceu de verdade. Sem derivação, o pai é a própria
   observação RAW — o seu identificador e o seu hash. Nada de `DERIVED_ID` de fachada.

8. **O que exactamente chega à Admission?** Cinco campos: o identificador, **a espécie**, o
   texto, a origem, e o pai só quando é derivado. Mais o universo e a corrida, que são
   argumentos da chamada. Foi a espécie que faltava — só isso.

9. **O T-32 decide alguma coisa sobre o conteúdo?** Não. Ele chama quem transforma e conta o
   que aconteceu. Não escolhe universo, não escolhe transcritor, não julga item.

10. **Há bloqueio para começar o 3→1?** **Sim, um.** O `STRUCTURED` não tem dono único, e o
    único a que o T-32 está ligado exige um canal que um boletim não tem. Não é a travessia
    que falta: é o dono daquela etapa. Já estava registado no mapa antes desta missão.

> **HARD STOP.** A travessia genérica está fechada. Não se altera código.
