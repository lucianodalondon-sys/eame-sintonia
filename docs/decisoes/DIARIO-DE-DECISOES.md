# DIÁRIO DE DECISÕES — SINTONIA EAME

Registro cronológico de **toda** decisão que afeta o repositório: estrutura, método,
escopo, fonte, ferramenta, corte.

Regras do diário:

- Uma decisão por entrada, com **data**, **motivo** e **estado**.
- Decisão revertida **não se apaga**: abre-se nova entrada que a revoga, citando a original.
- Decisão tomada por falta de informação é marcada como **SUPOSIÇÃO ASSUMIDA** e vira
  pergunta pendente até ser confirmada por quem tem autoridade.
- Nenhuma decisão de produto é registrada aqui sem ter sido dada por quem decide.

**Formato:**

```
### D-000 — Título
- Data:
- Estado: DECIDIDO | SUPOSIÇÃO ASSUMIDA | REVOGADA (por D-000) | PENDENTE
- Contexto:
- Decisão:
- Motivo:
- Consequência:
- Quem decidiu:
```

---

### D-001 — Repositório próprio, sem herdar artefatos do Sintonia Brasil
- **Data:** 2026-08-28
- **Estado:** DECIDIDO
- **Contexto:** Existe um Sintonia Brasil em operação, com código, réguas, banco e classificadores.
- **Decisão:** O SINTONIA EAME nasce em repositório próprio e vazio. O Brasil entra apenas
  como referência metodológica. Não se copia código, régua instável, banco ou classificador,
  e não se altera o repositório brasileiro.
- **Motivo:** Realidade regulatória, fontes, idiomas e mercado da EAME são outros; herdar
  artefato pronto importaria pressupostos brasileiros não verificados na Europa.
- **Consequência:** Todo aproveitamento vindo do Brasil precisa de entrada própria neste diário.
- **Quem decidiu:** Enunciado da tarefa.

### D-002 — Estrutura inicial de pastas conforme sugerida
- **Data:** 2026-08-28
- **Estado:** DECIDIDO
- **Contexto:** Primeira tarefa é preparar a casa antes de pesquisar ou implementar.
- **Decisão:** Adotada a estrutura sugerida: `docs/` (01 a 08), `data/` (samples, raw,
  normalized), `research/` (europe, france, spain, italy, people, competitors),
  `prototype/portal`, `tests/`, `scripts/`.
- **Motivo:** A estrutura já reflete a cadeia SOURCE → … → PORTAL e o recorte por país.
- **Consequência:** Diretórios ainda sem conteúdo carregam `.gitkeep` para existirem no versionamento.
- **Quem decidiu:** Enunciado da tarefa.

### D-003 — `data/raw` e `data/normalized` fora do versionamento
- **Data:** 2026-08-28
- **Estado:** SUPOSIÇÃO ASSUMIDA
- **Contexto:** Não houve instrução sobre o que versionar dentro de `data/`.
- **Decisão:** `data/raw/` e `data/normalized/` ficam ignorados pelo Git (exceto os
  `.gitkeep`). `data/samples/` é versionado.
- **Motivo:** Bruto e normalizado tendem a ser grandes, refazíveis e sujeitos a licença de
  redistribuição; amostras pequenas com procedência são justamente o que precisa viajar
  junto com a evidência.
- **Consequência:** Evidência preservável de uma fonte deve ir para `data/samples/`, não
  para `data/raw/`. Se alguma fonte exigir versionar bruto, revogar esta entrada.
- **Quem decidiu:** Assumido na ausência de instrução — **confirmado** pela MISSÃO 02 §0 (P-001 encerrada).

### D-005 — Estrutura de `docs/` realinhada ao briefing da MISSÃO EAME 01
- **Data:** 2026-08-28
- **Estado:** DECIDIDO (revoga parcialmente D-002)
- **Contexto:** D-002 adotou `docs/01-descoberta` … `docs/08-decisoes`, com prefixos
  numéricos e uma pasta `06-arquitetura`. O briefing da MISSÃO EAME 01, recebido depois,
  especifica `docs/descoberta`, `fontes`, `capacidades`, `cruzamentos`, `ferramentas`,
  `decisoes`, `apresentacao` — sem prefixos e sem pasta de arquitetura — e diz
  "não criar estrutura adicional sem necessidade comprovada".
