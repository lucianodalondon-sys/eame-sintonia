# CHECKPOINT — PILOTO EVOLUÇÃO DE DOENÇAS (VITE × PERONOSPORA × VENETO)

Branch `claude/pilot-disease-evolution-vite-veneto`. `sintonia/canonical` READ_ONLY, untouched.
Nothing wired into any surface. P0.2 / meeting portal / Supabase / Passaporte / Universal /
motor-43 not touched. `MEETING_FREEZE` intact.

## Os números pedidos

```
HISTORICAL_YEARS_FOUND                  = 26   (annata agraria 2000-01 … 2025)
HISTORICAL_YEARS_WITH_PERONOSPORA       = 21   (≥1 frase de peronospora atribuída à VIDE)
HISTORICAL_YEARS_WITH_COMPARABLE_OUTCOME= 6    confirmados (2014,2016,2021,2022,2024,2025)
                                               + no máximo ~3 possíveis em 2000-2013
HISTORICAL_YEARS_WITH_ONLY_MENTION      = 2    confirmados (2019, 2020) + 2 em disputa (2018, 2023)
HISTORICAL_YEARS_WITH_NO_OUTCOME        = 2    (2015 = nenhuma frase; 2017 = só RISCO)

PERONOSPORA_YEARS_FOUND     = 21 de 26
COMPARABLE_YEARS            = 6 confirmados  → GATE A = DEMO_ONLY (não STRONG)
OUTCOME_SCALE               = LOW/MEDIUM/HIGH sobrevive fraco em 6 safras
                              ABOVE/NORMAL/BELOW NÃO SOBREVIVE — ver abaixo
TARGET_SEASON_WEATHER_LEAKAGE = 0   (provado em código, 34 safras, 2 regimes de corte)
BASELINE_DEFINED            = SIM  (climatologia + persistência + piso uniforme)
BACKTEST_POSSIBLE           = NÃO com 6 safras
PRELIMINARY_BACKTEST_RUN    = NÃO — e não por falta de tempo, por aritmética
MODEL_BEATS_BASELINE        = NÃO TESTÁVEL
BEST_ALTERNATIVE_ISSUE      = busca ainda em execução
PC_REQUIRED_ROUTES          = 0 que importem — coleta inteira feita deste contêiner
```

## As quatro conclusões que já não dependem de mais coleta

### 1. `RISK_FORECAST != DISEASE_PRESENCE` foi violado — e pego

A única frase de peronospora na vide de 2017 é:

> *"Verso la metà di giugno i vigneti erano in prechiusura-grappolo con **un rischio basso
> di infezione** di Peronospora…"*

Isso é uma categoria de risco de um modelo, avaliada num dia. Não diz o que a doença fez.
Um dos meus dois pipelines codificou 2017 como sinal de gravidade — errado, e exatamente o
erro que a lei existe para impedir: teria pontuado uma previsão contra outra previsão.

Um passe adversarial não pegou. **Dois passes independentes comparados pegaram.** A regra
está agora aplicada em código (`merge_verified.py`), e rodando cega sobre as 12 safras ela
marca exatamente 2017 — o mesmo ano que a réplica independente rejeitou.

### 2. A escala ABOVE/NORMAL/BELOW não é construível a partir desta fonte

Três desenhistas de escala independentes (`scale_defensible` = PARCIAL, PARCIAL, **NÃO**):

> em nenhuma das doze relações uma única frase compara a peronospora da vide a uma norma,
> a uma média ou a um ano anterior — a ARPAV reserva essa linguagem para o **clima**

`NORMAL` é categoria vazia. Construí-la seria vestir a linha de base do analista com a
autoridade da fonte. **Isto é um achado, não uma lacuna a preencher.**

### 3. A circularidade é BAIXA — e o mesmo número limita a previsibilidade

Sobre 34 safras ERA5, o maior |Spearman| entre qualquer preditor antecedente e qualquer
motor de infecção da própria safra é **0,479**, e é o máximo de ~160 ligações rastreadas,
logo inflado por seleção.

