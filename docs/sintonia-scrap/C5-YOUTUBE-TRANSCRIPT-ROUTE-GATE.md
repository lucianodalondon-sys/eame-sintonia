# C5 · YOUTUBE TRANSCRIPT ROUTE GATE — a entrega

> **A pergunta:** existe HOJE uma rota de produção `YouTube de terceiro →
> transcript/caption` que seja ao mesmo tempo tecnicamente funcional,
> policy-compatible, operacionalmente sustentável e auditável — e que permita
> retirar os Actors pagos sem perder capacidade?
>
> **A resposta é NÃO**, e o que a fecha não é a técnica. É a autorização.

```
TRANSCRIPT_ROUTE_GATE = CLOSED

DECISÃO = D · BLOCKED_NEEDS_AUTHORIZATION

NENHUM ACTOR FOI RETIRADO. NENHUMA CAPACIDADE FOI PERDIDA.
NENHUMA ROTA NOVA FOI IMPLEMENTADA.
```

E uma coisa que esta missão encontrou sem a procurar: **onze das vinte e oito
transcrições que esta casa já pagou são traduções em inglês de vídeos que não
eram em inglês**, guardadas num campo chamado `TRANSCRIPT`.

---

# A · GIT

| campo | valor |
|---|---|
| **BRANCH** | `claude/sintonia-scrap-youtube-transcript-c5` |
| **SOURCE_BRANCH** | `claude/sintonia-scrap-local-gpu-c4` |
| **SOURCE_HEAD** (referência do coordenador) | `6ea058d3b5f67e0a74f4db09ab81d26d61d9c3f1` |
| **ACTUAL_INITIAL_HEAD** (medido) | `6ea058d3b5f67e0a74f4db09ab81d26d61d9c3f1` |
| **FINAL_HEAD** | o commit que traz este documento |
| **PUSH_STATE** | `PUSHED` · nenhum `force` |
| **WORKTREE** | `/home/user/eame-sintonia`, única e limpa |
| **DRIFT** | **NENHUM** |

O `fetch --all --prune` trouxe uma branch nova de outra frente
(`claude/executor-return-runtime-v1`). **Não foi lida nem fundida.**

---

# B · OFFICIAL CURRENT RULES

Cinco documentos oficiais, todos buscados em **2026-09-11**. Nenhum blog, nenhum
fórum, nenhuma memória.

### 1 · `captions.download` — a frase que fecha o assunto

| | |
|---|---|
| **SOURCE** | `developers.google.com/youtube/v3/docs/captions/download` |
| **FETCHED_AT** | 2026-09-11 |
| **RULE** | «This method is requires the user to have permission to edit the video.» |
| **IMPACT** | Para vídeo de concorrente, **não há rota oficial**. Não é limite de chave: é limite de **permissão**. |

Escopos exigidos: `youtube.force-ssl` e `youtubepartner`. Custo 200 unidades. Sem
a permissão devolve **403 `forbidden`**.

### 2 · `captions.list` — listar nunca foi ler

| | |
|---|---|
| **SOURCE** | `developers.google.com/youtube/v3/docs/captions/list` |
| **FETCHED_AT** | 2026-09-11 |
| **RULE** | Exige **OAuth**; a chave de API sozinha não autentica. Custo 50 unidades. E: «the API response does not contain the actual captions». |
| **IMPACT** | Mesmo que listasse, o texto continuaria atrás da `captions.download`. |

### 3 · `robots.txt` — e a linha que a casa citava estava trocada

| | |
|---|---|
| **SOURCE** | `youtube.com/robots.txt` |
| **FETCHED_AT** | 2026-09-11 |
| **RULE** | `Disallow: /api/` · `/comment` · `/feeds/videos.xml` · `/get_video` · `/results` · `/timedtext_video` · `/youtubei/` |
| **IMPACT** | A `baseUrl` que sai de `captionTracks` aponta para **`/api/timedtext`** — quem a cobre é o **`Disallow: /api/`**. |

