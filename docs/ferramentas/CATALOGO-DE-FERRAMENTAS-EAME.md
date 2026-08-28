# CATÁLOGO DE FERRAMENTAS — SINTONIA EAME

Ferramenta nasce de cruzamento provado, não de ideia bonita.
Ordem: `SOURCE → EVIDENCE → DATA → CROSSING → CAPABILITY → TOOL → PORTAL`.

**Estado:** MISSÃO 02 em curso — **12 fichas** — 11 qualificadas (CROSSING PROVED ou DATA EXISTS) e 1 ficha CONCEPT, que cobre duas ferramentas sem dado.
**Última atualização:** 2026-08-28

---

## FICHA DA FERRAMENTA

```
TOOL_NAME:
QUESTION:             # a pergunta real que ela responde
USER:                 # EAME | COUNTRY | MKT | COM | MD | REG | PORT | TEC | RND | COMM
DATA_REQUIRED:
SOURCES:              # SOURCE_IDs
CROSSING:             # CROSSING_IDs
REAL_EXAMPLE:
FACT:                 # o que é fato, direto da fonte
DERIVED_ANALYSIS:     # o que é cálculo/derivação nossa
UNKNOWN:              # o que a ferramenta NÃO sabe — declarado, não escondido
ADAMA_VALUE:
TECHNICAL_DIFFICULTY: # BAIXA | MÉDIA | ALTA | NÃO SEI
DATA_RISK:            # licença, GDPR, dependência de fonte única, fragilidade de acesso
PRIORITY:
STATUS:               # CONCEPT | DATA EXISTS | CROSSING PROVED | DEMO POSSIBLE | PROTOTYPE
LIMIT:                # o que ela NAO permite concluir (obrigatorio)
```

`FACT`, `DERIVED_ANALYSIS` e `UNKNOWN` são campos separados **por obrigação**: é a
diferença entre mostrar um dado e mostrar uma conclusão nossa vestida de dado.

---

## CANDIDATAS SUGERIDAS NO BRIEFING

Listadas como **candidatas**, todas em `NÃO QUALIFICADA`.
Nenhuma está aprovada. **A descoberta decide** — só sobe quem tiver dado que a sustente.

| Candidata | Estado |
|---|---|
| CROP PULSE | **QUALIFICADA — CROSSING PROVED** |
| PEST & DISEASE RADAR | **QUALIFICADA — CROSSING PROVED (só Andaluzia)** |
| CLIMATE IMPACT | **QUALIFICADA — CROSSING PROVED** (renomear: mede exposição) |
| SCIENCE RADAR | **QUALIFICADA — CROSSING PROVED** (junto com EXPERT NETWORK) |
| EXPERT NETWORK | **QUALIFICADA — CROSSING PROVED** |
| FIELD VOICES | **CONCEPT** — sem fonte de dado |
| COMPETITIVE RADAR | **QUALIFICADA — CROSSING PROVED** (camada regulatória) |
| REGULATORY WATCH | **QUALIFICADA — CROSSING PROVED** |
| PORTFOLIO OPPORTUNITY | **QUALIFICADA — DATA EXISTS** |
| EMERGING ISSUES | NÃO QUALIFICADA |

Ferramentas descobertas na varredura e que **não** estavam na lista do briefing:
REGISTRATION EXPIRY RADAR · UNMET NEED RADAR · EPPO NORMALIZER.
| EVENT RADAR | NÃO QUALIFICADA |
| COUNTRY PULSE | **QUALIFICADA — DATA EXISTS** |

Uma candidata só vira ferramenta do catálogo com ficha completa e ao menos um
`CROSSING` COMPROVADO por trás.

---

## FERRAMENTAS QUALIFICADAS

### REGULATORY WATCH — `CROSSING PROVED`

