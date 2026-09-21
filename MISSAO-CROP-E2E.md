# SINTONIA EAME — COLLECTION
# CIRURGIA CROP END-TO-END
# SOURCE BYTES → DERIVED → SALA → INTELLIGENCE
# SEM RECOLETA

Git + runtime + banco vencem qualquer handoff.

## CONTEXTO MEDIDO PELO COORDENADOR (verificar, não confiar)

BANCADA          C:/Users/London1/orca/workspaces/eame-sintonia/crop-e2e-v1
BRANCH           crop-e2e-v1
BASE             claude/int-pilot-sala-v1
INITIAL_HEAD     d51ea98aea74ddec0b0e96c3e638cc789adf42b5
WORKTREE_CLEAN   SIM na criação
SALA DSN         a Sala real medida pelo piloto vivia em 127.0.0.1:54330/sala_italia
                 (porta 54330 medida LISTENING neste host, pid 53588 — confirmar)

O segundo piloto da Intelligence terminou em d51ea98a.

Achado medido no piloto R2:

SALA_TOTAL = 46
ITEMS_EXPECTING_CROP = 5
ITEMS_WITH_CROP = 0
ITEMS_MISSING_CROP = 5
CROP_LOST_IN_DERIVATION = 5/5 = 100%

SOURCE_CONTENT_HAS_CROP = YES
DERIVED_STRUCTURED_CROP = NO

A informação textual existe (oliveira / vinha / macieira etc.), mas não
atravessa como chave estruturada utilizável.

Isso bloqueia:

CROP × PEST/DISEASE × ACTIVE INGREDIENT × ADAMA PRODUCT × TARGET × AUTHORIZATION

Peças já existentes nesta árvore (ponto de partida, medir antes de mexer):
- provas/o_piloto_da_sala.py — contém SONDA_CROP e medir_crop(); SONDA é
  instrumento de CONTAGEM, não fonte de chave.
- docs/operacao/PILOTO-DA-SALA-R2-INCREMENTAL.md — §C tem os 5 itens T3
  nomeados e as culturas observadas no texto.
- coleta/derivacao_forward.py, coleta/executor_texto_de_pdf.py,
  coleta/pdf_text.py, coleta/golden_path_pdf.py, admissao/admissao.py,
  admissao/sala_de_espera.py

## OBJETIVO ÚNICO

Fazer CROP atravessar corretamente pelo caminho canônico:

SOURCE EVIDENCE → DERIVATION → ADMISSION / SALA → CONSUMO PELA INTELLIGENCE

usando SOMENTE os bytes já armazenados.

NÃO recoletar os 5 itens.
NÃO buscar internet.
NÃO alterar a régua para produzir resultado.

## FASE 0 — ESTADO REAL / ANTI-COLISÃO

Medir e declarar:

COLLECTION_BRANCH = / HEAD = / REMOTE_HEAD = / WORKTREE = / DIRTY = / ACTIVE_WRITERS =

Não tocar em worktree ativa de Auditoria, Source Curator ou Intelligence.
Outras worktrees ATIVAS medidas agora (NÃO TOCAR): source-curator-integration-v1,
big-collection-release-v1, curator-04a-integration, it-trunk-v1, cutover-v2,
it-source-collection-readiness-v1, it-collection-sala, it-adama-reference,
it-sources-atlas, orca-test-claude, it-portal-reconciled-v1,
intelligence-bible-canonical-review-749b7c, hermes-orca-claude-integration-test,
social-acq-v1.

Trabalhar SOMENTE em crop-e2e-v1.

## FASE 1 — LOCALIZAR EXATAMENTE ONDE CROP SE PERDE

Para cada um dos 5 T3:

ITEM_ID / SOURCE_ID / RAW_ASSET_ID / STORAGE_OBJECT_ID / DERIVED_ID / SALA_ID

Medir:

CROP_PRESENT_IN_BYTES
CROP_PRESENT_IN_EXTRACTED_TEXT
CROP_PRESENT_IN_TABLE_STRUCTURE
CROP_PRESENT_IN_DERIVED
CROP_PRESENT_IN_ADMISSION
CROP_PRESENT_IN_SALA
CROP_VISIBLE_TO_INTELLIGENCE

Não assumir que todos quebram no mesmo ponto.

Entregar: CROP_LOSS_STAGE por item.

## FASE 2 — OWNER CANÔNICO

Antes de adicionar campo, localizar owner existente de:
crop / culture, agronomic entities, structured derivation, derived schema,
Sala schema, Claim/Fact schema se aplicável.

Não criar segundo vocabulário.
Se já existe representação canônica: usar.
Se não existe: criar somente o mínimo necessário no owner correto.

## FASE 3 — NÃO CONFUNDIR MENÇÃO COM CULTURA DO FATO

"olivo" aparecer no texto não significa automaticamente CROP = OLIVO.
A extração precisa preservar contexto suficiente.

Classificar quando possível:
CROP_EXPLICIT / CROP_CONTEXT / EVIDENCE_ANCHOR / PRECISION / STATUS

UNKNOWN continua UNKNOWN.
Não usar regex solta para produzir certeza sem contexto.

## FASE 4 — PDFs / TABELAS

O piloto indicou que parte da informação vive em colunas de PDF.

