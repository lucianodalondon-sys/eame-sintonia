# A CASA DO DERIVADO — a única tabela que sobreviveu à medição

**Censo, desenho e prova** · 2026-09-08 · ramo `claude/italia-biblia-integracao-v1`

> **Nada foi aplicado em produção.** 0 migrations aplicadas, 0 escritas, 0 uploads, 0 deletes,
> 0 backfill, 0 corridas retrocriadas. A `022` foi aplicada e provada num **Postgres 16 que
> morre no fim do job**.

---

## A · O CENSO VEIO PRIMEIRO

Quatro missões apontaram para `derived_artifact`. Isso não autoriza desenhá-la de cabeça —
**desenhar primeiro e medir depois é medir o buraco pelo tamanho da tampa já comprada.**

Medido em [`censo_das_derivacoes.py`](../../system-map/scripts/censo_das_derivacoes.py):

```
7 produtores medidos      e só 3 são de espécie DERIVED_ARTIFACT
2 ferramentas de derivação    texto-de-pdf · whisper
2 tipos reais hoje            texto simples · transcrição
```

### A armadilha: chamar tudo de derivado

| o quê | espécie | por quê |
|---|---|---|
| `executor_texto_de_pdf.py` → TXT | **`DERIVED_ARTIFACT`** | **nós** produzimos, de bytes que guardámos |
| `youtube_transcrever.py` → texto | **`DERIVED_ARTIFACT`** | Whisper local, com **modelo escolhível** |
| `instagram_transcrever.py` → texto | **`DERIVED_ARTIFACT`** | idem |
| legenda que o YouTube entregou | `RAW_CAPTURE` | ⚠️ **veio com a coleta.** Nós não a produzimos |
| `italy_extract_fields.mjs` → campos | `STRUCTURED_RECORD` | extrai campos, não um artefato com bytes |
| `admissao.py` → decisão | `CLAIM_OU_JUIZO` | julga. COL-LAW-502: julgar um texto não é derivá-lo |
| `pdf_text.py` | `BIBLIOTECA` | não escreve artefato nenhum |

> **Meter uma legenda do YouTube em `derived_artifact` diria que nós a produzimos.** Diria
> mal, e a partir daí a linhagem mentiria para toda a gente.

### E o vocabulário já existia

`leis/artefato.py` já distingue `RAW` de `DERIVED`, com `PARENT_ARTIFACT_ID`,
`PARENT_SHA256`, `DERIVATION_TYPE`, `EXECUTOR_ID/VERSION`, `PIPELINE_VERSION` — **os 9 campos
conferidos, todos presentes**. A tabela **traduz** esse contrato; não inventa outro. Duas
gramáticas para a mesma coisa dariam mais uma tradução a poder mentir.

---

## B · O GRÃO, EM UMA FRASE

> ## Uma linha representa **UM artefato que nós produzimos, a partir de UM conteúdo bruto, por UMA ferramenta numa VERSÃO, com UNS parâmetros, numa POSIÇÃO da série.**

Testada contra os oito casos que a quebrariam:

| caso | resultado |
|---|---|
| PDF → TXT | 1 linha |
| o mesmo PDF → OCR | outro `kind` → outra linha |
| o mesmo PDF → thumbnail | outro `kind` → outra linha |
| **o mesmo PDF → 10 frames** | mesmo tudo, e **dez artefatos** ⚠️ |
| áudio → transcrição | 1 linha |
| o mesmo RAW por **duas versões** | duas linhas, ambas legítimas |
| retry idêntico | mesma chave, mesmos bytes → **REUSED** |
| os mesmos bytes por rotas diferentes | `producer` diferente → duas linhas, **um só** `sha256` |

**O caso dos frames é o que quebra qualquer chave ingénua.** Mesmo pai, mesmo tipo, mesma
ferramenta, mesma versão, mesmos parâmetros — e dez artefatos distintos. Por isso existe
`serie_posicao`: `NULL` quando a derivação produz um só, `0..N` quando produz vários. **É o
único campo que existe por causa de um caso que ainda não temos** — e existe porque sem ele a
chave é falsa no dia em que ele aparecer.

---

## B2 · O RED TEAM ENCONTROU DUAS COISAS — e a primeira estava aberta

### 1 · O filho podia declarar DOIS pais diferentes

`raw_asset_id` apontava para o pai A. `parent_sha256` dizia os bytes de B. **As duas travas
passavam** — porque A existe, e porque o hash tinha o formato certo — e a linha ficava a
dizer duas coisas ao mesmo tempo.

