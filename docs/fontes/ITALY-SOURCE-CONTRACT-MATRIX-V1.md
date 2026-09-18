# MATRIZ DE CONTRATOS DE FONTE — ITÁLIA V1

**Data:** 2026-09-07 · **Branch:** `claude/italy-source-contracts-v1`

Um contrato responde, de forma executável: quem é · onde está · como encontro · o que espero
receber · como sei que é o documento certo · qual a identidade · qual a data · como sei que mudou ·
qual a frequência · o que preservo · como falha · o que a falha significa.

Contratos em `regras/italy_contracts.mjs`. Medidor em `regras/italy_source_health.mjs`.

Este arquivo é **gerado** por `candidatas/italy_write_matrix.mjs`. Não editar à mão.

---

## As leis que esta matriz carrega

```
HTTP_200                 ≠  HEALTHY_SOURCE
EMPTY_LIST               ≠  ZERO_DOCUMENTS        (lista vazia FALHA fechada)
SAME_URL                 ≠  SAME_DOCUMENT         (hash novo = observação nova)
DOCUMENT_ID              ≠  BYTE_ID               (identidade semântica ≠ SHA256)
DECLARED_FREQUENCY       ≠  OBSERVED_FREQUENCY
ACCESS_CLASSIFICATION    ≠  ANALYTIC_VERDICT
SOURCE_VERDICT           ≠  SOURCE_HEALTH
AGROCLIMATIC_SIGNAL      ≠  PEST_OCCURRENCE
COMPANY_CLAIM            ≠  REGULATORY_FACT
BROWSER_RENDERED_EXTRACT ≠  RAW_PRESERVED
QUERY_MATCH              ≠  PROVED_TOPIC
ROWS                     ≠  UNIQUE_ORGANIZATIONS
```

---

## A matriz

