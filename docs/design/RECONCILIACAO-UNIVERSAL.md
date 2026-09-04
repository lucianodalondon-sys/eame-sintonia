# A reconciliação universal — e a descoberta de que a base não era a bifurcação

```
UNIVERSAL_INTELLIGENCE_RECONCILIATION = PASS

HEAD inicial   85df96f   (inteligência)
               4628197   (catraca, já reconciliada até e7c154c)
HEAD final     este merge, em claude/opportunity-commercial-priority-v1
```

O briefing pedia para juntar `85df96f` com `d83f6f3`. A primeira medição mostrou
que a pergunta estava um passo atrasada — e o passo importa.

---

## 1 · Ancestralidade, medida antes de tocar em qualquer coisa

    NOME DE BRANCH NÃO É ANCESTRALIDADE. `git merge-base` É.

```
$ git merge-base 85df96f d83f6f3                 → 0ddf52d
```

| commit | ancestral de `85df96f` | ancestral de `d83f6f3` |
|---|---|---|
| `0ddf52d` | **YES** | **YES** ← a bifurcação |
| `caa6937` | YES | NO |
| `209335e` | YES | NO |
| `4b97cf5` | YES | NO |
| `e7c154c` | YES | NO |
| `85df96f` | YES | NO |
| `d83f6f3` | NO | YES |

Duas irmãs, nenhuma contém a outra — exatamente como o briefing supunha.

**Mas `d83f6f3` não é o HEAD da linhagem da catraca.** A branch
`claude/trilha-universal-inteligencia-a5rx9d` avançou dois commits depois dele,
e esses dois **já eram uma reconciliação**:

```
* 4628197  as 16 janelas nao eram janelas, e o ACT NOW zero era defeito meu
* 2fef157  reconciliar: a linhagem nova ja era dona do cartao, e a minha
|\         camada era um segundo dono
| * e7c154c  ← a inteligência, puxada para dentro
* d83f6f3  a catraca media a traducao antes de ela entrar
* 83d26b6  a catraca existe
```

```
$ git merge-base 85df96f origin/claude/trilha-universal-inteligencia-a5rx9d
→ e7c154c
```

**A base real deste merge é `e7c154c`, não `0ddf52d`.** Um commit meu de um
lado; dois do outro. O trabalho pedido — «não escolher uma das duas» — já tinha
sido metade feito por quem escreveu `2fef157`, e refazê-lo do zero teria
desfeito uma reconciliação correta.

    QUEM MERGEIA A PARTIR DA BIFURCAÇÃO QUANDO A BASE JÁ AVANÇOU
    NÃO ESTÁ A RECONCILIAR: ESTÁ A REVERTER.

---

## 2 · Zero conflitos de código — e essa é a prova, não a sorte

```
$ git merge origin/claude/trilha-universal-inteligencia-a5rx9d
CONFLICT (content) × 9  — todos marcadores de contagem de teste
```

**Nenhum arquivo de código colidiu.** Os nove conflitos foram o mesmo marcador
`TEST_COUNT_CURRENT` em nove documentos, e o dono deles é
`scripts/metricas_canonicas.py --sync`.

Isso só é possível porque os dois lados tocam conjuntos disjuntos:

| linhagem | arquivos |
|---|---|
| inteligência (`85df96f`) | `v21_janelas.py` · `v21_necessidade.py` · `v21_oportunidades.py` |
| catraca (`4628197`) | `v21_catraca.py` · `v21_aceitacao.py` · `v21_testemunha_universal.py` · passo `6c` da cadeia |

E são disjuntos porque `2fef157` **apagou** `v21_briefing.py` e
`v21_ler_briefing.py` — a camada paralela que era um segundo dono do cartão.

---

## 3 · O mapa de donos — nenhuma decisão com dois

`python3 scripts/v21_reconciliacao_universal.py` verifica isto lendo o código
da catraca, não a documentação.