```
A MATRIZ DESTA CASA CITAVA «/timedtext_video ESTÁ EM DISALLOW».
Está — e NÃO é esse o caminho que o código chamaria.

O VEREDITO ESTAVA CERTO E A PROVA ESTAVA TROCADA.
Uma citação errada cai no dia em que alguém a confere.
```

Corrigido nesta missão. E note-se o que **não** está em `Disallow`: `/watch` e
`/channel`. Isso importa para a secção seguinte.

### 4 · Termos de Serviço — a autoridade ACIMA do robots.txt

| | |
|---|---|
| **SOURCE** | `youtube.com/t/terms` |
| **FETCHED_AT** | 2026-09-11 |
| **RULE** | «access the Service using any automated means (such as robots, botnets or scrapers) except (a) in the case of public search engines, in accordance with YouTube's robots.txt file; or (b) with YouTube's prior written permission» |
| **IMPACT** | A excepção é para **motor de busca público**. O SINTONIA não é um, e não tem permissão escrita. |

Isto é mais largo que o `robots.txt`: mesmo o `/watch`, que o robots permite,
continua coberto — porque a excepção depende de **quem** acede, não de qual
caminho.

```
ROBOTS.TXT DIZ QUE CAMINHOS UM MOTOR DE BUSCA PODE PERCORRER.
OS TERMOS DIZEM QUEM PODE PERCORRÊ-LOS DE FORMA AUTOMATIZADA.
LER SÓ O PRIMEIRO É LER METADE DA LEI.
```

### 5 · Developer Policies — e esta casa está presa a elas

| | |
|---|---|
| **SOURCE** | `developers.google.com/youtube/terms/developer-policies` |
| **FETCHED_AT** | 2026-09-11 |

| secção | regra (verbatim) |
|---|---|
| **III.D.7** | «You must not use undocumented APIs without express permission.» |
| **III.E.6** | «You and your API Clients must not, and must not encourage, enable, or require others to, directly or indirectly, scrape YouTube Applications» |
| **III.I.14** | «use any technology other than YouTube API Services to access or retrieve API Data, including to access any portion of any YouTube audiovisual content» |
| **III.I.7** | «separate, isolate, or modify the audio or video components of any YouTube audiovisual content» |
| **III.E.1.a** | «download, import, backup, cache, or store copies of YouTube audiovisual content without YouTube's prior written approval» |

**Este é o documento que muda a conversa.** O SINTONIA usa a Data API com
`YOUTUBE_DATA_API_KEY` — logo é um API Client, e está preso a estas políticas,
não apenas ao `robots.txt`.

```
QUEM PEGA NA CHAVE PEGA NO CONTRATO QUE VEM COM ELA.
```

---

# C · CAPTIONS.LIST

```
CAN_LIST_THIRD_PARTY_CAPTION_TRACKS ?  NOT_PROVEN — e não foi tentado
AUTH_REQUIRED                          OAUTH (a API key NÃO serve)
OWNER_PERMISSION_REQUIRED              a doc não o diz; a mensagem de erro fala
                                       de «permissions ... not sufficient»
QUOTA                                  50 unidades
```

**Não foi executado, e a razão é a secção 8 do briefing.** Pedir OAuth ao dono da
casa para testar um método cujo resultado — mesmo no melhor caso — **não contém
o texto da legenda** seria ampliar acesso para não responder nada.

```
LISTAR UMA FAIXA NUNCA FOI O MESMO QUE PODER LÊ-LA.
```

A matriz ganhou linha própria para ele nesta missão, com estado
`REQUIRES_AUTHORIZATION`. Antes ele não existia na matriz — e um método ausente
é indistinguível de um método impossível.

---

# D · CAPTIONS.DOWNLOAD

```
CAN_DOWNLOAD_THIRD_PARTY_CAPTION ?   NO
OFFICIAL_TRANSCRIPT_ROUTE            NOT_AVAILABLE
ESTADO NA MATRIZ                     REQUIRES_OWNER_PERMISSION
```

