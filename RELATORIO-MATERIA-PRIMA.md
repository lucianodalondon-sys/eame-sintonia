# RELATÓRIO — MATÉRIA-PRIMA V1

`ACTUAL_LLM_MODEL = claude-opus-5`

⚠️ **ONDE VIVE CADA COISA.** Esta missão mexe em DUAS árvores e os números não
são os mesmos nas duas:

```
materia-prima-v1              @ 14e4d4fb   esta worktree. So o relatorio.
source-curator-service-v1     @ 216dd6db   A LANE VIVA. O bot corre aqui.
                                           O gatilho e a fila so existem aqui.
```

Os números do bot medem-se **sempre** na lane viva. A primeira medição deste
relatório foi feita na árvore errada e está corrigida abaixo, com as duas
leituras à vista.

---

## LOTE 1 — os carimbos

### 1a · `CAPABILITY_BLOCK` — os 17 do Facebook não são 17, e não são obsoletos

Medido na árvore desta worktree (17 `CAND-*`, de um total de 28):

```
SOURCE_ID                       MOTIVO_ESCRITO              COMMIT_DE_ORIGEM
CAND-0029/0030/0032/0043/       FACEBOOK_CAPABILITY_BLOCK   63b71421  (livro B2)
      0046/0047  (6)
CAND-0271/0289/0300/0331/       YouTube exige channel_id    216dd6db  (livro C)
      0332/0335/0377/0414/
      0423/0452/0469  (11)
```

**Os 6 do Facebook:**

```
ADAPTADOR_NECESSARIO   coleta/adaptador_facebook.py
ADAPTADOR_EXISTE_HOJE  SIM — 37 linhas, nasceu 11/09 no commit ed73aba3
CARIMBO NASCEU         21/09, commit 63b71421
VEREDITO               BLOQUEIO_VALIDO
```

A regra da missão — *"um carimbo importado de um commit anterior à ferramenta é
obsoleto"* — **não se aplica**: o adaptador já existia **dez dias antes** do
carimbo. Quem carimbou tinha o ficheiro à frente.

E o ficheiro não é um coletor: é um **registo de capacidades medidas**. Regista
`facebook.identity.discovery` como o único que responde, e
`facebook.content = 302 login`, `facebook.media = 302/400 deste IP`,
`facebook.metrics = sem conteudo nao ha metrica`. Diz-o em letra própria:

> `BLOCKED NAO VIRA SUCESSO PORQUE ALGUEM ESCREVEU CODIGO PARA ELE.`

**Não repostos. Ficam 6.**

### 1b · `POLICY_BLOCK` — a `REASON` não está vazia

```
COM_MOTIVO_ESCRITO = 69   SEM_MOTIVO = 0
  44  LINKEDIN_POLICY: coleta automatizada proibida pelos TOS da plataforma
  25  INSTAGRAM_POLICY: coleta automatizada proibida pelos TOS da plataforma
todos CAND-*, todos importados do livro B2, commit 63b71421
```

A premissa da missão (`REASON = "?"`) está errada. Falta medir se por trás do
motivo houve leitura real — esse é o Lote 3.

---

## LOTE 2 — o botão que ninguém carregou estava com o fio cortado

Commits na lane viva: **`95a456ca`** e **`5f6b28c2`**.

### O defeito

```
DISCOVERY_HOOK_ERRO   2298 ocorrencias   ultima 2026-09-22T16:40:59Z
ERRO  crawl_sementes() missing 4 required positional arguments:
      'orcamento', 'conhecidos', 'visitados', 'log'
supervisor PID 107504, vivo desde 00:43, SUPERVISOR_STATE = IDLE
```

A cadeia estava ligada de ponta a ponta — `supervisor.py:511` passa
`hook_fila_vazia` → `gatilho_discovery.talvez_alimentar`. Partia no último elo:
`gatilho_discovery.py:90` chamava `crawl_sementes(max_sementes=…)` quando a
assinatura exige quatro posicionais e devolve o par `(registados, stats)`. Dois
erros na mesma linha. O `TypeError` caía no `except` de `supervisor.py:434` e
virava uma linha de log. O serviço ficava `IDLE` para sempre, a reportar-se são.

Corrigido com **a mesma construção que `descobrir.py --crawl` já usa**
(`Orcamento(total=MAX_PEDIDOS_TOTAIS)`, `_construir_set_conhecido()`,
`_ler_visitados()`, `log`). Nenhuma regra nova.

### Porque é que a suíte estava verde por cima disto

Os quatro testes existentes injectavam todos `descobrir_fn` — nunca tocaram no
caminho de produção. Acrescentada a classe `TestLigacaoRealDoDiscovery`, que
exercita `_discovery_real` **sem injecção** e valida a chamada contra a
assinatura verdadeira de `crawl_sementes`.

```
RED_TEAM  mutante = repor a chamada antiga
          2 dos 7 testes caem (TypeError: missing 'orcamento')
          mutante revertido -> 7/7 OK, arvore limpa
```

### Prova em runtime — metade sim, metade não

```
talvez_alimentar()  ACCOES = [FEEDER, DISCOVERY, FEEDER_2]
                    DECISAO = DISCOVERY_ACCIONADA
                    ZERO TypeError
FILA  0 PENDING -> 0 PENDING     ← NAO subiu. Nao se declara o que nao aconteceu.
```

