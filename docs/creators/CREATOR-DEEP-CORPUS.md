# ACERVO PROFUNDO DO CREATOR — primeiro lote

`DATASET_OWNER = CREATOR_CONTENT_CORPUS_EAME` · referência **2026-08-30** ·
`APIFY_RUNS = 17` · `ITEMS_RAW = 641` · `COST_USD = 0,6183` · bruto preservado em
**17 de 17** execuções.

Artefatos: [`CORPUS-UNIVERSE.json`](../../data/samples/CREATOR-CONTENT-CORPUS-EAME/CORPUS-UNIVERSE.json)
· [`CORPUS-MATERIALS.json`](../../data/samples/CREATOR-CONTENT-CORPUS-EAME/CORPUS-MATERIALS.json)
· [`CORPUS-OBSERVATIONS.json`](../../data/samples/CREATOR-CONTENT-CORPUS-EAME/CORPUS-OBSERVATIONS.json)
· [`CORPUS-COMMENTS.json`](../../data/samples/CREATOR-CONTENT-CORPUS-EAME/CORPUS-COMMENTS.json)
· [`CREATOR-CORPUS-FICHES.json`](../../data/samples/CREATOR-CONTENT-CORPUS-EAME/CREATOR-CORPUS-FICHES.json)
· [`CORPUS-DELIVERY.json`](../../data/samples/CREATOR-CONTENT-CORPUS-EAME/CORPUS-DELIVERY.json)
· código em [`creator_corpus.py`](../../scripts/creator_corpus.py),
[`creator_corpus_coleta.py`](../../scripts/creator_corpus_coleta.py),
[`creator_corpus_analise.py`](../../scripts/creator_corpus_analise.py).

O **Creator Map continua congelado**. Nada aqui reabriu discovery, mudou os 8
`PERSON_CREATOR_ACTIVATION_READY`, mudou os 2 `FARM_BUSINESS_PARTNER_READY`,
abriu hub ou ampliou país. O mapa continua dono de `IDENTITY`, `ROLE` e
`ACTIVATION_STATE`; esta missão é dona do MATERIAL, das OBSERVAÇÕES, da AMOSTRA
DE AUDIÊNCIA e da EVIDÊNCIA DE RELAÇÃO COM MARCA.

---

## Quatro erros medidos no caminho — e o que cada um teria publicado

Ficam registrados porque os quatro produziriam número bonito e falso.

**1 · "mais", em francês, quer dizer "mas".** O léxico de cultura casava `mais`
com MILHO. Onze materiais saíram como milho; **dez** eram o canal francês
usando a conjunção — um deles falando de azoto em cereal. A busca por palavra
inteira estava certa; a palavra é que era outra. Depois da correção: **2**. Um
relatório com o erro teria posto milho num canal de cereais.

**2 · "bio" era o nome da empresa.** Vinte materiais casaram `bio` como sinal de
manejo biológico; **catorze** eram a Bio Campojoyma dizendo o próprio nome.
Nome de marca não é prática agronômica. Depois da correção, BIOLOGICALS caiu de
25 para 10.

**3 · hashtag de cultura virava manejo de cultura.** `CROP_MANAGEMENT` era dado
a todo material que nomeasse uma cultura. Resultado: **50 de 50** para uma conta
cuja legenda inteira era *"Pequeña avería #viña #viticultura"*. Como
`D_TECHNICAL_DEPTH` conta `CROP_MANAGEMENT`, isso publicaria **"50 materiais
técnicos"** para quem tinha zero. Agora exige cultura **mais** um sinal de
manejo: o mesmo criador caiu de 50 para **6**.

**4 · o contrato do ator estava vazio e se apresentava como lido.** A fase
grátis leu o `INPUT SCHEMA` no lugar errado e devolveu `campos=0` nos quatro
atores — sem erro nenhum. Um contrato vazio com cara de contrato lido é
exatamente o defeito que essa fase existe para não ter. O schema vive na
**build**, não no ator: são duas chamadas. Corrigido, a fase agora também
confere os campos que as fases **pagas** pretendem enviar. Nenhum seria
descartado em silêncio.

