# ADR · O CONTRATO CANÓNICO DO TEXTO NA COLLECTION

> **A pergunta:** qual é o contrato canónico para transportar evidência textual
> adquirida pela Collection sem confundir legenda, transcrição, ASR, texto de
> página, original e tradução?
>
> **O que estava medido antes desta decisão:** `E1–E6 = PASS`, `E7 = STOP`.

```
SCRAP/social_envelope      TEXT
Collection/admission       item['texto']
entre os dois              NENHUMA TRADUÇÃO CANÓNICA
```

---

## 1 · POR QUE `texto = TEXT` ERA A RESPOSTA ERRADA

Uma linha. E é exactamente por isso que era perigosa: escrevê-la **apaga a
espécie do texto**.

O censo mediu, nos produtores reais desta árvore, **cinco espécies diferentes a
sair pelo mesmo campo `TEXT`**:

| produtor | o que põe em `TEXT` | espécie real |
|---|---|---|
| `social_rotas.bluesky_feed_autor` | `record.text` | o que o autor escreveu |
| `social_rotas.bluesky_buscar_contas` | `description` | a **bio de um perfil** |
| `social_rotas.telegram_canal` | `_sem_tags(html)[:4000]` | **página raspada e cortada** |
| `youtube_oficial._comentario` | `textOriginal` | o comentário de uma pessoa |
| `adaptador_youtube.…_legenda_paga` | `it['transcript']` | **a FALA, ouvida por máquina** |

E o último **já sabia que não sabia**: ele escreve
`'SPECIES': 'NOT_DECLARED_BY_PROVIDER'` dentro do `RAW`, porque o contrato não
tinha onde pôr a resposta.

```
UM CAMPO CHAMADO `TEXT` NÃO PROVA A ESPÉCIE DO TEXTO.
```

### E não é uma preocupação teórica: muda o veredito

`admissao._do_universo` casa o texto contra léxico **italiano e português**. O
próprio ficheiro tem a medição escrita: *«contra o único texto italiano real
desta árvore: **1 de 28** palavras aparecia lá»*.

Entregar a **tradução inglesa** a quem mede o **original italiano** não parte
nada. Muda a resposta, e não deixa marca.

```
CAPTION != TRANSCRIPT · ORIGINAL != TRANSLATED
```

---

## 2 · O DONO — E POR QUE NÃO SE INVENTOU UM

`regras/proveniencia.py`. **Não é escolha nova:** é a que a C6 já tinha feito, e
está escrita no documento dela:

> `ONE CONCEPT -> ONE OWNER`. E o dono da procedência de um texto derivado não é
> quem o colheu primeiro: é quem governa procedência.

O que esta missão encontrou foi que **esse dono não existia na linha da
Collection**. `regras/proveniencia.py` tem 24 316 bytes no SCRAP e tinha 20 437
aqui — e `TEXT_KIND` aparecia **zero** vezes nesta linha. O contrato existia de
um lado da fronteira e não do outro. Era esse o E7.

---

## 3 · A DECISÃO — DOIS EIXOS, E NÃO QUATRO NOMES

A C6 declarou quatro valores num eixo só: `NATIVE_CAPTION_ORIGINAL`,
`NATIVE_CAPTION_TRANSLATED`, `ASR_LOCAL`, `NÃO SEI`. Resolviam o problema dela
— legenda de vídeo — e **não conseguem escrever o que atravessa esta
fronteira**. A razão é estrutural, não de gosto:

> `ASR_LOCAL` não tem par traduzido. Um Whisper que traduz enquanto ouve produz
> texto que não é `ASR_LOCAL` (não está na língua falada) e não é
> `NATIVE_CAPTION_TRANSLATED` (não é legenda da plataforma). Com quatro nomes
> num eixo só, **esse texto não tem nome** — e o que não tem nome vai parar ao
> nome mais parecido.

```
ESPÉCIE = (O QUE O TEXTO É) × (QUE RELAÇÃO TEM COM O ORIGINAL)
```

