# RECONCILIAÇÃO — DECK RECONSTRUÍDO × DECK REAL

Na MISSÃO 03 o PDF não estava disponível e os claims foram **reconstruídos** a partir de
citações do briefing. O deck real chegou em 2026-08-28
(`deck/AURA-ADAMA-EAME-texto.txt`, 14 slides, *"AURA intelligence portal for ADAMA EAME"*).

Este documento compara os dois **sem maquiar a reconstrução anterior**.

---

## PLACAR DA RECONCILIAÇÃO

| Resultado | Claims |
|---|---|
| **CONFIRMADO** | 22 |
| **ALTERADO** (existe, mas o deck diz algo diferente do que assumi) | 5 |
| **REMOVIDO** (eu inflei um claim que o deck não faz) | 1 |
| **NOVO** (o deck promete e eu não tinha registrado) | **6** |
| **Total de claims após reconciliação** | **35** |

**A reconstrução acertou o essencial e errou em duas direções opostas:** exagerou o peso de
`WEATHER` e de `CONFIDENCE/INDEPENDENT SOURCES`, e **perdeu um slide inteiro** (SLIDE 7,
a arquitetura do portal) mais as métricas de sucesso do piloto (SLIDE 13).

---

## 1 · A CORREÇÃO MAIS IMPORTANTE — o deck já se protege

Três slides carregam rótulo explícito que eu **não tinha**:

| Slide | Rótulo literal no deck |
|---|---|
| 3 · WHAT IT CATCHES | **"ILLUSTRATIVE SCENARIOS"** |
| 4 · LOCAL TO SHARED | **"ILLUSTRATIVE CROSS-MARKET FLOW"** |
| 6 · ONE SIGNAL, END TO END | **"ILLUSTRATIVE"** |
| 11 · INSIDE THE PORTAL | **"ILLUSTRATIVE OUTPUT"** |
| 12 · TRUST | **"ILLUSTRATIVE OUTPUT"** |

**Consequência direta e favorável:** `"Field attention is rising"`, `"Competitor activity is
increasing"`, `"3 independent sources"` e `"Confidence: Medium"` **não são promessas de
capacidade** — são exemplos de tela rotulados como ilustrativos pelo próprio deck.

Na MISSÃO 03 eu os tratei como capacidade prometida e escrevi que o SINTONIA *"não pode
emitir ALERT"* como se isso fosse uma dívida com o cliente. **Era uma dívida menor do que eu
disse.** A capacidade subjacente continua tendo de ser defensável **se for mostrada** — mas
o deck não vendeu que ela já existe.

Isso **não** relaxa o rigor: rebaixa o alarme.

## 2 · CLAIMS ALTERADOS

| ID | O que eu assumi | O que o deck diz | Efeito |
|---|---|---|---|
| **DECK-003 WEATHER** | camada de inteligência de primeira linha | aparece **só no SLIDE 2**, numa lista de oito palavras. **Não** está no motor, nem nas três *strategic lanes*, nem no portal | **rebaixado** — Weather é claim menor. Meu tratamento inflou o peso |
| **DECK-026/027** | promessa de régua de independência e confiança | **ILLUSTRATIVE OUTPUT** (SLIDE 11) | de `UNPROVED` bloqueante para **ilustrativo**; as réguas seguem necessárias se a tela existir |
| **DECK-008/021 DISTRIBUTION** | camada vaga | SLIDE 5 é específico: **"Distributors, cooperatives, crop data"** | **melhor alinhado** — é exatamente o que FR-T13-001 entrega |
| **DECK-005 COMPETITOR** | comunicação genérica | SLIDE 9 fecha o escopo: **"Publicly observable communication signals only"** | o deck **já** limitou o escopo; minha leitura era mais ampla que a promessa |
| **DECK-023 DELIVER** | seis saídas soltas | SLIDE 5 lista as seis **e** o SLIDE 7 as organiza em camada de evidência + visões | ganha estrutura |

## 3 · CLAIM REMOVIDO

| ID | Motivo |
|---|---|
| **DECK-022** "régua de *increasing*" | eu criei um claim autônomo. O deck **não promete uma régua**; ele mostra `"Competitor activity is increasing"` dentro de um **ILLUSTRATIVE OUTPUT**. A necessidade técnica continua real, mas **não é uma promessa do deck** — vira requisito interno, não dívida com o cliente |

## 4 · CLAIMS NOVOS — o que eu tinha perdido

### DECK-031 · SLIDE 7 · A ARQUITETURA DO PORTAL *(eu havia perdido o slide inteiro)*
```
TEXTO_REAL:    "One evidence layer. Multiple business views."
               Visões: Cross-market intelligence · Market Development ·
                       Regulatory & Portfolio · Molecule & competitive ·
                       Marketing opportunity
               Add-ons: Early warning · Ask Sintonia · Supply Watch ·
                        Science × Field · Distribution
TIPO:          CAPABILITY
```
**Isto é a arquitetura de informação que o deck já vendeu.** Minha
`ARQUITETURA-DE-INFORMACAO-EAME.md` foi escrita **sem** conhecê-la e precisa ser
reconciliada com ela (feito abaixo, §6).

