# CAPACIDADES QUE **NÃO** DEVEM VIRAR FERRAMENTA

**Data:** 2026-08-31

> Um dataset novo é um motivo terrível para uma tela nova. Este documento existe para que
> a pressão de "temos o dado, vamos mostrar" encontre uma resposta escrita antes de virar
> superfície.

---

## 1 · META ADS — **`SHOULD_NOT_BECOME_TOOL`**

**O que é:** 1.340 cartões únicos, 1.417 observações, 23 páginas com `page_id` provado,
entrega em ES · IT · FR, comparação temporal provada em 60 de 67 recortes.

**Por que é sedutor:** é o dataset mais "vivo" do projeto. Um painel de anúncios de
concorrente parece inteligência competitiva de verdade.

**Por que não pode virar ferramenta:**

- O produto existe para **reduzir** excesso de informação desconectada. Um painel de
  anúncios **é** informação desconectada, em volume, com aparência de sinal.
- A própria missão Meta lista **sete coisas que não pode afirmar** — quanto investiu, se
  vendeu, participação, sucesso de campanha, se o produto está autorizado ali, se a página
  é daquele país, se um anúncio parou de veicular. **Um painel convida o leitor a concluir
  todas as sete.**
- `OPERATIONAL_TEMPORAL_SIGNAL_VALUE = NOT_PROVED`. Um painel com eixo de tempo afirma
  cadência que não foi medida.

**Onde vive:** uma das quatro linhas da camada de **competição dentro do caso**.

```
ESSENCE_RISK = HIGH se virar superfície própria
```

---

## 2 · CREATOR DEEP CORPUS — **`SHOULD_NOT_BECOME_TOOL`**

**O que é:** 442 materiais, 280 nos últimos 90 dias, 10 alvos, 9 rotas de conteúdo
provadas.

**Por que não:** é conteúdo **sobre** uma entidade que o Creator Map já identificou.
Separá-lo em ferramenta criaria duas superfícies para a mesma pessoa e faria o corpus
responder *"quem chamar?"*, que é pergunta do mapa.

**E o corpus não sustenta o problema do caso**: classifica em `WEED` / `PEST` / `DISEASE`,
nunca em `FUSARIUM`, `REPILO` ou `SEPTORIA`.

**Onde vive:** aba dentro da ficha do creator.

---

## 3 · COMPETITOR PUBLIC COMMUNICATION — **`NOT_ENOUGH_EVIDENCE`, e cuidado**

**O que é:** 22 contas oficiais provadas (ES 10 · IT 8 · FR 4), 5 empresas, identidade e
manifesto congelados.

**Por que não, hoje:** `CONTENT_COLLECTION_STAGE = NOT_STARTED`. **Zero itens.**
`IDENTITY_IS_NOT_SIGNAL`.

**O risco específico:** uma tela com 22 contas parece cobertura. Ela é uma **lista de
endereços**. E o zero de hoje significa `NO_CONTENT_COLLECTION_EXECUTED` — **nunca**
`COMPANY_NOT_COMMUNICATING`.

**Onde vive quando houver conteúdo:** a mesma camada de competição do caso, outra linha.

---

## 4 · FILA DO "QUE FALTA PROVAR" — **estado visual, não ferramenta**

**O que é:** o inventário do que a inteligência não sabe — 138 tuplas `NOT_KNOWN`, 5
recortes esperando o problema, 1.873 rótulos, 206 strings, 22 páginas sem escopo de país,
a tabela cultura × alvo italiana.

**Por que é valioso:** *"o que ainda não sabemos?"* é uma das seis perguntas da gramática
do casco, e a única sem superfície.

**Por que não vira ferramenta:** viraria **painel de auditoria** — e o briefing original do
produto proíbe isso com nome: *"não deve virar painel de auditoria gigante; é transparência
operacional"*.

**Onde vive:** estado dentro de cada objeto, mais um bloco no caso.

---

## 5 · DIRETÓRIO DE ESPECIALISTAS COMO RANKING — **proibido, não apenas desaconselhado**

Não é uma capacidade a alocar: é uma forma que **não pode existir**.

```
RECURRENCE ≠ AUTHORITY        FOLLOWERS ≠ AUTHORITY        ENGAGEMENT ≠ INFLUENCE
IDENTITY_PROVED ≠ ISSUE_EXPERTISE_PROVED
```

Este refresh mostrou por quê, com número: as duas pessoas mais óbvias do recorte
`ES × OLIVE × REPILO` têm 42 e 27 obras no corpus e **zero** com repilo no título.
Um ranking por recorrência as teria colocado em primeiro lugar.

**Onde vive:** lista **sem ordem**, dentro do caso, com o portão de expertise antes da
contagem.

---

## 6 · QUALQUER "SCORE"

```
ADAMA_OPPORTUNITY_SCORE   ·   MARKET_OPPORTUNITY_SCORE   ·   SALES_SCORE
ADAMA_RELEVANCE_SCORE     ·   CREATORS_READY
```

Todos proibidos, e o motivo é sempre o mesmo: **somar eixos esconde qual eixo está vazio —
e o eixo vazio é a informação que o usuário precisa ver.**

`CREATORS_READY` é o exemplo mais concreto: somaria 8 pessoas com 2 empresas agrícolas e
apagaria a distinção que decide se a conversa é contrato de influenciador ou acordo B2B.

---

## RESUMO

```
SHOULD_NOT_BECOME_TOOL ......... META ADS · CREATOR DEEP CORPUS ·
                                 FILA DO QUE FALTA PROVAR · RANKING DE ESPECIALISTA
NOT_ENOUGH_EVIDENCE ............ COMPETITOR PUBLIC COMMUNICATION
PROIBIDO POR FORMA ............. qualquer score agregado
```

**Quatro capacidades reais, com dado real, que não devem ganhar superfície própria.**
Todas cabem dentro do caso — que é onde o produto comprime informação em vez de exibi-la.
