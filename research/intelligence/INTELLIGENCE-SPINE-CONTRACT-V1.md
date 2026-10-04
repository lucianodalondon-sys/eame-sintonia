# A ESPINHA COMUM DA INTELLIGENCE — CONTRATO V1

```
MISSAO      C-INT-SPINE-01
ESPECIE     ARBITRAGEM + CONTRATO + PROVA EXECUTAVEL
ESTADO      CANDIDATE — NAO PROMOVE NADA A CANONICO
MEDIDO_EM   2026-09-14
IMPLEMENTACAO_AUTORIZADA   NAO
```

> Este documento responde a **uma** pergunta:
>
> *Qual é a máquina comum que transforma evidência vinda da Sala de Espera em
> achado — incluindo promoção, rejeição e reversão — sem criar um motor por
> domínio?*
>
> Ele **não** cria Bíblia nova, **não** promove a Bíblia existente, **não**
> implementa `INTELLIGENCE_RUN` e **não** toca na Collection.

---

# 0 · O GIT, MEDIDO ANTES DE DECIDIR

```
CURRENT_BRANCH   claude/label-intelligence-v1-italy
INITIAL_HEAD     6afba2efd0aad240df1aac3e7143501041478788
WORKTREE_STATE   limpo na abertura
```

## ⚠️ A PRIMEIRA MEDIÇÃO É UM ACHADO, E MUDA O VALOR DE TUDO O QUE VEM DEPOIS

```
git merge-base HEAD origin/main                                  -> VAZIO
git merge-base HEAD origin/claude/epic-archimedes-ryo0ms         -> VAZIO
git merge-base HEAD origin/research/intelligence-bible-...-v1    -> VAZIO
git merge-base HEAD origin/claude/sintonia-eame-know-how-v1      -> VAZIO
git merge-base HEAD origin/claude/funny-hypatia-y7ho5s           -> VAZIO
```

**A branch designada para esta missão não tem ancestral comum com nenhuma
autoridade da Intelligence.** São histórias desconexas: 50 commits de um lado,
878 do outro, e zero em comum. A árvore desta branch não tem `motor/`, não tem
`coleta/`, não tem `admissao/`, não tem `leis/`.

```
UMA ESPINHA ESCRITA NUMA ARVORE QUE NAO PARTILHA UM SO COMMIT
COM O CODIGO QUE ELA GOVERNA NAO GOVERNA CODIGO NENHUM.
```

Isto **não** invalida a arbitragem — ela foi feita lendo as autoridades onde
elas realmente vivem, e não de memória. Mas fixa o veredito do §17 do enunciado
antes de qualquer outra coisa, e explica por que esta missão **não fez merge**:
não há merge pequeno e sem conflito entre histórias desconexas. Há um plano de
integração, e ele está no §13.

---

# 1 · AS AUTORIDADES, E ONDE ELAS ESTÃO DE VERDADE

| autoridade | branch | commit | estado | usada para quê |
|---|---|---|---|---|
| Bíblia de Engenharia da Intelligence V0.2 | `research/intelligence-bible-engineering-v1` | `7ae1b510` | `CANDIDATE_FOR_CANONICAL_REVIEW` | constituição: leis `INT-LAW-*` |
| Red team da Bíblia V0.2 | `research/intelligence-bible-engineering-v1` | `7ae1b510` | evidência de revisão | os 8 pontos `G-INT-*` ainda abertos |
| Benchmark de engenharia da Intelligence | `research/intelligence-bible-engineering-v1` | `7ae1b510` | pesquisa | origem externa das leis |
| Arbitragem da Intelligence Canónica V1 | `claude/funny-hypatia-y7ho5s` | `87712a01` | arbitragem | dono por conceito |
| `INTELLIGENCE-CONCEPT-OWNERSHIP-V1.json` | `claude/funny-hypatia-y7ho5s` | `87712a01` | arbitragem | 22 conceitos com dono/estado |
| Censo atual da Intelligence | `claude/funny-hypatia-y7ho5s` | `87712a01` | medição | o que existe em código |
| Motor Intelligence V2 — requisitos | `claude/intelligence-backlog-canonical` | `4df24aa9` | contrato subordinado | histórico append-only, estado da evidência |
| Benchmark agro `C-INT-AGRO-BENCH-01` (+9 irmãos) | `claude/epic-archimedes-ryo0ms` | `dc00583d` | pesquisa + modelo candidato | portões G0–G6, reversões, régua de doença |
| Know-how canónico (tail `§110`) | `claude/sintonia-eame-know-how-v1` | `338e171a` | memória durável | `§14` — fronteira e cadeia da Intelligence |
| Bíblia canónica da Coleta V1.4 | linha funcional | `f888776d` | **canónica** | fronteira upstream `CLAIM/FACT` |
| Contrato READY (12 campos) | linha funcional | `f888776d` | **em runtime** | `admissao.pronto_para_inteligencia()` |
| Contrato da gestão da coleta | linha funcional | `f888776d` | contrato | `leis/gestao_da_coleta.py` — `GESTAO_DA_COLETA/v1` |
| Control Plane / Autoridades canónicas | `research/...` e `funny-hypatia` | `7ae1b510` · `87712a01` | registo | quem manda, e onde |

`FUNCTIONAL_HEAD = f888776dffd789053fbaf39fc9fe630c74dde3ef` — o mesmo que a
arbitragem V1 declarou, e continua a ser antecessor de `dc00583d`.

**Nenhuma destas nove primeiras linhas coexiste num único commit.**
Ver `§12 · CONTROL_PLANE_ATOMICITY`.

---

# 2 · O QUE A MEDIÇÃO DERRUBOU DA HIPÓTESE DO ENUNCIADO

O enunciado propõe dez estágios. Três **não sobrevivem como entidade**, um
**muda de nome** e um **parte-se em dois donos**. E dois estágios que ele não
tem **têm de existir**.

