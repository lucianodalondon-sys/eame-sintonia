# SCRAP-FLOW-02 — a segunda rota pelo fluxo canônico, e ela não compra nada

> ```
> FREE != CANONICAL.  ROUTE WORKS != FLOW WORKS.  FREE_ROUTE != NO_GATES.
> ```

A SCRAP-FLOW-01 levou a fase **paga** ao caminho canônico e fechou com uma
declaração honesta:

> `CANONICAL_ORCHESTRATION(o fluxo) = NÃO` · «`janela*` continua a saltar o
> orquestrador».

Esta missão respondeu à pergunta seguinte: **o fluxo canônico funciona também
para uma aquisição gratuita, sem depender dos contratos específicos de uma
compra?** A resposta é sim — e o caminho até lá encontrou dois defeitos que
ninguém tinha medido.

---

## O QUE FOI MEDIDO ANTES DE SE DECIDIR QUALQUER COISA

```
CURRENT_BRANCH          claude/wonderful-hamilton-m50ahv
BASE_HEAD               af17f6d998f2e06917968f8045f4b5acd1715326
REMOTE_HEAD             af17f6d9  (igual)  ·  WORKTREE limpo  ·  1 worktree
SCRAP_FLOW_01_BRANCH    claude/wonderful-hamilton-m50ahv  @ af17f6d9   (esta linha)
KNOW_HOW_HEAD           claude/sintonia-eame-know-how-v1  @ 72c59dbe
TESTES (antes)          141 · 17 falhas pré-existentes
```

### ⚠️ A SCRAP-FLOW-01 CORREU EM DUAS LINHAS, E ELAS NÃO SE CONHECEM

O `git fetch` desta missão trouxe um ramo que não existia no fecho anterior:

```
claude/sintonia-scrap-canonical-flow-f01  @ 84422284
  «SCRAP-FLOW-01: um fluxo operacional real atravessa o orquestrador canonico»
  base comum com esta linha: e90451e1  (muito atrás)
```

Ele implementa **a mesma missão SCRAP-FLOW-01**, e implementa-a **sobre a rota
`janela`** — a mesma que esta missão migrou. As duas linhas divergem no
mecanismo, e a divergência é concreta:

| | esta linha (`wonderful-hamilton`) | a outra (`canonical-flow-f01`) |
|---|---|---|
| rota migrada na FLOW-01 | `yt-legenda-paga` (paga) | `janela` (grátis) |
| quem escolhe o executor | `receitas.escolher` + `pedido_pede` | `serve_fases` |
| onde a corrida declara | `retorno.ENVELOPE` → `RETORNO.json` | `envelope_em` → `ENVELOPE.json` |
| quem adapta o SCRAP à porta | `coleta/social_scrap.py` (o que já existia) | `coleta/scrap_colheita.py` (novo) |
| ficheiro de prova | `provas/o_fluxo_canonico_do_scrap.py` | `provas/o_fluxo_canonico_do_scrap.py` — **mesmo nome, outro conteúdo** |

**Nada disto foi fundido nesta missão, e a decisão é declarada:** reconciliar
duas implementações da mesma lei é uma escolha de arquitetura, e ela pertence a
uma pessoa — não a um efeito colateral de uma migração. O que esta missão faz é
**medir e dizer**, para que a escolha seja feita com os dois lados à vista.

```
RECONCILIACAO_PENDENTE = SIM
QUEM_DECIDE            = gente
O_QUE_COLIDE           = pedido/receitas.py · orquestrador/orquestrador.py
                         provas/o_fluxo_canonico_do_scrap.py (nome)
```

---

## FASE 1 · O CENSO DOS BYPASSES GRATUITOS

Medido nesta linha, entrypoint a entrypoint — e **não** pelo nome que o
relatório anterior citou.

