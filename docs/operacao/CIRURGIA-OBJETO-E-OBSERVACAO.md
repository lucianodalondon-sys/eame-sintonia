# A CIRURGIA QUE SEPARA O OBJETO DA OBSERVAÇÃO

**C-PLAN-B5** · o desenho, em `a86e667d`
**C-LIVE-B5** · o censo do banco vivo e a autorização faseada, em `48c9590d`
· ramo `claude/raw-observation-identity-3jbwco`

> Nenhuma migration foi criada em nenhuma das duas. Zero DDL, zero alteração de runtime, de
> teste, do System Map ou da Bíblia. Zero escrita em banco ou em armazém.
>
> **De onde vem cada número.** O desenho saiu do schema versionado, do código versionado e
> de duas medições que já viviam no repositório — tudo reproduzível aqui. O censo da secção
> M saiu de uma leitura autenticada do Supabase LIVE feita **pelo coordenador ChatGPT, fora
> desta sessão**, e está marcado como `EXTERNAL_LIVE_MEASUREMENT`. Esta sessão não tem
> credencial e não o reproduziu.

---

## 0 · O DEFEITO NÃO É UMA OMISSÃO. É UMA CONTRADIÇÃO ASSINADA

A migration 022, escrita por gente desta casa, declara o grão de `raw_asset`:

> *«Em `raw_asset` o grao e a OCORRENCIA, porque duas capturas sao DOIS FACTOS SOBRE O
> MUNDO: a fonte publicou nos dois sitios, e apagar uma perderia a prova de que o documento
> nao mudou entre elas.»*

A migration 001, na mesma tabela, declara outro grão — e declara-o com dentes:

```sql
storage_path   text not null unique
```

Um endereço único por linha é a definição de **objeto de storage**. A prosa diz ocorrência,
a trava diz objeto, e a trava ganha sempre, porque é ela que recusa a escrita.

```
O ALVO DESTA CIRURGIA NÃO É UMA IDEIA NOVA.
É FAZER A TRAVA CONCORDAR COM A FRASE QUE A CASA JÁ ASSINOU.
```

---

## A · O QUE ESTÁ MEDIDO NO SCHEMA VERSIONADO

`CURRENT_RAW_ASSET_COLUMNS` — migration 001, linhas 103-117:

```
id · run_id · storage_path · media_type · bytes · sha256 · captured_at
source_url · preserved · not_preserved_reason · created_at
```

| o quê | valor medido |
|---|---|
| `CURRENT_RAW_ASSET_PK` | `id bigserial` |
| `CURRENT_RAW_ASSET_UNIQUES` | `storage_path` (001) · `(id, sha256)` (022) |
| `CURRENT_RAW_ASSET_FKS` | `run_id → collection_run(run_id) on delete restrict` |
| `CHECK` | `preserved OR not_preserved_reason IS NOT NULL` |

**`ALL_TABLES_REFERENCING_RAW_ASSET_ID`** — nove referências, em cinco migrations:

| migration | referência |
|---|---|
| 003 | `conteudo.raw_asset_id` · e mais uma, `on delete set null` |
| 006 | uma, `on delete set null` |
| 010 | três, `on delete set null` |
| 014 | duas · uma delas `on delete restrict` |
| 022 | `derived_artifact (raw_asset_id, parent_sha256) → raw_asset (id, sha256)` |

**Isto é a razão principal da forma da cirurgia.** Nove chaves apontam para `raw_asset.id`.
Copiar as observações para uma tabela nova e trocar os identificadores obrigaria a reescrever
as nove — e a acertar todas, à mão, num banco que esta sessão não consegue ler.

`ALL_RUNTIME_WRITERS_RAW_ASSET` — dois emissores de SQL, e um ficheiro já emitido:

```
guarda/preservar_coleta.py:416      o dono canónico
guarda/catalogo_importar.py:430     gera .sql para importação; não aplica
supabase/importacoes/ADAMA-ES-CATALOGO-2026-08-30.sql   138 inserts já escritos
provas/derived_artifact_no_postgres.py                  a prova em Postgres
```

⚠️ **Os quatro dependem de `on conflict (storage_path) do nothing`.** O Postgres exige um
índice único que corresponda ao alvo do `on conflict`. Retirar `unique (storage_path)`
não é apenas relaxar uma trava: **torna o SQL destes quatro inválido**. Isso decide a
ordem, e está na secção G.

`ALL_RUNTIME_READERS_RAW_ASSET` — a porta `Memoria` e as suas três implementações:
`objeto_em(storage_path)`, `objetos_da_corrida(run_id)`, `raw_por_id(id)`, mais o
`contar()` das provas.

---

## B · O OBJETO DE STORAGE — nome, grão e identidade

```
STORAGE_OBJECT_TABLE_TARGET = public.storage_object
```

A casa nomeia em português as tabelas de conceito do mundo (`conteudo`, `documento`,
`observacao`, `fonte_externa`, `origem`, `canal`) e em inglês as três da camada de coleta
(`collection_run`, `raw_asset`, `derived_artifact`). O objeto físico é da camada de coleta,
e mora ao lado das irmãs.

```
STORAGE_OBJECT_GRAIN
    uma linha é UMA cópia de bytes gravada UMA vez num endereço do armazém.
    Não é o conteúdo (isso é o sha). Não é a ida à fonte (isso é a observação).
    É a cópia: aquilo que ocupa espaço e que se pode ler de volta.
```

### A identidade não pode ser o sha, e isto está MEDIDO

```
CASO A   mesma publicação · mesmo documento · mesmos bytes · observada amanhã
         →  SAME STORAGE OBJECT

CASO B   publicação diferente · mesmos bytes
         →  STORAGE OBJECTS DIFERENTES
```

As duas respostas são diferentes, e a prova do caso B está em
`data/samples/SUPABASE-LIVE-MEDICAO-EXTERNA.json`, medida no armazém a sério:

```
IT/adama-website/DOCUMENT/227779fdd6be9975-6321-Postscript-80-XL---Scheda-di-Sicurezza.pdf
IT/adama-website/DOCUMENT/227779fdd6be9975-731-Scheda-di-sicurezza---Davai.pdf

    mesmo etag · mesmos 138.284 bytes · DUAS chaves
    139 objetos carregam 138 conteúdos
```

A ADAMA publicou a mesma ficha de segurança como ficha de **dois produtos diferentes**. São
dois factos sobre o mundo, e o writer desta casa já os separa de propósito — o
`caminho_do_objeto()` põe um discriminante de publicação no endereço, e o comentário dele
cita este caso pelo nome.

```
STORAGE_OBJECT_IDENTITY   = o ENDEREÇO da cópia
STORAGE_OBJECT_UNIQUE_KEY = unique (storage_path)
SHA256_UNIQUE_ON_STORAGE_OBJECT = NO
```

`NO` não é cautela: é o resultado da medição. `sha256` continua a ser identidade **dos
bytes**, e fica na tabela como atributo indexado, nunca como chave.

---

## C · CADA CAMPO, E DE QUEM ELE É

Não por estética. Por quem responde à pergunta que o campo faz.

| campo | destino | porquê |
|---|---|---|
| `id` | **OBSERVATION** | é o `RAW_OBSERVATION_ID`, fechado na C-PLAN-0 e devolvido pelo B4 |
| `run_id` | **OBSERVATION** | a corrida é a ida à fonte, não o byte guardado |
| `captured_at` | **OBSERVATION** | o instante em que ESTA máquina recebeu; duas observações do mesmo byte têm horas diferentes |
| `source_url` | **OBSERVATION** | de onde se foi buscar DESTA vez; a mesma cópia pode ser reencontrada noutra URL |
| `preserved` · `not_preserved_reason` | **OBSERVATION** | uma tentativa que não preservou é uma observação sem objeto — e continua a ser uma observação |
| `storage_path` | **STORAGE_OBJECT** | o endereço é da cópia. Fica em `raw_asset` durante a transição, e sai na última fase |
| `media_type` | **STORAGE_OBJECT** | propriedade da cópia gravada |
| `bytes` | **CONTENT_ATTRIBUTE** → no objeto | o tamanho é do conteúdo; vive no objeto porque é lá que se confere a leitura |
| `sha256` | **CONTENT_ATTRIBUTE** → nos DOIS | ver abaixo |
| `created_at` | **OBSERVATION** | quando a linha nasceu |

### `sha256` fica nos dois, e não é duplicação por descuido

A migration 022 criou `unique (id, sha256)` em `raw_asset` **exatamente** para que
`derived_artifact` pudesse exigir, por chave estrangeira composta, que o pai por id e o pai
por sha sejam o mesmo pai. Um red team encontrou a brecha e ela foi reproduzida em Postgres
antes de ser fechada.

```
TIRAR `sha256` DE `raw_asset` APAGA UMA TRAVA QUE JÁ MORDEU.
```

Então `sha256` **permanece na observação** — é o conteúdo que aquela ida à fonte observou —
e **também** vive no objeto, que é o conteúdo que aquela cópia guarda. Os dois têm de
concordar, e a ligação declarativa entre eles fecha isso sem gatilho.

---

## D · A RELAÇÃO, E O CASO QUE ELA NÃO PODE ESTRAGAR

```
RAW_OBSERVATION   N : 1   STORAGE_OBJECT

RAW_ASSET_STORAGE_FK_TARGET = raw_asset.storage_object_id → storage_object(id)
FK_NULLABLE_DURING_TRANSITION = YES
FK_NULLABLE_AT_TARGET         = YES
```

`YES` no alvo, e por uma razão que já está escrita na migration 001:

```sql
CONSTRAINT bruto_ausente_precisa_de_motivo CHECK (preserved OR not_preserved_reason IS NOT NULL)
```

A casa já aceita observação com `preserved = false`. Uma tentativa que não trouxe bytes
**não pode ganhar um objeto de storage falso** só para a coluna ficar cheia. A trava certa
não é `not null`; é condicional:

```
preserved = true   ⇒   storage_object_id IS NOT NULL
preserved = false  ⇒   storage_object_id IS NULL
```

```
OBSERVAÇÃO DE TENTATIVA  ≠  OBSERVAÇÃO PRESERVADA COM BYTES
E FORÇAR A PRIMEIRA A APONTAR PARA ALGO É INVENTAR O QUE NÃO ACONTECEU.
```

---

## E · O FILHO DERIVADO NÃO SE MEXE

```
DERIVED_PARENT_TARGET                        = a RAW OBSERVATION
DERIVED_FK_CAN_REMAIN_VALID_DURING_TRANSITION = YES
DERIVED_SCHEMA_CHANGE_REQUIRED                = NO
```

Não é dedução: está escrito na própria coluna, na 022.

> *«QUAL COPIA FOI LIDA. E uma TESTEMUNHA, nao a identidade do pai: quando o mesmo conteudo
> foi capturado duas vezes, ha duas linhas de `raw_asset` com o mesmo sha256, e esta aponta
> para aquela de que se leu.»*

`raw_asset_id` já significa **de qual observação se leu**. `parent_sha256` continua a
verificar o conteúdo observado, e a chave da derivação continua a ser
`(parent_sha256, kind, producer, …)` — conteúdo por receita, sem tocar em nada.

A chave composta `(raw_asset_id, parent_sha256) → raw_asset (id, sha256)` sobrevive intacta
porque as duas colunas ficam onde estão e `id` não muda. É a segunda razão para a cirurgia
ser em-lugar.

---

## F · O QUE NÃO DÁ PARA PREENCHER SEM INVENTAR

```
SOURCE_ID_BACKFILL_PROVABLE   = PARTIAL
DOCUMENT_KEY_BACKFILL_PROVABLE = NONE
```

**`SOURCE_ID`.** Medi o que o repositório exibe:

| linhas | `SOURCE_ID` recuperável? | prova |
|---|---|---|
| 1 (canário forward) | **SIM** | `SUPABASE-LIVE-MEDICAO-EXTERNA.json` regista `SOURCE_ID: IT-T2-002` ao lado da captura |
| 138 (importação ADAMA-ES) | **NÃO** | o slug do caminho é `adama-website`, uma ORGANIZAÇÃO; e o site `adama.com/spain` **não é fonte nenhuma no atlas das 77** |
| as restantes | **NÃO SEI** | esta sessão não lê o banco |

⚠️ **Um slug no endereço não é a identidade da fonte.** `adama-website` é quem publica;
uma organização publica muitas fontes, e nenhuma das seis fontes espanholas do atlas é o
site corporativo da ADAMA. Extrair `SOURCE_ID` dali seria fabricar uma fonte que a casa
nunca registou.

**`DOCUMENT_KEY`.** A C-PLAN-0 fechou a regra:

```
DOCUMENT_KEY = DOCUMENT_ID     quando a fonte dá identidade semântica
             = CONTENT_SHA256  quando não dá
DOCUMENT_KEY_BASIS = SOURCE_DOCUMENT_ID | CONTENT_DERIVED
```

Para as 138 linhas da ADAMA a fonte **dá** identidade semântica: a URL traz `media/1781`,
e a A5.1a mediu que `media/731` e `media/6321` são duas publicações do mesmo PDF. Logo
`CONTENT_DERIVED` seria tecnicamente verdadeiro e materialmente enganador — diria «derivei
do conteúdo» sobre uma linha cuja fonte tinha nome próprio para dar. E decidir se
`media/<n>` É o `DOCUMENT_ID` exige o contrato daquela fonte, que não existe.

```
UM CAMPO QUE SE PODE CALCULAR NÃO É UM CAMPO QUE SE PODE AFIRMAR.
```

### Como instalar o alvo sem fabricar o passado

Quatro opções foram pesadas; a escolha é a **C**, com a **B** como mecanismo:

| | o que faz | veredito |
|---|---|---|
| A · colunas nullable + writer forward obrigatório | simples | **insuficiente sozinha**: `NULL` não diz se é legado ou esquecimento |
| B · trava parcial | `unique … where source_id is not null and document_key is not null` | **é o mecanismo**, e o Postgres suporta-o nativamente |
| **C · estado explícito de legado** | uma coluna que declara que aquela linha nasceu antes da lei | **escolhida** — é a única que não confunde ausência com descuido |
| D · outra forma já usada | — | a casa já usa `NOT_PRESERVED` e `NAO SEI` como estados declarados; C é a mesma família |

A casa nunca deixa um buraco calado. `NOT_PRESERVED != AUSENTE != NAO SEI != ZERO` é lei
escrita, e o legado ganha o mesmo tratamento: um estado com nome, não um `NULL` mudo.

---

## G · A ORDEM CIRÚRGICA

```
NUNCA PODE EXISTIR UMA JANELA EM QUE `raw_asset` FIQUE SEM TRAVA DE IDENTIDADE.
```

| # | fase | classe |
|---|---|---|
| 1 | criar `public.storage_object` + RLS | `ADDITIVE` |
| 2 | povoar, uma linha por `storage_path` existente | `DATA_BACKFILL` |
| 3 | `raw_asset.storage_object_id` nullable, FK para o objeto | `ADDITIVE` |
| 4 | ligar cada observação ao objeto dela | `DATA_BACKFILL` |
| 5 | check condicional `preserved ⇒ objeto`, `NOT VALID` primeiro | `CONSTRAINT_ADD` |
| 6 | `VALIDATE CONSTRAINT` | `CONSTRAINT_VALIDATE` |
| 7 | `source_id`, `document_key`, `document_key_basis`, estado de legado, `attempts`, `last_attempt_at` — todos nullable | `ADDITIVE` |
| 8 | preencher só o que é FORWARD; legado recebe o estado declarado | `DATA_BACKFILL` |
| 9 | índice único **parcial** da chave de idempotência | `CONSTRAINT_ADD` |
| 10 | **retirar `unique (storage_path)` de `raw_asset`**, deixando índice simples | `DESTRUCTIVE/RELAX` |
| 11 | retirar `storage_path` de `raw_asset` | `DESTRUCTIVE/RELAX` |

**A fase 2 é segura sem censo nenhum**, e isto é demonstrável: `storage_path` é único hoje,
logo a correspondência observação→objeto é total e injetora **por construção**. Não há
duplicado possível para descobrir.

```
FIRST_NON_ADDITIVE_STEP = fase 10 — retirar `unique (storage_path)`
```

```
PROOF_REQUIRED_BEFORE_FIRST_NON_ADDITIVE_STEP

  1. o índice único parcial da fase 9 existe e está válido
  2. TODOS os emissores de `on conflict (storage_path)` contra `raw_asset` já
     apontam para o novo alvo — são quatro, e estão nomeados na secção A.
     Sem isto o SQL deles fica INVÁLIDO, não apenas menos protegido.
  3. a bateria `banco-descartavel` passa contra Postgres 16 com as fases 1-9
     aplicadas, incluindo os dois casos da secção I
```

Da fase 1 à 9 nada se perde e nada se relaxa. **A cirurgia inteira que separa objeto de
observação vive nas fases 1-6, e todas são aditivas.**

---

## H · O QUE A TRANSIÇÃO NÃO ENTREGA SOZINHA

Registo honesto, porque é fácil ler esta cirurgia como mais do que ela é:

**Terminadas as fases 1-6, a segunda corrida do mesmo conteúdo AINDA dá
`METADATA_CONFLICT`.** O conflito nasce de `unique (storage_path)` sobre a observação, e
essa trava só cai na fase 10. A separação é a condição; a cura chega na fase 10.

```
SEPARAR AS ESPÉCIES NÃO É, SOZINHO, DEIXAR AS DUAS OBSERVAÇÕES ENTRAREM.
```

---

## I · OS DOIS CASOS QUE O ALVO TEM DE PRODUZIR

**Reobservação — mesma fonte, mesmo documento, mesmos bytes:**

```
RUN A → S · observação id=10
RUN B → não retransmite byte → reutiliza S → observação id=11

STORAGE_OBJECT_ROWS   = 1
RAW_OBSERVATION_ROWS  = 2
ids                   = 10 e 11, e o 10 continua a ser o 10
sem METADATA_CONFLICT · sem id emprestado
```

**Publicação diferente, bytes idênticos** — o caso ADAMA, medido:

```
CONTENTS          = 1
STORAGE OBJECTS   = 2
RAW OBSERVATIONS  = 2
```

O segundo caso é a trava contra transformar `sha256` em chave universal por acidente. Se
alguém, mais tarde, propuser `unique (sha256)` no objeto, estes números são a recusa.

---

## J · O WRITER, E CONTINUA A SER UM SÓ

```
WRITER_TARGET_SEQUENCE

  1  GARANTIR O OBJETO     endereço já existe? reusa. não existe? envia e regista.
  2  GARANTIR A OBSERVAÇÃO pela chave de idempotência, nunca pelo endereço
  3  LIGAR                 a observação aponta para o objeto
  4  RECONCILIAR OS DOIS   ler de volta as duas espécies, campo a campo

  ONE OWNER = guarda/preservar_coleta.py
```

Nenhum segundo writer nasce. O passo 4 é o que esta casa já faz — `conferir_os_bytes`,
`conferir_o_que_ja_existe`, `conferir_o_que_ficou_escrito` — aplicado a duas tabelas em vez
de uma. **Contar não é conferir** continua a valer nas duas.

---

## K · O B4 SOBREVIVE

```
B4_RETURN_CONTRACT_SURVIVES = YES
```

Os quatro campos ficam como estão: `RAW_OBSERVATION_ID`, `RUN_ID`, `STORAGE_PATH`,
`SHA256`. `sha256` continua na observação (obrigado pela chave composta da 022), e
`storage_path` continua lá até à fase 11.

```
B4_READ_PATH_TARGET

  fases 1-10   sem mudança nenhuma: tudo continua a sair de `objetos_da_corrida()`
  fase 11      `STORAGE_PATH` passa a vir de um join observação → objeto,
               dentro da MESMA leitura por corrida. Continua uma leitura só.
```

