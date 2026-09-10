# `SOURCE_DOCUMENT` — dono, casa e contrato

**C-PLAN-A5.1 · decisão pequena · 2026-09-10 · ramo `claude/raw-observation-identity-3jbwco`**

> **Nada foi implementado.** Zero migration, zero banco, zero runtime, zero T-32, zero
> Admission, zero READY, zero contrato de fonte, zero registo T-06, zero Bíblia, zero
> System Map.

A A4 fechou o conceito. Esta missão fecha **uma** coisa: onde ele mora, quem é o dono, e
**se o texto é copiado ou apontado**.

```
LOCAL_HEAD = REMOTE_HEAD = e6cb0f91870687be076635643e08fee507008d64
WORKTREE   = limpa   ·   divergência = 0
```

---

## 1 · A MEDIÇÃO QUE MUDA O DESENHO

Antes de decidir campos, medi a chave lógica contra o livro do coletor:

```
observações no livro                                 144
chaves (source_id, document_id, version_id) distintas  35
conteúdos sha256 distintos                             35
linhas que repetem uma chave já vista                 109
```

> ## `SOURCE_DOCUMENT` NÃO É UMA LINHA POR OBSERVAÇÃO.
> ## SÃO 35 VERSÕES DE DOCUMENTO PARA 144 OBSERVAÇÕES.

Exemplo medido: `IT-T3-005 · TERRETRURIA:31-08-2026:06-09-2026 · v1_2e488a8232ba` aparece em
**6 corridas diferentes**. É o mesmo documento, na mesma versão, visto seis vezes.

É a doutrina da C-PLAN-0 um andar acima:

```
RAW              a OCORRÊNCIA           144 linhas
SOURCE_DOCUMENT  a VERSÃO do documento   35 linhas
                 uma versão  →  N observações
```

Se `source_document` fosse uma linha por observação, o acervo diria que existem 144
documentos italianos. Existem 35, vistos 144 vezes.

---

## 2 · O DONO

```
SOURCE_DOCUMENT_OWNER = guarda/preservar_documento.py
```

**Nome por convenção medida, não por gosto.** Os três donos da mesma cadeia já vivem juntos
e já se chamam da mesma maneira:

```
RAW         guarda/preservar_coleta.py      «O DONO CANÓNICO DA ESCRITA»
DERIVED     guarda/preservar_derivado.py
STRUCTURED  guarda/preservar_documento.py   ← o irmão que falta
```

Ele responde a **uma** pergunta: *«que versão de que documento de que fonte foi
estruturada?»*

E não faz nada disto: coletar · baixar · extrair PDF · transcrever · decidir Admission ·
julgar conteúdo · decidir universo · orquestrar corrida. Como os dois irmãos, ele gera
escrita auditável e recebe a mão que a aplica por injecção — é o que permite provar contra
banco descartável sem tocar produção.

---

## 3 · A CASA

```
SOURCE_DOCUMENT_STORE = public.source_document
```

**Inglês, e a razão é medida.** Os nomes das tabelas desta casa são mistos, mas os **três
donos desta cadeia** são todos ingleses: `raw_asset` · `derived_artifact` · e agora
`source_document`. Um irmão em português no meio de dois ingleses faria o leitor procurar
uma diferença que não existe.

### ⚠️ E há uma tabela com nome de género que **não** é esta

`public.boletim_fitossanitario` já existe (`021:200`). **Não é `SOURCE_DOCUMENT`**, e
medi-o antes de decidir:

```
identidade       UNIQUE (fonte_id, titulo, publicado_em)   ← por TÍTULO, não por versão
guarda           crops_declaradas · crop_declarada · fase_declarada · avversita_citadas
                 · orientacao · citacao_literal            ← SEMÂNTICA EXTRAÍDA
não tem          run_id · raw_asset_id · derived_artifact_id · document_id · version_id
fonte             fonte_externa.id  (bigint, UNIQUE por url_base)
```

