# OS PORTÕES DA COLLECTION V1

`MEASURE != FIX` na medição. Os fechos abaixo vieram de missões próprias,
cada uma com a sua prova.

## O veredito

```
COLLECTION_CORE_CLOSE = FAIL
BIG_COLLECTION_READY  = FAIL

BLOCKERS            = 0
NON_BLOCKING_DEBT   = 5
ROOT_CAUSES         = 4
MISSÕES ATÉ FECHAR  = UNKNOWN
```

E a certificação que a última missão foi pedir — a Collection V1 como máquina
operacional completa, **excluindo só o SCRAP**:

```
COLLECTION_V1_CORE_READY_WITHOUT_SCRAP         = NO
ONLY_REMAINING_ACQUISITION_DEPENDENCY_IS_SCRAP = NO
```

O segundo é o que surpreende, e está medido: o buraco que resta é
`ADMISSION -> READY`, e **integrar o SCRAP não o tapa**. O SCRAP continua a ser
preciso antes da coleta grande — mas não é a única coisa que falta, e dizer que
é autorizava começar pela peça errada.

E a classe que fecha a máquina está nomeada, com o blocker dela:

```
CANONICAL_CANARY_CLASS_RECOMENDADA = T4 (Regulatório)
BLOCKER_REAL  = o executor de T4 não declara COLHEITA
É O SCRAP?    = NO
```

Este veredito não vem da média das 105 leis. Vem das propriedades que a
coleta grande precisa de ter, e cada falha aponta a propriedade que falta.

## Os dois eixos, que não se inferem

| eixo | natureza | fonte |
|---|---|---|
| `IMPLEMENTATION_STATE` | declarado pela Bíblia | `docs/biblia/leis.json` |
| `CLOSE_GATE` | **medido** | esta linha de missões |

> UMA LEI `PARTIAL` PODE NÃO BLOQUEAR NADA,  
> E UMA LEI PEQUENA PODE BLOQUEAR TUDO.

Medido: **48 leis `PARTIAL`** e **0 blockers**. Nenhum blocker foi derivado
do estado de lei.

## A estrada canónica

Duas colunas, e a segunda é a que responde à pergunta que as pessoas fazem.

| etapa | módulo | aresta | já correu | **pelo pedido** |
|---|---|---|---|---|
| `REQUEST` | YES | YES | YES | **SIM** |
| `ORCHESTRATOR` | YES | YES | YES | **SIM** |
| `EXECUTOR` | YES | YES | YES | **SIM** |
| `RUN` | YES | YES | YES | **SIM** |
| `RAW_OBSERVATION` | YES | YES | YES | **SIM** |
| `STORAGE_OBJECT` | YES | YES | YES | **SIM** |
| `DERIVED` | YES | YES | YES | **SIM** |
| `STRUCTURED` | YES | YES | YES | **SIM** |
| `ADMISSION` | YES | YES | YES | **SIM** |
| `READY` | YES | YES | YES | **NÃO** |
| `WAITING_ROOM` | YES | YES | YES | **NÃO** |

> MÓDULO EXISTE ≠ ARESTA EXISTE ≠ FLUXO EXECUTADO.

Todas as onze etapas já atravessaram. **E isso não é a estrada.**

> **DUAS METADES PROVADAS NÃO SÃO UMA ESTRADA PROVADA.**
> **ONZE ETAPAS QUE JÁ CORRERAM NÃO SÃO UMA HISTÓRIA.**

**Nove das onze atravessam agora na história do pedido** — de `REQUEST` até
`ADMISSION`, com o executor a ir à fonte real. As duas últimas atravessam só na
rota forward, que entra pelo `RAW` e não pelo pedido. Por isso o portão não soma
`YES`: exige a **mesma história**, medida por quem aperta o botão no pedido.

⚠️ **A coluna «pelo pedido» deixou de ser escrita à mão.** Já esteve escrita, e
envelheceu três vezes: dizia «`DERIVED` e `STRUCTURED` só atravessam na rota
forward» muito depois de as duas terem passado a atravessar pelo pedido. Agora é
lida de `system-map/data/pedido.observado.json`, que é escrito por quem mede.

> **O CENSO NÃO DECIDE ONDE A ESTRADA PARA. ELE LÊ QUEM MEDIU.**

Sem ambiente descartável a medição **não corre**, e isso diz-se: `SKIP != PASS`
e `NOT_MEASURED != PASS`.

## Os blockers

**Nenhum.** E isso **não** quer dizer que o core fechou.

