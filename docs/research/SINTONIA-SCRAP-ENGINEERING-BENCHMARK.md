# BENCHMARK DE ENGENHARIA — SINTONIA SCRAP

> **RESEARCHED_AT:** 2026-09-08. Método: `git clone --depth 1` e leitura do **código-fonte
> real** de yt-dlp, gallery-dl, crawlee-python e Instaloader; documentação oficial e tags
> git para os demais. Caminhos de arquivo e nomes de classe abaixo foram lidos, não inferidos.
>
> **A pergunta não é "como raspar mais sites".** É "como construir um executor de aquisição
> que continue bom quando os sites mudarem".

---

## FASE 0 — CENSO DO QUE EXISTE HOJE (medido)

### Correção de premissa da missão

A missão mandou ler `.github/workflows/sintonia-scrap.yml` "e todos os scripts chamados
por ele". **Quando esta pesquisa começou, esse arquivo não existia.** O SINTONIA SCRAP era
um conjunto de 3 workflows + ~25 scripts. **Ele passou a existir durante a pesquisa**
(commit `cf3aec6`, hoje), junto com `social_matriz.py`, `social_rotas.py`,
`social_envelope.py` e `social_scrap.py`.

Este documento, portanto, mede **duas** camadas: a antiga (paga, Apify) e a nova (grátis,
com portão de robots). Elas ainda não se conhecem.

### Números

| Medida | Valor |
|---|---|
| Dependências de terceiros | **ZERO.** Sem `requirements.txt`, sem `pyproject.toml` |
| Linhas de aquisição (camada antiga) | 8.692 · **62% específico de plataforma** |
| Linhas de infraestrutura compartilhada | 2.449 |
| Linhas de teste | 8.810 em 30 arquivos |
| **Fixtures de payload gravadas** | **1** (`tests/fixtures/yt-raw-minimo.json`) |
| Custo Apify medido no acervo | US$ 12,81 · **96% YouTube** |
| Decisões de plataforma no YAML | 1 `if` + 2 listas `options` |
| Decisões de **rota** no YAML | **zero** |

O cliente de navegador é escrito à mão sobre socket cru (`scripts/cdp.py`, 241 linhas,
Chrome DevTools Protocol, só stdlib), com trava de porta (`tomar_porta`, `dono_da_porta`).
ffmpeg e faster-whisper vivem **fora** do repositório, em `~/.sintonia-libs`.

### Acoplamento — as oito perguntas, respondidas

1. **Quantas decisões de plataforma no YAML?** Poucas: um `if` de fase e duas listas de
   opção. **O workflow NÃO virou o domínio.** Isso é uma boa notícia e é raro.
2. **Quantas decisões de rota no workflow?** **Zero.** A rota está no Python.
3. **Quanta lógica repetida?** `_gravar()` em 6 scripts, `agora()`/`hoje()` em 5,
   `_normalizar()` por plataforma em 4. E, o pior: **duas implementações da mesma camada
   de rede** — `coletor._curl` (com a trava anti-POST-duplicado) e
   `sensor_coleta._curl_robusto` + `_curl_compat`.
4. **Onde está a escolha PUBLIC vs API vs BROWSER vs APIFY?** **Não existe ponto de
   decisão.** Ela é feita por **qual script o humano manda rodar**.
5. **Quem sabe detalhes da ferramenta?** Todo coletor. Cada um monta a entrada do ator.
6. **O caller escolhe capacidade ou ferramenta?** **Ferramenta** — na camada antiga.
   Na camada nova (`social_scrap`), já escolhe capacidade. É o avanço do dia.
7. **O workflow virou parte do domínio?** Não.
8. **Quanto código é realmente compartilhado?** 38%.

### O achado principal: **o registro está fragmentado em três**

```
comunicacao_coleta.ATORES : PLATAFORMA          -> (ator, verificação)
sensor_coleta.ATORES      : PLATAFORMA_CAPACIDADE -> ator   (+ _ALT de reserva)
instagram_coleta.ATORES   : capacidade          -> (ator, build)   (+ TETO em USD)
```

