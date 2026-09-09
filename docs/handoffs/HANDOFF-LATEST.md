# HANDOFF — ÚLTIMO ESTADO · 2026-09-09

> O ficheiro grande é
> [`HANDOFF-EMERGENCIA-COLLECTION-FOUNDATION-2026-09-08.md`](HANDOFF-EMERGENCIA-COLLECTION-FOUNDATION-2026-09-08.md).
> **Este é só o ponteiro para onde o trabalho parou.**

```
WORK_BRANCH   claude/collection-foundation-integration-v1
WORK_HEAD     c268f3ba          (medir outra vez: git fetch)
WORKTREE      limpa
M2_STATE      CLOSED
M2I_STATE     PARTIAL
```

⚠️ **Duas sessões trabalham nesta branch.** Já colidimos sete vezes, e as sete
correram bem porque a regra foi cumprida: `git fetch` **antes de começar** e
**antes de cada commit**; se o remoto andou, **parar de escrever, ler, e
integrar por medição** — nunca por antiguidade, nunca com `--force`.

⚠️ **Não integrar `claude/system-map-freshness-v1`** enquanto essa missão não
entregar handoff próprio.

## Checkpoints

| commit | o que fechou |
|---|---|
| `8e1947d2` | **O9R** · o sensor sai do replay e entra na estrada oficial |
| `700da777` | **M2** · a rota atravessa DERIVED → STRUCTURED → ADMISSION |
| `ef9803bb` | **M2** · a aresta passa a ser percorrida, não desenhada |
| `ff26485c` | **M2R** · a travessia deixa de ser composta e passa a ser uma só |
| `c268f3ba` | **M2I** · a autoridade da identidade, medida — e não inventada |

## M2I — o veredito, e por que ele é este

```
M2I = PARTIAL
CHANNEL_IDENTITY_NOT_RESOLVED = OPEN
```

A missão pedia para resolver `SOURCE → OWNER → ORGANIZAÇÃO → ORIGEM → CANAL`,
que hoje só existe montada à mão dentro da prova. E dizia: **se não houver
autoridade canónica suficiente, termina PARTIAL.** Não há.

### O censo, antes de qualquer código

Quem **escreve** as quatro tabelas de identidade hoje:

```
organizacao   tests/ e provas/ — mais ninguém
pessoa        NINGUÉM
origem        tests/ e provas/ — mais ninguém
canal         tests/ e provas/ — mais ninguém
```

```
MODULE EXISTS ≠ OWNER EXISTS.
WRITER EXISTS ≠ IDENTITY AUTHORITY EXISTS.
```

Há dois módulos com «identidade» no nome e **nenhum é este dono**:
`regras/comunicacao_identidade.py` decide se uma conta social é oficial, de que
país e da empresa ou de uma marca — outra pergunta, outro corpus, e escreve
JSON. `coleta/sensor_canal_identidade.py` decide se um candidato de busca é
mesmo a pessoa. Nenhum liga `SOURCE_ID` a entidade.

**Não faltava schema.** A `002` já separa pessoa de organização, exige que uma
`origem` seja UMA das duas (`num_nonnulls = 1`) e põe `UNIQUE (plataforma,
channel_id)` no canal.

### A prova: `provas/a_autoridade_da_fonte.py` — 13 factos

```
o registo canónico é docs/fontes/ATLAS-DE-FONTES-EAME.md
  — e quem o diz é o scanner da casa, em sources.generated.json:
    «52 foram levantadas em Itália e nunca ganharam ficha no atlas
     — e o atlas é o registo canónico»

IT-T2-002 no atlas ................. 0 ocorrências (o atlas tem 42 fontes)
IT-T2-002 em CONTRATOS-DAS-FONTES ... não (o contrato declara OWNER para 5:
                                      FR-T4-001 ES-T4-005 IT-T4-001
                                      ES-T3-001 EU-T4-001)
a relação existe .................... só em candidatas/ITALY-SOURCE-MASTER-V1.json
                                      status=NEW · verdict=NAO SEI
e esse ficheiro diz de si próprio ... «aditivo e não altera o placar»
```

**A mutação está escrita na prova:** admitir o catálogo candidato como
autoridade viraria o veredito para `RESOLVED`. Era esse o atalho — e é por isso
que ele fica visível, e não tapado.

```
SOURCE CATALOG DECLARATION ≠ DB IDENTITY AUTHORITY.
CANDIDATE RECORD           ≠ CANONICAL FACT.
```

### O achado que poupa a próxima missão

**Promover a fonte não chega.** `organizacao.tipo` aceita **nove** nomes; o
catálogo fala **doze** `OWNER_KIND`, e **nenhum coincide** —
`OFFICIAL_REGIONAL_AGENCY`, `AOP`, `TECHNICAL_NETWORK`, `PRODUCER_ORG`,
`CONSORTIUM` não têm alvo.