```
COLLECTION_CORE_CLOSE     = FAIL
BLOQUEADO_POR             = []
CANONICAL_E2E             = NOT_PROVEN
CANONICAL_E2E_SAME_STORY  = FAIL
```

> **ZERO BLOCKERS ≠ CORE FECHADO.**

A mesma história parou em `ADMISSION -> READY`, medido em
[`provas/o_pedido_atravessa.py`](../../provas/o_pedido_atravessa.py).

E parou por um motivo que não se parece com nenhum dos anteriores: **não falta
peça nenhuma.**

## Onde a estrada se parte, e são três achados

Um pedido real atravessa `REQUEST → ORCHESTRATOR → EXECUTOR → RUN → RAW →
STORAGE → DERIVED → STRUCTURED → ADMISSION` numa história só, com o executor a
ir à fonte real. E para.

```
LAST_PROVEN_STAGE   = ADMISSION
FIRST_LOST_EDGE     = ADMISSION -> READY
NEXT_EXPECTED_STAGE = READY
```

Os três achados são de **espécies diferentes**, e não se misturaram — um
resolvia-se com código, o segundo com uma separação, o terceiro não se resolve
com nenhum dos dois. Os dois primeiros fecharam.

| aresta | tipo | quem resolve | estado |
|---|---|---|---|
| `STORAGE -> DERIVED` | `WIRING_GAP` | código | **FECHADO** |
| `DERIVED -> STRUCTURED` | `CONTRACT_OWNER_GAP` | gente | **FECHADO** |
| `ADMISSION -> READY` | `EMPTY_INTERSECTION` | gente | **ABERTO** |

**`STORAGE -> DERIVED` — WIRING_GAP, fechado.**
A capacidade existia e ninguém a chamava. A porta passou a devolver as
observações que o banco **confirmou**, cada uma com o endereço do byte dela, e o
orquestrador entrega-as ao runner canónico da derivação. A mesma corrida escreve
`derived_artifact` com pai real e deixa passagem `DERIVED` com `edge_from=RAW`.

> **CAPABILITY EXISTS ≠ EDGE EXISTS.**
> Uma capacidade que ninguém chama não é uma etapa da estrada.

O par (observação, bytes) sai inteiro da linhagem — `raw_asset.id` e o
`storage_path` do objeto ligado a ela. Não há ficheiro procurado no disco:
emparelhar o primeiro ficheiro da pasta com a primeira linha da tabela dá um
derivado com o pai errado, e `PATH ≠ IDENTITY`.

E fechar uma ligação não fecha a estrada: fecha uma ligação. O primeiro buraco
andou uma aresta para a frente, o que estava previsto e escrito antes de se
ligar.

**`DERIVED -> STRUCTURED` — CONTRACT_OWNER_GAP, fechado por separação.**

Esta ficou aberta uma missão inteira à espera de uma decisão de gente, com a
pergunta escrita no fim deste documento: *de quem é o `canal` de uma agência
pública que publica boletins em PDF?*

⚠️ **A resposta foi que a pergunta estava mal posta.** Um boletim em PDF **não
tem canal** — e por isso a pergunta não tinha resposta. `public.conteudo` é a
casa de conteúdo **de plataforma**: `canal.channel_id` está comentado como «o id
da plataforma, NUNCA o nome», e `conteudo.content_id` como «id da plataforma
(video_id, post_id)». A tabela pressupõe uma plataforma que emita
identificadores, e uma agência regional não é uma.

```
    ONE CONCEPT → ONE OWNER
    ≠ ONE TABLE FOR EVERY TYPE OF CONTENT
```

Foi escolhida a **opção B** das três que estavam em espera: fontes documentais
não têm canal, e `conteudo` não é a casa delas. A casa nova é
`public.documento_estruturado` (migration `030`), com um único dono de escrita,
[`guarda/preservar_documento.py`](../../guarda/preservar_documento.py). A chave é
`derived_artifact_id`: o documento é o registo estruturado **daquele** derivado.

**O que não foi fabricado, e fica escrito porque é a parte que interessa:**

| valor | estado |
|---|---|
| `canal_id` | **não criado** — nenhuma linha nova em `canal` ou `origem` |
| `channel_id` | **não criado** |
| `content_id` de plataforma | **não criado** |
| `document_id` | **`NULL`** — só se escreve quando a fonte o prova |

O `document_id` tem trava no esquema contra o atalho óbvio
(`document_id <> hash_texto`) e trava no dono contra os outros
(`hash_texto`, `source_url`, `storage_path`, `sha256`, nome do ficheiro). Um
hash identifica **bytes**; um caminho é uma **morada**. Nenhum dos dois é a
identidade que um emissor atribuiu a um documento.

