# ATLAS DE FONTES — SINTONIA EAME

Catálogo de tudo que conseguimos **realmente** observar em França, Espanha, Itália e na
camada comum europeia.

> Este atlas registra **fontes**, não desejos. Uma linha só existe aqui depois que alguém
> abriu a fonte, olhou o que ela entrega e guardou evidência disso.

**Estado:** atualizado em 2026-09-06 — **<!--M:SOURCE_ID_COUNT-->39<!--/M--> fontes registradas** (19 GREEN, 4 YELLOW, 16 NÃO SEI).
**Última atualização:** 2026-08-29

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
| **T9** | COMPETITORS | BASF, Bayer, Syngenta, Corteva, FMC, UPL, Nufarm + outros descobertos como relevantes. **Duas camadas separadas: RESPOSTA REGISTRADA (registro oficial) e ATIVAÇÃO OBSERVADA (comunicação e Meta Ads Library)** — nunca fundidas |
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

### Separação obrigatória em T9

**RESPOSTA REGISTRADA** e **ATIVAÇÃO OBSERVADA** são camadas distintas e não podem ser
misturadas. Registro é ato administrativo, datado e verificável; ativação é observação de
atividade pública. Um concorrente pode ter registro e nenhuma atividade observada, e o
inverso também acontece. A ficha declara em qual camada está, e a camada de ativação
declara qual dos quatro estados:

`COMPETITOR_REGISTERED_RESPONSE` · `COMPETITOR_PAID_META_ACTIVITY` ·
`COMPETITOR_PUBLIC_COMMUNICATION` · `COMPETITOR_TECHNICAL_ACTIVITY` · `NOT_KNOWN`

Contrato completo: `data/samples/EAME-COMPETITOR-CONTRACT-V1.json`.

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


<!-- PASSO 03 · fichas portadas de claude/sintonia-italy-pilot-b1l401. O enxerto trouxe
     coletor e evidencia destas quatro fontes; deixa-las sem ficha punha dado no repo sem
     fonte documentada, que e o inverso da regra deste atlas. -->

#### IT-T4-001-ETICHETTA · Ministero della Salute — etichetta autorizzata

```
SOURCE_ID:                    IT-T4-001-ETICHETTA
SOURCE_OWNER:                 Ministero della Salute (Italia)
COUNTRY:                      ITALY
TERRITORY:                    T4 (alimenta T3 e T9)
ACCESS_METHOD:                POST FitosanitariServlet ACTION=cercaProdotti
                              NUMERO_REGISTRAZIONE=<reg com zeros à esquerda>
                              -> HTML traz EtichettaServlet?id=<ID_INTERNO>
                              -> GET dessa URL devolve o PDF
CROPS:                        SIM — é justamente o que o CSV não tem
TOPICS:                       cultura, alvo com nome científico, dose, volume,
                              intervalo entre tratamentos, nº máx. de aplicações,
                              intervalo de segurança, grupo HRAC/FRAC/IRAC
PUBLICATION_DATE_AVAILABLE:   SIM — a data vem no nome do arquivo servido
                              (`15232_etichettaCLP_29042022.pdf`)
AUTOMATION_FEASIBILITY:       MÉDIA — ver os três defeitos da fonte abaixo
LEGAL_OR_ACCESS_RISK:         BAIXO — documento oficial público
REAL_EXAMPLE:                 CUSTODIA ULTRA (reg. 015232), rótulo de 29/04/2022:
                              tabela com grano tenero/duro, orzo, cetriolo, melone,
                              pomodoro, vite e alvos (Fusarium, Erysiphe, Puccinia,
                              Septoria, Uncinula) com dose e nº de aplicações.
EVIDENCE:                     data/samples/IT-T4-001/IT-T4-001-etichette-manifest.json
VERDICT:                      GREEN COM RESSALVAS OPERACIONAIS
```

**Três defeitos DA FONTE, medidos. São ficha de saúde, não motivo de abandono:**

1. **Cadeia TLS incompleta** — o host envia só a folha, sem o intermediário
   `TI Trust Technologies OV CA`. `curl` recusa, e recusa com razão. A correção **não** é
   desligar verificação: é buscar o intermediário no campo AIA do próprio certificado.
2. **Cabeçalho `Public-Key-Pins` malformado** (linha partida, sem `:`) — `curl` aborta com
   *Header without colon*; o parser do Python tolera. A rota é Python por medição.
3. **Uma busca por sessão** — reusar o `JSESSIONID` devolve **vazio**, não erro. Vazio de
   estrangulamento é indistinguível de vazio de inexistência. Sessão nova por consulta,
   com retentativa: `NO_LABEL_LINK` só se publica depois de esgotadas as tentativas, e
   **nunca** significa "o rótulo não existe" — na primeira passada 14 registros ficaram
   sem rótulo e a maioria foi recuperada **só por esperar mais**.

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
SUPERSEDED_BY:                ES-T4-005 (MISSÃO 07). O veredito acima fica registrado como
                              estava: era o que sabíamos, e estava errado por falta de
                              leitura, não por a fonte ser fechada.
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

> **A tabela acima foi corrigida na MISSÃO 07.** A linha SPAIN estava errada: o registro
> espanhol entrega produto, titular, **fabricante**, planta, formulado, estado, datas e
> cultura × alvo. A linha corrigida está na ficha `ES-T4-005`, abaixo.

---

#### ES-T4-005 · MAPA — ROPF, rotas públicas da aplicação oficial

```
SOURCE_ID:                    ES-T4-005
SOURCE_NAME:                  Registro Oficial de Productos Fitosanitarios — rotas públicas
SOURCE_OWNER:                 MAPA — D.G. de Sanidad de la Producción Agroalimentaria
COUNTRY:                      SPAIN
TERRITORY:                    T4
URL:                          https://servicio.mapa.gob.es/regfiweb/
ACCESS_METHOD:                as rotas que o próprio frontend chama, declaradas em texto
                              aberto na página (<input type="hidden">) e em
                              /regfiweb/js/site.min.js:
                                GET  Productos/ProductosGrid?NumRegistro=&Titular=&IdEstado=
                                GET  Productos/GetProductoById?idProducto=N
                                GET  Productos/ExportFichaProductoPdfGet?idProducto=N
                                POST Exportaciones/ExportJsonProductos  (dataDto[...])
                              Cliente: scripts/mapa_regfi.py
UPDATE_FREQUENCY:             semanal — a página declara a data da última atualização da
                              base ("viernes, 28 de agosto de 2026 14:00")
FORMAT:                       HTML (grade) · JSON (ficha e export) · PDF (ficha oficial)
FIELDS:                       numRegistro · nombre · titular · fabricante · fabrica ·
                              formulado · estado · tramite · estadoTramite · fechas
                              (inscripción, caducidad, renovación, modificación, límite de
                              venta) · observaciones · usos e cultivos (na ficha PDF)
COVERAGE:                     3.084 registros (1.993 vigentes · 1.091 cancelados)
COLLECTION_FEASIBILITY:       ALTA e EDUCADA — o export devolve o conjunto filtrado inteiro
                              numa requisição; não é preciso paginar a grade
LEGAL_OR_ACCESS_RISK:         BAIXO — nenhuma autenticação contornada, nenhuma
                              vulnerabilidade usada, nenhuma carga: um POST substitui
                              centenas de páginas. RISCO REAL: não é dataset publicado,
                              logo a rota pode mudar sem aviso. Arquivar cada versão.
REAL_EXAMPLE:                 ES-01717 · SORATEL MAX · titular ADAMA Agriculture España S.A.
                              · fabricante ADAMA Agricultural Solutions Ltd. · planta
                              (Neot Hovav) · azoxistrobina 20% + protioconazol 15% ·
                              Vigente · cebada, centeno, trigo, triticale
EVIDENCE:                     data/samples/ES-T4-005-ficha-primaria-es01717.json
                              data/samples/ES-T4-005-denominadores-ropf.json
VERDICT:                      GREEN
```

**Assimetria T4, corrigida:**

| | produto | titular | fabricante | cultura × alvo | vencimento | rota |
|---|---|---|---|---|---|---|
| FRANCE (E-Phy) | ✅ | ✅ | ❌ | ✅ | ❌ | **dump aberto** |
| SPAIN (ROPF) | ✅ | ✅ | ✅ | ✅ (ficha PDF) | ✅ | rota da aplicação |
| ITALY (Min. Salute) | ✅ | ✅ | ❌ | ❌ | ✅ | consulta web |

A assimetria que resta **não é de conteúdo, é de rota**: só a França publica um dump com
garantia de estabilidade. Espanha e Itália dependem de rotas que podem mudar. **Isso muda o
risco, não a qualidade do fato.**

