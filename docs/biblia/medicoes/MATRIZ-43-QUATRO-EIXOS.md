# MATRIZ DOS 43 × OS EIXOS SEMÂNTICOS — MEDIÇÃO D0.3

```
DOCUMENT_STATUS   MEASUREMENT
DATE              2026-09-08
BRANCH            research/delivery-bible-v1
HEAD_INICIAL      65cf4b206c9ae3bffcadddcb4a737bc78407d8e8   (árvore limpa)
BASELINE_MEDIDO   a4fb6d81681094925ccfd1638bc7386cbec6f4d4

FONTE A  italia-portale/client/meeting-intelligence-snapshot.json
         sha256 986ac3e3f6f0e53e422db5fc8ea9577c83e96ba89e4f016b5e6c3076e12d6828
FONTE B  italia-portale/client/adama-relevance.js
         sha256 cadb2a4d8db982c2a015cdd27e19bcbb4b20aa67a553187305b82d72392209e7

BUILD_ID (A) = BUILD_ID (B) = V21-ef6e7e5f37eaa6e6      ← a MESMA safra
GERADO POR   docs/biblia/medicoes/medir_43_quatro_eixos.py   READ-ONLY
DADOS        docs/biblia/medicoes/MATRIZ-43-QUATRO-EIXOS.json

IMPLEMENTAÇÃO 0 · PRODUÇÃO 0 · RUNTIME 0 · MERGE 0 · DEPLOY 0
```

> Esta missão **não escolhe** entre Linha A e Linha B. Mede a relação real entre os
> conceitos que já existem, e devolve o veredito que a medição sustenta — nem mais.

---

## §1 · PROVAS DE INTEGRIDADE

```
CASE_IDS_UNIQUE ................. 43        PASS
IDS DUPLICADOS .................. 0         PASS
IDS SÓ NUMA FONTE ............... 0         PASS   (os conjuntos coincidem)
AGREGADOS QUE RECOMPÕEM ......... 8 / 8     PASS
TODAS AS MATRIZES FECHAM EM 43 .. 11 / 11   PASS
DUAS CORRIDAS BYTE-IDÊNTICAS .... PASS      (determinismo)
```

O script **reprova e sai com erro** se qualquer uma destas contas deixar de fechar.
Reprovou uma vez, durante o desenvolvimento, e o motivo ficou registado:

> **`PER_CLASSE` declara `E: 0`.**
> Uma classe declarada com população zero não é uma divergência — é vocabulário
> publicado sem membros. O script passou a registá-la à parte em vez de a apagar da
> comparação em silêncio.
>
> **`ESTADO DECLARADO E VAZIO ≠ ESTADO AUSENTE`.**

**Dois estados declarados e vazios, medidos:**

| onde | estado | população |
|---|---|---|
| `adama_relevance.py` · `PER_CLASSE` | `E` («NÃO SEI — dados insuficientes; nunca sobe») | **0** |
| `v21_comercial.py` · `PRIORIDADES` | `SALES_PREPARE` | **0** |

`SALES_PREPARE` é o mais interessante: o código define-o, dá-lhe uma frase de
significado e **quatro caminhos de retorno distintos** — e nenhum dos 43 casos o
alcança. É um estado inteiro do vocabulário comercial que este universo não exercita.

---

## §2 · OS AGREGADOS MEDIDOS

```
BY_STATUS                ACT_NOW 2 · VALIDATE_NOW 4 · FUTURE_PREPARATION 7 ·
                         WATCH 21 · TO_VALIDATE 9                          = 43
BY_COMMERCIAL_PRIORITY   SALES_READY 6 · STRATEGIC_OPPORTUNITY 8 ·
                         COMMERCIAL_WATCH 13 · TO_VALIDATE 16              = 43
BY_PUBLICATION_STATE     PUBLISHABLE 6 · VALIDATION_REQUIRED 37            = 43
EXTERNAL_MATERIAL_READY  YES 6 · NO 37                                     = 43
PER_SUPERFICIE           OPPORTUNITA 17 · RADAR 21 · SEGNALI 4 · ERRORE 1  = 43
PER_CLASSE               A 17 · B 21 · C 4 · D 1  (E declarado, 0)         = 43
BY_WINDOW_DEFINED        YES 16 · NO 27                                    = 43
BY_WINDOW_OPEN_NOW       YES 2 · UNKNOWN 41                                = 43
```

