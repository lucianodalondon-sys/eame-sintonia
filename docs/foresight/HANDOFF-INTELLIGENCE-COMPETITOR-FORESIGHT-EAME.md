# HANDOFF · COMPETITOR FORESIGHT EAME → RODADA DE INTELIGÊNCIA

**Data:** 2026-08-30 · **Autocontido**: quem ler isto não precisa da conversa.
**DATASET_OWNER:** `COMPETITOR_FORESIGHT_EAME`

---

## 0 · LEITURA RÁPIDA — o estado em nove linhas

| | |
|---|---|
| **CAPABILITY STATUS** | **`FROZEN_WAITING_FOR_INTELLIGENCE`** |
| **O QUE ELA RESPONDE HOJE** | *"Que marcas este concorrente depositou, onde e quando — e que autorizações ele detém, com que datas?"* |
| **ONDE ELA RESPONDE HOJE** | **ES · IT · FR**, os três medidos com a **mesma régua** |
| **O QUE ELA NÃO RESPONDE** | o que foi ao mercado · quando · quanto · por quê · o que virá |
| **CADEIAS LIGADAS** | **1.683** (209 ES · 334 IT · 1.140 FR) |
| **CADEIAS COM 5 DE 5 CAMADAS** | **0** — todas têm 2 de 5 |
| **FALSOS LINKS RECUSADOS E PUBLICADOS** | **126** |
| **`OPERATIONAL_EARLY_WARNING_VALUE`** | **`NOT_PROVED`** |
| **APLICADO NO SUPABASE DE PRODUÇÃO** | **NÃO** |

### A pergunta, e a que ela NÃO é

> **WHAT HAS THIS COMPETITOR REGISTERED AND FILED — WHERE, AND WHEN?**
> **NÃO:** *what is this competitor about to launch?*

### As leis que precisam viajar com os dados

> **`SAME_NAME ≠ SAME_COMPETITOR_PRODUCT`**
> **`NICE_CLASS ≠ AGROCHEMICAL PROOF`**
> **`HISTORICAL_PRECEDENCE ≠ OPERATIONAL_EARLY_WARNING`**
> **`0 CHANGE_OBSERVED ≠ REGISTRO ESTÁTICO`**
> **`REFUTED_ROUTE ≠ REFUTED_LAYER`**
> **`NOT_JOINED ≠ NOT_AVAILABLE ≠ ZERO`**

---

## 1 · WHAT IS PROVED

| # | afirmação | evidência |
|---|---|---|
| 1 | **A rota TMview funciona e cobre os quatro escritórios** (OEPM · UIBM · INPI · EUIPO) numa requisição. Os portais nacionais recusam robô (403/403/sem conexão). | `COMPETITOR-IP-TMVIEW.json` · 9.661 marcas |
| 2 | **Os três registros nacionais abrem, inteiros, de graça e sem chave.** ES por POST JSON; IT por CSV aberto (CC BY 4.0); FR por ZIP do data.gouv.fr (Licence Ouverte). | `registro_local.py` · 3.084 + 17.695 + 15.140 |
| 3 | **`TRADEMARK ↔ LOCAL REGISTRATION` liga, nos três países, com a mesma régua.** Duas concordâncias obrigatórias: nome normalizado **e** grupo do titular. | **1.683 cadeias** `PROVED` |
| 4 | **A recusa funciona e é publicada.** 126 pares com nome idêntico e titular divergente foram RECUSADOS nos três países. | `URBOLE` — marca SYNGENTA, registro ES 24157 da ADAMA |
| 5 | **A frouxidão foi medida, não imaginada.** Um casador por prefixo foi realmente rodado: criaria 3.626 pares extras, **2.082 deles com titular errado** (57%). | `RUIDO_DO_CASADOR_FROUXO` por país |
| 6 | **Classe 5 de Nice não é prova agroquímica.** 4.496 das 9.661 marcas caem nela; **2.551 são da Bayer**, que tem divisão farmacêutica. | `GINECANES`, `BEPANTHEN` |
| 7 | **A classe nem é estável entre países.** `VERDALIS` da Corteva: classe 1 na IT e na FR, classe 5 na ES — mesma marca, mesmo titular, mesma semana. | regressão `N1` |

