# CASOS ADVERSARIAIS DA ENTREGA — as cicatrizes

```
DOCUMENT_STATUS   DRAFT
DOCUMENT_TYPE     CORE CONSTITUTION · evidência das leis
MEASURED_AT       2026-09-08
IMPLEMENTATION    NONE
```

> Cada caso é um defeito **que aconteceu neste repositório**, com data, com prova, e com
> a lei que dele nasceu. Nenhum é hipotético.
>
> A coluna que mais importa é a última: **`GUARDA`**. Uma lei em prosa é uma lei que
> volta. Uma lei em portão é uma lei que reprova.

**Legenda de `GUARDA`:**
`EXECUTÁVEL` — existe teste/portão que reprova · `PROSA` — está escrito, ninguém verifica ·
`NÃO MEDIDO` — nem escrito nem verificado.

---

## FAMÍLIA A · `DATASET → TOOL` sem contrato

### AD-01 · O arquivo que existe porque se podia contar

```
ID              AD-01
DATE            ≤ 2026-09-06
WHAT HAPPENED   A voz «Archivio · Archive» entrou na barra com o contador 1114.
                Medido: 1114 é um ÍNDICE DERIVADO sobre as outras colecções — não
                traz facto próprio. O modelo sabe-o: provenanceTotals conta
                `indexRows: 1114` à parte de `real: 17089` e `derived: 288`.
                Não existe ficha, contrato ou decisão sobre um Arquivo em nenhum
                documento do repositório.
WHY IT WAS      Um índice não responde a nenhuma decisão. E a HOME proíbe pelo nome
WRONG           «contador de linhas» — a barra imprime um.
                E há um quarto acervo sem entrada de menu: `searchIndex`, 1655
                entradas em 17 famílias, que já indexa tudo o que os outros três
                dizem arquivar.
LAW LEARNED     L-01 · DATA EXISTS ≠ TOOL EXISTS
                L-06 · DATASET ≠ INTELLIGENCE PRODUCT
                AP-01 · DATASET BECOMES MENU
CURRENT GUARD   a proibição da home
EXECUTABLE?     NÃO — PROSA
```

### AD-02 · A ficha que dizia `CONCEPT` e a aba que apareceu

```
ID              AD-02
DATE            2026-08-28 (ficha) → ≤ 2026-09-06 (aba)
WHAT HAPPENED   A última ficha escrita de FIELD VOICES dizia
                `STATUS: CONCEPT — sem fonte de dado`, TECHNICAL_FEASIBILITY BAIXA,
                ADAMA_ALIGNMENT UNKNOWN. Chegaram 79 vozes ao pacote. A aba nasceu.
                NINGUÉM REABRIU A FICHA.
WHY IT WAS      A ordem SOURCE → EVIDENCE → DATA → CROSSING → CAPABILITY → TOOL →
WRONG           PORTAL foi percorrida ao contrário: o dado chegou e a tela seguiu-o.
                O README diz, na primeira página: «Nunca o contrário.»
LAW LEARNED     L-01 · DATA EXISTS ≠ TOOL EXISTS
                E a lei irmã, que é a mais difícil:
                **UMA RECUSA POR FALTA DE FONTE EXPIRA QUANDO A FONTE CHEGA — E
                EXPIRAR NÃO É PROMOVER.** A ficha tinha de reabrir para CANDIDATE,
                não para ACTIVE.
CURRENT GUARD   nenhuma
EXECUTABLE?     NÃO MEDIDO
NOTA            A arquitetura de produto nunca escreveu KILL: escreveu
                `NOT REACHED / NÃO SEI, não KILL` e «Apify não foi testado. É
                preciso testar antes de decidir». **A recusa era de fonte, não de
                ideia.** Ver MATRIZ §3.
```

### AD-03 · O contador que o contrato proíbe pelo nome

```
ID              AD-03
DATE            2026-08-30 (contrato) → ≤ 2026-09-06 (barra)
WHAT HAPPENED   `EAME-COMPETITOR-CONTRACT-V1.json` diz, textualmente: «não é um
                painel de concorrência, não é um ranking, não é um score de ameaça,
                não é uma ferramenta isolada. NÃO EXISTE TELA NEM NÚMERO ÚNICO
                SAINDO DAQUI.»
                A barra imprime **577**.
WHY IT WAS      577 é, literalmente, o número único que o contrato proíbe. E soma
WRONG           quatro naturezas que a arquitetura manda nunca somar: 414 anúncios
                pagos + 147 vídeos orgânicos + 16 notas.
LAW LEARNED     L-12 · CLICK ≠ VALUE, e a sua irmã: CONTADOR ≠ CLAIM
                AP-14 · COUNTER AS VALUE
                **O MENU NÃO É LUGAR DE CLAIM.** Um número ao lado de um nome é uma
                afirmação sobre uma população, e afirmações precisam de contrato.
CURRENT GUARD   `competitor-population.mjs` PASS (577 corpus · 569 no DOM) —
                verifica a ARITMÉTICA, não a LEGITIMIDADE do número
EXECUTABLE?     PARCIAL — o portão prova que 577 está certo, não que pode ser dito
```

