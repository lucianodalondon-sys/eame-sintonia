# DAILY KNOW-HOW — 2026-09-13 — CARDS, GOVERNANÇA E CONTROL PLANE

Este arquivo pertence à trilha canônica `know-how/daily/`. Registra somente o delta durável desta decisão; **não cria um segundo KNOW-HOW** e não substitui `SINTONIA-EAME-KNOW-HOW.md`, as Bíblias, contratos, o System Map, o código, o runtime ou as provas.

> **ANTES DE QUALQUER TRABALHO SOBRE CARDS NO SYSTEM MAP, LER ESTE DELTA JUNTO DAS SEÇÕES `CARD NÃO É FILE` E `CARD CONTRACT / CARD FACTORY` DO KNOW-HOW CANÔNICO.**

## CONTEXTO

O Know-how já estabelece:

```text
CARD != FILE
DECLARED != OBSERVED
ONE CONCEPT -> ONE OWNER
```

Também já usa `CONTROL PLANE` no sentido **operacional interno da Collection**:

```text
COLLECTION EXECUTION CONTROL PLANE
ENTRADA -> PEDIDO -> ORQUESTRADOR -> EXECUTOR
```

Um benchmark arquitetural posterior, comparando padrões de governança, catálogo, ownership, lineage e observabilidade usados em plataformas como Databricks/Unity Catalog, Snowflake Horizon, Palantir Foundry, DataHub, OpenMetadata, Atlan, Backstage, Dagster e dbt, amadureceu uma segunda necessidade: o SINTONIA também precisa representar explicitamente **quem governa a máquina**, sem misturar isso com o fluxo operacional.

## DELTA DURÁVEL

### 1 · NÃO SOBRECARREGAR `CONTROL PLANE`

Há duas camadas diferentes e elas não podem receber o mesmo significado silenciosamente.

```text
PROJECT / GOVERNANCE CONTROL PLANE
!=
COLLECTION EXECUTION CONTROL PLANE
```

O primeiro governa a máquina. O segundo coordena uma execução dentro da Collection.

Para evitar ambiguidade, usar preferencialmente:

```text
GOVERNANCE PLANE / PROJECT CONTROL PLANE
```

para a camada superior de governo do projeto.

### 2 · CARD CONTINUA SENDO RESPONSABILIDADE, NÃO ARQUIVO

A lei permanece:

```text
CARD != FILE
```

Card representa conceito/responsabilidade arquitetural. Arquivo é implementação, contrato, prova, store, adapter, workflow ou outro suporte possível desse conceito.

Um card não nasce porque existe um arquivo. Um arquivo não ganha responsabilidade arquitetural apenas porque o scanner o encontrou.

### 3 · TODO CARD TEM DUAS FACES: DECLARED E OBSERVED

Separar obrigatoriamente:

```text
DECLARED
- propósito
- owner
- pergunta que possui
- inputs/outputs esperados
- contratos
- relações esperadas

OBSERVED
- código realmente encontrado
- relações realmente medidas
- runtime/evidência
- última prova
- estado observado
```

Regra:

```text
DECLARED != OBSERVED
DECLARED EDGE != OBSERVED EDGE
```

Nenhuma declaração promove runtime por desenho.

### 4 · EXISTEM CARDS OPERACIONAIS E CARDS DE GOVERNANÇA

Cards operacionais representam peças que fazem trabalho da máquina, por exemplo:

```text
COLLECTION
ORCHESTRATOR
EXECUTOR
ADMISSION
WAITING ROOM
INTELLIGENCE
DELIVERY
```

Cards de governança representam peças que comandam, restringem, documentam ou validam a máquina, por exemplo:

```text
BIBLE
CONTRACT
INSTRUCTION
DECISION LOG
KNOW-HOW
REGISTRY
VALIDATOR
HANDOFF
OBSERVER
```

**Governança não é etapa do fluxo de dados.**

Uma Bíblia não recebe um documento RAW e não entrega um Structured. Ela governa componentes que fazem isso.

### 5 · RELAÇÃO DE GOVERNANÇA NÃO É DATA FLOW

O vocabulário de edges precisa preservar diferenças semânticas. Quando aplicável, distinguir:

```text
GOVERNS
CONSTRAINS
REFERENCES
IMPLEMENTS
VALIDATES
OBSERVES
GENERATES
SUPERSEDES

CONTROL
DATA
READ
WRITE
PROOF
```

Nunca representar `BIBLE -> COMPONENT` como `DATA` apenas para poder desenhar uma seta.

Cada relação precisa dizer pelo menos:

```text
EDGE_TYPE
EDGE_STATE = DECLARED | OBSERVED
PROOF_KIND
PROOF_LOCATION
```

### 6 · O SYSTEM MAP DEVE CONSEGUIR MOSTRAR TRÊS PLANOS DA MESMA MÁQUINA

Direção arquitetural:

```text
GOVERNANCE / PROJECT CONTROL PLANE
            ↓ governa
OPERATIONAL PLANE
            ↓ executa/produz
EVIDENCE PLANE
```