**Confirma a V0.2 em todos os números.** Zero divergências.

### O quinto eixo, que a missão não pediu e o código tem

`EXTERNAL_MATERIAL_READY` — `YES` / `VALIDATION_REQUIRED` / `NO`. Vive em
`v21_comercial.py`, com lei própria escrita:

> *«SALES_READY responde «isto vende?». Ele NÃO responde «isto pode ser enviado a um
> revendedor ou a um RTV hoje?». São perguntas diferentes, e confundi-las é o jeito mais
> rápido de pôr uma inferência nossa na mão de terceiro como se fosse recomendação
> técnica.*
> ***VENDER É UMA DECISÃO INTERNA. ENVIAR É UMA AFIRMAÇÃO PÚBLICA.***
> *A SEGUNDA PRECISA SOBREVIVER A QUEM A LER SEM NOS CONHECER.»*

E a lei que viaja com o campo: **`SALES_READY sozinho NÃO autoriza saída externa`.**

**São, portanto, cinco eixos, não quatro.** Medido abaixo.

---
### A · ELIGIBILITY_SURFACE × ACTION_STATUS

```
                    | ACT_NOW | FUTURE_PREPARATION | TO_VALIDATE | VALIDATE_NOW | WATCH | TOTAL
------------------------------------------------------------------------------------------------
ERRORE              |       · |                  · |           1 |            · |     · |     1
OPPORTUNITA         |       2 |                  · |           · |            4 |    11 |    17
RADAR               |       · |                  7 |           6 |            · |     8 |    21
SEGNALI             |       · |                  · |           2 |            · |     2 |     4
------------------------------------------------------------------------------------------------
TOTAL               |       2 |                  7 |           9 |            4 |    21 |    43
```

### B · ELIGIBILITY_CLASS × ACTION_STATUS

```
                  | ACT_NOW | FUTURE_PREPARATION | TO_VALIDATE | VALIDATE_NOW | WATCH | TOTAL
----------------------------------------------------------------------------------------------
A                 |       2 |                  · |           · |            4 |    11 |    17
B                 |       · |                  7 |           6 |            · |     8 |    21
C                 |       · |                  · |           2 |            · |     2 |     4
D                 |       · |                  · |           1 |            · |     · |     1
----------------------------------------------------------------------------------------------
TOTAL             |       2 |                  7 |           9 |            4 |    21 |    43
```

### C · ELIGIBILITY_SURFACE × COMMERCIAL_PRIORITY

```
                    | COMMERCIAL_WATCH | SALES_READY | STRATEGIC_OPPORTUNITY | TO_VALIDATE | TOTAL
---------------------------------------------------------------------------------------------------
ERRORE              |                · |           · |                     · |           1 |     1
OPPORTUNITA         |                · |           6 |                     · |          11 |    17
RADAR               |               13 |           · |                     8 |           · |    21
SEGNALI             |                · |           · |                     · |           4 |     4
---------------------------------------------------------------------------------------------------
TOTAL               |               13 |           6 |                     8 |          16 |    43
```

### D · ACTION_STATUS × COMMERCIAL_PRIORITY

```
                   | COMMERCIAL_WATCH | SALES_READY | STRATEGIC_OPPORTUNITY | TO_VALIDATE | TOTAL
--------------------------------------------------------------------------------------------------
ACT_NOW            |                · |           2 |                     · |           · |     2
FUTURE_PREPARATION |                · |           · |                     7 |           · |     7
TO_VALIDATE        |                5 |           · |                     1 |           3 |     9
VALIDATE_NOW       |                · |           4 |                     · |           · |     4
WATCH              |                8 |           · |                     · |          13 |    21
--------------------------------------------------------------------------------------------------
TOTAL              |               13 |           6 |                     8 |          16 |    43
```

### E · COMMERCIAL_PRIORITY × PUBLICATION_STATE

```
                      | PUBLISHABLE | VALIDATION_REQUIRED | TOTAL
------------------------------------------------------------------
COMMERCIAL_WATCH      |           · |                  13 |    13
SALES_READY           |           6 |                   · |     6
STRATEGIC_OPPORTUNITY |           · |                   8 |     8
TO_VALIDATE           |           · |                  16 |    16
------------------------------------------------------------------
TOTAL                 |           6 |                  37 |    43
```

