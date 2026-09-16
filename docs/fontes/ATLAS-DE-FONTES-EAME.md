# ATLAS DE FONTES — SINTONIA EAME

Catálogo de tudo que conseguimos **realmente** observar em França, Espanha, Itália e na
camada comum europeia.

> Este atlas registra **fontes**, não desejos. Uma linha só existe aqui depois que alguém
> abriu a fonte, olhou o que ela entrega e guardou evidência disso.

**Estado:** atualizado em 2026-09-15 — **<!--M:SOURCE_ID_COUNT-->190<!--/M--> fontes registradas** (90 GREEN, 83 YELLOW, 17 NÃO SEI).
**Última atualização:** 2026-09-15

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

#### Números gastos que este ficheiro já não mostra

A regra acima só protege quem consegue ver o número. Um ID emitido e depois
**retirado** desaparece do atlas — e quem alocar «o próximo» volta a emiti-lo,
sem que nada acuse. Censo de 2026-09-15 sobre as **31** versões do atlas que
existem na história: **217** IDs já foram emitidos alguma vez, e **10** não
estão nesta população. Nove continuam visíveis noutro emissor
(`candidatas/ITALY-SOURCE-MASTER-V1.json`) e `tests/test_source_id.py` apanha-os.
Um não:

| ID | quando | o que era | porque saiu |
|---|---|---|---|
| `IT-T4-002` | 2 versões do atlas, em tabela de estado (nunca teve ficha) | categoria fitoiatrica — taxonomia oficial | **é vocabulário, não fonte.** A própria tabela que o declarava já dizia isso |

`IT-T4-002` **está gasto e não se reatribui.** O próximo T4 italiano livre é o
`IT-T4-003`.

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
COLLECTION_FEASIBILITY:       ALTA — `coleta/cellar.sh` reproduz a coleta
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
                              Sem chave, sem scraping. `coleta/ephy.sh download`.
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
                              Cliente: coleta/mapa_regfi.py
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
                              `./coleta/cellar.sh sparql "<consulta>"`
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
EVIDENCE:                     mesma cadeia de EU-T4-001; consulta registrada em coleta/cellar.sh
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

### T1 · CROP & PRODUCTION — ITALY · onda 1 (2026-09-14)

*22 fontes registradas nesta secção. Cada uma foi aberta, observada e tem exemplo real preservado em `data/samples/IT-SOURCE-SAMPLES/<SOURCE_ID>/`. Registada ≠ contratada: nenhuma tem contrato de busca, e nenhuma coleta foi corrida.*

#### IT-T1-002 · Provincia autonoma di Trento — Agricoltura

```
SOURCE_ID:                    IT-T1-002
SOURCE_NAME:                  Provincia autonoma di Trento — Agricoltura
SOURCE_OWNER:                 Provincia autonoma di Trento
COUNTRY:                      ITALY
REGION:                       TRENTINO-ALTO ADIGE
LANGUAGE:                     IT
TERRITORY:                    T1 (também serve T4)
SOURCE_TYPE:                  BASE_OFICIAL
URL:                          https://www.provincia.tn.it/
ACCESS_METHOD:                HTML
CROPS:                        melo;vite
TOPICS:                       agricoltura;melo;vite
GEOGRAPHIC_GRANULARITY:       REGIÃO — TRENTINO-ALTO ADIGE
UPDATE_FREQUENCY:             observada por data visível na página: 2026-09-12
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   SIM — 2026-09-10
RAW_EVIDENCE_PRESERVABLE:     SIM — HTML obtido por HTTP
AUTOMATION_FEASIBILITY:       ALTA — rota estruturada declarada (API/opendata)
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «AUTONOMIA 2026. Il Cammino della Comunità trentina - Provincia autonoma di
                              Trento» https://www.provincia.tn.it/News/Eventi/AUTONOMIA-2026.-Il-Cammino-
                              della-Comunita-trentina — HTML, 105599 bytes lidos em 2026-09-14
ADAMA_USE_CASE:               agencia regional agricola; alimenta T1 (cultura e producao), T4
                              (regulatorio)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T1-002/MANIFEST.json
VERDICT:                      GREEN — fonte aberta, exemplo real observado e preservado
```

#### IT-T1-003 · Regione Toscana — Agricoltura

```
SOURCE_ID:                    IT-T1-003
SOURCE_NAME:                  Regione Toscana — Agricoltura
SOURCE_OWNER:                 Regione Toscana
COUNTRY:                      ITALY
REGION:                       TOSCANA
LANGUAGE:                     IT-IT
TERRITORY:                    T1 (também serve T4, T12)
SOURCE_TYPE:                  BASE_OFICIAL
URL:                          https://www.regione.toscana.it/agricoltura-e-alimentazione
ACCESS_METHOD:                HTML
CROPS:                        olivo;vite
TOPICS:                       agricoltura;PSR;olivo;vite
GEOGRAPHIC_GRANULARITY:       REGIÃO — TOSCANA
UPDATE_FREQUENCY:             observada por data visível na página: 2026-09-12
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   NÃO SEI — nenhuma data legível no item observado
RAW_EVIDENCE_PRESERVABLE:     SIM — HTML obtido por HTTP
AUTOMATION_FEASIBILITY:       ALTA — rota estruturada declarada (API/opendata)
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Approfondimenti - Regione Toscana»
                              https://www.regione.toscana.it/regione/approfondimenti — HTML, 165734 bytes
                              lidos em 2026-09-14
ADAMA_USE_CASE:               orgao agricola regional / politica agricola; alimenta T1 (cultura e
                              producao), T4 (regulatorio), T12 (politica e ambiente agricola)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T1-003/MANIFEST.json
VERDICT:                      GREEN — fonte aberta, exemplo real observado e preservado
```

#### IT-T1-004 · Liguria — Regione Liguria agricoltura

```
SOURCE_ID:                    IT-T1-004
SOURCE_NAME:                  Liguria — Regione Liguria agricoltura
SOURCE_OWNER:                 Regione Liguria
COUNTRY:                      ITALY
REGION:                       LIGURIA
LANGUAGE:                     IT-IT
TERRITORY:                    T1 (também serve T4)
SOURCE_TYPE:                  BASE_OFICIAL
URL:                          https://www.regione.liguria.it/homepage-agricoltura.html
ACCESS_METHOD:                HTML
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       agricoltura;floricoltura
GEOGRAPHIC_GRANULARITY:       REGIÃO — LIGURIA
UPDATE_FREQUENCY:             NÃO SEI — nenhuma data de publicação legível na página
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   SIM — 2023-06-28
RAW_EVIDENCE_PRESERVABLE:     SIM — HTML obtido por HTTP
AUTOMATION_FEASIBILITY:       ALTA — rota estruturada declarada (API/opendata)
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «attività istituzionale - avvisi - Regione Liguria»
                              https://www.regione.liguria.it/homepage-attivita-istituzionale/atti-di-
                              notifica/avvisi-atti-notifica.html — HTML, 178556 bytes lidos em 2026-09-14
ADAMA_USE_CASE:               orgao agricola regional / politica agricola; alimenta T1 (cultura e
                              producao), T4 (regulatorio)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T1-004/MANIFEST.json
VERDICT:                      YELLOW — frequencia de atualizacao por provar
```

#### IT-T1-005 · Umbria — Agricoltura e foreste

```
SOURCE_ID:                    IT-T1-005
SOURCE_NAME:                  Umbria — Agricoltura e foreste
SOURCE_OWNER:                 Regione Umbria
COUNTRY:                      ITALY
REGION:                       UMBRIA
LANGUAGE:                     IT-IT
TERRITORY:                    T1 (também serve T4)
SOURCE_TYPE:                  BASE_OFICIAL
URL:                          https://www.regione.umbria.it/home
ACCESS_METHOD:                HTML
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       agricoltura;PSR
GEOGRAPHIC_GRANULARITY:       REGIÃO — UMBRIA
UPDATE_FREQUENCY:             NÃO SEI — nenhuma data de publicação legível na página
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   NÃO SEI — nenhuma data legível no item observado
RAW_EVIDENCE_PRESERVABLE:     SIM — HTML obtido por HTTP
AUTOMATION_FEASIBILITY:       ALTA — rota estruturada declarada (API/opendata)
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Celebrazioni del 165 anniversario dell’Ente Santa Croce Maria Montessori di
                              Perugia - Notizie - Regione Umbria» https://www.regione.umbria.it/notizie/-
                              /asset_publisher/54m7RxsCDsHr/content/celebrazioni-del-165-anniversario-
                              dell-ente-santa-croce-maria-montessori-di-perugia?read_more=true — HTML,
                              44288 bytes lidos em 2026-09-14
ADAMA_USE_CASE:               orgao agricola regional / politica agricola; alimenta T1 (cultura e
                              producao), T4 (regulatorio)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T1-005/MANIFEST.json
VERDICT:                      YELLOW — frequencia de atualizacao por provar
```

#### IT-T1-006 · ARSAC Calabria — Azienda Regionale per lo Sviluppo dell'Agricoltura Calabrese

```
SOURCE_ID:                    IT-T1-006
SOURCE_NAME:                  ARSAC Calabria — Azienda Regionale per lo Sviluppo dell'Agricoltura
                              Calabrese
SOURCE_OWNER:                 Regione Calabria
COUNTRY:                      ITALY
REGION:                       CALABRIA
LANGUAGE:                     IT-IT
TERRITORY:                    T1 (também serve T7, T3)
SOURCE_TYPE:                  BASE_OFICIAL
URL:                          https://www.arsac.calabria.it/
ACCESS_METHOD:                HTML
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       assistenza tecnica;divulgazione;fitosanitario
GEOGRAPHIC_GRANULARITY:       REGIÃO — CALABRIA
UPDATE_FREQUENCY:             observada por data visível na página: 2026-09-14
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   SIM — 2026-09-14
RAW_EVIDENCE_PRESERVABLE:     SIM — HTML obtido por HTTP
AUTOMATION_FEASIBILITY:       MÉDIA-ALTA — feed ou ficheiro previsível
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «BOLLETTINO agrometeorologico e fitosanitario – agrumi, olivo, vite e kiwi
                              &#8211; valido fino al 4 agosto 2026 &#8211; ARSAC»
                              https://arsac.calabria.it/bollettino-agrometeorologico-e-fitosanitario-
                              agrumi-olivo-vite-e-kiwi-valido-fino-al-4-agosto-2026/ — HTML, 183249 bytes
                              lidos em 2026-09-14
ADAMA_USE_CASE:               agencia regional agricola; alimenta T1 (cultura e producao), T7 (rede
                              tecnica), T3 (praga, doenca e infestantes)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T1-006/MANIFEST.json
VERDICT:                      GREEN — fonte aberta, exemplo real observado e preservado
```

#### IT-T1-007 · ARSIAL — Agenzia Regionale Sviluppo Innovazione Agricoltura Lazio

```
SOURCE_ID:                    IT-T1-007
SOURCE_NAME:                  ARSIAL — Agenzia Regionale Sviluppo Innovazione Agricoltura Lazio
SOURCE_OWNER:                 Regione Lazio
COUNTRY:                      ITALY
REGION:                       LAZIO
LANGUAGE:                     IT-IT
TERRITORY:                    T1 (também serve T7, T3)
SOURCE_TYPE:                  BASE_OFICIAL
URL:                          https://www.arsial.it/
ACCESS_METHOD:                HTML
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       sviluppo agricolo;biodiversita;assistenza
GEOGRAPHIC_GRANULARITY:       REGIÃO — LAZIO
UPDATE_FREQUENCY:             observada por data visível na página: 2026-09-11
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   SIM — 2026-08-31
RAW_EVIDENCE_PRESERVABLE:     SIM — HTML obtido por HTTP
AUTOMATION_FEASIBILITY:       ALTA — rota estruturada declarada (API/opendata)
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Avvisi per privati Archive - Arsial» https://www.arsial.it/bandi-e-
                              avvisi/avvisi-per-privati/ — HTML, 362452 bytes lidos em 2026-09-14
ADAMA_USE_CASE:               agencia regional agricola; alimenta T1 (cultura e producao), T7 (rede
                              tecnica), T3 (praga, doenca e infestantes)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T1-007/MANIFEST.json
VERDICT:                      GREEN — fonte aberta, exemplo real observado e preservado
```

#### IT-T1-008 · Agricoltura Regione Lombardia

```
SOURCE_ID:                    IT-T1-008
SOURCE_NAME:                  Agricoltura Regione Lombardia
SOURCE_OWNER:                 Regione Lombardia
COUNTRY:                      ITALY
REGION:                       LOMBARDIA
LANGUAGE:                     IT-IT
TERRITORY:                    T1 (também serve T4, T12)
SOURCE_TYPE:                  BASE_OFICIAL
URL:                          https://www.ersaf.lombardia.it/montagna/rifugi/it-servizi-alla-montagna-
                              attivita-per-i-territori-montani-2022/
ACCESS_METHOD:                PDF ligado a partir da página da fonte
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       agricoltura;PSR;fitosanitario
GEOGRAPHIC_GRANULARITY:       REGIÃO — LOMBARDIA
UPDATE_FREQUENCY:             observada por data visível na página: 2026-04-06
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   NÃO SEI — nenhuma data legível no item observado
RAW_EVIDENCE_PRESERVABLE:     SIM — PDF obtido por HTTP
AUTOMATION_FEASIBILITY:       ALTA — rota estruturada declarada (API/opendata)
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Clicca per scaricare il Decreto iscrizione Elenco rifugi 2025»
                              https://www.ersaf.lombardia.it/wp-
                              content/uploads/2024/08/SEO31_31-07-20241.pdf — PDF, 709669 bytes lidos em
                              2026-09-14
ADAMA_USE_CASE:               agencia regional agricola; alimenta T1 (cultura e producao), T4
                              (regulatorio), T12 (politica e ambiente agricola)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T1-008/MANIFEST.json
VERDICT:                      GREEN — fonte aberta, exemplo real observado e preservado
```

#### IT-T1-009 · Lazio — Agricoltura Regione Lazio

```
SOURCE_ID:                    IT-T1-009
SOURCE_NAME:                  Lazio — Agricoltura Regione Lazio
SOURCE_OWNER:                 Regione Lazio
COUNTRY:                      ITALY
REGION:                       LAZIO
LANGUAGE:                     IT
TERRITORY:                    T1 (também serve T4)
SOURCE_TYPE:                  BASE_OFICIAL
URL:                          https://www.regione.lazio.it/cittadini/agricoltura
ACCESS_METHOD:                HTML
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       agricoltura;PSR
GEOGRAPHIC_GRANULARITY:       REGIÃO — LAZIO
UPDATE_FREQUENCY:             observada por data visível na página: 2026-09-11
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   SIM — 2026-08-04
RAW_EVIDENCE_PRESERVABLE:     SIM — HTML obtido por HTTP
AUTOMATION_FEASIBILITY:       MÉDIA — site navegável, sem rota estruturada declarada
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «| Regione Lazio | PN FEAMPA 2021/2027 Intervento 222507 – Approvazione
                              Bando» https://www.regione.lazio.it/notizie/agricoltura/pn-
                              feampa-2021-2027-intervento-222507-approvazione-bando — HTML, 103903 bytes
                              lidos em 2026-09-14
ADAMA_USE_CASE:               orgao agricola regional / politica agricola; alimenta T1 (cultura e
                              producao), T4 (regulatorio)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T1-009/MANIFEST.json
VERDICT:                      GREEN — fonte aberta, exemplo real observado e preservado
```

#### IT-T1-010 · Regione Abruzzo — Agricoltura

```
SOURCE_ID:                    IT-T1-010
SOURCE_NAME:                  Regione Abruzzo — Agricoltura
SOURCE_OWNER:                 Regione Abruzzo
COUNTRY:                      ITALY
REGION:                       ABRUZZO
LANGUAGE:                     IT
TERRITORY:                    T1 (também serve T4)
SOURCE_TYPE:                  BASE_OFICIAL
URL:                          https://www.regione.abruzzo.it/
ACCESS_METHOD:                HTML
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       agricoltura;PSR
GEOGRAPHIC_GRANULARITY:       REGIÃO — ABRUZZO
UPDATE_FREQUENCY:             observada por data visível na página: 2026-09-14
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   NÃO SEI — nenhuma data legível no item observado
RAW_EVIDENCE_PRESERVABLE:     SIM — HTML obtido por HTTP
AUTOMATION_FEASIBILITY:       MÉDIA — site navegável, sem rota estruturada declarada
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Sanità, validati i nuovi atti aziendali delle quattro Asl regionali |
                              Regione Abruzzo» http://www.regione.abruzzo.it/notizie/validati-i-nuovi-
                              atti-aziendali-delle-4-asl-regionali — HTML, 100666 bytes lidos em
                              2026-09-14
ADAMA_USE_CASE:               orgao agricola regional / politica agricola; alimenta T1 (cultura e
                              producao), T4 (regulatorio)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T1-010/MANIFEST.json
VERDICT:                      GREEN — fonte aberta, exemplo real observado e preservado
```

#### IT-T1-011 · Regione Umbria — Agricoltura

```
SOURCE_ID:                    IT-T1-011
SOURCE_NAME:                  Regione Umbria — Agricoltura
SOURCE_OWNER:                 Regione Umbria
COUNTRY:                      ITALY
REGION:                       UMBRIA
LANGUAGE:                     IT-IT
TERRITORY:                    T1 (também serve T4)
SOURCE_TYPE:                  BASE_OFICIAL
URL:                          https://www.regione.umbria.it/agricoltura
ACCESS_METHOD:                HTML
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       agricoltura;PSR
GEOGRAPHIC_GRANULARITY:       REGIÃO — UMBRIA
UPDATE_FREQUENCY:             observada por data visível na página: 2025-11-10
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   NÃO SEI — nenhuma data legível no item observado
RAW_EVIDENCE_PRESERVABLE:     SIM — HTML obtido por HTTP
AUTOMATION_FEASIBILITY:       ALTA — rota estruturada declarada (API/opendata)
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Legge Serpieri - Notizia - Regione Umbria» https://www.regione.umbria.it/ag
                              ricoltura/notizia/-/asset_publisher/PVUq7ammJALj/content/legge-
                              serpieri?read_more=true — HTML, 46991 bytes lidos em 2026-09-14
ADAMA_USE_CASE:               orgao agricola regional / politica agricola; alimenta T1 (cultura e
                              producao), T4 (regulatorio)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T1-011/MANIFEST.json
VERDICT:                      GREEN — fonte aberta, exemplo real observado e preservado
```

#### IT-T1-012 · Regione Valle d'Aosta — Agricoltura

```
SOURCE_ID:                    IT-T1-012
SOURCE_NAME:                  Regione Valle d'Aosta — Agricoltura
SOURCE_OWNER:                 Regione Autonoma Valle d'Aosta
COUNTRY:                      ITALY
REGION:                       VALLE D'AOSTA
LANGUAGE:                     IT
TERRITORY:                    T1 (também serve T4)
SOURCE_TYPE:                  BASE_OFICIAL
URL:                          https://www.regione.vda.it/agricoltura/
ACCESS_METHOD:                HTML
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       agricoltura di montagna;viticoltura
GEOGRAPHIC_GRANULARITY:       REGIÃO — VALLE D'AOSTA
UPDATE_FREQUENCY:             observada por data visível na página: 2026-03-09
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   SIM — 2026-09-14
RAW_EVIDENCE_PRESERVABLE:     SIM — HTML obtido por HTTP
AUTOMATION_FEASIBILITY:       ALTA — rota estruturada declarada (API/opendata)
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Avvisi di incarichi dirigenziali - Pubblicità - Regione Autonoma Valle
                              d'Aosta» https://www.regione.vda.it/amministrazionetrasparente/personale/pub
                              blicazioneincarichidirigenziali/default_i.aspx — HTML, 36254 bytes lidos em
                              2026-09-14
ADAMA_USE_CASE:               orgao agricola regional / politica agricola; alimenta T1 (cultura e
                              producao), T4 (regulatorio)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T1-012/MANIFEST.json
VERDICT:                      GREEN — fonte aberta, exemplo real observado e preservado
```

#### IT-T1-013 · Assosementi

```
SOURCE_ID:                    IT-T1-013
SOURCE_NAME:                  Assosementi
SOURCE_OWNER:                 Assosementi
COUNTRY:                      ITALY
REGION:                       NAZIONALE (sem recorte regional)
LANGUAGE:                     IT-IT
TERRITORY:                    T1 (também serve T10)
SOURCE_TYPE:                  ORGANIZACAO
URL:                          https://www.sementi.it/
ACCESS_METHOD:                HTML
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       sementi;varieta
GEOGRAPHIC_GRANULARITY:       PAÍS — a fonte publica com alcance nacional
UPDATE_FREQUENCY:             observada por data visível na página: 2026-07-10
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   SIM — 2026-05-15
RAW_EVIDENCE_PRESERVABLE:     SIM — HTML obtido por HTTP
AUTOMATION_FEASIBILITY:       ALTA — rota estruturada declarada (API/opendata)
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Seme in natura certificato e pulito (tara 0%) di erba medica: confermato a
                              2,80 €/kg il prezzo orientativo per la campagna 2026 - Assosementi»
                              https://www.sementi.it/comunicati_stampa/seme-in-natura-certificato-e-
                              pulito-tara-0-di-erba-medica-confermato-a-280-e-kg-il-prezzo-orientativo-
                              per-la-campagna-2026/ — HTML, 67258 bytes lidos em 2026-09-14
ADAMA_USE_CASE:               ente de filiera / mercado oficial; alimenta T1 (cultura e producao), T10
                              (mercado e industria)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T1-013/MANIFEST.json
VERDICT:                      GREEN — fonte aberta, exemplo real observado e preservado
```

#### IT-T1-014 · Ente Nazionale Risi

```
SOURCE_ID:                    IT-T1-014
SOURCE_NAME:                  Ente Nazionale Risi
SOURCE_OWNER:                 Ente Nazionale Risi
COUNTRY:                      ITALY
REGION:                       LOMBARDIA
LANGUAGE:                     IT
TERRITORY:                    T1 (também serve T10, T4)
SOURCE_TYPE:                  BASE_OFICIAL
URL:                          http://www.enterisi.it/servizi/notizie/notizie_homepage.aspx
ACCESS_METHOD:                HTML
CROPS:                        riso
TOPICS:                       riso;mercato;statistiche;varieta
GEOGRAPHIC_GRANULARITY:       REGIÃO — LOMBARDIA
UPDATE_FREQUENCY:             observada por data visível na página: 2026-09-14
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   NÃO SEI — nenhuma data legível no item observado
RAW_EVIDENCE_PRESERVABLE:     SIM — HTML obtido por HTTP
AUTOMATION_FEASIBILITY:       MÉDIA-ALTA — feed ou ficheiro previsível
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Ente Nazionale Risi» http://www.enterisi.it/servizi/notizie/notizie_fase01.
                              aspx?categoriaVisualizzata=19 — HTML, 266233 bytes lidos em 2026-09-14
ADAMA_USE_CASE:               ente de filiera / mercado oficial; alimenta T1 (cultura e producao), T10
                              (mercado e industria), T4 (regulatorio)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T1-014/MANIFEST.json
VERDICT:                      YELLOW — so responde em HTTP
```

#### IT-T1-015 · Terra e Vita — Edagricole

```
SOURCE_ID:                    IT-T1-015
SOURCE_NAME:                  Terra e Vita — Edagricole
SOURCE_OWNER:                 Edagricole — New Business Media
COUNTRY:                      ITALY
REGION:                       EMILIA-ROMAGNA
LANGUAGE:                     EN
TERRITORY:                    T1 (também serve T3, T10)
SOURCE_TYPE:                  IMPRENSA
URL:                          https://terraevita.edagricole.it/
ACCESS_METHOD:                HTML
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       rivista tecnica;seminativi;difesa
GEOGRAPHIC_GRANULARITY:       REGIÃO — EMILIA-ROMAGNA
UPDATE_FREQUENCY:             observada por data visível na página: 2026-03-03
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   SIM — 2026-03-03
RAW_EVIDENCE_PRESERVABLE:     SIM — HTML obtido por HTTP
AUTOMATION_FEASIBILITY:       ALTA — rota estruturada declarada (API/opendata)
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Dublino mette alla prova la nuova agricoltura europea - Terra e Vita»
                              https://terraevita.edagricole.it/agridaily-guida-pac/pac-per-gli-
                              agricoltori/approfondimenti-pac/dublino-mette-alla-prova-la-nuova-
                              agricoltura-europea-sicurezza-innovazione-e-risorse/ — HTML, 268860 bytes
                              lidos em 2026-09-14
ADAMA_USE_CASE:               universidade / departamento agrario; alimenta T1 (cultura e producao), T3
                              (praga, doenca e infestantes), T10 (mercado e industria)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T1-015/MANIFEST.json
VERDICT:                      GREEN — fonte aberta, exemplo real observado e preservado
```

#### IT-T1-016 · Italia Olivicola

```
SOURCE_ID:                    IT-T1-016
SOURCE_NAME:                  Italia Olivicola
SOURCE_OWNER:                 Italia Olivicola Consorzio Nazionale
COUNTRY:                      ITALY
REGION:                       NAZIONALE (sem recorte regional)
LANGUAGE:                     IT-IT
TERRITORY:                    T1 (também serve T10)
SOURCE_TYPE:                  ORGANIZACAO
URL:                          https://www.italiaolivicola.it/
ACCESS_METHOD:                HTML
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       olivicoltura;OP
GEOGRAPHIC_GRANULARITY:       PAÍS — a fonte publica com alcance nacional
UPDATE_FREQUENCY:             observada por data visível na página: 2026-03-20
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   SIM — 2023-10-20
RAW_EVIDENCE_PRESERVABLE:     SIM — HTML obtido por HTTP
AUTOMATION_FEASIBILITY:       ALTA — rota estruturada declarada (API/opendata)
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «News &#8211; Italia Olivicola»
                              https://www.italiaolivicola.it/category/news/ — HTML, 109122 bytes lidos em
                              2026-09-14
ADAMA_USE_CASE:               organizacao de produtores; alimenta T1 (cultura e producao), T10 (mercado e
                              industria)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T1-016/MANIFEST.json
VERDICT:                      GREEN — fonte aberta, exemplo real observado e preservado
```

#### IT-T1-017 · Olivo e Olio — Edagricole

```
SOURCE_ID:                    IT-T1-017
SOURCE_NAME:                  Olivo e Olio — Edagricole
SOURCE_OWNER:                 Edagricole — New Business Media
COUNTRY:                      ITALY
REGION:                       NAZIONALE (sem recorte regional)
LANGUAGE:                     EN
TERRITORY:                    T1 (também serve T3)
SOURCE_TYPE:                  IMPRENSA
URL:                          https://olivoeolio.edagricole.it/
ACCESS_METHOD:                HTML
CROPS:                        olio;olivo
TOPICS:                       olivo;olio;difesa
GEOGRAPHIC_GRANULARITY:       PAÍS — a fonte publica com alcance nacional
UPDATE_FREQUENCY:             observada por data visível na página: 2014-03-05
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   SIM — 2014-03-05
RAW_EVIDENCE_PRESERVABLE:     SIM — HTML obtido por HTTP
AUTOMATION_FEASIBILITY:       ALTA — rota estruturada declarada (API/opendata)
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «EVOLIO Expo conquista gli USA: buyer pronti per Bari 2027 - Olivo e Olio»
                              https://olivoeolio.edagricole.it/notizie-dalle-aziende/evolio-expo-
                              conquista-usa-buyer-pronti-per-bari-2027/ — HTML, 265128 bytes lidos em
                              2026-09-14
ADAMA_USE_CASE:               universidade / departamento agrario; alimenta T1 (cultura e producao), T3
                              (praga, doenca e infestantes)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T1-017/MANIFEST.json
VERDICT:                      GREEN — fonte aberta, exemplo real observado e preservado
```

#### IT-T1-018 · Rivista di Agraria

```
SOURCE_ID:                    IT-T1-018
SOURCE_NAME:                  Rivista di Agraria
SOURCE_OWNER:                 Rivista di Agraria
COUNTRY:                      ITALY
REGION:                       NAZIONALE (sem recorte regional)
LANGUAGE:                     IT-IT
TERRITORY:                    T1 (também serve T5, T12)
SOURCE_TYPE:                  IMPRENSA
URL:                          https://www.rivistadiagraria.org/
ACCESS_METHOD:                HTML
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       divulgazione agraria
GEOGRAPHIC_GRANULARITY:       PAÍS — a fonte publica com alcance nacional
UPDATE_FREQUENCY:             NÃO SEI
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   NÃO SEI — nenhuma data legível no item observado
RAW_EVIDENCE_PRESERVABLE:     SIM — HTML obtido por HTTP
AUTOMATION_FEASIBILITY:       ALTA — rota estruturada declarada (API/opendata)
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Il sapore della salute - Rivista di Agraria.org»
                              https://www.rivistadiagraria.org/articoli/anno-2026/sapore-della-salute/ —
                              HTML, 75280 bytes lidos em 2026-09-14
ADAMA_USE_CASE:               imprensa tecnica agricola; alimenta T1 (cultura e producao), T5 (ciencia),
                              T12 (politica e ambiente agricola)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T1-018/MANIFEST.json
VERDICT:                      GREEN — fonte aberta, exemplo real observado e preservado
```

#### IT-T1-019 · SIA — Societa Italiana di Agronomia

```
SOURCE_ID:                    IT-T1-019
SOURCE_NAME:                  SIA — Societa Italiana di Agronomia
SOURCE_OWNER:                 Societa Italiana di Agronomia
COUNTRY:                      ITALY
REGION:                       NAZIONALE (sem recorte regional)
LANGUAGE:                     IT-IT
TERRITORY:                    T1 (também serve T5)
SOURCE_TYPE:                  ORGANIZACAO
URL:                          https://www.siagr.it/
ACCESS_METHOD:                PDF ligado a partir da página da fonte
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       agronomia;congresso
GEOGRAPHIC_GRANULARITY:       PAÍS — a fonte publica com alcance nacional
UPDATE_FREQUENCY:             observada por data visível na página: 2026-04-06
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   NÃO SEI — nenhuma data legível no item observado
RAW_EVIDENCE_PRESERVABLE:     SIM — PDF obtido por HTTP
AUTOMATION_FEASIBILITY:       ALTA — rota estruturada declarada (API/opendata)
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Scarica lo Statuto della SIA» https://siagr.it/wp-
                              content/uploads/2025/01/Statuto-della-Societa-Italiana-di-
                              Agronomia19.06.2023.pdf — PDF, 134455 bytes lidos em 2026-09-14
ADAMA_USE_CASE:               sociedade cientifica / academia; alimenta T1 (cultura e producao), T5
                              (ciencia)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T1-019/MANIFEST.json
VERDICT:                      GREEN — fonte aberta, exemplo real observado e preservado
```

#### IT-T1-020 · Agriligurianet — Regione Liguria agricoltura

```
SOURCE_ID:                    IT-T1-020
SOURCE_NAME:                  Agriligurianet — Regione Liguria agricoltura
SOURCE_OWNER:                 Regione Liguria
COUNTRY:                      ITALY
REGION:                       LIGURIA
LANGUAGE:                     IT-IT
TERRITORY:                    T1 (também serve T3, T7)
SOURCE_TYPE:                  BASE_OFICIAL
URL:                          https://www.agriligurianet.it/it/
ACCESS_METHOD:                HTML
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       agricoltura ligure;floricoltura;fitosanitario
GEOGRAPHIC_GRANULARITY:       REGIÃO — LIGURIA
UPDATE_FREQUENCY:             observada por data visível na página: 2013-04-04
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   SIM — 2025-11-19
RAW_EVIDENCE_PRESERVABLE:     SIM — HTML obtido por HTTP
AUTOMATION_FEASIBILITY:       MÉDIA — site navegável, sem rota estruturada declarada
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Generale - Agriligurianet» https://www.agriligurianet.it/it/impresa/2013-
                              04-04-08-54-42/approfondimenti.html — HTML, 108646 bytes lidos em 2026-09-14
ADAMA_USE_CASE:               agencia regional agricola; alimenta T1 (cultura e producao), T3 (praga,
                              doenca e infestantes), T7 (rede tecnica)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T1-020/MANIFEST.json
VERDICT:                      GREEN — fonte aberta, exemplo real observado e preservado
```

#### IT-T1-021 · AgroNotizie — Image Line

```
SOURCE_ID:                    IT-T1-021
SOURCE_NAME:                  AgroNotizie — Image Line
SOURCE_OWNER:                 Image Line
COUNTRY:                      ITALY
REGION:                       EMILIA-ROMAGNA
LANGUAGE:                     IT
TERRITORY:                    T1 (também serve T3, T4, T10)
SOURCE_TYPE:                  IMPRENSA
URL:                          https://agronotizie.imagelinenetwork.com/
ACCESS_METHOD:                HTML
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       notizie agricole;difesa;fitofarmaci
GEOGRAPHIC_GRANULARITY:       REGIÃO — EMILIA-ROMAGNA
UPDATE_FREQUENCY:             NÃO SEI — nenhuma data de publicação legível na página
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   NÃO SEI — nenhuma data legível no item observado
RAW_EVIDENCE_PRESERVABLE:     SIM — HTML obtido por HTTP
AUTOMATION_FEASIBILITY:       MÉDIA-ALTA — feed ou ficheiro previsível
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «AgroNotizie - Newsletter»
                              https://agronotizie.imagelinenetwork.com/newsletter/ — HTML, 54095 bytes
                              lidos em 2026-09-14
ADAMA_USE_CASE:               imprensa tecnica agricola; alimenta T1 (cultura e producao), T3 (praga,
                              doenca e infestantes), T4 (regulatorio), T10 (mercado e industria)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T1-021/MANIFEST.json
VERDICT:                      YELLOW — frequencia de atualizacao por provar
```

#### IT-T1-022 · OlivoNews — giornale di olivicoltura

```
SOURCE_ID:                    IT-T1-022
SOURCE_NAME:                  OlivoNews — giornale di olivicoltura
SOURCE_OWNER:                 OlivoNews
COUNTRY:                      ITALY
REGION:                       NAZIONALE (sem recorte regional)
LANGUAGE:                     IT-IT
TERRITORY:                    T1 (também serve T3, T10)
SOURCE_TYPE:                  IMPRENSA
URL:                          https://www.olivonews.it/
ACCESS_METHOD:                HTML
CROPS:                        olio;olivo
TOPICS:                       olivo;olio;tecnica
GEOGRAPHIC_GRANULARITY:       PAÍS — a fonte publica com alcance nacional
UPDATE_FREQUENCY:             observada por data visível na página: 2025-04-27
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   SIM — 2025-04-27
RAW_EVIDENCE_PRESERVABLE:     SIM — HTML obtido por HTTP
AUTOMATION_FEASIBILITY:       ALTA — rota estruturada declarada (API/opendata)
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Attualità Archivi - l&#039;OlivoNews»
                              https://olivonews.it/category/attualita/ — HTML, 150226 bytes lidos em
                              2026-09-14
ADAMA_USE_CASE:               imprensa tecnica agricola; alimenta T1 (cultura e producao), T3 (praga,
                              doenca e infestantes), T10 (mercado e industria)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T1-022/MANIFEST.json
VERDICT:                      GREEN — fonte aberta, exemplo real observado e preservado
```

#### IT-T1-023 · SOI — Societa di Ortoflorofrutticoltura Italiana

```
SOURCE_ID:                    IT-T1-023
SOURCE_NAME:                  SOI — Societa di Ortoflorofrutticoltura Italiana
SOURCE_OWNER:                 SOI
COUNTRY:                      ITALY
REGION:                       NAZIONALE (sem recorte regional)
LANGUAGE:                     IT
TERRITORY:                    T1 (também serve T5, T11)
SOURCE_TYPE:                  ORGANIZACAO
URL:                          https://www.soihs.it/
ACCESS_METHOD:                HTML
CROPS:                        ortofrutta
TOPICS:                       ortofrutta;floricoltura;congressi
GEOGRAPHIC_GRANULARITY:       PAÍS — a fonte publica com alcance nacional
UPDATE_FREQUENCY:             NÃO SEI — nenhuma data de publicação legível na página
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   NÃO SEI — nenhuma data legível no item observado
RAW_EVIDENCE_PRESERVABLE:     SIM — HTML obtido por HTTP
AUTOMATION_FEASIBILITY:       MÉDIA — site navegável, sem rota estruturada declarada
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Olivo - SOI» https://www.soihs.it/pubblicazioni/0000001920/video/olivo.aspx
                              — HTML, 46163 bytes lidos em 2026-09-14
ADAMA_USE_CASE:               imprensa tecnica agricola; alimenta T1 (cultura e producao), T5 (ciencia),
                              T11 (eventos)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T1-023/MANIFEST.json
VERDICT:                      YELLOW — frequencia de atualizacao por provar
```

