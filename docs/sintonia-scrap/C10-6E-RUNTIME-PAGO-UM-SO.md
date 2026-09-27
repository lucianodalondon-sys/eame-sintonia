# C10.6E — UM ÚNICO RUNTIME PARA A COMUNICAÇÃO PAGA

`C10_6E_PAID_RUNTIME_PREP = BLOCKED_CONTRACT_GAP`

> O segundo runtime foi localizado com linha e coluna. A pergunta da missão era
> se ele podia entrar hoje pela casa canônica preservando semântica, e a
> resposta é **não** — por um motivo que se mede, não se argumenta.
>
> ```
> A MATRIZ DECLARA A ESCADA. O ROTEADOR SÓ SABE SUBIR O PRIMEIRO DEGRAU.
> ```
>
> Mandar a fase paga por `COLLECT` hoje trocaria, em silêncio, uma janela de 30
> dias por 12 itens. Chamar isso de convergência seria falsificar equivalência.

---

## 1 · ONDE O SEGUNDO RUNTIME COMEÇA E ACABA

```
SECOND_RUNTIME_START = coleta/comunicacao_coleta.py :: fase_posts
                       na linha `ator, _ = ATORES[plataforma]`
SECOND_RUNTIME_END   = coleta/coletor.py :: executar   (a porta paga)
PLATAFORMAS          = INSTAGRAM · FACEBOOK · LINKEDIN
```

O orquestrador **não** é o segundo runtime, e não foi aposentado. Ele é o
orquestrador canônico da Collection: escolhe a receita, cunha o recibo, leva a
colheita à porta. A bifurcação é por TABELA, não por nome de plataforma — e essa
tabela é a prova de que a convergência funciona quando a capacidade existe:

```python
if plataforma in CAPACIDADES_SCRAP:          # hoje: só YOUTUBE
    itens, mans = _colher_pelo_scrap(...)    # → scrap_executor.COLLECT
```

A C3 tirou o YouTube dali acrescentando **uma linha**. Instagram e Facebook não
entram porque falta o que essa linha pressupõe.

---

## 2 · POR QUE NÃO ENTRAM — A MEDIÇÃO QUE DECIDE A MISSÃO

A matriz declara uma **escada** de rotas por capacidade, e para as duas
plataformas pagas ela declara os dois degraus:

| plataforma | degrau 1 (o que o roteador escolhe) | degrau 2 |
|---|---|---|
| INSTAGRAM | `instagram_janela.py:embed` · PUBLIC_BROWSER · PROVED | `apify:instagram-scraper` · **APIFY** · PROVED |
| FACEBOOK | `graph:/{page-id}/posts` · OFFICIAL_API_FREE · CREDENTIAL_MISSING | `apify:facebook` · **APIFY** · POSSIBLE_NOT_PROVED |
| LINKEDIN | `linkedin:Community Management API` · **NÃO** | `apify:harvestapi~linkedin-*` · **NÃO** |

A própria matriz escreve, ao lado do degrau 2, o motivo canônico de subir:
`FREE_ROUTE_INSUFFICIENT_CAPABILITY` para o Instagram — «qualquer coisa ALÉM dos
12 itens mais recentes» — e `AUTHORIZATION_BLOCK` para o Facebook.

E o roteador **já tem o portão do gasto**: `permitir_pago`, `motivo_pago` e o
vocabulário fechado `MOTIVOS_PAGOS`. O que falta é o degrau:

```
mz.decisao()      → UMA rota: a primeira viável
mz._rota_padrao() → UMA rota: a primeira viável
social_rotas.executar(..., rota=?)   ← não existe
```

Medido na prova, e é o achado central:

```
INSTAGRAM: autorizar gasto NAO alcanca a rota paga   instagram_janela.py:embed
INSTAGRAM: o motivo canonico nem chega a ser usado   None
FACEBOOK:  autorizar gasto NAO alcanca a rota paga   graph:/{page-id}/posts
FACEBOOK:  o motivo canonico nem chega a ser usado   None
```

