# CONTRATO DE COMPOSIÇÃO DOS ESTADOS — V1

```
DOCUMENT_STATUS   DRAFT
DOCUMENT_TYPE     CORE CONSTITUTION · contrato de composição
DATE              2026-09-08
BRANCH            research/delivery-bible-v1
HEAD_INICIAL      6685655efa2d8baf20aa998a366bad8c51150e22   (= remoto, 0/0, limpa)
BASELINE          a4fb6d81681094925ccfd1638bc7386cbec6f4d4
OWNER_HEAD        fb96f49d   ← declarado pelo próprio snapshot em SOURCE_HEAD

IMPLEMENTAÇÃO 0 · RUNTIME 0 · PORTAL 0 · COLLECTION 0 · DEPLOY 0 · MERGE 0
```

> **Este contrato não escolhe vencedores.**
> Diz **qual pergunta cada estado responde**, **quem tem autoridade para a responder**, e
> **como as respostas convivem sem uma apagar a outra**.

---

## §1 · A CORREÇÃO QUE ABRE ESTE DOCUMENTO

**D0.3 atribuiu uma regra ao ficheiro errado, e este contrato corrige-o antes de
construir por cima.**

D0.3 concluiu que *«nenhum dos 43 casos recebeu o seu estado temporal de uma janela; os
dois `ACT_NOW` são-no pela idade do sinal»*. A conclusão assentava em
`scripts/v21_oportunidades.py` **lido no baseline `a4fb6d8`**.

**Medido agora:**

| | `a4fb6d8` (ramo do portal) | `fb96f49d` (`SOURCE_HEAD` do snapshot) |
|---|---|---|
| `scripts/v21_oportunidades.py` | **1.216 linhas** | **2.475 linhas** |
| contém `estado_de_acao()` | **NÃO** | **SIM** |
| contém `VALIDATE_NOW` | **NÃO** | **SIM** |

**O ramo do portal carrega uma cópia obsoleta do gerador, com metade do tamanho.**
O snapshot foi produzido por `fb96f49d`, não pelo script que está ao lado dele.

### A lei que este erro compra

```
L-29 · SCRIPT PRESENT IN THE BASELINE ≠ SCRIPT THAT PRODUCED THE DATA

    É o par simétrico da regra que a própria missão escreveu —
    FIELD PRESENT IN SNAPSHOT ≠ OWNER PROVEN.
    Um artefacto declara o seu SOURCE_HEAD. Ler o código ao lado do dado,
    em vez do código que o dado nomeia, é ler o vizinho e chamar-lhe autor.
```

### O que a correção muda, e o que não muda

**Não muda nenhum número.** `DAYS_REMAINING` continua nulo em 43/43,
`WINDOW_OPEN_NOW` continua `UNKNOWN` em 41/43. A medição dos **dados** estava certa.

**Muda a atribuição da regra, e para melhor.** O dono real exige **cinco elos** para
`ACT_NOW`, e recusa explicitamente a idade do sinal sozinha:

```
SINAL_ATUAL  +  JANELA_DEFINIDA  +  JANELA_ABERTA_AGORA
             +  VINCULO_COM_PORTFOLIO  +  TEMPO_PARA_ACAO
```

E o comentário que acompanha a regra é, palavra por palavra, a lei que D0.3 tinha
derivado sozinha:

> *«A DATA DO BOLETIM DIZ QUE O SINAL É CORRENTE.
> ELA NÃO DIZ QUANDO SE PULVERIZA. SÃO DOIS RELÓGIOS.»*

**Verificação independente:** transcrita a regra de `fb96f49d` e reexecutada sobre os 43
casos do snapshot, ela reproduz **34 de 34** dos casos não sobrescritos. Os 9 que diferem
são exatamente os 9 `TO_VALIDATE` — ver §4.

> **`L-28` de V0.3 mantém-se inteira.** O que muda é o culpado: não é o motor que confunde
> os dois relógios — **é a cópia obsoleta que ainda vive no ramo do portal.**

---

## §2 · AS SETE PERGUNTAS

A missão hipotetizou seis. A medição encontrou **sete** — porque `ELIGIBILITY` se abre em
dois campos e `STATUS` carrega dois conceitos.

