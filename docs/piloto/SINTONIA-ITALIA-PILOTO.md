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

> **CORREÇÃO DA SEGUNDA RODADA — `NOT_FOUND ≠ DOES NOT EXIST`.** A frase acima continua
> verdadeira sobre Vêneto, Lombardia e Piemonte. A conclusão que eu tirei dela — "o milho
> italiano não tem sinal de campo" — estava errada. O **Friuli-Venezia Giulia** publica
> série própria de boletim do MILHO: **10 números em 2026**, o último de **12/08/2026**,
> sob difesa integrata obbligatoria (art. 19 D.lgs. 150/2012). Eu tinha lido a página-mãe
> das *colture erbacee* e não a subpágina `bollettini-2026`. O achado negativo estava
> certo no escopo e **errado no rótulo**, e a diferença entre as duas coisas é o tamanho
> de um clique.

As fontes das três primeiras regiões responderam `HTTP 200` e foram lidas: para elas, a
ausência de boletim de milho é medida. O que mudou é que ela **não vale para a Itália** —
vale para as regiões medidas. E o desalinhamento que sobra é outro, e é real: o sinal
existe na **5ª** região de milho (6,7 % da área), não nas três primeiras (71,6 %).

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

## 7 · HERO CASES — `ITALY-HERO-CASES-V1`

Três casos. Nenhum escolhido por preferência: cada perna é medida por conta própria, e a
perna que falta aparece como falta. `CONVERGENCE` é **contagem** de pernas com evidência,
nunca escore ponderado — peso seria opinião disfarçada de número.

### `IT-HERO-001` · VIDEIRA × FLAVESCÊNCIA DOURADA (*Scaphoideus titanus*) × **VÊNETO** + LOMBARDIA
**5/5 pernas.** O caso mais completo da Itália.

| Perna | Medida |
|---|---|
| ESCALA | 588,8 mil ha nacional (ISTAT) |
| ESCALA REGIONAL | **Vêneto 101,0 (17,2 %, 2º)** · Lombardia 18,2 (3,1 %, 7º) |
| SINAL | Bollettino vite Vêneto **n. 19 de 13/08/2026** |
| CIÊNCIA | fitoplasma da videira 135 · *Scaphoideus titanus* 66 |
| ADAMA | **6 produtos nomeiam o vetor no rótulo**, com dose |

> **A região do caso mudou, e quem decidiu foi a área.** A rodada anterior chamou o caso
> de "Lombardia" porque de lá veio o decreto mais claro. O Vêneto tem **5,5×** mais
> videira e a **mesma** obrigação legal. Documento achado primeiro não é critério.

**A obrigação é norma, e agora tem data.** Executar o `NEXT_SMALLEST_STEP` entregou os dois
atos:

| | LOMBARDIA | VÊNETO |
|---|---|---|
| Ato | Comunicato Giunta 25/05/2026 n. 39 (BURL 28/05) | DDR n. 13645 de 14/05/2026 |
| Datas | **no próprio ato** | **não** — delega ao boletim semanal |
| 2 tratamentos | 1º 2–14/06 · 2º 17–29/06 | 1ª janela 8–19/06 · 2ª a 10–15 dias |
| 3 tratamentos | 1º 2–14/06, seguintes a 10–14 dias | 1–11/06, seguintes a 7–12 dias |

**Não existe "o calendário italiano".** Existe um por região, com mecanismos de publicação
diferentes: a Lombardia resolve num documento, o Vêneto exige dois — e o segundo muda toda
semana.

**A regra de elegibilidade liga a norma ao portfólio.** A Lombardia admite
**exclusivamente** produtos cujo rótulo traga como alvo `«cicaline della vite»` ou
`«Scaphoideus titanus»`; o Vêneto lista `Tau-fluvalinate` e `Lambda-cialotrina` entre os
ativos de síntese admitidos, para 1º **e** 2º tratamento. Medido contra os 163 rótulos:

- **6 tau-fluvalinate** — nomeiam a espécie **e** o genérico. Vencem **31/01/2027**.
- **4 lambda-cialotrina** — trazem `«cicaline»`. Vencem **31/08/2026**.
- 2 óleo de parafina — fora da lista de sintéticos do Vêneto.