| entrypoint | plataforma / capacidade | rota | grátis | credencial | prova | fonte nas 77 | adquire? | salta o orquestrador? |
|---|---|---|---|---|---|---|---|---|
| `sintonia-scrap.yml janela*` → `social_scrap.py coletar` | INSTAGRAM / `instagram.profile.discovery` | `PUBLIC_BROWSER` | **sim** | **não** | `PARTIAL`, rota `PROVED` na matriz | não | **sim** | **sim** |
| `comunicacao-publica.yml` → T9/`posts`/YOUTUBE | YOUTUBE / `channel.resolve`+`discovery` | `OFFICIAL_API_FREE` | sim | sim | `PROVEN` | T9 | sim | **não — já é canônico** |
| `scrap-social.yml piloto` | MASTODON · BLUESKY · TELEGRAM | `PUBLIC_NATIVE` | sim | não | `PROVEN` | não | sim | sim, **e é medição declarada** |
| `scrap-social.yml youtube` | YOUTUBE / Data API direta | `OFFICIAL_API_FREE` | sim | sim | `PROVEN` | T9 | sim | sim, **e é medição declarada** |
| `scrap-social.yml youtube-oficial` | a MESMA API pelo executor | `OFFICIAL_API_FREE` | sim | sim | `PROVEN` | T9 | sim | sim, **e é prova (`…_prova`)** |
| `scrap-social.yml youtube-piloto*` · `cutover` | YOUTUBE | direta | sim | sim | — | — | sim | sim, **e são medições declaradas** |
| `sintonia-scrap.yml` restantes fases | — | — | — | — | — | — | recusadas no disparador | — |

**Por que as medições não se migram.** O próprio repositório escreve, ao lado
delas:

> «`youtube` existe para medir a API DIRETAMENTE, e `youtube-oficial` existe
> para medir a MESMA API pelo executor. O par é a medição: fazer as duas
> entrarem pela mesma porta apagava exactamente a pergunta que elas respondem —
> `MODULE EXISTS != EDGE EXISTS != FLOW EXISTS`.»

```
SELECTED_ROUTE       = janela · janela-perfis · janela-objetos
                       INSTAGRAM / instagram.profile.discovery · PUBLIC_BROWSER
WHY_SELECTED         = o único entrypoint GRATUITO desta linha que adquire em
                       OPERAÇÃO e ainda salta o orquestrador. Sem credencial,
                       sem provider, sem dinheiro; rota PROVED na matriz;
                       produz artefato e RAW observáveis.
WHY_OTHERS_REJECTED  = ou já são canônicos, ou são MEDIÇÕES declaradas cuja
                       conversão apagaria o que elas medem, ou são recusadas
                       no próprio disparador.
```

---

## FASE 3 · O CAMINHO, ANTES

```
sintonia-scrap.yml (fase=janela)
  └─► py coleta/social_scrap.py coletar janela $TETO
        └─► scrap_executor.COLLECT(INSTAGRAM, instagram.profile.discovery)
              └─► social_rotas → adaptador_instagram → instagram_janela → CDP
```

```
USES_PEDIDO                        NÃO
USES_ORCHESTRATOR                  NÃO
RUN_ID_CREATED_BEFORE_EXECUTION    NÃO — a CLI cunhava um por execução
SOURCE_RELEVANCE_CHECKED           NÃO — ninguém perguntava
OUTPUT_DECLARED                    SIM (envelope), mas sem origem por unidade
RECEIPT_WRITTEN                    NÃO
INGRESS_CALLED                     NÃO
```

## FASE 4 · O CAMINHO, DEPOIS

```
sintonia-scrap.yml (fase=janela)                      ENTRYPOINT
  └─► py orquestrador/orquestrador.py "colete concorrentes" --filtro fase=janela
        └─► pedido.Pedido                             REQUEST
        └─► receitas.resolver → Plano                 ORCHESTRATOR
              · receitas.escolher       — QUAL executor (dono único)
              · relevancia_da_fonte.portao — antes de qualquer coisa correr
              · novo_run_id             — a corrida nasce ANTES
        └─► subprocess: social_scrap.py coletar janela [teto] --run-id=…
              └─► scrap_executor.COLLECT              SCRAP EXECUTOR
                    · orcamento_de_rede · social_rotas · adaptador · CDP
        └─► RETORNO.json declarado pela corrida       COL-LAW-505
        └─► a_colheita → ingresso → admissão → recibo
```

