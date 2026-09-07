# CHECKPOINT — MOTOR → NAVEGAÇÃO → SUPERFÍCIE VISÍVEL

`branch = claude/visible-intelligence-v1` · `base = 5a5ab60` · `pacote = V21-06c6421d001ea52a`

Missão P0: *o portal visível não corresponde à inteligência integrada.* Corrigir **só** a
camada `MOTOR → NAVEGAÇÃO → SUPERFÍCIE VISÍVEL`. Não reinvestigar coleta, pacote ou motor.

Regra que governa tudo o que segue:

```
VALUE_EXISTS = YES  e  VISIBLE = NO   ->   NÃO ESTÁ INTEGRADO
```

---

## 1 · O MAPA — as sete perguntas

### 1.1 · Qual arquivo é servido em `/`

`vercel.json` na raiz: `outputDirectory: italia-portale/client`, `cleanUrls: true`. Logo `/`
serve **`italia-portale/client/index.html`** — 1.839 bytes, uma marca e um
`<meta http-equiv="refresh" content="0; url=accesso.html">`.

A cadeia inteira, medida:

```
/  ->  index.html  --(meta refresh 0s)-->  accesso.html
                   --(submit do formulário, accesso.html:314)-->  casa.html
                   --(CTA «PORTALE COMPLETO»)-->  portale.html
```

`accesso.html` já tinha sido corrigido numa rodada anterior para entrar em `casa.html` e não
no radar. **A raiz não era o defeito.** O defeito estava no que havia *depois* dela.

### 1.2 · Para onde leva `PORTALE COMPLETO`

`casa.html:633-634` (cabeçalho) e `casa.html:797-798` (rodapé) → **`portale.html`**. Dois
links, o mesmo destino, sem parâmetro nenhum: abre na vista por omissão.

### 1.3 · Qual arquivo contém o menu lateral que o utilizador fotografou

**`portale.html`**. A barra desenha-se em três `sc-for` — `nav` (165), `navEvidence` (173),
`navIntegrationItems` (183) — sobre `navDef`, definido em `portale.html:4406-4436`.
A entrada `['future', T.navFuture, navN('futureSignals')]` é a que imprimia
`Signal Archive 3` / `Archivio segnali 3`.

`casa.html` também tem uma navegação (as «portas», linha 664), mas é horizontal, no
cabeçalho, e sem contadores. O `3` só existe em `portale.html`.

### 1.4 · Onde estão as 44 fichas de Future Radar

**Não estão no pacote V2.1.** Cadeia própria, medida:

```
italia-portale/client/upstream/IT-FUTURO-HANDOFF-LINHA-B-V1.json   (COLLECTION = ITFC)
        ->  scripts/it_casa_dados.py  (linha 349 lê · linha 503 monta o registo)
        ->  italia-portale/client/italy-casa.js   ITALY_CASA.RADAR_FUTURO
        ->  casa.html  ledgerHtml()  (linha 550)
```

`RADAR_FUTURO`: `TOTAL 45 · RENDERIZAVEIS 44 · DERRUBADOS 1 · PREPARAR 23 · MONITORAR 21 ·
AGIR_AGORA 0`. `REGISTRO` tem 44 linhas, `ITFC-001` a `ITFC-045`.

**O que essas 44 linhas carregam, e o que não carregam.** O handoff declara
`CAMPOS_OBRIGATORIOS_DO_CARTAO` com 13 campos (`F_CITACAO_VERBATIM`, `F_FONTE`,
`F_DATA_DO_FATO`, `F_REGIAO`, `F_CULTURA`, `F_ALVO`, `T_JANELA_DE_APLICACAO`, `TRIGGER`…).
Nenhum deles viaja: `LIMITACOES_POR_SINAL` traz estado, ação, classe de portfólio e as
**contagens** das lacunas — a prosa da investigação fica a montante, em português.
Só 3 dos 44 (`IT-TOP3-SENSORES-V1.json`) têm conteúdo rico, e é conteúdo de *sensor*.

> **44 «fichas» é o que se pode dizer hoje. 44 fichas ricas não existem em lado nenhum
> deste repositório.** Tornar as 44 «acessíveis» só pode significar o registo que existe.

### 1.5 · Por que Future Radar não aparecia nesse menu

Três causas independentes, todas medidas:

| # | Causa | Onde |
|---|---|---|
| 1 | `navDef` não tinha entrada nenhuma para o Radar Futuro | `portale.html:4406-4436` |
| 2 | `navCasa` — a única referência a `casa.html` no portal inteiro — era **código morto**: declarada na linha 4457, consumida em lugar nenhum | `portale.html:4457` |
| 3 | `AMMESSE` (as rotas de hash aceites) não tem `radar`; e `isRadar` está fixo em `false` | `portale.html:2773` e `:9691` |