---

## 2 · WHAT IS PROMISING

**`A · TRADEMARK CHANGE WATCH` → `PROMISING`**

346 depósitos desde 2025-01-01 nos quatro escritórios, e um observado **três
dias** antes da coleta (`BLUEGROW`, Corteva, IT, classe 1+5).

> `RECENT_TRADEMARK_ACTIVITY_EXISTS = YES`
> `TRADEMARK_WATCH_AS_CHANGE_SOURCE = PROMISING`
> **`DAILY_VALUE = NOT_PROVED`**

**Por que não passa de PROMISING:** existe **uma** captura. Uma fotografia não
mede cadência. Promover exige segunda e terceira capturas em D+7 e D+30, com o
mesmo portão de filtro, e a contagem do que apareceu entre elas.

---

## 3 · WHAT IS NOT PROVED

| item | estado | por quê |
|---|---|---|
| `OPERATIONAL_EARLY_WARNING_VALUE` | **NOT_PROVED** | mediana defensável de **1.546 dias (~4,2 anos)**, amplitude bruta de −21.478 a +13.004. Um sinal que chega anos antes pode estar **cedo demais** para decisão |
| `DAILY_VALUE` da marca | **NOT_PROVED** | uma captura só |
| `REGULATORY_CHANGE_CADENCE` | **NOT_PROVED** | duas capturas a **dois dias** de distância |
| cadeia de 5 camadas | **NOT_PROVED** | 0 de 1.683 |
| junção com `CROP` e `ISSUE` | **NOT_PROVED** | nenhum dos três registros traz cultura e alvo neste dataset |
| `PATENT_WATCH` como um todo | **NOT_TESTED** | ver §4 |

### As frases que os números **não** autorizam

- ❌ "a marca prevê o registro"
- ❌ "a marca dá 4 anos de antecedência útil"
- ❌ "temos aviso prévio de lançamento"
- ❌ "o registro não se mexe no dia a dia"
- ❌ "o concorrente vai lançar o produto X"

---

## 4 · WHAT WAS REFUTED

**Uma rota. Não uma camada.**

```
PATENT_BRAND_LINKAGE_ROUTE = REFUTED_FOR_PILOT
PATENT_LAYER               = DEMOTED / NOT_USED
PATENT_WATCH (como um todo) = NOT_TESTED
```

Buscar o **nome comercial da marca** no texto completo do Espacenet: **0 de 5**
casos recuperaram o titular correto. `LIBERATOR` devolve coldre de bolso;
`DUAL GOLD`, um implante hospitalar; `VERDALIS`, zero.

**Continuam sem teste, e portanto sem veredicto:**
`APPLICANT_BASED_PATENT_WATCH` (a busca por titular devolve 6.333 resultados só
para a Syngenta — o volume existe) · `TECHNOLOGY_WATCH` ·
`ACTIVE_INGREDIENT_WATCH` · `FORMULATION_WATCH` · `ASSIGNEE_FAMILY_WATCH`.

> **Proibido escrever `PATENT_WATCH = REFUTED`.** Refutar uma camada com o teste
> de uma rota é o erro que este piloto passou a rodada evitando.

---

## 5 · COUNTRY COVERAGE

> ⚠️ **Os totais de registro NÃO são comparáveis entre si.** ES publica o
> conjunto corrente; IT guarda o revogado desde 1970; FR publica autorizado +
> retirado. Comparar totais brutos mede política de publicação de ministério,
> não mercado.