Ela é um **RECORD** — o lado semântico que a A4 mandou separar. E o cabeçalho da própria
021 diz que criou «cinco famílias» de facto publicado por terceiro.

> **A casa construiu o lado semântico e nunca construiu o lado documental.** Isso confirma
> a divisão da A4 por evidência, e não por argumento: `boletim_fitossanitario` responde
> «o que o boletim disse»; `source_document` responde «que boletim vimos, em que versão».
> Duas perguntas, duas tabelas — e uma delas já existe.

**Débito registado, não corrigido:** há **duas identidades de fonte** nesta casa —
`SOURCE_ID` texto (`IT-T2-002`), que o coletor, os contratos e `etapa_da_corrida` usam, e
`fonte_externa.id` bigint, chaveado por `url_base`, que a família da 021 usa. Não existe
mapeamento medido entre as duas. É território da COL-LAW-053, já aberto.

---

## 4 · A DECISÃO PRINCIPAL — o texto é APONTADO

```
TEXT_STORAGE_STRATEGY = REFERENCE
```

Medi as seis tabelas que guardam alguma forma de texto, e a lei é **sem excepção**:

| tabela | guarda texto? | que texto |
|---|---|---|
| `conteudo` | **sim** — `titulo`, `descricao` | **nativo**, veio da fonte assim |
| `comentario` | **sim** — `texto` | **nativo** |
| `transcricao` | **sim** — `texto` | **nativo** (15/15 legendas reais são buscadas, não derivadas) |
| `registro_regulatorio` | não | — |
| `catalogo_produto_documento` | **não** — `url`, `sha256`, `raw_asset_id`, `download_state` | aponta |
| `derived_artifact` | **não** — `storage_path unique`, `sha256` | os bytes vivem no armazém |

> ## TEXTO NATIVO COPIA-SE. TEXTO DERIVADO NUNCA SE COPIOU.
> Seis tabelas, zero excepções. **`derived_artifact` não tem coluna de texto**: o texto que
> esta casa produz vive no armazém, endereçado por `storage_path`.

O texto de um boletim em PDF é **derivado** — nasce de `executor_texto_de_pdf`. Copiá-lo
para `source_document` faria três coisas erradas de uma vez:

1. **Criaria segunda autoridade** sobre o mesmo texto. `ONE CONCEPT → ONE OWNER`: o dono do
   texto derivado é o dono do DERIVED, e continua a ser.
2. **Faria a tabela STRUCTURED fingir ser DERIVED** — a mesma família de erro que a
   migration 022 recusou por escrito: *«uma tabela chamada "bruto" com filhos dentro mente
   para todo o leitor futuro»*.
3. **Quebraria a reprodutibilidade da linhagem**: com duas cópias, a pergunta «qual é o
   texto verdadeiro» passa a ter duas respostas, e uma delas envelhece em silêncio.

### Como o consumidor chega ao texto

```
source_document.parent_stage = 'DERIVED'
  → derived_artifact_id → derived_artifact.storage_path → o texto, no armazém
  e derived_artifact.sha256 confere que é o texto que se espera

source_document.parent_stage = 'RAW'
  → raw_observation_id → raw_asset.storage_path → os bytes, que JÁ SÃO o texto
     (uma página HTML, um CSV)
```

Dois saltos, ambos por chave estrangeira, ambos com hash a confirmar. Nenhum deles adivinha.

---

## 5 · A CHAVE FÍSICA

```
PHYSICAL_PRIMARY_KEY  id bigserial primary key
LOGICAL_UNIQUE_KEY    UNIQUE (source_id, document_id, document_version_id)
```

**Surrogate mais chave natural única é a forma que esta casa já usa em 4 de 4 espécies
STRUCTURED:** `conteudo` · `registro_regulatorio` · `catalogo_produto_documento` ·
`derived_artifact`. Não se inventa forma nova.

