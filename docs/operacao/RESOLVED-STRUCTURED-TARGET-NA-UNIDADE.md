# `RESOLVED_STRUCTURED_TARGET` — a unidade diz o que produziu

**C-PLAN-A5.3 · fecha o bloqueio D2 · 2026-09-10 · ramo `claude/raw-observation-identity-3jbwco`**

> **Nada foi implementado.** Zero runtime, zero banco, zero migration, zero contrato de
> fonte, zero `source_document`, zero registo T-06, zero T-32, zero Admission, zero READY,
> zero System Map, zero Bíblia.

```
LOCAL_HEAD = REMOTE_HEAD = 87216cf7ada942f853643f96aa5f8d2c2e6d67e5
WORKTREE   = limpa   ·   DIVERGENCE = 0
```

---

## 1 · O ACHADO — o D2 não é «falta um campo». É «falta o objecto».

Medi os três caminhos do primeiro slice, e só eles.

### O que sai do coletor

`coleta/italy_pilot_collect.mjs` produz **observações de livro**: 25 campos, uma linha
NDJSON por observação, em `data/collection-ledger/italy/observations.ndjson`. Não produz
unidade nenhuma.

### O que o T-32 consome

`coleta/rota_forward_documento.py` lê um `dict` com **10 chaves**:

```
INDEXADAS DIRECTAMENTE (KeyError sem elas)
  na entrada de derivar()      RAW_ASSET_ID · PDF
  em estruturar(), já sobre a unidade que o próprio T-32 montou   CONTENT_ID · TEXTO

LIDAS COM .get() (toleram ausência)
  SOURCE_ID · ROUTE_CLASS_ID · CAPTURED_AT · URL · TIPO · RULE_VERSION
```

E o que o T-32 acrescenta à unidade antes de a passar adiante:
`TEXTO` · `CONTENT_ID` · `DERIVED_STORAGE_PATH` (`:319-322`).

### Quem constrói essa unidade

```
CURRENT_UNIT_PRODUCER = NINGUÉM EM RUNTIME
```

O único construtor é `tests/test_m2_rota_forward.py:259-264`. Nenhum ficheiro de produção
monta o `dict` que o T-32 exige.

> ## O D2 NÃO É ACRESCENTAR UM CAMPO A UM OBJECTO EXISTENTE.
> ## O OBJECTO NÃO TEM PRODUTOR.
> O coletor fala **observação**; o T-32 fala **unidade**; e entre os dois não há tradutor.

### E a casa já resolveu este problema uma vez, do outro lado

`coleta/ingresso.py::para_o_dono_do_raw` existe exactamente para isto, e diz porquê:

> *«A casa tem DUAS linguas de artefato, e as duas estao certas … `preservar()` nunca
> aceitou um `Artefato`: ele pede `COUNTRY`, `SOURCE_SLUG`, `ARTIFACT_KIND` … Nada no
> repositorio ligava as duas.*
> ***DOIS CONTRATOS CERTOS E NENHUMA PONTE SAO DOIS CONTRATOS QUE NAO SE USAM.»***

A ponte existe para o RAW. **Para o STRUCTURED não existe** — e é nela que o
`RESOLVED_STRUCTURED_TARGET` nasce.

```
CURRENT_T32_INPUT_BOUNDARY = rota_forward_documento.atravessar(banco, unidade=…, …)
                             — a fronteira existe; o que a atravessa não é produzido
```

---

## 2 · O CAMPO

```
RESOLVED_STRUCTURED_TARGET_FIELD = RESOLVED_STRUCTURED_TARGET
RESOLVED_STRUCTURED_TARGET_TYPE  = UM CONCEPT_ID, do vocabulário fechado da A5.2
                                   escalar · não é lista · não é texto livre
```

O par lê-se sozinho, e a diferença é de número e de dono:

```
ALLOWED_STRUCTURED_TARGETS   LISTA    na FONTE      «o que esta fonte PODE produzir»
RESOLVED_STRUCTURED_TARGET   ESCALAR  na UNIDADE    «o que esta unidade PRODUZIU»
```

---

## 3 · UM ALVO POR UNIDADE

```
RESOLVED_STRUCTURED_TARGETS_PER_UNIT = ONE
```

Confirmado pela arquitectura já fechada, e não por gosto:

1. **A4 fechou `ONE CONCEPT → ONE OWNER`.** Uma unidade com dois alvos obrigaria o T-32 a
   despachar a mesma unidade para dois donos — e nenhum dos dois seria dono dela.