A documentação viva, hoje, continua a dizer a mesma frase que a C2 já tinha
registado. Não mudou nada em três missões.

**E o estado dele mudou nesta missão, de propósito.** Estava
`ROUTE_NOT_ALLOWED`, que nesta casa significa «eu podia, e escolhi não». Não é o
caso: aqui a casa **não pode**, e quem tem a chave da porta é o dono do vídeo.

```
«EU NÃO QUIS» E «NÃO ME DEIXAM» NÃO SE ESCREVEM COM A MESMA PALAVRA.
```

---

# E · NATIVE / TIMEDTEXT

| eixo | estado | prova |
|---|---|---|
| **TECHNICAL** | `PARTIAL`, e **hoje não fecha** | `/watch` devolveu **429 + CAPTCHA** de IP de datacenter (2026-09-03, `@BayerAgri`); `timedtext` sem assinatura devolve **corpo vazio** |
| **POLICY** | `ROUTE_NOT_ALLOWED` | ToS (meio automatizado sem permissão escrita) · `Disallow: /api/` · III.D.7 · III.E.6 |
| **AUTHORIZATION** | `NOT_AVAILABLE` | não há permissão escrita |

O património técnico existe em `coleta/youtube_janela.py` e a cadeia é real:
página → `ytInitialPlayerResponse` → `captionTracks` → `baseUrl` assinado →
`timedtext` → segmentos com tempos.

**E continua fora.** Três autoridades independentes fecham-na, e a técnica
sozinha nem sequer a abre neste ambiente.

### O que NÃO conta como autorização

O código usa o navegador real da máquina local, pelo `cdp`, justamente porque o
429 é reputação de rede. Isso resolve o eixo **técnico** e não toca no eixo
**política**:

```
LOCAL / ONLINE É AMBIENTE.
NAVEGADOR REAL É AMBIENTE.
RUNNER RESIDENCIAL É AMBIENTE.

NENHUM DOS TRÊS É AUTORIZAÇÃO.
```

Um `robots.txt` não pergunta de que IP veio o pedido, e os Termos não abrem
excepção para Chrome.

---

# F · YT-DLP

| eixo | estado | prova |
|---|---|---|
| **TECHNICAL** | `BLOCKED` para metadados neste ambiente | «Sign in to confirm you are not a bot», de IP de datacenter |
| **POLICY** | `ROUTE_NOT_ALLOWED` | III.I.14 (outra tecnologia para obter API Data) · III.E.6 (scraping) |
| **AUTHORIZATION** | `NOT_AVAILABLE` | — |

A matriz já o tinha como `NAO` em duas capacidades, e **continua**. Medido em
`SEARCH_KEYWORD`: 8 resultados italianos em 1,6 s, achou o canal certo.

```
FUNCIONOU EM 1,6 SEGUNDOS, E CONTINUA PROIBIDO.
É exatamente a rota que funciona que precisa do registo — a que não funciona
ninguém tenta promover.
```

---

# G · LOCAL MEDIA + ASR

### Os dois lados, e por que são dois

| | estado | quem fecha |
|---|---|---|
| **ASR** (`ÁUDIO → TEXTO`) | **`PROVEN`** na C4, em CPU | ninguém — é capacidade da casa |
| **MEDIA** (`YOUTUBE → ÁUDIO`) | `BLOCKED` técnica **e** `ROUTE_NOT_ALLOWED` por política | III.E.1.a · III.I.7 · 403 de datacenter |

```
CAN_TRANSCRIBE_AUDIO  !=  CAN_ACQUIRE_YOUTUBE_AUDIO.

A C4 provou o primeiro. O segundo continua fechado, e a C5 mede que ele está
fechado por MAIS uma razão do que a C4 sabia.
```

### E a razão nova é a que importa