| SOURCE_ID | OWNER | T | VAL | ROTA | SAÍDA | IDENTIDADE | CAMPO DE DATA | FREQ. DECLARADA | FREQ. OBSERVADA | FORWARD | ARQUIVO | AUTOM. | SAÚDE | VEREDITO |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `IT-T3-002` | Regione Campania — Servi | T3 | P0 | PREDICTABLE | PDF | provincia + data_do_boletim | a data esta no NOME do arquivo | o proprio site declara: se | **7D — provado por 14 edicoe** | não | NORMAL | HIGH | HEALTHY | GREEN |
| `IT-T3-010` | A.P.OL. — Associazione t | T3 | P0 | DISCOVERED | PDF | ano + numero_da_edicao + comprensorio | VALID_FROM e VALID_TO impresso | o site nao declara cadenci | **7D — provado pelas DATAS d** | não | NORMAL | HIGH | HEALTHY | GREEN |
| `IT-T3-008` | ARIF Puglia — Agenzia re | T3 | P0 | PREDICTABLE | PDF | ano + numero_do_notiziario | no nome do arquivo E no cabeca | o site declara: semanal, c | **7D — provado por 11 edicoe** | não | NORMAL | MEDIUM | HEALTHY | GREEN |
| `IT-T3-005` | Terre dell'Etruria — Soc | T3 | P0 | STATIC | HTML | periodo_do_bollettino | 'Bollettino del periodo dal DD | o documento declara period | **NÃO SEI — uma unica edicao** | **SIM** | CRITICAL | HIGH | HEALTHY | NAO |
| `IT-T4-001` | Ministero della Salute — | T4 | P0 | PREDICTABLE | CSV | data_do_dataset + num_registrazione | data no nome do arquivo | nao declarada em texto; ha | **NÃO SEI — uma unica data o** | não | ALTO ate provar que os antigos ficam | HIGH | HEALTHY | GREEN |
| `IT-T1-001` | ISTAT | T1 | P0 | APPLICATION | CSV | DATAFLOW + REF_AREA + TYPE_OF_CROP + T | TIME_PERIOD | serie anual | **NÃO SEI — nao medido por c** | não | NORMAL | HIGH | HEALTHY | GREEN |
| `IT-T2-004` | SIAS — Servizio Informat | T2 | P1 | STATIC | HTML | table_type + station + window_end | 'dal DD/MM/AAAA al DD/MM/AAAA' | a rede declara 88 estacoes | **NÃO SEI — uma captura so** | **SIM** | CRITICAL | HIGH | HEALTHY | GREEN |
| `IT-T2-001` | ARPAE Emilia-Romagna | T2 | P1 | PREDICTABLE | PDF | ano + numero_do_boletim | AAAAMMDD no nome do arquivo | semanal | **7D — provado por 7 edicoes** | não | BAIXO — ha arquivo por ano de 2021 a 2026 | HIGH | HEALTHY | GREEN |
| `IT-T2-002` | ARPAV Veneto | T2 | P1 | BROWSER_DISCOVERED | PDF | zone_id + generated_at | NAO esta no nome do arquivo. E | o site declara: zonas 2-15 | **NÃO SEI — uma captura so** | **SIM** | CRITICAL | HIGH | HEALTHY | YELLOW |
| `IT-T7-002` | MASAF | T7 | P0 | DISCOVERED | ODS | versao_da_publicacao + codice_organizz | no titulo do link: 'al 31 dice | nao declarada em texto | **1Y — tres edicoes anuais n** | não | NORMAL | MEDIUM | HEALTHY | GREEN |
| `IT-T3-011` | AGRIOS — Alto Adige | T3 | P1 | DISCOVERED | PDF | ano_da_edicao | o ano no titulo da capa | anual, pelo proprio titulo | **NÃO SEI — uma edicao obser** | não | NORMAL | MEDIUM | HEALTHY | GREEN |
| `IT-T5-002` | Fondazione Edmund Mach — | T5 | P1 | APPLICATION | HTML | handle | — | nenhuma | **IRREGULAR — repositorio al** | não | BAIXO | MEDIUM | HEALTHY | GREEN |
| `IT-T9-008` | ADAMA Italia S.r.l. | T9 | P2 | BROWSER_DISCOVERED | BROWSER_RENDERED_EXTRACT | canonical_url + article_published_time | meta article:published_time e  | nenhuma | **NÃO SEI** | não | NORMAL | MEDIUM | HEALTHY | YELLOW |
| `IT-T1-002` | Provincia autonoma di Tr | T1 | NAO SEI | DISCOVERED | HTML |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | GREEN |
| `IT-T1-003` | Regione Toscana | T1 | NAO SEI | DISCOVERED | HTML |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | GREEN |
| `IT-T1-004` | Regione Liguria | T1 | NAO SEI | DISCOVERED | HTML |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | YELLOW |
| `IT-T1-005` | Regione Umbria | T1 | NAO SEI | DISCOVERED | HTML |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | YELLOW |
| `IT-T1-006` | Regione Calabria | T1 | NAO SEI | DISCOVERED | HTML |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | GREEN |
| `IT-T1-007` | Regione Lazio | T1 | NAO SEI | DISCOVERED | HTML |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | GREEN |
| `IT-T1-008` | Regione Lombardia | T1 | NAO SEI | DISCOVERED | PDF |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | GREEN |
| `IT-T1-009` | Regione Lazio | T1 | NAO SEI | DISCOVERED | HTML |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | GREEN |
| `IT-T1-010` | Regione Abruzzo | T1 | NAO SEI | DISCOVERED | HTML |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | GREEN |
| `IT-T1-011` | Regione Umbria | T1 | NAO SEI | DISCOVERED | HTML |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | GREEN |
| `IT-T1-012` | Regione Autonoma Valle d | T1 | NAO SEI | DISCOVERED | HTML |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | GREEN |
| `IT-T1-013` | Assosementi | T1 | NAO SEI | DISCOVERED | HTML |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | GREEN |
| `IT-T1-014` | Ente Nazionale Risi | T1 | NAO SEI | DISCOVERED | HTML |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | YELLOW |
| `IT-T1-015` | Edagricole — New Busines | T1 | NAO SEI | DISCOVERED | HTML |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | GREEN |
| `IT-T1-016` | Italia Olivicola Consorz | T1 | NAO SEI | DISCOVERED | HTML |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | GREEN |
| `IT-T1-017` | Edagricole — New Busines | T1 | NAO SEI | DISCOVERED | HTML |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | GREEN |
| `IT-T1-018` | Rivista di Agraria | T1 | NAO SEI | DISCOVERED | HTML |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | GREEN |
| `IT-T1-019` | Societa Italiana di Agro | T1 | NAO SEI | DISCOVERED | PDF |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | GREEN |
| `IT-T1-020` | Regione Liguria | T1 | NAO SEI | DISCOVERED | HTML |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | GREEN |
| `IT-T1-021` | Image Line | T1 | NAO SEI | DISCOVERED | HTML |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | YELLOW |
| `IT-T1-022` | OlivoNews | T1 | NAO SEI | DISCOVERED | HTML |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | GREEN |
| `IT-T1-023` | SOI | T1 | NAO SEI | DISCOVERED | HTML |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | YELLOW |
| `IT-T10-002` | BMTI — Borsa Merci Telem | T10 | NAO SEI | DISCOVERED | HTML |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | HEALTHY | YELLOW |
| `IT-T10-006` | Il Sole 24 Ore | T10 | NAO SEI | DISCOVERED | HTML |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | GREEN |
| `IT-T10-007` | ISMEA | T10 | NAO SEI | DISCOVERED | HTML |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | GREEN |
| `IT-T10-008` | Italmopa | T10 | NAO SEI | DISCOVERED | HTML |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | GREEN |
| `IT-T10-009` | Camera di Commercio di B | T10 | NAO SEI | DISCOVERED | HTML |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | GREEN |
| `IT-T10-010` | CSO Italy | T10 | NAO SEI | STATIC | PDF |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | GREEN |
| `IT-T10-011` | Ruminantia | T10 | NAO SEI | DISCOVERED | HTML |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | GREEN |
| `IT-T10-012` | Consorzio Tutela Vini d' | T10 | NAO SEI | DISCOVERED | PDF |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | GREEN |
| `IT-T10-013` | Consorzio Arancia Rossa  | T10 | NAO SEI | DISCOVERED | HTML |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | GREEN |
| `IT-T10-014` | Consorzio Tutela Grana P | T10 | NAO SEI | DISCOVERED | PDF |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | GREEN |
| `IT-T10-015` | Consorzio Tutela Prosecc | T10 | NAO SEI | DISCOVERED | PDF |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | YELLOW |
| `IT-T10-016` | Alleanza Cooperative | T10 | NAO SEI | DISCOVERED | HTML |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | GREEN |
| `IT-T11-005` | Unione Italiana Vini | T11 | NAO SEI | DISCOVERED | HTML |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | GREEN |
| `IT-T12-003` | CIA | T12 | NAO SEI | DISCOVERED | PDF |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | YELLOW |
| `IT-T12-004` | Confagricoltura | T12 | NAO SEI | DISCOVERED | HTML |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | YELLOW |
| `IT-T12-005` | AIAB | T12 | NAO SEI | DISCOVERED | PDF |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | GREEN |
| `IT-T12-006` | CIA Agricoltori Italiani | T12 | NAO SEI | DISCOVERED | PDF |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | GREEN |
| `IT-T2-006` | ARPAC | T2 | NAO SEI | DISCOVERED | HTML |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | GREEN |
| `IT-T2-007` | ARPA Sicilia | T2 | NAO SEI | DISCOVERED | HTML |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | GREEN |
| `IT-T2-008` | ARPAT | T2 | NAO SEI | DISCOVERED | HTML |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | GREEN |
| `IT-T2-009` | ISPRA | T2 | NAO SEI | DISCOVERED | PDF |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | GREEN |
| `IT-T2-010` | Provincia autonoma di Tr | T2 | NAO SEI | DISCOVERED | HTML |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | YELLOW |
| `IT-T2-011` | ARPA Lombardia | T2 | NAO SEI | DISCOVERED | PDF |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | YELLOW |
| `IT-T2-012` | ARPA FVG | T2 | NAO SEI | DISCOVERED | HTML |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | GREEN |
| `IT-T2-013` | ARPA Lazio | T2 | NAO SEI | DISCOVERED | HTML |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | GREEN |
| `IT-T2-014` | ARPA Molise | T2 | NAO SEI | STATIC | PDF |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | YELLOW |
| `IT-T2-015` | AIAM | T2 | NAO SEI | DISCOVERED | PDF |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | GREEN |
| `IT-T2-016` | ARPAM | T2 | NAO SEI | DISCOVERED | PDF |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | GREEN |
| `IT-T2-017` | CNR | T2 | NAO SEI | DISCOVERED | HTML |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | GREEN |
| `IT-T2-018` | CNR | T2 | NAO SEI | DISCOVERED | HTML |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | GREEN |
| `IT-T2-019` | ARPA Piemonte | T2 | NAO SEI | DISCOVERED | HTML |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | YELLOW |
| `IT-T2-020` | ARTA Abruzzo | T2 | NAO SEI | DISCOVERED | PDF |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | GREEN |
| `IT-T2-021` | ARPAL | T2 | NAO SEI | DISCOVERED | HTML |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | YELLOW |
| `IT-T2-022` | ARPA Valle d'Aosta | T2 | NAO SEI | DISCOVERED | HTML |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | YELLOW |
| `IT-T2-023` | ARPAB | T2 | NAO SEI | DISCOVERED | HTML |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | GREEN |
| `IT-T2-024` | ANBI | T2 | NAO SEI | DISCOVERED | PDF |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | GREEN |
| `IT-T3-013` | Regione Emilia-Romagna | T3 | NAO SEI | DISCOVERED | HTML |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | YELLOW |
| `IT-T3-014` | MASAF — Servizio Fitosan | T3 | NAO SEI | DISCOVERED | HTML |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | GREEN |
| `IT-T3-015` | Regione Toscana | T3 | NAO SEI | DISCOVERED | HTML |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | GREEN |
| `IT-T3-016` | Regione Veneto | T3 | NAO SEI | DISCOVERED | HTML |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | GREEN |
| `IT-T3-017` | CNR | T3 | NAO SEI | DISCOVERED | HTML |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | YELLOW |
| `IT-T3-018` | CNR | T3 | NAO SEI | DISCOVERED | HTML |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | YELLOW |
| `IT-T3-019` | Universita di Torino | T3 | NAO SEI | DISCOVERED | HTML |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | YELLOW |
| `IT-T3-020` | SEI | T3 | NAO SEI | DISCOVERED | PDF |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | GREEN |
| `IT-T3-021` | SIPaV | T3 | NAO SEI | DISCOVERED | HTML |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | YELLOW |
| `IT-T5-006` | CNR | T5 | NAO SEI | DISCOVERED | HTML |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | GREEN |
| `IT-T5-007` | Institut Agricole Region | T5 | NAO SEI | DISCOVERED | PDF |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | GREEN |
| `IT-T5-008` | Fondazione Agrion | T5 | NAO SEI | DISCOVERED | PDF |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | GREEN |
| `IT-T5-009` | Fondazione Minoprio | T5 | NAO SEI | DISCOVERED | PDF |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | GREEN |
| `IT-T5-010` | Fondazione Navarra | T5 | NAO SEI | DISCOVERED | PDF |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | GREEN |
| `IT-T5-011` | Universita di Bari Aldo  | T5 | NAO SEI | DISCOVERED | PDF |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | GREEN |
| `IT-T5-012` | Universita di Pisa | T5 | NAO SEI | DISCOVERED | PDF |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | GREEN |
| `IT-T5-013` | CRPA | T5 | NAO SEI | DISCOVERED | PDF |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | YELLOW |
| `IT-T5-014` | Universita della Tuscia | T5 | NAO SEI | DISCOVERED | PDF |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | YELLOW |
| `IT-T5-015` | CNR | T5 | NAO SEI | DISCOVERED | HTML |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | GREEN |
| `IT-T5-016` | Universita degli Studi d | T5 | NAO SEI | DISCOVERED | PDF |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | YELLOW |
| `IT-T5-017` | Universita di Firenze | T5 | NAO SEI | DISCOVERED | PDF |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | YELLOW |
| `IT-T5-018` | Universita di Bologna | T5 | NAO SEI | STATIC | PDF |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | YELLOW |
| `IT-T5-019` | Universita di Padova | T5 | NAO SEI | DISCOVERED | PDF |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | YELLOW |
| `IT-T5-020` | Universita di Torino | T5 | NAO SEI | DISCOVERED | PDF |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | YELLOW |
| `IT-T5-021` | Universita di Firenze | T5 | NAO SEI | DISCOVERED | HTML |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | YELLOW |
| `IT-T5-022` | Firenze University Press | T5 | NAO SEI | DISCOVERED | PDF |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | GREEN |
| `IT-T5-023` | SSICA | T5 | NAO SEI | DISCOVERED | PDF |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | GREEN |
| `IT-T5-024` | Universita degli Studi d | T5 | NAO SEI | DISCOVERED | HTML |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | GREEN |
| `IT-T5-025` | Scuola Superiore Sant'An | T5 | NAO SEI | DISCOVERED | HTML |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | YELLOW |
| `IT-T5-026` | Universita di Palermo | T5 | NAO SEI | DISCOVERED | PDF |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | YELLOW |
| `IT-T5-027` | Universita di Padova | T5 | NAO SEI | DISCOVERED | HTML |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | YELLOW |
| `IT-T5-028` | Universita di Udine | T5 | NAO SEI | DISCOVERED | HTML |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | YELLOW |
| `IT-T5-029` | Universita di Verona | T5 | NAO SEI | DISCOVERED | PDF |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | YELLOW |
| `IT-T5-030` | Universita di Teramo | T5 | NAO SEI | DISCOVERED | HTML |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | GREEN |
| `IT-T5-032` | Universita di Perugia | T5 | NAO SEI | DISCOVERED | HTML |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | YELLOW |
| `IT-T5-033` | Universita di Bologna | T5 | NAO SEI | DISCOVERED | HTML |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | GREEN |
| `IT-T5-034` | Accademia dei Georgofili | T5 | NAO SEI | DISCOVERED | HTML |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | GREEN |
| `IT-T5-035` | Accademia dei Georgofili | T5 | NAO SEI | DISCOVERED | HTML |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | YELLOW |
| `IT-T5-036` | Accademia dei Georgofili | T5 | NAO SEI | DISCOVERED | HTML |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | YELLOW |
| `IT-T7-013` | CONAF | T7 | NAO SEI | DISCOVERED | HTML |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | GREEN |
| `IT-T7-014` | Consorzi Agrari d'Italia | T7 | NAO SEI | DISCOVERED | PDF |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | GREEN |
| `IT-T9-009` | Cifo | T9 | NAO SEI | DISCOVERED | HTML |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | GREEN |
| `IT-T9-010` | Serbios | T9 | NAO SEI | DISCOVERED | PDF |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | YELLOW |
| `IT-T9-011` | Koppert Biological Syste | T9 | NAO SEI | DISCOVERED | HTML |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | YELLOW |
| `IT-T9-012` | CBC Europe — Biogard | T9 | NAO SEI | DISCOVERED | PDF |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | GREEN |
| `IT-T9-013` | Certis Belchim | T9 | NAO SEI | DISCOVERED | PDF |  | NAO SEI | NAO SEI | **NAO SEI — uma captura so** | não | NAO SEI | MEDIUM | UNKNOWN | GREEN |

