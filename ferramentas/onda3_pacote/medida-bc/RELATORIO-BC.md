# Quantas fontes terá a próxima Big Collection — ensaio consolidado (25/09/2026)

Só leitura. Cópia fiel do vivo `servico-20260923-0923 @ b607c9af` + os 16 livros do disco; rede FECHADA (D41.3);
0 pedidos. Junção consolidada local `medida-bc-v1 @ ae2d7435` = produção + onda3-pacote-v1 (local 0cc1dc56:
contrato-44 v1/v3, REVISAO-15, hr6-v1 + D51, ordens-63-v2 D52; sem receitas-182) + receita-t8-v1 (59e23365).
Conflitos: só ficheiros gerados do mapa (ficou a versão da produção); 0 de código.
LEGACY-99: só o bloco A, e só em «mostrar» (a ferramenta `importar_do_coletor.py` de legacy-99-v2 trazida para
a cópia; nenhum código juntado). Script: `ensaio_bc.sh`. Desfazer provado: 0 ficheiros de código ≠ vivo, livros = foto.

| | hoje (vivo) | com tudo |
|---|---|---|
| prontas (`micro_coleta plano`) | **29** | **61** (+32, 0 perdidas) |
| coorte congelável (`coorte_unica`) | — | **60** (fica fora a ISTAT, D45) |
| CORREM numa onda (`onda_web --so-plano`, teto D38) | — | **36** (24 saltam por teto de domínio, 1 parcial) |
| pedidos previstos | — | **150** · máximo 5 por domínio · prova-teto PASS |

| universo | prontas hoje | prontas com tudo | coorte | correm |
|---|---|---|---|---|
| T2 | 7 | 7 | 7 | 6 |
| T3 | 0 | 1 | 1 | 0 |
| T5 | 6 | 10 | 9 | 3 |
| T7 | 13 | 20 | 20 | 17 |
| T8 | 0 | 13 | 13 | 1 |
| T9 | 0 | 1 | 1 | 1 |
| T10 | 3 | 3 | 3 | 3 |
| T12 | 0 | 6 | 6 | 5 |
| **janela D29 (T2+T3)** | **7** | **8** | **8** | **6** |
| **total** | **29** | **61** | **60** | **36** |

União por SOURCE_ID: 0 repetidos nas prontas (antes e depois) e na coorte. Listas completas em `BC-LISTAS.json`.

**Regra da janela D29 usada (minha, declarada):** universo T2 (clima/agrometeo) ou T3 (fitossanitário). A D29 não
tem campo próprio nas fontes; outra regra daria outro número.

**Saltam por teto (24):** 12 de T8 (quase todas edagricole.it), 5 de T5 (enea.it, crea.gov.it…), 3 cia.it, e
IT-T12-131, IT-T2-146, IT-T3-023, IT-T5-080 · parcial IT-T7-118. Não são perdas: correm na onda seguinte.

**O que depende do robô com rede (NÃO somado acima):**
- bloco A: IMPORTA 62 (21 páginas + 41 YouTube), FICA 11. Sem canário = **0 prontas**. A LEGACY-99 v2 mediu,
  com rede, 11 das 21 páginas a chegar a elegíveis; os 41 YouTube precisam da rota VIDEO (v3), fora desta conta;
- HR-6: IT-T7-174 (+1 se o canário passar);
- REVISAO-15: até +3 READY, que não ficam prontas (sem contrato no coletor).

Provas (sha256): `BC-TABELA.txt` 88ecf002… · `BC-LISTAS.json` 385a92dd… · `BC-A-importar-mostrar.txt` 05cdfb08… ·
tudo em `SHA256SUMS.txt`.