- **Decisão:** Pastas renomeadas para a forma do briefing; `06-arquitetura` removida.
- **Motivo:** O briefing da missão é a especificação vigente e é mais restritivo.
  Arquitetura não tem necessidade comprovada nesta fase.
- **Consequência:** Os caminhos de D-002 não valem mais. Se o desenho técnico precisar de
  lugar próprio mais adiante, abre-se nova entrada justificando a necessidade.
- **Quem decidiu:** Briefing MISSÃO EAME 01, §0 e §17.

### D-006 — Documentos canônicos como memória externa
- **Data:** 2026-08-28
- **Estado:** DECIDIDO
- **Contexto:** Instrução de modo de execução com economia de contexto.
- **Decisão:** Todo achado é gravado imediatamente no documento canônico correspondente,
  com a evidência preservada e commit próprio. Nada de inventário grande vivendo só no
  contexto da conversa. Checkpoints referenciam arquivo em vez de reproduzir conteúdo.
- **Motivo:** Evidência sobrevive à conversa; contexto não.
- **Consequência:** Prioridade operacional: EVIDÊNCIA > CONTEXTO, ARQUIVO > MEMÓRIA,
  MEDIÇÃO > EXPLICAÇÃO.
- **Quem decidiu:** Instrução do usuário (modo de execução).

### D-004 — Documentos-base criados como esqueleto, sem conteúdo inventado
- **Data:** 2026-08-28
- **Estado:** DECIDIDO
- **Contexto:** Os documentos de fontes, capacidades, cruzamentos, ferramentas e casos de
  apresentação foram pedidos antes de qualquer pesquisa.
- **Decisão:** Cada um nasce com propósito, regra de preenchimento e formato de ficha —
  e com o registro de fontes/capacidades **vazio**.
- **Motivo:** Preencher exemplos plausíveis antes de pesquisar violaria o princípio
  SOURCE → EVIDENCE e contaminaria o atlas com conteúdo que ninguém verificou.
- **Consequência:** Os atlas mostram zero registros. Isso é o estado correto da Fase 0.
- **Quem decidiu:** Enunciado da tarefa (princípio e regra).

### D-007 — Claude descobre o produto; Claude Design desenha o produto
- **Data:** 2026-08-28
- **Estado:** DECIDIDO
- **Contexto:** o protótipo da MISSÃO 02 provou que os dados sustentam blocos reais, mas
  continuar a desenvolvê-lo misturaria descoberta com design.
- **Decisão:** `prototype/portal` fica **congelado como artefato histórico** — não é
  desenvolvido, não é atualizado e **não é base de decisão**. A MISSÃO 03 passa a ser
  100% texto, dados, evidência e arquitetura conceitual de informação. Todo o trabalho
  visual vai para missão separada, com Claude Design.
- **Motivo:** o Design não deve precisar descobrir o produto; deve transformar uma
  arquitetura de informação já fechada em experiência visual.
- **Consequência:** o fluxo desta missão termina em INFORMATION REQUIREMENTS e **não**
  continua para UI, componente, página ou portal. O estado `PROTOTYPE` deixa de ser usado
  em ficha de ferramenta.
- **Quem decidiu:** cliente, redirecionamento de 2026-08-28.

---

### D-008 — A versão de que um change event depende é evidência, não dado bruto

- **Data:** 2026-08-29
- **Estado:** DECIDIDO (estende D-003, não o revoga)
- **Contexto:** D-003 mantém `data/raw` fora do versionamento. Mas a detecção de mudança
  só existe porque **duas versões do mesmo documento** estavam guardadas — e o contêiner
  onde elas estavam é efêmero. Se a versão de 28/05/2025 se perder, o evento
  `MAXENTIS → SORATEL MAX` deixa de ser verificável por qualquer pessoa, inclusive por nós.
- **Decisão:** dado bruto continua fora do versionamento, **exceto** a versão específica de
  que um `CHANGE EVENT` publicado depende. Essa versão vai para `data/samples/`, com o nome
  carregando a data da versão e um `LEIA-ME.md` declarando SHA-256 e como reproduzir.
