# COMPETITOR FORESIGHT PILOT — ES · IT · FR

> ## ⚠️ ESTE DOCUMENTO É A RODADA 1, E FOI CORRIGIDO
>
> A rodada final mediu Itália e França e **corrigiu cinco afirmações** que
> este relatório fazia. O documento canônico da capacidade passou a ser
> [`docs/foresight/HANDOFF-INTELLIGENCE-COMPETITOR-FORESIGHT-EAME.md`](../foresight/HANDOFF-INTELLIGENCE-COMPETITOR-FORESIGHT-EAME.md).
>
> | o que a rodada 1 escreveu | o que está medido |
> |---|---|
> | "patente não serve" / `DEMOTED` sem recorte | a **rota** `PATENT_LOOKUP_BY_COMMERCIAL_BRAND_NAME` é `REFUTED_FOR_PILOT`. `PATENT_WATCH` como um todo é **`NOT_TESTED`** — quatro rotas nunca foram tentadas |
> | "a marca vem antes do registro em 76%" | `HISTORICAL_PRECEDENCE_OBSERVED` = 1.087 de 1.652 nos três países. **`OPERATIONAL_EARLY_WARNING_VALUE = NOT_PROVED`** — mediana de ~4 anos pode ser cedo DEMAIS |
> | "a marca tem cadência observável; o registro não" | `RECENT_TRADEMARK_ACTIVITY_EXISTS = YES`, mas **`DAILY_VALUE = NOT_PROVED`**: uma fotografia não mede cadência |
> | "o ROPF não tem sinal diário" | `REGULATORY_CHANGE_IN_THIS_INTERVAL = 0 OBSERVED`; **`REGULATORY_CHANGE_CADENCE = NOT_PROVED`**. Dois dias são dois dias |
> | "META e CREATOR não existem no acervo" | **errado.** O Creator Map está **congelado com handoff canônico** em branch própria; a missão Meta tem **1.111 anúncios** dos mesmos seis concorrentes. O estado correto é **`NOT_JOINED_IN_THIS_MISSION`** |
>
> **E o escopo mudou:** onde este documento diz "só Espanha", a paridade
> fechou nos três países — **1.683 cadeias ligadas** (209 ES · 334 IT ·
> 1.140 FR), com **126 falsos links recusados**.
>
> As tabelas abaixo continuam corretas **para a rodada 1 e para a Espanha**.
> Leia-as com esta correção no colo.


**Data:** 2026-08-30 · **DATASET_OWNER:** `COMPETITOR_FORESIGHT_EAME`
**Estado da capacidade:** **PARCIALMENTE COMPROVADA** — duas camadas de sete,
nenhuma cadeia fim-a-fim fechada.

> A pergunta do piloto era: dá para observar a trajetória pública de um
> concorrente, de MARCA a COMUNICAÇÃO?
>
> **A resposta medida é: metade da corrente existe e a outra metade não foi
> coletada.** MARCA e REGISTRO abrem, são datáveis e se ligam em 207 casos
> provados. CATÁLOGO, META e CREATOR não existem no acervo — e por isso
> nenhuma das 209 cadeias tem mais de 2 das 5 camadas.

---

## O RESUMO EM UMA TELA

| | |
|---|---|
| concorrentes no piloto | **6**, escolhidos pela contagem de titulares do registro espanhol |
| marcas coletadas | **9.661** em ES · IT · FR · EUIPO |
| fatos regulatórios datados | **2.716** |
| eventos gravados | **10.743** |
| links marca↔registro **provados** | **207** |
| links **recusados** e publicados | **2** (+31 pares que não viraram link, declarados) |
| cadeias com 5 de 5 camadas | **0** |
| change events regulatórios | **0** — e o motivo está medido |
| camada de patente | **DEMOTED / NOT_USED** — a *rota por nome de marca* foi refutada em 0 de 5; a camada inteira segue `NOT_TESTED` |

---

# A · FONTES IP COMPROVADAS POR PAÍS

Medido em 2026-08-30, com `curl` e User-Agent de navegador:

| porta | resultado | uso no piloto |
|---|---|---|
| **TMview** `POST tmdn.org/tmview/api/search/results` | **200** | **a rota do piloto** |
| OEPM `consultas2.oepm.es` | **403** | inalcançável por robô |
| INPI `data.inpi.fr` | **403** | inalcançável por robô |
| UIBM `uibm.gov.it` | **000** (não conecta) | inalcançável por robô |
| EUIPO `euipo.europa.eu/eSearch` | 200 (página) | coberto pelo TMview, escritório `EM` |
| Espacenet / EPO OPS | **403** | ver camada B |

**Uma rota cobre os quatro escritórios.** O TMview é o agregador oficial da
EUIPO sobre os registros nacionais, e cada resultado traz `tmOfficeURL`
apontando de volta para a ficha no portal de origem — a evidência continua
rastreável até a fonte primária mesmo quando ela recusa o robô.

> ⚠️ **TMview é ESPELHO, não é o registro.** O atraso de sincronização entre
> escritório nacional e TMview **não foi medido nesta rodada**. Ausência aqui
> é `NOT_OBSERVED_IN_TMVIEW`, nunca "a marca não existe".

## A armadilha que quase produziu o pior número do piloto

A API **ignora em silêncio** parâmetro cujo nome ela não conhece. Pedir
`applicantName`, `applicant`, `owner` ou `fApplicantName` devolve **HTTP 200 e
1.068.402 resultados** — a Espanha inteira — com cara de busca bem-sucedida.

Se o piloto não tivesse percebido, teria publicado *"1.068.402 marcas da
Syngenta"*. O nome correto é `appName`, e foi encontrado lendo
`index.e1860496.js` da própria página.

**Isso virou trava permanente:** `ip_tmview.buscar()` roda uma consulta de
CONTROLE sem filtro por escritório e **RECUSA** o resultado quando o total
filtrado é igual ao total sem filtro. Custa uma requisição por escritório e
paga o preço de nunca confundir "sem filtro" com "sem resultado".

---

# B · ACESSO A OEPM / UIBM / INPI / EUIPO / EPO

Os quatro primeiros: **via TMview, COMPROVADO** (tabela em A).

**EPO — DEMOTED, com medida.** Evidência:
`data/samples/COMPETITOR-PATENT-DEMOTE.json`

O Espacenet **abre** por navegador com janela gráfica (a tela de verificação
anti-robô libera sozinha após alguns segundos — nada foi contornado). Busca
por titular `pa=syngenta` devolve **6.333 resultados**. O volume existe.

O que não existe é **a chave**. Teste feito com o nome exato de 5 marcas do
piloto em texto completo:

| marca | concorrente | resultados | primeiro resultado | titular confere? |
|---|---|---|---|---|
| PROSARO | BAYER | 35 | HBCO Herbals [FR] | **não** |
| VERDALIS | CORTEVA | **0** | — | **não** |
| DUAL GOLD | SYNGENTA | 184 | implante de marcador de ouro, hospital [CN] | **não** |
| LIBERATOR | BAYER | 1.544 | coldre de bolso para eletrônicos | **não** |
| NITROPLUS | CORTEVA | 60 | composições com genes, farmacêutica [JP] | **não** |

**Placar: 0 de 5.** 1.823 resultados somados, nenhum atribuível ao concorrente.

**Por que a chave não existe:** patente nomeia MOLÉCULA e MECANISMO; marca e
registro nomeiam PRODUTO COMERCIAL. Os dois documentos falam de coisas
diferentes com vocabulários diferentes, e nenhum campo os une. A ponte
possível seria a substância ativa — que casaria a patente com **o setor
inteiro**, não com um concorrente.

Conforme §7 da missão, patente não atrasou a entrega.

---

# C · CONCORRENTES TESTADOS

A amostra **não** saiu da lista de nomes: saiu da contagem de titulares do
registro espanhol (3.084 registros, 262 titulares distintos).

| grupo | vigentes | registros | no piloto? |
|---|---|---|---|
| NUFARM | **102** | 147 | ✅ |
| _ADAMA (a casa)_ | _96_ | _188_ | — |
| SYNGENTA | **95** | 170 | ✅ |
| BAYER | **85** | 179 | ✅ |
| CORTEVA | **70** | 121 | ✅ |
| BASF | **70** | 119 | ✅ |
| UPL | **68** | 94 | ✅ |
| FMC | 50 | 143 | ❌ fora dos 6 maiores |
| CERTIS BELCHIM | 42 | 58 | ❌ |

