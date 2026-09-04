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

---

### D-013 — Uma rota gratuita que deixa de ser gratuita é falha de fonte, não falha do país

- **Data:** 2026-09-04
- **Estado:** DECIDIDO
- **Contexto:** o `speaker_universo.py` descreve o OpenAlex como "rota REST gratuita, sem
  chave". Na camada de sensores humanos italiana, os 25 recortes devolveram `HTTP 429` com
  `{"error":"Rate limit exceeded","message":"Insufficient budget... you only have $0
  remaining","retryAfter":49093,"dailyRemainingUsd":0}` — preço por requisição e orçamento
  diário zerado, com e sem `mailto`.
- **Decisão:** o OpenAlex sai como `FAILED_WITH_REASON` com a resposta preservada; os 25
  recortes saem `THROTTLED_NOT_EMPTY` e **nenhum com zero**. A rota substituta é o
  **Europe PMC** (`scripts/sensor_epmc_it.py`), declarada como substituta no próprio
  artefato, com o motivo da substituição dentro.
- **Motivo:** `SOURCE FAILURE != ZERO`. Um recorte que devolve zero por falta de crédito é
  indistinguível de um recorte sem pesquisadores — e a segunda leitura seria falsa.
- **Consequência:** a premissa "OpenAlex é grátis" deixa de valer no repositório. Qualquer
  missão futura que dependa dela precisa testar antes, não presumir. O Europe PMC entrega
  algo que o OpenAlex não dava tão diretamente: a **string de afiliação por autor**, com a
  cidade dentro — e daí sai `REGION` com base declarada.
- **Quem decidiu:** decisão técnica da missão de sensores humanos IT.

---

### D-014 — Afiliação decide domínio; o assunto do trabalho não decide

- **Data:** 2026-09-04
- **Estado:** DECIDIDO
- **Contexto:** consultas por `aflatoxin`, `deoxynivalenol`, `Monilinia` e `fungicide
  resistance` trouxeram para o corpus italiano gastroenterologia do Policlinico Gemelli
  (12 autores), Istituto Zooprofilattico (8), Human Nutrition de Parma (8) e Veterinária
  de Messina (7). Autores reais, italianos, do assunto — e não sensores agrícolas.
- **Decisão:** portão **positivo** de afiliação: a string precisa **declarar** domínio
  agronômico. Ausência de marcador vira `NOT_DECLARED` e a pessoa **não é promovida**.
  2.480 candidatos recusados por ele.
- **Motivo:** é o `MODELO-DE-IDENTIDADE-EAME` aplicado à afiliação — papel sai de campo
  declarado, nunca do assunto do trabalho. Micotoxina chega ao paciente; isso não põe o
  gastroenterologista no campo.
