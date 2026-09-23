# Para o runbook da X2 — os passos sociais do dia da virada (SOC2 + SOC3)

> Declarado pela SOC3 (2026-09-23) a pedido da coordenação. Nada disto corre sozinho: cada passo é um
> comando, com o que ele muda e como se confere. A ordem importa.

| # | Comando | O que muda | Como se confere |
|---|---|---|---|
| 1 | `bash motor/cadeia_canonica.sh migrations <URL>` | aplica a **033** (`lapide_de_retencao`) — tabela nova, não mexe em nenhuma existente | `select to_regclass('public.lapide_de_retencao')` não é nulo |
| 2 | `py scripts/desbloqueio/aplicar_desbloqueio.py --livro=… --tabela=… --rota-scrap=SOC2 --escrever` (junto com os blocos 1-3 do G1) | 50 contratos YouTube: livro → `SCRAP_FASE`; tabela → `COLETADO_POR` (ledger `D17.4`) | 2.ª passagem = 0 alterações |
| 3 | `py curadoria/ensaiar_qualify_youtube.py --reabrir` (serviço do Curator parado, ou pelo dono dele) | as 11 tarefas QUALIFY YouTube barradas pela frase antiga voltam a PENDING | `REABERTAS 11`; na volta seguinte o worker aplica a regra nova + D21 |
| 4 | aplicar no `pedido/receitas.py` o bloco `promover_o_scrap` (engenheiro do Scrap; `RELATORIO-SOC3`) | fase do Scrap → executor do Scrap em qualquer território | `py provas/roteamento_youtube_proposta.py` → `PROPOSTA {scrap-colheita, OK: 50}` |
| 5 | **diário**, na máquina onde o armazém local vive: `py guarda/retencao_youtube_api.py --checar --url=<memória operacional> --raiz=<raiz do armazém>` | nada (só lê) | `RETENCAO_30D = PASS`; `FAIL` = há dado da API vencido ou lápide com byte vivo; `NAO_SEI` = observação antiga cuja rota não se prova |
| 6 | quando o passo 5 disser `FAIL`: `py guarda/retencao_youtube_api.py --varrer --aplicar --operacional --url=… --raiz=…` | apaga o BYTE, escreve a lápide, `preserved=false`, apaga o texto na Sala e nas tabelas sociais | passo 5 volta a `PASS` |

⚠️ Passos 5-6 cobrem o **armazém local** (onde o orquestrador escreve hoje). Se o byte também foi
enviado ao bucket `raw` da Supabase, esse não sai: nenhum armazém desta casa tem verbo de apagar, e
dar-lho é decisão do dono do armazenamento (ver RELATORIO-SOC3, «o que falta»).
