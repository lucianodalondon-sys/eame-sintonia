# CASOS PARA APRESENTAÇÃO — SINTONIA EAME

Registro contínuo de casos reais encontrados durante a missão que possam demonstrar valor
para a ADAMA.

Meta: **5 a 10 casos extremamente claros**.
**Não fabricar casos para preencher quota.** 3 casos irrefutáveis valem mais que 10 mornos.

**Estado:** MISSÃO 02 em curso — **15 casos registrados**, classificados por TIER e por ADAMA_ALIGNMENT (meta 5–10).
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
ADAMA_ALIGNMENT:          # HIGH | MEDIUM | LOW | UNKNOWN — com evidência do radar público
TIER:                     # A HERO CASE | B STRONG SUPPORT | C TECHNICAL PROOF | D NÃO USAR
```

**ADAMA_ALIGNMENT** é medido contra `docs/adama/RADAR-ADAMA-EAME.md`, nunca por intuição.
`HIGH` exige sinal público da ADAMA na mesma cultura **e** no mesmo problema.

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

**ADAMA_ALIGNMENT: MEDIUM** · **TIER: B · STRONG SUPPORT**
> vinha × míldio: na França a ADAMA lidera o registro (17 usos) mas **não** há campanha 2025–2026; na Espanha há (Vinergy). O mecanismo do caso — ato da UE → produto — é HIGH; a cultura escolhida é MEDIUM.

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

**ADAMA_ALIGNMENT: LOW** · **TIER: C · TECHNICAL PROOF**
> ácido pelargônico não aparece em nenhum sinal público da ADAMA nos três países. O caso vale como **prova de método** (camada UE ≠ camada nacional), não como tema.

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

**ADAMA_ALIGNMENT: HIGH** · **TIER: A · HERO CASE**
> 58 das 155 autorizações ADAMA na Itália vencem em ≤6 meses, e a Itália é CORE PUBLIC SIGNAL em cereal. Toca diretamente o portfólio ativo da empresa.

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

**ADAMA_ALIGNMENT: HIGH** · **TIER: B · STRONG SUPPORT**
> a lista espanhola de autorizações excepcionais inclui culturas de alto valor, e a Espanha é onde a ADAMA tem sinal público em olivar (Neptune) e vinha (Vinergy).

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

**ADAMA_ALIGNMENT: HIGH** · **TIER: B · STRONG SUPPORT**
> trigo na França: cereal é CORE PUBLIC SIGNAL nos três países e a ADAMA lançou Forapro e Maxentis exatamente para doença de trigo.

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

**ADAMA_ALIGNMENT: MEDIUM** · **TIER: C · TECHNICAL PROOF**
> trigo espanhol: cultura alinhada (Avastel), mas o caso é sobre método de janela climática, não sobre um problema que a ADAMA comunique.

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

### CASE-007 · Três províncias, uma cultura, uma safra, três epidemias diferentes

```
CASE_ID:                CASE-007
COUNTRY:                SPAIN (Andalucía)
CROP:                   Vid (Vitis vinifera — VITVI)
REGION:                 Huelva · Córdoba · Cádiz
PROBLEM:                Míldio da videira (Plasmopara viticola — PLASVI)
TIME:                   safra 2026, amostragem semanal de março a julho
SOURCES:                ES-T3-001 (RAIF Andalucía)
CROSSING:               província × data × cultura × doença
```

**ADAMA_ALIGNMENT: MEDIUM** · **TIER: A · HERO CASE**
> vinha × míldio na Andaluzia: a ADAMA tem sinal público em vinha na Espanha (Vinergy, proteção declarada contra mildiu). Alinhado no país certo, na cultura certa, no problema certo — mas vinha caiu para segunda vertical.

**WHAT_HAPPENED**
A rede oficial andaluza mediu, parcela a parcela e semana a semana, o percentual de cepas
afetadas por míldio. Em 2026:

| | março | abril | maio | junho |
|---|---|---|---|---|
| **Huelva** | 0% | 4–9% | 13–17% | **24–26%** |
| **Córdoba** | 0% | 0% | 5–6% (a partir de 20/05) | 6% → 0% |
| **Cádiz** | 0% | 0% | 0% | 0% (duas leituras isoladas de 4%) |

**WHAT_SINTONIA_CONNECTS**
Uma epidemia real e crescente em Huelva, um episódio curto e contido em Córdoba, e
praticamente nada em Cádiz — tudo na mesma comunidade autônoma, na mesma cultura, no mesmo
ano, medido pela mesma rede com o mesmo protocolo.

**WHY_ADAMA_SHOULD_CARE**
Tratar "Andaluzia" como um território técnico único é errar por um fator de 26. A média
regional (~7%) **não descreve nenhuma das três províncias**. Posicionamento técnico,
recomendação e campanha precisam ser provinciais — e agora existe o dado que sustenta isso,
semanalmente, de graça.

**RAW_EVIDENCE**   `data/samples/ES-T3-001-raif-vid-mildiu-2026.json`
**SCREEN_AVAILABLE**   ainda não
**STATUS**             **REAL** (percentuais medidos em campo pela rede oficial)

**O que este caso NÃO diz:** por que a diferença existe. Ver CASE-008.

---

### CASE-008 · O gráfico que quase fizemos — e que teria mentido

```
CASE_ID:                CASE-008
COUNTRY:                SPAIN (Andalucía)
CROP:                   Vid
PROBLEM:                a tentação de explicar a doença pelo clima
TIME:                   safra 2026
SOURCES:                ES-T3-001 + EU-T2-001
CROSSING:               X-009
```

**ADAMA_ALIGNMENT: HIGH** · **TIER: A · HERO CASE**
> não pela cultura, mas pelo que demonstra: que o SINTONIA recusa a correlação fácil. É o caso que sustenta a **confiabilidade** de tudo o mais que for apresentado.

**WHAT_HAPPENED**
Com CASE-007 na mão, a pergunta seguinte é automática: *"foi o clima?"*. Medimos chuva,
dias de chuva e umidade relativa na janela 15/03–31/05 para as três províncias.

| Província | chuva | dias ≥1 mm | UR média | míldio |
|---|---|---|---|---|
| Huelva | 55,4 mm | 12 | 66,6% | **26,4%** |
| Córdoba | **65,1 mm** | 12 | 66,1% | 6,4% |
| Cádiz | 48,9 mm | 8 | **74,2%** | **≈0%** |

**WHAT_SINTONIA_CONNECTS**
Nada — e essa é a descoberta. **Córdoba choveu mais que Huelva e teve quatro vezes menos
doença. Cádiz teve a maior umidade das três e praticamente nenhuma doença.** A ordem
climática não reproduz a ordem epidemiológica.

**WHY_ADAMA_SHOULD_CARE**
Este é o caso que prova que o SINTONIA é um instrumento sério e não um gerador de painéis.
Um dashboard com as duas curvas lado a lado — clima e doença, ambos dados reais, ambos de
fontes oficiais — teria induzido a conclusão "a chuva trouxe o míldio", e teria orientado
recomendação técnica e campanha na direção errada, em duas das três províncias.

O SINTONIA **detectou** a armadilha porque tinha o dado dos dois lados e a disciplina de
testar antes de afirmar. É o oposto do que a §8 da missão proíbe.

**RAW_EVIDENCE**   `data/samples/X-001-completo-mildiu-vs-clima.json`
**SCREEN_AVAILABLE**   ainda não — e, se existir, precisa de aviso explícito no bloco
**STATUS**             **REAL** (as duas medições) + **DERIVED** (as janelas e agregações)

**O que este caso NÃO diz:** que o clima é irrelevante para o míldio — seria a mentira
oposta, e igualmente indefensável. A epidemiologia do míldio depende de clima; o que estes
dados mostram é que **três pontos de província numa safra não bastam** para explicar a
diferença observada, e que variedade, manejo e, sobretudo, o **programa de fungicida
aplicado** — que a RAIF registra e nós ainda não cruzamos — ficaram de fora.

---

### CASE-009 · A busca larga que entregaria a rede de especialistas errada

```
CASE_ID:                CASE-009
COUNTRY:                SPAIN (comparado a FRANCE e ITALY)
CROP:                   Trigo
PROBLEM:                septoriose (Zymoseptoria tritici)
TIME:                   trabalhos de 2018 a 2026
SOURCES:                EU-T5-001 (OpenAlex) · vocabulário de ES-T4-001
CROSSING:               X-002 / X-010
```

**ADAMA_ALIGNMENT: HIGH** · **TIER: B · STRONG SUPPORT**
> septoriose do trigo é exatamente o alvo declarado de Forapro (T1: Septoria, Rust, Powdery Mildew). O caso mostra como achar os especialistas certos do problema que a ADAMA está comunicando agora.

**WHAT_HAPPENED**
A pergunta era: *"quem estuda a septoriose do trigo na Espanha?"*. Duas consultas, a mesma
base, a mesma janela de anos, o mesmo país:

| consulta | trabalhos | autores mais recorrentes | quem são |
|---|---|---|---|
| `wheat septoria OR Zymoseptoria` | **2.627** | Slafer (30), Araus (24), Kefauver (15) | fisiologia de cultura e sensoriamento remoto |
| `"Zymoseptoria tritici"` | **27** | **Sánchez-Vallet (11)**, Meile (5), González-Menéndez (5) | patologia do próprio patógeno |

**97 vezes mais resultados, e uma lista de pessoas completamente diferente.**

**WHY_ADAMA_SHOULD_CARE**
A primeira lista não é falsa: são pesquisadores reais, espanhóis, de trigo, com números
reais. Ela apenas responde a **outra pergunta** — *"quem publica sobre trigo na Espanha"*.
Entregue como "os especialistas em septoriose", ela levaria a equipe técnica a procurar
parceria, ensaio ou consultoria com quem não trabalha no problema.

O SINTONIA só evita isso porque tem o **vocabulário controlado** (nome científico e código
EPPO, vindos do registro espanhol) para fazer a pergunta certa.

**RAW_EVIDENCE**   `data/samples/EU-T5-001-openalex-people.json`
**SCREEN_AVAILABLE**   ainda não
**STATUS**             **REAL** (as duas contagens e as duas listas)

**O que este caso NÃO diz:** que Sánchez-Vallet é "a autoridade em septoriose na Espanha".
Diz que é quem mais **publica sobre o patógeno**, com afiliação espanhola, nesta janela.
Publicar muito não é ser autoridade — a §8 da missão proíbe essa conversão.

---

### CASE-010 · Um mesmo nome em duas camadas: ciência e rede técnica

```
CASE_ID:                CASE-010
COUNTRY:                ITALY
CROP:                   Vid
REGION:                 Trentino
PROBLEM:                míldio da videira
SOURCES:                EU-T5-001 (OpenAlex) + IT-T3-001 (boletins regionais)
```

**ADAMA_ALIGNMENT: MEDIUM** · **TIER: C · TECHNICAL PROOF**
> ponte ciência↔rede técnica na Itália, em vinha. Mecanismo forte, cultura de segunda prioridade.

**WHAT_HAPPENED**
Buscando quem publica sobre míldio da videira na Itália, o segundo nome mais recorrente é
**Michele Perazzolli (12 trabalhos, 2018–2026)**, da **Fondazione Edmund Mach**.

**WHAT_SINTONIA_CONNECTS**
A Fondazione Edmund Mach é, independentemente, a instituição que publica os *Bollettini
Difesa integrata di base* do Trentino — encontrada na investigação de T3, por outro caminho
e sem relação com a busca científica.

**Ciência (T5) e rede técnica de campo (T7) se encontram na mesma organização.** É o primeiro
elo real do people graph medido nesta missão:
`PERSON → ORGANIZATION → COUNTRY → REGION → CROP → TOPIC → PAPER → DOCUMENT`.

**WHY_ADAMA_SHOULD_CARE**
Uma instituição que ao mesmo tempo publica ciência sobre o patógeno e emite a recomendação
técnica que chega ao produtor é um nó de influência real — não por número de seguidores,
mas por posição na cadeia entre conhecimento e campo.

**RAW_EVIDENCE**   `data/samples/EU-T5-001-openalex-people.json` · ficha IT-T3-001 no atlas de fontes
**SCREEN_AVAILABLE**   ainda não
**STATUS**             **REAL** (as duas ocorrências) + **DERIVED** (a ligação entre elas)

**O que este caso NÃO diz:** que a pessoa ou a instituição tenha influência comercial sobre
decisão de compra. Isso não foi medido e não está nestes dados.

---

### CASE-011 · Toda a nova plataforma europeia de cereal da ADAMA depende de uma molécula com data

```
CASE_ID:                CASE-011
COUNTRY:                EUROPEAN UNION → FRANCE · SPAIN · ITALY
CROP:                   Trigo, cevada, triticale, centeio
PROBLEM:                exposição concentrada numa única substância ativa
TIME:                   atos da UE de 2019 a 2025; registro francês de 25/08/2026
SOURCES:                EU-T4-001 (CELLAR) · FR-T4-001 (E-Phy) · radar público ADAMA
CROSSING:               X-006 (UE → nacional) + radar público
```

**ADAMA_ALIGNMENT: HIGH** · **TIER: A · HERO CASE**
> Cereal é **CORE PUBLIC SIGNAL nos três países** e a plataforma em questão é a que a
> própria ADAMA está lançando agora.

**WHAT_HAPPENED**
A ADAMA lançou na Europa cinco novos fungicidas de cereal — **Avastel, Forapro, Maxentis,
Maganic e Soratel**. Os cinco são formulações de **protioconazol**.

Na França, o registro oficial mostra a ADAMA com **exatamente três** produtos autorizados
contendo protioconazol, e são os três da nova plataforma:

| AMM | produto | composição |
|---|---|---|
| 2240236 | **AVASTEL** | protioconazol 150 g/L + fluxapiroxade |
| 2240001 | **FORAPRO** | protioconazol 175 g/L + fenpropidina |
| 2230815 | **MAXENTIS** | protioconazol 150 g/L + azoxistrobina |

**WHAT_SINTONIA_CONNECTS**
Do outro lado, o Jornal Oficial da UE:

- **CELEX 32025R0787** (24/04/2025): *"row 168, Prothioconazole, the date is replaced by
  **'31 March 2027'**"*.
- A aprovação foi **prorrogada seis vezes em seis anos**: 32019R0707 · 32020R0869 ·
  32021R0745 · 32022R0708 · 32023R0918 · 32025R0787.
- O **Parlamento Europeu objetou três vezes** a essas prorrogações: 52019IP0026 ·
  52020IP0197 · 52021IP0285.

E o contexto competitivo, do mesmo registro: dos **77 produtos autorizados com protioconazol
na França, 32 são da Bayer** — originadora da molécula.

**WHY_ADAMA_SHOULD_CARE**
Uma pessoa da ADAMA que abrisse esta tela veria, num lugar só, algo que hoje vive em três
departamentos diferentes: **o lançamento comercial**, **o horizonte regulatório da molécula
que o sustenta** e **quem mais depende dela**. Nenhuma dessas três informações é secreta.
O que não existe hoje é alguém as vendo juntas, na mesma semana, automaticamente.

**RAW_EVIDENCE**   `data/samples/RADAR-ADAMA-prothioconazole.json` · `docs/adama/RADAR-ADAMA-EAME.md`
**SCREEN_AVAILABLE**   sim — protótipo V2
**STATUS**             **REAL** (atos, AMMs e composições) + **DERIVED** (a ligação entre plataforma e horizonte)

> **RED TEAM — a mentira que esta tela poderia contar.**
> *"A ADAMA vai perder sua plataforma de cereal em março de 2027."* **Falso.**
> Expiração de aprovação **não é retirada**: o protioconazol está em processo de renovação, e
> as prorrogações sucessivas existem exatamente porque a avaliação não terminou. O que o
> padrão mostra é **incerteza regulatória prolongada e politicamente contestada** — não
> perda iminente. A tela precisa dizer "expiração da aprovação da substância na UE", nunca
> "fim do produto". E a exposição da Bayer ser maior em número de registros **não** significa
> que a Bayer esteja mais exposta comercialmente.

---

### CASE-012 · O repilo que ninguém vê ainda — olivar andaluz, 2026

```
CASE_ID:                CASE-012
COUNTRY:                SPAIN (Andalucía)
CROP:                   Olivar (Olea europaea — OLVEU)
REGION:                 Jaén · Sevilla · Granada · Córdoba · Málaga · Cádiz · Huelva
PROBLEM:                Repilo (Venturia oleaginea / Spilocaea oleagina)
TIME:                   safra 2026, amostragem semanal de janeiro a 19/08/2026
SOURCES:                ES-T3-001 (RAIF Andalucía) — 20.970 amostragens de olivar em 2026
CROSSING:               província × data × cultura × doença × estado da infecção
```

**ADAMA_ALIGNMENT: HIGH** · **TIER: A · HERO CASE**
> **Neptune** é o fungicida da ADAMA para repilo na Espanha, e a empresa participa da
> jornada **Plan STAR Olivar**. Cultura certa, país certo, problema certo — ver
> `docs/adama/RADAR-ADAMA-EAME.md` §2.

**WHAT_HAPPENED**
A rede andaluza mede o repilo em três estados distintos, e a diferença entre eles é a
decisão de campo:

| Província | % folhas com repilo **visível** | % repilo **incubado** | condições favoráveis (0–3) | leituras |
|---|---|---|---|---|
| **Huelva** | **8,83%** | 3,00% | — | 18 |
| **Cádiz** | **8,01%** | 1,00% | — | 141 |
| Sevilla | 2,74% (máx **73%**) | 3,14% | 2,40 | 674 |
| Córdoba | 2,37% | **3,55%** | 1,67 | 466 |
| **Málaga** | 1,08% | **3,54%** | **2,50** | 166 |
| Jaén | 0,77% (máx 21%) | 2,53% | 2,34 | 1.047 |
| Granada | 0,61% | 0,21% | — | 477 |

**WHAT_SINTONIA_CONNECTS**
Duas leituras que só existem porque a fonte separa visível de incubado:

1. **A doença é provincial, não regional — de novo.** Cádiz e Huelva têm cerca de **dez
   vezes** mais repilo visível que Jaén, a maior província olivareira da Espanha. O mesmo
   padrão encontrado na videira (CASE-007) reaparece em outra cultura, com outra doença,
   por medição independente.
2. **Em Málaga e Córdoba há mais repilo incubado do que visível** — 3,54% contra 1,08% em
   Málaga, 3,55% contra 2,37% em Córdoba. *Incubado* é a infecção já instalada e ainda sem
   sintoma. É precisamente a informação que decide se o tratamento é preventivo ou tardio, e
   é invisível para quem só olha a folha.

**WHY_ADAMA_SHOULD_CARE**
Neptune é vendido pela **janela de aplicação ampliada**. A janela útil é definida por
condições favoráveis e por infecção latente — as duas coisas que esta fonte publica,
semanalmente, por província, de graça. Uma recomendação técnica ou uma campanha em Málaga
baseada em sintoma visível chegaria tarde; baseada em incubado, chegaria na hora.

**RAW_EVIDENCE**   `data/samples/ES-T3-001-raif-olivar-repilo-2026.json`
**SCREEN_AVAILABLE**   sim — protótipo V2
**STATUS**             **REAL** (medições da rede oficial) + **DERIVED** (médias por província)

> **RED TEAM — o que esta tela poderia fazer alguém acreditar e os dados não provam.**
> *"Cádiz e Huelva são os focos do repilo na Andaluzia."* **Cuidado:** Huelva tem **18
> leituras** e Cádiz **141**, contra 1.047 em Jaén. Uma média alta sobre poucas parcelas não
> é a mesma coisa que uma média baixa sobre muitas — e as parcelas do RAIF são de
> acompanhamento técnico, não uma amostra aleatória da província. O número de leituras
> **precisa** aparecer ao lado da média em qualquer tela.
> E *"há mais doença do que parece"* não vale como generalização: incubado maior que visível
> foi observado em Málaga e Córdoba, **não** nas sete províncias.

---

### CASE-013 · O sinal que sobe há quatro safras — e sobrevive ao controle de coorte

```
CASE_ID:                CASE-013
TITLE:                  Repilo em alta em Cádiz e Huelva, plano em Jaén — 11 safras medidas
COUNTRY:                SPAIN (Andalucía)
REGION:                 Cádiz · Huelva · Jaén (controle)
CROP:                   Olivar (OLVEU)
PROBLEM:                Repilo (Venturia oleaginea)
DATE / PERIOD:          safras 2016–2026 · 44.584 leituras
SOURCES:                ES-T3-001 (RAIF Andalucía), CC BY 4.0
CROSSINGS:              província × safra × parcela × doença
ADAMA_ALIGNMENT:        **HIGH** — Neptune (fungicida ADAMA para repilo) e Plan STAR Olivar
PRESENTATION_VALUE:     **ALTA** — é o único caso que fecha o fluxo do SLIDE 8 do deck
```

**FACT — o que a fonte diz**
Percentual médio de folhas com repilo visível, por safra:

| safra | Cádiz | Huelva | Jaén |
|---|---|---|---|
| 2022 | 2,83 | 1,45 | 1,04 |
| 2023 | 4,64 | 1,19 | 0,73 |
| 2024 | 3,89 | 3,26 | 0,82 |
| 2025 | 5,60 | 6,45 | 0,91 |
| **2026** | **8,01** | **8,83** | **0,77** |

**Cádiz e Huelva estão no maior valor de onze safras.** Jaén, a maior província olivareira
da Espanha, está plana há uma década.

**INTERPRETATION — o que nós derivamos, e o controle que fizemos**
A média pode subir só porque as parcelas mudaram. Testamos: comparamos a média de **todas**
as parcelas com a média **apenas das parcelas que também são amostradas em 2026**.

| | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|
| Huelva — mesma coorte | 1,17 | 3,00 | 6,26 | **8,83** |
| Cádiz — mesma coorte | 5,01 | 3,97 | 6,23 | **8,01** |
| **Jaén — mesma coorte (controle)** | 0,56 | 0,73 | 0,90 | **0,77** |

**A alta persiste nas mesmas parcelas, e o controle fica plano.** Não é troca de amostra.

**UNKNOWN — o que não sabemos**
Por que sobe. Não medimos variedade, manejo, idade do olival nem — o mais importante — o
**programa de fungicida aplicado**, que a RAIF registra e nós não cruzamos. E Huelva tem
**7 parcelas** em 2026: a tendência é consistente, a base é pequena.

**ACTION — o que a ADAMA poderia decidir**
Priorizar Cádiz e Huelva na comunicação técnica e no posicionamento de Neptune para a
próxima safra, e validar em campo se a alta corresponde a pressão real ou a mudança de
manejo. **O SINTONIA não decide: ele diz onde olhar** — que é exatamente o que o SLIDE 8
do deck promete.

**O FLUXO DO SLIDE 8, EXECUTADO**

| pergunta do deck | resposta |
|---|---|
| **Signal appears** | ✅ repilo visível em alta em duas províncias |
| **Is it real?** | ✅ **sim** — 11 safras, 44.584 leituras, sobrevive ao controle de coorte |
| **Where else?** | ✅ **Cádiz e Huelva sim; Jaén, Sevilla, Córdoba, Granada e Málaga não** |
| **What supports it?** | ⚠️ **parcial** — a própria fonte publica "condições favoráveis"; clima não foi testado para este caso |
| **Does ADAMA have a response?** | ✅ **sim** — Neptune, com sinal público em olivar na Espanha |
| **What should we validate?** | ✅ programa de fungicida nas parcelas, e a base pequena de Huelva |

**Cinco das seis perguntas do fluxo têm resposta.** A sexta é justamente a pergunta que o
deck diz que o sistema deve devolver.

**RAW_EVIDENCE**   `data/samples/ES-T3-001-repilo-serie-historica.json`
**STATUS**             **REAL** (as medições) + **DERIVED** (médias e controle de coorte)
**TIER**               **A · HERO CASE**

> **RED TEAM.** *"O repilo está explodindo na Andaluzia."* **Falso.** Está subindo em duas
> das sete províncias e **plano ou em queda nas outras cinco**. A média andaluza continua
> não descrevendo ninguém. E *"subiu 7× desde 2023"* em Huelva é verdade sobre **7 parcelas**
> — o n precisa aparecer ao lado do número, sempre.

---

### CASE-014 · A mesma molécula em dois mercados — e a data que se repete

```
CASE_ID:                CASE-014
TITLE:                  Protioconazol: 8 produtos ADAMA em FR e IT, uma data europeia
COUNTRY:                EUROPEAN UNION → FRANCE · ITALY  (SPAIN: NÃO SEI)
CROP:                   Trigo, cevada, triticale, centeio
PROBLEM:                exposição de plataforma a uma única substância
DATE / PERIOD:          registro FR 25/08/2026 · registro IT 24/08/2026 · ato UE 24/04/2025
SOURCES:                EU-T4-001 · FR-T4-001 · IT-T4-001 · radar público ADAMA
CROSSINGS:              X-006 (substância normalizada, 82,1% do uso)
ADAMA_ALIGNMENT:        **HIGH** — cereal é CORE PUBLIC SIGNAL nos três países
PRESENTATION_VALUE:     **ALTA** — é a prova literal de "make relevant signals travel"
```

**FACT — o que as fontes dizem**

| | França | Itália |
|---|---|---|
| produtos autorizados com protioconazol | **77** | **85** |
| Bayer (originadora) | **32** | **18** |
| **ADAMA** | **3** | **5** |
| datas de vencimento publicadas | ❌ o registro francês não tem o campo | ✅ |

Os produtos ADAMA, por mercado:

| França (AMM) | Itália (nº reg.) | vencimento IT |
|---|---|---|
| AVASTEL 2240236 | AVASTEL 018089 | 31/03/2028 |
| FORAPRO 2240001 | — | — |
| MAXENTIS 2230815 | MAXENTIS 018067 | 31/05/2027 |
| — | MAGANIC 017955 | 31/01/2028 |
| — | **SORATEL 018175** | **31/03/2027** |
| — | KOJAMI 019095 | 31/05/2027 |

**INTERPRETATION — o que nós derivamos**

1. **A molécula atravessa os mercados, e o portfólio também.** AVASTEL e MAXENTIS estão
   autorizados nos dois países. A Itália tem três produtos que a França não tem — incluindo
   **SORATEL**, o quinto dos cinco lançamentos europeus, e **KOJAMI**, que o material de
   imprensa não citava e só aparece no registro.
2. **A data se repete.** A aprovação europeia do protioconazol expira em **31/03/2027**
   (CELEX 32025R0787, linha 168). A autorização italiana do **SORATEL vence exatamente em
   31/03/2027**. O vencimento nacional está **ancorado** na aprovação europeia da substância
   — é o acoplamento que a *lane* "Regulation & Portfolio" do deck promete, visível num
   número.
3. **A assimetria entre registros é ela própria informação.** A França publica cultura × alvo
   e não publica vencimento; a Itália publica vencimento e não publica cultura × alvo.
   Uma visão EAME honesta mostra as duas metades, não uma média.

**UNKNOWN — o que não sabemos**
A **Espanha**: sem dump aberto do registro de produtos, não sabemos quantos produtos com
protioconazol existem lá nem quais são da ADAMA — embora o Avastel tenha sido anunciado
publicamente no mercado espanhol. Também não sabemos vendas, prioridade comercial, nem quem
**fabrica** a substância (o registro traz titular, não fabricante).

**ACTION — o que a ADAMA poderia decidir**
Tratar a renovação europeia do protioconazol como evento de portfólio, não como assunto
regulatório isolado, e verificar se a exposição italiana (5 produtos, dois vencendo em 2027)
está no mesmo plano que a francesa.

**RAW_EVIDENCE**   `data/samples/CROSS-MARKET-prothioconazole-cereal.json`
**STATUS**             **REAL** (contagens, AMMs, nºs de registro e datas) + **DERIVED** (a leitura de acoplamento)
**TIER**               **A · HERO CASE — o melhor caso cross-market disponível**

> **RED TEAM.** *"A ADAMA perde SORATEL em março de 2027."* **Falso.** A coincidência de
> datas mostra **ancoragem administrativa**, não desfecho: se a renovação europeia avançar, a
> data nacional acompanha. E *"a Bayer está mais exposta"* também não se sustenta — ela tem
> mais **registros**, o que não é mais **exposição comercial**.

---

### CASE-015 · O concorrente chegou 18 meses depois — e com outro nome no registro

```
CASE_ID:                CASE-015
TITLE:                  Azoxistrobina + protioconazol na Itália: cronologia e identidade
COUNTRY:                ITALY
CROP:                   Trigo tenro e duro, cevada, triticale, centeio
PROBLEM:                septoriose, ferrugens, oídio, fusariose da espiga
DATE / PERIOD:          registros de 06/2024 a 12/2025 · registro consultado em 24/08/2026
SOURCES:                IT-T4-001 (Ministero della Salute) + comunicação técnica pública
CROSSINGS:              X-005 (concorrente × combate) + X-006 (substância normalizada)
ADAMA_ALIGNMENT:        **HIGH** — cereal é CORE PUBLIC SIGNAL nos três países
PRESENTATION_VALUE:     **ALTA** — prova a *lane* Competitor do deck com fato administrativo
```

**FACT — o que o registro italiano diz**
Produtos em vigor na Itália com a dupla **azoxistrobina + protioconazol**:

| nº reg. | produto | titular do registro | registrado em | vence em |
|---|---|---|---|---|
| 018067 | **MAXENTIS** | ADAMA ITALIA S.R.L. | **14/06/2024** | 31/05/2027 |
| 019095 | **KOJAMI** | ADAMA ITALIA S.R.L. | 29/09/2025 | 31/05/2027 |
| 019093 | PROMINO XTRA | **CAC CHEMICAL GMBH** | 03/10/2025 | 31/03/2028 |
| 019194 | **AMISTAR ERA 240 EC** | **CAC CHEMICAL GMBH** | **29/12/2025** | 31/03/2028 |

E a comunicação técnica pública italiana apresenta **AMISTAR® ERA 240 EC como a novidade
Syngenta para cereais em 2026**, com azoxistrobina e protioconazol, autorizada em trigo
tenro e duro, centeio, cevada e triticale.

**INTERPRETATION — duas leituras, ambas verificáveis**

1. **Cronologia competitiva.** Na mesma combinação de substâncias, a ADAMA registrou primeiro
   — **MAXENTIS em junho de 2024**, contra **AMISTAR ERA em dezembro de 2025**. Dezoito meses
   de diferença, legíveis no ato administrativo, não em opinião de mercado.

2. **O titular do registro não é a marca.** O AMISTAR é marca Syngenta na comunicação, mas o
   **titular do registro italiano é CAC CHEMICAL GMBH**. Este é o problema do DECK-015
   (*same competitor*) num caso concreto: contar "Syngenta" pelo campo `ragione_sociale`
   **teria perdido este produto**.

**UNKNOWN**
Se CAC Chemical atua como titular por conta da Syngenta, por acordo, ou de forma
independente — o registro **não diz**, e nós **não inferimos**. Também não sabemos vendas,
preço, nem qual dos produtos tem distribuição efetiva.

**ACTION**
Para MARKET DEVELOPMENT: a vantagem temporal da ADAMA nessa combinação é verificável e tem
prazo — os dois produtos ADAMA vencem em **31/05/2027**, antes dos dois concorrentes
(31/03/2028). Para COMPETITIVE: a normalização de titular → grupo (**G4**) deixa de ser
detalhe técnico e vira **pré-requisito**, com evidência.

**RAW_EVIDENCE**   `data/samples/COMPETITOR-azoxy-prothio-italy.json`
**STATUS**             **REAL** (registros e datas) + **DERIVED** (a leitura de cronologia)
**TIER**               **A · HERO CASE**

> **RED TEAM.** *"A Syngenta copiou a ADAMA."* **Não afirmável** — combinações de
> substâncias não são exclusivas e a ordem de registro não estabelece originalidade.
> *"CAC Chemical é a Syngenta."* **Não afirmável** — a relação societária não está no
> registro. O que é afirmável: **as datas de registro e a identidade do titular**, e que
> quem contar concorrente por razão social **erra este caso**.

---

| CASE_ID | País | Cultura | Status | Tela |
|---|---|---|---|---|
| CASE-001 | EU → FR | Vigne | REAL | ainda não |
| CASE-002 | EU → FR | — | REAL | ainda não |
| CASE-003 | IT | — | REAL + DERIVED | ainda não |
| CASE-004 | ES | 45 combinações | REAL | ainda não |
| CASE-005 | FR | Trigo comum | REAL + DERIVED | ainda não |
| CASE-006 | ES | Trigo comum | REAL + DERIVED | ainda não |
| CASE-007 | ES | Vid | REAL | ainda não |
| CASE-008 | ES | Vid | REAL + DERIVED | ainda não |
| CASE-009 | ES | Trigo | REAL | ainda não |
| CASE-010 | IT | Vid | REAL + DERIVED | ainda não |
| CASE-011 | EU → FR/ES/IT | Cereais | REAL + DERIVED | protótipo V2 |
| CASE-012 | ES | Olivar | REAL + DERIVED | protótipo V2 |
| CASE-013 | ES | Olivar | REAL + DERIVED | — (missão só texto) |
| CASE-014 | EU → FR/IT | Cereais | REAL + DERIVED | — (missão só texto) |
| CASE-015 | IT | Cereais | REAL + DERIVED | — (missão só texto) |
