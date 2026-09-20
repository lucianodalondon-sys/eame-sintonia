# SEGUNDA RODADA INCREMENTAL — 17 novos, 1 utilizável, 0 crossings

> **Missão:** `C-INT-PILOT-SALA-V2`
> **Natureza:** rodada incremental **READ-ONLY** sobre o delta da
> BIG COLLECTION `BCR-2026-09-20`.
> **Medição:** `provas/o_piloto_da_sala.py` · `PIPELINE_VERSION = 2`
> **Artefato do delta:** `data/derivados/O-PILOTO-DA-SALA-R2-DELTA.json`

---

## A RESPOSTA, ANTES DA PROVA

```text
SALA_TOTAL_CURRENT        46
PREVIOUSLY_PROCESSED      29
NEW_UNPROCESSED_ITEMS     17     medido por identidade, não por subtração

NEW_USABLE                 1
NEW_WEAK                   5
NEW_INSUFFICIENT          11

NEW_FINDINGS               0
NEW_CROSSINGS              0     ← zero tentados, não zero aprovados
NEW_WATCH_SIGNALS          0
NEW_OPPORTUNITY_CANDIDATES 0
```

**A Sala cresceu 59% e a Intelligence não avançou um passo.** E a razão não é
o gate: é que **nenhum dos 17 pertence à família que sabe responder** à
pergunta agronômica.

```text
NOVOS POR UNIVERSO   T5 = 13   T7 = 3   T9 = 1   T3 = 0
```

`IT-T3` — boletins fitossanitários, a única família que traz cultura, praga,
limiar e substância — **recebeu zero itens nesta Big Collection.**

---

## A · O DELTA MEDIDO POR IDENTIDADE, NÃO POR ARITMÉTICA

O enunciado dizia «≈17, mas medir». Medi — e a medição mudou a ferramenta.

### `--desde` era um filtro, e filtro não é checkpoint

A 1ª rodada entregou incrementalidade por data (`--desde AAAA-MM-DD`). Isso
responde *«o que pousou depois de quando?»*, que **não é** a pergunta da
incrementalidade:

```text
FILTRO POR TEMPO   !=   CHECKPOINT POR IDENTIDADE
```

As duas só coincidem enquanto ninguém pousar um item com carimbo antigo e
ninguém correr o piloto duas vezes no mesmo dia. Nesta rodada passou a existir
`--desde-artefato`, que subtrai por `(RUN_ID, ORDEM)` — a chave que a própria
migration 031 declara como endereço da linha.

```text
SALA_TOTAL_CURRENT              46
IDENTIDADES JÁ PROCESSADAS      29
AINDA PRESENTES NA SALA         29
PROCESSADOS QUE SUMIRAM          0
NEW_UNPROCESSED_ITEMS           17
```

⚠️ **`PROCESSADOS_QUE_SUMIRAM = 0` é uma medição, não uma suposição.** Um item
já processado que desaparecesse da Sala é um facto sobre a Sala — e um filtro
por data nunca o veria, porque ele sai do recorte por construção.

### A chave de idempotência é o par, não o item

```text
(RUN_ID, ORDEM)  +  PIPELINE_VERSION
```

Reprocessar com a **mesma** versão é ruído e sai vazio. Mudar a versão obriga a
reprocessar, porque a resposta de v1 não é a resposta de v2 — a régua mudou.

Isto **funcionou na primeira tentativa, e ao contrário do esperado**: ao apontar
o checkpoint para o artefato da 1ª rodada, o processo detetou
`PIPELINE_VERSION: None → 2` e **reprocessou os 46 em vez dos 17**, avisando no
`stderr`. Comportamento correto, e não o que eu queria naquele instante — o que
é o sinal de que o mecanismo não está a ser complacente.

---

## B · O ACHADO QUE MUDA A LEITURA DA BIG COLLECTION

**Dos 17 itens novos, 12 trazem texto que já estava na Sala.**

