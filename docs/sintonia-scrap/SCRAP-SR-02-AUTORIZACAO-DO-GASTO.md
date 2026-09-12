# SCRAP-SR-02 — NENHUMA COMPRA SEM AUTORIZAÇÃO

```
MEDIDO_EM              = 2026-09-12
APIFY_REAL_RUNS        = 0
META_REAL_REQUESTS     = 0
OTHER_PAID_REAL_RUNS   = 0
REAL_PROVIDER_START_POSTS = 0
COST_USD               = 0
FONTES AVALIADAS       = 0
```

> **EVIDÊNCIA DE MISSÃO, NÃO BÍBLIA.** Não avalia fontes, não classifica
> relevância, não decide o que serve. `SOURCE_RELEVANCE` continua a pertencer ao
> dono externo — esta missão apenas faz o dinheiro **obedecer** à decisão dele.

**O que mudou, numa frase:**

```
A COMPRA PASSOU A EXIGIR UMA AUTORIZAÇÃO QUE SE POSSA LER — E A TRAVA FICOU NO
ÚNICO SÍTIO DO REPOSITÓRIO ONDE UMA COMPRA NASCE.
```

---

## C · TOPOLOGIA — O CENSO REFEITO DO ZERO

Nenhum número foi herdado. Varridas todas as formas de iniciar execução paga:
`urlopen`, `requests`, `curl` por subprocess, `http.client`, `aiohttp`, `httpx`,
SDK, wrappers, scripts antigos, workflows.

```
NETWORK_ENTRYPOINTS        urlopen 56 · curl-subprocess 6 · http.client 2
                           aiohttp 5 · httpx 6 · requests 0
PAID_ENTRYPOINTS           7 módulos de produção chamam a porta da compra
PAID_CREATION_PRIMITIVES   1
PAID_WORKFLOWS             1  (`scrap-social.yml`, fase `yt-legenda-paga`)
```

### A primitiva, nomeada

```
coleta/coletor.py:executar  →  _curl('%s/acts/%s/runs?%s', metodo='POST')
```

Confirmado por varredura: `metodo='POST'` aparece **uma única vez** em todo o
código de produção.

### E quem NÃO compra, apesar de falar com a Apify

| ficheiro | o que faz |
|---|---|
| `superficie/rede.py` | `GET` de diagnóstico |
| `coleta/comunicacao_coleta.py` | cita o endpoint em prosa; compra pelo `coletor` |
| `ferramentas/apify_pool.py` | token, pool, rotação, redação — **zero** compras |
| `provas/corrigir_custo.py` | `GET /actor-runs` para ler custo |

```
UMA PORTA ÚNICA É A MELHOR NOTÍCIA POSSÍVEL PARA QUEM VAI PÔR UMA TRAVA.
Copiar a lei para os sete chamadores daria SETE LEIS, e a oitava porta
nasceria sem nenhuma.
```

---

## D · OS OWNERS, MEDIDOS

```
SOURCE_RELEVANCE_OWNER = leis/relevancia_da_fonte.py      (externo · SR-01)
TOKEN_OWNER            = ferramentas/apify_pool.py
PAID_EXECUTION_OWNER   = coleta/coletor.py:executar
PAID_POST_OWNER        = coleta/coletor.py:executar
FINANCIAL_BUDGET_OWNER = coleta/coletor.py
NETWORK_BUDGET_OWNER   = coleta/scrap_http.py
SPEND_GUARD_OWNER      = leis/autorizacao_de_gasto.py     (nasce nesta missão)

COLETOR_IS_ACTUAL_SINGLE_PAID_OWNER = YES
APIFY_POOL_IS_ACTUAL_PAID_OWNER     = NO
PAID_OWNER_SPLIT                    = NO para o POST · SIM para os orçamentos
                                      (financeiro no `coletor`, rede no `scrap_http`)
```

```
TER A CHAVE NÃO É TER LICENÇA.   TOKEN_OWNER != SPEND_OWNER.
```

---

## E · ANTES

```
CAN_SPEND_WITHOUT_AUTH = 7 módulos de produção + 2 provas

`coletor.executar` não tinha parâmetro nenhum de autorização de fonte.
Medido por inspeção da assinatura: quem a alcançasse, comprava.
```

## F · DEPOIS

```
CAN_SPEND_WITHOUT_AUTH = 0
```

Não por migração dos sete: pela **trava na porta única**. Chamar `executar` sem
`autorizacao=` levanta `GastoNaoAutorizado` antes de qualquer outra coisa.

E a sentinela não é `None`:

```
ESQUECER NÃO É O MESMO QUE DECLARAR QUE NÃO HÁ.
`None` seria um valor que alguém passa por engano e que se leria como uma
declaração. A sentinela só aparece quando o parâmetro NÃO FOI DADO.
```

---

## G · COLHEITA NORMAL — OS SETE CASOS

A guarda **não julga**: pergunta ao `portao()` do SR-01 e obedece.