> **O achado que não estava previsto.** O portfólio elegível para uma obrigação legal
> **anual** vence inteiro em cinco meses, e 4 dos 10 sintéticos vencem **amanhã**. Os
> outros 6 vencem ~4 meses **antes** de a janela de 2027 abrir, e antes do mês em que as
> duas regiões publicam o ato. `EXPIRY ≠ WITHDRAWAL` continua valendo inteira — re-registro
> é rotina e `RENEWAL_STATUS = NÃO SEI` —, mas a data pede revisão.

**As duas janelas, medidas, não coincidem:**
`APPLICATION_WINDOW = CLOSED_FOR_2026` · `MONITORING_WINDOW = OPEN` (sintoma, ago–set) ·
`NEXT_CYCLE = TO_BE_CONFIRMED`, `PREPARE_BY 2027-05-31`.

A obrigação recorre por norma europeia; as **datas** são fixadas a cada ano pelo
monitoramento, e o ato lombardo de 2026 registra que a estação **antecipou** o ciclo do
escafoide. Projetar 2026 sobre 2027 seria ignorar o aviso da própria fonte.

### `IT-HERO-002` · MILHO × PIRALIDE + *DIABROTICA* × **FVG** (sinal) e VALE DO PÓ (escala)
**5/5 pernas.** O melhor caso de milho — e não é o de daninhas nem o de micotoxina.

| Perna | Medida |
|---|---|
| ESCALA | 495,4 mil ha · 5º commodity, **3º entre as anuais** · ISTAT = Eurostat, idêntico |
| ESCALA REGIONAL | Vêneto 122,9 · Lombardia 115,8 · Piemonte 115,7 (**71,6 %**) · **FVG 33,1 (6,7 %)** |
| SINAL | ERSA FVG **n. 15 MAIS de 12/08/2026**, série de 10 números em 2026 |
| CIÊNCIA | *Ostrinia* 30 · *Diabrotica* 11 · (micotoxina domina com 208) |
| ADAMA | **6 produtos nomeiam piralide e/ou *Diabrotica*** no rótulo do milho |

O boletim traz fenologia observada (**BBCH 65-75**), o voo de 3ª geração iniciado, o pico
de ovideposição previsto — e o **limiar publicado**: tratar se houver `>3 ovaturas por 100
plantas` e/ou larvas em `30–40 % de 50–100 espigas`.

**A janela está aberta e é estreita, e a fonte diz por quê:** as populações de 3ª geração,
embora maiores, **não** causam dano porque as espigas estão em maturação avançada —
**exceto** em semeadura tardia (junho) e milho de segundo raccolto.

A resposta registrada tem duas camadas:
- **adulto** — `FORZA` · `NINJA` · `DURAVIS` · `ELTIRA` (lambda-cialotrina), rótulo:
  *"Mais … **Piralide, Diabrotica virgifera virgifera** 560-1000"*. Vencem **31/08/2026**.
- **larva/solo** — `LEBRON 0.5 G` · `SCHERMO 0.5 G` (tefluthrin, IRAC 3A), rótulo:
  *"Mais, Mais Dolce, Sorgo — Agriotes sp., Agrotis sp., **Diabrotica sp.** …"*.
  Vencem **31/05/2027**.
- e `COSAYR 200 SC` (clorantraniliprole, IRAC 28, registro **18561 de 04/02/2026**):
  *"Mais e Mais Dolce: 100-150 mL/ha per il controllo di **O. nubilalis** … Intervenire in
  fase di ovideposizione"*. `NEW_REGULATORY_RESPONSE / RECENT_REGISTRATION` — e nada além
  disso: lançamento comercial, estoque e relação com o lançamento de milho EAME **não são
  afirmados**.

**A âncora de 2027 vem da própria fonte**, não de dedução nossa: *"il trattamento
effettuato nell'anno in corso avrà effetto sulla diabrotica presente in campo nell'anno
successivo; se non si prevede di coltivare mais l'anno prossimo, il trattamento non è
necessario"*. A decisão de 2027 se toma em 2026.

**A ponte tentadora continua reprovada.** Broca → *Fusarium* → micotoxina ligaria este caso
ao cluster de 208 trabalhos. Medida: **5 trabalhos**. `THIN_EVIDENCE`. Não foi publicada.

**Não há lotta obbligatoria para milho:** a de *Diabrotica* foi **revogada** pelo D.M.
13/06/2014. O que existe é difesa integrata obbligatoria, que obriga o **método**, não um
tratamento com data.