```text
NEW_UNPROCESSED_ITEMS         17
DELTA_REDUNDANTE_VS_SALA      12      ← re-observação de texto já presente
TEXTO GENUINAMENTE NOVO        5
```

| `SOURCE_ID` | obs | o texto já estava na Sala? |
|---|---|---|
| `IT-T5-015`, `IT-T5-024`, `IT-T5-025`, `IT-T5-027` | 289, 298, 299, 301 | **sim** — mesma fonte, nova captura |
| `IT-T5-028`, `IT-T5-030`, `IT-T5-033` | 302, 304, 305 | **sim** |
| `IT-T5-034`, `IT-T5-035`, `IT-T5-036` | 306, 307, 308 | **sim** — e os três são o mesmo documento |
| `IT-T7-013`, `IT-T9-011` | 309, 313 | **sim** |
| `IT-T5-017` | 291 | não — FAQ do repositório FLORE |
| `IT-T5-039` | 334 | não — «Lezioni ed esami», Agraria Federico II |
| `IT-T5-049` | 335 | não — avisos de exames, Agraria Catania |
| `IT-T7-033` | 339 | não — e-learning do Chianti Classico |
| `IT-T7-041` | 341 | não — Settimana della Bonifica, Consorzio Romagna |

### E a medição da dependência teve de mudar de denominador

Vistos **só entre si**, os 17 novos pareciam 15 textos distintos — um bom
número. Medidos **contra a Sala inteira**, são 5.

```text
NOVO NA FILA   !=   NOVO COMO EVIDÊNCIA
```

Um item novo que repete o texto de um item já processado é dependente, e olhar
só para o delta não o vê: o gémeo dele ficou fora do recorte. A ferramenta
passou a medir impressão contra os 46, não contra os 17 — **a incrementalidade
aplica-se ao processamento, nunca à contagem de independência.**

```text
TEXTOS DISTINTOS NA SALA     31   de 46 itens
```

Quinze dos quarenta e seis itens da Sala são cópias de outros quinze.

### O único USABLE novo... já tinha sido processado

`IT-T9-011` (Koppert, ácaros predadores, densidade agro 34) é o único item do
delta classificado `USABLE_FOR_INTELLIGENCE`. **E o texto dele é byte-a-byte
igual ao `IT-T9-011` que a 1ª rodada já leu.**

```text
NEW_USABLE                            1
NEW_USABLE COM TEXTO INÉDITO          0
```

Os cinco itens com texto genuinamente novo classificam-se: 1 `WEAK`
(`IT-T5-049`) e 4 `INSUFFICIENT`. São FAQ de repositório institucional,
calendários de exames, um curso de e-learning sobre vinho e uma semana temática
de consórcio de irrigação.

**Esta Big Collection não trouxe evidência agronômica nova.**

---

## C · CROP — o gargalo, agora contado

A 1ª rodada narrou o problema. Esta contou-o, com três estados que são mesmo
três:

```text
                        SALA INTEIRA (46)      DELTA (17)
ITEMS_EXPECTING_CROP            5                   0
ITEMS_WITH_CROP                 0                   0
ITEMS_MISSING_CROP              5                   0
CROP_LOST_IN_DERIVATION         5                   0
```

### `LOST_IN_DERIVATION` não é o mesmo que ausência

```text
NOT_EXPECTED         a família não devia trazer cultura (edital, FAQ)
ABSENT_IN_TEXT       o documento não fala de cultura nenhuma
LOST_IN_DERIVATION   a cultura ESTÁ no texto e não tem campo onde pousar
```

Os cinco itens `IT-T3` estão todos no terceiro estado:

| item | culturas presentes no texto |
|---|---|
| `IT-T3-002` obs 7 e 26 | ACTINIDIA, AGRUMI, ARANCIO, CILIEGIO, FRAGOLA, MELO, NOCCIOLO, OLIVE, OLIVO |
| `IT-T3-008` obs 9 e 36 | AGRUMI, ARANCIO, GRANO, OLIVE, OLIVO, PERO, UVA, VITE |
| `IT-T3-010` obs 1 | GRANO, NOCCIOLO, OLIVE, OLIVO |