**Reproduzido no Postgres antes de ser fechado**, e o resultado foi literalmente:

```
FAIL COERENCIA_id_e_sha_apontam_para_o_mesmo_pai    ACEITOU DOIS PAIS DIFERENTES
```

> ### FK EXISTIR NÃO BASTA.
> Se dois campos declaram o mesmo parentesco, eles **não podem discordar**.

**Fechado com uma chave estrangeira COMPOSTA, declarativa — não com um gatilho:**

```sql
alter table public.raw_asset
  add constraint raw_asset_id_e_sha_juntos unique (id, sha256);

constraint o_pai_por_id_e_o_pai_por_sha_sao_o_mesmo
  foreign key (raw_asset_id, parent_sha256)
  references public.raw_asset (id, sha256) on delete restrict
```

As duas colunas **viajam juntas**. Se o par `(A, bytes-de-B)` não existir do outro lado, o
banco recusa — sem depender de quem escreve. A trava nova em `raw_asset` é aditiva e **não
pode reprovar sobre dado nenhum**: `(id, sha256)` já era único porque `id` é a chave
primária. Ela existe só para dar ao Postgres o alvo declarativo de que precisa.

**E `parent_sha256` fica.** Removê-lo obrigaria a identidade a passar por `raw_asset_id` — e
isso **mudaria o grão** de conteúdo para captura, pela porta dos fundos. A coluna redundante
não é conveniência: é o que torna o grão certo expressável.

---

## B3 · O GRÃO: conteúdo ou captura?

Duas corridas trouxeram os mesmos bytes — **duas capturas legítimas**, duas linhas em
`raw_asset`. Derivadas com a mesma receita, dão **uma** linha ou **duas**?

> ## RESPOSTA: UMA. O grão é **CONTEÚDO POR RECEITA**.

**E a assimetria com `raw_asset` é deliberada, não descuido:**

| | grão | por quê |
|---|---|---|
| `raw_asset` | **ocorrência** | duas capturas são **dois factos sobre o mundo** — a fonte publicou nos dois sítios, e apagar uma perderia a prova de que o documento não mudou entre elas |
| `derived_artifact` | **conteúdo por receita** | aqui há **um** facto: a nossa ferramenta, sobre estes bytes, com esta régua, dá este resultado. Correr duas vezes é trabalho repetido, não informação nova — e os bytes de saída são idênticos |

> **Mesmos bytes não apagam a diferença entre duas capturas.** Mas também não criam duas
> derivações onde só houve uma receita.

### E a procedência da captura não se perde — porque nunca morou aqui

Ela mora em `raw_asset`: uma linha por captura, com a sua corrida, o seu `captured_at` e a
sua URL. Todas as irmãs encontram-se com uma pergunta só:

```sql
select * from raw_asset where sha256 = <parent_sha256>
```

O `raw_asset_id` desta tabela diz apenas **de qual cópia se leu**. É **testemunha, não
identidade** — e está escrito assim no comentário da coluna, para não se fingir o contrário.

Provado: `GEMEOS_a_mesma_receita_da_UMA_derivacao` (1 linha) ·
`GEMEOS_a_procedencia_das_duas_capturas_continua_inteira` (2 capturas achaveis).

**Nenhuma tabela nova foi criada.** O modelo atual chegou.

---

### 2 · Duas frases minhas prometiam mais do que o banco cumpre

| eu tinha escrito | o que é verdade |
|---|---|
| `derived_at NOT NULL` garante que a data «não foi herdada» | **Não garante.** O banco vê um `timestamptz`; não vê de onde veio. Quem copiasse o `captured_at` passaria sem um arranhão |
| — | O banco confere o **formato** de `parameters_hash`, **não** a correspondência com o JSON ao lado |

```
DB_PROVES_PRESENT   ≠   DB_PROVES_NOT_COPIED
```

Corrigido no texto **e provado ao contrário**: `H2_o_banco_NAO_impede_copiar_o_captured_at`
insere uma linha com `derived_at` igual ao `captured_at` do pai, e ela **entra** — como se
esperava. O teste existe para que ninguém volte a escrever que o banco cumpre essa lei.

**A lei continua a valer, e é do writer.** Ele mede o momento da derivação e serializa os
parâmetros com uma função só — e é lá que o teste tem de morar, quando o writer existir.
Um gatilho que tentasse adivinhar a serialização canónica seria uma segunda implementação da
regra, livre para divergir da primeira. **Duas verdades são piores do que uma.**