### T2 · CLIMATE / WATER / SOIL — ITALY · onda 1 (2026-09-14)

*19 fontes registradas nesta secção. Cada uma foi aberta, observada e tem exemplo real preservado em `data/samples/IT-SOURCE-SAMPLES/<SOURCE_ID>/`. Registada ≠ contratada: nenhuma tem contrato de busca, e nenhuma coleta foi corrida.*

#### IT-T2-006 · ARPA Campania

```
SOURCE_ID:                    IT-T2-006
SOURCE_NAME:                  ARPA Campania
SOURCE_OWNER:                 ARPAC
COUNTRY:                      ITALY
REGION:                       CAMPANIA
LANGUAGE:                     IT-IT
TERRITORY:                    T2 (também serve T12)
SOURCE_TYPE:                  BASE_OFICIAL
URL:                          https://www.arpacampania.it/
ACCESS_METHOD:                HTML
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       ambiente;acque;meteo
GEOGRAPHIC_GRANULARITY:       REGIÃO — CAMPANIA
UPDATE_FREQUENCY:             observada por data visível na página: 2026-09-08
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   SIM — 2026-09-08
RAW_EVIDENCE_PRESERVABLE:     SIM — HTML obtido por HTTP
AUTOMATION_FEASIBILITY:       ALTA — rota estruturada declarada (API/opendata)
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «News - Arpac» https://www.arpacampania.it/web/guest/news — HTML, 472011
                              bytes lidos em 2026-09-14
ADAMA_USE_CASE:               agrometeorologia / clima / ambiente regional; alimenta T2 (clima/agua/solo),
                              T12 (politica e ambiente agricola)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T2-006/MANIFEST.json
VERDICT:                      GREEN — fonte aberta, exemplo real observado e preservado
```

#### IT-T2-007 · ARPA Sicilia

```
SOURCE_ID:                    IT-T2-007
SOURCE_NAME:                  ARPA Sicilia
SOURCE_OWNER:                 ARPA Sicilia
COUNTRY:                      ITALY
REGION:                       SICILIA
LANGUAGE:                     IT-IT
TERRITORY:                    T2 (também serve T12)
SOURCE_TYPE:                  BASE_OFICIAL
URL:                          https://www.arpa.sicilia.it/
ACCESS_METHOD:                HTML
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       ambiente;monitoraggio
GEOGRAPHIC_GRANULARITY:       REGIÃO — SICILIA
UPDATE_FREQUENCY:             observada por data visível na página: 2026-09-14
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   SIM — 2026-09-14
RAW_EVIDENCE_PRESERVABLE:     SIM — HTML obtido por HTTP
AUTOMATION_FEASIBILITY:       ALTA — rota estruturada declarada (API/opendata)
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Pubblicazioni - Arpa Sicilia»
                              https://www.arpa.sicilia.it/attivita/educazione-ambientale/pubblicazioni/ —
                              HTML, 158336 bytes lidos em 2026-09-14
ADAMA_USE_CASE:               agrometeorologia / clima / ambiente regional; alimenta T2 (clima/agua/solo),
                              T12 (politica e ambiente agricola)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T2-007/MANIFEST.json
VERDICT:                      GREEN — fonte aberta, exemplo real observado e preservado
```

#### IT-T2-008 · ARPAT Toscana

```
SOURCE_ID:                    IT-T2-008
SOURCE_NAME:                  ARPAT Toscana
SOURCE_OWNER:                 ARPAT
COUNTRY:                      ITALY
REGION:                       TOSCANA
LANGUAGE:                     IT-IT
TERRITORY:                    T2 (também serve T12)
SOURCE_TYPE:                  BASE_OFICIAL
URL:                          https://www.arpat.toscana.it/
ACCESS_METHOD:                HTML
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       ambiente;acque;monitoraggio
GEOGRAPHIC_GRANULARITY:       REGIÃO — TOSCANA
UPDATE_FREQUENCY:             observada por data visível na página: 2026-08-22
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   SIM — 2026-08-22
RAW_EVIDENCE_PRESERVABLE:     SIM — HTML obtido por HTTP
AUTOMATION_FEASIBILITY:       ALTA — rota estruturada declarada (API/opendata)
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Centrali geotermiche della Toscana – Anno 2025 - ARPAT»
                              https://www.arpat.toscana.it/pubblicazione/centrali-geotermiche-della-
                              toscana-anno-2025/ — HTML, 255196 bytes lidos em 2026-09-14
ADAMA_USE_CASE:               agrometeorologia / clima / ambiente regional; alimenta T2 (clima/agua/solo),
                              T12 (politica e ambiente agricola)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T2-008/MANIFEST.json
VERDICT:                      GREEN — fonte aberta, exemplo real observado e preservado
```

#### IT-T2-009 · ISPRA — Istituto Superiore per la Protezione e la Ricerca Ambientale

```
SOURCE_ID:                    IT-T2-009
SOURCE_NAME:                  ISPRA — Istituto Superiore per la Protezione e la Ricerca Ambientale
SOURCE_OWNER:                 ISPRA
COUNTRY:                      ITALY
REGION:                       NAZIONALE (sem recorte regional)
LANGUAGE:                     IT
TERRITORY:                    T2 (também serve T12)
SOURCE_TYPE:                  BASE_OFICIAL
URL:                          https://www.isprambiente.gov.it/it
ACCESS_METHOD:                PDF ligado a partir da página da fonte
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       ambiente;acque;suolo;indicatori
GEOGRAPHIC_GRANULARITY:       PAÍS — a fonte publica com alcance nacional
UPDATE_FREQUENCY:             observada por data visível na página: 2026-09-11
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   NÃO SEI — nenhuma data legível no item observado
RAW_EVIDENCE_PRESERVABLE:     SIM — PDF obtido por HTTP
AUTOMATION_FEASIBILITY:       ALTA — rota estruturada declarada (API/opendata)
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 https://www.isprambiente.gov.it/it/files/iso_9001-ita-c859101-2-20260709.pdf
                              — PDF, 129270 bytes lidos em 2026-09-14
ADAMA_USE_CASE:               instituto nacional de investigacao; alimenta T2 (clima/agua/solo), T12
                              (politica e ambiente agricola)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T2-009/MANIFEST.json
VERDICT:                      GREEN — fonte aberta, exemplo real observado e preservado
```

#### IT-T2-010 · APPA Trento — Agenzia provinciale protezione ambiente

```
SOURCE_ID:                    IT-T2-010
SOURCE_NAME:                  APPA Trento — Agenzia provinciale protezione ambiente
SOURCE_OWNER:                 Provincia autonoma di Trento
COUNTRY:                      ITALY
REGION:                       TRENTINO-ALTO ADIGE
LANGUAGE:                     IT
TERRITORY:                    T2 (também serve T12)
SOURCE_TYPE:                  BASE_OFICIAL
URL:                          https://appa.provincia.tn.it/
ACCESS_METHOD:                HTML
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       ambiente;acque
GEOGRAPHIC_GRANULARITY:       REGIÃO — TRENTINO-ALTO ADIGE
UPDATE_FREQUENCY:             NÃO SEI — nenhuma data de publicação legível na página
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   SIM — 2026-07-15
RAW_EVIDENCE_PRESERVABLE:     SIM — HTML obtido por HTTP
AUTOMATION_FEASIBILITY:       ALTA — rota estruturada declarada (API/opendata)
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Voluntary local review (VLR) 2026 / Approfondimenti / News / Homepage -
                              APPA» https://www.appa.provincia.tn.it/News/Approfondimenti/Voluntary-local-
                              review-VLR-2026 — HTML, 69245 bytes lidos em 2026-09-14
ADAMA_USE_CASE:               agrometeorologia / clima / ambiente regional; alimenta T2 (clima/agua/solo),
                              T12 (politica e ambiente agricola)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T2-010/MANIFEST.json
VERDICT:                      YELLOW — frequencia de atualizacao por provar
```

#### IT-T2-011 · ARPA Lombardia

```
SOURCE_ID:                    IT-T2-011
SOURCE_NAME:                  ARPA Lombardia
SOURCE_OWNER:                 ARPA Lombardia
COUNTRY:                      ITALY
REGION:                       LOMBARDIA
LANGUAGE:                     IT
TERRITORY:                    T2 (também serve T12)
SOURCE_TYPE:                  BASE_OFICIAL
URL:                          https://www.arpalombardia.it/
ACCESS_METHOD:                PDF ligado a partir da página da fonte
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       meteo;aria;acqua;agrometeo
GEOGRAPHIC_GRANULARITY:       REGIÃO — LOMBARDIA
UPDATE_FREQUENCY:             NÃO SEI — nenhuma data de publicação legível na página
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   NÃO SEI — nenhuma data legível no item observado
RAW_EVIDENCE_PRESERVABLE:     SIM — PDF obtido por HTTP
AUTOMATION_FEASIBILITY:       ALTA — rota estruturada declarada (API/opendata)
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Approfondisci qui
                              » https://www.arpalombardia.it/media/3filtsmf/la-montagna-che-cambia-crnv-
                              ottobre-2026.pdf — PDF, 704512 bytes lidos em 2026-09-14
ADAMA_USE_CASE:               agrometeorologia / clima / ambiente regional; alimenta T2 (clima/agua/solo),
                              T12 (politica e ambiente agricola)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T2-011/MANIFEST.json
VERDICT:                      YELLOW — frequencia de atualizacao por provar
```

#### IT-T2-012 · ARPA Friuli Venezia Giulia — OSMER

```
SOURCE_ID:                    IT-T2-012
SOURCE_NAME:                  ARPA Friuli Venezia Giulia — OSMER
SOURCE_OWNER:                 ARPA FVG
COUNTRY:                      ITALY
REGION:                       FRIULI-VENEZIA GIULIA
LANGUAGE:                     IT
TERRITORY:                    T2
SOURCE_TYPE:                  BASE_OFICIAL
URL:                          https://www.arpa.fvg.it/
ACCESS_METHOD:                HTML
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       meteo;agrometeo;OSMER
GEOGRAPHIC_GRANULARITY:       REGIÃO — FRIULI-VENEZIA GIULIA
UPDATE_FREQUENCY:             observada por data visível na página: 2026-08-19
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   SIM — 2026-09-09
RAW_EVIDENCE_PRESERVABLE:     SIM — HTML obtido por HTTP
AUTOMATION_FEASIBILITY:       ALTA — rota estruturada declarada (API/opendata)
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Le proposte per le scuole 2026/27
                              - ARPA FVG» https://www.arpa.fvg.it/temi/temi/educazione-ambientale/news/le-
                              proposte-per-le-scuole-202627/ — HTML, 99444 bytes lidos em 2026-09-14
ADAMA_USE_CASE:               agrometeorologia / clima / ambiente regional; alimenta T2 (clima/agua/solo)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T2-012/MANIFEST.json
VERDICT:                      GREEN — fonte aberta, exemplo real observado e preservado
```

#### IT-T2-013 · ARPA Lazio

```
SOURCE_ID:                    IT-T2-013
SOURCE_NAME:                  ARPA Lazio
SOURCE_OWNER:                 ARPA Lazio
COUNTRY:                      ITALY
REGION:                       LAZIO
LANGUAGE:                     IT-IT
TERRITORY:                    T2 (também serve T12)
SOURCE_TYPE:                  BASE_OFICIAL
URL:                          https://www.arpalazio.it/
ACCESS_METHOD:                HTML
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       ambiente;aria;acque
GEOGRAPHIC_GRANULARITY:       REGIÃO — LAZIO
UPDATE_FREQUENCY:             observada por data visível na página: 2026-09-13
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   NÃO SEI — nenhuma data legível no item observado
RAW_EVIDENCE_PRESERVABLE:     SIM — HTML obtido por HTTP
AUTOMATION_FEASIBILITY:       ALTA — rota estruturada declarada (API/opendata)
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Pubblicazioni - RIR - ARPA Lazio»
                              https://www.arpalazio.it/web/guest/ambiente/rir/pubblicazioni — HTML, 134725
                              bytes lidos em 2026-09-14
ADAMA_USE_CASE:               agrometeorologia / clima / ambiente regional; alimenta T2 (clima/agua/solo),
                              T12 (politica e ambiente agricola)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T2-013/MANIFEST.json
VERDICT:                      GREEN — fonte aberta, exemplo real observado e preservado
```

#### IT-T2-014 · ARPA Molise

```
SOURCE_ID:                    IT-T2-014
SOURCE_NAME:                  ARPA Molise
SOURCE_OWNER:                 ARPA Molise
COUNTRY:                      ITALY
REGION:                       MOLISE
LANGUAGE:                     IT-IT
TERRITORY:                    T2 (também serve T12)
SOURCE_TYPE:                  BASE_OFICIAL
URL:                          https://www.arpamolise.it/
ACCESS_METHOD:                PDF ligado a partir da página da fonte
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       ambiente;meteo
GEOGRAPHIC_GRANULARITY:       REGIÃO — MOLISE
UPDATE_FREQUENCY:             NÃO SEI — nenhuma data de publicação legível na página
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   NÃO SEI — nenhuma data legível no item observado
RAW_EVIDENCE_PRESERVABLE:     SIM — PDF obtido por HTTP
AUTOMATION_FEASIBILITY:       ALTA — rota estruturada declarada (API/opendata)
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 https://www.arpamolise.it/Comunicazione/Pubblicazioni/pdf/cartaservizi.pdf —
                              PDF, 704512 bytes lidos em 2026-09-14
ADAMA_USE_CASE:               agrometeorologia / clima / ambiente regional; alimenta T2 (clima/agua/solo),
                              T12 (politica e ambiente agricola)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T2-014/MANIFEST.json
VERDICT:                      YELLOW — frequencia de atualizacao por provar
```

#### IT-T2-015 · AIAM — Associazione Italiana di Agrometeorologia

```
SOURCE_ID:                    IT-T2-015
SOURCE_NAME:                  AIAM — Associazione Italiana di Agrometeorologia
SOURCE_OWNER:                 AIAM
COUNTRY:                      ITALY
REGION:                       NAZIONALE (sem recorte regional)
LANGUAGE:                     IT-IT
TERRITORY:                    T2 (também serve T5, T11)
SOURCE_TYPE:                  ORGANIZACAO
URL:                          https://www.agrometeorologia.it/
ACCESS_METHOD:                PDF ligado a partir da página da fonte
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       agrometeorologia;convegno
GEOGRAPHIC_GRANULARITY:       PAÍS — a fonte publica com alcance nacional
UPDATE_FREQUENCY:             NÃO SEI
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   NÃO SEI — nenhuma data legível no item observado
RAW_EVIDENCE_PRESERVABLE:     SIM — PDF obtido por HTTP
AUTOMATION_FEASIBILITY:       ALTA — rota estruturada declarada (API/opendata)
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Brochure» https://www.agrometeorologia.it/wp-
                              content/uploads/2021/03/2021_brochure_it.pdf — PDF, 534701 bytes lidos em
                              2026-09-14
ADAMA_USE_CASE:               agrometeorologia / clima / ambiente regional; alimenta T2 (clima/agua/solo),
                              T5 (ciencia), T11 (eventos)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T2-015/MANIFEST.json
VERDICT:                      GREEN — fonte aberta, exemplo real observado e preservado
```

#### IT-T2-016 · ARPA Marche

```
SOURCE_ID:                    IT-T2-016
SOURCE_NAME:                  ARPA Marche
SOURCE_OWNER:                 ARPAM
COUNTRY:                      ITALY
REGION:                       MARCHE
LANGUAGE:                     IT-IT
TERRITORY:                    T2 (também serve T12)
SOURCE_TYPE:                  BASE_OFICIAL
URL:                          https://www.arpa.marche.it/
ACCESS_METHOD:                PDF ligado a partir da página da fonte
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       ambiente;meteo
GEOGRAPHIC_GRANULARITY:       REGIÃO — MARCHE
UPDATE_FREQUENCY:             observada por data visível na página: 2026-08-18
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   NÃO SEI — nenhuma data legível no item observado
RAW_EVIDENCE_PRESERVABLE:     SIM — PDF obtido por HTTP
AUTOMATION_FEASIBILITY:       MÉDIA-ALTA — feed ou ficheiro previsível
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Tariffario»
                              https://www.arpa.marche.it/images/pdf/agenzia/TARIFFARIO_2026.pdf — PDF,
                              704512 bytes lidos em 2026-09-14
ADAMA_USE_CASE:               agrometeorologia / clima / ambiente regional; alimenta T2 (clima/agua/solo),
                              T12 (politica e ambiente agricola)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T2-016/MANIFEST.json
VERDICT:                      GREEN — fonte aberta, exemplo real observado e preservado
```

#### IT-T2-017 · CNR IRET — Istituto di Ricerca sugli Ecosistemi Terrestri

```
SOURCE_ID:                    IT-T2-017
SOURCE_NAME:                  CNR IRET — Istituto di Ricerca sugli Ecosistemi Terrestri
SOURCE_OWNER:                 CNR
COUNTRY:                      ITALY
REGION:                       NAZIONALE (sem recorte regional)
LANGUAGE:                     IT-IT
TERRITORY:                    T2 (também serve T5)
SOURCE_TYPE:                  CIENCIA
URL:                          https://www.iret.cnr.it/
ACCESS_METHOD:                HTML
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       ecosistemi;suolo
GEOGRAPHIC_GRANULARITY:       PAÍS — a fonte publica com alcance nacional
UPDATE_FREQUENCY:             observada por data visível na página: 2026-05-22
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   NÃO SEI — nenhuma data legível no item observado
RAW_EVIDENCE_PRESERVABLE:     SIM — HTML obtido por HTTP
AUTOMATION_FEASIBILITY:       ALTA — rota estruturada declarada (API/opendata)
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «News - IRET» https://www.iret.cnr.it/news/ — HTML, 86868 bytes lidos em
                              2026-09-14
ADAMA_USE_CASE:               instituto nacional de investigacao; alimenta T2 (clima/agua/solo), T5
                              (ciencia)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T2-017/MANIFEST.json
VERDICT:                      GREEN — fonte aberta, exemplo real observado e preservado
```

#### IT-T2-018 · CNR ISAFOM — Istituto per i Sistemi Agricoli e Forestali del Mediterraneo

```
SOURCE_ID:                    IT-T2-018
SOURCE_NAME:                  CNR ISAFOM — Istituto per i Sistemi Agricoli e Forestali del Mediterraneo
SOURCE_OWNER:                 CNR
COUNTRY:                      ITALY
REGION:                       CAMPANIA
LANGUAGE:                     IT-IT
TERRITORY:                    T2 (também serve T1, T5)
SOURCE_TYPE:                  CIENCIA
URL:                          https://www.isafom.cnr.it/
ACCESS_METHOD:                HTML
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       agrosistemi mediterranei;acqua;suolo
GEOGRAPHIC_GRANULARITY:       REGIÃO — CAMPANIA
UPDATE_FREQUENCY:             observada por data visível na página: 2025-06-27
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   SIM — 2025-06-27
RAW_EVIDENCE_PRESERVABLE:     SIM — HTML obtido por HTTP
AUTOMATION_FEASIBILITY:       ALTA — rota estruturada declarada (API/opendata)
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «News Archivi - CNR - ISAFOM» https://isafom.cnr.it/category/news/ — HTML,
                              101741 bytes lidos em 2026-09-14
ADAMA_USE_CASE:               instituto nacional de investigacao; alimenta T2 (clima/agua/solo), T1
                              (cultura e producao), T5 (ciencia)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T2-018/MANIFEST.json
VERDICT:                      GREEN — fonte aberta, exemplo real observado e preservado
```

#### IT-T2-019 · ARPA Piemonte

```
SOURCE_ID:                    IT-T2-019
SOURCE_NAME:                  ARPA Piemonte
SOURCE_OWNER:                 ARPA Piemonte
COUNTRY:                      ITALY
REGION:                       PIEMONTE
LANGUAGE:                     IT
TERRITORY:                    T2 (também serve T12)
SOURCE_TYPE:                  BASE_OFICIAL
URL:                          https://www.arpa.piemonte.it/home
ACCESS_METHOD:                HTML
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       meteo;clima;agrometeorologia
GEOGRAPHIC_GRANULARITY:       REGIÃO — PIEMONTE
UPDATE_FREQUENCY:             NÃO SEI — nenhuma data de publicação legível na página
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   NÃO SEI — nenhuma data legível no item observado
RAW_EVIDENCE_PRESERVABLE:     SIM — HTML obtido por HTTP
AUTOMATION_FEASIBILITY:       MÉDIA — site navegável, sem rota estruturada declarada
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «La Relazione sullo Stato dell&#039;Ambiente del Piemonte 2026 | Arpa
                              Piemonte» https://www.arpa.piemonte.it/notizia/relazione-sullo-stato-
                              dellambiente-piemonte-2026 — HTML, 84390 bytes lidos em 2026-09-14
ADAMA_USE_CASE:               agrometeorologia / clima / ambiente regional; alimenta T2 (clima/agua/solo),
                              T12 (politica e ambiente agricola)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T2-019/MANIFEST.json
VERDICT:                      YELLOW — frequencia de atualizacao por provar
```

#### IT-T2-020 · ARTA Abruzzo

```
SOURCE_ID:                    IT-T2-020
SOURCE_NAME:                  ARTA Abruzzo
SOURCE_OWNER:                 ARTA Abruzzo
COUNTRY:                      ITALY
REGION:                       ABRUZZO
LANGUAGE:                     IT
TERRITORY:                    T2 (também serve T12)
SOURCE_TYPE:                  BASE_OFICIAL
URL:                          https://www.artaabruzzo.it/
ACCESS_METHOD:                PDF ligado a partir da página da fonte
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       ambiente;monitoraggio
GEOGRAPHIC_GRANULARITY:       REGIÃO — ABRUZZO
UPDATE_FREQUENCY:             observada por data visível na página: 2026-07-27
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   NÃO SEI — nenhuma data legível no item observado
RAW_EVIDENCE_PRESERVABLE:     SIM — PDF obtido por HTTP
AUTOMATION_FEASIBILITY:       MÉDIA-ALTA — feed ou ficheiro previsível
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 NÃO REPRESENTATIVO — o item que se conseguiu confirmar por HTTP e' papelada administrativa (codigo etico, termos, formulario) — prova que a organizacao existe, NAO prova o que ela publica na sua area tecnica. Um exemplo representativo exige navegador ou leitura humana da seccao de noticias.
ADAMA_USE_CASE:               agrometeorologia / clima / ambiente regional; alimenta T2 (clima/agua/solo),
                              T12 (politica e ambiente agricola)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T2-020/MANIFEST.json
VERDICT:                      YELLOW — registada como real e util, mas sem exemplo representativo do que entrega; rever com navegador antes de contratar coleta.
```

#### IT-T2-021 · ARPA Liguria

```
SOURCE_ID:                    IT-T2-021
SOURCE_NAME:                  ARPA Liguria
SOURCE_OWNER:                 ARPAL
COUNTRY:                      ITALY
REGION:                       LIGURIA
LANGUAGE:                     IT-IT
TERRITORY:                    T2 (também serve T12)
SOURCE_TYPE:                  BASE_OFICIAL
URL:                          https://www.arpal.liguria.it/
ACCESS_METHOD:                HTML
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       meteo;ambiente;allerta
GEOGRAPHIC_GRANULARITY:       REGIÃO — LIGURIA
UPDATE_FREQUENCY:             NÃO SEI — nenhuma data de publicação legível na página
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   SIM — 2026-09-07
RAW_EVIDENCE_PRESERVABLE:     SIM — HTML obtido por HTTP
AUTOMATION_FEASIBILITY:       MÉDIA — site navegável, sem rota estruturada declarada
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Notizie tematiche - Estate 2026, a Genova quasi 90 notti tropicali e 60
                              “più che tropicali” - Arpal Liguria» https://www.arpal.liguria.it/home-
                              page/notizie-tematiche/item/estate-2026-a-genova-quasi-90-notti-
                              tropicali-e-60-piu-che-tropicali.html — HTML, 37187 bytes lidos em
                              2026-09-14
ADAMA_USE_CASE:               agrometeorologia / clima / ambiente regional; alimenta T2 (clima/agua/solo),
                              T12 (politica e ambiente agricola)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T2-021/MANIFEST.json
VERDICT:                      YELLOW — frequencia de atualizacao por provar
```

#### IT-T2-022 · ARPA Valle d'Aosta

```
SOURCE_ID:                    IT-T2-022
SOURCE_NAME:                  ARPA Valle d'Aosta
SOURCE_OWNER:                 ARPA Valle d'Aosta
COUNTRY:                      ITALY
REGION:                       VALLE D'AOSTA
LANGUAGE:                     IT-IT
TERRITORY:                    T2 (também serve T12)
SOURCE_TYPE:                  BASE_OFICIAL
URL:                          https://www.arpa.vda.it/
ACCESS_METHOD:                HTML
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       ambiente;meteo alpino;neve
GEOGRAPHIC_GRANULARITY:       REGIÃO — VALLE D'AOSTA
UPDATE_FREQUENCY:             NÃO SEI — nenhuma data de publicação legível na página
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   NÃO SEI — nenhuma data legível no item observado
RAW_EVIDENCE_PRESERVABLE:     SIM — HTML obtido por HTTP
AUTOMATION_FEASIBILITY:       MÉDIA — site navegável, sem rota estruturada declarada
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Agenzia Regionale della Protezione dell'Ambiente - Valle D'Aosta»
                              https://www.arpa.vda.it/component/tags/tag/bollettini — HTML, 108827 bytes
                              lidos em 2026-09-14
ADAMA_USE_CASE:               agrometeorologia / clima / ambiente regional; alimenta T2 (clima/agua/solo),
                              T12 (politica e ambiente agricola)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T2-022/MANIFEST.json
VERDICT:                      YELLOW — frequencia de atualizacao por provar
```

#### IT-T2-023 · ARPA Basilicata

```
SOURCE_ID:                    IT-T2-023
SOURCE_NAME:                  ARPA Basilicata
SOURCE_OWNER:                 ARPAB
COUNTRY:                      ITALY
REGION:                       BASILICATA
LANGUAGE:                     IT-IT
TERRITORY:                    T2 (também serve T12)
SOURCE_TYPE:                  BASE_OFICIAL
URL:                          https://www.arpab.it/
ACCESS_METHOD:                HTML
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       ambiente;monitoraggio
GEOGRAPHIC_GRANULARITY:       REGIÃO — BASILICATA
UPDATE_FREQUENCY:             observada por data visível na página: 2026-09-04
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   NÃO SEI — nenhuma data legível no item observado
RAW_EVIDENCE_PRESERVABLE:     SIM — TEXTO obtido por HTTP
AUTOMATION_FEASIBILITY:       ALTA — rota estruturada declarada (API/opendata)
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «VEDI TUTTE                                                       VEDI
                              TUTTE» https://www.arpab.it/articoli/news/arpa-informa/ — TEXTO, 397716
                              bytes lidos em 2026-09-14
ADAMA_USE_CASE:               agrometeorologia / clima / ambiente regional; alimenta T2 (clima/agua/solo),
                              T12 (politica e ambiente agricola)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T2-023/MANIFEST.json
VERDICT:                      GREEN — fonte aberta, exemplo real observado e preservado
```

#### IT-T2-024 · ANBI — Associazione Nazionale Consorzi di gestione e tutela del territorio e acque irrigue

```
SOURCE_ID:                    IT-T2-024
SOURCE_NAME:                  ANBI — Associazione Nazionale Consorzi di gestione e tutela del territorio e
                              acque irrigue
SOURCE_OWNER:                 ANBI
COUNTRY:                      ITALY
REGION:                       NAZIONALE (sem recorte regional)
LANGUAGE:                     IT
TERRITORY:                    T2 (também serve T12)
SOURCE_TYPE:                  ORGANIZACAO
URL:                          https://www.anbi.it/
ACCESS_METHOD:                PDF ligado a partir da página da fonte
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       consorzi di bonifica;irrigazione
GEOGRAPHIC_GRANULARITY:       PAÍS — a fonte publica com alcance nacional
UPDATE_FREQUENCY:             observada por data visível na página: 2026-09-14
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   NÃO SEI — nenhuma data legível no item observado
RAW_EVIDENCE_PRESERVABLE:     SIM — PDF obtido por HTTP
AUTOMATION_FEASIBILITY:       MÉDIA-ALTA — feed ou ficheiro previsível
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «LIPU» https://www.anbi.it/public/sezioni/protocollolipu-firmato-
                              pdf-20260303161103.pdf — PDF, 704512 bytes lidos em 2026-09-14
ADAMA_USE_CASE:               organizacao agricola / representacao de produtores; alimenta T2
                              (clima/agua/solo), T12 (politica e ambiente agricola)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T2-024/MANIFEST.json
VERDICT:                      GREEN — fonte aberta, exemplo real observado e preservado
```

### T3 · PEST / DISEASE / WEEDS — ITALY · onda 1 (2026-09-14)

*9 fontes registradas nesta secção. Cada uma foi aberta, observada e tem exemplo real preservado em `data/samples/IT-SOURCE-SAMPLES/<SOURCE_ID>/`. Registada ≠ contratada: nenhuma tem contrato de busca, e nenhuma coleta foi corrida.*

#### IT-T3-013 · Emilia-Romagna — Servizio Fitosanitario

```
SOURCE_ID:                    IT-T3-013
SOURCE_NAME:                  Emilia-Romagna — Servizio Fitosanitario
SOURCE_OWNER:                 Regione Emilia-Romagna
COUNTRY:                      ITALY
REGION:                       EMILIA-ROMAGNA
LANGUAGE:                     IT
TERRITORY:                    T3 (também serve T4)
SOURCE_TYPE:                  BASE_OFICIAL
URL:                          https://agricoltura.regione.emilia-romagna.it/fitosanitario
ACCESS_METHOD:                HTML
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       servizio fitosanitario;bollettini
GEOGRAPHIC_GRANULARITY:       REGIÃO — EMILIA-ROMAGNA
UPDATE_FREQUENCY:             NÃO SEI — nenhuma data de publicação legível na página
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   SIM — 2026-02-05
RAW_EVIDENCE_PRESERVABLE:     SIM — HTML obtido por HTTP
AUTOMATION_FEASIBILITY:       ALTA — rota estruturada declarada (API/opendata)
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Bollettini interprovinciali di produzione integrata e biologica 2026 -
                              Fitosanitario e difesa delle produzioni - Agricoltura, caccia e pesca»
                              https://agricoltura.regione.emilia-romagna.it/fitosanitario/difesa-
                              sostenibile/bollettini/bollettini-interprovinciali-di-produzione-integrata-
                              e-biologica-2026 — HTML, 704512 bytes lidos em 2026-09-14
ADAMA_USE_CASE:               servico fitossanitario / defesa vegetal; alimenta T3 (praga, doenca e
                              infestantes), T4 (regulatorio)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T3-013/MANIFEST.json
VERDICT:                      YELLOW — frequencia de atualizacao por provar
```

#### IT-T3-014 · Servizio Fitosanitario Nazionale — Protezione delle Piante

```
SOURCE_ID:                    IT-T3-014
SOURCE_NAME:                  Servizio Fitosanitario Nazionale — Protezione delle Piante
SOURCE_OWNER:                 MASAF — Servizio Fitosanitario Centrale
COUNTRY:                      ITALY
REGION:                       NAZIONALE (sem recorte regional)
LANGUAGE:                     IT-IT
TERRITORY:                    T3 (também serve T4)
SOURCE_TYPE:                  BASE_OFICIAL
URL:                          https://www.protezionedellepiante.it/
ACCESS_METHOD:                HTML
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       fitosanitario;organismi nocivi;quarantena
GEOGRAPHIC_GRANULARITY:       PAÍS — a fonte publica com alcance nacional
UPDATE_FREQUENCY:             observada por data visível na página: 2026-09-14
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   SIM — 2026-09-14
RAW_EVIDENCE_PRESERVABLE:     SIM — HTML obtido por HTTP
AUTOMATION_FEASIBILITY:       ALTA — rota estruturada declarada (API/opendata)
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Articoli Archivi - Protezione delle piante»
                              https://www.protezionedellepiante.it/category/articoli/ — HTML, 416737 bytes
                              lidos em 2026-09-14
ADAMA_USE_CASE:               servico fitossanitario / defesa vegetal; alimenta T3 (praga, doenca e
                              infestantes), T4 (regulatorio)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T3-014/MANIFEST.json
VERDICT:                      GREEN — fonte aberta, exemplo real observado e preservado
```

#### IT-T3-015 · Toscana — Servizio Fitosanitario Regionale

```
SOURCE_ID:                    IT-T3-015
SOURCE_NAME:                  Toscana — Servizio Fitosanitario Regionale
SOURCE_OWNER:                 Regione Toscana
COUNTRY:                      ITALY
REGION:                       TOSCANA
LANGUAGE:                     IT-IT
TERRITORY:                    T3 (também serve T4)
SOURCE_TYPE:                  BASE_OFICIAL
URL:                          https://www.regione.toscana.it/
ACCESS_METHOD:                HTML
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       servizio fitosanitario
GEOGRAPHIC_GRANULARITY:       REGIÃO — TOSCANA
UPDATE_FREQUENCY:             observada por data visível na página: 2026-09-14
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   NÃO SEI — nenhuma data legível no item observado
RAW_EVIDENCE_PRESERVABLE:     SIM — HTML obtido por HTTP
AUTOMATION_FEASIBILITY:       ALTA — rota estruturada declarada (API/opendata)
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Approfondimenti - Regione Toscana»
                              https://www.regione.toscana.it/regione/approfondimenti — HTML, 164237 bytes
                              lidos em 2026-09-14
ADAMA_USE_CASE:               servico fitossanitario / defesa vegetal; alimenta T3 (praga, doenca e
                              infestantes), T4 (regulatorio)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T3-015/MANIFEST.json
VERDICT:                      GREEN — fonte aberta, exemplo real observado e preservado
```

#### IT-T3-016 · Veneto — Servizio Fitosanitario Regionale

```
SOURCE_ID:                    IT-T3-016
SOURCE_NAME:                  Veneto — Servizio Fitosanitario Regionale
SOURCE_OWNER:                 Regione Veneto
COUNTRY:                      ITALY
REGION:                       VENETO
LANGUAGE:                     IT-IT
TERRITORY:                    T3 (também serve T4)
SOURCE_TYPE:                  BASE_OFICIAL
URL:                          https://www.regione.veneto.it/web/agricoltura-e-foreste
ACCESS_METHOD:                HTML
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       servizio fitosanitario
GEOGRAPHIC_GRANULARITY:       REGIÃO — VENETO
UPDATE_FREQUENCY:             observada por data visível na página: 2026-08-17
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   NÃO SEI — nenhuma data legível no item observado
RAW_EVIDENCE_PRESERVABLE:     SIM — HTML obtido por HTTP
AUTOMATION_FEASIBILITY:       ALTA — rota estruturada declarada (API/opendata)
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Newsletter - Regione del Veneto»
                              https://www.regione.veneto.it/web/guest/newsletter — HTML, 41256 bytes lidos
                              em 2026-09-14
ADAMA_USE_CASE:               servico fitossanitario / defesa vegetal; alimenta T3 (praga, doenca e
                              infestantes), T4 (regulatorio)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T3-016/MANIFEST.json
VERDICT:                      GREEN — fonte aberta, exemplo real observado e preservado
```

#### IT-T3-017 · CNR IPSP — Istituto per la Protezione Sostenibile delle Piante

```
SOURCE_ID:                    IT-T3-017
SOURCE_NAME:                  CNR IPSP — Istituto per la Protezione Sostenibile delle Piante
SOURCE_OWNER:                 CNR
COUNTRY:                      ITALY
REGION:                       NAZIONALE (sem recorte regional)
LANGUAGE:                     IT-IT
TERRITORY:                    T3 (também serve T5, T6)
SOURCE_TYPE:                  CIENCIA
URL:                          http://www.ipsp.cnr.it/
ACCESS_METHOD:                HTML
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       patologia vegetale;entomologia;biocontrollo
GEOGRAPHIC_GRANULARITY:       PAÍS — a fonte publica com alcance nacional
UPDATE_FREQUENCY:             observada por data visível na página: 2026-07-04
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   SIM — 2026-07-04
RAW_EVIDENCE_PRESERVABLE:     SIM — HTML obtido por HTTP
AUTOMATION_FEASIBILITY:       ALTA — rota estruturada declarada (API/opendata)
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Notizie &#8211; IPSP» http://www.ipsp.cnr.it/notizie/ — HTML, 72467 bytes
                              lidos em 2026-09-14
ADAMA_USE_CASE:               instituto nacional de investigacao; alimenta T3 (praga, doenca e
                              infestantes), T5 (ciencia), T6 (pesquisadores)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T3-017/MANIFEST.json
VERDICT:                      YELLOW — so responde em HTTP
```