- **Motivo:** evidência que não sobrevive ao contêiner não é evidência.
- **Consequência:** `data/samples/ES-T4-004-versoes/` (2 PDFs, 581 KB) e
  `data/samples/ES-T4-005/ropf_20260829.json.gz` (projeção, 147 KB) passam a ser
  versionados. A projeção guarda só os campos que entram em change event — não o export
  inteiro de 14 MB.
- **Quem decidiu:** decisão técnica da MISSÃO 07, registrada para revisão.

---

### D-009 — Número declarado tem de ser número derivado

- **Data:** 2026-08-29
- **Estado:** DECIDIDO
- **Contexto:** o fim da MISSÃO 06 deixou `37/37` num relatório e `38/38` na mensagem do
  commit `e37911a`. A suíte tinha 37. Nenhum dos dois números era derivado da suíte — os
  dois eram digitados.
- **Decisão:** todo total publicado num documento canônico tem de ter uma prova que o
  derive da coisa contada. Vale para: total de testes, placar do benchmark, contagens de
  fontes, números de denominações.
- **Motivo:** um número digitado diverge em silêncio; um número derivado quebra o teste.
- **Consequência:** `tests/test_canonico.py` ganhou
  `test_o_total_de_testes_declarado_vem_da_suite` (conta a suíte com
  `unittest.defaultTestLoader.discover`), o placar do benchmark passou a ser lido do JSON,
  e as contagens de denominação passaram a ser comparadas com o arquivo de medida.
- **Quem decidiu:** decisão técnica da MISSÃO 07.

---

### D-010 — Cobertura menor e declarada vence cobertura maior e silenciosa

- **Data:** 2026-08-29
- **Estado:** DECIDIDO
- **Contexto:** para separar as colunas coladas da lista de *denominaciones comunes* foram
  testadas duas regras. A heurística "cortar na primeira forma jurídica" resolveu **96,9%**
  das linhas — e produziu `INDUSTRIAS A` + `FRASA, S.A.` e `ECOLOGIA Y PROTECCION AG` +
  `RICOLA`. A regra ancorada em fontes externas (nome oficial do produto e vocabulário de
  titulares, ambos do export do ROPF) resolve **68,8%** e erra zero nas linhas que resolve.
- **Decisão:** fica a regra de 68,8%. O restante fica `UNRESOLVED`, com o motivo por linha.
- **Motivo:** erro silencioso é pior do que lacuna declarada. Uma tabela plausível e falsa
  passa pela revisão; uma lacuna não passa.
- **Consequência:** a cobertura é publicada junto com o número, sempre.
- **Quem decidiu:** decisão técnica da MISSÃO 07.

---

### D-011 — Toda cadeia declara os seus passos por natureza

- **Data:** 2026-08-29
- **Estado:** DECIDIDO
- **Contexto:** até a MISSÃO 07 a coleta estava em script e a **análise** estava na cabeça
  de quem a fez. Um engenheiro novo conseguia baixar o E-Phy e não conseguia chegar a
  "77 produtos, ADAMA 3". O RAIF era pior: a troca de host que faz o download funcionar
  estava em prosa no atlas.
- **Decisão:** toda cadeia que produz um fato do piloto vive em `scripts/chain.py` e
  declara cada passo como `AUTOMATIC`, `MANUAL` ou `HUMAN_JUDGMENT`.
- **Motivo:** o objetivo não é zerar julgamento humano — é saber **onde ele está**.
  Um dicionário de grupo empresarial não é dado; é decisão nossa, e move números.
- **Consequência:** as quatro cadeias somam 17 passos automáticos, **0 manuais** e 5 de
  julgamento. Toda contagem por grupo sai acompanhada da contagem por **entidade legal**,
  que não depende de dicionário nenhum.
- **Quem decidiu:** decisão técnica da MISSÃO 08.

---

### D-012 — Falhar fechado, sempre; e rebaixamento nunca é silencioso

- **Data:** 2026-08-29
- **Estado:** DECIDIDO
- **Contexto:** um pipeline que degrada tem duas saídas possíveis: parar, ou entregar um
  número menor com a mesma cara de sempre. A segunda é a que destrói confiança.
