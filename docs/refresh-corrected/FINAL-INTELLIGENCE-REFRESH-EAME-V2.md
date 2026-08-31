# FINAL INTELLIGENCE REFRESH — V2 CORRIGIDO

**Data:** 2026-08-31 · base `eb18c87` (testemunha V1 preservada) ·
**zero rede, zero coleta**

```
MANDATORY_HANDOFFS_ACCEPTED = 4/4        FIELD_HISTORICAL_SCOPE = IN
CASE_MULTI_SIGNAL_CONVERGENCES = 0       FULL_CASE_KEYS_V2 = 1
IDENTITY_CHAIN_CONVERGENCES = 36         LONGITUDINAL_FIELD_OBJECTS = 1
REGULATORY_DEADLINE_OBJECTS = 155
```

Correções detalhadas em [`PRE-ARBITRATION-CORRECTION-EAME.md`](PRE-ARBITRATION-CORRECTION-EAME.md).

---

## 1 · A UNIDADE DEIXOU DE SER ÚNICA

O V1 tinha um tipo de objeto: o **caso**. Por isso publicou `ACT_NOW = 0` como se fosse o
estado do produto inteiro. **Eram quatro tipos, e só um estava sendo medido.**

| objeto | unidade | quantidade | o que afirma |
|---|---|---|---|
| **CASE** | país × região × cultura × problema × tempo | **1** com chave completa | um fenômeno de campo, num lugar, num momento |
| **IDENTITY_CHAIN** | competidor × país × produto | **36** tuplas · 29 produtos | a mesma identidade sustentada em três fontes |
| **LONGITUDINAL_FIELD_PRESSURE** | país × região × cultura × problema × tempo | **1** | pressão medida ao longo de safras |
| **REGULATORY_DEADLINE** | país × registro × produto × prazo | **155** | uma data pública futura |

**Nenhum deles é o outro**, e somá-los seria o mesmo erro que o grafo de dependências
existe para impedir.

---

## 2 · CASE — um, e agora provado pela passagem

### `IT × Toscana/Grosseto × DURUM_WHEAT × FUSARIUM`

```
COUNTRY  IT  PROVED (herdado do mandato da fonte)
REGION   Toscana  PROVED (NAMED_IN_TEXT)     LOCALITY  Provincia di Grosseto
CROP     DURUM_WHEAT  PROVED — dentro da passagem, ausente do rótulo do item
ISSUE    FUSARIUM     PROVED
TIME     2026-04-23   PROVED
```

**A citação certa**, que o V1 não mostrava:

> *"**Fusariosi** Si segnala la comparsa di sintomi lievi nel **frumento duro** in alcune
> situazioni..."*

```
INDEPENDENT_SIGNAL_FAMILIES ........ 1   TERRITORIAL
CONVERGENCE_CLASS .................. SINGLE_SIGNAL
CROP_STAGE_AT_OBSERVATION .......... PROVED
APPLICATION_TRIGGER_AT_OBSERVATION . PROVED
CURRENT_CROP_STAGE_TODAY ........... NOT_PROVED
CURRENT_APPLICATION_WINDOW ......... NOT_PROVED
FUTURE_SEASON_WINDOW ............... NOT_ENOUGH_TIME_CONTEXT
SOURCE_LATENCY ..................... 130 dias
```

**O boletim de 23/04 declara fenologia e recomenda tratamento.** Isso prova o estágio **na
observação** e o gatilho **na observação** — e nada sobre hoje. O V1 escreveu "abril–maio
de 2027" por analogia com 2026; foi removido.

### Os cinco recortes sem chave completa

| recorte | itens | c/ cultura | c/ problema | c/ tempo | c/ local | par provado | **chave** |
|---|---:|---:|---:|---:|---:|---:|---:|
| `ES_OLIVE_REPILO` | 10 | 9 | **0** | 4 | 10 | 0 | 0 |
| `ES_CEREAL_SEPTORIA` | 10 | 4 | **0** | 4 | 10 | 0 | 0 |
| `IT_VINE_FLAVESCENCE` | 1 | 1 | **0** | 1 | 1 | 0 | 0 |
| `FR_VINE_DOWNY_MILDEW` | 11 | 9 | **4** | 7 | 4 | **2** | 0 |
| `FR_CEREAL_SEPTORIA` | 11 | 2 | **0** | 7 | 4 | 0 | 0 |

**O bloqueador não é o mesmo em todos**, e o V1 tratava como se fosse:

- **Espanha:** falta o **problema** — 10 itens, zero com o problema no corpo.
- **França:** o problema **sobrevive em 4 itens**; falta **localidade** em 7 dos 11.
- **Itália × videira:** um item só, sem o problema no corpo.

---

## 3 · IDENTITY_CHAIN — 36 tuplas, e não é convergência de caso

