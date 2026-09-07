# REGRAS DE INTERPRETACAO E ROTEAMENTO

Toda afirmacao derivada desta ferramenta nasce de uma regra escrita aqui, com
identificador. Nenhum roteamento nasce de bom senso. O que nenhuma regra cobre
sai como `UNKNOWN`, e `UNKNOWN` aparece na tela.

## 1 · As cinco camadas, que nunca se misturam

| camada | quem produz | pode ser inventada? |
|---|---|---|
| `FACT` | a fonte oficial | nunca |
| `DERIVED_REGULATORY_MEANING` | regra `R-*` sobre o FACT | so por regra escrita |
| `POTENTIAL_BUSINESS_IMPLICATION` | regra `B-*`, e sempre rotulada como potencial | so por regra escrita |
| `RECOMMENDED_REVIEW` | regra `V-*` — pede olhar humano, nao afirma nada | so por regra escrita |
| `ACTION` | **nenhuma regra automatica** | **nunca** |

`ACTION` nao e emitida por esta ferramenta. O parser nao produz acao. O maximo
que a ferramenta faz e `RECOMMENDED_REVIEW`, que e um convite a olhar.

## 2 · Leis que nenhuma regra pode violar

    DOCUMENT_CHANGED        != REGULATORY_MEANING_CHANGED
    SOURCE_REORDER          != LABEL_CHANGE_EVENT
    EXPIRY                  != WITHDRAWAL
    PARSER_FAILURE          != REGULATORY_ABSENCE
    CATALOG_PRESENCE        != MARKET_PRESENCE
    LABEL_CHANGE            != MARKETING_CLAIM_CHANGE
    EXPIRY_EVENT            != DEMAND_DROP / STOCK_RISK / STOP_SELLING

## 3 · Regras de significado regulatorio (`R-*`)

