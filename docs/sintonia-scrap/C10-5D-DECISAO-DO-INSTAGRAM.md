# C10.5D — A DECISÃO HUMANA DO INSTAGRAM, E AS TRÊS VERDADES QUE ELA NÃO COLAPSA

    INSTAGRAM_REMOTE_ACQUISITION = NOT_ALLOWED
    INSTAGRAM_LOCAL_ASR          = PROVEN
    REUSE_OF_PRESERVED_MEDIA     = ALLOWED

As três são verdadeiras ao mesmo tempo, e é por isso que este documento existe.
Escrever «Instagram = bloqueado» juntaria as três numa só e perderia duas.

---

## 1. O QUE FOI DECIDIDO, E POR QUEM

A decisão é humana e está tomada: **acesso remoto automatizado à superfície do
Instagram, pela rota medida de aquisição, não é permitido**.

A base é a medição da C10.5, refeita e confirmada: o `robots.txt` vivo de
`instagram.com` tem 6 256 bytes e o bloco que se aplica a esta casa é
`User-agent: *` seguido de `Disallow: /`. O agente desta coleta não aparece
nomeado em lado nenhum do ficheiro.

    ROTA QUE FUNCIONA NÃO É ROTA PERMITIDA.

O que esta decisão **não** diz:

- não diz que o reconhecedor local está proibido;
- não diz que os bytes já preservados nesta casa não podem voltar a ser processados;
- não rebaixa a capacidade medida.

```
CAN DO ≠ MAY DO ≠ DID DO
```

---

## 2. PRIMEIRO MEDIR, DEPOIS MUDAR — E A MEDIÇÃO MUDOU A MISSÃO

A correção óbvia era virar a linha da matriz de `SIM` para `NAO`. Medido
**antes** de a fazer, com a decisão simulada em memória:

| caminho | objetos | resultado | rede |
|---|---|---|---|
| aquisição remota | 0 | `ROUTE_NOT_ALLOWED` | 0 |
| reuso pela cadeia | 1 | `MEDIA_OK` | 0 |
| **reuso pelo adaptador** | **0** | **`ROUTE_NOT_ALLOWED`** | 0 |
| **reuso pelo executor canônico** | **0** | **`ROUTE_NOT_ALLOWED`** | 0 |

As duas últimas linhas são o achado. Um pedido que **traz os próprios bytes** —
ou cujos bytes já estão preservados — não precisa de autorização nenhuma, e era
recusado na mesma.

    O PORTÃO QUE RECUSA ANTES DE SABER SE VAI SAIR RECUSA TAMBÉM QUEM NÃO IA SAIR.

Isso é uma correção da C10.4, e é minha. A C10.4 pôs o portão no adaptador,
antes do `import` da cadeia, e a intenção era boa: `reel_transcricao` traz o
`yt-dlp` atrás dele. O preço só apareceu quando a política passou a dizer não.

O portão desceu para o ponto onde o socket abre, que é onde a C10.5 já o tinha
posto para a cadeia. O adaptador continua a ler a decisão — não para barrar, mas
para que o trace diga quem decidiu, mesmo quando a recusa nasce lá dentro.

---

## 3. O CONFLITO ESTRUTURAL, REGISTADO E NÃO RESOLVIDO

```
CONFLICT = o vocabulário de CLASSE não distingue «motor local» de
           «ferramenta local que sai à rede»

WHY      = a decisão precisa de dizer «podes transcrever, não podes ir buscar».
           Hoje as duas metades vivem na MESMA linha da matriz, e a classe que
           a nomeia — LOCAL_EXECUTOR — descreve ONDE a ferramenta corre, não SE
           ela toca a plataforma.

EVIDENCE = as quatro rotas LOCAL_EXECUTOR da matriz, medidas uma a uma:
             YOUTUBE/SEARCH_KEYWORD        yt-dlp:ytsearch        toca a plataforma
             YOUTUBE/FETCH_VIDEO_METADATA  yt-dlp:extract_info    toca a plataforma
             TELEGRAM/INCREMENTAL          MTProto/TDLib          toca a plataforma
             INSTAGRAM/FETCH_TRANSCRIPT    instagram_transcrever  toca a plataforma
           As quatro saem. Nenhuma é um motor puro sobre bytes já em casa — e o
           comentário da classe dá como exemplo justamente o `faster-whisper`,
           que é a única coisa que não sai.
           AUTH_MODE não separa: LOCAL_EXECUTOR é `PUBLIC`, igual a DIRECT_HTTP.

RECOMMENDED_NEXT_STEP =
           decidir, com gente, se nasce uma classe para «motor local sem acesso
           à plataforma» — e só então declarar a rota do ASR local como linha
           própria. Enquanto isso não existir, o roteador canônico recusa a
           capacidade inteira, e essa recusa é CORRETA: a matriz nunca declarou
           uma rota local-only para ela.
```

