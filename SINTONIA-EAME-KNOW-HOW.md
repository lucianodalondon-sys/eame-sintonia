# SINTONIA EAME — KNOW HOW

> Memória operacional durável do projeto.  
> **Não é a Bíblia canônica. Não é o System Map. Não é um relatório de status.**  
> É o registro do **como pensamos, por que decidimos, como investigar, como construir, como provar e quais erros não repetir**.

**Criado em:** 2026-09-09  
**Repositório:** `lucianodalondon-sys/eame-sintonia`  
**Branch de criação:** `claude/sintonia-eame-know-how-v1`  
**Base de criação:** `572647dce8a38b8835aafa6f9e3e42d2652fbcd9`  
**Regra:** atualizar todos os dias em que houver avanço material de arquitetura, metodologia, medição ou decisão.

**Última atualização material:** 2026-09-12 — §98: um portão que só se alcança com inventário não é um portão de política; um redirecionamento é um pedido novo.
**Próxima missão autorizada:** NÃO DEFINIDA NESTE DELTA — medir estado e objetivo antes de abrir nova missão.

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

> **SUPERADA — ver §109.7.** O contrato tem **12** campos desde
> `C-READY-LINEAGE-BEFORE-SCALE-V1`: `RAW_OBSERVATION_ID` entrou. A frase
> acima fica por ser o registo da data dela; o estado de hoje é o do §109.7.

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

Contrato READY tem 11 campos. **SUPERADA — hoje são 12; ver §109.7.**

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

## 88.8 · A DÍVIDA FOI FECHADA, E O QUE FALTAVA ERA AO TESTE

A `88.7` acaba em «declarar». A missão seguinte fechou a causa, e o caminho até
lá vale uma linha que não está em mais lado nenhum.

Para consertar era preciso primeiro **reproduzir**, e reproduzir não deu com dois
clones: no mesmo `ext4` o `readdir` devolve os nomes pela mesma ordem, os dois
clones concordavam, e a prova passava com o defeito na mão. O que separou os dois
resultados foi o **sistema de ficheiros**: `tmpfs` devolve por ordem de criação.
Mesma árvore git, outro disco, dez cartões diferentes.

```
    UMA PROVA DE DETERMINISMO QUE SÓ SE CORRE NUM DISCO MEDE O DISCO.
```

Isto é geral e barato: onde uma medição toca o sistema de ficheiros, a segunda
árvore da prova tem de estar noutro sistema de ficheiros, e há sempre um à mão.

A correcção em si não teve nada de esperto — teve de deixar de perguntar ao
disco. A lista de documentos passou a vir de `git ls-files`, ordenada; o tecto
das 20 linhas saiu; e a resposta passou a ser **todos** os documentos que casam,
não o primeiro. Ler os 287 documentos inteiros custa 14 milissegundos e
substitui 358 varreduras do repositório: o caminho determinístico era também o
mais barato, e a única razão para não o ter feito antes era não ter perguntado.

```
    LER TUDO UMA VEZ BATE PROCURAR MUITAS — E AINDA POR CIMA DÁ SEMPRE
    A MESMA RESPOSTA.
```

## 88.9 · CONSEQUÊNCIA

Qualquer contagem de topologia publicada pode agora ser auditada depois: o número
aponta para o artefato, o artefato enumera os membros, declara a regra, nomeia o
gerador, versiona cada input e sabe dizer se ainda vale. E as três populações
— coleta, vizinhos de fronteira, união — deixaram de caber na mesma palavra.

```
    UM VIZINHO DA COLETA NÃO VIRA MEMBRO DA COLETA.
```

---

# §89 · UMA TRADUÇÃO E UMA COMPRA DECIDEM AUTORIZAÇÃO, E NENHUMA DAS DUAS PARECE UMA DECISÃO

**Missão:** `LINKEDIN-BUILD-01` + `LINKEDIN-POLICY-01`
**Linha:** `claude/festive-fermi-1k2mf5` · **HEAD final:** `ab115d23`
**Tocado:** `coleta/scrap_capacidades.py` · `coleta/adaptador_linkedin.py` ·
`docs/sintonia-scrap/LINKEDIN-POLICY-01-ROTAS-AUTORIZAVEIS.md` ·
`docs/sintonia-scrap/LINKEDIN-ROUTE-MATRIX-V1.json`

A `§84.4` já tinha escrito `PROVIDER REACHED != CAPABILITY DELIVERED` — chegar
ao fornecedor não é ele entregar. Esta secção acrescenta as duas perguntas que
vêm **antes** dessa, e que são de autorização e não de capacidade: *quem decide
qual permissão é consultada?* e *pagar muda a resposta?*

As duas leis abaixo têm a mesma forma perigosa: a decisão acontece num sítio que
ninguém lê como sítio de decisão. Uma vive num campo de tradução; a outra, numa
fatura.

## 89.1 · O QUE MUDOU — UM CAMPO DE TRADUÇÃO CONCEDIA UMA PERMISSÃO

`coleta/scrap_capacidades.py` traduz o vocabulário fino das capacidades
(`linkedin.recent.discovery`) para o vocabulário grosso da política
(`DISCOVER_ACCOUNT`). O campo existe para que os dois vocabulários coexistam sem
que um se imponha ao outro, e foi escrito como conveniência de nomenclatura.

Medido: `linkedin.recent.discovery` — **as publicações recentes da página de
empresa** — traduzia para `DISCOVER_ACCOUNT`. E
`social_matriz.decisao('LINKEDIN','DISCOVER_ACCOUNT')` devolve **`ALLOWED`**.

A única rota debaixo daquela permissão é
`descoberta-indireta:site-da-organizacao`: ler o site **da própria organização**
para lhe achar o endereço. A própria matriz escreve o limite ao lado — «Guarda
`DISCOVERY_SOURCE`, `DISCOVERED_URL`, `TARGET_TYPE`, `DISCOVERED_AT`, e **nunca
conteúdo de post fabricado**».

```
    «AS PUBLICAÇÕES DA PÁGINA» E «O ENDEREÇO DA CONTA» SÃO DOIS ACTOS, E A
    TRADUÇÃO FAZIA O PRIMEIRO PEDIR EMPRESTADA A PERMISSÃO DO SEGUNDO.
```

## 89.2 · POR QUE ISTO NÃO REBENTOU, E POR QUE ISSO É O PIOR DA HISTÓRIA

Nenhuma linha de código explorava o defeito, por uma razão acidental: nenhuma
das sete capacidades de LinkedIn tinha rota ligada. A porta estava destrancada
por dentro de uma casa vazia.

Um erro de tipo rebenta. Um erro de nome rebenta. Um erro de **tradução de
permissão** não rebenta — ele responde `ALLOWED` e a execução segue em frente.

```
    UMA TRADUÇÃO ERRADA NÃO FALHA. ELA AUTORIZA.
    TRANSLATION IS AUTHORIZATION.
```

E há uma segunda propriedade que só se vê depois: enquanto duas capacidades
apontassem para a mesma capacidade grossa, `cap.pela_matriz()` devolveria a
primeira que encontrasse. **O dono de uma permissão seria decidido por ordem de
dicionário.**

## 89.3 · PROVA

```
ANTES   cap.pela_matriz('LINKEDIN','DISCOVER_ACCOUNT') -> linkedin.recent.discovery
        mz.decisao('LINKEDIN','DISCOVER_ACCOUNT')       -> ALLOWED
DEPOIS  cap.pela_matriz('LINKEDIN','DISCOVER_ACCOUNT') -> linkedin.identity.discovery
        donos declarados de DISCOVER_ACCOUNT no LINKEDIN -> 1
```

Corrigido em `a418f040`. O desenho não é novo: o Facebook já tinha
`facebook.identity.discovery` a apontar para `DISCOVER_ACCOUNT`, e o LinkedIn
passou a ter o mesmo. A correcção **retira** uma permissão que estava concedida
pelo nome errado — não abre nenhuma.

## 89.4 · CONSEQUÊNCIA DA PRIMEIRA LEI

O campo que traduz entre dois vocabulários de capacidade **é uma superfície de
permissão**, não um apelido e não canalização neutra.

```
    TODA TRADUÇÃO QUE MUDA A POLÍTICA CONSULTADA É UMA DECISÃO DE AUTORIZAÇÃO,
    E PRECISA DE PROVA E DE SENTINELA PRÓPRIAS.
```

Na prática, três obrigações:

1. mudar o campo de tradução entra na revisão de **política**, não só na de código;
2. cada capacidade grossa tem **um** dono declarado por plataforma, e isso
   confere-se — um segundo dono é uma permissão decidida por ordem alfabética;
3. um teste que leia a tradução e a decisão **juntas**, porque separadas as duas
   estão sempre certas.

## 89.5 · O QUE MUDOU — E A SEGUNDA PERGUNTA: PAGAR AUTORIZA?

A `LINKEDIN_LOCAL_FIRST` terminou em `PARTIAL` com uma pergunta aberta: para
conteúdo de terceiro no LinkedIn não há rota livre permitida — **comprar de um
fornecedor pago torna a aquisição autorizada?**

A resposta não veio da plataforma-alvo. Veio do contrato do próprio fornecedor.
`docs.apify.com/legal/general-terms-and-conditions`, em vigor **2026-07-09**,
lido em 2026-09-12:

> **§6.2** — «You must use the Services to process only the Customer Data that
> **you are authorized to access**…»

> **§11.1** — «Should you use the Services or Actors to extract Customer Data
> from **unauthorized sources**, **you shall be responsible** for compensating
> any damages incurred by and/or any claims of the affected third parties.»

> **§11.1** — «You agree to **indemnify, defend and hold us … harmless**…»

```
    O FORNECEDOR NÃO ASSUME A AUTORIZAÇÃO. DEVOLVE-A AO CLIENTE, POR ESCRITO,
    NO CONTRATO QUE SE ASSINA AO PAGAR.
```

## 89.6 · POR QUÊ, E ONDE ESTÁ A TENTAÇÃO

A tentação é estrutural e não é preguiça: o roteador escolhe a rota mais barata
**capaz**, e um Actor pago é, quase sempre, capaz. Se «capaz» fosse o único
eixo, uma rota directa recusada seria automaticamente substituída por uma rota
paga que faz a mesma coisa — e o relatório diria `OK`.

```
    PAID PROVIDER IS NOT A POLICY OVERRIDE.
    Preço e terceirização respondem CAPACIDADE. Nunca respondem PERMISSÃO.
```

E a pergunta certa sobre um fornecedor não é quanto custa nem quantos o usam. É
**qual é o mecanismo dele e qual é a base contratual dele** — porque um
fornecedor que apenas encapsula a técnica que a casa recusou é a mesma técnica
com uma fatura à frente.

## 89.7 · PROVA

Da `LINKEDIN-POLICY-01`, oito rotas inventariadas e sete fornecedores censados:

```
CLASSE A · rota de fornecedor aceitável           0
CLASSE B · contrato/mecanismo insuficientes       4   mecanismo = UNKNOWN
CLASSE C · incompatível com a política            2
```

Os dois da classe C caíram **pelo que dizem de si próprios**, não pela loja onde
vivem: um pede os **nossos** cookies de sessão — é a rota autenticada comprada,
com a nossa credencial; o outro declara «Google-based search» — é a rota de
índice comprada, e o §8.2(4) do User Agreement nomeia «search tools» ao lado de
«data aggregators or brokers».

```
    ACTOR != LEGAL/POLICY STATUS. Nenhum caiu por ser Apify, e nenhum subiu por
    ser barato.
```

E a sentinela, que corre nos **dois** sentidos:

```
    MECANISMO DESCONHECIDO NÃO É PROIBIDO AUTOMATICAMENTE,
    E NÃO É PERMITIDO AUTOMATICAMENTE.  É `REQUIRES_HUMAN_DECISION`.
```

## 89.8 · CONSEQUÊNCIA DA SEGUNDA LEI

Se uma rota directa está `NOT_ALLOWED`, o roteador **não pode** seleccionar
sozinho um Actor pago que faça o mesmo. Um fornecedor só é rota distinta quando
tem **contrato, mecanismo e procedência próprios** — e isso prova-se, não se
presume por ele existir e aceitar dinheiro.

```
    SE O PROVIDER APENAS ENCAPSULA A TÉCNICA RECUSADA, SEM BASE CONTRATUAL
    PRÓPRIA, ENTÃO  PAID_ROUTE != ALLOWED.
```

Três consequências operacionais:

1. a decisão de rota paga precisa do **motivo canónico** e, agora, também da
   **classe do fornecedor** — A, B ou C;
2. quando o único caminho para um campo é uma rota que a política recusa, o
   resultado é `BLOCKED_NO_PERMITTED_ROUTE`, **nunca** «precisa de dinheiro»;
3. ler os termos do fornecedor é um passo **grátis** que vem antes do gasto —
   irmão do `inputSchema` da `COL-LAW-018`. E ele pode falhar: o fornecedor cujos
   dados esta casa possui devolveu **HTTP 403** aos seus próprios termos, deste
   IP, nas duas tentativas. Isso é um `UNKNOWN` material, não um detalhe.

## 89.9 · E A LEI QUE JÁ EXISTIA GANHOU UM IRMÃO MAIS VELHO

A `§84.4` diz que chegar ao fornecedor não é ele entregar. A `§89` diz que pagar
ao fornecedor não é ter permissão. Juntas, e na ordem em que se perguntam:

```
    PODEMOS?          →  política e procedência do fornecedor   (§89)
    ELE CONSEGUE?     →  capacidade                             (§84.4)
    ELE ENTREGOU?     →  o payload, contado campo a campo       (§84.4)
```

Três perguntas, três respostas independentes. Um relatório que colapse duas
delas está a dizer a verdade sobre uma e a enganar sobre a outra — que foi
exactamente o defeito que a `§84.4` nasceu para nomear.

---

# §90 · ESCOLHER A CHAVE ANTES DO CONCEITO É DECIDIR A FORMA SEM SABER O QUE SE GUARDA

**Missão:** `C-DECIDE-DERIVED-PARTICIPATION-GRAIN-V1` (decisão, sem implementação)
**HEAD final:** `0a2992c4`
**Decisão:** [`docs/decisoes/ADR-LINHAGEM-DO-REAPROVEITAMENTO-V1.md`](docs/decisoes/ADR-LINHAGEM-DO-REAPROVEITAMENTO-V1.md)
**Medição:** `provas/a_linhagem_do_reaproveitamento.py`

A `§86` mediu o buraco e recomendou uma tabela. E a recomendação saiu
contraditória: dizia que o grão era `(observação, derivado, passagem)` e que a
identidade incluía `run_id` — e três parágrafos abaixo dizia que a entrada do
`run_id` na chave estava **em aberto**.

Escrevi as duas coisas no mesmo documento, no mesmo dia, sem dar por isso.

```
    O ERRO NÃO FOI DE REDAÇÃO.
    FOI TER ESCOLHIDO A CHAVE ANTES DO CONCEITO.
```

Uma chave é uma resposta à pergunta «o que é que duas linhas iguais
significariam?». Sem saber o que a tabela representa, essa pergunta não tem
resposta — e o que sai é uma chave plausível com uma dúvida pendurada.

## 90.1 · A PERGUNTA QUE SEPARA, E COMO SE MEDE

Duas perguntas parecidas, e não são a mesma:

```
L · LINHAGEM   esta observação participou deste derivado?
E · EXECUÇÃO   em que passagem isso aconteceu, e com que resultado?
```

> ⚠️ **CORRECÇÃO, E ELA É A LIÇÃO MAIOR DESTA SECÇÃO.**
> A primeira versão desta `§90.1` dizia «contam-se as duas coisas nos mesmos
> casos reais» e mostrava **1 aresta contra 6 eventos**. Os dois números não
> mediam o mesmo conjunto: o `1` excluía o caso 3 — justamente o que cria a
> segunda aresta — e o `6` incluía as passagens do arranque e do diagnóstico,
> que não pertencem a caso nenhum.
>
> A conclusão estava certa. A prova que a sustentava, não.
>
> ```
>     DOIS NÚMEROS SÓ SE COMPARAM SE MEDIREM O MESMO CONJUNTO.
>     UM RACIOCÍNIO CERTO APOIADO NUM NÚMERO ERRADO
>     É UM RACIOCÍNIO POR CONFIRMAR — E PARECE PROVADO.
> ```
>
> Uma razão entre dois contadores é a forma mais convincente de errar, porque
> o leitor confere a divisão e nunca as populações.

Os quatro casos, cada um com o que ele próprio tocou:

```
caso 1  RUN A, raw 1 -> derivado 3        aresta 1→3   NOVA    PASSED
caso 2  retry na MESMA corrida            aresta 1→3   a mesma REUSED
caso 3  RUN B, raw 5, mesmos bytes        aresta 5→3   NOVA    REUSED
caso 4  rederivar raw 1 noutra corrida    aresta 1→3   a mesma REUSED
```

E os contadores, **cada um com o universo no próprio nome**:

```
MATERIAL_EDGES_ALL_FOUR_CASES              2   as arestas distintas dos casos 1-4
PASSAGES_TOUCHING_ORIGINAL_EDGE            3   casos 1, 2 e 4, todos sobre 1→3
DERIVED_STAGE_PASSAGES_TOTAL_IN_SCENARIO   6   TODAS as passagens do cenário,
                                               arranque e diagnóstico incluídos
```

A separação dos conceitos não sai de dividir um pelo outro. Sai de **duas
propriedades**, cada uma medida dentro do seu próprio universo:

```
P1   a MESMA aresta 1→3 foi tocada por 3 passagens      → PASSAGEM ≠ ARESTA
P2   o caso 3 criou a aresta 5→3 sobre o MESMO derivado,
     e `derived_artifact` ficou em 4 → 4                 → ARESTA ≠ DERIVADO
```

Duas propriedades chegam. E a regra que fica é mais útil do que a conclusão:

```
    PARA SABER SE SÃO DOIS CONCEITOS, PROCURE UM CASO ONDE UM MUDA
    E O OUTRO NÃO — E NÃO UMA RAZÃO ENTRE DOIS TOTAIS.

    UM CONTADOR SEM UNIVERSO NO NOME É UM CONVITE À COMPARAÇÃO ERRADA.
```

## 90.2 · DOIS CONCEITOS NÃO SÃO DUAS TABELAS NOVAS

O reflexo, depois de provar que são dois, é criar dois donos. Estava errado: o
conceito de **passagem** já tem casa — `etapa_da_corrida`, uma linha por
`(run_id, etapa, tentativa)`.

```
    DOIS CONCEITOS, DOIS DONOS — E SÓ UM DELES PRECISA DE NASCER.
```

⚠️ **E aqui escrevi uma segunda imprecição, corrigida depois:** dizer que «o
evento de execução já tem dono» apaga uma distinção que a medição obriga a
fazer. São **três** coisas, e não duas:

```
MATERIAL LINEAGE   dono NOVO, e é o que falta
PASSAGE EVENT      dono EXISTENTE — etapa_da_corrida, em agregado
ITEM EXECUTION     SEM dono de persistência — medido, e não suposto
```

O balde guarda **quantos** itens foram reaproveitados, e nunca **quais**. Numa
passagem mista (`{ERROR: 1, REUSED: 1}`) nada no estado persistido separa as
duas observações.

```
    CONTAGEM POR PASSAGEM ≠ RESULTADO POR ITEM.
    NÃO SE CONSTRÓI POR ANTECIPAÇÃO —
    E TAMBÉM NÃO SE DIZ QUE JÁ EXISTE O QUE NÃO EXISTE.
```

Continua a não se construir a tabela por item — mas por **outra razão**: não
porque já exista, e sim porque nenhuma necessidade provada a exige. A pergunta
que a motivava («esta observação foi processada?») passa a ter resposta pela
**existência da aresta**, sem histórico por item.

## 90.3 · A SENTINELA: A CORRIDA QUE DERIVA PODE NÃO SER A QUE CAPTUROU

O caso 4 é o que fecha a decisão. Derivei outra vez uma observação da corrida A,
numa passagem que pertence à corrida B — e **o banco aceitou**.
`etapa_da_corrida.run_id` exige que a corrida exista, não que seja a que
capturou.

Com `run_id` na chave da aresta, o mesmo facto material teria duas linhas. E há
uma pergunta que essa chave nem consegue formular:

```
    QUAL run? A QUE CAPTUROU, OU A DA PASSAGEM QUE DERIVOU?
```

```
    UMA CHAVE QUE NÃO SABE RESPONDER «QUAL DOS DOIS?»
    NÃO É UMA IDENTIDADE: É UMA AMBIGUIDADE COM ÍNDICE.
```

O `run_id` fica, mas como **proveniência**: a corrida da passagem em que a
aresta foi vista pela primeira vez. E o nome tem de dizer isso, porque um
`run_id` seco seria lido como «a corrida desta aresta», que não existe.

## 90.4 · O QUE MUDA A CADA PASSAGEM NÃO PERTENCE À RELAÇÃO

A mesma aresta teve `INSERTED` na primeira passagem e `REUSED` nas duas
seguintes. O facto material não mudou; o resultado mudou três vezes.

```
    UMA RELAÇÃO QUE SE REESCREVE A CADA PASSAGEM NÃO É UMA RELAÇÃO.
```

E a casa já tinha a regra escrita, na `024`: `STAGE STATE != ITEM DESTINATION`.
Uma etapa não é «reaproveitada» — um item é. O mesmo vale para o tempo: o
carimbo da relação diz **primeira vez**, e os outros dois tempos já têm dono
(`derived_at` do artefato, `comecou_em` da passagem).

A regra geral, para o próximo desenho:

```
    ANTES DE PÔR UM CAMPO NUMA RELAÇÃO, PERGUNTE:
    ELE MUDA SE A MESMA COISA ACONTECER OUTRA VEZ?
    SE MUDA, ELE É DO EVENTO, E NÃO DA RELAÇÃO.
```

## 90.5 · AS CONVENÇÕES ESTAVAM NO ESQUEMA, E BASTOU MEDI-LAS

Três respostas que eu ia justificar por preferência já estavam escritas, e
mediram-se em vez de se argumentarem:

```
apagamento   material RESTRICT, telemetria CASCADE
             (raw_asset→collection_run, derived_artifact→raw_asset: RESTRICT;
              etapa_da_corrida→ambos: CASCADE)

tentativa    fora da identidade — `raw_asset.attempts` já é «TELEMETRIA, e fora
             da chave de idempotência»

corrida      a `022` recusou uma RUN própria para a derivação, e a `024` recusou
             um `flow_run` paralelo: «duas corridas divergem na primeira pressa»
```

```
    UMA CONVENÇÃO MEDIDA NO ESQUEMA VALE MAIS
    DO QUE UMA PREFERÊNCIA DEFENDIDA NUMA ADR.
```

## 90.6 · A TERCEIRA GUARDA DE TEXTO A MORDER A PRÓPRIA EXPLICAÇÃO

Escrevi um teste que reprovava se a ADR contivesse «em aberto». Ele reprovou —
na nota que **explica** que a pergunta *estava* em aberto e foi fechada.

É a terceira vez nesta linha de missões (`§85`, e duas vezes aqui) — e houve uma
**quarta** na correcção desta própria secção: um `assertNotIn` do nome de um
contador removido reprovou no comentário que explica **que ele foi removido**.
O padrão já não é acidente:

```
    UMA GUARDA DE TEXTO NÃO DISTINGUE A REGRA DO EXEMPLO DELA.
    UMA GUARDA LÊ O QUE A DECISÃO **DIZ**, E NÃO O FICHEIRO INTEIRO.
```

A versão que ficou confere **campo a campo**, com vocabulário fechado:
`PARTICIPATION_CONCEPT`, `RUN_ID_IN_MATERIAL_LINEAGE_KEY`, `ATTEMPT_IN_KEY`,
`RUN_ID_AS_PROVENANCE`, `INSERTED_REUSED_BELONGS_TO`. Se um deles voltar a
`UNKNOWN`, a guarda morde — e morde a coisa certa.

E houve uma quarta, da espécie oposta: uma guarda que exigia o estado
`RECOMENDADO` reprovou quando a ADR passou a `DECIDIDO`.

```
    UMA GUARDA QUE PRENDE O ESTADO ERRADO
    REPROVA O PROGRESSO E DEIXA PASSAR O DEFEITO.
```

## 90.7 · O QUE FICA POR SABER

Fica por saber se alguém vai precisar do histórico **por item** — quais
observações foram reaproveitadas em qual passagem. Hoje não há necessidade
provada, e por isso não se constrói. Se aparecer, o sítio já está escolhido: é
ao lado da passagem, e não dentro da aresta.

---

# §91 · QUATRO TETOS RESPONDIAM «QUANTO», E NENHUM RESPONDIA «QUEM DISSE QUE SIM»

**Missão:** `SCRAP-SR-02 — NENHUMA COMPRA SEM AUTORIZAÇÃO`
**Tocado:** `leis/autorizacao_de_gasto.py` (novo) · `coleta/coletor.py` ·
`coleta/scrap_executor.py` · `regras/sensor_coleta.py`
**Gasto:** `APIFY_RUNS = 0 · START_POSTS = 0 · PAID_USD = 0`

A `§80` deu à casa um teto de dinheiro. A `§81`, a certeza de que a chave
chega. A `§89` mostrou que uma tradução concede permissão. Esta secção é a
pergunta que faltava, e ela vinha antes de todas.

## 91.1 · O SISTEMA SABIA QUANTO PODIA GASTAR E NÃO SABIA SE DEVIA

Medido antes desta missão: uma única primitiva capaz de criar execução paga
(`coletor.executar`, o POST), quatro chamadores dela, e três a saltar o
roteador. Em volta dela, quatro portões a funcionar bem:

```
teto financeiro    responde  «quanto cabe?»
teto de rede       responde  «quantas idas restam?»
política da rota   responde  «este caminho é permitido?»
cap do provider    responde  «no máximo quanto, do lado de lá?»
```

Nenhum respondia à pergunta anterior a todas as quatro.

```
    ALGUÉM AUTORIZOU ESTA COMPRA?

    CREDENTIAL_PRESENT != SPEND_AUTHORIZED
    ROUTE_ALLOWED      != SPEND_AUTHORIZED
    BUDGET_PRESENT     != SPEND_AUTHORIZED
    TOKEN_OWNER        != SPEND_OWNER
```

Um sistema que sabe exactamente quanto pode gastar sem saber se devia gastar
gasta com **precisão contabilística em coisas que ninguém pediu**. É a forma
mais cara de rigor que existe: todos os números batem certo, e a pergunta que
importava nunca foi feita.

## 91.2 · UMA GUARDA QUE VIVE NUM CAMINHO GUARDA UM CAMINHO

Havia a tentação de pôr a verificação no roteador — é lá que a coleta canónica
passa. Mas três dos quatro chamadores não passam pelo roteador; foi por isso
que a `§83` já tinha encontrado bypasses.

```
    UMA GUARDA QUE VIVE NUM CAMINHO GUARDA UM CAMINHO.
    UMA GUARDA QUE VIVE NA PRIMITIVA GUARDA TODOS.
```

A guarda foi para dentro da função onde o POST nasce, e o seu parâmetro nasce
`None`:

```
    FAIL CLOSED. O SILÊNCIO NÃO AUTORIZA.
```

O efeito é o que se quer de uma lei: um chamador novo, escrito daqui a um ano
por quem nunca leu isto, **não compra** — em vez de comprar por omissão. Três
chamadores existentes deixaram de conseguir comprar no mesmo instante, e isso
não é um estrago: é o resultado. Eles esperam que alguém diga para que fonte e
que propósito cada um compra.

## 91.3 · O GUARDA CONFERE O BILHETE. NÃO É O DONO DO ESPECTÁCULO

A decisão de relevância vive noutra linhagem, com dono próprio. A tentação
seguinte era trazê-la para dentro — «é só importar a lei». Não se importou.

```
    SOURCE_RELEVANCE_OWNER != SPEND_ENFORCER.
```

A guarda recebe o veredito e valida-o. Não lê o livro, não classifica fonte,
não interpreta palavra-chave, não fabrica `SOURCE_ID`. Se o fizesse, a casa
passava a ter duas verdades sobre relevância, e a segunda envelhecia calada.

E houve uma terceira tentação, mais subtil: ler o estado e **reaplicar a tabela
do portão**. Isso seria a mesma lei escrita duas vezes, e a cópia daria
respostas antigas no dia em que o original mudasse. O que se fez foi o oposto,
e é a parte reutilizável desta secção:

```
    EXIGE-SE A ÚNICA COMBINAÇÃO QUE NÃO TEM LEITURA DUPLA —
    VEREDITO = AUTORIZA **E** ESTADO = SIM — E RECUSA-SE TUDO O RESTO,
    INCLUSIVE O QUE UMA VERSÃO FUTURA DO DONO VIESSE A AUTORIZAR.
```

Errar para o lado do «não compra» custa uma linha a alguém. Errar para o outro
custa dinheiro que ninguém pediu. Quando um contrato atravessa uma fronteira de
propriedade, o lado que **obedece** deve ser mais estreito que o lado que
**decide**.

E as ausências não se achatam. `NAO_AVALIADA`, `NAO_SEI`, `ERRO` e `NAO` dão
todas zero POST — e chegam com quatro nomes diferentes. Dizer `NOT_RELEVANT` a
uma fonte que ninguém abriu seria inventar um julgamento.

```
    FALTA DE AUTORIZAÇÃO É FALTA DE AUTORIZAÇÃO.
```

## 91.4 · O CICLO IMPOSSÍVEL, E OS DOIS MODOS QUE O PARTEM

Um portão de relevância sem escape fecha um ciclo:

```
    PARA PROVAR QUE A FONTE SERVE É PRECISO OBSERVÁ-LA,
    E PARA A OBSERVAR SERIA PRECISO ELA JÁ SERVIR.
```

Daí três modos e não um:

```
NORMAL   colher a sério            exige SOURCE_RELEVANCE = SIM para o PAR
PROBE    «esta candidata merece?»  arranca de NAO_AVALIADA, com limites
TRIAL    «esta ROTA consegue?»     mede a rota, não a fonte
```

O preço de escapar ao portão é ser **finito em tudo**: corridas, POSTs,
dólares, itens, rede. Um limite em falta é um limite infinito. E o escape não
paga a si próprio de volta:

```
    PROBE != DECISION. Quem escreve no livro é o dono do livro.
```

O eixo do modo mudou de casa por causa disto, e a razão é de propriedade: o
modo existe para dizer **que prova é precisa antes de comprar**, e isso é uma
pergunta de autorização, não de execução.

## 91.5 · UMA TROCA DE TRANSPORTE LEVA AS LEIS QUE MORAVAM NO TRANSPORTE

O achado que não estava no guião, e o mais silencioso de todos.

`regras/sensor_coleta.py` substitui `coletor._curl` **no import**, por um
transporte urllib. A troca é legítima: o proxy deste ambiente derruba conexões
e urllib sobrevive onde o subprocesso não sobrevive.

O que ela levava consigo não era. Duas leis moravam **dentro** do `_curl`
antigo:

```
o teto de rede         a reserva por ida vivia lá (§80)
o POST vai UMA vez     porque repetir um POST é comprar de novo
```

O transporte novo não reservava nada e repetia quatro vezes, qualquer método —
incluindo o POST que cria a execução paga. Bastava `import sensor_coleta` em
qualquer ponto do processo para as duas desaparecerem da única porta que gasta
dinheiro, **para toda a gente**.

```
    UMA TROCA DE TRANSPORTE LEVA COM ELA AS LEIS QUE MORAVAM NO TRANSPORTE.
    REPETIR UM GET É BARATO. REPETIR UM POST É COMPRAR DE NOVO.
```

E o `maxTotalChargeUsd` não cobria o buraco: ele limita **cada** execução,
nunca a soma das execuções que ninguém sabe que existem.

A generalização, que vale muito para lá deste ficheiro: **uma lei que mora
dentro de uma implementação viaja com ela**. Quando algo é substituível em
runtime, o que lá vive tem de ser ou uma lei explícita que o substituto herda,
ou uma sentinela que reprove o substituto que não a cumpra. O conserto aqui foi
os dois: as leis voltaram, e `coletor._CURL_DA_CASA` passou a guardar o
transporte original **com nome**, para que a troca deixe de ser invisível.

## 91.6 · DOIS FICHEIROS COM O MESMO NOME DE MÓDULO SÃO DOIS DONOS DO MESMO NOME

A prova desta missão chamou-se `provas/autorizacao_de_gasto.py` durante meia
hora, e partiu 45 sentinelas de uma vez. As gavetas desta casa estão todas no
mesmo caminho de importação: `leis/` e `provas/` são irmãs para o `import`.
Como a prova importava `coletor`, e `coletor` importa a lei, Python devolvia-lhe
a **própria prova a meio de nascer**.

```
    ONE CONCEPT → ONE OWNER, NA FORMA MAIS LITERAL QUE ELA TEM:
    DOIS FICHEIROS COM O MESMO NOME DE MÓDULO SÃO DOIS DONOS DO MESMO NOME,
    E QUEM IMPORTA RECEBE O QUE A ORDEM DO CAMINHO DECIDIR.
```

## 91.7 · E AS SONDAS QUE LIAM A PROSA, OUTRA VEZ

Duas sentinelas acusaram **comentários**: uma procurava a palavra «relevância»
no executor e encontrou a frase que explica que o executor não julga
relevância; outra procurava «VEREDITO» nos workflows e encontrou o comentário
do mapa a falar dos vereditos das suas provas.

```
    UMA SONDA QUE LÊ A PROSA ENCONTRA A FRASE QUE EXPLICA A REGRA
    E CHAMA-LHE VIOLAÇÃO DA REGRA.
```

É a terceira missão seguida com esta família (`§87.6` é a irmã sobre estado
global). E o conserto certo nunca é apagar a palavra do comentário: é medir a
**árvore**. Proibir o nome nunca impediu ninguém de escrever
`import relevancia_da_fonte` e chamar `portao()`. A sentinela saiu mais forte
do que entrou.

## 91.8 · CONSEQUÊNCIA

```
PAID_CREATION_PRIMITIVES        1  (era 1, e continua — não se criou porta)
CALLERS DA PRIMITIVA            4  · 1 passa autorização, 3 deixaram de comprar
CAN_SPEND_WITHOUT_AUTH   4  ->  0
ATAQUES 48 · MUTANTES 23 · SOBREVIVENTES 0 · NEW_FAILURES 0
APIFY_RUNS 0 · START_POSTS 0 · PAID_USD 0
```

Fica por fazer, e é dívida explícita: a `SR-01` declarou
`BIBLE_CHANGE_REQUIRED = YES`, e esta missão **não** tocou na Bíblia. E os três
chamadores que deixaram de comprar continuam à espera de que alguém diga para
que fonte e que propósito cada um compra — a resposta vive no livro da `SR-01`,
e não nesta linhagem.

    SPEND ENFORCEMENT resolvido != CANONICAL ORCHESTRATION resolvida.
    MODULE CAN'T SPEND != FLOW IS CANONICAL.

## 91.9 · A SEGUNDA LINHA DA MESMA MISSÃO, E O QUE ELA ACRESCENTA

A `SCRAP-SR-02` foi executada **duas vezes, em paralelo**, por linhas que não se
viram: a de cima e a de `claude/festive-fermi-1k2mf5` (HEAD `736844ee`, artefacto
`docs/sintonia-scrap/SCRAP-SR-02-NENHUMA-COMPRA-SEM-AUTORIZACAO.md`). As duas
chegaram à mesma arquitectura — guarda na primitiva, três modos, fail closed — por
caminhos independentes, o que é a melhor confirmação que a secção acima podia ter.

E as duas não estão reconciliadas. Isso é dívida explícita, e fica escrito aqui
porque o sítio de a esconder seria o silêncio.

O que a segunda linha traz e não está acima:

### 91.9.1 · O DONO PODE ESTAR AUSENTE DA ÁRVORE, E ISSO TEM DE TER NOME

A `91.3` diz `SOURCE_RELEVANCE_OWNER != SPEND_ENFORCER`, e que a lei do dono não
se importou para dentro. A segunda linha tropeçou um passo antes: tentou trazer o
**ficheiro** do dono, porque ele vive noutra linhagem e **não está na árvore**. Os
testes todos passaram, e estava errado.

```
    DEPENDER DO DONO != SER O DONO.
    COPIAR O DONO PARA DENTRO DE CASA CRIA UM SEGUNDO DONO,
    E O SEGUNDO DONO ENVELHECE CALADO.
```

Quem apanhou não foi uma revisão: foi o **validador do System Map**, com
`P9_CODIGO_DECLARADO` a perguntar de que peça era aquele ficheiro. A resposta
verdadeira — «de outra linhagem» — não é coisa que um ramo possa declarar. Uma
regra escrita para manter o mapa honesto apanhou um defeito de arquitectura que
nada no código teria apanhado.

O que ficou é uma dependência que **fecha por ausência**, com recusa própria:

```
    SEM O DONO DA RELEVÂNCIA, NENHUMA COLHEITA COM FONTE É AUTORIZÁVEL.
    FECHAR POR AUSÊNCIA É MAIS TRAVA, NÃO MENOS.
```

E a recusa chama-se `DONO_DA_RELEVANCIA_AUSENTE`, e não `RELEVANCE_RESULT_AUSENTE`:

```
    UMA RECUSA QUE DIZ «FALTA O DADO» QUANDO FALTA A LEI
    ESCONDE UM FACTO DE ARQUITECTURA ATRÁS DE UM FACTO DE DADOS.
```

Quem lesse o rasto iria procurar a decisão em vez de procurar o ficheiro. E o
`CAPABILITY_TRIAL`, que não julga fonte, continua a funcionar — é por isso que as
sentinelas da casa ainda atravessam a porta paga contra um provider falso.

**E as provas não podem copiar o dono pela janela.** Um substituto de teste com as
palavras **verdadeiras** do dono é a mesma cópia com outro nome. O substituto que
ficou tem palavras de propósito diferentes (`SERVE_SUB`, `AUTORIZA_SUB`), e o rasto
imprime `RELEVANCE_RESULT = SERVE_SUB` — a feiúra é o ponto: vê-se que é
substituto.

```
    O QUE UM SUBSTITUTO PROVA É A LIGAÇÃO, NUNCA A LISTA.
```

### 91.9.2 · A METADE DA `91.5` QUE NÃO SE HERDA

A `91.5` diz que o transporte novo «não reservava nada» no teto de rede. A segunda
linha mediu isso **antes** de copiar a reserva para lá, e foi bom tê-lo medido:

```
coletor._curl   sai por subprocess  →  o teto NÃO vê (§80)  →  reserva explícita
_curl_robusto   sai por urlopen     →  o teto VÊ            →  não reserva
```

`scrap_http.orcamento_de_rede` cobra exactamente em `urlopen`. Copiar a reserva
para o substituto contava a mesma ida **duas vezes** — medido, `orc.usados = 2`
para um único POST — e um teto que se esgota ao dobro da velocidade recusa coleta
legítima com o nome errado.

```
    O QUE O SUBSTITUTO HERDA É O EFEITO, NÃO A LINHA.
    COPIAR A TRAVA SEM VER ONDE ELA JÁ MORDE COBRA DUAS VEZES.
```

A lei da `91.5` mantém-se inteira — a do POST era real e custava dinheiro. O que
esta metade acrescenta é que «herdar as leis do transporte» se verifica **medindo o
efeito**, nunca conferindo se a linha está lá.

### 91.9.3 · E A `91.7` OUTRA VEZ, NA MESMA SESSÃO QUE A ESCREVEU

A `91.7` diz que uma sonda que lê a prosa encontra a frase que explica a regra e
chama-lhe violação. A segunda linha escreveu essa lei e **caiu nela a seguir**: a
sentinela que devia provar «o substituto não repete o POST» conferia se a palavra
`'POST'` aparecia no corpo da função, e **passava com a lei removida** — a palavra
continuava lá, noutra linha, no `raise PostTalvezCriado`.

```
    UMA SENTINELA QUE LÊ O TEXTO ENCONTRA A PALAVRA, NÃO A DECISÃO.
    UMA SENTINELA QUE NUNCA SE VIU REPROVAR NÃO ESTÁ PROVADA: ESTÁ SUPOSTA.
```

O conserto é medir **comportamento**: chamar o transporte com a rede em baixo e
**contar as idas**. Quatro mutações aplicadas à árvore (uma segunda porta, um
transporte que também cria, o POST a repetir outra vez, a reserva duplicada) fizeram
cada sentinela reprovar antes de alguém confiar nela. Duas famílias irmãs da mesma
lição: a `91.7` é sobre o que a sonda **lê**; esta é sobre o que ela **mede**.

E a variante mais fina, do lado oposto — uma sentinela que apanhou
`medidas/portao.py` por guardar `'POST /acts/{actor}/runs?waitForFinish'` como
**rótulo** de relatório, com `{actor}` nunca formatado:

```
    NOMEAR O ENDEREÇO NÃO É PEDI-LO.
    GREP CONTA TEXTO. AST CONTA CÓDIGO.
```

### 91.9.4 · UMA BASELINE MEDIDA NOUTRO SÍTIO NÃO É A BASELINE

Erro de método, e ele quase produziu uma mentira simpática — vale para qualquer
missão futura desta casa.

A baseline da regressão foi medida numa **worktree** em `/tmp` e deu `95/14`.
Depois da missão: `98/12`. Lido de frente, isso diz «fechei o buraco *e* curei dois
testes». Não curou nada. Duas das «14» falhavam **por ser uma worktree**:

- um teste compara caminhos, e a worktree é mais funda: o bruto escapava do
  redireccionamento com `../../../../../`;
- outro pergunta se o alvo é um «branch vivo», e a worktree está em
  **detached HEAD**.

Três corridas de cada lado: determinístico, não intermitente. Medido outra vez no
**mesmo directório, no mesmo ramo, com `git stash`** — baseline verdadeira `97/12`,
depois `98/12`, e as doze falhas são as mesmas doze, nome por nome.

```
    UMA BASELINE MEDIDA NOUTRO SÍTIO NÃO É A BASELINE.
    UMA WORKTREE MUDA O CAMINHO E A CABEÇA, E ALGUNS TESTES MEDEM OS DOIS.
    COMPARAR CONTAGENS ESCONDE O QUE COMPARAR NOMES MOSTRA.
```

A regra que fica: comparar regressão por **nome de ficheiro**, nunca por total. Um
`98/12` contra um `95/14` parece progresso em dois sítios e era ruído num só.

### 91.9.5 · E UM DIFF DE TRÊS ITENS COM 3.618 LINHAS

A primeira edição do `architecture.declared.json` foi feita reserializando o JSON,
e produziu 3.618 inserções e 3.590 remoções para acrescentar uma peça, uma aresta e
um ficheiro. Revertida e refeita cirurgicamente: 29 inserções.

```
    UM DIFF QUE NINGUÉM CONSEGUE LER NÃO FOI REVISTO: FOI ACEITE.
```

---

# §92 · LER A ÁRVORE PROVA QUE A PEÇA EXISTE. SÓ CORRER PROVA QUE A ARESTA EXISTE

**Missão:** `SCRAP-FLOW-01 — UM FLUXO OPERACIONAL REAL PELO ORQUESTRADOR`
**Tocado:** `coleta/scrap_colheita.py` (novo) · `leis/retorno_da_coleta.py`
(portado) · `orquestrador/orquestrador.py` · `coleta/ingresso.py` ·
`pedido/receitas.py` · `.github/workflows/sintonia-scrap.yml`
**Gasto:** `REAL_NETWORK = 0 · META_REQUESTS = 0 · APIFY_RUNS = 0 · COST_USD = 0`

A `§91` fechou o dinheiro e deixou escrita a diferença que faltava:
`MODULE CAN'T SPEND != FLOW IS CANONICAL`. Esta secção é o outro lado dela — e
o que se aprendeu foi mais sobre COMO SE PROVA um fluxo do que sobre o fluxo.

## 92.1 · OITO MUTANTES SOBREVIVERAM, E TODOS PELA MESMA RAZÃO

A bateria tinha vinte e duas sentinelas verdes. A mutação matou dez de dezoito
e deixou oito de pé — e os oito partiam o caminho de forma óbvia: tirar o
executor do registo, deixar o adapter cunhar a própria corrida, repor a
heurística, mandar à admissão o item de antes da porta.

Nenhum deles mudava uma linha que as sondas olhassem. Todas liam a **árvore**:
imports, chamadas, campos, nomes.

```
    LER A ÁRVORE PROVA QUE A PEÇA EXISTE.
    SÓ CORRER PROVA QUE A ARESTA EXISTE.
```

É a `MODULE EXISTS != EDGE EXISTS != FLOW EXISTS` aplicada às **sentinelas**, e
não ao código. Uma bateria inteira de análise estática prova que as peças estão
lá e não prova que elas se falam. O conserto foi uma classe que corre o caminho
todo — numa cópia da árvore, com um só ficheiro falso — e afirma sobre o
RESULTADO. Os oito morreram.

E o inverso também é verdade e vale dizer: as sondas de árvore continuam a
apanhar o que as de execução não apanham (o disparador a ganhar o nome do ator,
um classificador temático a entrar no coletor). São duas famílias, e nenhuma
substitui a outra.

## 92.2 · A IDENTIDADE DESCE COM O PEDIDO. NUNCA SOBE DA OBSERVAÇÃO

O SCRAP não conhece `SOURCE_ID`, e não é distração: o envelope canónico tem
`PLATFORM`, `SOURCE_ACCOUNT`, `NATIVE_ID` e `URL` — quatro campos verdadeiros,
e nenhum deles é uma fonte provada. A porta da coleta, do outro lado, fala em
FONTES do atlas.

A saída fácil era derivar: a conta vira fonte, o domínio vira fonte, o slug
vira fonte. Todas fabricam identidade, e uma identidade fabricada não rebenta —
ela responde, e a observação errada fica ligada à fonte errada para sempre.

```
    URL NÃO É SOURCE_ID. HANDLE NÃO É SOURCE_ID. PLATAFORMA NÃO É FONTE.
    A IDENTIDADE DESCE COM O PEDIDO, E NUNCA SOBE DA OBSERVAÇÃO.
```

É a mesma forma da `§91`: lá, a autorização de gasto chegava de fora com
`SOURCE_ID` e `PROPOSITO`; aqui, a fonte chega de fora com o pedido. Quem
observa não é quem sabe de quem observou. Sem a fonte, o executor declara **zero
colheita e escreve porquê** — o que não é uma falha, é a resposta certa.

## 92.3 · UMA TROCA QUE NÃO MUDA NENHUM NÚMERO NÃO SE CONSEGUE VIGIAR

Medido: o orquestrador fazia `pela_entrada(itens)` e a seguir `pela_porta(itens)`
— **a mesma lista**. O ingresso preservava a observação, cunhava-lhe ficha,
`sha256` e sítio no armazém, devolvia CONTAGENS, e o que ia a julgamento era o
item original.

```
    O ITEM QUE SAI DO INGRESSO NÃO É O ITEM QUE ENTROU,
    E MANDAR O ORIGINAL À ADMISSÃO É FAZER A PORTA NÃO TER ACONTECIDO.
```

O que torna este defeito perigoso não é o erro: é a **invisibilidade**. As duas
listas têm o mesmo tamanho, os mesmos campos e o mesmo aspecto no recibo.
Trocar uma pela outra não mexe em número nenhum, e por isso nenhuma sentinela
de contagem alguma vez a apanharia — o mutante que refazia a troca sobreviveu à
primeira volta exactamente por isso.

```
    UMA TROCA QUE NÃO MUDA NENHUM NÚMERO NÃO SE CONSEGUE VIGIAR.
```

A regra geral: quando a correcção é invisível nos números existentes, **o
conserto inclui criar o número**. Aqui foi `COM_CARIMBO_DA_PORTA` — quantos dos
julgados traziam a prova do ingresso. Sem ele, a lei ficava escrita e
indefensável.

## 92.4 · UM MUTANTE QUE NÃO MUDA O COMPORTAMENTO NÃO MEDE SENTINELA NENHUMA

Dois dos sobreviventes eram culpa da prova, e não do código: um renomeava o
`id` de um executor (que continuava a correr, só com outro nome) e o outro
acrescentava um `if x else []` a uma expressão onde `x` é sempre verdadeiro.

```
    UM MUTANTE QUE NÃO MUDA O COMPORTAMENTO NÃO MEDE SENTINELA NENHUMA —
    E CONTA-SE COMO SOBREVIVENTE, QUE É O PIOR DOS DOIS ENGANOS.
```

Ele acusa a bateria de um buraco que não existe, e a pressa seguinte escreve
uma sentinela para o tapar. Um sobrevivente obriga sempre a duas perguntas, por
esta ordem: *o mutante muda mesmo o comportamento?* e só depois *falta uma
sentinela?*

## 92.5 · CALAR QUATRO CAMINHOS PARA CORRIGIR UM NÃO É CORRIGIR

O contrato de retorno diz que só `COLHEITA` atravessa, e a árvore tinha uma
heurística a adivinhar: «uma lista, ou o primeiro campo do ficheiro que seja
lista de fichas». Aplicá-lo inteiro, de uma vez, foi o primeiro impulso — e
partiu oito sentinelas: quatro executores entregavam colheita real por ali.

A escolha certa não foi nenhum dos dois extremos. A heurística sobrevive para
quem ainda não declara envelope, e **deixou de ser silenciosa**: sai contada no
recibo, e um campo diz sempre qual das duas leituras foi usada.

```
    UMA DÍVIDA MEDIDA É UMA DÍVIDA. UMA DÍVIDA CALADA É UM BUG.
```

Uma missão que migra um caminho não pode calar cinco para o número fechar. O
que ela pode — e deve — é deixar os outros quatro **visíveis e contados**, para
que a missão seguinte saiba exactamente o que herda.

## 92.6 · DUAS LINHAGENS ESCREVERAM A MESMA LEI, E NENHUMA SABE DA OUTRA

Medido nesta missão, e não resolvido nela: `leis/autorizacao_de_gasto.py` existe
nas DUAS linhagens da SR-02, com bytes diferentes (20.572 e 18.236), escrito
duas vezes por duas frentes que não se viram.

```
    ONE CONCEPT → ONE OWNER É UMA LEI DE REPOSITÓRIO,
    E UM REPOSITÓRIO COM RAMOS LONGOS TEM MAIS DO QUE UM PRESENTE.
```

O portado nesta missão foi o oposto disso, de propósito: `retorno_da_coleta.py`
veio **byte a byte**, sem uma linha reescrita. Duas cópias da mesma lei são duas
leis, e a segunda aprende a responder o que a primeira recusa. Quando um
contrato atravessa a fronteira entre ramos, ou se copia exactamente ou se deixa
onde está.

## 92.7 · CONSEQUÊNCIA

```
ENTRYPOINT MIGRADO        1  (sintonia-scrap.yml · fase janela)
CAMINHO PROVADO           request -> orquestrador -> COLLECT -> router ->
                          adapter -> provider -> RAW -> envelope -> ingresso
                          -> admissao
SELECTED_DIRECT_BYPASS    NO
OUTROS BYPASSES           continuam, medidos e nomeados
ATAQUES 31 · MUTANTES 18 · SOBREVIVENTES 0 · NEW_FAILURES 0
REAL_NETWORK 0 · META_REQUESTS 0 · APIFY_RUNS 0 · COST_USD 0
```

E a distinção que fica, porque ela não se resolveu e não deve parecer resolvida:

```
    SPEND ENFORCEMENT resolvido != CANONICAL ORCHESTRATION resolvida.
    MODULE CAN'T SPEND != FLOW IS CANONICAL — e agora UM fluxo é canónico,
    o que é diferente de o sistema o ser.
```

---

# §93 · UM VEREDITO DE FRESCURA TEM DE SER PROPRIEDADE DO ARTEFATO, NÃO DO DISCO DE AGORA

**Missão:** `C-SYSTEM-MAP-G3-VERIFIABLE-SOURCE-TREE-FINGERPRINT-V1`
**Linha:** `claude/system-map-g3-tree-fingerprint-v1` · **HEAD final:** `c737335b`
**Tocado:** `system-map/scripts/impressao_da_arvore.py` ·
`scan_sources.py` · `pente_fino_da_coleta.py` · `censo_da_coleta.py` ·
`censo_cards_sensores.py` · `system-map/tests/test_impressao_verificavel.py`

A `§82` e a `§88` já escreveram que um SHA de commit não prova frescura e que a
versão de uma entrada gerada é a árvore que ela carimba. Esta secção regista a
peça que faltava, e que só apareceu quando um relógio foi posto a medir o caso
que ele existia para ver.

## 93.1 · O RELÓGIO ESTAVA A PERGUNTAR PELA COISA ERRADA

O relógio do ciclo atrasado comparava a versão **actual** da entrada com a
árvore de agora. Parece a pergunta certa e não é.

Medido num clone, com a cadeia canónica: mexe-se numa fonte e corre-se a cadeia
**uma vez**. O pente fino corre no passo 5 e lê o estado que o gerador só
escreve no passo 7 — logo ele mediu a geração **anterior**. Mas quando alguém
pergunta, o estado no disco já é o novo, e a comparação dá «iguais».

```
    O DEFEITO EXISTIA, O RELÓGIO ESTAVA LIGADO, E ELE DIZIA QUE ESTAVA TUDO BEM.
```

A pergunta certa é outra:

```
    «QUE ÁRVORE MEDIA ESTA ENTRADA QUANDO EU A LI?»
    e não
    «QUE ÁRVORE ELA MEDE AGORA?»
```

Compara-se a versão que o artefato **registou** com a árvore que ele próprio diz
ter medido. Assim o veredito é uma propriedade do artefato — ele responde
sozinho, e não muda porque alguém correu outra coisa no disco entretanto.

## 93.2 · A REGRA GERAL

Um veredito que depende do estado actual do disco não é sobre o artefato: é
sobre o momento em que se perguntou. Dois leitores em momentos diferentes
recebem respostas diferentes sobre o **mesmo** ficheiro, e nenhuma está errada —
o que está errado é a pergunta.

```
    SE O VEREDITO MUDA SEM O ARTEFATO MUDAR,
    ELE NÃO ESTAVA A FALAR DO ARTEFATO.
```

## 93.3 · A TERCEIRA SAÍDA PARA UMA ENTRADA QUE NÃO SE CONSEGUE VERSIONAR

Cinco artefatos lidos pela matriz ainda não carimbam impressão nenhuma. As duas
saídas óbvias são ambas erradas: hashar os bytes põe quem os lê `STALE` a cada
corrida da cadeia (eles carregam `HEAD` e `GENERATED_AT`); dizer `NÃO SEI`
transfere para o leitor uma dívida que não é dele.

A terceira é uma **constante declarada** — `DERIVADO_SEM_CARIMBO` — com a falta
escrita ficha a ficha. Não se move, não contamina o veredito, e deixa a dívida
contável em vez de escondida num número que ninguém consegue explicar.

```
    UMA FALTA DECLARADA É DADO. UMA FALTA DILUÍDA NUM HASH É RUÍDO.
```

## 93.4 · CONSEQUÊNCIA

Os quatro artefatos que só carimbavam SHA de commit passaram a dizer que árvore
mediram, e dá para conferir. O `G6` **não** foi fechado por isso: uma passagem
da cadeia depois de uma fonte mudar continua a deixar o pente fino em
`STALE_BY_CYCLE`, e são precisas duas para ele ficar em dia. Isso está provado,
e está à vista.

```
    UM CARIMBO VERIFICÁVEL NÃO PAGA UMA DÍVIDA DE ORDEM.
```
---

# §94 · FUNDAÇÃO NÃO É DESTINO: MISSÃO TEM OBJETIVO, ENTREGA E PARA

**Decisão operacional:** a lei normativa vive em `CLAUDE.md`; esta secção guarda o motivo e a consequência para que a decisão não desapareça quando a conversa acabar.
**Prova da lei:** branch `claude/sintonia-focus-finish-law-v1` · commit `0cdd1f5a36479e895c2886032c56a331fd7b1605`.

## 94.1 · O QUE MUDOU

O SINTONIA passa a tratar **foco e encerramento como requisito de engenharia**. Toda missão precisa nascer com um objetivo principal, critério de PASS, escopo, não-objetivos e HARD STOP. Ela vai até esse objetivo, prova, entrega e para.

```text
MISSÃO TEM UM OBJETIVO.
VAI ATÉ ELE.
PROVA.
ENTREGA.
PARA.
```

Achado novo não vira automaticamente nova frente. Só entra na missão corrente quando for **BLOCKER_DO_OBJETIVO**. Defeito não bloqueante, melhoria, generalização, limpeza ou dívida descoberta são registrados e ficam para decisão posterior.

```text
ACHADO != CONVOCAÇÃO
MELHORIA != BLOCKER
PASS_DA_MISSÃO != PERFEIÇÃO_DO_SISTEMA
FUNDAÇÃO != DESTINO
```

## 94.2 · POR QUÊ

O método rigoroso revelou defeitos reais e necessários, mas também criou um risco novo: cada descoberta podia gerar outra missão, cada missão outra auditoria, e um objetivo de produto podia transformar-se em dezenas de frentes antes de entregar valor ao cliente.

O problema não é testar demais. É **não ter critério para parar quando o objetivo já está provado**.

O SINTONIA existe para funcionar com prova, não para maximizar o número de missões. Prazo do cliente e valor entregue passam a ser restrições explícitas da engenharia — abaixo de segurança, identidade, procedência e contratos, mas acima de limpeza, generalização e perfeccionismo arquitetural.

## 94.3 · PROVA

A regra foi versionada no Git em `CLAUDE.md`, dono canônico das instruções permanentes para o Claude Code, no commit `0cdd1f5a36479e895c2886032c56a331fd7b1605`.

A motivação veio do padrão observado nas próprias missões: problemas reais foram sendo encontrados e corrigidos, mas o fechamento de uma frente frequentemente abria outra antes de o sistema voltar a produzir valor operacional. O risco passou a ser de calendário e produto, não apenas técnico.

Esta secção **não duplica o texto normativo**. O owner da regra continua `CLAUDE.md`; o know-how registra por que ela nasceu e como deve orientar decisões futuras.

## 94.4 · CONSEQUÊNCIA

Antes de abrir qualquer missão nova, a pergunta obrigatória é:

```text
ISTO IMPEDE O OBJETIVO ATUAL DE FUNCIONAR OU DE SER PROVADO?
```

- **SIM** → tratar dentro da missão se for o menor conserto necessário.
- **NÃO** → registrar como dívida/risco/melhoria e continuar até entregar o objetivo atual.

Tarefas pequenas que pertencem ao mesmo objetivo devem ser agrupadas na mesma missão; HARD STOP não pode virar mecanismo para fragmentar um único objetivo em vinte micro-missões.

Fundação deve ter critério explícito de encerramento. Legado não utilizado pode permanecer medido e marcado, sendo migrado quando entrar no caminho operacional real. Depois que a máquina mínima segura e auditável estiver provada, a prioridade volta a ser **usar a máquina e entregar valor**.

Hierarquia operacional:

```text
SEGURANÇA / LEI / CONTRATO
        ↓
OBJETIVO DA MISSÃO
        ↓
VALOR PARA O CLIENTE / PRAZO
        ↓
ROBUSTEZ NECESSÁRIA
        ↓
MELHORIA / LIMPEZA / GENERALIZAÇÃO
```

Regra final:

```text
O SINTONIA NÃO OTIMIZA PARA TER MAIS MISSÕES.
OTIMIZA PARA FUNCIONAR COM PROVA.
```

---

# §95 · UMA GUARDA PRESA AO ESTADO DE HOJE REPROVA O PROGRESSO DE AMANHÃ

**Missão:** `C-COLLECTION-V1-OPERATIONAL-CLOSE`
**HEAD final:** `bd5ad9c0`
**Tocado:** `supabase/migrations/029` · `guarda/preservar_derivado.py` ·
`coleta/executor_texto_de_pdf.py` · `coleta/derivacao_forward.py` · três testes

A decisão da `§86`/`§90` foi implementada: a participação
`(observação, derivado)` passou a ter tabela, dono e prova. E o que se aprendeu
não foi sobre linhagem — foi sobre **as guardas que escrevi para a proteger**.

## 95.1 · TRÊS GUARDAS REPROVARAM NO PROGRESSO, E NENHUMA NUM DEFEITO

```
test_nenhuma_migration_nova_entrou       exigia que a última fosse a 028
test_e_nao_escreve_relacao_nenhuma       exigia que o writer não escrevesse
test_nao_ha_migration_029_nesta_missao   exigia que a 029 não existisse
```

As três estavam **certas no dia em que nasceram**. As duas primeiras diziam
«esta missão mediu e não implementou», e a terceira usava o número da próxima
migration como atalho para «ninguém escolheu a morada da Sala de Espera por
baixo».

Nenhuma delas apanhou um defeito. Todas apanharam a missão seguinte a fazer o
que estava decidido.

```
    UMA GUARDA QUE PRENDE O ESTADO ERRADO
    REPROVA O PROGRESSO E DEIXA PASSAR O DEFEITO.
```

A terceira é a mais instrutiva, porque nem sequer era sobre o assunto dela: a
`029` nasceu para a **linhagem da derivação**, e fez reprovar a guarda da
**Sala de Espera**.

```
    UM NÚMERO DE MIGRATION NÃO É UMA PROPRIEDADE.
    PRENDER A GUARDA AO NÚMERO SEGUINTE FAZ O VIZINHO REPROVAR.
```

A pergunta a fazer antes de escrever uma guarda de estado: **o que é que isto
protege quando o trabalho avançar?** Se a resposta for «nada, ela só diz onde
parámos», então ela é um marcador, e um marcador com cara de teste será lido
como lei pela próxima pessoa.

O conserto não foi apagá-las. Foi virá-las para a propriedade que sobrevive:
a migration existe **e cumpre a decisão campo a campo**; o writer escreve a
aresta **nos três pontos em que ela é real e em mais nenhum**; nenhuma
migration — seja qual for o número — **dá casa em SQL** à Sala de Espera.