### `IT-HERO-003` · PORTFÓLIO × CALENDÁRIO DE VENCIMENTOS × NACIONAL
**3/5 pernas — e a única ação externa, defensável e imediata.**

```
ADAMA vigentes                    163
vencendo em 180 dias               58
vencendo em 6 meses de calendário  71      ← 13 de diferença, todas em 2027-02-28
vencendo em 12 meses              104
vencendo em 31/08/2026              7
vigentes com vencimento passado     8      REGULATORY_STATUS_LAG / INVESTIGATE
```

Culturas mais atingidas na janela de 6 meses: **maçã 36 · beterraba 35 · videira 34 ·
tomate 31 · batata 31**. As 34 de videira encostam direto no `IT-HERO-001`.

O atraso de estado **não** é chamado de erro do Ministero: não há fonte que sustente a
acusação. Pode ser fluxo administrativo, prorrogação não publicada ou defasagem do extrato
aberto. `INVESTIGATE`, não `DATABASE_ERROR`.

### `IT-DEMO-001` · OLIVEIRA × *Bactrocera oleae* × VÊNETO — **não é caso**

Fica registrado porque prova o que a camada de campo italiana consegue: fenologia
observada, pressão percentual em **11 sub-áreas nomeadas** (3–6 %) e janela declarada, tudo
oficial e datado de **26/08/2026**. Duas coisas o desqualificam como caso:

1. **`SIGNAL QUALITY ≠ REGIONAL WEIGHT`** — o Vêneto tem **5,3 mil ha** de oliveira,
   **0,5 %** do país. A oliveira italiana está em Puglia (347,8), Calabria (184,7) e
   Sicilia (161,7), e o serviço fitossanitário dessas três **não foi medido**.
2. **`NO_REGISTERED_RESPONSE`** — nenhum dos 163 rótulos nomeia *Bactrocera oleae*. Os dois
   inseticidas que citam olivo declaram, **em olivo**, `"Cocciniglie e Tignole"`. Não é
   ambíguo: é decisivo.

`APPLICATION_WINDOW = NOT_KNOWN` — "condições favoráveis à retomada da ovideposição" é
condição do inseto, não janela de aplicação.

---

## 8 · AS TRÊS CAPACIDADES, FECHADAS

| | Caso | Por quê |
|---|---|---|
| **AGIR AGORA** | `IT-HERO-003` | revisar vencimento é ação externa, defensável e com data própria |
| **MONITORAR AGORA** | `IT-HERO-002` | janela aberta e estreita, com limiar publicado |
| **PREPARAR** | `IT-HERO-002` | a fonte ancora a decisão de 2027 no tratamento de 2026 |
| **PLANEJAR PRÓXIMO CICLO** | `IT-HERO-001` | obrigação anual; janela 2027 a confirmar, `PREPARE_BY` 31/05 |
| **MELHOR DEMONSTRAÇÃO** | `IT-HERO-001` | obrigação legal + sinal corrente + ciência + resposta registrada elegível pelo critério do próprio decreto |

### Mapa de ação

| Área | Ação | Horizonte |
|---|---|---|
| REGULATORY / PORTFOLIO | revisar as 71 que vencem em 6 meses; 7 vencem em 31/08 | **AGIR AGORA** |
| REGULATORY / PORTFOLIO | investigar as 8 com vencimento passado e estado ativo | **AGIR AGORA** |
| MARKET DEVELOPMENT | monitorar sintoma de flavescência no Vêneto | MONITORAR AGORA |
| MARKET DEVELOPMENT | acompanhar ovideposição de piralide no FVG com o limiar publicado | MONITORAR AGORA |
| SCIENCE | abrir contato com o cluster de micotoxina em milho | PREPARAR |
| MARKETING | material de manejo de resistência com os grupos do próprio rótulo | PREPARAR |
| MARKET DEVELOPMENT | preparar o ciclo 2027 da flavescência antes de 31/05 | PLANEJAR |
| COMMERCIAL | **nada a propor** — sem dado interno seria fabricação | — |

`COMMERCIAL_CLOCK = NÃO SEI` em todas as linhas, e **nenhuma ação proposta depende dele**.

---

## 9 · ASK SINTONIA ITALIA

`scripts/ask_sintonia_italia.py` — **14 perguntas · 6 ANSWERABLE · 3 PARTIAL · 5 REFUSE.**

Um Ask que responde tudo não está medindo nada: **a recusa é o ativo**. As cinco regressões
vigiam as confusões que já custaram medição nesta branch, e passaram a **reprovar a suíte**
— porque regressão que só vive num script não protege quem edita um artefato sem rodá-lo.