Por isso este documento não inventa classe nem capacidade nova. A regra é a do
briefing: dúvida estrutural para, o resto continua.

---

## 4. ONDE A DECISÃO FOI ESCRITA

Uma linha, em `leis/social_matriz.py`, e nada mais:

```
INSTAGRAM / FETCH_TRANSCRIPT
  ANTES   PERMITIDA = SIM   ESTADO = PROVED
  DEPOIS  PERMITIDA = NAO   ESTADO = ROUTE_NOT_ALLOWED
```

O `NAO` pertence àquela rota porque **aquela rota sai**: `instagram_transcrever.py`
baixa o MP4 inteiro da CDN da Meta e só depois transcreve. Não é um motor local,
apesar da classe.

E o estado escolhido é `ROUTE_NOT_ALLOWED`, não `BLOCKED`. A casa já tem essa
distinção escrita:

```
ROUTE_NOT_ALLOWED   eu podia, e decidi não fazer.
BLOCKED             a plataforma impediu-me tecnicamente.
```

Escrever `BLOCKED` poria na plataforma a culpa de uma decisão desta casa.

**O que NÃO foi tocado:** `coleta/scrap_capacidades.py` continua a declarar
`instagram.reel.transcribe = PROVEN`, e tem de continuar.

    PROVEN ≠ AUTHORIZED_REMOTE_ROUTE. São dois donos, dois ficheiros, duas
    perguntas.

---

## 5. AS TRÊS PROVAS

### PROVA A · a política diz não

```
YT_DLP_CALLS    = 0        METADATA_CALLS = 0
SOCKETS         = 0        MEDIA_STATE    = ROUTE_NOT_ALLOWED
degraus         = [('LOCAL_YTDLP', 'ROUTE_NOT_ALLOWED')]
```

`AUDIO_ONLY_UNAVAILABLE` **não** foi usado como substituto. O som está lá; o que
falta é autorização, e o artefato diz isso.

> **A primeira versão desta prova era inválida.** Usou a sentinela preservada, o
> degrau 0 encontrou os bytes no disco e devolveu `MEDIA_OK` — mediu a gaveta,
> não o portão.
>
>     UMA PROVA DE RECUSA QUE NUNCA CHEGA A PEDIR NÃO MEDE A RECUSA.

### PROVA B · o reuso sob o não

Bytes preservados reais, 968 697, `VIDEO_STREAMS = 0`, `AUDIO_STREAMS = 1`:

```
NETWORK = 0    YT_DLP_CALLS = 0    objetos = 1
ASR     = LOCAL_ASR · OK    TRANSCRIPT_CHARS = 2 374
SOURCE_ID = NAO SEI    POLICY_DECISION = ROUTE_NOT_ALLOWED
```

Uma transcrição completa produzida **debaixo de uma política que proíbe
adquirir**. É isso que `REUSAR ≠ ADQUIRIR` significa na prática.

### PROVA C · a política diz sim, sem tocar a plataforma

Com `SIM` injetado em memória e transporte falso, o caminho chega à porta de
aquisição e pede exatamente o que sempre pediu:

```
['-f', 'bestaudio', '-o', '…/x.%(ext)s', 'https://www.instagram.com/reel/…']
SOCKETS = 0 · a plataforma não foi tocada
```

O portão não destruiu a capacidade técnica. Ele decide **quando** ela corre.

---

## 6. RED TEAM — DEZ TENTATIVAS, NOVE QUEDAS

| # | tentativa | medida |
|---|---|---|
| 1 | metadados saem antes do portão | `meta=None`, 0 yt-dlp, 0 rede |
| 2 | yt-dlp arranca antes do portão | pergunta L530 < saída L538; L425 < L429 |
| 3 | política NÃO desliga o ASR local | ASR chamado, 1 objeto, 0 rede |
| 4 | **bytes entregues passam por adquiridos** | **NÃO CAIU** — ver §7 |
| 5 | `PROVEN` técnico atropela a política | capacidade `PROVEN`, 0 yt-dlp, 0 rede |
| 6 | recusa de política vira `BLOCKED` | `ESTADO = ROUTE_NOT_ALLOWED` |
| 7 | o adaptador inventa `SOURCE_ID` | `SOURCE_ID = NAO SEI` |
| 8 | o adaptador fabrica `DOCUMENT_ID` | nenhuma chave `DOCUMENT_ID` |
| 9 | o teste passa sem chegar à aquisição real | a mesma chamada: 0 com `NAO`, 4 com `SIM` |
| 10 | a sentinela encontra-se a si própria | nenhum ficheiro sem exclusão |