### O segundo muro, atrás do primeiro

```
FEEDER     476 candidatas lidas · 476 JA_PROCESSADAS_IGNORADAS · 0 tarefas
DISCOVERY  33 sementes legitimas · 27 ja gastas · 6 por usar
           as 6 (cnr.it unimi.it unipd.it unibo.it unito.it istat.it)
           sao UNKNOWN -> recusadas pela regra ANTES da rede
           0 pedidos de rede · 0 candidatas novas · PAID_USD = 0
```

O commit `5f6b28c2` torna isto **visível**: o relatório do gatilho passa a
declarar `SEMENTES_DISPONIVEIS` · `SEMENTES_A_USAR` ·
`SEMENTES_RECUSADAS_POR_REGRA`, em vez do `0` mudo. São contadores que
`crawl_sementes` já produzia e que ninguém lia.

---

## LOTE 3 — onde estava a fome de verdade

### 3a · Os 11 do YouTube — o carimbo descreve mal o que bloqueia

```
CAND-0271  https://www.youtube.com/@ismeaofficial
CAND-0289  https://www.youtube.com/user/regionelombardia
CAND-0300  https://www.youtube.com/channel/UCNXmEqmby16fYsXOLP012tw
CAND-0331  https://www.youtube.com/playlist?list=PLrgSqU5xBcBMgcv3dofeB4RlMRFoh5-j7
CAND-0332  https://www.youtube.com/channel/UCCMlh614oidOkq-HNSa9RVA
CAND-0335  https://www.youtube.com/channel/UCCMlh614oidOkq-HNSa9RVA/featured  (duplicado de 0332)
CAND-0377  https://www.youtube.com/user/regcampania
CAND-0414  https://www.youtube.com/playlist?list=PLio2jmFoouCaMP0URkqMF83PBUSG1m1NA
CAND-0423  https://www.youtube.com/channel/UCJ8RdeFgPyGA8eyVHulEiOg
CAND-0452  https://youtube.com/playlist?list=PLrgIzVMUdTJ17DXc5r2FjOBvxEBKTt5gC
CAND-0469  http://www.youtube.com/arpatoscana
```

O motivo escrito diz *«YouTube exige channel_id … não watch-page»*. **Nenhuma é
watch-page**, e quatro trazem o `channel_id` no próprio endereço.

A causa real está em `curadoria/worker.py:396`: o `etapa_qualify` bloqueia
**todo** `TIPO == YOUTUBE` antes de olhar para o endereço, porque *«o worker só
tem molde HTML … capacidade com outro dono»*.

```
ADAPTADOR_NECESSARIO   coleta/adaptador_youtube.py
ADAPTADOR_EXISTE_HOJE  SIM — 779 linhas, coletor a serio (ao contrario do Facebook)
LIGADO AO WORKER       NAO — a rota do curator so tem molde HTML
VEREDITO               BLOQUEIO_REAL_HOJE, MOTIVO_MAL_ESCRITO
```

⚠️ **Não repostos, e digo porquê.** Repor para `CANARY_PENDING` mandá-las-ia
outra vez contra a mesma linha de código, que as voltaria a bloquear na volta
seguinte — trabalho a fingir. Ligar o adaptador do YouTube à rota do curator é
obra de integração, fora do «usa as máquinas que já existem» desta missão.
**Fica como decisão do dono**, com a medição feita.

### 3b · Os 69 `POLICY_BLOCK` — carimbo por plataforma, não por endereço

```
COM_PROVA_DE_ROBOTS = 0     SEM_PROVA_DE_ROBOTS = 69
```

A origem está em `curadoria/ponte_candidatas.py:59-71`: um dicionário fixo que
carimba por `TIPO` (`LINKEDIN`, `INSTAGRAM`), sem tocar em `robots.txt` de
endereço nenhum. Nunca houve leitura.

⚠️ **Mesmo assim, NÃO os reponho.** A missão manda repor «carimbo sem prova»,
mas aqui não é ausência de fundamento: é uma decisão de política da casa,
escrita no código ao lado do carimbo —

> *«Insistir no que a política barra não é persistência — é contorno. A ponte
> não pode ser a porta das traseiras.»*

Trocar TOS por `robots.txt` seria escolher a régua mais permissiva para chegar
ao resultado que se quer. **É decisão do dono, não minha.** Deixo o número à
vista: 69 fontes paradas por uma regra de plataforma que ninguém reexaminou.

### 3c · A fome verdadeira: 70 fontes que a casa marcou «tenta outra vez» e nunca mais tentou

```
RETRY_AFTER (no livro)      70
tarefas dessas fontes       69 FAILED · 76 DONE · 1 BLOCKED · 0 PENDING
ATTEMPTS das 69 FAILED      5 em 5 — todas no tecto
```

E o motivo das falhas:

```
62  teto de 5 tentativas: robots nao pode ser lido — UNKNOWN, nao proibicao
 5  teto de 5 tentativas: TimeoutError: The read operation timed out
 1  teto de 5 tentativas: URLError (ligacao forcada a fechar)
 1  teto de 5 tentativas: HTTP 500
```