### F · ELIGIBILITY_SURFACE × PUBLICATION_STATE

```
                    | PUBLISHABLE | VALIDATION_REQUIRED | TOTAL
----------------------------------------------------------------
ERRORE              |           · |                   1 |     1
OPPORTUNITA         |           6 |                  11 |    17
RADAR               |           · |                  21 |    21
SEGNALI             |           · |                   4 |     4
----------------------------------------------------------------
TOTAL               |           6 |                  37 |    43
```

### G · ACTION_STATUS × PUBLICATION_STATE

```
                   | PUBLISHABLE | VALIDATION_REQUIRED | TOTAL
---------------------------------------------------------------
ACT_NOW            |           2 |                   · |     2
FUTURE_PREPARATION |           · |                   7 |     7
TO_VALIDATE        |           · |                   9 |     9
VALIDATE_NOW       |           4 |                   · |     4
WATCH              |           · |                  21 |    21
---------------------------------------------------------------
TOTAL              |           6 |                  37 |    43
```

### H · WINDOW_DEFINED × ACTION_STATUS

```
               | ACT_NOW | FUTURE_PREPARATION | TO_VALIDATE | VALIDATE_NOW | WATCH | TOTAL
-------------------------------------------------------------------------------------------
NO             |       · |                  7 |           9 |            · |    11 |    27
YES            |       2 |                  · |           · |            4 |    10 |    16
-------------------------------------------------------------------------------------------
TOTAL          |       2 |                  7 |           9 |            4 |    21 |    43
```

### I · WINDOW_OPEN_NOW × ACTION_STATUS

```
                | ACT_NOW | FUTURE_PREPARATION | TO_VALIDATE | VALIDATE_NOW | WATCH | TOTAL
--------------------------------------------------------------------------------------------
UNKNOWN         |       · |                  7 |           9 |            4 |    21 |    41
YES             |       2 |                  · |           · |            · |     · |     2
--------------------------------------------------------------------------------------------
TOTAL           |       2 |                  7 |           9 |            4 |    21 |    43
```

### J · WINDOW_OPEN_NOW × COMMERCIAL_PRIORITY

```
                | COMMERCIAL_WATCH | SALES_READY | STRATEGIC_OPPORTUNITY | TO_VALIDATE | TOTAL
-----------------------------------------------------------------------------------------------
UNKNOWN         |               13 |           4 |                     8 |          16 |    41
YES             |                · |           2 |                     · |           · |     2
-----------------------------------------------------------------------------------------------
TOTAL           |               13 |           6 |                     8 |          16 |    43
```

### K · PUBLICATION_STATE × EXTERNAL_MATERIAL_READY

```
                    |   NO |  YES | TOTAL
------------------------------------------
PUBLISHABLE         |    · |    6 |     6
VALIDATION_REQUIRED |   37 |    · |    37
------------------------------------------
TOTAL               |   37 |    6 |    43
```

---

## §3 · OS CONJUNTOS, POR `CASE_ID`

Contagens iguais não são conjuntos iguais. Aqui estão os conjuntos.

```
OPPORTUNITA / CLASS_A   n=17
  OPP_169BD86DB324 OPP_195919127658 OPP_3C8C3960CC66 OPP_48C2731BAFD1
  OPP_5F31A63F844D OPP_75C37DED9160 OPP_81C053E9DCD3 OPP_9C600748BB1B
  OPP_C1735138E362 OPP_C5F7888EC524 OPP_D11664591168 OPP_D9B21D005CC3
  OPP_DF0C3648893A OPP_E138ECDFD7D2 OPP_EA2AE1EFB775 OPP_F6EEF5B32F65
  OPP_F8106D5E1767

SALES_READY / PUBLISHABLE / EXTERNAL_YES   n=6   ← os TRÊS são o MESMO conjunto
  OPP_3C8C3960CC66 OPP_5F31A63F844D OPP_75C37DED9160
  OPP_9C600748BB1B OPP_EA2AE1EFB775 OPP_F8106D5E1767

ACT_NOW / WINDOW_OPEN_YES   n=2   ← os DOIS são o MESMO conjunto
  OPP_5F31A63F844D OPP_F8106D5E1767
```

### As relações, calculadas por conjunto

