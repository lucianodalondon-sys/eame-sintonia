# ADR — EVOLUÇÃO DO SINTONIA SCRAP

**Data:** 2026-09-08 · **Estado:** PROPOSTO (nenhuma decisão implementada)
**Base:** `docs/research/SINTONIA-SCRAP-ENGINEERING-BENCHMARK.md`,
`docs/research/SINTONIA-SCRAP-CAPABILITY-MATRIX.md`,
`docs/arquitetura/SINTONIA-SCRAP-TARGET.md`

---

## CONTEXTO

O SINTONIA SCRAP tem hoje duas camadas: uma paga e madura, acoplada à Apify; e uma
grátis, nova, com registro de capacidade, resolvedor de rota e portão de `robots.txt`.
Elas não se conhecem. A pesquisa mediu 8.692 linhas de aquisição, **zero dependências de
terceiros**, 1 fixture de payload, e US$ 12,81 de gasto Apify — **96% em YouTube**.

---

## DECISÕES

### ADR-01 · **NÃO** reescrever. Evoluir por absorção.

62% do código de aquisição é específico de plataforma, mas os 38% compartilhados contêm
consertos comprados com dinheiro e com erro medido (POST não retentado, teto do lado da
plataforma, `requestsFailed`, status terminal). **Reescrita jogaria fora a memória.**
Cada componente da Camada A vira **uma rota atrás do resolver**, sem ter a implementação
tocada.
→ **`REUSE BEFORE BUILD. MEASURE BEFORE REWRITE.`**

### ADR-02 · Extrair a taxonomia de falha de `apify_pool` para um módulo neutro.

`apify_pool.classificar()` já separa `PLATFORM_FAILURE` / `ACTOR_FAILURE` /
`QUERY_FAILURE` / `PARSER_FAILURE` com `ROTACIONAM` vs `NAO_ROTACIONAM`.
**É a flag `expected=` do yt-dlp, descoberta independentemente nesta casa** — e é o
mecanismo que impede que coletor quebrado seja lido como "a fonte está vazia".
Está trancada dentro da rota paga.
→ Subir para `scripts/falhas.py`, neutro de rota. `apify_pool` passa a importá-lo.
**Maior retorno por linha de código do estudo inteiro.**

### ADR-03 · `PERMITIDA → BARATA → CAPAZ`. Nessa ordem.

Medido e verificado nesta pesquisa, direto em `youtube.com/robots.txt`:
`Disallow: /feeds/videos.xml`, `/results`, `/youtubei/`, `/comment`, `/get_video`.
As três rotas grátis de YouTube **funcionam** nesta casa e **estão barradas**.
→ **`FREE-FIRST` não é `FREE-AT-ANY-COST`.** Rota `Disallow` de custo zero é mais cara
que rota oficial de 1 unidade, porque o preço dela é a relação com a plataforma.
→ `social_rotas.permitido()` continua sendo portão executável, não comentário.

### ADR-04 · **Crawlee: PARCIAL** — copiar os padrões, adiar a dependência.

Verificado no código-fonte: crawlee-python roda **100% local, sem conta Apify, sem
custo** (Apache-2.0; os únicos vestígios de "apify" na árvore são duas URLs em docstring).
Windows está na CI dele, com Python 3.10–3.14. Ele resolve, prontas, todas as peças que
escrevemos à mão.

**E mesmo assim: PARCIAL, não SIM.** Duas razões locais, não de moda:
1. **Zero dependências é uma decisão desta casa, não um acidente.** Crawlee traz 12
   dependências de base mais `impit` (Rust compilado), em runners Windows autogeridos.
2. **O custo dominante é a conversão para asyncio** de ~30 scripts síncronos — não a
   biblioteca.

