# LINKEDIN ENRICHMENT — V1

**Data:** 2026-09-04 · **Branch:** `claude/linkedin-enrichment-v1-y1gikl`
**`REPROCESSAMENTO_DO_RAW_EXISTENTE_API_COST` = US$ 0** · execuções pagas iniciadas: **0**

> **Este número não diz que "o LinkedIn ficou grátis".** Ele descreve o
> **reprocessamento** do que já foi adquirido. Coleta **nova** de perfil ou de post
> continua dependendo das rotas e do provider já existentes, e **pode ter custo**.
> O whisper é local (`API_COST = US$ 0`) e ainda assim depende de **mídia
> legitimamente disponível** — e o custo dele é hora de máquina, não zero.
> O RAW relido **foi pago**: ver `COST_USD` das execuções `ES-T8-002-*` em
> `RUN-MANIFEST.json`.
>
> ```
> REPROCESSAR O JÁ PAGO ≠ COLETAR DE GRAÇA
> ```

Frente separada para enriquecer pesquisadores, técnicos e outras fontes humanas
**que já existem** no universo canônico. Não cria dono de identidade, não duplica
pessoa, não toca o portal, e não coletou nada em massa.

> **Estado: NÃO INTEGRADO AO CANÔNICO.** Vive em `data/samples/LINKEDIN-ENRICHMENT/`
> e em `scripts/linkedin_enriquecimento.py`. Nada foi ligado ao pipeline principal.

---

## A · CAPACIDADE ATUAL — o que a casa já tinha antes desta missão

Antes de escrever uma linha, o mapa. **Nenhuma rota nova foi criada: as que
existem cobrem perfil e post, e a que falta não falta por falta de código.**

| pergunta | dono atual | estado |
|---|---|---|
| `PROFILE_ROUTE` | `harvestapi~linkedin-profile-scraper` via `coletor.executar` | **FUNCIONA** — 138 pessoas + 62 páginas de empresa já pagas (US$ 0,484) |
| `PROFILE_SEARCH_ROUTE` | `harvestapi~linkedin-profile-search-by-name` | **FUNCIONA, MODO CURTO** — devolve nome, lugar e URL; não devolve cargo |
| `POST_ROUTE` | `harvestapi~linkedin-post-search` | **FUNCIONA** — 472 posts brutos, 372 únicos |
| `POST_BY_PROFILE_ROUTE` | `apimaestro~linkedin-profile-posts` (`linkedin_sensores.py`) | **DECLARADA, NUNCA EXECUTADA** — nenhuma execução no manifesto |
| `VIDEO_ROUTE` | `postVideo.videoUrl` dentro do RAW do post | **EXISTIA E NINGUÉM TINHA OLHADO** |
| `CAPTION_ROUTE` | — | **NÃO EXISTE NA ROTA PAGA**; existe como mecanismo público (`data-captions-url`), **não observado no nosso conteúdo** — ver **C5** |
| `MEDIA_ROUTE` | `postImages`, `document.transcribedDocumentUrl`, `article.link` | **EXISTIA E NINGUÉM TINHA OLHADO** |
| `WHISPER_ROUTE` | `youtube_transcrever.py`, `instagram_transcrever.py` | **JÁ ESTÁ NO MAIN** — não há branch experimental a mergear |
| `CURRENT_AUTH_METHOD` | `APIFY_TOKEN_POOL`, só no GitHub Actions | chave nunca existiu no contêiner de sessão |
| `CURRENT_CACHE` | nenhum cache de HTTP; RAW `.gz` preservado + retomada de transcrição | ver defeito **D-2** |
| `CURRENT_RATE_LIMIT` | nenhum backoff; rotação de chave por estado | ver defeito **D-3** |
| `CURRENT_PROVENANCE` | `proveniencia.py` + `RUN-MANIFEST.json` + `DATASET_OWNER` | **o ponto mais forte da casa** |
| `CURRENT_FAILURE_STATES` | `apify_pool.classificar` — dez estados nomeados | **melhor que todo o código aberto varrido** |
| `CURRENT_IDENTITY_OWNER` | `speaker_identidade.py` → `SPEAKER-UNIVERSE-PILOT-V1.json` (`PERSON_ID`) | 13 pessoas canônicas |
| `CURRENT_CHANNEL_LINK_OWNER` | `sensor_canal_identidade.py` → `SENSOR-PILOT/CANAL-IDENTIDADE.json` | 7 perfis PROVADOS, 5 pessoas |