---

## C · A IDENTIDADE — e por que o `sha256` sozinho não serve

```
(parent_sha256, kind, producer, producer_version, parameters_hash, serie_posicao)
```

> **`SHA256` IDENTIFICA BYTES. NÃO IDENTIFICA LINHAGEM.**
> Duas rotas diferentes podem chegar aos mesmos bytes — e são duas derivações, não uma.
> Provado no Postgres: `I_mesmo_sha_do_filho_com_pais_diferentes_coexiste`.

**E o `sha256` do filho NÃO entra na chave, de propósito.** Se entrasse, a mesma régua com
resultado diferente viraria duas linhas caladas. Ficando de fora, ela dá **conflito** — que é
o que um resultado que mudou merece.

### A versão da ferramenta não é enfeite

**`whisper` não basta.** O modelo `base` e o `small` sobre o mesmo áudio dão textos
diferentes, e **os dois são legítimos** — está escrito em
`ferramentas/youtube_transcrever.py`, não é hipótese. Sem a versão na identidade, a segunda
passagem apagaria a primeira em silêncio.

Versão histórica que não se consegue provar entra como `UNKNOWN`. **Não se adivinha a versão
do `pdftotext` que produziu os 43 legados.**

---

## D · O QUE FICOU DE FORA, E POR QUÊ

| pediram-me para considerar | veredito |
|---|---|
| `parent_derived_artifact_id` (derivado de derivado) | **NÃO** — zero casos reais medidos. Acrescentar depois é aditivo e barato; acrescentar agora é especular |
| `derivation_run` (entidade própria) | **NÃO** — não houve prova. E esticar `collection_run` para significar algo que não é coleta seria pior do que não ter nada. Ficou um `derivation_batch` de texto: **rótulo para agrupar, não entidade, sem chave estrangeira** |
| coluna de `status` com erros | **NÃO** — a tabela guarda **só o que existe**. Uma derivação que falhou não tem bytes; ela vive no manifesto da corrida. Guardar linhas de erro aqui faria a tabela dos artefatos contar coisas que não são artefatos |
| corpo do texto dentro do Postgres | **NÃO** — bytes no Storage, memória no banco. Provado: `K_o_banco_nao_guarda_o_corpo_do_derivado` |
| segunda tabela qualquer | **NÃO** — uma bastou |

---

## E · O LEGADO — 43 derivados sem pai canónico

```
derivados existentes           43
linhas de raw_asset IT          0
ligáveis honestamente           0
```

**Nenhum dos 43 pode apontar para um `raw_asset`, porque não há nenhum.** A corrida que
teria trazido aqueles PDFs é `RUN_NOT_PROVABLE`.

> ### LEGADO SEM PAI CANÓNICO CONTINUA LEGADO SEM PAI CANÓNICO.
> A tentação óbvia desta missão era inventar as linhas de `raw_asset` que faltam, para a
> chave estrangeira ficar bonita. **Não se fabrica história para embelezar um diagrama.**

Classe: **`LEGACY_DERIVATION_WITHOUT_CANONICAL_RAW_PARENT`**. Fica classificado, não
remendado. **A migration é FORWARD** — abre a casa para o que vier, não repinta o que passou.

E `raw_asset_id` é **`NOT NULL`** justamente por isso: derivado sem bruto canónico não entra.
Que os 43 de hoje não caibam **é o desenho a funcionar**.

---

## F · AS TRAVAS, E O QUE CADA UMA IMPEDE

| trava | impede |
|---|---|
| `raw_asset_id NOT NULL` + FK | derivado órfão, sem bruto que o justifique |
| **`ON DELETE RESTRICT`** | apagar um bruto com filhos e **levar a linhagem junto, em silêncio** |
| `unique (parent_sha256, kind, producer, producer_version, parameters_hash, serie_posicao)` | a mesma derivação virar duas linhas — e o resultado que mudou passar calado |
| `storage_path UNIQUE` | dois objetos no mesmo endereço |
| `sha256 ~ '^[0-9a-f]{64}$'` | um hash que não é um hash |
| `kind` em lista fechada | um tipo inventado a entrar sem decisão |
| `producer_version NOT NULL` | duas versões da ferramenta a apagarem-se |
| `bytes >= 0` · `derived_at NOT NULL` | artefato sem tamanho ou sem data |