| id | condicao (FACT) | significado derivado | prova |
|---|---|---|---|
| `R-01` | `data_scadenza_autorizzazione` mudou entre dois instantaneos oficiais | a validade declarada da autorizacao mudou | dois CSV oficiais arquivados, campo a campo |
| `R-02` | `stato_amministrativo` mudou | o estado administrativo declarado mudou | idem |
| `R-03` | registro presente em B e ausente em A | produto passou a constar no registro | idem |
| `R-04` | registro presente em A e ausente em B | produto deixou de constar entre ativos | idem |
| `R-05` | `ragione_sociale` mudou | o titular declarado mudou | idem |
| `R-06` | `sostanze_attive` mudou apos normalizacao multivalorada | a composicao declarada mudou | idem |
| `R-07` | `data_decreto_revoca` / `data_decorrenza_revoca` mudou | houve ato de revoga com data | idem |
| `R-08` | sha256 do PDF da etichetta mudou entre duas capturas | o documento do rotulo mudou | dois PDFs com hash distinto |
| `R-09` | validade oficial ja passou e o estado nao e Revocato/Scaduto | a data de validade passou **e o registro segue listando o produto como autorizado** | um campo do CSV vigente |
| `R-10` | `EXCLUSION_IS_NOT_PERMISSION` — uma cultura cujo unico apoio textual no rotulo esta **dentro** de uma janela de exclusao (`ad esclusione di`, `escluso/a/i/e`, `ad eccezione di`, `tranne`, `eccetto`) nao pode ser publicada como uso autorizado | o leitor de uso reusado nao modela escopo negativo. Medido: em `002983` e `013405` toda ocorrencia da raiz `cilieg` esta dentro de "Pomodoro (ad esclusione di Pomodoro ciliegino)", e mesmo assim `CILIEGIO x OIDIO` saia como uso autorizado — uma exclusao de tomate cereja virou permissao de cerejeira |
| `R-11` | `CROP_ASSIGNMENT_MUST_SURVIVE_THE_RULES` — a **cultura** de uma linha de dose so vale se o token da cultura estiver na mesma celula da coluna de cultura que a linha, medido pelos fios desenhados da tabela. Onde nao estiver: `CROP_ASSIGNMENT_CONTRADICTED_BY_RULE`, e a linha nao publica dose | `dose_validar.py` conferia se um fio separa a linha do **valor**; ninguem conferia se um fio separa a linha da **cultura**. Medido: na etichetta `008259` p.3 o token `Cimici` esta em y=182,8 e `Tabacco` em y=207,9, com fio desenhado em y=201,1 atravessando a coluna de cultura entre os dois — a linha `Cimici 600` e de `Porro`. A ferramenta publicava `TABACCO x CIMICI = 600 g/ha` com o selo `EXATA`, o mais forte que ela tem, em cinco produtos. Eram as **unicas cinco** juncoes exatas do acervo |
| `R-12` | `LABEL_CEILING_IS_PART_OF_THE_LABEL` — teto de dose por cultura escrito **fora** da tabela vale tanto quanto a tabela. Dose exibida acima do teto sai marcada, com as duas frases literais lado a lado, e a ferramenta **nao** calcula um terceiro numero | a etichetta e um documento unico. `008259` escreve, sob a tabela, &ldquo;non superare le seguenti dosi per ettaro: soia, carciofo, lattughe e simili, finocchio: 600 g/ha&rdquo; e a tabela da 580-1200 para soia. A string `non superare` nao aparecia uma unica vez no payload: a nota nunca tinha sido coletada. Casamento por **frase inteira** — `mais dolce` nao e `mais` |
| `R-13` | `TARGET_TEXT_LITERAL_CHECK` — **duas coisas, e a distincao importa para quem audita.** O MODULO (`alvo_literal.py`) procura o texto do alvo literalmente no rotulo, com o texto reconstruido POR COLUNA, e emite `TARGET_TEXT_FOUND_LITERALLY` / `NOT_FOUND_LITERALLY` / `NOT_CHECKED`. **Ele nao rebaixa nada.** O CASCO (`juntaDose` em `app.js`) USA esse estado como portao: um par cujas candidatas sao todas `NOT_FOUND_LITERALLY` sai `DOSE_NOT_PROVED_TARGET_NOT_LITERAL`, sem numero. Quem rebaixa e a tela, e o numero de pares rebaixados esta na legenda dela | a versao anterior desta linha dizia, em negrito, "nenhuma linha e rebaixada por esta regra" enquanto o casco rebaixava 152 pares: a lei escrita descrevia o modulo e nao o portao, e um arbitro nao podia auditar R-13 pela lei. E o teste comparava o alvo com o texto da pagina INTEIRA, onde uma etichetta de tres colunas intercala as linhas das tres: os 152 rebaixados vinham de poucas celulas REAIS quebradas em duas linhas de texto, e eram falso alarme. Com a reconstrucao por coluna — mesmos fios verticais e mesmas caixas de palavra que R-11 e R-14 usam — 119 linhas voltaram a ser literais e a fusao provada de `008259` continua NAO literal, que e o controle que importa |
| `R-10b` | `SOWING_BAN_IS_NOT_A_USE` — se **toda** ocorrencia do nome de uma cultura no rotulo cai dentro de uma frase de semeadura em sucessao/rotacao, o estado nao pode ser `ATTESTED_OUTSIDE_EXCLUSION`: e `CROP_ONLY_IN_ROTATION_RESTRICTION`, e o par nao e desenhado sob "Usos autorizados" | `R-10` so testava "a cultura ocorre FORA de janela de exclusao", e uma proibicao de semeadura nao tem marcador de exclusao nenhum. Medido: `017868` e `017585` sao herbicidas de ARROZ a base de imazamox e publicavam BARBABIETOLA e COLZA como uso autorizado, carimbados `ATTESTED`. A unica ocorrencia das duas palavras nos dois PDFs e &ldquo;Barbabietola da zucchero e colza possono essere seminate solo dopo 2 mesi dal trattamento&rdquo; — a frase e procurada no texto em ORDEM DE LEITURA, porque no texto de coluna ela vem partida em tres pedacos com uma linha de outra coluna no meio |
| `R-14` | `USE_PAIR_MUST_SURVIVE_THE_RULES` — o **par cultura x alvo** so vale se algum glifo do alvo estiver dentro da celula desenhada que contem o nome da cultura. Onde nao estiver: `PAIR_CONTRADICTED_BY_RULE`, e o par **nao entra** em `uses`. Onde o teste nao puder rodar, `PAIR_NOT_CHECKABLE_*` com o nome proprio do motivo — nunca aprovacao | a rodada 2 achou os defeitos na camada de DOSE e os consertos foram aplicados na camada de dose: `R-11` confere a cultura da *linha de dose*, `R-12` o teto *da dose*, `R-13` o alvo *da linha de dose*. Nenhum foi aplicado a camada de PARES DE USO, que e a afirmacao regulatoria mais fundamental — `R-11` tirou o NUMERO de `TABACCO x CIMICI` e deixou de pe a AFIRMACAO DE USO, com o selo verde `TABELA`. Medido com esta regra: **47 pares contraditos**, e os 47 estao na lista que o arbitro da rodada 3 mediu por conta propria, com outro instrumento — entre eles os 18 alvos falsos de `012573` EKO OIL SPRAY, cujo irmao `014386` OLIONET, com a MESMA frase, sai com zero |
| `R-15` | `INHERITED_LIMITS_MUST_SURVIVE_THE_RULES` — `MAX. APLICACOES` e `INTERVALO` herdados de celula mesclada tem de estar numa celula desenhada que **cubra a linha**; e quando a etichetta escreve &ldquo;N applicazioni: &lt;lista de culturas&gt;&rdquo;, a **lista manda sobre a posicao de linha**. Sem prova: `NOT_VALIDATED` ou `NOT_PROVED`, nunca numero com selo `HERDADA` | numero de tratamentos e restricao regulatoria. Medido: em `008259`/`013560`/`013590` p.2 a celula mesclada de `n.max` que cobre Dorifora + Cimici + Nottue contem um unico valor, `1`, e a ferramenta publicava `MAX=2` e `INTERVALO=7 giorni` para a linha Dorifora com selo `HERDADA` e `CONFIRMED_BY_RULE`, alimentando 96 pares — enquanto os irmaos `015275` e `017687` leem a MESMA linha como `MAX=1`. E em `004701` PIRIMOR 50 a nota mesclada &ldquo;1 applicazione: ... lattughe e insalate&rdquo; / &ldquo;2 applicazioni a distanza di 7-12 giorni: carciofo, cetriolo...&rdquo; era distribuida por POSICAO e trocada: alface, a cultura de ciclo curto onde o excesso de aplicacoes E o risco de residuo, saia com o dobro |


