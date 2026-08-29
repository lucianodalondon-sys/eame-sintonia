# REGRA DE COLETA EXTERNA — regra operacional permanente

**Vigora a partir de:** 2026-08-29 · aplicável a **todas** as missões de coleta do SINTONIA EAME.

> **Esta regra não recomeça a epistemologia do zero.** O que já foi provado construindo o
> SINTONIA continua valendo e é referenciado, não reescrito:
>
> | assunto | onde já está |
> |---|---|
> | identidade de origem, papel declarado, `PUBLIC_TECHNICAL_VOICE` | [`MODELO-DE-IDENTIDADE-EAME.md`](MODELO-DE-IDENTIDADE-EAME.md) |
> | o que conta como mudança e o que é só nova versão | [`REGUA-DE-CHANGE-EVENT-EAME.md`](REGUA-DE-CHANGE-EVENT-EAME.md) |
> | quando um sinal vira `WATCH`, `INVESTIGATE` ou `ALERT` | [`REGUA-DE-ALERTA-EAME.md`](REGUA-DE-ALERTA-EAME.md) |
> | chave Apify descartável: autonomia e limites | [`POLITICA-DE-CHAVES-DESCARTAVEIS.md`](POLITICA-DE-CHAVES-DESCARTAVEIS.md) |
> | estados de saúde de fonte e cobertura | `scripts/source_health.py` · `scripts/coverage.py` |
> | contrato de campos por vídeo, em código | `scripts/voz.py` |

---

## 1 · PRIORIDADE DE COLETA

Para inteligência técnica e agronômica externa:

| # | camada |
|---|---|
| 1 | **VIDEO / TRANSCRIPT** |
| 2 | **RESEARCHERS / SCIENCE** |
| 3 | **LINKEDIN PUBLIC** |
| 4 | INSTITUTIONS / TECHNICAL ORGANIZATIONS |
| 5 | COOPERATIVES / TECHNICAL VOICES / PRODUCERS |
| 6 | COMPETITOR COMMUNICATION |
| 7 | TECHNICAL MEDIA |
| 8 | INSTAGRAM / SHORT-FORM — só quando acrescentar sinal |

Nenhuma missão precisa coletar tudo. Mas **VÍDEO, PESQUISADORES e LINKEDIN não são
acessórios** e não podem ser esquecidos.

Vídeo começa por **YouTube**; depois LinkedIn Video e Instagram Reels quando for tecnicamente
útil.

## 2 · POR QUE VÍDEO PRIMEIRO

Vídeo entrega o que nenhuma outra camada entrega: **fala técnica longa**. Demonstração de
campo, webinar, entrevista, dia de campo, congresso, apresentação de pesquisador, técnico
explicando o problema, e a **linguagem que o próprio setor usa**.

**Medido na Espanha:** 15 vídeos entregaram **705.149 caracteres** de fala técnica. Nenhuma
outra camada da rodada chegou perto disso por unidade de custo.

## 3 · O CONTRATO DE CAMPOS POR VÍDEO

A lista vive em **`scripts/voz.py`**, em `CAMPOS_VIDEO` — **32 campos**. Ela está em código
para que o próximo país não a redigite e não a encolha em silêncio.

```
SOURCE_ID · ORIGIN_ID · CHANNEL_ID · CONTENT_ID · PLATFORM · EXTERNAL_ID · URL
TITLE · DESCRIPTION · PUBLICATION_DATE · CAPTURE_DATE · CHANNEL_NAME
DECLARED_AUTHOR · DECLARED_ROLE · ORGANIZATION · COUNTRY · LANGUAGE
DURATION · VIEWS · LIKES · COMMENTS_COUNT
TRANSCRIPT · TRANSCRIPT_LANGUAGE · CAPTION_SOURCE
CROP · ISSUE · PRODUCT · MOLECULE
FACT_LOCATION · SOURCE_LOCATION · RUN_ID · EVIDENCE_PATH
```

**Campo ausente vira `NÃO SEI`. Nunca some.** Um campo que desaparece do registro é
indistinguível de um campo que nunca existiu — e `registro_vazio()` garante que todas as 32
chaves existam sempre.

