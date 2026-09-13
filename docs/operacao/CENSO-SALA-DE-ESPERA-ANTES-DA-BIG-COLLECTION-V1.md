# CENSO DA SALA DE ESPERA — antes da BIG COLLECTION

> **Missão:** `C-CENSO-SALA-DE-ESPERA-ANTES-DA-BIG-COLLECTION-V1`
> **Natureza:** censo / auditoria **READ-ONLY**. Não é limpeza, não é
> reprocessamento, não é Intelligence, não é Big Collection.
> **Medição:** `provas/o_censo_da_sala_de_espera.py`
> **Relatório máquina:** `data/derivados/O-CENSO-DA-SALA-DE-ESPERA.json`
>
> Este documento é **fotografia histórica**. Ele **não** passa a ser dono do
> estado: quem decide se um item está `READY` continua a ser
> `admissao.pronto_para_inteligencia()`, e o dono da morada continua a ser
> `admissao/sala_de_espera.py`.

---

## EM PALAVRAS FÁCEIS — as cinco respostas

**1 · Quantas coisas temos na Sala de Espera?**

**Nenhuma.** Zero ficheiros, zero unidades. A morada canónica
`data/samples/PRONTO-PARA-INTELIGENCIA/` **não existe** na árvore, e **nunca
existiu em commit nenhum de branch nenhuma**.

**2 · Quantas estão claramente boas?**

Zero — porque zero é o total. Não há nada bom nem mau lá dentro.

**3 · Quantas são antigas / incompletas / desconhecidas?**

**Zero.** Não há legado na Sala de Espera. Não há item incompleto, não há item
de origem desconhecida, não há `READY` falso pousado. **Não há estoque
nenhum.**

**4 · Conseguimos separar o estoque antigo das novas coletas?**

**Sim, e da maneira mais forte possível:** não há estoque antigo para separar.
A sala vazia é um **marco zero** — tudo o que aparecer lá a partir de agora é,
por construção, coleta nova.

**5 · Podemos começar a Big Collection agora, ou devemos organizar algo antes?**

**Pelo lado do estoque da Sala de Espera: SIM, com condições.** O estoque
existente **não impede** — não existe estoque. As condições não são sobre o que
está lá; são sobre **o que uma sala vazia não prova**, e estão escritas abaixo.

> ⚠️ **Este censo responde por UMA pergunta só: o estoque impede?** Ele **não**
> diz que o resto da máquina está pronto para escala. Isso é medido noutro
> sítio — `data/derivados/COLLECTION-V1-CLOSE-GATES.json` — e lá
> `BIG_COLLECTION_READY` tem os seus próprios critérios.

---

## O ACHADO QUE MUDA A LEITURA

A Sala de Espera **funciona** e **nunca foi usada**. As duas coisas ao mesmo
tempo, e não é contradição:

```
READY PROVADO                 YES — em árvore DESCARTÁVEL
READY POUSADO NA SALA REAL    NO  — zero, em toda a história do Git
```

Todas as provas que produzem `READY` — `provas/a_unidade_pousa_na_espera.py`,
`provas/o_pedido_t4_atravessa.py`, `provas/o_pedido_atravessa.py`,
`provas/a_maquina_sob_carga.py`, `provas/a_maquina_depois_do_crash.py`,
`provas/a_linhagem_do_reaproveitamento.py`, `provas/a_repeticao_do_scrap.py` —
**redirigem `espera.MORADA`** para um `tempfile.mkdtemp()` ou para uma árvore
descartável antes de escrever. A unidade pousa, é medida, e morre com o
temporário.

Por isso a frase de `COLLECTION-V1-CLOSE-GATES.json` —
*«ficheiros na sala DEPOIS: `['IT-T4-…json']`»* — é verdadeira e **não** é
estoque:

> **PROVADO EM DESCARTÁVEL ≠ POUSADO NA SALA.**
> Uma porta por onde alguém passou num ensaio continua sem ninguém do lado de lá.

---

## A TABELA

