# SINTONIA EAME — COLLECTION CARD AUDIT REGISTRY

> Registro durável do censo de cards da Collection. Não é a Bíblia e não muda a fotografia auditada. Existe para impedir que o histórico de lotes dependa de chat, scratchpad ou container temporário.

## FOTOGRAFIA DO CENSO

```text
REPO = lucianodalondon-sys/eame-sintonia
CENSUS_BRANCH = claude/collection-plumbing-canonical-v1
CENSUS_HEAD = 572647dce8a38b8835aafa6f9e3e42d2652fbcd9
```

## UNIVERSO MEDIDO

```text
COLLECTION_MAP_NODES = 64
DECLARED_COLLECTION_COMPONENTS = 54
SYNTHETIC_GENERATED_COLLECTION_NODES = 10
```

Sintéticos medidos:

```text
C-AS-FONTES
C-IT-PDF-BRUTO
C-ARMAZEM-IT-SEM-LIVRO
C-DERIVED-ARTIFACT
C-IT-TEXTO-DERIVADO
V-YOUTUBE
V-INSTAGRAM
V-LINKEDIN
V-FACEBOOK
V-HTTP
```

## ESTADO APÓS LOTE 09

```text
AUDITED_COLLECTION_NODES = 50 / 64
AUDITED_DECLARED = 49 / 54
AUDITED_SYNTHETIC = 1 / 10
REMAINING_DECLARED = 5
REMAINING_SYNTHETIC = 9
```

Além desses, 4 cards auditados historicamente pertencem hoje a F-GOVERNANCA e não entram no denominador da Collection.

## LOTE 01

Collection:

```text
C-CI-COLETA
C-PEDIDO
C-RECEITAS
C-ORQUESTRADOR
C-AS-FONTES   [SYNTHETIC]
```

Auditado no mesmo lote mas fora da Collection atual:

```text
C-POLITICA-COLETA   [F-GOVERNANCA]
```

## LOTE 02

```text
C-SENSOR-COLETA
C-SINTONIA-SCRAP
C-SCRAP-ROTA
C-SCRAP-SOCIAL
C-COLETA-PUBLICA
C-APIFY-POOL
```

## LOTE 03

Collection:

```text
C-COLETA-BASE
C-COLETA-INSTAGRAM
C-COLETA-YOUTUBE
C-NAVEGADOR
C-SCRAP-GUARDA
```

Auditado no mesmo lote mas fora da Collection atual:

```text
C-SCRAP-LEIS   [F-GOVERNANCA]
```

## LOTE 04

```text
C-INGRESSO
C-DONO-DA-ESCRITA
C-DONO-DO-DERIVADO
C-DERIVACAO-FORWARD
C-PROCEDENCIA
C-RASTRO
```

## LOTE 05

Collection:

```text
C-IMPORTAR
C-ADMISSAO
C-ROTULOS
C-IT-PRESERVAR
```

Auditados no mesmo lote mas fora da Collection atual:

```text
C-ESTRADAS-IT          [F-GOVERNANCA]
C-PROVA-ENCANAMENTO    [F-GOVERNANCA]
```

## LOTE 06

```text
C-CI-PERSIST
C-SUPABASE
C-EXECUTOR-TEXTO-PDF
C-ROTA-M2
C-TRANSCRICAO
C-PADRAO-COLETA
```

Resultado do lote:

```text
CARDS_AUDITED = 6/6
MAP_EDGES_AUDITED = 70/70
MISSING_RUNTIME_EDGES = 9
FALSE_EDGES = 1
EVIDENCE_MISPLACED = 8
TYPE_WRONG = 1
UNKNOWN_RELATIONS = 0
LOTE_06_CLOSED = YES
```

Vereditos provisórios:

```text
C-CI-PERSIST          SPLIT_CANDIDATE
C-SUPABASE            SPLIT_CANDIDATE / AGRUPAMENTO VISUAL
C-EXECUTOR-TEXTO-PDF  SPLIT_CANDIDATE
C-ROTA-M2             KEEP
C-TRANSCRICAO         SPLIT_CANDIDATE
C-PADRAO-COLETA       KEEP, com reclassificação futura a estudar
```

