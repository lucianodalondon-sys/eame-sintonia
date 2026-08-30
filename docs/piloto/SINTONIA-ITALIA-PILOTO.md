# SINTONIA ITALIA — PRIMEIRA BASE REAL

`COUNTRY = IT` · missão paralela independente · **2026-08-30**

> A Itália não é extensão da Espanha. Este documento existe para que a Itália responda
> perguntas italianas sozinha.

Regra que governou a rodada: **coleta mínima × inteligência máxima demonstrável.**
Não se buscou completude nacional. Buscou-se o menor conjunto de evidência que permita
dizer, com prova: *nesta cultura, nesta região, este problema é relevante, esta é a
janela, estas fontes convergem, e a ADAMA tem ou não tem resposta pública.*

---

## 1 · O QUE MUDOU NO QUE JÁ SE SABIA

Duas afirmações que o repositório carregava sobre a Itália foram **medidas de novo**, e
as duas mudaram. Registrar isso primeiro é obrigatório: são correções, não novidades.

### 1.1 · O portfólio ADAMA italiano tinha o número certo e o dono errado

O Atlas publicava: *"ADAMA ITALIA S.R.L. com 155 autorizações de vencimento futuro —
58 nos próximos 6 meses."*

Os dois números **reproduzem exatamente**. O titular, não. O registro italiano traz
**sete razões sociais** do grupo, e o filtro que gerou aquele número foi a substring
`ADAMA`, que apanha cinco delas. `ADAMA ITALIA S.R.L.` sozinha tem **77**, não 155.

A correção não é trocar um número por outro — é **parar de ter um número só**:

| Escopo | Como se prova | Registros | Vigentes | Venc. futuro |
|---|---|---:|---:|---:|
| `ADAMA_IT_LEGAL_ENTITY` | `ragione_sociale` exata | 240 | 85 | 77 |
| `ADAMA_GROUP_IT_CORE` | **sede administrativa declarada c/o ADAMA ITALIA, VIA ZANICA 19** | 602 | 163 | 155 |
| `ADAMA_IT_ADJACENT` | nome sugere, registro **não** declara | 31 | **0** | 0 |

O vínculo do núcleo não é semelhança de nome: é um **campo que a fonte publica**. Cinco
razões sociais — `ADAMA AGAN LTD`, `ADAMA DEUTSCHLAND GMBH`, `ADAMA IRVITA N.V.`,
`ADAMA MAKHTESHIM LTD` e a própria `ADAMA ITALIA S.R.L.` — convergem para o mesmo
endereço administrativo em Grassobbio (BG). Isso é `MATCHED_WITH_EVIDENCE`, e a evidência
é citável.

**Duas ficam de fora, e é importante que fiquem.** `MAGAN ITALIA S.R.L.` tem outro
endereço; o nome lembra Makhteshim-**Agan**, e é exatamente essa semelhança que a regra
proíbe usar como prova. `MAKHTESHIM AGAN HOLLAND B.V.` declara sede c/o outra razão
social, em outra via. Ambas somam **zero** autorizações vigentes: a ambiguidade existe e
é **provadamente imaterial hoje**. Foi medida em vez de ser resolvida por intuição.

### 1.2 · A Itália sustenta `cultura × alvo`. O Atlas dizia que não

O Atlas registrava, sobre `IT-T4-001`: *"este arquivo não traz cultura nem alvo (…)
portanto a Itália **não** sustenta hoje o mesmo cruzamento cultura × alvo que a França
sustenta."*

A premissa está certa — o CSV aberto realmente não traz. A conclusão não está. A
**etichetta autorizada** é publicada pelo mesmo Ministério, por produto, e traz
`Coltura × Patogeno × Dose × Volumi × Intervallo × N° max applicazioni`, mais a **data do
rótulo**. **O dado existia; faltava a rota.**

