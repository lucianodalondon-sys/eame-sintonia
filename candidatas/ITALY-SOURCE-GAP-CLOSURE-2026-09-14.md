# FECHAR OS GAPS REAIS — ITÁLIA

**Data:** 2026-09-14 · **Branch:** `claude/italy-agricultural-sources-discovery-dfba81`
· **Entrega:** [`ITALY-SOURCE-GAP-CLOSURE-2026-09-14.xlsx`](ITALY-SOURCE-GAP-CLOSURE-2026-09-14.xlsx)
(13 folhas)

> **A pergunta:** quais fontes reais precisamos adicionar para que as
> ferramentas de Intelligence tenham matéria-prima suficiente, comprovada e
> recorrente?

---

## O TRABALHO PARALELO QUE EU NÃO SABIA QUE EXISTIA

O §2 mandava carregar dois ficheiros. Eles **não estavam nesta branch** — mas
estavam no histórico, noutra:

```
origin/claude/italy-source-qualification-v1 · commit d9535783
«fontes(IT): qualificacao, reconciliacao de endereco e priorizacao das 381»
```

É uma missão inteira, **paralela à minha** (`d9535783` não contém `08e590a7`).
Qualificou as **381 do acervo base** — não as minhas 217 — com sete dimensões:
`PASS 265 · REVIEW 88 · REJECT 25`, `P1 161`. E fez **125 correções de endereço
canónico**.

Três coisas dela mudaram esta missão:

| o que ela mediu | o que mudou aqui |
|---|---|
| **a ASSAM Marche redireciona para a AMAP Marche** | **um dono meu estava errado.** Eu escrevi «ASSAM» numa das 37 |
| o helper de TLS tinha a porta do proxy fixa em código; falhava em silêncio e **a falha parecia «fonte morta»** — cinco fontes oficiais só foram recuperadas depois do conserto | escrevi a sonda desta missão com a regra: **falha de ligação nunca escreve «fonte morta»** |
| o ataque 18 dela apanhou a ARPA Sardegna a servir **página de erro do IIS já promovida a P1** | a minha sonda ganhou detetor de erro-dentro-do-200 |

---

## A · G · ONDE ESTAMOS

```
A  BRANCH        claude/italy-agricultural-sources-discovery-dfba81
B  INITIAL_HEAD  581b5059
C  FINAL_HEAD    (o commit desta missão)
D  LOCAL_HEAD    = REMOTE_HEAD
E  REMOTE_HEAD   581b5059 -> empurrado no início desta missão
F  WORKTREE      limpo no início
G  PUSH_STATE    ⚠️ O 581b5059 NÃO ESTAVA NO REMOTO. O remoto estava em
                 191dbda4. Empurrei antes de tocar em nada, como o §1 manda —
                 não se continua sobre trabalho não preservado.
```

---

## H · L · AS 37 ROTAS, ABERTAS DE VERDADE

A entrega anterior declarava, ela mesma: *«nenhuma das 37 rotas foi aberta por
sonda»*. Agora foram, todas.

```
H  PREVIOUS_37                 37
I  VALIDATED_STRONG             9
J  VALIDATED_USEFUL             6   ·  VALIDATED_BUT_SECONDARY  15
K  REJEITADAS                   5   (1 BROKEN · 1 WRONG_SOURCE · 3 BLOCKED)
L  UNKNOWN                      2
   redirecionaram               8 de 37
   donos corrigidos             2
```

### A sonda foi provada antes de julgar

Sem isto, «não achei problema» pode significar «o detetor está cego»:

| controle | rota | esperado | deu |
|---|---|---|---|
| positivo | `fitosanitari.salute.gov.it` | tem de abrir | abriu |
| positivo | `regione.veneto.it/.../bollettini-viticoli` | tem de abrir | abriu |
| negativo | domínio inventado | BROKEN | BROKEN |
| negativo | `coeweb.istat.it` (sede encerrada) | não pode passar | BROKEN |

### Oito estados, não dois

`BROKEN` pede fonte nova. `BLOCKED` pede outra rota. `UNKNOWN` pede outra
tentativa. Colapsar em «viva/morta» perde as três ações.

