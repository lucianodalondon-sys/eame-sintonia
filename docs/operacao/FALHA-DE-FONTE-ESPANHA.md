# SE AMANHÃ O `regfiweb` DEVOLVER 404

Contrato operacional para a perda da fonte espanhola crítica. **Não é pessimismo:** a
`ES-T4-005` é a fonte que mais sustenta o piloto e a que tem a rota menos garantida.

**Data:** 2026-08-29 · **MISSÃO 08**

---

## O EXERCÍCIO

Amanhã as quatro rotas (`ProductosGrid`, `GetProductoById`, `ExportFichaProductoPdfGet`,
`ExportJsonProductos`) passam a devolver 404. O que acontece com o piloto?

### 1 · O que continuamos podendo afirmar — **como fato histórico**

Tudo o que já está arquivado, **desde que rotulado com a data da versão**:

| afirmação | continua? | por quê |
|---|---|---|
| ES-01717 tinha titular ADAMA Agriculture España S.A. **em 29/08/2026** | **SIM** | `ES-T4-005-ficha-primaria-es01717.json` + a ficha oficial em PDF |
| o fabricante era ADAMA Agricultural Solutions Ltd., planta Neot Hovav | **SIM** | idem |
| o registro espanhol tinha 3.084 registros, 1.993 em vigor **em 29/08/2026** | **SIM** | `ES-T4-005/ropf_20260829.json.gz` |
| ES-01717 foi renomeado de MAXENTIS para SORATEL MAX entre 05/2025 e 08/2026 | **SIM** | duas versões do `dc_web.pdf`, que **não** dependem do regfiweb |
| 1.786 denominações comuns sobre 720 registros | **SIM** | `dc_web.pdf`, URL `/dam/`, independente |
| em 165 registros o titular também é concessionário | **SIM** | cruzamento de dois arquivos arquivados |

> **A palavra que salva tudo isto é `em 29/08/2026`.** Sem ela, um fato histórico se
> apresenta como fato atual — que é exatamente o erro que a `REGUA-DE-CHANGE-EVENT` §4
> proíbe.

### 2 · O que deixa de ser atualizável — **imediatamente**

| função | vira |
|---|---|
| titular/fabricante de **qualquer novo** registro | `NÃO SEI` |
| status (vigente/cancelado) de qualquer registro | **STALE** a partir da semana seguinte |
| novas autorizações e cancelamentos espanhóis | **cego** |
| `STATUS/HOLDER/COMPOSITION/DATE CHANGE` na Espanha | **impossível** — nunca chegam a ter a segunda versão |
| a resposta de B03, B24, B26, B29 e B35 do Ask Sintonia | **CURRENT → STALE** |

### 3 · Hero cases — quem sobrevive

| case | sobrevive? | como |
|---|---|---|
| **CASE-013** (repilo, coorte) | **INTACTO** | não usa regfiweb. Fonte é RAIF |
| **CASE-008** (o clima não explica) | **INTACTO** | RAIF + NASA POWER |
| **CASE-014** (cronologia regulatória) | **INTACTO** | E-Phy + registro IT + CELLAR |
| **CASE-015** — `CORE CLAIM` | **INTACTO como histórico** | vive do `dc_web.pdf`, que é `/dam/` e não regfiweb; **mas** a separação de colunas usa o vocabulário de titulares do export arquivado, que congela |
| **CASE-015** — `ADAMA-SPECIFIC CLAIM` | **HISTÓRICO** | verdadeiro em 29/08/2026, não atualizável |

**É aqui que a divisão do CASE-015 feita na MISSÃO 07 paga.** O núcleo do hero não morre
com a fonte; só para de envelhecer.

### 4 · Cross-market cereal — 3/3 vira 2/3 + 1 histórico

| perna | efeito |
|---|---|
| FR | intacta |
| IT | intacta |
| **ES** | **congela em 29/08/2026** — os 30 produtos com protioconazol e os 3 da ADAMA continuam afirmáveis com data, não como estado atual |

O contrato de recorrência do cross-market (`chain.py`) tem de dizer
`FR changed · IT unchanged · ES source failed` — **nunca** recalcular um total como se as
três pernas tivessem sido lidas.

### 5 · O que vira `NÃO SEI`

`titular atual` · `fabricante atual` · `status atual` · `composição atual` ·
`usos autorizados atuais` · `novas denominações depois de 26/08/2026` ·
`qualquer contagem do registro espanhol com data posterior a 29/08/2026`.

---

## FALLBACKS — pesquisados, e a resposta honesta é dura

Pesquisa restrita à fonte espanhola crítica, como manda a missão. Nada além disso.

| candidato | o que entrega | classificação |
|---|---|---|
| **`dc_web.pdf`** — denominaciones comunes, URL `/dam/`, independente do regfiweb | registro · produto de referência · concessionária · denominação · data | **PRIMARY, para o que cobre.** Não traz titular, fabricante, composição, status nem cultura |
| **`ip_web.pdf`** — importações paralelas, mesma pasta `/dam/` | nº de registro em Espanha · nome comercial · empresa importadora · **país de procedência** · substância · datas · limite de venda | **SECONDARY / PARCIAL.** Cobre **só** importações paralelas. É a única rota pública que vimos com *país de procedência* |
| **`autorizaciones_excepcionales.xls`** (`ES-T4-002`) | necessidades sem solução autorizada | **INSUFFICIENT** para substituir o registro |
| **`jerarquia.xlsx` / `plagas.xlsx`** (`ES-T4-001`) | vocabulário de culturas e pragas | **INSUFFICIENT** — é vocabulário, não registro |
| **`lista-sustancias-activas-aceptadas-excluidas.pdf`** | lista de substâncias | **INSUFFICIENT** |
| **`pitumfinal.pdf`** | procedimento de usos menores | **INSUFFICIENT** — é norma, não dado |
| **datos.gob.es**, busca "fitosanitarios" | 6 datasets; o único de produto é **de Navarra** (`datosabiertos.navarra.es`), com cultura × doença × substância recomendada, 1.599 linhas, **sem número de registro, sem titular, sem fabricante** | **INSUFFICIENT** — é regional e é recomendação agronômica, não registro |
| ficha oficial em PDF por registro | tudo o que precisamos | **mesma infraestrutura** — cai junto. Não é fallback |

### Veredito

> **Não existe fallback equivalente ao `ES-T4-005`.** Nenhuma fonte pública encontrada
> entrega registro + titular + fabricante + composição + status fora do `regfiweb`.

O que existe é uma **cobertura parcial e independente**: o `dc_web.pdf` mantém vivos o
`CORE CLAIM` do CASE-015 e toda a análise de denominação/concessionária, porque está em
`/dam/` e não na aplicação.

---

## MITIGAÇÃO — o que fazer **antes** de amanhã

1. **Arquivar o export semanalmente.** Hoje há **uma** versão. Com uma versão só, o estado
   é `BASELINE_ESTABLISHED` e nenhum change event espanhol é possível — nem se a fonte
   continuar viva.
2. **Arquivar o `dc_web.pdf` semanalmente.** Mesma URL, conteúdo mutável: sem cópia datada,
   a próxima renomeação passa despercebida como a de 2025 quase passou.
3. **Rotular data de versão em toda saída espanhola.** É o que transforma "o titular é X"
   em "o titular era X em 29/08/2026" — e o segundo sobrevive à queda da fonte.
4. **Nunca publicar contagem do registro sem a data.** `1.998` já expira sozinho em
   30/09/2026 por decurso de prazo de escoamento, com a fonte no ar.
