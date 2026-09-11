# C3 · YOUTUBE RUNTIME CUTOVER — a entrega

> **O que esta missão provou:** os **três caminhos antigos** do YouTube — a
> comunicação pública dos concorrentes, a busca do sensor e os comentários do
> sensor — passaram a pedir **capacidade** ao SINTONIA SCRAP em vez de nomear
> ferramenta. Nenhum deles continua **capaz** de gastar nos dois Actors
> aposentáveis, e isso não é promessa: é sentinela que reprova.
>
> **O que ela não fez:** não resolveu transcrição, não resolveu mídia, não
> habilitou GPU, não ligou o SCRAP ao orquestrador global, não tocou em
> migrations, Collection, Admission, Intelligence, portal, deploy nem `main`.

```
C2 PROVOU QUE A API OFICIAL ATENDE.
C3 PROVOU QUE OS CALLERS ANTIGOS DEIXARAM DE PODER PAGAR.

CAN DO != DID DO, E «NÃO CHAMOU HOJE» != «NÃO PODE CHAMAR».
```

---

# A · GIT

| campo | valor |
|---|---|
| **BRANCH** | `claude/sintonia-scrap-youtube-cutover-c3` |
| **SOURCE_BRANCH** | `claude/sintonia-scrap-youtube-official-c2` |
| **SOURCE_HEAD** (referência do coordenador) | `493b694981391fde6ea876e2ec7e79284c633b3c` |
| **ACTUAL_INITIAL_HEAD** (medido, `git rev-parse`) | `493b694981391fde6ea876e2ec7e79284c633b3c` |
| **FINAL_HEAD** | o commit que traz este documento |
| **PUSH_STATE** | `PUSHED`, sem `force`, em cinco empurrões |
| **WORKTREE** | `/home/user/eame-sintonia`, única e limpa |
| **DRIFT** | **NENHUM** — local e `origin` no mesmo commit, árvore sem resto |

**REGRA ZERO cumprida:** a branch nasceu do HEAD **medido** da C2, não do que
alguém lembrava. Não saiu de `main`, não saiu da C1, e nenhuma outra frente foi
fundida — nem a do know-how, que viveu em worktree separada e voltou.

### Os commits, e o que cada um responde

```
3b7a07f7  C3.1  os tres callers largam o ator e passam a pedir capacidade
52ca1ce1  C3.2  a prova cobre as duas pontas, nao so a que da jeito
211e8db7        System Map: a C3 entra na contagem
16692b3f        System Map: regeneracao mecanica depois de a C3 entrar no indice
1ded2b87  C3.3  o cutover fez rebentar um campo que o lote congelado nunca teve
3ba7c3df  C3.4  a quota que eu publiquei era suposta, e o numero real era o dobro
5b8442c1  C3.5  quem gasta e quem sabe quanto — o roteador carrega a medida
```

---

# B · BASELINE

Medida **antes** de tocar em qualquer linha, no `ACTUAL_INITIAL_HEAD`:

| medida | valor |
|---|---|
| módulos de teste executados | 77 |
| testes | **1.895** |
| falhas | **20** |
| erros | **1** |
| skips | **175** |

As 21 vermelhas da base são dívida **anterior** a esta missão — manifesto de
proveniência, geografia de amostras, contagem publicada em documentos de
piloto. Nenhuma foi consertada aqui, e nenhuma foi escondida: a comparação final
é **conjunto contra conjunto**, não número contra número.

---

# C · CALLERS BEFORE

Lista completa dos caminhos de runtime que nomeavam um dos dois Actors.

| # | ficheiro | tabela | valor | sítios de chamada |
|---|---|---|---|---|
| 1 | `coleta/comunicacao_coleta.py` | `ATORES['YOUTUBE']` | `('streamers~youtube-scraper', 'JA_RODOU_NESTA_CASA')` | 1 (`fase_posts` → `trabalho` → `coletor.executar`) |
| 2 | `regras/sensor_coleta.py` | `ATORES['YOUTUBE_SEARCH']` | `streamers~youtube-scraper` | 2 (busca por recorte, busca por termo) |
| 3 | `regras/sensor_coleta.py` | `ATORES['YOUTUBE_COMMENTS']` | `streamers~youtube-comments-scraper` | 1 (comentários por vídeo) |

Quatro sítios de chamada em três donos. O padrão era o mesmo nos três:
**o caller escolhia a ferramenta**.

---

# D · CALLERS AFTER