Três arquivos descobriram, **cada um por conta própria, um subconjunto DIFERENTE dos
mesmos cinco campos**: ator, build, teto de custo, verificação, rota alternativa.
A união deles é exatamente uma linha de registro de capacidade.

E o **resolvedor de rota já existe, escrito à mão, como um `if`** —
`sensor_coleta.py:711`: se `YOUTUBE_TRANSCRIPT` recusar a entrada, tenta
`YOUTUBE_TRANSCRIPT_ALT`. Um resolvedor de rota com exatamente uma regra, numa plataforma.

### Órfãos — capacidade construída e não ligada

| Módulo | O que faz | Quem usa |
|---|---|---|
| `coleta_checkpoint.py` | checkpoint real: `pode_gastar()`, `unidades_pendentes()`, `JA_CONCLUIDO_NAO_PAGAR_DUAS_VEZES` | **nenhum coletor social** — só `cicatrizes_brasil.py` e um teste |
| `source_health.py` | contrato de fonte real: `required_fields`, `identity_key`, `NEW_VERSION_CHANGED`, `SOURCE_FAILED` | **nenhum coletor social** — só `chain.py` e um teste |

`instagram_diario.py` **reimplementou o próprio estado** (`ESTADO.json`, cadência,
`MADURO_DIAS`, detecção de seca) em vez de usar o checkpoint que já existia ao lado.

> Isto não é falta de capacidade. É **capacidade construída e não ligada** —
> o que é uma notícia muito melhor, porque o conserto é ligar, não escrever.

---

## FASE 1-2 — BENCHMARK EXTERNO

### 1 · yt-dlp — **a referência de arquitetura de extractor**

`2026.08.19`, commit em 2026-08-30, **941 extractors**. **Unlicense (domínio público)** —
podemos copiar até o código. `requires-python >=3.10`. **`dependencies = []`** — o núcleo
roda só com stdlib. Windows é alvo de primeira classe (descriptografia DPAPI de cookie do
Chrome em `cookies.py`).

**Arquitetura lida:** `yt_dlp/extractor/common.py` → `class InfoExtractor` (4.191 linhas).
O contrato por extractor é minúsculo: atributos `_VALID_URL`, `_TESTS`, `_WORKING`,
`_GEO_COUNTRIES`; métodos `_real_extract(url)`, opcional `_perform_login()`.
`devscripts/make_lazy_extractors.py` gera `lazy_extractors.py` com classes-toco que
carregam **só** o necessário para casar a URL — é assim que 941 extractors custam ~0 de
tempo de partida.

**PATTERN_WORTH_COPYING — e o mais importante do relatório inteiro:**

> **A flag `expected=`.** Em `ExtractorError(msg, expected=True)`, `expected=True` significa
> *"isto é comportamento do site, não defeito nosso"* e a mensagem omite o pedido de
> reportar bug. Falha de rede marca `expected=True` sozinha. Já `_search_regex` que não
> casa levanta `RegexNotFoundError` com "please report" — **o caminho inesperado**.
>
> **Um bit separa "o site disse não" de "nosso parser quebrou".**

Também: info-dict como envelope congelado (~120 campos documentados, com `_type` ∈
`video|playlist|url|url_transparent`); `url_transparent` (um extractor delega a outro
mantendo o próprio metadado); cadeia de postprocessor com `_restrict_to`;
`--cookies-from-browser` **copiando o SQLite para tempdir antes de ler**, para não travar
o navegador vivo.

**PATTERN_NOT_APPLICABLE:** negociação de formato (`FormatSort`, HLS/DASH), o
interpretador de JS (específico de assinatura do YouTube), o auto-atualizador.

**VERDICT: USE AS DEPENDENCY (como subprocesso, não como biblioteca importada)
+ COPY ARCHITECTURAL PATTERN ONLY.**
⚠️ **Mas ver a ressalva de permissão adiante — no YouTube ele está em `Disallow`.**

### 2 · gallery-dl — **o modelo de dedupe e de configuração**

