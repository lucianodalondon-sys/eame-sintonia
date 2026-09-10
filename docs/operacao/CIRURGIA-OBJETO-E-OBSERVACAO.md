# A CIRURGIA QUE SEPARA O OBJETO DA OBSERVAÇÃO

**C-PLAN-B5** · decisão, zero DDL · ramo `claude/raw-observation-identity-3jbwco`
· HEAD `a86e667d`

> Nenhuma migration foi criada. Zero DDL, zero alteração de runtime, de teste, do System
> Map ou da Bíblia. Zero rede, zero escrita em banco ou em armazém. Tudo abaixo saiu do
> schema versionado, do código versionado e de duas medições que já viviam no repositório.

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

## M · O DADO EXISTENTE, E O QUE FALTA MEDIR

```
VERSIONED   138 inserts de `raw_asset` em supabase/importacoes/ADAMA-ES-CATALOGO-2026-08-30.sql
            1 corrida · 138 sha256 distintos · ZERO casos de mesmos bytes na mesma corrida

LIVE        251 linhas em `raw_asset`, 8 em `collection_run`, 0 em `conteudo`
            medido pelo COORDENADOR em 2026-09-08 · EXTERNAL_LIVE_MEASUREMENT
            252 depois do canário forward · esse bloco é OBSERVED
```

```
LIVE_RAW_ASSET_ROWS = 252 em 2026-09-08 (recado de terceiro + um canário nosso)
                    = NÃO SEI hoje
```

Recado de terceiro pode estar certo e continuar não sendo prova nossa. Esta sessão não tem
credencial e não reproduziu a leitura.

```
LIVE_READONLY_CENSUS_REQUIRED_BEFORE_MIGRATION = YES
```

**Uma leitura, uma instrução, zero escrita:**

```sql
select count(*)                                                        as total,
       count(*) filter (where not preserved)                           as nao_preservados,
       count(*) filter (where sha256 !~ '^[0-9a-f]{64}$')              as sha_fora_de_formato,
       count(*) filter (where storage_path is null or storage_path = '') as sem_caminho,
       count(distinct storage_path)                                    as caminhos_distintos
  from public.raw_asset;
```

É ela que decide se as fases 2, 4 e 5 correm sem rebentar. `raw_asset.sha256` **não tem
check de formato** — `derived_artifact` tem, `raw_asset` não — e a trava condicional da
fase 5 reprova sobre qualquer linha com `preserved = true` e caminho vazio. Nenhuma dessas
duas coisas se sabe daqui.

```
ESCREVER DDL SOBRE UM BANCO QUE NUNCA SE LEU
NÃO É CORAGEM. É ESCREVER À NOITE, DE OLHOS FECHADOS.
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

## O · A AUTORIZAÇÃO

```
READY_FOR_B5_SCHEMA_IMPLEMENTATION = NO
```

Está fechado, sem adivinhação: tabelas alvo, grãos, chaves, preservação do
`raw_asset.id`, comportamento do derivado, política de legado, estratégia de `source_id`,
ordem da migration, primeira operação não aditiva, rollback, transição do writer e
compatibilidade com o B4.

Falta **uma** coisa, e é uma leitura:

```
NEXT = correr a instrução SELECT da secção M contra o Supabase LIVE, em modo
       leitura, e registar o resultado ao lado de quem o mediu.
```

Enquanto ela não existir, a implementação pára antes do DDL. Não porque o desenho esteja
incompleto — porque o banco onde ele vai correr nunca foi lido por esta casa.

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
