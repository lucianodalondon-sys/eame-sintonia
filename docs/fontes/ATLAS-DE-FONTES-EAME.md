# ATLAS DE FONTES — SINTONIA EAME

Catálogo de tudo que conseguimos **realmente** observar em França, Espanha, Itália e na
camada comum europeia.

> Este atlas registra **fontes**, não desejos. Uma linha só existe aqui depois que alguém
> abriu a fonte, olhou o que ela entrega e guardou evidência disso.

**Estado:** MISSÃO 02 em curso — **7 fontes registradas** (5 GREEN, 2 NÃO SEI).
**Última atualização:** 2026-08-28

---

## REGRA DAS CINCO FONTES

Para cada território (T1–T12), a exploração inicial vai até:

| Recorte | Teto inicial |
|---|---|
| EUROPE | até 5 fontes |
| FRANCE | até 5 fontes |
| SPAIN | até 5 fontes |
| ITALY | até 5 fontes |

**"Até 5" é teto de exploração, não meta.** Não preencher número artificialmente.
**2 COMPROVADAS é melhor que 5 FRACAS.**

---

## VERDICT

| Verdict | Significado |
|---|---|
| **GREEN** | Fonte verificada, acessível, útil, com exemplo real capturado. Serve para construir. |
| **YELLOW** | Fonte real e relevante, mas com atrito: acesso difícil, licença dúbia, granularidade fraca, frequência ruim ou automação incerta. |
| **RED** | Verificada e **descartada por motivo concreto** — não serve, não é acessível, ou o uso é proibido. Exige o motivo escrito. |
| **NÃO SEI** | Não foi possível verificar. **Nunca converter "não consegui verificar" em RED.** |

---

## OS 12 TERRITÓRIOS

| ID | Território | Escopo |
|---|---|---|
| **T1** | CROP & PRODUCTION | área plantada, produção, produtividade, calendário agrícola, desenvolvimento da cultura, previsão de safra, regiões produtoras, histórico |
| **T2** | CLIMATE / WATER / SOIL | chuva, temperatura, seca, geada, ondas de calor, umidade do solo, estresse hídrico, eventos extremos, indicadores agronômicos |
| **T3** | PEST / DISEASE / WEEDS | doenças, insetos, plantas daninhas, alertas, intensidade, geografia, evolução temporal, resistência |
| **T4** | REGULATORY | produtos, registros, culturas autorizadas, alvos, substâncias ativas, empresas, validade, novas autorizações, retiradas, restrições |
| **T5** | SCIENCE | papers, estudos, trials, institutos, universidades, projetos, tecnologias, novas práticas, resistência, inovação agronômica |
| **T6** | RESEARCHERS | pesquisadores por cultura, problema, instituição, território, especialidade |
| **T7** | TECHNICAL NETWORK | agrônomos, advisors, crop specialists, consultores, extensão, institutos técnicos, cooperativas, associações |
| **T8** | FARMERS & INFLUENCERS | agricultores, creators, YouTube, Instagram, TikTok, LinkedIn, podcasts, newsletters |
| **T9** | COMPETITORS | BASF, Bayer, Syngenta, Corteva, FMC, UPL, Nufarm + outros descobertos como relevantes |
| **T10** | MARKET / TRADE / INDUSTRY | commodities, produção, preços confiáveis, importações, exportações, indústria, ingredientes ativos, movimentos de mercado |
| **T11** | EVENTS | feiras, congressos, field days, webinars, eventos científicos, pesquisadores participantes, temas, empresas presentes |
| **T12** | POLICY / AGRICULTURAL ENVIRONMENT | CAP, políticas agrícolas, sustentabilidade, redução de insumos, agricultura regenerativa, restrições, mudanças que afetam produtor/mercado/portfólio |

### Separação obrigatória em T4

**EU ACTIVE SUBSTANCE** e **NATIONAL PRODUCT AUTHORIZATION** são camadas distintas e
**não podem ser misturadas**. Uma substância aprovada na UE não implica produto autorizado
em França, Espanha ou Itália; um produto autorizado nacionalmente não implica as mesmas
culturas, alvos ou condições nos três países. Toda ficha de T4 declara em qual camada está.

