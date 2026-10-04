# ONDE O `SOURCE_ID` SE PERDE — T3

Missão de medição. `MEASURE != FIX`: nada foi consertado, nenhum backfill,
nenhuma migration, nenhuma identidade inventada.

## A resposta

```
ONE_SINGLE_ROOT_CAUSE = NO
OUT_OF_FLOW_EVIDENCE   13
READER_GAP              7
```

Não há uma causa única. São **duas**, e consertam-se em sítios diferentes.

## Primeiro: o que «a linhagem sabe» queria mesmo dizer

O rótulo veio de uma missão anterior, e era generoso demais. O valor foi
resolvido assim:

```
provas/censo_corpus_rotulado_admission.py::fonte_de faz re.search(r'(IT-T\d+-\d+)') sobre o CAMINHO do item e dos seus pais
```

Uma expressão regular sobre o **caminho do ficheiro**. Isso é uma convencao de arrumacao, nao um campo.

> UMA CONVENÇÃO DE CAMINHO NÃO É UM CAMPO.  
> ELA NÃO VIAJA, NÃO TEM DONO, E NINGUÉM A DECLAROU.

A convenção não está *errada*: nos 7 casos em que existe também um campo
real, os dois valores batem exactamente. Ela está **ingovernada**.

## Causa 1 · `READER_GAP` — 7 casos

O valor **existe como campo**, em `data/collection-ledger/italy/observations.ndjson`,
ao lado do caminho e do SHA do bruto. Quem refaz o bruto não o lê.

```
coleta/executor_texto_de_pdf.py
    pai = art.raw_do_disco(str(pdf), str(RAIZ), COUNTRY_SCOPE="IT")
```

O bruto é reconstruído a partir do ficheiro no disco. `raw_do_disco` recusa-se,
por lei escrita, a deduzir o que quer que seja do nome do ficheiro, e **essa
recusa está certa**. O que falta é alguém passar-lhe a fonte que o recibo já tem.

Não foi apagado. Nunca foi consultado.

## Causa 2 · `OUT_OF_FLOW_EVIDENCE` — 13 casos

Estes corpos vivem em `data/samples/IT-SOURCE-SAMPLES/<SOURCE_ID>/...` e não
têm observação de coleta nenhuma. Não passaram pelo pipeline: foram colocados
como amostra. O `SOURCE_ID` existe **só** como nome de directório.

Aqui não há aresta perdida, porque nunca houve campo para atravessar.

## O caminho, estágio a estágio

| estágio | carrega `SOURCE_ID`? | prova |
|---|---|---|
| recibo da coleta | sim, campo real | `observations.ndjson` |
| bruto reconstruído | **não recebe** | `raw_do_disco(..., COUNTRY_SCOPE)` |
| derivado | sim, copia do pai | `leis/artefato.py::derivado_de` |
| ingresso | sim, traduz o nome | `coleta/ingresso.py::para_a_porta` |
| Admission | sim, lê `source_id` | `admissao/admissao.py::_tem_origem` |

Quatro dos cinco estágios estão certos. O leitor não é o defeito, a tradução
de nome não é o defeito, e a derivação não apaga nada: ela copia fielmente um
valor que já chega vazio.

## Schema não é fluxo

```
CAN_STORE            YES
WRITER_WRITES        NO
DERIVED_CARRIES      YES
STRUCTURED_CARRIES   NOT_OBSERVED
ADMISSION_READS      YES
```

O banco **pode** guardar: a migration `026` declara `raw_asset.source_id` e os
checks recusam `NAO SEI` no estado identificado. E mesmo assim 0 de 43 artefatos do registo tem SOURCE_ID provado; o registo tem {'DERIVED': 43} e ZERO RAW

> SCHEMA EXISTS != WRITER USES IT

## Histórico não é forward

```
HISTORICAL_GAP                     YES
FORWARD_CODE_HAS_SAME_GAP          YES
FORWARD_GAP_EXECUTED_AND_PROVEN    UNKNOWN
```

O código de hoje ainda tem o buraco. Que uma corrida nova o reproduza é
previsão, não medição, e esta missão não fabrica medição que não correu.

## O dono da aresta perdida

`COLLECTION_LEDGER -> RAW_RECONSTRUIDO`

coleta/executor_texto_de_pdf.py — quem refaz o bruto do disco e nao abre o recibo da coleta. `leis/artefato.py::raw_do_disco` NAO e o dono: ele recusa-se a deduzir do nome por lei escrita, e essa recusa esta certa.

## O que isto não autoriza

```
SOURCE_ID_BACKFILL     NO
WRITER_CHANGED         NO
INGRESS_CHANGED        NO
DERIVED_CHANGED        NO
ADMISSION_CHANGED      NO
MIGRATION_CREATED      NO
SOURCE_ID_INVENTED     NO
```

Os 16 do controlo negativo continuam sem fonte e **não foram tocados**.

## Onde estão os números

- `data/derivados/SOURCE-ID-WIRING-GAP-V1.json` — trilha por item, aresta a aresta
- `provas/medir_source_id_wiring_gap.py` — a medição
- `tests/test_source_id_wiring_gap.py` — 18 testes, 11 mutantes, 0 sobreviventes
