# MISSÃO 14 — MAPA DE CREATORS / FARMFLUENCERS EAME

**Data:** 2026-08-30 · **Escopo:** ES · IT · FR
**Pergunta operacional:** *"Se a ADAMA quiser fazer uma ação para esta cultura neste país,
quem já fala com esse público?"*

> **Esta missão não é o EARLY SIGNAL.**
> Early Signal: pessoa como **sensor técnico**. Esta missão: pessoa como **canal de
> comunicação**. A mesma pessoa pode ter os dois papéis; os papéis nunca se colapsam.
> No contrato, `SENSOR_ROLE_LINK` é **ponteiro** — nunca fusão. Nenhum campo desta ficha
> herda valor do universo de sensores.

---

## O QUE ESTA RODADA ENTREGA

Uma **capacidade executável** (contrato de campos, sete leis em código, 31 provas) e uma
**primeira base medida** — não um ranking de influencers.

| artefato | o que é | tamanho |
|---|---|---|
| `scripts/creators.py` | contrato de 91 campos + 7 leis + veredito derivado | — |
| `tests/test_creators.py` | uma prova por confusão proibida | **31 provas** |
| `CREATORS-ES-IT-FR.json` | candidatos por país, achados em pesquisa aberta | 14 |
| `SEED-IT-CANDIDATES.json` | a seed externa, como **alegação** | 25 handles |
| `SEED-IT-RESOLVED.json` | medição Apify no runner residencial | 25/25 · **US$ 0,0624** |
| `SEED-IT-VALIDATION.json` | identidade e cultura medidas por fonte aberta | 10 |
| `IT-CREATORS-CONSOLIDATED.json` | as três camadas juntas, sem se disfarçarem | 25 |
| `BRAND-COLLABORATIONS-EU.json` | pares creator × marca **nomeados** | 7 |
| `MARKET-EVIDENCE-EU.json` | prova de mercado + veredito + colisões | 8 |
| `DISCOVERY-HUBS.json` | universidades, feiras, prêmios, associações | **43** |

---

## A · PROVA DE MERCADO — o ecossistema existe?

| país | ecossistema de creators agrícolas | uso comercial por marcas |
|---|---|---|
| **ES** | **PROVED** | **PROVED** |
| **IT** | **PROVED** | **PROVED** |
| **FR** | **PROVED** | **PROVED** |

Evidência preservada em `MARKET-EVIDENCE-EU.json` (8 registros). Destaques:

- **ES** — Andalucía concentra **1 em cada 4** criadores de conteúdo agrário do país, com
  dois polos: olivar (Jaén/Córdoba/Sevilha) e horticultura de Almería. Existe
  infraestrutura de intermediação comercial (AGROLAND) e um **prêmio setorial com
  categorias por cultura patrocinadas por empresas de insumo**.
- **IT** — marcas contratam farm-influencer; a Regione Veneto recruta creators agrícolas
  desde 2023; a Syngenta mantém campanha multimídia própria (*Agcelerators*).
- **FR** — monetização declarada pelos próprios creators (~1.200 € por 4 vídeos/mês a
  70.000 visualizações); New Holland, Kuhn, Sencrop e Ifor Williams colaboram com
  agri-influenceurs; a Intercéréales paga parcerias.

---

## B · CROP PROTECTION — a pergunta específica

> **ARE FARMFLUENCERS USED FOR CROP-PROTECTION ACTIVATION IN EUROPE?**

| país | veredito | por quê |
|---|---|---|
| **ES** | **PARTIAL** | 3 casos de empresa de defensivo usando creators — nenhum é ativação de **produto** |
| **FR** | **PARTIAL** | 1 caso — patrocínio de imagem corporativa, não de produto |
| **IT** | **`NOT_OBSERVED_IN_MEASURED_CORPUS`** | testado; nada encontrado **dentro do corpus medido** |

O veredito é **derivado por `creators.veredito_crop_protection()`**, não digitado. A
distinção que ele executa é a que decide a resposta:

```
empresa de crop protection usando creator   ≠   ativação de produto fitossanitário
```

### O que estes estados NÃO significam

