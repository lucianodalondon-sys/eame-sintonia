# RECONCILIAÇÃO DO LOTE ITALIANO QUE JÁ ESTÁ NO SUPABASE

`COUNTRY = IT` · `SOURCE_ID = IT-ADAMA-CATALOG` · `COLLECTION_ID = IT-ADAMA-CATALOG-2026-08-30`
· `RULE_VERSION = IT-RECONCILE-1.0` · `RECONCILED_AT = 2026-09-05`

> **Esta missão para na porta da Inteligência.** Ela não classifica relevância, não roteia
> para capacidade, não abre o Casco, não define política do D1 e não ativa o Passaporte.

---

## 1 · A PERGUNTA

Há **195 objetos** sob o prefixo `IT/adama-website` no bucket `raw`. Eles subiram em
2026-08-30, pelo runner local, e o portão de preservação fechou com as oito condições
satisfeitas: 195 presentes, 195 hashes conferidos **depois de baixar cada um de volta**,
zero divergência, 80.714.570 bytes conferidos remotamente.

A pergunta desta missão não é *"o que esse material deveria virar"*. É:

> **de cada um dos 195, o que a casa já sabe — e quanto disso já foi pago?**

---

## 2 · A ROTA BARATA: LER A PROVA, NÃO O BALDE

Este ambiente **não tem** `SUPABASE_URL` nem `SUPABASE_SECRET_KEY`, e não deve ter. A rota
até o balde já havia sido tentada e registrada como fechada aqui, em
`LABEL-MANIFEST.json`:

| rota tentada | resultado medido |
|---|---|
| `ADAMA_MEDIA_DOWNLOAD` (adama.com) | **403** — três amostras, o mesmo veredicto |
| `MINISTERO_BANCA_DATI_ETICHETTE` | cadeia TLS incompleta (só a folha) |
| `SUPABASE_BUCKET` | **`NO_CREDENTIALS_IN_THIS_ENVIRONMENT`** |

E o inventário dos 195 **já existe em Git**, com SHA256 conferido no retorno. Abrir o balde
não acrescentaria um fato e custaria uma credencial que este ambiente não deve carregar.
Por isso a reconciliação é derivada de **prova preservada**, e o script fixa cada fonte pelo
**SHA do blob** — branch anda, conteúdo não.

`scripts/it_supabase_reconciliar.py` · `python3 scripts/it_supabase_reconciliar.py --conferir`

---

## 3 · O QUE ENTRA COMO IDENTIDADE, E O QUE NÃO ENTRA

| chave | força | por quê |
|---|---|---|
| `SHA256` | **forte** | o conteúdo é o próprio nome |
| `OBJETO` | **forte** | o endereço no balde |
| `ARQUIVO_LOCAL` | **forte** | o caminho no acervo que subiu |
| `SOURCE_URL` | **forte** | a rota de mídia daquele documento |
| `PRODUCT_URL` | fraca | identifica o **produto pai**, nunca o documento |
| `ORIGINAL_FILENAME` | fraca | colide — `robots.txt` casa com 42 arquivos do acervo |

Foi essa separação que evitou o erro mais fácil desta reconciliação: **139 documentos
aparecem no portal italiano** — mas por `PRODUCT_URL`. O que está no portal é o produto
pai. Nenhum daqueles PDFs foi lido.

### As três leis do crosswalk

1. **Mencionado não é consumido.** `ALREADY_CONSUMED` exige **duas** provas citadas: o
   conteúdo foi lido **e** virou fato derivado.
2. **Chave fraca não estabelece identidade.** Ela entra como contexto e nunca como prova.
3. **Ausência declarada é resultado.** `UNKNOWN` nunca é promovido a estado.

---

## 4 · OS SEIS BALDES — DISJUNTOS, ORDENADOS, FECHANDO EM 195

| balde | n | o que sustenta |
|---|---:|---|
| `ALREADY_CONSUMED` | **53** | 51 páginas de produto lidas e viradas em fato (`ACTIVE_INGREDIENT`, `FORMULATION`, `PACKAGE_SIZE`, `TABLES`) + 2 PDFs cujos bytes a casa leu pela rota Ministero, com o texto persistido |
| `KNOWN_NOT_CONSUMED` | **137** | **varridos lexicamente e nunca lidos** — ver §5 |
| `ALREADY_ACCOUNTED` | **2** | os dois `MANIFEST`: `enumeracao.json` (o censo copia 9 campos do conteúdo dele) e `indice-captura.json` (um teste adversarial o lê linha a linha) |
| `SUPABASE_ONLY` | **3** | os três `CAPTURE`: `home-italia-it.html`, `sitemap-italia-it.xml`, `robots.txt` — ver §6 |
| `AMBIGUOUS` | **0** | — |
| `UNKNOWN` | **0** | — |
| **TOTAL_ACCOUNTED** | **195** | |