→ **Copiar agora, de graça, sem instalar nada:** `RecoverableState` (um checkpoint
genérico no lugar de trinta), rate limit como **decorador de fila por domínio que devolve
`None` em vez de dormir no trabalhador**, **4xx nunca retentado**, rotação de sessão com
orçamento **separado** de retentativa, agrupamento difuso de erro com snapshot na primeira
ocorrência do grupo.
→ **Reabrir a decisão de instalar** apenas quando aparecer um workload de volume real
(≥500 URLs em fila, com retomada obrigatória) **e** um piloto de uma plataforma responder
duas perguntas: o asyncio custa menos que manter o equivalente à mão? E os wheels de
`impit` instalam limpo no Python exato dos runners?

### ADR-05 · **Scrapy: NÃO.** Copiar a separação, nunca instalar.

Twisted é um segundo laço de eventos, desconfortável no Windows, e briga com o Playwright.
Seria complexidade **somada**.
→ Copiar a fronteira: **rede ≠ parse ≠ processamento de item ≠ persistência**, e a
ideia do `JOBDIR`.

### ADR-06 · yt-dlp: dependência **onde permitido**, e padrão sempre.

Unlicense, `dependencies = []`, Windows de primeira classe. **Mas no YouTube as rotas dele
passam por `/results` e `/youtubei/`, ambos `Disallow`, e a extração já leva
"Sign in to confirm you are not a bot" de IP de datacenter.**
→ **Como dependência:** TikTok, Facebook e mídia em geral, sempre atrás de
`social_rotas.permitido()` — nunca como atalho para contornar o portão.
→ **Como padrão, incondicionalmente:** `_VALID_URL` como chave única de roteamento com
grupo nomeado dando o ID nativo; info-dict como envelope congelado; `expected=`;
`url_transparent`.
→ **Consequência que precisa ser dita:** se a legenda automática do YouTube ficar fora,
o corpus de texto barato não está garantido, e o custo volta para transcrição local.

### ADR-07 · gallery-dl: **só padrão.** GPL-2.0 fecha o código.

Podemos rodar; não podemos copiar código para dentro de um SINTONIA fechado.
E a cobertura de Instagram dele não é mais confiável que a nossa.
→ Copiar **`archive_fmt`** (dedupe declarativo como **dado**, por plataforma, sobre o ID
nativo), o protocolo extractor-emite-mensagem / job-decide (dá ensaio a seco e despejo de
esquema de graça), `cookies_check()` como **pré-voo**, e `_interval_429` **separado** do
backoff genérico.

### ADR-08 · Instaloader: **só padrão** (MIT permite copiar código).

Três primitivas que estamos escrevendo à mão: `NodeIterator.freeze()/thaw()` com `magic`
e `best_before` (checkpoint **dentro** da paginação, que se recusa a retomar em consulta
diferente); `LatestStamps` (marca d'água por alvo × tipo de mídia, chaveada pelo **ID
numérico imutável**, com caminho para troca de handle); `RateController` (janela
deslizante por tipo de consulta, proativa).
→ Usá-lo **como executor** é decisão de risco de conta, não de arquitetura. Fora por ora.

### ADR-09 · Playwright é o runtime de navegador **para sessão autenticada** — e só.

`cdp.py` funciona, é stdlib e é Windows. **Fica.** Mas grava `LOGGED_IN: 'NO'`.
→ Playwright entra **só** quando `LOCAL_AUTH_SESSION` for necessária, no padrão de dois
níveis: **um perfil `user_data_dir` de longa vida por (plataforma, conta) para o ritual de
login, exportado para um `storage_state` de vida curta a cada execução**.
→ **`storage_state` é credencial ao portador.** Nunca no Git, nunca em artefato do
Actions, ACL restrita no NTFS, embrulhado em DPAPI em repouso.
→ Rota barata primeiro: **`page.on('response')` para colher o JSON que a própria página
busca**, DOM só como reserva.

### ADR-10 · Fila persistente: **só onde o volume pedir.**

Não criar Kafka. Não criar Redis. Não pôr fila no caminho obrigatório.
→ **Precisa:** ~500 URLs descobertas, paginação interrompida, vídeos esperando
transcrição. **Não precisa:** o pedido de 5 contas do lote congelado.
→ Quando precisar: SQLite com **lease** (`lease_until` + `client_key`), para que
trabalhador morto devolva o item. **Evitar um-arquivo-por-requisição em NTFS.**

