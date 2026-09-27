# RELATÓRIO — MISSÃO LD2 · FECHAR O GATE LISTING/DETAIL (V1)

Branch `listing-detail-v2`, a partir de `origin/listing-detail-v1 @ c6a99f0b`. Motor: `claude-opus-5-5`.

```
COLLECTION NÃO CORREU · NADA NA SALA · SERVIÇOS VIVOS INTOCADOS
curadoria/retrato_html.py e os gémeos = INTOCADOS (a V1 não dominou nos dois gabaritos)
Rede: 1 site (IT-T11-010, 3 pedidos) + 50 sites do controlo (≤ 3 pedidos cada), egresso IT medido antes de cada site
Prova: scripts/detector_capa/LISTING-DETAIL-GATE-V2.json
```

## A ORDEM, PARA O CONTROLO SER INDEPENDENTE

| passo | commit | hora (UTC) |
|---|---|---|
| receitas V3 e IT-T11-010 decididas e **congeladas** | `64c3beb7` | 06:05:48 |
| recolha do controlo (50 sites nunca usados) | — | depois |
| rótulos do controlo gravados, **antes de medir** | `922f2230` | 06:16:59 |
| medição | — | depois |

## 1 — IT-T11-010: NÃO SEI

Pelo mesmo método do G1: saída IT medida antes, robots da casa, **3 pedidos**
(robots, listagem, notícia).

* A notícia `…/it/news/news/5649/in-un-mondo-di-policrisi…` foi lida: é matéria.
* A listagem `…/it/educazione-ambientale/notizie` tem **3 links** com a forma da notícia,
  porque o site pagina de 3 em 3. O G1 exige **≥ 10**. Não baixei a régua, e o teto de
  pedidos a este site esgotou-se.
* **Falta:** uma visita autorizada à mesma listagem com uma página maior
  (`dp-1-per-page`), ou outra listagem do site com ≥ 10 notícias.

## 2 — AS 14 MATÉRIAS FORA DA RECEITA: 2 COM PROVA, 12 NÃO SEI

Foi usado o mesmo método do 6-PREP-d (`por_fonte`), o mesmo guarda e o mesmo pacote, com o
mesmo ledger. O aditamento é o ficheiro `curadoria/PROPOSTA-RECEITAS-V3.json`, lido por
uma linha a mais em `aplicar_desbloqueio.py`.

* **IT-T2-039** arpae `/it/notizie/<slug>`: 30 dos 55 links da listagem que o G1 provou.
* **IT-T5-049** di3a `/it/notizie/<slug com %XX>`. ⚠️ **Risco:** 2 dos 5 exemplos parecem
  páginas de categoria.
* **12 NÃO SEI**, com o motivo do próprio método:
  * família com menos de 2 links (ersaf, tartufo, etvilloresi, assofertilizzanti, consorziopiave);
  * o guarda recusou, por o padrão também casar navegação (winenews, arpalombardia, arpa sicilia,
    agroalimentarenews, calabriaeuropa);
  * esqueleto que não se reproduz (regione puglia);
  * IT-T11-010.
* O pacote (G1 + V3) numa cópia do livro vivo fez **75 alterações** e depois **0**.

## 3 — O GABARITO DE CONTROLO

`scripts/detector_capa/GABARITO-CONTROLO-LD2.json`: **49 capas · 20 matérias**, de 23 domínios
(14 nas matérias). Ficaram de fora 8 VAZIAS e 1 AMBÍGUA (atrás de muro de assinatura).

* **50 sites cujo domínio nunca apareceu** em nenhuma recolha anterior, escolhidos pelo
  `colher_gabarito.py` sem olhar para o `LINK_PATTERN`. Saída **IT em 49/49**.
* ⚠️ 8 das 20 matérias são do grupo Edagricole (o mesmo sistema de site).
* **Segunda leitura:** um agente separado leu às cegas 10 páginas. **Concordou em 9/10.**
  Discordou da **#34** (Agrinsieme): eu disse matéria, ele disse capa e marcou-a como caso-limite.

## 4 — A TABELA

| regra | original (146): capa que passa | original: matéria barrada | controlo (69): capa que passa | controlo: matéria barrada |
|---|---|---|---|---|
| **ACTUAL** | 63/109 | 6/37 | **28/49** | **4/20** |
| **V1** | 20/109 | **7/37** | 5/49 | **5/20** |
| V2 (desacordo → pessoa) | 37/109 | 3/37 | 10/49 | 4/20 |
| SÓ_MORADA | 4/109 | 13/37 | 0/49 | 15/20 |

* **A V1 perde por uma matéria nos dois gabaritos**, e nos dois casos é a página que o
  contrato declara como índice e que é um artigo: #28 (IT-T11-010) e #34 (Agrinsieme).
  **O custo da V1 é igual à taxa de `INDEX_URL` errados nos contratos** (1 em 47 fontes no
  controlo).
* Com o rótulo do segundo leitor para a #34, a V1 dominaria no controlo. O rótulo foi
  congelado antes de medir e **não se muda**.
* **O ACTUAL deixa passar 57% das capas também em dados independentes** (28/49). Confirma a
  6-PREP-c.
* A V2 domina no controlo e nos totais do original. Mas, na fatia não circular do original,
  barra 3/22 contra 2/22 do ACTUAL, e as 3 são erros de receita (#28, #51, #108). Fica como
  informação para o dono. **Não foi pedida e não se aplica.**

## 5 — NÃO SEI: PASSA OU VAI PARA UMA PESSOA?

A decisão é do dono; ficam aqui as opções medidas (juiz ACTUAL):

| | original | controlo |
|---|---|---|
| **A — passa (hoje)**: capas que passam sem ninguém ver | 63/109 | 28/49 |
| **B — pessoa lê**: capas que passam sem ninguém ver | 37/109 | 10/49 |
| B: páginas para uma pessoa ler | 34 de 146 (26 capas + 8 matérias) | 19 de 69 (18 capas + 1 matéria) |
| B: matérias atrasadas à espera de uma pessoa | 8/37 | 1/20 |

A opção B não barra nenhuma matéria a mais: atrasa-as. **Precedente na casa:**
`curadoria/ready_split.py` diz que NÃO SEI não vira READY_CURRENT por conveniência, e a
COL-LAW-034 da Bíblia diz que identidade NÃO SEI não passa. Nenhum dos dois trata do
detector; a pergunta vai para o bot Luciano.

## ENTREGA

```
IT_T11_010                 = NAO SEI (listagem com 3 < 10 links; falta 1 visita autorizada)
CONTROLO                   = 49 capas / 20 materias / 23 dominios (14 nas materias); 2.a leitura 9/10 (discorda #34)
V1_APLICADA                = NO — perde por 1 materia no original (#28) e no controlo (#34)
RECEITAS_NOVAS_14          = 2 com prova (IT-T2-039, IT-T5-049 com risco) / 12 NAO SEI
TESTS                      = 36/36 (test_ld2_aditamento, test_medir_apos_receitas, test_aplicar_desbloqueio)
MUTATION                   = 3/3 mortos (pacote sem V3 · materia como entrada · sem recurso a listagem antiga)
EGRESS                     = IT em 50/50 sites visitados (Palermo), antes de cada site
LISTING_DETAIL_GATE_PROVEN = NO
OPCOES_NAO_SEI             = A passa (63/109 · 28/49 capas passam) · B pessoa (37/109 · 10/49; 34/146 · 19/69 para ler)
```