- **Consequência e o erro medido:** a primeira versão do portão barrou **Vittorio Rossi**
  ("Sustainable Crop Production" / "Plant Health Modelling"), **A. F. Logrieco**
  ("Institute of Sciences of Food Production (ISPA)") e **Nicola Mori** ("Department of
  Biotechnology"). Os dois primeiros entraram acrescentando termos **específicos**
  (`crop production`, `plant health`, `ispa`) — nenhum departamento médico se chama assim.
  O terceiro entrou por dono canônico: já estava no `SPEAKER-UNIVERSE-PILOT-V1` com
  `IDENTITY_PROVED` por ORCID, e barrá-lo seria o registro desconhecendo a própria prova.
  **A exceção não afrouxa o portão — ela reconhece prova anterior**, e sai marcada como
  `TECHNICAL_AUTHORITY = PROVED_BY_CANONICAL_OWNER`.
- **Quem decidiu:** decisão técnica da missão de sensores humanos IT.

---

### D-015 — Cobertura exige duas famílias de origem, não dois nomes

- **Data:** 2026-09-04
- **Estado:** DECIDIDO
- **Contexto:** a matriz `CROP × REGION × SPECIALTY` precisava de uma régua para `GOOD`,
  `WEAK` e `NONE`. Contar sensores por célula seria o caminho óbvio e estaria errado.
- **Decisão:** `GOOD` exige **≥2 sensores Tier A/B em ≥2 `INDEPENDENCE_GROUP` distintos**.
  Uma célula coberta por cinco nomes do mesmo instituto é `WEAK` **por construção**.
- **Motivo:** três pessoas do mesmo laboratório não são três fontes independentes. Sem
  isto, a matriz mediria produtividade institucional e chamaria o resultado de cobertura.
- **Consequência:** 117 células → `GOOD` 72 · `WEAK` 29 · `NONE` 16. E o achado que a régua
  tornou visível: **`CEREAL` não tem uma única célula `GOOD`**, justamente onde a ADAMA
  Itália tem 26 registros de herbicida em vigor. A causa é da rota — `CEREAL|GRASS_WEEDS`
  devolveu 21 hits no Europe PMC contra 791 de `VINE|FLAVESCENCE_DOREE` — e a resposta é
  **outra rota**, não um limiar mais frouxo na mesma.
- **Quem decidiu:** decisão técnica da missão de sensores humanos IT.

---

### D-016 — Recomendação de monitoramento é guardada; agendamento não é criado

- **Data:** 2026-09-04
- **Estado:** DECIDIDO
- **Contexto:** os 224 sensores qualificados têm `MONITORING_RECOMMENDATION` (`WEEKLY` 37,
  `MONTHLY` 154, `EVENT_DRIVEN` 2, `DISCOVERY_ONLY` 31). Havia a tentação de ligar isso a
  um agendador.
- **Decisão:** a recomendação é **gravada** e nada é agendado. `READY FOR CONTINUOUS
  MONITORING = NO`.
- **Motivo:** não há executor — nem chave de coleta (`APIFY_TOKEN` ausente), nem dono da
  arquitetura de agendamento. Declarar `YES` seria chamar de capacidade uma tabela.
- **Consequência:** a camada entrega dado canônico para ingestão posterior, e o veredito
  publicado é `PARTIAL`, com as três razões nomeadas no documento da missão.
- **Quem decidiu:** decisão técnica da missão de sensores humanos IT.

---

### D-017 — O contrato de fonte é do Brasil; a Itália traduz, não inventa

- **Data:** 2026-09-04
- **Estado:** DECIDIDO
- **Contexto:** a camada de sensores humanos italiana nasceu com taxonomia própria
  (`SENSOR_ID`, `SENSOR_TYPE`, `ENTITY_KIND`). O `portal-sintonia` (Sintonia Brasil) já tem
  o contrato: `entidades` (QUEM É) · `fontes` (ONDE EU BATO) · `documentos.fonte_id`, com
  `fontes.tipo` de 20 valores (`tipos-de-fonte.sql:38-66`) e as cinco famílias humanas de
  `vozes-do-acervo.py:128-140`.
- **Decisão:** a Itália **mapeia para os 20 valores existentes**, grava o esquema italiano
  **ao lado como proveniência**, e deixa **NULO** o que não couber. Nenhum valor novo.
  Executado em `scripts/sensor_mapear_brasil.py` → `MAPA-BRASIL.json`.
- **Motivo:** `CENSO-DA-IDENTIDADE-ANALITICA.md:277` avisa *"taxonomia PARALELA — ⛔ NÃO
  criar uma terceira"*. O Brasil já tem três; a Itália tinha criado uma quarta.
- **Consequência medida:** 224 "sensores" = **190 entidades + 115 fontes**. Eles nunca
  foram 224 origens. E **dez dos 20 tipos brasileiros a Itália não usa** — entre eles
  `revenda`, `distribuidor`, `comercial` e `comite_tecnico`, que são rotas ausentes.
- **Limite herdado, declarado:** o vocabulário de classificação brasileiro é PT-BR
  chumbado em regex e **não transfere**. A Itália herda o CONTRATO e **não** os
  classificadores.
- **Quem decidiu:** decisão técnica da missão Brasil → Itália.

---

### D-018 — Identificador é prova-entre-várias, nunca catraca de entrada

- **Data:** 2026-09-04
- **Estado:** DECIDIDO · **corrige D-014 e a régua da missão anterior**
- **Contexto:** o portão italiano rejeitava pesquisador sem ORCID, citando
  `REGRA-DE-COLETA §17`. Medido no Brasil: **não existe coluna de ORCID nem de Lattes**,
  não há CHECK e não há validação de formato. ORCID aparece **uma vez** em todo o
  repositório, como valor de `fontes.url`. Nas 36 linhas de cadastro de pesquisador de
  07/08, das 35 URLs legíveis: 29 página institucional, 3 Lattes, **1 ORCID (2,9%)**,
  1 Scholar.
- **Decisão:** identidade é o **endereço observável da conta na plataforma**
  (`fontes.external_id`, dono único em `identidade_da_conta.py:69-104`). ORCID, Lattes,
  Scholar e página institucional entram **pela mesma porta**. A ausência de ORCID passa a
  ser um **estado**, nunca uma rejeição.
- **Motivo:** `§17` é intitulado *VIDEO × SCIENCE* e trata de **construir o crosswalk**;
  ele mesmo mede que *"as plataformas públicas não publicam nenhum dos dois"*. Exigir
  ORCID de produtor, técnico ou creator tornaria essas famílias impossíveis por
  construção — o oposto do que a camada existe para fazer.
- **Consequência:** o gate italiano funde **qualidade de identidade** com **capacidade de
  crosswalk automático**. É defeito estrutural, registrado e **não corrigido em silêncio**.
  Sete pesquisadores foram barrados só por isso.
- **Quem decidiu:** decisão técnica da missão Brasil → Itália.

---

### D-019 — Nome nunca é chave de operação

- **Data:** 2026-09-04
- **Estado:** DECIDIDO
- **Contexto:** `SENSOR_ID = sha1(NOME|ORGANIZAÇÃO)[:10]`. A lei brasileira é
  *"nome é atributo de tela, nunca chave de operação"*, com **trava por AST**
  (`provar-fonte-por-id.py:96,144-167`), nascida de um defeito que deixou *"quatro das
  cinco frentes de YouTube vermelhas por dias"*.
- **Decisão:** o `SENSOR_ID` derivado de nome é **defeito**, e a substituição é o par
  brasileiro: id operacional opaco + `external_id` derivado do **endereço**.
- **Consequência medida — 5 de 8 casos adversariais quebram:** travessão U+2010, espaço
  duplo, inicial vs nome por extenso, nome do meio, e **mudança de instituição** produzem
  ids diferentes para a mesma pessoa; homônimo na mesma organização **colide**.
  Hoje há 0 duplicatas reais e 224 ids únicos **porque houve uma rota numa execução só** —
  a instabilidade é latente e dispara na segunda rota.
- **Agravante:** o próprio repositório italiano já normaliza o travessão U+2010 em
  `sensor_canal_identidade.py` e `speaker_identidade.py::_chave()`. O `SENSOR_ID` não
  reusou o contrato que a casa já tinha.
- **Quem decidiu:** decisão técnica da missão Brasil → Itália.

---

### D-020 — Origem, papel e canal são três coisas; papel é multivalorado

- **Data:** 2026-09-04
- **Estado:** DECIDIDO
- **Contexto:** o registro italiano guarda origem e canal na mesma linha e um papel único.
  Medido: **Fondazione Edmund Mach conta duas vezes** (`web:fmach.it` e
  `youtube:@fondazionemach`) — no contrato brasileiro é `MESMA_ENTIDADE`, uma entidade e
  duas fontes. E só 16 de 224 têm mais de um papel, **todos vindos de `AMBIGUOUS:`** —
  multivaloração real é **zero**.
- **Decisão:** `ORIGEM (entidade) · PAPEL (multivalorado, cada um com a sua prova) ·
  CANAL (fonte)` viram três coisas separadas. **Presença pública é dimensão à parte e
  nunca vira papel profissional** — `creator` não é tipo de entidade.
- **Motivo:** o Brasil mediu o custo de fundir: 39 dos 55 grupos "PODE FUNDIR" eram a mesma
  pessoa em plataformas diferentes, com 8.687 documentos. *"LIGAR, nunca fundir."*
  E o Brasil **não consegue** representar `produtor + creator`: `fontes.tipo` é uma coluna
  `text not null` com CHECK de valor único. A Itália deve **corrigir**, não copiar.
- **Consequência:** quatro defeitos italianos nomeados — `SENSOR_ID` por nome · origem e
  canal na mesma linha · papel único · 33 fontes sem entidade. Nenhum exige nova
  descoberta para consertar.
- **Quem decidiu:** decisão técnica da missão Brasil → Itália.

---

### D-021 — Das oito travas, sete dizem CORRIGIR e uma diz COPIAR

- **Data:** 2026-09-04
- **Estado:** DECIDIDO
- **Contexto:** as oito afirmações sobre classificação de fonte foram testadas uma a uma
  contra o **código vivo** brasileiro, por agentes instruídos a procurar o contra-exemplo
  antes de concluir e a não aceitar documentação como prova de comportamento.
- **Medido:**

  | trava | BR obedece | IT deve | defeito |
  |---|---|---|---|
  | creator não é identidade humana | PARCIAL | CORRIGIR | registrado |
  | produtor + agrônomo + creator | PARCIAL | CORRIGIR | registrado |
  | **não perder papel verdadeiro por peso** | **NÃO** | CORRIGIR | **não registrado** |
  | organização não vira técnica por keyword | PARCIAL | CORRIGIR | **não registrado** |
  | rede social não prova autoridade | PARCIAL | CORRIGIR | registrado |
  | portal que entrevista não vira agrônomo | PARCIAL | CORRIGIR | registrado |
  | **seguidores medem alcance, não autoridade** | **SIM** | **COPIAR** | registrado |
  | ausência de declaração não é negativa | PARCIAL | CORRIGIR | registrado |

- **Decisão:** a Itália herda o **contrato** brasileiro e **não** o comportamento. A única
  peça a copiar como está é a separação `alcance` × `autoridade`, que o Brasil implementa
  em eixo próprio (`relevancia_alcance`, 0-100 em 4 partes) e nunca funde com a nota.
- **Achado que o Brasil não tinha registrado:** `classificar-fontes.py:151` diz
  *"peso maior vence"* e :415-418 executa — o laço acha TODOS os papéis que casam e
  sobrescreve, e **os perdedores não vão para lista, contador, log ou coluna**. Um agrônomo
  que também é produtor perde o segundo papel sem deixar rastro.
- **Consequência para a Itália:** multivaloração precisa ser **array ou tabela com prova
  por papel** — nunca uma coluna `tipo` escalar, que é onde Brasil e Itália falham hoje
  pela mesma razão estrutural.
- **Quem decidiu:** decisão técnica da missão Brasil → Itália.

---

### D-022 — `NÃO SEI` tratado como negativa matou 68 canais italianos

- **Data:** 2026-09-04
- **Estado:** DECIDIDO · **corrige um relato meu incompleto**
- **Contexto:** a regra italiana de canal é `if COUNTRY != 'IT': REJECT`. Eu relatei que
  *"17 canais foram recusados por país declarado"* e apresentei isso como aplicação
  correta da lei *idioma não é país*.
- **O que a medição mostrou:** foram recusados **24** por declararem país estrangeiro e
  **68 por não declararem país nenhum**. `NOT_DECLARED` não é *"não é Itália"*.
- **Decisão:** ausência de declaração vira **estado**, nunca rejeição. O Brasil batizou o
  defeito: *"tratar ausência de medição como medição de ausência"* (`fila.py:1432-1433`),
  e tem mais de 40 programas com prova unitária de *"NÃO SEI, nunca zero"*.
- **Motivo:** é a mesma lei que este repositório já escreve em `FAIL CLOSED`
  (`falha de leitura ≠ zero`), aplicada a um campo de identidade em vez de a uma rota.
- **Consequência:** 68 canais voltam para avaliação como `PAIS = NÃO SEI`, e a decisão de
  promovê-los passa a exigir outra prova de país — nunca a ausência dela.
- **Quem decidiu:** decisão técnica da missão Brasil → Itália.

---

### D-023 — P-014 fechada: a Itália espelha o contrato e mantém registro próprio

- **Data:** 2026-09-04 · **Estado:** DECIDIDO **pelo dono do projeto**
- **Decisão:** `ITALY_WRITES_TO_BRAZIL_DB = NO` · `CONTRACT_MIRRORED = YES`.
  O Brasil é **referência de contrato**, não infraestrutura compartilhada. Sem camada
  federada. Um eventual reconhecimento da mesma entidade nos dois países será uma camada
  **explícita** de crosswalk, nunca compartilhamento silencioso de banco.
- **Motivo, medido:** o contrato `QUEM É → ONDE EU BATO → DOCUMENTO` está certo, mas o dado
  brasileiro não o realiza; 7 das 8 travas exigem correção; os classificadores são PT-BR
  chumbados em regex; `entidade_id` tem cobertura desconhecida (D-024); `creator` é default
  em 54,8%; papel continua escalar.
- **Consequência:** `BRASIL → semântica · contrato · leis` · `ITÁLIA → dados · registro ·
  classificadores`.

---

### D-024 — P-013 fechada: NÃO SEI, e os três números nunca brigaram

- **Data:** 2026-09-04 · **Estado:** DECIDIDO
- **Contexto:** três números circulavam como cobertura de `fontes.entidade_id` — 47/95, 57
  e 3.275/3.299.
- **Medido, por auditoria forense somente-leitura (Brasil HEAD `38e4b8d`, `git status`
  vazio ao fim):** os três medem coisas **diferentes** e **nenhum** é cobertura.
  **47/95** é contador de escrita de uma rodada — a seguinte deu **4/56**, o número
  **desceu**. **57** é `count(*)` da tabela `entidades`, e a citação de 23/08 é literal
  *hardcoded* em `matriz-do-rendimento.py:305`. **3.275/3.299** é **`external_id`** com o
  rótulo trocado; a medição original diz *"identidade (external)"*, e a seção que a carimba
  como "medido" se declara não-construída em `PLANO-location-resolver.md:665`.
- **Veredito:** `P013_REAL_COVERAGE = NÃO SEI` (firme: a única ocorrência de
  `entidade_id is not null` no repositório é um índice parcial; não há `count` nenhum) ·
  `P013_DENOMINATOR` = não existe um (três universos sem rótulo: 4.548 / 3.670 / 3.654) ·
  `P013_CONTRACT_OPERATIONAL = PARCIAL`.
- **Laterais:** `enderecos` é **fio cortado** (3.627 linhas idênticas em cinco dias, sem
  escritor vivo, sem leitor externo, sem `schedule`). `papel_da_fonte` é **contrato não
  implantado**, não abandonado — nunca recebeu uma linha.
- **Regra que fica, e já aplicada:** *toda coluna de contrato nasce com a sua consulta de
  cobertura no mesmo commit do DDL*, e *todo número publicado carrega coluna medida ·
  denominador declarado · data/execução*. `MIGRATION-VALIDATION.json` é esse censo para a
  Itália. **Herdar tabela sem herdar consumidor é importar esquema morto.**
- **Nada foi alterado no Brasil.**

---

### D-025 — Prosa livre não decide papel: os papéis de campo caem a zero PROVADO

- **Data:** 2026-09-04 · **Estado:** DECIDIDO · **corrige a rota de canal desta missão**
- **Contexto:** `MODELO-DE-IDENTIDADE-EAME.md` lista o que **nunca** decide papel:
  *nome da conta · foto · estilo do texto · idioma · **prosa livre (`about`,
  `description`)** · o assunto de um post*. A rota de canal italiana lia a descrição do
  canal e produzia papéis — exatamente o classificador que a casa já mediu e reprovou.
- **Decisão:** todo papel vindo da aba About passa a `NAO_PROVADO`. O YouTube **não expõe
  campo estruturado de papel**, logo nenhuma família de campo pode ser provada por essa
  rota. Assunto (`CROP`, `ISSUE`, domínio) **continua** podendo vir do texto — a mesma lei
  permite.
- **Consequência medida, e ela é grande:** `AGRONOMISTS = 0` · `TECHNICIANS = 0` ·
  `PRODUCERS = 0` **provados**. Não é perda de dado: é a retirada de uma afirmação que
  nunca teve prova. Os candidatos ficam gravados (`agronomo` 11 · `produtor` 11 ·
  `organizacao_de_pesquisa` 11 · `tecnico` 5 · `consultor` 3 · `cooperativa` 3 ·
  `pesquisador` 2).
- **O que fecharia:** rota com campo declarado estruturado — headline de LinkedIn, página
  de equipe institucional, Ordine dei Dottori Agronomi. **Não executada.**

---

### D-026 — Migração ENTITY · SOURCE · ROLE executada, com seis travas medidas

- **Data:** 2026-09-04 · **Estado:** DECIDIDO
- **Executado:** `scripts/sensor_entidade_it.py`. 224 fichas → **221 entidades + 281
  fontes**. Três fusões `MESMA_ENTIDADE` (Fondazione Edmund Mach, AgroNotizie, AIPO),
  todas por **claim declarado pelo próprio canal**, nunca por semelhança de nome.
- **Identidade:** id opaco sequencial, atribuído uma vez, persistido em `ID-LEDGER.json` —
  a semântica do `bigserial` brasileiro (`fontes.id`), **não** a de `entidades.chave`, que
  o próprio Brasil declara instável. Resolução por **claim**; nome e organização não são
  claims.
- **Achado de implementação:** a purga de papel-de-pessoa-em-organização **tem de ser passe
  final**, depois das fusões. Por registro, ela deixava passar o AgroNotizie: a ficha do
  canal chegava sem forma jurídica no nome, ganhava `agronomo`, e só a fusão revelava que a
  entidade é o veículo. **Kind só é conhecido quando a entidade está inteira.**
- **Dois marcadores corrigidos por medição:** `campo` saiu dos marcadores agronômicos
  (casava *"campo da medicina"* e fazia o Medical Excellence TV virar AGRO); e hobby
  **declarado** passou a vencer mesmo com marcador agronômico junto (*"mondo agricolo
  hobbistico"*).
- **Travas, todas medidas:** `ROLE_LOST_BY_WEIGHT = 0` ·
  `ORGANIZATION_CLASSIFIED_AS_PERSON_ROLE = 0` · `PORTAL_CLASSIFIED_AS_AGRONOMIST = 0` ·
  `NAME_OR_ORG_USED_AS_OPERATIONAL_ID = 0` · `FOLLOWERS_USED_AS_AUTHORITY = 0` ·
  `ID_MIGRATION_LOSS = 0`.

---

### D-027 — Endereço partilhado por duas pessoas não é identidade de nenhuma

- **Data:** 2026-09-04 · **Estado:** DECIDIDO
- **Contexto:** a resolução de entidade é por **claim**. Ao ligar as portas declaradas no
  ORCID, apareceu o caso real: **Marco Lapris** e **Michela Errico** declaram as **mesmas
  duas URLs** (`dipartimenti.unicatt.it/diana-home` e
  `scuoledidottorato.unicatt.it/agrisystem-home`). Sem guarda, as duas pessoas virariam
  **uma entidade**.
- **Decisão:** três guardas, todos medidos na saída.
  **(1)** raiz de domínio não vira claim — URL sem caminho é o endereço do **empregador**,
  não da pessoa; entra como FONTE e não participa da resolução (acionado **4×**).
  **(2)** duas entidades com ORCID distinto **nunca** fundem — união recusada e registrada.
  **(3)** endereço declarado por **≥2** pesquisadores distintos é página institucional
  compartilhada, não identidade (acionado **4×**).
- **Motivo:** a lei da casa é *"Nome NUNCA é identificador"*; o corolário que faltava é que
  **endereço institucional também não é identidade pessoal**. Sem isso, o mecanismo que
  protege contra homônimo abriria uma porta pior: fundir por empregador.
- **Consequência:** `NEW_ENTITIES = 0` · `ENTIDADES_COM_DOIS_ORCID = nenhuma`.

---

### D-028 — ORCID declara cargo acadêmico, não papel de campo

- **Data:** 2026-09-04 · **Estado:** DECIDIDO
- **Medido:** `employments.role-title` provou **114 papéis** em 107 entidades — e quase
  todos acadêmicos: `pesquisador` 60 · `professor` 31 · `estudante` 7 · **`tecnico` 3**.
  `AGRONOMIST_PROVED = 0` · `PRODUCER_PROVED = 0` · `CONSULTANT_PROVED = 0`.
- **Decisão:** a rota ORCID fecha o buraco **científico** e **não** fecha o buraco de campo.
  Um `Ricercatore` é pesquisador provado; não é agrônomo, técnico de campo nem produtor por
  isso. `PROVED_FIELD_ROLES` sobe de 0 para **3**, e o número é o que é.
- **Deliberadamente sem mapa:** `Director`, `Collaboratori`, `Group Leader` — posição
  hierárquica, não papel agrícola. Mapeá-los seria inventar papel a partir de organograma.
- **A rota dos sites rendeu pouco, e isso é informação:** 21 sites lidos, **4** com título
  profissional em posição estruturada. Dois vieram de `og:description`, que é campo
  estruturado com **conteúdo livre** — entraram como **PROBABLE**, nunca PROVADO. O
  contrato espelhado admite grau intermediário (`enderecos.confianca` brasileiro).

---

### D-029 — IDENTITY_SOURCE não é MONITORABLE_CHANNEL

- **Data:** 2026-09-04 · **Estado:** DECIDIDO
- **Medido:** das **53** portas novas, **50 são só identidade** e **3** são canal
  monitorável. Dos 135 pesquisadores, **32** ganharam porta e apenas **3** têm superfície
  onde conteúdo novo apareça.
- **Decisão:** os dois estados são separados e medidos em separado.
  `RESEARCHERS_WITH_MONITORABLE_CHANNEL` e `RESEARCHERS_WITH_IDENTITY_SOURCE_ONLY` nunca se
  somam. Uma página institucional prova **quem a pessoa é** e pode nunca publicar nada;
  chamá-la de monitorável seria prometer uma coleta sem o que colher.
- **`researchgate` e `scholar` ficam como IDENTITY**, por decisão declarada: publicam obra
  nova, mas são **espelho da produção científica que o Europe PMC já cobre** — contá-los
  como canal novo seria contar a mesma testemunha duas vezes.

---

### D-030 — Portão aberto para coleta social, com duas ressalvas que o SIM não apaga

- **Data:** 2026-09-04 · **Estado:** DECIDIDO
- **`SOURCE_RESOLUTION_READY = SIM`** e **`SOCIAL_CONTENT_COLLECTION_READY = SIM`**: as seis
  condições declaradas estão satisfeitas e medidas — conteúdo anexa a `SOURCE_ID`; toda
  fonte aponta para entidade **ou** carrega dívida explícita (91 `UNRESOLVED` nomeadas);
  canal novo não cria entidade; papel não depende de conteúdo; autoridade não depende de
  followers; e há universo declarado.
- **`COLLECTION_UNIVERSE` proposto, não executado:** **89 canais monitoráveis, 44 entidades**
  — YouTube 45 · Instagram 15 · LinkedIn 9 · TikTok 3 · outros 17. Fora: 154 fontes
  só-identidade e 91 `UNRESOLVED`.
- **Ressalva 1:** **79 dos 89 canais pertencem a entidades sem papel provado.** A coleta é
  arquiteturalmente segura, mas o que voltar será atribuível a uma entidade cujo papel
  agrícola continua `NÃO SEI`. Serve para medir *o que se fala*; não sustenta *quem é o
  sensor*.
- **Ressalva 2:** **`APIFY_TOKEN` continua ausente.** Não é uma das seis condições e por
  isso não derruba o `SIM` — mas bloqueia a execução e não deve ser descoberto na hora.

---

### D-031 — O dono canônico da coleta tem nome, e não é "Sintonia Scrap"

- **Data:** 2026-09-04 · **Estado:** DECIDIDO
- **Contexto:** a missão mandou localizar a implementação canônica do "Sintonia Scrap"
  antes de coletar, e parar se houvesse mais de uma.
- **Medido:** o termo **"SINTONIA SCRAP" não existe como componente no repositório** — ele
  aparece **só em documentos desta branch**, propagados por mim. Há **três** implementações
  reais, que não competem: `youtube_janela.py` (rota pública gratuita, `APIFY_RUNS=0`,
  `COST_USD=0`), `youtube_transcrever.py` (Whisper, só o que a legenda não deu) e
  `sensor_coleta.py`+`coletor.py`+`apify_pool.py` (rota paga, exige token ausente).
- **Decisão:** dono canônico deste piloto = **`scripts/youtube_janela.py`**, plataformas
  suportadas = **[YOUTUBE]**. O reúso foi por **injeção** de lote e diretório de saída; o
  arquivo não foi alterado, e os artefatos da missão anterior não foram tocados.
- **Consequência:** `APIFY_USED = NO` · `NEW_SCRAPER_CREATED = NO` ·
  `SCRAP_CHAIN_PROVED = SIM` (cadeia fechada em `IT-S-000071`).

---

### D-032 — Sem legenda, `OFF_TOPIC` não pode ser afirmado

- **Data:** 2026-09-04 · **Estado:** DECIDIDO · **corrige a primeira versão desta medição**
- **Contexto:** a camada de legendas **não abriu** (`PORTA_NAO_ABRIU` nos 150 objetos;
  `HAS_CAPTION = 0`). O único texto disponível é o título — **mediana de 51 caracteres**.
- **O erro, e a prova nos próprios dados:** a primeira versão classificou **98 documentos
  como `OFF_TOPIC`**. Entre eles, *"**Meli** in filare agroforestale — Quarto anno"* —
  **`meli` é macieira**, e caiu como off-topic porque o léxico não tinha o plural. Declarar
  off-topic a partir de 51 caracteres é **tratar ausência de texto como ausência de
  assunto**, a mesma falácia de `falha de leitura ≠ zero`.
- **Decisão:** `OFF_TOPIC` passa a exigir **marcador positivo de assunto não-agrícola**
  (`ricetta`, `bilancio di esercizio`, `assemblea`…) **ou** legenda presente. Sem isso, o
  estado é `NÃO SEI`.
- **Consequência medida:** `OFF_TOPIC` 98 → **7** · `NÃO SEI` 1 → **82**.
  **82 de 150 documentos não são julgáveis**, e esse é o resultado principal do piloto:
  ele mediu **títulos, não conteúdo**.

---

### D-033 — Papel provado NÃO melhorou a qualidade do conteúdo nesta amostra

- **Data:** 2026-09-04 · **Estado:** DECIDIDO
- **Experimento:** 4 fontes com papel PROVADO (40 documentos) contra 11 sem papel provado
  (110 documentos).
- **Medido:** `AG_RELEVANCE_RATE` **0,425 × 0,400** · `TECHNICAL_RATE` 0,025 × 0,027 ·
  `FIELD_SIGNAL_RATE` **0,000 × 0,009**. O **único** `FIELD_SIGNAL` do piloto veio de uma
  fonte **sem papel provado** (Agralia studio di agronomia).
- **Decisão:** a hipótese de que papel previamente provado melhora o conteúdo como sensor
  **não se sustenta nesta amostra**. E o veredito publicado é `NÃO SEI`, não "não": a
  amostra é pequena, sem legenda, e 55% dos documentos não são julgáveis.
- **Motivo de registrar:** a hipótese era intuitiva e eu poderia tê-la assumido. Medir foi
  o que mostrou que ela não se sustenta.

---

### D-034 — Escala barrada por duas condições, e as duas pela mesma causa

- **Data:** 2026-09-04 · **Estado:** DECIDIDO
- **`SCALE_TO_89_CHANNELS = NÃO`.** Das seis condições, quatro passam e **duas falham**:
  **(5)** custo/desperdício — rendimento de **7 documentos operacionais em 150**, sem a
  camada que importa; **(6)** duplicação com fontes científicas **não compreendida** — a
  família pesquisador **não foi testada**, porque os dois pesquisadores com canal
  monitorável publicam em Twitter e LinkedIn, sem rota gratuita.
- **A causa das duas é uma só: a legenda não abriu.** O bloqueio é de **ambiente** (o
  navegador não completou em >15 min), não de arquitetura nem de crédito.
- **Consequência:** o próximo passo é **abrir a camada de legendas** — gratuita, já
  existente em `youtube_janela.py`, já vem com tempos e substitui o Whisper. É o
  pré-requisito para que "vale manter?" tenha resposta.
- **`HUMAN_SOCIAL_CONTENT_HAS_VALUE = NÃO SEI`** — 7 documentos com valor operacional
  apareceram (1 FIELD_SIGNAL, 4 TECHNICAL, 2 RESEARCH), mas com 55% do corpus ilegível
  afirmar valor seria dizer o que não foi medido.

### D-035 — "O navegador não completou" era espera por um processo morto

- **Data:** 2026-09-04 · **Estado:** DECIDIDO · **Corrige:** D-034 (a parte do diagnóstico)
- A camada gratuita de legendas "não completava em >15 min". **Não era lentidão.**
  `cdp.subir` mandava o `stderr` do Chrome para `DEVNULL` e o laço de espera nunca
  consultava `p.poll()`. O Chromium morria em **0,43 s** e o código dormia os **25 s**
  inteiros para então **afirmar o falso**: *"o Chrome subiu mas a porta não passou a
  escutar"*. Ele não subiu.
- **Custo medido:** 150 objetos × 25,02 s = **~63 minutos** imprimindo `PORTA_NAO_ABRIU`
  a cada 25 s, com o motivo trocado. É exatamente o ">15 min sem completar" do relatório.
- **Consertado:** `stderr` vai para arquivo, o laço pergunta `poll()`, e a mensagem passa a
  citar a frase do próprio Chrome. **De 25,02 s de mentira para 1,00 s de verdade.**
- **Lei:** `PROCESSO MORTO ≠ PORTA LENTA`. Um diagnóstico que manda procurar defeito de
  rede onde há binário que se recusou a iniciar é pior que nenhum diagnóstico.

### D-036 — Não é preciso desligar a sandbox para ter navegador neste contêiner

- **Data:** 2026-09-04 · **Estado:** MEDIDO, **não aplicado**
- O Chromium existe aqui (`/opt/pw-browsers/chromium`, 141.0.7390.37) e **recusa iniciar
  como `root` sem `--no-sandbox`**; passado isso, falta `X server`.
- **Medido que os dois se resolvem sem tocar na sandbox:** `runuser -u nobody` + `xvfb-run`
  sobe o navegador **com janela e sandbox LIGADA**, e a porta DevTools responde.
- **Não apliquei ao dono canônico.** `navegador.py:45-49` decide que `--no-sandbox` não vira
  padrão "para funcionar", e a decisão é do dono. Trocar **como a casa executa** não é
  conserto de bug — é política. Fica a prova de que o caminho honesto existe.
- **Nem acrescentei `/opt/pw-browsers` à busca automática:** o mesmo arquivo explica que
  trocar o binário em silêncio troca User-Agent, codecs e TLS, e duas coletas deixam de ser
  comparáveis sem que ninguém tenha mudado nada. `CHROME_EXECUTABLE` já é a porta declarada.

### D-037 — Player negado não é vídeo sem legenda

- **Data:** 2026-09-04 · **Estado:** DECIDIDO · **Código:** `fase_legendas`, estado novo
- A rota barata **funciona** aqui: HTTP 200, 1,19 MB, `_bloqueado()` = `False`,
  `ytInitialPlayerResponse` presente. Dentro dele:
  `playabilityStatus = LOGIN_REQUIRED`, *"Accedi per confermare di non essere un bot"*.
- **Com o player negado o YouTube não manda o bloco `captions`.** O código lia `faixas == []`
  e gravava `AUSENTE` com `WHISPER_CANDIDATO = True`. No controle positivo `jNQXAC9IVRw`,
  que **tem duas faixas** (`de`, `en`), isso seria ausência falsa **com autorização para
  pagar transcrição** — o desastre que o cabeçalho do próprio arquivo promete evitar.
- **Estado novo `PLAYER_NEGADO`**, com `WHISPER_CANDIDATO = False`. `AUSENTE` passa a exigir
  player `OK`. O patch **não afrouxa régua**: move casos de `sem` para `barrado`, a direção
  conservadora; `com` não muda em cenário nenhum. Preso por `tests/test_legendas.py`.
- **Três regimes do mesmo IP, no mesmo dia, na mesma URL:**
  `VERDE` (200, player OK, faixas presentes) → `ÂMBAR` (200, `LOGIN_REQUIRED`, faixas
  ausentes) → `VERMELHO` (429, redirect para `google.com/sorry`). O corpo do 429 é texto de
  **reputação de IP**, não de conteúdo. `ÂMBAR` é o perigoso porque passa em todas as
  verificações que o código tinha.

### D-038 — A condição 6 do portão não era culpa da legenda

- **Data:** 2026-09-04 · **Estado:** DECIDIDO · **Corrige:** D-034
- D-034 afirmou que as condições 5 e 6 falhavam *"pela mesma causa: a legenda"*. Era
  **hipótese**, e a medição refuta metade.
- **Cruzamento offline** dos 89 canais monitoráveis (`sensor_piloto_social_it.py familia`,
  mesma regra de grupo de `selecionar()`, sem rede):

| grupo | facebook | instagram | linkedin | tiktok | twitter | **youtube** |
|---|---|---|---|---|---|---|
| A — papel de campo provado | 2 | 2 | 0 | 0 | 0 | **4** |
| B — pesquisador/professor | 0 | 0 | 1 | 0 | 1 | **0** |
| C — sem papel provado | 14 | 13 | 8 | 3 | 0 | **41** |

- **`RESEARCHER_YOUTUBE_CHANNELS = 0`.** Os dois canais da família pesquisador são um
  Twitter e um LinkedIn. Pelo papel da entidade dá o mesmo: dos 40 canais técnicos de
  YouTube, **0** pertencem a entidade com papel científico `PROVADO` — havendo **84**
  entidades com esse papel no registro.
- **Legenda é uma camada de YouTube. Não alcança quem não está no YouTube.**
  `CONDITION_6_TESTABLE_WITH_CURRENT_YOUTUBE_UNIVERSE = NÃO`, e continuará `NÃO` com a
  legenda funcionando perfeitamente. A condição 6 segue **BLOQUEADA / NÃO SEI**.

### D-039 — Amostra sem data não é evidência: o selo passou a ser um só lugar

- **Data:** 2026-09-04 · **Estado:** DECIDIDO
- `tests/test_evidence.py` ficou **vermelho nesta branch**: 13 amostras da camada italiana
  sem `CAPTURED_AT` e uma sem `SOURCE_ID`. Cada função de escrita montava o dicionário à mão
  e algumas esqueceram o campo — que é o modo normal de falhar quando o selo é opcional em
  doze lugares diferentes.
- **`scripts/selo_de_amostra.py`** carimba `SOURCE_ID` e `CAPTURED_AT` num lugar só, chamado
  em **todos** os pontos de escrita das amostras italianas. Não sobrescreve o que já existe:
  se a função pôs a data real da medição, ela vence.
- As 13 amostras existentes foram preenchidas com a **data do commit que as publicou**,
  declarada em `CAPTURED_AT_ORIGEM` como `BACKFILL` e como **limite superior** da captura —
  não como hora de medição. Inventar a hora exata seria pior que a lacuna.

### D-040 — M7 CONGELADA: o estado canônico da camada de legendas

- **Data:** 2026-09-04 · **Estado:** DECIDIDO · **Quem decidiu:** o dono do produto
- **Congelada em** `HEAD = 0fc50dd24e9b5c08042aaebbc4cd0a4a307568ce`, 337 testes verdes,
  árvore limpa. **M7 deixa de ser frente ativa.**

**As doze leis desta rodada, como estado canônico:**

| # | lei |
|---|---|
| 1 | A **ausência de `captionTracks` não pode ser lida como `NO_CAPTION`** quando o player está negado. |
| 2 | **`PLAYER_NEGADO` não autoriza Whisper.** |
| 3 | **`AUSENTE` só é válido com player `OK`.** |
| 4 | `CONDITION_5_CHANGED_BY_CAPTIONS = NÃO` — **porque nenhuma legenda foi obtida.** |
| 5 | Isso **não** significa que legenda não mudaria a condição 5. Significa que **não foi medido**. |
| 6 | `CONDITION_6_TESTABLE_WITH_CURRENT_YOUTUBE_UNIVERSE = NÃO`. |
| 7 | Razão de 6: universo pesquisador = **2 canais** — Twitter 1, LinkedIn 1, **YouTube 0**. |
| 8 | Portanto **condição 5 e condição 6 têm causas independentes**. |
| 9 | `SCALE_TO_89_CHANNELS = NÃO`. |
| 10 | **Custo zero.** Nenhum serviço pago foi usado. |
| 11 | **P-018 permanece medição isolada, não lei** — o corpo vazio do `timedtext` foi visto uma vez. |
| 12 | **`cdp._vivo` em Linux permanece defeito conhecido, fora do escopo.** |

- **A lei 5 é a que mais importa guardar.** `NÃO` aqui responde *"mudou?"*, não *"mudaria?"*.
  Quem ler a primeira como a segunda vai concluir que legenda não serve — e essa conclusão
  **não foi medida por ninguém**.
- **A correção de proveniência fica incorporada:** `CAPTURED_AT` preenchido **na origem**
  daqui para frente (`scripts/selo_de_amostra.py`); backfills existentes marcados
  explicitamente como `BACKFILL`; data de commit usada **apenas como limite superior**,
  nunca fingida como hora de captura.
- **Proibido nesta e nas próximas rodadas até nova ordem:** `--no-sandbox`; scraper novo;
  workaround de navegador; Whisper; escala para 89; Twitter/LinkedIn; reclassificar
  documento sem texto novo; consertar `cdp._vivo`; gastar tempo com P-018 antes da
  apresentação.

### D-041 — A apresentação do Portal Itália não depende de legenda

- **Data:** 2026-09-04 · **Estado:** DECIDIDO · **Quem decidiu:** o dono do produto
- **Não é preciso resolver legenda para apresentar o Portal Itália.** O sprint recebe apenas
  o que já é defensável:
  - canais e fontes existentes;
  - títulos e metadados **quando válidos**;
  - conteúdo classificado **com o nível correto de incerteza**;
  - **nenhuma afirmação baseada em legenda inexistente**.
- **Consequência operacional:** dos 150 documentos do piloto, **82 não são julgáveis por
  título**. Eles não somem da base e não viram `OFF_TOPIC`: aparecem como **`NÃO SEI`, com o
  motivo**. Uma tela que esconder os 82 estará mentindo por omissão; uma que os classificar
  estará mentindo por invenção.
- **Nenhuma nova missão de coleta social antes da apresentação.**
- **Prioridade retomada:** Portal Itália — ingestão do acervo existente → publicabilidade por
  família → Radar Agora → Radar Futuro → portfólio/regulatório → concorrência →
  oportunidades → vozes → geografia → mapa de ação departamental.

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
| P-010 | Rota para `coltura × avversità` autorizada na Itália: `fitosanitari.salute.gov.it` falha no TLS desta saída e `servizi.salute.gov.it` devolve 502. Sem ela a matriz ADAMA IT diz onde procurar gente, não o que a etiqueta permite. | matriz IT, CASE-014 | 2026-09-04 |
| P-011 | Rota para malherbologia italiana: o Europe PMC não a alcança (21 hits em `CEREAL\|GRASS_WEEDS`), e é onde o portfólio ADAMA IT é mais denso (26 herbicidas). Sociedade científica, atas, revista técnica. | cobertura CEREAL e SUGAR_BEET | 2026-09-04 |
| P-012 | GDPR sobre a camada de sensores humanos IT: 135 pessoas nomeadas com afiliação e ORCID. Mesma pergunta de P-008, agora com registro gravado e não só fila. | REGISTRY IT, qualquer tela | 2026-09-04 |
| P-013 | ~~Cobertura real de `fontes.entidade_id`?~~ — **resolvida** por D-024: `NÃO SEI` firme; os três números medem coisas diferentes e nenhum é cobertura. | — | resolvida 2026-09-04 |
| P-014 | ~~A Itália escreve no banco brasileiro?~~ — **resolvida** por D-023: registro próprio, contrato espelhado, sem escrita no Brasil. | — | resolvida 2026-09-04 |
| P-016 | ~~Camada de legendas do YouTube: a rota de navegador não completou em >15 min~~ — **diagnosticada** por D-035/D-036/D-037: eram quatro muros, não um. Os dois primeiros estão consertados; os dois últimos não são código deste repositório. | — | diagnosticada 2026-09-04 |
| P-017 | **CONGELADA por D-040 até depois da apresentação.** Saída de rede para `/watch` do YouTube: este IP recebe `LOGIN_REQUIRED` (*"Accedi per confermare di non essere un bot"*) e, sob volume, 429 com redirect para `google.com/sorry`. Feed RSS, `oembed` e página de canal continuam 200. Sem uma saída com reputação limpa, a camada de legendas não abre — e nenhuma linha de código muda isso. | legendas, escala para 89 | 2026-09-04 |
| P-018 | **CONGELADA por D-040 — medição isolada, não lei, e não se gasta tempo com ela antes da apresentação.** `/api/timedtext` ainda serve corpo a cliente anônimo? Medido **uma vez** nesta sessão: com player `OK` e duas faixas declaradas, o `baseUrl` **assinado** devolveu `200` com **0 bytes** em `json3` e `srv3`, e o HTML não trazia `pot`/`poToken`. Se for definitivo, a legenda gratuita do YouTube deixou de existir como rota e o orçamento de qualquer alternativa muda. | legendas, Whisper vs. gratuito | 2026-09-04 |
| P-015 | Qual dono de CULTURA a Itália segue? O Brasil tem DUAS listas vivas — `vocabulario.py` CULTURA=9 (em produção) e `lavouras.py` CULTURAS=23 (autodeclarado dono único), com as 9 comuns divergindo em padrão. | vocabulário IT | 2026-09-04 |
