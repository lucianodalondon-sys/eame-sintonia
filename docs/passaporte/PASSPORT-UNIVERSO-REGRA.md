# A REGRA DE PERTENÇA DO `UNIVERSE_PASSAPORTE`

**Data:** 2026-09-06 · **Regra:** `UNIVERSO-PASSAPORTE-REGRA-2026-09-06` · **Somente leitura**
**Fonte da regra:** `docs/passaporte/CONTRATO-DO-PASSAPORTE.md §1.5`

> **Resposta curta:** a regra existe, está escrita no contrato, é semântica e reproduz a
> lista histórica **inteira** — mas ela responde *com que granularidade* um item entra,
> **não** *se aquilo é uma unidade de informação*. Essa segunda condição não está
> declarada em lugar nenhum, e eu não a inventei. `RULE_PROVED = NÃO`.

---

## 1 · A REGRA, ACHADA NO CONTRATO

`§1.5 Granularidade`, transcrita sem alteração:

> *"Um passaporte por unidade sobre a qual o pipeline toma decisão **individual**. Isso
> vale quando **(a)** o item resolve para uma execução própria (`RUN_ID`/`COLLECTION_RUN_ID`),
> ou **(b)** o repositório já registra uma decisão por item sobre ele (classificação,
> fila, veto, estado de identidade). Registro oficial e corpus científico não satisfazem
> nem (a) nem (b): entram como `DATASET_SNAPSHOT`, com `UNIT_COUNT` declarado."*

| | |
|---|---|
| **RULE** | `(a) execução própria` **ou** `(b) decisão por item`, menos `é uma execução` |
| **OWNER** | o contrato do passaporte — não a lista, não a pasta |
| **SOURCE_FILE** | `docs/passaporte/CONTRATO-DO-PASSAPORTE.md §1.5` |
| **FIELDS_USED** | (a) `RUN_ID` · `COLLECTION_RUN_ID` · `BATCH_ID` · (b) `*_STATE` · `*_BASIS` · `*_EVIDENCE` · `*_DECISION` · `FILA` · `VETO` · `CLASSIFICA` · `TRIAGE` |
| **EXCLUSÃO** | o registro **é** uma execução (`ACTOR`+`INPUT`+`COST_USD`+…) → pertence a `UNIVERSE_EXECUCOES` |
| **EXAMPLES_INCLUDED** | `SENSOR-PILOT/VIDEOS-A.json` (a) · `COMPETITOR-PUBLIC-COMM/CONTAS-V1.json` (b, `ACCOUNT_IDENTITY_STATE`) |
| **EXAMPLES_EXCLUDED** | `SENSOR-PILOT/RUNS-A.json` (é execução) · 195 arquivos sem (a) nem (b) |
| **COUNTEREXAMPLES** | `CREATOR-CONTENT-CORPUS-EAME/ACTOR-CONTRACTS-CORPUS.json` — tem `CONTRACT_STATE` por ator, satisfaz (b) ao pé da letra, e **não é evidência sobre o mundo** |
| **STABLE** | **NÃO** — ver §6 |

### Como a regra foi verificada, e o que eu me proibi de fazer

Transcrevi a frase em teste, apliquei ao acervo inteiro, e **medi o desacordo uma vez**.
**Não ajustei a regra até o desacordo virar zero** — ajustar até fechar seria decorar a
lista, não derivar a regra.

Dois bugs meus apareceram nessa verificação, e os dois eram do leitor, não da regra:

1. **A primeira versão lia só a primeira lista de topo.** Por isso classificou
   `PUBLIC-COMM-FIRST-BATCH-EAME.json` como fora — a primeira lista dele é
   `EXECUTION_ORDER` (passos) e os itens estão em `ACCOUNTS`. Corrigido: o leitor agora
   percorre listas aninhadas.
2. **O detector de contraexemplo casava pedaço de palavra.** Acusou
   `ES-T8-001-transcricoes.json` porque `TRANSCRIPTS` contém `SCRIPT`. Transcrição **é**
   unidade de informação — está entre as 21 declaradas. Corrigido com fronteira de palavra.

---

## 2 · O UNIVERSO, RECALCULADO DA REGRA