```
candidatas ......... 174    provadas ... 36    recusadas ... 0    não sabidas ... 138
produtos ........... 29 de 147
por país ........... ES 22 · IT 10 · FR 4
por empresa ........ BASF 23 · BAYER 7 · CORTEVA 4 · UPL 2
URBOLE_GUARD ....... PASS, exercido por mutação
conservação ........ 36 + 0 + 138 = 174  ✓
```

**Proposição:** a mesma identidade de produto/titular é sustentada entre marca depositada,
registro local e anúncio observado — **com concordância de titular e país nas três pontas**.

**Não exige `CROP` nem `ISSUE` para existir.** E não prova problema de campo, demanda,
movimento de mercado, venda nem sucesso.

`IDENTITY_CONVERGENCE ≠ PHENOMENON_CONVERGENCE`.

---

## 4 · LONGITUDINAL_FIELD_PRESSURE — o RAIF entrou

```
ES × Andaluzia (7 províncias) × OLIVE × REPILO
amostragens 2026 ............ 20.970
série preservada ............ 11 safras · 44.584 leituras   ⚠️ ver divergência
coorte de controle .......... 5 províncias
backtest: disparos .......... 14
backtest: falsos positivos .. 11 de 14
```

**A conclusão é do próprio artefato:** *"a pressão de campo medida NÃO é um motor de aviso
de 6 a 12 meses. Ela entrega, no melhor caso observado, UMA safra."*

**Divergência declarada:** o artefato de série diz 11 safras; o backtest diz 23. Unidades
diferentes, e **não se escolhe a mais conveniente**.

**Independência do territorial: `NOT_PROVED`.** O RAIF também é fonte territorial (4 itens).
`SAME_PUBLISHER ≠ INDEPENDENT_OBSERVATION`.

**E o `adama_link`** do artefato (*"Neptune — fungicida ADAMA para repilo"*) é
`ADAMA_CONTEXT_DECLARED_IN_ARTIFACT` — `LOCAL_PRODUCT_AUTHORIZATION_PROVED = NOT_MEASURED`.

---

## 5 · REGULATORY_DEADLINE — objeto novo, com a lei junto

```
IT · Ministero della Salute · PROD_FTS_6_20260824.csv
produtos no registro ................ 17.695
em vigor ............................. 3.712
com vencimento futuro ................ 3.466
ADAMA em vigor com vencimento futuro .. 155
próximos vencimentos listados ......... 20
```

```
EXPIRY ≠ WITHDRAWAL                EXPIRY_DATE_REACHED ≠ PRODUCT_DISCONTINUED
AÇÃO PERMITIDA:  REVIEW / CONFIRMATION BY REGULATORY
AÇÃO PROIBIDA:   "ALERT: PRODUCT WILL DISAPPEAR"
```

Entra como **candidato de fila de atenção**, nunca como painel regulatório.

---

## 6 · TEMPO — com escopo, como o V1 não tinha

```
CASE_ACT_NOW ..................... 0
OBJECT_ACT_NOW ................... 0
REGULATORY_DEADLINE_REVIEW ....... 155 registros elegíveis a revisão (não a alerta)
NOT_EVALUATED_OBJECT_TYPES ....... COMPETITOR_PUBLIC_COMM (sem conteúdo) ·
                                   CREATOR (avaliado como oferta, não como atenção)
```

**`ACT_NOW = 0` sozinho era enganoso.** A medição do V1 cobria só casos, e havia 155
registros com data pública futura fora dela. Continuam **não** sendo `ACT_NOW` — vencimento
autoriza **revisão**, não alarme — mas agora isso está dito com escopo.

---

## 7 · LATÊNCIA

```
ES-RAIF ....... 4 itens ...   7 · 3.006 · 3.386 · 3.386 dias
IT-LAMMA ...... 1 item  ... 130 dias
FR-VIGNEVIN ... 7 itens ...  56 · 56 · 75 · 95 · 103 · 110 · 172 dias
medidos em 12 de 22 itens
```

⚠️ **Captura única:** todos têm o mesmo `CAPTURED_AT`, então `SOURCE_LATENCY ==
AGE_OF_OBSERVATION` por construção. Isto mede **idade do documento na primeira captura** —
não latência de regime. Os 3.000+ dias do RAIF são documentos históricos numa listagem, não
atraso de pipeline.

---

## 8 · ESTADO

```
FULL_CASE_KEYS_V1 = 1        FULL_CASE_KEYS_V2 = 1        FR_FULL_CASE_KEYS_V2 = 0
CASE_MULTI_SIGNAL_CONVERGENCES = 0
PHENOLOGY_AT_OBSERVATION_PROVED = 3 de 22
APPLICATION_TRIGGER_AT_OBSERVATION_PROVED = 5 de 22
MULTI_BULLETIN_DOCUMENTS = 6        PAIRS_CARTESIAN_AVOIDED = 6
DEPENDENCY_RELATIONS = 17 (13 dependentes · 4 independentes · 6 tipos)
CREATOR_LAST_90D = 164              (o V1 dizia 280, copiado do briefing)
ITALIAN_LABEL_PDFS_LOCAL = 139 de 163
```