`v1.32.11`, commit 2026-09-04, 258 extractors, mantenedor único.
⚠️ **GPL-2.0 — copyleft forte. Podemos RODAR; NÃO podemos copiar código para dentro
de um SINTONIA fechado.** Padrão não é copyrightável; código é.

**Arquitetura lida:** `Extractor.items()` é um **gerador que emite mensagens** —
`Message.Directory`, `Message.Url`, `Message.Queue` — e `job.py` (`DownloadJob`,
`SimulationJob`, `KeywordJob`, `DataJob`) decide **o que fazer** com elas.
**O mesmo extractor, cinco comportamentos a jusante.** Ensaio a seco e despejo de esquema
saem de graça.

**O `archive_fmt`:** `archive.py` mantém uma tabela SQLite `archive(entry PRIMARY KEY)`;
a chave é **uma string de formato declarada por extractor** sobre o metadado do item
(ex.: `"{gallery_id}_{num}"`), conferida antes de baixar e gravada depois.
**Dedupe como DADO, não como código.**

Também: config hierárquica com herança `extractor.<categoria>.<subcategoria>`;
`cookies_check(names, domain)` como **pré-voo** — falha alto no começo com "sessão
vencida" em vez de devolver 200 resultados vazios; `_interval_429` **separado** do backoff
genérico; `ChallengeError` como classe própria ("fomos barrados por bot" ≠ "HTTP 403");
códigos de saída em bitflag acumulados com OR ao longo da execução.

**VERDICT: COPY ARCHITECTURAL PATTERN ONLY** (+ executor opcional por CLI).
A GPL fecha a porta do código; e a cobertura de Instagram dele não é mais confiável que a
nossa.

### 3 · Instaloader — **o modelo de incremental e de retomada**

`v4.15.3`, commit 2026-09-06. **MIT — podemos copiar código.** Só `requests`.
Caráter das issues: quase tudo é "401/429/checkpoint" do Instagram, não defeito de código.
**Mantido, mas estruturalmente frágil.**

**Três primitivas que estamos escrevendo à mão:**

1. **`NodeIterator.freeze()/thaw()`** (`nodeiterator.py`) — checkpoint **dentro** de uma
   paginação. O `FrozenNodeIterator` guarda cursor + página já buscada e não processada +
   índice + `best_before` (TTL: cursor do Instagram apodrece). `thaw()` **se recusa a
   retomar** se o `magic` — `blake2b` sobre `[query_hash, variables, referer, usuário]` —
   não bater. E `resumable_iteration()` salva o estado congelado **na interrupção**.
2. **`LatestStamps`** (INI) — marca d'água **por perfil e por tipo de mídia**
   (`last_post`, `last_reels`, `last_story`), **chaveada pelo ID numérico imutável**, com
   `rename_profile()` para sobreviver a troca de handle.
3. **`RateController`** — orçamento de janela deslizante **por tipo de consulta**, com
   `wait_before_query()` **antes** de cada requisição (proativo) e `handle_429()` separado.
   Feito para ser subclassado.

Bônus de graça: a documentação registra que `fast_update` ("pare no primeiro já visto")
**quebra com post fixado** — `instaloader.py:1082` carrega a guarda explícita. É um
relatório de bug gratuito sobre a nossa própria lógica incremental.

**VERDICT: COPY ARCHITECTURAL PATTERN ONLY** (NEEDS PILOT se usado como executor —
rodá-lo com sessão real é decisão de risco de conta, não de arquitetura).

### 4 · Crawlee Python — **a pergunta central, respondida**

`v1.10.1`, **commit no dia desta pesquisa**. Cadência de minor quinzenal. **Apache-2.0.**
`requires-python >=3.10`, classificadores até 3.14.
**Windows está explicitamente na CI:** `.github/workflows/_checks.yaml:139` roda
`["ubuntu-latest","windows-latest","macos-latest"]` × Python 3.10–3.14.

**RODA 100% LOCAL, SEM CONTA APIFY, SEM CUSTO? — SIM, sem ambiguidade.**

