# CASCO CLIENT-DEMO — o que já estava feito, o que faltava, e o que passou a estar certo

```
CURRENT_PRODUCT_SCOPE      = ITALY_ONLY
PRODUCTION_PROMOTION       = BLOCKED  (à espera da aprovação do preview)
AUTORIDADE VISUAL          = /SINTONIA/SINTONIA ITALIA/CLIENT-DEMO/
AUTORIDADE DE DADOS        = intelligence real, provada
```

**Medido em** `claude/auditoria-acervo-inteligencia-2nknje` @ `d69b299`
**Casco medido**: `/home/user/canonical/italia-portale/client/` — o gémeo local do
CLIENT-DEMO. O `portale.html` do Dropbox e o desta pasta **diferem em dez sítios,
todos guardas contra queda** (`&& e.temp`, `(X || {})`, `MK && MK.EXTRA`). Nenhuma
diferença de desenho. O casco está, portanto, dentro do repositório.

---

## A · A INVERSÃO QUE A MEDIÇÃO OBRIGOU A DECLARAR

A direcção pedia: *pegar no casco CLIENT-DEMO, remover o synthetic data, ligar o
adaptador real*. A primeira medição mostrou que **essa operação já tinha sido feita
neste ramo** — e refazê-la a partir do casco reintroduziria 151 leituras de dados
falsos que depois teria de voltar a remover.

| | CLIENT-DEMO | PORTAL DE HOJE |
|---|---:|---:|
| leituras do pacote demonstrativo no ecrã | **154** | **3** |
| colecções demonstrativas lidas | **35** | **3** |

As três que restam: duas são **só geometria e cor** (a grelha 4×5 das vinte regiões
administrativas; seis pares de cor de departamento), a terceira alimentava um ecrã
que deixou de ter porta (ver **C**).

O que **não** estava feito, e passou a estar, está em **C** a **G**.

---

## B · FASE 4 · INVENTÁRIO DA SUBSTITUIÇÃO

35 colecções que os ecrãs do CLIENT-DEMO lêem, com 1 002 registos demonstrativos.

| ESTADO | COLECÇÕES |
|---|---:|
| `REPLACED_WITH_REAL` | **20** |
| `NO_REAL_EQUIVALENT` (tabelas de cor, rótulo, KPI escritos à mão) | **12** |
| `ANCORA_LETTA` (as três acima) | **3** |

As vinte substituídas: `WINDOWS`→`cropWindows` 29 · `ACTIVITIES`→`competitorActivities`
577 · `CASES`→`opportunities` 43 · `ARCHIVE`→`archive` 1 114 · `SOURCES`→`sources` 189
· `PRODUCTS`→`products` 173 · `RECORDS`→`scienceRecords` 88 · `PEOPLE`→`people` 66 ·
`COMPANIES`→`competitorCompanies` 11 · `CPRODUCTS`→`competitorProducts` 36 · e mais dez.

Tabela completa: `node audit/casco/fase4-inventario.mjs`

---

## C · GATE `SYNTHETIC_DEMO_VISIBLE = 0` — provado, não afirmado

Duas portas davam para o inventado e foram fechadas:

1. **`portale.html#field`** abria o ecrã Field Sales: sete representantes
   inventados, dezoito mensagens de campo escritas à mão, três sugestões com nomes
   de cidades e concorrentes nunca observados. O menu não a oferecia; a lista de
   endereços admitidos oferecia. Não existe equivalente real — vozes públicas e
   boletins regionais são outra coisa, não uma mensageria interna — por isso o
   bloco **esconde-se**, não se enche com a demonstração.
2. **O botão dos cenários**, no Arquivo de sinais, acendia 85 registos de
   apresentação dentro de um ecrã que no resto só traz intelligence provada.

Nenhum código apagado: duas rotas a menos.

**A prova** (`audit/casco/demo-visibile.mjs`) não lê comentários. Renderiza as dez
vistas do menu **nas duas línguas** e **1 222 fichas de detalhe** abertas sobre
identificadores reais (as 43 da reunião incluídas), e procura dentro do que seria
desenhado as **696 cadeias que existem SÓ no pacote demonstrativo**. As impressões
digitais calculam-se contra as dezasseis fontes reais carregadas, porque o demo
copia registos verdadeiros para dentro de si: calibrar sobre metade do verdadeiro
produz um alarme por cada cultura.

