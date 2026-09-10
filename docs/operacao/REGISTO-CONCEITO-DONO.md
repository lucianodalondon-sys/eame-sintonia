# `CONCEPT_ID → OWNER` — quem sabe receber cada espécie

**C-PLAN-A5.4 · fecha o bloqueio D3 · 2026-09-10 · ramo `claude/raw-observation-identity-3jbwco`**

> **Nada foi implementado.** Zero runtime, zero registo criado, zero migration, zero banco,
> zero T-32, zero contrato de fonte, zero `source_document`, zero Admission, zero READY,
> zero ponte, zero System Map, zero Bíblia.

```
LOCAL_HEAD = REMOTE_HEAD = 14be2c80f0e8b0a36dbd65900fa4e416b5316680
WORKTREE   = limpa   ·   DIVERGENCE = 0
```

---

## 1 · A CASA JÁ TEM ESTE PADRÃO A CORRER — E É QUASE IDÊNTICO

Antes de desenhar, medi: **há registos que mapeiam para referência (função ou módulo) nesta
casa?**

```
9 dicionários com valores que são referência, em 8 ficheiros.
E só UM deles é um registo de DESPACHO (id → quem executa):

    coleta/social_rotas.py:342   ADAPTADORES   9/9 valores são função
```

Os outros oito mapeiam para funções de **classificação** (`diagnostico.POR_ETAPA`,
`falhas._POR_ESTADO`) ou para **fases** de um coletor. Só o `ADAPTADORES` responde
*«quem sabe fazer isto?»*.

### E ele já separa as três autoridades que o D3 precisa de separar

```python
# coleta/social_rotas.py — a sequência real, hoje, em produção

rotas = (mz.MATRIZ.get(plat) or {}).get(cap)          # 1 · a LEI autoriza?
if not rotas:
    registro['ESTADO'] = 'NOT_APPLICABLE'
    registro['ERRO']   = 'capacidade não declarada na matriz para esta plataforma'

escolhida = mz._rota_padrao(rotas)                     # 2 · e PERMITE esta?
if escolhida is None:
    registro['ESTADO'] = 'ROUTE_NOT_ALLOWED'

fn = ADAPTADORES.get((plat, cap))                      # 3 · e QUEM executa?
if fn is None:
    registro['ESTADO'] = 'POSSIBLE_NOT_PROVED'
    registro['ERRO']   = 'rota declarada e permitida, mas SEM ADAPTADOR nesta missão'

try:
    objetos = fn(...)                                  # 4 · e o dono corre
```

> ## A LEI QUE AUTORIZA VIVE NUM FICHEIRO. O REGISTO QUE DESPACHA VIVE NOUTRO.
> `leis/social_matriz.py::MATRIZ` diz o que é permitido.
> `coleta/social_rotas.py::ADAPTADORES` diz quem sabe fazer.
> **Nunca o mesmo objecto.**

E o correspondente é linha a linha:

| aqui, já a correr | no D3 |
|---|---|
| `MATRIZ` — a capacidade é declarada? | `ALLOWED_STRUCTURED_TARGETS` no contrato da fonte |
| `NOT_APPLICABLE` — não declarada | `STRUCTURED_TARGET_NOT_DECLARED` |
| `ROUTE_NOT_ALLOWED` — declarada, não permitida | `STRUCTURED_TARGET_NOT_ALLOWED` |
| «declarada e permitida, mas **sem adaptador**» | **`OWNER_NOT_CONNECTED`** |
| `ADAPTADORES.get(...)` · `if fn is None` · sem fallback | o registo do T-06 |
| `try: fn(...)` | falha de runtime do dono, e é outra coisa |

**Não se inventa mecanismo.** O D3 é este padrão, com outra chave.

---

## 2 · O DONO DO REGISTO

```
REGISTRY_OWNER = T-06
```

A A4 fechou-o e não encontrei contradição medida. A responsabilidade é **uma**:

> **dado um `CONCEPT_ID` válido, devolver o dono ligado a esse conceito.**

E o T-06 **não**: escolhe conceito · muda conceito · decide Admission · decide universo ·
persiste a unidade · faz transformação. Ele resolve `CONCEPT_ID → OWNER`, e mais nada.

---

## 3 · A FORMA E O SÍTIO