2. **O rastro não aceita dois grãos numa passagem.** `etapa_da_corrida` tem `UNIQUE
   (run_id, etapa, tentativa)` e **um** `output_grain` com **um** `output_count`, e a lei
   diz `INPUT != OUTPUT QUANDO O GRAO MUDA`. Dois conceitos numa unidade cairiam em
   `GRAIN_MISMATCH` — código que já existe: *«contou-se entrada e saida em unidades
   diferentes. A razao entre elas nao e rendimento.»*
3. **Os grãos são mesmo diferentes.** A A5.1 mediu: `source_document` é a versão do
   documento; um registo regulatório é uma linha. Somá-los é a conta que a migration 024
   foi escrita para impedir.

---

## 4 · UMA OBSERVAÇÃO, VÁRIAS UNIDADES

```
ONE_RAW_CAN_PRODUCE_MULTIPLE_UNITS = YES
EACH_UNIT_HAS_OWN_TARGET           = YES
```

Medido, não suposto: `IT-T2-004` produziu **1 documento e 1045 linhas na mesma observação**;
`IT-T3-005`, **1 documento e 139 pontos**.

```
1 RAW observation
   ├─ unidade A   RESOLVED_STRUCTURED_TARGET = SOURCE_DOCUMENT
   ├─ unidade B   RESOLVED_STRUCTURED_TARGET = REGULATORY_REGISTRATION
   └─ unidade C   RESOLVED_STRUCTURED_TARGET = REGULATORY_REGISTRATION
```

Cada unidade carrega **a sua** identidade, **o seu** alvo e **a sua** linhagem — e todas
apontam para a mesma observação RAW, que é a testemunha comum.

**A forma da saída já existe nesta casa: uma LISTA.** `derivacao_forward.correr(unidades,
…)` e `ingresso.receber(itens, …)` já recebem listas. O executor devolve uma lista de
unidades auto-contidas — **nunca uma unidade gigante com vários conceitos dentro**.

> Juntar as 1045 linhas e o documento numa unidade só porque vieram da mesma ida à fonte
> seria repetir, um andar acima, o erro que a C-PLAN-0 desfez em baixo: confundir
> **a ida** com **o que foi trazido**.

---

## 5 · QUEM CARIMBA, E QUANDO

```
RESOLVED_TARGET_WRITER       o EXECUTOR que materializa a unidade
RESOLVED_TARGET_WRITE_MOMENT no acto de materializar — depois de a unidade satisfazer a
                             identidade do conceito, e antes de a entregar
```

```
executor busca / deriva
        ↓
materializa a unidade  (identidade completa)
        ↓
confirma o que produziu, contra o vocabulário fechado
        ↓
carimba RESOLVED_STRUCTURED_TARGET
        ↓
entrega a lista de unidades ao T-32
```

**Isto não faz do executor um cérebro**, e a razão é a mesma que a A4 deu: ele **rotula o
que acabou de produzir** com um valor que o contrato da fonte já autorizou. É exactamente a
forma que `derivacao_forward` já usa ao declarar `DERIVATION_TYPE` — o executor diz o que
fez, não decide o que devia ter feito.

E como o produtor da unidade **não existe** (§1), o carimbo nasce junto com a ponte, no
mesmo acto — não se acrescenta a nada.

---

## 6 · A EVIDÊNCIA MÍNIMA PARA CARIMBAR `SOURCE_DOCUMENT`

> ## NÃO SE DECLARA UM CONCEITO ANTES DE A UNIDADE SATISFAZER A IDENTIDADE DELE.

A identidade fechada pela A5.1 é `(source_id, document_id, document_version_id)`. E a A2
fechou que ninguém chama a porta sem linhagem RAW. Logo:

```
SOURCE_DOCUMENT_MINIMUM_RESOLUTION_EVIDENCE

  SOURCE_ID             valor real
  DOCUMENT_ID           valor real
  DOCUMENT_VERSION_ID   valor real
  RAW_OBSERVATION_ID    a observação de onde se leu   (A5.1: NOT NULL, testemunha)
```

**Quatro, e nem um a mais.** `PDF`, `MIME`, `TEXTO`, `URL` e `TIPO` **não** entram: nenhum
deles faz parte da identidade do conceito, e exigi-los faria um documento HTML ou CSV
falhar por não ser PDF.

**«Valor real» tem definição, e é lei desta casa** — COL-LAW-034: *«`"?"` e a string vazia
NÃO DEVEM ser usados como identidade. `UNKNOWN` fica explícito.»* Um `DOCUMENT_ID` a dizer
`NÃO SEI` não satisfaz a identidade: **não se carimba, e diz-se porquê**.