```
USES_PEDIDO                        SIM
USES_ORCHESTRATOR                  SIM
RUN_OWNER                          orquestrador (novo_run_id, antes do subprocesso)
OUTPUT_DECLARED                    SIM — e agora com origem POR UNIDADE
```

---

## O QUE MUDOU NO CÓDIGO, E PORQUÊ

### 1 · Três nomes de fase, uma rota

`receitas.escolher` já tinha dono único desde a FLOW-01, mas o selector
comparava **um** valor. A janela tem três nomes de fase e **uma** rota — e o
adaptador já escrevia isso por extenso: «DUAS CAMADAS DE UMA ROTA NÃO SÃO DUAS
ROTAS». Registar três executores daria três donos ao mesmo ato.

`_casa()` passou a aceitar uma coleção: um valor exige igualdade, uma coleção
exige pertença. **A ordem da lista continua a não decidir nada** — provado com
quatro ordens diferentes, incluindo a invertida.

### 2 · A origem de cada unidade deixou de ser deduzida da fase

A FLOW-01 escrevia, em cada unidade colhida:

```python
'SOURCE_ID': 'SCRAP-YOUTUBE/%s' % fase
```

Isso era verdade — **enquanto só houvesse uma fase**. Com uma segunda rota, a
mesma linha teria carimbado `SCRAP-YOUTUBE` em cima de material do Instagram.

> **UM LITERAL QUE ACERTA PORQUE SÓ HÁ UM CASO É UM LITERAL QUE VAI MENTIR.**

Agora cada unidade **traz** a sua origem, e quem a carimba é quem sabe: o
adaptador, que leu o artefato e **copiou o `SOURCE_ID` que o próprio artefato
declara** — `INSTAGRAM-JANELA/PERFIS`, `INSTAGRAM-JANELA/OBJETOS`. Quem chega
sem origem **não recebe uma**: fica de fora, e o número fica escrito no
envelope.

> **QUEM PRODUZ DIZ DE ONDE VEIO. QUEM DECLARA SÓ TRANSCREVE.**

E o literal da rota paga passou a viver num sítio só
(`origem_do_registo_pago`), porque estava escrito em dois.

### 3 · O `teto` desce pelo pedido — e não é um teto que guarda a casa

A FLOW-01 escreveu que «um teto que vive no disparador é um teto que quem
dispara escolhe», e escreveu-o sobre os dois tetos que **guardam** a casa: o de
gasto e o de rede. Esses continuam na tabela versionada e não passam por aqui.

O `teto` da janela diz **quantos objetos por conta** se lê. É escopo — e escopo
é do pedido.

> **TETO QUE GUARDA A CASA != LIMITE DO QUE SE PEDIU.**

---

## OS DOIS DEFEITOS QUE ESTA MISSÃO ENCONTROU

### ⚠️ 1 · «NÃO SERVE» estava a significar «não serve se for caro»

A prova negativa da relevância (P2) **reprovou à primeira**: uma fonte com um
`NÃO` explícito no livro continuava a ser observada pela rota gratuita.

`leis/relevancia_da_fonte.py` escreve a tabela da regra por extenso —

```
NAO            -> BARRA   em todas — inclusive na rota de graça
NAO_SE_APLICA  -> BARRA   a pergunta não faz sentido para o par
```

— e publica `PODE_OBSERVAR_BARATO` exactamente para dizer isso. Só que quem
corre lia **apenas** `BLOQUEIA_A_CORRIDA`, que é `bool(gastos) and not
pode_gastar`: numa rota gratuita não há gastos abertos, logo ele é **sempre
`False`**.

A lei estava escrita, o campo estava publicado, e ninguém o lia.

> **«NÃO SERVE» NÃO É «NÃO SERVE SE FOR CARO».**