Método: varri a árvore `src/crawlee` inteira por acoplamento com a nuvem. Os únicos
resultados para `apify\.com|APIFY_TOKEN|ApifyStorageClient|apify_client` são **duas URLs
de documentação dentro de uma docstring** (`crawlers/_adaptive_playwright/_result_comparator.py:27-28`).
**Não há import de `apify_client`, não há verificação de token, não há telefonema para
casa.** O cliente de armazenamento padrão é `FileSystemStorageClient`. O cliente de
armazenamento da Apify mora no pacote **separado** `apify`, que não é dependência daqui.

> **USAR CRAWLEE NÃO SIGNIFICA PAGAR APIFY.** São coisas diferentes, da mesma empresa.
> É Apache-2.0, roda offline, e o dado fica no nosso SQLite.

**Peso de dependência:** 12 na base — `pydantic>=2.11`, `pydantic-settings`, `protego`
(robots.txt), `psutil`, `tldextract`, `yarl`, `cachetools`, `colorama`, `more-itertools`,
`async-timeout`, `typing-extensions` e **`impit`** (cliente HTTP em Rust, compilado —
dependência binária de primeira parte). Extras opcionais e limpos:
`[playwright]`, `[sql_sqlite]`, `[httpx]`. Instalação mínima viável:
`crawlee[playwright,sql_sqlite]`. **Evitar `[adaptive-crawler]` — arrasta scikit-learn.**

**O que ele resolve, que nós escrevemos à mão:**

| Peça | Onde, no crawlee |
|---|---|
| Fila persistente com **lease** | `storage_clients/_sql/_db_models.py` — tabela `request_queue_records` com `time_blocked_until` + `client_key`. **Trabalhador morto devolve o item.** |
| Checkpoint genérico | `_utils/recoverable_state.py` → `RecoverableState[TStateModel]`: qualquer modelo pydantic, salvo automaticamente em evento `PERSIST_STATE`. **Uma classe no lugar de trinta checkpoints artesanais.** Estatística e SessionPool andam em cima dela — é a prova de que generaliza |
| Rate limit por domínio | `request_loaders/_throttling_request_manager.py` — decorador de fila; `fetch_next_request()` **pula domínio em espera e devolve `None`, liberando o trabalhador em vez de dormir nele** |
| Retentativa | `BasicCrawler._should_retry_request` (l.982): **4xx nunca é retentado**; rotação de sessão tem orçamento **separado** de retentativa de requisição; `error_handler` pode **reescrever** o pedido antes de repetir |
| Sessão como identidade pontuada | `sessions/_session.py` — `max_age=50min`, `max_usage_count=50`, `error_score` (+1 ruim, −0,5 bom, bloqueia em 3,0) |
| Navegador com perfil persistente | `browsers/_playwright_browser.py:70` — `launch_persistent_context(user_data_dir=...)`, com `user_data_dir` encanado desde `PlaywrightCrawler(...)` |
| Agrupamento de erro | `statistics/_error_tracker.py` — agrupa por (arquivo:linha, classe, **mensagem difusa**): `Timeout on /post/123` e `/post/456` colapsam num grupo. **Salva HTML+screenshot na primeira ocorrência de cada grupo** |

**RISK:** (1) **o custo da conversão para asyncio** é o custo dominante, não a biblioteca;
(2) armadilha documentada de Windows — `WindowsSelectorEventLoopPolicy` que o `curl-cffi`
quer **quebra o Playwright**: no Windows, ou um ou outro, nunca os dois no mesmo processo;
(3) v1.x é jovem e anda rápido — fixar versão exata; (4) `impit` é compilado — conferir
se existe wheel para o Python exato dos nossos runners.

**VERDICT: NEEDS PILOT → depois USE AS DEPENDENCY só da camada de orquestração.**

### 5 · Scrapy — **só o conceito**

`2.18.0`, BSD-3. **Peso:** Twisted (um segundo laço de eventos), lxml, parsel, w3lib,
queuelib, cryptography, pyOpenSSL. **Twisted é o desqualificador** — segundo paradigma
assíncrono, desconfortável no Windows, e briga com o Playwright.