```
MEMORY_INTERFACE_TARGET  — registado, não renomeado nesta missão

  objeto_em(storage_path)        → passa a consultar `storage_object`.
                                   Mantê-lo a consultar `raw_asset` por endereço
                                   passaria a MENTIR: a tabela é de observações.
  objetos_da_corrida(run_id)     → fica, e é a leitura que devolve a identidade
  + observacao_por_idempotencia(run_id, source_id, document_key, sha256)
  + objeto_por_endereco(storage_path)
```

---

## L · ROLLBACK

```
ROLLBACK_BEFORE_NON_ADDITIVE

  fases 1-9   reversíveis sem perda: apagar a tabela nova, a coluna nova e as
              travas novas devolve o banco ao estado de hoje.
  fase 10     ponto de não-retorno prático: recriar `unique (storage_path)`
              falha se, entretanto, duas observações partilharem endereço —
              que é justamente o que a fase 10 passa a permitir.
```

E a propriedade que torna tudo isto reversível:

```
RAW_OBSERVATION_ID_PRESERVED_IN_PLACE = YES
```

`raw_asset` **continua a ser a observação**, no lugar, com os mesmos `id`. Nada é copiado
para tabela nova, nada é renumerado. O rollback nunca precisa de reconstruir um único
identificador — e as nove chaves estrangeiras que apontam para `raw_asset.id` nunca ficam
a apontar para o vazio.

Uma solução que copiasse `raw_asset` e trocasse os identificadores está **rejeitada**, e
a razão é medida: os identificadores vivos são esparsos. O canário forward recebeu
`raw_asset_id = 890` num banco com **252 linhas**. Não há mapa de 1..N para reconstruir.

---

## M · O CENSO LIVE — feito, e por quem

```
LIVE_CENSUS_EXECUTED_BY_CLAUDE = NO
LIVE_CENSUS_SOURCE   = leitura autenticada do Supabase LIVE, feita pelo
                       coordenador ChatGPT, fora desta sessão
LIVE_CENSUS_DATE     = 2026-09-10
LIVE_CENSUS_MODE     = READ_ONLY
ESTADO               = EXTERNAL_LIVE_MEASUREMENT
```

⚠️ **Isto não é `OBSERVED_BY_CLAUDE`.** Esta sessão não tem credencial, não correu a
consulta e não a reproduziu. Quem mediu aparece ao lado do que foi medido, e um recado de
terceiro pode estar certo e continuar não sendo prova nossa.

### A CONSULTA DA VERSÃO ANTERIOR NÃO SERVIA

```
ORIGINAL_LIVE_QUERY_SUFFICIENT = NO
CORRECTED_LIVE_QUERY_MEASURED  = YES
```

A instrução que este documento pediu na primeira versão era esta, e fica escrita porque
apagá-la esconderia o erro em vez de o corrigir:

```sql
-- ⚠️ INSUFICIENTE. Ficou registada para se ver o que ela deixava passar.
count(*) filter (where storage_path is null or storage_path = '')  as sem_caminho
count(*) filter (where sha256 !~ '^[0-9a-f]{64}$')                 as sha_fora_de_formato
```

Três buracos, e cada um deixaria passar exactamente o caso que a fase 5 precisa de conhecer:

1. **`= ''` não apanha espaços em branco.** Um caminho com um espaço é tão inútil como um
   caminho vazio, e passaria por «preenchido».
2. **Não separava as duas ausências.** Uma linha `preserved = false` PODE não ter caminho —
   é uma tentativa que não preservou, e é legítima. Uma linha `preserved = true` sem
   caminho é outra coisa: é um objeto que se declara guardado e não diz onde. A trava
   condicional da fase 5 só reprova sobre a segunda, e a consulta antiga somava as duas
   num número só.
3. **`sha256 !~ '…'` sobre `NULL` devolve `NULL`, não `true`.** Um hash ausente não
   entrava em nenhuma das duas contagens: não é «fora de formato» nem é contado à parte.
   **Ficaria invisível.**

```
UMA CONTAGEM QUE SOMA DUAS AUSÊNCIAS DIFERENTES
RESPONDE A UMA PERGUNTA QUE NINGUÉM FEZ.
```

A consulta corrigida separa as três coisas, e foi essa que correu.

### O RESULTADO

| medida | valor |
|---|---:|
| `TOTAL` | **252** |
| `SHA256_NULL` | 0 |
| `SHA256_FORA_DE_FORMATO` | 0 |
| `NAO_PRESERVADOS` | 0 |
| `SEM_CAMINHO_TOTAL` | 0 |
| `PRESERVADOS_SEM_CAMINHO` | 0 |
| `COM_CAMINHO_NAO_VAZIO` | **252** |
| `CAMINHOS_DISTINTOS_NAO_VAZIOS` | **252** |

### AS TRAVAS, LIDAS DE `pg_constraint`

Confirmado no banco vivo, em `raw_asset`:

```
PRIMARY KEY (id)
UNIQUE (storage_path)
UNIQUE (id, sha256)
FOREIGN KEY (run_id) → collection_run(run_id) ON DELETE RESTRICT
CHECK (preserved OR not_preserved_reason IS NOT NULL)
```

e em `derived_artifact`:

```
FOREIGN KEY (raw_asset_id, parent_sha256) → raw_asset(id, sha256) ON DELETE RESTRICT
UNIQUE (storage_path)
UNIQUE NULLS NOT DISTINCT (parent_sha256, kind, producer, producer_version,
                           parameters_hash, serie_posicao)
```

```
LIVE_SCHEMA_RELEVANT_TO_B5 = bate com as suposições versionadas de que o B5 depende
```

E só isso. **Não se afirma que o schema LIVE seja igual ao repositório inteiro** — a
afirmação cobre as estruturas efectivamente lidas acima, e nem uma a mais.

Vale a pena dizer o que isto fecha: a chave composta que a migration 022 criou para impedir
que o pai por id e o pai por sha fossem pais diferentes **está viva no banco**, e não apenas
no ficheiro. É ela que obriga `sha256` a ficar na observação, e agora isso está medido dos
dois lados.

### O QUE ESTE NÚMERO NÃO É

```
VERSIONED   138 inserts de `raw_asset` em supabase/importacoes/ADAMA-ES-CATALOGO-2026-08-30.sql
            1 corrida · 138 sha256 distintos · ZERO casos de mesmos bytes na mesma corrida

LIVE        252 linhas · 2026-09-10 · EXTERNAL_LIVE_MEASUREMENT
```

252 linhas com 252 endereços distintos é a confirmação de que `unique (storage_path)` nunca
foi testada contra um duplicado — **não** é prova de que a casa nunca precisou de dois. O
caso ADAMA da secção B mostra o contrário no armazém, onde não há trava a impedir.

```
UMA TRAVA NUNCA VIOLADA PODE SER UMA TRAVA CERTA
OU UMA PORTA QUE NINGUÉM AINDA TENTOU ABRIR.
```

---

## N · O QUE ESTA CIRURGIA NÃO PRECISA

```
SOURCE_ID_FK_TARGET = NOT_READY
B5_SCHEMA_SPLIT_BLOCKED_BY_COL_LAW_053 = NO
```

Medido: a autoridade de fonte que existe no banco é `public.fonte_externa` — `id bigserial`,
`unique (url_base)`, sem qualquer coluna para o código textual. O código da coleta fala
`IT-T2-002`; o banco fala `1`, `2`, `3`, indexado por URL. **Não existe mapa entre os dois**,
e o site da ADAMA-ES, dono de 138 das linhas, não é fonte nenhuma no atlas das 77.

Mas isso **não bloqueia a separação**, e essa é a descoberta útil desta secção: a divisão
objeto/observação vive nas fases 1-6 e não usa `source_id` para nada. A chave de
idempotência — que precisa de `source_id` — é outra cirurgia, nas fases 7-9.

```
DUAS CIRURGIAS, E SÓ UMA ESTÁ BLOQUEADA.
Separar as espécies pode ir primeiro, sozinha, e sem resolver a COL-LAW-053.
```

---

## O · A AUTORIZAÇÃO, E ELA É FASEADA

```
READY_FOR_B5_PHASES_1_6    = YES
READY_FOR_B5_PHASES_7_9    = NO
READY_FOR_B5_PHASES_10_11  = NO
READY_FOR_FULL_B5_1_11     = NO
```

⚠️ **Um censo verde não é uma autorização em branco.** A leitura da secção M responde às
perguntas de que as seis primeiras fases dependem, e **só a essas**. Transformá-la numa
liberação das onze seria trocar «medi o que precisava» por «medi, logo pode tudo» — que é a
mesma troca que fez um teste contar linhas e chamar-lhe reuso.

### FASES 1-6 · AUTORIZADAS

```
1  criar public.storage_object + RLS
2  povoar, uma linha por storage_path existente
3  raw_asset.storage_object_id nullable + FK
4  ligar cada observação ao objeto dela
5  check condicional preserved ⇒ objeto, NOT VALID primeiro
6  VALIDATE CONSTRAINT
```

Cada risco que estas seis fases corriam tem agora um número ao lado:

| a fase podia rebentar se… | medido | logo |
|---|---:|---|
| houvesse caminho nulo, vazio ou de espaços (fases 2 e 4) | 0 | a correspondência observação→objeto é total |
| dois caminhos coincidissem (fase 2) | 252 de 252 distintos | e é injetora |
| houvesse linha preservada sem endereço (fase 5) | 0 | o check condicional valida |
| houvesse `sha256` nulo ou fora de formato (fases 1 e 2) | 0 e 0 | o objeto nasce com hash íntegro |

**O que esta autorização cobre, e mais nada:** a separação **aditiva** entre `storage_object`
e `raw_asset`. Ela **não** afirma que nova corrida com o mesmo conteúdo já poderá entrar.

```
ACABADAS AS FASES 1-6, A SEGUNDA CORRIDA DO MESMO CONTEÚDO AINDA CONFLITA.
O conflito nasce de `unique (storage_path)` sobre a observação, e essa
trava só cai na fase 10.
```

### FASES 7-9 · NÃO AUTORIZADAS

O censo LIVE não toca nestas perguntas. Ele conta linhas; elas pedem identidade.

```
1  fechar a autoridade canónica de SOURCE_ID para o forward — sem resolver o
   histórico por slug de endereço. `adama-website` é uma ORGANIZAÇÃO, e o site
   não é fonte nenhuma no atlas das 77.

2  fechar como o writer forward RECEBE e PERSISTE `SOURCE_ID`, `DOCUMENT_KEY` e
   `DOCUMENT_KEY_BASIS`. Hoje a porta não os transporta: `DO_COLETOR` tem treze
   campos e nenhum deles é estes três.

3  provar o estado explícito de legado que permite `NULL` histórico sem que a
   ausência silenciosa passe por dado válido.

4  provar a chave de idempotência forward — (RUN_ID, SOURCE_ID, DOCUMENT_KEY,
   CONTENT_SHA256) — sem fabricar backfill histórico.
```

Os quatro são pré-condições, não missões abertas aqui.

### FASES 10-11 · NÃO AUTORIZADAS

São as únicas operações não aditivas de todo o plano, e nenhuma das provas abaixo existe
hoje.

**Antes da fase 10** — retirar `unique (storage_path)` de `raw_asset`:

```
A  a trava parcial de idempotência da fase 9 instalada E válida
B  TODOS os emissores de `on conflict (storage_path)` contra `raw_asset`
   remapeados — são quatro, nomeados na secção A
C  o writer canónico a saber garantir objeto, garantir observação, ligar e
   reconciliar os dois
D  o caso da reobservação a produzir 1 objeto / 2 observações, ids diferentes,
   sem METADATA_CONFLICT
E  o caso das publicações diferentes com bytes iguais a continuar em
   1 conteúdo / 2 objetos / 2 observações
F  a bateria `banco-descartavel` verde com a estrutura nova, ANTES de a trava
   antiga sair
```

O **B** é o que morde primeiro e não é opinião: sem índice único correspondente, o
`on conflict (storage_path)` daqueles quatro não fica menos protegido — fica **inválido**.

**Antes da fase 11** — retirar a coluna `storage_path` de `raw_asset` — todos os leitores
afectados têm de obter `STORAGE_PATH` e `SHA256` pela relação, sem depender da coluna
antiga, preservando o contrato do B4 com `RAW_OBSERVATION_ID = raw_asset.id` inalterado.

```
WRITERS_MIGRATED_AWAY_FROM_RAW_ASSET_STORAGE_PATH_CONFLICT = NO
READERS_READY_FOR_PHASE_11                                 = NO
```

Os dois `NO` são a verdade simples de que **nenhum runtime foi alterado nesta missão**. Os
leitores em causa são `objeto_em(storage_path)`, `objetos_da_corrida(run_id)`,
`raw_por_id(id)`, o `RAW_OBSERVATIONS` do B4 e a procura do pai do derivado.

### O QUE VEM A SEGUIR

```
NEXT_IMPLEMENTATION_SLICE = B5A · implementar SOMENTE as fases 1-6

  PODE   criar `storage_object`, povoá-la, acrescentar e ligar
         `storage_object_id`, instalar e validar o check condicional
  NÃO PODE  fases 7, 8, 9, 10, 11
  NÃO PODE  declarar resolvido NEW_RUN_SAME_CONTENT
```

```
RAW_OBSERVATION_ID_STILL_PRESERVED = YES
```

Em nenhuma das onze fases o `raw_asset.id` se move. É isso que mantém as nove chaves
estrangeiras válidas e o rollback possível sem reconstruir identificador nenhum.

---

## P · O QUE NÃO ENTRA, E CONTINUA A NÃO ENTRAR

```
HISTORICAL_STORAGE_WITHOUT_OPERATIONAL_RUN   continua em aberto

  144 observações do livro italiano       não se tocam
  195 objetos do Storage                  não se tocam
  25 caminhos em `C:/…`                   não se tocam
  nenhuma linha de banco se fabrica para eles, e nenhuma corrida se retrocria
```

O B5 trata o schema existente e o caminho forward. A dívida histórica tem nome próprio e
espera a sua própria missão.

---

## Q · C-PLAN-B5B — PRÉ-CONDIÇÕES DAS FASES 7-9

**C-MAP-B5A + C-PLAN-B5B** · decisão, zero implementação · a partir de `49b1b983`

> Zero migration, zero runtime, zero escrita em banco. As medições abaixo saíram
> do código versionado desta árvore e correm outra vez com o mesmo resultado.

### Q.1 · A CORRIDA

```
RUN_ID_AUTHORITY = orquestrador/orquestrador.py::correr  (T-04)
```

Medido, e já com teste que o segura: `run_id = novo_run_id(p)` corre **antes**
do `subprocess.run` que chama o executor, e o teste
`test_4_o_run_id_e_cunhado_ANTES_de_o_executor_correr` compara os números de
linha na própria árvore sintática — prova de ORDEM, não de resultado.

O executor recebe `--run-id=`, a observação sai com `RUN_ID`, e
`pela_entrada` entrega a corrida ao dono do RAW dentro de `corrida=recibo`.

```
FORWARD_RUN_ID_ALREADY_AVAILABLE_TO_RAW_WRITER = YES
```

**Nunca se cunha um segundo `RUN_ID` no writer**, e nunca se reconstrói a
corrida depois do facto. Proveniência decidida a posteriori não é registada:
é reconstruída.

### Q.2 · A FONTE

```
SOURCE_ID_AUTHORITY = o SOURCE_ID TEXTUAL da Collection   (ex.: IT-T2-002)
SOURCE_ID_DB_SURROGATE_IS_NOT_CANONICAL_SOURCE_ID = fonte_externa.id NÃO é ele
```

`public.fonte_externa` tem `id bigserial` e `unique (url_base)`, e **nenhuma
coluna para o código textual**. O código da coleta fala `IT-T2-002`; o banco
fala `1`, `2`, `3`, indexado por URL. Não existe mapa entre os dois, e o site
que possui 138 das linhas vivas não é fonte nenhuma no atlas das 77.

```
NÃO se cria FK para fonte_externa(id) nesta fase.
NÃO se infere SOURCE_ID de SOURCE_SLUG, storage_path, URL, owner ou publisher.
```

### Q.3 · O BURACO É DE FIO, NÃO DE DEFINIÇÃO

```
SOURCE_ID_EXISTS_UPSTREAM           = YES
SOURCE_ID_REACHES_RAW_WRITER_TODAY  = NO
```

Medido nos dois pontos:

```
coleta/ingresso.py::DO_COLETOR      13 campos, e o primeiro é SOURCE_ID
coleta/ingresso.py::para_o_dono_do_raw()
    devolve 12 chaves — COUNTRY · SOURCE_SLUG · ARTIFACT_KIND · NAME ·
    SOURCE_NATIVE_ID · SHA256 · BYTES · MEDIA_TYPE · CAPTURED_AT ·
    SOURCE_URL · USED_BY · ARTIFACT_ID
    e SOURCE_ID NÃO está entre elas.
```

Ele só sobrevive **derretido** em `SOURCE_SLUG = _slug(f.SOURCE_ID)`, que é
endereço e nunca identidade. `it-t2-002` não se reconverte em `IT-T2-002` sem
adivinhar, e um slug não distingue duas fontes cujos códigos colapsem no mesmo
texto.

```
SOURCE_ID_WIRING_GAP = YES — e é isto que a implementação B5B tem de ligar.
```

**A identidade não é desconhecida; ela é conhecida e não viaja.** São coisas
diferentes, e confundi-las transformaria trabalho de fio em bloqueio de
arquitetura.

### Q.4 · A CHAVE DO DOCUMENTO

Já fechada na C-PLAN-0, e aqui apenas confirmada contra
`docs/operacao/IDENTIDADE-DA-OBSERVACAO-RAW.md`:

```
DOCUMENT_KEY       = DOCUMENT_ID      quando a fonte dá identidade semântica
                   = CONTENT_SHA256   quando não dá — o hash INTEIRO, 64 dígitos
DOCUMENT_KEY_BASIS = SOURCE_DOCUMENT_ID | CONTENT_DERIVED
```

⚠️ **A segunda linha foi RETIRADA na secção S.4.** Bytes iguais não provam
unidade documental igual — a S.1 reproduziu o contraexemplo desta casa. Não há
fallback de conteúdo: `DOCUMENT_KEY` existe só com `DOCUMENT_ID` provado, e a
observação que não o tem vai para `FORWARD_IDENTITY_UNPROVEN` (S.5). O resto
desta secção Q.4 continua de pé.

```
NUNCA são DOCUMENT_ID válido:  UNKNOWN · NAO_SEI · NÃO SEI · "" · null
NUNCA substituem a chave:      DOCUMENT_VERSION_ID · SOURCE_NATIVE_ID ·
                               slug · storage_path · URL · nome do ficheiro
NUNCA se usa prefixo de 16:    o `CONTENT_DERIVED` é o sha256 completo
```

```
DOCUMENT_KEY_INPUT_AVAILABLE = YES
```

Medido: `receber()` chama `para_o_dono_do_raw(f, item)` com o **item original**,
e a observação italiana traz `DOCUMENT_ID` desde o coletor — o adapter leva a
observação inteira e nunca a mutila. O dado está no sítio certo, no instante
certo. O que falta é a tradução escolher levá-lo.

O fallback é **contratual, e não inferência**: quando não há `DOCUMENT_ID`
válido, `DOCUMENT_KEY = sha256` com `BASIS = CONTENT_DERIVED` escrito ao lado.
Substituição declarada não é campo preenchido a fingir.

### Q.5 · LEGADO NÃO É FORWARD

```
LEGACY_IDENTITY_POLICY

  LEGACY_PRE_IDEMPOTENCY   as linhas anteriores ao contrato. Ficam
                           EXPLICITAMENTE fora da proteção forward.
  FORWARD_IDENTIFIED       a observação que chega com SOURCE_ID e DOCUMENT_KEY
                           comprovados.

IDENTITY_NOT_BACKFILLED_BY_GUESS = YES
```