### O que já estava duplicado, e não foi resolvido aqui

**Existem DOIS espaços de identidade de pessoa no LinkedIn, e eles não se tocam:**

```
PERSON_ID   (SPEAKER-UNIVERSE-PILOT-V1)   13 pessoas, âncora ORCID + OpenAlex
ORIGIN_ID   (ES-VOICE-LINKEDIN)          202 origens, âncora campo declarado
```

Dos 138 perfis de pessoa relidos, **zero** ligaram a um `PERSON_ID`. Não é falha
da regra de ligação: é que o corpus espanhol nasceu de busca por termo e o
universo canônico nasceu de recorte técnico. **Eles nunca se cruzaram.** Unir os
dois por nome parecido criaria pessoa — e é exatamente o que este V1 se recusa a
fazer. Fica declarado como pergunta aberta, não resolvido em silêncio.

---

## B · O QUE A NORMALIZAÇÃO JOGAVA FORA

O achado que sustenta a frente inteira. **Tudo já estava pago.**

### Perfis — 138 pessoas

| campo | presente no RAW | preservado no normalizado |
|---|---|---|
| `experience` | 135 (98%) | ❌ |
| `skills` | 121 (88%) | ❌ |
| `education` | 118 (86%) | ❌ |
| `currentPosition` | 124 (90%) | ❌ |
| `about` | 87 (63%) | ❌ |
| `languages` | 56 (41%) | ❌ |
| `certifications` | 37 (27%) | ❌ |
| `publications` | 11 (8%) | ❌ |
| `websites` | 9 (7%) | ❌ |

O artefato normalizado guardava nome, headline, localização, seguidores e URL.

### Posts — 472 brutos / 372 únicos

| campo | presente | preservado |
|---|---|---|
| `postImages` | 291 (62%) | ❌ |
| `article` | 93 (20%) | ❌ |
| `postVideo` | 56 (12%) | ❌ |
| `document` (PDF) | 20 (4%) | ❌ |
| hashtags no texto | 341 | ❌ |
| `PROFILE_MENTION` | 113 | ❌ |
| `COMPANY_NAME` | 353 | ❌ |

---

## C · AS TRÊS MEDIÇÕES QUE DECIDIRAM O DESENHO

### C1 · A rota pública de perfil está fechada — e isso encerra a busca por scraper

Cinco alvos canônicos com LinkedIn **PROVADO**, `GET` sem cookie e sem login:

```
Blanca B. Landa          HTTP 999   authwall   1530 bytes   sem JSON-LD   sem OpenGraph
Jesús Mercado-Blanco     HTTP 999   authwall   1530 bytes   sem JSON-LD   sem OpenGraph
Antonio Logrieco   (IT)  HTTP 999   authwall   1530 bytes   sem JSON-LD   sem OpenGraph
Andrea Sánchez-Vallet    HTTP 999   authwall   1530 bytes   sem JSON-LD   sem OpenGraph
Nicola Mori        (IT)  HTTP 999   authwall   1530 bytes   sem JSON-LD   sem OpenGraph
```

**O obstáculo é ACESSO, não parsing.** Nenhum parser conserta um 999. Os projetos
de código aberto que passam disso passam por cookie de sessão, replay de
credencial ou evasão de anti-bot — e as três estão fora do que esta casa faz.
Por isso a rota paga continua sendo a rota, e por isso nenhum scraper foi escrito.

> `HTTP 999 ≠ PERFIL INEXISTENTE`. É estado de acesso, e sai como tal.

### C2 · A URL de mídia é assinada e VENCE