## 95.2 · A CONTAGEM DAS GUARDAS DE TEXTO CHEGOU A SETE

`§90.6` contava quatro. Esta missão acrescentou três, todas iguais:

```
assertNotIn("bigserial", sql)   reprovou no comentário que explica
                                por que não há surrogate
assertNotIn("inserted", sql)    reprovou no comentário que explica
                                por que o resultado ficou de fora
"insert" not in corpo_da_funcao reprovou na docstring que diz
                                «Não há `insert` nesta função de propósito»
```

Sete vezes o mesmo erro, em sete sítios, ao longo de quatro missões. Já não é
distração: é a forma por omissão de escrever uma guarda, e ela está errada.

```
    UMA GUARDA LÊ O QUE O FICHEIRO FAZ, E NÃO O QUE ELE EXPLICA.
```

Para Python isso é o **AST**. Para SQL, é o texto **sem as linhas `--`**. E há
um segundo grau do mesmo erro: uma guarda larga de mais acusa o vizinho —
perguntar «há `create table` e há a palavra `ready` algures no ficheiro?»
acusou a `024`, que cria `etapa_da_corrida` e menciona `ready` noutro contexto.
O que se olha é o **nome da tabela criada**.

## 95.3 · TRANSPORTAR NÃO É CONHECER

O dono do derivado passou a precisar da corrida da passagem. O caminho óbvio
era acrescentar `run_id` ao executor — e o executor tem, escrito na própria
docstring, que **não sabe o que é uma corrida**:

> Ele não sabe — e não deve saber — o que é uma corrida, um `run_id`, um
> `source_id` ou uma tabela de rastro.

Essa regra não é decorativa: é o que impede um executor de declarar uma
linhagem que não pode provar. Quebrá-la para poupar um parâmetro teria sido
pagar a doutrina para não pensar.

O que atravessa é um **envelope opaco**, com um nome que não é `run_id`, e que
o executor não abre.

```
    O EXECUTOR PRODUZ O QUE SÓ ELE SABE.
    TRANSPORTAR NÃO É CONHECER.
```

E a guarda disso lê-se por AST: o parâmetro existe, o nome `run_id` **não**
aparece na assinatura, e não há um `Subscript` sobre o envelope. Se um dia ele
o abrir, o teste cai.

## 95.4 · «NÃO TEM DONO» É QUASE SEMPRE LARGO DE MAIS

A `§86.7` já tinha corrigido isto uma vez para o `canal_id`. Voltou a
confirmar-se ao medir o bloqueio do STRUCTURED:

```
SCHEMA OWNER       EXISTE   origem e canal, migration 002
RUNTIME RESOLVER   EXISTE   canal_canonico lê, e nunca cria
RUNTIME CREATOR    NÃO      nenhum ficheiro de produção cria canal
```

E a medição encontrou mais do que se procurava: não falta só o canal.
`conteudo.content_id` está comentado como «id da plataforma (video_id,
post_id)» e `canal.channel_id` como «o id da plataforma, NUNCA o nome». Um
boletim em PDF no sítio de uma agência regional não tem nenhum dos dois.

```
    A TABELA PRESSUPÕE UMA PLATAFORMA QUE EMITA IDENTIFICADORES.
    UMA FONTE DOCUMENTAL NÃO É UMA.
```

Isso muda a pergunta que vai a decisão. Não é «qual é o `channel_id` da
ARPAV?» — é «o que é um canal, quando a fonte não é uma plataforma?». A
primeira pede um valor; a segunda pede um significado, e só a segunda é
honesta.

```
    ANTES DE PEDIR UM VALOR A ALGUÉM,
    VERIFIQUE SE O QUE FALTA É O VALOR OU O CONCEITO.
```

---

# §96 · DUAS IMPLEMENTAÇÕES DO MESMO CONTRATO NÃO SÃO DUAS VERSÕES DA VERDADE

**Missão:** `SCRAP-OWNER-01 — CONVERGIR A AUTORIZAÇÃO DE GASTO`
**Tocado:** `leis/autorizacao_de_gasto.py` · `leis/relevancia_da_fonte.py`
(portado) · `coleta/coletor.py` e os cinco consumidores
**Gasto:** `REAL_NETWORK = 0 · APIFY_RUNS = 0 · COST_USD = 0`

A `§92` fechou com a observação de que um repositório com ramos longos tem mais
do que um presente. Esta secção é o que aconteceu quando os dois presentes se
encontraram.

## 96.1 · O SINAL NÃO É O CÓDIGO DIFERENTE. É O NOME IGUAL

Duas linhagens escreveram, cada uma por si, um ficheiro com o mesmo caminho
para a mesma pergunta. Isso, por si, é banal e recuperável. O que não é banal:
**os dois declaravam `AUTORIZACAO_DE_GASTO/v1`**.

Medido, com o mesmo input:

```
um dicionário escrito à mão pelo chamador
    linha A     ACEITE
    linha B     RECUSADO

uma autorização de UMA execução, usada duas vezes
    linha A     as duas passam
    linha B     a segunda é recusada
```

```
    DUAS IMPLEMENTAÇÕES DO MESMO CONTRATO
    NÃO SÃO DUAS VERSÕES DA VERDADE: SÃO DUAS VERDADES.
```

E o dano tem uma forma concreta: um manifesto guarda `CONTRATO: …/v1`, e quem o
lê daqui a um ano **não consegue saber qual dos dois comportamentos o
produziu**. O campo que existe para identificar o contrato deixa de o
identificar. Dois ficheiros com o mesmo nome de contrato são piores do que dois
com nomes diferentes, porque os segundos pelo menos confessam.

## 96.2 · COMO SE ESCOLHE ENTRE DOIS DONOS: POR PROPRIEDADES, NÃO POR IDADE

A tentação é escolher pela linha «principal», pela mais recente, ou pela que
tem mais consumidores. Nenhuma dessas responde à pergunta certa.

A pergunta certa é: **cada modelo preserva alguma propriedade que o outro não
preserva?** Se a resposta é «só um deles», não há decisão a tomar — há uma
medição a aceitar.

```
    autorização SELADA        o chamador não a consegue escrever
    autorização CONSUMÍVEL    uma execução autorizada não paga duas
    teto do FORNECEDOR        conferido contra o autorizado
    pergunta ao DONO          o portão de relevância é chamado, não imitado
```

Quatro propriedades num lado, zero no outro. O modelo que perdeu não tinha
nada que o vencedor não tivesse — e por isso a convergência não teve de
inventar um terceiro modelo, que era o risco real.

```
    QUANDO UM DOS DOIS É UM SUPERCONJUNTO,
    CONVERGIR NÃO É NEGOCIAR: É ESCOLHER E MIGRAR.
```

## 96.3 · A VERSÃO SEGUE A COMPATIBILIDADE MEDIDA, E NADA MAIS

`v2` não saiu de cerimónia nem de «é uma mudança grande». Saiu de uma medição:
`v1` **já** nomeava dois comportamentos incompatíveis. Manter o nome criaria um
terceiro `v1`.

```
    NÃO SE AUMENTA A VERSÃO PORQUE MUDOU MUITO.
    AUMENTA-SE PORQUE O NOME ANTIGO JÁ NÃO DESIGNA UMA COISA SÓ.
```

E o nome ambíguo fica escrito no ficheiro (`CONTRATO_AMBIGUO_ANTERIOR`), porque
os manifestos antigos existem e alguém os vai ler.

## 96.4 · VALIDAR UM CAMPO QUE QUEM PEDE ESCREVEU

O modelo que perdeu validava um dicionário: conferia que `VEREDITO` dizia
`AUTORIZA`, que o `SOURCE_ID` batia, que o propósito batia. Tudo correcto — e
tudo escrito pelo próprio chamador.

```
    VERIFICAR UM CAMPO QUE QUEM PEDE PREENCHEU
    É CONFERIR A ASSINATURA DE QUEM ASSINOU O CHEQUE.
    CAMPO PREENCHIDO PELO CHAMADOR != AUTORIZAÇÃO.
```

O conserto não precisou de criptografia: um objecto cujo construtor exige um
selo privado ao módulo, e uma única função que o possui. Quem quiser autorização
passa por lá e responde às perguntas; quem montar a estrutura à mão recebe
`AUTORIZACAO_FABRICADA`. E o mesmo vale para um sósia com os mesmos campos, e
para a própria autorização depois de passar por JSON — serializar tira-lhe o
selo, que é precisamente o que a torna dela.

## 96.5 · UMA AUTORIZAÇÃO QUE NÃO SE GASTA PAGA TANTAS VEZES QUANTAS CHAVES HOUVER

A propriedade mais fácil de não ver. O dono das credenciais **roda a chave** e
retoma a mesma unidade de trabalho quando uma esgota; o sensor percorre o pool
inteiro. Com uma autorização que só valida, uma única concessão paga tantas
execuções quantas chaves existam no cofre — e nenhuma delas parece irregular.

```
    ROTAÇÃO DE CHAVE NÃO É NOVA AUTORIZAÇÃO.
    UMA AUTORIZAÇÃO QUE NÃO SE GASTA NÃO É UM TETO: É UMA PERMISSÃO.
```

Consumir na porta — e não no chamador — é o que faz a volta seguinte encontrar
a autorização mais pobre, ou esgotada.

## 96.6 · DOIS EIXOS QUE CORRESPONDEM UM A UM CONTINUAM A SER DOIS EIXOS

As duas linhas tinham vocabulários diferentes para o que parecia a mesma coisa:
`NORMAL / TRIAL / PROBE` de um lado, três nomes longos do outro. A correspondência
é exacta, e a tentação de os fundir era grande.

Não se fundiram, e a razão é um caso que a correspondência esconde: **uma
coleta normal de uma rota gratuita tem modo e não tem motivo de gasto.** Fundir
daria motivo de gasto a quem não gasta — e a seguir alguém exigiria autorização
financeira a uma rota que não custa nada.

```
    UMA ROTA QUE NÃO GASTA NÃO PRECISA DE AUTORIZAÇÃO PARA GASTAR.
    SPEND AUTHORIZATION != UNIVERSAL EXECUTION AUTHORIZATION.
```

O que não pode existir são **duas traduções**. Há uma tabela, num sítio, e é o
único lugar onde um eixo vira o outro.

## 96.7 · UM MUTANTE QUE SOBREVIVE ACUSA A BATERIA, NÃO O CÓDIGO

Cinco dos vinte e quatro sobreviveram à primeira volta, e nenhum deles apontava
para um buraco no código: apontavam para sentinelas que não existiam. Trocar o
mapa entre os eixos, voltar a chamar o contrato `v1`, aceitar um dicionário —
tudo isso partia uma lei e nenhuma prova.

E um deles ensinou a distinção mais fina da missão. Havia uma sentinela a
provar que a LEI recusa um dicionário. O mutante acrescentava o ramo permissivo
na **porta** — em quem chama a lei — e sobrevivia inteiro.

```
    MEDIR A LEI NÃO É MEDIR QUEM A CHAMA.
```

A `§92` dizia que ler a árvore não prova a aresta. Esta acrescenta o andar de
cima: provar a regra não prova o caminho até ela.

## 96.8 · CONSEQUÊNCIA

```
SPEND_AUTH_OWNER_COUNT    2  ->  1
CONTRATO                  dois «v1» incompatíveis  ->  um v2
PAID_CREATION_PRIMITIVES  1 (intacto)
CAN_SPEND_WITHOUT_AUTH    0 (intacto)
FREE_ROUTE_REQUIRES_SPEND_AUTH   NO
ATAQUES 65 · MUTANTES 24 · SOBREVIVENTES 0 · NEW_FAILURES 0
```

E fica uma dívida nomeada: o `LIVRO-DE-RELEVANCIA` está **vazio** nesta
linhagem, e por isso toda a coleta normal falha fechada. É a verdade — ninguém
avaliou nenhuma fonte aqui ainda — e é a única resposta honesta enquanto o
livro não existir.

---

# §97 · UM LIMITE CONFERIDO CONTRA UM LEDGER QUE MUDA NÃO FOI CONFERIDO

**Missão:** `SCRAP-CV-02` — convergir o fluxo canónico do SINTONIA SCRAP com o
controlo de gasto já provado.
**Branch:** `claude/sintonia-scrap-paid-flow-convergence-cv02`
**Data:** 2026-09-12

O §91 registou a pergunta que faltava: quatro tectos respondiam «quanto» e
nenhum respondia «quem disse que sim». Esta secção regista o que se descobriu ao
pôr essa guarda a viver **na mesma linha** que o ledger — e não ao lado dele.

## 97.1 · DUAS LEIS QUE FALAM DO MESMO DÓLAR PRECISAM DE UMA RELAÇÃO

Duas linhas, cada uma verde sozinha:

```
FLOW-01    o fluxo canónico, com a guarda de autorização já dentro
C10.8A-F   o orçamento financeiro, com os sete conceitos do dinheiro
```

Juntas, deixavam passar o dobro. Medido antes de mexer:

```
autorização: MAX_PROVIDER_RUNS = 2 · MAX_USD = 1.00
duas execuções, cada uma a declarar orçamento de 1.00
EXPOSIÇÃO REPRESENTADA = 2.00
```

O limite humano era conferido por **presença** e por **sinal** — existe? é maior
que zero? — e nunca contra o que a execução declarava poder comprometer.

    CADA COMPRA GANHAVA O LIMITE INTEIRO OUTRA VEZ.

A convergência **não** é dar à primeira lei o que a segunda sabe. É escrever a
**relação** e deixar cada uma com o seu trabalho:

```
FINANCIAL_BUDGET.AUTHORIZED  <=  AUTORIZACAO.MAX_USD
```

A guarda recebe um NÚMERO e compara. Nunca soma.

    LIMITE HUMANO != LEDGER OPERACIONAL.
    DUAS PEÇAS A CONTAR O MESMO DÓLAR DIVERGEM NA TERCEIRA CHAMADA.

## 97.2 · E A RELAÇÃO SOZINHA NÃO CHEGA — ESTA É A PARTE NOVA

Com a relação instalada, o red team voltou a rebentar o limite:

```
DUAS execuções, cada uma a abrir o SEU orçamento de 1.00
cada compra custa 0.60  →  EXPOSIÇÃO TOTAL = 1.20
```

Cada orçamento sozinho cabia no limite humano. A **soma** não cabia. O defeito
era o mesmo, um andar acima: em vez de cada POST ganhar o limite inteiro, era
cada EXECUÇÃO.

    UM LIMITE CONFERIDO CONTRA UM LEDGER QUE MUDA NÃO FOI CONFERIDO.

A tentação é dar um saldo à guarda. Seria repor exactamente o problema que a
§97.1 acabou de evitar. O que ela passou a guardar é um **nome**: a identidade
do ledger contra o qual o limite foi conferido da primeira vez. Uma segunda
execução sob outro ledger é recusada.

    UM NOME NÃO É UMA SOMA.

E a semântica que isto escreve é a que uma pessoa já entendia por autorizar: a
autorização vale dentro de UMA execução; para outra, pede-se outra vez.

## 97.3 · UM FORMULÁRIO PREENCHIDO NÃO É UMA AUTORIZAÇÃO

A autorização era um `dict`. Medido:

```
AUTHORIZATION_COPY_ACCEPTED = 1
```

Um `copy.deepcopy` da autorização de outra compra passava inteiro, e um
dicionário escrito à mão também.

    UMA AUTORIZAÇÃO QUE O CHAMADOR ESCREVE É UM CAMPO DE FORMULÁRIO.
    COPIAR UMA AUTORIZAÇÃO NÃO É RECEBER UMA AUTORIZAÇÃO.

O que passa a valer não é a FORMA do objecto: é a **identidade** da instância que
saiu da porta que concede. Um direito de gastar não é um valor, é um
acontecimento — e dois acontecimentos com os mesmos campos não são o mesmo.

**E o objecto sela-se.** Uma autorização mutável permite trazer um bilhete e
entrar com outro:

    UMA AUTORIZAÇÃO QUE MUDA DEPOIS DE CONFERIDA NÃO FOI CONFERIDA.

Descoberta de implementação que vale a pena guardar: selar contra escrita mata
`copy.copy` e `copy.deepcopy` **antes** de existir cópia nenhuma, porque as duas
reconstroem o objecto escrevendo chave a chave. A defesa da identidade e a
defesa da imutabilidade reforçam-se uma à outra.

**E a identidade guarda-se por `id()`, não por hash.** Um `dict` (e as suas
subclasses) não é *hashable*, porque a igualdade dele é por valor; forçar um
`__hash__` de identidade poria a classe a violar o contrato hash/eq. O registo
por `id()` com referência fraca é *fail-closed*: se o objecto morreu e o `id`
foi reaproveitado, a consulta devolve outro objecto e a comparação por
identidade recusa.

## 97.4 · CONFERIR É DE GRAÇA. COMPRAR NÃO É

```
1 · conferir a autorização      não queima nada
2 · reservar o dinheiro         compromete, e rebaixa o cap do fornecedor
3 · consumir a unidade          a compra está comprometida
4 · o POST                      e lá dentro, o tecto de ACESSOS
```

    UM GATE BARATO CORRE PRIMEIRO, E NÃO QUEIMA NADA AO RECUSAR.

Gastar a unidade na conferência — que corre antes do dinheiro — queima uma
execução autorizada por uma compra que o gate seguinte ainda pode recusar.

E vale nos dois sentidos, que é onde está a subtileza:

    POST QUE NÃO SAIU != POST QUE SAIU.
    AUSÊNCIA DE NOTÍCIA NÃO É PROVA DE AUSÊNCIA DE COMPRA.

O tecto de acessos recusa **dentro** do transporte, depois do passo 3: há prova
de que nada foi comprado, e a unidade volta. O transporte que cai **no meio** do
POST não dá prova nenhuma, e a unidade não volta.

## 97.5 · UMA RECUSA SEM NOME CAI NO BALDE DO DESCONHECIDO

`SemAutorizacaoDeGasto` já era um `RuntimeError` nesta linha — a armadilha do
`OSError` não existia aqui. Mas nem a rota nem o executor a deixavam subir com
nome, e o resultado medido foi:

```
compra sem autorização  →  RESULT = UNKNOWN_ERROR
```

O balde de «ninguém sabe o que houve», para a única recusa que sabe exactamente
o que houve.

    SALDO ESGOTADO != NINGUÉM AUTORIZOU.

E os nomes não se achatam entre si: «ninguém autorizou», «não há ledger», «a
fonte não serve» e «ninguém avaliou a fonte» pedem coisas diferentes de quem lê
o rasto. O que partilham é a recuperação — `NO_RETRY`, porque repetir não
resolve e trocar de chave menos ainda.

## 97.6 · O QUE UMA SUITE PROMETE E O QUE ELA MEDE

O §91.5 já registou que trocar o transporte leva com ele as leis que moravam no
transporte. Esta missão encontrou a consequência seguinte, que é de MEDIÇÃO e
não de produção: um harness que finge o `subprocess` deixa de estar no caminho
quando o transporte passa a `urllib`.

    UM FAKE QUE JÁ NÃO ESTÁ NO CAMINHO NÃO É UM FAKE. É UM ADORNO.

E a promessa `NETWORK_REAL = 0` de três harnesses passava a depender de ninguém
ter importado um certo ficheiro primeiro. A cura tem duas metades:

- a porta guarda uma referência ao seu transporte original, e quem mede repõe-na;
- **uma prova não deixa o processo pior do que o encontrou**: a suite que activa
  a troca de propósito repõe a porta ao sair, para não contaminar as seguintes.

E para medir que **carregar** o módulo troca a porta, não serve um `import`: o
módulo já está carregado e o corpo dele não volta a correr. Serve `reload`.

    MEDIR UM EFEITO DE IMPORT COM UM SEGUNDO IMPORT NÃO MEDE NADA.

## 97.7 · UMA RECUSA PELO MOTIVO ERRADO NÃO É UMA DEFESA

Ao apertar a guarda, dezenas de provas passaram a ser recusadas — mas pela
**razão nova**, não pela razão que cada uma existia para medir. Uma prova que
ataca «probe sem `MAX_USD`» e recebe «não foi concedida» deixou de medir o que
dizia medir, e continuaria verde.

    UMA RECUSA PELO MOTIVO ERRADO NÃO É UMA DEFESA. É UM ACIDENTE.

Na prática: ao endurecer uma guarda, todo o harness que constrói entradas
inválidas de propósito tem de passar a construí-las **válidas em tudo menos no
campo atacado**. Foi a maior parte do trabalho desta missão, e é trabalho que
não aparece no diff da lei.

Dois casos concretos, guardados porque vão repetir-se:

- um harness declarava orçamento de `1.00` contra um limite humano de `0.10`;
  passava porque ninguém comparava os dois, e passou a ser recusado por isso;
- «zero» num limite não é «sem tecto», é «não pode» — e a nova conferência
  chegava primeiro e dava-lhe o nome errado. Ordem de checks é semântica.

## 97.8 · UM MUTANTE QUE NÃO NASCEU NÃO PROVA DEFESA NENHUMA

As provas de mutação desta casa ancoram-se em texto exacto. Mexer na assinatura
de uma chamada guardada invalida silenciosamente as âncoras — e o corolário
salvou esta missão duas vezes:

    ÂNCORA QUE NÃO BATE CONTA COMO SOBREVIVEU, NUNCA COMO MORTO.

E apareceu o caso irmão, que é mais fino: um mutante que apagava o `if` da
presença da autorização **sobreviveu por não mudar comportamento nenhum**, porque
a conferência de identidade logo a seguir recusava na mesma. A garantia que ele
existia para partir já era guardada por outra linha.

    UM MUTANTE QUE NÃO MUDA O COMPORTAMENTO NÃO MEDE SENTINELA NENHUMA.

## 97.9 · DUAS LINHAS PARCIALMENTE CORRECTAS NÃO SÃO UM FLUXO

Ao escolher a base, mediu-se o *dependency closure* nos dois sentidos: a linha do
fluxo trazia dezoito commits (orquestrador, colheita, contrato de retorno,
ingresso, receitas, workflow) e a linha do gasto trazia um. Porta-se o delta
pequeno para a base grande, nunca o contrário.

E a base escolhida tinha **duas provas do controlo de gasto vermelhas**, pela
mesma razão: a guarda tinha chegado àquela linha e aqueles ficheiros continuavam
a chamar a porta paga sem trazer autorização nenhuma. Ninguém as tinha visto
porque cada metade, sozinha, passava.

    UMA CONVERGÊNCIA QUE DEIXA UMA DAS METADES VERMELHA NÃO CONVERGIU.

## 97.10 · O QUE FICA POR SABER

- Quatro dos cinco workflows pagos continuam a chamar a porta paga pelo próprio
  pé, passando ao lado do orquestrador. Medido, não migrado.
- A troca de transporte do sensor continua a existir e continua a ser mitigada,
  não desfeita. A razão original dela mantém-se válida; a forma — reescrever a
  porta de todos no corpo de um import — é que não.
- A relevância de fonte continua a viver noutra linhagem. Esta linha recebe o
  veredito dela e obedece; nenhuma das 77 fontes foi avaliada.

---

# §98 · UM PORTÃO QUE SÓ SE ALCANÇA COM INVENTÁRIO NÃO É UM PORTÃO DE POLÍTICA

**Missão:** `LINKEDIN-OP-01` · **Linha:** `claude/sintonia-scrap-linkedin-operational-close-v1`
**Base:** `claude/sintonia-scrap-canonical-flow-f01` (`84422284`)
**Tocado:** `coleta/adaptador_linkedin.py` · `coleta/comunicacao_coleta.py` ·
`coleta/scrap_capacidades.py` · `coleta/scrap_colheita.py` · `coleta/scrap_http.py` ·
`pedido/receitas.py` · `docs/sintonia-scrap/LINKEDIN-OP-01-OPERACIONAL-V1.md`

A missão era ligar a única capacidade LinkedIn que a política permite e fechar o
resto. O que se aprendeu não foi sobre o LinkedIn: foi sobre **portões que
existem, funcionam, e nunca são alcançados** — e sobre proibições que se
confirmam pedindo licença a quem se quer evitar.

## 98.1 · O PORTÃO ESTAVA LÁ, CERTO, E ATRÁS DE UMA PERGUNTA DE STOCK

`coleta/comunicacao_coleta.py::fase_posts()` já consultava `leis/social_matriz.py`
antes de qualquer rota paga. A `C10.6D` pôs a pergunta lá, e ela está correta.

Mas vinha **depois** de `contas_autorizadas()`. Para o LinkedIn, que não tem conta
autorizada nesta casa, a função voltava `None` a dizer *«nenhuma conta
AUTORIZADA»* — e a resposta sobre **permissão** nunca era alcançada. Medido: a
política só respondia quando se injetava uma conta à mão.

```
    AUSÊNCIA DE CONTA NÃO É ROTA NÃO PERMITIDA.
    UM PORTÃO QUE SÓ SE ALCANÇA COM INVENTÁRIO NÃO É UM PORTÃO DE POLÍTICA.
```

O defeito não era a ausência da pergunta — era a **ordem**. E ordem é difícil de
ver, porque o resultado observável era o certo: `None`, nada comprado. Dois factos
diferentes a produzir a mesma saída, e a casa a ler o mais tranquilizador.

O risco era prospectivo e silencioso: no dia em que alguém cadastrasse uma conta
LinkedIn, a proteção passava a depender de um gate que **ninguém tinha visto
responder**. Uma trava nunca exercida é uma trava suposta.

```
    DOIS MOTIVOS PARA O MESMO `None` NÃO SÃO O MESMO MOTIVO.
    QUANDO A SAÍDA COINCIDE, SÓ A ORDEM DIZ QUEM RECUSOU.
```

A pergunta subiu, e **não mudou de dono**. Ela continua a ser `social_matriz` a
responder — só deixou de estar atrás de uma pergunta de inventário. O que a fez
não virar um `if plataforma == 'LINKEDIN'` foi a regra que a casa já tinha: quem
tem capacidade canônica não passa pelo gate de `FETCH_POST`, porque a rota dela
não é essa. Gatear por nome desligaria o YouTube.

### E tirar a plataforma da tabela apagava a recusa

O ator pago do LinkedIn saiu de `ATORES`. Mas `_PLATAFORMAS()` é construído a
partir dessa tabela — e sem ele o LinkedIn desaparecia do CLI, levando a recusa
consigo.

```
    UMA RECUSA QUE NÃO SE ALCANÇA NÃO É UMA RECUSA: É UM SILÊNCIO.
```

Então nasceu uma **terceira** resposta à pergunta «esta plataforma passa por esta
fase?»: passa, e sai recusada pela política. Uma tabela, não um `if`.

## 98.2 · UM REDIRECIONAMENTO É UM PEDIDO NOVO

A rota permitida lê o site **da própria organização** e extrai dali o endereço que
a organização publicou. Medido: passar-lhe `site_url = linkedin.com` fazia-a **ir
ao linkedin.com** e devolver identidade com `RESULT = OK`.

Havia defesa em produção — `scrap_http.buscar` chama `permitido()`, que lê o
robots do host. Ela não serve, por duas razões:

1. ela **pergunta ao LinkedIn** se pode ler o LinkedIn, e a pergunta é ela mesma
   um pedido ao host que se quer evitar;
2. o parâmetro `transporte` — que existe para os testes e chega pelo `**extra` do
   `COLLECT` — passa por fora dela.

```
    UMA PROIBIÇÃO QUE SE CONFIRMA PELA REDE DEPENDE DA REDE.
    UMA PROIBIÇÃO QUE PERGUNTA AO PROIBIDO NÃO CHEGOU A ZERO PEDIDOS.
```

Quando a política já é estática, a recusa tem de ser estática.

### E o portão julgava só o primeiro endereço

`urlopen` segue 301/302 em silêncio. Um site com `Location: linkedin.com` levava o
pedido ao host proibido sem ninguém perguntar nada.

```
    UM PORTÃO QUE JULGA SÓ O PRIMEIRO ENDEREÇO NÃO JULGA O PEDIDO.
    UM REDIRECIONAMENTO É UM PEDIDO NOVO, E PEDE LICENÇA OUTRA VEZ.
```

Isto vive no dono do **transporte**, e não no adaptador: «o portão vale em cada
salto» é uma propriedade do transporte, e uma cópia da regra dentro de um
adaptador seria a regra a valer numa rota e a faltar em todas as outras. A **lista
de hosts** vem de quem a declara; o **ponto de cobrança** é do transporte. Dois
papéis da mesma trava, e nenhum copia o outro.

Uma nota de implementação que custou uma correção: a primeira versão abriu o
opener por fora (`_ABRIDOR.open(...)`). Funcionava — e passava por fora do teto de
rede da `§77`/`§80`, que cobra em `urllib.request.urlopen`. Instalar o opener
mantém `urlopen` como a única porta.

```
    UM CONSERTO QUE CONTORNA UM TETO NÃO É UM CONSERTO.
```

### E pela terceira vez na mesma cadeia

O `except Exception` de `buscar()` traduzia a recusa do **nosso** portão para
`RotaBloqueada`, que quer dizer «a plataforma nos impediu». O ficheiro já tinha
esse aviso escrito duas vezes, sobre a queda do túnel (`§80`) e sobre o teto.

```
    QUEM DISSE NÃO TEM NOME, E O NOME NÃO SE TROCA A CAMINHO DE CIMA.
```

Três ocorrências da mesma família no mesmo `try` dizem que o defeito não é
distração: é a forma. Um `except Exception` num sítio onde recusas próprias
sobem vai reetiquetá-las, sempre, e a cada nova recusa que alguém acrescentar.

## 98.3 · UM CAMPO DE TRADUÇÃO EMPRESTAVA UMA PERMISSÃO — OUTRA VEZ

A `§89.1` mediu isto no `scrap_capacidades`: um campo de tradução concedia uma
permissão. Aconteceu de novo, no mesmo campo, noutra linha.

`linkedin.recent.discovery` significa **as publicações recentes da página de
empresa**. Era ela quem traduzia para `DISCOVER_ACCOUNT` — cuja única rota
permitida lê o site de terceiro e devolve um **handle**. Logo
`pela_matriz('LINKEDIN','DISCOVER_ACCOUNT')` devolvia a capacidade de
**conteúdo**: o roteador que pedia identidade encontrava posts.

```
    IDENTITY != CONTENT, NA CAMADA DE TRADUÇÃO.
```

Nenhum código explorava a porta, porque nenhuma das sete capacidades tinha rota.
**A porta estava destrancada por dentro** — e é esse o estado mais perigoso, porque
não produz sintoma até alguém ligar a primeira rota.

### E quatro capacidades PROVEN prometiam sem poder cumprir

Encontrado por uma sentinela desta missão, não por leitura: quatro capacidades de
conteúdo estavam `PROVEN` — provadas por uma rota que a política hoje proíbe — e
`promete_resultado()` respondia **SIM** para capacidade **sem rota ligada**.

