# TOOL ECONOMY — SINTONIA EAME

**Data:** 2026-08-31 · **`FINAL_TOOL_SET_DECIDED = NO`** — isto são candidatos, não decisão.

> Regra que governa o documento: **dataset não vira ferramenta**. Uma superfície só se
> justifica se responde uma **pergunta de decisão própria**, tem **dado real** e tem
> **valor recorrente**.

---

## 1 · AS DOZE SUPERFÍCIES DO CASCO V7

| # | superfície | pergunta de decisão | dado real hoje | valor recorrente | redundância | `ESSENCE_RISK` | recomendação |
|---|---|---|---|---|---|---|---|
| 1 | **Visão Geral** | o que merece atenção agora? | **1 item** (single signal) + estado das fundações | semanal | — | baixo | **KEEP** |
| 2 | **Radar do Futuro** | onde a evidência se acumula? | 5 recortes parciais, sem tema formado | semanal | com `Radar/Casos` | **médio** | **QUESTION** — ver 1.1 |
| 3 | **Radar / Casos** | que casos existem e até onde vão? | 1 caso + 5 parciais | por evento | — | baixo | **KEEP** |
| 4 | **Caso** (detalhe) | o que sustenta, o que falta, quem olha? | 1 caso enche 1 de 7 camadas | por caso | — | baixo | **STRENGTHEN** |
| 5 | **Janelas da Cultura** | ainda dá tempo? | **nenhum relógio de lavoura em país nenhum** | — | — | **alto** | **DEMOTE** — ver 1.2 |
| 6 | **Acervo** | o que já foi coletado? | 432 documentos + 234 RAW com SHA | contínuo | — | **médio** | **KEEP** com guarda |
| 7 | **Fontes** | a rota está viva? | 37 fontes fichadas + rotas bloqueadas | semanal | — | baixo | **KEEP** |
| 8 | **Análises** | o que dá para afirmar, e até onde? | 3 modelos, 0 leituras | por caso | **com as classes de caso** | baixo | **MERGE_CANDIDATE** |
| 9 | **Relatórios** | o que levo para a reunião? | snapshot e freeze têm lastro real | por ciclo | — | baixo | **KEEP** |
| 10 | **Sistema** (lib) | — | pronta e correta | — | — | nenhum | **KEEP** |
| 11 | **Config** | — | estrutura certa | — | — | nenhum | **KEEP** |
| 12 | **Camada EAME** | onde os mercados divergem? | matriz de comparabilidade enche | por ciclo | — | baixo | **KEEP** |

### 1.1 · Por que `Radar do Futuro` é `QUESTION`

Ele existe para temas **antes** de virarem caso. Hoje o acervo tem **cinco recortes
parciais** — e todos são parciais pelo **mesmo** motivo (falta o problema no corpo). Isso
não é um radar de temas emergentes: é uma **fila de itens incompletos**, que é outra coisa
e talvez pertença a outro lugar (ver `CAPABILITIES-THAT-SHOULD-NOT-BECOME-TOOLS.md`).

**Não é para matar.** É para o red team perguntar se ele responde uma pergunta que
`Radar/Casos` não responde.

### 1.2 · Por que `Janelas da Cultura` é `DEMOTE`

É a superfície mais elaborada do casco depois do detalhe de caso — quatro relógios,
resolução temporal declarada, semântica de ação em quatro combinações. E o acervo entrega:

```
APPLICATION_WINDOW ........ NÃO CONECTADA em ES, IT e FR
LABEL_USE_STAGE ........... FR 376/414 BBCH · ES 3 · IT 0
CURRENT_CROP_STAGE ........ não existe em país nenhum
```

**`ESSENCE_RISK = alto`**: uma tela de tempo bonita e vazia é o convite mais direto que
este produto tem para alguém preencher com estimativa. E `LABEL_USE_STAGE` **não** é
`CURRENT_APPLICATION_WINDOW`.

**`DEMOTE` não é `KILL`.** É rebaixar de superfície própria para **bloco dentro do caso**,
onde os quatro relógios já existem — até que exista relógio de lavoura.

---

## 2 · CAPACIDADES NOVAS — onde cada uma cabe

