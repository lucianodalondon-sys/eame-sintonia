# ATTENTION OBJECT MODEL — SINTONIA EAME

**Data:** 2026-08-31 · artefato executável em `data/arbitration/ATTENTION-OBJECT-SCHEMA.json`

```
TOP_LEVEL_PRODUCT_UNIT = ATTENTION_OBJECT
```

---

## 1 · O ENVELOPE COMUM

Todo objeto, de qualquer tipo, carrega:

```
ATTENTION_OBJECT_ID     identidade canônica, NEUTRA DE IDIOMA
OBJECT_TYPE             um dos quatro
COUNTRY                 obrigatório em todos
ATTENTION_STATE         ver ATTENTION-READINESS-GRAMMAR-EAME.md
SOURCE_COMMITS          commit fixo de cada entrada que o sustenta
EVIDENCE                ponteiros para a evidência ORIGINAL, nunca traduzida
WHAT_IS_STILL_UNKNOWN   estado transversal
DECISION_QUESTION       a pergunta de decisão que este objeto responde
DECISION_OWNER          departamento dono — nunca preenchido para completar tabela
TIME                    bloco de tempo, com os sete campos separados
PROVENANCE              SOURCE_ID · AS_OF_DATE · EVIDENCE_CLASS
```

**Cinco estados de campo, e o quinto é o que faltava no V7:**

```
PROVED · NOT_PROVED · NOT_MEASURED · NOT_READY · NOT_APPLICABLE
```

> **`NOT_APPLICABLE` é estado de primeira classe.** Um vencimento regulatório não tem
> cultura. Isso não é "não sei" nem campo vazio esperando preenchimento — é uma dimensão
> que **não existe** naquela unidade. Confundir os dois foi o que fez o V1 tentar encaixar
> tudo na chave do caso.

---

## 2 · PHENOMENON_CASE

```
UNIDADE     COUNTRY × REGION × CROP × ISSUE × TIME
PERGUNTA    um problema medido, num lugar, num momento, merece investigação?
GATILHO     observação de campo com as cinco âncoras no CORPO do documento
BLOCOS      Campo · Ciência · Competição · Portfólio local · Pessoas · Tempo ·
            Ação · Unknowns · Evidência
CONVERGÊNCIA aplicável
```

**O guard que define este tipo:**

> **`CROP_ISSUE_PAIRING_NOT_PROVEN`** — o par só fecha quando o termo da cultura aparece
> **dentro da passagem** que sustenta o problema. Um documento multi-boletim **não**
> autoriza produto cartesiano.

**Medido no acervo:** 6 dos 22 documentos territoriais são multi-boletim; **6 pares
cartesianos foram recusados**. No documento italiano sozinho, 6 pares possíveis → **3
recusados**.

**Exemplo hoje — e ele é sutil:** `IT × Toscana/Grosseto × DURUM_WHEAT × FUSARIUM`.
`DURUM_WHEAT` **não está no rótulo do item** (que diz `CEREAL`). Aparece **dentro da
passagem** da fusariose: *"sintomi lievi nel frumento duro"*. **O par fecha pela passagem,
não pela etiqueta** — e é por isso que o guard existe.

---

## 3 · REGULATORY_DEADLINE

```
UNIDADE          COUNTRY × REGISTRATION × PRODUCT × DEADLINE
PERGUNTA         esta data pública futura exige revisão, e de quem?
NOT_APPLICABLE   CROP · ISSUE · REGION
BLOCOS           Registro · Titular · Prazo · Ação · Evidência
CONVERGÊNCIA     não aplicável
```

```
EXPIRY ≠ WITHDRAWAL              EXPIRY_DATE_REACHED ≠ PRODUCT_DISCONTINUED
AÇÃO PERMITIDA   REVIEW / CONFIRMATION
AÇÃO PROIBIDA    "ALERT: PRODUCT WILL DISAPPEAR"
DO_NOT_BUILD     dashboard regulatório
```

**Exemplo hoje:** Itália — **155** registros ADAMA em vigor com vencimento futuro, de 3.712
em vigor e 17.695 no registro.

**É o único tipo com decisão de negócio defensável hoje** — e é o mais modesto dos quatro,
porque a data é **publicada**, não prevista. Foi ele que forçou a decisão de não exigir
convergência multi-sinal.

---

## 4 · COMPETITOR_IDENTITY_CHAIN

```
UNIDADE          COMPETITOR × COUNTRY × PRODUCT
PERGUNTA         a mesma identidade se sustenta entre marca, registro local e anúncio?
NOT_APPLICABLE   CROP · ISSUE
BLOCOS           Marca · Registro local · Atividade paga observada · Evidência
CONVERGÊNCIA     IDENTITY_CONVERGENCE apenas
```