| medida | valor |
|---|---|
| `TOTAL_WAITING_ROOM_RECORDS` | **0** |
| `TOTAL_UNIQUE_READY_ITEMS` | **0** |
| | |
| `CURRENT_CANONICAL_PROVEN` | 0 |
| `LEGACY_PROVEN` | 0 |
| `MIXED_OR_TRANSITIONAL` | 0 |
| `UNKNOWN_ORIGIN` | 0 |
| | |
| `LINEAGE_FULL` | 0 |
| `LINEAGE_PARTIAL` | 0 |
| `LINEAGE_BROKEN` | 0 |
| `LINEAGE_UNKNOWN` | 0 |
| | |
| `READY_DECLARED` | 0 |
| `READY_CONTRACT_VALID` | 0 |
| `READY_CONTRACT_INVALID` | 0 |
| `READY_CONTRACT_UNKNOWN` | 0 |
| | |
| `SOURCE_ID_KNOWN` / `SOURCE_ID_UNKNOWN` | 0 / 0 |
| `SOURCE_ID_SUSPECTED_FABRICATED` | 0 |
| `DOCUMENT_ID_PROVEN` / `DOCUMENT_ID_UNKNOWN` | 0 / 0 |
| `DOCUMENT_ID_SUSPECTED_FABRICATED` | 0 |
| | |
| `TEXT_KIND_KNOWN` / `TEXT_KIND_UNKNOWN` | 0 / 0 |
| `LANGUAGE_KNOWN` / `LANGUAGE_UNKNOWN` | 0 / 0 |
| `FACT_TIME_KNOWN` / `FACT_TIME_UNKNOWN` | 0 / 0 |
| `SOURCE_LOCATION_KNOWN` / `UNKNOWN` | 0 / 0 |
| `FACT_LOCATION_KNOWN` / `UNKNOWN` | 0 / 0 |
| | |
| `BYTE_DUPLICATES` | 0 |
| `OBSERVATION_ID_DUPLICATES` | **NÃO MEDIDO** — e não zero |
| `READY_ID_DUPLICATES` | 0 |
| `POSSIBLE_SEMANTIC_DUPLICATES` | **NÃO SEI** |
| | |
| `LEGACY_BUT_USABLE` | 0 |
| `LEGACY_NEEDS_REPROCESSING` | 0 |
| `LEGACY_UNEXPLAINED` | 0 |
| | |
| `REPROCESS_CANDIDATES` | 0 |
| `QUARANTINE_CANDIDATES` | 0 |
| `REVIEW_REQUIRED` | 0 |
| `NO_ACTION` | 0 |
| `UNKNOWN_ACTION` | 0 |
| | |
| `RED_TEAM_ATTACKS` | **15** |
| `RED_TEAM_SURVIVORS` | **0** |
| | |
| `LIVE_READS` / `LIVE_WRITES` | **0 / 0** |
| `CENSUS_BLOCKED_BY_LIVE_MEASUREMENT` | **NO** |
| | |
| `BIG_COLLECTION_CAN_START` | **YES_WITH_CONDITIONS** |

> ⚠️ **Estes zeros não são todos a mesma coisa.** `READY_ID_DUPLICATES = 0` é
> uma contagem feita sobre zero itens. `OBSERVATION_ID_DUPLICATES` **não é 0**:
> é **NÃO MEDIDO**, porque `RAW_OBSERVATION_ID` não viaja no contrato `READY`
> e não há o que conferir. **NÃO MEDIDO ≠ ZERO.**

---

## QUEM É A SALA, MEDIDO E NÃO SUPOSTO

```
CANONICAL_WAITING_ROOM_OWNER      admissao/sala_de_espera.py
CANONICAL_WAITING_ROOM_LOCATION   data/samples/PRONTO-PARA-INTELIGENCIA/<RUN_ID>.json
CANONICAL_READY_CONTRACT          COL-LAW-043 — 11 campos
CONSTRUTOR (único)                admissao.pronto_para_inteligencia()
BACKEND                           FILESYSTEM (ADR-SALA-DE-ESPERA-V1)
WRITERS                           orquestrador/orquestrador.py:573
                                  coleta/rota_forward_documento.py:381
                                  — os dois chamam o dono; nenhum escreve sozinho
READERS                           0 — e é o estado certo antes da Intelligence
REPRESENTAÇÕES                    1
```