```
REGISTRY_FORM = dicionário estático em código · CONCEPT_ID → referência ao dono
                lido com .get() · falha explícita quando ausente · sem fallback
```

Medido no `ADAPTADORES`: chave → função, `.get()`, `if fn is None` com estado nomeado, e o
`try` só depois. Nada de `first match wins`, nada de procurar por nome de ficheiro.

```
REGISTRY_LOCATION_TARGET = pedido/estruturados.py   (módulo novo, irmão de receitas.py)
```

**Por que ali, e a tensão fica dita.** O precedente põe o registo **junto do despachante**
(`ADAPTADORES` vive no ficheiro que despacha). **Aqui isso é proibido de propósito**: o
despachante é o T-32, e `T32_OWNS_REGISTRY = NO`. Então segue-se a outra regra medida — a
casa já guarda «id → quem executa» em `pedido/receitas.py::EXECUTORES`, que é o T-06 — e o
registo do STRUCTURED entra como **ficheiro irmão**, não como segunda chave dentro do
`EXECUTORES`. A A4 já tinha dito porquê: *mesma forma, outra pergunta; não se misturam duas
chaves numa tabela*.

⚠️ **Registado:** o pacote `pedido/` é a camada do pedido, e alojar registos ali é herança do
`EXECUTORES`, não desenho. Se um dia o T-06 ganhar casa própria, **os dois mudam juntos** —
e é por serem irmãos que isso será uma mudança e não uma arqueologia.

```
REGISTRY_ENTRY_MINIMUM_CONTRACT = CONCEPT_ID  →  referência ao dono
                                  UMA chave, UM valor. Nada mais.
```

O que **não** entra, e porquê:

| candidato | veredito |
|---|---|
| `OWNER_ID` | ✖ a referência ao módulo **é** o identificador. `EXECUTORES` já usa o caminho como id |
| `CALLABLE/HANDLER` separado do `OWNER` | ✖ são a mesma coisa; dois campos criariam duas verdades |
| `CONTRACT_VERSION` | ✖ **o dono já declara a sua versão** (`rule_version`, `CORPO_VERSAO`, `VERSAO_DA_REGRA`), e a A5.1 lê `contract_version` de lá. Copiá-la para o registo criaria segunda autoridade sobre a versão |

> **Um registo é uma lista telefónica, não um catálogo.** Ele diz para onde ligar. Quem
> atende é que sabe quem é.

---

## 4 · OS SEIS CONCEITOS FECHADOS

| `CONCEPT_ID` | `OWNER_TARGET` | `IMPLEMENTATION_EXISTS` | `CONNECTABLE_NOW` |
|---|---|---|---|
| `SOCIAL_CONTENT` | `coleta/social_persistencia.py` | **YES** — `persistir_video` escreve `conteudo` | **YES** |
| `SOCIAL_COMMENT` | `coleta/social_persistencia.py` | **YES** — escreve `comentario` | **YES** |
| `SOCIAL_TRANSCRIPT` | `coleta/social_persistencia.py` | **NO** — nenhum ficheiro escreve `transcricao` | **NO** |
| `REGULATORY_REGISTRATION` | `guarda/importar_italia.py` | **YES** | **YES** |
| `CATALOG_PRODUCT_DOCUMENT` | `guarda/catalogo_importar.py` | **YES** | **YES** |
| `SOURCE_DOCUMENT` | `guarda/preservar_documento.py` | **NO** — a A5.1 fechou o dono; o ficheiro não existe | **NO** |

```
CLOSED_CONCEPT_COUNT                        = 6
CONNECTABLE_OWNER_COUNT                     = 4
CONCEPTS_WITH_OWNER_IMPLEMENTATION_MISSING  = 2   SOURCE_DOCUMENT · SOCIAL_TRANSCRIPT
```

**Dono fechado não é dono existente**, e os dois casos são diferentes: `SOURCE_DOCUMENT`
espera um ficheiro que ninguém escreveu ainda; `SOCIAL_TRANSCRIPT` espera uma função dentro
de um ficheiro que já existe.

⚠️ **E `CONNECTABLE_NOW` significa exactamente uma coisa: o registo pode nomear um dono que
existe e se importa.** Não significa que ele aceite uma unidade como está —
`persistir_video(banco, canal_id=…, content_id=…, texto_canonico=…, raw_durou=…)` não tem
forma de unidade. **A interface do dono não é uniforme, e isso não é pergunta desta missão.**
Fica registado para não ser descoberto a meio da implementação.