```
SYNTHETIC_DEMO_VISIBLE = 0        (20 vistas + 1 222 fichas, 0 falhas de render)
EXPERIMENTAL_DISEASE_VISIBLE = 0  (596 ecrãs, duas línguas)
EXPERIMENTAL_LABEL_VISIBLE   = 0
```

---

## D · FASE 2 · BRANDWELL — os dois débitos fechados

O bloco `<style>` do portal difere do casco **numa só coisa**: um `@media
(max-width: 900px)`. A 1440px não muda um pixel. Acessibilidade, não redesenho.

Os dois débitos declarados fecharam:

- **BW1** · «SVILUPPO MERCATO» escrevia em `#7BE0A6`, um verde que o manual não
  contém e que nenhuma regra escrita derivava. A linha continua `#00B152`, a massa
  continua o verde profundo; muda a tinta do texto, agora o verde muito claro da
  paleta publicada — **6,98:1** onde antes lia 4,95:1.
- **BW2** · a linha dos VINCOLI era âmbar a dez pixels sobre o magenta da ficha:
  **4,25:1**, abaixo do mínimo. O âmbar é a cor da área REGULATORY e ali dentro não
  era uma área — era um aviso emprestado. Passou a usar a tinta de corpo da própria
  ficha: **6,57:1**.

```
BRANDWELL_COLOR_AUDIT = 5/5   (16 ecrãs lidos do DOM calculado)
TIPOGRAFIA: BrownLL 98% · nenhuma família fora de LL Brown / Aleo / Arial
```

---

## E · GATE `FALSE_ZERO` — o registo de fontes dizia zero 141 vezes

A coluna «registos» contava as linhas do arquivo. Com trinta e uma fontes era a
leitura certa. Com **189 fontes e 9 681 registos reais** deixou de ser: o arquivo
indexa **1 114** — o que ACONTECE — e as tabelas de referência não entram lá por
desenho. Então **ISTAT dizia ZERO** alimentando 2 970 registos, o YouTube ZERO com
389, a biblioteca de anúncios ZERO com 432.

> **UMA FONTE QUE NÃO ESTÁ NO ÍNDICE NÃO É UMA FONTE QUE NÃO DEU NADA.**

Zeros: **141 → 37**, e os trinta e sete são verdadeiros. A ficha da fonte declara
agora, numa linha, quanto a fonte alimenta e quanto o arquivo consegue abrir.

**E ainda**: 158 das 189 fontes **nunca foram revistas** — o pacote declara-o linha
a linha e o portal não lia esse campo em lado nenhum. No ecrã distinguiam-se por um
travessão. Nenhuma linha escondida: a coluna de estado diz agora **«Da rivedere»**.
26 Aperta · 1 Parziale · 1 Non raggiunta · 3 Bloccata · **158 Da rivedere**.

---

## F · A CHAVE ERRADA — 1 374 linhas de rótulo não chegavam ao produto

O Portfólio mostrava «0 ✓ · 0 ○» em **39 fichas de 51**, e a leitura óbvia era que o
corpus dos rótulos não cobrisse o catálogo. Não era.

A ligação procurava o produto em `byName[U(r.product)]` — o nome em maiúsculas. Mas
esse índice tem chaves normalizadas por `PKEY`, que tira espaços, pontuação e o sinal
de marca. «LAMDEX EXTRA» procurava `LAMDEX EXTRA` dentro de um índice que conhece
`LAMDEXEXTRA`. **Só se ligavam os nomes sem espaços.**

> **UMA FICHA QUE DIZ ZERO PORQUE A CHAVE NÃO ENCAIXA ESTÁ A MENTIR COM PRECISÃO.**

| | antes | depois |
|---|---:|---:|
| relações ligadas ao produto | **656** | **2 030 / 2 030** |
| fichas de Portfólio a zero | **39 / 51** | **24 / 51** |

A ligação usa agora a mesma resolução do resto do modelo — chave normalizada, depois
as variantes que o próprio modelo declara — e, quando o nome não chega, o **número de
registo**: um identificador declarado, não uma semelhança de letras. Nenhuma ligação
nova por assonância (`product-identity I3`, «o join não uniu dois produtos
diferentes», passa).

