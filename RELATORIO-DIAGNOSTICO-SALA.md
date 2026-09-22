# RELATÓRIO — DIAGNÓSTICO DA SALA · PORQUE 71 DE 76 NÃO ENTRARAM

Lane `diagnostico-sala-v1`, base `origin/lote-76-v1` @ `db146ddb`.
Corrida analisada: `XX-T10-2026-09-22-193411-0a8a01dbc999da85` (derived 833–908).

```
MISSAO            = SO LEITURA E ANALISE
ADMISSION_CHANGED = NO      DB_WRITES = 0      NETWORK_REQUESTS = 0
ACTUAL_LLM_MODEL  = claude-opus-5-5
```

---

## 0 — OS FACTOS DE PARTIDA, REMEDIDOS

Fontes de verdade usadas, só leitura:

* banco `sala_italia` @ `127.0.0.1:54330` — só `SELECT` (junção
  `derived_artifact × raw_asset` onde `run_id` contém `0a8a01dbc999da85`);
* `data/samples/LIVRO-DE-DECISOES.json` — os vereditos **escritos**;
* os 76 textos derivados, em `lote-76-v1/NAO_SEI/derivados/TEXT_EXTRACTION/`,
  **sha256 conferido contra o banco: 76/76 batem**;
* `admissao._do_universo()` chamada em memória — **nunca** `adm.escrever()`.

| medida | briefing | medido |
|---|---|---|
| itens da corrida | 76 | **76** |
| SIM / NAO / NAO_SEI / ERRO | 5 / 47 / 24 / 0 | **5 / 47 / 24 / 0** |
| NAO_SEI de 1 sinal | 8 | **8** |
| NAO_SEI «outro motivo» | 16 | **16** |
| a minha releitura T10 = veredito escrito | — | **76/76 idênticos** |
| leitura T7 correcta (56 itens T7) | 0 / 36 / 20 | **0 SIM / 36 NAO_SEI / 20 NAO** |

Todos os factos de partida confirmam-se. Scripts de leitura:
`scripts/diagnostico_sala/ler_os_76.py` e `onde_casou.py`.

---

## 1 — PARETO_POR_FONTE

| SOURCE_ID | o que é | n | SIM | NAO | NAO_SEI | leitura correcta (universo da fonte) |
|---|---|---|---|---|---|---|
| IT-T7-017 | Cantine Riunite & CIV — notícias do grupo vinícola | 30 | 0 | 21 | 9 | 0 / 20 NAO / 10 NAO_SEI |
| IT-T7-033 | Consorzio Vino Chianti Classico — notícias | 15 | 0 | 15 | 0 | 0 / 0 / 15 NAO_SEI |
| IT-T7-042 | Consorzio Tutela Aceto Balsamico di Modena — notícias | 10 | 0 | 9 | 1 | 0 / 0 / 10 NAO_SEI |
| IT-T10-022 | Zootecnica International — revista avícola, **em inglês** | 10 | 0 | 0 | 10 | igual |
| IT-T10-018 | myfruit.it — notícias de hortofruticultura | 9 | **5** | 0 | 4 | igual |
| IT-T10-021 | Plantgest (imagelinenetwork) — eventos | 1 | 0 | 1 | 0 | igual |
| IT-T7-021 | Consorzio Est Ticino Villoresi — notícias | 1 | 0 | 1 | 0 | 0 / 0 / 1 NAO_SEI |
| **total** | | **76** | **5** | **47** | **24** | 5 / 21 / 50 |

**Quem produz os 47 NAO: três fontes fazem 45 de 47.**
IT-T7-017 = 21 · IT-T7-033 = 15 · IT-T7-042 = 9 · IT-T10-021 = 1 · IT-T7-021 = 1.
Não é espalhado: são as três fontes de «notícias de marca» do vinho e do
vinagre. **Nenhum dos 47 vem de fonte T10 bem apontada** a não ser o único
item da IT-T10-021.

---

## 2 — OS 47 NAO: CAPA OU MATÉRIA?