---

## A · 8 pessoas tentadas · B · 2 empresas tentadas

Os 10 do artefato congelado, sem acréscimo nem corte. Mas o mapa e o acervo
perguntam coisas diferentes, e uma delas tem um **não** conhecido:

> **PC-03 · Gilles vk, agricultor do Loiret.** Identidade PROVADA e
> `ACTIVATION_READY` no Creator Map. O `PUBLIC_CHANNEL` registrado, porém, é uma
> **URL de busca** do YouTube (`/results?search_query=`), não um canal. Buscar
> não é ter endereço: coletar de uma página de resultados atribuiria a ele o que
> o buscador devolvesse. Ele está **contado no universo e fora da coleta**, com
> `CHANNEL_STATE = CHANNEL_NOT_RESOLVED`. `N = 0` aqui não significa "não
> publica" — significa que ninguém sabe ainda onde ele publica.

**9 canais coletáveis** · **1 não resolvido**.

## C–E · o que foi coletado

**442 materiais.** Instagram **399** · YouTube **43**.

| janela | materiais |
|---|---:|
| `LAST_30D` | 116 |
| `LAST_90D` | 164 |
| `LAST_180D` | 61 |
| `LAST_365D` | 48 |
| `OLDER_THAN_365D` | 53 |

As janelas ficam **separadas**. Os 53 materiais com mais de um ano provam
histórico e não entram em atividade atual — somá-los produziria um canal
"ativo" feito de conteúdo de 2024.

Alvo de profundidade: **50 por canal**. Oito canais chegaram a 50; um chegou a
49 e outro a 43 — o N real está em cada ficha. **N=30 continua sendo alvo, não
régua**: `CONTENT_RATE_MIN_N` é `PROPOSAL_ONLY` no congelamento, e por isso
`FIELD_CONTENT_RATE` e `TECHNICAL_CONTENT_RATE` saem dos artefatos como
`WITHHELD_PENDING_ARBITRATION`, com contagem e denominador à vista, mas **sem a
divisão**.

## F · culturas vistas no acervo

`GRAPEVINE` 53 · `PROTECTED_HORTICULTURE` 50 · `PISTACHIO` 48 · `TOMATO` 44 ·
`OLIVE` 37 · `PEPPER` 17 · `WHEAT` 13 · `RAPESEED` 9 · `BARLEY` 6 ·
`SUNFLOWER` 5 · `MAIZE` 2 · `CAROB` 2.

Isto é `CROPS_OBSERVED_IN_CORPUS` — campo **próprio**. `QUERY_CROP !=
PROVED_CROP`: nada aqui reescreve o `CROPS_PROVED` do Creator Map. Vale um
registro: **@oliverio_rodfer** aparece com 50 materiais de vinha, e o mapa o
trazia por outra cultura. Isso **não** reabre a Itália viticultura, que continua
`NOT_READY` — é Espanha, e é observação de conteúdo, não prova de cultura.

## G · assuntos vistos

`PEST` 16 · `WEED` 6 · `DISEASE` 5. Em 442 materiais, **27** nomeiam um problema
fitossanitário. É pouco, e é o número real.

## H–J · campo, técnico e proteção de cultivos

| entidade | N | campo | técnico | proteção | proteção de cultivos |
|---|---:|---:|---:|---:|---|
| PC-01 `@gomierofarm` | 50 | 2 | 0 | 0 | `NOT_OBSERVED_IN_CORPUS` |
| PC-02 `@chaineagricole` | 43 | 20 | 20 | 2 | `OBSERVED` |
| PC-03 Gilles vk | 0 | 0 | 0 | 0 | `NOT_MEASURED` |
| PC-04 `@huerto_ecologico.marc` | 50 | 13 | 15 | 10 | `OBSERVED` |
| PC-05 `@germanagrolife` | 50 | 17 | 14 | 8 | `OBSERVED` |
| PC-06 `@agrosamanta_` | 50 | 4 | 4 | 3 | `OBSERVED` |
| PC-07 `@chicurri_agro` | 50 | 31 | 26 | 2 | `OBSERVED` |
| PC-08 `@oliverio_rodfer` | 50 | 6 | 6 | 0 | `NOT_OBSERVED_IN_CORPUS` |
| FB-09 `@biocampojoyma` | 49 | 4 | 9 | 8 | `OBSERVED` |
| FB-10 `@terruzapistachos` | 50 | 12 | 12 | 6 | `OBSERVED` |