```
    TECHNICALLY_PROVEN_HISTORY != CURRENT_ALLOWED_ROUTE.
    UM ESTADO PROVADO POR UMA ROTA PROIBIDA PROMETE O QUE NÃO SE PODE CUMPRIR.
```

`BLOCKED` é literalmente «existe, não dá para usar agora (quota, teto, **termo**)».
O termo é o do LinkedIn, e a história técnica não se perde: vive no relatório do
censo, com os 372 posts e as datas. O que não fica é a promessa operacional.

## 98.4 · CADA FASE PASSOU A DIZER QUE ESPÉCIE PRODUZ

A `leis/retorno_da_coleta.py` nasceu a dizer que o «em que forma» **não tinha
campo nenhum, nem enum, nem guarda**, e mediu o preço: 253 itens de falsa
colheita, cento por cento.

A capacidade desta missão devolve um **endereço de conta** — que é a definição
literal de `CATALOG` naquela lei: «inventário de entidades de onde se PODE
coletar». E `ENTRAM_NO_INGRESSO = (COLHEITA,)`.

```
    UM ENDEREÇO DE CONTA NÃO É UMA OBSERVAÇÃO DELA.
    CATÁLOGO NÃO ATRAVESSA A PORTA — E O TERMINAL DELE TAMBÉM É CANÓNICO.
```

O contrato já recusava por construção. O que faltava era a **fase dizer**. O campo
entrou em `FASES`, obrigatório, e **sem valor por omissão**:

```
    UMA ESPÉCIE POR OMISSÃO É UMA DECISÃO QUE NINGUÉM TOMOU.
```

A lição de método é a que a missão recebeu por escrito e confirmou lendo: **não
empurrar um objeto para a Admissão só para completar uma seta.** Primeiro ler qual
espécie a capacidade realmente produz; depois ligar a mangueira.

## 98.5 · UM POSICIONAL NUMA LISTA COM BURACOS NÃO TEM POSIÇÃO

O orquestrador traduz filtros em argumentos de linha de comando, e só acrescenta o
valor **quando ele existe** (`if v:`). Então a posição de um argumento depende de
quais os anteriores estarem preenchidos.

Ler `resto[1]` como fonte e `resto[2]` como site punha o **site** no lugar da
**fonte** sempre que a fonte faltava — que foi exatamente o caso do pedido real
desta missão.

```
    UM ARGUMENTO POSICIONAL NUMA LISTA COM BURACOS NÃO TEM POSIÇÃO.
```

O que os distingue é a **forma**, e a regra que os distingue já era lei desta
casa: `SOURCE_ID != URL`. Um `SOURCE_ID` nunca tem esquema; um endereço tem
sempre. Classificar pela forma não fabrica identidade — recusa-se a fazê-lo.

## 98.6 · TRANCADO, E NÃO PELO DONO CERTO

O achado que a missão não pediu, e o risco mais alto que ela deixa escrito.

`regras/sensor_coleta.py` configura **quatro** atores HarvestAPI LinkedIn e
`grep -c social_matriz` naquele ficheiro dá **zero**: a política nunca é
consultada ali, e `_rodar()` leva um identificador de ator direto à porta paga.

Medido com chave no pool — para que a falta de token não se confunda com uma
trava, que é precisamente o que o censo já tinha registado como `FIRST_BREAK` —
quem o barra é `SemAutorizacaoDeGasto`, a guarda de gasto da `SCRAP-SR-02`:

```
    «Ter chave, teto e rota permitida não é ter autorização» · POSTS = 0
```

O caminho **está** fechado. E está fechado pelo dono do **gasto**, não pelo dono da
**política**.

```
    UM CAMINHO QUE NÃO PERGUNTA À POLÍTICA NÃO É PROTEGIDO PELA POLÍTICA.
    TRANCADO != TRANCADO PELO DONO CERTO.
```

A diferença é prospectiva: uma autorização de gasto concedida ali abriria quatro
atores LinkedIn sem a política ser perguntada uma vez. Ficou registado com
sentinela — para que a tranca não se perca em silêncio — e **não consertado**,
porque tornar aquele ficheiro inteiro consciente de política era expandir.

## 98.7 · IRMÃ DA §95: A RECUSA QUE CHEGA PRIMEIRO É A QUE SE LÊ

A `§95` mediu guardas presas ao **estado de hoje**. Esta é a mesma família por
outra ponta: uma sentinela presa a uma **razão de recusa**.

Ela exigia `DECLARED_WITHOUT_ROUTE` — «está declarada e não tem rota». Depois de a
capacidade descer para `BLOCKED`, o portão passou a responder
`CAPABILITY_STATE_PROMISES_NOTHING`, que vem **antes**: o estado recusa sozinho,
sem a pergunta da rota chegar a ser feita. A sentinela reprovou o dia em que a
casa ficou **mais estrita**.

```
    DUAS RECUSAS NÃO SÃO A MESMA RECUSA, E A QUE CHEGA PRIMEIRO É A QUE SE LÊ.
    PRENDER A MAIS TARDIA REPROVA O PROGRESSO, COMO PRENDER O ESTADO DE HOJE.
```

O conserto não é aceitar qualquer coisa: é guardar o que a sentinela **queria**
guardar — não há caminho executável — e aceitar as duas recusas, nunca um `OK`.

## 98.8 · E DUAS DE MÉTODO, CURTAS

**Uma aresta declarada que duplica uma provada.** Declarei
`C-SCRAP-COLHEITA → C-SCRAP-SOCIAL` e ela nasceu `UNKNOWN`: o scanner já provava a
relação na direção contrária.

```
    UMA ARESTA DECLARADA QUE DUPLICA UMA PROVADA NÃO ACRESCENTA UMA LIGAÇÃO:
    PÕE UM «NÃO SEI» AO LADO DE UM «SIM» SOBRE O MESMO FACTO.
```

A distinção que a missão pedia ao mapa foi para a **descrição da peça** que
carrega a fase — e a ausência de seta para conteúdo ficou escrita como
declaração, porque desenhar a seta faria o mapa prometer um caminho proibido.

**Um CLI sem falso injetado vai à rede.** Três execuções reais aconteceram numa
missão que planeava uma; a primeira foi por correr o executor pela linha de
comando para ver se a fase estava ligada. Zero dólares e zero pedidos ao LinkedIn
— mas as três deixaram bruto na árvore, e três suites de higiene do acervo
reprovaram, corretamente.

```
    CORRER O CLI É CORRER A ROTA.
    E TRÊS CÓPIAS DA MESMA PÁGINA NÃO SÃO TRÊS PROVAS.
```

## 98.9 · O QUE FICA POR SABER

- **A profundidade da descoberta indireta não está medida.** Uma sentinela de
  sete respondeu com handle. Quantas organizações do acervo publicam o seu é
  `NOT_MEASURED`, e medi-lo é uma passagem por sites de terceiros.
- **`PUBLICADO PELA ORGANIZAÇÃO != VERIFICADO`.** A rota devolve o que o site
  publica; que o handle seja da organização certa não é verificável por ela.
- **O que fazer com o catálogo** é decisão de quem coordena. Ele é candidato, e
  quem o recebe é o contrato de candidatas — não esta missão.

---

# §99 · DUAS LISTAS CERTAS QUE NÃO SE CRUZAM BLOQUEIAM TANTO COMO UMA PEÇA EM FALTA

**Missão:** `C-COLLECTION-V1-FINAL-OPERATIONAL-CERTIFICATION` — certificar a
Collection V1 como máquina operacional completa, excluindo só o SCRAP.
**Branch:** `claude/collection-v1-operational-close`
**Data:** 2026-09-12

A missão pedia uma frase de fecho e proibia escrevê-la sem prova. Encontrou-se
o contrário do esperado, e a parte durável é **como** se encontrou.

## 99.1 · UMA PERGUNTA SEM RESPOSTA PODE ESTAR MAL POSTA, E NÃO POR RESPONDER

A `§95` fechou com uma pergunta escrita para gente:

```
De quem é o `canal` de uma agência pública que publica boletins em PDF no
seu próprio sítio, e o que serve de `channel_id`?
```

Três opções ficaram em cima da mesa, todas consistentes com o modelo, e a
recomendação foi «nenhuma com evidência suficiente». Isso estava certo — e
estava incompleto. A pergunta assumia que a coisa existe e só falta descobrir
de quem é.

Não existe. `canal.channel_id` está comentado como «o id da plataforma, NUNCA o
nome» e `conteudo.content_id` como «id da plataforma (video_id, post_id)».
Nenhuma plataforma emitiu identificador nenhum para aquele PDF. A pergunta
pedia o nome de uma coisa que não tem nome porque não tem existência.

    UMA PERGUNTA QUE NÃO SE CONSEGUE RESPONDER DURANTE UMA MISSÃO INTEIRA
    MERECE UMA MEDIÇÃO DE SI PRÓPRIA ANTES DE MAIS UMA TENTATIVA.

O sinal que a denuncia: **as três opções falhavam pelo mesmo motivo.** Quando
opções desenhadas para serem diferentes partilham a causa de falha, a causa
está acima delas — está na pergunta.

## 99.2 · ONE CONCEPT → ONE OWNER NÃO É ONE TABLE FOR EVERY TYPE OF CONTENT

A lei que esta casa repete mais foi a que quase produziu o erro. Ler
`ONE CONCEPT → ONE OWNER` como «há uma tabela de conteúdo, logo todo o conteúdo
vai lá» leva direto a fabricar um `channel_id` para caber.

São duas leituras, e só uma é a lei:

```
CERTO   um conceito tem um dono — e «conteúdo de plataforma» e «documento
        não-plataforma» são DOIS conceitos, com duas identidades diferentes
ERRADO  uma tabela por família de coisa, e o que não couber que se adapte
```

A saída foi separar, não afrouxar: `public.documento_estruturado`
(migration 030), com chave `derived_artifact_id` — o documento é o registo
estruturado **daquele** derivado. `public.conteudo` ficou intacta, e o criador
de identidade de `canal` continua a **não existir**.

    UM CONCEITO DEIXAR DE PRECISAR DE UM DONO
    NÃO É O MESMO QUE ESSE DONO PASSAR A EXISTIR.

Conteúdo de plataforma continua a esbarrar na mesma falta. O gap mudou de nome
para dizer isso: era «STRUCTURED tem código que nunca correu», passou a
«STRUCTURED atravessa numa classe, e não nas duas».

## 99.3 · A ESPÉCIE NOVA: TUDO EXISTE E NADA PASSA

Fechada a aresta, o buraco andou — e chegou a um sítio que esta casa ainda não
tinha visto. Em `ADMISSION -> READY` **não falta peça nenhuma**. A porta existe,
julga os quatro itens, responde, e responde **certo**:

```
universos com regra de admissão escrita      T3 · T4 · T7 · T9
universos cujo executor declara colheita     T2
interseção                                   VAZIA
```

`COL-LAW-505` manda que só colheita entre no ingresso. `COL-LAW-502` manda que a
porta pergunte pela regra do universo. As duas leis cumpridas, ao mesmo tempo,
com estas duas listas, dão zero.

    FALTA DE PEÇA != PEÇAS QUE NÃO SE CRUZAM.

E as duas corrigem-se de maneiras opostas: a primeira construindo, a segunda
decidindo. Juntá-las debaixo do mesmo nome («falta fechar a aresta») faria a
segunda parecer trabalho de código, e ela não é. Foi por isso que a causa-raiz
antiga `RC-A` ganhou um campo `NAO_CONFUNDIR_COM`: o nome dela voltou a
descrever o presente, por **outro** motivo, e ler isso como «RC-A reabriu»
mandaria alguém reconstruir peças que já correm.

    INFRAESTRUTURA FUNCIONA != HÁ CASO ADMISSÍVEL NO CORPUS.

## 99.4 · UMA FRASE DE FECHO É UMA AUTORIZAÇÃO, E NÃO SE ARREDONDA

A missão mandava o red team **tentar** produzir
`ONLY_REMAINING_DEPENDENCY_IS_SCRAP = YES` e **falhar**. Tentou, e falhou — e o
motivo da falha é a parte transferível.

A armadilha não é mentir. É um raciocínio que parece sólido:

```
o SCRAP não está integrado          VERDADE
o SCRAP é preciso antes da coleta   VERDADE
logo: «só falta o SCRAP»            FALSO
```

O teste decisivo não é «o SCRAP está integrado?». É **«o buraco que está lá
seria tapado por integrar o SCRAP?»** Um buraco na porta de admissão não seria.
O SCRAP não escreve regra temática nem muda o que a porta pergunta.

Isto importa porque uma frase de fecho **autoriza alguém a começar outra coisa**.
«Só falta o SCRAP» faz uma pessoa abrir a integração do SCRAP — e, sendo falso,
ela integra o SCRAP e o buraco continua lá, agora com mais uma peça por cima.

Por isso as duas frases saem **calculadas** da mesma medição que faz o veredito,
e uma guarda garante que nenhum `"YES"` vive fora de uma condição dentro da
função que as produz.

## 99.5 · A GUARDA DE TEXTO MORDEU A REGRA OUTRA VEZ — E A CORREÇÃO JÁ TEM NOME

A guarda escrita para isso nasceu a procurar `", "YES"` na linha. Reprovou
`"YES" if pronto else "NO"`, que é exactamente a forma certa.

É a mesma família da `§95.4` (sete guardas a morder a prosa que explicava a
regra delas) e da `§86.7`. A correção é sempre a mesma e já não precisa de ser
descoberta: **AST em vez de texto**. A pergunta passou a ser estrutural — todo
`"YES"` dentro da função tem de viver dentro de uma condição. Um `"YES"` solto é
uma afirmação; um `"YES"` num `if` é um cálculo.

    PROCURAR O TEXTO DA REGRA NÃO É MEDIR A REGRA.

## 99.6 · TRÊS LISTAS ESCRITAS À MÃO ENVELHECERAM NA MESMA SEMANA

O censo dos portões declarava, em Python literal, qual etapa atravessava em que
rota. Dizia «`DERIVED` e `STRUCTURED` só atravessam na rota forward» e
«`FIRST_LOST_EDGE = STORAGE -> DERIVED`» muito depois de as duas coisas terem
deixado de ser verdade. Ninguém mentiu: a fronteira **anda** a cada missão, e a
lista não anda com ela.

```
ANTES  so_na_rota_forward = {"DERIVED", "STRUCTURED"}   # escrito à mão
DEPOIS lido de system-map/data/pedido.observado.json    # escrito por quem mede
```

    O CENSO NÃO DECIDE ONDE A ESTRADA PARA. ELE LÊ QUEM MEDIU.

Na mesma varrida caiu `MIGRATION_IN_GIT = 27`, com três migrations já entradas.
Passou a contar `git ls-files` — o **índice**, e não a pasta, porque um ficheiro
por commitar ainda não está em git e dizer que está é a mesma mentira com outra
roupa.

E a consequência de leitura: onze `fluxo=YES` numa coluna só leem-se como «a
estrada atravessa». A coluna «pelo pedido» passou a ir ao lado, sempre, com a
frase do buraco por baixo. `FLOW_EXECUTED = YES` com
`ATRAVESSA_PELO_PEDIDO = NO` não é contradição: é a distinção inteira.

## 99.7 · A MESMA DISCIPLINA APLICADA AOS TESTES DA PRÓPRIA MISSÃO

A `§95` registou três guardas que prendiam o estado de ontem e reprovavam o
progresso. Aconteceu de novo, em menor escala, e desta vez foi apanhado antes:
a docstring de um teste nomeava o buraco de então. Um teste que nomeia o buraco
de hoje falha no dia em que ele se fechar — que é o dia errado para um teste
falhar.

    UM TESTE QUE SÓ ESTÁ CERTO ENQUANTO NADA AVANÇA
    É UM TESTE QUE MEDE O PRIMEIRO DIA.

Mesma correção do resto da secção: o teste guarda a **propriedade** (o portão
exige a mesma história, e não a soma de `YES`), e lê o buraco de quem o mediu.

## 99.8 · O QUE FICA POR SABER

- `ADMISSION -> READY` continua aberto e é decisão de gente: escrever regra
  temática para `T2`, ou pôr colheita canónica num universo que já tem regra.
  Recomendada a primeira, com razão medida — `T2` é o único universo cujo
  executor já vai à fonte real e já declara colheita.
- A classe PLATAFORMA de STRUCTURED continua a esperar por um dono de identidade
  de canal. Não nasceu aqui, e não devia.
- Migration 030 **não foi aplicada em produção**. Medida contra descartável.
- Nenhum caso legitimamente admissível existe no corpus de hoje. Isso é um
  facto sobre o corpus, e não sobre a máquina — e a missão proibiu, por escrito,
  afrouxar a regra até um caso passar. Tinha razão: o veredito que saísse daí
  mediria a regra nova, e não a máquina.

---

# §100 · UMA DECISÃO QUE SÓ EXISTE EM PROSA VOLTA A SER TOMADA

**Missão:** `C-CLOSE-ADMISSION-TO-READY-V1` — fechar `ADMISSION → READY`.
**Branch:** `claude/collection-v1-operational-close`
**Data:** 2026-09-13

A `§99` fechou a recomendar: *escrever regra temática para `T2`, com uma razão
medida.* Estava errada. A medição que a desmente **já existia na árvore**, feita
por uma missão anterior, com 46 documentos reais e um portão fechado.

Esta secção regista como se chega a recomendar uma missão que já foi feita e
reprovada — e o que passou a impedir que volte a acontecer.

## 100.1 · O DIÁRIO DE DECISÕES NÃO É LEGÍVEL POR PROGRAMA

A decisão estava escrita, e bem escrita. Estava em
`docs/decisoes/DIARIO-DE-DECISOES.md`, numa entrada que abre com a frase certa:

> *«Esta entrada existe porque uma decisão de NÃO IMPLEMENTAR é a que mais
> facilmente se perde: não deixa código, e daqui a três meses alguém escreve a
> lista óbvia porque ninguém tinha tentado.»*

Três meses foi optimista. Foi **um dia**.

O autor previu o modo de falha exacto e escreveu a prevenção em prosa — e a
prevenção falhou porque **prosa não se cruza com outra medição**. O censo que
recomendou `T2` leu contratos, código e taxonomia. Não leu, nem podia, um
parágrafo em markdown.

```
ANTES   o veredicto de T2 vivia no diário e no terminal
DEPOIS  data/derivados/A-REGRA-DE-T2.json, e o censo LÊ-O
```

    UMA DECISÃO QUE SÓ EXISTE EM PROSA VOLTA A SER TOMADA.
    UM «NÃO» SEM ARTEFATO É UM «AINDA NÃO PERGUNTARAM».

É a irmã exacta da `§99.6`, e é pior do que ela. Lá, três listas escritas à mão
envelheceram e passaram a mentir sobre o presente. Aqui, uma decisão correcta,
completa e provada **não estava a mentir** — estava apenas fora do alcance de
quem decidia a seguir.

## 100.2 · «A UMA PEÇA DE DISTÂNCIA» NÃO ORDENA NADA

A `§99` mediu duas listas e cruzou-as: quem tem regra e quem tem colheita.
Interseção vazia. Verdade, e inútil para decidir — entre classes todas paradas,
nenhuma parece mais perto do que as outras.

O censo desta missão contou **o que falta a cada classe** das onze:

```
T2   tem aquisição · tem structured · falta a REGRA
T4   tem regra     · tem structured · falta a AQUISIÇÃO
```

Duas classes, uma peça cada. E aqui esteve a armadilha: **parecem empatadas, e
não estão.**

```
a peça de T2   já foi medida, e REPROVADA
a peça de T4   nunca foi tentada: é trabalho por fazer
```

    DUAS OPÇÕES NÃO SÃO DUAS OPÇÕES
    QUANDO UMA DELAS JÁ FOI MEDIDA E REPROVADA.

Contar o que falta transforma uma parede numa fila. Mas a fila só ordena depois
de se perguntar, a cada peça em falta, **se ela já foi tentada** — e essa
pergunta não se responde olhando para o que falta. Responde-se olhando para trás.

## 100.3 · QUATRO LETRAS E NENHUMA SERVE: QUANDO A CLASSIFICAÇÃO PEDIDA NÃO CHEGA

O brief pediu que a ausência da regra de `T2` fosse classificada como `A`
(deveria ter e falta), `B` (correctamente não deve ter), `C` (universos
incompatíveis) ou `D` (UNKNOWN).

Nenhuma serve inteira, e **escrever só uma letra mandava a próxima pessoa para o
sítio errado**:

| letra | para onde manda | por que está errada |
|---|---|---|
| `A` | escrever a lista | a lista foi procurada exaustivamente e reprovada |
| `B` | desistir de `T2` | `T2` é canónico, com 5 fontes e 10 positivos reais |
| `C` | refazer a taxonomia | as duas listas estão na **mesma** taxonomia |
| `D` | medir | já foi medido |

A resposta medida não é sobre o universo — **é sobre o mecanismo**. `T2` é
legítimo; o que não existe é maneira de o julgar com uma lista plana de palavras,
porque ela não distingue *documento SOBRE clima* de *documento que MENCIONA
clima*. As palavras óbvias de clima aparecem **mais fora** de `T2` do que dentro:
um boletim de praga fala do tempo a que a praga responde.

    QUANDO NENHUMA DAS OPÇÕES OFERECIDAS SERVE, A RESPOSTA HONESTA
    NÃO É A MENOS MÁ: É DIZER DE QUE É QUE ELAS FALAM TODAS AO LADO.

Registou-se `B_COM_A_RAZAO_DE_C`, com as três metades escritas ao lado. Uma letra
sozinha seria arrumação, não resposta.

## 100.4 · O TESTE DO SCRAP DEIXOU DE ARGUMENTAR PELA AUSÊNCIA

A `§99.4` já tinha o teste certo — *«o buraco que está lá seria tapado por
integrar o SCRAP?»* — e respondia-o mal: *«o SCRAP não escreve regra temática»*.
Verdade, e uma verdade **lateral**. Argumentava pelo que o SCRAP não faz, e
qualquer buraco novo teria de ser argumentado outra vez à mão.

Pior: a implementação adivinhava pelo **sítio** do buraco, com uma lista de
arestas escrita à mão (`EXECUTOR -> RUN`, `RUN -> RAW`). Responde bem aos buracos
que já se viram e mal a todos os outros — a mesma família da `§99.6`.

A versão medida faz uma conta:

```
o SCRAP é capacidade SOCIAL     →  a única classe com rotas sociais é T9
T9 tem regra temática           →  SIM
dá-se a T9 a aquisição de graça →  ainda falta DONO_STRUCTURED
logo                            →  T9 pára em STRUCTURED, uma etapa antes
```

    PARA SABER SE UMA PEÇA EM FALTA É A QUE BLOQUEIA,
    DÁ-SE-LHE A PEÇA DE GRAÇA E PERGUNTA-SE O QUE SOBRA.

Isto é generalizável e não tem nada de SCRAP: serve para qualquer dependência
que alguém queira nomear como bloqueio. E responde `NO` mesmo quando a
dependência é legítima e urgente, porque **`PRECISO ≠ BLOQUEANTE`**.

## 100.5 · O TESTE QUE GUARDAVA O MECANISMO EM VEZ DA PROPRIEDADE

Ao trocar a adivinha pela medição, um teste escrito **na missão anterior**
rebentou. Ele passava `EXECUTOR -> RUN` e exigia `YES` — estava a guardar a lista
de arestas, não a regra.

É a terceira vez nesta linha (`§95`, `§99.7`, agora). O sintoma é sempre o
mesmo: **o teste falha no dia em que o mecanismo melhora**, que é o dia errado
para um teste falhar. A correcção também é sempre a mesma: perguntar o que
sobrevive à mudança. Aqui sobrevive *«a certificação segue a medição»* — e o
teste novo prova-o **nos dois sentidos**, com a medição a dizer `YES` e a dizer
`NO`.

    UM TESTE QUE SÓ PROVA UM DOS SENTIDOS
    NÃO PROVA QUE O CÓDIGO SEGUE: PROVA QUE ELE CONCORDA HOJE.

## 100.6 · AMBIENTE E ARQUITECTURA SÃO DOIS BLOQUEIOS, E ESCREVEM-SE SEPARADOS

O canário medido é `T4`, e a fonte dele — o Ministero della Salute — **não passa
a verificação de TLS** deste ambiente: o servidor não envia a cadeia intermédia.
A fonte de `T2` responde `200` no mesmo instante e no mesmo ambiente.

Não se desligou a verificação. E os dois factos ficaram escritos **separados**:

```
ARQUITECTURA   o executor de T4 declara LEGADO e não COLHEITA
AMBIENTE       a fonte de T4 não verifica TLS aqui, medido em 2026-09-13
```

Juntá-los daria *«T4 está bloqueado»* — e mandaria a próxima pessoa desistir de
`T4` por causa de um certificado, ou tentar `T4` sem saber que vai bater num
certificado. O primeiro é permanente até alguém o escrever; o segundo pode
desaparecer sozinho noutra máquina.

    UM BLOQUEIO DE AMBIENTE COM DATA NÃO É UMA PROPRIEDADE DA ARQUITECTURA.

## 100.7 · O QUE FICA POR SABER

- **`ADMISSION → READY` continua aberto**, e agora tem dono e alvo: dar
  `ENVELOPE` por corrida ao executor de `T4`. É missão de código, não de gente.
- **A aquisição de `T4` não foi provada** neste ambiente, pelo certificado. Se a
  missão seguinte correr noutro sítio, esse obstáculo pode nem existir.
- **`T2` fica à espera de duas peças de arquitectura** que nenhuma missão de
  fecho deve improvisar: uma lei que diga o que é um documento ser *sobre* um
  assunto, e um mecanismo de admissão que conte sinais em vez de parar na
  primeira palavra. Nenhuma é urgente — `T4` fecha a máquina sem elas.
- **`TERRITÓRIO` e `UNIVERSO` continuam a ser duas coisas com o mesmo nome.** O
  território é propriedade da FONTE; o universo é pergunta ao DOCUMENTO. A ARPAV
  publica `T2` e `T3` e mostra os dois a divergir. Está medido, não está
  resolvido, e não foi tocado aqui.

---

# §101 · UMA TRANCA DE DINHEIRO NÃO É UMA TRANCA DE POLÍTICA

**Missão:** `SCRAP-RC-01` (Release Candidate V1) + `SCRAP-OP-CLOSE`.
**Branch:** `claude/sintonia-scrap-release-candidate-v1`
**Data:** 2026-09-13

A `§97` fechou o dinheiro: limite humano contra ledger, autorização selada,
cópia que não compra. A `§98` fechou um portão que só se alcançava com
inventário. Esta secção regista o que ficou **entre** as duas, e que nenhuma
delas vê.

## 101.1 · O CAMINHO ESTAVA TRANCADO, E PELA FECHADURA ERRADA

`regras/sensor_coleta.py` configura quatro atores HarvestAPI do LinkedIn e leva
um identificador de ator **direto à porta paga**, sem nunca perguntar à matriz
de rotas. Uma missão anterior mediu-o e registou-o como risco: o que o travava
era a guarda de **gasto**.

Estava trancado. E a tranca era a errada.

```
SEM autorização    -> POST 0   ✔ parecia seguro
COM autorização    -> POST 1   ✘ a rota proibida corria
```

    SPEND_AUTHORIZATION != ROUTE_POLICY.
    DINHEIRO AUTORIZADO NÃO TORNA PERMITIDA UMA ROTA PROIBIDA.

Uma tranca de dinheiro guarda **enquanto não houver dinheiro**. No dia em que
alguém concedesse a autorização — que é o dia para que a autorização existe — a
rota proibida passava, e a política continuaria a nunca ter sido perguntada.

E o botão continuava lá: `workflow_dispatch`, alcançável à mão, naquele dia.

    DIZER «É LEGADO» NUM DOCUMENTO NÃO DESLIGA UM BOTÃO.

## 101.2 · A CORREÇÃO NÃO VAI NO CAMINHO. VAI NA PRIMITIVA

Havia a tentação de pôr a pergunta em `sensor_coleta.py`, que era onde o
problema aparecia. Ela foi para `coleta/coletor.py` — o único sítio onde nasce
execução paga — e corre **antes** da guarda de gasto.

    UMA GUARDA QUE VIVE NUM CAMINHO GUARDA UM CAMINHO.
    UMA GUARDA QUE VIVE NA PRIMITIVA GUARDA TODOS.

A ordem também é lei: uma rota proibida não deve sequer **consumir** uma
execução da autorização de quem a pediu. Medido depois: `POST 0` e
`autorização gasta = 0`.

E a recusa ganhou classe própria. Vesti-la de `GastoRecusado` diria que faltou
autorização — e no dia em que alguém a concedesse, a mensagem mandaria procurar
no sítio errado.

    UMA RECUSA COM O NOME DE OUTRA MANDA CONSERTAR A COISA ERRADA.

## 101.3 · A POLARIDADE DE UMA LISTA DE PROIBIÇÃO

A pergunta «este ator é proibido?» tem duas respostas erradas possíveis, e só
uma delas é óbvia. Responder `False` a tudo abre a porta. Mas responder `True`
ao que a matriz não nomeia **fecha a casa inteira**: a maior parte dos atores
desta casa é nomeada pela CAPACIDADE, não pelo id — o `apify:transcricao` do
YouTube é exactamente isso.

A regra que ficou: proibido quando a matriz o nomeia numa rota `PERMITIDA = NAO`
e em **nenhuma** permitida.

    DECLARADO PROIBIDO != NÃO DECLARADO.
    O SILÊNCIO DA MATRIZ NÃO PROÍBE, E TAMBÉM NÃO AUTORIZA.

## 101.4 · `READY` NÃO QUER DIZER QUE ALGUÉM A PEÇA

Ao classificar a superfície V1 apareceu um campo que não existia: onde é que
cada capacidade **para**. E com ele um facto que nenhuma contagem mostrava:

```
READY                                    9
  das quais FIRST_BREAK = NO_REQUEST_PATH  5
```

Cinco capacidades prontas, permitidas, gratuitas — e **nenhuma fase do caminho
canônico as pede**. Não é defeito de engenharia; é trabalho de release por
fazer, e ninguém o via porque `READY` soa a fim de linha.

    CAPABILITY READY != CAPABILITY PEDIDA.
    UM NÚMERO DE PRONTAS NÃO DIZ QUANTAS ALGUÉM CONSEGUE PEDIR.

Daí os três degraus, e nenhum promete o seguinte:

    NO -> WIRED -> OBSERVED.
    MODULE EXISTS != EDGE EXISTS != FLOW OBSERVED.

## 101.5 · A RELEVÂNCIA GUARDA O GASTO, E NÃO A OBSERVAÇÃO

O livro de relevância está vazio, e durante duas missões isso leu-se como «a
máquina não pode trabalhar». Medido nos quatro eixos, contra o livro vazio:

| plano | formas de gasto abertas | bloqueia? |
|---|---|---|
| grátis · pontual | nenhuma | **não** |
| grátis · agendado | `COLETA_RECORRENTE` | sim |
| pago · pontual | `ROTA_PAGA` | sim |
| grátis · escopo TOTAL | `COLETA_TOTAL` | sim |

    O PORTÃO GUARDA O GASTO, NÃO A OBSERVAÇÃO.  (COL-LAW-018)