```
TOOL_NAME:            REGULATORY WATCH
QUESTION:             "Que decisão regulatória da UE saiu esta semana, sobre que substância,
                       e que produtos autorizados na França ela toca — nossos e dos outros?"
USER:                 REGULATORY (primário) · PORTFOLIO · MARKET DEVELOPMENT · EAME
DATA_REQUIRED:        atos CELEX + catálogo nacional de produtos
SOURCES:              EU-T4-001, FR-T4-001
CROSSING:             X-006
REAL_EXAMPLE:         CASE-001 (Metalaxyl-M → PANDERO GOLD, Vigne × Mildiou)
FACT:                 o ato, sua data, seu CELEX, a substância, o CAS, o período de
                      aprovação; o produto, seu AMM, seu titular, seu uso autorizado
DERIVED_ANALYSIS:     a ligação substância → produtos (feita por nós, via CAS)
UNKNOWN:              cobertura incompleta da chave CAS (X-006); a data de retirada
                      nacional; o impacto comercial
ADAMA_VALUE:          transforma acompanhamento regulatório manual e reativo em vigilância
                      automática ligada ao portfólio registrado
TECHNICAL_DIFFICULTY: BAIXA — duas fontes abertas, sem chave de API, scripts já existem
DATA_RISK:            BAIXO (fontes oficiais, licença aberta). Risco real é de
                      interpretação, não de acesso.
PRIORITY:             ALTA
STATUS:               CROSSING PROVED
LIMIT:                Não permite concluir que um produto será retirado, nem em que data.
                      Não mede mercado.
```

### PORTFOLIO OPPORTUNITY (França) — `DATA EXISTS`

```
TOOL_NAME:            PORTFOLIO OPPORTUNITY
QUESTION:             "Em que pares cultura × alvo os concorrentes têm uso autorizado
                       na França e a ADAMA não tem?"
USER:                 PORTFOLIO · MARKET DEVELOPMENT · COMMERCIAL
SOURCES:              FR-T4-001
CROSSING:             X-004, X-005
REAL_EXAMPLE:         parcial — a base foi provada (18.558 usos autorizados, titulares
                      identificados); a varredura de lacunas ainda não foi rodada
FACT:                 presença ou ausência de uso autorizado por titular × cultura × alvo
DERIVED_ANALYSIS:     a leitura de "lacuna"
UNKNOWN:              se a ausência é estratégica, técnica ou apenas histórica
ADAMA_VALUE:          mapa de espaços brancos apoiado em registro oficial
TECHNICAL_DIFFICULTY: BAIXA
DATA_RISK:            BAIXO
PRIORITY:             ALTA
STATUS:               DATA EXISTS
LIMIT:                Ausência de registro NÃO é ausência de oportunidade nem prova de
                      fraqueza. Pode significar que a molécula não serve àquele alvo.
```

### COMPETITIVE RADAR (camada regulatória) — `CROSSING PROVED`

```
TOOL_NAME:            COMPETITIVE RADAR — camada regulatória
QUESTION:             "Quem tem direito de uso em cada combate agronômico, com que molécula?"
USER:                 MARKET DEVELOPMENT · PORTFOLIO · MARKETING · EAME
SOURCES:              FR-T4-001
CROSSING:             X-005
REAL_EXAMPLE:         Vigne × Mildiou(s) — ADAMA 17, NUFARM 11, BAYER 8, UPL 7,
                      SYNGENTA 5, CORTEVA/DOW 3, BASF 2 (usos autorizados)
FACT:                 titular, produto, substância, cultura, alvo
DERIVED_ANALYSIS:     a contagem e a comparação
UNKNOWN:              vendas, área tratada, participação, eficácia, preço
ADAMA_VALUE:          radar competitivo apoiado em ato administrativo, não em clipping
TECHNICAL_DIFFICULTY: BAIXA
DATA_RISK:            BAIXO no acesso; ALTO na interpretação
PRIORITY:             MÉDIA-ALTA
STATUS:               CROSSING PROVED
LIMIT:                **Contagem de usos autorizados não é participação de mercado.**
                      Ver RED TEAM em CAP-005.
```

### REGISTRATION EXPIRY RADAR (Itália) — `CROSSING PROVED`