```
SYMPTOM WINDOW ≠ APPLICATION WINDOW      READ FAILURE   ≠ NO LABEL
AFFILIATION    ≠ STUDY GEOGRAPHY         REGISTRATION   ≠ COMMERCIAL CATALOG
GENERIC TARGET ≠ SPECIFIC TARGET
```

---

## 10 · CROSS-MARKET — apenas indicado

`CROSS_MARKET_RELATION = NOT_TESTED` · `CROSS_MARKET_READY = NO`

Dimensões comparáveis declaradas em `docs/piloto/HANDOFF-ITALIA-PARA-EAME.md`, seção H.
Nada foi cruzado.

---

## 11 · ENTREGA

### A · REPO
`BRANCH` = `claude/sintonia-italy-pilot-b1l401` · `TESTS` = **319, 0 falhas** · `PUSHED` = SIM

### B · REGULATORY
`ADAMA_GROUP_ACTIVE` = **163** · `LABELS_OBTAINED` = **163/163 (100 %)** ·
`LABELS_UNRESOLVED` = **0**
`EXPIRING_CALENDAR_6M` = **71** · `EXPIRING_180D` = **58** ·
`EXPIRED_BUT_ACTIVE_STATUS` = **8** · `STATUS_LAG_CASE` = `REGULATORY_STATUS_LAG / INVESTIGATE`

### C · VINE
`REGION` = **Vêneto** (101,0 mil ha, 17,2 %) + Lombardia (18,2) ·
`CURRENT_SIGNAL` = bollettino n. 19, 13/08/2026 · `VECTOR` = *Scaphoideus titanus*
`ADAMA_EXPLICIT_RESPONSES` = **6** (+4 genéricos elegíveis) ·
`VECTOR_CONTROL_WINDOW_2026` = **CLOSED** (junho) · `SYMPTOM_WINDOW` = **OPEN** (ago–set)
`NEXT_CYCLE_DATES` = **TO_BE_CONFIRMED**, `PREPARE_BY` 2027-05-31 ·
`REGIONAL_VINE_AREA` = **OBTIDA** · `CASE_STATUS` = **5/5** ·
`ACTION_HORIZON` = MONITORAR AGORA + PRÓXIMO CICLO

### D · OLIVE
`REGION` = Vêneto · `SIGNAL_DATE` = 26/08/2026 · `BACTROCERA_PRESSURE` = 3–6 % em 11 sub-áreas
`ADAMA_RESPONSE` = **NO_REGISTERED_RESPONSE** · `APPLICATION_WINDOW` = **NOT_KNOWN** ·
`MONITORING_WINDOW` = OPEN
`CASE_STATUS` = **demonstração de capacidade, não é caso** (Vêneto = 0,5 % da oliveira) ·
`ACTION_HORIZON` = sem ação de produto

### E · MAIZE
`AREA` = 495,4 mil ha · `TOP_REGIONS` = Vêneto · Lombardia · Piemonte (71,6 %)
`CURRENT_FIELD_SIGNAL` = **SIM — ERSA FVG n.15, 12/08/2026** (correção da rodada anterior)
`SCIENCE_MAIN_CLUSTER` = micotoxina/Fusarium (208) ·
`SELECTED_ISSUE` = **piralide + *Diabrotica*** — o único com alvo declarado, limiar publicado e sinal corrente
`COSAYR_OSTRINIA_RESPONSE` = confirmado, registro 18561 de 04/02/2026, IRAC 28
`APPLICATION_WINDOW` = **OPEN_BUT_NARROW** · `CASE_STATUS` = **5/5** ·
`ACTION_HORIZON` = MONITORAR AGORA + PREPARAR

### F · CASE PACK
`BEST_AGIR_AGORA` = `IT-HERO-003` · `BEST_PREPARAR` = `IT-HERO-002` ·
`BEST_PLANEJAR_NEXT_CYCLE` = `IT-HERO-001` · `BEST_DEMO_CASE` = `IT-HERO-001` ·
`ITALY_HERO_CASES_READY` = **SIM**

### G · ASK SINTONIA
`QUESTIONS` = 14 · `ANSWERABLE` = 6 · `PARTIAL` = 3 · `REFUSED` = 5 ·
`FALSE_CONFIDENCE_REGRESSIONS` = **5, todas na suíte**