> **Correção aplicada nesta rodada.** A primeira redação afirmava que a faixa de ativação
> de produto estaria livre e desocupada nos três países. Isso **não** era o que havia sido
> medido: era extrapolação, e está agora proibida por teste
> (`test_nenhum_artefato_AFIRMA_a_frase_extrapolada`).

O que foi medido é:

```
CROP_PROTECTION_PRODUCT_CREATOR_ACTIVATION = NOT_OBSERVED_IN_MEASURED_CORPUS
```

E o corpus medido é **pequeno e enviesado pelas fontes que alcançamos**: pesquisa aberta
por buscador mais **uma** rota Apify de Instagram. Ele **não** inclui varredura sistemática
de posts patrocinados, arquivos de campanha das marcas, nem plataformas de influencer
marketing.

| não observado no corpus **não** é | |
|---|---|
| ≠ ninguém faz | uma marca pode ativar produto com creator sem que a nossa busca alcance |
| ≠ white space de mercado | ausência de observação não mede ocupação de mercado |
| ≠ oportunidade comercial | a decisão comercial depende de dados que esta base não tem |

O mesmo vale para a Itália: **`NOT_OBSERVED_IN_MEASURED_CORPUS` não significa
`ITALY_DOES_NOT_USE_AGRICULTURAL_CREATORS`** — a Itália tem, e está provado neste mesmo
documento. Significa apenas que **não se observou uso ligado especificamente a crop
protection** dentro do universo medido.

A ressalva viaja **dentro do JSON**, no campo `ESTE_ESTADO_NAO_SIGNIFICA`, para que não se
perca entre o dado e o slide.

**Os quatro casos, todos preservados com fonte:**

| caso | marca | tipo de relação | mensagem |
|---|---|---|---|
| `#YoSoyAgricultor` (ES, 2020) | **BASF Agro** | `BRAND_COLLABORATION_PROVED` | imagem corporativa |
| Categoria *Tomatito* (ES, 2026) | **Seipasa** | `BRAND_ECOSYSTEM_SPONSORSHIP` | presença em evento |
| Categoria *Embajador del AOVE* (ES, 2026) | **Syngenta** | `BRAND_ECOSYSTEM_SPONSORSHIP` | presença em evento |
| Salon de l'Agriculture (FR, 2023) | **Bayer** | `PAID_PARTNERSHIP_PROVED` | imagem corporativa |

Os cinco tipos de relação **não são degraus** e não são equivalentes:
`BRAND_ECOSYSTEM_SPONSORSHIP` · `BRAND_EVENT_COLLABORATION` ·
`BRAND_COLLABORATION_PROVED` · `PAID_PARTNERSHIP_PROVED` · `PRODUCT_ACTIVATION_PROVED`.
São um `frozenset` **sem índice**, e um teste proíbe dar-lhes ordem — porque num contínuo
"a Syngenta patrocinou uma categoria" vira, três leituras depois, "a Syngenta ativa produto
com creators".

**Sobre o caso francês:** a creator encerrou a parceria após repercussão pública,
investigada por dois veículos. Isso está registrado como **fato daquele caso**, e não como
causa geral do mercado — não se infere dele por que a ativação de produto não foi observada
nos outros países.

---

## C · A SEED ITALIANA — o que a lista dizia e o que a medição encontrou

25 handles únicos (28 linhas, 3 duplicatas legítimas: a mesma pessoa alegada em duas
culturas). **Todos resolvidos pela Apify** no runner residencial, por **US$ 0,0624**.

### C.1 · Estado do handle

| estado | n | significado |
|---|---|---|
| `RESOLVED` | **16** | perfil devolvido com dado |
| `SEED_HANDLE_LIKELY_WRONG` | **4** | a imprensa mede alcance grande e o handle da seed não devolve nada |
| `HANDLE_UNRESOLVED` | **3** | rota não devolveu — **não** é "não existe" |
| `RESOLVED_MINIMAL_PRESENCE` | **2** | perfil real, presença ínfima |

### C.2 · O nome bate com a pessoa?

`EXACT` **10** · `PARTIAL` **2** · `NO_MATCH` **5** · `NOT_TESTED` **8**