### Separação obrigatória em T8

Quatro eixos independentes, medidos separadamente — nunca somados num único "score":

- **REACH** — alcance de audiência.
- **FIELD AUTHORITY** — autoridade de quem está no campo, produzindo.
- **TECHNICAL AUTHORITY** — autoridade técnica/agronômica reconhecida.
- **COMMERCIAL INFLUENCE** — influência sobre decisão de compra.

### Restrição em T6

Descobrir pesquisadores relevantes **por cultura, problema, instituição, território e
especialidade**. **Não criar ranking universal** de pesquisadores.

---

## FICHA OBRIGATÓRIA DA FONTE

Toda fonte descoberta recebe uma ficha completa. Campo sem resposta recebe `NÃO SEI` —
nunca fica em branco e nunca é preenchido por plausibilidade.

```
SOURCE_ID:                    # ex.: FR-T3-001
SOURCE_NAME:
SOURCE_OWNER:                 # quem publica e responde pelo dado
COUNTRY:                      # EUROPE | FRANCE | SPAIN | ITALY
REGION:
LANGUAGE:
TERRITORY:                    # T1..T12
SOURCE_TYPE:
URL:
ACCESS_METHOD:                # API | JSON | CSV | XML | HTML | PDF | RSS | SOCIAL | OTHER
CROPS:
TOPICS:
GEOGRAPHIC_GRANULARITY:       # país | região | subregião | ponto — o que a fonte REALMENTE dá
UPDATE_FREQUENCY:
HISTORICAL_DEPTH:
SOURCE_IDENTITY_PRESERVABLE:  # dá para provar de onde veio?
DOCUMENT_ID_AVAILABLE:
PUBLICATION_DATE_AVAILABLE:
RAW_EVIDENCE_PRESERVABLE:
AUTOMATION_FEASIBILITY:
COLLECTION_FEASIBILITY:
LEGAL_OR_ACCESS_RISK:         # licença, termos de uso, GDPR, robots, paywall
REAL_EXAMPLE:                 # um caso concreto, com link/arquivo
ADAMA_USE_CASE:               # para quem serve e em que decisão
EVIDENCE:                     # caminho da amostra em data/samples/ ou research/
VERDICT:                      # GREEN | YELLOW | RED | NÃO SEI
```

### Convenção de SOURCE_ID

`<PAÍS>-<TERRITÓRIO>-<sequencial>` — `EU`, `FR`, `ES`, `IT` + `T1`..`T12` + `001`.
Exemplos: `EU-T4-001`, `FR-T3-002`, `ES-T1-001`, `IT-T12-001`.
O ID, uma vez atribuído, **não é reciclado** mesmo se a fonte virar RED.

---

## AMOSTRA REAL

Para cada fonte **GREEN** ou **YELLOW** considerada importante: capturar **pelo menos um
exemplo real** e preservá-lo. Quando possível, guardar: fonte, URL, título, data, país,
região, cultura, assunto, texto original, idioma, identificador, evidência bruta.

**Não iniciar coleta massiva.** Nesta missão estamos medindo capacidade, não construindo base.

### Multilíngue

Preservar sempre `ORIGINAL_LANGUAGE`, `ORIGINAL_TEXT`, `SOURCE`, `EVIDENCE`.
Pode existir `NORMALIZED_ENGLISH` como campo adicional.
**Tradução nunca substitui a evidência original.**

### Geografia

Separar desde a primeira amostra:

- **SOURCE_LOCATION** — onde está quem publicou;
- **FACT_LOCATION** — onde o fato ocorreu.

Hierarquia desejada: `EUROPE → COUNTRY → REGION → SUBREGION → FACT`.
Investigar normalização por **NUTS** quando útil.
**Não forçar granularidade que a fonte não tem.**

---

## REGISTRO DE FONTES

### T4 · REGULATORY — EUROPE

#### EU-T4-001 · EU Publications Office / CELLAR — Jornal Oficial da UE