### Uma ressalva sobre os 51, escrita porque a primeira redação estava errada

O `CROSSWALK` das páginas de produto **não** foi corrido contra o registro nacional do
Ministero. Foi corrido contra a **fatia de 163 registros de titular ADAMA** que a casa
mediu — e o próprio arquivo escreve que o dataset nacional `PROD_FTS` *"não está neste
repositório"*. É por isso que 10 dos 51 saem como
`LOCAL_PRESENT_BUT_REGISTRATION_NOT_PROVED`: por causa da fatia, não por causa da página.
A leitura das 51 páginas está provada; a frase "contra o registro do Ministero" não estava.

### O achado que muda o valor do balde

Dos 195, **142 nunca tiveram o conteúdo lido** — e a razão está escrita, não suposta: a
origem devolve 403, e o material original vive numa máquina residencial fora do Git.

> **O balde deixou de ser cópia de segurança e passou a ser a única rota viva até esse
> conteúdo.** Os 137 documentos estão lá, com SHA256 conferido, prontos para leitura — e
> ninguém precisa pedir nada à `adama.com` de novo.

Isso é o oposto de "falta coletar". **Não falta coletar nada.** Falta ler o que já foi pago.

---

## 5 · `LEXICALLY_SCANNED` — O ESTADO QUE QUASE VIROU `NOT_READ`

A primeira redação deste crosswalk dizia que os 139 documentos estavam `NOT_READ`, apoiada
em `LABEL-MANIFEST.json`: `PARSE_STATE = NOT_PARSED` em 141 de 141. Uma verificação
adversarial derrubou isso, e o achado é melhor do que a afirmação.

`scripts/adama_it_catalogo.py :: tipar_documento` **abre cada PDF local** com
`scripts/pdf_text.py`, extrai até 3 páginas / 20.000 caracteres, e casa frases que só
existem **dentro** do documento — *"scheda di dati di sicurezza"*, *"etichetta
autorizzata"*, *"estensione d'impiego"*. O censo do catálogo carrega o resultado:

| campo do censo, derivado de dentro do PDF | medida |
|---|---|
| `TYPE_DECIDED_BY = CONTENT` | **85** de 141 |
| `TYPE_FROM_CONTENT` preenchido | 85 (48 SDS + 37 etichetta) |
| `PRODUCTS_NAMED_IN_DOCUMENT` não vazio | 16 |
| `CONTENT_READABLE` medido (`bool(texto)`) | 132 sim · 9 não |

**Os dois artefatos não se contradizem — eles são de ambientes diferentes.** A varredura é
de 2026-08-30, na máquina que tinha os bytes. O `NOT_PARSED` é de 2026-09-02, num ambiente
onde o PDF não era alcançável. O crosswalk carrega os dois, e o estado correto é o que o
contrato do Passaporte existe para criar:

> `LEXICALLY_SCANNED` registra que **um classificador tocou o texto** — e **nunca** satisfaz
> `INTELLIGENCE_READING`.

O balde não muda: `KNOWN_NOT_CONSUMED` continua com os 137. O que muda é a próxima ação, e
ela fica mais barata: o texto já saiu daquele PDF uma vez.

`CONTENT_READABLE = false` em 9 documentos também deixa de ser declaração e vira
**medição**: o extrator rodou e não tirou texto. A próxima ação continua sendo reler do
balde — e, se o texto não sair de novo, **declarar a rota de texto fechada** para aquele
documento. Nunca rejeitar por ausência.

### A quase-cobertura — 118 documentos que quase contam, e não contam

Uma segunda verificação varreu os 194 hashes distintos do inventário contra os 2.751 blobs
das 50 branches, nos dois sentidos. Ela **não** derrubou os 2 da rota Ministero — e trouxe
o vizinho perigoso:

| relação com os 163 rótulos lidos do Ministero | objetos | vale como leitura? |
|---|---:|---|
| **mesmos bytes** (SHA256 idêntico) | **2** | **sim** — o texto está em `testo/*.txt`, 24.229 e 12.466 caracteres |
| **mesmo registro, arquivo diferente** | **118** | **não** |
| nem registro em comum | 19 | não |

Os 118 são outra **renderização** do mesmo rótulo autorizado: `GOLTIX` reg. 002732 tem
108.797 bytes no site da ADAMA e 108.648 no Ministero. Ler um não é ter lido o outro.