- **Decisão:** `HTTP 200` não basta para `HEALTHY` — exige schema completo, identidade
  única e conteúdo. Lista vazia é `FAILED`, nunca "zero resultados". Cobertura abaixo do
  piso **levanta**. E quando algo é rebaixado para funcionar — como aceitar `SECLEVEL=1`
  no TLS do host italiano — o rebaixamento é **registrado como passo da cadeia**.
- **Motivo:** "não consegui ver" e "não há nada" produzem o mesmo número e significam o
  oposto.
- **Consequência:** 11 formas de degradação testadas; nenhuma produz número errado.
  Verificação de certificado **nunca** é desligada — há teste que proíbe `CERT_NONE` e
  `check_hostname = False` no código das cadeias.
- **Quem decidiu:** decisão técnica da MISSÃO 08.

---

### D-013 — Creator e sensor são dois papéis, e nunca uma ficha só

- **Data:** 2026-08-30
- **Estado:** DECIDIDO
- **Contexto:** a MISSÃO 14 pergunta *"quem já fala com esse público?"*; o EARLY SIGNAL
  pergunta *"quem enxerga o problema primeiro?"*. A mesma pessoa pode servir às duas, e a
  tentação de somar as duas num "score de pessoa" é imediata.
- **Decisão:** contratos separados. `SENSOR_ROLE_LINK` é **ponteiro**, nunca fusão, e
  nenhum campo do mapa de creators herda valor do universo de sensores.
- **Motivo:** um pesquisador com âncora ORCID é sensor excelente e pode ser canal inútil;
  um creator com 400 mil seguidores pode ser canal excelente e sensor inútil. Uma lista
  somada não responde a nenhuma das duas perguntas.
- **Consequência:** `test_papel_de_sensor_e_ponteiro_nunca_campo_fundido` proíbe
  `SENSOR_SCORE`, `AUTHORITY_SCORE`, `INFLUENCE_SCORE` e `RANK` no contrato.
- **Quem decidiu:** decisão técnica da MISSÃO 14.

---

### D-014 — Produto final não prova lavoura

- **Data:** 2026-08-30
- **Estado:** DECIDIDO
- **Contexto:** uma seed externa de 25 creators italianos trouxe críticos de vinho e
  sommeliers de azeite catalogados como candidatos de **viticultura** e **olivicultura**,
  e um **garden designer** catalogado em **fruticultura**.
- **Decisão:** `WINE_RELEVANCE` ≠ `VITICULTURE_RELEVANCE` e `OLIVE_OIL_RELEVANCE` ≠
  `OLIVE_GROWING_RELEVANCE`, em campos distintos. `CROP_STATE` ganha o estado
  `WRONG_ASSIGNMENT` — "provei que não é" não é a mesma coisa que "não consegui provar".
- **Motivo:** o custo é comercial, não semântico. Uma ativação de fungicida de videira
  entregue a uma audiência de consumidores de vinho fala com quem nunca comprará o
  produto — e o número de seguidores faria isso parecer sucesso. **Medido:** os cinco
  maiores perfis da seed somam ~452 mil seguidores e **quatro são mídia de vinho**.
- **Consequência:** 3 dos 10 candidatos validados saíram `WRONG_ASSIGNMENT`.
- **Quem decidiu:** decisão técnica da MISSÃO 14.

---

### D-015 — Suspeita nossa nunca vira veredito sozinha

- **Data:** 2026-08-30
- **Estado:** DECIDIDO
- **Contexto:** o portão levanta `SUSPECTED_CHAIN_MISMATCH` por léxico do handle
  (`wine`, `evo`, `oil`, `sommelier`, `garden`). Foi tentador deixá-lo rebaixar sozinho.
- **Decisão:** a suspeita **prioriza a checagem** e nunca promove a `WRONG_ASSIGNMENT`.
- **Motivo:** ela **errou**. `@evolovers` foi suspeito por *"EVO = azeite, produto
  final"*; a medição mostrou um **produtor pugliês** cuja comunidade nasceu de podas e
  colheitas no próprio olival. Um portão que confiasse na suspeita teria descartado o
  melhor olivicultor da lista pelo nome do handle — cometendo, do lado cético, o mesmo
  erro que a seed cometeu do lado otimista.
