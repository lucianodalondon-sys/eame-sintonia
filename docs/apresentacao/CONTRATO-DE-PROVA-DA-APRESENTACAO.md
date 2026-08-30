# CONTRATO DE PROVA DA APRESENTAÇÃO — SINTONIA EAME

A apresentação comercial já entregue à ADAMA EAME passa a ser o **contrato**. Este documento
transforma cada afirmação dela em um claim rastreável, com o que ele exige, o que já
sustentamos e o que falta.

**Data:** 2026-08-28 · **Piloto:** France · Spain · Italy

---

## PROCEDÊNCIA DESTE CONTRATO — leia antes de usar

> O arquivo da apresentação **não está no repositório** (`find` por `*.pdf`, `*.pptx` e
> `*deck*` não retornou nada). Os claims abaixo foram reconstruídos a partir das **citações
> literais** do briefing de redirecionamento de 2026-08-28, que reproduz as famílias A–H e
> frases exatas do deck.
>
> **Consequência:** a redação de cada `ORIGINAL_CLAIM` é fiel ao que foi citado, mas a
> **numeração de slides é desconhecida** (`SLIDE: NÃO SEI`) e pode haver claims no deck que
> o briefing não citou. Registrado como **P-010**: anexar o arquivo da apresentação ao
> repositório e reconciliar este contrato com ele, claim a claim.

## AS QUATRO CATEGORIAS — separadas por obrigação

| Tipo | O que é | Como se prova |
|---|---|---|
| **A · PROMESSA DE CAPACIDADE** | o sistema *consegue fazer* X | evidência de que X é executável e repetível |
| **B · EXEMPLO ILUSTRATIVO** | um cenário mostrado como ilustração | **não** exige que aquele evento exista; exige que a **capacidade implícita** seja defensável |
| **C · RESULTADO DE NEGÓCIO** | o valor que a ADAMA obteria | exige a capacidade **mais** uma decisão real que ela informa |
| **D · PRINCÍPIO METODOLÓGICO** | como o sistema se comporta | exige que a regra esteja escrita e seja verificável |

**Regra:** um exemplo ilustrativo **não** vira promessa de que aquele evento específico já
foi observado. Mas a capacidade que ele pressupõe **precisa** ser tecnicamente defensável.

## ESTADOS

`PROVED` · `PARTIAL` · `UNPROVED` · `NOT TESTABLE YET`

---

# FAMÍLIA A · EXTERNAL INTELLIGENCE

> A apresentação declara que o SINTONIA trabalha com **FIELD · SCIENCE · COMPETITOR ·
> REGULATION · MOLECULE · DISTRIBUTION · WEATHER · MARKET**. Cada palavra passa a exigir
> definição operacional.

### DECK-001 · REGULATION
```
CLAIM_TYPE:            A · PROMESSA DE CAPACIDADE
SLIDE:                 NÃO SEI
ORIGINAL_CLAIM:        "REGULATION" como camada de inteligência externa
WHAT_IT_REQUIRES:      observar mudança regulatória com identidade documental e data
MINIMUM_PROOF:         um ato real, identificável, datado, recuperável em qualquer momento
REQUIRED_SOURCES:      EU-T4-001 (CELLAR), FR-T4-001 (E-Phy), IT-T4-001 (Min. Salute)
REQUIRED_NORMALIZATION:substância (X-006)
REQUIRED_CROSSING:     X-006
COUNTRIES:             EU + FR + IT provados; ES sem dump aberto (ES-T4-003)
TIME_REQUIREMENT:      contínuo (UE) / semanal (FR) / arquivo datado (IT)
CURRENT_EVIDENCE:      CAP-001, CAP-002, CAP-003, CAP-007, CASE-001, CASE-011
CURRENT_STATUS:        **PROVED**
WHAT_IS_MISSING:       Espanha (registro de produtos em formato aberto)
FAILURE_MODE:          confundir expiração com retirada
ADAMA_ALIGNMENT:       HIGH
```

### DECK-002 · SCIENCE
```
CLAIM_TYPE:            A
ORIGINAL_CLAIM:        "SCIENCE" como camada de inteligência externa
MINIMUM_PROOF:         literatura com autoria, afiliação, país e data, consultável por problema
REQUIRED_SOURCES:      EU-T5-001 (OpenAlex)
REQUIRED_NORMALIZATION:vocabulário controlado — nome científico (X-010)
CURRENT_EVIDENCE:      CAP-017, CAP-018, CASE-009, CASE-010
CURRENT_STATUS:        **PROVED**
WHAT_IS_MISSING:       nada para observar; falta régua para "autoridade"
FAILURE_MODE:          consulta larga entrega a rede errada (medido: 2.627 × 27 trabalhos)
ADAMA_ALIGNMENT:       HIGH (septoriose é alvo declarado do Forapro)
```