Medido: as 144 observações do livro têm os três campos de identidade preenchidos, **zero
sentinelas**. A evidência mínima não é teórica — ela já existe no dado.

---

## 7 · O T-32 NÃO PODE ADIVINHAR

```
T32_CAN_INFER_RESOLVED_TARGET = NO
```

Proibido inferir o alvo a partir de:

```
extensão .pdf        MIME / assinatura de bytes      SOURCE_ID
nome do executor     nome do ficheiro                presença do campo PDF
universo             qualquer combinação dos acima
```

Não é regra nova: é a COL-LAW-034 aplicada aqui — ***IDENTIDADE NUNCA POR SIMILARIDADE
TEXTUAL*** — e é a mesma proibição que a A3 já escreveu como portão
(`T32_GUESSES_STRUCTURED_FROM_FIELDS = NO`).

**Campo ausente não se preenche por dedução.** Uma inferência que acerta 99 vezes ensina
toda a gente a confiar nela, e é na centésima que ela põe um boletim regional dentro da
tabela de outra espécie sem ninguém reparar.

---

## 8 · OS QUATRO ESTADOS, E CADA UM ACUSA OUTRO CULPADO

| situação | código | novo? | quem tem de agir |
|---|---|---|---|
| a **fonte** não declara `ALLOWED_STRUCTURED_TARGETS` | `STRUCTURED_TARGET_NOT_DECLARED` | A5.2 | quem mantém o contrato |
| a **unidade** chega sem `RESOLVED_STRUCTURED_TARGET` | **`STRUCTURED_TARGET_NOT_RESOLVED`** | **novo, A5.3** | quem escreveu o executor |
| a unidade declara alvo **fora da lista** | `STRUCTURED_TARGET_NOT_ALLOWED` | A5.2 | contrato **ou** executor — a divergência é o achado |
| alvo permitido, **dono não ligado** | `OWNER_NOT_CONNECTED` | **já existe** | quem liga o dono |

```
MISSING_RESOLVED_TARGET_BEHAVIOR = STRUCTURED_TARGET_NOT_RESOLVED · FAIL · sem fallback
```

**Por que um código novo e não o reaproveitamento do da A5.2.** Antes de o criar, medi o
registo de `leis/diagnostico.py` — 17 códigos — e nenhum responde a esta pergunta.
`GRAIN_NOT_DECLARED` é o vizinho mais próximo e fala de **contagem sem grão**, não de
unidade sem espécie. E o `STRUCTURED_TARGET_NOT_DECLARED` acusa **a fonte**; este acusa **o
executor**. Um código só mandaria a pessoa abrir o ficheiro errado.

> ## UM CÓDIGO É UM ENDEREÇO. DOIS CULPADOS, DOIS ENDEREÇOS.

---

## 9 · ONDE A CONFERÊNCIA ACONTECE

```
TARGET_NOT_ALLOWED_CHECK_OWNER = T-32, na fronteira, ANTES de despachar
```

Sem reabrir autoridade: a A4 fechou que o T-32 **confere** e não escolhe.

E há uma consequência que fica dita em vez de ser descoberta depois: **para conferir, o
T-32 tem de ler `ALLOWED_STRUCTURED_TARGETS` do contrato da fonte**, por `SOURCE_ID`. Não
serve o executor mandar a lista dentro da unidade — isso seria deixá-lo assinar a própria
licença. **Conferir exige uma segunda fonte de verdade, e é esse o ponto de haver
conferência.**

---

## 10 · LISTA VAZIA

```
EMPTY_ALLOWED_LIST_CAN_EMIT_TARGET = NO
```

Se `ALLOWED_STRUCTURED_TARGETS = []`, o executor **não carimba nada**, e a travessia
termina legitimamente em DERIVED, com a etapa STRUCTURED em `NOT_APPLICABLE`.

Uma unidade dessa fonte que chegue **com** alvo cai em `STRUCTURED_TARGET_NOT_ALLOWED`:
qualquer valor está fora de uma lista vazia. A trava fecha sozinha, sem regra especial.

⚠️ **O código de razão desse `NOT_APPLICABLE` fica `NÃO SEI`.** Os quatro códigos da A3 não
cobrem «a fonte não está autorizada», e a A5.2 mediu **zero** fontes com `[]`. **Não se
cria código para caso que ainda não existe** — quando existir, existe com razão escrita.

---

## 11 · O EXEMPLO — uma unidade real, medida ponta a ponta

Fixture: `IT-T2-002` (ARPAV Veneto), uma das 7 fontes autorizadas pela A5.2.

