SINTONIA LAB · analista independente · Missão-05 (identidade estável do cruzamento)
STUDY_RUN_ID=STUDY-20260927T185235-5b7bdb (confirmação de identidade da execução, sem comentário)

=========================================================================
0 · O QUE EU CONFERI COM MEUS PRÓPRIOS OLHOS (não aceitei o pacote de fé)
=========================================================================
Espelho lido: C:/eame-sintonia, branch `claude/italy-forward-only-scheduling-v1`, HEAD `ee1bcc6ec` (medido: `git log --oneline -1`). Os ramos citados foram lidos como refs `origin/...` (leitura, nada alterado).

[M] Gerei e medi o arquivo de entrada do pote do cruzamento:
  origem/claude/cruzamentos-max-sguy1x:docs/intelligence/r7/CRUZAMENTOS-MAX-ITENS-DO-POTE.json
  → ITENS_POR_FERRAMENTA.portfolio = 103 objetos, dos quais
    89 com CHAVES.CRUZAMENTO = ROTULO_X_SUBSTANCIA_CITADA_NO_BOLETIM
    14 com CHAVES.CRUZAMENTO = PORTFOLIO_MATCH
  → ITENS_POR_FERRAMENTA.competitors = 125 objetos.
  Confere com o pacote (14 PORTFOLIO_MATCH; 125 competitors) e prova a causa-raiz melhor do que o pacote:
  dos 14 PORTFOLIO_MATCH, **13 são o mesmo par OLIVO × MOSCA_OLIVO, estado SEM_PAR_LIDO**, cada um com uma PROVA
  diferente (XMAX-1a55ad6505ea3edc item XX-T3-2026-09-18-134205, XMAX-7e1446234d0925f8 item …171909,
  XMAX-efa46a97635e8ea3 item …171937, XMAX-e34ae7f9d2ee4deb item IT-T3-…234958, XMAX-7362a9ca09074c8d item
  IT-T3-…110656, e 8 objetos com PROVA em LINHA-BUSCA-RAW-20260927T152708#2/#6/#7/#20/#21/#34/#35/#37).
  O 14º é VITE × flavescenza dorata della vite (estado NAO_SEI).

[M] Verifiquei o caso do FOLPET, e ele é pior do que «2 cartões»: a MESMA substância (FOLPET) sai com estados
  diferentes conforme o documento que entrou na chave:
  - XMAX-78a0867e2021da1d · FOLPET · UNRESOLVED · motivo: «o cabecalho de uma cultura (X3h) nao esta no troco
    guardado no repo: nao o consigo conferir»;
  - XMAX-c5c0aa312b6343f7 / XMAX-edcbe56af505ab52 / XMAX-2542c97acc1d875c · FOLPET · PARTIAL_GRAO_INCOMPATIVEL ·
    «a substancia nao esta ligada a nenhuma cultura no texto …»;
  - XMAX-94f5da1a9908883a (IT-PRD-037) e XMAX-c7ad31bd0923cda3 (IT-PRD-077) · FOLPET × VITE · CONFIRMED_YES ·
    registo válido em 2026-05-12 · item …152708#22.
  Ou seja: o cartão muda de resposta conforme qual boletim foi lido e se o pedaço de texto estava guardado no repo.
  Isso não é «duplicação» apenas estética: é a resposta da mesma pergunta dependendo de acaso de arquivo.

[M] Causa-raiz, no código (não é opinião): os IDs nascem da ORIGEM, não da PERGUNTA.
  - motor/cruzamentos_max.py (origin/claude/cruzamentos-max-sguy1x), `_oid()` = «XMAX-» + sha256(...)[:16], e as
    partes incluem o OBJETO_ID do piloto (que contém o `source_id`), ou a SALA_CHAVE do boletim («PM»), ou a origem
    do item («CS») — nada de CULTURA_ID/SUBSTANCIA_ID/EDIÇÃO como chave.
  - SIGNAL: corrida_da_inteligencia.py:641-644 → «SG-» + sha256(run_id + ITEM_ID + RAW_OBSERVATION_ID + len(SIGNALS)):
    entra o run_id **e a posição** ⇒ a mesma observação em duas corridas é obrigatoriamente dois sinais.
  - CROSSING piloto: provas/o_piloto_da_sala.py:350 → «XC-<source_id>-<ordem>-<substancia[:12]>» (+ «@<run da
    coleta>» na R7) [M pelo pacote; coerente com o que li no pote: os 2 CROSSING de docs/casco/r7/POTE-R7.json têm
    sufixo @XX-T3-2026-09-18-… e @IT-T3-2026-09-20-…].
  - FUTURO: montar_entrada_r7.py:99 → «FUT-» + sha256(RUN + …): o run na chave.
  Nenhuma dessas fórmulas sobrevive a uma segunda corrida. O pacote diz 0/47 IDs iguais entre R6 e R7; faz sentido
  pela própria fórmula — dava para prever isso no papel.

[M] Contrato do pote (origin/claude/pote-v2-unico-contract-y8o1pi:docs/intelligence/pote-v2/POTE_INTELLIGENCE_CASCO-v2.schema.json):
  `$defs.objeto.required` = [MARCA, NAO_PARA_CLIENTE, COMPARTIMENTO, OBJETO_ID, ESPECIE, ESPECIE_DITA_POR, ESTADO,
  CHAVES, CHAVES_NAO_SEI, FORA_DO_CONTRATO, PORQUE, CONTRADIZ, INCERTEZA, RESULTADO, USO_EXIGE_TEMPO, PROVA,
  CORRIDA_SINTETICA]. Não há **nenhum** campo de «corrida anterior», «versão», «identidade anterior» ou «delta».
  `additionalProperties` **não** é declarado no objeto (logo, campo novo valida — serve de margem para o DELTA),
  mas o topo é montado por `_cabecalho` + campos fixos, e campos de topo extras não são copiados.

[M] Bíblia (espelho: .claude/worktrees/intelligence-bible-canonical-review-749b7c/BIBLIA-DE-ENGENHARIA-DA-INTELLIGENCE.md):
  INT-LAW-030 (cabeçalho l.252: CROSSING consta na lista de identidades semânticas distintas — «Isso não obriga uma
  tabela para cada conceito; obriga identidades semânticas distintas»), INT-LAW-031 (l.274-278), INT-LAW-054 (l.407:
  «Parece a mesma pergunta não é cache key»), INT-LAW-125 (l.697), INT-LAW-210 (l.971), INT-LAW-220 (l.993).
  Minhas linhas batem com as do pacote (lote6 21cc06c0 / este espelho) — logo, as duas medições concordam.

[INF] Divergência que eu NÃO consegui resolver (declaro NÃO SEI): docs/casco/r7/POTE-R7.json tem 47 objetos e, no
  compartimento `portfolio`, apenas **2** CROSSING (os dois XC do piloto); já a entrada do pote no ramo
  cruzamentos-max tem **228** objetos de cruzamento (103+125). Não consegui determinar qual dos dois alimenta o portal
  que vai ao ar hoje. Se for o pote de 47 objetos, o portal publica 2 cruzamentos e as 13 duplicatas de OLIVO×MOSCA
  nem aparecem — o problema é outro. Isso precisa ser medido antes da decisão final (é a pergunta P6/P8).

=========================================================================
1 · DIAGNÓSTICO (uma frase)
=========================================================================
O sistema trata **origem e posição** como identidade de cruzamento; a lei da Intelligence (INT-LAW-030/054) e a
decisão do dono (D119) já dizem que identidade é **semântica**. Enquanto o ID for feito de origem+corrida+ordem,
toda corrida nova renomeia tudo e o «pote» não é foto de um mundo estável: é uma fotografia nova de um mundo com
nomes novos. Duplicação de hoje é consequência; duplicação entre corridas será pior.

=========================================================================
2 · P1 — CHAVE POR FAMÍLIA
=========================================================================
Princípio que eu adoto (e que resolve os dois erros simétricos — juntar coisas diferentes × separar iguais):
  IDENTIDADE = a PERGUNTA respondida (campos canônicos e resolvidos)
  PROVA      = documentos/boletins/trechos que sustentam, refutam ou não deixam conferir
  RESPOSTA   = conteúdo que muda (produtos autorizados, lista de registros, estados de terceiros)
  APRESENTAÇÃO = agrupamento visual, que pode ser mais frouxo que a identidade — e precisa dizer que é agrupamento.

CHAVE = (FAMILIA, campos da família que estão RESOLVIDOS)

F1 ROTULO_X_SUBSTANCIA_CITADA_NO_BOLETIM
   pergunta: «o dossiê ADAMA autoriza a substância S na cultura C (e alvo A, se houver), na edição E?»
   chave: FAMILIA | SUBSTANCIA_ID (canônico) | CULTURA_ID (canônico) | ALVO_ID | DOSSIE_EDICAO
   NÃO entram na chave: documento/boletim (é prova), run, ordem, semana do boletim, PRODUCT_ID.
   PRODUCT_ID/REGISTRATION_ID vão para a RESPOSTA (lista) com a validade lida — é exatamente isso que impede o
   folpet×vite de aparecer como 2 respostas que se contradizem.

F2 PORTFOLIO_MATCH (cultura × praga)
   pergunta: «o rótulo ADAMA cobre o par cultura×praga P?»
   chave: FAMILIA | CULTURA_ID | ALVO_ID | DOSSIE_EDICAO   ← boletim é prova
   ⇒ as 13 fichas de OLIVO×MOSCA_OLIVO viram **1** [HIP a testar: vale se a edição do dossiê for a mesma nos 13;
   se houver boletins de semanas diferentes, ver P2].
   Lista de produtos do par = RESPOSTA (hoje 0 produtos lidos ⇒ SEM_PAR_LIDO), não identidade.

F3 COMPETITIVE_SET
   pergunta: «quem mais está registado com a substância S no mercado/tempo T?»
   chave ao grão substância: FAMILIA | SUBSTANCIA_ID | MERCADO/GEO | EDICAO_DO_REGISTRO | GRAO=SUBSTANCIA
   chave ao grão produto (quando o grão é PRODUTO): (… | NUM_REGISTRAZIONE)
   ⇒ os 125 objetos/122 produtos são **conteúdo de uma resposta**, não 122 cruzamentos. Ao grão substância seriam
   poucos objetos (as substâncias em comum).

F4 janela olivo×mosca (windows)
   chave: CAP-WIN (Bíblia l.1850) → CULTURA_ID | REGIAO_ID/LUGAR_ID | FENOLOGIA | JANELA
   ⇒ o mesmo cuidado: «janela» tem de ser intervalo normalizado (início/fim), senão duas corridas nunca casam.

F5 futuro
   chave: CAP-FUT (l.1790) → ISSUE_ID | GEO | HORIZONTE (janela). O `RUN` sai da chave (FUT- de hoje tem RUN).

F6 sinal (SG-)
   chave: (DOCUMENTO_ID, TRECHO_SHA256, TIPO_DE_SINAL) — sem run_id, sem len().
   Motivo [M]: a fórmula atual (corrida_da_inteligencia.py:641-644) faz o mesmo sinal mudar de nome a cada corrida
   (pacote mede SG-bd9e632048e29455 → SG-88e86b69caf55bea para o mesmo item).

F7 rendimento de fonte (REND-)
   aqui sim o run faz parte: é métrica de execução, não cruzamento. Chave: (SOURCE_ID, RUN_ID). Manter.

Granularidade — regras explícitas (nenhuma delas é preferência minha; todas saem da lei/decido do dono):
  - lugar: só funde quando o LUGAR_ID é o mesmo registro resolvido; comum ISTAT > província > região, e **níveis
    diferentes não fundem**. Zona definida pela fonte («Comprensorio LE - Pianura Salentina Sud») é um lugar próprio,
    não soma com província. «zona costeira» não resolvida ⇒ não funde (D111/D112; INT-LAW-091 l.579).
  - 3 distritos com o mesmo texto = **3 aplicações, 1 instituição** (D112; INT-LAW-071..078 l.476-526): 3 identidades,
    contagem de fonte independente = 1.
  - cultura genérica («drupacee») ≠ específica: chaves diferentes, nunca fundem por contenção. Equivalência só com
    alias declarado (D104.3) ou código EPPO (INT-LAW-081..084 l.549-571: similaridade não prova equivalência).
  - praga com 5 nomes: ID canônico (EPPO, ex. PEST:DACUOL no canário Puglia do LAB), nunca nome local.
  - tempo: a chave de F1/F2 **não** carrega a semana do boletim (é prova). F4/F5 carregam janela, e ela é intervalo.
    «validade do boletim» e «dia/semana/estação» vivem na prova/fato, não na identidade (INT-LAW-100 l.612).

E a pergunta decisiva: **o que acontece quando a chave tem NÃO SEI?**
  Minha resposta: o objeto é criado com CHAVE_INCOMPLETA = TRUE e **não funde com nada** enquanto a chave não
  resolver (INT-LAW-091 l.579 — chave faltando vira NOT_POSSIBLE/UNKNOWN/PARTIAL; INT-LAW-054 l.407 — parecer não é
  chave). Ele aparece no casco **dentro de um grupo** (agrupamento de apresentação, por ex. por SUBSTANCIA_ID), com
  o rótulo «chave incompleta» e o N (quantos). Quando a chave resolve (lugar/cultura/entidade), isso **não** é
  renomear: é mudança semântica e exige migration explícita com histórico (INT-LAW-224 l.1037). Sem essa separação,
  ou a gente funde perguntas diferentes (mentira) ou mantém 48 fichas de FOLPET na tela (bagunça). Este é o ponto
  mais importante do meu parecer.

=========================================================================
3 · P2 — TEMPO: SETEMBRO × OUTUBRO, EPISÓDIO × SÉRIE
=========================================================================
  - IDENTIDADE (a pergunta) é **estável no tempo**: «o rótulo cobre folpet em vite?» é uma.
  - EPISÓDIO = identidade × JANELA (o boletim 01–07/10, o horizonte de 7 dias, a semana ARIF n.38).
  - SÉRIE = a identidade ao longo do tempo (lista de episódios).
  Consequência: boletim de setembro e de outubro do MESMO par → **mesmo cruzamento** (1 cartão), com 2 provas e 2
  episódios; o estado ativo é o do episódio mais recente, e a passagem de estado fica no histórico append-only
  (INT-LAW-210 l.971, INT-LAW-125 l.697). Mudança de recomendação no tempo («tratar» → «não tratar») = estado
  MUDANCA_TEMPORAL, não contradição (D111/D112; INT-LAW-079 l.528).
  Ressalva honesta: quando a janela for parte da pergunta (F4/F5), semanas diferentes dão objetos diferentes — e aí
  a «série» é o que amarra os dois. Ou seja, a mesma regra, aplicada ao que a família declara.

=========================================================================
4 · P3 — PROVA
=========================================================================
Modelo: lista append-only de PROVA dentro do objeto, cada uma com ID estável próprio:
  PROVA_ID = sha256(SOURCE_ID | RAW_OBSERVATION_ID | DOCUMENT_ID | TRECHO_SHA256 | TRECHO_POSICAO) — **sem run e
  sem ordem** (mesma correção do SG-).
Campos que a independência exige (sem eles não há contagem honesta):
  - INSTITUTION_ID (originador: ARIF, Regione Campania, APOL, …) — INT-LAW-071..078;
  - CONTENT_SHA256 (o `raw_sha256` do documento) — dedupe de notícia replicada por CONTEÚDO, não por URL;
  - PAPEL: SUPORTA | REFUTA | NAO_CONFERIVEL;
  - ENTITY_SOURCE / LOCATION_SOURCE (D112: procedência por entidade, lugar só do texto);
  - LUGAR_E_FATO vs LUGAR_DA_FONTE separados (INT-LAW-100 l.612).
Contagens separadas e nunca somadas: EXTERNAL_SIGNAL_COUNT · INDEPENDENT_SOURCE_COUNT · STRUCTURAL_VALIDATION_COUNT
(INT-LAW-092 l.587). 3 distritos do mesmo texto = 1 instituição ⇒ INDEPENDENT_SOURCE_COUNT=1. Notícia replicada ⇒ 1.
Contradição aberta: as duas provas ficam, o estado fica UNRESOLVED, CONTRADIZ aponta a prova contrária
(INT-LAW-033 l.287-291 «CONTRADICTION é first-class»); INT-LAW-079: divergência ≠ contradição — 4-5% × 10-15% é
DIVERGENT (D112), não contradição.
A prova que não deu para conferir (o FOLPET «cabecalho … nao esta no troco guardado no repo») é PAPEL=NAO_CONFERIVEL.
Isso é importante por dois motivos: (a) não mente dizendo «não autoriza», (b) o motivo técnico («falta o pedaço de
texto no nosso arquivo») é **Know-how** (D109) — no objeto/Brain fica só NAO SEI + BASIS curto, nunca «o extrator
falhou». Se o LAB não respeitar isso, o Brain nasce contaminado de engenharia.

=========================================================================
5 · P4 — ESTADOS E TRANSIÇÕES
=========================================================================
Proposta de máquina (nomes honestos; os atuais misturam coisas diferentes):
  NAO_CONFERIVEL   prova existe, não conferível (texto/trecho ausente) — hoje disfarçado de UNRESOLVED
  CHAVE_INCOMPLETA falta componente da chave (PARTIAL_GRAO_INCOMPATIVEL cabe aqui)
  NAO              refutado com prova
  POSSIVEL         indicação sem confirmação de registro
  CONFIRMADO       dossiê autoriza, com a **lista de produtos/registros válidos** (a resposta, não o ID)
  DESATUALIZADO    D117: >14 dias sem checagem
  A_CONFIRMAR_POR_FRESCOR  D117: >30 dias ⇒ autorização «a confirmar»
  MUDANCA_TEMPORAL recomendação mudou no tempo (D112)
Gatilhos de reavaliação: (a) prova nova; (b) **nova edição do dossiê/bula** (D116: nova coleta oficial = nova versão
⇒ todo cruzamento que AFIRMA autorização tem de ser reavaliado); (c) relógio/frescor (D117); (d) correção na Sala
(revisão append-only — supabase/migrations/033:222-243 — pode revogar prova); (e) resolução de chave (migration
explícita, INT-LAW-224).
Regra dura, sem a qual nada disso é auditável: **estado = função pura de (conjunto de provas, edição do dossiê,
relógio)**. Se o estado depender de «qual corrida rodou primeiro», não é reproduzível.
Histórico: registro append-only com DE → PARA, QUANDO, QUAL_PROVA, POR_QUE (INT-LAW-125 l.697: PREVIOUS/NEW/
WHAT_CHANGED/WHY/NEW_EVIDENCE); nada se apaga (INT-LAW-210 l.971); outcome posterior não reescreve julgamento
passado (INT-LAW-210..213 l.1003-1015).
E o ponto que resolve a dor do dono: **CONFIRMADO é resposta por produto, não por pergunta** — a pergunta tem um
resumo (CONFIRMADO se ≥1 registro válido) + a lista. Sem isso, folpet×vite continuará saindo com 2 estados
diferentes e nenhum jeito honesto de mostrar.

=========================================================================
6 · P5 — COMPOSIÇÃO (Finding / Opportunity / Future)
=========================================================================
  - Referenciam CROSSING_ID estável **e** a versão usada (edição do dossiê + estado + data do julgamento); nunca
    copiam a prova para dentro (senão a prova muda e o finding mente em silêncio).
  - Reavaliação determinística: qualquer gatilho do P4 coloca o crossing numa fila de reavaliação; o finding é
    recomputado e registra de→para (INT-LAW-125). Chega de «finding velho apontando para cruzamento renomeado» —
    hoje isso viraria órfão silencioso.
  - Ciclos: proibir aresta que volte (CROSSING→FINDING→…→CROSSING); checagem de DAG simples no fim da corrida.
  - Dupla contagem: contar INSTITUIÇÕES distintas 1× e não cartões; a mesma prova em 2 findings conta 1
    (INT-LAW-092).

=========================================================================
7 · P6 — POTE E CASCO (onde vive o LIVRO)
=========================================================================
Manter «1 pote por corrida» (é a foto) e acrescentar um **LIVRO DE IDENTIDADES** (a memória):
  - onde: no **mesmo Postgres** — D104.1 proíbe banco paralelo — append-only, com o mesmo padrão já provado de
    `sala_de_espera_revisao` (trigger recusa UPDATE/DELETE; migrations/033:222-243). Escrito **só** pela Intelligence.
  - o que guarda: por identidade estável — primeira aparição, provas acumuladas, estado atual, histórico de estados,
    edição do dossiê usada. Nada de UPDATE: cada mudança é uma linha nova.
  - o pote continua a foto e ganha 3 coisas mínimas: (i) `LIVRO_HEAD` no topo (análogo a `SOURCE_HEAD`, medido no
    schema/`_cabecalho`) — sem isso o DELTA não é reproduzível; (ii) por objeto, um bloco opcional
    `DELTA {ENTROU|FORTALECEU|MUDOU_DE_ESTADO|SAIU, DE, PARA, DESDE_QUANDO, QUAIS_PROVAS}`; (iii)
    `ID_PROVISORIO: true` (D119).
  - compatibilidade v2: o objeto **não** declara `additionalProperties`, logo campos novos validam; o topo, porém,
    é montado em `_cabecalho` + campos fixos (pacote/pote_intelligence_casco.py:33 citado no pacote), então o topo
    precisa ser estendido no gerador. O casco **não calcula**: ele lê o campo e desenha (INT-LAW-023/280).
  - DELTA sem banco novo (mais simples, se o LIVRO assustar): comparar o pote da corrida com o pote anterior
    (arquivo versionado) e emitir o mesmo bloco. Funciona hoje, é reversível; a diferença é que, sem LIVRO, provas
    antigas que não reaparecem na corrida se perdem — e aí a contagem de fontes independentes fica errada.
    Meu veredito entre os dois: **LIVRO agora, porque provas acumulam**; DELTA-do-arquivo só como paliativo de hoje.
  - «saiu»: existe, mas é o estado mais perigoso. Um cruzamento não «sai» porque o boletim da semana não o citou —
    ele fica DESATUALIZADO (D117). SAIU só quando o dossiê deixa de autorizar (D116) ou a prova é revogada.

=========================================================================
8 · P7 — MIGRAÇÃO DOS IDs ATUAIS (XC-, XMAX-, SG-, FUT-, REND-)
=========================================================================
Nunca reescrever ID antigo (isso quebra lineage e prova; INT-LAW-045 l.371). Fazer:
  1. script de reconciliação que CALCULA a identidade nova de cada objeto antigo (R6 e R7 já publicados);
  2. tabela de mapa (OBJETO_ID antigo → IDENTIDADE_ID nova → corrida → quando) — é ela que torna a migração
     reversível;
  3. o objeto novo carrega `IDS_HISTORICOS: [...]` (alias nunca apagado — mesmo espírito da D104.3: nome original
     nunca apagado);
  4. medir e REPORTAR: quantos objetos, quantos fundem, quantas colisões.
  Critério de FALHA explícito: se dois objetos que se fundem tiverem conteúdo divergente (ex. um CONFIRMADO_YES e um
  NO, ou um NO e outro mesmo par) — **PARAR** e levar ao dono: pode ser contradição real, não duplicata. Fundir isso
  seria apagar evidência. REND- é exceção: identidade já é (fonte, corrida) → mantém.
  Enquanto o dono não decidir (D119), todo objeto novo sai com `ID_PROVISORIO`.

=========================================================================
9 · P8 — ANTES DE PUBLICAR HOJE (mínimo, reversível, nesta ordem)
=========================================================================
  1. Nada de migrar ID hoje. Nada de tabela nova hoje, se o dono preferir.
  2. Marcar `ID_PROVISORIO: true` em todo objeto (D119 já autoriza).
  3. A Intelligence calcula, no gerador do pote, um campo `GRUPO` = a chave-da-pergunta (F1/F2/F3/F4/F5) e o emite
     em cada objeto. O casco **só agrupa por esse campo** (é leitura, não cálculo — respeita INT-LAW-023/280).
     Efeito imediato e medido: as 13 fichas OLIVO×MOSCA_OLIVO viram 1 cartão; os 2 cartões de FOLPET×VITE viram 1;
     os 125 «competitors» viram poucos grupos. Isso ataca a «bagunça de duplicação» sem tocar em identidade.
     Regra de honestidade no cartão agrupado: mostrar «N provas, X não conferíveis» — nunca esconder que um
     documento não deu para ler.
  4. Não mexer em ROTULO_X_SUBSTANCIA além do GRUPO: o estado por produto (P4) é a correção seguinte, não a de hoje.
  5. Escrever o LIVRO em modo «sombra» (só escreve, ninguém lê) para a corrida de amanhã já poder medir DELTA
     sem risco para o portal de hoje.
  6. Teste mínimo que eu exigiria antes de dizer «pronto»: pegar as duas corridas R6 e R7 já existentes e provar
     por script (a) que os 43 objetos de mesmo conteúdo passam a ter 1 ID, (b) que 13→1 e 2→1 nos grupos, (c) que
     nenhuma fusão junta estados divergentes sem marcar contradição. Sem esse script medido, é promessa.
  Se o dono achar até isso arriscado hoje: entregar somente o passo 3 (GRUPO) — é o único que muda a tela, e é o
  mais fácil de desfazer (o casco volta a ler o pote sem agrupar).

=========================================================================
10 · RECOMENDAÇÃO EM 10 LINHAS
=========================================================================
1. Identidade do cruzamento = a PERGUNTA (família + chaves canônicas resolvidas + edição do dossiê), nunca a origem,
   nunca a corrida, nunca a ordem (é o que a INT-LAW-030/054 já manda; o código é que não obedece).
2. Documento/boletim, semana e produto autorizado são PROVA e RESPOSTA — não entram no ID.
3. Chave com NÃO SEI não funde: fica CHAVE_INCOMPLETA e aparece agrupada, com o número de casos ao lado.
4. Estado é função pura de (provas, edição do dossiê, relógio) e vive com histórico append-only de→para.
5. CONFIRMADO é resposta por produto (lista), não estado da pergunta — é o que corrige o folpet×vite.
6. Provas acumulam; contagem de independência por INSTITUIÇÃO (3 distritos = 1) e por conteúdo (notícia replicada = 1).
7. Livro de identidades append-only no Postgres existente (D104.1), escrito só pela Intelligence; pote continua 1
   por corrida, com LIVRO_HEAD e bloco DELTA.
8. Finding/Opportunity/Future referenciam o ID e são reavaliados por gatilho; nunca copiam a prova.
9. Migração é mapa reversível + IDS_HISTORICOS; colisão com estados divergentes = PARAR e perguntar ao dono.
10. Hoje: só ID_PROVISORIO + campo GRUPO + agrupamento no casco; o resto (livro, delta, migração) depois, medido.

=========================================================================
11 · ONDE POSSO ESTAR ERRADO
=========================================================================
a) Fundir por pergunta pode esconder diferença real: o FOLPET×VITE tem dois documentos (Arezzo e Cantina Negrar
   12/05) e a autorização é um fato por dossiê/edição. Se a edição do dossiê mudar entre os dois, os «dois cartões»
   são dois fatos verdadeiros — e fundir viraria mentira. Só o teste do passo 6 decide. [risco alto]
