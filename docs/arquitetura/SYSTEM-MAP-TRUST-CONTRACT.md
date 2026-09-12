# CONTRATO DE CONFIANÇA DO SYSTEM MAP

```
MISSAO        C-DESIGN-SYSTEM-MAP-TRUST-CONTRACT-V1
BRANCH        claude/dazzling-cerf-27a7v2
BASE MEDIDA   c828d1ac  (system-map, reconciliação)
DATA          2026-09-12
ESTADO        CONTRATO — nenhuma implementação nesta missão
```

> Este documento é **contrato, não implementação**. Ele diz o que o System Map
> **pode afirmar**, com que evidência, com que grau de certeza e com que frescura.
> As próximas missões obedecem-lhe. Ele não refatora nada.

**Dono da lei do mapa continua a ser [`AGENTS.md`](../../AGENTS.md).** Este ficheiro
não a repete: ele acrescenta o modelo de confiança que a lei ainda não tinha, e
aponta para ela sempre que ela já responde. Uma lei em dois sítios diverge.

---

## 0 · O QUE ESTE CONTRATO MEDE, E QUANDO

Todo número citado aqui foi medido em `c828d1ac` com os comandos ao lado. Um
número sem comando não entrou.

```bash
python3 system-map/scripts/reconciliacao_do_universo.py
python3 system-map/scripts/validate_system_map.py
python3 system-map/tests/test_reconciliacao_do_universo.py
```

| medida | valor | onde |
|---|---|---|
| nós do mapa | 160 | `state.generated.json · NODES[]` |
| arestas | 660 | `state.generated.json · EDGES[]` |
| universo visual da coleta | 65 (64 + 1) | `FAMILIES[].count` |
| pente fino | 48 incluídos, 17 excluídos | `pente-fino.generated.json` |
| arestas com `status = PROVEN` | 658 | `EDGES[].status` |
| arestas com `status = UNKNOWN` | 2 | `EDGES[].status` |
| nós com `status = PROVEN` | 59 | `NODES[].status` |
| executores com prova de execução | 2 de 57 | `provas-de-execucao.json · PROVADOS` |

---

## 1 · PRINCÍPIO FUNDAMENTAL

```
SYSTEM MAP OBSERVA.
SYSTEM MAP NÃO DEFINE A ARQUITETURA.
```

A arquitetura vem das autoridades do sistema: a Bíblia, os contratos, o código,
o banco, as corridas. O mapa **reúne e reconcilia evidências**. A interface é
**uma projeção** dessa evidência, nunca uma fonte dela.

Corolário operacional: nenhuma missão pode mover um cartão, criar uma aresta ou
mudar uma família **para fazer o mapa fechar uma conta**. Se a conta não fecha, o
que está errado é a medição ou a arquitetura — e as duas têm donos diferentes.

---

## 2 · MODELO DE VERDADE — QUATRO PLANOS QUE NÃO SE PROMOVEM

Cada plano responde a uma pergunta diferente. **Nenhum implica o seguinte.**

| plano | pergunta | quem responde |
|---|---|---|
| `DECLARED` | o sistema diz que isto **deveria** existir? | contratos, Bíblia, `architecture.declared.json` |
| `CODE` | existe implementação **capaz** de o fazer? | análise estática da árvore |
| `OBSERVED` | há evidência de que **aconteceu** de facto? | telemetria, ledger de corrida, banco, artefacto de corrida |
| `PROVEN` | a evidência **sustenta** a afirmação publicada? | a regra de suficiência da §11, aplicada à classe da afirmação |

```
DECLARED  →  CODE       PROIBIDO inferir
CODE      →  OBSERVED   PROIBIDO inferir
OBSERVED  →  PROVEN     PROIBIDO inferir
```

Cada plano tem valor próprio em `{YES, NO, UNKNOWN}`. **Os quatro coexistem.**
`DECLARED=YES · CODE=YES · OBSERVED=NO · PROVEN=NO` é um estado válido, comum, e
tem de poder ser publicado tal como é.

`OBSERVED=NO` e `OBSERVED=UNKNOWN` são estados **diferentes**: o primeiro diz «foi
procurado e não se encontrou», o segundo diz «ninguém procurou». Colapsá-los é a
forma mais barata de transformar cegueira em ausência.

### A tabela de promoção

| de | para | permitido por |
|---|---|---|
| `DECLARED=YES` | `CODE=YES` | nada. Só evidência de código. |
| `CODE=YES` | `OBSERVED=YES` | nada. Só evidência de execução. |
| `OBSERVED=YES` | `PROVEN=YES` | só a regra de suficiência da classe (§11 + §12) |
| qualquer | `UNKNOWN` | sempre permitido, e é o estado por omissão |

---

## 3 · AS LEIS QUE O CONTRATO INCORPORA

Estas já existem no SINTONIA. O contrato não as reescreve: **vincula-se a elas**.

```
CAN DO                != DID DO
MODULE EXISTS         != EDGE EXISTS        != FLOW EXISTS
DECLARED EDGE         != OBSERVED EDGE
UNKNOWN               != NO
NOT_OBSERVED          != DOES_NOT_EXIST
STALE                 != CURRENT
TEST EXISTS           != RUNTIME EXECUTED
GENERATED             != PROVEN
ERROR != REJECTED != UNKNOWN != NOT_RUN != REUSED
ONE CONCEPT           →  ONE OWNER
```

E as que a reconciliação acrescentou, já em `AGENTS.md`:

```
CONTADO PELA FAIXA    != DESENHADO NA TELA
ÓRFÃO NA VISTA        != ÓRFÃO NO GRAFO
FAMÍLIA               != TERRITÓRIO
```

---

## 4 · MODELO CANÓNICO DE ENTIDADE

Uma entidade do System Map é uma coisa com **identidade estável**.

### Os três tipos de campo, e por que a distinção é a metade do contrato

| classe | campos | regra |
|---|---|---|
| `IDENTITY` | `ENTITY_ID` · `ENTITY_SPECIES` | **nunca** muda sem ser uma entidade nova. É por aqui que se junta evidência. |
| `CLASSIFICATION` | `FAMILY` · `TERRITORY` · `KIND` · `ROLE` · `LANE` · `NIVEL` · `PAIS` | responde «que tipo de coisa é». **Muda sem a entidade mudar.** |
| `PRESENTATION` | `NAME` · `ICON` · `X` · `Y` · `VIEWS` · `ORDEM` | é como aparece. **Nunca é identidade.** |

**`OWNER`** é campo próprio e obrigatório: quem responde por esta entidade existir
e estar certa. Não é identidade nem classificação — é responsabilidade.

