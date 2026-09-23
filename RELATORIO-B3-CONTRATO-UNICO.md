# B3 — A PORTA DE CONTRATOS DO BOT E A REVALIDAÇÃO DAS ELEGÍVEIS

Branch `contrato-unico-v1`. Serviços vivos intocados. Prova: `curadoria/B3-CONTRATO-UNICO-V1.json`.
D10 = **opção A** com as 4 condições do dono.

## 1. A porta de contratos — o pacote G1 estendido

O G1 (enxertado de `origin/unificacao-v1`, ficheiro a ficheiro, sem merge) ganhou o
**bloco 3 — CONTRATO ÚNICO**: `--livro-bot=… --d10=A`. Só as 7 da D10; só com canário
ROUTE_PROVEN da aquisição que fica; muda só `ACQUISITION` e acrescenta `CONTRATO_UNICO`
(ORIGEM, PROVA, aquisição anterior, `PRECISA_DE_REMEDIR`); nunca acrescenta fonte; sem
prova salta (vale C); ledger com `DECISAO = D10`.

Ensaio em cópia (fotografia 06:15Z): **1.ª passagem 6 APLICA, 2.ª passagem 0**.
`dono_do_contrato()` = None para as 6; IT-T5-049 (sem prova) e IT-T5-041 (o bot não a
tem) continuam sem dono e saem do portão.

**Das 7, 6 passam os 4 passos** (reprodução sem rede dos dados M3 pela régua real;
não substitui a re-medição do bot). IT-T5-049 falha: não há matéria aberta com corpo.
Ressalva: READY ≠ relevante — Riunite, Chianti e Balsâmico são marca (missão 4).

## 2. Revalidação periódica — o que torna a DEMOTION possível sem humano

Não existia: o bot só re-media o que falhou. Nível **0b REVALIDAR** no
`gatilho_discovery.talvez_alimentar`: ELIGIBLE com prova > **7 dias** (proposto e
declarado — não há prazo na Bíblia nem no know-how) ou com contrato novo da D10 →
`VALIDATE_ROUTE`. Guarda anti-eco (T02077 mostrou que «BLOCK sem contrato» não
escreve no livro), 5 por volta, sem rede própria.

## Testes

20 novos (`test_contrato_unico`), 23 do G1 e 109 vizinhos verdes; mutação 12/12.
