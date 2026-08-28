# CASOS PARA APRESENTAÇÃO — SINTONIA EAME

Registro contínuo de casos reais encontrados durante a missão que possam demonstrar valor
para a ADAMA.

Meta: **5 a 10 casos extremamente claros**.
**Não fabricar casos para preencher quota.** 3 casos irrefutáveis valem mais que 10 mornos.

**Estado:** MISSÃO 02 em curso — **6 casos registrados** (meta 5–10 — atingida a faixa mínima) (meta 5–10).
**Última atualização:** 2026-08-28

---

## FICHA DO CASO

```
CASE_ID:
COUNTRY:
CROP:
REGION:
PROBLEM:                  # o problema real, do mundo, não do sistema
SOURCES:                  # SOURCE_IDs
WHAT_HAPPENED:            # o fato, com data e evidência
WHAT_SINTONIA_CONNECTS:   # o que o SINTONIA junta que ninguém junta hoje
WHY_ADAMA_SHOULD_CARE:    # a decisão que muda
SCREEN_AVAILABLE:         # existe tela no protótipo? qual?
STATUS:                   # REAL | DERIVED | DEMO | CONCEPT
```

---

## ESTADO VISUAL DOS BLOCOS

Todo bloco experimental do portal carrega estado interno **visível**:

| Estado | Significado |
|---|---|
| **REAL** | Informação diretamente sustentada por fonte. |
| **DERIVED** | Resultado calculado sobre informação real. |
| **DEMO** | Demonstração usando dados reais, ainda não automatizada. |
| **CONCEPT** | Capacidade ainda não comprovada. |

> **CONCEPT nunca pode aparecer como capacidade pronta numa apresentação.**
> E nenhuma tela bonita é evidência de que uma capacidade existe.

---

## CASOS REGISTRADOS

### CASE-001 · De um ato do Jornal Oficial da UE até um produto ADAMA numa videira francesa

```
CASE_ID:                CASE-001
COUNTRY:                EUROPEAN UNION → FRANCE
CROP:                   Vigne (videira)
REGION:                 nacional (a autorização francesa não tem recorte regional)
PROBLEM:                Mildiou de la vigne (míldio da videira)
TIME:                   ato de 15/06/2026; registro francês na versão de 25/08/2026
SOURCES:                EU-T4-001 (CELLAR/Jornal Oficial) + FR-T4-001 (ANSES E-Phy)
CROSSING:               X-006 (chave: nº CAS)
```

**WHAT_HAPPENED**
Em 15 de junho de 2026, a UE publicou o Regulamento de Execução (UE) 2026/1353
(CELEX 32026R1353), que trata da substância ativa **Metalaxyl-M**, CAS **70630-17-0**,
com período de aprovação de 01/06/2020 a 31/05/2035.

**WHAT_SINTONIA_CONNECTS**
Partindo apenas desse ato e sem nenhum dado interno, a cadeia se fecha sozinha:

```
CELEX 32026R1353  →  CAS 70630-17-0  →  E-Phy "Metalaxyl-M"  →  9 produtos autorizados na França
                                                                 ├─ 7 SYNGENTA
                                                                 ├─ 1 ASCENZA
                                                                 └─ 1 ADAMA
                                                                     PANDERO GOLD, AMM 2010398
                                                                     folpel 400 g/kg + metalaxil-M
                                                                     Vigne × Mildiou(s), 2,0 kg/ha
```

**WHY_ADAMA_SHOULD_CARE**
Três leituras, todas apoiadas em documento oficial:
1. **Exposição própria** — a ADAMA tem um produto autorizado na França que depende dessa
   substância, e o combate exato em que ele atua é conhecido (videira × míldio).
2. **Exposição do concorrente** — a Syngenta tem 7 dos 9 produtos autorizados com a mesma
   substância. Qualquer movimento europeu sobre o metalaxil-M atinge a Syngenta com
   intensidade muito maior do que atinge a ADAMA.
3. **Repetibilidade** — isso não é uma pesquisa manual. É uma consulta que roda sozinha,
   por substância, toda semana, para qualquer ato futuro.

