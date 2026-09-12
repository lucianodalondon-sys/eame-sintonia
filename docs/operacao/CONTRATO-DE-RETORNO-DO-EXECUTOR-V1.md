# O CONTRATO DE RETORNO DO EXECUTOR — V1

> **A lei está em `COL-LAW-505`. O contrato executável está em
> [`leis/retorno_da_coleta.py`](../../leis/retorno_da_coleta.py). Este ficheiro é a
> MEDIÇÃO que os produziu.**
>
> Nada aqui é opinião de arquitectura. Cada linha tem um ficheiro desta árvore
> por trás, e a escolha do desenho é consequência do que foi medido.

---

## 1 · O CENSO DOS RETORNOS (FASE 1)

Cinco executores canónicos em `pedido/receitas.py`, quinze caminhos declarados
em `larga_em`. Classificados pela **estrutura e significado**, nunca pelo nome
do ficheiro.

| executor | alvo | `larga_em` | espécie real | payload |
|---|---|---|---|---|
| `corpus-pesquisador` | T7 | `RESEARCHER-CORPUS-EAME-V1.json` | CATALOG | não |
| `rotulos-oficiais` | T4 | `data/raw/IT-ROTULOS/_MANIFESTO.json` | MANIFEST | **não** (0 PDFs) |
| `comunicacao-publica` | T9 | `COMPETITOR-PUBLIC-COMM/` (6 ficheiros) | CATALOG · RUN_RECEIPT · PLAN | não |
| `eppo` | T3 | `data/samples/IT-PRAGAS` | — | caminho não existe |
| `italia-recorrente` | T2 | `data/colheita/italia/` | — | caminho não existe |

```
HARVEST ENCONTRADO EM larga_em = 0 de 15
```

**Correcção a uma leitura anterior.** O `larga_em` do T2 **não** está podre: ele
confere exactamente com `coleta/italy_executor.py` (`BALCAO` / `COLHEITA`). A
pasta não existe porque o executor **nunca correu** — precisa de rede.

---

## 2 · A FALSA COLHEITA, REPRODUZIDA (FASE 2)

```
ITEMS_EMITTED        253
REAL_HARVEST_ITEMS     0
FALSE_HARVEST_TOTAL  253

CURRENT_GENERIC_HEURISTIC_SAFE = NO
```

| executor | itens emitidos | o que eram na verdade |
|---|---|---|
| `rotulos-oficiais` | 163 | linhas de um manifesto de descarga |
| `comunicacao-publica` | 78 | 74 fichas de conta + 4 passos de um plano |
| `corpus-pesquisador` | 12 | fichas de pessoa |

### O contraexemplo que fecha o assunto

`CLASSIFICADO-V1.json` **declara um contentor de colheita** chamado `ITEMS`,
com `ITEM_COUNT = 0`. A heurística genérica de `a_colheita()` — «uma lista, ou o
primeiro campo do ficheiro que seja lista de fichas» — **salta-o por estar
vazio** e agarra a lista de catálogo ao lado.

```
UMA HEURISTICA QUE PREFERE UMA LISTA CHEIA A UMA LISTA CERTA
NAO ESTA A LER O RETORNO: ESTA A ADIVINHAR.
```

O executor tinha declarado. Ninguém leu a declaração.

---

## 3 · AS ESPÉCIES (FASE 3)

Cada uma foi **encontrada** nesta árvore. Nenhuma foi inventada.

| espécie | o que é | ficheiro real |
|---|---|---|
| `COLHEITA` | unidade observada na fonte | `data/collection-store/italy/IT-T3-005/…/monitoraggio.html` |
| `MANIFEST` | listagem de payloads | `data/raw/IT-ROTULOS/_MANIFESTO.json` |
| `CATALOG` | inventário de entidades / de onde se PODE coletar | `RESEARCHER-CORPUS` · `CONTAS-V1` · `ANCORAS` |
| `RUN_RECEIPT` | prova da execução | `MEDICAO-PRIMEIRO-LOTE-V1.json` |
| `PLAN` | o que se tenciona fazer | `PUBLIC-COMM-FIRST-BATCH :: EXECUTION_ORDER` |
| `UNKNOWN` | declarado e não classificável | — nunca entra |

**`INDEX` não é espécie própria.** Procurou-se a diferença entre índice e
manifesto e ela não existe: as duas são uma listagem de payloads. O que varia é
onde o payload está e se está — e isso já tem campo, com estado próprio.

**`SUPPORTING_ARTIFACT` não é a sexta espécie**: é tudo o que não é colheita.
Deriva-se. Assim não há saco misto onde esconder o que não se soube classificar.

### `PAYLOAD` tem três estados, e o terceiro custou a medição inteira

```
PRESENTE       ha bytes nesta arvore, no caminho declarado
AUSENTE        o caminho foi declarado e os bytes nao estao ca
NAO_SE_APLICA  a observacao E o proprio item
```

`AUSENTE` **não é erro.** O `_MANIFESTO.json` declara 163 ficheiros e há zero ao
lado. Chamar-lhe erro faria a corrida falhar; calar faria o índice passar por
colheita. É um terceiro estado, e precisa de nome.

---

## 4 · O DONO (FASE 4)