As 56 URLs de vídeo do corpus capturado em **2026-08-29** carregavam
`e=1788580800` — expiração em **2026-09-05**. Sete dias de vida.

```
RAW PRESERVADO ≠ MÍDIA PRESERVADA
```

O `.raw.json.gz` fica para sempre dizendo que havia vídeo. O vídeo some. Quem
quiser a fala precisa buscar a mídia **perto da coleta**, não meses depois.
Medido no último dia útil da janela: **56 de 56 alcançáveis, HTTP 200, sem login**,
398 MB no total. Os 12 PDFs de carrossel: **12 de 12**, mesma condição.

### C3 · Vídeo não é fala, e o whisper alucina sobre música

Três vídeos de origens que a casa **já conhecia**, whisper local `small`/int8:

| origem | áudio | transcrição | estado |
|---|---|---|---|
| Celestino Domínguez Infante | 64 s | 823 caracteres de fala técnica sobre repilo | `TRANSCRIPT_OK` |
| demoFARM Andalucía (autoridade pública) | 19 s | `"¡Suscríbete!"` | `SUSPECTED_HALLUCINATION` |
| Alberto Giner | 22 s | nada | `NO_SPEECH_DETECTED` |

Os dois últimos foram **reconferidos sem filtro de voz**, para separar "o filtro
comeu" de "não havia fala": o áudio foi lido, a duração foi medida, e não havia
fala. `"¡Suscríbete!"` não é o que a demoFARM disse — é o que o modelo produz
sobre música e silêncio. **Se aquilo entrasse no corpus, o Sintonia teria
registrado uma autoridade fitossanitária andaluza pedindo inscrição num canal.**

```
VÍDEO ≠ FALA
TRANSCRIÇÃO VAZIA ≠ SEM ÁUDIO
FALHA DE ACESSO ≠ VÍDEO SEM LEGENDA
```

### C4 · E o mesmo defeito, num segundo decodificador

Os PDFs de carrossel são material técnico real — *Xylella fastidiosa buenas
prácticas agrícolas*, *Decreto FLYPACK DACUS TRAP*, boletim oficial, mesa do
olivar. O leitor da casa (`pdf_text.py`) devolveu para três deles **5.818, 5.755
e 15.447 caracteres**. Números grandes, texto nenhum:

```
"$ ) 2 5 2  / , 0 , 7 $ ' 2 , 1 6 & 5  % ( 7 (  $ 4 8"
```

Fontes embutidas com subconjunto próprio, sem `ToUnicode` utilizável. **O leitor
não errou por pouco: não decodificou e não disse isso.**

```
DECODIFICOU ≠ LEGÍVEL
```

Uma string longa com cara de sucesso é pior que um erro, porque atravessa o
pipeline calada. O guarda de legibilidade é a mesma disciplina do guarda de
alucinação, aplicada a outro decodificador.

### C5 · A legenda nativa existe como mecanismo, e não no nosso conteúdo

A varredura de código aberto afirmou que o LinkedIn expõe legenda **WebVTT
pública** em `data-captions-url`, presente em cerca de 6 de cada 10 vídeos
recentes. **Conferido sobre o nosso próprio corpus, em cinco posts de vídeo:**

```
5 posts   →   HTTP 200   ·   5 com fonte de vídeo   ·   0 com legenda
```

O mecanismo existe. No nosso conteúdo ele não aparece — é vídeo de criador agro
sem SRT anexado. Amostra pequena (5), e o estado é
`LEGENDA_NÃO_OBSERVADA_NO_NOSSO_CORPUS`, **nunca** "o LinkedIn não tem legenda".

**Consequência de custo:** se a legenda não existe no nosso tipo de conteúdo, o
degrau "legenda primeiro" não poupa hora de máquina aqui, e o whisper deixa de ser
o último recurso para ser o único. Isso encarece a escada — e reforça medir onde
há fala antes de transcrever em lote, já que **1 em 3 vídeos tinha fala**.

---

## C6 · O LIMITE QUE NÃO É TÉCNICO, E QUE DECIDE MAIS QUE O CÓDIGO