### DECK-003 · WEATHER
```
CLAIM_TYPE:            A
MINIMUM_PROOF:         série climática diária, por geografia, com histórico
REQUIRED_SOURCES:      EU-T2-001 (NASA POWER), EU-T2-002 (GISCO)
CURRENT_EVIDENCE:      CAP-012, CAP-013, CASE-005, CASE-006
CURRENT_STATUS:        **PROVED como CONTEXTO**
WHAT_IS_MISSING:       nada para o contexto. Causalidade **não é vendável** (X-009)
FAILURE_MODE:          vender "weather causes agronomic event". Ver §20 do briefing e CASE-008
ADAMA_ALIGNMENT:       MEDIUM
```

### DECK-004 · MARKET
```
CLAIM_TYPE:            A
ORIGINAL_CLAIM:        "MARKET" como camada
WHAT_IT_REQUIRES:      **MARKET não é um dataset** — são variáveis separadas
CURRENT_STATUS:        **PARTIAL**, por variável:
                       · área de cultura por NUTS 2 ....... PROVED (EU-T1-001)
                       · rendimento por país .............. PROVED (EU-T1-002)
                       · rendimento por região ............ NOT AVAILABLE (medido)
                       · preço de cereal por praça ........ PROVED (EU-T10-001)
                       · importação / exportação .......... UNPROVED (FAOSTAT 401; Eurostat mal consultado)
                       · eventos de mercado ............... UNPROVED
                       · presença competitiva ............. PROVED via registro (X-005)
                       · distribuição ..................... UNPROVED — ver DECK-021
WHAT_IS_MISSING:       comércio exterior e eventos de mercado
FAILURE_MODE:          usar "MARKET" como se fosse uma fonte única
ADAMA_ALIGNMENT:       MEDIUM
```

### DECK-005 · COMPETITOR
```
CLAIM_TYPE:            A
CURRENT_STATUS:        **PARTIAL** — duas camadas com destinos opostos:
                       · presença **regulatória** ......... PROVED (X-005, CAP-005)
                       · **comunicação** .................. UNPROVED (X-003 NÃO COMPÕE)
CURRENT_EVIDENCE:      Vigne×Mildiou FR: ADAMA 17, Nufarm 11, Bayer 8, UPL 7, Syngenta 5,
                       Corteva 3, BASF 2 (usos autorizados)
WHAT_IS_MISSING:       toda a camada de comunicação — ver DECK-013 a DECK-016
FAILURE_MODE:          contagem de registros lida como participação de mercado
ADAMA_ALIGNMENT:       HIGH
```

### DECK-006 · MOLECULE
```
CLAIM_TYPE:            A
ORIGINAL_CLAIM:        "MOLECULE" como camada, incluindo origin & manufacturer
WHAT_IT_REQUIRES:      **seis entidades distintas**, nunca sinônimas:
                       manufacturer da substância ativa · manufacturer do formulado ·
                       titular do registro · fonte autorizada · país de fabricação ·
                       país de origem
CURRENT_STATUS:        **PARTIAL**
                       · substância ativa e titular ....... PROVED (registros nacionais)
                       · normalização de substância ....... PROVED com cobertura medida (X-006)
                       · manufacturer / origem autorizada .. **UNPROVED — não investigado**
WHAT_IS_MISSING:       fontes públicas de fabricante e de origem autorizada
FAILURE_MODE:          assumir que registro nacional contém manufacturer. **Não contém**:
                       o E-Phy traz `titulaire`, que é titular de AMM, não fabricante
NEXT_TEST:             procurar fonte pública de "authorized source"/"origem autorizada"
ADAMA_ALIGNMENT:       HIGH
```

### DECK-007 · FIELD
```
CLAIM_TYPE:            A
ORIGINAL_CLAIM:        "FIELD" / "public technical conversations"
CURRENT_STATUS:        **PARTIAL**
                       · medição fitossanitária oficial ... PROVED, **só na Andaluzia** (ES-T3-001)
                       · boletim técnico regional ......... PARTIAL (FR-T3-001, IT-T3-001 — PDF)
                       · conversa pública do campo ........ UNPROVED (T8)
WHAT_IS_MISSING:       França e Itália em formato processável; e toda a camada de vozes
ADAMA_ALIGNMENT:       HIGH
```

