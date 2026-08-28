# MODELO DE IDENTIDADE — quem é quem num registro fitossanitário

Regra canônica nascida da investigação do **ES-01717** (MISSÃO 06), **fechada em fonte
primária e submetida a red team na MISSÃO 07**.

> **`COMPETITOR_IDENTITY` ≠ um único campo `COMPANY`.**

**Data:** 2026-08-29 · **Fonte das fichas:** `ES-T4-005` (rotas públicas do ROPF)

---

## AS SETE ENTIDADES — nunca colapsar

| Entidade | O que é | Onde se lê | ES-01717 |
|---|---|---|---|
| **REGISTRATION_ID** | o identificador da autorização | registro nacional | `ES-01717` |
| **REFERENCE_PRODUCT** | o nome oficial do produto de referência | ficha do registro | `SORATEL MAX` |
| **REFERENCE_HOLDER** | quem **detém** a autorização | ficha do registro | `ADAMA Agriculture España S.A.` |
| **MANUFACTURER** | quem **fabrica** | ficha do registro | `ADAMA Agricultural Solutions Ltd.` |
| **MANUFACTURING_SITE** | a **planta** | campo `fabrica` da ficha | `ADAMA Agricultural Solutions Ltd. (Neot Hovav)` |
| **COMMON_DENOMINATION** | nome comercial concedido sobre a **mesma** autorização | lista de *denominaciones comunes* | `AMISTAR ERA 350 SC` · `CUMILZAN` |
| **CONCESSIONAIRE** | empresa que recebeu a denominação comum | idem | `SYNGENTA ESPAÑA S.A.` · `COMERCIAL QUÍMICA MASSÓ S.A.` |

**BRAND** não é uma oitava entidade: é o **papel** que `REFERENCE_PRODUCT` e
`COMMON_DENOMINATION` ocupam quando a pergunta é comercial. Continua sendo o nome de um
desses dois campos — nunca um campo próprio, senão o vínculo com a autorização se perde.

**A pergunta decide qual entidade importa.** *"Quem pode vender?"* → concessionária.
*"De quem é o registro?"* → titular. *"Quem fabrica?"* → manufacturer. *"Onde se fabrica?"*
→ site. **Não existe um "dono verdadeiro" universal.**

---

## FICHA DE REFERÊNCIA · ES-01717 — **PRIMÁRIA, campo a campo**

```
REGISTRATION_ID:            ES-01717
REFERENCE_PRODUCT (atual):  SORATEL MAX          ← ficha oficial, 26/08/2026 e 28/08/2026
REFERENCE_PRODUCT (antes):  MAXENTIS             ← MAPA dc_web, versão de 28/05/2025
REFERENCE_HOLDER:           ADAMA Agriculture España S.A.
                            C/ Ramírez de Arellano nº 29-2º · 28043 Madrid · ESPAÑA
MANUFACTURER:               ADAMA Agricultural Solutions Ltd.
                            Golan Street, Airport City · ISRAEL 7019900 POB298
MANUFACTURING_SITE:         ADAMA Agricultural Solutions Ltd. (Neot Hovav)
COMPOSITION:                AZOXISTROBIN 20% + PROTIOCONAZOL 15% [SC] P/V
STATUS:                     Vigente · inscrição 10/06/2024 · caducidade 31/05/2027
LAST TRÂMITE:               MODIFICACION NOMBRE · Terminada · 28/07/2026
USOS AUTORIZADOS:           cebada · centeno · trigo · triticale
COMMON_DENOMINATIONS:
   · SYNGENTA ESPAÑA S.A.            → AMISTAR ERA 350 SC   (aceite 11/09/2024 → 10/08/2026)
   · COMERCIAL QUÍMICA MASSÓ S.A.    → CUMILZAN             (aceite 18/09/2024 → 10/08/2026)
```

**Qualidade de fonte, declarada campo a campo:**

