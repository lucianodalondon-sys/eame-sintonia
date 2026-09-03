# CLASSIFICAÇÃO DO PILOTO — O QUE VAI, O QUE ESPERA, O QUE NÃO SABEMOS

O deck já vende a filosofia: **"Start focused. Prove usefulness. Then scale."** (SLIDE 13).
Este documento separa o subconjunto certo para o piloto.

**Data:** 2026-08-29 · Deck real em `deck/` · Reconciliação em `RECONCILIACAO-DECK-REAL.md`

**Regra:** `COMING SOON` **não é depósito de incerteza**. Só entra o que tem fonte ou caminho
técnico identificado **e** nenhum bloqueio conhecido. O incerto vai para `EXPLORATION`.

---

## 1 · PILOT READY — demonstrável com matéria-prima real

| Capacidade | Prova | Mercados |
|---|---|---|
| **Evento regulatório da UE → substância → produto nacional → ADAMA → concorrentes** | CASE-011, CASE-014 | EU · FR · IT |
| **Mesma molécula atravessando mercados** (X-006, 82,1% do uso) | CASE-014 | FR · IT |
| **Calendário de vencimento por empresa** | CASE-003 | IT |
| **Cronologia competitiva por registro** | CASE-015 | IT · FR |
| **Pressão de doença medida, com série de 23 safras e controle de coorte** | CASE-013 | ES (Andaluzia) |
| **Infecção latente × sintoma visível** | CASE-012 | ES (Andaluzia) |
| **Necessidades sem solução autorizada** (art. 53) | CASE-004 | ES |
| **Rede de especialistas por problema e país** | CASE-009, CASE-010 | FR · ES · IT |
| **Contexto climático por região e janela** — e a recusa da causalidade | CASE-005, CASE-006, CASE-008 | FR · ES · IT |
| **Área de cultura por NUTS 2, 25 anos** · **preço de cereal por praça** | CAP-010, CAP-019 | FR · ES · IT |
| **Ask Sintonia** — consulta à camada de evidência | benchmark 35 perguntas: 20 respondidas, 14 recusadas, 1 parcial, **0 erradas** | todos |
| **Toda resposta leva à evidência** + *"we don't know yet"* | **<!--M:TEST_COUNT_CURRENT-->748<!--/M--> provas automatizadas**; 16 fontes em NÃO SEI com motivo | todos |
| **Rede de distribuição** (distribuidores e cooperativas) | FR-T13-001, 4.646 empresas | FR |

## 2 · COMING SOON — caminho técnico identificado, sem bloqueio conhecido

| Capacidade | O que falta | Por que não é EXPLORATION |
|---|---|---|
| **Normalização de titular → grupo empresarial** (DECK-015) | construir e medir | baixo custo; **CASE-015 já mostra a necessidade e o teste** |
| **Comunicação de concorrente** (DECK-005, 011) | coleta repetível | **a rota existe**: PDFs técnicos corporativos com data no caminho (`syngenta.it/.../2025/12/17/...`), imprensa técnica com arquivo datado, e o registro oficial para cruzar. A MISSÃO 03 testou as *home pages* (403) — a rota errada |
| **Registro espanhol de produtos** (DECK-001 em ES) | acesso ou permissão | a fonte existe e é oficial; falta a via |
| **Detecção de "novo registro"** (DECK-012) | versionar semanalmente | `scripts/data_clock.py` já registra versão, data e SHA-256 |
| **Baseline de campo em FR e IT** | processar PDF de boletim | conteúdo existe: corpus BSV de 40.899 documentos e boletins IT de 2025–2026 |
| **Régua de confiança e de independência** | aplicar a casos reais | já escritas em `../regras/REGUA-DE-ALERTA-EAME.md` |

## 3 · EXPLORATION — ainda não sabemos se dá para construir de forma defensável

| Capacidade | Por quê |
|---|---|
| **Manufacturer · fonte autorizada · país de origem** (DECK-006, 012, 029) | **nenhuma fonte encontrada**; o registro traz titular, não fabricante. E `CASE-015` mostra que titular ≠ marca |
| **Vozes do campo / field attention** (DECK-007 parcial) | APIs exigem credencial; o gargalo é **descoberta** de canais, não coleta |
| **Fluxo de distribuição** — volume, catálogo, acordos (DECK-021) | temos a rede, não o fluxo |
| **Patente e marca** (DECK-005) | EUIPO 401 · EPO OPS 403 · Espacenet 403 · PatentsView bloqueado |
| **Marketing opportunity** completo (DECK-028) | dois dos quatro lados fracos → estágio **PARTIAL CONNECTION** |
| **Science × Field** (DECK-031, add-on do SLIDE 7) | o elo depende de X-007, que resolve **23,5%** do uso |

## 4 · NOT RECOMMENDED para o piloto
Qualquer saída que dependa de **"rising" / "increasing"** em conversa pública ou comunicação
de concorrente. O deck rotula esses exemplos como **ILLUSTRATIVE OUTPUT** — não são dívida —
mas mostrá-los como capacidade viva seria vender o que não temos.

**Exceção medida:** *"rising"* **é demonstrável** para pressão de doença na Andaluzia
(CASE-013), porque ali existem 11 safras e controle de coorte.

---

## 5 · FICHAS POR CAMADA DO DECK