**Conferência que dá confiança na contagem:** o script devolveu 96 vigentes
para a ADAMA — exatamente os 96 da fundação `ES-REGULATORIO-ROPF-2026-08-29`,
importada por outro caminho.

**O que este número NÃO é:** não é market share, não é volume vendido, não é
presença comercial. É quantas autorizações a empresa detém.

**Ficam de fora e pesam:** ASCENZA (97), SHARDA (97+46), ALBAUGH (78),
ARYSTA (50), SIPCAM (55). Estar fora é decisão do recorte, não medida de
irrelevância.

**Agrupamento é DECLARADO, não inferido.** `SHARDA CROPCHEM ESPAÑA S.L.` e
`SHARDA EUROPE BVBA` são duas pessoas jurídicas; somá-las é uma afirmação
societária que este piloto não tem. UPL soma duas razões sociais porque as
duas estão declaradas no script, e ambas ficam visíveis no artefato.

---

# D · TRADEMARKS ENCONTRADOS

**9.661 marcas.** `data/samples/COMPETITOR-IP-TMVIEW.json`

| | ES | IT | FR | EUIPO | total |
|---|---|---|---|---|---|
| NUFARM | 62 | 32 | 256 | 104 | 454 |
| SYNGENTA | 52 | 64 | 469 | 918 | 1.503 |
| BAYER | 243 | 461 | 1.130 | 2.103 | 3.937 |
| BASF | 114 | 96 | 732 | 1.668 | 2.610 |
| CORTEVA | 122 | 35 | 98 | 420 | 675 |
| UPL | 52 | 25 | 81 | 324 | 482 |

## ⚠️ O erro que esta rodada cometeu, mediu e corrigiu

A primeira régua tratou **classe 5 de Nice como sinal agro**. A classe 5 cobre
`preparações farmacêuticas, veterinárias, higiênicas **e** pesticidas` — tudo
na mesma classe. Resultado: `GINECANES` e `BEPANTHENSENSICALMSOS`, da Bayer,
foram carimbados como relevantes para defensivo. **São remédio.**

Medido nas 9.661 marcas, depois de corrigir para três estados:

| estado | n | leitura |
|---|---|---|
| `CLASSE_1_E_5` | 2.119 | o padrão do defensivo agrícola |
| `SO_CLASSE_1` | 1.413 | químico agrícola declarado |
| **`SO_CLASSE_5`** | **4.496** | **AMBÍGUO** — pode ser farma, veterinário ou pesticida |
| `FORA_DAS_CLASSES_AGRO` | 1.615 | nem 1 nem 5 |
| sem classe | 18 | |

**O ruído tem dono: 2.551 das 4.496 ambíguas são da Bayer**, que tem divisão
farmacêutica. Um piloto que somasse as duas forças diria que a Bayer é o
concorrente com mais atividade de marca agroquímica na EAME. Não é o que o
dado mostra — é o que a classe compartilhada faz parecer.

## ⚠️ E um achado que enfraquece a própria régua de classe

O **VERDALIS da Corteva**, mesma marca, mesmo titular, depositado na mesma
semana:

| escritório | data | classe de Nice | o que a régua diz |
|---|---|---|---|
| IT | 2026-07-16 | **[1]** | `SO_CLASSE_1` — sinal agro |
| FR | 2026-07-16 | **[1]** | `SO_CLASSE_1` — sinal agro |
| ES | 2026-07-17 | **[5]** | `SO_CLASSE_5` — **AMBÍGUO** |

**A mesma marca recebe leituras diferentes conforme o país.** A classe é
escolha de quem deposita, escritório por escritório, e não uma propriedade do
produto. Isso não invalida a régua — mas proíbe usá-la como filtro duro, e é
por isso que ela **marca** em vez de **descartar**.

---

# E · REGULATORY EVENTS EXISTENTES

`data/samples/COMPETITOR-REGULATORY-EVENTS.json`

## Change events: **ZERO**, e o zero é auditável

| | |
|---|---|
| versão A | `ropf_20260829.json.gz` · servidor `2026-08-29T00:21:08+02:00` · 3.084 registros |
| versão B | captura de hoje · servidor `2026-08-31T01:38:50+02:00` · 3.084 registros |
| comparações campo a campo | **40.092** |
| registros só em A | 0 |
| registros só em B | 0 |
| campos que diferem | **0** |
| estado do portão | **`NEW_VERSION_IDENTICAL`** |