Não se descobre `SOURCE_ID` histórico por `storage_path`. `adama-website` é uma
ORGANIZAÇÃO e não um código de fonte. `media/<n>` não é `DOCUMENT_ID` sem
contrato que o prove, e a A5.1a mediu o mesmo PDF sob dois desses números.

**O terceiro estado não nasce por antecipação.** `FORWARD_IDENTITY_UNPROVEN` só
existirá se aparecer um emissor forward real que precise continuar a escrever
durante as fases 7-9 sem conseguir provar identidade. Hoje há **um** writer
canónico, e ele terá os dois campos assim que o fio da Q.3 for ligado.

```
NULL SILENCIOSO  !=  LEGADO DECLARADO  !=  IDENTIDADE FORWARD COMPROVADA
```

### Q.6 · QUEM O ÍNDICE PARCIAL PROTEGE

```
PARTIAL_INDEX_SCOPE

  semanticamente   UNIQUE (run_id, source_id, document_key, sha256)

  INCLUÍDO   a observação forward com identidade comprovada
  EXCLUÍDO   a linha anterior ao contrato, marcada com o estado explícito
  PORQUÊ     proteger o histórico exigiria inventar-lhe identidade, e um
             índice construído sobre valores fabricados protege uma ficção
  COMO       pela cláusula do índice parcial, que nomeia o estado —
             e NÃO por «onde o campo é nulo»
```

⚠️ **A diferença entre as duas exclusões é a missão inteira desta secção.**
Excluir «onde o campo é nulo» deixaria uma observação forward escapar da
proteção só porque alguém esqueceu de a preencher. Excluir «onde o estado diz
LEGACY» obriga a linha a **declarar-se** legado para sair — e nenhum
esquecimento declara nada.

```
FORWARD_NULL_ESCAPE_PREVENTED_BY_DATABASE = YES     ← corrigido na secção R
```

⚠️ **A redação anterior desta linha dizia `PREVENTED_BY_DESIGN`, e era
insuficiente.** Ela assumia que o writer forward *escreve* o estado. Um writer
que **esquece** a coluna não escreve estado nenhum: a linha entra com
`identity_state = NULL`, o `check` da fase 7 — escrito como «forward exige
identidade» — não a toca, e a cláusula parcial do índice também não. Isso é uma
terceira classe silenciosa, e ela não pode existir.

A trava real está fechada na **secção R**: a coluna termina a fase 8
`NOT NULL` e **sem `DEFAULT`**, de modo que omitir a coluna é ERRO do banco, e
não uma classificação por omissão.

### Q.7 · RETRY NÃO É REOBSERVAÇÃO

```
IDEMPOTENCY_KEY = (RUN_ID, SOURCE_ID, DOCUMENT_KEY, CONTENT_SHA256)

CASO A   RUN A · X · Y · H, tentado outra vez   → mesma chave → REUSED
CASO B   RUN B · X · Y · H                      → chave diferente → NOVA
```

```
CURRENT_WRITER_DISTINGUISHES_RETRY_FROM_REOBSERVATION = NO
```

Medido: hoje o writer reencontra por `storage_path` e compara
`IDENTIDADE_DO_OBJETO = (run_id, sha256, bytes, captured_at, source_url)`. O
endereço é do conteúdo, logo a corrida seguinte cai no mesmo endereço com outro
`run_id` — e sai `METADATA_CONFLICT`.

Mas a pergunta certa não é «isto já está implementado?». É:

```
TEMOS OS DADOS E O CONTRATO PARA IMPLEMENTAR A DISTINÇÃO?   SIM
PHASES_7_9_CAN_DISTINGUISH_THE_KEYS = YES
```

E com todas as letras, porque as duas frases parecem a mesma e não são:

```
PHASES_7_9_CAN_DISTINGUISH_THE_KEYS      = YES
PHASES_7_9_CAN_PERSIST_BOTH_OBSERVATIONS = NO
NEW_RUN_SAME_CONTENT_RESOLVED            = NO
```

`unique (raw_asset.storage_path)` continua de pé depois das fases 7-9. A
segunda observação só coexiste fisicamente depois da **fase 10**, com todas as
pré-condições dela cumpridas.

### Q.8 · A TELEMETRIA QUE NÃO ENTRA NA CHAVE

```
ATTEMPTS_FORWARD_PROVABLE = PARTIAL
```

Medido em `coleta/italy_pilot_collect.mjs`: `baixar()` devolve `tentativas: i`
**também no sucesso**, mas a observação bem-sucedida não o regista — só a de
`TRANSPORT_OR_EMPTY` guarda `retries`. O número existe no instante do sucesso e
é deitado fora ali.

```
attempts · last_attempt_at   NULLABLE, e TELEMETRIA
                             NÃO fazem parte da chave de idempotência
```

**Não se escreve `1` só porque houve sucesso**: pode ter havido retry antes. A
ausência deles não bloqueia o B5B, porque nenhuma lei desta casa exige
telemetria completa para instalar identidade. Fica dívida separada, e não se
fabrica.

### Q.9 · A AUTORIZAÇÃO

```
RUN_ID_SOURCE                 = PROVEN      T-04, antes do executor, com teste de ordem
SOURCE_ID_CANONICAL_AUTHORITY = PROVEN      o código textual da Collection
SOURCE_ID_FORWARD_INPUT       = AVAILABLE   está em DO_COLETOR, não na tradução
DOCUMENT_KEY_RULE             = CLOSED      C-PLAN-0, confirmada aqui
DOCUMENT_KEY_INPUT/FALLBACK   = AVAILABLE   o item original chega à tradução
LEGACY_VS_FORWARD_STATE       = EXPLICIT    dois estados, e o terceiro só se aparecer
PARTIAL_INDEX_SCOPE           = EXPLICIT    exclui por ESTADO, nunca por NULL
FORWARD_NULL_ESCAPE           = BLOCKED BY DATABASE   ← corrigido na secção R
RETRY_VS_NEW_RUN              = DISTINGUISHABLE BY KEY
PHASE_10_STILL_REQUIRED       = YES
```

```
READY_FOR_B5B_IMPLEMENTATION = YES
B5B_BLOCKERS = nenhum bloqueio de arquitetura
```

O único trabalho por fazer é o fio da Q.3: `SOURCE_ID` e `DOCUMENT_KEY` ainda
não chegam nem persistem no dono do RAW. Isso é **implementação do B5B**, e não
razão para dizer que a arquitetura é desconhecida.

```
NEXT_STEP = B5B · implementar SOMENTE as fases 7, 8 e 9
            e continuar a NÃO tocar nas fases 10 e 11
```

---

## R · C-CORR-B5B — A TERCEIRA CLASSE SILENCIOSA NÃO PODE EXISTIR

**C-CORR-B5B** · correção de decisão, zero implementação · a partir de `2ae05493`

> Zero migration, zero runtime, zero escrita em banco. Esta secção corrige a
> Q.6 e a Q.9 e fecha o mecanismo. Não instala nada: nomeia o que a fase 7 e a
> fase 8 do B5B terão de instalar, e porquê.

### R.0 · A LACUNA, DITA SEM ATENUAÇÃO

A Q.6 provou a coisa certa e parou um passo antes do fim. Ela provou que
**excluir por ESTADO é melhor do que excluir por NULL** — e é. Mas depois
sustentou a garantia numa frase sobre o writer:

```
«O writer forward escreve o estado.»
```

Isso é uma **convenção de escrita**, e uma convenção não é uma trava. A linha
que ninguém escreveu é exatamente a linha que o argumento não cobre:

```
identity_state  = NULL
source_id       = NULL
document_key    = NULL

não é FORWARD_IDENTIFIED       → o check «forward exige identidade» não a toca
não é LEGACY_PRE_IDEMPOTENCY   → não declarou nada
não entra no índice parcial    → a cláusula nomeia um estado que ela não tem
```

```
UM CAMPO ESQUECIDO VIRARIA UMA CATEGORIA.
```

E uma categoria que nasce de esquecimento é pior do que o `NULL` que a Q.6
recusou, porque tem a aparência de estar coberta por três travas e não está
coberta por nenhuma.

### R.1 · O MECANISMO — E ELE NÃO É NOVO NESTA CASA

A casa já resolve isto duas vezes, e as duas estão medidas nesta árvore:

| onde | como | o que ensina |
|---|---|---|
| `001` · `raw_asset.preserved` | `boolean not null default true` + `CHECK (preserved OR not_preserved_reason IS NOT NULL)` | ausência de bruto é **estado declarado com motivo**, nunca silêncio |
| `016` · `canal.tipo_de_perfil` | `text not null default 'NOT_KNOWN'` + `check (… in (…))` + `check (tipo_de_perfil = 'NOT_KNOWN' or evidencia is not null)` | um estado declarado exige evidência; o estado que não exige nada é o padrão |
| `018` · `geografia.especie` | `text not null default 'ADMIN'` + `check (… in (…))` | vocabulário fechado num `check`, e `ADD COLUMN NOT NULL DEFAULT` corre sobre tabela povoada |

O `016` é o precedente mais próximo — e é também onde a diferença tem de ser
dita, porque **copiá-lo inteiro reabriria a lacuna**:

```
NO 016   omitir a coluna → cai no DEFAULT 'NOT_KNOWN'  → classificação por omissão
AQUI     omitir a coluna → tem de ser ERRO             → nenhuma classificação
```

```
O DEFAULT É A PORTA DE FUGA.
```

Um `default 'LEGACY_PRE_IDEMPOTENCY'` fecharia o `NULL` e abriria pior: todo
writer forward que esquecesse a coluna passaria a escrever **legado declarado**
sem o declarar, e o índice parcial excluí-lo-ia com a consciência limpa. Trocar
um escape silencioso por outro não é fechar nada.

```
IDENTITY_STATE_HAS_DEFAULT = NO
```

`NOT NULL` **sem** `DEFAULT` é o que transforma o esquecimento em recusa:

```
insert into raw_asset (run_id, storage_path, …)      -- sem identity_state
ERROR:  null value in column "identity_state" violates not-null constraint
```

Não é aviso, não é `NULL`, não é uma terceira classe. É a escrita a não
acontecer.

### R.2 · A ORDEM, PORQUE ELA É A METADE DA GARANTIA

`ADD COLUMN … NOT NULL` sem `DEFAULT` não corre sobre tabela povoada — as 252
linhas vivas não têm valor para a coluna nova. Logo a coluna **nasce nullable**,
e a janela em que ela o é tem de fechar **antes** do índice da fase 9:

```
FASE 7   add column identity_state text            -- NULLABLE, e só aqui
         add column source_id text
         add column document_key text
         add column document_key_basis text
         check de vocabulário e check de forward-exige-identidade
             instalados NOT VALID

FASE 8   update … set identity_state = 'LEGACY_PRE_IDEMPOTENCY'
             where identity_state is null            -- todas as linhas de hoje
         alter column identity_state set not null    ← ACTO DE FECHO DA FASE 8
         (e NUNCA um set default)
         validate constraint …

FASE 9   create unique index … where identity_state = 'FORWARD_IDENTIFIED'
```

```
IDENTITY_STATE_TRANSITION_NULLABLE   = YES   -- apenas dentro da fase 7
IDENTITY_STATE_TARGET_NULLABLE       = NO
NULL_STATE_ROWS_ALLOWED_AT_PHASE_9   = NO
```

⚠️ **A fase 9 não pode começar com uma linha em `NULL`.** O índice parcial é o
que dá sentido ao estado; instalá-lo enquanto o estado ainda é opcional é
instalar a proteção e deixar a porta aberta ao lado dela. O `set not null` é
pré-condição da fase 9, e não um acabamento posterior.

### R.3 · OS SEIS CASOS, DECIDIDOS EXECUTAVELMENTE

Cada caso abaixo é uma escrita concreta e um veredito do **banco**, não do
writer.

| | escrita | veredito | quem recusa |
|---|---|---|---|
| **A** | `identity_state = NULL` | **REJECT** | `NOT NULL` da coluna (fecho da fase 8) |
| **B** | `FORWARD_IDENTIFIED` · `source_id = NULL` | **REJECT** | `forward_exige_identidade` |
| **C** | `FORWARD_IDENTIFIED` · `document_key = NULL` | **REJECT** | `forward_exige_identidade` |
| **D** | `FORWARD_IDENTIFIED` · `document_key_basis = NULL` | **REJECT** | `forward_exige_identidade` |
| **E** | `LEGACY_PRE_IDEMPOTENCY` · os três `NULL` | **ALLOW** | ninguém — e é isso que se quer |
| **F** | writer **omite** a coluna | **REJECT** | `NOT NULL` **e a ausência de `DEFAULT`** |

O predicado, escrito uma vez e a morder só o forward:

```sql
constraint estado_de_identidade_tem_vocabulario
  check (identity_state in ('LEGACY_PRE_IDEMPOTENCY','FORWARD_IDENTIFIED'))

constraint forward_exige_identidade
  check (identity_state <> 'FORWARD_IDENTIFIED'
         or (source_id          is not null and btrim(source_id)          <> ''
         and document_key       is not null and btrim(document_key)       <> ''
         and document_key_basis is not null))
```

```
O CASO E É O QUE PROVA QUE O PREDICADO ESTÁ CERTO.
```

Um `check` que exigisse identidade de **todas** as linhas reprovaria as 252 e a
fase 8 não passaria — e a saída fácil seria fabricar-lhes `SOURCE_ID`, que a
Q.5 proíbe. O predicado morde por estado, e o legado sai por declaração.

`btrim(x) <> ''` não é adorno: é o mesmo mecanismo que a `025` já usa em
`objeto_tem_endereco`. Espaço em branco não é identidade.

### R.4 · O VOCABULÁRIO DE SENTINELA — MEDIDO, NÃO INVENTADO

A pergunta «que valores não podem passar por identidade real?» não se responde
com uma lista de imaginação. Contei o que esta árvore usa:

```
supabase/migrations/*.sql     'NAO_SEI' 33 · 'NOT_KNOWN' 31 · 'UNKNOWN' 3 · 'NAO_SE_APLICA' 1
leis/ coleta/ guarda/         "UNKNOWN" 12 · "NAO SEI" 6 · "NOT_KNOWN" 5 · "NAO_SE_APLICA" 5 · "NAO_SEI" 4
leis/artefato.py              NAO_SEI = "NAO SEI"   ·   NAO_SE_APLICA = "NAO_SE_APLICA"
                              DERIVATION_UNKNOWN = "UNKNOWN"
```

São **seis** literais em circulação, e a Q.4 já proibia cinco deles como
`DOCUMENT_ID`. A diferença é que a Q.4 os proibia numa regra escrita e a fase 7
tem de os proibir num `check`:

```sql
constraint identidade_forward_nao_aceita_sentinela
  check (identity_state <> 'FORWARD_IDENTIFIED'
         or (upper(btrim(source_id))    not in
                ('NAO SEI','NAO_SEI','NÃO SEI','NAO_SE_APLICA','UNKNOWN','NOT_KNOWN')
         and upper(btrim(document_key)) not in
                ('NAO SEI','NAO_SEI','NÃO SEI','NAO_SE_APLICA','UNKNOWN','NOT_KNOWN')))
```

```
UNKNOWN_IDENTITY_CAN_ENTER_PARTIAL_UNIQUE_AS_REAL_ID = NO
```

⚠️ **Uma confissão preenchida é pior do que um campo vazio quando existe um
índice em cima.** `UNIQUE (run_id, source_id, document_key, sha256)` com
`source_id = 'NAO SEI'` não protege coisa nenhuma: junta observações de fontes
diferentes debaixo de uma palavra que quer dizer «não sei qual». O índice
passaria a colidir por ignorância partilhada.

`NAO_SE_APLICA` entra na lista pela mesma razão e por outra: identidade de fonte
**aplica-se sempre** a uma observação forward. Dizer que não se aplica é uma
afirmação falsa, não uma confissão.

### R.5 · `CONTENT_DERIVED` ⇒ A CHAVE É O SHA INTEIRO — E ISSO É `CHECK`, NÃO CONVENÇÃO

⚠️ **CORRIGIDA PELA S.4:** `CONTENT_DERIVED` foi retirado do vocabulário. O
raciocínio abaixo — «isto é verificável pelo banco, não pelo writer» — continua
certo; o predicado final é o da S.4, mais curto.

A Q.4 fechou a regra e deixou-a do lado do writer. Ela não precisa de lá ficar:
os dois campos vivem **na mesma linha**, logo o predicado é verificável pelo
banco sem função, sem subconsulta e sem gatilho.

```sql
constraint chave_derivada_do_conteudo_e_o_sha_inteiro
  check (document_key_basis <> 'CONTENT_DERIVED' or document_key = sha256)

constraint base_da_chave_tem_vocabulario
  check (document_key_basis is null
         or document_key_basis in ('SOURCE_DOCUMENT_ID','CONTENT_DERIVED'))
```

```
CONTENT_DERIVED_KEY_EQUALS_FULL_SHA256 = DB_ENFORCED
```

Decisão: **constraint, não writer.** O writer continua a escrever a regra; o
banco deixa de acreditar nele. Isto fecha por construção o prefixo de 16 que a
Q.4 proibia por escrito — `substr(sha256,1,16) <> sha256`, e o `check` reprova.

### R.6 · OS DOIS RISCOS DO LEGADO EXPLÍCITO — E ELES NÃO SÃO O MESMO RISCO

Excluir por estado obriga a linha a declarar-se legado. Falta perguntar quem
consegue fazer essa declaração.

**RISCO A · declaração por esquecimento.** O writer não escreve a coluna e a
linha acaba legado sem ninguém o ter decidido.

```
LEGACY_BY_OMISSION_RISK = CLOSED_BY_DATABASE
```

Fechado pela R.1: sem `DEFAULT` não há classificação por omissão. Não é
convenção, não é revisão de código, não é teste. É a escrita a falhar.

> ### ⛔ REVOGADO PELA SECÇÃO T — o corte por `created_at` não funciona
>
> O mecanismo descrito no RISCO B abaixo foi **reproduzido em PostgreSQL 16.13
> descartável e falhou**. `now()` é `transaction_timestamp()`: uma transação
> aberta ANTES do corte carrega a hora de abertura para dentro de um `INSERT`
> feito DEPOIS dele, e a linha futura declara-se legado com a trava a aplaudir.
> Fica aqui como histórico do raciocínio. **A trava válida é a da secção T** —
> corte pelo surrogate `raw_asset.id`, com lock. Nenhuma instrução deste bloco
> deve ser implementada.

**RISCO B · declaração explícita e falsa.** Um runtime novo escreve
`identity_state = 'LEGACY_PRE_IDEMPOTENCY'` numa observação de hoje, e sai da
proteção pela porta da frente.

Este é o risco que a Q.6 não viu, e ele **também** tem trava de banco, porque
`LEGACY_PRE_IDEMPOTENCY` tem uma definição temporal: *linha anterior à lei*. A
`raw_asset` já carrega o relógio para o provar — `created_at timestamptz not
null default now()`, medido na `001`. O corte congela-se no instante da fase 8:

```sql
do $$
declare corte timestamptz := now();
begin
  execute format(
    'alter table public.raw_asset add constraint legado_e_anterior_a_lei '
    'check (identity_state <> %L or created_at < %L) not valid',
    'LEGACY_PRE_IDEMPOTENCY', corte);
end $$;
```

```
LEGACY_BY_EXPLICIT_DECLARATION_RISK = DB_ENFORCED
```

Todas as linhas de hoje têm `created_at` anterior ao corte e passam a
validação; nenhuma linha futura o consegue ter. O estado de legado deixa de ser
uma etiqueta escolhível e passa a ser um **facto sobre quando a linha nasceu**.

⚠️ **O limite desta trava, dito antes que alguém o descubra:** ela é forjável
por um writer que **também** falsifique `created_at`, porque a coluna tem
`DEFAULT` e não proibição de escrita explícita. Mas isso deixa de ser
esquecimento e passa a ser proveniência falsificada — outra lei, mais alta, e
já escrita. Registo o limite; não o escondo atrás da palavra `DB_ENFORCED`.