Cinco handles devolvem outra pessoa. `@nicolo.polo` devolve um perfil chamado
**"phineASS"** (211 seguidores); `@giacomolepri` devolve **"giacomo_le."** com
**2 seguidores e 0 posts**. Um portão que parasse no nome teria promovido os dois a
creators de milho e de fruticultura.

### C.3 · O achado que inverte a leitura da lista

Os **cinco maiores perfis da seed somam ~452 mil seguidores — e quatro são mídia de
vinho**, não viticultura:

| handle | seguidores | o que é |
|---|---|---|
| `@theyoungnonno` | 257.344 | a validar |
| `@italianwinelover` | 206.142 | **wine media** — blogger/educador |
| `@enoblogger` | 101.510 | **wine media** |
| `@giulia_sattin` | 79.752 | a validar |
| `@doctor.wine` | 38.677 | **wine media** — crítico, 40 anos de carreira |

> Ordenar esta lista por seguidores entregaria ao Marketing uma **audiência de consumidor
> de vinho** como se fosse **audiência de produtor de uva**.

Enquanto isso, os perfis de cultura têm presença mínima no Instagram:
`@giulia_tonello` **90**, `@pedro.pastore` **536**, `@filippoballardin` **820**.

### C.4 · O candidato mais valioso da lista tem o endereço errado

**`@davide_gomiero`** — o único produtor de **~400 ha** da seed, com **~410 mil
seguidores** segundo a imprensa e audiência declarada de *agricultores, criadores e
entusiastas* — **não devolveu perfil**. Marcado `SEED_HANDLE_LIKELY_WRONG`.

É o caso mais caro se passar batido: o melhor candidato **some por erro de endereço**, e a
lista continua parecendo correta. Mesmo padrão em `@evolovers` (imprensa: comunidade
consolidada desde 2020; rota: 13 seguidores, 9 posts), `@maria.pezone` e
`@yuliyapyliavska`.

### C.5 · A suspeita que estava errada — e por que isso importa

O portão levantou `SUSPECTED_CHAIN_MISMATCH` para 10 dos 25 handles, por léxico de
produto final (`wine`, `evo`, `oil`, `sommelier`, `garden`). **Ela acertou em três e
errou em um:**

> **`@evolovers`** foi suspeito por *"EVO = azeite, produto final"*.
> **Medido:** Leonardo Leggeri é **produtor pugliês**; a comunidade nasceu de **podas,
> colheitas e degustações no campo dele**. A seed estava **certa** e a nossa suspeita,
> **errada**.

Por isso `SUSPECTED_CHAIN_MISMATCH` **nunca** promove sozinho a `WRONG_ASSIGNMENT`. Um
portão que confiasse na suspeita teria descartado o melhor olivicultor da lista pelo nome
do handle — cometendo, do lado cético, o mesmo erro que a seed cometeu do lado otimista.

### C.6 · Culturas: alegado × provado

| estado | n | casos |
|---|---|---|
| `PROVED` | 1 | Leggeri — olival próprio |
| `PARTIAL` | 3 | Gomiero (milho ✓, trigo ✗, arroz ✗) · Pezone (horticultura ✓, tomate ✗) · Russo |
| `NOT_PROVED` | 3 | Ballardin · Agromoderni · Pyliavska |
| `WRONG_ASSIGNMENT` | **3** | Cernilli · Gardini · Colzani |

**Os três erros de categoria:**
- **Daniele Cernilli** e **Luca Gardini** vieram como *viticultura*. São **crítico
  enológico** e **sommelier** (Melhor Sommelier do Mundo 2010) — vinho pronto, não videira.
- **Mirco Colzani** veio como *fruticultura*. É **garden designer** — jardim ornamental,
  não produção de fruta. Erro de categoria, não de grau.

---

## D · CREATORS POR PAÍS · REGIÃO · CULTURA

Estrutura obrigatória `COUNTRY → REGION → CROP → PERSON`. Base atual (`CREATORS-ES-IT-FR`):

| país | total | cultura provada | produtor provado |
|---|---|---|---|
| **ES** | 5 | **5** | 4 |
| **IT** | 5 | 2 | 2 |
| **FR** | 4 | 0 | 1 |