E a chave natural **foi medida contra dado real**: 35 valores distintos em 144 linhas de
livro, zero sentinelas, zero colisões. **Nenhum hash entra na identidade** — o `sha256` está
lá para encontrar as irmãs, não para nomear a linha.

---

## 6 · A PROVENIÊNCIA — voltar ao RAW e à corrida

```
De SOURCE_DOCUMENT conseguimos voltar deterministicamente até RAW e até a corrida?  YES
```

| ligação | coluna | obrigatória? | o que é |
|---|---|---|---|
| `RAW_LINK` | `raw_observation_id → raw_asset(id)` | **NOT NULL** | **testemunha**: de que observação se leu |
| conteúdo | `content_sha256 char(64)` | **NOT NULL** | é por aqui que se acham **todas** as observações da mesma versão |
| `DERIVED_LINK` | `derived_artifact_id → derived_artifact(id)` | **nulável** | `NULL` quando `parent_stage = 'RAW'` |
| `RUN_LINK` | `run_id → collection_run(run_id)` | **NOT NULL** | a corrida que **estruturou** |

**`raw_observation_id` é testemunha, e está escrito assim de propósito** — é a palavra da
própria migration 022 sobre o campo equivalente dela:

> *«O `raw_asset_id` desta tabela diz apenas DE QUAL CÓPIA SE LEU. É testemunha, e está
> escrito assim na coluna — não se finge que é a identidade do pai.»*

Uma versão de documento tem N observações (medido: até 6). Guardar **uma** delas como se
fosse *a* observação seria mentir sobre a cardinalidade. As irmãs encontram-se com
`where sha256 = content_sha256`.

E `run_id` é a corrida que estruturou — que **pode não ser** a que observou primeiro. São
duas perguntas, e ficam em dois sítios.

---

## 7 · OS CAMPOS

### `REQUIRED_FIELDS`

```
id                    bigserial primary key
source_id             text        not null      -- texto, sem FK (ver §3, débito COL-LAW-053)
document_id           text        not null
document_version_id   text        not null
run_id                text        not null  → collection_run(run_id)
raw_observation_id    bigint      not null  → raw_asset(id)          testemunha
content_sha256        char(64)    not null
parent_stage          text        not null  check in ('RAW','DERIVED')
contract_version      text        not null      -- precedente: rule_version · CORPO_VERSAO
created_at            timestamptz not null default now()
```

### `OPTIONAL_FIELDS`

```
derived_artifact_id   bigint  → derived_artifact(id)
                      NULL quando parent_stage='RAW'; NOT NULL quando 'DERIVED'
                      — e uma trava CHECK amarra os dois, como a 014 já faz com
                        `preservado_exige_bytes_hash_e_asset`

published_at          date    -- a data que o DOCUMENTO declara, não a nossa.
                              medida: SOURCE_DATE_ISO existe em 144/144
                              é PUBLICATION_TIME, e NUNCA se confunde com captured_at
```

### O que ficou **de fora**, e porquê

| campo | veredito |
|---|---|
| `texto` | fora — §4. O texto é apontado |
| `fact_time` · `fact_location` | fora — §8, medido |
| `document_genre` | fora — §9, sem autoridade |
| `language` | fora — não responde «que versão de que documento» |
| `source_location` | fora — é da fonte, e a fonte tem cadastro próprio |
| `observed_time` · `collected_time` | fora — vivem em `raw_asset.captured_at`, já fechado na C-PLAN-0 |

**Nenhum campo entrou por «pode ser útil um dia».**

---

## 8 · `FACT_TIME` E `FACT_LOCATION` — a medição decide

```
FACT_TIME_BEHAVIOR     = C · não os possui nesta etapa
FACT_LOCATION_BEHAVIOR = C · não os possui nesta etapa
```

Medido nas 144 observações, e o resultado é inequívoco:

```
FACT_LOCATION presente em   0 / 144

FACT_TIME — nunca é um valor; é sempre uma frase:
  124  «UNKNOWN — o PDF nao expoe a data do fato medido, so a de geracao»
    6  «por ponto — cada ponto traz sua propria data de campionamento»
    6  «por linha — cada celula tem sua propria data»
    2  «UNKNOWN — o boletim nao data a observacao de campo»
    2  «UNKNOWN — o periodo e de validade, nao de observacao»
    2  «UNKNOWN — o CSV traz datas de registro por linha»
    2  «UNKNOWN»
```

Em 12 casos o próprio livro diz que a data do facto é **por linha ou por ponto** — ou seja,
pertence ao **RECORD**, não ao documento. Nos outros 132, o documento não a expõe.

> **Uma coluna que seria `NULL` em 132 linhas e errada nas outras 12 não é um campo em
> falta: é um campo que pertence a outra tabela.**

E não se deriva de nada: nem do país da fonte, nem do idioma, nem da data de publicação. A
casa já enforça isso em código (`provas/o_encanamento_tem_uma_porta.py` P5:
`fact_time_nao_e_inventado` · `fact_location_nao_e_inventado`).

---

## 9 · GÉNERO DO DOCUMENTO

```
DOCUMENT_GENRE_BEHAVIOR = NÃO SEI — fica fora do primeiro slice, e não o bloqueia
```

A A4 fechou que género não é conceito, e citou `catalogo_produto_documento.tipo` como
precedente de «género vira coluna de lista fechada». Mas medi essa lista antes de a
reutilizar:

```
ADAMA_COMMERCIAL_LABEL · SDS · TECHNICAL_SHEET · REGISTRATION_SHEET · BROCHURE
· CATALOG · GUIDE · TRIAL_DOCUMENT · OTHER_TECHNICAL_DOCUMENT
```

**É a taxonomia do catálogo de um fabricante**, com um valor que traz o nome da própria
ADAMA. Não é autoridade sobre boletins regionais, e forçá-la seria dar a um documento
público a etiqueta de um catálogo comercial.

**Não se inventa taxonomia nesta missão** — e o campo não é essencial: a identidade
`(source, document, version)` não precisa dele para nada. Quando houver autoridade, ele
entra por migration aditiva, com lista fechada, sem tocar em linha nenhuma existente.

---

## 10 · BACKFILL — medido, e nada se fabrica

```
EXISTING_OBSERVATIONS_TOTAL            144   (observações no livro italiano)
VERSÕES DE DOCUMENTO DISTINTAS          35   (as linhas que source_document teria)

identidade completa                    144 / 144
  SOURCE_ID · DOCUMENT_ID · DOCUMENT_VERSION_ID · RUN_ID · RAW_SHA256 · CAPTURED_AT
```

| | contagem | o que é |
|---|---|---|
| `BACKFILL_FULLY_DETERMINISTIC_COUNT` | **7** | têm objecto RAW próprio **e** derivado `TEXT_EXTRACTION` — dá para preencher `raw_observation_id` **e** `derived_artifact_id` sem adivinhar nada |
| `BACKFILL_PARTIAL_COUNT` | **28** | têm objecto RAW próprio e **não** têm derivado — entram com `parent_stage='RAW'` e `derived_artifact_id = NULL`, que é a verdade, não um buraco |
| `BACKFILL_IMPOSSIBLE_COUNT` | **0** | — |

As 109 observações restantes **não geram linha**: são re-observações da mesma versão, e o
grão de `source_document` é a versão. Elas continuam inteiras no lado RAW, cada uma com a
sua corrida — que é exactamente o que a C-PLAN-0 fechou.

⚠️ **Duas honestidades sobre estes números.** Primeiro: eles medem o que o **livro em Git**
consegue provar. O `raw_asset` ao vivo esta sessão não o viu — sem credencial, como em todas
as missões desta série. Segundo: só **7 dos 35** shas têm derivado, porque a derivação
correu sobre o acervo italiano antigo e não sobre as corridas de ops.