### A regra que fecha o defeito medido

> **Nome visual, posição, família e território NÃO são identidade.**

Provado nesta árvore: em `1766c232` treze peças mudaram de `FAMILY` sem mudar de
`ENTITY_ID`. Duas contagens publicadas moveram-se; a terceira não. Se `FAMILY`
fosse identidade, teriam sido treze entidades novas, e não eram.

Provado também: `Z-GUARDA` e `Z-ESPERA` publicam o mesmo `NAME` («A SALA DE
ESPERA») em famílias diferentes. **Quem lê a tela vê o nome.** Nome não junta
evidência; `ENTITY_ID` junta.

### Campos obrigatórios de uma entidade publicada

```
ENTITY_ID          identidade, estável, único no seu universo
ENTITY_SPECIES     §5
OWNER              quem responde por ela
NAME               apresentação
FAMILY             classificação
TERRITORY          classificação
KIND               classificação
ROLE               classificação — §5.1
DECLARED           YES | NO | UNKNOWN
CODE               YES | NO | UNKNOWN
OBSERVED           YES | NO | UNKNOWN
PROVEN             YES | NO | UNKNOWN
EVIDENCE[]         §6
FRESHNESS          §9
```

---

## 5 · ESPÉCIES — A PALAVRA «CARD» DEIXA DE EXISTIR SOZINHA

Cinco espécies medidas nesta árvore. Os nomes canónicos são os que já vivem em
`SYSTEM-MAP-UNIVERSE-RECONCILIATION-V1.json` e na prova que o defende: renomeá-los
criaria um segundo vocabulário para o mesmo inventário.

| `ENTITY_SPECIES` | o que conta | contagem | dono |
|---|---|---|---|
| `ARCHITECTURE_NODE` | peça **declarada** à mão por gente | 133 | `architecture.declared.json` |
| `SYSTEM_MAP_VISUAL_CARD` | o retângulo que a tela desenha | 160 | `generate_system_map.py` |
| `COLLECTION_INTERNAL_PIECE` | peça da coleta que recebe as quatro perguntas | 48 | `pente_fino_da_coleta.py` |
| `PORTAL_TOOL_CARD` | ferramenta do portal italiano | 11 | `censo_cards_sensores.py` |
| `VISUAL_ONLY_BLOCK` | retângulo de família ou de zona | 28 | `generate_system_map.desenhar()` |

Relações medidas, não assumidas:

```
ARCHITECTURE_NODE          ⊂  SYSTEM_MAP_VISUAL_CARD   (133 de 160; 27 sintetizados por medição)
COLLECTION_INTERNAL_PIECE  ⊂  SYSTEM_MAP_VISUAL_CARD   (48 de 65 do universo da coleta)
PORTAL_TOOL_CARD           ≡  os 11 nós de Z-TELAS     (provado por NOME; os ids diferem)
PORTAL_TOOL_CARD           ∩  universo da coleta = 0
VISUAL_ONLY_BLOCK          ∩  qualquer das outras = 0  (não é peça; é fundo)
```

### 5.1 · `ROLE` é classificação, não espécie

Uma peça que **mede** a coleta é um `SYSTEM_MAP_VISUAL_CARD` como qualquer outro:
mesma identidade, mesmo universo, mesma espécie. O que a distingue é o papel.

```
ROLE ∈ { OPERATIONAL_STEP, MEASUREMENT_INSTRUMENT, CONTRACT_OR_RULE,
         STORAGE, SURFACE, DISPATCH_ENTRYPOINT, PROOF, UNKNOWN }
```

**`MEASUREMENT_ARTIFACT` não é uma espécie de card.** É um artefacto de evidência
(§13). Confundir os dois seria repetir, num nível acima, o erro que esta missão
acabou de separar: o instrumento que mede não é da mesma espécie que o medido,
mas também não é uma espécie visual nova — é um **papel**.

### 5.2 · `CARD_COUNT` sozinho deixa de existir

> **Proibido publicar uma contagem sem `ENTITY_SPECIES` e `UNIVERSE_ID`.**

`«65 cards»` é uma frase ilegal sob este contrato. Legal é:
`65 SYSTEM_MAP_VISUAL_CARD em SYSTEM_MAP_COLLECTION_WAITING_UNIVERSE, regra family ∈ {F-COLETA, F-ESPERA}`.

---

## 6 · MODELO CANÓNICO DE ARESTA

Uma aresta é **entidade verificável**, com identidade própria.

```
EDGE_ID           identidade estável: hash(FROM, TO, RELATION_TYPE)
FROM_ENTITY_ID
TO_ENTITY_ID
RELATION_TYPE     §6.1
DECLARED          YES | NO | UNKNOWN
CODE              YES | NO | UNKNOWN
OBSERVED          YES | NO | UNKNOWN
PROVEN            YES | NO | UNKNOWN
EVIDENCE[]        §7
LAST_OBSERVED_RUN RUN_ID | UNKNOWN
FRESHNESS         §9
```

`EDGE_ID` inclui `RELATION_TYPE` de propósito: A **importa** B e A **corre** B são
duas afirmações diferentes sobre o mesmo par, e podem ter planos de prova
diferentes.

### 6.1 · `RELATION_TYPE` — só o que existe

**Medidos nesta árvore**, pelo scanner, com ficheiro e linha:

| tipo | n | o que a evidência prova |
|---|---|---|
| `READS` | 332 | `CODE` |
| `IMPORTS` | 210 | `CODE` |
| `RUNS` | 64 | `CODE` (que existe quem mande correr, não que tenha corrido) |
| `WRITES` | 14 | `CODE` |

**Declarados sem tipo medido** (40 arestas, `raw_type = null`): `PRODUZ`,
`ABRE_O_CANAL`, `FEEDS`, `ENTREGA_A_LISTA`, `DERIVA_TEXTO`, `DERIVA_TEXTO_A_MAO`,
`ALIMENTA`, `VIAJA_POR`. São **rótulos narrativos de declaração**, e o contrato
classifica-os assim: `DECLARED=YES`, `CODE=UNKNOWN` até alguém os normalizar num
tipo medido.

**Reservados, proibidos até haver evidência:** `CALLS`, `PRODUCES`, `DERIVES`,
`PERSISTS`, `ADMITS`, `CONSUMES`, `TESTS`, `PROVES`. Criar o tipo antes da medição
seria desenhar a seta e chamar-lhe medição.

> Um `RELATION_TYPE` novo só entra no contrato acompanhado do medidor que o emite
> e da classe de evidência que o sustenta.

