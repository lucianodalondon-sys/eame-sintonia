# OS PORTÕES DA COLLECTION V1

`MEASURE != FIX` na medição. Os fechos abaixo vieram de missões próprias,
cada uma com a sua prova.

## O veredito

```
COLLECTION_CORE_CLOSE = PASS
BIG_COLLECTION_READY  = FAIL

BLOCKERS            = 0
NON_BLOCKING_DEBT   = 6
ROOT_CAUSES         = 4
MISSÕES ATÉ FECHAR  = 0
```

**A Collection V1 fechou.** Um pedido `T4` real atravessou as onze etapas na
mesma corrida, do botão até à Sala de Espera, com o executor a ir à fonte
oficial e a porta a dizer `SIM` por uma regra que já existia.

```
COLLECTION_V1_CORE_READY_WITHOUT_SCRAP         = YES
ONLY_REMAINING_ACQUISITION_DEPENDENCY_IS_SCRAP = NO
```

⚠️ **As duas frases não dizem a mesma coisa, e a segunda é a que trava.** A
máquina está fechada: a estrada existe e foi atravessada de ponta a ponta. Mas
**nove das onze classes continuam sem aquisição canónica**, e só uma delas
(`T9`) é do domínio do SCRAP. As outras oito esperam por executores que o SCRAP
não escreve.

> **A MÁQUINA ESTAR FECHADA NÃO DIZ NADA SOBRE QUANTAS CLASSES AINDA NÃO A
> ATRAVESSAM.**

Isto esteve a um passo de sair falso, e pelo atalho mais inocente que há: a
certificação calculava a segunda frase como *«o core fechou **ou** o SCRAP
taparia o buraco»*. Com o core fechado, ela dizia «só falta o SCRAP» sem nunca
ter perguntado quem mais falta.

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
| `READY` | YES | YES | YES | **SIM** |
| `WAITING_ROOM` | YES | YES | YES | **SIM** |

> MÓDULO EXISTE ≠ ARESTA EXISTE ≠ FLUXO EXECUTADO.

**As onze atravessam, e agora na mesma história.** O que fechou a coluna da
direita foi um pedido `T4`:

```
RUN         IT-T4-…        collection_run · concluida
RAW         id=1           source_id=EU-T4-001
                           document_key=32026R1696 · basis=SOURCE_DOCUMENT_ID
STORAGE     1 objeto ligado à observação
DERIVED     1 · TEXT_EXTRACTION · participação material escrita
STRUCTURED  1 · documento_estruturado, sem canal inventado
ADMISSION   {'SIM': 1}     pela regra de T4 que já existia
READY       1 unidade
SALA        IT-T4-….json
```

⚠️ **A coluna «pelo pedido» lê DUAS medições, e não uma.** Cada classe tem a
sua: `T4` atravessa, `T2` para na porta. A pergunta do censo é *«esta etapa
atravessa por algum pedido?»*, e não *«atravessa pelo pedido T2?»* — enquanto
só havia uma classe medida, as duas perguntas tinham a mesma resposta.

> **UMA CLASSE NÃO ATRAVESSA ≠ A ESTRADA NÃO ATRAVESSA.**

`T2` continua a parar em `ADMISSION`, e isso continua **certo**: ela não tem
regra temática escrita, e a porta não inventa uma. Isso é cobertura por fechar,
não estrada por construir.

Sem ambiente descartável a medição **não corre**, e isso diz-se: `SKIP != PASS`
e `NOT_MEASURED != PASS`.

## Os blockers

**Nenhum — e agora isso quer dizer alguma coisa.**

```
COLLECTION_CORE_CLOSE     = PASS
BLOQUEADO_POR             = []
CANONICAL_E2E             = PROVEN
CANONICAL_E2E_SAME_STORY  = PASS
```

Durante quatro missões esta secção dizia **`ZERO BLOCKERS ≠ CORE FECHADO`** — e
estava certa: a fila estava vazia e o veredito era `FAIL`, porque o que faltava
não era um buraco declarado, era uma propriedade por provar.

A propriedade ficou provada. O veredito mudou porque a medição mudou, e não
porque a régua desceu.

## Onde a estrada se partia, e eram três achados

Um pedido `T4` real atravessa hoje as **onze** etapas numa história só, com o
executor a ir à fonte oficial.

```
LAST_PROVEN_STAGE   = WAITING_ROOM
FIRST_LOST_EDGE     = (nenhum)
```