```
NENHUMA DESTAS TRÊS FRASES É A MESMA:
  o writer costuma escrever certo        →  CONVENÇÃO
  o writer é obrigado por código a isso  →  CODE_ENFORCED
  a escrita errada não entra             →  DB_ENFORCED
```

### R.7 · O TERCEIRO ESTADO CONTINUA A NÃO NASCER

Nada aqui cria `FORWARD_IDENTITY_UNPROVEN`. A Q.5 fica de pé sem uma emenda:

```
IDENTITY_STATE_VOCABULARY = LEGACY_PRE_IDEMPOTENCY | FORWARD_IDENTIFIED
THIRD_STATE_CREATED       = NO      ← passou a YES na S.5
```

⚠️ **A S.5 fez nascer `FORWARD_IDENTITY_UNPROVEN`, e dentro da condição que
esta secção escreveu.** Não foi antecipação: apareceu um contraexemplo medido
(S.1) e a `COL-LAW-006` obriga o emissor a existir. A frase abaixo continua a
ser o teste certo; o que mudou foi ele ter passado a ser satisfeito.

E a razão é agora mais forte do que era na Q.5. Lá o terceiro estado não nascia
por não haver emissor que o pedisse. Aqui ele não nasce porque **o buraco que o
justificaria foi tapado**: a linha sem estado não existe, e a linha forward sem
identidade não entra. Um terceiro estado só voltaria à mesa com um emissor
forward real, medido, que precise de escrever durante as fases 7-9 sem
conseguir provar identidade — e aí seria uma decisão com contraexemplo à
frente, não uma antecipação.

### R.8 · O QUE O BANCO NÃO FECHA, E QUEM FECHA

Honestidade de camadas, porque chamar tudo `DB_ENFORCED` seria o mesmo erro da
Q.6 com outro nome:

```
DB_ENFORCED     estado não-nulo · sem default · vocabulário · forward exige
                identidade · sentinela recusada · CONTENT_DERIVED = sha inteiro
                · legado é anterior ao corte

CODE_ENFORCED   ligar SOURCE_ID e DOCUMENT_KEY até ao dono do RAW — o fio da
                Q.3. O banco recusa a linha errada; ele não sabe transportar
                o campo certo.

TEST_ENFORCED   que os seis casos continuem a ser recusados/aceites depois de
                cada alteração do writer.
```

> ### ⛔ SUPERSEDED PELA SECÇÃO T.7 — esta lista tem dois casos revogados
>
> Os casos **9 e 10** mandam aceitar `CONTENT_DERIVED`, e a S.4 revogou esse
> valor. O caso **11** apoia-se no corte por `created_at`, que a T.2 reprovou.
> **A lista executável final é a da T.7.** Esta fica como histórico e NÃO se
> implementa.

```
TEST_ENFORCED_INVARIANTS   ⛔ SUPERSEDED — ver T.7

  1. insert sem identity_state              → REJEITADO  (caso F)
  2. insert com identity_state = NULL       → REJEITADO  (caso A)
  3. FORWARD sem source_id                  → REJEITADO  (caso B)
  4. FORWARD sem document_key               → REJEITADO  (caso C)
  5. FORWARD sem document_key_basis         → REJEITADO  (caso D)
  6. FORWARD com source_id = 'NAO SEI'      → REJEITADO  (R.4)
  7. FORWARD com source_id = '   '          → REJEITADO  (R.3)
  8. LEGACY com os três campos nulos        → ACEITE     (caso E)
  9. CONTENT_DERIVED com key = sha16        → REJEITADO  ⛔ ver T.7
 10. CONTENT_DERIVED com key = sha256       → ACEITE     ⛔ REVOGADO pela T.7,
                                                            que manda REJEITAR
 11. LEGACY escrito numa linha de agora     → REJEITADO  ⛔ mecanismo revogado;
                                                            veredito mantido, ver T.7
 12. após a fase 8, zero linhas com estado nulo — contagem, não amostra
```

Estes doze são casos da bateria `banco-descartavel` contra **Postgres 16**, e
não de SQLite: `NOT VALID`/`VALIDATE`, `btrim` e o `do $$` do corte só existem
lá. Escrevem-se no B5B, junto com a migration que instalam. **Nesta missão não
se escreve nenhum deles.**

### R.9 · O FECHO

```
IDENTITY_STATE_TRANSITION_NULLABLE                    = YES  (só na fase 7)
IDENTITY_STATE_TARGET_NULLABLE                        = NO
IDENTITY_STATE_HAS_DEFAULT                            = NO
IDENTITY_STATE_VOCABULARY                             = ver S.5 — três estados
THIRD_STATE_CREATED                                   = YES na S.5
FORWARD_NULL_ESCAPE_PREVENTED_BY_DATABASE             = YES
NULL_STATE_ROWS_ALLOWED_AT_PHASE_9                    = NO
UNKNOWN_IDENTITY_CAN_ENTER_PARTIAL_UNIQUE_AS_REAL_ID  = NO
CONTENT_DERIVED_KEY_EQUALS_FULL_SHA256                = RETIRADO na S.4
LEGACY_BY_OMISSION_RISK                               = CLOSED_BY_DATABASE
LEGACY_BY_EXPLICIT_DECLARATION_RISK                   = DB_ENFORCED, mas pelo
                                                        SURROGATE (T), nunca pelo relógio
IDENTITY_INVARIANTS_ENFORCEMENT_CLASS                 = DB_ENFORCED + CODE_ENFORCED + TEST_ENFORCED
TEST_ENFORCED_INVARIANTS                              = lista final na T.7
```

```
A TERCEIRA CLASSE SILENCIOSA ESTÁ ELIMINADA DO ESTADO ALVO.
```

O índice parcial da fase 9 continua a excluir por **estado**, e agora toda linha
tem um. `PHASE_10_STILL_REQUIRED = YES`, e nada nesta secção o antecipa.

---

## S · C-RECON-B5B — A CONTRAPROVA EXTERNA, RECONCILIADA CONTRA O HEAD

**C-RECON-B5B** · reconciliação, zero implementação · a partir de `e375ee5d`

> Uma contraprova externa read-only comparou o B5 com OpenLineage, Temporal,
> Airbyte e PostgreSQL e devolveu `PASS_WITH_REQUIRED_FIXES` com quatro
> candidatos. **Nenhuma das quatro soluções propostas foi aceite por vir de
> fora.** Cada uma foi reproduzida contra esta árvore, e três mudaram de forma
> ao passar pela medição.

### S.1 · B-1 · A CHAVE COLAPSA — E COLAPSA MESMO

Cenário do benchmark: mesma `RUN`, mesmo `SOURCE_ID`, duas publicações
diferentes, os mesmos bytes, sem `DOCUMENT_ID` comprovado.

Regra da Q.4, aplicada literalmente:

```
publicação P1   sem DOCUMENT_ID  →  DOCUMENT_KEY = H   (BASIS = CONTENT_DERIVED)
publicação P2   sem DOCUMENT_ID  →  DOCUMENT_KEY = H   (BASIS = CONTENT_DERIVED)

(RUN, SOURCE, H, H)  ==  (RUN, SOURCE, H, H)
```

```
SAME_BYTES_DISTINCT_PUBLICATIONS_COLLAPSE = YES
```

E não é hipótese. O contraexemplo está medido nesta casa desde a secção B:

```
IT/adama-website/DOCUMENT/227779fdd6be9975-6321-Postscript-80-XL---Scheda-di-Sicurezza.pdf
IT/adama-website/DOCUMENT/227779fdd6be9975-731-Scheda-di-sicurezza---Davai.pdf
    mesmo etag · mesmos 138.284 bytes · DUAS publicações
```

⚠️ **O endereço já sabia separá-las e a chave proposta não sabia.** O
`caminho_do_objeto()` carrega um DISCRIMINANTE exatamente para isto — está
escrito na docstring dele. A chave `(RUN, SOURCE, DOCUMENT_KEY, SHA)` com
`DOCUMENT_KEY = sha` não carrega nada equivalente.

**O defeito não é a chave ter poucos campos. É o fallback afirmar identidade
documental a partir de bytes, que não a provam.**

### S.2 · `SOURCE_NATIVE_ID` NÃO É A SAÍDA — MEDIDO CAMPO A CAMPO

A contraprova sugeriu a cadeia `DOCUMENT_ID → SOURCE_NATIVE_ID → SHA256`.
Recusada, e com prova de linha:

```python
coleta/ingresso.py:215
nativo = (item.get("SOURCE_NATIVE_ID") or item.get("ID")
          or item.get("id") or f.SHA256[:16])
...
"SOURCE_NATIVE_ID": _slug(nativo),
```

| | pergunta | resposta | prova |
|---|---|---|---|
| A | tem definição canónica única? | **NÃO na produção** | `COL-LAW-206` define-o como «o id que a própria fonte dá»; o runtime aceita três chaves diferentes e um fallback |
| B | é sempre fornecido pela fonte? | **NÃO** | o fallback existe precisamente porque não é; `CONFORMIDADE-ITALIA.md` regista «`SOURCE_NATIVE_ID` não é campo» |
| C | é estável entre retries? | **NÃO garantido** | quando cai no fallback é `SHA256[:16]`; muda com os bytes, não com a publicação |
| D | é escopado à publicação/documento? | **NÃO** | `item.get("ID")`/`item.get("id")` é a chave que a observação por acaso trouxer |
| E | pode ser id de produto, relação, linha ou post? | **SIM** | nada no código restringe a espécie; `_slug()` aceita qualquer texto |
| F | algum caminho o fabrica a partir do SHA? | **SIM** | `f.SHA256[:16]`, e depois `_slug()` por cima |

```
GENERIC_SOURCE_NATIVE_ID_IS_SAFE_DOCUMENT_KEY = NO
```

⚠️ **Promovê-lo a chave fecharia B-1 escrevendo o defeito com outra letra.** No
pior caso o «id nativo» É o sha16 — e aí a chave de idempotência passaria a
conter o hash duas vezes, uma delas disfarçada de identidade da fonte. Um
prefixo de 16 dígitos com nome de identidade é pior do que o sha inteiro
assumido: mente sobre a origem além de não distinguir.

E há o corte de qualidade: `_slug()` é declaradamente **endereço, nunca
identidade** — a docstring dele diz isso, e a Q.3 já o tinha usado para recusar
`SOURCE_SLUG` como fonte.

### S.3 · O CONCEITO CANÓNICO JÁ TEM DONO — NÃO SE CRIA SINÓNIMO

A pergunta certa era «que identidade comprovada distingue duas UNIDADES
PUBLICADAS da mesma fonte?». A resposta já existe nesta árvore, e não é um
campo: é um **contrato por fonte**.

```
regras/italy_contracts.mjs
    IDENTITY_KEYS      quais campos nativos identificam a unidade publicada
    DOCUMENT_ID_RULE   como se monta o DOCUMENT_ID a partir deles
    FAIL_CLOSED_RULE   o que fazer quando eles não aparecem
```

Medido em **todas** as fontes do piloto. Dois exemplos que respondem
diretamente à sugestão do benchmark:

```
FEM      DOCUMENT_ID_RULE = "FEM:HANDLE:{10449/NNNNN}"
         ← um id NATIVO promovido a identidade documental PELO CONTRATO

ADAMA    DOCUMENT_ID_RULE = "ADAMA:{CANONICAL_URL}:{PUBLISHED_TIME}"
         FAIL_CLOSED_RULE = "extrato sem canonical_url ou sem published_time
                             nao tem identidade — FAILED"
         ← e é este contrato que separa media/731 de media/6321
```

```
CANONICAL_NATIVE_PUBLICATION_ID_CONCEPT = DOCUMENT_ID, via IDENTITY_KEYS +
                                          DOCUMENT_ID_RULE do contrato da fonte
NEW_BASIS_NAME_REQUIRED = NO
```

**`SOURCE_NATIVE_PUBLICATION_ID` não nasce.** Seria um sinónimo de uma coisa
com dono. Um id nativo pode participar da identidade documental — mas apenas
atravessando o contrato, e aí ele já é `DOCUMENT_ID` com
`BASIS = SOURCE_DOCUMENT_ID`. Nunca por promoção automática no encanamento.

### S.4 · O FALLBACK DE HASH — E ELE NÃO SOBREVIVE

Pergunta do §6, respondida sem rodeio:

> Quando só conhecemos os bytes, podemos afirmar que duas ocorrências de bytes
> iguais são a mesma UNIDADE documental?

```
NO — e o contraexemplo é da própria casa: 227779fdd6be9975, duas publicações.
```

Logo `CONTENT_DERIVED` não pode carregar o selo `FORWARD_IDENTIFIED`. E a
consequência é maior do que parece: **se o hash nunca prova identidade
documental, o hash nunca é uma `DOCUMENT_KEY`.** Um campo que só se preenche
quando não se sabe a resposta não é uma chave; é uma confissão com nome de
chave.

```
DOCUMENT_KEY_FINAL_RULE

  DOCUMENT_KEY  existe SOMENTE quando o contrato da fonte prova identidade
                documental — DOCUMENT_ID, e nada mais.
  NÃO EXISTE    fallback de conteúdo. O sha256 continua na linha, continua na
                chave de idempotência e continua a ser a identidade dos BYTES.
                Ele não muda de espécie por ser copiado para outra coluna.

DOCUMENT_KEY_BASIS_FINAL_ENUM = SOURCE_DOCUMENT_ID
```

```
CONTENT_DERIVED = RETIRADO
```

⚠️ **Isto corrige a R.5 desta mesma sessão.** A R.5 tinha decidido um `check`
para garantir que `CONTENT_DERIVED ⇒ document_key = sha256` — um `check` correto
sobre uma regra que não devia existir. O predicado certo é mais curto:

```sql
constraint base_da_chave_tem_vocabulario
  check (document_key_basis is null or document_key_basis = 'SOURCE_DOCUMENT_ID')
```

A Q.4 fica corrigida no mesmo movimento: a linha «`= CONTENT_SHA256` quando não
dá» deixa de valer para a `DOCUMENT_KEY`.

### S.5 · O DESTINO DE UM FORWARD SEM IDENTIDADE — E AQUI O TERCEIRO ESTADO NASCE

Retirado o fallback, sobra a pergunta que a R.7 tinha deixado adormecida: o que
acontece a uma coleta forward cujos bytes chegaram e cuja identidade documental
não se prova?

As três opções do §6, pesadas:

| | o que faz | veredito |
|---|---|---|
| A · recusar até haver identidade | a linha não entra | **insuficiente** — e a razão é uma LEI, não uma preferência |
| **B · estado explícito `FORWARD_IDENTITY_UNPROVEN`** | os bytes ficam, a chave não se inventa | **escolhida** |
| C · solução existente | — | não existe: hoje o coletor resolve isto deitando os bytes fora |

**A lei que decide.** `COL-LAW-006 · RAW PRIMEIRO`:

```
CAPTUROU → PRESERVA O ORIGINAL → DEPOIS DERIVA

«O RAW DEVE ser gravado antes de qualquer normalização, extração,
 transcrição ou CLASSIFICAÇÃO.»
```

Resolver identidade **é** classificação. Recusar a linha por falta de
identidade é subordinar a preservação do original a um passo que a lei manda
correr depois dele. A opção A não é «mais rigorosa»: é a ordem invertida.

```
FORWARD_WITHOUT_PROVABLE_DOCUMENT_ID_POLICY = PRESERVE_AND_DECLARE_UNPROVEN
THIRD_STATE_REQUIRED = YES
```

E ele nasce dentro da condição que a Q.5 tinha escrito — não por antecipação.
Há agora um contraexemplo medido (S.1) **e** uma lei que obriga o emissor a
existir. O que faltava era isso.

```
IDENTITY_STATE_VOCABULARY  (final)

  LEGACY_PRE_IDEMPOTENCY     anterior ao contrato · sem identidade inventada
  FORWARD_IDENTIFIED         source_id + document_key + basis, os três válidos
  FORWARD_IDENTITY_UNPROVEN  source_id válido · document_key NULL · basis NULL
                             bytes preservados · FORA do índice parcial
```

⚠️ **`document_key` fica NULL, e nunca o sha.** É a diferença entre «não provei
qual documento é» e «declarei que o documento é o seu próprio conteúdo». A
primeira é verdadeira; a segunda é a S.1 outra vez.

`source_id` continua obrigatório nos dois estados forward: a Collection sempre
soube a que fonte pediu. O que pode faltar é a identidade do documento, nunca a
da fonte.

> ### ⛔ SUPERSEDED PELA T.1 — estes dois `check` deixam entrar `'NAO SEI'`
>
> Ambos exigem `source_id` não-nulo e não-branco, e mais nada. Uma observação
> `FORWARD_IDENTITY_UNPROVEN` com `source_id = 'NAO SEI'` passa nos dois — e
> «não sei qual documento é» não é «não sei que fonte pedi». A T.1 substitui-os
> por um par onde a exigência de FONTE REAL é uma trava só, comum aos dois
> estados forward. **Implementar a T.1, não este bloco.**

```sql
-- ⛔ SUPERSEDED — ver T.1
constraint forward_identificado_exige_identidade
  check (identity_state <> 'FORWARD_IDENTIFIED'
         or (source_id is not null and btrim(source_id) <> ''
         and document_key is not null and btrim(document_key) <> ''
         and document_key_basis is not null))

constraint forward_sem_prova_nao_finge_chave
  check (identity_state <> 'FORWARD_IDENTITY_UNPROVEN'
         or (source_id is not null and btrim(source_id) <> ''
         and document_key is null and document_key_basis is null))
```

O índice parcial não muda de forma: continua a nomear
`identity_state = 'FORWARD_IDENTIFIED'`, e agora há um terceiro estado que ele
exclui **por declaração**, como exclui o legado.

### S.6 · O CASO ITALIANO DE HOJE — E A DÍVIDA QUE ELE EXPÕE

Medido em `coleta/italy_pilot_collect.mjs`, caminho de sucesso:

```js
:349   const RAW_SHA256 = sha(r.buf);
:350   const ident = identidade(sourceId, alvo, r.buf);
:352   if (!ident.DOCUMENT_ID) {
:354     HEALTH_STATE: "FAILED", OBSERVATION_RESULT: "IDENTITY_FAILED"
:355     gravar(obs); detalhes.push(obs); continue;      ← e guardarRaw NUNCA corre
:392   const g = guardarRaw(sourceId, ident.DOCUMENT_ID, …);
```

```
CURRENT_ITALY_SUCCESS_CAN_REACH_CONTENT_DERIVED_DOCUMENT_KEY = NO
```

**B-1 é uma lacuna estrutural do caminho genérico/futuro, e NÃO um bug exercido
pelo slice italiano atual.** Dito com todas as letras, porque a diferença
decide o que é urgente: nenhuma observação italiana chega hoje ao dono do RAW
sem `DOCUMENT_ID`, e `CONTENT_DERIVED` tem **zero emissores** em todo o código
versionado — medido por varredura, o termo só existe nos documentos de plano.

Mas a mesma medição expõe a dívida:

```
RAW_PRESERVED_BEFORE_PARSE                    = YES   (linha 392 antes de 396)
RAW_PRESERVED_BEFORE_IDENTITY_CLASSIFICATION  = NO    (linha 352 antes de 392)
```

```
DÍVIDA COL-LAW-006 · o coletor italiano descarta bytes válidos quando a
classificação de identidade falha. Bytes que passaram na validação de
assinatura são perdidos por um passo que a lei manda correr DEPOIS.
```

Não se conserta aqui: `RUNTIME_CHANGED = 0`. Fica registada, com dono
(`coleta/italy_pilot_collect.mjs`) e com o efeito prático de que
`FORWARD_IDENTITY_UNPROVEN` **não terá emissor** enquanto ela não for paga.
Instalar o estado sem emissor é barato e correto; usá-lo é outro trabalho.