**62 das 69 morreram por não se conseguir LER o `robots.txt`** — exactamente o
`UNKNOWN` que a lei da casa diz não ser proibição. Cinco tentativas, tecto, e a
fonte ficou parada para sempre: o livro diz `RETRY_AFTER`, a fila diz `FAILED`.
Ninguém as volta a pôr.

São **44 hosts distintos**, e entre eles estão fontes agrícolas a sério —
`coldiretti.it` (e as delegações de Puglia, Sicilia, Veneto), `confai.it`,
`copagri.it`, `unaprol.it`, `ersaf.lombardia.it`, `arpalombardia.it`,
`fitosanitario.regione.lombardia.it`, `meteotrentino.it`.

```
EGRESSO MEDIDO AGORA   146.70.182.38 · Italy · Figino (Milao) · M247  → IT = SIM
```

### 3d · ⚠️ A PRIMEIRA MEDIÇÃO DOS ROBOTS ESTAVA ERRADA

A primeira releitura, com `gate_de_rota.robots_de` em série nos 44 hosts, deu
**39 inalcançáveis**. Os tempos saíam em blocos idênticos — 26,7 s e 44,3 s —
que é assinatura de paragem de rede, não de 39 sites a recusar cada um por sua
conta.

A contraprova desmontou-a: `www.fitosanitario.regione.lombardia.it` dava
`URLError` no leitor da casa e, minutos depois, **`HTTP 200` em 1,2 s pelos dois
caminhos** (`curl` e `urllib`). A rede oscilou durante a corrida longa.

Remedição, `curl`, duas voltas por host, 8 em paralelo:

```
HOSTS 44   ALCANCAVEIS 41   INALCANCAVEIS 3
inalcancaveis: www.copagri.it · www.meteotrentino.it · www.regione.vda.it
```

E os que respondem já dão resposta com significado, em vez de silêncio:

```
200/301  33 hosts      robots legivel — a rota pode ser validada
403       4 hosts      coldiretti (www, puglia, sicilia) e unaprol
                       → a norma manda tratar como Disallow total: e PROVA,
                         nao UNKNOWN. Vira POLICY_BLOCK com fundamento.
404       4 hosts      nao publicam robots.txt — nao proibiram nada
```

**O defeito não era do leitor da casa nem das fontes: era da minha medição.**
Fica registado porque quase custou declarar 39 fontes agrícolas mortas.

### 3e · O botão carregado: a fila passou de 0 a 59

Reenfileiradas pela máquina que já existe — `fila.enfileirar`, idempotente,
`TASK_TYPE = VALIDATE_ROUTE`, o mesmo degrau que tinha falhado:

```
FONTES_ALVO            59  (as 62 menos as 3 de host inalcancavel)
FILA_ELEGIVEL_ANTES     0
FILA_ELEGIVEL_DEPOIS   59
TAREFAS_CRIADAS        59   REUTILIZADAS 0
```

E o supervisor apanhou-as **sozinho**, sem eu lhe tocar:

```
LAST_RESTART_REASON  "sem worker vivo e 59 tarefas elegiveis"
SUPERVISOR_STATE     IDLE -> RUNNING
WORKER_PID           122452   (supervisor 107504 nunca foi morto)
QUEUE_DONE           706 -> 752
```

---

## AS DUAS LEITURAS, LADO A LADO

```
                         materia-prima-v1     LANE VIVA (a que conta)
candidatas em carteira         241                   476
tarefas na fila                 68                   855
fontes no livro                555                   437
READY_FOR_COLLECTION           109                    40
CAPABILITY_BLOCK                28                    31
POLICY_BLOCK                    69                    69
QUEUE_PENDING                    0                     0
```

---

## LOTE 5 — o que o motor produziu

O worker correu as 59 até ao fim, sozinho, e esvaziou a fila outra vez:

```
DESTINO DAS 59
  15  READY_FOR_COLLECTION          ← materia-prima nova
  44  CONTRACTED_CANARY_FAILED      «nenhum dos N enderecos da entrada casa
                                     com o padrao — EMPTY_LIST, como o
                                     contrato preve»
```

As 15 que passaram a régua inteira:

```
IT-T11-010  IT-T12-019  IT-T12-027  IT-T12-057  IT-T12-074  IT-T12-086
IT-T12-089  IT-T12-095  IT-T5-082   IT-T7-050   IT-T7-051   IT-T7-052
IT-T7-053   IT-T7-058   IT-T9-021
```

Movimento no livro, medido nas duas pontas:

```
                      ANTES   DEPOIS
READY_FOR_COLLECTION    40      55     +15
RETRY_AFTER             70      11     −59
CANARY_FAILED          153     153 (109 -> 153, +44 das reenfileiradas)
QUEUE_DONE             706     824
QUEUE_PENDING            0       0     (0 -> 59 -> 0: entrou e saiu)
```

`READY-SOURCES-V1.json` — o ficheiro que a Collection lê — foi regerado com
`READY_TOTAL = 55`. Commit na lane viva: **`1c4ef5e8`**.

Taxa real desta leva: **15 em 59 = 25,4%**. As 44 que caíram não caíram por
culpa da fonte: o padrão de link do contrato não casou com nenhum endereço da
página de entrada. É defeito de contrato, e fica escrito como tal.

