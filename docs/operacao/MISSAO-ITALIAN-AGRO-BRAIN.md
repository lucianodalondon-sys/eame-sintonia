# MISSÃO ESTRATÉGICA — CRIAR O ITALIAN AGRO BRAIN

Esta missão é uma NOVA LINHA PARALELA do projeto SINTONIA EAME — ITÁLIA.

NOME OFICIAL:

# ITALIAN AGRO BRAIN

SIGLA INTERNA:

IAB


# 0. CONTEXTO

Estamos coletando cada vez mais:

- boletins fitossanitários;
- pesquisas;
- artigos;
- documentos regulatórios;
- informações climáticas;
- produtos;
- moléculas;
- culturas;
- doenças;
- pragas;
- ervas daninhas;
- pesquisadores;
- empresas;
- regiões;
- eventos;
- informações de mercado;
- comunicação de concorrentes;
- ciência;
- observações históricas.

Também começamos a cruzar essas informações.

Hoje temos uma preocupação estratégica:

NÃO queremos que todo o conhecimento adquirido pelo Sintonia continue existindo apenas como:

- arquivos;
- PDFs;
- JSONs;
- registros brutos;
- embeddings;
- resultados temporários;
- respostas de LLM;
- cruzamentos que desaparecem depois da execução.

Queremos construir uma MEMÓRIA AGRONÔMICA PERSISTENTE sobre a agricultura italiana.

Não é armazenamento de arquivos.

É armazenamento de CONHECIMENTO.


# 1. VISÃO

O ITALIAN AGRO BRAIN deve, ao longo dos anos, tornar-se uma representação acumulada e pesquisável do mercado agrícola italiano.

No futuro deverá permitir perguntas como:

“Conte todo o histórico da praga X na região Y nos últimos cinco anos.”

“Quando ela normalmente aparece?”

“Que condições climáticas precederam os surtos?”

“Quais culturas foram afetadas?”

“Que tratamentos foram recomendados?”

“Quais moléculas estavam autorizadas naquele período?”

“Quais produtos ADAMA poderiam atender esse problema?”

“Como a situação mudou de um ano para outro?”

“Que pesquisadores estudaram esse problema?”

“Quais regiões apresentaram comportamento semelhante?”

“O que está diferente este ano?”

“Quais riscos podem crescer nas próximas semanas?”

“O que mudou no mercado de tomate no norte da Itália?”

“Quais oportunidades fitossanitárias estão surgindo?”

Isso deve ser possível SEM precisar reler toda a biblioteca bruta toda vez.


# 2. VALOR ESTRATÉGICO

O ITALIAN AGRO BRAIN pode se tornar um dos principais ativos proprietários do Sintonia.

Os arquivos públicos podem ser baixados novamente.

Modelos de IA podem ser contratados por qualquer empresa.

Scrapers podem ser recriados.

Mas uma estrutura acumulada durante anos contendo:

FATOS
+
HISTÓRICO
+
ENTIDADES
+
RELAÇÕES
+
TEMPO
+
GEOGRAFIA
+
EVIDÊNCIAS
+
CRUZAMENTOS
+
APRENDIZADOS

é muito mais difícil de reconstruir.

Portanto tratar essa camada como PATRIMÔNIO DE CONHECIMENTO.


# 3. NÃO INTERROMPER O PROJETO ATUAL

Esta missão NÃO pode parar nem desviar:

- Collection;
- Sala de Espera;
- Intelligence;
- desenvolvimento das ferramentas;
- Casco;
- outras missões ativas.

Criar linha paralela própria.

Não modificar worktrees em execução.

Não fazer merge prematuro.

Não usar esta missão para rearquitetar silenciosamente partes ativas do sistema.


# 4. PRIMEIRA ORDEM — ENCOMENDAR ESTUDO AO SINTONIA LAB

Antes da implementação arquitetural definitiva, encomende ao bot:

SINTONIA LAB

um estudo específico chamado:

# STUDY — ITALIAN AGRO BRAIN ARCHITECTURE V1


O SINTONIA LAB deve analisar o estado REAL do Sintonia e estudar como sistemas maduros tratam:

- knowledge graphs;
- semantic layers;
- ontologies;
- temporal knowledge;
- event knowledge;
- provenance;
- evidence graphs;
- entity resolution;
- claim consolidation;
- historical knowledge;
- decision intelligence;
- RAG;
- GraphRAG;
- structured retrieval;
- knowledge bases;
- derived knowledge;
- contradiction management;
- knowledge lineage.

Usar sua triangulação:

CLAUDE OPUS 5.5
GPT-5.6 SOL
DEEPSEEK 4.1 FLASH

Primeira análise cega.

Depois confronto.

Depois síntese baseada em evidência.


# 5. BENCHMARK PRIORITÁRIO DO LAB

Estudar principalmente:

Palantir Foundry / Ontology / AIP

Databricks

DataHub

OpenLineage

Neo4j

PostgreSQL

PGVector

GraphRAG

LlamaIndex

knowledge graph research

temporal knowledge graphs

event sourcing quando aplicável

decision intelligence

e sistemas comparáveis.

NÃO copiar tecnologia.

Perguntar:

“Qual problema resolvem?”

“Precisamos realmente disso?”

“Qual é a solução mínima equivalente para o Sintonia?”


# 6. PERGUNTA ARQUITETURAL CENTRAL

O estudo precisa responder com evidência:

ONDE O CONHECIMENTO DEVE SER GRAVADO?

Não assumir previamente que deve ficar:

ANTES da Intelligence

ou

DEPOIS da Intelligence.

Avaliar.

Minha hipótese inicial a ser TESTADA pelo Lab é:

# ARQUITETURA HÍBRIDA

O ITALIAN AGRO BRAIN possui duas classes fundamentais.


## A — OBSERVED KNOWLEDGE

Conhecimento proveniente diretamente de evidências admitidas.

Exemplos:

uma ocorrência;

uma recomendação oficial;

uma relação cultura-doença descrita por fonte confiável;

uma autorização regulatória;

um evento;

uma condição climática observada;

uma região produtora;

uma presença registrada.

Isso entra ANTES do raciocínio da Intelligence.


## B — DERIVED KNOWLEDGE

Conhecimento obtido por:

- cruzamentos;
- regras;
- estatística;
- modelos;
- Intelligence;
- inferências.

Exemplo:

“Há aumento de risco de míldio.”

Isso NÃO é a mesma coisa que:

“Choveu 80 mm.”

O primeiro é derivado.

O segundo pode ser observado.

O sistema deve preservar essa diferença eternamente.


# 7. REGRA INVIOLÁVEL

INFERÊNCIA NUNCA VIRA FATO APENAS POR TER SIDO ARMAZENADA.

Todo conhecimento deve carregar tipo epistemológico.

Exemplos:

OBSERVED_FACT

ASSERTED_FACT

DERIVED_FACT

INFERENCE

HYPOTHESIS

SIGNAL

PREDICTION

RULE

RELATION

EVENT

SUMMARY

UNKNOWN.


# 8. NÃO DUPLICAR ARQUIVOS

O ITALIAN AGRO BRAIN deve ser MUITO LEVE.

Queremos principalmente:

TEXTO ESTRUTURADO

+

IDs

+

RELAÇÕES

+

METADADOS ESSENCIAIS.

Não duplicar:

PDF

imagem

vídeo

áudio

HTML gigante

transcrição inteira

arquivo bruto.

Esses continuam em suas casas canônicas.

O Brain aponta para eles por identidade/proveniência.


# 9. PRINCÍPIO DE COMPACTAÇÃO

Se 50 fontes diferentes confirmarem:

“Doença X afeta cultura Y”

NÃO precisamos armazenar 50 frases completas repetidas como conhecimento independente.

Podemos possuir:

CLAIM CANÔNICA:

DOENÇA X
→ AFETA
→ CULTURA Y

e:

EVIDENCE LINKS = 50.

Preservar todas as evidências.

Evitar duplicação sem perder auditabilidade.


# 10. UNIDADE CENTRAL

Estudar uma arquitetura baseada em unidades mínimas como:

ENTITY

FACT

CLAIM

RELATION

EVENT