#### IT-T3-018 · CNR ISPA — Istituto di Scienze delle Produzioni Alimentari

```
SOURCE_ID:                    IT-T3-018
SOURCE_NAME:                  CNR ISPA — Istituto di Scienze delle Produzioni Alimentari
SOURCE_OWNER:                 CNR
COUNTRY:                      ITALY
REGION:                       PUGLIA
LANGUAGE:                     EN-US
TERRITORY:                    T3 (também serve T5)
SOURCE_TYPE:                  CIENCIA
URL:                          https://www.ispa.cnr.it/
ACCESS_METHOD:                HTML
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       micotossine;sicurezza alimentare;Fusarium
GEOGRAPHIC_GRANULARITY:       REGIÃO — PUGLIA
UPDATE_FREQUENCY:             NÃO SEI — nenhuma data de publicação legível na página
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   NÃO SEI — nenhuma data legível no item observado
RAW_EVIDENCE_PRESERVABLE:     SIM — HTML obtido por HTTP
AUTOMATION_FEASIBILITY:       MÉDIA — site navegável, sem rota estruturada declarada
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «ISPA - CNR News & Eventi ISPA» https://www.ispa.cnr.it/news-e-eventi —
                              HTML, 12265 bytes lidos em 2026-09-14
ADAMA_USE_CASE:               instituto nacional de investigacao; alimenta T3 (praga, doenca e
                              infestantes), T5 (ciencia)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T3-018/MANIFEST.json
VERDICT:                      YELLOW — frequencia de atualizacao por provar
```

#### IT-T3-019 · Agroinnova — Centro di Competenza per l'Innovazione in campo agro-ambientale

```
SOURCE_ID:                    IT-T3-019
SOURCE_NAME:                  Agroinnova — Centro di Competenza per l'Innovazione in campo agro-ambientale
SOURCE_OWNER:                 Universita di Torino
COUNTRY:                      ITALY
REGION:                       PIEMONTE
LANGUAGE:                     IT
TERRITORY:                    T3 (também serve T5, T6)
SOURCE_TYPE:                  CIENCIA
URL:                          https://www.agroinnova.unito.it/it
ACCESS_METHOD:                HTML
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       patologia vegetale;difesa;sostenibilita
GEOGRAPHIC_GRANULARITY:       REGIÃO — PIEMONTE
UPDATE_FREQUENCY:             NÃO SEI — nenhuma data de publicação legível na página
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   SIM — 2026-06-04
RAW_EVIDENCE_PRESERVABLE:     SIM — HTML obtido por HTTP
AUTOMATION_FEASIBILITY:       MÉDIA-ALTA — feed ou ficheiro previsível
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Progetti di Ricerca | Centro Interdipartimentale per l&#039;Innovazione in
                              campo Agro-ambientale – AGROINNOVA»
                              https://www.agroinnova.unito.it/it/ricerca/progetti-di-ricerca — HTML, 69444
                              bytes lidos em 2026-09-14
ADAMA_USE_CASE:               universidade / departamento agrario; alimenta T3 (praga, doenca e
                              infestantes), T5 (ciencia), T6 (pesquisadores)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T3-019/MANIFEST.json
VERDICT:                      YELLOW — frequencia de atualizacao por provar
```

#### IT-T3-020 · Societa Entomologica Italiana

```
SOURCE_ID:                    IT-T3-020
SOURCE_NAME:                  Societa Entomologica Italiana
SOURCE_OWNER:                 SEI
COUNTRY:                      ITALY
REGION:                       NAZIONALE (sem recorte regional)
LANGUAGE:                     IT-IT
TERRITORY:                    T3 (também serve T5)
SOURCE_TYPE:                  ORGANIZACAO
URL:                          https://www.societaentomologicaitaliana.it/
ACCESS_METHOD:                PDF ligado a partir da página da fonte
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       entomologia;insetti
GEOGRAPHIC_GRANULARITY:       PAÍS — a fonte publica com alcance nacional
UPDATE_FREQUENCY:             observada por data visível na página: 2026-07-07
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   NÃO SEI — nenhuma data legível no item observado
RAW_EVIDENCE_PRESERVABLE:     SIM — PDF obtido por HTTP
AUTOMATION_FEASIBILITY:       ALTA — rota estruturada declarada (API/opendata)
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Approfondisci» https://www.societaentomologicaitaliana.it/wp-
                              content/uploads/2024/11/Volantino_Esapodi.pdf — PDF, 716081 bytes lidos em
                              2026-09-14
ADAMA_USE_CASE:               sociedade cientifica / academia; alimenta T3 (praga, doenca e infestantes),
                              T5 (ciencia)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T3-020/MANIFEST.json
VERDICT:                      GREEN — fonte aberta, exemplo real observado e preservado
```

#### IT-T3-021 · SIPaV — Societa Italiana di Patologia Vegetale

```
SOURCE_ID:                    IT-T3-021
SOURCE_NAME:                  SIPaV — Societa Italiana di Patologia Vegetale
SOURCE_OWNER:                 SIPaV
COUNTRY:                      ITALY
REGION:                       NAZIONALE (sem recorte regional)
LANGUAGE:                     IT-IT
TERRITORY:                    T3 (também serve T5, T6)
SOURCE_TYPE:                  ORGANIZACAO
URL:                          https://www.sipav.org/
ACCESS_METHOD:                HTML
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       patologia vegetale;congresso
GEOGRAPHIC_GRANULARITY:       PAÍS — a fonte publica com alcance nacional
UPDATE_FREQUENCY:             NÃO SEI — nenhuma data de publicação legível na página
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   NÃO SEI — nenhuma data legível no item observado
RAW_EVIDENCE_PRESERVABLE:     SIM — HTML obtido por HTTP
AUTOMATION_FEASIBILITY:       MÉDIA-ALTA — feed ou ficheiro previsível
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «SIPaV News» https://www.sipav.org/it/12/News/ — HTML, 22197 bytes lidos em
                              2026-09-14
ADAMA_USE_CASE:               sociedade cientifica / academia; alimenta T3 (praga, doenca e infestantes),
                              T5 (ciencia), T6 (pesquisadores)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T3-021/MANIFEST.json
VERDICT:                      YELLOW — frequencia de atualizacao por provar
```

### T5 · SCIENCE — ITALY · onda 1 (2026-09-14)

*31 fontes registradas nesta secção. Cada uma foi aberta, observada e tem exemplo real preservado em `data/samples/IT-SOURCE-SAMPLES/<SOURCE_ID>/`. Registada ≠ contratada: nenhuma tem contrato de busca, e nenhuma coleta foi corrida.*

#### IT-T5-006 · CNR — Consiglio Nazionale delle Ricerche

```
SOURCE_ID:                    IT-T5-006
SOURCE_NAME:                  CNR — Consiglio Nazionale delle Ricerche
SOURCE_OWNER:                 CNR
COUNTRY:                      ITALY
REGION:                       NAZIONALE (sem recorte regional)
LANGUAGE:                     IT
TERRITORY:                    T5 (também serve T6)
SOURCE_TYPE:                  ORGANIZACAO
URL:                          https://www.cnr.it/
ACCESS_METHOD:                HTML
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       ricerca;istituti
GEOGRAPHIC_GRANULARITY:       PAÍS — a fonte publica com alcance nacional
UPDATE_FREQUENCY:             observada por data visível na página: 2026-09-14
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   SIM — 2026-09-11
RAW_EVIDENCE_PRESERVABLE:     SIM — HTML obtido por HTTP
AUTOMATION_FEASIBILITY:       MÉDIA-ALTA — feed ou ficheiro previsível
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «L&#039;enigma del Medioevo a Grotta Romanelli: tre corpi e un mistero lungo
                              millenni | Consiglio Nazionale delle Ricerche»
                              https://www.cnr.it/it/news/14617/l-enigma-del-medioevo-a-grotta-romanelli-
                              tre-corpi-e-un-mistero-lungo-millenni — HTML, 45559 bytes lidos em
                              2026-09-14
ADAMA_USE_CASE:               instituto nacional de investigacao; alimenta T5 (ciencia), T6
                              (pesquisadores)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T5-006/MANIFEST.json
VERDICT:                      GREEN — fonte aberta, exemplo real observado e preservado
```

#### IT-T5-007 · Institut Agricole Regional — Aosta

```
SOURCE_ID:                    IT-T5-007
SOURCE_NAME:                  Institut Agricole Regional — Aosta
SOURCE_OWNER:                 Institut Agricole Regional
COUNTRY:                      ITALY
REGION:                       VALLE D'AOSTA
LANGUAGE:                     IT-IT
TERRITORY:                    T5 (também serve T1, T7)
SOURCE_TYPE:                  ORGANIZACAO
URL:                          https://www.iaraosta.it/
ACCESS_METHOD:                PDF ligado a partir da página da fonte
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       ricerca;formazione;viticoltura alpina
GEOGRAPHIC_GRANULARITY:       REGIÃO — VALLE D'AOSTA
UPDATE_FREQUENCY:             observada por data visível na página: 2026-08-12
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   NÃO SEI — nenhuma data legível no item observado
RAW_EVIDENCE_PRESERVABLE:     SIM — PDF obtido por HTTP
AUTOMATION_FEASIBILITY:       ALTA — rota estruturada declarada (API/opendata)
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Carta della Qualità» https://www.iaraosta.it/wp-
                              content/uploads/2026/07/Carta-della-qualita-FIRMATA.pdf — PDF, 704512 bytes
                              lidos em 2026-09-14
ADAMA_USE_CASE:               agencia regional agricola; alimenta T5 (ciencia), T1 (cultura e producao),
                              T7 (rede tecnica)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T5-007/MANIFEST.json
VERDICT:                      GREEN — fonte aberta, exemplo real observado e preservado
```

#### IT-T5-008 · Fondazione Agrion — Fondazione per la ricerca l'innovazione e lo sviluppo tecnologico dell'agricoltura piemontese

```
SOURCE_ID:                    IT-T5-008
SOURCE_NAME:                  Fondazione Agrion — Fondazione per la ricerca l'innovazione e lo sviluppo
                              tecnologico dell'agricoltura piemontese
SOURCE_OWNER:                 Fondazione Agrion
COUNTRY:                      ITALY
REGION:                       PIEMONTE
LANGUAGE:                     IT-IT
TERRITORY:                    T5 (também serve T3, T1)
SOURCE_TYPE:                  CIENCIA
URL:                          https://www.agrion.it/
ACCESS_METHOD:                PDF ligado a partir da página da fonte
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       frutticoltura;viticoltura;sperimentazione
GEOGRAPHIC_GRANULARITY:       REGIÃO — PIEMONTE
UPDATE_FREQUENCY:             observada por data visível na página: 2026-06-10
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   NÃO SEI — nenhuma data legível no item observado
RAW_EVIDENCE_PRESERVABLE:     SIM — PDF obtido por HTTP
AUTOMATION_FEASIBILITY:       ALTA — rota estruturada declarada (API/opendata)
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 NÃO REPRESENTATIVO — o item que se conseguiu confirmar por HTTP e' papelada administrativa (codigo etico, termos, formulario) — prova que a organizacao existe, NAO prova o que ela publica na sua area tecnica. Um exemplo representativo exige navegador ou leitura humana da seccao de noticias.
ADAMA_USE_CASE:               centro de investigacao aplicada / experimentacao; alimenta T5 (ciencia), T3
                              (praga, doenca e infestantes), T1 (cultura e producao)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T5-008/MANIFEST.json
VERDICT:                      YELLOW — registada como real e util, mas sem exemplo representativo do que entrega; rever com navegador antes de contratar coleta.
```

#### IT-T5-009 · Fondazione Minoprio

```
SOURCE_ID:                    IT-T5-009
SOURCE_NAME:                  Fondazione Minoprio
SOURCE_OWNER:                 Fondazione Minoprio
COUNTRY:                      ITALY
REGION:                       LOMBARDIA
LANGUAGE:                     IT-IT
TERRITORY:                    T5 (também serve T7, T1)
SOURCE_TYPE:                  ORGANIZACAO
URL:                          https://www.fondazioneminoprio.it/
ACCESS_METHOD:                PDF ligado a partir da página da fonte
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       formazione;floricoltura;sperimentazione
GEOGRAPHIC_GRANULARITY:       REGIÃO — LOMBARDIA
UPDATE_FREQUENCY:             observada por data visível na página: 2026-05-15
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   NÃO SEI — nenhuma data legível no item observado
RAW_EVIDENCE_PRESERVABLE:     SIM — PDF obtido por HTTP
AUTOMATION_FEASIBILITY:       ALTA — rota estruturada declarada (API/opendata)
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Regolamento» https://www.fondazioneminoprio.it/wp-
                              content/uploads/2025/04/REGOLAMENTO-FM-2025-26.pdf — PDF, 445797 bytes lidos
                              em 2026-09-14
ADAMA_USE_CASE:               centro de investigacao aplicada / experimentacao; alimenta T5 (ciencia), T7
                              (rede tecnica), T1 (cultura e producao)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T5-009/MANIFEST.json
VERDICT:                      GREEN — fonte aberta, exemplo real observado e preservado
```

#### IT-T5-010 · Fondazione per l'Agricoltura F.lli Navarra

```
SOURCE_ID:                    IT-T5-010
SOURCE_NAME:                  Fondazione per l'Agricoltura F.lli Navarra
SOURCE_OWNER:                 Fondazione Navarra
COUNTRY:                      ITALY
REGION:                       EMILIA-ROMAGNA
LANGUAGE:                     IT-IT
TERRITORY:                    T5 (também serve T1)
SOURCE_TYPE:                  CIENCIA
URL:                          https://www.fondazionenavarra.it/
ACCESS_METHOD:                PDF ligado a partir da página da fonte
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       frutticoltura;sperimentazione
GEOGRAPHIC_GRANULARITY:       REGIÃO — EMILIA-ROMAGNA
UPDATE_FREQUENCY:             observada por data visível na página: 2026-05-15
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   NÃO SEI — nenhuma data legível no item observado
RAW_EVIDENCE_PRESERVABLE:     SIM — PDF obtido por HTTP
AUTOMATION_FEASIBILITY:       ALTA — rota estruturada declarada (API/opendata)
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «La Pianura» https://www.fondazionenavarra.it/images/pdf/la_pianura_n_3_2010
                              _copertina.pdf — PDF, 704512 bytes lidos em 2026-09-14
ADAMA_USE_CASE:               centro de investigacao aplicada / experimentacao; alimenta T5 (ciencia), T1
                              (cultura e producao)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T5-010/MANIFEST.json
VERDICT:                      GREEN — fonte aberta, exemplo real observado e preservado
```

#### IT-T5-011 · UNIBA DiSSPA — Dipartimento di Scienze del Suolo della Pianta e degli Alimenti

```
SOURCE_ID:                    IT-T5-011
SOURCE_NAME:                  UNIBA DiSSPA — Dipartimento di Scienze del Suolo della Pianta e degli
                              Alimenti
SOURCE_OWNER:                 Universita di Bari Aldo Moro
COUNTRY:                      ITALY
REGION:                       PUGLIA
LANGUAGE:                     IT
TERRITORY:                    T5 (também serve T6, T3)
SOURCE_TYPE:                  CIENCIA
URL:                          https://www.uniba.it/it/ricerca/dipartimenti/disspa
ACCESS_METHOD:                PDF ligado a partir da página da fonte
CROPS:                        olivo;vite
TOPICS:                       patologia;Xylella;olivo;vite
GEOGRAPHIC_GRANULARITY:       REGIÃO — PUGLIA
UPDATE_FREQUENCY:             observada por data visível na página: 2026-08-26
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   NÃO SEI — nenhuma data legível no item observado
RAW_EVIDENCE_PRESERVABLE:     SIM — PDF obtido por HTTP
AUTOMATION_FEASIBILITY:       ALTA — rota estruturada declarada (API/opendata)
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Processi e subprocessi associati ai Dipartimenti di ricerca»
                              https://www.uniba.it/it/ricerca/dipartimenti/processi-e-subprocessi-dei-
                              dipartimenti-di-ricerca.pdf — PDF, 126187 bytes lidos em 2026-09-14
ADAMA_USE_CASE:               universidade / departamento agrario; alimenta T5 (ciencia), T6
                              (pesquisadores), T3 (praga, doenca e infestantes)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T5-011/MANIFEST.json
VERDICT:                      GREEN — fonte aberta, exemplo real observado e preservado
```

#### IT-T5-012 · UNIPI DiSAAA-a — Dipartimento di Scienze Agrarie Alimentari e Agro-ambientali

```
SOURCE_ID:                    IT-T5-012
SOURCE_NAME:                  UNIPI DiSAAA-a — Dipartimento di Scienze Agrarie Alimentari e Agro-
                              ambientali
SOURCE_OWNER:                 Universita di Pisa
COUNTRY:                      ITALY
REGION:                       TOSCANA
LANGUAGE:                     IT-IT
TERRITORY:                    T5 (também serve T6, T1)
SOURCE_TYPE:                  CIENCIA
URL:                          https://www.agr.unipi.it/
ACCESS_METHOD:                PDF ligado a partir da página da fonte
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       agraria;agronomia;difesa
GEOGRAPHIC_GRANULARITY:       REGIÃO — TOSCANA
UPDATE_FREQUENCY:             observada por data visível na página: 2026-09-14
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   NÃO SEI — nenhuma data legível no item observado
RAW_EVIDENCE_PRESERVABLE:     SIM — PDF obtido por HTTP
AUTOMATION_FEASIBILITY:       ALTA — rota estruturada declarada (API/opendata)
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 https://www.agr.unipi.it/wp-content/uploads/2026/07/ad-agraria.pdf — PDF,
                              211583 bytes lidos em 2026-09-14
ADAMA_USE_CASE:               universidade / departamento agrario; alimenta T5 (ciencia), T6
                              (pesquisadores), T1 (cultura e producao)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T5-012/MANIFEST.json
VERDICT:                      GREEN — fonte aberta, exemplo real observado e preservado
```

#### IT-T5-013 · CRPA — Centro Ricerche Produzioni Animali

```
SOURCE_ID:                    IT-T5-013
SOURCE_NAME:                  CRPA — Centro Ricerche Produzioni Animali
SOURCE_OWNER:                 CRPA
COUNTRY:                      ITALY
REGION:                       EMILIA-ROMAGNA
LANGUAGE:                     IT
TERRITORY:                    T5 (também serve T1)
SOURCE_TYPE:                  CIENCIA
URL:                          https://www.crpa.it/
ACCESS_METHOD:                PDF ligado a partir da página da fonte
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       zootecnia;ambiente;biogas
GEOGRAPHIC_GRANULARITY:       REGIÃO — EMILIA-ROMAGNA
UPDATE_FREQUENCY:             NÃO SEI — nenhuma data de publicação legível na página
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   NÃO SEI — nenhuma data legível no item observado
RAW_EVIDENCE_PRESERVABLE:     SIM — PDF obtido por HTTP
AUTOMATION_FEASIBILITY:       MÉDIA — site navegável, sem rota estruturada declarada
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Codice SDI Agenzia delle Entrate» https://www.crpa.it/media/crpa_www/images
                              /contattaci/QRCode_01253030355_CRPA.pdf — PDF, 51027 bytes lidos em
                              2026-09-14
ADAMA_USE_CASE:               centro de investigacao aplicada / experimentacao; alimenta T5 (ciencia), T1
                              (cultura e producao)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T5-013/MANIFEST.json
VERDICT:                      YELLOW — frequencia de atualizacao por provar
```

#### IT-T5-014 · UNITUS DAFNE — Dipartimento di Scienze Agrarie e Forestali

```
SOURCE_ID:                    IT-T5-014
SOURCE_NAME:                  UNITUS DAFNE — Dipartimento di Scienze Agrarie e Forestali
SOURCE_OWNER:                 Universita della Tuscia
COUNTRY:                      ITALY
REGION:                       LAZIO
LANGUAGE:                     IT-IT
TERRITORY:                    T5 (também serve T6, T1)
SOURCE_TYPE:                  CIENCIA
URL:                          https://www.unitus.it/dipartimenti/dafne/
ACCESS_METHOD:                PDF ligado a partir da página da fonte
CROPS:                        nocciolo
TOPICS:                       agraria;nocciolo;difesa
GEOGRAPHIC_GRANULARITY:       REGIÃO — LAZIO
UPDATE_FREQUENCY:             NÃO SEI — nenhuma data de publicação legível na página
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   NÃO SEI — nenhuma data legível no item observado
RAW_EVIDENCE_PRESERVABLE:     SIM — PDF obtido por HTTP
AUTOMATION_FEASIBILITY:       ALTA — rota estruturada declarada (API/opendata)
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Linee guida internazionalizzazione CdL» https://www.unitus.it/wp-
                              content/uploads/2024/02/Linee-guida-con-allegati_2023.24-2.pdf — PDF, 498310
                              bytes lidos em 2026-09-14
ADAMA_USE_CASE:               universidade / departamento agrario; alimenta T5 (ciencia), T6
                              (pesquisadores), T1 (cultura e producao)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T5-014/MANIFEST.json
VERDICT:                      YELLOW — frequencia de atualizacao por provar
```

#### IT-T5-015 · CNR IBBR — Istituto di Bioscienze e Biorisorse

```
SOURCE_ID:                    IT-T5-015
SOURCE_NAME:                  CNR IBBR — Istituto di Bioscienze e Biorisorse
SOURCE_OWNER:                 CNR
COUNTRY:                      ITALY
REGION:                       NAZIONALE (sem recorte regional)
LANGUAGE:                     IT
TERRITORY:                    T5 (também serve T1)
SOURCE_TYPE:                  CIENCIA
URL:                          https://www.ibbr.cnr.it/ibbr/
ACCESS_METHOD:                HTML
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       germoplasma;genetica vegetale
GEOGRAPHIC_GRANULARITY:       PAÍS — a fonte publica com alcance nacional
UPDATE_FREQUENCY:             observada por data visível na página: 2025-12-09
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   NÃO SEI — nenhuma data legível no item observado
RAW_EVIDENCE_PRESERVABLE:     SIM — HTML obtido por HTTP
AUTOMATION_FEASIBILITY:       ALTA — rota estruturada declarada (API/opendata)
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «IBBR News: European Biotech Week 2026 - IBBR-CNR»
                              https://www.ibbr.cnr.it/ibbr/news/european-biotech-week-2026 — HTML, 57204
                              bytes lidos em 2026-09-14
ADAMA_USE_CASE:               instituto nacional de investigacao; alimenta T5 (ciencia), T1 (cultura e
                              producao)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T5-015/MANIFEST.json
VERDICT:                      GREEN — fonte aberta, exemplo real observado e preservado
```

#### IT-T5-016 · AIR UNIMI — Archivio Istituzionale della Ricerca

```
SOURCE_ID:                    IT-T5-016
SOURCE_NAME:                  AIR UNIMI — Archivio Istituzionale della Ricerca
SOURCE_OWNER:                 Universita degli Studi di Milano
COUNTRY:                      ITALY
REGION:                       LOMBARDIA
LANGUAGE:                     IT
TERRITORY:                    T5 (também serve T6)
SOURCE_TYPE:                  CIENCIA
URL:                          https://air.unimi.it/
ACCESS_METHOD:                PDF ligado a partir da página da fonte
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       repositorio scientifico
GEOGRAPHIC_GRANULARITY:       REGIÃO — LOMBARDIA
UPDATE_FREQUENCY:             NÃO SEI — nenhuma data de publicação legível na página
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   NÃO SEI — nenhuma data legível no item observado
RAW_EVIDENCE_PRESERVABLE:     SIM — PDF obtido por HTTP
AUTOMATION_FEASIBILITY:       ALTA — rota estruturada declarada (API/opendata)
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Guida alla nuova interfaccia» https://air.unimi.it/sr/static/DS6/AIR-
                              nuova_interfaccia.pdf — PDF, 704512 bytes lidos em 2026-09-14
ADAMA_USE_CASE:               universidade / departamento agrario; alimenta T5 (ciencia), T6
                              (pesquisadores)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T5-016/MANIFEST.json
VERDICT:                      YELLOW — frequencia de atualizacao por provar
```

#### IT-T5-017 · FLORE UNIFI — Archivio istituzionale della ricerca

```
SOURCE_ID:                    IT-T5-017
SOURCE_NAME:                  FLORE UNIFI — Archivio istituzionale della ricerca
SOURCE_OWNER:                 Universita di Firenze
COUNTRY:                      ITALY
REGION:                       TOSCANA
LANGUAGE:                     IT
TERRITORY:                    T5 (também serve T6)
SOURCE_TYPE:                  CIENCIA
URL:                          https://flore.unifi.it/
ACCESS_METHOD:                PDF ligado a partir da página da fonte
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       repositorio scientifico
GEOGRAPHIC_GRANULARITY:       REGIÃO — TOSCANA
UPDATE_FREQUENCY:             NÃO SEI — nenhuma data de publicação legível na página
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   NÃO SEI — nenhuma data legível no item observado
RAW_EVIDENCE_PRESERVABLE:     SIM — PDF obtido por HTTP
AUTOMATION_FEASIBILITY:       ALTA — rota estruturada declarada (API/opendata)
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «REG. TESI DOTTORATO (ARTT. 29, 30)» https://www.unifi.it/sites/default/file
                              s/migrated/documents/dr_575_2022_regolamento_dottorato.pdf — PDF, 577677
                              bytes lidos em 2026-09-14
ADAMA_USE_CASE:               universidade / departamento agrario; alimenta T5 (ciencia), T6
                              (pesquisadores)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T5-017/MANIFEST.json
VERDICT:                      YELLOW — frequencia de atualizacao por provar
```

#### IT-T5-018 · IRIS UNIBO — Archivio istituzionale della ricerca

```
SOURCE_ID:                    IT-T5-018
SOURCE_NAME:                  IRIS UNIBO — Archivio istituzionale della ricerca
SOURCE_OWNER:                 Universita di Bologna
COUNTRY:                      ITALY
REGION:                       EMILIA-ROMAGNA
LANGUAGE:                     IT
TERRITORY:                    T5 (também serve T6)
SOURCE_TYPE:                  CIENCIA
URL:                          https://cris.unibo.it/
ACCESS_METHOD:                PDF ligado a partir da página da fonte
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       repositorio scientifico;pubblicazioni
GEOGRAPHIC_GRANULARITY:       REGIÃO — EMILIA-ROMAGNA
UPDATE_FREQUENCY:             NÃO SEI — nenhuma data de publicação legível na página
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   NÃO SEI — nenhuma data legível no item observado
RAW_EVIDENCE_PRESERVABLE:     SIM — PDF obtido por HTTP
AUTOMATION_FEASIBILITY:       ALTA — rota estruturada declarada (API/opendata)
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Policy di Ateneo per l’accesso aperto alle pubblicazioni e ai dati della
                              ricerca» https://www.unibo.it/it/allegati/policy-di-ateneo-per-l2019accesso-
                              aperto-alle-pubblicazioni-e-ai-dati-della-ricerca/@@download/file/PolicyAten
                              eoAccessoApertoPubblicazioniDatiRicerca.pdf — PDF, 135160 bytes lidos em
                              2026-09-14
ADAMA_USE_CASE:               universidade / departamento agrario; alimenta T5 (ciencia), T6
                              (pesquisadores)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T5-018/MANIFEST.json
VERDICT:                      YELLOW — frequencia de atualizacao por provar
```

#### IT-T5-019 · IRIS UNIPD — Archivio della ricerca

```
SOURCE_ID:                    IT-T5-019
SOURCE_NAME:                  IRIS UNIPD — Archivio della ricerca
SOURCE_OWNER:                 Universita di Padova
COUNTRY:                      ITALY
REGION:                       VENETO
LANGUAGE:                     IT
TERRITORY:                    T5 (também serve T6)
SOURCE_TYPE:                  CIENCIA
URL:                          https://www.research.unipd.it/
ACCESS_METHOD:                PDF ligado a partir da página da fonte
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       repositorio scientifico
GEOGRAPHIC_GRANULARITY:       REGIÃO — VENETO
UPDATE_FREQUENCY:             NÃO SEI — nenhuma data de publicação legível na página
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   NÃO SEI — nenhuma data legível no item observado
RAW_EVIDENCE_PRESERVABLE:     SIM — PDF obtido por HTTP
AUTOMATION_FEASIBILITY:       ALTA — rota estruturada declarada (API/opendata)
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Policy Open Access» https://wwwassets.unipd.it/sites/default/files/2026-
                              04/Policy_accesso_aperto.pdf — PDF, 315249 bytes lidos em 2026-09-14
ADAMA_USE_CASE:               universidade / departamento agrario; alimenta T5 (ciencia), T6
                              (pesquisadores)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T5-019/MANIFEST.json
VERDICT:                      YELLOW — frequencia de atualizacao por provar
```

#### IT-T5-020 · IRIS UNITO — Archivio istituzionale

```
SOURCE_ID:                    IT-T5-020
SOURCE_NAME:                  IRIS UNITO — Archivio istituzionale
SOURCE_OWNER:                 Universita di Torino
COUNTRY:                      ITALY
REGION:                       PIEMONTE
LANGUAGE:                     IT
TERRITORY:                    T5 (também serve T6)
SOURCE_TYPE:                  CIENCIA
URL:                          https://iris.unito.it/
ACCESS_METHOD:                PDF ligado a partir da página da fonte
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       repositorio scientifico
GEOGRAPHIC_GRANULARITY:       REGIÃO — PIEMONTE
UPDATE_FREQUENCY:             NÃO SEI — nenhuma data de publicação legível na página
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   NÃO SEI — nenhuma data legível no item observado
RAW_EVIDENCE_PRESERVABLE:     SIM — PDF obtido por HTTP
AUTOMATION_FEASIBILITY:       ALTA — rota estruturada declarada (API/opendata)
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Come allegare il file Open Access [istruzioni]»
                              https://iris.unito.it/sr/htm/pdf/come_allegare_2023.pdf — PDF, 148662 bytes
                              lidos em 2026-09-14
ADAMA_USE_CASE:               universidade / departamento agrario; alimenta T5 (ciencia), T6
                              (pesquisadores)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T5-020/MANIFEST.json
VERDICT:                      YELLOW — frequencia de atualizacao por provar
```

#### IT-T5-021 · UNIFI DAGRI — Dipartimento di Scienze e Tecnologie Agrarie Alimentari Ambientali e Forestali

```
SOURCE_ID:                    IT-T5-021
SOURCE_NAME:                  UNIFI DAGRI — Dipartimento di Scienze e Tecnologie Agrarie Alimentari
                              Ambientali e Forestali
SOURCE_OWNER:                 Universita di Firenze
COUNTRY:                      ITALY
REGION:                       TOSCANA
LANGUAGE:                     IT
TERRITORY:                    T5 (também serve T6, T1)
SOURCE_TYPE:                  CIENCIA
URL:                          https://www.dagri.unifi.it/
ACCESS_METHOD:                HTML
CROPS:                        olivo;vite
TOPICS:                       agraria;olivo;vite
GEOGRAPHIC_GRANULARITY:       REGIÃO — TOSCANA
UPDATE_FREQUENCY:             NÃO SEI — nenhuma data de publicação legível na página
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   SIM — 2026-09-14
RAW_EVIDENCE_PRESERVABLE:     SIM — HTML obtido por HTTP
AUTOMATION_FEASIBILITY:       MÉDIA-ALTA — feed ou ficheiro previsível
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «News | Dipartimento di Scienze e Tecnologie Agrarie, Alimentari, Ambientali
                              e Forestali (DAGRI) | UniFI» https://www.dagri.unifi.it/avvisi — HTML,
                              167376 bytes lidos em 2026-09-14
ADAMA_USE_CASE:               universidade / departamento agrario; alimenta T5 (ciencia), T6
                              (pesquisadores), T1 (cultura e producao)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T5-021/MANIFEST.json
VERDICT:                      YELLOW — frequencia de atualizacao por provar
```

#### IT-T5-022 · Advances in Horticultural Science

```
SOURCE_ID:                    IT-T5-022
SOURCE_NAME:                  Advances in Horticultural Science
SOURCE_OWNER:                 Firenze University Press
COUNTRY:                      ITALY
REGION:                       TOSCANA
LANGUAGE:                     EN-US
TERRITORY:                    T5 (também serve T1)
SOURCE_TYPE:                  CIENCIA
URL:                          https://oaj.fupress.net/
ACCESS_METHOD:                PDF ligado a partir da página da fonte
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       journal;orticoltura
GEOGRAPHIC_GRANULARITY:       REGIÃO — TOSCANA
UPDATE_FREQUENCY:             observada por data visível na página: 2025-05-07
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   NÃO SEI — nenhuma data legível no item observado
RAW_EVIDENCE_PRESERVABLE:     SIM — PDF obtido por HTTP
AUTOMATION_FEASIBILITY:       MÉDIA-ALTA — feed ou ficheiro previsível
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «PDF» https://journals.fupress.net/wp-content/uploads/2025/10/Call-N31.pdf —
                              PDF, 327650 bytes lidos em 2026-09-14
ADAMA_USE_CASE:               universidade / departamento agrario; alimenta T5 (ciencia), T1 (cultura e
                              producao)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T5-022/MANIFEST.json
VERDICT:                      GREEN — fonte aberta, exemplo real observado e preservado
```

#### IT-T5-023 · SSICA — Stazione Sperimentale per l'Industria delle Conserve Alimentari

```
SOURCE_ID:                    IT-T5-023
SOURCE_NAME:                  SSICA — Stazione Sperimentale per l'Industria delle Conserve Alimentari
SOURCE_OWNER:                 SSICA
COUNTRY:                      ITALY
REGION:                       EMILIA-ROMAGNA
LANGUAGE:                     IT-IT
TERRITORY:                    T5 (também serve T10)
SOURCE_TYPE:                  CIENCIA
URL:                          https://www.ssica.it/
ACCESS_METHOD:                PDF ligado a partir da página da fonte
CROPS:                        pomodoro
TOPICS:                       pomodoro;conserve;trasformazione
GEOGRAPHIC_GRANULARITY:       REGIÃO — EMILIA-ROMAGNA
UPDATE_FREQUENCY:             observada por data visível na página: 2011-06-20
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   NÃO SEI — nenhuma data legível no item observado
RAW_EVIDENCE_PRESERVABLE:     SIM — PDF obtido por HTTP
AUTOMATION_FEASIBILITY:       ALTA — rota estruturada declarada (API/opendata)
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 https://www.ssica.it/wp-content/uploads/2025/03/PROGETTO-ACTION.pdf — PDF,
                              194972 bytes lidos em 2026-09-14
ADAMA_USE_CASE:               centro de investigacao aplicada / experimentacao; alimenta T5 (ciencia), T10
                              (mercado e industria)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T5-023/MANIFEST.json
VERDICT:                      GREEN — fonte aberta, exemplo real observado e preservado
```

#### IT-T5-024 · UNIMI DiSAA — Dipartimento di Scienze Agrarie e Ambientali

```
SOURCE_ID:                    IT-T5-024
SOURCE_NAME:                  UNIMI DiSAA — Dipartimento di Scienze Agrarie e Ambientali
SOURCE_OWNER:                 Universita degli Studi di Milano
COUNTRY:                      ITALY
REGION:                       LOMBARDIA
LANGUAGE:                     IT
TERRITORY:                    T5 (também serve T6, T1)
SOURCE_TYPE:                  CIENCIA
URL:                          https://disaa.unimi.it/it
ACCESS_METHOD:                HTML
CROPS:                        mais;riso
TOPICS:                       agronomia;difesa;riso;mais
GEOGRAPHIC_GRANULARITY:       REGIÃO — LOMBARDIA
UPDATE_FREQUENCY:             observada por data visível na página: 2026-09-11
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   SIM — 2026-06-18
RAW_EVIDENCE_PRESERVABLE:     SIM — HTML obtido por HTTP
AUTOMATION_FEASIBILITY:       MÉDIA — site navegável, sem rota estruturada declarada
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Pubblicazioni | Dipartimento di Scienze Agrarie e Ambientali - Produzione,
                              Territorio, Agroenergia» https://disaa.unimi.it/it/ricerca/attivita-e-
                              risultati-di-ricerca/pubblicazioni — HTML, 88512 bytes lidos em 2026-09-14
ADAMA_USE_CASE:               universidade / departamento agrario; alimenta T5 (ciencia), T6
                              (pesquisadores), T1 (cultura e producao)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T5-024/MANIFEST.json
VERDICT:                      GREEN — fonte aberta, exemplo real observado e preservado
```

#### IT-T5-025 · Scuola Superiore Sant'Anna — Istituto di Scienze delle Produzioni Vegetali

