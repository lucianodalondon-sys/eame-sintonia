# O SAMPLING FRAME DE T3 — as 46 são a população certa?

> **A pergunta:** as 46 fichas do pacote formam uma amostra adequada para
> **avaliar** T3, ou é preciso ampliar antes de alguém rotular?
>
> **A resposta medida:**
>
> ```
> CURRENT_46_ADEQUATE_FOR_GENERAL_T3_EVALUATION = NO
> CURRENT_46_ROLE = B. PARTIAL_T3_EVAL_SLICE
> ADDITIONAL_ITEMS_NEEDED = 7
> SELECTION_METHOD = CENSO, não amostra
> ```
>
> As 46 **não se apagam**. São um subconjunto do frame completo, e a revisão
> delas continua válida quando os outros 7 entrarem.
>
> ```
> HUMAN_LABELS_ADDED = 0     MACHINE_LABELS_ADDED = 0
> ```

> **ESTADO POSTERIOR.** O pacote foi regenerado sobre esta população: já tem as
> **53** fichas, as 46 reaproveitadas e as 7 acrescentadas, e `ISTAT`, `AGEA` e
> `ISMEA` deixaram de estar ausentes. Ver
> [`T3-REVIEW-PACKET-V1.md`](T3-REVIEW-PACKET-V1.md). O que está escrito abaixo é
> a **medição que motivou** essa regeneração, e fica como estava.

Para refazer:

```bash
py provas/amostragem_neutra_t3.py
py -m unittest tests.test_amostragem_neutra_t3
```

---

## 1 · DE ONDE VIERAM AS 46 — lido do código, não assumido

```
CURRENT_PACKET_POPULATION_SOURCE   censo._gabarito_t2()
UNIVERSOS_QUE_O_GABARITO_ROTULA    ['T2']
CURRENT_46_SELECTED_FOR_T2         YES
CURRENT_46_SELECTED_FOR_T3         NO
```

`provas/pacote_de_revisao_t3.py :: construir` chama `censo._gabarito_t2()`. Esse
gabarito foi montado para responder *«este documento pertence a T2?»*. Os
negativos dele são **«não é tempo»** — nunca *«uma amostra do que a porta
encontra»*.

A missão anterior corrigiu o vazamento do **amostrador** ao nível da
pré-seleção: os 27 candidatos deixaram de ser apresentados sozinhos. O degrau de
baixo ficou por examinar, e é este.

```
LEAKAGE NO ROTULADOR   quem decide o rótulo        (§52)
LEAKAGE NO AMOSTRADOR  quem decide quem entra      (§53)
LEAKAGE NA POPULAÇÃO   de que pergunta veio a lista inteira   ← esta missão
```

    HUMAN LABEL DOES NOT REPAIR A BIASED SAMPLING FRAME.

### Um defeito desta própria prova, e ele quase passou

A primeira versão respondia `CURRENT_46_SELECTED_FOR_T2 = NO` — o **contrário**
da verdade. Ela procurava uma frase no ficheiro de T2, e a frase que eu procurava
não era a frase que lá estava.

    PROCURAR UMA FRASE QUE EU IMAGINEI NÃO É LER O CÓDIGO.

Corrigido: a resposta vem agora dos **rótulos que o gabarito produz**. Se todos
falam de um universo, foi para esse universo que a população foi montada.

---

## 2 · O SAMPLING FRAME · inclusão não temática

A regra de inclusão usa **só** existência, extensão e legibilidade. É proibido, e
está preso por teste, selecionar por palavra de T2 ou T3, nome de ficheiro,
território da ficha da fonte, decisão de `PERGUNTAS_DO_UNIVERSO` ou resultado do
gabarito de T2.

```
ficheiros de documento              63
DOCUMENTOS UNICOS (por bytes)       54
em mais de um caminho                9
ALL_REVIEWABLE_DOCUMENTS            53
sem corpo legivel                    1   (um .ods — IT-T7-002)
```