`ROUTES_TO_FUTURE_RADAR = 0`, confirmado.

`navCasa` foi removida da barra num commit anterior (47bb8b8) por repetir o contador da
reunião — e a razão era boa. O que ficou por fazer foi pôr no lugar a voz **do Radar
Futuro**, que não repete contador nenhum.

### 1.6 · `casa.html` e `portale.html` são duas arquiteturas concorrentes?

**São duas arquiteturas. O acoplamento é de sentido único.**

| | `casa.html` | `portale.html` |
|---|---|---|
| dados | `italy-casa.js` (`ITALY_CASA`) | `italy-handoff-v21.js` → `ITALY_APP_MODEL` |
| gerador | `scripts/it_casa_dados.py` | `scripts/site_v21_ingest.py` |
| render | `innerHTML` imperativo | template `sc-if`/`sc-for` + classe `Component` |
| portão | `casa-gate.mjs` (30/30) | `checks.mjs` + 56 módulos |
| dicionário | `meeting-labels.js` | `italy-i18n.js` + `meeting-labels.js` |
| ligações para o outro | **7** (`portale.html` e `portale.html#…`) | **0** — era este o buraco |

Partilham tokens de design e o dicionário de códigos canónicos. Não partilham dados: as 44
do Radar Futuro **não existem** do lado do portal, e as 43 oportunidades não existem do lado
da casa a não ser como contagem.

Não são um erro a fundir. São duas superfícies com donos diferentes — e o defeito era o
zero da última linha.

### 1.7 · Que famílias novas existem no motor e não tinham componente visível

Medido por varrimento de `portale.html` (marcação + lógica), família a família:

| Família | No pacote | Referências em `portale.html` |
|---|---|---|
| **`scienceCorpus`** | 763 | **0** |
| **`transcripts`** | 184 | **0** |

Estas duas atravessavam a cadeia inteira — ACERVO → pacote → motor → navegador — e
**nenhuma linha de código as lia**. Chegavam em cada carregamento e morriam ali.

Não é uma lista longa por acaso: as outras 32 famílias do pacote têm pelo menos uma
referência. Estas duas eram as únicas com zero, e são exatamente as duas que a rodada
anterior acrescentou ao motor.

---

## 2 · A TABELA DE PROVA

Gerada por `italia-portale/audit/superficie-visivel.mjs`, que monta o portal a sério
(uma montagem por medição) e conta o que a marcação consome. `run.mjs` chama-a (`SV1`).

```
FAMILY                  IN_MODEL   VISIBLE  REACHABLE  STATUS           ROUTE
OPPORTUNITIES                 43        13         43  VISIVEL          #meeting -> ficha (mcase)
FUTURE_RADAR                  44        44         44  VISIVEL          menu «Radar Futuro» -> casa.html#radar-futuro
SIGNAL_ARCHIVE                 3         3          3  VISIVEL          #future
TRANSCRIPTS                  184         4          4  VISIVEL_PARCIAL  #meeting -> ficha -> «Voce tecnica»
SCIENCE                      851        92        154  VISIVEL_PARCIAL  #science · ficha -> «Scienza»
ADS_TEMPORAL                 414        27        414  VISIVEL          #competitors · ficha -> «Concorrenza»
FACT_TIME_PLACE              947         3          3  VISIVEL_PARCIAL  ficha -> «Luogo del fatto»
FIELD_SIGNALS                  7         7          7  VISIVEL          #archive (tipo FIELD_SIGNAL)
COMPETITOR_ACTIVITIES        577        12        569  VISIVEL_PARCIAL  #competitors
PRODUCT_RELATIONSHIPS       2030        41       2030  VISIVEL          #portfolio -> produto
```

**Três números, não dois.** `VISIBLE` é o que a primeira chegada desenha; `REACHABLE` é o
que se abre com uma interação. Confundi-los foi como este portal chegou a ter 44 fichas
desenhadas e nenhuma porta.

Notas que a tabela carrega e que não se podem perder:

- **`ADS_TEMPORAL` não é família do pacote.** O tempo do anúncio viaja *dentro* de
  `competitorActivities` (`startDate` / `endDate` / `isActive`). 414 têm data; **27 estão
  ativos**. Histórico de anúncio não é ativo, e as duas contagens estão separadas onde
  aparecem.
- **`FACT_TIME_PLACE`**: `FACT-TIME-PLACE-V1.json` está declarado FORA em
  `site_v21_ingest.py` — «a lei não viaja num agregado, viaja NOS REGISTOS». Correto. O que
  faltava era a outra metade: provar que ela **chega ao ecrã**. Agora chega, e mede-se.
- **`OPPORTUNITIES` 43 → 13**: é a lei de relevância ADAMA (13 + 21 + 8 + 1), não uma
  truncagem. As outras duas populações têm entrada própria no fundo do radar.