---

## LOTE 6 — os dois poços secos, e o que ainda tem água

### 6a · Fase 3 (creators e investigadores) — os dois motores estão secos

Corridos os dois motores de descoberta que existem, sem escrever nada de novo:

```
descobrir.py --familia SOCIAL_PUBLICO        14 achados · 14 duplicados · 0 novas · 0 pedidos
             --familia UNIVERSIDADES_CENTROS  5 achados ·  5 duplicados · 0 novas · 0 pedidos
             --familia CIENCIA_APLICADA       5 achados ·  5 duplicados · 0 novas · 0 pedidos
             --familia ASSOCIACOES            6 achados ·  6 duplicados · 0 novas · 0 pedidos
             --familia COOPERATIVAS           4 achados ·  4 duplicados · 0 novas · 0 pedidos

crawl_sementes  33 sementes · 27 gastas · 6 restantes, todas UNKNOWN e recusadas
```

```
CREATORS_ANTES/DEPOIS    = 6 / 6
RESEARCHERS_ANTES/DEPOIS = 0 / 0
PAID_USD = 0   REQUESTS_MADE = 0 (a deduplicacao corre ANTES da rede)
```

**Os dois motores consumiram tudo o que tinham.** O catálogo de famílias está
todo já em carteira e a lista de sementes está gasta. Trazer fontes novas exige
**sementes novas** — entrada humana, não uma corrida a mais. Não as invento.

### 6b · Correcção: as 66 `QUALIFY` bloqueadas não são um nó cego

Li mal à primeira. O campo `MOTIVO` guarda a etiqueta que a ponte escreveu na
criação (*«aguarda qualificacao pelo curator»*), e por isso parecia uma tarefa
de qualificação à espera de qualificação. A razão verdadeira está noutro campo,
o `LAST_ERROR`. Classificadas as 80 bloqueadas por aí:

```
55  SEMANTIC   «territorio indeterminado pelo nome — SOURCE_ID fica UNKNOWN,
                sem fabricar; precisa de decisao semantica (Opus/humano)»
13  ROBOTS     «o endereco do contrato casa com Disallow no robots vivo»
11  CAPABILITY YouTube (os mesmos do Lote 3a)
 1  sem contrato nesta arvore
```

Os 13 do robots estão **correctamente** bloqueados, com prova viva. A casa
funciona.

### 6c · Onde ainda há água: 55 fontes à espera de uma decisão humana

As 55 `SEMANTIC_REVIEW` são o maior bolso por abrir, e o próprio worker diz
para quem manda o recado: *«precisa de decisao semantica (Opus/humano)»*. Entre
elas, por exemplo, `CAND-0253` = **AGEA, Agenzia per le Erogazioni in
Agricoltura** — a agência nacional italiana de pagamentos agrícolas. O worker
recusa-se a adivinhar o território dela, e faz bem.

⚠️ **Não avanço sozinho, e digo o risco.** Decidir o território aloca um
`SOURCE_ID` no Atlas, e o registo de `SOURCE_ID` está partido por várias
branches — alocar pelo atlas local já colidiu em 11 de 12 territórios noutra
missão. Fazer 55 alocações no fim de uma sessão longa, sem reconciliação
prévia, é a forma de transformar um bolso cheio num livro partido.
**Decisão do dono.**

---

## ESTADO DA MISSÃO

```
CARIMBOS_OBSOLETOS_REPOSTOS   = 0   (6 Facebook + 11 YouTube medidos e VALIDOS hoje)
POLICY_BLOCK_SEM_PROVA        = 69  medidos, NAO repostos — decisao do dono
FILA_ANTES/DEPOIS             = 0 / 59 / 0   (entrou e foi toda consumida)
READY_CURRENT_ANTES/DEPOIS    = 40 / 55
CREATORS_ANTES/DEPOIS         = 6 / 6    (dois motores corridos, ambos secos)
RESEARCHERS_ANTES/DEPOIS      = 0 / 0    (idem — catalogo todo ja em carteira)
COLLECTION_ELIGIBLE_ANTES/DEPOIS = por medir — ver abaixo
ITENS_COLHIDOS                = 0
PAID_USD                      = 0
NEW_FAILURES                  = 0
```

### Porque é que a Fase 4 (colher) não avançou aqui

O portão de colheita — `curadoria/collection_gate.py` e `ready_split.py` — **não
existe na lane viva**. Vive nesta worktree (`materia-prima-v1`). As duas
linhagens divergiram: a lane do serviço tem o bot, esta tem o portão.

Colher exigiria correr o portão desta árvore sobre o livro da outra. Não o faço
por iniciativa própria: é cirurgia entre ramos, e a missão diz `zero bypass`.
**Fica como a decisão seguinte do dono.**

### Falha pré-existente encontrada (não minha, não corrigida)

```
curadoria/veredito_ready.py  ->  KeyError: 'CAND-0013'  (linha 58)
```

Já vinha assim. Não lhe toquei — arranjá-lo é obra fora desta missão.

---

## EM PALAVRAS SIMPLES

