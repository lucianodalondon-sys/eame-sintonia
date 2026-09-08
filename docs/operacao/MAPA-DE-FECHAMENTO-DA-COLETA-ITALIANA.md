# MAPA DE FECHAMENTO DA COLETA ITALIANA

> Medido em 08/09/2026 sobre `claude/collection-foundation-integration-v1`,
> com base em `claude/italia-biblia-integracao-v1` (`45f621c0`).
> Nenhum número aqui veio de memória. Cada um tem o comando que o produz.

---

## PARA QUE SERVE

Até agora a casa trabalhou **por fonte**. Cada fonte nova custava um estudo
novo, ainda quando a estrada era a mesma de outra já provada. 54 fontes
italianas por esse caminho são 54 missões.

    A UNIDADE DE ANÁLISE DEIXA DE SER A FONTE.
    PASSA A SER A CLASSE DE ESTRADA.

Uma fonte nova numa estrada já fechada não é missão — é configuração. Só uma
estrada **nova** justifica um canário novo.

E `COLLECTION_FOUNDATION_CLOSED` **não** significa «coletamos todas as fontes».
Significa: toda classe de estrada necessária tem arquitetura e donos fechados,
ou um blocker escrito. A lei que o segura vive em `leis/fundacao_da_coleta.py`.

---

## A — O CENSO, COM O COMANDO QUE O PRODUZ

`python3 system-map/scripts/censo_da_coleta.py`

| medida | número |
|---|---:|
| ficheiros de código na coleta | 100 |
| pontos de entrada | 82 |
| **executores que saem para fora** | **21** |
| ficheiros sem chamador e fora do CI | 46 |
| gravam no banco | 2 |
| **peças que coordenam mais de um executor** | **0** |

`python3 system-map/scripts/censo_das_estradas_it.py` →
`system-map/data/estradas-it.generated.json`. **54 fontes italianas**, e o que
o catálogo diz sobre a rota delas:

| `ACCESS_METHOD` | fontes |
|---|---:|
| **`NÃO SEI`** (todas as variantes) | **51** |
| rota concreta declarada | 3 |

> Esse 51 é o achado mais importante deste mapa. O catálogo sabe **o que cada
> fonte prova**; não sabe **por onde se chega nela**. A classe de estrada aqui
> não foi lida do catálogo — foi derivada do código que existe e do que já se
> observou.

---

## B — AS CLASSES DE ESTRADA

O vocabulário **não foi inventado**: `leis/social_matriz.py` já declara `CLASSE`
por rota, e as 46 rotas sociais declaradas usam sete nomes. As classes
não-sociais saem do código medido.

### Matriz

| ROUTE_CLASS | FONTES | DISCOVER | FETCH | RAW | RUN | CHECKPOINT | DERIVED | STRUCTURED | ADMISSION | LOCAL | DB | LIVE | OBSERVED | CUSTO | CLOSED |
|---|---:|---|---|---|---|---|---|---|---|:-:|:-:|:-:|:-:|---|:-:|
| **RC-1 · OFFICIAL_HTTP_DOCUMENT** | ~40 | manual/catálogo | `texto_fonte`, `rotulos_baixar`, `gire_mapas` | G-42 | `collection_run` | — | `preservar_derivado` + `executor_texto_de_pdf` | `importar_italia` | `admissao.py` | ✅ | ✅ | ✅ | ✅ | US$ 0 | **SIM** |
| **RC-2 · YOUTUBE_OFFICIAL_API** | 5 canais | `channels.list` | `youtube_oficial` | `social_envelope` → G-42 fwd | `collection_run` | `coleta_checkpoint` | — | `social_persistencia` | — | ✅ | ✅ | ❌ | ✅ API | quota grátis | NÃO |
| **RC-3 · PUBLIC_NATIVE_API** | 3 plat. | `social_rotas` | `social_rotas` | `social_envelope` | — | — | — | — | — | ✅ | ❌ | ❌ | ❌ | US$ 0 | NÃO |
| **RC-4 · SCIENCE_METADATA_API** | 5 | `universo_ciencia_it`, `corpus_pesquisador` | HTTP | — | — | — | — | — | — | ✅ | ❌ | ❌ | parcial | US$ 0 | NÃO |
| **RC-5 · REGULATORY_BULK_IMPORT** | 2 | — (arquivo) | `regulatorio_importar` | — | — | — | — | `registro_regulatorio` | — | ✅ | ✅ | ✅ | ✅ | US$ 0 | **SIM** |
| **RC-6 · PUBLIC_BROWSER** | 0 permitidas | `cdp`/`navegador` | idem | — | — | — | — | — | — | ✅ | ❌ | ❌ | ❌ | máquina local | BLOCKED |
| **RC-7 · LOCAL_SESSION** | 0 permitidas | `navegador` | idem | — | — | — | — | — | — | ✅ | ❌ | ❌ | ❌ | máquina local | BLOCKED |
| **RC-8 · PAID_FALLBACK (Apify)** | 0 permitidas | `apify_pool` | `coletor` | — | `sensor_coleta` | `coleta_checkpoint` | — | — | — | ✅ | ❌ | ✅ ES | US$/run | BLOCKED |
| **RC-9 · GIT_LEDGER (legado)** | 1 piloto | `italy_pilot_collect.mjs` | idem | **Git** | **Git** | **Git** | — | — | — | ✅ | ❌ | — | ✅ | US$ 0 | **NÃO — dívida** |