## AS QUATRO VEZES QUE A MINHA PRÓPRIA SONDA ERROU

Apanhadas por olhar o resultado em vez de o publicar:

**1 · `getaddrinfo failed` tratado como fonte morta.** A sonda falhou em
`www.arpa.piemonte.it` — em Python **e** em curl. Ia escrever BROKEN. O
resolvedor público devolve **três endereços** (alias de
`vip-lb-1-portali.nivolapiemonte.it`). O domínio está vivo; **o DNS desta
máquina é que não o alcança.**

Três fontes vivas salvas de serem apagadas do acervo:

```
www.alsia.it                      -> 78.40.170.40
difesafitosanitaria.ersa.fvg.it   -> 135.181.210.8
www.arpa.piemonte.it              -> 84.240.178.144 (+2)
```

E uma delas é **a que fecha a Basilicata**. A pergunta certa nunca é
«falhou?» — é **«falhou de que lado?»**

**2 · Filtro de assunto só em italiano.** A EU Pesticides Database saiu
`WRONG_SOURCE` por publicar em inglês. É a repetição exata do erro da missão 1,
que recusou o Versuchszentrum Laimburg (alemão) e o *Italian Journal of
Agrometeorology* (inglês). Detetor monolíngue não é conservador — é cego de um
olho. Corrigido com inglês, alemão e francês.

**3 · Aplicação de JavaScript confundida com página morta.** Texto curto tem
duas causas opostas: página morta tem pouco texto **e** pouco byte; app de JS
tem pouco texto e **muito** byte — e está viva. `sian.it` (5.950 bytes, 4
caracteres) e `venetoagricoltura.org` (6.250 bytes, 8 caracteres) são apps.

**4 · Página de redirecionamento chamada de quebrada.** O `irriframe.it`
devolve *«Stai per essere reindirizzato ad altra pagina»*. Placa de «siga em
frente» não é porta fechada.

## O ERRO MEU MAIS CARO, E ELE ESTAVA PUBLICADO

Na missão anterior escrevi que a produção e a área do ISTAT vinham do dataflow
**`DCSP_COLTIVAZIONI`**. Abri o serviço:

```
GET /SDMXWS/rest/dataflow/IT1/DCSP_COLTIVAZIONI
HTTP 404 — "Could not find requested structures"
```

**O identificador não existe.** Quem tentasse coletar pelo meu ID receberia
404 e nada mais. Procurei nos **4.907 dataflows** publicados e achei os
verdadeiros:

| dataflow | o que é |
|---|---|
| `101_1015_DF_DCSP_COLTIVAZIONI_1` | superfícies e produção, dados no conjunto |
| `101_1015_DF_DCSP_COLTIVAZIONI_2` | o mesmo, **por província** |
| `101_1015_DF_DCSP_COLTIVAZIONI_10` | **intenções de semeadura** — sinal de futuro |
| `101_12_DF_DCSP_PREZZIAGR_10` | índice de preços na produção, mensal, base 2020 |

E depois puxei **dado**, não página:

```
13.522.174 bytes de CSV
DATAFLOW, FREQ, REF_AREA, DATA_TYPE, TYPE_OF_CROP, DESTINATION_WINEGRAPES,
TIME_PERIOD, OBS_VALUE, OBS_STATUS, ..., UNIT_MEAS, UNIT_MULT
```

`REF_AREA` + `TYPE_OF_CROP` + `TIME_PERIOD` + `OBS_VALUE` + `UNIT_MEAS` é
exatamente a matéria-prima do gap crítico de produção/área/rendimento. **Não é
página que fala de dado — é o dado.**

---

## M · R · OS 15 CRÍTICOS, CLASSIFICADOS POR TIPO

O §16 exige o tipo **antes** de procurar mais fonte, e a razão é prática:
procurar fonte pública para um dado que a lei proíbe publicar é procurar para
sempre.

```
M  CRITICAL_GAPS_BEFORE                 15
N  CRITICAL_GAPS_AFTER (pedem fonte)     2
O  SOURCE_GAP                           10   (9 fechados ou fechados-na-origem)
P  ACCESS_GAP                            0   dentro dos 15 · 3 fora deles
Q  DATA_MODEL_GAP                        4   não fecham com fonte nenhuma
R  COLLECTION_CAPABILITY_GAP             1
```