**A unidade é o documento, não o caminho.** Nove documentos vivem em dois sítios
(a captura e a amostra) e contam **uma** vez. Contá-los duas vezes inflacionaria
a diversidade sem acrescentar uma evidência.

```
DERIVED_ITEMS            43
UNIQUE_PARENT_DOCUMENTS  43   (zero pais partilhados)
brutos ja legiveis       10
```

---

## 3 · CARACTERIZAÇÃO — e nenhuma destas é um rótulo

| | |
|---|---|
| `PUBLISHERS` | **17** |
| `SOURCE_IDS` | 13 resolvidos · 27 documentos sem fonte |
| `DOCUMENT_FAMILIES` | PDF 43 · HTML 5 · sem extensão 3 · CSV 2 |
| `COUNTRIES` | IT 53 |
| `LANGUAGES` | `it` onde o manifesto declara · `NAO SEI` no resto |
| `TIME_PERIODS` | agosto–setembro 2026 no material datado |

Distribuição por publicador: ARPAV 13 · Campania 7 · Lazio 5 · Fondazione Edmund
Mach 4 · Piemonte 4 · ARIF 3 · SIAS 2 · APOL 2 · Ministero della Salute 2 · AGEA
2 · ARPAE 2 · Giornate Fitopatologiche 2 · Terre dell'Etruria 1 · Molise 1 ·
ISTAT 1 · Agrios 1 · ISMEA 1.

---

## 4 · 46 vs POPULAÇÃO REVISÁVEL

```
CURRENT_PACKET         46
TOTAL_REVIEWABLE       53
OVERLAP                46
NOT_IN_CURRENT_PACKET   7
COBERTURA = 46/53 = 86%
```

**Mas 86% é a cobertura contada em documentos.** Contada por publicador é
**14/17**, e três publicadores estão **inteiramente ausentes** do pacote:

| publicador | o que publica | ficheiro |
|---|---|---|
| **ISTAT** | estatística de colheitas | `ISTAT_101_1015_COLTIVAZIONI_2_2025.csv` |
| **AGEA** | subsídio | `46622`, `46647` |
| **ISMEA** | preço e mercado | `91515` |

E mais quatro documentos de publicadores que o pacote conhece mas por outras
peças: a segunda janela do SIAS e duas páginas HTML do Piemonte.

### O que ficou de fora tem uma forma

```
familias DENTRO do pacote   PDF 43 · HTML 2 · CSV 1
familias FORA do pacote     sem extensao 3 · HTML 3 · CSV 1
```

O gabarito de T2 procurava *«documentos sobre tempo»* e *«documentos que
claramente não são tempo»*. Na prática os negativos dele saíram **todos da mesma
prateleira: boletins**. O que ficou de fora é o material **tabular e
administrativo** — preço, subsídio, estatística.

Isto não é um rótulo. É a **forma do que não foi apanhado**. E importa para T3
precisamente porque um classificador de praga precisa de negativos que não sejam
só boletins de tempo.

---

## 5 · SÉRIES DE PUBLICAÇÃO — edições não são evidências independentes

```
46 documentos  ->  34 séries de publicação
```

As maiores: 4 zonas do mesmo boletim ARPAV · 4 edições do mesmo boletim da
Fondazione Edmund Mach · 2 do Notiziario da ARIF · 2 do boletim da APOL.

    QUATRO ZONAS DO MESMO BOLETIM SÃO QUATRO DOCUMENTOS
    E QUASE UMA SÓ EVIDÊNCIA.

Não invalida nada — mas quem contar «46» como 46 observações independentes vai
achar o corpus mais forte do que ele é.

---

## 6 · RED TEAM — dez ataques, com número

