# PACOTE DE MATÉRIA-PRIMA — PILOTO SINTONIA EAME

Porta de entrada do futuro Claude Design. **Descreve conteúdo, não interface.**
`PROTOTYPE_FROZEN = SIM`.

**Data:** 2026-08-29 · Deck em `../apresentacao/deck/` · Todos os números têm arquivo de
evidência em `../../data/samples/`

---

# PILOT SCOPE
**Mercados:** França · Espanha · Itália (+ camada UE).
**Culturas:** cereais (trigo, cevada, triticale, centeio) · olivar · videira.
**Não entram:** Polônia e Romênia — o próprio deck as mostra como fluxo ilustrativo (SLIDE 4).

---

# BUSINESS QUESTION 1 · REGULATORY & PORTFOLIO
> *"What changed, what does it touch, and where?"*

**Status: PILOT READY.** Único eixo provado ponta a ponta.

**Cadeia comprovada:** ato da UE (CELEX + data + texto em 4 línguas) → substância normalizada
(**82,1%** do uso) → registro nacional → titular → produtos ADAMA → concorrentes.

**Números disponíveis (FR, registro de 25/08/2026):**
- **77** produtos autorizados com protioconazol · **Bayer 32** · **ADAMA 3**
- ADAMA: AVASTEL (AMM 2240236) · FORAPRO (2240001) · MAXENTIS (2230815)

**Números disponíveis (IT, registro de 24/08/2026):**
- **85** autorizações em vigor com protioconazol · **Bayer 18** · **ADAMA 5**
- ADAMA: MAGANIC (017955) · MAXENTIS (018067) · AVASTEL (018089) · SORATEL (018175) · KOJAMI (019095)
- **60 das 85 (71%)** vencem em **31/03/2027**

**Fato regulatório europeu:** CELEX **32025R0787** (24/04/2025) fixa a expiração da aprovação
do protioconazol em **31/03/2027**; a molécula foi prorrogada **6 vezes em 6 anos** e o
Parlamento Europeu objetou **3 vezes**.

**Espanha — a perna fechou em fonte PRIMÁRIA na MISSÃO 07.** Lendo o registro oficial pelas
rotas públicas da própria aplicação (`ES-T4-005`):

- **30** autorizações em vigor com protioconazol na Espanha · **Bayer 8** · **ADAMA 3**
- ADAMA: **AVASTEL** (ES-01818, fluxapiroxade + protioconazol, cad. 31/10/2027) ·
  **SORATEL** (ES-01665, protioconazol 25%, cad. 31/03/2027) ·
  **SORATEL MAX** (ES-01717, azoxistrobina 20% + protioconazol 15%, cad. 31/05/2027)
- **ES-01717 completo e primário:** produto de referência **SORATEL MAX** (antes
  **MAXENTIS**), titular **ADAMA Agriculture España S.A.**, fabricante **ADAMA
  Agricultural Solutions Ltd.**, planta **(Neot Hovav)**, status **Vigente**, usos
  **cebada · centeno · trigo · triticale**, denominações **AMISTAR ERA 350 SC** (Syngenta)
  e **CUMILZAN** (Massó)
- o **único** outro registro espanhol vigente com azoxistrobina + protioconazol é
  **ES-01770 · PROMINO XTRA**, titular **CAC Chemical GmbH**

A MISSÃO 06 tinha titular e fabricante em **fonte secundária**, e a fonte secundária
**errou o fabricante** (dizia `ADAMA MAKHTESHIM LTD.`). Nenhum campo do ES-01717 depende
mais de fonte secundária.

**O que continua não sendo verdade:** o registro espanhol **não** é publicado como open
data. O que existe é a rota de exportação da própria aplicação oficial — primária e
completa (3.084 registros), mas sem garantia de estabilidade.

# BUSINESS QUESTION 2 · MARKET DEVELOPMENT / FIELD SIGNAL
> *"Is this signal real, where is it happening, what supports it, and does ADAMA have a response?"*

**Status: PILOT READY, escopo declarado — Espanha / olivar / repilo.**

**O fluxo do SLIDE 8, executado — e o que NÃO fecha:**

