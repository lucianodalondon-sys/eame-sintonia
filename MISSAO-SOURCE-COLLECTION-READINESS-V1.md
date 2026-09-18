# MISSÃO — SOURCE COLLECTION READINESS V1
# TRANSFORMAR O UNIVERSO DE FONTES EM FONTES COLETÁVEIS
# ONBOARDING MASSIVO POR CLASSES DE AQUISIÇÃO

Você está continuando o MESMO SINTONIA EAME.

Esta é uma missão de COLLECTION.

NÃO é missão de descobrir novas fontes.
NÃO é missão de Intelligence.
NÃO é missão de Portal.
NÃO é missão de reconstruir SCRAP.

A pergunta principal é:

DAS FONTES JÁ CONHECIDAS DO SINTONIA ITÁLIA/EU,
QUANTAS CONSEGUIMOS TRANSFORMAR AGORA EM
SOURCE_COLLECTION_READY,
REUTILIZANDO PRIMEIRO AS CAPABILITIES/COLLECTORS QUE JÁ EXISTEM?

==================================================
0-BIS. ESTADO JÁ MEDIDO PELO COORDENADOR (2026-09-18)
==================================================

O coordenador mediu ANTES de abrir esta worktree. Estes valores são FATO MEDIDO,
mas não substituem a sua própria medição: confirme cada um. Git atual vence.

```
REPO                 = lucianodalondon-sys/eame-sintonia
ORCA_REPO_ID         = 21fd565e-b307-4e21-a48a-ae64d3b31330
TRUNK_BRANCH         = claude/it-trunk-v1
TRUNK_HEAD           = d915f85a86a7ef0d310859f7380159dbed65b48a
REMOTE_HEAD          = d915f85a86a7ef0d310859f7380159dbed65b48a  (local == remoto)
LOCAL_EQUALS_REMOTE  = YES
```

CORREÇÃO IMPORTANTE — NÃO USE O HEAD DO PROMPT ORIGINAL:

O prompt original citava `78f8fcdcd240191d0c681ee746be5c02d6bc9342`.
Esse HEAD está OBSOLETO. É ancestral de `d915f85a`, que tem 1 commit à frente:

```
d915f85a  collection: primeira Big Collection italiana — 6 fontes, 2 READY
```

BASE_HEAD desta missão = d915f85a86a7ef0d310859f7380159dbed65b48a

Esta worktree já nasceu nesse HEAD, em branch própria:

```
WORKTREE = C:/Users/London1/orca/workspaces/eame-sintonia/it-source-collection-readiness-v1
BRANCH   = it-source-collection-readiness-v1
BASE_REF = claude/it-trunk-v1
```

NÃO trabalhar no trunk. NÃO trabalhar em `C:/eame-sintonia` (checkout principal,
que está noutra branch e com 42 entradas não commitadas — não é o seu lugar).

### Censo preliminar medido pelo coordenador (CONFIRMAR, não confiar)

Contado em `docs/fontes/INDICE-DE-FONTES.md` no HEAD d915f85a, tabela de fichas:

```
FICHAS COM SOURCE_ID NA TABELA       210
  IT                                 157
  ES                                  34
  EU                                  13
  FR                                   6

"A MÁQUINA BUSCA SOZINHA?" = SIM      5   (IT 1, ES 2, EU 1, FR 1)
"A MÁQUINA BUSCA SOZINHA?" = NÃO    205

ESTADO IT: GREEN 75 · YELLOW 81 · NÃO SEI 1
```

Divergência já registada pelo próprio índice, e que NÃO deve ser "corrigida" por
atalho: o cabeçalho do Atlas declara **190 fontes**, as fichas com SOURCE_ID válido
são **210**. O índice diz explicitamente que isto é decisão humana, não correção
automática. Trate como `BLOCKER = CONTADOR_DIVERGENTE` e meça você mesmo o número
real; não edite o contador para fazer bater.

Escada declarada no índice: CANDIDATA 0 · REGISTADA 173 · CONTRATADA 5 · AUTOMÁTICA —
Fila de candidatas: 241 em `candidatas/FONTES-CANDIDATAS.json` (NÃO entram nesta missão).

ATENÇÃO — estes três números são universos DIFERENTES e o índice já os mistura em
sítios distintos (210 fichas × 190 no cabeçalho × 173 "REGISTADA"). Medir e declarar
os três separadamente, com o denominador de cada um. Ver §2 e §22.