### 3b · Regras de literalidade e de geometria da tabela (`R-17` a `R-22`)

Estas seis nasceram nas rodadas 4 e 5 e a tela ja as citava ao leitor enquanto
este documento parava em `R-15`. O §4b ja tinha condenado exatamente isto uma
vez, com `P-01` a `P-05`: **uma regra citada e nao escrita e uma regra que
ninguem pode conferir.** Foi um arbitro independente que pegou a reincidencia;
agora o portao `UI_RULE_IDS_ARE_DEFINED_IN_REGRAS` compara os dois conjuntos a
cada execucao e nao aceita diferenca.

Nao existe `R-16` publicada. Ela foi tentada — uma regra de escopo por PROSA, em
`prosa_escopo.py` — e **rejeitada**: nao discriminou, e ficou como diagnostico
que nao entra em producao e nao carimba nada. O numero fica vago de proposito,
para nao dar a impressao de que a lei tem um buraco onde ela tem uma recusa.

Como em `R-13`, a coluna **portao na tela** e obrigatoria: o que importa para
quem audita nao e o estado que o modulo emite, e sim o que a interface esconde,
rebaixa ou deixa de afirmar por causa dele. E a coluna traz DUAS medidas
diferentes, porque confundi-las e o proprio erro de `R-13`: o que a FORMULA
manda, e quantos itens ela de fato derruba NO CENSO DE HOJE. Uma regra pode
estar escrita na formula e nao mover nada — isso nao a torna decorativa, mas
dizer que ela "fecha o selo" sem dizer que hoje fecha zero seria descrever o
codigo e chamar isso de medicao.

**Aviso sobre os nomes em CAIXA_ALTA desta secao.** De `R-10` a `R-15` o nome
curto (`EXCLUSION_IS_NOT_PERMISSION`, `USE_PAIR_MUST_SURVIVE_THE_RULES`) e um
token que existe no codigo. De `R-17` a `R-22` **nao**: estes seis modulos nao
se dao nome curto nenhum, e os unicos identificadores que eles emitem sao o
`RULE_ID` e os estados. Os nomes abaixo sao **transposicao deste documento**,
escritos para a familia ler junto, e nao citacao do repositorio. Ficam em
italico por isso.