A rota foi construída, medida e preservada em `scripts/italia_etichette.py`. Três
defeitos **da fonte** tiveram de ser vencidos sem afrouxar nada — cadeia TLS incompleta,
cabeçalho `Public-Key-Pins` malformado, e **uma busca por sessão** (reusar a sessão
devolve *vazio*, que é indistinguível de "não existe"). Estão documentados no
`MAPA-DE-FONTES-ITALIA.md`.

---

## 2 · A AGRICULTURA ITALIANA, MEDIDA

Ordem de culturas em **nível commodity**, 2024, mil hectares. A não-sobreposição é
**provada aritmeticamente** (`C1100 = C1110 + C1120`, diferença 0,00) e não assumida —
sem essa prova, qualquer ranking pode contar o mesmo hectare duas vezes.

| # | Cultura | mil ha | Top 3 regiões | Conc. top3 |
|---:|---|---:|---|---:|
| 1 | Trigo duro | 1.177,4 | Puglia · Sicilia · Basilicata | 62,1 % |
| 2 | Oliveira | 1.083,0 | **NÃO SEI** — sem NUTS 2 nesta fonte | — |
| 3 | Videira | 715,8 | **NÃO SEI** — sem NUTS 2 nesta fonte | — |
| 4 | Trigo mole | 520,3 | Emilia-Romagna · Veneto · Piemonte | 57,4 % |
| 5 | **Milho grão** | **495,4** | **Veneto 122,9 · Lombardia 115,8 · Piemonte 115,8** | **71,6 %** |
| 6 | Soja | 336,7 | — | 82,9 % |
| 7 | Cevada | 239,1 | — | 26,7 % |
| 8 | Arroz | 226,1 | — | 96,6 % |

**Posição do milho, sem retórica:** 5º geral, **3º entre as culturas anuais**. É grande e
é concentrado — 71,6 % em três regiões contíguas da Planície do Pó. Não é a primeira
cultura da Itália: o trigo duro tem **2,4×** a sua área.

**Limitação que muda decisões:** o Eurostat **não publica oliveira nem videira em NUTS 2**.
Área nacional existe, recorte regional não. Isso é `NÃO SEI`, não zero — e significa que
as duas maiores culturas permanentes do país **não podem ser regionalizadas** pelas fontes
desta rodada. Regionalizá-las exige ISTAT, que continua não alcançado.

---

## 3 · O CAMPO ITALIANO NÃO OLHA PARA O MILHO

Foram medidas as fontes fitossanitárias das **três primeiras regiões de milho**. O achado
é **negativo e é dos mais úteis da rodada**:

| Região | Boletins 2026 | Herbáceas |
|---|---|---:|
| Veneto | 28 olivícola · 24 frutícola · 22 hortícola · 16 videira | **2** |
| Lombardia | 6 videira · 4 macieira | **0** |
| Friuli-VG | seção "colture erbacee" existe | nenhum de milho localizado |

> Nas duas maiores regiões produtoras de milho da Itália, 2026 produziu **~100 boletins
> de culturas permanentes e hortícolas contra 2 de herbáceas** — e o único boletim de
> herbáceas do Veneto que foi aberto trata de **beterraba açucareira / *Cercospora
> beticola***, não de milho.

As três fontes responderam `HTTP 200` e foram lidas. Isto **não** é falha de leitura: é
**ausência medida de cobertura**. O sistema italiano de boletins de campo é construído
para permanentes e hortícolas.

**Distinção que essa camada torna concreta:** `ISSUE_KNOWN` (o *disciplinare* do Piemonte
diz quais problemas o milho tem) **≠** `CURRENT_SIGNAL` (o *bollettino* diz o que está
acontecendo agora). Nenhuma região medida publicou o segundo para milho.

### O único sinal de campo CORRENTE encontrado na Itália

**Veneto · Bollettino Olivo n. 28 · 26/08/2026** — quatro dias antes desta medição:

- **Fenologia observada:** ingrossamento/inolizione; azeitonas em tamanho final,
  entrando em endurecimento e acúmulo de óleo.
