# META-OP-01 — a Meta oficial autentica, e pelo caminho da casa

> ```
> TOKEN_PRESENT  !=  TOKEN_SENT.
> PUBLIC_WEB_HTTP  !=  OFFICIAL_API_HTTP.
> PAGE_ID  !=  SOURCE_ID.
> 401/403  !=  ZERO_RESULTS.
> ```

A META-BUILD-01 deixou as duas capacidades oficiais da Meta `DECLARED`,
`REGISTERED`, `WIRED` e `NOT_EXECUTED`. Esta missão fez-lhes a pergunta
seguinte — **estão realmente ligadas, autenticam, e conseguem ser usadas quando
a credencial existe?** — e a resposta trouxe **quatro defeitos** que ninguém
tinha medido.

---

## REGRA ZERO — sem drift

```
BRANCH         claude/wonderful-hamilton-m50ahv
INITIAL_HEAD   c36734edc5bb92aec870061d27c7df7f5e1b0b49   (igual à referência)
REMOTE         c36734ed   ·   WORKTREE limpo   ·   1 worktree
TESTES (antes) 142 · 17 falhas pré-existentes
```

---

## O SEGREDO DESTA MÁQUINA

```
META_GRAPH_TOKEN = ABSENT
```

Medido lendo **apenas os nomes** das variáveis de ambiente: não há nenhuma
variável `META*`, `GRAPH*`, `FACEBOOK*` ou `FB_*`. Esta missão **não procurou
segredo**, não criou conta, não fez login e não usou token de outra integração.

```
REAL_META_REQUESTS = 0
```

---

## DEFEITO 1 · O TOKEN NUNCA ERA ENVIADO

`META_GRAPH_TOKEN` aparecia numa **linha só** do repositório inteiro:

```python
TOKEN_ENV = 'META_GRAPH_TOKEN'      # coleta/adaptador_meta.py
```

lida por `credencial_presente()` — a **sonda**. As duas rotas montavam a URL,
chamavam `http.buscar(url)`, e mais nada. A requisição sairia **anónima**.

> **UMA SONDA QUE CONFIRMA A PRESENÇA DE UM SEGREDO NÃO PROVA QUE ELE É USADO.
> PROVA QUE ELE EXISTE — E ESSAS SÃO DUAS PERGUNTAS.**

### O conserto

`_transporte_e_token()` é agora o dono único de «como se leva o token»:

- lê-o do ambiente **no ponto onde a requisição nasce**;
- entrega-o ao transporte, que o põe em `Authorization: Bearer` — **nunca na
  URL**;
- e, **sem token, recusa antes de qualquer ida à rede**:

```
NÃO SE BATE À PORTA DE QUEM NÃO SE TEM CHAVE.
```

Sair anónimo para receber um 401 gastaria uma requisição para descobrir uma
coisa que já se sabia em memória — e num probe com tecto de UMA requisição
gastaria a única que havia.

### Por que cabeçalho, e não query string

A própria META-DEEP-01 mediu o risco, e escreveu-o sobre o `ad_snapshot_url`:

> «UM `ad_snapshot_url` CARREGA UM TOKEN. GUARDÁ-LO NUM ARTEFATO É GUARDAR UMA
> CREDENCIAL NUM FICHEIRO QUE VAI PARA O GIT.»

Uma URL viaja para o rasto, o log, a excepção e o manifesto. Um cabeçalho não
viaja para nenhum deles.

```
TOKEN NA URL É UM SEGREDO COM PASSAPORTE.
```

**⚠️ E ESTA FORMA NÃO FOI MEDIDA AO VIVO.** `Authorization: Bearer` é a forma
oficial documentada da Graph API, e é a que não vaza — mas sem credencial não há
como confirmar que esta conta, este app e este nó a aceitam. Fica
`LIVE_PROVEN = NO`, e é o probe real que responderá.

---

## DEFEITO 2 · O SEGREDO QUE A META NOS DEVOLVE VIAJAVA INTEIRO

O `ad_snapshot_url` que a Ad Library devolve traz o token embutido na query
string — e `_anuncio()` guardava o item inteiro em `raw` e o snapshot em `URL`.

A META-DEEP-01 previu exactamente este vazamento. Ele estava aberto.

```
O SEGREDO QUE VEM DE FORA TAMBÉM É UM SEGREDO.
```