### Trabalho vizinho já medido (não duplicar, não esperar)

```
claude/it-source-readiness-v1      JÁ INTEGRADO no trunk
claude/it-sources-atlas-v1         JÁ INTEGRADO no trunk
claude/scrap-capabilities-wiring-v1 JÁ INTEGRADO no trunk (é o 78f8fcd)
claude/it-sources-candidatas-v1    NÃO INTEGRADO — 89 candidatas novas (725f9450)
```

`it-sources-candidatas-v1` NÃO faz parte desta missão: são candidatas não promovidas
a SOURCE, e §3 exclui candidatas. Não puxe essa branch. Apenas não conte esses 89
como universo.

==================================================
0. REGRA ZERO — MEDIR O ESTADO ATUAL
==================================================

Antes de qualquer alteração:

medir:

REPO =
TRUNK_BRANCH =
TRUNK_HEAD =
REMOTE_HEAD =
LOCAL_EQUALS_REMOTE =
STATUS =
WORKTREES =

Git atual vence memória, handoff e este documento.

==================================================
1. AUTORIDADES
==================================================

Ler somente o necessário:

- Bíblia da Collection
- contratos de identidade/procedência/admission
- know-how canônico
- Atlas / owner de SOURCE_ID
- livro de relevância
- candidatas/fonte_nova.py
- receitas atuais
- orquestrador
- executores atuais
- scrap_colheita
- scrap_executor
- capability registry
- admission
- Sala de Espera
- System Map

Ponteiros medidos pelo coordenador (confirmar no seu HEAD):

```
docs/fontes/ATLAS-DE-FONTES-EAME.md
docs/fontes/INDICE-DE-FONTES.md            (GERADO — não editar à mão)
docs/fontes/ITALY-SOURCE-CONTRACT-MATRIX-V1.md
docs/capacidades/ATLAS-DE-CAPACIDADES-EAME.md
docs/operacao/CONTRATOS-DAS-FONTES-EAME.md
docs/operacao/CONTRATO-DE-RETORNO-DO-EXECUTOR-V1.md
docs/operacao/SOURCE-DOCUMENT-DONO-STORE-CONTRATO.md
docs/operacao/SOURCE-ID-WIRING-GAP-V1.md
docs/operacao/ORQUESTRACAO-UM-CEREBRO.md
docs/operacao/ALLOWED-STRUCTURED-TARGETS-POR-FONTE.md
docs/research/SINTONIA-SCRAP-CAPABILITY-MATRIX.md
docs/sintonia-scrap/C10-1-SOURCE-ID.md
docs/sintonia-scrap/C12-X-CAPABILITY-DEEP-CENSUS.md
orquestrador/orquestrador.py · orquestrador/persistencia.py
pedido/receitas.py
coleta/italy_executor.py · coleta/scrap_executor.py
coleta/executor_texto_de_pdf.py · coleta/executor_transcricao_midia.py
coleta/eu_regulatorio_executor.py · coleta/ingresso.py · coleta/texto_fonte.py
admissao/admissao.py · leis/artefato.py
candidatas/fonte_nova.py
system-map/scripts/censo_dos_executores.py
SINTONIA-EAME-KNOW-HOW.md
```

`docs/operacao/SOURCE-ID-WIRING-GAP-V1.md` já mediu, no trunk, que o SOURCE_ID se
perde em dois sítios distintos (READER_GAP 7 · OUT_OF_FLOW_EVIDENCE 13) e que
`ONE_SINGLE_ROOT_CAUSE = NO`. Leia antes de tocar em linhagem. Não refaça essa
medição às cegas e não faça backfill inferido.

Preservar:

SOURCE_ID nunca é inventado.
DOCUMENT_ID nunca é fabricado.
RAW_OBSERVATION_ID = raw_asset.id.

==================================================
2. NÃO CONFUNDIR OS NÚMEROS
==================================================

Medir separadamente:

TOTAL_SOURCES =
ITALY_SOURCES =
EU_SOURCES_APPLICABLE =
RELEVANCE_SIM =
RELEVANCE_PENDING =
SOURCE_EVIDENCE_READY =
SOURCE_COLLECTION_READY =
SOURCE_COLLECTION_NOT_READY =

Não usar:

8 capabilities wired

como se significasse:

8 sources collectable.

CAPABILITY != SOURCE.