| eixo | valores |
|---|---|
| `TEXT_KIND` | `AUTHOR_TEXT` · `NATIVE_CAPTION` · `TRANSCRIPT` · `ASR` · `PAGE_TEXT` · `DOCUMENT_TEXT` · `UNKNOWN` |
| `TEXT_RELATION` | `ORIGINAL` · `TRANSLATED` · `UNKNOWN` |
| `TEXT_KIND_BASIS` | `DECLARED_BY_PROVIDER` · `PRODUCED_BY_LOCAL_ASR` · `DECLARED_BY_ROUTE` · `NOT_DECLARED` |

**Não é um segundo modelo.** Os quatro nomes da C6 continuam a resolver, e
decompõem-se no par que sempre foram (`ESPECIE_COMPOSTA`). Há prova de que
`serve_para_original` responde o mesmo nas duas formas.

### `CAPTION` teve de deixar de existir como valor

Medido: o mesmo token significa duas coisas incompatíveis nesta árvore.

```
coleta/comunicacao_coleta.py   'TEXT_KIND': 'CAPTION'   = o que o AUTOR escreveu
regras/proveniencia.py (C6)    NATIVE_CAPTION_*         = a faixa de LEGENDA
```

Um vocabulário em que `CAPTION` é ao mesmo tempo «texto de gente» e «fala de
máquina» é o ataque *caption tratado como transcript* **já escrito no
dicionário**. O `BENCHMARK-V1-FINAL` viu metade disto e pediu `NATIVE_CAPTION`;
a outra metade é esta — o primeiro valor também precisava de um nome que não
colidisse, e passa a ser `AUTHOR_TEXT`.

```
DOIS SIGNIFICADOS NUM TOKEN NÃO SÃO UM VOCABULÁRIO:
SÃO UMA COLISÃO COM AR DE ACORDO.
```

---

## 4 · UMA LISTA DE UNIDADES, E NÃO UM CAMPO

Isto não foi escolhido: **já estava escrito à mão** em
`coleta/comunicacao_coleta.py`, e ninguém lhe tinha dado nome —

> «`TEXT` É A LEGENDA — o que o autor escreveu. […] existe um segundo texto no
> mesmo item: a FALA. Somar os dois neste campo apagaria qual deles sustentou o
> que vier depois. A fala entra em `TRANSCRIPT_TEXT`, e nunca aqui.»

A casa já tinha aberto um segundo campo para não somar os dois. Um terceiro
campo para a tradução, um quarto para o ASR:

```
UM CAMPO POR ESPÉCIE É UM ESQUEMA QUE CRESCE COM O VOCABULÁRIO.
UMA LISTA DE UNIDADES COM ESPÉCIE DECLARADA NÃO CRESCE COM NADA.
```

O campo é `TEXT_UNITS`. Cada unidade leva valor, espécie, relação, língua,
morada, e **linhagem**: `RAW_OBSERVATION_ID` · `SOURCE_ARTIFACT` ·
`DERIVATION_METHOD` · `TOOL` · `MODEL`.

### O `TEXT_UNIT_ID` é morada, nunca identidade

Ele serve para uma tradução apontar para o seu original e para o recibo dizer
qual unidade foi lida. **Não pode ser um SHA**, e o contrato recusa-o —
`leis/retorno_da_coleta.py::_fabricado` já mediu porquê: 35 valores de `sha256`
aparecem em observações DISTINTAS desta árvore.

```
SHA IDENTIFICA BYTES. NÃO IDENTIFICA DOCUMENTO, NEM UNIDADE DE TEXTO.
```

---

## 5 · COMO QUEM JULGA ESCOLHE O TEXTO QUE LÊ

A porta lê **um** texto; a observação traz **N**. Entre as duas há uma escolha.

```
PEGAR NO PRIMEIRO DA LISTA É UMA REGRA. É SÓ UMA REGRA QUE NINGUÉM DECIDIU,
QUE NINGUÉM CONSEGUE LER, E QUE MUDA QUANDO A ORDEM MUDA.
```

A ordem canónica, em `regras/proveniencia.py`:

1. `ORIGINAL` antes de `TRANSLATED`, e `TRANSLATED` antes de `UNKNOWN`.
2. Depois, por **quantas máquinas há entre o autor e o texto**:
   `AUTHOR_TEXT` → `NATIVE_CAPTION` → `TRANSCRIPT` → `ASR` → `PAGE_TEXT` →
   `DOCUMENT_TEXT` → `UNKNOWN`.
