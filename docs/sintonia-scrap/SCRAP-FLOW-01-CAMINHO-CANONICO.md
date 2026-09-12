# SCRAP-FLOW-01 — o caminho é canônico, e não só o dinheiro é guardado

> ```
> MODULE CAN'T SPEND  !=  FLOW IS CANONICAL.
> ```

A SCRAP-SR-02 fechou a porta do dinheiro: nenhuma compra nasce sem autorização
que se possa ler. Ela não fechou o **caminho**. No fim daquela missão ficou
escrito, com estas palavras:

> «proteger o dinheiro não é fechar o fluxo. Os caminhos antigos continuam a
> saltar o orquestrador; eles apenas já não conseguem comprar.
> `SPEND_ENFORCEMENT = PASS` não é `CANONICAL_ORCHESTRATION = PASS`.»

Esta missão fechou **um** desses caminhos. Um só, de propósito.

---

## O QUE FOI MEDIDO ANTES DE SE DECIDIR QUALQUER COISA

```
CURRENT_BRANCH              claude/wonderful-hamilton-m50ahv
CURRENT_HEAD                3d4dd165cddd60c7377b8aeb054dfb347e9d79c7
REMOTE_HEAD                 3d4dd165cddd60c7377b8aeb054dfb347e9d79c7   (igual)
WORKTREE                    limpo · um só worktree
SPEND_AUTH_PRESENT          SIM   leis/autorizacao_de_gasto.py::exigir
FINANCIAL_BUDGET_PRESENT    SIM   coleta/coletor.py::orcamento_financeiro
NETWORK_BUDGET_PRESENT      SIM   coleta/scrap_http.py::orcamento_de_rede
SOURCE_RELEVANCE_PRESENT    SIM   leis/relevancia_da_fonte.py::portao
PAID_EXECUTION_GUARD        SIM   coleta/coletor.py::executar  (a porta única)
CONVERGENCIA                PRESENTE — os cinco na MESMA linha técnica
```

Linha de base dos testes, medida **antes** de tocar em código, com a invocação
que `docs/operacao/ESTADO-DA-FUNDACAO-DA-COLETA.md` declara:

```
TESTES = 140 · FALHAS PRE-EXISTENTES = 17
```

---

## O CENSO DO DESVIO — QUEM ADQUIRE SEM PASSAR PELO ORQUESTRADOR

O repositório já tinha metade deste censo escrito, e honesto:
`social_scrap.FASES_QUE_NAO_ATRAVESSAM_O_BOUNDARY` nomeia as quatro fases que
não chegam a `scrap_executor.COLLECT`. Mas esse é o boundary **de baixo**.

O boundary desta missão é o de cima. E aí a conta é outra: das fases que o
`sintonia-scrap.yml` despacha, **as que adquirem e chegam ao `COLLECT`
continuavam todas a saltar o orquestrador**:

| fase | chega ao `COLLECT`? | passa pelo orquestrador? | custa? |
|---|---|---|---|
| `janela` · `janela-perfis` · `janela-objetos` | SIM | **NÃO** | grátis |
| `yt-legenda-paga` | SIM | **NÃO** | **PAGO** |
| `diario` · `yt-canais` · `yt-objetos` · `yt-legendas` · `yt-alvos` · `yt-transcrever` · `bio` · `posts` · `reels` · `comentarios` | recusadas no disparador | — | — |

`ATRAVESSA O SCRAP` não é `ATRAVESSA A CASA`. Uma fase podia ter portão de
rota, teto de rede, teto de gasto e guarda de compra — e mesmo assim nascer sem
pedido, sem plano, sem portão de relevância da fonte, sem corrida cunhada antes
do facto, sem recibo, sem ingresso e sem admissão.

---

## O CAMINHO ESCOLHIDO — UM SÓ, E PORQUÊ ESTE

```
ESCOLHIDO = yt-legenda-paga
```

É a **única** rota paga desta casa com capacidade declarada, rota declarada e
autorização humana escrita (C10.8B-LIVE). É o único sítio onde os cinco donos
se encontram ao mesmo tempo — e portanto o único onde as três recusas
(autorização, rede, dinheiro) se podem provar **sem serem vácuo**.

As fases `janela*` foram medidas e **não** foram escolhidas: sendo gratuitas,
duas das três provas negativas nasceriam vazias nelas.

### Antes

```
sintonia-scrap.yml  ──►  coleta/social_scrap.py coletar yt-legenda-paga
                    ──►  scrap_executor.COLLECT
```

### Depois