---

## FAMÍLIA B · `CAPABILITY → MENU` sem decisão

### AD-04 · Nove superfícies sobre uma capacidade

```
ID              AD-04
DATE            2026-08-28 (atlas) → 2026-09-07 (portal)
WHAT HAPPENED   O `ATLAS-DE-CAPACIDADES-EAME.md` tem 22 capacidades COMPROVADO.
                Distribuição medida: EUROPE 11 · SPAIN 7 · FRANCE 3 · **ITALY 1**
                (CAP-007, calendário de vencimento).
                O portal é italiano e tem 12 superfícies.
WHY IT WAS      `Market Pulse` assenta em CAP-019, que cobre FRANCE e SPAIN.
WRONG           `Scientific Intelligence` assenta em CAP-017, que cobre FRANCE e
                SPAIN. Nenhuma das duas tem capacidade provada para o país que o
                portal serve.
LAW LEARNED     L-02 · CAPABILITY EXISTS ≠ TOOL APPROVED
                E: **PAÍS É DIMENSÃO, NÃO RODAPÉ.** Uma capacidade provada num país
                não é uma capacidade noutro — é a regra 5 do README, e foi violada
                por transporte de tela.
CURRENT GUARD   o atlas declara COUNTRY por capacidade
EXECUTABLE?     NÃO — PROSA. Nenhum portão liga superfície ↔ capacidade ↔ país
```

### AD-05 · A promoção que ninguém registou

```
ID              AD-05
DATE            entre 2026-09-06 e 2026-09-07
WHAT HAPPENED   `const STRUMENTI = ['meeting', 'portfolio']`.
                O Portfolio passou de item de evidência a ferramenta principal.
                Nenhum documento registou a decisão. O `DIARIO-DE-DECISOES.md`
                termina em D-026 (2026-08-30) e numa entrada de 2026-09-02.
WHY IT WAS      Nove mudanças de superfície em 48 horas, zero registos. **Nenhuma
WRONG           era ilegítima. As nove eram invisíveis.**
                Não é desleixo: é AUSÊNCIA DE LUGAR. O diário de decisões foi
                desenhado para decisões de método, não para «Portfolio subiu».
LAW LEARNED     §20 · o LIVING PRODUCT REGISTRY existe exatamente para isto
                AP-11 · SILENT OVERWRITE
CURRENT GUARD   nenhuma
EXECUTABLE?     NÃO MEDIDO
```

---

## FAMÍLIA C · `UI → JUDGMENT` sem dono

### AD-06 · A janela que se declarava aberta por aritmética

```
ID              AD-06
DATE            2026-09-02 (importação) → 2026-09-08 (medição)
WHAT HAPPENED   As 29 janelas colturais imprimem `CURRENT_STATUS`.
                Medido: `CURRENT_STATUS` é ARITMÉTICA PURA de datas contra
                2026-09-02 em **29/29**. `SOURCE_IDS` está vazio em **29/29**.
                `LAST_VALIDATED` tem UM ÚNICO VALOR (2026-09-02) em 29/29 — que é
                um carimbo de geração, não uma validação.
                O gerador, o insumo (`CANONICAL-CROP-WINDOWS-2026-09-02.json`) e o
                contrato que o ficheiro cita estão **AUSENTES DE 979 COMMITS DE
                TODOS OS REFS**.
WHY IT WAS      Um estado calculado na fronteira UI/modelo é um juízo produzido pelo
WRONG           casco. E um estado sem fonte é um estado que ninguém pode contestar.
LAW LEARNED     L-11 · UI ≠ INTELLIGENCE ENGINE
                F-07 · aritmética de datas não é frescor de evidência
                AP-04 · UI CALCULATES CLAIM
CURRENT GUARD   `CROP_WINDOWS_TRUSTED = NÃO` está declarado no checkpoint;
                5 janelas sem data mostram «DATA DA CONFERMARE» e nenhuma data foi
                inventada
EXECUTABLE?     PARCIAL — o estado está medido e publicado; nada impede a tela de o
                mostrar como facto
```

### AD-07 · Dois factos diferentes sob a mesma etiqueta