### S.7 · B-2 · JÁ FECHADO, E SEM `NULLS NOT DISTINCT`

A secção R fechou o escape do estado nulo com `NOT NULL` sem `DEFAULT`. Falta
responder à cláusula que o benchmark propôs.

O índice parcial cobre **apenas** linhas com `identity_state =
'FORWARD_IDENTIFIED'`. Dentro desse predicado:

```
run_id        NOT NULL   desde a 001
sha256        NOT NULL   desde a 001
source_id     NOT NULL   pelo check forward_identificado_exige_identidade
document_key  NOT NULL   pelo mesmo check
```

Nenhuma coluna indexada pode ser nula nas linhas indexadas. `NULLS NOT
DISTINCT` não muda um único resultado.

```
NULLS_NOT_DISTINCT_REQUIRED_FOR_CORRECTNESS = NO
```

**Não se acrescenta.** Uma cláusula que não altera nenhum caso é ruído que
sugere uma proteção inexistente — e daqui a um ano alguém lê-a como se os
campos pudessem ser nulos.

### S.8 · B-3 · O BANCO ACEITA UMA OBSERVAÇÃO A APONTAR PARA OUTRO CONTEÚDO

Lido na `025`, tal como ficou:

```sql
alter table public.raw_asset
  add column if not exists storage_object_id bigint
    references public.storage_object(id) on delete restrict;
```

Uma FK simples, para `id` e mais nada.

```
DECLARED_SHA_AGREEMENT_EXISTS_IN_DB = NO
```

O teste conceptual do §9, contra o schema de hoje:

```
raw_asset.sha256            = H1
raw_asset.storage_object_id = 10
storage_object.id           = 10
storage_object.sha256       = H2

FK       passa — o objeto 10 existe
CHECK    passa — H1 tem formato de sha
resultado: a linha entra, e diz duas coisas ao mesmo tempo
```

```
DB_ACCEPTS_OBSERVATION_POINTING_TO_DIFFERENT_CONTENT = YES
```

⚠️ **Esta casa já apanhou este defeito uma vez, e fechou-o.** Está escrito na
`022`, sobre o derivado:

> «com chaves estrangeiras separadas, dava para escrever `raw_asset_id` = A e
> `parent_sha256` = os bytes de B. As duas travas passavam. **FK EXISTIR NÃO
> BASTA.**»

Logo a solução mínima não é candidata nova: é o padrão da casa, aplicado ao
par que a `025` deixou de fora.

```sql
alter table public.storage_object
  add constraint objeto_id_e_sha_juntos unique (id, sha256);

alter table public.raw_asset
  add constraint a_observacao_e_a_copia_falam_do_mesmo_conteudo
  foreign key (storage_object_id, sha256)
  references public.storage_object(id, sha256) on delete restrict;
```

```
COMPOSITE_STORAGE_FK_REQUIRED = YES
```

**Quando é obrigatório — e as três perguntas não têm a mesma resposta:**

```
REQUIRED_BEFORE_PHASE_9   = NO
    o índice parcial é sobre colunas da própria observação; a divergência não
    o corrompe. E entre as fases 7 e 9 nada torna a divergência alcançável:
    a fase 4 ligou por ENDEREÇO e `unique (storage_path)` mantém 1:1.

REQUIRED_BEFORE_PHASE_10  = YES  ← O GATE
    a fase 10 é o que torna N:1 real. Caindo `unique (storage_path)`, o writer
    passa a REENCONTRAR um objeto para reutilizar, e reencontrar é onde se
    aponta para a cópia errada. É a fase que abre a porta, e a trava tem de
    estar posta antes de ela abrir.

REQUIRED_BEFORE_PHASE_11  = YES
    já obrigatório desde a 10; e na 11, sem `storage_path` na observação, o
    `sha256` fica a ÚNICA conferência cruzada que sobra.
```

Recomendação operacional: **instalar na fase 7**, junto com o resto. É aditiva,
não varre dado que não caiba num fôlego e não depende de nada das fases 8-9.
Adiá-la até à véspera da 10 é guardar uma dívida conhecida sem ganhar nada.

O writer canónico de hoje **não** consegue produzir a divergência — o SQL da
`preservar_coleta` procura o objeto por `storage_path` e escreve o `sha256` da
mesma linha conferida. O buraco é do schema, não do emissor. Mas um buraco de
schema é exatamente o que a `022` disse que não se deixa aberto.

### S.9 · B-4 · `source_url` É ATRIBUTO, E A CORREÇÃO ESPERA PELA B-1

Hoje:

```python
guarda/preservar_coleta.py:81
IDENTIDADE_DO_OBJETO = ("run_id", "sha256", "bytes", "captured_at", "source_url")
```

Cenário do §10: mesma `RUN`, mesmo `SOURCE_ID`, mesma unidade documental, os
mesmos bytes, URL A na tentativa 1 e URL B na tentativa 2 — um espelho, um
redirecionamento, um parâmetro que a fonte acrescentou.

```
SHOULD_THIS_BE_RETRY = YES
```

É a mesma corrida, o mesmo documento e os mesmos bytes. O que mudou foi **por
onde a tentativa passou**, e `COL-LAW-206` já diz que a URL não é uma das
identidades.

```
SOURCE_URL_IS_IDEMPOTENCY_IDENTITY = NO
```

**Mas não se retira agora.**

```
B4_FIX_DEPENDS_ON_B1 = YES
```

Enquanto a `DOCUMENT_KEY` não existir em coluna, `source_url` é o **único**
campo da identidade atual que separa duas publicações dos mesmos bytes da mesma
fonte. Retirá-lo antes seria abrir a S.1 no writer que funciona hoje, para
fechar um defeito que ainda não tem substituto instalado.

```
ORDEM OBRIGATÓRIA

  1. fases 7-8 instalam e preenchem source_id + document_key + estado
  2. a chave de idempotência passa a existir de facto
  3. SÓ ENTÃO source_url sai de IDENTIDADE_DO_OBJETO

Retirá-lo no passo 1 seria trocar uma trava a mais por nenhuma.
```

### S.10 · O INVARIANTE DO BENCHMARK — REFUTADO, E O DETECTOR FICA

Proposta: «a chave de idempotência deve distinguir pelo menos tanto quanto o
endereço.» Testada contra o que o endereço realmente é:

```
caminho_do_objeto() = PAIS/FONTE/TIPO/<sha16>-<discriminante>-<nome>
                                                              ↑
                                          basename do STORAGE_LOCATION
```

O `<nome>` é um nome de ficheiro. Duas observações da MESMA unidade documental,
dos mesmos bytes, na mesma corrida, com nomes de ficheiro diferentes, produzem
endereços diferentes — e são a mesma observação. Uma chave obrigada a
distingui-las estaria obrigada a tratar uma renomeação como um facto novo.

```
IDEMPOTENCY_KEY_MUST_BE_AT_LEAST_AS_DISCRIMINATING_AS_STORAGE_PATH = NO
```

A regra correta:

```
A CHAVE PRECISA DISTINGUIR TODA DIFERENÇA SEMÂNTICA/OBSERVACIONAL COMPROVADA.
NÃO TODA DIFERENÇA FÍSICA OU NOMINAL DO ENDEREÇO.
```

⚠️ **Mas o invariante do benchmark é um bom DETECTOR, e por isso não se deita
fora inteiro.** Quando o endereço distingue mais do que a chave, há duas
leituras possíveis, e só uma é inofensiva:

```
o endereço distingue por <nome>          → diferença NOMINAL   → a chave está certa
o endereço distingue por <discriminante> → diferença SEMÂNTICA → é a S.1, e é bug
```

Foi exatamente assim que a B-1 se deixou ver: `227779fdd6be9975-731` e
`227779fdd6be9975-6321` separam-se no discriminante, e a chave proposta não os
separava. O invariante não é a lei; é o alarme que aponta para ela.

### S.11 · O FECHO DA RECONCILIAÇÃO

```
B-1  DOCUMENT_KEY colapsa duas publicações      REPRODUZIDO · CORRIGIDO na S.4/S.5
     solução do benchmark (promover native id)  RECUSADA · S.2
B-2  identidade NULL escapa do índice parcial   JÁ FECHADO na R · NULLS NOT DISTINCT recusado
B-3  sem acordo declarativo de sha              CONFIRMADO · FK composta, gate na fase 10
B-4  source_url na identidade do writer         CONFIRMADO · retirada depende da B-1
     invariante «chave ≥ endereço»              REFUTADO · fica como detector · S.10
```

```
AS OITO CONDIÇÕES DO NOVO READY

 1. significado da DOCUMENT_KEY sem DOCUMENT_ID   FECHADO   não existe; sem fallback
 2. quando um id nativo participa                 FECHADO   só via DOCUMENT_ID_RULE do contrato
 3. destino do forward sem identidade             FECHADO   FORWARD_IDENTITY_UNPROVEN
 4. state NULL impossível no alvo                 FECHADO   secção R
 5. forward exige source/document/basis           FECHADO   secções R e S.5
 6. acordo raw_asset.sha ↔ storage_object.sha     FECHADO   FK composta, padrão da 022
 7. source_url classificado                       FECHADO   atributo; sai depois da B-1
 8. fase 10 continua proibida                     SIM
```

```
READY_FOR_B5B_IMPLEMENTATION = YES

B5B_BLOCKERS = nenhum

DÍVIDAS REGISTADAS, e nenhuma delas bloqueia o B5B:
  · COL-LAW-006 no coletor italiano (S.6) — sem ela, o terceiro estado nasce sem emissor
  · o fio da Q.3 — SOURCE_ID e DOCUMENT_KEY ainda não chegam ao dono do RAW
```

```
NEXT_STEP = B5B · implementar SOMENTE as fases 7, 8 e 9, agora com:
            três estados · sem CONTENT_DERIVED · FK composta do objeto
            e continuar a NÃO tocar nas fases 10 e 11
```

---

## T · C-CORR-B5B2 — OS TRÊS BLOQUEIOS FINAIS, FECHADOS CONTRA POSTGRES 16

**C-CORR-B5B2** · correção de especificação, zero implementação · a partir de `621a8d3f`

> Zero migration, zero runtime, zero banco vivo. As decisões abaixo foram
> **reproduzidas em PostgreSQL 16.13 descartável** (`127.0.0.1:55432`, cluster
> criado e destruído dentro desta missão). Onde diz REPROVADO, foi o banco que
> reprovou — não o raciocínio.

### T.0 · O QUE ESTA SECÇÃO REVOGA

Três instruções anteriores desta mesma cadeia deixam de valer. Ficam no
documento como histórico, marcadas no sítio, e **nenhuma delas se implementa**:

```
R.6   corte do legado por created_at            ⛔ REVOGADO   → T.2 · T.3
R.8   casos 9, 10 e 11 da bateria               ⛔ SUPERSEDED → T.7
S.5   os dois check de identidade forward       ⛔ SUPERSEDED → T.1
```

```
DUAS ORDENS EXECUTÁVEIS NO MESMO DOCUMENTO SÃO ZERO ORDENS.
```

### T.1 · BLOQUEIO 1 · «NÃO SEI QUAL DOCUMENTO» ≠ «NÃO SEI QUE FONTE PEDI»

A S.5 escreveu dois `check` separados, e ambos exigiam do `source_id` apenas
não-nulo e não-branco. Isto entrava:

```
identity_state = 'FORWARD_IDENTITY_UNPROVEN'
source_id      = 'NAO SEI'
document_key   = NULL
document_key_basis = NULL
```

A R.4 já tinha recusado a sentinela — mas só no estado `FORWARD_IDENTIFIED`. O
terceiro estado nasceu na S.5 **depois** dessa trava e passou ao lado dela.

**A correção não é uma terceira trava: é uma só, comum aos dois estados
forward.** O `source_id` não é a parte incerta de uma identidade incompleta. A
Collection sempre soube a que fonte pediu; o que pode faltar é o documento.

```sql
constraint fonte_real_em_qualquer_estado_forward
  check (identity_state = 'LEGACY_PRE_IDEMPOTENCY'
         or (source_id is not null and btrim(source_id) <> ''
             and upper(btrim(source_id)) not in
                 ('NAO SEI','NAO_SEI','NÃO SEI','NAO_SE_APLICA','UNKNOWN','NOT_KNOWN')));

constraint forward_identificado_exige_identidade
  check (identity_state <> 'FORWARD_IDENTIFIED'
         or (document_key is not null and btrim(document_key) <> ''
             and upper(btrim(document_key)) not in
                 ('NAO SEI','NAO_SEI','NÃO SEI','NAO_SE_APLICA','UNKNOWN','NOT_KNOWN')
             and document_key_basis is not null));

constraint forward_sem_prova_nao_finge_chave
  check (identity_state <> 'FORWARD_IDENTITY_UNPROVEN'
         or (document_key is null and document_key_basis is null));
```

⚠️ **O predicado é `= 'LEGACY_PRE_IDEMPOTENCY' or …`, e não `<> 'FORWARD_…'`.**
A diferença decide o futuro: escrito assim, qualquer estado que venha a nascer
cai automaticamente **dentro** da exigência de fonte real. Só o legado — que é
o único estado com licença para não ter identidade — fica de fora, e fica de
fora por nome.

O vocabulário é o **medido na R.4**, seis literais, e não uma lista nova.

```
FORWARD_UNPROVEN_UNKNOWN_SOURCE_CAN_ENTER = NO
```

Sem FK nova. Sem mudar o conceito de `SOURCE_ID`.

### T.2 · BLOQUEIO 3 · O CORTE POR RELÓGIO REPROVOU NO BANCO

A R.6 propôs congelar um instante e escrever `created_at < corte`. O revisor
apontou o contraexemplo; reproduzi-o antes de aceitar.

```
W  abriu a transacao em   20:00:03.851962
M  congelou o corte em    20:00:05.857606
M  terminou em            20:00:05.863010
W  INSERIU depois disso, com created_at = 20:00:03.851962   ← a hora da ABERTURA
```

```
resultado: id 6 | IT/nova/created-at-1 | LEGACY_PRE_IDEMPOTENCY
```

Uma linha criada **depois** do corte declarou-se legado, e a trava deixou.
`now()` é `transaction_timestamp()`: congela na abertura da transação e não
anda. Não é um defeito da proposta — é o que a função faz, e a proposta não o
sabia.

```
CREATED_AT_CUTOFF_IS_SUFFICIENT = NO   ← medido, PostgreSQL 16.13
```

E o remédio não é `clock_timestamp()`: `created_at` tem `DEFAULT`, logo quem
escreve pode simplesmente dar-lhe outro valor. **Um relógio que a linha carrega
não serve para datar a linha contra ela própria.**

### T.3 · A TRAVA QUE FUNCIONA — O SURROGATE, COM LOCK

O corte deixa de ser um instante e passa a ser um **número que já não pode ser
sorteado outra vez**. `raw_asset.id` é `bigserial` desde a `001`, e é o
`RAW_OBSERVATION_ID`. A fase 8 inteira corre numa transação:

```sql
begin;
  lock table public.raw_asset in access exclusive mode;   -- 1 · fecha a porta

  select coalesce(max(id),0) into corte from public.raw_asset;   -- 2 · congela

  update public.raw_asset                                        -- 3 · classifica
     set identity_state = 'LEGACY_PRE_IDEMPOTENCY'
   where identity_state is null;

  execute format(                                                -- 4 · trava constante
    'alter table public.raw_asset add constraint legado_e_anterior_ao_corte '
    'check (identity_state <> %L or id <= %s) not valid',
    'LEGACY_PRE_IDEMPOTENCY', corte);
  alter table public.raw_asset validate constraint legado_e_anterior_ao_corte;

  alter table public.raw_asset alter column identity_state set not null;   -- 5
commit;                                                          -- 6 · abre a porta
```

Como o banco a guardou, lida de volta de `pg_constraint`:

```
CHECK (((identity_state <> 'LEGACY_PRE_IDEMPOTENCY'::text) OR (id <= 6)))
```

```
LEGACY_CUTOFF_MECHANISM = SURROGATE_ID_FROZEN_UNDER_LOCK
```

⚠️ **É um literal, e essa é a metade do valor.** Sem função, sem relógio, sem
nada que possa devolver outra resposta amanhã. Um `CHECK` só é uma promessa se
o predicado não depender de quem o lê nem de quando.

**O lock, e porque é este.** `ACCESS EXCLUSIVE` conflitua com o
`ROW EXCLUSIVE` que todo `INSERT` toma, e é o mesmo que os dois `ALTER TABLE`
dos passos 4 e 5 iriam tomar de qualquer maneira. Tomá-lo **uma vez, no topo**,
evita a subida de lock a meio da transação — que é onde nascem os deadlocks.

```
LOCK_USED = LOCK TABLE public.raw_asset IN ACCESS EXCLUSIVE MODE
```

### T.4 · OS DOIS CENÁRIOS DE CONCORRÊNCIA, MEDIDOS

**CENÁRIO A · a transação velha que ainda não inseriu.**

```
W  abriu a transacao ANTES da migration
M  pegou ACCESS EXCLUSIVE as        20:00:40.176614
M  congelou LEGACY_CUTOFF_ID = 5
W  tentou o INSERT as               20:00:41.177087
        observador: pid 908 | wait_event_type=Lock | insert into raw_asset …
M  fez COMMIT as                    20:00:43.183625
W  conseguiu inserir as             20:00:43.186488   com id 6
```

```
PRE_MIGRATION_TX_WITHOUT_INSERT_RESULT = BLOQUEADO ATE AO COMMIT · id 6 > corte 5
```

O `INSERT` não «passou primeiro»: ficou à espera, e quando a porta abriu o
número que lhe coube já estava fora do conjunto congelado.

**CENÁRIO B · a transação que já inseriu e ainda não commitou.**

```
W  INSERIU (sem commit) id 6 as     20:01:00.574133
        observador: pid 936 | wait_event_type=Lock | lock table raw_asset in access …
W  fez COMMIT as                    20:01:03.577955
M  pegou ACCESS EXCLUSIVE as        20:01:03.579369   ← 1,4 ms depois
M  congelou LEGACY_CUTOFF_ID = 6    ← VIU a linha
```

```
PRE_MIGRATION_TX_WITH_UNCOMMITTED_INSERT_RESULT = A MIGRATION ESPERA E DEPOIS VE
```

A migration esperou pela transação inteira, e ao pedir `max(id)` depois do lock
— em `READ COMMITTED`, snapshot novo por instrução — encontrou a linha 6 e
classificou-a. Nenhuma linha ficou com estado nulo:

```
select count(*) from raw_asset where identity_state is null   →   0
```

⚠️ **E se tivesse ficado, o passo 5 gritava.** `set not null` sobre uma linha
nula reprova a migration inteira. A trava não depende de eu ter pensado em
todos os casos: a que sobrar reprova a fase, em vez de passar calada.

### T.5 · O QUE UM `INSERT` FUTURO CONSEGUE E NÃO CONSEGUE

```
CANONICAL_WRITER_EXPLICITLY_WRITES_RAW_ASSET_ID = NO
```

Medido nos três emissores que existem:

```
guarda/preservar_coleta.py:440   insert into public.raw_asset (run_id, storage_path,
                                 media_type, bytes, sha256, captured_at, source_url,
                                 storage_object_id)                  ← sem id
guarda/catalogo_importar.py:430  mesma lista                          ← sem id
supabase/importacoes/ADAMA-ES-…  (run_id, storage_path, …)            ← sem id
```

Nenhum toca no `id`. Logo o número vem sempre da sequência, e a sequência só
anda para a frente:

```
depois de um ROLLBACK a sequencia esta em 33 — o numero foi gasto, nao devolvido
```

```
NATURAL_FUTURE_ID_CAN_FALL_INSIDE_LEGACY_CUTOFF = NO
```

