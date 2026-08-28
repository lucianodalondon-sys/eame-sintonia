# ATLAS DE FONTES — SINTONIA EAME

Catálogo de tudo que conseguimos **realmente** observar em França, Espanha, Itália e na
camada comum europeia.

> Este atlas registra **fontes**, não desejos. Uma linha só existe aqui depois que alguém
> abriu a fonte, olhou o que ela entrega e guardou evidência disso.

**Estado:** MISSÃO 02 em curso — **20 fontes registradas** (10 GREEN, 2 YELLOW, 8 NÃO SEI).
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

**Por que NÃO SEI e não RED:** a chamada à API interna
(`/api/subst/getSubstances`) é redirecionada para `sorry.ec.europa.eu`
("Server temporarily unavailable"), com e sem User-Agent de navegador, em duas tentativas
separadas com intervalo. O conteúdo também é renderizado por JavaScript, de modo que o HTML
servido não contém dados. **A fonte não foi avaliada — apenas não foi alcançada.**

**Correção registrada (não apagada):** a primeira leitura desta investigação foi
*"todo `ec.europa.eu` está inacessível deste ambiente"*. **Isso estava errado.** Verificou-se
depois que `ec.europa.eu/eurostat/...` responde normalmente (ver EU-T1-001 e EU-T1-002) e que
a própria página da aplicação de pesticidas devolve HTTP 200. O que falha é **o caminho da
API interna**, não o domínio. A hipótese ampla caiu; a conclusão sobre esta fonte
permanece NÃO SEI.

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

### T1 · CROP & PRODUCTION — EUROPE

#### EU-T1-001 · Eurostat `apro_cpshr` — produção vegetal por região NUTS 2

```
SOURCE_ID:                    EU-T1-001
SOURCE_NAME:                  Crop production in EU standard humidity by NUTS 2 region
SOURCE_OWNER:                 Eurostat
COUNTRY:                      EUROPE (cobre FR, ES, IT e demais)
LANGUAGE:                     EN (+ DE, FR)
TERRITORY:                    T1
SOURCE_TYPE:                  Estatística oficial europeia
URL:                          https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/apro_cpshr
ACCESS_METHOD:                API REST, JSON-stat 2.0, sem chave
CROPS:                        79 rubricas (trigo comum, cevada, milho grão, beterraba…)
TOPICS:                       área, área principal, produção colhida, rendimento, umidade
GEOGRAPHIC_GRANULARITY:       **NUTS 2 para ÁREA. Apenas PAÍS para RENDIMENTO.** Medido:
                              ver a limitação abaixo — é a descoberta mais importante aqui.
UPDATE_FREQUENCY:             anual (fonte declarou atualização em 2026-05-28)
HISTORICAL_DEPTH:             **2000–2024, 25 anos** verificados para FR/ES/IT
SOURCE_IDENTITY_PRESERVABLE:  SIM
DOCUMENT_ID_AVAILABLE:        SIM — código do dataset + dimensões
PUBLICATION_DATE_AVAILABLE:   SIM — campo `updated`
RAW_EVIDENCE_PRESERVABLE:     SIM
AUTOMATION_FEASIBILITY:       ALTA
COLLECTION_FEASIBILITY:       ALTA
LEGAL_OR_ACCESS_RISK:         BAIXO — política de reutilização do Eurostat, sem dado pessoal
REAL_EXAMPLE:                 5.685 valores NUTS2 para FR/ES/IT, 2000–2024.
                              Trigo comum 2024: ES41 Castilla y León 771,8 mil ha;
                              FRB0 Centre–Val de Loire 544,6; FRE2 Picardie 472,0.
                              Cevada 2024: ES42 Castilla-La Mancha 702,7 mil ha.
ADAMA_USE_CASE:               MD / COMMERCIAL / EAME: onde estão de fato as culturas,
                              em que região, com que peso e com que evolução em 25 anos.
EVIDENCE:                     data/samples/EU-T1-001-nuts2-crop-area.json
VERDICT:                      GREEN
```