| id | condicao (FACT) | significado derivado | portao na tela | prova |
|---|---|---|---|---|
| `R-17` | *TARGET_NAME_MUST_BE_A_WORD_OF_THE_DOCUMENT* (nome deste documento) — o **nome do alvo** publicado tem de aparecer no texto do rotulo, lido nas tres formas do `pdftotext` (fluxo, `-layout`, `-raw`). Estados: `TARGET_NAME_LITERAL` (2.617), `TARGET_NAME_INFLECTED_IN_LABEL` (34), `TARGET_NAME_BY_TAXONOMY_NOT_IN_LABEL` (222), `TARGET_NAME_NOT_CHECKED` | o nome veio do documento, de uma flexao dele, ou de uma **taxonomia que este repositorio nao tem** — e inferencia tem de viajar rotulada como inferencia | **esta na formula do selo `FATO` e hoje derruba ZERO pares.** A formula exige `LITERAL` ou `INFLECTED_IN_LABEL`; medido no censo de hoje, todo par que `R-14` absolve ja tem nome de alvo literal ou flexionado, entao tirar esta coluna da formula produziria os mesmos 1.324 fatos. Isso NAO e motivo para tira-la — os 222 por taxonomia sao reais e estao medidos no documento —, mas &ldquo;medido contra o CODIGO&rdquo; e &ldquo;medido contra o CENSO&rdquo; sao duas coisas. Os 222 continuam visiveis, com o nome do estado e o texto que o rotulo escreve ao lado | `007555` escreve &ldquo;ditteri cecidomidi (Contarinia pyrivora), lepidotteri (Cydia pomonella, Phyllonorycter blancardella)&rdquo; e a ferramenta publicava CECIDOMIA, CARPOCAPSA e LITOCOLLETE. `Cydia pomonella` **e** a carpocapsa — mas quem sabe disso e uma taxonomia que nao esta aqui, nao pode ser mostrada ao lado da afirmacao e nao volta ao documento. O estado do meio nasceu de 34 pares em que a etichetta escreve &ldquo;Ruggini&rdquo; e a ferramenta publica RUGGINE: plural italiano, nao taxonomia |
| `R-18` | *QUOTED_TEXT_MUST_EXIST_IN_THE_DOCUMENT* (nome deste documento) — toda frase que a interface imprime **entre aspas**, com o verbo &ldquo;o rotulo escreve&rdquo;, tem de existir literal e contigua numa leitura PLANA do `pdftotext`. A coluna que este projeto remonta colando linhas **nao conta como leitura**: ela cola sem olhar os fios horizontais e produz 755 sentencas que atravessam um fio desenhado | aspas sao a afirmacao mais forte que a ferramenta faz, porque convidam quem le a ir conferir no PDF. Uma citacao remontada e pior que um numero errado: manda a pessoa procurar no documento uma frase que nao esta la, e o que ela conclui e que o documento e que esta errado | **fecha o verbo de citacao**: `citavel()` so aceita `QUOTE_VERBATIM` (4.261). Os outros oito estados saem com nome proprio e o texto vai como `leitura do extrator`, nunca entre aspas — 894 cortadas no meio de palavra, 754 com parentese aberto e nao fechado, 560 nao contiguas, 523 curtas demais, 312 linhas remontadas de celulas, 150 com palavra que nao esta na pagina, 40 cortadas no meio de linha, 6 que so existem na remontagem | `SF-12`: 318 doses citavam &ldquo;ravanello, zucchino sedano&rdquo; e nas coordenadas da fonte `zucchino` e `sedano` sao celulas PROPRIAS — a string nao existe no papel. `SF-07`: `004701` imprimia &ldquo;tranne spinacio&rdquo; quando a etichetta exclui espinafre **baby leaf**, invertendo o escopo de estreito para largo com um recorte que E substring verbatim |
| `R-19` | *LABEL_VALIDITY_HAS_MORE_THAN_ONE_FORM* (nome deste documento) — a vigencia declarada pela propria etichetta e procurada em todas as formas medidas no acervo, e nao so em `valida dal X al Y`. Estados: `VALIDITY_WINDOW_READ` (1), `VALIDITY_PHRASE_PRESENT_FORM_NOT_READ` (160), `VALIDITY_PHRASE_NOT_FOUND` (2), `VALIDITY_NOT_CHECKED` | `PARSER_FAILURE != REGULATORY_ABSENCE`. A regra **nao** parseia a data da forma nova: nada no acervo prova que a data de &ldquo;modificata ai sensi ... con validita dal&rdquo; e o mesmo fato que a data de &ldquo;valida dal ... al&rdquo;, e inventar essa equivalencia para preencher campo vazio e o movimento que a lei zero proibe | **nao rebaixa nada — devolve**: o campo saia `NOT_PRESENT` em 162 dos 163 rotulos, e `NOT_PRESENT` le-se &ldquo;nao esta no rotulo&rdquo;. Agora a tela mostra a **frase literal** e o estado; quem precisa da data le a frase | medido no acervo: 150 rotulos escrevem &ldquo;Etichetta autorizzata con&rdquo;, 145 &ldquo;decreto dirigenziale del &lt;data&gt;&rdquo; e **112 escrevem &ldquo;con validita dal &lt;data&gt;&rdquo;** — 112 rotulos declaravam desde quando a etichetta vale e a ferramenta dizia que nao declaravam. A forma que era lida existe em **1** |
| `R-20` | *COVERAGE_MUST_BE_COUNTED_BY_DRAWN_CROP_CELL* (nome deste documento) — alem da cobertura por ROTULO, conta-se por **celula de cultura desenhada**: acham-se os nomes de cultura por um vocabulario ABERTO (as celulas que o leitor de dose gravou, mais os 46 nomes de uso), calcula-se a celula desenhada de cada ocorrencia com o mesmo instrumento de `R-14`, e cada celula sai `CROP_BLOCK_READ` (536), `CROP_BLOCK_NOT_COLLECTED` (211) ou `CROP_BLOCK_IN_VOCABULARY_NOT_READ` (147) | cobertura por rotulo esconde o que o leitor nao leu: **o bloco nao lido desaparece no denominador do bloco lido**. O terceiro estado e o mais grave, porque ali o nome ESTA no vocabulario e mesmo assim nao virou par — nao e diferenca de dicionario | **nao rebaixa par nenhum**: e uma segunda cobertura, publicada ao lado da primeira na tela de COBERTURA. O numero **nao** e &ldquo;a cobertura verdadeira&rdquo; — uma celula com nome de cultura nao e necessariamente bloco de uso autorizado | `008259` conta como coberto com 184 pares, e na p.3 tem celulas de cultura com fio desenhado, cheias, cujo nome nunca virou par: PORRO, LATTUGHE, SCAROLE, RUCOLA, FINOCCHIO. O vocabulario de uso e uma lista fechada de 46 nomes e nenhum desses esta nela |
| `R-21` | *CROP_NAME_MUST_BE_A_WORD_OF_THE_DOCUMENT* (nome deste documento) — a irma de `R-17` do lado da CULTURA, que e a camada mais cara das duas porque diz em que lavoura o produto entra. `CROP_NAME_LITERAL` (2.821), `CROP_NAME_INFLECTED_IN_LABEL` (31), `CROP_NAME_NOT_IN_LABEL` (21 na tela) | passar da palavra do documento para o nome publicado e uma **equivalencia de cultura**, e equivalencia de cultura precisa de prova documental ou taxonomica: semelhanca de escrita nao e prova | **esta na formula do selo `FATO` e hoje derruba ZERO pares**, exatamente como `R-17`: os 21 ja caem por outra coluna antes de chegar aqui. `payload.py` diz isso de si mesmo em comentario desde a rodada 4 — &ldquo;tirar `crop_name` desta formula produz um payload byte-identico&rdquo;. Os 21 continuam visiveis com o estado e a leitura do extrator ao lado | os 21 nao sao um fenomeno so, e o modulo NAO decide qual: FRUMENTO 12 (a etichetta escreve &ldquo;Grano tenero e duro&rdquo; — grano E frumento, mas o dicionario nao esta aqui), ZUCCHINO 5 (a etichetta escreve &ldquo;zucca&rdquo;, e zucca e zucchino sao duas culturas no registro italiano), FAGIOLO 4 (a etichetta escreve &ldquo;FAGIOLINO&rdquo;, e o diminutivo e outra entrada). Um quinto caso, CILIEGIO em `002983`/`013405`, nem chega aqui: `R-10` ja o retirou como `CROP_ONLY_INSIDE_EXCLUSION`. Duas regras feitas para perguntas diferentes acusaram o mesmo defeito por caminhos independentes |
| `R-22` | *A_DOSE_ROW_MUST_NOT_CROSS_A_DRAWN_RULE* (nome deste documento) — se dentro da banda `SOURCE_Y` de onde o extrator leu uma linha de dose existe um fio horizontal desenhado que cobre >= 60% da largura da propria linha, com texto acima **e** abaixo dele **e em cima do fio, em x**, entao aquilo nao e uma linha: sao duas, e a etichetta desenhou o risco entre elas. `DOSE_ROW_BAND_IS_ONE_DRAWN_ROW` (827), `DOSE_ROW_BAND_CROSSES_A_DRAWN_RULE` (10), `DOSE_ROW_BAND_NOT_CHECKED` (2) | nao resolve fusao de linha no caso geral — `FUSION_DETECTOR = NOT_IMPLEMENTED` continua valendo. Resolve o caso em que **o documento desenhou a separacao e o extrator passou por cima dela**. Sem vocabulario, sem heuristica de conteudo e sem numero novo | **esconde a dose**: 8 linhas de dose publicadas saem sem numero, com o nome do estado. E o unico dos seis que retira um numero da tela | `018270` p.4: a dose da linha do MAIS esta do outro lado de um risco desenhado em y 277,25. A primeira medicao, sem exigir texto dos dois lados, acusava 188, e as 159 de diferenca eram a PROPRIA BORDA da banda — borda de linha nao e separador de linha. A segunda, sem exigir sobreposicao em **x**, acusava 29, e 19 delas suprimiam dose correta: qualquer fio da folha tem texto acima e abaixo se so o y for olhado |