3. Empate só entre unidades iguais nos dois eixos, e aí desempata a **morada
   declarada** — não «a primeira que apareceu».

A escolha **fica escrita no item** (`texto_especie`, `texto_relacao`,
`texto_lingua`, `texto_unidade`, `texto_escolha_porque`), e aplica-se **uma vez
só**, em `coleta/ingresso.py::para_a_porta` — que já era o tradutor único da
fronteira para os dez nomes do contrato comum.

```
UMA TRAVESSIA, UM TRADUTOR, NA FRONTEIRA. O TEXTO NÃO É EXCEPÇÃO.
```

---

## 6 · MIGRAÇÃO — E O QUE TEM DATA PARA SAIR

| campo | estado | quem manda |
|---|---|---|
| `TEXT_UNITS` | **o dono da evidência textual** | `regras/proveniencia.py` |
| `TEXT` (envelope) | projecção curta, **mantida** | tem leitores medidos: `social_scrap.TEXT_HEAD`, `social_envelope.dedupe` |
| `texto` (porta) | projecção da escolha, **mantida** | produzida só pelo selector canónico |

`TEXT` e `texto` **não são um segundo contrato equivalente**: são projecções
declaradas de `TEXT_UNITS`, com regra escrita e um só produtor. O que era
proibido — dois donos do mesmo conceito — não existe: há prova
(`test_so_um_ficheiro_declara_o_vocabulario_da_especie`) de que **um só ficheiro
em toda a árvore declara `TEXT_KINDS`**.

E o caminho antigo não contorna o novo: um `texto` escrito à mão ao lado de
`TEXT_UNITS` que **discorde** do que a regra escolheu levanta
`ingresso.TextoEmConflito`.

```
UM CONTRATO QUE O CAMINHO ANTIGO CONSEGUE CONTORNAR NÃO É UM CONTRATO.
```

### O envelope legado

Envelopes escritos antes desta lei só têm `TEXT`. A ponte
(`proveniencia.unidades_do_envelope`) dá-lhes **`UNKNOWN` com base
`NOT_DECLARED`** — nunca `AUTHOR_TEXT` porque «é um post, deve ser do autor». É
a mesma forma de `leis/retorno_da_coleta.py::envelope_do_legado`, onde o legado
só pode declarar SUPORTE: **o legado só declara o que é inofensivo estar
errado.**

E a língua da publicação **não desce** para a unidade: colá-la a um texto de
espécie desconhecida seria afirmar, sobre um texto que não sabemos o que é, que
está na língua de outra coisa.

---

## 7 · O QUE FALTA DO OUTRO LADO DA FRONTEIRA

`coleta/scrap_colheita.py` **não existe na linha da Collection** e não foi
tocado — a branch do SCRAP não se modifica. Quando as duas linhas convergirem,
o mapeador dele precisa de **uma linha**, e ela chama o dono, não reescreve a
travessia:

```python
fora[pv.CAMPO_DAS_UNIDADES] = pv.unidades_do_envelope(objeto)
```

Está provada em `provas/ensaio_do_texto_na_collection.py`, que é onde a entrada
controlada equivalente ao SCRAP a exerce. Enquanto essa linha não existir lá, o
envelope do SCRAP atravessa pela ponte do legado — isto é, com espécie
`UNKNOWN`. **Não perde texto; declara que não sabe a espécie.**

```
SCRAP_MAPPER_PENDING = uma linha, em `DO_SCRAP_PARA_A_PORTA`
```

---

## 8 · O QUE FICOU MEDIDO

```
E1–E7                      PASS   nos quatro casos
TEXT_KIND_LOSS             0
SURVIVING_ATTACKS          0      (15 ataques)
SURVIVING_MUTANTS          0
NEW_FAILURES               0
ADMISSION_JUDGMENT_CHANGED NO     174 vereditos reais, byte a byte iguais
REAL_NETWORK               0      APIFY_RUNS 0 · PAID_USD 0
```
