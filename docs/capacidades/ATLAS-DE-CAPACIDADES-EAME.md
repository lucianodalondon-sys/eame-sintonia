# ATLAS DE CAPACIDADES — SINTONIA EAME

Fonte não é capacidade. Este atlas converte descoberta em **o que conseguimos saber**.

> "Existe um portal francês de alertas fitossanitários" é uma fonte.
> "Detectar alertas fitossanitários regionais em trigo na França" é uma capacidade.
> A segunda só entra aqui quando a primeira está provada com exemplo real.

**Estado:** MISSÃO 02 em curso — **13 capacidades COMPROVADAS**.
**Última atualização:** 2026-08-28

---

## FICHA DA CAPACIDADE

```
CAPABILITY:          # frase única, verificável. "Detectar X, em Y, para Z."
SOURCE:              # SOURCE_ID(s) do ATLAS DE FONTES que a sustentam
COUNTRY:
CROP:
GEOGRAPHY:           # granularidade REAL alcançada
TIME:                # janela temporal coberta
UPDATE_FREQUENCY:
CAN_AUTOMATE:        # SIM | NÃO | PARCIAL | NÃO SEI
CAN_HISTORY:         # dá para reconstruir série histórica?
CONFIDENCE:          # COMPROVADO | INFERÊNCIA | HIPÓTESE | NÃO SEI
ADAMA_DECISION:      # que decisão real da ADAMA isso informa
REAL_EXAMPLE:        # o caso concreto que prova a capacidade
```

Uma capacidade sem `REAL_EXAMPLE` **não pode** ter `CONFIDENCE: COMPROVADO`.

---

## MATRIZ DE USUÁRIOS ADAMA

Cada capacidade marca seus **possíveis** consumidores. O caminho é
**DADO → DECISÃO → POSSÍVEL USUÁRIO**, nessa ordem.

| Usuário | Sigla |
|---|---|
| EAME Management | EAME |
| Country Management | COUNTRY |
| Marketing | MKT |
| Commercial | COM |
| Market Development | MD |
| Regulatory | REG |
| Portfolio | PORT |
| Technical | TEC |
| R&D | RND |
| Communication | COMM |

**Não criar módulo por departamento ainda.** A matriz aqui é de identificação, não de arquitetura.

---

## REGISTRO DE CAPACIDADES

### CAP-001 · Vigiar toda decisão da UE sobre substância ativa, com data e identificador

```
CAPABILITY:          Detectar, de forma repetível e datada, todo ato da UE que aprove,
                     renove, altere ou retire uma substância ativa fitossanitária —
                     com identificador oficial (CELEX), data e texto integral.
SOURCE:              EU-T4-001 (CELLAR / Publications Office)
COUNTRY:             EUROPE (camada EU ACTIVE SUBSTANCE)
CROP:                não aplicável — o ato regula substância, não cultura
GEOGRAPHY:           União Europeia. NÃO desce a país, região ou cultura.
TIME:                todo o acervo CELEX; verificado de 2026-01 a 2026-07
UPDATE_FREQUENCY:    contínua (cada edição do Jornal Oficial)
CAN_AUTOMATE:        SIM — SPARQL público + content negotiation, sem chave, sem scraping.
                     Reproduzível por `scripts/cellar.sh`.
CAN_HISTORY:         SIM — série histórica completa por CELEX
CONFIDENCE:          COMPROVADO
ADAMA_DECISION:      REGULATORY: antecipar perda de substância e janela de expiração.
                     PORTFOLIO: ler o calendário de expirações do mercado europeu.
                     R&D / MARKET DEVELOPMENT: ver o que sai e abre espaço.
REAL_EXAMPLE:        CELEX 32026R1696 (14/07/2026) — renovação do ácido pelargônico,
                     CAS 112-05-0, CIPAC 888, aprovação 01/10/2026, expiração 30/09/2041.
                     Evidência: data/samples/EU-T4-001/
USERS:               REG (primário) · PORT · RND · MD · EAME
```

**Limite declarado:** esta capacidade prova o **ato europeu**. Ela **não** informa se existe
produto comercial autorizado em França, Espanha ou Itália, nem para que cultura ou alvo.
Isso é a camada NATIONAL PRODUCT AUTHORIZATION, ainda não investigada.

