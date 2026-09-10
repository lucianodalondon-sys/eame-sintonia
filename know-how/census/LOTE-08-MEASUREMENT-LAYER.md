# SINTONIA EAME — KNOW HOW — LOTE 08

> Registro durável dos aprendizados materiais do Lote 08 do censo da Collection. Não substitui Bíblia, runtime, provas ou System Map.

## CHECKPOINT AUDITADO

```text
REPO = lucianodalondon-sys/eame-sintonia
BRANCH = claude/collection-plumbing-canonical-v1
HEAD = 572647dce8a38b8835aafa6f9e3e42d2652fbcd9
MODE = READ_ONLY
```

## RESULTADO DO LOTE

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

Cards:

```text
C-SAUDE-FONTE
C-CENSO-EXECUTORES
C-CENSO-OBSERVABILIDADE
C-CONTRATO-CAMPOS
C-REGRA-COLETA
C-RELATORIO-FLUXO
```

Estado acumulado depois do lote:

```text
AUDITED_COLLECTION_NODES = 44 / 64
AUDITED_DECLARED = 43 / 54
AUDITED_SYNTHETIC = 1 / 10
REMAINING_DECLARED = 11
REMAINING_SYNTHETIC = 9
```

## LIÇÃO 1 — MEDIR NÃO É BLOQUEAR

Nenhum dos seis componentes auditados bloqueia diretamente a Collection em runtime. Alguns medem fatos reais; outros publicam estados derivados ou literais; mas a camada, como conjunto, é observacional e não enforcement do runtime.

Regra:

> Um MEASURE pode estar correto e ainda não impedir um defeito. Sempre separar `MEASURED`, `GATED` e `RUNTIME_ENFORCED`.

Não chamar a camada inteira de “narrativa”: `C-SAUDE-FONTE` e `C-RELATORIO-FLUXO` medem dados reais. O problema é cobertura e poder de enforcement, não ausência total de medição.

## LIÇÃO 2 — OITO DEFEITOS CONHECIDOS FICAM FORA DA COBERTURA

Contra os defeitos já provados nos Lotes 06/07, nenhum dos seis mede de forma suficiente:

```text
A. módulo existe mas não carrega
B. workflow YAML coleta/escreve RAW
C. writer direto de banco fora do owner
D. coleta pula Pedido/Orquestrador/Ingresso
E. saída sem consumidor
F. path funciona somente em outra máquina
G. contrato existe mas não é consumido
H. edge nasce de literal/prosa em vez de relação real
```

Regra:

> Observabilidade precisa ser desenhada contra classes de falha reais, não somente contra dimensões que já são fáceis de contar.

## LIÇÃO 3 — CENSO DE EXECUTORES NÃO É CENSO DE TODA A EXECUÇÃO

`C-CENSO-EXECUTORES` descobre somente `.py` no topo de quatro gavetas (`coleta`, `guarda`, `ferramentas`, `orquestrador`). Não vê MJS, YAML, shell, heredoc e subdiretórios. Também não resolve imports e não detecta módulo que existe mas não carrega.

Ele consegue distinguir parcialmente `CAN DO` de `DID DO` porque consulta `provas-de-execucao.json`, mas esse ledger não possui writer encontrado no repositório auditado e é mantido como declaração.

Regra:

> Inventário de executor deve separar `FILE_FOUND`, `LOADABLE`, `REGISTERED`, `WIRED`, `RAN` e `PROVED`. Extensão/pasta não prova executabilidade.

## LIÇÃO 4 — PROOF LEDGER MANUAL NÃO É PROVA AUTOATUALIZADA

`system-map/data/provas-de-execucao.json` é consumido por censos e testes, mas nenhum writer foi encontrado no repositório durante a medição do lote.

Regra:

> Booleano `PROVED=true` em artefato mantido manualmente é uma declaração de prova, não a execução da prova. Quando possível, consumir a evidência executável e o exit code do dono real.

## LIÇÃO 5 — OBSERVABILIDADE NÃO PODE TER DIMENSÃO “MEDIDA” POR LITERAL

`C-CENSO-OBSERVABILIDADE` possui uma dimensão realmente medida (cobertura de instrumentação) e outras dimensões publicadas a partir de literais ou de números de outros censos. `ARCHITECTURE = MEDIDO` foi encontrado sem medição correspondente dentro desse censo.

Regra:

> Estado `MEDIDO/PROVED/OBSERVED` precisa carregar `MEASURED_BY`, `INPUT`, `RUN/HEAD` e evidência. Literal não promove estado epistemológico.

## LIÇÃO 6 — CONTRATO DE CAMPOS E CLASSIFICADOR SEMÂNTICO SÃO PERGUNTAS DIFERENTES

`C-CONTRATO-CAMPOS` mistura:

```text
A. forma/cobertura de 32 campos
B. classificação lexical de crop, issue, molecule, fact location, content type e originality
```

Os 32 campos são tratados como opcionais/UNKNOWN; não há enforcement geral da Collection. `FACT_TIME`, `RAW_ID` e `PARENT_ID` nem existem nesse contrato auditado.

Regra:

> Schema/field contract declara forma. Classificador atribui significado. Não unir ambos somente porque usam o mesmo registro.

`C-CONTRATO-CAMPOS = SPLIT_CANDIDATE` pelo critério de perguntas independentes.