| decisão | dono | nasceu em |
|---|---|---|
| `WINDOW_TYPE` · `WINDOW_DEFINED` · `WINDOW_OPEN_NOW` | `v21_janelas.py` | `209335e` |
| `WINDOW_OPEN_NOW_METHOD` | `v21_janelas.py` | `e7c154c` |
| `WINDOW_RULE_STATE` (`DECLARED` · `ADMINISTRATIVE_ONLY` · `DELEGATED_TO_FARM` · `NOT_DECLARED`) | `v21_oportunidades.py` | `85df96f` |
| `THRESHOLD_STATE` | `v21_oportunidades.py` | `e7c154c` |
| `PEST_STAGE_STATE` · `ACTION_RECOMMENDATION_STATE` | `v21_necessidade.py` | `e7c154c` |
| `NEED_DIRECTION` | `v21_necessidade.py` | `0ddf52d` |
| `COMMERCIAL_PRIORITY` · `EXTERNAL_MATERIAL_READY` | `v21_comercial.py` | `0ddf52d` |
| `STATUS` · `WHY_NOW_CODES` | `v21_oportunidades.py` | `caa6937` |
| `PORTFOLIO_MATCHES` · `PRIMARY_MATCH` | `v21_oportunidades.py` | `0ddf52d` |
| `EVIDENCE_ROLES` · `INTELLIGENCE_BRIEF` · `ACTION_BY_DEPARTMENT` · `WHAT_IS_MISSING` | `v21_oportunidades.py` | `caa6937` |
| **`PUBLICATION_STATE` · `TRAIL_STATE`** | **`v21_catraca.py`** | **`d83f6f3`** |

`U10` já pinava que a catraca escreve **exatamente** sete campos, todos seus.
`v21_reconciliacao_universal.py` volta a conferir por fora, e reprova se a
catraca passar a escrever qualquer campo com outro dono.

    UMA CAMADA POR CIMA QUE MUDA UM NÚMERO DE BAIXO NÃO É CAMADA: É DONO.

---

## 4 · As oito testemunhas semânticas, no estado reconciliado

Todas medidas por `v21_reconciliacao_universal.py` — **0 falhas**.

| | testemunha | medido |
|---|---|---|
| **A** | botrite × videira × Emilia-Romagna | `OPP_5F31A63F844D` · `ACT_NOW` · `PREHARVEST_WINDOW` · `WINDOW_OPEN_NOW = YES` por `ESTADIO_DECLARADO_NO_MESMO_DOCUMENTO` · **`PUBLICATION_STATE = PUBLISHABLE`** por cima |
| **B** | Toscana · «siamo nella fase di maggior suscettibilità» | prova **um** elo. Janela de `IT-COL-2609-TO-BOTRITE`; direção de `IT-PHEN-040`; produto do rótulo ministerial — três donos |
| **C** | Veneto × carpocapsa | `PEST_STAGE_STATE = STAGE_ENDED` **e** `ACTION_RECOMMENDATION_STATE = CONTINUE_RECOMMENDED`, com `WINDOW_OPEN_NOW = UNKNOWN` — fim do voo não fechou nada |
| **D** | Emilia-Romagna · 5% | `THRESHOLD_STATE = NOT_DECLARED` · `WINDOW_OPEN_NOW = UNKNOWN` por `FONTE_NAO_DECLARA_A_MEDICAO_QUE_A_CONDICAO_EXIGE`. **Nunca `NO`** |
| **E** | Umbria · 10–15% | `WINDOW_CONDITION` própria, evidência `IT-COL-2609-UM-TIGNOLETTA` ≠ `IT-PHEN-001` da Emilia-Romagna. Os 5% não migraram |
| **F** | `RULE_DELEGATED_TO_FARM` | `WINDOW_DEFINED = YES` (a regra é conhecida) · `WINDOW_OPEN_NOW = UNKNOWN` (a medição é do pomar) |
| **G** | `STANDING_RULE` | 7 regras no acervo · **0 cartões** com direção vinda de uma regra |
| **H** | `RULE_ADMINISTRATIVE_ONLY` | `WINDOW_DEFINED = NO` e `WHAT_IS_MISSING` diz `WINDOW_RULE_ADMINISTRATIVE_ONLY` — ato de norma não virou janela agronômica |

E nenhuma das cinco proibições reapareceu: calendário como única janela,
limiar cruzando região, fim de voo = fim de ação, frase vaga = medição, regra
permanente = direção atual.

---

## 5 · A testemunha da catraca, ponta a ponta

`python3 scripts/v21_testemunha_universal.py` → **EXIT 0**

```
RAW MATERIAL → CANONICAL ENTRY → NORMALIZATION → INTELLIGENCE
             → WINDOW MODEL → COMMERCIAL PRIORITY → COMMERCIAL BRIEFING
             → ACCEPTANCE → PUBLICATION_STATE
```

Dez fixtures, uma por família, mais uma fonte nova — todas pela porta real, sem
uma única chamada manual. Oito entraram e passaram pela catraca; duas
(`COMMERCIAL_CATALOG`, `HERBICIDE_CURRENT_CONTEXT`) estão **declaradas fora**, e
a testemunha conta isso como declaração, não como perda.