| estágio proposto | veredito | porquê, medido |
|---|---|---|
| `INTELLIGENCE_RUN` | **SOBREVIVE** | arbitrado em `CONCEPT-OWNERSHIP-V1`; `INT-LAW-050..054` |
| `EVIDENCE` | **NÃO É ENTIDADE DA INTELLIGENCE** | o que atravessa a fronteira é o item READY, de 12 campos, e o dono é a Collection. `INT-LAW-000` |
| `SIGNAL` | **SOBREVIVE** | `INT-LAW-036`; e ganha definição fechada no §4.1 |
| `CROSSING` | **SOBREVIVE** | único com `CANONICAL_OWNER_PROVEN` em código (`motor/v21_crossings.py`, 8 invariantes) |
| `JUDGMENT` | **NÃO É ESTÁGIO** | a arbitragem V1 já fundiu: `FINDING / ANALYTIC_JUDGMENT` é **um** conceito com **um** dono. Um estágio próprio criaria o segundo dono da mesma decisão |
| `CANDIDATE_FINDING` | **RENOMEADO** | o nome canónico já existe: `ANALYTIC_HYPOTHESIS` (`INT-LAW-035`, `CONCEPT-OWNERSHIP-V1`, portão `G3` do agro) |
| `VALIDATION_QUEUE` | **NÃO É ENTIDADE** | vira estado do objeto + projeção. Ver §4.5 — é aqui que a fila deixa de poder virar ferramenta |
| `FINDING` | **SOBREVIVE** | `INT-LAW-140` |
| `REVERSAL` | **NÃO É ENTIDADE** | é uma **classe de transição** com 7 causas nomeadas e uma aresta `DEMOTED_BY` |
| `COLLECTION_GAP` | **PARTE-SE EM DOIS DONOS** | ver §4.10 — é o achado mais consequente desta missão |
| — | **FALTAVA** `INTELLIGENCE_REQUEST` | a corrida precisa de uma pergunta com identidade (`CONCEPT-OWNERSHIP-V1`, `NOT_IMPLEMENTED`) |
| — | **FALTAVA** `SCREENING` | portão `G1` do agro: o rastreio barato, feito **para descartar** |

E a régua que o enunciado repete de memória, conferida contra o artefato:

```
o enunciado diz          VALIDATION QUEUE = necessaria · DECISION INBOX = descartada
o artefato diz           a revisao humana e um ATRIBUTO DE PORTAO (G3/G4/G6),
                         e a autonomia e granular (INT-LAW-170)
o que sobrevive          o ESTADO de validacao. A fila e a leitura desse estado.
```

---

# 3 · A ESPINHA APROVADA

```
                    INTELLIGENCE_REQUEST          ← a pergunta, com identidade
                            │
                    INTELLIGENCE_RUN              ← identidade + config efetiva
                            │
                    EVIDENCE_SELECTION            ← aresta para itens READY
                            │                        (os itens continuam da Collection)
        ┌───────────────────┴─────────────────────────────────┐
        │   SALA DE ESPERA · READY_ITEM · 12 campos           │  dono: COLLECTION
        └───────────────────┬─────────────────────────────────┘
                            │
                     [G0]   │  IDENTIDADE · ESPÉCIE · TEMPO DO FACTO
                            ▼
                         SIGNAL ──────────► BLOQUEADO_EM_G0 ──► REQUISITO
                            │
                     [G1]   │  RASTREIO BARATO, FEITO PARA DESCARTAR
                            ▼
                    SIGNAL(RASTREADO) ────► DESCARTADO (motivo + versão da regra)
                            │
                     [G2]   │  CRUZAMENTO + GRAFO DE DEPENDÊNCIA
                            ▼
                        CROSSING ─────────► NOT_POSSIBLE · PARCIAL · UNKNOWN
                            │
                     [G3]   │  FORMAÇÃO DE HIPÓTESE (falsificável)
                            ▼                 ▲
              ANALYTIC_HYPOTHESIS             └── as arestas APOIA/CONTRADIZ
              [ = candidate finding ]             nascem AQUI, e não no cruzamento
                            │
                     [G4]   │  VALIDAÇÃO (estado no objeto, não caixa de entrada)
                            ▼
                    ┌───────┴────────┐
                 FINDING          REJEITADA (e não produz achado nenhum)
                    │
          ┌─────────┴─────────┐
     [G5] │                   │ [G6]
          ▼                   ▼
    WATCH / FUTURE        OPPORTUNITY (nível A·B·C·D declarado)
          │                   │
          └─────────┬─────────┘
                    ▼
            RECOMMENDATION            ← nunca ACTION (INT-LAW-024)
                    │
                    ▼
             OUTCOME LOOP  ──DEMOTED_BY──►  reverte qualquer estado acima
```

E, ortogonal a **todos** os portões, o único caminho de volta:

```
INTELLIGENCE
   └─ INTELLIGENCE_REQUIREMENT       (o que falta, a janela, o grão, o porquê)
         └─ GESTOR DA COLETA         GESTAO_DA_COLETA/v1 — mede o GAP
               └─ DECISÃO            COLLECT_NOW · LATER · DO_NOT · NEEDS_HUMAN
                     └─ ORQUESTRADOR  escolhe COMO e POR ONDE
                           └─ COLLECTION RUN → RAW → … → ADMISSÃO
                                 └─ SALA DE ESPERA
                                       └─ nova INTELLIGENCE_RUN
```

## As três coisas que esta espinha recusa por desenho

```
1. NAO EXISTE ARESTA DE SIGNAL PARA FINDING.
   Entre os dois ha tres portoes, e cada um sabe dizer NAO.

2. O CRUZAMENTO NAO TEM ONDE ESCREVER UM JULGAMENTO.
   A classe nao tem campo para isso. Ganhar esse campo E o ataque.

3. A INTELLIGENCE NAO TEM NENHUMA FUNCAO QUE NOMEIE UMA ROTA.
   O requisito recusa, em codigo, 12 palavras que pertencem a Collection.
```

---

# 4 · OS CONCEITOS, UM A UM

Formato do §8 do enunciado. `CURRENT` é o que está medido hoje; `TARGET` é o
que este contrato propõe. **Nunca se escreveu `OBSERVED` onde só há `DEFINED`.**

## 4.1 · `SIGNAL`

```
DEFINICAO    uma LEITURA TIPADA de UM item READY, dentro de UMA corrida.
OWNER        INTELLIGENCE
IDENTITY     SIGNAL_ID  (da corrida; NUNCA reescreve ITEM_ID nem SOURCE_ID)
INPUT        READY_ITEM + espécie declarada pela fonte + ontologia do domínio
OUTPUT       (ESPECIE, SUJEITO, MATCH_TYPE, FACT_TIME, FACT_LOCATION, precisões)
STATE        SINAL · RASTREADO · DESCARTADO
PERSISTENCE  append-only, dentro da corrida
PROVENANCE   aponta para ITEM_ID e SOURCE_ID; não os substitui
VERSIONING   carrega a versão da regra que o produziu
REVERSIBILITY  a Collection corrigir o RAW; a normalização ser revista
CURRENT      DEFINED · NOT_IMPLEMENTED. `ANALYTIC_SIGNAL` = 0 ficheiros.
             `SIGNAL_ID` aparece em 9 ficheiros, nenhum deles dono
             (`motor/v2_cruzamentos.py` usa `FIELD_SIGNAL_IDS` como lista)
TARGET       objeto de primeira classe, com espécie obrigatória
```

### A resposta ao §8.1 do enunciado

O enunciado pergunta se signal é registo, classificação, interpretação, estado
ou relação. **É classificação, e as outras quatro já têm dono:**

