# SINTONIA EAME — COLLECTION — SYNTHETIC CENSUS FINAL CLOSURE

> Registro durável do fechamento dos nós sintéticos da fotografia de censo da Collection. Não altera a fotografia auditada, não corrige arquitetura e não substitui a Bíblia ou o runtime.

## CHECKPOINT

```text
REPO = lucianodalondon-sys/eame-sintonia
CENSUS_BRANCH = claude/collection-plumbing-canonical-v1
CENSUS_HEAD = 572647dce8a38b8835aafa6f9e3e42d2652fbcd9
PRECHECK = PASS
WORKTREE = CLEAN
```

## FECHAMENTO DO UNIVERSO

```text
COLLECTION_MAP_NODES = 64
AUDITED_COLLECTION_NODES = 64 / 64

DECLARED_COLLECTION_COMPONENTS = 54
AUDITED_DECLARED = 54 / 54
REMAINING_DECLARED = 0

SYNTHETIC_GENERATED_COLLECTION_NODES = 10
AUDITED_SYNTHETIC = 10 / 10
REMAINING_SYNTHETIC = 0

DECLARED_COLLECTION_CENSUS_CLOSED = YES
SYNTHETIC_COLLECTION_CENSUS_CLOSED = YES
FULL_COLLECTION_CENSUS_CLOSED = YES
READY_FOR_TRANSVERSAL_CONSOLIDATION = YES
```

Fechar o censo significa apenas que todos os 64 nós da fotografia foram explicados. Não significa que a arquitetura esteja correta, que o runtime funcione, que a Collection esteja pronta ou que implementação esteja autorizada.

## SYNTHETICS AUDITADOS

O sintético `C-AS-FONTES` já havia sido auditado historicamente. A missão final auditou os nove restantes:

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

## DUAS FAMÍLIAS DE SYNTHETIC

`synthetic` não é uma única espécie.

### Família A — nó literal + censo

```text
C-AS-FONTES
C-IT-PDF-BRUTO
C-ARMAZEM-IT-SEM-LIVRO
C-DERIVED-ARTIFACT
C-IT-TEXTO-DERIVADO
```

São criados por funções específicas do gerador. Identidade/nome/prosa são hard-coded; números e estados vêm de artefatos de medição. Em geral desaparecem se o artefato de censo necessário não existe.

### Família B — tabela fixa + varredura de código

```text
V-YOUTUBE
V-INSTAGRAM
V-LINKEDIN
V-FACEBOOK
V-HTTP
```

Nascem da tabela `CANAIS` no gerador. Os nós existem por taxonomia; a varredura decide estado/provas. Portanto Família A representa estados/artefatos medidos; Família B representa meios/plataformas/protocolo.

Regra de Know How:

> Nunca tratar `SYNTHETIC` como uma classe arquitetural homogênea. Primeiro classificar o mecanismo de criação e o conceito representado.

## RESULTADOS DOS QUATRO C-*

### C-IT-PDF-BRUTO

```text
CLASS = SYNTHETIC_STORE
REPRESENTS = acervo italiano em PDF no Git
PHYSICAL = YES
PDF_OCCURRENCES = 49
UNIQUE_CONTENTS = 43
CAPTURES = 24
OWNER = NONE
SINGLE_WRITER = NO
IS_CANONICAL_RAW = PARTIAL
VERDICT = KEEP_SYNTHETIC
```

Há dois writers de código e uma via manual/VPN. O acervo não tem owner canônico declarado. SHA identifica conteúdo, mas SOURCE_ID/ledger canônico não estão completos.

Regra:

> Um arquivo bruto em disco não vira RAW canônico apenas por existir. RAW canônico exige identidade, owner, proveniência e memória operacional compatíveis com o contrato.

### C-ARMAZEM-IT-SEM-LIVRO

