# B1 — PONTE AUTOMÁTICA: PROMOTION E DEMOTION COM DADOS REAIS

Branch `ponte-prova-viva-v1` (de `origin/unificacao-v1`). Só leitura, **por cópia**:
log, estado e livros da ponte (`ponte-curador-v1`) e do bot (`source-curator-service-v1`)
copiados às 05:14Z para `~/sintonia-gabarito/B1-SNAPSHOT-20260923T051430Z/`, com
sha256 no JSON. Nenhum serviço vivo foi tocado. Prova: `curadoria/B1-PONTE-PROVA-VIVA-V1.json`.

## Travessias reais

106 travessias (104 desde o arranque do PID 14960), 2 arranques. **Em todas, o
portão ficou 8 → 8: ENTRARAM 0, SAIRAM 0.** Latência bot → ponte: mediana 3,8 s;
máximo 12 703 s na 1.ª travessia, que apanhou decisões anteriores ao arranque.

No livro, dentro da janela: 35 fontes entraram em READY e 3 saíram de READY.
Nenhuma mexeu o portão:

* as 35 são **READY_LEGACY** — 23 chegaram sem a prova do bot importada para as
  evidências que o portão lê, 12 sem contrato no livro de contratos do portão; o
  próprio bot escreve «PASS_PARCIAL» e promove;
* as 3 que saíram (IT-T12-086, IT-T12-095, IT-T5-082) não eram elegíveis.

## Invariantes

| invariante | estado |
|---|---|
| o portão lê a ponte, não o git | **OK** — `avaliar` lê o livro do disco; o único `git show` está num relatório |
| nunca promove fonte RETIRADA_POR_DECISAO (D9) | **NÃO IMPLEMENTADO** — nenhum estado nem guarda; IT-T12-086 (Saúde) entrou em READY na janela |
| nunca sem canário do contrato actual | **PARCIAL** — sem `INTEGRADO_EM` a régua assume contrato actual; IT-T5-041 é elegível só por isso |

Divergência: o bot tem IT-T5-041 em CAPABILITY_BLOCK (20/09); o livro do portão
tem READY (21/09, listagem provada na bancada da ponte); o portão aprova-a.

## Gates

`BRIDGE_AUTOMATIC = YES` · `PROMOTION_PROVEN = NO (não observado; hoje estruturalmente
impossível para promoções do bot)` · `DEMOTION_PROVEN = NAO_OBSERVADO`.

## Prova viva proposta (NÃO executada)

* **DEMOTION** — uma revalidação do bot a IT-T5-041 (crpv.it → rinova.eu, falha
  natural medida na M3). Esperado: ELIGIBLE 8 → 7 com SAIRAM=[IT-T5-041] no log.
* **PROMOTION** — não há prova segura sem código: faltam a importação da prova,
  o contrato no livro do portão e os quatro passos DETAIL/v1 na prova do bot.
