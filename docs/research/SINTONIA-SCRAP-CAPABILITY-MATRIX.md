# MATRIZ DE CAPACIDADE × ROTA — SINTONIA SCRAP

> **RESEARCHED_AT:** 2026-09-08. Toda linha marcada `⚠️NAO_VERIFICADO` **não** foi
> confirmada contra fonte primária hoje. Não construir em cima dela sem reconferir.
>
> A pergunta desta matriz **não** é "qual é a melhor rota do Instagram?".
> É "qual é a melhor rota para **esta capacidade** do Instagram?".
> PERFIL, COMENTÁRIO, HISTÓRICO e VÍDEO têm rotas diferentes na mesma plataforma.

---

## LEGENDA DE ROTA

| Código | Significado |
|---|---|
| `PUB_HTTP` | GET sem autenticação (JSON/HTML/RSS), sem navegador |
| `API_FREE` | API oficial, custo marginal zero |
| `API_PAID` | API oficial, medida |
| `PUB_BROWSER` | Navegador sem login |
| `LOCAL_AUTH` | **Nosso** perfil Chrome logado, no PC Windows local |
| `LIB` | Biblioteca local livre (yt-dlp, gallery-dl, Instaloader, atproto, Telethon…) |
| `STREAM` | Firehose / websocket / push |
| `APIFY` | Ator pago |
| `✖` | Indisponível ou impraticável |

## O ATIVO QUE MUDA A MATRIZ INTEIRA

Quase todo aviso público de "a rota não-oficial é frágil" pressupõe **IP de datacenter**.
Nós rodamos em **PC residencial italiano com perfil de navegador realmente logado**.
Isso move Instagram, TikTok, YouTube, Threads e X de "APIFY necessário" para
"APIFY conveniente". Confirmado para o YouTube: pedido de nuvem/VPN leva desafio de bot
onde a conexão doméstica com cookie passa.

**Contra-fato, dito com honestidade:** usar conta logada para coleta automática viola o
contrato (ToS) de Meta, TikTok, X e LinkedIn. É risco **contratual**, não criminal —
raspar dado público não é crime (pós-*hiQ*; a UE não tem análogo do CFAA). O pior caso
realista é **banimento da conta e bloqueio de IP**; e, só no LinkedIn, notificação
extrajudicial. Ver §GDPR.

---

## 1 · YOUTUBE — valor agrícola IT: **MÁXIMO**

| Capacidade | Rota escolhida | Custo | Alternativa |
|---|---|---|---|
| DISCOVER_CONTENT | **`PUB_HTTP` RSS `/feeds/videos.xml?channel_id=UC…`** | **0 quota, sem chave** | `API_FREE playlistItems` 1u/50 |
| DISCOVER_ACCOUNT | `API_FREE search.list type=channel` | **100u** — caro | `LIB` yt-dlp |
| SEARCH_KEYWORD | `LIB` yt-dlp `ytsearchN:` | 0 | `API_FREE search.list` 100u |
| FETCH_PROFILE | `API_FREE channels.list` | 1u | `LIB` |
| FETCH_VIDEO_METADATA | `API_FREE videos.list` | **1u por chamada, até 50 ids** | `LIB` yt-dlp `--dump-json` (0) |
| FETCH_METRICS | `API_FREE videos.list part=statistics` | 1u | — |
| FETCH_COMMENTS | `API_FREE commentThreads.list` | 1u/100 | `LIB` yt-dlp `--write-comments` |
| **FETCH_CAPTION** | **`LIB` yt-dlp `--write-auto-subs --skip-download`** | **0** | `API captions.download` = **só do dono**, 200u → `✖` para nós |
| FETCH_MEDIA (áudio) | `LIB` yt-dlp `-f bestaudio -x` | 0 | só quando não há legenda |
| INCREMENTAL | RSS + ETag (**304 não consome quota**) | 0 | |
| DELETE_DETECTION | `videos.list` por lote de ids → id ausente = removido | 1u | não distingue removido/privado/geobloqueado |
| STREAM | PubSubHubbub — push real de upload novo | 0 | precisa de callback público |

**Conta de quota:** 10.000u/dia grátis. Isso é ~500.000 registros de metadados de vídeo
(lotes de 50) **desde que `search.list` nunca seja usado para vigiar canal**.
Teto sugerido: ≤20 `search.list`/dia (2.000u) só para descoberta.