```
CLASS_A          ==  OPPORTUNITA        idênticos, n=17
SALES_READY      ==  PUBLISHABLE        idênticos, n=6
SALES_READY      ==  EXTERNAL_YES       idênticos, n=6
ACT_NOW          ==  WINDOW_OPEN_YES    idênticos, n=2

ACT_NOW          ⊂   SALES_READY        próprio, 2 de 6
SALES_READY      ⊂   OPPORTUNITA        próprio, 6 de 17
ACT_NOW          ⊂   OPPORTUNITA        próprio, 2 de 17
```

> **A cadeia é um encaixe estrito, sem uma única exceção em 43 casos:**
>
> ```
> ACT_NOW (2)  ⊂  SALES_READY = PUBLISHABLE = EXTERNAL_YES (6)  ⊂  OPPORTUNITA = A (17)  ⊂  43
> ```

---

## §4 · SALES_READY — a quarentena semântica, medida

**Não renomeado. Não apagado. Não corrigido.** Medido.

### §4.1 · A condição exata que o produz

`scripts/v21_comercial.py`, ramo 4 — «problema agronómico declarado: o caminho da venda»:

```python
if o.get('TARGET'):                                    # há alvo declarado
    if not rotulo_par:            return TO_VALIDATE   # PRODUCT_LINK_STATE != VERIFIED_LABEL_MATCH
    if need not in POSITIVA:      return SALES_PREPARE/TO_VALIDATE
    if not geo_ok:                return SALES_PREPARE # CLAIM_GEOGRAPHY_HOLDS is not True
    if quando in ('ACT_NOW', 'PREPARE_NOW'):
                                  return SALES_READY, ['ALL_GATES_CLOSE']
    return SALES_PREPARE, ['TIME_NOT_PRECISE']
```

Cinco condições, todas necessárias: **alvo declarado · rótulo verificado no par ·
necessidade positiva · geografia que se sustenta · `COMMERCIAL_WINDOW` em
`ACT_NOW|PREPARE_NOW`**.

**É uma condição composta e independente por construção** — não lê `PUBLICATION_STATE`,
não lê `STATUS`, não lê `SUPERFICIE`.

### §4.2 · Os seis casos

| CASE_ID | arq. | classe / superfície | ACTION_STATUS | PUBLICATION | janela | aberta? | need | geo | prod. | evid. |
|---|---|---|---|---|---|---|---|---|---|---|
| `OPP_3C8C3960CC66` | O1 | A / OPPORTUNITA | VALIDATE_NOW | PUBLISHABLE | YES | **UNKNOWN** | POSITIVE_PRESSURE | ✓ | 1 | 8 |
| `OPP_5F31A63F844D` | O1 | A / OPPORTUNITA | **ACT_NOW** | PUBLISHABLE | YES | **YES** | POSITIVE_PRESSURE | ✓ | 2 | 14 |
| `OPP_75C37DED9160` | O1 | A / OPPORTUNITA | VALIDATE_NOW | PUBLISHABLE | YES | **UNKNOWN** | POSITIVE_PRESSURE | ✓ | 2 | 9 |
| `OPP_9C600748BB1B` | O1 | A / OPPORTUNITA | VALIDATE_NOW | PUBLISHABLE | YES | **UNKNOWN** | POSITIVE_PRESSURE | ✓ | 1 | 7 |
| `OPP_EA2AE1EFB775` | O1 | A / OPPORTUNITA | VALIDATE_NOW | PUBLISHABLE | YES | **UNKNOWN** | POSITIVE_PRESSURE | ✓ | 1 | 7 |
| `OPP_F8106D5E1767` | O1 | A / OPPORTUNITA | **ACT_NOW** | PUBLISHABLE | YES | **YES** | POSITIVE_PRESSURE | ✓ | 2 | 9 |

**Os seis são homogéneos:** todos `O1_FIELD_PRESSURE`, todos classe A, todos
`POSITIVE_PRESSURE`, todos com geografia que se sustenta, todos com
`WHY_COMMERCIAL_CODES = ['ALL_GATES_CLOSE', 'TIME_FROM_SOURCE_RECOMMENDATION']`, todos
com `COMMERCIAL_TIMING_BASIS = CURRENT_SOURCE_RECOMMENDATION`.

### §4.3 · As respostas pedidas, por conjunto

