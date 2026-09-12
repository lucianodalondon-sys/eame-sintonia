# LINKEDIN-BUILD-01 — LOCAL-FIRST / PAID-RESIDUAL

```
LINKEDIN_LOCAL_FIRST = PARTIAL
LINKEDIN_REAL_REQUESTS = 0 · LICDN_REQUESTS = 0
APIFY_RUNS = 0 · PAID_RUNS = 0 · COST_USD = 0,00
POLICY_CHANGED = NAO   (`leis/social_matriz.py` intacto)
```

> `PARTIAL` e o veredito honesto, e o motivo nao e engenharia. A escada foi
> construida inteira e provada no seco contra o bruto real. **Ela nao tem onde
> correr ao vivo: para conteudo do `linkedin.com` a politica desta casa nao
> declara rota permitida nenhuma — nem gratuita, nem paga.** A unica rota que
> ficou ligada e a unica que a politica permite, e ela nao toca no LinkedIn.

---

## A · GIT

```
CURRENT_BRANCH  = claude/festive-fermi-1k2mf5
WORKTREE_STATUS = LIMPA
WORKTREES       = 1 (mais duas temporarias, criadas e removidas na medicao)

HEAD do SCRAP encontrado   5bcc44f5  C10.8B «a primeira rota paga canonica»
                           2026-09-12 15:54:39 — APARECEU DEPOIS do estudo
HEAD do estudo LinkedIn    57552ea3  LINKEDIN-DEEP-01
HEAD do know-how           4f87fd48  §83 — noutro ramo, nao tocado
```

A linha do SCRAP **andou durante o estudo**. A C10.8B foi fundida para ca antes
de escrever uma linha de codigo: os oito conflitos foram todos em artefatos
gerados, resolvidos por REGERAR e nao por editar, e a conferencia de linhas
apagadas nao encontrou remocao nenhuma que nao fosse da propria C10.8B.

    CONSTRUIR SOBRE UM HEAD DE HA DUAS HORAS E CONSTRUIR AO LADO DA CASA.

### O estudo continua orfao?

Nao. `LINKEDIN-DEEP-STUDY-V1.md` e `LINKEDIN-ROUTE-MATRIX-V1.json` estao nesta
linha desde a LINKEDIN-DEEP-01. O **C11**, esse, continua orfao — e continua a
nao ser copiado: o que dele importava foi **portado como prova citada**, nao
como ficheiro arrastado.

---

## B · CURRENT CAPABILITIES

Medido no HEAD fundido, corrido e nao lembrado.

### Antes

```
DECLARED = 7 · WIRED = 0 · LIVE = 0
```

### Depois

| capacidade | STATE | WIRED | ROUTE | POLICY | CHECK |
|---|---|---|---|---|---|
| **`linkedin.identity.discovery`** | **PARTIAL** | **SIM** | `descoberta-indireta:site-da-organizacao` | **ALLOWED** | **`CAN_COLLECT_NOW`** |
| `linkedin.recent.discovery` | PROVEN | nao | — | *(sem traducao)* | `DECLARED_WITHOUT_ROUTE` |
| `linkedin.direct_post` | PROVEN | nao | — | `ROUTE_NOT_ALLOWED` | `DECLARED_WITHOUT_ROUTE` |
| `linkedin.native_video` | PROVEN | nao | — | — | `DECLARED_WITHOUT_ROUTE` |
| `linkedin.native_caption` | PROVEN | nao | — | — | `DECLARED_WITHOUT_ROUTE` |
| `linkedin.history.discovery` | UNKNOWN | nao | — | — | `PROMISES_NOTHING` |
| `linkedin.comments` | UNKNOWN | nao | — | — | `PROMISES_NOTHING` |
| `linkedin.documents` | NOT_EXECUTED | nao | — | — | `PROMISES_NOTHING` |

```
DECLARED = 8 · WIRED = 1 · LIVE = 1 (a permitida)
```

### O defeito de traducao que esta missao encontrou — e fechou

Este e o achado de seguranca da missao, e ele estava vivo.

```
ANTES:  'linkedin.recent.discovery' -> MATRIZ 'DISCOVER_ACCOUNT'
        mz.decisao('LINKEDIN','DISCOVER_ACCOUNT') = ALLOWED
```

