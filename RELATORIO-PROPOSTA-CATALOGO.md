# PROPOSTA DE CORRECÇÃO DO CATÁLOGO T2/T12 — para o dono decidir (D5)

Missão 3d · branch `catalogo-proposta-v1` · 2026-09-23. **Nada foi aplicado** ao
catálogo, à porta (`admissao/`) nem à Sala.

Ficheiro: `curadoria/PROPOSTA-CATALOGO-V1.json` (gerado sem rede por
`medidas/montar_proposta_catalogo.py`). Provas: `curadoria/CATALOGO-PROVA-V1.json`
(55 páginas de entrada, egresso IT 51/51, 107 pedidos, ≤3 por sítio, regra
commitada antes em 8d34dc9d), gabaritos V2/V3, acervo versionado e o canário da
3b. Bytes fora do Git em `~/sintonia-gabarito/`.

## Âmbito

189 fontes: as 162 T2/T12 do livro `origin/lote-76-v1`, as 26 T2/T12 que só estão
no Atlas, e IT-T7-043. **Uma ACÇÃO só existe com prova de página**; sem página ou
com dúvida é UNKNOWN, e o que o nome sugere vai à parte (`INDICIO_DO_CATALOGO`).

| acção | T2 | T12 | T7 |
|---|---|---|---|
| MANTER | 28 (7 duplicam uma ficha do Atlas no mesmo sítio) | **6** | — |
| MUDAR_PARA_Tx | T5: 1 · T10: 1 | T7: 2 · T2: 2 | T9: 1 |
| RETIRAR_DO_UNIVERSO | 8 | **39** | — |
| UNKNOWN | 25 | 76 | — |

As 3 fontes em gaveta errada: IT-T2-030 Nomisma → T10 · IT-T7-043 Agrofarma → T9 ·
IT-T12-015 APPA Trento → UNKNOWN (é um canal YouTube não aberto; o indício diz
T2). As 4 não agrícolas: IT-T12-057 e IT-T12-074 → RETIRAR (com prova);
IT-T12-012 e IT-T12-014 → UNKNOWN (canais YouTube gerais da Região, não abertos).

## Os três números

1. **T12 agrícolas de verdade, provadas: 6** — CIA, CIA Toscana, MASAF, Regione
   Veneto (agricoltura), Pianeta PSR, Agricoltura Campania. Mais 19 com indício
   agrícola e sem prova (canais YouTube, entradas que caem no portal geral,
   páginas sem corpo).
2. **Positivos atingíveis só com essas:** T12 — teto de **18** por ida (6 × 3);
   em 3 idas deram **9**. T2 — 21 fontes mantidas sem duplicado, teto 63 por ida;
   em 3 idas deram **13**.
3. **T12 chega a 20 sem fontes novas? NÃO numa ida** (teto 18 < 20). Só
   acumulando idas ao longo do tempo, sem garantia.

Fontes reais de política agrícola que faltam (verificado no livro, no Atlas e
nas candidatas): **AGEA** (só como candidata via SIAN) · **CREA-PB** (ausente; o
CREA tem 14 centros, todos T5) · **Rete Rurale** (só o canal YouTube e a revista
Pianeta PSR) · **ISMEA** (no Atlas como T10) · **Agriregionieuropa** (ausente) ·
**MASAF comunicados** (a fonte existe, falta a entrada de notícias). E Coldiretti,
CIA nacional, Confagricoltura e Copagri **existem, mas em T7** — pela lei D2, os
itens de política delas podem ir para T12 por REROUTE sem mudar a gaveta da fonte.