**Divergência resolvida na MISSÃO 08.** A grade dava `1.998/1.086` e o export `1.993/1.091`,
com o mesmo total de 3.084. A regra:

```
IdEstado=1 ("VIGENTE") == Estado == 'Vigente'
                          OR (Estado == 'Cancelado' AND fechaLimiteVenta >= hoje)
```

Os cinco da diferença — `16192`, `25454`, `ES-00195`, `ES-01106`, `ES-01107` — são
**cancelados dentro do prazo legal de escoamento**. O **filtro** responde *"ainda pode ser
vendido?"*; o **campo** responde *"a autorização está em vigor?"*. Os dois números estão
certos e respondem perguntas diferentes; publicar um sem dizer qual é o erro. E `1.998`
**tem data de validade**: cai sozinho em 03 e 30/09/2026.

Contrato operacional completo desta fonte: `../operacao/CONTRATOS-DAS-FONTES-EAME.md`.

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
| IT-T1-001 | ISTAT — coltivazioni (SDMX) | **RESOLVIDA no P0.2 · PASSO 03 — hoje GREEN, ficha em `T1 · CROP & PRODUCTION — ITALY`** | Medição de então, preservada: `esploradati.istat.it` não respondeu no tempo limite e `sdmx.istat.it` devolveu 302 sem conteúdo. **Aquilo não era ausência da fonte, era ausência da rota** — o enxerto trouxe a rota SDMX que responde, `scripts/italia_istat.py` e a evidência. |
| ES-T1-001 | MAPA — Estadística Anual de Superficies y Producciones | **NÃO SEI** | localizados apenas os *esquemas de conceitos* no datos.gob.es, não a série. |

Nenhuma delas é RED: **não foram avaliadas, foram apenas não alcançadas**. Não bloqueiam T1,
porque EU-T1-001 já entrega área por NUTS 2 com 25 anos para os três países.

> **A linha do ISTAT ficou.** Uma fonte que passou de `NÃO SEI` a `GREEN` não apaga a rodada em
> que não foi alcançada: apagar o registro faria a régua parecer sempre certa. `NOT_REACHED ≠
> DOES NOT EXIST`, e a prova disso é a própria linha ter mudado de estado sem ser removida.

---

### T1 · CROP & PRODUCTION — ITALY

<!-- PASSO 03 · ficha portada de claude/sintonia-italy-pilot-b1l401. O enxerto trouxe
     coletor e evidencia desta fonte; deixa-la sem ficha punha dado no repo sem fonte
     documentada, que e o inverso da regra deste atlas. -->

#### IT-T1-001 · ISTAT — Coltivazioni: superfici e produzione

```
SOURCE_ID:                    IT-T1-001
SOURCE_OWNER:                 ISTAT
COUNTRY:                      ITALY
TERRITORY:                    T1
ACCESS_METHOD:                SDMX REST, CSV/JSON, sem chave
                              dataflow IT1,101_1015_DF_DCSP_COLTIVAZIONI_1,1.0
GEOGRAPHIC_GRANULARITY:       PAÍS · REGIÃO · PROVÍNCIA
CROPS:                        inclui OLIVEIRA e VIDEIRA — que o Eurostat NÃO dá em NUTS 2
REAL_EXAMPLE:                 2024: videira 588,8 mil ha (Sicilia 120,2 · Veneto 101,0 ·
                              Puglia 79,1); oliveira 1.113,7 (Puglia 347,8 · Calabria
                              184,7 · Sicilia 161,7)
VERDICT:                      GREEN
```

**Por que ela importa:** o Eurostat não publica `O1000` nem `W1000` em NUTS 2. Sem o ISTAT,
as duas maiores culturas permanentes da Itália ficam sem geografia — e sem geografia não há
caso regional.

**A armadilha, e ela não dá erro.** O ISTAT codifica regiões em **NUTS 2006**; o Eurostat em
**NUTS 2021**. `ITD3` é Vêneto no primeiro e `ITH3` no segundo. Cruzar pela chave literal
devolve um resultado **menor e plausível**: somem `ITD*` e `ITE*`, ou seja todo o Nord-Est e
todo o Centro — Vêneto e Emilia-Romagna, justamente as que mais importam para milho e
videira. O sintoma foi a soma NUTS 2 do milho dar 261,3 mil ha contra 495,4 nacionais.
Com o mapeamento: 495,2 (100,0 %). O mapa vive em `scripts/italia_istat.py`.

**Validação cruzada:** milho 495,4 = 495,4 · trigo duro 1.177,4 = 1.177,4 · trigo mole
520,3 = 520,3 contra o Eurostat. **Idênticos**, porque é o mesmo dado — o Eurostat republica
o que o ISTAT apura. Videira **não** bate (588,8 × 715,8): definições diferentes, e os dois
números não se trocam.

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

<!-- PASSO 03 · ficha portada de claude/sintonia-italy-pilot-b1l401. O enxerto trouxe
     coletor e evidencia destas fontes; deixa-las sem ficha punha dado no repo sem fonte
     documentada, que e o inverso da regra deste atlas. -->

#### IT-T3-006 · ERSA Friuli-Venezia Giulia — bollettini colture erbacee

```
SOURCE_ID:                    IT-T3-006
SOURCE_OWNER:                 ERSA — Servizio fitosanitario e chimico, FVG
COUNTRY:                      ITALY · REGION: Friuli-Venezia Giulia
ACCESS_METHOD:                PDF em caminho previsível, texto extraível
UPDATE_FREQUENCY:             semanal na safra
REAL_EXAMPLE:                 "Boll_15_MAIS_120826" — mais em BBCH 65-75, voo de 3ª
                              geração de piralide, limiar publicado (>3 ovaturas/100
                              plantas; larvas em 30-40% de 50-100 espigas)
VERDICT:                      GREEN
```

**É a única série de boletim de MILHO medida na Itália** — 10 números em 2026, sob difesa
integrata obbligatoria (art. 19 D.lgs. 150/2012). Foi encontrada só na segunda rodada,
porque na primeira eu li a página-mãe das *colture erbacee* e não a subpágina
`bollettini-2026`. `NOT_FOUND ≠ DOES NOT EXIST`, e a diferença era um clique.

#### IT-T3-LOTTA · Decretos regionais de lotta obbligatoria (flavescência dourada)

```
SOURCE_ID:                    IT-T3-LOTTA-OBBLIGATORIA
SOURCE_OWNER:                 Regione Lombardia · Regione del Veneto
TERRITORY:                    T3 (alimenta T4 e T9)
ACCESS_METHOD:                PDF do ato + bollettini semanais
REAL_EXAMPLE:                 Lombardia, Comunicato Giunta 25/05/2026 n. 39 (BURL 28/05):
                              2 tratamentos, 2–14/06 e 17–29/06.
                              Vêneto, DDR n. 13645 de 14/05/2026: datas NÃO no ato,
                              delegadas ao boletim semanal (8–19/06 na integrada).
VERDICT:                      GREEN
```

**As duas regiões não publicam do mesmo jeito**, e quem tratar "o calendário italiano" como
uma coisa só vai errar em uma das duas: a Lombardia resolve num documento, o Vêneto exige
dois — e o segundo muda toda semana.

**A regra de elegibilidade liga a norma ao portfólio:** a Lombardia admite exclusivamente
produtos cujo rótulo traga como alvo `«cicaline della vite»` ou `«Scaphoideus titanus»`.
É um critério que se avalia **contra o texto da etichetta**, e por isso `IT-T4-001-ETICHETTA`
é pré-requisito desta ficha.

#### IT-T3-002 · Servizio fitosanitario della Regione del Veneto — bollettini di difesa integrata

```
SOURCE_ID:                    IT-T3-002
SOURCE_OWNER:                 Regione del Veneto — U.O. Fitosanitario
COUNTRY:                      ITALY · REGION: Veneto
LANGUAGE:                     IT
TERRITORY:                    T3
ACCESS_METHOD:                PDF semanal, uma série por cultura (vite, olivo, frutticolo,
                              orticolo), numerada e datada no nome do arquivo
                              (`vite_19_130826.pdf` = n. 19 de 13/08/2026)
GEOGRAPHIC_GRANULARITY:       região, com sub-áreas nomeadas dentro do boletim
UPDATE_FREQUENCY:             semanal na safra
PUBLICATION_DATE_AVAILABLE:   SIM — número e data no cabeçalho e no nome do arquivo
RAW_EVIDENCE_PRESERVABLE:     SIM — os PDFs estão no repositório
REAL_EXAMPLE:                 VITE n. 19 de 13/08/2026: adulto da cicalina presente; videiras
                              com sintomas de Giallumi devem ser capitozzate ou estirpate;
                              trocar as armadilhas cromotrópicas a cada duas semanas.
                              OLIVO n. 29 de 02/09/2026: inolizione — inizio invaiatura.
EVIDENCE:                     data/samples/IT-ARPAV-VENETO/ (6 PDFs + texto extraído) ·
                              data/samples/IT-FONTES/ITALY-SOURCE-PROBE.json (HTTP 200, 30/08/2026)
VERDICT:                      GREEN
```

