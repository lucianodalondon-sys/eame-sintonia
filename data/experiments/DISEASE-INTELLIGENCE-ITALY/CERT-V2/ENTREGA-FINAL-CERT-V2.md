# CERTIFICAÇÃO INDEPENDENTE V2 — PILOTO DE PRESSÃO DE DOENÇA · ENTREGA FINAL

Todos os números deste documento são lidos de `p17_delivery.json`, que por sua vez os lê dos
ficheiros de evidência. Se um número aqui divergir de lá, este documento está errado.

---

## REGRA 0 — ISOLAMENTO

```
SOURCE_ENTRY_BRANCH   = claude/pilot-disease-evolution-vite-veneto
SOURCE_ENTRY_HEAD     = d7631a29aeef46e1e528ce31cc38059436477dda
SOURCE_ENTRY_CONTAINS_THE_FINAL_PILOT = NÃO
```

**A branch de entrada era a errada.** Ela contém o piloto de *previsão* (VITE × PERONOSPORA,
ERA5 + ARPAV) e está **34 commits atrás** do piloto de *pressão*. A missão manda, nesse caso,
localizar o HEAD final correto e usá-lo como base. Foi o que fiz.

```
SOURCE_BRANCH  = claude/disease-intelligence-italy-overnight
SOURCE_HEAD    = a4d19ddf36f3fa4b187e8563d1d4226d399a4daf
                 ("Independent arbiter: NOT_YET. Five of my ten gate verdicts overturned")
BRANCH         = claude/disease-pressure-certification-v2
HEAD           = 098b4de5418885bc28ada78e8d1aa81f09d7477f
WORKTREE_CLEAN = SIM (worktree separado em C:/cert-v2-disease-pressure)
UNTRACKED_DEPENDENCIES = 1
```

A única dependência fora do Git é `ENGINE/gates.py:241`, que lê o caminho absoluto
`/home/user/eame-sintonia/italia-portale/client/meeting-intelligence-snapshot.json` — enquanto
uma cópia byte-a-byte está versionada neste repositório. Varredura dos 19 ficheiros Python do
piloto: é a **única** referência que um clone novo não resolve.

`ENGINE/`, `CASES/` e `italia-portale/` estão **byte-a-byte idênticos** a `a4d19dd`. Nada do
piloto e nada do portal foi tocado.

---

## ENTREGA

```
CLEAN_CHECKOUT_REPRODUCIBLE = NÃO
```

Um clone novo devolve gate C = 18, F = 0.924, G = 0.432, J = FAIL, e a contagem
`PASS=8 FAIL=2 NOT_TESTABLE=0`. O `gates.json` commitado diz 19, 0.918, 0.424, NOT_TESTABLE e
`PASS=8 FAIL=1 NOT_TESTABLE=1`. **8 de 28 campos diferem.** Offline vira `PASS=7 FAIL=3`,
porque o gate H faz chamadas HTTP ao vivo dentro da própria execução.

**Causa, uma só:** `current_pressure.denominator_guard` escreve `den[id_survey]` percorrendo um
`glob.glob()` **não ordenado**, e `id_survey` não é único — de 52 250 chaves, 14 649 aparecem em
mais de um ficheiro de safra, 2 443 com valores conflitantes, e em 1 759 delas o conflito decide
DESCARTAR ou MANTER. Ganha o ficheiro que o disco entregar por último.

**Correção contra mim:** eu primeiro escrevi que o valor commitado 0.918 *não era alcançável por
nenhuma ordem*. Estava errado, e o defeito era da minha sonda, que reembaralhava a cada chamada.
Com ordens **fixas** (uma permutação por semente, aplicada a todas as chamadas), 0.918 aparece em
2 de 8 execuções minhas e em 16 de 33 de uma lente independente, que ainda reproduziu o trio
commitado inteiro em 4 de 33. O resultado não é *irreproduzível*: é **subdeterminado**. Duas
máquinas rodando o mesmo código corretamente discordam. Continua desqualificante, porque o gate E
certifica "re-execução byte-a-byte" e não consegue ver isto — as duas execuções que ele compara
estão no mesmo processo e no mesmo sistema de ficheiros.

```
UNIT_OF_ANALYSIS = REGIÃO × CULTURA × PROBLEMA × DATA (× PROVÍNCIA)
REGION_X_CROP_X_ISSUE_X_DATE = PASS como fenómeno · FAIL como representação
```

A DATA é real e é decisiva: 22 de 25 células mudam de estado ao longo da série, 21 delas dentro
de 2026. A tabela C25 do próprio piloto foi reproduzida **exatamente**, nas seis células:

| data | OLIVEIRA | VINHA |
|---|---|---|
| 2026-06-15 | 0/10 (latência 241 d) | 6/10 |
| 2026-08-01 | 6/10 | 1/10 |
| 2026-09-06 | 8/10 | 0/10 |