```
SOURCE_ID:                    IT-T5-025
SOURCE_NAME:                  Scuola Superiore Sant'Anna — Istituto di Scienze delle Produzioni Vegetali
SOURCE_OWNER:                 Scuola Superiore Sant'Anna Pisa
COUNTRY:                      ITALY
REGION:                       TOSCANA
LANGUAGE:                     IT
TERRITORY:                    T5 (também serve T6, T1)
SOURCE_TYPE:                  CIENCIA
URL:                          https://www.santannapisa.it/it/istituto/produzioni-vegetali
ACCESS_METHOD:                HTML
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       agricoltura sostenibile;precision farming
GEOGRAPHIC_GRANULARITY:       REGIÃO — TOSCANA
UPDATE_FREQUENCY:             NÃO SEI — nenhuma data de publicação legível na página
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   SIM — 2026-06-24
RAW_EVIDENCE_PRESERVABLE:     SIM — HTML obtido por HTTP
AUTOMATION_FEASIBILITY:       MÉDIA — site navegável, sem rota estruturada declarada
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Al via il progetto INNOFLORENERG con il contributo scientifico
                              dell’Istituto di Produzioni Vegetali della Scuola Sant’Anna. Tecnologie
                              innovative per una floricoltura più sostenibi»
                              https://www.santannapisa.it/it/news/progetto-innoflorenerg — HTML, 54711
                              bytes lidos em 2026-09-14
ADAMA_USE_CASE:               universidade / departamento agrario; alimenta T5 (ciencia), T6
                              (pesquisadores), T1 (cultura e producao)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T5-025/MANIFEST.json
VERDICT:                      YELLOW — frequencia de atualizacao por provar
```

#### IT-T5-026 · UNIPA SAAF — Dipartimento Scienze Agrarie Alimentari e Forestali

```
SOURCE_ID:                    IT-T5-026
SOURCE_NAME:                  UNIPA SAAF — Dipartimento Scienze Agrarie Alimentari e Forestali
SOURCE_OWNER:                 Universita di Palermo
COUNTRY:                      ITALY
REGION:                       SICILIA
LANGUAGE:                     IT
TERRITORY:                    T5 (também serve T6, T1)
SOURCE_TYPE:                  CIENCIA
URL:                          https://www.unipa.it/dipartimenti/saaf/
ACCESS_METHOD:                PDF ligado a partir da página da fonte
CROPS:                        olivo;vite
TOPICS:                       agraria;vite;olivo
GEOGRAPHIC_GRANULARITY:       REGIÃO — SICILIA
UPDATE_FREQUENCY:             NÃO SEI — nenhuma data de publicação legível na página
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   NÃO SEI — nenhuma data legível no item observado
RAW_EVIDENCE_PRESERVABLE:     SIM — PDF obtido por HTTP
AUTOMATION_FEASIBILITY:       MÉDIA — site navegável, sem rota estruturada declarada
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 https://www.unipa.it/dipartimenti/saaf/.content/documenti/Linee-guida-
                              semestre-aperto-2025.pdf — PDF, 704512 bytes lidos em 2026-09-14
ADAMA_USE_CASE:               universidade / departamento agrario; alimenta T5 (ciencia), T6
                              (pesquisadores), T1 (cultura e producao)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T5-026/MANIFEST.json
VERDICT:                      YELLOW — frequencia de atualizacao por provar
```

#### IT-T5-027 · UNIPD DAFNAE — Dipartimento di Agronomia Animali Alimenti Risorse Naturali e Ambiente

```
SOURCE_ID:                    IT-T5-027
SOURCE_NAME:                  UNIPD DAFNAE — Dipartimento di Agronomia Animali Alimenti Risorse Naturali e
                              Ambiente
SOURCE_OWNER:                 Universita di Padova
COUNTRY:                      ITALY
REGION:                       VENETO
LANGUAGE:                     IT
TERRITORY:                    T5 (também serve T6, T3)
SOURCE_TYPE:                  CIENCIA
URL:                          https://www.dafnae.unipd.it/
ACCESS_METHOD:                HTML
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       agronomia;entomologia;patologia
GEOGRAPHIC_GRANULARITY:       REGIÃO — VENETO
UPDATE_FREQUENCY:             NÃO SEI — nenhuma data de publicação legível na página
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   NÃO SEI — nenhuma data legível no item observado
RAW_EVIDENCE_PRESERVABLE:     SIM — HTML obtido por HTTP
AUTOMATION_FEASIBILITY:       MÉDIA — site navegável, sem rota estruturada declarada
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «|  | Università di Padova» https://www.dafnae.unipd.it/news/termine/2 —
                              HTML, 53705 bytes lidos em 2026-09-14
ADAMA_USE_CASE:               universidade / departamento agrario; alimenta T5 (ciencia), T6
                              (pesquisadores), T3 (praga, doenca e infestantes)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T5-027/MANIFEST.json
VERDICT:                      YELLOW — frequencia de atualizacao por provar
```

#### IT-T5-028 · UNIUD DI4A — Dipartimento di Scienze Agroalimentari Ambientali e Animali

```
SOURCE_ID:                    IT-T5-028
SOURCE_NAME:                  UNIUD DI4A — Dipartimento di Scienze Agroalimentari Ambientali e Animali
SOURCE_OWNER:                 Universita di Udine
COUNTRY:                      ITALY
REGION:                       FRIULI-VENEZIA GIULIA
LANGUAGE:                     IT
TERRITORY:                    T5 (também serve T6, T3)
SOURCE_TYPE:                  CIENCIA
URL:                          https://www.di4a.uniud.it/it
ACCESS_METHOD:                HTML
CROPS:                        vite
TOPICS:                       vite;flavescenza;agronomia
GEOGRAPHIC_GRANULARITY:       REGIÃO — FRIULI-VENEZIA GIULIA
UPDATE_FREQUENCY:             NÃO SEI — nenhuma data de publicação legível na página
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   NÃO SEI — nenhuma data legível no item observado
RAW_EVIDENCE_PRESERVABLE:     SIM — HTML obtido por HTTP
AUTOMATION_FEASIBILITY:       MÉDIA — site navegável, sem rota estruturada declarada
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Pubblicazioni — Italiano» https://di4a.uniud.it/it/ricerca/pubblicazioni-
                              dipartimento — HTML, 38408 bytes lidos em 2026-09-14
ADAMA_USE_CASE:               universidade / departamento agrario; alimenta T5 (ciencia), T6
                              (pesquisadores), T3 (praga, doenca e infestantes)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T5-028/MANIFEST.json
VERDICT:                      YELLOW — frequencia de atualizacao por provar
```

#### IT-T5-029 · UNIVR Dipartimento di Biotecnologie

```
SOURCE_ID:                    IT-T5-029
SOURCE_NAME:                  UNIVR Dipartimento di Biotecnologie
SOURCE_OWNER:                 Universita di Verona
COUNTRY:                      ITALY
REGION:                       VENETO
LANGUAGE:                     IT
TERRITORY:                    T5 (também serve T6)
SOURCE_TYPE:                  CIENCIA
URL:                          https://www.dbt.univr.it/
ACCESS_METHOD:                PDF ligado a partir da página da fonte
CROPS:                        vite
TOPICS:                       biotecnologie;vite
GEOGRAPHIC_GRANULARITY:       REGIÃO — VENETO
UPDATE_FREQUENCY:             NÃO SEI — nenhuma data de publicação legível na página
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   NÃO SEI — nenhuma data legível no item observado
RAW_EVIDENCE_PRESERVABLE:     SIM — PDF obtido por HTTP
AUTOMATION_FEASIBILITY:       MÉDIA-ALTA — feed ou ficheiro previsível
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «2026-28 " />                       Piano Operativo del Dipartimento
                              2026-28»
                              https://cdn.docs.univr.it/documenti/Documento/allegati/allegati375197.pdf —
                              PDF, 704512 bytes lidos em 2026-09-14
ADAMA_USE_CASE:               universidade / departamento agrario; alimenta T5 (ciencia), T6
                              (pesquisadores)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T5-029/MANIFEST.json
VERDICT:                      YELLOW — frequencia de atualizacao por provar
```

#### IT-T5-030 · UNITE Facolta di Bioscienze e Tecnologie Agro-alimentari e Ambientali

```
SOURCE_ID:                    IT-T5-030
SOURCE_NAME:                  UNITE Facolta di Bioscienze e Tecnologie Agro-alimentari e Ambientali
SOURCE_OWNER:                 Universita di Teramo
COUNTRY:                      ITALY
REGION:                       ABRUZZO
LANGUAGE:                     IT
TERRITORY:                    T5 (também serve T6)
SOURCE_TYPE:                  CIENCIA
URL:                          https://www.unite.it/UniTE/Bioscienze_e_Tecnologie_Agro-
                              Alimentari_e_Ambientali
ACCESS_METHOD:                HTML
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       bioscienze;agroalimentare
GEOGRAPHIC_GRANULARITY:       REGIÃO — ABRUZZO
UPDATE_FREQUENCY:             observada por data visível na página: 2023-10-19
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   SIM — 2023-10-19
RAW_EVIDENCE_PRESERVABLE:     SIM — HTML obtido por HTTP
AUTOMATION_FEASIBILITY:       MÉDIA-ALTA — feed ou ficheiro previsível
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «UniTE -                        News ed Eventi - Dipartimento di Bioscienze
                              e tecnologie agroalimentari e ambientali»
                              https://www.unite.it/UniTE/Bioscienze_e_Tecnologie_Agro-
                              Alimentari_e_Ambientali/News_ed_Eventi_-
                              _Dipartimento_di_Bioscienze_e_tecnologie_agroalimentari_e_ambientali — HTML,
                              103497 bytes lidos em 2026-09-14
ADAMA_USE_CASE:               universidade / departamento agrario; alimenta T5 (ciencia), T6
                              (pesquisadores)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T5-030/MANIFEST.json
VERDICT:                      GREEN — fonte aberta, exemplo real observado e preservado
```

#### IT-T5-031 · UNIVPM D3A — Dipartimento di Scienze Agrarie Alimentari e Ambientali

```
SOURCE_ID:                    IT-T5-031
SOURCE_NAME:                  UNIVPM D3A — Dipartimento di Scienze Agrarie Alimentari e Ambientali
SOURCE_OWNER:                 Universita Politecnica delle Marche
COUNTRY:                      ITALY
REGION:                       MARCHE
LANGUAGE:                     IT
TERRITORY:                    T5 (também serve T6, T1)
SOURCE_TYPE:                  CIENCIA
URL:                          https://www.d3a.univpm.it/
ACCESS_METHOD:                TEXTO
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       agraria;agronomia
GEOGRAPHIC_GRANULARITY:       REGIÃO — MARCHE
UPDATE_FREQUENCY:             observada por data visível na página: 2026-09-03
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   NÃO SEI — nenhuma data legível no item observado
RAW_EVIDENCE_PRESERVABLE:     SIM — TEXTO obtido por HTTP
AUTOMATION_FEASIBILITY:       MÉDIA — site navegável, sem rota estruturada declarada
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 https://www.d3a.univpm.it/sites/www.d3a.univpm.it/files/d3a/news_didattica/n
                              ew2026/insegnamenti%20a%20scelta_14sett20262.png — TEXTO, 704512 bytes lidos
                              em 2026-09-14
ADAMA_USE_CASE:               universidade / departamento agrario; alimenta T5 (ciencia), T6
                              (pesquisadores), T1 (cultura e producao)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T5-031/MANIFEST.json
VERDICT:                      GREEN — fonte aberta, exemplo real observado e preservado
```

#### IT-T5-032 · UNIPG DSA3 — Dipartimento di Scienze Agrarie Alimentari e Ambientali

```
SOURCE_ID:                    IT-T5-032
SOURCE_NAME:                  UNIPG DSA3 — Dipartimento di Scienze Agrarie Alimentari e Ambientali
SOURCE_OWNER:                 Universita di Perugia
COUNTRY:                      ITALY
REGION:                       UMBRIA
LANGUAGE:                     IT
TERRITORY:                    T5 (também serve T6, T1)
SOURCE_TYPE:                  CIENCIA
URL:                          https://dsa3.unipg.it/
ACCESS_METHOD:                HTML
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       agraria;agronomia;difesa
GEOGRAPHIC_GRANULARITY:       REGIÃO — UMBRIA
UPDATE_FREQUENCY:             NÃO SEI — nenhuma data de publicação legível na página
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   SIM — 2026-08-25
RAW_EVIDENCE_PRESERVABLE:     SIM — HTML obtido por HTTP
AUTOMATION_FEASIBILITY:       MÉDIA — site navegável, sem rota estruturada declarada
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Bandi - Dipartimento di Scienze Agrarie, Alimentari e Ambientali»
                              https://dsa3.unipg.it/home/news/bandi?view=elenco — HTML, 61402 bytes lidos
                              em 2026-09-14
ADAMA_USE_CASE:               universidade / departamento agrario; alimenta T5 (ciencia), T6
                              (pesquisadores), T1 (cultura e producao)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T5-032/MANIFEST.json
VERDICT:                      YELLOW — frequencia de atualizacao por provar
```

#### IT-T5-033 · UNIBO DISTAL — Dipartimento di Scienze e Tecnologie Agro-Alimentari

```
SOURCE_ID:                    IT-T5-033
SOURCE_NAME:                  UNIBO DISTAL — Dipartimento di Scienze e Tecnologie Agro-Alimentari
SOURCE_OWNER:                 Universita di Bologna
COUNTRY:                      ITALY
REGION:                       EMILIA-ROMAGNA
LANGUAGE:                     IT
TERRITORY:                    T5 (também serve T6, T1)
SOURCE_TYPE:                  CIENCIA
URL:                          https://distal.unibo.it/it
ACCESS_METHOD:                HTML
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       agraria;patologia;entomologia;agronomia
GEOGRAPHIC_GRANULARITY:       REGIÃO — EMILIA-ROMAGNA
UPDATE_FREQUENCY:             observada por data visível na página: 2025-12-09
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   SIM — 2025-12-09
RAW_EVIDENCE_PRESERVABLE:     SIM — HTML obtido por HTTP
AUTOMATION_FEASIBILITY:       MÉDIA — site navegável, sem rota estruturada declarada
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Bollettino agrofenologico — Scienze e Tecnologie Agro-Alimentari»
                              https://distal.unibo.it/it/con-societa-e-impresa/territorio-e-
                              comunita/bollettino-agrofenologico — HTML, 88190 bytes lidos em 2026-09-14
ADAMA_USE_CASE:               universidade / departamento agrario; alimenta T5 (ciencia), T6
                              (pesquisadores), T1 (cultura e producao)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T5-033/MANIFEST.json
VERDICT:                      GREEN — fonte aberta, exemplo real observado e preservado
```

#### IT-T5-034 · Accademia dei Georgofili

```
SOURCE_ID:                    IT-T5-034
SOURCE_NAME:                  Accademia dei Georgofili
SOURCE_OWNER:                 Accademia dei Georgofili
COUNTRY:                      ITALY
REGION:                       TOSCANA
LANGUAGE:                     IT
TERRITORY:                    T5 (também serve T11, T12)
SOURCE_TYPE:                  ORGANIZACAO
URL:                          https://www.georgofili.it/
ACCESS_METHOD:                HTML
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       accademia;convegni;agricoltura
GEOGRAPHIC_GRANULARITY:       REGIÃO — TOSCANA
UPDATE_FREQUENCY:             observada por data visível na página: 2026-09-08
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   NÃO SEI — nenhuma data legível no item observado
RAW_EVIDENCE_PRESERVABLE:     SIM — HTML obtido por HTTP
AUTOMATION_FEASIBILITY:       MÉDIA — site navegável, sem rota estruturada declarada
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Benvenuti nella Sezione dell'Ufficio Stampa dei Georgofili  | Georgofili»
                              https://www.georgofili.it/contenuti/notiziario-accademia/620 — HTML, 33731
                              bytes lidos em 2026-09-14
ADAMA_USE_CASE:               sociedade cientifica / academia; alimenta T5 (ciencia), T11 (eventos), T12
                              (politica e ambiente agricola)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T5-034/MANIFEST.json
VERDICT:                      GREEN — fonte aberta, exemplo real observado e preservado
```

#### IT-T5-035 · Georgofili INFO — notiziario

```
SOURCE_ID:                    IT-T5-035
SOURCE_NAME:                  Georgofili INFO — notiziario
SOURCE_OWNER:                 Accademia dei Georgofili
COUNTRY:                      ITALY
REGION:                       TOSCANA
LANGUAGE:                     IT
TERRITORY:                    T5 (também serve T12, T11)
SOURCE_TYPE:                  IMPRENSA
URL:                          https://www.georgofili.info/
ACCESS_METHOD:                HTML
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       notiziario tecnico;divulgazione
GEOGRAPHIC_GRANULARITY:       REGIÃO — TOSCANA
UPDATE_FREQUENCY:             NÃO SEI — nenhuma data de publicação legível na página
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   NÃO SEI — nenhuma data legível no item observado
RAW_EVIDENCE_PRESERVABLE:     SIM — HTML obtido por HTTP
AUTOMATION_FEASIBILITY:       MÉDIA — site navegável, sem rota estruturada declarada
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «“Notizie Forestali” - Australia e Nuova Zelanda adottano uno standard
                              comune per valutare le foreste - Accademia dei Georgofili»
                              https://www.georgofili.info/contenuti/notizie-forestali-australia-e-nuova-
                              zelanda-adottano-uno-standard-comune-per-valutare-le-foreste/33685 — HTML,
                              34898 bytes lidos em 2026-09-14
ADAMA_USE_CASE:               imprensa tecnica agricola; alimenta T5 (ciencia), T12 (politica e ambiente
                              agricola), T11 (eventos)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T5-035/MANIFEST.json
VERDICT:                      YELLOW — frequencia de atualizacao por provar
```

#### IT-T5-036 · Georgofili — Accademia dei Georgofili (portale .net)

```
SOURCE_ID:                    IT-T5-036
SOURCE_NAME:                  Georgofili — Accademia dei Georgofili (portale .net)
SOURCE_OWNER:                 Accademia dei Georgofili
COUNTRY:                      ITALY
REGION:                       TOSCANA
LANGUAGE:                     IT
TERRITORY:                    T5 (também serve T11)
SOURCE_TYPE:                  ORGANIZACAO
URL:                          https://www.georgofili.net/
ACCESS_METHOD:                HTML
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       accademia;pubblicazioni
GEOGRAPHIC_GRANULARITY:       REGIÃO — TOSCANA
UPDATE_FREQUENCY:             NÃO SEI — nenhuma data de publicação legível na página
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   NÃO SEI — nenhuma data legível no item observado
RAW_EVIDENCE_PRESERVABLE:     SIM — HTML obtido por HTTP
AUTOMATION_FEASIBILITY:       MÉDIA — site navegável, sem rota estruturada declarada
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Agrifood tra credito e sostenibilit&#224; - Accademia dei Georgofili»
                              https://www.georgofili.net/articoli/agrifood-tra-credito-e-
                              sostenibilit/15465 — HTML, 20305 bytes lidos em 2026-09-14
ADAMA_USE_CASE:               sociedade cientifica / academia; alimenta T5 (ciencia), T11 (eventos)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T5-036/MANIFEST.json
VERDICT:                      YELLOW — frequencia de atualizacao por provar
```

### T6 · RESEARCHERS — ITALY · onda 1 (2026-09-14)

*36 fontes registradas nesta secção. Cada uma foi aberta, observada e tem exemplo real preservado em `data/samples/IT-SOURCE-SAMPLES/<SOURCE_ID>/`. Registada ≠ contratada: nenhuma tem contrato de busca, e nenhuma coleta foi corrida.*

#### IT-T6-001 · Andrea Lentini — registo cientifico ORCID (Università degli Studi di Sassari)

```
SOURCE_ID:                    IT-T6-001
SOURCE_NAME:                  Andrea Lentini — registo cientifico ORCID (Università degli Studi di
                              Sassari)
SOURCE_OWNER:                 Andrea Lentini · Università degli Studi di Sassari
COUNTRY:                      ITALY
REGION:                       SARDEGNA
LANGUAGE:                     IT
TERRITORY:                    T6 (também serve T5)
SOURCE_TYPE:                  CIENCIA
URL:                          https://orcid.org/0000-0003-2089-1026
ACCESS_METHOD:                API pública ORCID (JSON) + página pública do registo
CROPS:                        mais
TOPICS:                       mais;piralide
GEOGRAPHIC_GRANULARITY:       REGIÃO — SARDEGNA
UPDATE_FREQUENCY:             NÃO SEI — nenhuma data de publicação legível na página
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        SIM — DOI
PUBLICATION_DATE_AVAILABLE:   SIM — 2025
RAW_EVIDENCE_PRESERVABLE:     SIM — registo público legível por HTTP
AUTOMATION_FEASIBILITY:       MÉDIA — site navegável, sem rota estruturada declarada
COLLECTION_FEASIBILITY:       NÃO SEI — o exemplo veio de API pública, não de descarga direta
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «From waste to opportunity: evaluating the pesticidal properties of a waste
                              cooking oil and its derivates» https://doi.org/10.1007/s41348-025-01103-3
                              (2025) — ORCID public API /works
ADAMA_USE_CASE:               pesquisador com afiliacao italiana atual; alimenta T6 (pesquisadores), T5
                              (ciencia)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T6-001/MANIFEST.json
VERDICT:                      YELLOW — frequencia de atualizacao por provar
```

#### IT-T6-002 · Anita Nencioni — registo cientifico ORCID (Consiglio per la ricerca in agricoltura e l’analisi dell’economia agraria)

```
SOURCE_ID:                    IT-T6-002
SOURCE_NAME:                  Anita Nencioni — registo cientifico ORCID (Consiglio per la ricerca in
                              agricoltura e l’analisi dell’economia agraria)
SOURCE_OWNER:                 Anita Nencioni · Consiglio per la ricerca in agricoltura e l’analisi
                              dell’economia agraria
COUNTRY:                      ITALY
REGION:                       LAZIO
LANGUAGE:                     IT
TERRITORY:                    T6 (também serve T5)
SOURCE_TYPE:                  CIENCIA
URL:                          https://orcid.org/0000-0003-1585-0529
ACCESS_METHOD:                API pública ORCID (JSON) + página pública do registo
CROPS:                        olivo
TOPICS:                       olivo;Xylella;batteriosi
GEOGRAPHIC_GRANULARITY:       REGIÃO — LAZIO
UPDATE_FREQUENCY:             NÃO SEI — nenhuma data de publicação legível na página
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        SIM — DOI
PUBLICATION_DATE_AVAILABLE:   SIM — 2026
RAW_EVIDENCE_PRESERVABLE:     SIM — registo público legível por HTTP
AUTOMATION_FEASIBILITY:       MÉDIA — site navegável, sem rota estruturada declarada
COLLECTION_FEASIBILITY:       NÃO SEI — o exemplo veio de API pública, não de descarga direta
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Visual adaptation of a biting fly that permanently foregoes flight»
                              https://doi.org/10.1242/jeb.251571 (2026) — ORCID public API /works
ADAMA_USE_CASE:               pesquisador com afiliacao italiana atual; alimenta T6 (pesquisadores), T5
                              (ciencia)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T6-002/MANIFEST.json
VERDICT:                      YELLOW — frequencia de atualizacao por provar
```

#### IT-T6-003 · Anna Aldrighetti — registo cientifico ORCID (University of Trento)

```
SOURCE_ID:                    IT-T6-003
SOURCE_NAME:                  Anna Aldrighetti — registo cientifico ORCID (University of Trento)
SOURCE_OWNER:                 Anna Aldrighetti · University of Trento
COUNTRY:                      ITALY
REGION:                       TRENTINO-ALTO ADIGE
LANGUAGE:                     IT
TERRITORY:                    T6 (também serve T5)
SOURCE_TYPE:                  CIENCIA
URL:                          https://orcid.org/0000-0002-9018-3343
ACCESS_METHOD:                API pública ORCID (JSON) + página pública do registo
CROPS:                        vite
TOPICS:                       vite;Plasmopara viticola
GEOGRAPHIC_GRANULARITY:       REGIÃO — TRENTINO-ALTO ADIGE
UPDATE_FREQUENCY:             NÃO SEI — nenhuma data de publicação legível na página
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        SIM — DOI
PUBLICATION_DATE_AVAILABLE:   SIM — 2026
RAW_EVIDENCE_PRESERVABLE:     SIM — registo público legível por HTTP
AUTOMATION_FEASIBILITY:       MÉDIA — site navegável, sem rota estruturada declarada
COLLECTION_FEASIBILITY:       NÃO SEI — o exemplo veio de API pública, não de descarga direta
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Sequential use of pre-flowering chemical fungicides and post-flowering
                              natural products effectively controls strawberry powdery mildew while
                              resulting in low residues in fruit»
                              https://doi.org/10.1016/j.cropro.2026.107572 (2026) — ORCID public API
                              /works
ADAMA_USE_CASE:               pesquisador com afiliacao italiana atual; alimenta T6 (pesquisadores), T5
                              (ciencia)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T6-003/MANIFEST.json
VERDICT:                      YELLOW — frequencia de atualizacao por provar
```

#### IT-T6-004 · Antonio Masetti — registo cientifico ORCID (University of Bologna)

```
SOURCE_ID:                    IT-T6-004
SOURCE_NAME:                  Antonio Masetti — registo cientifico ORCID (University of Bologna)
SOURCE_OWNER:                 Antonio Masetti · University of Bologna
COUNTRY:                      ITALY
REGION:                       EMILIA-ROMAGNA
LANGUAGE:                     IT
TERRITORY:                    T6 (também serve T5)
SOURCE_TYPE:                  CIENCIA
URL:                          https://orcid.org/0000-0001-6061-2752
ACCESS_METHOD:                API pública ORCID (JSON) + página pública do registo
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       Halyomorpha;cimice asiatica
GEOGRAPHIC_GRANULARITY:       REGIÃO — EMILIA-ROMAGNA
UPDATE_FREQUENCY:             NÃO SEI — nenhuma data de publicação legível na página
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        SIM — DOI
PUBLICATION_DATE_AVAILABLE:   SIM — 2026
RAW_EVIDENCE_PRESERVABLE:     SIM — registo público legível por HTTP
AUTOMATION_FEASIBILITY:       MÉDIA — site navegável, sem rota estruturada declarada
COLLECTION_FEASIBILITY:       NÃO SEI — o exemplo veio de API pública, não de descarga direta
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Smartphone and web apps for pest and disease management in viticulture: A
                              mapping of functionality, AI integration, and accessibility»
                              https://doi.org/10.1016/j.atech.2026.102480 (2026) — ORCID public API /works
ADAMA_USE_CASE:               pesquisador com afiliacao italiana atual; alimenta T6 (pesquisadores), T5
                              (ciencia)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T6-004/MANIFEST.json
VERDICT:                      YELLOW — frequencia de atualizacao por provar
```

#### IT-T6-005 · Antonio Pietro GARONNA — registo cientifico ORCID (Università degli Studi di Napoli Federico II)

```
SOURCE_ID:                    IT-T6-005
SOURCE_NAME:                  Antonio Pietro GARONNA — registo cientifico ORCID (Università degli Studi di
                              Napoli Federico II)
SOURCE_OWNER:                 Antonio Pietro GARONNA · Università degli Studi di Napoli Federico II
COUNTRY:                      ITALY
REGION:                       CAMPANIA
LANGUAGE:                     IT
TERRITORY:                    T6 (também serve T5)
SOURCE_TYPE:                  CIENCIA
URL:                          https://orcid.org/0000-0002-8441-5208
ACCESS_METHOD:                API pública ORCID (JSON) + página pública do registo
CROPS:                        olivo
TOPICS:                       olivo;mosca delle olive
GEOGRAPHIC_GRANULARITY:       REGIÃO — CAMPANIA
UPDATE_FREQUENCY:             NÃO SEI — nenhuma data de publicação legível na página
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        SIM — DOI
PUBLICATION_DATE_AVAILABLE:   SIM — 2026
RAW_EVIDENCE_PRESERVABLE:     SIM — registo público legível por HTTP
AUTOMATION_FEASIBILITY:       MÉDIA — site navegável, sem rota estruturada declarada
COLLECTION_FEASIBILITY:       NÃO SEI — o exemplo veio de API pública, não de descarga direta
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «A Probe-Based qPCR Method for Rapid Detection of Ips typographus
                              (Coleoptera: Curculionidae, Scolytinae) in Border Inspections and Forest
                              Surveillance» https://doi.org/10.3390/f17040440 (2026) — ORCID public API
                              /works
ADAMA_USE_CASE:               pesquisador com afiliacao italiana atual; alimenta T6 (pesquisadores), T5
                              (ciencia)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T6-005/MANIFEST.json
VERDICT:                      YELLOW — frequencia de atualizacao por provar
```

#### IT-T6-006 · Antonio Prodi — registo cientifico ORCID (University of Bologna)

```
SOURCE_ID:                    IT-T6-006
SOURCE_NAME:                  Antonio Prodi — registo cientifico ORCID (University of Bologna)
SOURCE_OWNER:                 Antonio Prodi · University of Bologna
COUNTRY:                      ITALY
REGION:                       EMILIA-ROMAGNA
LANGUAGE:                     IT
TERRITORY:                    T6 (também serve T5)
SOURCE_TYPE:                  CIENCIA
URL:                          https://orcid.org/0000-0002-7221-7271
ACCESS_METHOD:                API pública ORCID (JSON) + página pública do registo
CROPS:                        grano
TOPICS:                       grano duro;Fusarium;micotossine
GEOGRAPHIC_GRANULARITY:       REGIÃO — EMILIA-ROMAGNA
UPDATE_FREQUENCY:             NÃO SEI — nenhuma data de publicação legível na página
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        SIM — DOI
PUBLICATION_DATE_AVAILABLE:   SIM — 2026
RAW_EVIDENCE_PRESERVABLE:     SIM — registo público legível por HTTP
AUTOMATION_FEASIBILITY:       MÉDIA — site navegável, sem rota estruturada declarada
COLLECTION_FEASIBILITY:       NÃO SEI — o exemplo veio de API pública, não de descarga direta
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Seed Priming with Antagonistic Bacteria for Managing Fusarium Crown and
                              Root Rot in Durum Wheat» https://doi.org/10.1094/PDIS-10-25-2171-RE (2026) —
                              ORCID public API /works
ADAMA_USE_CASE:               pesquisador com afiliacao italiana atual; alimenta T6 (pesquisadores), T5
                              (ciencia)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T6-006/MANIFEST.json
VERDICT:                      YELLOW — frequencia de atualizacao por provar
```

#### IT-T6-007 · Aparna S Balan — registo cientifico ORCID (University of Palermo)

```
SOURCE_ID:                    IT-T6-007
SOURCE_NAME:                  Aparna S Balan — registo cientifico ORCID (University of Palermo)
SOURCE_OWNER:                 Aparna S Balan · University of Palermo
COUNTRY:                      ITALY
REGION:                       SICILIA
LANGUAGE:                     IT
TERRITORY:                    T6 (também serve T5)
SOURCE_TYPE:                  CIENCIA
URL:                          https://orcid.org/0009-0001-5306-0125
ACCESS_METHOD:                API pública ORCID (JSON) + página pública do registo
CROPS:                        olivo
TOPICS:                       olivo;Xylella;batteriosi
GEOGRAPHIC_GRANULARITY:       REGIÃO — SICILIA
UPDATE_FREQUENCY:             NÃO SEI — nenhuma data de publicação legível na página
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        SIM — DOI
PUBLICATION_DATE_AVAILABLE:   SIM — 2026
RAW_EVIDENCE_PRESERVABLE:     SIM — registo público legível por HTTP
AUTOMATION_FEASIBILITY:       MÉDIA — site navegável, sem rota estruturada declarada
COLLECTION_FEASIBILITY:       NÃO SEI — o exemplo veio de API pública, não de descarga direta
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Omics approaches to unveil biotic stress responses in olive: current
                              knowledge and the future» https://doi.org/10.1093/jxb/erag337 (2026) — ORCID
                              public API /works
ADAMA_USE_CASE:               pesquisador com afiliacao italiana atual; alimenta T6 (pesquisadores), T5
                              (ciencia)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T6-007/MANIFEST.json
VERDICT:                      YELLOW — frequencia de atualizacao por provar
```

#### IT-T6-008 · CLAUDIO RATTI — registo cientifico ORCID (Alma Mater Studiorum  Universita' di Bologna)

```
SOURCE_ID:                    IT-T6-008
SOURCE_NAME:                  CLAUDIO RATTI — registo cientifico ORCID (Alma Mater Studiorum  Universita'
                              di Bologna)
SOURCE_OWNER:                 CLAUDIO RATTI · Alma Mater Studiorum  Universita' di Bologna
COUNTRY:                      ITALY
REGION:                       EMILIA-ROMAGNA
LANGUAGE:                     IT
TERRITORY:                    T6 (também serve T5)
SOURCE_TYPE:                  CIENCIA
URL:                          https://orcid.org/0000-0002-5640-2143
ACCESS_METHOD:                API pública ORCID (JSON) + página pública do registo
CROPS:                        vite
TOPICS:                       vite;flavescenza dorata
GEOGRAPHIC_GRANULARITY:       REGIÃO — EMILIA-ROMAGNA
UPDATE_FREQUENCY:             NÃO SEI — nenhuma data de publicação legível na página
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        SIM — DOI
PUBLICATION_DATE_AVAILABLE:   SIM — 2026
RAW_EVIDENCE_PRESERVABLE:     SIM — registo público legível por HTTP
AUTOMATION_FEASIBILITY:       MÉDIA — site navegável, sem rota estruturada declarada
COLLECTION_FEASIBILITY:       NÃO SEI — o exemplo veio de API pública, não de descarga direta
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Metabarcoding of Pollen Carried by Syrphids Reveals Novel Plant–Pollinator
                              Interactions in a Protected Natural Area and Agricultural Sites»
                              https://doi.org/10.1111/eea.70092 (2026) — ORCID public API /works
ADAMA_USE_CASE:               pesquisador com afiliacao italiana atual; alimenta T6 (pesquisadores), T5
                              (ciencia)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T6-008/MANIFEST.json
VERDICT:                      YELLOW — frequencia de atualizacao por provar
```

#### IT-T6-009 · Chiara D'ERRICO — registo cientifico ORCID (Istituto per la Protezione Sostenibile delle Piante IPSP - CNR)

```
SOURCE_ID:                    IT-T6-009
SOURCE_NAME:                  Chiara D'ERRICO — registo cientifico ORCID (Istituto per la Protezione
                              Sostenibile delle Piante IPSP - CNR)
SOURCE_OWNER:                 Chiara D'ERRICO · Istituto per la Protezione Sostenibile delle Piante IPSP -
                              CNR
COUNTRY:                      ITALY
REGION:                       PIEMONTE
LANGUAGE:                     IT
TERRITORY:                    T6 (também serve T5)
SOURCE_TYPE:                  CIENCIA
URL:                          https://orcid.org/0000-0003-0546-9900
ACCESS_METHOD:                API pública ORCID (JSON) + página pública do registo
CROPS:                        vite
TOPICS:                       vite;flavescenza dorata
GEOGRAPHIC_GRANULARITY:       REGIÃO — PIEMONTE
UPDATE_FREQUENCY:             NÃO SEI — nenhuma data de publicação legível na página
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        SIM — DOI
PUBLICATION_DATE_AVAILABLE:   SIM — 2026
RAW_EVIDENCE_PRESERVABLE:     SIM — registo público legível por HTTP
AUTOMATION_FEASIBILITY:       MÉDIA — site navegável, sem rota estruturada declarada
COLLECTION_FEASIBILITY:       NÃO SEI — o exemplo veio de API pública, não de descarga direta
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Development of a Field-Deployable Loop-Mediated Isothermal Amplification
                              Assay for the Rapid Detection of <i>Erysiphe corylacearum</i> in Hazelnut»
                              https://doi.org/10.3390/jof12010079 (2026) — ORCID public API /works
ADAMA_USE_CASE:               pesquisador com afiliacao italiana atual; alimenta T6 (pesquisadores), T5
                              (ciencia)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T6-009/MANIFEST.json
VERDICT:                      YELLOW — frequencia de atualizacao por provar
```

#### IT-T6-010 · Daniele Daffonchio — registo cientifico ORCID (University of Turin)

