# O ARMAZÉM ITALIANO EXISTE — E NÃO TEM LIVRO DE ENTRADA

**Reconciliação READ-ONLY** · 2026-09-08 · ramo `claude/italia-biblia-integracao-v1`

> **Nada foi escrito, enviado, apagado ou migrado.** Zero `INSERT`/`UPDATE`/`DELETE`, zero
> upload, zero DDL, zero migration aplicada, zero byte movido, **zero corrida retrocriada**.

---

## A FRASE QUE DEIXOU DE SER VERDADE

Até ontem dizíamos: *«a Itália não está no Supabase»*. **Está errado.** A frase certa é mais
desconfortável e muito mais útil:

```
OS BYTES ITALIANOS ESTÃO NO ARMAZÉM.        195 objetos · 80,7 MB
A MEMÓRIA OPERACIONAL DELES NÃO EXISTE.     raw_asset IT = 0 · collection_run IT = 0
```

> **Um armazém cheio, com o livro de entrada em branco.** As caixas estão lá. Ninguém, olhando
> só para o banco, consegue dizer de onde vieram, quem as trouxe, nem quando.

---

## A · A BASE DE PROVA — quem mediu o quê

| o quê | quem mediu | estado |
|---|---|---|
| Storage `IT/`, `raw_asset`, `collection_run` (as **linhas**) | **coordenador**, no banco LIVE | `EXTERNAL_LIVE_MEASUREMENT` |
| o manifesto de 141 documentos, os 49 PDFs, o schema, os escritores | **esta sessão**, no repositório | `MEASURED_HERE` — corre outra vez e dá o mesmo |

**Esta sessão não tem credencial do banco.** Medido: `0` variáveis de ambiente do Supabase,
nenhum ficheiro `.env`. Por isso a leitura do coordenador ficou registada em
[`SUPABASE-LIVE-MEDICAO-EXTERNA.json`](../../data/samples/SUPABASE-LIVE-MEDICAO-EXTERNA.json)
com o nome de quem mediu ao lado — e **não** como `OBSERVED`.

> **Recado de terceiro pode estar certo e continuar não sendo prova nossa.** Chamar isto de
> `OBSERVED` faria o mapa dizer que esta casa foi lá e viu. Não foi.

`LIVE_STATE = PARTIAL`.

---

## B · OS 195 OBJETOS

| prefixo | objetos |
|---|---:|
| `IT/adama-website/DOCUMENT` | 139 |
| `IT/adama-website/PRODUCT_DOM` | 51 |
| `IT/adama-website/CAPTURE` | 3 |
| `IT/adama-website/MANIFEST` | 2 |
| **total** | **195** · 80.714.570 bytes |

⚠️ **`IT/` é prefixo de objeto, não pasta.** O Storage não tem diretórios: a barra faz parte
do nome da chave. O mapa pode desenhá-lo como uma gaveta; a semântica continua sendo outra.

### E a chave italiana não segue a convenção da casa

```
ES (documentada)   ES/adama-website/<RUN_ID>/<sha16>-<nome>.pdf
IT (medida)        IT/adama-website/<TIPO>/…
```

**A terceira posição da chave espanhola é a corrida. Na italiana é o tipo do documento.** A
corrida não aparece em lado nenhum da chave — e uma chave que não carrega a corrida não
consegue reconstruir sozinha quem a escreveu.

---

## C · QUEM PÔS OS 195 LÁ

A cadeia real tem **dois passos**, e ninguém obriga os dois a andarem juntos:

```
1 · o operador envia os bytes     scripts/storage_preservar.py --enviar    → Storage
2 · o gerador escreve a memória   guarda/catalogo_importar.py              → raw_asset
```

| | passo 1 | passo 2 |
|---|---|---|
| **onde vive** | **FORA deste repositório** — a máquina do operador | aqui |
| **prova** | `INTEGRACAO-CATALOGO-ADAMA-ES.md:69` lista-o como **NÃO INTEGRADO**; `tests/es/test_adama_es_gate.py:366` reprova se ele aparecer aqui | está no Git |
| **correu para a Itália?** | **SIM** — é o que explica os 195 | **NÃO** |

**O passo 2 está preso à Espanha pela própria escrita do ficheiro.** Medido: as entradas de
`guarda/catalogo_importar.py` são `ADAMA-ES-PRODUCT-INTELLIGENCE.json`,
`ADAMA-ES-PRESERVACAO-*.json`, e a saída é `ADAMA-ES-CATALOGO-2026-08-30.sql`. **Não existe
equivalente italiano em lado nenhum.**