| # | dimensão | **a pergunta que ela responde** | dono | provado |
|---|---|---|---|---|
| 1 | `ELIGIBILITY_CLASS` | *este caso tem ligação factual defensável com pelo menos um produto ADAMA?* | `adama_relevance.py` | ✅ |
| 2 | `ELIGIBILITY_SURFACE` | *em que superfície esta classe se apresenta?* | `adama_relevance.py` | ✅ **derivado de 1** |
| 3 | `TEMPORAL_STATE` | *o que sabemos sobre o momento real da janela e da ação?* | `v21_oportunidades.py::estado_de_acao` | ✅ |
| 4 | `VALIDATION_GATE_STATE` | *que portão factual falhou e impede a promoção?* | `v21_oportunidades.py::portoes` + `red_team` | ✅ |
| 5 | `COMMERCIAL_PRIORITY` | *isto vende, e porquê?* | `v21_comercial.py::prioridade` | ✅ |
| 6 | `EXTERNAL_MATERIAL_READY` | *pode sair da ADAMA para RTV, revenda ou terceiro?* | `v21_comercial.py::externo` | ✅ |
| 7 | `PUBLICATION_STATE` | *pode atravessar do acervo para o publicável?* | **`v21_catraca.py`** | ✅ |

**Sete perguntas. Sete donos. Todos provados.**
`U-25` e `U-26` de D0.3 estão **resolvidos** — ver §3.

---

## §3 · GENEALOGIA — os dois `UNKNOWN` de D0.3, resolvidos

### §3.1 · `PUBLICATION_STATE` — dono encontrado

```
OWNER        scripts/v21_catraca.py
BRANCH       claude/opportunity-commercial-priority-v1 · claude/trilha-universal-inteligencia-a5rx9d
RULE         A CATRACA — «a porta única entre o acervo e o publicável»
INPUTS       EXTERNAL_MATERIAL_READY  +  5 etapas obrigatórias do MATERIAL:
             IDENTITY_PROVENANCE · NORMALIZATION · CLASSIFICATION ·
             MISSION_RULER · RELATION_EXTRACTION
DERIVED_FROM EXTERNAL_MATERIAL_READY — **e a derivação é DECLARADA**
```

Citação do próprio ficheiro:

> *«`PUBLICATION_STATE` nasce de `EXTERNAL_MATERIAL_READY`, que é decisão de
> `v21_comercial.externo()` e continua sendo dele. A catraca só pode REBAIXAR o que aquele
> dono já decidiu.»*

E a propriedade que ela garante, com teste:

> ***«A CATRACA SÓ SEGURA. NUNCA EMPURRA.»***
> *«O teste `test_catraca_nunca_promove` existe para que essa propriedade seja verificada,
> não prometida.»*

**Isto resolve o mistério da igualdade de conjuntos.**
`SALES_READY == PUBLISHABLE == EXTERNAL_YES` **não é coincidência**: é uma **cadeia de
derivação declarada**, com um único passo que pode rebaixar e nenhum que pode promover.

```
COMMERCIAL_PRIORITY  ──▶  EXTERNAL_MATERIAL_READY  ──▶  PUBLICATION_STATE
    (vende?)                  (pode sair?)                 (pode atravessar?)
                          só REBAIXA               só REBAIXA
```

Nos 43, nenhum dos dois passos rebaixou nada. **Por isso os três conjuntos coincidem.**

### §3.2 · `VALIDATE_NOW` — dono e semântica encontrados

```
OWNER      scripts/v21_oportunidades.py::estado_de_acao, em fb96f49d
NASCEU EM  2026-09-03 · caa69379
           «o cartao para de dizer ACT NOW quando nao ha janela, e passa a dizer
            o que falta»
SEMÂNTICA  TEMPORAL — e é o estado de quem tem tudo MENOS a janela
```

A definição, verbatim:

> *«Sem janela, o estado honesto NÃO é `WATCH` — o serviço mandou intervir, e ignorar
> isso seria outra mentira, de sinal contrário. É `VALIDATE_NOW`: há necessidade declarada
> e produto ligado, e o que falta é a janela desta região.*
> ***O QUE FALTA TEM NOME. «NÃO SEI» COM ENDEREÇO É TRABALHO; SEM ENDEREÇO, É DESCULPA.»***