- **Consequência:** `SUSPICION_OUTCOME` registra `CONFIRMED` / `REFUTED_BY_EVIDENCE` por
  candidato. Nesta rodada: 3 confirmadas, 1 refutada.
- **Quem decidiu:** decisão técnica da MISSÃO 14.

---

### D-016 — Empresa de defensivo usando creator ≠ ativação de produto fitossanitário

- **Data:** 2026-08-30
- **Estado:** DECIDIDO
- **Contexto:** a pergunta do dono era binária — *farmfluencers são usados para crop
  protection na Europa?* Os quatro casos encontrados são todos de empresas de defensivo
  (BASF, Seipasa, Syngenta, Bayer) contratando creators — mas **nenhum** promove um
  produto fitossanitário.
- **Decisão:** três estados por país. `PROVED` exige peça de **categoria** crop protection
  **com mensagem de produto**; `PARTIAL` cobre empresa de defensivo usando creator para
  imagem, setor ou evento; `NOT_TESTED` nunca se confunde com `NOT_PROVED`.
- **Motivo:** colapsar os dois faria a ADAMA concluir que a faixa de ativação de produto
  já está ocupada — quando ela está, nesta medição, **vazia nos três países**. A diferença
  entre "o mercado existe" e "esta faixa do mercado existe" é a decisão inteira.
- **Consequência:** ES `PARTIAL` (3 casos) · FR `PARTIAL` (1) · IT `NOT_PROVED`. E o caso
  francês registra o custo reputacional: a creator encerrou a parceria após investigação
  de dois veículos independentes.
- **Quem decidiu:** decisão técnica da MISSÃO 14.

---

### D-017 — No runner Windows, urllib no lugar de curl

- **Data:** 2026-08-30
- **Estado:** DECIDIDO
- **Contexto:** `coletor._curl` chama `curl` por subprocess. No runner residencial isso
  devolveu **stdout vazio de forma intermitente**, e `json.loads(None)` virou um
  `TypeError` que não diz nada sobre a causa. Medido no mesmo endpoint, com a mesma
  chave: 21:53 OK · 21:56 falha · 22:00 OK (subprocess direto) · 22:02 falha nos três
  atores.
- **Decisão:** `creator_coleta.py` substitui `coletor._curl` por uma implementação
  `urllib`. A troca é por **substituição**, não por desvio: RAW antes de normalizar,
  `RUN_MANIFEST`, `ACTOR_VERSION` e `COST_USD` continuam passando pela porta única.
- **Motivo:** "a plataforma recusou" e "o subprocesso não entregou saída" produzem o mesmo
  `FAILED` com causas opostas. Sem processo filho, sem pipe e sem shell, a classe inteira
  do defeito desaparece — e `speaker_universo.py` já provava que urllib funciona na
  máquina.
- **Consequência:** a fase seguinte resolveu **25 de 25** perfis por **US$ 0,0624**.
  Resposta vazia agora é estado com mensagem, nunca `TypeError` mudo.
- **Quem decidiu:** decisão técnica da MISSÃO 14.

---

### D-018 — Ausência observada num corpus não é ausência no mercado

- **Data:** 2026-08-30
- **Estado:** DECIDIDO — **corrige uma afirmação publicada pela própria missão**
- **Contexto:** a rodada 1 publicou que a faixa de ativação de produto fitossanitário
  estaria livre nos três países, e a chamou de espaço livre. O que havia sido medido era
  outra coisa: nenhuma evidência **dentro de um corpus pequeno e enviesado** — pesquisa
  aberta por buscador mais **uma** rota de Instagram.
- **Decisão:** o estado passa a se chamar `NOT_OBSERVED_IN_MEASURED_CORPUS`, e o veredito
  viaja com dois campos obrigatórios: `ESTE_ESTADO_NAO_SIGNIFICA` e `CORPUS_MEDIDO`.
- **Motivo:** `NOT_PROVED` é curto, e **por ser curto foi lido como "não existe"**. O nome
  novo não cabe numa manchete — que é exatamente o ponto: obriga quem o cita a carregar o
  escopo junto. A ressalva vive **dentro do JSON** para não se perder entre o dado e o
  slide.