### 6.2 · `categoria` é um segundo eixo, e continua a ser

`PROOF · READ · CODE · DATA · CONTROL · RULE · WRITE` respondem «o que atravessa a
aresta». `RELATION_TYPE` responde «que relação é». São ortogonais e não se fundem.

---

## 7 · MODELO DE EVIDÊNCIA

```
EVIDENCE_ID           identidade da evidência
EVIDENCE_TYPE         §8
SOURCE                ficheiro:linha · run_id · query · artefacto
OWNER                 quem produziu a evidência
ASSERTION_SUPPORTED   que afirmação esta evidência sustenta, e em que plano
MEASURED_AT           quando foi medida
TREE_FINGERPRINT      que árvore foi medida
RUN_ID                quando aplicável; UNKNOWN é resposta válida
ENVIRONMENT           quando aplicável: rede? pago? produção? banco?
FRESHNESS             §9
LIMITATIONS           o que esta evidência explicitamente NÃO prova
```

**`LIMITATIONS` é obrigatório e não pode ser vazio.** Uma evidência que não
declara o seu limite é uma evidência que será usada fora dele.

Uma afirmação pode ter várias evidências. Uma evidência pode sustentar várias
afirmações **apenas quando `ASSERTION_SUPPORTED` o disser explicitamente para
cada uma**. Emprestar evidência entre afirmações é o mecanismo pelo qual `CODE`
vira `OBSERVED` sem que ninguém decida.

### 7.1 · O EMPRÉSTIMO DE EVIDÊNCIA, MEDIDO

> **UMA LINHA NÃO PROVA DUAS AFIRMAÇÕES DIFERENTES SÓ POR ESTAR PERTO DAS DUAS.**

Medido em `c828d1ac`, sobre 1160 linhas de evidência distintas:

| | |
|---|---|
| linhas usadas por mais de uma aresta | 55 |
| arestas envolvidas | 52 de 660 |
| linhas que sustentam `RELATION_TYPE` **diferentes** | 37 |

O caso mais claro, e ele é literal:

```
coleta/comunicacao_coleta.py:57
  import apify_pool as ap        # noqa: E402 — dono único da rotação de chave

sustenta, ao mesmo tempo:
  C-APIFY-POOL → C-COMUNICACAO   IMPORTS        ← isto, a linha prova
  C-APIFY-POOL → V-FACEBOOK      ABRE_O_CANAL   ← isto, não prova
  C-APIFY-POOL → V-INSTAGRAM     ABRE_O_CANAL   ← isto, não prova
  C-APIFY-POOL → V-LINKEDIN      ABRE_O_CANAL   ← isto, não prova
```

Um `import` prova que o módulo é importado. Não prova que ele abre o Facebook,
nem o Instagram, nem o LinkedIn — e muito menos prova as três coisas com a mesma
linha. Sob este contrato, `ASSERTION_SUPPORTED` teria de dizer, para cada uma,
que afirmação a linha sustenta; e para três delas não diria nada.

---

## 8 · HIERARQUIA DE EVIDÊNCIA — NÃO É UMA ESCADA

As classes respondem a perguntas diferentes. Não há ordem linear.

| `EVIDENCE_TYPE` | prova | **nunca** prova |
|---|---|---|
| `CANONICAL_CONTRACT` | `DECLARED` | `CODE`, `OBSERVED` |
| `GIT_TREE` | que árvore foi medida; existência de ficheiro | `CODE` correto, `OBSERVED` |
| `STATIC_CODE_ANALYSIS` | presença, referência, import, possibilidade de escrita | `OBSERVED`, `LIVE` |
| `AST` | `CODE` com precisão sintáctica | `OBSERVED`, `LIVE` |
| `WORKFLOW` | que existe quem mande correr | que correu |
| `TEST` | comportamento observado **naquele teste, ambiente e versão** | produção, `LIVE` |
| `POSTGRESQL` | `OBSERVED` **naquele ambiente** | `LIVE`, se o banco não for o de produção |
| `RUNTIME_TRACE` | `OBSERVED` da corrida que a emitiu | corridas que não emitiram |
| `GENERATED_ARTIFACT` | o que o gerador mediu, na árvore que carimbou | qualquer coisa que o gerador não mediu |
| `LIVE_OBSERVATION` | `OBSERVED` em produção, na janela medida | fora da janela |

```
AST prova CODE.                      AST não prova OBSERVED.
Um PostgreSQL descartável prova OBSERVED naquele ambiente. Não prova LIVE.
Um teste verde prova o teste.        Não prova produção.
```

---

## 9 · MODELO DE FRESCURA — SEIS RELÓGIOS, NUNCA UM

Regenerar o mapa hoje **não torna atual** uma execução de terça-feira.

| relógio | pergunta | prova |
|---|---|---|
| `SOURCE_TREE_FRESHNESS` | o mapa é desta árvore? | `SOURCE_TREE_FINGERPRINT` vs impressão de agora |
| `GENERATED_ARTIFACT_FRESHNESS` | este artefacto mediu esta árvore? | carimbo do artefacto |
| `STATIC_ANALYSIS_FRESHNESS` | a análise correu sobre este código? | árvore medida pelo scanner |
| `RUNTIME_EVIDENCE_FRESHNESS` | a corrida observada é de que versão? | `TREE_FINGERPRINT` da corrida |
| `DATABASE_EVIDENCE_FRESHNESS` | a leitura do banco é de quando, e de que ambiente? | timestamp + `ENVIRONMENT` |
| `LIVE_EVIDENCE_FRESHNESS` | a observação em produção é de quando? | janela declarada |

Estados: `CURRENT` · `STALE` · `UNVERIFIABLE` · `UNKNOWN`.

**`UNVERIFIABLE` é obrigatório** e não é sinónimo de `UNKNOWN`: diz que o carimbo
existe mas **não pode ser verificado por construção**. Medido nesta árvore: quatro
artefactos carimbam apenas SHA de commit, e um ficheiro commitado nunca nomeia o
commit que o contém — o carimbo nasce a apontar para o anterior.

```
sources.generated.json          UNVERIFIABLE
pente-fino.generated.json       UNVERIFIABLE
censo-da-coleta.generated.json  UNVERIFIABLE
MATRIZ-CARDS-SENSORES-V1.json   UNVERIFIABLE
```

> **AUSÊNCIA DE PROVA DE STALENESS NÃO É PROVA DE CURRENT.**
> (já é lei em `AGENTS.md`; aplica-se a cada um dos seis relógios)

### 9.1 · Frescura do mapa servido continua a ser outra pergunta