**RAW_EVIDENCE**
`data/samples/EU-T4-001/CELEX-32026R1696-eng.xhtml` (formato do ato, texto integral)
`data/samples/X-006-eu-cas-to-ephy.json` (a cadeia medida)
`data/samples/FR-T4-001/` (registro francês, produtos e usos ADAMA)
Reprodução: `scripts/cellar.sh` e `scripts/ephy.sh`

**SCREEN_AVAILABLE**   ainda não — protótipo não iniciado
**STATUS**             **REAL** (todos os elementos vêm direto de fonte oficial;
                       nenhuma derivação, nenhuma estimativa)

**O que este caso NÃO diz** — e a tela não pode sugerir:
- que o metalaxil-M vá ser retirado (o ato **mantém** a aprovação até 2035);
- que a ADAMA seja forte ou fraca em míldio da videira (contagem de registros não é mercado);
- que a Syngenta esteja em risco (ter mais registros não é ter mais exposição comercial).

---

### CASE-002 · Uma substância aprovada na Europa que não existe como produto na França

```
CASE_ID:                CASE-002
COUNTRY:                EUROPEAN UNION → FRANCE
CROP:                   —
PROBLEM / OPPORTUNITY:  descompasso entre a camada europeia e a camada nacional
TIME:                   ato de 14/07/2026; registro francês de 25/08/2026
SOURCES:                EU-T4-001 + FR-T4-001
CROSSING:               X-006
```

**WHAT_HAPPENED**
O Regulamento de Execução (UE) 2026/1696, de 14/07/2026, **renovou** a aprovação europeia do
**ácido pelargônico** (CAS 112-05-0, CIPAC 888) — de 01/10/2026 até **30/09/2041**, quinze anos.

**WHAT_SINTONIA_CONNECTS**
A substância consta no E-Phy francês como `INSCRITE`. Mas o cruzamento com o catálogo de
produtos devolve **zero produtos autorizados na França** que a contenham.

**WHY_ADAMA_SHOULD_CARE**
Este é o caso que **prova a regra mais importante de T4**: aprovação europeia de substância
e autorização nacional de produto são camadas diferentes, e **misturá-las produz conclusão
falsa**. Aqui, uma substância com quinze anos de aprovação europeia garantida não tem, hoje,
nenhum produto correspondente no mercado francês. Para MARKET DEVELOPMENT isso não é um erro
de dado: é a definição de um espaço vazio, com prazo regulatório longo e conhecido.

**RAW_EVIDENCE**   `data/samples/EU-T4-001/` · `data/samples/X-006-eu-cas-to-ephy.json`
**SCREEN_AVAILABLE**   ainda não
**STATUS**             **REAL**

**Ressalva:** "zero produtos" é zero **neste catálogo, nesta data**, e a busca foi por nome
de substância. Antes de apresentar isso como oportunidade, é preciso confirmar que não há
grafia alternativa no registro francês — o E-Phy tem entradas do tipo `AUTRE_CAS`.

---

### CASE-003 · O calendário de renovações que ninguém tem numa planilha só (Itália)

```
CASE_ID:                CASE-003
COUNTRY:                ITALY
CROP:                   —
PROBLEM:                carga de renovação regulatória concentrada no curto prazo
TIME:                   situação do registro em 24/08/2026
SOURCES:                IT-T4-001
CROSSING:               —  (leitura direta da fonte, sem composição)
```

**WHAT_HAPPENED**
O registro italiano publica a data de vencimento de cada autorização. Em 24/08/2026 havia
**3.466 autorizações em vigor com vencimento futuro**.

**WHAT_SINTONIA_CONNECTS**
Cruzando vencimento com titular:

| | vencem em ≤6 meses | total com vencimento futuro | % |
|---|---|---|---|
| **ADAMA ITALIA** | **58** | 155 | **37,4%** |
| mercado italiano | 724 | 3.466 | 20,9% |

Seis autorizações ADAMA venceram em **31/08/2026** — cinco delas de **lambda-cialotrina**
(LAMDEX EXTRA, FORZA, NINJA, DURAVIS, ELTIRA) e uma de metaldeído (LUMA-KL).

**WHY_ADAMA_SHOULD_CARE**
A concentração é conhecível com antecedência e por empresa. Serve para dimensionar equipe
regulatória, para antecipar risco de descontinuidade comercial e — o mais interessante —
para ver **a exposição do concorrente**, que é pública do mesmo jeito.