```
ID              AD-07
DATE            ≤ 2026-09-06, corrigido
WHAT HAPPENED   `casa.html` imprimia «DATA DI RIFERIMENTO 2026-09-04» e
                `portale.html` «OGGI · 02 SET».
                Não era contradição: 2026-09-02 é a data de referência do pacote
                V2.1 e 2026-09-04 é o CORTE da istantanea
                (MEETING_CUTOFF = 2026-09-04T00:52:54Z).
WHY IT WAS      «Eram dois factos sob a mesma etiqueta, e era a etiqueta que
WRONG           mentia.»
LAW LEARNED     L-13 · UPDATED_AT ≠ EVIDENCE_FRESHNESS
                F-01 · FRESHNESS_COMPONENTS é uma LISTA
                AP-10 · ONE UPDATED_AT FOR EVERYTHING
CURRENT GUARD   as duas telas dizem agora «TAGLIO DELL'ISTANTANEA» / «SNAPSHOT
                CUTOFF», a mesma palavra do radar (`meeting-labels lblCutoff`)
EXECUTABLE?     PARCIAL — `casa-gate.mjs` 30/30 cobre a casa
NOTA            A frase que ficou: **«DUE FATTI DIVERSI SOTTO LO STESSO NOME NON
                SONO UN DETTAGLIO. SONO UNA DOMANDA CHE IL LETTORE NON DOVREBBE
                DOVER FARE.»**
```

### AD-08 · «Validato» afirmava um ato que ninguém pode mostrar

```
ID              AD-08
DATE            2026-09-08 (commit ad491c8)
WHAT HAPPENED   29 janelas imprimiam a palavra «Validato». Ninguém as validou:
                `LAST_VALIDATED` é o carimbo de geração.
WHY IT WAS      Uma palavra de interface afirmou um ATO — a validação — que não
WRONG           tinha autor, data nem evidência.
LAW LEARNED     **O TESTE DA DERIVA SEMÂNTICA:** um leitor que só viu a frase de
                exibição chegaria a uma conclusão que o campo não autoriza?
                Aqui: sim.
                E: `DISPLAY-LAYER-V1` §A_REGRA_QUE_GOVERNA_TUDO — «uma frase de
                exibição só pode ser MAIS explícita que o enum, nunca mais
                conclusiva».
CURRENT GUARD   corrigido para «Dati al» / «Data as of».
                `DISPLAY-LAYER-V1.json` declara `SEMANTIC_DRIFT_ERRORS = 0` sobre
                103 regras
EXECUTABLE?     PARCIAL — as 103 regras foram lidas uma a uma, à mão. **A leitura
                foi humana; o zero não é derivado.**
```

---

## FAMÍLIA D · `DEMO → CURRENT`

### AD-09 · A pastilha verde que prometia uma oportunidade inexistente

```
ID              AD-09
DATE            2026-09-08 (commit 6f79552)
WHAT HAPPENED   Seis pastilhas prometiam OPPORTUNITY a partir da janela colturale.
                As seis caíam em «CASO NON TROVATO»: `LEGACY_CASE_ID` está
                preenchido em 29/29 e resolve **0/29**.
WHY IT WAS      Uma promessa de navegação é uma afirmação de existência.
WRONG
LAW LEARNED     `WINDOW_OPEN ≠ CURRENT_NEED` (CONTRATO-DE-DESIGN §2.1)
                E: **UM LINK É UM CLAIM.** Se ele diz que existe um caso, tem de
                existir um caso.
CURRENT GUARD   6 promessas falsas → 0
EXECUTABLE?     SIM — `cta-navigation.mjs`
```

### AD-10 · O contra-exemplo positivo — Field Sales Channel

```
ID              AD-10
DATE            corrente
WHAT HAPPENED   18 mensagens fabricadas, 7 representantes inventados, 3 sugestões
                de texto com nomes de cidades e concorrentes nunca observados.
                **E nada disto engana ninguém.**
WHY IT WAS      NÃO FOI ERRADO. É o contra-exemplo.
NOT WRONG       Quatro camadas de honestidade, medidas:
                1. rótulo «INTEGRAZIONI · DEMO» no ecrã
                2. grupo de menu separado
                3. cor distinta (âmbar #F5B317, não o verde corporativo)
                4. `provenance = SYNTHETIC_DEMO` no modelo, contado à parte
                   (`provenanceTotals.demo = 103`)
LAW LEARNED     L-15 · DEMO ≠ PRODUCT
                **UMA DEMONSTRAÇÃO ROTULADA NÃO É UMA MENTIRA. É UMA MAQUETE.**
                O que a torna maquete é o rótulo estar em QUATRO camadas, incluindo
                o dado — não só na tela.
CURRENT GUARD   `censo-demo.mjs` · `demo-visibile.mjs` · `PRECEDENCE` no modelo
EXECUTABLE?     SIM
```

---

## FAMÍLIA E · `SUPPORTING ENGINE → TOOL`

### AD-11 · Seis motores de suporte na barra