Do mesmo modo: "a máquina busca sozinha = SIM" em 5 fichas NÃO significa
5 fontes COLLECTION_READY. Meça a definição do §16, não o rótulo do índice.

==================================================
3. UNIVERSO DE TRABALHO
==================================================

Começar pelas fontes já existentes no Atlas.

Não incluir candidatas não promovidas como SOURCE.
(As 241 em `candidatas/FONTES-CANDIDATAS.json` ficam de fora. As 89 da branch
`claude/it-sources-candidatas-v1` também.)

Para cada SOURCE_ID do universo IT + EU aplicável,
produzir uma linha de censo:

SOURCE_ID
PROPÓSITO
SOURCE_TYPE
PRIMARY_URL
ACCESS_SHAPE
RELEVANCE_STATE
EXISTING_CAPABILITY
EXISTING_EXECUTOR
EXISTING_RECIPE
COLLECTION_WIRED
POLICY_STATE
COST_CLASS
CANARY_STATE
COLLECTION_READY
BLOCKER

==================================================
4. CLASSIFICAR POR FORMA DE AQUISIÇÃO
==================================================

NÃO tratar cada fonte como um software diferente.

Agrupar por equivalência operacional.

Exemplos possíveis, mas medir antes de declarar:

HTML_PUBLIC
PDF_DIRECT
PDF_DISCOVERY_PAGE
RSS
XML
JSON_API
CSV_DATASET
OFFICIAL_API
SEARCH_PAGE
BROWSER_PUBLIC
BROWSER_SESSION
YOUTUBE
SOCIAL_PUBLIC
PROVIDER
OTHER

A classe deve ser baseada no caminho REAL de aquisição,
não no tema da fonte.

Exemplo:

20 serviços fitossanitários diferentes
podem ser a mesma classe:

HTML → link PDF → PDF.

Não construir 20 coletores se um collector configurável resolve os 20.

==================================================
5. MATRIZ DE EQUIVALÊNCIA
==================================================

Para cada ACCESS_SHAPE responder:

SHAPE_ID =
SOURCES_IN_SHAPE =
EXISTING_COLLECTOR =
EXISTING_CAPABILITY =
EXISTING_WIRING =
INPUT_CONTRACT =
OUTPUT_CONTRACT =
POLICY =
COST =
REPRESENTATIVE_SOURCE =
CANARY_NEEDED =

Objetivo:

minimizar código novo.

==================================================
6. REUTILIZAR PRIMEIRO
==================================================

Ordem obrigatória:

1. collector/capability já existe e já está wired
2. collector existe, falta configurar a fonte
3. capability existe, falta wiring
4. collector genérico pode ser ampliado sem quebrar contrato
5. somente então criar capability nova

Não criar ferramenta por fonte.

Não manter ferramenta velha concorrente se uma nova substitui a anterior.

ONE CONCEPT → ONE OWNER.

==================================================
7. CONFIGURAR FONTES NAS FERRAMENTAS EXISTENTES
==================================================

Para fontes que já cabem em uma ferramenta existente:

não escrever scraper novo.

Criar apenas o mínimo necessário para a fonte:

SOURCE_ID
URL/endereço
parâmetros
filtros
paginação
limites
tipo de retorno
receita/fase

Se uma mesma classe tiver 50 fontes:

preferir configuração declarativa/registry

e NÃO:

50 módulos Python.

==================================================
8. SOURCE_ID
==================================================

O SOURCE_ID vem do Atlas/Collection.

Nunca derivar de:

URL
domínio
slug
filename
path
owner
SHA256
handle
channel_id.

ATENÇÃO MEDIDA: `SOURCE-ID-WIRING-GAP-V1.md` provou que hoje existem 13 corpos em
`data/samples/IT-SOURCE-SAMPLES/<SOURCE_ID>/` onde o SOURCE_ID existe SÓ como nome
de diretório. Nome de diretório NÃO é identidade governada. Não use essa convenção
de caminho como prova de que a fonte tem SOURCE_ID canônico wired.

Se uma fonte ainda não tiver SOURCE_ID canônico:

ela NÃO fica COLLECTION_READY nesta missão.

Entregar:

BLOCKER = SOURCE_ID_MISSING

para o owner correto.

==================================================
9. RELEVÂNCIA
==================================================

Não inventar decisão humana.

Estados possíveis:

SIM
NAO
NAO_AVALIADA
NAO_SEI
etc.