```
TOOL_NAME:            REGISTRATION EXPIRY RADAR
QUESTION:             "Que autorizações vencem nos próximos meses, nossas e dos concorrentes,
                       e quem está mais exposto?"
USER:                 REGULATORY · PORTFOLIO · MARKET DEVELOPMENT · EAME
SOURCES:              IT-T4-001
CROSSING:             titular × data de vencimento (interno à fonte)
REAL_EXAMPLE:         CASE-003 — ADAMA 58/155 (37,4%) em ≤6 meses × mercado 20,9%
FACT:                 nº de registro, produto, titular, substância, data de vencimento
DERIVED_ANALYSIS:     o percentual comparativo entre empresas
UNKNOWN:              se a autorização será renovada; o valor comercial de cada uma
ADAMA_VALUE:          planejamento regulatório e leitura de exposição do concorrente
TECHNICAL_DIFFICULTY: BAIXA
DATA_RISK:            BAIXO no acesso; MÉDIO na interpretação (vencimento ≠ perda)
PRIORITY:             ALTA
STATUS:               CROSSING PROVED
LIMIT:                Vencimento não é perda. Só existe para a Itália — França e Espanha
                      não publicam este campo.
```

### UNMET NEED RADAR (Espanha) — `DATA EXISTS`

```
TOOL_NAME:            UNMET NEED RADAR
QUESTION:             "Para que problemas agronômicos o Estado reconheceu que não há
                       solução autorizada?"
USER:                 MARKET DEVELOPMENT · R&D · PORTFOLIO
SOURCES:              ES-T4-002
CROSSING:             —
REAL_EXAMPLE:         CASE-004 — 45 autorizações excepcionais vigentes em 24/08/2026
FACT:                 cultura, problema, substância, produto, início e fim
DERIVED_ANALYSIS:     nenhuma ainda
UNKNOWN:              tamanho do mercado; se outra empresa já está resolvendo; histórico
ADAMA_VALUE:          lista oficial e curta de dores reais, por cultura
TECHNICAL_DIFFICULTY: BAIXA
DATA_RISK:            BAIXO
PRIORITY:             ALTA
STATUS:               DATA EXISTS
LIMIT:                Lacuna reconhecida não é oportunidade dimensionada. Só há a
                      fotografia das vigentes — sem série histórica.
```

### EPPO NORMALIZER — `DATA EXISTS` (infraestrutura, não tela)

```
TOOL_NAME:            EPPO NORMALIZER
QUESTION:             "Isto que a França chama de X e a Espanha chama de Y é a mesma coisa?"
USER:                 nenhum diretamente — é infraestrutura de todas as outras ferramentas
SOURCES:              ES-T4-001
CROSSING:             X-007
REAL_EXAMPLE:         492 culturas e 1.381 pragas com código EPPO e nome científico
FACT:                 o dicionário oficial espanhol
DERIVED_ANALYSIS:     o mapeamento FR → EPPO, que ainda **não existe**
UNKNOWN:              a taxa de acerto do lado francês (nomes comuns, muitos em grupo)
ADAMA_VALUE:          sem isto não existe visão EAME — existem três visões nacionais soltas
TECHNICAL_DIFFICULTY: MÉDIA — o difícil não é o dicionário, é o mapeamento francês
DATA_RISK:            BAIXO
PRIORITY:             ALTA (é pré-requisito de qualquer comparação entre países)
STATUS:               DATA EXISTS
LIMIT:                Não resolve sozinho: o lado francês é grupo, não espécie.
```

### CROP PULSE — `CROSSING PROVED`

```
TOOL_NAME:            CROP PULSE
QUESTION:             "Onde está cada cultura, com que peso por região, e como isso mudou
                       nos últimos 25 anos?"
USER:                 MARKET DEVELOPMENT · COMMERCIAL · COUNTRY · EAME
SOURCES:              EU-T1-001, EU-T1-002
CROSSING:             região NUTS 2 × cultura × ano (nativo na fonte)
REAL_EXAMPLE:         5.685 valores NUTS2 FR/ES/IT, 2000–2024. ES41 771,8 mil ha de trigo.
FACT:                 área por região e ano; rendimento por país e ano
DERIVED_ANALYSIS:     rankings, variações, tendências
UNKNOWN:              rendimento por região — **não existe na fonte**
ADAMA_VALUE:          mapa real de onde está o negócio, com 25 anos de contexto
TECHNICAL_DIFFICULTY: BAIXA
DATA_RISK:            BAIXO
PRIORITY:             ALTA
STATUS:               CROSSING PROVED
LIMIT:                Não dá produtividade regional. Misturar área regional com rendimento
                      nacional para "estimar produção regional" seria inventar dado.
```