## LIÇÃO 7 — REGRA DE COLETA QUE OLHA DEPOIS NÃO É PORTA DE ENTRADA

`C-REGRA-COLETA` mistura lei/policy em Markdown, gate sobre artefatos espanhóis já publicados e medição EAME. Nenhum workflow/Orquestrador/Executor consulta os gates auditados e eles não usam exit code para bloquear runtime.

Medido:

```text
COLLECTION_RULE_IS_RUNTIME_ENFORCED = NO
COVERS_ALL_COLLECTION_MECHANISMS = NO
BYPASS_CAN_EXIST_WHILE_RULE_IS_GREEN = YES
```

Regra:

> Gate “antes de coletar” precisa ser chamado antes da coleta. Avaliar artefato pós-coleta é auditoria/medição, não precondition operacional.

`C-REGRA-COLETA = SPLIT_CANDIDATE`.

## LIÇÃO 8 — RELATÓRIO PODE SER HONESTO E AINDA TER ESCOPO ESTREITO

`C-RELATORIO-FLUXO` lê o ledger italiano e prova corridas/observações que existem. Ele não prova qual código produziu as linhas, nem que o RAW apontado está acessível. `A_CONTA_FECHA=true` significa que a contabilidade de observações fecha dentro do ledger, não que toda evidência por trás dessas observações esteja disponível.

Regra:

> Toda frase verde precisa carregar a pergunta exata que respondeu. `A_CONTA_FECHA` não pode ser apresentada como “o fluxo inteiro está saudável”.

## LIÇÃO 9 — TRÊS CLASSES DE “FALSO VERDE”

O lote consolidou três categorias úteis:

```text
PROOF_FALSE
= a própria proposição publicada não tem medição suficiente.

PROOF_SCOPE_TOO_NARROW
= a medição é verdadeira, mas responde a uma pergunta menor.

SURFACE_OVERCLAIMS_PROOF
= a evidência pode ser legítima, mas o nome/estado mostrado promete mais do que ela prova.
```

Regra:

> Antes de corrigir uma prova, descobrir qual das três falhas ocorreu. Nem todo verde enganoso exige mudar a medição; às vezes precisa mudar a superfície/nome/escopo.

## LIÇÃO 10 — ARTEFATO GERADO PRECISA DE PROVENANCE DO SNAPSHOT

Na amostra examinada durante o lote, `executores.generated.json` e `semantica-it.generated.json` estavam carimbados em um HEAD anterior (`243cd25`), enquanto nove artefatos examinados não tinham bloco `PROVENANCE`, incluindo `observabilidade.generated.json` e `fluxo.generated.json`.

Escopo: isso foi uma medição read-only limitada aos 21 artefatos examinados; não é censo total de todo `*.generated.json` do repositório.

Regra:

> Resultado gerado precisa declarar pelo menos `SOURCE_HEAD`, gerador e momento/run. Sem isso, “gerado” não significa “descreve esta árvore”.

## LIÇÃO 11 — PROSA HUMANA CONTINUA GERANDO EDGES FALSAS

Seis das 38 edges auditadas eram falsas e compartilhavam o mesmo padrão: nomes de arquivos dentro de strings explicativas como `ONDE`, `ONDE_SE_VE`, `DERIVADO_DE` sendo tratados como leitura real.

Regra:

> String que explica onde uma coisa vive é META/PROSA, não READ. Scanner deve exigir operação semântica compatível com o tipo da edge.

## LIÇÃO 12 — GENERATED JSON SEM CARD PODE APAGAR DATA EDGES

Duas edges reais ficaram ausentes porque os artefatos intermediários `fluxo.generated.json` e `donos.generated.json` eram produzidos/consumidos mas não estavam reclamados como arquivos de um componente, então o mapa não tinha nó onde prender a relação.

Regra:

> Artefato gerado que participa de produtor → consumidor precisa ter owner/representação explícita. Arquivo intermediário sem owner torna o data flow invisível.

## LIÇÃO 13 — A CAMADA DE MEDIÇÃO DEVE SER CORE

Portabilidade medida:

```text
C-SAUDE-FONTE           CORE
C-CENSO-EXECUTORES      CORE
C-CENSO-OBSERVABILIDADE MIXED
C-CONTRATO-CAMPOS       MIXED
C-REGRA-COLETA          EAME no papel / country-specific no código
C-RELATORIO-FLUXO       country-specific por hard-code
```

Regra:

> Ao criar novo país, coletores/adapters podem ser locais; medidores de arquitetura, executabilidade, lineage, ownership e observabilidade devem tender a CORE parametrizado. Hard-code de país dentro do medidor multiplica custo e mascara diferenças.

## VEREDITOS PROVISÓRIOS

```text
C-SAUDE-FONTE           KEEP
C-CENSO-EXECUTORES      KEEP
C-CENSO-OBSERVABILIDADE KEEP
C-CONTRATO-CAMPOS       SPLIT_CANDIDATE
C-REGRA-COLETA          SPLIT_CANDIDATE
C-RELATORIO-FLUXO       KEEP
```

## PRÓXIMO PASSO

Restam 11 componentes declarados e 9 sintéticos no snapshot do censo. Prosseguir em lotes pequenos, mantendo o censo read-only e adiando correções para a consolidação transversal.