**`VALIDATE_NOW` é um estado TEMPORAL, não de validação.** O nome engana; a regra não.

E o commit que o criou nomeia o defeito que ele veio corrigir — **o mesmo que D0.3
mediu**: `ACT_NOW` emitido a partir da idade do sinal, com «no canonical window linked»
no mesmo cartão.

```
VALIDATE_NOW_AUTHORITY = RESOLVED
PUBLICATION_STATE_OWNER = scripts/v21_catraca.py   (PROVEN)
```

### §3.3 · `ELIGIBILITY_SURFACE` — derivação declarada, e lossy

```python
SUPERFICIE = {'A':'OPPORTUNITA','B':'RADAR','C':'SEGNALI','D':'ERRORE','E':'ERRORE'}
```

**Não são dois donos silenciosos.** É **um dono e uma projeção declarada**, na linha 194
de `adama_relevance.py`. `L-27` de V0.3 aplica-se — e resolve-se: a derivação **existe e
está escrita**.

**Mas é lossy, e isso é novo:** `D` e `E` mapeiam ambos para `ERRORE`. **De `ERRORE` não
se recupera a classe.**

```
L-30 · UMA PROJEÇÃO DECLARADA PODE PERDER INFORMAÇÃO, E TEM DE DIZER QUE PERDE.
       ONE FACT → ONE OWNER → MANY DECLARED PROJECTIONS é permitido.
       Uma projeção NÃO-INJETIVA obriga o consumidor a ir ao original quando
       a distinção importa. Consumir só a projeção e perguntar «foi D ou E?»
       é a pergunta que ela não pode responder.
```

---

## §4 · `STATUS` — um campo, dois conceitos, e o override

### §4.1 · O que está sobreposto

```python
STATUS = estado_de_acao(o)              # → TEMPORAL_STATE
...
if OPPORTUNITY_STATE == CANDIDATA:
    STATUS = 'TO_VALIDATE' if falhas else STATUS     # → VALIDATION_GATE_STATE
```

**`ACTION_STATUS` mistura DOIS conceitos.** `ACT_NOW`, `PREPARE_NOW`,
`FUTURE_PREPARATION`, `VALIDATE_NOW` e `WATCH` são temporais. **`TO_VALIDATE` não é**: é
uma falha de portão que **sobrescreve** o valor temporal no mesmo campo.

```
L-31 · OVERWRITE ≠ COMPOSITION
       Dois conceitos num campo só não compõem: um apaga o outro.
       Composição preserva os dois valores e declara a relação entre eles.
```

### §4.2 · A informação perdida — medida, não suposta

Para os 9 casos `TO_VALIDATE`, reexecutou-se a lei do dono sobre os campos que o
snapshot **já persiste** (`SIGNAL_AGE_DAYS`, `DAYS_REMAINING`, `WINDOW_*`,
`NEED_DIRECTION`, `TARGET`, `PRODUCT_LINK_STATE`, `COMMERCIAL_PRODUCT_COUNT`,
`ARCHETYPE`):

```
TEMPORAL_STATE_AFTER_OVERRIDE = RECOVERABLE_BY_RE_EXECUTION
    9 / 9 recuperados       valor recuperado: WATCH em 9/9
    34 / 34 dos não-sobrescritos reproduzem exatamente
```

**A informação não se perdeu nesta safra** — mas **não está no campo**, e a recuperação
exige **reexecutar a lei**, não inferir.

```
L-32 · RECONSTRUÇÃO POR REEXECUÇÃO NÃO É INFERÊNCIA — E NÃO É DO CASCO.
       Um script de pesquisa pode reexecutar a lei do dono para recuperar um estado
       apagado. Uma superfície de entrega NÃO PODE:
       reexecutar a lei no casco é o casco a fazer inteligência (L-11).
       A entrega recebe o valor ou recebe UNKNOWN. Nunca o recalcula.
```

**E a recuperabilidade é contingente, não garantida.** Ela funciona hoje porque os
insumos viajam. Se um deles deixar de viajar, o estado temporal desaparece sem aviso —
e **nada no artefacto declara essa dependência**.

```
RUNTIME_RECONCILIATION_REQUIRED · RR-01
    separar STATUS em TEMPORAL_STATE + VALIDATION_GATE_STATE, dois campos.
    NÃO EXECUTADO NESTA MISSÃO. É trabalho da linhagem da Inteligência.
```