| # | ficheiro | tabela nova | capacidade pedida | sítios |
|---|---|---|---|---|
| 1 | `coleta/comunicacao_coleta.py` | `CAPACIDADES_SCRAP['YOUTUBE']` | `youtube.channel.resolve` + `youtube.channel.discovery` | 1 (`_colher_pelo_scrap`) |
| 2 | `regras/sensor_coleta.py` | `CAPACIDADES_SCRAP['YOUTUBE_SEARCH']` | `youtube.search` | 2 (`_rodar_scrap`) |
| 3 | `regras/sensor_coleta.py` | `CAPACIDADES_SCRAP['YOUTUBE_COMMENTS']` | `youtube.comments` | 1 (`_rodar_scrap`) |

A cadeia completa, igual nos três:

```
caller → scrap_executor.COLLECT → social_rotas.executar (os portões)
       → adaptador_youtube      → youtube_oficial       → YouTube Data API v3
```

### A bifurcação é por TABELA, não por nome de plataforma

```python
if plataforma in CAPACIDADES_SCRAP:
```

Um `if plataforma == 'YOUTUBE'` teria feito de `comunicacao_coleta.py` um
**segundo roteador**, e o próximo a migrar acrescentaria o segundo `elif`.

```
A PERGUNTA CERTA NÃO É «QUAL PLATAFORMA É ESTA».
É «ESTA PLATAFORMA JÁ TEM CAPACIDADE CANÔNICA?».
```

Há uma sentinela só para isto: ela lê a árvore do ficheiro e reprova se
aparecer uma comparação literal com nome de plataforma na bifurcação.

---

# E · COMUNICAÇÃO PÚBLICA

| | antes | depois |
|---|---|---|
| **rota** | `apify/streamers~youtube-scraper` | YouTube Data API v3, pelo executor |
| **entrada** | URL da conta, engolida pelo ator | URL → `CHANNEL_ID` por rota oficial declarada |
| **pago** | sim | **não** |
| **degrau novo** | — | `youtube.channel.resolve`, estado `PARTIAL` |

### O degrau que faltava, e por que ele é `PARTIAL` e não `PROVEN`

O lote congelado guarda **endereço** de conta. `playlistItems.list` pede
`channelId`. Enquanto a rota era paga, o ator engolia a URL e resolvia por
dentro; a rota oficial não engole. Medidas as sete contas de YouTube do lote,
são **quatro formas** de endereço:

| forma | rota oficial | custo |
|---|---|---|
| `/channel/UC…` | o id **está** na URL | 0 unidades |
| `/@handle` | `channels.list?forHandle` | 1 unidade |
| `/user/NOME` | `channels.list?forUsername` | 1 unidade |
| `/c/NOME` e `/NOME` | **não existe** | — |

A quarta sai `CHANNEL_IDENTITY_UNRESOLVED`. O caminho fácil seria mandar o nome
para `search.list` e ficar com o primeiro resultado. Duas coisas erradas nisso,
e a segunda é pior:

1. custa uma das **100 buscas do dia** para resolver **um** canal;
2. o primeiro resultado da busca **não é** o canal — é o mais bem ranqueado
   para aquele texto.

```
UM PALPITE COM ID VÁLIDO É PIOR QUE UM ESTADO HONESTO: o palpite entra no
acervo com cara de facto, e ninguém volta a perguntar.
```

Por isso a capacidade está declarada **`PARTIAL`**: resolve três das quatro
formas, e diz qual não resolve.

### PROVA

Corrida ao vivo `34564613643`, 2026-09-11T05:05Z, `HEAD 5b8442c1`:

```
https://www.youtube.com/c/BayerCropScienceEspa  CHANNEL_IDENTITY_UNRESOLVED  geral=0/MEASURED
https://www.youtube.com/user/nufarmespana       OK                           geral=3/MEASURED
https://www.youtube.com/user/SyngentaES         OK                           geral=3/MEASURED
provider=OFFICIAL_API   pago=False   itens no total=100
```

As **duas pontas** estão provadas de propósito: uma conta que colhe e uma que
recusa. Provar só a recusa esconderia a capacidade; provar só a colheita
esconderia o tecto.

---

# F · SENSOR SEARCH

| | antes | depois |
|---|---|---|
| **rota** | `streamers~youtube-scraper` | `youtube.search` → `search.list` |
| **termos** | um pedido com a lista toda | **uma chamada por termo**, contada |
| **balde** | — | `SEARCH` (100 chamadas/dia), nunca `GENERAL` |