A prova da M2 escreve `'orgao_publico'` para `OFFICIAL_REGIONAL_AGENCY`.
Ninguém declarou essa tradução — foi escolha de quem escreveu a prova.

```
UMA TRADUÇÃO QUE NINGUÉM DECLAROU É UMA DECISÃO QUE NINGUÉM ASSINOU.
```

Fica anotado na própria fixture, com a outra coisa que ela decide sozinha: a
URL de recurso `https://exemplo.it/<fonte>`. **`canal.url` é NULLABLE** — um
dono a sério deixaria `NULL` em vez de fabricar endereço.

### O que NÃO foi feito, de propósito

Nenhum owner runtime nasceu. Há teste que **reprova se um escritor de
identidade aparecer fora de `provas/` e `tests/`**. `exigir_canal()` continua a
recusar e a nomear quem teria de resolver — a recusa está certa e não se lhe
tocou.

```
CONTENT PERSISTENCE ≠ IDENTITY RESOLUTION.
```

## A M2 não regrediu

Sobre a base da M2R, que tornou a travessia uma execução única:

```
DERIVED · STRUCTURED · ADMISSION            observados, mesma rota, mesma corrida
DERIVED→STRUCTURED · STRUCTURED→ADMISSION   arestas com os dois topos
UNACCOUNTED_INPUT = 0 · READY = 0
M2_ROUTE_OBSERVABILITY_READY = YES · TELEMETRY_INFRASTRUCTURE_PROVED = YES
```

## O que continua aberto, com nome

| gap | estado | o que falta |
|---|---|---|
| `CHANNEL_IDENTITY_NOT_RESOLVED` | **OPEN** | as três autoridades abaixo |
| `RAW_FORWARD_NAO_EMITE` | OPEN | `guarda/preservar_coleta.py` é mudo; a aresta `RAW→DERIVED` fica declarada sem topo |
| `TELEMETRY_FAILURE_SEM_POLITICA` | OPEN | a excepção do rastro sobe pelo chamador; não há política escrita |
| `LINEAGE_PROOF_GAP` (M2R) | OPEN | `conteudo` não tem FK para `derived_artifact`: há como conferir, não há como impedir |
| `024` | DESIGNED · DB_TESTED | não aplicada em produção, de propósito |

### `MISSING_AUTHORITY`, com nome

```
1 · ficha em docs/fontes/ATLAS-DE-FONTES-EAME.md
2 · contrato em docs/operacao/CONTRATOS-DAS-FONTES-EAME.md
3 · tradução declarada de OWNER_KIND → organizacao.tipo
```

## NEXT_CHECKPOINT

**Promover `IT-T2-002`** — dar-lhe ficha no atlas **ou** contrato em
`CONTRATOS-DAS-FONTES-EAME.md`. É uma **decisão de conteúdo**, com evidência
sobre a fonte, e não trabalho de engenharia: por isso não coube nesta missão.
Depois dela, **declarar a tradução `OWNER_KIND → organizacao.tipo`**. Só então
o resolver tem sobre o que assentar — e aí é pequeno.

## Verificar em nove comandos

```bash
cd <repo> && git fetch origin && git status --porcelain
python3 system-map/scripts/validate_system_map.py
python3 provas/paridade_da_lingua.py
python3 provas/o_executor_conta_se.py
export BANCO_DESCARTAVEL_URL=postgresql://postgres@127.0.0.1:5433/descartavel
python3 provas/o_forward_conta_se.py
python3 provas/a_rota_m2_atravessa.py
python3 provas/a_autoridade_da_fonte.py
python3 -m unittest discover -s tests -q
```

Esperado: `SYSTEM_MAP_CHECK=PASS` · `PARIDADE=PASS` · `EXECUTOR_CONTA_SE=PASS` ·
`FORWARD_CONTA_SE=PASS` · `ROTA_M2_ATRAVESSA=PASS` ·
`AUTORIDADE_DA_FONTE=PASS` com `SOURCE_AUTHORITY[IT-T2-002] = UNRESOLVED`, e a
suíte em **1645 · 1433 PASS · 17 FAIL · 20 ERROR · 175 SKIP**, com as **38
falhas herdadas** medidas em `ff26485c` (`NEW_FAILURES = 0`).

⚠️ `pdftotext` (poppler-utils) tem de estar na máquina. Sem ele as provas
**recusam correr**, em vez de passarem a verde medindo a ausência da máquina.

**Zero escritas em produção. Zero Supabase. Zero Intelligence, Delivery ou
Portal. `024` por aplicar.**

> O que falta não é verdade — a ARPAV publica mesmo aquele boletim.
> O que falta é **autoridade**.
> `UNKNOWN HONESTO > IDENTIDADE INVENTADA.`