```
ID              AD-11
DATE            2026-08-29 (contrato) → 2026-09-07 (barra)
WHAT HAPPENED   `ARQUITETURA-DE-PRODUTO-ATUAL` lista o SUPPORTING ENGINE — «por
                baixo, NÃO NO MENU»: science · experts · climate context · entity
                identity · market/crop context · data clock · change events ·
                normalizações · camada de evidência e proveniência.
                Na barra de 07/09 estão: Scientific Intelligence, Market Pulse,
                Source Register, Portfolio (entity identity), Crop Windows e
                Competitor Watch.
WHY IT WAS      **E AQUI ESTÁ A PARTE DIFÍCIL: NÃO FOI TODO ERRADO.**
PARTLY WRONG    O erro do contrato antigo foi usar `IS_INPUT_TO_ANOTHER_TOOL` como
                critério de classificação. Não é um critério.
                O critério é `HAS_OWN_DECISION_QUESTION`.
                Label Intelligence prova-o: alimenta o Radar, o Portfolio e o Ask —
                E tem pergunta, público, evidência e claim proibido próprios.
LAW LEARNED     PG-08 · **UMA INTELIGÊNCIA ALIMENTA MUITAS FERRAMENTAS, E ISSO NÃO
                A REBAIXA.** A cardinalidade M:N é constitucional; ser input é
                ortogonal a ser ferramenta.
                §10 · SURFACE CLASS existe porque este eixo estava em falta
CURRENT GUARD   nenhuma
EXECUTABLE?     NÃO MEDIDO
NOTA            Este caso é a razão pela qual a Bíblia recusa aplicar a arquitetura
                antiga como veredito. **Três das cinco recusas têm de ser
                reabertas.** Ver MATRIZ §3.
```

---

## FAMÍLIA F · mesma população, duas superfícies

### AD-12 · Dois radares dos mesmos 43

```
ID              AD-12
DATE            ≤ 2026-09-06, corrigido
WHAT HAPPENED   Duas vozes de menu: o radar histórico, servido pelo pacote ANTES da
                reconciliação, e o «Radar Canónico», servido pela istantanea.
                A primeira trazia uma linha de desculpas a remeter para a segunda.
WHY IT WAS      **«DUE RADAR DEGLI STESSI 43 SONO UN RADAR CHE NON CI SI FIDA.»**
WRONG
LAW LEARNED     PG-02 · uma ferramenta é uma DECISION QUESTION, não um dataset.
                Duas superfícies com a mesma pergunta são uma ferramenta com duas
                vistas — ou uma que ninguém confia.
                §9 · MERGED preserva histórico: a grelha histórica **não foi
                apagada**; deixou de ser renderizada (`isRadar = false`)
CURRENT GUARD   `isRadar` fixo em `false`; o contador vem da istantanea
EXECUTABLE?     SIM
```

### AD-13 · Duas portas, duas listas, o mesmo cartão

```
ID              AD-13
DATE            2026-09-06 (medido)
WHAT HAPPENED   Para o MESMO cartão de oportunidade:
                  casa.html    → PORTFOLIO_MATCHES        65 lugares de produto
                  portale.html → PRODUCT_RELATIONSHIPS   280 lugares
                Os 43 cartões DIVERGEM entre as duas portas.
WHY IT WAS      Duas superfícies que respondem à mesma pergunta com listas
WRONG           diferentes criam duas verdades sobre o mesmo objeto — e o
                utilizador não tem como saber qual abriu.
LAW LEARNED     C-03 · `CONFLICT_STATE` é obrigatório no Product Contract
                AP-02 · SCREEN BECOMES OWNER
CURRENT GUARD   nenhuma. Foi MEDIDO e DECLARADO, não resolvido
EXECUTABLE?     NÃO
```

### AD-14 · Três palavras «arquivo», quatro acervos

```
ID              AD-14
DATE            ≤ 2026-09-06
WHAT HAPPENED   Três itens de menu com a palavra «Archivio», sem relação entre si:
                  Archivio segnali V21    3     sinais — não é um arquivo
                  Archivio             1114     índice derivado
                  Archivio fonti V21    189     registo de fontes
                E um quarto, sem menu: `searchIndex`, 1655 entradas, 17 famílias.
WHY IT WAS      O nome descrevia o formato, não a pergunta. Três populações sem
WRONG           relação sob a mesma palavra.
LAW LEARNED     **UM NOME DESCREVE UMA POPULAÇÃO, E O PORTÃO PROVA-O.**
                Regra já aplicada uma vez, e bem: «NON "Radar Futuro": quel nome è
                dei 44 ITFC di questa pagina. La vista del portale porta 3 segnali
                IT-FUT- a monte — un altro insieme.»
CURRENT GUARD   renomeações: «Archivio segnali» · «Registro delle fonti»;
                e a pastilha que liga as duas populações
EXECUTABLE?     PARCIAL
```

---

## FAMÍLIA G · rótulo de ecrã afirma mais do que a evidência

### AD-15 · «OPPORTUNITÀ» e «SALES READY»