```
SOURCE_ID:                    IT-T6-010
SOURCE_NAME:                  Daniele Daffonchio — registo cientifico ORCID (University of Turin)
SOURCE_OWNER:                 Daniele Daffonchio · University of Turin
COUNTRY:                      ITALY
REGION:                       PIEMONTE
LANGUAGE:                     IT
TERRITORY:                    T6 (também serve T5)
SOURCE_TYPE:                  CIENCIA
URL:                          https://orcid.org/0000-0003-0947-925X
ACCESS_METHOD:                API pública ORCID (JSON) + página pública do registo
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       Popillia japonica
GEOGRAPHIC_GRANULARITY:       REGIÃO — PIEMONTE
UPDATE_FREQUENCY:             NÃO SEI — nenhuma data de publicação legível na página
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        SIM — DOI
PUBLICATION_DATE_AVAILABLE:   SIM — 2026
RAW_EVIDENCE_PRESERVABLE:     SIM — registo público legível por HTTP
AUTOMATION_FEASIBILITY:       MÉDIA — site navegável, sem rota estruturada declarada
COLLECTION_FEASIBILITY:       NÃO SEI — o exemplo veio de API pública, não de descarga direta
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «A Seasonal Record of Bacterial Communities in Micritized Carbonate
                              Sediments of the Eastern Red Sea» https://doi.org/10.1111/1462-2920.70313
                              (2026) — ORCID public API /works
ADAMA_USE_CASE:               pesquisador com afiliacao italiana atual; alimenta T6 (pesquisadores), T5
                              (ciencia)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T6-010/MANIFEST.json
VERDICT:                      YELLOW — frequencia de atualizacao por provar
```

#### IT-T6-011 · Dumitru Scutelnic — registo cientifico ORCID (University of Verona)

```
SOURCE_ID:                    IT-T6-011
SOURCE_NAME:                  Dumitru Scutelnic — registo cientifico ORCID (University of Verona)
SOURCE_OWNER:                 Dumitru Scutelnic · University of Verona
COUNTRY:                      ITALY
REGION:                       VENETO
LANGUAGE:                     IT
TERRITORY:                    T6 (também serve T5)
SOURCE_TYPE:                  CIENCIA
URL:                          https://orcid.org/0000-0001-6935-7540
ACCESS_METHOD:                API pública ORCID (JSON) + página pública do registo
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       precision farming;telerilevamento
GEOGRAPHIC_GRANULARITY:       REGIÃO — VENETO
UPDATE_FREQUENCY:             NÃO SEI — nenhuma data de publicação legível na página
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        SIM — DOI
PUBLICATION_DATE_AVAILABLE:   SIM — 2026
RAW_EVIDENCE_PRESERVABLE:     SIM — registo público legível por HTTP
AUTOMATION_FEASIBILITY:       MÉDIA — site navegável, sem rota estruturada declarada
COLLECTION_FEASIBILITY:       NÃO SEI — o exemplo veio de API pública, não de descarga direta
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Multi-model ensembles for object detection in multispectral images: A case
                              study for precision agriculture»
                              https://doi.org/10.1016/j.compag.2025.111213 (2026) — ORCID public API
                              /works
ADAMA_USE_CASE:               pesquisador com afiliacao italiana atual; alimenta T6 (pesquisadores), T5
                              (ciencia)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T6-011/MANIFEST.json
VERDICT:                      YELLOW — frequencia de atualizacao por provar
```

#### IT-T6-012 · Emilio Balducci — registo cientifico ORCID (University of Perugia)

```
SOURCE_ID:                    IT-T6-012
SOURCE_NAME:                  Emilio Balducci — registo cientifico ORCID (University of Perugia)
SOURCE_OWNER:                 Emilio Balducci · University of Perugia
COUNTRY:                      ITALY
REGION:                       UMBRIA
LANGUAGE:                     IT
TERRITORY:                    T6 (também serve T5)
SOURCE_TYPE:                  CIENCIA
URL:                          https://orcid.org/0000-0002-8656-7870
ACCESS_METHOD:                API pública ORCID (JSON) + página pública do registo
CROPS:                        grano
TOPICS:                       grano duro;Fusarium;micotossine
GEOGRAPHIC_GRANULARITY:       REGIÃO — UMBRIA
UPDATE_FREQUENCY:             NÃO SEI — nenhuma data de publicação legível na página
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        SIM — DOI
PUBLICATION_DATE_AVAILABLE:   SIM — 2026
RAW_EVIDENCE_PRESERVABLE:     SIM — registo público legível por HTTP
AUTOMATION_FEASIBILITY:       MÉDIA — site navegável, sem rota estruturada declarada
COLLECTION_FEASIBILITY:       NÃO SEI — o exemplo veio de API pública, não de descarga direta
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «High-Throughput Sequencing Study of the Mycobiota of Barley Grain Collected
                              in Northern and Central Italy and Accumulation of Fungal Secondary
                              Metabolites» https://doi.org/10.3390/toxins18090363 (2026) — ORCID public
                              API /works
ADAMA_USE_CASE:               pesquisador com afiliacao italiana atual; alimenta T6 (pesquisadores), T5
                              (ciencia)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T6-012/MANIFEST.json
VERDICT:                      YELLOW — frequencia de atualizacao por provar
```

#### IT-T6-013 · Francesco Nardi — registo cientifico ORCID (University of Siena)

```
SOURCE_ID:                    IT-T6-013
SOURCE_NAME:                  Francesco Nardi — registo cientifico ORCID (University of Siena)
SOURCE_OWNER:                 Francesco Nardi · University of Siena
COUNTRY:                      ITALY
REGION:                       NAZIONALE (sem recorte regional)
LANGUAGE:                     IT
TERRITORY:                    T6 (também serve T5)
SOURCE_TYPE:                  CIENCIA
URL:                          https://orcid.org/0000-0003-0271-9855
ACCESS_METHOD:                API pública ORCID (JSON) + página pública do registo
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       Popillia japonica
GEOGRAPHIC_GRANULARITY:       PAÍS — a fonte publica com alcance nacional
UPDATE_FREQUENCY:             NÃO SEI — nenhuma data de publicação legível na página
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        SIM — DOI
PUBLICATION_DATE_AVAILABLE:   SIM — 2026
RAW_EVIDENCE_PRESERVABLE:     SIM — registo público legível por HTTP
AUTOMATION_FEASIBILITY:       MÉDIA — site navegável, sem rota estruturada declarada
COLLECTION_FEASIBILITY:       NÃO SEI — o exemplo veio de API pública, não de descarga direta
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Echoes of Gondwana: Antarctic mite, <i></i>Maudheimia petronia<i></i>
                              (Acari: Maudheimiidae), reveals deep-time isolation and highly modified
                              mitochondrial tRNAs» https://doi.org/10.1093/zoolinnean/zlag163 (2026) —
                              ORCID public API /works
ADAMA_USE_CASE:               pesquisador com afiliacao italiana atual; alimenta T6 (pesquisadores), T5
                              (ciencia)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T6-013/MANIFEST.json
VERDICT:                      YELLOW — frequencia de atualizacao por provar
```

#### IT-T6-014 · Gerardo Puopolo — registo cientifico ORCID (University of Trento)

```
SOURCE_ID:                    IT-T6-014
SOURCE_NAME:                  Gerardo Puopolo — registo cientifico ORCID (University of Trento)
SOURCE_OWNER:                 Gerardo Puopolo · University of Trento
COUNTRY:                      ITALY
REGION:                       TRENTINO-ALTO ADIGE
LANGUAGE:                     IT
TERRITORY:                    T6 (também serve T5)
SOURCE_TYPE:                  CIENCIA
URL:                          https://orcid.org/0000-0002-4864-4396
ACCESS_METHOD:                API pública ORCID (JSON) + página pública do registo
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       biocontrollo;difesa biologica
GEOGRAPHIC_GRANULARITY:       REGIÃO — TRENTINO-ALTO ADIGE
UPDATE_FREQUENCY:             NÃO SEI — nenhuma data de publicação legível na página
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        SIM — DOI
PUBLICATION_DATE_AVAILABLE:   SIM — 2026
RAW_EVIDENCE_PRESERVABLE:     SIM — registo público legível por HTTP
AUTOMATION_FEASIBILITY:       MÉDIA — site navegável, sem rota estruturada declarada
COLLECTION_FEASIBILITY:       NÃO SEI — o exemplo veio de API pública, não de descarga direta
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Heat-inactivated Lysobacter capsici AZ78 cells effectively control
                              Peronospora belbahrii and Plasmopara viticola through direct and indirect
                              mechanisms» https://doi.org/10.1007/s10658-026-03207-4 (2026) — ORCID public
                              API /works
ADAMA_USE_CASE:               pesquisador com afiliacao italiana atual; alimenta T6 (pesquisadores), T5
                              (ciencia)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T6-014/MANIFEST.json
VERDICT:                      YELLOW — frequencia de atualizacao por provar
```

#### IT-T6-015 · Gianfranco ANFORA — registo cientifico ORCID (University of Trento)

```
SOURCE_ID:                    IT-T6-015
SOURCE_NAME:                  Gianfranco ANFORA — registo cientifico ORCID (University of Trento)
SOURCE_OWNER:                 Gianfranco ANFORA · University of Trento
COUNTRY:                      ITALY
REGION:                       TRENTINO-ALTO ADIGE
LANGUAGE:                     IT
TERRITORY:                    T6 (também serve T5)
SOURCE_TYPE:                  CIENCIA
URL:                          https://orcid.org/0000-0003-2545-1409
ACCESS_METHOD:                API pública ORCID (JSON) + página pública do registo
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       Halyomorpha;cimice asiatica
GEOGRAPHIC_GRANULARITY:       REGIÃO — TRENTINO-ALTO ADIGE
UPDATE_FREQUENCY:             NÃO SEI — nenhuma data de publicação legível na página
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        SIM — DOI
PUBLICATION_DATE_AVAILABLE:   SIM — 2026
RAW_EVIDENCE_PRESERVABLE:     SIM — registo público legível por HTTP
AUTOMATION_FEASIBILITY:       MÉDIA — site navegável, sem rota estruturada declarada
COLLECTION_FEASIBILITY:       NÃO SEI — o exemplo veio de API pública, não de descarga direta
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «A general DDE model for terrestrial arthropods: from theory to validation
                              guidelines under controlled conditions»
                              https://doi.org/10.1016/j.ecolmodel.2026.111619 (2026) — ORCID public API
                              /works
ADAMA_USE_CASE:               pesquisador com afiliacao italiana atual; alimenta T6 (pesquisadores), T5
                              (ciencia)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T6-015/MANIFEST.json
VERDICT:                      YELLOW — frequencia de atualizacao por provar
```

#### IT-T6-016 · Giulia Mandalà — registo cientifico ORCID (Verona University )

```
SOURCE_ID:                    IT-T6-016
SOURCE_NAME:                  Giulia Mandalà — registo cientifico ORCID (Verona University )
SOURCE_OWNER:                 Giulia Mandalà · Verona University
COUNTRY:                      ITALY
REGION:                       VENETO
LANGUAGE:                     IT
TERRITORY:                    T6 (também serve T5)
SOURCE_TYPE:                  CIENCIA
URL:                          https://orcid.org/0000-0001-7697-8310
ACCESS_METHOD:                API pública ORCID (JSON) + página pública do registo
CROPS:                        grano
TOPICS:                       grano duro;Fusarium;micotossine
GEOGRAPHIC_GRANULARITY:       REGIÃO — VENETO
UPDATE_FREQUENCY:             NÃO SEI — nenhuma data de publicação legível na página
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        SIM — DOI
PUBLICATION_DATE_AVAILABLE:   SIM — 2023
RAW_EVIDENCE_PRESERVABLE:     SIM — registo público legível por HTTP
AUTOMATION_FEASIBILITY:       MÉDIA — site navegável, sem rota estruturada declarada
COLLECTION_FEASIBILITY:       NÃO SEI — o exemplo veio de API pública, não de descarga direta
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Untargeted Metabolomics Reveals a Multi-Faceted Resistance Response to
                              Fusarium Head Blight Mediated by the Thinopyrum elongatum Fhb7E Locus
                              Transferred via Chromosome Engineering into Wheat»
                              https://doi.org/10.3390/cells12081113 (2023) — ORCID public API /works
ADAMA_USE_CASE:               pesquisador com afiliacao italiana atual; alimenta T6 (pesquisadores), T5
                              (ciencia)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T6-016/MANIFEST.json
VERDICT:                      YELLOW — frequencia de atualizacao por provar
```

#### IT-T6-017 · Graziella Amendola — registo cientifico ORCID (National Institute of Health)

```
SOURCE_ID:                    IT-T6-017
SOURCE_NAME:                  Graziella Amendola — registo cientifico ORCID (National Institute of Health)
SOURCE_OWNER:                 Graziella Amendola · National Institute of Health
COUNTRY:                      ITALY
REGION:                       NAZIONALE (sem recorte regional)
LANGUAGE:                     IT
TERRITORY:                    T6 (também serve T5)
SOURCE_TYPE:                  CIENCIA
URL:                          https://orcid.org/0000-0001-5461-0312
ACCESS_METHOD:                API pública ORCID (JSON) + página pública do registo
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       residui;fitofarmaci
GEOGRAPHIC_GRANULARITY:       PAÍS — a fonte publica com alcance nacional
UPDATE_FREQUENCY:             NÃO SEI — nenhuma data de publicação legível na página
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        SIM — DOI
PUBLICATION_DATE_AVAILABLE:   SIM — 2026
RAW_EVIDENCE_PRESERVABLE:     SIM — registo público legível por HTTP
AUTOMATION_FEASIBILITY:       MÉDIA — site navegável, sem rota estruturada declarada
COLLECTION_FEASIBILITY:       NÃO SEI — o exemplo veio de API pública, não de descarga direta
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Experimental determination of pesticide processing factors in milk during
                              soft cheese and ricotta cheese production»
                              https://doi.org/10.1016/j.foodcont.2025.111814 (2026) — ORCID public API
                              /works
ADAMA_USE_CASE:               pesquisador com afiliacao italiana atual; alimenta T6 (pesquisadores), T5
                              (ciencia)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T6-017/MANIFEST.json
VERDICT:                      YELLOW — frequencia de atualizacao por provar
```

#### IT-T6-018 · Leonardo Caproni — registo cientifico ORCID (Scuola Superiore Sant'Anna)

```
SOURCE_ID:                    IT-T6-018
SOURCE_NAME:                  Leonardo Caproni — registo cientifico ORCID (Scuola Superiore Sant'Anna)
SOURCE_OWNER:                 Leonardo Caproni · Scuola Superiore Sant'Anna
COUNTRY:                      ITALY
REGION:                       TOSCANA
LANGUAGE:                     IT
TERRITORY:                    T6 (também serve T5)
SOURCE_TYPE:                  CIENCIA
URL:                          https://orcid.org/0000-0002-7129-8575
ACCESS_METHOD:                API pública ORCID (JSON) + página pública do registo
CROPS:                        nocciolo
TOPICS:                       nocciolo;frutticoltura
GEOGRAPHIC_GRANULARITY:       REGIÃO — TOSCANA
UPDATE_FREQUENCY:             NÃO SEI — nenhuma data de publicação legível na página
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        SIM — DOI
PUBLICATION_DATE_AVAILABLE:   SIM — 2026
RAW_EVIDENCE_PRESERVABLE:     SIM — registo público legível por HTTP
AUTOMATION_FEASIBILITY:       MÉDIA — site navegável, sem rota estruturada declarada
COLLECTION_FEASIBILITY:       NÃO SEI — o exemplo veio de API pública, não de descarga direta
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Genotypic and transcriptomic characterization of a SAD gene cluster in
                              European hazelnut (Corylus avellana L.)»
                              https://doi.org/10.1016/j.jafr.2026.103294 (2026) — ORCID public API /works
ADAMA_USE_CASE:               pesquisador com afiliacao italiana atual; alimenta T6 (pesquisadores), T5
                              (ciencia)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T6-018/MANIFEST.json
VERDICT:                      YELLOW — frequencia de atualizacao por provar
```

#### IT-T6-019 · Leonardo Cera — registo cientifico ORCID (University of Padua)

```
SOURCE_ID:                    IT-T6-019
SOURCE_NAME:                  Leonardo Cera — registo cientifico ORCID (University of Padua)
SOURCE_OWNER:                 Leonardo Cera · University of Padua
COUNTRY:                      ITALY
REGION:                       VENETO
LANGUAGE:                     IT
TERRITORY:                    T6 (também serve T5)
SOURCE_TYPE:                  CIENCIA
URL:                          https://orcid.org/0009-0005-6118-7432
ACCESS_METHOD:                API pública ORCID (JSON) + página pública do registo
CROPS:                        vite
TOPICS:                       vite;flavescenza dorata
GEOGRAPHIC_GRANULARITY:       REGIÃO — VENETO
UPDATE_FREQUENCY:             NÃO SEI — nenhuma data de publicação legível na página
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        SIM — DOI
PUBLICATION_DATE_AVAILABLE:   SIM — 2026
RAW_EVIDENCE_PRESERVABLE:     SIM — registo público legível por HTTP
AUTOMATION_FEASIBILITY:       MÉDIA — site navegável, sem rota estruturada declarada
COLLECTION_FEASIBILITY:       NÃO SEI — o exemplo veio de API pública, não de descarga direta
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Natural Products for the Control of <i>Scaphoideus titanus</i> in
                              Vineyards: A Summary of Five-Year Field Trials»
                              https://doi.org/10.3390/insects17010083 (2026) — ORCID public API /works
ADAMA_USE_CASE:               pesquisador com afiliacao italiana atual; alimenta T6 (pesquisadores), T5
                              (ciencia)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T6-019/MANIFEST.json
VERDICT:                      YELLOW — frequencia de atualizacao por provar
```

#### IT-T6-020 · Lorenzo Baglieri — registo cientifico ORCID (Politecnico di Torino)

```
SOURCE_ID:                    IT-T6-020
SOURCE_NAME:                  Lorenzo Baglieri — registo cientifico ORCID (Politecnico di Torino)
SOURCE_OWNER:                 Lorenzo Baglieri · Politecnico di Torino
COUNTRY:                      ITALY
REGION:                       PIEMONTE
LANGUAGE:                     IT
TERRITORY:                    T6 (também serve T5)
SOURCE_TYPE:                  CIENCIA
URL:                          https://orcid.org/0000-0002-5022-5326
ACCESS_METHOD:                API pública ORCID (JSON) + página pública do registo
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       precision farming;telerilevamento
GEOGRAPHIC_GRANULARITY:       REGIÃO — PIEMONTE
UPDATE_FREQUENCY:             NÃO SEI — nenhuma data de publicação legível na página
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        SIM — DOI
PUBLICATION_DATE_AVAILABLE:   SIM — 2024
RAW_EVIDENCE_PRESERVABLE:     SIM — registo público legível por HTTP
AUTOMATION_FEASIBILITY:       MÉDIA — site navegável, sem rota estruturada declarada
COLLECTION_FEASIBILITY:       NÃO SEI — o exemplo veio de API pública, não de descarga direta
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Design of an Under-Actuated Mechanism for Collecting and Cutting Crop
                              Samples in Precision Agriculture»
                              https://doi.org/10.1007/978-3-031-59257-7_53 (2024) — ORCID public API
                              /works
ADAMA_USE_CASE:               pesquisador com afiliacao italiana atual; alimenta T6 (pesquisadores), T5
                              (ciencia)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T6-020/MANIFEST.json
VERDICT:                      YELLOW — frequencia de atualizacao por provar
```

#### IT-T6-021 · Luca Finetti — registo cientifico ORCID (University of Ferrara)

```
SOURCE_ID:                    IT-T6-021
SOURCE_NAME:                  Luca Finetti — registo cientifico ORCID (University of Ferrara)
SOURCE_OWNER:                 Luca Finetti · University of Ferrara
COUNTRY:                      ITALY
REGION:                       NAZIONALE (sem recorte regional)
LANGUAGE:                     IT
TERRITORY:                    T6 (também serve T5)
SOURCE_TYPE:                  CIENCIA
URL:                          https://orcid.org/0000-0001-5558-9156
ACCESS_METHOD:                API pública ORCID (JSON) + página pública do registo
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       Halyomorpha;cimice asiatica
GEOGRAPHIC_GRANULARITY:       PAÍS — a fonte publica com alcance nacional
UPDATE_FREQUENCY:             NÃO SEI — nenhuma data de publicação legível na página
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        SIM — DOI
PUBLICATION_DATE_AVAILABLE:   SIM — 2021
RAW_EVIDENCE_PRESERVABLE:     SIM — registo público legível por HTTP
AUTOMATION_FEASIBILITY:       MÉDIA — site navegável, sem rota estruturada declarada
COLLECTION_FEASIBILITY:       NÃO SEI — o exemplo veio de API pública, não de descarga direta
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Characterization of Halyomorpha halys TAR1 reveals its involvement in
                              (E)-2-decenal pheromone perception» https://doi.org/10.1242/jeb.238816
                              (2021) — ORCID public API /works
ADAMA_USE_CASE:               pesquisador com afiliacao italiana atual; alimenta T6 (pesquisadores), T5
                              (ciencia)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T6-021/MANIFEST.json
VERDICT:                      YELLOW — frequencia de atualizacao por provar
```

#### IT-T6-022 · Luca Mazzon — registo cientifico ORCID (Università degli Studi di Padova)

```
SOURCE_ID:                    IT-T6-022
SOURCE_NAME:                  Luca Mazzon — registo cientifico ORCID (Università degli Studi di Padova)
SOURCE_OWNER:                 Luca Mazzon · Università degli Studi di Padova
COUNTRY:                      ITALY
REGION:                       VENETO
LANGUAGE:                     IT
TERRITORY:                    T6 (também serve T5)
SOURCE_TYPE:                  CIENCIA
URL:                          https://orcid.org/0000-0002-8459-893X
ACCESS_METHOD:                API pública ORCID (JSON) + página pública do registo
CROPS:                        olivo
TOPICS:                       olivo;mosca delle olive
GEOGRAPHIC_GRANULARITY:       REGIÃO — VENETO
UPDATE_FREQUENCY:             NÃO SEI — nenhuma data de publicação legível na página
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        SIM — DOI
PUBLICATION_DATE_AVAILABLE:   SIM — 2026
RAW_EVIDENCE_PRESERVABLE:     SIM — registo público legível por HTTP
AUTOMATION_FEASIBILITY:       MÉDIA — site navegável, sem rota estruturada declarada
COLLECTION_FEASIBILITY:       NÃO SEI — o exemplo veio de API pública, não de descarga direta
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Antimicrobial treatment of egg-infested olives is associated with
                              perturbation and carry-over changes on bacterial communities in the olive
                              fly Bactrocera oleae (Rossi) (Diptera, Tephritidae)»
                              https://doi.org/10.1093/jisesa/ieag108 (2026) — ORCID public API /works
ADAMA_USE_CASE:               pesquisador com afiliacao italiana atual; alimenta T6 (pesquisadores), T5
                              (ciencia)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T6-022/MANIFEST.json
VERDICT:                      YELLOW — frequencia de atualizacao por provar
```

#### IT-T6-023 · Marco Mancini — registo cientifico ORCID (University of Florence)

```
SOURCE_ID:                    IT-T6-023
SOURCE_NAME:                  Marco Mancini — registo cientifico ORCID (University of Florence)
SOURCE_OWNER:                 Marco Mancini · University of Florence
COUNTRY:                      ITALY
REGION:                       TOSCANA
LANGUAGE:                     IT
TERRITORY:                    T6 (também serve T5)
SOURCE_TYPE:                  CIENCIA
URL:                          https://orcid.org/0000-0002-1454-4995
ACCESS_METHOD:                API pública ORCID (JSON) + página pública do registo
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       agrometeorologia;modelli
GEOGRAPHIC_GRANULARITY:       REGIÃO — TOSCANA
UPDATE_FREQUENCY:             NÃO SEI — nenhuma data de publicação legível na página
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        SIM — DOI
PUBLICATION_DATE_AVAILABLE:   SIM — 2020
RAW_EVIDENCE_PRESERVABLE:     SIM — registo público legível por HTTP
AUTOMATION_FEASIBILITY:       MÉDIA — site navegável, sem rota estruturada declarada
COLLECTION_FEASIBILITY:       NÃO SEI — o exemplo veio de API pública, não de descarga direta
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Integrating satellite data with a Nitrogen Nutrition Curve for precision
                              top-dress fertilization of durum wheat»
                              https://doi.org/10.1016/j.eja.2020.126148 (2020) — ORCID public API /works
ADAMA_USE_CASE:               pesquisador com afiliacao italiana atual; alimenta T6 (pesquisadores), T5
                              (ciencia)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T6-023/MANIFEST.json
VERDICT:                      YELLOW — frequencia de atualizacao por provar
```

#### IT-T6-024 · Marco Perfetto — registo cientifico ORCID (University of Milan)

```
SOURCE_ID:                    IT-T6-024
SOURCE_NAME:                  Marco Perfetto — registo cientifico ORCID (University of Milan)
SOURCE_OWNER:                 Marco Perfetto · University of Milan
COUNTRY:                      ITALY
REGION:                       LOMBARDIA
LANGUAGE:                     IT
TERRITORY:                    T6 (também serve T5)
SOURCE_TYPE:                  CIENCIA
URL:                          https://orcid.org/0000-0001-9370-2500
ACCESS_METHOD:                API pública ORCID (JSON) + página pública do registo
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       cover crop;rigenerativa
GEOGRAPHIC_GRANULARITY:       REGIÃO — LOMBARDIA
UPDATE_FREQUENCY:             NÃO SEI — nenhuma data de publicação legível na página
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   SIM — 2026
RAW_EVIDENCE_PRESERVABLE:     SIM — registo público legível por HTTP
AUTOMATION_FEASIBILITY:       MÉDIA — site navegável, sem rota estruturada declarada
COLLECTION_FEASIBILITY:       NÃO SEI — o exemplo veio de API pública, não de descarga direta
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Estimating spatial and temporal variability of crop growth by radiation-
                              driven models based on satellite data assimilation»
                              https://air.unimi.it/handle/2434/1223355 (2026) — ORCID public API /works
ADAMA_USE_CASE:               pesquisador com afiliacao italiana atual; alimenta T6 (pesquisadores), T5
                              (ciencia)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T6-024/MANIFEST.json
VERDICT:                      YELLOW — frequencia de atualizacao por provar
```

#### IT-T6-025 · Marwa Mourou — registo cientifico ORCID (Università degli Studi di Bari Aldo Moro)

```
SOURCE_ID:                    IT-T6-025
SOURCE_NAME:                  Marwa Mourou — registo cientifico ORCID (Università degli Studi di Bari Aldo
                              Moro)
SOURCE_OWNER:                 Marwa Mourou · Università degli Studi di Bari Aldo Moro
COUNTRY:                      ITALY
REGION:                       PUGLIA
LANGUAGE:                     IT
TERRITORY:                    T6 (também serve T5)
SOURCE_TYPE:                  CIENCIA
URL:                          https://orcid.org/0000-0002-9925-3520
ACCESS_METHOD:                API pública ORCID (JSON) + página pública do registo
CROPS:                        olivo
TOPICS:                       olivo;Xylella;batteriosi
GEOGRAPHIC_GRANULARITY:       REGIÃO — PUGLIA
UPDATE_FREQUENCY:             NÃO SEI — nenhuma data de publicação legível na página
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        SIM — DOI
PUBLICATION_DATE_AVAILABLE:   SIM — 2025
RAW_EVIDENCE_PRESERVABLE:     SIM — registo público legível por HTTP
AUTOMATION_FEASIBILITY:       MÉDIA — site navegável, sem rota estruturada declarada
COLLECTION_FEASIBILITY:       NÃO SEI — o exemplo veio de API pública, não de descarga direta
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Insight into biological strategies and main challenges to control the
                              phytopathogenic bacterium Xylella fastidiosa»
                              https://doi.org/10.3389/fpls.2025.1608687 (2025) — ORCID public API /works
ADAMA_USE_CASE:               pesquisador com afiliacao italiana atual; alimenta T6 (pesquisadores), T5
                              (ciencia)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T6-025/MANIFEST.json
VERDICT:                      YELLOW — frequencia de atualizacao por provar
```

#### IT-T6-026 · Paolo Boccacci — registo cientifico ORCID (Consiglio Nazionale delle Ricerche)

```
SOURCE_ID:                    IT-T6-026
SOURCE_NAME:                  Paolo Boccacci — registo cientifico ORCID (Consiglio Nazionale delle
                              Ricerche)
SOURCE_OWNER:                 Paolo Boccacci · Consiglio Nazionale delle Ricerche
COUNTRY:                      ITALY
REGION:                       LAZIO
LANGUAGE:                     IT
TERRITORY:                    T6 (também serve T5)
SOURCE_TYPE:                  CIENCIA
URL:                          https://orcid.org/0000-0001-8574-0478
ACCESS_METHOD:                API pública ORCID (JSON) + página pública do registo
CROPS:                        nocciolo
TOPICS:                       nocciolo;frutticoltura
GEOGRAPHIC_GRANULARITY:       REGIÃO — LAZIO
UPDATE_FREQUENCY:             NÃO SEI — nenhuma data de publicação legível na página
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        SIM — DOI
PUBLICATION_DATE_AVAILABLE:   SIM — 2024
RAW_EVIDENCE_PRESERVABLE:     SIM — registo público legível por HTTP
AUTOMATION_FEASIBILITY:       MÉDIA — site navegável, sem rota estruturada declarada
COLLECTION_FEASIBILITY:       NÃO SEI — o exemplo veio de API pública, não de descarga direta
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Grafting with non‐suckering rootstock increases drought tolerance in
                              Corylus avellana L. through physiological and biochemical adjustments»
                              https://doi.org/10.1111/ppl.70003 (2024) — ORCID public API /works
ADAMA_USE_CASE:               pesquisador com afiliacao italiana atual; alimenta T6 (pesquisadores), T5
                              (ciencia)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T6-026/MANIFEST.json
VERDICT:                      YELLOW — frequencia de atualizacao por provar
```

#### IT-T6-027 · Paolo Grazieschi — registo cientifico ORCID (Fondazione Bruno Kessler)

```
SOURCE_ID:                    IT-T6-027
SOURCE_NAME:                  Paolo Grazieschi — registo cientifico ORCID (Fondazione Bruno Kessler)
SOURCE_OWNER:                 Paolo Grazieschi · Fondazione Bruno Kessler
COUNTRY:                      ITALY
REGION:                       TRENTINO-ALTO ADIGE
LANGUAGE:                     IT
TERRITORY:                    T6 (também serve T5)
SOURCE_TYPE:                  CIENCIA
URL:                          https://orcid.org/0009-0009-6027-471X
ACCESS_METHOD:                API pública ORCID (JSON) + página pública do registo
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       precision farming;telerilevamento
GEOGRAPHIC_GRANULARITY:       REGIÃO — TRENTINO-ALTO ADIGE
UPDATE_FREQUENCY:             NÃO SEI — nenhuma data de publicação legível na página
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        SIM — DOI
PUBLICATION_DATE_AVAILABLE:   SIM — 2025
RAW_EVIDENCE_PRESERVABLE:     SIM — registo público legível por HTTP
AUTOMATION_FEASIBILITY:       MÉDIA — site navegável, sem rota estruturada declarada
COLLECTION_FEASIBILITY:       NÃO SEI — o exemplo veio de API pública, não de descarga direta
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Soilcast: a Multitask Encoder-Decoder AI Model for Precision Agriculture»
                              https://doi.org/10.1145/3672608.3707808 (2025) — ORCID public API /works
ADAMA_USE_CASE:               pesquisador com afiliacao italiana atual; alimenta T6 (pesquisadores), T5
                              (ciencia)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T6-027/MANIFEST.json
VERDICT:                      YELLOW — frequencia de atualizacao por provar
```

#### IT-T6-028 · ROBERTO RIZZO — registo cientifico ORCID (CREA - Research Centre for Plant Protection and Certification)

```
SOURCE_ID:                    IT-T6-028
SOURCE_NAME:                  ROBERTO RIZZO — registo cientifico ORCID (CREA - Research Centre for Plant
                              Protection and Certification)
SOURCE_OWNER:                 ROBERTO RIZZO · CREA - Research Centre for Plant Protection and
                              Certification
COUNTRY:                      ITALY
REGION:                       SICILIA
LANGUAGE:                     IT
TERRITORY:                    T6 (também serve T5)
SOURCE_TYPE:                  CIENCIA
URL:                          https://orcid.org/0000-0003-1628-643X
ACCESS_METHOD:                API pública ORCID (JSON) + página pública do registo
CROPS:                        olivo
TOPICS:                       olivo;mosca delle olive
GEOGRAPHIC_GRANULARITY:       REGIÃO — SICILIA
UPDATE_FREQUENCY:             NÃO SEI — nenhuma data de publicação legível na página
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        SIM — DOI
PUBLICATION_DATE_AVAILABLE:   SIM — 2026
RAW_EVIDENCE_PRESERVABLE:     SIM — registo público legível por HTTP
AUTOMATION_FEASIBILITY:       MÉDIA — site navegável, sem rota estruturada declarada
COLLECTION_FEASIBILITY:       NÃO SEI — o exemplo veio de API pública, não de descarga direta
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Encapsulation of a <i>N</i>-Alkylamide-Enriched Fraction from <i>Acmella
                              oleracea</i> and Its Efficacy Against <i>Tuta absoluta</i>, the Invasive Key
                              Tomato Pest» https://doi.org/10.3390/insects17050455 (2026) — ORCID public
                              API /works
ADAMA_USE_CASE:               pesquisador com afiliacao italiana atual; alimenta T6 (pesquisadores), T5
                              (ciencia)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T6-028/MANIFEST.json
VERDICT:                      YELLOW — frequencia de atualizacao por provar
```

#### IT-T6-029 · Roberta Maria Gravagno — registo cientifico ORCID (University of Catania)

```
SOURCE_ID:                    IT-T6-029
SOURCE_NAME:                  Roberta Maria Gravagno — registo cientifico ORCID (University of Catania)
SOURCE_OWNER:                 Roberta Maria Gravagno · University of Catania
COUNTRY:                      ITALY
REGION:                       SICILIA
LANGUAGE:                     IT
TERRITORY:                    T6 (também serve T5)
SOURCE_TYPE:                  CIENCIA
URL:                          https://orcid.org/0009-0005-2447-3608
ACCESS_METHOD:                API pública ORCID (JSON) + página pública do registo
CROPS:                        vite
TOPICS:                       vite;Plasmopara viticola
GEOGRAPHIC_GRANULARITY:       REGIÃO — SICILIA
UPDATE_FREQUENCY:             NÃO SEI — nenhuma data de publicação legível na página
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        SIM — DOI
PUBLICATION_DATE_AVAILABLE:   SIM — 2026
RAW_EVIDENCE_PRESERVABLE:     SIM — registo público legível por HTTP
AUTOMATION_FEASIBILITY:       MÉDIA — site navegável, sem rota estruturada declarada
COLLECTION_FEASIBILITY:       NÃO SEI — o exemplo veio de API pública, não de descarga direta
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Sicilian Wineries' Intention to Comply With Sustainability Certification as
                              a Strategic Business Behavior» https://doi.org/10.1002/sd.71410 (2026) —
                              ORCID public API /works
ADAMA_USE_CASE:               pesquisador com afiliacao italiana atual; alimenta T6 (pesquisadores), T5
                              (ciencia)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T6-029/MANIFEST.json
VERDICT:                      YELLOW — frequencia de atualizacao por provar
```

#### IT-T6-030 · Roberta Paris — registo cientifico ORCID (Council for Agricultural Research and Economics Analysis (CREA) )

```
SOURCE_ID:                    IT-T6-030
SOURCE_NAME:                  Roberta Paris — registo cientifico ORCID (Council for Agricultural Research
                              and Economics Analysis (CREA) )
SOURCE_OWNER:                 Roberta Paris · Council for Agricultural Research and Economics Analysis
                              (CREA)
COUNTRY:                      ITALY
REGION:                       EMILIA-ROMAGNA
LANGUAGE:                     IT
TERRITORY:                    T6 (também serve T5)
SOURCE_TYPE:                  CIENCIA
URL:                          https://orcid.org/0000-0001-7823-2475
ACCESS_METHOD:                API pública ORCID (JSON) + página pública do registo
CROPS:                        melo
TOPICS:                       melo;Venturia inaequalis
GEOGRAPHIC_GRANULARITY:       REGIÃO — EMILIA-ROMAGNA
UPDATE_FREQUENCY:             NÃO SEI — nenhuma data de publicação legível na página
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        SIM — DOI
PUBLICATION_DATE_AVAILABLE:   SIM — 2026
RAW_EVIDENCE_PRESERVABLE:     SIM — registo público legível por HTTP
AUTOMATION_FEASIBILITY:       MÉDIA — site navegável, sem rota estruturada declarada
COLLECTION_FEASIBILITY:       NÃO SEI — o exemplo veio de API pública, não de descarga direta
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Exploiting Exhausted Biomasses from Essential Oil Distillation in Animal
                              Feeding: Chemical Characterisation and Volatile Profile of Laurel Bay
                              (<i>Laurus nobilis</i>), Lavender (<i>Lavandula angustifo»
                              https://doi.org/10.3390/pr14172779 (2026) — ORCID public API /works
ADAMA_USE_CASE:               pesquisador com afiliacao italiana atual; alimenta T6 (pesquisadores), T5
                              (ciencia)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T6-030/MANIFEST.json
VERDICT:                      YELLOW — frequencia de atualizacao por provar
```