> **HASH DIFERENTE = OBJETO DIFERENTE = NÃO FOI LIDO.**
> São dívida de leitura, nunca crédito.

Isso entra como `EVIDENCIA_DE_CONTEXTO` — **nunca** como identidade — e está contado em
`QUASE_COBERTURA`, porque é a confusão mais fácil deste lote: quem somasse os dois
declararia uma cobertura que não existe. Há teste que reprova qualquer item cuja única
prova de leitura seja essa vizinhança.

E há uma ressalva sobre os **próprios 2**: pela porta da ADAMA eles também estão
`NOT_PARSED`. O que sustenta `ALREADY_CONSUMED` é exclusivamente a **identidade de bytes**
com um rótulo que a casa leu por outra rota — consumo por identidade forte, não consumo
pela porta da ADAMA. A distinção está escrita no artefato.

### A escada, depois da correção

| onde o item parou | n | por quê |
|---|---:|---|
| `INTELLIGENCE_READING` | **137** | conteúdo disponível no balde, varrido, nunca lido |
| `ROUTING` | **53** | lido, com fato extraído — rotear é pergunta da Inteligência |
| `NORMALIZATION` | **5** | não estão em censo nenhum; não têm projeção estruturada (ver §6) |

---

## 6 · OS CINCO CASOS DE BORDA, E O `robots.txt` QUE EU CLASSIFIQUEI ERRADO

Cinco objetos não são contados como material por nenhum censo. Eu havia classificado
`robots.txt` como `ALREADY_ACCOUNTED`, com o raciocínio de que
`DOCUMENT_CENSUS_INCOMPLETE_REASON = ROBOTS_DISALLOWS_AJAX_ROUTE` derivava de lê-lo. **Não
deriva.** A verificação mostrou, e conferi de novo por conta própria:

- a razão é **string literal** em `adama_it_preservar.py:262` — não há leitura de arquivo
  por perto;
- `captures` aparece **uma única vez** em todo o código italiano: a tupla
  `('captures', 'CAPTURE', None)`, que só percorre o diretório e calcula o hash;
- o único código da casa que **parseia** `robots.txt` está noutra branch e busca o arquivo
  **ao vivo pela rede**, nunca a cópia preservada.

**A espécie dele vem do nome da pasta, e classificador não é consumo.** → `SUPABASE_ONLY`.

A linha divisória, medida e não suposta: o código italiano abre uma lista **fechada** de
arquivos do acervo — `amostra-10.json`, `documentos-amostra.json`, `documentos-censo.json`,
`enumeracao.json`, `indice-captura.json`. Os dois `MANIFEST` preservados são exatamente os
dois que têm consumidor. Os três `CAPTURE` não são abertos por ninguém.

### A lacuna que apareceu olhando para o lado

Simetricamente: **três** arquivos do acervo que a casa **lê** ficaram **fora** dos 195 —
`amostra-10.json`, `documentos-amostra.json`, `documentos-censo.json`. São justamente
aqueles de que o censo completo (51 produtos / 141 links) depende.

> Eles não estão no Git (`data/raw` é ignorado) e não estão no balde. Existem **só** no
> disco da máquina que coletou. Se aquela máquina se perder, **o censo completo não é
> re-derivável** — e nenhum dos 195 avisa isso.

Está registrado como `GAP` em `CONTROL-PLANE-EVIDENCE-CANDIDATE.json`. Não é desta missão
resolver; é desta missão não deixar passar em silêncio.

---

## 7 · A PENEIRA TÉCNICA — A PRIMEIRA PERGUNTA NÃO É RELEVÂNCIA

| veredicto | n | motivo |
|---|---:|---|
| `KEEP` | **53** | já é fato na casa |
| `DEFER` | **142** | *não utilizável **ainda*** — 128 `LEXICALLY_SCANNED_NOT_READ`, 9 `CONTENT_DECLARED_UNREADABLE`, 5 `ROLE_DECLARED_NO_READING_YET`. A próxima ação é ler **a partir do balde** |
| `REJECT_WITH_REASON` | **0** | nada foi julgado inutilizável |
| `ERROR` | **0** | nenhum objeto sem bytes conferidos |

`REJECT = 0` **é um resultado, não uma omissão.** Os dois objetos que compartilham os
mesmos bytes (`Postscript 80 XL` e `Davai`, mesma Scheda di Sicurezza) não são duplicata a
descartar: a casa já decidiu que *hash igual não apaga origem*, e as duas procedências
continuam inteiras. **A máquina nunca rejeita por ausência.**

