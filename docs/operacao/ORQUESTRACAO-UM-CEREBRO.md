# ORQUESTRAÇÃO — UM CÉREBRO, UM CAMINHO ATÉ À ADMISSION — C-PLAN-A

**Decisão contratual · 2026-09-10 · ramo `claude/raw-observation-identity-3jbwco`**

> **Nada foi implementado.** Zero alteração de runtime, de Admission, de READY, de schema,
> de banco, de Bíblia e de System Map. Zero migration. Este documento **mede e decide**.

Pergunta única, e a única coisa que se fecha aqui:

> **Quem coordena a corrida, quem atravessa uma unidade, e qual deve ser o ÚNICO caminho
> runtime que chega à Admission?**

---

## 0 · O ESTADO MEDIDO

| | |
|---|---|
| `BRANCH` | `claude/raw-observation-identity-3jbwco` |
| `INITIAL_HEAD` | `b1cc973fe88a7fc2ea312f6c8c9f3e4acf808538` |
| `WORKTREE` | limpa antes e depois |

`HEAD` local e `origin` coincidem com o `KNOWN HEAD` da missão. Nada a corrigir.

### Os chamadores da porta, contados por símbolo

Contagem por `import admissao` **mais** chamada real — mencionar num docstring não é chamar:

```
admissao.decidir()                RUNTIME 3   ·  PROVA/TESTE 24
admissao.pronto_para_inteligencia() RUNTIME 1 ·  PROVA/TESTE  4
```

| símbolo | linha | corre em produção? |
|---|---|---|
| `orquestrador/orquestrador.py::pela_porta` | `:138` `adm.decidir` · `:145` `adm.pronto_para_inteligencia` | **SIM** — `comunicacao-publica.yml:139` |
| `coleta/golden_path_pdf.py::pela_porta_de_admissao` | `:169` `adm.decidir` | **NÃO** — nenhum workflow o corre |
| `coleta/rota_forward_documento.py::admitir` | `:191` `admissao.decidir` | **NÃO** — nenhum chamador runtime |

---

## 1 · AS TRÊS FICHAS

### FICHA 1 · `orquestrador/orquestrador.py` — T-04

```
CALLER             orquestrador/orquestrador.py :: pela_porta (:131-155)
CALLER_OF_CALLER   correr() :: :312-316  ←  main()  ←  .github/workflows/comunicacao-publica.yml:139
RUNTIME_PRODUCTION YES — é o único dos três que um workflow chama
TEST/PROOF         não
COMPATIBILITY      não
INPUT              itens crus de `a_colheita(e)` — os JSON que o executor largou em `larga_em`
OUTPUT             LIVRO-DE-DECISOES + data/samples/PRONTO-PARA-INTELIGENCIA/<RUN_ID>.json
WHY_IT_CALLS_TODAY porque foi ele quem fechou o caminho: «a peneira existia e nada passava
                   por ela» (:73). Ele resolveu o buraco certo pelo sítio errado — ligou-se
                   à porta em vez de ligar a porta a quem atravessa a unidade.
TARGET_DISPOSITION MOVE
TARGET_CALL_PATH   T-04 → T-32 :: atravessar()   (nunca T-04 → T-50)
```

> **O segundo cérebro medido não é o T-32. É o T-04.** Ele é o único dos três que corre em
> produção, e é o único dos três que chama **as duas** funções — `decidir()` **e**
> `pronto_para_inteligencia()`. Coordenar a corrida e julgar o item são duas perguntas, e
> hoje têm a mesma boca.

### FICHA 2 · `coleta/golden_path_pdf.py`