> **SOURCE ≠ ENDPOINT ≠ ARTIFACT ≠ DOCUMENT.**

**E o que continua a não existir:** o criador de identidade de `canal`. Ele
**não** nasceu aqui. Um documento não-plataforma deixou de precisar dele — o que
não é a mesma coisa que tê-lo. Conteúdo de plataforma continua a esbarrar nele, e
é isso que `G-STRUCT-01` passou a nomear.

Medido em `provas/o_pedido_atravessa.py::E1..E5`: o documento fica escrito, sem
`document_id` inventado, com `SOURCE_ID` provado pela fonte, sem canal nenhum
criado, e a linhagem anda **documento → participação → observação**.

**`ADMISSION -> READY` — EMPTY_INTERSECTION, aberto.**

Este é o mais raro dos três: **tudo o que ele precisa existe, e ainda assim nada
passa.** A porta existe, julga os quatro itens e responde. As regras temáticas
existem. Os executores existem.

```
universos com regra de admissão escrita         T3 · T4 · T7 · T9
universos cujo executor declara colheita        T2
interseção                                      VAZIA
```

A porta responde `NAO_SE_APLICA` aos quatro itens, e diz porquê por escrito:
«não há regra escrita do que conta como «T2». Sem regra, esta porta não inventa
uma.» **A recusa está certa.** `COL-LAW-505` manda que só colheita entre no
ingresso, e `COL-LAW-502` manda que a porta pergunte pela regra do universo. As
duas leis estão a ser cumpridas.

> **FALTA DE PEÇA ≠ PEÇAS QUE NÃO SE CRUZAM.**

### E depois mediu-se o que faltava a cada classe, e a parede virou fila

«A interseção é vazia» é verdade e não ajuda a decidir. Entre classes todas
paradas, nenhuma parece mais perto do que as outras até alguém contar **o que
falta a cada uma**. Medido em
[`provas/o_canario_da_collection.py`](../../provas/o_canario_da_collection.py),
sobre as onze classes da taxonomia:

| classe | aquisição | structured | regra | falta |
|---|---|---|---|---|
| **T2** · Clima e tempo | **SIM** | **SIM** | NÃO | só a **regra** |
| **T4** · Regulatório | NÃO | **SIM** | **SIM** | só a **aquisição** |
| T3 · Praga e doença | NÃO | — | SIM | aquisição + structured |
| T7 · Ciência e ensaio | NÃO | — | SIM | aquisição + structured |
| T9 · Concorrente | NÃO | NÃO | SIM | aquisição + structured |
| T1 · T5 · T10 · T11 · T12 · T13 | NÃO | — | NÃO | as três |

```
CANONICAL_CANARY_CLASS = NONE      (ninguém atravessa hoje)
A UMA PEÇA DE DISTÂNCIA = T2 · T4
```

⚠️ **O país não entra nesta conta, e isso foi medido.** A medição anterior
perguntou só por `pais=IT`. `receitas.resolver` escolhe executores por
`EXECUTORES.get(alvo)` e o país filtra **fontes**, nunca executores — conferido
em cinco países. Uma resposta de um país só não era uma resposta.

### As duas peças não são iguais, e é isso que decide

Uma peça e uma peça, e as duas classes parecem empatadas. Não estão:

```
T2 · falta a REGRA       ->  já foi medida, e REPROVADA
T4 · falta a AQUISIÇÃO   ->  nunca foi tentada: é trabalho por fazer
```

**A regra de T2 foi medida contra 46 documentos reais, e o portão fechou.**
Isso não é novo desta missão — está em
[`provas/a_regra_de_t2.py`](../../provas/a_regra_de_t2.py) e em
[`docs/operacao/MEDICAO-DA-REGRA-T2.md`](MEDICAO-DA-REGRA-T2.md), e foi
reconfirmado aqui ao correr outra vez:

```
gabarito       10 positivos · 33 negativos · 3 ambíguos não arredondados
nenhum termo aparece nos 10 positivos e em ZERO negativos
`vento`        30 dos 33 NEGATIVOS · 7 dos 10 positivos
GENERALIZACAO  0/10
```

A lista que separa o gabarito **existe** — e é feita de `venerdì`,
`pomeriggio`, `dipartimento`, `unità organizzativa`. Dias da semana e o nome do
departamento que imprime.

> **NÃO É VOCABULÁRIO DE CLIMA. É A IMPRESSÃO DIGITAL DE QUEM IMPRIME.**
> **UMA REGRA QUE SÓ ACERTA EM QUEM JÁ VIU NÃO É UMA REGRA.**