```
OBSERVAÇÃO RAW  (data/collection-ledger/italy/observations.ndjson)
  RUN_ID               PILOT_RUN_20260907153737_4c34b3
  SOURCE_ID            IT-T2-002
  DOCUMENT_ID          ARPAV:Z01:20260903160930
  DOCUMENT_VERSION_ID  v1_f88c89d73d6a
  RAW_SHA256           f88c89d73d6a132a1c1ec6e87aadd893dd1f1028425dcf0fc4ffb37ab29170af
  BYTES                463630        MIME  PDF
  RAW_PATH             data/collection-store/italy/IT-T2-002/ARPAV_Z01_20260903160930/…/agro_01.pdf

DERIVADO  (data/derivados/REGISTO-DE-ARTEFATOS.json)
  ARTIFACT_ID          DERIVED-TEXT_EXTRACTION-38547b91337c00b4
  DERIVATION_TYPE      TEXT_EXTRACTION
  PARENT_SHA256        f88c89d73d6a…            ← o mesmo conteúdo acima
  STORAGE_LOCATION     data/derivados/texto/RAW-f88c89d73d6a132a.txt

A UNIDADE QUE O EXECUTOR ENTREGARIA
  SOURCE_ID                  IT-T2-002
  DOCUMENT_ID                ARPAV:Z01:20260903160930
  DOCUMENT_VERSION_ID        v1_f88c89d73d6a
  RAW_OBSERVATION_ID         <a linha de raw_asset desta observação>
  RESOLVED_STRUCTURED_TARGET SOURCE_DOCUMENT      ← o carimbo

O QUE O T-32 FAZ, E SÓ ISTO
  lê ALLOWED_STRUCTURED_TARGETS de IT-T2-002        →  [SOURCE_DOCUMENT]
  confere SOURCE_DOCUMENT ∈ [SOURCE_DOCUMENT]       →  PASS
  despacha para o dono de SOURCE_DOCUMENT           →  D3, não é desta missão
```

**O T-32 nunca pergunta que espécie de coisa isto é.** A resposta chegou carimbada, e ele
só confirma que era permitida.

⚠️ **Honestidade sobre este derivado:** a linha do registo traz `SOURCE_ID: "NAO SEI"` e um
`RUN_ID` próprio (`DERIV-PDF-20260908T023205Z`) — ela veio do lote **legado** que varreu o
acervo de PDF, não da rota forward. A rota forward já passa a fonte adiante
(`derivacao_forward.correr(…, source_id=…)`), e por isso a unidade acima consegue carregar
`SOURCE_ID`. **Pela via legada não conseguiria** — e isso fica registado, não corrigido.

---

## 12 · ENTREGA

| | |
|---|---|
| **A** `BRANCH` | `claude/raw-observation-identity-3jbwco` |
| **B** `INITIAL_HEAD` | `87216cf7ada942f853643f96aa5f8d2c2e6d67e5` |
| **D** `WORKTREE` | limpa |
| **E** `CURRENT_UNIT_PRODUCER` | **nenhum em runtime** — só `tests/test_m2_rota_forward.py` |
| **F** `CURRENT_UNIT_SHAPE` | `dict` de 10 chaves; obrigatórias na entrada: `RAW_ASSET_ID` · `PDF` |
| **G** `RESOLVED_STRUCTURED_TARGET_FIELD` | `RESOLVED_STRUCTURED_TARGET` |
| **H** `RESOLVED_STRUCTURED_TARGET_TYPE` | um `CONCEPT_ID` escalar, vocabulário fechado |
| **I** `RESOLVED_STRUCTURED_TARGETS_PER_UNIT` | **ONE** |
| **J** `RESOLVED_TARGET_WRITER` | o **executor** que materializa a unidade |
| **K** `RESOLVED_TARGET_WRITE_MOMENT` | ao materializar, depois de a identidade estar completa, antes de entregar |
| **L** `SOURCE_DOCUMENT_MINIMUM_RESOLUTION_EVIDENCE` | `SOURCE_ID` · `DOCUMENT_ID` · `DOCUMENT_VERSION_ID` · `RAW_OBSERVATION_ID`, todos com valor real |
| **M** `T32_CAN_INFER_RESOLVED_TARGET` | **NO** |
| **N** `MISSING_RESOLVED_TARGET_BEHAVIOR` | `STRUCTURED_TARGET_NOT_RESOLVED` · `FAIL` · sem fallback · **código novo** |
| **O** `TARGET_NOT_ALLOWED_CHECK_OWNER` | **T-32**, como conferente, lendo o contrato da fonte |
| **P** `EMPTY_ALLOWED_LIST_CAN_EMIT_TARGET` | **NO** |
| **Q** `ONE_RAW_CAN_PRODUCE_MULTIPLE_UNITS` | **YES** — medido: 1 observação → 1 documento + 1045 linhas |
| **R** `EACH_UNIT_HAS_OWN_TARGET` | **YES** |
| **S** `CURRENT_RUNTIME_FILES_CHANGED` | **0** |
| **T** `CONTRACT_FILES_CHANGED` | **0** |
| **U** `DATABASE_MUTATIONS` | **0** |
| **V** `SYSTEM_MAP_CHANGED` | **0** |
| **W** `BIBLE_CHANGED` | **0** |
| **X** `UNRESOLVED_CRITICAL_A5_3_QUESTIONS` | **0** |

