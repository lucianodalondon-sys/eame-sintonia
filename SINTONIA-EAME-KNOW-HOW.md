# SINTONIA EAME — KNOW HOW

> Memória operacional durável do projeto.  
> **Não é a Bíblia canônica. Não é o System Map. Não é um relatório de status.**  
> É o registro do **como pensamos, por que decidimos, como investigar, como construir, como provar e quais erros não repetir**.

**Criado em:** 2026-09-09  
**Repositório:** `lucianodalondon-sys/eame-sintonia`  
**Branch de criação:** `claude/sintonia-eame-know-how-v1`  
**Base de criação:** `572647dce8a38b8835aafa6f9e3e42d2652fbcd9`  
**Regra:** atualizar todos os dias em que houver avanço material de arquitetura, metodologia, medição ou decisão.

**Última atualização material:** 2026-09-11 — o `READER_GAP` de `SOURCE_ID` foi fechado no forward (§61) e a ordem do projeto foi fixada: fechar toda a Collection, integrar o SCRAP, fazer coleta grande, só então Intelligence e Casco (§62).  
**Próximo passo mínimo:** decidir o tratamento dos `13 OUT_OF_FLOW_EVIDENCE` à luz da `COL-LAW-045`, sem backfill, identidade inventada ou atalhos; depois continuar o fechamento medido da Collection.

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
só, e ao módulo. Ninguém tinha corrido o fluxo. O censo classif…82634 chars truncated…