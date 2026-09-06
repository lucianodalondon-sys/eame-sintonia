# SINTONIA — LABEL INTELLIGENCE V1 · ENTREGA

Ferramenta paralela, standalone, para a equipa ADAMA Italia. Nao integra com o
portal, nao escreve em `sintonia/canonical`, nao faz deploy.

---

## A · HEAD / BRANCH

    BRANCH        claude/label-intelligence-v1-italy
    PILOT_HEAD    df3a4fd0029e74d16f171e5070b13ec4f3345d64   (base, missao 1)
    BUILD_HEAD    b371b74ec5238d94c01d5518afe2cad233593ad0
                  o commit cujo build foi medido para escrever este documento.
                  O commit que ATUALIZA este documento vem depois dele, e por
                  isso nao pode citar o proprio hash.
    COMMITS       24 desde PILOT_HEAD ate BUILD_HEAD
    RULESET       v1/inteligencia/REGRAS.md@5

    CANONICAL_TOUCHED = NAO
      medido com git, nao com uma constante: nenhum dos 19 commits desta missao
      esta em sintonia/canonical. Canonical avancou de bdb57cf para 10af4a7
      durante esta missao, com tres commits que NAO sao meus — outra sessao
      trabalhou nela. O portao antigo fixava o head numa constante e teria
      transformado o trabalho legitimo de outra pessoa num alarme desta missao.

    REUSO ANCORADO NO ARQUIVO, NAO NO BRANCH
      A lista de pares vinha de sintonia/canonical e ESTA SESSAO NAO TEM ACESSO
      a esse repositorio. Sem ela, exclusao.py e payload.py nao rodam, e um
      conserto que ninguem consegue reconstruir nao e um conserto.
      v1/fonte/pares_reconstruir.py remonta os 2.928 pares a partir de dois
      artefatos versionados que sao, os dois, derivados do original — o
      VERDICT_KEY_TRIPLE de EXCLUSAO.json e os `uses` de CASCO-PAYLOAD.json —
      e PARA se alguma posicao nao bater. Nada foi criado, removido ou
      reordenado.

      IT-ROTULOS-PARES-RECONSTRUIDO.json  2.928 pares
      conferido a cada build; se mudar, o payload aborta.

      A PROVA nao e do reconstrutor (v1/fonte/pares_conferir.py):
        R-10 devolve os 2.928 vereditos IDENTICOS
        payload.py devolve os 2.926 pares publicados IDENTICOS nos 9 campos
        e o HTML remontado por este caminho tinha sha256 7e4ea2a7b445fafa...,
        o MESMO alvo que o arbitro da rodada 3 julgou.

      CROP_Y e TARGET_Y nao sobreviveram ao payload e saem NOT_PRESERVED com o
      nome proprio. Quem precisa deles os remede no PDF — e e o que R-14 faz.

    FONTE PRIMARIA RECOLETAVEL
      v1/fonte/recoletar.py + MANIFESTO-FONTE.json trazem os 60 CSV e os 163 PDF
      do Ministero e conferem cada sha256. Medido nesta sessao:
      223 conferidos, 0 com sha errado.

    OFFICIAL_PORTAL_TOUCHED = NAO      DEPLOY = NENHUM

---

## B · ARQUITETURA — COLETA → INTELIGENCIA → CASCO

    COLETA          v1/coleta/       o que a fonte oficial diz, com proveniencia
      empacotar.py    163 produtos ADAMA ativos, 7 coberturas separadas
      exclusao.py     R-10, reconcilia cada par de uso contra o PDF oficial

    INTELIGENCIA    v1/inteligencia/ o que as regras escritas derivam do fato
      REGRAS.md       42 regras: R-01..R-13, N-01..N-05, T-01..T-09,
                      C-01..C-13/C-99, G-01..G-03, P-01..P-05
      objetos.py      210 intelligence objects, cada um com a regra que o autoriza
      dose_plausibilidade.py  P-01..P-05
      cultura_validar.py      R-11
      teto_dose.py            R-12
      alvo_literal.py         R-13

    CASCO           v1/casco/        so mostra; nunca abre PDF nem CSV
      payload.py      monta o JSON unico
      app.js          10 telas, nenhuma afirmacao sem caminho de volta
      label-intelligence.html   2,4 MB, um arquivo, abre sem servidor

