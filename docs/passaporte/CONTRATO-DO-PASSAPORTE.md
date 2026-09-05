# CONTRATO DO PASSAPORTE DA INFORMAÇÃO

**Data:** 2026-09-05 · **RULE_VERSION:** `PASSPORT-1.0` · **Decisão:** D-013

> **Objetivo:** tornar tecnicamente impossível existir informação no Sintonia sem
> identidade, origem, estado, histórico de processamento e destino conhecido.
>
> O Passaporte **não é documentação**. É parte obrigatória do pipeline, e a porta é
> fechada: informação nova sem passaporte é `REJECT_PIPELINE`, nunca `WARN_AND_CONTINUE`.

O estado do acervo antes deste contrato está em
[`BALANCO-E-RECONCILIACAO.md`](BALANCO-E-RECONCILIACAO.md). Este documento é o contrato,
e cada seção dele é exercida por código — não descrita por ele.

| entregável | onde vive |
|---|---|
| `PASSPORT_SCHEMA` | §1 · `scripts/passaporte.py :: ESTADOS` |
| `STATE_MACHINE` | §2 · `scripts/passaporte.py :: ESTAGIOS`, `_estagio()` |
| `EVENT_MODEL` | §3 · `scripts/passaporte.py :: ESCRITA`, `CAMPOS_EVENTO` |
| `CANONICAL_OWNER` | §4 · `data/passaporte/EVENTOS.jsonl` |
| `BACKFILL_PLAN` | §5 · `scripts/passaporte_backfill.py` |
| `GATES` | §6 · `scripts/passaporte_portao.py` |
| `CANARIES` | §7 · `passaporte_portao.py`, `tests/test_passaporte.py` |
| `MIGRATION_RISK` | §8 |

---

## 1 · PASSPORT_SCHEMA

### 1.1 Identidade — permanente, global, opaca

```
ITEM_ID           ITEM-<sha1(IDENTITY_BASIS)[:16]>   nasce na entrada, NUNCA muda
IDENTITY_BASIS    a chave natural GLOBAL, auditável  ex.: YOUTUBE:VIDEO:khXKfrU3iCs
PARENT_ITEM_ID    o pai, quando o item é derivado
DERIVED_FROM      a natureza da derivação            TRANSCRIPT_OF · COMMENT_ON
```

Três decisões carregadas aqui:

- **Nenhum arquivo, caminho ou URL é identidade.** Eles são `SOURCE_REFERENCE`. O ID é
  opaco de propósito: um ID legível vira caminho na cabeça de quem lê, e caminho não é
  identidade.
- **A base é GLOBAL, não por coleção.** O mesmo vídeo recolhido por duas missões é **um**
  item com duas capturas, nunca dois itens. Foi essa escolha que revelou 48 vídeos e 79
  comentários comprados duas vezes.
- **Derivado tem ID próprio e aponta para o pai.** Transcrição órfã é recusada na porta.

### 1.2 Origem e forma

```
COLLECTION_ID     a coleção que trouxe o item pela primeira vez
SOURCE_ID         a ficha da fonte no atlas
SOURCE_FAMILY     PLATFORM_PUBLIC_PAID_ROUTE · PLATFORM_PUBLIC_FREE_ROUTE ·
                  TERRITORIAL_BULLETIN · OFFICIAL_REGISTRY · FIELD_MONITORING_NETWORK ·
                  STATISTICAL_OFFICE · SCIENCE_CORPUS · MEDIA_FEED
SOURCE_REFERENCE  a URL/caminho — referência, nunca identidade
CAPTURED_AT       medido, nunca inferido
CONTENT_TYPE      VIDEO · COMMENT · POST · TRANSCRIPT · BULLETIN_DOCUMENT · ...
ITEM_CLASS        CONTENT · ORIGIN_CANDIDATE · DATASET_SNAPSHOT
```

### 1.3 Os quinze estados — vocabulário FECHADO