- **Alvo:** *Bactrocera oleae*. Pressão estável na semana; **queda térmica + aumento de
  umidade relativa abrindo janela favorável à retomada da ovideposição**.
- **Geografia sub-regional real:** 11 áreas nomeadas com percentual — Alto/Medio/Basso
  lago di Garda, Entroterra gardesano, Colline veronesi (N/C/S), Colli Berici, Colli
  Euganei, Pedemontana vicentina, Grappa–Asolo (3–4 %) e **Litorale veneziano (4–6 %)**.

É `OBSERVED_STAGE` + `CURRENT_SIGNAL` + geografia fina + janela declarada, tudo na mesma
página oficial. É o padrão-ouro do que a camada de campo italiana consegue entregar —
**para oliveira, não para milho.**

---

## 4 · O QUE A CIÊNCIA ITALIANA OLHA

Consulta dirigida (OpenAlex, instituições italianas, 2019+). Mede **atenção científica** —
não pressão de campo, não demanda.

| Recorte | Trabalhos |
|---|---:|
| Xylella × oliveira | 296 |
| Trigo × Fusarium/DON | 243 |
| **Milho × micotoxina/Fusarium** | **208** |
| Videira × *Plasmopara* | 106 |
| Trigo duro × Fusarium | 78 |
| Milho × plantas daninhas | 79 |
| *Bactrocera oleae* | 70 |
| Milho × broca (*Ostrinia*) | 30 |
| Videira × oídio | 26 |
| Milho × *Diabrotica* | 11 |
| *Cercospora beticola* | 5 |
| Milho × resistência a herbicida | **5** |

**Dentro do milho, a atenção científica italiana está em micotoxina** — 2,6× acima de
plantas daninhas e 40× acima de resistência a herbicida.

As 208 obras foram percorridas: **452 autores** com afiliação italiana declarada, com
ORCID, recorrência e última atividade. As pessoas **saem dos trabalhos** — não de uma cota
de "20 pesquisadores italianos".

| Pesquisador | Trab. | Instituição declarada | ORCID | Últ. |
|---|---:|---|---|---:|
| Antonio Logrieco | 27 | CNR | sim | 2026 |
| Paola Battilani | 24 | Università Cattolica del Sacro Cuore | sim | 2026 |
| Antonio Gallo | 18 | Università Cattolica del Sacro Cuore | sim | 2026 |
| Alessandra Lanubile | 16 | Università Cattolica del Sacro Cuore | sim | 2025 |
| Antonio Moretti | 15 | CNR | sim | 2025 |
| Marco Camardo Leggieri | 12 | Università Cattolica del Sacro Cuore | sim | 2026 |
| Massimo Blandino | 9 | University of Turin | sim | 2025 |

**Confundidor declarado antes de ser descoberto depois:** Cattolica (Piacenza), Torino,
Milano e Udine lideram a ciência **e** ficam nas mesmas regiões que lideram a área de
milho. Concordância geográfica pode ser sinal agronômico **ou** densidade institucional.
**Não separado.** É a mesma pergunta que ficou aberta na Espanha — aqui ela nasce
declarada. E vale a lei: `REGION_OF_STUDY ≠ AUTHOR AFFILIATION`.

---

## 5 · A RESPOSTA REGULATÓRIA DA ADAMA, LIDA NO RÓTULO

O rótulo é `REGULATORY_FACT`. Não é venda, não é recomendação, não é disponibilidade
comercial.

**Categoria fitoiátrica das 163 autorizações vigentes do grupo:**
`DISERBANTE` 77 · `FUNGICIDA` 46 · `INSETTICIDA` 16 · `DISERBANTE-ANTIDOTO` 13 ·
`INSETTICIDA-ACARICIDA` 4 · `AFICIDA` 3 · outros 4.

> **O portfólio italiano vigente da ADAMA é liderado por herbicida** — 91 das 163
> autorizações vigentes carregam categoria herbicida.