RULE

EVIDENCE

DERIVATION

INFERENCE

SIGNAL

HYPOTHESIS.


# 11. EXEMPLO

Uma notícia ou boletim diz:

“Em 26/08/2026 foram observadas condições favoráveis ao desenvolvimento de míldio em tomate no Veneto.”

O Brain poderia representar:

EVENT:

tipo:
DISEASE_RISK_OBSERVATION

disease:
Míldio

crop:
Tomate

fact_time:
2026-08-26

fact_location:
Veneto

condition:
condições favoráveis

evidence:
RAW_OBSERVATION_ID XYZ

source:
Serviço Fitossanitário Veneto.


Não armazenar somente a frase solta.


# 12. TEMPO É FUNDAMENTAL

O Brain deve ser construído desde o início para responder perguntas históricas.

Precisamos conseguir reconstruir:

O QUE SABÍAMOS?

QUANDO?

O QUE ESTAVA ACONTECENDO?

ONDE?

QUAL ERA O REGULATÓRIO NAQUELE MOMENTO?

QUE PRODUTOS EXISTIAM?

QUE RISCOS EXISTIAM?

QUE CONCLUSÕES O SISTEMA PRODUZIU?


Estudar campos como:

FACT_TIME

VALID_FROM

VALID_TO

OBSERVED_AT

PUBLISHED_AT

COLLECTED_AT

DERIVED_AT.


Nunca substituir um pelo outro.


# 13. GEOGRAFIA É FUNDAMENTAL

Preservar a separação já aprendida no Sintonia:

SOURCE_LOCATION

≠

FACT_LOCATION.

O Brain precisa entender estruturas territoriais italianas:

ITALIA
→ REGIONE
→ PROVINCIA
→ COMUNE

quando aplicável.

Não inferir localização sem prova.


# 14. PROVENIÊNCIA É OBRIGATÓRIA

Tudo no Brain deve poder responder:

DE ONDE VEIO?

Para conhecimento observado:

KNOWLEDGE
→ EVIDENCE
→ RAW OBSERVATION
→ SOURCE.


Para conhecimento derivado:

KNOWLEDGE
→ DERIVATION
→ INPUT KNOWLEDGE
→ EVIDENCE.


Nunca aceitar uma conclusão sem lineage.


# 15. DERIVAÇÃO

Se a Intelligence produzir:

“RISCO ELEVADO DE DOENÇA X NO VENETO”

guardar algo equivalente a:

DERIVED_KNOWLEDGE

method:
regra/modelo específico

version:
versão

inputs:
IDs dos fatos usados

run:
ID da execução

derived_at:
timestamp

confidence:
se houver método comprovado para isso.

Se a regra/modelo mudar, deve ser possível reproduzir ou invalidar a conclusão antiga.


# 16. CONHECIMENTO AGRONÔMICO

O Brain deverá gradualmente conhecer entidades e relações envolvendo:

CULTURAS

VARIEDADES

ESTÁDIOS FENOLÓGICOS

PRAGAS

DOENÇAS

ERVAS DANINHAS

PATÓGENOS

VETORES

SINTOMAS

MOLÉCULAS

INGREDIENTES ATIVOS

MODO DE AÇÃO

PRODUTOS

EMPRESAS

REGISTROS

AUTORIZAÇÕES

RESTRIÇÕES

TRATAMENTOS

RESISTÊNCIA

EFICÁCIA

CLIMA

TEMPERATURA

PRECIPITAÇÃO

UMIDADE

SOLO

REGIÕES

ÁREAS DE PRODUÇÃO

SAFRAS

PREÇOS

MERCADO

PRODUTORES

COOPERATIVAS

PESQUISADORES

UNIVERSIDADES

PUBLICAÇÕES

EVENTOS.


# 17. VOCABULÁRIO E SINÔNIMOS

Problema crítico:

a mesma coisa pode possuir vários nomes.

Exemplos:

nome comum

nome científico

nome italiano

nome inglês

sigla

marca comercial

ingrediente ativo.

O Brain precisa de identidade canônica e aliases.

Não gerar entidades duplicadas porque duas fontes escreveram nomes diferentes.