O robô tinha o interruptor ligado e o fio até à lâmpada inteiro. No último
centímetro, o fio estava cortado. De cada vez que tentava, escrevia um bilhete
de queixa numa gaveta que ninguém abria — 2298 bilhetes — e voltava a dizer
"estou bem, sem trabalho". Emendei o fio, e a lâmpada acendeu.

Só que atrás havia um segundo problema: o poço de onde ele tira fontes novas
está seco. Das 33 nascentes, 27 já foram bebidas, e as 6 que restam estão
marcadas com "não sei se isto é água boa" — e a regra manda não beber. Por isso
ainda não entrou matéria-prima nenhuma. Nenhum dinheiro foi gasto.

Do lado dos carimbos: os 6 do Facebook **não** estavam errados. O ficheiro que
parecia ser a chave da porta é, na verdade, o relatório de quem foi lá bater e
levou com a porta na cara.

Onde estava mesmo a comida: **70 fontes tinham dois papéis a dizer coisas
diferentes.** Um dizia "volta cá amanhã"; o outro, na fila, dizia "esta morreu".
Ninguém comparava os dois. E 62 delas não tinham morrido: a casa só não
conseguiu ler a placa da porta cinco vezes seguidas — e a lei desta casa diz,
com todas as letras, que não conseguir ler a placa **não é** proibição.

Fui lá bater outra vez: **41 das 44 portas abriram**. Voltei a pôr 59 fontes na
fila, e o robô — que nunca desliguei — acordou sozinho e trabalhou-as todas.
**Quinze passaram a régua inteira e são matéria-prima nova.** As outras 44
caíram, e não foi culpa delas: a receita que tínhamos escrito para as ler estava
errada.

E há uma coisa que eu próprio fiz mal, e convém ficar escrita: à primeira
medição, disse que 39 destes sites estavam bloqueados. Estava errado — era a
nossa ligação que tinha parado naquele minuto, não os sites. Se eu tivesse
parado aí, tinha-te dito que 39 fontes agrícolas estavam mortas. Não estavam.

Ainda não chegou nada ao arquivo. O portão que faz a colheita vive noutro ramo
do trabalho, e juntar os dois ramos é decisão tua, não minha.

---

## LOTE 7 — as gavetas juntas (autorizado pelo dono)

**Nenhum `git merge`.** A máquina certa já existia:
`curadoria/reconciliar_livros.py`, que trata o bot como **livro C** — lido por
`git show` no HEAD dele **de agora** (`1c4ef5e8`), nunca o ficheiro vivo, porque
o supervisor pode estar a gravar a meio. Reconcilia por `SOURCE_ID` e aplica por
`lifecycle.registar`: acréscimo validado, nunca cópia por cima.

```
LINHAS_ANTES   1450        LINHAS_DEPOIS  1524      APENDIDAS 74
CADEIAS_ILEGAIS_NAO_IMPORTADAS   []
BOT_READY 55 · ACEITES 47 · RECUSADAS 8 (PROMOCAO_SEM_PROVA_DE_CANARIO)
```

### As cinco regras, uma a uma, medidas

```
1  o bot NUNCA escreve COLLECTION_ELIGIBLE
   quem escreveu `False` em IT-T12-019 foi CG.avaliar — o gate, não o bot

2  READY_LEGACY não se lava pela junção
   as 15 do bot entram como LEGACY. DETAIL_PROOF_C:
     INDEX_URL true · DETAIL_LINKS true · ITEM_ABERTO false · BODY_UTIL false

3  POLICY_BLOCK e CAPABILITY_BLOCK com prova não desaparecem
   POLICY_BLOCK      69 -> 69   sairam do estado: 0
   CAPABILITY_BLOCK  28 -> 28   sairam do estado: 0

4  replay do mesmo evento = NO_OP
   SEGUNDA_PASSAGEM_PLANEIA = 0

5  recollection UNKNOWN não ganha passagem
   UNKNOWN 34 antes · 0 viraram READY
```

Mudanças de estado na aplicação — **só as 59 que eu tinha reenfileirado**:

```
44  RETRY_AFTER -> CANARY_PENDING
15  RETRY_AFTER -> READY_FOR_COLLECTION
 0  fontes novas
```

### O GATE, ANTES E DEPOIS

```
                        ANTES   DEPOIS
READY_TOTAL              109     124    +15
READY_CURRENT_TOTAL       10      10     0
READY_LEGACY_TOTAL        99     114    +15
HUMAN_REVIEW_REQUIRED      3       3     0
COLLECTION_ELIGIBLE        8       8     0
```

**O número honesto é menor do que se esperava, e reporta-se menor.**

### A prova de UMA fonte, ponta a ponta — `IT-T12-019` (ERSAF Lombardia)

```
1 O BOT APROVA     livro C @ source-curator-service-v1
                   NEW_STATE    READY_FOR_COLLECTION
                   OBSERVED_AT  2026-09-22T17:26:01Z
                   EVIDENCE_REF EV-IT-T12-019-CANARY-1196

2 LIVRO CANONICO   5 transicoes desta fonte; a ultima:
                   CANARY_PENDING -> READY_FOR_COLLECTION
                   IMPORTADO_DE { MISSAO: RECONCILIACAO-V1,
                                  EVIDENCE_SOURCE: "livro C (bot)" }

3 O GATE VE        STATE                READY_FOR_COLLECTION
                   READY_RULE           LEGACY
                   COLLECTION_ELIGIBLE  False
                   MOTIVO               READY_LEGACY
                   PORQUE               «promovida pela regua antiga; a regua
                                        de hoje e DETAIL/v1 — item aberto,
                                        retratado e com corpo util»
```