Os quatro estados de SYNC (`CURRENT · STALE · UNKNOWN · BROKEN`) de
[`freshness.js`](../../system-map/app/freshness.js) respondem **«o que está
servido é desta árvore?»**. Este contrato não os toca e não os absorve.

```
MAP VALID  !=  MAP CURRENT  !=  MAP TRUSTWORTHY
```

### 9.2 · A LEI DO CICLO ATRASADO

> **NENHUM ARTEFATO PODE SER CONSIDERADO `CURRENT` SE MEDIU O OUTPUT DA GERAÇÃO
> ANTERIOR ENQUANTO A SUA SEMÂNTICA DIZ QUE REPRESENTA A ATUAL.**

Medido e reproduzido: injetou-se um cartão em `Z-ACOES`, território que o pente
fino conhece, e o pente fino não o viu. Correr a cadeia **uma segunda vez**, sem
mexer em mais nada: 48 → 49. A causa é a ordem — o pente fino lê
`state.generated.json` no passo 5 e o gerador escreve-o no passo 7.

O que **deveria** acontecer (não implementado nesta missão):

1. cada artefacto declara os seus `INPUTS` (§13);
2. cada artefacto carimba a versão de cada input que leu;
3. se um input carimbado não é o output atual do seu produtor, o artefacto é
   `STALE_BY_CYCLE`, nunca `CURRENT`;
4. a cadeia é ordenada topologicamente pelos `INPUTS` declarados, e não à mão.

Até isso existir, a reconciliação **nomeia** o caso com razão própria
(`PENTE_FINO_MEDIU_OUTRO_CONJUNTO_DE_NOS`) e não o confunde com filtro estreito.

---

## 10 · MODELO DE OBSERVAÇÃO DE RUNTIME

Estrutura mínima de uma observação operacional:

```
RUN_ID                    ou UNKNOWN, com razão escrita
ENTITY_ID / EDGE_ID       a quem a observação se refere
STAGE                     §11
INPUT
OUTPUT
RESULT                    PASSED | FAILED | ERROR | REJECTED | REUSED | NOT_RUN | UNKNOWN
OBSERVED_AT
TREE_FINGERPRINT          a versão do código que correu
ENVIRONMENT               rede? pago? produção? que banco?
EXECUTION_MODE            FORWARD | LEGACY_REPLAY | UNKNOWN
LIMITATIONS
```

**Nunca inferir o HEAD atual como versão executada.** A corrida traz a sua versão
ou diz `UNKNOWN`.

> **UM ID DE RASTREIO INVENTADO É PIOR DO QUE `UNKNOWN`.**
> (lei já escrita em `provas-de-execucao.json`; o contrato adota-a)

O dono atual de `OBSERVED` para executores é
[`system-map/data/provas-de-execucao.json`](../../system-map/data/provas-de-execucao.json).
Ele já implementa quase tudo isto, à mão e com razão escrita para cada `UNKNOWN`.
**O contrato não cria um segundo dono.** Medido: 2 executores provados de 57.

`EXECUTION_MODE` é obrigatório porque `LEGACY_REPLAY` prova o **instrumento** e
não o **fluxo canónico**: `REAL EXECUTOR != CANONICAL FORWARD FLOW`.

---

## 11 · LINEAGE

O vocabulário de etapa é o da Bíblia (`COL-LAW-044`), não um paralelo:

```
RAW · DERIVED · ADMITTED · READY · QUARANTINED
```

Uma corrida (`RUN`) observa **zero ou mais** destas etapas. `STRUCTURED` existe
como alvo com contrato próprio e só entra na cadeia de lineage do mapa quando
tiver dono forward e evidência.

Leis que o mapa não pode violar ao desenhar lineage:

- **Lineage é afirmação sobre fluxo, nunca sobre proximidade visual.** Duas peças
  lado a lado não têm aresta por isso.
- Não criar aresta de lineage sem `OBSERVED=YES` proveniente de uma corrida.
- `ETAPA NÃO OBSERVADA != ETAPA QUE NÃO EXISTE`. `NOT_RUN` significa «fazia parte
  do plano e não chegou a vez» — usá-lo para uma etapa sem dono é mentir.
- `READY` só o é por `COL-LAW-043`: contratos obrigatórios satisfeitos, nunca «o
  ficheiro existe» nem «o workflow terminou».

---

## 12 · UNIVERSO E LENTE

### 12.1 · Universo

```
UNIVERSE_ID
ENTITY_SPECIES        qual espécie este universo conta
DEFINITION
MEMBERS[]
COUNT                 == len(MEMBERS), sempre
SOURCE                quem o calcula, de que ficheiro, de que campo
PARENT_UNIVERSE_ID    ou null
FRESHNESS
```

Seis universos declarados hoje, todos em
[`SYSTEM-MAP-UNIVERSE-RECONCILIATION-V1.json`](../../data/derivados/SYSTEM-MAP-UNIVERSE-RECONCILIATION-V1.json).

### 12.2 · Lente

```
LENS_ID
PARENT_UNIVERSE       obrigatório
FILTER_RULE           a regra, legível e executável
MEMBERS[]
COUNT
EXCLUDED_MEMBERS[]
EXCLUSION_REASON      por membro
SOURCE
FRESHNESS
```

> **Uma lente pode filtrar. Nunca pode perder em silêncio.**

Sete lentes declaradas hoje. Cada uma aponta para um universo real, e a prova
reprova se apontar para um que não existe.

### 12.3 · Reconciliação

```
PARENT = INCLUDED + EXCLUDED       quando a lente é subconjunto
```

Medido: `65 = 48 + 17`. Fecha, e fecha nos dois sentidos — nenhum membro da lente
está fora do universo pai.

Toda exclusão traz `REASON` · `OWNER` · `INTENTIONAL ∈ {YES, NO, UNKNOWN}`.

> **`INTENTIONAL = UNKNOWN` é dívida declarada, não silêncio.** Ela aparece na
> auto-observabilidade (§16) e conta para `DEGRADED`.

Hoje: 12 exclusões `UNKNOWN`, 4 `NO`, 1 `YES`.

**O objetivo não é todas as lentes darem o mesmo número.** É todos os números
conseguirem ser reconciliados.

---

## 13 · ARTEFACTOS GERADOS, E A PROIBIÇÃO DE AUTO-PROVA

Todo artefacto gerado publica:

```
OWNER
GENERATOR
INPUTS[]              com a versão de cada um
TREE_FINGERPRINT
GENERATED_AT
SCHEMA_VERSION
DEPENDENCIES[]        quando deriva de outros generated
LIMITATIONS
```