A C4 registou `youtube.media = BLOCKED` por motivo **técnico**: 403 de IP de
datacenter. A C5 mede que, mesmo que o 403 desaparecesse — num IP residencial,
por exemplo — a rota continuaria fechada:

- **III.E.1.a** proíbe «download, import, backup, cache, or store copies of
  YouTube audiovisual content» sem aprovação escrita;
- **III.I.7** proíbe «separate, isolate, or modify the audio or video
  components» — e extrair o áudio para o reconhecedor é exatamente isso.

```
UM BLOQUEIO TÉCNICO CONVIDA A PROCURAR OUTRO IP.
UM BLOQUEIO DE POLÍTICA NÃO SE RESOLVE MUDANDO DE REDE.
```

O reconhecedor local continua pronto e continua sem nada para ouvir, no que toca
ao YouTube. Ele serve os Reels do Instagram, que têm outra história de
autorização — e essa não é desta missão.

---

# H · CURRENT ACTORS

Censados contra as corridas reais preservadas em
`SENSOR-PILOT/RUNS-{A..E}.json` e `RUN-MANIFEST.json`. **Recontado, não
herdado.**

### `pintostudio~youtube-transcript-scraper`

| campo | medido |
|---|---|
| `RUNTIME_CALLERS` | 1 — `regras/sensor_coleta.py` |
| `RUNS` | **49** |
| `SUCCESS` / `FAILED` / `PARTIAL` | **28 / 19 / 2** → taxa de sucesso **57 %** |
| `MEASURED_USD` | **US$ 0,1300** |
| `NOT_PRESERVED_RUNS` | **20** |
| `UNKNOWN_USD` | 0 |
| itens produzidos | 48, dos quais **28 com texto** → rendimento **58 %** |
| `OUTPUT_FIELDS` | `TRANSCRIPT` · `TRANSCRIPT_AVAILABLE` · `TRANSCRIPT_LANGUAGE` · `CAPTION_SOURCE` · `WHY_EMPTY` |
| **timestamps** | **NENHUM** |
| `TRANSCRIPT_LANGUAGE` | **`NÃO SEI` em 48 de 48** |
| `CURRENT_ROLE` | única rota restante para legenda de terceiro |

### `starvibe~youtube-video-transcript`

| campo | medido |
|---|---|
| `RUNTIME_CALLERS` | 1 — reserva, só quando o primeiro recusa a **entrada** |
| `RUNS` | **0** — nunca executou |
| `MEASURED_USD` | **US$ 0,0000** |
| `CURRENT_ROLE` | reserva por **contrato**, não por medição |

```
APOSENTAR UM ATOR QUE NUNCA CORREU NÃO POUPA NADA.
E aposentar o que corre, sem substituto, perde a capacidade inteira.
```

---

# I · O QUE O ACTOR REALMENTE DEVOLVE

A secção 17 do briefing mandava não inferir pelo nome comercial. Medido sobre a
saída real preservada:

| pergunta | resposta medida |
|---|---|
| traz legenda nativa? | **sim** — os marcadores `[music]` (118×), `[laughter]`, `[snorts]`, `[clears throat]` são tokens de legenda automática do YouTube |
| faz ASR próprio? | **não há prova de que faça** |
| faz fallback? | não declara nenhum |
| declara a língua? | **não, em 48 de 48** |
| declara a espécie do texto? | **não** |

### E aqui está o que esta missão encontrou sem procurar

**Onze dos 28 textos são INGLÊS vindo de vídeo NÃO-inglês.**