Agora `scrap_http.sem_segredo()` redige `access_token`, `client_secret`,
`appsecret_proof`, `key` e `api_key` — e a redacção **diz-se**: escreve-se
`REDACTED`, que se procura num ficheiro e num teste, em vez de apagar em
silêncio. O `id` do anúncio fica, e é ele que permite reconstruir a URL na hora.

```
SECRET_LEAKS = 0
```

---

## DEFEITO 3 · UMA API OFICIAL PASSAVA PELO PORTÃO DOS CRAWLERS

`http.buscar()` é o transporte da **web pública**: lê o `robots.txt` do host
antes de tudo. As duas rotas da Meta usavam-no.

A pergunta foi respondida **pelo contrato existente**, não por opinião:

- `leis/social_matriz.py` já declara `OFFICIAL_API_FREE` como **classe
  separada** de `DIRECT_HTTP` e `PUBLIC_BROWSER`;
- e já havia precedente medido — `coleta/youtube_oficial.py::_http`, a única
  rota `OFFICIAL_API_FREE` ligada antes desta, **nunca** consultou `robots.txt`
  e faz a própria tradução de erro.

Três razões, nenhuma delas conveniência:

1. **`robots.txt` governa quem PERCORRE, não quem tem contrato.** Um cliente de
   API autenticado não é um crawler: identifica-se, traz credencial, e a
   permissão dele vive no contrato da plataforma — que é o que a matriz declara
   em `PERMITIDA`.
2. **Ler o `robots.txt` de uma API é uma ida à rede que ninguém pediu** — e num
   probe de uma requisição, é a requisição toda.
3. **`buscar()` não sabe levar credencial**: monta `User-Agent` e `Accept`, e
   não há por onde passar um token sem o pôr na URL.

> **UM PORTÃO FEITO PARA CRAWLER APLICADO A UMA API NÃO PROTEGE MAIS: PROTEGE
> OUTRA COISA, E COBRA UMA IDA À REDE POR ISSO.**

### O que NÃO mudou

`buscar()` continua exactamente como estava — **provado nesta missão**, com o
`robots.txt` a ser buscado para um host público. O teto de acessos continua a
cobrar a porta nova (ela abre um `urlopen` como qualquer outra), a política
continua soberana, e o portão da relevância continua antes de tudo.

```
NÃO HÁ BYPASS GENÉRICO DE ROBOTS. HÁ UM SEGUNDO TRANSPORTE, COM NOME E DONO.
```

---

## DEFEITO 4 · UM 401 CHEGAVA COMO «A PLATAFORMA BLOQUEOU-NOS»

`buscar()` traduz qualquer `HTTPError` em `RotaBloqueada` — que quer dizer «a
plataforma impediu-nos tecnicamente». Um 401 não é isso: é a nossa credencial a
não servir.

O transporte oficial tem tabela própria, e nenhuma linha dela é `ZERO_RESULTS`:

| HTTP | estado | porquê |
|---|---|---|
| 400 | `PERMANENT_HTTP_ERROR` | pedido malformado — defeito NOSSO |
| 401 | `AUTH_EXPIRED` | a credencial não vale |
| 403 | `AUTHORIZATION_BLOCK` | a credencial vale e **não autoriza isto** |
| 404 | `SOURCE_GONE` | |
| 429 | `RATE_LIMITED` | |
| 5xx | `SOURCE_UNAVAILABLE` | é da plataforma, e é retentável |

> **401/403 NÃO É ZERO. NUNCA FOI.** Uma recusa de autorização é uma coisa que
> aconteceu ao PEDIDO; zero é uma coisa medida sobre a FONTE. Colapsar os dois
> faz «não me deixaram ver» ler-se como «não havia nada para ver» — e a fonte
> leva a culpa pela credencial.

### E `AUTHORIZATION_BLOCK` não tinha família

Medido: a palavra que a META-DEEP-01 e `leis/social_matriz.py` já usavam caía em
`UNKNOWN_ERROR` — o balde de «ninguém sabe o que houve». Um 403 da Ad Library é
o contrário de não se saber.

Entrou como alias de `CREDENTIAL_MISSING` — mesma recuperação
(`HUMAN_PROVISION_CREDENTIAL`), rota viva, fonte sã. O que os separa não se
perde: `selar()` guarda o nome exacto em `ESTADO_ORIGINAL`, e
`social_matriz.prontidao()` continua a publicar `ACCESS_CREDENTIAL`,
`APP_REVIEW` e `PERMISSION` em eixos separados.