Valor fora do vocabulário é **recusado na selagem**. Não é normalizado, não é aceito com
aviso. A alternativa produziria, em seis meses, quatro grafias para o mesmo estado.

| campo | vocabulário | default | por que este default |
|---|---|---|---|
| `RAW_STATE` | PRESERVED · NOT_PRESERVED · ERROR · UNKNOWN | UNKNOWN | |
| `NORMALIZATION_STATE` | NORMALIZED · PENDING · ERROR · UNKNOWN | PENDING | |
| `DEDUP_STATE` | UNIQUE · DUPLICATE · PENDING · UNKNOWN | PENDING | |
| `CONTENT_STATE` | AVAILABLE · REQUESTED_EMPTY · NOT_TESTED · ABSENT · ERROR · UNKNOWN | UNKNOWN | |
| `CONTENT_READ_STATE` | READ · **LEXICALLY_SCANNED** · NOT_READ · UNKNOWN | **NOT_READ** | ler é um ato que deixa selo; a ausência do selo não é ignorância, é a informação de que não aconteceu |
| `IDENTITY_STATE` | PROVED · PLAUSIBLE · NOT_PROVED · NOT_APPLICABLE · UNKNOWN | UNKNOWN | |
| `CLAIM_STATE` | EXTRACTED · NO_USABLE_CLAIM · NOT_APPLICABLE · PENDING · UNKNOWN | PENDING | |
| `GEOGRAPHY_STATE` | PROVED · NOT_KNOWN · NOT_APPLICABLE · UNKNOWN | UNKNOWN | |
| `TIME_STATE` | PROVED · RELATIVE_ONLY · NOT_KNOWN · UNKNOWN | UNKNOWN | |
| `CROP_STATE` | DECLARED · NOT_KNOWN · NOT_APPLICABLE · UNKNOWN | UNKNOWN | |
| `ISSUE_STATE` | DECLARED · NOT_KNOWN · NOT_APPLICABLE · UNKNOWN | UNKNOWN | |
| `LINEAGE_STATE` | ROOT · RESOLVED · BROKEN · UNKNOWN | UNKNOWN | |
| `INTELLIGENCE_STATE` | PRODUCED · NOT_APPLICABLE · PENDING · UNKNOWN | PENDING | |
| `ROUTING_STATE` | ROUTED · NOT_APPLICABLE · PENDING · UNKNOWN | PENDING | |
| `CONSUMPTION_STATE` | CONSUMED · READY_NOT_CONSUMED · BLOCKED · **ORPHAN_INTELLIGENCE** · PENDING · UNKNOWN | PENDING | inteligência válida sem consumidor não pode ficar PENDING: PENDING é "ainda não se sabe", e aqui se sabe |

**`LEXICALLY_SCANNED` é o estado que este contrato existe para criar.** Ele registra que
um classificador tocou o texto — e ele **nunca** satisfaz `INTELLIGENCE_READING`. É a
tradução, em vocabulário, da lei que a casa já tinha:
*cobertura que sobe porque o classificador ficou permissivo não é cobertura.*

### 1.4 Derivados — nada aqui é digitado

```
CURRENT_STAGE          o primeiro estágio que ainda não passou
STAGE_VERDICT          PASSED · STOPPED_WITH_REASON · PENDING · ERROR
NEXT_REQUIRED_STAGE    null quando o item concluiu
BLOCKER_CODES          lista; inclui identidade e geografia, que não travam a escada
                       mas travam a inteligência
TRIAGE                 PASS · DEFER · REJECT · ERROR      ← a PRIMEIRA peneira
LIFECYCLE              ACTIVE · COMPLETED · DEFERRED · REJECTED · ERROR
REASON_CODE            obrigatório em todo item que não concluiu
NEXT_ACTION            derivado do motivo; motivo sem próxima ação é desculpa
CLAIMS · ROUTES        as afirmações do item e para onde elas foram
RECOLLECTED            quantas vezes o mesmo item voltou a entrar
CONTENT_CHARS          tamanho do conteúdo medido no selo de disponibilidade
```