| vídeo | título real | o que ficou gravado |
|---|---|---|
| `RisRARQSFAg` | «Periodico olivo 1° Maggio 2026» (AIPO Verona, descrição em italiano) | «Olive growers, welcome back to issue 18 of the May 1, 2026 periodical.» |
| `EAkcA_2FDN8` | «CONTRASTO ALLA FLAVESCENZA DORATA DELLA VITE» | inglês |
| `Ea-AcNeRDMU` | «Diserbo in post-emergenza, trattamenti erbicidi» | inglês |
| `G0oPuGlDkkU` | «Diserbo del mais in pre-emergenza con Adengo Xtra» | inglês |
| `J5ODH6Au_5E` | «Le mondine e il mostro delle risaie» | inglês |
| `-oMxkCI1ERc` | «Protection de la vigne en Champagne» | inglês |
| `6raOHsoibjk` | «Septoriose en blé d'hiver début avril 2026» | inglês |
| `QXwvQiufKxg` | «Septoriose et rouille du blé» | inglês |
| `rdDR4xgpQ4k` | «Mildiou et black-rot : comment protéger votre vignoble ?» | inglês |
| `rTOS8t1j174` | «Malezas: condiciones, emergencia, resistencia» | inglês |
| `w0Hd3H5coYY` | «Mosca Olivo 🪰 . Atracción 🧲» | inglês |

```
TRADUÇÃO ROTULADA COMO TRANSCRIÇÃO ORIGINAL É O PIOR DEFEITO POSSÍVEL NUM
CORPUS QUE EXISTE PARA SABER DE QUE CULTURA E DE QUE PRODUTO O CONCORRENTE
FALA, E EM QUE PAÍS.
```

Um termo agronómico italiano traduzido para inglês deixa de bater com o léxico
italiano. A peneira que procura «granella» nunca mais a encontra — e o vídeo
está lá, legendado, a falar de granella.

**Método, e o seu limite.** A classificação é por inspecção do título e da
descrição já preservados. Os onze acima têm título escrito em italiano, francês
ou espanhol — qualquer leitor confere lendo a coluna do meio. Um décimo-segundo
caso (`oIOoQaZXXzc`) foi **descartado**: o meu detector marcou-o por causa da
palavra «protection», que é francesa **e** inglesa. Falso positivo meu,
corrigido.

---

# J · QUALITY COMPARISON

```
NÃO FOI POSSÍVEL, E A RAZÃO É HONESTA.
```

Medido: **zero** vídeos têm ao mesmo tempo transcrição do actor e ASR local.

| corpus | itens | plataforma |
|---|---|---|
| transcrições do actor | 48 | YouTube |
| ASR local | 10 | Instagram (Reels) |
| **intersecção** | **0** | — |

A secção 28 pedia comparação «somente com material já existente» e proibia
adquirir mídia nova. **As duas coisas juntas fecham a comparação cabeça-a-cabeça**,
e inventar um corpus para a fazer seria produzir a evidência que se quer medir.

### O que ainda assim se pode comparar, porque não precisa do mesmo vídeo

| eixo | actor (48 itens medidos) | dono do ASR |
|---|---|---|
| timestamps | **nenhum** | `SEGMENTS` com início e fim |
| língua | `NÃO SEI` em 48/48 | `LANGUAGE` + `SOURCE` + `DETECTED` + `CONFIDENCE` |
| original vs tradução | 11 de 28 são tradução | declara a língua que transcreveu |
| rendimento | 28 de 48 com texto | estado declarado por peça |
| proveniência | só o nome do actor | motor, modelo, versão, ferro, transcritor |
| custo | US$ 0,13 + 20 `NOT_PRESERVED` | US$ 0, tempo de máquina |

O actor perde em todos os eixos menos **um** — e é o único que conta hoje: ele
consegue alcançar o conteúdo, e o caminho local não consegue.

---

# K · ROUTE MATRIX