---

## O CAMINHO CANÓNICO

```
sintonia · pedido "colete concorrentes" --filtro fase=meta-ads
  └─► pedido.Pedido                                   REQUEST
  └─► receitas.resolver → Plano                       ORCHESTRATOR
        · receitas.escolher → scrap-meta
        · relevancia_da_fonte.portao (grátis: deixa passar, e fica escrito)
        · novo_run_id — a corrida nasce ANTES
  └─► subprocess: social_scrap.py coletar meta-ads --run-id=…
        └─► scrap_executor.COLLECT (modo ENSAIO)      SCRAP
              └─► social_rotas → scrap_registo → adaptador_meta
                    └─► scrap_http.buscar_api_oficial → Graph API
  └─► RETORNO.json declarado pela corrida             COL-LAW-505
  └─► a_colheita → ingresso → recibo
```

**O probe não chama `adaptador_meta.ads_search()`.** Ele começa no PEDIDO — e a
prova mede isso: `pedido/pedido.py` não conhece `adaptador_meta`, nem
`graph.facebook.com`, nem `urllib`.

### E porque é ENSAIO

`meta.ads.search` está `NOT_EXECUTED`, e o `CHECK` em modo NORMAL recusa-a com
`CAPABILITY_STATE_PROMISES_NOTHING`. Isso é o desenho — e sozinho fecha um
ciclo:

> **UMA CAPACIDADE QUE SÓ PODE CORRER DEPOIS DE PROVADA NUNCA CHEGA A SER
> PROVADA.**

A saída já existia: a C10.7 escreveu o ENSAIO, e a META-CLOSE-AND-BUILD-01 já
tinha medido que ele vale mesmo sem credencial. `FASES_DE_ENSAIO` é quem DECLARA
que estas duas entram por ali — e declara também **todos os limites do ensaio**:
tecto de acessos **1**, tecto de itens **5**, janela **30 dias**.

E ensaio não promove nada:

```
TRIAL_ELIGIBLE != PRODUCTION_READY.
TRIAL PASSADO  != CAPACIDADE PROVADA.
```

---

## SOURCE_ID — e o que ele não é

```
SOURCE_ID_FABRICATED = 0
```

O alvo destas rotas é um `page_id` (`1741459832625091`, BASF IT) ou um
`ig_username` (`bayer_italia`, BAYER IT) — **identidades da conta na
plataforma**, ambas revalidadas nesta missão contra o lote congelado.

Nenhuma delas é `SOURCE_ID`. As oito fontes de T9 desta casa são
`type: site institucional` — o **site** da empresa, não a página dela. Nomear
uma delas atribuiria anúncios a uma ficha que fala de outra coisa.

```
PAGE_ID != SOURCE_ID.
IDENTIDADE NA PLATAFORMA != FICHA NESTA CASA.
```

Cada unidade colhida traz a origem do **nó que a produziu** —
`META-ADS/ads_archive`, `META-BRANDED/branded_content_search` — e o `page_id`
viaja preservado no RAW, com o nome que tem. **Os dois, separados.**

---

## AS PROVAS

`provas/a_meta_oficial_autentica.py` — **67 provas, 0 falhas**, offline.

| prova | o que exige |
|---|---|
| **P0** | a cadeia está ligada, e o pedido escolhe o executor da Meta |
| **P1** | o token CHEGA, em `Authorization: Bearer`, e não está na URL, no rasto nem em objeto nenhum |
| **P2** | a API oficial **não** busca `robots.txt` e gasta **uma** ida; a web pública **continua** a buscá-lo |
| **P3** | o caminho começa no PEDIDO e pára em `CREDENTIAL_MISSING` com **0 idas à rede** |
| **P4** | 401/403/429/500/400 têm nome próprio; nenhum é `ZERO_RESULTS`; uma resposta vazia **é** `ZERO_RESULTS` |
| **P5** | `page_id` não vira `SOURCE_ID`; o snapshot viaja redigido |
| **P6** | ADVERTISEMENT != POST · BRANDED_CONTENT != POST · marca != autor |
| **P7** | o campo de UE tem rótulo próprio; o campo político não é pedido |
| **P8** | nenhuma das duas importa provider pago nem conhece endereço dele |