O livro vazio não impede observar. Impede **comprar, repetir sozinho e varrer
tudo** — que são três formas de gasto, e não três formas de olhar.

E a consequência de método: quando uma lei parece bloquear tudo, perguntar-lhe
em vez de assumir. Alargá-la em silêncio para «toda coleta precisa de
relevância» teria sido inventar um requisito e chamar-lhe prudência.

    NÃO SE AUMENTA UM CONTRATO PARA O FAZER PARECER MAIS SEGURO.

## 101.6 · O CANÁRIO NÃO É A PLATAFORMA MAIS IMPORTANTE

O canário da Release foi o Bluesky: gratuito, permitido, sem credencial, sem
navegador autenticado, sem fornecedor pago. Não é a plataforma de maior valor
comercial desta casa, e essa foi exactamente a razão.

    O CANÁRIO EXISTE PARA PROVAR A MÁQUINA, NÃO A PLATAFORMA.
    LINKEDIN TESTA LINKEDIN. BLUESKY TESTA A MÁQUINA.

E houve um achado que só apareceu por o canário ter sido escolhido assim: a
única fase que o caminho canônico sabia pedir corria numa capacidade
`DATACENTER_BLOCKED` — precisa de máquina residencial.

    UMA ÁRVORE QUE SÓ SABE PEDIR O QUE NÃO CONSEGUE CORRER
    NÃO SE CONSEGUE PROVAR A CORRER.

## 101.7 · META CADEIA PROVADA, META CADEIA POR PROVAR

A `SCRAP-OP-CLOSE` procurou uma conta real ligada a um `SOURCE_ID` canônico.
Encontrou **metade** da cadeia, muito bem provada:

```
CONTA  <-  EMPRESA     PRIMARY_DECLARED_LINK · 32 PROVED · 22 autorizadas
           «o site oficial local declara este link.
            Primeira parte falando de si própria — não é busca por nome.»
```

E a outra metade em aberto, declarada em aberto pela própria casa:

```
EMPRESA  <-  SOURCE_ID   STATUS = REDEFINED · «REQUER DECISÃO»
                         0 das 23 fontes do atlas carrega conta de plataforma
```

O erro fácil era juntá-las: a conta é da BASF, a ficha fala da BASF, logo a
conta é da ficha. É plausível, e cada passo é verdadeiro — mas a ficha também
declara, na mesma linha, que **não mede empresa a empresa**.

    UMA FICHA QUE NOMEIA A EMPRESA E DIZ QUE NÃO A MEDE
    NÃO É UM VÍNCULO COM A CONTA DELA.
    DUAS METADES PROVADAS NÃO FAZEM UMA CADEIA PROVADA.

## 101.8 · E QUATRO DEFEITOS DE SONDA, PORQUE ELES REPETEM-SE

Nenhum estava no código medido. Todos estavam em quem media.

- **Contar um nome que ninguém escreve mais.** Uma classificação foi partida de
  três classes em seis; a sonda continuou a contar a classe antiga, obteve zero,
  e deu-se por satisfeita.
- **Julgar uma missão pela história inteira.** «Houve merge bruto?» perguntado
  ao log completo reprovava por merges de dois meses antes.
- **Medir a lei contra a própria lei.** Uma sentinela comparava os estados
  contra as constantes do próprio módulo; trocar o VALOR da constante deixava-a
  verde, porque os dois lados mudavam juntos.
- **Um falso instalado no import.** Uma bateria trocou `urlopen` no topo do
  módulo e nunca o devolveu. O carregador importa todos os módulos antes do
  primeiro teste — e uma bateria de outra missão, que levanta um servidor em
  `127.0.0.1`, passou a falar com um mundo falso que nunca ouviu falar de
  loopback.

```
UMA SONDA QUE CONTA UM NOME QUE NINGUÉM ESCREVE MAIS CONTA ZERO
E CHAMA-LHE PROVA.

MEDIR A HISTÓRIA INTEIRA PARA JULGAR UMA MISSÃO JULGA AS OUTRAS.

MEDIR A LEI CONTRA A PRÓPRIA LEI É MEDIR UMA TAUTOLOGIA.

UM FALSO INSTALADO NO IMPORT VIVE ENQUANTO O PROCESSO VIVER.
```

E um mutante que sobreviveu e valia a pena: pôr uma capacidade proibida de volta
em `PROVEN` não fazia a máquina correr — o portão continuava a recusar. Mudava
só o que a casa **diz**.

    UM MUTANTE QUE SÓ MUDA O QUE A CASA DIZ AINDA MUDA ALGUMA COISA:
    MUDA AQUILO EM QUE A PRÓXIMA MISSÃO VAI ACREDITAR.

## 101.9 · O QUE FICA POR SABER

- **Nenhuma conta está ligada a um `SOURCE_ID` canônico.** Três candidatos
  estão na mesa com uma pergunta de `SIM`/`NÃO`/`NÃO SEI`, e a máquina espera.
- **Cinco capacidades `READY` não têm quem as peça.** Decidir quais entram no
  caminho canônico é trabalho de release.
- **O bruto continua `NOT_PRESERVED` no dono forward.** Fica no disco do runner
  com SHA e dono nomeado, e o G-42 ainda não o recebeu.
- **Quatro desvios declarados continuam alcançáveis** por um workflow. Eles
  adquirem, saltam o `COLLECT`, e dizem-no na saída — o que é uma medição, e não
  um buraco. Fechá-los é fan-out, e não era destas missões.

---

# §102 · A FONTE QUE NÃO RESPONDE NÃO É A CLASSE QUE NÃO PRESTA

**Missão:** `C-T4-CANONICAL-ACQUISITION-TO-WAITING-ROOM-V1` — dar aquisição
canónica a T4 e fechar `ADMISSION → READY`.
**Branch:** `claude/t4-canonical-acquisition-v1`
**Data:** 2026-09-13

A Collection V1 fechou. Um pedido `T4` real atravessou as onze etapas na mesma
corrida, do botão à Sala de Espera, com o executor a ir à fonte oficial e a
porta a dizer `SIM` por uma regra que já existia.

Esta secção regista **como quase não fechou**, que é a parte que se transfere.

## 102.1 · MEDIU-SE A FONTE E CONCLUIU-SE SOBRE A CLASSE

A `§100` entregou `T4` como canário com um blocker de ambiente ao lado:

```
a fonte de T4 não passa a verificação de TLS deste ambiente
www.fitosanitari.salute.gov.it — unable to get local issuer certificate
```

Verdade, e medida com cuidado. E **enganosa**, porque a frase diz «a fonte de
T4» quando o que foi medido é *a fonte que o executor da receita usa*. O atlas
tem **oito** fontes T4 aprovadas. Ninguém as tinha perguntado.

```
IT-T4-001  dati.salute.gov.it       200 · CSV 4,6 MB
EU-T4-001  publications.europa.eu   200 · GREEN · sabe_coletar: true
FR         data.gouv.fr             404 (rota mudou)
—          fitosanitari.salute.gov  TLS não verifica
```

    A FONTE QUE O EXECUTOR USA NÃO É «A FONTE DA CLASSE».
    UMA CLASSE TEM UM ATLAS; UM EXECUTOR TEM UM ENDEREÇO.

O erro é fácil de repetir porque a medição estava certa e o salto era pequeno:
mediu-se um host, escreveu-se «a fonte», leu-se «a classe». **Um bloqueio de
ambiente com data é uma afirmação sobre um endereço, e nunca sobre a classe
inteira** — a menos que alguém tenha perguntado a todos os endereços dela, e
isso é uma medição diferente, que custa quatro `curl`.

## 102.2 · A ROTA QUE O CONTRATO DA FONTE JÁ DECLARAVA

`EU-T4-001` responde, e o colector que ela tem (`coleta/cellar.sh`) devolve
XHTML. O derivador canónico desta casa extrai texto de **PDF**: medido, um
ficheiro que não começa por `%PDF` sai com `EXTRACTION_ERROR`.

O caminho fácil dali seria escrever um derivador para XHTML — e abrir uma
segunda casa de derivação por causa de um formato.

Não foi preciso. O contrato da fonte, escrito muito antes, já dizia:

```
fallback: "EUR-Lex por CELEX (mesma casa, outra rota)"
```

O EUR-Lex serve o **mesmo ato** em PDF oficial. A rota estava declarada e
ninguém a tinha usado.

    ANTES DE CONSTRUIR A PEÇA QUE FALTA,
    LER O CONTRATO DA FONTE ATÉ AO FIM.

Esta é irmã da `§100.1` com o sinal trocado: lá, uma decisão perdeu-se por
estar só em prosa; aqui, uma **capacidade** estava escrita num campo estruturado
e também não foi lida. O campo existia, tinha nome, e estava a três linhas de
distância do que já se estava a ler.

## 102.3 · O PRIMEIRO `DOCUMENT_ID` PROVADO DESTA CASA

Durante missões seguidas, `DOCUMENT_ID` foi sempre `NULL`, e sempre com razão:
um boletim da ARPAV não traz número que a fonte declare, e derivá-lo do sha, do
caminho ou da URL seria fabricar.

`EU-T4-001` declara, no contrato dela:

```
identity_keys: CELEX
```

O CELEX **é** o nome que o emissor dá ao ato. Escrito, ele atravessa até
`raw_asset.document_key` com `document_key_basis = SOURCE_DOCUMENT_ID` e
`identity_state = FORWARD_IDENTIFIED` — a primeira observação desta casa com
identidade documental provada.

    SHA É DOS BYTES. CAMINHO É MORADA. URL É ENDPOINT.
    CELEX É O NOME QUE O MUNDO DEU AO DOCUMENTO.

E apanhou-se, ao lado, uma frase que tinha ficado verdadeira e deixou de ser. O
orquestrador dizia, em comentário:

> *«`document_id` NÃO VAI. A fonte documental não o prova.»*

Era verdade da **única** fonte que por ali tinha passado.

    UMA FRASE VERDADEIRA SOBRE A ÚNICA FONTE QUE JÁ PASSOU
    NÃO É UMA FRASE VERDADEIRA SOBRE A ESTRADA.

Corrigiu-se a frase e **não** se alargou o transporte: levar o `CELEX` até
`documento_estruturado` atravessa quatro donos, e isso é trabalho deliberado. A
identidade não se perde — vive na casa dela — e o `NULL` no registo estruturado
passou a significar «esta casa ainda não o transporta», que não é a mesma
ausência que «a fonte não o provou».

## 102.4 · O `or` QUE QUASE ESCREVEU UMA FRASE FALSA

Com o core a fechar, a certificação calculava:

```python
ONLY_REMAINING_ACQUISITION_DEPENDENCY_IS_SCRAP = pronto or fecharia == "YES"
```

O primeiro ramo ficou verdadeiro no instante em que a máquina fechou, e a frase
passou a dizer **«só falta o SCRAP»** sem nunca ter perguntado quem mais falta.
Medido: nove classes sem aquisição canónica, e só **uma** é do domínio do SCRAP.

    A MÁQUINA ESTAR FECHADA NÃO DIZ NADA
    SOBRE QUANTAS CLASSES AINDA NÃO A ATRAVESSAM.

É a terceira armadilha seguida na mesma frase (`§99.4`, `§100.4`, esta), e a
primeira que estava **no código** e não no raciocínio. As duas anteriores
apanharam-se a pensar; esta só se apanhou porque o veredito mudou de lado e
alguém foi reler o cálculo.

> **UMA CONDIÇÃO DE ATALHO NUM VEREDITO SÓ SE REVELA
> NO DIA EM QUE O OUTRO RAMO MUDA.**

Enquanto o core esteve `FAIL`, `pronto` foi sempre `False` e o `or` nunca fez
nada. Ele não estava testado: estava **adormecido**. Um veredito com um ramo que
nunca se exerce é um veredito por medir.

## 102.5 · TRÊS GUARDAS DE OUTRAS MISSÕES REBENTARAM, E AS TRÊS TINHAM RAZÃO DE SER

Fechar a estrada partiu três testes escritos antes. Nenhum era mau; os três
codificavam o **mecanismo** de então:

| guarda | o que codificava | o que sobrevive |
|---|---|---|
| `test_6_nenhum_executor_antigo…` | «todos menos `italia-recorrente`» | pedir a corrida é acto deliberado e visível |
| `test_sem_medicao_o_portao_nao_diz_PASS` | apagar **um** ficheiro | esconder **todas** as medições que o portão lê |
| `test_o_yes_nao_esta_escrito_a_mao` | qualquer `"YES"` fora de condição | `"YES"` **produzido**, não `"YES"` **comparado** |

O terceiro é o mais instrutivo: a guarda bania `"YES"` solto e apanhou
`if x != "YES"`.

    AFIRMAR «YES» É PRODUZIR UM VEREDITO.
    COMPARAR COM «YES» É LER O VEREDITO DE OUTRO.

É a mesma família da guarda que bania `listdir` e reprovava quem listava a Sala
de Espera para a medir. Uma guarda larga de mais reprova o uso legítimo, e quem
a herdar aprende a desligá-la — que é pior do que não a ter.

E o segundo tem uma regra própria que vale a pena isolar: ele escondia uma fonte
para provar «sem medição». Quando o número de fontes pode crescer, esconder uma
deixa de ser esconder todas — e a correcção é o teste **ler a lista do módulo**
em vez de a repetir.

## 102.6 · A QUARTA VEZ QUE UMA GUARDA MORDEU A PROSA DA PRÓPRIA REGRA

`test_nenhum_canal_nem_conteudo_de_plataforma_e_criado` procurava `channel_id`
no texto do executor — e o executor **diz**, na docstring, que não inventa
`channel_id`.

Quarta ocorrência (`§95`, `§99.5`, `§100.5`, esta). A correcção já não se
descobre, aplica-se: **AST em vez de texto**. Desta vez ficou um ajudante com
nome, `_codigo_sem_prosa`, que devolve o ficheiro sem comentários e sem
docstrings — `ast.unparse` deita fora os comentários sozinho, as docstrings
tiram-se à mão.

    PROCURAR O TEXTO DA REGRA NÃO É MEDIR A REGRA.

Vale registar que a guarda de TLS do mesmo ficheiro **é** de texto, de
propósito, e isso está escrito ao lado dela: as formas de desligar TLS em Python
são poucas e têm nome próprio (`_create_unverified_context`, `verify=False`,
`CERT_NONE`). São chamadas de biblioteca, não prosa. A regra não é «nunca
guardas de texto» — é «não procurar a regra no texto que a explica».

## 102.7 · O QUE FICA MEDIDO E NÃO CONSERTADO

**`G-ENV-01` · o envelope vive num caminho por executor, e não por corrida.**
Medido: pediu-se a colheita de uma corrida que não existe, e o orquestrador
devolveu a da última que escreveu — sem nota e sem recusa. Não é defeito desta
missão (o adapter italiano tem-na igual) e em série não morde. Morde quando duas
corridas do mesmo executor se cruzarem, que é a coleta grande.

E **não virou um `caso()` com veredito**, de propósito:

    UMA GUARDA QUE FIXA O DEFEITO DE HOJE DEFENDE O DEFEITO.

Um caso que afirmasse o comportamento actual reprovaria quem o consertasse.

## 102.8 · O QUE FICA POR SABER

- **Nove classes continuam sem aquisição canónica**, e só `T9` é do SCRAP. As
  outras oito esperam por executores que ninguém escreveu.
- **`T2` continua sem poder ser julgada** — falta uma lei que diga o que é um
  documento ser *sobre* um assunto, e um mecanismo que conte sinais. Nenhuma é
  urgente agora: `T4` fecha a máquina sem elas.
- **O `CELEX` não chega a `documento_estruturado`.** Vive em `raw_asset`, que é
  a casa dele; transportá-lo atravessa quatro donos.
- **A fonte `fitosanitari.salute.gov.it` continua sem verificar TLS** deste
  ambiente. Não se desligou a verificação, e o executor `rotulos-oficiais`
  continua na receita — atrás, porque indexa e não colhe.

---

# §103 · O QUE FUNCIONA EM SÉRIE NÃO ESTÁ PROVADO: ESTÁ POR PROVAR

**Missão:** `C-COLLECTION-OPERATIONAL-READINESS-OVERNIGHT-V1` — deixar a
Collection pronta para operar.
**Branch:** `claude/collection-operational-readiness-overnight-v1`
**Data:** 2026-09-13

A máquina estava provada de ponta a ponta. Bastou pô-la a correr **cinco vezes
ao mesmo tempo** para encontrar quatro defeitos, e um deles corrompia dados em
silêncio.

```
5 corridas concorrentes  ->  CORRIDAS_DISTINTAS = 1 · SUCCESS = 1 · ERROR = 4
```

    UMA MÁQUINA PROVADA EM SÉRIE É UMA MÁQUINA PROVADA EM SÉRIE.

## 103.1 · O SEGUNDO NÃO É UMA IDENTIDADE

A corrida chamava-se `{país}-{alvo}-{AAAA-MM-DD-HHMMSS}`. Cinco corridas do
mesmo alvo no mesmo segundo receberam **o mesmo nome**. Quatro rebentaram na
chave única de `etapa_da_corrida`.

E rebentar foi o **bom** desfecho: o banco recusou. O mau é silencioso, e
acontece em cada tabela sem essa chave — as observações de uma corrida ficam
atribuídas a outra, e ninguém vê.

    DUAS COLETAS NO MESMO SEGUNDO NÃO SÃO A MESMA COLETA.
    UM NOME QUE SE REPETE NÃO É UM NOME.

**E o tamanho do desempate mediu-se, não se escolheu a olho.** A primeira
correcção usou três bytes. Com 400 nomes gerados de uma vez, houve **uma**
colisão — 400 contra 399 distintos. Três bytes dão 16,7 milhões de valores, e o
paradoxo dos aniversários come isso depressa.

    «IMPROVÁVEL» NÃO É «IMPOSSÍVEL», E A COLETA GRANDE
    É EXACTAMENTE ONDE O IMPROVÁVEL ACONTECE.

Ter criticado os microsegundos por «reduzirem sem fechar» e depois aceitar três
bytes seria aplicar duas réguas. Ficaram oito.

## 103.2 · TRÊS SÍTIOS, UM SÓ DEFEITO: ESCRITA NÃO-ATÓMICA EM CAMINHO PARTILHADO

Depois do nome, caíram três coisas seguidas, e no fim eram a mesma:

| onde | o que acontecia |
|---|---|
| livro de decisões | ler-juntar-escrever sem trava → `LivroIlegivel`, e pior: *lost update* silencioso |
| PDF preservado | `open(…,"wb")` trunca antes de encher → outra corrida lê «não é PDF» e vai à rede |
| *(já curado antes)* Sala de Espera | tinha exactamente a mesma cura, de outra missão |

    UM FICHEIRO A MEIO DE SER ESCRITO NÃO É UM FICHEIRO VAZIO:
    É UM FICHEIRO QUE MENTE DURANTE UNS MILISSEGUNDOS.

A cura é sempre a mesma e já não precisa de ser descoberta: **corpo inteiro num
temporário na mesma filesystem, `fsync`, `os.replace`.** Quem ler durante a
escrita vê o ficheiro anterior, inteiro.

**Mas a trava não é sempre a mesma, e essa parte é conceito e não gosto.** Na
Sala de Espera a trava é *fail-fast*: duas escritas da MESMA corrida na mesma
morada são um conflito e devem gritar. No livro de decisões é **bloqueante**:
muitas corridas diferentes acrescentam ao mesmo livro, não há conflito nenhum,
há fila. Fazer o livro falhar transformaria trabalho legítimo em erro.

    A MESMA CURA, DUAS TRAVAS DIFERENTES:
    CONFLITO GRITA, FILA ESPERA.

## 103.3 · A CORTESIA NÃO É ENFEITE, E APRENDEU-SE PERDENDO A FONTE

O executor de T4 foi à mesma fonte umas dez vezes em duas horas — sem pausa,
sem recuo, e **sem reaproveitar os bytes que já tinha em disco**. O EUR-Lex
passou a responder `202` com corpo vazio a **tudo**: qualquer formato, qualquer
documento, host inteiro.

    UM COLETOR SEM CORTESIA NÃO PERDE UM DOCUMENTO: PERDE A FONTE.

E o `202` revelou um segundo erro, este de vocabulário: o executor chamava-lhe
`VAZIO`, que se lê como «a fonte não tinha nada».

    A FONTE QUE ME TRAVA NÃO É A FONTE QUE NÃO TEM NADA.

`EMPTY_SUCCESS != ERROR` continua a valer — uma fonte que responde e não tem
nada é um sucesso vazio. O que não pode é um travão passar por isso. Ficaram
cinco estados distintos, e `FONTE_INDISPONIVEL` é um deles.

**E a correcção mais barata foi não ir.** Bytes já preservados não se vão
buscar outra vez: zero informação nova, uma janela de escrita a mais, e um
pedido a mais a uma fonte pública.

    A ESCRITA MAIS SEGURA É A QUE NÃO ACONTECE.

## 103.4 · REAPROVEITAR BYTES ATRAVESSA A ESTRADA E NÃO PROVA A AQUISIÇÃO

O reaproveitamento local salvou a noite — a fonte estava travada e a estrada
continuou a atravessar. E abriu a porta a uma mentira confortável: uma noite
inteira de provas verdes a dizer «a aquisição funciona» sem ninguém ter aberto
uma ligação.

São duas propriedades, e separaram-se:

```
CANONICAL_E2E_T4     PASS         a máquina atravessa
AQUISICAO_PELA_REDE  NOT_PROVEN   a ida à fonte, nesta corrida, não
```

O executor **declara** `ORIGEM_DOS_BYTES`, e a prova lê a declaração em vez de
a supor.

    FIXTURE PROVA PARSER. SÓ A INTERNET PROVA AQUISIÇÃO.
    E REAPROVEITAR O QUE JÁ SE TEM NÃO É FIXTURE — É TAMBÉM NÃO É REDE.

## 103.5 · UM CASO QUE PASSA PORQUE NÃO CONSEGUIU MEDIR É UM CASO QUE NÃO MEDIU

A prova de crash simulava a morte rebentando a etapa seguinte. Quando a excepção
subia, não havia recibo — e a primeira versão dava-se por satisfeita com «a
excepção subiu», marcando `PASS`.

Isso mede o **chamador**. A pergunta era sobre o **estado**: o que ficou escrito,
e dá para o ler?

    UM CASO QUE PASSA PORQUE NÃO CONSEGUIU MEDIR É UM CASO QUE NÃO MEDIU.

A corrida morta encontra-se onde deixou marca — no banco, comparando o conjunto
de corridas antes e depois. O recibo nunca foi a verdade; era só o caminho mais
fácil até ela.

## 103.6 · A CURA TROUXE UMA CONSEQUÊNCIA, E ELA MEDE-SE TAMBÉM

Dar um endereço por corrida ao envelope resolveu o cruzamento — e passou a
deixar **um ficheiro por corrida, para sempre**. Uma noite de medição deixou
413 envelopes numa pasta.

Não é perda nem confusão: o órfão é inerte desde que o endereço leva a corrida,
e a pasta está no `.gitignore`. É crescimento sem fim, e isso decide-se antes da
coleta grande, não durante.

    UMA CORRECÇÃO QUE NÃO MEDE O QUE PASSOU A CRIAR
    TROCA UM DEFEITO CONHECIDO POR UM DESCONHECIDO.

Ficou `G-ENV-02`, com nome, antes de alguém tropeçar nela.

## 103.7 · `UNKNOWN` COM MOTIVO NÃO É ZERO

O LIVE não foi alcançado, e a resposta não é «não sei»: **este ambiente não tem
as credenciais**, medido variável a variável. Daí `LIVE_SCHEMA_VERSION`,
`MIGRATION_029_LIVE` e `MIGRATION_030_LIVE` ficarem `UNKNOWN`.

    ZERO MANDA APLICAR TUDO. NÃO-MEDIDO MANDA IR VER PRIMEIRO.

O caminho, esse, foi ensaiado inteiro num descartável virgem — incluindo a
segunda passagem, que é a que importa: `SKIP (já no livro-razão) HASH=MATCH`.
E o que **não** se mediu ficou escrito como não medido: a capacidade de backup
do LIVE. Escrever «há backup» sem ter visto seria a única linha perigosa do
pré-voo.

## 103.8 · REPROCESSAR TEM DE DIZER O QUE REPROCESSA

Dar endereço por corrida ao envelope partiu uma coisa que ninguém esperava:
`--so-a-porta`, o caminho que leva à peneira uma colheita **já existente** —
usado para reprocessar quando a regra muda.

Ele funcionava lendo «o último envelope que estivesse lá». Ou seja: **o defeito
estava a ser usado como funcionalidade.**

    UMA FUNCIONALIDADE QUE DEPENDE DE UM DEFEITO
    PARTE-SE NO DIA EM QUE O DEFEITO É CURADO — E ESSE É O DIA CERTO.

O reprocessamento passou a nomear a corrida cuja colheita quer: a corrida nova
é nova e julga de novo; o que se reaproveita é o **material**, não a corrida.
Isto arrumou de vez os quatro conceitos que o brief mandava separar:

```
corrida nova      material novo, corrida nova
retry             a mesma corrida outra vez
reprocessamento   material de OUTRA corrida, corrida nova, julgamento novo
reuse             o derivado reencontra-se; a etapa correu
```

## 103.9 · UMA GUARDA QUE COMPARA COM `HEAD` DEIXA DE GUARDAR NO COMMIT SEGUINTE

Dois testes de missões antigas dizem «`admissao/` não pode mudar nesta missão»
e implementam-no com `git diff HEAD -- admissao/`.

Isso compara a **árvore de trabalho** com o `HEAD`. Falha enquanto a alteração
está por commitar e **passa assim que ela é commitada** — inclusive quando o
commit muda exactamente aquilo que a guarda dizia proteger.

    UMA GUARDA CONTRA `HEAD` NÃO GUARDA A MISSÃO: GUARDA O INSTANTE.
    Ela avisa enquanto se trabalha e cala-se no fim.

Não se corrigiu aqui — é guarda de outra linha, e mexer-lhe na semântica é
outra missão. Fica registado porque explica um par de vermelhos que depois
ficaram verdes sozinhos, e porque quem confiar nela para provar que algo não
mudou vai confiar em nada.

## 103.10 · UMA IMPRESSÃO DIGITAL LARGA APANHA O QUE NÃO É DELA

O baseline da Admission de T3 guarda uma impressão que inclui o `sha256` do
**ficheiro inteiro** do dono da porta. Pôr uma trava no livro de decisões moveu
a impressão — sem mover uma única decisão.

Verificado antes de tocar em nada: as 36 previsões, a versão da regra e o
gabarito estavam **idênticos**.

    MUDAR COMO A DECISÃO SE GUARDA NÃO É MUDAR A DECISÃO.

A tentação era estreitar a impressão para olhar só às funções que julgam. Não
se fez: uma impressão que só vê o que alguém se lembrou de listar tem um ponto
cego do tamanho do que esqueceu. Ficou larga, e ao lado dela ficou o que
faltava — `PREVISOES_FINGERPRINT`, para quem investigar saber onde olhar.

    NÃO SE ESTREITA UMA GUARDA PARA ELA DEIXAR PASSAR O MEU CÓDIGO.
    ACRESCENTA-SE O QUE FALTAVA PARA A LER.

## 103.11 · O QUE FICA POR SABER

- **A aquisição de T4 pela rede continua por provar** enquanto o EUR-Lex nos
  travar. A cortesia e o recuo já lá estão; o tempo de espera não se mediu.
- **`collection_run.status` diz `concluida` quando o RAW fecha**, não quando a
  estrada acaba. Não corrompe nada; confunde quem opera. `G-RUN-02`.
- **Retenção de envelopes** por decidir. `G-ENV-02`.
- **A concorrência foi provada até 20 corridas** simultâneas sobre o mesmo
  documento, que é o pior caso para as chaves únicas. Acima disso é
  `NOT_MEASURED`.

---

# §104 · UMA GUARDA QUE CONFERE E DEPOIS CONSOME NÃO GUARDA NADA

**Missão:** `SINTONIA-SCRAP NIGHT-SHIFT-01` + `SCRAP-MORNING-01` — madrugada de
hardening e integração na Release.
**Branch:** `claude/sintonia-scrap-night-shift-01` → RC por fast-forward
**Data:** 2026-09-13

A `§103` aprendeu, do lado da Collection, que **uma máquina provada em série é
uma máquina provada em série**. Na mesma noite, do lado do SCRAP, a mesma lição
apareceu noutra forma — e a forma importa, porque a cura de lá (escrita atómica
em ficheiro) não serve aqui.

## 104.1 · O DINHEIRO

A porta paga tinha duas linhas que pareciam uma:

```python
if autorizacao.restantes <= 0: recusa
reg['GASTAS'] += 1
```

```
autorização para 1 execução   ->  2 corridas pagaram
autorização para 3 execuções  ->  5 corridas pagaram
```

E não só na primitiva. Pela **porta paga de verdade** — o coletor inteiro, com o
provider falso por baixo da guarda, dos dois tetos e do cap do fornecedor — com
16 fios sobre teto 3 **nasceram 4 POSTs**.

    UMA GUARDA QUE CONFERE E DEPOIS CONSOME
    DEIXA PASSAR QUEM CHEGAR NO MEIO.
    CONFERIR E CONSUMIR TÊM DE SER UM SÓ ACTO.

`+= 1` também não é atómico: ler, somar e escrever são três passos, e o
interpretador troca de fio entre bytecodes. A `§97` já tinha ensinado que **um
limite conferido contra um ledger que muda não foi conferido**; esta é a irmã
temporal dela — um limite conferido e consumido em dois momentos também não foi
conferido.

**E há uma parte de método que se transfere inteira.** A corrida é rara com o
intervalo de troca de fio normal, e rara não é ausente. `sys.setswitchinterval`
encurtado **não inventa** a corrida — ela existe no código ou não existe. Só a
torna visível numa medição de segundos em vez de numa de meses.

    «NÃO APARECEU» NÃO É «NÃO EXISTE».

A trava é **uma**, do módulo, e não uma por autorização: a secção crítica não faz
E/S nenhuma. E não precisa de atravessar processos — o selo é um `object()` do
processo, e uma autorização reconstruída noutro lado é recusada como fabricada.
Medido, não presumido.

    UM PROCESSO, UM REGISTO, UMA TRAVA.

## 104.2 · UMA ROTA QUE NÃO CORREU NÃO OBSERVOU NADA

Pôr cada capacidade `READY` a andar pelo caminho real — e não a ser contada —
encontrou duas a responder o impossível:

```
instagram.reel.capture   RESULT = ROUTE_NOT_ALLOWED   e 1 objeto
PROVIDER_USED = None · COST_STATE = NOT_RUN · sockets abertos = 0
```