As 24 que restam não têm linhas de uso no corpus. Esse zero é verdadeiro — e passou a
ter nome: **NÃO CONFIRMADO NESTA LEITURA**, com a cor que o modelo já publicava.

> **UM ZERO VERDADEIRO MERECE UM NOME, NÃO UM ALGARISMO.**

`FALSE_PRODUCT_RELATION = 0` — as 2 030 relações nomeiam um registo que existe no
portfólio de 173; nenhuma é órfã, nenhuma foi inventada.

---

## G · FASE 12 · O REAL É MAIS RICO — medido contra o CLIENT-DEMO

| MEDIDA | CLIENT-DEMO | PORTAL | FACTOR |
|---|---:|---:|---:|
| `REAL_SOURCE_FAMILIES` | 24 | **42** | 1,8× |
| `REAL_INTELLIGENCE_OBJECTS` | 2 017 | **10 213** | 5,1× |
| `REAL_CROSSINGS` | 9 | **67** | 7,4× |
| `REAL_REGIONS` | 25 | **46** | 1,8× |
| `REAL_CROPS` | 77 | **80** | 1× |
| `REAL_ISSUES` | 134 | **171** | 1,3× |
| `REAL_EVIDENCE_LINKS` | 774 | **1 436** | 1,9× |
| registos reais | 2 384 | **9 681** | 4,1× |
| leituras do demo no ecrã | 154 | **3** | 0× |

---

## H · FASE 11 · PARIDADE VISUAL — as 675 formas, uma a uma

A comparação não é sobre o texto — o texto TEM de mudar, porque os dados são
outros. É sobre a **forma**: a etiqueta e os seus atributos de estilo, sem
binding e sem conteúdo.

```
FORMAS DO CASCO 2 129 · MANTIDAS 1 334 · MUDADAS DE SÍTIO 121 · PERDIDAS 675
PARIDADE LITERAL          68,3%
PARIDADE COM O PISO 10px  79,6%
```

**O piso tipográfico sozinho explica 16 pontos.** O casco declara **674** corpos
de texto abaixo de 10px (326 a 9,5 · 153 a 9 · 123 a 8,5 · 72 a 8); o portal
declara **11**, e tem 690 a 10px onde o casco tinha 131. Cada etiqueta tocada
por essa regra vira, para uma comparação de strings, uma forma diferente — mesma
cor, mesmo padding, mesmo raio, mesma ordem das declarações, um pixel a mais.

> **SUBIR TODO O TEXTO UM PIXEL NÃO É REDESENHAR: É LER.**

### As 675, classificadas por 24 leitores e contestadas por um segundo

| CAUSA | FORMAS |
|---|---:|
| `ACESSIBILIDADE` (piso 10px, contraste, alvo de toque) | **395** |
| `CONTEÚDO_INEXISTENTE` (o facto não existe nos dados reais) | **224** |
| `DADO_REAL_EXIGE` (a estrutura real tem outra forma) | **28** |
| `CORREÇÃO_DE_ERRO` (bloco partido ou que derrubava a consola) | **20** |
| `DERIVA_INJUSTIFICADA` **declarada** | 8 |
| `DERIVA_INJUSTIFICADA` **confirmada após contestação** | **0** |

Os ecrãs mais afastados e porquê:

- **`isMarket` (126)** — 75 formas assentavam em `window.ITALY_MARKET`, uma
  fixture editorial que creditava oito organizações, **nenhuma** entre as 31
  fontes registadas, e cujos 23 valores 20 não existiam em observação nenhuma.
  14 formas eram os dois blocos `<svg>` que **não podiam renderizar** e produziam
  5 dos 6 erros de consola do portal a cada carregamento.
- **`isCase` (75)** e **`isCompetitors` (56)** — dominadas pelo piso 10px e por
  telhas que afirmavam relações não provadas.
- **`isSignal` (27)**, **`isProduct` (10)**, **`isBrief` (10)**, **`isArchive`
  (8)** — **100% piso tipográfico**: a mesma forma reaparece idêntica com o
  corpo a 10px.