**AUTH:** `API_FREE` (chave, sem OAuth) + cookies locais para o yt-dlp.
**APIFY_NECESSITY: 0.** Nada aqui precisa de Apify.

---

## 2 · INSTAGRAM — valor agrícola IT: **ALTO** · qualidade de rota: **A PIOR**

| Capacidade | Rota | Realidade |
|---|---|---|
| SEARCH_KEYWORD | `LOCAL_AUTH` | API `✖` por completo |
| SEARCH_HASHTAG | `API_FREE ig_hashtag_search` | **teto de 30 hashtags únicas / 7 dias / conta** |
| FETCH_PROFILE | `API_FREE business_discovery` | **só contas profissionais**; sem contas com restrição de idade |
| FETCH_POST / FETCH_MEDIA | `LIB` gallery-dl / Instaloader + sessão | URLs de CDN são **assinadas e vencem** — baixar imediatamente |
| **FETCH_COMMENTS** | **`LOCAL_AUTH` / `LIB` / `APIFY`** | **A API dá a CONTAGEM, nunca o TEXTO de comentário de terceiro** |
| FETCH_CAPTION | `✖` não existe legenda | Reel → áudio → faster-whisper |
| INCREMENTAL | `end_cursor` opaco | **não é watermark** — é "varrer até achar conhecido" |
| DELETE_DETECTION | refetch do shortcode → 404 | custa 1 requisição por post |

**O que a API oficial NÃO dá em 2026:** busca por palavra-chave, texto de comentário de
terceiro, conta pessoal (não-profissional), alcance/impressão de terceiros. Basic Display
API foi desligada em set/2025.