```
ID              AD-15
DATE            ≤ 2026-09-06
WHAT HAPPENED   §MT2 manda dizer `PRIORITY TO INVESTIGATE` e proíbe
                `SALES OPPORTUNITY`, com a palavra «nunca».
                O ecrã chama-se «OPPORTUNITÀ» e um dos estados impressos era
                `PRONTO PER LA VENDITA` / `SALES READY` — medido em 5 dos 13
                cartões.
WHY IT WAS      O nome do ecrã é o claim mais lido de todos. Um contrato que proíbe
WRONG           uma palavra e uma tela que a usa como título anulam-se.
LAW LEARNED     C-01 · `FORBIDDEN_CLAIMS` não pode estar vazio — e tem de valer
                para o NOME DA SUPERFÍCIE, não só para o conteúdo
CURRENT GUARD   `adama-relevance-gate` 7/7 verifica a classificação, não o rótulo
EXECUTABLE?     PARCIAL
```

### AD-16 · O selo ATTIVO sem a data que o prova

```
ID              AD-16
DATE            2026-09-08 (medido)
WHAT HAPPENED   27 anúncios exibem o selo ATTIVO. `ACTIVE_ADS_PROVED` no pacote = 0.
                O acervo tem `last_observed` e `first_observed` em **414/414**.
                O pacote não os pede.
WHY IT WAS      «O selo ATTIVO afirma o presente sem a data que o prova.»
WRONG           Um estado presente é uma afirmação temporal, e afirmações
                temporais precisam de relógio.
LAW LEARNED     F-04 · um selo de estado presente exige a data que o prova
                E a regra que FOI respeitada: **histórico nunca foi promovido a
                ativo** — 385 históricos e 192 UNKNOWN ficaram separados
CURRENT GUARD   as três contagens são publicadas separadas
EXECUTABLE?     PARCIAL — o número é honesto, o selo não
```

### AD-17 · O termo da busca lido como o achado

```
ID              AD-17
DATE            2026-09-08 (medido)
WHAT HAPPENED   Os 88 papers de ciência têm CROP e ISSUE. Medido: são o TERMO DA
                BUSCA, não o que o texto prova.
                  87/88 batem QUERY_*
                  37/88 e 34/88 batem PROVED_*
                  **39/88 são OFF_CASE**
WHY IT WAS      Um sistema que pesquisa «repilo» e devolve «repilo» não descobriu
WRONG           repilo: devolveu a pergunta. Apresentar isso como cobertura
                científica de um par é circular.
LAW LEARNED     PG-13 · **O TERMO DA BUSCA NÃO É O ACHADO**
                AP-17 · SEARCH TERM READ AS FINDING
                Parente medido do mesmo defeito: «O CORPUS É AMOSTRA DAS NOSSAS
                CONSULTAS» — o herbicida «caiu» de 1º para 3º porque *nós* abrimos
                outros recortes
CURRENT GUARD   está medido e declarado como INTEGRATION_DEPENDENCY nº 5
EXECUTABLE?     MEDIDO, NÃO TRAVADO
```

---

## FAMÍLIA H · ausência lida como conclusão

### AD-18 · «0 de 163» é afirmável; «não achámos em 102 de 163» não é

```
ID              AD-18
DATE            2026-09-02
WHAT HAPPENED   A leitura dos 163 rótulos autorizados levou a cobertura de uso de
                11,7% para 62,6%. No caminho, uma lei: **CENSO E AMOSTRA NÃO SÃO A
                MESMA AUSÊNCIA.**
WHY IT MATTERS  «0 de 163» é um censo — uma afirmação sobre o universo inteiro.
                «Não achámos em 102 de 163» é uma amostra — uma afirmação sobre o
                nosso esforço.
LAW LEARNED     L-17 · ABSENCE IN THIS READING ≠ ABSENCE IN THE WORLD
                AP-16 · ABSENCE READ AS CONCLUSION
                E os cinco estados que nunca se colapsam:
                `NÃO SEI` · `NOT_COLLECTED` · `NOT_KNOWN` · `AUSENTE_MEDIDO` ·
                `NAO_TESTADO`
CURRENT GUARD   `AM.ABSENCE_RULE` no modelo · `NOT_KNOWN_STATES` no
                `DESIGN-DATA-CONTRACT-V1`, que nomeia
                «O_PIOR_ERRO_POSSIVEL: colapsar AUSENTE_MEDIDO com NAO_TESTADO»
EXECUTABLE?     PARCIAL
```

### AD-19 · Uma afirmação global feita a partir de um snapshot

```
ID              AD-19
DATE            2026-08-30 · D-026 (REVOGA a redação da rodada 1)
WHAT HAPPENED   A rodada 1 escreveu que META e CREATOR «não existem no
                repositório». Estava errado, e do jeito mais caro: era uma
                afirmação GLOBAL feita a partir de um SNAPSHOT.
                Medido: o Creator Map estava congelado com handoff canónico noutra
                branch, e a missão Meta corria em paralelo com 1.111 anúncios.
WHY IT WAS      «Uma branch só pode declarar o que ELA juntou.»
WRONG
LAW LEARNED     Vocabulário obrigatório:
                `<CAMADA>_DATA_AVAILABLE_IN_THIS_SNAPSHOT = NO`
                + `ESTADO = NOT_JOINED_IN_THIS_MISSION`
                + o lugar onde a outra missão vive
                **E É EXATAMENTE O DEFEITO QUE ESTA PESQUISA QUASE COMETEU:**
                `grep "Label Intelligence" portale.html` = 0 nesta branch. Concluir
                «não existe» teria sido AD-19 outra vez. Existia — noutra linhagem.
CURRENT GUARD   um teste proíbe que a frase de ausência global volte
EXECUTABLE?     SIM
```