### ADR-11 · Checkpoint mora em **um** lugar genérico, não em trinta.

`coleta_checkpoint.py` existe, é testado e é **órfão**; `instagram_diario.py`
reimplementou o próprio estado ao lado dele.
→ Generalizar num `RecoverableState`: modelo salvo em timer **e** em `finally`,
**chaveado por hash dos parâmetros da consulta**, para que mudança de configuração
**invalide** o cursor velho em vez de corromper a execução em silêncio.
→ Separar os três: **fila de pedidos** ≠ **checkpoint do executor** ≠ **estado da execução**.

### ADR-12 · `SOURCE_HEALTH` ≠ `ROUTE_HEALTH`.

Quota acabou: fonte sã, rota indisponível. Sessão venceu: fonte sã, `LOCAL_SESSION` doente.
**401 do Instagram não é rate limit — é `LIBRARY_STALE`.**
→ `source_health.py` ganha o eixo de rota e sai da orfandade.

### ADR-13 · Mídia é camada de derivação, não plataforma. Legenda primeiro.

**Não** criar `youtube_transcriber` / `instagram_transcriber` / `tiktok_transcriber`.
O adaptador entrega **referência de mídia**; a derivação faz áudio, transcrição, thumbnail.
→ `se houver legenda → nunca buscar mídia` · `se precisar de áudio → nunca puxar o fluxo
de vídeo` · `se duração > N min → exigir nota de relevância antes de transcrever`.
→ Uma legenda automática já existente é **~1000× mais barata** que transcrever o mesmo
vídeo.

### ADR-14 · Evidência em escada de quatro níveis. WACZ fora do caminho principal.

Nível 0 sempre (payload bruto + cabeçalhos + `fetched_at` + URL final + status +
**SHA-256**); nível 1 quando a aparência importa; nível 2 (`trace.zip`) de graça na falha;
nível 3 (WACZ) raro e sob demanda.
→ Browsertrix é **Node + Docker**, sem qualquer orientação de Windows na documentação.
**Não entra no caminho principal.** Se um dia precisarmos de WARC, `warcio` (Python)
escreve a partir de respostas que já temos.

### ADR-15 · Deriva: canária em agenda separada + asserção estatística.

Conjunto pequeno de URLs públicas estáveis por adaptador, `FETCH → CONTRATO DE FORMA`
(presença, tipo, faixa plausível — **nunca igualdade de bytes**).
→ Mais a asserção sobre o **lote**: *"ontem 40±15 itens com 95% de legenda; hoje 40 itens
com 0%"*. É o que pega a quebra **parcial** e silenciosa.
→ **Não descobrir a quebra durante uma coleta de 10 mil itens.**

### ADR-16 · Testes: fixture de payload por plataforma, sem cassete VCR.

Hoje: 8.810 linhas de teste, **1 fixture**. As regras são bem testadas; **o parser, que é
a parte que quebra, quase não é.**
→ Meta: roteamento de URL 100% offline; tudo depois de `bytes → item` como função pura
testável com fixture; servidor HTTP **local** para testar retentativa/429.
→ **Não** construir suíte de cassete gravado para a camada de busca: resposta gravada que
não bate mais com o site vivo **é pior que teste nenhum** — fica verde enquanto a produção
está quebrada.

### ADR-17 · Adicionar plataforma = **uma função + uma linha na matriz.**

```python
platform · url_pattern (com grupo nomeado do ID nativo) · dedupe_key · requires_auth
· required_cookies · tests · collect(target, ctx) -> Iterator[Item]
```
Retentativa, throttle, sessão, checkpoint, dedupe, persistência e evidência vivem na
infraestrutura, que o coletor **nunca toca**.
→ **Não pode exigir alterar 8 arquivos + um `case` no workflow + um baixador novo +
uma transcrição nova.**

### ADR-18 · Existem **duas** formas de executor.