As 8 derivas declaradas (6 em `isCProduct`, 2 em `isWindow`) foram todas
**refutadas**: cada uma tinha uma ordem escrita nos próprios cadernos de bloco
do repositório (`audit/blocks/competitor.spec.json`, `audit/_specs.json`,
`audit/_block-reports.md`), que nomeiam o binding e mandam removê-lo, com a
razão medida ao lado.

`VISUAL_PARITY_WITH_CLIENT_DEMO = **PASS**` — 675/675 com razão escrita, 0 deriva.

**Uma dívida encontrada de passagem, não um defeito:** vários campos do modelo de
mercado continuam construídos mas já não consumidos pelo markup (`mp.traj.past`,
`mp.outlookNote`, `mp.weather`, `mp.production`, `mp.flow`, `mp.confidence`,
`mp.inputs`, `mp.contextIt`, `mp.commentary`). Código morto, a limpar ou a
reatar quando chegarem as séries verdadeiras.

Medição: `node audit/casco/parita-visiva.mjs`

---


## I · FASE 7 · MAPA DE ACÇÕES — a decisão tomada e executada

**DECISÃO DE PRODUTO** (do committente): canónico é o **Mapa de Acções da
reunião**, com **cinco áreas** — Marketing · Comercial · Desenvolvimento de
Mercado · Ciência/Técnico · Supply — em **todas as 43 oportunidades**.

Executado:

- **A ficha antiga de 7 áreas saiu da superfície.** O painel que a desenhava na
  ficha legacy foi removido, e com ele as duas propriedades que o markup lhe
  passava. Nenhum motor tocado.
- **Os códigos duplicados foram unificados**, e isso destapou um defeito real:
  `AREA_UI` guardava o azul sob `SCIENCE_TECHNICAL`; o motor da reunião pede
  `TECHNICAL_SCIENTIFIC`. Nenhum dos dois nomes estava errado sozinho; juntos
  eram um buraco, e `areaUI('TECHNICAL_SCIENTIFIC')` caía no cinzento de reserva.
  **Medido no ecrã, antes:** Ciência/Técnico e Supply saíam com a mesma linha, o
  mesmo fundo e a mesma tinta. Duas das cinco áreas eram indistinguíveis.

  > **DOIS NOMES PARA UM DEPARTAMENTO NÃO SÃO UM DETALHE DE NOMENCLATURA:
  > SÃO UM DEPARTAMENTO QUE PERDE A SUA COR.**

- **Duas propriedades mortas** — `actionMapL` e `departmentsL` — continuavam a
  traduzir os códigos da mapa retirada em cada caso, carregando PORTAFOGLIO,
  SVILUPPO DI MERCATO, TECNICO E SCIENTIFICO. Nenhum nó do markup as ligava.
  Saíram. `c.actionMap` e `c.departments` **ficam intactos no registo**.
- **Os botões do MATERIAL COMERCIAL ficam** — não são um mapa — e passam a falar
  a língua canónica. O documento REGULATORY / PORTFOLIO não se perde: continua
  acessível a partir das Janelas de Cultura.

### Medido

```
MAPA_CANONICO                = mapa da reunião · 5 áreas
43_OPORTUNIDADES_TESTADAS    = 43 casos × 2 línguas · 86/86 completos · 430 linhas
MAPA_ANTIGO_VISIVEL          = NÃO
NOMES_DUPLICADOS_POR_DEPT    = 0
ACOES_INVENTADAS_ENCONTRADAS = 0
```

Cada uma das 215 linhas por língua carrega `why`, `dependency`, `nextTrigger` e
`evidence`. As linhas silenciosas nomeiam a sua razão: «Nenhuma prioridade
comercial» (38) · «Não autorizado a sair para o cliente» (38) · «Nenhum sinal de
campo corrente» (37) · «Nada a validar» (2) · «Nenhuma base factual» (1).

> **Ausência de evidência nunca vira recomendação: vira uma frase que diz o que
> falta e o que a mudaria.**

### Duas coisas medidas que NÃO corrigi, e porquê

1. **`PREPARARE — PREPARARE`** em 3 das 215 linhas. O motor emite o mesmo token
   (`PREPARE`) para o estado e para a acção, e a tabela de rótulos é plana: o
   ecrã repete fielmente o que o motor diz. Dar-lhe uma frase distinta seria
   **adaptar a inteligência ao desenho** — o que a decisão proíbe. As três
   linhas trazem, ainda assim, `why` («Prioridade comercial sem tempo
   demonstrado»), `dependency` e `nextTrigger`.