`INPUTS` e `DEPENDENCIES` existem para que a §9.2 seja verificável e para que a
cadeia possa ser ordenada por dependência em vez de por hábito.

### 13.1 · Proibição de auto-prova

> **Um artefacto não é verdadeiro por o mesmo gerador o ter criado e validado
> contra os mesmos dados derivados.**

Três papéis, separados:

| papel | quem |
|---|---|
| `GENERATION` | o gerador |
| `VALIDATION` | quem regenera e compara, sem partilhar estado com o gerador |
| `INDEPENDENT_EVIDENCE` | uma classe de evidência **diferente** da que gerou |

A cadeia não pode ter ciclos de prova: se A valida B e B valida A, nenhum dos
dois foi validado.

### 13.2 · Persistência obrigatória

> **SE UM NÚMERO OU VEREDITO É PUBLICADO, A SUA MEDIÇÃO TEM DE SER REPRODUZÍVEL
> E PERSISTIDA.**

Um número que só existe enquanto alguém olha para o terminal não pode envelhecer
à vista de ninguém, e por isso não pode ser comparado amanhã.

Medido em falta: `censo_da_topologia.py` publica 111 e não escreve artefacto. O
número entra em documentação escrita à mão, que é a definição de segundo dono.

---

## 14 · CADEIA — UM DONO SÓ

```
CHAIN_OWNER = system-map/scripts/CADEIA-DO-MAPA.json
```

Medido: o manifesto declara **7** passos de `REGERAR`; o job `mapa` do workflow
corre **21** scripts, dos quais **13 não estão no manifesto**. O job `regras`
corre exatamente os 7.

Isto viola um princípio que o próprio manifesto escreve:

```
DOIS SÍTIOS COM A LISTA DOS PASSOS SÃO DUAS CADEIAS.
```

A prova `SMF-13` não apanha porque filtra as linhas para as que já estão no
manifesto, e uma sequência filtrada está sempre em ordem.

**O que o contrato exige (não implementado nesta missão):**

1. o manifesto é o único dono da lista, e declara **todos** os passos;
2. extensões opcionais declaram-se **dentro** do manifesto, com bloco próprio
   (`REGERAR_ESTENDIDO`), nunca numa lista paralela no `.yml`;
3. cada passo declara `INPUTS` e `OUTPUTS`, e a ordem deriva deles;
4. CI, build da Vercel e regeneração local consomem **a mesma** lista;
5. a prova compara a lista **inteira**, e reprova por excesso e por falta.

---

## 15 · MODELO DE CONFLITO

O mapa **não escolhe em silêncio** qual evidência vence.

```
CONFLICT_ID
ASSERTION_A · EVIDENCE_A
ASSERTION_B · EVIDENCE_B
STATUS        OPEN | RESOLVED | ACCEPTED_AS_DIFFERENT_QUESTIONS
OWNER         quem decide
RESOLUTION    e porquê; vazio enquanto OPEN
```

`ACCEPTED_AS_DIFFERENT_QUESTIONS` existe porque a maior parte das divergências
medidas nesta árvore **não eram conflitos**: eram duas perguntas diferentes com o
mesmo nome. Resolver essas escolhendo um vencedor destruiria informação.

Um conflito `OPEN` é publicado. Um conflito escondido é `FAIL`.

---

## 16 · TRUST MODEL

### 16.1 · O que TRUST mede

```
MAP TRUST  !=  COLLECTION HEALTH  !=  SYSTEM HEALTH
```

`TRUST` responde **«posso acreditar no que este mapa afirma?»**. Não responde «o
sistema está saudável».

- Um mapa confiável que mostra a Collection vermelha é um **sucesso do mapa**.
- Não pintar o mapa verde porque o sistema está saudável.
- Não pintar o mapa vermelho porque a Collection tem blocker.

Esta separação já é lei operacional em `CADEIA-DO-MAPA.json`
(`PORTAO_DA_COLETA` está na tela e **fora** de `decidir()`), e o contrato
estende-a a `TRUST`.

### 16.2 · Afirmações críticas e evidência mínima

| `ASSERTION_CLASS` | evidência mínima para publicar como facto |
|---|---|
| `EXISTS` | `GIT_TREE` ou `STATIC_CODE_ANALYSIS` |
| `OWNER` | `CANONICAL_CONTRACT` ou declaração com dono |
| `COUNT` | universo declarado + `MEMBERS` enumerados + frescura |
| `EDGE_EXISTS` (CODE) | `STATIC_CODE_ANALYSIS`/`AST` com ficheiro e linha |
| `EDGE_EXISTS` (OBSERVED) | `RUNTIME_TRACE` ou `POSTGRESQL` com `RUN_ID` |
| `FLOW_EXECUTED` | `RUNTIME_TRACE` com `RUN_ID`, `STAGE`, `RESULT` e versão |
| `PERSISTED` | `POSTGRESQL` ou armazém, lido depois da escrita |
| `READY` | `COL-LAW-043`: contratos obrigatórios satisfeitos |
| `LIVE` | `LIVE_OBSERVATION` na janela declarada |
| `BLOCKER_STATE` | evidência da classe do blocker + frescura |

Afirmação sem a evidência mínima **não é publicada como facto**. É publicada como
`UNKNOWN`, com o que falta escrito ao lado.

### 16.3 · Os quatro estados

**`PASS`** — todas verdadeiras:
1. toda afirmação crítica publicada é reconciliável a um universo declarado;
2. toda afirmação crítica tem evidência **da classe mínima** da §16.2;
3. nenhum plano foi promovido sem evidência própria (§2);
4. não há conflito `OPEN` não publicado;
5. nenhuma evidência crítica está `STALE` ou `UNVERIFIABLE` sem rótulo;
6. toda contagem publicada tem espécie, universo, membros e regra;
7. toda exclusão tem razão e dono.

**`DEGRADED`** — há `UNKNOWN`, `STALE` ou `UNVERIFIABLE` **explicitamente
rotulados**, e dívida declarada (`INTENTIONAL=UNKNOWN`), mas nenhuma afirmação
contraditória ou enganosa. O mapa continua útil e diz onde não sabe.

**`FAIL`** — basta **uma**:
- contradição publicada sem conflito declarado;
- contagem irreconciliável;
- `STALE` ou `UNVERIFIABLE` apresentado como `CURRENT`;
- `OBSERVED` ou `PROVEN` afirmado sem evidência da classe própria;
- auto-prova (§13.1);
- contagem sem espécie ou sem universo;
- exclusão sem razão.