| ataque | estado | prova |
|---|---|---|
| 1 · corpus inteiro herdado de T2 | **CONFIRMADO** | 46 de 53, e todos entraram pela pergunta de T2 |
| 2 · o que ficou de fora sai da mesma prateleira | **CONFIRMADO** | 7 documentos, 5 publicadores, nenhum é boletim |
| 3 · pasta tratada como publicador | CORRIGIDO | os 14 da pasta VPN resolvem-se em 4 publicadores |
| 4 · `UNKNOWN` tratado como grupo real | NÃO OCORRE | 0 revisáveis sem publicador |
| 5 · nome do ficheiro usado na seleção | NÃO OCORRE | preso por teste sobre o código de `sampling_frame()` |
| 6 · território da fonte usado na seleção | NÃO OCORRE | `SOURCE_ID` é característica, não filtro |
| 7 · decisão antiga usada na seleção | NÃO OCORRE | o livro de decisões não é lido por esta prova |
| 8 · mesmo publicador dos dois lados do holdout | **ESTRUTURALMENTE EVITÁVEL** | 17 de 17 podem ser retidos deixando ≥ 10. Se sobra positivo **e** negativo de T3 é **desconhecido até haver rótulos** |
| 9 · o mesmo documento contado duas vezes | EVITADO | 9 documentos em dois caminhos contam uma vez |
| 10 · diversos por contagem, poucos por publicação | **CONFIRMADO E MEDIDO** | 46 documentos, 34 séries |

O ataque 8 merece a frase: **estrutura não é cobertura.** Poder reter um
publicador não garante que sobra material dos dois lados — isso só se sabe
depois da rotulagem.

---

## 7 · GRUPOS E HOLDOUT

O estudo externo já fechado (`GroupKFold` do scikit-learn, *Splits and data
leakage* da AWS, `samplingKeyColumnName` do ML.NET) diz a mesma coisa: o grupo
correlacionado não pode atravessar a partição.

```
PUBLISHER_GROUPING_POSSIBLE = YES       17 grupos, nenhum «NAO SEI»
SOURCE_GROUPING_POSSIBLE    = PARCIAL   13 fontes resolvidas, 27 documentos sem fonte
PUBLISHER_HOLDOUT_POSSIBLE  = YES
maior publicador            ARPAV, 13 de 53
```

A regra que fica escrita para quem partir o conjunto:

```
SAME_PUBLISHER NÃO PODE APARECER EM TRAIN E EM TEST
quando a avaliação pretende medir generalização para publicador novo.
```

Nenhum split foi materializado. É cedo.

---

## 8 · O PORTÃO

| critério | resultado |
|---|:--:|
| `COBRE_A_POPULACAO` — o que fica de fora é vazio, ou excluído por critério não temático declarado | **NO** — 7 de fora, e com forma |
| `GRUPO_NAO_VAZA` — dá para reter um publicador inteiro | **YES** |
| `SELECAO_NAO_TEMATICA` — nada entrou por palavra, nome, ficha ou decisão | **NO** — a população veio do gabarito de T2 |

```
CURRENT_46_ADEQUATE_FOR_GENERAL_T3_EVALUATION = NO
CURRENT_46_ROLE = B. PARTIAL_T3_EVAL_SLICE
```

### A correção é barata, e não é amostrar melhor

```
SELECTION_METHOD = CENSO, NÃO AMOSTRA
```

Com **53** documentos revisáveis no total, escolher um subconjunto introduz viés
**sem poupar trabalho nenhum**. A expansão neutra é simplesmente: **incluir
todos**. Sem regra de amostragem não há regra de amostragem para enviesar.

```
ADDITIONAL_ITEMS_NEEDED = 7
```

E fica declarado o único excluído por critério não temático: o `.ods` do
`IT-T7-002`, que não tem corpo legível nesta árvore. Não foi escondido, e a
razão não tem nada a ver com assunto.

---

## 9 · O LIMITE QUE NEM O CENSO COMPLETO RESOLVE

Mesmo com os 53, o frame continua a ser:

```
1 país      IT
1 língua    it
53 documentos, 34 séries de publicação
```

O atlas declara **54 fontes italianas** e a Admission encontrará também França e
Espanha. Portanto, mesmo perfeito, este frame avalia T3 **dentro de material
agro-institucional italiano** — e não autoriza afirmar generalização para fora
disso. Está escrito aqui para ninguém se enganar depois.
