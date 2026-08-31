# HANDOFF DE CONTA — SINTONIA EAME

**Este documento existe porque a conta Claude que construiu o repositório acabou.**
Ele foi escrito para que a próxima conta entre **sem nenhum contexto da conversa anterior**
e continue com perda mínima de inteligência.

Se algo aqui divergir do repositório, **o repositório vence** — e a divergência é um achado
a reportar, não um erro a ignorar.

---

## A · IDENTIDADE DO ESTADO

| | |
|---|---|
| **DATE** | 2026-08-29 |
| **BRANCH** | `claude/sintonia-eame-repo-setup-xccfob` |
| **HEAD** | ver `git rev-parse HEAD` — o commit de handoff é o último |
| **REMOTE_HEAD** | idêntico ao local no momento do push |
| **WORKING_TREE** | limpo |
| **TESTS** | `python3 -m unittest discover -s tests` → **759 testes, 0 falhas, 0 erros, 0 pulados** |
| **LAST_MAJOR_MISSION** | 10B-ES — fechar os portões estruturais antes de coletar mais |
| **CURRENT_COUNTRY_SCOPE** | **ESPANHA**. França e Itália **não** foram abertas na camada de voz. |

**Nunca confie em HEAD de memória. Meça.**

---

## B · O QUE É O SINTONIA EAME

Sistema de **inteligência externa** para a ADAMA na região EAME. Lê fontes públicas
(registro regulatório, campo, ciência, clima, mercado, voz pública), normaliza, cruza e
entrega contexto conectado com a evidência sempre à mão.

**A premissa que define tudo: não teremos dados internos da ADAMA. Nunca.**

O sistema **não depende e não pode depender** de: `sales` · `margin` · `CRM` · `inventory` ·
`internal campaign data` · `internal distributor data` · `pipeline de registro interno` ·
`market share interno` · `field trials internos`.

**Consequência dura:** nenhuma saída pode afirmar `REVENUE`, `MARGIN`, `SALES` ou
`ROI REALIZED`. Não porque falte esforço — porque falta o dado, por decisão do cliente.

### O valor externo tem de ser defendido por estas seis coisas, e só por elas

| valor | estado hoje |
|---|---|
| **BETTER PRIORITIZATION** | **provado** — MT2 ordena províncias por exposição relativa |
| **FASTER RESEARCH** | **parcial** — ganho real, medição de tempo declarada inválida (ver §M) |
| **FALSE-SIGNAL AVOIDANCE** | **provado** — é o que o sistema mais faz bem (CASE-008, X-009) |
| **EXTERNAL OPPORTUNITY DISCOVERY** | parcial |
| **BETTER TIMING** | **só onde medido** — sobrevive em expiry regulatório; **não** sobrevive em voz |
| **CONNECTED CONTEXT** | provado |

---

## C · CONTRATO COM A APRESENTAÇÃO ORIGINAL

O deck do cliente é **contrato de prova**, não inspiração. Ele prometeu:

```
LOCAL SIGNALS → CONNECTED CONTEXT → BETTER TIMING
Listen → Understand → Connect → Deliver
FACT → INTERPRETATION → ACTION
```

E seis frentes: Market Development · Regulation & Portfolio · Molecule & Competitive ·
Competitor Communication · Marketing Opportunity · Ask Sintonia.

Placar atual em `docs/apresentacao/MATRIZ-DE-PROVA-EAME.md`:
**9 PROVED · 14 PARTIAL · 6 UNPROVED · 1 NOT_TESTABLE.**

### Onde BETTER TIMING sobreviveu, e onde não

**SOBREVIVEU — regulatório.** É a única antecipação temporal forte que temos. O vencimento
de registro é uma data pública futura: 486 registros vencem em ≤6 meses, 1.004 em ≤12.
Isso é antecipação real e verificável.

**NÃO SOBREVIVEU — voz pública.** Medido e reprovado, duas vezes:
- `ES-X-VOICE-FIELD.json` → **`NO_RELIABLE_SIGNAL`**. O coeficiente mais alto (ρ 0,442, voz
  antecipando o campo em uma safra) **não passa** do crítico de Spearman a 5% com n=10
  (≈0,648), e os sinais se invertem entre defasagens.
- `BACKTEST-REPILO-LEAD-TIME.json` → lead time de 1 safra no melhor caso, **0 em duas de três**.

**NÃO SOBREVIVEU — campo como alerta precoce geral.** `FIELD PRESSURE ≠ ALERTA ANTECIPADO
DE 6-12 MESES` é lei, não opinião.

---

## D · PORTA CANÔNICA DE ARQUITETURA

**`docs/piloto/ARQUITETURA-DE-PRODUTO-ATUAL.md` é o dono.** Verificado no HEAD atual: o
próprio documento diz *"se dois documentos discordarem sobre o que é o produto, este vence"*.

| documento | estado para design |
|---|---|
| `docs/piloto/ARQUITETURA-DE-PRODUTO-ATUAL.md` | **CURRENT — manda** |
| `docs/ferramentas/ARQUITETURA-DE-INFORMACAO-EAME.md` | **OBSOLETE_FOR_DESIGN** — descreve informação disponível, correto nisso; **não** são nove telas |
| `docs/piloto/ENTRADA-PARA-CLAUDE-DESIGN.md` | CURRENT **como pacote de fatos e números**, não como arquitetura |
| `docs/descoberta/MISSAO-EAME-01.md`, `SEGUNDA-PASSAGEM…`, `LACUNAS-E-VEREDITO-MISSAO-03.md` | **HISTORICAL** — registro de missão, não estado |
| `docs/piloto/VEREDITO-M10-HANDOFF.md` | CURRENT para o veredito de M10 |
| `docs/operacao/PORTOES-DE-COLETA-10B.md` | **CURRENT** — o estado mais recente |

**Nunca voltar para a arquitetura de 18 ferramentas.** Foi reduzida deliberadamente.

---

## E · ARQUITETURA ATUAL — verificada contra o HEAD

Três ferramentas, não um menu:

- **MT1 · REGULATORY & EXPIRY EXPOSURE** — a mais madura. Vencimento por empresa e molécula.
- **MT2 · GEOGRAPHIC COMMERCIAL PRIORITY** — ordena províncias por índice de exposição.
- **MT3 · PUBLIC ACTIVATION GAP** — **exploratória**, e o documento é explícito: apresentar
  MT3 como *oportunidade* é erro; ela é uma **`ACTIVATION QUESTION`**.

**ASK SINTONIA** é a interface e o contrato de aceitação, **não** uma quarta ferramenta e
**não** uma money tool.

**Camadas de apoio:** SCIENCE · EXPERTS · CLIMATE · ENTITY IDENTITY · CROP/MARKET CONTEXT ·
EVIDENCE · VOICE.

---

## F · ESTADO DA ESPANHA — números derivados do ledger

> Todos abaixo saem de `python3 scripts/metricas_canonicas.py`. **Se divergirem, o ledger
> vence e o documento está velho.**

### VÍDEO — `ES-T8-001`
252 conteúdos · **157 origens** (canais) · 2010–2026 · **67 vídeos ≥15 min**
15 transcrições preservadas, **705.149 caracteres**
Tipos: OTHER 137 · CONFERENCE 46 · TECHNICAL_WEBINAR 20 · MEDIA 15 · RESEARCH_TALK 10 ·
PROMOTIONAL 10 · PRODUCER_VOICE 8 · FIELD_DAY/FIELD_OBSERVATION/COOPERATIVE_CONTENT 2 cada
Originalidade: **241 UNKNOWN · 9 SYNDICATED · 2 RESHARE · nenhum ORIGINAL**

### COMENTÁRIOS — 346
154 com conteúdo classificável (**44,5 %**) · **148 perguntas** · **22 observações de campo**
**Conclusão que muda o uso da camada:** comentário de YouTube no olivar espanhol mede
**demanda por informação técnica**, não estado do campo. Usá-lo como sensor de campo é ler a
pergunta como se fosse resposta.

### LINKEDIN — `ES-T8-002`
202 perfis enriquecidos · 179 declaram ES · cobertura de papel **67 %**
472 posts brutos → **372 únicos** (100 duplicatas por `POST_ID`) · 221 origens
**67 PUBLIC_TECHNICAL_VOICE**, das quais **16 com tópico OLIVE** — este é o número acionável
**Limitações:** `COUNTRY` só do campo declarado; papel só de campo estruturado; 42 origens
ficam `NOT_DECLARED` e isso é honesto, não falha.

### INSTAGRAM — `ES-T8-003` · **FAILED_WITH_REASON**
39 de 60 itens agronômicos — reprovado mesmo assim. **24 de 32 contas não declaram país**,
3 declaram fora da Espanha, **5 declaram Espanha**.
`#repilo` está **100 % capturada** por `repilouk`, empresa britânica de gestão de avaliações.
**O nome de uma doença também pode ser uma marca.**

### CIÊNCIA — `ES-T5-002`
**1.771 documentos** com 16 campos · **9.958 autores distintos** · 380 instituições ·
**152 pesquisadores** (eram 153 — ver §G)

### MÍDIA TÉCNICA / ASSOCIAÇÕES — `ES-T7`
**8 de 18 rotas provadas.** Seis devolveram **HTTP 200 com zero `<item>`** (são páginas HTML,
não feeds). Três têm certificado que não valida — registrado como **estado da fonte**;
a verificação TLS **nunca** foi desligada.

---

## G · PESQUISADORES / CIÊNCIA

**Como foram encontrados:** OpenAlex, rota REST gratuita e sem chave, filtro
`institutions.country_code:es` + `publication_year:2019-2026`, **12 temas declarados**, cada
um com `CROP` e `ISSUE` explícitos na consulta. Isso importa: **`CROP` e `ISSUE` de cada
documento vêm da consulta que o trouxe, não de leitura livre do título.**

Inclusão no quadro: ≥5 trabalhos no escopo · ORCID presente · ao menos um tema de olivar.

### O caso do ID conflacionado — a lição mais cara desta camada

`Nikolaos Papadopoulos` estava no quadro, **em primeira posição**, com **58 organizações
declaradas contra mediana 2** (segundo maior: 7), 72 trabalhos cobrindo *todas* as culturas
e quase todos os temas, e **os dois identificadores nulos**.

Não é um pesquisador prolífico. É um **ID de autor do OpenAlex que juntou homônimos**.

**Pior:** o campo `IDENTITY_CAUTION` do próprio arquivo já dizia que ele havia sido excluído.
Estava dentro. **O texto contradizia o dado.**

> **`CONTAGEM ALTA NÃO VALIDA IDENTIDADE.`** Número de organizações muito acima da mediana do
> quadro é sintoma de conflação, e virou vigia: `VOICE_ES_RESEARCHER_MAX_ORGS` está no ledger
> com a mediana no denominador.

### `REGION_OF_STUDY ≠ AUTHOR AFFILIATION`

`REGION_OF_STUDY` é **0 % em 1.771 de 1.771** e isso está certo: o campo não existe no
registro, e a afiliação do autor **não** é o local do experimento. Um trabalho sobre olivar
marroquino assinado por alguém de Córdoba continua sendo Córdoba na afiliação.

### `SCIENCE → RESEARCHER → PUBLIC VOICE` = **`NOT_REACHED`**

Testado em `ES-X-VOICE-SCIENCE.json`: 152 pesquisadores × 202 origens LinkedIn × 157 canais
YouTube → **1 candidato por nome, nenhum confirmado.**