```
registo         e o READY_ITEM          → dono: COLLECTION
interpretacao   e a HIPOTESE            → dono: INTELLIGENCE, mas em G3
estado          e um CAMPO do sinal     → nao e o sinal
relacao         e o CROSSING            → dono: INTELLIGENCE, mas em G2
```

Um sinal **não cria facto nenhum**. Ele diz: *este item, lido por esta regra, é
uma evidência desta espécie sobre este sujeito, neste tempo e neste lugar.*

```
UMA EVIDENCIA VIRA SINAL QUANDO A ESPECIE DELA E CONHECIDA
E O SUJEITO RESOLVE — OU FICA DECLARADAMENTE POR RESOLVER.
NAO HA TERCEIRA HIPOTESE, E «PARECE SER» NAO E UMA DELAS.
```

### ⛔ O bloqueio, medido e não inferido

```
admissao.pronto_para_inteligencia() devolve 12 campos.
EVIDENCE_SPECIES nao e um deles.  Medido: 0 de 12.
```

Do lado da Intelligence, **hoje**, um boletim agroclimático e um relato de campo
são o mesmo texto. É o ataque `#7` do red team agro, que caiu como argumento e
sobreviveu como estado do repositório. `provas/espinha_da_intelligence.py`
recusa-se a produzir sinal nessas condições, e a recusa está sob teste
(`FronteiraMedida.test_o_item_real_de_hoje_nao_produz_sinal`).

## 4.2 · `CROSSING`

```
DEFINICAO    coincidencia estrutural com CHAVE DE JUNCAO PROVADA. Sem julgamento.
OWNER        INTELLIGENCE   (CANONICAL_OWNER_PROVEN — motor/v21_crossings.py)
IDENTITY     CROSSING_ID
INPUT        >= 2 sinais rastreados + a pergunta que o cruzamento responde
OUTPUT       JOIN_KEY + precisões herdadas + contagem de origens independentes
STATE        PROVADO · PARCIAL · NOT_POSSIBLE · UNKNOWN
PERSISTENCE  preserva os SIGNAL_IDs que o compõem — sempre
PROVENANCE   os sinais, e por eles os itens e as fontes
VERSIONING   versão da regra de junção
REVERSIBILITY  descobrir que as duas origens eram uma só (`SAME_ORIGIN`)
CURRENT      IMPLEMENTED + OBSERVED na linha V2.1, com 8 invariantes duras
TARGET       o mesmo, com espécie e método a viajarem nos sinais
```

### A resposta ao §8.2 — a fronteira, escrita

O enunciado pergunta se um cruzamento é coincidência estrutural ou já contém
julgamento. **É coincidência estrutural, e a fronteira é esta:**

```
O CRUZAMENTO DIZ      «estes dois sinais falam do MESMO sujeito, em tempo e
                       lugar compativeis, e a chave que os une e esta»
O CRUZAMENTO NAO DIZ  «logo»
```

A palavra `logo` é o julgamento, e ela nasce em `G3`. A prova disto não é uma
promessa: a classe `Cruzamento` **não tem campo** onde a escrever, e o teste
`P3.test_o_cruzamento_nao_tem_onde_escrever_julgamento` falha no dia em que
alguém lho acrescentar.

E a lei que o cruzamento carrega, herdada do agro:

```
UM CRUZAMENTO NAO PODE ALEGAR MAIS DO QUE O SEU APOIO MAIS FRACO.

  provincia x regiao  ->  REGIAO
  dia x campanha      ->  CAMPANHA
  especie x grupo     ->  GRUPO
```

## 4.3 · `JUDGMENT`

```
DEFINICAO    o ATO de ligar evidencia a uma unidade analitica, com direcao,
             regra e motivo. Materializa-se em arestas APOIA / CONTRADIZ.
OWNER        INTELLIGENCE — o MESMO dono do FINDING, e isso e deliberado
IDENTITY     nao tem identidade propria: e o par (aresta, unidade julgada)
INPUT        sinal ou cruzamento + a hipotese que ele afeta
OUTPUT       Aresta(TIPO, EVIDENCIA, REGRA, MOTIVO)
STATE        nao tem estado proprio
PERSISTENCE  vive no traco de decisao da hipotese e, depois, do achado
PROVENANCE   uma por aresta — e um julgamento sem motivo e recusado
VERSIONING   a versao da regra, por aresta
REVERSIBILITY  uma aresta nova nao apaga a anterior
CURRENT      DEFINED · NOT_IMPLEMENTED (SUPPORT e CONTRADICTION = 0 ficheiros
             como relacao de primeira classe)
TARGET       relacao de primeira classe, dirigida
```

### A resposta ao §8.3

Sim: `JUDGMENT` é o primeiro lugar onde a Intelligence pode dizer
`supports / contradicts / insufficient`. **Mas não é um estágio entre o
cruzamento e o candidato — é o nascimento do candidato.** Fazer dele um
estágio próprio criaria dois donos da mesma decisão, que é o ataque 13 do red
team. A arbitragem V1 já tinha decidido isto ao escrever
`"FINDING / ANALYTIC_JUDGMENT"` como **uma** entrada.

E `insufficient` não é uma aresta: é o **estado de um portão**, com motivo e
versão da regra — exatamente como a `AGRO-CROSSING-GRAPH-V1` reformulou `BLOCKS`.

## 4.4 · `CANDIDATE_FINDING` ≡ `ANALYTIC_HYPOTHESIS`

```
DEFINICAO    uma resposta PROPOSTA a uma pergunta analitica, FALSIFICAVEL.
OWNER        INTELLIGENCE
IDENTITY     HYPOTHESIS_ID
INPUT        cruzamento (ou sinal unico de autoridade alta) + premissas
OUTPUT       hipotese + arestas de julgamento + nivel pretendido
STATE        HIPOTESE · REJEITADA · PROMOVIDA   ×   VALIDACAO ∈ {NAO_EXIGIDA,
             PENDENTE, APROVADA, RECUSADA}
PERSISTENCE  append-only
PROVENANCE   os cruzamentos/sinais em que se apoia, resolvíveis na corrida
VERSIONING   versao da regra
REVERSIBILITY  evidencia contraria devolve-a a HIPOTESE
CURRENT      DEFINED · NOT_IMPLEMENTED (0 ficheiros)
TARGET       objeto de primeira classe
```

**Não se cria `CANDIDATE_FINDING`.** Dois nomes para o mesmo objeto é o começo
de dois donos. E a hipótese tem um portão que o nome «candidato» não sugere:

```
UMA HIPOTESE QUE NADA DERRUBA NAO E UMA HIPOTESE.
E UMA OPINIAO COM IDENTIFICADOR.
```

## 4.5 · `VALIDATION_QUEUE`

