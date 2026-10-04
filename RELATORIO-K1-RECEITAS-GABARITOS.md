# K1 — RECEITAS DAS FONTES DOS 2 GABARITOS, E AS TRÊS POLÍTICAS RE-MEDIDAS

Branch `receitas-gabaritos-v1` (de `detector-erro-v1` @ 260722dc). Serviços vivos intocados (só
cópias); Collection não correu; nada na Sala. Egresso **IT 13/13** (149.22.91.171, medido antes de
cada sítio), ≤ 3 pedidos por sítio, robots pela casa.

## 1. Porque as fontes não passam os 4 passos

Primeiro achado: nos livros do portão de hoje, **105/133** fontes dos gabaritos nem têm contrato —
está no bot. Por isso tudo foi medido numa **cópia pós-B2** (uma volta real da ponte B2 sobre os
livros vivos das 09:40Z: 493 contratos e 122 provas atravessam; portão 8 → 23). Nela:

| causa | fontes |
|---|---|
| passa os 4 passos | 20 |
| LEGACY — falta ITEM_ABERTO + BODY_UTIL (prova antiga, sem retrato) | 12 |
| LEGACY — falta também DETAIL_LINKS | 11 |
| LEGACY — só BODY_UTIL / outro | 4 |
| nunca promovida — canário falhou | 47 |
| nunca promovida — espera canário | 26 |
| nunca promovida — bloqueio / retry / sem contrato ainda | 13 |

## 2. Receitas V4 (mesmo método da V3 / 6-PREP-d, sem alteração)

`scripts/receitas/propor_receitas_v4.py` = a V3 da LD3 + as páginas do gabarito de controlo LD2.
**13 com prova / 100 NÃO SEI.** 9 dessas fontes já tinham receita V1 (o pacote aplica a primeira);
**4 são novas** (IT-T5-103, IT-T5-104, IT-T7-059, IT-T7-125). O G1 lê V3 e V4 e confere o sha256
também nos manifestos LD2. Ensaio em cópia: 1.ª passagem 71 alterações, 2.ª passagem 0.

Canário (receita aplicada, na cópia) + o juiz dos 4 passos: **5 passam** (IT-T12-024, IT-T12-039,
IT-T2-050, IT-T7-125, IT-T9-018); 7 resolvem a rota mas o item não tem corpo útil ou a lista sai
vazia; IT-T7-047 UNKNOWN (robots em timeout). **Fontes nos 4 passos: 20 → 25.**

## 3. As três políticas, depois das receitas (`curadoria/K1-MEDICAO-V1.json`)

| | original (109 capas / 37 notícias) | controlo desenv. (31/15) | controlo cego (18/5) |
|---|---|---|---|
| ACTUAL — capas que entram · notícias barradas · retidas | 37 · 6 · 8 | 6 · 4 · 1 | 4 · 0 · 0 |
| **C ligada** — notícias barradas | 4 (−2) | 3 (−1) | 0 |
| C — capas a mais na quarentena | +3 | +1 | **+4** |
| **V1 com a régua a mandar** — capas que entram | **30 (−7)** | **5 (−1)** | **3 (−1)** |
| V1 — notícias barradas / retidas | 6 / 8 (=) | 4 / 1 (=) | 0 / 0 (=) |

**RECOMENDAÇÃO_C = NÃO ligar.** Recupera 3 notícias por 8 capas verdadeiras na quarentena, e na
validação cega é só custo. Por isso o regresso automático (condição 2 da D14) **não foi construído**.

**V1 com a régua a mandar** é a única política que melhora sem custo medido: 9 capas a menos a
entrar, 0 notícias perdidas. A V1 é da LD3 e não foi aplicada — é decisão.

## Dívidas

(i) limiares do detector também em `coleta/retrato_html.mjs` (outra linha) — declarada no System
Map, na peça C-DETECTOR-CAPA-GABARITO. (ii) regresso automático à porta — não construído (a C não
passa as condições).

## Testes

`tests/test_k1_receitas.py` 13 + G1 23; mutação 9/9.