Tudo em **C2**, **C4** e **C5** funciona. Nada disso contornou controle nenhum:
sem cookie, sem sessão, sem CAPTCHA, sem evasão de anti-bot. E ainda assim:

```
https://www.linkedin.com/robots.txt   →   User-agent: *
                                          Disallow: /
                                          Disallow: /embed/feed/update/

https://dms.licdn.com/robots.txt      →   "The use of robots or other automated
                                           means to access LinkedIn without the
                                           express permission of LinkedIn is
                                           strictly prohibited."
```

**O host da mídia carrega a mesma proibição do site.** A rota gratuita de mídia,
legenda e PDF funciona **e mesmo assim não é uma rota que a casa possa passar a
usar em volume**, porque a plataforma pede explicitamente que não.

```
NÃO HÁ CONTROLE TÉCNICO ≠ HÁ PERMISSÃO
```

**O que foi feito:** sondagens pontuais e de volume pequeno, para responder "isto
é possível?" — 56 `HEAD` de vídeo, 3 downloads, 12 `HEAD` de PDF, 5 páginas de
embed. **Nenhuma coleta em volume foi iniciada.**

**O que continua limpo:** a releitura do `.raw.json.gz` **não toca a rede**. O dado
foi obtido pela rota paga e contratada e já está no repositório. Há teste que prova
que `scripts/linkedin_enriquecimento.py` não tem nenhuma chamada de rede.

**A decisão é do dono do produto, não minha.** Fica aqui como pergunta, com o
número ao lado.

---

## D · DEFEITOS ENCONTRADOS NO CANÔNICO — reportados, NÃO corrigidos aqui

A missão manda não integrar ao canônico ainda. Estes três ficam registrados com
arquivo e linha, para decisão separada.

**D-1 · Uma pessoa com três perfis "PROVADOS".**
`SENSOR-PILOT/CANAL-IDENTIDADE.json` dá a Antonio Logrieco **três** URLs
`PROVED`. Ou ele tem três contas, ou a regra aprovou homônimo. O V1 carimba
`MULTIPLE_PROVED_PROFILES` em vez de escolher uma em silêncio, mas **a regra de
identidade não foi tocada** — ela é de outro dono.

**D-2 · A chave de retomada do whisper ignora o modelo.**
`scripts/youtube_transcrever.py:199` —
`feito = {i['VIDEO_ID']: i for i in ... if i.get('TRANSCRIPT_STATE') == 'OK'}`.
O item grava `ASR_MODEL`, `ASR_BEAM`, `ASR_BATCH`; a chave lê só `VIDEO_ID`.
Rodar `rodar medium` depois de um `rodar small` **preserva o texto do `small` e
o reporta como feito**. O próprio docstring do arquivo mede `small`, `base` e
`tiny` como textos materialmente diferentes. Correção pequena: compor a chave com
os parâmetros de ASR, ou recusar item cujos parâmetros divirjam, com motivo dito.

**D-3 · O teto de páginas se disfarça de fim do cursor.**
`scripts/speaker_universo.py:155` — `while cursor and paginas < PAGINAS_MAX:` tem
duas saídas: cursor esgotado (fim real) e teto atingido (truncagem nossa). Em
`:193` as duas produzem `STATE = COLLECTED` com um `AUTHORS_FOUND` de aparência
real. O arquivo desenha essa distinção perfeitamente contra a **fonte**
(`THROTTLED_NOT_EMPTY`, contagem `None` e nunca `0`) e não a desenha contra **nós
mesmos**. É a mesma classe de erro que "12 posts" sem "de 1.973", que o caminho
do Instagram já se recusa a cometer.

---

## E · O QUE ENTROU DE FORA — um padrão, e só depois de medido aqui dentro

**A data que já estava dentro do id do post.** Os 41 primeiros bits do id de 19
dígitos são o instante de criação em milissegundos.

- **Origem:** `Ollie-Boyd/Linkedin-post-timestamp-extractor` — **GPL-3.0**.
- **Código NÃO copiado.** A licença não permitiria, e não precisa: o algoritmo é
  *prior art* pública (mesma técnica descrita para o TikTok, usada pelo Bellingcat).
  O que existe aqui é reimplementação a partir da descrição.