---

## SE NÃO COLETARMOS HOJE, O QUE DESAPARECE?

Três fontes são **`FORWARD_ONLY`**: o documento de hoje some quando chega o de amanhã.
Não é detalhe técnico — é risco de perda irreversível.

| fonte | o que se perde | por quê |
|---|---|---|
| `IT-T3-005` Terre dell'Etruria | a edição semanal inteira, com os **139 pontos** e suas coordenadas | o site mostra uma edição por vez; `/bollettini` devolve **404** |
| `IT-T2-002` ARPAV Veneto | o boletim de cada uma das **32 zonas** | nome de arquivo fixo, conteúdo sobrescrito, sem data na URL |
| `IT-T2-004` SIAS Sicília | a janela de 11 dias por estação | URL fixa, janela móvel; há seção de série histórica **não testada** |

**Consequência para a coleta futura:** essas três precisam de cadência **pelo menos igual** à de
publicação delas — senão o dado deixa de existir. As outras dez têm arquivo e podem ser buscadas depois.

---

## Onde o contrato admite que não sabe

- `IT-T3-008` **Puglia** — o nome da cultura é **imagem**, não texto. Pode ser *derivado* da praga
  (`Bactrocera oleae` → olivo), e nesse caso o campo é `CROP_DERIVED`, **nunca** `CROP_EXTRACTED`.