As tres colunas do selo `FATO` — `R-14` (o par sobrevive a geometria), `R-17`
(o nome do alvo esta no documento) e `R-21` (o nome da cultura esta no
documento) — dao hoje **1.324 fatos de 2.873 pares (46,1%)**, e as tres chegam
a esse numero sozinhas: `R-14` sozinha da os mesmos 1.324. As outras duas sao
guardas que ainda nao precisaram disparar, e ficam escritas justamente para que
o dia em que precisarem nao dependa de alguem lembrar.

`R-22` e hoje a regra mais conservadora do conjunto e isso esta medido: das 10
bandas que ela reprova, um arbitro independente verificou no papel que **8 sao
dose correta** — cultura, alvo e numero estao todos do mesmo lado do fio, e o
que ha do outro lado e fragmento da celula vizinha. A regra erra para o lado de
nao publicar, que e o lado que a lei zero prefere, mas quem le a tela tem
direito de saber que `DOSE_ROW_BAND_CROSSES_A_DRAWN_RULE` hoje significa, na
maioria dos casos, &ldquo;a nossa regra e severa demais aqui&rdquo;, e nao
&ldquo;a etichetta separou estas duas linhas&rdquo;.

`R-09` e a unica que exige nota permanente na tela: **vencer nao e ser revogado.**
A ferramenta mostra os dois campos e nao conclui saida de mercado.

