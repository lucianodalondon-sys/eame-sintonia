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
