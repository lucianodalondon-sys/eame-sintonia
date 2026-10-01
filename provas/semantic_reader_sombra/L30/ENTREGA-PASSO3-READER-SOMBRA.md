ENTREGA PASSO 3 — SEMANTIC READER EM SOMBRA — LOTE 30 (01/10 ~11:30)
EXPERIMENTAL / NAO_PARA_CLIENTE

VEREDITO: REPROVADO no lote 30. Os 313 NAO foram rodados (regra do dono: so se passar).

SHA: claude/semantic-reader-sombra-v1 823ad7f20 (ls-remote = 823ad7f200399ccec328c5174e9b35d23052da19), base c5db5eedd.
Codigo: provas/semantic_reader_sombra/leitor.py (LLM claude-opus-5, prompt SR-SOMBRA-PROMPT/v1 sha 78963c0a; ancora literal feita por codigo)
        provas/semantic_reader_sombra/placar.py (deterministico)
Lote: LOTE-30-SEMANTIC-READER-SOMBRA.json sha 3827c7d7...cd62 (conferido). Copia: SALA_ATUAL.json 943a20f8...2e71 (conferida; 30/30 TEXTO_SHA256 iguais).
Saidas (fora do Git): sintonia-sala-italia/intelligence-experimental/SEMANTIC-READER-SOMBRA-L30/
  RODADA-1.json b14bb824..., RODADA-2.json 04e3d36f..., PLACAR-L30.json 1b1b603a... (SHA256SUMS.txt)

ALVOS = 11/20 (criterio >=14)       -> FALHA
CONTROLES = 2/6                      -> FALHA
ARMADILHAS = 4/4
DATAS_FALSAS = 0
REGRESSOES = 4 (L30-22, 23, 24, 25)  -> FALHA
RODADAS_IDENTICAS = NAO (5 itens: L30-05, 06, 09, 17, 25) -> FALHA
CUSTO_ITEM = US$ 0,13 ; ~17.900 tokens entrada / ~200 saida ; ~15 s
TEMPO_TOTAL = 75 s (R1) + 84 s (R2), 6 em paralelo ; custo total US$ 7,95

Nao tocado: runtime, Sala, RODADA-VIVA, pote cliente, LOCK-PESADO.
comparar_313: nao rodado (313 nao autorizado).
FIM
