# FERRAMENTAS · o que a evidência já sustenta, e o que ainda não

Estado medido em `2cf4f98`. Nenhum número aqui foi digitado à mão — todos saem dos
artefatos versionados.

```
pares publicados      2.845   ·  46 culturas  ·  54 alvos  ·  122 rótulos
precisão 0,965 · recall 0,870 · portão PASS · testemunha reproduz idêntico
```

## 1 · PRONTA — Consulta de autorização de rótulo

**O que responde:** «a ADAMA tem produto autorizado para *cultura × alvo* na
Itália?» — com o rótulo, o número de registro e a substância ao lado.

| sustenta | |
|---|---|
| conjunto auditado | 100 perdas conferidas uma a uma, 99 eram autorização real |
| precisão medida | 0,965 contra gabarito completo de 30 rótulos |
| cauda não medida | amostra adjudicada de 25 pares fora do gabarito, 25 certos |
| reprodutibilidade | contêiner novo, sem rede e sem PDF, digest idêntico |

**Ressalva que a ferramenta tem de mostrar:** a resposta é a UNIÃO do conjunto novo
com o antigo. Sozinho, o novo ainda não pode substituir — 66 pares que o rótulo
autoriza continuam ilegíveis para o parser.

## 2 · PRONTA — Camada de portfólio das oportunidades

**O que responde:** «quais produtos ADAMA alcançam esta oportunidade, e há um
principal?»

28 das 43 oportunidades canônicas **ganham** produto; nenhuma perde. Nove
`PRIMARY_MATCH` mudam — cinco viram `null` porque um segundo produto passou a
qualificar, o que é mais honesto, e quatro nascem onde não havia (três deles
OLIVO, que entra no portfólio pela primeira vez).

**A regra do principal é a do motor, copiada e não reinventada.** `null` em 32 das
43 significa *mostrar todos sem hierarquia*, nunca «principal + N outros».

## 3 · QUASE PRONTA — Radar Futuro

```
10 sinais escritos à mão (7 COMPLETE, 3 PARTIAL)
14 candidatos aprovados pela régua, ainda não promovidos
231 candidatos fortes no acervo, de 3.035 brutos
```

**O que falta para promover os 14:** a ficha completa — janela esperada, mapa de
ação por departamento, portfólio. Escreve-se à mão, e não se gera.

**O que a régua provou sobre si mesma:** de 30 sinais julgados, 16 reprovados —
cinco deles por **citação que não existia no documento declarado**. Um mesmo leitor
atribuiu a um documento frases de outro. Sem o segundo estágio, cinco procedências
falsas teriam entrado com aparência perfeita.

## 4 · BLOQUEADA — Mapa de canal

```
CHANNEL_LAYER_STATE = PARTIALLY_COLLECTED_UNDER_ANOTHER_NAME
QUEM INFLUENCIA 50 · QUEM RECOMENDA 6 · QUEM REPRESENTA 6 · QUEM DISTRIBUI 4
QUEM COMPRA — sem resposta pública, e não vai ter
```

**Corrigi uma afirmação minha:** eu disse `NOT_COLLECTED`. A rodada de descoberta
de fontes já havia catalogado cooperativas, distribuidores e organizações de
produtores — com outro nome, e nunca usados para esta pergunta.

**Bloqueio real:** zero entidades ligadas à ADAMA, zero com compra conhecida. A
próxima coleta está desenhada, pequena e com régua de entrada declarada antes de
começar — dez consorzi agrari com catálogo público, dez OP reconhecidas.

## 5 · BLOQUEADA — Tradução para o motor canônico

O motor conhece 24 problemas; o vocabulário de rótulos fala 54 alvos. **38 alvos
foram aprovados para `ISSUE_ID` novo**, um é sinônimo, quatro são ruído, quatro
ficam `NAO_SEI`. A regressão de alias já rodou contra os 4,0 M de caracteres do
corpus e rejeitou `acaro` e `lema` (casaria *«problema»*).

**Bloqueio:** o motor vive em `claude/opportunity-commercial-priority-v1`. Alterá-lo
daqui seria mexer nele de fora. A proposta está pronta para quem o mantém.

## 6 · O gargalo real, agora nomeado

Não é mais o parser nem a leitura. É **a fronteira de linha em tabela de coluna
fundida** — 66 pares presos numa forma só.

A detecção de coluna **funciona** (agrupamento do x da primeira palavra de cada
linha; em LEBRON separa cultura em x 525,8 de alvo em x 607,3, e o recall sobe para
0,875). Mas os pares saem **deslocados de uma linha**, porque nessas tabelas as
linhas são adjacentes sem vão:

```
y=103,6  Mais, Mais Dolce,
y=113,1  Sorgo
```

e a regra de vão — que existe para não cindir texto que apenas quebra — funde as
duas numa célula só. Conferido à mão: ~4 de 16 pares sairiam errados. Precisão de
0,75 nessa família, abaixo do portão de 0,95, **e o gabarito não enxergaria**,
porque esses rótulos estão entre os seis que ele exclui.

Por isso a cisão está no código, documentada, e **desligada**.

> **O que falta:** inferir a fronteira de linha das DUAS colunas juntas.
> A linha é propriedade da TABELA, e não da coluna de cultura.

## 7 · Ordem sugerida para a próxima rodada

1. fronteira de linha conjunta → destrava 66 pares e permite responder **SIM** à
   pergunta da substituição;
2. promover os 14 candidatos aprovados a sinais completos;
3. coleta de canal, dez e dez, com a régua já escrita;
4. entregar a proposta de vocabulário a quem mantém o motor;
5. só então portal e Preview.