- **Consequência:** teste proíbe **afirmar** a frase extrapolada em documento — por linha,
  aceitando-a quando aparece sendo negada, para que a própria correção possa ser escrita.
- **Quem decidiu:** correção pedida pelo dono da missão, aplicada na MISSÃO 14 rodada 2.

---

### D-019 — Tipo de relação com marca não é escada

- **Data:** 2026-08-30
- **Estado:** DECIDIDO
- **Contexto:** patrocinar a categoria de um prêmio, colaborar num evento, colaborar com a
  pessoa, pagá-la e ativar um produto com ela são cinco fatos distintos. Modelá-los como
  degraus de uma mesma régua era conveniente e falso.
- **Decisão:** `TIPOS_DE_RELACAO` é um `frozenset` — **sem índice**. A FORÇA da evidência
  (`BRAND_RELATIONSHIP_STATE`) e o TIPO da relação (`BRAND_RELATION_TYPE`) passam a ser
  dimensões separadas.
- **Motivo:** num contínuo, *"a Syngenta patrocinou uma categoria do AgroInfluye"* vira,
  três leituras depois, *"a Syngenta ativa produto com creators"*. O `frozenset` torna a
  comparação de ordem impossível, e um teste guarda a propriedade.
- **Consequência:** os 4 casos de crop protection ficam legíveis pelo que são: 2
  patrocínios de ecossistema, 1 colaboração e 1 parceria paga — **nenhuma ativação de
  produto**.
- **Quem decidiu:** decisão técnica da MISSÃO 14 rodada 2.

---

### D-020 — Namespace, não lock, para missões concorrentes

- **Data:** 2026-08-30
- **Estado:** DECIDIDO
- **Contexto:** EARLY SIGNAL e CREATOR MAP rodaram ao mesmo tempo escrevendo no mesmo
  `RUN-MANIFEST.json`.
- **Decisão:** cada missão tem manifesto próprio. `pv.MANIFESTO` é redirecionado pelo
  módulo da missão; o `coletor` continua sendo a porta única. O workflow declara
  `concurrency` por missão e faz `git add` de **caminhos nomeados**, nunca `-A`.
- **Motivo:** não era corrida improvável — era **corrida garantida**: `pv.gravar()` lê
  tudo, junta e reescreve o arquivo inteiro, então quem terminasse por último apagaria o
  outro. Lock resolveria a escrita e não resolveria o commit; namespace remove o ponto de
  disputa inteiro. E `git add -A` num runner podia levar, num commit desta missão, um
  arquivo que a outra estava gravando.
- **Consequência:** paralelismo entre missões continua permitido, que era o objetivo.
- **Quem decidiu:** decisão técnica da MISSÃO 14 rodada 2.

---

### D-021 — Identidade primária antes de conteúdo, sempre

- **Data:** 2026-08-30
- **Estado:** DECIDIDO
- **Contexto:** `ACTIVATION_READY = 0` tinha causa única e nomeada: identidade não
  resolvida em fonte primária. A tentação era coletar mais conteúdo.
- **Decisão:** resolver identidade dos candidatos de maior valor **antes** de coletar mais
  um único post.
- **Motivo:** os quatro prioritários falharam de **quatro maneiras diferentes** — handle
  errado, nome errado, pessoa≠persona e pessoa≠empresa. Coletar conteúdo antes teria
  produzido um dossiê inteiro sobre a pessoa errada, com precisão e tudo. O caso decisivo:
  `@evolovers`, o handle da seed, está parado desde **2012**; a comunidade real nasceu em
  2020.
- **Consequência:** `ACTIVATION_READY` foi de 0 para 2, e os dois só existem porque o
  handle foi corrigido antes de medir. Custo total da rodada Apify: **≈ US$ 0,13**.
- **Quem decidiu:** decisão técnica da MISSÃO 14 rodada 2.

---

### D-022 — Hub bom é o que revela gente, não o que tem prestígio

- **Data:** 2026-08-30
- **Estado:** DECIDIDO
- **Contexto:** 43 hubs registrados, 34 intocados, e nenhum critério para escolher por
  onde começar além da asserção do dono.