`permitir_pago` é um **portão**, não um seletor. Confundir os dois faria quem
autoriza gasto acreditar que escolheu a rota paga.

### O que seria preciso, exatamente

```
MISSING_CONTRACT       uma forma de pedir um DEGRAU declarado da escada
ONDE                   leis/social_matriz.py  (`decisao`, `_rota_padrao`)
                       coleta/social_rotas.py (`_executar`)
POR QUE NÃO NESTA      a FASE 4 proíbe alterar `leis/social_matriz.py`.
MISSÃO                 A missão só obedece à política.
```

```
MISSING_CAPABILITY     INSTAGRAM/FETCH_POST não tem capacidade registada
                       FACEBOOK/FETCH_POST tem (`facebook.content`) e NÃO está WIRED
                       LINKEDIN/FETCH_POST tem (`linkedin.direct_post`) e NÃO está WIRED
```

---

## 3 · A CORRIDA TEM TRÊS DONOS

```
RUN_DUAL_OWNERSHIP = YES

orquestrador/orquestrador.py :: correr             `novo_run_id(p)`
coleta/scrap_executor.py     :: COLLECT            `abrir_execucao` → public.collection_run
coleta/comunicacao_coleta.py :: _colher_pelo_scrap `'%s-%s-%s-%s' % (MISSION, ...)`
```

Três sítios cunham `RUN_ID`, cinco chamadas ao todo. Uma colheita de YouTube
pela comunicação pública passa por **dois** deles: o orquestrador cunha o dele
antes de o subprocesso correr, e o `_colher_pelo_scrap` cunha outro por conta.

```
COLLECTION_RUN_OWNER = coleta/coleta_checkpoint.py (public.collection_run)
RUN_MANIFEST_OWNER   = orquestrador/orquestrador.py
RUN_MANIFEST_ROLE    = SEGUNDO DONO, não projeção
```

`STATUS` também é cunhado duas vezes e em vocabulários diferentes: o manifesto
escreve `SUCCESS`/`FAILED` a partir do código de saída do subprocesso; a corrida
canônica escreve `rodando`/`concluida`/`vazia`/`parcial`/`falhou` a partir do que
foi observado. Um subprocesso que devolve 0 e não colhe nada é `SUCCESS` num e
`vazia` no outro.

**Isto não foi corrigido nesta missão.** Fazer do manifesto uma projeção da
corrida canônica exige que a corrida canônica exista para os caminhos que hoje
não passam por `COLLECT` — que é exatamente o gap do §2. Corrigir a projeção
antes da convergência seria escrever um recibo de uma corrida que ninguém abriu.

```
PROVENIÊNCIA É PROSPECTIVA.
```

---

## 4 · A IDENTIDADE DO FORNECEDOR TINHA QUATRO DONOS

```
a matriz                        5 rotas de classe APIFY
coleta/comunicacao_coleta.py    3 atores
coleta/instagram_coleta.py      3 atores
regras/sensor_coleta.py         4 atores

PROVIDER_IDENTITY_OWNERS = 4
```

O nome da rota na matriz (`apify:instagram-scraper`) é um **rótulo de política**;
o `apify~instagram-scraper` é um **identificador de execução**. São coisas
diferentes, e derivar uma da outra trocando `:` por `~` seria inventar uma regra
que ninguém escreveu.

```
DERIVAR O QUE NÃO FOI DECLARADO É FABRICAR, NÃO É NORMALIZAR.
```

O que se fez sem inventar nada foi **amarrar**: cada ator declara qual rota da
matriz ele cumpre, e `conferir_atores()` recusa se a matriz deixar de declarar
essa rota ou se ela deixar de ser paga. Duas cópias amarradas continuam a ser
duas — mas deixam de poder divergir em silêncio, que era o defeito real.

---

## 5 · O CAMINHO ANTIGO DEIXOU DE SER SILENCIOSO