**RAW_EVIDENCE**   `data/samples/IT-T4-001/IT-T4-001-adama-expiries.json`
**SCREEN_AVAILABLE**   ainda não
**STATUS**             **REAL** (contagens) + **DERIVED** (o percentual comparativo)

**O que este caso NÃO diz:** que esses produtos serão perdidos. Vencimento abre renovação.
E as datas são agrupadas por calendário europeu — a comparação 37,4% × 20,9% vale porque foi
feita **dentro do mesmo agrupamento**, não apesar dele.

---

### CASE-004 · A Espanha dizendo, oficialmente, onde não há solução

```
CASE_ID:                CASE-004
COUNTRY:                SPAIN
CROP:                   45 combinações cultura × problema
REGION:                 nacional, com exceções regionais declaradas
PROBLEM:                necessidades agronômicas sem produto autorizado
TIME:                   situação em 24/08/2026
SOURCES:                ES-T4-002
```

**WHAT_HAPPENED**
O MAPA mantém e publica a lista de **autorizações excepcionais vigentes** (art. 53 do
Reg. 1107/2009). São 45 hoje. Uma autorização excepcional existe quando **não há solução
autorizada normal** para um perigo fitossanitário.

**WHAT_SINTONIA_CONNECTS**
A lista é, na prática, o Estado espanhol publicando uma lista de necessidades não atendidas,
com cultura, problema, substância usada em caráter de exceção e prazo:

- **Manzano y peral × fuego bacteriano** (*Erwinia amylovora*)
- **Champiñón × telaraña** — fluxapyroxad 30% SC
- **Remolacha azucarera × pulgón** — flonicamida 50% WG
- **Cebolla y ajo × *Delia antiqua*** — ciantraniliprol 10% OD
- **Fresal × desinfección del suelo** — metam sodio 51% SL

**WHY_ADAMA_SHOULD_CARE**
Para MARKET DEVELOPMENT e R&D, é uma lista curta, oficial, datada e específica de dores reais
— o oposto de intuição de mercado. E é comparável ano a ano, se arquivada.

**RAW_EVIDENCE**   `data/samples/ES-T4-001/ES-T4-002-autorizaciones-excepcionales.json`
**SCREEN_AVAILABLE**   ainda não
**STATUS**             **REAL**

**O que este caso NÃO diz:** que há mercado ali. Lacuna reconhecida não é oportunidade
dimensionada — pode ser pequena, sazonal ou já em vias de solução por outra empresa.

---

### CASE-005 · A safra francesa de 2024 vista pelo clima da própria região

```
CASE_ID:                CASE-005
COUNTRY:                FRANCE
CROP:                   Trigo comum (C1110)
REGION:                 FRB0 Centre–Val de Loire · FRE2 Picardie · FRI3 Poitou-Charentes
PROBLEM:                colapso de rendimento em 2024
TIME:                   janela 01/05–30/06, anos 2022–2024
SOURCES:                EU-T1-001 · EU-T1-002 · EU-T2-001 · EU-T2-002
CROSSING:               X-001
```

**WHAT_HAPPENED**
O rendimento nacional francês de trigo comum caiu de **7,28 t/ha em 2023 para 6,02 t/ha em
2024** — e voltou a 7,34 t/ha em 2025. Foi um buraco de um ano só, não uma tendência.

**WHAT_SINTONIA_CONNECTS**
Nas três maiores regiões produtoras, na janela de enchimento de grão:

| Região | trigo 2024 | dias ≥30 °C 2022 → 2023 → 2024 | chuva 2022 → 2023 → 2024 |
|---|---|---|---|
| FRB0 Centre–Val de Loire | 544,6 mil ha | 5 → 3 → **0** | 118 → 103 → **231 mm** |
| FRE2 Picardie | 472,0 mil ha | 1 → 1 → **0** | 101 → 95 → **175 mm** |
| FRI3 Poitou-Charentes | 283,7 mil ha | 13 → 3 → **0** | 106 → 137 → **198 mm** |

