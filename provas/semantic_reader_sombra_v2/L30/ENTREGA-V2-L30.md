ENTREGA — SEMANTIC READER V2 EM SOMBRA — LOTE 30 (01/10)
EXPERIMENTAL / NAO_PARA_CLIENTE

VEREDITO: REPROVADO. Os 313 NÃO foram rodados. Frente PARADA (decisão do dono: sem V3 automática).

Regras congeladas ANTES da 1ª rodada: commit 2330d623d (REGRAS-TEMPORAIS-V2.md sha caf6515f…, leitor_v2.py
sha b35a3dc7…). As duas rodadas registram esses mesmos shas. Régua = placar da V1 copiado sem mudança
(placar_v1_congelado.py sha 2320203c…, igual a 5fee44290). Lote 3827c7d7…cd62, cópia 943a20f8…2e71.

ALVOS_RECUPERADOS = 9/20 (régua >= 14)   -> FALHA   (V1: 11/20)
DATA_FALSA        = 0                    -> OK      (V1: 0)
REGRESSAO         = 4 (L30-21,23,24,25)   -> FALHA   (V1: 4 — 22,23,24,25)
RODADA_1=RODADA_2 = NÃO, 1 item (L30-20) -> FALHA   (V1: 5 itens)
ARMADILHAS 4/4. Custo US$ 0,58/item (5 votos), 607 s + 273 s; total US$ 34,91.

CAUSAS RESTANTES (20 alvos)
1. Data do fato escrita SEM ANO — 6 alvos (02, 04, 07, 13, 14, 19). A regra do dono proíbe inferir data
   ausente, portanto NÃO SEI é correto. Com esta regra, o teto da régua é 14/20, e só se tudo o mais passar.
2. Data da EDIÇÃO do boletim vs data da observação — 4 alvos (08, 09, 16, 20). O modelo as classifica
   EDITION_PERIOD (o texto não liga a data às observações). A V1 contava isso como recuperado. Decisão do dono:
   a data da edição de um boletim fitossanitário é ou não é tempo do fato?
3. Extrator de candidatos não pega intervalos de ano ("triennio 2024-2026") — 1 alvo (06).
REGRESSÕES
- L30-21: o valor congelado ("09 - 15 settembre 2026") é cabeçalho de previsão, publicado em 09/09.
  A V2 devolve a semana observada ("Dal 31-08 al 06-09-2026"), seguindo a mesma lógica do controle L30-22.
  Conflito lote × regra, registrado ANTES da rodada.
- L30-23/24/25: o valor congelado é um ano solto ("raccolta/stagione 2026", "2026"), dentro de textos
  comparativos. A V2 fica dividida (3/5) ou responde NÃO SEI.
INSTABILIDADE: caiu de 5 para 1 (L30-20: 4/5 votos numa rodada, 3/5 na outra).

Não tocado: runtime, Sala, RODADA-VIVA, pote, LOCK-PESADO. Rodada paralela não autorizada = NAO_CONTA (não usada).
Ensaio de 2 itens antes da rodada (ENSAIO-2-ITENS-NAO-CONTA.json) = NAO_CONTA.