| métrica | **ES** | **IT** | **FR** |
|---|---:|---:|---:|
| `TRADEMARKS` testadas | 5.579 | 5.690 | 7.612 |
| `LOCAL_REGISTRATIONS` | 3.084 | 17.695 | 15.140 |
| … em vigor | 1.993 | 3.715 | 2.691 |
| **`LINKED_CHAINS`** | **209** | **334** | **1.140** |
| `TM_BEFORE_REG` | 158 | 227 | 702 |
| `REG_BEFORE_TM` | 51 | 107 | 407 |
| `SAME_DATE` | 0 | 0 | 1 |
| `REG_DATE_MISSING` | 0 | 0 | **30** |
| `TM_DATE_MISSING` · `BOTH_MISSING` · `NOT_COMPARABLE` | 0 | 0 | 0 |
| **soma das classes** | **209** ✓ | **334** ✓ | **1.140** ✓ |
| `UNLINKED` | 5.335 | 5.219 | 6.188 |
| `PARTIAL` | 24 | 111 | 315 |
| **`STRICT_MATCH_FALSE_LINKS_REJECTED`** | **9** / 242 | **38** / 483 | **79** / 1.534 |
| **`LOOSE_CANDIDATE_LINKS_REJECTED`** | **151** / 441 | **828** / 1.364 | **1.103** / 1.821 |
| subcontagem por antecessor | 0 | **1.351** | **1.458** |

**`NOT_MEASURED`: nenhum.** Os três foram medidos.

### ⚠️ A conservação, verificada por `assert` e não por leitura

A primeira redação publicou `FR LINKED_CHAINS = 1140` ao lado de `702 + 407`.
**702 + 407 = 1109.** Trinta e uma cadeias ficavam invisíveis porque a soma nunca
era conferida. Medidas e classificadas:

| classe | n | causa, provada na fonte |
|---|---:|---|
| `REG_DATE_MISSING` | **30** | os 30 registros são `RETIRE` e o campo `Date de première autorisation` está **vazio no CSV bruto** do E-Phy. Conferido registro a registro. No registro francês inteiro, **280 de 15.140** estão assim |
| `SAME_DATE` | **1** | as duas datas existem e são iguais |

`antecedencia()` agora carrega um `assert` que **recusa** qualquer decomposição
que não feche. Nenhuma classe foi criada para fechar soma: `DATE_NOT_COMPARABLE`
existe e está em **zero** nos três — ele é reservado para data que a fonte
declarou e o *nosso leitor* não entendeu, que é defeito nosso e precisa aparecer
com esse nome.

### ⚠️ As DUAS métricas de falso link — nenhuma substitui a outra

Provado por medição: **os universos não se tocam** (0 nomes na interseção, nos
três países).

| | `STRICT_MATCH_FALSE_LINKS_REJECTED` | `LOOSE_CANDIDATE_LINKS_REJECTED` |
|---|---|---|
| **ES** | **9** de **242** | **151** de **441** |
| universo | as 242 marcas cujo nome **É** chave do registro | as 5.266 marcas cujo nome **não é** chave |
| estágio | **PRODUÇÃO** — é o casador que gera os links | **CONTRAFACTUAL** — nunca gerou link |
| regra | nome idêntico, titular de outro grupo | casamento por **prefixo**, titular divergente |
| o que mede | o que a régua **recusou tendo formado** o candidato | o que ela **nem chega a formar** |

`HOUVE_MUDANCA_METODOLOGICA = NO` · `UMA_SUBSTITUIU_A_OUTRA = NO` ·
**`ES_REGRESSION_PRESERVED = YES`**

> Trocar um pelo outro produziria dois erros ao mesmo tempo: a régua pareceria
> 17× mais falha, ou o ganho de exigir titular pareceria 17× menor.

### As três assimetrias que impedem somar as colunas ingenuamente

1. **A França tem uma superfície a mais.** `seconds noms commerciaux` do E-Phy é
   o equivalente das denominações comuns espanholas — o mesmo registro sob outro
   nome. Ele entra como `ALT_NAME` e **aumenta a chance de casamento**. Parte da
   vantagem francesa (1.140 × 209) é instrumento, não mercado.
