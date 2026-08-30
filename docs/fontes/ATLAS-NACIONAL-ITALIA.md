# ATLAS NACIONAL DE FONTES — ITÁLIA

`COUNTRY = IT` · **2026-08-30** · 20 fontes sondadas · **16 GREEN · 3 BLOCKED · 1 NOT_REACHED**

> Uma fonte que responde `200` ainda pode estar medindo outra coisa. Este atlas mede
> **três** dimensões por fonte — alcance, frescor e **assunto** — porque a terceira é a
> que separa fonte útil de fonte barulhenta.

Artefato: `data/samples/IT-FONTES/ITALY-SOURCE-PROBE.json`

---

## 1 · O QUE A SONDAGEM MEDIU

| Estado | Significado | n |
|---|---|---:|
| `GREEN` | respondeu e traz termo agronômico | **16** |
| `PARTIAL` | respondeu, sem termo agronômico no que foi lido | 0 |
| `BLOCKED` | bloqueio de origem — **não lida daqui**, não recusada | **3** |
| `NOT_REACHED` | não respondeu neste ambiente | 1 |

E, para cada uma, **o que ela mede**:

| Perfil | Fontes |
|---|---|
| `FIELD_OR_TECHNICAL_SIGNAL` | Vêneto · Lombardia · ERSA FVG · Emilia-Romagna · Agrometeo Puglia · AgroNotizie · CNR-ISPA · Assoproli · Corteva |
| `MARKET_AND_POLICY_SIGNAL` | Terra e Vita · L'Informatore Agrario · CREA (home) · Confagricoltura · Coldiretti · BASF |

> **Terra e Vita responde 200, está fresca (29/08/2026) e traz 30 itens — e fala de preço,
> geopolítica, subsídio e DOP.** É uma boa fonte. Só não é do que se pensava: publicar
> isso como "mídia técnica coberta" seria vender atenção de mercado como estado de lavoura.
> `MEDIA_SIGNAL ≠ FIELD_SIGNAL`.

---

## 2 · O BLOQUEIO É DA CLASSE, NÃO DA ADAMA

| Site | HTTP |
|---|---|
| `adama.com/italia/it` | **403** |
| `syngenta.it` | **403** |
| `cropscience.bayer.it` | **403** |
| `omnitrattore.it` | **403** |
| `agro.basf.it` | 200 |
| `corteva.it` | 200 |

São os sites do setor que recusam IP de datacenter. Isso **reclassifica** a lacuna
comercial: não é "a ADAMA nos bloqueia", é *"a camada de afirmação do fabricante, no
agronegócio, é majoritariamente inacessível de datacenter"* — e vale para Espanha e
França também.

`AgroNotizie` devolveu **403 numa sondagem e 200 noutra, no mesmo dia**: o bloqueio é
intermitente, o que é mais uma razão para `BLOCKED ≠ REJECTED`.

---

## 3 · AS CLASSES, E O QUE CADA UMA ENTREGA

### A · AGRICULTURE / SCALE — **GREEN**
`IT-T1-001` ISTAT (SDMX, CSV, sem chave) · `EU-T1-001` Eurostat.
Nacional **e** regional, validados entre si: milho, trigo duro e trigo mole batem
**exatamente**. Cobre oliveira e videira, que o Eurostat não dá em NUTS 2.
⚠️ ISTAT publica em **NUTS 2006**; Eurostat em **NUTS 2021**. Cruzar pela chave literal
apaga o Nord-Est e o Centro em silêncio.

### B · FIELD / PHYTOSANITARY — **GREEN, mas desalinhado**
5 regiões medidas. **A cobertura não segue a cultura** — ver matriz regional.

### D · REGULATORY — **GREEN, o mais forte do país**
`IT-T4-001` (CSV/JSON/XML abertos) + `IT-T4-001-ETICHETTA` (**163/163 rótulos**).
Entrega `CROP × TARGET × DOSE × INTERVALO × Nº APLICAÇÕES` e grupo HRAC/FRAC/IRAC.
Mais `IT-T3-LOTTA`: decretos de lotta obbligatoria com datas.