`linkedin.recent.discovery` significa **as publicacoes recentes da pagina de
empresa**. `DISCOVER_ACCOUNT` tem uma rota so debaixo da sua permissao:
`descoberta-indireta:site-da-organizacao` — ler o site **da propria
organizacao** para lhe achar o endereco. A propria matriz escreve o limite:
«Guarda `DISCOVERY_SOURCE`, `DISCOVERED_URL`, `TARGET_TYPE`, `DISCOVERED_AT`, e
**nunca conteudo de post fabricado**.»

    «AS PUBLICACOES RECENTES DA PAGINA» E «O ENDERECO DA CONTA» SAO DOIS ACTOS,
    E A TRADUCAO FAZIA O PRIMEIRO PEDIR EMPRESTADA A PERMISSAO DO SEGUNDO.
    `IDENTITY != CONTENT`, violado na camada de traducao.

Nenhum codigo o explorava — porque nenhuma das sete tinha rota. **A porta
estava destrancada por dentro, e a chave era o nome errado.** Qualquer missao
futura que ligasse uma rota a `linkedin.recent.discovery` teria encontrado
`ALLOWED` e seguido em frente.

```
DEPOIS: 'linkedin.recent.discovery' -> MATRIZ None
        'linkedin.identity.discovery' -> MATRIZ 'DISCOVER_ACCOUNT'   (PARTIAL)
        donos de DISCOVER_ACCOUNT no LINKEDIN: 1
```

    RETIRAR A TRADUCAO NAO ABRE ROTA NENHUMA. FECHA UMA QUE ESTAVA ABERTA PELO
    NOME ERRADO.

O desenho nao e novo: o Facebook ja tinha `facebook.identity.discovery` a
apontar para `DISCOVER_ACCOUNT`. O LinkedIn passou a ter o mesmo.

---

## C · RAW FIELDS RECOVERED

O nucleo desta missao, e o mais barato: o bruto ja estava no disco.

```
data/samples/raw-paid/ES-T8-002-linkedin-posts-{a,b}.raw.json.gz
472 itens · 26 campos de topo · RUN_ID ES-T8-002-2026-08-29-a
```

| campo do bruto | itens | o normalizado ANTIGO tinha? | agora |
|---|---:|---|---|
| `postVideo` → `VIDEO_URL` · `VIDEO_THUMBNAIL` | **56** | **NAO** | SIM |
| `document` → `DOCUMENT_URL` · `DOCUMENT_PAGES` · `DOCUMENT_TRANSCRIPT_URL` | **20** | **NAO** | SIM |
| `article` → `ARTICLE_URL` · `ARTICLE_TITLE` · `ARTICLE_DOMAIN` | **93** | **NAO** | SIM |
| `engagement.reactions[]` → `REACTIONS_BY_TYPE` | **449** | **NAO** | SIM |
| `postImages` → `IMAGE_URLS` | 472 | NAO | SIM |
| `newsletterUrl` · `repost` · `shareUrn` · `entityId` | 10 · 5 · 472 · 472 | NAO | SIM |

```
RAW_FIELD_PRESENT -> NORMALIZER_SEES_FIELD -> OUTPUT_PRESERVES_SEMANTICS
                                                       provado, campo a campo
tipos de midia recuperados:
  IMAGE 291 · ARTICLE 93 · VIDEO 56 · DOCUMENT 20 · TEXT 12
```

E o que **nao** foi fabricado, que importa tanto quanto:

```
VIDEO_DURATION   None em 472 de 472    o bruto nao o tem
NATIVE_CAPTION   0 de 472              nenhum fornecedor pago a entrega
COMMENTS_TEXT    0 de 472              contra 335 de CONTAGEM
REACTION_PEOPLE  None em 472 de 472    e nunca se pede sem pedido
```

Onze posts **falam** de video no texto e nao tem campo de video. Continuam
`MEDIA_TYPE = TEXT`: texto nao e prova de midia.

---

## D · FREE / OWN ROUTES

Uma, e e a unica que a politica permite:

```
linkedin.identity.discovery
  rota      descoberta-indireta:site-da-organizacao
  classe    DIRECT_HTTP · PERMITIDA = SIM
  le        o site DA PROPRIA ORGANIZACAO
  NAO le    linkedin.com · licdn.com · nenhum buscador
  devolve   CONTENT_TYPE = DISCOVERY, com DISCOVERY_SOURCE, DISCOVERED_URL,
            TARGET_TYPE (COMPANY|PERSON) e DISCOVERED_AT
  nunca     POST_CONTENT — o campo existe e e sempre None, de proposito
  custo     COST_STATE = FREE_ROUTE_BY_POLICY · ACTUAL_COST_USD = 0.0
```

    PERGUNTAR AO GOOGLE NAO E ESTA ROTA. O §8.2(4) do User Agreement nomeia
    «search tools» em claro, e o Actor de mercado que faz isto por US$ 4/1.000
    declara-se «Google-based search». Fica fora.