**A morada não foi copiada para dentro do censo.** A medição pergunta ao dono
(`espera.MORADA`) onde é a sala, e constrói os 11 campos chamando o construtor.
Uma lista escrita à mão no censo seria uma segunda declaração do contrato, e no
dia em que a `COL-LAW-044` permitir trocar o meio, o censo mediria a morada
velha e diria «vazia» sobre uma sala cheia.

### Não há segunda representação — e isto foi procurado, não assumido

O censo varreu **449 ficheiros `.json`/`.ndjson`** da árvore inteira à procura
de qualquer objecto com `ESTADO = PRONTO_PARA_INTELIGENCIA` ou com a forma
completa dos 11 campos.

```
OBJECTOS READY FORA DA SALA CANÓNICA    0
```

O enum `etapa_da_coleta` da migration 024 **tem** `'READY'` — mas isso é
**passagem de corrida** em `etapa_da_corrida`: telemetria, não a unidade.

> **ETAPA QUE PASSOU ≠ UNIDADE POUSADA.**

Nenhuma migration dá morada à Sala de Espera; a decisão de admissão não é
persistida em PostgreSQL. Por isso **nenhuma parte da sala vive só no LIVE**, e
`CENSUS_BLOCKED_BY_LIVE_MEASUREMENT = NO` — a resposta não depende de
credenciais que este ambiente não tem (e que continuam ausentes:
`SUPABASE_DB_URL`, `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`).

---

## ONDE A CADEIA QUEBRA — e ela quebra mesmo com zero itens

Esta é a parte que **zero itens não responderiam sozinhos**. Com a sala vazia,
contar quebras por item daria `0`, e `0 quebras` leria-se como «a cadeia
fecha». **Ela não fecha.** Quebra por construção — e a construção está em Git,
não nos itens.

Medido por AST, dos dois lados da porta:

```
A ROTA ENTREGA À PORTA     captured_at · id · raw_asset_id · texto · url
O READY LÊ DO ITEM         captured_at · data · fact_location · fact_time ·
                           fonte · id · source_id · source_location ·
                           texto · title · url
NÃO ATRAVESSA              raw_asset_id
```

**`raw_asset_id` é a única chave que a rota entrega à porta e que o caminho do
`READY` nunca lê.** E `RAW_OBSERVATION_ID = raw_asset.id` é a identidade
canónica da observação.

Consequência medida, e não opinião:

> **`LINEAGE_FULL` é inatingível a partir de um item pousado — e isso é a
> `COL-LAW-043` a cumprir-se**, não um defeito novo: a lei manda a inteligência
> receber 11 campos **e mais nada**, e `RAW`/`STORAGE` não estão entre eles.
> A cadeia até ao byte fecha-se pelo **ledger da corrida**, por `CORRIDA`.

O mesmo vale para o texto: o contrato E7 (`regras/proveniencia.py` —
`TEXT_UNITS` com `TEXT_KIND` · `LANGUAGE` · `TEXT_RELATION` ·
`RAW_OBSERVATION_ID`) **não atravessa**. O `READY` leva `TEXTO`, uma string.

> Por isso `TEXT_KIND`, `TEXT_RELATION` e `LANGUAGE` ficarão **UNKNOWN para todo
> item futuro** — e não por falta de dado a montante, mas porque o contrato da
> sala não tem onde os pousar.

**Isto é dívida de RECONCILIAÇÃO, e ela cresce com o volume.** Não bloqueia
começar. Fica muito mais cara depois de um milhão de itens do que antes do
primeiro.

---

## A FILA A MONTANTE — o que pode chegar, e que **não é** a sala