2024 não foi um ano de calor na França: foi um ano **sem nenhum dia de calor** e com **cerca
do dobro da chuva** na janela sensível, em todas as regiões grandes ao mesmo tempo.

**WHY_ADAMA_SHOULD_CARE**
O sinal é regional, é anterior à colheita e é obtido de fontes abertas. Um ano de excesso
hídrico prolongado na fase sensível é um ano de pressão de doença foliar e de janelas de
aplicação difíceis — hipótese que o SINTONIA pode **testar** assim que T3 entrar.

**RAW_EVIDENCE**   `data/samples/X-001-nuts2-heat-vs-wheat.json` · `data/samples/EU-T1-002-wheat-yield-country.json`
**SCREEN_AVAILABLE**   ainda não
**STATUS**             **REAL** (área, clima e rendimento) + **DERIVED** (a contagem de dias e a agregação da janela)

**O que este caso NÃO diz:** que a chuva causou a queda. O rendimento é **nacional**, o clima
é de **um ponto por região**, e nenhum dado de doença entrou. É coincidência medida, não
explicação. Enquanto T3 não fechar, isto é exposição — não causa.

---

### CASE-006 · A mesma pergunta, a janela errada, a resposta invertida

```
CASE_ID:                CASE-006
COUNTRY:                SPAIN
CROP:                   Trigo comum
REGION:                 ES41 Castilla y León (maior área de trigo dos três países: 771,8 mil ha)
PROBLEM:                seca de 2023 e o pior rendimento espanhol da série
TIME:                   2020–2024
SOURCES:                EU-T2-001 · EU-T1-002
CROSSING:               X-001 / CAP-013
```

**WHAT_HAPPENED**
O rendimento espanhol de trigo comum foi **2,14 t/ha em 2023** — o mais baixo do período
2019–2026 —, contra 3,07 em 2022 e 3,74 em 2024.

**WHAT_SINTONIA_CONNECTS**
Duas janelas, o mesmo ponto, o mesmo dado, conclusões opostas:

| Ano | chuva **fev–abr** | chuva **mai–jun** | rendimento ES |
|---|---|---|---|
| 2020 | 170,9 mm | 79,8 mm | 4,40 |
| 2021 | 142,3 mm | 83,3 mm | 4,15 |
| 2022 | 120,5 mm | **31,1 mm** | 3,07 |
| 2023 | **34,9 mm** | 84,0 mm | **2,14** |
| 2024 | 142,2 mm | 109,0 mm | 3,74 |

Pela janela **fevereiro–abril**, 2023 é de longe o ano mais seco e é o pior rendimento — a
ordem acompanha. Pela janela **maio–junho**, 2023 aparece **mais chuvoso** que 2022 e o
indicador aponta na direção contrária ao resultado.

**WHY_ADAMA_SHOULD_CARE**
Este é o caso que justifica o rigor do SINTONIA inteiro. As duas tabelas usam **a mesma fonte
e o mesmo ponto**. A única diferença é a janela — e ela inverte a leitura. Um painel bonito
construído sobre a janela errada teria dito ao time comercial exatamente o oposto do que
aconteceu no campo.

**RAW_EVIDENCE**   `data/samples/CASE-006-es41-rain-window-vs-yield.json`
**SCREEN_AVAILABLE**   ainda não
**STATUS**             **REAL** (chuva e rendimento) + **DERIVED** (as somas por janela)

**O que este caso NÃO diz:** que a chuva de fevereiro–abril explica o rendimento. São cinco
pontos, clima de um ponto contra rendimento nacional, e nenhum controle de outras variáveis.
O que ele **prova** é que a escolha da janela decide o sinal — e que isso precisa ser
declarado em qualquer tela climática.

---

| CASE_ID | País | Cultura | Status | Tela |
|---|---|---|---|---|
| CASE-001 | EU → FR | Vigne | REAL | ainda não |
| CASE-002 | EU → FR | — | REAL | ainda não |
| CASE-003 | IT | — | REAL + DERIVED | ainda não |
| CASE-004 | ES | 45 combinações | REAL | ainda não |
| CASE-005 | FR | Trigo comum | REAL + DERIVED | ainda não |
| CASE-006 | ES | Trigo comum | REAL + DERIVED | ainda não |