`NOT_MEASURED` (PC-03) e `NOT_OBSERVED_IN_CORPUS` (PC-01, PC-08) são estados
**diferentes**: o primeiro é "não houve o que ler", o segundo é "foi lido e não
apareceu". Nenhum dos dois é "essa pessoa não fala disso".

## K–M · audiência

**199 comentários** amostrados, dos materiais mais relevantes de cada canal.

`OPINION` 133 · `QUESTION` 28 · `NOISE` 25 · `TECHNICAL_REPLY` 6 ·
`FIRST_PERSON_FIELD_REPORT` 4 · `TECHNICAL_QUESTION` **3**.

As três perguntas técnicas estão todas em `@huerto_ecologico.marc`, e uma delas
é literalmente um produtor descrevendo o próprio problema e perguntando se
enxofre corrige. **`COMMENTER != FARMER`**: isso caracteriza a conversa pública
do canal e **não** é incidência de campo. Nenhum campo da ficha promove
comentarista a produtor.

`AUDIENCE_FACING` sai `GENERAL_AG` em sete canais, `MIXED` em um e `NOT_KNOWN`
em dois. Profissão de seguidor **não foi inferida**.

## N–P · marcas, concorrentes e patrocínio

**5 eventos de marca**, todos no degrau mais baixo:

| entidade | marca | degrau | data |
|---|---|---|---|
| PC-07 `@chicurri_agro` | SYNGENTA | `BRAND_MENTION` | 2025-12-11 · 2026-01-08 · 2026-01-24 · 2026-01-29 |
| PC-05 `@germanagrolife` | BASF | `BRAND_MENTION` | 2026-06-21 |

Nenhum subiu a `PAID_PARTNERSHIP_PROVED` nem a
`COMPETITOR_PRODUCT_ACTIVATION_PROVED`. **Menção não é parceria paga**, e a
escada de sete degraus só sobe com evidência do próprio degrau.

`SPONSORED_CONTENT` aparece em **12** materiais — detectado por **rótulo**
(`#adv`, `#publi`, *"in collaborazione con"*), nunca por texto elogioso. Note-se
que os patrocínios rotulados que apareceram são de **fertilizante, maquinaria e
bico de pulverização** — não de defensivo.

`COMPETITOR_HISTORY` sai `OBSERVED` em dois canais e
**`NOT_OBSERVED_IN_CORPUS`** nos demais. O escopo está dentro do nome de
propósito: o corpus é uma amostra do que é público, e **`NOT_OBSERVED` nunca
significa `NO_RELATIONSHIP`**.

## Q · contexto ADAMA local

**`NOT_KNOWN` nos dez.** O cruzamento só é lícito com portfólio ADAMA local
**provado**, e esse artefato não está visível nesta branch. Isso é ausência de
cruzamento, não ausência de contexto — e não significa nem *"a ADAMA deve usar
esta pessoa"* nem *"o produto X deve ser anunciado com ela"*.

## R–S · usos possíveis e fichas

**10 fichas enriquecidas**, cada uma com os oito eixos de relevância lado a
lado. **Não existe `ADAMA_RELEVANCE_SCORE`** e o artefato registra a métrica
como proibida: somar os oito eixos produziria um número que esconde qual eixo
está vazio — e o eixo vazio é a informação.

Os `POSSIBLE_MARKETING_USE_CASES` (pessoa) e `POSSIBLE_PARTNERSHIP_USE_CASES`
(empresa) são **hipóteses de avaliação**, não recomendação de contratação. A
pergunta das duas empresas é outra e está escrita como outra: não *"que conteúdo
ela faz"*, mas *"o que essa fazenda permite"* — `FIELD_VISIT`, `TECHNICAL_DEMO`,
`CASE_STUDY`, `FIELD_TRIAL_CONTEXT`. **Empresa não é creator.**

