# REGISTRO MESTRE DE FONTES

**31 fontes.** Toda fonte tem `SOURCE_ID` estável; os objetos do pacote apontam para ele.

| SOURCE_ID | fonte | tipo | geografia | cadência | último | acesso |
|---|---|---|---|---|---|---|
| `IT-SRC-MINISTERO` | Ministero della Salute — Banca dati prodotti fitosanitari | OFFICIAL | IT | continua | 2026-08-24 (PROD_FTS_6) | GREEN |
| `IT-SRC-CELLAR` | EU Publications Office — CELLAR / SPARQL | OFFICIAL | EU | continua | 2026-07-28 | GREEN |
| `IT-SRC-AGRIFOOD` | European Commission — Agri-food Data Portal | MARKET | EU/IT | semanal | 2026-08-23 | GREEN |
| `IT-SRC-GIRE` | GIRE — Gruppo Italiano Resistenza Erbicidi (CNR-IPSP) | RESEARCH | IT | irregular | 2025-06 | GREEN |
| `IT-SRC-OPENALEX` | OpenAlex | RESEARCH | GLOBAL | continua | 2026-07-30 | GREEN |
| `IT-SRC-META` | Meta Ads Library | COMPANY | IT/ES/FR | continua | 2026-08-31 | PARTIAL |
| `IT-SRC-YOUTUBE` | YouTube | PEOPLE | GLOBAL | continua | 2026-08-28 | GREEN |
| `IT-SRC-MODENA` | Consorzio Fitosanitario Provinciale di Modena | FIELD | Emilia-Romagna | semanal | 2026-08-18 | GREEN |
| `IT-SRC-PIEMONTE` | Regione Piemonte — Settore Fitosanitario | OFFICIAL | Piemonte | anual + boletins | 2026-03-16 | GREEN |
| `IT-SRC-ISTAT` | ISTAT — esploradati (SDMX) | OFFICIAL | IT | anual | 2024 | GREEN |
| `IT-SRC-EUROSTAT` | Eurostat | OFFICIAL | EU | anual/mensal | 2024 | GREEN |
| `IT-SRC-PROBE-001` | Terra e Vita (Edagricole) | TECHNICAL_MEDIA | IT | DATED | ['Sat, 29 Aug 2026 07:30:57 +0000', 'Fri, 28 Aug 2026 16:57: | GREEN |
| `IT-SRC-PROBE-002` | L'Informatore Agrario | TECHNICAL_MEDIA | IT | DATED | ['Thu, 27 Aug 2026 09:24:29 +0000', 'Thu, 27 Aug 2026 07:04: | GREEN |
| `IT-SRC-PROBE-003` | AgroNotizie (Image Line) | TECHNICAL_MEDIA | IT | DATED | ['25/11/2004'] | GREEN |
| `IT-SRC-PROBE-004` | Image Line (grupo) | TECHNICAL_MEDIA | IT | DATED | ['2026-08-24'] | GREEN |
| `IT-SRC-PROBE-005` | Regione Veneto — bollettini 2026 | FIELD | IT | DATED | ['27/08/2026', '13/08/2026', '06/08/2026', '30/07/2026', '22 | GREEN |
| `IT-SRC-PROBE-006` | ERSA FVG — colture erbacee 2026 | FIELD | IT | NO_DATE_FOUND | [] | GREEN |
| `IT-SRC-PROBE-007` | Regione Lombardia — bollettini | FIELD | IT | DATED | ['09/06/2021', '31/07/2026', '07/06/2022', '21/06/2022'] | GREEN |
| `IT-SRC-PROBE-008` | Emilia-Romagna — fitosanitario | FIELD | IT | DATED | ['2013-04-24', '2013-04-24', '2022-06-30', '2022-06-30', '20 | GREEN |
| `IT-SRC-PROBE-009` | Agrometeo Puglia — bollettini | FIELD | IT | DATED | ['11/04/2018', '07/08/2017', '11/04/2018', '07/08/2017'] | GREEN |
| `IT-SRC-PROBE-010` | CREA | RESEARCH_INSTITUTION | IT | DATED | ['2026-08-24'] | GREEN |
| `IT-SRC-PROBE-011` | CNR — Istituto di Scienze delle Produzioni Alimentari | RESEARCH_INSTITUTION | IT | NO_DATE_FOUND | [] | GREEN |
| `IT-SRC-PROBE-012` | Co.Pro.B. (beterraba) | COOPERATIVE | IT | None | None | NOT_REACHED |
| `IT-SRC-PROBE-013` | Assoproli Bari (olivo) | PRODUCER_ORG | IT | DATED | ['2024-06-11', '2024-06-11', '2024-06-11', '2026-05-15'] | GREEN |
| `IT-SRC-PROBE-014` | Confagricoltura Veneto | COOPERATIVE | IT | DATED | ['2026-06-10', '2025-07-02', '2026-06-10', '2025-07-02', '20 | GREEN |
| `IT-SRC-PROBE-015` | Coldiretti | COOPERATIVE | IT | DATED | ['15/09/2015', '15/09/2015', '26/06/2026', '26/06/2026', '26 | GREEN |
| `IT-SRC-PROBE-016` | Syngenta Italia | COMPETITOR | IT | None | None | BLOCKED |
| `IT-SRC-PROBE-017` | BASF Agro Italia | COMPETITOR | IT | NO_DATE_FOUND | [] | GREEN |
| `IT-SRC-PROBE-018` | Corteva Italia | COMPETITOR | IT | DATED | ['2025-12-01', '2024-06-06', '2025-12-01', '2024-06-06', '20 | GREEN |
| `IT-SRC-PROBE-019` | Bayer Crop Science Italia | COMPETITOR | IT | None | None | BLOCKED |
| `IT-SRC-PROBE-020` | ADAMA Italia | ADAMA | IT | None | None | BLOCKED |

---

## Limitação declarada de cada fonte

- **Ministero della Salute — Banca dati prodotti fitosanitari** — o rotulo e PDF; a coluna de epoca de aplicacao nao foi extraida
- **EU Publications Office — CELLAR / SPARQL** — so acha ato cujo titulo nomeia a substancia
- **European Commission — Agri-food Data Portal** — responde 302; sem -L devolve pagina de redirect. Preco vem como TEXTO.
- **GIRE — Gruppo Italiano Resistenza Erbicidi (CNR-IPSP)** — o host com TLS (gire.ipsp.cnr.it) tem certificado expirado; use o espelho
- **OpenAlex** — afiliacao e do AUTOR, nao do estudo. 429 depende do IP de saida.
- **Meta Ads Library** — so abre em navegador com janela grafica. Nao publica gasto nem alcance.
- **YouTube** — comentario devolve tempo RELATIVO, nao data. Coleta e paga (Apify).
- **Consorzio Fitosanitario Provinciale di Modena** — e UMA provincia. Nao representa a regiao nem o pais.
- **Regione Piemonte — Settore Fitosanitario** — o ato e PDF
- **ISTAT — esploradati (SDMX)** — ano de referencia atrasa em relacao a safra corrente
- **Eurostat** — rendimento so por pais, nao por NUTS2
- **Terra e Vita (Edagricole)** — sondada em 2026-08-30; estado pode ter mudado
- **L'Informatore Agrario** — sondada em 2026-08-30; estado pode ter mudado
- **AgroNotizie (Image Line)** — sondada em 2026-08-30; estado pode ter mudado
- **Image Line (grupo)** — sondada em 2026-08-30; estado pode ter mudado
- **Regione Veneto — bollettini 2026** — sondada em 2026-08-30; estado pode ter mudado
- **ERSA FVG — colture erbacee 2026** — sondada em 2026-08-30; estado pode ter mudado
- **Regione Lombardia — bollettini** — sondada em 2026-08-30; estado pode ter mudado
- **Emilia-Romagna — fitosanitario** — sondada em 2026-08-30; estado pode ter mudado
- **Agrometeo Puglia — bollettini** — sondada em 2026-08-30; estado pode ter mudado
- **CREA** — sondada em 2026-08-30; estado pode ter mudado
- **CNR — Istituto di Scienze delle Produzioni Alimentari** — sondada em 2026-08-30; estado pode ter mudado
- **Co.Pro.B. (beterraba)** — sondada em 2026-08-30; estado pode ter mudado
- **Assoproli Bari (olivo)** — sondada em 2026-08-30; estado pode ter mudado
- **Confagricoltura Veneto** — sondada em 2026-08-30; estado pode ter mudado
- **Coldiretti** — sondada em 2026-08-30; estado pode ter mudado
- **Syngenta Italia** — sondada em 2026-08-30; estado pode ter mudado
- **BASF Agro Italia** — sondada em 2026-08-30; estado pode ter mudado
- **Corteva Italia** — sondada em 2026-08-30; estado pode ter mudado
- **Bayer Crop Science Italia** — sondada em 2026-08-30; estado pode ter mudado
- **ADAMA Italia** — sondada em 2026-08-30; estado pode ter mudado