```
SALES_READY == PUBLISHABLE ?              SIM — conjuntos idênticos, n=6
SALES_READY == ACT_NOW ?                  NÃO
ACT_NOW     ⊂  SALES_READY ?              SIM — 2 de 6
SALES_READY ⊂  ACT_NOW ?                  NÃO
SALES_READY == OPPORTUNITA ?              NÃO
SALES_READY ⊂  OPPORTUNITA ?              SIM — 6 de 17
OPPORTUNITA ⊂  SALES_READY ?              NÃO
SALES_READY == EXTERNAL_MATERIAL_READY?   SIM — conjuntos idênticos, n=6
```

E, pela matriz D, `SALES_READY` decompõe-se exatamente em
**`ACT_NOW (2) ∪ VALIDATE_NOW (4)`**.

### §4.4 · O veredito da quarentena

```
SALES_READY_AUTHORITY = RESOLVED_AS_INDEPENDENT_RULE
                        with ZERO_DISCRIMINATING_POWER_ON_THIS_POPULATION
```

**A regra é defensável pelo código.** Tem cinco condições nomeadas, dono
(`scripts/v21_comercial.py`), versão (`V21-ef6e7e5f37eaa6e6`) e uma lei escrita a
separá-la explicitamente da autorização de saída externa. **Não é um rótulo solto.**

**E, nesta população, ela não distingue nada de `PUBLICATION_STATE` nem de
`EXTERNAL_MATERIAL_READY`.** Os três conjuntos são idênticos, caso a caso.

A prova de que o alinhamento é **derivação e não coincidência**:

```
EXTERNAL_BLOCKER_CODES, medido nos 43:
    ('NOT_SALES_READY',)   37       ← o ÚNICO código de bloqueio presente
    ()                      6
```

Dos oito códigos de bloqueio que `v21_comercial.py` define, **um só disparou** — e é o
que diz «o caso não é comercialmente pronto». Os outros sete — `EVIDENCE_GATE_OPEN`,
`RED_TEAM_FINDING` e os restantes — **nunca foram exercitados neste universo**.

> **`EXTERNAL_MATERIAL_READY` é, nesta safra, uma projeção de `SALES_READY`.**
> A lei que os separa está escrita e está certa. **Nunca foi testada por um caso que a
> obrigasse a discordar.**

**Consequência declarada, e é a que a missão pediu:**

```
DELIVERY_CONSUMPTION = BLOCKED  para qualquer superfície que queira consumir
                                SALES_READY, PUBLISHABLE ou EXTERNAL_MATERIAL_READY
                                como se fossem eixos independentes.

                                Não porque a regra esteja errada — porque nesta safra
                                os três dizem a mesma coisa, e uma superfície que os
                                mostrasse lado a lado exibiria três colunas iguais.
```

**Nenhuma alteração de runtime foi feita.** `SALES_READY` continua a chamar-se
`SALES_READY`.

---

## §5 · TEMPORALIDADE — o que a medição destapou

### §5.1 · Os números reconfirmados

```
TOTAL_CASES              43
BY_STATUS                ACT_NOW 2 · VALIDATE_NOW 4 · FUTURE_PREPARATION 7 ·
                         WATCH 21 · TO_VALIDATE 9
BY_WINDOW_DEFINED        YES 16 · NO 27
BY_WINDOW_OPEN_NOW       YES 2 · UNKNOWN 41
```

**E três medições que a V0.2 não tinha:**

```
DAYS_REMAINING = None    em  43 / 43        ← nenhum caso tem contagem decrescente
WINDOW_STATE = UNKNOWN   em  43 / 43        ← nenhum caso tem estado de janela
WINDOW_DEFINED=YES  mas  WINDOW_OPEN_NOW=UNKNOWN  em  14 de 16
```

> **Ter janela definida não é saber se ela está aberta.**
> Dos 16 casos com janela, **14 não sabem se ela está aberta**.

### §5.2 · As combinações contraintuitivas, e a regra que as produz

