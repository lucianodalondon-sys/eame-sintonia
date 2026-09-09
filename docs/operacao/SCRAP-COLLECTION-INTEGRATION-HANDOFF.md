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

## 4. STORIES — respondido de novo, depois do SCRAP-R2

A resposta do R1 (`não há capacidade STORY`) foi corrigida: `INSTAGRAM/FETCH_STORIES`
existe na matriz, tem escada de rota, adaptador, normalizador e 36 testes.

```
STORIES_CAPABILITY_READY          = PARTIAL   (bloqueio único: LIVE_SAMPLE)
STORIES_COLLECTION_ADMISSION_READY = NO
STORY_COLLECTION_BOUNDARY          = WAITING_FOR_C_FINAL
C_FINAL_HEAD_SEEN                  = ecad2148
```

O bloqueio **não** é técnico, nem de política, nem de custo, nem de confiabilidade
do Actor. É credencial: não há chave da Apify neste ambiente, e o piloto para com
`CREDENTIAL_MISSING` em vez de cair para a rota pública — que foi medida `BLOCKED`
para Story.

### O que o objeto Story já emite

```
CONTENT_TYPE = STORY          (classe própria; não POST, não REEL, não HIGHLIGHT)
NATIVE_ID                     `pk` do Instagram — a chave da dedupe
SOURCE_ACCOUNT · URL
PUBLISHED_AT                  `taken_at` da plataforma
EXPIRES_AT + EXPIRES_AT_SOURCE  `expiring_at` NATIVO, nunca «publicado + 24 h»
OBSERVED_AT · COLLECTED_AT      separados desde já
MEDIA_TYPE · MEDIA_URL · MEDIA_DIMENSIONS
MEDIA_URL_DURABILITY = TEMPORARY_CDN_SIGNED_URL
RAW_REFERENCE + SHA256
FACT_TIME · FACT_LOCATION · ACCOUNT_LOCATION = UNKNOWN  (e assim devem ficar)
DATA_CLASS = PERSONAL_DATA_POSSIBLE
LEGAL_INTERPRETATION_REQUIRED = true
```

### O que o C-FINAL precisa decidir, e o SCRAP não decidiu

1. **Onde o byte do Story mora.** Hoje o RAW sai como `NOT_PRESERVED` apontando
   para o disco do runner, como todo o resto. Para Story isso é mais grave que
   para post: o original não volta.
2. **Se `EXPIRES_AT` muda o tratamento na admissão.** Uma evidência com prazo é
   uma classe que a Collection ainda não tem.
3. **A base legal do monitoramento recorrente.** Perfis de pesquisadores e
   agrônomos são dados pessoais mesmo sendo públicos. O objeto já confessa isso
   e marca `LEGAL_INTERPRETATION_REQUIRED`; quem decide não é esta missão.

### O contrato de alvo, definido e ainda não povoado

```
SOURCE_ID · PERSON_ID (só se provado) · ACCOUNT_ID · PLATFORM · PROFILE_URL
IDENTITY_STATE · WHY_MONITORED · LEGAL_POLICY_STATE · FREQUENCY
```

Os três perfis do piloto são institucionais e públicos, e estão marcados no
código como alvo de piloto, não de watchlist.

```
PILOT TARGET != CANONICAL WATCHLIST TARGET.
```

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