```
DEFINICAO    NAO E UM OBJETO. E a projecao
             { h : portao(h) exige humano  ∧  h.VALIDACAO = PENDENTE }
OWNER        o estado vive na HIPOTESE. A projecao nao tem dono proprio.
IDENTITY     nenhuma — uma fila com identidade e uma caixa de entrada
INPUT        as hipoteses da corrida
OUTPUT       uma lista, calculada na hora
STATE        NAO_EXIGIDA · PENDENTE · APROVADA · RECUSADA   (no objeto)
PERSISTENCE  nenhuma propria
PROVENANCE   quem validou, quando e porquê — no evento, não na fila
VERSIONING   a politica de autonomia (INT-LAW-170) e versionada
REVERSIBILITY  uma validacao pode ser revista; o evento anterior fica
CURRENT      DEFINED · NOT_IMPLEMENTED (0 ficheiros)
TARGET       projecao, e so projecao
```

### A resposta ao §8.5 — e porque ela sobrevive ao red team

O benchmark anterior concluiu `VALIDATION QUEUE = necessária` e
`VALIDATION QUEUE != TOOL`. **Conferido: sobrevive, mas reduzida.**

```
O QUE E NECESSARIO   o ESTADO de validacao, no objeto
O QUE E FERRAMENTA   a fila, se ganhar armazenamento proprio
```

No momento em que a fila tem tabela, ela tem estado; no momento em que tem
estado, ela pode divergir do objeto; e no dia em que diverge, a pergunta «isto
foi validado?» passa a ter duas respostas.

```
UMA FILA COM ARMAZENAMENTO PROPRIO E UM SEGUNDO DONO
DA MESMA VERDADE, A ESPERA DE DIVERGIR.
```

## 4.6 · `FINDING`

```
DEFINICAO    julgamento analitico promovido, com traco de decisao auditavel
OWNER        INTELLIGENCE
IDENTITY     FINDING_ID
INPUT        hipotese validada
OUTPUT       achado + TRACO_DE_DECISAO completo
STATE        CONFIRMADO · REBAIXADO · REABERTO · REJEITADO · SUBSTITUIDO
PERSISTENCE  append-only; ACTIVE_STATE separado de HISTORICAL_STATE
PROVENANCE   evidencias, premissas, arestas, contraditorio, regra, config
VERSIONING   config efetiva da corrida, guardada no traco
REVERSIBILITY  as sete causas do §5
CURRENT      PARCIAL — `motor/v21_fechar.py` fecha estados; nao ha traco formal.
             `FINDING_ID` = 0 ficheiros.
TARGET       objeto de primeira classe com traco obrigatorio
```

### A resposta ao §8.4 — o que é preciso para promover

```
[1] a hipotese e falsificavel, e o falsificador esta escrito
[2] o NIVEL esta declarado E e sustentado pela ESPECIE da evidencia
[3] a evidencia contraria esta LIGADA, nao omitida
[4] a validacao exigida pelo portao aconteceu
[5] ha pelo menos uma evidencia de apoio que resolve na corrida
```

E o que **não** promove:

```
revisao humana          NAO promove nivel      (INT-LAW-172)
mais fontes do mesmo    NAO promove nivel
apresentacao melhor     NAO promove nivel
```

## 4.7 · `REVERSAL`

```
DEFINICAO    classe de transicao que faz um achado ANDAR PARA TRAS
OWNER        INTELLIGENCE
IDENTITY     nao tem — e o evento + a aresta DEMOTED_BY
INPUT        evidencia nova + causa canonica
OUTPUT       novo ACTIVE_STATE; HISTORICAL_STATE intacto
STATE        as 7 causas, com destino fixo (§5)
PERSISTENCE  append-only, sempre
PROVENANCE   quem/o que disparou, e a evidencia
REVERSIBILITY  ela propria e reversivel: um achado reaberto pode reconfirmar
CURRENT      DEFINED · NOT_IMPLEMENTED (`REVERSAL` = 0 ficheiros;
             `DEMOTED_BY` existe em 1 ficheiro, que e o documento agro)
TARGET       transicao de primeira classe
```

## 4.8 · `INTELLIGENCE_RUN`

```
DEFINICAO    uma execucao analitica identificavel
OWNER        INTELLIGENCE
IDENTITY     INTELLIGENCE_RUN_ID
INPUT        INTELLIGENCE_REQUEST + selecao de itens READY
OUTPUT       tudo o que esta espinha produz, mais a historia
STATE        NOT_RUN != ERROR != EMPTY_RESULT != NO_FINDING  (INT-LAW-053)
PERSISTENCE  append-only
PROVENANCE   EVIDENCE_SELECTION: os ITEM_IDs, e so eles
VERSIONING   CODE · BIBLE · RULESET · MODEL · PROMPT · PARAMETERS (INT-LAW-052)
REVERSIBILITY  uma corrida nao se apaga; corrige-se com outra corrida
CURRENT      NOT_IMPLEMENTED — `INTELLIGENCE_RUN` = 0 ficheiros na linha
             funcional (remedido nesta missao, contra `dc00583d`)
TARGET       a proxima missao
```

## 4.9 · `EVIDENCE`

```
DEFINICAO    NAO E UM OBJETO DA INTELLIGENCE.
             O que atravessa a fronteira e o READY_ITEM, de 12 campos.
OWNER        COLLECTION  (BIBLIA-CANONICA-DA-COLETA · COL-LAW-043)
IDENTITY     ITEM_ID + RAW_OBSERVATION_ID — e a Intelligence NAO os cunha
INPUT        —
OUTPUT       —
STATE        PRONTO_PARA_INTELIGENCIA
PERSISTENCE  data/samples/PRONTO-PARA-INTELIGENCIA/<RUN_ID>.json
PROVENANCE   da Collection, e ela nao muda por a Intelligence a ler
VERSIONING   ADMITIDO_POR = regra + versao
REVERSIBILITY  a Collection corrigir
CURRENT      IMPLEMENTED + OBSERVED — 12 campos, medidos
TARGET       +1 campo: EVIDENCE_SPECIES. E e um pedido, nao uma alteracao.
```

O que a Intelligence possui aqui é **a seleção**, não a evidência:

```
EVIDENCE_SELECTION = a aresta (RUN_ID -> ITEM_ID)
```

Chamar `EVIDENCE` ao objeto que já se chama `READY_ITEM` seria dar-lhe um
segundo nome, e a seguir um segundo dono.

## 4.10 · `COLLECTION_GAP` — ⚠️ O ACHADO MAIS CONSEQUENTE DESTA MISSÃO

A arbitragem V1 escreveu:

```
COLLECTION_GAP · OWNER = INTELLIGENCE · CURRENT_IMPLEMENTATION = NAO IMPLEMENTADO — 0 ficheiros
```

Isso é **literalmente verdade** para o token `COLLECTION_GAP`, e continua a ser
verdade hoje. Mas o **conceito** já tem dono, e a arbitragem não podia vê-lo:

```
leis/gestao_da_coleta.py   CONTRATO = 'GESTAO_DA_COLETA/v1'
                           adicionado em 220e0e7a, 2026-09-08
                           AUSENTE na branch da arbitragem (87712a01)
```

E o que ele já possui é exatamente a segunda metade do «collection gap»:

```
CAMPOS_DA_NECESSIDADE  REQUIREMENT_ID · O_QUE · JANELA · FRESCURA_EXIGIDA ·
                       GRAO · PORQUE_IMPORTA · POLICY_VERSION
CAMPOS_DA_FALTA        GAP_ID · SATISFACTION_STATE · O_QUE_FALTA · ...
DECISOES               COLLECT_NOW · COLLECT_LATER · DO_NOT_COLLECT ·
                       NEEDS_HUMAN · DEFER_UNKNOWN
A FRONTEIRA            «O GESTOR DECIDE O QUE E QUANDO;
                        O ORQUESTRADOR DECIDE COMO E POR ONDE»
                       «O GESTOR NAO CHAMA EXECUTOR»
```

**Logo, `COLLECTION_GAP` parte-se:**

```
INTELLIGENCE_REQUIREMENT   dono: INTELLIGENCE
                           a pergunta que a evidencia nao sustenta,
                           com janela, grao, frescura e porque importa

GAP · SATISFACTION · DECISION · ROTA · EXECUTOR
                           dono: COLLECTION (GESTAO_DA_COLETA/v1)
                           e a Intelligence NAO ESCREVE NENHUM DELES
```

```
DEFINICAO    ver acima — sao dois conceitos, e tinham um nome so
OWNER        REPARTIDO, e a reparticao e a propria lei
IDENTITY     REQUIREMENT_ID (Intelligence) · GAP_ID (Collection)
INPUT        um portao que nao consegue responder
OUTPUT       uma NECESSIDADE declarada
STATE        do lado da Intelligence: levantado. O estado de satisfacao e da Collection.
PERSISTENCE  append-only
PROVENANCE   a corrida que o levantou, e o portao que bloqueou
VERSIONING   POLICY_VERSION
REVERSIBILITY  um requisito pode fechar por REPROCESSAMENTO, sem nova coleta
               (INT-LAW-152, INT-LAW-223)
CURRENT      metade IMPLEMENTED (Collection, como contrato), metade
             NOT_IMPLEMENTED (Intelligence)
TARGET       a Intelligence escreve NECESSIDADE no vocabulario que ja tem dono
```

Isto é o que fecha o item `[7]` do critério de PASS: não existe caminho
paralelo de coleta porque a Intelligence **nunca chega a formar a frase** que
nomearia uma rota. `provas/espinha_da_intelligence.py` recusa 12 palavras em
código, e o teste `P10` tenta as quatro formas óbvias de as contrabandear.

## 4.11 · `SCREENING` — o portão que faltava

```
DEFINICAO    rastreio barato, com criterios visiveis, FEITO PARA DESCARTAR
OWNER        INTELLIGENCE
IDENTITY     nao tem — e a aresta SCREENED_BY + as respostas no sinal
INPUT        criterios do pacote de dominio
OUTPUT       RASTREADO ou DESCARTADO(motivo, versao da regra)
HARD GATE    um criterio duro sem SIM nao passa. NAO SEI nao vira «medio».
CURRENT      NOT_IMPLEMENTED
TARGET       primeiro portao depois de G0, e o mais barato de todos
```

O número externo que obriga este portão a existir:

```
EFSA 2017-2024: 392 pragas novas identificadas. 27 voltaram a ser mencionadas.
~7% DOS SINAIS SOBREVIVERAM A PROPRIA REPETICAO.
```

```
UM RASTREIO QUE NUNCA DESCARTA NAO E UM RASTREIO.
```

## 4.12 · `RELEVANCE` e `PRIORITY`

```
RELEVANCE_OWNER = HUMAN_DECISION_REQUIRED
PRIORITY_OWNER  = HUMAN_DECISION_REQUIRED
```

Continuam onde a arbitragem V1 os deixou: `OWNER_NEEDS_HUMAN_DECISION`, com
157 e 126 ficheiros a tocá-los e nenhuma lei a nomear dono. **Esta missão não
os decide em silêncio**, e a espinha não depende deles: nenhum portão de G0 a
G6 os consulta. Ficam explicitamente abertos.

---

# 5 · A MÁQUINA DE PROMOÇÃO

## 5.1 · A tabela do §9 do enunciado

| estágio | pergunta respondida | pode promover? | pode rejeitar? | evidência exigida | owner |
|---|---|---|---|---|---|
| `G0` identidade/espécie | de que espécie é isto, e sobre quem fala? | sim → `SIGNAL` | sim → `BLOQUEADO_EM_G0` | espécie declarada pela fonte · `FACT_TIME` · ontologia | Intelligence |
| `G1` rastreio | vale a pena olhar para isto? | sim → `RASTREADO` | **sim, e é para isso que existe** | resposta visível a cada critério | Intelligence |
| `G2` cruzamento | estes sinais falam do mesmo? | sim → `CROSSING(PROVADO)` | sim → `NOT_POSSIBLE` | chave de junção factual + grafo de dependência | Intelligence |
| `G3` hipótese | o que isto pode significar? | sim → `HIPOTESE` | sim (não nasce sem falsificador) | pergunta + premissas + o que a derruba | Intelligence (+ agrónomo) |
| `G4` validação/promoção | isto é defensável? | sim → `FINDING` | sim → `REJEITADA` | traço de decisão + nível + contraditório ligado | Intelligence + revisor humano |
| `G5` watch | quando é que isto volta à mesa? | sim → `WATCH` | sim (horizonte passa) | horizonte + gatilho | Intelligence |
| `G6` oportunidade | há algo a fazer, e a tempo? | sim → `OPPORTUNITY` | sim (janela, nível, registo) | nível A–D provado + janela composta | Intelligence propõe · MD valida |
| `DEMOTED_BY` | o que fez isto andar para trás? | **não** | sim, sempre | causa canónica + evidência | Intelligence |

## 5.2 · Transições proibidas

```
SIGNAL      -> FINDING              nao existe aresta. Ha tres portoes no meio.
CROSSING    -> FINDING              idem.
HIPOTESE    -> FINDING              sem validacao, quando o portao a exige.
FINDING     -> FINDING              sem causa canonica. Um achado nao muda de
                                    estado por alguem mudar de ideia.
QUALQUER    -> COLETOR              nao existe. Nem por requisito.
NAO SEI     -> FALSO                levanta LeiViolada.
NAO_ENCONTRADO -> ZERO_PROVED       sem universo declarado.
```

## 5.3 · A autonomia, por portão