> ⚠️ O dono deste número é `provas/o_censo_do_acervo.py`. Aqui ele entra como
> **conferência**, nunca como segunda verdade. **OBSERVADO PELO COLETOR ≠
> ADMITIDO ≠ POUSADO NA SALA.**

| medida | valor |
|---|---|
| observações no livro italiano | 144 |
| corridas no livro | 6 (todas `PILOT_RUN`, 2026-09-07) |
| primeiras observações | 35 |
| reobservações (`SEEN_AGAIN`) | 109 |
| `DOCUMENT_ID` distintos | 35 |
| `RAW_SHA256` distintos | 35 |
| com caminho de bytes declarado | 35 |
| **com bytes mesmo na árvore** | **10** |
| ficheiros no armazém | 10 |
| `COLLECTED_TIME` conhecido / desconhecido | 144 / 0 |
| `FACT_TIME` conhecido / desconhecido | 12 / 132 |

**Concentração por fonte** — e ela é extrema:

```
IT-T2-002   124 de 144   86%
IT-T2-004     6
IT-T3-005     6
IT-T3-002     2
IT-T3-008     2
IT-T3-010     2
IT-T4-001     2
```

> **86% da fila vem de UMA fonte.** Isto não é cobertura: é uma fonte que
> publica muito. Vale como aviso para o desenho da Big Collection, e **não** é
> um bloqueador do estoque.

⚠️ **35 grupos de bytes idênticos não são 35 documentos duplicados.** São 35
conjuntos de bytes observados mais de uma vez, porque reobservar a mesma
publicação devolve os mesmos bytes. **REOBSERVAR NÃO É DUPLICAR:** o documento é
um, e as observações dele são várias.

⚠️ **25 observações declaram caminho de bytes que não está na árvore** (35
declarados, 10 presentes). Isto é medição da fila, já conhecida do censo do
acervo — **não** é item da Sala de Espera, e não foi tocado.

---

## RED TEAM — 15 ataques, 0 sobreviventes

Cada ataque morre contra um **número** desta medição, nunca contra um
argumento.

| # | ataque | como morre |
|---|---|---|
| 1 | mesmo item em duas representações contado duas vezes | 449 ficheiros varridos · 0 objectos `READY` fora da sala canónica |
| 2 | SHA igual tratado como mesma observação | balde próprio + `OBSERVATION_ID_MEDIDO = NO` (e não `0`) |
| 3 | `SOURCE_ID` ausente fabricado de URL | lido do campo do contrato; nenhuma URL/path/slug entra nele |
| 4 | `DOCUMENT_ID` fabricado de SHA | `DOCUMENT_ID_PROVEN = 0`; não há caminho de código que o derive |
| 5 | `SOURCE_LOCATION` copiado para `FACT_LOCATION` | dois baldes, dois campos, sem fallback entre eles |
| 6 | publication time copiado para fact time | `PUBLICATION_TIME` não tem campo no contrato |
| 7 | `UNKNOWN` contado como vazio / `NO` | `_sabido()` devolve `False` para vazio **e** para `NAO SEI`/`NÃO SEI`/`UNKNOWN` |
| 8 | `NOT_APPLICABLE` contado como `PASS` | `RAW`/`STORAGE` fora do contrato contam como *missing*, e travam `LINEAGE_FULL` |
| 9 | `READY` declarado sem item na sala | conta ficheiros REAIS na morada do dono; provas usam morada descartável |
| 10 | item sem `RUN` contado como linhagem completa | exige `CORRIDA` presente **e igual** à do ficheiro |
| 11 | legado classificado como atual só por data | nenhuma classificação lê data — o critério é a **forma** |
| 12 | ficheiro novo com conteúdo antigo dado como novo | origem sai dos campos do item, nunca da idade do ficheiro |
| 13 | dois `RUN`s da mesma fonte colapsados | um ficheiro por corrida + `RUN_ID_CONFLICT` no dono |
| 14 | língua da publicação herdada pelo texto | contrato não tem campo de língua · `LANGUAGE_KNOWN = 0` |
| 15 | filename usado como identidade | identidade é `(CORRIDA, ITEM_ID)`, lida de dentro; `RUN_ID` reconferido no corpo |