O `nextval` de um `INSERT` é avaliado **dentro** do próprio `INSERT`, que precisa
de `ROW EXCLUSIVE` — e é precisamente esse lock que a fase 8 segura. Enquanto o
corte não está congelado e travado, nenhum número novo sai.

**O limite, medido em vez de assumido.** Abri um buraco no `id` 4 e escrevi o
`id` à mão:

```
insert … (id, …, identity_state) values (4, …, 'LEGACY_PRE_IDEMPOTENCY')
    → INSERT 0 1          ACEITE

insert … (…,  identity_state) values (    …, 'LEGACY_PRE_IDEMPOTENCY')
    → ERROR: violates check constraint "legado_e_anterior_ao_corte"
```

```
LEGACY_CUTOFF_DB_ENFORCED = YES  para todo caminho que deixe a sequência atribuir o id
RESIDUO                   = quem escreve o surrogate À MÃO, para dentro de um
                            buraco abaixo do corte, ainda declara legado
```

Isto **não** é escape por esquecimento — é forjar o identificador da observação,
a mesma família de `created_at` falsificado, e mais estreita: exige um buraco
*e* um `id` explícito. Nenhum emissor desta árvore o faz.

```
BLOCKS_B5B = NO
```

Endurecimento **opcional**, para o B5B avaliar e não para adotar aqui:
converter `id` para `generated always as identity`, que recusa `id` explícito
sem `OVERRIDING SYSTEM VALUE`. Fecha o resíduo, mas mexe na coluna que nove FKs
apontam e teria de ser provada lá. **Não decidido nesta missão.**

### T.6 · BLOQUEIO 2 · `CONTENT_DERIVED` NÃO TEM MAIS NENHUMA ORDEM DE ACEITAÇÃO

A S.4 revogou o valor; a R.8 continuava a mandar aceitá-lo num caso de teste.
Duas ordens executáveis, e a mais velha era a mais concreta.

```sql
constraint base_da_chave_tem_vocabulario
  check (document_key_basis is null or document_key_basis = 'SOURCE_DOCUMENT_ID')
```

Medido contra o banco, e o resultado é o mesmo dos dois lados:

```
basis = CONTENT_DERIVED + key = sha256 INTEIRO   → RECUSADO  base_da_chave_tem_vocabulario
basis = CONTENT_DERIVED + key = sha16            → RECUSADO  base_da_chave_tem_vocabulario
```

```
CONTENT_DERIVED_FINAL_STATUS          = REVOKED
CONTENT_DERIVED_ACCEPTANCE_TESTS_REMAIN = NO
```

⚠️ **A recusa não olha para o `document_key`.** Não é «CONTENT_DERIVED com a
chave errada»: é o valor que não existe. Um `check` que examinasse a chave
sugeriria que há uma forma certa de o escrever.

```
FORWARD_IDENTIFIED  ⇒  document_key_basis = 'SOURCE_DOCUMENT_ID'
```

### T.7 · A BATERIA FINAL — 27 CASOS, TODOS CORRIDOS

Substitui a lista da R.8. Correu contra PostgreSQL 16.13 com as travas da T.1,
T.3 e T.6 instaladas; **todos os 27 deram o veredito esperado.**

```
CORTE DO LEGADO
  1  novo INSERT declarando LEGACY                      REJEITADO  legado_e_anterior_ao_corte
  2  novo FORWARD_IDENTIFIED completo                   ACEITE
  3  novo FORWARD_IDENTITY_UNPROVEN com fonte real      ACEITE

O ESTADO NÃO PODE FALTAR
  4  identity_state = NULL                              REJEITADO  not-null
  5  o writer OMITE a coluna                            REJEITADO  not-null (sem DEFAULT)

FONTE REAL NOS DOIS ESTADOS FORWARD          ← as seis sentinelas, duas vezes
  6-11   FORWARD_IDENTIFIED       + source_id = NAO SEI · NAO_SEI · NÃO SEI ·
                                    NAO_SE_APLICA · UNKNOWN · NOT_KNOWN   REJEITADO ×6
 12-17   FORWARD_IDENTITY_UNPROVEN + as mesmas seis                       REJEITADO ×6
 18  UNPROVEN + source_id = 'unknown' (minúsculas)      REJEITADO  upper() apanha
 19  UNPROVEN + source_id = '   '                       REJEITADO  btrim() apanha
 20  UNPROVEN + source_id = NULL                        REJEITADO

CONTENT_DERIVED REVOGADO
 21  basis = CONTENT_DERIVED + key = sha256 inteiro     REJEITADO  base_da_chave_tem_vocabulario
 22  basis = CONTENT_DERIVED + key = sha16              REJEITADO  base_da_chave_tem_vocabulario

COERÊNCIA DOS DOIS ESTADOS FORWARD
 23  IDENTIFIED sem document_key                        REJEITADO  forward_identificado_exige_identidade
 24  IDENTIFIED sem document_key_basis                  REJEITADO  forward_identificado_exige_identidade
 25  UNPROVEN a fingir chave documental                 REJEITADO  forward_sem_prova_nao_finge_chave
 26  estado inventado 'FORWARD_QUALQUER_COISA'          REJEITADO  estado_de_identidade_tem_vocabulario
 27  após a fase 8, linhas com estado nulo              CONTAGEM = 0
```

E os dois cenários de concorrência da T.4, que não são casos de `INSERT` e por
isso se contam à parte.

**Estes 27 escrevem-se no B5B, junto com a migration que instalam. Nesta missão
não se escreveu nenhum ficheiro de prova** — o cluster foi criado, medido e
destruído.

### T.8 · `PHASE_10_UNPROVEN_GATE` — REGISTADO, NÃO RESOLVIDO

O índice parcial da fase 9 nomeia `FORWARD_IDENTIFIED`. **Ele não protege
`FORWARD_IDENTITY_UNPROVEN`** — e hoje isso não custa nada, porque
`unique (raw_asset.storage_path)` ainda segura tudo. A fase 10 é que retira
essa rede.

```
PHASE_10_UNPROVEN_GATE

  Antes de retirar UNIQUE(raw_asset.storage_path), pelo menos UM tem de ser
  verdadeiro:

    A   FORWARD_IDENTITY_UNPROVEN_EMITTERS = 0
    B   IDEMPOTENCY_FOR_FORWARD_IDENTITY_UNPROVEN = DEFINED_AND_PROVEN

  Hoje: A é verdadeiro — o coletor italiano recusa a observação sem
  DOCUMENT_ID (S.6), logo o estado nasce sem emissor. Mas isso muda no dia em
  que a dívida COL-LAW-006 for paga, e o gate é o que impede que mude em
  silêncio.
```

**A chave de idempotência do UNPROVEN não se define agora.** Sem emissor não há
caso a decidir, e decidir sem caso é o que a Q.5 chamou antecipação. O que se
regista é a obrigação de a decidir **antes** da fase 10, nunca depois.

`source_url` entra aqui pela mesma porta: a S.9 já tinha dito que ele sai só
depois de a `DOCUMENT_KEY` estar instalada, preenchida e usada. Para o UNPROVEN
não há chave documental nenhuma, logo **remoção global de `source_url` não fica
autorizada enquanto este gate não fechar**.

### T.9 · O QUE NÃO SE REABRIU

```
FK COMPOSTA DO OBJETO   decidida na S.8, mantida:
                        storage_object unique(id, sha256)
                        raw_asset fk (storage_object_id, sha256) → (id, sha256)
                        REQUIRED_BEFORE_PHASE_10 = YES · aditiva no B5B

SOURCE_URL              SOURCE_URL_IS_IDEMPOTENCY_IDENTITY = NO, mantido.
                        Não sai até DOCUMENT_KEY instalada, preenchida e usada;
                        e para o UNPROVEN, até o gate da T.8.

B5A                     fases 1-6 intactas. Nada nesta secção lhes toca.
FASES 10 e 11           continuam proibidas.
```

### T.10 · O FECHO

```
FORWARD_IDENTIFIED_SENTINELS_REJECTED     = YES   (6 casos)
FORWARD_UNPROVEN_SENTINELS_REJECTED       = YES   (6 casos)
FORWARD_UNPROVEN_UNKNOWN_SOURCE_CAN_ENTER = NO

CONTENT_DERIVED_FINAL_STATUS              = REVOKED
CONTENT_DERIVED_ACCEPTANCE_TESTS_REMAIN   = NO

CREATED_AT_CUTOFF_IS_SUFFICIENT           = NO    (reproduzido e reprovado)
LEGACY_CUTOFF_MECHANISM                   = SURROGATE_ID_FROZEN_UNDER_LOCK
LEGACY_CUTOFF_DB_ENFORCED                 = YES   (caminho natural)
LOCK_USED                                 = ACCESS EXCLUSIVE
CANONICAL_WRITER_EXPLICITLY_WRITES_ID     = NO
NATURAL_FUTURE_ID_CAN_FALL_INSIDE_CUTOFF  = NO

IDENTITY_STATE_TARGET_NULLABLE            = NO
IDENTITY_STATE_HAS_DEFAULT                = NO
IDENTITY_STATE_VOCABULARY                 = LEGACY_PRE_IDEMPOTENCY
                                          | FORWARD_IDENTIFIED
                                          | FORWARD_IDENTITY_UNPROVEN

PHASE_10_UNPROVEN_GATE                    = REGISTADO (T.8)
PHASE_10_STILL_FORBIDDEN                  = YES
```

```
READY_FOR_B5B_IMPLEMENTATION = YES
READY_FOR_PHASE_10           = NO
B5B_BLOCKERS                 = nenhum
```

```
NEXT_STEP = B5B · implementar SOMENTE as fases 7, 8 e 9, com:
            três estados · fonte real nos dois forward · CONTENT_DERIVED fora ·
            corte do legado pelo surrogate sob lock · FK composta do objeto
            e continuar a NÃO tocar nas fases 10 e 11
```

---

## U · C-LIVE-025 — A 025 ENTROU NO BANCO VIVO

**C-LIVE-025** · aplicação controlada · 2026-09-10

> A migration 025 deixou de ser proposta. Foi aplicada ao banco canónico pelo
> aplicador da casa, com o censo congelado antes e conferido depois.

### U.1 · O FICHEIRO CONTINUA A DIZER «NÃO EXECUTADA», E ISSO ESTÁ CERTO

```
supabase/migrations/025_o_objeto_ganha_casa.sql  ← NÃO foi editado
```

⚠️ **Uma migration aplicada é artefacto imutável.** O livro-razão guarda o
`sha256` do ficheiro inteiro, e reescrevê-lo para dizer que correu partiria a
cadeia em qualquer banco onde ele já esteja. A 022 vive com a mesma frase desde
que foi aplicada, e há teste que exige que assim continue.

```
QUEM DIZ QUE UMA MIGRATION CORREU É O LIVRO-RAZÃO, NUNCA O FICHEIRO.
```

### U.2 · O QUE FOI FEITO, E POR QUE PORTA

```
REF DA OPERAÇÃO   ops/live-025-only-20260910 → 09277bf8
                  ponteiro puro. A 025 lá está; a 026 ainda não existia.
PROCEDIMENTO      workflow_dispatch de .github/workflows/supabase-migrate.yml
                  importar = false
CORRIDAS          censo BEFORE   34531578033
                  aplicação      34531767304
                  censo AFTER    34531982144
```

O aplicador percorreu a cadeia inteira e escreveu **uma** linha:

```
MIGRATION_001..024 = SKIP (ja no livro-razao) HASH=MATCH
MIGRATION_025      = PASS
POST_APPLY_VERIFICATION (008) = PASS
passos de importação = skipped
```

### U.3 · O QUE MUDOU, MEDIDO DOS DOIS LADOS

| | BEFORE | AFTER |
|---|---|---|
| `raw_asset` linhas | 252 | 252 |
| min · max `id` | 1 · 890 | 1 · 890 |
| ids distintos | 252 | 252 |
| `storage_path` distintos | 252 | 252 |
| preservados | 252 | 252 |
| **md5 do CONJUNTO de ids** | `bf54cf47…86ce` | `bf54cf47…86ce` |
| `storage_object` | não existia | 252 linhas, RLS activa |
| `raw_asset.storage_object_id` | não existia | 252 ligadas, 0 preservadas sem cópia |
| ligações com caminho divergente | — | 0 |
| ligações com sha divergente | — | 0 |
| objectos sem observação | — | 0 |
| `unique (storage_path)` | presente | presente |

```
RAW_ASSET_ID_SET_PRESERVED = YES — e é o md5 do conjunto que o diz,
                             não a contagem. Count igual não é conjunto igual.
```

A trava condicional da 025 entrou **validada**, e não apenas criada:

```
preservado_aponta_para_a_copia    | c | convalidated = true
raw_asset_storage_object_id_fkey  | f | convalidated = true
```

### U.4 · E A 026 CONTINUA FORA

```
raw_asset.identity_state · source_id · document_key · document_key_basis
attempts · last_attempt_at                    NENHUMA existe no banco vivo
026 no livro-razão                            ausente
B5B_026_LIVE_APPLIED = NO
```

O ref da operação foi escolhido **exactamente** por isso: no `09277bf8` a 026
ainda não tinha nascido, logo o aplicador não tinha como a ver. Não se apagou
nada da fundação para conseguir isso.

### U.5 · OS DOIS BLOQUEIOS DA 026, QUE ESTA MISSÃO NÃO TOCOU

```
B5B_026_BLOCKER_ATOMICITY           = OPEN
    o aplicador corre cada ficheiro sem `--single-transaction`. Uma falha a
    meio da 026 deixa a fase 7 aplicada e o estado por fechar. É recuperável
    repetindo, e isso está medido — mas não é atómico.

B5B_026_BLOCKER_HISTORICAL_IMPORTER = OPEN
    o caminho de importações sob demanda carrega 138 `insert` em `raw_asset`
    sem identidade. Depois da 026 eles são recusados, e o `on conflict` não
    salva: o NOT NULL é cobrado antes de haver conflito para resolver.
```

```
READY_FOR_PHASE_10 = NO
```

---

## V · C-LIVE-026 — A OBSERVAÇÃO GANHOU IDENTIDADE NO BANCO VIVO

**C-LIVE-026** · aplicação controlada · 2026-09-10

> A 026 deixou de ser proposta. Aplicada ao banco canónico pelo aplicador da
> casa — o mesmo que a C-PREP-026 corrigiu — com o censo congelado antes e
> conferido depois.

### V.1 · O QUE FOI FEITO, E POR QUE PORTA

```
REF DA OPERAÇÃO   claude/raw-observation-identity-3jbwco @ 81ca1eda
                  026_BLOB_SHA = 0963ff53d784e5422f9ed4b96afe478311b4d090
                  igual ao que a preparação aprovou, recalculado
PROCEDIMENTO      workflow_dispatch de .github/workflows/supabase-migrate.yml
                  importar = false
CORRIDAS          censo BEFORE   34534258240
                  aplicação      34537688899
```

Desta vez **não foi preciso ramo operacional**: o ponteiro existia para esconder
a 026 do migrador, e agora ela é justamente o que se quer aplicar. A fundação é
o ref auditado.

```
MIGRATION_001..025 = SKIP (ja no livro-razao) HASH=MATCH
MIGRATION_026      = PASS
POST_APPLY_VERIFICATION (008) = PASS
passos 5, 6 e 7 (importações) = skipped
```

### V.2 · A CORREÇÃO DA C-PREP-026 ESTAVA A SEGURAR

A 026 entrou por um aplicador que só existe desde a preparação: cada ficheiro
corre com `--single-transaction`, e o registo no livro-razão viaja no mesmo
fluxo. Se a fase 8 tivesse reprovado — por exemplo na precondição da sequência —
não teria ficado uma coluna sequer.

```
A 026 TEM SEIS FASES. SEM ATOMICIDADE, UMA FALHA A MEIO
DEIXARIA METADE DA IDENTIDADE INSTALADA E O LIVRO SEM SABER.
```

### V.3 · O QUE MUDOU, MEDIDO DOS DOIS LADOS

| | BEFORE | AFTER |
|---|---|---|
| `raw_asset` linhas | 252 | 252 |
| min · max `id` | 1 · 890 | 1 · 890 |
| ids distintos | 252 | 252 |
| **md5 do CONJUNTO de ids** | `bf54cf47…86ce` | `bf54cf47…86ce` |
| `storage_object` | 252 | 252 |
| observações ligadas | 252 | 252 |
| preservadas sem cópia | 0 | 0 |
| caminho / sha divergentes | 0 / 0 | 0 / 0 |
| `unique (storage_path)` | presente | presente |
| checks em `public` | 129 | 135 |
| índices únicos em `public` | 135 | 137 |

As seis colunas da 026 não existiam antes — confirmado por **enumeração** das
colunas de `raw_asset`, e não por um probe que só encontra o que procura.

### V.4 · O LEGADO, E O QUE NINGUÉM LHE INVENTOU

```
LEGACY_ROWS                    = 252
LEGACY_COM_IDENTIDADE          = 0
IDENTITY_STATE_NOT_NULL        = true
IDENTITY_STATE_TEM_DEFAULT     = 0
```

⚠️ **Nenhuma das 252 recebeu fonte ou documento.** Elas não são anónimas por
descuido: são anteriores à lei, e dizê-lo é a única coisa honesta que se podia
escrever nelas. O corte que as separa do futuro é o `id`, congelado sob
`ACCESS EXCLUSIVE` — não um relógio, que a C-CORR-B5B2 já tinha reprovado.

### V.5 · A AUDITORIA PASSA A COBRAR O CONTRATO DA 026

O que a auditoria fazia pela 025 passa a fazer pela 026: contar, comparar e
**reprovar**. Sete travas pelo nome, com `convalidated`; o estado sem `default`;
zero observação sem estado; zero identidade no legado; e o índice de
idempotência forward válido.

```
UMA TRAVA CRIADA E NÃO VALIDADA É UMA PROMESSA SOBRE O FUTURO
E UM SILÊNCIO SOBRE O PASSADO.
```

### V.6 · O QUE CONTINUA FECHADO

```
NEW_RAW_ASSET_ROWS_CREATED_BY_C_LIVE_026 = 0
    Nenhum canário. A prova do writer forward foi feita em banco descartável
    na preparação, e o banco vivo termina com as mesmas 252 observações.

UNIQUE(raw_asset.storage_path)  PRESENTE
READY_FOR_PHASE_10              NO
```

---

## W · C-PREP-PHASE-10 — QUAL É A LEI DA FASE 10, E PORQUE ELA AINDA NÃO ENTRA

Missão **de preparação**. Zero DDL no vivo, zero escrita no vivo, zero coleta,
zero importação. O que ela produz é uma lei **medida**, um protótipo que não
mora na pasta das migrations, e um veredicto que continua `NO`.

    LIVE_DB_DDL = 0 · LIVE_DB_WRITES = 0 · LIVE_COLLECTION = 0 · LIVE_IMPORT = 0

### W.0 · O estado congelado, relido antes de qualquer coisa

Auditoria somente-leitura do banco canónico, run `34539798312`, no
`FOUNDATION_HEAD = 1b1487f0`:

```
025 = APLICADA          026 = APLICADA          MIGRATIONS_PENDENTES = nenhuma
raw_asset = 252         storage_object = 252    LEGACY_ROWS = 252
LEGACY_COM_IDENTIDADE = 0                       LEGACY_CUTOFF_VALUE = 890
identity_state NOT NULL = true                  IDENTITY_STATE_TEM_DEFAULT = 0
FORWARD_IDEMPOTENCY_INDEX_VALID = 1             unique(storage_path) = PRESENTE
RAW_ASSET_ID_SET_MD5 = bf54cf470e59a3c512e017a967cd86ce
```

Idêntico ao que a `C-LIVE-026` deixou. Nada mudou, e por isso não houve
`HARD STOP`.

### W.1 · A pergunta da fase 10, dita sem rodeios

A `025` separou as espécies e a `026` deu estado à observação. Ficou de fora,
de propósito, a trava que **junta o que as duas separaram**:

```
unique (raw_asset.storage_path)   →   duas observações no mesmo endereço são UMA
```

E isso contradiz a espécie. Uma corrida nova que reencontra o mesmo documento
faz uma **observação nova** — um facto novo, com outra hora e outra corrida.
Hoje ela não entra. Medido em `provas/a_lei_da_fase_10.py`, caso `C2`:

```
C2_A_OBSERVACAO_NOVA_ENTRA = NAO
C2_QUEM_A_IMPEDE           = raw_asset_storage_path_key
```

### W.2 · O que foi medido, e onde

Tudo contra **PostgreSQL 16 descartável**, com `001 + 022 + 025 + 026`
aplicadas, e nada contra SQLite: entram índices parciais únicos, inferência de
árbitro no `on conflict`, `ACCESS EXCLUSIVE` e `pg_stat_activity`, e nenhum
deles existe no SQLite com esta semântica.

A prova vive em **`provas/a_lei_da_fase_10.py`** e corre inteira num banco que
nasce e morre: `A_LEI_DA_FASE_10_DB_TESTED = PASS`.

| parte | o que perguntou | o que o banco respondeu |
|---|---|---|
| C1 | retry da mesma corrida | recusado — pelo **endereço**, não pela identidade |
| C2 | corrida nova, mesmo doc, mesmos bytes | **recusado** — é isto que a fase 10 abre |
| C3 | corrida nova, mesmo doc, bytes novos | aceite; duas versões do mesmo documento |
| C4 | dois documentos, mesmos bytes | aceite; **dois** objectos para um só `sha256` |
| C5 | mesmo documento, duas fontes | aceite; `source_id` está na chave |
| C6 | `FORWARD_IDENTITY_UNPROVEN` | entra — e **nenhum índice único o cobre** |
| F | N observações → 1 objecto | proibido hoje, por `raw_asset_storage_path_key` |
| G | identidade do objecto | é o **endereço**; `sha256` não é único |
| N | objecto sem observação | permitido; nada no esquema o proíbe |
| K/L4 | objecto e observação | precisam da **mesma transacção** |
| L1 | duas sessões, mesma observação forward | a segunda espera, e depois é recusada |
| L2 | duas sessões, mesma observação sem prova | **as duas entram** |
| L5 | o DDL contra um escritor vivo | espera pelo `commit`; `ACCESS EXCLUSIVE` |
| M | a máquina morre entre as duas escritas | objecto órfão sobrevive; o retry cura-o |

### W.3 · A chave do `FORWARD_IDENTITY_UNPROVEN` — escolhida por medição

Este era o buraco. O índice da fase 9 tem predicado `FORWARD_IDENTIFIED`; uma
linha sem prova não o satisfaz, e portanto **não tem chave nenhuma**.

Cinco candidatas, cada uma instalada como índice parcial a sério, e os mesmos
cinco cenários por todas:

```
                             S1  S2  S3  S4  S5
K0 · nada                    2!  2   2   2   2    REPROVADA
K1 · (run, fonte, sha256)    1   2   1!  1!  2    REPROVADA
K2 · (run, fonte, endereço)  1   2   2   2   2    APROVADA
K3 · (fonte, sha256)         1   1!  1!  1!  2    REPROVADA
K4 · K2 + sha256             1   2   2   2   2    APROVADA
```

`S3` é o contraexemplo que esta casa **mediu** nos 195 objectos italianos: a
ADAMA publicou o **mesmo PDF** em `media/731` e em `media/6321`. Dois factos
sobre o mundo, um conteúdo só.

    O CONTEUDO NAO E O DOCUMENTO. NUNCA FOI.

`K1` — a candidata que qualquer um escreveria primeiro, porque parece a mais
honesta — junta esses dois factos num. `K3` faz pior: apaga a corrida nova.
Fica `K4`, que é `K2` mais `sha256`, porque o endereço escrito na linha **pode
divergir** do endereço do objecto que ela aponta (medido:
`F_O_ENDERECO_DA_LINHA_PODE_DIVERGIR_DO_OBJETO = SIM`), e nesse dia o `sha256`
é a única coisa na chave que ainda fala do conteúdo.

### W.4 · A separação que a missão pediu que fosse investigada

Ela existe, e é o que as medições desenham:

```
IDENTIDADE DO DOCUMENTO    (source_id, document_key)     só em FORWARD_IDENTIFIED
IDENTIDADE DA TENTATIVA    (run_id, source_id, endereço, sha256)
```

A primeira diz **o quê**. A segunda diz **esta ida buscar**. São perguntas
diferentes, e por isso não podem partilhar chave: uma tentativa repetida da
mesma corrida é a mesma tentativa; a mesma tentativa noutra corrida é outra.
E onde não há prova do documento, a casa **não inventa** uma — regista a
tentativa, que é a única coisa que sabe.

### W.5 · As dez leis propostas

Cada uma com regra, razão, prova e o contraexemplo que ela evita.

1. **O endereço não é identidade da observação.**
   *Porquê:* junta observações distintas. *Prova:* `C2`, `F_N_OBSERVACOES_PARA_UM_OBJETO = NAO`.
   *Evita:* a corrida nova desaparecer em silêncio.
2. **O endereço é identidade do OBJECTO, e continua a ser.**
   *Porquê:* uma cópia guardada num sítio é uma cópia. *Prova:* `G_DOIS_OBJETOS_NO_MESMO_ENDERECO = NAO`.
   *Evita:* dois bytes diferentes no mesmo caminho.
3. **`sha256` identifica conteúdo, nunca documento.**
   *Prova:* `C4_OBJETOS_PARA_O_MESMO_SHA = 2`, `G_DOIS_OBJETOS_COM_O_MESMO_SHA = SIM`.
   *Evita:* `media/731` e `media/6321` virarem um.
4. **Sem `DOCUMENT_ID` provado não há chave de documento — e a tentativa tem chave própria.**
   *Prova:* parte E, `K4` aprovada. *Evita:* o `UNPROVEN` duplicar sem limite (`H_O_UNPROVEN_DUPLICA_SEM_LIMITE = SIM`).
5. **A observação e o objecto entram na MESMA transacção.**
   *Prova:* `L4_A_OBSERVACAO_ENTRA_SEM_O_OBJETO = 0`. *Evita:* observação a apontar para nada.
6. **O objecto órfão é aceite, e o retry reencontra-o.**
   *Porquê:* o armazém remoto não está na transacção do Postgres. *Prova:* `M_*`.
   *Evita:* apagar bytes que já custaram uma ida à rede.
7. **O estado de identidade não recua nem avança por `update`.**
   *Prova:* hoje o esquema **deixa** (`S3 · UPDATE que promove: ACEITE`); com o protótipo, `PROMOVER_UNPROVEN_POR_UPDATE = RECUSADO`.
   *Evita:* dizer, em retrospectiva, que se sabia o que não se sabia.
8. **Contar tentativas não é reescrever o passado.**
   `attempts` e `last_attempt_at` continuam escrevíveis. *Prova:* `CONTAR_TENTATIVAS_CONTINUA_PERMITIDO = SIM`.
9. **A derivação é por conteúdo, não por observação.**
   *Prova:* a segunda observação dos mesmos bytes é recusada por `derivacao_e_unica_por_regua`.
   *Evita:* derivar duas vezes os mesmos bytes com a mesma régua.
10. **Nenhuma lei acima vale enquanto o escritor não souber falá-la.**
    *Prova:* W.6. *Evita:* um esquema correcto servido por código que escolhe uma linha ao acaso.

### W.6 · Porque o veredicto é `NO` — os seis bloqueios que sobram

Nenhum deles se cura com `alter table`.

1. **`guarda/preservar_coleta.py` lê por endereço.** `objeto_em(storage_path)`
   faz `linhas[0] if linhas else None`. Com o `unique` de pé isso é uma linha;
   sem ele são N, e a função escolhe **uma em silêncio**. Medido:
   `J_OBJETO_EM_ENDERECO_DEIXA_DE_SER_UMA_LINHA = 2`.
2. **O `on conflict` do escritor não vê a linha sem prova.** Medido:
   `J_O_ON_CONFLICT_DO_ESCRITOR_NAO_VE_O_UNPROVEN = SIM`, e a linha entra duas
   vezes. Falta-lhe um segundo `on conflict`, contra o índice da tentativa.
3. **`attempts` e `last_attempt_at` continuam sem escritor.** Nasceram na 026 e
   ninguém as escreve.
4. **O endereço é FABRICADO quando a fonte cala.** `coleta/ingresso.py:215` cai
   para `f.SHA256[:16]`. Medido pelo código de produção, com dois ficheiros
   distintos de conteúdo igual e mesmo nome:

   ```
   com id nativo   XX/…/0b5c068c31e225fe-media-731-FDS.pdf
                   XX/…/0b5c068c31e225fe-media-6321-FDS.pdf     SEPARADOS
   sem id nativo   XX/…/0b5c068c31e225fe-0b5c068c31e225fe-FDS.pdf
                   XX/…/0b5c068c31e225fe-0b5c068c31e225fe-FDS.pdf   COLIDEM
   ```

   A lei 4 põe o endereço numa chave. O endereço só vale o que vale o
   discriminante — e este é inventado por nós. A cura é a montante.
5. **Quatro emissores de `on conflict (storage_path)` partem no passo 1**, e
   partem a **planear**, não a correr: 138 inserts em
   `supabase/importacoes/ADAMA-ES-CATALOGO-2026-08-30.sql`, mais
   `guarda/catalogo_importar.py`, `supabase-raw-roundtrip.yml` e
   `supabase-fichas-adama.yml`. Estão travados desde a `C-PREP-026`
   (`guarda/trava_do_escritor_antigo.sh`) — **travados não é curados**.
6. **Dois workflows lêem `where storage_path = '…'` à espera de UMA linha.**
   Com N observações no mesmo endereço a comparação de shell deixa de fazer
   sentido.

### W.7 · O protótipo, e onde ele mora

**`supabase/ensaios/PROTOTIPO-FASE-10-IDENTIDADE-DA-TENTATIVA.sql`** — três
passos: retirar o `unique` do endereço, criar o índice da tentativa, e o
gatilho que impede o estado de recuar.

Ele **não** está em `supabase/migrations/`, e a razão é mecânica: o aplicador
varre `supabase/migrations/*.sql` e mais nada.

    PROTOTIPO QUE MORA NA PASTA DAS MIGRATIONS E UMA MIGRATION
    QUE AINDA NAO FOI APLICADA. E ISSO NAO E UM PROTOTIPO.

Aplicado a um banco descartável próprio, ele faz o que promete — e isto foi
**corrido**, não afirmado:

```
C2_A_OBSERVACAO_NOVA_ENTRA            SIM
C1_RETRY_EXACTO_RECUSADO              SIM   por raw_identidade_forward_idx
S1_RETRY_DA_MESMA_CORRIDA_RECUSADO    SIM   por raw_tentativa_sem_prova_idx
S2_CORRIDA_NOVA_ENTRA                 SIM
S3_ADAMA_731_E_6321_SEPARADOS         SIM
PROMOVER_UNPROVEN_POR_UPDATE          RECUSADO
CONTAR_TENTATIVAS_CONTINUA_PERMITIDO  SIM
ON_CONFLICT_STORAGE_PATH              QUEBRA   (de propósito, e é o ponto 5)
```

### W.8 · O número da próxima migration, medido

Não assumido. `026` é o maior no repositório, o maior no livro-razão do vivo, e
o maior em **todas** as branches remotas — varridas uma a uma com `git ls-tree`,
e não pela que estava à mão.

```
NEXT_MIGRATION_NUMBER = 027
```

### W.9 · O SINTONIA SCRAP não entra nisto

Medido no código: a rota social **não atravessa RAW**. `social_envelope.py`
declara `NOT_PRESERVED` e nomeia o dono forward; nenhum dos três ficheiros do
scrap escreve `raw_asset`. A fase 10 não lhe toca.

### W.10 · Veredicto

```
PHASE_10_LAW_MEASURED          = YES
UNPROVEN_TEM_CHAVE_MEDIDA      = YES   (K4)
UNPROVEN_TEM_CHAVE_NO_ESQUEMA  = NO
WRITER_BLOCKERS                = 6
READY_FOR_PHASE_10_IMPLEMENTATION = NO
READY_FOR_PHASE_10_LIVE           = NO
```

A lei existe e está medida. O escritor ainda não a sabe falar, e instalar um
esquema que o código não sabe servir seria trocar uma trava honesta por um
silêncio.

---

## X · C-CLOSE-PHASE-10-BLOCKERS — O RUNTIME APRENDE A LEI

A `C-PREP-PHASE-10` mediu a lei e parou em `READY_FOR_PHASE_10_IMPLEMENTATION = NO`,
por seis bloqueios que nenhum `alter table` cura. Esta missão fecha-os. Continua
sem tocar em produção:

    LIVE_DB_DDL = 0 · LIVE_DB_WRITES = 0 · LIVE_COLLECTION = 0 · LIVE_IMPORT = 0
    027_CREATED = NO · 027_LIVE = NO

### X.1 · O censo, refeito e fechado

Não se assumiu que eram seis. A varredura cobriu Python, SQL, YAML, heredocs,
shell, workflows, SQL gerado, testes e provas.

```
DEPENDENTES_DO_UNIQUE_STORAGE_PATH_TOTAL = 21 ficheiros
WRITERS_DEPENDENTES = 17     READERS_DEPENDENTES = 17   (sobrepõem-se)
FALSOS_POSITIVOS = 1         `pacote/ler_saida_leque.py` tem um `objeto_em`
                             que equilibra chavetas de JSON. Homónimo, e o
                             censo diz isso em vez de o contar.
OPERACIONAIS (fora de `tests/` e `provas/`) = 7
BLOCKERS_FOUND_TOTAL = 9     (os 6 da preparação + 3 novos)
```

Os sete operacionais, com espécie:

| ficheiro | escreve | lê | espécie |
|---|:-:|:-:|---|
| `guarda/preservar_coleta.py` | ✔ | ✔ | o escritor canónico |
| `guarda/portas_live.py` |  | ✔ | porta do banco vivo |
| `guarda/memoria_descartavel.py` | ✔ | ✔ | porta SQLite, só provas |
| `guarda/preservar_derivado.py` |  | ✔ | dono do derivado |
| `guarda/catalogo_importar.py` | ✔ | ✔ | GERA; `--aplicar` aposentado |
| `supabase/importacoes/ADAMA-ES-CATALOGO-…` | ✔ | ✔ | registo histórico, fora da cadeia |
| `supabase/migrations/025_…sql` |  | ✔ | a migration que separou as espécies |

Os três que a preparação não tinha visto:

1. **`guarda/portas_live.py`** — a porta de PRODUÇÃO tinha o mesmo
   `objeto_em(storage_path)` com `linhas[0]`. A preparação mediu as portas de
   prova e a de SQLite, e passou ao lado da que fala com o banco vivo.
2. **`planear()` colapsava observações em Python.** O dicionário do plano era
   indexado só pelo caminho: duas FONTES a observar o mesmo endereço davam UMA
   entrada, e a segunda era contada como «relação sem byte novo». A mesma
   doença do `unique`, mas em código — e portanto invisível a qualquer
   migration.
3. **O escritor carregava a trava física dentro de si.** `conferir_o_que_ja_existe`
   devolvia `NEW_RUN_SAME_STORAGE_PATH` como **conflito**, e conflito PARA a
   escrita. Com a fase 10 instalada, o escritor continuaria a recusar sozinho
   o caso que ela existe para abrir.

```
UMA TRAVA DO ESQUEMA NAO SE REESCREVE EM PYTHON.
QUEM SABE SE A LINHA CABE E O BANCO.
```

### X.2 · A porta do banco, partida em perguntas determinísticas

`objeto_em(storage_path)` **saiu**, e o nome já dizia o erro: prometia um
OBJETO e ia buscá-lo a `raw_asset`, que guarda OBSERVAÇÕES.

| pergunta | onde | determinística porque |
|---|---|---|
| `copia_em(endereço)` | `storage_object` | `unique (storage_object.storage_path)` — e a fase 10 não lhe toca |
| `observacao_identificada(run, fonte, doc, sha)` | `raw_asset` | índice parcial da fase 9 |
| `tentativa_sem_prova(run, fonte, objeto, sha)` | `raw_asset` | índice da fase 10 |
| `observacoes_em(endereço)` | `raw_asset` | devolve **lista**, sempre |

As três implementações — Supabase, Postgres de prova, SQLite — foram mudadas
juntas. Nenhuma delas voltou a escolher a primeira linha.

### X.3 · A chave do `FORWARD_IDENTITY_UNPROVEN`, agora fechada

A preparação aprovou `K2`/`K4`, ambas construídas sobre `storage_path`. A fase
11 retira essa coluna de `raw_asset` — uma chave assim nasceria com dívida
marcada. Entraram duas candidatas sobre o OBJETO, e dez cenários:

```
                                  S1 S2 S3 S4 S5 S6 S7 S9
K1 (run, fonte, sha256)            1  2  1! 1! 2  1  2  1    REPROVADA
K3 (fonte, sha256)                 1  1! 1! 1! 2  1  1! 1    REPROVADA
K2 (run, fonte, endereço)          1  2  2  2  2  1  2  1    passa, morre na fase 11
K4 (run, fonte, endereço, sha)     1  2  2  2  2  1  2  1    passa, morre na fase 11
K5 (run, fonte, objeto)            1  2  2  2  2  1  2  2!   REPROVADA
K6 (run, fonte, objeto, sha)       1  2  2  2  2  1  2  1    APROVADA
```

```
UNPROVEN_KEY_FINAL = (run_id, source_id, storage_object_id, sha256)
                     NULLS NOT DISTINCT
                     where identity_state = 'FORWARD_IDENTITY_UNPROVEN'
PHASE_11_COMPATIBLE = YES
```

`K5` reprova em `S9` e a razão é fina: uma observação **não preservada** não tem
cópia, e `storage_object_id` fica nulo. Em Postgres dois nulos são distintos num
índice único — a chave deixaria passar TODAS as tentativas não preservadas, em
silêncio. `NULLS NOT DISTINCT` não é afinação: é o que faz a chave existir para
essas linhas.

### X.4 · A identidade não se reescreve — sete campos, e a regra que os escolhe

```
IDENTITY_IMMUTABLE_FIELDS = identity_state · source_id · document_key ·
                            document_key_basis · run_id · sha256 ·
                            storage_object_id
```

A regra cabe numa frase: **a afirmação de identidade, mais tudo o que as duas
chaves de idempotência usam.** Nada mais, porque congelar por medo fecharia o
que tem de mudar.

E `storage_path` **não** está na lista. Essa ausência é a prova de coerência do
desenho: ele é ENDEREÇO, e um endereço muda sem que o facto mude — se estivesse
congelado, a fase 11 teria de o descongelar.

```
IDENTITY_REWRITE_CURRENTLY_POSSIBLE = YES   (medido: o UPDATE passava)
IDENTITY_REWRITE_AFTER_FIX          = NO    (9 transições, todas recusadas)
```

O que continua a poder mudar, e foi medido a poder: `attempts`,
`last_attempt_at`, `preserved`, `not_preserved_reason`, `source_url`,
`captured_at`, `storage_path`.

### X.5 · `attempts` e `last_attempt_at` ganham dono

```
ATTEMPTS_OWNER = guarda/preservar_coleta.py, e mais ninguem
```

O SQL do escritor passou a ser `update` **e depois** `insert ... where not
exists`. O `update` vem primeiro de propósito: se a observação já existe,
incrementa; se não existe, afeta zero linhas e o `insert` põe `attempts = 1`.
Duas ordens, uma semântica, e nenhuma condição em Python a decidir qual correr.

```
LER-SOMAR-ESCREVER EM PYTHON PERDERIA INCREMENTOS.
```

`attempts = coalesce(attempts,0) + 1` acontece DENTRO do banco, debaixo do lock
da linha: dois retries simultâneos serializam e os dois contam.