# 18. CONTRADIÇÃO

O Brain NÃO deve obrigatoriamente escolher uma verdade quando fontes divergem.

Precisa suportar:

CLAIM A

CONTRADICTS

CLAIM B.

Registrar:

fonte;

data;

contexto;

escopo;

qualidade.

Algumas contradições podem ser resolvidas pela Intelligence.

Outras permanecem divergências legítimas.


# 19. RESUMOS NÃO SÃO FONTE DE VERDADE

Podemos possuir:

MARKET SUMMARY

DISEASE TIMELINE

REGIONAL PROFILE

CROP PROFILE.

Mas esses produtos devem ser DERIVADOS e reconstruíveis.

O conhecimento atômico e sua evidência continuam sendo a fundação.


# 20. COMO DEVE FUNCIONAR UMA PERGUNTA FUTURA

Exemplo:

“Conte tudo que aconteceu com a praga X na Emilia-Romagna entre 2024 e 2026.”

Não quero:

busca vetorial em 20 mil PDFs
→ mandar contexto gigante para LLM.

Quero primeiro:

ENTITY = praga X

+

LOCATION = Emilia-Romagna

+

TIME = 2024–2026

→ EVENTS

→ FACTS

→ RELATIONS

→ HISTÓRICO

→ EVIDENCES

→ DERIVED KNOWLEDGE

e só então usar IA para montar uma resposta humana.


# 21. BUSCA HÍBRIDA

Estudar arquitetura futura combinando:

STRUCTURED QUERY

+

FULL TEXT SEARCH

+

RELATION GRAPH

+

VECTOR SEARCH quando trouxer benefício comprovado

+

LLM REASONING.


VECTOR NÃO É O BRAIN.

Embedding NÃO É conhecimento canônico.

Embedding deve ser índice reconstruível.


# 22. TECNOLOGIA

Começar pelo mecanismo MAIS SIMPLES capaz de resolver o problema.

Nossa hipótese inicial:

POSTGRESQL

pode ser suficiente para a primeira versão através de:

tabelas estruturadas;

relações;

JSONB controlado;

full text;

índices;

eventualmente PGVector.

NÃO instalar Neo4j ou plataforma semelhante apenas porque o conceito se chama Knowledge Graph.

Somente adicionar infraestrutura especializada depois de medir necessidade.


# 23. PROPOSTA DE MODELO A SER ESTUDADA

O Lab deve avaliar algo conceitualmente equivalente a:

AGRO_ENTITY

AGRO_CLAIM

AGRO_RELATION

AGRO_EVENT

AGRO_RULE

AGRO_EVIDENCE_LINK

AGRO_DERIVATION

AGRO_INFERENCE

AGRO_SIGNAL

AGRO_ALIAS.


Não aceitar esses nomes como definitivos sem estudar o modelo atual do repositório.


# 24. NÃO CRIAR SEGUNDA IDENTIDADE

CRÍTICO.

O Sintonia já possui trabalho sério sobre:

RUN

OBSERVATION

CONTENT

STORAGE OBJECT

RAW_OBSERVATION_ID

SOURCE_ID

DOCUMENT_KEY

SHA256.

O Brain deve REFERENCIAR essa fundação.

NÃO criar uma segunda identidade concorrente para observações ou documentos.


# 25. MUDANÇAS NA COLLECTION

O estudo precisa identificar:

O QUE A COLLECTION PRECISA PRESERVAR AGORA

para o Brain funcionar corretamente depois.

Não transformar Collection em Intelligence.

Collection deve continuar coletando.

Mas pode precisar garantir que informações fundamentais sobrevivam, por exemplo:

SOURCE

OBSERVATION

PUBLICATION TIME

COLLECTION TIME

LANGUAGE

document identity

source URL

proveniência

estrutura textual

metadados importantes.


Separar claramente:

CAPTURAR

de:

INTERPRETAR.


# 26. MUDANÇAS NA SALA DE ESPERA

Avaliar se a admissão precisa preparar material para extração de conhecimento.

Possivelmente:

document accepted
→ extraction eligibility
→ entity/fact/event extraction.