```
AI CAN SUMMARIZE   sempre, com a fonte ao lado
AI CAN DERIVE      normalizar, ligar ontologia, calcular janela
                   ⛔ NAO: decidir que uma normalizacao 1:N e uma so
AI CAN PROMOTE     G0 · G1 · G2      ⛔ NAO: G4 · G6
AI CAN RECOMMEND   propor hipotese, propor cruzamento
AI CAN ACT         em nada, nesta V1
```

---

# 6 · A REVERSÃO

## 6.1 · As sete causas, com destino

| causa | quem dispara | destino | exemplo agro |
|---|---|---|---|
| `RECORD_INVALIDATED` | a autoridade | `REJEITADO` | ISPM 8: *pest records invalid* |
| `NO_LONGER_PRESENT` | a autoridade | `REBAIXADO` | praga erradicada; área volta a *pest free* |
| `NORMALIZATION_REVISED` | nós | `REABERTO` | a EPPO reclassifica; o `MATCH_TYPE` muda |
| `SOURCE_RETRACTED` | a fonte | `REJEITADO` | boletim corrigido; paper retratado |
| `DEPENDENCY_DISCOVERED` | nós | `REBAIXADO` | as «duas fontes» eram a mesma ONPF |
| `AUTHORIZATION_CHANGED` | o regulador | `SUBSTITUIDO` | o uso deixou de existir |
| `WINDOW_CLOSED` | o tempo | `REBAIXADO` | deixa de ser acionável — e **não** deixa de ser verdade |

## 6.2 · O que a reversão nunca faz

```
NAO APAGA O ESTADO ANTERIOR              (INT-LAW-210)
NAO REESCREVE O JULGAMENTO PASSADO       (INT-LAW-213)
NAO PERDE O TRACO DE DECISAO ORIGINAL
```

Um achado que estava certo com a evidência de Maio **continua a ter estado
certo em Maio**, mesmo que Junho o desminta. Reescrevê-lo apaga a única série
que permitiria calibrar.

## 6.3 · O caso executável (§F da entrega)

`P7.test_a_serie_completa_fica_legivel` promove um achado, reverte-o duas vezes
por causas diferentes, e confere a série completa:

```
HIPOTESE -> CONFIRMADO -> REJEITADO -> REABERTO
```

Nenhum evento foi alterado (são `frozen`), o traço de decisão original continua
a apontar para o mesmo cruzamento, e o livro da corrida só cresceu.

---

# 7 · OS CASOS AGRO A–E

| caso | entrada | resultado da máquina | prova |
|---|---|---|---|
| **A** só clima favorável | 1 `AGROCLIMATIC_SIGNAL` | **recusado**: `NIVEL_1` exige `OBSERVED_FIELD_SIGNAL`. A mensagem de recusa cita `AGROCLIMATIC_SIGNAL != PEST_OCCURRENCE` | `P1` (3 testes) |
| **B** relato isolado | 1 `OBSERVED_FIELD_SIGNAL` | gera sinal; chega a hipótese `NIVEL_1`; **não** vira achado sem validação | `P2` (2 testes) |
| **C** clima + relato | 2 sinais, mesmo sujeito, área e janela | cruzamento `PROVADO`, 2 origens independentes, hipótese `NIVEL_2`, achado após validação. **Para em `NIVEL_2`** | `P3`, `P4`, `P12` |
| **D** evidência contrária posterior | achado `NIVEL_2` + retratação | `SOURCE_RETRACTED` → `REJEITADO`, com história completa | `P6`, `P7` |
| **E** ontologia 1:N | termo `peronospora` → 3 códigos EPPO | `MATCH_TYPE = UNRESOLVED`, termo original preservado, cruzamento `NOT_POSSIBLE` | `P8` (2 testes) |

E o tecto, que esta missão **confirma** e não altera:

```
DISEASE_INTELLIGENCE_MAX_DEFENSIBLE_LEVEL = NIVEL 2
```

`NIVEL 3` exige limite de campo, variedade e data de sementeira — dado do
agricultor, e é problema de contrato, não de engenharia. `NIVEL 4` exige
denominador, população-alvo e método de diagnóstico, que **nenhuma das 13
fontes italianas contratadas declara**. E `SOURCE_DOES_NOT_PROVIDE != COLLECTION_BUG`.

---

# 8 · OPPORTUNITY — A FRONTEIRA PÚBLICO → COMERCIAL

Esta missão **não redesenha Opportunity**. Mede se a espinha a suporta.

```
NIVEL A  OPORTUNIDADE AGRONOMICA           publico: SIM
NIVEL B  OPORTUNIDADE DE PORTFOLIO REGISTADO  publico: SIM
NIVEL C  OPORTUNIDADE COMERCIAL            publico: NAO — exige dado interno
NIVEL D  OPORTUNIDADE DE VENDA             publico: NAO — exige identidade do agricultor
```

A espinha suporta o contrato existente sem lógica especial: `OPPORTUNITY` é
um destino de `FINDING` no portão `G6`, com gates próprios. O que a máquina
impõe:

```
dado so publico -> A ou B.        C e D levantam LeiViolada.
nivel nao declarado -> recusado.  «e o pior erro possivel desta casa»
CLIENT_SAFE = false sempre, e quem decide expor e a Delivery
```

E os estados que `INT-LAW-142` manda preservar (`MATCH`, `CROP_ONLY`,
`NOT_FOUND`, `UNKNOWN`, `MATERIAL_EXISTENTE_NAO_UTILIZAVEL`) **não foram
tocados**: eles vivem no objeto Opportunity, cujo dono provado é
`motor/v21_oportunidades.py`, e esta missão não lhe mexeu.

---

# 9 · CURRENT ≠ TARGET — A TABELA QUE NÃO SE PODE ARREDONDAR

