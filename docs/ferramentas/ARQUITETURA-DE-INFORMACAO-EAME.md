# ARQUITETURA DE INFORMAÇÃO — SINTONIA EAME

> **PORTA ÚNICA DE ARQUITETURA DE PRODUTO:** `docs/piloto/ARQUITETURA-DE-PRODUTO-ATUAL.md`.
>
> As nove áreas abaixo descrevem a **informação disponível**, e nisso continuam corretas. **Para desenho de produto elas NÃO são nove telas nem nove módulos.**


Este documento existe para que a missão de design **não precise descobrir o produto**.
Ele diz o que existe, o que pode ser afirmado, com que dado, para quem e com que limite.

**É arquitetura conceitual em texto. Não contém tela, componente, layout nem estilo.**
`PROTOTYPE_FROZEN = SIM` (D-007).

**Data:** 2026-08-28 · Claims em `../apresentacao/CONTRATO-DE-PROVA-DA-APRESENTACAO.md`

---

## O FLUXO QUE ESTE DOCUMENTO ENCERRA

```
SOURCE → EVIDENCE → NORMALIZATION → CAPABILITY → CROSSING → QUESTION → ADAMA USE
       → TOOL CONCEPT → INFORMATION REQUIREMENTS
                                                  ▲ este documento para aqui
```

Não continua para UI, componente, página ou portal.

## ESTADOS

`PROVED` · `BUILDABLE` · `PARTIAL` · `CONCEPT` · `BLOCKED`
(o estado `PROTOTYPE` foi abolido — não construiremos protótipo nesta fase)

---

# PARTE 1 · ÁREAS DE INFORMAÇÃO

## ÁREA · REGULATORY — `PROVED`
```
PURPOSE:              saber o que mudou na regulação europeia e nacional, o que isso toca
                      e quando realmente importa
QUESTIONS:            · o que mudou na UE nesta semana?
                      · que substâncias foram afetadas?
                      · que produtos nacionais dependem delas?
                      · quais produtos ADAMA estão envolvidos?
                      · quais concorrentes estão envolvidos?
                      · qual data realmente importa?
                      · qual interpretação seria errada?
CAPABILITIES_REQUIRED:CAP-001, CAP-002, CAP-003, CAP-006, CAP-007, CAP-020
TOOLS_REQUIRED:       REGULATORY WATCH · REGISTRATION EXPIRY RADAR
DATA_REQUIRED:        ato CELEX + substância + registro nacional + titular + cultura×alvo
SOURCES:              EU-T4-001, FR-T4-001, IT-T4-001, ES-T4-001, ES-T4-002, EU-T12-001
COUNTRIES_SUPPORTED:  EU ✅ · FR ✅ · IT ✅ · ES ⚠️ (sem dump aberto de produtos)
CROPS_SUPPORTED:      todas as do registro francês; Itália sem cultura×alvo
LIMITATIONS:          expiração ≠ retirada · vencimento ≠ perda ·
                      registro ≠ prioridade comercial · Itália não publica cultura×alvo
REAL_EXAMPLES:        CASE-001, CASE-002, CASE-003, CASE-011
ADAMA_USERS:          REGULATORY (primário) · PORTFOLIO · MD · EAME
STATUS:               **PROVED** — a área mais madura do sistema
```

## ÁREA · MOLECULE — `PARTIAL`
```
PURPOSE:              seguir uma substância ativa através de mercados, produtos e empresas
QUESTIONS:            · quem depende desta molécula, e onde?
                      · qual é o horizonte regulatório dela?
                      · há registro novo, fabricante novo ou origem nova?
CAPABILITIES_REQUIRED:CAP-006 + normalização X-006
TOOLS_REQUIRED:       MOLECULE WATCH
DATA_REQUIRED:        substância normalizada · CAS · titular · produto · ato da UE
SOURCES:              EU-T4-001, FR-T4-001, IT-T4-001
COUNTRIES_SUPPORTED:  EU ✅ · FR ✅ · IT ✅ · ES ⚠️
LIMITATIONS:          **manufacturer, fonte autorizada e país de origem NÃO EXISTEM na base**
                      — `titulaire` é titular de registro, não fabricante.
                      Cobertura da normalização: 82% do uso, não 100%.
                      Cobre e enxofre não normalizados.
REAL_EXAMPLES:        CASE-011 (protioconazol)
ADAMA_USERS:          REGULATORY · PORTFOLIO · R&D · MD
STATUS:               **PARTIAL** — forte em substância, vazio em origem
```

