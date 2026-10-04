# SINTONIA SCRAP — CAPACIDADE SOCIAL MULTIPLATAFORMA

**Escopo desta missão:** `COUNTRY_SCOPE = IT`. A arquitetura aceita país como
parâmetro; ES e FR não foram tocados.
**Medido em:** 2026-09-08, deste host (runner hospedado, IP de datacenter).
**Apify gasto nesta missão:** **US$ 0,0000** — nenhuma execução paga.

---

## A DESCOBERTA QUE MUDOU A MISSÃO

A missão pediu **FREE-FIRST**. Medindo, a pergunta útil não era *"isto é
grátis?"* — era **"isto é permitido?"**. As duas divergem, e divergem justamente
onde uma casa apressada constrói o que vai jogar fora.

Três rotas gratuitas de YouTube foram **medidas funcionando** nesta máquina:

| rota | o que devolveu | veredito |
|---|---|---|
| `yt-dlp` busca por termo | 8 vídeos italianos em 1,6 s; achou **Bayer Crop Science Italia** e **Corteva** | `/results` e `/youtubei/` estão em `Disallow` |
| `feeds/videos.xml` do canal | 15 uploads com id, data exata, **descrição inteira (586–1148 chars)** e views | `Disallow: /feeds/videos.xml` |
| `yt-dlp` por vídeo | — | *"Sign in to confirm you're not a bot"* deste IP |

As três estão em caminho proibido pelo `robots.txt` do YouTube, e o §3 dos Termos
proíbe *"access the Service using any automated means"* fora do `robots.txt` ou
de permissão escrita.

> **ROTA QUE FUNCIONA NÃO É ROTA PERMITIDA.**

