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
| quatro idiomas provados | **3 PASS + IT PARTIAL** (nunca «4 PROVEN») | ES 3/3 · FR 2/2 · EN 2/2 · **IT 2/3** (a marca sai «di singenta») |
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

## D · LINKEDIN — TÉCNICO PROVADO, AUTORIZAÇÃO EM ABERTO

O coordenador pôs LinkedIn como P0. A medição **não o descarta**: mostra que a captura
por URL direta funciona e é melhor que a do Instagram, e que o que falta resolver mudou
de lugar — saiu da engenharia de captura e foi para **descoberta** e **autorização**.

### Tecnicamente, funciona — e melhor do que o Instagram

Amostra mínima, 1 post público, sem login, hoje:

| medida | resultado |
|---|---|
| `/company/<slug>/posts/` (listagem) | **HTTP 302 → `/uas/login`** |
| `/posts/<slug>-<activity_id>-<4>` (post) | **HTTP 200**, 114 KB, contém `<video data-sources>` |
| `yt-dlp -J --skip-download` | **funciona** |
| identidade | `id = 7151241570371948544` — **é o activity id**, identificador real da plataforma |
| mídia | **3 MP4 progressivos** (58/125/143 kbps) em `dms.licdn.com` — não HLS, não DASH |
| expiração | `e=2147483647` (≈ 2038) — **`LONG_LIVED_OBSERVED_URL`** |
| legenda nativa | **WebVTT com timestamps**, 4.283 B, obtida e legível |

> A legenda nativa muda o custo inteiro: para LinkedIn dá para ter transcript **com tempos,
> sem baixar vídeo e sem ASR**. É a rota mais barata que existe — e é a mesma lei de
> «legenda primeiro» que a casa já escreveu para o YouTube.

> ⚠️ **`LONG_LIVED_OBSERVED_URL`, não «permanente».** `e=2147483647` é o máximo de um
> inteiro de 32 bits, o que se lê como «sem expiração prevista». Isso é **uma observação,
> numa amostra, num dia** — não é garantia documental da plataforma. As quatro
> classificações que esta casa passa a usar são `TEMPORARY` · `LONG_LIVED_OBSERVED` ·
> `DOCUMENTED_STABLE` · `UNKNOWN`. Esta é a segunda.

### E mesma forma que o Instagram

```
DESCOBRIR: bloqueado.    CAPTURAR por URL direta: vivo.
```

### Por permissão, ainda não decidido — e isto NÃO é um parecer jurídico

**Correção ao que escrevi antes.** A primeira versão deste documento concluiu «o bloqueio
não é técnico, é de permissão, e engenharia não resolve». Isso **colapsou três coisas de
naturezas diferentes numa só** e transformou `robots.txt` em veredito. Está corrigido: cada
evidência entra no seu próprio eixo, e nenhuma delas, sozinha, decide.

| eixo | LinkedIn | evidência |
|---|---|---|
| `TECHNICAL_CAPABILITY` | **PROVEN, para a URL direta testada** | 1 amostra, hoje, medida acima |
| `ROBOTS_STATUS` | **RESTRICTED** | `User-agent: * / Disallow: /`; só LinkedInBot tem `Allow` |
| `TERMS_STATUS` | **REQUIRES_LEGAL/CLIENT_REVIEW** | User Agreement §8.2 alcança dado obtido «through third parties (such as data aggregators or brokers)» |
| `OFFICIAL_API_STATUS` | **RESTRICTED a Páginas próprias** | `r_organization_social` lê a Página que o app ADMINISTRA |
| `HOUSE_POLICY_STATUS` | **NOT_ALLOWED** | `leis/social_matriz.py` marca `FETCH_POST` `PERMITIDA=NAO` pelas duas rotas |
| `CLIENT_AUTHORIZATION_STATUS` | **UNKNOWN** | nunca foi perguntado ao cliente |
| `PRODUCTION_AUTHORIZATION_STATUS` | **REQUIRES_REVIEW** | consequência das linhas acima, não substituto delas |

```
robots.txt NÃO É PARECER JURÍDICO. É evidência operacional, e entra como uma linha
entre várias — nunca como a conclusão.
```

O que muda na prática: **o LinkedIn não está descartado.** O que está é a autorização de
produção, que é uma decisão humana e não uma medição. As saídas conhecidas são pedir
whitelist a `whitelist-crawl@linkedin.com`, entrar num programa de parceiro, obter
autorização explícita do cliente, ou desistir.

### E a pergunta técnica que ficou aberta

A pergunta já **não** é «conseguimos baixar vídeo do LinkedIn?» — numa URL direta,
aparentemente sim. É:

```
COMO DESCOBRIMOS LEGITIMAMENTE OS POSTS QUE QUEREMOS PROCESSAR?
```

E por isso `LINKEDIN` deixa de ser uma célula e passa a ser sete:

| capacidade | estado |
|---|---|
| `LINKEDIN_DIRECT_POST_CAPTURE` | TECHNICAL_CAPABILITY = PROVEN (1 amostra) |
| `LINKEDIN_NATIVE_VIDEO` | PROVEN (3 MP4 progressivos) |
| `LINKEDIN_NATIVE_CAPTIONS` | PROVEN (WebVTT com tempos) |
| `LINKEDIN_DISCOVERY` | **NOT_EXECUTED — é a pergunta em aberto** |
| `LINKEDIN_COMPANY_PAGE` | listagem → 302 login |
| `LINKEDIN_HISTORY` | UNKNOWN |
| `LINKEDIN_COMMENTS` | UNKNOWN |

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

---

## I · CLAIMS DOS AGENTES, VERIFICADOS POR MIM

O benchmark paralelo produz afirmações. **Nenhuma entra sem eu a repetir.** Estas três
eram as mais graves, e as três mudaram de forma ao serem medidas.

### I.1 · «`redigir()` não apaga uma DSN» — CONFIRMADO, e menor do que parecia

Reproduzido: `social_sessao.redigir()` **e** `apify_pool.redigir()` devolvem
`postgresql://postgres:SenhaSecreta123@…` **intacto**. A branch órfã
`operational-readiness-v1` já tem o conserto (uma regra `_CREDENCIAL_NA_URL`) e ele
**não está no HEAD**.

Mas medi também o caminho vivo, e ele é mais estreito do que a manchete sugere:
`coleta/coleta_checkpoint.py:65` corre `psql <dsn>` e passa `stderr` por `redigir()`.
Com um host inexistente, o `stderr` real do psql foi
`could not translate host name "db.…" to address` — **sem a senha**.

```
VERDICT · o GUARDA tem o buraco (CONFIRMADO).
          o VAZAMENTO na rota que consegui reproduzir NÃO aconteceu (NOT_REPRODUCED).
```

Não corrigido nesta missão: o conserto vive na outra linhagem, e importar código de lá é
exatamente o que esta missão não pode fazer. Entra em `AO · CONVERGÊNCIA PROPOSTA`.

### I.2 · «80 ficheiros RAW dizem PRESERVED e não existem» — CONFIRMADO, e a causa é outra

Contei: **111 registos** com `RAW_EVIDENCE_PATH`, **11 existem**, **100 não**. Dos ausentes,
**80 declaram `RAW_EVIDENCE_STATE = PRESERVED`**.

A causa **não é perda**. É política: `.gitignore:26` (`data/samples/**/*.gz`) exclui esses
ficheiros desde 2026-08-29, pela decisão D-003 — «o bruto pesado vai para Storage; o Git
guarda hash e manifesto». Os 11 que restam são os grandfathered dessa mesma decisão.

O defeito real é de **contrato**, e é mais interessante:

```
O registo tem RAW_EVIDENCE_PATH e RAW_EVIDENCE_STATE. Não tem NENHUM campo que diga
ONDE está preservado. «PRESERVED» aponta para um caminho que o repositório exclui de
propósito — e quem lê não consegue distinguir preservado-no-Storage de perdido.
```

Isto toca a lei da Collection de frente: `STORAGE_PATH` endereça o objeto físico e **não**
identifica a observação. Um `PRESERVED` sem endereço verificável não é preservação: é uma
afirmação não falsificável.

### I.3 · «o dono único de ASR é único» — PARTIAL, e agora quantificado

`grep -rn "WhisperModel(\|BatchedInferencePipeline("` no HEAD devolve **três linhas, todas
em `fala_local.py`**. No HEAD a lei vale.

Na ponta SCRAP não existe `fala_local.py` nem `reel_transcricao.py`, e existem **três**
carregadores separados. E `story_transcrever.py` repete, uma a uma, decisões que o HEAD já
mediu e reverteu:

| decisão | HEAD (medido) | `story_transcrever.py` (branch SCRAP) |
|---|---|---|
| `beam_size` | 1 — «5 custa o dobro por 2.079 contra 2.054 chars» | **5 fixo** |
| texto vazio | `REQUESTED_EMPTY` | **`OK`** — o defeito que o HEAD declara ter consertado |
| idioma | declarado quando o país é provado | **sempre detetado** |

```
SINGLE_ASR_OWNER = PARTIAL. Não é um refactor pendente: é a mesma lição aprendida
duas vezes, em dois sítios, com resultados opostos.
```

### I.4 · «`medium` é o padrão dos Reels» — preciso demais para ficar como estava

Há **quatro** constantes de modelo independentes: `fala_local` `small` ·
`instagram_transcrever` `small` · `youtube_transcrever` `small` · `reel_transcricao`
`medium`. O `medium` é o padrão **da cadeia `reel_transcricao`**, não «dos Reels» em geral.
Um Reel que entre pelo transcritor de Instagram sai em `small` — e é `small` que escreve
«MICE» onde se disse «mais».