**Esta ficha existia como dado antes de existir como fonte.** `IT-T3-002` já era citado como
perna de CAMPO do `IT-HERO-001` (videira × flavescência) e do `IT-DEMO-001` (oliveira ×
*Bactrocera oleae*) com **conteúdo citado e datado**, e o atlas não o registrava. Era dado
publicado órfão de fonte documentada — o inverso da regra deste atlas. Sondado e fichado no
P0.2 · PASSO 03, contra os PDFs preservados.

**Ressalva de dono, e ela é fácil de errar:** o mesmo diretório de evidência guarda o
**BOLLETTINO AGROMETEOROLOGICO REGIONALE** da **ARPAV** (`boll_agro_settimanale.pdf`) e as
séries das estações agrometeorológicas. **Outro dono, outra série, outro território.**
`AGROMETEO != FITOSANITARIO`: o boletim de cultura é do Servizio fitosanitario e cita a
ARPAV como colaboradora do bloco meteorológico — citar não é publicar.

#### IT-T3-LAMMA · Consorzio LaMMA (Regione Toscana / CNR) — bollettino fitosanitario provincial

```
SOURCE_ID:                    IT-T3-LAMMA
SOURCE_OWNER:                 Consorzio LaMMA — Regione Toscana / CNR
COUNTRY:                      ITALY · REGION: Toscana
TERRITORY:                    T3
ACCESS_METHOD:                HTML por província. **Não existe PDF desta série** — os dois
                              PDFs linkados na página são fichas de peronospora e oídio da
                              VIDEIRA, outros documentos
GEOGRAPHIC_GRANULARITY:       província
PUBLICATION_DATE_AVAILABLE:   SIM — a data está no título da seção
RAW_EVIDENCE_PRESERVABLE:     SIM — HTML íntegro, 25.680 bytes,
                              sha256 93527b546eefc271283251356abb7ec22a0d0d277895e9e5881888d9f0ae356a
REAL_EXAMPLE:                 Grosseto, «Bolletino Frumento del 2026-04-23»: o duro «si colloca
                              tra piena fioritura e inizio fioritura» e há «la comparsa di
                              sintomi lievi» de fusariose — sintoma OBSERVADO, não modelado
EVIDENCE:                     data/samples/IT-T3-LAMMA/grosseto-ftsnt-2026-04-23.html ·
                              manifesto IT-T3-LAMMA-grosseto-2026-04-23.json (sha256 reconferido do disco)
VERDICT:                      GREEN
```

**Defeito DA FONTE, medido: a página é rolante.** Encerrada a campanha, a última edição fica
exposta e as anteriores saem. A série é **FORWARD-ONLY**: o que não for arquivado no dia
deixa de existir. Por isso os bytes estão no repositório e o hash é reconferível —
`scripts/italia_preservar_lamma.py --verify` recalcula do disco e do remoto. **Reconstruir de
memória seria proibido**, e não foi preciso: a rota devolveu o mesmo sha256 em duas coletas.

#### IT-T3-OP · organizações de produtores olivícolas — sinal de campo fora do serviço regional

```
SOURCE_ID:                    IT-T3-OP
SOURCE_OWNER:                 Assoprol Umbria · APOL (Lecce) · +2 sondadas
COUNTRY:                      ITALY · REGION: Umbria e Puglia
TERRITORY:                    T3
ACCESS_METHOD:                bollettino próprio da organização, fora do portal regional
REAL_EXAMPLE:                 Assoprol Umbria, «Bollettino Fitosanitario Olivo 2026 —
                              Monitoraggio mosca delle olive n. 3», válido de 6 a 10 de julho
                              de 2026, território regional: capturas em armadilha, fenologia
                              BBCH 71-75 e recomendação
COVERAGE:                     4 sondadas · **1 CONTENT_READ** · 1 EXISTS_NOT_READABLE
EVIDENCE:                     data/samples/IT-FONTES/ITALY-OP-FIELD-LAYER.json
VERDICT:                      YELLOW — uma de quatro lida
```

**A lei que esta camada acrescentou: `SOURCE_LAYER != SIGNAL_ABSENCE`.** Publicámos que «a
Puglia tem 31,2 % da área de oliveira e publica ZERO boletins». O que sobrevive: o **serviço
regional** da Puglia publica zero, e a inversão contra o Vêneto (28 boletins com 0,5 % da
área) continua de pé **como comparação entre serviços regionais**. O que **não** sobrevive é a
leitura «na Puglia não há sinal de olivo»: há, e sai da organização de produtores — a APOL de
Lecce mantém série numerada semanal de mosca-da-azeitona, com edições de 2026. Medir a camada
estatal e concluir ausência é perguntar à **instituição errada dentro da região certa**.

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

### T5 · SCIENCE e T6 · RESEARCHERS — EUROPE

#### EU-T5-001 · OpenAlex — grafo bibliográfico aberto

```
SOURCE_ID:                    EU-T5-001
SOURCE_NAME:                  OpenAlex
SOURCE_OWNER:                 OurResearch (organização sem fins lucrativos)
COUNTRY:                      global — filtrável por país de afiliação
LANGUAGE:                     EN (metadados)
TERRITORY:                    T5 e T6 (e parcialmente T7, pela instituição)
SOURCE_TYPE:                  agregador bibliográfico aberto
URL:                          https://api.openalex.org/works
ACCESS_METHOD:                REST JSON, **sem chave**; *polite pool* via `mailto`
TOPICS:                       trabalho, ano, DOI, autores, afiliações, instituições,
                              país da afiliação, tópicos
GEOGRAPHIC_GRANULARITY:       **país da afiliação do autor** — não é o país do experimento.
                              Ver a ressalva de geografia abaixo.
UPDATE_FREQUENCY:             contínua
HISTORICAL_DEPTH:             décadas
SOURCE_IDENTITY_PRESERVABLE:  SIM — DOI e ID OpenAlex por trabalho e por autor
DOCUMENT_ID_AVAILABLE:        SIM (DOI)
PUBLICATION_DATE_AVAILABLE:   SIM (ano)
RAW_EVIDENCE_PRESERVABLE:     SIM
AUTOMATION_FEASIBILITY:       ALTA — **com limite de taxa**: `429 Too Many Requests`
                              observado em rajada. Exige recuo entre chamadas.
COLLECTION_FEASIBILITY:       ALTA
LEGAL_OR_ACCESS_RISK:         BAIXO na licença. **GDPR: são pessoas identificadas.**
                              Nome, instituição e produção são públicos e profissionais,
                              mas qualquer perfilamento de pessoa exige revisão —
                              `NÃO SEI / REQUER REVISÃO` (P-008).
REAL_EXAMPLE:                 "Quem trabalha repetidamente com resistência a herbicidas na
                              França?" → **Christophe Délye (9 trabalhos, Agroécologie/INRAE
                              Dijon, 2019–2023)**, Valérie Le Corre (6), Séverine Michel (5),
                              Fanny Pernin (4) — os quatro no mesmo laboratório.
                              "Que pesquisadores aparecem ligados a doenças da videira na
                              Itália?" → **Silvia Laura Toffolatti (17, Università di Milano)**,
                              Michele Perazzolli (12, Fondazione Edmund Mach),
                              Giuliana Maddalena (11, Milano), Vittorio Rossi
                              (10, Università Cattolica del Sacro Cuore).
ADAMA_USE_CASE:               R&D / TECHNICAL / MD: quem realmente produz conhecimento sobre
                              um problema agronômico específico, em que instituição e desde
                              quando — para parceria, ensaio, consulta técnica e antena.
EVIDENCE:                     data/samples/EU-T5-001-openalex-people.json
VERDICT:                      GREEN
```

#### ES-T5-002 · OpenAlex — corpus científico espanhol de olivar e sanidade vegetal