2. **A linha de 3px do MARKETING** mede 2,35:1 contra o seu próprio fundo. A
   tinta do texto mede 13,54:1 e o nome da área é o identificador; a linha é
   reforço. As cinco tintas passam AA com folga (7,41 a 13,97).

### Alcance

42 das 43 abrem-se a clique a partir de uma das três grelhas. A 43.ª
(`OPP_4C39CCC05EEB`, Arroz · Giavone) está no grupo `errored` do motor: nenhuma
grelha lhe aponta, mas abre por id e mostra as suas cinco áreas.

### Dois portões que mediam a memória, não o portal

- `meeting-browser` procurava no menu «Radar Canonico», nome retirado quando os
  dois radares viraram um. Falhava 4 vezes e **não media a superfície da
  reunião de todo**. Agora lê o nome do dicionário: 4 → 0.
- `mobile` procurava os **sete** nomes da mapa retirada, encontrava três e
  passava, porque pedia «pelo menos uma».

  > **PEDIR «PELO MENOS UMA» A UM MAPA DE CINCO É NÃO O OLHAR.**

  Agora pede as cinco: **5/5 nomeadas a 390px.**

Medição: `node audit/casco/mappa-azioni.mjs`


### Provado num browser real, não só no banco de ensaio

`audit/casco/quarantatre.mjs` não renderiza: **abre**. Clica cada cartão que as
três grelhas oferecem, nas duas línguas, e lê do vidro.

```
84 cartões abertos a clique · 42 oportunidades distintas × 2 línguas
5 caixas de departamento em cada uma · 0 códigos fora das cinco
0 fichas vazias · 0 erros de consola · 0 pedidos falhados
```

A 43.ª está no grupo `errored` do motor: abre e mostra as suas cinco áreas, mas
nenhuma grelha lhe aponta. O portão **declara-o** em vez de falhar sobre um
facto que o motor declara sozinho.

Três erros meus antes deste portão medir o que diz medir: procurava
`data-case`, o atributo da grelha retirada, e achava **um** cartão onde há
treze; subia a `closest('[onclick],div')` e clicava **qualquer coisa**, abrindo
uma ficha que não era a pedida e contando cinco caixas — 86/86 sem medir nada;
e voltava atrás com `goto` para o **mesmo** endereço, que não recarrega o
documento, ficando na ficha aberta.

> **UM PORTÃO QUE ABRE UMA FICHA QUALQUER E A CONTA BOA MEDE-SE A SI PRÓPRIO.**

### Um defeito real que este teste destapou

O portal **obedecia ao endereço só depois do primeiro clique**. O ouvinte do
fragmento vivia dentro de `go()`. Medido em Chromium: carregada a página e
mudado o fragmento seis vezes, o título ficava «Radar delle Opportunità» as seis
— enquanto a mesma página *aberta* em `#portfolio` mostrava «Portafoglio».

> **UM PORTAL QUE OBEDECE AO ENDEREÇO SÓ DEPOIS DO PRIMEIRO CLIQUE OBEDECE A METADE.**

Passou a armar-se na primeira renderização. Verificado: seis fragmentos, seis
ecrãs certos, zero erros de consola. `casa-gate` continua 30/30.

---


## J · O QUE FOI MEDIDO E ESTÁ VERDE

```
suite de auditoria            69/71   (as 2 declaram NON MISURATO — ver L)
casa-gate                     30/30
brandwell (DOM calculado)       5/5
portfolio-claims                4/4   (80 ecrãs de produto abertos)
product-identity                2/2
adama-relevance-gate            7/7
meeting-gate                  22/23   (a 1 é a mesma de L)
internal-token                  6/6   ·  0 erros de consola em todo o varrimento
counters                          0   discrepâncias modelo ↔ ecrã
reachability                   PASS   toda a família canónica se abre nalgum sítio
deploy-surface                    0   problemas de superfície pública
build-gate / prova-da-build    PASS   com o conjunto exacto que a Vercel recebe
```

---