O objeto era um esqueleto com todos os campos em `NOT_KNOWN` — e, levado pelo
dono da colheita com uma fonte no pedido, virava **uma unidade carimbada com um
`SOURCE_ID` verdadeiro**, sem um único reparo do contrato de retorno. Na forma,
uma observação perfeita de uma fonte real.

    UMA ROTA QUE NÃO CORREU NÃO OBSERVOU NADA.
    UM ESQUELETO COM SOURCE_ID É UMA OBSERVAÇÃO FABRICADA.

O esqueleto nasce de propósito lá em baixo: a cadeia de Reel distingue REUSAR de
ADQUIRIR, e o portão está onde o socket abre para não recusar reprocessamento
local. O erro estava em cima, em quem decide o que é colheita.

**E o sinal não é o estado de falha.** Uma rota que colheu dez e depois levou
`RATE_LIMITED` colheu dez de verdade. O sinal é o do dono do custo, que nasce
`NOT_RUN` e só quem corre sobrescreve.

    NOT_RUN != COST 0. UNKNOWN COST != COST 0.

## 104.3 · UM ERRO DE AMBIENTE CONHECIDO NÃO É «NÃO SEI»

Num runner sem Chrome, `instagram.profile.discovery` chegava como
`UNKNOWN_ERROR` — o balde de «ninguém sabe» — enquanto a mensagem dizia, por
extenso, «sem Chrome nesta máquina».

    UMA MENSAGEM QUE SABE E UM ESTADO QUE NÃO SABE
    VALEM MENOS QUE NENHUM DOS DOIS: QUEM LÊ POR MÁQUINA LÊ O ESTADO.

De manhã, `UNKNOWN_ERROR` sobre Instagram manda alguém depurar o Instagram —
quando o que falta é um navegador. É a irmã da `§102.1` com o eixo trocado: lá
concluiu-se sobre a classe medindo um endereço; aqui, sabendo-se a causa exacta,
publicou-se «não sei».

**Nada disto era vocabulário novo.** A taxonomia já tinha o estado e já listava
o nome nativo; a ferramenta já tinha a constante. Os dois donos concordavam e
ninguém os tinha ligado.

    FAILURE STATE VEM DO DONO, OU NÃO É FAILURE STATE.

**E consertar o trace não chega.** Isso mediu-se na integração, no dia seguinte:
o *trace* já dizia `EXECUTOR_UNAVAILABLE`, `NEEDS_HUMAN_FIX` e a frase — e o
**recibo** que atravessa a fronteira levava cinco chaves, nenhuma delas a
recuperação nem a frase.

    CONSERTAR O TRACE É CONSERTAR O TRACE. O QUE ATRAVESSA É O RECIBO.
    UM ESTADO QUE SABE, NUM RECIBO QUE NÃO O LEVA,
    VOLTA A SER «NÃO SEI» PARA QUEM LÊ.

Dois defeitos gerais caíram ao consertar este, e nenhum era do Instagram:
`setdefault` sobre uma chave escrita a `None` nunca deriva nada — **uma chave
escrita a `None` não é uma chave ausente** — e um carregador de estado que só
leva NOMES apaga a única linha que diz *qual* ferramenta faltava.

    UM NOME E UMA FRASE NÃO CABEM NO MESMO CAMPO.

## 104.4 · A MÁQUINA DE PROVAR PROVAVA MENOS DO QUE DIZIA

Três defeitos, nenhum no produto. Estão todos na parte que julga o produto — que
é a mais cara quando mente, porque ninguém a audita.

**Um comentário roubou a âncora de um mutante.** A madrugada escreveu, no mesmo
ficheiro, um comentário que CITAVA a linha que o mutante mutava. `replace(…, 1)`
trocou o comentário; o código ficou intacto; o relatório chamou-lhe sobrevivente
e acusou a bateria de um buraco que ela não tinha.

    UM COMENTÁRIO QUE CITA O CÓDIGO
    ROUBA A ÂNCORA DE QUEM MUTA O CÓDIGO.

A cura não é re-ancorar aquele mutante: é a mutação passar a **contar** as
ocorrências e recusar-se a correr quando a âncora não é única. O guarda apanhou
um segundo caso no minuto em que nasceu.

    UM MUTANTE QUE NÃO MUDA NENHUM NÚMERO NÃO SE CONSEGUE VIGIAR.
    E UM QUE MUDA O NÚMERO ERRADO É PIOR: ELE MENTE COM CONFIANÇA.

**E uma sentinela era cega por escolher o sujeito errado.** Ela comparava
`CAPABILITY_STATE_BEFORE` com `AFTER` — e o canário era a única capacidade já
declarada `PROVEN`. Sobre ela, «não promoveu» e «promoveu para PROVEN» são a
mesma linha.

    UMA SENTINELA QUE VIGIA UM CAMPO CUJO VALOR JÁ É O DA MUTAÇÃO
    NÃO VIGIA NADA.
    UMA PROVA QUE SÓ CORRE ONDE O ERRO É INVISÍVEL NÃO É UMA PROVA.

## 104.5 · UM WORKTREE DESCARTÁVEL NÃO É UM STORAGE DESCARTÁVEL

O ensaio SCRAP → Collection correu o ingresso **deles** sobre os dados
**nossos**, sem merge. Passou — e escreveu cinco observações dentro do checkout
que estava a ler.

Não fez mal: o checkout era um worktree temporário e detached, a ref nunca se
moveu, nada foi commitado. Mas isso é sorte de endereço, não propriedade da
prova.

    UMA PROVA QUE ESCREVE NA ÁRVORE QUE LÊ MEDE A ÁRVORE QUE ELA MUDOU.
    UM WORKTREE DESCARTÁVEL NÃO É UM STORAGE DESCARTÁVEL.

O código tem de vir da árvore verdadeira — é ele que está sob prova. Os **bytes**
vão para uma raiz que a prova cria e que mais ninguém conhece.

## 104.6 · PASSAR TEXTO É PASSAR ESPÉCIE, NÃO SÓ VALOR

O ensaio liga do contrato à admissão e para numa aresta só: a unidade chega
**sem texto**, e quem julga responde `NÃO SEI` — que é a resposta certa para um
item sem conteúdo.

O envelope guarda o texto em `TEXT`; quem julga lê `texto`. Nenhum dos dois mapas
o carrega. A ligação parece uma linha, e é por isso que é perigosa: escrevê-la
apaga a espécie.

```
CAPTION != TRANSCRIPT
ORIGINAL != TRANSLATED
```

Uma legenda escrita pelo autor e uma fala reconhecida por máquina chegariam ao
mesmo campo, indistinguíveis — e essa é a primeira pergunta que a inteligência
faz sobre qualquer classificação.

    PASSAR TEXTO SEM PASSAR A ESPÉCIE DELE
    É ENTREGAR UMA RESPOSTA SEM DIZER A QUE PERGUNTA ELA RESPONDE.

Ligá-lo são **duas** decisões, não uma: o campo do texto, e o campo que diz o que
ele é. A segunda precisa de vocabulário que a porta hoje não tem. Sem as duas,
`E7 = BLOCKED_BY_CONTRACT_DECISION` — e isso **não** reprova o motor a montante.

    A CADEIA LIGAR E A ADMISSÃO DIZER SIM SÃO DUAS PERGUNTAS.

## 104.7 · CONSEQUÊNCIA

```
· onde houver estado consumível, perguntar se confere e consome no MESMO acto
· o sinal de que uma rota correu é do dono do custo, não do estado de falha
· quem sabe a causa publica a causa, e o recibo leva o que o trace soube
· mutação por texto conta antes de trocar; prova escolhe sujeito onde o erro
  possa aparecer
· prova escreve em storage próprio, não na árvore que lê
· texto que atravessa fronteira viaja com a espécie, ou não viaja
```

**Medido:** 56 ataques · 0 sobreviventes · 37 mutantes · 0 sobreviventes ·
0 regressões na suíte inteira comparada por identidade ·
`REAL_PAID_RUNS = 0` · `PAID_USD = 0`.


---

# §105 · UM NÚMERO QUE ERA CONSEQUÊNCIA FOI ESCRITO COMO EXPECTATIVA

**Missão:** `C-CLOSE-POSTGRES-CI-BEFORE-LIVE-V1` — fechar o job vermelho antes
de qualquer conversa sobre LIVE.
**Branch:** `claude/close-postgres-ci-before-live-v1` → `claude/raw-observation-identity-3jbwco` por fast-forward
**Data:** 2026-09-13

O job `postgres-descartavel` estava vermelho, e não porque alguma coisa tivesse
partido. `provas/a_fase_10_entra_no_acervo.py` encena um acervo com tudo
aplicado menos a `027`, corre o aplicador canónico e pergunta o que ele fez.
Perguntava assim:

```python
_e("AS_ANTERIORES_FORAM_SALTADAS_COM_HASH_A_BATER", len(saltadas), 25)
_e("NENHUMA_FOI_PULADA", len(mencionadas), 26)
```

Chegaram a `028`, a `029` e a `030`. O cenário não mudou **nada** — continuou a
haver exactamente uma migration pendente, e continuou a ser a `027`. A prova
reprovou na aritmética.

## 105.1 · A DISTINÇÃO

```
O CENARIO E «SO A 027 ESTA PENDENTE».
NAO E «HA 26 MIGRATIONS».
```

O segundo não é o cenário: é uma **consequência** dele, medida num dia. Escrita
como expectativa, ela caduca na migration seguinte — e caducou.

Isto não é o mesmo defeito da `§46` (contagem congelada numa trava, curada por
derivação). Ali o número era um **invariante que alguém quis afrouxar**. Aqui o
número nunca foi invariante nenhum: era um efeito colateral do universo, e o
universo cresce por desenho. A cura é a mesma família, o diagnóstico não.

## 105.2 · A EMENDA QUE PARECE CONSERTO E NÃO É

O caminho mais curto para o verde era trocar `25` por `28` e `26` por `29`.

```
TROCAR O NUMERO NAO E CONSERTAR O NUMERO.
E MARCAR ENCONTRO COM O MESMO DEFEITO.
```

Marcaria encontro na `031`, e nessa altura já ninguém se lembra porque é que o
número estava lá. Um CI que fica vermelho por crescimento normal do repositório
**ensina a equipa a ignorar o CI** — e é isso que custa, muito mais do que o
job.

## 105.3 · A CURA — CONJUNTOS, E NÃO QUANTIDADES

O universo lê-se do disco a cada corrida, **pela mesma regra que o aplicador
usa** (`supabase/migrations/*.sql` menos a que só confere). O livro-razão lê-se
do banco, e não de uma lista escrita na prova. O que se compara são conjuntos
de versões:

```
MIGRATIONS_IN_SCENARIO        medido do disco
ALREADY_APPLIED_BEFORE_TEST   lido do banco, ANTES de a cadeia correr
EXPECTED_PENDING              a diferenca dos dois  ->  tem de ser {027}
ACTUALLY_SKIPPED == ALREADY_APPLIED & MIGRATIONS_IN_SCENARIO
ACTUALLY_APPLIED == EXPECTED_PENDING
ACTUALLY_SKIPPED | ACTUALLY_APPLIED == MIGRATIONS_IN_SCENARIO
```

A contagem aparece no log e **não decide nada**.

```
UMA CONTAGEM CADUCA.
UM CONJUNTO NAO SABE CONTAR, E POR ISSO TAMBEM NAO SABE CADUCAR.
```

E quando falha, diz **quais** faltam e **quais** sobram. Um `28 != 25` não diz
a ninguém o que mudou; `SOBRAM 028-030` diz.

**A única versão escrita à mão é a `027`** — e tem de ser, porque ela *é* o
assunto da prova. A regra prática: escreve-se à mão o **sujeito**, nunca o
**tamanho do universo à volta dele**.

## 105.4 · O ESPERADO DECLARA-SE ANTES DE A RESPOSTA CHEGAR

`universo_da_cadeia()` e `livro_razao(url)` correm **antes** de
`aplicar_pela_cadeia()`. Declarar depois de ver a saída seria escrever o
gabarito a partir da resposta, e a prova passaria sempre. Há uma guarda que
compara as posições das duas chamadas na AST — não é paranóia: a ordem é
invisível numa revisão de diff.

## 105.5 · SALTAR NÃO É TUDO A MESMA COISA

O aplicador canónico tem **dois** SKIP, e significam o contrário um do outro:

```
SKIP (ja no livro-razao) HASH=MATCH       o livro sabia, e o ficheiro nao mudou
SKIP (objetos ja existem; anotado ...)    o livro NAO sabia; foi o banco que disse
```

O segundo, no cenário desta prova, é um defeito: quer dizer que a fixture não
semeou o que jurou ter semeado. Contados juntos, os dois davam o mesmo número e
ninguém via. São conjuntos separados agora — mais uma aplicação de
`ERRO != RECUSADO != DESCONHECIDO`.

E uma migration que a cadeia **nunca menciona** também aparece:

```
SILENCIO NAO E PASS.
```

Uma migration que ninguém viu não é uma migration que passou.

## 105.6 · A `008` FICA DE FORA PORQUE CONFERE

Ela lê o que as outras fizeram e reclama se não bater; não é DDL normal. Esse
juízo estava escrito em três sítios — o laço que aplica, o laço que semeia o
livro, e implicitamente nos números `25` e `26`. Passou a ter um dono só,
`SO_VERIFICA`, ao lado de `EM_PROVA` e `DEPOIS_DO_ACERVO`. Mais `ONE CONCEPT →
ONE OWNER`, e a guarda cobra que o literal `"008"` apareça **uma vez** no código.

## 105.7 · COMO SE PROVA QUE UM DEFEITO DESTES MORREU

Não por argumento. Pôs-se uma `031` real no disco e correu-se a prova inteira
contra PostgreSQL 16, **sem tocar numa linha dela**:

```
MIGRATIONS_IN_SCENARIO        29 -> 30
ACTUALLY_SKIPPED              28 -> 29
A_FASE_10_ENTRA_NO_ACERVO     PASS
```

Com o código antigo, isso era vermelho. **É esse o teste de uma cura contra
caducidade: acrescentar o que faria o defeito voltar, e não mexer em nada.**

## 105.9 · UM PASSO VERMELHO ESCONDE OS PASSOS A SEGUIR

Consertada a contagem, o job andou mais quatro passos e parou noutro sítio:

```
relation "public.participacao_na_derivacao" does not exist
```

O passo `2f` NUNCA TINHA CORRIDO. Estava atrás do passo vermelho, e um passo
que não corre não é um passo que passa.

```
UM JOB VERMELHO NAO TEM UM DEFEITO.
TEM UM DEFEITO VISIVEL, E SABE-SE LA QUANTOS POR TRAS DELE.
```

Isto muda o que significa «consertei o job». A medição honesta é: o passo que
era vermelho ficou verde, e apareceu outro que ninguém tinha visto. Corrigir a
contagem não foi o fim da missão — foi o que **tornou a missão mensurável**.

E a prática que se leva daqui: ao fechar um job vermelho, correr LOCALMENTE os
passos que vinham depois do que falhava, antes de empurrar. Foi assim que o
`2g` e o `2h` — também nunca corridos — foram medidos antes de o CI os
encontrar.

## 105.10 · A MESMA DOENÇA, E A CURA JÁ ESTAVA ESCRITA

O segundo defeito era o mesmo do primeiro noutra roupa:
`provas/o_forward_conta_se.py` montava o esquema a partir de uma **lista de
migrations escrita à mão**, que parava na `026`.

E já tinha envelhecido **uma vez**: faltava a `025`, foi remendada com
`'025', '026'`, e ficou um comentário ao lado a dizer, em letra bem grande,
`UMA LISTA A MAO ENVELHECE CALADA`. Envelheceu outra vez, exactamente como o
comentário avisava.

O que torna este caso instrutivo não é o defeito — é que **a cura já existia na
casa**. `provas/a_rota_m2_atravessa.py` tinha sofrido o mesmo, fora curado com
`_cadeia_de_migrations()` + `_SO_VERIFICA`, e ganhara uma guarda própria. Só
que a guarda olhava para **um ficheiro**.

```
CURAR UM SITIO E DEIXAR A GUARDA A OLHAR SO PARA ESSE SITIO
E CURAR UM SITIO.
```

Duas consequências práticas:

1. **A cura repetida usa o mesmo nome.** Inventar um segundo vocabulário para o
   mesmo defeito cria duas coisas que alguém tem de se lembrar de procurar.
   `_SO_VERIFICA` e `_cadeia_de_migrations()` foram copiados tal e qual.
2. **A guarda passou a iterar uma lista de ficheiros**
   (`PROVAS_QUE_MONTAM_O_ESQUEMA`), verificada a morder: reposta a lista à mão,
   ela reprova nomeando o ficheiro **e** a migration em falta. Quando nascer uma
   terceira prova que aplique migrations, acrescenta-se ao tuplo — e não a um
   comentário.

E um terceiro, mais pequeno e da mesma família: `delete from derived_artifact`
estava escrito em três sítios. A `029` deu um filho ao derivado, e a mesma linha
passou a bater numa chave estrangeira **nos três ao mesmo tempo**. Virou
`limpar_derivados()`.

```
TRES COPIAS DE UMA REGRA SAO TRES SITIOS PARA ESQUECER A MESMA COISA.
```

## 105.11 · CONSEQUÊNCIA

```
· uma contagem so entra numa assercao se for o SUJEITO, e nunca se for
  o tamanho do universo a volta dele
· o universo de uma prova le-se da mesma fonte que o codigo medido usa
· declarar o esperado ANTES de correr; a ordem merece guarda propria
· dois caminhos com o mesmo aspecto no log sao dois conjuntos, nao um numero
· silencio nao e PASS: todo elemento do universo tem de ter destino dito
· provar que uma cura contra caducidade pegou = acrescentar o proximo
  elemento e nao editar nada
· ao fechar um job vermelho, correr LOCALMENTE os passos que vinham
  depois do que falhava: eles nunca correram
· cura repetida usa o nome da cura que ja existe, nunca um segundo
· a guarda de uma cura itera uma LISTA DE SITIOS, e a lista vive no teste
```

**Medido:** `postgres-descartavel` reproduzido vermelho antes de tocar em nada ·
10 ataques · 0 sobreviventes (os dois últimos são exactamente «trocar só 25 por
28» e «trocar só 26 por 29») · 14 guardas novas · regressão 2632 → 2646 testes
com conjunto de falhas **idêntico**, `NEW_FAILURES = 0` ·
`SYSTEM_MAP_CHECK = PASS` · **nenhum byte de LIVE lido ou escrito**.


---

# §106 · PEDIR NÃO É OBTER — UM PORTÃO QUE NÃO SE CONFERE É UMA CONVENÇÃO

**Missão:** `C-LIVE-PREFLIGHT-READONLY-V1` — o LIVE está em estado conhecido o
suficiente para que uma missão posterior possa pedir autorização de apply?
**Branch:** `claude/live-preflight-readonly-v1`
**Data:** 2026-09-13
**LIVE_WRITES_PERFORMED:** 0

## 106.1 · O ACHADO

O preflight abre a sessão em somente-leitura antes de perguntar o que quer que
seja. A primeira versão fê-lo assim:

```bash
PGOPTIONS='-c default_transaction_read_only=on'
```

Contra um PostgreSQL 16 descartável na bancada: `on`, e uma escrita recusada
com `cannot execute CREATE TABLE in a read-only transaction`. Perfeito.

Contra o banco vivo, medido na corrida 29:

```
READ_ONLY_SESSION=off
```

Não deu erro. Não pendurou. Não avisou. O parâmetro foi **silenciosamente
ignorado** — `PGOPTIONS` é parâmetro de **arranque** da ligação, e um pooler no
meio pode simplesmente não o encaminhar. A sessão veio de escrita: exactamente
a sessão que o pedido dizia trancar.

```
PEDIR NAO E OBTER.
UM PORTAO QUE NAO SE CONFERE E UMA CONVENCAO COM AR DE TRANCA.
```

## 106.2 · O QUE SALVOU ISTO NÃO FOI O PEDIDO

Foi a **conferência**. A secção pergunta `show transaction_read_only` e compara
com `on` **antes** de fazer a primeira pergunta ao banco; como veio `off`, ela
recusou-se a correr e imprimiu `PREFLIGHT=NOT_MEASURED`.

Se tivesse confiado no pedido, teria corrido o preflight inteiro numa ligação de
escrita a chamar-lhe somente leitura — e teria escrito no relatório que a sessão
estava trancada, com toda a convicção.

```
A TRANCA E A RESPOSTA DO SERVIDOR, NUNCA O PEDIDO DO CLIENTE.
E A CONFERENCIA VEM ANTES DA PRIMEIRA PERGUNTA, NAO DEPOIS DA ULTIMA.
```

Isto generaliza para lá de Postgres: sempre que uma garantia é *pedida* a um
sistema remoto — read-only, timeout, isolamento, quota, região — o pedido e a
garantia são coisas diferentes até alguém perguntar ao outro lado o que ficou
realmente em vigor.

## 106.3 · A CURA PORTÁTIL

`begin read only` é **SQL comum**: atravessa pooler, não depende de parâmetro de
arranque, e quem o faz cumprir continua a ser o servidor. Medido contra o
**mesmo endpoint vivo** onde o `PGOPTIONS` falhara, corrida 30:

```
READ_ONLY_SESSION=on
READ_ONLY_PROVEN=YES
```

E o que dá valor ao `on` é o `off` do lado de fora: na bancada,
`transaction_read_only` fora do `begin` vem `off`. Sem essa metade, um `on`
podia ser só o ambiente já ser assim.

```
UMA PROVA DE QUE A TRANCA PEGOU PRECISA DO ESTADO SEM A TRANCA AO LADO.
```

## 106.4 · O QUE A BANCADA NÃO PODE PROVAR

O red team local matou 14 cenários e **não apanhou este**, porque o Postgres da
bancada aceitava `PGOPTIONS` à primeira. Não havia pooler, não havia endpoint
gerido, não havia camada nenhuma no meio.

```
PROVADO CONTRA O LOCAL NAO ESTA PROVADO CONTRA O VIVO,
QUANDO O QUE SE PROVA E UMA PROPRIEDADE DO CAMINHO E NAO DO MOTOR.
```

A divisão útil: o red team mede a **lógica** (o que a prova conclui de cada
estado) e corre em fixtures; o que depende do **caminho até ao banco** só se
mede no caminho verdadeiro — e por isso a primeira coisa que a secção faz no
vivo é conferir o portão.

## 106.5 · NÃO NARRAR UMA CAUSA A PARTIR DE UM OBSERVADOR ATRASADO

A API do GitHub serviu `in_progress` durante ~20 minutos para um job que tinha
terminado aos **80 segundos**. Concluí «pendurou contra o pooler», cancelei a
corrida, e escrevi isso numa mensagem de commit — que depois teve de ser
corrigida contra o log, onde estava a verdade: o job correu até ao fim, imprimiu
`READ_ONLY_SESSION=off` e `AUDITORIA_LIVE=PASS`.

```
UM OBSERVADOR ATRASADO NAO E UM SISTEMA PARADO.
ANTES DE NOMEAR A CAUSA, LER O REGISTO DE QUEM FEZ O TRABALHO.
```

O diagnóstico errado teria sobrevivido no know-how como facto sobre poolers. O
que o desfez foi o log do job — a fonte primária —, e não mais tempo de espera.
A cura (`begin read only` + prazos) continuou certa; a **razão** é que estava
errada, e uma razão errada ensina mal a próxima pessoa.

## 106.6 · MEDIR O LIVE SEM CREDENCIAL NENHUMA

Esta sessão não tinha `SUPABASE_DB_URL` — nem no ambiente, nem em `.env`, nem em
`~/.pgpass`. A conclusão fácil era `LIVE_DB_REACHABLE = NO` e parar.

Mas a casa já tinha uma **porta somente-leitura** com o segredo do lado dela
(`auditoria-live.yml`, disparada por `push` em `provas/auditoria_live.sh`), e 28
corridas de histórico. Duas coisas se seguiram:

1. os **logs das corridas antigas** são medição real do LIVE, e lê-los não custa
   acção nenhuma — verificado antes de usar que `supabase/migrations/` não mudara
   entre aquele commit e o HEAD, portanto a comparação continuava byte-idêntica;
2. estender essa porta com perguntas novas **somente-leitura** dá medição de
   hoje, sem criar caminho de acesso novo nem segredo novo.

```
SEM CREDENCIAL NA MAO != SEM MEDICAO POSSIVEL.
PROCURAR A PORTA QUE JA EXISTE ANTES DE DECLARAR QUE NAO HA PORTA.
```

## 106.7 · REGISTADA NÃO É EXISTENTE

O preflight pergunta pela `029` e pela `030` **duas vezes**, de propósito:

```
MIGRATION_029_IN_LEDGER = NO    PARTICIPACAO_NA_DERIVACAO_EXISTS = NO
MIGRATION_030_IN_LEDGER = NO    DOCUMENTO_ESTRUTURADO_EXISTS     = NO
```

Porque a diferença entre as duas respostas **é** o achado:

```
REGISTADA SEM TABELA  = o livro mente sobre o que correu
TABELA SEM REGISTO    = o aplicador vai tropecar nela
```

Aqui coincidiram, e isso é uma boa notícia medida — não uma pergunta que se
poupou. Perguntar só uma delas daria a mesma folha num caso e uma folha errada
no outro.

## 106.8 · BACKUP EXISTE ≠ RESTORE PROVADO

```
LIVE_BACKUP_STATUS    NOT_MEASURED    nao ha token de gestao nesta sessao
LIVE_RESTORE_STATUS   NOT_PROVEN      nao existe registo de restore ensaiado
```

Os dois rótulos são diferentes e a diferença é deliberada. `NOT_MEASURED` é «não
olhei, e não digo». `NOT_PROVEN` é «olhei, e a prova não existe» — prova é
artefacto positivo, e procurar por ele em `docs/`, `.github/`, `motor/` e
`provas/` e não o encontrar **é** uma medição.

```
«O SUPABASE TEM BACKUP» NAO E UMA MEDICAO. E UMA EXPECTATIVA SOBRE TERCEIROS.
```

E é isto, e não o banco, que mantém `LIVE_READY_FOR_APPLY = NO`: do lado do
schema não há nada a impedir o apply — livro íntegro, zero drift, zero órfãs,
três pendentes identificadas. O que falta é a **capacidade de voltar atrás**.

## 106.9 · CONSEQUÊNCIA

```
· garantia pedida a sistema remoto confere-se com a resposta dele,
  antes da primeira pergunta a serio
· a prova de que a tranca pegou precisa do estado SEM a tranca ao lado
· o que depende do caminho ate ao banco nao se prova na bancada
· antes de nomear a causa de um sistema «parado», ler o log de quem
  fez o trabalho; observador atrasado nao e sistema parado
· sem credencial na mao, procurar a porta read-only que a casa ja tem
· registada e existente sao duas perguntas, sempre as duas
· NOT_MEASURED e NOT_PROVEN nao sao sinonimos
· um retrato do LIVE diz na primeira linha que e um retrato
```

**Medido:** `READ_ONLY_PROVEN = YES` · ledger 26 versões, 0 duplicadas, 0
resultados inválidos, 0 SHA em falta, 0 drift, 0 extras · `PENDING = {028,029,030}`
· travas da Collection todas validadas · 14 ataques, 0 sobreviventes ·
regressão 2647 testes com conjunto idêntico ao baseline ·
**`LIVE_WRITES_PERFORMED = 0`**.


---

# §107 · UM TESTE QUE SÓ FALA PELO SÍMBOLO NÃO VÊ O CONTRATO MUDAR

**Missão:** `C-INTEGRATE-E7-INTO-CURRENT-COLLECTION-V2` — aterrar o contrato do
texto na linha funcional, que andou cinco commits desde a base dele.
**Branch:** `claude/integrate-e7-current-collection-v2` → linha funcional por fast-forward
**Data:** 2026-09-13

A `COL-E7-01` fechou o contrato do texto com 65 casos, e fechou-o bem. O red
team **da integração** — que ataca a junção, e não cada lado — pôs dois
mutantes que os 65 não viram:

```
CAMPO_DAS_UNIDADES = 'TEXTOS'          ->  65 testes verdes
TEXTO_DESCONHECIDO = 'TRANSCRIPT'      ->  65 testes verdes
```

O campo do envelope mudou de nome, e o desconhecido passou a dizer — no fio —
que alguém o tinha transcrito. Nenhum teste reclamou.

## 107.1 · POR QUÊ

Porque a suíte inteira se refere ao contrato pelo **símbolo**:

```python
pv.CAMPO_DAS_UNIDADES        e nunca   'TEXT_UNITS'
pv.TEXTO_DESCONHECIDO        e nunca   'UNKNOWN'
```

Isso é boa prática para código — e é exactamente o que cega o teste. Mudar a
constante move os dois lados da igualdade ao mesmo tempo, e a asserção continua
verdadeira sobre um mundo diferente.

```
UM TESTE QUE SO FALA PELO SIMBOLO MEDE A COERENCIA INTERNA,
E NAO O CONTRATO COM QUEM ESTA DO OUTRO LADO DO FIO.
```

## 107.2 · E DO OUTRO LADO DO FIO HÁ GENTE

`TEXT_UNITS` não é detalhe de implementação: é o nome que **viaja no envelope**,
fica escrito em disco, e é o que o SCRAP vai produzir na missão seguinte.
Renomeá-lo em silêncio não parte um teste — parte a leitura de tudo o que já foi
colhido, e parte uma ponte que ainda não foi construída.

```
UM VALOR QUE ATRAVESSA UMA FRONTEIRA E UM CONTRATO,
E UM CONTRATO PRENDE-SE PELO VALOR — UMA VEZ, NUM SITIO SO.
```

Onde? Numa guarda dedicada, separada da suíte de comportamento: ali escreve-se o
literal **de propósito**, e é o único sítio do repositório onde isso é correcto.

E a trava que mata a família toda, e não só o caso que apareceu: **a ausência de
espécie não pode coincidir com nenhuma espécie de verdade**, seja qual for o
valor que lhe derem.

## 107.3 · UM CONFLITO EM FICHEIRO GERADO NÃO SE RESOLVE ESCOLHENDO UM LADO

Das duas linhas juntas nesta missão, **nenhum ficheiro de código-fonte foi
tocado pelos dois lados**. Os únicos oito conflitos foram os JSON gerados do
System Map — cada lado tinha regenerado o mapa a partir da **sua** árvore.

`ours` guardaria o mapa de uma árvore que já não existe. `theirs`, o de outra
que também não. As duas opções são medições de passados diferentes.

```
UM MAPA E MEDIDA, E NAO OPINIAO.
NAO SE ESCOLHE ENTRE DUAS MEDIDAS DE ARVORES QUE JA NAO EXISTEM:
MEDE-SE A QUE EXISTE.
```

Resolveu-se correndo a cadeia canónica sobre a árvore **já junta** — e isso
prova-se, não se afirma: os oito ficheiros regenerados **diferem dos dois
lados**. Se algum coincidisse, seria sinal de que alguém tinha escolhido.

Generaliza: num merge, ficheiro derivado não tem lado. Tem **gerador**.