```
SOURCE_ID:                    ES-T5-002
SOURCE_NAME:                  OpenAlex, recorte espanhol declarado
DERIVA_DE:                    EU-T5-001 (mesma fonte, mesma rota, recorte próprio)
COUNTRY:                      SPAIN — filtro institutions.country_code:es
TERRITORY:                    T5 e T6
ACCESS_METHOD:                REST JSON, sem chave — **rota gratuita e REPLICÁVEL**
SEARCH_UNIVERSE:              12 temas declarados, cada um com CROP e ISSUE explícitos
YEARS:                        2019–2026
COLLECTION_FEASIBILITY:       ALTA
DOCUMENT_ID_AVAILABLE:        SIM — id OpenAlex em 1.771 de 1.771; DOI em 99,5%
RAW_EVIDENCE_PRESERVABLE:     SIM — data/raw/ES-T5-002/openalex_works.json (não versionado,
                              D-003: a rota é gratuita, a cadeia refaz o bruto)
CONTRATO_DE_CAMPOS:           os 16 campos da §7 da REGRA DE COLETA EXTERNA.
                              14 acima de 99%. Dois incompletos **com motivo escrito**:
                              MOLECULE 0,6% (o corpus foi buscado por patógeno, não por
                              substância) e REGION_OF_STUDY 0% (não existe campo; a
                              afiliação NÃO é o local do experimento).
TIPOS_COBERTOS:               article 1.598 · preprint 109 · conference-paper 17 ·
                              book-chapter 15 · review 10 · editorial 8 · dataset 3
TIPOS_NÃO_COBERTOS:           technical report · research project · institutional
                              publication · extension material — **NOT_REACHED declarado**,
                              não dados por cobertos
DERIVADOS:                    152 pesquisadores (era 153: um id de autor conflacionado,
                              com 58 organizações contra mediana 2, foi excluído) ·
                              380 instituições · 9.958 autores distintos
LEGAL_OR_ACCESS_RISK:         **GDPR: pessoas identificadas.** Entram apenas campos que a
                              própria pessoa publicou como identidade acadêmica.
EVIDENCE:                     data/samples/ES-T5-002-corpus-documentos.json
                              data/samples/ES-RESEARCHERS-OLIVE.json
DATA_CLOCK:                   SIM — no manifesto desde 2026-08-29
VERDICT:                      GREEN
```

**Por que esta ficha existe:** a auditoria adversarial de 2026-08-29 apontou que a camada que
entrega 152 pesquisadores, o corpus e as instituições **não tinha ficha de fonte** — logo não
tinha contrato de campos, não tinha registro de versão e não tinha `ACCESS_METHOD` auditável.
A camada existia; a ficha, não.

---

**Ressalva de geografia (obrigatória):** `authorships.countries:FR` significa **afiliação
francesa**, não pesquisa feita na França. Um trabalho sobre trigo australiano assinado por um
coautor de Montpellier entra no filtro. `SOURCE_LOCATION` e `FACT_LOCATION` **não coincidem**
nesta fonte, e essa é a sua limitação estrutural.

**Ponte descoberta entre territórios:** a **Fondazione Edmund Mach**, que aparece em T5 como
instituição do segundo pesquisador italiano mais recorrente em míldio da videira, é a mesma
instituição que publica os *Bollettini Difesa integrata* do Trentino, registrada em T3.
Ciência e rede técnica se encontram na mesma organização — é o primeiro elo real de
PERSON → ORGANIZATION → TOPIC → DOCUMENT do people graph.

---

### T10 · MARKET / TRADE — EUROPE

#### EU-T10-001 · Agri-food Data Portal — preços semanais de cereais por mercado

```
SOURCE_ID:                    EU-T10-001
SOURCE_NAME:                  European Commission — Agri-food Data Portal (cereal prices)
SOURCE_OWNER:                 Comissão Europeia — DG AGRI
COUNTRY:                      EUROPE (com detalhe FR, ES, IT)
LANGUAGE:                     EN
TERRITORY:                    T10
SOURCE_TYPE:                  série oficial de preços de mercado
URL:                          https://www.ec.europa.eu/agrifood/api/cereal/prices
ACCESS_METHOD:                REST JSON, **sem chave**
                              (parâmetros: memberStateCodes, years, beginDate)
CROPS:                        trigo panificável, trigo duro, cevada forrageira,
                              milho forrageiro, entre outros
TOPICS:                       preço, unidade, semana, mercado, estágio comercial
GEOGRAPHIC_GRANULARITY:       **MERCADO NOMEADO** dentro do país — mais fino que país.
                              ES 17 mercados (Albacete, Burgos, Ciudad Real, Huesca…),
                              IT 16 (Alessandria, Bologna, Foggia, Grosseto…),
                              FR 6 (Bordeaux, La Pallice, Rhin, Port-La-Nouvelle…)
UPDATE_FREQUENCY:             **semanal** — verificado com dado da semana de 17–23/08/2026
HISTORICAL_DEPTH:             consultável por ano
SOURCE_IDENTITY_PRESERVABLE:  SIM — estado, mercado, produto e semana
PUBLICATION_DATE_AVAILABLE:   SIM — beginDate, endDate, referencePeriod
RAW_EVIDENCE_PRESERVABLE:     SIM
AUTOMATION_FEASIBILITY:       ALTA
COLLECTION_FEASIBILITY:       ALTA — 2.562 registros numa chamada
LEGAL_OR_ACCESS_RISK:         BAIXO
REAL_EXAMPLE:                 Milho forrageiro em Mantova (IT), semana de 17–23/08/2026:
                              **€243,50/t**, saída de fazenda.
                              Trigo panificável, média nacional: FR €234,30/t (30/07/2026)
                              e IT €219,31/t (06/08/2026). Trigo duro: FR €267,50 ×
                              IT €271,83.
ADAMA_USE_CASE:               COMMERCIAL / EAME / MD: capacidade de pagamento do produtor e
                              atratividade relativa da cultura, por país e por praça.
EVIDENCE:                     data/samples/EU-T10-001-cereal-prices.json
VERDICT:                      GREEN
```

#### Outras fontes de T10 testadas

| ID | Fonte | Situação | Motivo medido |
|---|---|---|---|
| EU-T10-002 | FAOSTAT (API) | **NÃO SEI** | devolveu `401 — Missing Authorization Header`. Passou a exigir credencial. |
| EU-T10-003 | Eurostat `ext_lt_maineu` (comércio) | **NÃO SEI** | a API responde 200, mas a consulta feita voltou com `value` vazio. Faltou acertar as dimensões — **não foi avaliada**, foi mal consultada. |

---

### T9 · COMPETITORS — camada de comunicação

#### FR/ES/IT-T9-001 · Sites e canais de comunicação dos concorrentes

```
SOURCE_ID:                    FR-T9-001 / ES-T9-001 / IT-T9-001 (mesma natureza)
SOURCE_NAME:                  páginas de atualidades de BASF, Bayer, Syngenta, Corteva…
COUNTRY:                      FRANCE · SPAIN · ITALY
TERRITORY:                    T9
ACCESS_METHOD:                site institucional
COLLECTION_FEASIBILITY:       **BLOQUEADA NESTA RODADA**
REAL_EXAMPLE:                 nenhum
VERDICT:                      NÃO SEI
```

**Motivo medido:** `syngenta.fr/actualites` → **403** (proteção anti-robô);
`agriculture.basf.fr` → **502 no CONNECT** (não alcançado deste ambiente);
`corteva.it/notizie.html` → **404** (caminho inválido). Nenhum dos três foi lido.

**Consequência para o cruzamento X-003** (COMPETITOR + PRODUCT + CROP + COMMUNICATION):
a perna COMMUNICATION **não existe hoje**. E vencer esse bloqueio exigiria varredura de
sites com proteção anti-robô, que a §16 desta missão proíbe.

**O que isto significa — e é uma conclusão de valor, não uma falha:** a inteligência
competitiva defensável sobre os concorrentes na EAME hoje vem do **registro oficial**
(X-005, COMPROVADO: quem tem direito de uso em cada cultura × alvo, com que molécula),
e **não** de clipping de comunicação. O caminho difícil é justamente o que a missão
mandava não fazer; o caminho fácil já está provado.

#### EU-T9-002 · META ADS LIBRARY — fonte estratégica nomeada, **não testada**

```
SOURCE_ID:                    EU-T9-002 (uma ficha, quatro recortes: EU · ES · IT · FR)
SOURCE_NAME:                  Meta Ads Library
SOURCE_OWNER:                 Meta Platforms
COUNTRY:                      EUROPE · SPAIN · ITALY · FRANCE
TERRITORY:                    T9 (alimenta a camada COMPETITOR ACTIVATION)
SOURCE_TYPE:                  registro público de peça publicitária paga
ACCESS_METHOD:                NÃO SEI — rota não executada nesta rodada
REAL_EXAMPLE:                 nenhum
EVIDENCE:                     data/samples/EAME-COMPETITOR-CONTRACT-V1.json
VERDICT:                      NÃO SEI · **NÃO TESTADO**
```