- **Decisão:** `HUB_YIELD` mede pessoas úteis reveladas: `PEOPLE_DISCOVERED` →
  `IDENTITIES_PROVED` → `CROP_FIT_PROVED` → `ACTIVATION_READY`, e daí
  `VALID_CREATORS_PER_HUB`.
- **Motivo:** medido nesta rodada — **12 publicações da conta de um prêmio renderam 23
  pessoas, 17 válidas e 4 prontas; uma lista externa de 25 handles rendeu 0 válidas.**
  Nenhuma medida de tamanho, prestígio ou número de páginas teria previsto isso.
- **Consequência:** `INVALID` passa a significar *fora do recorte* (outro país, pecuária,
  patrocinador) — nunca "pessoa ruim"; todos seguem registrados.
- **Quem decidiu:** decisão técnica da MISSÃO 14 rodada 3.

---

### D-023 — Menção em hub não dá país, nem papel, nem cultura

- **Data:** 2026-08-30
- **Estado:** DECIDIDO
- **Contexto:** a extração por menções é barata e generosa demais: a conta de um prêmio
  menciona nomeados, patrocinadores, o local e a própria organizadora.
- **Decisão:** menção é **rota de descoberta**. País, papel e cultura continuam saindo de
  evidência própria — de preferência da bio pública da pessoa, com
  `DECLARATION_TYPE = SELF_DECLARED_PUBLIC_PROFILE`.
- **Motivo:** medido — `@la_huerta_malagon` escreve *"Guanajuato"* (México) e
  `@ironfarmer_rc` escreve *"ÉVORA/PORTUGAL"*; o prêmio espanhol criou categoria LATAM.
  Herdar o país do hub teria posto **dois estrangeiros no mapa espanhol**. E
  `@santander_es` — um banco — apareceu como se fosse creator.
- **Consequência:** `NAO_E_CREATOR` é lista curta e explícita do que já foi conferido, não
  um filtro esperto.
- **Quem decidiu:** decisão técnica da MISSÃO 14 rodada 3.

---

### D-024 — Pecuária sai do mapa vegetal sem sair da base

- **Data:** 2026-08-30
- **Estado:** DECIDIDO
- **Contexto:** a **grande vencedora** do AgroInfluye 2026 — `@luciiaacasal`, que levou
  Maquineros e Melhor Creator Agro — declara *"Ganaderia Casal Vazquez SC"*.
- **Decisão:** `LIVESTOCK_CREATOR = YES` retira do mapa de proteção de cultivo **vegetal**
  e entra em `LIVESTOCK_SEPARATE_MAP`. Não é descarte.
- **Motivo:** a melhor creator do prêmio não serve a uma ativação de fungicida de videira,
  e mantê-la no mesmo mapa faria o topo da lista responder à pergunta errada. Mas
  descartá-la perderia três creators fortes para o dia em que houver mapa de pecuária.
- **Consequência:** 3 creators listados à parte, prontos para esse mapa.
- **Quem decidiu:** decisão técnica da MISSÃO 14 rodada 3.

---

### D-025 — Conta de empresa agrícola não é creator-pessoa

- **Data:** 2026-08-30
- **Estado:** DECIDIDO — **corrige uma contagem publicada pela própria missão**
- **Contexto:** `@biocampojoyma` foi corretamente medido como conta de empresa e mesmo
  assim entrou numa frase de entrega como *"três produtores reais"*. O dado estava certo;
  a soma, errada.
- **Decisão:** campo `ACTIVATION_ENTITY_TYPE` de lista fechada, e **duas listas de saída**:
  `PERSON_CREATORS_ACTIVATION_READY` e `FARM_BUSINESS_PARTNERS_READY`.
- **Motivo:** uma exploração com canal forte é um parceiro comercial excelente — e isso é
  **outra relação**, com outro contrato, outro interlocutor e outro preço. Contá-la como
  creator-pessoa infla o número que o Marketing usa para planear elenco.
- **Consequência:** 7 pessoas + 2 empresas, nunca somadas. Quatro testes de regressão.
- **Quem decidiu:** correção pedida pelo dono, aplicada na MISSÃO 14 rodada 4.

---

