# ARQUITETURA DE PRODUTO ATUAL — porta única

**Data:** 2026-08-29 · **MISSÃO 10** · substitui, **para fins de design**, qualquer
documento que ainda descreva o SINTONIA como um menu de módulos independentes.

> **Se dois documentos discordarem sobre o que é o produto, este vence.** Os demais
> continuam válidos como registro do que se sabia — nenhum foi apagado.

---

## PRODUCT PROMISE

> **Inteligência externa que ajuda a ADAMA a decidir onde olhar primeiro — com evidência.**

Não promete faturamento. Não promete previsão. Promete **prioridade defensável**.

---

## DUAS FERRAMENTAS PRINCIPAIS, UMA EXPLORATÓRIA

### MT1 · REGULATORY & EXPIRY EXPOSURE

> *O que está mudando ou chegando, o que isso toca, e quem mais está exposto?*

**Absorve cinco coisas que eram cinco módulos:** regulatory watch · molecule watch ·
expiry radar · competitor registration · cross-market by molecule. **Não são quatro
sistemas por país** — são quatro *views* (EU · FR · ES · IT) da mesma pergunta.

```
INPUTS    ato europeu (CELEX, data, texto) · registro nacional · titular · substância ·
          data de caducidade · status · cultura×alvo quando a rota do país entrega
OUTPUT    quem está exposto a que prazo, por país, com a data oficial
ESTADOS   DATA_PROVED = SIM · DECISION_PROVED = NÃO (falta piloto) · ECONOMIC = NÃO AFIRMADO
```

**Números vivos:** <!--M:ES_EXPIRING_6M-->486<!--/M--> vencimentos espanhóis em ≤6 meses · <!--M:ES_EXPIRING_12M-->1.004<!--/M--> em ≤12 · ADAMA <!--M:ES_ADAMA_EXPIRING_6M-->36<!--/M--> e <!--M:ES_ADAMA_EXPIRING_12M-->61<!--/M--> ·
**Syngenta 37 e ADAMA 36 são os dois titulares mais expostos na janela de 6 meses**.

**O que falta e o benchmark localizou:** `BY_HOLDER`, `TOP_HOLDERS`, `BY_SUBSTANCE` e
`CROP_COVERAGE` **não existem na rota canônica** — as três primeiras saem do mesmo
snapshot, a quarta custa 972 requisições.

### MT2 · GEOGRAPHIC COMMERCIAL PRIORITY

> *Onde um problema medido está ficando mais relevante — e a ADAMA tem resposta registrada?*

```
INPUTS    CROP AREA · FIELD PRESSURE · TREND · CURRENT LEVEL · SAMPLE N ·
          ADAMA REGISTERED RESPONSE · COMPETITOR REGISTERED RESPONSE ·
          PUBLIC ACTIVATION quando disponível · SEASONAL TIMING
OUTPUT    PRIORITY TO INVESTIGATE   ← nunca SALES OPPORTUNITY
ESTADOS   DATA_PROVED = SIM · DECISION_PROVED = NÃO · ECONOMIC = NÃO AFIRMADO
```

**Por região, cinco campos obrigatórios:**

| campo | exemplo — Sevilla |
|---|---|
| **FACT** | coorte de repilo 1,10 → <!--M:RAIF_SEVILLA_COHORT_2026-->2,74<!--/M--> em duas safras, sobre **301 parcelas**; 253.293 ha de olivar |
| **WHY IT RANKS** | única província no top-3 das **duas** réguas — sobe **e** tem escala |
| **LIMITATION** | 2,74 está **abaixo** do próprio máximo histórico (7,07 em 2009); área é de 2024 e incidência de 2026 |
| **WHAT ADAMA COULD DO** | ativar assistência técnica na próxima safra; NEPTUNE (ES-00211) é resposta registrada para repilo em olivo |
| **WHAT ONLY ADAMA CAN DECIDE** | se a região já é atendida, e se a caducidade de 15/08/2026 do NEPTUNE está em renovação |

### MT3 · PUBLIC ACTIVATION GAP — exploratória

```
CONTRATO   REGISTERED STRENGTH × OBSERVED PUBLIC ACTIVITY → ACTIVATION QUESTION
NUNCA      UNDERUSED ASSET · WHITE SPACE CONFIRMED · SALES OPPORTUNITY
ESTADOS    DATA_PROVED = PARCIAL · DECISION = SÓ PERGUNTA · ECONOMIC = NÃO AFIRMADO
```

