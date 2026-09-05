# Espanha — os três hero cases endurecidos até V1

2026-08-30 · `claude/sintonia-eame-collection-es` · 380 testes OK

---

## O que fechou nesta rodada

**O `NEXT_SMALLEST_STEP` da rodada anterior.** Os 10 municípios de Huesca têm nome: Sariñena, Candasnos, Monzón, Tamarite de Litera, San Miguel del Cinca, Esplús, Peñalba, Sena, Grañén, Ilche. Junção exata `(cprovi, cmunca)` contra a tabela oficial de Aragón — 81 de 81, zero por aproximação. E a medida que justifica a recusa anterior: **em 335 dos 339 municípios de Aragón o código catastral difere do código INE**. Aproximar teria errado o nome em 99% dos casos.

**O bloqueio material do cereal.** Duas consultas ao Crossref. O resumo de um artigo de 2021 diz textualmente que, em cereal de inverno espanhol, a resistência a ALS e ACCase *"has become widespread, with farmers having to rely on pre-emergence herbicides over the last two decades"*. O primeiro autor é **Joel Torra** — o mesmo pesquisador que a camada científica já tinha confirmado por ORCID, achado pela rota do **milho**. Duas rotas independentes, culturas diferentes, mesma pessoa.

E isso vira o caso do avesso: o único produto ADAMA que nomeia *Lolium* na etiqueta é um inibidor de **ACCase** — o grupo comprometido. Os dez registros genéricos estão em pendimetalina, clortolurón, metribuzina e diflufenican — as químicas de pré-emergência para onde o mesmo resumo diz que o manejo migrou. **A arquitetura pública está melhor posicionada do que os rótulos declaram.**

**Os relógios do olivo, formalizados.** `FILE_DATE` 24/08 · `PUBLICATION_DATE` 26/08 · `OBSERVED_AT` Huelva 14/06 e Cádiz 27/05 · `CAPTURED_AT` 30/08. Classe: `SEASON_2026_SPRING_READING`, **não** `CURRENT_SIGNAL`. O `AGIR AGORA` se mantém — mas pela janela da etiqueta contra a fenologia observada, não por frescor de leitura.

## A classificação, e por que ela não mudou

| | tipo | o que sustenta |
|---|---|---|
| **ES-CASE-001** olivo × repilo | `AGIR AGORA` | CUPROXI FLO BBCH 10-85, prazo 7 d, contra fenologia **observada** BBCH 75-81 |
| **ES-CASE-003** cereal × gramíneas | `PREPARAR` | janela pós-emergência a 2-5 meses, com o contexto de resistência agora com fonte |
| **ES-CASE-002** milho × *Amaranthus* | `PLANEJAR` | janela fechada na etiqueta; abril/2027 |

`BEST_DEMO_CASE` = olivo.

## Magnitude e suporte amostral, separados

Huelva: 8,83%, **maior de 21 campanhas** — sobre **18 leituras em 7 parcelas**, o menor n da série inteira. Cádiz: 8,01%, 2ª maior — sobre **141 leituras em 39 parcelas**, rede estável nas 21 campanhas. Os dois campos não se compensam e agora vivem separados no cartão.

## O quarto erro, encontrado neste reteste

Eu media *"34 de 96 fichas ADAMA com código HRAC/IRAC/FRAC"*. O correto é **1 de 96**. Busca por substring sem limite de palavra e sem caixa: **"respiración" (26 ocorrências) e "aspiración" (15) contêm IRAC**. Uma sigla de quatro letras casa dentro de palavra comum em espanhol.

Consequência real: não dá para afirmar estratégia anti-resistência com o material público. A diversidade química está declarada; o modo de ação não. Agrupar substâncias por MoA seria classificação minha e não entra como fato.

## Regressão

15 testes novos, cada um em cima de um erro que já foi publicado uma vez: `FILE_DATE != SIGNAL_DATE`, `VARIANTE != CONTAGEM NACIONAL`, `21 != 23 campanhas`, `sigla curta precisa de \b`, `município nunca por aproximação`. `FALSE_CONFIDENCE_REGRESSIONS = 0`.

Uma nuance que tive que afinar: o número errado **pode** ser citado para ser corrigido. O teste percorre o JSON campo a campo e só aceita "23 safras" dentro de um campo cujo nome fala de discrepância, correção, erro ou contraprova.

Os 15 testes quebraram sete outros: o repositório exige que o número de testes publicado nos documentos venha da suíte real. 365 virou 380 em sete arquivos. A lei funcionou contra mim, que é para o que ela existe.

## Handoffs

As branches paralelas **existem** — com sufixo. Na rodada anterior procurei sem, e reportei que não existiam.

- **ADAMA datacenter** (`8680c58`): `ADAMA_ES_COLLECTION_READY = NO` — o catálogo público está negado **na borda** para o host inteiro. O mapa regulatório do milho é `USABLE` e foi o que me deu os 7 produtos do teste decisivo. O `PRODUCT-INTELLIGENCE` é `PARTIAL`: está todo vazio e corretamente marcado `NOT_COLLECTED` com motivo, nunca 0.
- **ADAMA local**: nenhuma branch casa o prefixo. `PENDING`, não bloqueia.
- **Itália** (`b8c0298`): `PARTIAL`, com material sério — 161 de 163 rótulos, ciência, três hero cases, 307 testes, e uma autocorreção de um `AGIR AGORA` que ela mesma havia declarado.

Nenhum merge.

## Cross-market: NÃO

Testei milho contra as sete pernas. Passam cultura, região de planície irrigada (Ebro e Pó) e portfólio de herbicida. **Falham** issue — Espanha tem *Amaranthus palmeri*, Itália tem daninha genérica e *Ostrinia* — e sinal público, porque a Itália tem **ausência medida** de boletim de milho nas três regiões do Pó.

O que os dois países têm em comum e **não** é um caso: mediram a mesma anomalia de autorização vigente com vencimento passado (Espanha 2 de 180 no par, 34 no ROPF; Itália 8). É observação sobre método.