**A separação de sete vias é o que vale:**
`ENGINE` · `SCHEDULER` (o que vem depois) · `DOWNLOADER` (só I/O) ·
`DOWNLOADER MIDDLEWARE` (**tudo que é sobre a REDE**: retentativa, cookie, robots,
throttle, proxy) · `SPIDER` (**só parse**: bytes → itens) · `SPIDER MIDDLEWARE` ·
`ITEM PIPELINE` (validação, dedupe, persistência, com `DropItem`) ·
`EXTENSIONS + SIGNALS` (observadores transversais).

Copiar também: **`JOBDIR`** (estado do agendador em disco → `scrapy crawl -s JOBDIR=…`
retoma depois de reboot) e **spider contracts** (asserções em docstring rodadas por
`scrapy check`).

**VERDICT: COPY ARCHITECTURAL PATTERN ONLY. NÃO INSTALAR.**
A separação é a resposta canônica ao nosso problema; Twisted + navegador no Windows é
exatamente a complexidade que queremos remover.

### 6 · Playwright — **três mecanismos de sessão, e escolher errado é a causa usual de "minha sessão morreu"**

`v1.62.0`, Apache-2.0, Microsoft. **API síncrona existe** (`sync_playwright()`) —
não somos obrigados a ir para async.

1. **`storage_state`** — `context.storage_state(path=…)` captura **cookies + localStorage
   + IndexedDB + credenciais WebAuthn**. JSON portátil, versionável, reutilizável entre
   máquinas. **NÃO captura `sessionStorage`** nem o perfil do navegador.
2. **`launch_persistent_context(user_data_dir=…)`** — perfil real em disco. Captura tudo
   que uma sessão de gente tem, inclusive o que os sites usam para fingerprint.
   **Não paraleliza** (o diretório fica travado).
3. **Contextos isolados** — `browser.new_context()` por trabalho, barato, jarro de cookie
   próprio. O padrão "um contexto por conta".

Também: `context.route()` para **bloquear imagem/fonte/analytics** (economia grande de
banda e menos sinal de bot); **`page.on('response')` para colher o JSON que a própria
página busca — em geral o caminho de extração mais barato e mais estável, melhor que
raspar o DOM**; `context.tracing` → `trace.zip` (rede + snapshot de DOM + screenshot).

**Segurança:** a documentação é explícita — o arquivo de `storage_state` "pode conter
cookies e cabeçalhos sensíveis que permitem se passar por você". **É uma credencial ao
portador.** Nunca no repositório, nunca em artefato do Actions, ACL restrita no NTFS,
e idealmente embrulhado em DPAPI (`CryptProtectData`) — a mesma primitiva que o
`cookies.py` do yt-dlp desfaz para ler o Chrome.

**VERDICT: USE AS DEPENDENCY.**

### 7 · Browsertrix / Webrecorder — **evidência**

`v1.14.3`, **AGPL-3.0**. **É Node.js, não Python**, dirigindo o Brave por Puppeteer, e
"desenhado para rodar em um único contêiner Docker". **Docker em runner Windows exige
WSL2/Docker Desktop, e a documentação não traz nenhuma orientação de Windows.**
Essa é a objeção prática decisiva.

Captura tudo que o navegador buscou → **WARC** + índice CDXJ + **WACZ** (zip com hashes),
que reproduz byte a byte no ReplayWeb.page.

**A linha que interessa — quando evidência web completa se justifica:** quando a
**página como renderizada** é a prova, e alguém de fora poderá contestá-la depois — uma
alegação, um preço, uma frase de rótulo sobre a qual vamos agir comercialmente; conteúdo
que provavelmente será editado ou apagado; algo que alimenta artefato regulatório ou de
disputa. **Conjunto pequeno e curado, sob demanda — nunca no caminho principal.**

**A escada de evidência que dá 95% do valor forense por ~1% do custo:**