```text
PERDA = 5 / 5 = 100%
```

> **O DADO CHEGOU. A ESTRUTURA NÃO.**
> A cultura foi colhida, preservada e sobreviveu até ao texto da Sala. O que
> não existe é campo no contrato READY de 19 campos onde ela possa pousar.

⚠️ **Isto não foi corrigido, e a correção não é minha.** A sonda `SONDA_CROP`
existe **só para contar a perda** — encontrar a palavra «OLIVO» no corpo do
texto não promove nada a `CROP`. Usá-la para fechar um join seria fabricar a
chave, que é o ataque que o gate existe para barrar.

---

## D · O DEFEITO QUE ESTA RODADA ENCONTROU NA RODADA ANTERIOR

**`D-01` — o gate de autorização falha fechado sempre, e isso não é o mesmo que
saber decidir.**

A 1ª rodada declarou, no red team `RT-5`, que o gate «distingue três estados».
**Medido agora: não distingue.**

```text
cruzar() usa SONDA_CROP ?    False
cruzar() usa medir_crop() ?  False
CROSSING_STATE possíveis:    {'NOT_POSSIBLE'}
```

Teste com três itens sintéticos que só diferem na cultura:

| cenário | veredito |
|---|---|
| sem cultura no texto | `NOT_POSSIBLE` |
| **com `MELO` no texto** (146 usos ADAMA autorizados) | `NOT_POSSIBLE` |
| **com `OLIVO` no texto** (1 uso ADAMA autorizado) | `NOT_POSSIBLE` |

```text
RECUSAR SEMPRE PELO MOTIVO CERTO   !=   SABER DISTINGUIR
```

O comportamento **está correto** — INT-LAW-037: sem join key não há crossing —
mas a afirmação da 1ª rodada era mais generosa do que o código. A distinção
autorizado/não-autorizado **está por construir**, e só faz sentido construí-la
quando `CROP` chegar como campo.

Corrigido no `docstring` de `cruzar()`, que agora declara a limitação em vez de
a esconder. A régua da casa aplica-se a mim: *implementação não pode cumprir →
defeito registado, não lei relaxada.*

---

## E · CRUZAMENTOS E CLIMA

```text
NEW_CROSSINGS_TENTADOS      0
NEW_CROSSINGS_POSSIVEIS     0
NEW_WATCH_SIGNALS           0
```

**Zero tentados, e a distinção importa:** não houve crossing reprovado — não
houve material que permitisse sequer tentar. `cruzar()` só trabalha sobre
`IT-T3`, e o delta trouxe zero `IT-T3`.

### FASE 8 · clima → risco → cultura → produto

```text
RESULTADO = ZERO
```

Não fabrico exemplo. Os novos 17 não contêm um único dado meteorológico,
fenológico ou de pressão de praga. O sinal climático que existe na Sala
— ARIF × APOL, «temperaturas altas travam a *Bactrocera oleae*, chuva e queda
térmica soltam-na» — **é o mesmo da 1ª rodada, e não ganhou evidência nova.**

Não emito `WATCH_SIGNAL` novo: repetir o sinal anterior com data de hoje seria
inflacionar contagem com a mesma observação.

---

## F · GAPS (registados, não despachados)

| id | gap | estado |
|---|---|---|
| `GAP-01` | **`CROP` não atravessa** — 5/5 dos T3 em `LOST_IN_DERIVATION` | **agravado: agora quantificado, 100%** |
| `GAP-02` | `FACT_TIME` = `NAO SEI` | **46/46** (era 29/29) |
| `GAP-03` | `FACT_LOCATION` = `NAO SEI` | **46/46** |
| `GAP-04` | `EVIDENCE_CLASS` = `NAO SEI` | **46/46** |
| `GAP-05` | universo largo para a pergunta | **agravado: 41 de 46 são T5/T7/T9** |
| `GAP-06` | **NOVO — re-observação sem evidência nova** | 12 dos 17 novos repetem texto já na Sala |
| `GAP-07` | **NOVO — a Big Collection não colheu `IT-T3`** | 0 boletins novos; a família útil ficou parada |