### 1.5 Granularidade — declarada por família de fonte

**Um passaporte por unidade sobre a qual o pipeline toma decisão INDIVIDUAL.** Isso vale
quando *(a)* o item resolve para uma execução própria (`RUN_ID`/`COLLECTION_RUN_ID`), **ou**
*(b)* o repositório já registra uma decisão por item sobre ele (classificação, fila, veto,
estado de identidade).

Registro oficial e corpus científico não satisfazem nem (a) nem (b): entram como
`DATASET_SNAPSHOT`, **com `UNIT_COUNT` declarado** — as 3.084 linhas do ROPF e os 1.771
documentos do corpus espanhol ficam contadas dentro do passaporte, nunca escondidas atrás
dele.

**Caminho de subida declarado:** no dia em que o pipeline passar a decidir por linha — ler
cada paper, por exemplo — o snapshot é expandido em passaportes por linha. Essa expansão é
uma migração declarada, com evento próprio, nunca um silêncio.

---

## 2 · STATE_MACHINE

### 2.1 A escada

```
CAPTURE → NORMALIZATION → DEDUP → CONTENT_ACQUISITION
        → INTELLIGENCE_READING → CLAIM_EXTRACTION → ROUTING → CONSUMPTION
```

`CURRENT_STAGE` é o primeiro estágio que não passou. Um item só é contado na entrada de um
estágio se passou por **todos** os anteriores — é isso que faz a contabilidade fechar em vez
de somar o mesmo item em dois lugares.

### 2.2 Quatro veredictos, e dois deles exigem motivo

`PASSED` · `STOPPED_WITH_REASON` · `PENDING` · `ERROR`

`STOPPED_WITH_REASON` e `PENDING` **sempre** devolvem `REASON_CODE`. Um estágio que
devolvesse `STOPPED` com motivo nulo é exatamente o defeito que este contrato torna
impossível — e a contabilidade conta esse caso como `UNEXPLAINED_STAGE_DROP` e reprova o
portão.

### 2.3 A primeira peneira NÃO é relevância

```
"Este material é tecnicamente utilizável?"    →  PASS · DEFER · REJECT · ERROR
"Para quais capacidades ele é relevante?"     →  outra pergunta, plural, no roteamento
```

`DEFER` é *"não utilizável AINDA"*. Não é reprovação, não fecha o item, e a fila continua
cobrando. `REJECT` exige julgamento declarado com evidência (`DUPLICATE`,
`FALSE_POSITIVE`, `OUTSIDE_SCOPE`) — a máquina nunca rejeita sozinha por ausência.

### 2.4 Motivos e próximas ações

| REASON_CODE | NEXT_ACTION |
|---|---|
| `DUPLICATE` | nenhuma — o item canônico já existe e carrega o histórico |
| `CONTENT_NOT_AVAILABLE` | reexecutar a rota de conteúdo, ou declarar a rota fechada |
| `TRANSCRIPT_PENDING` | pedir a transcrição; nunca concluir sem pedir |
| `CONTENT_NOT_PROCESSED` | ler o conteúdo e selar `CONTENT_READ` com evidência |
| `IDENTITY_UNRESOLVED` | cruzar camadas; nunca ler o texto com mais boa vontade |
| `GEOGRAPHY_UNRESOLVED` | procurar lugar **nomeado** no conteúdo; idioma não é país |
| `NO_USABLE_CLAIM` | nenhuma — lido e sem afirmação utilizável é resultado válido |
| `FALSE_POSITIVE` | nenhuma — o termo casou e o assunto não |
| `OUTSIDE_SCOPE` | nenhuma — fora do recorte declarado da coleção |
| `WAITING_INTELLIGENCE` | extrair claim antes de rotear |
| `NOT_ROUTED` | rotear o claim para as capacidades em que ele é relevante |
| `READY_NOT_CONSUMED` | apresentar à capacidade roteada, ou declarar por que não serve |
| `NORMALIZATION_PENDING` | normalizar o bruto, ou declarar que a fonte não tem projeção |
| `CAPTURE_ERROR` | reexecutar a captura; ERROR nunca conta como reprovado |