`tests/test_meta_op_01.py` — **68 ataques · 22 mutantes · 0 sobreviventes**.

### O que é falso, e o que não pode ser

Falso: **só o transporte HTTP** — numa prova uma função que regista o que lhe
pediram, noutra o `urlopen` do `urllib`, que é a fronteira mais funda antes do
socket. E o token usado é **inventado**, e diz-se que foi.

```
UM FAKE ACIMA DO GATE MEDE O FAKE.
```

---

## A SUÍTE QUE QUEBROU, E NÃO FOI ENFRAQUECIDA

`tests/test_meta_build_01.py` passou a bater na porta nova: ela chama as duas
rotas com transporte falso, e agora não há requisição sem credencial.

A saída fácil era abrir uma excepção para quem injecta `transporte` — e isso
transformaria a costura da prova num **bypass de credencial**, que é o buraco
que o red team desta casa caça.

> **UMA PROVA QUE PRECISA DO DEFEITO PARA PASSAR É UMA PROVA DO DEFEITO.**

A saída certa: a prova declara um token **obviamente falso**, chamada a chamada.
E **chamada a chamada**, não ao módulo inteiro — três ataques dessa suíte medem
exactamente o CONTRÁRIO, o que acontece **sem** credencial, e um token de
alcance largo apagava-os em silêncio.

> **UMA CREDENCIAL DE PROVA COM ALCANCE MAIOR DO QUE A CHAMADA APAGA AS PROVAS
> QUE MEDEM A AUSÊNCIA DELA.**

Outras duas provas apontavam para a porta antiga e subiram com ela:
`test_c10_6d_portas_canonicas` (a fase declara o que chega ao `COLLECT` — e por
isso a janela mudou de tabela) e `test_italia_na_porta_canonica` (a lista de
quem pede a corrida ganhou `scrap-meta`).

---

## O QUE ESTA MISSÃO **NÃO** FEZ

- **não** executou probe real: sem credencial não há probe, e inventar um
  resultado seria pior do que não ter;
- **não** promoveu `meta.ads.search` nem `meta.branded_content.search`: as duas
  continuam `NOT_EXECUTED`, porque **existir código não é prova**;
- **não** procurou segredo, não criou conta, não fez login;
- **não** tocou em LinkedIn, X, Facebook orgânico, Threads, PPCA, App Review;
- **não** executou Apify, não comprou provider, não gastou;
- **não** migrou os transportes das outras rotas oficiais — `youtube_oficial`
  continua com o `_http` dele, e essa dívida fica **nomeada, não paga**;
- **não** tentou reconciliar a linha paralela da SCRAP-FLOW-01.

```
REAL_META_REQUESTS = 0 · REAL_NETWORK = 0
APIFY_RUNS = 0 · PAID_RUNS = 0 · REAL_COST_USD = 0
SECRETS_READ = 0
```

---

## O ESTADO, SEM ARREDONDAR

```
META_GRAPH_AUTH_WIRING     = PASS
SECRET_LEAKS               = 0
CANONICAL_REQUEST_FLOW     = PASS
SAME_RUN_END_TO_END        = PASS

META_ADS_STATE             = NOT_EXECUTED   (inalterado — e é o correcto)
META_ADS_LIVE_PROBE        = CREDENTIAL_MISSING
META_BRANDED_STATE         = NOT_EXECUTED
META_BRANDED_LIVE_PROBE    = CREDENTIAL_MISSING

IMPLEMENTATION_READY       = PASS
LIVE_PROVEN                = NO
FIRST_BREAK                = CREDENTIAL_MISSING

META_V1                    = READY_PENDING_CREDENTIAL
```

**`READY_PENDING_CREDENTIAL` não é produção pronta.** A engenharia está feita e
provada offline; o que falta é uma coisa que código nenhum resolve — a
confirmação de identidade junto da Meta, e o token que sai dela. Quando ela
existir, o probe corre com **uma** requisição por rota, sem paginação, e é essa
corrida que decide se `NOT_EXECUTED` passa a `PROVEN`, `PARTIAL` ou `BLOCKED`.

E há uma pergunta que só o probe real responde, e que a própria Meta não
documenta: **qual token o nó `branded_content_search` aceita.**