### Onde o fungicida da ADAMA está: na videira

Dos fungicidas com rótulo analisado, **metade cita videira** — folpet (em muitas
formulações), bupirimate (`FRAC 8`), azoxistrobina + tebuconazol, cimoxanil,
metalaxil-M, fosetil-Al. Tomate vem em seguida; cereais depois.

**Nenhum fungicida da ADAMA cita milho.**

### Onde o milho da ADAMA está: no herbicida

| Categoria | Produtos citando milho | Substâncias |
|---|---:|---|
| `DISERBANTE` | 24 | nicosulfurom · sulcotriona+terbutilazina · dicamba+nicosulfurom+mesotriona · pendimetalina · glifosato · imazamox · fluroxipir · cletodim |
| `INSETTICIDA` / `AFICIDA` | 10 | **clorantraniliprole (IRAC 28, registro de 2026)** · tefluthrin (solo) · lambda-cialotrina · pirimicarbe · óleo de parafina |
| `MOLLUSCHICIDA` | 1 | metaldeído |
| **`FUNGICIDA`** | **0** | — |

Os grupos de modo de ação vêm **declarados no próprio rótulo**: `HRAC 2 (B)` ALS ·
`HRAC 5 (C1)` · `HRAC 27 (F2)` HPPD · `HRAC 3 (K1)` · `HRAC 4 (O)` · `HRAC G` ·
`IRAC 3A`. Isso é matéria-prima direta de **manejo de resistência**.

> **Uma armadilha que quase entrou no relatório.** A primeira leitura dizia "23 produtos
> citam milho". **Seis** deles — GOLTIX, GOLTIX 700 SC, GOLTIX BETA, GOLTIX TOP, NORTIM e
> GOLD-BEET, todos METAMITRON — são herbicidas de **beterraba**. `mais` aparece no rótulo porque a
> etichetta declara o que se pode semear **depois**, em caso de falha da cultura:
> *"patate e mais possono essere seminate in seguito ad aratura profonda."* Isso é
> **restrição de sucessão — o oposto de autorização de uso.** O parser agora separa
> `CROP_TERM_PRESENT` de `ROTATION_CONTEXT_ONLY`.

---

## 6 · O GÊMEO PÚBLICO NÃO FOI OBTIDO — e isso é uma recusa, não um buraco

`adama.com` devolve **HTTP 403 "Access Denied"** (WAF de origem) em todas as rotas
testadas, **inclusive `/robots.txt`**, por duas vias de saída distintas. O proxy da sessão
não registrou falha.

A missão informa que o site apresenta ~52 produtos em 27 Erbicidi / 14 Fungicidi /
6 Insetticidi / 5 Speciali, e manda **reproduzir na fonte, não copiar sem verificar**.
Não foi possível verificar. **Esses números não entram em nenhum artefato como fato** —
ficam como `UNVERIFIED_INPUT`.

**O que se perde, nomeado:** `POSITIONING` · `TECHNICAL_CLAIMS` · `COMMERCIAL_CLAIMS` ·
`PACK_SIZES` · `LAUNCH_SIGNALS` · pertencimento ao Catalogo 2026 ·
**`PUBLIC_ADAMA_MAIZE_SIGNAL`** (os conteúdos de campo de milho de 2026 citados no
enunciado **não foram reproduzidos** e portanto não são afirmados).

**O que não se perde:** a resposta **regulatória**, que veio inteira e é mais forte para
a pergunta desta missão.

**Contraste que a rodada permite medir:** 163 autorizações vigentes contra ~52 produtos
de catálogo relatados — razão de ~3,1×. É a demonstração numérica de
`REGISTRATION ≠ COMMERCIAL CATALOG`. Como o denominador comercial é `UNVERIFIED_INPUT`,
a razão fica como **ilustração da lei, não como métrica publicável**.

---

## 7 · HERO CASES

Três candidatos. Nenhum é escolhido por preferência: cada um é forte numa perna e fraco
noutra, e as pernas estão medidas.