Não inventar nova etapa se arquitetura existente já possui equivalente.


# 27. MUDANÇAS NA INTELLIGENCE

A Intelligence deixa de depender exclusivamente de reler conteúdo bruto.

Passa progressivamente a poder consumir:

ITALIAN AGRO BRAIN — OBSERVED KNOWLEDGE.

E seus resultados relevantes podem retornar como:

ITALIAN AGRO BRAIN — DERIVED KNOWLEDGE.


# 28. RELAÇÃO COM AS FERRAMENTAS

No futuro ferramentas como:

FUTURE RADAR

MARKET INTELLIGENCE

DISEASE WATCH

CROP INTELLIGENCE

COMPETITOR INTELLIGENCE

PRODUCT OPPORTUNITY

CLIMATE OPPORTUNITY

REGULATORY INTELLIGENCE

podem consumir o Brain.


# 29. FUTURE RADAR

O ITALIAN AGRO BRAIN é especialmente importante para Future Intelligence.

Previsão não deve depender apenas do presente.

Para projetar:

AMANHÃ

precisamos saber:

ONTEM
+
HOJE.

Exemplo:

histórico de chuva

+

histórico de doença

+

estágio das culturas

+

sazonalidade

+

região

+

tratamentos

+

regulatório

+

situação atual

+

previsão climática.

Portanto o Brain precisa preservar HISTÓRIA.


# 30. KNOWLEDGE TIMELINE

Uma capacidade estrutural desejável é reconstruir uma linha do tempo de qualquer entidade.

Exemplo:

ENTITY:
Peronospora infestans

TIMELINE:

2023
eventos...

2024
eventos...

2025
eventos...

2026
eventos...

por:

região;

cultura;

condições;

tratamentos;

fontes;

consequências.


# 31. BAIXO TAMANHO

Objetivo:

guardar MUITO conhecimento usando POUCOS bytes.

Preferir:

IDs

strings curtas

relações

timestamps

geo IDs

enumerações

texto normalizado

links de evidência.

Evitar armazenar novamente conteúdo bruto.

Medir:

BYTES_PER_KNOWLEDGE_ITEM.

Registrar evolução.


# 32. BACKFILL

Depois de definir o contrato:

não jogar todo o acervo dentro cegamente.

Criar piloto.

Sugestão:

selecionar:

1 doença/praga

1 cultura

1 ou 2 regiões

alguns anos de material disponível.

Construir a linha do tempo completa.

Perguntar:

“Conseguimos reconstruir a história agronômica dessa entidade?”

Se NÃO:

descobrir qual informação estrutural está faltando.


# 33. TESTE CANÁRIO

Criar um CANARY histórico.

Exemplo genérico:

PRAGA_X
+
REGIÃO_X
+
PERÍODO_DE_ANOS.

O sistema deve responder:

- o que aconteceu;
- quando;
- onde;
- culturas afetadas;
- condições associadas;
- intervenções relatadas;
- evolução;
- evidências;
- lacunas.

E toda afirmação importante precisa chegar à evidência.


# 34. NÃO PEDIR AO LLM PARA PREENCHER BURACOS

Se não houver dado:

UNKNOWN.

Nunca completar cronologia com conhecimento geral do modelo.


# 35. REORGANIZAR A DOCUMENTAÇÃO CANÔNICA

Depois do estudo arquitetural, levantar TODAS as Bíblias e documentos canônicos existentes.

Não confundir:

BÍBLIA

KNOW-HOW

SYSTEM MAP

HANDOFF

CONTRATO

RUNBOOK.


Propor as alterações mínimas necessárias.


Provavelmente precisaremos de um documento canônico dedicado equivalente a:

BIBLIA-ITALIAN-AGRO-BRAIN.md

mas primeiro verificar convenções reais do repositório.


# 36. A BÍBLIA DO IAB DEVE DEFINIR

PROPÓSITO

FRONTEIRA

O QUE É CONHECIMENTO

O QUE NÃO É CONHECIMENTO

TIPOS EPISTEMOLÓGICOS

IDENTIDADE

ENTIDADES

CLAIMS

EVENTOS

RELAÇÕES

