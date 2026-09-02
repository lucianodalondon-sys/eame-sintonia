# LEIA PRIMEIRO — ITALY REALITY HANDOFF V2

**02/09/2026** · pacote canônico · **zero sintéticos**

Este pacote é o anterior **inteiro** mais uma camada nova que passou por um portão de qualidade, registro a registro.

---

## ⚠️ A COISA MAIS IMPORTANTE DESTE ARQUIVO

Os 321 registros da coleta last-mile são **registros de coleta externa real**.
Eles **não** são 321 fatos validados de forma independente.

Uma segunda leva de agentes foi às fontes com ordem de **derrubar**:

| | |
|---|---:|
| amostrados | **104** |
| sobreviveram | **70** |
| **caíram** | **34 (32.7%)** |

> **Um em cada três não resistiu ao confronto com a própria fonte.**

a missao cita 52/72 (28 por cento). O numero certo e 70/104 (33 por cento): a montagem anterior perdeu a conferencia de 5 blocos ao casar nome de familia com nome de bloco. O erro e meu e a taxa real e PIOR.

---

## O PORTÃO — o que pode virar frase de tela

| estado | quantos | pode sustentar afirmação ao cliente? |
|---|---:|---|
| `QA_PASS` | 65 | **sim** |
| `QA_CORRECTED` | 33 | **sim** |
| `QA_UNREVIEWED` | 221 | **não sozinho** — fica no corpus de pesquisa |
| `QA_REJECTED` | 1 | **nunca** — está na quarentena |

**Client-safe: 98 de 319.**

⚠️ E o número que fecha o portão: **afirmações visíveis ao cliente sustentadas por `QA_UNREVIEWED` = 0**.

---

## O QUE FOI CORRIGIDO, E COMO

A conferência derrubou 34 registros. **33 foram reconstruídos** — campo por campo, não com um aviso pendurado — e **1 foi rejeitado**.

Por causa:

| causa | quantos |
|---|---:|
| ATRIBUICAO_DE_FALA | 1 |

O registro cru **não fica vivo ao lado do corrigido**. Ele está em `QUARANTINED-RECORDS.json`, com a linhagem e a lista do que mudou.

### A rejeição

Um rizicultor real, uma matéria real — e uma frase que **não é dele**. No HTML ela está dentro de `<blockquote>` sem aspas: é o destaque editorial que o jornal montou. **Atribuição de fala errada não tem conserto**, porque reescrever o campo não devolve a frase à boca de ninguém.

---

## AS DEZ FAMÍLIAS — e por que não viram uma tabela só

| família | arquivo | registros |
|---|---|---:|
| MARKET_OBSERVATIONS | `MARKET-OBSERVATIONS.json` | 80 |
| CURRENT_FIELD_SIGNALS | `CURRENT-FIELD-SIGNALS.json` | 49 |
| AGROMET_CONDITIONS | `AGROMET-CONDITIONS.json` | 44 |
| CROP_ECONOMIC_WEIGHT | `CROP-ECONOMIC-WEIGHT.json` | 33 |
| REGULATORY_FUTURE | `REGULATORY-FUTURE.json` | 28 |
| FUTURE_EVENTS | `FUTURE-EVENTS.json` | 22 |
| PUBLIC_VOICES | `PUBLIC-VOICES.json` | 21 |
| COMPETITOR_PUBLIC_SIGNALS | `COMPETITOR-PUBLIC-SIGNALS.json` | 16 |
| HERBICIDE_CURRENT_CONTEXT | `HERBICIDE-CURRENT-CONTEXT.json` | 16 |
| COMMERCIAL_CATALOG | `COMMERCIAL-CATALOG.json` | 10 |

Preço, boletim, clima e voz têm semânticas diferentes. Achatá-las foi o que fez o demo anterior apresentar conversa de horta como inteligência de lavoura.

---

## AS LEIS QUE VIAJAM COM O DADO

**ESCOPO NUNCA SOBE.** `PROVINCIAL`, `AREALE`, `ESTACAO`, `PIAZZA`, `MACROAREA` e `GRADE_DE_MODELO` jamais viram `REGIONAL` ou `NACIONAL`.
- boletins provinciais da Campânia ≠ censo regional da Campânia
- Metapontino ≠ Basilicata inteira
- Trento ≠ Trentino-Alto Adige (o Sudtirol é outra província)
- preço de uma piazza ≠ preço nacional

**CONDIÇÃO NÃO É PRESENÇA.** Clima ≠ doença · risco de modelo ≠ presença no campo · vetor ≠ doença · janela sazonal ≠ surto · comunicação ≠ participação de mercado · voz ≠ incidência.

**PRORROGAÇÃO NÃO É RENOVAÇÃO.** 39 das 50 substâncias do portfólio estão em aprovação prorrogada. Rascunho, discussão e reunião não são decisão.

**CATÁLOGO NÃO É TITULAR.** Seis produtos do catálogo ADAMA têm autorização em nome de outra empresa. Titular ≠ vendedor, e o contrato comercial continua **desconhecido**.

---

## A ROTA — §18

O metadado de acesso é **infraestrutura de coleta**, não dependência do portal.

Três fontes só abriram por saída italiana (ISMEA, ISTAT, ARPAV). Isso está gravado em `SOURCES.json` para automação futura. **O portal lê dado já guardado e nunca precisa da VPN para renderizar.**

---

## O QUE FOI PRESERVADO

`PREVIOUS-HANDOFF/` traz o pacote anterior **inteiro e intocado**: 7740 objetos, incluindo os 2.030 pares de uso de rótulo, as 561 atividades de concorrente, as 58 vozes de plateia, os 88 registros científicos, as 34 resistências do GIRE e os 163 produtos do registro.

⚠️ O portão de QA é sobre a camada **nova**. Aplicá-lo retroativamente rebaixaria trabalho que já tem a sua própria proveniência.

---

## POR ONDE COMEÇAR

1. este arquivo
2. `VALIDATION-MANIFEST.json` — os números, sem maquiagem
3. `TOP-CROSSINGS.json` — 19 cruzamentos, cada um com os IDs exatos
4. `CONFLICT-RESOLUTION.json` — o que as duas camadas disseram diferente
5. a família que interessar

⛔ **Não** comece pelo `NEW-REAL-DATA.json` da missão anterior. Ele contém os registros crus que a conferência derrubou.
