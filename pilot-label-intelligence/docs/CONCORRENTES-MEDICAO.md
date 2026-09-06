# CONCORRENTES — medicao, nao coleta

A missao proibe abrir uma coleta concorrente grande agora. O que se pede e
medir se a mesma infraestrutura serviria. Serve, e a medicao esta abaixo.

## A pergunta respondida em uma linha

O registro oficial italiano nao e um registro da ADAMA. E o registro **inteiro**.
Filtrar por titular e uma linha de codigo, nao uma rota nova.

    17.695 produtos no registro
     3.714 ativos
       244 titulares distintos com produto ativo
       163 ativos da ADAMA (5 entidades) = 4,4% do mercado autorizado

Titulares com mais produtos ativos, todos na mesma tabela ja baixada:

| # | ativos | titular |
|---|---|---|
| 1 | 263 | SHARDA CROPCHEM ESPANA S.L. |
| 2 | 206 | NUFARM ITALIA S.R.L. |
| 3 | 172 | GOWAN ITALIA S.R.L. |
| 4 | 158 | SYNGENTA ITALIA S.P.A. |
| 5 | 139 | BAYER CROPSCIENCE S.R.L. |
| 6 | 136 | CORTEVA AGRISCIENCE ITALIA S.R.L. |
| 9 | **85** | **ADAMA ITALIA S.R.L.** |

## Respostas exigidas

    COMPETITOR_LABEL_ROUTE_EXISTS    = SIM — e a mesma rota, nao uma parecida
    COMPETITOR_OFFICIAL_SOURCES_FOUND = SIM — a mesma fonte oficial, o mesmo servlet
    AUTOMATION_REUSABLE_FROM_ADAMA    = SIM — muda o filtro de titular, nada mais
    COMPETITOR_EXTENSION              = FEASIBLE_NOW (nao executada por decisao de escopo)

## Os 4 casos demonstrativos

Um produto por titular grande. Baixados da fonte oficial nesta sessao, com hash.

| registro | produto | titular | etichetta em vigor desde | bytes | texto | tabela de uso |
|---|---|---|---|---|---|---|
| 000619 | VALGRAN | NUFARM ITALIA | 2024-07-22 | 159.076 | 6.578 ch | nao localizada |
| 002520 | ACTELLIC | SYNGENTA ITALIA | 2022-04-30 | 57.889 | 11.656 ch | sim |
| 003065 | OLIOCIN | BAYER CROPSCIENCE | 2018-08-16 | 34.956 | 5.420 ch | sim |
| 003553 | CURZATE | CORTEVA AGRISCIENCE | 2025-09-10 | 328.868 | 18.287 ch | sim |

Em VALGRAN a tabela nao foi localizada pelo teste de presenca. Isso e
`PARSE_STATE`, nao "produto sem usos autorizados" — a mesma lei vale para
concorrente.

## O que este teste tambem provou, de quebra

O localizador de rotulo (`bin/rotulo_localizar.py`) foi apontado para o registro
015275 sem consultar o acervo, e devolveu
`EtichettaServlet?id=43526`, etichetta em vigor desde **2024-10-01** — exatamente
o que o manifesto de `sintonia/canonical` ja registrava. Confirmacao independente
do resolvedor.

## O limite honesto: o servlet e intermitente

Medido: a mesma consulta, no mesmo minuto, alterna entre a ficha certa e uma
pagina generica de erro. Nao depende do numero de registro nem do numero de
buscas na sessao — foi testado com o mesmo registro nas duas condicoes. Dos 5
registros consultados, as tentativas necessarias foram 2, 2, 3, 4 e 4.

Consequencia de engenharia, nao de dado: a busca precisa **repetir com sessao
nova e espera crescente**. Uma esteira que faca uma tentativa so vai reportar
ausencia onde ha presenca — que e exatamente o erro que a missao proibe. E por
isso que a falha depois das tentativas grava `SEARCH_REJECTED`, um estado de
coleta, e nunca "sem rotulo".

Custo estimado para estender: 3.714 fichas ativas x ~2,6 tentativas medias, com
pausa de cortesia, cabe em uma janela noturna. Nao foi executado nesta missao
porque a missao mandou medir, nao coletar.