## 107.4 · O A/B DE UM JULGAMENTO É CONTRA O HEAD DE HOJE

A `COL-E7-01` já provara 174 vereditos iguais — contra a base de onde ela saiu.
Isso não serve para a integração: a pergunta mudou de «o E7 muda o julgamento?»
para «o E7 **aqui**, sobre cinco commits que ele nunca viu, muda o julgamento?».

E ao construí-lo, três coisas quase o invalidaram:

1. **O carimbo de tempo não é um julgamento.** A primeira comparação deu 129 de
   129 «diferentes» por causa de `quando=`. Neutraliza-se esse campo **pelo
   nome** — apagar tudo o que varia até o diff se calar seria comparar o
   silêncio.
2. **Juntar pela chave errada não dá zero linhas: dá linhas vazias.** Os 36
   itens do gabarito não casam por `ITEM_ID` com `ARTIFACT_ID` — casam por
   `DOC_SHA256`. Com a chave errada: ficha vazia, item sem tipo, e a porta a
   abster-se em 100% dos casos. Um A/B assim passa sempre, e não por bom motivo.
3. **Um A/B onde nada discrimina não prova que nada mudou.** Enquanto todos os
   vereditos saíam `NAO_SEI`, a comparação passaria na mesma se a regra tivesse
   desaparecido. Só depois de o arnês da casa alcançar vereditos **temáticos**
   (`SIM`/`NÃO`) é que o zero passou a significar alguma coisa.

## 107.5 · CONSEQUÊNCIA

```
· contrato que atravessa fronteira prende-se pelo VALOR, em guarda propria
· a ausencia de especie nao pode coincidir com especie nenhuma de verdade
· ficheiro gerado nao tem lado num merge: tem gerador — e prova-se que o
  resultado difere dos DOIS lados
· A/B de julgamento e contra o HEAD de hoje, nao contra a base do ramo
· neutralizar num diff so o que nao e a pergunta, pelo NOME, e so isso
· antes de confiar num A/B, perguntar se ele CHEGA a discriminar
· (ja registado antes, e repetido aqui) red team que muta e restaura no
  mesmo segundo envenena o `.pyc`: a arvore fica certa e o comportamento
  errado, e TUDO o que se medir a seguir mede a bancada. Custou uma
  regressao inteira com 8 falhas que nao existiam. A lei ja estava
  escrita; o arnes novo e que nasceu sem ela.
```

**Medido:** `TEXT_CONTRACT_OWNER_COUNT = 1` · E1–E7 PASS em 5 casos ·
`TEXT_KIND_LOSS = TEXT_RELATION_LOSS = LANGUAGE_LOSS = 0` ·
`JUDGMENT_DIFF_COUNT = 0` em dois arneses · regressão 2647 → 2720 com conjunto
de falhas idêntico, `NEW_FAILURES = 0`, `DISAPPEARED_TESTS = 0` ·
`POSTGRES_DISPOSABLE = PASS` · 19 ataques e 6 mutantes, **0 sobreviventes** ·
`SCRAP_TOUCHED = NO` · `LIVE_READS = LIVE_WRITES = 0`.

---

# §108 · A ETAPA QUE NÃO SE APLICA, E A FALHA QUE NÃO ACONTECEU

**Missão:** `C-INTEGRATE-SCRAP-INTO-CURRENT-COLLECTION-V1` — fechamento final:
as duas dúvidas que ainda impediam o SCRAP de entrar na Collection.
**Branch:** `claude/integrate-scrap-current-collection-v1`
**Data:** 2026-09-13

Duas perguntas ficaram de pé depois de a estrada estar provada. A primeira era
um `FAIL` que ninguém sabia se era defeito. A segunda era uma prova que media
uma coisa e dizia outra. As duas ensinaram o mesmo: **antes de consertar,
classificar** — e depois **exigir ver o que se diz ter visto**.

## 108.1 · UMA ETAPA NÃO APLICÁVEL NÃO É PASS, E MUITO MENOS FAIL

A etapa `DERIVED` saía `FAIL` com `EXTRACTION_ERROR` em **toda** corrida do
SCRAP. A tentação era caçar o erro. A pergunta certa era anterior:

```
DERIVED PRECISA DE EXISTIR PARA ESTE MATERIAL?
```

A resposta estava escrita há muito, em três sítios que ninguém tinha juntado:

* `derived_artifact.kind` é uma lista **fechada** — `TEXT_EXTRACTION`, `OCR`,
  `TRANSCRIPTION`, `TRANSLATION`, `THUMBNAIL`, `FRAME`, `TABLE_EXTRACTION` — e
  toda ela é transformação de um byte-stream **noutro**;
* `COL-LAW-006` manda **ordem** (*preserva o original, depois deriva*), e não
  existência;
* o contrato do texto entrega a espécie **na porta**: o texto de uma observação
  social chega declarado, não extraído.

Uma observação social é um JSON cujo texto já vem dentro. Não há o que derivar.

```
DERIVED_APPLICABILITY = NOT_APPLICABLE
```

E o estado para dizer isso **já existia**, com a definição exacta, em
`leis/telemetria.py`: `NOT_APPLICABLE` — «não existe nesta rota, com razão
escrita» — e `ETAPA_ACONTECEU = ('PASS','PARTIAL')` já o excluía de contar como
trabalho feito. Não se inventou vocabulário nenhum.

```
NOT_APPLICABLE != FAIL      a etapa nao se partiu
NOT_APPLICABLE != PASS      e tambem nao aconteceu
NOT_APPLICABLE != SILENCIO  a passagem fica ESCRITA no rastro
```

A terceira é a que se perde mais fácil. Bastava não chamar o runner e a corrida
saía sem linha `DERIVED` nenhuma — que se lê, três meses depois, como «ninguém
sabe se aquela etapa correu». E sabia-se.

```
UMA ETAPA QUE NAO SE APLICA NAO E UMA ETAPA SEM RESPOSTA.
```

## 108.2 · UMA CAPACIDADE DECLARADA QUE NINGUÉM LÊ NÃO GUARDA NADA

A causa do `FAIL` não era o extrator. Era a pergunta que a porta fazia:

```python
local = armazem.caminho_local(caminho)
if not local: ...        # «os bytes estao alcancaveis?»
unidades.append({"RAW_ASSET_ID": ..., "PDF": local})
```

Uma pergunta só — e a chave da unidade chama-se literalmente `"PDF"`.

```
ALCANCAR OS BYTES NAO E SABER O QUE ELES SAO.
UMA FERRAMENTA QUE RECEBE O QUE NAO SABE ABRIR NAO FALHOU:
FOI CHAMADA PARA O TRABALHO ERRADO.
```

E o mais instrutivo: o executor **já declarava** o que sabe abrir —
`CAPACIDADE["SUPPORTS"] = ["PDF_RAW"]` — desde o primeiro dia. Medido: a string
`SUPPORTS` aparecia na linha que a escreve **e em mais lado nenhum** do código
de produção.

```
UMA CAPACIDADE DECLARADA QUE NINGUEM LE NAO GUARDA NADA.
```

É a irmã da lei que esta casa já tinha escrito duas vezes — *um parâmetro
opcional que ninguém consegue passar não é opcional: é inexistente*. Aqui não
era um parâmetro: era uma declaração de capacidade, e o efeito foi o mesmo.

O conserto foi ligar a declaração a quem decide, e **a regra tem três ramos**:

```
especie DECLARADA e suportada      -> deriva
especie DECLARADA e nao suportada  -> nao deriva, e diz-se porque
especie NAO DECLARADA              -> deriva, como sempre derivou
```

O terceiro não é zelo. Sem ele, bastaria um writer deixar de escrever a coluna
para metade do acervo parar de derivar **em silêncio**, e nada ficaria vermelho.

```
AUSENCIA NAO E RECUSA. «NAO SEI» NUNCA AUTORIZA A CONCLUIR «NAO SERVE».
```

## 108.3 · DUAS CORRIDAS NOVAS NÃO SÃO UMA CORRIDA REPETIDA

Havia uma prova de «repetição»: corria a mesma fonte duas vezes e media o que
ficava. Ela é verdadeira e está certa — só não prova o que o nome sugere.

```
NEW RUN + NEW RUN          e idempotencia ENTRE corridas
UMA CORRIDA FALHA -> RETRY e recuperacao DENTRO de uma
```

São duas perguntas com donos diferentes, e só a segunda responde «o que
acontece quando uma corrida falha». Medido, o contrato desta casa responde as
duas em sítios distintos: `orquestrador.correr()` **não tem porta de retoma** —
cada chamada cunha `RUN_ID` novo — e o retry real vive **por etapa**, dentro da
corrida, com `rastro.proxima_tentativa` e o contador `raw_asset.attempts`.

```
1a tentativa   RUN_STATE=PARTIAL  · RAW=0 · etapa RAW/0 = FAIL
retry          RUN_STATE=COMPLETE · RAW=2 · etapa RAW/1 = PASS
```

O mesmo `RUN_ID`, zero duplicação, linhagem fechada — e **a tentativa 0 fica**.
Apagar o que falhou apagaria a evidência daquilo que se está a consertar.

## 108.4 · UMA FALHA QUE NÃO ACONTECEU PASSA EM QUALQUER PROVA QUE NÃO A EXIJA

Para medir o retry era preciso uma falha controlada **depois** de a corrida já
estar persistida. A pedra caiu no sítio errado **três vezes**:

| tentativa | porque falhou |
|---|---|
| endereço calculado com `RUN_ID` inventado | o sha do bruto **embute** o `RUN_ID` — o endereço só existe depois de a corrida ter nome |
| `chmod 0o555` no depósito | a prova corre como `root`, e o root ignora bits de permissão |
| `data/raw/observacoes/` | o depósito real é `IT/<fonte>/OBSERVATION/` |

Nas três, a colheita passou inteira e a corrida saiu `COMPLETE`. Uma prova
escrita só com «o retry recuperou?» teria dito **retry provado** tendo medido
uma corrida que nunca falhou.

```
UMA FALHA QUE NAO ACONTECEU PASSA EM QUALQUER PROVA
QUE NAO EXIJA VER A FALHA.
```

O que apanhou os três não foi releitura. Foram as asserções do passo 1 — *um
post preservado, a corrida NÃO cumprida* — que obrigam a prova a **ver o
estranho** antes de medir o conserto.

```
UMA TRANCA QUE O UTILIZADOR DESTA MAQUINA IGNORA NAO E UMA TRANCA.
O SITIO ONDE EU ACHO QUE OS BYTES FICAM NAO E O SITIO ONDE ELES FICAM.
```

## 108.5 · A CONTRAPROVA É QUE ENCONTRA O ATAQUE QUE MORREU NA PORTA ERRADA

Na prova das travas do esquema, seis ataques deram `ok` sem nunca terem chegado
à lei que visavam: morreram todos em `NOT NULL: captured_at`, uma coluna que o
ataque esquecera de preencher. A recusa era verdadeira e o veredito era falso.

```
UMA RECUSA PELA LEI ERRADA NAO PROVA A LEI CERTA.
«O BANCO DISSE QUE NAO» NAO E UMA RESPOSTA: E METADE DELA.
```

Quem apanhou isso foi a **contraprova** — a mesma escrita **sem** a mutação, que
tinha de passar e não passava. Sem ela, o ficheiro reportaria oito travas a
morder tendo medido uma.

```
UMA TRAVA QUE RECUSA TUDO PASSA NUM TESTE QUE SO VERIFICA RECUSAS.
```

Daí a forma que ficou: cada ataque **declara a lei em que tem de morrer**, e
morrer noutra reprova.

## 108.6 · O QUE FICA

```
· antes de consertar um estado, perguntar se ele devia existir
· o estado que falta costuma ja estar no vocabulario, com dono
· uma capacidade declarada precisa de um LEITOR, ou nao existe
· ausencia declarada != recusa, e o ramo do meio e o que evita
  a coleta encolher em silencio
· retry e repeticao sao perguntas diferentes, com donos diferentes
· uma prova de recuperacao tem de EXIGIR VER a falha
· todo ataque precisa da contraprova ao lado
```

E a que vale para lá desta missão:

```
MEDIR ANTES DE CONSERTAR NAO E CAUTELA: E O QUE SEPARA
UM DEFEITO DE UMA ETAPA QUE NUNCA DEVIA TER SIDO CHAMADA.
```

---

# §109 · O VALOR QUE EXISTIA EM MÃOS E NÃO ATRAVESSAVA A FRONTEIRA

**Missão:** `C-SCRAP-READY-RAW-LINEAGE-V1` — fechar a única ponte que faltava
na rota social: do `READY` de volta ao `RAW` e ao byte.
**Branch:** `claude/scrap-ready-raw-lineage-v1-ywwn15`
**Data:** 2026-09-13

A rota documental já fechava `READY → RAW → STORAGE`. A social não. A tentação
era procurar uma maneira de **reencontrar** o bruto depois — por `sha256`, por
`storage_path`, pela posição na lista. Nenhuma delas é linhagem. O que a
medição mostrou foi outra coisa, e mais barata:

```
O ID NUNCA FALTOU. ELE EXISTIA, DENTRO DO DONO, E ERA DEITADO FORA.
```

## 109.1 · MEDIR O BURACO ANTES DE LHE TOCAR

A rota SCRAP inteira, contra PostgreSQL 16 descartável, no HEAD de antes:

```
SCRAP_RAW_OBSERVATION_CREATED   = YES
SCRAP_RAW_OBSERVATION_ID        = 1          ← o banco cunhou-o
SCRAP_READY_CREATED             = YES
SCRAP_READY_RAW_OBSERVATION_ID  = 'NAO SEI'  ← e o item não o levava
```

Dois números na mesma corrida, e a distância entre eles é a missão inteira.
Sem esta medida, qualquer conserto seria plausível — e um conserto plausível
sobre um defeito não reproduzido é uma alteração à espera de justificação.

```
NÃO CORRIGIR DEFEITO QUE NÃO SE VIU ACONTECER.
```

## 109.2 · A PERGUNTA CERTA NÃO É «COMO ENCONTRO», É «ONDE É QUE SE PERDE»

A pergunta errada — *como encontro depois o RAW correspondente?* — só tem
respostas heurísticas, e todas elas trocam identidade por semelhança.

A pergunta certa é temporal:

```
EM QUE FRONTEIRA O SISTEMA JÁ SABE QUAL raw_asset.id PERTENCE
ÀQUELE ITEM, E DEIXA DE O CARREGAR?
```

Seguindo a informação em execução, a resposta é um sítio só, e está dentro do
dono do RAW: `guarda/preservar_coleta.py::conferir_o_que_ficou_escrito()`. Ali,
por cada observação **planeada** — que é o artefato de quem chamou — lê-se de
volta a **linha escrita**, pela chave de identidade dela, e essa linha traz o
`id`. Os dois estão em mão ao mesmo tempo, uma única vez em toda a estrada.

E o par era descartado: guardava-se só o `storage_path`.

```
O QUE O DONO SABE E NÃO DEVOLVE, PARA QUEM ESTÁ DO OUTRO LADO
NUNCA ACONTECEU.
```

É a mesma família de `CONTAR UMA COISA NÃO É GUARDÁ-LA` (§76): a informação
existe no runtime, e não existe no sistema, porque nada a transporta.

```
RAW_OBSERVATION_ID PRECISA DE NASCER DO RETORNO DE preservar(),
E NUNCA DE CORRELAÇÃO POSTERIOR.
```

## 109.3 · UMA ASSOCIAÇÃO POR POSIÇÃO NÃO É LINHAGEM SEM CONTRATO DE CARDINALIDADE

A maneira cómoda de atar item a observação seria pelo índice: `itens[i]` com
`RAW_OBSERVATIONS[i]`. Ela é falsa em três sítios ao mesmo tempo, e os três
foram medidos numa colheita hostil de cinco itens sociais:

```
entrada                       5
recusado NA PORTA             1   (unidade de texto malformada)
chega à porta                 4
recusado POR preservar()      1   (sem SOURCE_ID real)
observações confirmadas       3
READY pousados                4   (um deles honestamente sem observação)
```

Quatro contagens diferentes na mesma passagem. E ainda há uma quarta razão,
que é a mais silenciosa das quatro:

```
objetos_da_corrida()  →  «order by storage_path»
storage_path          →  começa pelo sha do conteúdo

A LISTA QUE VOLTA DO BANCO SAI POR ORDEM DE HASH,
E NÃO POR ORDEM DE ENTRADA.
```

Medido: a entrada `[post-1, post-3, post-5]` voltou como `[3, 2, 4]`. Quem
ligasse por índice daria a cada item a observação de outro — e com cara de
certo, que é o pior modo de estar errado.

```
POSIÇÃO NÃO É LIGAÇÃO.
UMA ASSOCIAÇÃO POR POSIÇÃO ENTRE ITENS E OBSERVAÇÕES NÃO É LINHAGEM
SEM CONTRATO DE CARDINALIDADE — E O CONTRATO TEM DE SER MEDIDO,
NÃO PRESUMIDO.
```

O contrato que ficou escrito, e provado:

```
1 observação → N alças   legítimo, e só quando `planear()` as colapsou por
                         terem a MESMA identidade de observação: são a mesma
                         observação vista N vezes, e todas têm direito ao
                         mesmo id
1 alça → 2 observações   impossível, e LEVANTA. Escolher uma daria ao item o
                         id de outra observação com cara de linhagem provada
alça sem observação      ausência, e fica ausência: o READY diz `NAO SEI`
```

## 109.4 · UMA ALÇA É PARA AMARRAR, NÃO PARA IDENTIFICAR

O transporte precisava de um fio entre o item que entra e a observação que o
banco confirma. Três candidatos foram recusados **por medição**, e não por
gosto:

```
ARTIFACT_ID    nasce do sha256 — dois itens com os mesmos bytes partilham-no,
               e a ligação juntaria duas observações numa
SHA256         identidade dos BYTES, e dois endereços partilham o mesmo sha
storage_path   endereço físico, e endereço muda sem o facto mudar
```

O que entrou foi uma **alça de passagem**: um valor novo por item, vivo só
durante a chamada, que viaja no artefato, dobra-se com a observação planeada e
volta colada à linha confirmada. Ela não nomeia nada, não é escrita em coluna
nenhuma, não entra em `insert` nenhum, e morre no fim da função.

```
UMA ALÇA É PARA AMARRAR, NÃO PARA IDENTIFICAR.
A IDENTIDADE CANÓNICA CONTINUA A SER raw_asset.id, E MAIS NADA.
```

E o que **não** se fez, porque era a saída fácil e teria criado um segundo
dono do parentesco: nenhuma tabela nova, nenhum JSON paralelo de linhagem,
nenhum mapa `sha → raw`, nenhum índice auxiliar permanente.

```
A COLLECTION JÁ TEM O DONO DO RAW.
TRANSPORTA-SE A LIGAÇÃO; NÃO SE DUPLICA.
```

## 109.5 · UM PORTÃO QUE VALIDA A LEI ANTERIOR GUARDA O LADO ERRADO DA PORTA

`provas/o_scrap_chega_ao_acervo.py` exigia `len(item) == 11` no READY. A lei
tinha ido para 12 em `C-READY-LINEAGE-BEFORE-SCALE-V1`, quando
`RAW_OBSERVATION_ID` entrou no contrato. Ou seja: o portão exigia que o campo
da linhagem **não** estivesse lá.

```
UM PORTÃO QUE VALIDA A LEI ANTERIOR NÃO É UM PORTÃO A DORMIR:
É UM PORTÃO A GUARDAR O LADO ERRADO DA PORTA.
```

O conserto não foi trocar `11` por `12` — isso reabre o mesmo buraco na
próxima lei. O número passou a vir do **dono do contrato**
(`admissao.pronto_para_inteligencia()`), perguntado em execução.

```
DOIS SÍTIOS A DECLARAR O MESMO NÚMERO DIVERGEM NO DIA EM QUE UM MUDAR.
```

E foi preciso um segundo caso ao lado, porque doze campos não provam linhagem:

```
DOZE CAMPOS COM A LINHAGEM VAZIA SÃO DOZE CAMPOS E NENHUMA VOLTA.
```

## 109.6 · UM PORTÃO QUE NÃO CHEGA A CORRER NÃO É UM PORTÃO A FALHAR

Achado adjacente, e medido a caminho: **quatro** provas do workflow
`banco-descartavel` morriam em `relation "public.storage_object" does not
exist`. O passo do CI faz `drop database` + `create database` e nenhuma delas
aplicava a cadeia canónica — ao contrário de todas as suas irmãs. A mensagem
que saía era *«a corrida nao cunhou RUN_ID»*, que manda procurar o defeito no
orquestrador, onde ele não estava.

```
UM PORTÃO QUE NÃO CHEGA A CORRER NÃO É UM PORTÃO A FALHAR:
É UM PORTÃO QUE NÃO EXISTE, COM CARA DE VERMELHO.
```

A cadeia passou a ser aplicada por **um** dono
(`o_scrap_chega_ao_acervo.garantir_o_esquema`), e só quando o banco ainda não a
tem — a cadeia não é idempotente, e a pergunta é feita ao banco e não a uma
variável de ambiente que alguém se lembre de pôr.

## 109.7 · CORREÇÃO DE ESTADO — READY TEM DOZE CAMPOS

Afirmações deste ficheiro que ficaram para trás e que um leitor de hoje leria
como estado atual:

```
«A função atual admissao.pronto_para_inteligencia() devolve contrato de
 11 campos»                                              → SUPERADA
«Contrato READY tem 11 campos.»                          → SUPERADA
```

O estado medido no HEAD funcional, e conferido no que aterrou na sala:

```
READY_FIELDS = 12

ESTADO · ITEM_ID · RAW_OBSERVATION_ID · UNIVERSO · TEXTO · SOURCE_ID ·
SOURCE_LOCATION · FACT_LOCATION · FACT_TIME · CAPTURED_AT · CORRIDA ·
ADMITIDO_POR
```

As menções aos «11 campos» nas secções históricas (§37, §74) ficam como
estavam: elas descrevem o que era verdade na data delas, e reescrevê-las
apagaria a data. **O que se corrige é a afirmação de estado, não o registo do
passado.**

## 109.8 · O QUE FICA

```
· medir o buraco ANTES de lhe tocar, e reproduzi-lo no HEAD de hoje
· a pergunta nao e «como encontro depois», e «onde e que se perde»
· o valor que falta costuma ja estar em maos, dentro do dono
· posicao nao e ligacao — e a lista que volta do banco nao vem
  na ordem em que foi
· uma alca efemera transporta; ela nunca vira identidade externa
· cardinalidade declarada e contrato; cardinalidade presumida e defeito
· o numero de um contrato pergunta-se ao dono dele, nunca se escreve
  ao lado
· um portao que nao chega a correr nao e um portao
```

E a que vale para lá desta missão:

```
UMA LINHAGEM NÃO SE DESCOBRE: ELA TRANSPORTA-SE.
QUEM A PROCURA DEPOIS ENCONTRA SEMELHANÇA, E SEMELHANÇA NÃO É IDENTIDADE.
```

---

# §110 · PROVA DENTRO DO PROCESSO NÃO É DURABILIDADE OPERACIONAL

**Missão:** `C-SALA-PERSISTENTE-E-PREFLIGHT-REAL-V1`, a seguir ao bloqueio
medido em `C-ITALIA-FIRST-REAL-COLLECTION-CANARY-V1`.

## 110.1 · O QUE MUDOU

A Sala de Espera deixou de viver num ficheiro do workspace do runner e passou a
viver numa tabela — `public.sala_de_espera`, migration `031` — **atrás do mesmo
dono**, `admissao/sala_de_espera.py`. E ganhou o que um ficheiro não tinha:
uma fila com transição auditável, `WAITING → CONSUMED`, sem apagar a linha.

## 110.2 · POR QUÊ

Porque a primeira tentativa de coleta real italiana parou antes de adquirir um
único byte, e parou com razão. A pergunta que nunca tinha sido feita era esta:

> quando o runner acabar, onde é que o READY fica?

A `ADR-SALA-DE-ESPERA-V1` estava certa no que decidiu — o **meio** — e nunca
respondeu à **sobrevivência**. Não é contradição dela: é uma pergunta que ela
não fez, porque naquele momento ninguém tinha tentado coletar a sério.

E a razão de fundo é que **toda** a prova da Sala, até aqui, corria dentro de um
processo: escrever e reler na mesma execução prova a escrita atómica, e não
prova durabilidade nenhuma.

```
MODULE EXISTS != FILE WRITTEN ON RUNNER != PERSISTED AFTER RUN.
PROVA DENTRO DO PROCESSO != DURABILIDADE OPERACIONAL.
```

É a mesma família de `MODULE EXISTS != EDGE EXISTS != FLOW EXISTS`, aplicada ao
**tempo** em vez de ao grafo:

```
FLOW EXISTS != FLOW SURVIVES.
```

## 110.3 · PROVA

```
git log --all -- 'data/samples/PRONTO-PARA-INTELIGENCIA'      ->  vazio
.github/workflows/sintonia-scrap.yml                          ->  so INSTAGRAM|YOUTUBE|SCRAP, e RECUSA o resto
.github/workflows/scrap-social.yml                            ->  tres ficheiros nomeados de SOCIAL-IT
grep -rn upload-artifact .github/workflows/                   ->  nenhum cobre a Sala
ADR-SALA-DE-ESPERA-V1 §1                                      ->  sem tabela, sem migration, sem PostgreSQL
```

Nunca, em ramo nenhum, um ficheiro da Sala foi versionado. A pasta nem existe na
árvore.

Do lado do conserto, contra PostgreSQL 16 descartável: 67 casos e 30 ataques de
red team com zero sobreviventes (`provas/a_sala_sobrevive_ao_processo.py`), e 17
mutantes com 17 mortos (`provas/mutacao_da_sala_duravel.py`). A durabilidade é
medida **matando o processo de verdade** e só depois perguntando ao banco.

## 110.4 · CONSEQUÊNCIA

```
WAITING_ROOM_DURABILITY_OWNER   PostgreSQL, atras de admissao/sala_de_espera.py
WAITING_ROOM_V1_BACKEND         FILESYSTEM, preservado e declarado NAO CANONICO
```

E a regra que fica, maior do que a Sala: **uma prova que não sobrevive ao
processo que a produziu não prova persistência.** Sempre que uma peça desta casa
disser «guardado», a pergunta seguinte é «guardado onde, e quem o vai lá buscar
amanhã?». Se a resposta for um caminho no disco do runner, não está guardado.

---

## 110.5 · O SEGUNDO ACHADO — UM PREFLIGHT QUE SÓ CORRE DEPOIS DE COMEÇAR

**O QUE MUDOU.** `superficie/rede.py` — o portão que desde o primeiro dia
responde «a coleta é executável neste ambiente?» — passou a responder também
`EGRESS_COUNTRY_CODE`, e o workflow canónico chama-o **antes** do passo que
adquire.

**POR QUÊ.** O único medidor de egresso desta casa vivia dentro de
`coleta/instagram_janela.py`, ou seja **dentro de uma rota de aquisição**. Exigir
`IT` antes de adquirir era, por construção, impossível: para saber por onde se
saía era preciso já estar a sair.

```
UM PREFLIGHT QUE SÓ CORRE DEPOIS DE COMEÇAR NÃO É UM PREFLIGHT.
```

**PROVA.** 34 casos, 10 ataques, zero sobreviventes, todos determinísticos — o
corpo do checker é injetado, e nenhum caso liga VPN nenhuma. `UNKNOWN` bloqueia
tal como `FR` ou `US`.

```
UNKNOWN != IT.
```

**CONSEQUÊNCIA.** O egresso é propriedade do **ambiente de execução**, e nunca da
fonte. E continua a não dizer nada sobre o dado:

```
VPN_LOCATION != SOURCE_LOCATION
VPN_LOCATION != FACT_LOCATION
```

---

## 110.6 · TRÊS CICATRIZES DESTA MISSÃO, E TODAS APARECERAM A MEDIR

**(1) `None` a querer dizer duas coisas.** O portão de egresso usava `bruto=None`
para «não me deram corpo, vai medir» — e `None` é também o que o checker devolve
quando não respondeu. A prova do timeout **foi à rede a sério** e voltou com um
país verdadeiro: um caso de red team passou por acidente.

```
DOIS SIGNIFICADOS NO MESMO VALOR É COMO SE LÊ O ERRADO.
```

**(2) O portão aprovava um ambiente e a aquisição corria noutro.** A variável que
escolhe o backend da Sala estava declarada só dentro do passo do preflight. Ele
passava — e o passo seguinte, o que adquire, corria sem ela.

```
UM PORTÃO QUE MEDE UM AMBIENTE E DEIXA PASSAR PARA OUTRO NÃO MEDIU NADA.
```

**(3) A prova sujava a árvore que media.** A bateria de mutação corre numa cópia
com `data/` ligado por symlink à árvore real. O mutante que faz a Sala cair para
ficheiro escreveu, por esse symlink, um ficheiro dentro do repositório de
verdade — e ele chegou a aparecer no `git add`.

```
UMA PROVA QUE SUJA A ÁRVORE QUE MEDE DEIXOU DE SÓ MEDIR.
```

---

## 110.7 · E DUAS LIÇÕES SOBRE COMO SE MEDE

**O mutante que não muda comportamento mede o texto, não a lei.** A primeira
ronda de mutação teve dois sobreviventes, e os dois eram mutantes maus: um
trocava uma condição por outra que **também** falhava fechada; o outro alargava
uma chave primária de forma que não mudava a unicidade. Um sobrevivente pode ser
uma lei sem guarda — ou um mutante que não morde.

```
UM MUTANTE QUE NÃO MUDA O COMPORTAMENTO NÃO MEDE A LEI: MEDE O TEXTO.
```

**E o System Map apanhou um defeito de desenho.** Houve, a meio desta missão, um
`motor/preflight_da_coleta.py` a compor os dois portões. O validador reprovou-o
— uma peça nova a morar numa gaveta que não era a do seu território — e a
pergunta seguinte matou-o: para que serve um terceiro ficheiro se cada dono já
responde por si e a ordem mora no workflow?

```
UM COMPOSITOR QUE SÓ ENCADEIA DOIS DONOS
É UM TERCEIRO SÍTIO ONDE A VERDADE PODE DIVERGIR.
```

O mapa não serviu de decoração: serviu de red team.

---

## 110.8 · O ACHADO QUE QUASE ENTROU NO SCHEMA

A chave da fila ia ser `(run_id, item_id)`. Medi-la matou-a:

```python
ITEM_ID = str(item.get("id") or item.get("url") or "?")
```

`"?"` é alcançável. Dois itens admitidos sem `id` e sem `url` na mesma corrida
trazem **ambos** `ITEM_ID = "?"`, e uma chave primária ali deitaria um deles fora
— em silêncio.

```
ITEM_ID NÃO É IDENTIDADE GARANTIDA DENTRO DA CORRIDA.
DESCOBRIR ISSO A APAGAR UMA LINHA É DESCOBRIR TARDE DEMAIS.
```

A chave é `(run_id, ordem)`, e retirar por um `ITEM_ID` ambíguo é **recusado com
nome** em vez de escolher um à sorte.