**`nulls not distinct` na chave** é obrigatório: `serie_posicao` é nulável, e no Postgres dois
nulos são *diferentes*. Sem isso a trava destrancava sozinha justamente para as linhas de
derivação simples — que são a maioria.

---

## G · PROVADO EM POSTGRES 16 DE VERDADE

**`banco-descartavel`, execução `34246698477` = SUCCESS.** Lido, não presumido.

```
POSTGRES16_FOUNDATION_SCHEMA_TESTED = PASS · 19 casos    (a garantia forward)
DERIVED_ARTIFACT_DB_TESTED          = PASS · 23 casos    (a casa do derivado)
a tranca recusou 4 de 4 endereços que não são descartáveis
```

Escopo: **`FOUNDATION_MAIS_022`** — só a `001` e a `022`. As `002`–`021` não entram: a `022`
não precisa delas, e aplicá-las só para dizer «o esquema inteiro» seria pagar por uma frase
maior do que a medição. **Não houve `MIGRATION_CHAIN_DRIFT` a contornar** — a `022` assenta
na `001` sem mais nada.

### Um caso que passou a dar FAIL antes de dar PASS — e ainda bem

O caso **B** (`sem raw, a FK recusa`) reprovou na primeira execução. O banco **recusou** o
insert — mas pela trava de **unicidade**, não pela chave estrangeira: eu tinha dado ao órfão a
mesma identidade do caso A, e a unicidade mordeu primeiro.

> **Recusar não é recusar pelo motivo certo.** Se eu tivesse aceitado «qualquer erro serve
> como prova», o teste passava e não provava nada. Corrigido dando ao órfão uma identidade
> própria; agora o erro que volta é literalmente `violates foreign key constraint`.

---

## G2 · O DONO DA ESCRITA — `do nothing` deixou de bastar

A tabela já recusava a linha repetida. **Isso não chega**, e a diferença é toda:

```
o BANCO   recusa a linha repetida
o WRITER  tem de saber POR QUE ela foi recusada
```

Se ele ler o silêncio do `on conflict do nothing` como «já lá estava, tudo igual», uma
derivação que passou a produzir **outro resultado** entra como `REUSED` — e o sistema fica
calado exatamente no dia em que devia gritar.

> ## IDEMPOTÊNCIA É REENCONTRO + COMPARAÇÃO + PROVA DE IGUALDADE.

`guarda/preservar_derivado.py`. O `insert` dele **não tem `on conflict`**, de propósito: ele
quer o erro, para poder ir **ler** o que lá está e comparar.

### O que este dono possui, e ninguém mais

| | de onde vem |
|---|---|
| `parent_sha256` | **lido do `raw_asset`** — nunca aceite do chamador |
| `sha256` e `bytes` do filho | **calculados dos bytes reais** — um valor informado é uma afirmação; medido é um facto |
| `parameters_hash` | de **uma** função canónica, e só dela |
| `derived_at` | do **relógio do writer** — injetável só nos testes |
| `storage_path` | **derivado da receita** — o chamador não escolhe |

Um chamador que pudesse trazer qualquer um destes prontos poderia mentir sobre a linhagem
sem que nada o impedisse. **E o banco não distingue um `timestamptz` medido de um copiado.**

### A serialização canónica, e o que cada escolha impede

```python
json.dumps(p, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
```

`sort_keys` — a ordem em que alguém escreveu o dicionário não muda o hash · sem espaços — a
formatação não entra na conta · `ensure_ascii=False` — `città` é `città`, sempre em UTF-8 ·
**ausência de parâmetros = `b""`**, cujo hash é o da cadeia vazia, que é o valor que a `022`
e as suas provas já usavam.

⚠️ **Não é JSON canónico da norma (RFC 8785).** É determinístico para o que esta casa usa —
dicionários, listas, texto, inteiros, booleanos, nulos. **Números de vírgula flutuante têm
armadilhas de representação que esta função não resolve**, e por isso não devem entrar em
parâmetros de derivação sem decisão própria. Está escrito na função.

### Os seis estados, e a decisão diferente por trás de cada um