### `GAP-07` é o que decide a próxima Big Collection

```text
FONTES QUE PRODUZEM INTELLIGENCE:   IT-T3-002, IT-T3-008, IT-T3-010
ITENS NOVOS DESSAS FONTES:          0
```

A ARIF publica **semanalmente** (n.37, n.38 já estão na Sala). Entre a 1ª e a
2ª rodada saiu quase de certeza uma n.39 — e ela não foi colhida, enquanto
13 páginas de universidade entravam.

> Isto não é «fonte má» nem «coletor partido». É **prioridade de colheita**:
> a Big Collection escalou onde havia volume, não onde havia resposta.

```text
HIGH VOLUME  !=  HIGH VALUE
```

⚠️ Nenhum `COLLECTION_GAP` foi despachado e nenhum `SOURCE_COLLECTION_ADVICE`
foi emitido — esse owner continua sem implementação.

---

## G · TESTES (FASE 13)

| # | o que prova | medição | veredito |
|---|---|---|---|
| 1 | só itens novos são processados | interseção R1∩R2 = **0**; delta = 17 | **PASS** |
| 2 | item antigo não duplica | 3ª corrida com checkpoint de 46 → **0 itens** | **PASS** |
| 3 | `UNKNOWN` permanece | `FACT_TIME`/`FACT_LOCATION` = `{NAO SEI}`; conhecidos = 0 | **PASS** |
| 4 | `CROP` ausente bloqueia join | 0 crossings passaram | **PASS** |
| 5 | autorização continua gate duro | nenhum crossing sem join key; **defeito `D-01` registado** | **PASS com ressalva** |
| 6 | dependentes não viram independentes | 12/17 marcados redundantes | **PASS** |
| 7 | provenance permanece | itens sem `RAW_OBSERVATION_ID` = **0** | **PASS** |
| 8 | determinismo / idempotência | artefatos **byte-a-byte** iguais (16.963 B); 3ª corrida vazia | **PASS** |

```text
NEW_FAILURES = 0
```

---

## H · AUTOMAÇÃO (FASE 12 — preparar, não ligar)

```text
INCREMENTAL_PROCESSOR_READY      SIM   --desde-artefato, provado 46 → 17
CHECKPOINT_READY                 SIM   (RUN_ID, ORDEM), provado
IDEMPOTENCY_READY                SIM   (RUN_ID, ORDEM) + PIPELINE_VERSION
READY_FOR_SALA_EVENT_AUTOMATION  NÃO
```

### O que falta para `SALA_ITEM_ADMITTED → Intelligence automática`

```text
1. o checkpoint vive num FICHEIRO passado à mão.
   Automação precisa dele persistido e com dono — provavelmente uma tabela,
   e a decisão é arquitetural, não minha.

2. ninguém EMITE o evento. A Sala não avisa que alguém pousou;
   hoje quem sabe é quem corre o comando.

3. a TRAVA continua fechada: COLLECTION_FOUNDATION_CLOSED = NAO.
   Ligar Intelligence automática é «desenvolvimento NOVO de inteligencia»,
   que é exatamente o que ela impede.
```

**O motor é incremental e idempotente. O que falta é o gatilho e a
autorização — e nenhum dos dois é desta missão.**

---

## I · SYSTEM MAP

```text
SYSTEM_MAP_CHECK = PASS (sem churn)
```

Nenhum elo novo: a peça `C-PROVA-PILOTO-SALA` já estava declarada na 1ª rodada
e continua a ser o mesmo ficheiro, com o mesmo papel. O que mudou foi a lógica
interna, e lógica interna não move o mapa.