O casco nao interpreta documento. Se um campo nao existe na fonte, ele viaja
como token de ignorancia ate a tela — a interface nao tem permissao de inventar
o que a coleta nao trouxe.

---

## C · O QUE A FERRAMENTA MONITORA

    FONTE       Ministero della Salute (Italia), Banca dati prodotti fitosanitari
                dati.salute.gov.it — PROD_FTS_6 (CSV semanal, licenca IODL 2.0)
                fitosanitari.salute.gov.it — EtichettaServlet (PDF por registro)

    ESCOPO      163 produtos ADAMA no conjunto ativo do instantaneo vigente
                (de 17.695 produtos do registro inteiro)
    HISTORIA    60 instantaneos semanais, 54 documentos distintos por sha256
                janela 2025-07-14 .. 2026-08-31 (14 meses)
    ROTULOS     163 PDFs baixados e preservados, 163 com texto extraido

    TRES DATAS QUE NAO SAO A MESMA, e a ferramenta mostra as tres:
      dado ...................... 2026-08-31 (PROD_FTS_6_20260831)
      mudanca provada mais nova .. 2026-07-20
      build ...................... 2026-09-06

---

## D · OBJETOS DE INTELIGENCIA PRODUZIDOS

    210 objetos                        51 PROVED · 159 NOT_PROVED

    DATA_QUALITY_EVENT        140   estado da nossa leitura, nao do produto
    DATE_CHANGE                27   validade declarada mudou entre instantaneos
    NEEDS_HUMAN_REVIEW         19   13 por fio desenhado, 6 por plausibilidade
    EXPIRY_EVENT               15   validade passou e o registro lista em vigor
    PRODUCT_ENTERED_REGISTRY    4
    STATUS_CHANGE               3
    REVOCATION_ACT_CHANGE       2

    ACTION emitida: ZERO. Nao existe regra que a produza.
    POTENTIAL_BUSINESS_IMPLICATION: 210/210 NOT_PROVED (portao G-03 fechado).

---

## E · TELAS IMPLEMENTADAS

    1  O QUE MUDOU        mudanca vs condicao que continua valendo, com filtro
                          de janela real (30/90/365) contado a partir de HOJE
    2  PRODUTO 360        ficha, usos, dose, exclusoes, tetos, proveniencia
    3  LINHA DO TEMPO     54 versoes do registro, hash a hash
    4  CULTURA x ALVO     2.926 pares, com o estado de cada juncao de dose
    5  CALENDARIO         conflito real separado de concordancia
    6  POR AREA           7 capacidades ADAMA, com a regra de cada roteamento
    7  FILA DE REVISAO    o que a maquina recusou adivinhar, por mecanismo
    8  COBERTURA          7 coberturas, reconciliacao com a releitura crua
    9  BUSCA
    10 GAVETA DE EVIDENCIA (em todas as telas)

---

## F · USUARIOS ADAMA ATENDIDOS

    Regulatory ................ 210 objetos roteados (C-01, C-02)
    Intelligence ...............  51 roteados (C-08)
    Country / Product Team .....  51 roteados (C-09)
    Supply .....................  47 roteados (C-07, C-10, C-11, C-12)
    Comercial / RTV ............   0 — portao G-01 fechado, 210 barrados por C-05
    Marketing / Produto ........   0 — e a tela DIZ que e estrutural
    Desenv. de Mercado .........   0 — idem

Marketing e Desenvolvimento recebem zero porque as regras C-03, C-04 e C-06
consomem `CROP_USE_ADDED/REMOVED`, `TARGET_USE_ADDED/REMOVED`, `DOSE_CHANGE` e
`RESTRICTION_CHANGE`, e **nenhum desses tipos tem emissor nesta versao**: o motor
compara campos do registro e ainda nao compara duas leituras de rotulo. A tela
afirma isso em vez de fingir caixa de entrada.