Cada motivo carrega **próxima ação própria**, porque motivo sem próxima ação é desculpa —
e há teste que reprova um item em `DEFER` sem `NEXT_ACTION`.

---

## 8 · PRÉ-PASSAPORTE SOMBRA — O QUE ELE É, E O QUE ELE NÃO É

`data/samples/IT-SUPABASE-COLETA/IT-195-PRE-PASSAPORTE-SOMBRA.json`

**Sombra** quer dizer: usa o vocabulário fechado de `PASSPORT-1.0` e **não é passaporte**.
Nenhum evento foi selado, nenhum portão foi atravessado, `data/passaporte/EVENTOS.jsonl`
não foi tocado. É a projeção que o Passaporte **teria** se estes 195 entrassem — para que o
dia da entrada seja uma **migração declarada**, e não uma digitação.

Três decisões ficam **abertas e escritas**, em vez de resolvidas por conveniência:

- `SOURCE_FAMILY`: `MANUFACTURER_PUBLIC_CATALOG` **não existe** no vocabulário fechado de
  `PASSPORT-1.0`. Ou a família entra, ou o lote é dobrado numa família existente.
- **Granularidade**: 195 passaportes por objeto, ou um `DATASET_SNAPSHOT` com
  `UNIT_COUNT = 195`.
- `CONSUMPTION_STATE` dos 53 já consumidos: **qual** capacidade consumiu, e por **qual caso
  publicado**. Sem isso o selo seria digitado, não derivado — então ele fica `PENDING`, que
  é a verdade.

---

## 9 · CONTROL_PLANE_EVIDENCE_CANDIDATE

`data/samples/IT-SUPABASE-COLETA/CONTROL-PLANE-EVIDENCE-CANDIDATE.json`

**Não é o Control Plane de Coleta.** Não é estado canônico, não define schema e não abre
missão. É o que a casa **já escreveu** sobre esta coleta — onde ela parou, o que falhou,
qual rota morreu, quando foi, quanto pesou — preservado com a prova ao lado, para que o dia
em que o Control Plane existir não comece com uma página em branco.

Cada candidato traz `KIND`, `VALUE`, `SCOPE`, `RELIABILITY` (`MEDIDO` · `DECLARADO` ·
`INFERIDO`) e a citação da fonte.

---

## 10 · O CHECKPOINT ANTES DA FASE CARA

```
TOTAL                         = 195
MECHANICALLY_RECONCILED       = 190
ALREADY_READ                  =  53
ALREADY_LEXICALLY_SCANNED     = 137      (varridos, nunca lidos — nao contam como lidos)
READ_QUEUE                    =   5      (os 3 CAPTURE + 2 MANIFEST, casos de borda)
PERCENT_REQUIRING_NEW_READING = 2,6 %
```

O portão passou, e por um motivo que precisa ficar escrito: **a fila de leitura é baixa
porque a casa já tinha feito o trabalho** — não porque o crosswalk foi permissivo.
`REUSED_EXISTING_WORK = 190`.

E há um número que não é escolha, é medição:

```
OBJECT_BYTES_AVAILABLE_IN_THIS_ENVIRONMENT = 0
ACTUALLY_READ_NOW                          = 0
```

**Nenhum byte dos 195 existe neste ambiente.** `data/raw` está fora do Git por política
(D-003) e não há credencial do balde aqui. Toda leitura registrada nesta reconciliação é
leitura de **prova**, nunca de objeto — e o artefato diz isso em vez de deixar a contagem
sugerir o contrário.

---

## 11 · O QUE NÃO MUDOU

```
SUPABASE_CHANGED     = NÃO      (nenhuma chamada; não há credencial aqui)
STORAGE_CHANGED      = NÃO
CANONICAL_CHANGED    = NÃO      (sintonia/canonical intocada)
INTELLIGENCE_CHANGED = NÃO
PORTAL_CHANGED       = NÃO
OS_43_CHANGED        = NÃO
MOTOR_CHANGED        = NÃO
PASSAPORTE_ATIVADO   = NÃO
D1_POLICY_DEFINED    = NÃO
scripts/voz.py       = intocado
```

---

## 12 · O QUE FICA NA PORTA DA INTELIGÊNCIA

`COLLECTION_PACKAGE_STATE = READY`, com **uma** coisa faltando, e ela é pequena:

> **ler os 137 documentos a partir do balde.**

Eles estão lá, com hash conferido, a rota da origem está morta, e o texto **já saiu de
dentro deles uma vez** — a varredura de tipagem provou que o extrator funciona nesse
material. Essa leitura é uma missão da linha da Itália, não desta. Esta aqui para aqui.