### E/F · SCIENCE / RESEARCHERS — **GREEN**
OpenAlex dirigido por `CROP × ISSUE`. ⚠️ estrangula por rajada: consulta lenta é regra,
não defeito.

### G · TECHNICAL NETWORK — **GREEN, parcial**
Serviços regionais + **Consorzio Fitosanitario Provinciale di Piacenza** + **Fondazione
Edmund Mach** + **CREA** (Giornata del Mais 2026, com gravação pública sobre micotoxina).

### I · COOPERATIVAS / ORG. DE PRODUTORES — **PARCIAL**
**Co.Pro.B.** opera um DSS de *Cercospora* **citado pelo boletim oficial do Vêneto** —
cooperativa que **produz** sinal de campo, não só o consome.
**Assoproli Bari** publica boletins de mosca-da-azeitona na Puglia — assumindo o sinal
que a região deixou de publicar em 2018.

### J · CREATORS — **REJECTED nesta configuração**
Gate de amostra: **60 vídeos, 4 canais, 6,7 % de relevância** a `CROP × ISSUE`. São
canais de máquina e de negócio; dois estão parados (2015 e 11/2025). Ver §5.

### K · TECHNICAL MEDIA — **GREEN, com o assunto declarado**
Duas com RSS aberto e perfil de **mercado**; AgroNotizie com perfil técnico e acesso
intermitente.

### L · ADAMA — **BLOCKED**
Regulatório completo; comercial inacessível. Handoff residencial pronto.

### M · COMPETITORS — **PARCIAL**
Syngenta e Bayer publicam conteúdo técnico **exatamente nos dois issues dos casos**
(piralide/diabrotica; *Scaphoideus*). Existência confirmada por índice; páginas 403.

### C · CLIMATE · N · PRICES · O · IP — **NÃO INICIADAS**
Nenhuma decisão do piloto depende delas hoje.

---

## 4 · MATRIZ REGIONAL — a coluna que muda a leitura

Artefato: `data/samples/IT-FONTES/ITALY-REGIONAL-COVERAGE-MATRIX.json`

| Região | % milho | % videira | % oliveira | Campo |
|---|---:|---:|---:|---|
| Veneto | 24,8 | 17,2 | 0,5 | publica semanalmente |
| Lombardia | 23,4 | 3,1 | 0,2 | publica (vite, melo) |
| Piemonte | 23,4 | 6,8 | 0,0 | **`NOT_OBTAINED`** (bacheca em JS) |
| Emilia-Romagna | 10,4 | 5,9 | 0,4 | parcial (Piacenza) |
| Friuli-VG | 6,7 | 4,9 | 0,0 | publica **milho** |
| Puglia | 0,2 | 13,4 | **31,2** | **sem fitopatologia desde 2018** |
| Sicilia | 0,0 | 20,4 | 14,5 | `NOT_MEASURED` |
| Calabria | 0,8 | 0,7 | 16,6 | `NOT_MEASURED` |

**Quanto da cultura o sinal realmente cobre:**

| Cultura | sinal cobre | do medido | existe e não lido | regiões com sinal |
|---|---:|---:|---:|---|
| Videira | **31,1 %** | 44,5 % | — | Vêneto · Lombardia · E-R · FVG |
| Milho | **17,1 %** | 40,7 % | **24,8 %** | Emilia-Romagna · FVG |
| Oliveira | **0,5 %** | 32,3 % | — | apenas Vêneto |
| **Trigo duro** | **0,0 %** | 37,4 % | — | **nenhuma** |