#### IT-T6-031 · Roberto Ferrise — registo cientifico ORCID (University of Florence)

```
SOURCE_ID:                    IT-T6-031
SOURCE_NAME:                  Roberto Ferrise — registo cientifico ORCID (University of Florence)
SOURCE_OWNER:                 Roberto Ferrise · University of Florence
COUNTRY:                      ITALY
REGION:                       TOSCANA
LANGUAGE:                     IT
TERRITORY:                    T6 (também serve T5)
SOURCE_TYPE:                  CIENCIA
URL:                          https://orcid.org/0000-0001-8236-7823
ACCESS_METHOD:                API pública ORCID (JSON) + página pública do registo
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       agrometeorologia;modelli
GEOGRAPHIC_GRANULARITY:       REGIÃO — TOSCANA
UPDATE_FREQUENCY:             NÃO SEI — nenhuma data de publicação legível na página
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        SIM — DOI
PUBLICATION_DATE_AVAILABLE:   SIM — 2026
RAW_EVIDENCE_PRESERVABLE:     SIM — registo público legível por HTTP
AUTOMATION_FEASIBILITY:       MÉDIA — site navegável, sem rota estruturada declarada
COLLECTION_FEASIBILITY:       NÃO SEI — o exemplo veio de API pública, não de descarga direta
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «The FraNchEstYN framework for modelling crop yield losses due to fungal
                              diseases» https://doi.org/10.2139/ssrn.7228923 (2026) — ORCID public API
                              /works
ADAMA_USE_CASE:               pesquisador com afiliacao italiana atual; alimenta T6 (pesquisadores), T5
                              (ciencia)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T6-031/MANIFEST.json
VERDICT:                      YELLOW — frequencia de atualizacao por provar
```

#### IT-T6-032 · Rosa Francaviglia — registo cientifico ORCID (Consiglio per la ricerca in agricoltura e l'analisi dell'economia agraria (CREA))

```
SOURCE_ID:                    IT-T6-032
SOURCE_NAME:                  Rosa Francaviglia — registo cientifico ORCID (Consiglio per la ricerca in
                              agricoltura e l'analisi dell'economia agraria (CREA))
SOURCE_OWNER:                 Rosa Francaviglia · Consiglio per la ricerca in agricoltura e l'analisi
                              dell'economia agraria (CREA)
COUNTRY:                      ITALY
REGION:                       LAZIO
LANGUAGE:                     IT
TERRITORY:                    T6 (também serve T5)
SOURCE_TYPE:                  CIENCIA
URL:                          https://orcid.org/0000-0002-4362-5428
ACCESS_METHOD:                API pública ORCID (JSON) + página pública do registo
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       suolo;sostanza organica
GEOGRAPHIC_GRANULARITY:       REGIÃO — LAZIO
UPDATE_FREQUENCY:             NÃO SEI — nenhuma data de publicação legível na página
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        SIM — DOI
PUBLICATION_DATE_AVAILABLE:   SIM — 2026
RAW_EVIDENCE_PRESERVABLE:     SIM — registo público legível por HTTP
AUTOMATION_FEASIBILITY:       MÉDIA — site navegável, sem rota estruturada declarada
COLLECTION_FEASIBILITY:       NÃO SEI — o exemplo veio de API pública, não de descarga direta
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Prediction of soil organic carbon increase in the transition from shifting
                              cultivation to agroforestry in the Indian East Himalayas»
                              https://doi.org/10.1002/eap.70286 (2026) — ORCID public API /works
ADAMA_USE_CASE:               pesquisador com afiliacao italiana atual; alimenta T6 (pesquisadores), T5
                              (ciencia)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T6-032/MANIFEST.json
VERDICT:                      YELLOW — frequencia de atualizacao por provar
```

#### IT-T6-033 · Stefano Maini — registo cientifico ORCID (Alma Mater Studiorum - Università di Bologna)

```
SOURCE_ID:                    IT-T6-033
SOURCE_NAME:                  Stefano Maini — registo cientifico ORCID (Alma Mater Studiorum - Università
                              di Bologna)
SOURCE_OWNER:                 Stefano Maini · Alma Mater Studiorum - Università di Bologna
COUNTRY:                      ITALY
REGION:                       EMILIA-ROMAGNA
LANGUAGE:                     IT
TERRITORY:                    T6 (também serve T5)
SOURCE_TYPE:                  CIENCIA
URL:                          https://orcid.org/0000-0001-7272-1243
ACCESS_METHOD:                API pública ORCID (JSON) + página pública do registo
CROPS:                        mais
TOPICS:                       mais;piralide
GEOGRAPHIC_GRANULARITY:       REGIÃO — EMILIA-ROMAGNA
UPDATE_FREQUENCY:             NÃO SEI — nenhuma data de publicação legível na página
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        SIM — DOI
PUBLICATION_DATE_AVAILABLE:   SIM — 2026
RAW_EVIDENCE_PRESERVABLE:     SIM — registo público legível por HTTP
AUTOMATION_FEASIBILITY:       MÉDIA — site navegável, sem rota estruturada declarada
COLLECTION_FEASIBILITY:       NÃO SEI — o exemplo veio de API pública, não de descarga direta
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «In memory of Jerome Anthony Klun (1939&ndash;2026)»
                              https://doi.org/10.3897/bull.insectology.195590 (2026) — ORCID public API
                              /works
ADAMA_USE_CASE:               pesquisador com afiliacao italiana atual; alimenta T6 (pesquisadores), T5
                              (ciencia)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T6-033/MANIFEST.json
VERDICT:                      YELLOW — frequencia de atualizacao por provar
```

#### IT-T6-034 · Tito Caffi — registo cientifico ORCID (Università Cattolica del Sacro Cuore)

```
SOURCE_ID:                    IT-T6-034
SOURCE_NAME:                  Tito Caffi — registo cientifico ORCID (Università Cattolica del Sacro Cuore)
SOURCE_OWNER:                 Tito Caffi · Università Cattolica del Sacro Cuore
COUNTRY:                      ITALY
REGION:                       EMILIA-ROMAGNA
LANGUAGE:                     IT
TERRITORY:                    T6 (também serve T5)
SOURCE_TYPE:                  CIENCIA
URL:                          https://orcid.org/0000-0001-9929-4130
ACCESS_METHOD:                API pública ORCID (JSON) + página pública do registo
CROPS:                        vite
TOPICS:                       vite;Plasmopara viticola
GEOGRAPHIC_GRANULARITY:       REGIÃO — EMILIA-ROMAGNA
UPDATE_FREQUENCY:             NÃO SEI — nenhuma data de publicação legível na página
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        SIM — DOI
PUBLICATION_DATE_AVAILABLE:   SIM — 2022
RAW_EVIDENCE_PRESERVABLE:     SIM — registo público legível por HTTP
AUTOMATION_FEASIBILITY:       MÉDIA — site navegável, sem rota estruturada declarada
COLLECTION_FEASIBILITY:       NÃO SEI — o exemplo veio de API pública, não de descarga direta
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Development of an online pan-European Integrated Pest Management Resource
                              Toolbox» https://doi.org/10.12688/openreseurope.14679.2 (2022) — ORCID
                              public API /works
ADAMA_USE_CASE:               pesquisador com afiliacao italiana atual; alimenta T6 (pesquisadores), T5
                              (ciencia)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T6-034/MANIFEST.json
VERDICT:                      YELLOW — frequencia de atualizacao por provar
```

#### IT-T6-035 · Vera Pavese — registo cientifico ORCID (University of Turin)

```
SOURCE_ID:                    IT-T6-035
SOURCE_NAME:                  Vera Pavese — registo cientifico ORCID (University of Turin)
SOURCE_OWNER:                 Vera Pavese · University of Turin
COUNTRY:                      ITALY
REGION:                       PIEMONTE
LANGUAGE:                     IT
TERRITORY:                    T6 (também serve T5)
SOURCE_TYPE:                  CIENCIA
URL:                          https://orcid.org/0000-0002-6863-3950
ACCESS_METHOD:                API pública ORCID (JSON) + página pública do registo
CROPS:                        nocciolo
TOPICS:                       nocciolo;frutticoltura
GEOGRAPHIC_GRANULARITY:       REGIÃO — PIEMONTE
UPDATE_FREQUENCY:             NÃO SEI — nenhuma data de publicação legível na página
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        SIM — DOI
PUBLICATION_DATE_AVAILABLE:   SIM — 2026
RAW_EVIDENCE_PRESERVABLE:     SIM — registo público legível por HTTP
AUTOMATION_FEASIBILITY:       MÉDIA — site navegável, sem rota estruturada declarada
COLLECTION_FEASIBILITY:       NÃO SEI — o exemplo veio de API pública, não de descarga direta
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Into the Unknown: Hints to Overcome Recalcitrance in Woody Fruit Crops»
                              https://doi.org/10.1007/s00344-026-12211-1 (2026) — ORCID public API /works
ADAMA_USE_CASE:               pesquisador com afiliacao italiana atual; alimenta T6 (pesquisadores), T5
                              (ciencia)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T6-035/MANIFEST.json
VERDICT:                      YELLOW — frequencia de atualizacao por provar
```

#### IT-T6-036 · sara ruschioni — registo cientifico ORCID (Marche Polytechnic University)

```
SOURCE_ID:                    IT-T6-036
SOURCE_NAME:                  sara ruschioni — registo cientifico ORCID (Marche Polytechnic University)
SOURCE_OWNER:                 sara ruschioni · Marche Polytechnic University
COUNTRY:                      ITALY
REGION:                       MARCHE
LANGUAGE:                     IT
TERRITORY:                    T6 (também serve T5)
SOURCE_TYPE:                  CIENCIA
URL:                          https://orcid.org/0000-0003-2965-6364
ACCESS_METHOD:                API pública ORCID (JSON) + página pública do registo
CROPS:                        mais
TOPICS:                       mais;piralide
GEOGRAPHIC_GRANULARITY:       REGIÃO — MARCHE
UPDATE_FREQUENCY:             NÃO SEI — nenhuma data de publicação legível na página
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        SIM — DOI
PUBLICATION_DATE_AVAILABLE:   SIM — 2026
RAW_EVIDENCE_PRESERVABLE:     SIM — registo público legível por HTTP
AUTOMATION_FEASIBILITY:       MÉDIA — site navegável, sem rota estruturada declarada
COLLECTION_FEASIBILITY:       NÃO SEI — o exemplo veio de API pública, não de descarga direta
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Species Composition and Emergence Patterns of <i>Agriotes litigiosus</i>,
                              <i>A. brevis</i> and <i>A. sordidus</i> (Coleoptera: Elateridae) in Central
                              Italy» https://doi.org/10.3390/insects17020172 (2026) — ORCID public API
                              /works
ADAMA_USE_CASE:               pesquisador com afiliacao italiana atual; alimenta T6 (pesquisadores), T5
                              (ciencia)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T6-036/MANIFEST.json
VERDICT:                      YELLOW — frequencia de atualizacao por provar
```

### T7 · TECHNICAL NETWORK — ITALY · onda 1 (2026-09-14)

*2 fontes registradas nesta secção. Cada uma foi aberta, observada e tem exemplo real preservado em `data/samples/IT-SOURCE-SAMPLES/<SOURCE_ID>/`. Registada ≠ contratada: nenhuma tem contrato de busca, e nenhuma coleta foi corrida.*

#### IT-T7-013 · CONAF — Consiglio Ordine Nazionale Dottori Agronomi e Forestali

```
SOURCE_ID:                    IT-T7-013
SOURCE_NAME:                  CONAF — Consiglio Ordine Nazionale Dottori Agronomi e Forestali
SOURCE_OWNER:                 CONAF
COUNTRY:                      ITALY
REGION:                       NAZIONALE (sem recorte regional)
LANGUAGE:                     IT-IT
TERRITORY:                    T7 (também serve T12)
SOURCE_TYPE:                  ORGANIZACAO
URL:                          https://www.conaf.it/
ACCESS_METHOD:                HTML
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       agronomi;ordine professionale
GEOGRAPHIC_GRANULARITY:       PAÍS — a fonte publica com alcance nacional
UPDATE_FREQUENCY:             observada por data visível na página: 2026-09-14
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   SIM — 2022-10-04
RAW_EVIDENCE_PRESERVABLE:     SIM — HTML obtido por HTTP
AUTOMATION_FEASIBILITY:       ALTA — rota estruturada declarada (API/opendata)
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Circolari e Delibere - CONAF» https://www.conaf.it/formazione-
                              professionale-continua/normativa-formazione-professionale-
                              continua/circolari-2/ — HTML, 107524 bytes lidos em 2026-09-14
ADAMA_USE_CASE:               ordem profissional / rede tecnica; alimenta T7 (rede tecnica), T12 (politica
                              e ambiente agricola)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T7-013/MANIFEST.json
VERDICT:                      GREEN — fonte aberta, exemplo real observado e preservado
```

#### IT-T7-014 · Consorzi Agrari d'Italia — CAI

```
SOURCE_ID:                    IT-T7-014
SOURCE_NAME:                  Consorzi Agrari d'Italia — CAI
SOURCE_OWNER:                 Consorzi Agrari d'Italia
COUNTRY:                      ITALY
REGION:                       NAZIONALE (sem recorte regional)
LANGUAGE:                     EN
TERRITORY:                    T7 (também serve T10)
SOURCE_TYPE:                  ORGANIZACAO
URL:                          https://www.consorziagrariditalia.it/chi-siamo/
ACCESS_METHOD:                PDF ligado a partir da página da fonte
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       consorzio agrario;distribuzione
GEOGRAPHIC_GRANULARITY:       PAÍS — a fonte publica com alcance nacional
UPDATE_FREQUENCY:             observada por data visível na página: 2026-06-30
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   NÃO SEI — nenhuma data legível no item observado
RAW_EVIDENCE_PRESERVABLE:     SIM — PDF obtido por HTTP
AUTOMATION_FEASIBILITY:       ALTA — rota estruturada declarada (API/opendata)
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 NÃO REPRESENTATIVO — o item que se conseguiu confirmar por HTTP e' papelada administrativa (codigo etico, termos, formulario) — prova que a organizacao existe, NAO prova o que ela publica na sua area tecnica. Um exemplo representativo exige navegador ou leitura humana da seccao de noticias.
ADAMA_USE_CASE:               organizacao agricola / representacao de produtores; alimenta T7 (rede
                              tecnica), T10 (mercado e industria)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T7-014/MANIFEST.json
VERDICT:                      YELLOW — registada como real e util, mas sem exemplo representativo do que entrega; rever com navegador antes de contratar coleta.
```

### T9 · COMPETITORS — ITALY · onda 1 (2026-09-14)

*5 fontes registradas nesta secção. Cada uma foi aberta, observada e tem exemplo real preservado em `data/samples/IT-SOURCE-SAMPLES/<SOURCE_ID>/`. Registada ≠ contratada: nenhuma tem contrato de busca, e nenhuma coleta foi corrida.*

#### IT-T9-009 · Cifo

```
SOURCE_ID:                    IT-T9-009
SOURCE_NAME:                  Cifo
SOURCE_OWNER:                 Cifo
COUNTRY:                      ITALY
REGION:                       EMILIA-ROMAGNA
LANGUAGE:                     IT-IT
TERRITORY:                    T9 (também serve T10)
SOURCE_TYPE:                  ORGANIZACAO
URL:                          https://www.cifo.it/
ACCESS_METHOD:                HTML
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       nutrizione vegetale
GEOGRAPHIC_GRANULARITY:       REGIÃO — EMILIA-ROMAGNA
UPDATE_FREQUENCY:             observada por data visível na página: 2026-09-14
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   SIM — 2026-09-14
RAW_EVIDENCE_PRESERVABLE:     SIM — HTML obtido por HTTP
AUTOMATION_FEASIBILITY:       ALTA — rota estruturada declarada (API/opendata)
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Newsroom - Cifo» https://www.cifo.it/newsroom/ — HTML, 39244 bytes lidos em
                              2026-09-14
ADAMA_USE_CASE:               concorrente / industria de protecao e nutricao; alimenta T9 (concorrentes),
                              T10 (mercado e industria)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T9-009/MANIFEST.json
VERDICT:                      GREEN — fonte aberta, exemplo real observado e preservado
```

#### IT-T9-010 · Serbios

```
SOURCE_ID:                    IT-T9-010
SOURCE_NAME:                  Serbios
SOURCE_OWNER:                 Serbios
COUNTRY:                      ITALY
REGION:                       VENETO
LANGUAGE:                     IT
TERRITORY:                    T9 (também serve T3)
SOURCE_TYPE:                  ORGANIZACAO
URL:                          https://www.serbios.it/
ACCESS_METHOD:                PDF ligado a partir da página da fonte
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       biocontrollo;fitosanitari
GEOGRAPHIC_GRANULARITY:       REGIÃO — VENETO
UPDATE_FREQUENCY:             NÃO SEI — nenhuma data de publicação legível na página
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   NÃO SEI — nenhuma data legível no item observado
RAW_EVIDENCE_PRESERVABLE:     SIM — PDF obtido por HTTP
AUTOMATION_FEASIBILITY:       ALTA — rota estruturada declarada (API/opendata)
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 NÃO REPRESENTATIVO — o item que se conseguiu confirmar por HTTP e' papelada administrativa (codigo etico, termos, formulario) — prova que a organizacao existe, NAO prova o que ela publica na sua area tecnica. Um exemplo representativo exige navegador ou leitura humana da seccao de noticias.
ADAMA_USE_CASE:               concorrente / industria de protecao e nutricao; alimenta T9 (concorrentes),
                              T3 (praga, doenca e infestantes)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T9-010/MANIFEST.json
VERDICT:                      YELLOW — registada como real e util, mas sem exemplo representativo do que entrega; rever com navegador antes de contratar coleta.
```

#### IT-T9-011 · Koppert Italia

```
SOURCE_ID:                    IT-T9-011
SOURCE_NAME:                  Koppert Italia
SOURCE_OWNER:                 Koppert Biological Systems
COUNTRY:                      ITALY
REGION:                       NAZIONALE (sem recorte regional)
LANGUAGE:                     IT
TERRITORY:                    T9 (também serve T3)
SOURCE_TYPE:                  ORGANIZACAO
URL:                          https://www.koppert.it/
ACCESS_METHOD:                HTML
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       biocontrollo;insetti utili
GEOGRAPHIC_GRANULARITY:       PAÍS — a fonte publica com alcance nacional
UPDATE_FREQUENCY:             NÃO SEI — nenhuma data de publicação legível na página
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   NÃO SEI — nenhuma data legível no item observado
RAW_EVIDENCE_PRESERVABLE:     SIM — HTML obtido por HTTP
AUTOMATION_FEASIBILITY:       MÉDIA-ALTA — feed ou ficheiro previsível
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Newsletter Koppert - Ricevere aggiornamenti sulla protezione delle colture
                              e l'impollinazione» https://www.koppert.it/notizie-eventi/newsletter/ —
                              HTML, 115080 bytes lidos em 2026-09-14
ADAMA_USE_CASE:               concorrente / industria de protecao e nutricao; alimenta T9 (concorrentes),
                              T3 (praga, doenca e infestantes)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T9-011/MANIFEST.json
VERDICT:                      YELLOW — frequencia de atualizacao por provar
```

#### IT-T9-012 · CBC Biogard

```
SOURCE_ID:                    IT-T9-012
SOURCE_NAME:                  CBC Biogard
SOURCE_OWNER:                 CBC Europe — Biogard
COUNTRY:                      ITALY
REGION:                       LOMBARDIA
LANGUAGE:                     IT-IT
TERRITORY:                    T9 (também serve T3)
SOURCE_TYPE:                  ORGANIZACAO
URL:                          https://www.biogard.it/
ACCESS_METHOD:                PDF ligado a partir da página da fonte
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       biocontrollo;difesa biologica
GEOGRAPHIC_GRANULARITY:       REGIÃO — LOMBARDIA
UPDATE_FREQUENCY:             NÃO SEI
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   NÃO SEI — nenhuma data legível no item observado
RAW_EVIDENCE_PRESERVABLE:     SIM — PDF obtido por HTTP
AUTOMATION_FEASIBILITY:       ALTA — rota estruturada declarada (API/opendata)
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «CURVE DI SCARICO E DI RILASCIO DEI DIFFUSORI SHIN-ETSUscarica il report»
                              https://www.biogard.it/wp-content/uploads/2026/08/Report-Curve_30.07.26.pdf
                              — PDF, 704512 bytes lidos em 2026-09-14
ADAMA_USE_CASE:               concorrente / industria de protecao e nutricao; alimenta T9 (concorrentes),
                              T3 (praga, doenca e infestantes)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T9-012/MANIFEST.json
VERDICT:                      GREEN — fonte aberta, exemplo real observado e preservado
```

#### IT-T9-013 · Certis Belchim Italia

```
SOURCE_ID:                    IT-T9-013
SOURCE_NAME:                  Certis Belchim Italia
SOURCE_OWNER:                 Certis Belchim
COUNTRY:                      ITALY
REGION:                       NAZIONALE (sem recorte regional)
LANGUAGE:                     EN-US
TERRITORY:                    T9 (também serve T10)
SOURCE_TYPE:                  ORGANIZACAO
URL:                          https://www.certisbelchim.it/
ACCESS_METHOD:                PDF ligado a partir da página da fonte
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       agrofarmaci;concorrente
GEOGRAPHIC_GRANULARITY:       PAÍS — a fonte publica com alcance nacional
UPDATE_FREQUENCY:             NÃO SEI
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   NÃO SEI — nenhuma data legível no item observado
RAW_EVIDENCE_PRESERVABLE:     SIM — PDF obtido por HTTP
AUTOMATION_FEASIBILITY:       ALTA — rota estruturada declarada (API/opendata)
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 NÃO REPRESENTATIVO — o item que se conseguiu confirmar por HTTP e' papelada administrativa (codigo etico, termos, formulario) — prova que a organizacao existe, NAO prova o que ela publica na sua area tecnica. Um exemplo representativo exige navegador ou leitura humana da seccao de noticias.
ADAMA_USE_CASE:               concorrente / industria de protecao e nutricao; alimenta T9 (concorrentes),
                              T10 (mercado e industria)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T9-013/MANIFEST.json
VERDICT:                      YELLOW — registada como real e util, mas sem exemplo representativo do que entrega; rever com navegador antes de contratar coleta.
```

### T10 · MARKET / TRADE / INDUSTRY — ITALY · onda 1 (2026-09-14)

*11 fontes registradas nesta secção. Cada uma foi aberta, observada e tem exemplo real preservado em `data/samples/IT-SOURCE-SAMPLES/<SOURCE_ID>/`. Registada ≠ contratada: nenhuma tem contrato de busca, e nenhuma coleta foi corrida.*

#### IT-T10-006 · Agrisole — quotidiano agricolo del Sole 24 Ore

```
SOURCE_ID:                    IT-T10-006
SOURCE_NAME:                  Agrisole — quotidiano agricolo del Sole 24 Ore
SOURCE_OWNER:                 Il Sole 24 Ore
COUNTRY:                      ITALY
REGION:                       NAZIONALE (sem recorte regional)
LANGUAGE:                     IT
TERRITORY:                    T10 (também serve T12)
SOURCE_TYPE:                  IMPRENSA
URL:                          https://www.agrisole.ilsole24ore.com/
ACCESS_METHOD:                HTML
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       economia agricola;mercati;policy
GEOGRAPHIC_GRANULARITY:       PAÍS — a fonte publica com alcance nacional
UPDATE_FREQUENCY:             observada por data visível na página: 2026-09-14
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   NÃO SEI — nenhuma data legível no item observado
RAW_EVIDENCE_PRESERVABLE:     SIM — HTML obtido por HTTP
AUTOMATION_FEASIBILITY:       MÉDIA — site navegável, sem rota estruturada declarada
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «My24 - Il Sole 24 ORE» https://areautente.ilsole24ore.com/ — HTML, 118331
                              bytes lidos em 2026-09-14
ADAMA_USE_CASE:               agencia regional agricola; alimenta T10 (mercado e industria), T12 (politica
                              e ambiente agricola)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T10-006/MANIFEST.json
VERDICT:                      GREEN — fonte aberta, exemplo real observado e preservado
```

#### IT-T10-007 · ISMEA — Istituto di Servizi per il Mercato Agricolo Alimentare

```
SOURCE_ID:                    IT-T10-007
SOURCE_NAME:                  ISMEA — Istituto di Servizi per il Mercato Agricolo Alimentare
SOURCE_OWNER:                 ISMEA
COUNTRY:                      ITALY
REGION:                       NAZIONALE (sem recorte regional)
LANGUAGE:                     IT
TERRITORY:                    T10 (também serve T12)
SOURCE_TYPE:                  BASE_OFICIAL
URL:                          https://www.ismea.it/istituto-di-servizi-per-il-mercato-agricolo-alimentare
ACCESS_METHOD:                HTML
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       mercati;credito;filiere
GEOGRAPHIC_GRANULARITY:       PAÍS — a fonte publica com alcance nacional
UPDATE_FREQUENCY:             observada por data visível na página: 2026-09-11
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   SIM — 2026-09-11
RAW_EVIDENCE_PRESERVABLE:     SIM — HTML obtido por HTTP
AUTOMATION_FEASIBILITY:       MÉDIA — site navegável, sem rota estruturada declarada
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Comunicati stampa e news - Ismea» https://www.ismea.it/Press-
                              Area/Comunicati-Stampa — HTML, 102783 bytes lidos em 2026-09-14
ADAMA_USE_CASE:               ente de filiera / mercado oficial; alimenta T10 (mercado e industria), T12
                              (politica e ambiente agricola)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T10-007/MANIFEST.json
VERDICT:                      GREEN — fonte aberta, exemplo real observado e preservado
```

#### IT-T10-008 · Italmopa — Associazione Industriali Mugnai d'Italia

```
SOURCE_ID:                    IT-T10-008
SOURCE_NAME:                  Italmopa — Associazione Industriali Mugnai d'Italia
SOURCE_OWNER:                 Italmopa
COUNTRY:                      ITALY
REGION:                       NAZIONALE (sem recorte regional)
LANGUAGE:                     IT-IT
TERRITORY:                    T10 (também serve T1)
SOURCE_TYPE:                  ORGANIZACAO
URL:                          https://www.italmopa.com/
ACCESS_METHOD:                HTML
CROPS:                        grano
TOPICS:                       grano;molini;mercato
GEOGRAPHIC_GRANULARITY:       PAÍS — a fonte publica com alcance nacional
UPDATE_FREQUENCY:             NÃO SEI
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   NÃO SEI — nenhuma data legível no item observado
RAW_EVIDENCE_PRESERVABLE:     SIM — HTML obtido por HTTP
AUTOMATION_FEASIBILITY:       ALTA — rota estruturada declarada (API/opendata)
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Pubblicazioni - Italmopa» https://italmopa.com/pubblicazioni/ — HTML,
                              104454 bytes lidos em 2026-09-14
ADAMA_USE_CASE:               ente de filiera / mercado oficial; alimenta T10 (mercado e industria), T1
                              (cultura e producao)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T10-008/MANIFEST.json
VERDICT:                      GREEN — fonte aberta, exemplo real observado e preservado
```

#### IT-T10-009 · Borsa Merci Bologna — Camera di Commercio

```
SOURCE_ID:                    IT-T10-009
SOURCE_NAME:                  Borsa Merci Bologna — Camera di Commercio
SOURCE_OWNER:                 Camera di Commercio di Bologna
COUNTRY:                      ITALY
REGION:                       EMILIA-ROMAGNA
LANGUAGE:                     IT
TERRITORY:                    T10
SOURCE_TYPE:                  BASE_OFICIAL
URL:                          https://www.bo.camcom.gov.it/
ACCESS_METHOD:                HTML
CROPS:                        cereali
TOPICS:                       prezzi;cereali;borsa merci
GEOGRAPHIC_GRANULARITY:       REGIÃO — EMILIA-ROMAGNA
UPDATE_FREQUENCY:             observada por data visível na página: 2025-12-31
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   NÃO SEI — nenhuma data legível no item observado
RAW_EVIDENCE_PRESERVABLE:     SIM — HTML obtido por HTTP
AUTOMATION_FEASIBILITY:       MÉDIA — site navegável, sem rota estruturada declarada
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Sicurezza e Etichettatura dei Prodotti | Camera di Commercio di Bologna»
                              https://www.bo.camcom.gov.it/it/servizio-ispettivo/home — HTML, 55090 bytes
                              lidos em 2026-09-14
ADAMA_USE_CASE:               ente de filiera / mercado oficial; alimenta T10 (mercado e industria)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T10-009/MANIFEST.json
VERDICT:                      GREEN — fonte aberta, exemplo real observado e preservado
```

#### IT-T10-010 · CSO Italy — Centro Servizi Ortofrutticoli

```
SOURCE_ID:                    IT-T10-010
SOURCE_NAME:                  CSO Italy — Centro Servizi Ortofrutticoli
SOURCE_OWNER:                 CSO Italy
COUNTRY:                      ITALY
REGION:                       EMILIA-ROMAGNA
LANGUAGE:                     IT-IT
TERRITORY:                    T10 (também serve T1)
SOURCE_TYPE:                  ORGANIZACAO
URL:                          https://www.csoservizi.com/
ACCESS_METHOD:                PDF ligado a partir da página da fonte
CROPS:                        ortofrutta
TOPICS:                       ortofrutta;mercato;dati
GEOGRAPHIC_GRANULARITY:       REGIÃO — EMILIA-ROMAGNA
UPDATE_FREQUENCY:             observada por data visível na página: 2023-12-22
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   NÃO SEI — nenhuma data legível no item observado
RAW_EVIDENCE_PRESERVABLE:     SIM — PDF obtido por HTTP
AUTOMATION_FEASIBILITY:       ALTA — rota estruturada declarada (API/opendata)
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «CLICCARE QUI» https://www.csoservizi.com/wp-
                              content/uploads/2025/03/AGRIPAT_SCH_SINTESI_INIZIALE_DEF.pdf — PDF, 496652
                              bytes lidos em 2026-09-14
ADAMA_USE_CASE:               ente de filiera / mercado oficial; alimenta T10 (mercado e industria), T1
                              (cultura e producao)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T10-010/MANIFEST.json
VERDICT:                      GREEN — fonte aberta, exemplo real observado e preservado
```

#### IT-T10-011 · Ruminantia — web magazine dei ruminanti

```
SOURCE_ID:                    IT-T10-011
SOURCE_NAME:                  Ruminantia — web magazine dei ruminanti
SOURCE_OWNER:                 Ruminantia
COUNTRY:                      ITALY
REGION:                       NAZIONALE (sem recorte regional)
LANGUAGE:                     IT-IT
TERRITORY:                    T10 (também serve T1, T7)
SOURCE_TYPE:                  IMPRENSA
URL:                          https://www.ruminantia.it/
ACCESS_METHOD:                HTML
CROPS:                        latte
TOPICS:                       bovini;latte;zootecnia
GEOGRAPHIC_GRANULARITY:       PAÍS — a fonte publica com alcance nacional
UPDATE_FREQUENCY:             NÃO SEI
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   NÃO SEI — nenhuma data legível no item observado
RAW_EVIDENCE_PRESERVABLE:     SIM — HTML obtido por HTTP
AUTOMATION_FEASIBILITY:       ALTA — rota estruturada declarada (API/opendata)
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «News &#8211; Ruminantia &#8211; Web Magazine del mondo dei Ruminanti»
                              https://www.ruminantia.it/category/news/ — HTML, 144696 bytes lidos em
                              2026-09-14
ADAMA_USE_CASE:               imprensa tecnica agricola; alimenta T10 (mercado e industria), T1 (cultura e
                              producao), T7 (rede tecnica)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T10-011/MANIFEST.json
VERDICT:                      GREEN — fonte aberta, exemplo real observado e preservado
```

#### IT-T10-012 · Consorzio Tutela Vini d'Abruzzo

```
SOURCE_ID:                    IT-T10-012
SOURCE_NAME:                  Consorzio Tutela Vini d'Abruzzo
SOURCE_OWNER:                 Consorzio Tutela Vini d'Abruzzo
COUNTRY:                      ITALY
REGION:                       ABRUZZO
LANGUAGE:                     IT-IT
TERRITORY:                    T10 (também serve T1)
SOURCE_TYPE:                  ORGANIZACAO
URL:                          https://www.vinidabruzzo.it/
ACCESS_METHOD:                PDF ligado a partir da página da fonte
CROPS:                        vino
TOPICS:                       vino;DOC
GEOGRAPHIC_GRANULARITY:       REGIÃO — ABRUZZO
UPDATE_FREQUENCY:             observada por data visível na página: 2026-09-01
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   NÃO SEI — nenhuma data legível no item observado
RAW_EVIDENCE_PRESERVABLE:     SIM — PDF obtido por HTTP
AUTOMATION_FEASIBILITY:       ALTA — rota estruturada declarada (API/opendata)
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Press                                  La nuova terra dei Winelovers
                              Scarica PDF» https://www.vinidabruzzo.it/wp-content/uploads/2024/04/QN-
                              ITINERARI-1.pdf — PDF, 704512 bytes lidos em 2026-09-14
ADAMA_USE_CASE:               consorcio de tutela / bonifica; alimenta T10 (mercado e industria), T1
                              (cultura e producao)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T10-012/MANIFEST.json
VERDICT:                      GREEN — fonte aberta, exemplo real observado e preservado
```

#### IT-T10-013 · Consorzio di Tutela Arancia Rossa di Sicilia IGP

```
SOURCE_ID:                    IT-T10-013
SOURCE_NAME:                  Consorzio di Tutela Arancia Rossa di Sicilia IGP
SOURCE_OWNER:                 Consorzio Arancia Rossa di Sicilia
COUNTRY:                      ITALY
REGION:                       SICILIA
LANGUAGE:                     IT-IT
TERRITORY:                    T10 (também serve T1)
SOURCE_TYPE:                  ORGANIZACAO
URL:                          https://www.tutelaaranciarossa.it/
ACCESS_METHOD:                HTML
CROPS:                        agrumi
TOPICS:                       agrumi;IGP
GEOGRAPHIC_GRANULARITY:       REGIÃO — SICILIA
UPDATE_FREQUENCY:             observada por data visível na página: 2026-09-14
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   SIM — 2026-09-14
RAW_EVIDENCE_PRESERVABLE:     SIM — HTML obtido por HTTP
AUTOMATION_FEASIBILITY:       ALTA — rota estruturada declarada (API/opendata)
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Rassegna stampa - Tutela Arancia Rossa di Sicilia IGP»
                              https://www.tutelaaranciarossa.it/rassegna-stampa/ — HTML, 81643 bytes lidos
                              em 2026-09-14
ADAMA_USE_CASE:               consorcio de tutela / bonifica; alimenta T10 (mercado e industria), T1
                              (cultura e producao)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T10-013/MANIFEST.json
VERDICT:                      GREEN — fonte aberta, exemplo real observado e preservado
```

#### IT-T10-014 · Consorzio di Tutela del Grana Padano

```
SOURCE_ID:                    IT-T10-014
SOURCE_NAME:                  Consorzio di Tutela del Grana Padano
SOURCE_OWNER:                 Consorzio Tutela Grana Padano
COUNTRY:                      ITALY
REGION:                       LOMBARDIA
LANGUAGE:                     IT
TERRITORY:                    T10 (também serve T1)
SOURCE_TYPE:                  ORGANIZACAO
URL:                          https://www.granapadano.it/it-it/
ACCESS_METHOD:                HTML
CROPS:                        latte
TOPICS:                       DOP;latte;filiera
GEOGRAPHIC_GRANULARITY:       REGIÃO — LOMBARDIA
UPDATE_FREQUENCY:             observada por data visível na página: 2026-09-11
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   SIM — 2026-09-11
RAW_EVIDENCE_PRESERVABLE:     SIM — HTML obtido por HTTP
AUTOMATION_FEASIBILITY:       ALTA — rota estruturada declarada (API/opendata)
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Progetti Finanziati - Grana Padano» https://www.granapadano.it/it-it/il-
                              mondo-di-grana-padano/partnership-e-
                              sponsorizzazioni/sponsorizzazioni/progetti-finanziati/ — HTML, 154883 bytes
                              lidos em 2026-09-14
ADAMA_USE_CASE:               consorcio de tutela / bonifica; alimenta T10 (mercado e industria), T1
                              (cultura e producao)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T10-014/MANIFEST.json
VERDICT:                      GREEN — fonte aberta, exemplo real observado e preservado
```

#### IT-T10-015 · Consorzio Tutela Prosecco DOC