| ROTA | TECHNICAL | POLICY | AUTHORIZATION | COST | THIRD-PARTY | PROD_READY |
|---|---|---|---|---|---|---|
| `captions.download` | n/a | permitida (API oficial) | **`REQUIRES_OWNER_PERMISSION`** | 200 un. | **NÃO** | **NÃO** |
| `captions.list` | `NOT_EXECUTED` | permitida (API oficial) | **`REQUIRES_AUTHORIZATION`** (OAuth) | 50 un. | `UNKNOWN` | **NÃO** |
| `timedtext` | `PARTIAL` (429 + corpo vazio) | **`ROUTE_NOT_ALLOWED`** | `NOT_AVAILABLE` | zero | sim | **NÃO** |
| `yt-dlp` legendas | `BLOCKED` neste ambiente | **`ROUTE_NOT_ALLOWED`** | `NOT_AVAILABLE` | zero | sim | **NÃO** |
| mídia local + ASR | ASR `PROVEN` · mídia `BLOCKED` | mídia **`ROUTE_NOT_ALLOWED`** | `NOT_AVAILABLE` | US$ 0 | — | **NÃO** |
| `apify:transcricao` (actual) | `PARTIAL` — 57 % sucesso | ver secção M | `CONDICIONAL` | US$ 0,13 medido | sim | **em uso** |
| provedores externos (3) | presumivelmente igual | **igual** | nenhum licenciado | varia | sim | **NÃO** |

---

# L · EXTERNAL PROVIDERS

Pesquisa limitada, como a secção 19 manda. Três classes de candidato, e **nenhuma
resolve o eixo que importa**:

| classe | capacidade | terceiro? | posição de política |
|---|---|---|---|
| API comercial (Supadata e equivalentes) | legenda de vídeo arbitrário | sim | acesso a endpoint **não documentado** |
| API comercial (OutlierKit / TranscriptAPI) | idem | sim | idem |
| biblioteca `youtube-transcript-api` | idem | sim | idem |

A própria literatura destes provedores descreve a posição como **«gray area»** e
**«risky territory»** para uso comercial de volume. Nenhum apresenta base
licenciada.

E há a frase que fecha a porta a todos de uma vez — **III.E.6**:

> «must not, **and must not encourage, enable, or require others to, directly or
> indirectly**, scrape YouTube Applications»

```
TROCAR DE FORNECEDOR MUDA A FATURA, NÃO O EIXO.
ZERO_APIFY != ZERO_PAID_PROVIDER != POLICY_COMPATIBLE.
```

Por isso **não se recomenda troca**: a secção 26 exige ganho concreto, e não há
ganho em política, nem prova de ganho em fiabilidade, proveniência ou qualidade.

---

# M · DECISION

```
D · BLOCKED_NEEDS_AUTHORIZATION
```

### WHY

Quatro rotas, quatro portas fechadas, e **nenhuma delas se abre com engenharia**:

1. `captions.download` — o dono do vídeo teria de autorizar;
2. `captions.list` — falta OAuth, e mesmo com ele não devolve o texto;
3. `timedtext` e `yt-dlp` — ToS, `robots.txt` e Developer Policies, três vezes;
4. mídia local + ASR — III.E.1.a e III.I.7, independentemente do IP.

```
O GATE NÃO ESTÁ FECHADO POR FALTA DE TÉCNICA.
ESTÁ FECHADO POR FALTA DE AUTORIZAÇÃO — e é por isso que a decisão é D e não B.
```

### Por que **não** foi B · `KEEP_CURRENT_APIFY_TRANSCRIPT`

Operacionalmente o resultado é o mesmo: **o actor fica, nada é retirado, nenhuma
capacidade se perde**. A diferença é o que a palavra declara.

`B` diria que o arranjo actual é a resposta. A medição não deixa dizer isso:

- 43 % das corridas falham;
- 11 dos 28 textos são tradução rotulada como transcrição;
- a língua nunca é declarada;
- não há tempos;
- e o próprio actor faz, por nós, aquilo que **III.E.6** diz que não se deve
  «encourage, enable, or require others to» fazer.

**Este último ponto é para a casa decidir, não para mim.** Eu reporto o que o
documento diz e que ele alcança terceiros que agem por nossa conta. Se isso muda
a relação com a Apify é juízo do dono do projeto — possivelmente com aconselhamento
próprio —, e não uma conclusão que uma missão técnica deva tomar sozinha.