```
CALLER             coleta/golden_path_pdf.py :: pela_porta_de_admissao (:169)
CALLER_OF_CALLER   main() por linha de comando · provas/testa_golden_path_pdf.py (único importador)
RUNTIME_PRODUCTION NO — nenhum workflow corre `coleta/golden_path_pdf.py`.
                   `system-map.yml:529` corre a PROVA dele, não ele.
TEST/PROOF         YES — reconciliação offline sobre os 49 PDF já em árvore
COMPATIBILITY      não
INPUT              os 49 PDF guardados + os 43 artefatos derivados
OUTPUT             system-map/data/golden-path-pdf.generated.json  (o mapa lê)
WHY_IT_CALLS_TODAY porque é a única estrada ponta-a-ponta que alguém conseguia correr
                   inteira, offline, sem rede nem banco. Foi construída para PROVAR que a
                   estrada fecha — e provar exigia bater na porta.
TARGET_DISPOSITION PROOF_ONLY
TARGET_CALL_PATH   continua a chamar a porta COMO PROVA, e deixa de ser contado como
                   runtime — a mesma regra que `provas/a_fronteira_da_coleta.py:246` já
                   aplica ao excluir `provas/` e `tests/` da conta.
                   O trabalho OPERACIONAL dele (49 PDF → derivar → porta) passa a ser
                   T-04 a distribuir 49 unidades por T-32.
                   Quem recebe a saída dele NÃO muda: é o System Map, e já é hoje.
```

`GOLDEN_PATH_PDF_ROLE = PROOF` — medido, não opinado. **Não se remove nada nesta missão.**

### FICHA 3 · `coleta/rota_forward_documento.py` — T-32

```
CALLER             coleta/rota_forward_documento.py :: admitir (:191)
CALLER_OF_CALLER   atravessar() (:339)  ←  NINGUÉM EM RUNTIME
                   tests/test_m2_rota_forward.py:266,298,427,469  (teste)
                   provas/a_rota_m2_atravessa.py — que DELIBERADAMENTE não a chama (:359)
RUNTIME_PRODUCTION NO
TEST/PROOF         YES, hoje é só isso
COMPATIBILITY      não
INPUT              uma UNIDADE DE TRABALHO: {RAW_ASSET_ID, PDF, SOURCE_ID, ROUTE_CLASS_ID, ...}
OUTPUT             {DERIVED, STRUCTURED, ADMISSION} + linhas em `etapa_da_corrida`
WHY_IT_CALLS_TODAY porque é a única peça que TEM a unidade no momento em que a porta faz
                   sentido: ela acabou de derivar e de estruturar aquele item.
TARGET_DISPOSITION KEEP — e passa a ser o ÚNICO
TARGET_CALL_PATH   T-04 → T-32 → T-40 → T-42 → T-50 → T-52
```

> `T32_CALLERS_CURRENT = 0`. **A peça eleita para ser o caminho único é hoje órfã.** Não
> está errada; está desligada. Isso não é argumento contra ela — é a medida do trabalho.

---

## 2 · A PERGUNTA PRINCIPAL — T-32 → T-50 confirma-se, e com uma ressalva medida

A missão manda não escolher porque a arquitetura escreveu. Então mediu-se: montou-se o
item **exatamente** como cada chamador o monta, e perguntou-se à porta.

```
T-32  ·  rota_forward_documento.py:182-189
  chaves      captured_at · id · raw_asset_id · source_id · texto · url
  ESTAGIO     ESTAGIO_DESCONHECIDO
  perguntas   legivel · origem · TEMPO DO FATO
  resultado   NAO_SEI  ·  regra «tempo do fato»

T-50-via-golden-path  ·  golden_path_pdf.py:149-167
  chaves      artifact_type · parent_artifact_id · source_location · fact_location · ...
  ESTAGIO     DOCUMENTO
  perguntas   legivel · origem · LINHAGEM
  resultado   passa a linhagem; só depois é medido pelo vocabulário do universo
```

> ## T-32 TEM A LINHAGEM E NÃO A DECLARA.
> A unidade carrega `RAW_ASSET_ID` e, depois de derivar, `DERIVED_SHA256` (`:320`). O item
> que ela entrega à porta **deixa os dois de fora** — não põe `artifact_type` nem
> `parent_artifact_id`. A porta então não a reconhece como `DOCUMENTO`, aplica a régua do
> FATO e devolve `NAO_SEI` por «tempo do fato».

É **exatamente** o defeito COL-LAW-502 que a admissão já corrigiu — *«43 textos derivados
saíram NAO_SEI porque a porta lhes perguntava quando o fato aconteceu»* (`admissao.py:203`).
T-32 recai nele por não falar a língua da porta.

**Veredito.** `T-32 → T-50` **CONFIRMA-SE** como caminho operacional único: é a única peça
que possui a unidade e a linhagem no momento certo. Mas:

```
T32_ADMISSION_INPUTS_COMPLETE      = NO   (medido)
T32_CAN_CALL_ADMISSION_WITHOUT_LINEAGE = YES hoje  →  alvo NO
```

A correção é de **contrato de item**, não de arquitetura: declarar `artifact_type` e
`parent_*` no item que já os tem ao lado. Não é para fazer nesta missão.

---

## 3 · ONDE ENTRA O T-52

Medido pelo próprio censo da fronteira, que corre em CI (`system-map.yml:558`):

```
CONTRATO     COL-LAW-043 · 11 campos
DONO         admissao/admissao.py :: pronto_para_inteligencia()   (construtor único, F3 PASS)
PRODUTORES   1 em runtime: orquestrador/orquestrador.py
CONSUMIDORES 0 — e o destino declarado nem existe
```

`READY_CALLERS_CURRENT = 1` · `READY_TARGET_CALLER = T-32`, **imediatamente depois de um
`SIM` do T-50**, dentro da mesma unidade.

O construtor **não muda de dono**: continua a ser T-50. Muda a boca que o chama.

T-32 declara hoje *«NÃO emite READY … o contrato de saída exige `ADMITIDO_POR`»* (`:26-32`).
Isso era verdade **antes** de `admitir()` existir. `admitir()` devolve a `Decisao`, e
`ADMITIDO_POR` nasce dela (`admissao.py:446`). **O bloqueio que o docstring nomeia dissolve-se
no instante em que `admitir()` retorna.** Ler os 11 campos contra a unidade do T-32:

| origem | campos |
|---|---|
| a decisão | `ESTADO` · `ITEM_ID` · `UNIVERSO` · `CORRIDA` · `ADMITIDO_POR` |
| a unidade do T-32 | `TEXTO` · `SOURCE_ID` · `CAPTURED_AT` |
| ausentes → `NAO SEI` | `SOURCE_LOCATION` · `FACT_LOCATION` · `FACT_TIME` |

**Se três `NAO SEI` são um READY aceitável é pergunta da C-PLAN-C, não desta.** Aqui fecha-se
só a direcção: **T-04 nunca constrói READY; T-32 chama, T-50 constrói.**

---

## 4 · O UNIVERSO — três escritores, um dono

```
pedido/pedido.py:67    ALVOS = {T1 … T13}         o atlas
pedido/pedido.py:134   alvo_de(texto)             traduz, e NUNCA adivinha:
                                                  não reconhecendo, levanta PedidoInvalido
pedido/pedido.py:169   Pedido.__post_init__       valida na construção
orquestrador.py:315    pela_porta(itens, p.alvo,…)   T-04 CARREGA, não escolhe
```

E os outros dois inventam-no:

```
rota_forward_documento.py:68   UNIVERSO_PADRAO = 'T3'   ← o defeito conhecido
golden_path_pdf.py:57          UNIVERSO = "T7"          ← constante de módulo
```

O comentário do T-32 já sabe a resposta certa e não a impõe: *«Vem de fora quando o
chamador o souber; não se inventa»* (`:67`). **Um valor por omissão é exatamente inventá-lo
quando o chamador não soube.**

```
UNIVERSE_CURRENT_OWNER  3 escritores · 1 dono legítimo (Pedido.alvo)
UNIVERSE_TARGET_OWNER   T-02  ·  pedido/pedido.py :: Pedido.alvo
UNIVERSE_TARGET_INPUT_PATH
    Pedido.alvo  →  Plano.pedido.alvo  →  T-04  →  atravessar(universo=…)
                 →  admitir(universo=…)  →  admissao.decidir(item, universo)
```

`UNIVERSO_PADRAO` deixa de ter valor por omissão e passa a **parâmetro obrigatório**. Uma
chamada sem universo tem de rebentar, como `alvo_de()` já rebenta — a casa já escolheu esse
comportamento uma vez.

---

## 5 · ROUTE POLICY ≠ ADMISSION UNIVERSE — e hoje são o mesmo campo

Medido, e é a confusão que a missão manda evitar:

```python
# pedido/receitas.py:218
execs = EXECUTORES.get(p.alvo, [])          # QUAL EXECUTOR   ← indexado pelo universo
# orquestrador/orquestrador.py:315
r = pela_porta(itens, p.alvo, …)            # QUAL UNIVERSO   ← o mesmo campo
```

`p.alvo` responde às duas perguntas ao mesmo tempo. Funciona hoje porque há **um** executor
por universo (`EXECUTORES` tem 4 chaves, uma entrada cada). Deixa de funcionar no dia em
que dois executores servirem o mesmo universo, ou um executor servir dois.

**São duas decisões, com dois donos:**

| decisão | dono alvo | onde vive |
|---|---|---|
| que universo de admissão aplicar | **T-02** | `Pedido.alvo` |
| que executor usar | **T-06** | `receitas.py::EXECUTORES` |
| que rota preferir dentro do executor | **T-05** | ⚠️ **sem dono hoje** |

`custo` está **declarado** em cada executor (`gratuito`, `pago quando passa pela rota Apify`)
e **ninguém o ordena**: `orquestrador.py:225` faz `plano.executores[0]` — ordem de lista, não
política. A COL-LAW-018 manda «a rota mais barata capaz vem primeiro»; hoje quem manda é o
índice zero. **Enquanto houver um executor por universo isto não produz erro** — produz uma
lei sem enforcement.

---

## 6 · EXECUTOR SELECTION

```
EXECUTOR_SELECTION_OWNER
  hoje    PARTIDO — registry em pedido/receitas.py:58 · escolha em orquestrador.py:225
  alvo    T-06 resolve · T-04 pergunta
```

Confirma-se o alvo da V1.1: T-04 pergunta, T-06 responde. T-04 não indexa lista.

---

## 7 · RETRY — quem decide hoje é ninguém

```
orquestrador/orquestrador.py   ZERO retry. subprocess.run(..., timeout=1800), uma vez.
                               Falhou → STATUS=FAILED. Não repete, não escala, não pergunta.
rota_forward_documento.py:75   _tentativa() é CONTADOR, não decisão. Só evita colisão na
                               chave (run_id, etapa, tentativa). Nunca re-executa nada.
coleta/coletor.py:103,137      _curl(tentativas=4) — transporte, e NUNCA para POST/PUT/
                               PATCH/DELETE: «pedi e não sei o que houve» tem tipo próprio
                               (PostTalvezCriado, :90).
italy_pilot_collect.mjs:70     baixar(tentativas=2), só para a lista TRANSITORIOS.
```

```
GLOBAL_RETRY_OWNER              hoje 0 (ninguém)  ·  alvo T-04
EXECUTOR_LOCAL_RETRY_BOUNDARY   a fronteira é: MUDA O PLANO DA CORRIDA?

  não muda  →  do EXECUTOR: reenviar o mesmo pedido ao mesmo endereço por falha de
               transporte, com limite declarado e lista fechada de códigos.
               É o que `coletor.py` e `baixar()` já fazem, e está certo.
  muda      →  do T-04: re-executar um executor, trocar de rota, reabrir uma unidade,
               decidir circuit breaker (COL-LAW-026, hoje `IT: ABSENT`).
```

Nenhum retry existente muda de dono. O que muda é que **passa a haver dono para o que
hoje não tem** — e isso é criar o dono, não tirá-lo de ninguém.

---

## 8 · O CALL GRAPH ALVO — só arestas provadas

```
T-02  REQUEST            pedido/pedido.py :: Pedido            (alvo = UNIVERSO)
  ↓
T-03  PLAN               pedido/receitas.py :: resolver → Plano
  ↓
T-04  ORCHESTRATOR       orquestrador/orquestrador.py :: correr
  │                      coordena · assina o recibo · decide retry global
  │                      NÃO julga item · NÃO constrói READY · NÃO escolhe universo
  ├─ T-05  route policy      preferência de rota dentro do executor   ⚠️ SEM DONO HOJE
  ├─ T-06  executor registry pedido/receitas.py :: EXECUTORES
  ├─ T-1x  acquisition       o executor que T-06 resolveu (subprocess)
  ├─ T-30  ingress/RAW       coleta/ingresso.py :: receber
  │                          → guarda/preservar_coleta.py :: preservar
  │                          (corre ANTES de T-32: T-32 exige RAW_ASSET_ID)
  └─ T-32  unit forward      coleta/rota_forward_documento.py :: atravessar
             ↓                UMA unidade, com o universo RECEBIDO
           T-40  DERIVED      coleta/derivacao_forward.py
             ↓
           T-42  STRUCTURED   coleta/social_persistencia.py
             ↓
           T-50  ADMISSION    admissao/admissao.py :: decidir      ← ÚNICO chamador: T-32
             ↓  (só se SIM)
           T-52  READY        admissao/admissao.py :: pronto_para_inteligencia
                              construtor continua T-50 · chamador passa a ser T-32
```