TEMPO

GEOGRAFIA

PROVENIÊNCIA

DERIVAÇÃO

CONTRADIÇÃO

VALIDAÇÃO

COMPACTAÇÃO

RETENÇÃO

BACKFILL

QUERY

SEGURANÇA

INTEGRAÇÃO COM COLLECTION

INTEGRAÇÃO COM INTELLIGENCE

INTEGRAÇÃO COM TOOLS

INTEGRAÇÃO COM CASCO.


# 37. SYSTEM MAP

Depois de aprovado o desenho:

o System Map deve mostrar explicitamente o ITALIAN AGRO BRAIN.

Não colocá-lo como pasta lateral obscura.

Ele será uma camada estrutural do Sintonia.


# 38. ORDEM DE IMPLEMENTAÇÃO

FASE 0
medir Git e arquitetura real.

FASE 1
SINTONIA LAB executa estudo.

FASE 2
produzir arquitetura proposta.

FASE 3
red team da arquitetura.

FASE 4
atualizar contratos/Bíblias/System Map necessários.

FASE 5
implementar núcleo mínimo.

FASE 6
piloto histórico pequeno.

FASE 7
avaliação cega.

FASE 8
corrigir.

FASE 9
iniciar backfill progressivo do acervo existente.

FASE 10
integrar novos documentos ao fluxo permanente.


# 39. IMPORTANTE — JÁ COMEÇAR A GUARDAR

Não quero esperar o portal ficar pronto para começar essa memória.

Assim que:

CONTRATO V1
+
SCHEMA V1
+
CANARY PASS

existirem,

novos conhecimentos elegíveis devem começar a ser registrados no ITALIAN AGRO BRAIN.

Continuar amadurecendo enquanto Collection e Intelligence evoluem.


# 40. BACKFILL NÃO É PRIORIDADE SOBRE DADOS NOVOS

Depois do V1:

1. garantir que conhecimento NOVO não continue sendo perdido;

2. depois recuperar progressivamente o passado.


# 41. VERSIONAMENTO

O Brain evoluirá.

Toda mudança estrutural precisa possuir:

SCHEMA_VERSION

KNOWLEDGE_MODEL_VERSION.

Não destruir conhecimento antigo em migração silenciosa.


# 42. SEGURANÇA

Este é potencialmente um ativo estratégico.

Planejar:

controle de acesso;

auditoria;

backup;

restauração;

integridade;

exportação;

proteção contra alteração indevida;

separação de dados sensíveis;

future multi-country isolation.


# 43. PREPARAR EAME

O nome atual é:

ITALIAN AGRO BRAIN.

Mas não criar arquitetura impossível de expandir.

No futuro poderemos possuir:

ITALIAN AGRO BRAIN

FRENCH AGRO BRAIN

SPANISH AGRO BRAIN

etc.

e eventualmente:

EAME AGRO KNOWLEDGE.

Não implementar isso agora.

Apenas não fechar a arquitetura.


# 44. NÃO TRANSFORMAR O BRAIN EM MAIS UM LLM

O conhecimento NÃO mora no modelo.

Modelos são consumidores e produtores controlados de inferência.

Se amanhã trocarmos:

GPT

Claude

DeepSeek

por outros modelos,

o ITALIAN AGRO BRAIN deve continuar existindo intacto.


# 45. PROVA DE VALOR

O piloto precisa comparar:

MODO ANTIGO:

buscar arquivos
→ recuperar contexto
→ LLM responder.

VERSUS:

ITALIAN AGRO BRAIN
→ recuperar conhecimento estruturado
→ evidências
→ LLM responder.

Medir:

precisão;

cobertura;

rastreabilidade;

tempo;

tokens;

custo;

capacidade histórica;

contradições;

NÃO SEI correto.


# 46. O QUE NÃO FAZER

NÃO:

jogar tudo em embeddings;

criar um Neo4j enorme sem necessidade;

duplicar o acervo;

guardar respostas soltas de GPT como fatos;

inventar conhecimento faltante;

alterar Collection inteira;

parar missões atuais;

misturar inference com evidence;

usar resumo como verdade canônica;