```
DIZER «ESTÁ RESOLVIDO» SOBRE UM ARRANJO COM ESTES NÚMEROS SERIA
FECHAR O ASSUNTO EM VEZ DE O ENTREGAR.
```

### Por que não foi A nem C

`A` exigiria uma rota admissível. Não há.
`C` exigiria um substituto com ganho concreto. Não há.

---

# N · WHAT WOULD CHANGE THE DECISION

Quatro coisas, e **nenhuma delas é código**:

1. **Permissão escrita do YouTube** para acesso automatizado — a excepção (b) dos
   próprios Termos;
2. **Permissão de edição** concedida por cada canal-alvo, o que abriria
   `captions.download`. Improvável em escala de concorrente, possível em parceria;
3. **Mudança na API oficial** que passe a expor legenda pública de terceiro —
   hoje ela não existe, e não existia na C2 nem na C3;
4. **Um provedor com base contratual declarada** — não «gray area», mas licença
   que o provedor publique e que a casa possa ler.

E uma quinta que não abre o gate mas **muda o seu valor**: se a Apify publicar
qual espécie de texto entrega (original, traduzida, ou ASR próprio), o corpus
passa a poder distinguir o que já paga.

---

# O · TESTS / RED TEAM

**31 provas novas.** Ataques e resultados:

| # | ataque | resultado |
|---|---|---|
| RT1 | rota funciona tecnicamente, política diz NÃO | a matriz guarda as duas colunas; prova reprova se colapsarem |
| RT2 | API devolve metadados, download dá 403 | `captions.list` e `captions.download` têm linhas e estados diferentes |
| RT3 | navegador vê a faixa e isso vira autorização | prova reprova rota autorizada «por causa do navegador» |
| RT4 | `yt-dlp` funciona, alguém promove | prova reprova se sair de `PERMITIDA=NAO` |
| RT5 | provedor barato sem termos claros | secção L — nenhum tem base licenciada |
| RT6 | actor falha, alguém conclui que a capacidade não existe | `REQUESTED_EMPTY` continua distinto |
| RT7 | legenda automática rotulada manual | vocabulário fechado de espécies |
| RT8 | tradução rotulada transcrição original | **o defeito era real** — 11 de 28 |

### Duas correcções a sentinelas minhas, dentro desta missão

A primeira versão de duas provas lia **texto cru** em vez da árvore:

- uma reprovava o **comentário** que explica por que o actor fica, por ele citar
  `captions.download`;
- outra procurava `urllib.request` no próprio ficheiro — e encontrava-o, na lista
  do que procurava.

```
UMA SENTINELA QUE LÊ TEXTO REPROVA A EXPLICAÇÃO JUNTO COM O DEFEITO.
UMA SENTINELA QUE SE LÊ A SI PRÓPRIA ENCONTRA-SE SEMPRE.
```

As duas passaram a ler importações e literais na árvore sintática.

### E uma trava que faltava, encontrada por eu próprio a violar

`social_matriz.ESTADOS` era uma tupla fechada **que nada fazia valer**. Escrevi
dois estados novos e a suíte inteira passou sem reparar.

```
UMA LISTA FECHADA QUE NINGUÉM CONFERE É UMA LISTA ABERTA COM OUTRO NOME.
```

Agora há prova que varre a matriz inteira e reprova qualquer estado fora do
vocabulário.

---

# P · REGRESSIONS

```
BASE_TOTAL      1991        FINAL_TOTAL     2022
BASE_FAILURES     20        FINAL_FAILURES    20
BASE_ERRORS        1        FINAL_ERRORS       1
BASE_SKIPS       175

NEW_FAILURES       0
```

**Nenhuma regressão.** As 21 vermelhas finais são as mesmas 21 da base — dívida
anterior, nenhuma consertada aqui e nenhuma escondida.

---

# Q · UNKNOWNs