| gap | tipo | estado depois |
|---|---|---|
| WINDOWS · fase fenológica (`CROP_STAGE 0/29`) | SOURCE_GAP | **FECHADO** — 8 fontes abertas |
| MARKET · produção/área/rendimento | SOURCE_GAP | **FECHADO COM DADO NA MÃO** |
| PORTFOLIO · alteração de autorização | SOURCE_GAP | **FECHADO** |
| FUTURE · primeira deteção | SOURCE_GAP | **FECHADO** |
| VOICES · papel de quem fala | SOURCE_GAP | **FECHADO** |
| VOICES · região da voz | SOURCE_GAP | fechado p/ técnico, **aberto p/ produtor** |
| VOICES · data da observação | SOURCE_GAP | fechado p/ técnico, **aberto p/ produtor** |
| PORTFOLIO · carência (PHI) e n.º máx. | **COLLECTION_CAPABILITY_GAP** | mudou de natureza: o campo está no PDF do rótulo, e a casa já sabe abrir esses PDF. Deixa de ser «procurar fonte» e passa a ser «escrever o extrator» |
| WINDOWS · rastreabilidade (`SOURCE_IDS 0/29`) | **DATA_MODEL_GAP** | as fontes existem; **ninguém escreveu** qual sustentou qual janela |
| PORTFOLIO · produto × janela (`0/29`) | **DATA_MODEL_GAP** | join interno entre 219 produtos e 29 janelas |
| FIELD_NET · relato da rede comercial | **DATA_MODEL_GAP** | dado **próprio da ADAMA** |
| RADAR × 4 | herdam | melhoram quando a origem melhora |

**Cinco dos quinze não fecham com fonte nenhuma.** Isso não é má notícia — é
saber onde não gastar a próxima missão.

## OS TRÊS GAPS DE ACESSO

O dado existe e tem dono que não o publica — ou que o publica atrás de uma
porta. **Coleta não resolve.**

| gap | quem detém | como se adquire |
|---|---|---|
| **ensaio de campo com resultado** | a empresa que encomenda o ensaio. Os seis centros GEP executam e **não detêm o direito de publicar** | contrato ou parceria. Nunca coleta |
| custo médio de produção (ISMEA) | ISMEA | registo de conta |
| boletins do SeDI da ALSIA | ALSIA | inscrição gratuita — **e ainda o DNS desta máquina não alcança** `alsia.it` |

E o achado que abranda o primeiro: **a Veneto Agricoltura publica resultado
medido de ensaio**, com o número desfavorável incluído — *o tratamento no
momento de máxima eficácia melhorou produtividade e micotoxinas em **menos de
50% dos casos***, e as populações mais altas concentram-se sempre no sudoeste
(Rovigo, Padova, Venezia). Não substitui o ensaio de registo, mas é **resultado
público e medido**, que era o que faltava.

---

## S · T · AS 5 CULTURAS QUE FALTAVAM

```
S  FIVE_CROPS_SEARCHED    5 de 5
T  NEW_CROP_SOURCES      12
   culturas do casco ainda sem fonte:  NENHUMA
```

| cultura | janelas | antes | depois | quem fechou |
|---|---|---|---|---|
| Wheat | 3 | 0 | 6 | Veneto seminativi · Emilia-Romagna · ERSA FVG · Campania UTM · AIAB · Veneto Agricoltura |
| Durum Wheat | 3 | 0 | 3 | Emilia-Romagna · Veneto · AIAB |
| Maize | 3 | 0 | 8 | ERSA FVG (**BBCH 42-70**) · ERSAF Lombardia · Veneto Agricoltura |
| Soybean | 2 | 0 | 5 | ERSA FVG (*soia n. 2 del 16 febbraio 2026*) · AIAB FVG |
| Tomato | 3 | 0 | 5 | Consorzi Fitosanitari (**campos-espia não tratados**) · Campania UTM |