### H · EAME HANDOFF
`COMPARABLE_DIMENSIONS` = 7 declaradas · `CROSS_MARKET_CANDIDATES` = milho · cereais ·
videira × doença · molécula · `CROSS_MARKET_READY` = **NO**

### I · READINESS
`ITALY_PRIORITY_MATRIX` = SIM · `ITALY_PILOT_INTELLIGENCE_READY` = **SIM** ·
`ITALY_DEMO_CONTENT_READY` = **SIM** · `READY_TO_DESIGN_ITALY_PORTAL` = **NÃO — e parar aqui
é a instrução**

### J · BLOCKERS
1. `adama.com` bloqueado por WAF → camada de afirmação do fabricante inacessível.
2. Sem credencial Supabase → `SUPABASE_PERSISTENCE = PENDING`.
3. Campo não medido nas 3 maiores regiões de milho (71,6 %) e de oliveira (62,3 %).
4. ~30 % dos boletins da vite do Vêneto são digitalizados sem camada de texto.

`USER_DECISIONS_REQUIRED` = **nenhuma** para continuar; a única que mudaria o escopo é se
o portal deve ser desenhado — e a instrução atual é parar antes dele.

### O ACHADO QUE FECHA A RODADA — a camada de campo não cobre onde a cultura está

O `NEXT_SMALLEST_STEP` anterior era medir o campo nas regiões que **realmente** têm as
culturas. Foi executado, e o resultado é estrutural:

| | região que PUBLICA | fatia da cultura | região que NÃO publica | fatia |
|---|---|---:|---|---:|
| **Oliveira** | Vêneto — 28 boletins em 2026 | **0,5 %** | Puglia | **31,2 %** |
| **Milho** | Friuli-VG — 10 boletins em 2026 | **6,7 %** | Vêneto + Lombardia | **48,2 %** |

**A Puglia diz por quê, no próprio portal:** *"Dal Notiziario Agrometeorologico Regionale
n. 15 del 11/04/2018, la sezione dedicata alla Fitopatologia **non viene più redatta**
poiché le competenze sono in fase di trasferimento all'ARIF"*. Oito anos depois, a
transferência ainda é descrita como em curso. O sinal de mosca-da-azeitona na região que
tem um terço da oliveira italiana passou para **organizações de produtores** — e os
boletins expostos em HTML alcançável estão datados de 2024.

**O Vêneto publica zero boletins de milho** sendo a 1ª região de milho do país: seus dois
boletins de herbáceas de 2026 são trigo (março) e beterraba (junho), enquanto a mesma
região publica 28 de olivo, 25 de frutícola, 21 de hortícola e 16 de vite.

**O Piemonte fica `NOT_OBTAINED`, não "não existe":** a *bacheca dei bollettini* é
renderizada por JavaScript e o HTML obtido não traz PDF nem nome de cultura. Depois do que
aconteceu com o FVG, nenhuma ausência é declarada sem dizer qual rota foi tentada.

> **A consequência para o produto:** um sistema que dependa só de boletim oficial vai
> enxergar muito bem a cultura errada. Todo sinal de campo italiano tem de ser publicado
> junto com **a fatia da cultura que aquele sinal representa** — e é por isso que os dois
> hero cases carregam `SIGNAL_REGION_PCT_NATIONAL` como campo obrigatório.

---

### NEXT_SMALLEST_STEP
**Renderizar a *bacheca dei bollettini* do Piemonte** — é a única das seis regiões-alvo
que ficou `NOT_OBTAINED` por razão técnica, e não por ausência medida. O Piemonte é a 3ª
região de milho (115,7 mil ha, 23,4 %); se publicar boletim de milho, a cobertura do
`IT-HERO-002` salta de 6,7 % para 30,1 % da área nacional. É uma página.

Depois dela, e só depois: Calabria e Sicilia para oliveira (31,1 % somadas), que decidem
se o `IT-DEMO-001` pode virar caso de verdade em outra região.

> Os três `NEXT_SMALLEST_STEP` desta branch foram **executados, não recomendados**. O
> primeiro trocou o caso vencedor de míldio para flavescência; o segundo derrubou um
> *AGIR AGORA* que eu mesmo tinha escrito; o terceiro entregou as datas da obrigação e,
> de quebra, o achado de vencimento. **Nenhuma coleta grande desta branch mudou tanto
> quanto esses três downloads.**