- Bom: os preditores **não** são cópia disfarçada do tempo da safra-alvo → não circular.
- Ruim: o tempo antecedente explica no máximo **~23 %** da variância da chuva da própria
  safra. Se a gravidade é dirigida por essa chuva — e os relatórios dizem isso frase após
  frase — um outlook 12M de base meteorológica tem pouco espaço físico para ter skill.

É uma medição lida dos dois lados. O único caminho restante é **carryover de inóculo**
(epidemia do ano anterior → carga de oósporos), que é doença→doença e é precisamente o que
`BASELINE_PERSISTENCE` mede, sem usar clima nenhum.

### 4. Com 6 safras o backtest é aritmeticamente vazio, não apenas fraco

Fixado **antes** de qualquer modelo, para que a barra não fosse ajustada ao resultado
(k=3 classes, validação temporal estrita, treino mínimo 5 → N safras rendem ~N-5 pontuáveis):

| safras pontuáveis | acertos exigidos p≤0,05 |
|---|---|
| 3–4 | perfeição, e ainda assim não passa Bonferroni |
| 6 | 5/6 = 0,83 |
| 12 | 8/12 = 0,67 |
| 21 | 11/21 = 0,55 |

6 safras comparáveis deixam **≈1 ano pontuável**. Um ano não separa skill de sorte sob
teste nenhum. Qualquer acurácia impressa ali seria infalsificável, não impressionante.

## A ameaça estrutural nova, que limita o que 2000-2013 pode salvar

Recuperei 14 relatórios além dos 12 publicados na página (a pasta de anexos guarda 26; os
outros vieram da API REST do Plone, não de adivinhação de URL). Mas a varredura léxica
mecânica mostra que **eles relatam gravidade sistematicamente menos**:

| bloco | docs | com frase de peronospora na vide | com marcador de gravidade |
|---|---|---|---|
| 2000–2013 | 14 | 10 | **3** |
| 2014–2025 | 12 | 11 | **9** |

A disponibilidade do desfecho está **correlacionada com a época**. Isso limita 2000-2013 a
somar ~3 safras comparáveis (total provável 6–9, não 20), e introduz um viés de era que um
backtest de 26 safras não pode ignorar.

## O que foi construído e está provado

- **26 PDFs ARPAV** (SHA256 + URL exata em `EVIDENCE/SOURCES.json`), texto extraído.
- **ERA5 1990–2025**, 13.149 dias × 5 variáveis × 5 pontos vitícolas; validado contra o
  clima conhecido do Vêneto (Bardolino mais quente pelo lago, Valdobbiadene mais chuvoso
  1.596 mm, aquecimento 0,33–0,55 °C/década).
- **Preditores com corte, vazamento 0**, em dois regimes: `CUTOFF_B_TRUE_12M` (emitido em
  1/set de Y-1) e `CUTOFF_A_PRESEASON` (1/mar de Y). Provado por uma função independente
  daquela que os construiu. As normais climatológicas também são restritas ao corte.
- **Harness de backtest hostil**: baselines primeiro, 5 hipóteses a priori escritas antes
  de qualquer rótulo, validação temporal estrita como primária, LOYO só como limite
  otimista, teste de permutação em cada score, nota de Bonferroni, e um
  `OVERFIT_DEMONSTRATION` que mede quanta acurácia a pura seleção compra.
- **Motor de anos análogos** com duas piscinas separadas — meteorológica e rotulada —
  porque relatar só a primeira sugeriria uma profundidade histórica que o desfecho não tem.
- **Rotas medidas e rejeitadas com o resultado negativo guardado**: `bollettino-mese`
  (264 docs, zero conteúdo fitossanitário — medido, não presumido), `peronospora-vite`
  (saída do modelo VitiMeteo = `MODELLED_RISK`), `agrometeoinforma` (sem arquivo).

## Recomendação honesta para segunda-feira

Não apresentar isto como previsão. O produto defensável hoje é uma **reconstrução histórica
auditável** — 26 safras, cada célula com a frase italiana literal que a justifica — mais a
declaração explícita de por que um outlook 12M ainda não está provado. Vender skill que o
backtest não pode medir seria destruir a credibilidade que o resto do trabalho constrói.

Ainda em execução: verificação de 2000-2013 e a eleição outcome-first de alternativas
(Itália/França/Espanha, pragas e doenças, critério = o que permite PROVAR previsão).