### 2.5 Roteamento multicapacidade — não existe destino único

Dezesseis capacidades. `OPPORTUNITY` é **uma** delas, nunca o funil:

```
OPPORTUNITY · EARLY_SIGNAL · PHYTOSANITARY · WINDOWS · REGULATORY · PORTFOLIO ·
COMPETITOR · SCIENCE · HUMAN_SENSORS · MARKET_DEVELOPMENT · COMMERCIAL · MARKETING ·
SUPPLY · COUNTRY_CROP_PULSE · FUTURE_PLANNING · ASK_SINTONIA
```

Por `CLAIM_ID` × `CAPABILITY_ID`:

```
RELEVANCE   DIRECT · SUPPORTING · CONTEXT · BLOCKED · NOT_APPLICABLE
STATE       CONSUMED · READY_NOT_CONSUMED · BLOCKED
WHY         obrigatório — rota sem motivo não é rota
BLOCKER     obrigatório quando RELEVANCE = BLOCKED
```

**`OPPORTUNITY` não recebe rota automática de nenhuma área, de propósito.** O produto
declara `PRIORITY TO INVESTIGATE ← nunca SALES OPPORTUNITY`. Toda rota para `OPPORTUNITY`
nasce `BLOCKED`, com o motivo escrito, até que dado interno da ADAMA prove o contrário.

Inteligência válida sem nenhuma rota relevante fica `ORPHAN_INTELLIGENCE` — um estado com
nome, numa fila com nome. Ela não desaparece.

---

## 3 · EVENT_MODEL

Dez campos, sempre presentes. Campo não aplicável fica `null` explícito — a mesma lei de
`proveniencia.py`: **campo desconhecido é declarado, nunca ausente.**

```
EVENT_ID             EVT-<sha1(ITEM_ID|seq|tipo|timestamp|to_state)[:16]>
ITEM_ID
EVENT_TYPE
TIMESTAMP            medido, nunca "agora" implícito
ACTOR                o processo que selou
RULE_VERSION         PASSPORT-1.0
FROM_STATE
TO_STATE
REASON
EVIDENCE_REFERENCE
```

Eventos de claim e rota carregam ainda `CLAIM_ID`, `CAPABILITY_ID`, `RELEVANCE`, `BLOCKER`.

### Cada evento só escreve o campo que é dele

`ESCRITA` mapeia tipo → campo de estado. Um evento não pode escrever um campo que não é
seu — é o que impede que *"roteado"* comece a mexer em *"lido"* porque foi conveniente num
sábado.

| evento | campo que escreve |
|---|---|
| `ITEM_CAPTURED` · `CAPTURE_FAILED` | `RAW_STATE` |
| `NORMALIZED` | `NORMALIZATION_STATE` |
| `DEDUP_RESOLVED` | `DEDUP_STATE` |
| `CONTENT_AVAILABLE` · `TRANSCRIPT_AVAILABLE` · `CONTENT_UNAVAILABLE` | `CONTENT_STATE` |
| `CONTENT_SCANNED` · `CONTENT_READ` · `TRANSCRIPT_READ` | `CONTENT_READ_STATE` |
| `IDENTITY_PROVED` · `IDENTITY_NOT_PROVED` | `IDENTITY_STATE` |
| `GEOGRAPHY_PROVED` · `GEOGRAPHY_NOT_PROVED` | `GEOGRAPHY_STATE` |
| `TIME_RESOLVED` | `TIME_STATE` |
| `CROP_DECLARED` · `ISSUE_DECLARED` | `CROP_STATE` · `ISSUE_STATE` |
| `LINEAGE_RESOLVED` | `LINEAGE_STATE` |
| `CLAIMS_EXTRACTED` · `NO_USABLE_CLAIM` | `CLAIM_STATE` |
| `INTELLIGENCE_PRODUCED` | `INTELLIGENCE_STATE` |
| `ROUTED_TO_CAPABILITY` | `ROUTING_STATE` |
| `CONSUMED_BY_CAPABILITY` · `CONSUMPTION_BLOCKED` | `CONSUMPTION_STATE` |
| `STOPPED_WITH_REASON` | **nenhum** — declara por que o estado não avançou |