**Nenhum change event foi emitido, e isso é resultado — não falha.** Duas
capturas a dois dias de distância, 3.084 registros, 13 campos, e o registro
espanhol não moveu nada.

> ⚠️ Isto **não** prova que o registro é estável. Prova que **ele não mudou
> nesses dois dias**. O intervalo é o alcance, e nada além dele.

## Dated facts: 2.716

O que **é** publicável hoje sem segunda versão são as datas que a própria
fonte declara:

| tipo | n |
|---|---|
| `LOCAL_REGISTRATION` | 829 |
| `EXPIRY` | 784 |
| `REGISTRATION_MODIFIED` | 762 |
| `SELLING_OFF_DEADLINE` | 341 |

`REGISTRATION_MODIFIED` diz **QUE** mudou e **QUANDO** — nunca **O QUÊ**.
Isso só sai de duas versões arquivadas.

**Onde o acervo estava vazio:** a fundação existente importou **96 registros,
só da ADAMA**. A camada regulatória de concorrente não existia. Não é fonte
nova — é a mesma rota já provada em `scripts/mapa_regfi.py`, com outro filtro.

**IT e FR: `NOT_AVAILABLE`.** Não há registro local desses dois países no
acervo, e o peso na Espanha não se transfere para eles.

---

# F · PRODUCT / CATALOG EVENTS

**`NOT_AVAILABLE`.** `data/raw/ES/` contém apenas `adama-website`. Nenhum
catálogo público de concorrente foi coletado nesta rodada.

**Não significa que os concorrentes não publiquem catálogo.**

---

# G · META EVENTS

**`NOT_AVAILABLE`.** Não existe `META_COMPETITOR_EAME` neste repositório e não
há nenhum arquivo de Meta em `data/samples/`.

**Não significa que o concorrente não anuncie.** É `NOT_COLLECTED`, e as duas
respostas são diferentes.

---

# H · CREATOR / EVENT EVENTS

**`NOT_AVAILABLE`.** Nenhum Creator Map em `data/samples/`.

**Não significa ausência de atividade de creator.**

---

# I · CROSSWALKS PROVADOS

`data/samples/COMPETITOR-CROSSWALK.json`

**A regra exige DUAS concordâncias, não uma:**
1. o nome normalizado da marca == o nome do produto no registro;
2. o grupo do titular da marca == o grupo do titular do registro.

Nome sozinho nunca promove.

| estado | n | |
|---|---|---|
| `PROVED` | **209** | nome e empresa conferem |
| `PARTIAL` | 24 | nome confere, titular fora da amostra |
| `REJECTED_HOLDER_MISMATCH` | **9** | nome confere, empresa é OUTRO concorrente |
| `NOT_KNOWN` (`NO_LINK`) | **5.335** | sem par de nome |

**5.579 marcas testadas · 209 pares provados · 3,7%.** A maioria esmagadora
das marcas de um concorrente **não** tem registro espanhol de mesmo nome.

PROVED por grupo: BAYER 47 · CORTEVA 46 · SYNGENTA 39 · BASF 39 · NUFARM 24 ·
UPL 14.

## A recusa que prova que a régua tem dentes

**`URBOLE`** — a marca é da **SYNGENTA**; o registro espanhol com esse nome é
da **ADAMA** (24157). Um casador por nome teria escrito *"a Syngenta tem o
registro do URBOLE"*. O crosswalk devolve `REJECTED_HOLDER_MISMATCH` e mostra
os dois titulares — **sem explicar por quê, porque nenhum dos dois documentos
explica**.

---

# J · TIMELINES COMPLETAS ENCONTRADAS

## **ZERO.**

Nenhuma das 209 cadeias tem as 5 camadas. **Todas têm 2 de 5.**

```
1 · IP / MARCA          ✅ TMview
2 · REGISTRO LOCAL      ✅ ROPF ES
3 · PRODUTO / CATÁLOGO  ❌ NOT_AVAILABLE
4 · META                ❌ NOT_AVAILABLE
5 · CREATOR             ❌ NOT_AVAILABLE
```

Esta é a resposta direta à pergunta C da missão, e ela é negativa.

---

# K · TIMELINES PARCIAIS

