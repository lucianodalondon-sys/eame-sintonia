# INVENTÁRIO DAS FERRAMENTAS DE AQUISIÇÃO — medido em 2026-09-14

Este quadro **não** vem de lista antiga. Cada linha foi medida rodando a ferramenta
neste ambiente, nesta data. `PROOF` diz onde está a prova.

Ambiente da medição: contentor Linux, egress **Columbus, Ohio, US — AS396982 Google
LLC** (medido por `ipinfo.io`), sem `APIFY_TOKEN_POOL`, sem credenciais Supabase, sem
GPU, 4 núcleos de CPU.

| CAPABILITY | TOOL (dono canónico) | STATUS | INPUT | OUTPUT | INTEGRADO NA COLLECTION | PROOF |
|---|---|---|---|---|---|---|
| WEB_HTML | `coleta/italy_pilot_collect.mjs` | **PROVEN** | SOURCE_ID contratado | RUN + RAW + STORAGE + ledger | **SIM** — RUN e RAW canónicos | `evidencia/LAB-runs.ndjson`, 35 tentativas |
| PDF | `coleta/italy_pilot_collect.mjs` | **PROVEN** | rota do contrato | RAW PDF + SHA256 | **SIM** | 32 PDFs ARPAV/Campania/ARIF/APOL |
| WEB amostra (qualquer fonte) | `guarda/italy_preserve.mjs` | **PROVEN** | SOURCE_ID + URL | RAW + MANIFEST + SHA256 | **PARCIAL** — não escreve RUN | `evidencia/PRESERVACAO-54-FONTES.log`, 40/51 preservadas |
| PDF → texto | `pdftotext` (poppler 24.02) via contrato do piloto | **PROVEN** | ficheiro PDF | texto DERIVED | **SIM** | 40 DERIVED de PDF |
| HTML → texto | `ferramentas/html_text.mjs` | **PROVEN** | ficheiro/URL | texto DERIVED | **SIM** | 42 DERIVED de HTML |
| SCIENCE · ORCID | `coleta/corpus_pesquisador.py` | **PROVEN** | ORCID iD do universo congelado | RAW JSON por investigador | **PARCIAL** — não escreve RUN | 24 RAW em `data/raw/RESEARCHER-CORPUS/orcid/` |
| SCIENCE · OpenAlex | `coleta/corpus_pesquisador.py`, `coleta/universo_ciencia_it.py`, `coleta/speaker_universo.py` | **BROKEN** (mudança de plataforma) | filtro de obra | — | SIM, mas a rota fechou | HTTP 429 `"Insufficient budget… you only have $0 remaining"` · 17 tentativas |
| YOUTUBE · canal e objetos | `coleta/youtube_janela.py canais\|objetos` | **PROVEN** | lote congelado de contas | 8 canais, 240 objetos de vídeo | **NÃO** — não chega à admissão | `YOUTUBE-JANELA/CANAIS.json`, `OBJETOS.json` |
| YOUTUBE · legenda | `coleta/youtube_janela.py legendas` | **BLOCKED** neste ambiente | VIDEO_URL | — | NÃO | 24/24 `PORTA_NAO_ABRIU`; HTTP 429 na rota barata, navegador inalcançável |
| VIDEO · descarregar | `guarda/italy_preserve.mjs` (HTTP direto) | **PROVEN** | URL de média | RAW MP4 + SHA256 | PARCIAL | 3 vídeos, MD5 confere com o ETag do S3 |
| VIDEO · YouTube média | `yt-dlp` (declarado por `ferramentas/youtube_transcrever.py`) | **BLOCKED** neste ambiente | VIDEO_URL | — | NÃO | `"Sign in to confirm you're not a bot"` |
| CAPTION | `coleta/youtube_janela.py legendas` | **BLOCKED** neste ambiente | página do vídeo | — | NÃO | ver acima |
| TRANSCRIPTION | `ferramentas/youtube_transcrever.py`, `ferramentas/instagram_transcrever.py` | **PARTIAL** | áudio | texto + idioma | **NÃO** — não chega à admissão | vídeo CAI transcrito, 58 segmentos, `it` p=0,970 |
| TRANSLATION | `faster-whisper task='translate'` | **PROVEN** | áudio | texto EN separado do original | NÃO | `evidencia/VIDEO-TRANSCRICAO-E-TRADUCAO.json` |
| INSTAGRAM / REELS | `coleta/comunicacao_coleta.py posts INSTAGRAM` (Apify `apify~instagram-scraper`) | **BLOCKED** (credencial) | conta provada do lote | — | SIM, pelo caminho canónico | contrato do ator **APROVADO** (build 0.0.781); `POOL_STATE=POOL_EMPTY`, 0 runs, 0 USD |
| FACEBOOK | `coleta/comunicacao_coleta.py posts FACEBOOK` (Apify `apify~facebook-posts-scraper`) | **BLOCKED** (credencial) | conta provada do lote | — | SIM | contrato **APROVADO** (build 0.0.387); `POOL_EMPTY` |
| LINKEDIN | `coleta/comunicacao_coleta.py posts LINKEDIN` (Apify `harvestapi~linkedin-post-search`) | **BROKEN** (contrato) | conta provada | — | SIM | contrato **REPROVADO**: `companyUrls` e `maxItems` não existem no build 0.0.111; `postedLimit='30d'` fora do enum |
| YOUTUBE pago | `coleta/comunicacao_coleta.py posts YOUTUBE` (Apify `streamers~youtube-scraper`) | **BROKEN** (contrato) | canal provado | — | SIM | contrato **REPROVADO**: `dateFilter='2026-08-15'` fora do enum publicado |
| SCRAP social (rotas grátis) | `.github/workflows/scrap-social.yml` | **BROKEN** | fase | — | declarado, não entregue | os três coletores que ele invoca **não existem em `main`** |
| NAVEGADOR | `ferramentas/navegador.py` + `ferramentas/cdp.py` | **BLOCKED** neste ambiente | URL | — | usado pelo YouTube/Instagram | Chromium 141 encontrado, mas `Running as root without --no-sandbox is not supported` |
| ORQUESTRADOR | `pedido/orquestrador.py` | **PROVEN** | frase de pedido | RUN-MANIFEST + admissão | SIM | plano resolvido ao vivo |
| ADMISSÃO | `admissao/admissao.py` | **PROVEN** | item + universo | SIM/NAO/NAO_SEI/NAO_SE_APLICA/ERRO | SIM | 84 decisões novas |
| SALA DE ESPERA (ficheiro) | `pedido/orquestrador.py` → `data/samples/PRONTO-PARA-INTELIGENCIA/` | **PROVEN** | itens admitidos | linhas prontas | SIM | 6 linhas, de 0 |
| SALA DE ESPERA (banco) | `guarda/importar_italia.py` + Supabase | **UNKNOWN** | artefato JSON | SQL idempotente | SIM | sem credenciais neste ambiente — nada foi medido |
| COLETA AGENDADA IT | `coleta/italy_recurrent_collect.mjs` | **PROVEN** (recusou corretamente) | perfil | RUN + ledger | SIM | `FAILED_PRECONDITION` / `VPN_NOT_ITALY`, `SOURCE_NOT_MEASURED=3` |