```
SOURCE_ID:                    IT-T10-015
SOURCE_NAME:                  Consorzio Tutela Prosecco DOC
SOURCE_OWNER:                 Consorzio Tutela Prosecco DOC
COUNTRY:                      ITALY
REGION:                       VENETO
LANGUAGE:                     IT-IT
TERRITORY:                    T10 (também serve T1)
SOURCE_TYPE:                  ORGANIZACAO
URL:                          https://www.prosecco.it/it/
ACCESS_METHOD:                PDF ligado a partir da página da fonte
CROPS:                        vino
TOPICS:                       vino;DOC;viticoltura
GEOGRAPHIC_GRANULARITY:       REGIÃO — VENETO
UPDATE_FREQUENCY:             NÃO SEI — nenhuma data de publicação legível na página
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   NÃO SEI — nenhuma data legível no item observado
RAW_EVIDENCE_PRESERVABLE:     SIM — PDF obtido por HTTP
AUTOMATION_FEASIBILITY:       ALTA — rota estruturada declarada (API/opendata)
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 https://www.prosecco.it/wp-content/uploads/2023/07/Pagina-per-sito-web.pdf —
                              PDF, 704512 bytes lidos em 2026-09-14
ADAMA_USE_CASE:               consorcio de tutela / bonifica; alimenta T10 (mercado e industria), T1
                              (cultura e producao)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T10-015/MANIFEST.json
VERDICT:                      YELLOW — frequencia de atualizacao por provar
```

#### IT-T10-016 · Alleanza delle Cooperative Italiane Agroalimentare

```
SOURCE_ID:                    IT-T10-016
SOURCE_NAME:                  Alleanza delle Cooperative Italiane Agroalimentare
SOURCE_OWNER:                 Alleanza Cooperative
COUNTRY:                      ITALY
REGION:                       NAZIONALE (sem recorte regional)
LANGUAGE:                     IT
TERRITORY:                    T10 (também serve T12)
SOURCE_TYPE:                  ORGANIZACAO
URL:                          https://www.alleanzacooperative.it/
ACCESS_METHOD:                HTML
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       cooperative
GEOGRAPHIC_GRANULARITY:       PAÍS — a fonte publica com alcance nacional
UPDATE_FREQUENCY:             NÃO SEI
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   NÃO SEI — nenhuma data legível no item observado
RAW_EVIDENCE_PRESERVABLE:     SIM — HTML obtido por HTTP
AUTOMATION_FEASIBILITY:       ALTA — rota estruturada declarada (API/opendata)
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Alleanza Cooperative Italiane» https://www.alleanzacooperative.it/news-
                              eventi — HTML, 38843 bytes lidos em 2026-09-14
ADAMA_USE_CASE:               organizacao agricola / representacao de produtores; alimenta T10 (mercado e
                              industria), T12 (politica e ambiente agricola)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T10-016/MANIFEST.json
VERDICT:                      GREEN — fonte aberta, exemplo real observado e preservado
```

### T11 · EVENTS — ITALY · onda 1 (2026-09-14)

*1 fontes registradas nesta secção. Cada uma foi aberta, observada e tem exemplo real preservado em `data/samples/IT-SOURCE-SAMPLES/<SOURCE_ID>/`. Registada ≠ contratada: nenhuma tem contrato de busca, e nenhuma coleta foi corrida.*

#### IT-T11-005 · SIMEI — Salone Internazionale Macchine per Enologia e Imbottigliamento

```
SOURCE_ID:                    IT-T11-005
SOURCE_NAME:                  SIMEI — Salone Internazionale Macchine per Enologia e Imbottigliamento
SOURCE_OWNER:                 Unione Italiana Vini
COUNTRY:                      ITALY
REGION:                       NAZIONALE (sem recorte regional)
LANGUAGE:                     IT
TERRITORY:                    T11 (também serve T10)
SOURCE_TYPE:                  ORGANIZACAO
URL:                          https://www.simei.it/
ACCESS_METHOD:                HTML
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       fiera enologia
GEOGRAPHIC_GRANULARITY:       PAÍS — a fonte publica com alcance nacional
UPDATE_FREQUENCY:             observada por data visível na página: 2024-09-16
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   NÃO SEI — nenhuma data legível no item observado
RAW_EVIDENCE_PRESERVABLE:     SIM — HTML obtido por HTTP
AUTOMATION_FEASIBILITY:       MÉDIA-ALTA — feed ou ficheiro previsível
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Distillo 2026 - SIMEI» https://www.simei.it/news-media/news/distillo-2026 —
                              HTML, 30177 bytes lidos em 2026-09-14
ADAMA_USE_CASE:               ente de filiera / mercado oficial; alimenta T11 (eventos), T10 (mercado e
                              industria)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T11-005/MANIFEST.json
VERDICT:                      GREEN — fonte aberta, exemplo real observado e preservado
```

### T12 · POLICY / AGRICULTURAL ENVIRONMENT — ITALY · onda 1 (2026-09-14)

*4 fontes registradas nesta secção. Cada uma foi aberta, observada e tem exemplo real preservado em `data/samples/IT-SOURCE-SAMPLES/<SOURCE_ID>/`. Registada ≠ contratada: nenhuma tem contrato de busca, e nenhuma coleta foi corrida.*

#### IT-T12-003 · CIA — Agricoltori Italiani

```
SOURCE_ID:                    IT-T12-003
SOURCE_NAME:                  CIA — Agricoltori Italiani
SOURCE_OWNER:                 CIA
COUNTRY:                      ITALY
REGION:                       NAZIONALE (sem recorte regional)
LANGUAGE:                     IT
TERRITORY:                    T12 (também serve T7)
SOURCE_TYPE:                  ORGANIZACAO
URL:                          https://www.cia.it/
ACCESS_METHOD:                PDF ligado a partir da página da fonte
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       organizzazione agricola;policy
GEOGRAPHIC_GRANULARITY:       PAÍS — a fonte publica com alcance nacional
UPDATE_FREQUENCY:             NÃO SEI — nenhuma data de publicação legível na página
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   NÃO SEI — nenhuma data legível no item observado
RAW_EVIDENCE_PRESERVABLE:     SIM — PDF obtido por HTTP
AUTOMATION_FEASIBILITY:       MÉDIA-ALTA — feed ou ficheiro previsível
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 NÃO REPRESENTATIVO — o item que se conseguiu confirmar por HTTP e' papelada administrativa (codigo etico, termos, formulario) — prova que a organizacao existe, NAO prova o que ela publica na sua area tecnica. Um exemplo representativo exige navegador ou leitura humana da seccao de noticias.
ADAMA_USE_CASE:               organizacao agricola / representacao de produtores; alimenta T12 (politica e
                              ambiente agricola), T7 (rede tecnica)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T12-003/MANIFEST.json
VERDICT:                      YELLOW — registada como real e util, mas sem exemplo representativo do que entrega; rever com navegador antes de contratar coleta.
```

#### IT-T12-004 · Confagricoltura

```
SOURCE_ID:                    IT-T12-004
SOURCE_NAME:                  Confagricoltura
SOURCE_OWNER:                 Confagricoltura
COUNTRY:                      ITALY
REGION:                       NAZIONALE (sem recorte regional)
LANGUAGE:                     IT
TERRITORY:                    T12 (também serve T7, T10)
SOURCE_TYPE:                  ORGANIZACAO
URL:                          https://www.confagricoltura.it/ita/
ACCESS_METHOD:                HTML
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       organizzazione agricola;policy
GEOGRAPHIC_GRANULARITY:       PAÍS — a fonte publica com alcance nacional
UPDATE_FREQUENCY:             NÃO SEI — nenhuma data de publicação legível na página
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   SIM — 2026-06-04
RAW_EVIDENCE_PRESERVABLE:     SIM — HTML obtido por HTTP
AUTOMATION_FEASIBILITY:       MÉDIA-ALTA — feed ou ficheiro previsível
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «AgriFoodTech e IA: 2° Rapporto 2026 dedicato alla trasformazione
                              tecnologica dell'agroalimentare Made in Italy - Notizie Brevi |
                              Confagricoltura» https://www.confagricoltura.it/ita/area-stampa/notizie-
                              brevi/agrifoodtech-e-ia-presentato-il-2%C2%B0-rapporto-2026-dedicato-alla-
                              trasformazione-tecnologica-dell-agroalimentare-made-in-italy — HTML, 85962
                              bytes lidos em 2026-09-14
ADAMA_USE_CASE:               organizacao agricola / representacao de produtores; alimenta T12 (politica e
                              ambiente agricola), T7 (rede tecnica), T10 (mercado e industria)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T12-004/MANIFEST.json
VERDICT:                      YELLOW — frequencia de atualizacao por provar
```

#### IT-T12-005 · AIAB — Associazione Italiana Agricoltura Biologica

```
SOURCE_ID:                    IT-T12-005
SOURCE_NAME:                  AIAB — Associazione Italiana Agricoltura Biologica
SOURCE_OWNER:                 AIAB
COUNTRY:                      ITALY
REGION:                       NAZIONALE (sem recorte regional)
LANGUAGE:                     IT-IT
TERRITORY:                    T12 (também serve T1)
SOURCE_TYPE:                  ORGANIZACAO
URL:                          https://aiab.it/
ACCESS_METHOD:                PDF ligado a partir da página da fonte
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       biologico;agroecologia
GEOGRAPHIC_GRANULARITY:       PAÍS — a fonte publica com alcance nacional
UPDATE_FREQUENCY:             observada por data visível na página: 2026-05-15
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   NÃO SEI — nenhuma data legível no item observado
RAW_EVIDENCE_PRESERVABLE:     SIM — PDF obtido por HTTP
AUTOMATION_FEASIBILITY:       ALTA — rota estruturada declarada (API/opendata)
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 «Aiuti di Stato» https://aiab.it/wp-content/uploads/2023/01/AIAB-Aiuti-di-
                              Stato.pdf — PDF, 103612 bytes lidos em 2026-09-14
ADAMA_USE_CASE:               organizacao agricola / representacao de produtores; alimenta T12 (politica e
                              ambiente agricola), T1 (cultura e producao)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T12-005/MANIFEST.json
VERDICT:                      GREEN — fonte aberta, exemplo real observado e preservado
```

#### IT-T12-006 · CIA Toscana

```
SOURCE_ID:                    IT-T12-006
SOURCE_NAME:                  CIA Toscana
SOURCE_OWNER:                 CIA Agricoltori Italiani
COUNTRY:                      ITALY
REGION:                       TOSCANA
LANGUAGE:                     IT-IT
TERRITORY:                    T12 (também serve T7)
SOURCE_TYPE:                  ORGANIZACAO
URL:                          https://www.ciatoscana.eu/home/
ACCESS_METHOD:                PDF ligado a partir da página da fonte
CROPS:                        NÃO SEI — a fonte não declara cultura nesta camada
TOPICS:                       organizzazione agricola regionale
GEOGRAPHIC_GRANULARITY:       REGIÃO — TOSCANA
UPDATE_FREQUENCY:             observada por data visível na página: 2026-09-14
HISTORICAL_DEPTH:             NÃO SEI — não foi medido nesta missão (registar ≠ coletar)
SOURCE_IDENTITY_PRESERVABLE:  SIM — URL canónica estável
DOCUMENT_ID_AVAILABLE:        NÃO SEI — o item observado não expõe identificador próprio
PUBLICATION_DATE_AVAILABLE:   NÃO SEI — nenhuma data legível no item observado
RAW_EVIDENCE_PRESERVABLE:     SIM — PDF obtido por HTTP
AUTOMATION_FEASIBILITY:       ALTA — rota estruturada declarada (API/opendata)
COLLECTION_FEASIBILITY:       ALTA — o exemplo real foi obtido por HTTP simples nesta missão
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação foi
                              tentada e nenhum paywall foi contornado.
REAL_EXAMPLE:                 https://www.ciatoscana.eu/home/wp-content/uploads/2026/02/inn-
                              pratica_volume_il-futuro-dell-agricoltura_IT_web.pdf — PDF, 704512 bytes
                              lidos em 2026-09-14
ADAMA_USE_CASE:               organizacao agricola / representacao de produtores; alimenta T12 (politica e
                              ambiente agricola), T7 (rede tecnica)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T12-006/MANIFEST.json
VERDICT:                      GREEN — fonte aberta, exemplo real observado e preservado
```

---

### RECONCILIAÇÃO — prova guardada que o atlas não mostrava (2026-09-15)

*13 fontes italianas cujo `SOURCE_ID` já estava emitido em
`candidatas/ITALY-SOURCE-MASTER-V1.json`, cuja prova bruta já estava preservada em
`data/samples/IT-SOURCE-SAMPLES/<SOURCE_ID>/`, e que **nenhuma ficha deste atlas mostrava**.
Nenhum `SOURCE_ID` foi emitido aqui: os treze já existiam. Nenhuma coleta correu nesta
missão — o `SHA256` de cada um dos 23 ficheiros foi **reconferido contra os bytes em disco**
em 2026-09-15, e os 23 conferem.*

> **Porque isto é um defeito, e não uma arrumação.** Este atlas já avisa, na convenção de
> `SOURCE_ID`, que um número que desaparece daqui é um número que alguém volta a emitir «sem
> que nada acuse». Enquanto estas treze não tinham ficha, quem contava fontes pelo atlas
> contava treze a menos e quem contava pela pasta de provas contava treze a mais — duas
> contagens certas, para a mesma casa, e uma casa que não sabia o que tinha.

**Onze são GREEN e duas são YELLOW, e a diferença está na prova, não no gosto:** as onze
guardam os bytes que o próprio site serviu; as duas de T9 guardam um **extrato do DOM lido
por navegador**, e o manifesto delas declara, por escrito, que não são os bytes servidos.
Os sites da Bayer Italia e da ADAMA Italia devolvem 403 a `curl` do mesmo IP italiano.

⚠️ **Todas as capturas saíram por VPN comercial italiana (Proton AG, Milano).** Não foi
medido como cada fonte responde a partir de um IP não italiano. Está escrito em cada ficha.

Gerador e verificador: `candidatas/reconciliar_fichas_orfas.py`.

#### IT-T2-001 · ARPAE — Bollettino agrometeorologico regionale

```
SOURCE_ID:                    IT-T2-001
SOURCE_NAME:                  ARPAE — Bollettino agrometeorologico regionale
SOURCE_OWNER:                 ARPAE Emilia-Romagna (IT-OWN-002)
COUNTRY:                      ITALY
REGION:                       Emilia-Romagna
LANGUAGE:                     IT
TERRITORY:                    T2
SOURCE_TYPE:                  boletim agrometeorológico
URL:                          https://www.arpae.it/it/temi-ambientali/meteo/agrometeo
ACCESS_METHOD:                PDF
CROPS:                        transversal
TOPICS:                       precipitação, temperatura, água no solo, agroclima
GEOGRAPHIC_GRANULARITY:       NÃO SEI (esperado: região/zona)
UPDATE_FREQUENCY:             NÃO SEI
HISTORICAL_DEPTH:             NÃO SEI
SOURCE_IDENTITY_PRESERVABLE:  SIM — 2 de 2 ficheiro(s) com SHA256 reconferido em 2026-09-15
DOCUMENT_ID_AVAILABLE:        SIM — o documento traz título e numeração próprios
PUBLICATION_DATE_AVAILABLE:   SIM — 31-08-2026 (boletim n. 35) e 24-08-2026 (n. 34)
RAW_EVIDENCE_PRESERVABLE:     SIM — já preservada:
                              data/samples/IT-SOURCE-SAMPLES/IT-T2-001/MANIFEST.json
AUTOMATION_FEASIBILITY:       NÃO SEI — nenhuma rota foi contratada. O manifesto guarda o endereço
                              exato que trouxe cada ficheiro, o que é o ponto de partida de um
                              contrato.
COLLECTION_FEASIBILITY:       NÃO SEI — registar ≠ coletar; nenhuma coleta correu
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação
                              foi tentada (AUTH_USED: NENHUMA. Nao se tentou contornar
                              autenticacao.) e nenhum paywall foi contornado. ⚠️ A captura saiu
                              por VPN_COMERCIAL — nao e ISP residencial italiano (Milano,
                              Lombardia, IT — AS208172 Proton AG): a fonte pode responder de outro
                              modo a partir de um IP não italiano, e isso não foi medido.
REAL_EXAMPLE:                 «Bollettino agrometeorologico n. 35 / n. 34 del 2026»
                              https://www.arpae.it/it/temi-ambientali/meteo/report-meteo/bollettini-e-rapporti-agrometeo/bollettini-agrometeo/bollettini-2026/35_boll_agro_20260831.pdf
                              — application/pdf, 1787024 bytes, SHA256 conferido em 2026-09-07
SOURCE_LOCATION:              Bologna — sede da ARPAE
FACT_LOCATION:                Emilia-Romagna (regional). DIFERENTE da sede.
WHAT_IT_PROVES:               que existe boletim agrometeorologico regional numerado e semanal, em
                              PDF aberto, com arquivo por ano desde pelo menos 2021
WHAT_IT_DOES_NOT_PROVE:       presenca de praga · ocorrencia fitossanitaria · risco modelado de
                              praga · decisao de tratamento · dado por talhao. AGROCLIMATIC_SIGNAL
                              nunca vira PEST_OCCURRENCE.
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T2-001/MANIFEST.json
VERDICT:                      GREEN — fonte aberta, ficheiro bruto servido pelo site preservado e
                              SHA256 reconferido nesta missão
```

#### IT-T2-002 · ARPAV — Agrometeo / Agrometeo Informa / bollettini zonali

```
SOURCE_ID:                    IT-T2-002
SOURCE_NAME:                  ARPAV — Agrometeo / Agrometeo Informa / bollettini zonali
SOURCE_OWNER:                 ARPAV — Agenzia Regionale per la Prevenzione e Protezione Ambientale
                              del Veneto (IT-OWN-003)
COUNTRY:                      ITALY
REGION:                       Veneto
LANGUAGE:                     IT
TERRITORY:                    T2
SOURCE_TYPE:                  boletim agrometeorológico zonal
URL:                          https://www.arpa.veneto.it/dati-ambientali/bollettini/agrometeo
ACCESS_METHOD:                PDF
CROPS:                        transversal, com recortes por cultura nos bollettini zonali
TOPICS:                       chuva, temperatura, evapotranspiração, alerta agroclimático
GEOGRAPHIC_GRANULARITY:       NÃO SEI (esperado: zona)
UPDATE_FREQUENCY:             NÃO SEI
HISTORICAL_DEPTH:             NÃO SEI
SOURCE_IDENTITY_PRESERVABLE:  SIM — 2 de 2 ficheiro(s) com SHA256 reconferido em 2026-09-15
DOCUMENT_ID_AVAILABLE:        SIM — o documento traz título e numeração próprios
PUBLICATION_DATE_AVAILABLE:   SIM — agro_01 gerado em 03/09/2026 16:09; agro_09 gerado em
                              02/09/2026 15:26 (data lida do proprio PDF)
RAW_EVIDENCE_PRESERVABLE:     SIM — já preservada:
                              data/samples/IT-SOURCE-SAMPLES/IT-T2-002/MANIFEST.json
AUTOMATION_FEASIBILITY:       NÃO SEI — nenhuma rota foi contratada. O manifesto guarda o endereço
                              exato que trouxe cada ficheiro, o que é o ponto de partida de um
                              contrato.
COLLECTION_FEASIBILITY:       NÃO SEI — registar ≠ coletar; nenhuma coleta correu
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação
                              foi tentada (AUTH_USED: NENHUMA. Nao se tentou contornar
                              autenticacao.) e nenhum paywall foi contornado. ⚠️ A captura saiu
                              por VPN_COMERCIAL — nao e ISP residencial italiano (Milano,
                              Lombardia, IT — AS208172 Proton AG): a fonte pode responder de outro
                              modo a partir de um IP não italiano, e isso não foi medido.
REAL_EXAMPLE:                 «Agrometeo...informa — bollettino di zona»
                              https://www.arpa.veneto.it/risorse/data-agrometeo/agrometeo/32zone/agro_01.pdf
                              — application/pdf, 463630 bytes, SHA256 conferido em 2026-09-07
SOURCE_LOCATION:              Padova/Teolo — ARPAV
FACT_LOCATION:                zona agrometeorologica do Veneto correspondente ao numero do
                              arquivo. DIFERENTE da sede.
WHAT_IT_PROVES:               que a ARPAV publica boletim agrometeorologico por zona, em PDF
                              aberto, com 32 zonas e geracao independente por zona (datas
                              diferentes entre agro_01 e agro_09)
WHAT_IT_DOES_NOT_PROVE:       o conteudo especifico de cada boletim (nao lido) · praga · risco
                              modelado · decisao de tratamento
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T2-002/MANIFEST.json
VERDICT:                      GREEN — fonte aberta, ficheiro bruto servido pelo site preservado e
                              SHA256 reconferido nesta missão
```

#### IT-T2-004 · SIAS Sicilia — agrometeorologia regional

```
SOURCE_ID:                    IT-T2-004
SOURCE_NAME:                  SIAS Sicilia — agrometeorologia regional
SOURCE_OWNER:                 SIAS — Servizio Informativo Agrometeorologico Siciliano (IT-OWN-005)
COUNTRY:                      ITALY
REGION:                       Sicilia
LANGUAGE:                     IT
TERRITORY:                    T2
SOURCE_TYPE:                  serviço agrometeorológico regional
URL:                          http://www.sias.regione.sicilia.it
ACCESS_METHOD:                HTML
CROPS:                        transversal
TOPICS:                       chuva, temperatura, seca, território
GEOGRAPHIC_GRANULARITY:       NÃO SEI (esperado: estação/ponto)
UPDATE_FREQUENCY:             NÃO SEI
HISTORICAL_DEPTH:             NÃO SEI
SOURCE_IDENTITY_PRESERVABLE:  SIM — 2 de 2 ficheiro(s) com SHA256 reconferido em 2026-09-15
DOCUMENT_ID_AVAILABLE:        SIM — o documento traz título e numeração próprios
PUBLICATION_DATE_AVAILABLE:   SIM — janela 26/08/2026 a 05/09/2026 (11 dias) na tabela de chuva
RAW_EVIDENCE_PRESERVABLE:     SIM — já preservada:
                              data/samples/IT-SOURCE-SAMPLES/IT-T2-004/MANIFEST.json
AUTOMATION_FEASIBILITY:       NÃO SEI — nenhuma rota foi contratada. O manifesto guarda o endereço
                              exato que trouxe cada ficheiro, o que é o ponto de partida de um
                              contrato.
COLLECTION_FEASIBILITY:       NÃO SEI — registar ≠ coletar; nenhuma coleta correu
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação
                              foi tentada (AUTH_USED: NENHUMA. Nao se tentou contornar
                              autenticacao.) e nenhum paywall foi contornado. ⚠️ A captura saiu
                              por VPN_COMERCIAL — nao e ISP residencial italiano (Milano,
                              Lombardia, IT — AS208172 Proton AG): a fonte pode responder de outro
                              modo a partir de um IP não italiano, e isso não foi medido.
REAL_EXAMPLE:                 «Precipitazioni giornaliere (mm) — dal 26/08/2026 al 05/09/2026»
                              http://www.sias.regione.sicilia.it/NHEOWL0530_00.html — text/html,
                              79628 bytes, SHA256 conferido em 2026-09-07
SOURCE_LOCATION:              Palermo — Regione Siciliana
FACT_LOCATION:                estacoes da Sicilia, agrupadas por provincia (ex.: Calatafimi,
                              Castellammare del Golfo, Castelvetrano, Erice, Marsala, Mazara del
                              Vallo, Pantelleria, Salemi)
WHAT_IT_PROVES:               que a Sicilia publica dado agrometeorologico diario por estacao,
                              aberto, sem login, com janela movel de 11 dias e acumulado anual
WHAT_IT_DOES_NOT_PROVE:       praga · cultura · decisao de tratamento · dado por talhao · serie
                              historica longa (a pagina so mostra a janela corrente)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T2-004/MANIFEST.json
VERDICT:                      GREEN — fonte aberta, ficheiro bruto servido pelo site preservado e
                              SHA256 reconferido nesta missão
```

#### IT-T3-002 · Campania — Bollettini fitosanitari regionali

```
SOURCE_ID:                    IT-T3-002
SOURCE_NAME:                  Campania — Bollettini fitosanitari regionali
SOURCE_OWNER:                 Regione Campania — Servizio Fitosanitario Regionale (IT-OWN-007)
COUNTRY:                      ITALY
REGION:                       Campania
LANGUAGE:                     IT
TERRITORY:                    T3
SOURCE_TYPE:                  boletim fitossanitário oficial
URL:                          https://www.agricoltura.regione.campania.it
ACCESS_METHOD:                PDF
CROPS:                        múltiplas
TOPICS:                       fenologia, avversità, difesa integrata, província
GEOGRAPHIC_GRANULARITY:       NÃO SEI (esperado: província)
UPDATE_FREQUENCY:             NÃO SEI
HISTORICAL_DEPTH:             NÃO SEI
SOURCE_IDENTITY_PRESERVABLE:  SIM — 3 de 3 ficheiro(s) com SHA256 reconferido em 2026-09-15
DOCUMENT_ID_AVAILABLE:        SIM — o documento traz título e numeração próprios
PUBLICATION_DATE_AVAILABLE:   SIM — 02-09-2026 (SA e NA) e 26-08-2026 (SA)
RAW_EVIDENCE_PRESERVABLE:     SIM — já preservada:
                              data/samples/IT-SOURCE-SAMPLES/IT-T3-002/MANIFEST.json
AUTOMATION_FEASIBILITY:       NÃO SEI — nenhuma rota foi contratada. O manifesto guarda o endereço
                              exato que trouxe cada ficheiro, o que é o ponto de partida de um
                              contrato.
COLLECTION_FEASIBILITY:       NÃO SEI — registar ≠ coletar; nenhuma coleta correu
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação
                              foi tentada (AUTH_USED: NENHUMA. Nao se tentou contornar
                              autenticacao.) e nenhum paywall foi contornado. ⚠️ A captura saiu
                              por VPN_COMERCIAL — nao e ISP residencial italiano (Milano,
                              Lombardia, IT — AS208172 Proton AG): a fonte pode responder de outro
                              modo a partir de um IP não italiano, e isso não foi medido.
REAL_EXAMPLE:                 «Bollettino fitosanitario — produzione integrata»
                              https://agricoltura.regione.campania.it/difesa/bollettini/bollettini_2026/pdf/SA-02-09.pdf
                              — application/pdf, 813109 bytes, SHA256 conferido em 2026-09-07
SOURCE_LOCATION:              Napoli — sede da Regione Campania
FACT_LOCATION:                provincia do proprio boletim: Salerno (SA) e Napoli (NA). DIFERENTE
                              da sede.
WHAT_IT_PROVES:               que existe orientacao fitossanitaria oficial semanal por provincia
                              na Campania, com limiar de intervencao e substancia ativa nomeada, e
                              com marcacao de presenca/ausencia de pragas observada pelo servico
                              regional
WHAT_IT_DOES_NOT_PROVE:       tratamento efetivamente realizado no campo · venda · estoque ·
                              market share · produto ADAMA comprado · incidencia nacional ·
                              severidade numerica por ponto
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T3-002/MANIFEST.json
VERDICT:                      GREEN — fonte aberta, ficheiro bruto servido pelo site preservado e
                              SHA256 reconferido nesta missão
```

#### IT-T3-008 · ARIF Puglia / Agrometeo Puglia — rete fitosanitaria

```
SOURCE_ID:                    IT-T3-008
SOURCE_NAME:                  ARIF Puglia / Agrometeo Puglia — rete fitosanitaria
SOURCE_OWNER:                 ARIF Puglia — Agenzia Regionale per le Attività Irrigue e Forestali
                              (IT-OWN-010)
COUNTRY:                      ITALY
REGION:                       Puglia
LANGUAGE:                     IT
TERRITORY:                    T3
SOURCE_TYPE:                  rede regional
URL:                          https://www.arifpuglia.it
ACCESS_METHOD:                PDF
CROPS:                        OLIVE · DURUM_WHEAT
TOPICS:                       monitoramento, alerta, agrometeorologia
GEOGRAPHIC_GRANULARITY:       NÃO SEI
UPDATE_FREQUENCY:             NÃO SEI
HISTORICAL_DEPTH:             NÃO SEI
SOURCE_IDENTITY_PRESERVABLE:  SIM — 3 de 3 ficheiro(s) com SHA256 reconferido em 2026-09-15
DOCUMENT_ID_AVAILABLE:        SIM — o documento traz título e numeração próprios
PUBLICATION_DATE_AVAILABLE:   SIM — Notiziario n.36 de 02/09/2026 (valido ate 08/09) · n.35 de
                              26/08/2026 · Bollettino diario n.136 de 07/09/2026
RAW_EVIDENCE_PRESERVABLE:     SIM — já preservada:
                              data/samples/IT-SOURCE-SAMPLES/IT-T3-008/MANIFEST.json
AUTOMATION_FEASIBILITY:       NÃO SEI — nenhuma rota foi contratada. O manifesto guarda o endereço
                              exato que trouxe cada ficheiro, o que é o ponto de partida de um
                              contrato.
COLLECTION_FEASIBILITY:       NÃO SEI — registar ≠ coletar; nenhuma coleta correu
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação
                              foi tentada (AUTH_USED: NENHUMA. Nao se tentou contornar
                              autenticacao.) e nenhum paywall foi contornado. ⚠️ A captura saiu
                              por VPN_COMERCIAL — nao e ISP residencial italiano (Milano,
                              Lombardia, IT — AS208172 Proton AG): a fonte pode responder de outro
                              modo a partir de um IP não italiano, e isso não foi medido.
REAL_EXAMPLE:                 «Notiziario Agrometeorologico & Fitosanitario Regionale n. 36 del 02
                              settembre 2026 — Settimanale N.36 Anno XL»
                              https://www.agrometeopuglia.it/bollettino-elettronico/settimanale/2026/Notiziario_Agrometeorologico_N36_02-09-2026.pdf
                              — application/pdf, 2703344 bytes,
                              SHA256 e612807928b5ada942482707a04e24e6b0099270b3426b927651d3fc3a628859,
                              reconferido contra os bytes em disco em 2026-09-16
                              ⚠️ ATÉ 2026-09-16 ESTA LINHA DESCREVIA DOIS DOCUMENTOS COMO SE FOSSE
                              UM: o título era o do n.36, e o endereço e os 2.723.072 bytes eram os
                              do n.35. Os dois ficheiros são desta mesma fonte e os dois estão no
                              manifesto — o defeito era só da citação. UMA CITAÇÃO QUE MISTURA DOIS
                              DOCUMENTOS NÃO PROVA NENHUM DOS DOIS.
OUTROS_DOCUMENTOS_NA_AMOSTRA: Notiziario n.35 de 26/08/2026 (2.723.072 bytes) · Bollettino
                              Giornaliero Meteorologico n.136 de 07/09/2026 (1.446.423 bytes) —
                              ambos com SHA256 próprio no manifesto
ENDPOINT_QUE_SERVE:           www.agrometeopuglia.it — o portal agrometeo da ARIF Puglia. O endereço
                              da ficha (arifpuglia.it) é o da agência; os boletins são servidos pelo
                              portal. ENDEREÇO DIFERENTE, MESMO PUBLICADOR — COL-LAW-009.
SOURCE_LOCATION:              Bari — ARIF Puglia
FACT_LOCATION:                Puglia (regional)
WHAT_IT_PROVES:               que a Puglia tem boletim regional semanal declaradamente
                              agrometeorologico E fitossanitario, no ano XL (quadragesimo), em PDF
                              aberto, com rota previsivel; e um boletim meteorologico diario de
                              segunda a sexta
WHAT_IT_DOES_NOT_PROVE:       o conteudo fitossanitario especifico (nao lido) · cultura · praga ·
                              limiar · nenhuma ocorrencia de campo pode ser afirmada a partir
                              desta amostra
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T3-008/MANIFEST.json
VERDICT:                      GREEN — fonte aberta, ficheiro bruto servido pelo site preservado e
                              SHA256 reconferido nesta missão
```

#### IT-T3-010 · APOL Lecce — monitoraggio olivicolo

```
SOURCE_ID:                    IT-T3-010
SOURCE_NAME:                  APOL Lecce — monitoraggio olivicolo
SOURCE_OWNER:                 APOL Lecce — Associazione Produttori Olivicoli Lecce (IT-OWN-012)
COUNTRY:                      ITALY
REGION:                       Puglia (Lecce)
LANGUAGE:                     IT
TERRITORY:                    T3
SOURCE_TYPE:                  organização de produtores
URL:                          NÃO SEI
ACCESS_METHOD:                PDF
CROPS:                        OLIVE
TOPICS:                       monitoramento olivícola
GEOGRAPHIC_GRANULARITY:       NÃO SEI
UPDATE_FREQUENCY:             NÃO SEI
HISTORICAL_DEPTH:             NÃO SEI
SOURCE_IDENTITY_PRESERVABLE:  SIM — 2 de 2 ficheiro(s) com SHA256 reconferido em 2026-09-15
DOCUMENT_ID_AVAILABLE:        SIM — o documento traz título e numeração próprios
PUBLICATION_DATE_AVAILABLE:   SIM — Bollettino n.9 valido de 07/09/2026 a 13/09/2026 (comeca HOJE)
                              · n.8 de 31/08 a 06/09/2026
RAW_EVIDENCE_PRESERVABLE:     SIM — já preservada:
                              data/samples/IT-SOURCE-SAMPLES/IT-T3-010/MANIFEST.json
AUTOMATION_FEASIBILITY:       NÃO SEI — nenhuma rota foi contratada. O manifesto guarda o endereço
                              exato que trouxe cada ficheiro, o que é o ponto de partida de um
                              contrato.
COLLECTION_FEASIBILITY:       NÃO SEI — registar ≠ coletar; nenhuma coleta correu
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação
                              foi tentada (AUTH_USED: NENHUMA. Nao se tentou contornar
                              autenticacao.) e nenhum paywall foi contornado. ⚠️ A captura saiu
                              por VPN_COMERCIAL — nao e ISP residencial italiano (Milano,
                              Lombardia, IT — AS208172 Proton AG): a fonte pode responder de outro
                              modo a partir de um IP não italiano, e isso não foi medido.
REAL_EXAMPLE:                 «Bollettino n° 9 Mosca dell'olivo valido dal 07/09 al 13/09/2026»
                              http://www.apol.it/documenti/notizie/Bollettino_Mosca_dellOlivo_n_9_del_07_09_2026.pdf
                              — application/pdf, 1653200 bytes, SHA256 conferido em 2026-09-07
SOURCE_LOCATION:              Lecce — sede da cooperativa
FACT_LOCATION:                COMPRENSORIO declarado dentro do documento. Na amostra n.9: 'BR -
                              COLLINA LITORANEA', cobrindo BRINDISI, CAROVIGNO, CEGLIE MESSAPICA,
                              CELLINO SAN MARCO, FASANO, FRANCAVILLA FONTANA, MESAGNE, ORIA,
                              OSTUNI, SAN DONACI, SAN VITO DEI NORMANNI, TORCHIAROLO, TORRE SANTA
                              SUSANNA, VILLA CASTELLI, SAN GIORGIO IONICO. DIFERENTE da sede
                              (Lecce).
WHAT_IT_PROVES:               que existe monitoramento semanal de mosca-da-azeitona na Puglia, por
                              comprensorio, publicado aberto em PDF, com fase fenologica, contagem
                              de capturas, percentual de infestacao e referencia explicita ao
                              limiar de intervencao
WHAT_IT_DOES_NOT_PROVE:       tratamento realizado · venda · estoque · uso de produto · market
                              share · numero por talhao individual · cobertura de toda a Puglia (a
                              amostra cobre um comprensorio)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T3-010/MANIFEST.json
VERDICT:                      GREEN — fonte aberta, ficheiro bruto servido pelo site preservado e
                              SHA256 reconferido nesta missão
```

#### IT-T3-011 · AGRIOS — direttive, aggiornamenti e deroghe per la produzione integrata