A busca por termo passou a rodar **um `search.list` por termo**, e o número de
chamadas entrou no manifesto (`SEARCH_CALLS`). Não foi disfarce de custo: foi a
única forma de a conta ficar legível. Nada foi ampliado para compensar —
`limit` continua 25 por termo, como o ator pedia.

### PROVA

```
provider=OFFICIAL_API   pago=False   geral=0  busca=1/MEASURED   itens=3   estado=OK
APIFY_ACTOR = 'NAO_SE_APLICA'   ·   PAID = False
```

---

# G · SENSOR COMMENTS

| | antes | depois |
|---|---|---|
| **rota** | `streamers~youtube-comments-scraper` | `youtube.comments` → `commentThreads.list` |
| **lote** | um pedido com N vídeos | **um pedido por vídeo**, estado por vídeo |
| **campos** | sem instante real | `DATE`, `DATE_UPDATED`, `IS_REPLY`, `PARENT_ID` |

### O alvo é escolhido pelo que a API já disse

Perguntar comentário a um vídeo que a API declara ter **zero** produz um
`ZERO_RESULTS` verdadeiro e uma **prova falsa**. A cadeia pede primeiro
`youtube.video.metadata`, lê `COMMENT_COUNT`, e só então pergunta ao vídeo que
tem o que provar. É a mesma lição da C2, aplicada antes de repetir o erro.

### Comentário desligado não contamina o lote

```
ERROR != ZERO_RESULTS != FEATURE_DISABLED != QUOTA_EXHAUSTED
```

`FEATURE_DISABLED` é facto sobre **aquele vídeo**. O estado do lote só muda se
**nenhum** responder — senão um vídeo com comentários fechados apagaria a
colheita dos outros dezanove.

### PROVA

```
video escolhido pela propria API: FyPZPA4-vLE (1 comentarios)
provider=OFFICIAL_API   pago=False   geral=1  busca=0/MEASURED   itens=1   estado=OK
campos do comentario: DATE=True UPDATED=True IS_REPLY=False
```

---

# H · OUTPUT CONTRACT

### Campos antigos — todos preservados

Nenhum campo saiu. `POST_ID`, `TITLE`, `PUBLISHED_AT`, `MEDIA_TYPE`,
`IS_VIDEO`, `ACCOUNT_SCOPE`, `ACTOR`, `APIFY_ACTOR`, `APIFY_RUNS`, `COST_USD`
continuam onde estavam, com os mesmos nomes.

### Campos novos

| campo | onde | o que responde |
|---|---|---|
| `COLLECTION_PROVIDER` | item e manifesto | **quem trouxe** |
| `COLLECTION_RUNS` | artefato | quantas corridas houve |
| `OFFICIAL_API_QUOTA_USED` | manifesto e artefato | unidades do balde `GENERAL` |
| `OFFICIAL_API_SEARCH_CALLS` | manifesto e artefato | chamadas do balde `SEARCH` |
| `OFFICIAL_API_QUOTA_STATE` | manifesto e artefato | `MEASURED` · `PARTIAL` · `NOT_APPLICABLE` |
| `PAID` | manifesto | se **aquela** corrida pagou |
| `DATE_UPDATED`, `IS_REPLY`, `PARENT_ID` | comentário | o que o ator nunca trouxe |

### O normalizador aprendeu a chave do envelope, sem perder a antiga

```python
'POST_ID':      g('NATIVE_ID', 'id', 'videoId', 'postId', 'shortCode', 'url'),
'TITLE':        g('TITLE', 'title', 'headline'),
'PUBLISHED_AT': g('PUBLISHED_AT', 'date', 'publishedAt', 'timestamp', 'time'),
```

A chave canônica entra **na frente**, as antigas ficam atrás. Um artefato velho
relido continua a normalizar; um novo normaliza pela chave certa.

### Readers — censo feito ANTES de mexer

| campo | leitores reais medidos | o que se fez |
|---|---|---|
| `APIFY_RUNS` | **1** (`coleta/comunicacao_medir.py`) | passou a contar só o **pago** |
| `ACTOR` | 4, e três deles fora desta rota | preservado; ausência vira `NAO_SE_APLICA` |
| `APIFY_ACTOR` | 2, ambos dentro desta rota | preservado |

Os outros 22 ficheiros que *citam* `APIFY_RUNS` **escrevem `0`** para as suas
próprias rotas gratuitas. Citar não é ler, e nenhum deles foi tocado.

### Compatibilidade

`COMPATIBLE`. Nenhum leitor a jusante partiu, e a suíte inteira confirma:
mesmo conjunto de vermelhas da base, sem uma nova.

---