```
AUTOMATIC_NEW_INGEST      YES
UNIVERSAL_GATE            YES
BACKFILL                  YES
UNIVERSAL_TRAIL_COVERAGE  PARTIAL   (as duas famílias declaradas fora)

BUILD_ID base        V21-1cac64ceb8067205
BUILD_ID com fixture V21-37348edb8c8e1d44   ← a porta é lida mesmo
BUILD_ID restaurado  V21-1cac64ceb8067205   ← IGUAL. Zero resíduo.
```

E a catraca, no acervo inteiro:

```
== A CATRACA ==
porta          10 familias · COMMERCIAL_CATALOG 0/10 · HERBICIDE_CURRENT 0/16
material       7.036 registros · PASSED 6.998 · INCOMPLETE 38 · QUARANTINED 0
oportunidades  PUBLISHABLE 5 · VALIDATION_REQUIRED 38
trilha         COMPLETE 43                       VIOLACOES 0
```

---

## 6 · O backfill contra `85df96f` — o resultado que uma camada correta produz

`ANTES` gerado com `git checkout 85df96f` e a cadeia real; `DEPOIS`, a árvore
reconciliada.

```
                          85df96f          reconciliado
casos                        43                 43
casos que sumiram             —                  0
casos que nasceram            —                  0

STATUS                    idêntico            idêntico
COMMERCIAL_PRIORITY       idêntico            idêntico
EXTERNAL_MATERIAL_READY   idêntico            idêntico
NEED_DIRECTION            idêntico            idêntico
WINDOW_DEFINED            idêntico            idêntico   (16)
WINDOW_TYPE               idêntico            idêntico
WINDOW_OPEN_NOW           idêntico            idêntico
WINDOW_RULE_STATE         idêntico            idêntico
WHY_NOW_CODES             idêntico            idêntico
PORTFOLIO_MATCHES         idêntico            idêntico
PRIMARY_MATCH             idêntico            idêntico
ACTION_MAP                idêntico            idêntico
PEST_STAGE_STATE          idêntico            idêntico
ACTION_RECOMMENDATION     idêntico            idêntico
THRESHOLD_STATE           idêntico            idêntico
WHAT_IS_MISSING           idêntico            idêntico

CAMPOS QUE MUDARAM: {}     ← nenhum

PUBLICATION_STATE      None ×43     →   PUBLISHABLE 5 · VALIDATION_REQUIRED 38
TRAIL_STATE            ausente      →   COMPLETE 43
```

**Zero diferenças em dezesseis campos, e dois campos novos.** É exatamente o
que uma camada por cima deve produzir: ela acrescenta um estado e não decide
nada que já tinha dono.

`U19` reprova se isso mudar. `U20` reprova se a catraca declarar publicável um
cartão que o motor não autoriza a sair — hoje os 5 `PUBLISHABLE` são exatamente
os 5 `EXTERNAL_MATERIAL_READY = YES`.

Estado final do acervo:

```
STATUS                WATCH 22 · TO_VALIDATE 9 · FUTURE_PREPARATION 7
                      VALIDATE_NOW 3 · ACT_NOW 2
COMMERCIAL_PRIORITY   TO_VALIDATE 17 · COMMERCIAL_WATCH 13
                      STRATEGIC_OPPORTUNITY 8 · SALES_READY 5
WINDOW_DEFINED        YES 16 · NO 27
WINDOW_OPEN_NOW       UNKNOWN 41 · YES 2 · NO 0
WINDOW_RULE_STATE     NOT_DECLARED 26 · DECLARED 15
                      DELEGATED_TO_FARM 1 · ADMINISTRATIVE_ONLY 1
PUBLICATION_STATE     VALIDATION_REQUIRED 38 · PUBLISHABLE 5
TRAIL_STATE           COMPLETE 43
```

---

## 7 · O contrato comercial — apresentação, nunca recálculo

Cada linha do contrato aponta o campo do cartão que **já decidiu**. O witness
confere que o campo existe; se um dia o briefing recalcular, o dono some e o
teste acusa.