> **Correção — o Vêneto TEM boletim de milho, por outra rota.** O serviço fitossanitário
> publica 2 boletins de herbáceas em 2026 (trigo e beterraba) e nenhum de milho. Mas a
> **AVISP / Veneto Agricoltura** publica o *Bollettino Colture Erbacee*, numerado e
> semanal, com edições dedicadas à **piralide do mais** (n.42 de 15/07/2022, n.40 de
> 19/07/2024, n.4 de 20/01/2025) e página de tópico atualizada em **20/05/2026**. O site é
> um SPA Angular sem render no servidor e o host de arquivo devolve 503: a **existência**
> está provada pelo índice, o **conteúdo** não foi lido. Fica `NOT_OBTAINED`, fora da
> cobertura **e** fora da ausência.

> **Segunda correção — o conteúdo é legível por ID, e mesmo assim o Vêneto não sobe.**
> O endpoint `myportal/AVPISP/api/content/download?id=<id>` devolve o PDF real, e **duas
> edições foram lidas**: *n. 53 — Micotossine nel mais* (risco sazonal pelo DSS **Mais.net**
> da Horta sobre as estações das aziende da Veneto Agricoltura; **aflatossina ALTA** em
> todas, fumonisina de média-alta a alta; verificação de infecção das sedas com o **CREA-CI**)
> e *n. 18/2025 — Nottue* (primeira captura de *Agrotis ipsilon* em Cartura, PD, em
> 03/03/2025; graus-dia `(Tmax−Tmin)/2 − 10,4 °C`). Isso prova que a série existe, é
> numerada e trata de milho com estação nomeada e limiar.
>
> **Não prova quantas edições de 2026 existem.** O `<id>` só aparece em resultado de busca
> pública; não há endpoint de listagem alcançável, e a tentativa de encontrá-lo foi
> encerrada em vez de contornada. Sem índice não há denominador, e sem denominador não há
> cobertura: o Vêneto continua fora dos dois lados. **`EDIÇÃO LIDA ≠ SÉRIE MEDIDA`** —
> é a forma local de `COBERTURA ALTA ≠ COBERTURA CORRETA`, e o teste
> `test_edicao_lida_nao_promove_a_regiao_a_coberta` impede a promoção silenciosa.
>
> **Os dois PDFs não foram preservados** em `data/raw` antes de a rota deixar de estar
> disponível neste ambiente: `RAW_EVIDENCE_STATE = NOT_PRESERVED`. O resumo acima é
> **testemunho de leitura, não evidência re-verificável**, e por isso não sustenta métrica
> nenhuma. Re-obter e gravar está no handoff de navegador local.

> **O trigo duro é a primeira cultura da Itália — 1.177,4 mil ha — e não tem nenhum
> sinal de campo nas regiões medidas.** É a maior lacuna do país, e ela não aparece em
> nenhum caso porque nenhum caso foi construído sobre ela.

### ⚠ Correção de método — a tabela acima mede o painel, não o país

A coluna *"sinal cobre"* estava certa em aritmética e **errada em sentido**, e o trigo duro
é o caso extremo. Das cinco regiões que entraram como **medidas** para trigo duro,
**76,8 % da área é uma região só — a Puglia** —, justamente aquela cujo notiziario
**deixou de redigir a seção de fitopatologia em 11/04/2018**, por transferência de
competência à ARIF. Não é silêncio agronômico: é um ato administrativo de oito anos atrás.
E o **Friuli-Venezia Giulia entrou no painel com 0,0 mil ha de trigo duro** — uma região que
não planta a cultura aparece como se tivesse sido interrogada e tivesse respondido "não".

**A Sicília — 277,5 mil ha, 23,6 %, a segunda maior região de trigo duro do país — nunca foi
perguntada.** Nem a Basilicata (9,8 %), nem as Marche (6,2 %). Ao todo, **57,9 % do trigo
duro italiano nunca entrou em nenhuma sonda.**