**209 cadeias**, todas com 2 de 5 camadas, todas sobre link `PROVED`.
Nenhuma cadeia foi construída sobre link `PARTIAL`, `REJECTED` ou `NOT_KNOWN`.

**5 cadeias de destaque — as marcas de 2026 depositadas em mais de um país**
(as únicas 5 que existem em 2026 com sinal agro forte e ≥2 escritórios):

| # | concorrente | marca | escritórios | datas | classes |
|---|---|---|---|---|---|
| 1 | **BASF** | `ARVELDRA` | EM · IT · FR · ES | 27/05 → 09/07/2026 | 1,5,9,31,42,44 |
| 2 | **BASF** | `PANVAIA` | EM · IT · ES · FR | 06/03 → 01/04/2026 | 13 classes |
| 3 | **BASF** | `AGVEEA` | EM · IT · ES · FR | 06/03 → 01/04/2026 | 13 classes |
| 4 | **CORTEVA** | `NITROPLUS` | EM (encerrada 26/01) · ES · IT | 18/08/2026 | 1 |
| 5 | **CORTEVA** | `VERDALIS` | IT · FR · ES | 16–17/07/2026 | 1 (IT/FR) · 5 (ES) |

**O que estas cinco linhas provam:** que a marca foi depositada, quando, em
que escritórios, por qual titular, e sob que classes declaradas. Cada uma tem
URL navegável até a ficha oficial.

**O que elas NÃO provam:** nada sobre lançamento, produto, cultura, praga,
data de mercado ou intenção. Nenhuma delas tem registro espanhol
correspondente — as cinco são `NO_LINK` no crosswalk.

**Leitura honesta do caso 2 e 3:** `PANVAIA` e `AGVEEA` foram depositadas nas
**mesmas datas, nos mesmos 4 escritórios, sob as mesmas 13 classes**. Treze
classes cobrindo de tintas a serviços financeiros não é o perfil de um
defensivo: é o perfil de uma **marca guarda-chuva**. Tratá-las como sinal de
produto seria erro.

---

# L · FIRST-SOURCE E LEAD-DAYS

**Pergunta A da missão — a marca aparece antes do registro?**

| | n | % |
|---|---|---|
| **marca antes do registro** | **158** | 76% |
| registro antes da marca — **hipótese REFUTADA no par** | 51 | 24% |
| mesmo dia | 0 | |
| **total medido** | **209** | |

## Por que a maioria dos lead-days não é defensável

A amplitude bruta vai de **-15.700 a +11.033 dias** — 43 anos para trás e 30
para frente. Um número desses não descreve um lançamento: descreve uma palavra
que dois documentos usaram em décadas diferentes.

Causas conhecidas do estouro:
- **redepósito de marca** — o TMview traz cada depósito; uma marca dos anos 70
  redepositada em 2010 aparece com a data nova (`MATCH`, `VIPER`, `SEMPRA`);
- **reuso de nome comercial** sobre autorização antiga;
- **marca genérica** que colide com produto de outra época.

**Regra de defensabilidade aplicada:** o depósito usado tem de ser o **mais
antigo** daquela marca naquele grupo (remove redepósito) **e** a ordem tem de
ser marca→registro. **Sem corte de tempo arbitrário** — um limiar escolhido a
dedo produziria a antecedência que se quisesse.

| | |
|---|---|
| pares defensáveis | **155** de 209 |
| mediana | **2.179 dias** (≈ 6 anos) |
| faixa | 41 a 11.033 dias |

**Resposta à pergunta D (qual fonte aparece primeiro):** em 76% dos pares
provados, a **MARCA**. Mas com mediana de 6 anos, ela é um sinal de
**trajetória longa**, não de lançamento iminente.

**Resposta à pergunta F — CORRIGIDA na rodada final.** O que segue mostra que
as duas fontes **se comportaram diferente nesta janela**. Não estabelece cadência
de nenhuma das duas: a marca tem UMA captura e o registro tem DUAS, a dois dias
de distância. `DAILY_VALUE = NOT_PROVED` para a marca;
`REGULATORY_CHANGE_CADENCE = NOT_PROVED` para o registro.

| fonte | movimento medido |
|---|---|
| **TMview / marca** | marcas depositadas **3 dias antes** da coleta (CORTEVA, 27/08); **346 depósitos** desde 01/01/2025 |
| **ROPF / registro** | **0 mudanças** em 40.092 comparações a 2 dias de distância |