## ÁREA · PEST & DISEASE — `PARTIAL`
```
PURPOSE:              saber onde a pressão está e o que ela exige agora
QUESTIONS:            · onde a doença está e com que intensidade?
                      · há infecção latente ainda sem sintoma?
                      · a autoridade regional declarou condições favoráveis?
CAPABILITIES_REQUIRED:CAP-014, CAP-015, CAP-016, CAP-021
TOOLS_REQUIRED:       PEST & DISEASE RADAR
SOURCES:              ES-T3-001 (numérico) · FR-T3-001, IT-T3-001 (texto em PDF)
COUNTRIES_SUPPORTED:  ES ✅ **apenas Andaluzia** · FR ⚠️ · IT ⚠️ (1 de 20 regiões vista)
CROPS_SUPPORTED:      ES: 10 culturas do RAIF
LIMITATIONS:          a doença é **provincial, não regional** — a média não descreve
                      nenhuma província · parcelas do RAIF não são amostra aleatória ·
                      **o n precisa viajar junto com a média** ·
                      **o clima não explica a diferença** (X-009)
REAL_EXAMPLES:        CASE-007, CASE-008, CASE-012
ADAMA_USERS:          TECHNICAL (primário) · COMMERCIAL · MD · MKT
STATUS:               **PARTIAL** — `PROVED` na Andaluzia, `CONCEPT` fora dela
```

## ÁREA · SCIENCE & EXPERTS — `PROVED com ressalva`
```
QUESTIONS:            · quem trabalha repetidamente neste problema, neste país?
                      · em que instituição, desde quando?
CAPABILITIES_REQUIRED:CAP-017, CAP-018
SOURCES:              EU-T5-001 + vocabulário de ES-T4-001
COUNTRIES_SUPPORTED:  FR ✅ ES ✅ IT ✅
LIMITATIONS:          **recorrência não é autoridade** · afiliação não é local do
                      experimento · sem vocabulário controlado a lista muda por completo
                      (medido: 2.627 × 27 trabalhos) · **GDPR: pessoas identificadas**
REAL_EXAMPLES:        CASE-009, CASE-010
ADAMA_USERS:          R&D · TECHNICAL · MD
STATUS:               **PROVED**
```

## ÁREA · CROPS & CLIMATE — `PROVED como contexto`
```
QUESTIONS:            · onde está a cultura e com que peso por região?
                      · que exposição climática houve na janela sensível?
SOURCES:              EU-T1-001, EU-T1-002, EU-T2-001, EU-T2-002
LIMITATIONS:          **rendimento não existe por região** (medido) · clima é **um ponto**,
                      não média regional · **a janela escolhida inverte o sinal** (CASE-006)
                      · **nunca afirmar causalidade** (X-009, CASE-008)
REAL_EXAMPLES:        CASE-005, CASE-006
ADAMA_USERS:          MD · COUNTRY · TECHNICAL · EAME
STATUS:               **PROVED** para exposição · **CONCEPT** para impacto
```

## ÁREA · COMPETITIVE — `PARTIAL`
```
QUESTIONS:            · quem tem direito de uso no mesmo combate, com que molécula?
                      · quem está mais exposto ao mesmo horizonte regulatório?
                      · [não respondível] o concorrente está comunicando mais?
SOURCES:              FR-T4-001, IT-T4-001 (registro) · comunicação: **nenhuma**
LIMITATIONS:          contagem de registros **não é participação de mercado** ·
                      agrupamento de razão social em grupo **ainda não medido** (DECK-015) ·
                      camada de comunicação **inacessível** (403/502/404)
REAL_EXAMPLES:        X-005 · CASE-011 · trigo×septoriose FR: BASF 22, Bayer 20, ADAMA 6
ADAMA_USERS:          MD · PORTFOLIO · MARKETING · EAME
STATUS:               **PARTIAL** — `PROVED` no registro, `BLOCKED` na comunicação
```

## ÁREA · MARKET — `PARTIAL`
```
LIMITATIONS:          **MARKET não é um dataset.** Variável a variável:
                      área NUTS 2 ✅ · rendimento nacional ✅ · rendimento regional ❌ ·
                      preço por praça ✅ · comércio exterior ⚠️ · eventos ❌
SOURCES:              EU-T1-001, EU-T1-002, EU-T10-001
STATUS:               **PARTIAL**
```

## ÁREA · DISTRIBUTION — `PARTIAL (novo)`
```
QUESTIONS:            · quem distribui, e onde?
                      · [não respondível] que volume, que catálogo, que acordos?
SOURCES:              FR-T13-001 (base SIRENE aberta)
COUNTRIES_SUPPORTED:  FR ✅ · ES ❌ · IT ❌
LIMITATIONS:          dá **a rede**, não o **fluxo**
REAL_EXAMPLES:        4.646 atacadistas de grãos na França; OCEALIA, SOUFFLET, VIVESCIA,
                      AXEREAL, NATUP, ARTERRIS, OXYANE, CAVAC
STATUS:               **PARTIAL**
```