**Por que ela ganha ficha própria em vez de virar mais uma linha em "social media":**
ela é a única fonte identificada até aqui que registra **peça publicitária paga com
anunciante identificado e datas**. Isso é outra natureza de dado — não é um canal a mais.

**Ela não é a Meta Graph API.** O que este repositório já mediu é a Graph API
(`EU-T8-001`, **400 sem token**), que serve para conteúdo orgânico de perfis e exige App
Review. A Ads Library é outra rota, para outro fim, e **nunca foi aberta aqui**. Por isso
o veredito é `NÃO TESTADO` e **não** `RED` — e muito menos `AUSENTE_MEDIDO`.

**O que ela poderia observar:** anunciante · país · página · produto quando identificável
na peça · cultura · problema · claim · criativo · first observed · last observed ·
ativo/inativo quando a fonte permitir · repetição de mensagem · mudança de comunicação ·
**quantidade de peças OBSERVADAS**.

**O que ela prova:** `ATIVAÇÃO PUBLICITÁRIA OBSERVADA`. Só isso.

| não prova | |
|---|---|
| `META AD ≠ SALES` | `META AD ≠ MARKET SHARE` |
| `META AD ≠ CAMPAIGN SUCCESS` | `META AD ≠ STOCK` |
| `META AD ≠ PRODUCT AVAILABILITY` | `META AD ≠ INVESTIMENTO` |

**Denominador obrigatório:** toda contagem de peças viaja com o que foi consultado —
quais anunciantes, qual país, qual período, qual termo. *"A Syngenta tem 14 anúncios"*
sem isso é um número sem denominador.

**O que ela fecharia:** `X-003` (COMPETITOR + PRODUCT + CROP + COMMUNICATION) está
`NÃO COMPÕE` desde a MISSÃO 02 porque a perna COMMUNICATION não existe. Esta é a primeira
rota candidata a essa perna que **não** depende de varrer site com proteção anti-robô.

**Risco a medir antes de qualquer uso:** se o anunciante aparece como a empresa ou como
uma agência, a chave de casamento com o titular de registro muda inteira — e casar nome
de empresa entre bases diferentes já é o problema conhecido do `X-011`.

---

### T8 · FARMERS & INFLUENCERS

```
SOURCE_ID:                    EU-T8-001 (avaliação de rota de acesso, não de fonte única)
TERRITORY:                    T8
VERDICT:                      NÃO SEI · parcialmente NÃO TESTÁVEL AINDA
```

**Rotas testadas e resultado medido:**

| Rota | Resultado | Leitura |
|---|---|---|
| YouTube Data API v3 | **403** sem chave | exige chave de API |
| **YouTube RSS por `channel_id`** | **200**, 15 entradas, com `published` e estatísticas de visualização | **funciona sem chave** |
| YouTube RSS por `user=` | 404 | rota antiga, desativada |
| Instagram / Meta Graph API | 400 sem token | exige token e App Review |
| TikTok Research API | 404 sem token | exige credencial de pesquisa aprovada |

**A descoberta precisa:** o gargalo de T8 **não é a coleta, é a descoberta**. Com o
`channel_id` em mãos, o RSS público do YouTube entrega títulos, datas e estatísticas sem
chave nenhuma. O que não existe é uma forma legítima de **descobrir quais canais importam**
sem a API de busca (que exige chave) ou sem varredura da plataforma (proibida pela §16).

**Consequência para a separação exigida pela missão** (REACH · FIELD AUTHORITY ·
TECHNICAL AUTHORITY · COMMERCIAL INFLUENCE): apenas **REACH** seria mensurável por esta rota,
e ainda assim só depois de alguém decidir a lista de canais. **FIELD AUTHORITY**,
**TECHNICAL AUTHORITY** e **COMMERCIAL INFLUENCE** não têm, hoje, nenhuma fonte de dado
identificada nesta missão. Registrado como lacuna real, não como capacidade futura.

**Decisão necessária (P-009):** obter chave da YouTube Data API e definir se a ADAMA quer
perfilar pessoas em redes sociais — o que traz questão de GDPR distinta da de T5, porque
aqui há criadores individuais e não apenas autoria científica.

---

#### ATUALIZAÇÃO 2026-08-29 — o gargalo da descoberta foi resolvido para a Espanha

O diagnóstico acima continua correto sobre as rotas **gratuitas**. Ele foi superado por
**rotas de coleta pagas**, com o custo medido e declarado em
`../operacao/RELATORIO-DE-ROTAS-APIFY-ES.md`.

| SOURCE_ID | camada | origens | estado |
|---|---|---:|---|
| `ES-T8-001` | YouTube | 157 canais · 252 vídeos · 15 transcrições | **PROVED** |
| `ES-T8-002` | LinkedIn | 202 perfis · 179 declaram ES | **PROVED** (identidade) · PARCIAL (conteúdo) |
| `ES-T8-003` | Instagram | 32 contas agronômicas | **FAILED_WITH_REASON** |

**A separação que a missão original exigia agora existe** — e não da forma prevista:

- **REACH** é mensurável, e **foi deliberadamente excluído** de toda definição de papel.
  O termo canônico é `PUBLIC_TECHNICAL_VOICE`. **`INFLUENCER = AUTHORITY` não existe no
  modelo.**
- **TECHNICAL AUTHORITY** passou a ter fonte: papel declarado em campos estruturados
  (`companyType`, `pageType`, `industries`, `headline`, cargo atual). Cobertura medida:
  **67%**, com `AMBIGUOUS` e `NOT_DECLARED` visíveis.
- **FIELD AUTHORITY** continua **sem fonte**. Nada aqui mede o que uma voz sabe do campo.
- **COMMERCIAL INFLUENCE** continua **sem fonte**.

**O que o Instagram ensinou, e vale para qualquer plataforma futura:** 39 de 60 itens eram
agronômicos e mesmo assim a rota foi reprovada, porque **24 de 32 contas não declaram país
nenhum** e a hashtag `#repilo` está inteiramente ocupada por um homônimo comercial
britânico. **Volume não compensa identidade ausente.**

**A questão de GDPR de P-009 permanece aberta e agora é concreta:** existem pessoas físicas
identificadas na base. Só entraram campos que a própria pessoa publicou como identidade
profissional, e nenhum dado de contato foi coletado — o modo de scraping sem e-mail foi o
escolhido em todas as execuções.

---

### T7 · TECHNICAL NETWORK — SPAIN

#### ES-T7-001..027 · Mídia técnica, associações e rede de assessores

```
SOURCE_ID:                    ES-T7-001..027
SOURCE_NAME:                  feeds de imprensa técnica espanhola, associações agrárias,
                              e origens de assessoria técnica identificadas no LinkedIn
COUNTRY:                      SPAIN
TERRITORY:                    T7
ACCESS_METHOD:                PUBLIC APPLICATION ROUTE (RSS/Atom) · rota paga de plataforma
COLLECTION_FEASIBILITY:       PARCIAL — 8 de 18 rotas de feed provadas
REAL_EXAMPLE:                 Oleo Revista, 50 itens datados, 29 on-topic
VERDICT:                      PARCIAL
```

**Nenhuma destas rotas é documentada como API pública.** São **PUBLIC APPLICATION ROUTE**.

**HTTP 200 não bastou:** seis rotas devolveram **200 com zero `<item>`** — são páginas HTML.
Registradas como `FAILED_WITH_REASON`, não como fontes vivas.

**Três certificados não validam** (CITOLIVA, COAG, eComercio Agrario). Registrado como
**estado da fonte**. A verificação de certificado **não** foi desligada.

Evidência: `../../data/samples/ES-VOICE-MEDIA-ROUTES.json`

---

### T12 · POLICY / AGRICULTURAL ENVIRONMENT — EUROPE

#### EU-T12-001 · CELLAR / Jornal Oficial — atos de política agrícola (mesma fonte de EU-T4-001)