**Limitação medida — e ela derruba uma suposição óbvia:** o dataset se chama *"by NUTS 2
region"*, mas **o rendimento (YLD) não existe em NUTS 2 para nenhum país** — testado em 2021,
2022, 2023 e 2024, resultado zero regiões. Só **área** desce a NUTS 2 (253 regiões na UE, 67
em FR/ES/IT). Quem assumir "Eurostat dá produtividade regional" está errado.

#### EU-T1-002 · Eurostat `apro_cpsh1` — produção vegetal por país

```
SOURCE_ID:                    EU-T1-002
SOURCE_NAME:                  Crop production in EU standard humidity
SOURCE_OWNER:                 Eurostat
COUNTRY:                      EUROPE
TERRITORY:                    T1
ACCESS_METHOD:                API REST JSON-stat, sem chave
GEOGRAPHIC_GRANULARITY:       PAÍS
UPDATE_FREQUENCY:             fonte declarou atualização em 2026-08-17
HISTORICAL_DEPTH:             2010–2026 (ES já com 2026; FR e IT até 2025)
RAW_EVIDENCE_PRESERVABLE:     SIM
AUTOMATION_FEASIBILITY:       ALTA
LEGAL_OR_ACCESS_RISK:         BAIXO
REAL_EXAMPLE:                 rendimento de trigo comum (t/ha):
                              FR 2023 7,28 → **2024 6,02** → 2025 7,34
                              ES 2022 3,07 → **2023 2,14** → 2024 3,74 → 2025 4,51
                              IT 2021 6,26 → 2024 5,03 → 2025 5,02
ADAMA_USE_CASE:               leitura de ano bom e ano ruim por país, série longa
EVIDENCE:                     data/samples/EU-T1-002-wheat-yield-country.json
VERDICT:                      GREEN
```

#### Fontes nacionais de T1 — não alcançadas nesta rodada

| ID | Fonte | Situação | Motivo medido |
|---|---|---|---|
| FR-T1-001 | Agreste — Statistique agricole annuelle (SAA) | **NÃO SEI** | `agreste.agriculture.gouv.fr` falhou por TLS via curl e devolveu **HTTP 503** por outra rota de saída. Indisponibilidade do próprio site, não decisão sobre a fonte. |
| IT-T1-001 | ISTAT — coltivazioni (SDMX) | **NÃO SEI** | `esploradati.istat.it` não respondeu no tempo limite; `sdmx.istat.it` devolveu 302 sem conteúdo. |
| ES-T1-001 | MAPA — Estadística Anual de Superficies y Producciones | **NÃO SEI** | localizados apenas os *esquemas de conceitos* no datos.gob.es, não a série. |

Nenhuma delas é RED: **não foram avaliadas, foram apenas não alcançadas**. Não bloqueiam T1,
porque EU-T1-001 já entrega área por NUTS 2 com 25 anos para os três países.

---

### T2 · CLIMATE / WATER / SOIL — EUROPE

#### EU-T2-001 · NASA POWER — série climática diária por ponto