### Os candidatos não entram

```
AGROCLIMATIC_MEASUREMENT   NÃO
FIELD_MONITORING_POINT     NÃO
os conceitos da migration 021   NÃO — e nem sequer foram abertos aqui

CONCEPT NOT CLOSED  →  NOT IN CANONICAL REGISTRY
```

Um registo com um candidato lá dentro passa a ser uma promessa, e uma promessa num registo
é indistinguível de um facto.

---

## 5 · AS TRÊS AUTORIDADES, E O REGISTO NÃO É NENHUMA DAS OUTRAS DUAS

```
ALLOWED_STRUCTURED_TARGETS   contrato da FONTE     «esta fonte PODE produzir isto»
RESOLVED_STRUCTURED_TARGET   a UNIDADE             «esta unidade PRODUZIU isto»
CONCEPT → OWNER (T-06)       o REGISTO             «quem sabe RECEBER isto»
```

**O registo nunca autoriza uma fonte.** Um conceito estar no registo diz que **existe quem o
receba** — não diz que qualquer fonte o pode produzir. Se o registo pudesse autorizar, a
lista da fonte deixaria de valer, e a A5.2 inteira cairia por um atalho.

É a mesma disciplina que o `social_rotas` já pratica: a `MATRIZ` autoriza, o `ADAPTADORES`
executa, e **ter adaptador nunca fez uma rota permitida**.

---

## 6 · QUANDO NÃO HÁ DONO

```
OWNER_NOT_CONNECTED_BEHAVIOR

  alvo válido  +  alvo autorizado  +  nenhum dono ligado
        ↓
  OWNER_NOT_CONNECTED  ·  FAIL  ·  sem fallback
```

**Código já existente**, e o texto dele responde à pergunta palavra por palavra
(`leis/diagnostico.py`):

> *«há dono declarado para a etapa e ele não toca o artefato. **OWNER EXISTS != EDGE
> EXISTS**.»*

**Nenhum código novo.** E o precedente vivo diz o mesmo noutras palavras: *«rota declarada e
permitida, mas sem adaptador nesta missão»*.

### E isto é diferente de o dono falhar a correr

```
dono AUSENTE do registo      →  OWNER_NOT_CONNECTED       defeito de LIGAÇÃO
dono PRESENTE e rebenta      →  falha de runtime do dono  defeito de EXECUÇÃO
```

O `social_rotas` já as separa fisicamente: o `if fn is None` acontece **antes** do `try:
fn(...)`. Confundi-las mandaria alguém depurar um writer que nunca foi chamado.

**Retry não se aprofunda aqui** — a C-PLAN-A já fechou que retry global é do T-04.

---

## 7 · DOIS DONOS PARA UM CONCEITO

```
MULTIPLE_OWNERS_BEHAVIOR = falha de CONFIGURAÇÃO, no carregamento, com excepção
                           NUNCA resolução em runtime
                           NUNCA first match wins
                           NUNCA last wins
```

E há aqui uma armadilha que tem de ser dita, porque a estrutura escolhida **não protege
sozinha**:

> ## UM DICIONÁRIO EM PYTHON ENGOLE A CHAVE REPETIDA EM SILÊNCIO.
> `{"A": x, "A": y}` não levanta erro: fica `y`. Isso é `last wins`, **exactamente o que
> está proibido**, e acontece antes de qualquer código poder reparar.

Por isso a protecção são **duas camadas, e nenhuma é decorativa**:

1. **No carregamento** — o registo é montado a partir de entradas e **levanta excepção** ao
   ver um `CONCEPT_ID` repetido. Precedente da casa: `alvo_de()` levanta `PedidoInvalido`
   em vez de adivinhar; e `rastro.registrar` usa `assert estado in ESTADOS`.
2. **Por guarda** — um teste que lê a fonte e conta as chaves, porque a camada 1 não vê o
   que o literal já colapsou. Precedente:
   `tests/test_porta_de_producao.py::test_o_conjunto_de_escritores_nao_cresceu`, que existe
   precisamente para um conjunto não crescer sem alguém reparar.