---

## FAMÍLIA I · o pacote perde o acervo

### AD-20 · Cinco milhões de caracteres que chegam e morrem

```
ID              AD-20
DATE            2026-09-08 (medido)
WHAT HAPPENED   ACERVO      143 transcrições úteis · 5.033.374 caracteres de fala
                PACOTE      0 campos de transcrição em 32 ficheiros
                MOTOR       0 — a palavra `transcript` aparece 2× em
                            italy-app-model.js, ambas em prosa
                PORTAL      147 cartões de vídeo · 0 renderizam título, canal ou
                            data
                EVIDÊNCIA   0 das 43 oportunidades cita voz, canal ou vídeo
                E, em paralelo: ciência 763 → 88, com 93.933 ch de abstract → 0.
WHY IT WAS      «PRINCIPAL_LOSS_POINT: O ACERVO NÃO ATRAVESSA A INGESTÃO.»
WRONG           **Não é o transporte pacote→portal: esse não perde nada (0 de
                6.895 IDs).** É a fronteira ACERVO→PACOTE.
LAW LEARNED     PG-14 · **VALUE_EXISTS = YES e VISIBLE = NO significa NÃO ESTÁ
                INTEGRADO.** Não «quase».
                AP-19 · VALUE EXISTS AND VISIBLE = NO
                E a escada que nenhum degrau implica o seguinte:
                VIDEO_EXISTS ≠ TRANSCRIPT_EXISTS ≠ TRANSCRIPT_USABLE ≠
                TRANSCRIPT_USED_AS_EVIDENCE
CURRENT GUARD   `cadeia-de-familias.mjs` mede 26 famílias em 4 fronteiras;
                `superficie-visivel.mjs` mede IN_MODEL / VISIBLE / REACHABLE e
                **reproduz o defeito antes de o declarar corrigido**
EXECUTABLE?     SIM — e é o melhor portão do repositório
NOTA            «A régua reproduz o defeito antes de o declarar corrigido. Uma que
                só soubesse passar não teria provado nada.»
```

### AD-21 · O funil sem contador

```
ID              AD-21
DATE            2026-09-06 (medido)
WHAT HAPPENED   Chegou um relato: uma oportunidade de VITE DA VINO mostrava UM
                único produto ADAMA, havendo vários. O relato estava certo e a
                causa não era a que ele sugeria. Medido, cinco reduções em série:
                  2154  produtos ADAMA para as culturas dos 43 cartões
                   768  os que o rótulo ministerial nomeia
                   721  os que sobram depois do portão CLIENT_SAFE      −47
                   361  os que o ARQUÉTIPO escolhe olhar
                   280  os que sobrevivem ao corte produtos[:12]        −81
                    65  os que casam com o catálogo por nº de registo  −215
                **Nenhuma redução era visível de dentro da seguinte.**
WHY IT WAS      «UM PRODUTO NO ECRÃ NÃO É UMA ESCOLHA PRECOCE: É UM FUNIL SEM
WRONG           CONTADOR. O que faltava não era procurar mais — era dizer, em cada
                degrau, quantos ficaram para trás e porquê.»
LAW LEARNED     PG-12 · o funil precisa de um contador em cada degrau
                §6 · `DROPPED_FIELDS` é OBRIGATÓRIO na ficha de uma projeção
                §14 · `WHY_EXCLUDED` é OBRIGATÓRIO no manifesto
CURRENT GUARD   611 justificações de exclusão publicadas, uma por produto ausente;
                `reconciliacao-do-catalogo.mjs` reconstrói 711 = 275 + 436
EXECUTABLE?     SIM
```

---

## FAMÍLIA J · a rota e o menu discordam

### AD-22 · 44 fichas desenhadas e nenhuma porta

```
ID              AD-22
DATE            até 2026-09-07, corrigido
WHAT HAPPENED   `ROUTES_TO_FUTURE_RADAR = 0`, confirmado por três causas
                independentes, todas medidas:
                  1. `navDef` não tinha entrada para o Radar Futuro
                  2. `navCasa` — a única referência a casa.html no portal inteiro —
                     era CÓDIGO MORTO: declarada, consumida em lugar nenhum
                  3. `AMMESSE` não tinha a rota; `isRadar` fixo em `false`
                Entretanto `casa.html` desenhava 44 fichas.
WHY IT WAS      «UNA VOCE DI MENU CHE NESSUN ELENCO CONSUMA NON È UNA ROTTA.
WRONG           È UNA PROMESSA SCRITTA E MAI MANTENUTA.»
LAW LEARNED     PG-11 · `SURFACE_EXISTS`, `SURFACE_ROUTABLE`, `SURFACE_LISTED` e
                `SURFACE_REACHABLE` são QUATRO ESTADOS INDEPENDENTES
CURRENT GUARD   `superficie-visivel.mjs`, com controlo negativo sobre `5a5ab60`
EXECUTABLE?     SIM
```