```
SOURCE_ID:                    EU-T2-001
SOURCE_NAME:                  NASA POWER — Daily Point (community AG)
SOURCE_OWNER:                 NASA Langley Research Center
COUNTRY:                      global (aplicado a EUROPE, FRANCE, SPAIN, ITALY)
LANGUAGE:                     EN
TERRITORY:                    T2
SOURCE_TYPE:                  reanálise climática servida por API
URL:                          https://power.larc.nasa.gov/api/temporal/daily/point
ACCESS_METHOD:                API REST JSON, **sem chave, sem cadastro**
TOPICS:                       T2M_MAX, T2M_MIN, PRECTOTCORR (precipitação corrigida),
                              RH2M e demais parâmetros agroclimáticos
GEOGRAPHIC_GRANULARITY:       **PONTO (lat/lon)** — resolução nativa da reanálise.
                              **Não é média regional.** Ver a ressalva abaixo.
UPDATE_FREQUENCY:             diária, com defasagem de poucos dias
HISTORICAL_DEPTH:             décadas (verificado 2020–2024 sem falha)
RAW_EVIDENCE_PRESERVABLE:     SIM — JSON por ponto e período
AUTOMATION_FEASIBILITY:       ALTA
COLLECTION_FEASIBILITY:       ALTA — uma chamada cobre anos inteiros
LEGAL_OR_ACCESS_RISK:         BAIXO — dado público da NASA. Sem dado pessoal.
REAL_EXAMPLE:                 ES41 Castilla y León (ponto-rótulo NUTS2): chuva de
                              fevereiro a abril — 2020: 170,9 mm · 2021: 142,3 ·
                              2022: 120,5 · **2023: 34,9** · 2024: 142,2 mm.
ADAMA_USE_CASE:               TECHNICAL / MD: exposição climática por região e por janela
                              fenológica, com série histórica, em qualquer ponto dos 3 países.
EVIDENCE:                     data/samples/X-001-nuts2-heat-vs-wheat.json
                              data/samples/CASE-006-es41-rain-window-vs-yield.json
VERDICT:                      GREEN
```

**Ressalva de geografia — obrigatória em qualquer tela:** o valor é de **um ponto**, não da
região. Nós usamos o *ponto-rótulo* NUTS 2 do GISCO (EU-T2-002) como representante da região.
Castilla y León tem 94 mil km²; um ponto não a representa inteira. Isto é uma **aproximação
declarada**, não uma média regional — e precisa aparecer assim no protótipo.

#### EU-T2-002 · GISCO — pontos-rótulo das regiões NUTS 2

```
SOURCE_ID:                    EU-T2-002
SOURCE_NAME:                  NUTS_LB_2024_4326_LEVL_2 (label points)
SOURCE_OWNER:                 Eurostat / GISCO
COUNTRY:                      EUROPE
TERRITORY:                    T2 (infraestrutura geográfica para T1, T2 e T3)
ACCESS_METHOD:                GeoJSON direto, sem chave
GEOGRAPHIC_GRANULARITY:       NUTS 2 — 299 pontos
RAW_EVIDENCE_PRESERVABLE:     SIM
AUTOMATION_FEASIBILITY:       ALTA
LEGAL_OR_ACCESS_RISK:         BAIXO
REAL_EXAMPLE:                 ES41 (−4,788 / 41,751) · FRB0 (1,684 / 47,485) ·
                              FRE2 (2,808 / 49,642) · ITC1 (7,923 / 45,060)
ADAMA_USE_CASE:               é o que liga estatística agrícola e clima na mesma geografia
VERDICT:                      GREEN
```

#### EU-T2-003 · Open-Meteo (arquivo ERA5)

```
SOURCE_ID:                    EU-T2-003
SOURCE_NAME:                  Open-Meteo Historical Weather API (ERA5)
ACCESS_METHOD:                API REST, sem chave, com **cota diária por IP**
COLLECTION_FEASIBILITY:       **NÃO TESTÁVEL HOJE NESTE AMBIENTE**
REAL_EXAMPLE:                 nenhum
VERDICT:                      NÃO SEI
```

**Motivo:** a API respondeu `429 — "Daily API request limit exceeded"` já na primeira
chamada, porque a cota é por IP e este ambiente sai por IP compartilhado. A fonte é real,
gratuita e provavelmente muito boa; **não foi avaliada**. EU-T2-001 (NASA POWER) cobre a
mesma necessidade sem cota observada, então isto **não bloqueia T2**.

---

### T3 · PEST / DISEASE / WEEDS — SPAIN

#### ES-T3-001 · RAIF — Red de Alerta e Información Fitosanitaria de Andalucía