**`UNKNOWN`** — não há evidência suficiente para avaliar a própria confiança: a
cadeia não correu, o validador não correu, ou a reconciliação não existe.

### 16.4 · A ordem de avaliação, e por que ela é lei

```
1. UNKNOWN   não consigo avaliar?          →  UNKNOWN
2. FAIL      alguma condição de FAIL?      →  FAIL
3. DEGRADED  algum UNKNOWN/STALE rotulado? →  DEGRADED
4. PASS      só então
```

`PASS` é o **último** recurso, nunca o estado por omissão — a mesma ordem que
`freshness.js` já prova por força bruta.

---

## 17 · AUTO-OBSERVABILIDADE

Métricas que o próprio mapa publica sobre si:

```
TREE_CURRENT                 a impressão do mapa é a desta árvore?
GENERATION_PASS              a cadeia correu inteira e sem erro?
VALIDATION_PASS              o validador aprovou?
COUNTS_RECONCILED            toda lente fecha com o seu universo?
UNEXPLAINED_EXCLUSIONS       exclusões com INTENTIONAL=UNKNOWN
CONFLICTS                    conflitos OPEN
STALE_CRITICAL_EVIDENCE      evidência crítica STALE
UNKNOWN_CRITICAL_EVIDENCE    evidência crítica UNKNOWN ou UNVERIFIABLE
RUNTIME_COVERAGE             §17.1
```

### 17.1 · `RUNTIME_COVERAGE` — o denominador tem de ser defensável

**Proibido** `cartões observados / todos os cartões visuais`. Há cartões que são
contrato, regra ou armazém e que **nunca executam**: pô-los no denominador
inventa uma dívida que não existe e faz a cobertura parecer pior do que é.

```
RUNTIME_COVERAGE = observados / entidades com ROLE ∈ {OPERATIONAL_STEP, DISPATCH_ENTRYPOINT}
```

O denominador é publicado com a sua regra ao lado, e as entidades excluídas dele
são enumeradas com `ROLE`. Medido hoje pelo censo dos executores: **2 de 57**
caminhos relevantes instrumentados.

---

## 18 · UNKNOWN É ESTADO DE PRIMEIRA CLASSE

```
UNKNOWN  →  false            PROIBIDO
UNKNOWN  →  zero             PROIBIDO
UNKNOWN  →  not applicable    PROIBIDO
UNKNOWN  →  escondido         PROIBIDO
```

O mapa **mostra a ausência de conhecimento**. Isto não é novo: é
`NÃO SEI continua NÃO SEI` aplicado ao mapa, e o contrato de design já exige que
`NÃO SEI` ocupe espaço na tela.

`NOT_INSTRUMENTED` (ninguém emite) ≠ `NOT_MEASURED` (emite-se e ninguém leu) ≠
`MEDIDO`. As três pedem coisas diferentes.

---

## 19 · CONTRATO DE PUBLICAÇÃO

Antes de algo aparecer como **facto** na interface:

```
ASSERTION → EVIDENCE → RECONCILIATION → FRESHNESS → TRUST CHECK → PUBLISH
```

Falta uma etapa crítica? Publica-se `UNKNOWN`, `STALE` ou `DEGRADED` conforme o
contrato. **Nunca esconder, nunca omitir, nunca arredondar para verde.**

---

## 20 · O QUE O CARD E A ARESTA PRECISAM DE PODER MOSTRAR

Não é redesenho de UI. É a lista do que a evidência tem de conseguir alimentar.

**Card:** `IDENTITY` · `OWNER` · `DECLARED/CODE/OBSERVED/PROVEN` em quatro campos
separados · `FRESHNESS` por relógio · `EVIDENCE` clicável · `CONFLICTS` ·
`GAPS` · `LAST_OBSERVED_RUN`.

**Aresta:** `RELATION_TYPE` · `DECLARED/CODE/OBSERVED/PROVEN` separados ·
`EVIDENCE` · `LAST_OBSERVED_RUN`.

> **Uma seta verde não pode continuar a significar quatro coisas.**

---

## 21 · O PENTE FINO — ESCOPO SEMÂNTICO

As quatro perguntas do pente fino são:

```
DE ONDE VEM?   PARA ONDE VAI?   POR QUE EXISTE?   ALGUÉM CORRE?
```

Elas só fazem sentido para uma entidade que **participa de um fluxo**. Logo:

```
APLICA-SE A     ROLE ∈ { OPERATIONAL_STEP, DISPATCH_ENTRYPOINT }
NÃO SE APLICA A ROLE ∈ { CONTRACT_OR_RULE, MEASUREMENT_INSTRUMENT, STORAGE, PROOF }
INDECIDÍVEL     ROLE = UNKNOWN  →  entra, e a falta de resposta é dívida
```

> **A regra de inclusão passa a ser semântica (`ROLE`), nunca uma lista de
> territórios.**

O que isto resolve, quando for implementado (não agora):

| caso | hoje | sob o contrato |
|---|---|---|
| 4 cartões `nivel=PRINCIPAL` fora | acidente da tupla | `DISPATCH_ENTRYPOINT` → **entram** |
| `C-ADMISSAO` dentro | acidente da tupla | `OPERATIONAL_STEP` → **entra** |
| 11 de `Z-MEDIDAS` fora | `INTENTIONAL=UNKNOWN` | `MEASUREMENT_INSTRUMENT` → **fora, por regra escrita** |
| `C-BIBLIA` fora | decisão certa, razão escrita | `CONTRACT_OR_RULE` → **fora** |
| `C-READY` fora | `INTENTIONAL=UNKNOWN` | `STORAGE` → **fora, por regra escrita** |

**`ROLE` não existe ainda como campo.** Atribuí-lo é trabalho de medição e
decisão humana, não desta missão.

---

## 22 · TOPOLOGIA

```
TOPOLOGY_NODE      entidade do grafo
TOPOLOGY_EDGE      aresta do grafo
BOUNDARY_NEIGHBOR  entidade fora do universo, ligada a alguém dentro
```

> **Um vizinho da Collection não vira membro da Collection.**

A vista **pode** mostrá-lo — e deve, senão o cartão parece órfão. O universo
continua distinto. Medido: o censo da topologia conta 111 = 65 da coleta + 46
vizinhos de fronteira, e os 46 são enumerados.

`ÓRFÃO NA VISTA != ÓRFÃO NO GRAFO` continua a valer nos dois sentidos.

---

## 23 · DECISÕES EXPLÍCITAS