Medir se a perda ocorre porque:
- flattening destrói coluna;
- cabeçalho deixa de acompanhar linha;
- tabela vira texto sem contexto;
- parser ignora estrutura;
- outro motivo.

Se tabela for a causa, preservar associação:
CROP/CULTURE HEADER → ROW → RECOMMENDATION / PEST / ACTIVE

Não construir parser universal de PDF nesta missão.
Resolver o padrão real comprovado nesses itens, generalizável quando possível.

## FASE 5 — REDERIVAÇÃO LOCAL

Rederivar SOMENTE os bytes já existentes dos 5 itens T3. NETWORK = OFF.

T3_TOTAL = 5 / T3_REDERIVED = / T3_CROP_RECOVERED = / T3_CROP_UNKNOWN = / T3_FAILED =

Não criar nova observation. Não criar nova Collection Run. Não duplicar storage.

## FASE 6 — PROPAGAÇÃO

Por item: DERIVED_CROP / ADMISSION_CROP / SALA_CROP / INTELLIGENCE_INPUT_CROP

Se algum estágio não deve armazenar CROP por arquitetura: não forçar.
Nesse caso provar a referência canônica pela qual a Intelligence o recupera.

## FASE 7 — TESTE DURO DO GATE REGULATÓRIO

O piloto descobriu (defeito D-01) que `cruzar()` nunca lê cultura e que
CROSSING_STATE só assume NOT_POSSIBLE: MELO (146 usos autorizados) e OLIVO (1)
dão o MESMO veredito.

Testar com contraprova real: mesma substância/produto
+ CROP A autorizada versus CROP B não autorizada.

Provar ao menos:
AUTHORIZED_CROP_CASE / UNAUTHORIZED_CROP_CASE / UNKNOWN_CROP_CASE

Esperado conceitualmente:
CROP autorizada    → pode prosseguir para próximo gate
CROP não autorizada → bloqueia
CROP UNKNOWN       → NOT_POSSIBLE / NEED_MORE_EVIDENCE

Não precisa gerar oportunidade. Só provar que a chave CROP participa da decisão.

## FASE 8 — REGRESSÕES

Provar:
1. UNKNOWN não vira CROP;
2. PUBLISHED_AT não vira FACT_TIME;
3. SOURCE_LOCATION não vira FACT_LOCATION;
4. rederivação não duplica observation;
5. mesma evidência não vira duas evidências independentes;
6. CROP errado bloqueia autorização;
7. CROP correto realmente altera o resultado do gate.

NEW_FAILURES = (comparar nomes de falhas contra baseline d51ea98a na mesma árvore/ambiente)

## FASE 9 — SYSTEM MAP

Se esta correção mudar elo real (DERIVED → CROP → Intelligence), regenerar pela
cadeia canônica e exigir SYSTEM_MAP_CHECK = PASS.
Se não houver mudança arquitetural: não gerar churn.

## FASE 10 — NÃO RECOLETAR ARIF

NÃO buscar boletim novo da ARIF nesta missão.
A ausência de T3 novo na Big Collection (GAP-07) é problema separado de
SOURCE/CADENCE/SELECTION e pertence ao Source Curator/Auditor.

Aqui o foco é: fazer os documentos que JÁ TEMOS preservarem CROP.

## ENTREGA

INITIAL_HEAD = / FINAL_HEAD = / REMOTE_HEAD = / WORKTREE_CLEAN =
T3_TOTAL = / T3_REDERIVED =
CROP_PRESENT_IN_SOURCE = / CROP_RECOVERED = / CROP_STILL_UNKNOWN =
CROP_LOSS_ROOT_CAUSE =
DERIVED_CROP_AVAILABLE = / INTELLIGENCE_CAN_CONSUME_CROP =
AUTHORIZED_CROP_CASE = / UNAUTHORIZED_CROP_CASE = / UNKNOWN_CROP_CASE =
NEW_OBSERVATIONS_CREATED = 0
NEW_COLLECTION_RUNS = 0
NETWORK_REQUESTS = 0
PAID_USD = 0
NEW_FAILURES = / SYSTEM_MAP_CHECK =
KNOW_HOW_DELTA =

Commit e push da branch crop-e2e-v1. Não tocar em main. Não fazer merge.

## EM PALAVRAS SIMPLES (secção obrigatória no relatório final)

Responder sem jargão:
1. onde exatamente a cultura estava se perdendo;
2. quantos dos 5 documentos recuperaram CROP;
3. se foi necessário recoletar algo;
4. se a Intelligence agora consegue enxergar a cultura;
5. se o gate regulatório finalmente distingue cultura autorizada, não
   autorizada e desconhecida;
6. se esses 5 itens podem ser reprocessados pela Intelligence.

## HARD STOP

NÃO: fazer nova Big Collection; buscar ARIF; alterar Source Curator; construir
Intelligence nova; criar oportunidade; mexer no Portal; implementar automação
Sala→Intelligence.

FOCO: RECUPERAR A CHAVE CROP QUE JÁ EXISTE NA EVIDÊNCIA.

Se a evidência for insuficiente em qualquer fase: declarar
NÃO SEI / PRECISA MEDIR e parar. Não fabricar valor para fechar métrica.