2. **IT e FR subcontam o concorrente.** 1.351 e 1.458 registros estão sob razões
   sociais **antecessoras** (`AVENTIS`, `DU PONT`, `CIBA GEIGY`, `DOW ELANCO`,
   `MONSANTO`). Dobrá-las nos grupos de hoje seria afirmação societária que este
   piloto não tem. Ficam contadas e não agrupadas.
3. **A profundidade histórica difere.** A Itália guarda desde 1970; isso infla
   `LOCAL_REGISTRATIONS` e também `REG_BEFORE_TM`.

---

## 6 · TRADEMARK WATCH

| | |
|---|---|
| **rota** | `POST tmdn.org/tmview/api/search/results` — sem chave, sem autenticação |
| **cobertura** | ES (OEPM) · IT (UIBM) · FR (INPI) · EM (EUIPO) |
| **evidência por marca** | 14 campos + `tmOfficeURL` de volta à ficha oficial |
| **estado** | `PROMISING` — ver §2 |

### ⚠️ A trava que precisa viajar junto

A API **ignora em silêncio** parâmetro cujo nome ela não conhece: `applicantName`
devolve **HTTP 200 e 1.068.402 resultados** — a Espanha inteira. O nome correto é
`appName`.

`ip_tmview.buscar()` roda uma consulta de **CONTROLE sem filtro** por escritório
e **RECUSA** o resultado quando os totais coincidem. Sem essa trava, o piloto
teria publicado *"1.068.402 marcas da Syngenta"*.

> **`HTTP 200 ≠ PEDIDO ENTENDIDO`** · **`SEM FILTRO ≠ SEM RESULTADO`**

### TMview é espelho

Ausência aqui é `NOT_OBSERVED_IN_TMVIEW`, nunca "a marca não existe". **O atraso
de sincronização entre escritório nacional e TMview não foi medido.**

---

## 7 · REGULATORY WATCH

```
REGULATORY_CHANGE_IN_THIS_INTERVAL = 0 OBSERVED
INTERVALO                          = 29/08/2026 → 31/08/2026
COMPARAÇÕES                        = 40.092 campo a campo
REGULATORY_CHANGE_CADENCE          = NOT_PROVED
```

**Dois dias são dois dias.** Zero mudanças nessa janela não mede a frequência com
que o registro se mexe.

| país | change events | por quê |
|---|---|---|
| ES | 0 emitidos | `NEW_VERSION_IDENTICAL` — duas versões arquivadas, idênticas |
| IT | não emitidos | `BASELINE_ESTABLISHED` — **uma** captura |
| FR | não emitidos | `BASELINE_ESTABLISHED` — **uma** captura |

**O que É publicável hoje:** 11.675 **fatos datados** que a própria fonte declara
— inscrição, caducidade, limite de venda, modificação.
`EXPIRY ≠ WITHDRAWAL`. `REGISTRATION_MODIFIED` diz **que** mudou e **quando**,
nunca **o quê**.

**A França não emite `EXPIRY`:** o E-Phy publica **retirada**, que é outra coisa.

---

## 8 · TRADEMARK × REGISTRATION

**`B` → `PROVED`**, nos três países, com a régua idêntica.

```
1 · o nome normalizado da marca == o nome do produto no registro
2 · o grupo do titular da marca == o grupo do titular do registro
```

`PROVED` · `PARTIAL` · `REJECTED_HOLDER_MISMATCH` · `NOT_KNOWN`.
Normalização toca acento, caixa e pontuação — **nunca** sufixo, número ou
prefixo (`FENOVA S ≠ FENOVA SUPER`).

**Regressão de ouro, que não pode ser removida:** `URBOLE`.

**O limite honesto:** 16.742 marcas ficaram `NO_LINK` nos três países somados.
A maioria esmagadora das marcas de um concorrente **não** tem registro local de
mesmo nome — e isso é resultado, não falha do instrumento.