| linha do contrato | dono que responde |
|---|---|
| `WHAT_IS_HAPPENING` | `INTELLIGENCE_BRIEF` |
| `WHY_THIS_IS_A_COMMERCIAL_OPPORTUNITY` | `WHY_COMMERCIAL` |
| `WHY_NOW` | `WHY_NOW_CHAIN` |
| `PORTFOLIO_MATCHES[]` · `PRIMARY_MATCH` | os mesmos campos do cartão |
| `WHAT_IS_MISSING` | `WHAT_IS_MISSING` |
| `ACTION_MAP[]` | `ACTION_BY_DEPARTMENT` |
| `INTELLIGENCE_BRIEF` | `INTELLIGENCE_BRIEF` |
| `EVIDENCES[]` | `EVIDENCE_ROLES` |

O arquivo paralelo `OPPORTUNITY-BRIEFINGS.json` **não voltou** — `U10b` o
impede. O contrato existe inteiro dentro do cartão.

---

## 8 · Os 26 sem coleção, revalidados contra o modelo novo

`python3 scripts/v21_censo_das_16_janelas.py` · **não ingere nada**

```
PAPEL_DE_TRABALHO = 10        JANELAS_CORRENTES = 16
```

A separação 10/16 confirma-se. E agora medida contra o modelo **de `85df96f`**,
que conhece oito tipos de janela e um léxico estendido por cinco disciplinari:

| | |
|---|---:|
| com tipo **agronômico** reconhecido | **0** |
| `ADMINISTRATIVE_WINDOW` | 2 |
| sem alvo nomeado no texto | 6 |
| **duplicatas de janela já modelada** | **0** |
| cultura × região **já representada** no pacote | **6** |
| realmente novas | 16 |

> ⚠️ **Duas perguntas que o censo anterior fazia como uma.** «Já representado» é
> o pacote ter um caso para a mesma cultura × região; «duplicata» é já haver
> **janela definida** para o mesmo par. Seis são conhecidas pela primeira
> pergunta e nenhuma pela segunda.
>
>     DIZER «NOVO» SOBRE COISA CONHECIDA E «DUPLICATA» SOBRE COISA QUE NINGUÉM
>     MODELOU SÃO O MESMO ERRO, EM DIREÇÕES OPOSTAS.

Nenhuma das 16 corresponde a regra coletada em `85df96f`: as regras novas são de
videira, macieira e milho; as 16 são trigo genérico ×7, arroz ×3, beterraba,
tomate e quatro sem cultura. **Não foram ingeridas.**

---

## 9 · ISTAT · `area[0]` — o bug era latente, e agora tem critério

**Medido primeiro:** hoje `area[0]` **nunca dispara**. Das 2 978 linhas de
`CROP-ECONOMIC-WEIGHT`, 13 são client-safe e **nenhuma tem `INDICATOR`** — logo
**0 dos 43 cartões** carregam `AREA_OFICIAL_HA`. O defeito só nasce no dia do
carimbo.

**Corrigido:** a seleção deixou de ser a ordem do arquivo.

```python
area.sort(key=lambda e: (str(e.get('YEAR') or ''), str(e.get('ID'))), reverse=True)
```

    UM NÚMERO QUE MUDA DE SIGNIFICADO PELA ORDEM DO ARQUIVO
    É UM NÚMERO SEM DONO.

O critério aplicado **não é inventado**: é a composição de dois contratos que já
existem — «o documento mais recente que afirma alguma coisa responde por ela,
empate desfaz-se pelo ID» (`v21_oportunidades.declarados`, escrito em `e7c154c`)
e «só material client-safe entra no cartão». Junto: *a mais recente entre as que
passaram pelo portão*. O cartão passa a publicar `AREA_OFICIAL_ANO` e
`AREA_SELECTION_RULE` ao lado do valor — **número de área sem ano não se compara
com nada**.

**A POLÍTICA continua sendo decisão de vocês, e ela pesa:**

```
QUAL ANO ALIMENTA COMMERCIAL_MAGNITUDE?
  critério aplicado hoje : MAIS_RECENTE_ENTRE_AS_CLIENT_SAFE
  política               : DECISION_REQUIRED
  casos medidos          : 33
  critérios DISCORDAM em : 29
```

Os três candidatos divergem em **29 dos 33** casos, porque o ano do sinal é 2026
— justamente o ano que o ISTAT publica como provisório:

| critério | daria | tem contrato escrito? |
|---|---|---|
| `ULTIMO_QA_PASS` | 2025 | sim, por composição de dois contratos existentes |
| `ANO_MAIS_RECENTE` | 2026 (provisório) | não |
| `ANO_DO_SINAL` | 2026 (provisório) | não |

