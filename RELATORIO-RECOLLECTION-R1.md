# RELATÓRIO — R1 · RECOLLECTION E INCREMENTALIDADE NA LINHA UNIFICADA

Branch `recollection-prova-v1`, a partir de `origin/unificacao-v1` (`5a16d077`), 2026-09-23.
Travas cumpridas: nenhuma coleta real, nada na Sala, nenhum serviço vivo tocado,
nenhum código de produção alterado (nenhuma prova falhou por defeito do código).

## ENTREGA

```
ONDE_ESTAVA_PROVADO    regras/incrementalidade_test.mjs · regras/recollection_test.mjs ·
                       regras/paridade_test.mjs · provas/paridade_duas_rodadas.mjs ·
                       provas/recollection_red_team.mjs · provas/recollection_red_team_estrito.mjs
                       (nascidos em 69d16ea3, 68aef8a9, 42708647 — 22/09; know-how §167)
NA_UNIFICACAO          SIM — os seis estão em unificacao-v1 e passam nela (medido nesta branch)
INCREMENTALITY_PROVEN  YES — o 2.º pedido ao mesmo endereço não chega ao servidor (0 de 0)
UNNECESSARY_REFETCHES  0 — em 6 de 6 rodadas da prova nova e 5 de 5 da paridade
FALSE_DOCUMENT_CHANGED 0 — ruído de HTML (visitas, hora, token) dá SEEN_AGAIN e 0 objectos RAW
CHANGE_DETECTED        YES — matéria nova dá DOCUMENT_CHANGED_IN_PLACE, versão nova,
                       MATERIAL_DIFF=true, OLD/NEW_NORMALIZED_HASH; a versão anterior
                       continua em disco e o sha256 dela bate com o livro
RECOLLECTION_PROVEN    YES — 503 fica TRANSPORT_OR_EMPTY sem DOCUMENT_ID e o endereço NÃO
                       fica conhecido; quando o servidor volta é colhido (NEW=1). UNKNOWN
                       não virou NEVER: declarado MUTABLE, a fonte é revisitada
P9_RESOLVIDO           SIM nesta linha — o .mjs já estava declarado (C-PROVA-RECOLLECTION);
                       a prova nova entrou em C-PROVA-PARIDADE. Em 11 das 23 branches
                       remotas que têm o .mjs ele continua sem dono: são todas anteriores
                       à unificação e ficam resolvidas ao juntar unificacao-v1 (não tocadas)
TESTS                  prova nova 15/0 · incrementalidade_test 26/0 · recollection_test 31/0 ·
                       paridade_test 32/0 · paridade_duas_rodadas 13/0
MUTATION               prova nova: 5 mutantes no coletor, 5 executados (marca), 5 mortos ·
                       red team: 12/12 mortos · red team estrito: 12/12 mortos pela suíte dona
FINAL_HEAD = REMOTE_HEAD   conferido após o push (o hash vai na mensagem de entrega: um ficheiro não contém o hash do commit que o contém)
SYSTEM_MAP_CHECK       PASS — cadeia REGERAR (CADEIA=OK) + VALIDAR; P8 e P9 PASS
```

## O que a prova nova acrescenta

`provas/recollection_http_local.mjs` liga o que a prova de duas rodadas desliga: o
coletor chama o `curl` de verdade contra um servidor HTTP em 127.0.0.1, e os pedidos
são contados pelo SERVIDOR. A saída para a internet fecha-se pelo ambiente (proxy para
uma porta fechada; só 127.0.0.1 fica de fora) e a prova confirma que fechou:
`EGRESS_IP = NAO SEI` e um curl à internet devolve `000`.

| rodada | o que o servidor serve | pedidos | resultado |
|---|---|---|---|
| R1 | boletim de 01–07/09 | 1 | NEW=1 |
| R2 | o mesmo endereço (visitas/hora/token mudaram) | 0 | SKIPPED_KNOWN=1 |
| R3 | boletim de 08–14/09 num endereço novo — **503** | 1 | FAILED=1, nada gravado como documento |
| R4 | o mesmo, servidor de volta | 1 | NEW=1 — retomado |
| R5 | MUTABLE declarado; só ruído | 1 | SEEN_AGAIN, 0 objectos RAW |
| R6 | «bassa» → «ALTA» | 1 | CHANGED=1, versão nova, a anterior intacta |

Mutantes (cada um confirmado a correr por um ficheiro-marca que o próprio código
mutado escreve; cache de compilação do Node desligada; restauro conferido):

| mutante | onde morreu |
|---|---|
| a falha 503 gravada como NEW_DOCUMENT | R3 e R4 |
| a versão nova reusa o id da anterior | R6 |
| guardarRaw sem a guarda de existência (sobrescreve) | R5 e R6 |
| o salto SKIP_KNOWN desligado | R2 e o censo |
| o veredicto «só ruído» desligado | R5 |

## Erros meus, corrigidos antes da entrega

A primeira corrida da prova deu 2 falhas, e as duas eram minhas, não do coletor:
`DETAIL_NEW` conta a decisão de ir buscar (antes do transporte), não o documento
nascido; e servir os mesmos bytes num endereço novo é, correctamente, o mesmo
documento (a identidade vem do conteúdo). A prova passou a usar `NEW_DOCUMENTS` e um
boletim de outro período.

## O que NÃO se provou

- ETag / Last-Modified (304): o coletor não os pede nem os grava — não há o que provar.
- Timeout de rede: só o 503 foi exercitado.
- Fonte com índice: a prova usa uma STATIC_ROUTE (um endereço por corrida).