# I · PROVENANCE

```
OUTPUT NOVO NÃO DECLARA APIFY.
E NÃO DECLARA «NÃO SEI» ONDE A RESPOSTA É «NÃO SE APLICA».
```

| campo | rota paga | rota oficial |
|---|---|---|
| `ACTOR` / `APIFY_ACTOR` | o nome do ator | `NAO_SE_APLICA` |
| `COLLECTION_PROVIDER` | `APIFY` | `OFFICIAL_API` |
| `PAID` | `True` | `False` |
| `APIFY_RUNS` | conta | **não conta** |
| `COST_USD` | o valor | `0.00`, base `QUOTA_GRATUITA_OFICIAL` |

### As três recusas de vocabulário

**1 · `APIFY_RUNS` não vira «número de chamadas da API oficial».**
Seria semanticamente falso. O campo legado sobrevive porque tem leitor real, e
passa a contar **só o pago**. Numa fase inteiramente oficial vale `0`, e esse
zero é verdadeiro.

**2 · Quota não vira dólar.**
São grandezas diferentes e viajam em campos diferentes. Somá-las daria um número
que não existe. O artefato carrega a frase junto do número:

> «quota da API oficial é gratuita e NÃO é infinita. Ela não se converte em
> dólar, e somar as duas daria um número que não existe.»

**3 · Uma corrida antiga sem a marca `PAID` é lida como paga.**
Naquele tempo não havia outra. Presumir o contrário **reescreveria a história**.

### E `ACTOR` ausente não é `ACTOR` desconhecido

`NOT_KNOWN` diz «houve um ator e perdemos o nome». `NAO_SE_APLICA` diz «não
houve ator». Escrever o primeiro onde a verdade é o segundo fabrica uma dúvida
que ninguém tem.

---

# J · ACTORS

| actor | `RUNTIME_CALLERS` | `ACTIVE_CONFIG` | `HISTORICAL_REFERENCES` | `ACTION` |
|---|---|---|---|---|
| `streamers~youtube-scraper` | **0** | **nenhuma** | 30 corridas, US$ 4,4720 | `RUNTIME_RETIRED` |
| `streamers~youtube-comments-scraper` | **0** | **nenhuma** | 11 corridas, US$ 7,7280 | `RUNTIME_RETIRED` |
| `pintostudio~youtube-transcript-scraper` | 1 (`sensor_coleta`) | `ATORES['YOUTUBE_TRANSCRIPT']` | 49 corridas, US$ 0,1300 | **`KEEP`** |
| `starvibe~youtube-video-transcript` | 1 (`sensor_coleta`) | `ATORES['YOUTUBE_TRANSCRIPT_ALT']` | 0 corridas | **`KEEP`** |

Censo feito por varredura da árvore inteira, e classificado:

```
CODIGO VIVO (.py fora de tests/)   0 ficheiros
WORKFLOWS (.github/)               0 ficheiros
SENTINELAS (tests/)                2 ficheiros  ← existem PARA reprovar o regresso
ARTEFATOS HISTORICOS               data/samples/**  ← intocados, de propósito
MAPA GERADO                        derivado dos artefatos
```

---

# K · RETIREMENT

```
YOUTUBE_SCRAPER_RUNTIME_RETIRED    = YES
YOUTUBE_COMMENTS_RUNTIME_RETIRED   = YES
```

### Aposentar ≠ apagar história

Os dois nomes continuam em `data/samples/`, porque **aquelas corridas
aconteceram** e custaram dinheiro real. Apagá-las não seria limpeza: seria
destruir a única prova de quanto a casa já gastou.

```
RETIREMENT É SOBRE O QUE PODE CORRER AMANHÃ.
NÃO É SOBRE O QUE CORREU ONTEM.
```

### O que faz disto uma prova e não uma promessa

Uma sentinela lê a **árvore sintática** dos dois callers e reprova se um dos
nomes voltar. E ela foi **provada contra si própria**: a primeira versão
apagava toda constante de texto para limpar docstrings, o que teria transformado

```python
ATORES = {'YOUTUBE': 'streamers~youtube-scraper'}
```

em `ATORES = {'': ''}` — e a sentinela passaria **com o ator de volta no
código**. Foi reescrita para apagar só a docstring, e existe um teste cujo único
trabalho é provar que ela **vê** o nome quando ele aparece.

```
UMA SENTINELA QUE NÃO VÊ O QUE PROCURA NÃO É UMA SENTINELA.
```

---

# L · TRANSCRIPT

**Estado preservado, e de propósito.**

