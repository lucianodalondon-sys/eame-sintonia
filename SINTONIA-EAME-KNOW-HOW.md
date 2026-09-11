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
