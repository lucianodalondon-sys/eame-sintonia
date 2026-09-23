# D1 — PORQUE É QUE O DETECTOR CHAMA CAPA A NOTÍCIAS (e a D14, opção C)

Branch `detector-erro-v1` (de `quarentena-naosei-v1` @ c37c2423). Sem rede, sem Collection,
nada na Sala. Validação cega sorteada e **commitada antes** de olhar para as páginas
(`medidas/D1-VALIDACAO-CEGA-V1.json`, b626111a): 23 páginas do controlo, sem as 4 já vistas.

## As 10 notícias chamadas capa (6 original + 4 controlo)

`medidas/D1-CAUSAS-10-PAGINAS-V1.json`. A régua: CONTENT se ≥ 800 caracteres em `<p>` e ≥ 35%
do texto; NAVIGATION (capa) se < 40 caracteres por link.

* **A · o menu do sítio conta como se fosse a página — 9/10.** A maioria dos links vive em
  `<nav>/<header>/<footer>` (280/300, 171/194, 110/179…); no corpo há 5–15.
* **B · o corpo não chega a 800 caracteres em `<p>` — 8/10** (notícia curta, ou texto em
  `<div>`; 1 vídeo sem parágrafos). Um caso (IT-T2-030) tem 2798 em `<p>`, mas o menu faz disso
  menos de 35% do texto.

## Duas propostas, medidas — NÃO aplicadas

`medidas/D1-MEDICAO-DETECTOR-MOLDURA-V1.json`. As duas só mexem na fronteira CAPA↔NÃO SEI; a regra
de MATÉRIA fica intacta.

| | original | controlo (desenv.) | controlo cego |
|---|---|---|---|
| **V2** (links da moldura fora): notícias chamadas capa | 6 → 1 | 4 → 0 | 0 → 0 |
| V2: capas chamadas matéria | 37 → 37 | 6 → 6 | 4 → 4 |
| V2: capas verdadeiras → quarentena | +34 | +6 | +2 |
| **V3** (links e texto da moldura fora): notícias chamadas capa | 6 → 3 | 4 → 1 | 0 → 0 |
| V3: capas chamadas matéria | 37 → 37 | 6 → 6 | 4 → 4 |
| V3: capas verdadeiras → quarentena | +18 | +3 | +2 |

Ambas cumprem «FALSE_LISTING_AS_ARTICLE não sobe». Mas ambas **enchem a quarentena de capas
verdadeiras** (V2: 34 capas para recuperar 9 notícias; V3: 23 para 6). A D14 diz que isso volta ao
dono — **APLICADA = NO**; o detector (`curadoria/retrato_html.py`) ficou intocado.

## D14 — opção C, implementada e DESLIGADA

Livros do portão copiados às 08:25Z: só 10 das 133 fontes dos gabaritos passam os 4 passos.
**A C recupera 0/6 (original) e 0/4 (controlo)** — todas as notícias barradas vêm de fontes mal
configuradas — e poria **3 capas verdadeiras** em quarentena. Projeção, não medição: depois do
deploy da B2, IT-T5-090 (ISTAT) fica bem configurada e a C recuperaria 1/4.

`D14_C_LIGADA = False`. A capa barrada guarda fonte, raw_asset_id e sha256 (condição 2); o painel
conta barradas vs retidas por fonte bem/mal (condição 4). **Falta para ligar:** o regresso
AUTOMÁTICO à porta quando o contrato da fonte passar os 4 passos (condição 2) — não construído.

## Testes

`tests/test_d1_detector_d14.py` 9 + Q1 27 = 36 verdes; mutação 7/7.