criar arquitetura paralela à identidade RAW.


# 47. ENTREGÁVEIS DO SINTONIA LAB

O estudo deve devolver:

IAB_ARCHITECTURE_STUDY.md

contendo:

1. estado atual relevante do Sintonia;

2. problemas;

3. benchmark;

4. três análises independentes;

5. divergências dos modelos;

6. red team;

7. arquitetura recomendada;

8. posição do Brain no fluxo;

9. alterações necessárias na Collection;

10. alterações necessárias na Sala;

11. alterações necessárias na Intelligence;

12. modelo de conhecimento;

13. tecnologia mínima;

14. custo estimado;

15. riscos;

16. plano de piloto;

17. critérios de sucesso.


# 48. ENTREGÁVEIS DA ENGENHARIA

Após aprovação arquitetural:

contrato V1;

schema V1;

Bíblia IAB;

System Map atualizado;

migrations;

writer;

reader/query layer;

testes;

canary;

backfill pilot;

métricas.


# 49. GATE

O primeiro grande gate deve responder:

ITALIAN_AGRO_BRAIN_CONCEPT_VALID = YES/NO

OBSERVED_DERIVED_SEPARATED = YES/NO

RAW_IDENTITY_REUSED = YES/NO

PROVENANCE_END_TO_END = YES/NO

TEMPORAL_MODEL_VALID = YES/NO

GEOGRAPHY_MODEL_VALID = YES/NO

LOW_STORAGE_OVERHEAD = YES/NO

HISTORICAL_CANARY = PASS/FAIL

KNOWLEDGE_RETRIEVABLE = YES/NO

CLAIM_TO_EVIDENCE = PASS/FAIL.


# 50. HARD STOP

Não transformar imediatamente uma ideia estratégica em migração gigante.

Primeiro medir.

Depois estudar.

Depois provar pequeno.

Depois expandir.


# 51. RESULTADO QUE QUERO NO FUTURO

Quero poder entrar no Sintonia e perguntar:

“Me conte a história completa dessa doença na Itália.”

“Mostre como ela se comportou no Veneto.”

“Compare os últimos cinco anos.”

“O que geralmente aconteceu antes de grandes surtos?”

“O que está diferente agora?”

“Quais produtos estavam disponíveis em cada período?”

“Quais pesquisadores falaram disso?”

“Quais são as evidências?”

E o Sintonia responder usando ANOS DE CONHECIMENTO ACUMULADO, não apenas os documentos encontrados naquela busca.


# 52. PRINCÍPIO FINAL

O arquivo é memória bruta.

O fato é conhecimento observado.

A relação organiza conhecimento.

O histórico cria contexto.

A Intelligence cria entendimento.

O ITALIAN AGRO BRAIN deve preservar tudo isso sem confundir uma coisa com a outra.


# FRASE CANÔNICA DO PROJETO

ITALIAN AGRO BRAIN NÃO É UM DEPÓSITO DE DOCUMENTOS.

É A MEMÓRIA AGRONÔMICA E HISTÓRICA ESTRUTURADA DO SINTONIA SOBRE A AGRICULTURA ITALIANA.


# EXECUTAR AGORA

1. medir o estado real do Git;

2. preservar trabalhos atuais;

3. criar linha paralela IAB;

4. encomendar o estudo ao SINTONIA LAB;

5. receber a triangulação dos três modelos;

6. red team;

7. apresentar arquitetura;

8. iniciar piloto somente após contrato mínimo;

9. assim que o piloto passar, começar a registrar conhecimento novo;

10. não parar o restante do Sintonia.


Ao final desta primeira etapa, entregar:

IAB_STATUS =

LAB_STUDY =

MODELS_USED =

CURRENT_GIT_HEAD =

PROPOSED_POSITION_IN_PIPELINE =

COLLECTION_CHANGES_REQUIRED =

INTELLIGENCE_CHANGES_REQUIRED =

PROPOSED_STORAGE_MODEL =

ESTIMATED_BYTES_PER_ITEM =

FIRST_CANARY =

DOCUMENTATION_CHANGES =

NEXT_SAFE_STEP =


E explique também em palavras simples.