| caso | veredito | compra? |
|---|---|---|
| `SIM` A/T3 + pedido A/T3 | `AUTORIZADO` | **sim** |
| `SIM` A/T3 + pedido **B**/T3 | `AUTORIZACAO_INVALIDA` | não |
| `SIM` A/T3 + pedido A/**T9** | `AUTORIZACAO_INVALIDA` | não |
| `NAO` | `BARRADO_PELA_RELEVANCIA` | não |
| `NAO_SEI` | `EXIGE_AVALIACAO_DA_FONTE` | não |
| `ERRO` | `EXIGE_AVALIACAO_DA_FONTE` | não |
| `NAO_AVALIADA` | `EXIGE_AVALIACAO_DA_FONTE` | não |
| `SOURCE_ID` ausente | `AUTORIZACAO_INVALIDA` | não |
| URL no lugar de `SOURCE_ID` | `AUTORIZACAO_INVALIDA` | não |

```
AUTORIZAÇÃO NÃO É UM CARIMBO: É UM PAR (FONTE, PROPÓSITO).
```

E as recusas não se colapsam:

```
SEM_AUTORIZAÇÃO          falta nossa
BARRADO_PELA_RELEVÂNCIA  decisão sobre o mundo
EXIGE_AVALIAÇÃO          confissão: ninguém olhou
```

---

## H · SOURCE EVALUATION PROBE

```
SUPPORTED      = SIM
HUMAN_AUTH     = obrigatória
MAX_RUNS · MAX_POSTS · MAX_USD · MAX_ITEMS = os quatro, obrigatórios
STOP_CONDITION = obrigatória
AUTO_PROMOTION = NO
```

Existe para o caso em que o dono **ainda não decidiu** — logo não pode exigir a
decisão. O que exige em troca são tectos e mão humana.

```
UM TECTO PELA METADE É UM TECTO QUE NÃO EXISTE.
E `MAX_USD = 0` não é um tecto generoso: é uma proibição escrita com o
vocabulário de um limite.
```

```
PROBE != DECISION — quem mede não escreve no livro. Provado: o livro não muda.
```

## I · CAPABILITY TRIAL

```
SUPPORTED                    = SIM
EXISTING_TRIAL_REUSED        = SIM — `scrap_executor.TRIAL` continua o dono do modo
HUMAN_AUTH                   = obrigatória
ALVO FIXO                    = obrigatório
NORMAL_CAN_BYPASS_WITH_TRIAL = NO
```

A porta que não pode abrir:

```
SE A EXECUÇÃO NOMEIA A FONTE, NÃO É ENSAIO DE CAPACIDADE — É COLHEITA.
```

Provado nos dois sentidos: com uma fonte que tem `NAO` no livro, e com uma que
tem `SIM`. As duas são recusadas — porque o que se recusa é a **troca de porta**,
não a fonte.

---

## J · A ORDEM DOS PORTÕES, DERIVADA DOS OWNERS

Não aceite deste prompt: derivada de quem é dono de quê, e provada **no código**
por posição relativa.

```
1  AUTORIZAÇÃO DO GASTO      leis/autorizacao_de_gasto.py   ← nasce aqui
2  POLÍTICA DE ROTA           leis/social_matriz.py
3  TRAVA DA SESSÃO            guarda/social_sessao.py
4  TRAVA DO GASTO (motivo)    coleta/social_rotas.py
5  TRAVA DA CREDENCIAL        a sonda do adaptador
6  RESERVA FINANCEIRA         coleta/coletor.py
7  ORÇAMENTO DE REDE          coleta/scrap_http.py
8  POST DE CRIAÇÃO            coleta/coletor.py
```

Duas leis de ordem, e as duas foram pagas para se aprender:

```
UMA RECUSA DE GASTO NÃO PRECISA DE ORÇAMENTO PARA ACONTECER.
  → a autorização corre ANTES da reserva. Reservar já é dispor: o saldo fica
    comprometido e o próximo pedido legítimo encontra menos do que havia.

NÃO SE BATE À PORTA DE QUEM NÃO SE TEM CHAVE.
  → a credencial corre ANTES da rede (herdado da missão anterior).

E RECUSAR GASTAR NÃO DEPENDE DO AMBIENTE, ENQUANTO FALTAR A CHAVE DEPENDE.
  → por isso a trava do gasto fala ANTES da trava da credencial.
```

---

## K · META NÃO REGREDIU

```
CREDENTIAL_MISSING_STATE = CREDENTIAL_MISSING   (não `ROUTE_NOT_ALLOWED`)
NETWORK_ATTEMPTS         = 0
ALLOWED != READY         = preservado · `ZERO_DOLLAR_BUT_CREDENTIAL_GATED`
FONTE DA CREDENCIAL      = a sonda do adaptador, não a declaração da matriz
```

---

## L · ENTRYPOINTS E WORKFLOWS

| entrypoint | antes | depois | como |
|---|---|---|---|
| `regras/sensor_coleta.py` | podia | **não** | trava na porta única |
| `coleta/comunicacao_coleta.py` | podia | **não** | idem |
| `coleta/instagram_coleta.py` | podia | **não** | idem |
| `coleta/scrap_executor.py` | podia | **não** | idem |
| `coleta/social_scrap.py` (CLI) | podia | **não** | **traduz** a tabela `FASES_PAGAS` |
| `coleta/adaptador_youtube.py` | podia | **não** | **passa** a autorização recebida |
| `provas/*` | podia | **não** | autorização de ensaio declarada |

```
WORKFLOWS QUE NOMEIAM UM ACTOR PAGO = 0
WORKFLOWS QUE PODEM GASTAR SEM GUARDA = 0
```

A CLI não inventa autorização — **traduz** a declaração versionada que já
existia, agora com os quatro tectos ao lado da autorização humana.

```
TRADUZIR UMA DECLARAÇÃO EXISTENTE NÃO É FABRICAR UMA.
QUEM GASTA NÃO ASSINA A PRÓPRIA AUTORIZAÇÃO.
```

---

## M · PROVA

```
ATAQUES   = 45
RESULT    = PASS
MUTANTES  = 20
SURVIVORS = 0

TESTS_BEFORE = 139 · FAILURES_BEFORE = 15
TESTS_AFTER  = 140 · FAILURES_AFTER  = 15
NEW_FAILURES = 0   (as mesmas quinze, por identidade de teste)
```

### As três provas que quebraram, e por que nenhuma foi enfraquecida

`C10.8A-F`, `C10.8B` e `C10.8B-LIVE` passaram a falhar no instante em que a
trava entrou — porque compravam sem autorização, **que era exactamente o
defeito**.

A saída fácil era afrouxar a trava. A certa foi reconhecer o que elas são —
ensaios de capacidade, com actor falso, alvo fixo e transporte falso — e dar-lhes
a autorização que a lei desenhou para esse caso.

```
UMA PROVA QUE PRECISA DO DEFEITO PARA PASSAR É UMA PROVA DO DEFEITO.
```

### E um defeito da minha própria prova, corrigido

A varredura que conta as primitivas de compra contava também as ocorrências
dentro das próprias provas — que são strings de asserção.

```
UMA PROVA QUE SE CONTA A SI PRÓPRIA MEDE-SE, NÃO MEDE O SISTEMA.
```

---

## N · O QUE NÃO MUDOU

```
· nenhuma fonte foi avaliada · nenhuma decisão de relevância foi tomada aqui
· o livro da relevância não foi escrito — as provas usam livro em memória
· network budget · financial budget · `maxTotalChargeUsd` · um POST só
· `PostTalvezCriado` · exposição UNKNOWN · sem retry pago
· RAW antes da normalização · trace do provider · transporte de evidência
· Admission, Intelligence, Portal e Collection global: intocados
```

A autorização é uma **trava adicional**. Não substitui nenhuma das outras.

## O · O QUE CONTINUA DESCONHECIDO

```
· quantos dos sete chamadores vão passar a pedir autorização de verdade, e
  quando — a trava fecha a porta, não migra os caminhos
· se algum caminho antigo ainda produz uma compra por uma via não medida:
  a varredura cobriu as formas conhecidas, e uma forma desconhecida é,
  por definição, o que uma varredura não encontra
· o custo real histórico por fonte — continua fora do alcance desta missão
```

## P · RISCO RESTANTE

**1 · Dinheiro protegido não é fluxo canónico.**

```
SPEND_ENFORCEMENT = PASS   NÃO É   CANONICAL_ORCHESTRATION = PASS.
```

Continuam a existir caminhos antigos que não passam pelo orquestrador. Eles já
não compram sem autorização — mas isso é uma frase sobre o dinheiro, não sobre a
arquitectura. Declarar o segundo porque se conseguiu o primeiro seria trocar a
pergunta pela que já tem resposta.

**2 · A guarda depende de quem a chama passar o par verdadeiro.**
`source_id_pedido` e `proposito_pedido` são o que a execução declara fazer. Um
chamador que minta sobre eles engana a guarda. A trava mede o que lhe dizem — e
é por isso que a autorização vive numa tabela versionada, e não no pedido.

**3 · Duas colisões de numeração de `§` em duas missões seguidas.** O git junta
por posição de texto; a colisão é de significado e passa calada. Não há hoje
nada que a detecte automaticamente.

---

## Q · VEREDITOS

```
SCRAP_PAID_SPEND_ENFORCEMENT = PASS
MISSION_PROTOCOL             = PASS_ZERO_REAL_NETWORK

CAN_SPEND_WITHOUT_AUTH  antes = 7 módulos + 2 provas
                        depois = 0
ATAQUES 45 · MUTANTES 20 · SURVIVORS 0 · NEW_FAILURES 0
APIFY_REAL_RUNS 0 · META_REAL_REQUESTS 0 · REAL_START_POSTS 0 · COST_USD 0
```

**HARD STOP.**