Para esta missão técnica:

RELEVANCE_SIM
→ pode tornar-se EXECUTABLE após demais gates.

RELEVANCE_PENDING
→ pode ser tecnicamente onboarded/provado,
mas NÃO entra em COLETA_TOTAL.

Portanto separar:

TECHNICALLY_COLLECTION_READY

de:

BIG_COLLECTION_EXECUTABLE.

Uma fonte pode terminar:

TECHNICALLY_COLLECTION_READY = YES
RELEVANCE = NAO_AVALIADA
BIG_COLLECTION_EXECUTABLE = NO

Isso é correto.

==================================================
10. CANÁRIOS POR CLASSE, NÃO POR VIBE
==================================================

Não precisamos necessariamente executar uma missão completa por fonte.

Para cada shape:

selecionar representante real.

Provar:

REQUEST
→ ORCHESTRATOR
→ COLLECTOR
→ RUN
→ RAW OBSERVATION
→ STORAGE OBJECT
→ DERIVED
→ STRUCTURED
→ ADMISSION
→ SALA

Depois, para as fontes equivalentes,
provar individualmente pelo menos que:

- endereço resolve;
- parâmetros são aceitos;
- retorno pertence ao mesmo contrato;
- SOURCE_ID correto desce;
- nenhum filtro é ignorado silenciosamente.

CAN DO != DID DO.

Uma prova representativa da classe
não dispensa verificação por fonte.

==================================================
11. NÃO FAZER BIG COLLECTION NESTA MISSÃO
==================================================

Aqui o objetivo é ONBOARDING.

Usar:

canários mínimos
amostras mínimas
trials gratuitos permitidos

quando necessário.

Não fazer coleta total.

Não consumir centenas de páginas para provar uma rota.

==================================================
12. ROTAS PAGAS
==================================================

Não gastar sem autorização.

Se uma fonte só tiver caminho pago:

TECHNICALLY_COLLECTION_READY pode ser YES
se integração estiver provada.

Mas:

BIG_COLLECTION_EXECUTABLE =
NO

até Budget/Authorization PASS.

Registrar:

PAID_ROUTE
PROVIDER
EXPECTED_COST
AUTHORIZATION_STATE.

==================================================
13. SOCIAL / SCRAP
==================================================

Não esperar as frentes de Reels/YouTube terminarem para avançar no restante.

Se uma fonte depender de capability ainda não resolvida:

BLOCKER =
SCRAP_CAPABILITY_GAP

e seguir para a próxima.

Uma fonte Instagram não pode bloquear 50 PDFs.

==================================================
14. IMPLEMENTAÇÃO POR ONDAS
==================================================

Executar a missão em ondas independentes.

WAVE A — ROTAS MAIS SIMPLES

- PDF direto
- HTML público
- RSS/XML
- CSV
- JSON/API oficial simples

Objetivo:
converter rapidamente o maior conjunto que já cabe na Collection.

WAVE B — DISCOVERY + DOCUMENT

exemplo:

landing page
→ descobrir documentos
→ coletar PDFs.

WAVE C — APIS / PAGINAÇÃO

fontes oficiais estruturadas com contrato próprio.

WAVE D — BROWSER

somente quando HTTP/API não resolver.

WAVE E — SOCIAL / PROVIDER

apenas usando capabilities já PROVEN e permitidas.

Não deixar WAVE E travar A-D.

==================================================
15. QUANDO CONSTRUIR CAPABILITY NOVA
==================================================

Só construir se:

- várias fontes reais dependem do mesmo gap;
- não existe owner atual;
- não existe ferramenta canônica equivalente;
- contrato está claro;
- ganho de cobertura está medido.

Antes de implementar declarar:

NEW_CAPABILITY =
SOURCES_UNLOCKED =
WHY_EXISTING_TOOLS_CANNOT_DO_IT =

Se desbloqueia só uma fonte,
questionar se realmente precisa de capability global.

==================================================
16. DEFINIÇÃO DE SOURCE_COLLECTION_READY
==================================================

Uma fonte só recebe:

SOURCE_COLLECTION_READY = YES

se:

SOURCE_ID canônico existe
AND
endereço real foi validado
AND
rota existe
AND
capability existe
AND
executor existe
AND
wiring existe
AND
parâmetros estão contratados
AND
retorno está tipado
AND
policy não bloqueia a rota
AND
canário/observação suficiente provou o caminho
AND
lineage não fabrica identidade.

