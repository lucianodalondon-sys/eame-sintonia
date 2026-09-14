# CENSO DE ESCOPO DE FONTES — SINTONIA EAME

> **Este ficheiro é gerado.** Não o edite à mão: edite a lei em
> [`../../regras/ESCOPO-DE-FONTES.json`](../../regras/ESCOPO-DE-FONTES.json)
> ou a ficha da fonte, e rode `py system-map/scripts/generate_system_map.py`.

Este censo responde a UMA pergunta, e não à outra parecida:

```
esta fonte EXISTE e nós conhecemo-la?      <- o ATLAS responde
esta fonte pode ser CHAMADA pela operação? <- esta página responde
```

País operacional ativo: **IT**.

Nada aqui foi apagado. Espanha e França continuam inteiras no atlas, nos
contratos, nas evidências e nos source packs, e continuam pesquisáveis por
gente. O que elas deixaram de poder fazer é entrar numa corrida italiana.

---

## OS CINCO GRUPOS

| grupo | fichas | contas | recortes |
|---|---|---|---|
| `ITALY_ACTIVE` | 55 | 8 | 13 |
| `SPAIN_FUTURE` | 6 | 10 | 2 |
| `FRANCE_FUTURE` | 4 | 5 | 2 |
| `SHARED_EUROPE_INACTIVE` | 10 | 0 | 0 |
| `UNKNOWN` | 0 | 21 | 0 |

---

## ORGANIZAÇÃO NÃO É CANAL

```
54 CANAIS  ≠  54 ORGANIZAÇÕES
```

| | organizações | canais | fichas | contas | recortes |
|---|---|---|---|---|---|
| **Itália** | 48 | 62 | 54 | 8 | 13 |
| **Espanha** | 9 | 16 | 6 | 10 | 2 |
| **França** | 7 | 9 | 4 | 5 | 2 |
| **Europa partilhada** | 8 | 11 | 11 | 0 | 0 |
| **sem identidade provada** | 5 | 21 | 0 | 21 | 0 |

---

## O TESTE DE CONTAMINAÇÃO

O que o seletor italiano **conseguiria** executar hoje:

| medida | valor |
|---|---|
| `ES_ACTIVE_IN_ITALY` | **0** ✅ |
| `FR_ACTIVE_IN_ITALY` | **0** ✅ |
| `UNKNOWN_ACTIVE_IN_ITALY` | **0** ✅ |
| `EU_UNAPPROVED_ACTIVE_IN_ITALY` | **0** ✅ |

Ativos hoje: **55** fichas · **8** contas · **13** recortes.

---

## AS FONTES, UMA A UMA