## ÁREA · FIELD VOICES — `CONCEPT`
```
STATUS:               **CONCEPT** — sem fonte. YouTube Data API 403, Meta Graph 400,
                      TikTok 404. O RSS público do YouTube funciona **se** o channel_id
                      for conhecido: o gargalo é **descoberta**, não coleta.
                      Só REACH seria mensurável. FIELD, TECHNICAL e COMMERCIAL AUTHORITY
                      não têm fonte identificada.
```

## ÁREA · EVIDENCE & SOURCES — `PROVED`
```
PURPOSE:              toda resposta leva de volta à evidência (DECK-024)
STATUS:               **PROVED** — <!--M:SOURCE_ID_COUNT-->37<!--/M--> SOURCE_IDs fichados, 16 amostras com proveniência
                      obrigatória testada, <!--M:TEST_COUNT_CURRENT-->355<!--/M--> provas automatizadas
```

## ÁREAS AVALIADAS E **NÃO** RECOMENDADAS AGORA
| Área | Motivo |
|---|---|
| EVENTS | informação real, formato ruim; valor relativo baixo |
| POLICY (separada) | já coberta pela área REGULATORY, mesmo conector |
| EAME OVERVIEW | **só duas dimensões são comparáveis** entre os três países: área de cultura e preço de cereal. Uma área "overview" hoje fabricaria uniformidade — ver X-008 |

---

# PARTE 2 · CONTRATOS DE SAÍDA (DELIVER)

## REGULATORY REVIEW — `PROVED`
```
trigger:              ato publicado no Jornal Oficial da UE ou nova versão do registro nacional
evidence required:    CELEX + data + substância + (produto nacional, quando a chave casar)
comparison baseline:  não exige — é evento, não tendência
confidence rule:      HIGH (fonte oficial primária, medição direta, sem contradição)
questions answered:   o que mudou · sobre que substância · que produtos toca · de quem são
what it cannot say:   que o produto será retirado · em que data o produto sai do mercado ·
                      qual o impacto comercial
```

## MOLECULE WATCH — `PARTIAL`
```
trigger:              ato sobre a substância, ou mudança no conjunto de produtos que a contêm
evidence required:    substância normalizada + ato + produtos + titulares
coverage rule:        **declarar sempre**: a normalização cobre 82% do uso, não 100%
confidence rule:      HIGH quando casou por CAS ou nome exato; **LOW** quando casou por
                      sal ou fuzzy — e o método precisa aparecer
questions answered:   quem depende desta molécula · qual o horizonte dela
what it cannot say:   quem a fabrica · de onde vem · se há dependência de fornecimento
```

## MARKET DEVELOPMENT — `PARTIAL`
A régua de seis perguntas do deck, aplicada a um sinal:
```
1 SIGNAL APPEARS        de que fonte, com que data?
2 IS IT REAL?           medição direta ou relato? quantos publicadores originais?
3 WHERE ELSE?           o mesmo identificador aparece em outro mercado?
4 WHAT SUPPORTS IT?     ciência, registro, clima — cada um separado
5 ADAMA RESPONSE?       há produto registrado para esse par cultura×alvo?
6 WHAT TO VALIDATE?     o que só campo ou dado interno resolvem
```
Qualquer passo sem resposta → **NÃO SEI**, e isso é permitido.

## ALERT — `CONCEPT`
```
STATUS:               **CONCEPT — a régua existe, a porta BASELINE não abre**
                      Ver ../regras/REGUA-DE-ALERTA-EAME.md.
                      Hoje o sistema pode emitir **WATCH** (protioconazol, 31/03/2027) e
                      **INVESTIGATE** (repilo incubado acima do visível em Málaga e
                      Córdoba). **Não pode emitir ALERT** em nenhuma família de conversa
                      pública. Chamar isso de alerta seria vender feed como inteligência.
```

## MARKET BRIEF — `PARTIAL`
```
inputs:               país + período + cultura
evidence:             registro, ciência, clima, preço, e doença **só na Andaluzia**
output contract:      cada bloco com FACT / INTERPRETATION / ACTION separados, fonte,
                      data e ponteiro de evidência; ausência declarada como ausência
what it cannot say:   tendência de conversa pública; participação de mercado
```

## ASK SINTONIA — `BUILDABLE`
```
STATUS:               **BUILDABLE — provado que a camada é consultável**
evidence:             scripts/ask_sintonia.py responde 4 perguntas reais com
                      FACT / DERIVED / UNKNOWN e confiança, e **recusa** a quinta
contract:             toda resposta devolve ANSWER · EVIDENCE · SOURCE · WHAT_IS_FACT ·
                      WHAT_IS_DERIVED · WHAT_IS_UNKNOWN · CONFIDENCE
what it cannot say:   qualquer coisa fora da evidência preservada. A resposta correta
                      para o que falta é **"NÃO SEI"**, com o motivo.
```