- **Conferido contra os nossos próprios dados antes de entrar:** bateu com o
  `postedAt.timestamp` da plataforma em **472 de 472**, diferença abaixo de 1 s.
  **Zero divergências.**

Serve para duas coisas, e a segunda vale mais:

1. **datar** o post quando a rota só deu data relativa (`"3mo"`, que envelhece);
2. **conferir** a data que a rota afirmou — discordância sai `DISAGREE`, nunca uma
   das duas escolhida em silêncio.

Há teste que **refaz a conferência sobre o RAW**: se o id parar de datar o post,
o padrão cai junto. Um padrão de fora só fica nesta casa enquanto continuar
medido dentro dela.

### O que NÃO entrou, e por quê

| padrão | origem | por que não |
|---|---|---|
| leitura de JSON-LD do perfil público | scrapfly (NPOSL-3.0) | a rota está atrás de authwall — **C1**. Licença também é não-comercial |
| cliente Voyager com paginação real | open-linkedin-api (MIT) | exige credencial LinkedIn no CI; conta desafiada, e é quebra de ToS |
| replay de `li_at`, `curl-impersonate`, resolvedor de CAPTCHA, pool de proxy | vários, os **mais recentes** | replay de credencial e evasão de controle de acesso. Fora do que esta casa faz |
| projetos sem `LICENSE` que anunciam MIT no README | vários | sem licença não há permissão |

**Nenhum dos projetos varridos registra proveniência. Nenhum extrai vídeo,
documento ou carrossel do LinkedIn.** Nesses dois eixos a casa já estava à frente
do campo inteiro, e não havia o que copiar.

---

## F · MICROTESTE — 5 perfis, `REPROCESSAMENTO_..._API_COST` = US$ 0

Os cinco escolhidos são exatamente as pessoas canônicas com LinkedIn **PROVADO**,
duas delas italianas — a preferência que a missão pediu.

| medida | resultado |
|---|---|
| `PROFILES_ATTEMPTED` | 5 |
| `PROFILES_OPENED` (rota gratuita) | **0** — 999/authwall nos cinco |
| `PROFILE_FIELDS_GAINED` (rota gratuita) | **0** |
| `POSTS_FOUND` (RAW já pago) | 372 únicos, 100 duplicatas removidas |
| `POSTS_WITH_TEXT` | 365 |
| `POSTS_WITH_DATE` | 372 (e 472/472 conferidos contra o id) |
| `POSTS_WITH_MEDIA` | 238 imagem · 70 artigo · 42 vídeo · 12 documento |
| `VIDEOS_FOUND` | 56 no RAW · 42 após dedupe |
| `NATIVE_CAPTIONS` | **0** — ausente na rota paga **e** ausente em 5/5 na rota pública |
| `MEDIA_OBTAINED` | **56 de 56** (HTTP 200, sem login) |
| `WHISPER_NEEDED` / `WHISPER_SUCCESS` | 3 rodados · **1 com fala utilizável** |
| `DOCUMENTS_REACHABLE` | **12 de 12** |
| `DOCUMENTS_DECODED` | **0 de 3 lidos** — mojibake |
| `NEW_FACTS` | 1 transcrição técnica sobre repilo, com proveniência |
| `NAO_SEI_RESOLVED` | 0 nesta amostra (as 472 datas já vinham); a rota fica aberta |
| `REPROCESSAMENTO_DO_RAW_EXISTENTE_API_COST` | **US$ 0** — e só isso; ver aviso no topo |
| `TIME` | ~19 s de whisper · ~47 s de varredura de mídia |

### O ganho real, e ele não está em rota nova nenhuma

**138 perfis × até 10 campos declarados** voltaram do RAW **já pago** —
experiência, formação, competências, o texto que a própria pessoa escreveu sobre
si. Nenhuma execução nova. **É o dado mais barato da casa: o que já foi pago e
não foi lido** — barato porque o preço já saiu, não porque foi de graça.

