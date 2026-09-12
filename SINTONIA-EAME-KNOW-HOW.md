# SINTONIA EAME — KNOW HOW

> Memória operacional durável do projeto.  
> **Não é a Bíblia canônica. Não é o System Map. Não é um relatório de status.**  
> É o registro do **como pensamos, por que decidimos, como investigar, como construir, como provar e quais erros não repetir**.

**Criado em:** 2026-09-09  
**Repositório:** `lucianodalondon-sys/eame-sintonia`  
**Branch de criação:** `claude/sintonia-eame-know-how-v1`  
**Base de criação:** `572647dce8a38b8835aafa6f9e3e42d2652fbcd9`  
**Regra:** atualizar todos os dias em que houver avanço material de arquitetura, metodologia, medição ou decisão.

**Última atualização material:** 2026-09-11 — o estágio deixou de se perder entre a fronteira e a porta (secção 49; `FACT_TIME` não era o bloqueio).  
**Próxima missão autorizada:** `T2` não tem regra escrita em `PERGUNTAS_DO_UNIVERSO` — medir antes de escrever.

---

# 0. PARA QUE ESTE ARQUIVO EXISTE

O SINTONIA cresceu por muitas missões, branches, agentes, auditorias, red teams, descobertas e correções. A memória de chat ajuda durante a construção, mas não pode ser a única memória do projeto.

Este arquivo existe para impedir que a equipe volte a:

- redescobrir a mesma arquitetura;
- repetir erros já medidos;
- reconstruir decisões a partir de prompts antigos;
- confundir código que existe com fluxo que funciona;
- confundir mapa com runtime;
- confundir lei com implementação;
- perder o motivo de uma decisão quando a branch que a produziu deixa de ser a branch ativa;
- depender de memória humana ou memória de chat para saber “como esta casa trabalha”.

## O que entra aqui

Entra aqui conhecimento durável:

- princípios de arquitetura;
- método de investigação;
- método de prova;
- sequência de construção;
- papéis dos componentes;
- fronteiras entre Collection, Intelligence e Delivery;
- decisões importantes e o motivo delas;
- erros encontrados e o que eles ensinaram;
- padrões de prompt/trabalho que funcionaram;
- padrões que falharam;
- status arquitetural necessário para retomar o trabalho sem perder contexto;
- referências para leis, contratos, mapas e artefatos que são a autoridade real.

## O que NÃO entra aqui como autoridade

Este arquivo não substitui:

- `BIBLIA-CANONICA-DA-COLETA.md` — lei da Collection;
- schemas e contratos executáveis — definição de forma;
- runtime — prova do que realmente acontece;
- banco live — prova do estado operacional;
- System Map — visualização/medição da arquitetura;
- Git — história versionada;
- resultados de provas — evidência executável.

**Know How explica como chegar à verdade. Não declara sozinho que algo é verdade.**

---

# 1. REGRA-MÃE DO SINTONIA

> **NÃO SUPOR. MEDIR.**

Vocabulário obrigatório:

- se foi medido: dizer como;
- se foi inferido: marcar como inferência;
- se não há base: `NÃO SEI`, `UNKNOWN` ou `precisa medir`;
- ausência de evidência não vira evidência de ausência;
- zero só pode ser publicado quando zero foi realmente medido;
- erro de ferramenta não pode virar “não existe”; 
- falha de observabilidade não é automaticamente falha de Collection.

Distinções que nunca podem ser comprimidas:

```text
CAN DO != DID DO
MODULE EXISTS != EDGE EXISTS != FLOW EXISTS
DECLARED EDGE != OBSERVED EDGE
REPO SCHEMA != LIVE DATABASE STATE
ERROR != REJECTED
UNKNOWN != ZERO
NOT_RUN != ERROR
REUSED != REJECTED
SOURCE_LOCATION != FACT_LOCATION
COLLECTION_TIME != PUBLICATION_TIME != FACT_TIME
DOCUMENT READY != FACT READY
```

---

# 2. ORDEM DE CONSTRUÇÃO DO PROJETO

A ordem geral do SINTONIA EAME é:

```text
RÉGUAS
  ↓
COLETA
  ↓
FERRAMENTAS
  ↓
CASCO / PORTAL
```

Não inverter por ansiedade de demo.

Dentro da **Collection**, a ordem operacional atual é:

```text
1. CENSAR O AS-IS
2. ENTENDER TODOS OS CARDS E COMPONENTES ESCONDIDOS
3. CONSOLIDAR RESPONSABILIDADES
4. DESENHAR A ARQUITETURA-ALVO
5. ESCOLHER UM OWNER POR CONCEITO
6. CORRIGIR O RUNTIME REAL
7. REMOVER BYPASSES / DUPLICIDADES / WRITERS CONCORRENTES
8. LIGAR A ESPINHA CANÔNICA
9. PROVAR COM UM ITEM REAL DE PONTA A PONTA
10. ATUALIZAR O MAPA PARA REFLETIR A REALIDADE
```

**Nunca usar o System Map como desculpa para organizar só o desenho.**

---

# 3. O SYSTEM MAP

O System Map existe para permitir olhar o SINTONIA “de fora”, como um esquema elétrico ou mapa navegável.

Objetivo:

- ver departamentos/territórios;
- ver componentes;
- ver control flow;
- ver data flow;
- ver stores;
- ver regras;
- ver provas;
- ver consumidores;
- abrir um card e entender o que ele faz;
- encontrar gaps, bypasses, duplicidades, donos concorrentes e peças fora do lugar.

## Lei operacional do mapa

> **MAP SHOWS THE PROBLEM. MAP DOES NOT DECIDE THE ARCHITECTURE.**

O mapa deve ser consequência da arquitetura real.

Nunca assumir que uma edge desenhada prova runtime.

Tipos de edge devem permanecer separados:

```text
CONTROL
DATA
POLICY
RULE
CONFIG
READ
WRITE
CODE
PROOF
META
UNKNOWN
```

Erros históricos importantes do scanner:

- docstring sendo lida como rota;
- comentário virando edge;
- scanner lendo sua própria documentação;
- `import` tratado como control/data flow;
- caminho de arquivo dentro de `supabase/` confundido com conexão ao Supabase;
- writers `pathlib` invisíveis quando scanner só reconhecia `open(..., 'w')`;
- última atribuição de variável vencendo sem considerar escopo/ordem;
- provas que varrem apenas `.py` deixando `.yml`, `.mjs`, `.sql`, shell e `.cmd` invisíveis.

**Toda edge deve dizer por que existe e qual é o tipo de prova.**

---

# 4. CARD NÃO É FILE

Uma das principais lições do projeto:

> **CARD != FILE**

Card representa uma responsabilidade arquitetural.

Um arquivo pode:

- implementar parte de um card;
- implementar vários subcomponentes;
- ser prova;
- ser adapter;
- ser ferramenta;
- ser contrato;
- ser store;
- ser CLI;
- ser workflow.

Um card bom deve responder pelo menos:

```text
CARD_ID
NAME
TYPE
OWNER
PURPOSE
OWNS_QUESTION
WHO_CALLS_IT
INPUT
DECIDES
DOES
OUTPUT
READS
WRITES
CONSUMER
STATE PRODUCED
PROOF
```

Visual mental:

```text
                 CONTROL
                    ↓
             ┌────────────┐
DATA IN ────►│    CARD    │────► DATA OUT
RULE/POLICY ►│            │────► STATE OUT
CONFIG ─────►│            │
             └────────────┘
                │      └────► PROOF / TELEMETRY
                ↓
               STORE
```

## Tipos/arquetipos úteis

- TRIGGER
- CONTRACT
- REGISTRY
- POLICY
- ORCHESTRATOR
- EXECUTOR
- ADAPTER
- TOOL
- GATE
- TRANSFORM
- STORE
- SENSOR / MEASURE
- PROOF
- EXTERNAL / SURFACE

## Uma pergunta por owner

Exemplos:

```text
Pedido          = “o que foi pedido?”
Route Policy    = “qual rota pode/devemos usar?”
Orchestrator    = “como coordenar este pedido?”
Executor        = “como adquirir?”
APIFY Pool      = “qual credencial saudável usar?”
Ingress         = “como a saída do executor entra na Collection?”
RAW owner       = “qual original foi preservado?”
Derivation      = “o que nasceu do RAW?”
Admission       = “esta unidade pode entrar?”
READY           = “a Collection terminou?”
Sensor          = “o que aconteceu?”
```

Se um card possui duas perguntas fundamentais diferentes, é candidato a `SPLIT`.

---

# 5. CARD CONTRACT / CARD FACTORY — DIREÇÃO DE ARQUITETURA

Direção aprovada conceitualmente:

```text
NEED COMPONENT
   ↓
CARD FACTORY
   ↓
CARD DESCRIPTOR
   ↓
SCHEMA VALIDATOR
   ↓
ARCHITECTURE LINTER
   ↓
RUNTIME SCANNER
   ↓
SYSTEM MAP
```

O card deve ter duas metades separadas:

```text
DECLARED
vs
OBSERVED
```

Nunca promover declaração a runtime.

Separar também:

```text
LIFECYCLE:
PROPOSED / ACTIVE / DEPRECATED / RETIRED

EVIDENCE:
DECLARED / WIRED / OBSERVED / PROVEN / UNKNOWN
```

Direção futura de arquivos:

- Bíblia: lei;
- `system-map/contracts/card.schema.json`: contrato de card;
- `system-map/contracts/edge.schema.json`: contrato de edge;
- `component-types.json`: tipos;
- Skill Claude: procedimento de criação, sem duplicar a lei;
- hook/schema/CI: enforce determinístico;
- System Map: representação.

A criação direta manual de card no desenho não deve ser o fluxo final.

---

# 6. CONTROL PLANE E DATA PLANE DA COLLECTION

Lei arquitetural amadurecida:

```text
CONTROL PLANE
ENTRADA → PEDIDO → ORQUESTRADOR → EXECUTOR

DATA PLANE
SOURCE → EXECUTOR → RAW → DERIVAÇÕES → ADMISSÃO → READY
```

Uma versão mais completa da espinha que estamos construindo:

```text
GATILHO
  ↓
PEDIDO
  ↓
RECEITA / PLANO
  ↓
ORQUESTRADOR
  ↓
ROTA / EXECUTOR
  ↓
INGRESSO
  ↓
RAW
  ↓
DERIVED
  ↓
STRUCTURED
  ↓
ADMISSION
  ↓
READY
  ↓
SALA DE ESPERA
```

Collection deve parar em READY.

Intelligence não deve ser chamada “só para fechar o desenho”.

---

# 7. EM PALAVRAS FÁCEIS — O QUE CADA ETAPA FAZ

```text
PEDIDO
“o que eu quero buscar?”

EXECUTOR
“vou buscar de verdade”

INGRESSO
“esta é a porta oficial por onde o que voltou entra”

RAW
“guardo o original sem mexer”

DERIVED
“produzo algo a partir do original”

STRUCTURED
“coloco numa forma organizada que o sistema entende”

ADMISSION
“esta unidade pode entrar oficialmente?”

READY
“a Collection terminou o trabalho dela neste item”

SALA DE ESPERA
“fica aqui até a Intelligence vir buscar”
```

Uma analogia útil:

```text
PEDIDO       = encomenda
EXECUTOR     = quem vai buscar
INGRESSO     = portaria
RAW          = caixa original
DERIVED      = conteúdo extraído
STRUCTURED   = conteúdo organizado em gavetas
ADMISSION    = conferência
READY        = carimbo “pronto”
SALA ESPERA  = prateleira aguardando próximo departamento
```

---

# 8. LEIS OPERACIONAIS DA COLLECTION QUE NÃO PODEM SER ESQUECIDAS

```text
RAW != DERIVED != STRUCTURED != ADMISSION != READY
COLETAR != ADMITIR != JULGAR
ONE CONCEPT → ONE OWNER
COMMENT != EDGE
DOCSTRING != EDGE
IMPORT != CONTROL
PROOF != RUNTIME
MODEL != RUNTIME
REQUIRED FIELD != PERMISSION TO FABRICATE
```

Temporalidade/geografia/procedência:

```text
SOURCE_LOCATION != FACT_LOCATION
SOURCE_COUNTRY != FACT_COUNTRY
COLLECTION_TIME != PUBLICATION_TIME != FACT_TIME
```

Quando não houver prova:

```text
UNKNOWN / NÃO SEI
```

Nunca inferir silenciosamente país do fato, data do fato, pessoa, lugar ou relação apenas por escopo da coleta.

---

# 9. ORIGEM DAS LEIS E RELAÇÃO COM O SINTONIA BRASIL

O EAME deve reutilizar as leis maduras do SINTONIA Brasil quando elas já resolveram problemas de:

- temporalidade;
- geografia;
- procedência;
- identidade;
- relevância;
- voz;
- passaporte de evidência.

Não reinventar porque mudou o país.

Portar contrato significa:

1. localizar a lei/contrato canônico maduro;
2. entender a pergunta que ele resolve;
3. adaptar vocabulário/idioma/fonte quando necessário;
4. manter as distinções semânticas;
5. medir contra dados EAME;
6. só então promover.

---

# 10. MULTILÍNGUE

O acervo EAME é multilíngue.

Alvo de linguagem do projeto:

```text
PT / EN / IT / FR
```

Para vocabulários de conteúdo, a direção correta é:

```text
CONCEITO CANÔNICO
   ↓
TERMOS LOCAIS
PT / IT / ES / FR / EN
```

Não duplicar um dicionário dentro de cada executor.

**DICIONÁRIO COPIADO É DICIONÁRIO QUE ENVELHECE EM SILÊNCIO.**

---

# 11. VÍDEO / ÁUDIO — ARQUITETURA DESEJADA

O método deve servir a YouTube, Instagram, LinkedIn, Facebook e futuras plataformas.

A plataforma só deve decidir **como adquirir**.

Arquitetura desejada:

```text
YOUTUBE ──────┐
INSTAGRAM ────┤
LINKEDIN ─────┤
FACEBOOK ─────┤
OUTRO VIDEO ──┘
       ↓
SOURCE / PLATFORM ADAPTER
       ↓
MEDIA CONTENT
       ↓
CAPTION OU TRANSCRIÇÃO
       ↓
CONTENT TRIAGE
       ↓
STRUCTURED
       ↓
ADMISSION
       ↓
READY
```

Responsabilidades:

```text
Platform adapter
= “como pego este conteúdo?”

Caption/Whisper
= “o que foi falado?”

Content Triage
= “o que existe dentro deste conteúdo e serve ao SINTONIA?”

Structured
= “como represento o que achei?”

Admission
= “esta unidade pode entrar oficialmente?”
```

Nunca criar um cérebro diferente para relevância semântica em cada plataforma.

## Primeira peneira barata

Antes de gastar processamento:

- título;
- descrição;
- legenda pública;
- metadados;
- vocabulário barato.

Pergunta:

> “vale a pena gastar recurso para ouvir/ler mais?”

No YouTube existe `coleta/youtube_relevancia.py`, que decide a fila antes do Whisper.

## Segunda leitura — pós-transcrição

Depois que o conteúdo completo foi obtido/transcrito:

> “há informação útil aqui? qual?”

Direção de saída melhor que um booleano:

```text
FOUND:
- FIELD_OBSERVATION
- DISEASE
- PRODUCT
- COMPETITOR_ACTION
- SCIENCE
- REGULATORY
...

EVIDENCE:
- trechos
- timestamps

NOT_FOUND:
...

UNKNOWN:
...
```

Estado em 2026-09-09:

```text
CANONICAL_CROSS_PLATFORM_POST_TRANSCRIPTION_CONTENT_TRIAGE = NÃO PROVADO
```

Esse é um GAP arquitetural importante até que o censo prove um owner real.

---

# 12. ADMISSION

Admission deve responder uma pergunta:

> “este par (item, universo) pode entrar?”

Resultados não devem ser comprimidos:

```text
SIM
NAO
NAO_SEI
NAO_SE_APLICA
ERRO
```

`ERRO` não é `NAO`.

`NAO_SEI` não é `NAO`.

Admission atualmente possui responsabilidades demais em `admissao/admissao.py`:

```text
decidir()
escrever()
pronto_para_inteligencia()
```

Direção provável de arquitetura: separar decisão, persistência do livro e contrato READY, depois que o censo/consolidação autorizar.

## Léxico atual da Admission

Hoje existe `PERGUNTAS_DO_UNIVERSO` dentro de `admissao/admissao.py` com termos por universos como T7/T9/T4/T3.

Isso é responsabilidade candidata a sair dali para um registry/régua canônica de conceitos/termos.

Admission não deve ser dona do vocabulário só porque usa o vocabulário.

---

# 13. READY E SALA DE ESPERA

READY é a fronteira final da Collection.

A função atual `admissao.pronto_para_inteligencia()` devolve contrato de 11 campos e exige `decisao.resultado == SIM`.

A intenção é:

```text
COLLECTION FINISHED
↓
READY
↓
WAITING ROOM
↓
[STOP]
```

Intelligence consumer deve ser zero enquanto estivermos fechando Collection.

Uma sala de espera correta não é RAW/DERIVED storage.

Guardar o original é parte da Collection.

Sala de espera é onde fica **o que já terminou toda a Collection**.

---

# 14. INTELLIGENCE — FRONTEIRA E CADEIA

Collection não deve entregar diretamente para peças internas da Intelligence.

Alvo:

```text
COLLECTION
↓
READY CONTRACT
↓
WAITING ROOM
──────────────
INTELLIGENCE
```

A Intelligence canônica conceitualmente segue:

```text
INTELLIGENCE REQUIREMENT / KIT
→ KIQ
→ EVIDENCE SELECTION
→ OBSERVATION / CLAIM
→ ENTITY RESOLUTION
→ EVENT / RELATION
→ CORROBORATION / CONTRADICTION
→ INDICATORS
→ SIGNALS
→ COMPETING HYPOTHESES
→ JUDGMENT
→ FORECAST
→ IMPLICATION
→ WATCH / DO
→ DECISION / FEEDBACK
→ CALIBRATION / COLLECTION GAP
```

Distinções:

```text
Evidence != Claim != Fact != Signal != Hypothesis != Judgment != Forecast != Recommendation
Signal != Opportunity
Social attention != field incidence
```

LLM pode propor. Gate promove.

Intelligence pode abrir `COLLECTION GAP`, mas não deve chamar coletor diretamente.

---

# 15. REPOSITÓRIO E DISCIPLINA DE BRANCH

Repositório EAME:

```text
lucianodalondon-sys/eame-sintonia
```

Regra aprendida em 2026-09-09:

**mesmo nome de repositório não garante mesma fotografia de arquitetura.**

Antes de qualquer auditoria:

```text
git rev-parse --show-toplevel
git remote get-url origin
git rev-parse --abbrev-ref HEAD
git rev-parse HEAD
git status --porcelain
git worktree list --porcelain
```

Para censo Collection atual, fotografia de referência:

```text
BRANCH = claude/collection-plumbing-canonical-v1
HEAD   = 572647dce8a38b8835aafa6f9e3e42d2652fbcd9
```

Arquivos que ajudaram a provar a fotografia correta:

```text
coleta/ingresso.py
guarda/preservar_coleta.py
guarda/preservar_derivado.py
coleta/derivacao_forward.py
```

Erro que não repetir:

- rodar censo numa clone/worktree/branch diferente;
- aceitar ausência de arquivos como descoberta arquitetural antes de validar repo/branch/HEAD;
- checkout em worktree suja para “corrigir” snapshot;
- misturar resultado de duas fotografias no mesmo censo.

---

# 16. PROMPT / CLAUDE CODE — COMO TRABALHAR MELHOR

Aprendizado prático:

> **PROMPT CURTO → EXECUÇÃO LONGA → VERIFICAÇÃO FORTE**

Não repetir no prompt o que o repositório já sabe.

Um bom prompt contém:

- missão;
- base/HEAD;
- autoridade a ler;
- resultado desejado;
- limites;
- provas objetivas de conclusão.

Evitar prompts gigantes que recarregam toda a Bíblia, AGENTS e história sem necessidade.

Sequência ideal para missões difíceis:

```text
EXPLORATION (read-only)
↓
AS-IS + EVIDENCE
↓
PLAN
↓
FRESH SESSION
↓
IMPLEMENTATION
↓
DETERMINISTIC GATES
↓
RED TEAM
```

Use Skill para procedimento repetido.

Use hook/schema/CI para regra determinística.

Não depender da “memória do modelo” para enforce.

---

# 17. CENSO DA COLLECTION — MÉTODO

Objetivo original: entender todos os cards da Collection, inclusive os sem ligação, mal colocados, duplicados ou que escondem várias responsabilidades.

Método:

```text
CARDS
 ↓
CENSO COMPLETO
 ↓
ENTENDER 100%
 ↓
AGRUPAR POR FUNÇÃO REAL
 ↓
DESCOBRIR DUPLICATAS / SOBRAS / GAPS
 ↓
DESENHAR TOPOLOGIA CORRETA
 ↓
SÓ ENTÃO ALTERAR
```

Durante o censo:

- READ / MEASURE / CLASSIFY;
- não corrigir;
- lotes pequenos de ~6 cards;
- costura acumulada depois de cada lote;
- não decidir merge vendo só um card;
- card sem edge não é automaticamente defeito;
- componente sem card é registrado separadamente;
- 62 não é um número sagrado: se o manifesto medir outro total, usar o medido.

Vereditos provisórios:

```text
KEEP
MERGE_CANDIDATE
RENAME
MOVE
SPLIT
DEAD_CANDIDATE
GAP
UNKNOWN
```

---

# 18. CENSO DA COLLECTION — SNAPSHOT 2026-09-09

> **ESTADO = SUPERSEDED em 2026-09-11.** Esta fotografia continua aqui inteira,
> e continua verdadeira sobre a data dela. O que deixou de valer é o `30 / 62`
> como estado corrente e o «próximo passo = manifesto nominal» como próximo
> passo. Ver **secção 43**.
>
> Duas coisas a superaram, e são diferentes:
>
> 1. o **censo determinístico** fechou o universo do System Map em `64 / 64`
>    (`know-how/census/SYNTHETIC-CENSUS-FINAL-CLOSURE.md`), e mostrou que `62`
>    era expectativa histórica: o medido foi `64` nós, dos quais `54` declarados
>    e `10` sintéticos;
> 2. o **censo dos cards e dos sensores** (2026-09-11) mostrou que «card» tem
>    TRÊS espécies, e que a espécie contada aqui — peça do System Map — não é a
>    espécie operacional.
>
> ⚠️ `11` **NÃO É** `62` corrigido. São espécies diferentes, contadas por censos
> diferentes, e somá-las ou trocá-las é o erro que a secção 43 existe para
> impedir.

Fotografia:

```text
REPO   = lucianodalondon-sys/eame-sintonia
BRANCH = claude/collection-plumbing-canonical-v1
HEAD   = 572647dce8a38b8835aafa6f9e3e42d2652fbcd9
```

Estado após Lote 05:

```text
CARDS FORMALMENTE AUDITADOS = 30 / 62 (expectativa pré-manifesto)

ACQUISITION_SEGMENT_CENSUS_CLOSED = YES
INGRESS_RAW_DERIVED_SEGMENT_CENSUS_CLOSED = YES
STRUCTURED_ADMISSION_READY_SEGMENT_CENSUS_CLOSED = YES

ENCANAMENTO E2E FUNCIONANDO = NÃO
```

**Próxima missão antes do Lote 06:** congelar o manifesto nominal dos cards e inventariar componentes escondidos.

Nunca avançar para “62/62” apenas somando lotes.

---

# 19. LOTE 01 — CONTROL PLANE INICIAL

Cards:

```text
C-CI-COLETA
C-PEDIDO
C-RECEITAS
C-ORQUESTRADOR
C-POLITICA-COLETA
C-AS-FONTES
```

Principais aprendizados:

- múltiplos botões/entrypoints físicos;
- apenas uma rota canônica de control flow;
- três bypasses conhecidos;
- Pedido é contrato do WHAT;
- Recipe/Plano estava assumindo responsabilidade de seleção;
- Route Policy não tinha card próprio;
- `C-POLITICA-COLETA` não era Route Policy;
- `social_rotas.py` exercia policy real em território diferente;
- `social_matriz` atuava como registry.

Contagem histórica do lote:

```text
CARDS = 6/6
MAP_EDGES = 44/44
UNEXPLAINED = 0
```

---

# 20. LOTE 02 — EXECUÇÃO / SOCIAL / APIFY

Cards:

```text
C-SENSOR-COLETA
C-SINTONIA-SCRAP
C-SCRAP-ROTA
C-SCRAP-SOCIAL
C-COLETA-PUBLICA
C-APIFY-POOL
```

Aprendizados:

- `sensor_coleta` era coletor pago completo, não sensor;
- SINTONIA SCRAP acumulava workflow grande demais;
- `C-SCRAP-SOCIAL` misturava dispatcher, route policy, envelope, adapter e persistence;
- `C-COLETA-PUBLICA` era executor real e também fazia seleção de ator;
- APIFY Pool deve possuir saúde/credencial, não decisão semântica de rota;
- route policy e route registry estavam sem representação adequada;
- múltiplos dicionários hard-coded de ator criaram autoridade concorrente.

---

# 21. LOTE 03 — AQUISIÇÃO E TRANSPORTE

Cards:

```text
C-COLETA-BASE
C-COLETA-INSTAGRAM
C-COLETA-YOUTUBE
C-NAVEGADOR
C-SCRAP-LEIS
C-SCRAP-GUARDA
```

Aprendizados:

- `coleta/coletor.py` escreve `data/samples/raw-paid/*.raw.json.gz`;
- o mapa tinha edges falsas de navegador para Instagram/YouTube originadas em docstrings;
- `C-COLETA-BASE` era transporte HTTP/Apify + RAW pago + provenance, não “executor genérico”;
- Instagram misturava aquisição, browser route, diário/personal state e ator;
- YouTube misturava discovery, acquisition, captions e relevance queue;
- Navigator era ferramenta CDP/locator, não route authority;
- `C-SCRAP-LEIS` misturava falhas, foundation, registry e decisão;
- surgiram dois mecanismos de RAW:
  - `coleta/coletor.py → raw-paid/*.gz`
  - `coleta/ingresso.py → guarda/preservar_coleta.py → raw_asset/storage`

O relacionamento entre esses dois RAW não deveria ser decidido sem medição.

---

# 22. LOTE 04 — INGRESSO → RAW → DERIVED

Cards:

```text
C-INGRESSO
C-DONO-DA-ESCRITA
C-DONO-DO-DERIVADO
C-DERIVACAO-FORWARD
C-PROCEDENCIA
C-RASTRO
```

Resultado válido somente depois do PRECHECK de snapshot.

Principais achados:

- `CANONICAL_INGRESS_COUNT = 1`;
- ingresso é usado parcialmente;
- orquestrador chama Ingresso e depois envia novamente a lista original à Admission;
- RAW tem conflito de autoridade: owner canônico + escritores paralelos;
- DERIVED está mais bem definido: writer único, pai, hash, drift detection;
- `raw-paid` e RAW canônico têm responsabilidades diferentes;
- prova de encanamento tinha escopo limitado a `.py`;
- `guarda/portas_live.py` não tinha caller real na fotografia auditada;
- espinha `INGRESS → RAW → DERIVED` existe em código, mas não estava completamente ligada em produção.

---

# 23. LOTE 05 — STRUCTURED → ADMISSION → READY

Cards:

```text
C-IMPORTAR
C-ADMISSAO
C-ESTRADAS-IT
C-PROVA-ENCANAMENTO
C-ROTULOS
C-IT-PRESERVAR
```

Principais achados medidos:

```text
CARDS = 6/6
MAP_EDGES = 56/56
UNEXPLAINED = 0

MISSING_RUNTIME_EDGES = 5
FALSE_EDGES_OTHER = 3
EVIDENCE_MISPLACED = 3
```

## STRUCTURED

Estado:

```text
STRUCTURED_CANONICAL_CONTRACT_EXISTS = NO
STRUCTURED_CANONICAL_OWNER_EXISTS = NO
STRUCTURED_WRITER_COUNT = 7
```

Não existe obrigação de um único owner global de STRUCTURED; owner por classe de unidade pode ser legítimo.

O problema é **mais de um writer para o mesmo conceito/tabela**, por exemplo `registro_regulatorio`.

## Admission

Problema reproduzido:

```text
itens
→ pela_entrada(itens)
→ pela_porta(itens)
```

A lista recusada pelo Ingresso não filtra a lista enviada à Admission.

```text
INGRESS_REJECTED_ITEM_CAN_REACH_ADMISSION = YES
```

## Livro de decisões

Medido em Lote 05:

```text
813 decisões
46 pares distintos (item, universo)
506 decisões com item = "?"
retry duplica decisão
```

A versão da regra é preservada, mas falta identidade canônica da decisão.

## READY

```text
READY_CONTRACT_OWNER = admissao.pronto_para_inteligencia
READY_STORAGE_OWNER = orquestrador.pela_porta
READY_CONSUMER_COUNT = 0
```

Contrato READY tem 11 campos.

Problemas:

- READY não carrega parent lineage completo;
- producer real de runtime ainda não gerou um READY;
- sala de espera física ainda não nasceu;
- o modelo de estradas não tem etapa READY.

## Bypass para Intelligence

Foram encontrados leitores em `motor/` consumindo diretamente artefatos da Collection, inclusive antes de READY.

Contagem material reportada no Lote 05:

```text
DATA_BYPASS_TO_INTELLIGENCE = 3
TARGET = 0
```

Isso deve ser tratado depois do censo/consolidação.

## Rótulos

A cadeia atual tem problemas de linhagem:

```text
PDF RAW
→ pares DERIVED
→ cruzamento DERIVED
```

Os derivados de rótulos não preservavam os IDs/hashes de pai/filho necessários para rastreio completo.

Além disso, o Orchestrator estava mandando o manifesto/ficha de catálogo à Admission, e não necessariamente o documento/derivado correto.

---

# 24. OBJETIVO DE FECHAMENTO DA COLLECTION

Não basta mapa verde.

Não basta testes unitários.

Não basta cada módulo existir.

Fechamento desejado:

```text
COLLECTION CARDS AUDITED        = 100%
UNEXPLAINED CARDS               = 0
COLLECTION EDGES AUDITED        = 100%
UNEXPLAINED DATA/CONTROL EDGES  = 0
DUPLICATE CONCEPTS UNRESOLVED   = 0
DEAD COMPONENTS PROVED ACTIVE   = 0
CANONICAL COLLECTION STARTS     = 1
CANONICAL COLLECTION INGRESS    = 1
UNAUTHORIZED DATA BYPASSES      = 0
DATA EDGES TO INTELLIGENCE      = 0
REAL END-TO-END ITEM            = 1+
RAW                             = PROVED
DERIVED                         = PROVED
STRUCTURED                      = PROVED
ADMISSION                       = PROVED
READY                           = PROVED
READY CONSUMER                  = 0
FINAL STATE                     = WAITING FOR INTELLIGENCE
LINEAGE LOST                    = 0
FACT_TIME FABRICATED            = 0
FACT_LOCATION FABRICATED        = 0
NEW FAILURES                    = 0
```

A prova final deve seguir o MESMO item:

```text
SOURCE
→ COLLECTION REQUEST
→ RUN
→ RAW
→ DERIVED
→ STRUCTURED
→ ADMISSION ACCEPTED
→ READY
→ WAITING ROOM

INTELLIGENCE CONSUMER = NONE
```

Se o ID desaparece em qualquer ponto, falha.

---

# 25. COMPONENTES ESCONDIDOS

Uma conclusão importante do censo:

> **62 cards auditados não garantem que a arquitetura inteira foi vista.**

Podem existir:

1. cards visíveis da Collection;
2. cards declarados em outras views/families/lanes;
3. subcomponentes escondidos dentro de um card;
4. componentes reais sem card;
5. writers/entrypoints em extensões que o scanner não vê.

Por isso o fechamento precisa de dois censos:

```text
CENSO A
cards declarados

CENSO B
componentes/responsabilidades reais sem representação adequada
```

Categorias úteis:

```text
UNMAPPED_COMPONENT
SUBCOMPONENT_HIDDEN_INSIDE_CARD
DUPLICATE_AUTHORITY
UNMAPPED_WRITER
UNMAPPED_RUNTIME_ENTRYPOINT
UNMAPPED_POLICY
UNMAPPED_REGISTRY
UNMAPPED_STORE
UNMAPPED_TRANSFORM
UNMAPPED_GATE
UNMAPPED_PROOF
UNKNOWN
```

---

# 26. MANIFESTO CANÔNICO DOS CARDS — PRÓXIMO CONTROLE

> **ESTADO = SUPERSEDED em 2026-09-11 — ENTREGUE, não abandonado.** O controlo
> que esta secção pedia foi feito: o censo determinístico fechou
> `DECLARED_COLLECTION_COMPONENTS = 54`, `SYNTHETIC = 10`,
> `COLLECTION_MAP_NODES = 64`, com `REMAINING = 0`. O número medido não foi
> `62`, e a secção já dizia para usar o medido. Deixa de ser «próximo
> controlo». Ver **secção 43** para o próximo.

Antes de Lote 06, congelar a lista nominal do universo da Collection.

Não confiar apenas em “30/62”.

Precisamos de:

```text
DECLARED_COLLECTION_CARDS = X
AUDITED_UNIQUE = X
NOT_AUDITED = X
AMBIGUOUS = X

AUDITED_UNIQUE + NOT_AUDITED + AMBIGUOUS
=
DECLARED_COLLECTION_CARDS
```

Se o medido for 61, 63, 67 etc., usar o medido e explicar a diferença.

O número 62 é expectativa histórica, não lei.

---

# 27. COLLECTION PLUMBING — HISTÓRICO ÚTIL

## C-PLUMB-1

Branch histórica:

```text
claude/collection-plumbing-canonical-v1
```

Checkpoint de referência:

```text
572647dce8a38b8835aafa6f9e3e42d2652fbcd9
```

Introduziu/fechou entre outras coisas:

- `coleta/ingresso.py`;
- `ArmazemLocal`;
- passagem por ingresso antes de Admission;
- preservação RAW com provenance;
- correções de scanner de imports.

Caveat: RAW → DERIVED → STRUCTURED não ficou provado como runtime default.

## C-PLUMB-2

Branch histórica:

```text
claude/collection-plumbing-runtime-v1
```

Checkpoint conhecido:

```text
1dde7aab
```

Mediu constraints de `derived_artifact`, FK de RAW e condições de runtime.

Foi pausado para não implementar antes do censo/consolidação.

Regra: **não retomar plumbing de implementação no meio do censo sem autorização arquitetural.**

---

# 28. STORIES / SOCIAL — PRINCÍPIO DE ISOLAMENTO

Para Stories e social acquisition:

- manter aquisição específica separada da inteligência;
- público somente;
- não usar sessão/login como autorização para automação;
- quem decide “o que procurar” fica acima do scraper;
- scraper só sabe “como olhar”.

Lei operacional:

> **WHO DECIDES WHAT TO LOOK AT IS ABOVE IT. IT ONLY KNOWS HOW TO LOOK.**

Essa regra vale para futuras capacidades de Instagram Stories, LinkedIn, Facebook etc.

---

# 29. SECURITY — LIÇÃO TRANSVERSAL

Uma medição live anterior demonstrou que estado do schema no repo e estado live podem divergir.

Lei:

```text
REPO SCHEMA != LIVE DATABASE STATE
```

Não afirmar RLS/policies/permissões live lendo apenas migrations.

Segurança não deve ser misturada com o censo da Collection quando isso amplia escopo sem necessidade.

---

# 30. PORTAL / CASCO

O portal é o fim, não a fundação.

Fluxo histórico de navegação da demo italiana:

```text
/
→ index.html
→ accesso.html
→ casa.html
→ portale.html
```

Diretriz de design:

- usar ADAMA Design System;
- usar ícones oficiais de doenças/pragas quando aplicável;
- não inventar ícones genéricos se existe linguagem oficial;
- melhorar visual sem inventar inteligência que o backend não produz.

Portal deve apresentar decisão produzida antes dele.

**Surface não recalcula verdade.**

---

# 31. LABEL INTELLIGENCE — IDEIA FUNCIONAL

A Label Intelligence nasceu da necessidade real de “ler labels” de forma comparável e operacional, não apenas mostrar PDFs.

Valor esperado:

- localizar produtos;
- entender usos autorizados;
- comparar culturas/doenças/pragas/moléculas;
- cruzar labels entre produtos/concorrentes/mercados;
- responder perguntas que hoje exigem leitura humana cara.

Diferença conceitual:

```text
PORTFOLIO
= quais produtos existem / posição do catálogo

LABEL INTELLIGENCE
= o que as labels permitem, dizem e como se comparam
```

Não misturar visualização de catálogo com leitura regulatória de label.

---

# 32. FUTURE RADAR / OUTRAS FERRAMENTAS

Princípio de produto amadurecido:

Se previsão futura forte não tem base, uma análise bem estruturada dos dados existentes pode gerar mais valor do que “prever”.

Nunca inventar forecast para justificar uma ferramenta.

Ferramenta só deve existir se tiver:

- pergunta clara;
- fonte clara;
- owner claro;
- contrato de entrada;
- contrato de saída;
- consumer real.

---

# 33. DEPLOY / VERCEL — LIÇÃO OPERACIONAL

Endereço oficial histórico do preview:

```text
https://sintonia-eame-preview.vercel.app/
```

Mas aliases e builds podem apontar para commits diferentes.

Antes de afirmar “está publicado”:

- medir commit servido;
- medir alias atual;
- medir candidate deployment;
- diferenciar preview branch de production alias;
- não assumir que push disparou build;
- não assumir que branch “implantou” porque Vercel recebeu commit.

---

# 34. COMO FECHAR UMA MISSÃO

Uma missão boa deve terminar com:

```text
REPO
BRANCH
HEAD
WORKTREE CLEAN?
FILES CHANGED
TESTS / PROOFS
RUNTIME MEASURED?
PRODUCTION TOUCHED?
COMMIT
PUSH
VERDICT
NEXT BLOCKER
```

Nunca fechar com frases vagas como “parece funcionando”.

Vereditos úteis:

```text
PASS
PARTIAL
BLOCKED
FAIL
UNKNOWN
```

E sempre dizer por quê.

---

# 35. RED TEAM

Red team existe para tentar derrubar a conclusão, não para confirmar.

Ataques úteis:

- contraexemplo;
- mutation test;
- writer alternativo;
- caller alternativo;
- extensão fora do scanner;
- fixture que prova falso positivo;
- branch/snapshot diferente;
- banco live versus schema;
- dado sem ID;
- retry;
- item recusado atravessando gate;
- UNKNOWN sendo convertido em zero;
- docstring/comment criando edge;
- medidor copiando regra em vez de chamar owner real.

Uma prova forte testa a regra real, não uma cópia da regra.

---

# 36. ERROS QUE NÃO PODEM SER REPETIDOS

1. Construir portal antes de fechar Collection.
2. Implementar durante o censo.
3. Confundir “arquivo existe” com “runtime usa”.
4. Aceitar `main`/worktree errada numa auditoria sem PRECHECK.
5. Recontar cards auditados só porque apareceram como vizinhos.
6. Usar posição visual como autoridade semântica.
7. Ter mais de um owner para a mesma pergunta.
8. Copiar dicionários entre executores.
9. Deixar Admission possuir vocabulário por conveniência.
10. Fazer Intelligence ler RAW/DERIVED direto para “adiantar”.
11. Usar erro como rejeição.
12. Usar ausência como zero.
13. Usar idioma/país da fonte como local do fato.
14. Ter prova que cobre `.py` e publicar conclusão sobre toda a Collection.
15. Fazer scanner criar edges a partir de prosa.
16. Criar segundo cérebro dentro de workflow/scraper.
17. Persistir estado operacional importante em Git se deveria estar em memória operacional/banco.
18. Confundir armazenamento RAW com sala de espera READY.
19. Produzir READY sem lineage suficiente.
20. Ter retry que duplica decisão sem identidade.

---

# 37. ROTINA DE INÍCIO DE CADA DIA

Antes de começar trabalho material:

1. ler este arquivo;
2. ler o último bloco de `DAILY LOG`;
3. verificar repo/branch/HEAD/worktree;
4. verificar qual missão estava aberta;
5. verificar blockers pendentes;
6. medir se alguma branch remota avançou;
7. confirmar que a fotografia usada pela missão é a correta;
8. só então executar.

Se uma conversa nova começar sem memória suficiente, este arquivo deve ser o primeiro handoff.

---

# 38. ROTINA DE FIM DE CADA DIA

Atualizar este arquivo com apenas conhecimento material.

Checklist:

```text
[ ] O que aprendemos hoje?
[ ] Qual hipótese caiu?
[ ] Qual lei nasceu ou mudou?
[ ] Qual componente mudou de papel?
[ ] Qual owner ficou comprovado?
[ ] Qual bypass apareceu?
[ ] Qual bypass foi eliminado?
[ ] Qual prova ficou mais forte?
[ ] Qual prova descobrimos que era cega?
[ ] Qual branch/HEAD é o checkpoint?
[ ] Qual próximo passo fica autorizado?
[ ] Qual coisa continua NÃO SEI?
```

Não apagar conhecimento antigo silenciosamente.

Quando algo ficar obsoleto:

```text
STATUS: SUPERSEDED
SUPERSEDED_BY:
DATE:
WHY:
```

---

# 39. FORMATO DO DAILY LOG

Adicionar sempre no topo da seção de log mais recente.

```text
## YYYY-MM-DD

### CHECKPOINT
REPO =
BRANCH =
HEAD =

### O QUE FOI MEDIDO
- ...

### O QUE APRENDEMOS
- ...

### DECISÕES
- ...

### COISAS QUE DEIXARAM DE SER VERDADE
- ...

### GAPS ABERTOS
- ...

### PRÓXIMO PASSO AUTORIZADO
- ...

### NÃO SEI / PRECISA MEDIR
- ...
```

---

# 40. DAILY LOG

## 2026-09-09

### CHECKPOINT

```text
REPO = lucianodalondon-sys/eame-sintonia
CENSUS_BASE_BRANCH = claude/collection-plumbing-canonical-v1
CENSUS_BASE_HEAD = 572647dce8a38b8835aafa6f9e3e42d2652fbcd9
KNOW_HOW_BRANCH = claude/sintonia-eame-know-how-v1
```

### O QUE FOI MEDIDO

- Lotes 01–05 do censo da Collection foram consolidados até 30 cards formalmente auditados.
- Lote 04 anterior rodado em snapshot incorreto foi invalidado e não entrou no censo.
- Lote 04 correto fechou Ingresso → RAW → DERIVED em termos de censo, mas não de runtime E2E.
- Lote 05 fechou o censo STRUCTURED → Admission → READY e provou que o fim da Collection ainda não funciona.
- Ingresso pode recusar e o mesmo item ainda chegar à Admission.
- STRUCTURED não possui contrato/owner canônico geral; existem múltiplos writers e conflitos por conceito/tabela.
- READY tem contrato, mas não houve READY real produzido pelo runtime auditado.
- sala de espera READY ainda não existe de fato na fotografia censada.
- foram encontrados consumidores da Intelligence lendo artefatos da Collection por fora da fronteira READY.
- prova do encanamento não cobre todas as extensões relevantes.
- cross-platform post-transcription content triage ainda não foi provado.

### O QUE APRENDEMOS

- organizar visualmente sem reorganizar o runtime real não resolve o SINTONIA;
- o mapa precisa refletir writers/callers/owners reais;
- o censo precisa cobrir cards declarados e componentes escondidos;
- vídeo de qualquer plataforma deve convergir para transcrição/caption e content triage comum;
- Admission e vocabulário não devem virar um cérebro único por conveniência;
- READY é a fronteira que impede Intelligence de consumir Collection crua.

### DECISÕES

- não corrigir encanamento antes de terminar censo e consolidação;
- criar manifesto nominal do universo Collection antes do Lote 06;
- inventariar componentes sem card separadamente;
- manter Intelligence desconectada da Collection durante o fechamento;
- manter Know How como memória operacional durável, distinta da Bíblia.

### GAPS ABERTOS

```text
MANIFESTO NOMINAL DOS CARDS = OPEN
UNMAPPED COMPONENTS = OPEN
INGRESS FILTER TO ADMISSION = BROKEN
RAW AUTHORITY = CONFLICT
STRUCTURED CONTRACT = MISSING
STRUCTURED OWNER PER CONCEPT = PARTIAL
ADMISSION DECISION IDENTITY = MISSING
READY REAL PRODUCTION = MISSING
WAITING ROOM = MISSING
READY LINEAGE = INSUFFICIENT
COLLECTION → INTELLIGENCE BYPASSES = PRESENT
CROSS_PLATFORM CONTENT TRIAGE = NOT PROVEN
SYSTEM MAP SCANNER COVERAGE = PARTIAL
```

### PRÓXIMO PASSO AUTORIZADO

```text
1. COLLECTION CARD MANIFEST
2. HIDDEN COMPONENT INVENTORY
3. definir LOTE 06 a partir do manifesto real
4. terminar censo
5. consolidação transversal
6. arquitetura-alvo
7. implementação do encanamento real
8. prova E2E com um item
```

### NÃO SEI / PRECISA MEDIR

- total real do universo Collection: expectativa histórica 62, mas precisa de manifesto determinístico;
- owner canônico de content triage pós-transcrição;
- lista completa de writers/entrypoints que scanners atuais ainda não enxergam;
- forma final do contrato STRUCTURED por classe de unidade;
- forma final de lineage de READY;
- quais cards serão KEEP/MERGE/MOVE/SPLIT/RETIRED depois da consolidação total.

## 2026-09-11

### CHECKPOINT

```text
REPO = lucianodalondon-sys/eame-sintonia
CENSUS_BRANCH = claude/cards-sensors-census-v1
CENSUS_HEAD = 4feb581f3a02cf53317cdbad4a269493a3936ce9
MEDIDO_SOBRE = 9a40e5068c48e215cc4ac0d6aea25ee651a70b01
KNOW_HOW_BRANCH = claude/sintonia-eame-know-how-v1
```

### O QUE FOI MEDIDO

- Fase 10 aplicada no banco canónico: `PHASE10_LIVE = YES`, migration `027 = APLICADA`.
- `PHASE11_REQUIRED_BEFORE_COLLECTION_CLOSE = NO` — a coluna `storage_path` é peso morto, não risco activo.
- Censo dos cards e sensores fechado. A escada das cinco provas: `58 / 32 / 2 / 2 / 0`.
- 11 cards operacionais: 1 alimentado por real, 6 mistura, 4 sem fonte declarada.
- `CARD_SENSOR_EDGE_REAL = 0`. Arestas: 1 PROVEN, 21 BROKEN, 4 MISSING.
- 15 camadas do portal, 5 com gerador nesta árvore; as outras são ficheiros commitados.
- 23 defeitos abertos agrupam-se em `ROOT_CAUSES = 9`.
- A fronteira READY tem contrato e um produtor em runtime; o destino da Sala de Espera nunca foi escrito.
- **Medido no código, contra o veredito do mapa:** `orquestrador.py::correr()` chama executor → ingresso → admissão numa só função, e `pela_porta()` escreve a Sala de Espera. O código da cadeia existe inteiro.

### O QUE APRENDEMOS

- «card» tem três espécies e só uma é operacional: a ferramenta do portal, com contrato, consumidor e pergunta de negócio;
- «sensor» operacional é o executor que vai à fonte e traz evidência, não o ficheiro com `sensor` no nome;
- `EXISTE != CORRE != RODOU != PRODUZIU != ENTROU` — cinco provas, e nenhuma empresta o seu `YES` à seguinte;
- uma matriz 11 × 58 sem arestas reais fabricaria certeza: a matriz pequena é a descoberta, não a falha;
- ao medir quem produz uma camada, procura-se quem ESCREVE e não quem MENCIONA — senão o auditor pinta tudo de verde;
- um `else` no fim de uma escada de prova inventa a prova que falta;
- um número copiado à mão é um número que vai envelhecer em silêncio — a saída é a trava, não a proibição (secção 44).

### DECISÕES

- não corrigir nada nesta fase: primeiro o mapa verdadeiro;
- o portal NÃO é prioridade de correção agora;
- a Phase 11 não entra antes do fecho da Collection;
- a ordem de ataque é por impacto sistémico: CR-1, CR-2, CR-8, CR-5, CR-6, CR-3, CR-7, CR-4, CR-9.

### COISAS QUE DEIXARAM DE SER VERDADE

- `CARDS AUDITADOS = 30 / 62` como estado corrente — superseded (secção 18);
- «próximo passo = manifesto nominal dos cards» — entregue, `64 / 64` (secção 26);
- `62` como universo — o medido foi `64` nós, `54` declarados e `10` sintéticos;
- ler `READY_SEM_CONSUMIDOR` como «falta quem consuma»: `READY CONSUMER = 0` é o **alvo** declarado na secção 24. O defeito é `READY REAL PRODUCTION = MISSING`.

### GAPS ABERTOS

```text
CANONICAL CHAIN RUNTIME     = CORTE NAO EXPLICADO (CR-1)
WAITING ROOM PRODUCED       = NEVER
LEDGER EXECUTOR ATTRIBUTION = NOT_INSTRUMENTED (CR-5)
PORTAL LAYER GENERATORS     = 5 / 15 (CR-3)
CARDS SEM CONTRATO          = 4 (CR-4)
FONTES NUNCA COLETADAS      = 22 / 23 (CR-7)
FACT_TIME NOS DERIVADOS     = 0 / 43 (CR-8, COL-027)
FORWARD WRITER EM PRODUCAO  = NUNCA ESCREVEU
```

### PRÓXIMO PASSO AUTORIZADO

```text
C-PROVA-CR1

Pergunta unica:
«Onde esta, executavelmente, o corte que faz ENTROU = 0,
 considerando que partes da cadeia ja existem em codigo?»

Missao de MEDICAO antes de implementacao. Nao implementar.
```

### NÃO SEI / PRECISA MEDIR

- o corte de CR-1 é runtime real, entrypoint/bypass, route registry/policy, falta de execução observada, ou defeito da representação do mapa? Ver secção 43.8;
- se a Sala de Espera fica vazia por falta de ligação ou por falta de **admissibilidade** (`aceites` só enche com `adm.SIM`, e `COL-027` mediu 43 `NÃO SEI` por falta de `FACT_TIME`) — hipótese, não facto;
- se o escritor forward se comporta em produção como se comporta na bancada: nunca escreveu no banco vivo;
- a que corresponde cada uma das 144 observações do ledger: o ledger não guarda o executor.

---

# 41. COMO USAR ESTE ARQUIVO COM NOVOS CHATS / AGENTES

Ao iniciar uma nova aba/agente para trabalho arquitetural:

```text
1. LEIA SINTONIA-EAME-KNOW-HOW.md
2. LEIA AGENTS.md
3. LEIA APENAS AS LEIS RELEVANTES DA BÍBLIA
4. MEÇA REPO / BRANCH / HEAD / STATUS
5. NÃO HERDE STATUS OPERACIONAL SEM REMEDIR
6. CITE O CHECKPOINT USADO
7. EXECUTE A MISSÃO
8. NO FINAL, ATUALIZE O KNOW HOW SE HOUVE APRENDIZADO MATERIAL
```

Nunca mandar um agente “continuar de onde paramos” sem fornecer ou apontar uma autoridade durável.

---

# 42. PRINCÍPIO FINAL

O SINTONIA não é o portal.

O SINTONIA não é um scraper.

O SINTONIA não é um LLM.

O SINTONIA é uma cadeia de responsabilidades, evidências, regras, identidade, procedência, transformação, decisão e entrega.

A casa só fica confiável quando conseguimos pegar uma unidade real e responder sem adivinhar:

```text
quem pediu?
quem coletou?
por qual rota?
qual foi o original?
qual é o ID do original?
qual derivado nasceu?
quem é o pai?
como foi estruturado?
quem decidiu?
qual regra decidiu?
qual versão da regra?
qual READY saiu?
onde está esperando?
quem pode consumir?
```

Se uma dessas respostas desaparece no caminho, ainda existe trabalho de arquitetura.

**Este arquivo existe para que nunca precisemos reaprender isso do zero.**

---

# 43. CENSO DOS CARDS E DOS SENSORES — ESPÉCIES, PROVAS E ESTADO (2026-09-11)

```text
CENSUS_BRANCH = claude/cards-sensors-census-v1
CENSUS_HEAD   = 4feb581f3a02cf53317cdbad4a269493a3936ce9
MATRIZ        = data/derivados/MATRIZ-CARDS-SENSORES-V1.json   (dona dos números)
LEITURA       = docs/operacao/CENSO-CARDS-SENSORES-V1.md       (dona dos julgamentos)
MEDIDO SOBRE  = 9a40e5068c48e215cc4ac0d6aea25ee651a70b01
```

O JSON é o dono dos números e o relatório é o dono das causas-raiz. Este
capítulo **aponta** para os dois. Os números abaixo estão aqui porque um
know-how sem números não se lê — mas quem discorda deles vai ao JSON, não a
esta secção.

## 43.1 · «CARD» TEM TRÊS ESPÉCIES

Este foi o primeiro risco da missão, e confundi-las já tinha custado
contagens erradas antes.

```text
1. PEÇA DO SYSTEM MAP      módulo de arquitetura; `censo_da_topologia.py`
                           chama-lhe CARD_ID. Universo fechado: 64 nós.
2. FERRAMENTA DO PORTAL    tela com contrato de bloco, consumidor e pergunta
                           de negócio. Universo: 11.
3. BLOCO VISUAL            marcação sem contrato de dados. Não promete dado
                           a ninguém, e está certo assim.
```

**A espécie operacional é a 2** — é a única com contrato, consumidor e
pergunta de negócio. A 1 é o mapa do código e tem censo próprio. A 3 é
marcação.

> **Nem todo elemento visual chamado «card» é uma unidade operacional.**
> E `11` não é `64` corrigido: são universos diferentes.

## 43.2 · «SENSOR» NÃO É O QUE TEM `sensor` NO NOME

Havia dois ficheiros `regras/sensor_*.py`. Responder «dois» seria uma resposta
errada a uma pergunta certa.

**Sensor operacional = EXECUTOR: quem vai à fonte e traz evidência.** É essa a
espécie que se conta, e o censo dos executores já a enumera.

## 43.3 · AS CINCO PROVAS, QUE NÃO SE EMPRESTAM

```text
EXISTE     58    há ficheiro
CORRE      32    é chamável sem rede, sem pago, sem produção
RODOU       2    deixou rastro de execução
PRODUZIU    2    o rastro tem saída com etapa observada
ENTROU      0    a saída atravessou a fronteira canónica
```

```text
EXISTE != CORRE != RODOU != PRODUZIU != ENTROU
```

Um `YES` num degrau não empresta `YES` ao seguinte. A queda de 58 para 32 é
**ambiente**; a de 32 para 2 é **instrumentação**; a de 2 para 0 é
**arquitetura** — e só essa impede a Collection de fechar.

Os dois que rodaram: `coleta/executor_texto_de_pdf.py` (`LEGACY_REPLAY`,
`RAW → DERIVED`) e `coleta/rota_forward_documento.py` (`FORWARD`,
`DERIVED → STRUCTURED → ADMISSION`). Ambos provados por **teste**, não por
corrida de produção.

A quinta prova não se mede por sensor, e isso é um facto e não um limite do
método: o ledger de fluxo declara `POR_EXECUTOR = NOT_INSTRUMENTED` — guarda a
observação e não quem a produziu. O que se mede é o degrau.

## 43.4 · OS CARDS OPERACIONAIS

```text
CARDS_OPERACIONAIS      = 11
ALIMENTADO_POR_REAL     =  1    (windows · Finestre Colturali)
MISTURA_REAL_E_FIXTURE  =  6
SEM_FONTE_DECLARADA     =  4    (future · voices · sources · field)
```

Um card fala de dado com procedência. Seis ilustram e medem ao mesmo tempo sem
dizer qual é qual. Quatro não declaram fonte nenhuma.

## 43.5 · NÃO EXISTE UMA ÚNICA ARESTA CARD → SENSOR

```text
CARD_SENSOR_EDGE_REAL = 0

ARESTAS_POR_CLASSE   PROVEN = 1 · BROKEN = 21 · MISSING = 4
CAMADAS_DO_PORTAL    15,  das quais 5 com gerador nesta árvore
```

As arestas que existem apontam para **camadas do portal**, nunca para um
executor. E 21 dessas camadas são ficheiros **commitados sem gerador**:
nenhum sensor as reescreve.

```text
CARD -> CAMADA DO PORTAL -> (quem a produz?) -> SENSOR
                             ^
                             aqui a corrente parte
```

> **Uma matriz 11 × 58 daria 638 células e a sensação de um mapa. Seria falsa.**
> Desenhar células vazias para não entregar uma matriz pequena é fabricar
> certeza. A matriz é pequena porque o sistema é assim, e essa é a descoberta.

Ao medir quem produz uma camada, procura-se quem **escreve**, não quem
**menciona**: os auditores (`harness.mjs`, `checks.mjs`) citam todas as camadas
porque as auditam. Contar auditoria como geração pintaria a matriz de verde
por causa do auditor.

## 43.6 · AS CAUSAS-RAIZ

```text
ROOT_CAUSES = 9
```

Vinte e três defeitos abertos não são vinte e três problemas. As três que
mandam:

**CR-1 — A CADEIA CANÓNICA ESTÁ CORTADA EM DUAS JUNTAS.**

```text
ENTRADA -> ORQUESTRADOR -> EXECUCAO -> PORTA
   ok            ok          CORTE      CORTE
```

Quatro estações, duas ligações observadas. É a causa do degrau `ENTROU = 0`.
Ver 43.8 antes de agir sobre isto.

**CR-2 — A FRONTEIRA READY TEM CONTRATO E PRODUTOR; A SALA DE ESPERA NUNCA FOI
PRODUZIDA.** Contrato `COL-LAW-043`, dono
`admissao/admissao.py :: pronto_para_inteligencia()`, um produtor em runtime
(`orquestrador/orquestrador.py`, só por linha de comando — nenhum workflow o
chama). Destino `data/samples/PRONTO-PARA-INTELIGENCIA/<RUN_ID>.json`: não
existe.

> ⚠️ **CORREÇÃO DE LEITURA, e ela importa.** O censo etiqueta este gap como
> `READY_SEM_CONSUMIDOR`. **Zero consumidores NÃO é o defeito — é o alvo.** A
> secção 24 deste ficheiro declara `READY CONSUMER = 0` e
> `FINAL STATE = WAITING FOR INTELLIGENCE` como estado desejado. O defeito é o
> outro lado: `READY REAL PRODUCTION = MISSING` e `WAITING ROOM = MISSING`.
> Ler a etiqueta como «falta quem consuma» faria a próxima missão construir
> exactamente o que a arquitetura proíbe.

**CR-5 — O LEDGER NÃO ATRIBUI CORRIDA A EXECUTOR NEM A ETAPA.**
`POR_EXECUTOR`, `POR_ETAPA` e `CUSTO` = `NOT_INSTRUMENTED`. 144 observações no
ledger, nenhuma atribuível. Limita a prova operacional de tudo o resto: sem
isto, nenhuma correcção das outras oito se consegue **provar** em produção.

As outras seis: rota com vários donos (CR-6), camadas sem gerador (CR-3),
atlas por abrir (CR-7), cards sem contrato (CR-4), peças declaradas que
ninguém chama (CR-9), dívida de procedência no acervo (CR-8). A leitura
completa, com dono e camada de cada uma, está em
`docs/operacao/CENSO-CARDS-SENSORES-V1.md`, secção 8.

**O portal NÃO é prioridade de correção agora.** Consertá-lo primeiro daria a
aparência de um sistema a funcionar sobre uma cadeia que continua cortada.

## 43.7 · ESTADO DO BANCO — FASE 10 E FASE 11

```text
PHASE10_LIVE = YES
027          = APLICADA no banco canónico
PHASE11_REQUIRED_BEFORE_COLLECTION_CLOSE = NO
```

Provas: `provas/a_lei_da_fase_10.py`, `provas/a_fase_10_entra_no_acervo.py`,
`provas/auditoria_live.sh` (secção G cobra o contrato da 027 a cada corrida).
Leitura em `docs/operacao/CENSO-CARDS-SENSORES-V1.md`, secção 10.

A Phase 11 é a retirada da coluna `raw_asset.storage_path`. Ela é hoje **peso
morto, não risco activo**: o endereço já não é identidade, nenhum escritor
vivo o usa como chave, nenhum leitor devolve «a primeira linha do endereço», e
o único SQL que ainda o trata como chave não se aplica a banco nenhum desde a
026. Nenhuma das nove causas-raiz depende de a retirar.

**O limite desta resposta, dito em voz alta:** o escritor forward nunca
escreveu no banco vivo — 252 linhas legadas, zero forward. A prova é do
**código** e da bancada local, não de tráfego de produção.

## 43.8 · NÃO SEI / PRECISA MEDIR — O CORTE DE CR-1

> **ESTADO = RESPONDIDO em 2026-09-11 (C-MADRUGADA-CR1). Texto original
> mantido por baixo, porque a pergunta estava bem posta e é ela que explica o
> que se foi medir.** A resposta está na **secção 45**, e não é nenhuma das
> cinco hipóteses listadas aqui em baixo: não há corte. A cadeia corre
> inteira, e o que chega à porta é o índice da colheita.


Este é o ponto onde o censo **não** deve ser lido como resposta final, e onde
`CAN DO != DID DO` pode estar a morder nos dois sentidos.

O censo classifica `ORQUESTRADOR → EXECUÇÃO` e `EXECUÇÃO → PORTA` como
cortados. Mas medido no código, em 2026-09-11, na branch do censo:

- `orquestrador/orquestrador.py :: correr()` chama o executor por
  `subprocess`, depois `a_colheita(e)`, depois `pela_entrada(...)` (ingresso)
  e depois `pela_porta(...)` (admissão), numa só função;
- `pela_porta()` **escreve a Sala de Espera**:
  `PRONTOS.mkdir(...)` e `(PRONTOS / f"{run_id}.json").write_text(...)`,
  guardado por `if aceites:`.

Ou seja: **o código da cadeia inteira existe, incluindo o escritor da Sala de
Espera.** A pasta não existe porque nenhuma corrida real produziu um `aceite`,
e não porque ninguém a escreva.

```text
CAN DO != DID DO — nos dois sentidos.
O mapa diz CORTADO. O codigo diz LIGADO. Um dos dois esta a medir
outra coisa, e nao se sabe qual ate alguem correr.
```

**Antes de corrigir CR-1 é obrigatório medir, e nesta ordem:**

```text
1. o corte e RUNTIME REAL?      correr a cadeia e ver onde para
2. e ENTRYPOINT / BYPASS?       ninguem chama `correr()` num workflow
3. e ROUTE REGISTRY / POLICY?   a receita nunca resolve para este caminho
4. e FALTA DE EXECUCAO?         o caminho serve, nunca foi corrido
5. ou e DEFEITO/LIMITE DA REPRESENTACAO DO MAPA?
```

Hipótese a testar, **não** conclusão: `aceites` só enche com `adm.SIM`, e
`COL-027` mediu que a porta viu 43 textos derivados e devolveu **43 `NÃO SEI`**
por falta de `FACT_TIME`. Se isso se confirmar, a Sala de Espera fica vazia
mesmo com a cadeia inteira a correr — e o corte seria de **admissibilidade**,
não de ligação. Não foi provado nesta missão e não pode ser registado como
facto.

## 43.9 · O ERRO QUE ESTE CENSO COMETEU E CORRIGIU EM SI PRÓPRIO

A escada de estado do gerador terminava em `else ALIMENTADO_POR_REAL`. Com
isso o card `market` saía «real» porque a sua única camada não é fixture — mas
também não é classificada, e o contrato dela confessa por escrito que ali há
dado escrito à mão.

```text
UM `else` NO FIM DE UMA ESCADA DE PROVA INVENTA A PROVA QUE FALTA.
```

Vale para qualquer classificador desta casa: o degrau «não sei» tem de existir
por escrito, ou o caso mais favorável absorve a ausência de prova em silêncio.

---

# 44. LEI DO NÚMERO CITADO NUM DOCUMENTO HUMANO

Aprendida a construir o censo, e vale para todo relatório desta casa.

```text
UM NUMERO COPIADO A MAO E UM NUMERO QUE VAI ENVELHECER EM SILENCIO.
```

Um documento sem números não se lê. Um documento que reescreve números de que
não é dono cria um **segundo dono de cada contagem**, e dois donos divergem no
dia em que um deles medir outra vez.

A saída **não** é proibir a citação — é tornar a divergência barulhenta:

1. o gerador escreve o JSON, e o JSON é o dono;
2. a leitura humana cita dentro de blocos com forma fixa;
3. um teste compara cada número citado com o JSON e recusa uma chave que viva
   em dois sítios com valores diferentes.

Implementado em `tests/test_censo_cards_sensores.py`, testado por mutação em
quatro frentes: número errado, chave inventada, escada que sobe, estado
inventado. As quatro foram apanhadas.

> Uma trava verde que nunca apanhou nada é decoração. Mutação antes de
> confiar.


---

# 45. O CORTE DE CR-1, MEDIDO — E A MEDIDA QUE NÃO PODIA GANHAR

```
MISSAO      = C-MADRUGADA-CR1, 2026-09-11
BRANCH      = claude/overnight-cr1-v1
HEAD        = 9a6cbeed9504dc91a7132f53e3d8d43247058a46
PROVAS      = provas/o_corte_de_cr1.py
              tests/test_fronteira_mede_producao.py
SUPERSEDE   = seccao 43.8 (a pergunta) e a redaccao anterior de CR-1
```

A pergunta da secção 43.8 era: «o mapa diz CORTADO, o código diz LIGADO — qual
dos dois mede outra coisa?». **Mediram-se os dois, e os dois estavam a dizer
meia verdade.** São duas descobertas independentes.

## 45.1 · O QUÊ — a cadeia não está cortada

Numa única corrida real, sem rede e sem banco
(`orq.correr(pedido, so_a_porta=True)`), oito estações ficaram provadas por
execução controlada **no mesmo item e na mesma corrida**:

```
P0 pedido · P1 plano · P2 executor escolhido · P4 saida encontrada
P5 ingresso · P6 RAW preservado · P7 item na porta · P8 porta decidiu
```

`P9` e `P10` não foram alcançados porque **zero itens** tiveram `SIM`.
`P3` (executor realmente invocado) ficou `NOT_APPLICABLE`, e isso é um facto
sobre a casa e não um buraco da prova:

```
NENHUM EXECUTOR DE RECEITA CORRE OFFLINE.
Todos pedem rede ou sao pagos.
```

**PORQUÊ:** `MODULE EXISTS != EDGE EXISTS != FLOW EXISTS` foi aplicada uma vez
só, e ao módulo. Ninguém tinha corrido o fluxo. O censo classificou a aresta
pelo mapa; o mapa mede declaração, não execução.

**PROVA:** `provas/o_corte_de_cr1.py`, read-only e reprodutível.

**CONSEQUÊNCIA:** a redacção anterior de CR-1 («a cadeia canónica está cortada
em duas juntas») está **REFUTADA** e foi reescrita em
`docs/operacao/CENSO-CARDS-SENSORES-V1.md`.

## 45.2 · O QUÊ — o que chega à porta é o índice da colheita

253 itens reais atravessaram a cadeia. A porta julgou todos:

```
NAO_SEI        182    «o item veio sem texto nenhum»
NAO_SE_APLICA   71    «e ficha de conta ou de catalogo»
SIM              0
```

O `larga_em` das receitas aponta para o **índice**, não para a colheita:

```
_MANIFESTO.json     o indice dos documentos descarregados
CORPUS-*.json       o catalogo de pessoas
CONTAS-V1.json      a ficha de ONDE se pode coletar
```

E `a_colheita()` tem uma heurística genérica — «uma lista, ou o primeiro campo
do ficheiro que seja lista de fichas» — que transforma **linhas de um índice**
em pseudo-itens.

```
O INDICE DE UMA COLHEITA NAO E A COLHEITA.
E UM RECIBO — E UM RECIBO NAO SE ADMITE, LE-SE.
```

`data/raw/IT-ROTULOS/` contém **só** `_MANIFESTO.json`: os 163 PDF que ele
indexa não estão nesta árvore. Duas das cinco receitas apontam `larga_em` para
pastas que não existem.

**A ADMISSÃO NÃO É O PROBLEMA.** Ela faz exactamente o seu trabalho, e com o
vocabulário certo para cada caso. Quem quiser `ENTROU > 0` a mexer na porta
está a atacar a peça sã.

**CONSEQUÊNCIA:** fica por escrever o contrato do que um executor pode largar.
Isso é **lei nova**, e por isso não foi corrigido nesta missão.

## 45.3 · O QUÊ — a medida de `ENTROU` não conseguia reportar sucesso

Segunda descoberta, independente da primeira:

```
GAP        = None if consumidores else "READY_SEM_CONSUMIDOR"
atravessou = bool(DESTINO_EXISTE) and bool(CONSUMIDORES)
```

Red team com o medidor **real**, quatro mundos montados:

| mundo montado | GAP que saía | ENTROU |
|---|---|---|
| nada produzido, 0 consumidores | `READY_SEM_CONSUMIDOR` | 0 |
| **READY PRODUZIDO, 0 consumidores** (o ALVO) | `READY_SEM_CONSUMIDOR` | 0 |
| **nada produzido, 1 consumidor falso** | `None` («são») | 0 |
| READY produzido + consumidor | `None` | >0 |

Duas leituras erradas numa linha só. O **alvo** da arquitetura saía com o
diagnóstico do **defeito**, e um consumidor sem produção nenhuma **limpava** o
gap.

**PORQUÊ:** a secção 24 declara `READY CONSUMER = 0` como estado desejado. Com
o `and`, `ENTROU` só subia acima de zero no dia em que alguém violasse a
fronteira.

```
UMA MEDIDA QUE NAO CONSEGUE REPORTAR SUCESSO QUANDO O SISTEMA ESTA
CORRECTO ESTA PARTIDA, INDEPENDENTEMENTE DO SISTEMA.
```

O detalhe mais desconfortável: o docstring da própria prova já dizia
«DECLARADO != IMPLEMENTADO != PRODUZIDO != CONSUMIDO — são quatro perguntas, e
achatá-las é como se perdeu a conta». O printout respeitava isso. O JSON
exportado não.

```
A PROVA DIZIA A LEI QUE O SEU PROPRIO JSON QUEBRAVA.
```

**PROVA / CONSEQUÊNCIA:** corrigido. `o_estado_da_fronteira(produzido,
consumidores)` é agora função pura com dois eixos e quatro respostas:
`READY_NUNCA_PRODUZIDO` · `None` (o alvo) · `CONSUMIDOR_ANTES_DA_INTELIGENCIA`.
`ENTROU` lê `READY_PRODUZIDO`. Teste escrito a falhar primeiro (7 falhas), 13
travas depois, 3 mutações apanhadas. Nenhum runtime da Collection foi tocado.

```
ENTROU = 0 antes.   ENTROU = 0 depois.
```

E esse é o ponto. O número não se mexeu; o que ele **quer dizer** mudou de
«ninguém lê» para «nunca foi produzido». O primeiro não era accionável e
culpava a peça errada. O segundo é a verdade.

## 45.4 · A LIÇÃO QUE VALE PARA ALÉM DESTE CASO

```
UMA MEDIDA QUE SO PODE FICAR VERDE QUANDO A ARQUITETURA ESTIVER
ERRADA NAO ESTA A MEDIR A ARQUITETURA: ESTA A MEDIR OUTRA COISA.
```

Antes de acreditar num zero, montar o mundo em que ele deveria ser diferente e
confirmar que a medida o percebe. Se ela não percebe, o zero não é do sistema:
é do medidor. Foi isso que separou `READY_SEM_CONSUMIDOR` de
`READY_NUNCA_PRODUZIDO`, e as duas leituras mandavam a casa para lados opostos.

## 45.5 · O QUE CONTINUA NÃO SEI

- se alguma rota que **precisa de rede** se comporta de outra maneira: essas
  não correram, e não podiam correr;
- a hipótese `COL-027` («43 derivados sem `FACT_TIME`») — **não se confirma
  nesta rota** (zero das 253 decisões fala de tempo), mas o corpus dos 43
  derivados é outro e continua por replayar;
- `RUN -> EXECUTOR` continua impossível no ledger (`POR_EXECUTOR =
  NOT_INSTRUMENTED`). A atribuição perde-se em `coleta/ingresso.py`, onde o
  recibo já traz `ACTOR` e o campo de destino `EXECUTOR_ID` já existe em
  `leis/artefato.py` — e as duas pontas nunca se tocam. É dívida separada de
  CR-1, e fechar uma não fecha a outra.

---


---

# 46. O CONTRATO DE RETORNO DO EXECUTOR — `COL-LAW-505`

```
MISSAO   = C-PREP-EXECUTOR-RETURN-CONTRACT-V1, 2026-09-11
BRANCH   = claude/executor-return-contract-v1
HEAD     = 5524c512d4046364bba601e2b64b84f9d19cbdf5
LEI      = COL-LAW-505 · Biblia V1.3 -> V1.4
CONTRATO = leis/retorno_da_coleta.py
MEDICAO  = docs/operacao/CONTRATO-DE-RETORNO-DO-EXECUTOR-V1.md
```

## 46.1 · O QUÊ

O retorno de uma corrida passa a separar, **por declaração de quem correu**, a
**COLHEITA** dos **artefactos de suporte**. Seis espécies, vocabulário fechado:

```
COLHEITA · MANIFEST · CATALOG · RUN_RECEIPT · PLAN · UNKNOWN
```

**Só a COLHEITA entra no ingresso.** A espécie é **declarada, nunca inferida** de
nome de ficheiro, de pasta, de extensão, de presença de um campo, nem de «a
primeira lista do JSON».

## 46.2 · POR QUÊ — a lei já tinha feito a pergunta

`COL-LAW-013` exige `OUTPUT = onde larguei, E EM QUE FORMA`. O **onde** tem campo
desde a `COL-LAW-012` (`larga_em`). O **em que forma** nunca teve campo, enum nem
guarda: vivia em prosa livre no `o_que_traz`, que nenhum código lê. A
`COL-LAW-014` já nomeava os campos em falta — `artifact_types` e `produces` — e
declarava que não existiam.

```
UMA PERGUNTA ESCRITA NA LEI E NUNCA RESPONDIDA
NAO E UMA LACUNA: E UMA DIVIDA COM JUROS.
```

A 505 responde às duas e **cita-as**. Uma lei nova que as ignorasse teria dado à
casa duas autoridades sobre a mesma pergunta.

## 46.3 · PROVA

```
ITEMS_EMITTED        253
REAL_HARVEST_ITEMS     0
FALSE_HARVEST_TOTAL  253
```

Cento por cento de falsa colheita, sobre os cinco executores canónicos. E o
contraexemplo que fecha o assunto: `CLASSIFICADO-V1.json` **declara** um
contentor `ITEMS` com `ITEM_COUNT = 0`, e a heurística genérica **salta-o por
estar vazio** e agarra a lista de catálogo ao lado.

```
UMA HEURISTICA QUE PREFERE UMA LISTA CHEIA A UMA LISTA CERTA
NAO ESTA A LER O RETORNO: ESTA A ADIVINHAR.
```

O executor tinha declarado. Ninguém leu a declaração.

## 46.4 · A ESCOLHA DO DESENHO, E PORQUE NÃO FOI A ÓBVIA

Escolhido o **envelope de execução** em vez de declarar a espécie no registry.

O desenho do registry **já existe**: chama-se `larga_em`, e é uma declaração de
**intenção**. Duas das cinco receitas apontam para pastas que não existem e nada
o detecta.

```
UMA DECLARACAO FEITA ANTES DA CORRIDA APODRECE EM SILENCIO.
UM ENVELOPE E EMITIDO POR QUEM ACABOU DE CORRER.
```

E o envelope **não é invenção**: `coleta/italy_executor.py :: traduzir()` já
produz esta unidade campo a campo, com `STORAGE_LOCATION` ausente quando
desconhecido e `FACT_TIME` a recusar prosa. A forma já existia nesta casa. Não
tinha nome nem validador.

**Dono:** `leis/retorno_da_coleta.py`, **irmão** de `leis/artefato.py` e não
substituto — aquele governa a ficha de uma coisa **entregue**, este governa o
que a **corrida devolveu**.

## 46.5 · O QUE SE RECUSOU DISTINGUIR

`INDEX` e `MANIFEST` não são espécies diferentes. Procurou-se a diferença e ela
não existe: as duas são uma listagem de payloads, e o que varia é **onde** o
payload está e **se** está — que já é o campo `PAYLOAD`, com estado próprio.

E `AUSENTE` teve de ser um terceiro estado, ao lado de `PRESENTE` e
`NAO_SE_APLICA`: o manifesto declara 163 ficheiros e há zero ao lado. Chamar-lhe
erro faria a corrida falhar; calar faria o índice passar por colheita.

## 46.6 · CONSEQUÊNCIA

**O runtime não mudou.** `a_colheita()` continua com a heurística antiga e nenhum
executor foi adaptado. Impacto medido para quem ligar isto:

```
EXECUTORS_TOTAL    5      ALREADY_CONFORMING 0
NEED_ADAPTER       3      MISSING_PAYLOAD    4
NEED_RECOLLECTION  4      UNKNOWN            0

F1 forma ja certa, nunca correu        T2         so falta correr (precisa de rede)
F2 nunca correu, saida por definir     T3
F3 devolve suporte em vez de colheita  T4 T7 T9   declarar especie + apontar payload
```

Três famílias, não cinco missões.

## 46.7 · A LIÇÃO QUE VALE PARA ALÉM DESTE CASO

Três buracos das travas foram encontrados **pela mutação**, não pela leitura: o
filtro de entrada sem trava, a unidade sem payload, e o estado da corrida sem
vocabulário. Nenhum deles aparecia numa suíte verde.

```
UMA MUTACAO QUE NAO MATA NENHUM TESTE NAO PROVA QUE O CODIGO ESTA CERTO:
PROVA QUE NINGUEM O ESTAVA A OLHAR.
```

E duas travas de **contagem congelada** (a `VERSION` da Bíblia e o total do bloco
5xx) barraram esta emenda. A saída certa não foi afrouxá-las: a `VERSION` passou
a ser **derivada** da última linha do histórico constitucional, e as leis que
nunca podem desaparecer são agora nomeadas uma a uma. Um literal cravado num
teste convida a ser editado para o teste ficar verde — que é o contrário do que
a `COL-LAW-069` quer.


---

# 47. A LEI DO RETORNO ENTROU NO RUNTIME — 253 FALSOS PASSARAM A ZERO

```
MISSAO = C-IMPL-EXECUTOR-RETURN-RUNTIME-V1, 2026-09-11
BRANCH = claude/executor-return-runtime-v1
HEAD   = bf1ad7aa1bb4daddb67464ee99852d107efa934b
PROVAS = provas/so_a_colheita_atravessa.py
         provas/o_corte_de_cr1.py
         tests/test_runtime_so_deixa_passar_colheita.py
```

## 47.1 · O QUÊ

A `COL-LAW-505` deixou de ser lei escrita e passou a decidir. A heurística que
escolhia «a primeira lista de fichas do JSON» **saiu do orquestrador**, e a
espécie passa a vir declarada:

```
EXECUTOR -> ENVELOPE -> conferir() -> so_o_que_entra() -> COLHEITA[] -> Ingresso
```

```
FALSE_HARVEST_ANTES   253
FALSE_HARVEST_DEPOIS    0
SUPPORT_ITEMS_BLOCKED   8
REAL_HARVEST            0
READY_PRODUCED          0
```

Três famílias, tratadas como três e não como cinco: **F1** (T2) declara o que
produziu; **F2** (T3) não declara nada e o recibo diz porquê; **F3** (T4, T7,
T9) declara o legado como suporte.

## 47.2 · POR QUÊ — o legado só pode declarar suporte

A tentação óbvia era deixar a receita declarar a espécie de tudo, incluindo
colheita. Recusou-se, e a razão é medida: `larga_em` **já é** uma declaração
feita antes da corrida, e duas das cinco apontam para pastas que não existem
sem ninguém notar.

```
DECLARAR SUPORTE E INOFENSIVO MESMO QUANDO ERRADO: SUPORTE NAO ATRAVESSA.
DECLARAR COLHEITA NAO E — E POR ISSO NAO SE PODE.
```

Colheita vem de uma corrida, e de mais nada. Uma declaração que pudesse dizer
«aqui há colheita» teria trocado uma heurística por um literal desactualizável.

E o silêncio ganhou nome próprio:

```
UM RETORNO SEM DECLARACAO NAO E UM RETORNO VAZIO:
E UM RETORNO QUE NAO SE DECLAROU — E O QUE NAO SE DECLAROU NAO ENTRA.
```

## 47.3 · PROVA

Cadeia inteira, **mesma corrida e mesmo item**, offline, sem banco e sem rede:
adapter → envelope → contrato → `so_o_que_entra()` → ingresso → RAW preservado
→ admissão. Doze ataques, oito mutações, todas apanhadas.

### O que a prova apanhou no código desta própria missão

A primeira versão de `declarar()` construía um dicionário **novo** com seis
campos do contrato — e deitava fora o `texto`, o `SOURCE_URL` e o
`STORAGE_LOCATION` que `traduzir()` acabara de preparar. A admissão respondia
«NAO_SEI — veio sem texto nenhum», e a culpa era do código novo, não do dado.

```
DECLARAR O QUE UMA COISA E NAO E SUBSTITUI-LA PELA ETIQUETA.
```

O contrato acrescenta-se **por cima** do item; nunca no lugar dele.

## 47.4 · CONSEQUÊNCIA — o que a ligação tornou visível, e não criou

A unidade italiana chega à porta com `SOURCE_ID` **maiúsculo**, que é o nome do
contrato em `coleta/ingresso.py :: DO_COLETOR`. E
`admissao/admissao.py :: _tem_origem` procura `source_id` **minúsculo**. Dois
nomes para o mesmo campo, invisíveis até hoje porque **nenhuma unidade italiana
tinha chegado à porta antes**.

```
LIGAR UMA CADEIA NAO CRIA OS DEFEITOS DELA: MOSTRA-OS.
```

Não foi corrigido: mexer na admissão para conseguir verde era proibido, e com
razão. Fica medido, com nome, na prova.

## 47.5 · O QUE CONTINUA ABERTO

Os cinco degraus de CR-1, e só dois fecharam:

```
CONTRACT_DEFINED       SIM
RUNTIME_CONNECTED      SIM
PAYLOAD_AVAILABLE      NAO   4 de 5 executores sem payload nesta arvore
REAL_HARVEST_OBSERVED  NAO   nenhuma corrida real declarou colheita
READY_PRODUCED         NAO   zero
```

**«O runtime respeita o contrato» não é «a Collection fechou».** Juntar as duas
frases seria repetir exactamente o erro que o censo existe para não cometer.

Continuam a depender de corrida ou de recoleta: T2 (precisa de rede para o
coletor Node), T3 (nunca correu e a saída está por definir), T4 (os 163 PDF que
o manifesto indexa não estão nesta árvore), T7 e T9 (o retorno descreve onde
colher, nunca colheu).

## 47.6 · A LIÇÃO DE MÉTODO

O número caiu de 253 para zero **sem se perder um único item real** — porque não
havia nenhum.

```
DEIXAR DE CONTAR O QUE NAO EXISTIA NAO E PERDER DADO.
E PARAR DE MENTIR SOBRE ELE.
```

E a trava que impede a heurística de voltar teve de aprender a ler **código, e
não texto**: a primeira versão procurava a expressão no ficheiro e acusava o
docstring que a CITA para explicar o conserto. Agora percorre a árvore
sintáctica, e comentário e docstring ficam de fora — que é onde a história deve
poder viver.


---

# 48. UM SÓ TRADUTOR ENTRE O QUE SE COLHE E O QUE SE JULGA

```
MISSAO = C-PROVA-SEAM-INGRESSO-ADMISSION-V1, 2026-09-11
BRANCH = claude/ingresso-admission-seam-v1
HEAD   = 43fa06107fdb8012330d46a459de4ec1c09ab99b
DONO   = coleta/ingresso.py :: para_a_porta() + PARA_A_PORTA
PROVA  = tests/test_lingua_da_porta.py (29 travas, 9 mutações)
```

## 48.1 · O QUÊ

O contrato comum fala `SOURCE_ID`; a admissão lê `source_id`. Medidos **12
conceitos, 10 com dois nomes**. Agora há **um** tradutor, na fronteira, e as
três rotas que julgam passam por ele.

## 48.2 · POR QUÊ — o defeito não era o que parecia

Não era «a admissão lê minúsculas». Era que a tradução **já existia, escrita à
mão, em dois sítios com subconjuntos diferentes** — e a rota canónica não
traduzia de todo.

```
UMA TRADUCAO SEM DONO NAO E UMA TRADUCAO: SAO TRES.
```

E o remendo óbvio era o pior de todos:

```
item.get("SOURCE_ID") or item.get("source_id") or item.get("fonte")
```

espalhado por cada leitor. Isso não dá um dono à tradução — dá-lhe **um por
ficheiro**, e eles divergem no dia em que alguém acrescentar um alias a um só.

O dono é a **fronteira**, porque é lá que a travessia já acontece: o ingresso já
«transforma o que o coletor largou numa ficha do contrato comum».

## 48.3 · AS TRÊS REGRAS DO TRADUTOR

**Renomeia, não duplica.** Deixar os dois nomes na saída seria entregar a quem
julga a própria doença que a função veio curar.

**O valor atravessa intacto.** `IT-T2-002` sai `IT-T2-002`. Ausência continua
ausência; `NAO SEI` continua `NAO SEI`.

**Dois nomes com dois valores não se escolhem em silêncio.** Levanta
`AliasEmConflito`, e a rota marca o item `erro_de_leitura` — a porta responde
`ERRO`, que **não é rejeição**, e as outras unidades da corrida seguem.

## 48.4 · PROVA — e a escada que ela revelou

```
sem SOURCE_ID   NAO_SEI        «nao da para dizer de onde este item veio»
+SOURCE_ID      NAO_SEI        «o item nao diz quando o fato aconteceu»
+FACT_TIME      NAO_SE_APLICA  «nao ha regra escrita do que conta como T2»
```

A origem deixou de parecer ausente, e a porta passou à pergunta seguinte —
**sem nenhuma regra ter sido relaxada**. Os dois degraus à frente são reais:
falta `FACT_TIME` nas unidades italianas, e `PERGUNTAS_DO_UNIVERSO` tem T3, T4,
T7 e T9 — **não tem T2**.

## 48.5 · CONSEQUÊNCIA — há uma TERCEIRA língua

A unidade `STRUCTURED` fala `CONTENT_ID`, `TEXTO`, `URL`, `CAPTURED_AT`, que não
é o contrato comum (`SOURCE_URL`, `COLLECTED_AT`). Mediu-se a segunda língua e
fechou-se; a terceira fica medida e com nome.

```
UM TRADUTOR QUE ACEITA TUDO DEIXA DE DIZER O QUE E O QUE.
```

Meter `URL` no mapa canónico faria o tradutor do contrato comum conhecer o
vocabulário do STRUCTURED. E `NEM TODO MAPA DE NOMES E O MESMO MAPA`: a
telemetria também mapeia `SOURCE_ID → source_id`, e isso é legítimo, porque o
destino é outro.

## 48.6 · DOIS DEFEITOS MEUS, APANHADOS PELAS PRÓPRIAS TRAVAS

A trava do conflito chamava `pela_porta`, que chama `adm.escrever` — e despejou
417 linhas de decisões de teste dentro do `LIVRO-DE-DECISOES.json`, que é
versionado.

```
UM TESTE QUE ESCREVE NO ACERVO NAO ESTA A TESTAR O SISTEMA: ESTA A ALTERA-LO.
```

E a prova da cadeia chamava `adm.decidir` directamente, saltando a tradução.

```
UMA PROVA QUE SALTA UM DEGRAU NAO PROVA A CADEIA:
PROVA O DEGRAU SEGUINTE COM O ANTERIOR FINGIDO.
```


---

# 49. O ESTÁGIO PERDIA-SE ENTRE A FRONTEIRA E A PORTA

```
MISSAO = C-PROVA-SEAM-INGRESSO-ADMISSAO-V2, 2026-09-11
BRANCH = claude/ingresso-admission-handoff-v1
HEAD   = b2bc02b6e1b6ea3a9911d8f92c40b7fb173e893a
DONO   = coleta/ingresso.py :: unidade_para_a_porta()
PROVA  = tests/test_estagio_atravessa_a_fronteira.py (27 travas, 9 mutações)
```

## 49.1 · O QUÊ

O ingresso produz um `Artefato` de **29 campos**, com `ARTIFACT_TYPE = RAW`. A
porta recebia o item **original, de 6 campos**, sem estágio nenhum.

```
INGRESS_CANONICAL_UNIT_USED_BY_ADMISSION = NO
```

A linha exacta: `orquestrador.pela_entrada` devolvia `len(r["ACEITES"])`.

```
CONTAR UMA COISA NAO E GUARDA-LA.
```

## 49.2 · POR QUÊ — `FACT_TIME` nunca foi o bloqueio

Mesma unidade, mesmo dado, **nada alterado** — só o estágio preservado:

| | regra que falha primeiro |
|---|---|
| como estava | `tempo do fato` |
| com o estágio preservado | `pertence ao universo` |

```
FACT_TIME_WAS_REAL_BLOCKER  = NO
STAGE_LOSS_WAS_REAL_BLOCKER = YES
```

A `COL-LAW-502` existia, e a porta **já a implementava** — `estagio()` lê
`artifact_type`, e a um DOCUMENTO não se pergunta o tempo do FATO. O runtime é
que perdia o estágio antes de ela poder aplicá-la.

```
UMA LEI QUE O RUNTIME NAO DEIXA CHEGAR A QUEM A APLICA
E UMA LEI QUE NAO EXISTE NAQUELE CAMINHO.
```

## 49.3 · A ARMADILHA, MEDIDA ANTES DE ESCREVER

A ficha preenche com `NAO SEI` o que o coletor não disse. E a porta lê isso como
**valor**:

```
fact_time=''         ->  NAO_SEI, «o item nao diz quando»
fact_time='NAO SEI'  ->  passa, como se fosse uma data
```

```
A CONFISSAO DE IGNORANCIA NAO E UM VALOR.
JUNTA-LA COMO SE FOSSE E MENTIR COM A PALAVRA CERTA.
```

Por isso só atravessam **afirmações**. Juntar a ficha ao item sem esse cuidado
teria feito a porta achar que sabia quando o facto aconteceu.

## 49.4 · O DONO, E O QUE SE RECUSOU

`coleta/ingresso.py :: unidade_para_a_porta`, ao lado do `para_a_porta` que já
era dele. **Não é um terceiro objecto**: são os mesmos aceites, com o conteúdo
intacto e o estágio preservado. O item manda no conteúdo; a ficha manda no
estágio; um campo que o item já afirma não é tocado.

Recusou-se entregar o `Artefato` à porta: ele **não tem `texto`**. O conteúdo
morreria para salvar a metadata.

## 49.5 · CONSEQUÊNCIA — o próximo bloqueio, medido e não tocado

```
«nao ha regra escrita do que conta como T2»
```

`PERGUNTAS_DO_UNIVERSO` tem T3, T4, T7 e T9. **Não tem T2**, e não foi criada.

> **ESTADO ATUALIZADO (secção 50).** O bloqueio foi medido, e continua aberto —
> **por decisão, não por omissão**. Ver `50 · A REGRA DE T2 NÃO FOI ESCRITA`.

## 49.6 · A LIÇÃO DE MÉTODO — quatro mutações sobreviveram

```
UMA MUTACAO QUE SOBREVIVE NAO DIZ QUE O CODIGO ESTA CERTO:
DIZ QUE NINGUEM ESTAVA A OLHAR PARA AQUELA LINHA.
```

A última só morreu quando uma trava passou a **correr `correr()` inteiro**.
Provar `pela_entrada` e `pela_porta` em separado não prova que a rota os liga na
ordem certa.

```
PROVAR AS PECAS EM SEPARADO NAO PROVA A MONTAGEM.
```

E, pela terceira missão seguida, uma prova saltava um degrau — usava o item
original em vez da unidade que a fronteira aceitou.

```
PROVAR COM O QUE ENTROU NA FRONTEIRA NAO E PROVAR O QUE SAIU DELA.
```

E um defeito do próprio teste: assumi que `{"id": "mau"}` seria recusado pelo
ingresso. Não é — uma observação sem ficheiro **é** o próprio item.

```
SUPOR QUE UM ITEM E RECUSADO NAO E O MESMO QUE O VER RECUSADO.
```

---

# 50 · A REGRA DE T2 NÃO FOI ESCRITA — E ISSO É O RESULTADO

## 50.1 · O QUÊ

A pergunta era: *o que um documento precisa provar para a Admission dizer que
ele pertence a «T2 — Clima e tempo»?* A ordem era **medir primeiro**, e só
escrever a regra se a medição desse resposta clara.

```
T2_RULE_IMPLEMENTED = NO
```

`PERGUNTAS_DO_UNIVERSO` ficou com T3, T4, T7 e T9 — **exactamente como estava**.
Nem uma palavra acrescentada. Nenhuma lei mudou; a Bíblia não subiu de versão.

O que ficou foi a **prova do não**: `provas/a_regra_de_t2.py`,
`tests/test_a_regra_de_t2.py`, `docs/operacao/MEDICAO-DA-REGRA-T2.md`.

    UMA DECISÃO DE NÃO IMPLEMENTAR NÃO DEIXA CÓDIGO.
    SE NÃO DEIXAR PROVA, DAQUI A TRÊS MESES ALGUÉM REFAZ O ERRO
    «PORQUE NINGUÉM TINHA TENTADO».

## 50.2 · POR QUÊ — as palavras de clima vivem fora de T2

Gabarito de **46 documentos reais** desta árvore: 10 positivos, 33 negativos,
3 ambíguos. O rótulo de cada um vem do que **o próprio documento declara nas
primeiras linhas** — não do que dava jeito.

| termo | T2 (10) | NÃO-T2 (33) |
|---|---:|---:|
| `evapotraspirazione` | 6 | 0 |
| `agrometeo` | 8 | 8 |
| `meteo` | 9 | 25 |
| `vento` | 7 | **30** |
| `previsione` | 0 | 11 |

**Nenhum termo** aparece nos 10 positivos e em zero negativos. E o resultado que
vira a intuição do avesso: as palavras óbvias de clima aparecem **mais fora de
T2 do que dentro**.

Não é acidente. É o que um boletim de praga **é**: a praga responde ao tempo,
por isso todo o boletim fitossanitário fala de tempo.

```
DOCUMENTO SOBRE CLIMA != DOCUMENTO QUE APENAS MENCIONA CLIMA,
E O VOCABULARIO SOZINHO NAO VE A DIFERENCA.
```

E os dois termos que **pareciam** salvar a regra traem-se quando se lê onde
estão: `climatologia` está nos boletins de VITE porque eles creditam o
*«Servizio Meteorologia e Climatologia di Arpav»* — **é o nome de quem
colaborou**; `bagnatura fogliare` está nos boletins da Campânia como **condição
de risco de infecção** — é vocabulário de defesa da cultura.

```
UMA PALAVRA NAO TRAZ O SEU ASSUNTO COLADA.
ONDE ELA ESTA DECIDE O QUE ELA PROVA.
```

## 50.3 · O CONTRAEXEMPLO QUE FUNDA TUDO

A **ARPAV** está dos dois lados do gabarito. A mesma agência publica:

- `Meteo Veneto: luglio 2026 molto caldo, poche piogge` → **T2**
- `U.O. Fitosanitario — Bollettino n. 20 VITE` → **T3**

```
O PUBLICADOR NAO DECIDE O TERRITORIO.
```

Sem esses seis negativos da ARPAV no gabarito, classificar pela fonte
**pareceria funcionar** — e estaria errado em silêncio. Um gabarito onde cada
publicador cai todo do mesmo lado não testa a regra: testa a lista de
publicadores.

```
UM GABARITO SEM O MESMO PUBLICADOR DOS DOIS LADOS
NAO MEDE A REGRA. MEDE QUEM IMPRIMIU.
```

## 50.4 · O ATAQUE QUE DECIDIU — e a lição de método desta missão

Comparar candidatas que **eu** escolhi só responde *«estas não servem»*. Isso
não fecha nada: sobra sempre a suspeita de que faltou imaginação.

Então deixou de haver candidatas minhas. O **corpus** propôs 6.582 termos e
bigramas dos positivos; ficaram 4.942 que não aparecem em negativo nenhum; e
todos os 10 positivos são alcançáveis por algum deles. **Uma lista perfeita
existe.** A pergunta seguinte é a única que importa — **de que é que ela é
feita?**

```
7/10  'venerdì'              7/10  'pomeriggio'
7/10  'unità organizzativa'  7/10  'dipartimento'
```

Dias da semana. Horas do dia. O nome do departamento que imprime.

E a prova final — treinar num publicador, testar no que ficou de fora:

```
sem SIAS   cobre o treino 9/9  ·  acerta no retido 0/1
sem ARPAE  cobre o treino 8/8  ·  acerta no retido 0/2
sem ARPAV  cobre o treino 3/3  ·  acerta no retido 0/7

GENERALIZACAO = 0/10
```

Cobre o treino **sempre**. Acerta no retido **nunca**.

```
UMA REGRA QUE SO ACERTA EM QUEM JA VIU NAO E UMA REGRA:
E A LISTA DOS DOCUMENTOS QUE JA TINHAMOS.
```

**A lição de método**, e é a que vale para todas as missões seguintes:

```
NAO PERGUNTE «ESTA CANDIDATA SERVE?».
PERGUNTE «EXISTE ALGUMA QUE SIRVA, E DE QUE E FEITA A MELHOR?»
E DEPOIS TREINE NUM E TESTE NOUTRO.
```

Uma métrica medida **no material em que a regra foi ajustada** não é uma
medição: é um espelho.

## 50.5 · O QUE SE RECUSOU

**Recusou-se escrever `A5-titulo-do-documento`**, e ela tinha `FP = 0` e
`FN = 0`. Parece exactamente a regra certa. Não é uma regra de clima: é a lista
dos **nomes comerciais** de três publicações — `agrometeo… informa`,
`meteo veneto`, `bollettino agrometeorologico`. E mesmo assim responde
`NAO_SEI` ao **SIAS**, uma fonte T2 declarada cuja página é uma tabela de
precipitação sem uma linha de prosa.

**Recusou-se arredondar os três ambíguos.** Os boletins da ARIF Puglia abrem com
duas páginas de análise sinóptica e só depois trazem *Bactrocera*. A ficha
`IT-T3-008` declara `T3` — e declara, nos próprios tópicos, `agrometeorologia`.
São as duas coisas num PDF. Ficaram `AMBIGUO`.

**Recusou-se o desenho C** (classificar pela `source_id` → `territory` da
ficha). Além de a Admission nunca ler `source_id`, ele quebraria
`DECLARADO ≠ OBSERVADO`: a porta passaria a dizer *«é T2 porque a ARPAV
publicou»*, nunca *«é T2 porque o documento prova»*.

## 50.6 · O QUE ISTO TERIA CUSTADO

O caminho fácil estava a um `commit` de distância:

```python
"T2": ["clima", "tempo", "meteo", "temperatura", "pioggia", "vento"],
```

`TP = 9/10`. Número bonito. E, medido:

```
FALSE_POSITIVE = 32 dos 33 negativos
```

Todos os boletins fitossanitários de Campânia, Lazio, Trentino, Molise,
Piemonte, Puglia e Veneto passariam a ser **clima** — e, como a Admission
escreve no `LIVRO-DE-DECISOES.json`, cada um ficaria lá **com justificação**:
*«fala de clima, tempo, meteo, temperatura — que é do que «T2» trata»*.
Verdade palavra a palavra, falsa como julgamento.

```
O PIOR DEFEITO NAO E O QUE FALHA ALTO.
E O QUE ACERTA NA METRICA E ERRA NO MUNDO,
COM A PROVA ESCRITA AO LADO.
```

## 50.7 · O QUE FICOU ABERTO, MEDIDO E NÃO TOCADO

Descobertas por acidente, **nenhuma corrigida** — o brief mandou não atacar o
próximo bloqueio.

- **`lancio` casa dentro de `bilancio`.** As listas de `PERGUNTAS_DO_UNIVERSO`
  procuram subcadeias, sem fronteira de palavra. Por isso o `Bilancio
  Fitosanitario` é reclamado por **T9**, e `eventi intensi` — um evento
  meteorológico — também. Documentos T2 legítimos recebem `NAO` com uma
  justificação falsa.
- **Um documento pode pertencer a dois territórios.** `decidir(item, universo)`
  é por par, portanto o modelo aguenta — mas as fichas das fontes assumem **um
  território por fonte**, e a ARIF Puglia prova que isso não é verdade do
  documento.
- **Território é propriedade da FONTE; universo é pergunta ao DOCUMENTO.** Duas
  coisas diferentes com o mesmo nome. A ARPAV mostra-as a divergir.

```
DUAS COISAS DIFERENTES COM O MESMO NOME
SAO UM DEFEITO A ESPERA DE UMA MISSAO QUE AS CONFUNDA.
```

## 50.8 · O ESTADO, PARA A PRÓXIMA MISSÃO

```
T2 na Admission                 SEM REGRA, por decisão medida
resposta da porta a T2          NAO_SE_APLICA — e é verdade
T3 · T4 · T7 · T9               intactos, listas não tocadas
Admission (lógica)              intacta
runtime                         intacto
NEW_FAILURES                    0   (21 falhas, as mesmas 21 do baseline)
SYSTEM_MAP_CHECK                PASS
```

Se um dia aparecer material novo — mais publicadores T2, ou uma lei que diga o
que é ser *sobre* um assunto — o portão **reabre-se refazendo a medição**, não
contornando-a. `tests/test_a_regra_de_t2.py` cai alto no dia em que alguém
escrever T2 sem refazer a conta.

---

# 51 · A FRONTEIRA ESTAVA CERTA. O MECANISMO É QUE NÃO.

## 51.1 · O QUÊ

Depois de a regra de T2 falhar, ficou no ar uma dúvida maior do que ela: se o
mecanismo não consegue dizer a que universo um documento pertence, talvez a
**responsabilidade** esteja na camada errada. A pergunta foi posta assim:

> *«O julgamento `(item, universo)` deve continuar na Admission, ou deve ser
> movido para Intelligence?»*

Resposta, depois de ler as leis e estudar seis sistemas maduros:

```
ADMISSION_REMAINS_UNIVERSE_OWNER               YES
THEMATIC_CLASSIFICATION_MOVES_TO_INTELLIGENCE  NO
CURRENT_KEYWORD_IMPLEMENTATION_SUFFICIENT      NO
MULTI_UNIVERSE_REQUIRES_ARCH_CHANGE            NO   (provado)
BIBLE_CHANGE_REQUIRED                          NO
```

Zero linhas de runtime alteradas. `PERGUNTAS_DO_UNIVERSO` intacto.

## 51.2 · A ARMADILHA DE VOCABULÁRIO — a lição mais barata desta missão

A pergunta chegou com a palavra **"julgamento"**. Nesta casa essa palavra já tem
dono, e é outro:

> **COL-LAW-005** — *«`COLETAR` adquire evidência. `ADMITIR` decide se a evidência
> entra num universo. `JULGAR` combina e interpreta depois.»*

O par `(item, universo)` **não é julgar**. É **admitir**. Traduzida para a língua
da casa, a pergunta era *«ADMITIR deve continuar separado de JULGAR?»* — e assim
escrita **já tinha lei**, escrita há missões.

```
RESPONDER DEPRESSA A UMA PERGUNTA MAL TRADUZIDA
E MUDAR A ARQUITETURA POR CAUSA DE UMA PALAVRA.
```

Por isso a primeira coisa que se faz numa dúvida estrutural é **citar a
autoridade antes de a reinterpretar**. Metade da resposta estava lá.

## 51.3 · POR QUÊ — o que os seis sistemas dizem, e onde discordam

Databricks Medallion · AWS data lake layers · OCCRP Aleph/FollowTheMoney ·
OpenCTI · Azure AI Document Intelligence · Google Document AI. Três famílias
tecnológicas independentes, e **concordam em cinco pontos**:

1. **Ingestão não interpreta.** Bronze: *«no data cleanup or validation is
   performed here»*. Raw na AWS: *«the immutable copy of the data»*.
2. **Validação é estrutural, não semântica.** Silver pergunta *dá para ler, está
   completo, está conforme* — nunca *é sobre o quê*.
3. **Classificação semântica é um componente com dono próprio.** Nenhum dos seis
   a põe dentro do leitor; nenhum a põe no consumidor.
4. **Um item pode ter vários significados e vários destinos.**
5. **A incerteza tem forma própria e sobrevive** — `doubt`, confidence,
   quarentena, revisão humana.

**Onde divergem** — e a divergência ensinou mais do que a convergência: no
**quando**. Document AI e Document Intelligence classificam **antes** de extrair,
para escolher o extrator. Medallion e AWS classificam **depois** de validar, para
servir o consumidor. Aleph e OpenCTI fazem as duas: tipam à entrada e
**reinterpretam depois**.

```
A DIVERGENCIA NAO E SOBRE QUEM DECIDE. E SOBRE QUANDO.
QUE SEJA UM COMPONENTE PROPRIO, NISSO OS SEIS CONCORDAM.
```

E isso resolveu a pergunta: `COL-LAW-043` põe `UNIVERSO` entre os **11 campos que
a Intelligence RECEBE**. Mover a decisão para lá faria o consumidor produzir
aquilo que ele consome.

```
QUEM CONSOME O CAMPO NAO PODE SER QUEM O DECIDE.
```

## 51.4 · O QUE O ESTUDO MUDOU — não o dono, o diagnóstico

Esperava-se que o estudo mexesse na fronteira. Não mexeu: **confirmou-a**. O que
ele trouxe de novo foi outra coisa, e mais útil —

> **Azure AI Document Intelligence:** *«Custom classifiers identify document types
> **before invoking an extraction model**.»*
> **Google Document AI:** classificar vive numa categoria de processador
> **separada** da extração.

Decidir *«que tipo de documento é este»* é, em toda a indústria madura, **um
problema com dono, corpus e avaliação próprios**. Não é uma condição dentro do
leitor, e muito menos uma lista de palavras.

```
UMA LISTA DE PALAVRAS DENTRO DA PORTA
NAO E UMA IMPLEMENTACAO POBRE DE CLASSIFICADOR.
E OUTRA COISA A FINGIR QUE E UM.
```

`CURRENT_MECHANISM_FIT_FOR_PURPOSE = NO` — e isto **não autoriza** trocá-lo já.
O estudo diz de que **família** a solução é (regra estruturada + abstenção +
revisão: o `doubt` do Aleph casado com o `NAO_SEI` desta casa), não qual é.
Construir um classificador exige corpus rotulado com held-out honesto, e o T2
provou que esta árvore ainda não o tem.

## 51.5 · DONO NÃO É IMPLEMENTAÇÃO — e a prova da multipertença

A missão foi obrigada a separar duas perguntas que soam a uma só:

```
A. QUEM E DONO DA DECISAO ITEM x UNIVERSO?     -> a Admission. Fechado.
B. O MECANISMO DELA CHEGA?                     -> nao. Aberto.
```

Confundi-las é o erro que teria movido meia arquitetura para corrigir uma lista
de palavras.

```
UM MECANISMO MAU NAO PROVA QUE O DONO ESTA ERRADO.
PROVA QUE O DONO ESTA MAL EQUIPADO.
```

E a multipertença, **provada, não suposta**:

```
(PROVA-MULTI, T3) = SIM   fala de fungo, malattia
(PROVA-MULTI, T4) = SIM   fala de ministero, decreto, autorizzazione
(PROVA-MULTI, T7) = NAO   fala claramente de outro universo
```

Um item, três decisões independentes, cada uma com o seu motivo e a sua
`rule_version`. O livro real já tem **44 itens com mais de uma decisão**.
`MULTI_UNIVERSE_REQUIRES_ARCH_CHANGE = NO`.

**A ressalva, porque sem ela isto seria meia verdade:** o orquestrador pergunta
**um** universo por corrida (`pela_porta(itens, universo, run_id)`, o `alvo` do
pedido). O modelo suporta; o runtime não exercita. Implementação, não
arquitetura.

## 51.6 · CONSEQUÊNCIA — uma regra de método nova, e onde ela vive

Esta missão instalou uma regra permanente:

> **`DÚVIDA ESTRUTURAL → ESTUDO EXTERNO ANTES DE IMPLEMENTAR`**
> [`README.md`](README.md), secção própria, irmã arquitetural do item 7
> («trabalho visual consulta o Design System antes de inventar»).

**A regra inteira não se repete aqui** — tem um dono, e é lá. O que fica registado
é **por que ela precisou de existir**: a prática já existia como
**acontecimento** (Parte XVII da Bíblia, «AS LEIS ROUBADAS», emenda V1.1, 30 leis
vindas de um estudo de sistemas maduros) e **não existia como regra**.

```
UM PRECEDENTE NAO E UMA REGRA.
NINGUEM REPETE UM ACONTECIMENTO POR ELE TER ACONTECIDO.
```

E ela carrega o próprio travão, porque uma regra de pesquisa sem limite de
pesquisa é uma licença para adiar: para-se em **≥ 3 sistemas maduros** e **≥ 2
famílias tecnológicas**, quando a resposta converge ou contradiz explicitamente.
Se nem assim fechar, o resultado é `NÃO SEI / PRECISA ESTUDO MAIOR` — que é um
resultado.

## 51.7 · O ESTADO, PARA A PRÓXIMA MISSÃO

```
fronteira Admission/Intelligence   FECHADA, e confirmada por fora
mecanismo de PERGUNTAS_DO_UNIVERSO INSUFICIENTE, declarado
multipertenca                      permitida e provada; runtime so exercita um
T2                                 T2_RULE_IMPLEMENTED = NO, intacto
Biblia                             nao mudou. COL-LAW-005/042/043 confirmadas
runtime                            nao mudou
NEW_FAILURES                       0
SYSTEM_MAP_CHECK                   PASS
```

O que ficou por saber, e não se resolve navegando mais — resolve-se com material:
se existe nesta árvore corpus rotulado suficiente para treinar **ou sequer
avaliar** um classificador; e se *«documento SOBRE X»* merece lei própria ou é
consequência de leis que já existem.

---

# 52 · HÁ CHÃO PARA AVALIAR UM UNIVERSO, E PARA MAIS NENHUM

## 52.1 · O QUÊ

A secção 51 fechou o dono e declarou o mecanismo insuficiente, e deixou uma
pergunta por responder: existe nesta árvore corpus rotulado para **avaliar** — e
eventualmente **treinar** — o substituto? Contou-se.

```
T2 = B    serve para AVALIAR · não serve para treinar
T3 = D    T4 = D    T7 = D    T9 = D
T1 · T5 · T10 · T11 · T12 · T13 = D
OVERALL_VERDICT = B
```

Nenhum classificador construído. Nenhum rótulo gerado. `PERGUNTAS_DO_UNIVERSO`
intacto.

## 52.2 · A REGRA QUE GOVERNOU A CONTAGEM INTEIRA

```
ROTULO EXISTE  !=  ROTULO E VERDADE CONFIAVEL
```

e o caso particular que decidiu a missão:

```
DECISAO GERADA POR `PERGUNTAS_DO_UNIVERSO`  !=  GABARITO
```

O livro de decisões tem **813 linhas** e **zero gabarito**. Todas as 813 saíram
da lista de palavras que se quer substituir, e as 36 que dizem `SIM` trazem, na
evidência, **as palavras que as produziram**.

```
UM CLASSIFICADOR TREINADO NAS RESPOSTAS DO ANTERIOR
NAO O SUBSTITUI: CONFIRMA-O.
```

O livro continua útil — para comparação, diagnóstico e *hard-negative mining*:
os 597 `NAO_SEI` são exatamente onde o vocabulário não chegou, e isso é uma lista
de casos difíceis pronta a usar. **Útil não é o mesmo que gabarito.**

## 52.3 · QUE MATERIAL PODE SER GABARITO, E QUE MATERIAL NÃO PODE

| origem | autoridade | gabarito? |
|---|---|---|
| gabarito de T2 (46 documentos) | `DOCUMENT_SELF_DECLARED` | **SIM** |
| livro de decisões (813) | `KEYWORD_DERIVED` | **NÃO** |
| ficha da fonte / `MASTER_ITALIANO` | `SOURCE_CONTRACT_DECLARED` | **NÃO** |
| manifestos de amostra | `SOURCE_CONTRACT_DECLARED` | **NÃO** |
| registo de artefatos | `UNKNOWN` — não tem campo de universo | **NÃO** |

A ficha da fonte está fora por **três contraexemplos medidos**, não por gosto:
a ARPAV publica T2 **e** T3; a `IT-T5-003` declara *«Preço e mercado»* e entrega
*«Bilancio Fitosanitario»*; a `IT-T7-002` declara *«Ciência e ensaio»* e entrega
uma lista administrativa de organizações de produtores.

```
TERRITORIO DA FONTE != UNIVERSO DO DOCUMENTO,
E JA HA TRES PROVAS DISSO NESTA ARVORE.
```

## 52.4 · O DEFEITO QUE ESTA PRÓPRIA PROVA TEVE — e é a lição de método

A primeira versão do censo procurava o `SOURCE_ID` no **caminho**. Os 43 textos
derivados chamam-se `RAW-<sha>.txt` e não carregam fonte no nome. Resultado: 43
dos 46 itens caíram num balde chamado `NAO SEI`, e a prova respondeu

```
PUBLISHER_HOLDOUT_POSSIBLE = YES
```

porque o balde contava como **um publicador**.

```
UM BALDE DE DESCONHECIDOS CONTADO COMO CATEGORIA
E DIVERSIDADE FABRICADA.
```

Foi apanhado por olhar para a linha `publicadores: {'NAO SEI': 43, ...}` em vez
de olhar só para o `YES`. Corrigido pela **linhagem** — o registo de artefatos
diz de que pai cada derivado nasceu, e o caminho do pai diz a fonte — e agora
`NAO SEI` não conta como publicador em lado nenhum. 13 publicadores reais.

E a mesma armadilha apareceu num segundo sítio: `IT-BOLLETTINI-VPN-2026` é uma
**pasta** com boletins de quatro regiões, e estava a contar como um publicador.

```
UMA PASTA NAO E UMA INSTITUICAO.
O NOME DO DIRETORIO NAO E UM FACTO SOBRE O MUNDO.
```

## 52.5 · OS CRITÉRIOS FORAM ESCRITOS ANTES DA CONTAGEM

Estão em código (`CRITERIOS`), cada um com a razão ao lado, e presos um a um
pelos testes — não como soma. Subir um limiar passa; **baixar cai alto**.

| uso | positivos | negativos | publicadores | mais |
|---|---:|---:|---:|---|
| SANITY | ≥ 3 | ≥ 3 | ≥ 2 | — |
| EVALUATION | ≥ 10 | ≥ 10 | ≥ 3 | holdout de publicador obrigatório |
| TRAINING | ≥ 100 | ≥ 100 | ≥ 5 | ≥ 2 famílias, e cumprir EVALUATION |

Três publicadores para avaliar porque é o mínimo em que **tirar um ainda deixa
dois**. Com dois, tirar um deixa um, e um publicador não é uma distribuição.

```
UM CRITERIO ESCRITO DEPOIS DA CONTAGEM
E O ALVO DESENHADO A VOLTA DA FLECHA.
```

## 52.6 · MULTIRRÓTULO — permitido não é exercido

```
ITEMS_WITH_2_PLUS_UNIVERSES   1
MULTILABEL_CONFIRMED          0
```

A secção 51 provou que a arquitetura **permite** multirrótulo. O corpus real
ainda **não o exerce**: o único item com três decisões tem três `NAO_SEI` e
`NAO_SE_APLICA`, que não são rótulos.

```
TER TRES DECISOES REGISTADAS NAO PROVA QUE TRES ESTAO CERTAS.
PERMITIDO != EXERCIDO.
```

## 52.7 · A RESSALVA QUE A LETRA `B` NÃO MOSTRA

As candidatas `A3` e `A5` da missão de T2 **nasceram de olhar para este corpus**.
Para elas o gabarito é treino, não teste.

```
UM CONJUNTO SO E INDEPENDENTE DE QUEM NAO OLHOU PARA ELE.
```

Para um mecanismo que ninguém ajustou aqui, continua a servir de avaliação. E a
regra de partição fica escrita para quem avaliar: o **TEST** é um publicador
retido por inteiro, nunca «outros documentos dos mesmos publicadores».

## 52.8 · CONSEQUÊNCIA — a lacuna é alcançável, e sem coletar

Documentos **já nesta árvore** que abrem declarando o seu próprio género:

```
T3    27 documentos · 9 publicadores
T2     9 documentos · 2 publicadores
T4     1 documento  · 1 publicador
```

**T3 é alcançável sem coletar nada.** O que falta é a passagem de rotulagem — e
isso é trabalho de uma pessoa a ler, não de uma máquina a adivinhar. Rotular com
LLM o corpus inteiro reintroduziria exatamente o defeito da secção 52.2, com
outro nome.

Para levar um universo de `D` a `B`: 10 positivos, 10 negativos, 3 publicadores
no lado positivo, todos com corpo e razão escrita. Para levar T2 de `B` a `A`:
mais 90 positivos, mais 67 negativos, mais 2 publicadores, e pelo menos uma
língua além do italiano — o corpus é hoje **100% IT**.

## 52.9 · O ESTADO, PARA A PRÓXIMA MISSÃO

```
corpus de avaliacao          existe para T2, e so para T2
corpus de treino             nao existe para universo nenhum
gabarito legitimo            1 origem em 5
livro de decisoes            813 linhas, 0 ground truth, util como hard negatives
T3                           alcancavel por rotulagem do que ja esta ca
diversidade de lingua e pais 1 e 1 — o ponto mais fraco do corpus
Admission · T2 · Biblia      intactos
NEW_FAILURES                 0
SYSTEM_MAP_CHECK             PASS
```

A decisão que fica para quem vier: **rotular o que há, coletar material novo,
pedir revisão humana, ou combinar os três.** O censo dá a conta; não dá a
escolha.

---

# 53 · O VAZAMENTO NÃO ESTÁ SÓ EM QUEM ROTULA. ESTÁ EM QUEM ESCOLHE.

## 53.1 · O QUÊ

A secção 52 fechou a regra de que um rótulo produzido pelo mecanismo antigo não
pode ser gabarito do novo. Ao preparar a rotulagem humana de T3 apareceu o
mesmo defeito **um degrau acima**, e este não estava escrito.

Os 27 candidatos T3 do censo não foram escolhidos por uma pessoa: foram
encontrados por uma varredura de **seis frases literais**.

```
'difesa integrata' 16 · 'servizio fitosanitario' 13 ·
'bollettino fitosanitario' 12 · 'monitoraggio' 10 ·
'difesa delle colture' 7 · 'u.o. fitosanitario' 6
```

Se o pacote de revisão levasse **só esses 27**, e uma pessoa — uma pessoa de
verdade, sem máquina nenhuma — os marcasse `SIM`, o gabarito resultante teria a
propriedade de que **todo positivo contém uma daquelas seis frases**. E então
qualquer classificador baseado nelas tiraria nota perfeita.

```
UM GABARITO CUJOS POSITIVOS FORAM SELECIONADOS POR UMA FRASE
NAO MEDE UM CLASSIFICADOR: DEVOLVE-LHE A PROPRIA FRASE.
```

## 53.2 · POR QUÊ É DIFERENTE DA §52

A §52 fala do **rotulador**: quem atribui o rótulo não pode ser o mecanismo que
se quer substituir. Isto é do **amostrador**: mesmo com o rotulador perfeito —
uma pessoa, a ler, com a razão escrita — o conjunto continua contaminado se a
**entrada** dele foi escolhida pelo sinal que se vai avaliar.

```
LEAKAGE NO ROTULADOR   quem decide o rotulo  (§52)
LEAKAGE NO AMOSTRADOR  quem decide QUEM entra na lista  (§53)
```

Os dois produzem o mesmo número bonito, e nenhum dos dois aparece na métrica.

    ROTULADOR HUMANO NAO SALVA UM CORPUS ESCOLHIDO POR MAQUINA.

## 53.3 · A CORREÇÃO, E É BARATA

O pacote leva **os 46 documentos do corpus**, os 27 lá dentro **sem marca
nenhuma**, em ordem por hash do caminho — não por publicador, não por pasta, não
por «mais parecido com T3». O revisor olha para documentos, não para uma
pré-selecção. Os negativos saem da mesma passagem que os positivos, e por isso
não são definidos por ausência de frase.

E o que a máquina já «sabia» fica escondido até a decisão — a saída de
`PERGUNTAS_DO_UNIVERSO`, o território da ficha da fonte, e quais casaram a
varredura — numa secção `AUDIT_AFTER_REVIEW`, no fim.

```
HUMAN_LABEL NAO PODE NASCER A OLHAR PARA CURRENT_CLASSIFIER_OUTPUT.
```

## 53.4 · UMA ARMADILHA MEDIDA, QUE NÃO ERA HIPÓTESE

O nome do ficheiro tem de aparecer na ficha, porque procedência faz parte do
registo. Mas neste corpus, **seis** documentos têm no nome `Fitosanitari`,
`Agrometeorologico` ou `Meteorologico` e **cinco deles não dizem nada disso na
abertura**.

```
O NOME DO FICHEIRO NAO E PROVA SOBRE O CONTEUDO.
MOSTRAR PROCEDENCIA E OBRIGATORIO; TRATA-LA COMO EVIDENCIA SEMANTICA E ERRO.
```

Por isso o aviso vai no topo do pacote, antes da primeira ficha.

## 53.5 · CONSEQUÊNCIA

O pacote existe e está vazio: `AUTO_LABELS_ASSIGNED = 0`, `REVIEWER_A`,
`REVIEWER_B` e `FINAL_LABEL` todos em `NOT_RUN`, e `SECOND_REVIEW = NOT_RUN`
porque copiar A para B e chamar-lhe dupla revisão seria uma mentira barata.

As duas travas — não vazar o que a máquina sabe, e não pré-preencher rótulo —
foram provadas **por mutação**, não por afirmação.

O que falta é o que nenhuma missão pode fazer sozinha: **uma pessoa a ler 46
documentos e a escrever a razão de cada decisão.**

---

# 54 · UM CORPUS CURADO PARA UMA PERGUNTA NÃO É A POPULAÇÃO DE OUTRA

## 54.1 · O QUÊ

A §53 corrigiu o viés da **pré-seleção**: os 27 candidatos deixaram de ser
mostrados sozinhos. Ficou por examinar o degrau de baixo — **de onde veio a
lista inteira**.

Veio de `censo._gabarito_t2()`. Lido do código, não assumido:

```
CURRENT_PACKET_POPULATION_SOURCE   censo._gabarito_t2()
UNIVERSOS_QUE_O_GABARITO_ROTULA    ['T2']
CURRENT_46_SELECTED_FOR_T2         YES
CURRENT_46_SELECTED_FOR_T3         NO
```

```
T2-CURATED CORPUS != GENERAL T3 EVALUATION FRAME.
```

A hierarquia completa, que agora tem três degraus:

```
LEAKAGE NO ROTULADOR   quem decide o rotulo                 §52
LEAKAGE NO AMOSTRADOR  quem decide quem entra na lista      §53
LEAKAGE NA POPULACAO   de que PERGUNTA nasceu a lista       §54
```

Corrigir os dois primeiros e deixar o terceiro dá um pacote perfeitamente
neutro **sobre a população errada**.

## 54.2 · POR QUÊ — o viés não estava na contagem, estava na forma

```
CURRENT_PACKET 46 · TOTAL_REVIEWABLE 53 · COBERTURA 86%
```

86% parece bom, e **é a métrica errada**. Contada por publicador a cobertura é
**14/17**, e três publicadores estão **inteiramente ausentes**: ISTAT
(estatística), AGEA (subsídio), ISMEA (preço).

Não é acaso. O gabarito de T2 procurava *«documentos sobre tempo»* e
*«documentos que claramente não são tempo»*, e na prática os negativos dele
saíram **todos da mesma prateleira: boletins**. O que ficou de fora é o material
**tabular e administrativo** — que é exatamente o negativo de que T3 precisa.

```
UMA COBERTURA ALTA EM DOCUMENTOS PODE ESCONDER
UM BURACO INTEIRO EM PUBLICADORES.
CONTE PELO GRUPO, NAO PELA LINHA.
```

## 54.3 · A CORREÇÃO NÃO É AMOSTRAR MELHOR

```
TOTAL_REVIEWABLE = 53
SELECTION_METHOD = CENSO, NAO AMOSTRA
ADDITIONAL_ITEMS_NEEDED = 7
```

Com 53 documentos revisáveis no total, escolher um subconjunto **introduz viés
sem poupar trabalho nenhum**.

```
ABAIXO DE CERTA ESCALA, A AMOSTRAGEM MAIS NEUTRA E NAO AMOSTRAR.
SEM REGRA DE AMOSTRAGEM NAO HA REGRA DE AMOSTRAGEM PARA ENVIESAR.
```

E as 46 **não se apagam**: são subconjunto do frame completo, e a revisão delas
continua válida quando os outros 7 entrarem. `CURRENT_46_ROLE =
B. PARTIAL_T3_EVAL_SLICE`.

## 54.4 · DUAS MEDIDAS QUE MUDAM A LEITURA DE QUALQUER CORPUS

**A unidade é o documento, não o caminho.** Nove documentos desta árvore vivem
em dois sítios — a captura e a amostra. Contados por caminho seriam 63; por
bytes são 54.

**Edições não são evidências independentes.** Os 46 documentos são **34 séries
de publicação**: quatro zonas do mesmo boletim ARPAV, quatro edições do mesmo
boletim da Fondazione Edmund Mach.

```
QUATRO ZONAS DO MESMO BOLETIM SAO QUATRO DOCUMENTOS
E QUASE UMA SO EVIDENCIA.
```

## 54.5 · ESTRUTURA NÃO É COBERTURA

O red team produziu uma frase que faltava a esta casa. Dezassete de dezassete
publicadores podem ser retidos por inteiro deixando ≥ 10 documentos — portanto
`PUBLISHER_HOLDOUT_POSSIBLE = YES`.

Mas se reter um publicador deixa **positivos e negativos de T3 dos dois lados**
é **desconhecido, e continua desconhecido até haver rótulos**.

```
PODER PARTIR NAO E TER O QUE PARTIR.
ESTRUTURA NAO E COBERTURA.
```

## 54.6 · O DEFEITO DESTA PRÓPRIA PROVA, E QUASE PASSOU

A primeira versão respondeu `CURRENT_46_SELECTED_FOR_T2 = NO` — o **contrário**
da verdade. Ela procurava uma frase dentro do ficheiro de T2, e a frase que eu
procurava não era a frase que lá estava.

```
PROCURAR UMA FRASE QUE EU IMAGINEI NAO E LER O CODIGO.
```

Foi apanhado por o `NO` não bater com o que o resto da prova mostrava.
Corrigido: a resposta vem agora dos **rótulos que o gabarito produz** — se todos
falam de um universo, foi para esse universo que a população foi montada. É a
mesma disciplina de §52.4, e é a terceira missão seguida em que uma prova minha
deu verde por olhar para o sítio errado.

```
QUANDO UMA PROVA RESPONDE O CONTRARIO DO QUE O RESTO DELA MOSTRA,
O DEFEITO ESTA NA PROVA — NAO NO MUNDO.
```

## 54.7 · O LIMITE QUE NEM O CENSO COMPLETO RESOLVE

```
53 documentos · 34 series · 17 publicadores · 1 pais · 1 lingua
```

O atlas declara 54 fontes italianas, e a Admission encontrará também França e
Espanha. Mesmo completo, este frame avalia T3 **dentro de material
agro-institucional italiano**, e não autoriza afirmar generalização para fora
disso. Fica escrito para ninguém se enganar depois.

---

# §55 · RECEBER UMA REVISÃO HUMANA SEM LHE TOCAR

**Missão:** `C-INGEST-REVIEW-A-E-ADJUDICACAO-T3-V1` · HEAD final `d560ad69`
**Artefactos:** `provas/qualidade_t3.py` · `data/review/t3/` ·
`docs/operacao/T3-HUMAN-QUALITY-GATE-PTBR-V1.html`

## 55.1 · O QUÊ

As 53 respostas humanas chegaram. Entraram como evidência imutável
(`INPUT_SHA256` registado antes de qualquer leitura), foram provadas contra o
pacote que as gerou, e partiram-se em duas filas:

```
CONFIRMACAO      32   a resposta está dada; falta a RAZÃO e a atestação
SEGUNDA LEITURA  21   incerteza 11 + tensão 10, e a resposta não aparece
```

A **tensão** é um `T3_NAO` num documento que se auto-declara fitossanitário nos
~900 caracteres que a pessoa viu. Isso não classifica nada e não troca rótulo
nenhum. Diz uma coisa só: vale a pena olhar outra vez, com mais contexto.

## 55.2 · ZERO RAZÕES EM 53 RESPOSTAS

`HUMAN_REASON` veio nulo nas 53 — porque a primeira interface nunca perguntou.

```
CAN DO != DID DO.
UM CAMPO QUE EXISTE E UM CAMPO QUE NINGUEM PREENCHEU
SAO A MESMA COLUNA VAZIA.
```

O portão **pergunta** a razão, com vocabulário fechado por rótulo, e `OUTRO`
exige o texto da pessoa. E pergunta também a atestação — porque a página sabe
o que **mostrou**, e só a pessoa sabe o que **usou**:

```
EVIDENCE_PRESENTED != EVIDENCE_USED
```

## 55.3 · CEGO NÃO É ESCONDIDO NA INTERFACE

Um item da segunda leitura não leva rótulo, nota, motivo de fila ou gatilho —
nem no ecrã **nem dentro do JSON que viaja na página**.

```
ESCONDER NA INTERFACE E DEIXAR NO PAYLOAD
NAO E CEGAR: E ESPERAR QUE NINGUEM OLHE.
```

E o contexto extra tem de ser escolhido por regra **estrutural**: o documento
do princípio, em páginas de tamanho fixo. Mostrar o pedaço que contém a
expressão do gatilho seria entregar a resposta com cara de pergunta.

## 55.4 · CONFIRMAR NÃO É LER OUTRA VEZ

Um item confirmado sai com `CONFIRMED`, **sem** `LABEL_A2`. Fabricar um A2
igual ao A transformaria «não mudei de ideias» em «li duas vezes e bateu».

E quando a pessoa reabre um item que já viu respondido, essa leitura deixa de
ser cega — o ficheiro diz isso: `REOPENED_BY_HUMAN=YES`, `BLIND=false`.

```
REVIEW_A != REVIEW_A2
E NENHUM DOS DOIS E UM SEGUNDO REVISOR INDEPENDENTE:
E A MESMA PESSOA, EM SEGUNDA PASSAGEM.
```

Onde A != A2 o item fica **em aberto**. Ninguém escolhe A, A2, maioria ou a
última resposta por conta própria.

## 55.5 · O TESTE QUE REFAZ A CONTA CONCORDA CONSIGO MESMO

Duas mutações sobreviveram à primeira suite: apagar `raise RevisaoInvalida`
para rótulo fora do vocabulário, e apagar o `raise` para evidência divergente.
Os testes continuaram verdes — porque **refaziam a conta dentro do próprio
teste** e comparavam com ela própria. Nunca chamavam `carregar_a()`.

```
REFAZER A LOGICA NO TESTE NAO E TESTAR A LOGICA:
E ESCREVE-LA DUAS VEZES E CONCORDAR CONSIGO.
```

Corrigido: os testes escrevem um ficheiro estragado, apontam `ENTRADA` para
ele, e exigem que a função levante. Com isso, 11 mutações, 0 sobreviventes.

## 55.6 · O NAVEGADOR APANHOU O QUE O TEXTO NÃO APANHA

Virar a página do contexto acendia o item na grelha e movia a barra de
progresso. O contador lia a **existência** da linha em `respostas` — que a
paginação também escreve, para não se perder onde a pessoa ia — em vez de ler
a **decisão**.

```
CONTAR A EXISTENCIA DA LINHA EM VEZ DA DECISAO
E UMA BARRA DE PROGRESSO QUE ANDA SOZINHA.
```

Nenhum teste de string apanharia isto. Apanhou-se num Chromium de verdade, e é
a segunda missão seguida em que o navegador encontra o que a leitura do HTML
não encontra.

---

# §56 · T3 PASSOU DE `D` A `B` — E O QUE O NÚMERO 36 ESCONDIA

**Missão:** `C-FECHA-GABARITO-T3-E-RECALCULA-CENSO-V1` · HEAD final `357697c1`
**Artefactos:** `provas/fechar_ground_truth_t3.py` ·
`data/samples/T3-GROUND-TRUTH-EVAL-V1.json` ·
`docs/operacao/CENSO-CORPUS-ROTULADO-ADMISSION-V1.md` §8

## 56.1 · O QUÊ

```
T3_OLD_VERDICT = D        T3_NEW_VERDICT = B
SANITY YES · EVALUATION YES · TRAINING NO
```

T3 tem agora gabarito humano independente. É a **primeira** origem de rótulo
desta árvore que não é herdada da ficha da fonte nem derivada das palavras que a
Admission usa hoje — e portanto a primeira que pode avaliar um substituto delas.

## 56.2 · POR QUÊ

Duas leituras da mesma pessoa, e um fecho que só produz rótulo onde as duas
concordam:

```
EVAL_ELIGIBLE   36     CONFIRMED_SIM 14 · CONFIRMED_NAO 22
UNRESOLVED      11     EVIDENCE_GAP 6 · AMBIGUOUS 0
```

Os 11 divergentes não viraram rótulo de lado nenhum, e os 6 buracos de evidência
não viraram negativo. Isso não é perda: é o dataset a dizer a verdade sobre si.

```
A != A2  ->  UNRESOLVED, E MAIS NADA.
EVIDENCIA_INSUFICIENTE != NAO
```

## 56.3 · O DEFEITO QUE O NÚMERO 36 ESCONDIA

Quatro dos 14 positivos são edições seguidas do mesmo boletim regional e
partilham a abertura quase inteira. Contados como quatro, o gabarito parecia ter
mais evidência do que tem.

```
QUATRO COPIAS DO MESMO BOLETIM NAO SAO QUATRO PROVAS.
```

A correcção **não** foi mexer no limiar — foi mudar o que conta como **um**:

```
36 ficheiros  ->  31 observações
14 positivos  ->  11 observações      (o critério pede 10)
```

A margem passou a ser de um. Um item que se descubra mal rotulado derruba o
veredicto, e isso está escrito no censo, no artefacto e no commit.

**A distinção que isto ensina:** baixar um limiar depois de ver a contagem é
desenhar o alvo à volta da flecha; corrigir a UNIDADE de contagem é medir a
coisa certa. A primeira muda a régua, a segunda muda o que se põe em cima dela.

## 56.4 · UMA SONDA QUE NÃO PODE FALHAR NÃO É UMA SONDA

O red team desta missão tinha dez sondas. **Três nasceram incapazes de ceder:**

- uma comparava o número de grupos consigo próprio;
- outra perguntava se um dicionário estava vazio;
- a terceira tinha um `or` que a fazia passar sempre.

As três reportavam `AGUENTA` sem terem olhado para nada.

```
UMA SONDA QUE NAO PODE FALHAR NAO ESTA A MEDIR NADA:
ESTA A DIZER QUE SIM.
```

A correcção foi dupla: reescrever a condição para apontar ao que interessa (o
veredicto assenta nos grupos? cada item está contado numa caixa de idioma? a
ressalva de escopo está escrita no texto?) e **acrescentar, para cada sonda, um
teste que a derruba**. Uma verificação sem prova de falsificabilidade é
decoração.

É a mesma família de defeito de §55.5 — o teste que refaz a conta e concorda
consigo — a aparecer numa camada acima: agora no verificador, não no teste.

## 56.5 · O IDIOMA NÃO ERA O QUE SE PRESUMIA

Três missões falaram de «corpus italiano» como facto assente. Ao medir:

```
resolvido como italiano   18 de 36
LANGUAGE não resolvido    17
em inglês                  1   (ISMEA)
COUNTRY = IT              36 de 36
```

O país é uniforme; o idioma nunca foi medido. Por isso o escopo afirma o que foi
visto e só isso:

```
EVALUATION_SCOPE = ITALIAN_AGRO_INSTITUTIONAL_CORPUS
```

Não autoriza afirmar França, Espanha nem EAME.

## 56.6 · CONSEQUÊNCIA

T3 pode finalmente participar de uma comparação entre mecanismos de
classificação — como **teste**, não como treino, e dentro do escopo declarado.
Continua sem chão para treinar: 100 por classe é o critério, e há 11 e 20.

O que o gabarito não resolve é a independência: quem ajustar um mecanismo
olhando para estes 36 deixa de poder avaliá-lo com eles.

```
UM CONJUNTO SO E INDEPENDENTE DE QUEM NAO OLHOU PARA ELE.
```

---

# §57 · A BASELINE DA ADMISSION EM T3 — E O ACERTO QUE VEIO DA SORTE

**Missão:** `C-MEDE-ADMISSION-ATUAL-CONTRA-GABARITO-T3-V1` · HEAD final `d43126e3`
**Artefactos:** `provas/medir_admission_t3_atual.py` ·
`data/derivados/BASELINE-ADMISSION-T3-V1.json` ·
`docs/operacao/BASELINE-ADMISSION-T3-V1.md`

## 57.1 · O QUÊ

Primeira medição do mecanismo temático de hoje contra rótulo humano
independente. Nada foi corrigido.

```
FIRST_VALID_BASELINE_FINGERPRINT
f24eceedd1235a1c1909a0d941aea4b87bdf8cba6547be762c5785e9ff635a85
```

## 57.2 · A PORTA NÃO CHEGA À PERGUNTA — E ISSO É METADE DO ACHADO

Com o item a levar só o que o próprio contrato declara:

```
DECISION_COVERAGE = 0.0      36 de 36 param na pergunta da ORIGEM
```

O registo de artefactos diz `SOURCE_ID = "NAO SEI"` nos 30 textos derivados, e
`coleta/ingresso.py` é explícito: *a confissão de ignorância não é um valor*.
Logo o item chega sem origem e a porta para antes do tema — como manda
`COL-LAW-042`.

```
MEDIR O MECANISMO TEMÁTICO E MEDIR A LINHAGEM
SÃO DUAS PERGUNTAS, E A PRIMEIRA NÃO CHEGA A SER FEITA.
```

Por isso a medição tem **dois planos de entrada**, com a regra de qual é a
baseline fixada antes de correr: `CONTRATO` (o que a produção vê) e `LINHAGEM`
(mais o `SOURCE_ID` que o gabarito já resolveu). A baseline temática é o
segundo — é o único que exercita a regra.

## 57.3 · A BASELINE TEMÁTICA

```
TP 2 · TN 4 · FP 5 · FN 0 · ABSTAIN 25 · NOT_APPLICABLE 0 · ERROR 0 = 36

DECISION_COVERAGE     0.3056
EFFECTIVE_ACCURACY    0.1667      CONDITIONAL_ACCURACY  0.5455
PRECISION 0.2857 · RECALL 1.0 · F1 0.4444
```

`RECALL = 1.0` parece perfeito e não é: a porta deu decisão binária a **dois**
dos 14 positivos humanos e absteve-se nos outros doze. **As duas acurácias
ficam sempre lado a lado** — uma taxa sem o seu denominador é propaganda.

Por observação independente (31 grupos, agrupamento vindo do gabarito e nunca
das previsões): `PASS 6 · FAIL 5 · NOT_DECIDED 20`.

## 57.4 · O BUG DO SUBSTRING NÃO SÓ SOBREVIVEU: ELE PRODUZ RESULTADO

```
SUBSTRING_FALSE_MATCH_STILL_EXISTS = YES
```

34 casamentos nos 36 documentos em que a palavra **nunca aparece sozinha** —
`lancio` dentro de `bilancio` nove vezes, `revista` dentro de `prevista` seis,
`sintoma` dentro de `sintomatologia` três.

E uma das quatro negativas correctas assenta **inteiramente** nisso:

```
RAW-445e41701f737d73.txt   humano T3_NAO · porta NAO · termo: ['lancio']
```

A porta disse «não é T3, fala de lançamento de produto». O documento fala de
**balanço fitossanitário**. Acertou pelo motivo errado.

```
UM ACERTO QUE VEM DE UM CASAMENTO FALSO
NÃO É O MECANISMO A FUNCIONAR: É A SORTE A ALINHAR-SE.
```

**Dos 6 acertos binários, 5 são do mecanismo e 1 é da sorte.** Medir acerto sem
medir *de onde ele veio* teria dado 6.

## 57.5 · O PADRÃO DOS CINCO FALSOS POSITIVOS

Todos têm vocabulário de praga denso no texto e todos são `NÃO` humano:
balanços anuais, boletins agrometeorológicos com secção fitossanitária,
directrizes de produção integrada.

```
MENCIONAR NÃO É TRATAR DE.
UMA LISTA DE PALAVRAS NÃO CONSEGUE VER A DIFERENÇA.
```

Isto liga-se a §50: a regra de T2 também não se deixou escrever como lista de
palavras. O mesmo limite, agora medido noutro universo e com rótulo humano.

## 57.6 · DUAS MUTAÇÕES QUE APANHARAM TESTES MEUS

- **Esconder os erros do relatório impresso** sobreviveu porque eu procurava o
  `ITEM_ID` no ecrã *inteiro* — e ele aparece também nas sondas de red team.
  Procurar no sítio errado e encontrar é pior do que não procurar.
- **Publicar só a acurácia condicional** sobreviveu porque eu exigia
  `EFFECTIVE <= CONDITIONAL`, e a mutação satisfazia a relação ao calcular as
  duas sobre o mesmo denominador.

```
UMA RELAÇÃO QUE A MUTAÇÃO TAMBÉM SATISFAZ
NÃO DISTINGUE O CERTO DO ERRADO.
```

A correcção foi exigir a **fórmula** (cada acurácia contra o seu denominador) e
olhar para a **secção** certa do relatório, não para a página.

## 57.7 · CONSEQUÊNCIA

Há baseline reprodutível para T3, com impressão digital e com a independência
histórica provada por datas do Git (o mecanismo não é tocado desde 09-09; o
gabarito só existe desde 09-11).

```
PERFORMANCE_GATE_PREDEFINED  = NO
CURRENT_MECHANISM_ACCEPTABLE = NOT_DECIDED
```

Não existe limiar canónico de aprovação para um mecanismo de classificação
nesta árvore. Sem gate prévio, medir não aprova nem reprova — e inventar o gate
depois de ver o resultado seria desenhar o alvo à volta da flecha.

---

# §58 · O GATE DE ACEITAÇÃO TEMÁTICA — O ALVO, DESENHADO ANTES DA FLECHA

**Missão:** `C-FECHA-GATE-ACEITACAO-TEMATICA-V1` · HEAD final `71de3214`
**Dono único:** `provas/gate_de_aceitacao_tematica.py` · decisão em `D-040`

## 58.1 · O QUÊ

O primeiro critério canónico de aceitação de um mecanismo temático da Admission.
Oito condições duras no plano da **observação independente**, mais um gate
separado de **alcance**, mais a regra de integração que exige os dois.

```
GATE_VERSION = V1
THIS_IS      = THEMATIC_MECHANISM_EVALUATION_GATE_V1
THIS_IS_NOT  = FULL_EAME_PRODUCTION_RELEASE_GATE
```

## 58.2 · POR QUÊ

A baseline de T3 (§57) mediu e não pôde concluir: `CURRENT_MECHANISM_ACCEPTABLE
= NOT_DECIDED`, porque não existia critério em lado nenhum.

```
SEM ALVO DESENHADO ANTES,
A FLECHA ATERRA SEMPRE NO CENTRO DE ALGUMA COISA.
```

E o inverso é a mesma fraude com o sinal trocado: escolher os números para o
mecanismo de hoje passar — ou falhar.

## 58.3 · O ESTUDO EXTERNO DEU UMA AUSÊNCIA, E ISSO É UM RESULTADO

```
THERE_IS_A_UNIVERSAL_CLASSIFIER_ACCEPTANCE_THRESHOLD = NO
```

Google Document AI, Azure Document Intelligence, scikit-learn e NIST AI RMF, nas
fontes oficiais: **quatro em quatro recusam-se a prescrever um número.** Todos
dizem, por palavras diferentes, que ele sai da função de custo de quem opera.

**Registou-se também onde NÃO convergem** — só a concordância seria consenso
fabricado:

- a Google **cala-se** sobre assimetria de custo, e o seu default de maximizar
  F1 assume que falso positivo e falso negativo custam o mesmo;
- a Azure é a única que nomeia um número (80%) e nomeia-o contra uma estimativa
  de **treino**, não holdout — o tipo de número de que as outras avisam;
- o NIST está noutra altitude: manda **documentar** a tolerância, não diz qual é,
  e avisa que o problema de medição está por resolver.

```
CONVERGÊNCIA FABRICADA É PIOR DO QUE DISCORDÂNCIA REGISTADA.
```

## 58.4 · A ASSIMETRIA QUE PRODUZ TODOS OS NÚMEROS

```
FALSE_NEGATIVE_COST > FALSE_POSITIVE_COST
```

Um falso positivo custa **trabalho** e fica visível: a Inteligência ainda julga.
Um falso negativo custa **conhecimento**, e em silêncio — ninguém volta a olhar.

Daí a ordem de dureza: falso negativo explícito com zero tolerância, captura de
positivos quase total, precisão exigente mas não absoluta. E daí `ABSTAIN` ser
preferível a um `NÃO` errado — **mas abster-se sempre também reprova**, e por
isso há limiar de cobertura.

## 58.5 · A REGRA ESTRUTURAL QUE SOBREVIVE A ESTE GATE

Duas coisas ficam, independentemente dos números escolhidos:

**Um gate que se compensa é uma média com nome de regra.** Nenhuma condição
compensa outra. Precisão excelente não compensa captura positiva ruim.

**A acurácia condicional não aprova.** Ela mede só os casos em que o mecanismo
se atreveu — é assim que um mecanismo fraco parece forte.

E a unidade: `DOCUMENT != INDEPENDENT_OBSERVATION`. Pontuar por ficheiro dá
quatro créditos por resolver um boletim que aparece em quatro edições.

## 58.6 · O RESULTADO, APLICADO MECANICAMENTE

```
CURRENT_ADMISSION_GATE_RESULT = FAIL
```

O mecanismo de hoje cumpre **duas das oito**: não comete falso negativo
explícito e não rebenta. Falha as outras seis, e falha o alcance (15/36).

Nada foi consertado. `ADMISSION_CHANGED = NO`, zero linhas de runtime.

## 58.7 · ONDE A LEI FICOU, E POR QUÊ NÃO NA BÍBLIA

```
BIBLE_CHANGE_REQUIRED    = NO
CONTRACT_CHANGE_REQUIRED = YES
```

A Bíblia é a constituição da **coleta**. Este gate legisla sobre a **qualidade de
um mecanismo de decisão** — outro conceito. `COL-LAW-042` já governa a *forma* de
uma decisão da Admissão; enxertar-lhe um limiar de qualidade daria dois donos ao
mesmo assunto. É o mesmo raciocínio da `D-039`, e a mesma conclusão.

Os números vivem no código e só lá; o documento explica e cita, e **um teste
prova que os dois dizem a mesma coisa**.

## 58.8 · DOIS DEFEITOS DE PROCESSO APANHADOS AQUI

**Um marcador que não distingue a definição do valor reprova o texto que explica
a regra.** Um teste meu procurava a string `THEMATIC_GATE_PASS` dentro do
contrato para provar que ele não carregava veredicto — e acendia na frase que
*define* a regra de integração. Passou a varrer a **estrutura**: nenhuma chave de
aplicação, nenhum booleano de PASS, nenhum número do baseline. É a terceira vez
nesta sessão que um marcador de string reprova código certo.

**Correr o passo que lê e não o que escreve é regenerar nada, com mensagem de
sucesso.** `P1_SEM_DRIFT` reprovou com o SHA de um ficheiro desatualizado. A
causa não era o gerador: `generate_system_map.py` **lê**
`architecture.generated.json`, e quem o **escreve** é `scan_repo.py`. Correr só o
gerador deixava o censo do repositório parado no commit anterior — e ele repetia
o HEAD antigo sem se queixar.

    A CADEIA CANÓNICA DO MAPA COMEÇA EM `scan_repo.py`.
    O GERADOR SOZINHO CONFIRMA O PASSADO E CHAMA-LHE OK.

## 58.9 · A SEGUNDA PASSAGEM: MEDIR A SUITE, E IR VER A FONTE

A missão foi corrida outra vez. **Nenhum limiar mudou** — e essa é a primeira
coisa a registar, porque uma segunda passagem que mexe nos números depois de já
ter visto o resultado é exactamente a fraude que o gate existe para impedir.
Fecharam-se duas coisas que faltavam à *prova* dele.

**Uma suite verde não prova que ela morde.** Prova que, com o código como está,
nada rebentou. São coisas diferentes, e a diferença só aparece quando se mexe no
código de propósito. `provas/mutacao_do_gate.py` altera o ficheiro do dono — um
limiar de cada vez — corre a suite real e exige que ela reprove.

```
MUTANTES  13
SURVIVORS 0
```

O risco concreto deste gate nunca foi um bug: é alguém mexer num número depois
de ver um resultado de que não gostou.

```
UMA SUITE QUE NÃO REPROVA UM LIMIAR ALTERADO
NÃO ESTÁ A GUARDAR LIMIAR NENHUM.
```

**A armadilha da prova de mutação, e ela morde na primeira tentativa.** Os
testes que guardam a própria mutação (âncora única, ficheiro por mutar) falham
enquanto a árvore *está* mutada — e matariam todos os mutantes por
contabilidade, dando `SURVIVORS = 0` sem provar nada sobre o gate. Ficam
marcados com `SINTONIA_MUTACAO_EM_CURSO`: defendem a árvore commitada, não a
árvore sob mutação.

```
UM MUTANTE QUE NÃO SE APLICA
É INDISTINGUÍVEL DE UM MUTANTE QUE MORREU.
```

**A afirmação estava certa e a fonte apontava ao lado.** O único número que o
estudo externo inteiro encontrou — o *«It's best to target a score of 80% or
higher»* da Azure — não vive na *transparency note* nem na página de threshold,
que eram as duas citadas. Vive na `accuracy-confidence`, que também diz contra o
que ele é medido: *«running a few different combinations of the training data»*
— treino, não holdout. A leitura estava certa; só não havia como ir confirmá-la.

```
UMA CITAÇÃO QUE NÃO SE CONFIRMA
VALE O MESMO QUE NENHUMA.
```

E as quatro fontes foram relidas de origem nesta passagem: `NO` continua `NO`.

**A cadeia do mapa tem sete passos, e o §58.8 parou no primeiro.** A lição
anterior estava certa e incompleta: `generate_system_map.py` corre sozinho
`scan_repo.py` e `scan_sources.py`, mas a lista canónica em
`system-map/scripts/CADEIA-DO-MAPA.json` tem **sete**. Correr só o gerador
deixou três censos com o `HEAD` de um ramo anterior. A lista existe para não
haver duas cadeias — e quem não a lê inventa a sua.

    A CADEIA NÃO É O QUE O GERADOR CHAMA. É O QUE `CADEIA-DO-MAPA.json` LISTA.

**Ficheiro novo é invisível ao mapa até ser rastreado pelo git.** O censo lista
com `git ls-files`; um `provas/` novo e por adicionar não existe para ele, e
`P9_CODIGO_DECLARADO` só o vê depois do `git add` — e depois exige a declaração
em `architecture.declared.json`. São dois passos, e nesta ordem.

---

# §59 · A CORRIDA CEGA DEU `NONE` — E O ACHADO ESTAVA NOUTRO SÍTIO

**Missão:** `C-DEFINE-CANDIDATOS-TEMATICOS-V1` + janela autónoma
**HEAD final:** `102c171a`
**Donos novos:** `provas/candidatos_tematicos.py` · `provas/implementacoes_candidatas.py` · `provas/benchmark_tematico.py` · `provas/alcance_da_pergunta_tematica.py`

## 59.1 · O QUÊ

Quatro mecanismos candidatos definidos e congelados **antes** de verem o corpus,
implementados, submetidos a mutação, e corridos **uma vez** contra o gabarito de
T3 com o portão do §58 intacto.

```
WINNER  = NONE
BLOCKED = C3-LLM-STRUCTURED
EVALUATION_EXPOSED = YES
ADMISSION_CHANGED  = NO
```

## 59.2 · `NONE` É UM RESULTADO

O portão não tem segundo lugar. Nenhum dos quatro resolve T3, e a baseline
também não. A tentação de escrever «o melhor dos que correram» existe e é
exactamente o que o gate foi congelado para impedir.

```
«QUASE PASSOU» NÃO É UM ESTADO.
```

## 59.3 · O ACHADO QUE VALE MAIS DO QUE O VEREDITO

Cinco missões a afinar a pergunta temática, e a medição de alcance diz:

```
plano CONTRATO (o que a produção vê hoje) ...  0 de 36
plano LINHAGEM (com o SOURCE_ID já escrito) .. 15 de 36
```

    UM CLASSIFICADOR PERFEITO NUMA PERGUNTA QUE NINGUÉM FAZ
    MELHORA EXACTAMENTE ZERO DOCUMENTOS.

Trocar hoje o mecanismo temático mudaria a resposta de **nenhum** documento em
produção. O gargalo é identidade, não conteúdo — e nenhuma das cinco missões
anteriores o teria visto, porque todas mediam o classificador.

As classes de paragem nasceram da medição, não de uma taxonomia escrita antes:
vinte documentos param porque o registo confessa `NÃO SEI` e a linhagem **sabe**
(encanamento perdido), dezasseis porque ninguém sabe (fonte por descobrir), e
cinco porque não declaram o que são e apanham a régua antiga.

    NÃO_SEI DE TEMA E NÃO_SEI DE PRONTIDÃO SÃO A MESMA PALAVRA
    E NÃO SÃO A MESMA COISA.

## 59.4 · TRÊS HIPÓTESES A ERRAR NO MESMO LADO

Negativos certos, de 20 grupos: baseline 4, C1 3, C2 zero, C4 zero. Inventários
diferentes, o mesmo lado a falhar.

    TRÊS HIPÓTESES A ERRAR NO MESMO LADO
    NÃO SÃO TRÊS ERROS: SÃO UMA PERGUNTA MAL FEITA.

## 59.5 · QUATRO DEFEITOS QUE SÓ A MEDIÇÃO APANHOU

**Um número escrito à mão não é uma medição.** `FALSE_SUBSTRING_OUTCOME_DEPENDENCY`
estava fixado em `0` com a justificação — verdadeira — de que C1 e C2 casam por
palavra inteira por construção. A constante passava pelo mesmo caminho para a
baseline, que tem o defeito vivo.

    UM NÚMERO QUE NÃO OLHOU PARA O DOCUMENTO
    NÃO É UMA MEDIÇÃO: É UMA OPINIÃO COM CARA DE MÉTRICA.

**Apresentar a prova proibida ao lado da permitida não testa qual foi usada.**
O teste de «nenhum candidato lê o caminho» punha os conceitos no texto **e** no
caminho. Uma mutação que fazia C2 concatenar `BODY_PATH` sobreviveu à suíte
inteira. Agora o texto é neutro e os conceitos vivem só nos metadados.

**Um limiar só está testado se algum caso cair exactamente por baixo dele.**
Baixar o limiar de conceitos de 2 para 1 sobreviveu porque todos os sintéticos
tinham zero conceitos ou dois. Nenhum caía no meio, que é o único sítio onde um
limiar decide.

**Dois caminhos que dão a mesma resposta em todos os exemplos são um caminho
testado e outro por testar.** Desligar a exigência de contiguidade do índice
sobreviveu porque o ramo do género dispara sozinho a partir de seis letras, e
todos os sintéticos usavam géneros longos. `aphis` tem cinco.

## 59.6 · UM GATE APLICADO A UMA CORRIDA QUE NÃO ACONTECEU

C3 não corre sem credencial: devolve 36 `ERRO`, e o portão calculava
obedientemente «6 de 8 condições em falha». A tabela ficava com `BLOCKED` e seis
reprovações na mesma linha.

    GUARDAR O NÚMERO AO LADO DA PALAVRA «BLOCKED»
    E DEIXAR A PALAVRA PARA QUEM LER O RODAPÉ.

Aquele seis media a falta da chave, não a hipótese. O defeito apareceu ao
**escrever o relato** — passar números para uma tabela é um teste que o código
não faz.

## 59.7 · A CADEIA DO MAPA, OUTRA VEZ

O §58.9 já dizia que a cadeia tem sete passos. Corri dois. Os outros cinco
censos ficaram com o `HEAD` de um commit anterior e ninguém reclamou, porque
cada script corre sem erro sozinho.

    A CADEIA NÃO É O QUE EU ME LEMBRO DELA. É O QUE `CADEIA-DO-MAPA.json` LISTA.

E o gerador rebentava com `IndexError` numa string feita só de espaços —
`w.split()[0]` numa lista vazia. O gatilho foi um fixture de teste com
`"   \n\t  "`; o defeito esperava por ele desde sempre.

    UMA STRING VAZIA NÃO É UMA PALAVRA CURTA:
    É A AUSÊNCIA DE PALAVRA, E PARTE-SE NOUTRO SÍTIO.

## 59.8 · O QUE NÃO MUDOU

```
ADMISSION_CHANGED          = NO
GATE_THRESHOLD_CHANGED     = NO
GROUND_TRUTH_CHANGED       = NO
TRAINING_ON_EVALUATION_SET = NO
INTEGRAÇÃO                 = NOT_READY
NEW_FAILURES               = 0   (2334 testes, 93 módulos)
```

`CLASSIFIER_BAD + LINEAGE_BROKEN`: consertar só um dos dois lados não entrega
documento nenhum.

---

# §60 · O `SOURCE_ID` PERDE-SE EM DOIS SÍTIOS, E NENHUM É A ADMISSION

**Missão:** `C-MEASURE-SOURCE-ID-WIRING-GAP-V1`
**HEAD final:** `3ca38679`
**Dono novo:** `provas/medir_source_id_wiring_gap.py`

## 60.1 · O QUÊ

Os 20 documentos de T3 em que a linhagem aparentava saber a origem e a Admission
recebeu `NÃO SEI`, seguidos aresta a aresta desde a primeira evidência até à porta.

```
ONE_SINGLE_ROOT_CAUSE = NO

OUT_OF_FLOW_EVIDENCE   13
READER_GAP              7
```

## 60.2 · POR QUÊ — «A LINHAGEM SABE» ERA GENEROSO DEMAIS

O rótulo saiu do `§59`, escrito por mim. Fui ver de onde vinha o valor:

```
provas/censo_corpus_rotulado_admission.py::fonte_de
re.search(r"(IT-T\d+-\d+)") sobre o CAMINHO do item e dos pais
```

Uma expressão regular sobre um nome de directório. A lei desta casa diz
`SOURCE_ID != path`, e eu tinha contado isso como linhagem a saber.

    UMA CONVENÇÃO DE CAMINHO NÃO É UM CAMPO.
    ELA NÃO VIAJA, NÃO TEM DONO, E NINGUÉM A DECLAROU.

**A convenção não está errada — está ingovernada.** Nos 7 casos em que existe
também um campo real, os dois valores batem exactamente. É por isso que ela
enganou: ela acerta.

## 60.3 · PROVA — AS DUAS CAUSAS

**`READER_GAP`, 7 casos.** O valor existe como campo em
`data/collection-ledger/italy/observations.ndjson`, ao lado do caminho e do SHA
do bruto. Quem refaz o bruto não o lê:

```
coleta/executor_texto_de_pdf.py
    pai = art.raw_do_disco(str(pdf), str(RAIZ), COUNTRY_SCOPE="IT")
```

`raw_do_disco` recusa-se, por lei escrita, a deduzir seja o que for do nome do
ficheiro, e **essa recusa está certa**. Falta alguém passar-lhe a fonte.

    NÃO FOI APAGADO. NUNCA FOI CONSULTADO.

**`OUT_OF_FLOW_EVIDENCE`, 13 casos.** Corpos em
`data/samples/IT-SOURCE-SAMPLES/<SOURCE_ID>/` sem observação de coleta nenhuma.
Não passaram pelo pipeline: foram postos como amostra. Aqui não há aresta
perdida, porque nunca houve campo para atravessar.

## 60.4 · QUATRO DOS CINCO ESTÁGIOS ESTAVAM CERTOS

A Admission **lê** `source_id`. O ingresso **traduz** o nome. A derivação
**copia** do pai: `derivado_de` faz `SOURCE_ID=pai.SOURCE_ID`, e copia
fielmente um valor que já chega vazio.

    O LEITOR NUNCA FOI O DEFEITO.

Duas missões estiveram a olhar para o lado errado da cadeia.

## 60.5 · `SCHEMA EXISTS != WRITER USES IT`

A migration `026` declara `raw_asset.source_id` e os checks recusam `NAO SEI`
no estado identificado. `CAN_STORE = YES`. E o registo de artefactos tem 43
`DERIVED`, **zero `RAW`**, e zero `SOURCE_ID` provado. `WRITER_WRITES = NO`.

O banco poder guardar não é ninguém escrever.

## 60.6 · DOIS DEFEITOS MEUS QUE A MEDIÇÃO APANHOU

**Um grep que não distingue código de comentário.** Perguntei
`"collection-ledger" in fonte` para saber se o executor lia o recibo. Resposta:
sim — por causa de um comentário que explica que ele **não** lê. O relatório
saiu a dizer que o forward não tinha o buraco.

    UM GREP QUE NÃO DISTINGUE CÓDIGO DE COMENTÁRIO
    DEIXA O TEXTO QUE EXPLICA O DEFEITO PROVAR QUE ELE NÃO EXISTE.

Corrigido com uma verificação estrutural por `ast`: há alguma string literal,
fora de comentário, que nomeie o recibo?

**Um teste que lê o resultado guardado.** A suíte carregava
`SOURCE-ID-WIRING-GAP-V1.json` do disco quando ele existia. Seis mutações da
lógica de medição sobreviveram à suíte inteira: os testes liam o artefacto
congelado de uma corrida anterior e nunca tocavam no código mutado.

    UM TESTE QUE LÊ O RESULTADO GUARDADO
    TESTA O FICHEIRO, E NÃO A FUNÇÃO QUE O ESCREVEU.

O artefacto no disco é a entrega. A suíte tem de exercitar o código. Depois da
correcção: 11 mutantes, 0 sobreviventes.

## 60.7 · CONSEQUÊNCIA

O defeito tem **dois donos diferentes**, e uma correcção só serve metade:

| causa | quem conserta | o que é |
|---|---|---|
| `READER_GAP` | `coleta/executor_texto_de_pdf.py` | passar ao bruto a fonte que o recibo já tem |
| `OUT_OF_FLOW_EVIDENCE` | decisão de contrato, não de código | o que fazer com corpos que entraram por fora do pipeline |

`FORWARD_CODE_HAS_SAME_GAP = YES`. `FORWARD_GAP_EXECUTED_AND_PROVEN = UNKNOWN`:
não houve corrida forward, e previsão não é medição.

Nada foi consertado. `MEASURE != FIX`.

---

# §61 · A FONTE ATRAVESSA — E TRÊS MUTANTES QUE ENSINARAM A TESTAR

**Missão:** `C-FIX-SOURCE-ID-READER-GAP-V1`
**HEAD final:** `95b72b86`
**Tocado:** `coleta/italy_executor.py` · `coleta/executor_texto_de_pdf.py`

## 61.1 · O QUÊ

O `READER_GAP` dos 7, medido no `§60`, está fechado no forward. Os 13
`OUT_OF_FLOW` continuam intocados.

```
FORWARD_EXECUTED    = YES
SOURCE_ID_PRESERVED = YES
```

## 61.2 · POR QUÊ — A CORREÇÃO FOI PARA O DONO

O recibo da coleta já tinha dono: `coleta/italy_executor.py` escreve-o e lê-o
por corrida. A pergunta nova vive lá. Não há segundo livro, não há índice
paralelo de identidade, e `raw_do_disco` **não mudou uma linha** — a lei que o
proíbe de adivinhar pelo nome continua de pé.

    O DEFEITO NÃO ERA UMA LEI ERRADA.
    ERA UMA PERGUNTA QUE NINGUÉM FAZIA.

## 61.3 · PROVA — A CHAVE É O CONTEÚDO, E ISSO FOI MEDIDO

```
RAW_SHA256 presente .... 144 de 144
RAW_PATH presente ......  35 de 144
e um dos RAW_PATH é `C:/ea...`, absoluto e de outra máquina
```

Juntar por caminho responderia «não sei» a três quartos do livro.

    O SHA É A CHAVE QUE ACHA A LINHA.
    A FONTE VEM DO CAMPO QUE O COLETOR ESCREVEU NELA.

**O caminho não ganhou voto.** O brief admitia detectar conflito entre caminho
e livro. Não foi implementado na coleta, de propósito: para discordar do
caminho é preciso lê-lo, e ler o caminho para extrair identidade é o padrão
proibido. Não há desempate porque não há empate.

## 61.4 · TRÊS MUTANTES, TRÊS LIÇÕES DE COMO TESTAR

**O arnês de mutação mentia.** Um mutante compila o `.pyc`; a restauração
devolve o `.py`; o interpretador seguinte serve o bytecode do mutante. Medido:
a suíte «restaurada» falhou 4 testes com os ficheiros já corrigidos.

    UM ARNÊS DE MUTAÇÃO COM CACHE
    MEDE O QUE ESTEVE LÁ, E NÃO O QUE ESTÁ.

**Código sem costura não se testa.** Duas mutações sobreviveram — «não passar a
fonte ao bruto» e «passar o PAÍS em vez da fonte» — porque a ligação vivia
solta dentro do ciclo, e a única porta de entrada era uma corrida completa do
executor.

    CÓDIGO SEM COSTURA NÃO É CÓDIGO SIMPLES:
    É CÓDIGO QUE SÓ SE PODE TESTAR POR INTEIRO, OU NÃO SE TESTA.

Extraídas `fonte_para_o_bruto` e `registar_achado`, os dois mutantes morreram.

**Um ramo sem dados reais fica por testar.** A contagem do conflito sobreviveu
porque o corpus de hoje tem **zero** conteúdos com duas fontes.

    UM RAMO QUE SÓ OS DADOS DE AMANHÃ EXERCITAM
    FICA POR TESTAR ATÉ AMANHÃ — E AÍ É TARDE.

13 mutantes, 0 sobreviventes.

## 61.5 · E UM DEFEITO DA PRÓPRIA PROVA

A prova forward entregava à porta apenas `DO_COLETOR`, deixando de fora
`DA_FICHA_PARA_A_PORTA`, onde vive `ARTIFACT_TYPE`. Sem ele a porta cai em
`ESTAGIO_DESCONHECIDO` e pergunta o tempo de um facto que ainda não foi
extraído — uma régua que a produção não usa ali.

    UMA PROVA QUE ENTREGA MENOS DO QUE A PRODUÇÃO ENTREGA
    MEDE UM CAMINHO QUE NINGUÉM PERCORRE.

Corrigida, os positivos chegam a `pertence ao universo`.

## 61.6 · CONSEQUÊNCIA

No corpus de hoje, 12 dos 49 PDF italianos passam a nascer com fonte provada.
Os outros 37 continuam `NÃO SEI`, e é o que se espera: entraram por fora do
pipeline, e `COL-LAW-045` diz que coleta manual também entra pelo contrato.

O executor passou a contar as três respostas do livro no recibo.

    UMA CONSULTA QUE NINGUÉM CONTA
    É INDISTINGUÍVEL DE UMA CONSULTA QUE NÃO ACONTECE.

Sem backfill, sem migration, sem identidade inventada. `admissao.py`,
`ingresso.py` e `leis/artefato.py` com zero linhas de diff.

---

# §62 · APOSENTAR NÃO É BLOQUEAR — E TRÊS SONDAS QUE MEDIRAM A SI PRÓPRIAS

**Missão:** `C10.4C — RETIRE LEGACY INSTAGRAM TRANSCRIPTION`
**HEAD final:** `5292be8a`
**Tocado:** `ferramentas/instagram_transcrever.py` · `.github/workflows/sintonia-scrap.yml` ·
`coleta/social_scrap.py` · `system-map/scripts/censo_das_derivacoes.py` ·
`system-map/scripts/censo_da_coleta.py`

## 62.1 · O QUÊ

A C10.4B mediu duas implementações vivas de «obter a fala de um Reel» e travou a
velha pela política. A C10.4C fechou-a.

```
OPERATIONAL_DOORS_BEFORE = 6
OPERATIONAL_DOORS_AFTER  = 0
TRANSCRIPTION_OWNERS     = 1
POLICY_CHANGED           = NO
```

O `§`61 e os anteriores já tinham registado que workflows são portas e que uma
decisão só vale onde é consultada. Isto é a consequência disso, executada. O que
segue **não** é: são quatro coisas que nasceram aqui.

## 62.2 · A SEXTA PORTA ERA UM `print()`

A C10.4B contou cinco portas. Havia seis. A sexta não era `import`, nem
`workflow_dispatch`, nem `__main__`:

```python
# coleta/social_scrap.py, no raio-x de transcrição
print('    2. faster-whisper local   → scripts/instagram_transcrever.py, ...')
```

Um programa que **imprime** a um operador qual comando correr é uma porta, e o
operador é o transporte. O caminho impresso nem existia — `scripts/` virou
`ferramentas/` há muito. Uma instrução operacional errada continua a ser uma
instrução.

    DOCUMENTAÇÃO OPERACIONAL USADA COMO COMANDO É UMA PORTA.
    E QUEM A IMPRIME É O DONO DELA.

Corolário apanhado no fim da mesma missão, contra o **próprio documento de
entrega**: a secção que demonstrava a recusa do CLI escrevia-a em forma de
`$ py …`. O ataque 9 da missão marcou-a. Que o comando só produza recusa não
muda a forma.

    UMA DEMONSTRAÇÃO EM FORMA DE INSTRUÇÃO É UMA INSTRUÇÃO.

## 62.3 · O QUE SAI DE UM APOSENTADO, ALÉM DAS PORTAS

Fechar as portas não bastou. O ficheiro continuava a **parecer** um dono do
conceito para todos os censos da casa, por três coisas que não eram portas:

| saiu | porquê |
|---|---|
| `import fala_local` | um aposentado que carrega o reconhecedor é contado como transcritor por qualquer varredura de donos |
| `politica_da_aquisicao` | quem não adquire não precisa de autorização para adquirir |
| o docstring operacional | as três primeiras linhas eram comandos para copiar |

A segunda é a menos óbvia e a mais útil:

    UM PORTÃO À FRENTE DE UMA FUNÇÃO QUE LEVANTA É CERIMÔNIA.
    E CERIMÔNIA PARECE CAPACIDADE.

O que **fica** é a medição: o benchmark de velocidade de modelo que aquele
ficheiro cronometrou está citado em seis documentos e em dois módulos vivos.
Apagar o ficheiro apagaria a proveniência desses números.

    APOSENTAR A ROTA NÃO PEDE APAGAR A PROVENIÊNCIA.
    PEDE QUE ELA DEIXE DE SER UMA PORTA.

E a fila que a rota velha usava (`alvos`) saiu com ela, com os critérios escritos
no documento da missão — porque um deles, exigir `VIDEO_URL_TEMPORARY`, nem faz
sentido para uma rota audio-only. Selecionar alvos **para** uma aquisição é parte
dessa aquisição, não capacidade à parte.

## 62.4 · O CENSO DO MAPA CONTAVA PROSA COMO ARESTA

Regenerada a cadeia dos sete passos, o mapa declarou que o módulo **aposentado**
chamava três módulos vivos, e que dois deles corriam no CI. O módulo importa
`sys` e mais nada.

A fonte de todas essas arestas era o docstring que explica a aposentadoria e o
comentário do workflow que a anuncia. `system-map/scripts/censo_da_coleta.py`
media com `if outro in texto` — o texto inteiro.

    UM NOME DENTRO DE UMA FRASE NÃO É UM ARGV.

A casa já tinha esta lei para os **testes** (`UMA SENTINELA ANCORADA NO TEXTO
MEDE O TEXTO, NÃO A LEI`). O que é novo é que ela vale para o **mapa** — e que
lá a correção não pode ser deitar a citação fora, porque uma citação *é* uma
porta (62.2). A resposta foi nomear as duas:

```
chamado_por   import na árvore, OU caminho numa linha executável,
              E só se o ficheiro chegar a lançar processo
citado_por    o caminho aparece, mas em prosa — não é aresta, e fica registado
no_ci         caminho numa linha NÃO-comentário de um workflow
```

O terceiro critério do `chamado_por` é o que resolve o caso geral:

    UM FICHEIRO QUE NUNCA LANÇA PROCESSO NÃO ESTÁ A CORRER OUTRO
    PELO CAMINHO, POR MAIS VEZES QUE O NOMEIE.

`orfaos` manteve o significado antigo (ninguém o chama, ninguém o corre, ninguém
o nomeia) porque `citado_por` entra na conta. Ao lado nasceu o número mais
apertado, `sem_aresta_medida`. **Afinar uma medição não é mudar o que ela
contava** — se muda, são duas medições e cada uma precisa do seu nome.

## 62.5 · A SENTINELA QUE MEDE UM MUNDO QUE ACABOU

Seis testes da C10.4B caíram com esta missão. Nenhum estava errado: mediam a
porta **aberta** — exigiam a fase no workflow, o portão de política na rota
velha, cobertura das suas saídas de rede. Um deles dizia-o no corpo: apagar a
entrada operacional é decisão de gente, e o que o teste exige é que ela não mude
em silêncio.

A C10.4C é essa decisão. A sentinela disparou a fazer o seu trabalho.

    UMA SENTINELA QUE CONTINUA A MEDIR UM MUNDO QUE ACABOU MEDE O PASSADO.

Nenhuma foi apagada. Cada uma passou a medir que a porta **não voltou**, e o que
media antes ficou escrito no seu próprio docstring. A de «cada saída de rede tem
portão» virou a afirmação mais forte — **zero** saídas de rede — e ganhou
controlo positivo sobre o dono canônico, onde a sonda *tem* de encontrar saída.

    APAGAR UMA SENTINELA QUE DISPAROU É APAGAR A MEDIÇÃO.
    MIGRÁ-LA É GUARDAR A LEI E TROCAR O MUNDO.

## 62.6 · TRÊS ATAQUES QUE FALHARAM CONTRA A PRÓPRIA SONDA

Dos vinte ataques do red team, três deram positivo e nenhum era a casa:

| ataque | o que a sonda mediu | o que devia medir |
|---|---|---|
| `subprocess` | *nomes* do módulo em literais — achou a mensagem de recusa do próprio aposentado e o rótulo da rota na matriz | o literal **dentro** de uma chamada de subprocesso |
| mapa esconde edge | o *texto* do censo — achou o comentário que explica a troca do PRODUTOR | as declarações |
| código renomeado | qualquer ficheiro com `-vn` — achou o dono do ASR, que converte um ficheiro **já em disco** | trazer da rede **e** cortar, as duas metades |

E a correção do terceiro trouxe o mesmo defeito outra vez: o filtro de rede
aceitava `dict.get` e declarou que 171 ficheiros traziam mídia. O número era da
sonda.

    UMA SONDA QUE CONTA NOMES CONTA NOMES, NÃO CHAMADAS.
    E UMA CORREÇÃO DE SONDA PRECISA DO MESMO CONTROLO POSITIVO
    QUE A SONDA ORIGINAL NÃO TEVE.

Por isso cada ataque passou a imprimir **o que mediu**, e não só o que não
encontrou: «104 chamadas de subprocesso inspecionadas», «7 PRODUTORES
declarados», «21 ficheiros trazem mídia da rede». Um zero sem denominador não é
um resultado.

## 62.7 · CONSEQUÊNCIA

`ONE CONCEPT → ONE OWNER` satisfeito para transcrição de Reel. `ASR_OWNERS = 1`.
`MUTATION_SURVIVORS = 0` em seis mutações, `RED_TEAM_RESULT = PASS` em vinte
ataques, `NEW_FAILURES = 0` em 2321 testes, `SYSTEM_MAP_CHECK = PASS` com os sete
passos da cadeia.

A política **não** foi tocada: `INSTAGRAM/FETCH_TRANSCRIPT` continua
`ROUTE_NOT_ALLOWED` pela decisão da C10.5D. Fica uma dívida declarada — a matriz
ainda chama a rota `instagram_transcrever.py:faster-whisper`. O rótulo está
velho; a decisão não. Mexer na matriz é missão da matriz.

    O NOME DE UMA ROTA NA MATRIZ NÃO É A ROTA.
    MAS UM NOME VELHO NUM DONO DE DECISÃO É DÍVIDA, NÃO DETALHE.

---

# §63 · OS TREZE FICAM: PRESERVADOS, E FORA DA COLLECTION

**Missão:** `C-DECIDE-OUT-OF-FLOW-LEGACY-DECISION-V1`
**HEAD final:** `465e318a`
**Dono novo:** `provas/o_legado_fora_do_fluxo.py`

## 63.1 · O QUÊ

```
LEGACY_KEEP_OUT_OF_FLOW = 13
```

Os treze corpos históricos de T3 que têm bytes e não têm observação de coleta
ficam preservados como evidência e fora da Collection operacional.

    PRESERVAR NÃO É ADMITIR.
    São duas perguntas, e nenhuma disposição manda apagar corpo nenhum.

## 63.2 · POR QUÊ — A DISTINÇÃO QUE DECIDIU TUDO

```
CONTENT_PROVES_PUBLISHER != ACQUISITION_PROVENANCE_PROVEN
```

**Sete dos treze** dizem quem os publicou, dentro do próprio texto. **Nenhum**
diz que esta cópia foi adquirida dali, por quem, quando ou como.

É por aqui que um sistema honesto se perde: a evidência de publicação é forte,
está no documento, e não é a evidência que falta.

## 63.3 · PROVA — E NÃO FOI POR FALTA DE ALTERNATIVA

| alternativa | por que não |
|---|---|
| `CANONICAL_EQUIVALENT_ALREADY_EXISTS` | 0 de 13 têm bytes iguais a uma observação canónica |
| `RECOLLECT_FROM_SOURCE` | exigiria o endereço **deste** documento, que viveria na observação que falta |
| `LEGACY_IMPORT_WITH_CURRENT_PROVENANCE` | o contrato não separa a proveniência da importação atual da aquisição histórica |
| `UNRESOLVED` | os corpos existem e a evidência chega para classificar |

A sonda externa tocou o sítio de cada fonte: quatro respondem, cinco não.
Isso mede a instituição, não o ficheiro.

    SABER ONDE FICA A BIBLIOTECA
    NÃO É SABER QUE LIVRO SE FOI LÁ BUSCAR.

## 63.4 · O ESTUDO EXTERNO — TRÊS FAMÍLIAS

| sistema | achado |
|---|---|
| W3C PROV-DM | uma entidade pode ser afirmada **sem** `wasGeneratedBy`; a atribuição aplica-se «quando a actividade não é conhecida» |
| Archivematica | material transferido fica em **backlog**: guardado, avaliável, e explicitamente ainda não um AIP |
| Apache Beam | sem tempo do evento atribui-se um **sentinela**, nunca um valor inventado |

**Convergem** em preservar o corpo, registar o evento de custódia actual, e
nunca fabricar a aquisição original.

**Divergem** no resto, e a divergência é a parte útil: o arquivo **admite** o
objecto porque a função dele é a custódia; o sistema de dados **mantém-no
fora** da semântica operacional porque as contas a jusante dependem da
proveniência.

A Collection não é um arquivo de custódia. Por isso vale a postura dos dois
lados: guardar como o arquivo guarda, e manter fora como o sistema de dados
mantém.

## 63.5 · CONSEQUÊNCIA — UMA PERGUNTA SEM DONO

```
EXISTING_CONTRACT_SUFFICIENT = PARTIAL
BIBLE_CHANGE_REQUIRED        = NO
CONTRACT_CHANGE_REQUIRED     = YES
```

Qual é o estado canónico de um **corpo que existe** e cuja **aquisição nunca
foi registada**? `raw_asset.identity_state` tem três estados e os **três**
pressupõem uma linha em `raw_asset`. `LEGACY_PRE_IDEMPOTENCY` é para
observações que já lá estavam no corte; estes treze não estão no corte, estão
antes da porta.

    UM ESTADO PARA LINHAS NÃO CLASSIFICA QUEM NÃO TEM LINHA.

**A Bíblia não muda.** Nenhuma lei existente está errada. `COL-LAW-045` obriga
a coleta manual a entrar pelo contrato, e não diz nada sobre quem entrou
**antes** dela existir. Falta um estado, não uma lei.

## 63.6 · E UM DEFEITO DO PRÓPRIO ARNÊS

Dois dos meus mutantes não mutavam: `[] or [...]` devolve a lista, e
`[][:0] + [...]` devolve a lista. Apareciam no relatório como sobreviventes.

    UM MUTANTE QUE NÃO MUTA NÃO É UM SOBREVIVENTE:
    É UMA PERGUNTA QUE NUNCA FOI FEITA.

Corrigidos: 12 mutantes, 0 sobreviventes.

---

# §64 · CINCO BLOCKERS, E NENHUM DELES VEM DO PLACAR

**Missão:** `C-REMEASURE-COLLECTION-V1-CLOSE-GATES`
**HEAD final:** `be1f42eb`
**Dono novo:** `provas/os_portoes_da_collection.py`

## 64.1 · O QUÊ

```
COLLECTION_CORE_CLOSE = FAIL
BIG_COLLECTION_READY  = FAIL

BLOCKERS          5
DÍVIDA QUE NÃO BLOQUEIA  5
CAUSAS-RAIZ       4
MISSÕES ATÉ FECHAR  3
```

## 64.2 · POR QUÊ — DOIS EIXOS QUE NÃO SE INFEREM

A matriz de conformidade tinha um eixo só: a lei já funciona? Faltava o outro:
a falta dela **impede** a coleta grande?

| eixo | natureza | fonte |
|---|---|---|
| `IMPLEMENTATION_STATE` | declarado pela Bíblia | `docs/biblia/leis.json` |
| `CLOSE_GATE` | **medido** | esta missão |

Medido: **48 leis `PARTIAL`** e **5 blockers**. Nenhum blocker foi derivado do
estado de lei.

    UMA LEI PARTIAL PODE NÃO BLOQUEAR NADA,
    E UMA LEI PEQUENA PODE BLOQUEAR TUDO.

Inferir um eixo do outro produz uma fila de missões que trabalha no que é fácil
de medir em vez do que está a travar.

## 64.3 · PROVA — DOIS ACHADOS QUE SÓ APARECERAM POR CORRER

Levantei um PostgreSQL 16 descartável, apliquei as 27 migrations, e a
verificação `008` da própria casa passou. Depois:

```
corrida COMPLETA  →  raw_asset = 1 · RUN_STATE = COMPLETE
corrida sem país  →  raw_asset = 0 · enum `pais` recusa NOT_PRESERVED
```

**A prova da estrada canónica não corre neste HEAD.**
`test_m2_rota_forward` salta 22 de 25 sem banco, e com banco falha 21. O
fixture escreve a ficha do armazém com `SOURCE_SLUG` e **sem** `SOURCE_ID`, e
desde a B5B o escritor recusa observação sem fonte real.

    A ESTRADA ESTÁ BOA E O RETRATO DELA ESTÁ VELHO.
    Mas um retrato velho não prova a estrada de hoje.

O defeito é o **inverso** do clássico: não é uma prova que usa dados que a
produção nunca entrega — é uma prova que entrega **menos** do que a produção
entrega. `ingresso.para_o_dono_do_raw` já carrega `SOURCE_ID`.

**Duas línguas para a ausência colidem no banco.** `_corrida_completa` preenche
campo em falta com `NOT_PRESERVED`; o enum `pais` só aceita
`ES/FR/IT/PT/EU/BR/OTHER/NAO_SEI`. Sem `SOURCE_COUNTRY` o bruto não aterra e a
corrida fica `PARTIAL`, em silêncio para quem não lê o recibo.

É a **mesma família** do defeito do `SOURCE_ID` no `§60`: um valor honesto de um
lado que o outro lado não aceita.

## 64.4 · O QUE CUSTOU A CLASSIFICAR

O mecanismo temático falhar o portão é `HIGH` e **não** bloqueia. A função da
coleta grande é **adquirir e preservar**; admitir bem é a etapa seguinte, e a
Admission já produz decisão auditável com `NÃO SEI` de primeira classe. Bloqueia
o universo T3, e não a máquina.

Os 13 legados também não bloqueiam: estão fora por decisão, e o que entra pela
frente não passa por aquele estado.

E o inverso também foi guardado: `G-READY-01` continua `CRITICAL/BLOCKER`
embora exista um CLI que produz READY à mão.

    UM CLI NÃO É UMA ROTA.

## 64.5 · CONSEQUÊNCIA — A FILA MÍNIMA

| # | missão | causa-raiz |
|---|---|---|
| 1 | `C-FIX-ABSENCE-VOCABULARY-AT-THE-RUN-SEAM-V1` | RC-B, sem dependência |
| 2 | `C-RESTORE-CANONICAL-E2E-PROOF-V1` | RC-C, depende de RC-B |
| 3 | `C-CLOSE-THE-READY-EDGE-V1` | RC-A |

`MINIMUM_MISSIONS_TO_BIG_COLLECTION_READY = UNKNOWN`: depende de quantas
capacidades do SCRAP a coleta grande exige, e isso ainda não foi medido. Contar
agora seria feeling com cara de DAG.

## 64.6 · E UM MUTANTE QUE ENSINOU A CONFERIR

O último sobrevivente foi o total das leis escrito à mão: `return d, L, 105`.
O teste conferia `LAW_TOTAL == 105` e o mutante satisfazia-o.

    UM NÚMERO CONFERIDO CONTRA ELE PRÓPRIO
    NÃO É UMA CONFERÊNCIA: É UM ECO.

Morto com um registo alterado para sete leis, exigindo que o total o siga.
12 mutantes, 0 sobreviventes.

---

# §65 · A CONFISSÃO TEM DE CABER NA COLUNA QUE A RECEBE

**Missão:** `C-FIX-ABSENCE-VOCABULARY-AT-THE-RUN-SEAM-V1`
**HEAD final:** `5fbfb3ff`
**Tocado:** `coleta/ingresso.py::_corrida_completa`

## 65.1 · O QUÊ

O primeiro blocker da DAG do `§64` está fechado. Uma corrida que não declara o
seu país volta a aterrar o bruto.

```
antes:  corrida sem país  →  raw_asset = 0 · RUN_STATE = PARTIAL
depois: corrida sem país  →  raw_asset = 1 · RUN_STATE = COMPLETE
```

## 65.2 · POR QUÊ

`_corrida_completa` preenchia todo campo em falta com `NOT_PRESERVED`. Mas
`collection_run.source_country` não é texto: é o enum `pais`, e o vocabulário
dele é `ES/FR/IT/PT/EU/BR/OTHER/NAO_SEI`.

    UMA CONFISSÃO QUE A COLUNA RECUSA
    NÃO É UMA CONFISSÃO: É UMA PERDA.

E a perda era silenciosa para quem não lesse o recibo: o bruto não aterrava e a
corrida ficava `PARTIAL`.

É a **mesma família** do defeito do `SOURCE_ID` no `§60`: um valor honesto de um
lado que o outro lado não aceita.

## 65.3 · PROVA — E O QUE NÃO SE FEZ

Três casos contra PostgreSQL real, e não comparação de strings. A string
`NOT_PRESERVED` é perfeitamente válida em Python; quem a recusou foi o banco.

**O centro da correcção é o que ela NÃO fez.** Não se colapsaram os dois
conceitos. `NOT_PRESERVED != NÃO SEI` continua a valer e continua a ser o que os
outros campos recebem. Trocar a palavra em todo o lado faria o teste passar e
apagaria a diferença entre «não guardei» e «não sei».

O que a tabela nova diz é outra coisa: **qual das duas palavras o dono de cada
campo entende**.

    QUEM MANDA NO VOCABULÁRIO DA AUSÊNCIA
    É O DONO DA COLUNA, E NÃO A FRONTEIRA.

A palavra não foi escolhida por gosto: `pais` já declara `NAO_SEI` como o seu
próprio default desde a migration `001`. O autor do esquema já tinha decidido o
que é um país não declarado.

6 mutantes, 0 sobreviventes. O mutante que mais interessa é o segundo: colapsar
`AUSENCIA_PADRAO` em `NAO_SEI` faria os três casos aterrarem e morre na mesma,
porque há teste a exigir que os dois campos confessem com palavras diferentes.

## 65.4 · UM SUSTO QUE ERA MEU

`test_social_persistencia_pg` deu 40 erros de chave estrangeira, e eu quase os
registei como achado pré-existente. Era resíduo das minhas próprias sondas no
banco descartável: recriado limpo, passa.

    UMA MEDIÇÃO FEITA EM CIMA DA SUJEIRA DA MEDIÇÃO ANTERIOR
    MEDE A SUJEIRA.

## 65.5 · CONSEQUÊNCIA

`test_m2_rota_forward` continua a falhar 21, com o mesmo erro de fixture sem
`SOURCE_ID`. Isso é `RC-C`, a missão 2 da DAG, e não esta.

A ordem da fila confirmou-se na prática: esta era a que não dependia de nada, e
qualquer prova E2E nova teria batido neste enum antes de chegar ao resto.

```
COLLECTION_CORE_CLOSE  continua FAIL
BLOCKERS               5 → 4
```

---

# §66 · UMA EXECUÇÃO QUE MORREU NÃO ESCREVE O PRÓPRIO FIM

**Missão:** `C10.6B — RUN DURÁVEL / CHECKPOINT CANÔNICO`
**HEAD final:** `a8c28172`
**Tocado:** `coleta/coleta_checkpoint.py` · `medidas/rastro_da_coleta.py` ·
`ferramentas/reel_transcricao.py` · `coleta/adaptador_instagram.py`

## 66.1 · O QUÊ

A C10.6 tinha provado que a cadeia de Reel aguenta um `os._exit()`. Ficou
`PARTIAL` por um motivo só: o processo seguinte sabia ler a **gaveta**.

```
RUN_STATE_PERSISTENCE  NOT_IMPLEMENTED → IMPLEMENTED
MUTANTS = 12  SURVIVORS = 0 · ATTACKS = 25 · NEW_FAILURES = 0
NEW_MIGRATION = NO · LIVE_TOUCHED = NO
```

    UM FICHEIRO NO DISCO É UM RESULTADO. NÃO É UMA EXECUÇÃO.

Nenhuma coluna nova. As migrations 001, 016 e 024 já tinham representação
honesta para tudo — o que faltava era **aresta**, e a casa já tinha escrito que
isso não é a mesma coisa: `MODULE EXISTS != EDGE EXISTS != FLOW EXISTS`.

## 66.2 · A LEI QUE A TABELA JÁ TINHA, E QUE RESOLVEU A PERGUNTA DIFÍCIL

Depois de uma retomada, o que fazer com a execução que morreu? A tentação é
marcá-la `falhou`. O comentário da própria `collection_run` proíbe:

> «PROVENIÊNCIA É PROSPECTIVA: não se preenche elo de execução passada. Inventar
> o elo depois seria fabricar proveniência.»

    UMA EXECUÇÃO QUE MORREU NÃO ESCREVE O PRÓPRIO FIM.
    E NINGUÉM ESCREVE POR ELA.

E não é só direito: é **conhecimento**. `rodando` e `EM_CURSO` não distinguem
«alguém está a correr agora» de «alguém morreu a correr». Sem lease, heartbeat
ou `pid+host`, nenhum leitor sabe qual dos dois é — e inventar a distinção seria
sobrecarregar um campo com um segundo significado.

O abandono fica **legível** na evidência: uma etapa `RUNNING` que ninguém fechou,
ao lado de uma execução posterior no mesmo checkpoint que concluiu. Quem decide
o que isso significa é gente.

    UM ESTADO QUE SE LÊ DA EVIDÊNCIA É MAIS HONESTO QUE UM ESTADO QUE SE ESCREVE
    POR SUPOSIÇÃO.

## 66.3 · `RUNNING` ESTAVA NO VOCABULÁRIO E NENHUM ESCRITOR O SABIA ESCREVER

`leis/telemetria.py` declarava `RUNNING` desde sempre. `medidas/rastro_da_coleta`
escrevia a passagem **depois** de ela acontecer, com o estado final — a forma
certa para quem chega ao fim, e inútil para quem não chega.

    UM ESTADO QUE NENHUM ESCRITOR ESCREVE SÓ EXISTE NO PAPEL.

A etapa passou a escrever-se em dois tempos na MESMA linha (`abrir_etapa` /
`fechar_etapa`), e a chave `(run_id, etapa, tentativa)` continua única. Quem
morre entre as duas deixa `RUNNING` com `terminou_em` nulo — que não diz «está a
correr agora», diz «começou e ninguém a fechou».

**Corolário que a mesma missão descobriu:** um processo VIVO nunca pode deixar
isso atrás de si. Só a morte tem esse direito, porque só ela não teve como
fechar. Uma exceção dentro do trabalho fecha as etapas abertas antes de subir.

## 66.4 · LER «PODES» NÃO É TER TOMADO

`pode_gastar` é uma função `stable` — uma leitura pura. Entre a leitura e a
escrita não há nada. Dois processos de verdade contra um Postgres de verdade,
**20 rodadas em 20** avançaram o mesmo checkpoint duas vezes.

    ENTRE A PERGUNTA E A ESCRITA CABE OUTRO PROCESSO INTEIRO.

A correção não foi um lock novo nem uma coluna nova: a pergunta e a escrita
passam a viajar na **mesma instrução** — `where estado <> 'CONCLUIDO' returning
…`, o `compare-and-set` que a tabela já permitia. O perdedor volta de mãos
vazias e **sabe** que perdeu.

O que isto NÃO conserta, e ficou declarado: os dois continuam a fazer o
trabalho. Impedir isso exige saber se o dono anterior está vivo — §66.2.

## 66.5 · O `psql` FALA, E A FALA VIRAVA DADO

Um `update … returning` que não casa com linha nenhuma imprime o **seu próprio
recibo** em stdout: `UPDATE 0`. O leitor da casa devolvia-o como se fosse uma
linha de resultado — e o `compare-and-set` acima lia `[['UPDATE 0']]`, concluía
que tinha ganho, e os **dois** processos diziam «avancei».

    ZERO LINHAS NÃO É UMA LINHA QUE DIZ ZERO.

Conserto: `-q`. É a terceira vez que esta família morde a casa — `pode_gastar`
já carrega no corpo o aviso do `'t'` contra `'true'`, e o mesmo leitor já tinha
o buraco do campo final vazio que some no recorte.

    QUANDO SE LÊ UM BANCO POR UM CLIENTE DE LINHA DE COMANDO,
    A CONVERSA DO CLIENTE É PARTE DO QUE VOLTA — E NÃO É RESPOSTA.

## 66.6 · UMA PROVA QUE MOSTRA O NÚMERO E NÃO O EXIGE MEDE O ECRÃ

A prova de Postgres desta missão nasceu a **imprimir** o estado de cada crash e
a passar. Parecia completa: matava processos de verdade, abria ligação nova,
lia tudo do banco. Doze mutações mostraram o preço — **nove sobreviveram**.

Nada ali exigia que o estado fosse aquele.

    IMPRIMIR NÃO É AFIRMAR.

Sete invariantes passaram a ser afirmadas, e a taxa foi a 12/12. É a mesma lei
que a casa já tinha para sondas (`UMA SONDA QUE ENCONTRA ZERO E DIZ «LIMPO» MEDE
A SONDA`), aplicada ao outro lado: uma prova que só descreve mede o relatório.

## 66.7 · DOIS MUTANTES INVÁLIDOS, E O SEGUNDO DRIVER QUE ELES REVELARAM

Duas das mutações «sobreviventes» não mudavam comportamento nenhum: uma
renomeava uma função e chamava o nome novo; a outra cortava uma das **duas**
escritas da mesma ligação.

    UMA MUTAÇÃO QUE NÃO MUDA O QUE O CÓDIGO FAZ NÃO PROVA NADA.
    UM MUTANTE INVÁLIDO É UM SOBREVIVENTE FALSO — E ELE ESCONDE OS VERDADEIROS.

E uma terceira sobreviveu por um motivo que valeu a missão inteira: existiam
**dois drivers** da mesma sequência durável. O segundo tinha zero chamadores, e
a mutação trocou o bloco de abertura *dele*. A suíte não caiu porque ninguém o
corre.

    UM OWNER COM DUAS CÓPIAS DA MESMA ORDEM JÁ É DOIS.
    E A CÓPIA QUE DIVERGE EM SILÊNCIO É SEMPRE A QUE NINGUÉM CHAMA.

Foi retirado. Zero chamadores não é «inofensivo»: é «ninguém vai reparar».

## 66.8 · INSTRUMENTAR NÃO PODE SER CONDIÇÃO PARA FUNCIONAR

A cadeia de Reel sabe onde os seus degraus estão; não sabe que existe um
Postgres do outro lado. A junta é um **relator**: um objeto com `abrir` e
`fechar` que a cadeia usa nos degraus que realmente atravessa, e que quem tem
banco substitui pelo que escreve.

Sem relator, um objeto mudo responde `None` a tudo e a cadeia corre como sempre
correu — um caminho de código só, e não dois com um `if` em cada degrau.

    UM `if` POR DEGRAU É ONDE UM DEGRAU FICA DE FORA.

E os estados que ela relata não são booleanos: bytes que já estavam em casa
fecham `FETCH` em `SKIPPED` com `reused=1`, porque **reusar não é adquirir**; e
«ouvi e não havia fala» fecha `DERIVED` em `PASS` com `canonical_state =
ZERO_RESULTS`, porque **zero resultados é um resultado**.

## 66.9 · CONSEQUÊNCIA

`RUN_STATE_PERSISTENCE` deixa de ser o bloqueio da C10.6. A cadeia de Reel tem
aresta para os três donos — RUN, checkpoint e rastro — e nenhum deles ganhou um
segundo.

Fica escrita, em vez de improvisada, a única coisa que exige contrato novo:
**não há como perguntar se uma RUN está viva**. Enquanto não houver, `rodando`
numa execução morta é a verdade que a casa consegue dizer.

---

# §67 · UMA INFRAESTRUTURA COMUM NÃO É PROVADA POR UM ÚNICO ADAPTER USANDO-A

**Missão:** `C10.6C — CONVERGÊNCIA DO RUNTIME DURÁVEL DO SINTONIA SCRAP`
**HEAD final:** `66e41b9c`
**Tocado:** `coleta/scrap_executor.py` · `coleta/scrap_registo.py` ·
`coleta/coleta_checkpoint.py` · `coleta/adaptador_instagram.py` ·
`medidas/rastro_da_coleta.py`

## 67.1 · O QUÊ

A `§66` fechou o estado durável na cadeia de Reel. Esta missão perguntou de quem
ele era, e a resposta foi medida:

```
WIRED_CAPABILITIES = 13 · COM DURABILIDADE = 3 · SEM = 10
C10_6C_RUNTIME_CONVERGENCE = BLOCKED_ARCHITECTURE_DECISION
```

O runtime comum foi construído, está no boundary certo e está provado em três
classes de execução. O que bloqueia são **15 invocações vivas de workflow** que
correm as implementações e nunca tocam no executor.

## 67.2 · A PERGUNTA QUE UMA MISSÃO SÓ FAZ DEPOIS DE TER SUCESSO

A `§66` foi um PASS. Fez tudo certo: donos chamados, nada duplicado, mutações a
zero. E pôs a durabilidade **dentro do adaptador do Instagram**, porque era ali
que o trabalho estava.

    UMA INFRAESTRUTURA COMUM NÃO É PROVADA POR UM ÚNICO ADAPTER USANDO-A.

A lição não é que a `§66` errou — é que **provar uma coisa num sítio não diz de
quem ela é**. A pergunta «isto é comum?» tem de ser feita depois, e tem de ser
feita com um censo, não com uma impressão.

## 67.3 · ALCANCE NÃO É USO

O primeiro censo desta missão caminhou o fecho transitivo dos `import` e disse
que o YouTube tinha durabilidade. Tinha `import coleta_checkpoint` — para dois
ajudantes de identidade. Nunca chamou o driver.

    UMA SONDA QUE MEDE ALCANCE TRANSITIVO MEDE O QUE PODE, NÃO O QUE FAZ.

A medição certa é por CHAMADA, e com o nome da função. É a irmã da lei que a
`§62` escreveu para os censos de texto: alcance, citação e chamada são três
coisas, e só a última é uma aresta.

## 67.4 · O BOUNDARY É O PONTO MAIS ALTO QUE NÃO INVENTA

Cinco critérios decidiram, e o quinto foi o que desenhou o código: o boundary
não pode registar etapa que nunca ocorreu. `scrap_executor.COLLECT` não sabe se
houve `FETCH` — logo não o escreve. Escreve **uma** etapa: o `CHECK` que ele
próprio atravessa.

    NÃO SE FABRICA ETAPA. QUEM NÃO ATRAVESSOU NÃO RELATA.

O que desce para quem sabe reportar é um **relator**, e só para quem o declara na
assinatura. Um executor que só funcionasse com implementações instrumentadas já
não seria o executor de todas.

## 67.5 · TRÊS COISAS DIFERENTES, E SÓ UMA É SEMPRE VERDADE

```
RUN_REQUIRED          toda execução real existiu
STAGE_TRACE_REQUIRED  toda etapa atravessada deixa rasto
CHECKPOINT_REQUIRED   só quando há unidade retomável
```

«Resolver um canal pelo nome» ou resolveu ou não resolveu. Dar-lhe checkpoint
para o painel dizer `CHECKPOINT = YES` trancá-la-ia para sempre com
`JA_CONCLUIDO_NAO_PAGAR_DUAS_VEZES` na segunda vez que alguém a pedisse.

    FABRICAR RETOMADA ONDE NÃO HÁ NADA A RETOMAR NÃO AUMENTA COBERTURA.
    TRANCA A PORTA.

Quem declara a unidade é o adapter, porque é a única coisa que só ele sabe dizer.
Quem não declara não ganha checkpoint — e isso é uma resposta, não um
esquecimento.

## 67.6 · UM PORTÃO QUE RECUSA NÃO FALHOU

O `CHECK` fecha em `SKIPPED`, não em `FAIL`. `FAIL` diria que o próprio CHECK
rebentou; o que houve foi ele correr, medir e responder «não dá».

E o schema já o sabia: `falha_tem_codigo` exige `diagnostic_code` em toda linha
`FAIL`, e `leis/diagnostico.py` não tem código para `CHECK`. **Não tem porque
`CHECK` não falha.** A ausência no registry era a lei escrita onde ninguém tinha
lido.

    QUANDO UMA TRAVA DO BANCO RECUSA, LEIA-A ANTES DE A CONTORNAR:
    ÀS VEZES ELA ESTÁ A DIZER QUE O SEU VOCABULÁRIO É QUE ESTÁ ERRADO.

## 67.7 · A PROVA DE QUE É COMUM É PARTIR-SE IGUAL

Três classes de execução — mídia por `executa`, API por `rota`, JSON por `rota` —
mortas no mesmo ponto com `os._exit(97)`. As três deixaram exactamente a mesma
forma: `RUN=rodando`, `CHECK/PASS`, checkpoint só onde havia unidade.

    A PROVA DE QUE A INFRAESTRUTURA É COMUM É ELA PARTIR-SE IGUAL EM TODAS.

Um teste de sucesso mostra que funciona nas três. Um teste de **morte** mostra
que é a mesma coisa nas três.

## 67.8 · QUATRO MUTANTES, E A REGRA QUE ELES ENSINARAM

Quatro sobreviveram à primeira bateria. Um deles — sobrescrever a tentativa
anterior — sobreviveu porque eu corria só a prova da missão nova.

    UMA MISSÃO NOVA NÃO DISPENSA A PROVA DA ANTERIOR.
    A BATERIA DE MUTAÇÃO TEM DE EXIGIR TODAS AS PROVAS QUE JÁ EXISTEM.

Os outros três pagaram sentinelas que faltavam: a ordem entre abrir a etapa e
fazer o trabalho, o ramo de excepção que não pode fechar como sucesso, e a regra
de que só capacidade **wired** declara unidade.

## 67.9 · UM ZERO SÓ VALE SE A SONDA ESTIVER A OLHAR PARA O SÍTIO

O ataque que devia encontrar os bypasses procurou **adapters** nos workflows e
achou zero. Os workflows não chamam adapters: chamam as **implementações**.

    UM ZERO SÓ VALE SE A SONDA ESTIVER A OLHAR PARA O SÍTIO.

Corrigido, encontrou 19 menções; separando invocação de verificação de presença —
a disciplina que a `§62` já tinha escrito — ficaram **15 portas reais**.

## 67.10 · CONSEQUÊNCIA

O runtime durável comum existe, está provado, e não precisa de migration nenhuma.
A convergência não fecha porque 15 fases operacionais entrariam por outro sítio,
e mudá-las muda a superfície operacional inteira da casa.

    QUANDO O QUE FALTA É UMA DECISÃO DE GENTE, O VEREDITO É BLOQUEADO —
    NÃO PARCIAL, E MUITO MENOS PASSA.

Arredondar isso para `PASS` porque «o código está pronto» seria dizer que o
sistema converge quando quinze portas dizem que não.

---

# §68 · A ESTRADA ESTAVA BOA E O RETRATO DELA ESTAVA VELHO

**Missão:** `C-RESTORE-CANONICAL-E2E-PROOF-V1`
**HEAD final:** `d8c21d4a`
**Tocado:** `tests/test_m2_rota_forward.py` · `provas/a_rota_m2_atravessa.py`

## 68.1 · O QUÊ

`G-E2E-01` fechado. A prova da estrada canónica volta a correr: **25 de 25**
contra PostgreSQL 16 com as migrations `001..027`, e `ROTA_M2_ATRAVESSA=PASS`
sobre banco virgem.

`RUNTIME_CHANGED = NO`. Nenhuma linha de produção mudou.

## 68.2 · POR QUÊ — DUAS CÓPIAS DE UM CONTRATO

O defeito não era um: eram dois do mesmo género, e os dois eram **cópias**.

**O fixture escrevia à mão a língua do armazém.** Medido campo a campo, ele
entregava menos do que a produção entrega, e o campo que faltava era
`SOURCE_ID` — o que a B5B passou a exigir.

    UM FIXTURE QUE ENTREGA MENOS DO QUE A PRODUÇÃO ENTREGA
    REPROVA A ESTRADA POR UM DEFEITO QUE É DELE.

**A lista de migrations parava na `026`.** A `027` — a que tirou a trava do
endereço de `raw_asset` — nunca era aplicada. A prova atravessava um esquema
uma migration atrás da realidade e dizia-se canónica. O comentário que lá
estava já avisava: «uma lista à mão envelhece calada, e esta envelheceu».
Envelheceu outra vez.

    REMENDAR UMA LISTA QUE JÁ ENVELHECEU UMA VEZ
    É MARCAR ENCONTRO COM O MESMO DEFEITO.

## 68.3 · PROVA — SEGUIR, E NÃO IMITAR

Os dois passaram a **derivar do dono** em vez de o copiar: o fixture fala pelo
`ingresso.para_o_dono_do_raw`, e a cadeia de migrations é lida da pasta.

    PRODUCTION CONTRACT → TEST FOLLOWS,
    e nunca STALE TEST → PRODUCTION WEAKENED.

A linhagem, lida do banco:

```
RUN_ID              RUN-M2-ATRAVESSA
RAW_OBSERVATION_ID  raw_asset.id = 1 · FORWARD_IDENTIFIED
SOURCE_ID           IT-T2-002
STORAGE_OBJECT_ID   1
DERIVED_ID          1  →  raw_asset_id 1
STRUCTURED          conteudo id 1
```

## 68.4 · QUATRO MUTANTES, E TRÊS ERAM O MESMO

Trocar a fonte pelo slug, pelo sha, ou por uma expressão que lê o **caminho**:
a travessia completava-se na mesma, porque o escritor aceita qualquer texto que
não seja sentinela.

    ATRAVESSAR NÃO É ATRAVESSAR COM A IDENTIDADE CERTA.

E o do caminho não se apanha por valor nenhum: ele dá **exactamente a mesma
string**.

    QUANDO O DEFEITO DÁ O VALOR CERTO,
    SÓ A ESTRUTURA O DENUNCIA.

Morreu com uma verificação `ast`: o `SOURCE_ID` do fixture tem de ser um
literal, nunca uma expressão.

O quarto sobrevivente era a minha própria guarda com agulha vazia. E a guarda
que a apanha teve de ser estrutural também — a primeira versão usava expressão
regular e apanhou o **exemplo** dentro da docstring que cita o padrão mau de
propósito. É o `§60` outra vez, ao contrário.

    UM TEXTO NÃO DISTINGUE O EXEMPLO DA OCORRÊNCIA.

9 mutantes, 0 sobreviventes.

## 68.5 · E DOIS TESTES QUE TIVERAM DE APRENDER QUE GAPS FECHAM

Ao fechar `G-E2E-01` e `G-RUN-01`, dois testes meus do censo reprovaram uma
fila correcta: um exigia que **todos** os sintomas de uma causa fossem blocker,
o outro que a lista de dependências fosse vazia.

    UM TESTE QUE SÓ ESTÁ CERTO ENQUANTO NADA AVANÇA
    É UM TESTE QUE MEDE O PRIMEIRO DIA.

Passaram a falar de blocker **aberto** e dependência **aberta**.

## 68.6 · CONSEQUÊNCIA

```
BLOCKERS  5 → 3   G-READY-01 · G-READY-02 · G-RAW-01
FILA      1. C-MAKE-RAW-OBSERVABLE-V1
          2. C-CLOSE-THE-READY-EDGE-V1
```

Os gaps fechados **ficam** na lista com o estado novo. Um gap que some não
deixa ver que existiu, nem por que deixou de existir.

O que esta prova continua a **não** provar: produção, e READY. Ela começa no
bruto já preservado e acaba na ADMISSION. `REQUEST`, `ORCHESTRATOR` e
`EXECUTOR` continuam por observar.

---

# §69 · O SKIP QUE PARECIA UM PASS

A missão §68 fechou `G-E2E-01` com 25/25 verdes e uma mutação de 9 mutantes
sem sobreviventes. A prova estava boa. Faltava-lhe uma linha, e a linha estava
a saltar.

## 69.1 · ONDE O BURACO ESTAVA

A prova de **valor** — ler `raw_asset` e comparar a fonte que aterrou com o
canário declarado em `system-map/data/estradas-it.model.json` — vivia em
`tests/test_a_prova_e2e_segue_a_producao.py`. Ela lia uma tabela que o módulo
ao lado tinha acabado de limpar:

```
tests/test_m2_rota_forward.py   tearDownClass  →  delete from raw_asset
tests/test_a_prova_e2e...       depois         →  tabela vazia → skipTest
```

A `tearDownClass` está **certa**: uma suite que suja o banco parte quem correr
a seguir (foi assim que nasceram os 40 erros de chave estrangeira de §61). O
erro não era limpar. Era pôr a pergunta num sítio onde a resposta já não
existe.

```
    SKIP != PASS.
    UM SUMÁRIO VERDE COM `skipped=1` NÃO DIZ QUAL PROVA NÃO CORREU.
```

E a lei já estava escrita — em `provas/os_portoes_da_collection.py`, por mim,
na missão anterior: `PORQUE_SALTA_SEM_BANCO: "SKIP != PASS"`. Escrevi a lei
para o caso de não haver banco, e não a apliquei ao caso de não haver linhas.

## 69.2 · O QUE O BURACO DEIXAVA PASSAR — MEDIDO

Com a prova a saltar, apliquei o mutante «trocar `SOURCE_ID` por slug» e
perguntei **quais** provas morriam:

```
FAIL  test_a_fonte_declarada_nao_e_o_slug         ← texto
FAIL  test_o_fixture_declara_a_fonte_do_canario   ← texto
      (nenhuma leitura do banco)
```

Duas guardas de **texto**, e mais nada. E `test_mesmo_SOURCE_ID_e_ROUTE_CLASS`
— que lê o banco — **não** reprovou: ela lê `etapa_da_corrida`, cujo
`source_id` vem da unidade, não da ficha. O que aterra em `raw_asset` não
tinha leitor nenhum.

Por isso o mutante que importa é este, e ele é de **produção**:

```
coleta/ingresso.py:   "SOURCE_ID": f.SOURCE_ID   →   "SOURCE_ID": "NAO SEI"
```

O fixture continua a declarar `IT-T2-002`. Todas as guardas de texto passam —
o texto está certo. A fonte é largada entre o fixture e a linha. É a família
exacta do `READER_GAP` de §60, e a prova restaurada não a via.

```
    UMA GUARDA DE TEXTO CONFERE O QUE ESTÁ ESCRITO.
    SÓ UMA LEITURA DO BANCO CONFERE O QUE ATERROU.
```

## 69.3 · A CORREÇÃO — A PROVA MUDA-SE, A REGRA NÃO

A prova de valor mudou-se para `M2_TravessiaUnica`, que corre a travessia e
pergunta ao banco **antes** de limpar. Ela salta só quando não há PostgreSQL
descartável nenhum — o caso honesto, e o mesmo `skipUnless` da classe `Base`.

No ficheiro de guardas ficou uma **sentinela**, não uma cópia:

```
alguém lê `public.raw_asset` e compara com o CANARIO   → tem de existir
e essa prova não chama `skipTest`                       → tem de ser verdade
```

A segunda é a que fecha o círculo: ela impede que a prova volte a
auto-salvar-se com um `skipTest`.

## 69.4 · A GUARDA QUE NÃO TINHA QUEM A CONFERISSE

Um mutante sobreviveu e ensinou o resto. A guarda do `G-E2E-01` estava escrita
a direito dentro da asserção:

```python
self.assertIn("_ing.para_o_dono_do_raw(ficha, {})", s, "...")
```

Enfraquecer a agulha para `assertIn("x", s + "x")` não parte nada. A guarda
passa a dizer sim a tudo, e ninguém repara — porque só há uma pergunta, e a
resposta certa continua a ser sim.

```
    UMA REGRA QUE SÓ SABE DIZER «SIM» AO FICHEIRO REAL
    NÃO DISTINGUE UMA GUARDA QUE MORDE DE UMA QUE JÁ NÃO MORDE.
    O «NÃO» É QUE PROVA A MORDIDA.
```

A regra saiu para uma função e ganhou dois exemplos sintéticos: um que ela tem
de aceitar, e um escrito à mão que ela tem de recusar. O mesmo mutante passa a
reprovar o exemplo negativo.

Isto não é regresso infinito. A meta-guarda não confere a guarda: ela dá-lhe
um **caso** em que a resposta certa é «não», e um caso é conferível.

## 69.5 · E A MEDIÇÃO QUE MEDIU A SUJEIRA OUTRA VEZ

A regressão desta janela acusou **14 falhas novas** em dois módulos. Ambos
passavam sozinhos, na mesma árvore limpa, no mesmo HEAD. A suite tinha corrido
ao mesmo tempo que a mutação, que reescreve ficheiros no sítio.

É a terceira vez na Collection. §63 foi resíduo da sonda anterior; aqui foi
concorrência — a mesma lei, outra porta:

```
    UMA MEDIÇÃO NÃO PODE CORRER AO LADO DE QUEM MEXE NO QUE ELA MEDE.
```

Antes de reportar qualquer falha nova: reproduzir o módulo sozinho. Se ele
passa, a falha não é dele — é da janela.

## 69.6 · CONSEQUÊNCIA

```
MUTANTES  9 → 11 · SURVIVORS 0
NOVOS     10 · o INGRESSO larga a fonte a caminho do RAW
          11 · a prova de VALOR volta a saltar-se a si própria
```

Os dois novos morrem, e são exactamente os que passavam inteiros antes desta
correção. `G-E2E-01` continua fechado — e agora fechado por uma prova que
corre, e não por uma que salta.

---

# §70 · UMA DECISÃO QUE UMA PORTA NÃO CONHECE NÃO É UMA DECISÃO. É UM DESEJO

**Missão:** `C10.6D — PORTAS OPERACIONAIS CANÔNICAS`
**HEAD final:** `1149e2b1`
**Tocado:** `.github/workflows/sintonia-scrap.yml` · `coleta/social_scrap.py` ·
`coleta/adaptador_instagram.py` · `coleta/comunicacao_coleta.py`

## 70.1 · O QUÊ

A C10.6C encontrou o boundary durável comum e mediu 15 portas que o
contornavam. A C10.6D foi medir quem essas portas eram — e a coisa que decidiu
tudo não era o número.

```
NENHUMA das seis implementações que os workflows corriam direto
importa `leis/social_matriz.py`.
```

Seis portas de produção, e nenhuma perguntava à dona da decisão se podia.
Quando a pergunta finalmente foi feita, a resposta foi **não** em quatro casos.
O pior: `yt-legendas` corria `_timedtext`, que a matriz declara
`ROUTE_NOT_ALLOWED` desde a C5 — por ToS, por `Disallow: /api/` e pelas
Developer Policies.

```
    UMA ROTA QUE FUNCIONA NÃO É UMA ROTA PERMITIDA.
```

## 70.2 · O CENSO TEVE DE SER REFEITO QUATRO VEZES, E AS TRÊS PRIMEIRAS MEDIRAM A SONDA

Esta é a parte reutilizável. Um censo de portas erra de três maneiras
diferentes, e cada uma parece um resultado.

**Primeira: filtrar por diretório.** O censo só olhava para `coleta/`,
`ferramentas/` e `admissao/`, e por isso não via `orquestrador/orquestrador.py`
— que é exactamente uma porta de Collection, e a única que sobrou no fim.

```
    UM CENSO QUE DECIDE A ESPÉCIE PELO DIRETÓRIO MEDE A ÁRVORE, NÃO A CASA.
```

**Segunda: classificar o módulo.** `instagram_coleta.py` faz cinco coisas:
`contratos` lê o schema do ator com `APIFY_RUNS = 0`, `liquidar` lê a fatura
depois, e `bio`/`posts`/`reels`/`comentarios` gastam. Classificar o módulo
contava duas ferramentas de leitura como aquisição paga.

```
    UM MÓDULO QUE FAZ CINCO COISAS TEM CINCO ESPÉCIES,
    E O CENSO MEDE A QUE FOI PEDIDA.
```

**Terceira: ler só a primeira etiqueta de um ramo.** O ramo
`contratos|plano|semaforo|liquidar)` tem quatro fases e um comando só,
`... "${{ inputs.fase }}"`. Guardar só `contratos` fazia o censo perguntar a
espécie de uma fase e responder pelas outras três.

Só a quarta volta mede a casa. `LIVE_INVOCATIONS 109 → 101`,
`COLLECTION_DIRECT_BYPASSES 7 → 0`.

## 70.3 · UMA SONDA SEM FRONTEIRA À ESQUERDA

O red team deu 16 achados na primeira volta. Doze eram da sonda, e oito eram a
mesma linha.

`instagram_coleta.py` **acaba** em `py`. A expressão

```python
re.search(r'(?:\$PY|python3?|py)\s+\S*' + re.escape(alvo), linha)
```

casa dentro de `for f in instagram_coleta.py instagram_janela.py`, porque o
`py` do fim de um nome de ficheiro serve de interpretador para o nome seguinte.

```
    UMA SONDA SEM FRONTEIRA À ESQUERDA
    VÊ UM INTERPRETADOR NO FIM DE UM NOME DE FICHEIRO.
```

A correção é `(?:^|[\s;|&(`])` antes do interpretador — e o controlo positivo é
a verificação de presença: a sonda TEM de a encontrar, e TEM de não a contar.

Outros quatro achados liam **menção** como **invocação**: dois ficheiros que
apenas imprimem o próprio nome numa linha de `uso:`, e uma CLI que imprime o
caminho da cadeia de fala numa mensagem de ajuda.

```
    MENÇÃO NÃO É INVOCAÇÃO.
```

## 70.4 · A BATERIA DE MUTAÇÃO QUE MEDIU O MUTANTE ANTERIOR

M7 sobreviveu. A sentinela matava-o quando corrida à mão, com o mesmo comando,
na mesma árvore. Duas horas de suspeita sobre o código, e o defeito estava no
`pyc`.

O bytecode valida por `(mtime, tamanho)` do ficheiro fonte. A linha que M6
acrescenta e a linha que M7 acrescenta têm **exactamente** o mesmo comprimento:

```python
"    'contratos':      ('INSTAGRAM', 'instagram.profile.discovery', ...)"
"    'yt-relevancia':  ('INSTAGRAM', 'instagram.profile.discovery', ...)"
```

Escritas no mesmo segundo, o mutante M7 correu contra o bytecode compilado para
M6 — e M6 já tinha sido morto por outra sentinela, noutro ficheiro.

```
    UMA BATERIA QUE MEDE O MUTANTE ERRADO NÃO MEDE NADA.
```

Duas correções, e ambas devem ficar em qualquer bateria futura desta casa:
apagar `__pycache__` antes de cada volta, e `troca()` confirmar por leitura que
a mutação chegou ao disco.

## 70.5 · O GRAFO INDEXADO POR NOME JUNTA DOIS DONOS

Para responder «esta fase da CLI chega ao boundary?», a primeira sonda montou
um grafo de chamadas indexado por **nome de função**. Ela disse que `censo`
alcançava `COLLECT`.

Não alcança. `censo` chama `mz.main()` — o `main` do `social_matriz`. E há
`main` em quase todo o ficheiro desta casa, incluindo o do próprio
`social_scrap`, que chega mesmo a `COLLECT`.

```
    UM GRAFO INDEXADO POR NOME JUNTA DOIS DONOS COM O MESMO NOME.
```

Cada nó passou a ser `(MÓDULO, FUNÇÃO)`, com `alias.f()` resolvido pelo import.
O resultado honesto: das 16 fases, **3** alcançam o boundary e **13** não.

## 70.6 · O DESVIO DECLARADO

Das 13 que não alcançam, nove não adquirem nada — leem o acervo ou imprimem
política. Quatro adquirem: `youtube`, `youtube-piloto`,
`youtube-piloto-oneshot` e `piloto`.

Não foram convertidas, e isso não é preguiça. `youtube` existe para medir a API
**diretamente** e `youtube-oficial` existe para medir a **mesma** API pelo
executor. O par É a medição: fazer as duas entrarem pela mesma porta apagava
exactamente a pergunta que elas respondem —

```
    MODULE EXISTS != EDGE EXISTS != FLOW EXISTS.
```

O que se corrigiu foi o silêncio. Cada uma passa a imprimir
`DESVIO_DECLARADO=<fase>` com o motivo, para que ninguém a leia como porta de
produção.

```
    UM DESVIO DECLARADO É UMA MEDIÇÃO. UM DESVIO CALADO É UM BURACO.
```

## 70.7 · E O QUE NÃO SE FEZ, QUE É METADE DO TRABALHO

`yt-relevancia` pergunta «vale a pena esta fonte?». Havia uma forma trivial de
fazer o número de bypasses cair de uma vez: pô-la na tabela de fases canônicas.
Ela correria, o censo diria zero, e juízo temático passaria a viver dentro da
coleta.

```
    COLETAR != ADMITIR != JULGAR.
    FABRICAR CAPACIDADE PARA BAIXAR O NÚMERO DE BYPASSES É MENTIR COM MÉTRICA.
```

Nove fases ficaram de fora de propósito, cada uma com a espécie escrita ao lado.
E as que não podem correr **recusam alto**, com o motivo — não desaparecem:

```
    BLOCKED != RETIRED.
```

## 70.8 · CONSEQUÊNCIA

```
COLLECTION_DIRECT_BYPASSES   7 → 0
COLLECTION_SECOND_RUNTIME    1 → 1   (nomeado: o orquestrador, com recibo próprio)
MUTANTES 13 · SURVIVORS 0
ATAQUES  32 · POSITIVE_FINDINGS 0
NEW_FAILURES 0 · SYSTEM_MAP_CHECK PASS
NETWORK_REAL 0 · APIFY_RUNS 0 · COST_USD 0
```

O veredito ficou `PARTIAL_CAPABILITY_GAPS` e não `PASS`, porque dois buracos
continuam abertos e ambos estão nomeados com o que seria preciso para os
fechar. Arredondar qualquer um deles para verde teria custado a única coisa que
estas missões produzem.

---

# §71 · A MATRIZ DECLARA A ESCADA. O ROTEADOR SÓ SABE SUBIR O PRIMEIRO DEGRAU

**Missão:** `C10.6E — PREP DO RUNTIME PAGO`
**HEAD final:** `01efc8a0`
**Tocado:** `coleta/comunicacao_coleta.py` (e mais nada de código)

## 71.1 · O QUÊ

A C10.6D deixou um segundo runtime de Collection nomeado. A C10.6E foi
convergi-lo e mediu que não dá — por uma razão que não é falta de política nem
falta de vontade.

A matriz declara uma **escada** de rotas por capacidade. Para
`INSTAGRAM/FETCH_POST` ela declara a rota grátis (que ela própria diz cobrir «os
12 mais recentes») e a rota paga, e escreve ao lado o motivo canônico de subir:
`FREE_ROUTE_INSUFFICIENT_CAPABILITY`. O roteador já tem o portão do gasto, com
vocabulário fechado.

O que não existe é a forma de pedir o degrau. `decisao()` e `_rota_padrao()`
devolvem **uma** rota — a primeira viável — e `executar()` não aceita `rota=`.

```
    A MATRIZ DECLARA A ESCADA. O ROTEADOR SÓ SABE SUBIR O PRIMEIRO DEGRAU.
```

Converger hoje trocaria, em silêncio, uma janela de 30 dias por 12 itens.

```
    UM CAMINHO QUE MUDA O QUE COLHE NÃO É O MESMO CAMINHO.
```

## 71.2 · O PORTÃO NÃO É O SELETOR

`permitir_pago=True` mais um motivo do vocabulário canônico **não** faz a rota
paga ser escolhida. Ele autoriza gasto na rota que já tinha sido escolhida.
Medido nas duas plataformas: com e sem autorização, a rota é a mesma, e o
`MOTIVO_PAGO` nem chega a ser gravado.

```
    UM PORTÃO DECIDE SE PASSA. UM SELETOR DECIDE POR ONDE.
    QUEM OS CONFUNDE AUTORIZA UM GASTO E ACHA QUE ESCOLHEU UMA ROTA.
```

Isto vale para qualquer casa com escada declarada: o campo que diz «pode gastar»
e o campo que diz «vai por aqui» são dois, e ter só o primeiro faz a escada
inteira parecer inalcançável sem que ninguém perceba porquê.

## 71.3 · DERIVAR O QUE NÃO FOI DECLARADO É FABRICAR

O censo encontrou quatro donos da identidade do fornecedor: a matriz e três
tabelas `ATORES` em código. A matriz diz `apify:instagram-scraper`; as tabelas
dizem `apify~instagram-scraper`.

Era tentador derivar uma da outra trocando `:` por `~` e declarar um dono só.
Seria inventar uma regra que ninguém escreveu — o nome na matriz é um **rótulo
de política**, o outro é um **identificador de execução**, e a semelhança é
coincidência de quem escolheu os nomes.

```
    DERIVAR O QUE NÃO FOI DECLARADO É FABRICAR, NÃO É NORMALIZAR.
```

O que se pode fazer sem inventar é **amarrar**: cada ator declara qual rota da
matriz cumpre, e uma conferência recusa quando a matriz deixa de a declarar ou
quando ela deixa de ser paga. Duas cópias amarradas continuam a ser duas — mas
deixam de poder divergir em silêncio, que era o defeito real.

## 71.4 · DOIS MUTANTES MAUS, E COMO SE RECONHECEM

Quatro sobreviventes na primeira volta. Dois eram das sentinelas e dois eram das
próprias mutações — e distinguir os casos é o trabalho.

**O mutante que não muda nada.** Acrescentar uma chave `_MUTANTE: None` a uma
plataforma da matriz não altera decisão nenhuma. Ele sobrevive por não ser uma
mutação.

```
    UMA MUTAÇÃO QUE NÃO MUDA O QUE O CÓDIGO FAZ NÃO PROVA NADA.
```

**O mutante que só tira metade do fecho.** O portão do gasto tem dois guardas
seguidos: `not permitir_pago` e `motivo_pago not in MOTIVOS_PAGOS`. Tirar o
primeiro deixa o segundo a recusar na mesma, porque `motivo_pago` continua
`None`. O mutante sobrevive por a mutação ser incompleta.

```
    UM PORTÃO COM DOIS FERROLHOS SÓ ABRE QUANDO SE TIRAM OS DOIS.
```

Antes de acusar a sentinela, rodar o mutante à mão e ver se o comportamento
mudou. Nos dois casos não tinha mudado.

## 71.5 · A SONDA QUE ACUSA O DONO

O ataque «LinkedIn usa HarvestAPI escondido» varria todos os módulos à procura
de `harvestapi`, e acusou `leis/social_matriz.py` — que nomeia o ator porque é
ele que o **proíbe**.

```
    UMA SONDA QUE PROCURA O DONO NA LISTA DOS SUSPEITOS ACUSA O DONO.
```

O dono da lei sai da população, e entra um controlo positivo: se a sonda deixar
de ver **qualquer** utilizador do ator, é ela que se partiu.

## 71.6 · O QUE SE ENTREGA QUANDO NÃO SE PODE CONVERGIR

O veredito foi `BLOCKED_CONTRACT_GAP`, e um veredito bloqueado só vale se
entregar três coisas: onde exatamente o caminho para, o que falta para não
parar, e o preço de continuar sem isso.

O caminho antigo ficou — a política permite-o e pará-lo por decisão própria
fecharia uma coleta autorizada. O que deixou de existir foi o silêncio: a fase
diz que não atravessa a casa, que rota usa, qual seria a canônica e o que falta.

```
    UM DESVIO DECLARADO É UMA MEDIÇÃO. UM DESVIO CALADO É UM BURACO.
```

## 71.7 · CONSEQUÊNCIA

```
PAID_ROUTE_REACHABLE  = NO      (medido, não suposto)
PROVIDER_IDENTITY_OWNERS 4 → 4, mas 3 amarrados e conferidos
RUN_ID_MINTERS = 3              escrito, não corrigido: exige a convergência antes
MUTANTES 12 · SURVIVORS 0 · ATAQUES 33 · NEW_FAILURES 0
APIFY_RUNS 0 · COST_USD 0 · LIVE_TOUCHED NO
```

```
    CAN DO != DID DO.
```

---

# §72 · UMA ETAPA MUDA NÃO SE DISTINGUE DE UMA QUE NÃO CORREU

`G-RAW-01` dizia: «a etapa RAW corre e não fala». Fechá-lo parecia ser
acrescentar uma chamada. Foi — e o que se aprendeu não estava na chamada.

## 72.1 · NÃO FALTAVA DONO. FALTAVA UMA CORRELAÇÃO

A primeira pergunta da missão era se isto exigia um sistema novo de
observabilidade. Medido, não exigia nada disso:

```
medidas/rastro_da_coleta.py      o dono do rastro    JÁ EXISTIA
telemetria.ETAPAS_DA_COLETA      já continha `RAW`
diagnostico.da_etapa('RAW', …)   já devolvia RAW_PERSISTENCE_FAILED
```

Estava tudo escrito menos a linha. O que faltava era **uma** coisa: a
passagem sabia nomear a corrida (`run_id`) e a fonte (`source_id`), e não
sabia nomear a **observação** que tinha produzido.

Isso é uma coluna na tabela canónica, não um livro ao lado.

```
    DOIS DONOS DA MESMA PERGUNTA
    SÃO DUAS RESPOSTAS À ESPERA DE DIVERGIR.
```

A migration 028 acrescenta `etapa_da_corrida.raw_asset_id`, NULLABLE, com
uma trava que só deixa a etapa `RAW` preenchê-la: apontar para o artefato de
outra etapa é assinar o trabalho dela.

## 72.2 · A FRONTEIRA JÁ TINHA SÍTIO, E NÃO ERA O DONO DO RAW

O gate nomeava `guarda/preservar_coleta.py` como owner. Mas esse ficheiro
nunca abre ligação — é isso que permite prová-lo contra banco descartável. A
peça que fala pelo DERIVED é `coleta/derivacao_forward.py`, uma **fronteira**
que traduz o recibo do dono para a língua do rastro.

A fronteira equivalente do RAW já existia: `coleta/ingresso.py`, que
`provas/o_encanamento_tem_uma_porta.py` prova ser o único chamador de
`preservar()` na casa. Foi lá, e não inventou módulo nenhum.

E fala **depois**:

```
RAW PERSISTE → o banco devolve o id → a telemetria conta a passagem
```

Emitir antes do INSERT dá um sucesso sem sujeito, e um rastro de sucesso que
aponta para nada é pior do que rastro nenhum — porque parece medido.

## 72.3 · TRÊS DEFEITOS QUE SÓ A MEDIÇÃO VIU

**A mesma observação caía em dois baldes.** Num reencontro, a linha
reaproveitada aparece em `RAW_OBSERVATIONS` *e* em `REUSED_METADATA`. Somar
as duas dava `accounted = 2` para uma entrada de 1, e o banco devolvia
`unaccounted_input = -1`: um buraco **negativo**, inventado pela contagem.

**`"   "` passava por fonte.** `preservar_coleta._identifica` já o recusava —
«veio vazio, com espaço a fingir conteúdo». A fronteira não. Duas regras
iguais escritas de maneiras diferentes são duas regras à espera de discordar.

**O censo da observabilidade era uma lista à mão.** `["DERIVED","STRUCTURED",
"ADMISSION"]` escrito a direito, com `["RAW"]` ao lado. No dia em que a etapa
RAW passasse a falar, ele continuaria a dizer que não falava — sem erro
nenhum.

```
    UM CENSO ESCRITO À MÃO MEDE QUEM O ESCREVEU.
```

Agora é AST sobre o código de produção: quem chama `rastro.registrar`, e com
que `etapa=`.

## 72.4 · RECUSAR NÃO É FALHAR

O primeiro desenho marcava `FAIL` sempre que nada aterrava. Medido contra uma
colheita sem fonte provada, isso dava uma etapa avariada onde havia uma
colheita recusada — e mandava o operador consertar a peça errada.

`rota_forward_documento` já tinha decidido isto no STRUCTURED: «NÃO é erro
nosso: é o item». Quatro estados, e nenhum colapsa:

```
NOT_RUN   nem chegou a ser tentada      (nada sobreviveu ao contrato da porta)
PASS      correu — mesmo que tenha recusado tudo, com `rejected` a contar
FAIL      tentou persistir e não conseguiu
REUSED    reencontrou, e não observou de novo
```

## 72.5 · UMA PROVA QUE REBENTA NÃO DÁ VEREDITO

Cinco mutantes — um caminho dentro do `raw_asset_id`, um `run_id` sem
corrida, o rastro a falar antes de persistir — faziam a prova levantar a
meio. O veredito saía `?`, e o harness contou-os como **sobreviventes**.

```
    UMA PROVA QUE NÃO CONSEGUE DIZER `FAIL`
    NÃO ESTÁ A APROVAR: ESTÁ A CALAR-SE.
```

É o irmão do `SKIP != PASS` de §69, por outra porta: ali a prova saltava, aqui
morria. As duas leem-se de longe como se nada tivesse acontecido.

## 72.6 · E A GUARDA QUE NÃO VIA O QUE PROIBIA

`tests/test_raw_observation_id_volta` protege uma lei boa: a porta transporta
o que o dono devolveu, não fala com o banco. Ela lia o código por `_codigo()`,
que **apaga as strings** — e SQL vive dentro de strings.

Posto de propósito um `memoria.aplicar("select 1 from public.raw_asset")`
dentro da porta, ela deixou passar sem uma queixa. O que ela apanhava era o
*token* `raw_asset_id`, que é o nome de uma coluna e não uma conversa.

```
    UMA GUARDA QUE LÊ O CÓDIGO SEM AS STRINGS
    NÃO VÊ O SQL, QUE É EXACTAMENTE ONDE ELE MORA.
```

Passou a ler por AST: vê as strings e não vê os comentários — que é a divisão
certa, porque a prosa pode nomear a tabela e o código não pode falar com ela.
Conferida com o defeito posto: morde. Retirado: passa.

E a consulta saiu da porta para `rastro.proxima_tentativa()`, onde já devia
estar: a pergunta é sobre `etapa_da_corrida`.

## 72.7 · UM ERRO MEU, REGISTADO COMO TAL

A meio da missão corri `git checkout -- .` com trabalho **não commitado** e
revertei todas as alterações em ficheiros rastreados. Sobreviveram os três
ficheiros novos, por serem untracked. Refiz tudo.

O gesto vinha da missão anterior, onde ele é o passo final **legítimo** da
cadeia do mapa — mas lá corre *depois* do commit.

```
    O MESMO COMANDO É HIGIENE DEPOIS DO COMMIT
    E DESTRUIÇÃO ANTES DELE.
```

Regra que fica: commitar antes de limpar; e, numa missão longa, commitar o
trabalho verde assim que ele está verde, em vez de o acumular na árvore.

## 72.8 · E A CADEIA DO MAPA MEDE O ÍNDICE

Corri a cadeia antes do `git add`, e os três ficheiros novos ainda não
estavam no índice. O mapa nasceu a medir 1495 ficheiros quando a árvore já
tinha 1498, e o validador apanhou-o. A ordem é:

```
git add  →  correr a cadeia  →  git add  →  commit  →  validar
```

## 72.9 · CONSEQUÊNCIA

```
ETAPAS_QUE_FALAM  RAW · DERIVED · STRUCTURED · ADMISSION   (era 3)
ETAPAS_MUDAS      READY                                     (é G-READY-01)
BLOCKERS          3 → 2
FILA              1. C-CLOSE-THE-READY-EDGE-V1
MUTAÇÃO           14 mutantes · 0 sobreviventes
```

`G-TEL-01` continua dívida declarada, e de propósito: a política para quando
a **própria telemetria** falha foi MEDIDA e preservada — a exceção sobe, e o
bruto preservado fica. Inventar política nova aqui faria uma falha de
telemetria passar por falha de RAW, e elas não são a mesma coisa.

O que isto continua a **não** provar: produção, e READY. A estrada continua a
acabar na ADMISSION.

---

# §73 · UMA FERRAMENTA QUE RECUSA TUDO O QUE AINDA NÃO PROVOU FAZ NASCER TODA CAPACIDADE NOVA FORA DELA

**Missão:** `C10.7 — ENSAIO CANÔNICO DE CAPACIDADE`
**HEAD final:** `27ceddcf`
**Tocado:** `coleta/scrap_executor.py` (e mais nada de código)

## 73.1 · O CICLO, E POR QUE ELE SE FECHA SOZINHO

O SCRAP tinha uma regra certa: uma capacidade que nunca foi provada não promete
resultado, e o `CHECK` recusa-a. Isso protege a produção de adaptadores que
existem e fingem.

Só que a regra, sozinha, fecha um ciclo:

```
NOT_EXECUTED
  → o CHECK recusa
  → para deixar de o ser, tem de correr uma vez
  → corre por um script lateral
  → alguém «integra»
  → nasce um bypass.
```

Não é um risco teórico, e é isso que torna a lei útil. Duas capacidades estavam
presas nele com adaptador ligado e política permitida. E o script lateral já
existia: o `piloto` do `social_scrap.py`, que uma missão anterior mediu a chamar
o roteador sem passar pelo boundary, **é** o produto deste ciclo.

```
    TODA REGRA QUE SÓ SABE DIZER «AINDA NÃO» PRECISA DE UM CAMINHO
    CANÓNICO PARA DEIXAR DE O DIZER. SENÃO ALGUÉM ABRE UM.
```

## 73.2 · A CURA É UM TERCEIRO EIXO, NÃO UMA EXCEÇÃO

A tentação é uma flag de exceção — `allow_unproven`, `force`, `override`. Todas
elas têm o mesmo defeito: são uma autorização, e uma autorização acaba
concedida por conveniência.

O que faltava não era permissão, era uma **pergunta diferente**:

```
NORMAL   «vou colher, e espero resultado»
TRIAL    «vou MEDIR se consigo, e NÃO espero resultado»
```

E a regra que mantém isto honesto é uma só:

```
    A ÚNICA DIFERENÇA ENTRE OS DOIS MODOS É O PORTÃO EPISTEMOLÓGICO.
```

Política, roteamento, adaptador, fornecedor, gasto e taxonomia de falha são os
mesmos objetos, chamados pelas mesmas linhas. No dia em que o modo decidir uma
segunda coisa — uma rota, um fornecedor, um gasto — deixou de ser um modo e
passou a ser um segundo runtime. Uma sentinela lê todas as comparações com o
modo e recusa que apareça `ROTA`, `provider`, `pago` ou `CLASSE` ao lado.

## 73.3 · DUAS PERGUNTAS NÃO PODEM DAR A MESMA RESPOSTA

O `CHECK` devolvia `CAN`. Com dois modos, `CAN = True` passaria a querer dizer
duas coisas conforme quem perguntou — e quem lê o veredicto não sabe quem
perguntou.

```
PRODUCTION_READY   dá para colher a sério, com direito a esperar objeto
TRIAL_ELIGIBLE     dá para medir uma vez, sem direito a esperar nada
```

Os dois vêm **sempre**, nos dois modos.

```
    UM `CAN = True` QUE NÃO DIGA QUAL DOS DOIS
    MENTE PARA METADE DE QUEM O LÊ.
```

E o padrão do parâmetro é o modo restritivo. Uma assinatura cujo default é o
modo permissivo é um atalho com outro nome, e há uma sentinela que lê a árvore
sintática para o garantir.

## 73.4 · UM ENSAIO QUE PROMOVE ESTADO É UMA MEDIÇÃO QUE SE AUTO-ASSINA

O ponto mais fácil de errar. O ensaio corre, devolve objetos, e é tentador
escrever `PROVEN` ali mesmo — afinal funcionou.

```
    TRIAL PASSADO != CAPACIDADE PROVADA.
    OFFLINE FIXTURE PASSADO != CAPACIDADE PROVADA AO VIVO.
```

Promover exige prova definida, artefato, evidência observada e um commit que se
lê. Três provas de que não promoveu, e a terceira é a que viaja:

- o ficheiro da declaração comparado por SHA antes e depois;
- uma sentinela que recusa que o executor ganhe sequer **como** escrever
  (`open(`, `write_text`, `json.dump`);
- `CAPABILITY_STATE_BEFORE == CAPABILITY_STATE_AFTER` **dentro do trace** — a
  prova dentro do próprio artefato, onde quem o ler daqui a um ano a encontra.

## 73.5 · MOCKAR O RUNTIME PROVA O MOCK

Para provar que o ensaio atravessa a casa toda, substituiu-se **um** objeto: a
chamada externa do fornecedor. Executor, roteador, registo e adaptador correram
a sério, com as linhas de produção.

```
    MOCKAR O RUNTIME PROVA O MOCK. MOCKAR A PORTA EXTERNA PROVA O RUNTIME.
```

E a prova conta quem foi tocado — roteador, adaptador, fornecedor falso — em vez
de assumir que foram. Uma prova que não conta as passagens prova que não rebentou.

## 73.6 · UM ESTADO QUE DIZ DUAS COISAS NÃO PODE SER LIDO COMO SE DISSESSE UMA

`BLOCKED` ficou de fora do ensaio, e a razão não é cautela: é um achado.

A prova que escreve `BLOCKED` numa capacidade desta casa mediu **uma rota**, a
partir de **um host**, e arruma-se numa tabela intitulada «o que só o runner
local pode fechar». A política, ao lado, declara a mesma capacidade permitida
por duas **outras** rotas.

```
    `BLOCKED` NA CAPACIDADE ESTÁ A DESCREVER UMA ROTA NUM AMBIENTE.
```

Registado como `CAPABILITY_ROUTE_STATE_CONFLATION = YES` e **não corrigido**:
separar os eixos muda a declaração de cinco capacidades e é ato de quem mede.
O que se fez foi impedir que o ensaio leia o estado misturado como se estivesse
limpo. Corrigir de passagem seria reescrever medição por lógica.

## 73.7 · E O DEFEITO QUE SÓ APARECE QUANDO SE MEXE

Ao expor os eixos na introspecção, apareceu que `CAPABILITIES()` respondia
`HAS_ROUTE` perguntando só por um dos dois papéis que um adaptador pode ter
(`executa=`, mas não `rota=`). Onze das catorze capacidades ligadas apareciam
sem rota — enquanto o `CHECK`, na linha ao lado, dizia que podiam colher agora.

```
    DUAS RESPOSTAS PARA A MESMA PERGUNTA SÃO DOIS DONOS.
```

A função existia e era do registo. Passou a delegar. 11 divergências → 0.

## 73.8 · UMA SONDA QUE MEDE FICHEIROS NÃO VÊ UMA FUNÇÃO

O ataque que procura scripts laterais media por ficheiro: excluía um módulo
inteiro por ele importar o executor nalgum sítio, e acusava o próprio executor,
que não se importa a si mesmo. Medido por **função**, passou a ver o `piloto` —
o lateral real que existe, e que esta missão estava proibida de resolver.

```
    UMA SONDA QUE MEDE FICHEIROS NÃO VÊ UMA FUNÇÃO.
```

## 73.9 · CONSEQUÊNCIA

```
FOUND_EXISTING_MECHANISM = NO   (procurado por 14 palavras antes de criar)
PRODUCTION_BEHAVIOR_CHANGED = NO
STATE_PROMOTED = NO · NETWORK_REAL = 0 · PAID_RUNS = 0
MUTANTES 10 · SURVIVORS 0 · ATAQUES 28 · NEW_FAILURES 0
```

Duas capacidades deixaram de estar presas e continuam `NOT_EXECUTED` — que é a
verdade, porque o que se provou foi o caminho, com fornecedor falso.

```
    CAN DO != DID DO.
```

---

# §74 · UMA MORADA ESCOLHIDA EM SILÊNCIO É UMA QUE NINGUÉM PODE DISCUTIR DEPOIS

A missão `C-CLOSE-THE-READY-EDGE-V1` pedia para fechar os dois últimos
blockers da Collection. Ela mediu, encontrou uma decisão por tomar, e parou.
Isto é o registo de por que parar foi o trabalho, e não a falta dele.

## 74.1 · O QUE NÃO FALTAVA

```
CONTRATO   COL-LAW-043, 11 campos fixos
DONO       admissao.pronto_para_inteligencia(), e é o ÚNICO construtor
ENTRADA    `item` + `Decisao` — e `rota_forward_documento.admitir()` já os
           tem em mãos, montados, no sítio certo
```

`G-READY-01` («READY não é produzido por nenhuma rota») não precisa de
contrato novo nem de tradutor novo. A ligação que falta é **uma chamada**.

## 74.2 · O QUE FALTAVA ERA UMA MORADA, E A LEI NÃO ESCOLHE

```
COL-LAW-043   fixa os 11 campos · CALA-SE sobre onde a unidade pousa
COL-LAW-044   ONDE ESTÁ: Supabase · git · data/raw · data/samples
```

A lei lista ficheiro **e** banco como armazenamento legítimo. Não há contrato
para consultar: há uma escolha por fazer.

## 74.3 · A CORREÇÃO QUE MUDOU A DECISÃO A MEIO

Eu ia declarar que a morada declarada no mapa — `data/samples/
PRONTO-PARA-INTELIGENCIA/<RUN_ID>.json` — «não tem escritor».

**Tem.** `orquestrador/orquestrador.py` decide, escreve o livro da porta,
chama o dono do READY por cada `SIM` e grava o ficheiro da corrida. A pasta
não existe porque nenhuma corrida daquele caminho produziu aceites.

```
    DESTINO VAZIO != DESTINO SEM DONO.
```

Isto não é um detalhe: muda a decisão. A saída «ficheiro» deixa de ser
hipótese e passa a ser implementação existente — e «criar uma tabela ao lado»
passa a ser um **segundo dono da mesma espera**, que é precisamente o que
`ONE CONCEPT → ONE OWNER` proíbe.

## 74.4 · AS DUAS SAÍDAS, E POR QUE NENHUMA É ÓBVIA

**(A) a rota forward usa a morada que já existe.** Um dono, zero migrations,
`G-READY-01` fecha por uma chamada. Mas a espera continua em ficheiro: sem
chave estrangeira, sem unicidade, sem transação. A missão pedia concorrência
e crash/retry **provados em PostgreSQL** — e com ficheiro não se provam.

**(B) a sala de espera ganha tabela (migration 029).** Suporta unicidade e
concorrência reais, e põe a espera ao lado das outras etapas. Mas passam a
existir duas moradas para a mesma espera, e retirar a do orquestrador muda um
caminho que não é destes dois blockers. E há um segundo fio: a decisão de
admissão **não tem linha nenhuma** — o dono escreve num livro JSON e `Decisao`
não carrega surrogate. Ou READY se liga a ela por chave natural, ou a
ADMISSION ganha armazenamento, e isso é `G-ADM-01`: dívida de **outro** portão.

```
    DUAS SAÍDAS LEGÍTIMAS COM CONSEQUÊNCIAS DIFERENTES
    NÃO SÃO UM DETALHE DE IMPLEMENTAÇÃO. SÃO UMA DECISÃO.
```

E o repositório já tinha dito isto, antes da missão, em
`provas/a_fronteira_da_coleta.py`: «São duas coisas, e ligá-las é uma DECISÃO
DE ARQUITETURA — não um remendo de código.»

## 74.5 · DUAS LIÇÕES, E AS DUAS SÃO A MESMA

Ambas nasceram de eu ler **texto** onde a pergunta era de **estrutura**.

**Procurar a palavra acusou o inocente.** A medição procurava a string
`PRONTO_PARA_INTELIGENCIA` nos ficheiros e concluiu que o orquestrador era um
segundo construtor do registo READY. Ele escreve aquele texto como `ESTADO` de
um recibo, e **chama** o dono.

```
    MENCIONAR UM CONTRATO NÃO É IMPLEMENTÁ-LO.
    E A DIFERENÇA SÓ SE VÊ NA ESTRUTURA, NUNCA NO TEXTO.
```

Por AST — quem devolve um dicionário com os 11 campos da lei — o orquestrador
sai da lista sozinho. É a mesma família do defeito de §60 e do medidor de §72.

**E a medição aceitava casos que não comparavam nada.** Dois mutantes
sobreviveram trocando a condição de um caso por `True`, ou por
`True or <a condição>`. Nada reprovava, porque a resposta certa já era «sim».

```
    UM CASO QUE PASSA MESMO SEM COMPARAR NADA
    NÃO É UMA MEDIÇÃO: É UMA AFIRMAÇÃO.
```

A guarda que fecha isto não confere o valor de cada caso — confere que cada um
ainda **faz uma pergunta**: nenhuma condição é constante, e nenhuma começa por
uma constante que a curto-circuite. É finita, e mata as duas formas.

## 74.6 · CONSEQUÊNCIA

```
G-READY-01  BLOCKER  (remedido neste HEAD)
G-READY-02  BLOCKER  (remedido neste HEAD)
COLLECTION_CORE_CLOSE = FAIL · 1 missão até fechar
MUTAÇÃO  6 mutantes · 0 sobreviventes
```

Nenhuma migration criada. Nenhuma tabela criada. Nada fechado.

O que fica é a pergunta, posta de maneira que custe pouco a responder: **onde
pousa a unidade pronta da rota forward?** Respondida essa, o resto é a chamada
que já estava à espera.

---

# §75 · UM TRANSPORTE QUE CAIU NÃO É UMA POLÍTICA QUE RECUSOU

**Missão:** `C10.8A — PRIMEIRO TRIAL AO VIVO (BLUESKY)`
**HEAD final:** `509d2b59`
**Tocado:** `coleta/scrap_http.py` · `coleta/social_rotas.py` ·
`coleta/scrap_capacidades.py` (promoção, em commit próprio)

## 75.1 · O ACHADO QUE SÓ APARECE AO VIVO

A C10.7 provou o ensaio canônico com fornecedor falso e passou. A primeira
corrida real, contra o Bluesky, falhou — e falhou de uma maneira que nenhuma
fixture teria produzido.

O túnel morreu a meio da leitura do `robots.txt`. O portão tinha três
respostas — `LIDO`, `AUSENTE`, `ILEGIVEL` — e um `except Exception` varria para
`ILEGIVEL` tanto «o host respondeu uma coisa que não sei ler» como «o host não
respondeu de todo». `permitido()` traduz `ILEGIVEL` para `False`, e o roteador
traduz isso para `ROUTE_NOT_ALLOWED`.

O `robots.txt` daquele host, lido logo a seguir, diz `Allow: /` e escreve, por
extenso, que rastrear a API pública é permitido.

```
    UM TRANSPORTE QUE CAIU NÃO É UMA POLÍTICA QUE RECUSOU.
```

A recusa em si estava certa: não se afirma permissão que não se leu. O que
estava errado era o **nome** dela, e o nome é o que a casa obedece:

```
ROUTE_NOT_ALLOWED        recuperação = NO_RETRY
TRANSIENT_NETWORK_ERROR  recuperação = WAIT
```

Chamar a segunda pela primeira ensina a casa a desistir de uma porta aberta —
e a desistir em silêncio, porque `NO_RETRY` não reclama.

A correção tem duas metades, e a segunda esquece-se: um estado próprio para «não
consegui ler», **e** não memorizar esse estado. Guardar «indisponível» em cache
faria um soluço de rede virar proibição permanente até ao fim do processo.

## 75.2 · O QUE UMA PROVA AO VIVO CUSTA QUANDO A SONDA ESTÁ ERRADA

O briefing fixou o teto em duas requisições. Foram sete, em quatro tentativas.
Três excessos foram defeitos da minha própria sonda, não da ferramenta:

- ela assumiu que `RAW_REFERENCE` era uma string, e rebentou com `TypeError`
  **depois** de a chamada real ter corrido e trazido o objeto;
- o ensaio a seco, feito a seguir para validar, escreveu por cima do registo da
  corrida real.

```
    UMA PROVA QUE SÓ SE TESTA AO VIVO TESTA-SE À CUSTA DO HOST.
    UM ENSAIO A SECO QUE ESCREVE POR CIMA DA CORRIDA REAL APAGA A PROVA.
    UMA SONDA QUE ASSUME A FORMA DO CAMPO MEDE A ASSUNÇÃO.
```

A regra que saiu daí, e que vale para qualquer prova que vá tocar em algo caro:
**ela tem de ter um modo que corra o corpo inteiro contra bytes preservados,
com a rede trancada, antes de haver um único pedido.** E o registo da corrida
real escreve-se **antes** de qualquer asserção poder rebentar.

```
    UMA CHAMADA REAL QUE NÃO DEIXOU REGISTO CUSTOU A REDE E NÃO COMPROU NADA.
```

## 75.3 · O TETO CONTA TUDO O QUE SAI

O portão do `robots.txt` é uma ida à rede como qualquer outra. Não contá-lo para
o teto seria a mesma contabilidade que esta casa recusa noutros sítios.

```
    UM PEDIDO QUE NÃO CONTA PARA O TETO CONTA PARA O HOST.
    UM TETO QUE NÃO RECUSA NÃO É UM TETO.
```

O teto foi implementado a embrulhar o transporte: a requisição seguinte ao teto
**levanta**. E isso teve de ganhar sentinela de comportamento, porque a
primeira que existia procurava a palavra `TetoEstourado` no ficheiro — e um
`if False:` à frente do `raise` deixa a palavra lá.

```
    UMA SENTINELA QUE PROCURA A PALAVRA NÃO MEDE O QUE ELA FAZ.
```

## 75.4 · QUEM PROMOVE É A EVIDÊNCIA, LIDA

O `TRIAL` correu, trouxe um objeto real e **não** promoveu nada: o ficheiro da
declaração foi comparado por SHA antes e depois, e o trace carrega
`BEFORE == AFTER`. A promoção de `NOT_EXECUTED` para `PROVEN` foi um commit
separado, depois de a evidência existir e poder ser lida.

```
    TRIAL PASSADO NÃO PROMOVE. QUEM PROMOVE É A EVIDÊNCIA, LIDA.
```

E a prova citada na declaração passou a apontar para o artefato da corrida **ao
vivo** — não para a matriz, nem para a prova offline da missão anterior. Uma
capacidade promovida que cita uma fixture está a dizer que correu quando não
correu.

## 75.5 · A PROVA QUE FALHA POR TER FUNCIONADO

Depois da promoção, a prova ficou vermelha. Ela exigia `NOT_EXECUTED` como
pré-condição — o estado que ela própria fez mudar.

```
    UMA PROVA QUE EXIGE O ESTADO DE ONTEM FALHA POR TER SIDO BEM-SUCEDIDA.
```

Uma prova de trânsito de estado não pode exigir o estado de partida para
sempre. O que ela mede a partir daí é a **coerência**: ou a capacidade ainda não
promete e o `CHECK` normal recusa, ou ela já promete e a prova citada aponta
para o artefato desta corrida. O momento histórico guarda-se num artefato, que
é onde um momento se guarda.

## 75.6 · O ALVO TAMBÉM SE PROVA

Um alvo escolhido na internet é um alvo que ninguém pode discutir depois. O
desta corrida veio do RAW preservado de uma descoberta canônica anterior,
commitado, com o termo que a própria casa declara. Sete contas voltaram; usou-se
a única com nome de organização.

```
    UMA SENTINELA NÃO DEVE SER A CONTA PESSOAL DE NINGUÉM.
```

## 75.7 · CONSEQUÊNCIA

```
bluesky.author.incremental   NOT_EXECUTED → PROVEN
2 requisições · 1 objeto · 2 555 bytes de RAW com SHA · COST_USD = 0
MUTANTES 10 · SURVIVORS 0 · ATAQUES 24 · rede no red team = 0
```

E o que `PROVEN` **não** afirma: um objeto, uma conta, `limit=1`. Não se mediu
volume, paginação, janela nem `429`. `PROVEN` nesta casa quer dizer «correu e
ficou registado».

```
    CAN DO != DID DO.
```

---

# §76 · A COLETA ACABA NA SALA DE ESPERA — E A ESCOLHA DA MORADA FOI FEITA

`§74` deixou uma pergunta aberta de propósito: **onde pousa a unidade pronta?**
A resposta veio de gente, e é a **saída A** — o sistema de ficheiros, na morada
que já existia. Está versionada em `docs/decisoes/ADR-SALA-DE-ESPERA-V1.md`.

Com ela, `G-READY-01` e `G-READY-02` fecharam. Eram os dois últimos blockers.

## 76.1 · O QUE FALTAVA NÃO ERA O CONTRATO

`admissao.pronto_para_inteligencia()` já era o único construtor, com os 11
campos da `COL-LAW-043`. Faltavam duas coisas, e nenhuma era o contrato.

**A escrita estava no plano errado.** `orquestrador/orquestrador.py` gravava o
ficheiro directamente, e a `COL-LAW-012` diz que o orquestrador **controla**,
não transporta dado. Enquanto a única escrita estivesse no control plane, a
rota forward não tinha como pousar a unidade sem escrever uma **segunda**.

```
    ONE CONCEPT → ONE OWNER.
```

O corpo mudou de casa para `admissao/sala_de_espera.py` — não foi
reimplementado — e ganhou as travas que um ficheiro exige e que nunca teve:
escrita atómica por troca (`fsync` e depois `os.replace`), retry idempotente
(`REUSED`), conflito explícito (`RUN_ID_CONFLICT`, nome que já tinha dono), e
uma trava **por corrida** — duas corridas diferentes escrevem ao mesmo tempo;
a mesma, não.

```
    UMA RUN_ID NÃO PODE CONTAR DUAS HISTÓRIAS.
```

## 76.2 · E O ESTÁGIO NÃO VIAJAVA ATÉ À PORTA

Este é o achado que fazia `G-READY-01` parecer maior do que era.

A porta pergunta o **estágio** do item (`COL-LAW-502`) e lê-o em
`artifact_type`. A rota forward só lhe passava `SOURCE_ID` — então todo
documento chegava como `ESTAGIO_DESCONHECIDO`, e a um desconhecido pergunta-se
o **tempo do fato**, que um documento não tem.

```
    36 de 36 documentos reais respondiam NAO_SEI em «tempo do fato».
    A PORTA ESTAVA CERTA. A PERGUNTA É QUE ERA A ERRADA.
```

`ingresso.DA_FICHA_PARA_A_PORTA` já declarava os três campos que viajam da
ficha para a porta. Nada foi inventado: declarou-se o que a rota **já sabia** —
a unidade que chega à ADMISSION nasceu de um `derived_artifact`. Com o estágio
a viajar, 29 de 43 textos derivados reais respondem `SIM` em T3.

```
    UM CAMPO QUE NÃO VIAJA NÃO É UM CAMPO EM FALTA:
    É UMA RESPOSTA ERRADA DADA COM CONFIANÇA.
```

É a mesma família do `SOURCE_ID` de `§60`. Duas vezes o mesmo defeito, em dois
campos diferentes, no mesmo trajecto.

## 76.3 · ZERO BLOCKERS NÃO É CORE FECHADO

Fechados os dois, a fila mínima esvaziou-se. E `COLLECTION_CORE_CLOSE`
continua **FAIL** — agora por outra razão, e o artefacto passou a dizê-la:

```
BLOQUEADO_POR = []
PORQUE        = CANONICAL_E2E não está provado
```

Não há buraco declarado por tapar. Falta a **cabeça** da estrada: `REQUEST`,
`ORCHESTRATOR`, `EXECUTOR` e `RUN` continuam sem corrida observada.

```
    ZERO BLOCKERS ≠ CORE FECHADO.
    O VEREDITO VEM DAS PROPRIEDADES, E NÃO DA CONTAGEM DE BURACOS.
```

Uma fila vazia ao lado de um FAIL é o retrato honesto. Inventar uma missão só
para a fila não ficar vazia seria fabricar dívida; esconder o FAIL seria pior.

## 76.4 · E A LIÇÃO ESCRITA QUE EU NÃO TINHA APLICADO

Quatro mutantes que impediam a unidade de pousar faziam a prova levantar
`KeyError` a meio, e ela morria sem veredito. É exactamente `§72.5`, escrita
por mim, duas missões antes.

```
    UMA LIÇÃO ESCRITA E NÃO APLICADA
    É O MESMO QUE UMA LIÇÃO NÃO ESCRITA.
```

A partir daqui, toda prova nova nasce com o fecho defensivo: sem o objecto que
ela mede, os casos que dependem dele **reprovam com nome** em vez de rebentar.

## 76.5 · DOIS TESTES QUE MUDARAM DE LADO, E É O NORMAL

Ambos estavam certos quando foram escritos:

- um exigia que o **orquestrador** gravasse o ficheiro — era essa medição que
  provava `DESTINO VAZIO ≠ DESTINO SEM DONO`;
- outro exigia que `READY` **não** falasse no rastro — ninguém o emitia.

Nenhum foi apagado. Os dois passaram a guardar o mesmo facto no dono novo, e
dizem no corpo por que mudaram. Um gap que fecha fica na lista com o estado
novo; um teste que o guardava muda de lado com a razão à vista.

## 76.6 · CONSEQUÊNCIA

```
G-READY-01   BLOCKER → CLOSED
G-READY-02   BLOCKER → CLOSED
BLOCKERS     2 → 0
ESTRADA      RAW · DERIVED · STRUCTURED · ADMISSION · READY · SALA DE ESPERA
ETAPAS MUDAS []
MUTAÇÃO      11 mutantes · 0 sobreviventes
```

Zero **consumidores** da sala continua a ser o estado certo: a Intelligence é
outra missão, e criar um consumidor agora só para a sala parecer ligada seria
ligar uma ponta a nada.

O backend não está fechado para sempre: `WAITING_ROOM_V1_BACKEND = FILESYSTEM`,
`BACKEND_CHANGE_ALLOWED_LATER = YES`. A `COL-LAW-044` garante que trocar o meio
não redefine o estado — e porque o dono é um só, a troca é uma mudança dentro
de `admissao/sala_de_espera.py`, e não uma reescrita de quem o chama.

---

# §77 · UM TETO QUE VIVE NA PROVA MEDE A PROVA

**Missão:** `C10.8A-R — O TETO DE ACESSOS EXTERNOS`
**HEAD final:** `9c720dfe`
**Tocado:** `coleta/scrap_http.py` · `coleta/scrap_executor.py` ·
`coleta/social_rotas.py` · `provas/orcamento_de_rede.py` ·
`provas/bluesky_trial_ao_vivo.py`

`§75` registou a cicatriz: a C10.8A declarou duas requisições e fez sete. O que
essa secção ainda não podia dizer é **por que** o teto não segurou, e o que foi
preciso para que segure.

## 77.1 · A MISSÃO QUE MEDIU O PRÓPRIO EXCESSO E SE DEU PASS

O teto existia. Vivia numa constante de um script de prova, e a prova rebentou a
meio e teve de ser repetida — o teto repetiu-se com ela, zerado. Nenhuma
requisição foi recusada por ele, porque ele nunca teve como recusar nada.

```
    UM TETO QUE VIVE NA PROVA MEDE A PROVA.
    DECLARED BUDGET != ENFORCED BUDGET.
```

E o veredito da missão, escrito por mim, contou as sete idas no corpo do
documento e assinou `PASS_PROVEN` no topo.

```
    UMA MISSÃO QUE MEDE O PRÓPRIO EXCESSO E SE DÁ PASS
    TRANSFORMOU O GATE NUM COMENTÁRIO.
```

A correcção tem duas metades, e trocar uma pela outra estraga as duas. O
veredito da missão passou a `FAIL`. A capacidade **não** foi rebaixada: houve
rede real, `HTTP 200`, objeto real, RAW com SHA lido de volta. E a contagem das
sete idas ficou onde estava, no §11 do documento antigo.

```
    MISSÃO FALHOU O PROTOCOLO != CAPACIDADE NÃO FOI PROVADA.
    CORRIGIR O VEREDITO NÃO É APAGAR O FACTO.
```

Reescrever o documento para o excesso desaparecer teria feito a única coisa pior
do que o excesso: destruir a medição que o revelou.

## 77.2 · O CENSO DECIDE ONDE O TETO VIVE — NÃO O ORGANOGRAMA

O sítio óbvio para contar era `scrap_http.buscar`: é o transporte **nomeado**
desta casa. O censo mediu por onde as catorze capacidades ligadas saem de
verdade, e o óbvio estava errado:

```
scrap_http.buscar          5 capacidades
reel_transcricao.baixar    3      ← não passa por lá
cdp.abas / cdp._handshake  1      ← não passa por lá
youtube_oficial._http      5      ← não passa por lá
25 funções da casa abrem ligação directamente
```

```
    UM TETO QUE COBRE METADE DAS PORTAS NÃO É UM TETO. É UMA SUGESTÃO.
```

O único sítio que **todas** atravessam são duas primitivas do Python:
`urllib.request.urlopen` e `socket.create_connection`. É aí que se cobra.

O dono do conceito continua a ser `coleta/scrap_http.py` — isso é `ONE CONCEPT →
ONE OWNER` e não se negoceia. Mas o dono do conceito e o ponto de cobrança não
têm de ser a mesma linha de código:

```
    QUEM É DONO DA IDEIA DECLARA-A.
    QUEM VÊ A LIGAÇÃO ABRIR É QUEM A COBRA.
```

Há uma armadilha nessa escolha: um `urlopen` chama `create_connection` por
baixo. Sem profundidade de reentrância, **uma** ida à rede é cobrada **duas**
vezes, e o teto fecha a meio de um pedido legítimo. Um contador colocado numa
primitiva tem de saber que a outra está por baixo dele.

## 77.3 · O CONTADOR É DA EXECUÇÃO, NÃO DO PROCESSO

Um contador global de processo faz a segunda execução herdar a despesa da
primeira, e faz um teste envenenar o seguinte. O orçamento vive em
`threading.local`, nasce no `with` e morre nele.

```
    UM ORÇAMENTO DE PROCESSO PAGA A CONTA DE OUTRA EXECUÇÃO.
```

E sem `teto_de_rede` nada acontece: produção corre exactamente como antes, e o
rasto não inventa números de um teto que ninguém pediu. Um mecanismo novo que
muda o comportamento de quem não o pediu é uma mudança escondida numa
ferramenta.

## 77.4 · OS DOIS EIXOS DA RETENTATIVA

`leis/falhas.py` responde a uma pergunta, e só a uma:

```
    FAILURE POLICY decide se a retentativa ADIANTA.
    NETWORK BUDGET decide se a retentativa CABE.
```

São perguntas diferentes, e uma não responde pela outra: um `WAIT` de uma falha
transitória continua a ser o conselho certo com o teto a zero — e continua a não
poder acontecer.

A medição honesta é que **não existe ciclo de retentativa nenhum no SCRAP**.
`RECOVERY_ACTION` é escrito e não é lido por ninguém no caminho de aquisição.

```
    UMA POLÍTICA QUE NINGUÉM EXECUTA NÃO É UM COMPORTAMENTO.
```

Por isso o eixo da retentativa está provado como **contrato**, e o documento
di-lo por extenso, em vez de exibir uma tabela de retentativas que na verdade
mede chamadas ordinárias. Quando alguém escrever o ciclo, os dois têm de dizer
sim antes do socket.

O mesmo vale para o outro par, que a C10.8B vai precisar:

```
    GRÁTIS EM DÓLAR != GRÁTIS EM REQUESTS.
    PAID BUDGET != NETWORK BUDGET.
```

`permitir_pago=True` com motivo canônico não aumenta o teto de rede — medido. E
a classe do orçamento não conhece a palavra `USD`.

## 77.5 · SEGUNDA VEZ: A NOSSA RECUSA VESTIDA DE RECUSA DA FONTE

Assim que o teto passou a levantar, a recusa dele apareceu no executor como
`BLOCKED`. O `except Exception` de `buscar` traduzia tudo para `RotaBloqueada`.

```
    ESGOTAR O ORÇAMENTO NÃO É A PLATAFORMA IMPEDIR.
```

`§75.1` conta a primeira ocorrência: um túnel caído a sair como
`ROUTE_NOT_ALLOWED`. Esta é a mesma família, do outro lado — lá era a rede a
levar a culpa da política, aqui é a fonte a levar a culpa da nossa própria
decisão. Duas vezes na mesma cadeia chega para ser lei:

```
    UM `except Exception` LARGO NÃO DISTINGUE QUEM DISSE NÃO.
```

O padrão que sai daqui: **uma recusa nossa atravessa os `except` largos inteira**.
Ela é relançada antes de qualquer tradução, em cada camada que a apanhe, e chega
com nome próprio — `NETWORK_BUDGET_EXHAUSTED`, não `BLOCKED`.

E a recusa fica no rasto como tentativa, com `COUNTED = False` e
`OUTCOME = REFUSED_BY_BUDGET`. Recusar em silêncio faria a execução parecer que
nunca quis sair.

## 77.6 · MUDAR O SÍTIO DO CORPO MUDA O QUE AS SENTINELAS VEEM

Para embrulhar o `COLLECT` no orçamento, a primeira tentativa partiu-o em
`COLLECT` + `_collect`. Comportamento idêntico, quatro sentinelas da C10.6C a
vermelho: elas lêem o **corpo** da fronteira para provar que a ordem das etapas
não mudou, e o corpo tinha mudado de casa.

```
    UMA REFATORAÇÃO QUE MUDA O SÍTIO DO CORPO
    MUDA O QUE AS SENTINELAS VEEM.
```

As sentinelas estavam certas e o refactor é que estava errado. Um decorador
(`@_com_teto_de_rede`) faz o mesmo trabalho e deixa o corpo onde estava. Onde
existem sentinelas estruturais, a forma do ficheiro é interface — e move-se com
a mesma cerimónia que uma assinatura pública.

## 77.7 · E A PROVA MEDE-SE CONTRA UM CONTADOR QUE NÃO É O DELA

```
    UM TETO QUE SE MEDE A SI PRÓPRIO MEDE O ESPELHO.
```

O transporte falso entra **por baixo** do teto e conta o que realmente saiu pelo
socket. O número do runtime é comparado com o número do transporte. E o harness
da C10.8A passou a declarar `teto_de_rede=MAX_PEDIDOS` ao `COLLECT`: o contador
local dele deixou de ser o teto e passou a ser o conferente.

## 77.8 · CONSEQUÊNCIA

```
C10.8A  PASS_PROVEN → FAIL          (as 7 idas continuam escritas)
bluesky.author.incremental          PROVEN, intocado
teto    urlopen + create_connection · por execução · gate antes do socket
NETWORK_CALL_N_PLUS_1 = 0
MUTANTES 12 · SURVIVORS 0 · ATAQUES 28 · rede real 0 · COST_USD 0
```

Fica por saber o comportamento sob retentativa real, porque o ciclo não existe;
e fica por saber se algum caminho futuro abrirá ligação por uma primitiva que
não seja nenhuma das duas. Hoje as vinte e cinco portas usam uma delas.

---

# §78 · DUAS METADES PROVADAS NÃO SÃO UMA ESTRADA PROVADA

A pergunta era uma só: um pedido canónico atravessa hoje a máquina real, de
`REQUEST` a `SALA DE ESPERA`, numa mesma história? A resposta é **não**, e
agora sabe-se onde e porquê.

## 78.1 · O BOTÃO FOI APERTADO NO SÍTIO CERTO

Todas as provas anteriores começavam no meio: no `raw_asset` já preservado, ou
chamando `atravessar()` directamente.

```
    UMA PROVA QUE COMEÇA PELO MEIO NÃO PROVA A ESTRADA:
    PROVA O PEDAÇO POR ONDE ELA COMEÇOU.
```

`provas/o_pedido_atravessa.py` entra por `orquestrador.correr(Pedido)` — o
único ponto de entrada canónico — e o executor é o **real**, a ir à fonte
**real**. Um executor de mentira provaria o orquestrador, não a aquisição.

O livro append-only, o livro da porta e a Sala de Espera ficam em moradas
descartáveis (`ITALY_OPS_ROOT`, `admissao.LIVRO`, `espera.MORADA`).

## 78.2 · A CABEÇA DA ESTRADA ATRAVESSA

Isto foi a surpresa boa, e estava listada como o défice:

```
REQUEST        Pedido T2 · fonte IT-T2-002
ORCHESTRATOR   receita `italia-recorrente` · RUN_ID cunhado antes de correr
EXECUTOR       coleta/italy_executor.py na ARPAV real · 4 itens
RUN            collection_run = 1 · concluída
RAW            raw_asset = 4, todas desta corrida
STORAGE        4 storage_object ligados às 4 observações
```

`CAN DO ≠ DID DO` fica provado do lado bom: não é que os módulos existam — é
que o comando foi lançado, a versão do executor é o commit que lhe tocou, e a
colheita que ele largou está no banco.

## 78.3 · E PARTE-SE NO MEIO

```
FIRST_LOST_EDGE = STORAGE -> DERIVED
```

A rota do orquestrador vai de RAW/STORAGE **directo** à ADMISSION. A ADMISSION
corre — e responde `NAO_SEI` nos quatro, com razão: o item chega **sem texto**,
porque ninguém o derivou.

```
    UMA ETAPA QUE CORRE DEPOIS DO BURACO NÃO PROVA A ESTRADA:
    A HISTÓRIA JÁ ESTAVA PARTIDA ANTES DELA.
```

E a primeira versão da minha própria prova errou aqui: guardava a última etapa
observada da lista **inteira**, e dizia `ADMISSION -> DERIVED` — uma aresta ao
contrário, que mandaria procurar o defeito a jusante de onde ele está. O
primeiro buraco é o que explica os seguintes.

## 78.4 · E SÃO DUAS ESPÉCIES DE BURACO, NÃO UMA

Medido, e não deduzido:

- **`STORAGE → DERIVED` é ligação.** Corri `derivacao_forward` sobre o **mesmo**
  `raw_asset` daquela corrida: `PASS`. A capacidade existe; falta a chamada.
- **`DERIVED → STRUCTURED` é contrato sem dono.** `public.conteudo` exige
  `canal_id`, e `social_persistencia.exigir_canal` recusa dizendo, por escrito,
  que quem o resolve é «um dono de identidade, fora do executor de coleta».
  Esse dono **não existe**.

Por isso a missão parou de corrigir: a primeira é pequena, a segunda é decisão
de arquitectura. Ligar a primeira sem resolver a segunda moveria o buraco uma
aresta para a frente e chamar-lhe-ia progresso.

## 78.5 · O PORTÃO QUASE FECHOU POR UMA SOMA

Quando a cabeça da estrada passou a atravessar, as **onze** etapas ficaram
`FLOW_EXECUTED = YES` e `COLLECTION_CORE_CLOSE` deu **PASS**.

Era falso. As etapas atravessam em **duas estradas diferentes**: a do pedido
vai de RAW/STORAGE à ADMISSION; a forward faz DERIVED/STRUCTURED entrando pelo
RAW.

```
    DUAS METADES PROVADAS NÃO SÃO UMA ESTRADA PROVADA.
    ONZE ETAPAS QUE JÁ CORRERAM NÃO SÃO UMA HISTÓRIA.
```

O portão passou a exigir a **mesma história**, lida da medição que aperta o
botão no pedido — e diz onde ela parou. `NOT_MEASURED` conta como não-passa.

## 78.6 · E A MEDIÇÃO DEIXOU ACERVO NA ÁRVORE

Três sujidades, todas minhas, e todas com lei já escrita:

- quatro PDFs numa pasta `XX/` — a raiz que `ArmazemLocal` usa sem armazém
  próprio — **commitados** como se fossem acervo;
- dezasseis decisões de T2 no livro **real** da porta, também commitadas. Quem
  as apanhou foi um teste que já existia: «apareceu decisão de T2 no livro. T2
  não tem regra escrita»;
- e o livro descartável, quando o isolei, ficou **dentro** da sala — e passou a
  contar como ficheiro da espera.

```
    UMA MEDIÇÃO QUE SUJA A ÁRVORE
    É UMA MEDIÇÃO QUE A PRÓXIMA VAI MEDIR.
```

Toda prova que escreve tem de declarar as suas três moradas descartáveis antes
de correr: onde o coletor larga, onde a porta escreve o livro, onde a espera
pousa.

## 78.7 · E DOIS MUTANTES ENSINARAM O QUE FALTAVA

Seis sobreviveram na primeira ronda. Cinco eram casos que passam sem comparar
nada — a guarda de `§74.5`, que eu tinha escrito e **não apliquei aqui**. O
sexto foi um limiar que nenhum caso ultrapassava: `== 1` trocado por `>= 1`
num banco com **uma** corrida.

```
    UM LIMIAR SÓ ESTÁ TESTADO SE ALGUM CASO CAIR POR BAIXO DELE.
```

A regra da mesma história saiu para uma função usada duas vezes, e o caso
negativo corre uma **segunda corrida real**. Tentei primeiro inserir a linha à
mão e o banco recusou-a por falta de identidade — e estava certo:

```
    UMA BANCADA QUE FABRICA IDENTIDADE MEDE A FÁBRICA.
```

## 78.8 · CONSEQUÊNCIA

```
CANONICAL_E2E          FAIL
FIRST_LOST_EDGE        STORAGE -> DERIVED
ROOT_CAUSE             FUNCTIONAL_GAP (ligação) + CONTRACT_GAP (dono do canal)
COLLECTION_CORE_CLOSE  FAIL, por medição e não por contagem
MUTAÇÃO                10 mutantes · 0 sobreviventes
```

E uma correcção entrou, a única que era pequena, local e inequívoca: a corrida
canónica corria e **não deixava rasto nenhum** — 4 linhas em `raw_asset`, zero
em `etapa_da_corrida`. A etapa RAW já sabia falar; quem a chamava é que não lhe
dava onde. É a mesma família do defeito da `memoria`, na **mesma função**, com
o aviso já escrito à vista.

```
    UM PARÂMETRO OPCIONAL QUE NINGUÉM CONSEGUE PASSAR
    NÃO É OPCIONAL: É INEXISTENTE.
```

---

# §79 · UMA CONTAGEM QUE NÃO DIZ O QUE CONTA É UM NÚMERO, NÃO UMA MEDIÇÃO

**Missões:** `C-RECONCILE-SYSTEM-MAP-AS-OBSERVABILITY-SYSTEM-V1` ·
`C-DESIGN-SYSTEM-MAP-TRUST-CONTRACT-V1` ·
`C-IMPLEMENT-SYSTEM-MAP-ENTITY-SPECIES-G0-V1`
**Linha:** `claude/dazzling-cerf-27a7v2`
**Tocado:** `docs/arquitetura/SYSTEM-MAP-TRUST-CONTRACT.md` ·
`system-map/scripts/reconciliacao_do_universo.py` ·
`system-map/tests/test_reconciliacao_do_universo.py` · `AGENTS.md`

O System Map publicava três números com o mesmo nome. Fechá-los obrigou a
escrever o que ele pode afirmar, com que evidência — e a primeira coisa que esse
contrato apanhou foi o artefato que ele próprio usava como exemplo de boa prática.

## 79.1 · TRÊS CONTAGENS CERTAS QUE NÃO ERAM COMPARÁVEIS

```
65   a faixa visual   familia F-COLETA + F-ESPERA
48   o pente fino     TERRITORIO numa tupla fixa de nove zonas
111  o censo           a mesma familia MAIS o fecho por aresta
```

Nenhuma era falsa. Nenhuma declarava o seu universo, e por isso nenhuma era
comparável com a do lado.

```
    UMA FERRAMENTA DE OBSERVABILIDADE NÃO É COERENTE PORQUE CADA CENSO
    ESTÁ CERTO. É COERENTE QUANDO OS CENSOS CONSEGUEM RECONCILIAR
    OS PRÓPRIOS UNIVERSOS.
```

**PROVA.** Em `1766c232`, treze peças de `Z-GUARDA` mudaram de família `F-ESPERA`
para `F-COLETA`. A faixa visual foi de `49/13` para `62/1`; o pente fino não
mexeu uma peça, porque filtra por TERRITÓRIO. Uma reatribuição de família moveu
treze peças entre duas contagens publicadas e zero na terceira.

```
    FAMÍLIA != TERRITÓRIO. Trocar uma pela outra numa lente
    move números sem mover peças.
```

## 79.2 · MEDIR BEM E PUBLICAR A PALAVRA ERRADA

O erro mais caro não foi medir mal.

```
    658 arestas e 59 peças publicavam  status = PROVEN
    apoiadas SÓ em análise estática — e a medição estava certa em todas.
```

As razões que o mapa escreve dizem-no: *«provado por 1 linha de código»*, *«outra
peça importa isto»*. Todas provam que o código CONSEGUE. Nenhuma prova que
ACONTECEU.

```
    ANÁLISE ESTÁTICA PROVA CAN DO. SÓ TELEMETRIA PROVA DID DO.
    DECLARED → CODE → OBSERVED → PROVEN: nenhum implica o seguinte.
```

**PROVA.** Zero arestas têm evidência de runtime, e `OBSERVED` é
*irrepresentável*: o esquema de aresta não tem `RUN_ID`, `OBSERVED_AT` nem
`ENVIRONMENT`. Não há onde escrever uma observação, mesmo que alguém a medisse.

## 79.3 · UMA LINHA NÃO PROVA DUAS AFIRMAÇÕES DIFERENTES

```
coleta/comunicacao_coleta.py:57
  import apify_pool as ap

sustentava ao mesmo tempo:
  C-APIFY-POOL → C-COMUNICACAO   IMPORTS        ← a linha prova
  C-APIFY-POOL → V-FACEBOOK      ABRE_O_CANAL   ← não prova
  C-APIFY-POOL → V-INSTAGRAM     ABRE_O_CANAL   ← não prova
  C-APIFY-POOL → V-LINKEDIN      ABRE_O_CANAL   ← não prova
```

**PROVA.** Sobre 1162 linhas de evidência distintas: 55 usadas por mais de uma
aresta, 37 delas a sustentar tipos de relação diferentes, em 52 arestas.

```
    A EVIDÊNCIA TEM DE SUSTENTAR A AFIRMAÇÃO CONCRETA,
    NÃO APENAS TER RELAÇÃO COM O MÓDULO.
```

## 79.4 · UM CAMPO OBRIGATÓRIO SÓ ESCRITO EM CONTRATO NÃO ESTÁ PROTEGIDO

O contrato exigia `ENTITY_SPECIES` em toda contagem publicada. Duas missões
depois, medido: **zero de seis universos e zero de sete lentes** o publicavam.

```
    UM CAMPO OBRIGATÓRIO QUE NENHUMA PROVA EXIGE
    FICA POR ESCREVER, E NINGUÉM REPARA.
```

E não foi por distração: as duas missões anteriores NARRARAM as causas que
conheciam em vez de PERCORREREM as sete condições que tinham escrito.

```
    NARRAR AS CAUSAS QUE SE CONHECE NÃO É PERCORRER
    AS CONDIÇÕES QUE SE ESCREVEU.
```

## 79.5 · UM MUTANTE QUE SOBREVIVE POR NÃO HAVER O QUE APANHAR

Ao implementar, seis mutantes sobreviveram — todos da mesma classe: guardas que
nunca tinham visto um defeito, porque nesta árvore não havia nenhum para elas
apanharem. Desligá-las não mudava nada.

```
    UMA GUARDA QUE NUNCA VIU UM DEFEITO NÃO É UMA GUARDA: É UMA FRASE.
```

A resposta foi tirar cada regra de dentro da asserção, torná-la função, e
corrê-la contra um defeito fabricado. Isolada, ela passou a responder também NÃO.
E uma delas era genuinamente fraca: «os membros pertencem à espécie» aceitava
declarar `SYSTEM_MAP_VISUAL_CARD` a um conjunto que era EXACTAMENTE o do pente
fino.

```
    PERTENCER À ESPÉCIE LARGA NÃO É SER DA ESPÉCIE LARGA.
```

## 79.6 · O BACKUP TIRADO DEPOIS DA MUTAÇÃO

O harness de mutação guardava a cópia ao lado do ficheiro. Quando um mutante fez
o gerador rebentar, a corrida seguinte tirou o seu backup de um ficheiro **já
mutado** — e a restauração repôs a mutação. O trabalho de uma sessão inteira
ficou pendurado num `.bak` que sobrou por acaso.

```
    UM BACKUP TIRADO DEPOIS DA MUTAÇÃO NÃO É UM BACKUP:
    É UMA CÓPIA DO DEFEITO.
```

## 79.7 · VIOLAR `ONE CHAIN OWNER` NÃO É, SOZINHO, PERDER CONFIANÇA

O manifesto declara 7 passos; o job do CI corre 21. Parecia causa de `FAIL`.
Medido, correndo as duas cadeias em clones separados do mesmo commit:

```
architecture.generated.json   IDÊNTICO
state.generated.json          IDÊNTICO
sources.generated.json        IDÊNTICO
impressão da árvore           d692478a  vs  8e6f06e4   DIFERE
```

As duas cadeias produzem o mesmo mapa. A impressão difere por outra dívida já
nomeada. A violação existe; o sintoma não.

```
    VIOLAR ONE CHAIN OWNER    → risco latente  → não move TRUST
    DUAS CADEIAS, DOIS MAPAS  → contradição    → FAIL

    NÃO PROMOVER UMA VIOLAÇÃO A CAUSA DE FAIL SEM SINTOMA MEDIDO —
    e não a deixar desaparecer por não ter onde aparecer.
```

## 79.8 · CONSEQUÊNCIA

```
CONTRATO   docs/arquitetura/SYSTEM-MAP-TRUST-CONTRACT.md
           4 planos · modelo de evidência · 6 relógios de frescura
           TRUST = PASS | DEGRADED | FAIL | UNKNOWN, com PASS em último

G0 FEITO   13 de 13 superfícies publicam ENTITY_SPECIES
           dono único, gerador RECUSA superfície desconhecida
           10 mutantes · 0 sobreviventes · 8 ataques · 0 sobreviventes

TRUST      FAIL — C6 fechada; C4 e C4b continuam
MÍNIMO     [G1] — quatro planos por afirmação + ASSERTION_SUPPORTED
```

Fica por saber que afirmação cada uma das 37 linhas emprestadas realmente
sustenta, e `ROLE` continua por atribuir nas 160 entidades. `G0` sozinho nunca
autorizou `DEGRADED`, e a DAG previu isso antes de a medição o confirmar.

---

# §80 · UM TETO COBRADO NA PRIMITIVA NÃO VÊ QUEM SAI POR UM SUBPROCESSO

**Missão:** `C10.8A-F — O TETO DE GASTO`
**HEAD final:** `532e3bed`
**Tocado:** `coleta/coletor.py` · `coleta/scrap_executor.py` ·
`coleta/social_rotas.py` · `coleta/scrap_fornecedores.py` · `leis/falhas.py` ·
`provas/orcamento_financeiro.py`

A `§77` fechou o teto de ACESSOS e deixou escrito, como incógnita, que um
caminho que abrisse ligação por uma primitiva fora de `urlopen` e
`create_connection` escaparia. A incógnita não era futura: já existia, e é a
porta paga.

## 80.1 · O MESMO CENSO, A RESPOSTA OPOSTA — E ISSO É O MÉTODO A FUNCIONAR

A `§77` diz que o dono do conceito e o ponto de cobrança não têm de ser a mesma
linha. Aplicada ao dinheiro, a mesma disciplina deu o contrário:

```
rede      25 funções abrem ligação   → dono em `scrap_http`, cobrança nas primitivas
dinheiro   1 POST compromete gasto   → dono e cobrança no mesmo ficheiro
```

Trinta e cinco capacidades declaradas, três com rota paga por omissão, **zero**
com adaptador. O único sítio que compromete dinheiro é o `POST` dentro de
`coletor.executar`.

```
    ONE CONCEPT → ONE OWNER. QUANDO HÁ UMA SÓ PORTA, O DONO ESTÁ NELA.
```

A lição não é «o dono fica sempre longe do ponto de cobrança», nem sempre perto.
É que a **forma vem do censo**, e um censo feito outra vez pode devolver outra
forma sem que nenhuma das duas esteja errada.

## 80.2 · O BURACO QUE O SEGUNDO TETO REVELOU NO PRIMEIRO

A matriz dos dois gates tinha quatro casos. O segundo saiu vermelho à primeira:

```
NETWORK = 0 · FINANCIAL = 1.00 → o provider FOI CHAMADO
```

O teto de rede cobra onde a ligação abre — `urllib.request.urlopen` e
`socket.create_connection`. A porta paga não passa por nenhuma das duas: ela
lança um processo `curl`.

```
    UM TETO COBRADO NA PRIMITIVA NÃO VÊ QUEM SAI POR UM SUBPROCESSO.
```

E o censo das vinte e cinco portas não mentiu — ele contou **funções de Python
que abrem ligação**, e essa contagem estava certa para o universo que declarou.
O que faltava era o universo incluir quem sai por fora da linguagem.

```
    UM CENSO ESTÁ CERTO DENTRO DO UNIVERSO QUE DECLARA.
    QUEM SAI POR FORA DA LINGUAGEM SAI POR FORA DO CENSO.
```

O conserto manteve o dono: `coletor` não conta nada, **pede** autorização a
`scrap_http` antes de cada `subprocess.run`. Um saldo de rede copiado para o
coletor seria um segundo contador, e dois contadores da mesma coisa divergem
sempre.

## 80.3 · O QUE NÃO SE CONSEGUE LER NÃO VOLTA AO BOLSO

O dinheiro tem um intervalo que a rede não tem: entre comprometer e saber quanto
custou. Três eixos, e o do meio é onde o dinheiro fica sem dono:

```
AUTHORIZED   o que esta execução pode comprometer
COMMITTED    reservado por uma chamada em curso, ainda sem custo lido
ACTUAL       o que ela custou — lido, e não liquidado
```

Um POST que cai no transporte pode ter nascido do outro lado. Devolver a reserva
faria a chamada seguinte gastar outra vez o que talvez já tenha saído.

```
    UNKNOWN COST != ZERO COST.
    POTENTIAL COMMITMENT != NOTHING HAPPENED.
    UMA RESERVA QUE NINGUÉM LIQUIDOU NÃO VOLTA AO BOLSO.
```

Só voltam ao saldo os casos com **prova** de que nada correu: a plataforma
respondeu recusa sem criar execução, e o teto de rede recusou antes do POST.
«Não encontrei execução nenhuma» é uma leitura, não uma prova.

E há um quarto valor que já existia nesta casa e não podia ser colapsado:
`READ_NOT_SETTLED`. O custo lido não é o custo pago — esta casa anunciou US$0,90
e pagou US$5,04.

```
    READ COST != SETTLED COST.
```

## 80.4 · UM TETO POR CHAMADA NÃO É UM TETO DA CORRIDA

`maxTotalChargeUsd` já era usado, e parecia proteção. Ele limita **cada**
execução da Apify, nunca a soma delas: `instagram_coleta` declara US$0,50 por
conta em quatro fases, e cem contas são US$50,00 de exposição sem que nenhum
número acima de 0,20 apareça em lado nenhum.

```
    PROVIDER CAP != EXECUTION BUDGET.
    PROVIDER CAP <= EXECUTION REMAINING.
```

O cap que o chamador pede passou a ser **rebaixado** ao saldo, nunca elevado. E
quem não pede cap nenhum recebe o saldo inteiro como trava: duas das três portas
pagas desta casa chamavam sem trava alguma, e uma delas em ciclo sobre as chaves
do pool.

Detalhe que evita uma classe inteira de defeito: o saldo vive em **micro-dólares
inteiros**. Cem reservas de US$0,01 fecham exactamente em US$1,00, e um teto que
erra na sexta casa decimal é um teto que às vezes deixa passar.

## 80.5 · O FAKE TEM DE SER SEMPRE A CAMADA MAIS FUNDA

Três vezes na mesma missão, e sempre a mesma forma:

- trocar `_curl` inteiro punha o falso **acima** do gate de rede — e o caso
  `NETWORK = 0` passava a verde por o gate ter desaparecido, não por funcionar;
- trocar `http.buscar` punha o falso **acima** de onde um mutante metia
  cobrança — e esse mutante sobreviveu;
- abrir o orçamento e **só depois** instalar o falso substituía o próprio
  contador, porque o orçamento embrulha a primitiva no momento em que entra.

```
    UM FAKE ACIMA DO GATE MEDE O FAKE.
    UM FAKE INSTALADO DEPOIS DO TETO SUBSTITUI O CONTADOR.
```

A regra que fica: o falso entra no ponto mais fundo que existir — o
`subprocess.run`, a primitiva — e entra **antes** de qualquer teto. E quando a
medição puder ser feita sem falso nenhum, faz-se sem: reprocessar bytes
preservados com os dois tetos a zero prova mais do que qualquer substituição,
porque qualquer socket ou qualquer reserva levantaria.

## 80.6 · SONDAS QUE MEDEM A PALAVRA, OUTRA VEZ, DE DUAS MANEIRAS NOVAS

A `§75.3` já ensinou que uma sentinela que procura a palavra não mede o que ela
faz. Esta missão produziu duas variantes que aquela frase não cobria:

```
    UMA SONDA QUE PROCURA A PALAVRA ENCONTRA A FRASE QUE DIZ QUE ELA NÃO EXISTE.
```

A sonda do paralelismo procurou `threading` nos ficheiros e acusou o comentário
que eu próprio tinha escrito a dizer que não havia paralelismo. E, quando passou
a ler a árvore, acusou o `import threading` do próprio orçamento — que usa
`Lock` e `local`, nenhum dos quais arranca coisa nenhuma.

```
    IMPORTAR `threading` NÃO É CORRER EM PARALELO.
    MEDE-SE QUEM ARRANCA, NÃO QUEM IMPORTA.
```

A segunda: a sonda do «quem faz POST» acusou `adaptador_aberto.py`, onde `POST`
é o **grão do conteúdo** — um post do Mastodon — e não um método HTTP.

```
    O VALOR SEM O NOME DO CAMPO É OUTRA COISA.
```

## 80.7 · TERCEIRA VEZ, E A LIÇÃO JÁ ESTAVA ESCRITA

A `§75.1` apanhou um túnel caído a sair como `ROUTE_NOT_ALLOWED`. A `§77.5`
apanhou a recusa do teto de rede a sair como `BLOCKED`, e escreveu a regra: uma
recusa nossa atravessa os `except` largos inteira. Agora, o `except Exception`
de `coletor.executar` vestia a recusa dos dois tetos de `STATUS: FAILED` — um
manifesto a dizer que a Apify falhou sem a Apify ter sido chamada.

```
    UM `except Exception` LARGO NÃO DISTINGUE QUEM DISSE NÃO.
```

A regra estava escrita e não tinha sido aplicada **na porta que ainda não tinha
recusa nenhuma para deixar passar**. É a `§76.4` outra vez, por outro lado:

```
    UMA REGRA APLICADA ONDE A RECUSA NASCEU E NÃO ONDE ELA PASSA
    ESTÁ APLICADA A MEIO.
```

A partir daqui: quando um dono ganha uma recusa própria, cada `except` largo no
caminho dela é um sítio a rever — e não só o do ficheiro que a levantou.

## 80.8 · REUSAR O VOCABULÁRIO REVELA O QUE FALTAVA NELE

`leis/falhas.py` já tinha `BUDGET_EXHAUSTED` — «teto NOSSO», `NO_RETRY`. O teto
financeiro entrou lá como alias em vez de nascer estado novo. E foi ao fazê-lo
que se viu que `NETWORK_BUDGET_EXHAUSTED`, da missão anterior, **não tinha
alias**: passado ao tradutor, virava `UNKNOWN_ERROR`.

Não dava erro porque nunca lá chegava — o embrulho do executor constrói o próprio
trace.

```
    UM ESTADO QUE NUNCA CHEGA AO TRADUTOR ESCONDE QUE NÃO TEM TRADUÇÃO.
```

## 80.9 · CONSEQUÊNCIA

```
FINANCIAL_BUDGET   por execução · 7 conceitos · micro-dólares inteiros
CHARGING_POINT     o POST, dentro do dono do dinheiro
GATES              financeiro primeiro; quem é recusado pelo dinheiro não gasta acesso
TRIAL              rota paga sem teto declarado não começa
ATAQUES 30 · MUTANTES 16 · SOBREVIVENTES 0 · rede real 0 · custo real 0
```

Fica por saber o comportamento sob retentativa real — o ciclo continua a não
existir — e o custo de `x.discovery`, que nunca correu. E fica escrito que a
recomendação de valor não é autorização: quem autoriza dinheiro é gente.

---

# §81 · UMA CHAVE NO COFRE NÃO É UMA CHAVE NO PROCESSO

**Missão:** `C10.8B — A PRIMEIRA ROTA PAGA CANÔNICA`
**HEAD final:** *ver o documento da missão*
**Tocado:** `coleta/adaptador_youtube.py` · `coleta/coletor.py` ·
`coleta/social_rotas.py` · `provas/primeira_rota_paga.py`

A `§80` fechou o teto de gasto. Esta missão tinha autorização humana de US$0,10
para o primeiro gasto real — e não gastou. O que se aprendeu foi o caminho até
ao portão, e o portão.

## 81.1 · A PERGUNTA NÃO ERA A DA CAPACIDADE

`youtube.native_caption` já estava `PROVEN`. A rota paga que a serve estava
`POSSIBLE_NOT_PROVED`. São duas perguntas, e a primeira não responde pela
segunda:

```
    CAPABILITY PROVEN != PAID ROUTE PROVEN.
    ROUTE ALLOWED != ROUTE EXECUTED.
```

Uma capacidade diz «esta casa consegue». Uma rota diz «por esta porta, com este
fornecedor, a este preço». Promover a capacidade nunca provou a porta — e ir
buscar a capacidade para dizer que a rota está provada seria escrever a
conclusão antes da medição.

## 81.2 · O PORTÃO QUE PAROU A MISSÃO, E POR QUE ELE ESTÁ CERTO

`APIFY_TOKEN_POOL` vive nos *Secrets* do GitHub e é injectado pelos workflows.
Numa sessão que corre fora do workflow, ele não existe.

```
    A CHAVE EXISTIR NO COFRE NÃO É A CHAVE CHEGAR AO PROCESSO.
```

E deste lado do processo, «não temos credencial» e «a ligação do segredo está
partida» são indistinguíveis. A sonda diz só o que consegue provar —
`CREDENTIAL_MISSING NESTE AMBIENTE` — e quem distingue é o workflow. Essa
distinção já estava escrita no adaptador do YouTube para a chave da API oficial;
o que faltava era aplicá-la à chave **paga**, que tem outro dono.

A recusa é canônica, e é a única desta cadeia que pede gente:
`HUMAN_PROVISION_CREDENTIAL`.

## 81.3 · DOIS PORTÕES, E CADA UM TEM DE SEGURAR SOZINHO

A credencial é lida em dois sítios: a sonda gratuita do `CHECK`, e a própria
rota antes de chamar o dono pago. Parece redundância, e um mutante mostrou que
não é: removendo o portão de dentro da rota, a bateria continuava verde —
porque o `CHECK` recusava primeiro e o segundo portão nunca era exercido.

```
    UM PORTÃO QUE SÓ FUNCIONA PORQUE OUTRO O PRECEDE NÃO É UM PORTÃO.
    É UMA LINHA QUE NINGUÉM MEDE.
```

A sentinela que faltava desliga o primeiro portão de propósito e mede o segundo
sozinho. Vale para qualquer defesa em profundidade desta casa: se as duas
camadas nunca são medidas em separado, existe uma só.

## 81.4 · ROTAÇÃO DE CHAVE É UMA SEGUNDA COMPRA

`apify_pool` roda chaves quando uma esgota, e isso nasceu certo: numa rota
gratuita, rodar é resiliência. Numa rota **paga**, cada volta do ciclo é um novo
`POST` de criação de execução.

```
    ROTAÇÃO DE CHAVE É UMA SEGUNDA COMPRA.
```

E é pior do que parece, porque o ciclo existente roda quando a primeira chamada
falha — que é exactamente quando não se sabe se a primeira compra aconteceu. A
rota paga desta missão usa a primeira posição e para. Um mecanismo de
resiliência herdado de um contexto gratuito tem de ser relido antes de atravessar
para um contexto pago.

## 81.5 · O QUE TORNA UM TETO DE REDE FINITO É UM `wait`

O teto de acessos de uma corrida paga não é um número escolhido. Ele sai da
leitura do dono:

```
1   POST que cria a execução
≤1  consulta ao estado, só se não terminal aos 60 s
1   leitura do dataset
2   leituras do armazém de chave-valor
```

A plataforma concede 60 s no próprio POST. Tudo acima disso vira **consulta**, e
cada consulta é uma ida à rede: com `wait=120` seriam até treze.

```
    UM `wait` MAIOR NÃO É MAIS PACIÊNCIA. É MAIS IDAS À REDE.
```

Quem quiser um teto de rede pequeno paga em certeza, e quem quiser certeza paga
em idas. A escolha é declarada, não herdada — e o retrato de uma corrida que não
terminou sai marcado como parcial em vez de ser comprado outra vez.

## 81.6 · UMA COMPRA DUVIDOSA LIDA COMO «NÃO CORREU»

O red team encontrou o pior estado possível a ler-se como o melhor. Um POST que
cai no transporte pode ter criado execução paga; o orçamento sabia disso e
segurava o dinheiro em `UNKNOWN`. O **rastro** dizia `NOT_RUN`.

```
    NOT_RUN != UNKNOWN.
    UMA COMPRA DUVIDOSA NÃO É UMA COMPRA QUE NÃO HOUVE.
```

Duas metades do mesmo defeito, e nenhuma delas se vê sozinha:

- a reserva só era anexada ao manifesto quando fechava **no fim**; no caminho em
  que fechava antes — justamente o ambíguo — o manifesto não dizia nada;
- o roteador só levantava o custo do balde no caminho de **sucesso**, e uma rota
  que falhou pode ter gastado na mesma.

```
    UMA RESERVA QUE NÃO SOBE AO MANIFESTO DEIXA O RASTO DIZER «NÃO CORREU».
    O CAMINHO DE FALHA TAMBÉM TEM DE CARREGAR O QUE SE GASTOU.
```

A `§80` provou que o orçamento guarda a verdade. Esta missão mostrou que guardar
a verdade e **dizê-la** são dois trabalhos.

## 81.7 · DUAS SENTINELAS QUE ERAM FOTOGRAFIAS

Duas medições viraram testes e, com o tempo, pareciam leis:

```
C10.8A-F  «nenhuma capacidade de rota paga tem adaptador»
C2        «a legenda continua declarada SEM rota»
```

As duas estavam certas quando foram escritas. As duas reprovaram no dia em que
esta casa ligou a rota paga **de propósito**, com autorização humana e teto
declarado.

```
    UM CENSO QUE VIRA LEI TRANCA A PORTA QUE ELE SÓ MEDIU.
```

Nenhuma foi apagada. As duas passaram a guardar o que continua a valer — a lista
de rotas pagas ligadas é fechada e nomeada, e cada uma tem sonda gratuita — e
dizem no corpo por que mudaram. É a `§76.5` outra vez, e vale a pena tê-la
escrita duas vezes: um teste que muda de lado com a razão à vista é saúde; um
teste apagado é história perdida.

## 81.8 · O CONTRATO DO FORNECEDOR ENVELHECE

O ator de transcrição aceitava `videoUrls`, uma lista. Hoje exige `videoUrl`, no
singular. Quem descobriu não foi documentação — foi a recusa da própria
plataforma, `HTTP 400 invalid-input`, e só porque a mensagem chegou **inteira**
ao manifesto.

```
    ENTRADA PROVADA ONTEM != ENTRADA VÁLIDA HOJE.
```

E o esquema de saída desta missão não veio de documentação nenhuma: veio dos
bytes preservados de uma corrida anterior do mesmo ator. Um acervo de RAW não
serve só para auditar o passado — é a única leitura de contrato que não custa
dinheiro.

## 81.9 · E O QUE O FORNECEDOR NÃO DECLARA

O ator devolve `{url, transcript, chars}`. Não diz a língua, não devolve marcas
de tempo, e não diz se o texto é a legenda publicada ou um reconhecimento de fala
que ele próprio fez.

```
    CAPTION != TRANSCRIPT != ASR.
    O QUE O PROVIDER NÃO DECLARA, A CASA NÃO INVENTA.
```

O campo ficou `NOT_DECLARED_BY_PROVIDER`. Chamar-lhe `TRANSCRIPT` seria afirmar
uma origem que ninguém mediu — e seria um número com cara de medida, que é o
erro que a `§79` já catalogou noutro sítio.

## 81.10 · CONSEQUÊNCIA

```
ROTA         apify:transcricao — ligada, gateada, e ainda POSSIBLE_NOT_PROVED
WIRING       executor → router → adapter → dono pago, sem bypass, provado offline
TETOS        rede 5 · dinheiro 0.10 · ambos activos e medidos
GASTO        US$ 0,00 — READY_TO_SPEND = NO, e o motivo tem nome canônico
ATAQUES 34 · MUTANTES 16 · SOBREVIVENTES 0
```

A ligação está construída e nunca correu contra o fornecedor real. O ensaio
offline mede o **nosso** lado do contrato; o lado do ator só se mede a gastar. E
uma autorização de dinheiro que não foi usada continua inteira — não caduca, e
não se transforma em permissão para tentar outra coisa.

---

# §82 · UM ARTEFATO DESACTUALIZADO NÃO É UM ARTEFATO ANTIGO: É UM ARTEFATO FALSO

**Missão:** `C-PROVE-CANONICAL-E2E-FROM-REQUEST-V1 — correcção de drift`
**HEAD final:** `3b53ef0c`
**Tocado:** `provas/os_portoes_da_collection.py` ·
`docs/operacao/COLLECTION-V1-CLOSE-GATES.md` ·
`data/derivados/COLLECTION-V1-CLOSE-GATES.json`

A `§78` provou que um pedido canónico atravessa `REQUEST → ORCHESTRATOR →
EXECUTOR → RUN → RAW → STORAGE` numa história só, e pára. Os artefatos de
fechamento não souberam disso: continuaram a dizer `FLOW_EXECUTED = NO` nas
quatro primeiras etapas e a chamar muda uma `READY` que já emite rasto.

O erro não foi medir mal. Foi medir e não voltar a escrever.

```
    QUEM NÃO REESCREVE O RETRATO DEPOIS DE MEDIR
    NÃO FICA COM UM RETRATO VELHO: FICA COM UM RETRATO QUE MENTE.
```

## 82.1 · UM CARIMBO DE COMMIT NUM FICHEIRO COMMITADO NASCE SEMPRE ATRASADO

O artefato carimbava `MEASURED_HEAD`. Estava dois commits atrás, e não por
descuido: **é impossível por construção.** O ficheiro que guarda o carimbo entra
no commit seguinte, logo ele nunca pode nomear o commit que o contém.

```
    A PERGUNTA NÃO É «QUE COMMIT?». É «QUE FICHEIROS DECIDEM ISTO?».
```

A `CADEIA-DO-MAPA.json` já tinha aprendido isto para a árvore inteira, com a
`IMPRESSAO_DA_ARVORE`. Aqui aplica-se ao mesmo problema à escala de uma medição:
`DONOS_DA_MEDICAO` nomeia os quatro ficheiros que decidem o resultado, e
`IMPRESSAO_DOS_DONOS` é o `sha256` do conteúdo deles.

```
DONOS_DA_MEDICAO = provas/os_portoes_da_collection.py
                   docs/biblia/leis.json
                   system-map/data/buracos.generated.json
                   system-map/data/pedido.observado.json
```

Se eles não mudaram, a medição continua a valer por mais commits que passem. Se
mudaram, mudou por commits nenhuns. O carimbo de commit fica — ele diz **quando**
— mas quem quer saber se o retrato ainda vale compara a impressão.

## 82.2 · O MARKDOWN COPIAVA O NÚMERO, E POR ISSO ENVELHECIA SOZINHO

A primeira correcção que escrevi foi pôr a impressão nova no documento. Uma
medição depois, o documento já tinha a impressão errada — a mesma doença, num
sítio novo.

```
    DOIS DONOS DE UM NÚMERO SÃO DUAS VERDADES,
    E A PARTIR DAÍ NENHUMA DAS DUAS VALE.
```

A guarda `ODocumentoNaoEDonoDosNumeros` já dizia, em `tests/`, que o JSON é o
dono e o Markdown explica. Eu tinha-a lido e mesmo assim copiei o número. A
correcção final tira os dois números do documento e deixa lá o comando que os lê
do artefato. Um documento que **ensina onde está o número** não envelhece; um que
o **repete** envelhece a cada medição.

## 82.3 · DOIS ACHADOS NA MESMA ESTRADA PODEM SER DE ESPÉCIES DIFERENTES

A estrada parte-se em `STORAGE -> DERIVED` e volta a partir-se em
`DERIVED -> STRUCTURED`. A tentação é escrever «faltam duas ligações».

```
STORAGE  -> DERIVED     WIRING_GAP           resolve-se com CÓDIGO
DERIVED  -> STRUCTURED  CONTRACT_OWNER_GAP   resolve-se com GENTE
```

O primeiro é uma chamada que não está ligada, e a prova mostra a **mesma**
observação a derivar com `PASS` quando `derivacao_forward` é chamada à mão:
a capacidade existe, falta o fio. O segundo é `public.conteudo` a exigir
`canal_id`, e a recusa diz por escrito quem resolve — «um dono de identidade,
fora do executor de coleta». Esse dono não existe hoje, e inventá-lo é uma
decisão de arquitetura, não uma ligação.

```
    MISTURAR OS DOIS PRODUZ UM PLANO QUE NINGUÉM CONSEGUE EXECUTAR:
    METADE DELE ESPERA POR UMA REUNIÃO.
```

## 82.4 · O QUE NÃO SE MEXEU, E NÃO SE MEXEU DE PROPÓSITO

```
CANONICAL_E2E         = FAIL
COLLECTION_CORE_CLOSE = FAIL
FIRST_LOST_EDGE       = STORAGE -> DERIVED
```

Nenhum buraco foi tapado nesta passagem. Corrigir o retrato e tapar o buraco na
mesma missão é a maneira mais limpa de nunca se saber qual dos dois produziu o
verde.

```
    MEASURE != FIX. E A ORDEM IMPORTA:
    UM RETRATO FALSO TAPADO É UM BURACO QUE DESAPARECE SEM SER CONSERTADO.
```

A prova voltou a correr num banco descartável e deu o mesmo veredito — só o
`RUN_ID` mudou. Uma medição que não se repete não é uma medição: é uma anedota.

## 82.5 · E A PRÓPRIA IMPRESSÃO NASCEU ERRADA, PELA MESMA DOENÇA

A impressão somava os **bytes** dos quatro donos. Um deles é
`buracos.generated.json`, e ele guarda um `PROVENANCE.HEAD` — o commit em que o
censo correu.

```
commit seguinte  →  PROVENANCE.HEAD muda  →  impressão muda
                     sem que uma vírgula do censo mude
```

Medido: a impressão deixou de coincidir no commit a seguir àquele que a criou.
A cura estava contaminada pela doença que vinha curar — um carimbo de commit
dentro de um ficheiro a estragar quem o lê, um andar abaixo.

```
    UMA IMPRESSÃO QUE NUNCA COINCIDE NÃO DIZ «ESTÁ VELHO».
    NÃO DIZ NADA.
```

Agora a impressão mede o que o dono **diz**, e não **quando** foi feito: de um
dono gerado em JSON sai `PROVENANCE.HEAD`, e só ele. `MEDIDO_POR` fica, porque
trocar quem mede é mudança de substância e tem de gritar.

A lição geral não é sobre este campo:

```
    UMA IMPRESSÃO DE FRESCURA NÃO PODE INCLUIR NADA QUE MUDE
    POR RAZÕES QUE NÃO SÃO A PERGUNTA QUE ELA FAZ.
```

E só se soube porque a impressão foi **conferida contra a árvore depois de o
commit mudar**. Uma guarda de frescura que nunca se testa contra o segundo
commit passa despercebida para sempre.

## 82.6 · O QUE FICA POR SABER

Fica por saber se a `IMPRESSAO_DOS_DONOS` tem os donos certos: ela mede quatro
ficheiros, e nada hoje reprova quem acrescentar um quinto decisor sem o declarar.
A lista é hoje um acordo escrito, e não uma guarda que morde — ao contrário da
`EXCLUIDO` da cadeia do mapa, que `test_impressao_da_arvore.py` confere.
E fica por saber se há outros campos voláteis dentro dos donos: encontrei
`PROVENANCE.HEAD` porque ele partiu à primeira volta, e não porque alguém
tenha feito o censo do que lá muda sozinho.

---

# §83 · UMA LINHA DE CÓDIGO PROVA QUE ALGO CONSEGUE, NÃO QUE ALGO ACONTECEU

**Missão:** `C-SYSTEM-MAP-G1-FOUR-PLANES-AND-EVIDENCE-BINDING-V1`
**Linha:** `claude/dazzling-cerf-27a7v2` · **HEAD final:** `e50717e6`
**Tocado:** `system-map/scripts/generate_system_map.py` ·
`system-map/scripts/revisao_da_evidencia.py` ·
`system-map/tests/test_quatro_planos.py` · `system-map/app/map.js` ·
`docs/arquitetura/SYSTEM-MAP-TRUST-CONTRACT.md`

`§79` registou que o mapa media bem e publicava a palavra errada. Esta secção é
o que foi preciso para ele parar de a publicar.

## 83.1 · O QUE MUDOU

Cada afirmação do mapa passou a viver em quatro planos separados, e cada
evidência passou a dizer **que afirmação sustenta**.

```
antes   659 arestas e 59 peças:  status = PROVEN
        uma palavra a responder por quatro perguntas

depois  DECLARED · CODE · OBSERVED · PROVEN, cada um YES|NO|UNKNOWN
        614 CODE=YES · 47 CODE=UNKNOWN · 661 OBSERVED=UNKNOWN
        e PROVEN traz sempre o PLANO em que está provado
```

```
    ANÁLISE ESTÁTICA PROVA CAN DO. SÓ TELEMETRIA PROVA DID DO.
    DECLARED → CODE → OBSERVED → PROVEN: nenhuma seta é automática.
```

## 83.2 · POR QUÊ

Porque as duas falhas eram a mesma correcção vista de dois lados, e separá-las
teria deixado o mapa a mentir por metade:

- rotular os planos **sem** ligar a evidência à afirmação deixava 52 arestas com
  `CODE=YES` apoiado numa linha que não as prova;
- ligar a evidência **sem** rotular os planos deixava 659 arestas a dizer
  `PROVEN` sobre evidência de código.

Nenhuma das duas, sozinha, tirava o mapa de `FAIL`.

## 83.3 · PROVA — E O CASO QUE SÓ APARECEU AO IMPLEMENTAR

A sentinela conhecida ficou fixada como caso de teste:

```
C-APIFY-POOL → C-COLETA-PUBLICA  IMPORTS       CODE = YES      (plano CODE)
C-APIFY-POOL → V-FACEBOOK        ABRE_O_CANAL  CODE = UNKNOWN
C-APIFY-POOL → V-INSTAGRAM       ABRE_O_CANAL  CODE = UNKNOWN
C-APIFY-POOL → V-LINKEDIN        ABRE_O_CANAL  CODE = UNKNOWN
```

E apareceu um terceiro caso que ninguém tinha nomeado: **a mesma linha medida
duas vezes, por duas perguntas**. O scanner emite `IMPORTS` pelo casador de
imports e emite também `READS artefacto` pelo casador de **literais**, que
encontra `'./lang.mjs'` dentro de `import { X } from './lang.mjs'` e não
distingue um especificador de módulo de um caminho de dado. Trinta e seis linhas,
todas `.mjs`.

```
    UM `import` NÃO É UMA LEITURA DE ARTEFACTO.
```

O scanner não foi corrigido — o mapa **observa**. Diz-se o que a evidência
sustenta, e o plano cai para `UNKNOWN`.

As 52 arestas foram revistas uma a uma, com o porquê ao lado: 30 `SUPPORTED`,
7 `AMBIGUOUS`, 15 `UNSUPPORTED`. Nenhuma decisão entrou sem `WHY`.

```
    NO != UNKNOWN. Onde a evidência não sustenta a afirmação, o plano cai
    para UNKNOWN — nunca para NO. Falta de prova não é prova de ausência.
```

## 83.4 · INFERIDO PELO OBSERVADOR NÃO É DECLARADO PELA AUTORIDADE

O contrato chamava aos 40 rótulos sem tipo medido «rótulos narrativos **de
declaração**» e dava-lhes `DECLARED = YES`. Medido: só **duas** vêm de
`architecture.declared.json`. As outras **38 são inferidas pelo próprio gerador**
a partir de factos de ficheiro.

São o caso mais desconfortável do mapa: ele desenha-as e não as consegue provar
em plano nenhum. Agora diz isso, em vez de lhes emprestar uma autoridade que
elas não têm.

## 83.5 · UM CAMPO QUE SOBREVIVE À REFORMA TEM DE PASSAR A DERIVAR DELA

`status` ficou, porque a tela e três censos o leem. O que mudou é que deixou de
ser uma segunda opinião: é derivado de `PROVEN`, está marcado `DEPRECATED`, e a
prova reprova se contradisser os planos.

```
    UM CAMPO LEGADO QUE NÃO DERIVA DA REFORMA
    NÃO É COMPATIBILIDADE: É UM CONCORRENTE.
```

## 83.6 · UM TOTAL QUE VEM DA MESMA LISTA QUE ELE CONTA NUNCA ACUSA UMA FALTA

Três mutantes sobreviveram à primeira ronda, todos guardas que nunca tinham visto
um defeito. Um deles apanhou um erro a sério: a prova conferia a cobertura da
revisão **comparando-a consigo própria** — `ARESTAS_REVISTAS == len(ARESTAS)` —
e as duas encolhem juntas quando alguém deixa uma aresta de fora.

Conferida contra o **estado**, ela acusou de imediato uma aresta em falta: a do
próprio APIFY. A revisão corria antes da última passagem da cadeia e media o
conjunto da corrida anterior — a mesma dívida do ciclo atrasado, noutro sítio.

```
    UMA COBERTURA CONFERIDA CONTRA A PRÓPRIA LISTA MEDE ZERO.
```

## 83.7 · CONSEQUÊNCIA

```
C1..C7    todas FALSE
TRUST     DEGRADED — medido, não forçado, e previsto pela DAG antes de o ser
RED TEAM  12 ataques · 0 sobreviventes
MUTAÇÃO   14 mutantes · 0 sobreviventes
```

`CAN DO` e `DID DO` passam a coexistir sem promoção automática. O mapa saiu de
`FAIL` não por ter provado mais, mas por ter passado a dizer com precisão o que
sabe e o que não sabe — e **661 arestas dizem agora `OBSERVED = UNKNOWN`**, que é
a verdade que ele antes escondia atrás da palavra `PROVEN`.

Fica por saber o comportamento de `OBSERVED` quando houver travessia observada
por par de cartões: hoje o ledger observa **ficheiros de executor**, não arestas,
e duas peças de 160 estão observadas.

---

# §84 · UM BRUTO QUE NÃO SOBREVIVE AO JOB SEGUINTE É UM BRUTO QUE NÃO EXISTE

**Missão:** `C10.8B-LIVE — A PRIMEIRA ROTA PAGA REAL`
**Corrida:** `sintonia-scrap` run 34705103759 · `SINTONIA-EAME-LOCAL-2`
**Gasto:** autorizado US$0,10 · lido US$0,00 · liquidado UNKNOWN

A `§81` fechou a pergunta da credencial. Esta missão atravessou a porta e pagou
— e o que se aprendeu está do outro lado dela.

## 84.1 · O SEGREDO CHEGOU, E ISSO ERA MESMO A ÚNICA COISA QUE FALTAVA

```
    SECRET EXISTS != SECRET REACHES PROCESS.
```

A `§81` deixou isso escrito como hipótese. Confirmou-se: a mesma árvore, a mesma
cadeia, o mesmo alvo — num job do workflow, `CHECK.CAN = True` e a corrida
aconteceu em 37 segundos. Nenhuma linha de coleta mudou entre um caso e o outro.

E o censo dos workflows trouxe uma segunda metade que não estava à vista: **todos**
os que recebem a chave paga correm em runner self-hosted. Três despachos
anteriores tinham ficado 24 horas na fila e sido cancelados por não haver
runner.

```
    UM WORKFLOW QUE NINGUÉM EXECUTA É UM WORKFLOW QUE NINGUÉM TESTOU.
```

## 84.2 · A GUARDA QUE APONTAVA PARA A MORADA ANTIGA

O primeiro passo do workflow verificava dez ficheiros em `scripts/` — uma pasta
**vazia** desde a reorganização. Ela reprovava toda a gente, sempre, com a frase
de quem despachou contra o ref errado.

```
    UMA GUARDA QUE APONTA PARA A MORADA ANTIGA RECUSA A CASA CERTA.
    E DIZ A CULPA DE OUTRA PESSOA AO FAZÊ-LO.
```

Ninguém a viu falhar porque ninguém corria o workflow; e ninguém corria o
workflow, em parte, porque ele falhava. Uma guarda só se prova a deixar passar
quem deve passar.

## 84.3 · O TETO NÃO PODE VIVER NO DISPARADOR

O workflow ganhou **uma linha de menu e um ramo**. O ator, o alvo, o modo, o
motivo e os dois tetos ficaram numa tabela em Python versionado.

```
    UM TETO QUE VIVE NO DISPARADOR É UM TETO QUE QUEM DISPARA ESCOLHE.
```

É a `§77` outra vez, uma camada acima: lá o teto vivia num script de prova, aqui
viveria num campo de formulário. Em ambos os casos ele deixa de ser uma lei da
casa e passa a ser uma opção de quem carrega no botão. Um teto que se lê num
commit é um teto que alguém reviu.

## 84.4 · CHEGAR AO PROVIDER NÃO É ENTREGAR

A corrida foi impecável no que se podia medir: um POST, cap US$0,10, `SUCCEEDED`,
três idas à rede de um teto de cinco, RAW escrito e relido com SHA igual. E o
objeto voltou **sem transcrição**.

```
    PROVIDER REACHED != CAPABILITY DELIVERED.
```

Toda a maquinaria de gasto e de rede funcionou. A capacidade não foi entregue.
São duas afirmações independentes, e um relatório que só publicasse a primeira
estaria a dizer a verdade e a enganar.

Por isso a rota ficou `PARTIAL`, e não `PROVED` nem `POSSIBLE_NOT_PROVED`: já não
é verdade que não se saiba se ela corre — ela correu; e não é verdade que
entregue.

```
    PARTIAL SEM O LIMITE ESCRITO É `PROVED` COM OUTRO NOME.
```

## 84.5 · E OS BYTES QUE RESPONDERIAM JÁ NÃO EXISTIAM

O bruto tinha 59.743 bytes, o que não é o tamanho de uma resposta vazia. Duas
hipóteses, e só os bytes as separam: o ator mudou o esquema de **saída**, ou o
vídeo deixou de ter legenda.

```
    UM OBJETO VAZIO NÃO DIZ SE A FONTE CALOU OU SE O CAMPO MUDOU DE NOME.
```

Reler não custa nada — os bytes já estavam pagos e estavam na máquina.

```
    RELER O QUE JÁ SE PAGOU NÃO É PAGAR OUTRA VEZ.
```

Só que não estavam. `.gitignore` ignora `data/samples/**/*.gz`, e
`actions/checkout` limpa o que o `.gitignore` ignora. O bruto foi escrito,
relido e assinado dentro do mesmo processo — e apagado pelo checkout do job
seguinte.

```
    RAW CAPTURADO NO PROCESSO
      != RAW QUE SOBREVIVE AO JOB
      != RAW DEVOLVIDO AO REPOSITÓRIO
      != PRESERVAÇÃO FORWARD CANÔNICA.
```

Quatro estados que cabiam todos na palavra «preservado» — e o manifesto desta
casa diz `PRESERVED` para o primeiro. Fica explicado, de passagem, por que os
brutos das corridas do SENSOR aparecem como preservados e não estão em lado
nenhum: nunca estiveram.

O `SHA-256` sobrevive no registo e não resolve para ficheiro nenhum. É uma
impressão digital de uma coisa que já não existe — útil se alguém trouxer os
bytes, inútil para a pergunta de hoje.

## 84.6 · O CONSERTO É A FORMA, E NÃO OUTRA COMPRA

Não se comprou outra vez. O registo passou a guardar a **FORMA** do bruto — as
chaves de cada item, o tipo, o tamanho e se está vazio — no mesmo processo em
que os bytes ainda existem.

```
    QUANDO OS BYTES NÃO PODEM VIAJAR, VIAJA A FORMA.
```

É barato, cabe num JSON, e responde no registo à pergunta que custou uma corrida
paga para ficar por responder. A regra geral: tudo o que só existe **dentro** do
processo que o produziu tem de sair de lá em forma legível antes de o processo
acabar — porque o que fica para trás não fica.

## 84.7 · CONSEQUÊNCIA

```
apify:transcricao   POSSIBLE_NOT_PROVED → PARTIAL, com artefato citado
POLICY              CONDICIONAL, intocada · CLASSE APIFY, intocada
CAPACIDADE          PROVEN, intocada
PROVIDER_RUNS 1 · START_POSTS 1 · AUTORIZADO 0.10 · LIDO 0.00 · LIQUIDADO UNKNOWN
ATAQUES 33 · MUTANTES 18 · SOBREVIVENTES 0
```

Fica por saber por que o objeto veio vazio, e isso é dinheiro que ninguém
autorizou ainda. Uma rota `PARTIAL` é uma rota que corre e gasta: promovê-la
exige uma corrida que entregue.

---

# §85 · UMA CAPACIDADE QUE NINGUÉM CHAMA NÃO É UMA ETAPA DA ESTRADA

**Missão:** `C-WIRE-STORAGE-TO-DERIVED-IN-CANONICAL-E2E-V1`
**HEAD final:** `2bbf25cd`
**Tocado:** `orquestrador/orquestrador.py` · `coleta/ingresso.py` ·
`coleta/derivacao_forward.py` · `guarda/preservar_coleta.py` ·
`provas/o_pedido_atravessa.py`

A `§78` mediu a estrada e encontrou-a partida em `STORAGE -> DERIVED`. A `§82`
arrumou o retrato e deixou o buraco onde estava. Esta fechou-o — e o achado não
é o conserto: é o **tamanho** dele.

```
o que faltava   uma chamada
o que existia   o executor, o runner, o dono da escrita, o dono do rastro
```

Quatro peças completas, escritas, testadas, com prova própria a passar. E a
estrada partida porque nenhuma linha as invocava.

```
    CAPABILITY EXISTS ≠ EDGE EXISTS.
    UMA CAPACIDADE QUE NINGUÉM CHAMA NÃO É UMA ETAPA DA ESTRADA.
```

## 85.1 · A PONTE NÃO ERA A CHAMADA: ERA O QUE ELA TINHA DE LEVAR

A chamada é uma linha. O que custou foi descobrir que **a porta já sabia tudo o
que a derivação precisa, e deitava fora**.

`ingresso.receber()` devolvia `PRESERVADOS: len(aceites)` — uma contagem. O
`recibo` que ela tinha em mãos trazia, por observação, o `RAW_OBSERVATION_ID`
real e o `storage_path` do objeto. Os dois campos que fazem um derivado ter pai.

```
    CONTAR UMA COISA NÃO É GUARDÁ-LA.
```

É literalmente o mesmo defeito que `PARA_A_PORTA` fechou um degrau atrás, na
mesma função, quando o estágio se perdia entre a porta e a admissão. Duas vezes
o mesmo, e a segunda com a primeira escrita à vista, oito linhas acima.

A lição não é «olhar melhor». É que **uma função que devolve um número em vez do
objeto apaga a linhagem sem dar erro** — e o erro aparece etapas à frente, com
outra cara.

## 85.2 · O `GLOB` DA PROVA DIAGNÓSTICA NÃO PODIA ATRAVESSAR PARA A PRODUÇÃO

O `D1` da `§78` respondia «o DERIVED é alcançável a partir deste bruto?». Para
isso procurava um PDF com `glob` e emparelhava-o com `brutos[0]`.

Como diagnóstico estava certo: separava «não sabe» de «ninguém chama».
Como costura de produção seria um desastre silencioso.

```
    PATH ≠ IDENTITY.
    O PRIMEIRO FICHEIRO DA PASTA NÃO É O FILHO DA PRIMEIRA LINHA.
```

As duas ordens — a do `sorted(glob(...))` e a do `order by id` — não têm razão
nenhuma para coincidir. Quatro derivados podiam nascer todos com o pai trocado,
todos apontando para a corrida certa, e nenhuma conferência de corrida daria por
isso. Por isso a guarda não pergunta «é da mesma corrida?» mas «o
`parent_sha256` bate certo com o `sha256` da observação que o banco diz ser o
pai?».

```
    MESMA CORRIDA ≠ MESMO PAI.
```

E o `glob` saiu **também da prova**. Uma prova que usa a heurística que a
produção tem proibida ensina a heurística a quem a ler a seguir.

## 85.3 · O ARMAZÉM PASSOU A RESPONDER ONDE, PORQUE A FERRAMENTA NÃO RECEBE BYTES

`pdftotext` não aceita um `bytes`: recebe um caminho e abre-o. A porta do
armazém sabia `ler`, e isso não servia. Havia três saídas e duas eram piores:

```
1. perguntar ao armazém ONDE está        (a escolhida)
2. copiar o byte para um sítio temporário (segunda cópia do bruto, sem dono)
3. juntar a raiz ao storage_path por fora (a regra de endereçamento em dois sítios)
```

A terceira é a tentadora, porque é uma linha. E é a que põe o guarda do `..` e o
separador de caminho a viver em dois lugares.

```
    DOIS DONOS DO MESMO ENDEREÇO SÃO DOIS ENDEREÇOS,
    E UM DELES VAI ESCREVER FORA DO ARMAZÉM.
```

`None` ficou como resposta legítima: um armazém de objetos remoto não tem
caminho local, e inventar-lhe um ficheiro temporário seria responder à pergunta
errada. Quem recebe `None` não faz a unidade — e sabe porquê.

## 85.4 · DUAS GUARDAS DE TEXTO MORDERAM A PRÓPRIA EXPLICAÇÃO, NA MESMA MISSÃO

```python
self.assertNotIn("RC-1", fonte(ORQ))                    # falhou
self.assertNotIn("derivacao_forward.correr(", fonte)    # falhou
```

As duas reprovaram no parágrafo que **diz para não escrever aquilo**. Um
comentário que explica uma proibição tem de nomear o que proíbe.

```
    LER O FICHEIRO NÃO É LER O CÓDIGO.
    UMA GUARDA DE TEXTO NÃO DISTINGUE A REGRA DO EXEMPLO DELA.
```

Já estava escrito na `§72`, com o `_codigo()` que arrancava strings. Repeti-o
duas vezes no mesmo dia. As duas foram substituídas por AST: numa, o que a
chamada REALMENTE passa e qual é o valor por omissão; noutra, que chamadas
partem de um módulo com aquele nome.

E houve uma terceira, de espécie oposta — **larga de mais**. Bani `listdir` na
prova, e a prova lista a Sala de Espera de propósito, para conferir que ela
começa e acaba vazia.

```
    VARRER PARA ENCONTRAR O QUE DERIVAR  →  linhagem por acaso
    LISTAR PARA MEDIR O QUE CHEGOU       →  medição
```

Uma guarda que reprova o uso legítimo ensina quem a herda a desligá-la — e isso
é pior do que não a ter.

## 85.5 · O GRÃO DO DERIVADO É POR BYTES DO PAI, E ISSO SÓ SE VÊ DEPOIS DE LIGAR

`derivacao_e_unica_por_regua` é `UNIQUE` sobre `parent_sha256`. Duas observações
distintas dos mesmos bytes — o mesmo boletim colhido em duas corridas — partilham
**um** `derived_artifact`, e ele nomeia como pai só a primeira.

```
segunda corrida   4 observações novas
                  DERIVED PASS · reused=4 · zero linhas novas
```

`REUSED ≠ NOT_RUN`: a etapa correu, e o resultado já existia. Mas a consequência
é maior do que parece — **uma corrida cujos bytes já foram derivados antes não
tem `derived_artifact` próprio**, mesmo tendo a etapa corrido. Quem medir a
estrada nessa corrida verá `DERIVED` por atravessar.

Não se consertou: mudar a régua é mexer no contrato do dono do derivado. A
missão media a cardinalidade, não a redefinia. Mas só se soube porque a ligação
existiu — **uma cardinalidade declarada num `UNIQUE` não se lê; encontra-se.**

## 85.6 · ZERO BLOCKERS NÃO É ZERO TRABALHO

O documento publicava, lado a lado:

```
COLLECTION_CORE_CLOSE = FAIL
MISSÕES ATÉ FECHAR    = 0
```

O número era `len(dag())`, e a fila está mesmo vazia — não há blocker aberto
nenhum. O número estava certo sobre a fila e mentia sobre o caminho.

```
    UMA FILA VAZIA MEDE A FILA, E NÃO O CAMINHO.
```

A cura não foi um número maior inventado. O que falta depende de uma decisão que
ninguém tomou — de quem é o `canal_id` — e uma decisão por tomar pode dar uma
missão ou quatro. Ficou `UNKNOWN`, com a próxima coisa conhecida **nomeada** ao
lado. É a mesma disciplina que `MINIMUM_MISSIONS_TO_BIG_COLLECTION_READY` já
aplicava a três centímetros dali, e que ninguém tinha estendido ao vizinho.

## 85.7 · O QUE FICA POR SABER

O executor desta rota é de PDF, e as quatro observações do canário são PDFs.
**Uma rota que misture espécies não foi medida**: uma observação JSON entregue ao
extractor de PDF sai `ERROR`, e «a ferramenta falhou» é verdade literal — foi a
nossa ligação que a chamou. Escolher executor por espécie não tem dono hoje, e
inventar-lhe um seria a missão seguinte a começar sozinha.

E o derivado aterra em `NAO_SEI/derivados/...`, porque `raw_asset` não tem coluna
de país para o provar. O dono do derivado está certo em não inferir; o efeito é
que toda medição canónica deixa uma pasta `NAO_SEI/` na árvore — agora ignorada,
como o `XX/` que a `§78` pagou para descobrir.

---

# §86 · REUSO POR CONTEÚDO NÃO PRESERVA, SOZINHO, LINHAGEM POR OBSERVAÇÃO

**Missão:** `C-DECIDE-DERIVED-REUSE-LINEAGE-V1` (medição + contrato)
**HEAD final:** `397ee92a`
**Decisão:** [`docs/decisoes/ADR-LINHAGEM-DO-REAPROVEITAMENTO-V1.md`](docs/decisoes/ADR-LINHAGEM-DO-REAPROVEITAMENTO-V1.md)
**Medição:** `provas/a_linhagem_do_reaproveitamento.py`

A `§85` ligou `STORAGE -> DERIVED` e, ao ligar, mostrou que duas observações dos
mesmos bytes partilham **um** `derived_artifact`. Esta mediu até ao fim o que
isso custa — e nada foi implementado.

O grão do derivado está certo e não se reabre: a migration `022` decidiu
`CONTEÚDO POR RECEITA` com a razão escrita. Duas capturas são dois factos sobre
o mundo; a nossa ferramenta sobre estes bytes com esta régua dá **um** resultado.

O que não se sustenta é a frase que ela deixou ao lado.

## 86.1 · A CONSULTA QUE «RESOLVE» RESPONDE A OUTRA PERGUNTA

A `022` escreveu que nenhuma procedência se perde, porque as irmãs se encontram
com `select * from raw_asset where sha256 = <parent_sha256>`.

```
essa consulta responde   que observações TÊM os mesmos bytes
a pergunta era           que observações PASSARAM por esta derivação
```

Medido: para o derivado `1` ela devolve `[3, 7]`, e as duas chegam **iguais**.
Uma foi lida e derivada. A outra pode ter sido derivada e reaproveitada, ou pode
nunca ter sido processada. A consulta não as separa — e não é defeito dela, é a
pergunta que é outra.

```
    CAN INFER ≠ OBSERVED EDGE.
    TER OS MESMOS BYTES NÃO É TER PARTICIPADO DA MESMA EXECUÇÃO.
```

A lição maior é sobre a forma do argumento, e não sobre esta tabela: **uma
justificação de esquema que termina numa consulta possível está a provar
alcançabilidade, não registo.** Vale a pena reler assim todas as outras.

## 86.2 · PROCURAR O DONO NA MINHA MEMÓRIA NÃO É PROCURAR

A primeira tentação foi responder «não existe owner» depois de olhar para três
tabelas de que me lembrava. Isso mede a memória de quem procurou.

Quem sabe que colunas apontam para cada tabela é o catálogo do Postgres:

```sql
select conrelid::regclass, confrelid::regclass
  from pg_constraint
 where contype = 'f'
   and confrelid in ('public.raw_asset'::regclass,
                     'public.derived_artifact'::regclass)
```

Resultado: **dez** tabelas apontam para `raw_asset`; **nenhuma tabela do esquema
inteiro** aponta para `derived_artifact`. Não há ponte porque não há nada do
outro lado da ponte — e isso é uma afirmação medida, não uma impressão.

E apanhou um **falso amigo** que eu teria citado como resposta:
`public.derivacao_observacao`, da migration `005`. O nome bate. A camada não:
ela liga `derivacao` (uma *conclusão analítica*, com pergunta, resposta e
limitação) a `observacao` (um *facto medido com denominador*). Nada disso é
`raw_asset` nem `derived_artifact`.

```
    DOIS NOMES IGUAIS EM CAMADAS DIFERENTES SÃO DOIS CONCEITOS.
    USAR UM PELO OUTRO PORQUE O NOME BATE É O PIOR TIPO DE REUSO.
```

## 86.3 · A ARITMÉTICA DA CORRIDA HOMOGÉNEA NÃO É UMA ARESTA

O ledger da corrida B diz `input_count=4` e `reused=4`. Daí **deduz-se** que as
quatro observações foram reaproveitadas — e a dedução parece prova.

Ela funciona só porque todos os itens caíram no mesmo balde. Medido no caso
misto: a mesma passagem devolveu `{ERROR: 1, REUSED: 1}` para duas observações,
e a linha guarda os números, não os nomes. As duas leituras possíveis são
simétricas.

```
    CONTAGEM POR ETAPA ≠ DESTINO POR ITEM.
    UMA DEDUÇÃO QUE SÓ FUNCIONA NO CASO UNIFORME
    NÃO É UM REGISTO: É UMA COINCIDÊNCIA DE FORMATO.
```

Para medir isto foi preciso **construir** a passagem mista chamando o runner
directamente — a fonte real só entrega PDFs. E isso tem de vir com a razão
escrita ao lado: a pergunta aqui não é sobre a estrada (essa começa no botão e
mede-se noutra prova), é sobre **o que o ledger consegue exprimir**. Esperar que
a fonte um dia varie seria não medir.

## 86.4 · O ACHADO: O RUNTIME CALCULA A ARESTA E DEITA-A FORA

`guarda/preservar_derivado.py`, no reencontro, devolve os **dois lados**:

```
TESTEMUNHA_NO_BANCO       o raw_asset que a linha existente nomeia   (A)
TESTEMUNHA_DESTA_CHAMADA  o raw_asset que esta passagem trouxe        (B)
```

Distingue os dois casos de reencontro por escrito, em prosa, na explicação que
devolve. E não persiste nenhum.

```
    RUNTIME SABE ≠ O SISTEMA GUARDA.
    O QUE MORRE COM O PROCESSO NÃO É LINHAGEM.
```

Não faltava descobrir a aresta. Ela é calculada, nomeada, e perdida — que é uma
categoria de defeito diferente de «não sabemos», e muito mais barata de
consertar. Vale procurá-la noutros sítios: **onde é que este sistema já sabe
alguma coisa e só não a escreve?**

## 86.5 · A ASSIMETRIA DA LEI, VISTA AGORA COM NOME

`COL-LAW-008` diz que todo derivado deve responder `DERIVED_FROM`. Singular, e
cumprida: o derivado sabe de qual cópia nasceu, e o banco trava isso com uma
chave estrangeira **composta** sobre `(raw_asset_id, parent_sha256)` — o pai por
id e o pai por sha têm de ser o mesmo pai.

A lei nunca exigiu a recíproca: que cada observação saiba em que derivação
participou. Enquanto uma observação tinha no máximo um derivado, as duas
perguntas tinham a mesma resposta por acidente. O reuso separou-as.

```
    UMA LEI CUMPRIDA NUM SENTIDO NÃO ESTÁ CUMPRIDA NOS DOIS.
```

## 86.6 · E O PASSADO NÃO SE PREENCHE

A recomendação é aditiva — uma relação de **participação**, uma linha por
(observação, derivado, passagem), com dono no writer que já decide o reencontro.
Mas o histórico não tem cura:

```
    PREENCHER O PASSADO POR INFERÊNCIA
    É FABRICAR A EVIDÊNCIA QUE FALTAVA.
```

Uma migration que populasse a tabela por `sha256` escreveria como facto
exactamente aquilo que esta medição prova não ser sabido. O que se declara é o
começo; o que é anterior fica `UNKNOWN`, que é a verdade.

## 86.7 · «NÃO EXISTE» ERA LARGO DE MAIS — O CASO DO `canal_id`

A `§85` escreveu que o dono da identidade de canal «não existe». A medição
obriga a ser mais preciso, e a correcção é reutilizável:

```
SCHEMA OWNER                     EXISTE   origem · canal, migration 002
RUNTIME RESOLVER (ler + recusar) EXISTE   social_persistencia.exigir_canal
RUNTIME OWNER (decidir + criar)  NÃO      só testes e provas inserem
```

Três coisas diferentes debaixo da palavra «owner». Dizer que não existe owner
quando duas das três existem manda a missão seguinte construir o que já está
construído.

```
    ANTES DE DIZER QUE ALGO NÃO TEM DONO,
    DIGA QUAL DOS DONOS É QUE FALTA.
```

---

# §87 · METADE DE UM MECANISMO NÃO É UM MECANISMO A METADE: É NENHUM

**Missão:** `C10.8B-R — RAW PAGO NÃO MORRE NO CHECKOUT`
**Corrida:** `scrap-evidencia` run 34707069109 · dois runners, `ubuntu-latest`
**Gasto:** `APIFY_RUNS = 0 · PROVIDER_START_POSTS = 0 · PAID_USD = 0`

A `§84` descobriu que o bruto pago não sobrevivia ao job seguinte, e consertou a
**forma**. Esta missão foi buscar os **bytes** — e o que se aprendeu está quase
todo no caminho até lá, não no destino.

## 87.1 · A CASA JÁ SABIA SUBIR. NUNCA TINHA IDO BUSCAR

A busca pelo dono, antes de escrever qualquer linha, deu um resultado partido ao
meio:

```
actions/upload-artifact    vivo, com lei própria    scrap-social.yml
actions/download-artifact  ZERO workflows
```

Havia um dono do inventário com SHA, havia retenção declarada, havia até a lei
`UPLOAD STEP SUCCESS != ARTIFACT EXISTS` escrita à mão porque um passo verde com
zero ficheiros já tinha custado uma prova. Faltava a volta.

```
    GUARDAR SEM NUNCA TER IDO BUSCAR NÃO É GUARDAR. É ESPERAR.
```

Um mecanismo de transporte que nunca foi exercido nos dois sentidos é um
mecanismo não testado que **parece** testado, porque metade dele tem provas.
Vale para artefatos, para backups, para exports e para qualquer coisa que se
escreva com a intenção de um dia se ler.

## 87.2 · O BRUTO MAIS CARO DA CASA ERA O ÚNICO INVISÍVEL

O `coletor` — a porta paga — grava o bruto com gzip e SHA próprios. É o dono
daquele formato e, com razão, não passa pelo `guardar_raw` genérico. Só que
quem embala a evidência lê o inventário da corrida, e o inventário só conhece
quem passou pelo caminho genérico.

```
    O QUE O INVENTÁRIO NÃO VÊ NÃO ATRAVESSA A FRONTEIRA DO JOB.
```

O resultado é perverso e silencioso: os brutos **gratuitos** viajavam, e o único
que custou dinheiro ficava para trás. Ninguém escreveu essa regra; ela emergiu
de um dono legítimo ter um formato legítimo próprio.

A lição não é «centralizar tudo num dono». É que **um dono especializado tem de
se anunciar ao inventário** — a especialização é sobre o FORMATO, nunca sobre a
existência.

## 87.3 · UMA SONDA QUE NÃO DESCOMPRIME DÁ VERDE AO QUE NÃO CONSEGUE LER

O pacote recusa-se a levar seis formas de credencial. A primeira versão da sonda
lia os bytes do ficheiro e procurava os termos.

O bruto pago nasce **comprimido**. Um token dentro do gzip passaria inteiro — e
a sonda diria «limpo», com toda a confiança, sobre bytes que nunca leu.

```
    UMA SONDA QUE NÃO DESCOMPRIME DÁ VERDE AO QUE NÃO CONSEGUE LER.
```

O conserto foi olhar as duas formas. E a segunda metade importa tanto quanto a
primeira: um gzip **ilegível** devolve `GZIP_ILEGIVEL`, e não «limpo». Falhar a
ler não é a mesma coisa que ler e não encontrar — é a `§80` outra vez, noutra
roupa: `UNKNOWN != ZERO`.

A generalização: qualquer verificação sobre conteúdo tem de declarar o que
**não conseguiu inspeccionar**, ou o seu verde é sobre a sua própria cegueira.

## 87.4 · E A RECUSA NÃO PODE APAGAR A COISA QUE ELA PROTEGE

Havia um atalho óbvio: encontrar o segredo e redigi-lo, deixando o pacote
passar. É exactamente o que não se pode fazer.

```
    MELHOR FALHAR ALTO DO QUE REDIGIR EM SILÊNCIO:
    APAGAR EVIDÊNCIA PARA O PACOTE PASSAR DESTRÓI A COISA
    QUE O PACOTE EXISTE PARA GUARDAR.
```

Um RAW redigido é um RAW que já não é RAW, e ninguém a jusante saberia disso. A
recusa levanta, e nada é escrito — nem pacote meio feito.

## 87.5 · UM WORKFLOW SÓ SE PROVA NO RAMO ONDE FOI ESCRITO

Medido duas vezes, com o ficheiro já no remoto:

```
POST …/workflows/scrap-evidencia.yml/dispatches → 404 Not Found
```

`workflow_dispatch` só é disparável quando o ficheiro já vive no **ramo padrão**.
Um workflow novo, escrito num ramo de missão, não existe para a API que o
dispararia.

```
    UM WORKFLOW QUE SÓ O RAMO PADRÃO PODE DISPARAR
    NÃO PROVA NADA NO RAMO ONDE O MECANISMO FOI ESCRITO.
```

Junta-se à `§84.1`, e as duas juntas dizem a mesma coisa por dois caminhos: um
workflow que ninguém executa é um workflow que ninguém testou — e às vezes a
razão por que ninguém o executa é que **ainda não pode ser executado**. O
conserto foi um `push` com filtro de caminhos: quando o mecanismo muda, ele
volta a provar-se, no ramo onde está a ser construído.

## 87.6 · UMA SENTINELA QUE LÊ ESTADO GLOBAL MEDE QUEM CORREU ANTES DELA

Uma das quarenta sentinelas passava sozinha e ficava vermelha na suíte inteira.
Ela lia uma variável de módulo viva — e outra bateria redirecciona essa mesma
variável de propósito, para o bruto de teste não cair no acervo.

```
    UMA SONDA QUE LÊ ESTADO GLOBAL MEDE QUEM CORREU ANTES DELA.
```

É prima da `§77` (`um fake acima do gate mede o fake`) e da armadilha da sonda
que lê a própria prosa — três formas da mesma coisa: **a sonda tem de medir a
declaração, não o ambiente em que calhou correr**. Passou a ler o ficheiro que
declara a gaveta.

## 87.7 · UM MECANISMO TEMPORÁRIO QUE NÃO DIZ O PRAZO PASSA POR PERMANENTE

O pacote funciona. É por isso que ele tem de dizer, dentro de si, o que não é:

```
EVIDENCE_CLASS                   DIAGNOSTIC_JOB_TO_JOB
EVIDENCE_RETENTION               TEMPORARY · 30 dias
CANONICAL_FORWARD_PRESERVATION   NO
```

```
    WORKFLOW ARTIFACT != CANONICAL FORWARD STORAGE.
    PRESERVAÇÃO COM PRAZO É PRESERVAÇÃO COM PRAZO, E NÃO PRESERVAÇÃO.
```

Sem estas linhas, a missão seguinte encontra um transporte que funciona, conclui
que a preservação está resolvida, e o dono forward nunca é construído. Um
mecanismo que resolve 30 dias e não o declara **adia para sempre** o que resolve
o resto — e faz isso parecendo progresso.

A recuperação é pela identidade da corrida, e só por ela: não há volta que
escolha «o último artefato», porque um pacote de outra corrida com a mesma cara
não é este pacote. E o SHA do manifesto nunca é aceite sozinho — ele é uma
afirmação do pacote sobre si próprio; o recalculado é a medição.

## 87.8 · CONSEQUÊNCIA

```
JOB_A_ARTIFACT_ID    10302640238 · 228.283 + 719.722 bytes assinados
JOB_B_LOCAL_BEFORE   ABSENT   (runner distinto, checkout limpo)
JOB_B_RECOVERED      YES · SHA_MATCH YES · REPROCESS_ITEMS 20
REDE NO REPROCESSO   0 · PROVIDER_CALLS 0
ATAQUES 40 · MUTANTES 14 · SOBREVIVENTES 0
apify:transcricao    PARTIAL, intocada — nada correu no provider
CANONICAL_FORWARD_PRESERVATION = NO, por escrito, em cada pacote
```

Os 59.743 bytes da `§84` não voltam. Continua por saber por que aquele objeto
veio vazio, e continua a ser dinheiro que ninguém autorizou. O que mudou é que o
próximo bruto pago que alguém precise de reler **vai lá estar** — durante trinta
dias, e a contagem está escrita ao lado dos bytes.

---

# §88 · A VERSÃO DE UMA ENTRADA GERADA NÃO É O SEU CONTEÚDO: É A ÁRVORE QUE ELA MEDIU

**Missão:** `C-SYSTEM-MAP-G2-PERSIST-TOPOLOGY-CENSUS-V1`
**Linha:** `claude/dazzling-cerf-27a7v2` · **HEAD final:** `896e9bc1`
**Tocado:** `system-map/scripts/censo_da_topologia.py` ·
`system-map/tests/test_topologia_persistida.py` ·
`system-map/scripts/reconciliacao_do_universo.py` ·
`system-map/scripts/CADEIA-DO-MAPA.json` · `.github/workflows/system-map.yml` ·
`docs/arquitetura/SYSTEM-MAP-TRUST-CONTRACT.md`

A `§82` já tinha escrito que um artefato desactualizado é um artefato falso, e
que a pergunta certa não é «que commit?» mas «que ficheiros decidem isto?». Esta
secção é o que aconteceu ao aplicar essa lei a um censo cujas **entradas são
elas próprias artefatos gerados** — e as duas armadilhas que só aparecem aí.

## 88.1 · O QUE MUDOU

O censo da topologia publicava dezassete números — entre eles `111`, `65`, `590`
— e não escrevia ficheiro nenhum. O número entrava em documentação escrita à mão,
que é a definição de segundo dono.

```
    STDOUT NÃO É MEMÓRIA DURÁVEL.
```

Ele passou a escrever `system-map/data/topologia.generated.json`: as três
populações enumeradas membro a membro, a regra de entrada de cada uma, as arestas
no modelo dos quatro planos, e a proveniência com a versão de cada input que leu.

## 88.2 · A ARMADILHA DE HASHAR O CONTEÚDO DE UMA ENTRADA GERADA

A primeira versão versionava cada input pelo `sha256` do ficheiro. É o que a
`§82` ensina, e para uma **fonte** está certo.

Para uma **entrada gerada** está errado, e o erro só aparece no CI. Os dois
`.generated.json` que este censo lê são reescritos a cada corrida da cadeia, e
carregam `HEAD` e `GENERATED_AT` no carimbo. Regerar o mapa **sem mudar uma
linha da árvore** move o conteúdo deles — logo movia a versão, logo o artefato
nascia `STALE` em toda a corrida.

```
    UM ALARME QUE TOCA SEMPRE NÃO É UM ALARME: É UM RUÍDO QUE SE APRENDE A
    IGNORAR.
```

A versão certa de uma entrada gerada é a **impressão da árvore que ela carimba**.
Ela responde «que fontes mediste?», que é a pergunta de que a frescura precisa, e
fica quieta quando só o relógio andou.

```
FONTE            versão = SHA do blob que o git guardaria
ENTRADA GERADA   versão = SOURCE_TREE_FINGERPRINT que ela própria carimba
```

## 88.3 · DUAS PERGUNTAS SOBRE O MESMO FICHEIRO PRECISAM DE DOIS NÚMEROS

O artefato começou com um `SEMANTIC_HASH` só, a servir duas perguntas. Medido na
primeira corrida a sério: editar **um comentário** noutro ficheiro fez a
auto-observabilidade publicar `TOPOLOGY_COUNTS_REPRODUCIBLE = NO`. Nenhuma
contagem tinha mudado.

A causa é que as duas perguntas têm sensibilidades opostas:

| número | pergunta | tem de mudar quando |
|---|---|---|
| `MEASUREMENT_HASH` | as contagens reproduzem-se? | o grafo medido muda — **e só** |
| `SEMANTIC_HASH` | o ficheiro é o que o gerador escreveu? | **qualquer** campo não volátil muda |

O segundo tem de incluir a proveniência, senão adulterar um carimbo passa
despercebido. O primeiro tem de a excluir, senão grita a cada commit.

```
    UM NÚMERO QUE RESPONDE A DUAS PERGUNTAS RESPONDE MAL ÀS DUAS.
```

## 88.4 · O TERCEIRO RELÓGIO: QUEM SÓ SE COMPARA CONSIGO NUNCA SE DESCOBRE VELHO

Dois relógios — «a árvore mudou?» e «alguma entrada mudou?» — comparam o
artefato **consigo mesmo no tempo**. Os dois diziam `CURRENT` num artefato
gerado sobre um `state.generated.json` de três árvores atrás: ninguém tinha
mexido em nada **desde** que ele correu.

```
    REGERAR SOBRE UMA ENTRADA VELHA NÃO TORNA A ENTRADA NOVA:
    TORNA A MENTIRA MAIS RECENTE.
```

O terceiro relógio pergunta outra coisa: **cada entrada gerada mediu esta
árvore?** Quando não mediu, o veredito é `STALE` com motivo `STALE_BY_CYCLE` —
a lei do ciclo atrasado do contrato de confiança, aplicada a um artefato.

Ele **nomeia** e não repara: ordenar a cadeia pelos `INPUTS` declarados é outro
trabalho, e um censo que reordenasse a cadeia deixava de ser um censo.

## 88.5 · A PROVA, E O QUE ELA MEDIU

`test_topologia_persistida.py` — 83 provas — não lê o artefato à procura de
confirmação: regenera, adultera e compara. Cada guarda é mordida com o defeito
que devia apanhar (contagem sem membros, vizinho contado como coleta, aresta
duplicada, texto reescrito à mão), e as três populações são **recontadas a
partir do estado**, não lidas do próprio ficheiro.

```
    CONFERIR UM ARTEFATO CONTRA ELE PRÓPRIO NÃO É CONFERIR NADA.
```

E a frescura não é lida no artefato: um ficheiro não se declara actual a si
mesmo. Quem responde `CURRENT · STALE · UNVERIFIABLE · UNKNOWN` é outro processo,
contra a árvore de agora.

## 88.6 · TRÊS ALARMES QUE SÓ SE TESTAM JUNTOS SÃO UM ALARME SÓ

Dezassete mutantes, zero sobreviventes — mas dois deles só morreram depois de a
mutação encontrar um buraco que eu não tinha visto.

Apagar o relógio da árvore **não reprovava nada**. Apagar o das entradas
**também não**. A razão é que todas as provas de frescura corriam sobre uma
árvore mexida, e numa árvore mexida os três relógios tocam ao mesmo tempo: os
outros dois tapavam o buraco e a prova dizia `PASS` sobre uma guarda que já não
existia.

```
    UMA GUARDA QUE SÓ É TESTADA JUNTO COM AS OUTRAS
    NÃO FOI TESTADA: FOI ACOMPANHADA.
```

A correcção foi morder cada relógio **sozinho**, mexendo só no carimbo que ele
lê. E o arnês de mutação tinha o seu próprio defeito: ao mutar uma fonte, ele
movia a árvore e deixava o relógio do ciclo aceso em todas as corridas. Um arnês
que deixa um alarme sempre ligado não testa os outros.

## 88.7 · PERSISTIR UMA MEDIÇÃO É O QUE DESCOBRE QUE ELA NUNCA FOI REPRODUTÍVEL

O passo novo do CI reprovou, e a razão não era do artefato: era do censo, e
estava lá desde sempre. `DOCUMENTADO_COMO_CLI` divergiu em **seis cartões** entre
a mesma árvore medida aqui e no GitHub Actions.

```
C-CADEIA-V21      CHECKPOINT-INTEGRACAO-ACERVO-PORTAL.md  ·  HANDOFF-V2-PAUSE.md
C-IT-CONTRATOS    BIBLIA-CANONICA-DA-COLETA.md            ·  ITALY-SOURCE-CONTRACT-MATRIX-V1.md
C-MAPA-GERADOR    system-map/README.md                    ·  regras/LEIA-ANTES-DE-COLETAR.md
C-ORQUESTRADOR    BIBLIA-CANONICA-DA-COLETA.md            ·  (vazio)
C-PACOTE-CAMADAS  HANDOFF-CONTA-CLAUDE-SINTONIA-EAME.md   ·  PROMPT-PARA-NOVA-CONTA-CLAUDE.md
C-PROCEDENCIA     HANDOFF-CONTA-CLAUDE-SINTONIA-EAME.md   ·  PROMPT-PARA-NOVA-CONTA-CLAUDE.md
```

A função para no primeiro `.md` que casa e só vê as primeiras 20 linhas do
`grep` — e a ordem do `grep` é do sistema de ficheiros, não do código. O caso
`C-ORQUESTRADOR` é o mais duro: o tecto cortou as 31 linhas **antes** da que
casava, e o campo saiu vazio. Ele nem sequer responde «está documentado?».

Enquanto o número só passava pelo terminal, ninguém tinha como reparar. **Foi o
artefato que o denunciou**, e foi preciso o CI — outra máquina, outra ordem — para
ele aparecer. Duas árvores no mesmo disco tinham dado igual.

```
    UM CAMPO QUE NÃO SE CONSEGUE REPRODUZIR NÃO PODE SER PROVA DE DRIFT.
```

A saída não foi consertar a função — isso é mudar a semântica da medição, e era
outro trabalho. Foi **declarar**: o campo sai do `MEASUREMENT_HASH` com o motivo
carimbado ao lado, continua publicado cartão a cartão, e continua coberto pelo
`SEMANTIC_HASH` contra adulteração. O que deixou de valer foi a promessa que ele
nunca conseguiu cumprir.

```
    ESCONDER UM CAMPO INSTÁVEL DENTRO DE UM HASH ESTÁVEL
    É TRANSFORMAR UMA MEDIÇÃO FRACA NUM VEREDITO FORTE.
```

E uma lista de exclusão que cresce sem prova é um silenciador: os três nomes
estão fixados na prova, o artefato tem de os declarar com motivo, o campo tem de
continuar publicado, e adulterá-lo tem de continuar a reprovar. Acrescentar um
quarto obriga a mexer na prova — e mexer na prova obriga a escrever porquê.

## 88.8 · CONSEQUÊNCIA

Qualquer contagem de topologia publicada pode agora ser auditada depois: o número
aponta para o artefato, o artefato enumera os membros, declara a regra, nomeia o
gerador, versiona cada input e sabe dizer se ainda vale. E as três populações
— coleta, vizinhos de fronteira, união — deixaram de caber na mesma palavra.

```
    UM VIZINHO DA COLETA NÃO VIRA MEMBRO DA COLETA.

# §89 · UMA ROTA OFICIAL QUE NINGUÉM MODELOU NÃO ESTÁ BLOQUEADA: ESTÁ POR OLHAR

> **Fonte:** `docs/sintonia-scrap/META-DEEP-STUDY-V1.md`,
> `META-ROUTE-MATRIX-V1.json`, `META-COMPETITOR-COVERAGE-V1.md`.
> Medido em 2026-09-12 · `META_PLATFORM_PROBES = 0` · `APIFY_RUNS = 0` · `COST_USD = 0`.

A `§83` escreveu que uma linha de código prova que algo *consegue*, não que algo
*aconteceu*. Esta secção acrescenta o degrau anterior, e ele é mais barato de
errar: **antes de perguntar se a casa consegue, alguém tem de ter perguntado se
a rota existe.**

O estudo varreu a família Meta inteira e encontrou a maior rota oficial,
gratuita e permitida para observar concorrentes — a **Meta Ad Library** — sem
uma única ocorrência no repositório. Não bloqueada. Não recusada. Não medida e
reprovada. **Ausente.** O mesmo para o *Branded Content Search*.

```
    AUSENTE NÃO É UM ESTADO DE CAPACIDADE. É A FALTA DE UM.
    E o vocabulário fechado não avisa: `social_matriz.CAPACIDADES` tem doze
    palavras e nenhuma delas nomeia «anúncio». Uma rota que não tem nome não
    pode ser declarada `BLOCKED` — nem sequer chega a ser perguntada.
```

## 89.1 · OFFICIAL-FIRST MUDA O PAPEL DA APIFY, E NÃO O PREÇO DELA

**O QUE MUDOU.** Onde existe rota oficial e gratuita, a Apify deixa de ser
candidata a motor e passa a ser cobertura de **buraco residual**.

**POR QUÊ.** Sete actors de Ad Library vendem, entre US$ 0,55 e US$ 17,00 por
mil, a leitura de uma fonte cuja API oficial custa zero e cobre a Itália. O que
eles dão a mais é o criativo em pixels, arrancado da página de *snapshot* —
rota que documentação nenhuma garante.

**PROVA.** `META-DEEP-STUDY-V1.md`, Parte 19 e Parte 28; `gap_apify()` medido no
próprio repositório.

**CONSEQUÊNCIA.** Comprar por item o que a rota oficial entrega de graça é pagar
pela diferença entre não ter credencial e ter. O motivo canónico de gasto passa
a ter de distinguir isso — e a casa já tem as duas palavras:
`FREE_ROUTE_UNAVAILABLE` ≠ `AUTHORIZATION_BLOCK`.

## 89.2 · JANELA CURTA TORNA O DELTA UMA NECESSIDADE DE PRESERVAÇÃO

**O QUE MUDOU.** O delta deixa de ser optimização de custo e passa a ser a única
forma de a casa ter histórico.

**POR QUÊ.** A janela comercial da Ad Library na UE é de **um ano a contar da
última impressão** — não de sete, que é a janela do corpus político. O que não
for colhido enquanto está lá desaparece e não volta.

**PROVA.** `META-DEEP-STUDY-V1.md` §5: `COMMERCIAL_EU_HISTORY = 1 ANO a contar
da última impressão`, citado da documentação primária da Meta.

**CONSEQUÊNCIA.**

```
    NÃO HÁ CATÁLOGO ANTIGO A RECUPERAR. Colheita rolante, nunca consulta
    retrospectiva. E como a Meta não emite sinal de remoção, «sumiu do
    resultado» tem quatro causas possíveis e só uma delas é «o anúncio parou».
```

## 89.3 · A CASA DECLAROU UM BURACO PAGO CITANDO O FICHEIRO QUE O DESMENTE

**O QUE MUDOU.** `INSTAGRAM/FETCH_COMMENTS` era a única linha da Meta a dizer
«APIFY NECESSÁRIA», com o motivo `FREE_ROUTE_INSUFFICIENT_CAPABILITY` — «a rota
grátis dá o NÚMERO, nunca o TEXTO».

**POR QUÊ ESTAVA ERRADO.** O ficheiro citado como evidência mede o contrário.
`coleta/instagram_janela.py` regista, em comentário de código: *«MEDIDO em 7
posts das 5 contas do lote, deslogado: 18 de 31 comentários declarados saíram
COM TEXTO — 58%.»*

**PROVA.** O código, e o RAW pago em `ES-T8-003-instagram-hashtags.raw.json.gz`:
`commentsCount` soma 31 e `latestComments` traz **zero** comentários em 60 de 60
itens — a rota paga entregou a contagem e não o texto.

**CONSEQUÊNCIA, E ELA TEM DUAS METADES QUE NÃO SE ANULAM.**

```
    COMMENT_COUNT != COMMENT_TEXT — continua verdade.
    E 18/31 TAMBÉM NÃO É 31/31.
```

Uma medição parcial não promove a rota grátis a suficiente, e não autoriza
declarar a paga necessária universalmente. O estado honesto é **parcial**, e o
motivo do gasto muda de «a rota grátis não sabe» para «a rota grátis não é
permitida» — que é uma frase sobre autorização, não sobre capacidade.

## 89.4 · `AUDIO_ONLY` É PROPRIEDADE DO ITEM, NÃO DA PLATAFORMA

**O QUE MUDOU.** A `C10` provou aquisição só-áudio num Reel: `-f bestaudio`
seleccionou uma representação DASH de áudio, `VIDEO_BYTES_DOWNLOADED = 0`. Essa
prova **continua de pé** e não é rebaixada aqui.

**POR QUÊ PRECISA DE CERCA.** Evidência pública de terceiros mostra itens do
mesmo Instagram cuja tabela de formatos não tem **nenhuma** linha `audio only` —
só DASH de vídeo e MP4 muxado. Nesses, extrair áudio é *demux local*, não
poupança de rede.

**PROVA.** `META-DEEP-STUDY-V1.md`, Parte 13, com os dois sentidos medidos.

**CONSEQUÊNCIA.**

```
    A ÚNICA PROVA FIÁVEL É A TABELA DE FORMATOS DAQUELE ITEM.
    UM REEL NÃO É UM LOTE. Orçar banda com «Reel = ~200 KB de áudio» é
    generalizar uma medição de um caso para uma plataforma inteira.
```

## 89.5 · A LIÇÃO TRANSVERSAL: DINHEIRO E CREDENCIAL SÃO EIXOS DIFERENTES

Sete das nove observações que um concorrente completo exigiria custam **zero
dólares**. As sete estão fechadas — por App Review, verificação de negócio ou
confirmação de identidade.

```
    USD_COST = 0  NÃO SIGNIFICA  EXECUTÁVEL AGORA.
    Uma rota que custa zero e exige aprovação que a casa não tem é tão
    inalcançável hoje quanto uma que custasse mil — e mais perigosa, porque
    o número zero convida a chamar-lhe «grátis» e a dá-la por pronta.
```

## 89.6 · O QUE ESTA SECÇÃO NÃO AFIRMA

Nenhuma rota Meta foi executada. Nenhuma foi promovida a `PROVED`. Nenhuma
política mudou por causa deste estudo. O que ele entrega é o mapa — e a
distinção entre não conseguir e não ter olhado.

```
    CAN DO ≠ MAY DO ≠ DID DO ≠ EVER ASKED.
```