---

## §5 · `PUBLISHABLE` — semântica incompleta, declarada

A missão pergunta: **publicável para quem?** A medição responde: **o contrato não diz.**

`v21_catraca.py` define `PUBLICATION_STATE` como *«a porta única entre o acervo e o
publicável»* — uma fronteira **de maturidade do material**, não **de audiência**.

```
PUBLICATION_AUDIENCE = NOT_DECLARED
```

E é por isso que o eixo 6 existe e não é redundante: `EXTERNAL_MATERIAL_READY` é o que
**tem** audiência declarada — «revendedor ou RTV», com a lei:

> ***«VENDER É UMA DECISÃO INTERNA. ENVIAR É UMA AFIRMAÇÃO PÚBLICA.
> A SEGUNDA PRECISA SOBREVIVER A QUEM A LER SEM NOS CONHECER.»***

```
L-33 · PUBLISHABLE SEM AUDIÊNCIA É SEMÂNTICA INCOMPLETA.
       Todo estado de publicação declara a FRONTEIRA que autoriza:
       interno-equipa · interno-ADAMA · brief de papel · terceiro nomeado · público.
       Sem fronteira, «publicável» é uma permissão sem destinatário — e uma
       permissão sem destinatário acaba por ser lida como todas.
```

**Não corrigido aqui.** Registado como `RR-02`.

---

## §6 · `SALES_READY` — que pergunta responde, afinal

A missão pergunta se é *priority*, *readiness*, *commercial eligibility* ou *actionability*.

**A medição responde: é uma COMPOSIÇÃO, e não é prioridade.**

As cinco condições, todas necessárias:

```
TARGET declarado
  + PRODUCT_LINK_STATE == VERIFIED_LABEL_MATCH     ← elegibilidade de rótulo
  + NEED_DIRECTION ∈ POSITIVA                      ← necessidade externa
  + CLAIM_GEOGRAPHY_HOLDS is True                  ← geografia
  + COMMERCIAL_WINDOW ∈ (ACT_NOW, PREPARE_NOW)     ← tempo
  → SALES_READY
```

**Não há nenhuma ordenação.** Nenhum ramo compara casos entre si. `PRIORIDADES` é uma
tupla de **cinco estados nomeados**, não uma escala.

```
SALES_READY É:      COMMERCIAL READINESS — uma composição de quatro pré-condições
                    (rótulo · necessidade · geografia · tempo)
SALES_READY NÃO É:  prioridade · ordenação · ranking · score
                    nem autorização de saída externa (EXTERNAL_LAW é explícita)
```

> **`L-34` · O NOME DO CAMPO NÃO PROVA A SEMÂNTICA DO CAMPO.**
> `SALES_READY` vive dentro de `COMMERCIAL_PRIORITY` e **não é prioridade**.
> `VALIDATE_NOW` chama-se validação e **é temporal**.
> `TO_VALIDATE` está num campo temporal e **é validação**.
> Três nomes, três enganos, e nenhum é bug: são campos que cresceram e ficaram com o
> nome do dia em que nasceram.

**Não renomeado.** Registado como `RR-03`.

---

## §7 · O CONTRATO — quem pode o quê

### §7.1 · Matriz de autoridade

> **Não é «o campo A vence o campo B».**
> É **«o campo A tem autoridade sobre ESTA pergunta»** — e sobre nenhuma outra.
> Se duas perguntas são distintas, **não há vencedor**.

| dimensão | **pode BLOQUEAR** | **pode PROMOVER** | **NUNCA pode reescrever** |
|---|---|---|---|
| `ELIGIBILITY_CLASS` | publicação · promoção a oportunidade | — | tempo · comercial · publicação |
| `ELIGIBILITY_SURFACE` | — *(projeção)* | — | a sua própria origem |
| `TEMPORAL_STATE` | `ACT_NOW` de quem não tem janela | — | elegibilidade · comercial |
| `VALIDATION_GATE_STATE` | `OPPORTUNITY_STATE` · publicação | — | **`TEMPORAL_STATE`** ⚠️ *hoje viola* |
| `COMMERCIAL_PRIORITY` | `EXTERNAL_MATERIAL_READY` | — | elegibilidade · tempo |
| `EXTERNAL_MATERIAL_READY` | `PUBLICATION_STATE` | — | comercial |
| `PUBLICATION_STATE` | toda a entrega | **— nunca** *(«só segura»)* | tudo o resto |