### CAP-002 · Ler o mesmo fato regulatório em EN, FR, ES e IT sem perder o original

```
CAPABILITY:          Obter o texto integral oficial de um mesmo ato regulatório da UE em
                     inglês, francês, espanhol e italiano, preservando o original de cada
                     língua e mantendo o mesmo identificador de documento.
SOURCE:              EU-T4-001
COUNTRY:             EUROPE (com leitura direta para FRANCE, SPAIN, ITALY)
GEOGRAPHY:           UE
TIME:                acervo CELEX
UPDATE_FREQUENCY:    contínua
CAN_AUTOMATE:        SIM — mesmo endpoint, header Accept-Language
CAN_HISTORY:         SIM
CONFIDENCE:          COMPROVADO
ADAMA_DECISION:      COMMUNICATION / COUNTRY MANAGEMENT: falar do mesmo fato regulatório
                     na língua de cada país usando a redação oficial daquele país, e não
                     uma tradução nossa.
REAL_EXAMPLE:        CELEX 32026R1696 obtido em eng (13.892 car.), fra (15.590),
                     spa (15.667) e ita (15.181). Títulos oficiais preservados em
                     data/samples/EU-T4-001/evidence-32026R1696.json
USERS:               COMM · COUNTRY · REG · MKT
```

**Por que isso importa:** resolve o requisito multilíngue da missão (§14) na sua forma mais
forte — não guardamos tradução, guardamos **a versão oficial em cada língua**, com o mesmo
CELEX ligando as quatro. `NORMALIZED_ENGLISH` aqui não é tradução automática: é a versão EN
oficial.

### CAP-003 · Saber o que é legalmente vendável na França, por cultura e por alvo

```
CAPABILITY:          Determinar, para qualquer produto fitofarmacêutico autorizado na
                     França, em que cultura e contra que alvo ele pode ser usado, com dose,
                     estádio BBCH, DAR, nº máximo de aplicações e zonas de não tratamento.
SOURCE:              FR-T4-001 (ANSES E-Phy)
COUNTRY:             FRANCE (camada NATIONAL PRODUCT AUTHORIZATION)
CROP:                todas as culturas do catálogo francês
GEOGRAPHY:           PAÍS. A AMM é nacional — não há recorte regional. Forçar região aqui
                     seria inventar granularidade.
TIME:                estado corrente + data de decisão por uso + data de 1ª autorização
                     e de retirada por produto
UPDATE_FREQUENCY:    semanal
CAN_AUTOMATE:        SIM — dados abertos, `scripts/ephy.sh download`
CAN_HISTORY:         PARCIAL — o dataset é um retrato do estado atual. Série histórica
                     exige arquivar as versões semanais a partir de agora. Datas de
                     retirada e de 1ª autorização dão profundidade parcial retroativa.
CONFIDENCE:          COMPROVADO
ADAMA_DECISION:      REGULATORY / COMMERCIAL / MARKET DEVELOPMENT: o que se pode vender,
                     onde há uso autorizado e onde não há.
REAL_EXAMPLE:        15.140 produtos, 18.558 usos autorizados. AMM 2080088 NEMO
                     (nicosulfuron 40 g/L) — Maïs*Désherbage, 1,5 L/ha, ZNT aquática 20 m.
USERS:               REG · COM · MD · PORT · TEC
```

### CAP-004 · Ler o portfólio ADAMA na França a partir de fonte pública oficial

```
CAPABILITY:          Reconstruir, sem nenhum dado interno, o portfólio autorizado da ADAMA
                     na França — produto, substância ativa, função, cultura, alvo, estado —
                     e o de cada concorrente, a partir do registro oficial.
SOURCE:              FR-T4-001
COUNTRY:             FRANCE
CROP:                Blé (58), Vigne (51), Orge (50), Seigle (32), Crucifères oléagineuses (30)…
GEOGRAPHY:           país
TIME:                estado corrente
UPDATE_FREQUENCY:    semanal
CAN_AUTOMATE:        SIM
CAN_HISTORY:         PARCIAL (ver CAP-003)
CONFIDENCE:          COMPROVADO
ADAMA_DECISION:      PORTFOLIO / MD: onde a ADAMA tem e onde não tem direito de uso;
                     onde um concorrente tem e a ADAMA não.
REAL_EXAMPLE:        ADAMA FRANCE SAS — 267 produtos, 504 usos autorizados.
                     Top cultura×alvo: Vigne×Mildiou (17), Vigne×Black rot (13),
                     Traitements généraux×Limaces et escargots (18), Blé×Septoriose (6).
                     Evidência: data/samples/FR-T4-001/
USERS:               PORT (primário) · MD · COM · REG · EAME
```