| capacidade | classificação | por quê |
|---|---|---|
| **COMPETITOR FORESIGHT** | **`CASE_LAYER_CANDIDATE`** | a camada de competição do caso **já existe** no casco, com as quatro linhas certas. Mas hoje a capacidade **não alcança a chave de caso** — sem cultura × alvo ela fica órfã |
| **META** | **`CASE_LAYER_CANDIDATE`** — dentro da mesma camada | é uma das quatro linhas de competição (`atividade paga em mídia`). **Nunca superfície própria**: um painel de anúncios é exatamente o `ESSENCE_RISK` que o produto combate |
| **TERRITORIAL** | **`CASE_LAYER_CANDIDATE`** | é a camada `Campo` do caso. Já tem lugar |
| **CREATOR MAP** | **`BOTH_POSSIBLE`** | responde uma pergunta de decisão **própria** (*quem o Marketing pode avaliar?*), com 10 entidades e valor recorrente. Mas ficaria vazia em 5 dos 6 recortes se fosse camada de caso |
| **CREATOR DEEP CORPUS** | **`SHOULD_NOT_BECOME_TOOL`** | é conteúdo **sobre** a entidade do Creator Map. Vira aba dentro da ficha, nunca ferramenta |
| **EXPERT DIRECTORY** | **`CASE_LAYER_CANDIDATE`** | `CASE_ID` já é a chave. Mas precisa do **portão de expertise** antes de contar alguém como especialista do problema |
| **PUBLIC COMMUNICATION** | **`NOT_ENOUGH_EVIDENCE`** | 22 contas provadas, **zero conteúdo**. Identidade não é sinal |

---

## 3 · AS TRÊS LACUNAS FUNCIONAIS, REAVALIADAS

### A · Creator sem superfície própria → **`BOTH_POSSIBLE`, e o dado agora ajuda a decidir**

O teste: dos 6 recortes, **1** tem creator com rota de ativação (país + cultura) e
**nenhum** tem creator com o problema provado.

- Como **camada de caso**: ficaria vazia em 5 de 6.
- Como **ferramenta própria**: teria conteúdo (10 entidades) e responderia uma pergunta que
  o caso não faz.

**A pergunta de negócio decide, não a estética:** o Marketing procura creator *a partir de
um caso*, ou *a partir de uma cultura e uma região*? Se for a segunda, é ferramenta.

### B · "Quem viu primeiro" / relógio temporal → **componente transversal, não ferramenta**

Cinco relógios já nomeados no contrato de produto; o casco implementa quatro. O quinto
(`COMPETITOR OBSERVATION CLOCK`) não existe.

**Mas o refresh mostrou que ele não tem dado**: a comparação temporal da Meta cobre uma
janela de **uma hora**, e `OPERATIONAL_TEMPORAL_SIGNAL_VALUE = NOT_PROVED`. Construir a
superfície agora seria construir uma pergunta sem resposta.

**Veredito: componente transversal dentro do caso, quando houver duas leituras com
intervalo real.** Não é ferramenta.

### C · Fila do "que falta provar" → **estado visual, e talvez a coisa mais honesta do produto**

Este refresh produziu, sozinho: 5 recortes esperando o problema · 138 tuplas `NOT_KNOWN` ·
1.873 rótulos de ontologia · 206 strings · 22 páginas sem escopo de país · a tabela cultura
× alvo italiana.

**Não é backlog de engenharia: é o mapa do que a inteligência ainda não sabe** — e uma das
seis perguntas da gramática do próprio casco é *"o que ainda não sabemos?"*, a única sem
superfície.

**Veredito: `CASE_LAYER_CANDIDATE` + estado visual transversal.** Ferramenta própria, não —
viraria painel de auditoria, que é `ESSENCE_RISK`.

---

## 4 · RESUMO

```
TOOLS_KEEP ................. 8   Visão Geral · Radar/Casos · Acervo · Fontes ·
                                 Relatórios · Sistema · Config · Camada EAME
TOOLS_STRENGTHEN ........... 1   Caso (detalhe)
TOOLS_MERGE_CANDIDATES ..... 1   Análises  →  dentro do Caso
TOOLS_DEMOTE ............... 1   Janelas da Cultura  →  bloco do Caso
TOOLS_KILL_CANDIDATES ...... 0
TOOLS_QUESTION ............. 1   Radar do Futuro

NEW_TOOL_CANDIDATES ........ 1   Creator Map (BOTH_POSSIBLE)
CASE_LAYER_CANDIDATES ...... 4   Foresight · Meta · Territorial · Expert Directory
SHOULD_NOT_BECOME_TOOLS .... 4   ver documento próprio
```

**Nenhuma ferramenta nova foi decidida.** Um dataset novo não é motivo para uma superfície
nova — e este refresh trouxe quatro datasets que cabem todos **dentro do caso que já
existe**.