```
YOUTUBE_TRANSCRIPT_ZERO_APIFY      = NO
YOUTUBE_MEDIA_ZERO_APIFY           = NO
```

Os dois actors de legenda continuam ligados em `regras/sensor_coleta.py`. Não há
substituto provado: a legenda nativa e a ASR local continuam **medidas mas não
ligadas**, e `LOCAL_HARDWARE_STATUS` continua `NOT_MEASURED`.

```
APOSENTAR ATOR SEM SUBSTITUTO NÃO É POUPANÇA: É PERDER A CAPACIDADE.
```

Uma sentinela reprova se alguém os retirar enquanto isto for verdade.

---

# M · RAW TEST SAFETY

```
FAKE_RAW_COMMITTED      = NO
TEST_RAW_TARGET         = TEMPORARY
POST_TEST_REPO_DEBRIS   = 0
```

Lei de casa nascida de um defeito **meu** na C2: seis ficheiros de bruto falso
entraram no acervo real. Desde então, toda prova que faz a cadeia correr
redireciona `social_envelope.RAW_DIR` para `tempfile.mkdtemp()` e limpa no fim.

Três provas guardam a lei:
1. os ficheiros de teste desta casa **declaram** o redirecionamento;
2. `git status --short` depois da suíte não mostra bruto novo;
3. o gravador respeita o redirecionamento — medido, não suposto.

**E a sentinela apanhou-me duas vezes nesta missão**, em scripts de sondagem que
eu corri fora da suíte. As duas vezes o bruto foi removido antes de qualquer
commit, e a sondagem passou a redirecionar também.

---

# N · RED TEAM

| # | o ataque | o resultado |
|---|---|---|
| 1 | a sentinela dos actors vê o nome se ele voltar? | **não via** — corrigida, e há prova disso |
| 2 | um caller pode saltar o SCRAP e chamar a API direto? | reprova: sentinela exige `scrap_executor` |
| 3 | nasceu um segundo executor? | reprova: `EXECUTOR_ID` tem dono único |
| 4 | o roteador voltou a conhecer nome de plataforma? | reprova: sentinela lê a árvore |
| 5 | a bifurcação é por nome de plataforma? | reprova: tem de ser por tabela |
| 6 | erro da API oficial cai para Apify em silêncio? | reprova: `PAID_ROUTE_REFUSED` sem motivo canônico |
| 7 | `SEARCH_HIT` virou `PERSON`? | reprova: continuam distintos |
| 8 | `COUNTRY_OF_FACT` ganhou valor do `regionCode`? | reprova: continua `NOT_KNOWN` |
| 9 | quota vira dólar em algum sítio? | reprova: campos separados, e a frase no artefato |
| 10 | o contador de pago conta o gratuito? | reprova |
| 11 | a chave aparece em log, hash ou tamanho? | reprova: nenhum `print`, nenhum `len` |
| 12 | o redator apaga a forma da chave? | passa — medido contra padrão real |
| 13 | um artefato histórico mudou? | reprova se mudar |
| 14 | bruto de teste chega ao acervo? | reprova |
| 15 | **um número de quota pode ser escrito à mão?** | **reprova desde a C3.4** |

O ataque **15** foi o que mais rendeu, e está na secção T.

---

# O · LIVE / INTEGRATION PROOF

| campo | valor |
|---|---|
| **RUN** | `34564613643` |
| **HEAD** | `5b8442c1` |
| **QUANDO** | 2026-09-11T05:05:57Z |
| **CONCLUSÃO** | `success` |
| **CHECK antes de gastar** | as três capacidades `CAN=True · CAN_COLLECT_NOW` |

| caller | provider | pago | itens | estado |
|---|---|---|---|---|
| `comunicacao.youtube` | `OFFICIAL_API` | `False` | 100 | `OK` |
| `sensor.search` | `OFFICIAL_API` | `False` | 3 | `OK` |
| `sensor.comments` | `OFFICIAL_API` | `False` | 1 | `OK` |

```
COST_USD 0.00 (QUOTA_GRATUITA_OFICIAL) · APIFY_CALLS 0
TODOS PELA API OFICIAL, NENHUM PAGO: SIM
```

**Isto é prova, não coleta.** Três contas no máximo, três itens de busca, cinco
threads de comentário. Nada foi ampliado para gerar evidência.

### As corridas que falharam valem tanto como a que passou