**Como isto se relaciona com a pendência P-003:** o portfólio aqui **não é informação
interna da ADAMA** — é o registro público francês, onde a ADAMA FRANCE SAS é titular
nomeada. Nada foi inventado. O que continua `NÃO TESTÁVEL COMPLETAMENTE` é o portfólio
comercial real (vendas, foco, prioridade, pipeline), que não é público.

### CAP-005 · Comparar ADAMA e concorrentes no mesmo par cultura × alvo (França)

```
CAPABILITY:          Para um par cultura × alvo na França, listar quais empresas têm uso
                     autorizado e quantos usos cada uma detém.
SOURCE:              FR-T4-001
COUNTRY:             FRANCE
CROP / TARGET:       qualquer par presente no catálogo
GEOGRAPHY:           país
UPDATE_FREQUENCY:    semanal
CAN_AUTOMATE:        SIM
CAN_HISTORY:         PARCIAL
CONFIDENCE:          COMPROVADO (para a contagem de usos autorizados)
ADAMA_DECISION:      MD / PORTFOLIO / COMMERCIAL: mapear em que combates a ADAMA está
                     presente, ausente ou cercada.
REAL_EXAMPLE:        Vigne × Mildiou(s): ADAMA 17, NUFARM 11, BAYER 8, UPL 7, SYNGENTA 5,
                     CORTEVA/DOW 3, BASF 2.
                     Vigne × Black rot: ADAMA 13, BASF 5, BAYER 4, SYNGENTA 2, FMC 1, NUFARM 1.
USERS:               MD · PORT · COM · MKT · EAME
```

> **RED TEAM — a conclusão perigosa.** Alguém olhando "ADAMA 17 × BASF 2" pode ler
> *"a ADAMA lidera o mildio da videira na França"*. **Os dados não provam isso.**
> A contagem é de **usos autorizados no registro**, e não de: vendas, área tratada,
> participação de mercado, eficácia, preço ou preferência do produtor. Um titular pode ter
> muitos registros antigos e pouca venda; outro, um único produto dominante. Qualquer tela
> que mostre esta contagem precisa dizer, no próprio bloco, que a unidade é
> **"usos autorizados"** — nunca "posição de mercado".


### CAP-006 · Ligar uma decisão regulatória da UE ao produto ADAMA afetado na França

```
CAPABILITY:          Partindo de um ato da UE sobre uma substância ativa, identificar
                     automaticamente quais produtos autorizados na França dependem dela,
                     de quem são, e em que cultura × alvo são usados.
SOURCE:              EU-T4-001 + FR-T4-001
COUNTRY:             EUROPE → FRANCE
CROP:                resultante (no exemplo: Vigne)
GEOGRAPHY:           UE (ato) → França (produto). Sem granularidade regional.
TIME:                data do ato + data de decisão do uso
UPDATE_FREQUENCY:    contínua (UE) × semanal (França)
CAN_AUTOMATE:        PARCIAL — a chave CAS cobre 3 de 6 atos testados e 621 das 1.338
                     substâncias do E-Phy. Ver X-006 para os limites medidos.
CAN_HISTORY:         PARCIAL
CONFIDENCE:          COMPROVADO para a cadeia; PARCIAL para a cobertura
ADAMA_DECISION:      REGULATORY: qual decisão europeia toca o portfólio da ADAMA na França,
                     e em que cultura. PORTFOLIO: onde há dependência de uma substância
                     com prazo. MD: onde um concorrente está mais exposto que a ADAMA.
REAL_EXAMPLE:        CELEX 32026R1353 (15/06/2026), Metalaxyl-M, CAS 70630-17-0.
                     Na França: 9 produtos autorizados — 7 SYNGENTA, 1 ASCENZA e
                     1 ADAMA (PANDERO GOLD, AMM 2010398, folpel + metalaxil-M),
                     uso Vigne × Mildiou, 2,0 kg/ha.
USERS:               REG (primário) · PORT · MD · TEC · EAME
```