A rota aceita transporte injectado, e e por isso que 54 sentinelas a exercem
sem abrir um socket.

---

## E · LOCAL PROCESSING

```
texto de PDF     coleta/executor_texto_de_pdf.py   ja existe, dono unico
fala             fala_local                         ja existe, dono unico
```

Nenhum dos dois foi reescrito, e nenhum dos dois e o gargalo.

```
TRANSCRIPT · TIER = LOCAL · nao pede permissao de rota
             porque nao ha ida a rede nenhuma
```

E a linha que impede a confusao mais cara desta casa:

    `MEDIA ACCESS != ASR`. Ter um motor de fala bom nao move a fala do LinkedIn
    um milimetro. `ASR_BLOCKED_BY_ACQUISITION = YES`, ainda.

---

## F · PAID RESIDUAL

O plano de aquisicao resolve, para cada campo em falta, o nivel e a politica.
Com a politica de hoje, contra um post de video real, pedindo **tudo**:

```
WANT_COMMENTS · WANT_REACTION_PEOPLE · WANT_MEDIA · WANT_DOCUMENT · WANT_TRANSCRIPT

PAID_NEEDED_FOR = []                          ← nenhum campo sai como PAID
BLOCKED_FOR     = COMMENTS_TEXT · REACTION_PEOPLE · VIDEO_BYTES ·
                  DOCUMENT_BYTES · NATIVE_CAPTION
LOCAL_FOR       = TRANSCRIPT
```

Cada um dos cinco sai como `BLOCKED_NO_PERMITTED_ROUTE`, **e nao como «precisa
de dinheiro»**.

```
PAID PROVIDER NAO TRANSFORMA ROTA PROIBIDA EM ROTA PERMITIDA.
Se o gap so tem rota nao permitida, o resultado e BLOCKED — nunca uma compra.
```

E e por isso que o veredito e `PARTIAL`: a escada esta construida e o degrau
pago esta vazio **por politica**, nao por falta de codigo.

---

## G · DELTA

O adapter aceita a janela e **nao tem memoria**. O checkpoint vem de fora.

```
SINCE · POSTED_LIMIT_DATE · LAST_SEEN_TIME · LAST_SEEN_ID · MAX_POSTS
```

Medido contra os 472 reais:

| corte | dentro | fora por tempo |
|---|---:|---:|
| 2026-08-22 | **13** | 459 |
| 2026-07-30 | **56** | 416 |
| 2026-05-31 | **173** | 299 |
| 2025-08-29 | **452** | 20 |

`RUN 1` com corte em 2026-08-22 achou 13 ids. `RUN 2` com
`last_seen_time` = o mais novo deles devolve **interseccao vazia**.

Tres nomes para o mesmo eixo — `since`, `posted_limit_date`, `last_seen_time` —
porque tres fornecedores lhes dao tres nomes. **Vence o mais restritivo.**
Aceitar o mais largo faria um delta virar historia sempre que dois nomes
chegassem juntos.

### Uma imprecisao que esta missao encontrou em si mesma

O estudo profundo publicou `7 dias = 16 de 472`. Este adapter mede `13`.

**Os dois estao certos.** O estudo contou `(captura − publicado).days <= N`, e
`.days` **trunca**: um post de 7,9 dias conta como 7. Aqui o corte e uma **data
absoluta**.

    «7 DIAS» NAO E UMA MEDIDA ATE ALGUEM DIZER SE O CORTE E UMA DATA OU UMA
    SUBTRACCAO TRUNCADA.

O adapter usa data, porque e o que o provider aceita em `postedLimitDate` — e
um filtro que nao bate com o do provider e um delta que pede itens que o
provider ja tinha excluido.

---

## H · ENRICHMENT

```
LIST_POSTS   →  normalizar_lote()      barato, e ja traz 16 campos
ENRICH_POST  →  plano_de_aquisicao()   explicito, e o padrao de TUDO e False
```

| bandeira | campo | padrao |
|---|---|---|
| `WANT_COMMENTS` | `COMMENTS_TEXT` | **False** |
| `WANT_REACTION_PEOPLE` | `REACTION_PEOPLE` | **False** |
| `WANT_MEDIA` | `VIDEO_BYTES` | **False** |
| `WANT_DOCUMENT` | `DOCUMENT_BYTES` | **False** |
| `WANT_TRANSCRIPT` | `NATIVE_CAPTION`, `TRANSCRIPT` | **False** |