```
sintonia-scrap.yml            ENTRYPOINT
  └─► orquestrador.py "colete concorrentes" --filtro fase=yt-legenda-paga
        └─► pedido.Pedido                                       REQUEST
              └─► receitas.resolver → Plano                     ORCHESTRATOR
                    · receitas.escolher  — QUAL executor
                    · relevancia_da_fonte.portao — antes de qualquer gasto
                    · novo_run_id — a corrida nasce ANTES de correr
              └─► subprocess: social_scrap.py coletar yt-legenda-paga --run-id=…
                    └─► scrap_executor.COLLECT                  SCRAP EXECUTOR
                          · orcamento_de_rede · orcamento_financeiro
                          · social_rotas → adaptador → coletor.executar
                                · autorizacao_de_gasto.exigir
              └─► RETORNO.json declarado pela corrida           COL-LAW-505
              └─► a_colheita → ingresso → admissão → recibo
```

---

## O QUE MUDOU NO CÓDIGO, E PORQUÊ

### 1 · A escolha do executor passou a ter dono

`leis/gestao_da_coleta.py` escreve, desde que existe:

```
ORQUESTRADOR_DECIDE = ('COMO', 'QUAL_ROTA', 'QUAL_EXECUTOR')
```

E durante todo esse tempo `QUAL_EXECUTOR` **não era uma decisão: era o índice
zero.** `receitas.resolver` perguntava a relevância sobre `execs[0]`, e
`orquestrador.correr` corria `executores[0]` — duas linhas, em dois ficheiros,
a decidir a mesma coisa por acidente. O próprio registo de T9 documentava a
consequência: «um segundo registo em T9 nunca seria aberto e ficaria a mentir
nesta lista».

> **UMA LEI QUE SE CUMPRE PORQUE SÓ HÁ UM CANDIDATO NÃO ESTÁ A SER CUMPRIDA.**

`receitas.escolher(execs, p)` é agora o dono único. Duas linhas, sem exceções:

1. o **primeiro** executor cujo `pedido_pede` casa com os filtros do pedido;
2. senão, o primeiro que **não** declara `pedido_pede`.

Um executor com `pedido_pede` **nunca** é escolhido por omissão — se pudesse,
acrescentar uma linha nova mudava calado o caminho de todos os pedidos que já
existiam.

> **QUEM PEDE NOMEIA. QUEM NÃO NOMEIA LEVA O DE SEMPRE.**

E o portão passou a julgar **o executor que vai correr**. Enquanto era
`execs[0]`, bastava um segundo registo no alvo para o portão julgar um executor
e a corrida correr outro.

> **JULGAR UM E CORRER OUTRO É PIOR DO QUE NÃO JULGAR NADA.**

### 2 · Aceitar uma fonte deixou de se deduzir da linha de comando

`fonte_nomeada` decidia se havia par (fonte, propósito) para julgar olhando
para `argumentos_de_filtros`. A dedução valia por acidente: o único executor
que aceitava fonte também a passava como argumento posicional.

> **QUEM O PORTÃO JULGA != O QUE A LINHA DE COMANDO LEVA.**

Passou a ser uma declaração: `aceita_fonte`. O T2, que já aceitava fonte,
declara-a — e o comportamento dele não muda.

### 3 · O livro de relevância passou a ser uma ENTRADA que se diz

`resolver(p, *, livro=None)` e `correr(p, ..., livro=None)`. `None` continua a
ser «lê o livro desta casa», que é o que a produção faz.

> **UMA ENTRADA QUE SÓ SE LÊ DO DISCO OBRIGA A PROVA A ESCREVER NO DISCO.**

A regra continua onde sempre esteve. Dar a entrada ao dono da lei não é decidir
por ele.

### 4 · A corrida é uma só, do princípio ao fim

`coletar` já sabia receber `run_id`, e **nada lho passava**: a CLI cunhava um
por execução. Enquanto o único chamador era o workflow, isso era honesto. Com o
orquestrador a chamar, deixou de ser.

> **PROVENIÊNCIA É PROSPECTIVA. Duas corridas para um facto só não é
> redundância: é perder o facto.**

`main()` lê `--run-id` como **opção**, e os argumentos posicionais deixaram de
ver as opções longas — antes, um `--run-id=X` entrava em `args[2]` e era lido
como TETO.

### 5 · A corrida declara o que produziu

`social_scrap._declarar_o_retorno` escreve `data/colheita/scrap/RETORNO.json`.
Sem isto, o executor largava ficheiros e ninguém ia buscar.