### D-026 — Cultura casa por palavra inteira, nunca por substring

- **Data:** 2026-08-30
- **Estado:** DECIDIDO — **corrige uma medição errada da própria missão**
- **Contexto:** a primeira prova de cultura por conteúdo devolveu **8 `PROVED`**. Lendo o
  resultado com desconfiança, **seis eram falsos**: `riz` casava dentro de *nariz* e
  *matriz*; `mais` (milho em italiano) casava com o *mais* **português** de um perfil de
  Évora, que saiu "MAIZE PROVED".
- **Decisão:** casamento por palavra inteira, com acentos normalizados, e **remoção** dos
  termos curtos ambíguos.
- **Motivo:** era literalmente o erro que o meu próprio código **citava** do
  `speaker_universo` — consulta frouxa traz outra população com cara de sucesso. Um termo
  que precisa de contexto para não errar não é termo, é palpite; por isso foi removido em
  vez de "melhorado".
- **Consequência:** 8 → 2 `PROVED`. E uma segunda lei junto: para audiência de consumidor,
  mencionar a cultura prova **assunto**, não lavoura (`CROP_TOPIC_ONLY`).
- **Quem decidiu:** decisão técnica da MISSÃO 14 rodada 4.

---

### D-027 — Isolamento de namespace é inteiro ou não é

- **Data:** 2026-08-30
- **Estado:** DECIDIDO
- **Contexto:** a rodada 3 moveu o **manifesto** da missão para o seu namespace mas deixou
  o **bruto** em `data/samples/raw-paid/`, partilhado. A suíte quebrou — e quebrou com
  razão: os testes da casa exigem que todo arquivo daquele diretório resolva pelo
  manifesto global.
- **Decisão:** `coletor.RAW_DIR` também aponta para o namespace da missão. A única execução
  anterior ao isolamento foi migrada do manifesto global para o da missão, com o caminho
  corrigido.
- **Motivo:** um bruto sem manifesto que o alcance é um **arquivo órfão**. Ou os dois são
  globais, ou os dois são da missão — meio isolamento produz exatamente a inconsistência
  que o manifesto existe para impedir.
- **Consequência:** medido por **diferença de conjuntos**, não por impressão: as falhas que
  eu introduzira eram exatamente duas, e saíram. O baseline subiu de 9 para 11+1 por
  commits da missão Early Signal, ativa no mesmo branch — nenhuma referencia arquivo meu.
- **Quem decidiu:** decisão técnica da MISSÃO 14 rodada 4.

---

## PERGUNTAS PENDENTES

| # | Pergunta | Bloqueia | Aberta em |
|---|---|---|---|
| P-001 | ~~Confirmar D-003~~ — **resolvida** pela MISSÃO 02 §0: não versionar dumps grandes, amostras em `data/samples`, bruto temporário em `data/raw` local. | — | resolvida 2026-08-28 |
| P-002 | Quem é a audiência da apresentação e qual a data-alvo? | `07-apresentacao` | 2026-08-28 |
| P-003 | Que dados internos da ADAMA EAME estarão disponíveis? | `02-fontes` | 2026-08-28 |
| P-004 | Idioma exigido nos entregáveis finais? | Todos os docs | 2026-08-28 |
| P-005 | Restrições jurídicas / GDPR / licença aplicáveis ao uso pretendido? | `fontes`, `capacidades` | 2026-08-28 |
| P-006 | Criar conta institucional EPPO para obter token da API (EU-T3-001)? É gratuita, mas fica em nome de alguém. | EU-T3-001 | 2026-08-28 |
| P-009 | Obter chave da YouTube Data API e decidir se a ADAMA quer perfilar criadores individuais (T8). Questão de GDPR distinta da de T5. | T8 inteiro | 2026-08-28 |
| P-008 | Perfilamento de pesquisadores identificados (EU-T5-001/OpenAlex): revisão GDPR antes de qualquer tela que liste pessoas nomeadas. | T6, people graph, protótipo | 2026-08-28 |
| P-007 | Uso e difusão de coordenadas de parcela do RAIF (ES-T3-001): revisão jurídica antes de expor em tela externa. | ES-T3-001, protótipo | 2026-08-28 |