| Cultura | medido | dependência de 1 região | veredito | o que fecha a lacuna |
|---|---:|---:|---|---|
| Oliveira | 32,4 % | **96,5 %** (Puglia) | `UNMEASURED_NOT_ZERO` | `PANEL_EXPANSION` — Calábria 16,6 %, Sicília 14,5 % nunca perguntadas |
| Trigo duro | 37,4 % | **76,8 %** (Puglia) | `UNMEASURED_NOT_ZERO` | `PANEL_EXPANSION` — Sicília 23,6 %, Basilicata 9,8 % |
| Milho | 40,6 % | 57,6 % (Lombardia) | `PARTIALLY_MEASURED` | `ROUTE_ENGINEERING` — 48,2 % foi perguntado e a rota não respondeu |
| Videira | 44,4 % | 38,6 % (Vêneto) | `PARTIALLY_MEASURED` | `PANEL_EXPANSION` — Sicília 20,4 %, Toscana 9,3 % |

**A lei que entra:** `PAINEL MEDIDO ≠ PAÍS MEDIDO`, com o corolário
`NOT_ASKED ≠ NOT_FOUND ≠ DOES NOT EXIST` — **três** estados, não um. Publicar "0,0 % de
cobertura" para uma cultura que só foi perguntada a uma região colapsa os três.
Quando a dependência de uma região passa de 60 %, o veredito vira `UNMEASURED_NOT_ZERO`
por mais que o painel pareça grande: **uma amostra de tamanho um não é cobertura nacional.**

**O que a coluna `o que fecha a lacuna` compra.** Ela separa dois orçamentos que estavam
sendo tratados como um. O milho **não** precisa de região nova — as regiões certas já foram
interrogadas e o que falha é a rota (JavaScript no Piemonte, índice ausente na AVISP do
Vêneto): é engenharia de coleta. O trigo duro e a oliveira **não** se resolvem com nenhuma
engenharia, porque as regiões grandes nunca foram perguntadas. Sem essa separação, o esforço
vai para a cultura errada.

**O que isto não diz.** Não diz que exista boletim de trigo duro na Sicília — **não perguntei**.
A inversão olivícola continua de pé como comparação entre **duas regiões medidas** (o Vêneto
publica 28 boletins de olivo com 0,5 % da área; a Puglia, com 31,2 %, não publica): essa
afirmação sobrevive. O que **não** sobrevive é ler "0,5 %" como a cobertura olivícola **do
país**, quando 63,9 % da oliveira italiana nunca foi interrogada.

Medido em `data/samples/IT-FONTES/ITALY-PANEL-BIAS.json` · `scripts/italia_vies_de_painel.py`

---

## 5 · A ROTA DE CREATORS QUE FALHOU, E A QUE FUNCIONOU

**Falhou:** "principais canais de agricultura italiana" → 4 canais, 60 vídeos,
**6,7 %** de relevância. Edagricole e Agri Italia testam **tratores**; Agri Italia está
parado desde **2015**.

**Funcionou:** `CROP × REGION × TOPIC → conteúdo → pessoa`. Duas buscas devolveram o
Consorzio de Piacenza, a FMach, a Giornata del Mais do CREA e conteúdo técnico de dois
concorrentes — **todos ligados aos issues dos casos**.

O **RSS público do YouTube responde sem chave de API** (15 itens por canal, com data e
ID). O gargalo é **discovery**, nunca a coleta.

---

## 6 · PLACAR

| | |
|---|---|
| Fontes sondadas | **20** |
| GREEN | **16** · BLOCKED **3** · NOT_REACHED 1 |
| Regiões na matriz | **8** de 20 |
| Fontes de campo | 5 regiões + 2 org. de produtores |
| Fontes de ciência | OpenAlex + CREA + CNR + FMach |
| Rotas estruturadas | ISTAT SDMX · Eurostat · Ministero CSV/JSON/XML · 2 RSS · YouTube RSS |
| Custo | **US$ 0,00** |