## T–U · convergência e Meta

**19 recortes** `COUNTRY × CROP` no índice de convergência. Um caso pode
perguntar *"há voz pública neste contexto?"* e receber quem, por que é
relevante, do que fala, material recente, histórico de concorrente e contato.
Recorte ausente significa que **ninguém perguntou**, não que não há voz.

Chaves de junção prontas para a missão Meta: `PERSON_ID`, `ENTITY_ID`,
`HANDLE`, `BRAND`, `COUNTRY`, `CROP`, `OBSERVED_AT`. Se a Meta encontrar uma
destas pessoas num anúncio, isso vira `CREATOR_APPEARANCE_OBSERVED`;
`PAID_CREATOR_RELATION` só sobe a `PROVED` com prova adicional, e **não é
antecipado aqui**.

## V · execuções, itens e custo

17 execuções · 641 itens brutos · **US$ 0,6183** · 15 `SUCCESS`, 2 `PARTIAL`.

As duas `PARTIAL` não são falha silenciosa: a plataforma ainda estava com o
estado `READY` quando o conjunto de dados já tinha itens, e o coletor preferiu
registrar `PARTIAL` com 49 e 43 itens a chamar de sucesso uma leitura feita no
meio da execução. Bruto preservado em **17 de 17**.

## W · o que continua NÃO SABIDO

- **Onde Gilles vk publica.** Sem canal resolvido, não há acervo — e nenhuma
  conclusão sobre ele pode ser tirada deste relatório.
- **Só TEXTO foi lido.** Imagem e vídeo não foram analisados. Um material sem
  legenda não foi classificado por conteúdo visual, e **imagem sozinha não prova
  cultura**.
- **O léxico é forte em espanhol, mediano em francês e fraco em italiano.**
  `@gomierofarm` tem 33 materiais com texto farto e ainda assim 43 caíram em
  `OTHER`. Isso mede o léxico, não o criador — e é a correção mais barata
  disponível para a próxima rodada.
- **`@oliverio_rodfer` escreve por hashtag.** 17 legendas são só hashtag/emoji e
  33 são curtas. O silêncio é da legenda, não da pessoa.
- **Região do fato não foi extraída do texto.** A região das fichas é a herdada
  do Creator Map. `COUNTRY_OF_FACT` só sai de `NOT_KNOWN` quando o texto nomeia
  o lugar, e material com dois países nomeados fica ambíguo em vez de escolher.
- **A amostra de comentários é fina em quatro canais** (1 a 3 materiais), porque
  poucos materiais tinham sinal técnico para priorizar.
- **Nenhuma taxa de conteúdo foi publicada**, por decisão e não por falta de
  dado.

## X · handoff para inteligência

`OPTIONAL_REFRESH_INPUT = READY`. Esta missão **não bloqueia** nada: EARLY
SIGNAL TERRITORIAL, META COMPETITOR e COMPETITOR FORESIGHT seguem sem depender
dela.

**Supabase: nenhuma migração aplicada.** O modelo persistente fica proposto e
não criado, porque criar tabela agora produziria um segundo dono de campo antes
da arbitragem. A forma proposta é direta e reflete a separação que já existe nos
arquivos:

| tabela proposta | chave | dona de |
|---|---|---|
| `material_do_creator` | `CONTENT_ID` | material bruto normalizado, janela, métricas públicas |
| `observacao_do_material` | `CONTENT_ID` | tipos, cultura vista, assunto, país do fato |
| `comentario_amostrado` | `COMMENT_ID` | amostra de audiência e sua classe |
| `evento_de_marca` | `CONTENT_ID` + `BRAND` | o degrau da escada, com data e URL |
| `ficha_de_relevancia` | `ENTITY_ID` | os oito eixos, sem score |