O que se segue é a história de como os três buracos fecharam, pela ordem em que
apareceram. Fica escrita porque **um buraco que some não deixa ver que existiu,
nem por que deixou de existir** — e os três fecharam de maneiras diferentes,
que é a parte transferível.

Os três achados são de **espécies diferentes**, e não se misturaram — um
resolvia-se com código, o segundo com uma separação, o terceiro parecia não se
resolver com nenhum dos dois. **Os três fecharam**, e o terceiro fechou pelo
lado que a medição anterior tinha recomendado errado.

| aresta | tipo | quem resolve | estado |
|---|---|---|---|
| `STORAGE -> DERIVED` | `WIRING_GAP` | código | **FECHADO** |
| `DERIVED -> STRUCTURED` | `CONTRACT_OWNER_GAP` | gente | **FECHADO** |
| `ADMISSION -> READY` | `EMPTY_INTERSECTION` | código | **FECHADO** |

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

**`ADMISSION -> READY` — EMPTY_INTERSECTION, fechado por aquisição.**

Este era o mais raro dos três: **tudo o que ele precisava existia, e ainda
assim nada passava.** A porta existia, julgava e respondia. As regras temáticas
existiam. Os executores existiam.

```
universos com regra de admissão escrita         T3 · T4 · T7 · T9
universos cujo executor declarava colheita      T2
interseção                                      VAZIA
```

> **FALTA DE PEÇA ≠ PEÇAS QUE NÃO SE CRUZAM.**

**Como fechou:** `T4` passou a ter aquisição canónica, e por isso entrou na
segunda lista sem sair da primeira. A interseção deixou de ser vazia por
**movimento**, e não por alguém ter reescrito uma das listas.

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

### O canário, e o blocker que fechou

```
CANONICAL_CANARY_CLASS = T4 (Regulatório)   — e agora ele ATRAVESSA
```

T4 é a única classe a uma peça de distância cuja peça em falta **não foi medida
e reprovada**. Ela já tem regra temática escrita e já tem dono `STRUCTURED`
documental — a mesma casa que T2 usa, porque a espécie é a mesma: PDF oficial.

**O blocker que estava nomeado:**

```
o executor de T4 não declarava COLHEITA
onde        pedido/receitas.py::EXECUTORES['T4'] -> retorno
declarava   LEGADO (MANIFEST) — suporte, e suporte nunca atravessa
faltava     um ENVELOPE por corrida
```

**Como fechou, e a parte que quase o impediu.** A medição anterior deixou ao
lado um bloqueio de ambiente:

```
www.fitosanitari.salute.gov.it — unable to get local issuer certificate
```

Verdade, medida com cuidado, e **enganosa** — porque diz «a fonte de T4» quando
o que foi medido é *a fonte que o executor da receita usa*. O atlas tem **oito**
fontes T4 aprovadas, e ninguém lhes tinha perguntado:

| fonte | resposta |
|---|---|
| `EU-T4-001` · Publications Office da UE | **200** · `GREEN` · `sabe_coletar: true` |
| `IT-T4-001` · dati.salute.gov.it | **200** · CSV 4,6 MB |
| França · data.gouv.fr | 404 (a rota mudou) |
| `fitosanitari.salute.gov.it` | TLS não verifica |

> **A FONTE QUE O EXECUTOR USA NÃO É «A FONTE DA CLASSE».**
> Uma classe tem um atlas; um executor tem um endereço.

**E a rota certa já estava escrita no contrato da fonte.** O colector de
`EU-T4-001` devolve XHTML, e o derivador desta casa extrai texto de PDF — medido:
um ficheiro que não começa por `%PDF` sai com `EXTRACTION_ERROR`. O caminho fácil
era escrever um derivador para XHTML. Não foi preciso: o contrato da fonte já
declarava, no campo `fallback`, *«EUR-Lex por CELEX (mesma casa, outra rota)»* —
e o EUR-Lex serve o mesmo ato em PDF oficial.

> **ANTES DE CONSTRUIR A PEÇA QUE FALTA, LER O CONTRATO DA FONTE ATÉ AO FIM.**

O executor novo é `coleta/eu_regulatorio_executor.py`. Não cunha corrida, não
julga, não escreve em tabela nenhuma: larga bytes e **declara**. E o
`rotulos-oficiais` **fica** na receita, atrás — ele indexa 163 rótulos e esse
índice tem valor; sai da frente porque não colhe, não porque não sirva.

