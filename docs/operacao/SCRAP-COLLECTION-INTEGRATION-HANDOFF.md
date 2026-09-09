# SCRAP → COLLECTION · handoff para o C-FINAL

Produzido por **SCRAP-R1** em 2026-09-09. Este documento **não decide** a fronteira
da Collection — ele entrega o que foi medido para o C-FINAL absorver.

## 1. O que o SCRAP emite hoje

`social_envelope.py` sela todo objeto; `social_rotas.selar()` sela todo registro de
execução. Os campos que já viajam:

```
PLATFORM · NATIVE_ID · SOURCE_URL · CAPTURED_AT · RUN_ID
LANGUAGE · SOURCE_LOCATION · COUNTRY_SCOPE (recorte do PEDIDO, não do objeto)
ESTADO · FAILURE_LAYER · SOURCE_HEALTH · ROUTE_HEALTH · EXECUTOR_HEALTH
RECOVERY_ACTION · DEGRADES_SOURCE · COST_USD
```

Dedupe por `PLATFORM+NATIVE_ID` roda no artefato: 118 brutos → 98 distintos no
piloto de 2026-09-09, duas execuções seguidas, sem duplicação silenciosa.

## 2. Os buracos de metadado, nomeados

| campo pedido pela missão | estado |
|---|---|
| `PUBLICATION_TIME` | presente por plataforma, não normalizado no envelope |
| `OBSERVED_TIME` vs `COLLECTED_TIME` | **um só campo** (`CAPTURED_AT`) — não separados |
| `FACT_TIME` | **ausente** — e é assim que deve ser: o SCRAP não prova fato |
| `FACT_LOCATION` | **ausente**, mesma razão |
| `SOURCE_LOCATION` | presente, e `UNKNOWN` em 98 de 98 objetos do piloto |
| `CONTENT_HASH` / `RAW_REFERENCE` | raw gravado em `raw-free/<PLATAFORMA>/` |

O piloto mede a própria honestidade: **Itália PROVADA = 0 de 98**. Nenhuma rota
gratuita declara país. `COUNTRY_SCOPE=IT` é o recorte do pedido.

```
ACCOUNT LOCATION != SOURCE LOCATION != FACT LOCATION.
PUBLICATION TIME != FACT TIME.
```

## 3. Onde o SCRAP ainda NÃO tem dono

```
SCRAP → RAW          data/samples/SOCIAL-IT/raw-free/  (artefato de piloto)
SCRAP → DERIVED      WAITING_FOR_COLLECTION_FINALIZATION
SCRAP → STRUCTURED   WAITING_FOR_COLLECTION_FINALIZATION
SCRAP → ADMISSION    WAITING_FOR_COLLECTION_FINALIZATION
```

`SCRAP_COLLECTION_ROUTE_PROVED = NO`. O SCRAP prova que as portas abrem e preserva
proveniência; **nada foi admitido**. Esta é a pergunta que o C-FINAL fecha, não esta
missão.

```
SCRAP SUCCESS != ADMITTED EVIDENCE.
```

## 4. STORIES — a pergunta obrigatória, respondida separada

| escopo | estado | por quê |
|---|---|---|
| Instagram, terceiro público | `BLOCKED` | Story não é superfície pública; não há rota permitida |
| Instagram, conta própria/autorizada | `AUTH_BLOCK` | exige sessão; a política desta casa marca LOCAL_SESSION contra terceiro como NOT_USABLE, e conta própria como REVIEW pendente |
| Instagram, rota paga permitida | `PAID_ROUTE_ONLY` | `apify~instagram-scraper` declara `resultsType: "stories"`; **nunca executado, custo por Story não medido** |
| Facebook Stories | `NOT_SUPPORTED` | nenhuma capacidade declarada |

Não há capacidade `STORY` em `leis/social_matriz.py`. Não foi inventada uma.
Se o C-FINAL quiser Stories, o que falta é, nesta ordem:

1. decidir o escopo de conta (própria vs terceiro) — é decisão jurídica, não técnica;
2. declarar a capacidade na matriz com `PERMITIDA` justificada;
3. medir o custo real do ator numa execução única;
4. separar `STORY_PUBLICATION_TIME`, `OBSERVED_TIME`, `COLLECTED_TIME` no envelope;
5. só então `piloto` com alvo legítimo.

**Nenhum destes cinco foi feito.** `STORIES_READY = NO`.

## 5. Watchlist de alto valor

`HIGH_VALUE_TARGETS_FOUND = UNKNOWN`. O piloto colhe por hashtag e termo, não por
pessoa; nenhuma identidade foi provada e nenhum canal foi atribuído a ninguém.
Derivar a watchlist das fontes já existentes no SINTONIA é trabalho do dono das
fontes, não do dispatcher.

```
APPEARING IN CONTENT != OWNING THE CHANNEL.
DISCOVERED TARGET != CANONICAL SOURCE.
```

## 6. O que esta missão mudou no código

Três arquivos, dois defeitos reais e um vazamento — todos medidos ao vivo, nenhum
inventado. Ver o log de `claude/sintonia-scrap-operational-readiness-v1`.
