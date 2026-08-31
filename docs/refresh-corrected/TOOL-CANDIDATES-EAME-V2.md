# TOOL ECONOMY — V2

**Data:** 2026-08-31 · **`FINAL_TOOL_SET_DECIDED = NO`** — tudo aqui é
`ARBITRATION_CANDIDATE`.

> Só atualizo o que as correções mudaram. Nada é implementado, nada é arbitrado.

---

## 1 · O QUE MUDOU DESDE O V1

### `RADAR / CASOS` precisa aceitar **quatro tipos de objeto**, não um

Esta é a maior consequência da passagem. O V1 tratava tudo como **caso**, e por isso
publicou `ACT_NOW = 0` como estado do produto inteiro. São quatro:

| objeto | unidade | quantidade |
|---|---|---|
| `CASE` | país × região × cultura × problema × tempo | 1 |
| `REGULATORY_DEADLINE` | país × registro × produto × prazo | 155 |
| `LONGITUDINAL_FIELD_PRESSURE` | país × região × cultura × problema × tempo | 1 |
| `IDENTITY_CHAIN` | competidor × país × produto | 36 |

**`ARBITRATION_CANDIDATE`:** a superfície `Radar/Casos` absorve os quatro, ou eles se
separam? O argumento a favor de absorver é forte — todos respondem *"o que merece
atenção?"*. O argumento contra também: **três deles não têm cultura nem problema**, e o
card de caso foi desenhado em cima dessa chave.

**Não decido.**

### `JANELAS DA CULTURA` sai de `DEMOTE` e vira **`TEST`**

O V1 rebaixou dizendo *"não há relógio em país nenhum"*. **Estava largo demais.**

```
CROP_STAGE_AT_OBSERVATION ................ PROVADO em 3 de 22 itens
APPLICATION_TRIGGER_AT_OBSERVATION ....... PROVADO em 5 de 22 itens
CURRENT_CROP_STAGE_TODAY ................. NOT_PROVED em 22 de 22
```

**Existe fenologia no corpo — mas ela é do momento da observação, não de hoje.** A
superfície tem dado para **um** dos quatro relógios, e só na metade que é passado.

`TEST` até a arbitragem: a pergunta é se uma tela de tempo que só mostra *"em 23/04 o
boletim declarava fase X e recomendava tratamento"* é útil ou é armadilha.

### `FONTES` vira **`STRENGTHEN_CANDIDATE`** — por causa da latência

Medição nova:

```
ES-RAIF ....... 7 · 3.006 · 3.386 · 3.386 dias
IT-LAMMA ...... 130 dias
FR-VIGNEVIN ... 56 · 56 · 75 · 95 · 103 · 110 · 172 dias
```

A superfície `Fontes` hoje mostra **estado de acesso** (viva, bloqueada, com ressalva).
A latência é outra dimensão, e é operacional: uma fonte que responde 200 e entrega
documento de 130 dias não é a mesma coisa que uma que entrega o de ontem.

⚠️ **Com a ressalva junto:** captura única, então `SOURCE_LATENCY == AGE_OF_OBSERVATION`
por construção. Mede idade na primeira captura, não latência de regime. **Uma tela que
mostrasse isso como "atraso do pipeline" estaria errada** — e é por isso que é `TEST`
dentro do `STRENGTHEN`, não implementação.

### `RADAR DO FUTURO` continua `QUESTION`, com um argumento novo

O V1 disse que os cinco recortes parciais falhavam *pelo mesmo motivo*. **Falso.** Espanha
falha por **problema**; França falha por **localidade**. São filas diferentes, e talvez
isso seja exatamente o que um radar de temas emergentes deveria mostrar: **o bloqueador,
não o tema**.

---

## 2 · O QUE NÃO MUDOU

| superfície | veredito | motivo inalterado |
|---|---|---|
| Visão Geral · Radar/Casos · Acervo · Relatórios · Sistema · Config · Camada EAME | **KEEP** | — |
| **Caso** (detalhe) | **STRENGTHEN** | 4 das 7 camadas enchem |
| **Análises** | **MERGE_CANDIDATE** | duplica as classes de caso |
| — | **KILL_CANDIDATE = 0** | nenhuma superfície se provou descartável |

---