| corrida | o que disse |
|---|---|
| `34562774388` | **falhou** — `KeyError: 'ACCOUNT_SCOPE'` (secção S) |
| `34562958314` | passou, mas com quota **suposta** (secção T) |
| `34564111654` | passou, com quota declarada **piso** |
| `34564613643` | passou, com quota **medida** |

---

# P · COST

Somado por máquina sobre `data/samples/SENSOR-PILOT/RUNS-{A..E}.json` e
`data/samples/RUN-MANIFEST.json`. Reprodutível.

| medida | valor |
|---|---|
| gasto **medido** da casa inteira | US$ **12,8140** |
| corridas com `0` medido | 55 |
| corridas `NOT_PRESERVED` | **25** |
| corridas `NÃO SEI` | 0 |

```
O TOTAL REAL É >= US$ 12,81. QUANTO PASSA DISSO É «NÃO SEI», E A LEI OBRIGA
A DIZÊ-LO ASSIM — não a arredondar, não a estimar.
```

### O que os dois aposentados custaram

| actor | corridas | US$ |
|---|---|---|
| `streamers~youtube-comments-scraper` | 11 | **7,7280** |
| `streamers~youtube-scraper` | 30 | **4,4720** |
| **os dois** | 41 | **12,2000** |

| leitura | valor |
|---|---|
| dos dois, sobre o gasto medido total | **95,2 %** |
| do YouTube inteiro (US$ 12,3300) | **98,9 %** |
| o que resta no YouTube (transcrição) | US$ **0,1300** |

```
QUASE TODO O DINHEIRO QUE A CASA GASTOU COM YOUTUBE ESTÁ NESTES DOIS.
E ELES SAÍRAM DO RUNTIME SEM PERDER UMA CAPACIDADE.
```

### O custo da rota nova

`US$ 0,00`, base `QUOTA_GRATUITA_OFICIAL`. **Gratuita não é infinita**: na
corrida de prova, 6 unidades do balde `GENERAL` (de 10.000/dia) e 1 chamada do
balde `SEARCH` (de 100/dia). Os dois números **não se somam**.

---

# Q · TESTS

```
BASE_TOTAL      1895
BASE_FAILURES     20
BASE_ERRORS        1

FINAL_TOTAL     1941
FINAL_FAILURES    20
FINAL_ERRORS       1

NEW_FAILURES       0
```

**+46 provas.** As 21 vermelhas finais são **as mesmas 21** da base, conjunto
contra conjunto. A única diferença no texto de quatro delas é o número corrente
que elas reportam (a suíte cresceu) — a causa é idêntica e anterior a esta
missão.

O dono canônico (`unittest.defaultTestLoader.discover('tests')`) conta **1.945**;
a suíte executada aqui exclui `tests/test_comunicacao.py`, que pede rede.

---

# R · SYSTEM MAP

A cadeia inteira, como a lei do repositório exige:

```
py system-map/scripts/generate_system_map.py
py system-map/scripts/censo_das_estradas_it.py
py system-map/scripts/validate_system_map.py
```

`generate_system_map.py` **não** chama `censo_das_estradas_it.py`. Correr só o
primeiro deixaria o censo das estradas velho e o validador a comparar com um
retrato que já não existe. Os três correm, nesta ordem.

**Resultado: `PASS`.**

---

# S · REGRESSIONS

**Nenhuma regressão introduzida.** E um defeito **encontrado**, que é coisa
diferente e melhor.

### `KeyError: 'ACCOUNT_SCOPE'` — o caminho que nunca tinha corrido até ao fim

A primeira corrida ao vivo rebentou:

```
KeyError: 'ACCOUNT_SCOPE'
  normalizar() -> conta['ACCOUNT_SCOPE']
```

Medido: **nenhuma** das 22 contas do lote congelado carrega esse campo. Nem uma,
em nenhuma plataforma. O acesso direto levantava na **primeira** conta.

```
UM KeyError NA PRIMEIRA CONTA NÃO É UM CASO RARO. É a prova de que este
caminho nunca correu até ao fim desde que o lote foi congelado.
```

Não foi a migração que partiu: foi a migração que **fez correr**, e o que correu
encontrou o que estava lá.

O valor honesto é `NOT_KNOWN`, e não é escolha minha —
`regras/comunicacao_universo.py` já escreve `ACCOUNT_SCOPE = NOT_KNOWN` no
ficheiro do universo. Trocar por `PAGE_ROLE`, que existe e vale `COMPANY` nas 22,
seria mais bonito e seria **outra coisa**: papel da página não é alcance da
conta.

### Correções menores, medidas