Consertado onde pertence — no **obediente**, não na lei: `Plano` ganhou
`barra_a_observacao`, e o orquestrador passou a barrar também por ele. A outra
metade da lei fica intacta: `EXIGE_AVALIACAO` numa rota gratuita **continua a
deixar observar**, porque o portão guarda o gasto (COL-LAW-018).

### ⚠️ 2 · «Não tenho navegador» chegava como `UNKNOWN_ERROR`

Sem Chrome na máquina, `cdp.subir` levanta, a exceção caía no balde genérico de
`social_rotas`, e o rasto dizia `UNKNOWN_ERROR` — o mesmo nome de um extractor
partido.

E `leis/falhas.py` **já** escrevia a família certa, com este alias lá dentro:

> `EXECUTOR_UNAVAILABLE` ← `BROWSER_NOT_REACHED` — «a nossa ferramenta não está
> lá — Chrome não subiu, ator não existe. **Nada foi medido sobre a fonte.**»

Faltava alguém dizer o nome. É a mesma forma do defeito que a FLOW-01 encontrou
na guarda do gasto, um andar ao lado:

> **UM `except Exception` LARGO NÃO DISTINGUE QUEM DISSE NÃO.**
> **E UMA FALHA NOSSA COM CARA DE DESCONHECIDA VAI PARAR À FONTE.**

---

## AS PROVAS

`provas/o_fluxo_gratuito_do_scrap.py` — **53 provas, 0 falhas**, offline.

| prova | o que exige |
|---|---|
| **P0** | a cadeia está ligada, e a escolha é a mesma em quatro ordens de lista |
| **P1 · POSITIVA** | a cadeia inteira atravessa: 1 RUN_ID, 5 unidades colhidas com a origem do artefato, RAW escrito e **relido**, ingresso, recibo, custo zero |
| **P2 · RELEVÂNCIA** | um `NÃO` no livro barra a corrida **gratuita** · **0 pedidos CDP** |
| **P3 · EXECUTOR** | o pedido de outra fase não abre este executor · **0 pedidos CDP** |
| **P4 · POLÍTICA** | rota não permitida ⇒ `ROUTE_NOT_ALLOWED` · **0 pedidos CDP** |
| **P5 · EXECUÇÃO** | sem navegador: `FAILED` com motivo, zero colheita, **ERRO e nunca REJEITADO**, e a falha diz **que** ferramenta faltou |
| **P6 · OUTPUT** | payload é **medido**, nunca afirmado; caminho declarado sem bytes é recusado |

### O mundo falso é um navegador que não existe, numa porta que existe

Um servidor local que fala **DevTools por socket real**: responde `GET /json` e
o WebSocket do CDP. `ferramentas/cdp.py` fala com ele exactamente como falaria
com o Chrome. Enquanto ele escuta, `cdp.subir()` encontra a porta ocupada e
**não abre navegador nenhum**.

```
META_REAL_REQUESTS = 0 · nenhuma página do instagram.com foi pedida.
```

E ele é o mais fundo que existe: abaixo do socket só há o Chrome.

> **UM FAKE ACIMA DO GATE MEDE O FAKE.**

E ele **regista cada pedido CDP** — é desse registo que as quatro negativas leem
«o navegador foi tocado?». A medição está na camada mais funda, e não no que o
runtime disse que fez.

Não é falso — e falsificá-lo invalidaria tudo: `pedido`, `receitas`,
`orquestrador`, `scrap_executor`, `social_rotas`, `adaptador_instagram`,
`instagram_janela`, `orcamento_de_rede`, `relevancia_da_fonte`,
`retorno_da_coleta`, `ingresso`.

### A casa fica como estava, e isso é conferido

Cinco caminhos fotografados antes e repostos depois — o `LIVRO-DE-DECISOES`, o
artefato da rota, o envelope, e as duas pastas que a rota cria (`provas/`,
`html-bruto/`). O conteúdo é comparado byte a byte no fim.

```
TEST_MUTATED_CANONICAL_BOOKS = NO
```

---

## O RED TEAM

`tests/test_scrap_flow_02.py` — **51 ataques · 18 mutantes · 0 sobreviventes**.

---

## FASE 14 · A SUÍTE QUE SUJA A ÁRVORE