```
OLD_DECLARED_FILES        =     74      (lista histórica inteira)
   dos quais carregam item =     21      (rótulos ITENS + SELOS)
NEW_RULE_DERIVED_FILES    =    132
SCANNED_FILES_IN_SCOPE    =    132

OLD_DECLARED_RECORDS      = NÃO DECLARADO
NEW_RULE_DERIVED_RECORDS  = 14.842
SCANNED_RECORDS_IN_SCOPE  = 14.842

RULE_DERIVED_FAMILIES     =     32
RULE_DERIVED_COLLECTIONS  =     71
```

A regra **cobre as 21 inteiras** — nenhum arquivo que a lista declara como item escapa
dela — e encontra **111 a mais**. A lista histórica não vence: ela é um subconjunto do
que a regra encontra.

Por qual regra os 132 entraram:

```
REGRA_B_DECISAO_POR_ITEM   96
REGRA_A_EXECUCAO_PROPRIA   36
```

---

## 3 · TODO ARQUIVO OBSERVADO, CLASSIFICADO

```
FILES_TOTAL_SEEN  = 933
IN_SCOPE          = 132
OUT_OF_SCOPE      = 801
UNKNOWN_SCOPE     =   0
                    ───
soma                933   ✓ fecha
```

Motivos de `OUT_OF_SCOPE` — nenhum arquivo sai sem motivo:

| motivo | arquivos |
|---|---:|
| `NAO_E_JSON` (`.md`, `.csv`, `.txt`, `.html`) | 452 |
| `NEM_A_NEM_B` — não satisfaz nenhuma das duas condições | 195 |
| `SEM_REGISTROS` — não tem lista de registros nem `UNIT_COUNT` | 88 |
| `RAW_PAID_TEM_REGRA_DE_DIRETORIO_PROPRIA` | 60 |
| `E_UMA_EXECUCAO_PERTENCE_A_UNIVERSE_EXECUCOES` | 6 |

**`UNKNOWN_SCOPE = 0`** hoje. Se um arquivo ficar ilegível, ele vira `UNKNOWN_SCOPE` — e
não `OUT_OF_SCOPE`. Não saber não é estar fora, e há teste para isso.

---

## 4 · UNIVERSO NÃO É PASTA — formalizado

```
data/samples  É  um DIRETÓRIO FÍSICO.

data/samples  NÃO É  UNIVERSE_PASSAPORTE
              NÃO É  UNIVERSE_ACERVO_IT
              NÃO É  UNIVERSE_EXECUCOES
```

Estar no diretório não põe ninguém no universo: **801 dos 933 arquivos estão na pasta e
fora do universo do passaporte.** Há teste que cai se um dia todo o diretório entrar —
seria o sinal de que o universo virou a pasta outra vez.

**`UNIVERSE_DATA_SAMPLES` não foi criado**, e não deve ser. Continua sendo o que já estava
registrado: uma união sem dono.

---

## 5 · O PORTÃO

Compara **o que a regra espera** contra **o que o passaporte cobre**. Os dois lados medem
coisas diferentes de propósito — se ambos fossem a regra, o portão compararia uma conta
consigo mesma e daria `PASS` sempre.

```
                          ESPERADO       COBERTO
FILES                          132            21
RECORDS                     14.842         7.070
FAMILIES                        32             6
COLLECTIONS                     71             9
FINGERPRINT             91e10d20bb…   dce22b7910…

MISSING (satisfaz a regra e não tem passaporte)   = 111
COBERTO MAS FORA DA REGRA                          =   0
UNKNOWN CRÍTICO                                    =   1
```

```
UNIVERSE_COMPLETENESS = FAIL
MOTIVO                = MEMBERSHIP_CONDITION_NOT_DECLARED
```

**Não maquiado.** Os 111 `MISSING` são arquivos que a regra do próprio contrato diz que
pertencem ao universo e que não têm passaporte. E `COBERTO_MAS_FORA_DA_REGRA = 0`
significa que o passaporte nunca cobriu nada que a regra rejeite — a lista histórica
estava certa no que incluiu, e curta no que faltou.

---

## 6 · POR QUE `RULE_PROVED = NÃO`