| combinação | n | regra que a produz | classificação |
|---|---|---|---|
| `ACT_NOW` com `WINDOW_OPEN_NOW ≠ YES` | **0** | — | — |
| `SALES_READY` com `WINDOW_OPEN_NOW ≠ YES` | **4** | `v21_comercial.py:282` lê `COMMERCIAL_WINDOW`, **não** `WINDOW_OPEN_NOW` | **`SEMANTIC_TENSION`** |
| `PUBLISHABLE` com `WINDOW_OPEN_NOW ≠ YES` | **4** | derivado do anterior | **`SEMANTIC_TENSION`** |
| `FUTURE_PREPARATION` sem `WINDOW_DEFINED` | **7** | `estado_temporal():217` — `if arquetipo == 'O5_REGULATORY_PREPARATION': return 'FUTURE_PREPARATION'`, **antes** de olhar para a janela | **`CONSISTENT_WITH_CONTRACT`** |

**Nenhuma é bug.** As sete de `FUTURE_PREPARATION` são o arquétipo regulatório: um prazo
europeu não precisa de janela agronómica, e o código diz-o na linha antes.

### §5.3 · O achado temporal mais importante

`estado_temporal()` decide assim:

```python
if arquetipo == 'O5_REGULATORY_PREPARATION':  return 'FUTURE_PREPARATION'
if not tem_janela or dias is None:            return 'WATCH'
if 0 <= dias <= 30:                           return 'ACT_NOW'
...
```

E logo a seguir, em `v21_oportunidades.py:762`:

```python
if o['STATUS'] == 'WATCH' and sidade is not None and sidade <= 30:
    o['STATUS'] = 'ACT_NOW'
```

**`dias` (`DAYS_REMAINING`) é `None` em 43 de 43.** Logo o ramo `0 <= dias <= 30` **nunca
executou**. Todos os casos caem em `WATCH`, e os que se tornam `ACT_NOW` tornam-se por
**`sidade` — a idade do sinal**.

> **NENHUM DOS 43 CASOS RECEBEU O SEU ESTADO TEMPORAL DE UMA JANELA.**
> Os dois `ACT_NOW` são-no porque o **sinal tem menos de 30 dias**, não porque a janela
> esteja a fechar. Que ambos tenham também `WINDOW_OPEN_NOW = YES` é verdade — e é uma
> **coincidência de dois casos**, não o mecanismo.
>
> **`TIME SINCE WE SAW IT ≠ TIME UNTIL IT CLOSES`.**
> São dois relógios, e hoje só um deles anda.

O mesmo vale para `SALES_READY`: `COMMERCIAL_WINDOW` cai no ramo `SIGNAL_DATE` porque
`DAYS_REMAINING` é nulo — e é por isso que os seis carregam
`COMMERCIAL_TIMING_BASIS = CURRENT_SOURCE_RECOMMENDATION`.

**Consequência para a Bíblia:** o §34 da V0.2 disse *«a arquitetura temporal está pronta;
o relógio que a alimenta não está»*. A medição precisa-o: **o relógio que anda é o de
frescura do sinal; o de contagem decrescente até à janela não existe em nenhum caso.**

---

## §6 · OS DONOS, MEDIDOS

Não deduzidos pelo nome do ficheiro. Lidos no código, na geração e no fluxo.

| eixo | dono medido | versão | prova |
|---|---|---|---|
| `ELIGIBILITY_CLASS` · `ELIGIBILITY_SURFACE` | **`scripts/adama_relevance.py`** | `V21-ef6e7e5f37eaa6e6` | `DONO_DA_LEI` declarado no próprio artefacto |
| `ACTION_STATUS` — `ACT_NOW`, `WATCH`, `FUTURE_PREPARATION`, `TO_VALIDATE` | **`scripts/v21_oportunidades.py`** | idem | `estado_temporal()` + a sobrescrita por portão |
| `ACTION_STATUS` — **`VALIDATE_NOW`** | **`UNKNOWN`** | — | a string **não aparece em nenhum script** do baseline |
| `COMMERCIAL_PRIORITY` | **`scripts/v21_comercial.py`** | idem | `prioridade()`, cinco ramos |
| `PUBLICATION_STATE` | **`UNKNOWN`** | idem | `meeting_snapshot.py` apenas **transporta** o campo; nenhum script o calcula |
| `EXTERNAL_MATERIAL_READY` | **`scripts/v21_comercial.py`** | idem | `EXTERNAL_LAW` + `BLOQUEIO_EXTERNO` |
| `WHY_NOW_CODES` | **`scripts/v21_oportunidades.py`** | idem | presente em **43/43** |
| `WINDOW_*` | `scripts/v21_janelas.py` (declarado em `ENGINE_VERSION`) | idem | — |

