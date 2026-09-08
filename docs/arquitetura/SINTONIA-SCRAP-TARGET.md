# SINTONIA SCRAP — ATUAL, ALVO, LACUNAS

> Documento de arquitetura. **Nada aqui foi implementado por esta pesquisa.**
> Fontes: `docs/research/SINTONIA-SCRAP-ENGINEERING-BENCHMARK.md` e
> `docs/research/SINTONIA-SCRAP-CAPABILITY-MATRIX.md`.

---

## O ATUAL — DUAS CAMADAS QUE NÃO SE CONHECEM

Em 2026-09-08 o SINTONIA SCRAP passou a ter **duas** arquiteturas vivas ao mesmo tempo.

### Camada A — paga, madura, acoplada à Apify

```
workflow (fase, plataforma)
   → comunicacao_coleta / sensor_coleta / instagram_coleta
        · cada um com seu dict ATORES
        · cada um montando a entrada do ator
   → contrato_ator.portao()        ← portão GRÁTIS antes do gasto
   → coletor.executar()            ← "porta única das rotas PAGAS"
        · apify_pool                ← rotação de chave + taxonomia de falha
   → RAW primeiro → proveniencia.RUN_MANIFEST
```

Boa engenharia, comprovada por acidente medido: teto `maxTotalChargeUsd` do lado da
plataforma; `requestsFailed` lido porque **contagem de item não detecta perda**; POST
**não** retentado porque repetir um POST perdido acende uma segunda execução paga.

**O defeito estrutural:** `coletor.py` se chama "porta única das rotas pagas" e **só
conhece a Apify**. A porta existe; ela é do **fornecedor**, não da **rota**.

### Camada B — grátis, nova, com portão de permissão

```
workflow sintonia-scrap.yml (censo|portao|video|gap|piloto|ledger)
   → social_scrap        ← executor composto
   → social_matriz       ← REGISTRO DE CAPACIDADE (plataforma × capacidade × rota)
   → social_rotas        ← RESOLVEDOR + adaptadores + permitido() lendo robots.txt vivo
   → social_envelope     ← envelope de evidência + dedupe + raw-free
```

Piloto real: **99 objetos distintos, US$ 0,00, zero Apify** — e pegou dois defeitos que um
piloto só-feliz não pegaria (o id do Mastodon é local, então o mesmo post federado contava
duas vezes; e "agronomo" no Bluesky devolveu agrônomos espanhóis e brasileiros).

**As duas camadas não se falam.** A Camada B não sabe que a Apify existe; a Camada A não
sabe que existe um registro de capacidade.

### As oito medições de acoplamento

| Pergunta | Resposta medida |
|---|---|
| Decisões de plataforma no YAML | 1 `if` + 2 listas — **o workflow não virou o domínio** |
| Decisões de rota no YAML | **zero** |
| Lógica repetida | `_gravar()` ×6, `agora()` ×5, **duas camadas de rede** (`coletor._curl` vs `sensor_coleta._curl_robusto`) |
| Onde se escolhe PUBLIC/API/BROWSER/APIFY | **na Camada A: em lugar nenhum** — é escolhido por qual script o humano roda. Na Camada B: em `social_rotas` |
| Caller pede capacidade ou ferramenta | A: **ferramenta**. B: **capacidade** |
| Código compartilhado | 38% |

---

## O MAIOR PROBLEMA ESTRUTURAL

Não é o Apify, não é o YAML, não é a falta de framework.

> **O conhecimento de rota está gravado em três dicionários `ATORES` diferentes, cada um
> com um subconjunto diferente dos mesmos cinco campos — e a taxonomia de falha que
> distingue "a plataforma disse não" de "nosso parser quebrou" existe, é boa, e está
> trancada dentro da rota paga.**

`apify_pool.classificar()` já separa `PLATFORM_FAILURE` / `ACTOR_FAILURE` /
`QUERY_FAILURE` / **`PARSER_FAILURE`**, com `ROTACIONAM` vs `NAO_ROTACIONAM`.
**Isso é a flag `expected=` do yt-dlp, descoberta independentemente nesta casa** — e é o
mecanismo que faz um coletor quebrado ser *notado* em vez de virar "a fonte está vazia".
Hoje ela só funciona se o caminho passar pela Apify.

---

## O QUE É MUITO BOM E DEVE SER PRESERVADO