| Campo | Fonte | Qualidade |
|---|---|---|
| todos os campos acima | **MAPA / ROPF** — `GetProductoById?idProducto=114367` **e** a ficha oficial em PDF (`ExportFichaProductoPdfGet`, 5 páginas, doc `114367-2026210`), duas rotas independentes da mesma autoridade | **PRIMÁRIA** |
| nome anterior `MAXENTIS` | **MAPA — dc_web.pdf, versão de 28/05/2025** (documento arquivado) | **PRIMÁRIA** |
| denominações, concessionárias, datas de aceite | **MAPA — dc_web.pdf (26/08/2026)**, lido por `scripts/denominaciones.py` | **PRIMÁRIA** |

**Nenhum campo do ES-01717 depende mais de fonte secundária.**

### Onde a fonte secundária errou — e o que isso ensina

A MISSÃO 06 registrou `MANUFACTURER = ADAMA MAKHTESHIM LTD.` a partir de um agregador
comercial do registro espanhol. O registro oficial diz **`ADAMA Agricultural Solutions
Ltd.`**. A fonte secundária **acertou o grupo e errou a entidade**.

> Uma fonte secundária que acerta o grupo é a mais perigosa: parece confirmada. A regra
> que fica: **grupo empresarial correto não é entidade correta**, e `MANUFACTURER` é um
> nome jurídico, não um pertencimento.

---

## O QUE ISTO **NÃO** SIGNIFICA

| Não dizer | Porque |
|---|---|
| *"A Syngenta vende produto da ADAMA."* | a denominação comum é um regime administrativo espanhol; a relação comercial entre as empresas **não está no documento** |
| *"A ADAMA fabrica o AMISTAR ERA."* | fabricante do **registro de referência** ≠ fabricante de cada lote comercializado sob denominação |
| *"A Syngenta é titular do ES-01717."* | **erro observado ao vivo** na MISSÃO 06: um resumo automático de busca chamou a concessionária de titular. É exatamente o colapso que este modelo proíbe |
| *"SORATEL MAX é a mesma coisa que o SORATEL italiano."* | o SORATEL italiano (reg. 018175) é **protioconazol isolado**; o espanhol `SORATEL` é o **ES-01665** (protioconazol 25% isolado) e o `SORATEL MAX` é azoxistrobina + protioconazol |
| *"A ADAMA fabrica em Israel, logo depende de Israel."* | a ficha nomeia **um** fabricante e **um** site para **este** registro. Não é a cadeia de suprimento da empresa |

---

## TESTE NEGATIVO — os papéis continuam distintos quando os valores coincidem

A pergunta do red team: *se duas entidades tiverem o mesmo valor, o sistema mantém os
papéis separados?* Isto não é hipótese — é **medido**, na lista espanhola:

```
TITULAR == CONCESSIONÁRIA no próprio registro
    165 registros de referência · 263 linhas de denominação
    (medido sobre as 1.228 linhas que o parser resolve; ver COBERTURA abaixo)
```

| caso | `REFERENCE_HOLDER` | `CONCESSIONAIRE` | valores | papéis |
|---|---|---|---|---|
| **ES-01130 · RAPIDINSECT** | EVERGREEN GARDEN CARE FRANCE S.A.S. | EVERGREEN GARDEN CARE FRANCE S.A.S. | **iguais** | **distintos** — a mesma empresa concedeu a si própria duas denominações (`PIRINSECT`, `TURBOPYR`) sobre o seu próprio registro |
| **ES-01829 · TROJAN** | SHARDA CROPCHEM ESPAÑA S.L. | SHARDA + 6 outras | **um igual, seis diferentes** | distintos — o mesmo registro tem o titular *e* seis terceiros como concessionários |
| **ES-01717 · SORATEL MAX** | ADAMA Agriculture España S.A. | SYNGENTA · MASSÓ | **diferentes** | distintos |
| **AVASTEL na França** | ADAMA FRANCE SAS (AMM 2240236) | — (não há regime de denominação comum) | titular e marca alinhados | **ainda distintos**: `REFERENCE_HOLDER` = empresa, `REFERENCE_PRODUCT` = AVASTEL |
| **Itália · AMISTAR ERA 240 EC** | CAC CHEMICAL GMBH | — | — | nem denominação comum, nem ADAMA |