Relevância não faz parte desta definição técnica.

Separar depois:

BIG_COLLECTION_EXECUTABLE =
SOURCE_COLLECTION_READY
× RELEVANCE_SIM
× POLICY_ALLOWED
× BUDGET_ALLOWED.

==================================================
17. PROVA DE CADA CLASSE
==================================================

Para cada shape implementado:

SHAPE =
REPRESENTATIVE =
REQUEST =
RUN =
RAW =
STORAGE =
DERIVED =
STRUCTURED =
ADMISSION =
READY =

Depois:

SOURCES_CONFIGURED =
SOURCES_VERIFIED =
SOURCES_FAILED =

==================================================
18. FALHAS NÃO PODEM SUMIR
==================================================

Cada fonte não pronta precisa de blocker explícito:

RELEVANCE_PENDING
SOURCE_ID_MISSING
URL_DEAD
ROUTE_UNKNOWN
CAPABILITY_MISSING
NOT_WIRED
POLICY_BLOCKED
AUTH_REQUIRED
PAID_BLOCKED
BROWSER_REQUIRED
SOURCE_CHANGED
RATE_LIMITED
CANARY_FAILED
UNKNOWN

UNKNOWN permanece UNKNOWN.

==================================================
19. RED TEAM
==================================================

Atacar:

- duas fontes diferentes recebendo mesmo SOURCE_ID;
- URL usada como SOURCE_ID;
- SHA usado como DOCUMENT_ID;
- collector genérico engolindo parâmetro sem usar;
- PDF linkado mas nunca baixado;
- landing page registrada como documento final;
- CATALOG contado como COLHEITA;
- SUPPORT entrando em Admission;
- canário de uma fonte usado para declarar outra pronta sem verificar;
- paginação inexistente sendo declarada como total;
- erro 403 tratado como zero resultados;
- rota paga executada sem autorização;
- browser fallback escondido;
- fact location inferida do source location;
- publicação usada como fact time;
- mesmo conteúdo em duas fontes colapsando observações.

RED_TEAM_BLOCKERS = 0.

==================================================
20. REGRESSÃO
==================================================

Rodar:

testes das capabilities alteradas
testes da Collection
provas de identidade
provas de admission
System Map chain.

Contraprovar falhas no trunk-base (d915f85a), mesma árvore e mesmo ambiente,
comparando NOMES de falhas — não contagens.

NEW_FAILURES = 0.

Suíte incompleta ou interrompida é `NOT_MEASURABLE`, nunca PASS.

==================================================
21. SYSTEM MAP
==================================================

Não editar JSON gerado.
`docs/fontes/INDICE-DE-FONTES.md` também é GERADO — não editar à mão.

Código/configuração
→ owner
→ regeneração
→ validação.

MODULE EXISTS
!=
EDGE EXISTS
!=
FLOW EXISTS.

SYSTEM_MAP_CHECK = PASS.

==================================================
22. RESULTADO QUE EU QUERO
==================================================

No final quero saber:

ANTES:

SOURCES_TOTAL =
SOURCE_COLLECTION_READY_BEFORE =

DEPOIS:

SOURCE_COLLECTION_READY_AFTER =
NEW_SOURCE_COLLECTION_READY =
STILL_NOT_READY =

e, separadamente:

RELEVANCE_SIM =
BIG_COLLECTION_EXECUTABLE_NOW =

Não misturar esses quatro números.

==================================================
23. RELATÓRIO POR CLASSE
==================================================

Entregar:

| SHAPE | FONTES | READY | BLOCKED | TOOL | NEW CODE? |
|-------|--------|-------|---------|------|-----------|

Depois:

| BLOCKER | FONTES |
|---------|--------|

Quero enxergar imediatamente:

qual ferramenta destrava mais fontes.

==================================================
24. PRIORIDADE
==================================================

Priorizar cobertura.

Se uma mudança pequena destrava 40 fontes
e outra mudança complexa destrava 1:

fazer primeiro a de 40.

Não usar ranking subjetivo.

Usar:

SOURCES_UNLOCKED
× COMPLEXITY
× POLICY/COST CONSTRAINTS.

==================================================
25. NÃO PERSEGUIR PERFEIÇÃO
==================================================

Não precisamos deixar 170/170 prontas nesta missão.

Precisamos maximizar:

NEW_SOURCE_COLLECTION_READY