```
SOURCE_ID:                    IT-T3-011
SOURCE_NAME:                  AGRIOS — direttive, aggiornamenti e deroghe per la produzione
                              integrata
SOURCE_OWNER:                 AGRIOS — Arbeitsgruppe für den Integrierten Obstbau Südtirol
                              (IT-OWN-013)
COUNTRY:                      ITALY
REGION:                       Südtirol (Bolzano)
LANGUAGE:                     IT (O MESMO DOCUMENTO EXISTE EM DE)
TERRITORY:                    T3
SOURCE_TYPE:                  diretriz técnica de rede
URL:                          https://www.agrios.it
ACCESS_METHOD:                PDF
CROPS:                        APPLE
TOPICS:                       difesa integrata, direttive, aggiornamenti, deroghe
GEOGRAPHIC_GRANULARITY:       província
UPDATE_FREQUENCY:             NÃO SEI (esperado: anual + atualizações na safra)
HISTORICAL_DEPTH:             NÃO SEI
SOURCE_IDENTITY_PRESERVABLE:  SIM — 1 de 1 ficheiro(s) com SHA256 reconferido em 2026-09-15
DOCUMENT_ID_AVAILABLE:        SIM — o documento traz título e numeração próprios
PUBLICATION_DATE_AVAILABLE:   SIM — 2026 (declarado no titulo e na capa)
RAW_EVIDENCE_PRESERVABLE:     SIM — já preservada:
                              data/samples/IT-SOURCE-SAMPLES/IT-T3-011/MANIFEST.json
AUTOMATION_FEASIBILITY:       NÃO SEI — nenhuma rota foi contratada. O manifesto guarda o endereço
                              exato que trouxe cada ficheiro, o que é o ponto de partida de um
                              contrato.
COLLECTION_FEASIBILITY:       NÃO SEI — registar ≠ coletar; nenhuma coleta correu
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação
                              foi tentada (AUTH_USED: NENHUMA. Nao se tentou contornar
                              autenticacao.) e nenhum paywall foi contornado. ⚠️ A captura saiu
                              por VPN_COMERCIAL — nao e ISP residencial italiano (Milano,
                              Lombardia, IT — AS208172 Proton AG): a fonte pode responder de outro
                              modo a partir de um IP não italiano, e isso não foi medido.
REAL_EXAMPLE:                 «DIRETTIVE PER LA FRUTTICOLTURA INTEGRATA 2026»
                              https://www.agrios.it/wp-content/uploads/0286_26_Agrios_Broschuere_Richtlinien_integrierte_Kernobstbau_IT_WEB.pdf
                              — application/pdf, 5705903 bytes, SHA256 conferido em 2026-09-07
SOURCE_LOCATION:              Terlano (BZ), Alto Adige
FACT_LOCATION:                Alto Adige / Sudtirol — area de aplicacao da diretriz
WHAT_IT_PROVES:               que existe um disciplinar tecnico anual, publico e em italiano, que
                              define o que pode ser usado na fruticultura integrada do Alto Adige
                              em 2026
WHAT_IT_DOES_NOT_PROVE:       ocorrencia de praga · tratamento realizado · venda · quantos
                              produtores seguem · autorizacao regulatoria (isso e do Ministero)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T3-011/MANIFEST.json
VERDICT:                      GREEN — fonte aberta, ficheiro bruto servido pelo site preservado e
                              SHA256 reconferido nesta missão
```

#### IT-T5-002 · FEM OpenPub — repositório de publicações

```
SOURCE_ID:                    IT-T5-002
SOURCE_NAME:                  FEM OpenPub — repositório de publicações
SOURCE_OWNER:                 Fondazione Edmund Mach (FEM) (IT-OWN-014)
COUNTRY:                      ITALY
REGION:                       Trentino
LANGUAGE:                     EN
TERRITORY:                    T5
SOURCE_TYPE:                  repositório institucional
URL:                          https://publications.fmach.it
ACCESS_METHOD:                HTML
CROPS:                        GRAPE · APPLE e outras
TOPICS:                       papers, autores, instituição
GEOGRAPHIC_GRANULARITY:       não aplicável (afiliação != local do experimento)
UPDATE_FREQUENCY:             NÃO SEI
HISTORICAL_DEPTH:             NÃO SEI
SOURCE_IDENTITY_PRESERVABLE:  SIM — 1 de 1 ficheiro(s) com SHA256 reconferido em 2026-09-15
DOCUMENT_ID_AVAILABLE:        SIM — o documento traz título e numeração próprios
PUBLICATION_DATE_AVAILABLE:   SIM — 2025-07-15
RAW_EVIDENCE_PRESERVABLE:     SIM — já preservada:
                              data/samples/IT-SOURCE-SAMPLES/IT-T5-002/MANIFEST.json
AUTOMATION_FEASIBILITY:       NÃO SEI — nenhuma rota foi contratada. O manifesto guarda o endereço
                              exato que trouxe cada ficheiro, o que é o ponto de partida de um
                              contrato.
COLLECTION_FEASIBILITY:       NÃO SEI — registar ≠ coletar; nenhuma coleta correu
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação
                              foi tentada (AUTH_USED: NENHUMA. Nao se tentou contornar
                              autenticacao.) e nenhum paywall foi contornado. ⚠️ A captura saiu
                              por VPN_COMERCIAL — nao e ISP residencial italiano (Milano,
                              Lombardia, IT — AS208172 Proton AG): a fonte pode responder de outro
                              modo a partir de um IP não italiano, e isso não foi medido.
REAL_EXAMPLE:                 «Establishment and parasitism levels of Ganaspis kimorum on
                              Drosophila suzukii in Northeastern Italy: insights from a 4-yr
                              release program» https://openpub.fmach.it/handle/10449/91515 —
                              text/html, 60778 bytes, SHA256 conferido em 2026-09-07
SOURCE_LOCATION:              San Michele all'Adige (TN) — Fondazione Edmund Mach
FACT_LOCATION:                Nordeste da Italia — area do programa de soltura, conforme o proprio
                              titulo
WHAT_IT_PROVES:               que a FEM mantem repositorio publico, pesquisavel, com abstract
                              aberto, autores, ano e tipologia — e que ha massa critica de ciencia
                              italiana sobre pragas especificas
WHAT_IT_DOES_NOT_PROVE:       ocorrencia de campo hoje · eficacia comercial · autorizacao · venda
                              · que o texto completo do artigo esteja aberto (so o registro e o
                              abstract foram vistos)
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T5-002/MANIFEST.json
VERDICT:                      GREEN — fonte aberta, ficheiro bruto servido pelo site preservado e
                              SHA256 reconferido nesta missão
```

#### IT-T5-003 · AIPP — bilanci fitosanitari regionali («I Giovedì dell'AIPP»)

```
SOURCE_ID:                    IT-T5-003
SOURCE_NAME:                  Bilanci fitosanitari regionali 2024-2025 — ciclo «I Giovedì
                              dell'AIPP»
SOURCE_OWNER:                 AIPP — Associazione Italiana per la Protezione delle Piante
                              (IT-OWN-AIPP)
EVENTO_ASSOCIADO:             Giornate Fitopatologiche (IT-OWN-GIORNATE-FITO) — comitê científico
                              com site próprio, giornatefitopatologiche.it. É o EVENTO em que o
                              material é apresentado, NÃO o publicador destes ficheiros.
                              ⚠️ ATÉ 2026-09-16 ESTA FICHA DECLARAVA «Giornate Fitopatologiche
                              (IT-OWN-017)» COMO DONO, e apontava para giornatefitopatologiche.it.
                              O dono passou a AIPP. A PROVA NÃO É SÓ O ALOJAMENTO — hospedar bytes,
                              por si, não prova quem publica (um CDN ou um espelho também hospeda).
                              O que prova a AIPP como publicadora é a soma de QUATRO coisas:
                              1 · a página institucional da própria AIPP descreve o ciclo «I Giovedì
                                  dell'AIPP — Bilanci fitosanitari» como publicação sua (lida em
                                  2026-09-02, HTTP 200: research/italy-lastmile/NEW-REAL-SOURCES.json,
                                  registo «AIPP», campo O_QUE_PUBLICA);
                              2 · o ciclo tem o nome da AIPP;
                              3 · o PDF da Basilicata traz «Associazione Italiana Protezione delle
                                  Piante» no slide final (página 21 de 21) — o da Marche NÃO traz
                                  marca da AIPP em nenhuma das 44 páginas;
                              4 · os dois PDFs foram servidos por aipp.it/wp-content/uploads/ e têm o
                                  mesmo /Author («galassi_t») — uma só mão publicou os dois, e não é
                                  nenhum dos dois autores (Altieri, Alesi). Quem é galassi_t: NÃO SEI.
                              AUTOR ≠ PUBLICADOR: os autores são os serviços regionais (Ufficio
                              Fitosanitario Regione Basilicata; AMAP Regione Marche). O manifesto já
                              dizia, desde 2026-09-07, `OWNER_ID: IT-OWN-AIPP` e «são DUAS
                              organizações; não fundir». O EVENTO ONDE SE FALOU NÃO É O PUBLICADOR.
COUNTRY:                      ITALY
REGION:                       nacional
LANGUAGE:                     IT
TERRITORY:                    T5
SOURCE_TYPE:                  apresentação técnica de ciclo científico
URL:                          https://aipp.it
ACCESS_METHOD:                PDF
CROPS:                        múltiplas
TOPICS:                       cultura, problema, substância/prática quando explícita, autor,
                              instituição
GEOGRAPHIC_GRANULARITY:       não aplicável
UPDATE_FREQUENCY:             BIENAL (a confirmar)
HISTORICAL_DEPTH:             NÃO SEI
SOURCE_IDENTITY_PRESERVABLE:  SIM — 2 de 2 ficheiro(s) com SHA256 reconferido em 2026-09-15
DOCUMENT_ID_AVAILABLE:        SIM — o documento traz título e numeração próprios
PUBLICATION_DATE_AVAILABLE:   SIM — 27-11-2025 (sessao olivo)
RAW_EVIDENCE_PRESERVABLE:     SIM — já preservada:
                              data/samples/IT-SOURCE-SAMPLES/IT-T5-003/MANIFEST.json
AUTOMATION_FEASIBILITY:       NÃO SEI — nenhuma rota foi contratada. O manifesto guarda o endereço
                              exato que trouxe cada ficheiro, o que é o ponto de partida de um
                              contrato.
COLLECTION_FEASIBILITY:       NÃO SEI — registar ≠ coletar; nenhuma coleta correu
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação
                              foi tentada (AUTH_USED: NENHUMA. Nao se tentou contornar
                              autenticacao.) e nenhum paywall foi contornado. ⚠️ A captura saiu
                              por VPN_COMERCIAL — nao e ISP residencial italiano (Milano,
                              Lombardia, IT — AS208172 Proton AG): a fonte pode responder de outro
                              modo a partir de um IP não italiano, e isso não foi medido.
REAL_EXAMPLE:                 «Bilancio Fitosanitario Olivo 2024-2025 — Regione Marche» (Alesi)
                              https://aipp.it/wp-content/uploads/2025/12/7_Alesi_olivo-2025_-Bilancio-Fitosanitario-Marche.pdf
                              — application/pdf, 6585313 bytes,
                              SHA256 924aabd94168c53aa1b042935cef3072889ced9dbc1374ca735bbcad791b98b6,
                              reconferido contra os bytes em disco em 2026-09-16
                              ⚠️ o título anterior dizia «Basilicata / Marche» ao lado do endereço
                              e dos bytes de UM só dos dois ficheiros. São duas apresentações
                              distintas, ambas preservadas; a citação agora descreve uma.
OUTRO_DOCUMENTO_NA_AMOSTRA:   «Bilancio Fitosanitario Olivo 2024-2025 — Regione Basilicata»
                              (Altieri), 3.991.102 bytes,
                              SHA256 2a12cb316622a9a5c28c233f236befd29707ca0e19c84ebabf43023ff23ae34e
EVIDENCE_HOST:                aipp.it (SERVER_IP 86.107.32.111) — os dois ficheiros, HTTP 200
SOURCE_LOCATION:              evento nacional online
FACT_LOCATION:                Basilicata e Marche — a regiao do balanco, DIFERENTE do local do
                              evento
WHAT_IT_PROVES:               que existe uma retrospectiva anual, por regiao e por cultura,
                              assinada pelos servicos fitossanitarios regionais, publicada em PDF
                              aberto
WHAT_IT_DOES_NOT_PROVE:       situacao corrente do campo (e balanco de campanha passada) · venda ·
                              uso de produto · numero por talhao
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T5-003/MANIFEST.json
VERDICT:                      GREEN — fonte aberta, ficheiro bruto servido pelo site preservado e
                              SHA256 reconferido nesta missão
```

#### IT-T7-002 · MASAF — elenco delle OP e AOP riconosciute

```
SOURCE_ID:                    IT-T7-002
SOURCE_NAME:                  MASAF — elenco delle OP e AOP riconosciute
SOURCE_OWNER:                 MASAF — Ministero dell'Agricoltura, della Sovranità Alimentare e
                              delle Foreste (IT-OWN-020)
COUNTRY:                      ITALY
REGION:                       nacional com desagregação regional
LANGUAGE:                     IT
TERRITORY:                    T7
SOURCE_TYPE:                  lista oficial de reconhecimento
URL:                          https://www.politicheagricole.it
ACCESS_METHOD:                OTHER (ODS)
CROPS:                        por setor
TOPICS:                       nome, tipo, setor, região, reconhecimento, data/lista
GEOGRAPHIC_GRANULARITY:       região (esperado)
UPDATE_FREQUENCY:             NÃO SEI
HISTORICAL_DEPTH:             NÃO SEI
SOURCE_IDENTITY_PRESERVABLE:  SIM — 1 de 1 ficheiro(s) com SHA256 reconferido em 2026-09-15
DOCUMENT_ID_AVAILABLE:        SIM — o documento traz título e numeração próprios
PUBLICATION_DATE_AVAILABLE:   SIM — situacao em 31 dicembre 2025, arquivo atualizado em 08.04.2026
RAW_EVIDENCE_PRESERVABLE:     SIM — já preservada:
                              data/samples/IT-SOURCE-SAMPLES/IT-T7-002/MANIFEST.json
AUTOMATION_FEASIBILITY:       NÃO SEI — nenhuma rota foi contratada. O manifesto guarda o endereço
                              exato que trouxe cada ficheiro, o que é o ponto de partida de um
                              contrato.
COLLECTION_FEASIBILITY:       NÃO SEI — registar ≠ coletar; nenhuma coleta correu
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação
                              foi tentada (AUTH_USED: NENHUMA. Nao se tentou contornar
                              autenticacao.) e nenhum paywall foi contornado. ⚠️ A captura saiu
                              por VPN_COMERCIAL — nao e ISP residencial italiano (Milano,
                              Lombardia, IT — AS208172 Proton AG): a fonte pode responder de outro
                              modo a partir de um IP não italiano, e isso não foi medido.
REAL_EXAMPLE:                 «Elenco nazionale OP e AOP riconosciute al 31 dicembre 2025 -
                              aggiornato al 08.04.2026»
                              https://www.masaf.gov.it/flex/cm/pages/ServeAttachment.php/L/IT/D/1%252F3%252Fb%252FD.4476adcbe95b46973538/P/BLOB%3AID%3D6063/E/ods?mode=download
                              — application/vnd.oasis.opendocument.spreadsheet, 59052 bytes,
                              SHA256 conferido em 2026-09-07
SOURCE_LOCATION:              Roma — MASAF
FACT_LOCATION:                Italia inteira; cada linha traz a REGIONE e a SEDE (comune +
                              provincia) da organizacao
WHAT_IT_PROVES:               quem sao, oficialmente, as organizacoes de produtores reconhecidas
                              na Italia fora do setor hortifruti: nome, forma juridica, setor,
                              sede, regiao, data de reconhecimento e valor da producao
                              comercializada declarado
WHAT_IT_DOES_NOT_PROVE:       nada de campo · nenhuma praga · nenhum preco de transacao · nao
                              prova que a organizacao publica boletim · VPC e valor declarado de
                              producao comercializada, NAO e venda de insumo nem market share
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T7-002/MANIFEST.json
VERDICT:                      GREEN — fonte aberta, ficheiro bruto servido pelo site preservado e
                              SHA256 reconferido nesta missão
```

#### IT-T9-002 · Bayer CropScience Italia — comunicação pública

```
SOURCE_ID:                    IT-T9-002
SOURCE_NAME:                  Bayer CropScience Italia — comunicação pública
SOURCE_OWNER:                 Bayer CropScience Italia (IT-OWN-042)
COUNTRY:                      ITALY
REGION:                       nacional
LANGUAGE:                     IT
TERRITORY:                    T9
SOURCE_TYPE:                  site institucional
URL:                          https://www.cropscience.bayer.it
ACCESS_METHOD:                JSON
CROPS:                        NÃO SEI
TOPICS:                       NÃO SEI
GEOGRAPHIC_GRANULARITY:       NÃO SEI
UPDATE_FREQUENCY:             NÃO SEI
HISTORICAL_DEPTH:             NÃO SEI
SOURCE_IDENTITY_PRESERVABLE:  SIM — 1 de 1 ficheiro(s) com SHA256 reconferido em 2026-09-15
DOCUMENT_ID_AVAILABLE:        SIM — o documento traz título e numeração próprios
PUBLICATION_DATE_AVAILABLE:   SIM — primeira parte anunciada para 10 marzo 2026; a pagina ja fala
                              de 'seconda stagione'. A pagina NAO expoe data de publicacao em
                              metadado — SOURCE_DATE e o que o texto declara, nao um campo do
                              site.
RAW_EVIDENCE_PRESERVABLE:     SIM — já preservada:
                              data/samples/IT-SOURCE-SAMPLES/IT-T9-002/MANIFEST.json
AUTOMATION_FEASIBILITY:       NÃO SEI — nenhuma rota foi contratada. O manifesto guarda o endereço
                              exato que trouxe cada ficheiro, o que é o ponto de partida de um
                              contrato.
COLLECTION_FEASIBILITY:       NÃO SEI — registar ≠ coletar; nenhuma coleta correu
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação
                              foi tentada (AUTH_USED: NENHUMA) e nenhum paywall foi contornado. ⚠️
                              A captura saiu por VPN_COMERCIAL (Milano, IT — Proton AG): a fonte
                              pode responder de outro modo a partir de um IP não italiano, e isso
                              não foi medido.
REAL_EXAMPLE:                 «Arriva Mais Lab: il nuovo podcast dedicato alla coltivazione del
                              mais»
                              https://www.cropscience.bayer.it/Magazine/News/Generica/Mais-Lab —
                              application/json, 3477 bytes, SHA256 conferido em 2026-09-07
SOURCE_LOCATION:              site nacional Bayer Crop Science Italia
FACT_LOCATION:                UNKNOWN — nenhum fato de campo localizado. Nao inferir pela sede.
WHAT_IT_PROVES:               que a Bayer Italia publica conteudo tecnico aberto sobre milho, com
                              pessoas nomeadas e cargo · que ela escolheu RESISTENCIA A HERBICIDA
                              em milho como tema de campanha em 2026 · que o site exige NAVEGADOR:
                              403 para curl do mesmo IP italiano
WHAT_IT_DOES_NOT_PROVE:       autorizacao de nenhum produto — so o registro do Ministero prova ·
                              venda, estoque, market share, uso realizado ou eficacia · qualquer
                              ocorrencia de campo
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T9-002/MANIFEST.json
VERDICT:                      YELLOW — o que está preservado é extrato do DOM lido por navegador —
                              o manifesto declara que NÃO são os bytes servidos pelo site
```

#### IT-T9-008 · ADAMA Italia — comunicação pública

```
SOURCE_ID:                    IT-T9-008
SOURCE_NAME:                  ADAMA Italia — comunicação pública
SOURCE_OWNER:                 ADAMA Italia S.r.l. (IT-OWN-040)
                              OWNER_ID_LEGACY: IT-OWN-ADAMA-IT — até 2026-09-16 o manifesto da
                              amostra e regras/italy_contracts.mjs chamavam a este mesmo dono
                              IT-OWN-ADAMA-IT («ADAMA Italia», nome curto). Reconciliado no mesmo
                              dia: é a MESMA entidade (os dois ids eram o dono declarado desta
                              mesma fonte, mesmo site, nascidos no mesmo commit 2640c5e0); o
                              canónico é o desta ficha, porque na cadeia de autoridade da casa
                              (provas/a_autoridade_da_fonte.py) a ficha no registo canónico decide
                              e o .mjs é contrato de ACESSO. O nome antigo não se apaga: está
                              escrito no MASTER, no manifesto e no contrato num campo chamado
                              OWNER_ID_LEGACY — ⚠️ REPRESENTAÇÃO PROVISÓRIA, SEM CONTRATO: o campo
                              nasceu em 2026-09-16 por analogia com SOURCE_ID, não há mecanismo
                              canónico de alias de dono, e este atlas identifica o dono por NOME
                              (IT-OWN-* é chave do catálogo candidato). Gate BLOCKED; ver
                              know-how §127-5b.1. Não copiar para outros donos.
                              ⚠️ Só a ADAMA foi reconciliada. Outros 11 manifestos (ISTAT, BMTI,
                              ARPAE, ARPAV, SIAS, Campania SFR, ARIF, AGRIOS, Ministero, MASAF,
                              Bayer) continuam com id de dono nomeado diferente do MASTER — dívida
                              medida, com dono na faixa Sources, NÃO paga aqui.
IDENTIFICADORES_LEGADOS:      IT-ADAMA-CATALOG — o catálogo comercial em
                              www.adama.com/italia/it/prodotti-adama/* (31 páginas) e
                              /it/prodotti/* (20 páginas). NÃO é uma segunda fonte:
                              é outro ENDPOINT desta fonte — mesmo site, o mesmo /it/sitemap.xml
                              enumera artigos e páginas de produto, mesma pessoa jurídica. Decidido
                              em 2026-09-16 e revisto no mesmo dia; ver a nota abaixo da ficha.
                              O identificador não se apaga: a ADAMA Reference mapeia-o para esta
                              ficha em referencia/adama/SOURCE-ID-MAP.json e guarda-o em
                              SOURCE_IDS_LEGACY / SOURCE_ID_LEGACY; a pasta
                              data/samples/IT-ADAMA-CATALOG/ mantém o nome (path não é identidade).
ENDPOINTS_CONHECIDOS:         /it/articolo/*          artigo técnico datado (a amostra desta ficha)
                              /it/prodotti-adama/*    catálogo comercial — 31 páginas de produto
                              /it/prodotti/*          catálogo comercial — 20 páginas de produto
                                                      (51 LEGÍVEIS ao todo; o total oficial é NÃO SEI:
                                                      a listagem /it/products/crop-protection não abre)
                              /it/sitemap.xml         enumeração, 261 endereços (51 de produto +
                                                      13 de artigo + 197 outros)
COUNTRY:                      ITALY
REGION:                       nacional
LANGUAGE:                     IT
TERRITORY:                    T9
SOURCE_TYPE:                  site institucional
URL:                          https://www.adama.com/italia
ACCESS_METHOD:                JSON
CROPS:                        NÃO SEI
TOPICS:                       NÃO SEI
GEOGRAPHIC_GRANULARITY:       NÃO SEI
UPDATE_FREQUENCY:             NÃO SEI
HISTORICAL_DEPTH:             NÃO SEI
SOURCE_IDENTITY_PRESERVABLE:  SIM — 1 de 1 ficheiro(s) com SHA256 reconferido em 2026-09-15
DOCUMENT_ID_AVAILABLE:        SIM — o documento traz título e numeração próprios
PUBLICATION_DATE_AVAILABLE:   SIM — 2026-06-03T16:36:57+0200 (published) ·
                              2026-06-03T16:45:17+0200 (modified)
RAW_EVIDENCE_PRESERVABLE:     SIM — já preservada:
                              data/samples/IT-SOURCE-SAMPLES/IT-T9-008/MANIFEST.json
AUTOMATION_FEASIBILITY:       NÃO SEI — nenhuma rota foi contratada. O manifesto guarda o endereço
                              exato que trouxe cada ficheiro, o que é o ponto de partida de um
                              contrato.
COLLECTION_FEASIBILITY:       NÃO SEI — registar ≠ coletar; nenhuma coleta correu
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação
                              foi tentada (AUTH_USED: NENHUMA) e nenhum paywall foi contornado. ⚠️
                              A captura saiu por VPN_COMERCIAL (Milano, IT — Proton AG): a fonte
                              pode responder de outro modo a partir de um IP não italiano, e isso
                              não foi medido.
REAL_EXAMPLE:                 «Orticole: come controllare le infestanti, anche quelle piu
                              difficili»
                              https://www.adama.com/italia/it/articolo/orticole-come-controllare-le-infestanti-anche-quelle-piu-difficili
                              — application/json, 5295 bytes, SHA256 conferido em 2026-09-07
SOURCE_LOCATION:              site nacional ADAMA Italia
FACT_LOCATION:                UNKNOWN — o artigo nao localiza nenhum fato de campo. Nao inferir
                              pela sede.
WHAT_IT_PROVES:               que a ADAMA Italia publica conteudo tecnico datado, em italiano,
                              aberto e sem login · que ela associa publicamente o produto Sonavio®
                              a bifenox, a inibicao de PPO e ao problema de resistencia em
                              horticolas/tomate · que o site exige NAVEGADOR: 403 para curl mesmo
                              com cabecalhos completos, do mesmo IP italiano
WHAT_IT_DOES_NOT_PROVE:       que Sonavio® esta autorizado na Italia — isso so o registro do
                              Ministero prova · que esta comercialmente disponivel · eficacia,
                              venda, estoque, market share ou uso realizado · qualquer ocorrencia
                              de campo — o artigo nao mede nada em campo
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T9-008/MANIFEST.json
VERDICT:                      YELLOW — o que está preservado é extrato do DOM lido por navegador —
                              o manifesto declara que NÃO são os bytes servidos pelo site
```

##### `IT-ADAMA-CATALOG` não é uma segunda fonte — decidido em 2026-09-16, revisto no mesmo dia

O catálogo comercial da ADAMA Itália andou **17 dias** (30/08 → 16/09/2026; a primeira
redação desta nota escreveu «dois anos», e estava errada) com identificador próprio,
`IT-ADAMA-CATALOG`, sem nunca ter ficha neste atlas. A pergunta era: fonte nova, ou
outro endereço da fonte que já está aqui?

**A lei decide, e a prática não a revoga — mas a lei diz menos do que a primeira redação
lhe pôs na boca.** O que a Bíblia sustenta, à letra:

| lei | o que diz | aqui |
|---|---|---|
| `COL-LAW-009` | `SOURCE` = quem publica / mantém (ex.: **ARPAV Veneto**); `ENDPOINT` = onde tecnicamente se acessa (ex.: a URL do boletim da zona 7) | ADAMA Italia S.r.l. · `/it/prodotti-adama/*` e `/it/articolo/*` |
| `COL-LAW-205` | trocar o **meio técnico de acesso** não cria fonte; uma fonte pode ter vários endpoints (site, RSS, API, sitemap…) | o catálogo é um endpoint do mesmo site |
| `COL-LAW-206` | URL e *slug* não são identidade canónica | `/prodotti-adama` vs `/articolo` não decide nada |

⚠️ A Bíblia escreve `SOURCE = instituição / publisher / **origem lógica**` (COL-LAW-205) e
**nunca define «origem lógica»** — a expressão aparece uma vez em todo o texto. Não existe lei
que diga «mesmo publicador ⇒ mesma fonte». E a régua da casa
(`candidatas/ITALY-SOURCE-MASTER-V1.md`, §3) diz o **contrário** do que a primeira redação
lhe atribuiu: *«uma organização pode ter vários canais, sem ser duplicada»* fala do
**OWNER** não se duplicar — a tabela ao lado dá a **um só dono vários `SOURCE_ID`** (ICQRF:
Cantina Italia · Frantoio Italia, T10 · T10; ISTAT: coltivazioni · commercio estero). Os
precedentes `EU-T1-001`/`002` (Eurostat) e `IT-T1-005`/`011` (Regione Umbria, mesmo
território, só muda a URL) mostram o mesmo publicador com duas fichas.

    MESMO PUBLICADOR NÃO É, POR SI, MESMA FONTE. A LEI NÃO O DIZ, E A CASA NÃO O PRATICA.

**O que decide este caso são factos, não a regra geral:**

1. **mesma pessoa jurídica** — `CATALOG-SNAPSHOTS.json` · `AUTHORITY` «ADAMA Italia S.r.l.»; esta ficha · `SOURCE_OWNER` «ADAMA Italia S.r.l. (IT-OWN-040)»;
2. **mesmo site e mesmo sistema** — `www.adama.com/italia`, atrás do mesmo Akamai Bot Manager (403 a curl nos dois casos);
3. **uma só enumeração** — `data/samples/IT-ADAMA-CATALOG/2026-09-15/catalog-enumeration.json`: o **mesmo** `/it/sitemap.xml` (SHA256 `7648b94e…`) lista 51 URLs de produto (31 em `/it/prodotti-adama/*` + 20 em `/it/prodotti/*`) **e** 13 URLs `/it/articolo/*`, num total de 261;
4. **o desenho deste registo** — as oito entradas T9 `IT-T9-001` … `IT-T9-008` de `candidatas/ITALY-SOURCE-MASTER-V1.json` (duas delas, `002` e `008`, já com ficha neste Atlas) são todas «*&lt;empresa&gt; Italia — comunicação pública*», `SOURCE_TYPE` «site institucional»: uma entrada por site institucional de concorrente. O catálogo é uma secção desse site;
5. **nada aponta para uma segunda origem lógica** — não há mantenedor distinto, nem contrato distinto, nem série própria com identidade e cadência próprias. O que difere é a **identidade nativa do item** (página de produto: `NODE_ID` + número de registo; artigo: título + data) — e isso é `SOURCE_NATIVE_ID` de COL-LAW-206, identidade de **item**, não de fonte.

As quatro diferenças que existem — URL, secção do site, tipo de conteúdo, uso — **não bastam
sozinhas** para criar fonte. O que bastaria (mantenedor, contrato, série ou sistema
distintos) não foi encontrado. **«Origem lógica» continua sem definição na Bíblia: isso é um
`NÃO SEI` declarado, não uma regra nova escrita aqui.**

```
IT_ADAMA_CATALOG_IDENTITY  =  PROVEN_EXISTING_SOURCE  →  IT-T9-008
SOURCE_ID_CRIADO           =  0
SOURCE_IDENTITY_REASON     =  mesma pessoa jurídica + mesmo site/sistema + um só sitemap
                              enumera os dois caminhos + registo T9 é por site institucional;
                              nenhuma prova de segunda origem lógica
```

**O identificador não se apaga.** `IT-ADAMA-CATALOG` é **legado**: a pasta
`data/samples/IT-ADAMA-CATALOG/` mantém o nome (path não é identidade), e cada registo
produzido sob ele continua a responder «como me chamava quando fui produzido?» —
`SOURCE_IDS_LEGACY` em 51 linhas do portfolio e 141 documentos, `SOURCE_ID_LEGACY` nas
duas fotos do catálogo.

**A dívida da faixa ADAMA Reference foi paga pelo dono, em 2026-09-16.**
`fontes/adama_referencia.py` (`SOURCE_ID_CANONICO`) passou a mapear `SRC_ADAMA_COM` e
`IT-ADAMA-CATALOG` para `IT-T9-008`, e `referencia/adama/SOURCE-ID-MAP.json` foi regenerado
por ele (3 registos). Havia uma **segunda cópia** do identificador em
`fontes/adama_catalogo_snapshot.py` (`SOURCE_ID = 'IT-ADAMA-CATALOG'`, escrito como
identidade nas fotos) — passou a ler o mapa da Reference, para que a casa tenha uma lista
só (`COL-LAW-053`). Nenhum `ADAMA_PRODUCT_ID`, `DOCUMENT_ID`, `SHA256` ou `IDENTITY_SEAL`
mudou: só proveniência de fonte. Provas: `tests/test_adama_referencia.py` (classe
`LegadoNaoECanonico`) e `tests/test_adama_catalogo_drift.py`.

    HERDAR UM IDENTIFICADOR NÃO É CERTIFICÁ-LO.
    LEGADO NÃO É CANÓNICO — E QUEM CORRIGE É O DONO DO BUILDER, NÃO A MÃO NO JSON.

#### IT-T10-002 · BMTI — analisi di mercato cereali

```
SOURCE_ID:                    IT-T10-002
SOURCE_NAME:                  BMTI — analisi di mercato cereali
SOURCE_OWNER:                 BMTI — Borsa Merci Telematica Italiana S.c.p.A. (IT-OWN-032)
COUNTRY:                      ITALY
REGION:                       nacional
LANGUAGE:                     IT
TERRITORY:                    T10
SOURCE_TYPE:                  análise de mercado telemática
URL:                          https://www.bmti.it
ACCESS_METHOD:                HTML
CROPS:                        DURUM_WHEAT · SOFT_WHEAT · MAIZE
TOPICS:                       preço, tendência, análise
GEOGRAPHIC_GRANULARITY:       NÃO SEI
UPDATE_FREQUENCY:             NÃO SEI
HISTORICAL_DEPTH:             NÃO SEI
SOURCE_IDENTITY_PRESERVABLE:  SIM — 2 de 2 ficheiro(s) com SHA256 reconferido em 2026-09-15
DOCUMENT_ID_AVAILABLE:        SIM — o documento traz título e numeração próprios
PUBLICATION_DATE_AVAILABLE:   SIM — 24/08/2026 (cereais)
RAW_EVIDENCE_PRESERVABLE:     SIM — já preservada:
                              data/samples/IT-SOURCE-SAMPLES/IT-T10-002/MANIFEST.json
AUTOMATION_FEASIBILITY:       NÃO SEI — nenhuma rota foi contratada. O manifesto guarda o endereço
                              exato que trouxe cada ficheiro, o que é o ponto de partida de um
                              contrato.
COLLECTION_FEASIBILITY:       NÃO SEI — registar ≠ coletar; nenhuma coleta correu
LEGAL_OR_ACCESS_RISK:         NÃO SEI — termos de uso não lidos nesta missão. Nenhuma autenticação
                              foi tentada (AUTH_USED: NENHUMA. Nao se tentou contornar
                              autenticacao.) e nenhum paywall foi contornado. ⚠️ A captura saiu
                              por VPN_COMERCIAL — nao e ISP residencial italiano (Milano,
                              Lombardia, IT — AS208172 Proton AG): a fonte pode responder de outro
                              modo a partir de um IP não italiano, e isso não foi medido.
REAL_EXAMPLE:                 «Mercato cerealicolo, mais e grano tenero in rialzo tra clima
                              avverso e tensioni nel Mar Nero»
                              https://www.bmti.it/prezzi-cereali/46622/ — text/html, 96573 bytes,
                              SHA256 conferido em 2026-09-07
SOURCE_LOCATION:              Roma — sede da BMTI
FACT_LOCATION:                Italia (listini das Borse Merci nacionais) + mercado internacional
                              (Mar Negro, Europa). NAO e um ponto de campo.
WHAT_IT_PROVES:               que ha analise de preco datada e recorrente de milho, trigo mole e
                              azeite, com variacao percentual mensal e comparacao anual, publicada
                              aberta
WHAT_IT_DOES_NOT_PROVE:       preco de uma transacao especifica · volume vendido por empresa ·
                              sinal de campo · incidencia de praga · uso de defensivo
EVIDENCE:                     data/samples/IT-SOURCE-SAMPLES/IT-T10-002/MANIFEST.json
VERDICT:                      GREEN — fonte aberta, ficheiro bruto servido pelo site preservado e
                              SHA256 reconferido nesta missão
```


---

### Regra de contagem (declarada para evitar leitura ambígua)

O placar conta **SOURCE_IDs**, não fichas. Uma ficha pode cobrir mais de um SOURCE_ID
(ex.: `FR/ES/IT-T9-001` é uma ficha e três fontes), e algumas fontes testadas aparecem em
tabelas de "não alcançadas" sem ficha própria (as nacionais de T1, EU-T10-002/003).

Verificado na MISSÃO 07 e atualizado em 2026-08-29: **26 fichas · <!--M:SOURCE_ID_COUNT-->190<!--/M--> SOURCE_IDs · 16 GREEN · 4 YELLOW · 0 RED · 16 NÃO SEI**.
Os números batem. `tests/test_canonico.py` passou a verificar isso.

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
| ITALY | 75 | 81 | 0 | 3 | 159 |
| **Total** | **90** | **83** | **0** | **17** | **190** |

*Movimento de 2026-09-15: **+11 GREEN e +2 YELLOW**, todos italianos, todos vindos da
secção de RECONCILIAÇÃO — prova que já estava guardada e que o atlas não mostrava.
**Nenhum `SOURCE_ID` novo foi emitido** e nenhuma coleta correu: a população continua em
257 identidades (`py leis/fonte_do_atlas.py`). O que mudou foi quantas delas este ficheiro
deixa ver.*

### Cobertura por território

| | T1 | T2 | T3 | T4 | T5 | T6 | T7 | T8 | T9 | T10 | T11 | T12 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| EUROPE | 2G | 3G/1? | 1? | 1G/1? | 1G | 1G | – | 1? | – | 1G/2? | – | **1G** |
| FRANCE | 1? | – | 1Y/1? | 1G | – | – | – | – | 1? | – | 1Y | – |
| SPAIN | 1? | – | **1G** | 3G/1? | – | – | – | – | 1? | – | – | – |
| ITALY | 1?/17G/5Y | 16G/6Y | 1Y/8G/5Y | 1G | 17G/16Y | 36Y | 3G | – | 1?/3G/4Y | 11G/1Y | 1Y/1G | 2G/2Y |

*(– = não investigado)*