| pergunta | decisão |
|---|---|
| `ONE CANONICAL ENTITY MODEL?` | **SIM** — §4 |
| `ONE CANONICAL EDGE MODEL?` | **SIM** — §6 |
| `ONE EVIDENCE MODEL?` | **SIM** — §7 |
| `ONE RUNTIME OBSERVATION MODEL?` | **SIM** — §10, dono `provas-de-execucao.json` |
| `ONE CHAIN OWNER?` | **SIM** — `CADEIA-DO-MAPA.json`. Hoje **violado**. |
| `LENSES DECLARE PARENT UNIVERSE?` | **SIM** — obrigatório, já provado |
| `EVERY PUBLISHED COUNT HAS MEMBERS?` | **SIM** — `COUNT == len(MEMBERS)` sempre |
| `EVERY EXCLUSION HAS REASON?` | **SIM** — com `OWNER` e `INTENTIONAL` |
| `UNKNOWN IS FIRST-CLASS?` | **SIM** — §18 |
| `STALE CAN NEVER PRESENT AS CURRENT?` | **SIM** — §9, e `UNVERIFIABLE` também não |
| `CODE CAN NEVER AUTO-PROMOTE TO OBSERVED?` | **SIM** — §2 |
| `OBSERVED CAN NEVER AUTO-PROMOTE TO PROVEN?` | **SIM** — §2 |
| `MAP TRUST IS SEPARATE FROM SYSTEM HEALTH?` | **SIM** — §16.1 |

---

## 24 · RED TEAM DO CONTRATO

Vinte ataques. Cada um tem de produzir resultado inequívoco.

| # | ataque | veredito do contrato |
|---|---|---|
| 1 | código existe e nunca correu | `CODE=YES OBSERVED=UNKNOWN`. `PASS` se rotulado; `FAIL` se publicado como PROVEN |
| 2 | runtime correu código velho | observação traz o seu `TREE_FINGERPRINT`; diverge do HEAD → evidência válida, `RUNTIME_EVIDENCE_FRESHNESS=STALE` |
| 3 | aresta declarada e ausente do código | `DECLARED=YES CODE=NO`. Publicável. `FAIL` se desenhada como verde |
| 4 | aresta observada e já não está no código | `CODE=NO OBSERVED=YES` → `CONFLICT` `OPEN`, publicado |
| 5 | artefacto gerado stale | `GENERATED_ARTIFACT_FRESHNESS=STALE` → `DEGRADED`; `FAIL` se servido como current |
| 6 | duas lentes com contagens diferentes | esperado. `PASS` se reconciliáveis; `FAIL` se não |
| 7 | mesma entidade aparece duas vezes na tela | `ENTITY_ID` é um só; duas vistas, uma identidade. `FAIL` se contada duas vezes |
| 8 | mesmo nome, identidades diferentes | nome é `PRESENTATION`. Legal, e obriga a rótulo desambiguador na tela |
| 9 | fonte da evidência `UNKNOWN` | evidência sem `SOURCE` é inválida; a afirmação cai para `UNKNOWN` |
| 10 | teste passa, produção desconhecida | `TEST` prova o teste. `LIVE=UNKNOWN`. `FAIL` se publicado como LIVE |
| 11 | dois workflows geram mapas diferentes | viola `ONE CHAIN OWNER` → `FAIL` |
| 12 | contagem hardcoded no frontend | sem `WHO_COMPUTES`/`MEMBERS` → não publicável; `FAIL` |
| 13 | scanner vê docstring e conclui aresta | `STATIC_CODE_ANALYSIS` sem `AST` tem `LIMITATIONS`; menção não é referência |
| 14 | aresta inferida de nome de ficheiro | não é classe de evidência. Rejeitada |
| 14b | **uma linha de evidência sustenta duas afirmações diferentes** | **medido: 37 linhas, 52 arestas.** `ASSERTION_SUPPORTED` por afirmação (§7.1); sem ele, `FAIL` |
| 15 | vizinho da topologia tomado por membro | §22. Universo distinto; `FAIL` se somado |
| 16 | instrumento de medição tomado por componente de runtime | `ROLE=MEASUREMENT_INSTRUMENT`; fora do denominador de cobertura (§17.1) |
| 17 | UI fresca sobre evidência velha | frescura é por evidência, não da página. `DEGRADED` ou `FAIL` |
| 18 | mesmo SHA, observações diferentes | ambas válidas: `ENVIRONMENT` difere. `CONFLICT` só se a mesma pergunta |
| 19 | mapa saudável, Collection a falhar | **`PASS`.** É sucesso do mapa (§16.1) |
| 20 | Collection saudável, mapa stale | `FAIL` ou `DEGRADED` conforme rotulado. Saúde do sistema não compra confiança no mapa |

**Sobreviventes: 0.** Nenhum ataque produz resultado ambíguo sob o contrato.

---

## 25 · VEREDITO SOBRE O MAPA ATUAL

Aplicando este contrato ao estado medido em `c828d1ac`, sem herdar veredito
anterior:

```
CURRENT_SYSTEM_MAP_TRUST = FAIL
```

**São duas causas, ambas nomeáveis e limitadas.**

### Causa 1 · a palavra promete o plano seguinte

> O mapa publica `status = PROVEN` em **658 arestas** e **59 nós** apoiado
> exclusivamente em análise estática.

As razões que o próprio mapa escreve dizem-no: *«Provado por 1 linha de codigo»*,
*«outra peca importa isto»*, *«algum workflow manda rodar isto»*. Todas provam
`CODE`. Nenhuma prova `OBSERVED`. **Zero arestas e zero nós têm evidência de
runtime.** Os únicos 2 caminhos com prova de execução vivem noutro ficheiro e não
alimentam `status`.

Pior do que a promoção a partir de `CODE`: das 40 arestas **sem tipo medido** —
rótulos narrativos de declaração — **38 também publicam `PROVEN`**. Aí a promoção
parte de `DECLARED`, e salta dois planos de uma vez.

E `OBSERVED` não está apenas ausente: **é irrepresentável.** O esquema de aresta
não tem campo de `RUN_ID`, `OBSERVED_AT` nem `ENVIRONMENT`. Não há onde escrever
uma observação, mesmo que alguém a medisse.

### Causa 2 · uma linha de evidência sustenta afirmações que ela não prova

Medido: **37 linhas** sustentam `RELATION_TYPE` diferentes, em **52 arestas**. O
caso literal está na §7.1 — um `import` a sustentar três afirmações de abertura
de canal.

Cada causa, sozinha, aciona a §16.3: *«`OBSERVED` ou `PROVEN` afirmado sem
evidência da classe própria»*.

**O que NÃO é a causa, e é preciso dizer:**