**Nenhuma ligação histórica ausente será fabricada.** Onde não há derivado, `parent_stage`
diz `RAW` e a coluna fica `NULL` — e `NULL` aqui significa «não houve derivação», não
«não sei».

---

## 11 · O DESENHO DA MIGRATION FUTURA — sem SQL

```
CREATE TABLE            YES · public.source_document · ADITIVA
PRIMARY KEY             id (bigserial)
UNIQUE KEY              (source_id, document_id, document_version_id)
FOREIGN KEYS            run_id             → collection_run(run_id)   on delete restrict
                        raw_observation_id → raw_asset(id)            on delete restrict
                        derived_artifact_id→ derived_artifact(id)     on delete set null
NOT NULL essenciais     source_id · document_id · document_version_id · run_id
                        raw_observation_id · content_sha256 · parent_stage · contract_version
CHECK                   parent_stage in ('RAW','DERIVED')
                        parent_stage='DERIVED'  ⟺  derived_artifact_id is not null
                        (o par amarrado, como a 014 amarra download_state e raw_asset_id)
CAMPOS OPCIONAIS        derived_artifact_id · published_at
BACKFILL POSSÍVEL       7 completas + 28 parciais = 35 linhas
BACKFILL NÃO POSSÍVEL   nenhuma
```

**Ordem segura:** ① criar a tabela (não toca em nada) → ② ligar o dono novo e escrever
**para a frente** → ③ backfill das 35, opcional e separado, com `on conflict do nothing`
sobre a chave natural.

> **Esta migration NÃO depende da C-PLAN-0.** O rebaixamento do `unique` de `storage_path`
> é preciso para as 109 re-observações terem linha própria em `raw_asset` — e as 35 versões
> só precisam da **primeira** observação de cada uma, que já tem linha. As duas migrations
> são independentes, e é bom que sejam.

---

## 12 · ENTREGA

| | |
|---|---|
| **A** `BRANCH` | `claude/raw-observation-identity-3jbwco` |
| **B** `INITIAL_HEAD` | `e6cb0f91870687be076635643e08fee507008d64` |
| **D** `WORKTREE` | limpa |
| **E** `SOURCE_DOCUMENT_OWNER` | `guarda/preservar_documento.py` |
| **F** `SOURCE_DOCUMENT_STORE` | `public.source_document` |
| **G** `PHYSICAL_PRIMARY_KEY` | `id bigserial` |
| **H** `LOGICAL_UNIQUE_KEY` | `(source_id, document_id, document_version_id)` |
| **I** `REQUIRED_FIELDS` | 10, listados na §7 |
| **J** `OPTIONAL_FIELDS` | `derived_artifact_id` · `published_at` |
| **K** `RAW_LINK` | `raw_observation_id → raw_asset(id)`, **NOT NULL**, testemunha |
| **L** `DERIVED_LINK` | `derived_artifact_id → derived_artifact(id)`, nulável, amarrado a `parent_stage` |
| **M** `RUN_LINK` | `run_id → collection_run(run_id)`, **NOT NULL** |
| **N** `TEXT_STORAGE_STRATEGY` | **REFERENCE** |
| **O** `WHY` | 6 tabelas medidas, zero excepções: texto **nativo** copia-se, texto **derivado** nunca se copiou. Copiar criaria segunda autoridade e faria STRUCTURED fingir ser DERIVED |
| **P** `FACT_TIME_BEHAVIOR` | **C** — não possui. 132/144 dizem `UNKNOWN` com motivo; 12/144 dizem «por linha/por ponto» |
| **Q** `FACT_LOCATION_BEHAVIOR` | **C** — não possui. Presente em **0/144** |
| **R** `DOCUMENT_GENRE_BEHAVIOR` | **NÃO SEI** — sem autoridade; fora do slice e não o bloqueia |
| **S** `EXISTING_OBSERVATIONS_TOTAL` | **144** observações · **35** versões de documento |
| **T** `BACKFILL_FULLY_DETERMINISTIC_COUNT` | **7** |
| **U** `BACKFILL_PARTIAL_COUNT` | **28** |
| **V** `BACKFILL_IMPOSSIBLE_COUNT` | **0** |
| **W** `FUTURE_MIGRATION_REQUIRED` | **YES**, aditiva, independente da C-PLAN-0 |
| **X** `RUNTIME_FILES_CHANGED` | **0** |
| **Y** `DATABASE_MUTATIONS` | **0** |
| **Z** `UNRESOLVED_CRITICAL_A5_1_QUESTIONS` | **0** |