Dois achados que valem mais que a contagem:

- **`Boll_09_MAIS_03072026.pdf`** declara o milho em **BBCH 42-70** conforme
  época de semeadura e classe varietal. É a única fonte achada que publica
  código BBCH numérico de milho.
- **«campo-espia não tratado»**: uma parcela deixada deliberadamente sem
  tratamento para se ver a doença acontecer. Isso é observação de campo no
  sentido forte — não é modelo, é medição.

E uma **correção ao que eu escrevi**: apresentei o Bollettino Nazionale di
Fenologia da RRN como fonte de fenologia «por cultura». A busca desta missão
mediu que ele cobre **principalmente vite, olivo e robinia**. Não serve soja,
nem milho, nem trigo. Continua forte — para três culturas, não para dez. **As
arvenses vêm das regiões, não do nacional.**

## U · X · AS REGIÕES

```
U  ZERO_REGIONS_BEFORE    2   Basilicata · Valle d'Aosta
V  ZERO_REGIONS_AFTER     0
W  WEAK_REGIONS_BEFORE    4   Abruzzo · Campania · Friuli-VG · Molise
X  WEAK_REGIONS_AFTER     2   Basilicata · Molise
```

**As duas regiões a zero fecharam com fonte REGIONAL própria, não com
nacional** — fonte nacional continua a não contar, porque a fenologia muda com
altitude e distância ao mar (o próprio Abruzzo mede **~2 semanas de atraso**
acima de 400 m ou a mais de 40 km da costa).