### Por que T2 não tem regra — a classificação, com as três metades

A missão pediu A, B, C ou D. **Nenhuma das quatro serve inteira**, e dizer só
uma letra mandaria a próxima pessoa para o sítio errado:

| letra | o que diria | por que não serve sozinha |
|---|---|---|
| **A** · deveria ter regra e está ausente | manda escrever a lista | a lista foi procurada exaustivamente e reprovada |
| **B** · correctamente não deve ter regra | manda desistir de T2 | T2 é um universo canónico com 5 fontes e 10 positivos reais |
| **C** · dois universos incompatíveis | manda refazer a taxonomia | as duas listas estão na **mesma** taxonomia |
| **D** · UNKNOWN | manda medir | já foi medido |

A resposta medida **não é sobre o universo — é sobre o mecanismo**:

```
O_UNIVERSO_E_LEGITIMO = YES
O_QUE_FALHA           = MECANISMO
```

Uma lista plana de palavras não distingue *«documento SOBRE clima»* de
*«documento que MENCIONA clima»* — e as palavras óbvias de clima aparecem
**mais fora** de T2 do que dentro, porque um boletim de praga fala do tempo a
que a praga responde. Para escrever a regra faltam duas coisas que esta casa
não tem: uma **lei** que diga o que é ser *sobre* um assunto, e um **mecanismo**
que conte sinais em vez de parar na primeira palavra.

E há um resíduo de `C` que a própria medição registou, e que fica escrito
porque é verdadeiro e é caro:

> **TERRITÓRIO É PROPRIEDADE DA FONTE. UNIVERSO É PERGUNTA AO DOCUMENTO.**
> A ARPAV publica `Meteo Veneto` (T2) **e** `U.O. Fitosanitario — VITE` (T3).
> O publicador não decide o território.

### O canário, e o blocker real

```
CANONICAL_CANARY_CLASS_RECOMENDADA = T4 (Regulatório)
```

T4 é a única classe a uma peça de distância cuja peça em falta **não foi medida
e reprovada**. Ela já tem regra temática escrita e já tem dono `STRUCTURED`
documental — a mesma casa que T2 usa, porque a espécie é a mesma: PDF oficial.

**O blocker real, nomeado:**

```
o executor de T4 não declara COLHEITA
onde        pedido/receitas.py::EXECUTORES['T4'] -> retorno
hoje        declara LEGADO (MANIFEST) — suporte, nunca colheita
falta       um ENVELOPE por corrida, com RUN_ID, EXECUTOR_ID,
            EXECUTOR_VERSION, ESTADO e as listas COLHEITA/SUPORTE/ERROS
quem        código — e é trabalho de AQUISIÇÃO
```

⚠️ **E não é o SCRAP.** O SCRAP é uma capacidade social e não colhe documento de
ministério. Integrá-lo não muda uma linha do retorno de T4.

**O que ficou medido e não resolvido, sobre o ambiente:** a fonte de T4
(`www.fitosanitari.salute.gov.it`) **não passa a verificação de TLS** deste
ambiente — o servidor não envia a cadeia intermédia, e o erro é
`unable to get local issuer certificate`. Medido em 2026-09-13; a fonte de T2
(`www.arpa.veneto.it`) responde `200` no mesmo ambiente e no mesmo instante.
Não se desligou a verificação, e por isso **a aquisição de T4 não foi provada
aqui**. Isto é um facto sobre o ambiente, e não sobre a arquitectura: os dois
ficam escritos separados de propósito.

### O que o fecho desta ligação revelou, e não consertou

O grão do derivado é por **bytes do pai**, e não por observação:
`derivacao_e_unica_por_regua` é `UNIQUE` sobre `parent_sha256`. Duas observações
distintas dos mesmos bytes — o mesmo boletim colhido em duas corridas —
partilham **um** `derived_artifact`, e esse artefato nomeia como pai só a
primeira delas.

Medido: segunda corrida, quatro observações novas, `DERIVED PASS` com
`reused=4` e zero linhas novas. `REUSED ≠ NOT_RUN`: a etapa correu e o
resultado já existia.

Fica escrito porque tem consequência: uma corrida cujos bytes já foram
derivados antes não tem `derived_artifact` próprio, mesmo tendo a etapa
corrido. Mudar isso é mexer na régua de unicidade do dono do derivado, e esta
medição mede a cardinalidade em vez de a redefinir.