**Carimbo não aplicado.** `QA_PASS = PARTIAL` — 2024 YES · 2025 YES · 2026
UNKNOWN. Carimbar 2024+2025 liberaria 2 006 linhas e tiraria
`OFFICIAL_AREA_NOT_CLIENT_SAFE` de 43 cartões; **nenhum resultado comercial
mudaria**, porque área não é portão.

---

## 10 · A suíte, com a equação fechada

Dono da contagem: `scripts/v21_contagem_da_suite.py`.

```
DISCOVERED         786
NEVER_EXECUTED       0     (nenhuma classe abortou no setUpClass)
EXECUTED           786
  PASS             765
  FAIL               6
  ERROR_CASE         1
  ERROR_HOLDER       0
  SKIPPED           14
  XFAIL / XPASS    0 / 0

EQUAÇÃO   786 = 765 + 6 + 1 + 14        ✅ fecha
          DISCOVERED = NEVER_EXECUTED + EXECUTED   →   786 = 0 + 786   ✅ fecha
```

As 6 falhas e o 1 erro são os de sempre: procedência de amostras antigas (×5),
o gate de import ES, e `test_comunicacao`, que é script e falha na descoberta.
**Nenhuma nova.**

Por camada: comercial **100/100** · trilha universal **23/23** (`U19`–`U21`
novos).

---

## 11 · Regressões

Nenhuma. Todas as testemunhas verdes na árvore reconciliada:

```
UNIVERSAL_INTELLIGENCE_RECONCILIATION = PASS
SEMANTIC_RED_TEAM                     = PASS
REGRESSAO_DO_RED_TEAM                 = PASS
WINDOW_RULE_CLOSURE                   = PASS
testemunha universal                  = EXIT 0 · BUILD_ID restaurado idêntico
catraca / aceitação / geografia / procedência = 0 violações
```

---

## Resposta

```
UNIVERSAL_INTELLIGENCE_RECONCILIATION = PASS

HEAD inicial     85df96f (inteligencia) · 4628197 (catraca ja reconciliada)
merge-base real  e7c154c — NAO 0ddf52d, porque a outra branch ja tinha
                 puxado a inteligencia em 2fef157
HEAD final       o merge desta rodada, em claude/opportunity-commercial-priority-v1

conflitos        9 — TODOS marcadores de contagem de teste. ZERO em codigo.
donos preservados de 85df96f   janela, tipo, regra, limiar, fase da praga,
                               recomendacao, direcao, prioridade comercial,
                               WHY_NOW, portfolio, papeis de evidencia
componentes de d83f6f3         UNIVERSAL_GATE, v21_catraca, PUBLICATION_STATE
                               so rebaixavel, aceitacao fatal, testemunha
                               universal, ordem traducao -> catraca

43 casos antes -> 43 depois · 0 sumiram · 0 nasceram
CAMPOS QUE MUDARAM = {}   (16 campos comparados)
WINDOW_DEFINED     16 -> 16        WINDOW_RULE_STATE   inalterado
STATUS / COMMERCIAL_PRIORITY / EXTERNAL_MATERIAL_READY / NEED_DIRECTION  iguais
PUBLICATION_STATE  ausente -> PUBLISHABLE 5 · VALIDATION_REQUIRED 38
TRAIL_STATE        ausente -> COMPLETE 43

testemunhas semanticas   A a H · 0 falhas
testemunha de ingestao   AUTOMATIC_NEW_INGEST YES · BACKFILL YES
                         BUILD_ID restaurado identico
26 sem colecao           10 papel de trabalho · 16 janelas
16 janelas               0 agronomicas · 2 administrativas · 0 duplicatas
                         6 com cultura x regiao ja representada · NAO ingeridas
ISTAT / area[0]          bug latente (0 cartoes hoje) · seleção agora explicita
                         politica = DECISION_REQUIRED · criterios discordam em
                         29 de 33 casos · CARIMBO NAO APLICADO
suite                    786 = 765 + 6 + 1 + 14 · 0 nunca executados
regressoes               nenhuma

CANONICAL_BRANCH = claude/opportunity-commercial-priority-v1
AUDIT_BRANCH     = FROZEN (claude/opportunity-radar-audit-hem6p2 em e7c154c)

PORTAL = NAO TOCADO      DESIGN = NAO TOCADO      VERCEL = NAO TOCADO
PRODUCAO = NAO TOCADA    NOVA COLETA = NAO        THRESHOLDS = NAO ALTERADOS
SEGUNDO MOTOR = NAO CRIADO   PUBLICACAO = NAO     MERGE EM MAIN = NAO
```