~~A marca tem cadência observável. O registro, nesta janela, não.~~
**Corrigido:** a marca mostrou ATIVIDADE RECENTE; o registro não mudou NESTA
JANELA. Nenhum dos dois é uma medida de cadência.

---

# M · NOISE / FALSE-LINK RATE

O casador frouxo **foi realmente rodado** — não imaginado — sobre as mesmas
marcas, para medir o que a frouxidão produziria:

| | |
|---|---|
| pares extras que um casador por prefixo criaria | **441** |
| destes, com **titular errado** | **151** |
| taxa de falso link do casador frouxo | **151 de 441 — 34%** |

Somando: o casador estrito produziu 209 links; o frouxo produziria 650, dos
quais 151 estariam comprovadamente errados.

**Ruído da camada IP:** 4.496 de 9.661 marcas (**47%**) caem em `SO_CLASSE_5`,
ambíguo entre defensivo e farmacêutico. **Esta é a maior fonte de ruído do
piloto**, e ela se concentra na Bayer (2.551).

**Ruído da camada PATENTE:** 5 de 5 casos — 100%. Por isso `DEMOTED`.

**Ruído da camada REGULATÓRIA:** 0 eventos emitidos, logo 0 falsos.

---

# N · SUPABASE SCHEMA

`supabase/migrations/019_evento_do_concorrente.sql`
`supabase/migrations/020_views_do_concorrente.sql`

**A migração NÃO cria dono de nada.** Cada entidade continua com seu dono, e a
tabela nova só APONTA:

| entidade | dono, que já existia |
|---|---|
| empresa | `public.organizacao` (002) |
| registro espanhol | `public.registro_regulatorio` (006) |
| produto de catálogo | `public.catalogo_produto` (014) |
| canal / página | `public.canal` (002) |
| cultura / problema | `public.crop`, `public.issue` (004) |
| bruto preservado | `public.raw_asset` (001) |

Marca é a única coisa que nasce aqui, e nasce como **texto num evento** — não
como tabela. Criar um dono de marca na véspera do piloto seria a modelagem
fora de hora que a migração 018 já recusou uma vez.

## As travas, e o que cada uma impede

| trava | o que ela impede |
|---|---|
| `evento_tem_um_dono_so` | a tabela virar depósito comum de outras missões |
| `observacao_nao_e_no_futuro` | erro de carga passando por observação |
| `fato_datado_exige_a_data` | tipo datado sem data — um tipo sem conteúdo |
| `evento_regulatorio_aponta_para_registro` | evento de registro sobre nada |
| `evento_de_ip_tem_marca` | evento de marca sem a marca |
| `meta_e_creator_apontam_para_o_dono` | criar uma **segunda verdade** sobre anúncio |
| **`lead_days_exige_identidade_provada`** | **antecedência sobre identidade não provada** |
| **`defensavel_exige_ordem_e_valor`** | **publicar a refutação como confirmação** |

As duas últimas são as centrais. Sem elas, um link ligado só por nome parecido
carregaria um número de dias — e o número sobrevive à ressalva.

## Read models

| view | o que ela responde | e o que se recusa a responder |
|---|---|---|
| `v_competidor_timeline` | eventos datados em ordem | não é narrativa; dois eventos seguidos não afirmam causa |
| **`v_competidor_cobertura_camada`** | **quantos eventos por camada, INCLUINDO as vazias** | zero é `NOT_COLLECTED`, nunca `NOT_HAPPENING` |
| `v_competidor_antecedencia` | lead days sobre link provado | pares que REFUTAM aparecem escritos, não omitidos |
| `v_competidor_links_recusados` | os pares que o crosswalk recusou | publicar a recusa impede a taxa de acerto de parecer 100% |
| `v_competidor_marcas_recentes` | depósitos do mais recente ao mais antigo | um depósito é ATTENTION ITEM, nunca lançamento |

---

# O · ROWS GRAVADAS

`supabase/importacoes/COMPETITOR-FORESIGHT-2026-08-30.sql`

| | |
|---|---|
| organizações | 6 |
| **eventos** | **10.743** |
| **links** | **209** (207 `PROVED` + 2 recusados) |