### E o ataque que o censo fez a si próprio

> **UM CENSO QUE DEVOLVE SEMPRE ZERO NÃO É UM CENSO.**
> **ZERO MEDIDO E ZERO POR AVARIA SÃO O MESMO NÚMERO.**

`tests/test_o_censo_da_sala_de_espera.py` — **14 casos** — enche uma sala
**descartável** e exige que o contador se mexa: 3 ficheiros dão 3 registos e 7
itens; sentinela conta como `UNKNOWN`; `CORRIDA` diferente da do ficheiro quebra
a ligação; forma de outra era com ligações completas dá `LEGACY_PROVEN`;
ficheiro ilegível não vira zero silencioso. A morada de produção nunca é tocada.

---

## REPRODUTIBILIDADE

```
ITEM_COUNT_RUN1            = ITEM_COUNT_RUN2            = 0
CLASSIFICATION_RUN1        = CLASSIFICATION_RUN2        (idênticas)
SHA256 DO RELATÓRIO RUN1   = SHA256 DO RELATÓRIO RUN2   (byte a byte)
```

O relatório **não carrega timestamp de geração**, então as duas corridas dão o
mesmo ficheiro — não há campo a excluir de impressão nenhuma. Isto é testado:
`test_duas_corridas_dao_o_MESMO_relatorio_byte_a_byte`.

E o censo **só escreve o próprio relatório** —
`test_o_censo_nao_escreve_fora_do_proprio_relatorio` mede o `git status` antes e
depois. Nenhum ficheiro foi apagado, movido, renomeado, tocado ou reescrito.
A morada medida **não foi criada** pelo acto de a medir.

---

## REGRESSÃO

```
PRODUCTION_CODE_CHANGES = 0
```

Nenhum ficheiro de produção foi alterado. O que entrou:

| ficheiro | o que é |
|---|---|
| `provas/o_censo_da_sala_de_espera.py` | a medição |
| `tests/test_o_censo_da_sala_de_espera.py` | as guardas do instrumento (14 casos) |
| `data/derivados/O-CENSO-DA-SALA-DE-ESPERA.json` | o relatório máquina |
| 8 documentos, 1 linha cada | `TEST_COUNT_CURRENT` 3.874 → 3.888 |

**A suíte foi medida dos dois lados, e o delta é conhecido item a item:**

```
BASELINE (sem estes ficheiros)   3.867 testes · 18 falhas · 16 erros · 194 pulados
COM O CENSO                      3.881 testes · 24 falhas · 16 erros · 194 pulados
```

As **6 falhas novas** foram identificadas pelo nome e todas eram
**escrituração**, nenhuma comportamento:

- **5 ×** `TEST_COUNT_CURRENT` — a casa publica a contagem da suíte em
  documentos, e 14 provas novas movem-na. Corrigido com o remédio da própria
  casa: `python3 pacote/metricas_canonicas.py --sync`, que mexeu **só** nessa
  métrica, em 8 documentos.
- **1 ×** `test_rt7b_o_ficheiro_partido_nao_deixou_nada_no_acervo` — exige que
  `git status` não tenha nada por versionar dentro de `data/`. Resolve-se
  **versionando o relatório**, que é o destino dele.

> As **18 falhas e 16 erros restantes são anteriores a esta missão** e estão no
> `HEAD` funcional sem estes ficheiros. Não foram tocadas — medir não é
> consertar.

---

## SYSTEM MAP

O System Map continua **paralelo**: nenhuma branch foi integrada e nenhuma
arquitetura foi actualizada por causa de achado do censo.

```
SYSTEM_MAP_DELTA = uma medição nova em `provas/`, e o teste dela em `tests/`
                   — `provas/o_censo_da_sala_de_espera.py`
                   — `tests/test_o_censo_da_sala_de_espera.py`
```