b) Não medi a Sala (38 sem `raw_document_key`, 13 documentos 2×) — isso é medição do coordenador, eu não reproduzi;
   se ali houver erro, a contagem de independência muda de base.
c) Não sei qual pote alimenta o portal hoje (47 objetos / 2 cruzamentos × 228 objetos de entrada). Se for o de 47, o
   problema mais urgente não é identidade: é publicação.
d) Não medi o custo: número de cruzamentos × edições de dossiê (D116) pode explodir a reavaliação; não calculo o
   volume de trabalho, então não afirmo que «cabe».
e) O LIVRO no Postgres é minha proposta, e D119 congela esquemas de ID até a conclusão. Eu li o congelamento como
   valendo para ID novo, não para histórico — mas quem decide isso é o dono, não eu.

Referências externas (padrões maduros, para o mesmo problema — observados, não copiados):
 - W3C PROV-O (proveniência como grafo, com atividade/entidade separados): https://www.w3.org/TR/prov-overview/
 - W3C Time Ontology (janelas como intervalos comparáveis): https://www.w3.org/TR/owl-time/
 - W3C Cool URIs (identificador estável de coisa, não de acesso): https://www.w3.org/TR/cooluris/
 - Delta Lake MERGE/upsert com chave determinística (foto + delta sobre chave estável): https://docs.delta.io/delta-update
 - Kimball SCD Type 2 (mesma entidade, versões datadas, histórico não apagado): https://kimballgroup.com/2008/08/slowly-changing-dimensions
 - Palantir Foundry — tipos de objeto e linkages com identidade declarada (o que o casco consome é objeto, não tela):
   https://palantir.com/docs/foundry/object-link-types/object-types-overview
 - Entity resolution determinística com chaves de bloqueio (fundir só com chave, não por parecença):
   https://cran.r-project.org/web/packages/blocking/blocking.pdf