Mas o objeto que o motor devolve carrega `AS_OF` e **nada** que nomeie a região, a cultura ou o
problema. Três das quatro dimensões existem só no nome de uma pasta e num argumento de texto
livre que o chamador passa — e em `gates.py:26` esse argumento é literalmente a palavra `"crop"`.

```
GATES_TOTAL          = 10
VALID_GATES          = 1     (apenas o G — que é o único que FALHA nos dados reais)
INVALID_GATES        = 9
TAUTOLOGICAL_GATES   = 1     (J: incapaz de devolver PASS)
MUTATION_TESTS       = 33 minhas + 5 do red team + 5 do árbitro = 43
MUTATIONS_CAUGHT     = 14
MUTATIONS_NOT_CAUGHT = 8 minhas/red team + 5 do árbitro
```

**Oito dos dez gates passam enquanto a propriedade que eles nomeiam está destruída.** O árbitro
escreveu cinco mutações do zero: **5 de 5 sobreviveram**, e uma delas *aumentou* a nota de 8 PASS
para 9 PASS. As três mais graves:

- **B** devolve PASS com o corte de tempo removido, imprimindo "o corte é LOAD-BEARING e este
  gate consegue detectar a sua remoção". Isolando só o corte superior: **0 de 20** células mudam
  de classe. As 18 células que o gate exibe como prova movem-se porque avançar o `AS_OF` em 30
  dias desloca o limite **inferior** da janela.
- **D** devolve PASS enquanto todas as províncias sem dados são publicadas com VALOR 0.0 e classe
  `LOWER_THAN_USUAL`. O seu predicado é "existe pelo menos um UNKNOWN", satisfeito por uma célula
  simbólica. E a asserção que ele cita como prova —
  `Missing.assert_not_coerced_to_zero(NOT_KNOWN, None)` — **não consegue disparar**: só levanta
  quando o valor é 0, 0.0 ou "0", e a chamada passa `None` literal.
- **E** devolve PASS sob uma ordem de ficheiros fixa mas diferente — exatamente o defeito do
  Passo 1.

```
DATE_SENSITIVITY_TEST         = PASS
CELLS_CHANGING_STATE_BY_DATE  = 22 de 25

EFFECT_FLOOR                  = NOT_PROVED
EFFECT_FALSE_POSITIVES        = não mensurável pelo teste que usei primeiro
EFFECT_FALSE_NEGATIVES        = 8 células retidas eram o valor mais alto já registado naquela
                                janela naquela província (3 delas em datas de 2026)
```

**A minha primeira prova do piso era uma tautologia** e foi retirada: `kept` é definido como
`STATE == HIGHER`, que o piso só permite quando `n_sites × incidência ≥ 5`; filtrar `kept` por
`< 5` dá vazio por construção. Aqueles dois zeros apareceriam para um piso de 1, de 5 ou de 70.
O que sobra, medido honestamente: o piso está **ausente** da lista de parâmetros do próprio
módulo, ausente do bloco `PARAMS` emitido e ausente da grade de 135 pontos — ou seja, o gate F,
cujo trabalho é medir dependência de parâmetros, nunca o variou. E **0** das chamadas HIGHER que
ele preserva estão na safra de 2026.

```
REFRESH_FAIL_CLOSED  = FAIL
LATENCY_TRUTHFUL     = PASS na medição · FAIL na certificação
CODE_VS_VALUE_GATE   = FAIL
GEOGRAPHY_GATE       = FAIL (não inventada; incompleta e não verificada)
CROP_NORMALIZATION   = FAIL
CROPS_IN_DATA        = OLIVO, VITE, FRUMENTO
CROPS_CANONICALIZED  = nenhuma
```

- **Refresh:** o guarda de escrita funciona — uma resposta vazia é recusada e o último dado bom
  sobrevive. Mas não existe **estado** nenhum de refresh: zero campos de tentativa, estado,
  último-bom ou data de coleta. Qualquer refresh parcial reconstrói o índice do zero e os
  ficheiros antigos deixam de ser verificados, em silêncio. Um erro de rede apaga a tabela de
  códigos e derruba o caso inteiro. E numa máquina cp1252 o ficheiro é gravado numa codificação e
  o hash calculado noutra: **22 de 138** ficheiros têm bytes não-ASCII, e refrescar qualquer um
  deles deixa o caso permanentemente offline.
- **Latência:** a definição está certa — vem da observação legível mais recente, e a data do
  ficheiro provadamente não entra. Mas o gate H compara com `as_of = 2026-09-06`, uma constante
  no código: a certificação de frescura nunca expira. E a badge é regional: nove províncias com
  900 dias de atraso ainda mostram "4 dias".