Pedido vazio → `GAP = []` → `PLAN = []`. Nenhum passo, nenhuma ida, nenhum
dolar. Uma bandeira com nome errado **rebenta** em vez de nunca se cumprir.

E a sentinela que a missao existe para ter:

```
FIELD_ALREADY_PRESENT  ->  PAID_ENRICHMENT_NOT_REQUIRED
```

Provada: com `COMMENTS_TEXT` ja presente e `WANT_COMMENTS=True`, o gap sai
vazio e o plano nao propoe comprar nada.

### A selectividade, medida

```
comentarios   95 de 472 posts tem ao menos 1   (20,1%)
video         56 de 472                        (11,9%)
documento     20 de 472                         (4,2%)
```

A contagem de comentarios vem **gratis na listagem** e diz, antes de qualquer
gasto, quais dos 472 valem uma pergunta. Pedir texto para os 472 seria pagar
377 perguntas cuja resposta ja se sabe vazia.

---

## I · COST MODEL

Para a execucao desta missao:

```
FREE_REQUESTS            = 0   (a rota permitida correu com transporte injectado)
LOCAL_CPU                = a leitura de 2 ficheiros .gz e 54 sentinelas
PAID_RUNS                = 0
PAID_ITEMS               = 0
PAID_USD                 = 0,00
FIELDS_ALREADY_AVAILABLE = 16 campos de listagem, em 472 itens
FIELDS_BOUGHT            = 0
PAID_INCREMENTAL_VALUE   = 0 campos novos — porque nada foi comprado
```

`PAID_INCREMENTAL_VALUE` responde «que campos NOVOS o pagamento trouxe?». Hoje
a resposta e zero, e ela e util: mostra que **a recuperacao dos 56 videos, dos
20 documentos e dos 93 artigos custou zero dolares.** Eles ja tinham sido
pagos uma vez, em 2026-08-29, e a normalizacao deitava-os fora.

---

## J · PROBES NEEDED

Nenhuma executada.

```
PROBE_A  listagem gratuita/local permitida
  TARGET       1 site de organizacao real (ex.: imagelinenetwork.com)
  REQUESTS     1 (mais 1 do portao, ao robots do MESMO site)
  COST         US$ 0
  PROVA        `linkedin.identity.discovery` ao vivo: o portao le o robots do
               site da organizacao, a rota devolve handle, e o estado sobe de
               PARTIAL para PROVEN — ou nao sobe, e diz porque.

PROBE_B  um post conhecido
  TARGET       1 URL de post publico ja conhecida
  REQUESTS     1
  COST         US$ 0
  PROVA        se a legenda SRT ainda e servida e com que TTL; e VIDEO_BYTES,
               o denominador que falta a escada de video inteira.
  BLOQUEIO     `FETCH_POST` esta ROUTE_NOT_ALLOWED. DECISAO HUMANA, primeiro.

PROBE_C  uma capacidade residual paga
  TARGET       harvestapi/linkedin-company-posts, 1 empresa, maxPosts=10
  REQUESTS     1 run
  COST         ≈ US$ 0,015
  PROVA        se o payload de COMPANY-POSTS traz os mesmos campos de midia que
               o de POST-SEARCH — e se traz LEGENDA, que e a unica coisa que
               falta a casa inteira.
  BLOQUEIO     rota paga, ROUTE_NOT_ALLOWED. DECISAO HUMANA + dinheiro.
```

```
TOTAL SE AS TRES FOSSEM AUTORIZADAS: ≈ US$ 0,015 e 4 pedidos.
NENHUMA FOI INICIADA.
```

---

## J-bis · O FLUXO DE EXEMPLO, CORRIDO NO SECO

Pedido: **«posts novos desta empresa desde 2026-08-22»**, contra os 472 reais.