⚠️ **E não foi o SCRAP.** O SCRAP é uma capacidade social e não colhe documento
de ministério.

### O primeiro `DOCUMENT_ID` provado desta casa

Durante missões seguidas, `DOCUMENT_ID` foi sempre `NULL` — e sempre com razão.
`EU-T4-001` declara no contrato dela:

```
identity_keys: CELEX
```

O CELEX **é** o nome que o emissor dá ao ato. Medido, ele atravessa até
`raw_asset`:

```
document_key        32026R1696
document_key_basis  SOURCE_DOCUMENT_ID
identity_state      FORWARD_IDENTIFIED
```

> **SHA É DOS BYTES. CAMINHO É MORADA. URL É ENDPOINT.**
> **CELEX É O NOME QUE O MUNDO DEU AO DOCUMENTO.**

E apanhou-se ao lado uma frase que tinha ficado verdadeira e deixou de ser. O
orquestrador dizia, em comentário: *«`document_id` NÃO VAI. A fonte documental
não o prova.»* Era verdade da **única** fonte que por ali tinha passado.

> **UMA FRASE VERDADEIRA SOBRE A ÚNICA FONTE QUE JÁ PASSOU
> NÃO É UMA FRASE VERDADEIRA SOBRE A ESTRADA.**

A frase foi corrigida e o transporte **não** foi alargado: levar o CELEX até
`documento_estruturado` atravessa quatro donos, e isso é trabalho deliberado. A
identidade não se perde — vive na casa dela. O `NULL` no registo estruturado
passou a significar *«esta casa ainda não o transporta»*, que não é a mesma
ausência que *«a fonte não o provou»*.

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
corrida** — são duas perguntas, e a segunda mede-se na estrada, acima. Na
corrida `T4` que fechou a Collection falaram todas as que a estrada atravessa.

## A dívida que não bloqueia

| id | porque não bloqueia |
|---|---|
| `G-STRUCT-01` | STRUCTURED atravessa numa classe e não nas duas: a DOCUMENTAL passa pelo pedido; a PLATAFORMA espera por um dono de identidade de canal, que é da frente social. É dívida de COBERTURA, não de ausência de travessia. |
| `G-ADM-01` | o ledger prova ADMISSION observada na rota forward, com caminho bom e caminho de falha. A infraestrutura ATRAVESSA; o que falta e a cobertura do tipo `derived_artifact`. |
| `G-TEL-01` | nao impede executar nem preservar. Impede LER o que aconteceu, e isso e divida de observabilidade, nao de fecho. |
| `G-TEMA-01` | NAO bloqueia a coleta grande. A funcao da coleta grande e ADQUIRIR e PRESERVAR; admitir bem e a etapa seguinte, e a Admission ja produz decisao auditavel com NAO_SEI de p |
| `G-ENV-01` | o envelope vive num caminho por executor e não por corrida: duas corridas do mesmo executor escrevem no mesmo ficheiro. Em série não morde, e a coleta de hoje é em série. Morde quando duas corridas se cruzarem — e isso é a coleta grande, não o fecho. |
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
| `C-T4-CANONICAL-ACQUISITION-TO-WAITING-ROOM-V1` | deu aquisição canónica a `T4` e **fechou a Collection V1** |

## A fila mínima

**Vazia — e desta vez a fila vazia e o veredito concordam.**

```
MINIMUM_MISSION_DAG                       []
MINIMUM_MISSIONS_TO_COLLECTION_CORE_CLOSE 0
COLLECTION_CORE_CLOSE                     PASS
```

Durante quatro missões esta secção teve de explicar por que uma fila vazia
convivia com um veredito `FAIL`:

> **ZERO BLOCKERS ≠ CORE FECHADO.**
> **UMA FILA VAZIA MEDE A FILA, E NÃO O CAMINHO.**

As duas frases continuam verdadeiras e continuam a valer para a próxima vez. O
que mudou é que o caminho acabou.

**O que vem a seguir não é do fecho da máquina**, e por isso não entra nesta
fila: são nove classes sem aquisição canónica, cada uma com o seu executor por
escrever. `T9` espera pelo SCRAP; as outras oito esperam por trabalho que ainda
não tem dono. Contar isso como «missões até fechar o core» seria contar duas
coisas diferentes no mesmo número.