```text
CLASS = SYNTHETIC_STORE
REPRESENTS = Supabase Storage raw/IT + ausência de ledger
OBJECTS = 195 (medição externa anterior)
RAW_ASSET_IT = 0
COLLECTION_RUN_IT = 0
OWNER = UNKNOWN
STORE_HAS_CONTRACT = NO
STORE_HAS_LEDGER = NO
UNTRACKED_STORAGE = YES
VERDICT = KEEP_SYNTHETIC
```

O uploader apontado (`scripts/storage_preservar.py --enviar`) não existe no repositório auditado. O store físico foi observado por medição externa, mas não há owner/contrato/ledger desta árvore.

Regra:

> Storage sem ledger é dado preservado sem memória operacional. O mapa deve distinguir existência física de governança canônica.

### C-DERIVED-ARTIFACT

```text
CLASS = SYNTHETIC_STORE
REPRESENTS = public.derived_artifact
OWNER = C-DONO-DO-DERIVADO
WRITER = guarda/preservar_derivado.py
LIVE = YES
VERDICT = RENAME_SYNTHETIC_CANDIDATE
```

O synthetic é a casa/store; `C-DONO-DO-DERIVADO` é o dono da escrita. Não são duplicatas. O nome `ALVO` é resíduo histórico porque a tabela já foi aplicada live.

Regra:

> Owner da escrita e store onde o estado vive são conceitos diferentes. Separá-los é correto; a edge owner→store precisa existir.

### C-IT-TEXTO-DERIVADO

```text
CLASS = SYNTHETIC_ARTIFACT
REPRESENTS = 43 textos TEXT_EXTRACTION com pai
WRITER = C-EXECUTOR-TEXTO-PDF
CONSUMER = C-ESTRADA-PDF -> C-ADMISSAO
PARENT = YES 43/43
VERDICT = KEEP_SYNTHETIC
```

Não sobrepõe `C-IT-TEXTO-PESQUISAVEL`: os caminhos e espécies são diferentes.

Regra:

> TEXT_EXTRACTION, MANUAL_TEXT, SEARCHABLE_TEXT e TRANSLATION são espécies diferentes e não devem ser colapsadas por extensão `.txt`.

## VEÍCULOS E PROTOCOLO

Os quatro sociais são `SYNTHETIC_PLATFORM`:

```text
V-YOUTUBE
V-INSTAGRAM
V-LINKEDIN
V-FACEBOOK
```

`V-HTTP` é `SYNTHETIC_PROTOCOL`.

Todos:

```text
HAS_OWN_CODE = NO
HAS_OWN_STATE = NO
DECIDES = NO
OWNER = NOT_APPLICABLE
RESPONSIBILITY_CARD_NEEDED = NO
```

Plataforma e transporte são eixos diferentes e podem coexistir na mesma chamada:

```text
PLATFORM = YouTube
TRANSPORT = HTTP
```

Regra:

> Plataforma não é SOURCE_ID, não identifica conta e não identifica quem foi coletado. É apenas um meio/eixo da relação.

O mapa hoje perde essa distinção porque as duas espécies podem sair como `VIAJA_POR`.

## VOCABULÁRIO DE PLATAFORMAS TEM TRÊS AUTORIDADES

Medido:

```text
leis/social_matriz.py = 11 plataformas
coleta/social_persistencia.py = 9 plataformas
generate_system_map.py::CANAIS = 4 sociais + HTTP
```

O mapa não deriva seus veículos da lei que declara as plataformas.

Regra:

> Taxonomia publicada pelo mapa deve derivar da autoridade canônica ou declarar explicitamente que é projeção parcial. Tabela manual paralela cria autoridade fantasma.

## EDGES DO SYNTHETIC CENSUS

```text
MAP_EDGES_AUDITED = 27 / 27
TRUE = 21
EVIDENCE_MISPLACED = 5
EXPECTED_ONLY = 1
MISSING_RUNTIME_EDGES = 7
FALSE_EDGES = 0
UNKNOWN_RELATIONS = 0
```

Cinco provas mal colocadas repetem um defeito já conhecido: o laço `ABRE_O_CANAL` lê texto cru e aceita docstring/string/contador de zero, enquanto outras partes do gerador já possuem filtros melhores.