Não é código de diagnóstico: um `CONCEPT_ID` duplicado **nunca chega ao runtime** como
estado distinguível. É erro de configuração, e reprova antes de correr.

---

## 8 · O PAPEL DO T-32

```
T32_OWNS_REGISTRY = NO
```

O T-32 **não mantém cópia paralela** do registo, não o lê de um ficheiro seu, não o embute.
Ele pergunta.

```
T32_LOOKUP_SEQUENCE

  1  recebe a unidade, já com RESOLVED_STRUCTURED_TARGET   (A5.3)
  2  lê ALLOWED_STRUCTURED_TARGETS do contrato da FONTE, por SOURCE_ID
       ausente  →  STRUCTURED_TARGET_NOT_DECLARED · FAIL
  3  confere pertença
       fora     →  STRUCTURED_TARGET_NOT_ALLOWED   · FAIL
  4  pergunta ao T-06:  dono(CONCEPT_ID)
       ausente  →  OWNER_NOT_CONNECTED             · FAIL
  5  entrega a unidade ao dono
```

Quatro perguntas, quatro respostas possíveis de falha, **quatro culpados diferentes** — o
executor, o contrato, a divergência entre os dois, e a ligação. Nenhuma delas é «não sei».

---

## 9 · O PRIMEIRO SLICE, CONCEITUALMENTE

```
unidade  ·  SOURCE_ID = IT-T2-002
            DOCUMENT_ID = ARPAV:Z01:20260903160930
            DOCUMENT_VERSION_ID = v1_f88c89d73d6a
            RESOLVED_STRUCTURED_TARGET = SOURCE_DOCUMENT
                 ↓
T-32   lê ALLOWED_STRUCTURED_TARGETS de IT-T2-002   →  [SOURCE_DOCUMENT]
       confere pertença                             →  PASS
                 ↓
T-06   dono("SOURCE_DOCUMENT")                      →  guarda/preservar_documento.py
                 ↓
       (a chamada não acontece nesta missão)
```

```
SOURCE_DOCUMENT_OWNER_MAPPING = CLOSED
```

O dono foi fechado pela A5.1 e **não é reaberto**. Aqui só se fecha **como se chega a ele**.

---

## 10 · O QUE CONTINUA A FALTAR, MESMO COM O D3 FECHADO

```
UNIT_BRIDGE_STILL_REQUIRED = YES
```

A A5.3 mediu: `CURRENT_UNIT_PRODUCER = nenhum em runtime`. O coletor produz observações de
livro; o T-32 consome unidades; **e entre os dois não há tradutor**.

Fechar o D3 dá ao T-32 **para onde** entregar. Não lhe dá **o que** entregar.

**Não se desenha a ponte aqui.** Fica dito para que ninguém, ao ler o D3 fechado, conclua
que o slice já corre.

---

## 11 · ENTREGA

| | |
|---|---|
| **A** `BRANCH` | `claude/raw-observation-identity-3jbwco` |
| **B** `INITIAL_HEAD` | `14be2c80f0e8b0a36dbd65900fa4e416b5316680` |
| **D** `WORKTREE` | limpa |
| **E** `REGISTRY_OWNER` | **T-06** |
| **F** `REGISTRY_FORM` | dicionário estático em código · `CONCEPT_ID → referência ao dono` · `.get()` · falha explícita · sem fallback |
| **G** `REGISTRY_LOCATION_TARGET` | `pedido/estruturados.py` — irmão de `receitas.py::EXECUTORES`, nunca dentro do T-32 |
| **H** `REGISTRY_ENTRY_MINIMUM_CONTRACT` | uma chave, um valor. Sem `OWNER_ID`, sem `CONTRACT_VERSION` |
| **I** `SOURCE_DOCUMENT_OWNER_MAPPING` | `SOURCE_DOCUMENT → guarda/preservar_documento.py` · **CLOSED** |
| **J** `CLOSED_CONCEPT_COUNT` | **6** |
| **K** `CONNECTABLE_OWNER_COUNT` | **4** |
| **L** `CONCEPTS_WITH_OWNER_IMPLEMENTATION_MISSING` | **2** — `SOURCE_DOCUMENT` · `SOCIAL_TRANSCRIPT` |
| **M** `OWNER_NOT_CONNECTED_BEHAVIOR` | `OWNER_NOT_CONNECTED` · `FAIL` · sem fallback · **código já existente** |
| **N** `MULTIPLE_OWNERS_BEHAVIOR` | falha de configuração, no carregamento, com excepção **e** guarda por teste. Nunca first/last wins |
| **O** `T32_OWNS_REGISTRY` | **NO** |
| **P** `T32_LOOKUP_SEQUENCE` | recebe → lê o contrato → confere → pergunta ao T-06 → entrega |
| **Q** `UNIT_BRIDGE_STILL_REQUIRED` | **YES** |
| **R** `RUNTIME_FILES_CHANGED` | **0** |
| **S** `CONTRACT_FILES_CHANGED` | **0** |
| **T** `DATABASE_MUTATIONS` | **0** |
| **U** `SYSTEM_MAP_CHANGED` | **0** |
| **V** `BIBLE_CHANGED` | **0** |
| **W** `UNRESOLVED_CRITICAL_A5_4_QUESTIONS` | **0** |