> **`ROLE_A ≠ ROLE_B` mesmo quando `VALUE_A == VALUE_B`.** Um esquema com um único campo
> `COMPANY` perderia a distinção em **165 registros espanhóis**, não num caso de exceção.

---

## COMO O MODELO SE COMPORTA EM REGISTROS DE TAMANHOS DIFERENTES

Amostra sorteada com semente fixa `20260828`, entre registros **vigentes**, num balde por
número de denominações (343 com uma, 142 com duas, 221 com três ou mais):

| registro | produto de referência | titular | fabricante | denominações |
|---|---|---|---|---|
| **ES-00401** | REGISTER 25 WG | ASCENZA PRODUCTOS PARA AGRICULTURA S.A.U. | ASCENZA | 1 — LAINCO, S.A. → FLAZZEX |
| **ES-01143** | KINVARA | BARCLAY CHEMICALS (R&D) LTD. | BARCLAY LTD | 1 — SIPCAM IBERIA S.A. → CLADDA |
| **ES-01130** | RAPIDINSECT | EVERGREEN GARDEN CARE FRANCE S.A.S. | EVERGREEN GARDEN | 2 — **ao próprio titular** → PIRINSECT, TURBOPYR |
| **ES-01491** | ROXY 800 EC | GLOBACHEM N.V. | GLOBACHEM NV | 2 — BAYER → COFENO; CORTEVA → GALA |
| **19549** | ACCRESTO | ADAMA Agriculture España S.A. | ADAMA Agri Sol | 3 — MASSÓ → INFINITY; PROBELTE → CHILLON; KEY → PROQUER |
| **ES-00792** | TANKE 360 | ALBAUGH TKI d.o.o. | IND_AFRASA | 6 — ALBAUGH EUROPE, COARVAL, ZENAGRO, FLOWER, KENOGARD, SOLEM |
| **ES-01829** | TROJAN | SHARDA CROPCHEM ESPAÑA S.L. | SHARDA CROPCHEM LTD | 7 — incluindo o **próprio titular** |

**O que a amostra mostra e que o ES-01717 sozinho não mostrava:**
`REFERENCE_HOLDER` e `MANUFACTURER` divergem com frequência (**GLOBACHEM/GLOBACHEM**
coincide; **ALBAUGH TKI / IND_AFRASA** não; **DE SANGOSSE / LOVELAND PRODUCTS** não). A
estrutura é **estável em todos os baldes** — nenhum registro precisou de campo novo.

---

## COBERTURA DO PARSER — declarada, não presumida

`scripts/denominaciones.py` resolve **1.228 de 1.786 linhas (68,8%)**. O resto fica
`UNRESOLVED`, nunca adivinhado:

| motivo | linhas |
|---|---|
| `CONCESSIONAIRE_NOT_IN_REGISTER_VOCABULARY` — concessionária que não é titular de nenhum registro (distribuidor puro) | 519 |
| `REFERENCE_PRODUCT_NOT_MATCHED` — registro que não está no export atual do ROPF (número histórico) | 39 |

**Uma regra foi testada e descartada:** cortar na primeira forma jurídica
(`S.A.`/`S.L.`/`AG`). Ela dava **96,9%** de cobertura aparente e produzia
`INDUSTRIAS A` + `FRASA, S.A.` e `ECOLOGIA Y PROTECCION AG` + `RICOLA` — erro silencioso,
plausível na tela e falso. **Cobertura maior com erro invisível é pior do que cobertura
menor declarada.**

---

## PERGUNTA QUE NÃO PRECISAMOS FAZER À ADAMA

Nada nesta ficha precisa ser perguntado: titular, fabricante, planta, composição, status,
datas, usos e denominações estão todos em fonte pública primária. **O que continua sendo
pergunta para a ADAMA é o que fonte pública não contém** — volume, preço, canal, margem,
prioridade interna e a relação comercial (se houver) com as concessionárias.