**Guards:**

```
SAME_NAME ≠ SAME_COMPETITOR_PRODUCT          (URBOLE_GUARD, exercido por mutação)
IDENTITY_CONVERGENCE ≠ PHENOMENON_CONVERGENCE
PAGE_COUNTRY_SCOPE ≠ AD_DELIVERY_COUNTRY
a perna Meta é DERIVED_DEPENDENCY_ON_META — não conta duas vezes
```

**Não prova:** problema de campo · demanda · movimento de mercado · venda · sucesso · que o
produto anunciado está autorizado naquele país.

**Exemplo hoje:** 36 tuplas provadas · 29 produtos · ES 22 · IT 10 · FR 4 · zero recusadas ·
138 honestamente `NOT_KNOWN`.

> **As 36 não entram na Home só por existirem.** Sem gatilho de atenção — uma **mudança**
> observada na cadeia, entre duas leituras com intervalo real — o estado é
> `VALID_EVIDENCE_NOT_ATTENTION_READY`.

---

## 5 · LONGITUDINAL_FIELD_PRESSURE

```
UNIDADE       COUNTRY × REGION × CROP × ISSUE × TIME
PERGUNTA      a pressão medida ao longo de safras muda a ordem de investigação?
BLOCOS        Série · Baseline · Coorte · Backtest · Evidência
CONVERGÊNCIA  aplicável
```

**Guards:**

```
FIELD_PRESSURE ≠ DEMAND
ha × incidência é RELATIVE EXPOSURE INDEX: ordena, nunca dimensiona
a média nunca viaja sem o n
SAME_PUBLISHER ≠ INDEPENDENT_OBSERVATION
ADAMA_CONTEXT_DECLARED_IN_ARTIFACT ≠ LOCAL_PRODUCT_AUTHORIZATION_PROVED
```

**Exemplo hoje:** `ES × Andaluzia × OLIVE × REPILO` (RAIF), 20.970 amostragens em 2026, 7
províncias.

**E a honestidade que vem colada:** o backtest deu **14 disparos com 11 falsos positivos**,
e no melhor caso **uma safra** de antecedência.

```
INDEPENDENCE_FROM_TERRITORIAL_RAIF = NOT_PROVED
```

O RAIF **também** é fonte territorial. Entrar no escopo não compra perna: sem linhagem
parcela-a-parcela, histórico e territorial são **uma** família.

---

## 6 · O BLOCO DE TEMPO — sete campos que nunca se fundem

```
OBSERVATION_TIME        quando a fonte publicou / observou
STAGE_AT_OBSERVATION    o estágio da lavoura NAQUELE momento
CURRENT_CROP_STAGE      o estágio HOJE
LABEL_USE_STAGE         o estágio autorizado no rótulo
APPLICATION_WINDOW      a janela real de aplicação
REGULATORY_DEADLINE     o prazo publicado
FUTURE_SEASON_WINDOW    a janela do ciclo seguinte
```

**Estado medido hoje:**

```
STAGE_AT_OBSERVATION ................ PROVADO em 3 de 22 itens
APPLICATION_TRIGGER_AT_OBSERVATION .. PROVADO em 5 de 22
CURRENT_CROP_STAGE .................. NOT_PROVED em 22 de 22
APPLICATION_WINDOW .................. NOT_PROVED em ES, IT e FR
```

> **`UNKNOWN` continua `UNKNOWN`. Não fabricar calendário** — e **não projetar a janela de
> uma safra sobre a seguinte**. O refresh V1 escreveu "abril–maio de 2027" porque foi assim
> em 2026; foi removido, e o guard existe para que não volte.

---

## 7 · MULTILÍNGUE

```
ATTENTION_OBJECT_ID = LANGUAGE_NEUTRAL
contrato congelado em 1443f643 — preservado integralmente
```

**Um objeto, várias representações. Nunca um objeto por idioma.**
`SOURCE_LANGUAGE ≠ ARTIFACT_LANGUAGE ≠ UI_LANGUAGE ≠ DISPLAY_LANGUAGE ≠
TRANSLATION_TARGET_LANGUAGE`.

---

## 8 · ÍCONE DE DOENÇA

```
OFFICIAL_ADAMA_DISEASE_ICON_ASSET = EXISTS_EXTERNALLY_IN_DESIGN_SYSTEM
DISEASE_ID → OFFICIAL_ADAMA_DISEASE_ICON_ID        (vínculo do V8)
DISEASE_ICON_CROSSWALK = NOT_MEASURED
```

**Não criar substituto genérico.** Enquanto o mapa não for medido no design system oficial,
a linha de produto entra como **cor** — que é oficial — e não como desenho inventado.
