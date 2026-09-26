# ÍNDICE DE FONTES — SINTONIA EAME

> **Este ficheiro é gerado.** Não o edite à mão: edite
> [`ATLAS-DE-FONTES-EAME.md`](ATLAS-DE-FONTES-EAME.md) ou
> [`CONTRATOS-DAS-FONTES-EAME.md`](../operacao/CONTRATOS-DAS-FONTES-EAME.md)
> e rode `py system-map/scripts/generate_system_map.py`.

O atlas guarda a ficha inteira de cada fonte. Esta página é só a porta de
entrada: quantas fontes existem, de que países, e quais delas a máquina já
sabe buscar sozinha.

---

## O NÚMERO

| | |
|---|---|
| fichas completas no atlas | **297** |
| dessas, com contrato de busca escrito | **5** |
| palavras de busca medidas no código | **103** em 34 grupos |
| endereços que o código realmente chama | **668** |
| desses, publicados no mapa | **40** (truncados: 628) |

> ### ⚠ O cabeçalho do atlas e as fichas não batem
>
> O cabeçalho do atlas diz **277 fontes registradas**
> (linha 9). Fichas completas, com `SOURCE_ID` válido, há
> **297**. Faltam **-20**.
>
> As fontes que faltam podem existir de verdade — mas sem ficha, ninguém
> consegue saber o que elas têm. Isto não é corrigido automaticamente:
> é decisão de gente escrever as fichas ou acertar o contador.

---

## A ESCADA — o que uma fonte tem de subir

A distância entre os degraus é o trabalho que falta fazer. Subir exige
gente: nenhum degrau se sobe sozinho.

| # | degrau | o que é | quantas | mora em | sobe como |
|---|---|---|---|---|---|
| 1 | **CANDIDATA** | alguem viu que existe. Ninguem abriu ainda. | **267** | `candidatas/FONTES-CANDIDATAS.json` | abrir, olhar o que entrega e guardar um exemplo real |
| 2 | **REGISTADA** | tem ficha no atlas, com exemplo real guardado. | **260** | `docs/fontes/ATLAS-DE-FONTES-EAME.md` | escrever COMO se busca e o que fazer quando quebrar |
| 3 | **CONTRATADA** | tem contrato de busca escrito. | **5** | `docs/operacao/CONTRATOS-DAS-FONTES-EAME.md` | por a busca a correr sozinha, num workflow |
| 4 | **AUTOMATICA** | a maquina vai la sozinha, sem ninguem por perto. | — | `.github/workflows/` | — |

### A porta de entrada

Fonte nova entra por `candidatas/fonte_nova.py` — na mão, ou de dentro de uma coleta
que tropeçou nela. **O que entra é candidata, nunca fonte.**

```bash
py candidatas/fonte_nova.py --tipos          # os tipos aceites
py candidatas/fonte_nova.py --listar         # a fila, agrupada por tipo
py candidatas/fonte_nova.py \
    --tipo BASE_OFICIAL --pais ES --nome "..." --url https://... \
    --para-que "para que serve" --quem-viu voce --onde-viu "onde viu"
```

Hoje há **1199** candidata(s) na fila,
em `candidatas/FONTES-CANDIDATAS.json`.

`--para-que` é obrigatório de propósito: fonte sem uso declarado vira
entulho — daqui a seis meses ninguém sabe por que ela foi anotada.

---

## CONTAS PÚBLICAS, POR PLATAFORMA

Registradas em `data/samples/COMPETITOR-PUBLIC-COMM/CONTAS-V1.json`.
**Estar na lista não é autorização:** só entra na coleta quem tem
identidade PROVADA e é conta local do país.

| plataforma | mapeadas | autorizadas a coletar |
|---|---|---|
| **FACEBOOK** | 17 | 10 |
| **INSTAGRAM** | 7 | 5 |
| **LINKEDIN** | 6 | 0 ⚠ |
| **YOUTUBE** | 14 | 7 |

Total: **44** contas, **22** autorizadas.

---

## A DIFERENÇA QUE IMPORTA

| | |
|---|---|
| **fonte registrada** | alguém abriu, olhou e guardou um exemplo real |
| **fonte com contrato** | a **máquina** sabe ir lá sozinha, sabe o que esperar de volta e o que fazer quando quebrar |

A distância entre as duas é o trabalho que falta fazer. Uma fonte sem
contrato só funciona enquanto a pessoa que a descobriu estiver por perto.

---

## POR PAÍS

### ESPANHA · 34 fontes · 2 com contrato de busca