| candidato | de que pergunta já é dono | porque não serve |
|---|---|---|
| `pedido/receitas.py` | «que executor atende este pedido, e onde ele larga» | declara **intenção**, e `COL-LAW-015` proíbe-o como estação de topo. `DECLARED != OBSERVED` |
| `leis/artefato.py` | «que ficha uma coisa entregue preenche» | descreve **uma coisa já entregue**; o campo seria preenchido pelo ingresso, logo continuaria adivinhado |
| `coleta/ingresso.py` | «posso preservar esta observação como RAW?» | decidir espécie aqui é decidir **por cheiro, depois do facto** — o defeito que a lei veio fechar |

```
RETURN_CONTRACT_OWNER = leis/retorno_da_coleta.py
```

Irmão de `leis/artefato.py`, e não substituto dele:

```
receitas.py         declara a INTENCAO   (que executor, que rota, onde larga)
retorno_da_coleta   declara o RESULTADO  (o que a corrida devolveu, e o que e o que)
leis/artefato.py    governa a FICHA      de cada coisa entregue
coleta/ingresso.py  pergunta             «posso preservar esta observacao?»
```

> **Aviso de segunda autoridade.** `regras/italy_contracts.mjs` é dono da espécie
> do **destino estruturado**. Espécie do **retorno** e espécie do **destino** são
> perguntas diferentes, e esta lei não toca na outra.

---

## 5 · OS TRÊS DESENHOS (FASE 5)

| critério | A · declaração no registry | B · adapter por executor | **C · envelope de execução** |
|---|---|---|---|
| ONE_OWNER | sim | **não** — a lei em 5 sítios | sim |
| DETERMINISM | sim | sim | sim |
| TESTABILITY | média | baixa | **alta** — função pura |
| IDENTITY_SAFETY | não trata | por adapter | **sim** — recusa `DOCUMENT_ID` fabricado |
| RUN_CORRELATION | **não** | parcial | **nativa** |
| LEGACY_COMPATIBILITY | alta | alta | alta |
| MIGRATION_COST | 5 campos | 5 adapters | 3 famílias |
| EXTENSIBILITY | baixa | baixa | **alta** |
| NO_GENERIC_HEURISTICS | sim | sim | sim |

```
CHOSEN_DESIGN = C
```

**Porquê, e o argumento é medido.** O desenho A **já existe**: chama-se
`larga_em`, e é uma declaração de intenção. Duas das cinco receitas apontam para
pastas que não existem, e nada o detecta. Uma declaração feita antes da corrida
pode apodrecer em silêncio; um envelope é emitido por quem acabou de correr, e
não pode estar errado sobre o que acabou de fazer.

E o desenho C **não é invenção**: `coleta/italy_executor.py :: traduzir()` já
produz exactamente esta unidade — `EXECUTOR_ID` e `EXECUTOR_VERSION` declarados
por quem corre, `STORAGE_LOCATION` **ausente quando desconhecido, nunca
inventado**, `FACT_TIME` a recusar prosa. A forma já existia. Não tinha nome nem
validador.

O desenho A sobrevive **dentro** de C: cada unidade continua a ser governada por
`leis/artefato.py`. O envelope embrulha, não duplica.

---

## 6 · AS DEZ PERGUNTAS (FASE 6)

| # | pergunta | campo que a responde |
|---|---|---|
| 1 | a execução ocorreu? | `ESTADO` ∈ SUCCESS · PARTIAL · FAILED |
| 2 | produziu material coletado? | `len(COLHEITA)` |
| 3 | quais unidades são colheita? | `ESPECIE == COLHEITA` |
| 4 | quais são só suporte? | lista `SUPORTE` |
| 5 | onde estão os payloads? | `PAYLOAD.ONDE` + `PAYLOAD.ESTADO` |
| 6 | qual RUN os produziu? | `RUN_ID`, conferido contra cada unidade |
| 7 | qual `SOURCE_ID` é provado? | obrigatório; `NAO SEI` não serve para colheita |
| 8 | `DOCUMENT_ID` existe ou é UNKNOWN? | obrigatório declarar; `NAO SEI` permitido |
| 9 | qual unidade entra no Ingresso? | `so_o_que_entra()` |
| 10 | o que nunca chega à Admissão? | tudo o que não é `COLHEITA` |

**Nenhum campo obrigatório que a fonte não possa provar.** `DOCUMENT_ID` pode ser
`NAO SEI`; `FACT_TIME` não é exigido; o payload pode ser `NAO_SE_APLICA`.

---

## 7 · IMPACTO NOS EXECUTORES (FASE 10)

```
EXECUTORS_TOTAL    5
ALREADY_CONFORMING 0
NEED_ADAPTER       3
MISSING_PAYLOAD    4
NEED_RECOLLECTION  4
UNKNOWN            0
```

**Três famílias, não cinco missões:**

| família | executores | o que falta |
|---|---|---|
| **F1** forma já certa, nunca correu | `italia-recorrente` (T2) | só correr — precisa de rede |
| **F2** nunca correu, saída por definir | `eppo` (T3) | definir o retorno antes de correr |
| **F3** devolve suporte em vez de colheita | `rotulos-oficiais` · `corpus-pesquisador` · `comunicacao-publica` | declarar a espécie e apontar o payload |

```
A_CORRECAO_PODE_SER_FEITA_POR_FAMILIA = YES
```

---

## 8 · O QUE ESTA MISSÃO **NÃO** FEZ

- **não** alterou `a_colheita()` — continua com a heurística genérica;
- **não** adaptou nenhum executor;
- **não** recolheu material;
- **não** ligou o contrato ao runtime.

A lei existe e tem dentes. Ligá-la é outra missão, e ela sabe agora exactamente
quantas famílias tem pela frente.