```
1 · JANELA          13 de 472           459 recusados por tempo
2 · LISTAGEM        13 objetos          ARTICLE 1 · IMAGE 12
                    campos por objeto: 15, todos ja pagos em 2026-08-29
3 · O CALLER escolhe UM post            7497300910252134400
4 · O SCRAP confere o que ja tem
      WANTED          COMMENTS_TEXT · VIDEO_BYTES · NATIVE_CAPTION · TRANSCRIPT
      ALREADY_PRESENT (vazio — este post e ARTICLE, nao tem video)
      GAP             os quatro
5 · E decide o nivel de CADA UM
      COMMENTS_TEXT    TIER=BLOCKED  BLOCKED_NO_PERMITTED_ROUTE
      VIDEO_BYTES      TIER=BLOCKED  BLOCKED_NO_PERMITTED_ROUTE
      NATIVE_CAPTION   TIER=BLOCKED  BLOCKED_NO_PERMITTED_ROUTE
      TRANSCRIPT       TIER=LOCAL    READY
      PAID_NEEDED_FOR  []
6 · PROCESSAMENTO LOCAL   possivel para TRANSCRIPT — e inutil sem bytes, e o
                          plano di-lo ao por a legenda BLOQUEADA antes dele
7 · TRACE
      ACQUISITION_TIER   LOCAL          (reler bruto preservado)
      FIELDS_FROM_PAID   15 campos      (a procedencia, de 2026-08-29)
      FIELDS_FROM_FREE   0
      PROVIDER           apify:harvestapi~linkedin-post-search
      COST_USD           0.0
      BLOCKED_FOR        COMMENTS_TEXT · NATIVE_CAPTION · VIDEO_BYTES
```

    O TRACE MOSTRA `FREE`, `LOCAL` E `PAID` SEM OS SOMAR — E MOSTRA QUE ESTA
    CORRIDA FOI `LOCAL` SOBRE CAMPOS DE PROCEDENCIA `PAID`. Sao dois eixos, e
    colapsa-los faria o relatorio dizer que 15 campos foram de graca.

---

## K · RED TEAM — 30 ataques, e tres que a missao virou contra si

`provas/linkedin_local_first.py` · `tests/test_linkedin_build_01_local_first.py`

| # | ataque | resultado | como e apanhado |
|---|---|---|---|
| 1 | normalizer perde `postVideo` | **apanhado** | sentinela conta 56 |
| 2 | normalizer perde `document` | **apanhado** | conta 20, e 20 com `transcriptManifestUrl` |
| 3 | normalizer perde `article` | **apanhado** | conta 93 |
| 4 | normalizer perde tipos de reacao | **apanhado** | conta 449, e os cinco tipos |
| 5 | comments count vira comments text | **apanhado** | 335 de contagem, 0 de texto, no mesmo payload |
| 6 | document metadata vira PDF capturado | **apanhado** | `DOCUMENT_BYTES_ACQUIRED = False` ao lado do URL |
| 7 | video URL vira video bytes | **apanhado** | `VIDEO_BYTES_ACQUIRED = False`, e o gap inclui `VIDEO_BYTES` |
| 8 | ASR corre sem midia | **apanhado** | `TRANSCRIPT` e LOCAL; a legenda antes dele sai `BLOCKED` |
| 9 | caption inexistente vira transcript | **apanhado** | 0 de 472, e `TRANSCRIPT` nunca e preenchido |
| 10 | history route vira company-page history | **apanhado** | a nota do registo nomeia os dois eixos; estado fica `UNKNOWN` |
| 11 | corrida total acontece em delta | **apanhado** | 13 de 472, e `dentro + fora = 472` |
| 12 | `lastSeen` ignorado | **apanhado** | interseccao vazia entre RUN 1 e RUN 2 |
| 13 | pago corre antes da rota livre | **apanhado** | a unica ligada e `DIRECT_HTTP` |
| 14 | enriquecimento compra campo ja presente | **apanhado** | `ALREADY_PRESENT` e gap vazio |
| 15 | `want_comments=false` compra comentarios | **apanhado** | gap vazio, plano vazio |
| 16 | `want_media=false` baixa midia | **apanhado** | idem, e nenhum byte adquirido em 472 |
| 17 | provider escolhido pelo workflow | **apanhado** | o adaptador nao importa `coletor` nem `apify_pool` |
| 18 | provider escolhido so por preco | **apanhado** | nenhuma constante de preco vive no adaptador |
| 19 | list price vira actual cost | **apanhado** | `1.50` e `4.033` nao aparecem no ficheiro |
| 20 | CPU local vira custo zero total | **apanhado** | `FREE` e `LOCAL` sao niveis distintos, quatro no vocabulario |
| 21 | paid provider muda policy | **apanhado** | `PAID_NEEDED_FOR = []`, tudo `BLOCKED_NO_PERMITTED_ROUTE` |
| 22 | paid provider bypassa router | **apanhado** | a rota entra por `rota=`, que e a porta que mede o portao |
| 23 | chamada directa a actor vira prova | **apanhado** | AST: nenhum import de provider, nenhuma chamada de compra |
| 24 | raw nao e preservado | **apanhado** | `RAW_REFERENCE` existe e o ficheiro existe |
| 25 | normalized substitui raw | **apanhado** | o bruto viaja inteiro em `RAW` |
| 26 | `article URL` vira `SOURCE_ID` | **apanhado** | `NATIVE_ID` e o activity id, e e digito |
| 27 | post URL vira `SOURCE_ID` | **apanhado** | idem, e `NATIVE_ID != URL` |
| 28 | `country_scope` vira `source_location` | **apanhado** | `COUNTRY_SCOPE=ES` e `SOURCE_LOCATION=UNKNOWN` |
| 29 | localizacao da empresa vira `fact_location` | **apanhado** | `SOURCE_LOCATION` fica UNKNOWN em 472 de 472 |
| 30 | reaction people colhidas sem pedido | **apanhado** | `None` em 472, e fora do gap sem bandeira |

