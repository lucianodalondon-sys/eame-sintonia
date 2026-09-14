# CENSO DO CORPUS ROTULADO DA ADMISSION

> **Isto é uma fotografia, não um contrato novo.** As leis continuam na
> [`BIBLIA-CANONICA-DA-COLETA.md`](../../BIBLIA-CANONICA-DA-COLETA.md); o método
> continua no [`README.md`](../../README.md).
>
> **A pergunta:** o SINTONIA tem hoje corpus rotulado, confiável e diverso o
> bastante para **avaliar** — e eventualmente **treinar** — um classificador
> semântico da Admission?
>
> **A resposta medida** (setembro de 2026, na fotografia original):
>
> ```
> T2  = B   serve para AVALIAR · não serve para treinar
> T3  = D   T4 = D   T7 = D   T9 = D
> T1 · T5 · T10 · T11 · T12 · T13 = D
> OVERALL_VERDICT = B
> ```
>
> **T3 mudou depois.** A revisão humana fechou e T3 passou de `D` a `B`. A
> fotografia acima fica como estava — ela é o que se via naquele dia. O que
> mudou está na [secção 8](#8--atualização-t3--11092026), no fim.
>
> Nenhum classificador foi construído. `PERGUNTAS_DO_UNIVERSO` não foi tocado.

Para refazer a medição:

```bash
py provas/censo_corpus_rotulado_admission.py
py -m unittest tests.test_censo_corpus_rotulado_admission
```

---

## 0 · OS CRITÉRIOS, ESCRITOS ANTES DA CONTAGEM

Estão em código, em `provas/censo_corpus_rotulado_admission.py :: CRITERIOS`,
e presos um a um pelos testes. Cada número traz a razão ao lado.

| uso | positivos | negativos | publicadores | mais |
|---|---:|---:|---:|---|
| **SANITY** | ≥ 3 | ≥ 3 | ≥ 2 | — |
| **EVALUATION** | ≥ 10 | ≥ 10 | ≥ 3 | holdout de publicador obrigatório |
| **TRAINING** | ≥ 100 | ≥ 100 | ≥ 5 | ≥ 2 famílias de documento, e cumprir EVALUATION |

**Por que 3 publicadores para avaliar.** É o mínimo em que tirar um ainda deixa
dois. Com dois, tirar um deixa um — e **um publicador não é uma distribuição**.
A lição é a de T2: uma regra ajustada em 10 positivos de 3 publicadores cobriu o
treino 9/9 e acertou **0/10** no publicador que não viu.

    UM CRITÉRIO ESCRITO DEPOIS DA CONTAGEM
    É O ALVO DESENHADO À VOLTA DA FLECHA.

---

## 1 · `LABEL_SOURCES_FOUND = 5`

| origem | itens | quem rotulou | autoridade | serve de gabarito? |
|---|---:|---|---|---|
| `data/samples/LIVRO-DE-DECISOES.json` | 813 | `admissao.decidir()`, regra v3 | `KEYWORD_DERIVED` | **NÃO** |
| `provas/a_regra_de_t2.py :: GABARITO` | 46 | pessoa, lendo a abertura de cada documento | `DOCUMENT_SELF_DECLARED` | **SIM** |
| `sources.generated.json :: MASTER_ITALIANO` | 54 | pessoa, ao abrir a ficha da **fonte** | `SOURCE_CONTRACT_DECLARED` | **NÃO** |
| `IT-SOURCE-SAMPLES/*/MANIFEST.json` | 26 ficheiros | herdado do `SOURCE_ID` da pasta | `SOURCE_CONTRACT_DECLARED` | **NÃO** |
| `data/derivados/REGISTO-DE-ARTEFATOS.json` | 43 | ninguém — **não há campo de universo** | `UNKNOWN` | **NÃO** |

### Por que a ficha da fonte não serve de gabarito

Porque já foi medido que ela discorda do documento:

- a **ARPAV** publica `Meteo Veneto` (T2) **e** `U.O. Fitosanitario — VITE` (T3);
- a ficha `IT-T3-008` declara **T3** e o `Giornaliero Meteorologico` dessa fonte
  é previsão do tempo pura;
- a ficha `IT-T5-003` declara **T5 — Preço e mercado** e os dois ficheiros são
  *«Bilancio Fitosanitario — Olivo»*;
- a ficha `IT-T7-002` declara **T7 — Ciência e ensaio** e o ficheiro é
  `ELENCO-OP-AOP`, uma lista administrativa de organizações de produtores.

```
TERRITÓRIO DA FONTE ≠ UNIVERSO DO DOCUMENTO.
```

### Um achado de vocabulário, e é sério

A palavra `UNIVERSE`/`UNIVERSO` aparece em quatro sentidos diferentes nesta
árvore, e nenhum deles é o mesmo:

| ficheiro | o que `UNIVERSE` significa lá |
|---|---|
| `LIVRO-DE-DECISOES.json` | o universo `T2..T13` da Admission |
| `IT-CIENCIA/IT-CIENCIA-UNIVERSO-V1.json` | uma lista de **pessoas** (investigadores) |
| `IT-T4-001-enriquecimento-validado.json` | `REGULATORY_LIVE_ADMIN`, estado de registo de **produto** |
| `ES-X-VOICE-SCIENCE.json` | **contagens** de canais e instituições |

Quem procurar rótulos por nome de campo encontra 405 ocorrências de `UNIVERSE` e
**zero** rótulos temáticos de documento. Registado e **não corrigido** — não era
esta missão.

---

## 2 · O LIVRO DE DECISÕES — 813 decisões, zero gabarito

```
TOTAL_DECISIONS   813
UNIQUE_ITEMS       44
POR UNIVERSO      T7 331 · T4 326 · T9 156
POR RESULTADO     NAO_SEI 597 · NAO_SE_APLICA 142 · NAO 38 · SIM 36
```

```
DECISIONS_PRODUCED_BY_CURRENT_KEYWORDS   = 813   (TODAS)
DECISIONS_WITH_INDEPENDENT_GROUND_TRUTH  = 0
LABEL_LEAKAGE (rótulo feito com a palavra a avaliar)  = 36
SELF_CONFIRMING_LABEL (idem, por exclusão)            = 38
```

Os 36 `SIM` trazem, na evidência, **as palavras que os produziram**. Usá-los para
provar que um mecanismo baseado nessas palavras funciona é pôr duas cópias da
mesma regra a concordarem uma com a outra.

    UM CLASSIFICADOR TREINADO NAS RESPOSTAS DO ANTERIOR
    NÃO O SUBSTITUI: CONFIRMA-O.

**Para que o livro serve:** comparação, diagnóstico, e *hard-negative mining* —
os 597 `NAO_SEI` são exatamente onde o vocabulário não chegou, e isso é uma
lista de casos difíceis pronta a usar. **Para que não serve:** gabarito.

---

## 3 · MULTIRRÓTULO — decisões múltiplas não são multirrótulo

```
ITEMS_WITH_1_UNIVERSE        43
ITEMS_WITH_2_PLUS_UNIVERSES   1
MAX_UNIVERSES_PER_ITEM        3

MULTIPLE_DECISIONS_ONLY       1
MULTILABEL_CONFIRMED          0
```

Há **um** item com decisões em T4, T7 e T9. As três são `NAO_SEI` e
`NAO_SE_APLICA` — que **não são rótulos**, são confissões de que a porta não
soube. Zero itens têm dois `SIM`.

A missão anterior provou que a arquitetura **permite** multirrótulo
(`(item, T3) = SIM` e `(item, T4) = SIM` no mesmo item). Isto aqui é outra coisa:
o corpus real ainda **não exerce** essa permissão.

```
PERMITIDO ≠ EXERCIDO.
TER TRÊS DECISÕES REGISTADAS NÃO PROVA QUE TRÊS ESTÃO CERTAS.
```

---

## 4 · O ÚNICO CORPUS COM CORPO, RÓTULO E RAZÃO

O gabarito de T2, 46 documentos. Cada um responde às sete perguntas de
proveniência (`ITEM_ID · SOURCE_ID · CONTENT_PATH · LABEL · LABEL_AUTHORITY ·
LABEL_REASON · LABEL_EVIDENCE`), e **nenhum** está sem corpo no disco.

```
CLEAR_POSITIVE   10
CLEAR_NEGATIVE   33
AMBIGUOUS         3     (ARIF Puglia — não arredondados)
INSUFFICIENT_EVIDENCE  0
```

**13 publicadores:** ARPAV 13 · Regione Campania 7 · Regione Lazio 5 ·
Fondazione Edmund Mach 4 · ARIF Puglia 3 · ARPAE 2 · APOL Lecce 2 · Regione
Piemonte 2 · Giornate Fitopatologiche 2 · Ministero della Salute 2 · SIAS 1 ·
Terre dell'Etruria 1 · Agrios 1.

**3 famílias de documento:** texto derivado de PDF 43 · HTML 2 · CSV 1.
**1 país** (IT) · **1 língua** (it).

### Um defeito que esta própria prova teve, e com que deu verde

A primeira versão procurava o `SOURCE_ID` no **caminho**. Os 43 textos derivados
chamam-se `RAW-<sha>.txt` e não carregam fonte no nome — portanto 43 dos 46 itens
caíram num balde chamado `NAO SEI`, e `PUBLISHER_HOLDOUT_POSSIBLE` respondeu
**YES** porque `NAO SEI` contava como **um publicador**.

    UM BALDE DE DESCONHECIDOS CONTADO COMO CATEGORIA
    É DIVERSIDADE FABRICADA.

Corrigido: o publicador vem agora da **linhagem** (o registo de artefatos diz de
que pai cada derivado nasceu, e o caminho do pai diz a fonte), e `NAO SEI` não
conta como publicador em lado nenhum. `tests/test_censo_corpus_rotulado_admission.py`
tem o caso que reprova a versão antiga.

---

## 5 · O VEREDICTO, POR UNIVERSO

| universo | POS | NEG | AMB | publicadores | famílias | SANITY | EVAL | TRAIN | veredicto |
|---|---:|---:|---:|---:|---:|:--:|:--:|:--:|:--:|
| **T2** | 10 | 33 | 3 | 13 | 3 | YES | YES | NO | **B** |
| **T3** | 0 | 0 | 0 | 0 | 0 | NO | NO | NO | **D** |
| **T4** | 0 | 0 | 0 | 0 | 0 | NO | NO | NO | **D** |
| **T7** | 0 | 0 | 0 | 0 | 0 | NO | NO | NO | **D** |
| **T9** | 0 | 0 | 0 | 0 | 0 | NO | NO | NO | **D** |
| T1 · T5 · T10 · T11 · T12 · T13 | 0 | 0 | 0 | 0 | 0 | NO | NO | NO | **D** |

T3, T4, T7 e T9 **têm** regra na Admission e **não têm** um único item com rótulo
independente e corpo. As 813 decisões que existem sobre eles vieram da própria
regra que se quer avaliar.

```
PUBLISHER_HOLDOUT_POSSIBLE = YES   (T2: ARPAE · ARPAV · SIAS no lado positivo)
SOURCE_HOLDOUT_POSSIBLE    = YES   (IT-T2-001 · IT-T2-002 · IT-T2-004)
COUNTRY_HOLDOUT_POSSIBLE   = NO    (100% IT)
LANGUAGE_HOLDOUT_POSSIBLE  = NO    (100% it)
```

### A ressalva que a letra `B` não mostra

As candidatas `A3` e `A5` da missão anterior **nasceram de olhar para este
corpus**. Para elas, o gabarito é treino, não teste.

    UM CONJUNTO SÓ É INDEPENDENTE DE QUEM NÃO OLHOU PARA ELE.

Para um mecanismo que ninguém ajustou aqui, continua a servir de avaliação.

### A partição que a próxima missão deve usar, se avaliar

Não foi materializada — a missão proíbe. Mas a regra mínima fica escrita:

```
TEST  = um publicador RETIDO por inteiro (ARPAE, ou SIAS, ou ARPAV)
        nunca «outros documentos dos mesmos publicadores»
TRAIN/VALIDATION = os restantes
```

---

## 6 · A LACUNA, MEDIDA — e de onde poderia vir sem coletar nada

Documentos **já nesta árvore** que abrem declarando o seu próprio género:

| universo | documentos | publicadores |
|---|---:|---:|
| **T3** | **27** | **9** |
| T2 | 9 | 2 |
| T4 | 1 | 1 |

**T3 é alcançável sem coletar nada.** Há 27 documentos que abrem com
*«Bollettino Fitosanitario»*, *«Servizio Fitosanitario … Difesa Integrata»* ou
*«Difesa delle Colture»*, de 9 publicadores distintos. Falta a passagem de
rotulagem — que é trabalho de uma pessoa a ler, não de uma máquina a adivinhar.

Para levar **um** universo de `D` a `B`:

```
NEEDED_POSITIVES   10   com corpo e razão escrita
NEEDED_NEGATIVES   10
NEEDED_PUBLISHERS   3   no lado positivo
NEEDED_AMBIGUOUS    0   ambíguo não é requisito: é resultado
```

Para levar **T2** de `B` a `A`:

```
positivos  +90      negativos  +67      publicadores positivos  +2
NEEDED_LANGUAGES  ≥ 1 além de `it`
```

**Isto não é um pedido de coleta.** É a conta que a próxima missão precisa para
escolher entre rotular o que há, coletar material novo, pedir revisão humana, ou
combinar os três.

---

## 7 · O QUE ESTE CENSO NÃO FEZ

Nenhum modelo treinado. Nenhum *embedding*. Nenhum LLM a rotular corpus. Nenhum
prompt-classifier. Nenhum *benchmark* de fornecedor. A Admission não mudou,
`PERGUNTAS_DO_UNIVERSO` não mudou, T2 continua `T2_RULE_IMPLEMENTED = NO`.

    AINDA NÃO SABÍAMOS SE HAVIA CHÃO PARA MEDIR UM.
    AGORA SABEMOS: HÁ PARA UM UNIVERSO, E SÓ PARA AVALIAR.


---

## 8 · ATUALIZAÇÃO T3 — 11/09/2026

> **Isto não apaga nada acima.** A secção 1 continua a dizer que, naquele dia,
> T3 não tinha um único rótulo independente com corpo. Isso era verdade. Deixou
> de ser, e a diferença entre as duas coisas é o trabalho de quatro missões.
>
> Missão: `C-FECHA-GABARITO-T3-E-RECALCULA-CENSO-V1`

### O que mudou

```
T3_OLD_VERDICT = D
T3_NEW_VERDICT = B

T3_SANITY_SUFFICIENT      = YES
T3_EVALUATION_SUFFICIENT  = YES
T3_TRAINING_SUFFICIENT    = NO
```

### De onde veio o rótulo

Uma pessoa leu 53 documentos e respondeu. Depois leu outra vez: 32 em modo de
confirmação, com a resposta à vista e a razão por escrever, e 21 **às cegas**,
sem ver a primeira resposta e com o documento inteiro disponível.

```
REVIEW_A              53 respostas
QUALITY_GATE (A2)     53 respostas · 32 confirmações + 21 releituras cegas
```

Não houve segundo revisor independente, e o gabarito diz isso de si mesmo. É a
mesma pessoa em segunda passagem.

### O fecho

```
EVAL_ELIGIBLE   36     CONFIRMED_SIM 14 · CONFIRMED_NAO 22
UNRESOLVED      11     as duas leituras não bateram
EVIDENCE_GAP     6     as duas disseram «não dá para saber»
AMBIGUOUS        0
```

Onde as duas leituras divergiram, **não há rótulo**. Não se escolheu A, não se
escolheu A2, não se tirou maioria de duas respostas.

```
A != A2  ->  UNRESOLVED, E MAIS NADA.
EVIDÊNCIA INSUFICIENTE  !=  NÃO
```

Os 17 que ficaram de fora estão guardados no mesmo artefato, em
`EXCLUDED_FROM_EVALUATION`, com as duas respostas e a razão. Não são gabarito,
e o ficheiro diz isso na cara.

### O gabarito

```
data/samples/T3-GROUND-TRUTH-EVAL-V1.json
sintonia.t3-ground-truth-eval/1
LABEL_AUTHORITY = HUMAN_VERIFIED   ·   AUTO_LABELS_ASSIGNED = 0
gerado por provas/fechar_ground_truth_t3.py
```

É a primeira origem de rótulo desta árvore que não é herdada da ficha da fonte
nem derivada das palavras que a Admission usa hoje.

### O portão, critério a critério

Os limiares são os da secção 2 desta fotografia, escritos antes de qualquer
contagem e **não mexidos** nesta missão.

| critério | medido | |
|---|---|---|
| positivos ≥ 10 | 11 | passa |
| negativos ≥ 10 | 20 | passa |
| publicadores no lado positivo ≥ 3 | 6 | passa |
| holdout de publicador com as duas classes | YES | passa |
| corpo recuperável | 31/31 | passa |
| razão estruturada | 31/31 | passa |
| evidência atestada | 31/31 | passa |

### As três ressalvas

**1 · A margem é de um.** O critério pede 10 positivos independentes e há 11.
Um item que se descubra mal rotulado derruba o veredicto.

**2 · Os 14 positivos são 11 observações.** Quatro deles são edições seguidas do
mesmo boletim regional e partilham a abertura quase inteira.

```
QUATRO CÓPIAS DO MESMO BOLETIM NÃO SÃO QUATRO PROVAS.
```

O portão conta **grupos**, não ficheiros. Os limiares não mudaram; mudou o que
conta como um. Nenhum par quase-duplicado atravessa publicadores, portanto uma
divisão por publicador nunca põe duas cópias do mesmo boletim em lados opostos.

**3 · O idioma não foi medido em todos.** 17 dos 36 não resolvem `LANGUAGE` e um
está em inglês. O país é `IT` em 36/36, e é isso — e só isso — que o escopo
afirma.

```
EVALUATION_SCOPE = ITALIAN_AGRO_INSTITUTIONAL_CORPUS
```

Não autoriza afirmar França, Espanha nem EAME.

### Diversidade e holdout, medidos

```
DOCUMENTS            36   ->  GRUPOS INDEPENDENTES 31
PUBLICATION_SERIES   27       PUBLISHERS 14       SOURCES 11
POSITIVE_PUBLISHERS   6       NEGATIVE_PUBLISHERS  9

PUBLISHER_HOLDOUT_WITH_BOTH_CLASSES_POSSIBLE = YES
SOURCE_HOLDOUT_WITH_BOTH_CLASSES_POSSIBLE    = YES
COUNTRY_HOLDOUT_POSSIBLE                     = NO
LANGUAGE_HOLDOUT_POSSIBLE                    = NO
```

`NAO SEI` não conta como fonte: 16 dos 36 não resolvem `SOURCE_ID` e ficam fora
de toda a contagem de diversidade.

### O que esta atualização não fez

Nenhum classificador construído. Nenhum modelo escolhido. Nenhum *benchmark*.
Nenhum *embedding*. A Admission não mudou, `PERGUNTAS_DO_UNIVERSO` não mudou,
nenhuma regra de T3 entrou em runtime. Nada foi recoletado.

```
CLASSIFIER_BUILT = NO   ·   ADMISSION_CHANGED = NO   ·   RECOLLECTION = NO
```

    ANTES: T3 NÃO TINHA UM ÚNICO RÓTULO INDEPENDENTE COM CORPO.
    AGORA: TEM 36, E 11 DELES SÃO POSITIVOS INDEPENDENTES.
    CONTINUA SEM CHÃO PARA TREINAR.