| Peça | Por quê |
|---|---|
| `proveniencia.py` | RUN_MANIFEST, redação de token, classificação de RAW. **É o nível 0 da escada de evidência, já pronto** |
| `apify_pool.classificar()` | a taxonomia `expected=`. **Libertar, não reescrever** |
| `contrato_ator.py` | portão **grátis** antes do gasto + `cheira_a_credencial()` |
| `coletor.executar()` | RAW primeiro; status terminal; `maxTotalChargeUsd`; `requestsFailed`; `PostTalvezCriado` |
| `instagram_diario.py` | incremental real (cadência, `MADURO_DIAS`, seca) — **é o `LatestStamps` do Instaloader, escrito à mão** |
| `instagram_janela.saida_de_rede()` | `NETWORK_EXIT_COUNTRY` na proveniência. *"Mudar a rota de rede entre duas medições é mudar o método"* |
| `social_rotas.permitido()` | lê o `robots.txt` vivo com o User-agent real. **Já reprovou rota que funcionava** |
| `cdp.py` | cliente CDP em stdlib com trava de porta. Windows, sem dependência |
| Zero dependências | **é uma decisão, não um acidente** — e é o que torna a resposta sobre Crawlee diferente da resposta genérica |

---

## O ALVO

A figura pedida pela missão, **criticada e simplificada**. Duas caixas foram removidas:

- **`REQUEST QUEUE` sai do caminho obrigatório.** Fila é resposta para *alguns*
  workloads, não para todos. Um pedido de 5 contas não precisa de fila; 500 URLs
  descobertas precisam. Fila como **caixa opcional entre resolver e executor**.
- **`PLATFORM ADAPTER` e `ROUTE EXECUTOR` são a MESMA caixa.** Separá-las cria a
  cerimônia que o estudo diz para evitar: um adaptador *é* o que atravessa uma rota.

```
                    SOCIAL REQUEST
              (plataforma, capacidade, alvo)
                          ↓
                  CAPABILITY REGISTRY          social_matriz
                          ↓
                   ROUTE RESOLVER              social_rotas
          permitida? → capaz? → saudável? → com credencial? → barata?
                          ↓
              [ QUEUE ]  ← só para workload de volume
                          ↓
   ┌──────────────── ROUTE EXECUTOR ────────────────┐
   │  HTTP livre │ API oficial │ BROWSER local │ LIB │ APIFY │
   └────────────────────────┬───────────────────────┘
                            ↓
                   RAW EVIDENCE                social_envelope
                     (escada de 4 níveis)
                            ↓
               MEDIA / DERIVATIONS   ← legenda-primeiro, áudio depois
                            ↓
              CANONICAL COLLECTION CONTRACT
                            ↓
                    RUN / PROOF                proveniencia
```

### As três leis do alvo

1. **`PERMITIDA → BARATA → CAPAZ`**, nessa ordem. Não `barata → capaz → permitida`.
   Uma rota `Disallow` de custo zero é mais cara que uma rota oficial de 1 unidade,
   porque o preço dela é a relação com a plataforma.
2. **A função de parse é pura: bytes → itens.** Sem retentativa, sem sleep, sem
   autenticação, sem armazenamento, sem política de rede.
3. **Um bit separa "o site disse não" de "nosso parser quebrou".**

### Route Resolver — a ordem de decisão

```
PERMITIDA?      robots.txt vivo + termos declarados      → ROUTE_NOT_ALLOWED
CAPAZ?          o registro diz que a rota faz isto       → CAPABILITY_UNAVAILABLE
SAUDÁVEL?       ROUTE_HEALTH, não SOURCE_HEALTH          → ROUTE_UNAVAILABLE
TEM CREDENCIAL? chave/sessão presente e não vencida      → CREDENTIAL_MISSING
CABE NO ORÇAMENTO? teto por execução e por mês           → BUDGET_EXHAUSTED
                          ↓
              a mais BARATA das que sobraram
```

Apify é **uma rota**, avaliada por essas mesmas cinco perguntas. **Não é a arquitetura.**

### SOURCE HEALTH ≠ ROUTE HEALTH

`source_health.py` já existe e mede a **fonte**. Falta o outro eixo:

| Situação | SOURCE | ROUTE |
|---|---|---|
| Quota da Data API acabou | `HEALTHY` | `UNAVAILABLE` |
| Sessão do navegador venceu | `HEALTHY` | `LOCAL_SESSION` = `UNHEALTHY` |
| Instagram aposentou o `doc_id` | `HEALTHY` | `LIBRARY_STALE` |
| O canal foi apagado | `GONE` | `HEALTHY` |

> **401 do Instagram não é rate limit.** É `LIBRARY_STALE`. Tratar como backoff é passar
> a noite repetindo um pedido que nunca vai passar.

### Evidência — a escada de quatro níveis