**Nenhuma dimensão pode promover. Nenhuma. Em todo o contrato.**
É a propriedade mais forte encontrada, e já é lei executável num sítio
(`test_catraca_nunca_promove`).

```
L-35 · NO ESTADO DE ENTREGA, TODA A AUTORIDADE É DE BLOQUEIO.
       Um eixo pode segurar o que outro autorizou. Nenhum pode autorizar o que
       outro segurou. A promoção só existe na Inteligência, com evidência nova.
```

### §7.2 · As oito regras de composição

Testadas contra 8 casos sintéticos — §8 e `RED-TEAM-COMPOSICAO-V1.md`.

```
C1  ELEGIBILIDADE NÃO É PROMOVIDA POR URGÊNCIA.
    Um caso RADAR com janela aberta continua RADAR.

C2  ELEGIBILIDADE NÃO É PROMOVIDA POR PRONTIDÃO COMERCIAL.
    Nos 43, SALES_READY ⊂ OPPORTUNITA — e não porque o comercial promova:
    porque as duas exigem a mesma cadeia de rótulo e produto.

C3  O GATE DE VALIDAÇÃO NÃO REESCREVE O TEMPO.
    ⚠️ VIOLADA HOJE. `STATUS = TO_VALIDATE` apaga o estado temporal. RR-01.

C4  A PUBLICAÇÃO NÃO CRIA VALIDADE.
    PUBLISHABLE sobre um caso inelegível é impossível por construção.

C5  A ENTREGA EXTERNA NUNCA É MENOS RESTRITIVA QUE A INTERNA.
    EXTERNAL_DELIVERY ⊆ INTERNAL_PUBLICATION, sempre.
    Pode ser MAIS restritiva; nunca menos, e nunca por conveniência de UI.

C6  TEMPO `UNKNOWN` NÃO VIRA «AGIR AGORA».
    Um card pode existir com timing UNKNOWN. Não pode existir com timing inventado.

C7  RECÊNCIA DE SINAL NÃO É JANELA ABERTA.
    `TIME SINCE WE SAW IT ≠ TIME UNTIL IT CLOSES` (L-28).

C8  SÓ `EXTERNAL = YES` AUTORIZA MATERIAL PARA TERCEIRO.
    UNKNOWN NÃO É PERMISSÃO.
    ⚠️ Esta regra foi acrescentada PELO RED TEAM: sem ela, RT-07 passava por
    OMISSÃO em vez de por regra. Ver §8.3.
```

### §7.3 · Sete relações distintas — e nenhuma é «conflito»

```
DERIVATION          B = f(A), declarada.        ELIGIBILITY_SURFACE ← CLASS
                                                PUBLICATION_STATE ← EXTERNAL
BLOCK               B pode segurar A.           CATRACA sobre EXTERNAL
ORTHOGONAL STATE    respondem perguntas         ELIGIBILITY × TEMPORAL
                    diferentes; coexistem
NOT_APPLICABLE      a pergunta não se aplica    janela para arquétipo regulatório
UNKNOWN             a pergunta aplica-se e      WINDOW_OPEN_NOW em 41/43
                    não há resposta
SUPERSESSION        versão nova substitui,      RULE_VERSION
                    com WHY_CHANGED
CONTRADICTION       MESMA pergunta,             ← NENHUMA ENCONTRADA
                    respostas incompatíveis        em 43 casos
```

> **`L-36` · Antes de registar um `CONFLITO`, responder: as duas coisas respondem à MESMA
> pergunta?** Se não, é uma das seis relações acima — e o que falta é um contrato, não um
> vencedor. É `L-26` de V0.3, agora com as categorias nomeadas.

---

## §8 · O QUE O RED TEAM PROVOU

Detalhe em `medicoes/RED-TEAM-COMPOSICAO-V1.md`. Resumo:

```
CASOS SINTÉTICOS EXECUTADOS ....... 8   (RT-01 … RT-08)
PASSARAM ........................... 8 / 8
ENTRARAM NOS 43 .................... 0     ← SYNTHETIC_CONTRACT_TEST ≠ OBSERVED CASE
TESTE DE INDEPENDÊNCIA ............. PASS
REGRAS ACRESCENTADAS PELO RED TEAM . 1     (C8)
```

### §8.3 · O buraco que o red team encontrou no próprio contrato

`RT-07` — *material para terceiro com `EXTERNAL = UNKNOWN`* — **passou na primeira
execução**, e passou **errado**: nenhuma regra o cobria, e a ausência de proibição foi
lida como permissão.

> **UM CONTRATO QUE ACEITA POR OMISSÃO NÃO É UM CONTRATO. É UM SILÊNCIO.**

`C8` nasceu daí. Fica registado que nasceu do red team, e não da primeira escrita.

### §8.4 · O teste de independência

Nos 43 observados, `SALES_READY`, `PUBLISHABLE` e `EXTERNAL_YES` são o mesmo conjunto.
**Forçou-se a divergência sintética** e verificou-se que o contrato:

```
✅ ACEITA   SALES_READY=YES com PUBLICATION=VALIDATION_REQUIRED
            — os três valores permanecem distintos, nenhum foi «corrigido»
✅ RECUSA   EXTERNAL=YES com PUBLICATION=VALIDATION_REQUIRED   (C5)
✅ NÃO CODIFICA  SALES_READY == PUBLISHABLE como regra
```

```
L-37 · OBSERVED SET EQUALITY ≠ SEMANTIC IDENTITY.

  EVIDÊNCIA        nos 43, SALES_READY == PUBLISHABLE == EXTERNAL_YES, n=6
  CONTRAEXEMPLO    a igualdade é consequência de uma DERIVAÇÃO onde nenhum passo
                   rebaixou (§3.1). Basta UM material a falhar uma das cinco etapas
                   da catraca para PUBLISHABLE ⊊ EXTERNAL_YES. O caminho existe,
                   está escrito, e nunca foi percorrido: 7 dos 8 códigos de bloqueio
                   nunca dispararam.
  CONSEQUÊNCIA     nenhuma superfície pode tratar os três como um só campo, e
                   nenhum contrato pode codificar a igualdade.
```

---

## §9 · O QUE A ENTREGA NUNCA FAZ

```
O CASCO NUNCA:
    calcula elegibilidade · calcula tempo · decide validação · cria prioridade ·
    promove publicação · autoriza saída externa · REEXECUTA a lei de um dono
    para recuperar um estado apagado (L-32)

O CASCO RECEBE:
    a composição autorizada, com os sete valores, cada um com o seu dono e versão.
    Onde um valor não existe, recebe UNKNOWN — e mostra UNKNOWN.
```

---

## §10 · PRÉ-CONDIÇÕES PARA OS PRODUCT CONTRACTS

**Não escritos aqui.** As pré-condições, sim.

### §10.1 · Opportunity Radar — `PARCIAL`

O futuro Opportunity Card terá de separar **seis perguntas**, e a arquitetura já as tem:

```
IS OPPORTUNITY?             ELIGIBILITY_CLASS          ✅ dono provado
WHAT IS THE TIMING?         TEMPORAL_STATE             ⚠️ sobreposto com o gate (RR-01)
WHAT NEEDS VALIDATION?      VALIDATION_GATE_STATE      ⚠️ idem
COMMERCIAL READINESS?       COMMERCIAL_PRIORITY        ✅
CAN WE DISPLAY IT?          PUBLICATION_STATE          ⚠️ sem audiência (RR-02)
CAN WE SEND IT OUTSIDE?     EXTERNAL_MATERIAL_READY    ✅
```

**Nem todos aparecem na tela.** Arquitetura ≠ densidade visual — o Product Contract
futuro decide o que é 3s, 30s e 3min.

```
BLOQUEIO   RR-01 e RR-02. Um card não pode mostrar «o que falta validar» ao lado de
           «qual é o timing» enquanto os dois viverem no mesmo campo.
```

### §10.2 · Home — `PARCIAL`

A Home é uma fila. Para agrupar, precisa de um `ACTION_STATE` **vindo do dono canónico**.