| # | pergunta | resultado |
|---|---|---|
| 1 | Signal appears | ✅ repilo em alta em duas províncias |
| 2 | **Is it real?** | ✅ **23 safras (2003–2026), 148.964 leituras**, sobrevive ao controle de coorte |
| 3 | **Where else?** | ✅ sobe em Cádiz e Huelva; **não** sobe em Jaén, Sevilla, Córdoba, Granada e Málaga |
| 4 | **What supports it?** | ❓ **NÃO FECHA.** A fonte publica "condiciones favorables", mas **não há leitura desse campo em Cádiz nem em Huelva** — exatamente as duas províncias em alta. E X-009 proíbe a explicação climática fácil |
| 5 | Does ADAMA have a response? | ✅ **REGISTERED RESPONSE EXISTS** — **ES-00211 · NEPTUNE**, titular ADAMA Agriculture España S.A., tebuconazol 3,6% + oxicloruro de cobre 36% [SC], uso **Olivo × Repilo del olivo (*Venturia oleaginea*)**, ficha oficial do ROPF. **Com qualificador:** status `Vigente` e caducidade **15/08/2026** — duas semanas antes da captura. Último trâmite: `PRÓRROGA DE AUTORIZACIÓN`, Terminada, 30/08/2023. Fábrica **Humanes (Espanha)** |
| 6 | What should we validate? | ✅ programa de fungicida nas parcelas; a base pequena de Huelva (7 parcelas) |

**É 5 ✅ · 1 ❓ — e a que não fecha continua sendo a nº 4.** A nº 5 fechou na MISSÃO 09,
quando o NEPTUNE apareceu no export primário que já estava no repositório e não havia sido
usado. **Mas "fechou" aqui tem três camadas que não podem virar um ✅ só:**

| camada | estado |
|---|---|
| `REGISTERED RESPONSE EXISTS` | **SIM, primário** — ES-00211, uso exatamente para repilo em olivo |
| `CURRENT COMMERCIAL AVAILABILITY` | **NÃO SEI** — o registro não diz o que está no canal |
| `REGULATORY STATUS INTERPRETATION` | **INVESTIGATE** — `Vigente` com caducidade vencida há duas semanas |

**E o vencido não é caso isolado:** **34** registros espanhóis estão `Vigente` com
caducidade passada, e **31 deles compartilham a mesma data, 15/08/2026**, com titulares
diferentes. Dentro da mesma substância a maioria dos produtos já carrega data de 2028 e
estes ficaram em 2026. Parece lote administrativo pendente — e fica em `INVESTIGATE`,
porque afirmar derivação de data europeia é exatamente o que o CASE-014 proíbe.
**`EXPIRED` nunca é lido como `WITHDRAWN`.**

**Enriquecimento encontrado nesta missão:** o Neptune ataca repilo **e** tuberculose, e a
RAIF mede as duas (`1702 Repilo…` e `2005 Tuberculosis: Síntomas (0-3)`). O alinhamento
produto↔fonte é maior do que se supunha.

# BUSINESS QUESTION 3 · CROSS-MARKET
> *"Does the same molecule appear elsewhere?"*

**Status: PILOT READY — por MOLÉCULA, não por ISSUE.** Medido: X-006 cobre **82,1%** do uso;
X-007 cobre **23,5%**. A primeira demonstração cross-market **deve** usar molécula.

---

# HERO CASE 1 · CASE-014 — protioconazol em dois mercados
8 produtos ADAMA (3 FR + 5 IT), a expiração europeia de 31/03/2027, e **60 de 85** produtos
italianos com a mesma data. **Red team aplicado:** a derivação legal entre a data italiana e
a europeia **não é afirmável** — 199 produtos italianos vencem em 31/03/2027, incluindo
nicosulfuron (58), que **não tem ato europeu recente**. Diz-se *"as datas coincidem,
sistematicamente"*, nunca *"A causa B"*.

# HERO CASE 2 · CASE-013 — repilo, 23 safras e controle de coorte
Huelva **1,17% (2023) → 8,83% (2026)** nas **mesmas parcelas** — e 8,83 é o **máximo das 23
safras**. Jaén, na mesma coorte, fica entre 0,56% e 0,90%; é **comparação observacional**,
não controle experimental.