---

## 9 · PATENT DEMOTION

Ver §4. **Não voltar a esta camada nesta missão.**

---

## 10 · TIMELINE READINESS

| | |
|---|---|
| cadeias com link `PROVED` | **1.683** |
| camadas por cadeia | **2 de 5** |
| cadeias fim-a-fim | **0** |
| `LEAD_DAYS` defensáveis | 1.063 · mediana **1.546 dias** · faixa 1 a 13.004 |
| pares que **refutam** a hipótese | **565**, gravados na base |

**A regra de defensabilidade:** o depósito usado tem de ser o **mais antigo**
daquela marca naquele grupo (remove redepósito) **e** a ordem tem de ser
marca→registro. **Sem corte de tempo arbitrário** — um limiar a dedo produziria a
antecedência que se quisesse.

Os 565 pares em que o registro precede a marca **continuam na base**. Apagá-los
produziria 100% de confirmação.

---

## 11 · CONVERGENCE READINESS

**As duas camadas entram como FATOS SEPARADOS.** Não é preciso ter o link
marca→registro para usar qualquer uma delas.

| fato | eventos | chaves de junção |
|---|---:|---|
| `COMPETITOR_BRAND_EVENT_OBSERVED` | 9.661 | `COMPETITOR` · `COUNTRY` · **`BRAND`** · `EFFECTIVE_DATE` |
| `COMPETITOR_LOCAL_REGISTRATION_OBSERVED` | 11.675 | `COMPETITOR` · `COUNTRY` · `REGULATORY_ID` · `EFFECTIVE_DATE` |
| `COMPETITOR_TIMELINE` | 1.683 cadeias | só onde o link é `PROVED` |

**A chave nova que esta camada traz ao SINTONIA EAME é `BRAND`** — ela não existe
em nenhuma outra camada.

### O que ainda **não** liga

`CROP` e `ISSUE`. Nenhum dos três registros nacionais traz cultura e alvo neste
dataset. **Sem eles, a camada de concorrente não entra no eixo cultura×praga** —
que é o coração da convergência. Este é o próximo trabalho, e não um detalhe.

**Não criar score.** Nenhum número desta camada é ranking ou ameaça.

---

## 12 · META JOIN READINESS

```
META_CANONICAL_SOURCE_COMMIT = acfd987   (declarado pela própria missão Meta)
ESTADO DA CAPACIDADE META    = ACCEPTED · PARKED
ONDE  branch claude/eame-meta-competitor · data/samples/META-EAME/
```

> ⚠️ A primeira entrega escreveu que "não existe Meta no repositório".
> **Errado, e corrigido.** A Meta congelou, e o join foi **reexecutado** sobre a
> base congelada.

### A fonte é um COMMIT, não a ponta de uma branch

Uma branch se move. Um join que aponta para a ponta responde diferente a cada
hora sem que ninguém tenha mudado nada. `concorrente_tres_camadas.py` lê o
commit fixo **`acfd987`**, que é o que `META-HANDOFF-FREEZE-V1.json` declara como
`meta_canonical_freeze_commit`.

**Uma sutileza que virou trava:** em `acfd987` o handoff já existia, mas ainda
não podia nomear o próprio commit — o campo entrou depois, em `68f3cd8`. Então a
**declaração** é lida da ponta e o **dado** é lido do congelado. O que impede a
ponta de contrabandear dado novo é uma comparação de blob: se o arquivo tiver
mudado entre os dois, o script **para**. Verificado — mesmo blob.

E os nomes crus deixaram de ser número cravado no código: são **contados** nos
blocos e **conferidos** contra `snapshot_1.raw_product_names_proved` do handoff
da Meta. Divergência para o script. Bateu: **151 = 151**.

### ⚠️ A junção foi MEDIDA, depois **AUDITADA** — e o número caiu