- **`FUTURE_RADAR`**: a rota faz parte da medição. Se a voz sair da barra, o visível cai a
  zero por mais linhas que `casa.html` desenhe.

### Controlo negativo

A régua foi corrida em *worktree* sobre `5a5ab60` — o HEAD que o utilizador tinha diante dos
olhos:

```
FUTURE_RADAR       44        0  INVISIVEL   NENHUMA ROTA DO PORTAL
TRANSCRIPTS       184        0  INVISIVEL
FACT_TIME_PLACE   947        0  INVISIVEL
FAIL
```

**A régua reproduz o defeito antes de o declarar corrigido.** Uma que só soubesse passar não
teria provado nada.

---

## 3 · O QUE FOI CORRIGIDO

| # | Pedido | O que se fez |
|---|---|---|
| 1 | `/` deve abrir o portal correto | Medido: já abria. `/` → `index.html` → `accesso.html` → `casa.html` → `portale.html`, sem elo partido. O defeito não estava na raiz, estava no beco a seguir a ela — corrigido em 2 e 3. Nada foi mexido em `index.html`. |
| 2 | Future Radar na navegação | `navCasa` (código morto) dá lugar a `navRadarFuturo`, **imediatamente a seguir a «Archivio segnali»**. Menu agora: `Archivio segnali 3` · `Radar Futuro 44`. |
| 3 | As 44 fichas com superfície acessível | `casa.html` ganha âncora `#radar-futuro`, uma sétima porta e abertura da dobra ao chegar pelo endereço. O registo dos 44 abre-se sozinho. |
| 4 | Signal Archive continua separado | A frase «Popolazione distinta dal Radar Futuro» mantém-se **e passa a ter rota**: pastilha «L'altra popolazione: Radar Futuro 44 →». Uma distinção declarada e não verificável não é uma distinção. |
| 5 | Uma ficha com inteligência real | Bloco **«Cosa si sa oltre il caso»**: ciência, voz técnica, concorrência — cada uma com o seu ligame declarado, o **luogo del fatto** em cada linha, e o silêncio dito em voz alta onde não há material. |
| 6 | QA/regras/missing em «Ver prova» | Interruptor **VEDI LA PROVA**, fechado por omissão, sobre os códigos do motor, as siglas de regra e as referências de evidência. |

### Sobre a correção 6 — uma divergência declarada