`ENTITY_ID` e `PERSON_ID` apontam para o Creator Map; **nenhuma dessas tabelas
escreve `IDENTITY`, `ROLE` ou `ACTIVATION_STATE`**.

O acervo parou nos 10 perfis. **Nenhum creator novo foi aberto.**

---

# SELO DA V1 — validação semântica e congelamento

Artefato: [`CORPUS-V1-SEAL.json`](../../data/samples/CREATOR-CONTENT-CORPUS-EAME/CORPUS-V1-SEAL.json)
· código em [`creator_corpus_selo.py`](../../scripts/creator_corpus_selo.py).
**Zero coleta, zero Apify, zero custo** — só leitura do que já estava preservado,
mais leitura READ-ONLY de artefatos canônicos de outras branches por `git show`,
sem copiar arquivo e sem trocar de branch.

## 1 · a janela real: 442 não é 280

O número que a missão pede não é o número que a coleta devolveu.

| | itens |
|---|---:|
| `ALL_ITEMS_COLLECTED` | **442** |
| `LAST_90D_CORPUS` | **280** |
| `ITEMS_91_180D` | 62 |
| `ITEMS_OLDER_THAN_180D` | 100 |

Nenhum item antigo foi descartado para o número caber. Os 100 itens com mais de
180 dias **provam histórico** e continuam no acervo, separados.

| alvo | tipo | tent. | sucesso | itens | 90d | 91–180d | >180d | mais antigo → mais novo |
|---|---|---:|---:|---:|---:|---:|---:|---|
| PC-01 `@gomierofarm` | pessoa | 1 | 1 | 50 | **50** | 0 | 0 | 2026-06-08 → 2026-08-24 |
| PC-02 `@chaineagricole` | pessoa | 1 | 1 | 43 | **5** | 2 | 36 | 2023-09-02 → 2026-08-04 |
| PC-03 Gilles vk | pessoa | **0** | 0 | 0 | 0 | 0 | 0 | — |
| PC-04 `@huerto_ecologico.marc` | pessoa | 1 | 1 | 50 | **32** | 16 | 2 | 2024-02-07 → 2026-08-30 |
| PC-05 `@germanagrolife` | pessoa | 1 | 1 | 50 | **50** | 0 | 0 | 2026-06-04 → 2026-08-29 |
| PC-06 `@agrosamanta_` | pessoa | 1 | 1 | 50 | **28** | 22 | 0 | 2026-04-09 → 2026-08-27 |
| PC-07 `@chicurri_agro` | pessoa | 1 | 1 | 50 | **8** | 10 | 32 | 2025-01-08 → 2026-08-25 |
| PC-08 `@oliverio_rodfer` | pessoa | 1 | 1 | 50 | **50** | 0 | 0 | 2026-07-20 → 2026-08-28 |
| FB-09 `@biocampojoyma` | empresa | 1 | 1 | 49 | **7** | 12 | 30 | 2025-01-21 → 2026-07-31 |
| FB-10 `@terruzapistachos` | empresa | 1 | 1 | 50 | **50** | 0 | 0 | 2026-07-09 → 2026-08-30 |

PC-03 conta **0 canais tentados**, não uma tentativa falhada: não havia endereço
para tentar. Quatro alvos (PC-02, PC-04 parcialmente, PC-07, FB-09) só alcançam
o alvo de 30 itens **somando histórico**; dentro de `LAST_90D` eles têm 5, 8 e 7.
Isso está escrito em `EXACT_LIMITATION` de cada um.

## 2 · identidade dos canais usados

**9 `PROVED` · 1 `NOT_APPLICABLE`.** Todo canal que produziu material é
literalmente o `PUBLIC_CHANNEL` do artefato congelado — a coleta não aceita
handle, nome nem busca como entrada. **Nenhum canal descoberto nesta missão foi
usado**, e portanto nenhum material foi atribuído a alguém por semelhança de
nome, avatar, idioma ou tema.

