# C10.5 — O PORTÃO VIVE ONDE O SOCKET ABRE, E O `robots` DO INSTAGRAM DIZ NÃO

    C10_5_COLLECTION_FLOW = BLOCKED_HUMAN_DECISION

A C10.4 pôs o portão de política no adaptador do Instagram e mediu que ninguém
atravessava a aquisição sem passar por ele — **pelo executor canônico**. A C10.5
perguntou quem mais entra, e a resposta mudou a missão duas vezes.

---

## 1. A PORTA DE SERVIÇO QUE A COLLECTION AINDA TINHA

Censo de toda chamada à cadeia de aquisição, medido no AST, fora de teste e de
prova:

| ficheiro | chama | passava pelo portão? |
|---|---|---|
| `coleta/adaptador_instagram.py` | `transcrever_reel` | sim, desde a C10.4 |
| `coleta/comunicacao_coleta.py::fase_transcrever` | `rt.fase_posts` | **não** |

A segunda linha não é um atalho de laboratório. É a **fase de fala da
Collection** — a que o orquestrador chama com `fase=transcrever`. O caminho era:

```
orquestrador → receitas T9 → comunicacao_coleta.fase_transcrever
             → reel_transcricao.fase_posts → transcrever_reel     ← sem portão
```

    UM PORTÃO QUE UMA PORTA DE PRODUÇÃO CONTORNA NÃO DECIDE NADA. É UMA SUGESTÃO.

---

## 2. ONDE O PORTÃO PASSOU A VIVER, E POR QUE NÃO NO LOTE

No ponto exato onde o socket abre: `midia_por_ytdlp` e `metadados_ytdlp`. Não na
fase, não no lote, não só no adaptador.

Isso tem uma consequência que **é a lei**, e não um efeito colateral: reprocessar
bytes que já estão em casa continua a correr mesmo com a política em `NAO`.

    REUSAR ≠ ADQUIRIR. Uma recusa de AQUISIÇÃO que também apagasse o
    REPROCESSAMENTO castigaria o que já está preservado — e obrigaria quem
    mudasse uma regra a recolher tudo outra vez.

Os degraus 0 e 1 (bytes já preservados, ficheiro entregue) correm sempre. Os
degraus 2 e 3 (rede) só correm com a lei do lado deles.

### A plataforma é parte da pergunta

A política responde por plataforma, e a plataforma vem de `ident['PLATFORM']` —
dado medido, nunca adivinhado do endereço. Sem plataforma declarada a resposta é
`NOT_DECLARED`, e não declarado não é permitido.

---

## 3. O BURACO QUE A PRIMEIRA MEDIÇÃO ENCONTROU

Com o portão só no download, a porta da Collection sob `PERMITIDA = NAO` ainda
fazia **quatro chamadas** ao `yt-dlp`. Eram os metadados, com `-J`.

    QUEM PERGUNTA AS HORAS JÁ ENTROU NO PÁTIO.

Pedir metadados é tocar a plataforma: abre socket, gasta pedido e aparece no log
do host. Gatear só o download deixaria a casa a bater à porta de quem disse que
não, e a jurar que não entrou. Depois de gatear os dois:

| política | chamadas ao `yt-dlp` | sockets | `MEDIA_STATE` |
|---|---|---|---|
| `NAO` | 0 | 0 | `ROUTE_NOT_ALLOWED` |
| `SIM` | 8 | 0 (trava armada) | a rota é tentada |

### A recusa sobe com o nome dela

Antes, uma recusa saía do fluxo como `AUDIO_ONLY_UNAVAILABLE` — uma mentira
precisa: o som está lá; o que falta é autorização. Quem lesse o artefato daqui a
um ano concluiria que a plataforma não serve áudio.

    ERROR ≠ REJECTED ≠ UNKNOWN ≠ NOT_RUN ≠ ROUTE_NOT_ALLOWED ≠ NOT_DECLARED.

---

## 4. O ACHADO QUE PARA A MISSÃO

O portão de transporte desta casa — `coleta/scrap_http.py` — lê o `robots.txt`
**vivo** do host, com o `User-Agent` real da coleta. A C10.5 perguntou-lhe pela
rota do Reel. Medido nesta máquina, agora:

```
https://www.instagram.com/reel/DW6X5lZkU41/            → False
https://www.instagram.com/p/DW6X5lZkU41/               → False
https://www.instagram.com/p/DW6X5lZkU41/embed/...      → False
https://www.instagram.com/syngentaitalia/              → False
```

E o motivo devolvido foi `robots.txt do host barra este caminho` — que só sai
quando o ficheiro foi **lido e parseado**. Lido diretamente, `instagram.com/robots.txt`
tem 6 256 bytes, 295 linhas, e o bloco que se aplica a esta casa é:

```
User-agent: *
Disallow: /
```

O agente `SintoniaScrap` não aparece nomeado em lado nenhum do ficheiro, portanto
cai no `*`.

### O que isto significa, e o que não significa

A casa já tem a lei escrita, e ela foi escrita exatamente para este caso:

    ROTA QUE FUNCIONA NÃO É ROTA PERMITIDA.