## 3 · CAPACIDADES — reclassificação

| capacidade | V1 | V2 | por quê mudou |
|---|---|---|---|
| **COMPETITOR FORESIGHT** | `CASE_LAYER_CANDIDATE` | **`NEW_OBJECT_TYPE_CANDIDATE`** | não é camada de caso: é **outra unidade** (competidor × país × produto). Forçá-la para dentro do caso exigiria cultura e problema que ela não tem |
| **META** | `CASE_LAYER_CANDIDATE` | **`SHOULD_NOT_BECOME_TOOL`** + perna da cadeia de identidade | inalterado no essencial: painel de anúncios é `ESSENCE_RISK = HIGH` |
| **TERRITORIAL** | `CASE_LAYER_CANDIDATE` | **`CASE_LAYER_CANDIDATE`** | confirmado — é a camada `Campo` |
| **FIELD_HISTORICAL (RAIF)** | fora do escopo | **`CASE_LAYER_CANDIDATE`** + `NEW_OBJECT_TYPE_CANDIDATE` | entrou por decisão do coordenador; mas **não é perna independente** do territorial |
| **REGULATORY_DEADLINE** | não existia | **`NEW_OBJECT_TYPE_CANDIDATE`** | é o único objeto com decisão de negócio defensável hoje |
| **CREATOR MAP** | `BOTH_POSSIBLE` | **`BOTH_POSSIBLE`** | inalterado |
| **CREATOR DEEP CORPUS** | `SHOULD_NOT_BECOME_TOOL` | inalterado | é conteúdo sobre a entidade |
| **EXPERT DIRECTORY** | `CASE_LAYER_CANDIDATE` | inalterado | com portão de expertise antes de contar |
| **PUBLIC COMMUNICATION** | `NOT_ENOUGH_EVIDENCE` | inalterado | 22 contas, zero conteúdo |

---

## 4 · AS TRÊS LACUNAS FUNCIONAIS, REVISITADAS

**A · Creator sem superfície** — inalterado: `BOTH_POSSIBLE`. O dado novo (corpus com
`LAST_90D = 164`, não 280) não muda a decisão, mas corrige a base sobre a qual ela seria
tomada.

**B · "Quem viu primeiro" / relógio temporal** — **agora tem um argumento a mais contra
construir já.** A latência mostrou que o sistema lê documentos com 56 a 172 dias. Um
relógio de "quem viu primeiro" construído sobre leituras assim mediria **a ordem em que o
pipeline leu**, não a ordem em que o mundo aconteceu. `NOT_ENOUGH_EVIDENCE`.

**C · Fila do "que falta provar"** — **fortalecida**. Esta passagem produziu bloqueador
exato por item: `FALTA REGION` em 3 itens franceses, `FALTA ISSUE` em 4 espanhóis, e assim
por diante. Isso não é backlog: é **o mapa do que falta para cada recorte virar caso**, e é
a única das três lacunas que ganhou dado nesta passagem.

Continua `CASE_LAYER_CANDIDATE` + estado visual transversal. **Não** ferramenta.

---

## 5 · RESUMO

```
TOOLS_KEEP ................. 7
TOOLS_STRENGTHEN ........... 2    Caso · Fontes (por latência, com ressalva)
TOOLS_MERGE_CANDIDATES ..... 1    Análises
TOOLS_DEMOTE ............... 0    (Janelas da Cultura saiu de DEMOTE para TEST)
TOOLS_TEST ................. 2    Janelas da Cultura · Radar do Futuro
TOOLS_KILL_CANDIDATES ...... 0

NEW_OBJECT_TYPE_CANDIDATES . 3    REGULATORY_DEADLINE · IDENTITY_CHAIN ·
                                  LONGITUDINAL_FIELD_PRESSURE
NEW_TOOL_CANDIDATES ........ 1    Creator Map (BOTH_POSSIBLE)
CASE_LAYER_CANDIDATES ...... 3    Territorial · Expert Directory · Field Historical
SHOULD_NOT_BECOME_TOOLS .... 4    inalterado
```

**A mudança conceitual desta passagem não é uma ferramenta nova — é o reconhecimento de que
o produto tem mais de um tipo de objeto.** Essa é a pergunta que vai para a arbitragem.