### `IT-HERO-001` · VIDEIRA × FLAVESCÊNCIA DOURADA (*Scaphoideus titanus*) × LOMBARDIA
**As quatro pernas, e a janela está ABERTA hoje.**

| Perna | Estado | Evidência |
|---|---|---|
| ESCALA | 715,8 mil ha — 3ª cultura do país · **região: `NÃO SEI`** | `EU-T1-001` |
| CAMPO | **`CURRENT_SIGNAL`** — Bollettino Regionale LA VITE n.6, **31/07/2026** | `IT-T3-003` |
| JANELA | **`OPEN`** — *"da inizio agosto alla fine settembre"* para reconhecer sintomas foliares; hoje é **30/08** | idem |
| CIÊNCIA | fitoplasma da videira **135** · *Scaphoideus titanus* **66** | `IT-T5-001` |
| **ADAMA** | **6 produtos vigentes com *Scaphoideus titanus* como ALVO DECLARADO no rótulo** | `IT-T4-001-ETICHETTA` |

A resposta registrada não é inferida — está escrita na etichetta oficial, com dose:

> *"Vite (da vino e da tavola) — Contro cicaline (Empoasca vitis, **Scaphoideus titanus**)
> e tripidi (…) impiegare a 30-300 ml/hl senza superare 0,3 l/ha in 100-1000 litri di
> acqua/ha."*

`KLARTAN 20 EW` · `KLARTAN SMART` · `TAU AL 240 EW` · `MAVRIK EW` · `MAVRIK SMART` ·
`EVURE PRO` — todos **TAU-FLUVALINATE**.

**Por que este é o caso:** é o único em que **escala, sinal de campo corrente, janela
agronômica aberta, ciência e resposta registrada da ADAMA** apontam para o mesmo
`CROP × ISSUE × REGION` **ao mesmo tempo**. O boletim oficial ainda remete ao
*Documento tecnico ufficiale n. 29 dei Servizi Fitosanitari Nazionali*, o que dá ao caso
uma camada institucional nacional além da regional.

**Ressalva que não pode ser apagada:** o boletim descreve a janela para **reconhecer
sintomas foliares** da doença. O produto da ADAMA atua sobre o **vetor**, não sobre o
fitoplasma. As duas coisas são do mesmo caso, mas **não são a mesma janela** — a janela de
controle do vetor tem de ser medida, e não foi. `WINDOW_FOR_VECTOR_CONTROL = NÃO SEI`.

**O que falta:** regionalizar a área de videira (exige ISTAT); medir a janela do vetor;
confirmar se a mesma janela vale no Vêneto.

> **Nota de método.** Este caso quase não apareceu. Ele só surgiu porque o
> `NEXT_SMALLEST_STEP` — *"abrir o boletim de videira da safra corrente"* — foi executado
> em vez de deixado como recomendação. A leitura anterior supunha míldio/oídio, que é o
> que a ciência mais estuda em videira; o campo, em 31/07, falava de **flavescência**,
> porque a estação do míldio já tinha fechado. **A ciência dizia uma coisa e o calendário
> dizia outra, e quem manda na janela é o calendário.**

### `IT-HERO-002` · OLIVEIRA × *Bactrocera oleae* × VÊNETO
**O sinal de campo mais fino do país — e sem resposta ADAMA.**

| Perna | Estado |
|---|---|
| ESCALA | 1.083,0 mil ha, 2ª cultura · **região: `NÃO SEI`** |
| CAMPO | **`CURRENT_SIGNAL` de 26/08/2026** — 11 sub-áreas nomeadas, 3–6 %, janela declarada |
| JANELA | **`OPEN`** — queda térmica + umidade abrindo retomada da ovideposição |
| CIÊNCIA | *Bactrocera* 70 · (Xylella domina a oliveira italiana com **296**) |
| **ADAMA** | **resposta ao alvo NÃO ENCONTRADA** — presença em oliveira é herbicida de solo + óleo de parafina |