### AD-23 · O defeito simétrico — voz de menu sem rota estável

```
ID              AD-23
DATE            2026-09-08 (medido, NÃO corrigido)
WHAT HAPPENED   `AMMESSE` não inclui `field`. O comentário do código declara a
                intenção: «una schermata che nessuna voce di menu offre, ma che un
                indirizzo apriva, è una porta di servizio aperta».
                **Mas a voz de menu continua a ser desenhada** em
                `navIntegrationItems`. Consequência: abre por clique; um refresh em
                `#field` cai em `#meeting`.
WHY IT IS       É AD-22 ao contrário. A intenção e o código discordam.
WRONG
LAW LEARNED     AP-18 · MENU ENTRY WITHOUT ROUTE
CURRENT GUARD   nenhuma
EXECUTABLE?     NÃO — **DIVERGÊNCIA ABERTA**
```

---

## FAMÍLIA K · manual vira segunda verdade

### AD-24 · O inventário digitado de uma população que muda

```
ID              AD-24
DATE            2026-08-29 · D-013
WHAT HAPPENED   `POLITICA-RAW-ROTA-PAGA.json` era uma LISTA DIGITADA do diretório
                `raw-paid/`. Entrou um bruto novo; o DATA CLOCK (derivado) apanhou-o,
                a política (digitada) não. Ficou a publicar 10 arquivos e 2.121.837
                bytes onde havia 11 e 2.182.917 — internamente consistente e falsa.
                **Nenhum teste lia a política.**
                No mesmo movimento: o handoff publicava 26 fichas com o dono a
                derivar 25; a porta canónica carregava 486/1.004/36/61/34 sem
                marcador; e o rótulo do benchmark do Ask dizia «20 perguntas» com 35
                no ficheiro.
WHY IT WAS      «Um inventário digitado de uma população que muda envelhece em
WRONG           silêncio, e soma consistente consigo mesma dá aparência de
                correção. LISTA COERENTE ≠ LISTA COMPLETA.»
LAW LEARNED     M-02 · o manifesto é DERIVADO da build, nunca digitado
                D-009 · todo total publicado tem de ter prova que o derive da coisa
                contada
CURRENT GUARD   `scripts/proveniencia.py` é dono do diretório; marcadores `<!--M:-->`
                ligados ao ledger; a suíte foi de 280 para 295 provas
EXECUTABLE?     SIM — **e a primeira coisa que as provas novas apanharam foi a
                própria deriva que elas introduziram**
```

### AD-25 · O ficheiro que mente sobre a sua safra

```
ID              AD-25
DATE            2026-09-08 (declarado, não resolvido)
WHAT HAPPENED   `build/SINTONIA-ITALY-REALITY-HANDOFF-V2.1.zip` carrega
                `V21-99226fbb90dcdbc2` e 37 casos. O pacote corrente é outro.
                Medido: não é entrada da cadeia e nenhum consumidor o lê.
WHY IT IS       «Actualizá-lo custa 2 MB permanentes; deixá-lo mantém no
DECLARED        repositório um pacote que mente sobre a sua safra.
                DECISÃO DO DONO DO REPOSITÓRIO.»
LAW LEARNED     §14 · sem PUBLICATION MANIFEST, um artefacto sem consumidor é
                indistinguível de um artefacto abandonado
                AP-12 · MANUAL BUILD WITHOUT MANIFEST
CURRENT GUARD   declarado em «O QUE FICA EM ABERTO»
EXECUTABLE?     NÃO — e a declaração honesta é o guarda provisório
```

---

## FAMÍLIA L · legado apresentado como corrente

### AD-26 · Quatro superfícies legadas atrás da barra

```
ID              AD-26
DATE            corrente
WHAT HAPPENED   Nenhum item da barra é legado. O legado está ATRÁS dela:
                  vista `case`   renderiza; lê `D.CASES` = 29 casos DEMO_SCENARIO
                  vista `brief`  renderiza; é onde vive o único [data-download-pdf]
                  `radar`/`mradar`  aliases ainda aceites
                  ponte: `legacyCaseId` é null em **43 de 43** casos do motor
WHY IT IS       Nenhuma oportunidade real chega às vistas legadas. Elas renderizam
WRONG           e estão vazias de real.
LAW LEARNED     §9 · `RETIRED` não apaga — mas tem de estar REGISTADO como retirado.
                Uma vista que renderiza sem estar no registo é um estado que
                ninguém declarou.