| estado | quando |
|---|---|
| `INSERTED` | escrito, lido de volta e conferido nos **13 campos** |
| `REUSED` | identidade e **resultado** iguais, **lidos e comparados** |
| `REUSED_AFTER_RACE` | outro escritor ganhou a corrida **e escreveu o mesmo** |
| **`DERIVATION_DRIFT`** | mesma receita, **outro resultado**. Não apaga, não sobrescreve, não finge |
| `STORAGE_CONFLICT` | o endereço já tem outros bytes. Não apaga para «tentar de novo» |
| `METADATA_NOT_RECONCILED` | bytes guardados, linha não entrou — **e os bytes ficam** |

### O caso adversarial central

A mesma receita. A primeira execução produziu `AAAA`; a segunda, por um defeito de versão ou
de ambiente, produz `BBBB`. **A identidade continua igual.**

```
DERIVATION_DRIFT · o antigo continua lá · nenhum byte novo sobe
```

> **As duas versões são factos, e um deles é um defeito por descobrir.** Quem decide o que
> fazer é uma pessoa — não um `UPDATE` silencioso.

### A segunda captura, do lado de quem escreve

Duas capturas dos mesmos bytes, a mesma receita → **`REUSED`**, uma linha só. E a
**testemunha não se troca**: a linha continua a apontar para a cópia que foi lida da primeira
vez. Trocá-la reescreveria a história por nada, e a outra captura continua inteira em
`raw_asset`.

### Um limite medido e declarado

`REUSED` sai da leitura da **linha**. O writer **não** vai ao armazém confirmar que o objeto
continua lá. Se os bytes sumirem, o reencontro é sobre um artefato que já não existe — e
`test_26` documenta esse comportamento **como ele é hoje**, não como se estivesse resolvido.
É o próximo passo do dono.

---

## G3 · A PONTE PARA O EXECUTOR — e ela está desligada

`coleta/executor_texto_de_pdf.py` ganhou um parâmetro `entregar_ao_dono`, que é `None` por
omissão. **Enquanto for `None`, nada muda:** o caminho antigo continua a escrever o
`REGISTO-DE-ARTEFATOS.json`, como sempre.

**O executor não escreve no banco, e não vai passar a escrever.** A doutrina é a mesma do
bruto: o executor produz o artefato, o **dono canónico** persiste. Nenhum executor grava só
porque conhece a `SUPABASE_URL`.

E o que a ponte entrega é **só a receita** — `kind`, `producer`, `producer_version`,
`pipeline_version`, `parameters`, `serie_posicao`, `media_type`, `country` — e os bytes.
**Nem o `sha256` do pai viaja nela**, nem sequer como informação: um campo que ninguém usa é
um campo que um dia alguém usa mal, e este seria usado para declarar um pai que o executor
não pode provar. Há teste que reprova se algum deles aparecer lá.

**O legado não foi tocado.** Os 43 continuam `LEGACY_DERIVATION_WITHOUT_CANONICAL_RAW_PARENT`,
e nenhum foi migrado.

---

## G4 · O RED TEAM DO WRITER — três brechas, e a terceira era minha a fingir de limite

### 1 · `REUSED` sem confirmar que o byte ainda existe

O writer devolvia `REUSED` a partir da **leitura da linha**, sem nunca perguntar ao armazém.
Uma ficha viva sobre um artefato apagado passava por «reaproveitado, está tudo bem».

> ### UMA LINHA NO BANCO NÃO É PROVA DE QUE O BYTE AINDA EXISTE.

⚠️ **E eu tinha escrito um teste que exigia esse comportamento**, chamando-lhe «limite
conhecido». Um teste que exige o comportamento errado **impede quem o vem consertar** — e
ainda dá ao defeito um ar de decisão tomada. Não era limite: era defeito com etiqueta.

**Agora `REUSED` exige as cinco provas:** linha existe · resultado igual · `storage_path`
existe · o byte no armazém bate com o `sha256` da linha · e bate com o desta execução.

| situação | estado |
|---|---|
| tudo bate | `REUSED` + `BYTES_CONFERIDOS_NO_ARMAZEM: True` |
| a ficha está lá, o artefato sumiu | **`STORAGE_MISSING`** |
| o byte foi trocado debaixo da ficha | `STORAGE_CONFLICT` |

**Um estado novo, não cinco.** `STORAGE_MISSING` existe porque «o artefato desapareceu» e «a
ficha não entrou» são avarias diferentes, com conserto diferente — dar-lhes o mesmo nome
mandaria o operador ao sítio errado.

E **não se reenvia o byte por conta própria.** Um desaparecimento de evidência regista-se
primeiro; curar em silêncio apagaria o rasto de que houve um buraco.