> **RED TEAM — a conclusão perigosa.** Uma tela que mostre "ato da UE → seu produto" convida
> à leitura *"este produto vai ser retirado nesta data"*. **Os dados não provam isso.**
> A expiração da aprovação europeia **não** é a data de retirada do produto nacional, e a
> maioria dos atos de renovação **estende** a aprovação em vez de encerrá-la — no exemplo do
> ácido pelargônico, até 2041. A tela precisa dizer o que a data é: *expiração da aprovação
> da substância na UE*, não *fim do produto na França*.


### CAP-007 · Calendário de vencimento de autorizações na Itália, por empresa

```
CAPABILITY:          Listar, para qualquer empresa, quais autorizações italianas vencem em
                     que data — e comparar a exposição de curto prazo entre empresas.
SOURCE:              IT-T4-001
COUNTRY:             ITALY
GEOGRAPHY:           país
TIME:                registros desde 1970; vencimentos até 2041 no arquivo atual
UPDATE_FREQUENCY:    arquivo datado (versão 2026-08-24)
CAN_AUTOMATE:        SIM (o nome do arquivo muda por versão e precisa ser descoberto)
CAN_HISTORY:         SIM — o arquivo carrega estado, motivo e datas de revogação
CONFIDENCE:          COMPROVADO
ADAMA_DECISION:      REGULATORY: o que precisa de renovação e quando.
                     PORTFOLIO / MD: onde um concorrente tem exposição maior.
REAL_EXAMPLE:        3.712 autorizações em vigor; 3.466 com vencimento futuro.
                     ADAMA ITALIA: 155 com vencimento futuro, das quais **58 em até
                     6 meses (37,4%)** — contra **20,9% do mercado** no mesmo prazo.
                     Seis produtos ADAMA venceram em 31/08/2026 (LAMDEX EXTRA, FORZA,
                     NINJA, DURAVIS, ELTIRA — lambda-cialotrina — e LUMA-KL, metaldeído).
USERS:               REG (primário) · PORT · MD · EAME
```

> **RED TEAM — duas conclusões perigosas.**
> 1. *"A ADAMA vai perder 58 produtos na Itália em 6 meses."* **Falso.** Vencimento de
>    autorização abre processo de renovação; a maior parte é renovada. O dado mede
>    **carga de renovação**, não perda.
> 2. *"A ADAMA está mais exposta que os concorrentes."* **Cuidado.** As datas são
>    fortemente agrupadas em fins de mês (344 produtos vencem em 30/06/2029; 123 em
>    31/08/2026), porque seguem o calendário europeu das substâncias ativas. Ainda assim,
>    a diferença 37,4% × 20,9% foi medida sobre o mesmo agrupamento e **é real** — ela
>    reflete quais substâncias compõem o portfólio italiano da ADAMA, não um viés do cálculo.

### CAP-008 · Falar de cultura e de praga nos três países com o mesmo código (EPPO)

```
CAPABILITY:          Traduzir cultura e alvo entre França, Espanha e Itália usando código
                     EPPO e nome científico como chave, em vez de nome comum.
SOURCE:              ES-T4-001 (tabelas oficiais do MAPA)
COUNTRY:             SPAIN (vocabulário) → aplicável a EUROPE, FRANCE, ITALY
GEOGRAPHY:           não aplicável (é vocabulário)
CAN_AUTOMATE:        SIM para o lado espanhol
CAN_HISTORY:         não aplicável
CONFIDENCE:          COMPROVADO para o dicionário; **PARCIAL** para o uso entre países
ADAMA_DECISION:      infraestrutura de toda comparação EAME: sem isto, "míldio" na França,
                     "mildiu" na Espanha e "peronospora" na Itália são três coisas soltas.
REAL_EXAMPLE:        492 culturas e 1.381 pragas indexadas por EPPO.
                     VITVI=Vitis vinifera · PLASVI=Plasmopara viticola ·
                     SEPTTR=Zymoseptoria tritici · GUIGBI=Phyllosticta ampelicida ·
                     UNCINE=Erysiphe necator · TRZAX=Triticum aestivum/durum
USERS:               TEC · RND · MD · PORT (infraestrutura, não tela)
```

### CAP-009 · Ler as necessidades agronômicas não atendidas na Espanha, declaradas pelo Estado