CURRENT GUARD   `isRadar = false`; os ids continuam aceites
EXECUTABLE?     PARCIAL
```

---

## FAMÍLIA M · o portão que nunca reprovou

### AD-27 · Uma página que nenhuma rota alcança é uma página que nenhum portão lê

```
ID              AD-27
DATE            2026-09-07
WHAT HAPPENED   Ligar `casa.html` a partir do portal fez o portão `brandwell.mjs`
                LER ESSA PÁGINA PELA PRIMEIRA VEZ. Reprovou de imediato:
                `BW3 · No headline (>=16px) in ALL CAPS → 1`
                (25px, «AZOXYSTROBIN + PROTHIOCONAZOLE»)
WHY IT MATTERS  «O defeito é anterior a esta missão. O que era novo era a
                possibilidade de o ver.»
LAW LEARNED     PG-15 · **UMA PÁGINA QUE NENHUMA ROTA ALCANÇA É UMA PÁGINA QUE
                NENHUM PORTÃO LÊ.**
                Corolário para a Bíblia: a COBERTURA DE PORTÃO é função da
                ALCANÇABILIDADE. Um portão que só corre onde já se passa não mede
                o produto: mede o caminho batido.
CURRENT GUARD   `brandwell.mjs` 5/5, agora incluindo `casa.html`
EXECUTABLE?     SIM
```

### AD-28 · O portão que usava como porta um campo que o contrato diz não ser porta

```
ID              AD-28
DATE            2026-09-08 (commit 40bae7b)
WHAT HAPPENED   O check `O1` usava como portão de visibilidade um campo que o
                contrato declara EXPLICITAMENTE não ser porta de visibilidade.
                Resultado: 2 «NÃO MENSURÁVEL».
WHY IT WAS      Um portão que lê o campo errado não mede nada — e o «não
WRONG           mensurável» esconde-o.
LAW LEARNED     **UM PORTÃO QUE NÃO REPROVA NUNCA NÃO É UM PORTÃO.**
                Parente direto de D-014: «uma reconciliação que nunca reprova prova
                tão pouco quanto um DUPLICATE_COUNT = 0»
CURRENT GUARD   corrigido: 2 N/M → 0 N/M, 71/71
EXECUTABLE?     SIM
```

---

## PLACAR DAS CICATRIZES

```
CASOS REGISTADOS ................................... 28
FAMÍLIAS ........................................... 13   (A … M)

POR ESTADO DA GUARDA
  EXECUTÁVEL ....................................... 9    AD-09 · AD-10 · AD-12 ·
                                                          AD-19 · AD-20 · AD-21 ·
                                                          AD-22 · AD-24 · AD-27 · AD-28
  PARCIAL .......................................... 9    AD-03 · AD-06 · AD-07 ·
                                                          AD-08 · AD-14 · AD-15 ·
                                                          AD-16 · AD-18 · AD-26
  PROSA ............................................ 3    AD-01 · AD-04 · AD-25
  NÃO MEDIDO / ABERTO .............................. 7    AD-02 · AD-05 · AD-11 ·
                                                          AD-13 · AD-17 · AD-23 · (AD-25)

CASOS QUE SÃO CONTRA-EXEMPLOS POSITIVOS ............ 2    AD-10 (Field Sales) ·
                                                          AD-12 (a correção do radar)
CASOS AINDA ABERTOS HOJE ........................... 5    AD-13 · AD-17 · AD-23 ·
                                                          AD-25 · AD-05
```

### As quatro frases que este ficheiro quer dizer

**Primeira.** Nove das 28 cicatrizes têm portão executável. **É muito, para um
repositório desta idade** — e é o resultado de uma disciplina que já existia antes desta
Bíblia. `superficie-visivel.mjs` reproduz o defeito antes de o declarar corrigido;
`etichette-gate.mjs` recalcula um sha; `proveniencia.py` apanhou a própria deriva que
introduziu.

**Segunda.** Sete estão `NÃO MEDIDO`, e **cinco continuam abertas hoje**. As duas mais
caras são AD-13 (duas portas, duas listas, o mesmo cartão) e AD-05 (nove decisões de
produto sem registo).

**Terceira.** Duas cicatrizes são positivas. Field Sales Channel é uma demonstração
rotulada em quatro camadas e não engana ninguém. A fusão dos dois radares preservou o
código e apagou só a renderização. **O repositório já sabe fazer isto bem; o que lhe falta
é o lugar onde registar que o fez.**

**Quarta, e a mais desconfortável.** AD-19 quase se repetiu **nesta pesquisa**. O
comando `grep "Label Intelligence" portale.html` devolveu 0 nesta branch, e concluir «não
existe» teria sido uma afirmação global a partir de um snapshot. Existia — noutra
linhagem, com selo criptográfico e 22 regras versionadas.

> **A lei que este ficheiro compra com o seu próprio quase-erro:**
> **`NÃO ENCONTRADO NESTA BRANCH ≠ NÃO EXISTE NO PRODUTO`.**