```
SOURCE_ID:                    EU-T12-001
SOURCE_NAME:                  CELLAR / EU Publications Office — camada de política agrícola
SOURCE_OWNER:                 Publications Office of the European Union
COUNTRY:                      EUROPE
TERRITORY:                    T12
ACCESS_METHOD:                **a mesma infraestrutura já provada em EU-T4-001** —
                              SPARQL + content negotiation. Muda apenas a consulta.
                              `./scripts/cellar.sh sparql "<consulta>"`
TOPICS:                       PAC, condicionalidade, ecoesquemas, restrições, sustentabilidade
GEOGRAPHIC_GRANULARITY:       UNIÃO EUROPEIA
UPDATE_FREQUENCY:             contínua
HISTORICAL_DEPTH:             todo o acervo CELEX
RAW_EVIDENCE_PRESERVABLE:     SIM
AUTOMATION_FEASIBILITY:       ALTA
LEGAL_OR_ACCESS_RISK:         BAIXO
REAL_EXAMPLE:                 CELEX 32026R0148 e 32026R0149, ambos de 21/01/2026, alterando
                              regulamentos de execução e delegado da **política agrícola
                              comum**.
ADAMA_USE_CASE:               EAME / COUNTRY / REGULATORY: mudanças de política que afetam
                              o produtor antes de afetarem o mercado.
EVIDENCE:                     mesma cadeia de EU-T4-001; consulta registrada em scripts/cellar.sh
VERDICT:                      GREEN
```

**Descoberta de eficiência:** T12 **não precisou de fonte nova**. A mesma infraestrutura de
T4 responde à política agrícola — muda o filtro do título, não o acesso. Isto reduz o custo
de duas famílias a um único conector.

---

### T11 · EVENTS

```
SOURCE_ID:                    IT-T11-001 (EIMA) · FR-T11-001 (Vinitech-SIFEL)
TERRITORY:                    T11
ACCESS_METHOD:                site institucional do evento (HTML)
VERDICT:                      YELLOW
```

**Alcance medido:** `eima.it` **200** · `vinitech-sifel.com` **200** ·
`fimazaragoza.com` **502 no CONNECT** · `fruitattraction.com` **502**. Dois dos quatro
grandes eventos testados são alcançáveis deste ambiente; dois não.

**REAL_EXAMPLE:** **EIMA International**, 47ª edição, **10–14 de novembro de 2026**, Bologna
(IT), com catálogo de expositores publicado on-line e planta do salão disponível.

**Por que YELLOW e não GREEN:** existe informação real, datada e verificável — data, edição,
local e lista de expositores. Mas **não há formato estruturado**: nem API, nem calendário
padronizado, nem catálogo em dado aberto. Montar um EVENT RADAR exigiria tratar cada evento
como um caso, com o site de cada um mudando a cada edição. É viável e de baixo risco
jurídico, mas de manutenção alta e de valor menor que T3, T4 e T5.

**O que T11 poderia entregar e ainda não foi testado:** o catálogo de expositores da EIMA
cruzaria com T9 (quais concorrentes estão presentes, com que estande) e com T6 (que
pesquisadores participam do programa científico). É um cruzamento **plausível e não testado**.

---

### T13 · DISTRIBUTION — FRANCE

*(território novo, aberto na MISSÃO 03 porque a apresentação promete DISTRIBUTION como
camada de inteligência — DECK-008 e DECK-021 — e T1–T12 não a cobriam)*

#### FR-T13-001 · Annuaire des Entreprises — base SIRENE aberta

```
SOURCE_ID:                    FR-T13-001
SOURCE_NAME:                  recherche-entreprises.api.gouv.fr (base SIRENE)
SOURCE_OWNER:                 DINUM / INSEE (França)
COUNTRY:                      FRANCE
LANGUAGE:                     FR
TERRITORY:                    T13
SOURCE_TYPE:                  registro oficial de empresas, dados abertos
URL:                          https://recherche-entreprises.api.gouv.fr/search
ACCESS_METHOD:                REST JSON, **sem chave**, filtrável por código NAF
TOPICS:                       razão social, SIREN, departamento, comuna, faixa de efetivo,
                              data de criação, atividade principal
GEOGRAPHIC_GRANULARITY:       **comuna** — a mais fina de qualquer fonte da missão para
                              entidades. É a sede da empresa, não a área que ela atende.
UPDATE_FREQUENCY:             contínua (base SIRENE)
HISTORICAL_DEPTH:             data de criação por empresa
RAW_EVIDENCE_PRESERVABLE:     SIM
AUTOMATION_FEASIBILITY:       ALTA (observado corte de conexão em rajada; exige recuo)
LEGAL_OR_ACCESS_RISK:         BAIXO — Licence Ouverte. Pessoas jurídicas.
REAL_EXAMPLE:                 NAF **46.21Z** (atacado de grãos, sementes e alimentos para
                              animais): **4.646 empresas**. Entre as maiores da amostra:
                              OCEALIA, SOUFFLET AGRICULTURE, VIVESCIA, AXEREAL, NATUP,
                              ARTERRIS, OXYANE, CAVAC — as grandes cooperativas francesas.
                              NAF **46.75Z** (atacado de produtos químicos): **4.251
                              empresas**, com BRENNTAG, BASF FRANCE e GIVAUDAN na amostra.
ADAMA_USE_CASE:               COMMERCIAL / MD: mapa de quem distribui e onde — a rede que
                              está entre a ADAMA e o produtor.
EVIDENCE:                     data/samples/FR-T13-001-distribution.json
VERDICT:                      GREEN
```

**O que esta fonte NÃO dá — e o deck promete:** volume distribuído, catálogo de produtos,
mudanças de catálogo, acordos comerciais e culturas atendidas. Ela dá **a rede**, não o
**fluxo**. Afirmar volume a partir daqui seria inventar (DECK-021, failure mode).

**Espanha e Itália — registrados como não alcançados:**

| ID | Fonte pretendida | Situação | Motivo |
|---|---|---|---|
| ES-T13-001 | registro mercantil / cooperativas agroalimentares espanholas | **NÃO SEI** | equivalente aberto não investigado nesta rodada |
| IT-T13-001 | Registro Imprese / cooperative italiane | **NÃO SEI** | idem; não há API aberta comparável conhecida |

---

## CAMADA DE DESCOBERTA — ITÁLIA (2026-09-03)

Este Atlas continua **dono** do catálogo de fontes. O que segue é uma **camada de
descoberta** ligada a ele, não um segundo dono.

**Onde ela vive:**

| | |
|---|---|
| registro legível por máquina | `data/samples/IT-FONTES-V1/IT-FONTES-DESCOBERTA-V1.json` |
| gerador (a curadoria está no código, não em prosa) | `scripts/it_fontes.py` |
| lotes sociais congelados para o Sintonia Scrap | `PUBLIC-COMM-IT-SOCIAL-BATCH-V1/V2/V3.json` em `data/samples/COMPETITOR-PUBLIC-COMM/` |
| cruzamentos que essas fontes já sustentam | `data/samples/IT-CRUZAMENTO-V1/` |
| as minhas releituras, host a host, da segunda leva | `data/samples/IT-FONTES-V1/IT-FONTES-RECONFERENCIA-V1.json` |
| as 95 rejeições da varredura paralela, em bruto | `data/samples/IT-FONTES-V1/IT-FONTES-REJEICOES-LOTE2-V1.json` |
| camada de áudio permanente (Spreaker + whisper local) | `scripts/it_audio.py` → `data/samples/IT-VOZ-AUDIO-V2/` |

### Por que os IDs são `IT-SRCX-###` e não `IT-T<n>-<seq>`

Porque `SOURCE_ID_COUNT` é uma **sentinela do ledger**, verificada por
`tests/test_handoff.py` contra o valor **36** e contra o prompt de bootstrap. Mintar 90
`SOURCE_ID:` novos moveria essa sentinela **em silêncio**, dentro de uma missão de
descoberta — e mover uma régua verificada é ato deliberado, não efeito colateral.

O namespace `IT-SRCX-###` foi escolhido para **não casar** com o regex do ledger
(`(EU|FR|ES|IT)-T\d{1,2}-\d{3}`). A contagem canônica fica intacta e a descoberta fica
guardada.

**Para promover uma fonte da camada de descoberta a ficha canônica**, três coisas mudam
juntas, na mesma passagem: a ficha entra aqui com `SOURCE_ID: IT-T<n>-<seq>`; o placar e a
tabela de cobertura acompanham; `SOURCE_ID_COUNT` sobe no comentário `<!--M:-->`, no
`PROMPT-PARA-NOVA-CONTA-CLAUDE.md` e em `tests/test_handoff.py`.

### O que a camada trouxe

**90 fontes qualificadas** — 43 HIGH, 47 MEDIUM · 52 AUTOMATABLE · 29 com feed ou API ·
**45 perfis sociais declarados pela própria organização** · 11 rejeições com motivo escrito
no código (mais 95 preservadas em bruto) · 21 rotas não alcançadas desta sessão ·
**1 contradição aberta** entre duas fontes de autoridade. `DEDUPE: PASS`.

