# MODELO DE IDENTIDADE — quem é quem num registro fitossanitário

Regra canônica nascida da investigação do **ES-01717** (MISSÃO 06).

> **`COMPETITOR_IDENTITY` ≠ um único campo `COMPANY`.**

**Data:** 2026-08-29

---

## AS SEIS ENTIDADES — nunca colapsar

| Entidade | O que é | Onde se lê |
|---|---|---|
| **REGISTRATION_ID** | o identificador da autorização | registro nacional |
| **REFERENCE_PRODUCT** | o nome oficial do produto de referência | registro / lista de denominaciones |
| **REFERENCE_HOLDER** | quem **detém** a autorização | ficha do registro |
| **MANUFACTURER** | quem **fabrica** | ficha do registro (quando publicado) |
| **COMMON_DENOMINATION** | nome comercial concedido sobre a **mesma** autorização | lista de denominaciones comunes |
| **CONCESSIONAIRE** | empresa que recebeu a denominação comum | idem |

**A pergunta decide qual entidade importa.** *"Quem pode vender?"* → concessionária.
*"De quem é o registro?"* → titular. *"Quem fabrica?"* → manufacturer.
**Não existe um "dono verdadeiro" universal.**

---

## FICHA DE REFERÊNCIA · ES-01717

```
REGISTRATION_ID:            ES-01717
REFERENCE_PRODUCT (atual):  SORATEL MAX          ← MAPA, versão de 26/08/2026
REFERENCE_PRODUCT (antes):  MAXENTIS             ← MAPA, versão de 28/05/2025
REFERENCE_HOLDER:           ADAMA Agriculture España S.A.
MANUFACTURER:               ADAMA MAKHTESHIM LTD.
COMPOSITION:                AZOXISTROBIN 20% + PROTIOCONAZOL 15% [SC] P/V
STATUS:                     Vigente
COMMON_DENOMINATIONS:
   · SYNGENTA ESPAÑA S.A.            → AMISTAR ERA 350 SC   (aceite 11/09/2024 → 10/08/2026)
   · COMERCIAL QUÍMICA MASSÓ S.A.    → CUMILZAN             (aceite 18/09/2024 → 10/08/2026)
```

**Qualidade de fonte, declarada campo a campo:**

| Campo | Fonte | Qualidade |
|---|---|---|
| `REGISTRATION_ID`, `REFERENCE_PRODUCT`, denominações, concessionárias, datas | **MAPA — dc_web.pdf (26/08/2026) e dc_web_28052025.pdf (28/05/2025)** | **PRIMÁRIA** |
| `REFERENCE_HOLDER`, `MANUFACTURER`, `COMPOSITION`, `STATUS` | agregador comercial do registro espanhol | **SECUNDÁRIA** — não lida por nós em fonte primária |
| corroboração de que MAXENTIS é marca ADAMA | adama.com (AR, US, CA, UK) e registro italiano (ADAMA ITALIA, reg. 018067, azoxistrobina + protioconazol) | primária, indireta |

> **Não lemos a ficha oficial do MAPA.** A aplicação `servicio.mapa.gob.es/regfiweb` responde
> 200, mas a grade é renderizada por JavaScript e as rotas de detalhe devolvem 404.
> A atribuição de titular e fabricante é **fortemente corroborada e não verificada em
> primária**. Registrado assim, não melhor do que isso.

---

## O QUE ISTO **NÃO** SIGNIFICA

| Não dizer | Porque |
|---|---|
| *"A Syngenta vende produto da ADAMA."* | a denominação comum é um regime administrativo espanhol; a relação comercial entre as empresas **não está no documento** |
| *"A ADAMA fabrica o AMISTAR ERA."* | fabricante do **registro de referência** ≠ fabricante de cada lote comercializado sob denominação |
| *"A Syngenta é titular do ES-01717."* | **erro observado ao vivo** nesta missão: um resumo automático de busca chamou a concessionária de titular. É exatamente o colapso que este modelo proíbe |
| *"SORATEL MAX é a mesma coisa que o SORATEL italiano."* | o SORATEL italiano (reg. 018175) é **protioconazol isolado**; o espanhol é azoxistrobina + protioconazol |

---

## É EXCEÇÃO OU PADRÃO? — medido

Sobre a lista completa de *denominaciones comunes* do MAPA (versão 26/08/2026):

| medida | valor |
|---|---|
| denominações comuns concedidas | **1.737** |
| registros de referência distintos | **708** |
| registros com **mais de uma** denominação | **359 (50,7%)** |
| média de marcas por registro | **2,45** |
| máximo observado | **24** (ES-00750) |

**ES-01717 não é exceção. Metade dos registros desta lista é vendida sob mais de uma marca.**

### O experimento de contagem

Contando o **mesmo** universo espanhol de quatro maneiras:

| visão | contagem | o que ela mede |
|---|---|---|
| **por marca / denominação** | **1.737** | identidades comerciais |
| **por registro de referência** | **708** | autorizações reais |
| por concessionária | (empresas distintas) | quem opera comercialmente |
| por titular | não obtível em fonte aberta | quem detém |

**Um radar competitivo que contasse por marca inflaria o mercado espanhol em ~2,45×.**
E um que contasse por concessionária atribuiria a autorização à empresa errada.

---

## TESTE NEGATIVO — a regra precisa distinguir os dois casos

| caso | marca = titular? | exemplo |
|---|---|---|
| **coincidem** | SIM | **AVASTEL** na França: AMM 2240236, titular ADAMA FRANCE SAS, marca AVASTEL. Uma empresa, um nome |
| **divergem** | NÃO | **ES-01717**: titular ADAMA (secundária), produto de referência SORATEL MAX, marcas AMISTAR ERA 350 SC (Syngenta) e CUMILZAN (Massó) |
| **divergem, outro mecanismo** | NÃO | **Itália**: AMISTAR ERA 240 EC registrado sob **CAC CHEMICAL GMBH** — nem denominação comum, nem ADAMA |

A regra **não** é uma exceção para o ES-01717: os três casos convivem, e o modelo tem de
representar os três.