### Selo novo não apaga selo antigo

O log é append-only e há portão que prova isso. Os 99 candidatos a canal do piloto
carregam **dois** selos de identidade: o da coleta (`NOT_PROVED`) e o da prova derivada
(`PROVED`/`PLAUSIBLE`/`NOT_PROVED`). Os dois ficam no histórico; a projeção mostra o
último.

---

## 4 · CANONICAL_OWNER

```
data/passaporte/EVENTOS.jsonl     ← O ÚNICO artefato canônico gravado
```

O passaporte de um item é o resultado de **dobrar os eventos dele, em ordem**. Não existe
um segundo arquivo onde o mesmo estado possa envelhecer em silêncio — é a disciplina de
D-009 (*número declarado tem de ser número derivado*) aplicada a estado em vez de número.

- `scripts/passaporte.py` é o único escritor. Ninguém edita o log à mão.
- `data/passaporte/PAINEL.json` guarda **contagens**, não estado por item, e o teste
  compara o que está gravado com o que é derivado agora.
- Nenhum outro arquivo do repositório repete uma decisão de estado do Passaporte.

---

## 5 · BACKFILL_PLAN

**Somente leitura sobre o acervo.** Nenhuma coleta, nenhuma reinterpretação de conteúdo,
nenhuma execução paga. A pergunta que ele responde é **ONDE CADA COISA ESTÁ**, nunca
*o que cada coisa deveria ter virado*.

| passo | o que faz |
|---|---|
| 1 | `VOICE_ES` — vídeos, transcrições, comentários, posts, origens |
| 2 | `EARLY_SIGNAL_EAME` — vídeos, transcrições, comentários, candidatos + o segundo selo de identidade |
| 3 | `TERRITORIAL` — entradas de listagem e corpos de boletim |
| 4 | `YOUTUBE_JANELA` — grade pública + as decisões da fila do Whisper |
| 5 | origens — contas de concorrente e perfis do LinkedIn |
| 6 | `ACERVO_BASE` — 29 snapshots com `UNIT_COUNT` |
| 7 | leitura, claim, rota e consumo **derivados dos casos publicados** |

### As três proibições

1. **Não inventar que um item foi lido porque existe classificador.**
2. **Não inventar que algo foi consumido porque aparece numa pasta de inteligência.**
3. **Não promover `UNKNOWN` a estado.**

### De onde vem `READ`, e só de onde

Um item sai de `INTELLIGENCE_READING` quando um **caso publicado** em
`CASOS-PARA-APRESENTACAO.md` nomeia a fonte, publica um número derivado dela e aponta a
evidência preservada. A capacidade que consumiu sai da **área** que lista aquele caso em
`REAL_EXAMPLES` (`ARQUITETURA-DE-INFORMACAO-EAME.md`). Nada é digitado: caso e área são
lidos dos documentos.

Quando nenhuma área lista o caso, o claim fica sem rota e aparece em
`ORPHAN_INTELLIGENCE` — que é exatamente o que ele é.

### Determinismo

`BACKFILL_AT = 2026-09-05`, declarado como constante — como `ES_REFERENCE_DATE` em
`metricas_canonicas.py`. Usar *"hoje"* faria o mesmo comando produzir um log diferente
amanhã sem que nada tivesse mudado no acervo. Há teste que roda o backfill duas vezes e
compara evento a evento.

---

## 6 · GATES

`python3 scripts/passaporte_portao.py` — dez portões, todos derivados.