**Por que importa mesmo assim:** é a melhor demonstração do que a camada de campo italiana
consegue entregar — fenologia observada, pressão percentual por sub-área e janela, tudo
datado e oficial. **O que falta:** a ADAMA não tem, nos rótulos analisados, produto com
*Bactrocera oleae* como alvo declarado.

### `IT-HERO-003` · MILHO × PLANÍCIE DO PÓ — **dois problemas candidatos, medidos**

| Perna | Estado |
|---|---|
| ESCALA | 495,4 mil ha · 3ª anual · **71,6 % em Veneto + Lombardia + Piemonte** |
| CAMPO | **ausência medida** — nenhum boletim de milho nas três regiões |
| **ADAMA** | 24 herbicidas · 9 inseticidas · **0 fungicidas** |

O milho tem **dois** problemas candidatos, e eles ganham em pernas diferentes. Escolher um
sem dizer isso seria esconder a medição:

| | DANINHAS | ***Ostrinia nubilalis* / lepidópteros** |
|---|---|---|
| Produtos ADAMA | **24** | 1 (`COSAYR 200 SC`) |
| Modo de ação | **≥6 grupos HRAC** | IRAC 28 (diamida) |
| Ciência italiana | 79 | 30 |
| Registro | portfólio maduro | **18561, de 04/02/2026 — novo** |
| Época no rótulo | não extraída | **sim: *"intervenire in fase di ovideposizione"*** |

O rótulo do produto novo é explícito, e é `REGULATORY_FACT`:

> *"Mais e Mais Dolce: utilizzare 100-150 mL/ha per il controllo di **O. nubilalis** e
> lepidotteri nottuidi quali H. armigera, S. exigua, S. littoralis, **Sesamia spp.**
> Intervenire in fase di ovideposizione."*

**Uma ponte tentadora foi testada e NÃO passou.** O dano da broca é, agronomicamente, porta
de entrada de *Fusarium* — o que ligaria o produto novo ao cluster científico dominante do
milho italiano (208 trabalhos em micotoxina). Se a ponte existisse, este seria o melhor caso
da Itália. Foi medida: **milho × *Ostrinia* × micotoxina = 5 trabalhos italianos.** Cinco é
pouco demais. A ligação é plausível e **não está provada aqui** — fica como hipótese, com o
teste que a mediria já escrito.

**A tensão do milho, dita sem suavizar:** a ciência italiana do milho olha para
**micotoxina** (208, 2,6× as daninhas). A ADAMA tem **zero fungicidas** citando milho. As
duas coisas são fatos medidos; a distância entre elas **não** é prova de lacuna comercial
nem de erro de portfólio — daninhas é mercado legítimo e grande, e manejo de micotoxina em
milho é largamente agronômico.

**Sobre a prioridade estratégica declarada.** `STRATEGIC_ADAMA_EAME_PRIORITY(MAIZE) = HIGH`
veio do enunciado e é respeitada como entrada. A medição **não a contradiz**: o milho
italiano é grande, concentrado, e o portfólio recebeu registro novo em 2026. O que a
medição mostra é que o milho é, dos três candidatos, **o de menor evidência demonstrável
hoje** — sem sinal de campo e sem janela que vire data. Isso é informação para a decisão,
não argumento contra ela.

---

## 8 · MAPA DE AÇÃO — quem poderia agir

Sem dado interno da ADAMA, `COMMERCIAL_CLOCK = NÃO SEI` em todas as linhas.