### E a Itália TEM SQL de importação — que nunca fala do bruto

```
supabase/importacoes/IT-CAMADAS-2026-09-02.sql     0 menções a raw_asset / collection_run
supabase/importacoes/IT-LASTMILE-2026-09-02.sql    0 menções a raw_asset / collection_run
```

A Itália importou **camadas analíticas** e **nunca importou a procedência**. Não é que
faltasse importador: é que o importador que existe olha para outro andar do prédio.

---

## D · POR QUE `raw_asset` FICOU VAZIO — a classificação

> ## `STORAGE_ONLY_PIPELINE`

| hipótese | veredito |
|---|---|
| `LEGACY_BEFORE_RAW_ASSET_OWNER` | **NÃO** — `raw_asset` existe desde a migration `001`; os objetos foram capturados em 30/08/2026 |
| `FAILED_METADATA_WRITE` | **NÃO há prova de tentativa** — não existe ficheiro de importação italiano do bruto para ter falhado |
| `INTENTIONAL_NOT_REGISTERED` | **NÃO** — não há decisão escrita em lado nenhum. **Ausência de decisão não é decisão** |
| `UNKNOWN` | não é preciso: os dois passos estão identificados e um deles nunca foi escrito para a Itália |

⚠️ **A ressalva honesta.** O passo 1 vive noutra máquina e esta sessão **não o consegue ler**.
Logo, não se pode *provar* que ele não tentou escrever `raw_asset` e falhou. O que se prova é
o lado de cá: **aqui não há escritor italiano do bruto, e nunca houve.**

---

## E · A PROCEDÊNCIA PERDEU-SE?

> ## NÃO. Ela não está no banco — está no Git.

`research/adama-italy-product-intelligence-deep/LABEL-MANIFEST.json`, versionado:

```
141 documentos declarados
141 com procedência completa    SHA256 · BYTES · CAPTURED_AT · SOURCE_URL · SOURCE_ID
138 conteúdos únicos            (3 registos partilham bytes com outro)
 77.146.360 bytes declarados
 capturados entre 30/08/2026 19:18:30Z e 19:21:36Z — três minutos
```

Por tipo: 51 `SCHEDA_DI_SICUREZZA` · 51 `ETICHETTA` · 23 `BROCHURE` · 13 `COMUNICAZIONE` ·
2 `ESTENSIONE_USO` · 1 `LEAFLET`. E os **51 `PRODUCT_DOM`** do armazém batem exatamente com
os **51 produtos comerciais** do `BUILD-SUMMARY.json`.

### Mas a CORRIDA não é recuperável

```
RUN_ID no manifesto:  NENHUM.  Medido: a palavra não aparece em nenhum ficheiro do build.
```

**`RUN_NOT_PROVABLE`.** A procedência que existe é a **do documento** (quando, de que URL,
que bytes). A **da corrida** — quem a lançou, com que versão, quanto custou, se terminou —
nunca foi escrita.

> ### PROCEDÊNCIA RECUPERÁVEL NÃO É PROCEDÊNCIA INVENTADA.
> Inserir hoje uma `collection_run` histórica seria escrever no livro de história um dia que
> ninguém viveu. **Não foi feito, e não deve ser feito sem decisão própria.**

---

## F · AS TRÊS CONTAGENS — ✅ FECHADAS EM 08/09/2026

```
141   registos no manifesto      uma linha por (produto, documento)
138   conteúdos                  bytes diferentes
139   objetos no armazém         cópias guardadas
```

Ontem isto ficou em `NÃO_RECONCILIADO`, à espera das chaves. Elas chegaram pela metade — as
contagens de identidade e as duas chaves do único duplicado — e bastaram, porque **a
explicação estava do lado de cá o tempo todo**, no `SOURCE_URL` de cada registo:

```
141 − 138 = 3     três documentos servem a DOIS produtos cada um
139 − 138 = 1     um conteúdo foi PUBLICADO EM DUAS URLs
```

**As duas diferenças têm causas diferentes.** Era isso que faltava dizer.