**E foi medido a seguir, até ao fim.** A `022` decidiu o grão com a razão
escrita, e essa decisão fica. O que não se sustenta é a frase ao lado dela —
que as irmãs se encontram por `where sha256 = parent_sha256` e por isso
«nenhuma procedência se perde». Essa consulta responde «que observações têm os
mesmos bytes», e não «que observações passaram por esta derivação».

```
DERIVED_REUSE_LINEAGE = GAP_CONFIRMED
DURABLE_EDGE_A_TO_X   = YES
DURABLE_EDGE_B_TO_X   = NO
```

Nenhuma tabela do esquema inteiro aponta para `derived_artifact` — medido pelo
catálogo do Postgres, e não por memória. E `guarda/preservar_derivado.py`
**conhece** a aresta: no reencontro devolve os dois lados, e não escreve
nenhum.

> **RUNTIME SABE ≠ O SISTEMA GUARDA.**

E a decisão está fechada: a participação é uma **relação material**, com grão
`(observação, derivado)` e sem a corrida na chave — medido em quatro casos, onde
uma aresta foi tocada por seis passagens sem nunca mudar.

> **DOIS CONCEITOS, DOIS DONOS — E SÓ UM DELES PRECISA DE NASCER.**
> A execução já tem casa em `etapa_da_corrida`.

A decisão está em
[`docs/decisoes/ADR-LINHAGEM-DO-REAPROVEITAMENTO-V1.md`](../decisoes/ADR-LINHAGEM-DO-REAPROVEITAMENTO-V1.md),
e **já foi implementada**: `public.participacao_na_derivacao` (migration `029`),
com `guarda/preservar_derivado.py` como único dono de escrita. A observação
declara que participou nos três desfechos — `INSERTED`, `REUSED` e
`REUSED_AFTER_RACE` — e não em dois deles.

```
PARTICIPACAO  chave (raw_asset_id, derived_artifact_id)
              first_seen_derivation_run_id  →  a corrida que VIU primeiro
```

A corrida fica **fora da chave** e dentro da linha: ela diz *quando se soube*,
e não *o que é a aresta*. E não é herdada de `raw_asset.run_id` — vem da corrida
que está a correr, transportada pelo orquestrador como
`contexto_da_passagem`. O executor continua a não saber o que é uma corrida:
**transportar não é conhecer**.

Sem corrida na mão, o dono devolve `PARTICIPACAO_SEM_CORRIDA` e não escreve
linha nenhuma. Histórico anterior a esta migration fica `UNKNOWN`: não houve
backfill por `parent_sha256`, porque isso escreveria como observado o que foi
inferido.

> **HISTÓRICO SEM ARESTA = UNKNOWN.**

A medição corre em
[`provas/a_linhagem_do_reaproveitamento.py`](../../provas/a_linhagem_do_reaproveitamento.py)
— oito casos, com quatro fios em concorrência a produzirem **uma** linha, e o
`RESTRICT` a recusar apagar uma observação que participou.

## Os que já fecharam

Ficam na lista com o estado novo. Um gap que some não deixa ver que
existiu, nem por que deixou de existir.

| id | o que mudou |
|---|---|
| `G-E2E-01` | 25 de 25 passam contra PostgreSQL 16 com as migrations 001..027, e a prova da rota devolve ROTA_M2_ATRAVESSA=PASS sobre banco virgem |
| `G-RUN-01` | a fronteira traduz a ausencia para a palavra que o dono de CADA campo entende; `NOT_PRESERVED` continua a valer nos outros |
| `G-RAW-01` | a etapa RAW deixa passagem em `etapa_da_corrida`, e a passagem nomeia a observação que produziu (`raw_asset_id`, migration 028) |
| `G-READY-01` | a rota forward produz READY na mesma corrida: as cinco etapas falam no rastro |
| `G-READY-02` | a sala tem UM dono, escrita atómica, retry idempotente e conflito explícito |

## Quem fala, medido

| etapa | fala? |
|---|---|
| `RAW` | **SIM** |
| `DERIVED` | **SIM** |
| `STRUCTURED` | **SIM** |
| `ADMISSION` | **SIM** |
| `READY` | **SIM** |

Não é uma lista escrita à mão: vem de AST sobre o código de produção — quem
chama `rastro.registrar`, e com que `etapa=`. Um comentário que nomeie uma
etapa não conta.

> UMA ETAPA MUDA PODE ESTAR A CORRER.
> `MUDA != PARADA` — e esse é o problema.

As cinco falam. A tabela diz **quem sabe falar**, e não **quem falou nesta
corrida** — são duas perguntas, e a segunda mede-se na estrada, acima. Nesta
corrida do pedido falaram `RAW`, `DERIVED` e `ADMISSION`; `READY` não falou
porque não houve `READY`.