### CLIMATE IMPACT — `CROSSING PROVED` (com nome perigoso)

```
TOOL_NAME:            CLIMATE IMPACT
QUESTION:             "Que exposição climática teve cada região na janela sensível da
                       cultura, neste ano e nos anteriores?"
USER:                 TECHNICAL · MARKET DEVELOPMENT · COUNTRY · R&D
SOURCES:              EU-T2-001, EU-T2-002, EU-T1-001
CROSSING:             X-001
REAL_EXAMPLE:         CASE-005 (França 2024) e CASE-006 (Espanha 2023)
FACT:                 séries diárias de temperatura e precipitação; área por região
DERIVED_ANALYSIS:     contagem de dias de estresse, somas por janela, comparação entre anos
UNKNOWN:              o efeito sobre a safra; a média regional real (usamos um ponto)
ADAMA_VALUE:          sinal antecipado e regional de ano atípico
TECHNICAL_DIFFICULTY: BAIXA no dado; **MÉDIA na agronomia** — a janela precisa ser correta
                      por cultura e por país
DATA_RISK:            BAIXO no acesso; **ALTO na interpretação**
PRIORITY:             ALTA
STATUS:               CROSSING PROVED (para exposição)
LIMIT:                **O nome da ferramenta é o seu maior risco.** Ela mede EXPOSIÇÃO,
                      não IMPACTO. Enquanto não houver dado de safra regional e de doença,
                      chamar isto de "impacto" é afirmar o que os dados não provam.
                      Considerar renomear para CLIMATE EXPOSURE.
```

### PEST & DISEASE RADAR — `CROSSING PROVED` (Andaluzia) / `CONCEPT` (FR e IT)

```
TOOL_NAME:            PEST & DISEASE RADAR
QUESTION:             "Onde a pressão de qual praga ou doença está subindo, agora,
                       em que cultura e em que província?"
USER:                 TECHNICAL · COMMERCIAL · MARKET DEVELOPMENT · MARKETING
DATA_REQUIRED:        medição de incidência por local e data
SOURCES:              ES-T3-001 (Andaluzia, numérico) · FR-T3-001 (França, texto em PDF)
                      · IT-T3-001 (Emilia-Romagna, texto em PDF)
CROSSING:             província × data × cultura × doença
REAL_EXAMPLE:         CASE-007 — míldio na vid 2026: Huelva 26,4%, Córdoba 6,4%, Cádiz ≈0%
FACT:                 percentual de cepas/folhas/cachos afetados; capturas em armadilha;
                      sinalizador oficial de condições favoráveis
DERIVED_ANALYSIS:     agregação por província e por semana
UNKNOWN:              **a causa.** Ver X-009 e CASE-008. E a cobertura fora da Andaluzia.
ADAMA_VALUE:          a informação técnica mais acionável encontrada na missão:
                      pressão real, por província, semanal, gratuita
TECHNICAL_DIFFICULTY: BAIXA na Andaluzia (XML aberto);
                      **ALTA na França e na Itália** (PDF descentralizado, sem API)
DATA_RISK:            MÉDIO — depende de uma única região de um único país;
                      coordenadas de parcela pedem revisão jurídica (P-007)
PRIORITY:             ALTA
STATUS:               CROSSING PROVED para Andaluzia · CONCEPT para França e Itália
LIMIT:                **Não explica a causa e não prevê surto.** Agregar províncias produz
                      um número que não descreve nenhuma delas (CAP-015). Fora da
                      Andaluzia, a ferramenta ainda não tem dado numérico — só texto.
```