| Área | Ação | Por quê agora | Evidência | Horizonte |
|---|---|---|---|---|
| REGULATORY / PORTFOLIO | Revisar as **71** autorizações do grupo que vencem em 6 meses de calendário | 13 delas vencem **na mesma data**, 2027-02-28 | `IT-T4-001` | **AGIR AGORA** |
| REGULATORY | Conferir as **8** autorizações vigentes com vencimento já passado | o campo de estado atrasa ≥ 9 dias | `IT-T4-001` | **AGIR AGORA** |
| MARKET DEVELOPMENT | **Caso videira × flavescência na Lombardia** | **janela aberta agora** (ago–set) e resposta registrada existente | `IT-HERO-001` | **AGIR AGORA** |
| SCIENCE | Abrir contato com o cluster de micotoxina em milho | 208 trabalhos, autores com ORCID e atividade em 2026 | `IT-T5-001` | PREPARAR |
| MARKETING | Manejo de resistência em daninhas de milho, com os MoA do próprio rótulo | ≥6 grupos declarados no portfólio | `IT-HERO-003` | PLANEJAR |
| COMMERCIAL | — | **nada a propor**: sem dado de venda, qualquer ação seria fabricada | — | — |

Não se fabrica urgência: as duas linhas de `AGIR AGORA` são as únicas com data própria.

---

## 9 · CROSS-MARKET — apenas indicado

`CROSS_MARKET_RELATION = NOT_TESTED`

Candidatos anotados para quando houver evidência comparável dos dois países: **milho**;
**cereais de inverno**; **videira × míldio** (Espanha tem `ES-T3-001`, Itália tem a
camada regional mais rica); e por **molécula** — folpet, tebuconazol, azoxistrobina,
glifosato, nicosulfurom aparecem nos dois registros. Nada foi cruzado.

---

## 10 · ENTREGA

### A · GIT
`BRANCH` = `claude/sintonia-italy-pilot-b1l401` · `TESTS` = **307, 0 falhas** · `PUSHED` = SIM

### B · SOURCES
`OFFICIAL_SOURCES` = 9 · `STRUCTURED` = 3 (CSV/JSON/XML, API JSON-stat, API REST) ·
`APIS` = 2 · `REGIONAL_FIELD_SOURCES` = 5 regiões

### C · REGULATORY
`ITALY_TOTAL_REGISTRATIONS` = **17.695** · `CURRENT_AUTHORIZED` = **3.712** ·
`DISTINCT_HOLDERS` = **576**
`ADAMA_IT_REGISTRATIONS` = **602** (grupo) / **240** (entidade italiana)
`ADAMA_IT_ACTIVE` = **163** / **85** · `ADAMA_IT_REVOKED` = **425** · `EXPIRED` = **14**
`ADAMA_IT_ACTIVE_SUBSTANCES` = **53** (grupo) / **36** (entidade)
`EXPIRING_6M` = **71** (calendário) · **58** (180 dias) — *a convenção muda a resposta*
`EXPIRING_12M` = **104**
`ACTIVE_WITH_PAST_EXPIRY` = **8** (anomalia)

### D · ADAMA PUBLIC PORTFOLIO
`CURRENT_CATALOG_TOTAL` = **NÃO OBTIDO** (403 de origem) ·
`CATALOG_52_CLAIM` = `UNVERIFIED_INPUT`
`OFFICIAL_LABELS_AVAILABLE` = 163 alvos · `OFFICIAL_LABELS_PRESERVED` = **161 (98,8 %)**
— 33,8 MB, com SHA-256 por arquivo, **não versionados**
`LABEL_DATE` obtida em **159** rótulos, de 2016-12-19 a 2026-07-29
`PRODUCT_PAGES_PARSED` = **162** · `CROP_TERM_RELATIONS` e `ISSUE_RELATIONS` extraídos do
rótulo · `TECHNOLOGIES` = grupos HRAC/FRAC/IRAC declarados (36 % dos rótulos declaram)
`TECHNICAL_CLAIMS` / `COMMERCIAL_CLAIMS` = **NOT_COLLECTED** (fonte bloqueada)

Os **2** rótulos não obtidos (`FOLPAN ENERGY`, `AGHARTA`) são `NÃO OBTIDO`, **não**
`não existe`: na primeira passada faltavam **14**, e **12 foram recuperados só por
esperar mais**. `READ FAILURE ≠ ZERO`, demonstrado com número.

