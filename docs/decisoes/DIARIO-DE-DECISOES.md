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
| P-013 | Qual é a cobertura REAL de `fontes.entidade_id` no Brasil? Três números no mesmo período: 47/95 (MAPA-DOS-DADOS.md:180), 57 (inventário 19/08), 3.275/3.299 (PLANO-location-resolver.md:683). A Itália precisa saber se o contrato está operante antes de se apoiar nele. | mapeamento IT→BR | 2026-09-04 |
| P-014 | A Itália escreve no banco brasileiro ou mantém registro próprio espelhando o contrato? Decide se `MAPA-BRASIL.json` é destino final ou passo intermediário. | arquitetura EAME | 2026-09-04 |
| P-015 | Qual dono de CULTURA a Itália segue? O Brasil tem DUAS listas vivas — `vocabulario.py` CULTURA=9 (em produção) e `lavouras.py` CULTURAS=23 (autodeclarado dono único), com as 9 comuns divergindo em padrão. | vocabulário IT | 2026-09-04 |