### E os tres que esta missao encontrou em si propria

| # | ataque | resultado |
|---|---|---|
| 31 | **«visible to anyone» vira permissao** | **apanhado** — o campo e guardado como `DECLARED_VISIBILITY` e a sentinela exige que `FETCH_POST` continue nao-ALLOWED ao lado dele |
| 32 | **a sentinela proibe o NOME do provider e apaga a procedencia** | **apanhado, e foi real**: a primeira versao do mutante M10 proibia a cadeia `harvestapi~` e reprovou — o nome aparece uma vez, como **rotulo** de procedencia do bruto. A sentinela passou a medir o **import** e a **chamada**, por AST. *Proibir o nome apagaria o rasto; o que nao pode existir e a IDA.* |
| 33 | **a medicao suja a arvore** | **apanhado, e foi real**: a prova escrevia tres ficheiros em `data/samples/SOCIAL-IT/raw-free/LINKEDIN/`. A casa ja tinha a lei — *uma medicao que suja a arvore e uma medicao que a proxima vai medir* — e a correccao foi apontar `RAW_DIR` a um temporario, sem mudar a funcao de producao |

---

## L · MUTATION — 12 mutantes, zero sobreviventes

| # | mutante | a sentinela que o mata |
|---|---|---|
| M1 | remover `postVideo` do mapeamento | `VIDEO_URL == 56` |
| M2 | remover `document` | `DOCUMENT_URL == 20` e `DOCUMENT_TRANSCRIPT_URL == 20` |
| M3 | remover `reactions` | `REACTIONS_BY_TYPE == 449` |
| M4 | ignorar delta | `DENTRO == 13`, e `!= 472` |
| M5 | always-enrich | pedido vazio → `GAP == []` e `WANTED == []` |
| M6 | paid-before-free | a classe da unica ligada nao e `APIFY` nem `OFFICIAL_API_PAID` |
| M7 | comments true por default | todas as bandeiras sao `False` |
| M8 | full-video antes de caption | `NATIVE_CAPTION` antes de `TRANSCRIPT` no plano |
| M9 | ASR sem media gate | a legenda sai `BLOCKED` e os bytes nao foram adquiridos |
| M10 | provider directo | AST: sem import de `coletor`/`apify_pool`/`urllib`, sem chamada de compra |
| M11 | raw depois da normalizacao | sem `RAW_REFERENCE`, o nivel desta accao **nao** e `LOCAL` |
| M12 | policy ignorada | `PAID_NEEDED_FOR == []` e `BLOCKED_FOR` nao vazio |

```
SURVIVORS = 0
```

---

## M · REGRESSION

Medida em duas arvores: uma **worktree limpa do HEAD fundido**, antes de uma
linha desta missao existir, e esta.

```
BASELINE (worktree limpa de ed2adb3c)    PASS=91  FAIL=15
DEPOIS   (esta arvore)                   PASS=94  FAIL=13
NOVOS TESTES                             54 sentinelas, num ficheiro novo
```

E a comparacao que importa nao e a contagem — e o **conjunto**:

```
FALHAS(DEPOIS)  ⊂  FALHAS(BASELINE)     inclusao ESTRITA
diferenca: test_c3_youtube_cutover e test_portao, que FALHAVAM na baseline
           e PASSAM aqui.

NEW_FAILURES = 0
```

Nenhuma reprovacao nova, e duas a menos. As treze restantes sao **herdadas** e
tocam rede, GPU ou credencial que este container nao tem.