| pergunta | estado | porquê |
|---|---|---|
| `captions.list` funciona para terceiro com OAuth? | `NOT_EXECUTED` | pedir OAuth para um método que não devolve texto seria ampliar acesso por nada |
| que espécie de texto o actor entrega, item a item? | `NOT_KNOWN` | ele não declara, e inferir do conteúdo seria adivinhar duas vezes |
| quantos dos 28 são tradução, exactamente? | **11 confirmados** por título | o método é inspecção de título; casos de título ambíguo ficam de fora |
| os 20 `NOT_PRESERVED` custaram quanto? | `NOT_PRESERVED` | confissão preservada, não apagada |
| `timedtext` funcionaria de IP residencial? | `NOT_MEASURED` | **e não vai ser medido** — a política fecha antes da técnica |
| a relação com a Apify muda por causa de III.E.6? | **decisão da casa** | reportado, não decidido |
| qual o hardware local? | `NOT_MEASURED` | runner offline desde a C4 |

---

# R · VERDICTS

```
YOUTUBE_NATIVE_CAPTION_TECHNICALLY_PROVEN  = PARTIAL
     a cadeia existe em código e já produziu segmentos; hoje, deste ambiente,
     o /watch devolve 429 e o timedtext sem assinatura devolve vazio.

YOUTUBE_NATIVE_CAPTION_PRODUCTION_ALLOWED  = NO
     ToS · robots.txt · Developer Policies III.D.7 e III.E.6.

YOUTUBE_MEDIA_ZERO_APIFY                   = NO
YOUTUBE_TRANSCRIPT_ZERO_APIFY              = NO
YOUTUBE_ZERO_APIFY_TOTAL                   = PARTIAL
```

Os três últimos **não se mexeram**, e não se mexeriam por nada que esta missão
pudesse fazer: eles dependem de autorização, e autorização não se implementa.

### Critérios de PASS

| | critério | |
|---|---|---|
| P1 | estado actual medido | ✅ |
| P2 | rotas classificadas nos três eixos | ✅ |
| P3 | documentação oficial actual usada | ✅ cinco fontes, todas de 2026-09-11 |
| P4 | legenda nativa não promovida por conveniência | ✅ |
| P5 | chave de API não confundida com permissão de dono | ✅ estados separados |
| P6 | mídia e ASR continuam separados | ✅ |
| P7 | actores censados contra corridas reais | ✅ 49 corridas |
| P8 | custo real reproduzido | ✅ recontado |
| P9 | uma das quatro opções escolhida | ✅ **D** |
| P10 | nenhuma capacidade perdida | ✅ nada foi retirado |
| P11 | nenhum acesso proibido implementado | ✅ |
| P12 | nenhuma rota declarada sem prova | ✅ |

```
C5 = PASS. O gate fecha, e fecha com a prova na mão.
```

---

# S · KNOW_HOW_DELTA

```
KNOW_HOW_DELTA = ATUALIZAÇÃO NECESSÁRIA
```

Três coisas duráveis, e nenhuma é sobre YouTube em particular:

1. **quem pega na chave pega no contrato** — usar a Data API prende a casa às
   Developer Policies, que são mais largas que o `robots.txt` e alcançam
   terceiros que agem por nossa conta;
2. **tradução não é transcrição**, e um campo sem espécie declarada acaba por
   guardar as três como se fossem uma;
3. **uma lista fechada que ninguém confere é uma lista aberta com outro nome.**

---

# T · READY_FOR_NEXT_MISSION

```
YES
```

O gate está respondido e o caminho seguinte não é o que a casa esperava. Não é
retirar o actor — é **saber o que ele entrega**. O corpus tem 28 textos, 11 dos
quais traduzidos, e nenhum com a espécie declarada.

```
ANTES DE TROCAR QUEM TRAZ O TEXTO,
VALE SABER QUAL DOS TEXTOS É O QUE SE JULGA ESTAR A LER.
```