**Exemplo:** FR · Vigne × Mildiou — 168 usos autorizados, **ADAMA 17**, a empresa nomeada
com mais usos, e **nenhuma campanha 2025–2026 encontrada nas fontes pesquisadas**.
**A saída é uma pergunta:** *este nível de ativação pública é deliberado?* Quem responde é
a ADAMA.

---

## INTERFACE · Ask Sintonia

**Não é uma quarta ferramenta.** É como se pergunta às duas primeiras. E é um
**contrato de aceitação**, não um benchmark executado: 5 perguntas executam, 35 têm
veredito escrito à mão. Toda resposta devolve `FACTS` · `CONNECTIONS` · `UNKNOWN` ·
`WHY IT MAY MATTER` · `EVIDENCE`.

## SUPPORTING ENGINE — por baixo, não no menu

science · experts · climate context · entity identity (7 entidades) · market/crop context ·
data clock · change events · normalizações (substância <!--M:X006_USE_COVERAGE-->82,1<!--/M-->% · agronômica <!--M:X007_USE_COVERAGE-->23,5<!--/M-->%) ·
camada de evidência e proveniência.

## COLLECT MORE — rota identificada, base insuficiente

| frente | estado medido |
|---|---|
| **competitor communication** | rota **provada para um** dos cinco majors: sitemap da Bayer ES, 265 URLs, todas com `lastmod`, 5 páginas de olivo. Syngenta, ADAMA e BASF: 403. **`PROVED ROUTE` ≠ `MARKET-WIDE BASELINE`** — 403 não é ausência de comunicação |
| **marketing opportunity** | precisa de quatro lados: field/attention · science · competitor communication · ADAMA legitimate response · timing. Hoje **dois** existem. **Sem "marketing score"** |
| **field voices** | **`NOT REACHED / NÃO SEI`**, não `KILL`. Reddit 403, YouTube search RSS 400, fóruns 403 — e **Apify não foi testado** (sem credencial). É preciso testar antes de decidir |
| **unmet need (art. 53)** | `BASELINE ONLY` — o arquivo do MAPA tem 48 linhas e diz "vigentes" |

## DO NOT BUILD

distribution network · supply watch · crop pulse genérico.

---

## HOME — o que ela prioriza (conteúdo, não desenho)

Uma pergunta manda na home: **o que merece atenção agora?**

Cinco classes de item, e **nenhum KPI decorativo**:

| classe | exemplo real disponível hoje |
|---|---|
| `REGULATORY DEADLINE` | <!--M:ES_ADAMA_EXPIRING_6M-->36<!--/M--> autorizações ADAMA vencem em ≤6 meses; Syngenta tem 37 |
| `GEOGRAPHIC AGRONOMIC PRIORITY` | Sevilla — sobe 2,5× na maior base e tem 15,2% da área |
| `ACTIVATION QUESTION` | FR · Vigne × Mildiou — 17 usos, nenhuma campanha encontrada |
| `CHANGE DETECTED` | ES-01717 renomeado MAXENTIS → SORATEL MAX |
| `INVESTIGATE` | <!--M:ES_ACTIVE_WITH_PAST_EXPIRY-->34<!--/M--> registros `Vigente` com caducidade passada, 31 na mesma data |

**Proibido na home:** contador de fontes, contador de linhas, "buzz", score de influência,
ou qualquer número que não mude uma decisão.

---

## O QUE O DESIGN NÃO PODE FAZER

| não pode | porque |
|---|---|
| transformar *"better timing"* em **predictive early warning** | o backtest mediu: **1 safra** no melhor caso, **zero** em dois de três. Só o regulatório antecipa, e porque a data é publicada |
| chamar `ha × incidência` de hectares afetados, área tratada, demanda ou venda | é **índice de exposição relativa**; serve para ordenar |
| apresentar MT3 como oportunidade | é `ACTIVATION QUESTION` |
| dizer que um concorrente está silencioso | o correto é `NO PUBLIC ACTIVITY FOUND IN SEARCHED SOURCES` |
| mostrar "35 perguntas respondidas pelo sistema" | 5 executam; 35 são contrato |
| ler `EXPIRED` como `WITHDRAWN` | <!--M:ES_ACTIVE_WITH_PAST_EXPIRY-->34<!--/M--> registros espanhóis provam o contrário |
| desenhar um menu de módulos independentes | são **duas ferramentas e uma pergunta**, com um motor por baixo |