## A dívida que não bloqueia

| id | porque não bloqueia |
|---|---|
| `G-STRUCT-01` | STRUCTURED atravessa numa classe e não nas duas: a DOCUMENTAL passa pelo pedido; a PLATAFORMA espera por um dono de identidade de canal, que é da frente social. É dívida de COBERTURA, não de ausência de travessia. |
| `G-ADM-01` | o ledger prova ADMISSION observada na rota forward, com caminho bom e caminho de falha. A infraestrutura ATRAVESSA; o que falta e a cobertura do tipo `derived_artifact`. |
| `G-TEL-01` | nao impede executar nem preservar. Impede LER o que aconteceu, e isso e divida de observabilidade, nao de fecho. |
| `G-TEMA-01` | NAO bloqueia a coleta grande. A funcao da coleta grande e ADQUIRIR e PRESERVAR; admitir bem e a etapa seguinte, e a Admission ja produz decisao auditavel com NAO_SEI de p |
| `G-LEG-01` | nao impede propriedade nenhuma da coleta grande: os 13 estao FORA da Collection operacional por decisao, e o que entra pela frente nao passa por este estado. |

## As causas-raiz

**`RC-A` · a estrada acaba na ADMISSION e READY fica do outro lado**

Sintomas: `G-READY-01`, `G-READY-02`. Dono: admissao/admissao.py + quem decidir o destino.

os dois sao a mesma falta vista de dois lados: nao ha travessia de ADMISSION para READY, e nao ha onde pousar. Consertar so um entrega zero unidades.

**`RC-B` · duas linguas para a ausencia, e a fronteira nao traduz**

Sintomas: `G-RUN-01`. Dono: coleta/ingresso.py::_corrida_completa.

NOT_PRESERVED e NAO_SEI sao dois donos da mesma pergunta. E a MESMA familia do defeito do SOURCE_ID: um valor honesto de um lado que o outro lado nao aceita.

**`RC-C` · a estrada canonica nao tem prova que corra hoje**

Sintomas: `G-E2E-01`, `G-RAW-01`. Dono: tests/test_m2_rota_forward.py + guarda/preservar_coleta.py.

os dois sao a mesma cegueira: a estrada corre e nao se consegue ver. Um porque o retrato esta velho, o outro porque a etapa e muda. E depende de RC-B: uma prova E2E que corra vai bater no enum assim que a corrida nao declarar pais.

**`RC-D` · o SCRAP ainda nao entrega pelo contrato canonico**

Sintomas: `SCRAP_RAW_NAO_RECEBIDO`. Dono: frente do SCRAP — fora desta medicao.

nao e do core: e a integracao que vem DEPOIS do core fechar. Fica na DAG da coleta grande, e nao na do fecho.

## Missões já fechadas

| missão | fechou |
|---|---|
| `C-FIX-ABSENCE-VOCABULARY-AT-THE-RUN-SEAM-V1` | `G-RUN-01` |
| `C-RESTORE-CANONICAL-E2E-PROOF-V1` | `G-E2E-01` |
| `C-MAKE-RAW-OBSERVABLE-V1` | `G-RAW-01` |
| `C-CLOSE-READY-WITH-CANONICAL-WAITING-ROOM-V1` | `G-READY-01` · `G-READY-02` |
| `C-WIRE-STORAGE-TO-DERIVED-IN-CANONICAL-E2E-V1` | a aresta `STORAGE -> DERIVED` |
| `C-DECIDE-DERIVED-REUSE-LINEAGE-V1` | mediu `DERIVED_REUSE_LINEAGE = GAP_CONFIRMED` |
| `C-DECIDE-DERIVED-PARTICIPATION-GRAIN-V1` | decidiu o conceito, o grão e a identidade da participação |
| `C-COLLECTION-V1-OPERATIONAL-CLOSE` | implementou a participação (migration `029`) |
| `C-COLLECTION-V1-FINAL-OPERATIONAL-CERTIFICATION` | a aresta `DERIVED -> STRUCTURED` (migration `030`) |
| `C-CLOSE-ADMISSION-TO-READY-V1` | nomeou o canário (`T4`) e o blocker real; provou que o SCRAP não o tapa |

## A fila mínima

**Vazia.** E uma fila vazia mede a fila, não o caminho.

```
MINIMUM_MISSION_DAG                       []
MINIMUM_MISSIONS_TO_COLLECTION_CORE_CLOSE UNKNOWN
```

> **ZERO BLOCKERS ≠ ZERO TRABALHO.**