A primeira medição desta junção anunciou **36 cadeias de três camadas**. Ela
casava **apenas o nome** do produto anunciado com o nome da marca. Só o nome —
exatamente a falha que `URBOLE` existe para impedir.

O red team exigiu **concordância de titular nas TRÊS pontas** e o **mesmo país**
nas três:

```
company da Meta == grupo do titular da marca == grupo do titular do registro
```

### ⚠️ Duas unidades, duas contas — e elas **não se subtraem**

`TUPLA` e `PRODUTO` são coisas diferentes. O mesmo produto anunciado por um
concorrente em dois países é **duas tuplas e um produto**. Cada decomposição
fecha por `assert`, separadamente.

**Unidade `TUPLA` (competidor, país, produto normalizado)**

| | |
|---|---:|
| `THREE_LAYER_CANDIDATES_TOTAL` | **174** |
| `THREE_LAYER_CHAIN_PROVED_TUPLES` | **36** |
| `THREE_LAYER_CHAIN_REJECTED_TUPLES` | **0** |
| `THREE_LAYER_CHAIN_NOT_KNOWN_TUPLES` | **138** |
| soma | **174** ✓ |

**Unidade `PRODUTO` (nome normalizado)**

| | |
|---|---:|
| `META_RAW_PRODUCT_NAMES` | **151** (contados e conferidos com a Meta) |
| `META_PRODUCTS_TOTAL` | **147** |
| `META_PRODUCTS_WITH_PROVED_THREE_LAYER_CHAIN` | **29** |
| `META_PRODUCTS_WITHOUT_PROVED_THREE_LAYER_CHAIN` | **118** |
| soma | **147** ✓ |

**Por que 147 e não 151.** Quatro pares são o mesmo nome em caixas diferentes —
`SPECTRUM`/`Spectrum`, `VELIFER`/`Velifer`, `GAXY`/`Gaxy`, `KUSABI`/`Kusabi` — e
colapsam ao normalizar. **151 − 4 = 147**, exato.

> `151 − 29` seria subtração entre um total de **nomes crus** e uma contagem de
> **produtos normalizados**. Não é uma conta; é mistura de unidades.

### A linhagem, corrigida sem apagar nada

| | antes | agora |
|---|---|---|
| commit Meta | `4cee050` | **`acfd987`** |
| cartões | 1.111 | **1.340** |
| nomes crus | 145 | **151** |
| produtos normalizados | 141 | **147** |
| **cadeias provadas** | 35 tuplas · 28 produtos | **36 tuplas · 29 produtos** |

```
OLD_RESULT        = SUPERSEDED_BY_CORRECTED_META_INPUT
LINEAGE_CORRECTION = COMPLETE
```

> O resultado anterior **não é inválido**. Foi medido corretamente sobre o input
> daquele momento. O que mudou foi **o ponteiro da fonte** — e só ele: o casador,
> o portão URBOLE, a normalização e as três concordâncias obrigatórias são
> exatamente os do commit congelado do Foresight, `25194e3`.

### ⚠️ Um defeito meu que a conferência de unidade encontrou

Os blocos da Meta usam `{"state": "NOT_KNOWN"}` para dizer **"nenhum produto
provado neste bloco"**. Meu extrator leu `state` como se fosse nome de produto e
criou **cinco tuplas fantasma**. Nada "quebrava" — elas caíam todas em
`NOT_KNOWN` — só o denominador ficava 5 maior que a realidade. **Ausência
declarada por outra missão nunca entra como observação.** O descarte agora é
explícito e vem listado no artefato.

### `URBOLE_GUARD = PASS`, e ele foi **exercido**

Zero recusas no dado real e um portão sem dentes dão o mesmo resultado na tela.
Por isso a recusa foi **provocada**: injetando *"a Meta anuncia URBOLE como
SYNGENTA na Espanha"*, o classificador devolve `THREE_LAYER_CHAIN_REJECTED` e
nomeia `ADAMA Agriculture España S.A.` como o titular conflitante.