```
SOURCE_ID:                    ES-T3-001
SOURCE_NAME:                  Datos de seguimiento de plagas y enfermedades en las
                              estaciones de control biológico [2006–2026]
SOURCE_OWNER:                 Junta de Andalucía — Consejería de Agricultura, Pesca,
                              Agua y Desarrollo Rural
COUNTRY:                      SPAIN (Andalucía)
REGION:                       províncias e municípios andaluzes
LANGUAGE:                     ES
TERRITORY:                    T3 (com leitura para T1 e T2)
SOURCE_TYPE:                  rede oficial de monitoramento em campo, dados abertos
URL:                          https://www.juntadeandalucia.es/datosabiertos/portal/dataset/raif
ACCESS_METHOD:                CKAN API + ZIP com XML. **Atenção:** a URL de download que a
                              API devolve aponta para `gdc-pdpopendata-ckan.paas.junta-
                              andalucia.es`, host que este ambiente não alcança (502 no
                              CONNECT). Trocando o host por `www.juntadeandalucia.es`,
                              o mesmo caminho baixa normalmente. Registrado porque é a
                              diferença entre a fonte "não funcionar" e funcionar.
CROPS:                        10 culturas — olivar, cítricos, vid, fresa, arroz, algodón,
                              almendro, cereales de invierno, hortícolas, remolacha
TOPICS:                       parcelas (com coordenadas), amostragens por data, fenologia,
                              incidência de pragas e doenças **em percentual medido**,
                              armadilhas de feromônio, tratamentos fitossanitários
GEOGRAPHIC_GRANULARITY:       **PARCELA** — código de parcela, município, comarca,
                              zona homogênea, coordenadas UTM e altitude.
                              É a granularidade mais fina encontrada em toda a missão.
UPDATE_FREQUENCY:             semanal (visor); dataset atualizado em 2026-08-26
HISTORICAL_DEPTH:             2006–2026 conforme a cultura (vid desde 2017)
SOURCE_IDENTITY_PRESERVABLE:  SIM — CODPARCELA + FECHA
DOCUMENT_ID_AVAILABLE:        SIM
PUBLICATION_DATE_AVAILABLE:   SIM — data de cada amostragem
RAW_EVIDENCE_PRESERVABLE:     SIM — XML original
AUTOMATION_FEASIBILITY:       ALTA (XML com nomes de campo codificados em `_x0020_`)
COLLECTION_FEASIBILITY:       ALTA — vid 3,9 MB; olivar 57 MB
LEGAL_OR_ACCESS_RISK:         BAIXO — CC BY 4.0. **Atenção GDPR:** há coordenadas de
                              parcela. São parcelas de monitoramento de agrupamentos
                              técnicos, não cadastro de produtor identificado — mas o
                              uso de coordenadas precisa de revisão antes de publicação.
                              `NÃO SEI / REQUER REVISÃO` para difusão externa.
REAL_EXAMPLE:                 Vid 2026: 639 amostragens em Cádiz, Córdoba e Huelva.
                              Campos medidos incluem "1601 Mildiu: % cepas afectadas",
                              "1701 Oidio: % cepas afectadas", "0401 Lobesia: nº adultos/
                              trampa feromona y día" e "1604 Mildiu: condiciones
                              favorables (0=No; 1=Si)".
ADAMA_USE_CASE:               TECHNICAL / MD / COMMERCIAL: pressão real de doença por
                              cultura, por província e por semana — não opinião de campo.
EVIDENCE:                     data/samples/ES-T3-001-raif-vid-mildiu-2026.json
                              data/samples/X-001-completo-mildiu-vs-clima.json
VERDICT:                      GREEN
```

**Esta é a fonte mais rica encontrada na missão inteira.** Ela mede o que as outras apenas
regulam ou contextualizam: a doença, no campo, em percentual, por parcela e por semana.

---

### T3 · PEST / DISEASE / WEEDS — FRANCE

#### FR-T3-001 · Bulletins de Santé du Végétal (BSV) — sistema vivo