| portão | o que prova |
|---|---|
| `ACERVO_DECLARADO` | todo arquivo do acervo tem classificação declarada |
| `ITEMS_WITHOUT_PASSPORT` | as chaves naturais, **relidas por caminho independente**, todas têm passaporte |
| `CONTABILIDADE_FECHADA` | o total fecha no acervo e em **cada** coleção |
| `UNEXPLAINED_STAGE_DROPS` | nenhum item parou sem motivo; quem entra num estágio é quem passou no anterior |
| `TRANSCRIPT_AVAILABLE_BUT_UNTRACKED` | os 1.005.157 caracteres estão dentro de passaportes |
| `VALID_INTELLIGENCE_WITH_UNKNOWN_CONSUMPTION_STATE` | nenhuma inteligência válida com consumo desconhecido |
| `LOG_APPEND_ONLY` | o log gravado contém o backfill como **prefixo íntegro** |
| `FAIL_CLOSED` | 11 entradas inválidas exercidas, 11 recusadas |
| `CANARIO_TRANSCRICAO` | primeiro canário |
| `CANARIO_MULTICAPACIDADE` | segundo canário |

**`PASSPORT_ENFORCEMENT = ACTIVE` só quando os dez passam.** Um portão vermelho é a
resposta a *"podemos considerar esta informação entregue?"* — NÃO, com o nome do portão.

### O portão de entrada, e por que ele é fechado de verdade

`INVENTARIO` em `passaporte_backfill.py` classifica **arquivo por arquivo**. Não há
classificação por padrão, heurística de nome ou *"provavelmente é derivado"*. Arquivo novo
em `data/samples/` que ninguém declarou **derruba o portão** — e há teste que cria um
arquivo não declarado só para provar que ele derruba.

Duas pastas têm regra de diretório, com motivo declarado: `raw-paid/` (bruto de rota paga,
governado por `POLITICA-RAW-ROTA-PAGA.json`) e `data/runs/` (fragmentos de manifesto,
governados por `proveniencia.py`, que já tem portão próprio).

### As recusas exercidas

item sem identidade · item sem coleção · item sem data de captura · derivado sem pai ·
claim sem item rastreável · rota sem claim existente · consumo sem rota declarada ·
consumo sem evidência · estado fora do vocabulário · parada sem motivo declarado ·
evento sem tempo.

---

## 7 · CANARIES

### Canário 1 · os 1.005.157 caracteres

```
TRANSCRIÇÕES                     30
CARACTERES                1.005.157   (705.149 ES-T8-001 + 300.008 SENSOR-PILOT)
TRANSCRIPT_AVAILABLE            YES   30 de 30
TRANSCRIPT_READ                  NO   30 de 30
CURRENT_STAGE  INTELLIGENCE_READING   30 de 30
STAGE_VERDICT             PENDING     30 de 30
BLOCKER      CONTENT_NOT_PROCESSED    30 de 30
LIFECYCLE                    ACTIVE   30 de 30  ← nunca REJECTED, nunca invisível
```

> **Se o sistema conseguir deixar estes itens invisíveis, IMPLEMENTAÇÃO = FAIL.**

O número `1.005.157` é constante no portão. Se o acervo mudar, o portão precisa **dizer**
que mudou — não se ajustar em silêncio.

### Canário 2 · multicapacidade sem funil de oportunidade

**Sonda de contrato, e declarada como tal.** Nenhuma coleta nova foi feita nesta missão, e
o acervo não contém conteúdo de milho do Massimo Blandino — contém quatro candidatos de
LinkedIn homônimos, todos `NOT_PROVED` por cidade divergente. **Inventar o item seria
exatamente o que este contrato proíbe.**

Então o canário prova o que pode ser provado sem coletar: **que a máquina permite o
estado**. Ele roda num registro isolado, em memória, que nunca toca
`data/passaporte/EVENTOS.jsonl` — e há teste que verifica que a sonda não deixou rastro
no acervo.