**Um `CORRECTION_CANDIDATE`:** o PC-01 anuncia um canal de YouTube — *"Canale
Gomiero Farm"* — na legenda do próprio Instagram provado. É declaração da
própria conta, e é forte. Continua sendo **apenas candidato**: `USED_IN_THIS_CORPUS
= NO`, `MATERIALS_ATTRIBUTED = 0`. O Creator Map está congelado e não foi
escrito; o candidato fica para a atualização dele.

> Aqui o detector também errou e foi corrigido: a primeira versão aceitava a
> palavra *youtube* como gatilho e devolveu **`y Spotify`** e **`o Spotify.`**
> como candidatos — pedaços da frase *"en YouTube y Spotify"*. Candidato de canal
> que é uma preposição solta não é candidato fraco: é ruído com cara de
> descoberta. Agora exige a palavra CANAL antes do nome.

**PC-03 · Gilles vk** permanece exatamente assim:
`CREATOR_IDENTITY` = conforme o Creator Map · `CONTENT_CHANNEL_PROVED = NO` ·
`CORPUS_ITEMS = 0` · `CORPUS_ZERO_MEANING = NO_PROVED_CONTENT_ROUTE`.
Em nenhum lugar deste relatório está escrito que ele não publica.

## 3 · regressões e cobertura por idioma

Os quatro defeitos viraram teste executável, mais dois:

| regressão | estado |
|---|---|
| `FR_MAIS_NOT_MAIZE_GUARD` | **PASS** |
| `BIO_BRAND_NOT_BIOLOGICAL_GUARD` | **PASS** |
| `HASHTAG_ALONE_NOT_TECHNICAL_MANAGEMENT_GUARD` | **PASS** |
| `HASHTAG_GUARD_STILL_CLASSIFIES` | **PASS** |
| `ACTOR_SCHEMA_ROUTE_GUARD` | **PASS** |
| `NO_RELEVANCE_SCORE` | **PASS** |

A quarta existe porque uma guarda que só sabe dizer *não* passaria com o
classificador desligado: ela exige que cultura **mais** sinal de manejo continue
produzindo `CROP_MANAGEMENT`.

**`CLASSIFICATION_COVERAGE_OBSERVED`** — e não acurácia, porque não há gabarito
humano:

| idioma | itens com texto | classificados | em `OTHER` |
|---|---:|---:|---:|
| ES | 288 | 138 | 150 |
| FR | 43 | 24 | 19 |
| IT | 30 | 6 | 24 |
| ambíguo / não sei | 81 | 10 | 71 |

Abri **12 itens italianos em `OTHER`** à mão. Veredito:
**`ITALIAN_OTHER_CONTAINS_MISSED_RELEVANT_CONTENT`** ·
**`ITALIAN_DICTIONARY_COVERAGE_GAP = PROVED`**. O que escapou: **7 de evento**
(a feira italiana chama-se *Agrishow* e se apresenta como festival; o léxico só
conhece *feria/fiera/jornada*), **3 de maquinaria** (drone, engate rápido, marca
de implemento) e **1 ensaio de campo com fertilizante** (*"campo PROVA"*, com
rótulo `#adv` que também não estava previsto).

**O dicionário italiano não foi expandido.** Expandir até o número ficar bonito
é como se fabrica cobertura falsa. Consequência declarada: toda contagem
temática do PC-01 é **piso, não medida** — ali
`NOT_OBSERVED_IN_MEASURED_CORPUS` significa, em parte, *não-lido*.

## 4 · duplicatas

`WITHIN_PLATFORM_DUPLICATES = 0` · `UNIQUE_ITEMS = 442` (por id estável, não por
texto parecido) · `CROSS_PLATFORM_DUPLICATION = NOT_MEASURED`.

Não existe chave segura ligando um post do Instagram ao mesmo vídeo no YouTube.
Ainda assim, nenhuma contagem agregada aqui pode estar inflada por crosspost
entre plataformas: **PC-02 é YouTube puro e todos os outros são Instagram puro**
no acervo — nenhum alvo tem as duas.

## 5 · comentários

199 preservados como camada própria, agora com papel:
**`UNKNOWN` 198 · `COMPANY` 1**. O papel só sobe de `UNKNOWN` com evidência
escrita **dentro do próprio comentário**; nenhum comentarista virou produtor.

