# RÉGUAS DO SINTONIA EAME — ALERTA, CONFIANÇA E INDEPENDÊNCIA

A apresentação promete `EARLY WARNING`, `ALERT`, `INVESTIGATE`, `WATCH`, `3 independent
sources` e `CONFIDENCE = Medium`. Nenhuma dessas palavras significa nada sem uma régua.

> **Sem régua não existe alerta. Existe apenas feed.**

**Data:** 2026-08-28 · Estado: **régua escrita, ainda NÃO APLICADA a um caso real**
(por isso DECK-026 e DECK-027 permanecem `UNPROVED`).

---

## 1 · RÉGUA DE INDEPENDÊNCIA

Duas fontes são **independentes** quando não compartilham a origem do fato.

| Situação | Independente? |
|---|---|
| Dois portais reproduzindo o **mesmo comunicado de imprensa** | **NÃO** — é uma fonte |
| Dois portais citando o **mesmo ato CELEX** | **NÃO** — é uma fonte (o ato) |
| Dois datasets derivados do **mesmo registro oficial** | **NÃO** |
| Registro oficial + medição de campo independente | **SIM** |
| Ato da UE + registro nacional | **PARCIAL** — o nacional depende do europeu por construção; contam como **1,5**, nunca como 2 |
| Duas províncias da **mesma rede** (RAIF) | **NÃO** para independência de fonte; **SIM** para independência geográfica |

**Campos obrigatórios para avaliar:** `ORIGINAL_PUBLISHER` · `SOURCE_OWNER` ·
`DOCUMENT_ORIGIN` · `IS_REPUBLISHED` · `SHARED_DATASET` · `COMMON_PRESS_RELEASE`.

**Regra prática:** conte **publicadores originais distintos**, não URLs.

## 2 · RÉGUA DE CONFIANÇA

Nove dimensões, cada uma verificável. **Não é score ponderado arbitrário** — é uma
sequência de portas.

| Dimensão | Pergunta verificável |
|---|---|
| SOURCE QUALITY | é fonte oficial primária, oficial derivada, técnica reconhecida ou aberta? |
| DIRECTNESS | a fonte **mede** o fato ou **fala sobre** ele? |
| INDEPENDENCE | quantos publicadores originais distintos? (régua 1) |
| RECENCY | a defasagem cabe na janela da decisão? |
| GEOGRAPHIC MATCH | a geografia da fonte é a geografia do fato? (SOURCE ≠ FACT LOCATION) |
| TEMPORAL MATCH | as janelas temporais das partes coincidem? |
| NORMALIZATION CONFIDENCE | qual método casou? (CAS/EXACT = alta; SALT/FUZZY = baixa) |
| CROSSING COVERAGE | que fração do universo o cruzamento alcança? (X-006: 82% do uso) |
| CONTRADICTION | alguma fonte contradiz? |

**Atribuição:**

- **HIGH** — fonte oficial primária **e** medição direta **e** granularidade geográfica e
  temporal coincidentes **e** normalização por CAS ou nome exato **e** sem contradição.
- **MEDIUM** — falha em **uma** dimensão, e a falha está declarada.
- **LOW** — normalização por sal ou fuzzy, **ou** descompasso de geografia/tempo,
  **ou** publicador original único em fato contestável.
- **NÃO SEI** — falta dimensão suficiente para avaliar. **É resposta válida.**

**Exemplo aplicado (CASE-011):** fonte oficial primária ✅, medição direta ✅, geografia
coincidente ✅, normalização por nome exato ✅, sem contradição ✅, mas independência = 1,5
(ato da UE + registro nacional são acoplados) → **CONFIDENCE: HIGH para os fatos,
MEDIUM para a leitura de exposição.**

## 3 · RÉGUA DE ALERTA

Um item só recebe estado de alerta quando **todas** as portas abrem.

| Porta | Exigência |
|---|---|
| BASELINE | existe histórico comparável **da mesma coleta**? Sem isso, **nada de "rises"** |
| NEW OBSERVATION | o fato é novo em relação à última coleta arquivada? |
| CHANGE | a mudança é mensurável na mesma unidade? |
| THRESHOLD | a mudança excede o limiar declarado para aquela família? |
| SOURCE QUALITY | ≥ MEDIUM na régua 2 |
| INDEPENDENCE | ≥ 2 publicadores originais, ou 1 oficial primário |
| RECENCY | dentro da janela de decisão da família |
| CONFIDENCE | HIGH ou MEDIUM. **LOW nunca vira alerta** |