**Cobertura por campo é obrigatória.** `voz.cobertura()` conta quantos registros declaram cada
um. É isso que impede a lista de encolher sem ninguém notar.

## 4 · TRANSCRIÇÃO É MATÉRIA-PRIMA

`TRANSCRIPT_ORIGINAL` e `TRANSLATION` são **campos separados**. Tradução nunca substitui
evidência original. `TRANSLATION: null` significa **não traduzido**, nunca "igual ao original".

Registrar **como** a transcrição foi obtida, em `CAPTION_SOURCE`.

**Transcrição indisponível ≠ vídeo sem conteúdo técnico.** Pedida e vazia fica
`REQUESTED_EMPTY` — um estado, não uma ausência.

## 5 · NEM TODO VÍDEO É SINAL

Tipos em `voz.TIPOS_VIDEO`: `RESEARCH_TALK` · `TECHNICAL_WEBINAR` · `FIELD_DAY` ·
`FIELD_OBSERVATION` · `COOPERATIVE_CONTENT` · `TECHNICAL_ADVISER` · `PRODUCER_VOICE` ·
`COMPETITOR_TECHNICAL` · `PRODUCT_DEMO` · `CONFERENCE` · `MEDIA` · `PROMOTIONAL` · `OTHER`.

**O papel da origem nunca sai do conteúdo do vídeo.** Um vídeo técnico num canal promocional
continua sendo um canal promocional. Assunto (`CROP`, `ISSUE`, `MOLECULE`) pode sair do texto;
**identidade não**.

## 6 · PESQUISADORES SÃO CAMADA CENTRAL

A cadeia a construir:

```
PERSON → INSTITUTION → SCIENCE → CROP → ISSUE → PUBLIC VOICE → VIDEO / LINKEDIN / EVENTS
```

Buscar por pesquisador: ORCID · OpenAlex · perfil institucional · papers · projetos ·
aparições em congresso · YouTube · webinars · entrevistas · LinkedIn público.

**Não criar authority score.** Recorrência não é autoridade, e um número que ordena pessoas
seria exatamente a "palavra maior que o dado" que o repositório recusa em todo lugar.

## 7 · DOCUMENTOS CIENTÍFICOS, NÃO SÓ NOMES

Campos por documento: `DOCUMENT_ID` · `TITLE` · `AUTHORS` · `YEAR` · `DATE` · `DOI` ·
`INSTITUTION` · `CROP` · `ISSUE` · `MOLECULE` · `COUNTRY` · `REGION_OF_STUDY` ·
`DOCUMENT_TYPE` · `SOURCE_ID` · `URL` · `EVIDENCE_PATH`.

**Science não é voz de mercado. Mas Science × Voice é cruzamento de primeira ordem.**

## 8 · LINKEDIN: IDENTIDADE PRIMEIRO, CONTEÚDO DEPOIS

**PERSON/ORG primeiro. POST depois.** Nunca criar identidade a partir do texto de um post.

Na Espanha isso virou dois arquivos separados de propósito:
`ES-VOICE-LINKEDIN.json` (**identidade**) e `ES-T8-002-posts.json` (**conteúdo**).

## 9 · IDENTIDADE — o que nunca se inventa

**NÃO** inventar handle · **NÃO** transformar nome em endereço · **NÃO** inferir URL ·
**NÃO** inferir identidade por similaridade textual.

```
NAME ≠ HANDLE ≠ PROFILE ≠ PERSON ≠ ORGANIZATION
```

**Medido duas vezes, no mesmo repositório:**
- `linkedin.com/company/adama/` devolve uma **incorporadora imobiliária romena**. Casar nome
  entrega a entidade errada.
- Três funcionários — FMC, UPL, BASF — foram contados como se fossem o canal da empresa,
  porque o *headline* deles nomeia o empregador. **O headline nomeia o empregador; não
  transforma o post em comunicação da empresa.**