- **Basilicata** tinha, desde **1996**, uma rede de **40 estações**
  agrometeorológicas com molha foliar e evapotranspiração por Blaney-Criddle e
  Penman-Monteith, mais boletins do SeDI em três comprensori (Metapontino, Alta
  Valle d'Agri, Valle del Bradano) e relatório climático mensal com **anomalia
  face a 1991-2020**. Passa de ZERO a FRACA — fica FRACA, e não COBERTA, porque
  é **uma** fonte e porque eu **não consegui abri-la desta máquina**.
- **Valle d'Aosta** passa a COBERTA com duas: os *Avvisi fitosanitari*
  (atualizados em **26/06/2026**, com rede de armadilhas por estação e
  distribuição por aviso afixado, gravador telefónico, web e **SMS**) e os dados
  de maturação da uva do Institut Agricole Régional.
- **Molise** continua FRACA. **Não foi pesquisada nesta missão** — e isso é
  ausência de busca, não de fonte. Foi exatamente o que a Basilicata ensinou.

⚠️ Parte do serviço da Valle d'Aosta distribui-se por **SMS e gravador
telefónico** — canais que nenhum coletor alcança. A fonte publica; parte do que
publica está fora do alcance de qualquer rota web.

---

## Y · AB · O QUE ENTRA E O QUE ESTÁ PRONTO

```
Y   NEW_SOURCES_FOUND      13
Z   NEW_STRONG              6
AA  NEW_USEFUL              2      ·  UNKNOWN (limite nosso)  5
AB  READY_TO_REGISTER      23      CRITICAL 5 · HIGH 3 · MEDIUM 15
AC  PRIMARY (validadas)    23
AD  SECONDARY (validadas)  15      — nenhuma passou a porta
AE  NEW_PEOPLE              1      Emanuele Scalcione (ALSIA, responsável do SAL)
AF  NEW_SOCIAL              0      nenhuma conta social promovida
AG  SECOND_PROOF_COUNT      9      6 CONFIRMED · 3 UNKNOWN
AH  SECOND_PROOF_DIVERGENCES 0
```

`READY_TO_REGISTER` é **uma porta, não um prémio**: entra só quem tem as dez
coisas — identidade e dono confirmados, URL canónica, **exemplo real**,
necessidade que alimenta, ferramenta que serve, âmbito, recorrência, evidência,
nenhuma duplicata verdadeira — e validação STRONG ou USEFUL. **27 ficaram fora,
e a folha REJECTED diz por quê.**

### TOP 20 · PRONTAS PARA CADASTRO

| # | valor | fonte | quem publica | ferramenta | região |
|---|---|---|---|---|---|
| 1 | CRITICAL | Bollettini colture estensive | Regione Veneto + Veneto Agricoltura | WINDOWS | Veneto |
| 2 | CRITICAL | Bollettini interprovinciali di produzione integrata | Regione Emilia-Romagna + Consorzi | WINDOWS · PORTFOLIO | Emilia-Romagna (6 áreas) |
| 3 | CRITICAL | Bollettini fitosanitari — UTM | Regione Campania | WINDOWS · VOICES | Campania, por UTM |
| 4 | CRITICAL | Bollettini pomodoro da industria | Consorzi Fitosanitari RE/MO/PR/PC | WINDOWS · PORTFOLIO | 4 províncias |
| 5 | CRITICAL | Avvisi fitosanitari | Ufficio fitosanitario Valle d'Aosta | WINDOWS · FUTURE | Valle d'Aosta |
| 6 | HIGH | Bollettino Mais | ERSAF + Condifesa Lombardia NE | WINDOWS | Lombardia |
| 7 | HIGH | Bollettino seminativi biologici | AIAB FVG + ERSA | WINDOWS · VOICES | Friuli-VG |
| 8 | HIGH | Dati di maturazione dell'uva | Institut Agricole Régional | WINDOWS | Valle d'Aosta |
| 9 | MEDIUM | Bollettino Nazionale di Fenologia | RRN / MASAF | WINDOWS · RADAR | nacional |
| 10 | MEDIUM | Bollettini viticoli | Regione Veneto | WINDOWS · RADAR | Veneto |
| 11 | MEDIUM | Bollettino agrometeo e fitosanitario | ARSAC | WINDOWS · VOICES | Calabria, 8 zonas |
| 12 | MEDIUM | Notiziario agrometeorologico | **AMAP Marche** *(era «ASSAM»)* | WINDOWS | Marche |
| 13 | MEDIUM | Bollettini fenológicos privados | Agralia, Brescia | WINDOWS · VOICES | Brescia |
| 14 | MEDIUM | Bollettini agronomici per vite | Terre dell'Etruria | WINDOWS · VOICES | Toscana costeira |
| 15 | MEDIUM | **Dataflow `..._COLTIVAZIONI_1`** | ISTAT | MARKET · RADAR | nacional + província |
| 16 | MEDIUM | Indice prezzi mezzi correnti | ISMEA | MARKET | nacional |
| 17 | MEDIUM | Monitoraggio costi medi | ISMEA | MARKET | nacional |
| 18 | MEDIUM | Cantina Italia — giacenze | MASAF/CREA via SIAN | MARKET | nacional + região |
| 19 | MEDIUM | Banca dati prodotti fitosanitari | Ministero della Salute | PORTFOLIO · COMPETITORS | nacional |
| 20 | MEDIUM | Convegno «Prodotti fitosanitari» | Regione Emilia-Romagna + empresas | PORTFOLIO · COMPETITORS · FUTURE | nacional no conteúdo |

---

## AI · AJ · PROVAS

```
AI  RED_TEAM_RESULT     18 ataques · 18 OK · 0 falhas · 0 detetores cegos
AJ  REGRESSION_RESULT   708 testes · 37 falhas · igual à base 581b5059
                        NEW_FAILURE = 0 · PRE_EXISTING_FAILURE = 37
```

O **ataque 9 apanhou a entrega** na primeira passagem, e tinha razão: onze
fontes diziam *«HIGH — semanal»* sem que eu tivesse visto **uma única data** na
rota. «Semanal» escrito na página é a **promessa da casa**; recorrência medida
seria contar edições no arquivo, e eu **não contei nenhuma**.

A correção não foi apagar o HIGH nem enfraquecer o teste — foi o dado passar a
dizer o que sabe, numa coluna nova:

```
RECORRENCIA_ESTADO = OBSERVADA | DECLARADA | NAO_SEI
```

As 23 prontas para cadastro estão todas **OBSERVADA**. As DECLARADA ficaram
fora, rotuladas.

Outros ataques com achado: **#11** (dono errado — o meu «ASSAM»), **#17** (três
fontes vivas salvas de BROKEN), **#13** (acesso separado de fonte), **#4**
(nacional não conta como regional), **#6** («mais» português ≠ milho italiano).