```
SOURCE_ID:                    EU-T4-001
SOURCE_NAME:                  CELLAR / EU Publications Office (Official Journal of the EU)
SOURCE_OWNER:                 Publications Office of the European Union
COUNTRY:                      EUROPE
REGION:                       EU-27 (ato de alcance da União)
LANGUAGE:                     24 línguas oficiais (EN, FR, ES, IT verificadas)
TERRITORY:                    T4 (também serve T12)
SOURCE_TYPE:                  Registro legal oficial primário
URL:                          https://publications.europa.eu/webapi/rdf/sparql
                              https://publications.europa.eu/resource/celex/<CELEX>
ACCESS_METHOD:                API — SPARQL (JSON) + content negotiation HTTP
                              (Accept: application/xhtml+xml; Accept-Language: eng|fra|spa|ita)
CROPS:                        transversal — o ato define substância, não cultura
TOPICS:                       aprovação, renovação, alteração e retirada de substância ativa
                              (Reg. (CE) 1107/2009 e Reg. Exec. (UE) 540/2011)
GEOGRAPHIC_GRANULARITY:       UNIÃO EUROPEIA. Sem granularidade nacional/regional — e isso é
                              característica do fato, não limitação da fonte.
UPDATE_FREQUENCY:             contínua (cada edição do Jornal Oficial)
HISTORICAL_DEPTH:             todo o acervo CELEX
SOURCE_IDENTITY_PRESERVABLE:  SIM — CELEX + ELI + URI CELLAR
DOCUMENT_ID_AVAILABLE:        SIM — CELEX (ex.: 32026R1696), ELI, cellar UUID
PUBLICATION_DATE_AVAILABLE:   SIM — data do documento e data de publicação no JO
RAW_EVIDENCE_PRESERVABLE:     SIM — XHTML integral do ato, por língua
AUTOMATION_FEASIBILITY:       ALTA — endpoint público, sem chave, sem scraping de HTML
COLLECTION_FEASIBILITY:       ALTA — `scripts/cellar.sh` reproduz a coleta
LEGAL_OR_ACCESS_RISK:         BAIXO — legislação pública oficial; sem dado pessoal
REAL_EXAMPLE:                 CELEX 32026R1696 — Reg. Exec. (UE) 2026/1696, de 14/07/2026,
                              renova a aprovação da substância ativa ácido pelargônico
                              (CAS 112-05-0, CIPAC 888), pureza >= 889 g/kg,
                              aprovação 2026-10-01, expiração 2041-09-30.
                              Texto integral obtido em EN, FR, ES e IT.
ADAMA_USE_CASE:               REGULATORY e PORTFOLIO — saber, na data, que substância entra,
                              é renovada (e até quando) ou sai do mercado europeu.
EVIDENCE:                     data/samples/EU-T4-001/
                              (sparql-active-substance-2026.json, CELEX-32026R1696-eng.xhtml,
                               evidence-32026R1696.json com os 4 idiomas)
VERDICT:                      GREEN
```

**Nota de camada:** esta fonte é **EU ACTIVE SUBSTANCE**. Não diz nada sobre qual produto
está autorizado em França, Espanha ou Itália, nem em que cultura ou alvo. Confundir as duas
camadas seria o erro mais grave possível em T4.

#### EU-T4-002 · EU Pesticides Database (DG SANTE)

```
SOURCE_ID:                    EU-T4-002
SOURCE_NAME:                  EU Pesticides Database
SOURCE_OWNER:                 Comissão Europeia — DG SANTE
COUNTRY:                      EUROPE
LANGUAGE:                     EN (+ outras)
TERRITORY:                    T4
SOURCE_TYPE:                  Base de dados oficial consolidada (substâncias ativas, MRLs)
URL:                          https://ec.europa.eu/food/plant/pesticides/eu-pesticides-database/
ACCESS_METHOD:                aplicação Angular (SPA) + API JSON interna
                              (/api/subst/getSubstances) — observado, não obtido
GEOGRAPHIC_GRANULARITY:       NÃO SEI (não verificado)
RAW_EVIDENCE_PRESERVABLE:     NÃO SEI
AUTOMATION_FEASIBILITY:       NÃO SEI
COLLECTION_FEASIBILITY:       BLOQUEADO NESTE AMBIENTE
LEGAL_OR_ACCESS_RISK:         NÃO SEI / REQUER REVISÃO (termos de uso da API interna)
REAL_EXAMPLE:                 nenhum capturado
ADAMA_USE_CASE:               seria a visão consolidada de substância ativa + MRL
EVIDENCE:                     nenhuma — ver motivo abaixo
VERDICT:                      NÃO SEI
```

