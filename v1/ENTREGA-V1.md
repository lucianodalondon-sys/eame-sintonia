# SINTONIA — LABEL INTELLIGENCE V1 · ENTREGA

Ferramenta paralela, standalone, para a equipa ADAMA Italia. Nao integra com o
portal, nao escreve em `sintonia/canonical`, nao faz deploy.

---

## A · HEAD / BRANCH

    BRANCH        claude/label-intelligence-v1-italy
    PILOT_HEAD    df3a4fd0029e74d16f171e5070b13ec4f3345d64   (base, missao 1)
    BUILD_HEAD    eabaaac9c13431e4635ae776e24b9ef1e36e72d5
                  o commit cujo build foi medido para escrever este documento.
                  O commit que ADICIONA este documento vem depois dele, e por
                  isso nao pode citar o proprio hash.
    COMMITS       19 desde PILOT_HEAD ate BUILD_HEAD
    ARQUIVOS      35 em v1/ em BUILD_HEAD, mais os do piloto
    RULESET       v1/inteligencia/REGRAS.md@4

    CANONICAL_TOUCHED = NAO
      medido com git, nao com uma constante: nenhum dos 19 commits desta missao
      esta em sintonia/canonical. Canonical avancou de bdb57cf para 10af4a7
      durante esta missao, com tres commits que NAO sao meus — outra sessao
      trabalhou nela. O portao antigo fixava o head numa constante e teria
      transformado o trabalho legitimo de outra pessoa num alarme desta missao.

    REUSO ANCORADO NO ARQUIVO, NAO NO BRANCH
      IT-ROTULOS-PARES-V3.json  sha256 024b19979343df2f255ab543...  2.928 pares
      conferido a cada build; se mudar, o payload aborta.

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

    PORTOES desta entrega: 19/19.  RUIDO: 12/12.  RENDER: 12/12.

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

Nao por prudencia retorica: por duas razoes nomeaveis.

    1  NENHUM ARBITRO ADJUDICOU ESTE BUILD. O ultimo veredito (rodada 2, 13
       MUST_FIX) e sobre o build anterior; doze deles foram corrigidos e o
       decimo terceiro foi fechado por abstencao, mas quem mede o resultado
       disso nao pode ser quem o produziu. Declarar SIM aqui seria eu me
       aprovando, e a ferramenta inteira existe para nao aceitar afirmacao sem
       verificacao de fora.

    2  Os 20 SHOULD_FIX da rodada 2 foram enderecados em parte, nao em todo.

    O que faria virar SIM, na ordem:
      a) uma terceira rodada adversarial contra ESTE build, com arbitro;
      b) fechar os SHOULD_FIX remanescentes;
      c) um detector de fusao de linha de verdade, que devolveria as 152
         respostas hoje perdidas pela abstencao.

    Nao esta na lista "corrigir MF-04": ele esta fechado pelo lado da
    abstencao, que e o lado seguro, e a entrega diz isso em vez de chamar
    abstencao de capacidade.

    A metade do REGISTRO desta ferramenta esta solida e foi verificada de fora:
    373 sha256 recalculados sem divergencia, 528/496/36 reproduzido em
    recontagem independente, o censo de T-09 conferido digito por digito.
    A metade que LE ROTULO melhorou muito nesta rodada — a classe de evidencia
    mais forte deixou de existir em vez de continuar errada — mas ainda nao
    merece a mesma confianca, e a ferramenta agora diz isso em vez de esconder.

---

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