| Nível | O que | Quando |
|---|---|---|
| **0** | payload bruto + cabeçalhos + `fetched_at` + URL final + status + **SHA-256** | **sempre** |
| **1** | HTML gzipado + screenshot de página inteira | quando a aparência importa |
| **2** | `trace.zip` do Playwright (rede + DOM + screenshot) | **de graça, na falha** |
| **3** | WACZ | raro, sob demanda, para o que pode virar disputa |

Envelope mínimo de toda aquisição: `PLATFORM`, `NATIVE_ID`, `SOURCE/ACCOUNT`, `URL`,
`RAW_PAYLOAD_REFERENCE`, `CAPTURED_AT`, `PUBLISHED_AT`, `RUN_ID`, `ROUTE`, `EXECUTOR`,
`CONTENT_TYPE`, `PROVENANCE` (+ `NETWORK_EXIT_COUNTRY`, que já temos).
**Preservar o payload nativo. Não tentar transformar Instagram, YouTube e LinkedIn na
mesma estrutura completa.**

### Mídia — uma camada de derivação, não um transcritor por rede

```
DESCOBRIR VÍDEO → METADADO → tem legenda?
                                ├── SIM → texto (≈1000× mais barato)
                                └── NÃO → só ÁUDIO → whisper local
```

**Não** criar `youtube_transcriber`, `instagram_transcriber`, `tiktok_transcriber`.
O adaptador de plataforma entrega **uma REFERÊNCIA DE MÍDIA**; a camada de derivação faz
áudio, transcrição e thumbnail para todos.
`instagram_transcrever.py` já tem o miolo certo (idioma **declarado** pelo país, nunca
detectado; teto de tempo 6×; lote 8 medido) — falta **generalizar e acrescentar
legenda-primeiro**, que hoje não existe.

**Download de vídeo inteiro: só quando não houver outro caminho.**

### Rate limiting — três eixos

1. **Cortesia por domínio** — de posse da fila/resolver, não dos coletores.
2. **Orçamento por identidade** — por (plataforma, conta), **proativo**, com backoff
   separado no 429 e pontuação que aposenta a sessão **antes** do banimento.
   **É o eixo que protege nossas contas, e é o que falta.**
3. **Teto global por execução.**

Hoje temos `PAUSA_ENTRE_CHAMADAS = 1.0` — que é exatamente o `sleep(2)` espalhado que a
missão proíbe, só que centralizado. Melhor, mas ainda não é política.

### Deriva — canária

Um punhado de URLs públicas estáveis por adaptador, rodando em agenda **separada** da
coleta: `FETCH → CONTRATO DE FORMA` (presença de campo, tipo, faixa plausível).
Mais **a asserção estatística sobre o lote** — *"ontem 40±15 itens com 95% de legenda;
hoje 40 itens com 0% de legenda"* — que é o que pega a quebra parcial silenciosa.

> **Não descobrir a quebra durante uma coleta de 10 mil itens.**

---

## CURRENT × TARGET

| Componente atual | Veredito | Como |
|---|---|---|
| `social_matriz.py` | **KEEP** | já é o registro de capacidade. Falta só absorver as rotas pagas |
| `social_rotas.permitido()` | **KEEP** | o portão de robots é o melhor ativo novo |
| `social_rotas` adaptadores | **KEEP + estender** | acrescentar plataforma é acrescentar função + linha na matriz |
| `social_envelope.py` | **KEEP + estender** | subir para a escada de 4 níveis; guardar SHA-256 |
| `proveniencia.py` | **KEEP** | é o RUN/PROOF do alvo |
| `contrato_ator.py` | **KEEP** | vira o pré-voo genérico (estilo `cookies_check`) |
| `coletor.py` | **WRAP** | vira `executor_apify`, uma rota **atrás** do resolver. **Não reescrever** |
| `apify_pool.classificar()` | **REFACTOR (extrair)** | a taxonomia sobe para `falhas.py`, neutra de rota. **A mudança de maior retorno do estudo** |
| `apify_pool` (rotação de chave) | **KEEP** | continua dono da chave da Apify |
| Os três dicts `ATORES` | **REPLACE** | migram para linhas de `social_matriz` |
| `coleta_checkpoint.py` | **REFACTOR (ligar)** | existe, é testado, é órfão. Generalizar para `RecoverableState` |
| `source_health.py` | **REFACTOR (ligar)** | existe, é órfão. Separar em SOURCE × ROUTE |
| `instagram_diario.ESTADO.json` | **REFACTOR** | é o `LatestStamps` à mão. Generalizar para marca d'água por alvo × tipo |
| `instagram_transcrever.py` | **REFACTOR** | miolo certo, nome errado. Vira derivação neutra + legenda-primeiro |
| `cdp.py` | **KEEP hoje, REPLACE quando precisar de login** | funciona sem dependência. `LOGGED_IN: 'NO'` é o limite |
| `sensor_coleta._curl_robusto` | **RETIRE LATER** | duplica `coletor._curl` |
| `comunicacao_coleta` / `sensor_coleta` / `instagram_coleta` | **WRAP** | continuam rodando; passam a ser chamados **pelo** resolver |
| `rede.py` | **KEEP** | portão de egresso, resposta pronta |
| Workflows antigos | **KEEP** | ficam até o equivalente novo estar provado |