> **LARGAR NÃO É ENTREGAR. SÓ COLHEITA DECLARADA ATRAVESSA.** (COL-LAW-505)

O estado do payload **não é afirmado: é medido** por
`retorno_da_coleta.estado_do_payload`. E o `SOURCE_ID` de cada unidade é o que
o registo desta fase já declarava — `SCRAP-YOUTUBE/<fase>` — e **não** é
nenhuma das 77 fontes em ficha.

---

## O DEFEITO QUE ESTA MISSÃO ENCONTROU AO PROVAR A NEGATIVA

A prova negativa da autorização passou à primeira na parte que conta — **zero
POST saiu** — e reprovou na outra: a recusa chegava ao rasto como
`UNKNOWN_ERROR`.

```
resultado   UNKNOWN_ERROR
FINANCIAL_CALLS_REFUSED    0
COST_STATE                 NOT_RUN
```

Exactamente o mesmo que um extrator partido, um `TypeError` desta casa ou um
adaptador a rebentar. E a casa já tinha escrito a lei, duas vezes:

> **UM `except Exception` LARGO NÃO DISTINGUE QUEM DISSE NÃO.**

e, dentro da própria família `BUDGET_EXHAUSTED` de `leis/falhas.py`, sobre os
dois tetos: «sem alias eles caíam em `UNKNOWN_ERROR`, que é o balde de "ninguém
sabe o que houve"».

A guarda da SCRAP-SR-02 estava fora dessa lista. Consertado:

- `leis/falhas.py` — `SPEND_NOT_AUTHORIZED` entra na família `BUDGET_EXHAUSTED`,
  cuja descrição **já dizia** «ou a missão não autorizou pagar»;
- `coleta/social_rotas.py` — a recusa da compra é apanhada **antes** do balde
  genérico, e o **veredito inteiro** sobe no registo;
- `coleta/social_scrap.py` — a CLI imprime qual dos donos disse não.
  `leis/falhas.py` tem vocabulário fechado e `selar()` guarda o nome exacto em
  `ESTADO_ORIGINAL` — e durante todo esse tempo esse nome não era impresso por
  lado nenhum. Num runner, a saída **é** o registo.

> **COLAPSAR OS TRÊS DONOS NUMA FAMÍLIA FAZ O RASTO MENTIR SOBRE QUAL DELES
> PAROU A EXECUÇÃO.**

---

## ⚠️ O QUE A MIGRAÇÃO CUSTOU, DITO SEM ARREDONDAR

```
ESTADO DE PRODUCAO DA FASE `yt-legenda-paga` APOS A MIGRACAO
  = BARRADO_NA_RELEVANCIA  (codigo de saida 3 · nada corre · nada custa)
```

O alvo sentinela desta fase é o vídeo `EAkcA_2FDN8`, do canal **Coldiretti
Emilia Romagna**. Esse canal **não tem ficha nenhuma nas 77 fontes desta casa**.
Com rota paga e sem fonte nomeada, `leis/relevancia_da_fonte.py` responde
`EXIGE_AVALIACAO`, e o orquestrador responde `BARRADO_NA_RELEVANCIA`.

Isto **não foi contornado**, e havia duas formas fáceis de o contornar — ambas
recusadas:

- escrever um `source_id` no registo do executor para o portão ter o que julgar
  → seria **fabricar procedência**: o portão julgaria uma fonte que esta rota
  não visita;
- escrever um veredito no livro de relevância → esta missão **não avalia
  fontes**, e não escreveu `SIM`, `NÃO` nem `NÃO SEI` para fonte nenhuma.

> **O FLUXO CANÔNICO NÃO PARTIU ESTA FASE. ELE FEZ-LHE A PERGUNTA QUE O DESVIO
> NÃO FAZIA.**

Para ela voltar a correr falta uma decisão humana que não é desta missão:
**levantar a ficha da fonte e avaliar a relevância dela**. Até lá, o disparador
diz isso em voz alta em vez de comprar em silêncio.

---

## AS PROVAS

`provas/o_fluxo_canonico_do_scrap.py` — 27 provas, cadeia inteira, offline.

| prova | o que exige |
|---|---|
| **P0** | a cadeia está ligada: o pedido escolhe, o portão julga quem corre |
| **P1 · POSITIVA · MUNDO FALSO** | a cadeia inteira atravessa: 1 POST, corrida única, envelope declarado, colheita encontrada, ingresso |
| **P2 · NEGATIVA · AUTORIZAÇÃO** | sem autorização: **zero POST**, `SPEND_NOT_AUTHORIZED` |
| **P3 · NEGATIVA · ORÇAMENTO DE REDE** | teto de rede a zero: **zero POST**, `NETWORK_BUDGET_EXHAUSTED` |
| **P4 · NEGATIVA · ORÇAMENTO FINANCEIRO** | teto de gasto a zero: **zero POST**, `FINANCIAL_BUDGET_EXHAUSTED` |