| Camada | O que observamos | FR | ES | IT | EU | Histórico | Frequência | Normalização | PILOT STATUS |
|---|---|---|---|---|---|---|---|---|---|
| **REGULATION** | ato, substância, produto, titular, cultura×alvo, vencimento | STRONG | USABLE | STRONG | STRONG | CELEX completo | contínua/semanal | X-006 82% | **PILOT READY** |
| **MOLECULE** | substância, CAS, titular, horizonte | STRONG | WEAK | STRONG | STRONG | acervo | contínua | X-006 82% | **PILOT READY** (origem: EXPLORATION) |
| **SCIENCE** | autoria, afiliação, país, DOI, ano | STRONG | STRONG | STRONG | STRONG | décadas | contínua | vocabulário científico | **PILOT READY** |
| **FIELD** | incidência medida %, parcela, semana | WEAK | **STRONG** | WEAK | EMPTY | **23 safras (ES)** | semanal | X-007 23,5% | **PILOT READY só ES** |
| **COMPETITOR** | titular × cultura × alvo × molécula; datas de registro | USABLE | WEAK | USABLE | EMPTY | datas de registro | semanal | **falta G4** | **PILOT READY no registro** · COMING SOON na comunicação |
| **MARKET** | área NUTS 2, rendimento nacional, preço por praça | USABLE | USABLE | USABLE | USABLE | 25 anos | anual/semanal | — | **PILOT READY** (parcial) |
| **DISTRIBUTION** | empresas, comuna, porte | USABLE | EMPTY | EMPTY | EMPTY | data de criação | contínua | — | COMING SOON |
| **WEATHER** | série diária por ponto | STRONG | STRONG | STRONG | STRONG | décadas | diária | — | **PILOT READY como contexto** |
| **ADAMA CONTEXT** | presença registrada + sinal público | USABLE | USABLE | USABLE | — | — | — | — | **PILOT READY** |

---

## 6 · AS TRÊS BUSINESS QUESTIONS RECOMENDADAS

### BQ1 · REGULATORY & PORTFOLIO — *"What changed, what does it touch, and where?"*
**PILOT READY.** Único eixo provado ponta a ponta. Hero: CASE-011 + CASE-014.
Mercados: EU → FR → IT. Espanha entra como `NÃO SEI` declarado.

### BQ2 · MARKET DEVELOPMENT — *"Is this signal real, where is it happening, what supports it, and does ADAMA have a response?"*
**PILOT READY, com escopo declarado: Espanha / olivar / repilo.**
**Foi medido, não escolhido por preferência** — dos três candidatos, é o único que fecha
**5 das 6** perguntas do fluxo do SLIDE 8:

| candidato | signal | is it real? | where else? | what supports? | ADAMA response? | validate? | fecha |
|---|---|---|---|---|---|---|---|
| **ES · olivar · repilo** | ✅ | ✅ 23 safras + coorte | ✅ 2 de 7 províncias | ⚠️ | ✅ Neptune | ✅ | **5/6** |
| ES · vinha · míldio | ✅ | ⚠️ 1 safra analisada | ✅ | ❌ X-009 refuta | ✅ Vinergy | ✅ | 4/6 |
| Cereais · septoriose | ⚠️ sem sinal de campo | ❌ | ❌ | ✅ | ✅ | ✅ | 3/6 |

### BQ3 · CROSS-MARKET — *"Does the same molecule appear elsewhere?"*
**PILOT READY — e por MOLÉCULA, não por ISSUE.** Medido: X-006 cobre **82,1%** do uso,
X-007 cobre **23,5%**. A primeira demonstração cross-market **deve** usar molécula.
Hero: CASE-014.

---

## 7 · HERO CASES — três, não quatro

| # | Caso | Prova qual parte do motor | Por que entra |
|---|---|---|---|
| **1** | **CASE-014** protioconazol FR+IT | **Connect** + **Local to shared** | a única prova literal de *"make relevant signals travel"*: mesma molécula, dois mercados, 8 produtos, e a data europeia reaparecendo no vencimento italiano |
| **2** | **CASE-013** repilo em 23 safras | **Market Development** (SLIDE 8) | único caso que responde 5 das 6 perguntas do fluxo, com controle de coorte contra artefato de amostragem |
| **3** | **CASE-008** o clima não explica a doença | **Trust** (SLIDE 12) | prova que o sistema **recusa** a correlação fácil. Sustenta a credibilidade dos outros dois |

**Rebaixados a SUPPORT:** CASE-011 (absorvido pelo CASE-014), CASE-003, CASE-012, CASE-015 —
este último é o melhor **TECHNICAL PROOF** do repositório, porque mostra o custo de não
normalizar entidade.

---

## 8 · PACOTE PARA O CLAUDE DESIGN

O que a missão de design recebe pronto, sem precisar descobrir nada:

| Precisa de | Está em |
|---|---|
| o que o deck prometeu, slide a slide | `CONTRATO-DE-PROVA-DA-APRESENTACAO.md` + `RECONCILIACAO-DECK-REAL.md` |
| o que está provado e o que não está | `MATRIZ-DE-PROVA-EAME.md` |
| que áreas o portal precisa ter | `../ferramentas/ARQUITETURA-DE-INFORMACAO-EAME.md` (reconciliada com o SLIDE 7) |
| que fontes alimentam cada área | `SOURCE-PACKS-EAME.md` |
| que números reais mostrar | `../../data/samples/` — 24 amostras com proveniência testada |
| que limites precisam aparecer na tela | o campo *"Não conclua"* de cada caso e cada RED TEAM |
| como o piloto será julgado | DECK-032: *relevance · evidence quality · time-to-insight · usefulness* |

**Regra para o design:** nenhum bloco sem `FACT` / `INTERPRETATION` / `ACTION` separados, sem
fonte, sem data e sem o ponteiro de evidência. E **nenhum número inventado** — se falta,
a tela escreve *"we don't know yet"*, como o SLIDE 12 promete.