---

## G · EXEMPLOS REAIS DE VALOR

    1. Ruido separado de fato
       528 diferencas brutas entre instantaneos -> 496 (93,9%) sao a fonte
       reordenando a propria lista -> 36 mudancas reais. Sem esse filtro, a
       equipa leria 528 alertas para encontrar 36.

    2. Exclusao que era publicada como permissao
       NIMROD 002983 e VERBUM EW 013405: "Pomodoro (ad esclusione di Pomodoro
       ciliegino)". Toda ocorrencia de "cilieg" nos dois documentos esta dentro
       da exclusao, e a ferramenta publicava CILIEGIO x OIDIO como uso
       AUTORIZADO. Retirado, com a frase literal do rotulo e sha256 do PDF.

    3. Dose atribuida a cultura errada
       LAMDEX EXTRA e mais quatro: "TABACCO x CIMICI = 600 g/ha" com o selo de
       evidencia mais forte da ferramenta. Na etichetta, a linha Cimici esta
       dentro da celula de PORRO, com um fio desenhado entre as duas. Eram os
       CINCO unicos pares EXACT_MATCH do acervo — 100% da classe estava errada.

    4. Teto que a etichetta escreve fora da tabela
       "non superare le seguenti dosi per ettaro: soia... 600 g/ha" enquanto a
       tabela da 580-1200. 40 pares exibiam dose acima do teto do proprio rotulo;
       a string "non superare" nao aparecia uma unica vez no payload.

    5. A pergunta de terca-feira
       "O que mudou nos ultimos 30 dias?" — resposta ZERO, com a razao: a
       mudanca provada mais recente e de 2026-07-20, e dos 30 dias da janela, 6
       nao foram cobertos por coleta nenhuma (NOT_COLLECTED, nao zero).

---

## H · METRICAS DE COBERTURA

Nao existe um numero unico. Cada linha conta uma coisa e nenhuma implica a
seguinte:

    LABEL_DISCOVERY ............ 163/163  100%
    LABEL_DOWNLOAD ............. 163/163  100%
    TEXT_EXTRACTION ............ 163/163  100%
    LABEL_READ ................. 163/163  100%
    AUTHORIZED_USE_ROW ......... 128/163   78,5%
    DOSE ........................ 21/163   12,9%
    PHI ......................... 0/163     0%   NOT_ATTEMPTED por decisao

    166 fichas e 163 denominador nao sao contradicao: 3 registros aparecem no
    historico sem estar no conjunto ativo (009322, 014225, 014227). Tem ficha
    porque a linha oficial deles foi lida; nao entram na cobertura porque nenhum
    rotulo foi coletado para eles. A tela COBERTURA declara os dois e se recusa
    a soma-los.

    RECONCILIACAO com a releitura crua da fonte (calculada, nao digitada):
      mudancas reais ............ 36 medidas / 36 publicadas / delta 0
      linhas de dose distintas .. 519 / 510 / delta 9   = filtro P-01..P-05
      rotulos com dose .......... 23 / 21 / delta 2     = P-01

---

## I · MUDANCAS REAIS VS RUIDO

    528  diferencas brutas de campo entre instantaneos consecutivos
    496  (93,9%) ruido de serializacao: a fonte reordena a propria lista
      2  a menos que a primeira versao da V1, porque a regra de oscilacao N-03
         apagava uma prorrogacao REAL de validade da POWERFILM
     36  mudancas reais publicadas

    Suite adversarial de ruido: 12/12.
    Ataques que a ferramenta resiste, cada um medido: BOM, CRLF, aspas,
    reordenacao de colunas e de linhas, espaco interno, zeros a esquerda,
    duplicata, outro leitor de CSV, oscilacao ida-e-volta, e — novo — coluna
    VIGIADA renomeada, que agora PARA o differ em vez de emitir uma mudanca
    falsa por produto.
    Dois controles positivos: mudanca real de validade e revoga real continuam
    sendo detectadas.