**9 classes · 2 CLOSED · 4 OBSERVED · 3 DB_TESTED · 3 BLOCKED · 1 dívida.**

---

## C — A ESTRADA JÁ FECHADA, E QUANTAS ELA CARREGA

**RC-1** é a estrada que a Bíblia provou ponto a ponto com o canário italiano:

```
HTTP → RAW → Storage → raw_asset → executor de PDF → derived_artifact
```

Ela tem os cinco donos e todos únicos, e foi observada ao vivo (`0feb4967`,
«o primeiro derivado italiano nasceu de uma captura nova»).

    UMA FONTE NOVA NESTA ESTRADA NÃO PRECISA DE CANÁRIO NOVO.

Das 54 fontes, as que o catálogo descreve como boletim, PDF periódico,
documento oficial, CSV direto ou site institucional são **operacionalmente
equivalentes** a ARPAV: **cerca de 40**, ~74% do catálogo. Elas não precisam de
estudo — precisam de configuração e de um `SOURCE_ID`.

> O número é aproximado **de propósito**: 51 fontes têm `ACCESS_METHOD = NÃO
> SEI`, e transformar «NÃO SEI» num número exato seria inventar. Fechar essa
> classificação é o gap G-1 abaixo.

---

## D — SOCIAL

| plataforma | capabilities permitidas | estado |
|---|---:|---|
| YouTube | 4 | **API OBSERVED** (corrida 34258433872) · persistência **DB_TESTED**, não LIVE |
| Mastodon | 4 | rota livre, `LOCAL_TESTED`, sem persistência |
| Bluesky | 4 | idem |
| Telegram | 1 | idem |
| Instagram | 1 (`FETCH_TRANSCRIPT`) | resto **BLOCKED** por termos/robots |
| LinkedIn | 1 (`DISCOVER_ACCOUNT`) | resto BLOCKED |
| X | 1 (`SEARCH_KEYWORD`) | resto BLOCKED |
| TikTok | 1 (`FETCH_VIDEO_BYTES`) | resto BLOCKED |
| Threads · Facebook · Reddit | **0** | BLOCKED inteiro |

`OPERATIONAL` do YouTube continua **NOT_OBSERVED**: o único piloto foi
`ONE_SHOT` e não tocou o checkpoint.

---

## E — OS DONOS

| espécie | dono | único? |
|---|---|:-:|
| RAW (Storage + `raw_asset`) | G-42 forward | ✅ |
| DERIVED | `guarda/preservar_derivado.py` | ✅ |
| RUN (`collection_run`) | G-42 forward | ✅ |
| CHECKPOINT | `coleta/coleta_checkpoint.py` | ✅ |
| STRUCTURED · social | `coleta/social_persistencia.py` | ✅ |
| STRUCTURED · regulatório | `coleta/regulatorio_importar.py` | ✅ |
| STRUCTURED · catálogo IT | `guarda/importar_italia.py` | ✅ |
| ADMISSÃO | `admissao/admissao.py` | ✅ |
| **ORQUESTRADOR** | **nenhum** | **gap** |

**Não existe orquestrador**, e este mapa **não cria um**: 0 peças coordenam
mais de um executor. `SINTONIA SCRAP` é um **COMPOSITE_EXECUTOR** — o chamador
diz plataforma + capability e a rota é decisão da casa — e chamá-lo de segundo
orquestrador seria promover sem prova: ele coordena rotas de UMA aquisição, não
o calendário da casa.