---

## 110.9 · O QUE ISTO **NÃO** DESBLOQUEIA

```
LIVE_MIGRATION_APPLIED   NO
READY_FOR_LIVE_APPLY     NO   ·  BLOCKER = RESTORE_NOT_PROVEN
```

A implementação está provada em **descartável**. O bloqueio à aplicação é
anterior a esta missão e está medido em
`docs/operacao/PREFLIGHT-LIVE-READONLY-V1.md`: o projeto não tem prova de que
consegue voltar atrás.

```
BACKUP EXISTE != RESTORE PROVADO.
DESIGNED != DB_TESTED != LIVE.
```

O canário italiano continua parado, e agora por **uma** razão em vez de três.

---

# §111 · UM RESTAURO QUE ARRANCA NÃO É UM RESTAURO QUE CHEGOU

**Missão:** `C-RESTORE-PROOF-BEFORE-LIVE-V2`, a seguir ao
`RESTORE_NOT_PROVEN` de `C-SALA-PERSISTENTE-E-PREFLIGHT-REAL-V1` e ao
`SAME_CLASS_RESTORE = NO` de `C-RECOVERY-PROOF-BEFORE-LIVE-V1`.

## 111.1 · O QUE MUDOU

A bancada de recuperação deixou de ser da classe **lógica** (`pg_dump`) e
passou a ser da classe **física** — base backup + arquivo de WAL +
recuperação a um instante — em PostgreSQL **17**, o mesmo major do LIVE.

```
SAME_CLASS_RESTORE       NO   ->  YES
SAME_PLATFORM_RESTORE    (nao medido) ->  NO
```

A lacuna **não fechou: mudou de sítio.** Deixou de ser sobre a classe da
ferramenta e passou a ser só sobre **quem opera o botão**.

## 111.2 · POR QUÊ

Porque a V1 provou um restauro a sério, e depois mediu a classe do backup do
LIVE e descobriu que tinha provado a classe errada. Um dump lógico e um
snapshot físico não se restauram com as mesmas ferramentas nem falham pelos
mesmos motivos.

```
RESTAURO PROVADO DE UMA CLASSE != RESTAURO PROVADO DA OUTRA.
```

E a razão de fundo, que é a que dura: `ONE RECOVERY PLAN → ONE PROOF`. Prova-se
o mecanismo que a **emergência** usaria, e não o que é mais fácil de exercer.

## 111.3 · PROVA

`provas/recuperacao_fisica_provada_no_postgres.py`, contra PostgreSQL 17
descartável. O banco é **destruído** antes de restaurar — restaurar por cima do
que ainda existe faz o verde vir do banco velho em vez de vir do backup.

```
DESTRUICAO_REAL     SIM   (delete · drop table · schema+ledger · corrupcao logica)
SECOES_DIFERENTES   NENHUMA  (11 seccoes)
WAL_FOI_REPRODUZIDO SIM
SEQUENCIAS          PASS  (64)
CADEIA_REAPLICADAS  0     e 29 SKIP HASH=MATCH
TRAVAS              8 provocadas, 8 RECUSARAM
CONTRAPROVA         13 sabotagens, 13 ACUSOU
RED_TEAM            28 ataques, 0 sobreviventes
LIVE_READS/WRITES/DDL   0 / 0 / 0
```

### Os três achados, e os três vieram do red team a atacar a própria prova

**1 · O PostgreSQL não recusa um alvo anterior ao backup.**

| alvo pedido | o que o servidor faz |
|---|---|
| **à frente** do WAL disponível | `FATAL`, e não promove — defende-se |
| **atrás** do início do backup | **PROMOVE, calado**, no estado do backup |

No segundo caso o log escreve *«database system is ready to accept
connections»* e o `exit` é `0`. O banco entregue está **silenciosamente
atrasado**, e nada diz que não chegou onde lhe pediram.

```
EXIT 0 E «READY TO ACCEPT CONNECTIONS» NAO SAO PROVA
DE QUE O RESTAURO CHEGOU AO INSTANTE PEDIDO.
```

**2 · Copiar o base backup não é reproduzir o WAL.**

A impressão de referência estava a ser tirada **antes** do base backup — e
então um restauro que reproduzisse **zero** WAL batia certo na mesma. A prova
teria aprovado um PITR que nunca fez PITR. A defesa é um **marco**: linhas
escritas depois do backup e antes do instante de destino, que não estão nos
ficheiros copiados e só existem no WAL.

```
UMA IMPRESSAO QUE O BASE BACKUP SOZINHO SATISFAZ NAO PROVA RECUPERACAO.
```

**3 · Sequência adiantada é correcto; atrasada é um id duplicado.**

O PostgreSQL regista as sequências no WAL aos saltos de 32 (`SEQ_LOG_VALS`), de
propósito, para que uma recuperação nunca devolva uma sequência atrasada.
Exigir igualdade byte a byte reprovaria todo o restauro físico correcto — e
reprovou: na primeira corrida esta prova reprovou o seu próprio restauro, com
`SECOES_DIFERENTES = ['SEQUENCIAS']`. **O restauro estava certo; a regra de
comparação é que estava errada.** A regra passou a ser `>=` com tecto.

### E duas coisas menores que custaram caro

- **Um desastre que o banco recusa não é um desastre.** Duas corrupções foram
  travadas pelo próprio schema (a identidade da observação e o `sha` da cópia).
  Tratar a recusa como estrago deixaria a prova a restaurar de um estrago que
  nunca aconteceu — e a chamar-lhe verde.
- **`setval` não é transaccional.** Sabotar uma sequência dentro de
  `begin … rollback` para testar a regra deixa a sequência sabotada depois do
  teste. Um teste que contamina o que mede não é um teste. E a sequência
  escolhida valia `1`: «pô-la em 1» não é pô-la para trás — uma sabotagem que
  não sabota mede o nada e diz `PASS`.

## 111.4 · CONSEQUÊNCIA

```
DISPOSABLE_BACKUP_CLASS  PHYSICAL
RESTORE_PROOF            BLOCKED
BLOCKER                  PLATFORM_RESTORE_NOT_EXERCISED
RUNBOOK_CANONICO         docs/operacao/RUNBOOK-DE-RECUPERACAO.md
```

A regra que fica, e é maior do que este banco:

> **Provar a classe não é provar a plataforma.** Um restauro local, por mais
> forte, não prova que o botão de Restore do fornecedor funciona nesta conta,
> neste projeto, com estas credenciais. As duas coisas ficam em campos
> separados, e o portão recusa-se a promover uma na outra.

```
MESMA CLASSE != MESMA PLATAFORMA.
POLITICA DA PLATAFORMA PROVADA != ESTE BACKUP EXISTE, E E DESTE INSTANTE.
CAN DO != DID DO.
```

E a que se aplica a qualquer conferência, não só a restauros:

> **O código de saída de uma operação não é o resultado dela.** Sempre que uma
> peça desta casa disser «correu bem», a pergunta seguinte é «correu bem *até
> onde*?» — e a resposta tem de vir de uma medição do estado final, nunca do
> facto de o processo ter terminado sem erro.

E, para a operação: **rollback não é restore.** Uma migration precisa de
`FORWARD_RECOVERY_PLAN`; a operação precisa de `DISASTER_RESTORE_PLAN`. Tratar
os dois como um leva a restaurar o banco inteiro — apagando tudo o que veio
depois — para desfazer um `create table`.

---

# §112 · O QUE FALTA É A CHAVE, E NÃO O RECURSO

**Missão:** `C-SUPABASE-LIVE-RECOVERY-PREFLIGHT-V1`, a medir o que a
`C-RESTORE-PROOF-BEFORE-LIVE-V2` deixou em `NOT_MEASURED`.

## 112.1 · O QUE MUDOU

Três regras nasceram, e nenhuma é sobre backups — são sobre **como se mede**.

## 112.2 · A PRIMEIRA · `401` NÃO É `404`

```
CREDENCIAL AUSENTE != RECURSO AUSENTE.
```

Durante duas missões esta casa escreveu «a API de gestão do Supabase não é
alcançável daqui». Medido agora, a frase era falsa no sítio que importa:

```
GET https://api.supabase.com/v1/projects                  ->  401
GET .../v1/projects/{ref}/database/backups                ->  401
```

`401` — e não `404`, e não *timeout*. **A rota existe e a rede chega lá.** O
que falta é a chave. A diferença entre as duas leituras é a diferença entre
«falta comprar» e «falta pedir», e elas levam a decisões opostas.

> Sempre que uma peça desta casa disser «não temos acesso a X», a pergunta
> seguinte é **qual foi o código de resposta**. «Não consegui» é um
> sentimento; `401`, `403`, `404` e *timeout* são quatro diagnósticos
> diferentes, e só um deles quer dizer que o recurso não existe.

## 112.3 · A SEGUNDA · NÚMERO MAIOR NÃO É DEPENDÊNCIA

O LIVE está declarado em `027`. A Sala é a `031`. Toda a gente — incluindo
duas missões desta casa — leu isso como «faltam três migrations e a `031`
precisa delas». Medido a **executar**, sobre o estado `027` construído num
banco descartável:

```
A_031_SOBRE_A_027_SEM_AS_TRES     PASS
A_031_DEPENDE_DE_028_029_030      NAO
```

A `031` toca `collection_run` e `raw_asset`, e **as duas nascem na `001`**.
As três do meio mexem em tabelas que ela não usa.

```
NUMERO MAIOR NAO E DEPENDENCIA.
ORDEM DE APLICACAO != GRAFO DE DEPENDENCIA.
```

E o remate, que é o que impede a lição de virar desculpa:

> **Não há dependência, e continua a não se saltar.** O aplicador canónico
> tem uma ordem só e um livro-razão com buraco é *drift* por construção. As
> duas frases são verdade ao mesmo tempo, e confundi-las erra nos dois
> sentidos: inventa um *blocker* que não existe, ou autoriza um salto que
> ninguém pode dar.

## 112.4 · A TERCEIRA · UMA LEI SÓ MORDE DEPOIS DO COMMIT

Esta foi apanhada em casa, e contra a missão anterior.

A `V2` correu `validate_system_map.py` e recebeu `PASS`, incluindo
`P9_CODIGO_DECLARADO`. Só que o ficheiro de prova ainda estava **por
versionar**, e o censo do mapa lê o **Git**, não a árvore de trabalho. O
verde era sobre um repositório onde o ficheiro não existia.

```
VALIDADOR VERDE SOBRE FICHEIRO POR VERSIONAR E VERDE SOBRE OUTRO REPOSITORIO.
```

A violação só apareceu na missão seguinte, quando o ficheiro já estava
commitado — e então o `P9` reprovou, com razão, código da missão anterior.

> A regra que fica: **valide depois de `git add`, nunca antes.** E, mais
> geral: quando uma conferência lê o Git e a mudança ainda está na árvore de
> trabalho, ela não está a conferir o que você fez — está a conferir o que
> havia antes de o fazer. É a mesma família do `§110` (`PROVA DENTRO DO
> PROCESSO != DURABILIDADE`), aplicada à fronteira entre a árvore e o
> índice.

## 112.5 · CONSEQUÊNCIA

```
LIVE_BACKUP_PREFLIGHT     BLOCKED   (12 campos, 12 NOT_MEASURED)
CREDENCIAL_QUE_FALTA      Personal Access Token de LEITURA
                          (`backups_read` / escopo `database:read`)
CUSTO_DE_A_USAR           zero — nao escreve nada
```

E uma correcção de dinheiro, que é onde um erro de leitura fica caro:
**o PITR não é pré-requisito** para provar a plataforma. O «Restore to a New
Project» do Supabase funciona a partir do **backup diário físico**. A `V2`
tinha deixado no ar que provar a plataforma implicava o add-on — implicava
**100 USD/mês** que não são precisos.

```
PRECO LIDO != PRECO PRESUMIDO.
E DUAS PAGINAS OFICIAIS DO MESMO FORNECEDOR PODEM DISCORDAR — registe a
divergencia, nao escolha a que lhe convem.
```

---

# §113 · A CHAVE FOI USADA, E O QUE ELA VIU

**Missão:** `C-SUPABASE-BACKUP-READONLY-MEASURE-V1`, a fechar a previsão que
o `§112` deixou escrita.

## 113.1 · O `§112` ACERTOU, E ISSO MEDE-SE

O `§112` disse que a API respondia `401` — e não `404` — e que o que faltava
era **a chave, não o recurso**. Nomeou a credencial exacta: um *scoped token*
de `Database → Backups → Read`. Ela foi criada e usada.

```
GET /v1/projects/{ref}/database/backups     ->  200
```

```
UMA PREVISAO QUE SE PODE MEDIR E UM ATIVO. UMA QUE NAO SE PODE E UMA OPINIAO.
```

O escopo mínimo foi **suficiente**: nenhum `403`, nenhum pedido de mais
permissão. Vale a lição inversa, que é a que poupa acessos: **pedir o escopo
estreito primeiro**, e só alargar contra um `403` real.

## 113.2 · O ESTADO REAL, QUE AGORA É FACTO E NÃO POLÍTICA

```
BACKUP_COUNT              7, todos COMPLETED, todos FISICOS
LATEST                    2026-09-13T03:05:36Z
OLDEST                    2026-09-07T03:07:43Z
RETENCAO OBSERVADA        6,00 dias de janela visivel
WALG_ENABLED              true          REGION   eu-west-1
PITR_ENABLED              NO   —  medido: o campo veio `false`
```

> **`PITR_ENABLED = NO` é diferente de `PITR_ENABLED = UNKNOWN`.** Ficaria
> `UNKNOWN` se o campo não tivesse vindo. Veio, e veio `false`. Só um valor
> explícito promove um `UNKNOWN` a `NO` — colapsar os dois inventa
> conhecimento que ninguém tem.

### A consequência que custa dados

```
RPO REAL DESTE PROJETO = ATE ~24 HORAS.
```

E a precisão que a média esconde: o backup é das **~03:07 UTC**. Uma perda às
02:00 UTC custa ~23 horas de escritas; uma às 04:00 UTC custa ~1 hora.

```
UM RPO MEDIO NAO E UM RPO. DIGA A HORA, E NAO SO O NUMERO.
```

## 113.3 · CADÊNCIA OBSERVADA NÃO É AGENDAMENTO DECLARADO

A Management API **não tem rota read-only** que devolva o agendamento de
backup. `BACKUP_SCHEDULE` ficou `UNKNOWN` — e o motivo importa:

```
UNKNOWN POR AUSENCIA DE ROTA  !=  UNKNOWN POR 403  !=  UNKNOWN POR FALHA.
```

O primeiro não se resolve pedindo mais permissão. Registar *qual* dos três é
que se tem evita a missão seguinte gastar tempo a pedir um acesso que não
existe.

O que se pode dizer é aritmética sobre os sete carimbos — seis intervalos
entre 23,94 h e 24,04 h, sempre às 03:05–03:08 UTC — e diz-se como o que é:
um backup diário **a acontecer**, e não um backup diário **agendado**.

## 113.4 · UM VARREDOR QUE NUNCA FICA VERMELHO É UM ENFEITE

Esta é a lição de engenharia da missão, e nasceu de um erro meu.

O varredor de vazamento procurava as **palavras** `sbp_`, `Bearer` e
`Authorization:`. Reprovou o artefacto — e o que lá estava era o **texto do
red team**, que nomeia esses padrões para explicar que os procura.

```
NOME DO PADRAO != VALOR DO PADRAO.
```

A correcção foi procurar a **forma** de uma credencial. Mas a regra durável é
a seguinte, e é mais geral:

> Uma verificação que nunca pode ficar vermelha não é uma verificação. Ponha
> **iscas conhecidas** a atravessá-la antes de ela julgar seja o que for, e
> **textos legítimos** a atravessá-la para medir o falso positivo.

Esse autoteste apanhou **dois buracos reais** no próprio varredor, ambos no
mesmo sítio: `Authorization: Bearer <x>` escapava porque `Bearer` tem seis
caracteres e o padrão exigia oito colados aos dois pontos. Nenhum deles teria
aparecido sem as iscas.

### E as iscas não se escrevem por extenso

Os guardas desta casa — `test_security_secret_shapes`, `test_handoff`,
`test_social_sessao` — varrem a **árvore versionada** à procura da forma de
uma credencial, e reprovaram as iscas. **Tinham razão.**

```
UM GUARDA QUE ABRE EXCECAO PARA «E SO UM TESTE» PASSA A TER EXCECOES
ATE DEIXAR DE SER GUARDA.
```

A isca precisa de existir **em memória**, e não no ficheiro: monta-se em
tempo de execução. O varredor recebe os bytes exactos; a árvore deixa de os
conter.

## 113.5 · DUAS ARMADILHAS DE FERRAMENTA, MEDIDAS E NÃO SUPOSTAS

### `workflow_dispatch` não existe fora do ramo por omissão

A API de dispatch devolveu `404`. Não era permissão nem atraso de indexação:
a lista de workflows do repositório devolveu **22 nomes, todos com
`blob/main/`**, e o novo não estava lá.

```
workflow_dispatch SO EXISTE PARA FICHEIROS QUE JA VIVEM NO RAMO POR OMISSAO.
```

O caminho certo **não** é fazer merge para `main` só para conseguir disparar
— isso troca um problema de execução por uma alteração de linha funcional sem
decisão de gente. É um `push` com `paths` estreito, que corre a versão **do
ramo**.

### `cmd | tee` devolve o estado do `tee`

```
shell por omissao do GitHub Actions = bash -e {0}   —  SEM pipefail.
```

Sem `set -o pipefail`, um script que aborta por vazamento detectado dá o
passo por **verde**. Um `| tee "$GITHUB_STEP_SUMMARY"` bem-intencionado apaga
o código de saída que é a única coisa que interessa.

## 113.6 · E O QUE ISTO NÃO PROVOU

```
BACKUP LISTADO           != RESTAURO PROVADO.
SETE BACKUPS FISICOS     != O BOTAO «RESTORE TO A NEW PROJECT» EXISTE AQUI.
`COMPLETED` NA API       != OS BYTES LEEM-SE.
```

`SAME_PLATFORM_RESTORE` continua `NOT_RUN` e `READY_FOR_LIVE_APPLY` continua
`NO` — e não por falta de informação.

```
MEDIR REMOVE UNKNOWN. NAO RELAXA PORTAO.
```

Uma missão que mede bem sente a tentação de cobrar o portão como prémio. O
portão não é pago em medições; é pago na coisa que ele exige.

### O corolário do `A20`, aprendido a sério

Correr a prova à mão **sobrescreve o artefacto commitado**. Nesta missão um
ensaio com token inválido substituiu a medição de `200` por um `401` de
cobaia, e só não foi commitado porque o `sha256` não batia com o digest que o
GitHub publicou.

```
O ARTEFACTO QUE VALE E O QUE A CORRIDA PRODUZIU.
Descarregue-o do run e confira o digest — nao o regenere localmente.
```

---

# §114 · A ORDEM NASCE DA DEPENDÊNCIA — UM CONSUMIDOR ANTES DO PRODUTOR NÃO FALHA

**Missão:** `C-SYSTEM-MAP-G6-DEPENDENCY-ORDER-V1`
**Linha:** `claude/system-map-g6-dependency-order-v1` · **HEAD medido:** `4224a234`
**Delta de origem:** `handoff/KNOW-HOW-DELTA-ORDEM-POR-DEPENDENCIA.md`
(blob `799ba94b`, o mesmo nas duas linhas que o carregam)

A `§93.4` fechou com uma dívida escrita à mão: **`UM CARIMBO VERIFICÁVEL NÃO PAGA
UMA DÍVIDA DE ORDEM`**. Esta secção é o pagamento dessa dívida, e o que se
aprendeu a pagá-la. A `§88.4` já tinha o terceiro relógio a nomear sem reparar, e
a `§93.1` já tinha a pergunta certa sobre frescura — *«que árvore media esta
entrada quando eu a li?»*. O que faltava era o outro lado: **o que se faz depois
de nomear.**

## 114.1 · UM CONSUMIDOR ANTES DO PRODUTOR NÃO FALHA

Três passos da cadeia do System Map corriam **antes** do passo que escreve o que
eles leem. A cadeia ficava verde. Os testes ficavam verdes. O validador ficava
verde.

```
    UM CONSUMIDOR ANTES DO PRODUTOR NÃO FALHA:
    ELE RESPONDE DA RODADA PASSADA.
```

Porque o ficheiro **existe**. É o da geração anterior, e abrir um ficheiro antigo
não levanta excepção nenhuma — devolve uma resposta antiga, com ar de resposta.

É por isso que este defeito não se apanha a correr o sistema. Só se apanha
comparando **o que cada passo declara ler** com **o sítio onde ele corre** — e
isso exige duas coisas anteriores, que são as duas missões de antes: cada passo
declarar as suas entradas, e haver uma lista só.

> **Consequência de método.** Quando um defeito não produz erro, procurar erro é
> a estratégia errada. Procura-se **discordância entre duas declarações**.

## 114.2 · A DEPENDÊNCIA DETERMINA A ORDEM; A ORDEM NÃO DETERMINA A DEPENDÊNCIA

Havia duas coisas que podiam discordar: a lista escrita e o que os passos diziam
ler. Discordaram durante meses.

A correcção não é arrumar a lista. É **tirar-lhe a autoridade**: a ordem passa a
sair de um ordenamento topológico sobre as dependências declaradas, com desempate
estável pela posição escrita. A posição escrita deixa de decidir e passa a
desempatar.

```
    DUAS COISAS IGUAIS HOJE NÃO SÃO A MESMA COISA:
    SÓ SE SABE QUAL DELAS MANDA QUANDO ELAS DISCORDAM.
```

E daí sai a forma de o provar: **baralhar a lista escrita** e exigir que a ordem
derivada continue a respeitar todas as arestas. Se a resposta não muda quando a
semente muda, a derivação não estava a derivar — estava a copiar com um passo
extra.

E se houver ciclo entre as dependências, **a derivação rebenta em vez de
escolher**. Escolher seria esconder o ciclo para conseguir ordenar, que é
exactamente a mentira que a lei existe para impedir.

## 114.3 · DUAS CLASSES DE DEPENDÊNCIA, E A FUGA BARATA ENTRE ELAS

Nem toda a leitura é o mesmo tipo de dependência:

| classe | o consumidor pediu | ordena? |
|---|---|---|
| **nomeada** | *aquele* artefacto, pelo nome | **sim** — o produtor corre antes |
| **varredura** | «o que existir na árvore quando eu correr» | **não** — lê a rodada anterior |

A segunda não é uma dependência menor: é uma dependência com **outro contrato
temporal**. E entre as duas há uma fuga barata — tirar o nome e deixar o seletor
apanhar o ficheiro na mesma. A leitura continua explicada, a aresta deixa de
ordenar, e tudo continua verde.

```
    QUERES FRESCO? NOMEIA.
    QUEM NOMEIA NO CÓDIGO, NOMEIA NO CONTRATO.
```

A guarda que fecha isto compara o que o código **nomeia** (literais na árvore
sintáctica) com o que o contrato declara. Nomear no código e declarar varredura é
mentira detectável.

## 114.4 · UM MEDIDOR QUE ESCREVE DENTRO DO QUE MEDE NÃO SE ORDENA: CONVERGE

Ficou um ciclo, e ele não se ordena. Dizer «é estrutural» seria opinião. A prova
cabe numa linha:

> o seletor do censo do congelamento apanha o ficheiro que **o próprio censo do
> congelamento escreve**.

Nenhuma permutação põe um passo antes de si mesmo. Deixa de ser argumento e passa
a ser aritmética.

```
    UM MEDIDOR QUE ESCREVE DENTRO DO QUE MEDE
    NÃO SE ORDENA: CONVERGE.
```

Generalizando: sempre que um sistema mede uma superfície onde ele próprio
escreve, o ciclo é da forma do problema e não da ordem dos passos. O que se exige
nesse caso não é ordem — é **convergência provada**. Isto não é a convergência da
`§96` (duas implementações que se reduzem a um dono); é o laço de um medidor
sobre si próprio, e as duas não se resolvem pelo mesmo meio.

## 114.5 · «O ATRASO EXISTE» E «O ATRASO CUSTA» SÃO DUAS AFIRMAÇÕES

Medido: mexe-se numa fonte, correm-se três passagens, comparam-se os conteúdos
sem o relógio. A 1.ª e a 2.ª dão o **mesmo** conteúdo.

O atraso **existe** — está provado pelo laço. E **não custa** — porque os
varredores dependem do *conjunto* (que ficheiros existem, de que espécie) e não
do conteúdo que os passos seguintes reescrevem. As duas afirmações medem-se
separadamente, e é por isso que se escrevem separadamente.

```
    MEDIR A PRIMEIRA E PUBLICAR A SEGUNDA É O ERRO DE SEMPRE.
```

E a prova de igualdade precisa de **controlo positivo**: antes de comparar, exigir
que o retrato *veja* a mudança que a fonte mexida provocou. Sem isso, um retrato
partido — que devolvesse sempre o mesmo — passava as comparações todas sem medir
nada.

Corolário separado, e que não se esconde um atrás do outro:

```
SEMANTIC_DETERMINISM = sim     BYTE_DETERMINISM = não (relógio nos artefactos)
```

## 114.6 · `STALE_BY_CONTRACT` NÃO É `STALE_BY_CYCLE`, E NENHUM DOS DOIS É *STALE* POR ACIDENTE

Três regeneradores não são corridos por automação nenhuma. Os artefactos deles
ficam para trás sempre que a árvore anda. Chamar defeito a isso seria acusar o
sistema de cumprir o próprio contrato; chamar-lhe normal sem contrato escrito
seria varrer dívida para debaixo de uma palavra.

A regra que sobrevive às duas tentações:

```
    O ATRASO É ESPERADO QUANDO A DECLARAÇÃO O EXPLICA,
    E DEFEITO QUANDO NÃO EXPLICA.
```

Basta **um** pedaço de prova por explicar para a resposta inteira ser defeito —
somar explicações parciais é tratar meia prova como prova.

E prova-se pelos dois lados: tira-se a classe declarada e o mesmo artefacto tem
de voltar a ser defeito no minuto seguinte.

```
    UMA CLASSE QUE NÃO MUDA QUANDO A DECLARAÇÃO MUDA
    NÃO ESTÁ A CLASSIFICAR: ESTÁ A ETIQUETAR.
```

`STALE_BY_CONTRACT` responde por *«ninguém o corre, e está escrito»*.
`STALE_BY_CYCLE` (`§93`) responde por *«correu, mas leu a rodada anterior»*. Usar
um pelo outro apaga exactamente a diferença que esta missão foi buscar.

## 114.7 · SE A LEI JÁ IMPEDE O CASO, O RAMO QUE O TRATA NÃO PROTEGE NADA

O classificador tinha um ramo para «o produtor corre depois». A derivação da
ordem impede esse caso, portanto nenhum teste conseguia lá chegar — e uma mutação
que o partisse sobrevivia a tudo.

```
    SE A LEI JÁ IMPEDE O CASO, O RAMO QUE O TRATA
    NÃO PROTEGE NADA: SÓ ADIA A DESCOBERTA.
```

Saiu, com a razão escrita no lugar dele.

A `§61.4` tinha o ramo que só os dados de amanhã exercitam e a `§102.4` tinha o
ramo adormecido atrás de um `or`. Esta acrescenta o terceiro caso, e o mais
incómodo: **o ramo que nenhuns dados alcançam porque a própria lei o tornou
impossível.** Nos dois primeiros espera-se; neste apaga-se.

E daí sai um uso novo para uma ferramenta velha: o sobrevivente de mutação **é**
o detector de código morto. Um mutante que ninguém mata está a apontar para uma
linha que ninguém consegue exercitar.

> **Corolário operacional.** Quando uma guarda só corre em presença do defeito,
> ela nunca corre num repositório saudável. Constrói-se o caso à mão.

## 114.8 · CONFERIR NÃO É REIMPLEMENTAR

Havia dois runtimes a ler a mesma lista (Python e JavaScript). Derivar a ordem nos
dois seria repetir o algoritmo — e dois algoritmos que se afastem são duas ordens
outra vez, que é precisamente o que a `§96` proíbe. Derivar só num e deixar o
outro acreditar no ficheiro seria confiar num ficheiro que pode mentir.

A saída é assimétrica de propósito: **um deriva, o outro confere**. A conferência
cabe em cinco linhas, não tem opinião e recusa-se a agir quando o ficheiro
contradiz as dependências.

```
    UM VERIFICADOR QUE FALHA DIZ «ESTE FICHEIRO ESTÁ ERRADO».
    UM SEGUNDO ALGORITMO DIZ «EU TENHO OUTRA OPINIÃO».
```

Isto é a saída para quando `ONE CONCEPT → ONE OWNER` encontra dois runtimes que
têm ambos de agir: o dono continua a ser um, e o segundo é leitor conferente, não
co-autor.

## 114.9 · O ARNÊS QUE SÓ REPÕE NO `finally` DEIXA O ESTRAGO NOS DIAS MAUS

Regra antiga, defeito novo. A `§79.6` já tinha o backup tirado **depois** da
mutação e a `§88.6` já tinha o arnês que deixava um alarme sempre aceso. Esta é a
terceira família: ler os originais antes de mutar e repor no `finally` **não
chega**. Se o processo for morto a meio — *timeout*, CI a cortar o job — o
`finally` não corre e a mutação fica no disco de trabalho.

Aconteceu: uma linha de entradas ficou apagada e foi para o `git add`. Só a prova
de IO a apanhou, três corridas depois.

```
    UM ARNÊS QUE SÓ REPÕE QUANDO ACABA BEM
    DEIXA O ESTRAGO EXACTAMENTE NOS DIAS MAUS.
```

O que fecha: o original lê-se no arranque do módulo e há uma guarda **no fim** que
compara o ficheiro com ele. A prova acusa-se a si própria.

## 114.10 · A CATEGORIA QUE NINGUÉM CORRE É A QUE PODE ESTAR PARTIDA HÁ MESES

O corredor da cadeia anunciava cinco categorias e a tabela dele tinha quatro. A
quinta morria com `KeyError`. Era, precisamente, a categoria dos passos que
nenhuma automação corre.

```
    A CATEGORIA QUE NINGUÉM CORRE
    É A QUE PODE ESTAR PARTIDA HÁ MESES.
```

A guarda que ficou não testa as quatro que se usam: percorre **o vocabulário
declarado** e exige que cada categoria anunciada tenha corredor. A forma geral —
testar o vocabulário inteiro e não os membros que o dia-a-dia exercita — vale
para qualquer tabela de despacho desta casa.

## 114.11 · O QUE ISTO NÃO AUTORIZA

- Não autoriza chamar `CURRENT` a um artefacto atrasado.
- Não autoriza declarar varredura uma dependência pedida pelo nome.
- Não autoriza automatizar um regenerador para fechar uma contagem: medido quatro
  vezes, isso troca um número por uma cadeia que nunca mais assenta.
- Não autoriza usar «ciclo atrasado» como nome para *stale* que ninguém explicou.