O pedido diz «QA/regras/**missing links** vão para Ver prova». O bloco **COSA MANCA** ficou
**fora** do interruptor. Razão:

> `docs/design/CONTRATO-DE-DESIGN-SINTONIA.md` §3: `NÃO SEI / NOT_COLLECTED / NOT_KNOWN` —
> «mesmo peso tipográfico do fato. Nunca cinza-claro, nunca em rodapé, **nunca colapsado por
> padrão**.»

E `CLAUDE.md` faz do contrato o desempate. Uma lacuna atrás de um botão é uma lacuna que
ninguém abre. O que entrou no interruptor foi só a **tracciabilità** — códigos, siglas e ids.

**A prova dobra-se. A lacuna não.**

### O bloco novo, e as suas leis

- **O ligame é declarado, não adivinhado.** A ficha fala `CROP_GRAPEVINE` / `ISSUE_DOWNY_MILDEW`;
  o corpus fala `VINE` / `DOWNY_MILDEW`. A ponte é `AM.cropResolve` — que já existe e já é o
  dono da tabela `CROP_BY_TOKEN`. Não se escreveu uma segunda tabela de sinónimos. O prefixo
  `ISSUE_` é o espaço de nomes da entidade e retira-se; não se traduz nada.
- **Onde a coppia não se resolve, o bloco não procura — declara que não pode procurar.**
- **A aderência ao caso ORDENA, não filtra.** Esconder os 32 fora do caso congelado faria ler
  os 34 como tudo o que existe sobre a coppia.
- **O luogo del fatto viaja em cada linha.** Medido em Vite × Peronospora: 66 materiais, dos
  quais `FR 15 · TN 3 · IT 2 · DE 1 · NÃO ESTABELECIDO 45`.
  *Uma coppia que coincide não faz de um preprint francês prova italiana.*
- **A escada da transcrição tem cinco degraus e nenhum implica o seguinte.**
  `TRANSCRIPT_USED_AS_EVIDENCE = false` em 184/184, e a ficha di-lo: «nenhuma destas é usada
  como prova neste pacote».
- **A concorrência liga-se por SÓ cultura, e diz-se.** `issueIds` está vazio em 577/577;
  fingir uma coppia sobre texto livre seria a juntura frágil que o controlo A3 proíbe.
  `ATIVO` fica separado de `HISTÓRICO`.

**O silêncio é conteúdo.** 10 das 13 fichas não têm material nenhum para a sua coppia, e a
ficha diz «é uma coppia que este pacote não interrogou» — que não é o mesmo que «não há
ciência».

---

## 4 · UM DEFEITO ANTIGO QUE ESTA CORREÇÃO DESTAPOU

A voz «Radar Futuro» tornou `casa.html` alcançável a partir do portal — e com isso o portão
`brandwell.mjs` passou a **ler essa página pela primeira vez**. Reprovou:

```
BW3  No headline (>=16px) in ALL CAPS  ->  1
     25px · "AZOXYSTROBIN + PROTHIOCONAZOLE"
```

O defeito é anterior a esta missão. O que era novo era a possibilidade de o ver.

> **Uma página que nenhuma rota alcança é uma página que nenhum portão lê.**

Consultado o ADAMA Design System (`rules/typography-and-casing.md`): «ALL CAPS — rare. Single
words only, never long text» e «Title Case for all product names». Dois princípios ativos em
fila não são uma palavra só. Mudou a **caixa** — que é desenho; as letras do registo ficaram
intactas, porque o nome é um facto.

`ADAMA_DESIGN_SYSTEM_MATCH = FOUND` (`rules/typography-and-casing.md`, e o cartão do
componente reutilizado para o bloco novo). `NEW_PATTERN_REQUIRED = NO` — o bloco «Cosa si sa
oltre il caso» reutiliza o cartão que os blocos vizinhos da ficha já usam.

A primeira versão do ajudante chamava-se `titolo` e colidiu com uma função com o mesmo nome
que já existia em `casa.html`. O `casa-gate` apanhou-a de imediato: 43 `[object Object]` no
ecrã, um por caso. Renomeado para `cassaTitolo`.

---

## 5 · ENTREGA

```
ROOT_SURFACE                    = italia-portale/client/index.html
                                  (meta-refresh 0s -> accesso.html -> casa.html)
FULL_PORTAL_SURFACE             = italia-portale/client/portale.html
                                  (CTA «PORTALE COMPLETO», casa.html:634 e :798)
FUTURE_RADAR_SURFACE            = ITALY_CASA.RADAR_FUTURO.REGISTRO (44 linhas)
                                  desenhado por casa.html ledgerHtml(), âncora #radar-futuro

WHY_FUTURE_RADAR_WAS_INVISIBLE  = três causas, todas medidas:
                                  1. navDef não tinha entrada para ele
                                  2. navCasa — a única referência a casa.html — era código morto
                                  3. AMMESSE não tem rota, e isRadar está fixo em false
                                  ROUTES_TO_FUTURE_RADAR = 0

FUTURE_RADAR_MODEL_COUNT        = 44   (45 julgados, 1 derrubado)
FUTURE_RADAR_VISIBLE_BEFORE     = 0    (medido em 5a5ab60 pela mesma régua)
FUTURE_RADAR_VISIBLE_AFTER      = 44

HIGH_VALUE_FIELDS_HIDDEN_BEFORE = scienceCorpus  59 campos × 763 registos  ->  0 no ecrã
                                  transcripts    51 campos × 184 registos  ->  0 no ecrã
                                  0 referências em portale.html, marcação e lógica

HIGH_VALUE_FIELDS_HIDDEN_AFTER  = 20 campos chegam ao ecrã, com o seu estado:
                                  ciência   title · venue · year · citedBy · caseAdherence
                                            countryOfFact · doi · queryCrop · queryIssue
                                  voz       title · channel · publishedAt · chars
                                            factCountry · videoId · platform · usable
                                            usedAsEvidence · routeCrop · routeIssue
                                  os restantes continuam a viajar e a não se ver — declarado,
                                  não resolvido, e a régua conta-o como VISIVEL_PARCIAL

READY_FOR_USER_VISUAL_REVIEW    = YES
DEPLOY                          = NÃO FEITO, como pedido
```

### Prova visual local

`.tmp/prova/` (não versionado), capturado com Chromium sobre o `client/` real servido em
`http://localhost:8912`, com `index.html` na raiz:

| ficheiro | o que prova |
|---|---|
| `01-root.png` | o que `/` serve |
| `02-portale-menu.png` | `Archivio segnali 3` **e** `Radar Futuro 44`, lado a lado |
| `03-signal-archive.png` | a declaração de população distinta, agora com rota |
| `04-casa-radar-futuro.png` | `casa.html#radar-futuro` aterra no registo, com a dobra aberta |
| `05-ficha-topo.png` | a ficha sem siglas, com «VEDI LA PROVA» |
| `06-ficha-oltre-il-caso.png` | ciência, voz técnica e concorrência, com o luogo del fatto |
| `07-ficha-vedi-la-prova.png` | a tracciabilità acesa |

Para reproduzir: `node italia-portale/audit/serve.mjs 8899` (nota: mapeia `/` a
`portale.html`; para ver a raiz a sério, servir o directório `client/` com `index.html` por
omissão).

### Portões

```
run.mjs                72/72   (inclui SV1, o portão novo da superfície)
superficie-visivel.mjs PASS    · FAIL em 5a5ab60, controlo negativo
casa-gate.mjs          30/30
brandwell.mjs          5/5     · BW3 passou a ser lido, e passa
meeting-gate.mjs       23/23
```

`acceptance.mjs` continua a reprovar `SHIPPED DOC MATCHES THE PACKAGE` e `V2.1 BUILD ID`.
Verificado em *worktree* sobre `5a5ab60`: **idêntico**. Não é desta missão.

---

## 6 · O QUE FICA POR FAZER, DECLARADO

- **`transcripts` e `scienceCorpus` continuam maioritariamente invisíveis.** 4 de 184 e 92 de
  851 chegam ao ecrã. O limite não é de desenho: é que só 7 coppie distintas existem entre as
  13 fichas, e o corpus foi recolhido sobre outras. `VISIVEL_PARCIAL` é a resposta honesta.
- **As 44 do Radar Futuro não têm ficha rica, e não podem ter.** 12 dos 13 campos obrigatórios
  do cartão não viajam no handoff. Isto é trabalho a montante, não de superfície.
- **`adamaProof` não foi acrescentado à ficha**: medido, o seu valor já está sempre na lista
  de produtos da mesma ficha (13/13). Acrescentá-lo imprimiria o mesmo facto duas vezes.
- **`casa.html` e `portale.html` continuam a ser duas arquiteturas.** Esta missão ligou-as
  numa direção que faltava; não as fundiu, e fundi-las não era o pedido.
- **Seis portões continuam sem corredor** (`negative-control`, `action-map-consistency`,
  `cta-navigation`, `opportunity-trace`, e outros). `superficie-visivel` não é o sétimo:
  `run.mjs` chama-o.

---

## 7 · MEETING POLISH — a inteligência passa a ver-se em segundos

Segunda passagem, sobre o mesmo HEAD. O motor já tinha tudo; a superfície é que
não mostrava. Nenhum facto novo entrou — mudou o que se vê primeiro.

### O cartão do radar

Treze cartões diziam cultura, avversità, região e estado. Somavam-se todos.

> **Se todos os cartões se parecem, nenhum diz nada.**

Cada um mostra agora `SCIENZA · VOCI TECNICHE · CONCORRENZA · SEGNALI DI CAMPO ·
PRODOTTI ADAMA` e quantas famílias independentes trazem evidência. **Sem pastilha
com zero**: uma caixa vazia desenhada para encher espaço não informa, ocupa. E as
cores não mudam por família — a regra ADAMA proíbe misturar as linhas e o cartão
já tem a sua: distingue a palavra, não a tinta.

### Um cálculo, dois leitores

`incrocio(cultura, avversità)` é o dono. Calcula-se por **coppia** (13 casos em 7
coppie) e o vocabulário resolve-se com `AM.cropResolve`, que já existia. Onde a
coppia não se resolve, não se procura: declara-se que não se pode procurar.

### A ficha

Nova ordem: herói → **RELAZIONE ADAMA compacta** → **SEGNALI CONVERGENTI** →
ciência, voz técnica e concorrência → portafoglio inteiro (um interruptor) →
`VEDI LA PROVA` → perché ora → finestra → mappa → evidenze →
**COSA NON SAPPIAMO ANCORA**.

> **O produto é a resposta. Não pode ser a primeira pergunta.**

Sete campos por produto abriam a ficha antes de se saber porque o caso existe.
Continuam todos lá, inteiros, um estrato adiante.

`QUERY_*` **não é** `PROVED_*`: cada linha de ciência diz se o texto sustenta a
coppia ou se só a busca a encontrou. Medido em Vite × Peronospora: 66 materiais,
**34 sustentados**.

A concorrência mostra empresa, data, estado temporal e a citação pública na
língua em que foi dita. `ATIVO` separado de `HISTÓRICO`.

### O Radar Futuro

Abria com `ITFC-001` e `6 / 11`. Um identificativo interno e um rácio de defeitos
são a **recibo** da leitura, não a leitura. Abre agora pela **ação** — preparar ou
monitorar — e pelo que o cartão **pode citar**. O id, o sensor e as lacunas ficam
no rodapé de cada ficha. E não se inventou nada: 12 dos 13 campos obrigatórios
não viajam no handoff, e onde a fonte não dá um facto, não aparece um.

### Os três casos WOW

Medidos por diversidade de famílias, não escolhidos à mão. Os três com as quatro
famílias (ciência + voz técnica + concorrência + relação ADAMA):

| caso | região | famílias |
|---|---|---|
| Vite · Peronospora | Friuli-Venezia Giulia | 4 — 66 ciência · 4 voz · 44 concorrência · 2 ADAMA |
| Vite · Peronospora | Umbria | 4 — idem |
| Vite · Peronospora | Emilia-Romagna | 4 — idem |

Usam **o mesmo componente** de todos os outros. São exemplos, não uma UI especial.

### Três erros de consola a menos

`<path d="{{ p }}">` estava no documento antes do runtime o substituir, e o parser
SVG lia-o logo: três erros por carregamento, medidos. O ícone passa a data-URI —
o padrão que esta página já usava para todos os outros.

> **Um erro que o leitor não vê é na mesma um erro.**

### Um portão que guardava uma tabela

`LEDGER_44_NAVIGABLE` prendia-se a `table tbody tr` e reprovou porque a
apresentação mudou. A lei é «os 44 estão desenhados», não «há uma tabela».

> **Um portão preso ao desenho cai com o desenho, e leva a lei com ele.**

### Medido

```
run.mjs                72/72   (com SV1)
casa-gate              30/30
brandwell               5/5
meeting-gate           23/23
browser                 7/7
responsive             PASS
mobile                 50 ecrãs · overflow 0
reachability           PASS
build-gate             PASS · V21-06c6421d001ea52a
release-gate (disco)   BROWSER_ERRORS 0 · BROKEN_LINKS 0
viagens do leitor      26/26 passos · ERROS DE PÁGINA 0 (eram 3)
```

### Promoção

```
claude/visible-intelligence-v1            = 4b22957
claude/auditoria-acervo-inteligencia-2nknje = 4b22957
árvores                                    = 6541bba… idênticas
commits exclusivos perdidos                = 0 (fast-forward de 5a5ab60)
```

---

## 8 · CONTEXTO REGIONAL, FORÇA DA EVIDÊNCIA, E O ARCHIVIO FORA DA BARRA

Três pedidos do leitor, medidos antes de escritos.

### 8.1 · A carta a caselle — o que o motor tem, e o que não tem

A referência mostrava três linhas: **Region**, **Crop relevance** («Major Olive
area — ISTAT regional scale») e **Validate next** («Basilicata · Calabria»).
Só uma delas tem dado no motor.

| linha da referência | campo do motor | estado | o que se desenha |
|---|---|---|---|
| Region | `GEOGRAPHY` / `CLAIM_GEOGRAPHY` | **existe** — 17/43 nomeiam região, 19 Itália, 7 UE | nome + a casella acesa |
| precisão NUTS | derivado do lugar declarado | **existe** | `NUTS-2` região · `NUTS-0` país · `EU` |
| escala | `GEOGRAPHIC_SCOPE` | **existe** — 19 nacional, 10 provincial, 7 regional, 7 europeu | linha própria |
| Crop relevance / área ISTAT | `AREA_OFICIAL_HA`, `AREA_OFICIAL_ANO` | **null nos 43**, e `OFFICIAL_AREA_NOT_CLIENT_SAFE` declarado nos 43 | **não se desenha** |
| Validate next (regiões vizinhas) | não existe campo | **inexistente** | **não se desenha** |
| nº de regiões do par | `COMMERCIAL_MAGNITUDE_DIMENSIONS.REGIOES_DO_PAR` | existe (18/43) mas está em `BOOKKEEPING_EXACT` | **não atravessa a fronteira, por lei** |

Onde a referência punha uma frase de relevância agronómica, a ficha põe a
**lacuna com as palavras do motor** — `missingGeo`, filtrado por código dentro
de `meeting-surface.js`, onde os códigos vivem, para que só a frase atravesse.

    UMA MAPA QUE CALA O QUE NÃO SABE É UMA MAPA QUE MENTE.

A carta tem três estados e nenhum quarto: região declarada acende **uma**
casella na cor da linha ADAMA; escala nacional acende **todas** no tom
profundo; escala europeia não acende nenhuma. A nota por baixo diz, em
palavras, que é um índice e não uma projecção — e o bloco é `aria-hidden`,
porque cada facto que a carta desenha está escrito ao lado.

### 8.2 · A força da evidência

`mcStrength` estava calculado desde a missão anterior e nunca era desenhado.
Passa a barras, com a nota que impede a leitura errada: a escala é **interna ao
caso**, não é uma pontuação.

### 8.3 · O Archivio segnali sai da barra, e não do produto

Três, ao lado de quarenta e quatro, na mesma coluna, lia-se como «aqui dentro
não há quase nada». A voz sai da barra lateral; **nada foi apagado**:

```
rota #future                     responde
Component.CAPABILITY_OF.future   admitida
AMMESSE                          admitida
vista visibleSignals             desenha os 3
```

E ganha a porta que faltava: a vista gémea do Radar Futuro passa a nomeá-lo com
o número do dono (`saRoute`), espelho exacto da linha que, do arquivo, remete
para os 44. A régua `superficie-visivel.mjs` deixou de assumir a rota e passa a
**medi-la** (`portaArquivo`): se a linha se partir, `SIGNAL_ARCHIVE` cai a
`VISIBLE = 0`, exactamente como cairia se a rota não existisse.

### 8.4 · ADAMA Design System — o que se reutilizou e o que não existia lá

Consultado antes de desenhar. O manifesto declara `Badge · Button · Card ·
ProductIcon · Tag` mais os cartões de marca; **não** declara carta, grelha de
casellas, gráfico nem barra.

```
Card                          REUTILIZADO   superfície #1C1817 · raio 14px · borda 1px
cores da linha (pest/disease) REUTILIZADO   CATEGORY_UI.color · .dark · .soft
Earth Grey / Text Grey        REUTILIZADO   #8F8886 · #EDEAE9
ícone oficial da categoria    INTACTO       nenhum ícone novo, nenhum emoji

ADAMA_DESIGN_SYSTEM_MATCH = NOT_FOUND   (carta a caselle · barra de força)
NEW_PATTERN_REQUIRED      = YES
```

**Motivo:** o Design System não tem componente de mapa nem de gráfico. Os dois
padrões novos foram construídos apenas com tokens oficiais — não introduzem cor,
tipo, raio nem ícone fora da paleta — e passam BW1 (paleta), BW2 (contraste AA) e
BW3 (sem caixa-alta em títulos ≥16px).

### 8.5 · Medição

```
run.mjs                72/72
brandwell               5/5   (BW1 paleta · BW2 contraste · BW3 sem caixa-alta)
casa-gate              30/30
meeting-gate           23/23
cta-navigation         13/13
viagens do leitor      31/31 passos · ERROS DE PÁGINA 0
mobile 390px           overflow 0
carta a caselle        20 casellas · 1 acesa em 13/13 fichas · cor = linha da categoria
```


---

## 9 · A PORTA DEIXA DE SER DUAS

`index.html` mostrava marca, nome, linha de marca e um botão «ENTRA NELLA
DEMO». `accesso.html` mostrava marca, nome, linha de marca e o mesmo botão. O
`meta refresh` a zero segundos não tirava a primeira — fazia-a **piscar**.

    DUAS PORTAS IGUAIS, UMA ATRÁS DA OUTRA, NÃO SÃO UMA ENTRADA.
    SÃO UMA HESITAÇÃO.

O reencaminhamento passa para a CABEÇA do documento e usa `replace`: parte
antes de o corpo ser pintado — logo não há lampejo — e não deixa etapa no
histórico, portanto o «voltar» a partir da página de acesso sai do site em vez
de ressaltar no splash.

**O ficheiro fica**, e não por hábito: `deploy-surface.mjs` exige `/index.html`
entre as rotas públicas e o `build` do `package.json` verifica a sua existência
antes de cada deploy. Uma decisão de aparência não retira uma rota. Sem
JavaScript e sem refresh, o `<noscript>` continua a dar uma porta.

```
navegações medidas   / -> /accesso.html      (o splash nunca é pintado)
h1 na chegada        «L'intelligenza agricola che anticipa il campo»
voltar do portal     /accesso.html, sem splash
build-gate           PASS
deploy-surface       0 problemas · /index.html continua na superfície pública
viagens do leitor    31/31
```

---

## 10 · PORTFÓLIO — O QUE ESTÁ VAZIO, E PORQUÊ

Pergunta do leitor: os cartões vazios são dados que temos e não estão ligados,
ou dados que não temos? **Medido nos 51 do catálogo comercial:**

| | produtos | o que existe | veredicto |
|---|---|---|---|
| cartões com relações | **27** | ligações verificadas e/ou relacionadas | completo |
| registo + etiqueta, **zero** linhas de uso | **14** | nº de registo e URL da etiqueta oficial | **falta a leitura da etiqueta** |
| sem registo nenhum | **10** | nada | **não temos o dado** |
| dado que existe e não está ligado | **0** | — | a junção não está partida |

As 2030 linhas `LABEL_USE_RELATIONSHIP` nomeiam 102 produtos distintos. Nenhum
dos 24 cartões vazios aparece lá sob qualquer grafia. Os nomes que *rimam* —
`GOLTIX® TOP` (018814) contra `GOLTIX` (002732) · `GOLTIX 700 SC` (010569) ·
`GOLTIX BETA` (018813) · `GOLTIX SUPER` (017580); `Mirador® SC` contra
`MIRADOR TURBO` (017824); `FOLPAN 80 WDG` e `Folpan® Energy` contra
`FOLPAN GOLD` — são **registos diferentes**. Ligá-los seria inventar.

Os 14 com etiqueta são o grupo accionável: a etiqueta está em
`fitosanitari.salute.gov.it`, temos o URL, ninguém leu os usos dela. É uma
**lacuna de recolha**, não de ligação — e a recolha está fora do que esta missão
pode fazer.

---

## 11 · OS RÓTULOS LIDOS POR DENTRO — 102 → 119, E O PACOTE REGENERADO

Partiu de uma pergunta simples sobre os cartões vazios do portfólio: *temos o
dado e não está ligado, ou não temos o dado?* A resposta obrigou a descer até à
recolha, e a subir de volta até ao pacote canónico.

### 11.1 · O que já existia

`scripts/rotulos_baixar.py` e `scripts/rotulos_ler.py` já tinham corrido a
2 de Setembro: **163/163** etiquetas descarregadas do Ministero, **2030 pares**
lidos de **102/163** produtos. Os cartões vazios não eram lacuna de recolha —
eram o leitor a recusar adivinhar, que é a lei dele:

> *«Um rótulo com 4 culturas e 6 alvos não tem 24 pares. Tem os pares que a
> TABELA une, linha a linha.»*

### 11.2 · A rota que estava fechada por um certificado

`research/.../LABEL-USES.json` regista 7 rotas de recuperação tentadas. A do
Ministero falhou com `SSL certificate problem: unable to get local issuer
certificate` — o servidor serve só o certificado folha, sem o intermédio. Fui
buscar o intermédio ao endereço que o próprio certificado publica (extensão AIA,
`tiTrust.crt.sectigo.com`) e completei a cadeia. **A verificação TLS ficou
ligada**: não se desliga uma fechadura por estar mal montada do outro lado.

### 11.3 · Determinismo antes de mudar

163 PDF restaurados e conferidos contra o sha256 de 02/09: **163/163
idênticos**. Leitor corrido sem lhe tocar: **2030 pares, ficheiro byte a byte
igual ao commitado**. Só depois disso mudei uma linha.

### 11.4 · As quatro mudanças

| # | o quê | porquê |
|---|---|---|
| 1 | `malatti` no cabeçalho da tabela | o `Avastel®` abre com «Coltura \| Malattia fungina»; o padrão aceitava `patogen`, o termo técnico, e não o do agrónomo |
| 2 | numa tabela de doenças não se pesca daninha | `Blumeria graminis` saía como PLANTA_INFESTANTE num fungicida de cereais; a coluna já declara a natureza do alvo |
| 3 | uma tabela sem linha de cultura não é tabela | uma frase (`...la coltura abbia almeno 3 foglie ed infestanti...`) fazia de cabeçalho e **fechava a porta do herbicida** a TOPIK, PRESSING, VIP |
| 4 | verbos e legendas não são organismos | «Eseguire massimo», «Moderatamente suscettibili» têm a forma de binómio latino |

**Tentei e desfiz:** fechar a tabela em «Applicare il prodotto». Essas frases
também aparecem *dentro* de tabelas boas — cortava 6 produtos. Um ganho que
custa seis leituras não é um ganho.

### 11.5 · Onde o leitor continua a dizer NÃO SEI, e está certo

`GOLTIX® TOP` nomeia 17 daninhas e nenhuma cultura tratada: todas as culturas na
página estão em contexto de **rotação** («in caso di fallimento della coltura»).
`ACTIVUS ME` nomeia 26 culturas, todas na lista de **fascia di sicurezza** —
zonas tampão, não usos autorizados. Ligá-las seria exactamente «pescar alvo de
outra cultura».

### 11.6 · A subida até ao pacote

O `CANONICAL-PACKAGE-CONTRACT` nomeia um dono único da geração:
`claude/acervo-to-package-intelligence-v1`. A cadeia foi corrida **lá** — e
primeiro com o input antigo, reproduzindo `V21-06c6421d001ea52a` exactamente,
como controlo. Só então o input passou aos 2389.

```
BUILD_ID          V21-06c6421d001ea52a -> V21-fb74d2728213e8dd
relações          2030 -> 2389
rótulos lidos     102/163 -> 119/163
alvos distintos   78 -> 84
portfólio         27/51 -> 30/51 cartões com dados

casos             43        (inalterado)
WATCH 22 · TO_VALIDATE 9 · FUTURE_PREPARATION 7 · VALIDATE_NOW 3 · ACT_NOW 2
                            (inalterados — é isto que prova que está certo)
```

### 11.7 · Os recibos andam com o pacote

`CANONICAL-PACKAGE-CONTRACT.json` e `INGESTION-REPRODUCTION.json` passam a
nomear `40477d5`; o id anterior entra em `STALE_KNOWN_BUILD_IDS` **com a razão
pela qual saiu**. O `H2` — que existe para apanhar linhas que somem em silêncio
— foi actualizado com a justificação escrita ao lado: 2030 → 2389 não é deriva,
é ter lido mais do mesmo documento.