- Nada foi falsificado. Todas as 1160 linhas de evidência apontam ficheiro e
  linha reais, e o texto de cada `reason` descreve honestamente o que mediu.
- As contagens reconciliam. `65 = 48 + 17`, `COUNT == len(MEMBERS)`, toda exclusão
  tem razão e dono.
- A frescura do servido é medida e não mente: `UNVERIFIABLE` nunca vira `CURRENT`.
- O mapa não está a esconder nada. Está a **prometer de mais** sobre o que mostra.

**As duas causas têm preços diferentes, e isso importa para quem as vai fechar.**

A Causa 1 é uma colisão de vocabulário: as 658 medições estão certas, e só a
palavra publicada sobre elas promete o plano seguinte. Renomear `status: PROVEN`
→ `CODE` e abrir os quatro planos como campos separados fecha-a **sem medir uma
única coisa nova**.

A Causa 2 **não** é vocabulário: em 52 arestas a evidência está ligada à afirmação
errada, e nenhum renomear conserta isso. Fechá-la exige rever, uma a uma, que
afirmação cada linha sustenta — e aceitar que algumas ficarão sem evidência, ou
seja, `UNKNOWN`. **São 52 de 660: caro por aresta, barato no total.**

Com as duas fechadas, o mapa fica em `DEGRADED` — não `PASS` — porque continuam
declaradas estas dívidas:

| dívida | medida |
|---|---|
| exclusões com `INTENTIONAL=UNKNOWN` | 12 |
| artefactos `UNVERIFIABLE` | 4 |
| censos que publicam número sem persistir | 1 (`censo_da_topologia`) |
| violação de `ONE CHAIN OWNER` | 13 scripts fora do manifesto |
| entidades com `ROLE` atribuído | 0 de 160 |
| cobertura de runtime | 2 de 57 |
| arestas com evidência emprestada | 52 de 660 |
| arestas onde `OBSERVED` é sequer representável | 0 de 660 |

---

## 26 · GAPS ORDENADOS ATÉ `PASS` — LISTA, NÃO EXECUÇÃO

Ordenados pela **menor dependência arquitetural**. Nenhum é executado nesta missão.

| # | gap | depende de | custo |
|---|---|---|---|
| 1 | separar `status` em `DECLARED/CODE/OBSERVED/PROVEN` em nós e arestas | nada | gerador + tela |
| 2 | persistir o censo da topologia como artefacto | nada | um `json.dump` |
| 3 | carimbar `SOURCE_TREE_FINGERPRINT` nos 4 artefactos `UNVERIFIABLE` | nada | 4 geradores |
| 4 | declarar `INPUTS`/`OUTPUTS` por passo no manifesto | 3 | manifesto |
| 5 | unificar a cadeia: manifesto passa a declarar os 21 passos | 4 | manifesto + workflow + `SMF-13` |
| 6 | ordenar a cadeia por `INPUTS` e fechar a lei do ciclo atrasado (§9.2) | 4, 5 | cadeia |
| 7 | atribuir `ROLE` às 160 entidades | 1 | medição + decisão humana |
| 8 | pente fino por `ROLE` em vez de tupla de territórios | 7 | pente fino + reconciliação |
| 8b | `ASSERTION_SUPPORTED` por evidência, e desfazer os 37 empréstimos | 1 | gerador |
| 9 | `LIMITATIONS` obrigatório em toda evidência publicada | 1 | gerador |
| 10 | modelo de conflito publicado | 1, 9 | gerador + tela |
| 11 | `RUNTIME_COVERAGE` com denominador por `ROLE` | 7 | censo |
| 12 | ligar `provas-de-execucao.json` a `OBSERVED` de nós e arestas | 1, 10 | gerador |
| 13 | painel de auto-observabilidade (§17) | 1–12 | tela |

Os gaps **1, 2 e 3 não dependem de nada** e sozinhos tiram o mapa de `FAIL`.

---

## 27 · DELTA PARA O KNOW-HOW CANÓNICO

O know-how canónico vive em `SINTONIA-EAME-KNOW-HOW.md`, na linha
`claude/sintonia-eame-know-how-v1`. **Não está nesta linha, e este contrato não
cria um segundo.** O delta para integração posterior é:

```
UMA FERRAMENTA DE OBSERVABILIDADE NÃO É CONFIÁVEL PORQUE MEDE MUITO.
ELA É CONFIÁVEL QUANDO CADA AFIRMAÇÃO QUE PUBLICA DECLARA A EVIDÊNCIA
QUE A SUSTENTA, O PLANO EM QUE ELA VIVE, E O QUE ESSA EVIDÊNCIA NÃO PROVA.

O ERRO MAIS CARO NÃO É MEDIR MAL. É MEDIR BEM E PUBLICAR A PALAVRA ERRADA:
658 ARESTAS COM EVIDÊNCIA CORRETA DE CÓDIGO ESTAVAM ROTULADAS «PROVEN»,
E A MEDIÇÃO ESTAVA CERTA EM TODAS.

ANÁLISE ESTÁTICA PROVA CAN DO. SÓ TELEMETRIA PROVA DID DO.
```

Local de integração sugerido: secção de leis do System Map, junto de
`CAN DO != DID DO`.

---

## 28 · RELAÇÃO COM OS OUTROS FICHEIROS

| ficheiro | papel |
|---|---|
| [`AGENTS.md`](../../AGENTS.md) | **dono da lei do mapa** — frescura do servido, pratelaria, universos |
| **este ficheiro** | **dono do modelo de confiança** — evidência, planos, TRUST |
| [`BIBLIA-CANONICA-DA-COLETA.md`](../../BIBLIA-CANONICA-DA-COLETA.md) | dono das etapas e dos estados da coleta |
| [`CADEIA-DO-MAPA.json`](../../system-map/scripts/CADEIA-DO-MAPA.json) | dono da cadeia |
| [`SYSTEM-MAP-UNIVERSE-RECONCILIATION-V1.json`](../../data/derivados/SYSTEM-MAP-UNIVERSE-RECONCILIATION-V1.json) | dono das contagens |
| [`provas-de-execucao.json`](../../system-map/data/provas-de-execucao.json) | dono de `OBSERVED` para executores |
| [`CONTRATO-DE-DESIGN-SINTONIA.md`](../design/CONTRATO-DE-DESIGN-SINTONIA.md) | dono do que a tela não pode esconder |

**Um dono. Múltiplos ponteiros.** Este contrato não copia nenhuma dessas leis.

Em conflito entre este contrato e o contrato de design, **o de design vence**:
nenhuma decisão de confiança autoriza esconder um `NÃO SEI`.