## 4 · Regras de ruido (`N-*`) — o que NAO vira evento

| id | padrao | por que nao e mudanca |
|---|---|---|
| `N-01` | campo multivalorado com os mesmos itens em ordem diferente | serializacao da fonte, nao regulacao |
| `N-02` | diferenca so de espaco em branco | idem |
| `N-03` | valor que reaparece no mesmo registro/campo (A→B→A) | fonte oscilando entre publicacoes |
| `N-04` | mesmo documento recapturado com sha256 identico | uma captura nova nao e uma versao nova |
| `N-05` | parser diferente sobre o mesmo documento | mudanca de instrumento, nao de fato |

Medido no acervo: `N-01` sozinha responde por 496 das 528 diferencas brutas.

## 4b · Regras de plausibilidade de dose (`P-*`)

Estas regras nao dizem o que a etichetta autoriza. Elas dizem que **a nossa
leitura de uma linha nao parece uma leitura de linha de dose**, e por isso a
linha vai para revisao humana em vez de virar numero na tela. Sao HEURISTICA
nossa, escrita por nos, e a interface e obrigada a apresenta-las com grau de
evidencia menor que o fio desenhado da tabela — que e medida do documento.
A tela citava `P-01` a `P-05` e este documento nao as continha: uma regra citada
e nao escrita e uma regra que ninguem pode conferir.

| id | quando dispara | efeito |
|---|---|---|
| `P-01` | nenhuma linha da tabela candidata tem dose (nem por concentracao nem por hectare) | a "tabela" inteira e descartada: o extrator achou tabela onde havia prosa |
| `P-02` | o alvo comeca por marcador de lista ou simbolo (bullet, quadrado, traco) | fragmento de prosa, nao celula |
| `P-03` | linha sem dose, sem maximo e sem intervalo, num rotulo cujas outras linhas tem valor | a linha nao carrega nada que so uma linha de dose carregaria |
| `P-04` | cultura ou alvo com menos de 3 caracteres uteis | curto demais para ser identidade |
| `P-05` | cultura ou alvo comeca por palavra funcional italiana (`da`, `della`, `di`, `del`, `in`, `con`...) | a celula foi cortada no meio pelo extrator |