```
SOURCE_ID:                    FR-T3-001
SOURCE_NAME:                  Bulletins de Santé du Végétal
SOURCE_OWNER:                 rede de epidemiovigilância — DRAAF, Chambres d'agriculture,
                              institutos técnicos (ARVALIS, ITB…), dados no Vigicultures®
COUNTRY:                      FRANCE
REGION:                       por região administrativa
LANGUAGE:                     FR
TERRITORY:                    T3
SOURCE_TYPE:                  boletim oficial de vigilância fitossanitária
ACCESS_METHOD:                **PDF por região e por setor**, publicado em sites de DRAAF,
                              câmaras de agricultura, institutos e na base documental do
                              Ecophytopic. Não foi encontrada API nem dump aberto.
GEOGRAPHIC_GRANULARITY:       região (por vezes com detalhe sub-regional no texto)
UPDATE_FREQUENCY:             semanal na safra
HISTORICAL_DEPTH:             anos, dispersos por site
RAW_EVIDENCE_PRESERVABLE:     SIM (o PDF)
AUTOMATION_FEASIBILITY:       **BAIXA** — descentralizada, sem formato comum, conteúdo em
                              texto corrido dentro de PDF. Coletar exigiria varredura de
                              dezenas de sites, o que esta missão **proíbe** (§16, sem
                              scraping agressivo).
LEGAL_OR_ACCESS_RISK:         publicação pública e gratuita; `NÃO SEI / REQUER REVISÃO`
                              quanto a reuso sistemático.
REAL_EXAMPLE:                 Hauts-de-France — BSV Grandes Cultures n°32 de 25/08/2026 e
                              BSV Pommes de Terre n°27 de 27/08/2026 (publicação ARVALIS
                              para a rede regional). Verificado em 28/08/2026: um dia de
                              defasagem.
ADAMA_USE_CASE:               TECHNICAL: leitura semanal de pressão por região e cultura.
                              Alto valor de conteúdo, alto custo de coleta.
VERDICT:                      YELLOW
```

**Assimetria estrutural França × Espanha em T3:** a França publica **texto interpretado por
especialista, semanal e regional**. A Andaluzia publica **medida numérica por parcela**. As
duas são de altíssima qualidade e **não são comparáveis**: uma dá julgamento, a outra dá
número. Qualquer tela que as coloque lado a lado precisa dizer isso.

#### FR-T3-002 · Corpus histórico de BSV (arquivo em agroecologia)

```
SOURCE_ID:                    FR-T3-002
SOURCE_NAME:                  Archive en agro-écologie de BSV
SOURCE_OWNER:                 publicado em data.gouv.fr (licença CC-BY), origem pestobserver.eu
COUNTRY:                      FRANCE
TERRITORY:                    T3
ACCESS_METHOD:                ZIP (OCR, 173 MB) e RAR de amostra (14,9 MB)
HISTORICAL_DEPTH:             **40.899 documentos**, com parte de 1960 a 2000
                              (OCR declarado de qualidade média nesse período)
COLLECTION_FEASIBILITY:       **NÃO CONSEGUIDA NESTA RODADA** — o download em
                              `static.data.gouv.fr` foi cortado (`Connection reset by peer`;
                              o proxy registrou `ws_closed_mid_exchange` após 7 s), tanto no
                              pacote OCR quanto na amostra. O mesmo host serviu o E-Phy
                              (3,9 MB) sem problema, então o corte parece ligado ao volume
                              ou ao recurso, não ao domínio.
REAL_EXAMPLE:                 nenhum capturado
LEGAL_OR_ACCESS_RISK:         BAIXO (CC-BY)
VERDICT:                      NÃO SEI
```

**O que falta:** uma rota de download que suporte o volume. **Não bloqueia T3** — a fonte é
histórica (última atualização em 2023) e o valor operacional está em FR-T3-001, que é vivo.

---