### O que continua `NÃO SEI` — e nenhum bloqueia

1. Lista fechada de `document_genre` — não há autoridade, e o campo não é essencial.
2. Cadastro canónico de `SOURCE_ID`, e o mapeamento para `fonte_externa` — COL-LAW-053,
   aberta antes desta missão.
3. `boletim_fitossanitario` não tem `run_id`, `raw_asset_id` nem `derived_artifact_id` — é
   um RECORD sem proveniência de corrida. Registado, não corrigido.

---

## 13 · VEREDITO

```
SOURCE_DOCUMENT_OWNER    = ONE     guarda/preservar_documento.py
SOURCE_DOCUMENT_STORE    = ONE     public.source_document
SOURCE_DOCUMENT_IDENTITY = CLOSED  surrogate + UNIQUE(source, document, version)
SOURCE_DOCUMENT_LINEAGE  = CLOSED  raw_observation_id · content_sha256 · derived_artifact_id · run_id
TEXT_STORAGE_STRATEGY    = CLOSED  REFERENCE
MINIMUM_SCHEMA_CONTRACT  = CLOSED  10 obrigatórios · 2 opcionais
BACKFILL_MEASURED        = YES     7 completas · 28 parciais · 0 impossíveis

C-PLAN-A5.1 = PASS
```

A implementação futura pode criar `source_document` **sem decidir outra vez** quem é o dono,
onde guarda, qual é a identidade, como liga ao RAW, ao DERIVED e à corrida, e onde está o
texto.

---

## 14 · EM PALAVRAS FÁCEIS

1. **O que é `SOURCE_DOCUMENT`?** Uma versão de um documento de uma fonte. O boletim da
   ARPAV da zona 1, gerado naquele dia — essa coisa, uma vez.

2. **Para que precisamos dessa tabela?** Para responder «que documento vimos, em que
   versão». Hoje ninguém responde: o acervo tem os bytes e o texto, e nada que diga qual
   documento eles são.

3. **O texto fica nela?** Não. Ela **aponta**. O texto derivado já tem dono e já vive no
   armazém; copiá-lo criaria uma segunda versão da verdade que envelhece sozinha.

4. **Como ela sabe de qual coleta veio?** Guarda a corrida que a estruturou e a observação
   RAW de onde se leu, ambas com chave estrangeira.

5. **Como voltamos ao arquivo original?** Dois saltos com hash a conferir: pela observação
   RAW chega-se aos bytes; pelo derivado chega-se ao texto.

6. **As 144 observações antigas entram?** Entram **35 linhas** — porque 144 observações são
   35 versões de documento vistas várias vezes. Sete completas, vinte e oito parciais.

7. **Algum dado antigo será inventado?** Nenhum. Onde não houve derivação, a coluna fica
   vazia e a etapa diz `RAW` — e isso é a verdade, não um buraco.

8. **O que falta depois desta missão?** Os outros bloqueios do primeiro slice: declarar os
   alvos no contrato de fonte, o registo conceito→dono, e as quatro mudanças no T-32.

9. **Já podemos programar a tabela?** Sim. Não sobra decisão nenhuma sobre esta tabela —
   sobra trabalho.

> **HARD STOP.** Dono, casa e contrato fechados. Não se inicia migration. Não se altera o T-32.