**Ressalva obrigatória (MISSÃO 09/10):** **Cádiz 2026 = 8,01 NÃO é máximo histórico** —
foi 9,71 em 2013. E ao entrar a **área de olivar**, a prioridade comercial muda: Huelva e
Cádiz são as **duas menores** províncias de olivar da Andaluzia (4,3% da área somadas), e a
única província no top-3 das duas réguas é **Sevilla**. Ver `CASE-016`.

# HERO CASE 3 · CASE-008 — o clima não explica a doença
Córdoba choveu mais que Huelva e teve 4× menos míldio; Cádiz teve a maior umidade e
praticamente nenhum. **Prova que o sistema recusa a explicação óbvia** quando os dados não
a sustentam. É o case de TRUST.

**Rebaixados nesta missão:** CASE-015 (HERO → TECHNICAL PROOF, ver abaixo) ·
CASE-011 (absorvido pelo 014) · CASE-003, CASE-012 (SUPPORT).

---

# SOURCE PACKS
Ver `SOURCE-PACK-PILOTO.md` — **12 fontes**, não 34.

# ADAMA CONTEXT
**CEREAL — o denominador comum público nos três países.**
FR: Forapro, Maxentis, Avastel (registrados) + Go Céréales + Maïstria (2027) · €135 M em 2025.
ES: Avastel + Timeline Trio + evento ADAMAexperience (Guadalajara, 150+ participantes).
IT: Avastel, Maxentis, Maganic, Soratel, Kojami (registrados).
Tecnologias de formulação citadas: **Asorbital** (ES, IT) e **Isondalis** (FR).
**OLIVE — só Espanha.** Neptune (repilo e tuberculose) + participação no Plan STAR Olivar.
**VINE — Espanha tem campanha** (Vinergy, OPAR, KONA, ORISOS); **França tem registro forte
sem campanha 2025–2026** (17 usos em Vigne×Mildiou, a empresa nomeada com mais usos).
`INTERNAL PRIORITY = NÃO SEI` — exige dado interno.

# CROSS-MARKET MATERIAL
| | França | Espanha | Itália |
|---|---|---|---|
| fato regulatório da UE aplicável | ✅ | ✅ | ✅ |
| sinal público ADAMA em cereal | ✅ | ✅ | ✅ |
| **registro nacional verificável** | ✅ 3 produtos | ✅ ES-01717 (titular por fonte secundária) | ✅ 5 produtos |
| datas de vencimento | ❌ campo inexistente | ❌ | ✅ |
| cultura × alvo no registro | ✅ | ❌ | ❌ |

**A cadeia fecha nos três mercados — 3/3, com uma ressalva de qualidade de fonte.**
FR: MAXENTIS AMM 2230815 · ES: MAXENTIS/SORATEL MAX ES-01717 · IT: MAXENTIS reg. 018067.
**São três autorizações nacionais distintas, não um produto único** — mesma molécula não é
mesmo produto. Na Espanha, titular e fabricante vêm de fonte **secundária**; o dump geral do
registro espanhol continua indisponível (grade em JavaScript).

# ASK SINTONIA MATERIAL
35 perguntas · **20 respondidas · 14 recusadas corretamente · 1 parcial · 0 erradas**.
Contrato e detalhe em `ASK-SINTONIA-BENCHMARK.md`.

# TRUST / EVIDENCE
Toda amostra declara origem, data de captura, idioma original, SOURCE_LOCATION e
FACT_LOCATION. **<!--M:TEST_COUNT_CURRENT-->649<!--/M--> provas automatizadas** reprovam amostra sem proveniência — e já
reprovaram três vezes nesta linha de missões, incluindo contagens que eu havia declarado
errado. Regra: `FACT` / `INTERPRETATION` / `ACTION` nunca no mesmo campo.

# PILOT READY · COMING SOON · EXPLORATION
Ver `../apresentacao/PILOTO-CLASSIFICACAO.md`, atualizado por esta missão:
**Competitor communication permanece COMING SOON** (rota provada) ·
**Manufacturer/origem permanece EXPLORATION** · **Distribution: COMING SOON (rede, não fluxo)**.

# WHAT WE MUST NOT CLAIM
Ver `O-QUE-PODEMOS-DIZER.md`.