FASE 25 é explícita: o antigo não pode continuar como fallback calado. Ele
continua a correr, porque a política o permite e pará-lo por decisão minha
fecharia uma coleta autorizada. O que mudou é que ele **diz o que é**:

```
SEGUNDO_RUNTIME=INSTAGRAM/FETCH_POST
  Esta fase NAO atravessa `scrap_executor.COLLECT`.
  rota em uso     apify:instagram-scraper (ator apify~instagram-scraper)
  rota canonica   instagram_janela.py:embed
  FALTA           o roteador nao sabe pedir um DEGRAU da escada, e
                  nao ha adaptador ligado a INSTAGRAM/FETCH_POST.
  LIVE_PROOF_REQUIRED=YES
```

```
UM DESVIO DECLARADO É UMA MEDIÇÃO. UM DESVIO CALADO É UM BURACO.
```

---

## 6 · A PROVA, CONTRA POSTGRES DESCARTÁVEL

`provas/runtime_pago_no_postgres.py`, PostgreSQL 16.13 descartável, migrations
001–026 mais a conferência 008.

**F1 · a prova negativa do LinkedIn.** A política recusa, o roteador devolve
`ROUTE_NOT_ALLOWED`, nenhuma rota é escolhida, `coletor.executar` não é chamado,
custo 0.

**F2 · a escada.** Medida acima. É o achado que decide o veredito.

**F3 · o portão do gasto.** `INSTAGRAM/FETCH_COMMENTS` é a capacidade cuja rota
padrão já é paga. Sem autorização o estado selado é `BUDGET_EXHAUSTED`, com
`ESTADO_ORIGINAL = PAID_ROUTE_REFUSED`. Com motivo fora do vocabulário, a mesma
recusa. Com motivo canônico o portão deixa passar — e a execução para logo a
seguir, em `POSSIBLE_NOT_PROVED`, porque não há adaptador ligado.

**F4 · a taxonomia continua canônica.** Sete modos de morte injetados no boundary
do transporte, seis estados distintos, nenhum inventado:

| injetado | estado canônico |
|---|---|
| 401 · 403 | `AUTH_EXPIRED` |
| 404 | `SOURCE_GONE` |
| 429 | `RATE_LIMITED` |
| 500 | `SOURCE_UNAVAILABLE` |
| timeout | `TRANSIENT_NETWORK_ERROR` |
| malformed | `PARSER_DRIFT` |

```
PARSER QUEBRADO NÃO É FONTE VAZIA.
```

**F5 · a corrida negativa é durável.** Lida por OUTRA conexão:
`status = falhou`, `error = CHECK: DECLARED_WITHOUT_ROUTE`, etapa `CHECK/SKIPPED`,
nenhuma pendurada em `RUNNING`, custo 0.

```
SAIDA_DE_REDE_REAL   = 0
PAID_PROVIDER_CALLS  = 0
COST_USD             = 0
PAID_ROUTE_REACHABLE = NO
RUNTIME_PAGO=PASS
```

---

## 7 · RAW E NORMALIZAÇÃO — O QUE JÁ DÁ PARA COMPARAR

```
HISTORICAL_RAW_AVAILABLE = SIM, parcialmente
  data/samples/raw-paid/ES-T8-003-instagram-hashtags.raw.json.gz
  60 itens do `apify~instagram-scraper`, preservados pelo piloto de sensores ES
```

O normalizador corre sobre esses bytes **sem rede** e produz o contrato inteiro.
Os campos de proveniência vêm do manifesto, não do item:

```
RAW_REFERENCE     ← man['RAW_EVIDENCE_PATH']
RAW_COMPLETENESS  ← man['RAW_COMPLETENESS']
COLLECTION_RUN_ID ← man['RUN_ID']
COLLECTION_PROVIDER ← man['COLLECTION_PROVIDER']
```

Um manifesto que não os traga faz o item nascer `NOT_KNOWN` — que é honesto, e
é por isso que a convergência tem de levar o manifesto junto, não só os itens.

