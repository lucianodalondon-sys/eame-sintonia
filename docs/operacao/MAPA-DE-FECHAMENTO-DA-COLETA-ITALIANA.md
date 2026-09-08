# MAPA DE FECHAMENTO DA COLETA ITALIANA

> **Este ficheiro é DERIVADO.** Os números de estado saem de
> `system-map/data/estradas-it.generated.json`, produzido por
> `python3 system-map/scripts/censo_das_estradas_it.py`.
> `tests/test_estradas_it.py` falha se algum número aqui divergir de lá.
>
> A versão anterior publicava «2 CLOSED» porque **uma pessoa escreveu 2**.
> Quando a medição passou a rodar, o resultado foi **0**.

---

## POR QUE ESTE MAPA FOI REESCRITO

O mapa anterior pintou duas estradas como prontas. O red team achou o erro, e
ele é do tipo que se repete:

    OWNER EXISTS ≠ OWNER CONNECTED.

`guarda/importar_italia.py` existe, escreve estrutura, e está no repositório —
então foi listado como o `STRUCTURED` da RC-1. Medido: ele **não lê
`derived_artifact` nem `raw_asset`**. Ele carrega outros artefatos JSON
(regulatório, GIRE, substâncias) e gera SQL por conta própria. Um writer existir
não prova que ele é o writer **daquela** estrada.

O mesmo vale para `admissao/admissao.py`: tem chamadores, mas nenhum recebe a
saída da RC-1.

    CODE EXISTS ≠ ROUTE CLOSED.
    LIVE SCHEMA ≠ COLLECTION CLOSED.
    CANDIDATE ≠ PROVEN.

---

## A — OS DOIS EIXOS, SEPARADOS

Uma cor não responde duas perguntas. Por isso o estado agora tem dois:

| eixo | pergunta |
|---|---|
| `ARCHITECTURE_CLOSED` | toda etapa necessária tem dono **e está ligada**, ou é `NOT_APPLICABLE` com razão escrita? |
| `OBSERVATION_STATE` | isso já **aconteceu**, e com que prova? |

Uma estrada pode ter arquitetura fechada e nunca ter rodado. E pode ter parte
observada com a arquitetura ainda aberta — é o caso de todas as de hoje.

### Como a ligação é medida

O modelo (`estradas-it.model.json`) diz **quais** etapas cada estrada tem e
**quem seria** o dono. O censo mede duas coisas separadas:

- `OWNER_EXISTS` — o ficheiro está no disco;
- `CONNECTED_TO_ROUTE` — esse ficheiro **cita o artefato da etapa anterior**.

O segundo é grep, e é grosseiro de propósito: o mesmo critério para todas as
estradas, porque um critério que muda por estrada deixa de comparar. O que ele
responde é estreito e honesto — «este ficheiro sequer menciona aquilo?». Um
**não** aí é definitivo.

---

## B — A MATRIZ MEDIDA

⚠ = o dono existe mas a ligação **não** foi medida.

| ROUTE_CLASS | DISCOVER | FETCH | RAW | RUN | CHECKPOINT | DERIVED | STRUCTURED | ADMISSION | FECHADA | OBSERVAÇÃO | FALTA |
|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|---|---|
| **RC-1 · OFFICIAL_HTTP_DOCUMENT** | Declared | Observed | Observed | Observed | N/A | Observed | Code ⚠ | Code ⚠ | **NÃO** | PARTIALLY_OBSERVED | STRUCTURED, ADMISSION |
| **RC-2 · YOUTUBE_OFFICIAL_API** | Observed | Observed | LocalTested | Code ⚠ | DbTested | N/A | DbTested | Code ⚠ | **NÃO** | PARTIALLY_OBSERVED | RUN, ADMISSION |
| **RC-3 · PUBLIC_NATIVE_API** | LocalTested | LocalTested | LocalTested | — | — | N/A | — | — | **NÃO** | NOT_OBSERVED | RUN, CHECKPOINT, STRUCTURED, ADMISSION |
| **RC-4 · SCIENCE_METADATA_API** | LocalTested | LocalTested | — | — | — | — | — | — | **NÃO** | NOT_OBSERVED | RAW, RUN, CHECKPOINT, DERIVED, STRUCTURED, ADMISSION |
| **RC-5 · REGULATORY_BULK_IMPORT** | — | — | — | LiveSchema | N/A | N/A | LiveSchema | — | **NÃO** | DB_TESTED | DISCOVER, FETCH, RAW, ADMISSION |

| ROUTE_CLASS | OBSERVAÇÃO | razão |
|---|---|---|
| **RC-6 · PUBLIC_BROWSER** | BLOCKED | robots/termos: zero capabilities permitidas na matriz |
| **RC-7 · LOCAL_SESSION** | BLOCKED | AUTOMATION_NOT_ALLOWED: sessao humana nao autoriza automacao |
| **RC-8 · PAID_FALLBACK** | BLOCKED | APIFY-LAST: zero rotas permitidas hoje na matriz |
| **RC-9 · GIT_LEDGER** | DEBT | estado operacional em Git, contra P-011. Nao e estrada a fechar: e divida a mover. |

### Contagem, derivada

| medida | valor |
|---|---:|
| `ROUTE_CLASSES_MODELED` | **9** |
| `ARCHITECTURE_CLOSED` | **0** |
| `OBSERVED` | **2** |
| `DB_TESTED` | **1** |
| `BLOCKED` | **3** |
| `DEBT` | **1** |
| `ROUTE_CLASSES_REQUIRED_TOTAL` | **UNKNOWN** |