---

## J · REVIEW QUEUE

    19 doses rebaixadas, por DOIS mecanismos com graus de evidencia diferentes:
       13 por FIO DESENHADO da tabela (medida do documento)
        6 por PLAUSIBILIDADE P-01..P-05 (heuristica nossa)
       e a fila mostra, por linha, o que o fio dizia ANTES da heuristica passar
       por cima — em 2 das 6 ele dizia CONFIRMED_BY_RULE.

    140 rotulos sem tabela de uso lida (a maioria dos herbicidas italianos
        declara dose em prosa; este leitor le tabela)
     76 linhas de dose com a CULTURA contradita por fio (R-11) — nao publicam
    180 linhas com alvo nao encontrado literalmente (R-13) — publicam, marcadas
     10 pares com dose AMBIGUA — a ferramenta nao escolhe
    152 pares com DOSE_NOT_PROVED_TARGET_NOT_LITERAL — o numero existe, esta a
        um clique, e nao e apresentado como resposta

---

## K · RESULTADO DOS TESTES DE USO

Oito tarefas reais, medidas em navegador nas duas rodadas adversariais.
O que a ferramenta responde HOJE, apos as correcoes:

    1  "o que mudou nos ultimos 30 dias?"     ZERO, com a razao e os dias
                                              nao cobertos declarados
    2  "e nos ultimos 12 meses?"              22, com evidencia por card
    3  "qual produto vence primeiro?"          CALENDARIO, com conflito real
                                              separado de concordancia
    4  "GOLTIX STAR foi revogado — e agora?"  ficha completa lida do
                                              instantaneo, rotulo NOT_COLLECTED
    5  "posso usar NIMROD em tomate cereja?"  a exclusao aparece, com a frase
                                              literal e o sha256 do PDF
    6  "dose de LAMDEX em barbabietola?"      AMBIGUA, com as candidatas
       "dose de LAMDEX em soia x nottue?"     NO_DOSE_ROW_FOR_THIS_PAIR — era
                                              420-800, de uma linha fundida
    7  "quem tem uso em VITE x OIDIO?"        lista com o estado de cada juncao
    8  "o que a ferramenta NAO sabe?"         COBERTURA + FILA DE REVISAO

---

