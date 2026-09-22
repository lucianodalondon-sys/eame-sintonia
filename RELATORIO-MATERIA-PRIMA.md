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

A releitura dos 44 `robots.txt` com o leitor da casa
(`gate_de_rota.robots_de`) está a correr.

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

## ESTADO DA MISSÃO

```
CARIMBOS_OBSOLETOS_REPOSTOS = 0 ate agora (6 do Facebook medidos e VALIDOS)
POLICY_BLOCK_SEM_PROVA      = por medir
FILA_ANTES/DEPOIS           = 0 / 0
CREATORS_ANTES/DEPOIS       = por medir
PAID_USD                    = 0
NEW_FAILURES                = 0
```

**A FAZER:** os 11 do YouTube · a prova dos 69 `POLICY_BLOCK` · encher a fila ·
reiniciar o supervisor com a fila já cheia.

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
