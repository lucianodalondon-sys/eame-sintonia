# JANELAS-68 — as 68 fontes de janela D29 que chumbaram no canario

Ramo janelas-68-v1 sobre a producao df0865e6. Vivo e Sala nao tocados. Detalhe por fonte em
JANELAS-68-RELATORIO-V1.json; formas em -FORMAS-V1; cruzamento com os ramos em -CRUZAMENTO-V1; medida com rede em
-MEDICAO-V1 (codigo receitas-182-v1 @ 41d8751e, 1 fonte por dominio, 100 pedidos, max 5 por dominio, portao 5/5 PASS IT).

| Forma (pelo retrato que o robo guardou) | Fontes |
|---|---|
| MENU (entrada e navegacao) | 22 |
| PAGINA_BOLETIM (entrada e o proprio conteudo) | 17 |
| PDF (boletins em PDF/anexos) | 11 |
| REPARADO_A_REVER (reparo achou itens, falta revisao) | 6 |
| JS_API (HTML vazio, conteudo por JS) | 5 |
| LISTA_NOTICIA | 3 |
| NAO_SEI (so paginas fixas) | 4 |

| Estado | Fontes |
|---|---|
| resolve janela-formas-v1 (medido pelo ramo) | 2 — ERSA FVG PDF, LaMMA pagina=boletim |
| resolve receitas-182-v1 (reparo geral; item revisto a mao) | 5 — Asnacodi x2, Horta x2, Regione Marche agrometeo |
| canario passa mas o item e pagina fixa (FALSO) | 6 — Lazio, Piemonte, Toscana, Veneto, ARPA Lombardia, SIARL |
| nenhum ramo resolve (medido ou sem rota) | 36 |
| nao medida: outra fonte do mesmo dominio ja foi medida nesta rodada | 16 |
| sem contrato no livro vivo | 3 |

Achados:
- O reparo geral da receitas-182-v1 + canario aprovam PAGINAS FIXAS como se fossem noticia (6 de 9 aqui). Antes de
  instalar esse ramo, o canario precisa de recusar item sem data/sem ser noticia.
- A ARSAC (Calabria) nao parou: mudou para arsac.calabria.it (boletins validos ate 04/08/2026, lidos pela
  janela-formas-v1). O endereco registado na P1g era o antigo — corrige o que eu disse na P1g.
- A menor mudanca para quase todas as 36 e TROCAR A ENTRADA: o contrato aponta para a pagina institucional e o
  boletim esta uma pagina mais dentro (medido na P1g). PDF: contrato PDF na rota que ja existe. JS: rota JSON nova.

EM PALAVRAS SIMPLES: das 68 fontes de boletins que o robo nao conseguia ler, so 7 ficam resolvidas pelos consertos que
ja existem. O conserto «geral» parece salvar mais 6, mas quando olhei o que ele apanhou eram paginas fixas (acessibilidade
do site, residuos, viveiros) e nao boletins — isso tem de ser travado antes de instalar. Para a maior parte das outras,
o problema e simples: registamos a porta de entrada da instituicao e nao a pagina onde o boletim esta; trocar o
endereco de entrada resolve a maioria, e os PDF precisam do contrato PDF que ja existe noutro ramo.