**ES → Andalucía → OLIVO:** Fernando Giraldo *(Tomy Rohde)*, Córdoba, olivarero ·
Alberto Rojas *(Agriproducción)*, Córdoba, olivar + extensivos.
**ES → Almería → HORTÍCOLAS:** Caterina Pak *(AgroComunidad)*, técnica agrícola ·
Francisco Jesús Montoya *(biocampojoyma)*, horticultor · Esther Molina, invernadero solar.
**IT → Toscana → VITE:** Paolo Nenci, conduz as vinhas e produz vinho.
**IT → Campania → HORTICULTURA:** Maria Pezone, 130 ha de alface e melão.
**IT → Puglia → OLIVO:** Leonardo Leggeri, produtor.
**IT → Veneto → MILHO:** Davide Gomiero, ~400 ha *(handle a resolver)*.
**FR:** Thierry Bailliet (Pas-de-Calais, produtor) · Agricoolteur · Océane Agricultrice ·
Jean-Baptiste De Wever — **nenhuma cultura provada ainda**. É a maior lacuna da rodada.

---

## E · HISTÓRICO COM MARCAS E CONCORRENTES

7 pares **nomeados** em `BRAND-COLLABORATIONS-EU.json`. Concorrentes observados:
**BASF** (ES), **Seipasa** (ES), **Syngenta** (ES), **Bayer** (FR).
Não-concorrentes: Manitou France × Jean-Baptiste De Wever (maquinaria, engajamento 12× a
média), Kuhn Ibérica (maquinaria), e uma colaboração italiana **provada sem marca
nomeada** — The Roman Farmer cria conteúdo para empresas do setor, mas **nenhuma fonte
nomeia qual**, então `BRAND = NÃO SEI`.

**ADAMA:** `ADAMA_COLLABORATION_OBSERVED = NOT_OBSERVED` nos três países — busca feita,
nada encontrado. **Não é `NOT_TESTED` e não é prova de ausência.**

E uma colisão medida, preservada porque a próxima busca vai reencontrá-la:

> Buscar *"ADAMA campanha embaixador"* devolve **Adamo** — uma operadora de telecom
> espanhola — em campanha com Jesús Calleja. **Uma letra** separa a empresa de defensivos
> de uma telecom. Casar por nome teria criado uma "colaboração ADAMA com influencer"
> inexistente.

---

## F · DISCOVERY HUBS — 43 registrados

`DISCOVERY_HUB ≠ CREATOR`. Universidade, feira, associação e prêmio **não entram no
ranking de creators**: eles são de onde saem os nomes.

**ES 12 · IT 19 · FR 12.** Identidade: `PROVED` 4 · `NOT_TESTED` 34 ·
`IDENTITY_NOT_PROVED` 2 · `CORRECTED` 2 · `DEMOTED` 1.

As instruções de correção do dono estão **executadas no dado**, não só anotadas:

| hub | estado | motivo |
|---|---|---|
| *IIT Agro* | `IDENTITY_NOT_PROVED` | não aceitar como unidade formal sem validação |
| *Osservatorio Agro* | `IDENTITY_NOT_PROVED` | não coletar em volume até resolver a identidade |
| **SIMA / AgriSIMA** | `DEMOTED` | o SIMA antigo foi cancelado — não usar como master source sem edição medida |
| **AgFunder** | `CORRECTED` | retirado do mapa francês; é inteligência global, não hub local |
| **Sencrop** | `CORRECTED` | pertence ao Groupe ISAGRI — não é startup independente |

`ROLE` e `PRIORITY` dos 34 `NOT_TESTED` são **asserção do dono**, marcada campo a campo em
`ROLE_SOURCE` — para que ninguém os leia daqui a um mês como resultado de pesquisa.

**Seipasa** é caso especial: é fonte **e objeto**. Patrocina a categoria *Tomatito* do
prêmio que usamos como fonte de descoberta — logo não conta como observador independente
do próprio patrocínio.

---

## G · WHO COULD MARKETING CALL? — candidatos desta rodada

