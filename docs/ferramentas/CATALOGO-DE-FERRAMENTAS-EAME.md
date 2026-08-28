# CATÁLOGO DE FERRAMENTAS — SINTONIA EAME

Ferramenta nasce de cruzamento provado, não de ideia bonita.
Ordem: `SOURCE → EVIDENCE → DATA → CROSSING → CAPABILITY → TOOL → PORTAL`.

**Estado:** MISSÃO 02 em curso — **3 ferramentas qualificadas**.
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
| CROP PULSE | NÃO QUALIFICADA |
| PEST & DISEASE RADAR | NÃO QUALIFICADA |
| CLIMATE IMPACT | NÃO QUALIFICADA |
| SCIENCE RADAR | NÃO QUALIFICADA |
| EXPERT NETWORK | NÃO QUALIFICADA |
| FIELD VOICES | NÃO QUALIFICADA |
| COMPETITIVE RADAR | **QUALIFICADA — CROSSING PROVED** (camada regulatória) |
| REGULATORY WATCH | **QUALIFICADA — CROSSING PROVED** |
| PORTFOLIO OPPORTUNITY | **QUALIFICADA — DATA EXISTS** |
| EMERGING ISSUES | NÃO QUALIFICADA |
| EVENT RADAR | NÃO QUALIFICADA |
| COUNTRY PULSE | NÃO QUALIFICADA |

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

