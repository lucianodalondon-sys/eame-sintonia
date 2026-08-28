# ASK SINTONIA — BENCHMARK

O deck promete *"a way to query the evidence layer"* (SLIDE 5). Antes de qualquer interface,
é preciso provar que a camada **é consultável** — e que **sabe recusar**.

**Não é chat.** É consulta determinística sobre evidência preservada.
Execução: `scripts/ask_sintonia.py` · Dados: `../../data/samples/ASK-SINTONIA-benchmark.json`

---

## PLACAR

| Resultado | n | % |
|---|---|---|
| **ANSWERED CORRECTLY** | **12** | 60% |
| **REFUSED CORRECTLY** | **8** | 40% |
| **WRONG ANSWER** | **0** | **0%** |
| UNEXPECTED REFUSAL | 0 | 0% |

> **Recusa correta é resultado positivo.** O erro grave é inventar resposta. Zero.

## AS 20 PERGUNTAS

| id | domínio | pergunta | esperado | evidência / motivo da recusa | o que destravaria |
|---|---|---|---|---|---|
| B01 | REGULATION | Que atos da UE de 2026 tratam de substância ativa? | ANSWER | EU-T4-001, SPARQL | — |
| B02 | REGULATION | Quando expira a aprovação do protioconazol? | ANSWER | CELEX 32025R0787, linha 168 | — |
| B03 | REGULATION | Quantos produtos ES têm protioconazol? | **REFUSE** | sem dump aberto do registro espanhol | acesso ao ROPF |
| B04 | REGULATION | Que autorizações ADAMA vencem na IT em 6 meses? | ANSWER | IT-T4-001: 58 de 155 | — |
| B05 | MOLECULE | Produtos FR com metalaxil-M e de quem são? | ANSWER | 9 autorizados: 7 Syngenta, 1 Ascenza, 1 ADAMA | — |
| B06 | MOLECULE | Quem fabrica a substância de um produto ADAMA? | **REFUSE** | registro traz **titular**, não fabricante | fonte de manufacturer |
| B07 | MOLECULE | "Folpel" e "folpet" são a mesma substância? | ANSWER | X-006 MORPHOLOGY | — |
| B08 | MOLECULE | Qual a origem autorizada de uma formulação IT? | **REFUSE** | nenhuma fonte de *authorized origin* | idem B06 |
| B09 | PORTFOLIO | Pares cultura × alvo da ADAMA na França? | ANSWER | 504 usos; Vigne×Mildiou 17 | — |
| B10 | PORTFOLIO | A ADAMA lidera o míldio da videira na FR? | **REFUSE** | registro **não é** mercado | dado de vendas |
| B11 | PORTFOLIO | Produtos ADAMA em cereal na IT com protioconazol? | ANSWER | 5: MAGANIC, MAXENTIS, AVASTEL, SORATEL, KOJAMI | — |
| B12 | SCIENCE | Quem publica sobre resistência a herbicidas na FR? | ANSWER | Délye, 9 trabalhos, INRAE Agroécologie | — |
| B13 | SCIENCE | Quem é a maior autoridade em septoriose na ES? | **REFUSE** | recorrência **não é** autoridade | régua de autoridade |
| B14 | CROP | Região com mais área de trigo em FR/ES/IT? | ANSWER | ES41 Castilla y León, 771,8 mil ha | — |
| B15 | CROP | Rendimento de trigo em Castilla y León em 2024? | **REFUSE** | Eurostat não publica rendimento em NUTS 2 (H-001) | fonte nacional |
| B16 | FIELD | O repilo subiu em Huelva nas últimas safras? | ANSWER | 11 safras + controle de coorte | — |
| B17 | FIELD | O míldio subiu na França nesta safra? | **REFUSE** | BSV é PDF regional sem série processável | processar o corpus BSV |
| B18 | COMPETITOR | Empresas com registro contra septoriose FR? | ANSWER | BASF 22, Bayer 20, Syngenta 8, ADAMA 6 | — |
| B19 | COMPETITOR | A Syngenta aumentou a comunicação sobre septoriose? | **REFUSE** | sem coleta e **sem linha de base** | baseline retrospectivo |
| B20 | MARKET | Preço do trigo duro FR e IT na última semana? | ANSWER | FR €267,50/t · IT €271,83/t | — |

## O QUE ESTE BENCHMARK PASSA A EXIGIR DO PRODUTO
Qualquer versão futura do Ask Sintonia **precisa preservar as 8 recusas**. Um sistema que
começar a responder B03, B06, B10, B13 ou B19 sem fonte nova **regrediu**, mesmo parecendo
mais capaz.