## L · RESULTADO DO RED TEAM

    RODADA 1   12 lentes + arbitro    108 achados   20 BLOCKING
               veredito: DEMO_READY = NAO, 7 MUST_FIX
    RODADA 2   12 lentes + arbitro    118 achados
               veredito: DEMO_READY = NAO, 13 MUST_FIX, 20 SHOULD_FIX
               contra o build ja corrigido da rodada 1

    Estado dos 13 MUST_FIX da rodada 2:
      MF-01 dose com cultura errada e selo EXATA .......... CORRIGIDO (R-11)
      MF-02 selo CONFIRMADA sobre celula errada ........... CORRIGIDO em parte
      MF-03 rebaixa anunciada e valor publicado ........... CORRIGIDO
      MF-04 alvo fundido de duas linhas ................... CORRIGIDO na forma
            que o arbitro prescreveu ("se o alvo nao existe literalmente, o
            estado e NOT_PROVED, nao um numero"), NAO por deteccao de fusao:
            o detector continua NOT_IMPLEMENTED e R-13 diz por que. 152 pares
            deixaram de responder com numero e passam a
            DOSE_NOT_PROVED_TARGET_NOT_LITERAL, com o valor lido a um clique.
            SOIA x NOTTUE, o caso provado, deixou de exibir 420-800.
      MF-05 dose acima do teto do rotulo .................. CORRIGIDO (R-12)
      MF-06 citacao de frase que o rotulo nao escreveu .... CORRIGIDO
      MF-07 janela de calda apresentada como cultura ...... CORRIGIDO
      MF-08 conflito de validade inventado ................ CORRIGIDO
      MF-09 relogio quebrado virando zero ................. CORRIGIDO
      MF-10 link para token de ignorancia ................. CORRIGIDO
      MF-11 C-11 descrevia campo que os objetos nao tem ... CORRIGIDO
      MF-12 ambiguidade sobre candidata sem valor ......... CORRIGIDO
      MF-13 numerador digitado a mao na legenda ........... CORRIGIDO

    Tres achados foram MEUS, encontrados antes ou junto do red team: a
    atribuicao de cultura das linhas de dose, o teto por cultura, e um erro de
    indexacao de pagina (fios() e 1-indexado, palavras() e 0-indexada) que fez
    duas medicoes minhas compararem a pagina errada com numeros plausiveis.

    RODADA 3   12 lentes + arbitro    130 achados brutos
               veredito: DEMO_READY = NAO, 11 MUST_FIX, 16 SHOULD_FIX,
               8 FUTURE, 6 FALSE_FINDING. 7 de 12 portoes falharam.
               Diagnostico central, na frase do arbitro: "a rodada 2 achou os
               defeitos na camada de DOSE e os consertos foram aplicados na
               camada de dose. Nenhum foi aplicado a camada de PARES DE USO,
               que e a afirmacao regulatoria mais fundamental e a unica sem
               regra R-* propria. O defeito nao foi corrigido: subiu uma
               camada, usando os mesmos selos verdes."

    Estado dos 11 MUST_FIX da rodada 3 — remedido em
    v1/testes/CONFERENCIA-MUST-FIX.json e travado em test_casco.js:
      MF-01 R-11 nunca aplicada aos PARES DE USO ......... FECHADO — regra nova
            R-14 (v1/inteligencia/par_validar.py). 47 pares retirados,
            e os 47 estao na lista que o arbitro mediu por conta
            propria, com outro instrumento e a partir de coordenadas que este
            repositorio nao tem.
      MF-02 012573 EKO OIL SPRAY: 18 alvos falsos ....... FECHADO — BARBABIETOLA
            fica com os 4 alvos que a etichetta lhe da e CARCIOFO com os 6; o
            irmao 014386 OLIONET, que le a MESMA frase e ja acertava, sai com
            ZERO retirada.
      MF-03 EXCLUSION_AS_PERMISSION em sucessao ......... FECHADO — regra nova
            R-10b. 4 pares (BARBABIETOLA e COLZA em 017868/017585) saem com a
            frase literal do rotulo ao lado.
      MF-04 heranca de celula mesclada em MAX/INTERVALO . FECHADO — regra nova
            R-15 (v1/inteligencia/heranca_validar.py), nos dois casos: os fios
            da coluna DO VALOR, e a nota que enumera culturas mandando sobre a
            posicao de linha.
      MF-05 MAX/INTERVALO publicados em linha reprovada . FECHADO — a supressao
            vale para as tres colunas.
      MF-06 R-13 calculado e nao lido na tela ........... FECHADO — chega a
            viewProduto, a evDose e ao selo, que deixa de dizer CONFIRMADA
            sobre linha cujo alvo nao existe no documento.
      MF-07 contido() casando token dentro de lista ..... FECHADO — casamento
            por ITEM INTEIRO, e CROP_IDENTITY_NOT_PROVED onde a etichetta
            escreve duas formas do mesmo nome curto.
      MF-08 #cq=porro respondendo "0 pares" ............. FECHADO em parte:
            a tela responde CROP_NOT_IN_USE_VOCABULARY com as linhas de dose que
            existem, e a COBERTURA declara o vocabulario fechado. Cobertura por
            CELULA DE CULTURA DESENHADA continua NOT_MEASURED, e esta dito.
      MF-09 ressalva escondida da tela de cultura ....... FECHADO.
      MF-10 conflito de validade inventado em viewProduto FECHADO.
      MF-11 NOT_PRESENT apagando restricao de fora ...... FECHADO — vocabulario
            de restricao medido nos 163 rotulos, e a citacao para no salto de
            coluna para nao virar frase remontada.

    O QUE ISSO CUSTOU EM PARES PUBLICADOS
      2.926 -> 2875.  47 retirados por R-14, 4 por R-10b.
      Conferencia da heranca: {"INTERVAL_NOT_INHERITED": 743, "MAX_NOT_INHERITED": 579, "MAX_CONFIRMED_BY_RULE": 209, "INTERVAL_CONTRADICTED_BY_RULE": 47, "MAX_CONTRADICTED_BY_RULE": 39, "INTERVAL_CONFIRMED_BY_RULE": 37, "MAX_CONTRADICTED_BY_LABEL_NOTE": 9, "MAX_NOT_VALIDATED": 3, "INTERVAL_NOT_VALIDATED": 3}

    UMA CONTRA-PROVA QUE NAO SERVIU, E ESTA DITO QUE NAO SERVIU
      Conferir os pares retirados so pelo TEXTO — cultura e alvo no mesmo escopo
      de cabecalho com dois-pontos — responde SIM em 93,6% dos contraditos e em
      98,5% dos consistentes NOS MESMOS ROTULOS. Um teste que responde a mesma
      coisa para os dois grupos nao mede nada. E exatamente o vazamento de
      escopo que MF-02 descreve, e a razao de a regra ser GEOMETRICA. A medicao
      esta em CONFERENCIA-MUST-FIX.json para que ninguem apresente a
      coocorrencia textual como corroboracao.

    PORTOES desta entrega: 19/19.  RUIDO: 12/12.  RENDER: 23/23
    (12 anteriores + os 11 MUST_FIX da rodada 3 virados teste de regressao).

---

## M · LIMITACOES / NAO SEI

Escrito como limitacao porque e limitacao, nao como nota de rodape:

    1  DETECTOR DE FUSAO DE LINHA: NOT_IMPLEMENTED.
       Existe fusao provada (008259, "Nottue defogliatrici (allo scoperto)
       tentredine" recebendo a dose de outra linha). Tres tentativas medidas:
       teste literal acusa 180/839 e a maioria e quebra de coluna; heuristica de
       conteudo acusa 86 e condena alvo multiplo legitimo; ancoragem por fios
       acusa ZERO. Nenhuma serve, e nenhuma foi enviada.
       Consequencia assumida: a ferramenta se ABSTEM onde nao pode confirmar a
       linha de origem, e perde 152 respostas provavelmente corretas para nao
       arriscar uma errada. Isto e o preco de nao ter o detector, e esta pago
       na direcao segura.

    1b PARES DE PROSA: SEM INSTRUMENTO NENHUM.
       R-14 confere a geometria e por isso so alcanca par lido de TABELA.
       1.056 pares vem de rota de prosa (AUTHORISED_USE_LIST,
       HEADER_CONTINUATION) e saem PAIR_NOT_CHECKABLE_ROUTE_NOT_GEOMETRIC —
       NOT_CHECKED, nunca aprovacao, e a tela diz isso na coluna de evidencia.
       Mas eles continuam publicados como uso autorizado, e nao ha nem regra
       geometrica nem regra textual para eles: medido, o teste so-de-texto
       responde a mesma coisa (93,6% x 98,5%) para pares que a geometria condena
       e para os que ela absolve. E o maior buraco aberto desta versao.

    1c AS QUATRO ABSTENCOES DE R-14 SAO SUPERFICIE NOVA DE ATAQUE.
       PAIR_NOT_CHECKABLE_NO_DRAWN_CELL, _ANCHOR_NOT_FOUND,
       _CROP_ALSO_OUTSIDE_TABLE e _TARGET_UNDER_CROP_HEADER existem porque cada
       uma nasceu de um falso positivo REAL medido no acervo (008102 MERPAN,
       012573, 010587 FOLPAN SC, e a flexao "Tignola"/TIGNOLE). Todas erram para
       o lado de nao apagar uso verdadeiro — que e o lado certo — e todas podem,
       pelo mesmo mecanismo, estar deixando passar um par falso. A proxima
       rodada adversarial deve atacar exatamente elas.

    2  CELULA DE CULTURA TRUNCADA: nao detectada.
       Em 008189/014479 a celula publicada perde "Rapa, Navone, Melone". A linha
       especifica ja e barrada por R-11, mas o truncamento em si nao tem teste.

    3  PHI: nao publicado. O extrator do piloto esta PROTOTYPE_NOT_SHIPPED
       (2 de 15 rotulos, primeira linha de cada bloco contaminada).
       PHI_COVERAGE = 0 por DECISAO, nao por ausencia de carencia nas etichette.

    4  CITACAO LITERAL DOS PARES CULTURA x ALVO: NOT_PRESERVED. Os pares
       reusados nao gravam coordenada x e a etichetta tem varias colunas por
       pagina. Tentado, medido, descartado no piloto.

    5  52 rotulos tem restricao de dose fora da tabela em formato que este
       leitor nao le ("non superare la dose massima di X per anno"):
       LABEL_NOTES_NOT_READ. Nao autoriza dizer que a dose da tabela e o limite.

    6  40 pares tem apoio textual da cultura so por prefixo
       (CROP_NAME_PREFIX_MATCH_ONLY) e 12 tem o nome ausente do texto do rotulo
       (o rotulo escreve "Grano", o leitor normaliza para FRUMENTO).

    7  A ferramenta nao modela escopo negativo DENTRO de um uso. Ela avisa que
       ele existe em 10 rotulos.

    8  Nada foi coletado depois de 2026-08-31. O que mudou desde entao e
       NOT_COLLECTED, nao zero.

---

## N · COMPETITOR_EXTENSION_RECOMMENDATION

    COMPETITOR_EXTENSION_VALUE   ALTO e ja medido, nao projetado.
      O mesmo CSV que traz os 163 produtos ADAMA traz 17.695 do mercado. Sem
      coleta nova: 2.298 eventos regulatorios de mercado contra 34 da ADAMA na
      mesma janela. A ADAMA e 4,4% dos produtos ativos e 1,5% dos eventos.
      Sem denominador de mercado, "houve 36 mudancas" nao tem escala.

    COMPETITOR_COLLECTION_COST   ZERO para o registro (o dado ja esta em disco,
      no mesmo arquivo). ALTO para rotulo: seriam ~17.500 PDFs.

    COMPETITOR_V1_RECOMMENDATION
      Estender ao REGISTRO de concorrentes: sim, custo zero, valor imediato.
      Estender ao ROTULO de concorrentes: nao nesta versao. A metade que le
      rotulo ainda esta sendo consertada; multiplicar por 100 o volume de uma
      leitura que acabou de errar a cultura de 76 linhas seria multiplicar o
      erro, nao o valor.

---

## O · AUTOMATION_READINESS

    A esteira esta DESENHADA e EXECUTAVEL A MAO, e NAO ESTA ATIVADA.
    `sh v1/pipeline.sh 2026-09-06` roda os 15 passos:

      chain TLS -> registro (check/snapshot/hash/identidade) -> rotulo
      (conferir hash, baixar so o que mudou, preservar) -> dose por geometria
      -> conferir dose contra fios -> plausibilidade -> R-10 exclusao
      -> R-11 cultura -> R-12 teto -> R-13 alvo literal -> COLETA
      -> INTELIGENCIA -> PORTAO de ruido -> CASCO -> PORTAO de render
      -> auditoria independente

    NAO ha cron, webhook, deploy nem agendamento. Ligar e decisao de quem opera.
    Os dois portoes rodam ANTES de publicar: se qualquer um falhar, o pipeline
    para e nada e publicado.

---

## P · DEMO_READY = **NAO**

Nao por prudencia retorica: por duas razoes nomeaveis, e as duas mudaram de
conteudo desde a ultima vez.

    1  NENHUM ARBITRO ADJUDICOU ESTE BUILD. O ultimo veredito (rodada 3, 11
       MUST_FIX, 7 de 12 portoes falhando) e sobre o build d08668c. Os onze
       estao fechados e remedidos, e onze testes de regressao os travam — mas
       quem mede o resultado disso nao pode ser quem o produziu. Declarar SIM
       aqui seria eu me aprovando, e a ferramenta inteira existe para nao
       aceitar afirmacao sem verificacao de fora.

       O que ha de convergencia independente, e vale registrar sem chamar de
       adjudicacao: R-14 foi escrita sem acesso as coordenadas que o arbitro
       usou (CROP_Y e TARGET_Y morreram no payload e o repositorio de origem
       nao esta acessivel), e os 47 pares que ela condena sao exatamente os que
       ele enumerou por conta propria — incluindo os 18 de 012573 e o zero do
       irmao 014386. Dois instrumentos diferentes chegando a mesma lista e
       evidencia; nao e veredito.

    2  A CAMADA QUE LE ROTULO CONTINUA SENDO A METADE FRACA, e agora ela diz
       isso com mais precisao em vez de dizer menos:
         - FUSION_DETECTOR = NOT_IMPLEMENTED, com as tres tentativas medidas;
         - 1.056 pares tem rota de PROSA e R-14 nao roda neles: sao
           PAIR_NOT_CHECKABLE_ROUTE_NOT_GEOMETRIC, que e NOT_CHECKED e nunca
           aprovacao — mas continuam publicados como uso autorizado;
         - a cobertura por CELULA DE CULTURA DESENHADA continua NOT_MEASURED;
         - PHI continua PROTOTYPE_NOT_SHIPPED, nada publicado.

    O que faria virar SIM, na ordem:
      a) uma quarta rodada adversarial contra ESTE build, com arbitro — e ela
         tem de atacar as ABSTENCOES novas, que sao onde nasce defeito novo:
         as quatro de R-14 (sem celula desenhada, ancora nao encontrada,
         evidencia mista, cabecalho de bloco) foram escritas para nao apagar uso
         verdadeiro, e cada uma pode estar escondendo um par falso;
      b) uma regra para os 1.056 pares de prosa — hoje eles nao tem instrumento
         nenhum, nem geometrico nem textual (ver a contra-prova da secao L);
      c) um detector de fusao de linha de verdade.

    Nao esta na lista "corrigir os 11 MUST_FIX": estao fechados, e cinco deles
    fechados por ABSTENCAO, que e o lado seguro. A entrega diz isso em vez de
    chamar abstencao de capacidade.

    A metade do REGISTRO desta ferramenta esta solida e foi verificada de fora:
    373 sha256 recalculados sem divergencia, 528/496/36 reproduzido em
    recontagem independente, o censo de T-09 conferido digito por digito, e
    36/36 objetos e 166/166 produtos conferindo campo a campo contra os CSVs no
    differ que o proprio arbitro reescreveu.
    A metade que LE ROTULO deu o maior salto desta missao — a afirmacao de USO,
    que e a mais fundamental que a ferramenta emite, passou a ser conferida
    contra o desenho da tabela — e ainda nao merece a mesma confianca.

## Q · PORTAL_INTEGRATION_RECOMMENDATION

    NAO INTEGRAR.

    Nao por cautela generica, e sim porque a metade que le rotulo ainda produz
    afirmacao material errada e a integracao removeria a moldura que hoje avisa
    disso. Dentro desta ferramenta, uma dose sem prova aparece como
    NO_DOSE_ROW_FOR_THIS_PAIR ao lado da regra que a barrou; exportada para o
    portal, ela vira um campo.

    Quando integrar fizer sentido, integrar o que esta provado: a metade do
    registro — mudanca, ruido, versao, validade, estado — que sustenta cada
    palavra do proprio vocabulario. A metade do rotulo entra depois, e so
    depois de um arbitro dizer que ela merece.

---

    Ferramenta:  v1/casco/label-intelligence.html   (abre sem servidor)
    Regras:      v1/inteligencia/REGRAS.md@4
    Portoes:     v1/testes/  — 19 portoes, 12 testes de ruido, 12 de render