| id | fonte | assunto | estado | a máquina busca? |
|---|---|---|---|---|
| `ES-T3-001` | Datos de seguimiento de plagas y enfermedades en las estac | T3 · PEST / DISEASE / WEEDS | 🟢 GREEN | sim |
| `ES-T4-001` | Jerarquía de especies vegetales · Clasificación de plagas | T4 · REGULATORY | 🟢 GREEN | **não** |
| `ES-T4-002` | Autorizaciones excepcionales vigentes | T4 · REGULATORY | 🟢 GREEN | **não** |
| `ES-T4-003` | Registro de Productos Fitosanitarios — aplicação de consul | T4 · REGULATORY | ⚪ NAO SEI | **não** |
| `ES-T4-005` | Registro Oficial de Productos Fitosanitarios — rotas públi | T4 · REGULATORY | 🟢 GREEN | sim |
| `ES-T5-002` | OpenAlex, recorte espanhol declarado | T5 · SCIENCE | 🟢 GREEN | **não** |
| `ES-T7-001` | feeds de imprensa técnica espanhola, associações agrárias, | T7 · TECHNICAL NETWORK | ⚪ PARCIAL | **não** |
| `ES-T7-002` | feeds de imprensa técnica espanhola, associações agrárias, | T7 · TECHNICAL NETWORK | ⚪ PARCIAL | **não** |
| `ES-T7-003` | feeds de imprensa técnica espanhola, associações agrárias, | T7 · TECHNICAL NETWORK | ⚪ PARCIAL | **não** |
| `ES-T7-004` | feeds de imprensa técnica espanhola, associações agrárias, | T7 · TECHNICAL NETWORK | ⚪ PARCIAL | **não** |
| `ES-T7-005` | feeds de imprensa técnica espanhola, associações agrárias, | T7 · TECHNICAL NETWORK | ⚪ PARCIAL | **não** |
| `ES-T7-006` | feeds de imprensa técnica espanhola, associações agrárias, | T7 · TECHNICAL NETWORK | ⚪ PARCIAL | **não** |
| `ES-T7-007` | feeds de imprensa técnica espanhola, associações agrárias, | T7 · TECHNICAL NETWORK | ⚪ PARCIAL | **não** |
| `ES-T7-008` | feeds de imprensa técnica espanhola, associações agrárias, | T7 · TECHNICAL NETWORK | ⚪ PARCIAL | **não** |
| `ES-T7-009` | feeds de imprensa técnica espanhola, associações agrárias, | T7 · TECHNICAL NETWORK | ⚪ PARCIAL | **não** |
| `ES-T7-010` | feeds de imprensa técnica espanhola, associações agrárias, | T7 · TECHNICAL NETWORK | ⚪ PARCIAL | **não** |
| `ES-T7-011` | feeds de imprensa técnica espanhola, associações agrárias, | T7 · TECHNICAL NETWORK | ⚪ PARCIAL | **não** |
| `ES-T7-012` | feeds de imprensa técnica espanhola, associações agrárias, | T7 · TECHNICAL NETWORK | ⚪ PARCIAL | **não** |
| `ES-T7-013` | feeds de imprensa técnica espanhola, associações agrárias, | T7 · TECHNICAL NETWORK | ⚪ PARCIAL | **não** |
| `ES-T7-014` | feeds de imprensa técnica espanhola, associações agrárias, | T7 · TECHNICAL NETWORK | ⚪ PARCIAL | **não** |
| `ES-T7-015` | feeds de imprensa técnica espanhola, associações agrárias, | T7 · TECHNICAL NETWORK | ⚪ PARCIAL | **não** |
| `ES-T7-016` | feeds de imprensa técnica espanhola, associações agrárias, | T7 · TECHNICAL NETWORK | ⚪ PARCIAL | **não** |
| `ES-T7-017` | feeds de imprensa técnica espanhola, associações agrárias, | T7 · TECHNICAL NETWORK | ⚪ PARCIAL | **não** |
| `ES-T7-018` | feeds de imprensa técnica espanhola, associações agrárias, | T7 · TECHNICAL NETWORK | ⚪ PARCIAL | **não** |
| `ES-T7-019` | feeds de imprensa técnica espanhola, associações agrárias, | T7 · TECHNICAL NETWORK | ⚪ PARCIAL | **não** |
| `ES-T7-020` | feeds de imprensa técnica espanhola, associações agrárias, | T7 · TECHNICAL NETWORK | ⚪ PARCIAL | **não** |
| `ES-T7-021` | feeds de imprensa técnica espanhola, associações agrárias, | T7 · TECHNICAL NETWORK | ⚪ PARCIAL | **não** |
| `ES-T7-022` | feeds de imprensa técnica espanhola, associações agrárias, | T7 · TECHNICAL NETWORK | ⚪ PARCIAL | **não** |
| `ES-T7-023` | feeds de imprensa técnica espanhola, associações agrárias, | T7 · TECHNICAL NETWORK | ⚪ PARCIAL | **não** |
| `ES-T7-024` | feeds de imprensa técnica espanhola, associações agrárias, | T7 · TECHNICAL NETWORK | ⚪ PARCIAL | **não** |
| `ES-T7-025` | feeds de imprensa técnica espanhola, associações agrárias, | T7 · TECHNICAL NETWORK | ⚪ PARCIAL | **não** |
| `ES-T7-026` | feeds de imprensa técnica espanhola, associações agrárias, | T7 · TECHNICAL NETWORK | ⚪ PARCIAL | **não** |
| `ES-T7-027` | feeds de imprensa técnica espanhola, associações agrárias, | T7 · TECHNICAL NETWORK | ⚪ PARCIAL | **não** |
| `ES-T9-001` | páginas de atualidades de BASF, Bayer, Syngenta, Corteva… | T9 · COMPETITORS | ⚪ NAO SEI | **não** |

### EUROPA · 13 fontes · 1 com contrato de busca