**Por que NÃO SEI e não RED:** todo acesso a `ec.europa.eu` a partir deste ambiente é
redirecionado para `sorry.ec.europa.eu` ("Server temporarily unavailable"), com e sem
User-Agent de navegador. O conteúdo também é renderizado por JavaScript, de modo que o
HTML servido não contém dados. **A fonte não foi avaliada — apenas não foi alcançada.**
Não é uma fonte ruim; é uma porta fechada *neste ambiente*.

**O que falta para resolver:** acesso de rede a `ec.europa.eu` ou execução com navegador
headless. **Não bloqueia T4**: EU-T4-001 cobre a camada de ato regulatório da UE com
qualidade superior (documento primário, identificável e datado, em vez de tabela derivada).

### T4 · REGULATORY — FRANCE

#### FR-T4-001 · ANSES E-Phy — catálogo francês de produtos fitofarmacêuticos

```
SOURCE_ID:                    FR-T4-001
SOURCE_NAME:                  Données ouvertes du catalogue E-Phy
SOURCE_OWNER:                 ANSES (Agence nationale de sécurité sanitaire) via data.gouv.fr
COUNTRY:                      FRANCE
REGION:                       nacional (a autorização é nacional; há ZNT e condições de emprego)
LANGUAGE:                     FR
TERRITORY:                    T4 (alimenta também T1, T3 e T9)
SOURCE_TYPE:                  Registro oficial de autorizações (AMM), dados abertos
URL:                          https://www.data.gouv.fr/datasets/donnees-ouvertes-du-catalogue-e-phy-des-produits-phytopharmaceutiques-matieres-fertilisantes-et-supports-de-culture-adjuvants-produits-mixtes-et-melanges
ACCESS_METHOD:                CSV e XML em ZIP, resolvidos pela API do data.gouv.fr.
                              Sem chave, sem scraping. `scripts/ephy.sh download`.
CROPS:                        todas as culturas do catálogo francês (Blé, Vigne, Orge, Maïs…)
TOPICS:                       produto, nº AMM, titular, substâncias ativas, função,
                              formulação, estado de autorização, data de retirada,
                              uso autorizado por cultura × alvo, dose, BBCH, DAR,
                              nº máx. de aplicações, ZNT (aquática, artrópodes, plantas)
GEOGRAPHIC_GRANULARITY:       PAÍS. Não há granularidade regional — a AMM é nacional.
UPDATE_FREQUENCY:             semanal (declarada e confirmada: versão de 2026-08-25)
HISTORICAL_DEPTH:             estado atual + datas de 1ª autorização e de retirada;
                              série histórica exige arquivar as versões semanais
SOURCE_IDENTITY_PRESERVABLE:  SIM — nº AMM é identificador oficial estável
DOCUMENT_ID_AVAILABLE:        SIM — numero AMM
PUBLICATION_DATE_AVAILABLE:   SIM — data da decisão por uso; versão datada do dataset
RAW_EVIDENCE_PRESERVABLE:     SIM — CSVs oficiais
AUTOMATION_FEASIBILITY:       ALTA
COLLECTION_FEASIBILITY:       ALTA — 3,9 MB comprimidos, ~41 MB abertos, 10 tabelas
LEGAL_OR_ACCESS_RISK:         BAIXO — Licence Ouverte (fr-lo). Sem dado pessoal:
                              o titular é pessoa jurídica.
REAL_EXAMPLE:                 15.140 produtos; 18.558 usos autorizados.
                              AMM 2080088 "NEMO" (ADAMA FRANCE SAS), nicosulfuron 40 g/L,
                              herbicida, uso Maïs*Désherbage, dose 1,5 L/ha,
                              ZNT aquática 20 m, decisão de 08/07/2014.
ADAMA_USE_CASE:               REGULATORY, PORTFOLIO, MARKET DEVELOPMENT, COMMERCIAL:
                              o que a ADAMA pode legalmente vender na França, em que
                              cultura, contra que alvo — e o mesmo para cada concorrente.
EVIDENCE:                     data/samples/FR-T4-001/
VERDICT:                      GREEN
```