## CAPABILITY_GAP registados

```
CAPABILITY_GAP = TRANSCRIÇÃO POR GPU
   Os dois donos canónicos (`ferramentas/youtube_transcrever.py:191` e
   `ferramentas/instagram_transcrever.py:247`) fixam `device='cpu',
   compute_type='int8'` no código. NÃO existe nenhuma rota CUDA/GPU versionada
   neste repositório. A operação usa a placa de vídeo da máquina local
   (`eame-sintonia-local`), e essa configuração NÃO está no Git.
   CONSEQUÊNCIA: quem clonar o repo e correr a ferramenta transcreve em CPU.

CAPABILITY_GAP = RUN FORA DO PILOTO ITALIANO
   Só `coleta/italy_pilot_collect.mjs` e `pedido/orquestrador.py` escrevem RUN.
   `guarda/italy_preserve.mjs`, `coleta/youtube_janela.py` e
   `coleta/corpus_pesquisador.py` coletam sem recibo de corrida.

CAPABILITY_GAP = COLHEITA DE VÍDEO E DE REDE SOCIAL NÃO CHEGA À ADMISSÃO
   Nenhum dos executores de YouTube, Instagram ou vídeo declara `larga_em` em
   `pedido/receitas.py`. A colheita fica no ficheiro e o orquestrador não a leva
   à porta.

CAPABILITY_GAP = IMPRENSA TÉCNICA
   Terra e Vita e AgroNotizie não existem na base qualificada de 54 fontes.
   Não foram coletados porque SOURCE_ID não se fabrica.
```