Nota de fronteira (D109): isto é resposta de analista, não relatório do LAB. O bloco CONTENT_CLASSIFICATION
(KNOW_HOW / ITALIAN_AGRO_BRAIN / BIBLE_CHANGE / HANDOFF_ONLY) pertence à síntese do coordenador — eu não escrevo em
nenhuma das três casas.

=========================================================================
EM PALAVRAS SIMPLES
=========================================================================
Hoje o sistema dá nome a cada achado com base em «de onde veio e em que posição estava». Isso faz a mesma conclusão
nascer com nome diferente toda vez que roda de novo — por isso a mesma pergunta aparece repetida na tela (13
cartõezinhos para «olivo × mosca do olivo»; dois cartões para «o rótulo cobre folpet em videira?», um dizendo «não
consegui conferir» e outro dizendo «sim, dois produtos»).

O conserto é dar nome ao cruzamento pelo que ele PERGUNTA (cultura, praga, substância, lugar, época, edição da bula)
— e deixar o boletim, a semana e os produtos como prova e resposta, não como nome. Onde não se sabe (por exemplo,
não se sabe a cultura ligada à substância), o sistema não deve fingir que são a mesma coisa nem fingir que são coisas
diferentes: ele guarda como «chave incompleta» e mostra agrupado, dizendo quantos casos são.

Para hoje, antes do portal ir ao ar, o mínimo seguro é: não mexer nos nomes antigos, marcar os novos como
«provisórios» e mandar a Intelligence calcular um rótulo de grupo — o portal passa a mostrar 1 cartão por pergunta
em vez de 13. Isso é pequeno e dá para desfazer. O resto (livro de identidades, aviso de «atualizado desde ontem»,
migração dos nomes antigos) fica para depois, com um teste medido antes.

O que ainda falta medir e eu não consegui: qual arquivo de saída o portal de hoje realmente usa (um tem 2
cruzamentos, outro tem 228) — sem isso, não sei se o problema mais urgente é duplicação ou publicação.