| id | fonte | assunto | estado | a máquina busca? |
|---|---|---|---|---|
| `EU-T1-001` | Crop production in EU standard humidity by NUTS 2 region | T1 · CROP & PRODUCTION | 🟢 GREEN | **não** |
| `EU-T1-002` | Crop production in EU standard humidity | T1 · CROP & PRODUCTION | 🟢 GREEN | **não** |
| `EU-T10-001` | European Commission — Agri-food Data Portal (cereal prices | T10 · MARKET / TRADE / INDUSTRY | 🟢 GREEN | **não** |
| `EU-T12-001` | CELLAR / EU Publications Office — camada de política agríc | T12 · POLICY / AGRICULTURAL ENVIRONMENT | 🟢 GREEN | **não** |
| `EU-T2-001` | NASA POWER — Daily Point (community AG) | T2 · CLIMATE / WATER / SOIL | 🟢 GREEN | **não** |
| `EU-T2-002` | NUTS_LB_2024_4326_LEVL_2 (label points) | T2 · CLIMATE / WATER / SOIL | 🟢 GREEN | **não** |
| `EU-T2-003` | Open-Meteo Historical Weather API (ERA5) | T2 · CLIMATE / WATER / SOIL | ⚪ NAO SEI | **não** |
| `EU-T3-001` | EPPO Global Database | T3 · PEST / DISEASE / WEEDS | ⚪ NAO SEI | **não** |
| `EU-T4-001` | CELLAR / EU Publications Office (Official Journal of the E | T4 · REGULATORY | 🟢 GREEN | sim |
| `EU-T4-002` | EU Pesticides Database | T4 · REGULATORY | ⚪ NAO SEI | **não** |
| `EU-T5-001` | OpenAlex | T5 · SCIENCE | 🟢 GREEN | **não** |
| `EU-T8-001` | EU-T8-001 | T8 · FARMERS & INFLUENCERS | ⚪ NAO SEI | **não** |
| `EU-T9-002` | Meta Ads Library | T9 · COMPETITORS | ⚪ NAO SEI | **não** |

### FRANCA · 6 fontes · 1 com contrato de busca

| id | fonte | assunto | estado | a máquina busca? |
|---|---|---|---|---|
| `FR-T11-001` | FR-T11-001 | T11 · EVENTS | 🟡 YELLOW | **não** |
| `FR-T13-001` | recherche-entreprises.api.gouv.fr (base SIRENE) | T13 · DISTRIBUTION | 🟢 GREEN | **não** |
| `FR-T3-001` | Bulletins de Santé du Végétal | T3 · PEST / DISEASE / WEEDS | 🟡 YELLOW | **não** |
| `FR-T3-002` | Archive en agro-écologie de BSV | T3 · PEST / DISEASE / WEEDS | ⚪ NAO SEI | **não** |
| `FR-T4-001` | Données ouvertes du catalogue E-Phy | T4 · REGULATORY | 🟢 GREEN | sim |
| `FR-T9-001` | páginas de atualidades de BASF, Bayer, Syngenta, Corteva… | T9 · COMPETITORS | ⚪ NAO SEI | **não** |

### ITALIA · 244 fontes · 1 com contrato de busca

| id | fonte | assunto | estado | a máquina busca? |
|---|---|---|---|---|
| `IT-T1-002` | Provincia autonoma di Trento — Agricoltura | T1 · CROP & PRODUCTION | 🟢 GREEN | **não** |
| `IT-T1-003` | Regione Toscana — Agricoltura | T1 · CROP & PRODUCTION | 🟢 GREEN | **não** |
| `IT-T1-004` | Liguria — Regione Liguria agricoltura | T1 · CROP & PRODUCTION | 🟡 YELLOW | **não** |
| `IT-T1-005` | Umbria — Agricoltura e foreste | T1 · CROP & PRODUCTION | 🟡 YELLOW | **não** |
| `IT-T1-006` | ARSAC Calabria — Azienda Regionale per lo Sviluppo dell'Ag | T1 · CROP & PRODUCTION | 🟢 GREEN | **não** |
| `IT-T1-007` | ARSIAL — Agenzia Regionale Sviluppo Innovazione Agricoltur | T1 · CROP & PRODUCTION | 🟢 GREEN | **não** |
| `IT-T1-008` | Agricoltura Regione Lombardia | T1 · CROP & PRODUCTION | 🟢 GREEN | **não** |
| `IT-T1-009` | Lazio — Agricoltura Regione Lazio | T1 · CROP & PRODUCTION | 🟢 GREEN | **não** |
| `IT-T1-010` | Regione Abruzzo — Agricoltura | T1 · CROP & PRODUCTION | 🟢 GREEN | **não** |
| `IT-T1-011` | Regione Umbria — Agricoltura | T1 · CROP & PRODUCTION | 🟢 GREEN | **não** |
| `IT-T1-012` | Regione Valle d'Aosta — Agricoltura | T1 · CROP & PRODUCTION | 🟢 GREEN | **não** |
| `IT-T1-013` | Assosementi | T1 · CROP & PRODUCTION | 🟢 GREEN | **não** |
| `IT-T1-014` | Ente Nazionale Risi | T1 · CROP & PRODUCTION | 🟡 YELLOW | **não** |
| `IT-T1-015` | Terra e Vita — Edagricole | T1 · CROP & PRODUCTION | 🟢 GREEN | **não** |
| `IT-T1-016` | Italia Olivicola | T1 · CROP & PRODUCTION | 🟢 GREEN | **não** |
| `IT-T1-017` | Olivo e Olio — Edagricole | T1 · CROP & PRODUCTION | 🟢 GREEN | **não** |
| `IT-T1-018` | Rivista di Agraria | T1 · CROP & PRODUCTION | 🟢 GREEN | **não** |
| `IT-T1-019` | SIA — Societa Italiana di Agronomia | T1 · CROP & PRODUCTION | 🟢 GREEN | **não** |
| `IT-T1-020` | Agriligurianet — Regione Liguria agricoltura | T1 · CROP & PRODUCTION | 🟢 GREEN | **não** |
| `IT-T1-021` | AgroNotizie — Image Line | T1 · CROP & PRODUCTION | 🟡 YELLOW | **não** |
| `IT-T1-022` | OlivoNews — giornale di olivicoltura | T1 · CROP & PRODUCTION | 🟢 GREEN | **não** |
| `IT-T1-023` | SOI — Societa di Ortoflorofrutticoltura Italiana | T1 · CROP & PRODUCTION | 🟡 YELLOW | **não** |
| `IT-T10-002` | BMTI — analisi di mercato cereali | T10 · MARKET / TRADE / INDUSTRY | 🟢 GREEN | **não** |
| `IT-T10-006` | Agrisole — quotidiano agricolo del Sole 24 Ore | T10 · MARKET / TRADE / INDUSTRY | 🟢 GREEN | **não** |
| `IT-T10-007` | ISMEA — Istituto di Servizi per il Mercato Agricolo Alimen | T10 · MARKET / TRADE / INDUSTRY | 🟢 GREEN | **não** |
| `IT-T10-008` | Italmopa — Associazione Industriali Mugnai d'Italia | T10 · MARKET / TRADE / INDUSTRY | 🟢 GREEN | **não** |
| `IT-T10-009` | Borsa Merci Bologna — Camera di Commercio | T10 · MARKET / TRADE / INDUSTRY | 🟢 GREEN | **não** |
| `IT-T10-010` | CSO Italy — Centro Servizi Ortofrutticoli | T10 · MARKET / TRADE / INDUSTRY | 🟢 GREEN | **não** |
| `IT-T10-011` | Ruminantia — web magazine dei ruminanti | T10 · MARKET / TRADE / INDUSTRY | 🟢 GREEN | **não** |
| `IT-T10-012` | Consorzio Tutela Vini d'Abruzzo | T10 · MARKET / TRADE / INDUSTRY | 🟢 GREEN | **não** |
| `IT-T10-013` | Consorzio di Tutela Arancia Rossa di Sicilia IGP | T10 · MARKET / TRADE / INDUSTRY | 🟢 GREEN | **não** |
| `IT-T10-014` | Consorzio di Tutela del Grana Padano | T10 · MARKET / TRADE / INDUSTRY | 🟢 GREEN | **não** |
| `IT-T10-015` | Consorzio Tutela Prosecco DOC | T10 · MARKET / TRADE / INDUSTRY | 🟡 YELLOW | **não** |
| `IT-T10-016` | Alleanza delle Cooperative Italiane Agroalimentare | T10 · MARKET / TRADE / INDUSTRY | 🟢 GREEN | **não** |
| `IT-T10-017` | Myfruit.it — Youtube ufficiale | T10 · MARKET / TRADE / INDUSTRY | 🟢 GREEN | **não** |
| `IT-T10-018` | Myfruit.it | T10 · MARKET / TRADE / INDUSTRY | 🟢 GREEN | **não** |
| `IT-T10-019` | WineNews — Youtube ufficiale | T10 · MARKET / TRADE / INDUSTRY | 🟢 GREEN | **não** |
| `IT-T10-020` | WineNews | T10 · MARKET / TRADE / INDUSTRY | 🟢 GREEN | **não** |
| `IT-T10-021` | Plantgest — banca dati varieta | T10 · MARKET / TRADE / INDUSTRY | 🟢 GREEN | **não** |
| `IT-T10-022` | Zootecnica International | T10 · MARKET / TRADE / INDUSTRY | 🟢 GREEN | **não** |
| `IT-T11-001` | IT-T11-001 | T11 · EVENTS | 🟡 YELLOW | **não** |
| `IT-T11-005` | SIMEI — Salone Internazionale Macchine per Enologia e Imbo | T11 · EVENTS | 🟢 GREEN | **não** |
| `IT-T11-006` | Macfrut — Youtube ufficiale | T11 · EVENTS | 🟢 GREEN | **não** |
| `IT-T11-007` | Agrilevante — Youtube ufficiale | T11 · EVENTS | 🟢 GREEN | **não** |
| `IT-T12-003` | CIA — Agricoltori Italiani | T12 · POLICY / AGRICULTURAL ENVIRONMENT | 🟡 YELLOW | **não** |
| `IT-T12-004` | Confagricoltura | T12 · POLICY / AGRICULTURAL ENVIRONMENT | 🟡 YELLOW | **não** |
| `IT-T12-005` | AIAB — Associazione Italiana Agricoltura Biologica | T12 · POLICY / AGRICULTURAL ENVIRONMENT | 🟢 GREEN | **não** |
| `IT-T12-006` | CIA Toscana | T12 · POLICY / AGRICULTURAL ENVIRONMENT | 🟢 GREEN | **não** |
| `IT-T12-007` | ARSAC Calabria — Azienda Regionale per lo Sviluppo dell'Ag | T12 · POLICY / AGRICULTURAL ENVIRONMENT | 🟢 GREEN | **não** |
| `IT-T12-008` | ASSAM Marche — Agenzia Servizi Settore Agroalimentare dell | T12 · POLICY / AGRICULTURAL ENVIRONMENT | 🟢 GREEN | **não** |
| `IT-T12-009` | ASSAM Marche — Agenzia Servizi Settore Agroalimentare dell | T12 · POLICY / AGRICULTURAL ENVIRONMENT | 🟢 GREEN | **não** |
| `IT-T12-010` | Regione Molise — Agricoltura — Youtube ufficiale | T12 · POLICY / AGRICULTURAL ENVIRONMENT | 🟢 GREEN | **não** |
| `IT-T12-011` | Pianeta PSR — Youtube ufficiale | T12 · POLICY / AGRICULTURAL ENVIRONMENT | 🟢 GREEN | **não** |
| `IT-T12-012` | Regione Piemonte — Agricoltura e cibo — Youtube ufficiale | T12 · POLICY / AGRICULTURAL ENVIRONMENT | 🟢 GREEN | **não** |
| `IT-T12-013` | Regione Piemonte — Agricoltura e cibo | T12 · POLICY / AGRICULTURAL ENVIRONMENT | 🟢 GREEN | **não** |
| `IT-T12-014` | Regione Toscana — Agricoltura — Youtube ufficiale | T12 · POLICY / AGRICULTURAL ENVIRONMENT | 🟢 GREEN | **não** |
| `IT-T12-015` | APPA Trento — Agenzia provinciale protezione ambiente — Yo | T12 · POLICY / AGRICULTURAL ENVIRONMENT | 🟢 GREEN | **não** |
| `IT-T12-016` | Regione Valle d'Aosta — Agricoltura — Youtube ufficiale | T12 · POLICY / AGRICULTURAL ENVIRONMENT | 🟢 GREEN | **não** |
| `IT-T12-017` | ERSA FVG — Agenzia regionale per lo sviluppo rurale | T12 · POLICY / AGRICULTURAL ENVIRONMENT | 🟢 GREEN | **não** |
| `IT-T2-001` | ARPAE — Bollettino agrometeorologico regionale | T2 · CLIMATE / WATER / SOIL | 🟢 GREEN | **não** |
| `IT-T2-002` | ARPAV — Agrometeo / Agrometeo Informa / bollettini zonali | T2 · CLIMATE / WATER / SOIL | 🟢 GREEN | **não** |
| `IT-T2-004` | SIAS Sicilia — agrometeorologia regional | T2 · CLIMATE / WATER / SOIL | 🟢 GREEN | **não** |
| `IT-T2-006` | ARPA Campania | T2 · CLIMATE / WATER / SOIL | 🟢 GREEN | **não** |
| `IT-T2-007` | ARPA Sicilia | T2 · CLIMATE / WATER / SOIL | 🟢 GREEN | **não** |
| `IT-T2-008` | ARPAT Toscana | T2 · CLIMATE / WATER / SOIL | 🟢 GREEN | **não** |
| `IT-T2-009` | ISPRA — Istituto Superiore per la Protezione e la Ricerca  | T2 · CLIMATE / WATER / SOIL | 🟢 GREEN | **não** |
| `IT-T2-010` | APPA Trento — Agenzia provinciale protezione ambiente | T2 · CLIMATE / WATER / SOIL | 🟡 YELLOW | **não** |
| `IT-T2-011` | ARPA Lombardia | T2 · CLIMATE / WATER / SOIL | 🟡 YELLOW | **não** |
| `IT-T2-012` | ARPA Friuli Venezia Giulia — OSMER | T2 · CLIMATE / WATER / SOIL | 🟢 GREEN | **não** |
| `IT-T2-013` | ARPA Lazio | T2 · CLIMATE / WATER / SOIL | 🟢 GREEN | **não** |
| `IT-T2-014` | ARPA Molise | T2 · CLIMATE / WATER / SOIL | 🟡 YELLOW | **não** |
| `IT-T2-015` | AIAM — Associazione Italiana di Agrometeorologia | T2 · CLIMATE / WATER / SOIL | 🟢 GREEN | **não** |
| `IT-T2-016` | ARPA Marche | T2 · CLIMATE / WATER / SOIL | 🟢 GREEN | **não** |
| `IT-T2-017` | CNR IRET — Istituto di Ricerca sugli Ecosistemi Terrestri | T2 · CLIMATE / WATER / SOIL | 🟢 GREEN | **não** |
| `IT-T2-018` | CNR ISAFOM — Istituto per i Sistemi Agricoli e Forestali d | T2 · CLIMATE / WATER / SOIL | 🟢 GREEN | **não** |
| `IT-T2-019` | ARPA Piemonte | T2 · CLIMATE / WATER / SOIL | 🟡 YELLOW | **não** |
| `IT-T2-020` | ARTA Abruzzo | T2 · CLIMATE / WATER / SOIL | 🟡 YELLOW | **não** |
| `IT-T2-021` | ARPA Liguria | T2 · CLIMATE / WATER / SOIL | 🟡 YELLOW | **não** |
| `IT-T2-022` | ARPA Valle d'Aosta | T2 · CLIMATE / WATER / SOIL | 🟡 YELLOW | **não** |
| `IT-T2-023` | ARPA Basilicata | T2 · CLIMATE / WATER / SOIL | 🟢 GREEN | **não** |
| `IT-T2-024` | ANBI — Associazione Nazionale Consorzi di gestione e tutel | T2 · CLIMATE / WATER / SOIL | 🟢 GREEN | **não** |
| `IT-T2-025` | ARPA Lazio — Youtube ufficiale | T2 · CLIMATE / WATER / SOIL | 🟢 GREEN | **não** |
| `IT-T2-026` | ARPA Liguria — Youtube ufficiale | T2 · CLIMATE / WATER / SOIL | 🟢 GREEN | **não** |
| `IT-T2-027` | ARPA Lombardia — Youtube ufficiale | T2 · CLIMATE / WATER / SOIL | 🟢 GREEN | **não** |
| `IT-T2-028` | ARPA Marche — Youtube ufficiale | T2 · CLIMATE / WATER / SOIL | 🟢 GREEN | **não** |
| `IT-T2-029` | ARPA Puglia | T2 · CLIMATE / WATER / SOIL | 🟢 GREEN | **não** |
| `IT-T2-030` | Nomisma | T2 · CLIMATE / WATER / SOIL | 🟢 GREEN | **não** |
| `IT-T3-001` | IT-T3-001 | T3 · PEST / DISEASE / WEEDS | 🟡 YELLOW | **não** |
| `IT-T3-002` | Campania — Bollettini fitosanitari regionali | T3 · PEST / DISEASE / WEEDS | 🟢 GREEN | **não** |
| `IT-T3-008` | ARIF Puglia / Agrometeo Puglia — rete fitosanitaria | T3 · PEST / DISEASE / WEEDS | 🟢 GREEN | **não** |
| `IT-T3-010` | APOL Lecce — monitoraggio olivicolo | T3 · PEST / DISEASE / WEEDS | 🟢 GREEN | **não** |
| `IT-T3-011` | AGRIOS — direttive, aggiornamenti e deroghe per la produzi | T3 · PEST / DISEASE / WEEDS | 🟢 GREEN | **não** |
| `IT-T3-013` | Emilia-Romagna — Servizio Fitosanitario | T3 · PEST / DISEASE / WEEDS | 🟡 YELLOW | **não** |
| `IT-T3-014` | Servizio Fitosanitario Nazionale — Protezione delle Piante | T3 · PEST / DISEASE / WEEDS | 🟢 GREEN | **não** |
| `IT-T3-015` | Toscana — Servizio Fitosanitario Regionale | T3 · PEST / DISEASE / WEEDS | 🟢 GREEN | **não** |
| `IT-T3-016` | Veneto — Servizio Fitosanitario Regionale | T3 · PEST / DISEASE / WEEDS | 🟢 GREEN | **não** |
| `IT-T3-017` | CNR IPSP — Istituto per la Protezione Sostenibile delle Pi | T3 · PEST / DISEASE / WEEDS | 🟡 YELLOW | **não** |
| `IT-T3-018` | CNR ISPA — Istituto di Scienze delle Produzioni Alimentari | T3 · PEST / DISEASE / WEEDS | 🟡 YELLOW | **não** |
| `IT-T3-019` | Agroinnova — Centro di Competenza per l'Innovazione in cam | T3 · PEST / DISEASE / WEEDS | 🟡 YELLOW | **não** |
| `IT-T3-020` | Societa Entomologica Italiana | T3 · PEST / DISEASE / WEEDS | 🟢 GREEN | **não** |
| `IT-T3-021` | SIPaV — Societa Italiana di Patologia Vegetale | T3 · PEST / DISEASE / WEEDS | 🟡 YELLOW | **não** |
| `IT-T4-001` | Fitosanitari — elenco dei prodotti fitosanitari autorizzat | T4 · REGULATORY | 🟢 GREEN | sim |
| `IT-T5-002` | FEM OpenPub — repositório de publicações | T5 · SCIENCE | 🟢 GREEN | **não** |
| `IT-T5-003` | Bilanci fitosanitari regionali 2024-2025 — ciclo «I Gioved | T5 · SCIENCE | 🟢 GREEN | **não** |
| `IT-T5-006` | CNR — Consiglio Nazionale delle Ricerche | T5 · SCIENCE | 🟢 GREEN | **não** |
| `IT-T5-007` | Institut Agricole Regional — Aosta | T5 · SCIENCE | 🟢 GREEN | **não** |
| `IT-T5-008` | Fondazione Agrion — Fondazione per la ricerca l'innovazion | T5 · SCIENCE | 🟡 YELLOW | **não** |
| `IT-T5-009` | Fondazione Minoprio | T5 · SCIENCE | 🟢 GREEN | **não** |
| `IT-T5-010` | Fondazione per l'Agricoltura F.lli Navarra | T5 · SCIENCE | 🟢 GREEN | **não** |
| `IT-T5-011` | UNIBA DiSSPA — Dipartimento di Scienze del Suolo della Pia | T5 · SCIENCE | 🟢 GREEN | **não** |
| `IT-T5-012` | UNIPI DiSAAA-a — Dipartimento di Scienze Agrarie Alimentar | T5 · SCIENCE | 🟢 GREEN | **não** |
| `IT-T5-013` | CRPA — Centro Ricerche Produzioni Animali | T5 · SCIENCE | 🟡 YELLOW | **não** |
| `IT-T5-014` | UNITUS DAFNE — Dipartimento di Scienze Agrarie e Forestali | T5 · SCIENCE | 🟡 YELLOW | **não** |
| `IT-T5-015` | CNR IBBR — Istituto di Bioscienze e Biorisorse | T5 · SCIENCE | 🟢 GREEN | **não** |
| `IT-T5-016` | AIR UNIMI — Archivio Istituzionale della Ricerca | T5 · SCIENCE | 🟡 YELLOW | **não** |
| `IT-T5-017` | FLORE UNIFI — Archivio istituzionale della ricerca | T5 · SCIENCE | 🟡 YELLOW | **não** |
| `IT-T5-018` | IRIS UNIBO — Archivio istituzionale della ricerca | T5 · SCIENCE | 🟡 YELLOW | **não** |
| `IT-T5-019` | IRIS UNIPD — Archivio della ricerca | T5 · SCIENCE | 🟡 YELLOW | **não** |
| `IT-T5-020` | IRIS UNITO — Archivio istituzionale | T5 · SCIENCE | 🟡 YELLOW | **não** |
| `IT-T5-021` | UNIFI DAGRI — Dipartimento di Scienze e Tecnologie Agrarie | T5 · SCIENCE | 🟡 YELLOW | **não** |
| `IT-T5-022` | Advances in Horticultural Science | T5 · SCIENCE | 🟢 GREEN | **não** |
| `IT-T5-023` | SSICA — Stazione Sperimentale per l'Industria delle Conser | T5 · SCIENCE | 🟢 GREEN | **não** |
| `IT-T5-024` | UNIMI DiSAA — Dipartimento di Scienze Agrarie e Ambientali | T5 · SCIENCE | 🟢 GREEN | **não** |
| `IT-T5-025` | Scuola Superiore Sant'Anna — Istituto di Scienze delle Pro | T5 · SCIENCE | 🟡 YELLOW | **não** |
| `IT-T5-026` | UNIPA SAAF — Dipartimento Scienze Agrarie Alimentari e For | T5 · SCIENCE | 🟡 YELLOW | **não** |
| `IT-T5-027` | UNIPD DAFNAE — Dipartimento di Agronomia Animali Alimenti  | T5 · SCIENCE | 🟡 YELLOW | **não** |
| `IT-T5-028` | UNIUD DI4A — Dipartimento di Scienze Agroalimentari Ambien | T5 · SCIENCE | 🟡 YELLOW | **não** |
| `IT-T5-029` | UNIVR Dipartimento di Biotecnologie | T5 · SCIENCE | 🟡 YELLOW | **não** |
| `IT-T5-030` | UNITE Facolta di Bioscienze e Tecnologie Agro-alimentari e | T5 · SCIENCE | 🟢 GREEN | **não** |
| `IT-T5-031` | UNIVPM D3A — Dipartimento di Scienze Agrarie Alimentari e  | T5 · SCIENCE | 🟢 GREEN | **não** |
| `IT-T5-032` | UNIPG DSA3 — Dipartimento di Scienze Agrarie Alimentari e  | T5 · SCIENCE | 🟡 YELLOW | **não** |
| `IT-T5-033` | UNIBO DISTAL — Dipartimento di Scienze e Tecnologie Agro-A | T5 · SCIENCE | 🟢 GREEN | **não** |
| `IT-T5-034` | Accademia dei Georgofili | T5 · SCIENCE | 🟢 GREEN | **não** |
| `IT-T5-035` | Georgofili INFO — notiziario | T5 · SCIENCE | 🟡 YELLOW | **não** |
| `IT-T5-036` | Georgofili — Accademia dei Georgofili (portale .net) | T5 · SCIENCE | 🟡 YELLOW | **não** |
| `IT-T5-037` | CNR ISAFOM — Istituto per i Sistemi Agricoli e Forestali d | T5 · SCIENCE | 🟢 GREEN | **não** |
| `IT-T5-038` | UNINA Dipartimento di Agraria — Portici — Youtube ufficial | T5 · SCIENCE | 🟢 GREEN | **não** |
| `IT-T5-039` | UNINA Dipartimento di Agraria — Portici | T5 · SCIENCE | 🟢 GREEN | **não** |
| `IT-T5-040` | CRPV — Centro Ricerche Produzioni Vegetali — Youtube uffic | T5 · SCIENCE | 🟢 GREEN | **não** |
| `IT-T5-041` | CRPV — Centro Ricerche Produzioni Vegetali | T5 · SCIENCE | 🟢 GREEN | **não** |
| `IT-T5-042` | Fondazione per l'Agricoltura F.lli Navarra — Youtube uffic | T5 · SCIENCE | 🟢 GREEN | **não** |
| `IT-T5-043` | UNIBO DISTAL — Dipartimento di Scienze e Tecnologie Agro-A | T5 · SCIENCE | 🟢 GREEN | **não** |
| `IT-T5-044` | Fondazione Minoprio — Youtube ufficiale | T5 · SCIENCE | 🟢 GREEN | **não** |
| `IT-T5-045` | ISPRA — Istituto Superiore per la Protezione e la Ricerca  | T5 · SCIENCE | 🟢 GREEN | **não** |
| `IT-T5-046` | Olio Officina | T5 · SCIENCE | 🟢 GREEN | **não** |
| `IT-T5-047` | UNIBA DiSSPA — Dipartimento di Scienze del Suolo della Pia | T5 · SCIENCE | 🟢 GREEN | **não** |
| `IT-T5-048` | UNICT Di3A — Dipartimento di Agricoltura Alimentazione e A | T5 · SCIENCE | 🟢 GREEN | **não** |
| `IT-T5-049` | UNICT Di3A — Dipartimento di Agricoltura Alimentazione e A | T5 · SCIENCE | 🟢 GREEN | **não** |
| `IT-T5-050` | Libera Universita di Bolzano — Facolta di Scienze agrarie  | T5 · SCIENCE | 🟢 GREEN | **não** |
| `IT-T5-051` | UNIRC Dipartimento di Agraria | T5 · SCIENCE | 🟢 GREEN | **não** |
| `IT-T5-052` | Bulletin of Insectology | T5 · SCIENCE | 🟢 GREEN | **não** |
| `IT-T5-053` | Phytopathologia Mediterranea | T5 · SCIENCE | 🟢 GREEN | **não** |
| `IT-T5-054` | Legacoop Agroalimentare | T5 · SCIENCE | 🟢 GREEN | **não** |
| `IT-T6-001` | Andrea Lentini — registo cientifico ORCID (Università degl | T6 · RESEARCHERS | 🟡 YELLOW | **não** |
| `IT-T6-002` | Anita Nencioni — registo cientifico ORCID (Consiglio per l | T6 · RESEARCHERS | 🟡 YELLOW | **não** |
| `IT-T6-003` | Anna Aldrighetti — registo cientifico ORCID (University of | T6 · RESEARCHERS | 🟡 YELLOW | **não** |
| `IT-T6-004` | Antonio Masetti — registo cientifico ORCID (University of  | T6 · RESEARCHERS | 🟡 YELLOW | **não** |
| `IT-T6-005` | Antonio Pietro GARONNA — registo cientifico ORCID (Univers | T6 · RESEARCHERS | 🟡 YELLOW | **não** |
| `IT-T6-006` | Antonio Prodi — registo cientifico ORCID (University of Bo | T6 · RESEARCHERS | 🟡 YELLOW | **não** |
| `IT-T6-007` | Aparna S Balan — registo cientifico ORCID (University of P | T6 · RESEARCHERS | 🟡 YELLOW | **não** |
| `IT-T6-008` | CLAUDIO RATTI — registo cientifico ORCID (Alma Mater Studi | T6 · RESEARCHERS | 🟡 YELLOW | **não** |
| `IT-T6-009` | Chiara D'ERRICO — registo cientifico ORCID (Istituto per l | T6 · RESEARCHERS | 🟡 YELLOW | **não** |
| `IT-T6-010` | Daniele Daffonchio — registo cientifico ORCID (University  | T6 · RESEARCHERS | 🟡 YELLOW | **não** |
| `IT-T6-011` | Dumitru Scutelnic — registo cientifico ORCID (University o | T6 · RESEARCHERS | 🟡 YELLOW | **não** |
| `IT-T6-012` | Emilio Balducci — registo cientifico ORCID (University of  | T6 · RESEARCHERS | 🟡 YELLOW | **não** |
| `IT-T6-013` | Francesco Nardi — registo cientifico ORCID (University of  | T6 · RESEARCHERS | 🟡 YELLOW | **não** |
| `IT-T6-014` | Gerardo Puopolo — registo cientifico ORCID (University of  | T6 · RESEARCHERS | 🟡 YELLOW | **não** |
| `IT-T6-015` | Gianfranco ANFORA — registo cientifico ORCID (University o | T6 · RESEARCHERS | 🟡 YELLOW | **não** |
| `IT-T6-016` | Giulia Mandalà — registo cientifico ORCID (Verona Universi | T6 · RESEARCHERS | 🟡 YELLOW | **não** |
| `IT-T6-017` | Graziella Amendola — registo cientifico ORCID (National In | T6 · RESEARCHERS | 🟡 YELLOW | **não** |
| `IT-T6-018` | Leonardo Caproni — registo cientifico ORCID (Scuola Superi | T6 · RESEARCHERS | 🟡 YELLOW | **não** |
| `IT-T6-019` | Leonardo Cera — registo cientifico ORCID (University of Pa | T6 · RESEARCHERS | 🟡 YELLOW | **não** |
| `IT-T6-020` | Lorenzo Baglieri — registo cientifico ORCID (Politecnico d | T6 · RESEARCHERS | 🟡 YELLOW | **não** |
| `IT-T6-021` | Luca Finetti — registo cientifico ORCID (University of Fer | T6 · RESEARCHERS | 🟡 YELLOW | **não** |
| `IT-T6-022` | Luca Mazzon — registo cientifico ORCID (Università degli S | T6 · RESEARCHERS | 🟡 YELLOW | **não** |
| `IT-T6-023` | Marco Mancini — registo cientifico ORCID (University of Fl | T6 · RESEARCHERS | 🟡 YELLOW | **não** |
| `IT-T6-024` | Marco Perfetto — registo cientifico ORCID (University of M | T6 · RESEARCHERS | 🟡 YELLOW | **não** |
| `IT-T6-025` | Marwa Mourou — registo cientifico ORCID (Università degli  | T6 · RESEARCHERS | 🟡 YELLOW | **não** |
| `IT-T6-026` | Paolo Boccacci — registo cientifico ORCID (Consiglio Nazio | T6 · RESEARCHERS | 🟡 YELLOW | **não** |
| `IT-T6-027` | Paolo Grazieschi — registo cientifico ORCID (Fondazione Br | T6 · RESEARCHERS | 🟡 YELLOW | **não** |
| `IT-T6-028` | ROBERTO RIZZO — registo cientifico ORCID (CREA - Research  | T6 · RESEARCHERS | 🟡 YELLOW | **não** |
| `IT-T6-029` | Roberta Maria Gravagno — registo cientifico ORCID (Univers | T6 · RESEARCHERS | 🟡 YELLOW | **não** |
| `IT-T6-030` | Roberta Paris — registo cientifico ORCID (Council for Agri | T6 · RESEARCHERS | 🟡 YELLOW | **não** |
| `IT-T6-031` | Roberto Ferrise — registo cientifico ORCID (University of  | T6 · RESEARCHERS | 🟡 YELLOW | **não** |
| `IT-T6-032` | Rosa Francaviglia — registo cientifico ORCID (Consiglio pe | T6 · RESEARCHERS | 🟡 YELLOW | **não** |
| `IT-T6-033` | Stefano Maini — registo cientifico ORCID (Alma Mater Studi | T6 · RESEARCHERS | 🟡 YELLOW | **não** |
| `IT-T6-034` | Tito Caffi — registo cientifico ORCID (Università Cattolic | T6 · RESEARCHERS | 🟡 YELLOW | **não** |
| `IT-T6-035` | Vera Pavese — registo cientifico ORCID (University of Turi | T6 · RESEARCHERS | 🟡 YELLOW | **não** |
| `IT-T6-036` | sara ruschioni — registo cientifico ORCID (Marche Polytech | T6 · RESEARCHERS | 🟡 YELLOW | **não** |
| `IT-T7-002` | MASAF — elenco delle OP e AOP riconosciute | T7 · TECHNICAL NETWORK | 🟢 GREEN | **não** |
| `IT-T7-013` | CONAF — Consiglio Ordine Nazionale Dottori Agronomi e Fore | T7 · TECHNICAL NETWORK | 🟢 GREEN | **não** |
| `IT-T7-014` | Consorzi Agrari d'Italia — CAI | T7 · TECHNICAL NETWORK | 🟡 YELLOW | **não** |
| `IT-T7-015` | Consorzio Tutela Vini d'Abruzzo — Youtube ufficiale | T7 · TECHNICAL NETWORK | 🟢 GREEN | **não** |
| `IT-T7-016` | Cantina Sociale Cooperativa Riunite e CIV — Youtube uffici | T7 · TECHNICAL NETWORK | 🟢 GREEN | **não** |
| `IT-T7-017` | Cantina Sociale Cooperativa Riunite e CIV | T7 · TECHNICAL NETWORK | 🟢 GREEN | **não** |
| `IT-T7-018` | Confagricoltura Lombardia — Youtube ufficiale | T7 · TECHNICAL NETWORK | 🟢 GREEN | **não** |
| `IT-T7-019` | Confagricoltura Lombardia | T7 · TECHNICAL NETWORK | 🟢 GREEN | **não** |
| `IT-T7-020` | Consorzio di Bonifica Est Ticino Villoresi — Youtube uffic | T7 · TECHNICAL NETWORK | 🟢 GREEN | **não** |
| `IT-T7-021` | Consorzio di Bonifica Est Ticino Villoresi | T7 · TECHNICAL NETWORK | 🟢 GREEN | **não** |
| `IT-T7-022` | Consorzio di Tutela del Grana Padano — Youtube ufficiale | T7 · TECHNICAL NETWORK | 🟢 GREEN | **não** |
| `IT-T7-023` | ANBI — Associazione Nazionale Consorzi di gestione e tutel | T7 · TECHNICAL NETWORK | 🟢 GREEN | **não** |
| `IT-T7-024` | Assosementi — Youtube ufficiale | T7 · TECHNICAL NETWORK | 🟢 GREEN | **não** |
| `IT-T7-025` | CIA — Agricoltori Italiani — Youtube ufficiale | T7 · TECHNICAL NETWORK | 🟢 GREEN | **não** |
| `IT-T7-026` | CONAF — Consiglio Ordine Nazionale Dottori Agronomi e Fore | T7 · TECHNICAL NETWORK | 🟢 GREEN | **não** |
| `IT-T7-027` | Coldiretti — Youtube ufficiale | T7 · TECHNICAL NETWORK | 🟢 GREEN | **não** |
| `IT-T7-028` | Confcooperative Fedagripesca — Youtube ufficiale | T7 · TECHNICAL NETWORK | 🟢 GREEN | **não** |
| `IT-T7-029` | Confcooperative Fedagripesca | T7 · TECHNICAL NETWORK | 🟢 GREEN | **não** |
| `IT-T7-030` | FederBio — Youtube ufficiale | T7 · TECHNICAL NETWORK | 🟢 GREEN | **não** |
| `IT-T7-031` | FederBio | T7 · TECHNICAL NETWORK | 🟢 GREEN | **não** |
| `IT-T7-032` | Consorzio Vino Chianti Classico — Youtube ufficiale | T7 · TECHNICAL NETWORK | 🟢 GREEN | **não** |
| `IT-T7-033` | Consorzio Vino Chianti Classico | T7 · TECHNICAL NETWORK | 🟢 GREEN | **não** |
| `IT-T7-034` | Consorzio del Vino Brunello di Montalcino — Youtube uffici | T7 · TECHNICAL NETWORK | 🟢 GREEN | **não** |
| `IT-T7-035` | Georgofili INFO — notiziario — Youtube ufficiale | T7 · TECHNICAL NETWORK | 🟢 GREEN | **não** |
| `IT-T7-036` | Consorzio Tutela Prosecco DOC — Youtube ufficiale | T7 · TECHNICAL NETWORK | 🟢 GREEN | **não** |
| `IT-T7-037` | Consorzio Tutela Vini Valpolicella — Youtube ufficiale | T7 · TECHNICAL NETWORK | 🟢 GREEN | **não** |
| `IT-T7-038` | Consorzio Tutela Vini Valpolicella | T7 · TECHNICAL NETWORK | 🟢 GREEN | **não** |
| `IT-T7-039` | Consorzio di Bonifica Piave — Youtube ufficiale | T7 · TECHNICAL NETWORK | 🟢 GREEN | **não** |
| `IT-T7-040` | Consorzio del Parmigiano Reggiano | T7 · TECHNICAL NETWORK | 🟢 GREEN | **não** |
| `IT-T7-041` | Consorzio di Bonifica della Romagna | T7 · TECHNICAL NETWORK | 🟢 GREEN | **não** |
| `IT-T7-042` | Consorzio di Tutela dell'Aceto Balsamico di Modena | T7 · TECHNICAL NETWORK | 🟢 GREEN | **não** |
| `IT-T7-043` | Agrofarma — Federchimica | T7 · TECHNICAL NETWORK | 🟢 GREEN | **não** |
| `IT-T8-001` | Agronotizie - Notizie per l'agricoltura (canale YouTube uf | T8 · FARMERS & INFLUENCERS | 🟢 GREEN | **não** |
| `IT-T8-002` | Image Line - pagina aziendale LinkedIn (IT) | T8 · FARMERS & INFLUENCERS | 🟡 YELLOW | **não** |
| `IT-T8-003` | AgroNotizie - profilo Instagram ufficiale | T8 · FARMERS & INFLUENCERS | 🟡 YELLOW | **não** |
| `IT-T8-004` | Terra e Vita — Edagricole — Youtube ufficiale | T8 · FARMERS & INFLUENCERS | 🟢 GREEN | **não** |
| `IT-T8-005` | Agriumbria — Youtube ufficiale | T8 · FARMERS & INFLUENCERS | 🟢 GREEN | **não** |
| `IT-T8-006` | L'Informatore Agrario — canale YouTube | T8 · FARMERS & INFLUENCERS | 🟢 GREEN | **não** |
| `IT-T8-007` | Rivista di Frutticoltura e di Ortofloricoltura | T8 · FARMERS & INFLUENCERS | 🟢 GREEN | **não** |
| `IT-T8-008` | Agroalimentare News | T8 · FARMERS & INFLUENCERS | 🟢 GREEN | **não** |
| `IT-T9-001` | páginas de atualidades de BASF, Bayer, Syngenta, Corteva… | T9 · COMPETITORS | ⚪ NAO SEI | **não** |
| `IT-T9-002` | Bayer CropScience Italia — comunicação pública | T9 · COMPETITORS | 🟡 YELLOW | **não** |
| `IT-T9-008` | ADAMA Italia — comunicação pública | T9 · COMPETITORS | 🟡 YELLOW | **não** |
| `IT-T9-009` | Cifo | T9 · COMPETITORS | 🟢 GREEN | **não** |
| `IT-T9-010` | Serbios | T9 · COMPETITORS | 🟡 YELLOW | **não** |
| `IT-T9-011` | Koppert Italia | T9 · COMPETITORS | 🟡 YELLOW | **não** |
| `IT-T9-012` | CBC Biogard | T9 · COMPETITORS | 🟢 GREEN | **não** |
| `IT-T9-013` | Certis Belchim Italia | T9 · COMPETITORS | 🟡 YELLOW | **não** |
| `IT-T9-014` | Conserve Italia — Youtube ufficiale | T9 · COMPETITORS | 🟢 GREEN | **não** |
| `IT-T9-015` | Conserve Italia | T9 · COMPETITORS | 🟢 GREEN | **não** |
| `IT-T9-016` | Consorzi Agrari d'Italia — CAI — Youtube ufficiale | T9 · COMPETITORS | 🟢 GREEN | **não** |
| `IT-T9-017` | Koppert Italia — Youtube ufficiale | T9 · COMPETITORS | 🟢 GREEN | **não** |
| `IT-T9-018` | FreshPlaza Italia | T9 · COMPETITORS | 🟢 GREEN | **não** |
| `IT-T9-019` | SCAM | T9 · COMPETITORS | 🟢 GREEN | **não** |
| `IT-T9-020` | Sipcam Italia | T9 · COMPETITORS | 🟢 GREEN | **não** |

---

## AS PALAVRAS USADAS NA BUSCA

Na língua do país, sempre. Buscar em inglês devolve literatura
internacional, não a conversa técnica local.

### `regras/rotulos_censo.py:48` · 35 palavras

| grupo | palavras |
|---|---|
| `SCAPHOIDEUS_TITANUS` | scaphoideus · scafoideo |
| `FLAVESCENZA_DOURADA` | flavescenza · giallumi della vite |
| `BACTROCERA_OLEAE` | bactrocera oleae · mosca dell.oliva · mosca dell.olivo |
| `BACTROCERA_OUTRAS` | bactrocera dorsalis · bactrocera zonata |
| `OCCHIO_DI_PAVONE` | occhio di pavone · spilocaea · cicloconio · venturia oleaginea |
| `OLIVO` | olivo · oliveto · olive da · olivicol |
| `VENTURIA_MELO` | ticchiolatura · venturia inaequalis |
| `HALYOMORPHA` | halyomorpha · cimice asiatica |
| `DIABROTICA` | diabrotica |
| `OSTRINIA` | ostrinia · piralide |
| `FUSARIUM` | fusarium · fusarios |
| `ZYMOSEPTORIA` | zymoseptoria · septoria · septorios |
| `ECHINOCHLOA` | echinochloa · giavone |
| `ORYZA_CRODO` | riso crodo |
| `AMBROSIA` | ambrosia artemisiifolia |
| `POPILLIA` | popillia japonica |
| `XYLELLA` | xylella |

### `regras/sensor_coleta.py:213` · 68 palavras

| grupo | palavras |
|---|---|
| `ES-OLIVE-REPILO` | repilo del olivo · Venturia oleaginea olivo · repilo olivar tratamiento · jornada tecnica olivar repilo |
| `ES-CEREAL-SEPTORIA` | septoria trigo · septoriosis del trigo · Zymoseptoria tritici trigo · jornada tecnica cereal septoria |
| `IT-VINE-FLAVESCENCE` | flavescenza dorata vite · flavescenza dorata vigneto · giallumi della vite · convegno flavescenza dorata |
| `IT-DURUM_WHEAT-FUSARIUM` | fusariosi grano duro · micotossine grano duro · fusariosi della spiga · convegno grano duro micotossine |
| `FR-VINE-DOWNY_MILDEW` | mildiou de la vigne · Plasmopara viticola vigne · mildiou vigne traitement · webinaire mildiou vigne |
| `FR-CEREAL-SEPTORIA` | septoriose du ble · Zymoseptoria tritici ble · septoriose ble traitement · webinaire septoriose ble |
| `IT-MAIZE-WEED` | diserbo del mais · infestanti del mais · diserbo mais pre-emergenza · diserbo mais post-emergenza |
| `IT-CEREAL-WEED` | diserbo dei cereali · diserbo del grano infestanti · loietto resistente frumento · avena resistente diserbo grano |
| `IT-SOYBEAN-AMARANTHUS` | amaranto resistente soia · diserbo della soia · infestanti resistenti soia · resistenza erbicidi soia |
| `IT-SUGARBEET-WEED` | diserbo barbabietola da zucchero · diserbo bietola · infestanti barbabietola · diserbo bietola post-emergenza |
| `IT-RICE-WEED` | diserbo del riso · riso crodo diserbo · giavone risaia · diserbo risaia infestanti |
| `IT-APPLE-DISEASE` | ticchiolatura del melo · difesa del melo · ticchiolatura melo trattamenti · melo maculatura bruna |
| `IT-VINE-WEED` | diserbo del vigneto · gestione del sottofila vigneto · inerbimento vigneto · diserbo sottofila vite |
| `IT-OLIVE-BACTROCERA` | mosca delle olive difesa · Bactrocera oleae olivo · monitoraggio mosca olivo · trattamento mosca olive |
| `IT-CEREAL-SEPTORIA` | septoriosi del frumento · malattie fogliari frumento · difesa cereali a paglia · ruggine gialla frumento |
| `IT-APPLE-INSECT` | afidi del melo difesa · carpocapsa del melo · insetticidi melo difesa · difesa melo insetti |
| `IT-TOMATO-DISEASE` | peronospora del pomodoro · difesa pomodoro malattie · alternaria pomodoro · botrite pomodoro difesa |

---

Veja também: o mesmo conteúdo, navegável e ligado ao código que
faz a coleta, no **System Map** em `/system-map/` (bloco **COLETA**).
