# ITALIAN AGRO BRAIN — DECISÕES DO PROPRIETÁRIO APÓS STUDY V1

Recebi o resultado do estudo executado pelo SINTONIA LAB com triangulação dos três motores.

As seguintes decisões estão APROVADAS.

Não reabrir essas perguntas sem nova evidência concreta.


# DECISÃO 1 — ARQUITETURA

ACEITO a conclusão do estudo:

O ITALIAN AGRO BRAIN NÃO deve virar um sistema ou banco paralelo.

Ele deve aproveitar a arquitetura canônica existente e preencher/extender estruturas dentro do PostgreSQL atual.

Princípio:

UMA VERDADE CANÔNICA.

Não criar:

POSTGRES DO SINTONIA

+

POSTGRES/BANCO DO BRAIN

com os mesmos fatos duplicados.


O Italian Agro Brain será uma CAPACIDADE DE MEMÓRIA DE CONHECIMENTO dentro do sistema existente.


# DECISÃO 2 — TRÊS CLASSES

Aceito a descoberta do LAB de que precisamos de três classes principais, e não apenas observado × derivado.


## A. SOURCE / OBSERVED KNOWLEDGE

O que uma fonte afirmou ou documentou.


## B. OFFICIAL / AUTHORITATIVE KNOWLEDGE

Conhecimento normativo/oficial.

Exemplos:

registro;

autorização;

rótulo;

status regulatório;

documento oficial;

aprovação relevante.


## C. DERIVED KNOWLEDGE

Resultado produzido pelo Sintonia através de:

cruzamento;

regra;

modelo;

estatística;

Intelligence;

inferência.


Essas três categorias NÃO podem ser misturadas.


# DECISÃO 3 — VOCABULÁRIO AGRÍCOLA

O dono canônico do vocabulário será:

ITALIAN AGRO BRAIN

através de um componente lógico chamado provisoriamente:

CANONICAL AGRO VOCABULARY REGISTRY.


Isso NÃO significa criar sistema novo.

Deve utilizar a estrutura mínima adequada no PostgreSQL existente.


O registry deve possuir identidade canônica para coisas como:

CROP

PEST

DISEASE

PATHOGEN

WEED

ACTIVE_INGREDIENT

MOLECULE

PRODUCT

COMPANY

RESEARCHER

INSTITUTION

LOCATION

REGION

PROVINCE

COMUNE

e outras entidades quando necessárias.


Collection NÃO cria sua própria taxonomia.

Intelligence NÃO cria sua própria taxonomia.

Casco NÃO cria sua própria taxonomia.

Todos referenciam a mesma identidade.


# ALIASES

Uma entidade pode possuir diversos nomes.

Exemplo conceitual:

CANONICAL ENTITY:
X

ALIASES:

nome italiano

nome inglês

nome português

nome científico

sigla

grafias alternativas.


Onde houver identificador externo oficial/confiável:

preservar referência.

Não reinventar códigos desnecessariamente.


# DECISÃO 4 — SOURCE ASSERTION

AUTORIZO formalmente que:

SOURCE ASSERTION

ou nome canônico equivalente encontrado na arquitetura existente

passe a ser uma peça oficial do fluxo de Collection.


Mas sua fronteira é rígida.


SOURCE ASSERTION significa:

“O QUE ESTA FONTE AFIRMOU?”


Não:

“O QUE O SINTONIA CONCLUIU?”


Collection pode produzir uma unidade estruturada que preserve:

SOURCE

RAW_OBSERVATION_ID

DOCUMENT / CONTENT IDENTITY EXISTENTE

SPAN/TEXTO DE SUPORTE

IDIOMA

PUBLICATION TIME quando comprovado

FACT TIME quando explicitamente comprovado

FACT LOCATION quando explicitamente comprovado

entidades reconhecidas

versão do extrator

proveniência.


# REGRA CRÍTICA

Nenhuma afirmação pode existir sem evidência localizada no documento.

Se o sistema não consegue apontar onde a fonte sustentou a afirmação:

NÃO ADMITIR COMO SOURCE ASSERTION.


# LITERALIDADE

O estudo identificou a necessidade de a evidência estar efetivamente presente no conteúdo.

Preservar:

EVIDENCE SPAN

ou mecanismo equivalente que permita reencontrar exatamente o suporte documental.

Não permitir paráfrase de LLM virar evidência.


# DECISÃO 5 — KNOWLEDGE TIME

NÃO vamos usar apenas um conceito de:

“O que sabíamos naquela data”.

Precisamos preservar DOIS.