**Colisões de nome entre as 35 provadas: nenhuma.**

### O estado destas cadeias

```
PRELIMINARY_CROSS_BRANCH_JOIN = PROVED
FINAL_REFRESH_INPUT           = NO
```

A Meta é **fonte externa** a esta missão e **seu handoff ainda não foi congelado
pelo coordenador**. Entrada final de refresh só depois do handoff canônico da
Meta. A leitura foi `git show` somente-leitura sobre
`claude/eame-meta-competitor` — **nenhum merge, nenhum checkout, nenhuma
alteração de índice**.

Exemplos provados: `Revycare` (BASF ES, reg ES-01263) · `Revyona` (ES-01394) ·
`Serifel` (ES-00558) · `Belanty` (BASF FR, AMM 2210797).

**Chave de junção:** `BRAND` × `COUNTRY` × `TIME`.

---

## 13 · CREATOR JOIN READINESS

```
CREATOR_DATA_AVAILABLE_IN_THIS_SNAPSHOT = NO
ESTADO REAL DA CAPACIDADE               = FROZEN_WAITING_FOR_INTELLIGENCE
ONDE  branch claude/eame-agro-creators-map-77c4ld
      docs/creators/HANDOFF-INTELLIGENCE-CREATOR-MAP-EAME.md
```

O Creator Map declara, no próprio handoff, que a chave de junção com
**COMPETITION** é **`BRAND × RELATION_TYPE`**, com 4 casos de concorrente já
mapeados.

**Esta camada oferece exatamente `BRAND`.** As duas pontas encaixam.

> ⚠️ Também aqui a primeira entrega escreveu "não há Creator Map". **Errado.**

---

## 14 · SUPABASE READINESS

```
MIGRATION_READY          = YES
TESTED_IN_DISPOSABLE_DB  = YES  (portão concorrente-portao, Postgres 16 descartável)
APPLIED_TO_EAME_SUPABASE = NO
```

| artefato | o que é |
|---|---|
| `019_evento_do_concorrente.sql` | `evento_concorrente` + `evento_concorrente_link` |
| `020_views_do_concorrente.sql` | 5 read models |
| `COMPETITOR-FORESIGHT-2026-08-30.sql` | 19.702 eventos · 1.696 links · determinístico |

**A migração não cria dono de nada.** Aponta para `organizacao`,
`registro_regulatorio`, `catalogo_produto`, `canal`, `crop`, `issue`,
`raw_asset`. Marca é **texto num evento**, não tabela.

### As duas travas centrais

| trava | o que impede |
|---|---|
| `lead_days_exige_identidade_provada` | antecedência sobre identidade não provada |
| `defensavel_exige_ordem_e_valor` | publicar a refutação como confirmação |

E `meta_e_creator_apontam_para_o_dono`: nenhuma linha de META ou CREATOR pode
existir sem apontar para o `canal` que já tem dono em outra missão.

**Nenhum ajuste de schema foi necessário para IT e FR** — o tipo `pais` já os
previa. A migração não mudou entre a rodada 1 e esta.

**Aplicar em produção é decisão de quem tem a chave, com o arquivo na mão.**

---

## 15 · EXACT CLAIMS ALLOWED

✅ "A `<CONCORRENTE>` depositou a marca `<X>` em `<escritório>` em `<data>`, sob
as classes `<n>`." — com URL da ficha oficial.

✅ "A `<CONCORRENTE>` detém a autorização `<ID>` em `<país>`, inscrita em
`<data>`, com caducidade declarada em `<data>`."

✅ "A marca `<X>` e o registro `<ID>` têm o mesmo nome **e** o mesmo grupo
titular — o link está `PROVED`."

✅ "Nestes três registros nacionais, a marca precedeu o registro em 1.087 de
1.652 pares ligados." — **sempre com o denominador**.

✅ "Não conseguimos ligar esta marca a nenhum registro local." (`NO_LINK`)