### Dois donos fora deste baseline

`VALIDATE_NOW` e `PUBLICATION_STATE` chegam prontos no pacote
`build/ITALY-REALITY-HANDOFF-V2.1/DESIGN-INGEST/OPPORTUNITIES.json` — que **está no
`.gitignore`** (linha 49) e é reconstruído pela cadeia a partir da linhagem
`opportunity-commercial-priority`.

> **Dois dos cinco eixos têm o seu dono FORA do baseline medido.**
> Não é uma falha da medição: é o estado real. `OWNER = UNKNOWN` é a resposta correta, e
> é a que fica escrita.

---

## §7 · O VEREDITO SOBRE C-06

A V0.2 descreveu `C-06` como **duas leis a discordar sobre o que é uma oportunidade** —
uma disputa por um dono. **A medição derruba essa descrição.**

```
C-06_VERDICT = PARTIAL_OVERLAP
               (ortogonalidade estrutural entre A e B,
                com DERIVAÇÃO e COLAPSO dentro da Linha A)
```

### §7.1 · A pergunta que cada eixo efetivamente responde

Escritas a partir do código e dos contratos, não do nome:

| eixo | pergunta efetiva | evidência |
|---|---|---|
| `ELIGIBILITY_CLASS` / `SURFACE` | **«este caso tem ligação factual defensável com pelo menos um produto ADAMA?»** | `CADEIA_EXIGIDA` de 8 elos; `SO_A_PUBLICA` |
| `ACTION_STATUS` | **«em que estado temporal-ou-de-portão este caso está?»** — e são **duas** perguntas num campo só | `estado_temporal()` **sobrescrito** por `TO_VALIDATE` quando um portão falha |
| `COMMERCIAL_PRIORITY` | **«isto vende, e porquê?»** | `v21_comercial.py`, cinco ramos nomeados |
| `PUBLICATION_STATE` | **«pode ser publicado?»** | `UNKNOWN` — chega pronto |
| `EXTERNAL_MATERIAL_READY` | **«pode sair da ADAMA para um terceiro?»** | `EXTERNAL_LAW`, explícita |

**Quatro perguntas diferentes. Confirmado.** E uma correção ao próprio enunciado: o eixo
`ACTION_STATUS` **não responde a uma pergunta só** — `TO_VALIDATE` não é um estado
temporal, é uma **falha de portão que sobrescreve o estado temporal**.

### §7.2 · Por que NÃO é contradição

Percorridos os 43 casos, **não existe um único par de eixos que se contradiga**. Não há
um caso `OPPORTUNITA` que a Linha A declare inelegível, nem um `SALES_READY` fora da
classe A. As duas linhas **encaixam**:

```
ACT_NOW (2) ⊂ SALES_READY (6) ⊂ OPPORTUNITA (17) ⊂ 43
```

**A Linha A nunca promove o que a Linha B recusa.** Zero exceções.

### §7.3 · O que É, então, o problema

Três coisas distintas, e nenhuma é «duas leis a discordar»:

**1 · DERIVAÇÃO não declarada.** `ELIGIBILITY_CLASS` e `ELIGIBILITY_SURFACE` são o mesmo
facto sob dois nomes: `A↔OPPORTUNITA`, `B↔RADAR`, `C↔SEGNALI`, `D↔ERRORE`, 43/43. **Um é
projeção do outro** e nada o declara.

**2 · COLAPSO de três eixos.** `SALES_READY`, `PUBLISHABLE` e `EXTERNAL_YES` são o mesmo
conjunto de 6. Declarados independentes; medidos co-extensivos.

**3 · COMPOSIÇÃO, não propriedade.** A barra imprime `17` (Linha B) e chama-lhe
«Opportunity Radar». O motor tem `ACT_NOW 2`. **Nenhum dos dois está errado** —
respondem a perguntas diferentes. O que falta é a regra de **composição**: qual eixo
governa a contagem do menu, qual governa a ordem da fila, qual governa o selo do cartão.

> **DUAS RESPOSTAS DIFERENTES NÃO SÃO UMA CONTRADIÇÃO
> SE RESPONDEM A PERGUNTAS DIFERENTES.**
>
> O que elas exigem não é um vencedor. É um **contrato de composição**.

### §7.4 · A hipótese da missão, julgada

