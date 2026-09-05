# COLETA DE CANAL 10 + 10 — O DESENHO, ANTES DE QUALQUER COLETA

Missão C. **Nada foi coletado.** Isto é a régua, os dois universos e a matriz do
que cada documento pode e não pode responder — para ser lido antes de decidir se
a coleta começa.

Estado da camada, corrigido e mantido: **`PARTIALLY_COLLECTED_UNDER_ANOTHER_NAME`**.
Não é `NOT_COLLECTED`. A rodada de descoberta de fontes já tinha classificado
`COOPERATIVE`, `COOPERATIVE_DISTRIBUTOR`, `PRODUCER_ORGANISATION` e
`PRIVATE_AGRONOMIC_ADVISORY` — material de canal, catalogado com outro nome e
nunca usado para esta pergunta.

---

## 1 · O que a amostra já provou, sem coleta nova

Medido em `data/samples/IT-FUTURO-V1/IT-CANAL-REGUA-V1.json`, sobre 119 entidades
que já estavam no acervo:

| papel | entidades com evidência | o acervo responde? |
|---|---|---|
| QUEM INFLUENCIA | 50 | **sim** |
| QUEM RECOMENDA | 6 | **sim** |
| QUEM REPRESENTA PRODUTORES | 6 | em parte |
| QUEM DISTRIBUI | 4 | em parte |
| QUEM COMPRA | 0 | **não, e nunca vai** |

E o número que decide esta missão:

> **`LINKED_TO_ADAMA = 0`** · **`BUYS_PRODUCT_KNOWN = 0`**

Sessenta entidades com papel demonstrável, e **nenhuma** com ligação demonstrável
à ADAMA. É isso que a coleta tem de mudar — ou não vale a pena fazê-la.

## 2 · A régua de entrada

Uma entidade só entra se **um documento público, citável por URL, provar o papel**.
O que não estiver no documento fica `NOT_IN_SOURCE`. Não há inferência.

| teste | entra | não entra |
|---|---|---|
| **prova de papel** | catálogo de mezzi tecnici publicado, lista de pontos de venda, ato de reconhecimento regional da OP | presença em convegno, menção por terceiro, "toda a gente sabe" |
| **território** | a própria fonte nomeia província ou região | região herdada do nome, do domínio ou do palestrante |
| **identidade** | razão social + sede + um identificador estável (P.IVA, número de reconhecimento, domínio próprio) | página agregadora sem dono declarado |
| **data** | o documento traz data, ou o snapshot traz `CAPTURED_AT` e o URL | página sem data e sem snapshot |
| **ligação ADAMA** | o catálogo público **nomeia** o produto | o catálogo cita a substância activa e eu deduzo o produto |

> **ORGANIZAÇÃO NOMEADA NUM CONVEGNO NÃO É CANAL COMERCIAL.**

## 3 · Os dois universos

### Universo A — 10 consorzi agrari com catálogo público de mezzi tecnici

**Por que este universo:** é a única fonte pública que liga **território** a
**distribuição**. Um consorzio agrario publica o que vende e onde vende.

**Como se escolhem os 10:** pelas regiões dos sinais futuros já verificados —
Calabria e Sicília (agrumi), Veneto e Piemonte (noce, nocciolo), Lazio–Viterbo
(nocciolo), Friuli-Venezia Giulia e Alto Adige (vite), Emilia-Romagna (pero),
Capitanata–Puglia (pomodoro). Não por tamanho, não por fama: **pela região onde
já existe sinal**, para que a coleta possa cruzar com alguma coisa.

**Critério de exclusão:** consorzio sem catálogo publicado não entra, por maior
que seja. Sem catálogo, não há documento; sem documento, não há papel provado.

### Universo B — 10 organizzazioni di produttori reconhecidas

**Por que este universo:** responde QUEM REPRESENTA com **registo público** — o
reconhecimento da OP é ato administrativo regional, citável, datado, com culturas
declaradas.

**Como se escolhem os 10:** as OP reconhecidas nas mesmas regiões, priorizando as
culturas dos sinais (agrumi, nocciolo/noce, vite, pomodoro da industria, pero).

**Critério de exclusão:** associação sem reconhecimento regional citável não
entra. Consórcio de tutela de denominação não é OP e não entra.

## 4 · A matriz — o que cada documento pode e não pode responder

| pergunta | catálogo de consorzio | ato de reconhecimento de OP |
|---|---|---|
| quem **distribui** naquele território | **SIM** — é literalmente o que o documento declara | não |
| quem **representa** produtores, e de que culturas | não | **SIM** — culturas e sócios estão no ato |
| quem **recomenda** | parcial: só se o consorzio publicar serviço técnico | não |
| quem **influencia** | não | não |
| quem **compra** | **NÃO** | **NÃO** |
| **o canal carrega produto ADAMA** | **SIM, e só aqui** — se o catálogo nomear o produto | não |
| quanto compra, a que preço, com que frequência | **NÃO** | **NÃO** |
| o produtor final daquele território usa o produto | **NÃO** | **NÃO** |

### A única ligação ADAMA que esta coleta pode produzir

`CATALOGO_PUBLICO_NOMEIA_PRODUTO`, e o que ela significa, escrito por extenso:

> **o canal publica que carrega o produto.**

Não significa que o canal compra da ADAMA. Não significa que o produtor compra o
produto. Não significa volume, preço nem exclusividade. É um facto de catálogo, e
o cartão tem de dizer isso na cara de quem o lê.

> **PROXY NÃO VIRA FACTO PRIVADO.** Compra é dado privado. O máximo honesto é
> quem distribui e quem representa.

## 5 · Custo, tamanho e forma do resultado

- **20 documentos**, um por entidade. Não é varredura: é leitura dirigida.
- Cada entidade sai como uma ficha com `SOURCE_URL`, `CAPTURED_AT`, papel provado,
  citação literal que prova o papel, território declarado, e `NOT_IN_SOURCE` em
  tudo o resto.
- O que entra em `LINKED_TO_ADAMA` só entra com o nome do produto **copiado do
  catálogo**, com a linha citada.
- Resultado esperado, declarado antes de medir: `QUEM_DISTRIBUI` sai de 4 para
  ~14; `QUEM_REPRESENTA` de 6 para ~16; `LINKED_TO_ADAMA` sai de 0 para **um
  número que pode perfeitamente ser 0** — se nenhum catálogo nomear produto ADAMA,
  esse zero é o resultado, e é um resultado válido.

## 6 · A decisão

A coleta **vale a pena se, e só se**, puder mover `LINKED_TO_ADAMA` acima de zero
por catálogo citado. Se a resposta for não, o que se ganha é apenas mais mapa de
canal sem ADAMA dentro — e isso o acervo já tem.

**Estado: DESENHADA, NÃO EXECUTADA.** Aguarda autorização, por três razões:

1. é coleta externa nova, e a ordem desta rodada é réguas antes de coleta;
2. a Missão A ainda estava a correr quando este desenho foi escrito;
3. o resultado pode legitimamente ser zero, e isso deve ser aceite **antes** de
   se gastar a coleta, não depois.