**O caminho está aberto e funciona.** O bot aprova, a prova atravessa com
proveniência, e o gate vê e decide **sozinho** — e disse que não. Não é falha da
ponte: é a régua a fazer o seu trabalho.

### O que falta para estes 15 virarem colheita

O canário do bot para em `DETAIL_LINKS`. Para chegar a `DETAIL/v1` falta abrir
**um item** e provar **corpo útil** — os passos 3 e 4. A máquina que faz isso
existe nesta lane (`executor_texto_de_html.py`, `incrementalidade.mjs`) e não
está ligada ao canário do bot. É o mesmo padrão dos 11 do YouTube: a capacidade
existe, a ligação não.

`ITENS_COLHIDOS = 0` · `PAID_USD = 0` · Big Collection **não** executada.

---

## LOTE 8 — os quatro passos fechados: `COLLECTION_ELIGIBLE 8 → 11`

**Objectivo cumprido: `> 8` com prova dos quatro passos.**

### As quatro tampas, por ordem

**1 · O worker do bot não tinha os passos 3 e 4 — tinha o mesmo ficheiro, mais velho.**

```
grep ITEM_ABERTO|BODY_UTIL|retrato_html na lane do bot  ->  ZERO ocorrencias
worker.etapa_canary ja chamava CANARIO.canario_html     ->  212 linhas, nao 245
```

Trazidos ficheiro a ficheiro, sem merge: `retrato_html.py` (novo lá, sem
dependências do projecto) e `canario.py` (212 → 245). **O worker não foi
tocado.** Testes 14/14. *(bot `95567c43`)*

**2 · Corridas as 15 no canário completo — 9 provaram os quatro passos.** *(bot `e26de5e2`)*

**3 · `READY → READY` é recusado por lei**, logo recanariar não actualizava a
promoção, que continuava a citar a prova de 2/4. Caminho legal:
`READY → CANARY_PENDING`, e só a nova corrida promove. 9 de 9.

**4 · A ponte importava ZERO provas, sempre.** *(canónica `be09703c`)*

```
o plano cita   RECONCILIACAO-V1:livro_C_(bot)@<commit>:EV-IT-T12-019-CANARY-1282
o manifesto C  EV-IT-T12-019-CANARY-1282
```

Nunca casavam. A função que existe **para evitar** o entupimento no último metro
estava entupida por dentro. Corrigida: procura pela chave nua, importa com a
chave sintética (a que a promoção cita). **24 provas importadas, 0 colisões**,
manifesto 550 → 574.

**5 · A régua lê o `INDEX_URL` do CONTRATO — e o contrato ficara na gaveta do bot.**
*(canónica `a7ddd069`)*

```
contratos nesta arvore  81        no bot 279        so no bot 202
desses, READY aqui      36
uniao por SOURCE_ID: 202 importados · 0 SOBREPOSTOS (o contrato local manda)
```

### O NÚMERO

```
                        ANTES   DEPOIS
READY_TOTAL              109     123
READY_CURRENT_TOTAL       10      14
READY_LEGACY_TOTAL        99     109
HUMAN_REVIEW_REQUIRED      3       4
COLLECTION_ELIGIBLE        8      11    ← +3
```

### As três novas, com os cinco campos à vista

```
IT-T12-057  DETAIL/v1  INDEX_URL·DETAIL_LINKS·ITEM_ABERTO·BODY_UTIL·CONTRATO_ATUAL = todos true
            /news/news/578/nominato-il-primo-forum-…   CONTENT · MATERIA_PROVAVEL · 1826
IT-T12-074  idem
            /it/news/news/9441/digital-h…             CONTENT · MATERIA_PROVAVEL · 2738
IT-T9-021   idem
            /it/news/aperte-le-iscrizioni-ai-90-…     CONTENT · MATERIA_PROVAVEL · 3686
```

Nenhuma foi promovida sem os quatro passos. O que mudou foi a régua passar a
**ver** a prova que já existia.

### As 6 que continuam de fora, e exactamente porquê

```
4  BODY_UTIL nao provado — o item abriu e tem 1.564 a 3.471 caracteres de
   paragrafo, mas o classificador diz MIXED/NAO_SEI. «NAO SEI» nao e «materia»,
   e esta casa nao promove NAO SEI.
1  IT-T12-095 e IT-T11-010 sao DETAIL/v1 mas caem em HUMAN_REVIEW_REQUIRED:
   o endereco do item parece seccao. Pede olho humano, nao condena a fonte.
1  reprovou o canario
```

`PAID_USD = 0` · Big Collection **não** executada · supervisor 107504 vivo do
princípio ao fim.

---

## LOTE 9 — FASE 2 da missão: as 77 `READY_LEGACY` re-testadas

As «77» da missão apareceram, e são exactamente 77:

```
READY_LEGACY no gate        109
  com contrato nesta arvore  77   ← as 77
  conhecidas pelo bot        77
  e READY no livro do bot    35   ← as que podiam correr JA
```