**Nenhum creator está `ACTIVATION_READY`.** Todos os 39 registros estão
`RESEARCH_NEEDED`, e o motivo é honesto e específico: **identidade não resolvida na fonte
primária**. O egresso deste contêiner bloqueia os domínios do setor
(medido: `plataformatierra.es`, `revistamercados.com`, `cibotoday.it`, `reporterre.net`,
`desmog.com` — todos `EGRESS_BLOCKED`), então o buscador **surfou** os fatos e a **página
não foi aberta**.

Os quatro mais próximos de `ACTIVATION_READY`, todos precisando apenas de resolução de
perfil e medição de atividade:

| candidato | país · região | cultura provada | por que |
|---|---|---|---|
| **Davide Gomiero** | IT · Limena, Padova | MILHO (+ alfafa, soja) | produtor de ~400 ha, ~410 mil seguidores, audiência declarada de agricultores · **resolver o handle** |
| **Leonardo Leggeri** | IT · Puglia | OLIVO | produtor; conteúdo de poda e colheita no próprio olival |
| **Fernando Giraldo** *(Tomy Rohde)* | ES · Córdoba | OLIVO | olivarero; 52 mil no X, 9,6 mil no Instagram |
| **Francisco J. Montoya** | ES · Almería | HORTÍCOLAS | horticultor de invernadero |

`AUDIENCE_FIT_FOR_ADAMA` já separa o joio: **LOW 4** (mídia de vinho e azeite,
`WRONG_ASSIGNMENT`) · **MEDIUM 4** · **NOT_KNOWN 17**.

---

## H · APIFY — o que a rota custou e o que ela devolveu

| métrica | valor |
|---|---|
| runs desta missão | 5 (2 contratos · 1 diag · 2 seed) |
| itens coletados | 25 perfis |
| **custo** | **US$ 0,0624** |
| creators válidos | 16 resolvidos + 4 com handle suspeito |
| **custo por handle resolvido** | **~US$ 0,0025** |

**Dois defeitos encontrados e corrigidos, ambos falhando fechado:**

1. **`carregar()` conhecia 3 chaves de artefato e a seed usava uma quarta.** A fase paga
   rodou com **zero handles**. Não produziu dado errado — gastou uma execução para
   descobrir. Dois testes novos fecham a classe inteira; o segundo já encontrou mais duas
   chaves (`ACTORS`, `MARKET_EVIDENCE`) na primeira execução.
2. **`curl` por subprocess devolvia stdout vazio, de forma intermitente, no runner
   Windows.** Medido no mesmo endpoint com a mesma chave: 21:53 OK · 21:56 `TypeError` ·
   22:00 OK (subprocess direto) · 22:02 `TypeError` nos três atores. **Não era a
   plataforma recusando — era o subprocesso não entregando saída.** Trocado por `urllib`,
   que remove a classe inteira; a proveniência continua passando pela porta única
   (`coletor.executar`), por **substituição** de `coletor._curl`, não por desvio.

E uma lição de contrato: a primeira versão da fase `contratos` lia só o ator e dizia
`AVAILABLE`. Isso **não é o contrato** — `AVAILABLE` prova que o ator existe, não que a
entrada que vamos mandar é a que ele aceita. Agora lê o **input schema** do build.

---

## I · AS SETE LEIS, EM CÓDIGO E COM PROVA

| # | lei | onde falha se violada |
|---|---|---|
| 1 | `NAME ≠ HANDLE ≠ PROFILE` — handle não se infere de nome | `checar()` recusa handle sem `SOURCE_URL` |
| 2 | **cultura se prova** — "é agro" não prova "é olivar" | `CROP_STATE=PROVED` exige `CROP_EVIDENCE` |
| 3 | **creator rural ≠ produtor** | `ACTUAL_FARMER` é campo próprio com evidência própria |
| 4 | **menção ≠ patrocínio** | `promover_marca()` recusa subida sem evidência do degrau |
| 5 | **categoria não transfere** | maquinaria nunca conta no veredito de defensivo |
| 6 | **sem authority score** | `relevancia()` devolve estado derivado; seguidor alto sem identidade não sobe |
| 7 | **produto final ≠ lavoura** | vinho não prova videira; azeite não prova olivar |