```
NORMALIZER_IS_PLATFORM_ADAPTER_RESPONSIBILITY = MIXED
  mapeamento de campo do provider  → adapter
  TEXT_KIND, COUNTRY_OF_FACT, as ausências  → domínio, e fica onde está
```

O executor **não** aprende campos de Instagram. `ARTIFACT_EQUIVALENCE` não é
`BLOCKED_ARTIFACT_GAP`: há RAW preservado bastante para comparar formato quando
o caminho canônico existir. O que falta comparar é a saída de um caminho que
ainda não existe.

---

## 8 · CUSTO

```
OLD_COST_SOURCE     coletor.executar → `usageTotalUsd` da execução da Apify
CANONICAL_COST_OWNER o registo do roteador (`COST_USD` + o balde `MEDIDA`)
COST_USD_REAL desta missão  = 0   porque nada correu
REAL_ROUTE_COST             = UNKNOWN / NOT_RUN
```

O zero desta missão não é o zero da rota.

```
0 DE «NÃO CORREU» NÃO É 0 DE «CORREU E NÃO CUSTOU».
```

---

## 9 · O PACOTE PARA A PROVA PAGA

Não executar. Este é o pedido mínimo para a missão seguinte, e **só** depois de
o contrato do §2 existir.

```
PRE_REQUISITO            o roteador tem de saber pedir um degrau declarado
PLATFORMS_REQUIRING_LIVE_PROOF   INSTAGRAM  ·  FACEBOOK
MINIMUM_SENTINELS        1 conta por plataforma, do LOTE CONGELADO
MINIMUM_ITEMS_PER_SENTINEL   1   (a prova é do CAMINHO, não do corpus)
PROVIDER_CALLS_EXPECTED  2   (uma por plataforma)
ESTIMATED_MAX_COST_USD   UNKNOWN_NEEDS_MEASUREMENT
                         a matriz diz `CUSTO: por item` e não guarda preço.
                         O teto entra por `maxTotalChargeUsd`, que o
                         `coletor` já sabe passar.
WHAT_EACH_RUN_PROVES     que o degrau pago declarado foi escolhido, que o
                         `MOTIVO_PAGO` ficou no registo, que o RAW nasceu antes
                         do normalizado, que a corrida canônica abriu e fechou,
                         e que o custo REAL voltou da plataforma
STOP_CONDITION           primeira corrida que devolva estado transitório, ou
                         custo acima do teto, ou RAW ausente
ROLLBACK_PLAN            nenhuma escrita em LIVE; o artefato fica no ramo e o
                         caminho antigo continua a ser o operacional
POST_RUN_ASSERTIONS      collection_run.status terminal · etapa sem RUNNING ·
                         raw_asset antes de derived_artifact · COST_USD > 0 e
                         igual ao da plataforma · SOURCE_ID não fabricado
```

---

## 10 · O QUE ESTA MISSÃO NÃO FEZ

- Não executou fornecedor pago. `APIFY_RUNS = 0`, `PAID_RUNS = 0`,
  `COST_USD = 0`, `NETWORK_REAL = 0`.
- Não alterou `leis/social_matriz.py`. A política continua exatamente como
  estava, e é ela que proíbe o LinkedIn.
- Não criou orquestrador novo, executor novo, dono de RUN novo, taxonomia nova,
  checkpoint novo nem `paid_provider_registry_v2`.
- Não tocou LIVE, Admission, Source Relevance, Intelligence ou Portal.
- Não mexeu nas quatro rotas de medição direta da C10.6D
  (`youtube`, `youtube-piloto`, `youtube-piloto-oneshot`, `piloto`).
  `MEASUREMENT_ACQUISITION_GAP = UNCHANGED_FROM_C10_6D`.
- Não marcou nenhuma rota como `PROVEN` por causa de fixture.
  `PAID_ROUTE_RUNTIME_PROVEN = NO` · `LIVE_PROOF_REQUIRED = YES`.