---

## F — APIFY E GIT

**Apify não é default em lugar nenhum.** Das 46 rotas sociais declaradas: **0
com prioridade 1**, 5 como fallback, **0 permitidas hoje**. 1 rota das 46 está
sem razão escrita.

**Git ainda é banco operacional em 1 lugar**: `data/collection-ledger/italy/`
(6 runs, 144 observações), escrito por `coleta/italy_pilot_collect.mjs` e
`italy_recurrent_collect.mjs`. Contra P-011. Histórico não se apaga — o que
muda é quem passa a ser o dono daqui para a frente.

---

## G — OS 14 CRITÉRIOS

| # | critério | estado |
|---:|---|:-:|
| 1 | fontes IT em route class ou BLOCKED | ⚠️ 51 com rota `NÃO SEI` |
| 2 | RAW com owner único | ✅ |
| 3 | run com contrato | ✅ |
| 4 | checkpoint com owner único | ✅ |
| 5 | derived com owner | ✅ |
| 6 | structured com owner por espécie | ✅ |
| 7 | route selection coerente | ✅ social · ⚠️ resto sem matriz |
| 8 | Apify não é default universal | ✅ |
| 9 | Git não é runtime DB | ❌ RC-9 |
| 10 | retry/crash seguro | ✅ social · ⚠️ resto |
| 11 | cost/provenance registrados | ✅ social · ⚠️ resto |
| 12 | UNKNOWN não inferido | ✅ |
| 13 | System Map parity | ✅ |
| 14 | Intelligence congelada | ✅ |

**`COLLECTION_FOUNDATION_CLOSED = NÃO` · 4 blockers.**

---

## H — TOP 5 GAPS

Ordenados por **quantas estradas destravam**, nunca por visibilidade.

| # | gap | destrava | por quê primeiro |
|---:|---|---:|---|
| **G-1** | classificar as 51 fontes `NÃO SEI` em route class | ~40 fontes | é leitura de catálogo, não coleta. Enquanto durar, ninguém sabe quantas missões faltam |
| **G-2** | mover `collection-ledger` para os donos canônicos | 1 classe | último lugar onde Git é banco operacional (P-011) |
| **G-3** | YouTube `OPERATIONAL` ao vivo (1 canal) | 1 classe | fecha a única cadeia social ponta a ponta; `023` aplicada com autorização |
| **G-4** | matriz de rota para as classes não-sociais | 4 classes | RC-1/4/5 escolhem rota por `if` espalhado; a matriz já existe e só serve o social |
| **G-5** | ciência: separar paper descoberto de PDF coletado | 1 classe | `DISCOVERED PAPER ≠ COLLECTED PDF`, e hoje as duas contam igual |

---

## I — A SEQUÊNCIA MÍNIMA

**Quatro missões**, agrupadas por dono e estrada — não uma por fonte.

| # | missão | fecha |
|---:|---|---|
| **M1** | **Classificar as 54 fontes por route class.** Zero coleta nova: lê catálogo e código, carimba `ROUTE_CLASS` por fonte, e separa «estrada fechada» de «estrada nova». | G-1 · critério 1 |
| **M2** | **Tirar o Git do runtime.** `collection-ledger` → `collection_run` + `checkpoint_coleta`. Histórico preservado como importação. | G-2 · critério 9 |
| **M3** | **YouTube operacional ao vivo, um canal.** Aplicar a `023` com autorização, RAW durável → conteúdo → comentário → checkpoint → re-run provando zero gasto duplicado. | G-3 · RC-2 |
| **M4** | **Matriz de rota para as classes não-sociais + ciência.** Estende `social_matriz` ao documento oficial, regulatório e ciência. | G-4 · G-5 |

**A primeira é M1**, e não M3 — por mais que M3 seja a mais visível. Sem M1 não
se sabe quantas fontes as outras três fecham, e um plano que não sabe seu
próprio tamanho não é um plano.

---

## J — O QUE ESTE MAPA NÃO PROVA

- Não prova que as ~40 fontes de RC-1 **funcionam**: prova que a estrada delas
  funciona. Fonte que muda de URL continua quebrando uma a uma.
- Não prova nada sobre produção: nesta missão houve **zero** DDL, INSERT,
  UPDATE, DELETE, escrita em Storage, chamada de API ou chamada Apify.
- Não mede o que a Espanha já fechou. O recorte aqui é `COUNTRY_SCOPE=IT`.