### DECK-032 · SLIDE 13 · COMO O PILOTO SERÁ JULGADO
```
TEXTO_REAL:    "MEASURE: Relevance · Evidence quality · Time-to-insight · Usefulness"
TIPO:          METHODOLOGY
```
**O deck define os critérios de sucesso do piloto e eu não os tinha.** São quatro, e três
deles nós conseguimos sustentar hoje: *evidence quality* (proveniência testada),
*time-to-insight* (consulta determinística já roda) e *relevance* (radar ADAMA).
*Usefulness* só a ADAMA responde.

### DECK-033 · SLIDE 8 · AS TRÊS PROMESSAS DE VALOR DO MARKET DEVELOPMENT
```
TEXTO_REAL:    "→ Earlier visibility  → Evidence attached  → Prioritized questions"
               e "Market Development decides. Sintonia prioritizes where to look."
TIPO:          BUSINESS OUTCOME
```
Importante: o deck **não** promete que o SINTONIA decide. Promete que ele **prioriza onde
olhar**. É uma promessa mais modesta e mais defensável do que eu havia assumido.

### DECK-034 · SLIDE 1 · A HIERARQUIA DAS CAMADAS
```
TEXTO_REAL:    SLIDE 1 lista cinco: REGULATION · COMPETITOR · MOLECULE · FIELD · SCIENCE
               SLIDE 2 lista oito, acrescentando Distribution · Weather · Market
TIPO:          CAPABILITY
```
Há **cinco camadas centrais e três de apoio**. Eu tratei as oito como iguais. As três de
apoio (incluindo Weather) pesam menos na promessa.

### DECK-035 · SLIDE 5 · OS QUATRO GRUPOS DE FONTE
```
TEXTO_REAL:    "Field & technical: Public technical conversations"
               "Science & regulation: Publications, regulatory sources"
               "Competition: Competitor communication, public ads"
               "Market & distribution: Distributors, cooperatives, crop data"
TIPO:          CAPABILITY
```
O deck **já agrupa** as fontes em quatro packs, não nove. Meus SOURCE PACKS usam nove
camadas — mais granular, compatível, mas a comunicação com a ADAMA deve usar os quatro.

### DECK-036 · SLIDE 2 · A TESE COMERCIAL
```
TEXTO_REAL:    "Important market signals often stay local."
               "The information exists. The value is lost when the signals stay separate."
TIPO:          BUSINESS OUTCOME
```
A tese não é *"descobrimos informação que ninguém tem"* — é *"a informação existe e está
separada"*. **Isto é exatamente o que a MISSÃO 02 e 03 provaram**: todas as 14 fontes GREEN
são públicas e gratuitas. A tese do deck é a mais defensável possível, e nós temos a prova.

## 5 · O QUE A RECONSTRUÇÃO ACERTOU

Os 22 claims confirmados incluem todo o núcleo: as oito camadas (SLIDE 2), os quatro
cenários (SLIDE 3), o *same issue / molecule / competitor / movement* (SLIDE 4), o motor de
quatro passos (SLIDE 5), as seis saídas, as três *strategic lanes* e a ressalva
`"Authorized source ≠ proven supply dependency"` (SLIDE 9), a fórmula de *marketing
opportunity* (SLIDE 10), o TRUST com `Fact / Interpretation / Action` e o
`"we don't know yet"` (SLIDE 12), e o piloto de 2–3 mercados (SLIDE 13).

**A reconstrução era utilizável.** O erro não foi de conteúdo central, foi de **peso** —
e de dois slides perdidos.

## 6 · RECONCILIAÇÃO DA ARQUITETURA DE INFORMAÇÃO

O SLIDE 7 do deck já define a estrutura. Comparando com o que escrevi sem conhecê-la:

| Deck (SLIDE 7) | Minha arquitetura | Situação |
|---|---|---|
| **One evidence layer** | área EVIDENCE & SOURCES `PROVED` | ✅ coincide |
| Regulatory & Portfolio | área REGULATORY `PROVED` | ✅ coincide |
| Molecule & competitive | áreas MOLECULE `PARTIAL` + COMPETITIVE `PARTIAL` | ✅ coincide |
| Market Development | contrato de saída MARKET DEVELOPMENT `PARTIAL` | ✅ coincide |
| Cross-market intelligence | **eu não tinha como área** — tratei como cruzamento | ⚠️ **criar como área** |
| Marketing opportunity | DECK-028, `PARTIAL CONNECTION` | ✅ coincide |
| Early warning *(add-on)* | ALERT `CONCEPT` | ✅ coincide |
| Ask Sintonia *(add-on)* | `BUILDABLE`, provado por execução | ✅ coincide |
| Supply Watch *(add-on)* | `UNPROVED` | ✅ coincide |
| Science × Field *(add-on)* | **eu tinha SCIENCE e FIELD separados** | ⚠️ o deck promete o **cruzamento** dos dois |
| Distribution *(add-on)* | área DISTRIBUTION `PARTIAL` | ✅ coincide |

**Duas correções na minha arquitetura:** *Cross-market intelligence* precisa existir como
área própria, e *Science × Field* é um **cruzamento prometido** que eu não havia registrado
como tal — e que hoje é `UNPROVED`, porque o elo entre problema de campo e literatura
depende de X-007 (23,5% do uso).