### T3 · PEST / DISEASE / WEEDS — ITALY e EUROPE

#### IT-T3-001 · Bollettini di produzione integrata (Emilia-Romagna e consórcios provinciais)

```
SOURCE_ID:                    IT-T3-001
SOURCE_OWNER:                 Regione Emilia-Romagna — Servizio fitosanitario;
                              Consorzi Fitosanitari Provinciali (Reggio Emilia, Modena…)
COUNTRY:                      ITALY
REGION:                       província
LANGUAGE:                     IT
TERRITORY:                    T3
ACCESS_METHOD:                PDF semanal por província, em caminho previsível
GEOGRAPHIC_GRANULARITY:       província
UPDATE_FREQUENCY:             semanal na safra
REAL_EXAMPLE:                 "Bollettino 15 del 21 maggio 2026 — Reggio Emilia",
                              publicado no portal da Regione Emilia-Romagna
                              (bollettini interprovinciali di produzione integrata e
                              biologica 2026).
AUTOMATION_FEASIBILITY:       MÉDIA — PDF, mas com nomenclatura e caminho regulares
LEGAL_OR_ACCESS_RISK:         `NÃO SEI / REQUER REVISÃO` para reuso sistemático
ADAMA_USE_CASE:               TECHNICAL: recomendação oficial de defesa por província
VERDICT:                      YELLOW
```

**Cobertura parcial declarada:** foi verificada **uma** região italiana (Emilia-Romagna).
A Itália tem 20 regiões, cada uma com seu próprio serviço fitossanitário. O que se sabe é
que **existe** sistema regional publicado; **não se sabe** a cobertura nacional. Tratar
Emilia-Romagna como "a Itália" seria erro grosseiro.

#### EU-T3-001 · EPPO Global Database

```
SOURCE_ID:                    EU-T3-001
SOURCE_NAME:                  EPPO Global Database
SOURCE_OWNER:                 European and Mediterranean Plant Protection Organization
COUNTRY:                      EUROPE
TERRITORY:                    T3 (e vocabulário para todos)
URL:                          https://gd.eppo.int  ·  API: https://data.eppo.int/api/rest/1.0/
ACCESS_METHOD:                site HTML acessível (HTTP 200). **API REST devolveu
                              `403 — "You do not have sufficent rights"`**: exige token
                              de conta EPPO, que não temos.
REAL_EXAMPLE:                 nenhum capturado pela API
LEGAL_OR_ACCESS_RISK:         requer cadastro; termos não avaliados
VERDICT:                      NÃO SEI
```

**O que falta:** uma conta EPPO e seu token. **Decisão necessária** — é um cadastro
institucional gratuito, mas é uma conta em nome de alguém. Registrado em PERGUNTAS
PENDENTES como P-006. **Não bloqueia:** o vocabulário EPPO de que precisamos já veio,
por outro caminho, em ES-T4-001.

---

### Placar

| Recorte | GREEN | YELLOW | RED | NÃO SEI | Total |
|---|---|---|---|---|---|
| EUROPE | 5 | 0 | 0 | 3 | 8 |
| FRANCE | 1 | 1 | 0 | 2 | 4 |
| SPAIN | 3 | 0 | 0 | 2 | 5 |
| ITALY | 1 | 1 | 0 | 1 | 3 |
| **Total** | **10** | **2** | **0** | **8** | **20** |

### Cobertura por território

| | T1 | T2 | T3 | T4 | T5 | T6 | T7 | T8 | T9 | T10 | T11 | T12 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| EUROPE | 2G | 3G/1? | 1? | 1G/1? | – | – | – | – | – | – | – | – |
| FRANCE | 1? | – | 1Y/1? | 1G | – | – | – | – | – | – | – | – |
| SPAIN | 1? | – | **1G** | 2G/1? | – | – | – | – | – | – | – | – |
| ITALY | 1? | – | 1Y | 1G | – | – | – | – | – | – | – | – |

*(– = não investigado)*