Três testes, e o terceiro cai:

| teste | resultado |
|---|---|
| reproduz a lista histórica sem falso negativo | **SIM** — 21 de 21 |
| discrimina (não inclui quase tudo) | **SIM** — 132 de 933 |
| toda inclusão é unidade de informação | **NÃO** — 1 contraexemplo |

O contraexemplo:

```
CREATOR-CONTENT-CORPUS-EAME/ACTOR-CONTRACTS-CORPUS.json   lista=ACTORS, 4 registros
   campo de decisão: CONTRACT_STATE
```

Um contrato de ator do Apify tem estado por ator. Satisfaz a regra (b) **literalmente**,
e é **ferramenta, não evidência sobre o mundo**.

> **§1.5 declara GRANULARIDADE, não PERTENÇA.** Ela responde *"um passaporte por quê?"* —
> e não responde *"isto é uma unidade de informação?"*. A segunda condição não está
> escrita em lugar nenhum do contrato. Escrevê-la agora seria eu inventando o que a casa
> não decidiu.

**O que falta declarar, e é decisão humana:** o que separa uma unidade de informação
*sobre o mundo* de um registro *sobre o nosso próprio processo* (contrato de ator,
manifesto de preservação, saúde da fonte). É a mesma pergunta que apareceu na missão do
`EVIDENCE_CLASS`, onde `HUMAN_DECISION`, `PRESERVATION_MANIFEST` e `SOURCE_HEALTH` também
ficaram `NÃO SEI`. **É um conceito que falta no contrato, e ele aparece em dois lugares
independentes** — o que reforça que é real e não é detalhe.

---

## ENTREGA

```
UNIVERSE_PASSAPORTE_OWNER = docs/passaporte/CONTRATO-DO-PASSAPORTE.md §1.5
                            (o contrato, não a lista de 74 nem a pasta)
UNIVERSE_PASSAPORTE_RULE  = (a) execução própria  OU  (b) decisão por item,
                            menos "o registro É uma execução"
RULE_PROVED               = NÃO  ·  MEMBERSHIP_CONDITION_NOT_DECLARED

OLD_DECLARED_FILES        =     74   (21 carregam item)
RULE_DERIVED_FILES        =    132
SCANNED_FILES_IN_SCOPE    =    132

RULE_DERIVED_RECORDS      = 14.842
SCANNED_RECORDS_IN_SCOPE  = 14.842

FILES_TOTAL_SEEN          =    933
IN_SCOPE                  =    132
OUT_OF_SCOPE_FILES        =    801
UNKNOWN_SCOPE_FILES       =      0
                                     soma fecha ✓

EXPECTED_FINGERPRINT = 91e10d20bba1c219407cdb7caa863f4027c98319c97dbd84858693dd5d212a84
SCANNED_FINGERPRINT  = dce22b791018…  (o que o passaporte cobre hoje)

UNIVERSE_COMPLETENESS = FAIL  ·  MEMBERSHIP_CONDITION_NOT_DECLARED
   MISSING = 111   ·   COBERTO_MAS_FORA_DA_REGRA = 0   ·   UNKNOWN_CRITICO = 1

CLAIM_ID_GATE       = PASS   (não reaberto)
EVIDENCE_STATE_GATE = PASS   (não reaberto)

PASSPORT_READY = NO   ·   FULL_BACKFILL = NO
PORTAL_TOUCHED = NO   ·   DEPLOY = NO
```

### BLOCKERS_REMAINING

1. **A condição de pertença não está declarada.** É o único bloqueio que impede
   `UNIVERSE_COMPLETENESS = PASS`, e é decisão humana.
2. **111 arquivos satisfazem a regra e não têm passaporte.** Passaportá-los é backfill —
   não autorizado aqui.
3. `UNIVERSE_ACERVO_IT` (141 × 101 × 164) **não foi tocado** — é outra missão.
4. `UNIVERSE_EXECUCOES` **não foi alterado**; fica registrado como universo distinto de
   proveniência, com dono próprio (`scripts/proveniencia.py`).
5. Sem `pytest`/`pip`: a suíte antiga do repositório continua `NAO_MEDIDO`.