### EXPERT NETWORK / SCIENCE RADAR — `CROSSING PROVED`

```
TOOL_NAME:            EXPERT NETWORK (com SCIENCE RADAR como a mesma base)
QUESTION:             "Quem trabalha repetidamente com este problema, neste país,
                       em que instituição e desde quando?"
USER:                 R&D · TECHNICAL · MARKET DEVELOPMENT
DATA_REQUIRED:        literatura com autoria, afiliação e país; vocabulário controlado
SOURCES:              EU-T5-001 (OpenAlex) + ES-T4-001 (EPPO / nome científico)
CROSSING:             X-002, X-010
REAL_EXAMPLE:         França × resistência a herbicidas → Christophe Délye (9), INRAE
                      Agroécologie. Itália × míldio da videira → Silvia Laura Toffolatti
                      (17), Università di Milano.
FACT:                 autoria, afiliação, ano, DOI
DERIVED_ANALYSIS:     a contagem de recorrência e o agrupamento por instituição
UNKNOWN:              autoridade real, influência sobre o campo, disponibilidade para
                      parceria, e se o trabalho foi feito naquele país
ADAMA_VALUE:          antena científica dirigida a um problema, e não clipping de papers
TECHNICAL_DIFFICULTY: BAIXA no acesso; **MÉDIA no vocabulário** — sem nome científico a
                      ferramenta responde à pergunta errada (CASE-009)
DATA_RISK:            **ALTO em GDPR** — são pessoas identificadas (P-008)
PRIORITY:             MÉDIA-ALTA
STATUS:               CROSSING PROVED
LIMIT:                **Recorrência não é autoridade.** Afiliação não é local do
                      experimento. E sem vocabulário controlado a lista muda por completo.
                      Não construir ranking universal — a missão proíbe, e com razão:
                      a lista só faz sentido colada a um problema e a um país.
```

### COUNTRY PULSE — `DATA EXISTS`

```
TOOL_NAME:            COUNTRY PULSE
QUESTION:             "Como está o ano agrícola neste país — área, rendimento, preço,
                       clima e pressão de doença?"
USER:                 COUNTRY MANAGEMENT · EAME MANAGEMENT · COMMERCIAL
SOURCES:              EU-T1-001, EU-T1-002, EU-T2-001, EU-T10-001 (+ ES-T3-001 na Espanha)
CROSSING:             país × ano; X-001 na camada regional
REAL_EXAMPLE:         França 2024 (CASE-005) e Espanha 2023 (CASE-006)
FACT:                 área por região, rendimento por país, preço por praça, clima por ponto
DERIVED_ANALYSIS:     a leitura conjunta de "ano bom / ano ruim"
UNKNOWN:              pressão de doença fora da Andaluzia; rendimento por região
ADAMA_VALUE:          uma leitura de país que hoje é montada à mão, se é montada
TECHNICAL_DIFFICULTY: BAIXA — todas as fontes já provadas e sem chave
DATA_RISK:            BAIXO
PRIORITY:             ALTA
STATUS:               DATA EXISTS
LIMIT:                As camadas têm granularidades diferentes (região, país, praça, ponto).
                      Empilhá-las numa tela sem dizer isso cria falsa comparabilidade.
```

### FIELD VOICES / COMPETITIVE RADAR (camada de comunicação) — `CONCEPT`

```
TOOL_NAME:            FIELD VOICES · COMPETITIVE RADAR (comunicação)
QUESTION:             "O que produtores, criadores e concorrentes estão dizendo?"
SOURCES:              nenhuma obtida
STATUS:               **CONCEPT**
LIMIT:                Sem dado. YouTube Data API, Meta Graph e TikTok Research exigem
                      credenciais que não temos; sites de concorrentes devolveram 403/502/404.
                      O RSS público do YouTube funciona **se** o `channel_id` for conhecido —
                      ou seja, o gargalo é a **descoberta**, não a coleta.
                      REACH seria mensurável; FIELD, TECHNICAL e COMMERCIAL AUTHORITY
                      não têm fonte identificada. Ver P-009.
```

