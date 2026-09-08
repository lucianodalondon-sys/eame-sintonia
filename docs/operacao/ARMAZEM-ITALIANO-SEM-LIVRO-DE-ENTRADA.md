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

## F · AS TRÊS CONTAGENS QUE NÃO BATEM

```
141   documentos no manifesto
138   conteúdos únicos no manifesto
139   objetos DOCUMENT no armazém
```

**Três números, nenhum igual ao outro.** Não escolhi o mais bonito.

Não dá para resolver aqui: a medição externa trouxe **contagens por prefixo, não a lista de
chaves**. Sem as chaves não se casa objeto a objeto, e qualquer explicação para a diferença
seria inventada.

> **E é exatamente esta a conta que uma linha de `raw_asset` por objeto tornaria trivial.** A
> lacuna não é teórica: ela está a impedir uma reconciliação agora mesmo.

`ESTADO = NÃO_RECONCILIADO`.

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

## J · O GAP — um só, não cinco

> ## `G-42 · ITALY_STORAGE_METADATA_RECONCILIATION`

**195 objetos italianos no bucket `raw`, com 0 linhas de `raw_asset` e 0 de `collection_run`
a reclamá-los.** Cobre: os objetos órfãos, as três contagens que não batem, o passo 2 que não
existe para a Itália, e a política futura de atomicidade.

**Um gap, não cinco tickets** — porque são um problema só visto de quatro ângulos, e partido
em cinco cada pedaço ficaria pequeno demais para alguém priorizar.

---

## K · A PRÓXIMA AÇÃO SEGURA

1. **Pedir a lista de chaves** do prefixo `IT/` — só ela fecha as três contagens.
2. Decidir se um *backfill verificável* (141 documentos com procedência completa) é aceitável
   — **e a corrida continua não sendo recuperável**, o que precisa de resposta própria.
3. Só depois: `derived_artifact`, testada num Postgres local e descartável.

**Nada disto é para hoje. Hoje era medir e mostrar.**