**Por que T-30 fica com T-04 e não dentro de T-32.** T-32 declara *«NÃO emite RAW»* (`:23`),
e a prova `o_encanamento_tem_uma_porta.py` (P3) proíbe qualquer coletor preservar por fora.
T-32 **começa** em DERIVED e exige `RAW_ASSET_ID` já existente (`:252`). Logo o ingresso é
etapa da corrida, coordenada por T-04, e não etapa da unidade.

---

## 9 · UM CÉREBRO — a tabela

| QUESTION | CURRENT OWNER(S) | TARGET OWNER | MIGRATION ACTION |
|---|---|---|---|
| run coordination | T-04 | **T-04** | nenhuma |
| route policy | **nenhum** (`executores[0]`, ordem de lista) | **T-05** | criar o dono; ordenar por `custo` (COL-LAW-018) |
| executor resolution | partido: registry em T-06 · escolha em T-04 | **T-06** | T-04 pergunta em vez de indexar |
| unit traversal | **nenhum em runtime** (T-32 órfã) | **T-32** | T-04 passa a chamar `atravessar()` por unidade |
| **Admission** | **3**: T-04 · golden_path · T-32 | **T-32** | T-04 e golden_path deixam de chamar em runtime |
| READY construction | construtor T-50 · chamador T-04 | construtor **T-50** · chamador **T-32** | move-se a chamada, não o construtor |
| admission universe | 3 escritores · dono real T-02 | **T-02** | matar `UNIVERSO_PADRAO` e a constante `UNIVERSO` |
| global retry | **nenhum** | **T-04** | criar o dono |

```
ORCHESTRATION_OWNER_COUNT = 1
ADMISSION_TARGET_CALLER   = 1
READY_TARGET_CALLER       = 1
UNIVERSE_OWNER            = 1
GLOBAL_RETRY_OWNER        = 1
```

---

## 10 · AS CHAMADAS QUE TERÃO DE SAIR

Sem patch, sem sequência de commits. Só o que sai, para onde vai, e porquê.

| # | CURRENT CALL | TARGET CALL | WHY |
|---|---|---|---|
| 1 | `orquestrador.py:138` `adm.decidir(x, universo, …)` | `m2.atravessar(banco, unidade=…, universo=…)` | quem julga tem de possuir a unidade. Hoje T-04 julga itens que nunca passaram por DERIVED nem STRUCTURED |
| 2 | `orquestrador.py:145` `adm.pronto_para_inteligencia(x, d)` | *(deixa de existir aqui)* — T-32 chama depois do `SIM` | READY nasce da decisão; quem tem a decisão é quem chamou a porta |
| 3 | `golden_path_pdf.py:169` `adm.decidir(item, UNIVERSO, …)` | mantém-se, **reclassificada como prova** | uma prova que não bate na porta não prova nada. Deixa de ser contada como runtime, como `provas/` e `tests/` já são |
| 4 | `rota_forward_documento.py:191` `admissao.decidir(item, universo)` | igual, com `item` completo: `artifact_type` + `parent_artifact_id` | ela **tem** a linhagem e não a declara; sem isso a porta aplica a régua errada e devolve `NAO_SEI` |
| 5 | `rota_forward_documento.py:68` `UNIVERSO_PADRAO = 'T3'` | parâmetro obrigatório, sem omissão | «vem de fora quando o chamador souber» é o que o próprio ficheiro escreve; um default é inventá-lo quando ele não soube |
| 6 | `orquestrador.py:225` `plano.executores[0]` | T-06 resolve, T-04 pergunta | índice zero não é política de rota |