**Descoberta lateral relevante:** o campo `titulaire` é público e nomeia as empresas.
**ADAMA FRANCE SAS** consta com **267 produtos** e **504 usos autorizados**. BAYER SAS (859),
BASF FRANCE SAS (420), SYNGENTA FRANCE SAS (349), DOW AGROSCIENCES (267), NUFARM (240).
Isso dá a T9 · COMPETITORS uma base **factual e oficial**, e não clipping — e resolve
parcialmente a pendência P-003 com informação pública inequívoca, sem inventar portfólio.

---

### T4 · REGULATORY — ITALY

#### IT-T4-001 · Ministero della Salute — Banca dati dei prodotti fitosanitari

```
SOURCE_ID:                    IT-T4-001
SOURCE_NAME:                  Fitosanitari — elenco dei prodotti fitosanitari autorizzati
SOURCE_OWNER:                 Ministero della Salute (Italia)
COUNTRY:                      ITALY
LANGUAGE:                     IT
TERRITORY:                    T4 (alimenta T9)
SOURCE_TYPE:                  Registro oficial de autorizações, dados abertos
URL:                          https://www.dati.salute.gov.it/it/dataset/fitosanitari/
                              arquivo: /sites/default/files/opendata/PROD_FTS_6_<AAAAMMDD>.csv
ACCESS_METHOD:                CSV direto (4,6 MB), sem chave
CROPS:                        NÃO PRESENTE neste arquivo — ver limitação abaixo
TOPICS:                       nº de registro, produto, empresa titular e sede, data de
                              registro, **data de vencimento da autorização**, indicações de
                              perigo, formulação, substâncias ativas, teor, importação
                              paralela, estado administrativo, **motivo e datas da revogação**
GEOGRAPHIC_GRANULARITY:       PAÍS (a sede da empresa traz província, mas é local da
                              EMPRESA — SOURCE_LOCATION —, nunca local do fato agronômico)
UPDATE_FREQUENCY:             o nome do arquivo é datado; versão obtida de 2026-08-24
HISTORICAL_DEPTH:             registros desde 1970 (o mais antigo observado: ENOVIT, 1970),
                              com estado atual, motivo e data de revogação
SOURCE_IDENTITY_PRESERVABLE:  SIM — num_registrazione
DOCUMENT_ID_AVAILABLE:        SIM
PUBLICATION_DATE_AVAILABLE:   SIM — data_registrazione, data_scadenza_autorizzazione,
                              data_decreto_revoca, data_decorrenza_revoca
RAW_EVIDENCE_PRESERVABLE:     SIM
AUTOMATION_FEASIBILITY:       MÉDIA-ALTA — o nome do arquivo muda a cada versão e precisa
                              ser descoberto na página do dataset
COLLECTION_FEASIBILITY:       ALTA
LEGAL_OR_ACCESS_RISK:         BAIXO — CC BY 4.0. Endereços são de pessoa jurídica.
REAL_EXAMPLE:                 17.695 produtos; 3.712 em vigor. ADAMA ITALIA S.R.L. com
                              155 autorizações de vencimento futuro — 58 nos próximos
                              6 meses. Reg. 008929 TOPIK 240 EC (clodinafop +
                              cloquintocet mexyl), vencimento 31/07/2027.
ADAMA_USE_CASE:               REGULATORY / PORTFOLIO: calendário de vencimentos do próprio
                              portfólio italiano e do de cada concorrente.
EVIDENCE:                     data/samples/IT-T4-001/
VERDICT:                      GREEN
```