## A. KNOWLEDGE_STATE_AT

Pergunta:

“O que o Sintonia realmente sabia naquela data?”

Considerar somente conhecimento que já havia sido:

coletado;

admitido;

organizado;

disponibilizado

até aquele momento, conforme contrato definido.


## B. WORLD_STATE_AT

Pergunta:

“O que hoje sabemos que estava acontecendo naquela data?”

Pode utilizar documento histórico descoberto posteriormente.


EXEMPLO:

Documento de maio de 2024 só foi coletado em 2027.

Ele pode alterar:

WORLD_STATE_AT(2024)

mas NÃO pode alterar retrospectivamente:

KNOWLEDGE_STATE_AT(2024).


Essa distinção deve ser estrutural e não apenas textual.


# DECISÃO 6 — DATASET OURO HUMANO

AUTORIZO o primeiro dataset manual de validação.

Objetivo:

aproximadamente 12 documentos inicialmente;

podendo chegar a aproximadamente 20 conforme necessidade de validação.


Não usar esse conjunto para treinar a resposta que será avaliada.

Ele é referência humana.


# CANÁRIO V1

Usar:

MOSCA DA OLIVEIRA
×
OLIVEIRA
×
PUGLIA.


Fontes inicialmente identificadas:

ARIF

APOL

e demais evidências válidas encontradas para o mesmo recorte.


O LAB já descartou corretamente a proposta inicial de míldio quando confrontou a sugestão dos modelos com o acervo real.

Essa disciplina deve continuar:

DADOS REAIS VENCEM IDEIAS DOS MODELOS.


# 6 PERGUNTAS FIXAS

O piloto manual deve definir seis perguntas fixas ANTES da implementação automática.

Sugestão de estrutura:

1. O QUE aconteceu?

2. ONDE aconteceu?

3. QUANDO aconteceu?

4. QUAL entidade/cultura/praga/doença estava envolvida?

5. O QUE exatamente cada fonte afirmou?

6. QUAL evidência documental sustenta cada resposta?


O LAB pode ajustar a formulação final, mas não deve alterar as perguntas depois de ver o resultado para fazer o teste passar.


# REVISÃO HUMANA

A prova final desse gold set deve possuir revisão humana.

Preferencialmente:

competência agronômica

+

capacidade de interpretar italiano técnico.


IA pode:

auxiliar;

preparar;

sugerir mappings.


IA NÃO pode ser a única autoridade que cria e ao mesmo tempo aprova o gold standard.


# CÓDIGOS INTERNACIONAIS / NOMES

Para entidade que necessite tradução/mapeamento:

preservar separadamente:

RAW_NAME_FROM_SOURCE

CANONICAL_ENTITY_ID

CANONICAL_NAME

ALIAS

LANGUAGE

EXTERNAL_REFERENCE/CODE quando houver.


Nunca apagar o nome original da fonte depois da normalização.


# DECISÃO 7 — HISTÓRICO

ACEITO o diagnóstico:

o acervo atual NÃO possui profundidade histórica suficiente para provar casos de cinco anos.

Não tratar isso como falha do Brain.


Portanto:

HISTORICAL_DEPTH = CURRENTLY_INSUFFICIENT


Registrar isso como gap de Collection/acervo.


Não fazer o Brain inventar história ausente.


# FUTURO

Depois que o Brain V1 estiver comprovado:

planejar uma missão separada de:

HISTORICAL BACKFILL.


Objetivo futuro:

buscar deliberadamente arquivos de anos anteriores para formar história agronômica.


NÃO iniciar uma coleta histórica gigante agora.


# DECISÃO 8 — POSIÇÃO NO FLUXO

Adotar provisoriamente, sujeito à validação de implementação:

SOURCE
↓
COLLECTION
↓
SALA / ADMISSION
↓
SOURCE ASSERTIONS
↓
KNOWLEDGE STRUCTURES
↓
INTELLIGENCE
↓
DERIVED KNOWLEDGE
↓
POTES / PRODUCTS
↓
CASCO


OFFICIAL / AUTHORITATIVE KNOWLEDGE entra por trilha própria adequada, mas converge para a mesma capacidade de consulta.


Não obrigar registros oficiais a fingirem que são observações fitossanitárias.


# DECISÃO 9 — TAMANHO

O estudo estimou aproximadamente:

~1 KB / KNOWLEDGE ITEM

a partir do estado real observado.


Não transformar estimativa em verdade permanente.

Criar métrica real:

AVERAGE_KNOWLEDGE_BYTES.


Medir no piloto.

Nosso objetivo continua:

MUITO CONHECIMENTO

POUCO ARMAZENAMENTO

SEM DUPLICAR CONTEÚDO BRUTO.


# DECISÃO 10 — BUG DO TRI-MODEL RUNNER

O defeito encontrado pelo próprio LAB precisa gerar correção permanente.

Houve interferência de uma execução simultânea de outro modelo/perfil na conferência da triangulação.

Não basta corrigir apenas o caso.


Criar identidade explícita para cada execução de modelo.


No mínimo registrar:

STUDY_RUN_ID

MODEL_RUN_ID

EXPECTED_MODEL

ACTUAL_MODEL

MODEL_PROVIDER

PROFILE/CONFIGURATION quando aplicável

STARTED_AT

FINISHED_AT

RESULT_ID/HASH.


# REGRA

Uma execução só conta na triangulação se:

EXPECTED_MODEL == ACTUAL_MODEL

e

MODEL_RUN_ID pertencer ao STUDY_RUN_ID correto.


Nunca inferir o motor pelo terminal, ordem de resposta ou perfil compartilhado.


# PARALELISMO

Execuções simultâneas devem ser isoladas suficientemente para que:

teste externo

benchmark paralelo

ou outra conversa

não possa ser contado como membro da triangulação atual.


Adicionar teste de regressão para isso.


# MODELOS

O Study V1 utilizou:

GPT-5.6 Sol

porque começou antes da alteração do motor.

Registrar isso historicamente.

Não reescrever o estudo dizendo que utilizou GPT-6.


A partir das próximas execuções, utilizar a configuração atual definida para o LAB e registrar ACTUAL_MODEL real em cada execução.


# AGORA — PRÓXIMA FASE

NÃO começar por migração grande.

Executar:

# IAB MANUAL CANARY V1


Sem Intelligence automática.

Sem LLM decidindo verdade.

Sem nova infraestrutura.

Sem Neo4j.

Sem novo banco.


Usar aproximadamente 12 documentos reais.


Construir manualmente as estruturas necessárias para:

MOSCA DA OLIVEIRA × OLIVEIRA × PUGLIA.


# OBJETIVO DO CANÁRIO

Responder:

Conseguimos representar corretamente o conhecimento contido nesses documentos usando estruturas pequenas e rastreáveis?


Testar especialmente:

SOURCE ASSERTION

OFFICIAL KNOWLEDGE quando houver

ENTITY

ALIAS

TIME

LOCATION

EVIDENCE

RELATION

CONTRADICTION quando houver.


# NÃO IMPLEMENTAR DERIVED KNOWLEDGE AINDA

Primeiro provar a memória do que as fontes disseram.

Depois provar Intelligence derivada.


# SAÍDA OBRIGATÓRIA

Ao terminar o canário manual, entregar:

CANARY = PASS / FAIL

DOCUMENTS =

SOURCE_ASSERTIONS =

CANONICAL_ENTITIES =

ALIASES =

RELATIONS =

EVIDENCE_LINKS =

UNRESOLVED_ENTITIES =

CONTRADICTIONS =

AVERAGE_BYTES_PER_KNOWLEDGE_ITEM =

QUESTIONS_CORRECT = X/6

HUMAN_REVIEW = PASS / FAIL

GAPS_FOUND =


# E PRINCIPALMENTE

Responder:

1. QUAL É O MENOR SCHEMA que representa isso sem perder informação importante?

2. O que já existe no banco que podemos reutilizar?

3. Quais são exatamente as 2 ou 3 “gavetas” novas necessárias?

4. O que NÃO precisamos construir?

5. Collection precisa mudar alguma coisa AGORA para não perder conhecimento futuro?

6. Qual é o contrato exato entre Collection → Source Assertions → Intelligence?


# HARD RULE

Não deixar a importância estratégica do ITALIAN AGRO BRAIN virar desculpa para aumentar a arquitetura.

O Brain ficará valioso pelo conhecimento acumulado.

Não pela quantidade de tecnologia usada para armazená-lo.


# FRASE CANÔNICA

ITALIAN AGRO BRAIN É A MEMÓRIA ESTRUTURADA DO QUE AS FONTES DISSERAM, DO QUE É OFICIAL E DO QUE O SINTONIA CONSEGUIU DERIVAR — SEM CONFUNDIR ESSAS TRÊS COISAS.


# EXECUTAR EM PARALELO

Não interromper:

Collection;

Intelligence;

Casco;

ou outras missões em andamento.


O Italian Agro Brain segue como linha paralela.


Ao final me dê também uma explicação simples.