E `where not exists` — em vez de um segundo `on conflict` — porque ele funciona
**antes e depois** da fase 10. Não inventa trava nenhuma: quem arbitra a corrida
entre duas sessões continua a ser um índice, e há sempre um.

```
HOJE      unique (raw_asset.storage_path)
FASE 10   raw_identidade_forward_idx + raw_tentativa_sem_prova_idx
```

Em nenhum momento há zero travas — e é isso que permite ao escritor mudar
**antes** da migration.

### X.6 · O endereço deixa de ser fabricado a partir do conteúdo

`coleta/ingresso.py` tinha um `or` de quatro pernas cuja última era o próprio
`sha256`. Medido pelo código de produção, com dois ficheiros distintos de
conteúdo igual e o mesmo nome: **um endereço só**, e a segunda publicação nunca
chegava a existir.

A escada passou a ser, da prova mais forte para a mais fraca:

```
1. o identificador que a FONTE deu                `media/731`
2. a URL que esta casa PEDIU, sem o fragmento     `u<sha16 da url>`
3. o proprio conteudo                             `<sha16 dos bytes>`
```

Oito casos, todos medidos pelo código real: duas publicações com id nativo,
duas sem, a mesma repetida, querystring a distinguir documentos, só o fragmento
a diferir, sem id e sem URL, id nativo `NAO SEI`, e mesmos bytes em URLs
distintas. `8/8`.

A querystring **fica**: `?id=731` e `?id=6321` são dois documentos na mesma
fonte. Limpá-la não arrumaria nada — apagaria um facto.

O degrau 3 continua a colapsar, e de propósito: sem identificador e sem URL não
há **nenhuma** evidência de que sejam duas coisas.

```
STORAGE_ADDRESS_FALLBACK_BEFORE = sha16 do conteudo
STORAGE_ADDRESS_FALLBACK_AFTER  = id nativo > URL pedida > sha16
REAL_COLLISION_FIXED = YES
DOCUMENT_ID_FABRICATED = NO   — o degrau 2 e ENDERECO, e nunca `DOCUMENT_KEY`
```

### X.7 · Os escritores antigos: aposentados, não bloqueados

`OLD_WRITER_BUT_BLOCKED` não era um estado final. Cada um recebeu espécie.

| caminho | espécie | porquê |
|---|---|---|
| `guarda/preservar_coleta.py` | **o escritor canónico** | sabe falar identidade |
| `guarda/catalogo_importar.py --aplicar` | REMOVED | não há `SOURCE_ID` para dar |
| `supabase/importacoes/ADAMA-ES-CATALOGO-…sql` | ARCHIVED AS DEAD | sai da cadeia |
| `.github/workflows/supabase-raw-roundtrip.yml` | REMOVED | escrevia pré-026 |
| `.github/workflows/supabase-fichas-adama.yml` | REMOVED | escrevia pré-026 |
| `guarda/trava_do_escritor_antigo.sh` | REMOVED | sem porta para guardar |

A razão do importador não é de calendário e está no próprio código: **`adama-website`
é uma ORGANIZAÇÃO, não um código de fonte do atlas.** Sem `SOURCE_ID` real não há
estado forward possível para aquelas linhas, e nunca houve. Medido contra um
Postgres com a 026: o import falha na PRIMEIRA linha, em `identity_state` NOT
NULL, antes de haver conflito para o `on conflict` resolver.

E a trava teve de sair **com** ele. Dos três ficheiros da etapa `importacoes`,
nenhum dos outros dois toca `raw_asset`. Mantida, ela deixaria de proteger o que
quer que fosse e passaria a recusar TODA importação futura contra qualquer banco
pós-026 — ou seja, contra o único banco que existe.

```
UMA TRAVA QUE SO TRAVA O QUE E LEGITIMO NAO E UMA TRAVA.
ONE_OPERATIONAL_FORWARD_WRITER = YES
```

O teste que cobrava «cada caminho antigo chama a trava» foi virado do avesso:
agora cobra que eles **não existem**, e que o inventário de quem sequer menciona
`insert into raw_asset` está fechado em três ficheiros com espécie declarada —
um que ESCREVE, um que GERA, um que LÊ.

### X.8 · Os casos, medidos contra Postgres 16 descartável

`provas/a_lei_da_fase_10.py` — `A_LEI_DA_FASE_10_DB_TESTED = PASS`. Aplica
`001 + 022 + 025 + 026`, mede o mundo de hoje, **depois** aplica o protótipo e
mede o mundo de amanhã com o escritor a sério.

| caso | o que ficou provado |
|---|---|
| I1 | primeira observação: um objecto, uma observação, `attempts = 1` |
| I2 | retry da mesma corrida: **o mesmo `raw_asset.id`**, `attempts = 2` |
| I3 | corrida nova: observação nova, ids diferentes, **um só objecto** |
| I4 | conteúdo novo do mesmo documento: duas observações, dois objectos |
| I5 | publicações diferentes, mesmos bytes: não funde |
| I6 | fontes diferentes, mesmo conteúdo: não funde |
| I7 | retry sem prova: não duplica, e `attempts` sobe |
| I8 | sem prova em corrida nova: observação nova |
| I9 · I10 | duas sessões, mesma observação: uma linha, a segunda recusada |
| I11 | objecto órfão reutilizado, observação nasce a apontar-lhe |
| J1–J3 | morte a meio, retry, e metadados incompatíveis com nome próprio |
| K | derivação por conteúdo, e a conta da casa continua a fechar |

Montar `J3` ensinou mais do que ele mede: a primeira versão desligava a
observação da cópia para poder mexer no `sha256` dela, e **o gatilho recusou** —
`storage_object_id` é um dos sete campos congelados.

```
UMA OBSERVACAO NAO SE DESLIGA DA COPIA QUE ELA DIZ TER VISTO.
```

### X.9 · A derivação, dita em voz alta para ninguém a ler mal

```
DERIVED_IDENTITY = CONTENT_BASED
```

Duas observações dos mesmos bytes partilham o derivado, e o segundo `insert` é
recusado por `derivacao_e_unica_por_regua`. Isso está certo. Medido também que a
conta da casa é entre espécies comparáveis — **conteúdos** contra derivados, e
não observações contra derivados:

```
K_CONTEUDOS_UNICOS = 1   K_DERIVADOS_PRESENTES = 1   K_PERDA_POR_CONTEUDO = 0
K_A_CONTA_POR_OBSERVACAO_DARIA_PERDA_FALSA = 1
```

A última linha está lá de propósito: é a conta errada, escrita para que ninguém
a faça por engano.

### X.10 · Os leitores, com duas observações num objecto

`tests/test_leitores_depois_da_fase_10.py` monta a bancada que só existe depois
da fase 10 — um `storage_object`, duas `raw_asset` — e prova que nenhuma
pergunta responde «a primeira». Dez casos, incluindo o que cobra que
`objeto_em` não volta por outra porta.

### X.11 · Veredicto

```
BLOCKERS_FOUND_TOTAL  = 9
BLOCKERS_CLOSED_TOTAL = 9
BLOCKERS_OPEN_TOTAL   = 0

READY_FOR_PHASE_10_IMPLEMENTATION = YES
READY_FOR_PHASE_10_LIVE           = NO
027_CREATED = NO
```

O escritor sabe falar a lei. A migration que abre a porta é da missão seguinte.

---

## Y · C-IMPL-PHASE-10 — A LEI VIRA MIGRATION

A `C-PREP-PHASE-10` mediu a lei. A `C-CLOSE-PHASE-10-BLOCKERS` ensinou-a ao
runtime. Esta escreve-a em SQL versionado — e não a aplica em lado nenhum.

```
LIVE_DB_DDL = 0 · LIVE_DB_WRITES = 0 · LIVE_COLLECTION = 0 · LIVE_IMPORT = 0
PHASE10_LIVE = NO
```

### Y.0 · O estado, medido antes de escrever

```
CURRENT_BRANCH = claude/raw-observation-identity-3jbwco
INITIAL_HEAD   = ea9b0d8d578305d2b514fd42eb783edb6232cbf4   (== remoto, sem drift)
WORKTREE       = limpa, uma só
NEXT_MIGRATION_NUMBER      = 027   (maior em 104 branches remotas: 026)
LIVE_LAST_APPLIED_MIGRATION = 026  (auditoria 34548511070, MIGRATIONS_PENDENTES=nenhuma)
```

### Y.1 · O protótipo foi aposentado no mesmo movimento

`supabase/ensaios/PROTOTIPO-FASE-10-IDENTIDADE-DA-TENTATIVA.sql` existia porque
a fase 10 era lei sem migration. Com a `027` escrita passariam a existir **dois**
ficheiros a dizer a mesma lei.

```
UMA LEI EM DOIS SITIOS DIVERGE,
E A PARTIR DAI NENHUMA DAS DUAS VALE.
```

Saiu. `provas/a_lei_da_fase_10.py` deixou de aplicar o protótipo e passou a
aplicar a **migration a sério** — o que também torna aquela prova mais forte do
que era: ela mede agora o ficheiro que vai para produção.

### Y.2 · A migration

```
MIGRATION_FILE   = supabase/migrations/027_a_observacao_deixa_de_ser_o_endereco.sql
MIGRATION_SHA256 = 67c8fa932d66afad2852fb4a10e903267cb31638742a3abfad1f2cb855ac9163
```

Três movimentos, uma transacção:

| fase | o quê | porquê |
|---|---|---|
| 10a | `drop constraint raw_asset_storage_path_key` | o endereço deixa de ser identidade da observação |
| 10b | `raw_tentativa_sem_prova_idx`, parcial, `nulls not distinct` | sem isto, 10a abriria um buraco em vez de uma porta |
| 10c | gatilho que congela sete campos | a afirmação de identidade não se reescreve |

E o que ela **não** faz: retirar a coluna `storage_path`. Isso é a fase 11, e a
chave de 10b foi escolhida sobre `storage_object_id` exactamente para que essa
fase não tenha de a desfazer.

### Y.3 · A passagem, e não só a lei

`provas/a_fase_10_entra_no_acervo.py` — `A_FASE_10_ENTRA_NO_ACERVO = PASS`.

A fixture tem a **forma** do vivo: 252 observações legadas, `id` esparsos até
757, corte da fase 8 instalado, 252 cópias ligadas uma a uma, um derivado com
chave estrangeira composta, e o livro-razão já a registar `001`–`026`. O
aplicador vê o que veria em produção: **uma** migration pendente.

```
AS_ANTERIORES_FORAM_SALTADAS_COM_HASH_A_BATER = 25
A_027_FOI_APLICADA          = MIGRATION_027=PASS
NENHUMA_OUTRA_FOI_APLICADA  = 1
NENHUMA_FOI_PULADA          = 26
LEDGER_TEM_A_027            = APLICADA
LEDGER_GUARDOU_O_SHA        = 67c8fa93…  (igual ao do ficheiro)
```

E as catorze medidas do acervo, ANTES e DEPOIS, todas idênticas: contagens,
`md5` do conjunto de ids, `md5` do conjunto de shas, `md5` dos caminhos, `md5`
das ligações observação→cópia, legado, forward, derivados e as ligações deles,
órfãos e divergentes.

```
MIGRATION SO PROVADA EM BANCO NOVO E MIGRATION POR PROVAR.
```

### Y.4 · A falha a meio

Uma cópia da `027` com um erro deliberado no fim, pela **mesma cadeia**, numa
raiz temporária — porque pôr um ficheiro estragado na pasta a sério seria
encenar a falha no sítio onde ela não pode acontecer.

```
A_CADEIA_REPROVOU                      = SIM · MIGRATION_027=FAIL
PARTIAL_PHASE10_AFTER_FAILED_MIGRATION = 0
O_UNIQUE_DO_ENDERECO_CONTINUA_LA       = 1
O_LIVRO_RAZAO_NAO_REGISTOU_A_027       = 0
A_027_BOA_ENTRA_A_SEGUIR_SEM_LIMPEZA   = MIGRATION_027=PASS
```

### Y.5 · A janela da transição

O ponto crítico não é o esquema novo nem o writer novo — é o **intervalo** entre
os dois. Medido nos dois sentidos:

| | esquema velho | esquema novo |
|---|---|---|
| **writer novo** | `E1` · a 2ª corrida não entra, `PARTIAL`, `NEW_RUN_SAME_STORAGE_PATH`, erro do banco guardado | `E3`/`E4` · entra, 1 objecto, 2 ids; o retry não duplica e conta a tentativa |
| **writer antigo** | (era o mundo de antes) | `E2` · falha ALTO, e a **planear**: `no unique or exclusion constraint` |

Não há quadrante em que a escrita não aconteça e ninguém saiba.

```
SILENCIO INCORRECTO E O UNICO RESULTADO INACEITAVEL.
```

Mais: `E5` a tentativa sem cópia continua travada (`storage_object_id` nulo dos
dois lados), `E6` dois documentos com o mesmo `sha256` continuam dois,
`E7`/`E8` duas sessões simultâneas nas duas famílias dão uma linha e uma recusa.

### Y.6 · Imutabilidade, no banco já migrado

```
IDENTITY_MUTATIONS_REJECTED   = 10/10
OPERATIONAL_MUTATIONS_ALLOWED = 6/6
```

Entre as dez recusadas está `desligar storage_object_id`, que não é óbvia: uma
observação não se desliga da cópia que ela diz ter visto. Entre as seis
permitidas está `storage_path`, e essa ausência da lista de congelados é a prova
de coerência do desenho — a fase 11 não vai ter de descongelar nada.

### Y.7 · O ratchet que faltava

O caso `test_unique_com_coluna_nulavel_usa_nulls_not_distinct` varria blocos
`create table`. A fase 10 não trouxe uma coluna — trouxe um `create unique
index`, e a lei era a mesma.

```
UMA LEI QUE SO SE COBRA NUM DOS SITIOS ONDE ELA VALE
E UMA LEI COM UM BURACO DO TAMANHO DO OUTRO SITIO.
```

O caso novo varre os índices. Ele encontrou **três** casos antigos, e dois deles
são legítimos por razões diferentes: dois índices de `origem` cujo predicado já
exclui o NULL (derivável, tratado em código), e o índice forward da `026`, cuja
não-nulidade vem de duas travas noutra migration (não derivável, e por isso uma
isenção **nomeada**). E há um caso que confere que essas duas travas continuam
a existir — uma isenção cuja justificação some deixa de valer.

Os dois ratchets foram testados por mutação: tirar `nulls not distinct` da `027`
reprova; construir a chave sobre `storage_path` reprova.

### Y.8 · Veredicto

```
READY_FOR_PHASE_10_LIVE = YES
```

Significa exactamente uma coisa: **a migration está pronta para ser aplicada**.
Não foi. O livro-razão do banco canónico continua a terminar na `026`, e a
próxima auditoria vai passar a dizer `MIGRATIONS_PENDENTES= 027` — que é a
frase certa para o estado certo.

A aplicação é a `C-LIVE-PHASE-10`, com autorização própria.

---

## Z · C-LIVE-PHASE-10 — A FASE 10 ENTROU NO BANCO VIVO

Aplicada ao banco canónico pelo aplicador da casa, por `workflow_dispatch` de
`supabase-migrate.yml` em `claude/raw-observation-identity-3jbwco` @ `57780b8a`,
com `importar=false`. Run **`34550502265`**.

```
MIGRATION_FILE   027_a_observacao_deixa_de_ser_o_endereco.sql
MIGRATION_SHA256 67c8fa932d66afad2852fb4a10e903267cb31638742a3abfad1f2cb855ac9163
```

### Z.1 · O pré-voo, e o alvo confirmado por derivação

```
DB_CONNECTION=PASS
TABLES_IN_PUBLIC=68
SAME_PROJECT_CONFIRMED=YES
ESTADO_ACEITO=68 tabelas, nenhuma fora do que o Git cria
TABELAS_DECLARADAS_NAS_MIGRATIONS=68
```

`SAME_PROJECT_CONFIRMED` não é uma afirmação: o workflow deriva o `ref` do
projeto das DUAS variáveis — `SUPABASE_URL` e `SUPABASE_DB_URL` — e exige que
coincidam. Escrever no banco errado exigiria que os dois segredos estivessem
errados do mesmo modo.

### Z.2 · O estado congelado ANTES (auditoria `34550386346`)

```
RAW_ASSET_COUNT=252          STORAGE_OBJECT_COUNT=252
LEGACY_ROWS=252              FORWARD_IDENTIFIED=0   FORWARD_UNPROVEN=0
RAW_ASSET_MIN_ID=1           RAW_ASSET_MAX_ID=890
RAW_ASSET_ID_SET_MD5=bf54cf470e59a3c512e017a967cd86ce
LINKED_RAW_ASSETS=252        PRESERVED_WITHOUT_OBJECT=0
RAW_STORAGE_PATH_MISMATCHES=0  RAW_STORAGE_SHA_MISMATCHES=0
OBJETOS_SEM_OBSERVACAO=0     derived_artifact=1 (raw_asset_id=890)
LEGACY_CUTOFF_VALUE=890      FORWARD_IDEMPOTENCY_INDEX_VALID=1
unique(raw_asset.storage_path) = PRESENTE
025=APLICADA  026=APLICADA  027=ausente   MIGRATIONS_PENDENTES= 027
```

Idêntico ao baseline conhecido, incluindo o `md5` do conjunto de ids.

### Z.3 · A aplicação

```
MIGRATION_001..026 = SKIP (ja no livro-razao) HASH=MATCH
MIGRATION_027      = PASS
POST_APPLY_VERIFICATION (008) = PASS
passos de importacao = skipped
```

Vinte e seis migrations vistas, uma aplicada, nenhuma pulada. Quarenta e dois
segundos.

E o inventário medido do banco real diz a mesma coisa por outro caminho:

```
PUBLIC_TABLE_COUNT=68     (68 antes)
CHECK_CONSTRAINTS=135     (135 antes — a 027 nao traz CHECK nenhum)
UNIQUE_INDEXES=137        (137 antes — sai um unique, entra um indice)
ROWS_TOTAL=2208
```

`UNIQUE_INDEXES` não mudar é a confirmação independente de que a `027` fez
exactamente duas coisas com índices: tirou `raw_asset_storage_path_key` e pôs
`raw_tentativa_sem_prova_idx`. Menos um, mais um.

### Z.4 · A sentinela da fase 10 virou-se ao contrário

A auditoria dizia, desde a `C-LIVE-025`:

> ⚠️ SENTINELA DA FASE 10. Enquanto ela nao for resolvida, esta trava fica — e
> se um dia desaparecer sem missao que o declare, a auditoria grita.

A `027` é a missão que o declarou. A sentinela **não se apaga** — inverte-se.

```
UMA SENTINELA APAGADA NAO GUARDA NADA.
UMA SENTINELA INVERTIDA GUARDA O LADO NOVO.
```

A partir daqui o que a auditoria grita é a trava **voltar**. E nasce a sentinela
seguinte, no mesmo sítio e pela mesma razão: a COLUNA `storage_path` fica, e se
desaparecer sem missão que o declare, a auditoria grita — essa é a fase 11.

### Z.5 · O contrato da 027, agora cobrado pela auditoria

A secção `G` é nova e não imprime: reprova.

```
UNPROVEN_INDEX_VALID              o indice da tentativa existe e e valido
UNPROVEN_NULLS_NOT_DISTINCT       dois nulos contam como iguais
UNPROVEN_SOBRE_O_OBJETO           fala de storage_object_id, e nao do endereco
IDENTITY_IMMUTABILITY_TRIGGER     a identidade nao se reescreve
COLUNA_STORAGE_PATH_AINDA_EXISTE  a fase 11 e que a retira
```

A terceira é a que menos se espera num auditor e a que mais importa: ela cobra
que a chave **não** foi construída sobre o endereço. Uma chave assim passaria
hoje e teria de ser desfeita na fase 11.