Onde:

```text
GOVERNANCE PLANE
= Bíblias, contratos, instruções, decisões, Know-how, registry, governance gates

OPERATIONAL PLANE
= Collection -> Sala de Espera -> Intelligence -> Delivery/Casco

EVIDENCE PLANE
= Git, código, banco, runtime, testes, runs, provas e artefatos gerados
```

O System Map observa os três.

```text
SYSTEM MAP != AUTHORITY
SYSTEM MAP OBSERVES THE MACHINE
SYSTEM MAP DOES NOT DEFINE THE ARCHITECTURE
```

### 7 · NAVEGAÇÃO VERTICAL DEVE SER POSSÍVEL

Para um componente real, o mapa deve conseguir responder verticalmente, quando houver prova:

```text
BIBLE
  ↓ GOVERNS
CONTRACT / LAW
  ↓ IMPLEMENTED BY
COMPONENT / CARD
  ↓ IMPLEMENTED IN
CODE
  ↓ VALIDATED BY
TEST
  ↓ OBSERVED IN
RUNTIME / EVIDENCE
```

Se um elo não puder ser provado:

```text
UNKNOWN
```

Melhor um buraco verdadeiro que uma seta inventada.

### 8 · UMA REPRESENTAÇÃO, MÚLTIPLAS LENTES

Direção de visualização para o mesmo System Map:

```text
MACHINE
GOVERNANCE
PROOF
STATUS
HISTORY
```

Uma lens muda o que se destaca. Não muda a verdade subjacente e não cria um segundo mapa.

### 9 · CARD DE GOVERNANÇA TAMBÉM OBEDECE ONE CONCEPT -> ONE OWNER

Exemplos:

```text
Collection Bible owns Collection law.
Intelligence Bible, quando existir e for provada, owns Intelligence law.
Delivery/Casco Bible, quando existir e for provada, owns Delivery/Casco law.
Know-how owns durable learned knowledge, não lei executável.
System Map owns no architecture law; ele representa/mede.
Handoff owns contexto operacional de retomada, não constituição.
```

Não permitir dois cards `CANONICAL` possuindo o mesmo conceito sem decisão explícita de supersession.

### 10 · CARD DE GOVERNANÇA NÃO PODE SER INVENTADO NA UI

Fluxo correto:

```text
AUTORIDADE / CONTRATO / METADATA EXISTE NO REPO
        ↓
SCANNER + DECLARED METADATA + PROVAS
        ↓
SYSTEM MAP REPRESENTA
```

Nunca:

```text
DESENHAR CARD NO MAPA
        ↓
ASSUMIR QUE A AUTORIDADE EXISTE
```

O mapa não pode ser usado para fabricar o Control Plane que deveria apenas observar.

## CONSEQUÊNCIA IMEDIATA PARA MISSÕES PARALELAS DO SYSTEM MAP

Antes de alterar card schema, card factory, tipos de card, edge schema ou layout dos cards:

1. reler as seções canônicas `CARD NÃO É FILE` e `CARD CONTRACT / CARD FACTORY`;
2. ler este delta;
3. preservar `DECLARED != OBSERVED`;
4. não confundir Governance Plane com o control plane operacional da Collection;
5. não representar relações de governo como DATA/CONTROL por conveniência visual;
6. não criar cards de Bíblia, contrato, Know-how ou handoff sem medir primeiro que esses objetos existem e qual é o owner real;
7. se houver conflito com lei/Bíblia/contrato já vigente, parar e reportar a colisão em vez de criar uma terceira definição.

## O QUE NÃO MUDOU

- nenhum card foi criado nesta atualização;
- nenhum schema foi alterado;
- nenhum edge foi alterado;
- nenhum System Map foi regenerado;
- nenhuma Bíblia foi criada ou alterada;
- nenhuma implementação de Collection, Intelligence ou Delivery foi tocada;
- o System Map continua observador, não autoridade.

## PROVA / ORIGEM DO APRENDIZADO

Este delta combina:

```text
1. leis já registradas no Know-how canônico:
   CARD != FILE
   DECLARED != OBSERVED
   ONE CONCEPT -> ONE OWNER

2. aprendizado do benchmark arquitetural externo realizado em 2026-09-13:
   separação de governance/control plane, operational/data plane,
   ownership, lineage, applied/runtime state e múltiplas lenses
   sem múltiplas fontes de verdade.

3. necessidade concreta do SINTONIA:
   missão paralela do System Map chegará em breve à evolução dos cards;
   este conhecimento não pode ficar apenas no chat.
```

O benchmark orienta a direção; **não substitui as autoridades do repositório**.

## PRÓXIMO PASSO MÍNIMO

Quando a missão paralela chegar à etapa dos cards, reavaliar o estado real do Git e reconciliar este delta com o card schema/edge schema então vigentes antes de qualquer implementação.

`KNOW_HOW_DELTA = ATUALIZADO`

HARD STOP.