---

## J · ACUMULADO (contexto, não resultado)

```text
TOTAL_SALA                       46
TOTAL_PROCESSED_BY_INTELLIGENCE  46      29 (R1) + 17 (R2)

acumulado: USABLE 8 · WEAK 12 · INSUFFICIENT 26
crossings tentados 3 · possíveis 0 · oportunidades 0
```

---

## EM PALAVRAS SIMPLES

**1 · O que chegou de novo?**
Dezassete documentos. Treze de universidades, três de ordens/consórcios, um de
um concorrente. Nenhum boletim agrícola — **zero**.

**2 · Quantos serviram?**
Um. E esse um é uma piada do destino: é a página da Koppert sobre ácaros
predadores, **exatamente a mesma que já estava na Sala desde a rodada anterior**.
Foi recolhida outra vez.

Dos dezassete, **doze eram textos que a Sala já tinha**. Só cinco traziam
conteúdo inédito — e esses cinco são: as perguntas frequentes de um repositório
de universidade, dois calendários de exames, um curso online sobre vinho
Chianti e a página de uma semana temática sobre irrigação.

**3 · Apareceu sinal novo?**
Não. O único sinal interessante continua a ser o da rodada anterior: quando a
chuva chegar e a temperatura cair, a mosca da oliveira pode acordar. Não
repeti esse sinal com data de hoje — repetir a mesma observação com data nova
é inflacionar a contagem.

**4 · Apareceu oportunidade defensável?**
Não. E desta vez nem sequer houve tentativa: para tentar, é preciso ter
boletim agrícola, e não veio nenhum.

**5 · O `CROP` continua a ser o gargalo?**
Sim, e agora está **contado**. Dos cinco boletins agrícolas que a Sala tem, os
cinco perderam a cultura. **Cem por cento.** E não é que a informação não
exista: a palavra «oliveira», «vinha», «macieira» está lá escrita, no texto.
É que não há uma gaveta onde a guardar.

**A informação chegou. A prateleira não existe.**

**6 · O que a Collection precisa melhorar?**
Duas coisas, e a segunda é a que ninguém tinha visto:

Primeira, a gaveta da cultura — já sabíamos.

Segunda, **esta recolha foi buscar ao sítio errado**. As três fontes que dão
informação agrícola de verdade (a agência ARIF da Puglia, o serviço
fitossanitário de Salerno, a associação de olivicultores) **não entregaram um
único documento novo**. A ARIF publica todas as semanas; deve ter saído um
boletim novo entre uma rodada e outra, e ele não foi colhido — enquanto treze
páginas de universidade entravam.

Não é que as fontes estejam avariadas. É que se recolheu onde havia **muito**,
não onde havia **resposta**.

**7 · A Intelligence já pode ser ligada automaticamente à Sala?**
O motor sim: ele já sabe processar só o que é novo, e sabe não repetir trabalho
— testei três vezes seguidas e à terceira ele processou zero, corretamente.

Mas faltam três coisas: o «caderno» de onde ele parou ainda é um ficheiro
passado à mão; **ninguém avisa** quando chega documento novo à Sala; e a trava
de segurança do projeto continua fechada — ligar isto sozinho é precisamente o
que ela proíbe.

**Também encontrei um erro meu da rodada anterior e corrigi-o.** Na primeira vez
escrevi que o sistema «sabe distinguir» quando um produto está autorizado para
uma planta. Fui verificar com cuidado: **não sabe.** Ele recusa sempre, e recusa
pelo motivo certo — falta-lhe a planta — mas recusar sempre não é o mesmo que
saber decidir. Deixei isso escrito no código, em vez de o deixar parecer melhor
do que é.

**Próximo passo mínimo:** pedir à Collection o boletim novo da ARIF, e a gaveta
da cultura. Sem esses dois, a próxima Big Collection vai fazer a Sala crescer
outra vez sem a Intelligence avançar.

**HARD STOP.**