## K · O QUE FOI VERIFICADO E ERA FALSO

- **«1 374 relações de rótulo nunca chegam a um produto»** → chegam todas: as 2 030
  nomeiam um registo do portfólio de 173. O que falhava era a chave da ligação (**F**).
- **«170 de 189 fontes mostram 0 elementos»** → o campo `linkedRecordCount` que o
  pacote traz está a zero em 170, mas o modelo tem referências para 151 delas. O
  ecrã mostrava zero em 141; agora em 37, e esses são reais (**E**).
- **`action-map-consistency` acusava «12 áreas caídas, 0 no ecrã»** → a auditoria
  clicava num cartão da reunião e depois procurava o markup do ecrã legacy. Alvo
  desactualizado, não defeito do portal (**I**).

---

## L · O QUE CONTINUA POR MEDIR, E PORQUÊ

`W2` · `O1` · `V4` · `SNAPSHOT_SOURCE_HEAD_VALID` — **o pacote canónico gera-se, não
se guarda**. Não está no repositório, por contrato. Falhavam antes destas alterações
(verificado em `0fb3979`). Gera-se em
`claude/opportunity-commercial-priority-v1 @ 55c2674`.

`rtv-gate` · `pdf-gate` — precisam de `pdfjs-dist`, que não está instalado neste
contentor. Não são defeitos do portal.

---

## M · GATES

```
SYNTHETIC_DEMO_VISIBLE            = 0        PASS
EXPERIMENTAL_DISEASE_VISIBLE      = 0        PASS
EXPERIMENTAL_LABEL_VISIBLE        = 0        PASS
BRANDWELL_PARITY                  = PASS
FALSE_PRODUCT_RELATION            = 0        PASS
FALSE_ACTION_ROUTING              = 0        PASS
FALSE_ZERO                        = 37 reais, 0 falsos   PASS
READY_REAL_INTELLIGENCE_LOST      = 0        PASS
BROWSER_ERRORS                    = 0        PASS
BROKEN_LINKS                      = 0        PASS
UNKNOWN_HIDDEN                    = 1 encontrado e corrigido (coluna de estado das
                                    fontes); sem gate geral — ver N
VISUAL_PARITY_WITH_CLIENT_DEMO    = PASS     675/675 com razão escrita · 0 deriva
DUPLICATE_CAPABILITIES            = 0        resolvido pela decisão de produto
```

---

## N · UMA MEDIÇÃO QUE NÃO CONSIGO FAZER HONESTAMENTE

`UNKNOWN_HIDDEN` não tem gate geral. Razão medida: `renderVals()` devolve as
propriedades de **todos** os ecrãs em cada render — contar travessões por ecrã dá o
mesmo número em todos (11,3%), que não distingue nada. Um número que não distingue é
pior do que nenhum. A instância concreta que encontrei está corrigida (**E**).

---

## O · O QUE NÃO FIZ, E PORQUÊ

- **Não reconstruí o portal a partir do casco.** A medição em **A** mostra que isso
  reintroduziria 151 leituras de dados falsos. Declaro a divergência em relação ao
  método pedido; o objectivo — a experiência do demo alimentada só por dados
  provados — é o que persegui.
- **Não escolhi entre os dois mapas de acções** (**I**). É semântica de produto.
- **Não uniformizei os nomes dos departamentos.** Renomear «APPROVVIGIONAMENTO» para
  «SUPPLY» (ou o contrário) é a mesma decisão.
- **Não promovi nada para produção.**

---

## P · `PORTAL_READY_FOR_PRODUCTION = NO`

---

## Q · BLOQUEIOS

1. **`DUPLICATE_CAPABILITIES = 1`** — dois mapas de acções, sete áreas contra cinco,
   dois nomes para o mesmo departamento, sobre as mesmas 43 oportunidades. Precisa de
   uma decisão sua: qual das duas fichas é a ficha.
2. **`VISUAL_PARITY_WITH_CLIENT_DEMO` por classificar** — 675 formas do casco que o
   portal não desenha. A medição está feita; falta dizer, uma a uma, se a razão é
   dado real, correcção, acessibilidade, conteúdo inexistente — ou deriva.
3. **Aprovação do preview.** `PRODUCTION_PROMOTION` continua `BLOCKED`.