**System Map:** regenerado pela cadeia manual. `MAPA=OK · peças=100 ·
ligações=336`. Peça nova declarada: `C-IT-FECHAR-GAP` (zona `Z-CANDIDATAS`),
com os 8 ficheiros de código e a planilha. 12 de 13 provas passam;
`P9_CODIGO_DECLARADO` reprova por `.github/workflows/scrap-social.yml`,
commitado em `df165da9` e **já não declarado em `191dbda4`** —
`PRE_EXISTING_FAILURE`.

## AK · AO · O QUE NÃO SE FEZ

```
AK  COLLECTION_RUNS_CREATED    0        RAW_OBSERVATIONS_CREATED   0
AL  DERIVED_CREATED            0        STRUCTURED_CREATED         0
AM  ADMISSION_CREATED          0        WAITING_ROOM_DELTA         0
    SOURCE_ID                  0        DOCUMENT_ID                0
    ATLAS_PROMOTION      NOT_RUN        PORTAL_CHANGED            NO
    TAXONOMIA_NOVA            NO        ARQUITETURA_NOVA          NO
AN  XLSX_PATH   candidatas/ITALY-SOURCE-GAP-CLOSURE-2026-09-14.xlsx
AO  KNOW_HOW_DELTA   ATUALIZAÇÃO NECESSÁRIA — texto abaixo, sem criar cabeça nova
```

**O que isto não prova:**

- a sonda **lê HTML e não executa JavaScript**: quatro portais do Estado
  italiano ficam ilegíveis por isso, e ficam UNKNOWN, não BROKEN;
- **três fontes vivas não abrem desta máquina** (DNS local). Uma delas é a que
  fecha a Basilicata;
- **nenhuma edição foi contada em nenhum arquivo.** Toda recorrência é declarada
  ou observada numa única leitura — nunca medida ao longo do tempo;
- **nenhum conteúdo foi guardado em ficheiro.** Há rota, código HTTP e exemplo
  lido — não há prova arquivada;
- **nenhuma afiliação de pessoa foi verificada** em perfil institucional;
- **Molise não foi pesquisada**, e continua FRACA.

---

## AO · DELTA PARA O KNOW-HOW — *atualização necessária*

> **Não crio cabeça nova.** O know-how canónico está bifurcado em 20 cópias com
> cinco cabeças divergentes, §118 ocupado duas vezes, e a decisão de qual é
> canónica é do Luciano. O texto abaixo está **em forma final**, com o número em
> branco.

### § — FALHA DE LIGAÇÃO NÃO É ATESTADO DE ÓBITO

Quando uma rota não abre, há sempre **duas hipóteses e elas não são
simétricas**: a fonte morreu, ou nós não a alcançamos. Tratar as duas como uma
apaga do acervo casas que publicam todos os dias.

Medido em 14/09/2026, duas vezes e por dois caminhos:

- a missão `italy-source-qualification-v1` recuperou **cinco fontes oficiais**
  (ISMEA, ARPA Puglia, ARPA Sicilia, Regione Abruzzo, UNIPI) que «pareciam
  mortas» e eram um helper de TLS com a porta do proxy fixa em código de outra
  sessão — falhava em silêncio;
- esta missão salvou **três agências regionais** (ALSIA, ERSA FVG, ARPA
  Piemonte) de serem declaradas `BROKEN`. `getaddrinfo failed` em Python **e**
  em curl; o resolvedor público `8.8.8.8` devolve endereço para as três.

**Lei:** antes de escrever que uma fonte está morta, perguntar a um resolvedor
independente se o domínio existe no mundo. Se existir, o veredito é `UNKNOWN` e
a nota diz **«a dúvida é nossa»**.

**E os três estados nunca se juntam:** `BROKEN` pede fonte nova; `BLOCKED` pede
outra rota do mesmo dono; `UNKNOWN` pede outra saída de rede. Um único rótulo
«morta» destrói as três ações.

### § — CADÊNCIA ESCRITA NA PÁGINA É PROMESSA, NÃO MEDIÇÃO

