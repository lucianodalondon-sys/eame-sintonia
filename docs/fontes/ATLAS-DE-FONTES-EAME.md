# ATLAS DE FONTES — SINTONIA EAME

Catálogo de tudo que conseguimos **realmente** observar em França, Espanha, Itália e na
camada comum europeia.

> Este atlas registra **fontes**, não desejos. Uma linha só existe aqui depois que alguém
> abriu a fonte, olhou o que ela entrega e guardou evidência disso.

**Estado:** Fase 0 — estrutura pronta, **0 fontes registradas**.
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

*(vazio — nenhuma fonte investigada ainda; a investigação dos territórios T1–T12 é o próximo passo)*

### Placar

| Recorte | GREEN | YELLOW | RED | NÃO SEI | Total |
|---|---|---|---|---|---|
| EUROPE | 0 | 0 | 0 | 0 | 0 |
| FRANCE | 0 | 0 | 0 | 0 | 0 |
| SPAIN | 0 | 0 | 0 | 0 | 0 |
| ITALY | 0 | 0 | 0 | 0 | 0 |
| **Total** | **0** | **0** | **0** | **0** | **0** |

### Cobertura por território

| | T1 | T2 | T3 | T4 | T5 | T6 | T7 | T8 | T9 | T10 | T11 | T12 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| EUROPE | – | – | – | – | – | – | – | – | – | – | – | – |
| FRANCE | – | – | – | – | – | – | – | – | – | – | – | – |
| SPAIN | – | – | – | – | – | – | – | – | – | – | – | – |
| ITALY | – | – | – | – | – | – | – | – | – | – | – | – |

*(– = não investigado)*