Uma nota de honestidade sobre a primeira medicao desta missao: ela deu
`FAIL=16`, com `test_c5_transcript_gate` e `test_c6_especie_do_texto` a
reprovar. Os dois passam isoladamente nas duas arvores, e a corrida onde
reprovaram foi a que aconteceu **enquanto a prova ainda sujava a arvore** com
tres ficheiros em `data/samples/SOCIAL-IT/`. Corrigida a sujidade, os dois
voltaram a passar na suite inteira.

    A MEDICAO QUE SUJA A ARVORE NAO SO SUJA — ELA MEDE ERRADO, E MEDE ERRADO
    NOUTRO TESTE, QUE E O SITIO ONDE NINGUEM VAI PROCURAR.

---

## N · SYSTEM MAP

Cadeia inteira corrida. O LinkedIn aparece como

```
executor -> router -> adaptador_linkedin -> rota livre permitida
                                         -> provider pago SO onde a politica deixar
                                            (hoje: em lado nenhum)
```

Nenhum segundo runtime foi criado. O adaptador nao chama provider, nao abre
socket e nao decide permissao — le a decisao do dono dela.

Cadeia corrida inteira:

```
generate_system_map.py        MAPA=OK · pecas=163 · ligacoes=675 · 753/1526
validate_system_map.py        SYSTEM_MAP_CHECK=PASS
test_system_map.py            TESTES_SYSTEM_MAP=PASS
test_freshness.mjs            TESTES_FRESCURA=PASS · 49 provas
test_impressao_da_arvore.py   **FAIL · 1 reprovada (herdada)**
publicar_no_deploy.mjs        DEPLOY_METADATA=OK · MESMA_ARVORE=SIM · PERTENCE=SIM
impressao --conferir-carimbo  IMPRESSAO_DO_CARIMBO=IGUAL, sobre 1 680 fontes
```

### O `P9` apanhou-me, e apanhou bem

A primeira validacao reprovou com
`P9_CODIGO_DECLARADO: provas/linkedin_local_first.py` — codigo novo sem peca no
mapa. Declarado em `architecture.declared.json`, na mesma peca onde a C10.8B
declarou a dela.

    UMA PROVA NOVA QUE O MAPA NAO CONHECE E ARQUITETURA INVISIVEL. O portao
    disse-o antes de eu ter de descobrir.

### E uma reprovacao que continua herdada

```
nenhum_passo_e_engolido_pelo_erro_do_anterior
  passos sem `if: !cancelled()`:
    mapa: 1 · regerar o mapa a partir desta arvore
    mapa: 1b · o censo da topologia da coleta
    coleta: 4k · a lingua e a mesma no contrato, no ...
    coleta: 4l · a telemetria distingue NAO CORREU d...
```

A mesma reprovacao, com os mesmos quatro passos, foi medida numa worktree limpa
de `532e3bed` na LINKEDIN-DEEP-01, e esta missao **nao toca num unico ficheiro
`.github/`**. Nao foi consertada aqui de proposito: consertar um workflow e
alteracao de infraestrutura, fora do escopo declarado. Fica registada pela
segunda vez, com o mesmo nome.

---

## O · WHAT CHANGED

```
1. coleta/adaptador_linkedin.py  60 -> ~800 linhas: passa a ser o DONO da
   traducao bruto->envelope, da janela, do plano de aquisicao e do rasto
2. `linkedin.identity.discovery` declarada (PARTIAL) e LIGADA — a unica rota
   que a politica permite
3. `linkedin.recent.discovery` deixa de traduzir para DISCOVER_ACCOUNT
   — fecha a permissao emprestada
4. as notas de `history.discovery`, `comments`, `documents` e `native_video`
   passam a dizer o que foi medido, com numero
5. provas/linkedin_local_first.py — a escada no seco, contra o bruto real
6. tests/test_linkedin_build_01_local_first.py — 54 sentinelas
```

## P · WHAT DID NOT CHANGE

```
leis/social_matriz.py          INTACTO — nenhuma rota foi aberta nem fechada
coleta/social_rotas.py         INTACTO
coleta/scrap_executor.py       INTACTO
coleta/scrap_http.py           INTACTO
coleta/coletor.py              INTACTO
o estado de 7 das 8 capacidades  INTACTO
Collection · Admission · Intelligence · Portal · Vercel · LIVE   NAO TOCADOS
```

## Q · UNKNOWN

```
· se a legenda SRT ainda e servida, e com que TTL
· VIDEO_BYTES — nenhum MP4 do LinkedIn foi baixado, nunca
· se `company-posts` traz os mesmos campos de midia que `post-search`
· se `scanRequiredForDownload: true` impede o download do PDF
· a cobertura real da descoberta indireta: 1 de 2 alcancaveis, de 7 tentadas
· o robots do `licdn.com` — NUNCA medido
· o custo real das 3 corridas historicas com COST_USD = NOT_PRESERVED
```