A fila conta **blockers abertos**, e não há nenhum. O que falta para o core
fechar não é um buraco declarado: é uma propriedade por provar. E o número não
é zero — zero ao lado de um veredito `FAIL` lê-se como «não falta nada», e
falta.

Também não é um número maior inventado. A próxima coisa conhecida **é** uma
missão de código, e passou a sê-lo nesta medição: **dar aquisição canónica a
`T4`**. O ficheiro e o campo estão nomeados —
`pedido/receitas.py::EXECUTORES['T4'] -> retorno`, hoje `LEGADO`, e o executor
`coleta/rotulos_baixar.py`, que já colhe PDF real do Ministero.

Ela não entra na fila porque a fila conta **blockers abertos** e este gap está
registado como dívida de aquisição, não como blocker do fecho. E o número
continua `UNKNOWN` porque a missão pode descobrir ao correr o que a medição do
contrato não vê — contar agora seria feeling com cara de DAG.

⚠️ **O que já não é a próxima coisa:** escrever regra temática para `T2`. Esse
caminho foi medido contra 46 documentos reais e reprovado, e continuar a
oferecê-lo ao lado do outro mandava a próxima pessoa repetir uma missão já
feita.

`MINIMUM_MISSIONS_TO_BIG_COLLECTION_READY = UNKNOWN`, pela mesma disciplina:
depende de quantas capacidades do SCRAP a coleta grande exige, e isso ainda não
foi medido.

## O que ficou `UNKNOWN`

```
MIGRATION_APPLIED_LIVE                    UNKNOWN
COST                                      NOT_INSTRUMENTED
MINIMUM_MISSIONS_TO_BIG_COLLECTION_READY  UNKNOWN
```

`NOT_INSTRUMENTED` não é zero. Produção não é laboratório.

## A frescura deste retrato

> Um carimbo de commit num ficheiro commitado nasce sempre atrasado: ele nunca
> pode nomear o commit que o contém.

Por isso, ao lado do `MEASURED_HEAD`, o artefato guarda a impressão dos **donos
da medição** — o `sha256` do conteúdo dos ficheiros que decidem este resultado.
Se eles não mudaram, a medição continua a valer por mais commits que passem.
Quem quer saber se este retrato ainda vale compara a impressão, e não o commit.

Os dois números vivem no artefato, e **só lá** — copiados para aqui, envelhecem
a cada medição e passam a mentir:

```bash
py -c "import json;d=json.load(open('data/derivados/COLLECTION-V1-CLOSE-GATES.json'));print(d['MEASURED_HEAD']);print(d['FRESCURA']['IMPRESSAO_DOS_DONOS'])"
```

> **O JSON é o dono. O Markdown explica.**

## Onde estão os números

- `data/derivados/COLLECTION-V1-CLOSE-GATES.json` — dono dos números
- `provas/os_portoes_da_collection.py` — a medição
- `tests/test_portoes_da_collection.py` — a guarda dos dois eixos
- `docs/biblia/CONFORMIDADE-ITALIA.md` — o eixo declarado, por lei


---

## A PERGUNTA QUE ESTAVA À ESPERA DE GENTE — RESPONDIDA

Ficou escrita aqui uma missão inteira:

```
DECISION_REQUIRED
Para uma fonte DOCUMENTAL não social — uma agência pública que publica
boletins em PDF no seu próprio sítio — qual é o `canal` canónico, e o que
serve de `channel_id`?
```

**A resposta foi «nenhum», e isso não é uma evasiva.** Um boletim em PDF não tem
canal: `canal.channel_id` é «o id da plataforma, NUNCA o nome», e nenhuma
plataforma emitiu identificador nenhum para aquele PDF. A pergunta pedia o nome
de uma coisa que não existe.

Das três opções que estavam em cima da mesa, ficou a **B** — *fontes documentais
não têm canal, e `conteudo` deixa de ser a casa delas*. O que a opção B exigia
foi feito: a casa estruturada de um documento é
`public.documento_estruturado` (migration `030`), com dono único.

**Por que não a A** (uma pessoa declara e assina um `channel_id`): faria uma
pessoa escrever, todas as semanas, um identificador de plataforma para fontes
que não estão em plataforma nenhuma. Um valor assinado continua a ser um valor
inventado.

**Por que não a C** (`conteudo.canal_id` passa a aceitar ausência): afrouxaria
uma trava para lá caber uma coisa que não é conteúdo de plataforma. A coluna
ficava honesta e a tabela ficava com dois significados.