**32 das 90** são **canal novo de organização já registrada** e trazem `DEDUPE_AGAINST`
apontando o `SRC_*` do pacote canônico. **Dedupe une organização; não colapsa canal** — a
mesma instituição pode ser site, feed, perfil e API, e as quatro quebram de jeitos
diferentes.

A camada cresceu em **duas levas**: 43 fichas na primeira, sequencial, e 47 na segunda, a
partir de uma varredura paralela de 34 agentes que devolveu 93 fontes e 95 rejeições.
**Nada da segunda leva entrou por confiança:** os 52 hosts ainda não registrados e os 17
handles sociais foram relidos por mim, um a um, e as medições estão em
`IT-FONTES-RECONFERENCIA-V1.json`. **Duas admissões da varredura caíram** — `anicav.it`, que
é muro de bot com 200 e bytes, e o LinkedIn do CSO Italy, que não está declarado na casa do
dono.

> **PROVA DE AGENTE NÃO É PROVA.** O que entra no acervo permanente precisa ter sido lido
> por quem assina.

### As seis que mais mudam o que dá para observar na Itália

| ID | fonte | por que importa |
|---|---|---|
| `IT-SRCX-003` | UNIBO BIG — rede de trappole de *Halyomorpha halys* | única série **numérica** de campo desta rodada: 177 pontos, por província e por estádio, 2021 → 2026-08-31, por API aberta sem chave |
| `IT-SRCX-004` | API Plone dos bollettini do Servizio Fitosanitario Emilia-Romagna | o host já estava no acervo; a **rota** não. A página é um SPA e não entrega link nenhum — a API entrega os 150 PDFs de 2026 com título e data |
| `IT-SRCX-016` | Agricast — podcast dos Gruppi Operativi da Emilia-Romagna | fala técnica longa onde o sinal está **só no áudio**: 9 objetos, 151,7 min, 130.935 caracteres transcritos localmente por 0 USD |
| `IT-SRCX-076` | Fitogest — diretório de empresas produtoras | a **única rota alcançável** para o catálogo italiano dos concorrentes, porque `syngenta.it` e `cropscience.bayer.it` devolvem 403: Syngenta 136, UPL 116, Corteva 93, Bayer 78, ADAMA 56. **E 56 ≠ 51 comerciais ≠ 163 registros** — três contagens de três donos |
| `IT-SRCX-046` | ISTAT — web service SDMX | superfície e produção **por província**, em CSV. É a diferença entre ler uma página e **ter uma série**: sem hectare, "pressão em melo na Emilia-Romagna" não tem escala |
| `IT-SRCX-051` | base de Heap — resistência a herbicida | põe **número** na exposição do bloco herbicida: dos 29 casos italianos, **23** caem nos dois grupos onde a ADAMA se concentra — 15 em ALS e 8 em ACCase |

### Uma contradição que ficou ABERTA

`IT-CONTRA-001` · resistência a **propanil** (HRAC 5) em *Echinochloa crus-galli*: o **GIRE**
declara populações resistentes em Piemonte, Lombardia e Toscana desde 2000; a base de **Heap**
põe a Itália em **zero** naquele grupo. Os dois números foram lidos direto da fonte. É
divergência de **critério de admissão**, e não erro de leitura. Fica registrada sem árbitro —
porque publicar *"a Itália tem 29 casos"* tratando Heap como censo omitiria o propanil.

### Dois defeitos de identidade encontrados no acervo canônico

1. **`SRC_IMAGE_LINE_COM`** está registrado como `TECHNICAL_MEDIA`, `ACCESS_STATUS: GREEN`
   e **sem campo `NAME`**. Lido em 2026-09-03: `image-line.com` é a **FL Studio**, software
   de produção musical. A editora agrícola italiana é a **Image Line s.r.l.**, em
   `imagelinenetwork.com`. São duas empresas homônimas — a mesma família do caso
   `repilouk` da Espanha.
2. Dos **62 `PUBLIC_CHANNEL`** do pacote V2.1, uma parte é horticultura doméstica
   (*Passione Orto*, *Orto Da Coltivare*, *Piccoli Orti Grandi Raccolti*, *Your Hobby*) e
   quatro **não são italianos** (Cornell SIPS, INTA Chubut, Aragón TV, Laderas del
   Naranco). Não se propõe apagar: propõe-se `RELEVANCE: LOW` e `COUNTRY != IT`, para que
   "62 canais" pare de sugerir 62 canais técnicos italianos.

### O que esta sessão não conseguiu fazer, e por quê

`ROTA BLOQUEADA PARA ESTA SESSÃO ≠ ROTA INEXISTENTE.`

- **Instagram — corrigido**: eu havia escrito aqui que a rota precisava do navegador.
  **Estava errado, e o erro era meu:** o que faltava era o `User-Agent`. Mesma URL, mesmo
  minuto — UA de Chrome devolve 625.215 B com `contextJSON = 0`; UA
  `facebookexternalhit/1.1` devolve 262.551 B com `contextJSON = 1`. A rota virou capacidade
  permanente (`scripts/instagram_sem_navegador.py`) e coletou 180 objetos em 30 contas, com
  48 reels transcritos localmente por 0,00 USD. **Continua verdadeiro** que a página de
  perfil devolve `HTTP 302` sob UA de navegador e que o Chrome do `cdp.py` não atravessa o
  proxy — as duas medições estavam certas; a conclusão que tirei delas é que estava errada.
- **Mídia do YouTube**: metadados voltam normalmente; o binário de áudio é recusado com
  `HTTP 403` pela política de saída (`googlevideo.com`).
- **TLS**: `enterisi.it` (GREEN no acervo) hoje falha com `DH_KEY_TOO_SMALL`; `ismea.it`,
  `confagricoltura.it` e `emergenzaxylella.it` falham na verificação de certificado. São
  **estados da fonte**, registrados — a verificação **nunca** foi desligada.

---

### Regra de contagem (declarada para evitar leitura ambígua)

O placar conta **SOURCE_IDs**, não fichas. Uma ficha pode cobrir mais de um SOURCE_ID
(ex.: `FR/ES/IT-T9-001` é uma ficha e três fontes), e algumas fontes testadas aparecem em
tabelas de "não alcançadas" sem ficha própria (as nacionais de T1, EU-T10-002/003).

Verificado na MISSÃO 07, atualizado em 2026-08-29 e recontado no P0.2 · PASSO 03: **<!--M:SOURCE_FICHA_COUNT-->33<!--/M--> fichas · <!--M:SOURCE_ID_COUNT-->39<!--/M--> SOURCE_IDs · <!--M:SOURCE_GREEN_COUNT-->19<!--/M--> GREEN · 4 YELLOW · 0 RED · 16 NÃO SEI**.
Os números batem. `tests/test_canonico.py` passou a verificar isso.

**Duas fichas do PASSO 03 têm ID fora do formato do ledger** — `IT-T4-001-ETICHETTA` e
`IT-T3-LOTTA-OBBLIGATORIA`. Não casam com `(EU|FR|ES|IT)-T\d{1,2}-\d{3}` e portanto **não
movem `SOURCE_ID_COUNT`**, pelo mesmo mecanismo declarado para `IT-SRCX-###`. **Não é
promoção silenciosa nem descuido:** os dois IDs já são usados *literalmente* pelo coletor, pelas
amostras e pelo portal (`scripts/italia_etichette.py`, `scripts/italia_lotta_obbligatoria.py`,
`data/samples/IT-T3-LOTTA/`, `italia-portale/client/italy-ingested.js`), e renomeá-los para caber
na régua quebraria dado já publicado. Ficam declarados aqui como **`LEDGER_ID_MISMATCH`** —
fonte **documentada** e **não contada**. `FICHA_DOCUMENTADA ≠ SOURCE_ID_CONTADO`, e a diferença
é visível em vez de silenciosa.

**A ficha nova é `ES-T5-002`** — a camada científica espanhola, que entregava 152
pesquisadores e 1.771 documentos **sem ter ficha de fonte**. A auditoria adversarial de
2026-08-29 apontou: sem ficha não havia contrato de campos, registro de versão nem
`ACCESS_METHOD` auditável.

### Placar

| Recorte | GREEN | YELLOW | RED | NÃO SEI | Total |
|---|---|---|---|---|---|
| EUROPE | 8 | 0 | 0 | 7 | 15 |
| FRANCE | 2 | 2 | 0 | 3 | 7 |
| SPAIN | 5 | 0 | 0 | 4 | 9 |
| ITALY | 4 | 2 | 0 | 2 | 8 |
| **Total** | **19** | **4** | **0** | **16** | **39** |