Por instituição, o casamento estrito deu **zero** (o OpenAlex escreve *"Instituto de
Investigación y Formación Agraria y Pesquera"*, a plataforma escreve *"IFAPA TV"*), e o
casamento frouxo produziu **falso positivo demonstrável**: *"Instituto de Agricultura
Sostenible"* casou com UPL e BURGOS SALAVERRY; *"Universitat de Barcelona"* casou com uma
unidade de pesquisa em **tuberculose**.

**A rota não está refutada — ela não se constrói com nome.** Falta um **identificador
declarado que atravesse camadas** (ORCID, ROR). A ciência já tem; as plataformas públicas não
publicam nenhum dos dois.

---

## H · VOICE — incluindo o que deu errado

| camada | estado | o que ficou provado |
|---|---|---|
| **VÍDEO** | PROVED | melhor custo por conteúdo técnico de toda a rodada |
| **LINKEDIN** | PROVED (identidade) / PARTIAL (conteúdo) | é o que resolve país e papel |
| **COMENTÁRIOS** | PROVED como coleta | mede **demanda por informação**, não campo |
| **INSTAGRAM** | **FAILED_WITH_REASON** | volume não compensa identidade ausente |
| **COOPERATIVAS** | PARCIAL | 2 COOPERATIVE + 1 PRODUCER_ORGANISATION verificadas |
| **VOZES TÉCNICAS** | PROVED | 67 verificadas, 16 de olivar |
| **VOZ DE CONCORRENTE** | PARTIAL | 11 origens, 26 posts — **denominador é o recorte, não a empresa** |
| **MÍDIA TÉCNICA** | PARTIAL | 8 de 18 rotas |

### Resultados negativos que NÃO podem ser apagados

1. **A voz não antecipa no tempo.** `NO_RELIABLE_SIGNAL`.
2. **A ciência não se liga à voz por nome.** `NOT_REACHED`.
3. **O Instagram falha na identidade, não no volume.**
4. **A correção do concorrente:** publicamos 14 origens / 54 posts. O correto é **11 / 26**.
   Duas causas distintas: 100 posts duplicados por falta de chave estrutural, e **três
   funcionários (FMC, UPL, BASF) contados como se fossem o canal da empresa** porque o
   *headline* deles nomeia o empregador.

---

## I · VOICE × FIELD

**Testado:** share do tema por ano na voz × incidência média ponderada de repilo (RAIF).
**Denominador:** os vídeos **daquele ano** — não a contagem bruta.
**n:** 11 anos com ≥8 vídeos.

| defasagem | ρ |
|---|---:|
| mesmo ano | 0,300 |
| voz[t] × campo[t+1] | **0,442** |
| voz[t+1] × campo[t] | −0,600 |
| voz[t] × campo[t+2] | 0,250 |

**Veredito: `NO_RELIABLE_SIGNAL`.** Com n=10 o crítico de Spearman a 5 % é ≈0,648. Nenhum
chega lá, e os sinais **se invertem** entre defasagens — padrão de estimativa instável.

**Duas armadilhas que valem para qualquer país:**
1. **A contagem bruta de vídeos por ano não mede atenção — mede o que a rota alcança.**
   26 vídeos até 2015 contra 226 depois. Correlacionar isso mediria o crescimento do YouTube.
2. **O coeficiente mais alto era publicável e estava errado.**

### O que sobrevive: concordância geográfica

| camada | ρ vs incidência | ρ vs área | ρ vs **índice de exposição** |
|---|---:|---:|---:|
| YouTube (n=8) | 0,214 | 0,607 | **0,964** |
| LinkedIn, rota de posts (n=6) | 0,543 | 0,543 | **0,943** |

Duas camadas independentes concordam com a **exposição**, não com a incidência isolada.

**`CONCORDÂNCIA GEOGRÁFICA ≠ ANTECIPAÇÃO TEMPORAL.`**

**Confundidor aberto — Córdoba.** Córdoba concentra IAS-CSIC, a Universidade de Córdoba e a
ETSIAM. **Densidade institucional é explicação rival** para Córdoba liderar a voz, e ela
**não** foi separada da exposição agronômica. Isto continua aberto.

**Só a rota de posts entrou na correlação.** A rota de cargo pediu "Andalusia" em parte das
consultas; correlacioná-la mediria o desenho da consulta. Seria circular.

---

## J · FIELD / RAIF — `ES-T3-001`

**23 safras · 2003–2026 · 148.964 leituras.**

### As correções históricas que a próxima conta não pode desfazer

- A MISSÃO 02 leu só os três arquivos modernos e publicou **"11 safras"**. O pacote traz
  também oito arquivos por província com 2003–2016. São **23**.
- **Cádiz 2026 (8,01 %) NÃO é o máximo da série.** Cádiz teve 9,71 em 2013, 8,40 em 2010.
- **Huelva 2026 (8,83 %) É o máximo de toda a série.**
- **Sevilla ganhou peso** quando o denominador de escala entrou: incidência 2,74 % sobre
  253.293 ha pesa mais que incidência alta em área pequena.

**Campo 1702 = repilo VISÍVEL. Campo 1703 = repilo INCUBADO.** São medidas diferentes.

**`FIELD PRESSURE ≠ DEMAND.`** Pressão de doença não é demanda comercial.

---

## K · CROP SCALE / DENOMINADORES

Área de olivar por província: MAPA, Anuário 2024, planilha
`re1_olivar_formato_tabla_global.xlsx`, aba `BD_HORTALIZAS-NO`, indicador SRTT.
Andaluzia total: **1.665.100 ha**. Jaén 589.047 · Córdoba 376.967 · Sevilla 253.293.

**O denominador inverteu a prioridade.** Por incidência isolada, Cádiz e Huelva lideram. Por
`ha × incidência`, Córdoba e Sevilla passam à frente. **A pergunta decide o eixo.**

### `ha × incidência` é `RELATIVE EXPOSURE INDEX` e nada mais

**NÃO é:** hectares afetados · hectares tratados · vendas · demanda · mercado endereçável.
**É:** um número que **ordena** províncias. Nunca dimensiona.

**Cautela obrigatória:** as parcelas do RAIF **não são amostra aleatória**. São parcelas de
acompanhamento escolhidas pela rede. A média nunca viaja sem o `n`, e a coorte (mesmas
parcelas ao longo dos anos) existe justamente para controlar artefato de amostragem.

---

## L · REGULATORY — `ES-T4-005`

Registro espanhol ROPF: **3.084 registros, 1.993 em vigor**, ADAMA **96 em vigor**.

| | total | ADAMA |
|---|---:|---:|
| vencendo em ≤6 meses | **486** | **36** |
| vencendo em ≤12 meses | **1.004** | **61** |
| `Vigente` com caducidade anterior à captura | **34** | **3** |

Aqueles 34 são o achado mais interessante: **`Vigente` com data de caducidade já passada.**
Não invente explicação — é `INVESTIGATE`.

**`EXPIRY ≠ WITHDRAWAL`.** Vencimento de registro não é retirada de produto, não é perda de
mercado, não é decisão comercial.

### Neptune `ES-00211`

```
REGISTERED RESPONSE EXISTS   = YES
CURRENT COMMERCIAL AVAILABILITY = NÃO SEI
REGULATORY INTERPRETATION    = INVESTIGATE
```

**`REGISTRATION ≠ COMMERCIAL AVAILABILITY`.** Ter registro não prova que o produto está à
venda.

---

## M · MONEY TOOLS / BUSINESS CASE

| | estado |
|---|---|
| `PRODUCT_READINESS` | **READY FOR DESIGN** |
| `BUSINESS_CASE` | **PROMISING BUT UNPROVEN** |
| `RESEARCH_SAVING` | **PARCIAL** — ganho real, relógio inválido |
| `ECONOMIC_VALUE` | **NÃO PROVADO** |

**Por que o business case não está provado:** valor econômico exigiria dados internos que
**não virão**. O caso externo é defensável por priorização, velocidade e recusa de sinal
falso — não por receita.

**O que derrubou ambições anteriores:**
- **A medição de tempo do benchmark foi declarada INVÁLIDA por mim mesmo**, porque eu era o
  analista manual e o comparativo. Ver `PROTOCOLO-BENCHMARK-RESEARCH-SAVING.md`.
- O backtest de lead time deu **1 safra no melhor caso e 0 em duas de três**.
- `Ask Sintonia` foi retirado da lista de money tools: é interface, não gerador de valor.

---

## N · ASK SINTONIA

**`scripts/ask_sintonia.py`** tem **5 perguntas executáveis** — funções `q1`…`q5`
(verificado: `grep -n "^def q" scripts/ask_sintonia.py`). Cada uma devolve `ANSWER` ·
`EVIDENCE` · `SOURCE` · `WHAT_IS_FACT` · `WHAT_IS_DERIVED` · `WHAT_IS_UNKNOWN` ·
`CONFIDENCE`.

**As 35 perguntas são um CONTRATO DE ACEITAÇÃO avaliado manualmente — não 35 respostas
executadas automaticamente.** Resultado: **20 respondidas · 14 recusadas · 1 parcial ·
0 erradas.**

**As 14 recusas são parte do valor, não falha.** Um sistema que responde tudo é um sistema
que inventa. `ASK_WRONG = 0` é a métrica que importa.

---

## O · LEIS EPISTÊMICAS — não reabrir sem evidência nova

```
SOURCE ≠ EVIDENCE
FACT ≠ INTERPRETATION ≠ ACTION
NAME ≠ HANDLE ≠ URL ≠ PROFILE ≠ PERSON ≠ ORGANIZATION
SOURCE_LOCATION ≠ FACT_LOCATION ≠ ORIGINAL_LANGUAGE
REGISTRATION ≠ SALES
REGISTRATION ≠ COMMERCIAL AVAILABILITY
EXPIRY ≠ WITHDRAWAL
FIELD PRESSURE ≠ DEMAND
VOICE ≠ DEMAND
DISCUSSION ≠ SALES
ENGAGEMENT ≠ INFLUENCE
FOLLOWERS ≠ AUTHORITY
PUBLIC SILENCE ≠ COMMERCIAL SILENCE
SOURCE FAILURE ≠ ZERO
NOT COLLECTED ≠ DOES NOT EXIST
FIRST SNAPSHOT ≠ NO CHANGE
CURRENT ≠ HISTORICAL
PLATFORM ≠ CONTENT FORMAT
ORIGIN ≠ CHANNEL ≠ CONTENT
CORRELATION ≠ CAUSALITY
GEOGRAPHIC CONCORDANCE ≠ TEMPORAL ANTICIPATION
HTTP 200 ≠ FONTE VIVA
SUCCEEDED DA PLATAFORMA ≠ EXECUÇÃO BEM-SUCEDIDA
COBERTURA ALTA ≠ COBERTURA CORRETA
```

Cada uma custou uma medição. Reabrir sem evidência nova é refazer o erro.

---

## P · IDENTIDADE

`ORIGIN_ID` · `CHANNEL_ID` · `CONTENT_ID` · `PERSON_ID` · `ORG_ID` são **entidades
distintas**. Documento dono: `docs/regras/MODELO-DE-IDENTIDADE-EAME.md`.

- **Uma pessoa em três plataformas = UMA ORIGEM** com três evidências.
- **157 canais publicaram 252 vídeos** = 157 origens, 252 conteúdos. Nunca se somam.
- **Conteúdo sindicado não vira múltiplas evidências independentes.**
- **`OpenAlex author ID pode conflacionar homônimos`** — medido, 58 organizações.
- **`linkedin.com/company/adama/` devolve uma incorporadora imobiliária romena.** Casar nome
  entrega a entidade errada.

### O papel nunca sai do conteúdo

Para **página**: `companyType` + `pageType` + `industries`.
Para **pessoa**: `headline` + cargo atual declarado.
**Nunca:** nome da conta · foto · estilo · idioma · **prosa livre**.

**Por que a prosa livre está proibida** — três erros medidos em 40 perfis: `Oleo Revista`
virou RESEARCHER porque "investigador" aparecia numa notícia citada; `ASCENZA` virou
RESEARCH_INSTITUTION porque o token `imida` casou **dentro de "ftalimida"**; pessoas viraram
COMPANY por trabalharem numa S.L. Aquele classificador reportava **100 % de cobertura**.
Trocado pelos campos estruturados, o número verdadeiro apareceu: **67 %**.

**O custo da regra, pago à vista:** o `Grupo de Aerobiología. Universidad de Córdoba`
publicou o post mais relevante de todo o corpus — detecção de esporos de *Venturia
oleaginea* — e tem `headline` vazio. Sai como `NOT_DECLARED`. **O nome não decide papel, nem
quando o nome está certo.**

---

## Q · DEDUPE

**Chave estrutural, sempre:** `PLATFORM + EXTERNAL_ID` · `VIDEO_ID` · `POST_ID` ·
`COMMENT_ID`.

**NUNCA usar como chave primária:** texto, título, similaridade textual, hash de conteúdo.
Dois comentários "Gran video" são dois comentários reais. Dois vídeos com o mesmo título em
canais diferentes são dois vídeos.

**O que está provado (10B-ES):** `voz.pipeline_video()` invoca o dedupe e publica
`RAW_COUNT` / `DUPLICATE_COUNT` / `UNIQUE_CONTENT_COUNT` com a relação duplicata→canônico
preservada. Teste **ponta a ponta** em `tests/test_pipeline.py` com fixture mínima.

**O custo de não ter tido isso:** 100 de 472 posts do LinkedIn eram o mesmo `POST_ID`.

> **`DUPLICATE_COUNT = 0` na camada de vídeo é verdade e por isso mesmo não prova nada.** O
> portão **exerce** o dedupe num caso conhecido em vez de confiar num zero.

---

## R · DATA CLOCK

`scripts/data_clock.py` → `data/samples/DATA-CLOCK-manifest.json`.

Registra por arquivo: `SOURCE_ID` · `VERSION_DATE` · `COLLECTION_DATE` · `SIZE_BYTES` ·
**`SHA-256`** · `ARCHIVING_URGENCY`.

**Granularidade:** por arquivo, e **por canal** na camada de voz —
`ES-T8-001-baseline-canais.json` dá baseline aos **157 canais**, porque um baseline agregado
não detecta `NEW_VIDEO` de um canal específico. 252 continua 252 se um canal publicar três e
outro sumir com três.

**Primeira observação é sempre `BASELINE_ESTABLISHED`, nunca `NO_CHANGE`.** Não se declara
ausência de mudança contra um baseline que não existia.

**Urgência `CRITICA`** é categoria nova e existe só para o bruto de rota paga: perder a versão
de hoje não custa histórico, custa **a evidência inteira**.

---

## S · APIFY — política permanente

Documento dono: `docs/regras/POLITICA-DE-CHAVES-DESCARTAVEIS.md`.

Chave enviada pelo Luciano é **autorizada, descartável, ≈US$5**, cada uma um **orçamento
independente**. Pode gastar todo o saldo útil **sem pedir autorização de novo**. Exposição da
chave no contexto **não** bloqueia a missão. Quando o crédito acaba, a chave está encerrada.

**A chave nunca vai para arquivo versionado, commit, README, documentação, fixture ou
relatório.** Há teste que varre o repositório atrás de padrão de token.

### Actors testados, com o que aprendemos

| Actor | custo | qualidade | **identidade** | transcript | atualização |
|---|---|---|---|---|---|
| `harvestapi/linkedin-profile-search` | US$0,004/perfil | 10/10 com cargo técnico | **FORTE** | n/a | contínua |
| `harvestapi/linkedin-profile-scraper` | US$0,004/perfil | 202 perfis, 179 com país | **FORTE** — é o que resolve país e papel | n/a | contínua |
| `harvestapi/linkedin-post-search` | por evento | 472→372 únicos | **FRACA** — 46 % das origens são páginas de empresa | n/a | `postedAt` absoluto ✅ |
| `streamers/youtube-scraper` | por evento | 252 vídeos, 27 de 32 campos | MÉDIA | ✅ | `date` absoluto ✅ |
| `pintostudio/youtube-transcript-scraper` | por evento | 15 de 20 alvos | n/a | ✅ | n/a |
| `streamers/youtube-comments-scraper` | por evento | 346, 44,5 % com conteúdo | **AUSENTE** — só handle | n/a | ❌ **só tempo relativo** |
| `apify/instagram-hashtag-scraper` | por evento | 39/60 agronômicos | **AUSENTE** — 24/32 sem país | n/a | `timestamp` ✅ |

**A dimensão que decide é identidade, nas duas direções.** O Instagram foi reprovado apesar de
65 % de itens agronômicos; a busca por cargo foi escalada apesar de não trazer conteúdo nenhum.

### Limites medidos da plataforma

- **Plano gratuito: 10 itens por execução** no enriquecimento → 12 lotes de 10.
- **`harvestapi` limita contas gratuitas a 10 execuções por ator.** Ao estourar, o ator devolve
  **`SUCCEEDED`, `exitCode` limpo e ZERO itens**, com `statusMessage: "free user run limit
  reached"`. **Cota esgotada que se apresenta como sucesso.** O coletor agora trata isso como
  `PARTIAL`.
- **Consulta sobre-restrita devolve 0**, e isso é o comportamento correto — falha fechada.
- `run-sync` expira; use `nohup` + gravação incremental para execuções longas.

---

## T · FONTES / ATLAS

Documento dono: `docs/fontes/ATLAS-DE-FONTES-EAME.md`.
**36 SOURCE_IDs · 26 fichas · 16 GREEN · 4 YELLOW · 0 RED · 16 NÃO SEI.**

### As que a próxima conta precisa conhecer primeiro

| SOURCE_ID | o que é | por que importa |
|---|---|---|
| `ES-T3-001` | RAIF Andaluzia | única série de campo com 23 safras |
| `ES-T4-005` | ROPF, registro espanhol | MT1 inteira depende dele |
| `ES-T5-002` | OpenAlex, recorte espanhol | ciência e pesquisadores |
| `ES-T8-001/002/003` | vídeo · LinkedIn · Instagram | camada de voz |
| `EU-T4-001` | CELEX / Jornal Oficial | camada regulatória europeia |
| `FR-T4-001` / `IT-T4-001` | registros FR e IT | cross-market por molécula |

---

## U · AUDITORIA ADVERSARIAL

**Resultado (contra `3a2659c`, antes dos portões):** **206 achados · 68 ATENDIDO ·
91 PARCIAL · 47 NAO_ATENDIDO**, e **91 classificações foram corrigidas pela fase de
refutação** — nos dois sentidos: desmentindo conformidade inexistente **e** desmentindo
lacunas inventadas. Artefato: `data/samples/AUDITORIA-REGRA-COLETA-EXTERNA.json`.

### O erro metodológico, que é meu e está assumido no artefato

**A auditoria correu contra um repositório EM MOVIMENTO** — oito commits entraram enquanto
ela lia. Um auditor afirmou que a regra não existia em `docs/regras/` e listou 4 arquivos
onde havia 5, porque leu **antes** do commit que a criou.

**Nova regra, implementada em `scripts/auditoria.py`:** `AUDIT_TARGET_SHA` é definido antes;
o auditor lê um **worktree `--detach`**. Se o SHA auditado mudar, a auditoria é
**INVÁLIDA — não "com ressalva"**. Quatro modos de invalidação, todos testados.

> ### **47 NAO_ATENDIDO ≠ 47 tarefas obrigatórias.**
> Vários são decisão de escopo, e alguns custam mais do que valem. O backlog garante que
> nenhum seja **esquecido por acidente** nem **dado como coberto sem estar**.

### Verificação adversarial dos seis portões — **NÃO CONCLUÍDA**

Lancei uma verificação adversarial dos seis portões contra o SHA congelado `a79f434`.
**Ela não terminou antes do fim dos créditos.** Não há resultado, e nada neste documento
depende dela. O snapshot pode ter sido reciclado com o contêiner.
**A próxima conta deve refazê-la contra o HEAD de handoff, não confiar em resultado ausente.**

---

## V · BACKLOG DOS 47 — estado verificado hoje

| item | estado |
|---|---|
| taxonomia de vídeo não aplicada aos 252 | **FECHADO** — 252/252 classificados |
| `ORIGINALITY` ausente | **FECHADO** — 241 UNKNOWN · 9 SYNDICATED · 2 RESHARE |
| `RAW_EVIDENCE` de rotas pagas | **FECHADO** — 8,8 MB preservados em 2,1 MB |
| `RUN_ID` sem manifesto de execução | **FECHADO** — `RUN-MANIFEST.json`, 22 campos |
| dedupe existe mas pipeline não chama | **FECHADO** — `pipeline_video()` + teste ponta a ponta |
| id conflacionado no quadro de pesquisadores | **FECHADO** — 153 → 152 |
| denominador publicado ≠ usado | **FECHADO** |
| corpus científico só agregado | **FECHADO** — 1.771 documentos com 16 campos |
| ficha de fonte da camada científica | **FECHADO** — `ES-T5-002` no Atlas |
| camada de voz fora do Data Clock | **FECHADO** |
| **researchers public voice não testado** | **ABERTO** — fila de 20 pronta, 132 `NOT_TESTED` |
| **LinkedIn Video / Instagram Reels** | **ABERTO** — fora de escopo por decisão |
| **competitor × video** | **ABERTO** — o cruzamento só existe na camada LinkedIn |
| **crosswalk ciência↔voz** | **ABERTO** — exige identificador, não algoritmo |
| **`ORGANIZATION_ID` / `SAME_AS` entre origens** | **ABERTO** |
| **4 tipos de documento sem fonte** | **ABERTO** — relatório técnico, projeto, publicação institucional, extensão |

---

## W · BRASIL → EAME

Repositório: **`lucianodalondon-sys/portal-sintonia`**.

**A ponte NÃO foi executada.** Nada dela foi medido nesta conta. O que segue é a hipótese
registrada, não um resultado.

O objetivo **não** é copiar schema nem código. É transferir **leis, invariantes,
contraexemplos, testes e padrões de pipeline**.

Aprendizados do Brasil já identificados para comparação:

```
NOME NUNCA É ENDEREÇO
platform + external_id para identidade estrutural
duplicata marcada ≠ duplicata viva
PLATFORM ≠ FORMAT
não coletei ≠ não existe
publication clock ≠ collection clock
custo sem coleta_id = NÃO SEI
função testada mas não chamada pelo pipeline = sistema não provado
MEDIR → DRY RUN → DECIDIR → APLICAR
```

**Nota:** "função testada mas não chamada pelo pipeline" foi **exatamente** o defeito que a
auditoria encontrou no EAME e que a missão 10B fechou. Isso é evidência de que a ponte vale.

**Esta ponte deve ser medida contra SHAs congelados dos dois lados.** Não declare que foi
executada.

---

## X · DESIGN

- **ADAMA Design System** = fundação da marca. **Não inventar tokens oficiais.**
- **Deck EAME** = direção de modernização.
- **Sintonia** = produto de inteligência contemporâneo **dentro** do universo ADAMA.

**Design PODE afirmar:** três ferramentas (MT1/MT2/MT3) + Ask como interface; que toda saída
separa `FACT` / `INTERPRETATION` / `ACTION`; que ausência aparece como ausência.

**Design NÃO PODE afirmar:** 18 dashboards; que MT3 é oportunidade (é `ACTIVATION QUESTION`);
qualquer número que não esteja no ledger; qualquer promessa de receita, margem ou market share.

Pacote de fatos: `docs/piloto/ENTRADA-PARA-CLAUDE-DESIGN.md`.

---

## Y · DECISÕES ENCERRADAS — não reabrir

Verificadas hoje, todas continuam válidas:

1. **Dados internos da ADAMA não virão.** External-only é **definitivo**.
2. **Campo não é early warning geral.**
3. **Expiry regulatório é a antecipação temporal mais forte que temos.**
4. **`Ask Sintonia` não é money tool** — é interface e contrato de aceitação.
5. **Instagram não vira prioridade por volume.** Reprovado por identidade.
6. **Followers não definem authority.** `INFLUENCER = AUTHORITY` não existe no modelo.
7. **França e Itália não se misturam com a Espanha** antes do fechamento do país.
8. **Cross-market vem depois das camadas nacionais**, e **por molécula** (X-006 cobre 82,1 %
   do uso; X-007 cobre 23,5 %).
9. **Não voltar para 18 ferramentas.**
10. **A regra de identidade não se flexibiliza para melhorar cobertura.**

---

## Z · SE EU FOSSE A PRÓXIMA CONTA — o que não está óbvio no código

### Arquivos em que eu confio mais
`data/samples/*.json` com envelope de proveniência. `scripts/metricas_canonicas.py` — **é a
fonte de verdade dos números**, e há teste que reprova documento com número divergente.
`tests/` inteiro: <!--M:TEST_COUNT_CURRENT-->329<!--/M--> testes que codificam as leis, não só o comportamento.

### Documentos que envelhecem rápido
Qualquer `.md` com número digitado sem marcador `<!--M:NOME-->`. Os documentos de missão
(`MISSAO-EAME-01`, `SEGUNDA-PASSAGEM`) são registro histórico e **envelheceram de propósito**.

### Onde os números divergem
**Sempre no mesmo lugar: contagem de testes, contagem de fontes, e contagem de origens vs
conteúdos.** Por isso o ledger existe. Rode `python3 scripts/metricas_canonicas.py --sync`
depois de qualquer mudança e a suíte reprova se algo ficou para trás.

### Bugs que se repetiram — os mesmos três, várias vezes
1. **Acento em regex.** `agronom` não casa "agrónomo". Custou uma classificação inteira.
2. **Campo que é lista de dicionários tratado como lista de strings.** `industries` foi
   silenciosamente descartado por um `isinstance(i, str)`.
3. **Número digitado num documento que envelhece.** Resolvido pelos marcadores de sync.

E um quarto, mais perigoso: **cobertura que sobe porque o classificador ficou permissivo.**
Aconteceu duas vezes (denominações espanholas 96,9 % falso; papel LinkedIn 100 % falso).
**Cobertura alta é suspeita, não conquista.**

### Inferências sedutoras já derrubadas
- "A voz antecipa o campo" — ρ 0,442 parecia bonito. Não passa do crítico.
- "A ciência liga à voz por nome" — produz falso positivo demonstrável.
- "O clima explica a doença" — X-009 refuta.
- "Contagem de registros é participação de mercado" — não é.
- "Estar no canal da empresa prova originalidade" — não prova.

### Onde a próxima conta provavelmente erraria
1. **Confiar num HEAD de memória.** Meça sempre.
2. **Auditar árvore em movimento.** Use `scripts/auditoria.py`.
3. **Tratar os 47 NAO_ATENDIDO como lista de tarefas.**
4. **Reconstruir o corpus científico** achando que não existe — existe, em
   `ES-T5-002-corpus-documentos.json`.
5. **Gastar chave paga refazendo o que já está preservado** em `data/samples/raw-paid/`.
6. **Escrever número em documento sem marcador de sync.**

### Fontes que entregaram inteligência real
**RAIF** (23 safras, coorte), **ROPF** (vencimentos, 34 anomalias), **OpenAlex** (1.771
documentos com identificador estável), **YouTube com transcrição** (705 mil caracteres),
**LinkedIn profile-search por cargo** (identidade forte).

### Fontes que entregaram ruído
**Instagram** (identidade ausente, homônimo comercial), **LinkedIn post-search** para
identidade (favorece página de empresa), **comentários** como sensor de campo (são perguntas),
**sites institucionais de concorrente** (403/502/404 desde a MISSÃO 03).

### Relações mais valiosas
`área × incidência` → ordena províncias. `substância normalizada` → atravessa mercados (82,1 %
do uso). `vencimento × titular` → antecipação real.

### Métricas bonitas e não defensáveis
"67 vozes técnicas" (o acionável é 16). "2,45× de inflação de mercado" (recusada por não
medir o que 1.737 e 708 contam). Qualquer ρ com n<10. "100 % de cobertura" em identidade
pública.

### Onde temos mais vantagem
**Recusar sinal falso com evidência.** Nenhum concorrente de dashboard faz isso. `ASK_WRONG=0`
com 14 recusas em 35 é o ativo mais forte do produto.

### Onde o produto ainda está fraco
**MT3** (exploratória). **Voz** (não antecipa). **Business case econômico** (não provado, e
não será sem dado interno). **Cobertura fora da Andaluzia** (campo só existe lá).

### Se eu tivesse mais 24 horas
1. Terminar a verificação adversarial dos seis portões contra SHA congelado.
2. Executar a fila de 20 pesquisadores — é a única coisa que pode fechar
   `SCIENCE → PUBLIC VOICE`, e a fila já está pronta.
3. Construir o crosswalk ORCID/ROR ↔ plataforma, manual, para 20 pessoas.

### O que eu NÃO faria
Abrir França ou Itália. Coletar Instagram. Aumentar o corpus de vídeo sem antes usar o que já
tem. Criar tipo novo de vídeo para reduzir `OTHER`. Tentar provar valor econômico.

### A pergunta mais importante ainda aberta

> **A concordância geográfica entre voz e exposição (ρ 0,96 e 0,94) é sinal agronômico ou
> artefato de densidade institucional?**

Córdoba concentra IAS-CSIC + UCO + ETSIAM **e** lidera a voz. Enquanto esse confundidor não
for separado, MT2 apoiada em voz é **corroboração**, não prova. Separá-lo provavelmente exige
normalizar menções por densidade de instituições por província — o dado existe no corpus
científico (380 instituições com afiliação declarada).

---

## AA · MAPA DE ARQUIVOS — ler nesta ordem

| # | PATH | PURPOSE | ESTADO | POR QUE IMPORTA |
|---|---|---|---|---|
| 1 | `HANDOFF-CONTA-CLAUDE-SINTONIA-EAME.md` | este documento | CURRENT | mapa da casa |
| 2 | `docs/piloto/ARQUITETURA-DE-PRODUTO-ATUAL.md` | o que o produto É | **CURRENT — manda** | se dois documentos discordam, este vence |
| 3 | `docs/regras/MODELO-DE-IDENTIDADE-EAME.md` | identidade de entidade e de origem | CURRENT | quase todo erro grave veio daqui |
| 4 | `docs/regras/REGRA-DE-COLETA-EXTERNA-EAME.md` | como coletar | CURRENT | prioridade, contratos de campo, fail closed |
| 5 | `docs/operacao/PORTOES-DE-COLETA-10B.md` | os seis portões | CURRENT | diz se pode coletar |
| 6 | `scripts/metricas_canonicas.py` | ledger de números | CURRENT | **fonte de verdade numérica** |
| 7 | `docs/descoberta/CAMADA-DE-VOZ-ESPANHA.md` | a rodada espanhola inteira | CURRENT | inclui as correções |
| 8 | `data/samples/AUDITORIA-REGRA-COLETA-EXTERNA.json` | 206 achados + backlog | CURRENT | o que falta e o que não |
| 9 | `docs/fontes/ATLAS-DE-FONTES-EAME.md` | 36 fontes | CURRENT | de onde vem cada dado |
| 10 | `docs/regras/REGUA-DE-ALERTA-EAME.md` | quando vira alerta | CURRENT | impede vender feed como inteligência |
| 11 | `docs/regras/REGUA-DE-CHANGE-EVENT-EAME.md` | mudança vs nova versão | CURRENT | `FIRST SNAPSHOT ≠ NO CHANGE` |
| 12 | `docs/regras/POLITICA-DE-CHAVES-DESCARTAVEIS.md` | Apify | CURRENT | autonomia e limites |
| 13 | `docs/apresentacao/MATRIZ-DE-PROVA-EAME.md` | placar do deck | CURRENT | o que foi prometido vs provado |
| 14 | `docs/piloto/VEREDITO-M10-HANDOFF.md` | veredito M10 | CURRENT | estado do produto |
| 15 | `docs/piloto/EXTERNAL-ONLY-BUSINESS-CASE.md` | caso externo | CURRENT | por que não há prova econômica |
| 16 | `docs/decisoes/DIARIO-DE-DECISOES.md` | D-001… | CURRENT | **por que fizemos assim** |
| 17 | `docs/operacao/RELATORIO-DE-ROTAS-APIFY-ES.md` | Actors nas 5 dimensões | CURRENT | não repetir teste pago |
| 18 | `docs/descoberta/MISSAO-EAME-01.md` e afins | missões antigas | **HISTORICAL** | contexto, não estado |

---

## AB · COMANDOS — todos testados nesta sessão

```bash
# suíte canônica — <!--M:TEST_COUNT_CURRENT-->329<!--/M--> testes
python3 -m unittest discover -s tests
python3 -m unittest discover -s tests -q          # silencioso
python3 -m unittest tests.test_pipeline            # um arquivo

# ledger de métricas — FONTE DE VERDADE dos números
python3 scripts/metricas_canonicas.py              # tabela legível
python3 scripts/metricas_canonicas.py --json       # máquina
python3 scripts/metricas_canonicas.py --sync       # reescreve marcadores nos documentos

# portão de saída — pode coletar?
python3 scripts/portao.py
python3 scripts/portao.py --json

# auditoria contra alvo congelado
python3 scripts/auditoria.py                       # SHA e estado da árvore
python3 scripts/auditoria.py --congelar            # cria o worktree só-leitura

# proveniência — o RUN_ID resolve
python3 scripts/proveniencia.py
python3 scripts/proveniencia.py --campos

# relógio de dados — recalcula SHA-256 de tudo que é vigiado
python3 scripts/data_clock.py

# contratos da camada de voz
python3 scripts/voz.py
python3 scripts/voz.py --campos

# filas de descoberta
python3 scripts/filas.py

# Ask Sintonia
python3 scripts/ask_sintonia.py
```

---

## AC · DEPENDÊNCIAS EXTERNAS

**Runtime:** Python 3.11, **biblioteca padrão apenas**. Nenhum `pip install` é necessário
para a suíte nem para os scripts canônicos. `pytest` **não** está instalado — use `unittest`.

**Ferramentas de sistema usadas:** `git`, `curl`, `unzip` (fallback para ZIP Deflate64, que o
`zipfile` da stdlib não abre).

**APIs sem chave:** OpenAlex · CELEX/Cellar · Eurostat · NASA POWER · RAIF · ROPF · E-Phy ·
registro italiano.

**APIs com chave:** Apify (chave descartável fornecida pelo Luciano, **nunca versionada**).
Lida em tempo de execução de arquivo fora do repositório.

**Variável esperada:** nenhuma obrigatória. `AUDITOR_VERSION` é opcional e entra no registro
de auditoria.

**Rede:** o ambiente usa proxy com CA em `/root/.ccr/ca-bundle.crt`, já default. **Nunca
desligar verificação TLS** — certificado que não valida é *estado da fonte*, e há teste que
proíbe `CERT_NONE` e `check_hostname = False`.

---

## AD · PRÓXIMA MISSÃO RECOMENDADA

```
NEXT_MISSION = VERIFICACAO-ADVERSARIAL-DOS-SEIS-PORTOES-CONTRA-SHA-CONGELADO
               e, se passarem, EXECUTAR A FILA DE 20 PESQUISADORES
```

**Por que esta e não a ponte Brasil→EAME:**

1. **Os seis portões estão `PROVED` por auto-avaliação e nunca foram refutados por terceiro.**
   A verificação que eu lancei não terminou. Declarar `READY_FOR_NEXT_ES_COLLECTION = YES`
   com base só na minha própria medição é o mesmo erro de classe que a auditoria pegou: um
   portão que se verifica sozinho.
2. **É barato.** O mecanismo de congelamento já existe e está testado.
3. **A fila de 20 pesquisadores já está pronta** e é a única coisa que pode fechar
   `SCIENCE → PUBLIC VOICE`, hoje `NOT_REACHED`.
4. **A ponte Brasil→EAME é valiosa mas não urgente**, e exige congelar SHAs dos **dois**
   repositórios. Sem os portões verificados, ela importaria padrões para uma base cuja
   reprodutibilidade ainda não foi confirmada por terceiro.

**Ordem sugerida:** verificar portões → executar a fila de 20 → só então a ponte Brasil.

---

## AE · SOBRE A TAG DE HANDOFF — não existe, e por quê

Tentei criar e enviar a tag anotada `handoff-claude-account-2026-08-29`.
**O proxy git deste ambiente recusa push de tag: `RPC failed; HTTP 403`.**
`git ls-remote --tags origin` não devolve tag nenhuma — o remoto não tem nenhuma.

Não forcei, e apaguei a tag local para não deixar um marcador que morreria com o
contêiner e daria falsa impressão de existir.

**O marcador do handoff é o commit**, encontrável por:

```bash
git log --oneline --grep='^handoff: transferencia completa'
```

---

## NOTA FINAL DE HONESTIDADE

O que esta conta **não** conseguiu terminar:

1. **A verificação adversarial dos seis portões.** Lançada contra `a79f434`, não retornou.
2. **A ponte Brasil→EAME.** Nunca foi medida.
3. **`SCIENCE → PUBLIC VOICE`.** Fila pronta, execução não feita.
4. **O confundidor de Córdoba.** Continua aberto.

Nada disso está escondido em nenhum lugar deste repositório.
