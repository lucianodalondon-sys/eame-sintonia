# SINTONIA SCRAP — ESTADO REAL V1

> **MEDIDO_EM:** 2026-09-10, no runner desta sessão.
> **MÉTODO:** Git é a autoridade. Cada afirmação abaixo tem commit, caminho:linha, comando
> ou URL. Nada foi herdado de relato.
>
> **ESTE DOCUMENTO NÃO SUBSTITUI** `docs/research/SINTONIA-SCRAP-ENGINEERING-BENCHMARK.md`,
> `docs/research/SINTONIA-SCRAP-CAPABILITY-MATRIX.md` nem
> `docs/arquitetura/SINTONIA-SCRAP-TARGET.md` (todos de 2026-09-08). Ele os **confere** e
> acrescenta o que mudou desde então — a frente de Reels e a medição de LinkedIn.

---

## A CORREÇÃO QUE ABRE TUDO

A missão anterior foi relatada como se tivesse partido do zero e construído a
transcrição de Reels. **Ela construiu — mas noutra árvore.** O SINTONIA SCRAP já existia,
com roteador, matriz de permissão, portão de robots e um piloto real, e a frente de Reels
não tocou em nenhum deles.

```
NÃO HÁ UM SINTONIA SCRAP. HÁ DOIS, E ELES NÃO SE CONHECEM.
```

| | router SCRAP | router EAME |
|---|---|---|
| ficheiro | `coleta/social_rotas.py` | `orquestrador/orquestrador.py` + `pedido/receitas.py` |
| registo | `ADAPTADORES` — 9 rotas `(PLATAFORMA, CAPACIDADE)` | `EXECUTORES` — 5 executores |
| portão de robots.txt | **SIM** (`permitido()`, linhas 82-122) | **não** |
| portão de permissão | **SIM** (`leis/social_matriz.py`) | **não** |
| portão de sessão | **SIM**, antes de navegar, padrão `THIRD_PARTY` | **não** |
| a frente de Reels entra por aqui? | **não** | sim (`T9`, `fase=transcrever`) |

Medido: `ferramentas/reel_transcricao.py` e `coleta/comunicacao_coleta.py` importam
`social_rotas`, `social_matriz` ou `social_sessao` **zero** vezes.

> **A rota de captura de Reels que a missão anterior provou corre SEM portão de robots e
> SEM portão de permissão** — enquanto o roteador irmão, no mesmo repositório, tem os dois.
> E a rota `yt-dlp` **não está declarada em `leis/social_matriz.py`**: nunca foi
> classificada pela lei da própria casa.

---

## A · GIT — ONDE ESTÁ CADA COISA

`INITIAL_HEAD = 9bed1b19` · branch `claude/jolly-archimedes-lqpvlf` · árvore limpa, pushada.

### Os 4 commits da frente de Reels — todos localizados e vivos

| commit | o que trouxe |
|---|---|
| `70a45e5a` | `fala_local.py` (dono único de ASR), `reel_transcricao.py` (a cadeia), refactor de `instagram_transcrever` e `youtube_transcrever`, trava do `"..."`, chave por RAW, campos de evidência |
| `1eac7254` | System Map + `TRANSCRIPT_WITHOUT_PRESERVED_PARENT` |
| `b72c575b` | a trava que o modo em lote não aplica, e a comparação dos três caminhos |
| `9bed1b19` | regeneração mecânica do mapa |

Cada afirmação do relato anterior foi rastreada com `git log -S`. Todas conferem.

### O patrimônio SCRAP vive noutras 6 branches, NENHUMA contida no HEAD

| branch | commit | o que tem de próprio |
|---|---|---|
| `claude/sintonia-scrap-stories-no-apify-v1` | `2d38a558` | **ponta da linha.** Stories sem Apify, trava que morde, CDP contra Chrome real |
| `claude/sintonia-scrap-stories-v1` | `e46539a3` | contida na de cima |
| `claude/sintonia-scrap-operational-readiness-v1` | `b030c3b2` | contida nas duas |
| `claude/sintonia-scrap-local-session-v1` | `946107d4` | linha própria — «o SCRAP aprendeu a perguntar *posso?* antes de *consegue?*» |
| `claude/scrap-social-na-biblia-v1` | `a1513382` | linha própria — piloto real (run 34258433872) |
| `claude/register-scrap-social-workflow-v1` | `b297f872` | foi para `main` |

Ficheiros que a ponta SCRAP tem e o HEAD **não** tem: `coleta/instagram_stories.py`,
`coleta/story_local.py`, **`ferramentas/story_transcrever.py`**, `ferramentas/apify_contrato.py`,
`ferramentas/apify_recuperar.py`, `medidas/fato_local.py`, `medidas/lugar_do_fato.py`,
mais 5 testes e 3 documentos de operação.