«Semanal» impresso no cabeçalho é o que a casa **pretende** fazer. Recorrência
medida é **contar edições no arquivo**. Em 14/09/2026, onze fontes desta entrega
declaravam `HIGH — semanal` sem que uma única data tivesse sido lida na rota.

**Lei:** `RECURRING_POTENTIAL` viaja sempre com `RECORRENCIA_ESTADO ∈
{OBSERVADA, DECLARADA, NAO_SEI}`. Promessa e medição na mesma coluna é a forma
mais barata de uma tabela mentir a favor de quem a escreveu.

---

## O QUE PERGUNTARAM, EM PALAVRAS SIMPLES

**Antes tínhamos 15 buracos graves.**

**Abrimos as 37 fontes sugeridas** e, de verdade, **15 eram boas** (9 fortes e
6 úteis). Outras 15 abrem mas são de segunda mão. **Cinco não serviram** e
**duas não conseguimos abrir** — e essas duas estão vivas; o problema é a nossa
internet.

**Pesquisamos as cinco culturas que faltavam** — trigo, trigo duro, milho, soja
e tomate, que são quase metade das janelas. Agora **todas as dez culturas da
casa têm fonte**. A melhor surpresa foi o milho: existe um boletim que escreve o
número da fase da planta (BBCH 42-70), coisa que nenhuma das 37 tinha.

**As regiões que estavam vazias eram Basilicata e Valle d'Aosta.** Agora as
duas têm fonte própria. A Basilicata tinha, desde 1996, uma rede de 40 estações
que ninguém tinha procurado — o buraco era da nossa busca, não do território.
**Sobra o Molise**, que eu não pesquisei.

**Encontramos 13 fontes novas**, 6 delas fortes. **Dessas todas, 23 estão
prontas para cadastro** — passaram uma porta com dez exigências, e 27 não
passaram.

**Ainda faltam estas coisas:** a voz de **quem cultiva**, com região e data
(achamos a voz do técnico do governo, que é outra pessoa); ligar produto a
janela; escrever de onde veio cada janela; e tirar a carência de dentro do PDF
do rótulo.

**E estes buracos não se resolvem procurando fonte pública:** o ensaio de campo
oficial é **segredo por lei** — é de quem pagou; o relato da rede comercial é
**dado da própria ADAMA**; e três coisas são conta interna, não coleta.

**Nenhuma coleta foi executada.** Nada foi cadastrado.

---

## VEREDITO

```
VEREDITO = PASS
```

O §43 diz que PASS não exige zerar todos os gaps. Exige quatro coisas, e as
quatro estão feitas:

| exigência | como se cumpriu |
|---|---|
| **cada gap corretamente classificado** | os 15 críticos têm TIPO declarado: 10 de fonte, 4 de modelo de dado, 1 de capacidade nossa — mais 3 de acesso identificados fora deles. Cinco dos quinze **não fecham com fonte nenhuma**, e isso está escrito |
| **busca suficiente** | as 5 culturas pesquisadas (0 ficam sem fonte), as 2 regiões a zero fechadas com fonte regional própria, 7 buscas registadas com rodada e sinal de saturação |
| **fontes fortes comprovadas** | as 50 rotas abertas com sonda provada por 4 controles · 23 prontas para cadastro, todas PRIMARY e todas com recorrência OBSERVADA · segunda prova 6 CONFIRMED, 0 DIVERGED · e o ISTAT provado com **13,5 MB de dado real**, não com uma página |
| **nenhuma invenção** | 18 ataques, 18 OK · quatro defeitos da minha própria sonda corrigidos antes de publicar · dois números meus desmentidos e substituídos pelos verdadeiros — o dataflow do ISTAT e o dono da ASSAM · e o ataque 9 obrigou-me a separar promessa de medição |

**O mais valioso desta missão não foram as 13 fontes novas.** Foi descobrir que
**o meu próprio identificador de dataflow do ISTAT não existia**, e que três
agências regionais italianas estavam a um passo de ser declaradas mortas por
uma falha de DNS desta máquina.

```
HARD STOP
```