Agregados permitidos, e só esses: `FIELD_VOICE_OBSERVED` (**4** relatos em
primeira pessoa) e `AUDIENCE_QUESTION_OBSERVED` (**31** perguntas, 3 delas
técnicas). Proibidos e ausentes: `INCIDENCE`, `OUTBREAK`, `TREND`.

## 6 · contexto ADAMA local — agora medido, e não em todo lugar

| país | artefato canônico lido (read-only) | estado |
|---|---|---|
| ES | `ES-ADAMA-PORTFOLIO-ROPF.json` · 162 culturas de registros vigentes | **`MEASURED`** |
| FR | `FR-T4-001-adama-crop-target.json` · **TOP-25** de usos autorizados | **`MEASURED_POSITIVE_ONLY`** |
| IT | `IT-ADAMA-CATALOG-V1.json` | **`NOT_MEASURED`** |

O caso italiano é o próprio artefato que responde: ele declara
**`AUTHORIZED_REGULATORY = 0`** — as 622 relações cultura↔produto são `CITED` ou
`ROTATION_ONLY`, e citação em rótulo não é autorização por cultura.

O caso francês é um recorte de exibição: um TOP-25 **prova presença e não prova
ausência**. Dizer *"não há portfólio para esta cultura"* com base nele seria
transformar um recorte em ausência de autorização.

Sobreposição observada, por alvo, via crosswalk explícito:
PC-04 e PC-05 `OLIVE·PEPPER·TOMATO` · FB-09 `MAIZE·PEPPER·TOMATO` ·
PC-06 e PC-08 `TOMATO` · PC-07 `OLIVE` · PC-02 `WHEAT·BARLEY` ·
**FB-10 sem sobreposição** (pistácio não está no registro ADAMA ES) ·
PC-01 `NOT_MEASURED` · PC-03 `MEASURED_FROM_CREATOR_MAP_CROPS_ONLY`, porque a
cultura dele vem do mapa e não do acervo — nenhuma publicação dele foi lida.

Nada disso significa *"a ADAMA deve usar esta pessoa"* nem *"o produto X deve
ser anunciado com ela"*.

## 7 · perfil, não score

Dez perfis com o vocabulário de quatro estados —
`OBSERVED` · `NOT_OBSERVED_IN_MEASURED_CORPUS` · `NOT_MEASURED` ·
`NOT_APPLICABLE` — em COUNTRY, REGION, CROP, ISSUE, FIELD_CONTENT,
TECHNICAL_CONTENT, CROP_PROTECTION, AUDIENCE_TYPE, BRAND_HISTORY,
COMPETITOR_HISTORY, SPONSORED_CONTENT, ACTIVATION_STYLE e LOCAL_ADAMA_CONTEXT.

`ADAMA_RELEVANCE_SCORE`, `CREATOR_SCORE`, `RANKING` e `FOLLOWER_RANK` não
existem, e há uma regressão que **falha** se algum deles aparecer num artefato.

## 8 · freeze

| condição | estado |
|---|---|
| `COLLECTION_WINDOW_RECONCILED` | YES |
| `USED_CHANNEL_IDENTITIES_AUDITED` | YES |
| `FALSE_POSITIVE_REGRESSIONS` | PASS |
| `LANGUAGE_COVERAGE_EXPOSED` | YES |
| `COMMENT_SEMANTICS_GUARDED` | YES |
| `NO_RELEVANCE_SCORE` | YES |

**`CREATOR_DEEP_CORPUS_V1 = FROZEN`** ·
**`OPTIONAL_REFRESH_INPUT = READY_WITH_LIMITATIONS`**

As limitações que viajam junto com o congelamento, e que qualquer uso precisa
respeitar: Gilles sem rota de conteúdo; contexto ADAMA não medido na Itália e só
positivo na França; cobertura italiana **provadamente** incompleta; quatro alvos
que só chegam a profundidade somando histórico; região do fato não extraída do
texto; e só texto lido — imagem e vídeo, não.