| Nível | O que | Custo |
|---|---|---|
| **0 — sempre** | JSON/XHR bruto + cabeçalhos + `fetched_at` + URL final + status + **SHA-256 do payload** | zero |
| **1 — barato** | HTML bruto gzipado + screenshot de página inteira | ~nada |
| **2 — de graça com Playwright** | `context.tracing` → `trace.zip` (rede + DOM + screenshot), sem Docker | zero |
| **3 — raro, sob demanda** | WACZ | alto |

**Copiar a IDEIA do WACZ mesmo no nível 1:** um pacote autodescrito e verificado por hash
(`{raw.json.gz, page.html.gz, screenshot.png, manifest.json com sha256 e fetched_at}`),
em vez de arquivos soltos.

**VERDICT: USE AS OPTIONAL EXECUTOR (só nível 3). Fora do caminho principal.**
Alternativa sem Docker: `warcio` (Python) escreve WARC a partir de respostas que já temos.

### 8 · atproto / Bluesky — **a lição de que coleta social não precisa ser scraping**

`v0.0.71`, MIT. ⚠️ **Pré-1.0: o README diz que compatibilidade entre versões não é
garantida.** `libipld` é dependência compilada em Rust — conferir wheel de Windows.

Todo o modelo é **gerado a partir de Lexicon** — o esquema publicado da plataforma.
Onde a plataforma publica contrato legível por máquina, **o problema de deriva de
extractor desaparece**.

- **Firehose** = `subscribeRepos` por WebSocket, DAG-CBOR, com **`seq` monotônico**.
  Reconecta com `cursor=<último seq>`. Tipos de quadro: `#commit` (cada operação é
  `create` | `update` | **`delete`**), `#identity`, `#account`, `#info` (`OutdatedCursor`).
- **Jetstream** = o mesmo fluxo em **JSON puro**, **filtrado no servidor** por
  `wantedCollections` e `wantedDids`. Recebemos kilobytes onde o firehose entrega a rede
  inteira. Preço: sem verificação criptográfica.

**PATTERN_WORTH_COPYING — o mais estrutural:**