**Estados:**

| Estado | Quando |
|---|---|
| **ALERT** | todas as portas abrem **e** há decisão possível para um usuário nomeado |
| **INVESTIGATE** | fato novo e confiável, mas **sem baseline** — não se pode afirmar mudança |
| **WATCH** | fato conhecido cuja janela se aproxima (ex.: expiração em <12 meses) |
| **EARLY** | sinal detectado numa camada e ainda **não confirmado** em outra |
| **NÃO SEI** | portas insuficientes |

> **Consequência imediata e desconfortável:** hoje o SINTONIA **não pode emitir ALERT** em
> nenhuma família de conversa pública, porque a porta BASELINE não abre em nenhuma delas.
> Pode emitir **WATCH** (protioconazol, expiração 31/03/2027) e **INVESTIGATE**
> (repilo incubado acima do visível em Málaga e Córdoba). Chamar qualquer um dos dois de
> "alerta" seria vender feed como inteligência.

## 4 · LEI FACT / INTERPRETATION / ACTION

Toda saída separa três coisas que nunca se misturam:

| Camada | Definição | Exemplo (CASE-011) |
|---|---|---|
| **FACT** | o que a fonte diz, recuperável | *"CELEX 32025R0787 substitui a data da linha 168, Prothioconazole, por 31 March 2027."* |
| **INTERPRETATION** | o que o SINTONIA deriva | *"Os três produtos de cereal da ADAMA na França dependem dessa substância."* |
| **ACTION** | o que a pessoa da ADAMA pode decidir | *"Antecipar o plano regulatório e observar a renovação."* |

E o comportamento obrigatório permanece: **"Not enough evidence? We don't know yet."**

---

## 5 · CORREÇÃO DA MISSÃO 03 — o baseline nem sempre depende do tempo

A MISSÃO 03 afirmou, de forma **universal**, que *"linha de base histórica não se resolve
pesquisando melhor; só o tempo"*. A MISSÃO 04 reabriu a afirmação fonte a fonte, como
mandava o briefing, e **ela estava errada para a fonte de campo mais forte que temos**.

| Fonte | Conteúdo histórico? | Data? | Coletável? | Comparável no tempo? | Resultado |
|---|---|---|---|---|---|
| **ES-T3-001 RAIF** | **SIM — 23 safras** | SIM | SIM | **SIM, e por parcela** | **RETROSPECTIVE BASELINE POSSIBLE** |
| IT-T3-001 bollettini ER | parcial — 2025 e 2026 no ar; 2024 devolveu 404 | SIM | PDF | limitado | **RETROSPECTIVE PARCIAL** (≈2 safras) |
| FR-T3-002 corpus BSV | **SIM — 40.899 documentos** | SIM | download cortou | provável | **NÃO SEI** — a fonte existe, o acesso falhou |
| EU-T5-001 OpenAlex | SIM — décadas | SIM | SIM | SIM | **RETROSPECTIVE BASELINE POSSIBLE** |
| EU-T4-001 CELLAR | SIM — acervo CELEX | SIM | SIM | SIM | **RETROSPECTIVE BASELINE POSSIBLE** |
| FR-T4-001 E-Phy | **NÃO** — é retrato do estado atual | versão datada | SIM | **não** | **FORWARD-ONLY** |
| IT-T4-001 registro | parcial — traz datas de registro e revogação | SIM | SIM | parcial | **RETROSPECTIVE PARCIAL** |
| Comunicação de concorrente | não avaliado — sites bloqueados | — | **NÃO** | — | **NÃO SEI** |
| Vozes do campo (T8) | — | — | **NÃO** | — | **FORWARD-ONLY**, e nem isso sem chave |

**A afirmação correta é esta:** o baseline é **forward-only** para o registro francês e para
qualquer camada de conversa pública; é **retrospectivo e já disponível** para o RAIF, o
OpenAlex e o CELLAR. **Onde o SINTONIA mais precisa de baseline — pressão de doença — ele
já tem onze safras.**

A recomendação de começar a arquivar continua valendo, mas por outro motivo: o E-Phy é
`FORWARD-ONLY` e é ele que perde história a cada semana, não o campo.