O mesmo se repetiu em X (`x.com` **e** `cdn.syndication.twimg.com` são os dois
`User-agent: * / Disallow: /`), Facebook (`Disallow: /`), TikTok (nomeia
`ClaudeBot`, `Claude-User`, `anthropic-ai` num bloco `Disallow: /`) e LinkedIn
(*"The use of robots or other automated means to access LinkedIn without the
express permission of LinkedIn is strictly prohibited"*).

**Consequência de arquitetura:** o portão de permissão virou código, não
comentário. `social_rotas.permitido()` lê o `robots.txt` **vivo** do host, com o
`User-agent` real da coleta, antes da primeira requisição. Ele já reprovou rota
que funcionava — é para isso que serve.

---

## O QUE SOBRA QUANDO SÓ O PERMITIDO CONTA

| categoria | plataformas |
|---|---|
| grátis **e** permitido, hoje, sem credencial | **MASTODON · BLUESKY · TELEGRAM** |
| permitido, mas exige credencial ou App Review | YOUTUBE (Data API v3) · THREADS (`keyword_search`) · FACEBOOK/INSTAGRAM (PPCA/PPMA) · X (pago por uso) |
| permitido só como **descoberta indireta** | LINKEDIN |
| sem rota própria permitida | TIKTOK (fora o oEmbed por URL conhecida) |
| porta anônima fechada em 2026 | REDDIT |

---

## O PILOTO REAL — 2026-09-08

15 execuções, **99 objetos distintos**, **US$ 0,00**, **zero Apify**.

| estado | n | leitura |
|---|---|---|
| `OK` | 8 | trouxe objeto |
| `ZERO_RESULTS` | 1 | rota sã, busca vazia |
| `BLOCKED` | 2 | Telegram: os dois canais não existem |
| `ROUTE_NOT_ALLOWED` | 2 | LinkedIn e TikTok, recusados pela política |
| `PAID_ROUTE_REFUSED` | 1 | X, recusado por falta de motivo canônico |
| `CREDENTIAL_MISSING` | 1 | YouTube Data API, sem chave nesta casa |

### Dois defeitos que o piloto pegou, e que um piloto só-feliz não pegaria

**1. A federação inflava a contagem em 19%.** O `id` do Mastodon é *local*: o
mesmo post federado ganha número diferente em cada instância. `mastodon.uno` e
`mastodon.social` devolveram os mesmos 19 posts com ids distintos, e a primeira
rodada declarou **118 distintos** quando eram **99**. A identidade correta é o
`uri` do ActivityPub.

> **ID LOCAL NÃO É IDENTIDADE. FEDERAÇÃO INFLA CONTAGEM.**

**2. País não é idioma — e o piloto provou isso contra si mesmo.** A busca por
`agronomo` no Bluesky devolveu agrônomos **espanhóis e brasileiros**, porque
`agronomo/agrónomo/agrônomo` não é palavra italiana, é palavra latina.

```
LANGUAGE declarado    {'it': 39, 'UNKNOWN': 33, 'es': 19, 'en': 6, 'pt': 2}
SOURCE_LOCATION       {'UNKNOWN': 99}
italiano declarado    39 de 99
Itália PROVADA        0 de 99
```

> **`COUNTRY_SCOPE=IT` É O RECORTE DO PEDIDO. NÃO É PROPRIEDADE PROVADA DO OBJETO.**

Nenhuma das rotas gratuitas declara país. Isso não invalida o corpus — invalida
qualquer frase que diga "coletamos 99 objetos italianos".

---

## APIFY DEPENDENCY MATRIX

Referência de preço: **o que esta casa já pagou de verdade** — 84 runs, 6.878
itens, US$ 12,81 → **US$ 1,86 por 1.000 itens**.

| plataforma | capacidade | veredito | motivo canônico |
|---|---|---|---|
| YOUTUBE | `FETCH_TRANSCRIPT` | **APIFY NECESSÁRIA** | `ROUTE_NOT_ALLOWED` |
| INSTAGRAM | `FETCH_COMMENTS` | **APIFY NECESSÁRIA** | `FREE_ROUTE_INSUFFICIENT_CAPABILITY` |
| INSTAGRAM | `FETCH_POST` | dispensável | rota do embed cobre os 12 recentes |
| FACEBOOK | `FETCH_POST` | dispensável | Graph API cobre, quando o App Review sair |
| LINKEDIN | `FETCH_POST` | **sem rota permitida** | nem livre, nem paga, nem Apify |
| TIKTOK | `DISCOVER_ACCOUNT` | **sem rota permitida** | idem |

**32 capacidades declaradas · 27 com rota padrão que não é Apify · 2 com Apify
como padrão · 2 sem rota permitida alguma.**

### X: API oficial ou Apify?

A X API acabou com as faixas Basic/Pro em 2026-02-06 e hoje é pay-per-usage
puro: **US$ 0,005 por post = US$ 5,00 / 1.000**, sem faixa gratuita de leitura,
teto de 3 milhões/mês.

Contra os US$ 1,86/1.000 medidos na Apify, **a API oficial custa ~2,7× mais por
objeto** — e ainda assim é a resposta certa, porque é a **única rota permitida**.
Aqui a decisão não é de preço.

### LinkedIn: risco registrado, não endossado

Esta casa **já gastou US$ 0,484** em 120 perfis via `harvestapi~linkedin-*`. O
§8.2 do User Agreement alcança explicitamente dado obtido *"through third
parties (such as data aggregators or brokers)"* — o intermediário não muda a
cláusula. A missão manda **não remover Apify agora**; fica declarado como
dependência legada com **risco jurídico aberto, para decisão humana**.

---

## LINKEDIN — COMO FICOU, DE VERDADE

Não existe API que leia post público de organização de terceiro:
`r_organization_social` é *"restricted to organizations in which the
authenticated member has ADMINISTRATOR / DIRECT_SPONSORED_CONTENT_POSTER /
CONTENT_ADMIN"*. Lê a **nossa** página, não a do concorrente.

O que ficou permitido é **DISCOVER, não FETCH**: colher a URL do LinkedIn do
**site da própria organização** (rodapé, *"seguici su"*), guardando
`DISCOVERY_SOURCE`, `DISCOVERED_URL`, `TARGET_TYPE`, `DISCOVERED_AT` — nunca
conteúdo de post fabricado. Ler o site da empresa não é obter informação do
LinkedIn; é obter da empresa.

Para vigilância ampla de concorrente no LinkedIn: **não existe rota permitida.**
Isso é uma resposta, não uma pendência.

---

## VÍDEO — O BURACO HONESTO

A cadeia de transcrição desta casa já existe e não foi recriada:
**legenda pública → `faster-whisper` local (US$ 0) → transcrição paga**.

O problema não está no Whisper. `captions.download` da Data API é **só do dono
do vídeo** (*"requires the user to have permission to edit the video"*), e não
há rota permitida até o **áudio** de canal de terceiro no YouTube. Sem áudio, o
Whisper local não tem o que fazer.

> **É LIMITE DE PERMISSÃO, E ELE É ANTERIOR AO LIMITE TÉCNICO.**

---

## ARQUIVOS

| arquivo | papel |
|---|---|
| `scripts/social_matriz.py` | a matriz declarativa: plataforma × capacidade × escada de rotas, com evidência e data |
| `scripts/social_rotas.py` | o portão de `robots.txt` vivo + os adaptadores permitidos + a política de rota |
| `scripts/social_envelope.py` | o envelope canônico, a dedupe por `PLATFORM + NATIVE_ID`, o RAW preservado |
| `scripts/social_scrap.py` | o executor composto: `censo · portao · video · gap · piloto · ledger` |
| `.github/workflows/sintonia-scrap.yml` | a porta de entrada, uma fase por execução, sem secret |
| `data/samples/SOCIAL-IT/` | artefato do piloto, ledger e RAW gratuito |

Nada em `supabase/`, nada em `italia-portale/`, nenhum arquivo existente
alterado — a missão paralela não foi tocada.

---

## O QUE FALTA PARA VIRAR COLETA DIÁRIA

1. **Chave da YouTube Data API v3** — destrava busca, uploads incrementais,
   metadados e comentários dentro de 10.000 unidades/dia. É o maior ganho por
   menor esforço desta lista.
2. **App Review da Meta** — `threads_keyword_search` (o único endpoint Meta
   desenhado para monitorar conteúdo público de terceiros) e PPCA/PPMA para
   Facebook.
3. **Alvos de Telegram** — a rota está provada, os canais agrícolas italianos
   ainda não foram descobertos. É trabalho de descoberta, não de engenharia.
4. **Rodar o piloto do runner local** — para separar *"a rota caiu"* de *"a rota
   caiu neste IP"* (Bluesky `searchPosts` e o player do YouTube barram este host).
5. **Decisão humana sobre o LinkedIn via Apify** — risco declarado acima.

---

# ADENDO — LOCAL_SESSION (sessão local autenticada)

**Medido em:** 2026-09-08. **Apify gasto:** US$ 0,00. **Teste real:** `NOT_RUN`.

## A pergunta que decide, e não é "a plataforma permite?"

Medindo os termos das sete plataformas prioritárias, o que separa o permitido do
proibido **não é a plataforma — é de quem é a conta**:

| | `OWN_PROPERTY` (conta da ADAMA) | `THIRD_PARTY` (conta de outro) |
|---|---|---|
| LOCAL_SESSION | **PERMITIDO** nas 7 | **NÃO** nas 7 |

Ler o próprio dado com a própria sessão é o que qualquer administrador faz.
Contra terceiro, a sessão autenticada vira exatamente o que os contratos
proíbem — e **estar logado piora, não melhora**:

| plataforma | cláusula que fecha a porta |
|---|---|
| LINKEDIN | User Agreement §8.2 — *"bots or other unauthorized automated methods"* |
| TIKTOK | Termos §5 — *"automated scripts to collect information"* |
| YOUTUBE | Termos §3 — *"any automated means"*, valendo logado e deslogado |
| FACEBOOK | `robots.txt` `Disallow: /`; a rota de terceiro é PPCA, com App Review |
| INSTAGRAM | a rota desta casa roda **deslogada** de propósito; logar muda a natureza do ato |
| X | `x.com` e o CDN de sindicância são `Disallow: /` |
| THREADS | a API `keyword_search` já faz o trabalho — sessão seria pior **e** proibida |

> **AUTENTICADO NÃO É AUTORIZADO A AUTOMATIZAR QUALQUER COISA.**

## Impacto real na Apify: nenhum, hoje

| capability | rota ANTES | rota DEPOIS | Apify antes | Apify depois |
|---|---|---|---|---|
| INSTAGRAM `FETCH_COMMENTS` | Apify | Apify | necessária | **ainda necessária** |
| INSTAGRAM `FETCH_POST` (>12) | Apify | Apify | necessária | **ainda necessária** |
| LINKEDIN `FETCH_POST` | Apify (legado) | sem rota permitida | usada | **continua sem rota** |
| YOUTUBE `FETCH_TRANSCRIPT` | Apify | Apify | necessária | **ainda necessária** |

**LOCAL_SESSION não reduziu a dependência de Apify em nenhuma capability.** Não
há o que comemorar: onde a sessão ajudaria, ela é proibida; onde é permitida
(conta própria), a API oficial já é a rota melhor. O ganho é a **infraestrutura
e as travas**, prontas para o dia em que houver permissão escrita ou uma conta
própria a ler.

## O que ficou construído

| arquivo | papel |
|---|---|
| `scripts/social_sessao.py` | política `OWN_PROPERTY`/`THIRD_PARTY` com cláusula citada, preflight, health, estados, `redigir()` |
| `scripts/social_guarda.py` | a trava: falha o commit se cookie, perfil ou segredo entrarem |
| `tests/test_social_sessao.py` | 30 testes, sem rede e sem conta real |
| `docs/operacao/HOW-TO-PROVISION-LOCAL-SESSION.md` | o guia de 5 minutos |

Reusados sem reescrita: `navegador.py` (acha o Chrome) e `cdp.py` (fala com ele).

## Três defeitos que os testes pegaram

1. **A redação vazava o token.** `redigir()` transformava
   `Authorization: Bearer <token>` em `Authorization=<REDIGIDO> <token>` — apagava
   o rótulo e **deixava o valor**. Pior que não redigir: parecia tratado.
2. **A guarda gritava do jeito certo.** Acusou três
   `Authorization: Bearer $SUPABASE_SECRET_KEY` — que é a forma correta. Guarda
   que grita demais é desligada, então ela passou a examinar o *valor*.
3. **Fixture com cara de credencial.** Meu próprio teste usava um JWT falso de
   20+ caracteres e disparou o scanner do repositório. Encurtado.

## Achado real, fora do escopo — não corrigido

`scripts/v21_tm_colher.py:55` embute um caminho pessoal de Windows
(`C:\Users\<usuário>\AppData\...`) como padrão de `LOCALAPPDATA`, expondo o nome
de usuário da máquina. É da cadeia v21, **não do SINTONIA SCRAP** — reportado e
listado em `DIVIDA_CONHECIDA`, não alterado, para não colidir com a missão
paralela. A correção é de uma linha e é sua para autorizar.