`PollingExecutor` (cron do Actions) e **`StreamExecutor`** (conexão longa, cursor,
reconexão, e que recebe `create`/`update`/**`delete`**).
→ Hoje só temos o primeiro — **é por isso que remoção e edição são invisíveis para nós.**
→ **`AUSÊNCIA NUMA RODADA ≠ REMOÇÃO.**
→ GitHub Actions é hospedeiro ruim para fluxo longo (teto de 6h). StreamExecutor quer ser
serviço no PC local. **É outra forma de runtime e precisa ser planejada como tal.**

### ADR-19 · Três dependências novas, e só três.

**`feedparser`** (BSD, ~zero deps) e **`trafilatura`** (Apache-2.0) para imprensa técnica
IT/ES/FR: rota livre, limpa de ToS, sem anti-bot, com `etag`/`If-Modified-Since` dando
incremental de graça. **Apagam uma categoria inteira de parser por site.**
**`yt-dlp`** (Unlicense) como subprocesso, onde permitido.
→ **Recusadas:** Scrapy, gallery-dl, Selenium, streamlink, Mastodon.py, Redis, Kafka,
Prometheus, scikit-learn, browserforge, Docker/browsertrix no caminho principal.
→ A regra: **cada dependência nova tem de APAGAR mais código do que traz.**

### ADR-20 · Ordem de plataforma para a Itália, com uma ressalva declarada.

**YouTube → Instagram → TikTok → Facebook (só Ad Library) → Threads → Telegram → X →
Bluesky → Reddit → Mastodon → LinkedIn.**
Bluesky e Mastodon rankeiam baixo como **fonte** e **entram cedo como andaime** — grátis,
risco zero, e é onde o pipeline se prova.
→ ⚠️ **A massa de conteúdo agrícola italiano por plataforma NÃO foi medida.** O ranking é
raciocinado a partir do cenário de agro-influencer italiano e da demografia de plataforma.
**Rodar uma amostra manual de ~200 contas antes de travar a ordem.**

### ADR-21 · Apify: manter, confinar, medir. Necessidade → duas células.

**Não remover o fallback agora.** Mas a necessidade real, dados nossos ativos, se reduz a
**comentário de Instagram** e **comentário de TikTok** — mais **LinkedIn por transferência
de risco**, que é razão legítima: ali a Apify compra *indenidade da nossa conta*, não
capacidade.
→ **Nunca rotear por Apify:** YouTube, Reddit, Bluesky, Mastodon, Telegram, Threads.
→ Meta: Apify ≤5% do gasto, com teto mensal duro e medidor de custo por item.
→ **96% do gasto histórico é YouTube, onde a necessidade é zero.**

### ADR-22 · Convênio universitário é decisão de arquitetura, não de negócio.

Um convênio formal com departamento de universidade italiana abre **três** portas
fechadas de uma vez: TikTok Research API (busca e **comentário**, grátis), Meta Content
Library (Facebook **e Instagram**, incluindo comentário) e pesquisador validado do Art. 40
do DSA.
→ **Colapsa a zero as duas células restantes de necessidade de Apify e tira a maior parte
do risco de ToS das duas plataformas mais difíceis.** É a ação de maior alavancagem
disponível — e não é de engenharia. **Registrada aqui porque muda o desenho.**

### ADR-23 · GDPR entra na arquitetura, não no rodapé.

Estamos na UE processando dado da UE. **"Era público" não é base legal.**
→ Handle de **criador/empresa** é guardado; **handle de comentarista é pseudonimizado na
entrada** (HMAC com pepper rotativo). Sem avatar, sem URL de perfil de comentarista.
Agregar primeiro; texto bruto de comentário com TTL curto.
→ **Excluir Grupos do Facebook e lista de membros do Telegram da coleta automática.**
→ Honrar remoção — é também a via do Art. 17.
→ `instagram_pessoal.py` já é o dono único do dado pessoal. **Não criar um segundo.**

---

## O QUE ESTAS DECISÕES **NÃO** AUTORIZAM

Não autorizam começar migração para Crawlee, adaptador de Facebook, LinkedIn ou TikTok,
fila nova, registro novo, nem instalar dependência definitiva.
**Primeiro o TARGET é aceito. Depois o PASSO 1.**