> **O «dono único de ASR» é único apenas nesta árvore.** `ferramentas/story_transcrever.py`
> instancia `WhisperModel` por conta própria (linha 98) e vive numa branch que o refactor
> nunca tocou. Num merge, voltam a ser três donos.

---

## B · O RELATO ANTERIOR, REPRODUZIDO

| afirmação | estado | prova |
|---|---|---|
| já existia um transcritor de Instagram | **PROVEN** | `ferramentas/instagram_transcrever.py`, anterior aos 4 commits |
| listing de perfil bloqueado (302 / 429) | **PROVEN, hoje** | `GET /syngentaitalia/` → 302 `/accounts/login/?…is_from_rle`; `yt-dlp instagram:user` → 429 |
| URLs diretas de Reel funcionam | **PROVEN, hoje** | reel novo baixado: 12.884.420 B, 145,4 s, sem login |
| um dono único de ASR | **PARTIAL** | único no HEAD; um terceiro existe em branch não integrada |
| transcript chega à classificação | **PROVEN** | `comunicacao_classificar.py` lê `TRANSCRIPT_TEXT` como fonte separada |
| trava do `"..."` | **PROVEN** | `fala_local._tem_conteudo`; teste passa |
| linhas duplicadas por Reel | **PROVEN** | chave passou a ser o RAW; teste `test_um_resultado_corrigido_substitui_o_antigo` |
| refactor do YouTube | **PROVEN** | nenhum `WhisperModel(` nos dois programas de lote |
| `medium` como padrão de Reels | **PROVEN** | `reel_transcricao.MODELO_PADRAO` |
| quatro idiomas provados | **PARTIAL** | ES 3/3 · FR 2/2 · EN 2/2 · **IT 2/3** (a marca sai «di singenta») |
| trava que o batched não executava | **PROVEN** | `_sem_os_mudos`, conferido contra a biblioteca instalada |

`python3 -m unittest tests.test_reel_transcricao` → **47/47 OK**.
`python3 provas/reel_fala_qualidade.py` → PASS 3 · PARTIAL 1 · NAO_CONFERIDO 6.

---

## C · A LEI QUE JÁ EXISTIA, E QUE A FRENTE DE REELS NÃO CONSULTOU

`leis/social_matriz.py`, medido em 2026-09-08, decide **permissão**, não capacidade.

```
LOCAL_SESSION contra TERCEIRO = NOT_USABLE nas sete prioritárias.
```

| plataforma | PUBLIC | OFFICIAL_API | LOCAL_SESSION | PAID_API | APIFY |
|---|---|---|---|---|---|
| INSTAGRAM | AVAIL/REVIEW | AVAIL+USABLE | AVAIL/NOT_USE | — | AVAIL/REVIEW |
| LINKEDIN | AVAIL/REVIEW | — | AVAIL/NOT_USE | — | — |
| FACEBOOK | — | AVAIL+USABLE | AVAIL/NOT_USE | — | AVAIL/REVIEW |
| YOUTUBE | AVAIL/REVIEW | AVAIL+USABLE | AVAIL/NOT_USE | — | AVAIL/REVIEW |
| X | — | — | AVAIL/NOT_USE | AVAIL+USABLE | — |

### robots.txt, medido por mim hoje

| host | `User-agent: *` |
|---|---|
| linkedin.com | **`Disallow: /`** + «The use of robots or other automated means to access LinkedIn without the express permission of LinkedIn is strictly prohibited.» |
| instagram.com | **`Disallow: /`** |
| facebook.com | **`Disallow: /`** |
| x.com | **`Disallow: /`** |
| youtube.com | **seletivo** — `/watch` e `/channel` livres; barrados `/api/`, `/comment`, `/feeds/videos.xml`, `/get_video`, `/youtubei/`, `/results` |

> **YouTube é a única das cinco que não é bloqueio total.** É onde uma pilha própria é
> defensável — e é, medido, onde a casa mais gastou com Apify.

---

## D · LINKEDIN — O CAPÍTULO QUE INVERTE A PRIORIDADE

O coordenador pôs LinkedIn como P0. A medição diz que o obstáculo **não é técnico**.

### Tecnicamente, funciona — e melhor do que o Instagram

Amostra mínima, 1 post público, sem login, hoje:

| medida | resultado |
|---|---|
| `/company/<slug>/posts/` (listagem) | **HTTP 302 → `/uas/login`** |
| `/posts/<slug>-<activity_id>-<4>` (post) | **HTTP 200**, 114 KB, contém `<video data-sources>` |
| `yt-dlp -J --skip-download` | **funciona** |
| identidade | `id = 7151241570371948544` — **é o activity id**, identificador real da plataforma |
| mídia | **3 MP4 progressivos** (58/125/143 kbps) em `dms.licdn.com` — não HLS, não DASH |
| expiração | `e=2147483647` (≈ 2038) — **URL efetivamente permanente** |
| legenda nativa | **WebVTT com timestamps**, 4.283 B, obtida e legível |