As 35 voltaram a `CANARY_PENDING` (porque `READY → READY` é recusado por lei) e
correram o canário dos 4 passos:

```
14  READY_FOR_COLLECTION
16  CONTRACTED_CANARY_FAILED
 5  por acabar
```

### O que isto mudou — e o que não mudou

```
                        ANTES   DEPOIS
READY_TOTAL              123     102    −21
READY_CURRENT             14      14      0
READY_LEGACY             109      88    −21
COLLECTION_ELIGIBLE       11      11      0
```

**16 fontes que se diziam `READY` não resolvem contra a rede real.** Estavam
promovidas pela régua antiga e nunca tinham sido re-testadas. Não se perdeu
colheita nenhuma — `LEGACY` nunca foi elegível. Ganhou-se a verdade sobre elas.

A correcção da ponte (`be09703c`) provou-se nesta corrida: **16 provas
importadas**, onde antes eram sempre 0.

### As 14 que passaram continuam `LEGACY`, e porquê

```
6  falta ITEM_ABERTO,BODY_UTIL     a promocao citada e anterior ao canario novo
4  BODY_UTIL: corpo MIXED/NAO_SEI  ha texto, o classificador nao jura que e materia
3  falta DETAIL_LINKS,ITEM_ABERTO,BODY_UTIL
1  falta DETAIL_LINKS
```

Os 6 e os 3 são o mesmo padrão estrutural já visto: a promoção no livro
canónico aponta para a evidência que existia **antes** do canário novo. A ponte
move estados e agora também traz provas, mas **não refresca a citação de uma
promoção cujo estado não mudou**. É a próxima tampa, e está nomeada.

---

## LOTE 10 — a terceira tampa: `COLLECTION_ELIGIBLE 11 → 17`

A ponte move estados e (depois de `be09703c`) traz provas, mas **não refresca a
citação de uma promoção cujo estado não mudou**. Não se corrige na ponte:
`lifecycle` recusa `READY → READY`, por lei. Corrige-se pela **ordem** das
máquinas que já existem:

```
1  despromover na arvore canonica    (carimbo T)
2  despromover e recanariar no bot   (promove em T+n, logo mais recente)
3  reconciliar                       (C mediu depois -> promove e traz a prova)
```

A ordem não é detalhe: à primeira tentativa fi-lo ao contrário, a despromoção
local ficou **posterior** à promoção do bot, e a ponte respondeu «C mediu ANTES
desta árvore — não derruba». Zero planeado.

```
ALVO  14  (READY em A e em C, contrato aqui, mas LEGACY por citar prova velha)
      14 de 14 repromovidas no bot
PONTE 14 transicoes · 14 provas importadas · 0 colisoes · manifesto 590 -> 604
```

### O NÚMERO

```
                        ANTES   DEPOIS
READY_TOTAL              102     102
READY_CURRENT_TOTAL       14      21
READY_LEGACY_TOTAL        88      81
HUMAN_REVIEW_REQUIRED      4       6
COLLECTION_ELIGIBLE       11      17    ← +6
```

### As 6 novas, com o item que abriram

```
IT-T10-021  plantgest.imagelinenetwork.com/…        CONTENT · MATERIA · 1489
IT-T12-041  bura.regione.abruzzo.it/bollettino/…    CONTENT · MATERIA · 5650
IT-T2-034   arpa.marche.it/notizie-2026/…           CONTENT · MATERIA · 3109
IT-T2-051   arpae.it/it/notizie/30-anni-…           CONTENT · MATERIA · 1253
IT-T2-056   arpae.it/it/notizie/30-anni-…           CONTENT · MATERIA · 1253
IT-T7-021   etvilloresi.it/attivita/progetti…       CONTENT · MATERIA · 4545
```

### As 8 que continuam de fora, nomeadas

```
6  BODY_UTIL: o item e MIXED/NAO_SEI. Ha texto (799 a 3.471 caracteres), o
   classificador nao jura que e materia. NAO SEI nao e materia.
1  IT-T5-064: DETAIL/v1, mas HUMAN_REVIEW_REQUIRED (o endereco parece seccao)
1  IT-T11-010: CONTENT/MATERIA/3201 e mesmo assim LEGACY — o LINK_PATTERN do
   contrato so encontra 1 ligacao de detalhe e a regua exige 2. Nao e defeito:
   e a regua, e o contrato e que e estreito de mais.
```

## O SALDO DA MISSÃO ATÉ AQUI

```
DISCOVERY_HOOK_ERRO       2298 -> 0
FILA                      0 -> 59 -> 0 -> 15 -> 0 -> 35 -> 0 -> 14 -> 0
COLLECTION_ELIGIBLE       8 -> 17          (+9, todas com os 4 passos)
READY_CURRENT             10 -> 21
READY falsas expostas     16
PAID_USD                  0
supervisor 107504         vivo do principio ao fim
```

---

## LOTE 11 — a veia mecânica esgotou-se. Rendimento desta volta: **ZERO**

Corrida a mesma sequência de três passos nas `READY_LEGACY` que restavam. Só 7
estavam em condições de correr, e correram:

```
PONTE  7 transicoes · 7 provas importadas · 0 colisoes · manifesto 604 -> 611
GATE   COLLECTION_ELIGIBLE 17 -> 17      READY_CURRENT 21 -> 21
```

**Não subiu nada.** As 7 voltaram com prova fresca e continuam `LEGACY` pelas
mesmas duas razões de sempre:

```
IT-T11-010  CONTENT/MATERIA · 3201 car. · DETAIL_ENUMERATED = 1   falta DETAIL_LINKS (exige 2)
IT-T12-019  MIXED/NAO_SEI · 3471 car. · n=30
IT-T12-086  MIXED/NAO_SEI · 1564 car. · n=2
IT-T12-089  MIXED/NAO_SEI · 1564 car. · n=1
IT-T2-049   MIXED/NAO_SEI · 2340 car. · n=1
IT-T5-082   MIXED/NAO_SEI ·  799 car. · n=6
IT-T7-040   MIXED/NAO_SEI ·  932 car. · n=9
```

Repetir a sequência nestas não produz mais nada: a prova já é a mais recente.
**O que falta não é mecânica — são decisões.**

### As 81 `READY_LEGACY` que sobram, repartidas por causa

```
50  RECONCILIATION_REQUIRED no bot, todas com o MESMO motivo:
    «bloqueio medido contra feeds/videos.xml; a integracao deu rota nova None»
    → sao fontes de YouTube. Caem no mesmo sitio que os 11 CAPABILITY_BLOCK:
      o adaptador existe, a ligacao a rota do curator nao.
32  sem contrato em livro nenhum (ja importei os 202 do bot — nao existem)
 7  as de cima: MIXED/NAO_SEI ou DETAIL_LINKS < 2
```

### As três decisões que destrancam cada bolso

```
1  YOUTUBE       ligar coleta/adaptador_youtube.py a rota do curator.
                 Destranca ate 50 LEGACY + 11 CAPABILITY_BLOCK. E integracao.
2  CLASSIFICADOR CAPA_NAO_E_MATERIA/v1 devolve NAO_SEI em paginas com 3.471
                 caracteres de texto corrido. Mexer-lhe e mexer na LEI.
3  CONTRATOS     32 fontes READY sem contrato nenhum. Escrever contrato e
                 trabalho de curadoria, nao de maquina.
```

**Nenhuma delas é minha para tomar.** Paro aqui e reporto, como a missão manda.

---

## LOTE 12 — FASE 4: A COLHEITA. **76 documentos reais no armazém.**

Corrido o entrypoint canónico, sem atalho nenhum:

```
node coleta/italy_recurrent_collect.mjs --profile forward-only-live --no-git
```

Ordem obrigatória cumprida inteira: `lock · runtime · timezone · VPN Itália ·
storage · contratos · PORTÃO DE ADMISSÃO · RUN_ID · RAW primeiro · bytes · sha ·
RAW imutável · ledger · normalizar`. **Zero bypass.**

```
RUN_ID      OPS_forward-only-live_20260922185447_a9d037
VPN         IT · EGRESS_IP 205.147.30.2
DURACAO     18:54:49Z -> 18:58:26Z
```

### O portão decidiu, não eu

```
COLLECTION_ELIGIBLE        17
  ELIGIBLE_WITH_CONTRACT    9   ← colhidas
  ELIGIBLE_WITHOUT_CONTRACT 8   ← rota que falta DO NOSSO LADO, e fica dita
COLLECTION_REFUSED_TOTAL   85
```

⚠️ As 8 sem contrato exigiriam escrever **contrato novo** em
`regras/italy_contracts.mjs` — e isso a missão proíbe por escrito. **Não as
escrevi.** `ELIGIBLE_WITHOUT_CONTRACT` não é falha da fonte nem não do portão: é
trabalho que falta, com nome próprio.

### O QUE ENTROU

```
ITENS_COLHIDOS   76        (observacoes 445 -> 521)
BYTES            7.563.718  mediana 95.880 por documento
MIME             text/html, 76 de 76
COM RAW_SHA256   76 de 76   (RAW preservado antes de interpretar)

IT-T7-017  30    IT-T7-033  15    IT-T10-022 10    IT-T7-042 10
IT-T10-018  9    IT-T10-021  1    IT-T7-021   1
```

**`IT-T10-021` e `IT-T7-021` só ficaram elegíveis por causa desta missão** — as
outras cinco já passavam antes.

## SALDO FINAL

```
DISCOVERY_HOOK_ERRO        2298 -> 0
FILA                       0 -> 59 -> 15 -> 35 -> 14 -> 7 -> 0
COLLECTION_ELIGIBLE        8 -> 17        (+9, todas com os 4 passos)
READY_CURRENT              10 -> 21
READY falsas expostas      16
ITENS_COLHIDOS             76
MATERIA_REAL               76 HTML com sha256, mediana 95 KB
CAPAS                      0 admitidas — o gate de detalhe corre ANTES
CREATORS / RESEARCHERS     6/6 · 0/0 (os dois motores estao secos)
PAID_USD                   0
NEW_FAILURES               0
supervisor 107504          vivo do principio ao fim
```

**HARD STOP** — a missão manda parar depois da primeira colheita com o conjunto
novo. Paro aqui.