## LOTE 07

```text
C-PORTA-FONTE
C-IT-CATALOGO
C-FONTES-EU
C-IT-COLETA
C-IT-CONTRATOS
C-IDENTIDADE
```

Resultado do lote:

```text
CARDS_AUDITED = 6/6
MAP_EDGES_AUDITED = 41/41
MISSING_RUNTIME_EDGES = 7
FALSE_EDGES = 2
EVIDENCE_MISPLACED = 5
TYPE_WRONG = 6
EXPECTED_ONLY = 5
UNKNOWN_RELATIONS = 0
LOTE_07_CLOSED = YES
```

Achado dominante: a cadeia italiana do snapshot auditado possui 10 imports relativos quebrados e componentes centrais falham em tempo de carga; recibos históricos de outros HEADs não provam executabilidade deste HEAD.

Vereditos provisórios reconciliados pela regra dura de split:

```text
C-PORTA-FONTE     KEEP
C-IT-CATALOGO     SPLIT_CANDIDATE
C-FONTES-EU       KEEP; MOVE_CANDIDATE para coleta/regulatorio_importar.py
C-IT-COLETA       SPLIT_CANDIDATE
C-IT-CONTRATOS    KEEP; guardas/scripts podem precisar MOVE/REMAP
C-IDENTIDADE      KEEP
```

Correções importantes do Lote 07:

```text
- gerar SQL não é escrever no banco;
- C-FONTES-EU não foi provado como writer direto de registro_regulatorio;
- C-IT-COLETA é o writer real de observations.ndjson e runs.ndjson;
- SOURCE_ID não tem owner/gerador canônico provado;
- CHANNEL_IDENTITY_NOT_RESOLVED continua OPEN;
- contratos italianos existem e são máquina-legíveis, mas só parte pequena governa runtime;
- o fluxo candidata → fonte registrada não existe de forma canônica;
- o coletor italiano não passa por Pedido → Orquestrador → Ingresso;
- 25 de 35 RAW apontam para caminho absoluto fora do repo auditado.
```

## LOTE 08

```text
C-SAUDE-FONTE
C-CENSO-EXECUTORES
C-CENSO-OBSERVABILIDADE
C-CONTRATO-CAMPOS
C-REGRA-COLETA
C-RELATORIO-FLUXO
```

Resultado do lote:

```text
CARDS_AUDITED = 6/6
MAP_EDGES_AUDITED = 38/38
TRUE = 25
FALSE_EDGES = 6
EVIDENCE_MISPLACED = 3
TYPE_WRONG = 4
EXPECTED_ONLY = 0
UNKNOWN_RELATIONS = 0
MISSING_RUNTIME_EDGES = 2
LOTE_08_CLOSED = YES
```

Achado dominante: a camada auditada mede partes reais do sistema, mas nenhuma das seis peças é runtime enforcement e, em conjunto, não detecta as oito classes de defeito já conhecidas dos Lotes 06/07.

Vereditos provisórios:

```text
C-SAUDE-FONTE           KEEP
C-CENSO-EXECUTORES      KEEP
C-CENSO-OBSERVABILIDADE KEEP
C-CONTRATO-CAMPOS       SPLIT_CANDIDATE
C-REGRA-COLETA          SPLIT_CANDIDATE
C-RELATORIO-FLUXO       KEEP
```

Correções e lições importantes do Lote 08:

```text
- medir != bloquear != enforcement;
- C-CENSO-EXECUTORES vê só .py no topo de 4 gavetas e não detecta broken import;
- provas-de-execucao.json não teve writer encontrado: PROVED manual precisa ser distinguido de prova executada;
- C-CENSO-OBSERVABILIDADE tem uma dimensão realmente medida e outras publicadas por literal/repasse;
- C-CONTRATO-CAMPOS mistura schema/cobertura com classificador semântico;
- C-REGRA-COLETA olha artefatos depois da coleta e não bloqueia runtime;
- C-RELATORIO-FLUXO mede o ledger, mas A_CONTA_FECHA não prova acessibilidade do RAW;
- falso verde deve ser separado em PROOF_FALSE, PROOF_SCOPE_TOO_NARROW e SURFACE_OVERCLAIMS_PROOF;
- generated artifacts precisam de provenance do snapshot.
```