O cabeçalho de `leis/social_matriz.py` documenta o precedente: três rotas
gratuitas do YouTube que **funcionaram medidas nesta máquina** estão em
`Disallow`, e ficaram registadas como `ROUTE_NOT_ALLOWED` em vez de viverem em
silêncio.

A rota do Reel está na mesma situação, e a matriz ainda a declara
`PERMITIDA = SIM · PROVED`.

**Esta missão não muda esse valor.** Mudar `PERMITIDA` é decisão de política, e
política é de gente — tanto para afrouxar como para apertar. O que a missão faz é
pôr a medição em cima da mesa e garantir que, seja qual for a decisão, ela passe a
valer em **todas** as portas — que era exatamente o que não acontecia antes.

Quando a decisão for tomada, ela liga-se num sítio só: `scrap_http.permitido()`,
que já existe, já lê o robots vivo e já reprovou rota que funcionava.

---

## 5. E AINDA HAVIA UM SEGUNDO BLOQUEIO, INDEPENDENTE

`data/samples/COMPETITOR-PUBLIC-COMM/POSTS-INSTAGRAM.json` **não existe** nesta
árvore. A fase paga nunca correu para o Instagram aqui, e a fase de fala trabalha
sobre o que a fase paga deixou.

Isto **não** é «a empresa não publica». É «a coleta ainda não rodou» — e a própria
cadeia já distingue as duas coisas na mensagem que imprime. Produzir esse ficheiro
exigiria uma corrida paga, que está proibida.

Logo: mesmo com a decisão do `robots` tomada a favor, o fluxo de ponta a ponta a
partir da porta da frente precisaria de uma corrida que esta missão não pode fazer.

---

## 6. O QUE FICOU PROVADO, APESAR DOS DOIS BLOQUEIOS

| prova | resultado |
|---|---|
| a porta da Collection bate no portão | `NAO` → 0 `yt-dlp`, 0 sockets, `ROUTE_NOT_ALLOWED` |
| a mesma porta deixa passar com `SIM` | 8 chamadas, todas com `-f bestaudio` |
| reuso sobrevive a um `NAO` | ficheiro entregue atravessa, 0 rede |
| o caminho canônico continua inteiro | 1 objeto, `TRANSCRIPT_STATE = OK`, 0 rede |
| áudio-only não regrediu | `VIDEO_STREAMS = 0`, `AUDIO_STREAMS = 1` |
| custo | `APIFY_RUNS = 0` · `COST_USD = 0,00` |

---

## 7. DÍVIDA MEDIDA, NÃO CORRIGIDA AQUI

**`FASE_NAO_EXPRESSIVEL_POR_FRASE = CONFIRMED`** — `de_uma_frase` só extrai `pais`
e `tema`. «colete a fala dos vídeos dos concorrentes no Instagram» resolve para T9
com `filtros = {}`, e o padrão da receita é `fase=posts`. Pedir fala por frase
não chega à fala. Só um `Pedido` estruturado exprime `fase=transcrever`.

**`GRAVAR_LOTE_REPETE_A_VIOLACAO_DA_C10_3 = CONFIRMED`** — o cabeçalho do lote em
`gravar_lote` declara `'SOURCE_LOCATION': 'a plataforma onde o video esta
publicado'`. A C10.3 tirou a plataforma do `SOURCE_LOCATION` na ficha de cada
item; o cabeçalho do conjunto ainda a põe lá.

**`TEST_COMUNICACAO_NAO_CARREGA = CONFIRMED`** — `tests/test_comunicacao.py`
falha no import, nos dois baselines. A fase T9 não tem cobertura viva.

As dívidas da C10.4 (`INSTAGRAM_TRANSCRIPT_TWO_IMPLEMENTATIONS`,
`AUDIO_ONLY_LABEL_ON_SUPPLIED_MEDIA`, `MATRIZ_EVIDENCE_PATH_DEBT`,
`COUNTRY_SCOPE_NOT_FORWARDED`) continuam abertas e intocadas.

---

## 8. CICATRIZ DE SONDA

A primeira prova da porta da Collection deu **0 chamadas ao `yt-dlp` nos dois
casos** — com a política em `NAO` e em `SIM`. Parecia o portão a funcionar. Não
era: o fixture trazia `POST_URL` e a cadeia lê `URL`, portanto o item nunca
chegava ao degrau da rede.

    UMA SONDA QUE NÃO DISTINGUE OS DOIS CASOS NÃO MEDE O PORTÃO. MEDE A SONDA.

Foi ao corrigir a chave que os quatro pedidos de metadados apareceram — e foi
assim que o buraco do `-J` foi encontrado. A sonda partida escondia o defeito
**e** fingia o sucesso.

---

## 9. O QUE ESTA MISSÃO NÃO FEZ

Não mudou política. Não ligou o portão de transporte à aquisição. Não fez corrida
paga. Não escreveu nas gavetas da casa. Não tocou Admission, Sala de Espera,
scheduler, Supabase, portal. Não mergeou nada.

    CAN RUN THROUGH SCRAP GATE ≠ FULL COLLECTION FLOW PROVEN.
