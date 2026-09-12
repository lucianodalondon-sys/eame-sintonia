# SINTONIA EAME — COLLECTION CARD AUDIT REGISTRY

> Registro durável do censo de cards da Collection. Não é a Bíblia, não muda a fotografia auditada e não substitui os dossiês de cada lote. Existe para impedir que o histórico de auditoria dependa de chat, scratchpad ou container temporário.

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

## ESTADO FINAL DO CENSO DA FOTOGRAFIA

```text
AUDITED_COLLECTION_NODES = 64 / 64
AUDITED_DECLARED = 54 / 54
AUDITED_SYNTHETIC = 10 / 10
REMAINING_DECLARED = 0
REMAINING_SYNTHETIC = 0

DECLARED_COLLECTION_CENSUS_CLOSED = YES
SYNTHETIC_COLLECTION_CENSUS_CLOSED = YES
FULL_COLLECTION_CENSUS_CLOSED = YES
READY_FOR_TRANSVERSAL_CONSOLIDATION = YES
```

Além desses, 4 cards auditados historicamente pertencem hoje a F-GOVERNANCA e não entram no denominador da Collection.

**Interpretação obrigatória:** `FULL_COLLECTION_CENSUS_CLOSED = YES` significa apenas que todos os 64 nós da fotografia foram explicados. Não significa arquitetura correta, runtime funcional, Collection pronta ou autorização para implementar.

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

```text
CARDS_AUDITED = 6/6
MAP_EDGES_AUDITED = 70/70
MISSING_RUNTIME_EDGES = 9
FALSE_EDGES = 1
EVIDENCE_MISPLACED = 8
TYPE_WRONG = 1
LOTE_06_CLOSED = YES
```

Vereditos provisórios:

```text
C-CI-PERSIST          SPLIT_CANDIDATE
C-SUPABASE            SPLIT_CANDIDATE / AGRUPAMENTO VISUAL
C-EXECUTOR-TEXTO-PDF  SPLIT_CANDIDATE
C-ROTA-M2             KEEP
C-TRANSCRICAO         SPLIT_CANDIDATE
C-PADRAO-COLETA       KEEP
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

```text
CARDS_AUDITED = 6/6
MAP_EDGES_AUDITED = 41/41
MISSING_RUNTIME_EDGES = 7
FALSE_EDGES = 2
EVIDENCE_MISPLACED = 5
TYPE_WRONG = 6
EXPECTED_ONLY = 5
LOTE_07_CLOSED = YES
```

Vereditos provisórios reconciliados pela regra dura de split:

```text
C-PORTA-FONTE     KEEP
C-IT-CATALOGO     SPLIT_CANDIDATE
C-FONTES-EU       KEEP; MOVE_CANDIDATE para coleta/regulatorio_importar.py
C-IT-COLETA       SPLIT_CANDIDATE
C-IT-CONTRATOS    KEEP; guardas/scripts podem precisar MOVE/REMAP
C-IDENTIDADE      KEEP
```

Achados dominantes: imports relativos italianos quebrados no snapshot; recibo histórico não prova executabilidade do HEAD; SOURCE_ID sem owner canônico provado; contratos parcialmente aplicados; coletor italiano fora de Pedido→Orquestrador→Ingresso; writer real do ledger em C-IT-COLETA; paths absolutos locais em parte do RAW.

## LOTE 08

```text
C-SAUDE-FONTE
C-CENSO-EXECUTORES
C-CENSO-OBSERVABILIDADE
C-CONTRATO-CAMPOS
C-REGRA-COLETA
C-RELATORIO-FLUXO
```

```text
CARDS_AUDITED = 6/6
MAP_EDGES_AUDITED = 38/38
TRUE = 25
FALSE_EDGES = 6
EVIDENCE_MISPLACED = 3
TYPE_WRONG = 4
MISSING_RUNTIME_EDGES = 2
LOTE_08_CLOSED = YES
```

Vereditos provisórios:

```text
C-SAUDE-FONTE           KEEP
C-CENSO-EXECUTORES      KEEP
C-CENSO-OBSERVABILIDADE KEEP
C-CONTRATO-CAMPOS       SPLIT_CANDIDATE
C-REGRA-COLETA          SPLIT_CANDIDATE
C-RELATORIO-FLUXO       KEEP
```

Achado dominante: a camada mede partes reais, mas não é runtime enforcement e não enxerga classes relevantes de defeito já conhecidas. `PROOF_FALSE`, `PROOF_SCOPE_TOO_NARROW` e `SURFACE_OVERCLAIMS_PROOF` devem permanecer estados distintos.

## LOTE 09

```text
C-ESTRADA-PDF
C-LEITORES
C-IT-TEXTO-PESQUISAVEL
C-CORPUS
C-PALAVRAS
C-FRONTEIRA-TELEMETRIA
```

```text
CARDS_AUDITED = 6/6
MAP_EDGES_AUDITED = 34/34
TRUE = 25
FALSE_EDGES = 0
EVIDENCE_MISPLACED = 5
TYPE_WRONG = 2
EXPECTED_ONLY = 2
MISSING_RUNTIME_EDGES = 3
LOTE_09_CLOSED = YES
```

Vereditos provisórios:

```text
C-ESTRADA-PDF                  KEEP
C-LEITORES                     SPLIT_CANDIDATE
C-IT-TEXTO-PESQUISAVEL        RENAME_CANDIDATE
C-CORPUS                       SPLIT_CANDIDATE
C-PALAVRAS                     RENAME_CANDIDATE + SPLIT_CANDIDATE
C-FRONTEIRA-TELEMETRIA         KEEP
```

Achado dominante: os seis não formam uma pipeline única; golden path não é produção; quatro maneiras de abrir PDF sem interface canônica; texto pesquisável não é store real; corpus mistura unidades; C-PALAVRAS contém classificador/relevance/triagem pós-transcrição de YouTube; telemetria é CORE mas cobre poucos executores.

## LOTE 10 — FECHAMENTO DO DECLARED

```text
C-BIBLIA
C-ADAMA-IT
C-ADAMA-ES
C-BANCO-NO-SECO
C-CICATRIZES-BR
```

```text
CARDS_AUDITED = 5/5
MAP_EDGES_AUDITED = 19/19
TRUE = 12
FALSE_EDGES = 2
EVIDENCE_MISPLACED = 2
TYPE_WRONG = 2
EXPECTED_ONLY = 1
MISSING_RUNTIME_EDGES = 3
LOTE_10_CLOSED = YES
DECLARED_COLLECTION_CENSUS_CLOSED = YES
```

Vereditos provisórios:

```text
C-BIBLIA        SPLIT_CANDIDATE + MOVE_CANDIDATE -> GOVERNANCE
C-ADAMA-IT      SPLIT_CANDIDATE + RENAME_CANDIDATE; MIXED country/reference-data/proof
C-ADAMA-ES      MOVE_CANDIDATE + SPLIT_CANDIDATE; frozen/future handoff
C-BANCO-NO-SECO MOVE_CANDIDATE -> PROOF/INFRASTRUCTURE
C-CICATRIZES-BR MOVE_CANDIDATE + RENAME_CANDIDATE -> GOVERNANCE/CORE KNOW HOW
```

Achados dominantes:

```text
- C-BIBLIA é autoridade de governança, não etapa operacional; lei, registry, conformidade de país, censos e logs estão misturados.
- Há duas formas de a máquina ler a lei: leis.json derivado e parsing direto do markdown.
- C-ADAMA-IT mistura catálogo/rótulos locais com reference data EU/global (Reg. 540/2011, FRAC/HRAC/IRAC) e QA.
- C-ADAMA-ES tem artefato observado, mas runtime quebrado/congelado no snapshot; output existente não prova gerador vivo.
- C-BANCO-NO-SECO é test double CORE e não finge provar Postgres real.
- As 35 cicatrizes do Brasil são princípios reutilizáveis do SINTONIA; Brasil é proveniência do aprendizado, não escopo da regra.
- Há literais `family` obsoletos que contradizem a família derivada da zona e são ignorados silenciosamente.
- `registro_regulatorio` continua sem owner canônico provado.
```

## SYNTHETIC CENSUS — FECHAMENTO FINAL

O sintético `C-AS-FONTES` já havia sido auditado no Lote 01. A missão final auditou:

```text
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

```text
SYNTHETIC_AUDITED = 9/9 nesta missão
MAP_EDGES_AUDITED = 27/27
TRUE = 21
EVIDENCE_MISPLACED = 5
EXPECTED_ONLY = 1
MISSING_RUNTIME_EDGES = 7
FALSE_EDGES = 0
UNKNOWN_RELATIONS = 0
SYNTHETIC_COLLECTION_CENSUS_CLOSED = YES
FULL_COLLECTION_CENSUS_CLOSED = YES
```

Classificação final:

```text
C-AS-FONTES                    synthetic medido; histórico L01
C-IT-PDF-BRUTO                 SYNTHETIC_STORE; KEEP_SYNTHETIC
C-ARMAZEM-IT-SEM-LIVRO        SYNTHETIC_STORE; KEEP_SYNTHETIC
C-DERIVED-ARTIFACT             SYNTHETIC_STORE; RENAME_SYNTHETIC_CANDIDATE
C-IT-TEXTO-DERIVADO           SYNTHETIC_ARTIFACT; KEEP_SYNTHETIC
V-YOUTUBE                      SYNTHETIC_PLATFORM; KEEP_SYNTHETIC
V-INSTAGRAM                    SYNTHETIC_PLATFORM; KEEP_SYNTHETIC
V-LINKEDIN                     SYNTHETIC_PLATFORM; KEEP_SYNTHETIC
V-FACEBOOK                     SYNTHETIC_PLATFORM; KEEP_SYNTHETIC
V-HTTP                         SYNTHETIC_PROTOCOL; KEEP_SYNTHETIC
```

Achados dominantes:

```text
- `synthetic` junta duas famílias diferentes: nós de medição/estado e nós de taxonomia/veículo.
- C-IT-PDF-BRUTO representa 49 PDFs, 43 conteúdos únicos, com múltiplos writers e sem owner canônico.
- C-ARMAZEM-IT-SEM-LIVRO representa storage externo observado sem raw_asset/collection_run IT; uploader indicado está fora do repo.
- C-DERIVED-ARTIFACT é store, distinto do owner C-DONO-DO-DERIVADO; a edge owner->store está ausente.
- C-IT-TEXTO-DERIVADO é saída machine TEXT_EXTRACTION e não duplica o acervo manual/searchable.
- plataforma != account != source_id; V-* social não identifica quem foi coletado.
- V-HTTP é protocolo/transporte, não a mesma espécie dos quatro V-* sociais.
- a taxonomia de plataformas tem três autoridades: lei 11, persistência 9, mapa 4 sociais.
- scanner `ABRE_O_CANAL` ainda aceita docstring/string/contador de zero em provas; filtros anti-prosa não são aplicados uniformemente.
- synthetics com `files=[]` ficam invisíveis ao mecanismo genérico de FILE_EDGE e podem aparecer órfãos mesmo com relações reais.
- synthetic correto pode revelar owner ausente ao redor dele sem precisar virar card.
```

Responsabilidades/autoridades ausentes reveladas pelo synthetic census:

```text
SYN-H-001  fronteira/owner do uploader externo do Storage IT
SYN-H-002  owner canônico do acervo bruto italiano em disco
SYN-H-003  resolver dois livros do DERIVED: registro Git vs public.derived_artifact
```

## PRÓXIMA FASE

```text
READY_FOR_TRANSVERSAL_CONSOLIDATION = YES
```

A próxima fase deve consolidar toda a fotografia antes de implementar: KEEP, SPLIT, MOVE, RENAME, duplicate authorities, hidden responsibilities, missing/false edges, bypasses, owners ausentes, stores sem owner, outputs sem consumidor, gaps e classes CORE/EAME/COUNTRY, usando o Card Contract V1 como critério de arquitetura-alvo.

## REGRA DE ATUALIZAÇÃO

Depois de cada lote fechado ou fase material:

1. acrescentar os IDs auditados;
2. separar Collection de Governança/Prova;
3. marcar sintéticos explicitamente;
4. atualizar os contadores do snapshot;
5. nunca promover card a auditado por ter aparecido apenas como vizinho;
6. nunca apagar histórico de lote;
7. se a fotografia de censo mudar, abrir nova seção de snapshot em vez de misturar universos;
8. quando resumo final contradizer o critério detalhado, reconciliar pela evidência e registrar a correção;
9. distinguir `MEASURED`, `GATED` e `RUNTIME_ENFORCED`;
10. nunca tratar `PROVED/MEDIDO/OBSERVED` como autoexplicativo: exigir origem/evidência e snapshot;
11. distinguir `GOLDEN_PATH`, `TEST/PROOF` e `PRODUCTION`;
12. registrar outputs sem consumidor e componentes sem owner;
13. não promover path/filename a identidade ou lineage;
14. manter motores reutilizáveis separados de overlays de país;
15. `OUTPUT_OBSERVED != GENERATOR_RUNTIME_ALIVE`;
16. `DRY_TESTED != DB_TESTED`;
17. proveniência local de um aprendizado não torna a regra local;
18. `DECLARED_COLLECTION_CENSUS_CLOSED` não implica `FULL_COLLECTION_CENSUS_CLOSED`;
19. `FULL_COLLECTION_CENSUS_CLOSED` não implica arquitetura correta ou runtime pronto;
20. `SYNTHETIC` precisa ser classificado pelo mecanismo de criação e pelo conceito representado;
21. owner da responsabilidade e store/artefato representado são conceitos diferentes;
22. plataforma, transporte, account e SOURCE_ID não devem ser colapsados;
23. synthetic sem `files` precisa de mecanismo de edges por conceito/store/owner, não só por ownership de ficheiro.
