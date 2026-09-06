# O DONO DO `EXPECTED_UNIVERSE` — candidatos medidos, decisão não tomada

**Data:** 2026-09-06 · **Regra:** `UNIVERSOS-2026-09-06` · **Somente leitura**
**Escopo desta missão:** apenas o bloqueio `EXPECTED_UNIVERSE_NOT_DECLARED`.
`CLAIM_ID` está fechado e não foi reaberto.

> **Resposta curta:** os donos **existem**, são três, são canônicos cada um para o seu
> universo — e **os três estão desatualizados** em relação ao acervo de hoje. Nenhum pode
> ser adotado como está. Não inventei um quarto.

---

## 1 · OS CANDIDATOS, MEDIDOS

| | `UNIVERSE_PASSAPORTE` | `UNIVERSE_ACERVO_IT` | `UNIVERSE_EXECUCOES` |
|---|---|---|---|
| **CANDIDATE_OWNER** | o backfill do passaporte | o inventário do portal italiano | a proveniência |
| **FILE** | `scripts/passaporte_backfill.py` | `data/samples/IT-PORTAL-V1/IT-ACERVO-INVENTARIO-V2.json` | `scripts/proveniencia.py` |
| **FIELD** | `INVENTARIO` + `DIRETORIOS` | `FICHEIROS` · `TOTAL_REAL_ACERVO` · `CHAVES_DE_COLECAO_ENCONTRADAS` | `RUN_ID` → `RUN_MANIFEST` |
| **registro auxiliar** | — | `IT-ACERVO-CHAVES-V1.json` (80 chaves, semeadas 2026-09-04) | `data/runs/` |
| **WHAT_IT_DECLARES** | a lista de arquivos que o passaporte reconhece, **arquivo por arquivo**, sem heurística de nome | o acervo italiano contado pela **forma** das coleções | **como** uma execução tem de ser descrita |
| **UNIVERSE_TYPE** | arquivos | coleções + registros | execuções |
| **SCOPE** | itens passaportáveis (ES + piloto + territorial + snapshots) | `COUNTRY=IT` · `LAYER=PORTAL` | qualquer coleta |
| **TEMPORAL_SCOPE** | congelado em `ce6add1` (2026-09-05) | `CAPTURED_AT = 2026-09-04` | contínuo |
| **fail-closed** | arquivo não declarado → órfão → `ACERVO_DECLARADO` cai | chave fora do registo → `UNKNOWN_COLLECTION_KEY` → reprova | campo desconhecido → `NOT_PRESERVED`, nunca ausente |
| **CANONICAL** | **SIM**, para o universo dele | **SIM**, para o universo dele | **SIM**, para o universo dele |

### O precedente que a casa já tinha

`scripts/inventario_esperado.py` faz exatamente isto para o **banco**: deriva as tabelas
esperadas das migrations em vez de manter uma lista fixa, *"para o pré-voo não ser um
número mágico"*. É a mesma disciplina, aplicada a outro universo — e é por isso que
**nenhum valor esperado foi digitado** neste contrato: todos são derivados do dono.

---

## 2 · SÃO UNIVERSOS DIFERENTES — e não podem ser somados

Um mesmo vídeo do `SENSOR-PILOT` pertence aos três ao mesmo tempo, respondendo a três
perguntas diferentes:

```
tem passaporte?              → UNIVERSE_PASSAPORTE
que forma de coleção ele tem? → UNIVERSE_ACERVO_IT
que execução o trouxe?        → UNIVERSE_EXECUCOES
```

Somá-los produziria um total que parece completo e não é total de nada.

### E existe um quarto que **ninguém declara**

```
UNIVERSE_DATA_SAMPLES_INTEIRO   —  todo arquivo sob data/samples, qualquer país e camada
                                   SEM DONO
```

**Foi esse que a primeira versão do meu portão impressionou digitalmente** — 421 arquivos,
26.061 registros, `0813535703856bdd…`. Uma digital de um universo que ninguém declarou
não prova completude; prova só que eu contei alguma coisa. O portão agora recusa
explicitamente tratar essa união como universo.

---

## 3 · O CONTRATO — cinco dimensões, e faltar uma já reprova

```
EXPECTED_FILE_COUNT      ↔  SCANNED_FILE_COUNT
EXPECTED_RECORD_COUNT    ↔  SCANNED_RECORD_COUNT
EXPECTED_FAMILIES        ↔  SCANNED_FAMILIES
EXPECTED_COLLECTIONS     ↔  SCANNED_COLLECTIONS
EXPECTED_FINGERPRINT     ↔  SCANNED_FINGERPRINT
```

`PASS` exige as **cinco** declaradas **e** batendo. Qualquer uma ausente →
`EXPECTED_DIMENSIONS_MISSING` → `FAIL`.

`python3 scripts/passaporte_universos.py --acervo . --passaporte <ref>`

---

## 4 · O QUE A MEDIÇÃO DEU

### `UNIVERSE_PASSAPORTE` = **FAIL** · `EXPECTED_DIMENSIONS_MISSING`

```
EXPECTED_FILE_COUNT      =  74
SCANNED_FILE_COUNT       = 873
MISSING                  =   0    ← nenhum arquivo declarado sumiu
EXTRA                    = 799    ← arquivos no disco que o dono não declara

DIMENSÕES NÃO DECLARADAS = EXPECTED_RECORD_COUNT · EXPECTED_FAMILIES
                           EXPECTED_COLLECTIONS · EXPECTED_FINGERPRINT
```