### 2 · O endereço colapsava identidades que o banco distingue

O caminho era `PAIS/derivados/TIPO/<pai16>-<produtor>-<versão>` — e **não incluía o
`parameters_hash`**. O mesmo PDF a 150 dpi e a 300 dpi são **duas derivações legítimas** pela
`022`, e disputavam **o mesmo endereço**.

> ### SE A IDENTIDADE DO BANCO DIZ QUE SÃO DUAS DERIVAÇÕES,
> ### O ENDEREÇO TEM DE PERMITIR QUE AS DUAS EXISTAM.

```
antes   IT/derivados/TEXT_EXTRACTION/<pai16>-texto-de-pdf-1.txt
agora   IT/derivados/TEXT_EXTRACTION/texto-de-pdf-1-<receita_sha256>.txt
```

O discriminante é o `sha256` **completo** da receita inteira — pai, tipo, produtor, versão,
hash dos parâmetros e posição na série — serializada pela **mesma** função canónica dos
parâmetros. **Não um prefixo de 16 caracteres a fazer de identidade.**

E o `sha256` do **filho** continua fora do caminho, de propósito: se entrasse, um
`DERIVATION_DRIFT` ganharia endereço novo e **deixaria de ser drift** — passaria a ser dois
artefatos calados.

**A identidade da tabela não mudou.** Isto é defeito de *writer*, não de esquema: a `022`
está igual.

### 3 · A ponte para o executor não carregava o pai

A primeira ponte passava a receita e os bytes — e **não o `raw_asset_id`**. O dono ficava sem
saber qual linha de `raw_asset` era o pai daquele PDF. E o meu teste só verificava que o
callback tinha sido chamado, **o que não prova nada**.

> ### UM EXECUTOR FORWARD SEM `RAW_ASSET_ID` REAL NÃO TEM PAI CANÓNICO.

A ponte foi **removida**. No lugar entrou `derivar_um(raw_asset_id, pdf, armazem, memoria)`,
que recebe o pai como **contexto da unidade de trabalho** — quem manda derivar já sabe de que
bruto se trata. O executor continua a não calcular `parent_sha256`, `parameters_hash`,
`sha256` do filho, `derived_at` nem `storage_path`.

**E os dois modos ficam separados:**

```
LEGADO    correr()      → PDFs históricos → JSON → o dono NÃO entra
FORWARD   derivar_um()  → um raw_asset real → o dono canónico
```

O teste é **de ponta a ponta com o dono real**: `raw_asset X` → executor → writer →
`derived_artifact.raw_asset_id = X`, `parent_sha256` = o SHA de X, byte no armazém, metadata
conferida. E com **dois brutos distintos**, para provar que nenhum caminho global troca os
pais.

### 4 · E o país deixou de ser do chamador

O `country` vinha no pedido. Um chamador podia mandar `country="ES"` para um bruto italiano e
pôr o byte a morar no sítio errado. Agora ele é **lido do pai** — do `source_country` da
corrida que o trouxe, por um `join` só de leitura, **sem coluna nova**. Onde o pai não prova,
fica `NAO_SEI`: não se infere.

---

## H · O ESTADO, MARCADO UM A UM

```
DESIGNED       ✅  migration 022 escrita, com o grão e a identidade medidos
IMPLEMENTED    ✅  SQL completo, com travas e comentários
SEMANTICS      ✅  coerência pai-id/pai-sha fechada; grão decidido
WRITER         ✅  guarda/preservar_derivado.py · 50 provas locais
DB_TESTED      ✅  Postgres 16 descartável · 38/38 · run 34255823282
LIVE_APPLIED   ❌  NÃO. Nenhuma migration aplicada em produção
OBSERVED       ❌  NÃO. Nenhuma linha real escreveu-se em lado nenhum

WRITER_READY_FOR_LIVE = SIM
```

**O primeiro produtor deve ser o Golden Path para a frente** — nova corrida, novo `raw_asset`,
novo derivado. **Nunca o legado retroativo.**

## I · O QUE FALTA PARA LIGAR O GOLDEN PATH

1. Aplicar a `022` em produção — **missão própria, com autorização explícita**.
2. Uma corrida italiana real a passar pelo dono da escrita (`guarda/preservar_coleta.py`),
   criando `collection_run` + `raw_asset` de verdade.
3. Só então o derivado tem pai, e a chave estrangeira tem em que assentar.

**Por esta ordem, e nenhum passo antes do anterior.**