> `ROUTE_CLASSES_REQUIRED_TOTAL` é **UNKNOWN**, e não 9. 51 fonte(s) sem rota conhecida. Ate a M1 provar, nenhuma delas garante caber nas 9 classes modeladas.
> Dizer «existem 9 classes» seria afirmar que o modelo já cobre o sistema. Ele
> cobre o que foi visto.

---

## C — AS FONTES

| medida | valor |
|---|---:|
| total no catálogo | 54 |
| `SOURCE_ROUTE_PROVEN` | **1** |
| `SOURCE_ROUTE_CANDIDATE` | **2** |
| `SOURCE_ROUTE_UNKNOWN` | **51** |

O mapa anterior dizia «~40 fontes operacionalmente equivalentes à ARPAV». Isso
era **candidato apresentado como provado**. «Boletim», «PDF», «site
institucional» são descrições — não provam por onde se chega na fonte.

    A DESCRIÇÃO NÃO PROVA A ROTA.

**Uma** fonte teve a rota medida ponta a ponta: o canário. As outras 53 esperam
a M1.

---

## D — O ORQUESTRADOR

O mapa anterior publicou **«não existe orquestrador»**. Errado, e o erro merece
ser dito por inteiro: apoiei-me na métrica «0 peças coordenam mais de um
executor» do censo da coleta. Essa métrica conta **import direto**, e
`orquestrador/orquestrador.py` despacha por `subprocess`. A métrica estava
certa; a leitura dela respondia outra pergunta.

    UMA MÉTRICA NÃO É UMA RESPOSTA
    ENQUANTO NINGUÉM CONFERIR O QUE ELA MEDE.

Medido agora: **existe**, e alcança **4 executores** via `pedido/receitas.py`.
Existir não é cobrir — são 4 de 21 executores. E `SINTONIA SCRAP` continua
sendo `COMPOSITE_EXECUTOR`, não um segundo orquestrador: ele coordena rotas de
**uma** aquisição, não o calendário da casa.

---

## E — SOCIAL, SEM ARREDONDAR

| camada | estado |
|---|---|
| YouTube Data API v3 | `OBSERVED` — corrida 34258433872 |
| RAW operacional | **`NOT_OBSERVED`** — o artefato 10068850407 é `PILOT_PROOF`, não `OPERATIONAL_STORAGE` |
| `RUN` da rota social | **não ligado** — `social_persistencia` não cria `collection_run` |
| STRUCTURED | `DB_TESTED`, **não LIVE** |
| CHECKPOINT operacional | **`NOT_OBSERVED`** — o piloto foi `ONE_SHOT` |
| migration 023 | `DESIGNED` · `DB_TESTED` · **`NOT LIVE`** |

Por isso a RC-2 **não fecha**: falta `RUN` ligado e `ADMISSION`.

---

## F — APIFY E GIT

Apify: **0 rotas com prioridade 1**, 5 como fallback, 0 permitidas hoje.

Git como banco operacional: **2 ficheiro(s)** em `data/collection-ledger/italy/`.
Contra P-011. Histórico não se apaga — muda o dono daqui para a frente.

---

## G — TOP 5 GAPS

Ordenados por quantas estradas destravam, nunca por visibilidade.

| # | gap | destrava | por quê |
|---:|---|---|---|
| **G-1** | classificar as 51 fontes com rota desconhecida | o tamanho de todas as outras missões | enquanto durar, ninguém sabe quantas estradas o sistema precisa |
| **G-2** | ligar `STRUCTURED` e `ADMISSION` da RC-1 ao `derived_artifact` | fecha a estrada mais populosa | é o defeito que este red team achou |
| **G-3** | tirar o Git do runtime (`collection-ledger`) | 1 classe | último lugar onde Git é banco operacional |
| **G-4** | RC-2 ao vivo: `RUN` ligado + operacional | 1 classe | fecha a única cadeia social ponta a ponta |
| **G-5** | RC-5: dar `DISCOVER`/`FETCH`/`RAW` ao regulatório | 1 classe | hoje os dados chegam ao importador sem passar por bruto nenhum |

---

## H — A SEQUÊNCIA

| # | missão | fecha |
|---:|---|---|
| **M1** | classificar as fontes com rota desconhecida. Zero coleta nova. | G-1 |
| **M2** | ligar RC-1: `derived_artifact` → estruturado → admissão | G-2 |
| **M3** | tirar o Git do runtime | G-3 |
| **M4** | RC-2 ao vivo, um canal | G-4 |
| **M5** | RC-5 e ciência: bruto e proveniência | G-5 |

**A primeira continua sendo M1** — e agora por um motivo medido, não estético:
`ROUTE_CLASSES_REQUIRED_TOTAL` é `UNKNOWN`, e um plano que não sabe o próprio
tamanho não é um plano.

---

## I — O QUE ESTE MAPA NÃO PROVA

- Não prova que alguma estrada está pronta: **0** têm arquitetura fechada.
- Não prova nada sobre produção: zero DDL, INSERT, UPDATE, DELETE, Storage, API,
  Apify.
- Não mede a Espanha. O recorte é `COUNTRY_SCOPE=IT`.
- O grep que mede ligação prova **ausência** com firmeza e **presença** com
  folga: citar o artefato é necessário, não suficiente. Uma etapa marcada como
  ligada pode estar ligada errado — isso só a execução mostra.

`COLLECTION_FOUNDATION_CLOSED` = **NÃO**.