**Mesma pessoa em várias plataformas = UMA ORIGEM.**
`ORIGIN_ID`, `CHANNEL_ID` e `CONTENT_ID` são entidades distintas.

## 10 · ORIGEM ≠ CONTEÚDO

Uma pessoa com 50 vídeos é **1 ORIGIN e 50 CONTENTS**.
**Medido:** 157 canais publicaram 252 vídeos. As duas contagens nunca se somam nem se trocam.

Uma release republicada em site + LinkedIn + YouTube + Instagram **não vira quatro evidências
independentes**. Separar `ORIGINAL` · `RESHARE` · `SYNDICATED` · `UNKNOWN`.

**O que não pode ser provado fica `UNKNOWN` — nunca `ORIGINAL` por omissão.**

## 11 · DEDUPE É ESTRUTURAL

Chave: `PLATFORM + EXTERNAL_ID` · `VIDEO_ID` · `POST_ID` · `COMMENT_ID`.

**Texto semelhante não é chave de dedupe.** Dois comentários com texto idêntico podem ser dois
comentários reais.

**O custo de não ter isso foi medido:** dos 472 posts do corpus espanhol, **100 eram o mesmo
`POST_ID`** devolvido por consultas diferentes. Quase metade dos posts de indústria era
duplicata contada como evidência independente. O número publicado caiu de **54 para 26**.

## 12 · COMENTÁRIOS

Úteis, mas **não coletar volume por volume**.

Preservar: `COMMENT_ID` · `VIDEO_ID` · `AUTHOR_REFERENCE` · `DATE` · `TEXT` · `LIKE_COUNT` ·
`PARENT_COMMENT_ID` · `SOURCE_ID` · `RUN_ID`.

Classificar só quando há conteúdo real: `FIELD_OBSERVATION` · `TECHNICAL_QUESTION` ·
`PRODUCT_QUESTION` · `PROBLEM_REPORT` · `TECHNICAL_DISCUSSION`.

**Comentário genérico não vira inteligência.**

## 13 · SEM FICHA DE ORIGEM, NÃO PROMOVE

Antes de subir para a camada analítica, a origem precisa de evidência suficiente de
identidade. Sem ela: `ORIGIN_STATUS = NÃO SEI / UNVERIFIED`.

**Não inventar pessoa nem organização para completar a tabela.**

## 14 · PROVENANCE FIRST

Manter: `RUN_ID` · `SOURCE_ID` · `CAPTURE_DATE` · `EXTERNAL_ID` · `RAW_EVIDENCE` ·
`NORMALIZED_RECORD`. **RAW nunca é substituído pelo normalizado.**

### A exceção que a rota paga cria — e que muda a decisão D-003

A decisão **D-003** mantém `data/raw/` fora do git porque o bruto é um **cache reproduzível**:
perdeu-se, roda-se a cadeia de novo (`scripts/chain.py`).

**Para rota paga com chave descartável essa premissa é falsa.** A chave morre quando o crédito
acaba, e a rota **não pode ser replicada**. Ou a evidência é versionada, ou ela se perde.

**Regra:** coleta por rota não replicável entra em `data/samples/`, que é versionado — registro
normalizado **e** transcrição. `data/raw/` continua sendo cache para o que a cadeia refaz.

## 15 · FAIL CLOSED

| não é | |
|---|---|
| falha de leitura | ≠ zero |
| falha de scraping | ≠ ausência de conteúdo |
| **403** | ≠ empresa silenciosa |
| nenhum resultado de Actor | ≠ nenhum resultado na plataforma |
| transcript indisponível | ≠ vídeo sem conteúdo técnico |
| **HTTP 200** | ≠ fonte viva — medido: 6 rotas devolveram 200 com zero `<item>` |
| certificado que não valida | ≠ motivo para desligar verificação — é **estado da fonte** |

Estados: `PROVED` · `PARTIAL` · `NOT_REACHED` · `NOT_TESTED` · `FAILED_WITH_REASON` · `NÃO SEI`.

## 16 · COLETA NÃO É INTELIGÊNCIA

10.000 vídeos coletados não são sucesso. O alvo é:

> **QUEM** disse **O QUÊ** sobre **QUE CULTURA** e **QUE PROBLEMA**, **ONDE**, **QUANDO**,
> **DE QUE PAPEL** e **COM QUE EVIDÊNCIA.**

E então cruzar com FIELD · SCIENCE · REGULATION · CROP SCALE · COMPETITOR COMMUNICATION ·
resposta legítima da ADAMA.

**Corolário medido:** 67 vozes técnicas verificadas, das quais **16** falam de olivar. O número
acionável é o segundo. **Quantidade não é representatividade.**

## 17 · VIDEO × SCIENCE

Um pesquisador em paper + congresso + webinar no YouTube **não são três pessoas**. É **uma
origem com três evidências**.

Rota forte: `SCIENCE → RESEARCHER → PUBLIC EXPLANATION`.

## 18 · VIDEO × FIELD

Perguntar sempre, com um dos quatro estados: **`LEADS` · `COINCIDES` · `LAGS` ·
`NO_RELIABLE_SIGNAL`.**

**Não fabricar antecipação.** Na Espanha, duas camadas concordaram com o índice de exposição
(ρ 0,96 e 0,94) e mesmo assim o estado correto é **`COINCIDES`**: as medidas são do mesmo
período. **Concordância de ordem não é antecedência.**

## 19 · VIDEO × COMPETITOR

Revela tópicos ativados, culturas enfatizadas, produtos apresentados, claims técnicos, eventos,
timing e geografia quando explicitada.

```
communication ≠ sales · communication ≠ market share · communication ≠ demand
```

E o denominador precisa aparecer: "posts que casaram com as nossas consultas" **nunca** é
"tudo que a empresa publica". Sem isso, não existe *share of voice*.

## 20 · DATA CLOCK POR CANAL

Todo canal que sobreviver ao discovery recebe baseline — **por canal, não só por camada**.

Eventos a detectar: `NEW_VIDEO` · `NEW_TOPIC` · `NEW_RESEARCHER_ACTIVITY` ·
`NEW_COMPETITOR_CLAIM` · `NEW_TECHNICAL_DISCUSSION` · `NEW_PRODUCT_MENTION` ·
`NEW_REGION_MENTION`.

Primeira observação é **`BASELINE_ESTABLISHED`**. **Nunca `NO_CHANGE`** — não se pode declarar
ausência de mudança contra um baseline que não existia.

## 21 · APIFY — comparar antes de escalar

Fluxo obrigatório (da política de chaves): `DISCOVERY → TESTE PEQUENO → MEDIÇÃO → ESCOLHA →
ESCALA CONTROLADA`.

**Vídeo entra na comparação.** Não gastar tudo em LinkedIn e Instagram e lembrar do vídeo
depois.

Comparar Actors em **cinco dimensões**: custo · qualidade · **identidade** · transcript ·
atualização.

**A dimensão que decide é identidade.** Medido: o Instagram entregou 39 itens agronômicos em 60
— e foi reprovado, porque **24 de 32 contas não declaram país** e `#repilo` está inteiramente
ocupada por um homônimo comercial britânico. **Volume não compensa identidade ausente.**

## 22 · O ALVO POR PAÍS

Por país, quando o universo sustentar: 20+ pesquisadores verificáveis · 20+ vozes técnicas
públicas · corpus científico · instituições de pesquisa e extensão · YouTube técnico em
profundidade · LinkedIn público · cooperativas e associações · comunicação de concorrente ·
mídia técnica · Instagram **só se agregar sinal**.

**Vídeo não fica para depois.**

## 23 · PRINCÍPIO FINAL

**O SINTONIA não é um coletor de posts.**

Ele transforma VIDEO + SCIENCE + PEOPLE + INSTITUTIONS + FIELD + REGULATION + COMPETITOR
COMMUNICATION em **contexto conectado**, para responder:

> O que está acontecendo · quem está falando sobre isso · quem está estudando isso · onde isso
> importa · o que os concorrentes estão fazendo publicamente · **e por que a ADAMA deveria
> investigar agora.**