## RECONCILIAÇÃO DE SOURCE_IDs USADOS FORA DO ATLAS — P0.2 · PASSO 03

Regra que este bloco existe para cumprir: **dado não entra no repositório órfão de fonte
documentada.** A varredura é mecânica e reprodutível — todo token no formato
`(EU|FR|ES|IT)-T<n>-<seq>` que aparece em `data/`, `scripts/`, `docs/`, `research/` e no
portal, comparado com os SOURCE_IDs deste atlas:

```
grep -rhoE '\b(EU|FR|ES|IT)-T[0-9]{1,2}-[0-9]{3}\b' data/ scripts/ docs/ research/ \
     italia-portale/client italia-portale/BASELINE | sort -u
```

**34 tokens** ficam fora das fichas. Nenhum é silencioso: cada um está classificado abaixo,
com onde está documentado e por que não virou ficha. `FICHA_DOCUMENTADA != SOURCE_ID_CONTADO`
e `PROBE_GREEN != FICHA` são as duas leis que organizam a tabela.

### A · Reconciliados — mesmo objeto, outro nome (não contam duas vezes)

| ID usado | É, comprovadamente | Prova |
|---|---|---|
| `IT-T5-001`, `IT-T5-001-B` | recorte italiano de `EU-T5-001` (OpenAlex) | `MAPA-DE-FONTES-ITALIA.md` §4 intitula a entrada «OpenAlex — recorte italiano»; os arquivos declaram `"source": "OpenAlex"`. Rota REST aberta, a mesma. |
| `IT-T3-004` | primeira medição de `IT-T3-006` (ERSA Friuli-VG) | mesma região e mesma seção «colture erbacee»; a segunda rodada achou a subpágina `bollettini-2026` e 10 boletins de milho. Ver o bloco de reconciliação do mapa nacional. |
| `IT-T3-ER-MODENA` | `IT-T3-001` | a ficha de `IT-T3-001` nomeia os *Consorzi Fitosanitari Provinciali (Reggio Emilia, Modena…)*. |
| `IT-T3-LOTTA-B` | `IT-T3-LOTTA-OBBLIGATORIA` | mesma série de decretos regionais; sufixo de lote, não fonte nova. |
| `IT-SRC-MINISTERO` · `IT-SRC-MODENA` · `IT-SRC-PIEMONTE` · `IT-SRC-REGIONAL` · `IT-SRC-OPENALEX` | chaves internas do portal (`IT-RADAR-V21`) | namespace `IT-SRC-*`, que **não casa** com a régua do ledger; apontam para `IT-T4-001`, `IT-T3-001`, `IT-T3-005`, a camada regional e `EU-T5-001`. `CHAVE_DE_RENDERIZAÇÃO != SOURCE_ID`. |

### B · `PROBED_CANDIDATE / NOT_PROMOTED` — 16 IDs

`IT-T3-007` · `IT-T3-008` · `IT-T5-002` · `IT-T5-003` · `IT-T7-001` · `IT-T7-002` ·
`IT-T7-003` · `IT-T7-004` · `IT-T9-002` · `IT-T9-003` · `IT-T9-004` · `IT-T9-005` ·
`IT-T13-002` · `IT-T13-003` · `IT-T13-004` · `IT-T13-005`

**Onde estão documentados:** `data/samples/IT-FONTES/ITALY-SOURCE-PROBE.json`, com HTTP,
bytes, formato, datas vistas, frescor e `ACCESS_STATUS` medidos em 30/08/2026 —
16 GREEN, 3 BLOCKED (403 em Syngenta, Bayer e ADAMA Itália), 1 NOT_REACHED.

**Por que NÃO viraram ficha, e a razão é medida:** a sondagem mede **alcance e frescor**, não
contrato de fonte. Nenhum deles tem, hoje, licença lida, granularidade declarada, exemplo
real extraído nem caminho de evidência bruta no repositório. O próprio arquivo declara o
método: *«mede ALCANCE, FRESCOR e ASSUNTO. `HTTP 200 ≠ FONTE VIVA`»*. Promovê-los agora
seria escrever ficha por analogia — inventar. **Nenhum dado publicado depende deles:** os
16 aparecem só no probe e no script que o gera (`scripts/italia_fontes_probe.py`).

**O risco que fica declarado:** eles **ocupam o namespace canônico** sem ficha. Enquanto
estiverem assim, nenhum destes números pode ser reemitido para outra fonte — foi por não
querer esse risco que a camada de descoberta usou `IT-SRCX-###`.

### C · Documentados só no mapa nacional — 4 IDs

| ID | Documentado em | Estado medido | Por que não é ficha |
|---|---|---|---|
| `IT-T3-003` | `MAPA-DE-FONTES-ITALIA.md` §3 | **GREEN** — 2026: 6 videira · 4 macieira · 0 herbáceas | rota medida, mas **sem evidência bruta preservada** no repositório. **Ressalva registrada:** a linha de proveniência de `ITALY-HERO-CASES-V1` diz «derivado de … IT-T3-002/003/006», e **nenhuma perna de caso cita `IT-T3-003`** — a prosa nomeia mais fontes do que as pernas usam. Corrigir a prosa exigiria reabrir o pacote de casos, que não é escopo deste passo; fica declarado em vez de silencioso. |
| `IT-T3-005` | `MAPA-DE-FONTES-ITALIA.md` §3 | **YELLOW** — *disciplinari* + decretos de deroga | `ISSUE_KNOWN != CURRENT_SIGNAL`: o Piemonte publica o primeiro, não o segundo. |
| `IT-T3-004` | idem | **YELLOW, superada** | ver grupo A. |
| `IT-T4-002` | `MAPA-DE-FONTES-ITALIA.md` §1 | categoria fitoiatrica (taxonomia oficial) | é **vocabulário**, não fonte de fato; entra no mesmo balde de `ES-T4-001`, que é ficha porque tem rota XLSX e exemplo lido. Este ainda não tem. |

### D · Dívida anterior a este passo — 13 IDs

`ES-T2-002` · `ES-T2-003` · `ES-T3-002` · `ES-T4-004` · `ES-T5-003` · `ES-T5-004` ·
`ES-T6-001` · `ES-T8-001` · `ES-T8-002` · `ES-T8-003` · `ES-T9-002` · `EU-T9-001` ·
`IT-T12-001`

**Já estavam no repositório antes de `bdb57cf`** — conferido token a token contra a base — e
portanto **não são efeito deste enxerto**. Ficam nomeados porque a alternativa é carregá-los
em silêncio. Onde já há descrição: `ES-T8-001/002` em `docs/regras/REGRA-DE-COLETA-EXTERNA-EAME.md`;
`ES-T2-002`, `ES-T3-002` e `ES-T6-001` em `docs/relatorios/RELATORIO-FILA-AUTONOMA-ES.md`;
`ES-T4-004` em `docs/apresentacao/CASOS-PARA-APRESENTACAO.md` e no atlas de capacidades.
`IT-T12-001` **não é uso**: é o exemplo da própria «Convenção de SOURCE_ID» acima. `EU-T9-001`
é grafia divergente de `FR/ES/IT-T9-001` num único documento.

**Estado do portão, declarado sem arredondar:**

```
SOURCE_IDS_WITHOUT_ATLAS_ENTRY   = 0 não classificados
                                   34 classificados, com razão medida e reprodutível
NOVOS DESTE PASSO SEM FICHA      = 20 — 16 no grupo B, 4 no grupo C
ANTERIORES A bdb57cf             = 14 — os 13 do grupo D mais IT-T5-001,
                                   que é anterior E reconciliado (grupo A)
DADO PUBLICADO ÓRFÃO DE FONTE    = 0 — as fontes que alimentam caso publicado
                                   (IT-T3-002, IT-T3-LAMMA, IT-T3-OP, IT-T1-001,
                                   IT-T3-006, IT-T4-001-ETICHETTA) foram fichadas aqui
```

---

### Cobertura por território

| | T1 | T2 | T3 | T4 | T5 | T6 | T7 | T8 | T9 | T10 | T11 | T12 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| EUROPE | 2G | 3G/1? | 1? | 1G/1? | 1G | 1G | – | 1? | – | 1G/2? | – | **1G** |
| FRANCE | 1? | – | 1Y/1? | 1G | – | – | – | – | 1? | – | 1Y | – |
| SPAIN | 1? | – | **1G** | 3G/1? | – | – | – | – | 1? | – | – | – |
| ITALY | **1G** | – | 1Y/**2G** | 1G | – | – | – | – | 1? | – | 1Y | – |

*(– = não investigado)*
