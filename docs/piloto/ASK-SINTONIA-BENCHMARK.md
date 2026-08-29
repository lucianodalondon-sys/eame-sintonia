# ASK SINTONIA — BENCHMARK

O deck promete *"a way to query the evidence layer"* (SLIDE 5). Antes de qualquer interface,
é preciso provar que a camada **é consultável** — e que **sabe recusar**.

**Não é chat.** É consulta determinística sobre evidência preservada.
Execução: `scripts/ask_sintonia.py` · Dados: `../../data/samples/ASK-SINTONIA-benchmark.json`

---

## PLACAR

| Resultado | n | % |
|---|---|---|
| **ANSWERED CORRECTLY** | **20** | 57% |
| **REFUSED CORRECTLY** | **14** | 40% |
| **PARTIAL** | **1** | 3% |
| **WRONG ANSWER** | **0** | **0%** |
| UNEXPECTED REFUSAL | 0 | 0% |

*(35 perguntas na MISSÃO 07; eram 25 com 14/10/1/0 e 20 com 12/8/0.)*

**Duas recusas viraram respostas nesta missão — e isso é um resultado, não um conserto:**

| id | era | é | por quê |
|---|---|---|---|
| **B03** | `CORRECT REFUSAL` | `ANSWERABLE` | a recusa estava certa sobre o que sabíamos e **errada sobre a fonte**: o registro espanhol tinha rota pública o tempo todo |
| **B24** | `PARTIAL` | `ANSWERABLE` | titular passou de agregador comercial para ficha oficial |

> Uma recusa que cai porque a fonte abriu é o comportamento desejado. Uma recusa que cai
> porque baixamos a régua seria o contrário. **Nenhuma resposta nova veio de régua mais
> frouxa** — todas vieram de fonte primária nova.

> **Recusa correta é resultado positivo.** O erro grave é inventar resposta. Zero.

## AS 35 PERGUNTAS

| id | domínio | pergunta | esperado | evidência / motivo da recusa | o que destravaria |
|---|---|---|---|---|---|
| B01 | REGULATION | Que atos da UE de 2026 tratam de substância ativa? | ANSWER | EU-T4-001, SPARQL | — |
| B02 | REGULATION | Quando expira a aprovação do protioconazol? | ANSWER | CELEX 32025R0787, linha 168 | — |
| B03 | REGULATION | Quantos produtos ES têm protioconazol? | ANSWER | ES-T4-005: **30 em vigor** — Bayer 8, ADAMA 3 | — *(era REFUSE até a MISSÃO 06)* |
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
| B16 | FIELD | O repilo subiu em Huelva nas últimas safras? | ANSWER | coorte **1,17 → 8,83**, mesmas parcelas · base **7 parcelas** | — *(corrigido na M09: antes comparava 1,19 geral com 8,83 de coorte)* |
| B17 | FIELD | O míldio subiu na França nesta safra? | **REFUSE** | BSV é PDF regional sem série processável | processar o corpus BSV |
| B18 | COMPETITOR | Empresas com registro contra septoriose FR? | ANSWER | BASF 22, Bayer 20, Syngenta 8, ADAMA 6 | — |
| B19 | COMPETITOR | A Syngenta aumentou a comunicação sobre septoriose? | **REFUSE** | sem coleta e **sem linha de base** | baseline retrospectivo |
| B20 | MARKET | Preço do trigo duro FR e IT na última semana? | ANSWER | FR €267,50/t · IT €271,83/t | — |

### Bloco IDENTITY — acrescentado na MISSÃO 06

| id | pergunta | esperado | base |
|---|---|---|---|
| B21 | Qual o produto de referência do ES-01717? | ANSWER | MAPA: **SORATEL MAX** (26/08/2026); era **MAXENTIS** (28/05/2025) |
| B22 | Que denominações comuns estão ligadas ao ES-01717? | ANSWER | AMISTAR ERA 350 SC (Syngenta) e CUMILZAN (Massó) |
| B23 | A Syngenta é titular do ES-01717? | **REFUSE** | é **concessionária**, não titular — e o documento não traz o titular |
| B24 | IDENTITY | Quem detém o registro ES-01717? | ANSWER | **ADAMA Agriculture España S.A.**, ficha oficial do ROPF | — *(era PARTIAL na MISSÃO 06)* |
| B25 | AMISTAR ERA 350 SC tem registro independente? | **REFUSE** | na Espanha é denominação comum do **mesmo** registro; o AMISTAR ERA **240 EC** italiano é outro registro |
| B26 | IDENTITY | Quem fabrica o produto do registro ES-01717 e onde? | ANSWER | ADAMA Agricultural Solutions Ltd., planta (Neot Hovav) — ficha oficial do ROPF | — |
| B27 | IDENTITY | A ADAMA depende de Israel para fornecer na Espanha? | **REFUSE** | a ficha nomeia UM fabricante e UMA planta para UM registro. Não é cadeia de suprimento | — |
| B28 | IDENTITY | A ADAMA é a maior empresa do mercado fitossanitário espanhol? | **REFUSE** | é a titular com MAIS REGISTROS (188 de 3.084). Contagem de registros não é venda, volume nem participação | — |
| B29 | IDENTITY | Quantos registros espanhóis têm mais de uma denominação comum? | ANSWER | 363 em vigor, 18,2% dos 1.993 em vigor. O denominador vai junto ou a resposta engana | — |
| B30 | IDENTITY | Contar por marca infla o mercado espanhol em quanto? | **REFUSE** | a pergunta não é respondível como está: MERCADO não é medível nesta fonte. O que se mede é excesso de contagem de AUTORIZAÇÕES — 1,52x sobre o registro em vigor | — |
| B31 | CHANGE | Algum registro espanhol mudou de nome entre 2025 e 2026? | ANSWER | 5 renomeações confirmadas em 311 registros comparáveis, incluindo ES-01717 | — |
| B32 | CHANGE | A renomeação do ES-01717 indica um relançamento comercial? | **REFUSE** | prova apenas OFFICIAL RECORD NAME CHANGED. Nem canal, nem preço, nem venda | — |
| B33 | CHANGE | Algum registro espanhol mudou de titular no último ano? | **REFUSE** | o campo existe e é comparável, mas só temos UMA versão arquivada do export do ROPF. Detectável a partir da segunda | — |
| B34 | CHANGE | Quando o nome do ES-01717 mudou? | *PARTIAL* | sabemos o intervalo (entre 28/05/2025 e 26/08/2026) e o trâmite datado em 28/07/2026; a data em que o mercado passou a ver o nome novo não está na fonte | — |
| B35 | FIELD | Que culturas o ES-01717 pode tratar? | ANSWER | cebada, centeno, trigo e triticale — ficha oficial em PDF do ROPF | — |

**B23 é a pergunta mais importante do benchmark inteiro**: um resumo automático de busca
cometeu exatamente esse erro durante esta missão, chamando a concessionária de titular.

## O QUE ESTE BENCHMARK PASSA A EXIGIR DO PRODUTO
Qualquer versão futura do Ask Sintonia **precisa preservar as 10 recusas**. Um sistema que
começar a responder B03, B06, B10, B13, B19, B23 ou B25 sem fonte nova **regrediu**, mesmo parecendo
mais capaz.
