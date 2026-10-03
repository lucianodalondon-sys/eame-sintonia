# PRÓXIMA MISSÃO — YOUTUBE, POR CAPACIDADE

> **Plano, não implementação.** Nada aqui foi executado. `yt-dlp` **não** foi
> instalado. Base: `docs/research/SINTONIA-SCRAP-CAPABILITY-MATRIX.md` e o veredito
> vivo de `scripts/social_matriz.py`.

---

## POR QUE YOUTUBE, E QUANTO ELE ATACA

Medido no acervo desta casa, somando `COST_USD` por ator nos manifestos:

| Ator | Gasto | Execuções |
|---|---|---|
| `streamers~youtube-comments-scraper` | **US$ 7,73** | 10 |
| `streamers~youtube-scraper` | **US$ 4,47** | 15 |
| `pintostudio~youtube-transcript-scraper` | US$ 0,13 | 13 |
| `harvestapi~linkedin-profile-scraper` | US$ 0,48 | 1 |

**US$ 12,33 de US$ 12,81 — 96% do gasto Apify histórico é YouTube.**
É o alvo por medição, não por opinião.

⚠️ Mas a economia potencial **não é 96%**: parte do YouTube não tem rota livre
permitida (abaixo). O número honesto de redução só sai depois de medir a rota
oficial com chave.

---

## NÃO EXISTE "A ROTA DO YOUTUBE"

Seis capacidades, seis respostas diferentes. Este é o ponto inteiro da missão.

| CAPACIDADE | OFFICIAL_API | YT_DLP | PUBLIC | LOCAL_SESSION | APIFY | **MELHOR ROTA** | PORQUÊ |
|---|---|---|---|---|---|---|---|
| **DISCOVER** (busca) | `search.list` · **100u** | `ytsearch` — `/results` **Disallow** | ✖ | `NOT_USABLE` (§3) | US$ | **`search.list`, com teto** | única permitida. Cara em quota: ≤20/dia = 2.000u |
| **METADATA** | `videos.list` · **1u até 50 ids** | `--dump-json` — `/youtubei/` **Disallow** e **`BLOCKED` de facto** ("Sign in to confirm you are not a bot") | `oembed` — só título/autor/thumbnail, **`CONDICIONAL`** | `NOT_USABLE` | US$ | **`videos.list`** | 50 ids por unidade: praticamente grátis |
| **COMMENTS** | `commentThreads.list` · **1u/100** | `--write-comments` — `/comment` **Disallow** | ✖ | `NOT_USABLE` | **US$ 7,73 gastos** | **`commentThreads.list`** | **o maior ganho isolado da missão** |
| **CAPTION** | `captions.download` · **só do dono**, 200u | `--write-auto-subs` — `/timedtext_video` e `/api/` **Disallow** | ✖ | `NOT_USABLE` | US$ 0,13 | **NENHUMA para terceiro** | ver o buraco honesto abaixo |
| **MEDIA** (áudio) | ✖ | `/get_video` **Disallow** | ✖ | `NOT_USABLE` | — | **NENHUMA para terceiro** | idem |
| **TRANSCRIPT** | — | — | — | — | US$ | **depende de CAPTION ou MEDIA** | derivação, não aquisição |

Verificado por mim, hoje, em `https://www.youtube.com/robots.txt`:
`Disallow: /feeds/videos.xml`, `/results`, `/youtubei/`, `/comment`, `/get_video`,
`/timedtext_video`, `/api/`.

> **`Disallow: /feeds/videos.xml` é literal.** O feed RSS de canal, que a matriz
> chegou a recomendar como a melhor rota de vigilância diária por custo zero,
> **está barrado.** A vigilância barata permitida é `playlistItems.list` sobre a
> playlist de uploads — **1 unidade por chamada**, não zero, e vale a pena.

---

## O BURACO HONESTO — DECLARADO, NÃO ESCONDIDO

Para vídeo de canal de **terceiro** no YouTube **não existe rota permitida até a
legenda nem até o áudio**. `captions.download` é só do dono; as rotas do `yt-dlp`
passam por caminho `Disallow`.

Sem áudio, o faster-whisper local **não tem o que fazer**. Isso não é limite do
Whisper — **é limite de permissão, e é anterior a ele.**

Consequência que precisa ser dita antes de alguém prometer corpus: **o corpus de
texto barato de YouTube não está garantido.** Ou se obtém permissão escrita, ou a
transcrição de terceiro continua sendo a única célula onde a Apify tem argumento —
e é por isso que `social_scrap gap` mostra `YOUTUBE / FETCH_TRANSCRIPT` como
**APIFY NECESSÁRIA · ROUTE_NOT_ALLOWED**.

**Não fingir que 96% do gasto some.** DISCOVER + METADATA + COMMENTS somam
US$ 12,20 (95%) e têm rota oficial permitida. CAPTION/TRANSCRIPT (US$ 0,13) não tem.

---

## O BLOQUEIO REAL É `CREDENTIAL_MISSING`

Todas as rotas oficiais acima estão na matriz com estado **`CREDENTIAL_MISSING`** —
não `BLOCKED`, não `ROUTE_NOT_ALLOWED`. **Conseguir a chave da Data API v3 é a
primeira tarefa da próxima missão, não uma otimização.**

Conta de quota: 10.000 unidades/dia grátis. Isso é ~500 mil registros de metadado
(lotes de 50) ou ~1 milhão de comentários — **desde que `search.list` (100u) nunca
seja usado para vigiar canal conhecido.**

---

## ORDEM SUGERIDA

1. **Chave da Data API v3** + `AUTH_STATUS` na matriz.
2. **COMMENTS** por `commentThreads.list` — ataca US$ 7,73, o maior item isolado.
3. **METADATA** por `videos.list` em lote de 50.
4. **DISCOVER** por `search.list`, **com teto de 20 chamadas/dia**.
5. **INCREMENTAL** por `playlistItems.list` + ETag (**304 não consome quota**).
6. **CAPTION/TRANSCRIPT**: **não implementar.** Registrar `ROUTE_NOT_ALLOWED` e
   manter a Apify como única rota, com motivo canônico declarado.

Cada passo entra como linha em `social_matriz.MATRIZ` e adaptador em
`social_rotas.ADAPTADORES` — **uma função e uma linha.** Se exigir tocar em mais de
dois arquivos, o contrato falhou e o passo para.

## `YT-DLP` NESTA MISSÃO

**Não instalar.** No YouTube ele está duplamente fora: caminho `Disallow` **e**
`BLOCKED` de facto deste IP. O valor dele para nós é em **TikTok e Facebook**, e é
outra missão. O padrão arquitetural dele (roteamento por `_VALID_URL`, envelope
congelado, flag `expected=`) **já foi copiado** — a flag virou `falhas.esperado()`.