> **ONE CONCEPT → ONE OWNER ≠ ONE TABLE FOR EVERY TYPE OF CONTENT.**

---

## A SEGUNDA PERGUNTA — TAMBÉM RESPONDIDA, E POR MEDIÇÃO

Ficou escrita aqui, uma missão atrás:

```
DECISION_REQUIRED
Nenhum universo tem, ao mesmo tempo, regra temática escrita E executor de
colheita canónica. Qual dos dois lados se move?
```

Duas opções estavam em cima da mesa, e a recomendação era a **A** — escrever
regra temática para `T2`, «com uma razão medida».

⚠️ **A recomendação estava errada, e a medição que a desmente já existia.**
`provas/a_regra_de_t2.py` tinha medido exactamente isso contra 46 documentos
reais e o portão fechou na quarta condição. A recomendação anterior tratou as
duas opções como igualmente abertas porque olhou para o que **falta** a cada
lado, e não para o que já tinha sido **tentado**.

> **DUAS OPÇÕES NÃO SÃO DUAS OPÇÕES QUANDO UMA DELAS JÁ FOI MEDIDA E REPROVADA.**

A resposta é a **B**: mover o lado da aquisição, e o alvo é `T4`. Não é uma
decisão de gente — é uma missão de código, com o ficheiro e o campo nomeados.

**Por que isto não precisou de decisão humana.** A pergunta parecia de
arquitectura («qual é o significado de um universo?») e era de facto: bastava
ler quem já tinha medido. A decisão humana que restava era escolher entre dois
caminhos, e um deles estava fechado por prova.

---

## O QUE ESTÁ À ESPERA DE GENTE — e é outra coisa

Já não é o fecho da máquina. É o que fazer com `T2`:

```
T2 tem aquisição canónica, tem dono STRUCTURED, tem 5 fontes declaradas
e 10 positivos reais — e não tem como ser julgado.
```

Para T2 atravessar faltam **duas peças de arquitectura**, e nenhuma delas cabe
numa missão de fecho:

1. uma **lei** que diga o que é um documento ser *sobre* um assunto;
2. um **mecanismo** de admissão que conte sinais em vez de parar na primeira
   palavra.

As duas mudam a Admission. Nenhuma é urgente: `T4` fecha a máquina sem elas.
Fica registado para quando a pergunta voltar — e ela volta, porque `T2` é o
universo que mais material tem a entrar hoje.

## O que esta certificação NÃO pôde escrever

```
COLLECTION_V1_CORE_READY_WITHOUT_SCRAP        = NO
ONLY_REMAINING_ACQUISITION_DEPENDENCY_IS_SCRAP = NO
```

O segundo é o que importa, e é o contrário do que se esperava encontrar. O red
team tentou produzir `ONLY_REMAINING_DEPENDENCY_IS_SCRAP = YES` e **não
conseguiu** — duas vezes, e a segunda com uma cadeia muito mais forte do que a
primeira.

**A primeira tentativa** respondeu: *o SCRAP não escreve regra temática nem muda
o que a porta pergunta.* Verdade, e uma verdade lateral — argumentava pelo que o
SCRAP **não faz**.

**A segunda mediu a classe que ele serve.** O SCRAP é uma capacidade social, e a
única classe desta casa com rotas sociais é `T9`. Então o teste deixou de ser
uma impressão e passou a ser uma conta: **dá-se a `T9` a aquisição de graça e
pergunta-se o que lhe falta depois.**

```
o SCRAP serve            T9
T9 tem regra temática    SIM
dando-lhe a aquisição    ainda falta DONO_STRUCTURED
```

`T9` é conteúdo de plataforma: `public.conteudo` exige `canal_id`, e o criador
dessa identidade não existe na produção. **O SCRAP traz bytes; não traz um dono
de identidade de canal.** Integrá-lo amanhã levaria `T9` de «sem aquisição» a
«com aquisição» — e ela continuaria a parar em `STRUCTURED`, uma etapa antes de
`READY`.

> **«O SCRAP AINDA FALTA» ≠ «O SCRAP É O QUE BLOQUEIA».**
> O teste não é *«o SCRAP está integrado?»*. É *«o buraco que está lá seria
> tapado por integrar o SCRAP?»*

E a pergunta certa tem agora dono: o veredicto vem de
`provas/o_canario_da_collection.py`, e a certificação **lê-o** em vez de o
adivinhar. A versão anterior adivinhava pelo **sítio** do buraco, com uma lista
de arestas escrita à mão — respondia bem aos buracos já vistos e mal a todos os
outros.

> Uma frase de fecho só se escreve se estiver **provada**. Esta não estava.