| conceito | `DEFINED` | `IMPLEMENTED` | `OBSERVED` | medida |
|---|:--:|:--:|:--:|---|
| `INTELLIGENCE_REQUEST` | ✅ | ❌ | ❌ | arbitragem V1: `NOT_IMPLEMENTED` |
| `INTELLIGENCE_RUN` | ✅ | ❌ | ❌ | `grep INTELLIGENCE_RUN` = **0 ficheiros** em `dc00583d` |
| `READY_ITEM` (evidência) | ✅ | ✅ | ✅ | 12 campos, em runtime |
| `EVIDENCE_SPECIES` | ✅ | ❌ | ❌ | **0 de 12** campos |
| `SIGNAL` | ✅ | ❌ | ❌ | `ANALYTIC_SIGNAL` = 0 ficheiros |
| `SCREENING` | ✅ | ❌ | ❌ | — |
| `CROSSING` | ✅ | ✅ | ✅ | `motor/v21_crossings.py`, 8 invariantes |
| `CONVERGENCE` | ✅ | ✅ | ⚠️ | `motor/pacote_convergencia.py` |
| `JUDGMENT` (arestas) | ✅ | ❌ | ❌ | `SUPPORT`/`CONTRADICTION` = 0 como 1.ª classe |
| `ANALYTIC_HYPOTHESIS` | ✅ | ❌ | ❌ | 0 ficheiros |
| `VALIDATION` (estado) | ✅ | ❌ | ❌ | 0 ficheiros |
| `FINDING` | ✅ | ⚠️ | ❌ | `v21_fechar.py` fecha estados; sem traço |
| `REVERSAL` | ✅ | ❌ | ❌ | `REVERSAL` = 0 ficheiros |
| `INTELLIGENCE_REQUIREMENT` | ✅ | ❌ | ❌ | 0 ficheiros do lado da Intelligence |
| `GAP / DECISION / ROTA` | ✅ | ✅ (contrato) | ❌ | `leis/gestao_da_coleta.py`; **`SEM_IA_VIVA`** declarado |
| `OPPORTUNITY` | ✅ | ✅ | ✅ | `motor/v21_oportunidades.py` |

```
INTELLIGENCE_RUNTIME_IMPLEMENTED = NO
```

O que esta missão acrescenta é `PROVED_IN_DISPOSABLE`: a máquina de estados
corre, e recusa o que tem de recusar, em `provas/espinha_da_intelligence.py`.
**Isso não é runtime.** É a forma executável do contrato.

---

# 10 · AS PROVAS

```
python3 -m unittest tests.test_espinha_da_intelligence -v     39 testes
python3 -m unittest discover -s tests                        368 testes, OK
```

| prova | o que morde | testes |
|---|---|---|
| `P1` | clima favorável não vira ocorrência | 3 |
| `P2` | signal não vira finding sem promoção | 2 |
| `P3` | crossing preserva as evidências, herda o pior lado, não julga | 3 |
| `P4` | cada julgamento tem regra, evidência e motivo; o traço chega ao achado | 3 |
| `P5` | candidato rejeitado não produz achado; sem falsificador não nasce | 2 |
| `P6` | as 7 reversões; causa sem nome canónico é recusada | 4 |
| `P7` | a série completa fica legível; os eventos são imutáveis | 2 |
| `P8` | 1:N fica `UNRESOLVED` com o termo original; cruzamento `NOT_POSSIBLE` | 2 |
| `P9` | `NAO SEI` não vira falso; o rastreio sabe dizer não | 4 |
| `P10` | falta de evidência produz requisito; 12 palavras recusadas; **a máquina não tem porta para rede** | 4 |
| `P11` | dois domínios na mesma espinha; o pacote de domínio não traz comportamento | 3 |
| `P12` | dado público chega a A e B; C e D levantam lei | 4 |
| `FronteiraMedida` | o CURRENT, escrito como teste para não virar lembrança | 3 |

O último merece nota: se um dia o contrato READY passar a transportar a espécie
da evidência, `FronteiraMedida` **falha** — e falhar é o comportamento certo.

```
UM TESTE QUE SO CONFIRMA O CAMINHO FELIZ NAO PROVA UMA LEI:
PROVA UM EXEMPLO.
```

---

# 11 · A MESMA ESPINHA, DOIS DOMÍNIOS

`P11` corre o domínio `REGULATORIO` pelos **mesmos sete portões**, com a mesma
máquina, e obtém achado e reversão (`AUTHORIZATION_CHANGED → SUBSTITUIDO`).

O que muda entre domínios é **dado**, e o teste
`P11.test_o_dominio_so_traz_dados_nunca_portoes` prova-o de duas maneiras: a
lista de campos de `PacoteDeDominio` é fechada, e nenhum valor de nenhum pacote
é chamável.

```
UM DOMINIO QUE PRECISASSE DE UM PORTAO PROPRIO
NAO SERIA UM PACOTE: SERIA UMA SEGUNDA ARQUITETURA.
```

E é por isto que esta missão **não** criou Disease Intelligence, Climate
Intelligence, Market Intelligence nem Science Intelligence. Elas são pacotes.

---

# 12 · `CONTROL_PLANE_ATOMICITY`

Pergunta obrigatória do §17: existe algum commit que contenha simultaneamente
Bíblia, Motor V2, censo/arbitragem, authority registry, benchmark agro e
know-how?

| autoridade | commit | Bíblia | Motor V2 | Arbitragem | Registry | Agro | Know-how |
|---|---|:--:|:--:|:--:|:--:|:--:|:--:|
| `research/intelligence-bible-engineering-v1` | `7ae1b510` | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ |
| `claude/intelligence-backlog-canonical` | `4df24aa9` | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ |
| `claude/funny-hypatia-y7ho5s` | `87712a01` | ❌ | ❌ | ✅ | ✅ | ❌ | ❌ |
| `claude/epic-archimedes-ryo0ms` | `dc00583d` | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ |
| `claude/sintonia-eame-know-how-v1` | `338e171a` | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| `origin/main` | `f437ff11` | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **esta branch** | `6afba2ef` | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |

```
CONTROL_PLANE_ATOMICITY = FAIL
```

E esta missão mediu **o custo real** dessa fragmentação, em vez de o repetir
como slogan:

```
A ARBITRAGEM V1 DECLAROU `COLLECTION_GAP` COMO «0 FICHEIROS».
O CONCEITO JA TINHA DONO EM `leis/gestao_da_coleta.py` DESDE 2026-09-08.
A BRANCH ONDE A ARBITRAGEM FOI FEITA NAO TEM ESSE FICHEIRO.

UMA MEDICAO CORRECTA NUMA FOTOGRAFIA INCOMPLETA
PRODUZ UMA CONCLUSAO ERRADA — E PARECE RIGOROSA.
```

**Não se fez merge.** Entre histórias desconexas não existe «integração pequena
e sem conflito», e o §17 manda `HARD STOP` na ambiguidade.

---

# 13 · O PLANO DE INTEGRAÇÃO, EXATO

Não é uma sugestão: é a sequência mínima, e nenhum passo é desta missão.

```
1. ESCOLHER O TRONCO
   Candidato medido: `claude/epic-archimedes-ryo0ms` @ dc00583d
   Porque:  contem a linha funcional (f888776d e antecessor),
            contem `leis/gestao_da_coleta.py`, contem `admissao/`,
            contem `motor/`, e contem o benchmark agro inteiro.
   Falta-lhe: Biblia, Motor V2, arbitragem, registry, know-how.

2. TRAZER, POR ORDEM DE DEPENDENCIA
   a. know-how canonico        338e171a   (nao tem conflito de ficheiro)
   b. Motor V2 requisitos      4df24aa9   (docs/intelligence/)
   c. arbitragem + censo       87712a01   (docs/intelligence/ + docs/operacao/)
   d. Biblia V0.2 + registry   7ae1b510   (raiz + controle/)
   ⚠️ (c) e (d) tocam ambos `controle/AUTORIDADES-CANONICAS.json`.
       E o unico conflito previsto, e e de conteudo, nao de estrutura.

3. RE-MEDIR A ARBITRAGEM CONTRA O TRONCO
   Obrigatorio: `COLLECTION_GAP` muda de veredito (§4.10), e podem existir
   outros conceitos cuja medicao dependia da fotografia incompleta.

4. REGENERAR O SYSTEM MAP pela cadeia canonica. Nunca a mao.

5. SO ENTAO decidir promocao da Biblia.
```

