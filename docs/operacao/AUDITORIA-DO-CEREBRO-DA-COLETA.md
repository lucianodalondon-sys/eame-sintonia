# AUDITORIA DO CÉREBRO DA COLETA

> Etapa 2. Medido em 07/09/2026. **Nenhuma fusão funcional foi feita** — esta
> etapa mede e propõe. O que está marcado `PROPOSED` **não existe** no código.

---

## A — MATRIZ DE RESPONSABILIDADES

Medida lendo o código, com comentários removidos para não contar prosa.

| responsabilidade | BOTÕES | PEDIDO | RECEITA | ORQUESTRADOR | SCRAP | APIFY | NAVEGADOR |
|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| recebe a intenção | **X** | | | | **X** | | |
| representa a intenção | | **X** | | | | | |
| valida a entrada | | **X** | | **X** | | | **X** |
| escolhe fontes | | | **X** | | | | |
| escolhe executor | | | **X** | **X** | **X** | | |
| escolhe rota | | | **X** | | **X** | | **X** |
| decide custo | | | **X** | **X** | **X** | **X** | |
| chama subprocesso | **X** | | | **X** | **X** | | **X** |
| acessa a rede | | | | | | | **X** |
| usa Apify | **X** | | | | **X** | **X** | |
| usa navegador | | | | | **X** | | **X** |
| transcreve | | | | | **X** | | |
| grava ficheiro | | | | **X** | | | **X** |
| assina o recibo | | | | **X** | | | |
| leva à admissão | | | | **X** | | | |

### O que a matriz mostra

**Três colunas decidem "escolhe executor": RECEITA, ORQUESTRADOR e SCRAP.**
É a mesma pergunta — *como atender este pedido?* — respondida em três lugares.

**Quatro colunas decidem custo.** Nenhuma delas obriga a rota grátis primeiro.

---

## B — OS BOTÕES: o que cada um chama hoje

| botão | chama orquestrador | executores | ferramentas | regras |
|---|:--:|--:|--:|--:|
| `sintonia-scrap.yml` | **NÃO** | **6** | **4** | 0 |
| `comunicacao-publica.yml` | SIM | 3 | 1 | 1 |
| `apify-sensores.yml` | **NÃO** | 0 | **1** | 1 |
| `apify-conexao.yml` | **NÃO** | 0 | **1** | 0 |

**Três dos quatro não passam pelo orquestrador.** Dois chamam a Apify pelo nome —
e escolher a ferramenta não é trabalho de um botão.

`comunicacao-publica` já pede ao orquestrador (migrado na etapa anterior), mas
ainda chama três executores diretamente nos passos seguintes.

---

## C — PEDIDO: contrato, não motor

**`CONTROL_CONTRACT`.** Medido: não acessa a rede, não grava ficheiro, não chama
subprocesso. Só valida e traduz. Consumido por: orquestrador, receita, provas.

Não deve ser removido — mas **não precisa de ser uma estação grande** no mapa
principal. Ele é a forma do pedido, não uma etapa que o dado atravessa.

---

## D — RECEITA: política interna do orquestrador

**`KEEP_INTERNAL`.** Medido: escolhe fontes, executor e rota. Não executa nada —
sem rede, sem escrita, sem subprocesso.

**Quem a consome: só o orquestrador** (e as provas). Nenhum outro consumidor.

Uma responsabilidade que tem **um único dono** e não executa nada é política
interna desse dono. O módulo pode ficar separado — a separação de código é boa.
O que não se justifica é ser uma estação no mapa principal.

---

## E — ORQUESTRADOR: o dono legítimo

Responsabilidades medidas: `RECEBE_PEDIDO` · `RESOLVE_PLANO` ·
`ESCOLHE_EXECUTOR` · `CHAMA_EXECUTOR` · `ASSINA_RUN_MANIFEST` ·
`LOCALIZA_COLHEITA` · `LEVA_PARA_ADMISSAO` · `TRATA_ERRO`.

**`KEEP_TOP_LEVEL`.** É o único que fecha o caminho do pedido até a porta.

Mas hoje **quase ninguém o chama**: um workflow e um coletor.

---

## F — SINTONIA SCRAP: `COMPOSITE_EXECUTOR`

Não é um segundo orquestrador, e a razão é medida:

- oferece **24 fases**, e **a pessoa escolhe** qual — a estratégia é decidida
  fora da máquina;
- as condições `if:` abrem **portões** (checa o navegador nas fases de navegador,
  faz o censo do pool nas fases pagas) — isso é **guarda**, não escolha de rota;
- depois despacha para o script daquela fase.