**Recusados na entrada, e declarados no cabeçalho do SQL:**
- 1.633 marcas sem classe agro declarada;
- 1 evento sem data do fato;
- **33 pares do crosswalk que não viraram link** — 29 por falta do evento de
  registro, 2 por falta do evento de marca, 2 por faltarem os dois.

> Os 33 mereceram trabalho extra. Um `insert ... select` cujo evento não
> existe **não dá erro: produz zero linhas, em silêncio**. O piloto teria
> afirmado 242 links e gravado 209. A viabilidade passou a ser decidida antes,
> e a perda está escrita no cabeçalho do arquivo.

## Onde este SQL foi provado

**Não** no Supabase. Esta máquina não tem `psql` nem senha do banco.

O arquivo é provado em `.github/workflows/concorrente-portao.yml`, contra um
**Postgres 16 descartável**, que mede:
1. o gerador é determinístico (mesmo SHA-256 duas vezes — verificado localmente);
2. as migrations 001–020 aplicam num banco vazio;
3. a fundação ADAMA (96 registros) entra antes **e sobrevive** ao import;
4. as **28 afirmações** passam — 20 de significado e 8 de red team;
5. as 7 mutações **REPROVAM** — lei que não reprova quando quebrada perdeu os dentes;
6. a view de cobertura mostra as **18 camadas vazias** (6 concorrentes × 3).

**Aplicar em produção é decisão de quem tem a chave, com o arquivo na mão.**

Fora do banco, `tests/test_concorrente.py`: **34 testes, todos passando**.

---

# P · VIEWS / READ MODELS

Ver **N**. As cinco views estão em `020_views_do_concorrente.sql`.

A mais importante é `v_competidor_cobertura_camada`, e ela existe **para expor
uma ausência**: as cinco camadas aparecem sempre, inclusive as vazias, porque
camada que some da listagem é indistinguível de camada que nunca foi tentada.

---

# Q · OS 5 MELHORES EXEMPLOS REAIS

Ver **K**. São cinco, e são as cinco que existem — não uma seleção dos
melhores entre muitos.

Formato `ATTENTION ITEM`, conforme §12 da missão, para o caso mais limpo:

```
COMPETITOR MOVEMENT OBSERVED · CORTEVA · VERDALIS

WHAT HAPPENED   depósito de marca nominativa "VERDALIS" pela Corteva
                Agriscience LLC em três escritórios.
WHEN            IT 2026-07-16 · FR 2026-07-16 · ES 2026-07-17
WHERE           UIBM (IT) · INPI (FR) · OEPM (ES)
EVIDENCE        IT502026000128707 · FR500000005278814 · ES500000004392600
                — três fichas oficiais, com URL navegável
WHAT IS LINKED  nada. NO_LINK: nenhum registro espanhol tem este nome.
WHAT IS NOT     não há produto, não há registro, não há catálogo, não há
  PROVED        anúncio, não há data de mercado. A classe declarada difere
                entre países (1 na IT/FR, 5 na ES), o que enfraquece até a
                leitura de "é um defensivo".
```

**Nunca:** *"a Corteva vai lançar o produto VERDALIS"*.

---

# R · O QUE ESTA CAPACIDADE ACRESCENTA À CONVERGÊNCIA

Ela acrescenta **duas colunas datáveis** ao caso de convergência, e as duas
são fato administrativo verificável:

| coluna | pergunta que ela responde | estado |
|---|---|---|
| `COMPETITOR IP / BRAND EVENT` | que marcas este concorrente depositou, onde, quando | **COMPROVADO** |
| `COMPETITOR REGISTERED RESPONSE` | que autorizações ele detém, com que datas de validade | **COMPROVADO** |

E ela acrescenta **uma chave nova para o join**: `BRAND`, que hoje não existe
em nenhuma outra camada do SINTONIA EAME.

**A ligação com `COUNTRY` e `TIME` está pronta.** A ligação com `CROP` e
`ISSUE` **não está**: o import do ROPF deixou 993 rótulos de cultivo e 195 de
agente fora, porque o casamento com o vocabulário canônico não acontece. Sem
isso, a camada de concorrente **ainda não entra** no eixo cultura×praga que é
o coração da convergência.