- **Código vs valor:** o guarda executa em **0 de 3** casos reais. E falta o guarda no sentido
  contrário — alimentado com a coluna `prodotto` (que fungicida o produtor aplicou), o motor
  publica classe de doença em 9 de 10 províncias, carimbada `OFFICIAL_OBSERVATION`. É pior do que
  o defeito que o piloto corrigiu: aquele produzia um absurdo 1.000, este produz um plausível
  0.000.
- **Geografia:** não é inventada — 0 províncias herdam a classe do vizinho, e a organização que
  faz o levantamento não é substituta da província (13 de 20 organizações trabalham em várias).
  Mas 30 linhas de 120 133 contradizem o código ISTAT da própria linha (comune 48049 VICCHIO, de
  Florença, arquivado sob Siena), e nada faz essa conferência. E — correção do árbitro contra mim
  — províncias sem qualquer dado **desaparecem da saída**, não são publicadas como UNKNOWN: o
  caso do trigo mostra 5 províncias das 10 da Toscana.

```
OLIVE_SIGNAL (2026-09-06) = 8/10 províncias publicadas, latência 2 dias
                            TODAS as oito leem LOWER_THAN_USUAL
                            0 HIGHER_THAN_USUAL publicadas em 2026, em qualquer caso
OLIVE_ADAMA_PRODUCT_RELATION = NOT_FOUND
```

A célula que "qualifica" é uma célula de pressão **baixa**. E 0 de 476 sítios monitorizados
atingem a banda amarela da própria fonte; 0 atingem a vermelha; a pior oliveira da Toscana leu
5%. `LOWER_THAN_USUAL` compara dois estados que a fonte pinta como "não requer ação".

`NOT_FOUND` está correto e é **mais largo** do que eu escrevi: o handoff que citei adjudica 3
produtos; a leitura maior no mesmo repositório cobre 2 030 pares rótulo-uso sobre 102 produtos, e
**0 de 2 030** nomeiam a mosca-da-azeitona. Continua a não ser prova de ausência no mundo, e
continua a não ser "não verificámos".

```
NEGATIVE_CONTROLS       = 8
FALSE_POSITIVES         = 0
FALSE_NEGATIVES         = NÃO SEI
UNKNOWN_GROUND_TRUTH    = não existe neste repositório um registo independente da pressão de
                          mosca-da-azeitona e de oídio na Toscana por província e data; a fonte
                          em teste não pode arbitrar sobre si mesma

INDEPENDENT_REPRODUCTIONS = 3 casos, reimplementados a partir do contrato escrito, sem importar
                            o motor: 25 células, 25 concordam, 0 discordam
INDEPENDENT_RED_TEAM      = 6 lentes (RT1..RT6), nenhuma escreveu os gates
INDEPENDENT_ARBITER       = ARBITER-V2.md
```

```
DISEASE_PRESSURE_TOOL = NOT_YET

PORTAL_INTEGRATION        = NO
OPPORTUNITY_INTEGRATION   = NO
FUTURE_RADAR_INTEGRATION  = NO
```

O `PORTAL_INTEGRATION = NO` não é decorativo: o portal já converte pressão em campo em ação
comercial. Dos 43 casos, 43 têm identificador `OPP_`; 17 são `O1_FIELD_PRESSURE` com estados
`WATCH` 12, `VALIDATE_NOW` 3, `ACT_NOW` 2; e `OPP_F8106D5E1767` é vinha × botrytis ×
`REGION_TOSCANA`, `ACT_NOW`, `COMMERCIAL_PRIORITY: SALES_READY`, produto BANJO.

---

## AS TRÊS PERGUNTAS, SEPARADAS

**(a) Existe um fenómeno real nos dados? SIM.** Vinte e uma safras de levantamento oficial
mostram um afastamento genuíno e reproduzível da permutabilidade: 8 de 9 células provinciais
classificam LOWER onde o acaso daria 2.13, e numa amostra independente de 282 células LOWER
aparece 79 vezes contra 46.0 esperadas, sem nenhum sorteio de 20 000 chegando a 79. As províncias
discordam realmente entre si. O fenómeno é *"como a vigilância desta safra se ordena contra a
mesma janela de calendário no seu próprio passado, por província"*, e é real. Dois limites
pertencem ao fenómeno e não ao instrumento: só o braço LOWER tem excesso sobre o acaso (HIGHER
dispara 36 vezes onde o acaso dá 36.5), e tudo o que foi medido em 6 de setembro está dentro da
banda de não-ação da fonte.