**Limitação importante:** este arquivo **não traz cultura nem alvo**. Cultura e alvo estão no
rótulo (etichetta) de cada produto, que não faz parte deste dataset. Portanto a Itália
**não** sustenta hoje o mesmo cruzamento cultura × alvo que a França sustenta. O que a Itália
dá, e a França não dá, é a **data de vencimento por autorização**.

---

### T4 · REGULATORY — SPAIN

#### ES-T4-001 · MAPA — vocabulário oficial (jerarquía de cultivos e clasificación de plagas)

```
SOURCE_ID:                    ES-T4-001
SOURCE_NAME:                  Jerarquía de especies vegetales · Clasificación de plagas
SOURCE_OWNER:                 MAPA — Ministerio de Agricultura, Pesca y Alimentación
COUNTRY:                      SPAIN
LANGUAGE:                     ES + nome científico latino
TERRITORY:                    T4 (é infraestrutura para T1, T3 e para toda normalização)
SOURCE_TYPE:                  Tabelas de referência do Registro de Productos Fitosanitarios
URL:                          https://www.mapa.gob.es/dam/mapa/contenido/agricultura/temas/
                              sanidad-vegetal/medios-de-defensa-fitosanitaria/
                              registro-productos-fitosanitarios/{jerarquia,plagas}.xlsx
ACCESS_METHOD:                XLSX direto
TOPICS:                       hierarquia de espécies vegetais e classificação de pragas,
                              doenças, ervas daninhas e reguladores — **com código EPPO**
GEOGRAPHIC_GRANULARITY:       não aplicável (é vocabulário, não fato geográfico)
UPDATE_FREQUENCY:             NÃO SEI — o arquivo não declara periodicidade
SOURCE_IDENTITY_PRESERVABLE:  SIM
RAW_EVIDENCE_PRESERVABLE:     SIM
AUTOMATION_FEASIBILITY:       ALTA
COLLECTION_FEASIBILITY:       ALTA (74 KB + 119 KB)
LEGAL_OR_ACCESS_RISK:         BAIXO — publicação oficial. Sem dado pessoal.
REAL_EXAMPLE:                 813 espécies vegetais (710 com EPPO) e 1.395 linhas de pragas.
                              VITVI = Vitis vinifera; TRZAX = Triticum aestivum/durum;
                              PLASVI = "Mildiu de la vid, Plasmopara viticola";
                              SEPTTR = "Septoriosis del trigo, Zymoseptoria tritici";
                              GUIGBI = "Black rot… Phyllosticta ampelicida".
ADAMA_USE_CASE:               infraestrutura: é o que permite falar de "míldio da videira"
                              nos três países como sendo a mesma coisa.
EVIDENCE:                     data/samples/ES-T4-001/ (inclui eppo-dictionary.json derivado:
                              492 culturas e 1.381 pragas indexadas por código EPPO)
VERDICT:                      GREEN
```

#### ES-T4-002 · MAPA — Autorizaciones excepcionales (art. 53 Reg. 1107/2009)