## O que ficou `UNKNOWN`

```
MIGRATION_APPLIED_LIVE                    UNKNOWN
COST                                      NOT_INSTRUMENTED
MINIMUM_MISSIONS_TO_BIG_COLLECTION_READY  UNKNOWN
```

`NOT_INSTRUMENTED` não é zero. Produção não é laboratório.

⚠️ **E o core ter fechado não promove nada disto.** A estrada foi provada
contra PostgreSQL descartável, com a cadeia de migrations que está em git. Que
LIVE tenha a mesma cadeia continua por medir, e medir contra descartável nunca
promoveu nada a LIVE.

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

## O que a certificação pôde e não pôde escrever

```
COLLECTION_V1_CORE_READY_WITHOUT_SCRAP         = YES
ONLY_REMAINING_ACQUISITION_DEPENDENCY_IS_SCRAP = NO
```

A primeira **pôde** escrever-se, e só se escreveu porque um pedido `T4` real
atravessou as onze etapas na mesma corrida. A segunda continua a não poder — e
pela terceira vez seguida, por um motivo diferente do da vez anterior.

**A primeira tentativa** respondeu: *o SCRAP não escreve regra temática nem muda
o que a porta pergunta.* Verdade, e uma verdade lateral — argumentava pelo que o
SCRAP **não faz**.

**A segunda mediu a classe que ele serve.** O SCRAP é uma capacidade social, e a
única classe desta casa com rotas sociais é `T9`. O teste passou a ser uma
conta: **dá-se a `T9` a aquisição de graça e pergunta-se o que lhe falta
depois.**

```
o SCRAP serve            T9
T9 tem regra temática    SIM
dando-lhe a aquisição    ainda falta DONO_STRUCTURED
```

**A terceira apareceu quando o core fechou**, e era a mais perigosa das três
porque estava no código e não no raciocínio. A certificação calculava:

```
ONLY_REMAINING = "YES" se (core fechou) OU (o SCRAP taparia o buraco)
```

Com o core a fechar, o primeiro ramo ficou verdadeiro e a frase passou a dizer
«só falta o SCRAP» **sem nunca ter perguntado quem mais falta**. Medido:

| classes sem aquisição canónica | 9 |
|---|---|
| dessas, do domínio do SCRAP | `T9` |
| dessas, que o SCRAP não serve | `T1` `T3` `T5` `T7` `T10` `T11` `T12` `T13` |

> **A MÁQUINA ESTAR FECHADA NÃO DIZ NADA SOBRE QUANTAS CLASSES AINDA NÃO A
> ATRAVESSAM.**
> Uma classe provou a estrada. Isso diz que **quando** as outras tiverem
> aquisição, a estrada está lá — não que já a atravessem.

A frase passou a contar as classes e só diz `YES` se **todas** as que faltam
forem do SCRAP. E um teste prova os dois sentidos, com o core fechado nos dois.

> Uma frase de fecho é uma **autorização**. Não se arredonda, e não se deixa
> cair de um `or`.

---

## O QUE FICA MEDIDO E NÃO CONSERTADO

**`G-ENV-01` · o envelope vive num caminho por executor, e não por corrida.**

`retorno.ENVELOPE` é uma constante da receita: duas corridas do mesmo executor
escrevem no mesmo ficheiro. Medido nesta missão — perguntou-se pela colheita de
uma corrida que não existe, e o orquestrador devolveu a colheita da última que
escreveu, **sem nota e sem recusa**.

```
ENVELOPE_PARTILHADO = NAO_DETECTA
```

Não é defeito desta missão: o adapter italiano tem a propriedade exactamente
igual. **Em série não morde** — cada corrida escreve, o orquestrador lê a
seguir — e a coleta de hoje é em série. Morde quando duas corridas do mesmo
executor se cruzarem no tempo, que é o que a coleta grande vai fazer.

Fica como dívida com nome, e não como promessa de que está certo: corrigi-la é
mudar a convenção de **todos** os executores, e isso é trabalho deliberado, não
efeito secundário de uma missão de aquisição.

⚠️ **E não virou um `caso()` com veredito.** Um caso que afirmasse o
comportamento de hoje passaria a abençoá-lo: no dia em que alguém o
consertasse, a prova reprovava a correcção.

> **UMA GUARDA QUE FIXA O DEFEITO DE HOJE DEFENDE O DEFEITO.**