## 5 · Regras de janela temporal (`T-*`)

| id | condicao | janela | por que |
|---|---|---|---|
| `T-01` | validade ja passou e produto ainda listado ativo | `ACT_NOW` | ha um conflito declarado entre dois campos oficiais **hoje** |
| `T-02` | validade em ate 90 dias | `PREPARE` | prazo oficial proximo, com data na fonte |
| `T-03` | validade entre 91 e 180 dias | `MONITOR` | prazo oficial no horizonte |
| `T-04` | validade acima de 180 dias | `PLAN_NEXT_CYCLE` | ha data, sem urgencia |
| `T-05` | mudanca real detectada nos ultimos 30 dias de janela observada | `PREPARE` | o fato e novo para nos |
| `T-06` | qualquer outro caso | `NO_ACTION_YET` | nada na fonte pede tempo |
| `T-07` | dado em revisao | `UNKNOWN` | nao se atribui tempo a fato nao provado |
| `T-08` | `REVOCATION_ACT_CHANGE` | `ACT_NOW` | um **ato administrativo datado** sobre a validade do proprio registro (motivo, decreto ou decorrencia da revoga) e exatamente o que uma janela marca. `ACT_NOW` aqui significa **olhe hoje**; `EXPIRY != WITHDRAWAL` continua valendo e nenhuma `ACTION` nasce desta regra |
| `T-09` | `STATUS_CHANGE` cujo estado NOVO e um dos que a fonte declara fora de vigor (`Revocato`, `Scaduto`, `Sospeso` — medidos no instantaneo vigente: 13.216 / 765 / 3 dos 17.695 produtos) | `ACT_NOW` | o **estado** mudou, e so isso. Nem sempre ha ato datado por tras: em `014225` e `014227` (`Revocato -> Scaduto`) os tres campos de revoga sao `-` nos 60 instantaneos, e chamar isso de &ldquo;ato datado&rdquo;, como a redacao anterior de `T-08` fazia, era descrever um documento que a fonte nao traz. O que se afirma e a transicao de estado; a janela existe porque uma transicao para fora de vigor pede olhar hoje, nao porque haja decreto |

`ACT_NOW` aqui significa **"olhe hoje"**, nunca "pare de vender".

## 6 · Capacidades ADAMA e regras de roteamento (`C-*`)

Roteamento diz **quem pode precisar olhar**, nunca **o que fazer**.

| id | capacidade | recebe | estado | justificativa |
|---|---|---|---|---|
| `C-01` | `REGULATORY` | todo evento com `PROOF_STATE = PROVED` | `RELEVANT` | a mudanca e do registro oficial, que e o objeto de trabalho desta area |
| `C-02` | `REGULATORY` | todo item `NEEDS_REVIEW` | `RELEVANT` | so esta area pode adjudicar leitura de rotulo |
| `C-03` | `DEVELOPMENT_MARKET` | `CROP_USE_ADDED`, `TARGET_USE_ADDED` | `POTENTIALLY_RELEVANT` | uso novo pode abrir avaliacao; a ferramenta nao afirma oportunidade |
| `C-04` | `DEVELOPMENT_MARKET` | `CROP_USE_REMOVED`, `TARGET_USE_REMOVED`, `DOSE_CHANGE` | `POTENTIALLY_RELEVANT` | pode exigir reavaliacao de posicionamento |
| `C-05` | `COMMERCIAL_RTV` | qualquer evento | `NOT_RELEVANT` **por padrao** | o campo nao deve receber fato regulatorio bruto; so passa pelo portao `G-01` |
| `C-06` | `MARKETING_PRODUCT` | `CROP_USE_ADDED/REMOVED`, `TARGET_USE_ADDED/REMOVED`, `DOSE_CHANGE`, `RESTRICTION_CHANGE` | `POTENTIALLY_RELEVANT` | material publicado pode citar o uso que mudou; gera `CONTENT_REVIEW_CANDIDATE`, nunca "material errado" |
| `C-07` | `SUPPLY` | `EXPIRY_EVENT` | `POTENTIALLY_RELEVANT` | e uma data no horizonte, e so isso. `EXPIRY != WITHDRAWAL`: a regra nao autoriza derivar dela nenhum efeito comercial — nem sobre procura, nem sobre inventario, nem sobre venda |
| `C-10` | `SUPPLY` | `STATUS_CHANGE` | `POTENTIALLY_RELEVANT` | o estado administrativo do registro mudou. O fato e a mudanca de estado; a consequencia de abastecimento nao esta provada por ele |
| `C-11` | `SUPPLY` | `DATE_CHANGE` | `POTENTIALLY_RELEVANT` | a **data de validade declarada** (`data_scadenza_autorizzazione`) mudou entre dois instantaneos oficiais. E prazo oficial com data na fonte, e nada mais: prorrogar validade nao e efeito comercial, e encurtar tampouco. A redacao anterior dizia &ldquo;um campo de data que nao e a validade&rdquo; e estava simplesmente errada — os 27 objetos `DATE_CHANGE` deste acervo sao 27/27 do campo de validade |
| `C-12` | `SUPPLY` | `REVOCATION_ACT_CHANGE` | `POTENTIALLY_RELEVANT` | mudou um dado do ato de revoga (motivo, decreto, decorrencia). Isto e sobre o ATO, nao sobre a existencia do produto no mercado |
| `C-13` | `SUPPLY` | `PRODUCT_LEFT_ACTIVE_SET` | `POTENTIALLY_RELEVANT` | a registracao saiu do conjunto ativo do instantaneo. `CATALOG_PRESENCE != MARKET_PRESENCE`: sair do conjunto ativo prova uma coisa so, que a linha saiu daquele conjunto naquele instantaneo |
| `C-08` | `INTELLIGENCE` | todo evento provado | `RELEVANT` | a area cruza portfolio, cultura, alvo e tempo |
| `C-09` | `COUNTRY_PRODUCT_TEAM` | eventos do proprio pais | `POTENTIALLY_RELEVANT` | dono do portfolio local |
| `C-99` | qualquer | tipo de evento sem regra acima | `UNKNOWN` | nenhuma regra cobre; aparece como nao roteado |