**O que ela NÃO acrescenta:**
- não acrescenta `COMPETITOR PRODUCT COMMUNICATION` — camada vazia;
- não acrescenta `COMPETITOR PAID META ACTIVITY` — camada vazia;
- não acrescenta `CREATOR ACTIVITY` — camada vazia;
- não acrescenta score, ranking nem alerta.

---

# S · LIMITAÇÕES EXATAS

1. **Três das cinco camadas da cadeia não foram coletadas.** Catálogo, Meta e
   creator estão `NOT_AVAILABLE`. Nenhuma cadeia fim-a-fim foi fechada. Zero é
   `NOT_COLLECTED`, **nunca** `NOT_HAPPENING`.

2. **Change events regulatórios: zero, num intervalo de 2 dias.** Isto não
   prova estabilidade do registro — prova que ele não mudou nesses dois dias.

3. **O crosswalk é só ES.** O registro do outro lado é espanhol. Marcas IT e FR
   (3.479 delas) **não têm** contra o que ser cruzadas neste piloto.

4. **IT e FR não têm registro local no acervo.** O piloto observa marca nos
   três países e registro em **um**.

5. **A classe de Nice é sinal fraco.** 47% das marcas caem na classe 5, que é
   compartilhada com farmacêutico. E a mesma marca recebe classes diferentes
   em países diferentes (VERDALIS).

6. **Lead-days não são tempo de lançamento.** Mediana de 6 anos entre depósito
   e registro, com faixa de 41 a 11.033 dias.

7. **Em 24% dos pares provados a hipótese do piloto é REFUTADA** — o registro
   precede a marca. Esses 51 pares continuam na base.

8. **O agrupamento de titular é declarado por prefixo, não lido de registro
   societário.** `PROVED` prova que os dois titulares casam com o mesmo
   prefixo declarado, não que pertencem à mesma empresa em direito.

9. **TMview é espelho.** Atraso de sincronização não foi medido.

10. **Patente: `DEMOTED`.** A porta abre, o volume existe, a chave não.

11. **Nada foi aplicado no Supabase de produção.** O SQL é provado em banco
    descartável no GitHub.

12. **Cinco casos de patente não são amostra estatística.** São cinco casos,
    todos negativos, apresentados assim.

13. **O casco não foi alterado.** Migrações 001–018, scripts e réguas
    existentes ficaram como estavam. A fundação ADAMA (96 registros) é
    verificada antes e depois do import.

---

## ARTEFATOS DESTA RODADA

| arquivo | o que preserva |
|---|---|
| `data/samples/COMPETITOR-PILOT-AMOSTRA.json` | a contagem que escolheu os 6 |
| `data/samples/COMPETITOR-IP-TMVIEW.json` | 9.661 marcas, com controle de filtro |
| `data/samples/COMPETITOR-REGULATORY-EVENTS.json` | portão de versão + 2.716 fatos datados |
| `data/samples/COMPETITOR-CROSSWALK.json` | 209 provados, 9 recusados, ruído medido |
| `data/samples/COMPETITOR-EVENTS.json` | 12.377 eventos + 209 timelines |
| `data/samples/COMPETITOR-PATENT-DEMOTE.json` | os 5 casos que rebaixaram a patente |
| `scripts/concorrente_amostra.py` | a amostra sai do registro |
| `scripts/ip_tmview.py` | cliente TMview + portão do filtro ignorado |
| `scripts/concorrente_regulatorio.py` | portão de versão + fatos datados |
| `scripts/concorrente_crosswalk.py` | as duas concordâncias obrigatórias |
| `scripts/concorrente_evento.py` | eventos, timelines e lead-days |
| `scripts/concorrente_importar.py` | gerador determinístico do SQL |
| `supabase/migrations/019_*.sql` `020_*.sql` | tabela derivada + read models |
| `supabase/importacoes/COMPETITOR-FORESIGHT-2026-08-30.sql` | 10.743 eventos + 209 links |
| `supabase/tests/regressoes_concorrente.sql` `mutacao_concorrente.sql` | 28 afirmações + 7 mutações |
| `tests/test_concorrente.py` | 34 testes |
| `.github/workflows/concorrente-portao.yml` | onde o SQL é realmente provado |

---

**PARADO AQUI**, conforme a missão. Nada foi aplicado em produção, o casco não
foi tocado, e nenhuma intenção de concorrente foi inventada.