## LOTE 09

```text
C-ESTRADA-PDF
C-LEITORES
C-IT-TEXTO-PESQUISAVEL
C-CORPUS
C-PALAVRAS
C-FRONTEIRA-TELEMETRIA
```

Resultado do lote:

```text
CARDS_AUDITED = 6/6
MAP_EDGES_AUDITED = 34/34
TRUE = 25
FALSE_EDGES = 0
EVIDENCE_MISPLACED = 5
TYPE_WRONG = 2
EXPECTED_ONLY = 2
UNKNOWN_RELATIONS = 0
MISSING_RUNTIME_EDGES = 3
LOTE_09_CLOSED = YES
```

Achado dominante: os seis não formam uma única pipeline. Existem duas rotas desligadas e uma fronteira de telemetria isolada. O caminho PDF observado não usa C-LEITORES, não passa por Ingresso, não chega a STRUCTURED/READY; o corpus científico nasce diretamente de OpenAlex/ORCID; e a triagem pós-transcrição existe em C-PALAVRAS para YouTube, mas não é cross-platform.

Vereditos provisórios:

```text
C-ESTRADA-PDF                  KEEP
C-LEITORES                     SPLIT_CANDIDATE
C-IT-TEXTO-PESQUISAVEL        RENAME_CANDIDATE
C-CORPUS                       SPLIT_CANDIDATE
C-PALAVRAS                     RENAME_CANDIDATE + SPLIT_CANDIDATE
C-FRONTEIRA-TELEMETRIA         KEEP
```

Correções e lições importantes do Lote 09:

```text
- golden path != production;
- proximidade visual != pipeline;
- reader precisa de interface/owner canônico;
- leitura != extração semântica;
- glob de .txt sem writer/chave/contrato != store;
- tradução é derivação de segunda ordem e precisa de parent/language/executor;
- corpus precisa declarar unidade (WORK/PERSON/CHANNEL/etc.);
- vocabulário (dados) != classificador (decisão);
- post-transcription triage existe para YouTube; o GAP é cross-platform;
- saída sem consumidor deve ser declarada como dead-end/unconsumed;
- dispatch por recipe/registry e path computado criam edges reais invisíveis a scanner literal;
- path/filename != identidade/lineage;
- decision lineage (evidência exata do rótulo) é ativo a preservar;
- CONTRACT_READY != INSTRUMENTED != OBSERVED;
- telemetria por etapa/run != lineage de item;
- status de card não pode herdar prova de apenas um subarquivo;
- censo semântico com lista fixa pode fechar sobre universo incompleto;
- para portabilidade, motor tende a CORE e léxico/recorte/localidade tende a COUNTRY overlay.
```

## REGRA DE ATUALIZAÇÃO

Depois de cada lote fechado:

1. acrescentar os IDs auditados;
2. separar Collection de Governança/Prova;
3. marcar sintéticos explicitamente;
4. atualizar os quatro contadores do estado;
5. nunca promover card a auditado por ter aparecido apenas como vizinho;
6. nunca apagar histórico de lote;
7. se a fotografia de censo mudar, abrir nova seção de snapshot em vez de misturar universos;
8. quando resumo final contradizer o critério detalhado, reconciliar pela evidência e registrar a correção;
9. distinguir `MEASURED`, `GATED` e `RUNTIME_ENFORCED`;
10. nunca tratar estado `PROVED/MEDIDO/OBSERVED` como autoexplicativo: exigir origem/evidência e snapshot quando aplicável;
11. distinguir `GOLDEN_PATH`, `TEST/PROOF` e `PRODUCTION`;
12. registrar explicitamente outputs sem consumidor e componentes sem owner;
13. não promover path/filename a identidade ou lineage;
14. manter motores reutilizáveis separados de overlays de país.