**Nada é removido agora.**

---

## AS LACUNAS — o que o alvo tem e o atual não

| # | Lacuna | Gravidade |
|---|---|---|
| 1 | Taxonomia `expected=` presa na rota Apify | **ALTA** — é o que faz coletor quebrado virar "fonte vazia" |
| 2 | Sem `ROUTE_HEALTH` (só `SOURCE_HEALTH`, e órfão) | **ALTA** |
| 3 | Sem legenda-primeiro na mídia | **ALTA** — paga transcrição por texto que já existe |
| 4 | Checkpoint órfão; estado reimplementado por script | **ALTA** |
| 5 | 1 fixture de payload para 30 arquivos de teste | **ALTA** — parser é a parte que quebra, e é a menos testada |
| 6 | Sem política de rate limit por identidade | **MÉDIA** — é o eixo que protege as contas |
| 7 | Sem canária de deriva | **MÉDIA** |
| 8 | Sem `StreamExecutor` → remoção e edição são invisíveis | **MÉDIA** |
| 9 | Camada paga fora do registro | **MÉDIA** |
| 10 | Sem sessão local autenticada (`LOGGED_IN: NO`) | **MÉDIA** — e é a que abre Instagram/TikTok |
| 11 | Duas camadas de rede | **BAIXA** |
| 12 | Sem `feedparser`/`trafilatura` para imprensa técnica | **BAIXA em risco, ALTA em retorno** |

---

## BUILD vs REUSE vs WRAP

| Peça | Veredito | Razão |
|---|---|---|
| Runtime HTTP | **BUILD (manter)** | `coletor._curl` já carrega o conserto anti-POST-duplicado, que nenhuma biblioteca teria |
| Runtime de navegador **sem login** | **BUILD (manter `cdp.py`)** | funciona, zero dependência, Windows |
| Runtime de navegador **com login** | **REUSE — Playwright** | `storage_state` + `launch_persistent_context` não valem a pena reescrever |
| Fila de requisição | **BUILD, mínima (SQLite)** | só quando um workload de volume aparecer |
| Gestão de sessão | **BUILD sobre Playwright** | a política é nossa; o mecanismo é dele |
| Retentativa | **BUILD (já existe)** | falta só unificar as duas implementações |
| Rate limiter | **BUILD** | copiar a forma de três eixos; ~80 linhas |
| Baixador de mídia | **REUSE — yt-dlp**, onde permitido | ⚠️ no YouTube está em `Disallow` |
| Transcrição | **KEEP** | faster-whisper local já está medido e afinado |
| Adaptador de plataforma | **BUILD** | é o nosso domínio |
| Evidência nível 0-2 | **BUILD (quase pronto)** | `proveniencia` + `social_envelope` |
| Evidência nível 3 (WACZ) | **DO NOT NEED ainda** | Docker no Windows não se paga |
| Imprensa técnica | **REUSE — feedparser + trafilatura** | apaga uma categoria inteira de parser |

---

## O QUE **NÃO** ADICIONAR

**Scrapy** (Twisted é um segundo laço de eventos e briga com navegador no Windows) ·
**gallery-dl como dependência** (GPL-2.0, e a cobertura de Instagram não é melhor que a
nossa) · **Selenium** (o Playwright faz mais e melhor) · **streamlink** (yt-dlp cobre) ·
**Redis / Kafka** (SQLite resolve num PC) · **Prometheus** (JSON no repositório resolve) ·
**scikit-learn** via `crawlee[adaptive-crawler]` (já sabemos qual plataforma precisa de
navegador) · **browserforge / fingerprint spoofing** (com sessão de gente real é inútil e
contraproducente) · **Docker/browsertrix no caminho principal**.

> **Não queremos Scrapy + Crawlee + Playwright + Selenium + gallery-dl + Instaloader no
> núcleo.** O estudo tem de REDUZIR complexidade. As três dependências recomendadas —
> `feedparser`, `trafilatura`, `yt-dlp` — somam menos peso que qualquer uma sozinha das
> recusadas, e **duas delas apagam código que hoje escrevemos à mão**.