```
PODE CONSUMIR HOJE   ELIGIBILITY_CLASS · COMMERCIAL_PRIORITY ·
                     EXTERNAL_MATERIAL_READY · PUBLICATION_STATE
NÃO PODE AGRUPAR     por ACTION_STATE, enquanto STATUS misturar dois conceitos
NUNCA                calcular a sua própria prioridade (H-06)
```

### §10.3 · `ACTION_STATE` derivado — requisitos, se vier a existir

**Não criado nesta missão.** Se for criado, exige:

```
OWNER · RULE_ID · RULE_VERSION · INPUTS declarados ·
FORBIDDEN INFERENCES · e a lista do que NÃO pode ser inferido a partir dele
```

E uma proibição herdada, que não se relaxa:

> **`LEGACY_STATUS.ACT_NOW` NÃO AUTORIZA SOZINHO O RÓTULO DE PRODUTO `AGIR AGORA`.**
> Requisito para um futuro `AGIR AGORA`: os **cinco elos** fechados **com
> `DAYS_REMAINING` real**, e não apenas `JANELA_ABERTA_AGORA` sobre um sinal recente.
> Hoje `DAYS_REMAINING` é nulo em 43/43. **O requisito não é satisfeito por nenhum caso.**

---

## §11 · DEPENDÊNCIAS DA BÍBLIA DA INTELIGÊNCIA

Campos cuja **autoridade semântica** a Bíblia da Entrega não pode nomear:

| campo | por que não é da Entrega |
|---|---|
| `TIME_TO_ACT` · `TIME_TO_PREPARE` | não existem; exigem `DAYS_REMAINING` real |
| `ACTION WINDOW` | exige relógio agronómico comprovado — hoje `SOURCE_IDS` vazio 29/29 |
| `WHY_NOW` | existe (43/43) mas a régua que escolhe os códigos é juízo |
| `MATURITY` · `CONFIDENCE` | réguas de evidência |
| `ADAMA RESPONSE` · `WHAT TO DO` | recomendação; exige autoridade técnica e regulatória |
| separar `STATUS` em dois campos | `RR-01` |
| declarar a audiência de `PUBLISHABLE` | `RR-02` |
| o objeto `CLAIM` | continua ausente |

### Dependência de Crop Windows — declarada, não corrigida

```
ACTION WINDOW precisa receber relógio agronómico comprovado.
    DAYS_REMAINING     null      43/43
    WINDOW_OPEN_NOW    UNKNOWN   41/43
    WINDOW_STATE       UNKNOWN   43/43
    janelas definidas sem estado aberto conhecido   14/16
    SOURCE_IDS vazio                                29/29

E os relógios NÃO PODEM ser um só campo:
    AGRONOMIC_WINDOW · WINDOW_OPEN_NOW · COMMERCIAL_LEAD_TIME ·
    TIME_TO_PREPARE · TIME_TO_ACT · SIGNAL_RECENCY
```

---

## §12 · `RUNTIME_RECONCILIATION_REQUIRED`

**Encontrado e NÃO corrigido.** Registado para a fase da Inteligência.

| id | o que | onde | por que não aqui |
|---|---|---|---|
| `RR-01` | `STATUS` mistura tempo e portão; o portão sobrescreve | `v21_oportunidades.py:1812` | é engine |
| `RR-02` | `PUBLISHABLE` sem audiência declarada | `v21_catraca.py` | é contrato de dado |
| `RR-03` | três nomes que não descrevem a semântica | `v21_comercial.py` · `v21_oportunidades.py` | renomear é migração |
| `RR-04` | cópia obsoleta do gerador no ramo do portal | `a4fb6d8:scripts/v21_oportunidades.py` | é a linhagem, não a entrega |
| `RR-05` | `SALES_PREPARE` e classe `E` declarados, população 0 | ambos | pode ser correto |

**Zero destes foi tocado.**

---

## §13 · O QUE ESTE CONTRATO NÃO FEZ

Não alterou engine, portal, collection, snapshot, schema, base de dados, migration,
produção, deploy. Não renomeou nenhum campo. Não escreveu o Product Contract de
Opportunity nem de Home. Não criou um `ACTION_STATE` canónico. Não somou nenhum caso
sintético aos 43. Não fez merge.

`PRODUCT_CONTRACT_DEPENDENCY = OPEN` · `SYNTHETIC_NOT_OBSERVED = TRUE`