sem quebrar leis.

Se chegar a:

100 prontas
20 bloqueadas por social
30 por relevância
etc.

isso já é informação operacional excelente.

==================================================
26. KNOW-HOW
==================================================

Registrar aprendizado durável:

shape reutilizável
collector canônico
gap real
ferramenta aposentada
limitação provada
decisão arquitetural.

O QUE
→ POR QUÊ
→ PROVA
→ CONSEQUÊNCIA.

Não criar novo KNOW-HOW.
Existe UM só na árvore (`SINTONIA-EAME-KNOW-HOW.md`), e um teste reprova
know-how concorrente. Delta interino vai para `handoff/KNOW-HOW-DELTA-*.md`.
Seção antiga não se apaga: erro revogado ganha aviso apontando a seção que o corrigiu.

==================================================
27. CRITÉRIOS DE PASS
==================================================

SOURCE_COLLECTION_READINESS_V1 = PASS

se:

- universo atual foi medido;
- fontes foram agrupadas por aquisição;
- tools existentes foram reutilizadas primeiro;
- fontes configuráveis foram onboarded;
- gaps reais foram separados;
- canários suficientes provaram os shapes;
- wiring está canônico;
- identidade/procedência foram preservadas;
- nenhuma rota bloqueada foi aberta por atalho;
- NEW_FAILURES = 0;
- System Map passa;
- censo final mostra claramente quanto a Collection cresceu.

==================================================
28. ENTREGA FINAL
==================================================

GIT

BRANCH =
BASE_HEAD =
FINAL_HEAD =
REMOTE_HEAD =

UNIVERSO

TOTAL_SOURCES =
IT_SOURCES =
EU_APPLICABLE =

ANTES

SOURCE_COLLECTION_READY_BEFORE =
BIG_COLLECTION_EXECUTABLE_BEFORE =

DEPOIS

SOURCE_COLLECTION_READY_AFTER =
NEW_SOURCE_COLLECTION_READY =
BIG_COLLECTION_EXECUTABLE_AFTER =

RELEVÂNCIA

RELEVANCE_SIM =
RELEVANCE_PENDING =

SHAPES

ACQUISITION_SHAPES =
SHAPES_ALREADY_SUPPORTED =
SHAPES_NEWLY_SUPPORTED =
SHAPES_BLOCKED =

IMPLEMENTAÇÃO

SOURCES_CONFIGURED =
SOURCES_CANARY_PASS =
SOURCES_CANARY_FAIL =

NEW_CAPABILITIES =
NEW_COLLECTORS =
REUSED_COLLECTORS =

BLOCKERS

SOURCE_ID_MISSING =
ROUTE_UNKNOWN =
CAPABILITY_MISSING =
NOT_WIRED =
POLICY_BLOCKED =
PAID_BLOCKED =
RELEVANCE_PENDING =
UNKNOWN =

PROVAS

TESTS =
NEW_FAILURES =
RED_TEAM_BLOCKERS =
SYSTEM_MAP_CHECK =

RESULTADO

SOURCE_COLLECTION_READINESS_V1 =
PASS / PARTIAL / FAIL

KNOW_HOW_DELTA =
NENHUM / ATUALIZAÇÃO NECESSÁRIA

BIBLIA_CONTRACT_CHANGE =
YES / NO

NEXT_MINIMUM_STEP =

==================================================
29. COMO ENTREGAR (OBRIGATÓRIO)
==================================================

O dono do projeto NÃO é engenheiro. Toda entrega tem duas partes, nesta ordem:

1. RELATÓRIO MEDIDO — os campos do §28, com commits, gates e evidência.
2. EM LINGUAGEM SIMPLES — secção final sem jargão: o que aconteceu, o que mudou
   na prática, em que ponto do caminho estamos, o que falta e o que trava.
   Termo técnico inevitável vem traduzido na mesma frase.
   "NÃO SEI" diz-se em português claro: "isto ainda não foi medido, portanto não sei".

Commitar e fazer push da branch `it-source-collection-readiness-v1`.
Declarar FINAL_HEAD e REMOTE_HEAD reais.

==================================================
HARD STOP
==================================================

Não iniciar Big Collection automaticamente.
Não iniciar Intelligence.
Não iniciar Portal.
Não descobrir novas fontes.
Não iniciar próxima missão.
Não fazer merge para o trunk sem autorização do coordenador.