| SOURCE_ID | dono | escopo | grupo | contrato | chamável | motivo |
|---|---|---|---|---|---|---|
| `EU-T4-001` | Publications Office of the Europea | EU | `ITALY_ACTIVE` | sim | **sim** | autorizada explicitamente para a operacao italiana: a aprovacao europeia da su |
| `IT-T1-001` | ISTAT — Istituto Nazionale di Stat | IT | `ITALY_ACTIVE` | não | **sim** | COUNTRY_SCOPE = IT = pais da operacao ativa |
| `IT-T10-001` | ISMEA — Istituto di Servizi per il | IT | `ITALY_ACTIVE` | não | **sim** | COUNTRY_SCOPE = IT = pais da operacao ativa |
| `IT-T10-002` | BMTI — Borsa Merci Telematica Ital | IT | `ITALY_ACTIVE` | não | **sim** | COUNTRY_SCOPE = IT = pais da operacao ativa |
| `IT-T10-003` | ISTAT — Istituto Nazionale di Stat | IT | `ITALY_ACTIVE` | não | **sim** | COUNTRY_SCOPE = IT = pais da operacao ativa |
| `IT-T10-004` | ICQRF — Dipartimento dell'Ispettor | IT | `ITALY_ACTIVE` | não | **sim** | COUNTRY_SCOPE = IT = pais da operacao ativa |
| `IT-T10-005` | ICQRF — Dipartimento dell'Ispettor | IT | `ITALY_ACTIVE` | não | **sim** | COUNTRY_SCOPE = IT = pais da operacao ativa |
| `IT-T11-001` | FederUnacoma / EIMA International | IT | `ITALY_ACTIVE` | não | **sim** | COUNTRY_SCOPE = IT = pais da operacao ativa |
| `IT-T11-002` | Unione Italiana Vini (Enovitis in  | IT | `ITALY_ACTIVE` | não | **sim** | COUNTRY_SCOPE = IT = pais da operacao ativa |
| `IT-T11-003` | Veronafiere S.p.A. (Fieragricola) | IT | `ITALY_ACTIVE` | não | **sim** | COUNTRY_SCOPE = IT = pais da operacao ativa |
| `IT-T11-004` | Fondazione Edmund Mach (FEM) | IT | `ITALY_ACTIVE` | não | **sim** | COUNTRY_SCOPE = IT = pais da operacao ativa |
| `IT-T12-002` | MASAF — Ministero dell'Agricoltura | IT | `ITALY_ACTIVE` | não | **sim** | COUNTRY_SCOPE = IT = pais da operacao ativa |
| `IT-T2-001` | ARPAE Emilia-Romagna | IT | `ITALY_ACTIVE` | não | **sim** | COUNTRY_SCOPE = IT = pais da operacao ativa |
| `IT-T2-002` | ARPAV — Agenzia Regionale per la P | IT | `ITALY_ACTIVE` | não | **sim** | COUNTRY_SCOPE = IT = pais da operacao ativa |
| `IT-T2-003` | CNR-IBE — Istituto per la BioEcono | IT | `ITALY_ACTIVE` | não | **sim** | COUNTRY_SCOPE = IT = pais da operacao ativa |
| `IT-T2-004` | SIAS — Servizio Informativo Agrome | IT | `ITALY_ACTIVE` | não | **sim** | COUNTRY_SCOPE = IT = pais da operacao ativa |
| `IT-T2-005` | ALSIA — Agenzia Lucana di Sviluppo | IT | `ITALY_ACTIVE` | não | **sim** | COUNTRY_SCOPE = IT = pais da operacao ativa |
| `IT-T3-001` | Regione Emilia-Romagna — Servizio  | IT | `ITALY_ACTIVE` | não | **sim** | COUNTRY_SCOPE = IT = pais da operacao ativa |
| `IT-T3-002` | Regione Campania — Servizio Fitosa | IT | `ITALY_ACTIVE` | não | **sim** | COUNTRY_SCOPE = IT = pais da operacao ativa |
| `IT-T3-003` | Regione Campania — Servizio Fitosa | IT | `ITALY_ACTIVE` | não | **sim** | COUNTRY_SCOPE = IT = pais da operacao ativa |
| `IT-T3-004` | ALSIA — Agenzia Lucana di Sviluppo | IT | `ITALY_ACTIVE` | não | **sim** | COUNTRY_SCOPE = IT = pais da operacao ativa |
| `IT-T3-005` | Terre dell'Etruria — Società Coope | IT | `ITALY_ACTIVE` | não | **sim** | COUNTRY_SCOPE = IT = pais da operacao ativa |
| `IT-T3-006` | Terre dell'Etruria — Società Coope | IT | `ITALY_ACTIVE` | não | **sim** | COUNTRY_SCOPE = IT = pais da operacao ativa |
| `IT-T3-007` | Regione Siciliana — Servizio Fitos | IT | `ITALY_ACTIVE` | não | **sim** | COUNTRY_SCOPE = IT = pais da operacao ativa |
| `IT-T3-008` | ARIF Puglia — Agenzia Regionale pe | IT | `ITALY_ACTIVE` | não | **sim** | COUNTRY_SCOPE = IT = pais da operacao ativa |
| `IT-T3-009` | Assoproli Bari — Associazione Prod | IT | `ITALY_ACTIVE` | não | **sim** | COUNTRY_SCOPE = IT = pais da operacao ativa |
| `IT-T3-010` | APOL Lecce — Associazione Produtto | IT | `ITALY_ACTIVE` | não | **sim** | COUNTRY_SCOPE = IT = pais da operacao ativa |
| `IT-T3-011` | AGRIOS — Arbeitsgruppe für den Int | IT | `ITALY_ACTIVE` | não | **sim** | COUNTRY_SCOPE = IT = pais da operacao ativa |
| `IT-T3-012` | Fondazione Edmund Mach (FEM) | IT | `ITALY_ACTIVE` | não | **sim** | COUNTRY_SCOPE = IT = pais da operacao ativa |
| `IT-T4-001` | Ministero della Salute (Italia) | IT | `ITALY_ACTIVE` | sim | **sim** | COUNTRY_SCOPE = IT = pais da operacao ativa |
| `IT-T5-001` | CREA — Consiglio per la ricerca in | IT | `ITALY_ACTIVE` | não | **sim** | COUNTRY_SCOPE = IT = pais da operacao ativa |
| `IT-T5-002` | Fondazione Edmund Mach (FEM) | IT | `ITALY_ACTIVE` | não | **sim** | COUNTRY_SCOPE = IT = pais da operacao ativa |
| `IT-T5-003` | Giornate Fitopatologiche | IT | `ITALY_ACTIVE` | não | **sim** | COUNTRY_SCOPE = IT = pais da operacao ativa |
| `IT-T5-004` | CNR — Consiglio Nazionale delle Ri | IT | `ITALY_ACTIVE` | não | **sim** | COUNTRY_SCOPE = IT = pais da operacao ativa |
| `IT-T5-005` | SIRFI — Società Italiana per la Ri | IT | `ITALY_ACTIVE` | não | **sim** | COUNTRY_SCOPE = IT = pais da operacao ativa |
| `IT-T7-001` | Terre dell'Etruria — Società Coope | IT | `ITALY_ACTIVE` | não | **sim** | COUNTRY_SCOPE = IT = pais da operacao ativa |
| `IT-T7-002` | MASAF — Ministero dell'Agricoltura | IT | `ITALY_ACTIVE` | não | **sim** | COUNTRY_SCOPE = IT = pais da operacao ativa |
| `IT-T7-003` | Consorzi Agrari d'Italia — CAI S.p | IT | `ITALY_ACTIVE` | não | **sim** | COUNTRY_SCOPE = IT = pais da operacao ativa |
| `IT-T7-004` | Apo Conerpo | IT | `ITALY_ACTIVE` | não | **sim** | COUNTRY_SCOPE = IT = pais da operacao ativa |
| `IT-T7-005` | Agrintesa Società Cooperativa Agri | IT | `ITALY_ACTIVE` | não | **sim** | COUNTRY_SCOPE = IT = pais da operacao ativa |
| `IT-T7-006` | Fondazione Edmund Mach (FEM) | IT | `ITALY_ACTIVE` | não | **sim** | COUNTRY_SCOPE = IT = pais da operacao ativa |
| `IT-T7-007` | Apofruit Italia Società Cooperativ | IT | `ITALY_ACTIVE` | não | **sim** | COUNTRY_SCOPE = IT = pais da operacao ativa |
| `IT-T7-008` | Ortofruit Italia | IT | `ITALY_ACTIVE` | não | **sim** | COUNTRY_SCOPE = IT = pais da operacao ativa |
| `IT-T7-009` | VOG — Consorzio Cooperative Ortofr | IT | `ITALY_ACTIVE` | não | **sim** | COUNTRY_SCOPE = IT = pais da operacao ativa |
| `IT-T7-010` | Melinda Consorzio | IT | `ITALY_ACTIVE` | não | **sim** | COUNTRY_SCOPE = IT = pais da operacao ativa |
| `IT-T7-011` | CAVIT — Cantina Viticoltori Trenti | IT | `ITALY_ACTIVE` | não | **sim** | COUNTRY_SCOPE = IT = pais da operacao ativa |
| `IT-T7-012` | PICA — Piattaforma Integrata Carto | IT | `ITALY_ACTIVE` | não | **sim** | COUNTRY_SCOPE = IT = pais da operacao ativa |
| `IT-T9-001` | BASF Italia S.p.A. | IT | `ITALY_ACTIVE` | não | **sim** | COUNTRY_SCOPE = IT = pais da operacao ativa |
| `IT-T9-002` | Bayer CropScience Italia | IT | `ITALY_ACTIVE` | não | **sim** | COUNTRY_SCOPE = IT = pais da operacao ativa |
| `IT-T9-003` | Syngenta Italia S.p.A. | IT | `ITALY_ACTIVE` | não | **sim** | COUNTRY_SCOPE = IT = pais da operacao ativa |
| `IT-T9-004` | Corteva Agriscience Italia | IT | `ITALY_ACTIVE` | não | **sim** | COUNTRY_SCOPE = IT = pais da operacao ativa |
| `IT-T9-005` | Nufarm Italia S.r.l. | IT | `ITALY_ACTIVE` | não | **sim** | COUNTRY_SCOPE = IT = pais da operacao ativa |
| `IT-T9-006` | FMC Agricultural Solutions Italia | IT | `ITALY_ACTIVE` | não | **sim** | COUNTRY_SCOPE = IT = pais da operacao ativa |
| `IT-T9-007` | UPL Italia S.r.l. | IT | `ITALY_ACTIVE` | não | **sim** | COUNTRY_SCOPE = IT = pais da operacao ativa |
| `IT-T9-008` | ADAMA Italia S.r.l. | IT | `ITALY_ACTIVE` | não | **sim** | COUNTRY_SCOPE = IT = pais da operacao ativa |
| `ES-T3-001` | Junta de Andalucía — Consejería de | ES | `SPAIN_FUTURE` | sim | não | COUNTRY_SCOPE = ES, STATUS_OPERACIONAL = FUTURE. Preservada e pesquisavel; for |
| `ES-T4-001` | MAPA — Ministerio de Agricultura,  | ES | `SPAIN_FUTURE` | não | não | COUNTRY_SCOPE = ES, STATUS_OPERACIONAL = FUTURE. Preservada e pesquisavel; for |
| `ES-T4-002` | MAPA | ES | `SPAIN_FUTURE` | não | não | COUNTRY_SCOPE = ES, STATUS_OPERACIONAL = FUTURE. Preservada e pesquisavel; for |
| `ES-T4-003` | MAPA | ES | `SPAIN_FUTURE` | não | não | COUNTRY_SCOPE = ES, STATUS_OPERACIONAL = FUTURE. Preservada e pesquisavel; for |
| `ES-T4-005` | MAPA — D.G. de Sanidad de la Produ | ES | `SPAIN_FUTURE` | sim | não | COUNTRY_SCOPE = ES, STATUS_OPERACIONAL = FUTURE. Preservada e pesquisavel; for |
| `ES-T5-002` | NAO SEI | ES | `SPAIN_FUTURE` | não | não | COUNTRY_SCOPE = ES, STATUS_OPERACIONAL = FUTURE. Preservada e pesquisavel; for |
| `EU-T1-001` | Eurostat | EU | `SHARED_EUROPE_INACTIVE` | não | não | fonte europeia/partilhada sem autorizacao explicita para a operacao IT. ITALY_ |
| `EU-T1-002` | Eurostat | EU | `SHARED_EUROPE_INACTIVE` | não | não | fonte europeia/partilhada sem autorizacao explicita para a operacao IT. ITALY_ |
| `EU-T10-001` | Comissão Europeia — DG AGRI | EU | `SHARED_EUROPE_INACTIVE` | não | não | fonte europeia/partilhada sem autorizacao explicita para a operacao IT. ITALY_ |
| `EU-T12-001` | Publications Office of the Europea | EU | `SHARED_EUROPE_INACTIVE` | não | não | fonte europeia/partilhada sem autorizacao explicita para a operacao IT. ITALY_ |
| `EU-T2-001` | NASA Langley Research Center | EU | `SHARED_EUROPE_INACTIVE` | não | não | fonte europeia/partilhada sem autorizacao explicita para a operacao IT. ITALY_ |
| `EU-T2-002` | Eurostat / GISCO | EU | `SHARED_EUROPE_INACTIVE` | não | não | fonte europeia/partilhada sem autorizacao explicita para a operacao IT. ITALY_ |
| `EU-T2-003` | NAO SEI | EU | `SHARED_EUROPE_INACTIVE` | não | não | fonte europeia/partilhada sem autorizacao explicita para a operacao IT. ITALY_ |
| `EU-T3-001` | European and Mediterranean Plant P | EU | `SHARED_EUROPE_INACTIVE` | não | não | fonte europeia/partilhada sem autorizacao explicita para a operacao IT. ITALY_ |
| `EU-T4-002` | Comissão Europeia — DG SANTE | EU | `SHARED_EUROPE_INACTIVE` | não | não | fonte europeia/partilhada sem autorizacao explicita para a operacao IT. ITALY_ |
| `EU-T5-001` | OurResearch (organização sem fins  | EU | `SHARED_EUROPE_INACTIVE` | não | não | fonte europeia/partilhada sem autorizacao explicita para a operacao IT. ITALY_ |
| `FR-T13-001` | DINUM / INSEE (França) | FR | `FRANCE_FUTURE` | não | não | COUNTRY_SCOPE = FR, STATUS_OPERACIONAL = FUTURE. Preservada e pesquisavel; for |
| `FR-T3-001` | rede de epidemiovigilância — DRAAF | FR | `FRANCE_FUTURE` | não | não | COUNTRY_SCOPE = FR, STATUS_OPERACIONAL = FUTURE. Preservada e pesquisavel; for |
| `FR-T3-002` | publicado em data.gouv.fr (licença | FR | `FRANCE_FUTURE` | não | não | COUNTRY_SCOPE = FR, STATUS_OPERACIONAL = FUTURE. Preservada e pesquisavel; for |
| `FR-T4-001` | ANSES (Agence nationale de sécurit | FR | `FRANCE_FUTURE` | sim | não | COUNTRY_SCOPE = FR, STATUS_OPERACIONAL = FUTURE. Preservada e pesquisavel; for |

---

## AS CONTAS PÚBLICAS, UMA A UMA

A célula do lote (`EMPRESA|PAÍS|PLATAFORMA`) é a **pergunta** que se foi
fazer, não a identidade da conta que se encontrou: oito células levam duas
contas diferentes. Por isso o censo conta **linhas**, e uma célula ambígua
fecha em `UNKNOWN`.

| célula | dono | canal | escopo provado | grupo | chamável | motivo |
|---|---|---|---|---|---|---|
| `BASF|ES|FACEBOOK` | BASF | FACEBOOK | LOCAL_COUNTRY_PROVED | `SPAIN_FUTURE` | não | conta local PROVADA de ES — preservada, e fora da operacao IT. |
| `BASF|ES|INSTAGRAM` | BASF | INSTAGRAM | LOCAL_COUNTRY_PROVED | `SPAIN_FUTURE` | não | conta local PROVADA de ES — preservada, e fora da operacao IT. |
| `BASF|ES|LINKEDIN` | BASF | LINKEDIN | GLOBAL | `UNKNOWN` | não | COUNTRY_SCOPE = GLOBAL — a localidade da conta nao esta provada. UNKNO |
| `BASF|ES|YOUTUBE` | BASF | YOUTUBE | NOT_KNOWN | `UNKNOWN` | não | COUNTRY_SCOPE = NOT_KNOWN — a localidade da conta nao esta provada. UN |
| `BASF|FR|YOUTUBE` | BASF | YOUTUBE | NOT_KNOWN | `UNKNOWN` | não | COUNTRY_SCOPE = NOT_KNOWN — a localidade da conta nao esta provada. UN |
| `BASF|IT|FACEBOOK` | BASF | FACEBOOK | LOCAL_COUNTRY_PROVED | `ITALY_ACTIVE` | **sim** | identidade PROVED + COUNTRY_SCOPE LOCAL_COUNTRY_PROVED + pais IT = ope |
| `BASF|IT|INSTAGRAM` | BASF | INSTAGRAM | GLOBAL | `UNKNOWN` | não | COUNTRY_SCOPE = GLOBAL — a localidade da conta nao esta provada. UNKNO |
| `BASF|IT|LINKEDIN` | BASF | LINKEDIN | GLOBAL | `UNKNOWN` | não | COUNTRY_SCOPE = GLOBAL — a localidade da conta nao esta provada. UNKNO |
| `BASF|IT|YOUTUBE` | BASF | YOUTUBE | NOT_KNOWN | `UNKNOWN` | não | COUNTRY_SCOPE = NOT_KNOWN — a localidade da conta nao esta provada. UN |
| `BAYER|ES|FACEBOOK` | BAYER | FACEBOOK | LOCAL_COUNTRY_PROVED | `SPAIN_FUTURE` | não | conta local PROVADA de ES — preservada, e fora da operacao IT. |
| `BAYER|ES|INSTAGRAM` | BAYER | INSTAGRAM | LOCAL_COUNTRY_PROVED | `SPAIN_FUTURE` | não | conta local PROVADA de ES — preservada, e fora da operacao IT. |
| `BAYER|ES|YOUTUBE` | BAYER | YOUTUBE | LOCAL_COUNTRY_PROVED | `SPAIN_FUTURE` | não | conta local PROVADA de ES — preservada, e fora da operacao IT. |
| `BAYER|ES|YOUTUBE` | BAYER | YOUTUBE | NOT_KNOWN | `UNKNOWN` | não | COUNTRY_SCOPE = NOT_KNOWN — a localidade da conta nao esta provada. UN |
| `BAYER|FR|FACEBOOK` | BAYER | FACEBOOK | LOCAL_COUNTRY_PROVED | `FRANCE_FUTURE` | não | COLLECTION_AUTHORIZED = NO · a página é de MARCA/PRODUTO, não da empre |
| `BAYER|FR|YOUTUBE` | BAYER | YOUTUBE | LOCAL_COUNTRY_PROVED | `FRANCE_FUTURE` | não | conta local PROVADA de FR — preservada, e fora da operacao IT. |
| `BAYER|FR|YOUTUBE` | BAYER | YOUTUBE | NOT_KNOWN | `UNKNOWN` | não | COUNTRY_SCOPE = NOT_KNOWN — a localidade da conta nao esta provada. UN |
| `BAYER|IT|FACEBOOK` | BAYER | FACEBOOK | LOCAL_COUNTRY_PROVED | `ITALY_ACTIVE` | **sim** | identidade PROVED + COUNTRY_SCOPE LOCAL_COUNTRY_PROVED + pais IT = ope |
| `BAYER|IT|INSTAGRAM` | BAYER | INSTAGRAM | LOCAL_COUNTRY_PROVED | `ITALY_ACTIVE` | **sim** | identidade PROVED + COUNTRY_SCOPE LOCAL_COUNTRY_PROVED + pais IT = ope |
| `BAYER|IT|LINKEDIN` | BAYER | LINKEDIN | GLOBAL | `UNKNOWN` | não | COUNTRY_SCOPE = GLOBAL — a localidade da conta nao esta provada. UNKNO |
| `BAYER|IT|YOUTUBE` | BAYER | YOUTUBE | LOCAL_COUNTRY_PROVED | `ITALY_ACTIVE` | **sim** | identidade PROVED + COUNTRY_SCOPE LOCAL_COUNTRY_PROVED + pais IT = ope |
| `CORTEVA|ES|FACEBOOK` | CORTEVA | FACEBOOK | LOCAL_COUNTRY_PROVED | `SPAIN_FUTURE` | não | conta local PROVADA de ES — preservada, e fora da operacao IT. |
| `CORTEVA|FR|INSTAGRAM` | CORTEVA | INSTAGRAM | NOT_KNOWN | `UNKNOWN` | não | COUNTRY_SCOPE = NOT_KNOWN — a localidade da conta nao esta provada. UN |
| `CORTEVA|FR|YOUTUBE` | CORTEVA | YOUTUBE | NOT_KNOWN | `UNKNOWN` | não | COUNTRY_SCOPE = NOT_KNOWN — a localidade da conta nao esta provada. UN |
| `NUFARM|ES|FACEBOOK` | NUFARM | FACEBOOK | NOT_KNOWN | `UNKNOWN` | não | COUNTRY_SCOPE = NOT_KNOWN — a localidade da conta nao esta provada. UN |
| `NUFARM|ES|LINKEDIN` | NUFARM | LINKEDIN | NOT_KNOWN | `UNKNOWN` | não | COUNTRY_SCOPE = NOT_KNOWN — a localidade da conta nao esta provada. UN |
| `NUFARM|ES|YOUTUBE` | NUFARM | YOUTUBE | LOCAL_COUNTRY_PROVED | `SPAIN_FUTURE` | não | conta local PROVADA de ES — preservada, e fora da operacao IT. |
| `NUFARM|FR|FACEBOOK` | NUFARM | FACEBOOK | LOCAL_COUNTRY_PROVED | `FRANCE_FUTURE` | não | conta local PROVADA de FR — preservada, e fora da operacao IT. |
| `NUFARM|FR|FACEBOOK` | NUFARM | FACEBOOK | NOT_KNOWN | `UNKNOWN` | não | COUNTRY_SCOPE = NOT_KNOWN — a localidade da conta nao esta provada. UN |
| `NUFARM|FR|LINKEDIN` | NUFARM | LINKEDIN | NOT_KNOWN | `UNKNOWN` | não | COUNTRY_SCOPE = NOT_KNOWN — a localidade da conta nao esta provada. UN |
| `NUFARM|IT|FACEBOOK` | NUFARM | FACEBOOK | LOCAL_COUNTRY_PROVED | `ITALY_ACTIVE` | **sim** | identidade PROVED + COUNTRY_SCOPE LOCAL_COUNTRY_PROVED + pais IT = ope |
| `NUFARM|IT|FACEBOOK` | NUFARM | FACEBOOK | NOT_KNOWN | `UNKNOWN` | não | COUNTRY_SCOPE = NOT_KNOWN — a localidade da conta nao esta provada. UN |
| `NUFARM|IT|LINKEDIN` | NUFARM | LINKEDIN | NOT_KNOWN | `UNKNOWN` | não | COUNTRY_SCOPE = NOT_KNOWN — a localidade da conta nao esta provada. UN |
| `SYNGENTA|ES|FACEBOOK` | SYNGENTA | FACEBOOK | LOCAL_COUNTRY_PROVED | `SPAIN_FUTURE` | não | conta local PROVADA de ES — preservada, e fora da operacao IT. |
| `SYNGENTA|ES|FACEBOOK` | SYNGENTA | FACEBOOK | NOT_KNOWN | `UNKNOWN` | não | COUNTRY_SCOPE = NOT_KNOWN — a localidade da conta nao esta provada. UN |
| `SYNGENTA|ES|INSTAGRAM` | SYNGENTA | INSTAGRAM | LOCAL_COUNTRY_PROVED | `SPAIN_FUTURE` | não | conta local PROVADA de ES — preservada, e fora da operacao IT. |
| `SYNGENTA|ES|YOUTUBE` | SYNGENTA | YOUTUBE | LOCAL_COUNTRY_PROVED | `SPAIN_FUTURE` | não | conta local PROVADA de ES — preservada, e fora da operacao IT. |
| `SYNGENTA|ES|YOUTUBE` | SYNGENTA | YOUTUBE | NOT_KNOWN | `UNKNOWN` | não | COUNTRY_SCOPE = NOT_KNOWN — a localidade da conta nao esta provada. UN |
| `SYNGENTA|FR|FACEBOOK` | SYNGENTA | FACEBOOK | LOCAL_COUNTRY_PROVED | `FRANCE_FUTURE` | não | conta local PROVADA de FR — preservada, e fora da operacao IT. |
| `SYNGENTA|FR|FACEBOOK` | SYNGENTA | FACEBOOK | NOT_KNOWN | `UNKNOWN` | não | COUNTRY_SCOPE = NOT_KNOWN — a localidade da conta nao esta provada. UN |
| `SYNGENTA|FR|YOUTUBE` | SYNGENTA | YOUTUBE | LOCAL_COUNTRY_PROVED | `FRANCE_FUTURE` | não | conta local PROVADA de FR — preservada, e fora da operacao IT. |
| `SYNGENTA|IT|FACEBOOK` | SYNGENTA | FACEBOOK | LOCAL_COUNTRY_PROVED | `ITALY_ACTIVE` | **sim** | identidade PROVED + COUNTRY_SCOPE LOCAL_COUNTRY_PROVED + pais IT = ope |
| `SYNGENTA|IT|FACEBOOK` | SYNGENTA | FACEBOOK | NOT_KNOWN | `UNKNOWN` | não | COUNTRY_SCOPE = NOT_KNOWN — a localidade da conta nao esta provada. UN |
| `SYNGENTA|IT|INSTAGRAM` | SYNGENTA | INSTAGRAM | LOCAL_COUNTRY_PROVED | `ITALY_ACTIVE` | **sim** | identidade PROVED + COUNTRY_SCOPE LOCAL_COUNTRY_PROVED + pais IT = ope |
| `SYNGENTA|IT|YOUTUBE` | SYNGENTA | YOUTUBE | LOCAL_COUNTRY_PROVED | `ITALY_ACTIVE` | **sim** | identidade PROVED + COUNTRY_SCOPE LOCAL_COUNTRY_PROVED + pais IT = ope |

---

## OS RECORTES DE BUSCA

O termo decide o que se procura e em que língua — é seleção de fonte
também. Os recortes ES e FR **não foram apagados**: continuam declarados
em `regras/sensor_coleta.py`, e o runner italiano não os carrega.

| recorte | escopo | grupo | carregado pelo runner IT? |
|---|---|---|---|
| `ES-CEREAL-SEPTORIA` | ES | `SPAIN_FUTURE` | não |
| `ES-OLIVE-REPILO` | ES | `SPAIN_FUTURE` | não |
| `FR-CEREAL-SEPTORIA` | FR | `FRANCE_FUTURE` | não |
| `FR-VINE-DOWNY_MILDEW` | FR | `FRANCE_FUTURE` | não |
| `IT-APPLE-DISEASE` | IT | `ITALY_ACTIVE` | **sim** |
| `IT-APPLE-INSECT` | IT | `ITALY_ACTIVE` | **sim** |
| `IT-CEREAL-SEPTORIA` | IT | `ITALY_ACTIVE` | **sim** |
| `IT-CEREAL-WEED` | IT | `ITALY_ACTIVE` | **sim** |
| `IT-DURUM_WHEAT-FUSARIUM` | IT | `ITALY_ACTIVE` | **sim** |
| `IT-MAIZE-WEED` | IT | `ITALY_ACTIVE` | **sim** |
| `IT-OLIVE-BACTROCERA` | IT | `ITALY_ACTIVE` | **sim** |
| `IT-RICE-WEED` | IT | `ITALY_ACTIVE` | **sim** |
| `IT-SOYBEAN-AMARANTHUS` | IT | `ITALY_ACTIVE` | **sim** |
| `IT-SUGARBEET-WEED` | IT | `ITALY_ACTIVE` | **sim** |
| `IT-TOMATO-DISEASE` | IT | `ITALY_ACTIVE` | **sim** |
| `IT-VINE-FLAVESCENCE` | IT | `ITALY_ACTIVE` | **sim** |
| `IT-VINE-WEED` | IT | `ITALY_ACTIVE` | **sim** |

---

Veja também: [`INDICE-DE-FONTES.md`](INDICE-DE-FONTES.md) — a porta de
entrada, e [`ATLAS-DE-FONTES-EAME.md`](ATLAS-DE-FONTES-EAME.md) — a ficha
inteira de cada fonte.