Declarado, e não integrado.

---

## KNOW-HOW

```
KNOW_HOW_HEAD = NÃO ESTÁ NESTE REPOSITÓRIO
```

`SINTONIA-EAME-KNOW-HOW.md` não existe em `origin/main` nem na linha funcional;
o `§74` é citado pelo `ADR-SALA-DE-ESPERA-V1` mas o documento vive fora da
árvore. Não foi possível ler nem comparar.

```
KNOW_HOW_DELTA = ATUALIZAÇÃO NECESSÁRIA
```

Três coisas duráveis, e **nenhuma delas é um número deste censo** (números são
fotografia):

1. **A Sala de Espera tem UMA representação, e ela é o filesystem.** O `'READY'`
   do enum `etapa_da_coleta` é passagem de corrida, não unidade.
   **ETAPA QUE PASSOU ≠ UNIDADE POUSADA.**
2. **`READY` provado em árvore descartável não é estoque na sala.** Toda prova
   que produz `READY` redirige `espera.MORADA`. Ler «ficheiros na sala DEPOIS»
   de um relatório de prova como estoque é o erro que este censo teve de
   desfazer.
3. **`raw_asset_id` chega à porta e não atravessa para o `READY`.** A cadeia até
   ao byte só fecha pelo ledger da corrida — e o contrato E7 do texto também não
   atravessa. É dívida de reconciliação, e ela cresce com o volume.

---

## VEREDITO

```
SALA_DE_ESPERA_CENSUS    = PASS
BIG_COLLECTION_CAN_START = YES_WITH_CONDITIONS
```

**`PASS`** porque tudo o que a missão pediu foi medido: a sala tem dono, morada
e contrato conhecidos; o universo foi varrido inteiro; nenhuma parte ficou por
medir por falta de acesso — nem o LIVE, porque a sala não vive lá.

**`YES_WITH_CONDITIONS`** porque o estoque **não impede** — não existe estoque —
mas uma sala vazia **não prova** que a rota aguenta volume.

### AS CONDIÇÕES, exactamente

1. **Toda unidade nova pousa por `admissao/sala_de_espera.py`.** É o único dono
   da morada. Segunda escrita = segunda verdade.
2. **Toda corrida nova carrega `RUN_ID` próprio**, e o ficheiro da sala é dessa
   corrida. A sala vazia faz de **marco zero**: tudo o que aparecer depois é
   coleta nova **por construção**, sem precisar de rótulo.
3. **A ponte `READY → RAW/STORAGE` tem de existir antes de a escala a tornar
   cara.** `raw_asset_id` não atravessa o contrato de 11 campos, e a
   reconciliação só é possível pelo ledger da corrida. Reconciliar 1.000 itens é
   trabalho; reconciliar 1.000.000 é outra missão.
4. **`TEXT_KIND`, `TEXT_RELATION` e `LANGUAGE` vão ficar `UNKNOWN` para todo item
   novo**, porque o contrato E7 não atravessa. Se a Intelligence precisar deles,
   isso é decisão a tomar **antes** da coleta grande, não depois.
5. **Medir de novo depois do primeiro lote.** Um censo antes da coleta não é um
   censo durante.

### O que este veredito NÃO diz

Não diz que a Big Collection **deve** começar. Não diz que a máquina está pronta
para escala — `BIG_COLLECTION_READY` é medido em
`data/derivados/COLLECTION-V1-CLOSE-GATES.json`, com critérios próprios que
incluem integração do SCRAP e observabilidade para escala.

> **Diz uma coisa só: O ESTOQUE DA SALA DE ESPERA NÃO IMPEDE COMEÇAR.**

---

## HARD STOP

Nada foi limpo, reprocessado, movido, deduplicado, consolidado ou re-admitido.
Nenhuma coleta foi iniciada. Nenhum `SCRAP` real correu. Nenhuma chamada paga.
Intelligence não foi chamada. O Portal não foi tocado.

**A decisão volta ao coordenador.**