Uma regra de roteamento so pode ser citada por um tipo de evento que ela
nomeia. `C-07` ja foi escrita para `EXPIRY_EVENT, STATUS_CHANGE` e usada por
cinco tipos: o cabecalho dizia "sao eventos com data" sobre uma saida do
conjunto ativo, que nao e uma data. Cinco tipos diferentes agora tem cinco
regras, cada uma com a sua propria justificativa, porque as razoes sao
diferentes — e porque juntar vencimento com saida do conjunto ativo debaixo de
uma frase so e exatamente a confusao que `EXPIRY != WITHDRAWAL` proibe.

## 7 · Portoes (`G-*`)

| id | portao | condicao para abrir |
|---|---|---|
| `G-01` | mensagem para o campo (RTV) | exige `PROOF_STATE = PROVED` **e** revisao humana registrada. A ferramenta nunca abre este portao sozinha; ela so cria `COMMERCIAL_MESSAGE_CANDIDATE` |
| `G-02` | `PHI_CHANGE` | so existe se o PHI estiver provado. Como `PHI_PROVED = 0`, nenhum `PHI_CHANGE` pode ser emitido nesta versao |
| `G-03` | implicacao de negocio | so com regra `B-*` propria. Nao existe nenhuma `B-*` nesta versao, entao `POTENTIAL_BUSINESS_IMPLICATION = NOT_PROVED` em todos os objetos |

## 8 · O que esta versao declaradamente NAO faz

- nao emite `ACTION`;
- nao emite `PHI_CHANGE` (portao `G-02` fechado por falta de prova);
- nao emite implicacao de negocio (portao `G-03`, sem regra `B-*`);
- nao envia nada ao campo (portao `G-01`);
- nao infere demanda, estoque, preco ou concorrencia a partir de rotulo;
- nao mede cobertura por **celula de cultura desenhada**: o vocabulario do leitor
  de uso e uma lista FECHADA de nomes (declarada na tela de COBERTURA), e nomes
  que a etichetta escreve e que ele nao tem — `PORRO`, `FINOCCHIO`, `LATTUGHE`,
  `SCAROLE`, `POMACEE`, `FRUMENTO` — nao viram par de uso. A tela responde
  `CROP_NOT_IN_USE_VOCABULARY` com as linhas de dose que existem, em vez de zero;
- **nao detecta fusao de linha** (`FUSION_DETECTOR = NOT_IMPLEMENTED`). `R-13`
  acusa o sintoma e `R-14` retira o par quando a geometria o contradiz, mas
  nenhum dos dois separa alvo quebrado entre colunas de alvo fundido.