### O que continua `NÃO SEI` — e nenhum bloqueia

1. **A interface do dono não é uniforme.** Nenhum dos 4 donos ligáveis aceita hoje uma
   unidade como está. Nomear não é chamar (§4).
2. **`pedido/` é a casa herdada dos registos**, não a desenhada (§3).
3. **A ponte observação→unidade continua sem existir** (§10).

---

## 12 · VEREDITO

```
REGISTRY_OWNER            = CLOSED   T-06
REGISTRY_FORM             = CLOSED   dict estático, id → referência, sem fallback
SOURCE_DOCUMENT_MAPPING   = CLOSED   → guarda/preservar_documento.py
MISSING_OWNER_BEHAVIOR    = CLOSED   OWNER_NOT_CONNECTED, código já existente
MULTIPLE_OWNER_BEHAVIOR   = CLOSED   erro de configuração, duas camadas de trava
T32_LOOKUP_ROLE           = CLOSED   pergunta, não guarda

C-PLAN-A5.4 = PASS
```

O futuro T-32 recebe `SOURCE_DOCUMENT` e descobre `guarda/preservar_documento.py` **de forma
única**, sem adivinhar, sem procurar por nome de ficheiro, sem escolher o primeiro que
aparece e sem manter mapa próprio.

---

## 13 · EM PALAVRAS FÁCEIS

1. **Para que serve este registo?** É a lista telefónica. Dado o nome da espécie, diz para
   onde ligar.

2. **O que acontece quando chega uma unidade `SOURCE_DOCUMENT`?** O T-32 confere que a
   fonte podia produzir aquilo, pergunta ao registo quem recebe, e entrega.

3. **Quem diz para onde ela vai?** O T-06, e só ele. Uma pergunta, uma resposta.

4. **O T-32 guarda essa lista?** Não. Se guardasse, teríamos duas listas — e no dia em que
   divergissem, ninguém saberia qual valia.

5. **E se não existir dono?** Falha com nome: `OWNER_NOT_CONNECTED`. Não se procura um
   parecido, não se escolhe outro. O código já existe e diz exactamente isto.

6. **E se aparecerem dois donos?** É erro de configuração e reprova antes de correr. E
   houve um cuidado extra: um dicionário em Python engole a chave repetida em silêncio, por
   isso a trava não pode ser só a estrutura — tem de haver uma guarda que conte as chaves.

7. **Quantos tipos já têm dono de verdade?** Quatro de seis. Faltam o documento de fonte,
   cujo ficheiro ninguém escreveu, e a transcrição, que espera uma função num ficheiro que
   já existe.

8. **A ponte entre coleta e T-32 continua a faltar?** Continua. Fechar isto diz **para onde**
   entregar; não diz **o que** entregar.

9. **Algum código foi alterado?** Nenhum. E encontrei o padrão pronto: `social_rotas.py` já
   faz exactamente esta sequência há missões, com outra chave.

10. **Qual é o próximo passo?** A ponte observação→unidade. É a última peça que falta para o
    primeiro slice deixar de ser desenho.

> **HARD STOP.** Dono do registo, forma, sítio, contrato da entrada, mapeamento do
> `SOURCE_DOCUMENT`, falha por dono ausente, falha por dono duplicado e papel do T-32 estão
> fechados. Não se cria o registo. Não se cria a ponte.