| conteúdo | registos | URLs | objetos | por quê |
|---|---:|---:|---:|---|
| `227779fdd6be…` | 2 | **2** | **2** | a ADAMA publicou o mesmo PDF em `media/731` (Davai®) **e** `media/6321` (FullPage®). Duas publicações, dois objetos, um conteúdo |
| `308764028a95…` | 2 | 1 | 1 | Highcard® e Max-Ace® apontam para a **mesma** `media/6121` — relação lógica, não byte novo |
| `ef688c782159…` | 2 | 1 | 1 | os mesmos dois produtos, a **mesma** `media/6026` |

```
OBJETOS PREVISTOS PELO MANIFESTO   139
OBJETOS MEDIDOS NO ARMAZÉM         139      ✅ batem
CONTEÚDOS NO MANIFESTO             138
CONTEÚDOS NO ARMAZÉM               138      ✅ batem
BYTE PERDIDO                       NENHUM
```

⚠️ **`FORÇA_DA_PROVA = PREFIX_MATCH`, e não `FULL_SHA256_MATCH`.** A chave carrega 16
caracteres do hash — isso é **endereço, não identidade**. Fechar como igualdade completa
exigiria ler os 139 objetos de volta e bater o `sha256` inteiro, e esta sessão não tem
credencial para isso. `ETag` igual e tamanho igual reforçam; sozinhos não provam.

`ESTADO = RECONCILIADO_POR_PREFIXO`.

---

## G · OS 49 PDFs DO GOLDEN PATH — dois acervos, não um

Comparado por **impressão digital**, nunca por nome de ficheiro:

```
GOLDEN_PATH_CONTENTS      43
ALREADY_IN_STORAGE         0
NOT_IN_STORAGE            43
UNKNOWN                    0
```

**Zero.** São universos completamente separados:

| | armazém | Golden Path |
|---|---|---|
| **o quê** | catálogo comercial da ADAMA Itália — fichas de segurança, etiquetas, brochuras | boletins fitossanitários regionais — ARPAV, Campania, olivo |
| **fonte** | `adama.com/italia` | sítios das regiões |
| **conteúdos** | 138 | 43 |

`UNKNOWN = 0` porque a comparação é completa dos dois lados: todo conteúdo do Golden Path tem
`sha256` calculado do disco, e todo documento do manifesto declara o seu.

⚠️ **Ressalva:** isto compara com o **manifesto** do armazém, não com a **lista de chaves** do
armazém. Se um objeto lá foi parar sem passar pelo manifesto, este censo não o vê.

---

## H · O QUE NÃO MUDA NA DECISÃO DE ONTEM

| pergunta | resposta | mudou? |
|---|---|---|
| precisa de tabela de ocorrência? | **NÃO** | não mudou — `sha256` continua não sendo `UNIQUE` |
| `derived_artifact` continua sendo a única mudança de esquema? | **SIM** | não mudou |

**Nada do que se mediu hoje toca no modelo de identidade.** O que se descobriu não é uma
lacuna de *esquema* — é uma lacuna de **caminho de escrita**. As colunas existem; ninguém as
preenche para a Itália.

### Terminologia, precisada

Uma linha de `raw_asset` representa melhor um **`PRESERVED RAW OBJECT`** do que um `CONTENT`:
ela é *um objeto guardado, com a captura que o trouxe anotada ao lado*. O `sha256` é
**atributo** dela, não a sua identidade — e por isso pode repetir-se entre linhas.

E `conteudo_visto_em` continua a resolver observações de `conteudo` (item de canal). **Não
forçar PDF bruto para dentro de `conteudo`:** `RAW BYTE CONTENT` e `CONTENT ENTITY` são
espécies diferentes, e fundi-las obrigaria a inventar um canal que não existe.

---

## I · O CAMINHO DE ESCRITA DESEJADO — e o que falta nele hoje

```
COLETOR / EXECUTOR
      ↓
RUN                  collection_run        ← existe · Itália nunca escreveu
      ↓
BYTES BRUTOS
      ↓
STORAGE              bucket raw            ← existe · Itália JÁ escreveu (195)
      ↓
RAW_ASSET METADATA   raw_asset             ← existe · Itália nunca escreveu   ⛔ O CORTE
      ↓
DERIVAÇÃO
      ↓
DERIVED_ARTIFACT     —                     ← NÃO EXISTE (G-39, projetado)
      ↓
ADMISSÃO             admissao/admissao.py  ← existe, e já corre
```