### DECK-008 · DISTRIBUTION
```
CLAIM_TYPE:            A
CURRENT_STATUS:        **UNPROVED — não investigado**. Ver DECK-021.
ADAMA_ALIGNMENT:       NÃO SEI
```

---

# FAMÍLIA B · WHAT IT CATCHES

### DECK-009 · "Technical discussion around a crop issue **rises** in one market"
```
CLAIM_TYPE:            B · EXEMPLO ILUSTRATIVO (mas exige capacidade real)
WHAT_IT_REQUIRES:      identificar discussão técnica pública · classificar cultura ·
                       classificar problema · atribuir mercado · **medir mudança temporal** ·
                       distinguir aumento real de simples descoberta de novas fontes
CURRENT_STATUS:        **UNPROVED**
WHAT_IS_MISSING:       a coleta de discussão pública (T8) e, sobretudo, **a linha de base
                       histórica**. Sem histórico comparável não se pode dizer "rises".
FAILURE_MODE:          **snapshot apresentado como tendência.** É o risco mais grave da
                       família B: encontrar três menções e chamar de aumento.
NEXT_TEST:             ver DECK-022 (régua temporal) — sem ela este claim não sobe.
ADAMA_ALIGNMENT:       HIGH
```

### DECK-010 · "A regulatory status changes around an active ingredient"
```
CLAIM_TYPE:            B
WHAT_IT_REQUIRES:      ato · substância · data · tipo de mudança · identidade documental ·
                       ligação com produto nacional · ligação com ADAMA quando existir
CURRENT_STATUS:        **PROVED** — o claim mais bem sustentado do deck inteiro
CURRENT_EVIDENCE:      CASE-011: CELEX 32025R0787 → protioconazol → AVASTEL/FORAPRO/MAXENTIS
                       (AMM 2240236 / 2240001 / 2230815) → expiração 31/03/2027
FAILURE_MODE:          expiração ≠ retirada
ADAMA_ALIGNMENT:       HIGH
```

### DECK-011 · "A competitor **increases** communication around a problem or claim"
```
CLAIM_TYPE:            B
WHAT_IT_REQUIRES:      identidade do concorrente · item de comunicação · data · cultura,
                       problema ou claim · **linha de base histórica** · coleta comparável ·
                       regra de medição
CURRENT_STATUS:        **UNPROVED**
WHAT_IS_MISSING:       tudo. Sites de concorrentes devolveram 403/502/404 (X-003)
FAILURE_MODE:          "encontrar três posts não prova aumento" — citação do próprio briefing
ADAMA_ALIGNMENT:       HIGH
```

### DECK-012 · "A new registration, manufacturer or authorized origin appears"
```
CLAIM_TYPE:            B
WHAT_IT_REQUIRES:      **três acontecimentos diferentes, com fontes diferentes**
CURRENT_STATUS:        **PARTIAL**
                       · NEW REGISTRATION ........ PARTIAL — o registro traz data de primeira
                         autorização (FR) e de registro (IT); detectar "novo" exige arquivar
                         versões semanais, o que ainda não fazemos
                       · NEW MANUFACTURER ........ UNPROVED (ver DECK-006)
                       · NEW AUTHORIZED ORIGIN ... UNPROVED
WHAT_IS_MISSING:       versionamento do registro + fontes de fabricante e origem
NEXT_TEST:             arquivar a versão semanal do E-Phy e a versão datada do CSV italiano
ADAMA_ALIGNMENT:       HIGH
```

---

# FAMÍLIA C · LOCAL TO SHARED

### DECK-013 · Inteligência viaja entre mercados: SAME ISSUE
```
CLAIM_TYPE:            A · promessa estrutural crítica
MINIMUM_PROOF:         um mesmo problema agronômico observado em dois ou três mercados,
                       com o mesmo identificador
CURRENT_STATUS:        **PARTIAL**
CURRENT_EVIDENCE:      míldio da videira existe como PLASVI no vocabulário espanhol e como
                       "Mildiou(s)" no registro francês — mas o casamento FR→EPPO ainda é
                       PARCIAL (X-007). O identificador comum existe do lado espanhol e
                       **falta do lado francês**.
WHAT_IS_MISSING:       fechar X-007
```

### DECK-014 · SAME MOLECULE
```
CLAIM_TYPE:            A
CURRENT_STATUS:        **PROVED com cobertura medida**
CURRENT_EVIDENCE:      X-006 fechado: normalização de substância resolve 63,3% das grafias
                       francesas e **82,1% do uso**; amostra cega **62,2%** das grafias e **77,8%** do uso.
                       Caso real multipaís: **protioconazol** ligando ato da UE a produtos
                       ADAMA na França e a lançamentos na Espanha e na Itália (CASE-011).
WHAT_IS_MISSING:       cobre e enxofre (formas não normalizadas)
```