### E · AGRICULTURE
`TOP_CROPS` = trigo duro · oliveira · videira · trigo mole · **milho**
`MAIZE_POSITION` = **5º commodity, 3º anual** · `MAIZE_TOP_REGIONS` = Veneto ·
Lombardia · Piemonte (**71,6 %**)

### F · ISSUES / TIME
`CURRENT_FIELD_SIGNALS` = **2** — oliveira × *Bactrocera* × Vêneto (26/08/2026) e
videira × flavescência × Lombardia (31/07/2026)
`CURRENT_AGRONOMIC_WINDOWS` = **2 abertas** · `MAIZE_FIELD_SIGNAL` = **NOT_FOUND (medido)**

### G · SCIENCE
`SCIENCE_DISCOVERY_READY` = **SIM** · `RELEVANT_PAPERS` = 208 no recorte profundo ·
`RESEARCHERS_FOUND` = **452** · `IDENTITY_CONFIRMED` = via ORCID ·
`RESEARCHERS_WITH_PUBLIC_CHANNELS` = **0 — NOT_COLLECTED**

### H · VOICE
Tudo **NOT_STARTED**. A missão manda vir depois dos pares; os pares ficaram prontos agora.
Pista real registrada: **Co.Pro.B.**, cooperativa que opera um DSS de *Cercospora* citado
pelo boletim oficial do Vêneto — cooperativa que **produz** sinal de campo.

### I · PILOT
`HERO_CASE_CANDIDATES` = **3** · `BEST_CURRENT_CASE` = **`IT-HERO-001`** — videira ×
flavescência dourada × Lombardia, **único com as quatro pernas e janela aberta** ·
`BEST_MAIZE_CASE` = `IT-HERO-003` (daninhas) · `OPEN_DECISION_WINDOW_CANDIDATES` = **2**

### J · CROSS-MARKET
`CROSS_MARKET_RELATION` = **NOT_TESTED**

### K · COST
`APIFY_USED` = **NÃO** · `APIFY_COST` = **US$ 0,00** · `OTHER_PAID_COST` = **US$ 0,00**

### L · STATE
`ITALY_FOUNDATION_READY` = **SIM** · `ITALY_PRIORITY_MATRIX` = **SIM** ·
`ITALY_PERSON_DISCOVERY_READY` = **SIM** · `ITALY_PILOT_INTELLIGENCE_READY` = **PARCIAL**
`READY_TO_DESIGN_ITALY_PORTAL` = **NÃO — e parar aqui é a instrução**

`SUPABASE_PERSISTENCE` = **NÃO FEITO** — não há credencial neste ambiente. Declarar é
obrigatório; fingir persistência não é opção. Convenção `IT/<source>/<run>/<asset>` já
gravada em cada registro de rótulo, pronta para quando houver credencial.

### BLOCKERS
1. `adama.com` bloqueado por WAF de origem → camada de afirmação do fabricante inacessível.
2. ISTAT não alcançado → oliveira e videira sem regionalização.
3. Sem credencial Supabase → persistência não executada.
4. Calendário agronômico regional não coletado → janela do milho `NOT_DERIVED`.

### NEXT_SMALLEST_STEP
**Medir a janela de controle do VETOR em `IT-HERO-001`.** O boletim de 31/07 dá a janela
para *reconhecer sintomas* da flavescência (ago–set); o produto da ADAMA atua sobre
*Scaphoideus titanus*. São o mesmo caso e **não são a mesma janela**. Um documento — o
*disciplinare* de videira da Lombardia ou o Documento tecnico ufficiale n. 29 — decide se
existe decisão acionável **nesta safra** ou só na próxima.

O passo anterior era *"abrir o boletim de videira da safra corrente"*, e foi executado
dentro desta mesma rodada: foi ele que trocou o caso de míldio para flavescência e
mostrou uma janela aberta. **O menor passo seguinte costuma valer mais que a próxima
grande coleta.**