Regra:

> Regras anti-prosa precisam ser reutilizadas por TODOS os scanners/loops de edge. Corrigir um laço e deixar outro antigo mantém a mesma classe de falso positivo.

## POR QUE SYNTHETIC STORES FICAM ÓRFÃOS

O motor genérico de edges só promove `FILE_EDGE` quando os dois arquivos têm owner declarado. Synthetics de store têm `files=[]`; portanto nunca recebem edges por essa via. Se a função específica que gera o synthetic não escrever as edges à mão, o nó vira órfão mesmo com relações reais.

Casos encontrados:

```text
C-ARMAZEM-IT-SEM-LIVRO = 0 edges no mapa
C-DERIVED-ARTIFACT = 0 edges no mapa
```

mas relações reais existem.

Regra:

> Nó synthetic sem arquivos precisa de um mecanismo de edge baseado no conceito/store/owner, não em ownership de ficheiro.

## ARESTAS REAIS AUSENTES IMPORTANTES

Foram encontradas naturalmente sete relações ausentes, incluindo:

```text
C-IT-COLETA -> C-IT-PDF-BRUTO              WRITES
C-IT-PRESERVAR -> C-IT-PDF-BRUTO           WRITES
C-DONO-DO-DERIVADO -> C-DERIVED-ARTIFACT   WRITES
C-SUPABASE -> C-DERIVED-ARTIFACT           DEFINES
C-DONO-DA-ESCRITA -> C-DERIVED-ARTIFACT    READS
C-DERIVACAO-FORWARD -> C-DERIVED-ARTIFACT  PRODUCES
C-ESTRADA-PDF -> C-IT-TEXTO-DERIVADO       READS
```

## RESPONSABILIDADES AUSENTES AO REDOR DOS SYNTHETICS

Os nós em si não precisam virar cards, mas revelaram owners/responsabilidades ausentes:

### SYN-H-001 — uploader externo do Storage IT

A responsabilidade `quem tem o direito de pôr bytes no armazém IT` está fora do repositório. Precisa de fronteira/owner explícito na arquitetura-alvo.

### SYN-H-002 — owner do acervo bruto italiano em disco

Hoje há múltiplos layouts/writers. A pergunta `qual é o caminho canônico de um PDF italiano preservado?` não tem owner único.

### SYN-H-003 — dois livros do DERIVED

```text
data/derivados/REGISTO-DE-ARTEFATOS.json = 43
public.derived_artifact = 1
```

A pergunta `qual é a verdade canônica sobre um derivado?` precisa ser resolvida na consolidação.

Regra:

> Synthetic pode estar correto como representação visual e ainda revelar ausência de owner ao redor dele. Não corrigir removendo o synthetic; corrigir a autoridade real.

## PORTABILIDADE

Princípios reutilizáveis:

```text
RAW_STORE = CORE concept; country é dimensão/path/data
DERIVED_ARTIFACT = CORE
TEXT_EXTRACTION contract = CORE
STORAGE_WITHOUT_LEDGER = CORE gap class
V-HTTP = CORE/external protocol
social platforms = EXTERNAL, reutilizadas entre países
accounts/sources = COUNTRY data
```

Regra:

> Não criar um card estrutural novo por país quando o conceito é CORE e o país é apenas dimensão do estado. Evitar padrões como `C-DE-PDF-ALEMAO`; preferir store/contrato CORE com country_scope.

## PRÓXIMO PASSO AUTORIZADO

```text
READY_FOR_TRANSVERSAL_CONSOLIDATION = YES
```

A próxima fase deve cruzar todos os lotes e construir uma arquitetura-alvo antes de qualquer implementação. Deve consolidar KEEP, SPLIT, MOVE, RENAME, duplicate authorities, hidden responsibilities, missing/false edges, bypasses, owners ausentes, stores sem owner, outputs sem consumidor, gaps e classes CORE/EAME/COUNTRY, usando o Card Contract V1 como critério futuro sem modificar a fotografia original.