**(b) O instrumento é sólido? NÃO.** Publica classe de doença a partir de uma coluna de
pulverização; o guarda código-vs-valor corre em 0 de 3 casos; junta o denominador por uma chave
que colide 2 443 vezes em 52 250; não carrega cultura, problema nem região na saída; um dos três
casos tem a doença errada na caixa; províncias somem em vez de serem publicadas UNKNOWN; e um
refresh numa máquina cp1252 tira um caso do ar permanentemente.

**(c) A certificação é sólida? NÃO.** A minha própria suíte não mata: 5 de 5 mutações escritas
pelo árbitro sobreviveram. Retirei três das minhas próprias conclusões e o árbitro retirou mais
duas. Publiquei um número a partir de um script que estava fora do Git — que é exatamente o
defeito que esta certificação existe para apanhar.

**Um NÃO em (b) e (c) não é um NÃO em (a).**

---

## O QUE FALTA, NA ORDEM (do árbitro)

1. Tornar a junção do denominador determinística — chave `(ano_do_ficheiro, id_survey)`, falhando
   alto em colisão. **Nada abaixo disto é mensurável antes disto.**
2. Consertar os dois gates que não se mexem: J precisa de um PASS alcançável e de um caminho
   relativo ao repositório; B precisa comparar as células com e sem corte **no mesmo `AS_OF`**.
3. Repetir o mutation testing até matar. AM1, AM2 e AM3 do árbitro têm de ficar vermelhos.
4. Renomear o caso do trigo, ou coletar a var 382. Hoje a caixa diz Septoria e o conteúdo é oídio.
5. Adicionar o guarda no sentido que falta: tabela de códigos nominal não pode virar escala.
6. Publicar a banda absoluta ao lado da classe.
7. Pôr o piso de efeito no `PARAMS` e na grade de sensibilidade, e re-rodar o gate F.
8. Dar estado ao refresh, fundir o índice em vez de reconstruí-lo, e gravar em UTF-8.
9. Carregar a identidade no objeto: país, região, cultura, problema — e emitir **todas** as
   províncias da região.
10. Descongelar o relógio da certificação.
11. Só então re-rodar a suíte a partir de um clone novo e exigir artefactos byte-a-byte iguais.

Duas coisas **nenhuma alteração de código resolve**: a taxa de falsos negativos, e se uma chamada
HIGHER significa alguma coisa.

---

## TOP 5 ACHADOS

1. **Oito dos dez gates passam com a sua própria propriedade destruída**, e um gate não consegue
   passar de todo. Cinco mutações escritas por um árbitro que não viu o código: 5 de 5
   sobreviveram, uma delas *melhorando* a nota.
2. **O motor publica uma classe de doença a partir da coluna que diz qual fungicida foi
   aplicado** — 9 de 10 províncias, carimbadas OFFICIAL_OBSERVATION. O guarda que deveria impedir
   isto corre em 0 de 3 casos reais.
3. **O resultado commitado é subdeterminado**: a mesma pasta dá números diferentes conforme a
   ordem em que o disco entrega os ficheiros, e metade dos bytes de que a célula publicada
   depende nunca é verificada por hash — enquanto o gate E imprime que "todos os ficheiros são
   verificados".
4. **A célula que qualifica é uma célula de pressão baixa**: as 8 províncias publicadas leem
   todas LOWER_THAN_USUAL, e 0 de 476 sítios atingem a banda mais baixa de alerta da fonte. E o
   piloto publicou a variável atrasada: em 24 834 de 78 012 visitas há infestação **viva** onde o
   dano registado é zero.
5. **O caso que prova a generalização mede a doença errada** — `FRUMENTO-SEPTORIA` coleta a var
   372, *Intensità Oidio*, em 14 de 14 ficheiros; a Septoria é a var 382 e nunca foi coletada.

## BLOQUEADORES

- Junção do denominador não determinística (bloqueia toda a medição a jusante).
- Gates B, D, E, A, C, F, H, I passam com a sua propriedade destruída; J não pode passar.
- O motor aceita uma lista nominal como escala de severidade.
- Sem estado de refresh e com o índice reconstruído a cada execução, a cadeia de hashes encolhe
  em silêncio; numa máquina cp1252 um refresh derruba o caso.
- Sem gabarito independente, a taxa de falsos negativos é **NÃO SEI**.

## COMMITS

```
098b4de  cert-v2: my step-1 headline was wrong, and the probe behind it was not in git
54ff58c  cert-v2: correction against myself — the cutoff changes 0 of 20 cells, not 5 of 10
a8b9650  cert-v2: inventory re-run including the red team's own five mutations
a2a9820  cert-v2 step 15: the red team broke my own certification in three places
7b12110  cert-v2 steps 2-3: 28 mutations against ten gates, and three gates that do not notice
61041f9  cert-v2 steps 4-14: the instrument measured against itself, including three of my own
         bad tests
28a445c  cert-v2 step 1: the clean checkout does not reproduce, and the cause is the machine
```