O dono declara **arquivos, e só**. Dizer que ele declara registros ou digital seria
inventar. E os 799 extras não são defeito dele: o `INVENTARIO` foi escrito para o
universo do passaporte, e o acervo canônico cresceu muito além dele.

### `UNIVERSE_ACERVO_IT` = **FAIL** · `EXPECTED_DIMENSIONS_MISSING`

E aqui está o achado mais duro desta missão: **três contagens do mesmo universo, todas
diferentes.**

| medição | ficheiros | registros | chaves desconhecidas |
|---|---:|---:|---:|
| **declarado** pelo dono, 2026-09-04 | 141 | 9.438 | **0** |
| o **próprio script do dono**, rodado hoje | 101 | 8.770 | **35** |
| **minha varredura independente**, hoje | 164 | 29.694 | **82** |

O dono e eu implementamos a mesma regra — *"coleção é qualquer chave de topo cujo valor
seja lista não vazia de dicionários"* — e chegamos a números diferentes. **Duas
implementações que discordam é informação, não ruído:** enquanto elas discordarem, não
existe número de universo que possa ser declarado com honestidade.

> **Registro de um erro meu, e do que ele custou.** Para medir se o dono ainda batia, eu
> **executei** `it_acervo_inventario_v2.py` — e ele **regrava** o artefato do dono.
> Modifiquei um arquivo do acervo numa missão declarada somente-leitura. Detectei por
> `git status`, capturei o número antes, e restaurei com `git checkout --`. O acervo está
> intacto (`git status data/` = 0). O portão desta missão reimplementa a contagem
> **sem executar o script do dono**, e há teste que cai se ele ganhar uma escrita.

### `UNIVERSE_EXECUCOES` = **FAIL** · `OWNER_DECLARES_SHAPE_NOT_EXTENT`

```
SCANNED_FILE_COUNT = 22
SCANNED_RUN_COUNT  = 22
```

`proveniencia.py` declara **como** uma execução tem de ser descrita — ator, entrada,
dataset, bruto, dono, tempo medido. Não declara **quantas** deveriam existir.
**Forma declarada não é extensão declarada**, e é por isso que este universo não pode
receber `PASS` — não por defeito do dono, mas porque ele responde outra pergunta.

---

## 5 · O QUE PRECISA DE DECISÃO HUMANA

Nenhuma destas é minha para tomar, e nenhuma se resolve inventando número.

1. **Qual universo o portão do passaporte deve cobrar?** O `INVENTARIO` (74 arquivos) é
   coerente com o passaporte e incoerente com o acervo canônico (873). Ampliá-lo é
   decisão de escopo, não de código.
2. **Quem reconcilia as três contagens do acervo italiano?** Enquanto 141, 101 e 164
   coexistirem, `EXPECTED_FILE_COUNT` não tem valor honesto.
3. **`UNIVERSE_EXECUCOES` deve ter extensão declarada?** Se sim, quem declara quantas
   execuções deveriam existir.
4. **A união `data/samples` deve virar um universo com dono, ou continuar sem?** Se
   continuar sem, o portão está certo em recusá-la — e isso precisa ficar escrito.

---

## ENTREGA

```
EXPECTED_UNIVERSE_OWNER    = TRÊS, um por universo, todos canônicos no próprio escopo
                             · scripts/passaporte_backfill.py            (arquivos)
                             · data/samples/IT-PORTAL-V1/IT-ACERVO-INVENTARIO-V2.json
                                                                          (coleções)
                             · scripts/proveniencia.py                   (execuções)
EXPECTED_UNIVERSE_FILE     = ver acima, por universo
EXPECTED_UNIVERSE_DECLARED = NÃO — nenhum declara as cinco dimensões, e os três
                             estão desatualizados em relação ao acervo de hoje

                                    ESPERADO        VARRIDO
UNIVERSE_PASSAPORTE  FILES              74             873
                     RECORDS      não declarado      9.287
                     FAMILIES     não declarado         —
                     COLLECTIONS  não declarado         —
                     FINGERPRINT  não declarado    (calculável)

UNIVERSE_ACERVO_IT   FILES             141             164
                     RECORDS         9.438          29.694
                     FAMILIES           12              12
                     COLLECTIONS        80              93
                     FINGERPRINT  não declarado    (calculável)

UNIVERSE_EXECUCOES   tudo         não declarado    22 execuções

UNIVERSE_COMPLETENESS = FAIL
MISSING               = 0 no passaporte · não computável nos outros
EXTRA                 = 799 no passaporte · 82 chaves não declaradas no acervo IT
OUT_OF_SCOPE          = UNIVERSE_DATA_SAMPLES_INTEIRO — declarado sem dono, de propósito

CLAIM_ID_GATE         = PASS   (estado ativo, inalterado por esta missão)
EVIDENCE_STATE_GATE   = PASS   (inalterado)

PASSPORT_READY = NO   ·   FULL_BACKFILL = NO
PORTAL_TOUCHED = NO   ·   DEPLOY = NO
```

### BLOCKERS_REMAINING

1. **Nenhum dono declara as cinco dimensões.** Nenhum declara impressão digital.
2. **Três contagens do acervo italiano discordam** (141 · 101 · 164).
3. **799 arquivos fora do `INVENTARIO`** do passaporte — decisão de escopo.
4. **A união `data/samples` continua sem dono**, e o portão a recusa de propósito.
5. Os quatro itens da §5 aguardam decisão humana.
6. Sem `pytest`/`pip`: a suíte antiga do repositório continua `NAO_MEDIDO`.