> **Existem DUAS formas de executor, não uma.** `PollingExecutor` (buscar → parsear →
> gravar, tocado por cron do Actions) e **`StreamExecutor`** (conexão longa, checkpoint de
> cursor, reconexão com backoff, e que recebe `create`/`update`/**`delete`**).
> Nosso desenho hoje só supõe o primeiro — **é por isso que remoção e edição são invisíveis
> para nós.**

E um fato operacional: **o GitHub Actions é hospedeiro ruim para fluxo longo** (teto de 6h
por job). Um StreamExecutor quer ser serviço do Windows no PC local, com reinício
programado e cursor persistido. **É outra forma de runtime, e precisa ser planejada como tal.**

**VERDICT: USE AS OPTIONAL EXECUTOR (Jetstream primeiro) — NEEDS PILOT.**

### Outros, onde materialmente relevante

| Projeto | Licença | Veredito |
|---|---|---|
| **feedparser** | BSD, puro Python, ~zero deps, API estável há uma década | **USE AS DEPENDENCY. O maior retorno pelo menor risco do relatório inteiro.** Para imprensa técnica agrícola IT/ES/FR, RSS/Atom é a rota livre, limpa de ToS e sem anti-bot. `entry.id` é chave nativa de dedupe; `etag=`/`modified=` dão incremental de graça (HTTP 304) |
| **trafilatura** | Apache-2.0 | **USE AS DEPENDENCY** para a cauda longa de site. `feedparser` acha a URL, `trafilatura` transforma HTML em `{title, author, date, text}` — **apaga a categoria inteira de parser por site de notícia** |
| **PRAW** | BSD | USE AS DEPENDENCY **só se** Reddit virar alvo. Hoje: despriorizar |
| **Mastodon.py** | MIT | **DO NOT USE** — instâncias expõem RSS por conta; `feedparser` cobre o caso trivial sem dependência nova |
| **Telethon** | MIT | **NEEDS PILOT**, restrito a canal público. **Nunca enumerar membros** |
| **streamlink** | BSD-2 | **DO NOT USE** — o yt-dlp cobre; segundo baixador é complexidade somada |

---

## RESPOSTAS TRANSVERSAIS

### Como projetos maduros detectam extractor quebrado

Quatro mecanismos, do mais barato ao mais caro:

1. **Interruptor `_WORKING = False`** (yt-dlp) — extractor quebrado é **marcado**, não
   apagado; CLI e suíte de teste desviam dele. Em gallery-dl é o dict `BROKEN = {}` no topo
   de `test/test_results.py`.
2. **Teste ao vivo agendado contra URLs reais** — yt-dlp gera um teste por entrada de
   `_TESTS`; gallery-dl roda os 371 arquivos de `test/results/`. **São as canárias.** Não
   rodam em todo PR (lentas, dependem de rede e geografia); rodam em agenda, e a falha é
   triada como "o site mudou" vs "nós quebramos".
3. **Asserção estrutural dentro do parse** — `_search_regex(fatal=True)` levanta
   `RegexNotFoundError` **com pedido explícito de reportar bug**. Ou seja: seletor que
   falha é, por construção, erro **inesperado**. Detecção de deriva embutida no extractor.
4. **Contrato de forma sobre a saída** — `expect_info_dict` compara com matchers de
   **tipo**, não de bytes: `'like_count': int`, `'chapters': 'count:7'`,
   `'description': 'md5:c0959…'`, `r're:…'`.
   **Contrato = "a forma e os tipos continuam certos", não "os bytes são idênticos".**

**E uma adição barata que nenhum deles formaliza:** *assertar sobre a estatística do lote*.
"Ontem este coletor trouxe 40±15 itens com 95% de legenda não-nula; hoje trouxe 40 itens
com 0% de legenda" pega a **quebra parcial silenciosa** que contrato por campo não pega.

### Como testam sem bater na rede — e quanto é testável offline

- **Roteamento de URL é 100% offline e muito testado.** `test/test_all_urls.py` instancia
  todos os extractors e afirma `matching_ies(url) == [esperado]`. Pega a regressão mais
  comum: o `_VALID_URL` de um extractor novo roubando URLs de outro.
- **Tudo a jusante de "já temos os bytes" é testável offline e é testado assim** —
  utilitários, seleção de formato, arquivo de dedupe, cookies (contra fixture de banco),
  e `test_networking.py` que **sobe um servidor HTTP local**, não a internet.
- **Só a camada "o HTML deste site ainda parseia" é online**, isolada atrás de
  `@is_download_test`.
- **Divisão aproximada: ~70-80% da suíte é offline; ~20-30% é inerentemente online.**

> **Nenhum dos dois usa cassete gravado estilo VCR em escala, e isso é deliberado:**
> uma resposta gravada que não bate mais com o site vivo **é pior que teste nenhum**,
> porque fica verde enquanto a produção está quebrada.

Eles mantêm `--write-pages` para **despejar a página e reproduzir um bug específico** —
fixture para depurar, não para CI.

### Rate limiting — três eixos independentes, não um número

1. **Cortesia por domínio** — intervalo mínimo entre requisições + resfriamento dirigido
   por 429/`Retry-After`, **de posse da fila, não dos coletores** (formato do crawlee).
2. **Orçamento por identidade** — requisições por janela deslizante por (plataforma,
   conta/sessão), **proativo** (`wait_before_query()`), com backoff bem maior e separado
   no 429, e uma pontuação de erro que **aposenta a sessão antes de ela ser banida**.
   **Este é o eixo que protege nossas contas, e é o que script à mão sempre omite.**
3. **Orçamento global por execução** — teto duro de requisições/itens/tempo por execução,
   para que um laço fugido não queime uma conta de madrugada.

E: **nunca retentar 4xx exceto 429**; contar rotação de sessão **separado** de retentativa.

### Incremental e dedupe — três regras transferíveis

1. **Deduplicar pelo ID nativo imutável, nunca pela URL** (URL ganha slug de vaidade,
   parâmetro de rastreio, troca de handle). Declarar a chave por plataforma como string de
   formato sobre o envelope — **dado, não código**.
2. **Manter caminho de migração da chave** (`_old_archive_ids`) **e da identidade do alvo**
   (`rename_profile`). As duas coisas mudam, e as duas quebram dedupe ingênuo em silêncio.
3. **Duas estratégias, e preferir a segunda:** (a) "pare no primeiro já visto" é barato mas
   quebra com post fixado/reordenado; (b) **marca d'água de tempo por alvo e por tipo de
   conteúdo** é robusta — é o padrão certo.

### Fila e checkpoint — onde moram, e como retomam

Adotar **exatamente duas** primitivas:

1. **Fila durável com lease** — SQLite é a escolha certa num PC Windows
   (`unique_key PK, payload, sequence, is_handled, lease_until, client_key`).
   **Evitar um-arquivo-por-requisição em NTFS quando o volume subir.**
2. **Checkpoint genérico estilo `RecoverableState`** com cursor/marca d'água por alvo,
   salvo em timer **e** em `finally`, **chaveado por um hash estilo `magic` dos parâmetros
   da consulta**, para que mudança de configuração **invalide** o cursor velho em vez de
   corromper a execução em silêncio.

Todo checkpoint por script de hoje colapsa nessas duas.

### A fronteira universal

> **A função de parse tem de ser função pura de bytes → itens: sem retentativa, sem sleep,
> sem autenticação, sem armazenamento, sem política de I/O.**

Os cinco projetos impõem isso, e diferem só em onde põem a maquinaria ao redor.

| Projeto | Rede | Parse | Processamento de item | Persistência |
|---|---|---|---|---|
| yt-dlp | `networking/` + `downloader/` | `_real_extract` → info-dict | cadeia de `postprocessor/` | `YoutubeDL` |
| gallery-dl | `Extractor.request()` | `items()` emite mensagem | `postprocessor/` | `job.py` + `archive.py` |
| crawlee | `http_clients/` + `SessionPool` + throttling | `@router.handler` | código do usuário | `storage_clients/` |
| Scrapy | Downloader + Middleware | Spider | Item Pipeline | Feed/pipeline |

### A interface mínima convergente para adicionar plataforma

```python
class Coletor:
    platform: str                  # espaço de configuração
    url_pattern: re.Pattern        # roteamento + captura do ID nativo (grupo nomeado)
    dedupe_key: str                # string de formato sobre o envelope
    requires_auth: bool
    required_cookies: tuple[str]   # pré-voo, estilo cookies_check
    tests: tuple[TestCase]         # roteamento offline + contrato online
    def collect(self, target, ctx) -> Iterator[Item]:   # gerador; ctx fornece fetch()
```

**Quatro atributos e um gerador.** Registrar acrescentando **uma linha** a uma lista.
Todo o resto — retentativa, throttle, sessão, checkpoint, dedupe, persistência, evidência —
vive na infraestrutura compartilhada, que o coletor **nunca toca**.
Registro preguiçoso só quando o tempo de import doer de verdade.

---

## OS TRÊS PADRÕES QUE MAIS RENDEM, INDEPENDENTE DE QUALQUER DEPENDÊNCIA

1. **A flag `expected=`** separando "o site disse não" de "nosso parser quebrou".
2. **Dedupe declarativo estilo `archive_fmt`** sobre ID nativo.
3. **Um `RecoverableState` genérico** no lugar de trinta checkpoints artesanais.

**E o que já é nosso:** a taxonomia de falha do `apify_pool.classificar()` —
`PLATFORM_FAILURE` / `ACTOR_FAILURE` / `QUERY_FAILURE` / **`PARSER_FAILURE`**, com
`ROTACIONAM` vs `NAO_ROTACIONAM` — **é a flag `expected=` do yt-dlp, descoberta
independentemente nesta casa.** Ela só está presa dentro de uma rota. Libertá-la é
provavelmente a mudança de maior retorno por linha de código deste estudo inteiro.