### O que continua `NÃO SEI` — e nenhum bloqueia

1. Código de razão para `NOT_APPLICABLE` por lista vazia — zero casos medidos (§10).
2. O lote legado de derivação não carrega `SOURCE_ID` (§11). A rota forward carrega.
3. Onde exactamente mora a ponte observação→unidade — é implementação, e o contrato dela
   está fechado aqui.

---

## 13 · VEREDITO

```
RESOLVED_TARGET_FIELD                = CLOSED
RESOLVED_TARGET_PER_UNIT_CARDINALITY = CLOSED   ONE
RESOLVED_TARGET_WRITER               = CLOSED   o executor
RESOLUTION_MOMENT                    = CLOSED   ao materializar, antes de entregar
MINIMUM_RESOLUTION_EVIDENCE          = CLOSED   4 campos, com valor real
MISSING_TARGET_FAILURE               = CLOSED   código novo, culpado próprio
T32_INFERENCE_PROHIBITION            = CLOSED   NO, e sem excepção

C-PLAN-A5.3 = PASS
```

O futuro T-32 nunca precisa de perguntar *«que tipo de coisa será que esta unidade é?»*. A
resposta chega pronta, comprovada pelo executor, e ele só confere se era permitida.

---

## 14 · EM PALAVRAS FÁCEIS

1. **O que é `RESOLVED_STRUCTURED_TARGET`?** O carimbo que a unidade traz a dizer que
   espécie ela é. Uma palavra, de uma lista fechada.

2. **Quem põe esse nome?** O executor, no momento em que constrói a unidade — quando ele
   ainda sabe o que acabou de fazer. Depois disso ninguém mais sabe.

3. **Uma fonte pode produzir várias unidades diferentes?** Pode. O SIAS traz um documento e
   mil e quarenta e cinco linhas na mesma ida. São mil e quarenta e seis unidades.

4. **Cada unidade recebe um nome só?** Um só. Duas espécies na mesma unidade fariam a conta
   de entrada e saída medir coisas diferentes, e isso já tem nome de erro nesta casa.

5. **O T-32 pode adivinhar pelo PDF ou pelo nome da fonte?** Não. Nem pela extensão, nem
   pelo MIME, nem pelo executor, nem pelo universo. Adivinhar acerta muitas vezes, e é a vez
   em que erra que ninguém vê.

6. **E se o executor esquecer de informar?** Falha com nome próprio,
   `STRUCTURED_TARGET_NOT_RESOLVED`, que aponta para o executor — e não para o contrato da
   fonte, que é outro culpado.

7. **E se informar um tipo que a fonte não pode produzir?** Falha também, e sem plano B. A
   divergência entre o que a fonte autoriza e o que o executor diz ter feito é o achado, não
   um detalhe a contornar.

8. **Como fica o exemplo?** O boletim da zona 1 da ARPAV: fonte `IT-T2-002`, documento
   `ARPAV:Z01:20260903160930`, versão `v1_f88c89d73d6a`, carimbo `SOURCE_DOCUMENT`. O T-32
   lê a lista da fonte, vê que é permitido, e despacha.

9. **Algum código foi alterado?** Nenhum. E medi uma coisa que não esperava: a unidade que
   o T-32 exige **não tem produtor nenhum** hoje — só um teste a monta. O D2 não era um
   campo em falta; era o objecto inteiro.

10. **Qual é o próximo bloqueio?** O **D3**: qual módulo é dono de cada `CONCEPT_ID`. Aqui
    só carregámos o nome; falta saber a quem entregá-lo.

> **HARD STOP.** O campo, a cardinalidade, o autor, o momento, a evidência mínima, a falha e
> a proibição de inferência estão fechados. Não se inicia o D3.