O nº 9 é o que dá valor aos outros: prova que os testes **chegam** à função real
de aquisição, e que é o portão — e não um caminho morto — que os para.

---

## 7. O QUE A DECISÃO TORNOU MAIS AGUDO, E NÃO FOI CORRIGIDO AQUI

```
CONFLICT = sob uma política que proíbe adquirir, um registo de mídia entregue
           pelo chamador ainda escreve AUDIO_ONLY_ACQUISITION = PROVEN

WHY      = a etiqueta trata «não adquiri porque reusei a gaveta» e «não adquiri
           porque me entregaram» de formas diferentes. A primeira sai
           REUSED_NOT_ACQUIRED; a segunda sai PROVEN.

EVIDENCE = execução medida nesta missão, com a matriz real em ROUTE_NOT_ALLOWED:
             CAPTURE_PROVIDER       = MEDIA_FORNECIDA
             rede = 0 · yt-dlp = 0
             AUDIO_ONLY_ACQUISITION = 'PROVEN'

RECOMMENDED_NEXT_STEP =
           incluir o provedor de mídia entregue na mesma regra do reuso. É uma
           linha, e o vocabulário para a dizer já existe: REUSED_NOT_ACQUIRED.

POR QUE NÃO AQUI =
           o briefing lista AUDIO_ONLY_LABEL_ON_SUPPLIED_MEDIA entre as dívidas
           que NÃO entram nesta missão. Corrigi-la em silêncio seria decidir por
           cima de uma instrução explícita.
```

---

## 8. DÍVIDA MEDIDA NESTA MISSÃO, NOVA

**`GUARDAR_FALSE_NAO_COBRE_A_OFICINA = CONFIRMED`** — `guardar=False` impede a
escrita do artefato, mas o WAV intermédio é sempre calculado para
`data/raw/REEL-MIDIA/<nome>.wav` e escrito lá. Uma corrida de teste suja a
gaveta da casa.

    `guardar=False` COBRE O ARTEFATO. NÃO COBRE A OFICINA.

Apanhado pela própria sentinela `T10` ao ser escrita. A sentinela passou a
limpar o que a oficina deixa, e a exigir apenas o que a lei exige: que o bruto
histórico não mude.

**`COL_LAW_505_AUTHORITY_ABSENT = CONFIRMED`** — `leis/retorno_da_coleta.py`,
que o handoff nomeia como autoridade, **não existe** nesta linha técnica.
COL-LAW-505 vive só em documentos.

---

## 9. SCRAP × COLLECTION CANÔNICA

```
COL_LAW_505_APPLICABILITY       = NOT_APPLICABLE_TO_THIS_POLICY_CHANGE
                                  (e a autoridade em código está ausente — §8)
COLHEITA_SEPARADA_DE_SUPORTE    = NOT_EXERCISED_IN_THIS_MISSION
RUN_ID_BORN_AT                  = NOT_EXERCISED_IN_THIS_MISSION
RAW_PRESERVATION                = intocado · bruto histórico idêntico, ficheiro
                                  a ficheiro, antes e depois
SOURCE_ID_PRESERVATION          = NAO SEI, nunca fabricado do endereço
FABRICATED_DOCUMENT_ID          = NO
PARALLEL_RAW_RUN_IDENTITY_MODEL = NO
THEMATIC_CLASSIFICATION_IN_SCRAPER = NO

MODULE_EXISTS = YES  o adaptador, a cadeia e o dono da política existem
EDGE_EXISTS   = YES  o adaptador lê o dono da política; a cadeia lê-o no socket
FLOW_EXISTS   = PARCIAL  o fluxo corre para REUSO (provado, PROVA B) e está
                RECUSADO para aquisição (provado, PROVA A). Pelo roteador
                canônico a capacidade inteira é recusada — ver o conflito da §3.
```

Nenhum destes três foi promovido pelo outro.

---

## 10. O QUE NÃO MUDOU

Não se adquiriu nada. Não se tocou a plataforma. Não se trocou `User-Agent`,
não se usou navegador nem sessão autenticada, não se procurou contorno. Não se
reabriu a pesquisa do `robots` para tentar um `SIM`.

Não se tocou em Admission, Collection, orquestrador, Ingresso, portal, Supabase,
Sala de Espera. Não se tocou no X: a C12 fica exatamente como a mediu. Não se
tocou na C11.

E nenhuma das dívidas listadas no briefing foi corrigida — todas continuam
abertas, e continuam registadas.