**O corte é entre o Storage e o `raw_asset`.** É o único ponto da cadeia onde o degrau
existe e ninguém sobe nele.

### Atomicidade — a pergunta que este caso responde sozinho

*O que acontece se o envio passa e o `INSERT` falha?*

**Acontece exatamente o que está a acontecer agora:** bytes preservados, memória em branco, e
ninguém a saber, porque nada reconcilia os dois lados. Não é hipótese — é o estado medido.

O que falta é um estado que saiba dizer isso em vez de ficar calado. Algo como
`UPLOAD_PENDING_METADATA`, com uma conta de reconciliação por corrida:

```
PRESERVED_OBJECTS  =  RAW_ASSET_ROWS      (por corrida, quando 1:1 for mesmo a lei)
```

⚠️ **Não congelar esta regra sem medir.** Nas chaves italianas de hoje a relação nem sequer
é conhecida — 141/138/139 já mostram que 1:1 não é evidente. **Nada disto foi implementado
nesta missão.**

---

## J · O GAP — um só, em duas dimensões

> ## `G-42 · ITALY_STORAGE_METADATA_RECONCILIATION`

**Um gap, não cinco tickets** — e ele tem duas metades que não se separam:

| dimensão | estado |
|---|---|
| **HISTÓRICO** · os 195 objetos existentes sem memória operacional | **ABERTO, e assim fica.** Classe de dívida: `HISTORICAL_STORAGE_WITHOUT_OPERATIONAL_RUN`. Preservados, com procedência documental recuperável e `RUN` `NOT_PROVABLE`. **Sem corrida inventada.** |
| **GARANTIA FORWARD** · nenhum objeto NOVO pode repetir isto em silêncio | **FECHADO em código e teste.** `guarda/preservar_coleta.py` + 19 provas. Ainda **não** em produção |

### A classe de dívida do histórico, escrita com todas as letras

```
HISTORICAL_STORAGE_WITHOUT_OPERATIONAL_RUN

  bytes                 PRESERVADOS         195 objetos, 80,7 MB
  procedência do doc    RECUPERÁVEL         141 de 141, no Git
  procedência da RUN    NOT_PROVABLE        nenhum registo declara run_id
  o que se faz          NADA, por agora     e sobretudo: não se inventa
```

> **A migration `001` declara que proveniência é PROSPECTIVA.** Criar hoje uma
> `collection_run` para eles — `LEGACY-IT`, `UNKNOWN-RUN`, `BACKFILL-RUN` — seria fabricar
> história. E **relaxar o `run_id NOT NULL` só para caber o legado** seria pior ainda: cederia
> a lei para acomodar a exceção, e a partir daí toda coleta nova poderia entrar sem corrida.

---

## J2 · A GARANTIA FORWARD — o dono canônico da escrita

`guarda/preservar_coleta.py`. Não conserta o passado; impede o futuro de o repetir.

### Por que em `guarda/`, e por que não um dono novo

Censo dos escritores atuais — **cinco, e nenhum é dono do par**:

| quem | escreve | escopo |
|---|---|---|
| `supabase-fichas-adama.yml` | Storage **+** `raw_asset` | fichas MAPA |
| `supabase-raw-roundtrip.yml` | Storage **+** `raw_asset` | prova de round-trip |
| `guarda/catalogo_importar.py` | SQL de `raw_asset` | **só ES** |
| `coleta/regulatorio_importar.py` | SQL de `collection_run` | regulatório |
| `coleta/ropf_pre_requisito.py` | SQL de `collection_run` | ROPF |

**Reusar antes de criar, aplicado:** o padrão da casa já estava provado em
`guarda/catalogo_importar.py` — *gerar SQL auditável em vez de falar com o banco*, porque
**o primeiro a olhar não pode ser a produção**. O novo dono segue esse padrão exatamente, e
passa no portão da casa (`guarda/sql_conferir.py`), apóstrofes italianas incluídas.

**Não se criou dono novo por reflexo:** nenhum dos cinco podia assumir a responsabilidade —
dois são workflows presos a uma rota, três geram SQL de um único país ou entidade.

### A doutrina

```
EXECUTOR         produz o artefato.  NÃO conhece banco.
DONO CANÔNICO    persiste o PAR: byte + memória.
```

Nenhum executor deve gravar no banco só porque conhece a `SUPABASE_URL`. Foi assim que a
Espanha acabou com cinco escritores e a Itália com zero.