O fecho anterior sinalizou «a suíte de testes suja a árvore». Esta missão
**mediu-o**, comparando `git status` antes e depois de **cada um** dos 142
testes, e repondo a árvore entre eles.

### ⚠️ A ATRIBUIÇÃO ANTERIOR ESTAVA ERRADA, E A MEDIÇÃO CORRIGE-A

```
TESTES QUE SUJAM A ARVORE  =  0  de 142
```

Nenhum teste suja. Quem suja é uma **prova**:

```
SUJA   provas/mutacao_do_portao_de_relevancia.py
       M  data/samples/LIVRO-DE-DECISOES.json
       M  data/collection-ledger/italy/observations.ndjson
       M  data/collection-ledger/italy/runs.ndjson
       ?? data/collection-store/italy/IT-T2-002/ARPAV_Z*/        (4 pastas)
```

Porquê: ela corre `provas/red_team_da_relevancia_da_fonte.py`, que chama o
**orquestrador real** por subprocesso — e o orquestrador real atravessa o
ingresso e a porta de admissão, que escrevem nos livros desta casa. Corrida
sozinha, essa prova é limpa; é a suíte de mutação que a corre 22 vezes.

No fecho da FLOW-01 isso foi atribuído aos testes da Itália porque foi ali que a
sujidade apareceu — depois de eu ter corrido **as duas coisas**.

```
    ONDE A SUJIDADE APARECE NÃO É QUEM A FEZ.
    ATRIBUIR SEM ISOLAR É ADIVINHAR COM CARA DE MEDIÇÃO.
```

```
OWNER    de quem escreveu a prova — NÃO desta missão
DIVIDA   declarada, não paga: corrigir a prova de outra missão aqui
         seria trocar de missão a meio
```

As provas **novas** desta missão não sujam — e isso é conferido byte a byte
dentro delas, não prometido. Medido também: `provas/o_fluxo_canonico_do_scrap.py`
(FLOW-01) e `provas/red_team_da_relevancia_da_fonte.py` correm limpas.

---

## O QUE ESTA MISSÃO **NÃO** FEZ

- **não** migrou uma terceira rota — as medições declaradas continuam onde estão,
  e isso está medido acima, não escondido;
- **não** avaliou fonte nenhuma, e **não** escreveu `SIM`, `NÃO` ou `NÃO SEI`
  para fonte nenhuma;
- **não** fundiu a linha paralela da FLOW-01 — a reconciliação é de quem decide;
- **não** corrigiu a prova que suja a árvore — a dívida fica nomeada, com
  caminho e dono;
- **não** executou rede real, provider, Apify, nem gastou.

```
REAL_NETWORK        = 0
META_REAL_REQUESTS  = 0
APIFY_REAL_RUNS     = 0
PAID_REAL_RUNS      = 0
REAL_COST_USD       = 0
FONTES_AVALIADAS    = 0
```

---

## O QUE FICA POR FECHAR

```
CANONICAL_ORCHESTRATION(yt-legenda-paga) = PASS   (FLOW-01)
CANONICAL_ORCHESTRATION(janela*)         = PASS   (esta missão)
CANONICAL_ORCHESTRATION(o fluxo)         = NAO    — as medições declaradas
                                                    continuam por fora, de propósito
PRODUCTION_READY(janela*)                = depende do ambiente: sem Chrome a rota
                                           recusa com nome próprio, e isso é o desenho
RECONCILIACAO_COM_A_LINHA_PARALELA       = PENDENTE
QUEM_SUJA_A_ARVORE                       = provas/mutacao_do_portao_de_relevancia.py
                                           (0 de 142 testes) — MEDIDO, NAO CORRIGIDO
```

Duas rotas, dois contratos diferentes, o mesmo caminho. O que a segunda provou
que a primeira não podia provar sozinha: **o fluxo canônico não depende de haver
uma compra.** O portão continua a ser consultado, a política continua soberana,
o teto de acessos continua dono do seu eixo — e nenhum deles precisou de um
dólar para funcionar.