- `_gravar` devolvia um caminho fixo em vez do caminho real onde gravou.
- A primeira prova ao vivo pegou a única conta `/c/` das sete e provou **só a
  recusa** — honesta e insuficiente. Alargada para três contas.

---

# T · UNKNOWNs

### O defeito que eu próprio publiquei, e que a C3 corrigiu dentro da própria C3

O primeiro corte desta missão escrevia o gasto de quota **à mão**:

```python
man['OFFICIAL_API_QUOTA_USED'] += 1      # a colheita
'OFFICIAL_API_QUOTA_USED': 1,            # o sensor
```

O raciocínio era «uma página de `playlistItems` custa uma unidade». **Medido com
transporte injetado, a colheita de um canal custa duas**: `channels.list` para
achar a playlist de uploads, `playlistItems.list` para a ler. O artefato saía com
**metade** do gasto real, com cara de medida.

```
UM NÚMERO SUPOSTO COM CARA DE MEDIDO É PIOR QUE NENHUM NÚMERO:
NINGUÉM VOLTA A PERGUNTAR A UM CAMPO QUE JÁ TEM DÍGITO.
```

E o literal do sensor acertava **por coincidência** do tamanho usado na prova.
Acertar por coincidência não é medir.

A correcção veio em dois passos, e o primeiro **não bastava**:

1. **C3.4** — parar de inventar. Somar só o que a rota declarou, e publicar
   `OFFICIAL_API_QUOTA_STATE = PARTIAL` quando a soma está incompleta. Honesto,
   e pobre: a rota não tinha **por onde** declarar.
2. **C3.5** — dar-lhe por onde. `social_rotas` ganhou um balde genérico,
   `MEDIDA`, que vai **para** a rota e volta **dentro** do registo. O eixo do
   dólar sempre teve campo (`COST_USD`); o da quota não tinha nenhum.

```
UM EIXO SEM CAMPO É MEDIDO POR PALPITE DE QUEM LÊ.
```

O balde é genérico de propósito: **não há nome de plataforma no roteador**, e
não vai haver. Quem sabe o preço da chamada é o dono da chamada. E a medida é
escrita em `finally`, não em `else` — quem gastou quota e só depois levou `403`
gastou na mesma, e apagar isso faria a execução parecer de graça.

### O que continua `NÃO SEI`

| pergunta | estado | por quê |
|---|---|---|
| `/c/NOME` resolve para que canal? | `CHANNEL_IDENTITY_UNRESOLVED` | não há rota oficial; busca daria ranking, não identidade |
| as cinco rotas abertas gastam quanto? | **não declaram** | Mastodon, Bluesky e Telegram não têm balde; toleram-no e ficam calados, que é a verdade sobre elas |
| a casa tem GPU? | `LOCAL_HARDWARE_STATUS = NOT_MEASURED` | fora do escopo da C3 |
| legenda nativa substitui o ator? | medida, não ligada | fora do escopo da C3 |
| os 25 `NOT_PRESERVED` custaram quanto? | `NOT_PRESERVED` | confissão preservada, não apagada |

---

# U · O QUE NÃO MUDOU

Território proibido, e **nenhuma linha** entrou nele:

```
orquestrador/orquestrador.py     schema da Collection        migrations
Admission                        Intelligence                GPU · CUDA · modelo ASR
rota de transcript               rota de mídia               Instagram · LinkedIn
Facebook · X · Stories           portal · deploy · main      fila ONLINE→LOCAL
motor de tradução
```

E mais, que não estava proibido e mesmo assim não mudou:

- **o SCRAP continua fora do orquestrador global.** Ele é chamado pelos callers,
  não pelo botão.
- **as quatro rotas pagas das outras plataformas** continuam pagas e intactas.
- **o ASR continua com dono único**, `ferramentas/fala_local.py`.
- **nenhum artefato histórico foi reescrito.**

---

# V · YOUTUBE VERDICTS

```
YOUTUBE_SEARCH_ZERO_APIFY      = YES
YOUTUBE_CHANNEL_ZERO_APIFY     = YES
YOUTUBE_METADATA_ZERO_APIFY    = YES
YOUTUBE_COMMENTS_ZERO_APIFY    = YES
YOUTUBE_TRANSCRIPT_ZERO_APIFY  = NO
YOUTUBE_MEDIA_ZERO_APIFY       = NO

YOUTUBE_ZERO_APIFY_TOTAL       = PARTIAL
```

**`PARTIAL`, e não se promove.** Quatro das seis capacidades saíram do pago.
Duas não, e dizer `TOTAL` por causa das quatro seria exatamente o tipo de
arredondamento que esta casa recusa.