### DECK-015 · SAME COMPETITOR
```
CLAIM_TYPE:            A
CURRENT_STATUS:        **PARTIAL**
CURRENT_EVIDENCE:      os mesmos grupos aparecem nos registros dos três países. Mas os nomes
                       jurídicos diferem: "SYNGENTA FRANCE SAS", "SYNGENTA ITALIA S.P.A.",
                       "ADAMA FRANCE SAS", "ADAMA ITALIA S.R.L.".
WHAT_IS_MISSING:       **normalização de entidade jurídica → grupo**, com taxa de acerto
                       medida. Ainda não construída.
NEXT_TEST:             normalizador de titular, com amostra cega, nos moldes de X-006
```

### DECK-016 · SIMILAR MOVEMENT
```
CLAIM_TYPE:            A
CURRENT_STATUS:        **NOT TESTABLE YET**
WHAT_IS_MISSING:       "movimento" exige série temporal comparável entre países.
                       Hoje só a Andaluzia tem série de campo. Não há como comparar
                       movimento entre FR, ES e IT em nenhuma camada de campo.
FAILURE_MODE:          declarar "movimento similar" comparando um país com série contra
                       outro sem série
```

---

# FAMÍLIA D · LISTEN · E · UNDERSTAND · F · CONNECT · G · DELIVER

### DECK-017 · "Configured public sources, by market and language. No private conversations."
```
CLAIM_TYPE:            D · PRINCÍPIO METODOLÓGICO
CURRENT_STATUS:        **PROVED como princípio; PARTIAL como cobertura**
CURRENT_EVIDENCE:      <!--M:SOURCE_ID_COUNT-->37<!--/M--> SOURCE_IDs registrados, todos públicos; nenhuma conversa privada
                       foi coletada; licenças registradas por fonte. Ver SOURCE-PACKS-EAME.md
WHAT_IS_MISSING:       packs de FIELD, COMPETITOR, MOLECULE e DISTRIBUTION
```

### DECK-018 · "WHO · WHAT · WHERE · WHEN" + "EVIDENCE: source, date, statement"
```
CLAIM_TYPE:            D
CURRENT_STATUS:        **PARTIAL** — medido por família em CONTRATO-DE-DADOS (abaixo)
CURRENT_EVIDENCE:      as famílias regulatória e fitossanitária entregam os quatro campos;
                       a científica entrega WHO/WHAT/WHEN mas **WHERE é a afiliação do
                       autor, não o local do fato**; a climática não tem WHO.
FAILURE_MODE:          preencher artificialmente campo ausente
```

### DECK-019 · "Local-language sources, normalized into one structure"
```
CLAIM_TYPE:            D
CURRENT_STATUS:        **PARTIAL**
CURRENT_EVIDENCE:      original preservado sempre (CAP-002: o mesmo ato em EN/FR/ES/IT);
                       normalização de substância medida (X-006); normalização agronômica
                       ainda PARCIAL (X-007)
```

### DECK-020 · "CROP × ISSUE × SCIENCE × MOLECULE × COMPETITOR × PORTFOLIO"
```
CLAIM_TYPE:            A · a frase estrutural mais importante do deck
CURRENT_STATUS:        **PARTIAL — a cadeia fecha em 5 de 6 elos num caso real**
CURRENT_EVIDENCE:      cadeia do protioconazol (CASE-011):
                       MOLECULE ✅ protioconazol · PORTFOLIO ✅ 3 AMMs ADAMA ·
                       COMPETITOR ✅ Bayer 32 produtos · ISSUE ✅ septoriose/ferrugem/oídio
                       (alvo declarado do Forapro) · SCIENCE ✅ especialistas em
                       Zymoseptoria (CASE-009) · CROP ✅ trigo
                       — **mas o elo ISSUE↔SCIENCE ainda depende de vocabulário manual**
WHAT_IS_MISSING:       X-007 para tornar o elo ISSUE automático
```

### DECK-021 · DISTRIBUTION como camada
```
CLAIM_TYPE:            A
CURRENT_STATUS:        **UNPROVED — não investigado**
WHAT_IT_REQUIRES:      quem distribui · onde · que culturas atende · que produtos oferece
                       publicamente · mudanças de catálogo · acordos · eventos · rede de
                       cooperativas · presença geográfica
FAILURE_MODE:          afirmar volume distribuído sem dado
NEXT_TEST:             investigação dedicada (item 12 da ordem de execução)
```