```
CAPABILITY:          Identificar, por cultura e por praga, os problemas para os quais a
                     Espanha reconheceu oficialmente não haver solução autorizada normal —
                     via autorizações excepcionais do art. 53.
SOURCE:              ES-T4-002
COUNTRY:             SPAIN
CROP:                45 combinações vigentes (cítricos, olivo, alcachofa, fresal, champiñón,
                     manzano y peral, remolacha azucarera, cebolla y ajo, lechuga…)
GEOGRAPHY:           nacional, com exceções regionais explícitas quando a fonte as declara
TIME:                situação declarada em 24/08/2026, com início e fim por autorização
UPDATE_FREQUENCY:    NÃO SEI — o arquivo declara a data da situação, não a periodicidade
CAN_AUTOMATE:        SIM (formato .xls legado exige tratamento)
CAN_HISTORY:         NÃO — o arquivo traz apenas as **vigentes**. Série histórica exigiria
                     arquivar as versões a partir de agora.
CONFIDENCE:          COMPROVADO
ADAMA_DECISION:      MARKET DEVELOPMENT / R&D / PORTFOLIO: lista curta e oficial de dores
                     agronômicas sem solução registrada — o oposto de achismo de mercado.
REAL_EXAMPLE:        Manzano y peral × fuego bacteriano (Erwinia amylovora);
                     Champiñón × telaraña (fluxapyroxad 30% SC);
                     Remolacha azucarera × pulgón (flonicamida 50% WG);
                     Cebolla y ajo × Delia antiqua (ciantraniliprol 10% OD).
USERS:               MD (primário) · RND · PORT · TEC
```

> **RED TEAM.** Uma autorização excepcional **não** significa mercado disponível. Significa
> lacuna reconhecida — que pode ser pequena, sazonal, regional, ou já estar sendo resolvida
> por outra empresa. E a lista traz o que está **vigente**: um problema resolvido no ano
> passado saiu da lista sem deixar rastro. Ler isto como "oportunidade de mercado" sem mais
> nada seria fabricar inteligência.


### CAP-010 · Saber onde estão as culturas, por região NUTS 2, com 25 anos de série

```
CAPABILITY:          Determinar a área de cada cultura por região NUTS 2 na França, Espanha
                     e Itália, e acompanhar sua evolução de 2000 a 2024.
SOURCE:              EU-T1-001
COUNTRY:             FRANCE · SPAIN · ITALY
CROP:                trigo comum, cevada, milho grão, beterraba (entre 79 rubricas)
GEOGRAPHY:           **NUTS 2** — 67 regiões com valor em FR/ES/IT
TIME:                2000–2024 (25 anos)
UPDATE_FREQUENCY:    anual
CAN_AUTOMATE:        SIM — API sem chave
CAN_HISTORY:         SIM — a série já vem completa, sem precisar arquivar
CONFIDENCE:          COMPROVADO
ADAMA_DECISION:      MD / COMMERCIAL: onde alocar esforço; que regiões crescem ou encolhem
                     numa cultura ao longo de 25 anos.
REAL_EXAMPLE:        Trigo comum 2024 — ES41 Castilla y León 771,8 mil ha;
                     FRB0 Centre–Val de Loire 544,6; FRE2 Picardie 472,0.
                     Cevada 2024 — ES42 Castilla-La Mancha 702,7 mil ha.
USERS:               MD · COM · EAME · COUNTRY · PORT
```

**Limite:** área sim, **rendimento não**. Rendimento só existe por país (CAP-011).

### CAP-011 · Ler o ano agrícola por país, com série longa

```
CAPABILITY:          Comparar o rendimento nacional de uma cultura ano a ano em FR, ES e IT.
SOURCE:              EU-T1-002
GEOGRAPHY:           PAÍS
TIME:                2010–2026 (ES já com 2026)
CAN_AUTOMATE:        SIM
CONFIDENCE:          COMPROVADO
ADAMA_DECISION:      COUNTRY / EAME: distinguir ano ruim de tendência.
REAL_EXAMPLE:        Trigo comum, t/ha — FR: 7,28 (2023) → **6,02 (2024)** → 7,34 (2025).
                     ES: 3,07 (2022) → **2,14 (2023)** → 3,74 (2024) → 4,51 (2025).
USERS:               EAME · COUNTRY · MD · COM
```