| responsabilidade | tem? |
|---|:--:|
| TRIGGER | **X** |
| EXECUTION | **X** |
| BROWSER · APIFY · TRANSCRIPTION · INSTAGRAM · YOUTUBE | **X** |
| COST_POLICY | **X** (censo do pool antes das fases pagas) |
| PLAN · ROUTE_SELECTION | — *(a pessoa escolhe a fase)* |
| FREE_FIRST_POLICY | **só no texto do cabeçalho** |

**A ressalva honesta:** escolher entre 24 fases *é* escolher estratégia. Ela não
desapareceu — foi para fora do sistema, para a cabeça de quem clica. Isso não
aparece em nenhum lugar do mapa.

---

## G — APIFY: 25 ficheiros a usam, nenhum tenta a rota grátis antes

| | |
|---|---:|
| ficheiros que usam a Apify | **25** |
| que documentam «grátis primeiro» | 2 |
| que **impõem** «grátis primeiro» em código | **0** |

Procurei a política nos quatro sítios onde ela faria sentido —
`apify_pool.py`, `sintonia-scrap.yml`, `receitas.py`, `orquestrador.py`.
Está **em texto** num deles e **em código em nenhum**.

> A intenção do produto é *«Apify é o último recurso»*. Medido: não há uma linha
> de código que a faça valer. Uma política que só existe em comentário é uma
> intenção, não uma regra — e a fatura não lê comentários.

---

## H — NAVEGADOR: existe de verdade; a rota assistida, não

`ferramentas/navegador.py` e `ferramentas/cdp.py` são automação real (631 linhas,
Chrome/CDP). São **rota canónica**.

**Coleta assistida por Claude/navegador humano: não existe integrada.** Procurei
uma porta de devolução no código e não há nenhuma — os resultados da busca são
prosa dentro de ficheiros de dado, não integração.

Classificação: `ASSISTED_MANUAL_ROUTE` — **não desenhar como automação**.
A porta correta para devolver material recolhido à mão já existe e é
`candidatas/` (fonte nova) seguida do `larga_em` do executor.

---

## I — REDUNDÂNCIAS, por prioridade

| # | o que | onde | gravidade |
|---|---|---|---|
| 1 | «como atender este pedido» decidido em **3 lugares** | RECEITA · ORQUESTRADOR · SCRAP | alta |
| 2 | «que ferramenta usar» decidido pelo **botão** | apify-conexao · apify-sensores | alta |
| 3 | **4 pontos de entrada** para a mesma intenção «colher Instagram» | scrap · orquestrador · instagram_coleta · botão | alta |
| 4 | política de custo em **4 peças**, imposta em nenhuma | receita · orq · scrap · apify | média |
| 5 | módulo interno como estação de topo | PEDIDO · RECEITA | baixa *(só visual)* |

---

## J — CLASSIFICAÇÃO FINAL

| peça | classificação | porquê |
|---|---|---|
| ORQUESTRADOR | `KEEP_TOP_LEVEL` | único que fecha pedido → porta |
| SINTONIA SCRAP | `KEEP_TOP_LEVEL` | executor composto real, com 24 fases a funcionar |
| NAVEGADOR · APIFY | `KEEP_TOP_LEVEL` | rotas reais, com trabalho próprio |
| PEDIDO | `KEEP_INTERNAL` | contrato; existe, mas não é estação |
| RECEITA | `KEEP_INTERNAL` | política do orquestrador; um só consumidor |
| `apify-conexao.yml` | `MERGE_CANDIDATE` | testa a ligação; cabe numa fase do scrap |
| `apify-sensores.yml` | `REPLACE_CANDIDATE` | devia pedir ao orquestrador |

**Nenhuma peça é `REMOVE_CANDIDATE`.** Nada aqui está morto.

---

## K — MODELO MÍNIMO PROPOSTO *(`PROPOSED` — não existe ainda)*

```
ENTRADA          botão · agenda · à mão
   ↓ cria
PEDIDO           o que se quer, sem dizer como       (contrato)
   ↓
ORQUESTRADOR     único dono de «como atender»
   ↓ consulta: receita · fontes · réguas
   ↓ despacha
EXECUÇÃO         SINTONIA SCRAP · navegador · HTTP · Apify (último recurso)
```

**Quatro estações**, não sete. Arquivo não é responsabilidade; módulo não é
estação.

---

## L — COMO FICARIA O INÍCIO DO MAPA

Hoje: `O PEDIDO E O PLANO` com 4 cartões do mesmo tamanho.

Proposto: **`ENTRADA DE COLETA`** → **`ORQUESTRADOR`**, e ao clicar no
orquestrador o raio-X mostra *recebe: Pedido · consulta: Receita, Fontes, Regras
· despacha: Scrap, executores*.

Nenhuma caixa desaparece: PEDIDO e RECEITA continuam acessíveis no raio-X, e
continuam no `state.generated.json`. **A decidir na etapa 3** — esta etapa não
reorganiza a tela.