### Precondição que a migração tem de satisfazer ANTES da número 1

`T-32` só sabe atravessar **uma espécie de unidade**: documento com PDF.
`derivar()` (`:252`) passa `{'RAW_ASSET_ID', 'PDF'}` a `derivacao_forward.correr`, que chama
`executor_texto_de_pdf`. Os itens que T-04 leva hoje à porta são publicações de concorrente
(T9, YouTube/Instagram) — **não são PDF**.

Logo, colapsar 3→1 exige primeiro que T-32 aceite uma unidade cuja derivação seja
`NAO_SE_APLICA` — o texto já é o bruto. A casa já tem a palavra (`NAO_SE_APLICA` é um dos
cinco resultados) e já tem a lei das capacidades declaradas (COL-LAW-207: `DISCOVER` ·
`FETCH` · `DERIVE`). **É pergunta de capacidade de executor, não de propriedade de decisão** —
por isso não reabre nada do que se fecha aqui, e por isso está escrito antes de alguém
tropeçar nela.

---

## 11 · ENTREGA

| | |
|---|---|
| **A** `BRANCH` | `claude/raw-observation-identity-3jbwco` |
| **B** `INITIAL_HEAD` | `b1cc973fe88a7fc2ea312f6c8c9f3e4acf808538` |
| **D** `WORKTREE` | limpa |
| **E** `ORCHESTRATION_OWNER_CURRENT` | 1 nominal (T-04) — mas acumulando 4 papéis alheios |
| **F** `ORCHESTRATION_OWNER_TARGET` | **T-04**, só coordenação |
| **G** `ADMISSION_CALLERS_CURRENT` | **3** runtime (+24 prova/teste) |
| **H** `ADMISSION_CALLERS_TARGET` | **1** runtime |
| **I** `ADMISSION_TARGET_CALLER` | **T-32** `rota_forward_documento.py::admitir` |
| **J** `ORQUESTRADOR_DIRECT_ADMISSION_TARGET` | **NO** ✅ |
| **K** `ORQUESTRADOR_DIRECT_READY_TARGET` | **NO** ✅ |
| **L** `GOLDEN_PATH_PDF_ROLE` | **PROOF** — nenhum workflow o corre; único importador é a prova dele |
| **M** `GOLDEN_PATH_PDF_TARGET` | **PROOF_ONLY**; saída continua a ir para o System Map; o trabalho operacional passa a T-04 → T-32 |
| **N** `T32_CALLERS_CURRENT` | **0** em runtime (4 em teste, 0 na prova, por decisão dela) |
| **O** `T32_CALLERS_TARGET` | **1** — T-04 |
| **P** `T32_ADMISSION_INPUTS_COMPLETE` | **NO** — falta `artifact_type` e `parent_artifact_id` no item |
| **Q** `T32_CAN_CALL_ADMISSION_WITHOUT_LINEAGE` | **YES hoje** → alvo **NO** |
| **R** `UNIVERSE_CURRENT_OWNER` | 3 escritores; dono legítimo `Pedido.alvo` |
| **S** `UNIVERSE_TARGET_OWNER` | **T-02** `pedido/pedido.py::Pedido.alvo` |
| **T** `UNIVERSE_TARGET_INPUT_PATH` | `Pedido.alvo → Plano → T-04 → atravessar(universo=) → admitir(universo=) → decidir(item, universo)` |
| **U** `EXECUTOR_SELECTION_OWNER` | hoje partido → alvo **T-06**, com T-04 a perguntar |
| **V** `GLOBAL_RETRY_OWNER` | hoje **0** → alvo **T-04** |
| **W** `EXECUTOR_LOCAL_RETRY_BOUNDARY` | transporte com limite e lista fechada fica no executor; tudo o que muda o plano da corrida é T-04 |
| **X** `READY_CALLERS_CURRENT` | **1** — `orquestrador.py:145` |
| **Y** `READY_TARGET_CALLER` | **T-32**, depois do `SIM`; construtor continua T-50 |
| **Z** `CRITICAL_MULTIPLE_OWNERS_CURRENT` | **4**: Admission (3) · universo (3) · executor selection (2) · route policy e retry global (0 = ninguém, que é o mesmo defeito ao contrário) |
| **AA** `CRITICAL_MULTIPLE_OWNERS_TARGET` | **0** |