### CAP-012 · Medir exposição climática por região e por janela fenológica

```
CAPABILITY:          Calcular, para qualquer região NUTS 2 e qualquer janela do calendário
                     agrícola, indicadores climáticos diários — dias de calor, chuva
                     acumulada, temperaturas extremas — com série histórica.
SOURCE:              EU-T2-001 (NASA POWER) + EU-T2-002 (pontos NUTS 2)
COUNTRY:             FRANCE · SPAIN · ITALY
GEOGRAPHY:           **ponto-rótulo da região NUTS 2** — aproximação declarada, não média
TIME:                séries diárias, décadas
UPDATE_FREQUENCY:    diária
CAN_AUTOMATE:        SIM — sem chave, sem cota observada
CAN_HISTORY:         SIM
CONFIDENCE:          COMPROVADO
ADAMA_DECISION:      TECHNICAL / MD: em que regiões e em que anos houve estresse na fase
                     sensível da cultura.
REAL_EXAMPLE:        Dias com Tmáx ≥ 30 °C entre 01/05 e 30/06 —
                     ES41: 11 (2022), 6 (2023), 4 (2024);
                     FRB0: 5, 3, **0**; FRI3 Poitou-Charentes: 13, 3, **0**.
                     Chuva na mesma janela em FRB0: 118 → 103 → **231 mm**.
USERS:               TEC · MD · RND · COUNTRY
```

### CAP-013 · Escolher a janela certa — e provar que a errada mente

```
CAPABILITY:          Testar se um indicador climático numa dada janela fenológica acompanha
                     o resultado da safra — e detectar quando não acompanha.
SOURCE:              EU-T2-001 + EU-T1-002
COUNTRY:             SPAIN (verificado em Castilla y León / rendimento nacional)
GEOGRAPHY:           ponto NUTS 2 × rendimento **nacional** — granularidades diferentes,
                     e isso é parte do que a capacidade mede
CONFIDENCE:          COMPROVADO como método; **INFERÊNCIA** para qualquer leitura agronômica
ADAMA_DECISION:      TECHNICAL / RND: não construir alerta climático sobre a janela errada.
REAL_EXAMPLE:        ES41, chuva de **fevereiro a abril** × rendimento nacional ES (t/ha):
                     2020 170,9 mm → 4,40 · 2021 142,3 → 4,15 · 2022 120,5 → 3,07 ·
                     **2023 34,9 → 2,14** · 2024 142,2 → 3,74.
                     A mesma comparação na janela **maio–junho** aponta na direção contrária
                     (2023 teve 84 mm, *mais* que os 31 mm de 2022, e mesmo assim foi o pior
                     ano). A janela decide o sinal.
USERS:               TEC · RND (é capacidade de método, não tela de negócio)
```

> **RED TEAM — a conclusão mais perigosa desta missão até aqui.** Cinco pontos alinhados
> **não são** prova de causalidade. A seca de fevereiro–abril de 2023 em Castilla y León e o
> pior rendimento espanhol da série **coincidem**; nada aqui prova que uma causou o outro, e
> o rendimento é **nacional** enquanto a chuva é de **um ponto**. Uma tela que colocasse as
> duas curvas juntas sem dizer isso estaria fabricando inteligência — exatamente o que a §8
> da missão proíbe. O que está provado é a **capacidade de medir**, não a explicação.


### Placar

| CONFIDENCE | Quantidade |
|---|---|
| COMPROVADO | 13 |
| INFERÊNCIA | 0 |
| HIPÓTESE | 0 |
| NÃO SEI | 0 |

### Cobertura por país

| | COMPROVADO | INFERÊNCIA | HIPÓTESE | NÃO SEI |
|---|---|---|---|---|
| EUROPE | 7 | 0 | 0 | 0 |
| FRANCE | 3 | 0 | 0 | 0 |
| SPAIN | 2 | 0 | 0 | 0 |
| ITALY | 1 | 0 | 0 | 0 |

---

## HIPÓTESES DERRUBADAS

Capacidade que caiu **permanece registrada aqui**, com o motivo e a data. Não se reescreve
a história para o relatório ficar mais bonito.

| ID | Capacidade que se supôs | Por que caiu | Data |
|---|---|---|---|
| *(nenhuma ainda)* | | | |