### O fecho, com seis condições medidas

```
PLANEAR → ENVIAR → CONFERIR → MEMÓRIA → RECONCILIAR → FECHAR
```

`COMPLETE` exige: `plano_feito` · `bytes_no_armazem` · `bytes_conferidos` ·
`nenhum_envio_falhado` · **`memoria_escrita`** · **`reconciliacao_bate`**. As duas últimas
são novas em relação ao fecho da estrada do PDF — e são exatamente as que a Itália não teve.

**A conta é entre espécies comparáveis:**
`OBJETOS_ESPERADOS == OBJETOS_CONFERIDOS == LINHAS_DE_MEMÓRIA`. Nunca «141 registos = 139
objetos» — são espécies diferentes e a igualdade seria falsa.

### Atomicidade — e por que não se apaga o byte

Armazém e Postgres não são uma transação só. Se o envio passar e a memória falhar:

```
RUN_STATE   PARTIAL
FALTOU      ["memoria_escrita", "reconciliacao_bate"]
PENDÊNCIA   UPLOAD_PENDING_METADATA
BYTES       ficam onde estão
```

> **Nunca `COMPLETE`.** E o byte **não** é apagado para fingir atomicidade — não existe
> caminho no código para isso. `Armazem` tem três métodos, e nenhum é «remover». Apagar o
> bruto preservado destruiria a única evidência que sobrou de uma falha.

**Estado novo no banco: nenhum.** O enum de `001` já tem `parcial`, e a pendência mora no
manifesto da corrida, do lado do Git. Menos esquema, mesma verdade.

### Retry idempotente

Repetir a chamada faz **só o que falta**: o objeto já lá está, `existe()` decide, e nenhum
byte volta a subir. O `INSERT` traz `on conflict (storage_path) do nothing` — não duplica
linha nem inventa `captured_at` novo. Provado nos casos H e N.

### Provado sem produção

19 testes em `tests/test_preservar_coleta.py`, com armazém de mentira: **sem banco, sem rede,
sem instalar nada**. Cobrem A–N, incluindo as duas mortes do processo e a recuperação.

---

## K · `derived_artifact` — continua sendo a única lacuna de esquema

**SIM.** Nada do que se mediu hoje mudou isso, e uma coisa reforçou:

A pendência `UPLOAD_PENDING_METADATA` **não pediu coluna nem enum novo** — mora no manifesto
da corrida e mapeia para o `parcial` que a `001` já tem. Era o candidato mais provável a
virar uma sexta alteração de esquema, e não virou.

Continua faltando **uma** tabela, para a etapa de **derivação**: os 43 textos de PDF, com
`parent_sha256`, tipo, ator e versão. SQL projetado em
[`IDENTIDADE-DO-ARTEFATO.md`](IDENTIDADE-DO-ARTEFATO.md) §F. **Não aplicado, aqui nem em
lado nenhum.**

---

## L · O GOLDEN PATH, DEPOIS DESTA MISSÃO

Os 43 **não** foram migrados, e não devem ser até a decisão do enum de custo e um teste da
`022` num Postgres descartável. O que esta missão prova é que a próxima execução **poderia**
correr pelo caminho certo:

```
NOVA CORRIDA → planear → armazém → conferir → memória → reconciliar → COMPLETE
```

⚠️ **E a cardinalidade não é 43 por decreto.** O plano é calculado dos artefatos que
entrarem: registos, conteúdos e objetos são três contagens diferentes, e o armazém italiano
acabou de mostrar por quê. Fixar «43 objetos» na arquitetura repetiria o erro de escrever no
código um número que só era verdade num dia.

## M · A PRÓXIMA AÇÃO SEGURA

1. **Ler os bytes de volta do armazém** e bater o `sha256` inteiro — sobe a prova de
   `PREFIX_MATCH` para `FULL_SHA256_MATCH`. Precisa de credencial.
2. Decidir se um *backfill verificável* dos 141 documentos é aceitável — **e a corrida
   continua `NOT_PROVABLE`**, o que precisa de resposta própria e não se resolve por conforto.
3. Testar a `022` (`derived_artifact`) num Postgres local e descartável.
4. Decidir `ROTA_GRATUITA_PROVADA` no enum de `cost_method`.

**Nenhuma delas foi feita hoje. Hoje era fechar a conta e fechar a porta da frente.**