---

## G · ANTES × DEPOIS

| | antes | depois |
|---|---|---|
| campos de perfil aproveitados | 5 | **até 15**, cada um carimbado como declaração |
| mídia do post | descartada | vídeo, imagem, documento, artigo, com estado de validade |
| data do post | o que a rota disse | conferida contra o id, com `AGREE` / `DISAGREE` / `RESOLVED_BY_URN` |
| vídeo sem fala | indistinguível de falha de acesso | `NO_SPEECH_DETECTED` com duração medida |
| alucinação do ASR | entraria como voz da pessoa | `SUSPECTED_HALLUCINATION`, não promovida |
| PDF ilegível | 15.447 caracteres de lixo com cara de texto | `DOCUMENT_NOT_DECODED` |
| mídia vencida | "não havia vídeo" | `MEDIA_URL_EXPIRED` |
| perfil sem ligação provada | — | `IDENTITY = NÃO SEI`, nunca pessoa nova |
| provas automatizadas | 329 | **371** |

---

## H · O QUE O LINKEDIN ACRESCENTA — e o que ele não prova

**ACRESCENTA:** especialidade e trajetória declaradas (experiência, formação,
competências, publicações); a voz da pessoa em texto próprio; menção explícita de
organizações e de outras pessoas; documentos técnicos e regulatórios que ela
escolheu publicar; e, quando há fala, a fala.

**NÃO PROVA:**
- **cargo** — headline é como a pessoa se apresenta, não o que ela é;
- **localização do fato** — onde a pessoa mora não é onde o fenômeno ocorreu;
- **autoridade** — `FOLLOWERS ≠ AUTHORITY`, e curtida não é competência técnica;
- **censo** — o corpus veio de busca por termo, não de tudo que se publicou;
- **rede de pesquisadores** — os 138 perfis não tocaram nenhuma das 13 pessoas
  canônicas. A ponte entre os dois espaços de identidade **não existe ainda**.

**Radar Futuro e sinal de campo:** um único vídeo com fala técnica não sustenta
afirmação nenhuma. Fica como medida, não como sinal.

---

## I · VEREDITO

```
VERDICT = ADOPT_LIMITED
```

**Adotar — e isto não depende de decisão nenhuma, porque não toca a rede:** a
releitura do RAW já pago (ganho grande, risco zero, sem custo novo de API); a data derivada do
id, com a conferência que a autoriza; e os quatro guardas de estado — mídia vencida,
ausência de fala, alucinação de ASR, texto ilegível.

**Não adotar:** scraper próprio de LinkedIn em qualquer forma. A rota de **perfil**
está fechada por acesso (**C1**), e as maneiras de contorná-la estão fora do que
esta casa faz.

**Levar ao dono do produto, não decidir aqui:** a rota gratuita de mídia, legenda e
PDF. Ela **funciona** — 56/56 vídeos, 12/12 PDFs, sem login e sem contornar nada — e
o `robots.txt` do site **e do host de mídia** pede que não seja usada (**C6**).
Tecnicamente possível, e por isso mesmo a pergunta é de política, com uma saída
óbvia se a resposta for não: **a mídia também pode vir pela rota paga já contratada**,
que é como o vídeo chegou até aqui.

**Não escalar ainda.** Antes de qualquer coleta nova, três perguntas continuam sem
resposta, e todas as três são mais baratas de responder do que de ignorar:

1. **A ponte entre `PERSON_ID` e `ORIGIN_ID` existe?** Hoje, zero de 138. Sem ela,
   o LinkedIn enriquece um corpus que não é o universo canônico.
2. **A rota `POST_BY_PROFILE` funciona?** Está declarada em `linkedin_sensores.py`
   e nunca foi executada. Sem ela não há como pedir os posts *de uma pessoa* —
   só busca por termo.
3. **Vale a hora de máquina?** Um vídeo com fala em três. Antes de transcrever em
   lote, medir em quantos há fala — e a mídia vence em uma semana, então essa
   medição tem prazo.

**PARADO AQUI, como a missão mandou.**