> A legenda nativa muda o custo inteiro: para LinkedIn dá para ter transcript **com tempos,
> sem baixar vídeo e sem ASR**. É a rota mais barata que existe — e é a mesma lei de
> «legenda primeiro» que a casa já escreveu para o YouTube.

### E mesma forma que o Instagram

```
DESCOBRIR: bloqueado.    CAPTURAR por URL direta: vivo.
```

### Por permissão, não

Três provas independentes, e todas dizem o mesmo:

1. **`leis/social_matriz.py`** — `FETCH_POST` por API oficial **e** por Apify:
   `PERMITIDA = NAO` / `ROUTE_NOT_ALLOWED`. Nota verbatim: *«`r_organization_social` lê a
   Página que o app ADMINISTRA — a nossa, não a do concorrente. Não existe API que leia
   post público de organização de terceiro. Para vigilância ampla de concorrente: NÃO
   EXISTE ROTA PERMITIDA. Isto é uma resposta, não uma pendência.»*
2. **robots.txt do LinkedIn** — `Disallow: /` para todos menos LinkedInBot.
3. **User Agreement §8.2** — alcança dado obtido *«through third parties (such as data
   aggregators or brokers)»*. O intermediário Apify não muda a cláusula. Já gastos
   US$ 0,484 em 120 perfis por essa rota, registados como dependência legada com risco
   jurídico aberto.

```
LINKEDIN_VIDEO_FEASIBILITY = YES tecnicamente · NO por permissão.
Engenharia não resolve isto. Só decisão humana resolve.
```

As saídas legítimas são três, e nenhuma é código: pedir whitelist a
`whitelist-crawl@linkedin.com`, entrar num programa de parceiro, ou desistir do LinkedIn.

---

## E · O QUE A FRENTE DE REELS DEIXOU NA MESA

A própria `CAPABILITY-MATRIX` já tinha escrito a lei: **«nunca baixar vídeo»**. A cadeia
de Reels baixa o MP4 inteiro. Medi o que isso custa:

| | vídeo completo | só a faixa de áudio |
|---|---|---|
| `C-FanW_CYMz` (34,1 s) | 1.788.869 B | **362.479 B** |
| transcrição | idêntica, 343 chars | idêntica, 343 chars |
| corpus de 8 reels | 35,9 MB | **7,3 MB** |
| projeção 1.000 reels | 4.492 MB | **910 MB** |
| na rota paga Apify (`$0,020`/MB iniciado/reel) | **$100 / 1.000** | **$20 / 1.000** |

O Instagram expõe a faixa de áudio separada (`dash-…a`, m4a 85 kbps) ao lado da faixa de
vídeo. **Baixar só o áudio dá o mesmo texto por ⅕ da banda.**

> Isto é uma recomendação medida, **não implementada**: esta missão é de medição.

---

## F · APIFY — O GASTO REAL, REPRODUZIDO

Somei todo `COST_USD > 0` com `ACTOR` em `data/samples/**`:

| actor | US$ |
|---|---|
| `streamers~youtube-comments-scraper` | 7,7280 |
| `streamers~youtube-scraper` | 4,4720 |
| `apify/harvestapi~linkedin-profile-scraper` | 0,4840 |
| `pintostudio~youtube-transcript-scraper` | 0,1300 |
| **TOTAL** | **12,8140** |

**96,2% do gasto é YouTube** — exatamente a plataforma onde o robots.txt não é bloqueio
total, onde existe API oficial `AVAIL+USABLE`, e onde a legenda nativa é grátis.

Censo de actors citados no código (idêntico nas duas linhagens): **13 distintos** —
6 de YouTube, 4 de LinkedIn/harvestapi, 3 de Instagram, 1 de Facebook.

---

## G · O QUE AINDA ESTÁ A SER MEDIDO

Um benchmark paralelo de 10 agentes corre neste momento sobre: censo linha a linha das
branches SCRAP · contrato e preço vivo dos 13 actors · Instagram (rotas de discovery
legítimas, incluindo Graph API business_discovery) · Facebook · X/Twitter · YouTube ·
estante OSS de captura · ASR alternativo e tradução.

Este documento será completado com esses resultados. **O que está escrito acima já é
medição, não previsão.**

---

## H · O QUE NÃO FOI FEITO, DE PROPÓSITO

Nenhuma branch foi integrada. Nenhuma migration. Nenhum toque em banco live, portal,
casco ou deploy. Nenhum merge. Nenhuma coleta ampla: cada teste de plataforma usou
**uma** amostra. Nenhum login, cookie de terceiro, CAPTCHA ou bypass.
