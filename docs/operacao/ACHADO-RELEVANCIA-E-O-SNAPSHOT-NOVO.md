# ACHADO ABERTO — a lei de relevância e o snapshot novo

Ao trazer o Portal atual, o `meeting-intelligence-snapshot.json` veio com ele.
A lei (`leis/adama_relevance.py`) é **byte a byte idêntica** nas duas linhas.
Mesmo assim, a classificação muda:

    snapshot da linha técnica  ->  {'A': 13, 'B': 21, 'C': 8, 'D': 1, 'E': 0}
    snapshot do Portal atual   ->  {'A': 17, 'B': 21, 'C':  4, 'D': 1, 'E': 0}

O total continua 43. Quatro casos que eram `C` (RELEVANCE_C_NO_LINK) passaram a
`A` (RELEVANCE_A_PROVEN): o snapshot novo traz ligação a produto onde o antigo
não tinha.

`tests/test_adama_relevance.py` está preso aos números antigos, e é **igual nas
duas linhas** — logo ele JÁ REPROVA em `release/canonical`. Não foi esta missão
que o partiu; foi esta missão que o tornou visível.

    O TESTE NÃO FOI ALTERADO. Mudá-lo para o gate passar seria assinar que
    alguém conferiu os 43 casos novos, e ninguém conferiu.

Quem decide: o dono da lei de relevância. A pergunta é uma só — os 4 casos que
subiram de C para A subiram com razão?