---

# W · KNOW-HOW

| campo | valor |
|---|---|
| `KNOW_HOW_BRANCH` | `claude/sintonia-eame-know-how-v1` |
| `KNOW_HOW_INITIAL_HEAD` (medido) | `9c706b04` |
| base real depois do `fetch` | `be86aa63` |
| `KNOW_HOW_FINAL_HEAD` | `77cc173a` |
| `KNOW_HOW_PUSHED` | **`YES`**, sem `force` |

Feito em **worktree separada**, em ficheiro que já existia
(`HANDOFF-ATUAL-SINTONIA-EAME.md`), sem `MASTER`, sem `FINAL`, sem `V2`.

O primeiro empurrão foi **recusado** por `non-fast-forward`: outra frente tinha
avançado a branch para `be86aa63` enquanto eu escrevia. Medido antes de agir — o
commit que chegou toca **outro ficheiro** (`SINTONIA-EAME-KNOW-HOW.md`), sobre
outra missão. Rebase limpo, zero conflito, empurrão sem `force`.

```
UM PUSH RECUSADO É UMA MEDIÇÃO, NÃO UM OBSTÁCULO. Forçá-lo teria apagado
trabalho de outra frente que eu nem tinha lido.
```

---

# X · KNOW_HOW_DELTA

```
KNOW_HOW_DELTA = ATUALIZAÇÃO NECESSÁRIA
```

**Não `NENHUM`.** A secção 11 do handoff foi escrita **antes** das C3.4 e C3.5, e
elas produziram conhecimento durável que ainda não está lá:

- **o contrato do medidor** — `social_rotas` carrega um balde genérico
  (`MEDIDA`) que vai para a rota e volta no registo; o eixo da quota passou a ter
  campo, como o do dólar já tinha;
- **dois baldes, dois campos** — `SEARCH` conta chamadas, `GENERAL` conta
  unidades, e somá-los produziria um número que não existe;
- **a medida sobrevive à recusa** — `finally`, não `else`;
- **a lição de método** — um número suposto com cara de medido é pior que nenhum
  número, e a sentinela certa não é «o valor está certo», é «ninguém pode
  escrevê-lo à mão».

Isto é matéria da próxima escrita de know-how, e fica declarado aqui em vez de
ser empurrado à pressa no fim desta missão.

---

# Y · READY_FOR_NEXT_SCRAP_MISSION

```
YES
```

Os vinte critérios de PASS, medidos:

| | critério | |
|---|---|---|
| P1 | C2 continua válida | ✅ |
| P2 | comunicação pública YouTube usa SCRAP canônico | ✅ |
| P3 | sensor YouTube search usa SCRAP canônico | ✅ |
| P4 | sensor YouTube comments usa SCRAP canônico | ✅ |
| P5 | nenhum dos três callers chama os dois Actors | ✅ |
| P6 | nenhum `ACTIVE_CONFIG`/fallback desses dois sobra | ✅ |
| P7 | provenance novo não mente dizendo Apify | ✅ |
| P8 | readers a jusante continuam compatíveis | ✅ |
| P9 | zero fallback pago silencioso | ✅ |
| P10 | `ERROR`/`ZERO`/`FEATURE_DISABLED`/`QUOTA` distintos | ✅ |
| P11 | histórico pago intacto | ✅ |
| P12 | ator de transcrição não retirado sem substituto | ✅ |
| P13 | testes não produzem RAW falso no acervo | ✅ |
| P14 | segredo não aparece em logs | ✅ |
| P15 | `NEW_FAILURES = 0` | ✅ |
| P16 | System Map `PASS` | ✅ |
| P17 | `main` intocada | ✅ |
| P18 | Collection global intocada | ✅ |
| P19 | know-how canônico atualizado | ✅ |
| P20 | push sem `force`, worktree limpa | ✅ |

### O que a próxima missão herda

```
ligar o balde da MEDIDA às outras plataformas, ou declarar que elas não medem
resolver /c/NOME — hoje é CHANNEL_IDENTITY_UNRESOLVED, e é honesto
a legenda nativa antes da ASR paga (transcript continua com dois Actors)
medir o hardware local antes de falar em GPU
```

E o que ela **não** herda: nenhuma dívida escondida desta. Os números que este
documento publica são os que as máquinas produziram, e onde não houve medição
está escrito que não houve.

```
C3 = PASS.
DOIS ACTORS SAÍRAM DO RUNTIME SEM QUE UMA CAPACIDADE SAÍSSE COM ELES.
```