---

# 14 · O QUE NÃO MUDOU

```
COLLECTION_RUNTIME   INTACTO — nenhum ficheiro de coleta/, admissao/, guarda/,
                     leis/ ou orquestrador/ foi lido para escrita nem alterado.
                     Esta branch nem sequer os contem.
SALA_DE_ESPERA       INTACTA — 0 leituras, 0 escritas
MIGRATIONS           INTACTAS — nenhuma criada, nenhuma aplicada
LIVE                 0 leituras · 0 escritas
PORTAL               INTACTO
CASCO / UI           INTACTOS
motor/               INTACTO — esta branch nao o contem
BIBLIA DA COLETA     NAO ALTERADA
BIBLIA DA INTELLIGENCE  NAO ALTERADA, NAO PROMOVIDA
SYSTEM MAP           NAO APLICAVEL nesta branch (nao ha geradores aqui)
```

⚠️ **O que mudou, e não é Intelligence:** adicionar 39 provas a esta branch fez
a suite passar de 329 para 368 testes, e a branch tem um portão que exige que
todo número publicado venha do seu dono. Regenerou-se pelo gerador canónico
(`scripts/metricas_canonicas.py --sync`), nunca à mão. Ver `§15`.

---

# 15 · O DEFEITO QUE ESTA MISSÃO ENCONTROU NO PORTÃO DA PRÓPRIA BRANCH

Ao correr o gerador canónico, dois ficheiros da raiz publicavam
`TEST_COUNT_CURRENT` e o `--sync` **não lhes chegava**: o walk só via `docs/`.

```
tests/test_handoff.py EXIGE o numero certo em HANDOFF e PROMPT.
scripts/metricas_canonicas.py --sync NAO CONSEGUIA la chegar.
Logo: o unico jeito de passar o portao era DIGITAR o numero
      — exactamente o que o ledger existe para impedir.
```

Corrigido **na fonte**, como o §18 do enunciado manda:

- `_marcados()` passa a incluir os `.md` da raiz;
- os dois números ganharam marcador e passam a ser derivados;
- `repl()` deixa de rebentar em marcador sem dono no ledger — havia um
  `<!--M:NOME-->` na raiz que é o **exemplo da sintaxe**, escrito em prosa, e
  o sincronizador tentava reformatá-lo (`ValueError: Cannot specify ',' with 's'`);
- o teste passa a aceitar o marcador, continuando a exigir o valor certo.

```
UM PORTAO QUE SO SE SATISFAZ A MAO NAO E UM PORTAO: E UM LEMBRETE.
```

---

# 16 · VEREDITOS

```
INTELLIGENCE_SPINE_CONTRACT_READY = YES
PROMOTION_MODEL_READY             = YES (contrato) · NO (matéria-prima)
REVERSAL_MODEL_READY              = YES
VALIDATION_MODEL_READY            = YES
COLLECTION_GAP_CONTRACT_READY     = YES — e com o dono corrigido
ONTOLOGY_BOUNDARY_READY           = YES
OPPORTUNITY_BOUNDARY_READY        = YES
CONTROL_PLANE_ATOMICITY           = FAIL
INTELLIGENCE_RUNTIME_IMPLEMENTED  = NO
```

O detalhe que o `PROMOTION_MODEL_READY` duplo esconde, e não deve esconder:

```
O CONTRATO ESTA PRONTO: os sete portoes existem, cada um sabe recusar,
                        e as recusas estao sob teste.
A MATERIA-PRIMA NAO:    G0 bloqueia hoje, porque a especie da evidencia
                        nao atravessa a fronteira.

UM PORTAO QUE NAO RECEBE O DADO NAO RECUSA: DEIXA PASSAR.
E POR ISSO O PORTAO G0 DESTA MAQUINA RECUSA POR OMISSAO,
E LEVANTA UM REQUISITO EM VEZ DE ADIVINHAR.
```

---

# 17 · O QUE FICA EM NÃO SEI

```
NAO_SEI  quem possui RELEVANCE e PRIORITY. Continua a exigir decisao humana.
NAO_SEI  se KIT/KIQ, FIELD_VOICES e DECISION_TELEMETRY entram na Biblia antes
         da promocao. O inventario pediu-os; a V0.2 nao os tem.
NAO_SEI  se `CONFIDENCE` deve ter escala congelada. O red team da Biblia
         deixou-o em NEEDS_CONTRACT, e esta missao nao o mede.
NAO_SEI  quantos dos 22 conceitos da arbitragem V1 mudam de veredito quando
         re-medidos contra um tronco completo. Um mudou (§4.10). Nao sei se
         e o unico, e nao o infiro.
NAO_SEI  se o `UNIVERSO` do contrato READY chega para definir o universo
         analitico exigido por INT-LAW-110/111. Nao foi medido nesta missao.
NAO_SEI  o custo real dos sete portoes em corpus real. Nada aqui correu
         contra a Sala de Espera.
```

Nenhum destes foi preenchido por inferência.

---

# 18 · A PRÓXIMA MISSÃO — UMA, E SÓ UMA

```
C-INT-ATOMICITY-01

   Construir o tronco unico da Intelligence: um commit que contenha
   simultaneamente Biblia V0.2, Motor V2, arbitragem, censo, authority
   registry, know-how canonico e benchmark agro — pela sequencia do §13 —
   e RE-MEDIR a arbitragem contra ele.

   NAO promove a Biblia.  NAO implementa INTELLIGENCE_RUN.  NAO toca Collection.
```

**Porquê esta e não `INTELLIGENCE_RUN`:** a Bíblia fixa como primeira missão
pós-promoção o contrato mínimo de `INTELLIGENCE_RUN` — mas a promoção está
bloqueada pela atomicidade, e esta missão acaba de provar que medir sobre uma
fotografia incompleta produz conclusões erradas com aparência de rigor.
Implementar `INTELLIGENCE_RUN` antes de fechar o tronco é construir sobre a
mesma fotografia.

```
KNOW_HOW_DELTA = ATUALIZACAO NECESSARIA
```

Ver `handoff/KNOW-HOW-DELTA-INTELLIGENCE-SPINE.md`.