### DECK-022 · "Competitor activity is increasing" — a régua temporal
```
CLAIM_TYPE:            A
WHAT_IT_REQUIRES:      UNIT · WINDOW · BASELINE · COMPARABLE SOURCES · MINIMUM_VOLUME ·
                       NORMALIZATION
CURRENT_STATUS:        **UNPROVED**
WHAT_IS_MISSING:       a régua não existe e a coleta também não
```

### DECK-023 · DELIVER: ALERT · MARKET BRIEF · MARKET DEVELOPMENT · MOLECULE WATCH · REGULATORY REVIEW · ASK SINTONIA
```
CLAIM_TYPE:            A
CURRENT_STATUS:        **PARTIAL** — contratos textuais em ARQUITETURA-DE-INFORMACAO-EAME.md
                       · REGULATORY REVIEW ... PROVED
                       · MOLECULE WATCH ...... PARTIAL (falta manufacturer/origem)
                       · MARKET DEVELOPMENT .. PARTIAL
                       · ALERT ............... UNPROVED — falta a régua (REGUA-DE-ALERTA)
                       · MARKET BRIEF ........ PARTIAL
                       · ASK SINTONIA ........ PARTIAL — ver o teste em MATRIZ-DE-PROVA
```

### DECK-024 · "EVERY ANSWER LEADS BACK TO EVIDENCE" + FACT / INTERPRETATION / ACTION
```
CLAIM_TYPE:            D · LEI CENTRAL
CURRENT_STATUS:        **PROVED como prática**
CURRENT_EVIDENCE:      toda amostra em `data/samples/` declara origem, data de captura,
                       idioma original e localização; `tests/test_evidence.py` reprova
                       amostra sem proveniência — e já reprovou duas na prática.
                       Todo caso separa o que é fato do que é derivado, e todo caso carrega
                       o que **não** pode ser dito.
WHAT_IS_MISSING:       a separação FACT/INTERPRETATION/ACTION está implícita nos casos;
                       precisa virar campo explícito. Aplicado a partir do CASE-013.
```

### DECK-025 · "Not enough evidence? We don't know yet."
```
CLAIM_TYPE:            D
CURRENT_STATUS:        **PROVED**
CURRENT_EVIDENCE:      16 dos <!--M:SOURCE_ID_COUNT-->37<!--/M--> SOURCE_IDs estão em NÃO SEI com motivo medido; nenhuma
                       fonte foi reprovada sem avaliação; cinco hipóteses caíram e ficaram
                       registradas, duas delas nossas.
```

### DECK-026 · "3 independent sources" · DECK-027 · "CONFIDENCE = Medium"
```
CLAIM_TYPE:            D
CURRENT_STATUS:        **UNPROVED — as réguas não existiam**
NEXT_TEST:             `docs/regras/REGUA-DE-ALERTA-EAME.md` (criada nesta missão) define
                       independência e confiança. Enquanto não forem aplicadas a um caso
                       real, permanecem regra sem prova.
```

### DECK-028 · MARKETING OPPORTUNITY = MARKET × SCIENCE × COMPETITORS × ADAMA
```
CLAIM_TYPE:            C · RESULTADO DE NEGÓCIO
CURRENT_STATUS:        **UNPROVED como resultado; INPUT EXISTS parcial**
                       · SCIENCE ................... forte
                       · ADAMA (o que podemos dizer)  parcial-forte
                       · COMPETITOR communication ... fraco
                       · o que as pessoas falam ..... fraco
ESTÁGIOS:              INPUT EXISTS → PARTIAL CONNECTION → MARKETING SIGNAL →
                       MARKETING OPPORTUNITY CANDIDATE → PROVED USE CASE
                       **Hoje: PARTIAL CONNECTION.** Dois dos quatro lados estão fracos.
```

### DECK-029 · SUPPLY WATCH
```
CLAIM_TYPE:            A
CURRENT_STATUS:        **UNPROVED**
LEI:                   **AUTHORIZED SOURCE ≠ PROVEN SUPPLY DEPENDENCY.** O resultado
                       possível é SUPPLY SIGNAL, nunca SUPPLY DEPENDENCY.
FAILURE_MODE:          afirmar "a ADAMA depende da fábrica X" sem evidência específica
```

### DECK-030 · PILOT: "start focused, prove usefulness, then scale"
```
CLAIM_TYPE:            D
CURRENT_STATUS:        **PROVED como método** — o piloto já está restrito a FR/ES/IT e as
                       business questions serão escolhidas pela matriz de prova, não por
                       preferência.
```