**Saúde da rota não-oficial (verificada hoje):** Instaloader vivo (v4.15.1, 2026-03-21) mas
estruturalmente frágil — o Instagram aposenta `doc_id` de GraphQL e isso produz
**401 que PARECE rate limit e não é** ([issue #2532](https://github.com/instaloader/instaloader/issues/2532)).

> **REGRA DE DESENHO, DIRETO DAQUI:** `401 do Instagram ≠ recuar e repetir`.
> É `LIBRARY_STALE` — a biblioteca precisa ser atualizada. Tratar como backoff
> é gastar a noite inteira repetindo um pedido que nunca vai passar.

---

## 3 · FACEBOOK — **dividir a plataforma em duas**

| Capacidade | Rota | Veredito |
|---|---|---|
| **Anúncios do concorrente** | **`API_FREE` Ad Library API** | ✅ **O único endpoint Meta aberto, grátis e de risco zero.** Sob o DSA, **todos** os anúncios servidos na UE estão lá. Inteligência competitiva de agroquímico/máquina na Itália, semana 1 |
| Páginas de terceiro | `API_FREE` só com **PPCA** (raramente concedido) | adiar |
| Posts / comentários | `LOCAL_AUTH` / `APIFY` | adiar |
| **Grupos** | `LOCAL_AUTH` (precisa ser membro) | **EXCLUIR da coleta automática na v1** — maior exposição GDPR do conjunto |

CrowdTangle foi desligado em 2024-08-14. O sucessor (**Meta Content Library**) é restrito a
pesquisador com vínculo acadêmico/sem fins lucrativos, via ICPSR, **sem exportação de dados**.

---

## 4 · THREADS — **o ganho escondido**

A Meta entrega aqui a busca por palavra-chave pública que **recusa** no Instagram.

| Capacidade | Rota | Detalhe |
|---|---|---|
| **SEARCH_KEYWORD** | **`API_FREE threads_keyword_search`** | **2.200 consultas / 24h corridas**; TOP ou RECENT; filtro por media_type, faixa de data e usuário |
| DISCOVER_ACCOUNT | derivado do resultado da busca (`username`) | laço de descoberta real |
| INCREMENTAL | `since`/`until` unix | limpo |

**Porta de entrada:** sem aprovação da permissão `threads_keyword_search`, a busca só
enxerga os posts do próprio usuário autenticado. **App Review é o caminho longo — começar já.**

**Valor estratégico real para nós:** massa de conteúdo agrícola italiano no Threads é fina,
**mas o namespace de usuário do Threads é o MESMO do Instagram.** Usar o Threads como
instrumento legal e grátis de descoberta, e resolver a conta encontrada no Instagram.

---

## 5 · LINKEDIN — valor B2B **ALTO**, rota **A PIOR DE TODAS**

Nenhuma leitura de perfil/empresa de terceiro é oferecida **em nenhum preço**. Community
Management API = só páginas que administramos. `API_FREE` = só a própria identidade.

> **LinkedIn é a única plataforma do conjunto que notifica extrajudicialmente e litiga.**
> Recomendação honesta: **é a única onde NÃO devemos usar nossa sessão logada.**
> Ou aceitar Apify (que absorve comercialmente o risco de banimento), ou despriorizar.

---

## 6 · X / TWITTER — sinal de política, não de campo

`since_id` é o melhor incremental do conjunto (**A+**), e `GET /2/tweets?ids=` devolve
`errors[]` com lápide explícita por id ausente — melhor detecção de remoção depois do Bluesky.

**Preço mudou e importa:** o X migrou para **crédito pré-pago por uso** como padrão.
Tarifa amplamente reportada: **US$0,005 por post lido** (Basic legado fechado; Pro legado
depreciado em 2026-08-14, migrado para pay-per-use após 2026-09-01).
⚠️**NAO_VERIFICADO** contra a página oficial de preço — conferir antes de orçar.

**Conta que deve travar a decisão:** 200.000 posts/mês ≈ **US$1.000/mês**.
Teto sugerido: ≤20k leituras/mês (~US$100) sobre um conjunto estreito de termos agrícolas IT.

---

## 7 · TIKTOK — vídeo alto, texto baixo

| Capacidade | Rota |
|---|---|
| FETCH_PROFILE / METADATA / METRICS | **`LIB` yt-dlp `--dump-json`** — grátis, sem chave |
| FETCH_MEDIA | `LIB` yt-dlp |
| FETCH_CAPTION | `yt-dlp --list-subs` ⚠️**NAO_VERIFICADO** para 2026 |
| SEARCH / DISCOVER | `LOCAL_AUTH` |
| **FETCH_COMMENTS** | `LOCAL_AUTH` (assinatura `X-Bogus`/`msToken`) ou `APIFY` — **o endpoint com maior deriva do relatório inteiro** |

**Research API existe e faria tudo — e não somos elegíveis:** só instituição acadêmica ou
sem fins lucrativos, e *"em base não lucrativa"*. Produto comercial não qualifica.

---

## 8-11 · BLUESKY · MASTODON · TELEGRAM · REDDIT

| Plataforma | Rota principal | Nota decisiva |
|---|---|---|
| **BLUESKY** | `PUB_HTTP public.api.bsky.app`, sem autenticação | **Único firehose público grátis.** `STREAM` emite operação `delete` **e** `update` explícitas → **a única plataforma com evento de remoção E edição em tempo real.** `getPostThread` devolve a árvore inteira numa chamada. Conteúdo agrícola italiano ≈ zero, mas é **1 dia de trabalho e risco zero** → é o nosso banco de provas de pipeline |
| **MASTODON** | `PUB_HTTP /api/v1/timelines/tag/{tag}` por instância | `STREAM` grátis; `delete` e `edited_at` nativos. Massa italiana ≈ zero. Serve de alerta precoce de crítica a agroquímico |
| **TELEGRAM** | **`PUB_HTTP t.me/s/{canal}`** — sem autenticação nenhuma | Sinal de mercado/máquina italiano **sem concorrência**. `min_id` monotônico = incremental A+. **Nunca enumerar membros** (banimento + pesadelo GDPR). Só posts de canal |
| **REDDIT** | `PUB_HTTP` sufixo `.json` | Massa italiana ≈ zero; útil para agronomia global. **Melhor detecção de edição do conjunto:** corpo vira `[deleted]` vs `[removed]` (distinguíveis) + campo `edited`. ⚠️ Registro de app agora exige aprovação manual (Responsible Builder Policy) — ⚠️**NAO_VERIFICADO**, a página devolveu 403 |

---

## RANKING PARA A ITÁLIA

Pontuado por valor agrícola, massa de conteúdo italiano, valor de vídeo, valor de
descoberta, estabilidade de rota, qualidade de API, custo, esforço e risco legal.
**Não por popularidade geral.**

| # | Plataforma | Veredito |
|---|---|---|
| **1** | **YouTube** | **Construir primeiro.** Melhor razão valor/esforço da matriz inteira. Legenda grátis = a espinha do corpus de texto |
| **2** | **Instagram** | **Segundo apesar da rota péssima** — a economia de criador agrícola italiana está aqui. Aceitar manutenção permanente. Isolar em módulo próprio, com orçamento de falha próprio |
| **3** | **TikTok** | yt-dlp resolve 80% de graça. **Pular comentários na v1** |
| **4** | **Facebook — só Ad Library** | Vitória grátis, rápida, risco zero, semana 1. Página/Grupo: adiar ou largar |
| **5** | **Threads** | Massa baixa, **melhor instrumento legal e grátis de descoberta que podemos ter** — e resolve direto em handle do Instagram |
| **6** | **Telegram** | Barato, sem concorrência, sinal real de comércio italiano. Só canais |
| **7** | **X** | Só sinal institucional/política. **Teto duro de gasto** |
| **8** | **Bluesky** | Quase nenhum conteúdo agrícola italiano — mas **1 dia, grátis, risco zero**: construir **cedo como andaime de engenharia**, ranquear baixo como fonte |
| **9** | **Reddit** | Agronomia global, não Itália. Agora atrás de aprovação manual |
| **10** | **Mastodon** | Completude + alerta precoce de crítica a pesticida. Meio dia |
| **11** | **LinkedIn** | Valor de negócio alto, **todo o resto péssimo**. Por último, via Apify, ou não |

---

## APIFY — NECESSIDADE × CONVENIÊNCIA

**Necessidade = "nenhuma outra rota produz esta capacidade, dados os nossos ativos".**
Com IP residencial + sessão logada, esse conjunto é **quase vazio**.

| Plataforma + capacidade | Veredito | Caminho para zero |
|---|---|---|
| **Instagram FETCH_COMMENTS** | **NECESSIDADE (o caso mais forte)** | API só dá contagem. `LOCAL_AUTH` com ritmo estrito (poucas centenas de posts/dia, com jitter, uma conta descartável por PC) + aceitar cobertura parcial. Realista: Apify nos ~5% de posts com mais engajamento, `LOCAL_AUTH` no resto |
| **TikTok FETCH_COMMENTS** | **NECESSIDADE** | Tratar comentário como metadado opcional na v1 |
| **LinkedIn (tudo)** | **CONVENIÊNCIA — mas necessidade por TRANSFERÊNCIA DE RISCO** | Alcançável por `LOCAL_AUTH`; **não devemos**. Apify aqui compra *indenidade da nossa conta*, não capacidade. Razão legítima para manter |
| Instagram perfil/post/mídia/busca | CONVENIÊNCIA | business_discovery + gallery-dl + Threads |
| Facebook páginas | CONVENIÊNCIA | ou largar |
| **TikTok metadado/mídia/descoberta** | **DESNECESSÁRIO** | yt-dlp |
| **X (tudo)** | **DESNECESSÁRIO** (só arbitragem de preço) | Não trocar legalidade por centavos |
| **YouTube, Reddit, Bluesky, Mastodon, Telegram, Threads** | **ZERO necessidade, ZERO conveniência** | **Nunca rotear por Apify** |

> **APIFY_NECESSITY se reduz a exatamente DUAS células** — comentário de Instagram e
> comentário de TikTok — **mais uma célula de transferência de risco** (LinkedIn).
> Meta realista: **Apify ≤5% do gasto**, confinado a `comments`, com teto mensal duro
> e medidor de custo por item.

**Medido no acervo desta casa (Fase 0):** de US$12,81 de gasto Apify atribuído,
**US$12,33 (96%) é YouTube** — `youtube-comments-scraper` US$7,73 · `youtube-scraper`
US$4,47 · `youtube-transcript-scraper` US$0,13 — exatamente a plataforma onde a
necessidade de Apify é **zero**.

---

## VÍDEO — O CAMINHO MAIS BARATO

**Princípio:** `descobrir → metadado → legenda existente → (só se não houver) áudio → whisper`.
**Nunca baixar vídeo.**

| Plataforma | (a) descobrir | (b) metadado | (c) legenda SEM baixar | (d) só áudio |
|---|---|---|---|---|
| **YouTube** | RSS (0 quota) | `videos.list` 1u/50 | **`yt-dlp --write-auto-subs --sub-langs "it.*" --skip-download`** — nenhum byte de mídia | `-f bestaudio -x` (~1MB/min vs ~50MB/min) |
| **Instagram** | `LOCAL_AUTH` | GraphQL | **não existe legenda** | MP4 é muxado → `ffmpeg -vn -c:a copy` lendo por faixa do CDN assinado |
| **TikTok** | `LOCAL_AUTH` | `yt-dlp --dump-json` | `--list-subs` ⚠️**VERIFICAR** | `yt-dlp -f ba -x` |
| **Reddit** | `.json` | idem | ✖ | **faixa DASH de áudio é URL SEPARADA** (`DASH_audio.mp4`) — a mais barata de todas |
| **X / Bluesky / Mastodon** | API/search | API | ✖ | MP4/HLS → `ffmpeg -vn` |
| **Telegram** | t.me/s | idem | ✖ | Telethon baixa arquivo inteiro — **filtrar por duração/tamanho ANTES** |

> **Uma legenda automática do YouTube já existente é ~1000× mais barata que transcrever
> o mesmo vídeo.** É por isso que o YouTube é #1 — não por popularidade.

**Regras a codificar:**
`se houver legenda → nunca buscar mídia` ·
`se precisar de áudio → nunca puxar o fluxo de vídeo` ·
`se duração > N min → exigir nota de relevância antes de transcrever`.

---

## INCREMENTAL — DOIS MODOS, NÃO UM

| Nota | Plataformas | Primitiva |
|---|---|---|
| **A+** | X, Telegram, Bluesky | id monotônico / cursor de commit — **watermark real** |
| **A** | Reddit, Mastodon, YouTube | fullname / `since_id` / RSS+ETag |
| **B+** | Threads | `since`/`until` por timestamp (cuidado com empate) |
| **C** | **Instagram, TikTok, Facebook** | cursor opaco — **não é watermark**: é "varrer até bater em id conhecido" |
| **F** | **LinkedIn** | nenhuma — varredura completa toda vez |

> **Consequência de esquema:** precisamos de **duas** estratégias, não uma.
> `watermark_id` (X, Telegram, Bluesky, Reddit, Mastodon, YouTube) e
> `conjunto_conhecido` + "parar depois de K itens conhecidos seguidos" (IG, TikTok, FB).
> Guardar `collection_mode` por plataforma para o agendador saber qual é.

---

## REMOÇÃO E EDIÇÃO

| Nível | Plataformas | Mecanismo |
|---|---|---|
| **Tempo real** | **Bluesky**, Mastodon | evento `delete` e `update` no stream |
| **Lápide explícita** | Reddit (`[deleted]` vs `[removed]`, distinguíveis), X (`errors[]` por id) | grátis e confiável |
| **Diferença de conjunto** | YouTube (`videos.list` com N ids devolve só os vivos), Telegram (buraco na faixa de id) | barato em lote |
| **Refetch manual** | Instagram, TikTok, Facebook | **1 requisição por post** — caro |
| **✖** | LinkedIn | impraticável |

> **AUSÊNCIA NUMA RODADA ≠ REMOÇÃO.** Só há remoção onde a plataforma dá lápide, ou onde
> a diferença de conjunto foi feita sobre uma consulta que provadamente cobriu o id.

**Desenho recomendado:** um passo `verificacao` com estratégia por plataforma — push para
Bluesky/Mastodon (grátis, instantâneo), lote-barato para YouTube/X, e **reconferência
amostrada com cadência decrescente (1d/7d/30d)** para IG/TikTok/FB, aplicada **só aos posts
que já mostramos a um cliente**. Isso é, ao mesmo tempo, o pipeline de apagamento do
Art. 17 do GDPR.

---

## GDPR — DECLARAÇÃO HONESTA

Estamos estabelecidos na UE processando dado pessoal da UE. **O GDPR se aplica por inteiro,
e "era público" NÃO é base legal.**

| Ponto | Realidade |
|---|---|
| Base legal | Art. 6(1)(f) interesse legítimo é a única viável. Exige **LIA documentada**. Post de **empresa/marca** = risco baixo. **Comentário de pessoa física = risco alto** |
| Transparência | Art. 14: dever de informar quem não nos deu o dado. A derrogação 14(5)(b) exige **publicar aviso de privacidade descrevendo a coleta** — o caso *Bisnode* é o aviso de que confiar nela em silêncio falha |
| Categoria especial | Art. 9. Comentário sobre pesticida e saúde, opinião política sobre PAC/Green Deal → pode ser Art. 9. **Não construir perfil de pessoa nomeada** |
| DPIA | Art. 35 muito provavelmente disparado (monitoramento sistemático de área pública, em escala, com cruzamento). **Fazer DPIA antes de produção** |

**Mitigação a embutir na arquitetura:** (1) guardar handle de **criador/empresa**, mas
**pseudonimizar handle de comentarista na entrada** (HMAC com pepper rotativo);
(2) nunca guardar avatar/URL de perfil de comentarista; (3) agregar primeiro — persistir
tema/sentimento e manter texto bruto de comentário com TTL curto; (4) **excluir Grupos do
Facebook e lista de membros do Telegram**; (5) honrar remoção (acima) — é a defesa mais
forte em qualquer reclamação.

*O SINTONIA já tem o dono único desse assunto:* `scripts/instagram_pessoal.py`.
A camada nova não deve criar um segundo.

---

## NÃO VERIFICADO — não construir sem conferir

1. Tabela exata de preço por uso do X (US$0,005/leitura) — só fonte secundária.
2. Texto da Responsible Builder Policy do Reddit — página devolveu 403.
3. Se o TikTok expõe legenda automática por `yt-dlp --list-subs` em 2026.
4. Se a API do Threads devolve **perfil** e **thread de resposta** de terceiro, ou só busca.
5. Se `mbasic.facebook.com` ainda serve conteúdo sem JS em 2026.
6. Comportamento do `business_discovery` para conta profissional italiana sob DMA/DSA.
7. **Massa de conteúdo agrícola italiano por plataforma** — o ranking acima é raciocinado
   a partir do cenário de agro-influencer italiano e da demografia de plataforma,
   **não de contagem medida de corpus.** → **Rodar uma amostra manual de 200 contas antes
   de travar a ordem.** Esta é a lacuna de evidência mais importante do documento.

---

## RECOMENDAÇÃO NÃO PEDIDA, MAS MATERIAL

Um convênio formal com departamento de universidade italiana (economia agrária ou ciências
da comunicação) abre **três portas fechadas de uma vez**: TikTok Research API (busca por
palavra-chave, hashtag e **comentário**, grátis), Meta Content Library (conteúdo público de
Facebook **e Instagram, incluindo comentário**) e acesso de pesquisador validado do
Art. 40 do DSA (portal aberto em 2025-10-28, via Coordenador de Serviços Digitais nacional).

**Esse único convênio colapsa a zero as duas células restantes de necessidade de Apify e
tira a maior parte do risco de ToS das duas plataformas mais difíceis.** É, de longe, a
ação de maior alavancagem disponível — e não é de engenharia.

---

## FONTES

[quota YouTube](https://developers.google.com/youtube/v3/determine_quota_cost) ·
[captions.download](https://developers.google.com/youtube/v3/docs/captions/download) ·
[yt-dlp legendas](https://yt-dlp.net/guides/subtitles) ·
[yt-dlp bot check](https://yt-dlp.net/errors/sign-in-to-confirm-not-a-bot) ·
[IG business_discovery](https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/business-discovery) ·
[IG Hashtag Search](https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/reference/ig-hashtag-search/) ·
[Instaloader #2532](https://github.com/instaloader/instaloader/issues/2532) ·
[Threads Keyword Search](https://developers.facebook.com/docs/threads/keyword-search) ·
[Meta Content Library](https://transparency.meta.com/researchtools/other-data-catalogue/crowdtangle/) ·
[LinkedIn Community Management](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/community-management-overview) ·
[X API](https://docs.x.com/x-api/introduction) ·
[TikTok Research API](https://developers.tiktok.com/products/research-api/) ·
[TikTok Display API](https://developers.tiktok.com/docs/en/display-api-overview) ·
[Bluesky API hosts](https://docs.bsky.app/docs/advanced-guides/api-directory) ·
[Bluesky rate limits](https://docs.bsky.app/docs/advanced-guides/rate-limits) ·
[Telethon MTProto](https://docs.telethon.dev/en/stable/concepts/botapi-vs-mtproto.html) ·
[DSA Art. 40](https://digital-strategy.ec.europa.eu/en/news/commission-adopts-delegated-act-data-access-under-digital-services-act)