Classificado pelo **texto derivado**, não pelo endereço. Cada texto é
«moldura do site (menu, busca, rodapé) + corpo». Em todos os 47 há um corpo
com título próprio, data própria e parágrafos de notícia. O mais curto
(derived 902, «Imparare a riconoscere l'autentico Aceto Balsamico…», 22/09/2026)
tem 606 caracteres de corpo e é uma notícia inteira.

```
CAPA_OU_LISTAGEM_ENTRE_OS_NAO = 0/47
MATERIA_INDIVIDUAL = 47/47   (nenhuma do universo pedido pela fonte)
```

Do que falam os 47 (lido item a item):

| assunto | n | exemplos |
|---|---|---|
| feira / degustação / evento promocional | 15 | 862, 864, 878, 879, 884–887, 890, 891, 897, 898, 903, 906, 907 |
| patrocínio (música, desporto, praia) | 8 | 854, 859, 865, 868, 871–873, 876 |
| prémio / pontuação de vinho | 8 | 855, 861, 866, 888, 889, 893, 894, 905 |
| produto, receita, marca, lançamento | 6 | 860, 875, 880, 899, 902, 904 |
| institucional (ESG, festa interna, visita à fábrica, obituário, e-learning, emenda de lei sobre denominação) | 6 | 856, 858, 877, 892, 895, 908 |
| mercado (crise do vinho, excedentes, procura de uva) | 1 | 900 |
| campanha agrícola (produção e qualidade do azeite DOP 2025) | 1 | 896 |
| técnico-agronómico (congresso de nocicultura, SOI) | 1 | 842 |
| aviso local (derrame no canal, navegação retomada) | 1 | 883 |
| **total** | **47** | |

⚠️ **A prova do NAO é quase sempre palavra de moldura ou palavra de todos os dias.**
O NAO desta régua exige «prova positiva de outro universo». Medido:

* 28 dos 47 NAO têm como prova `consorzio` ou `cooperativa` — que é **o nome de
  quem publica** («Consorzio Vino Chianti Classico», «realtà cooperativa»);
* 13 dos 47 NAO assentam em **uma só** palavra de outro universo — enquanto o
  SIM exige duas;
* as palavras que decidiram: `evento` (menu «Eventi» e texto corrente),
  `prodotto`, `ricerca` (caixa «Ricerca per:» do site, e «ricerca della
  qualità»), `tesi` (dentro de «sin**tesi**» e no apelido «Valentino **Tesi**»),
  `etichetta`.

O NAO está **certo no resultado** (nenhum destes 47 é matéria para a Sala), e
**fraco na prova**. É exactamente o defeito que a régua já descreve para
`fitosanitario`: «o nome de quem publica não é o assunto do que se publica».

---

## 3 — OS 16 «OUTRO MOTIVO DA MESMA REGRA»

O motivo é **o mesmo nos 16**, palavra por palavra (livro de decisões, campo
`motivo`):

> «nao encontrei nada de «T10» — nem de nenhum outro universo. Isso NAO prova
> que o item nao pertence: prova que o vocabulario nao lhe chegou.»

| derived | fonte | título | o que é |
|---|---|---|---|
| 843 | IT-T10-022 | EuroTier 2026: poultry, biosecurity and AI | feira; cita «market instability, rising costs» |
| 844 | IT-T10-022 | Newcastle disease confirmed on two Hungarian broiler farms | sanidade animal |
| 845 | IT-T10-022 | Indonesia eyes China and the Middle East for poultry exports | **mercado** (export ×11, market ×7) |
| 846 | IT-T10-022 | FEFAC and Sindirações sign feed industry MoU | acordo sectorial / regulação |
| 847 | IT-T10-022 | Bob Buresh receives 2026 PSA Poultry Industry Award | prémio pessoal |
| 848 | IT-T10-022 | Poultry revitalisation in Ghana | programa público; importações e produção |
| 849 | IT-T10-022 | EU advances new environmental rules for large poultry farms | regulação ambiental |
| 850 | IT-T10-022 | EU poultry output rises as broiler prices decline | **mercado** (price ×14, import ×14, export ×11) |
| 851 | IT-T10-022 | Indonesia asks feed mills to delay price increases | **mercado** (price ×13, import ×16) |
| 852 | IT-T10-022 | Remembering Dr James "Jim" McKay | obituário |
| 853 | IT-T7-017 | Lambrusco Vigna del Cristo … Tre Bicchieri 2025 | prémio de vinho |
| 857 | IT-T7-017 | Riunite & CIV con la Federazione Italiana Cuochi a HOST | feira |
| 863 | IT-T7-017 | Cantine Maschio a Sanremo con Vanity Fair | evento |
| 867 | IT-T7-017 | Un giorno insieme, come una famiglia | evento interno |
| 870 | IT-T7-017 | Riunite al Raduno degli Alpini | patrocínio |
| 881 | IT-T7-017 | Riunite al Tour Music Fest | patrocínio |

**A causa dos 10 da IT-T10-022 é a língua.** A régua T10 tem palavras
italianas e portuguesas e **nenhuma inglesa** (`price`, `export`, `market`
não existem na lista). Três deles (845, 850, 851) são matéria de mercado
clara; a régua não os consegue ler.

---

## 4 — OS 8 DE UM SINAL: ACIDENTE OU TEMA?

| derived | fonte | palavra | onde casou | veredito da leitura |
|---|---|---|---|---|
| 833 | IT-T10-018 | prezzi | **nuvem de etiquetas do menu** («prezzi / 464») | acidente de moldura |
| 837 | IT-T10-018 | prezzi | idem | acidente de moldura |
| 838 | IT-T10-018 | prezzi | idem | acidente de moldura |
| 840 | IT-T10-018 | prezzi | idem | acidente de moldura |
| 869 | IT-T7-017 | prezzo | «rapporto qualità-**prezzo**» (guia de vinhos) | expressão feita, não mercado |
| 874 | IT-T7-017 | prezzo | «qualità e **prezzo**» | expressão feita, não mercado |
| 882 | IT-T7-017 | prezzo | «**prezzo** medio di riparto pari a 47,20 euro al quintale» (balanço da cooperativa, facturação 266 M€) | **tema real** |
| 901 | IT-T7-042 | prezzi | «l'aumento dei **prezzi** legato ai dazi» (inquérito Nomisma, consumidores dos EUA) | **tema real** |

```
ACIDENTE = 6/8      TEMA_REAL = 2/8
```

A régua tratou os 8 correctamente: nenhum subiu a SIM com uma palavra só.
Os dois de tema real são matéria de **mercado** publicada por fontes
catalogadas como **T7** — ver secção 5.

---

## 5 — O ERRO T7/T10 MUDA ALGUMA FONTE DE LADO?

| SOURCE_ID | escrito (pergunta T10) | correcto (pergunta T7) | muda? |
|---|---|---|---|
| IT-T7-017 | 0 / 21 NAO / 9 NAO_SEI | 0 / 20 NAO / 10 NAO_SEI | 3 NAO→NAO_SEI, 2 NAO_SEI→NAO |
| IT-T7-033 | 0 / 15 NAO / 0 | 0 / 0 / 15 NAO_SEI | 15 NAO→NAO_SEI |
| IT-T7-042 | 0 / 9 NAO / 1 NAO_SEI | 0 / 0 / 10 NAO_SEI | 9 NAO→NAO_SEI |
| IT-T7-021 | 0 / 1 NAO / 0 | 0 / 0 / 1 NAO_SEI | 1 NAO→NAO_SEI |
| as três T10 | — | igual | não |

```
FONTES_QUE_PASSAM_A_TER_SIM = 0/7
```

**Nenhuma fonte muda de lado para SIM.** E o NAO_SEI que aparece com a
pergunta certa é, em 28 de 28 casos novos, provocado por `consorzio` ou
`cooperativa` — outra vez o nome de quem publica, agora do lado T7. Ou seja:
a pergunta certa não acha matéria técnica; acha o nome do publicador.

---

## 6 — PARETO_POR_CLASSE (os 71 que não entraram)

Definições usadas:
**FONTE** — a fonte escolhida não publica, nesta rota, matéria do seu universo ·
**ROTA** — a fonte tem a matéria mas a coleta apanhou a página errada ·
**REGUA** — a matéria é do universo e a régua não a leu ·
**TEMA** — fonte certa, rota certa, o dia não trouxe o assunto ·
**UNKNOWN** — não se decide sem ir à fonte (proibido nesta missão).

| classe | n | itens |
|---|---|---|
| **FONTE** | **55** | IT-T7-017 (30) · IT-T7-033 (15) · IT-T7-042 (10) |
| **TEMA** | **9** | myfruit 833, 837, 838, 840 · Zootecnica 844, 847, 849, 852 · Villoresi 883 |
| **REGUA** | **3** | Zootecnica 845, 850, 851 (mercado em inglês) |
| **ROTA** | **0** | (ver ressalva) |
| **UNKNOWN** | **4** | Zootecnica 843, 846, 848 (mercado lateral, em inglês) · Plantgest 842 |
| **total** | **71** | |

Porque cada classe:

* **FONTE 55.** As três secções de notícias são comunicação de marca:
  prémios, patrocínios, feiras, receitas. O próprio menu capturado no texto
  derivado mostra o que o site oferece — Riunite: «Il gruppo · I nostri brand ·
  News e eventi · Progetti»; Chianti: «Vino · Territorio · Marchio · Consorzio ·
  Shop»; Balsamico: «Storia · Consorzio · In cucina · Ricette». Nenhuma destas
  fontes é «rede técnica» (agrónomos, assistência técnica, extensão) — que é o
  que T7 pergunta. Dentro das 55 há **3 matérias de mercado reais** (882
  balanço com preço pago à uva, 900 excedentes de vinho, 901 preços e tarifas
  nos EUA) e **1 relatório de campanha** (896, azeite DOP 2025). O que estas
  fontes têm de útil é mercado ou campanha — nunca rede técnica.
* ⚠️ **Ressalva ROTA, declarada.** Os menus do Chianti («Vendemmia»,
  «Tracciabilità», «Tutela») e do Balsamico («Vigilanza e Tutela»,
  «Monitoraggio», «Dati economici») mostram secções que **podem** ter matéria
  mais útil do que as notícias. Sem rede não o provo. Se tiverem, parte das 25
  (IT-T7-033 + IT-T7-042) passa de FONTE a ROTA. O número firme é **ROTA = 0,
  ROTA possível ≤ 25**.
* **TEMA 9.** Fonte com matéria do universo noutros dias (myfruit deu os 5
  SIM desta mesma corrida; Zootecnica publica mercado — 845/850/851), mas o
  artigo do dia era rótulos compostáveis, campanha escolar, protocolo de
  legalidade, doença, prémio, regras ambientais, obituário, derrame no canal.
* **REGUA 3.** Mercado inequívoco, em inglês, e a lista T10 não tem inglês.
* **UNKNOWN 4.** 843/846/848 tocam mercado de passagem (custos, comércio de
  rações, importações do Gana) — é decisão de gabarito humano, não minha.
  842 é um congresso técnico de nocicultura numa fonte catalogada T10: ou a
  fonte está mal catalogada (FONTE) ou a rota foi à secção de eventos (ROTA);
  um item só, e não se decide sem ir lá.

Os 5 que entraram (834, 835, 836, 839, 841, todos myfruit) foram lidos:
preços do tomate, uva de mesa, bananas na GDO, aberturas de mercado — **SIM
correcto nos 5**.

---

## 7 — RECOMENDAÇÕES (nenhuma aplicada)

### Para o Source Curator

1. **RECOMENDACAO** — rever a catalogação T7 de IT-T7-017, IT-T7-033 e
   IT-T7-042. Em 55 de 55 itens colhidos não há matéria de rede técnica; há
   comunicação de marca. Opções: retirar da colheita, ou recatalogar como T9
   (marketing/concorrência) ou T10 (das 55, as únicas úteis são 3 de mercado e 1 de campanha).
2. **RECOMENDACAO** — rever IT-T10-021 (Plantgest): o item colhido é técnico,
   não de mercado.
3. **RECOMENDACAO** — IT-T10-022 e IT-T10-018 ficam: a fonte está certa, o
   que falha é o dia (TEMA) ou a língua (REGUA).

### Para as rotas

4. **RECOMENDACAO** — antes de mexer no catálogo, uma visita **com rede e
   autorização** às secções «Vendemmia»/«Tutela» (Chianti) e «Monitoraggio»/
   «Dati economici» (Balsamico) decide se as 25 são FONTE ou ROTA.
5. **RECOMENDACAO** — o derivador de HTML leva o menu e a nuvem de etiquetas
   para dentro do texto. Separar moldura de corpo na derivação eliminaria 6
   dos 8 «um sinal» e a maior parte das provas de NAO. É mudança de
   transformação, não de régua — e tem de ser medida contra o gabarito antes.

### Para a régua (Admission)

6. **RECOMENDACAO** — a lista T10 não tem inglês. Juntar formas inglesas
   (`prices`, `exports`, `imports`, `commodity` já existe) faria 845, 850 e
   851 serem lidos. **Medir contra o gabarito antes**, como a própria régua
   exige — `market` e `trade` são candidatas a palavra de menu.
7. **RECOMENDACAO** — `consorzio` e `cooperativa` na lista T7 são o nome de
   quem publica em 28 de 28 NAO_SEI novos (e em 30 dos 36 NAO_SEI T7). Mesma lei que tirou `fitosanitario`
   de T3. Avaliar se devem sair.
8. **RECOMENDACAO** — o NAO «com prova de outro universo» aceita **uma**
   palavra, enquanto o SIM exige **duas**. Em 13 de 47 NAO a prova é uma
   palavra só (`evento`, `prodotto`, `ricerca`). Avaliar exigir o mesmo
   `SINAIS_MINIMOS` para a prova de exclusão. Efeito esperado: NAO→NAO_SEI,
   **zero** SIM a mais — não é afrouxar a porta.
9. **RECOMENDACAO** — pagar a dívida T7/T10 declarada no RELATORIO-LOTE-76
   só depois da 7 e da 8: com a régua de hoje, a pergunta certa produz 36
   NAO_SEI dos quais 30 nascem do nome do publicador.

---

## ENTREGA

```
PARETO_POR_FONTE   = IT-T7-017 30 (0 SIM) · IT-T7-033 15 (0) · IT-T7-042 10 (0)
                     · IT-T10-022 10 (0) · IT-T10-018 9 (5) · IT-T10-021 1 (0)
                     · IT-T7-021 1 (0)
NAO_POR_FONTE      = 45/47 em três fontes (T7-017 21 · T7-033 15 · T7-042 9)
PARETO_POR_CLASSE  = FONTE 55 · TEMA 9 · REGUA 3 · ROTA 0 · UNKNOWN 4   (= 71)
                     ROTA possivel <= 25 (secções não visitadas, sem rede)
CAPA_OU_LISTAGEM_ENTRE_OS_NAO = 0/47
OS_16_MOTIVO       = 16/16 «nada de T10 nem de nenhum outro universo»;
                     10/16 são inglês (IT-T10-022)
OS_8_UM_SINAL      = 6 acidente (4 menu, 2 «qualità-prezzo») · 2 tema real
T7_T10_MUDA_FONTE  = 0/7 fontes ganham SIM; 28 itens NAO→NAO_SEI, 2 NAO_SEI→NAO
SIM_CONFERIDOS     = 5/5 correctos pela leitura do texto
ADMISSION_CHANGED  = NO
SYSTEM_MAP_CHECK   = FAIL herdado — só P9 por provas/recollection_red_team_estrito.mjs
                     (o mesmo do RELATORIO-LOTE-76; não é desta missão).
                     As peças desta missão (C-DIAGNOSTICO-SALA) passam. CADEIA=OK 20/20.
DB_WRITES          = 0     (só SELECT)
NETWORK_REQUESTS   = 0
```

`FINAL_HEAD` / `REMOTE_HEAD`: no fim da entrega da sessão (o commit não pode
conter o próprio hash).

---

## EM PALAVRAS SIMPLES

Pense na Sala como um cesto onde só entram notícias úteis para a ADAMA.
Chegaram 76 notícias; entraram 5; ficaram 71 de fora. Fui ver porquê, só a
ler, sem mexer em nada.

**55 das 71 vieram de três "lojas" erradas.** Duas associações de vinho e uma
de vinagre balsâmico. As notícias delas falam de prémios, festas, maratonas e
receitas de cocktail. É como ir à padaria procurar remédio: a padaria não está
avariada, só não vende isso.

**Nenhuma das 47 recusadas era uma "página de capa"** (menu, contactos,
índice). Eram 47 notícias inteiras de verdade — só que sobre outra coisa.

**3 foram recusadas por a porta não saber inglês.** Uma revista de frangos
escreve em inglês sobre preços e exportações, e a lista de palavras da porta
só tem italiano e português. Essas 3 eram boas e ficaram de fora.

**9 são azar do dia:** a loja certa, mas naquele dia a notícia era de outro
assunto.

**4 não sei decidir** sem ir ao site, e ir ao site estava proibido nesta
missão.

Duas coisas que a porta faz mal, mesmo quando acerta: ela às vezes decide
pelo **menu do site** (a palavra "prezzi" estava na lista de etiquetas, não
na notícia), e pelo **nome de quem escreveu** ("Consorzio" aparece em toda
notícia do Consorzio). É como julgar uma carta pelo envelope.

Não mudei nada: nem a porta, nem o banco, nem fui à internet. Deixei 9
recomendações, cada uma com o dono dela, para alguém decidir.