```
HIPÓTESE   ELIGIBILITY ≠ ACTION_STATE ≠ COMMERCIAL_PRIORITY ≠ PUBLICATION_STATE

ELIGIBILITY ≠ ACTION_STATE .............. CONFIRMADA   partições diferentes (matriz A)
ELIGIBILITY ≠ COMMERCIAL_PRIORITY ....... CONFIRMADA   17 ≠ 6, encaixe próprio
ACTION_STATE ≠ COMMERCIAL_PRIORITY ...... CONFIRMADA   SALES_READY = ACT_NOW ∪ VALIDATE_NOW
COMMERCIAL_PRIORITY ≠ PUBLICATION_STATE . REFUTADA NESTA POPULAÇÃO — conjuntos idênticos
ELIGIBILITY_CLASS ≠ ELIGIBILITY_SURFACE . REFUTADA — derivação 1:1, 43/43
```

**Três confirmadas, duas refutadas.** A lei candidata **não pode ser canonizada como
está**: seria escrever como distinção estrutural aquilo que a medição mostra ser, em dois
casos, o mesmo facto com dois nomes.

---

## §8 · SOBRE O `OPPORTUNITY_SCORE`

Existe um `OPPORTUNITY_SCORE` inteiro nos 43 casos, entre **6 e 11**. A V0.2 escreveu
`L-19 · ORDERING IS EXPLAINABLE OR IT IS NOT ORDERING`. Medido, o score **não ordena**:

```
ACT_NOW              n= 2   scores 10, 11
VALIDATE_NOW         n= 4   scores 10, 10, 10, 11
WATCH                n=21   scores 8 … 11        ← contém 10 e 11
FUTURE_PREPARATION   n= 7   scores 6 … 9
TO_VALIDATE          n= 9   scores 7 … 9
```

Há casos `WATCH` com score **11** — o mais alto do universo — e casos `ACT_NOW` com
score 10. **O score não determina o estado.** E o próprio código diz porquê:

> *«A–H. Devolve a lista dos que FALHARAM. Score alto não abre portão.*
> ***UM 12 COM PORTÃO FECHADO CONTINUA SENDO UM 12 COM PORTÃO FECHADO.»***

**`L-19` está cumprida no motor.** Fica registado para não ser reaberto por engano.

---

## §9 · O QUE FICA `UNKNOWN`

| # | pergunta | consequência |
|---|---|---|
| U-25 | Quem calcula `PUBLICATION_STATE`? | o eixo da publicação não tem dono neste baseline |
| U-26 | Quem produz `VALIDATE_NOW`? A string não existe em nenhum script daqui | 4 de 43 casos com estado sem origem rastreável |
| U-27 | Por que `SALES_PREPARE` (declarado, 4 caminhos de retorno) tem 0 casos? | um estado inteiro por exercitar |
| U-28 | Por que `PER_CLASSE.E` tem 0 casos? | idem, do lado da elegibilidade |
| U-29 | Sete dos oito `BLOQUEIO_EXTERNO` nunca dispararam | a lei que separa venda de saída externa nunca foi testada |
| U-30 | `DAYS_REMAINING` nulo em 43/43 e `WINDOW_STATE` `UNKNOWN` em 43/43 | o relógio de contagem decrescente não existe |
| U-31 | 14 dos 16 com janela definida não sabem se ela está aberta | `WINDOW_DEFINED` não implica `WINDOW_OPEN_NOW` |

**Nenhum foi resolvido por inferência.**

---

## §10 · O QUE ESTA MEDIÇÃO NÃO FEZ

Não alterou portal, motor, coletores, schema, Supabase, Vercel, Apify nem um único dos 43
casos canónicos. Não escolheu entre Linha A e Linha B. Não renomeou `SALES_READY`. Não
mapeou `ACT_NOW` para `AGIR AGORA` — **`MAPPING_TO_ENGINE` continua `NOT_MEASURED`**, e
a medição reforça porquê: `ACT_NOW` significa *«sinal com menos de 30 dias»*, que não é o
que «AGIR AGORA» diz a um leitor.

> **SIMILARIDADE LEXICAL NÃO É EQUIVALÊNCIA SEMÂNTICA.**

Não fechou nenhum Product Contract. **`PRODUCT_CONTRACT_DEPENDENCY = OPEN`.**