### AB · `UNRESOLVED_ORCHESTRATION_QUESTIONS`

`UNRESOLVED_CRITICAL_ORCHESTRATION_QUESTIONS = 0` — nenhuma das abertas é sobre **quem é
dono de quê**.

1. **T-32 só atravessa documento com PDF.** Precondição da migração, escrita em §10. Não é
   pergunta de propriedade.
2. **READY com três `NAO SEI`** (`SOURCE_LOCATION`, `FACT_LOCATION`, `FACT_TIME`) é READY? —
   **C-PLAN-C**, por instrução da missão.
3. **T-05 não existe como peça.** O dono está decidido; onde ele mora é decisão de
   implementação.
4. **READY continua com 0 consumidores** e destino inexistente. Medido pelo censo da
   fronteira, anterior a esta missão, e não bloqueia direcção nenhuma.
5. **Circuit breaker (COL-LAW-026) continua `IT: ABSENT`.** Passa a ter dono (T-04) sem
   passar a existir.

---

## 12 · EM PALAVRAS FÁCEIS

1. **Quem é o único cérebro?** O **T-04**, o orquestrador. Só que hoje ele faz coisas que
   não são dele — julga item e constrói READY. Passa a só coordenar.
2. **Quem escolhe qual executor trabalha?** O **T-06**, o registo de executores. O T-04
   pergunta; hoje ele pega no primeiro da lista.
3. **Quem decide a rota?** O **T-05**. Hoje ninguém decide: a preferência é a ordem da
   lista, não o custo.
4. **Quem atravessa uma unidade até à Admission?** O **T-32**. Hoje ninguém o chama.
5. **Quem é o único que chama a Admission no alvo?** O **T-32**, e mais ninguém.
6. **Por que os outros dois deixam de chamar?** O orquestrador porque não tem a unidade —
   ele tem a corrida. O golden path porque é prova, e prova não é produção.
7. **De onde vem o universo?** Do **pedido** (`Pedido.alvo`), que já valida contra o atlas e
   já se recusa a adivinhar. Nunca de um `UNIVERSO_PADRAO = 'T3'` dentro do encaminhador.
8. **Quem constrói READY?** A **admissão** constrói, como hoje. Quem passa a **chamar** é o
   T-32, logo depois do `SIM`.
9. **Quem decide retry da corrida?** O **T-04**. Hoje ninguém decide. Retry de transporte
   continua dentro do executor, com limite e lista fechada.
10. **Há decisão crítica ainda aberta?** **Não.** Há cinco perguntas em §11-AB, e nenhuma é
    sobre quem é dono de quê.

---

## 13 · VEREDITO

```
ONE_ORCHESTRATOR           = CLOSED
ADMISSION 3 → 1            = CLOSED
T32_CALLER                 = CLOSED
UNIVERSE_OWNER             = CLOSED
EXECUTOR_SELECTION_OWNER   = CLOSED
GLOBAL_RETRY_OWNER         = CLOSED
READY_CALLER_DIRECTION     = CLOSED

UNRESOLVED_CRITICAL_ORCHESTRATION_QUESTIONS = 0

C-PLAN-A = PASS
```

```
RUNTIME_FILES_CHANGED = 0
MIGRATIONS_CHANGED    = 0
DATABASE_MUTATIONS    = 0
SYSTEM_MAP_CHANGED    = 0
BIBLE_CHANGED         = 0
```

### Nota honesta sobre o validador do System Map

`SYSTEM_MAP_CHECK = FAIL`, numa prova só: `P1_SEM_DRIFT`. A diferença é inteira o nome do
ramo, o `HEAD` e o carimbo de geração — filtrados os três, o diff é **vazio**, e acrescentar
este documento não muda nenhuma das projeções de arquitetura. É a mesma nota da C-PLAN-0, e
pela mesma razão: **ninguém mexeu na arquitetura**. A regeneração pertence a quem integrar
isto no ramo canónico.

> **HARD STOP.** A orquestração está fechada. Não se começa a alterar código.
