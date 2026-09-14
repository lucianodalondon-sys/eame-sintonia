# VEREDITO TEMÁTICO T3 — V1

Corrida cega executada uma vez. `EVALUATION_EXPOSED = YES`.
Nenhum limiar foi tocado: `GATE_THRESHOLD_CHANGED = NO`.

## O resultado

```
WINNER  = NONE
BLOCKED = C3-LLM-STRUCTURED
ADMISSION_CHANGED = NO
```

`NONE` é um resultado, não a falta de um. O portão não tem segundo lugar,
e «quase passou» não é um estado.

## Quem correu, e como foi

| mecanismo | papel | veredito | condições em falha |
|---|---|---|---|
| `BASELINE-ADMISSION-ACTUAL` | CONTROL | **FAIL** | 6 de 8 |
| `C1-LEXICAL-STRUCTURED` | CANDIDATE | **FAIL** | 6 de 8 |
| `C2-TAXONOMY-CONCEPT` | CANDIDATE | **FAIL** | 5 de 8 |
| `C3-LLM-STRUCTURED` | CANDIDATE | **BLOCKED** | — gate não aplicado |
| `C4-HYBRID-CASCADE` | CANDIDATE | **FAIL** | 6 de 8 |

`C3-LLM-STRUCTURED` **não reprovou: não foi medido.** Sem credencial de
modelo neste ambiente, a hipótese continua por testar. O portão não lhe foi
aplicado de propósito: aplicar um gate a uma corrida que não aconteceu
produz um FAIL com cara de julgamento sobre a ideia.

## O que a corrida mostrou, e que nenhum dos quatro procurava

O problema dominante não é capturar o positivo. É o negativo.

| mecanismo | negativos certos, de 20 grupos |
|---|---|
| `BASELINE-ADMISSION-ACTUAL` | 4 |
| `C1-LEXICAL-STRUCTURED` | 3 |
| `C2-TAXONOMY-CONCEPT` | 0 |
| `C4-HYBRID-CASCADE` | 0 |

Três mecanismos com inventários diferentes falham no mesmo sítio. Isso
aponta para o desenho da pergunta, não para a lista de palavras.

> TRÊS HIPÓTESES A ERRAR NO MESMO LADO  
> NÃO SÃO TRÊS ERROS: SÃO UMA PERGUNTA MAL FEITA.

A cascata mostrou o seu custo em número: 13 `ERRO`, um por cada documento
em que o primeiro andar se absteve e o segundo não existia. Abstenção a
atravessar uma cascata degradada sai do outro lado como falha.

## O achado que vale mais do que o veredito

```
plano CONTRATO   alcance  0 de 36
plano LINHAGEM   alcance 15 de 36
```

Zero documentos chegam à pergunta temática no plano que a produção vê hoje.
Trocar o mecanismo temático mudaria a resposta de **nenhum** documento.

> UM CLASSIFICADOR PERFEITO NUMA PERGUNTA QUE NINGUÉM FAZ  
> MELHORA EXACTAMENTE ZERO DOCUMENTOS.

Onde eles param, medido e não presumido:

| classe | documentos |
|---|---|
| origem · o registo confessa «NAO SEI» e a linhagem SABE | 20 |
| origem · ninguem sabe, nem o registo nem a linhagem | 16 |

Os vinte que param por «o registo confessa NÃO SEI e a linhagem sabe» são
encanamento perdido: a informação existe escrita e não chega à porta. Os
dezasseis são fonte por descobrir — outro problema, outro sítio, outro
custo. Fundir os dois num número só apagaria justamente a parte accionável.

## O que isto não autoriza

```
ADMISSION_CHANGED          = NO
GATE_THRESHOLD_CHANGED     = NO
GROUND_TRUTH_CHANGED       = NO
TRAINING_ON_EVALUATION_SET = NO
INTEGRAÇÃO                 = NOT_READY
```

Nada entra em produção por causa destes ficheiros. Um PASS aqui seria um
PASS de avaliação, e nem esse houve. `CLASSIFIER_BAD + LINEAGE_BROKEN`:
consertar só um dos dois lados não entrega documento nenhum.

## Onde estão os números

- `data/derivados/BENCHMARK-TEMATICO-V1.json` — a corrida, linha a linha
- `data/derivados/ALCANCE-PERGUNTA-TEMATICA-T3-V1.json` — o alcance
- `provas/gate_de_aceitacao_tematica.py` — os limiares, intactos
- `provas/candidatos_tematicos.py` — as fichas, congeladas antes de medir