```
CONTENT_READ            YES
CLAIMS_EXTRACTED        YES
SCIENCE                 DIRECT
COMPETITOR              SUPPORTING
MARKET_DEVELOPMENT      SUPPORTING
OPPORTUNITY             BLOCKED  (sem produto ADAMA registrado para o par cultura×alvo)
CONSUMED_BY             1 capacidade
ORPHAN_INTELLIGENCE     NO
```

**E o mesmo padrão já existe em dado real**, o que é a prova mais forte: os 12 snapshots
concluídos saem `REGULATORY`, `PORTFOLIO` e `COMPETITOR` em `DIRECT`/`CONSUMED` e
`OPPORTUNITY` em `BLOCKED`. O Passaporte não é um funil exclusivo de oportunidades.

---

## 8 · MIGRATION_RISK

| risco | severidade | mitigação | estado |
|---|---|---|---|
| **Backfill inventar estado que o acervo não prova** | ALTA | só estados comprováveis; três proibições no cabeçalho do backfill; `READ` só a partir de caso publicado | mitigado — 22 `READ` em 2.960 itens |
| **Varredura lexical ser confundida com leitura** | ALTA | `LEXICALLY_SCANNED` é um estado próprio e nunca satisfaz `INTELLIGENCE_READING`; o painel separa as duas linhas | mitigado, com teste |
| **Contabilidade fechar por construção e o portão virar decorativo** | MÉDIA | o portão prova três coisas independentes: a soma, o fechamento por estágio, e que a entrada de um estágio é igual aos aprovados do anterior | mitigado |
| **Identidade global colapsar itens que não são o mesmo** | MÉDIA | a base é `plataforma + id externo da fonte`, nunca título ou texto; 164 reencontros verificados um a um contra interseção de conjuntos | mitigado, com teste |
| **O log de eventos crescer sem controle** | MÉDIA | 33.886 eventos, 12,7 MB em texto, 862 KB comprimidos; é JSONL, que o Git delta-comprime bem — ao contrário de `.gz`, que entra pelo tamanho integral em toda versão | aceito e declarado |
| **Alguém editar `EVENTOS.jsonl` à mão** | MÉDIA | `LOG_APPEND_ONLY` exige que o log gravado contenha o backfill como prefixo íntegro | mitigado |
| **Snapshot esconder unidades** | MÉDIA | `UNIT_COUNT` obrigatório; caminho de subida declarado | mitigado, declarado |
| **Fontes citadas sem snapshot preservado** | BAIXA | `EU-T2-001`, `EU-T2-002`, `IT-T3-001` são impressas pelo portão a cada execução | declarado, não resolvido — resolver exige coleta |
| **`FAIL_CLOSED` quebrar coleta paga em andamento** | MÉDIA | a porta fechada vale na **admissão**, antes de gastar; a lei da casa continua sendo `DINHEIRO GASTO ≠ DADO PRESERVADO` e nenhuma regra de metadado derruba execução em curso | mitigado por desenho |
| **A migração perder o que já existia** | BAIXA | o backfill não altera nenhum arquivo do acervo; ele só escreve em `data/passaporte/` | mitigado |

---

## 9 · A PARTIR DAQUI

```
PASSPORT_REQUIRED = YES
```

- Nenhuma coleta nova é considerada entregue sem `ITEM_ID` e passaporte criado.
- Nenhum item normalizado sem referência ao `ITEM_ID`.
- Nenhuma transcrição sem `ITEM_ID` + `PARENT_ITEM_ID`.
- Nenhum claim sem origem rastreável. Nenhuma inteligência sem `CLAIM_ID`.
- Nenhuma ferramenta sem referência ao objeto de inteligência que consome.

Quem coleta chama `Registro.admitir()`. Quem lê, classifica, cruza ou consome **sela** o
que fez. O que não for selado não existe — e agora isso aparece numa fila com nome, em vez
de não aparecer em lugar nenhum.