### O que é falso, e o que não pode ser

Falso — **só o mundo lá fora**, e nada disto é nosso:

- **`curl`** — um binário falso à frente no `PATH`. É o cliente HTTP que o
  `coletor` usa para falar com a Apify. Nenhum pacote sai da máquina, e cada
  invocação fica escrita num ficheiro que a prova **lê** para contar os POST.
- **`APIFY_TOKEN_POOL`** — uma chave obviamente falsa, para um provider falso.
- **o livro de relevância** — um livro de fixture, com **uma fonte obviamente
  falsa** (`fake~fonte-da-prova`), montado pelo próprio dono da lei
  (`rel.Decisao`) e nunca à mão.

> **UM FAKE ACIMA DO GATE MEDE O FAKE.** Por isso o fake é o `curl`: mais fundo
> do que ele só existe o socket, e o socket é que não queremos abrir.

Não é falso — e falsificá-lo invalidaria a prova inteira: `pedido`, `receitas`,
`orquestrador`, `scrap_executor`, `social_rotas`, `coletor`,
`autorizacao_de_gasto`, `orcamento_de_rede`, `orcamento_financeiro`,
`retorno_da_coleta`, `ingresso`.

### A casa fica como estava — e isso é medido

Na primeira volta, a prova positiva escreveu **três decisões falsas** no
`LIVRO-DE-DECISOES.json` desta casa e reescreveu o registo da corrida paga REAL
da C10.8B-LIVE. A cadeia inteira inclui o ingresso e a porta de admissão — e uma
prova que atravessa a cadeia inteira escreve onde a cadeia inteira escreve.

> **UMA PROVA QUE DEIXA OBSERVAÇÃO FALSA NO LIVRO DA CASA NÃO PROVOU A CASA:
> CONTAMINOU-A.**

Os três ficheiros são fotografados antes, repostos depois, e conferidos byte a
byte no fim — e o bruto que a compra falsa gravou é apagado, mesmo estando
ignorado pelo `.gitignore`, que é exactamente o que o faria passar despercebido
para sempre.

---

## O RED TEAM

`tests/test_scrap_flow_01.py` — **42 ataques · 16 mutantes · 0 sobreviventes**.

Os três mutantes de COMPORTAMENTO (autorização, rede, dinheiro) correm em
`provas/o_fluxo_canonico_do_scrap.py`: alteram o ficheiro real, correm a cadeia
real, contam os POST no `curl` falso, restauram e conferem o sha256. Não se
repetem no teste.

> **DOIS SÍTIOS COM A MESMA PROVA SÃO DUAS PROVAS QUE PODEM DIVERGIR.**

---

## O QUE ESTA MISSÃO **NÃO** FEZ

- **não** migrou os outros caminhos — `janela*` continua a saltar o orquestrador,
  e isso está medido acima, não escondido;
- **não** avaliou fonte nenhuma, e **não** escreveu `SIM`, `NÃO` ou `NÃO SEI`
  para fonte nenhuma;
- **não** executou provider real, **não** correu a C10.8B outra vez, **não**
  gastou;
- **não** tocou em Admission, Intelligence nem Portal.

```
REAL_NETWORK        = 0
APIFY_REAL_RUNS     = 0
PAID_REAL_RUNS      = 0
META_REAL_REQUESTS  = 0
REAL_COST_USD       = 0
FONTES_AVALIADAS    = 0
```

---

## O QUE FICA POR FECHAR, E É DE QUEM DECIDE

```
CANONICAL_ORCHESTRATION(yt-legenda-paga) = PASS
CANONICAL_ORCHESTRATION(janela*)         = NAO  — continua a saltar
PRODUCTION_READY(yt-legenda-paga)        = NAO  — BARRADO_NA_RELEVANCIA
BLOQUEADO_POR                            = a fonte do alvo sentinela nao tem ficha
```

Fechar um caminho não é fechar o fluxo. O que mudou é que agora **há um caminho
canônico provado ponta a ponta**, e o próximo custa menos do que este — a
escolha do executor, o livro como entrada e o envelope declarado já estão
feitos, e servem qualquer fase que venha a seguir.