- `IT-T5-002` **FEM OpenPub** — os 188 resultados são o que a **busca casou**: não são 188 evidências
  independentes, nem 188 pesquisadores, nem 188 trabalhos comprovadamente sobre o tema.
- `IT-T9-008` **ADAMA** e `IT-T9-002` **Bayer** — não há caminho honesto para virar `RAW_PRESERVED`
  enquanto o servidor recusar cliente sem navegador. Não forçar.
- **Frequência observada** só foi provada por datas de documento em quatro fontes. Nas demais é
  `NÃO SEI`, mesmo quando o site declara uma cadência — declaração não é medição.

---

## Controles negativos

Um teste que nunca viu vermelho não é teste. `node regras/italy_source_health.mjs --negativos`
corrompe o documento **em memória** (nunca no disco) e exige que a saúde caia para `FAILED`.

```
IT-T2-001  PDF esperado vira HTML de 'Access denied'  (a armadilha do /view do Plone)
IT-T3-010  documento vazio
IT-T3-008  PDF sem nenhum marcador de conteúdo
IT-T4-001  CSV sem a coluna obrigatória
IT-T7-002  planilha sem a coluna CODICE IT
IT-T9-008  extrato de navegador sem data — sem identidade
IT-T3-005  HTML de monitoramento vazio
IT-T1-001  resposta SDMX vazia
```