✅ "`NOT_JOINED_IN_THIS_MISSION`" para catálogo, Meta e creator.

---

## 16 · EXACT CLAIMS PROHIBITED

❌ "O concorrente vai lançar o produto `<X>`."
❌ "A marca prevê o registro" / "temos aviso prévio de lançamento."
❌ "A marca dá ~4 anos de antecedência útil."
❌ "O registro não se mexe no dia a dia" / "o registro é estático."
❌ "`PATENT_WATCH = REFUTED`."
❌ "Não existe Meta / Creator no repositório."
❌ "O concorrente não anuncia" / "não publica catálogo."
❌ Qualquer soma de `LOCAL_REGISTRATIONS` entre países como medida de mercado.
❌ Qualquer score, ranking ou índice de ameaça.
❌ Qualquer afirmação de venda, volume, preço, share ou investimento.

---

## 17 · O QUE FAZER A SEGUIR, EM ORDEM

1. **Segunda captura do TMview** (D+7, D+30). É o único caminho para promover
   `A` de `PROMISING` a `PROVED`, e não exige código novo.
2. **Ligar `CROP` e `ISSUE`.** É o bloqueio real da convergência. As fichas
   individuais de ES e as etiquetas de IT/FR trazem cultura e alvo; o dataset
   aberto, não.
3. **No refresh final: montar as 36 cadeias de três camadas** (36 tuplas ·
   29 produtos) sobre a Meta congelada em `acfd987`. Já estão medidas,
   auditadas e reexecutadas sobre a base corrigida.
4. **Não voltar a patentes.** Não ampliar concorrentes. Não alterar casco.

---

## 18 · ARTEFATOS

| arquivo | o que preserva |
|---|---|
| `data/samples/COMPETITOR-EAME-PARIDADE.json` | os três países, mesma régua |
| `data/samples/COMPETITOR-EAME-VEREDITOS.json` | um veredicto por capacidade |
| `data/samples/COMPETITOR-IP-TMVIEW.json` | 9.661 marcas + portão do filtro |
| `data/samples/COMPETITOR-REGULATORY-EVENTS.json` | portão de versão + 11.675 fatos |
| `data/samples/COMPETITOR-CROSSWALK.json` | o crosswalk espanhol, inalterado |
| `data/samples/COMPETITOR-EVENTS.json` | 21.336 eventos + 1.683 timelines |
| `data/samples/COMPETITOR-PATENT-DEMOTE.json` | a rota refutada, com os 5 casos |
| `data/samples/COMPETITOR-PILOT-AMOSTRA.json` | a contagem que escolheu os 6 |
| `scripts/registro_local.py` | os três registros na forma comum |
| `scripts/concorrente_paridade.py` | o mesmo teste nos três países |
| `scripts/concorrente_vereditos.py` | os veredictos e os pares semânticos |
| `scripts/ip_tmview.py` · `concorrente_*.py` | a cadeia inteira |
| `supabase/migrations/019_*.sql` `020_*.sql` | tabela derivada + read models |
| `supabase/importacoes/COMPETITOR-FORESIGHT-2026-08-30.sql` | 19.702 + 1.696 |
| `supabase/tests/regressoes_concorrente.sql` `mutacao_concorrente.sql` | 32 afirmações + 7 mutações |
| `data/samples/COMPETITOR-THREE-LAYER-AUDIT.json` | o red team da junção Meta |
| `scripts/concorrente_tres_camadas.py` | a auditoria + o portão URBOLE exercido |
| `tests/test_concorrente.py` | 73 testes |
| `.github/workflows/concorrente-portao.yml` | onde o SQL é realmente provado |
| `docs/piloto/COMPETITOR-FORESIGHT-PILOT.md` | o relatório da rodada 1 (A–S) |

---

**`FROZEN_WAITING_FOR_INTELLIGENCE`** · nada aplicado em produção · casco
intocado · nenhuma intenção de concorrente inventada.