```
SOURCE_ID:                    ES-T4-002
SOURCE_NAME:                  Autorizaciones excepcionales vigentes
SOURCE_OWNER:                 MAPA
COUNTRY:                      SPAIN
LANGUAGE:                     ES
TERRITORY:                    T4 (com leitura direta para T3 e para oportunidade de portfólio)
SOURCE_TYPE:                  Lista oficial de autorizações de emergência
URL:                          .../registro-productos-fitosanitarios/autorizaciones_excepcionales.xls
ACCESS_METHOD:                XLS (formato OLE2 legado, 32 MB; requer xlrd)
TOPICS:                       CULTIVO × PLAGA/FUNCIÓN × SUSTANCIA ACTIVA × PRODUCTO
                              COMERCIAL × data de início × data de fim
GEOGRAPHIC_GRANULARITY:       nacional, com exceções regionais explícitas quando existem
                              (ex.: "Extremadura: Tomate…")
UPDATE_FREQUENCY:             o próprio arquivo declara a data de situação (24/08/2026)
RAW_EVIDENCE_PRESERVABLE:     SIM
AUTOMATION_FEASIBILITY:       MÉDIA — .xls legado, cabeçalho em linha variável
COLLECTION_FEASIBILITY:       ALTA
LEGAL_OR_ACCESS_RISK:         BAIXO
REAL_EXAMPLE:                 45 autorizações excepcionais vigentes em 24/08/2026. Ex.:
                              Manzano y peral × fuego bacteriano (Erwinia amylovora);
                              Champiñón × telaraña (fluxapyroxad 30% SC);
                              Remolacha azucarera × pulgón (flonicamida 50% WG);
                              Fresal × desinfección del suelo (metam sodio 51% SL).
ADAMA_USE_CASE:               MARKET DEVELOPMENT / PORTFOLIO / R&D: uma autorização
                              excepcional é o Estado espanhol **declarando oficialmente que
                              não existe solução normal** para aquele problema naquela
                              cultura. É necessidade não atendida, documentada e datada.
EVIDENCE:                     data/samples/ES-T4-001/ES-T4-002-autorizaciones-excepcionales.json
VERDICT:                      GREEN
```

#### ES-T4-003 · MAPA — Registro de Productos Fitosanitarios (consulta)

```
SOURCE_ID:                    ES-T4-003
SOURCE_NAME:                  Registro de Productos Fitosanitarios — aplicação de consulta
SOURCE_OWNER:                 MAPA
COUNTRY:                      SPAIN
TERRITORY:                    T4
URL:                          https://www.mapa.gob.es/es/agricultura/temas/sanidad-vegetal/
                              productos-fitosanitarios/registro-productos
ACCESS_METHOD:                aplicação web de consulta. **Não foi encontrado** dump aberto
                              equivalente ao E-Phy francês ou ao CSV italiano.
COLLECTION_FEASIBILITY:       NÃO SEI — exigiria consulta form-a-form
LEGAL_OR_ACCESS_RISK:         NÃO SEI / REQUER REVISÃO — automatizar a consulta pode
                              conflitar com os termos de uso. Não foi tentado.
REAL_EXAMPLE:                 nenhum
VERDICT:                      NÃO SEI
```

**Consequência prática e assimetria a registrar:** os três países **não são simétricos** em T4.

| | produto | titular | cultura × alvo | data de vencimento | vocabulário EPPO |
|---|---|---|---|---|---|
| FRANCE (E-Phy) | ✅ | ✅ | ✅ | ❌ | ❌ (nomes comuns FR) |
| ITALY (Min. Salute) | ✅ | ✅ | ❌ | ✅ | ❌ |
| SPAIN (MAPA) | ❌ (só consulta) | — | ❌ | ❌ | ✅ |

Nenhuma comparação direta entre os três países é possível hoje sem declarar esta assimetria.
**Não** existe, até aqui, uma "visão EAME unificada de registro". Existem três visões
diferentes, com pontos fortes diferentes.

---

### Placar

| Recorte | GREEN | YELLOW | RED | NÃO SEI | Total |
|---|---|---|---|---|---|
| EUROPE | 1 | 0 | 0 | 1 | 2 |
| FRANCE | 1 | 0 | 0 | 0 | 1 |
| SPAIN | 2 | 0 | 0 | 1 | 3 |
| ITALY | 1 | 0 | 0 | 0 | 1 |
| **Total** | **5** | **0** | **0** | **2** | **7** |

### Cobertura por território

| | T1 | T2 | T3 | T4 | T5 | T6 | T7 | T8 | T9 | T10 | T11 | T12 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| EUROPE | – | – | – | 1G/1? | – | – | – | – | – | – | – | – |
| FRANCE | – | – | – | 1G | – | – | – | – | – | – | – | – |
| SPAIN | – | – | – | 2G/1? | – | – | – | – | – | – | – | – |
| ITALY | – | – | – | 1G | – | – | – | – | – | – | – | – |

*(– = não investigado)*