## R · RISK

```
1. O bruto preservado tem URLs EXPIRADAS. `VIDEO_URL` e `DOCUMENT_URL` sao
   endereco, nao ficheiro — e aqueles ja nao abrem. Um leitor apressado ve
   «temos 56 videos». Temos 56 ENDERECOS MORTOS, e o campo
   `VIDEO_URL_EXPIRES_AT` esta la para o dizer.
2. `linkedin.identity.discovery` esta PARTIAL por medicao de OUTRA missao
   (a sonda da C11), nao por corrida desta rota. So a PROBE_A a promove.
3. Cinco das sete sentinelas da C11 nao responderam — o IP de datacenter ve
   uma fatia estreita da web, e isso limita a propria rota permitida.
4. 138 perfis pessoais continuam preservados no disco sem base legal declarada.
   Esta missao nao os aumentou e nao os resolveu.
```

## S · KNOW_HOW_DELTA

```
KNOW_HOW_DELTA = ATUALIZACAO NECESSARIA
```

O ficheiro vive em `origin/claude/sintonia-eame-know-how-v1` (§83), fora desta
linha. Esta missao nao lhe toca. O que ele precisa de receber:

```
O QUE          uma capacidade pode herdar a PERMISSAO de outra pela traducao,
               sem que uma linha de codigo o peca
POR QUE        `linkedin.recent.discovery` traduzia para `DISCOVER_ACCOUNT` e
               herdava ALLOWED. Os dois actos sao diferentes: um le posts, o
               outro le o site da organizacao para achar um handle.
PROVA          `cap.pela_matriz('LINKEDIN','DISCOVER_ACCOUNT')` devolvia a
               capacidade errada; agora devolve `linkedin.identity.discovery`
CONSEQUENCIA   o campo de traducao entre dois vocabularios e uma SUPERFICIE DE
               PERMISSAO, e nao um apelido. Uma traducao errada nao rebenta —
               ela autoriza.

               `TRANSLATION IS AUTHORIZATION`.
```

---

## T · VERDICT

```
LINKEDIN_LOCAL_FIRST = PARTIAL
```

`PASS` nos vinte criterios que dependem de engenharia:

| # | criterio | |
|---|---|---|
| 1 | RAW util deixa de ser descartado | ✔ 56 · 20 · 93 · 449 |
| 2 | listing e enrichment separados | ✔ |
| 3 | delta suportado onde disponivel | ✔ 5 knobs |
| 4 | paid nao roda por default | ✔ |
| 5 | comments text nao e comprado sem pedido | ✔ |
| 6 | media nao e adquirida sem pedido | ✔ |
| 7 | local processing usado apos bytes | ✔ (donos reusados) |
| 8 | caption precede ASR | ✔ |
| 9 | paid provider e residual | ✔ — e hoje esta vazio |
| 10 | fields existentes nao sao recomprados | ✔ |
| 11 | policy continua soberana | ✔ matriz intacta |
| 12 | nenhum bypass | ✔ |
| 13 | red team PASS | ✔ 33 |
| 14 | survivors 0 | ✔ |
| 15 | NEW_FAILURES 0 | ✔ |
| 16 | System Map PASS | ✔ |
| 17 | nenhuma rede real necessaria | ✔ |
| 18 | nenhuma execucao paga | ✔ |
| 19 | worktree limpa | ✔ |
| 20 | push sem force | ✔ |

E `PARTIAL` — nao `PASS` — por uma razao que nenhum teste conserta:

> **A escada existe inteira e o degrau do meio esta vazio.** Para conteudo do
> `linkedin.com` esta casa nao tem rota permitida nenhuma: nem gratuita, nem
> paga. O `plano_de_aquisicao` responde `BLOCKED_NO_PERMITTED_ROUTE` a cinco
> dos seis campos que alguem possa querer, e essa e a resposta certa.

    CHAMAR ISTO `PASS` SERIA DIZER QUE O LINKEDIN ESTA RESOLVIDO. O QUE ESTA
    RESOLVIDO E A CASA: ELA JA NAO PERDE O QUE COMPRA, JA NAO COMPRA O QUE TEM,
    E JA NAO PEDE EMPRESTADA UMA PERMISSAO QUE NAO E DELA.

O que falta nao e codigo. E a decisao do coordenador sobre se existe alguma
rota autorizavel para conteudo do LinkedIn — e a PROBE_C diz que, mesmo
havendo, continua por saber se alguma delas entrega **legenda**.

```
HARD STOP.
```