31 provas em `tests/test_creators.py`, uma por confusão proibida.

---

## L · COMPLIANCE — o que esta base **não** autoriza

`ACTIVATION_READY` significa **"há evidência suficiente para o Marketing avaliar"**.
**Não** significa campanha aprovada. Para qualquer ativação de produto fitossanitário
ficam pendentes, e `pendencias_de_compliance()` as devolve sempre:

`COUNTRY_SPECIFIC_ADVERTISING_CHECK` · `LOCAL_REGISTRATION_CHECK` ·
`AUTHORIZED_CROP_CHECK` · `PLATFORM_POLICY_CHECK` · `SPONSORED_CONTENT_DISCLOSURE_CHECK`

> **PORTFÓLIO GLOBAL ≠ PORTFÓLIO LOCAL.** Não sugerir promoção de produto sem registro
> local compatível com aquele país **e** aquela cultura.

O caso Bayer/França não é só um dado de mercado — é o **custo reputacional medido** desta
faixa: a creator encerrou a parceria e declarou que recusaria o pagamento, após
investigação de dois veículos.

---

## M · LACUNAS — declaradas, não escondidas

1. **Identidade não resolvida na fonte primária.** Egresso do contêiner bloqueia os
   domínios do setor. Todos os 39 registros seguem `IDENTITY_STATE=NOT_PROVED` ou
   dependem de resumo de buscador. **A rota existe e está provada** — o runner residencial
   — mas só foi usada para Instagram nesta rodada.
2. **França sem nenhuma cultura provada.** 4 candidatos, 0 culturas. A maior lacuna.
3. **34 dos 43 hubs `NOT_TESTED`.** Nenhuma pessoa foi extraída de hub ainda —
   `PEOPLE_EXTRACTED = 0` em todos.
4. **Seeds ES e FR do briefing ainda não gravados** (AgroInfluye, Blacks Moutons, os 6
   nomes espanhóis e os 11 franceses). Foram lidos, não ingeridos.
5. **Atividade não medida em ninguém.** `ACTIVITY_STATE=NOT_MEASURED` em 100% dos
   registros — a fase que mede `POSTS_LAST_30D` / `LAST_ACTIVITY_DATE` não rodou.
6. **`FIELD_VOICE` não iniciado.**
7. **4 handles da seed provavelmente errados** — resolver antes de descartar as pessoas.

---

## N · PRÓXIMOS PASSOS, NA ORDEM QUE O DADO PEDE

1. **Resolver os 4 handles suspeitos** — a começar por `@davide_gomiero`, o melhor
   candidato da lista italiana.
2. **Rodar a fase de atividade** (posts 30/90 dias) sobre os 16 perfis resolvidos.
3. **Ingerir os seeds ES e FR** e resolvê-los pela mesma rota — a França é a lacuna maior
   e tem a maior lista de seeds.
4. **Extrair pessoas dos hubs `VERY_HIGH`**: Premios AgroInfluye (ES), Enovitis in Campo
   (IT), SITEVI e SIVAL (FR) — os três últimos ocorrem **dentro da lavoura**, com sessões
   de crop protection.
5. **Promover `apify-creators.yml` ao branch padrão** — hoje as fases entram por ponte
   pelo `apify-sensores.yml`, porque o GitHub só registra `workflow_dispatch` de arquivos
   no branch padrão. **Isso exige autorização do dono.**

## O · EXPANSÃO — DE / PL / RO

**Não recomendada ainda.** ES/IT/FR ainda não estão medidos: França sem cultura provada,
34 hubs intocados, atividade não medida em ninguém. Abrir um quarto país agora
multiplicaria a lacuna em vez de fechá-la.

Quando abrir, a ordem sugerida pelo que esta rodada mostrou:
**DE** primeiro (mercado de maquinaria forte, o que costuma vir junto de creator economy
agrícola madura), depois **PL** (grandes culturas), depois **RO**.

---

**Casco não alterado. Arquitetura canônica não alterada.** Esta rodada construiu e provou
a capacidade — e mediu o quanto uma lista externa, lida sem portão, teria custado.
