# PRONTIDÃO DA COLLECTION PARA A INTELLIGENCE AGRÍCOLA — V1

```
MISSAO        C-INT-AGRO-BENCH-01
ESPECIE       AUDITORIA — EVIDENCIA DE UM COMMIT
MEDIDO_EM     2026-09-13
BASE          claude/raw-observation-identity-3jbwco @ f888776d
INSTRUMENTO   provas/auditoria_agro_fronteira.py   (nao-invasivo, nao escreve nada)
```

> **A Collection não foi alterada por esta missão.** Zero runtime, zero
> migration, zero contrato, zero Admission. Isto mede.
> E mede **depois** de descobrir os requisitos externos — nunca antes
> (`§27` do enunciado).

---

## 0 · OS SEIS ATAQUES, CORRIDOS CONTRA O CÓDIGO REAL

Todos reproduzíveis: `python3 provas/auditoria_agro_fronteira.py`.

### ATAQUE A · `FACT STRUCTURE SURVIVAL`

Um facto agronómico descartável, com os campos que os benchmarks externos
exigem de uma observação defensável (MIAPPE/Crop Ontology, EFSA, EPPO, BBCH,
PP1/248), passado pelo caminho real
`admissao.decidir → admissao.pronto_para_inteligencia`:

```
estagio reconhecido ........ FATO          (as MARCAS_DE_FATO ja existem no codigo)
porta ...................... SIM
campos na entrada .......... 39
campos no READY ............ 12
sobrevivem com valor ....... 9
PERDIDOS ................... 30
```

Os 30 perdidos:

```
active_substance · active_substance_cas · bbch · claim_id · confidence_level ·
crop · crop_eppo · denominator · design_prevalence · diagnostic_method · doi ·
method · method_sensitivity · nuts · object · parent_artifact_id ·
phenological_stage · predicate · problem · problem_eppo · product ·
published_at · registration_id · sample_size · scale · subject ·
target_population · unit · url · value
```

```
O `estagio` DO ITEM E RECONHECIDO COMO «FATO» — O CODIGO JA SABE O QUE E UM
CLAIM (`claim_id` · `subject` · `predicate` · `fact_id`) —
E A SAIDA NAO TEM ONDE POR NENHUM DOS TRES.
```

**`ITEM_ID` permite recuperar deterministicamente o objecto estruturado?**
`ITEM_ID = str(item.get("id") or item.get("url") or "?")`. Ele identifica a
unidade que passou a porta. **Não há, no READY, nenhuma referência a um objecto
estruturado** — porque o objecto estruturado agronómico não existe. Para a única
espécie ligada (`SOCIAL_CONTENT`), o caminho de volta existe e é determinístico,
por `RAW_OBSERVATION_ID`. Para as outras quatro espécies com store
(`SOCIAL_COMMENT`, `SOCIAL_TRANSCRIPT`, `REGULATORY_REGISTRATION`,
`CATALOG_PRODUCT_DOCUMENT`) a rota forward não liga.

### ATAQUE B · `PUBLICATION TIME`

```
pergunta do tempo, directa ... SIM · «tem tempo do fato» · {"quando": "2026-06-30"}
                               (o item so tem `published_at`)
essa evidencia chega ao livro  False
campo generico `data` vira FACT_TIME: '2026-06-30'
FACT_TIME no READY ........... 'NAO SEI'
```

**Três defeitos distintos, e são três.**

```
B1  `admissao.py::_tem_quando` responde «TEM TEMPO DO FATO» a um item cujo
    unico tempo e a data de PUBLICACAO.
    A COL-LAW-031 escreve, em caixa alta: «FACT_TIME = PUBLISHED_AT E PROIBIDO.
    Nao por conveniencia, nao por omissao, NAO POR FALLBACK.»
    A propria Biblia ja o marcou como VIOLACAO VIVA (gap G-01, defeito C-001) —
    esta medicao confirma que continua viva, e mostra que ela agora afecta
    tambem o estagio FATO, que e o estagio a que a pergunta SE APLICA.

B2  A EVIDENCIA DESSA RESPOSTA NAO CHEGA AO LIVRO DE DECISOES.
    `decidir()` devolve apenas a evidencia da ULTIMA pergunta. As respostas SIM
    das perguntas anteriores — e a prova de que uma delas foi satisfeita por uma
    data de publicacao — desaparecem.
    A COL-LAW-042 exige `evidence` na decisao. Ela esta la; e a evidencia certa
    nao esta.
        UM PORTAO QUE PASSA POR UMA RAZAO QUE NAO REGISTA
        E UM PORTAO QUE NINGUEM CONSEGUE AUDITAR.

B3  O CAMPO GENERICO `data` VIRA `FACT_TIME` NO CONTRATO DE SAIDA.
    `pronto_para_inteligencia` faz `item.get("fact_time") or item.get("data")`.
    `data` nao declara DE QUE TEMPO E. Um coletor que escreva `data` com a data
    do documento produz um FACT_TIME falso, e ele sai carimbado como facto.
```

E a ironia que fecha o ataque: no caso B, a porta **passa** por causa de
`published_at`, e o contrato **escreve `NAO SEI`**. As duas metades do sistema
dão respostas opostas à mesma pergunta, na mesma passagem.

### ATAQUE C · `STRUCTURED AGRONOMIC CONTEXT`

23 campos agronómicos testados (cultura, problema, produto, substância,
fenologia, método, valor, unidade, escala, denominador, NUTS, DOI…):

```
com chave propria no READY ... 0   de 23
so no TEXTO .................. 6   (aparecem por acaso, dentro da frase)
```

```
A INTELLIGENCE AGRICOLA SO PODE OBTER CULTURA, PROBLEMA, METODO, VALOR E
UNIDADE REPARSEANDO O TEXTO. NAO HA OUTRA VIA.
E REPARSEAR TEXTO NAO E LER UM CAMPO: E ADIVINHAR OUTRA VEZ O QUE A FONTE JA
TINHA DITO — COM UM SEGUNDO CEREBRO, SEM AUDITORIA E SEM VERSAO.
```

### ATAQUE D · `IDENTITY`

```
raw_asset_id -> RAW_OBSERVATION_ID .... 9901        ✅ PRESERVADO
id -> ITEM_ID ......................... AUDIT-FATO-1 ✅
source_id -> SOURCE_ID ................ IT-T3-005   ✅
claim_id .............................. PERDIDO
parent_artifact_id .................... PERDIDO
doi ................................... PERDIDO
registration_id ....................... PERDIDO
crop_eppo ............................. PERDIDO
problem_eppo .......................... PERDIDO

item sem `id` nem `url` -> ITEM_ID = '?'     ⚠️ COL-LAW-034 PROIBE
```

**`RAW_OBSERVATION_ID` está preservado, e é uma vitória recente e real** — foi
fechada em `C-READY-LINEAGE-BEFORE-SCALE-V1`, contra PostgreSQL real, e a prova
está escrita na Bíblia: `READY_TO_RAW` passou de `AMBIGUOUS — 2 candidatos` a
`PROVEN — 1, por id canónico`.

**E o achado novo:** um item com `source_id` mas sem `id` e sem `url` passa a
porta e sai com `ITEM_ID = "?"`. A `COL-LAW-034` diz, sem margem: *«`"?"` e a
string vazia **NÃO DEVEM** ser usados como identidade.»*

### ATAQUE E · `LÉXICO DO UNIVERSO`

O mesmo facto, o mesmo código EPPO, duas redacções:

```
"Sintomo di peronospora al 12,5% delle foglie..."   -> SIM
"Peronospora osservata al 12,5% delle foglie..."    -> NAO_SEI
mesmo EPPO nos dois: True
a decisao muda sem o facto mudar: True
```

`PERONOSPORA` não está no léxico de T3. A doença mais importante da vinha
europeia. E o código do próprio ficheiro já diagnosticou a causa:

> *«a arquitetura certa e CONCEITO -> TERMO LOCAL (um `WHEAT_SEPTORIA` com as
> suas formas em IT/ES/FR/EN), e ela NAO existe aqui.»*

E a segunda metade do achado: **a arquitectura CONCEITO → TERMO LOCAL existe
nesta casa, noutra gaveta.** `data/samples/X-007-canonical-agro-dictionary.json`
tem 105 pares com `ORIGINAL_TARGET` → `EPPO_TARGET` verificados contra a EPPO
Global Database. As duas peças não se falam.

### ATAQUE F · `VOCABULÁRIO DA FRONTEIRA`

```
contrato comum (ingresso.PARA_A_PORTA) ..... 10 nomes
  ARTIFACT_TYPE · COLLECTED_AT · FACT_LOCATION · FACT_TIME ·
  PARENT_ARTIFACT_ID · PARENT_SHA256 · PUBLISHED_AT · SOURCE_ID ·
  SOURCE_LOCATION · SOURCE_URL

a rota forward real poe no item ............ 9 nomes
  SOURCE_ID · ARTIFACT_TYPE · PARENT_SHA256 · PARENT_ARTIFACT_ID ·
  id · texto · url · captured_at · raw_asset_id

campos agronomicos no contrato comum ....... NENHUM
campos agronomicos na rota forward ......... NENHUM
FACT_TIME na rota forward .................. False
FACT_LOCATION na rota forward .............. False
```

```
O CONTRATO DE SAIDA TEM 12 CAMPOS.
A ROTA REAL SO CONSEGUE PREENCHER 9 DELES.
FACT_TIME, FACT_LOCATION E SOURCE_LOCATION SAIEM «NAO SEI» POR CONSTRUCAO
NESTA ROTA — NAO PORQUE A FONTE NAO SAIBA, MAS PORQUE O ITEM NAO OS CARREGA.
```

---

## 1 · «NÃO ESTÁ NO READY» NÃO É «NÃO EXISTE»

O `§28` do enunciado exige esta separação, e ela muda o diagnóstico
completamente. Medido, camada a camada:

| informação | RAW | DERIVED | STRUCTURED | READY | estado |
|---|---|---|---|---|---|
| bytes do documento | ✅ `raw_asset` + `sha256` | — | — | — | `PROVEN_UPSTREAM_BUT_NOT_READY` (por desenho, e está certo) |
| identidade da observação | ✅ `raw_asset.id` | ✅ | ✅ | ✅ `RAW_OBSERVATION_ID` | `PROVEN_AT_READY` |
| espécie da evidência | ✅ contrato de fonte (`EVIDENCE_CLASS`, 13 fontes) | ✖ | ✖ | ✖ | **`COLLECTED_BUT_LOST`** |
| `FACT_TIME` | ✅ lei + contrato comum | ✅ | ✅ | ⚠️ campo existe; rota forward não o preenche | `PROVEN_UPSTREAM_BUT_NOT_READY` |
| `FACT_LOCATION` | ✅ lei + migration 015/018 | ✅ | ✅ | ⚠️ idem | `PROVEN_UPSTREAM_BUT_NOT_READY` |
| cultura (EPPO) | ✅ `public.crop.eppo_code` · `X-007` | ✅ | ✅ `crop` | ✖ | **`COLLECTED_BUT_LOST`** |
| problema (EPPO) | ✅ `public.issue.eppo_code` + `classe` | ✅ | ✅ `issue` | ✖ | **`COLLECTED_BUT_LOST`** |
| termo original + normalizado | ✅ `X-007` (`ORIGINAL_*` + `CANONICAL_*` + `MATCH_TYPE` + `EVIDENCE`) | — | parcial (`crop.nome_es`) | ✖ | **`COLLECTED_BUT_LOST`** |
| registo regulatório | ✅ | ✅ | ✅ `registro_regulatorio` (com `fonte_versao` na chave) | ✖ | `PROVEN_UPSTREAM_BUT_NOT_READY` |
| uso autorizado | ✅ | parcial | ⚠️ `registro_uso` = **4 eixos**, não 6 | ✖ | `RAW_ONLY` para os 2 eixos que faltam |
| valor · unidade · denominador | ✖ na coleta | ✖ | ⚠️ existe em `public.observacao` (`base_denominador NOT NULL`) — **camada analítica, sem writer de runtime** | ✖ | `NOT_COLLECTED` |
| método / escala | ✖ | ✖ | ✖ | ✖ | `SOURCE_DOES_NOT_PROVIDE` (nas 13 fontes italianas) |
| população-alvo · design prevalence · sensibilidade | ✖ | ✖ | ✖ | ✖ | `SOURCE_DOES_NOT_PROVIDE` |
| BBCH / fenologia | ✖ | ✖ | ⚠️ `010_calendario_agronomico` existe | ✖ | `NOT_COLLECTED` |
| DOI | ✅ quando a fonte o dá | ✅ | ✖ | ✖ | **`COLLECTED_BUT_LOST`** |
| limite de talhão / variedade / sementeira | — | — | — | — | `INTERNAL_DATA_REQUIRED` |
| identidade do agricultor · área · compras | — | — | — | — | `INTERNAL_DATA_REQUIRED` |

### O achado que reorganiza tudo

> ## O PROBLEMA DESTA CASA NÃO É NÃO TER O DADO. É PERDÊ-LO NA ÚLTIMA PORTA.

Sete das entradas acima são `COLLECTED_BUT_LOST` ou
`PROVEN_UPSTREAM_BUT_NOT_READY`. Apenas quatro são `NOT_COLLECTED`, e duas
delas são `SOURCE_DOES_NOT_PROVIDE` — que **não é um bug da Collection**
(`§41` do enunciado).

E a prova mais dura dessa frase é do schema:

```
public.observacao  (migration 005, camada analitica)
    valor · unidade · base_denominador NOT NULL · base_descricao NOT NULL ·
    camada in (FIELD, SCIENCE, VOICE, MEDIA, COMPETITOR, REGULATORY) ·
    crop_issue_id · geografia_id · periodo · rule_version

    comment: «Obrigatorio. O Brasil ja travava isso em
              termos_medicoes.base_comentarios/base_pessoas.»

A TABELA DE DESTINO EXIGE DENOMINADOR, UNIDADE, CAMADA E PAR CULTURA-PROBLEMA.
O CONTRATO DE ENTREGA DA COLLECTION NAO CARREGA NENHUM DOS QUATRO.
E ELA NAO TEM WRITER DE RUNTIME — SO UMA FIXTURE.
```

Uma coluna `NOT NULL` sem fonte a montante tem dois destinos possíveis: nunca
ser preenchida, ou ser preenchida com um número inventado. **Os dois são piores
do que o estado actual, e é por isso que isto é um P0 e não um pedido de
funcionalidade.**

---

## 2 · A MATRIZ FINAL, POR CAPACIDADE (`§38`)

| CAPABILITY | REQUIRED INPUT | JOIN KEYS | REQUIRED GRANULARITY | COLLECTION STATUS | GAP | PRIVATE DATA? |
|---|---|---|---|---|---|---|
| **DISEASE / PEST** | espécie da evidência · organismo (EPPO) · cultura · lugar do facto · tempo do facto · método · valor+unidade · denominador | `(EPPO_PEST, EPPO_CROP, AREA, TEMPO)` | província/comune · dia · BBCH quando aplicável | `PARTIAL` — identidade e lugar/tempo existem a montante; **nada atravessa** | espécie da evidência `LOST`; método/denominador `SOURCE_DOES_NOT_PROVIDE` | NÃO (nível 1-2) · SIM (3-4) |
| **SCIENCE** | DOI · ensaio · variável (trait×method×scale) · desenho · local e ano do ensaio · grupo | `DOI` ≠ `trial_id` ≠ `ORCID` | estudo | `PARTIAL` — `IT-T5-002` declara `SCIENTIFIC_EVIDENCE`; DOI perde-se na fronteira | independência não mensurável | NÃO (paywall é limite) |
| **REGULATORY** | acto oficial · registo · estado · datas · substância · versão da fonte | `(pais, registration_id)` + `fonte_versao` | país · data do decreto | **`READY_UPSTREAM`** — `registro_regulatorio` tem a versão na chave; `IT-T4-001` é `REGULATORY_AUTHORIZATION` | não atravessa a fronteira | NÃO |
| **LABEL** | a tupla de SEIS da PP 1/248 + dose, n.º, intervalo, BBCH, PHI, restrições · versão do rótulo | `(registration_id, versão, índice_do_uso)` | uso | `PARTIAL` — `registro_uso` tem **4 eixos de 6**; sem dose, sem BBCH, sem PHI, sem identidade de uso | **objecto `PPP_USE` não existe** | NÃO |
| **PORTFOLIO** | registado (público) · comercial · resposta agronómica · pipeline | `registration → uso → (crop, target)` | país | `PARTIAL` — `resposta_registrada` já separa registo de disponibilidade comercial (`default NAO_SEI`) e está certo | comercial/pipeline | **SIM** |
| **COMPETITOR** | identidade da empresa · registo vs comunicação | `titular → registration` | país | `PARTIAL` — `IT-T9-008` já declara `COMPANY_CLAIM != REGULATORY_FACT` | identidade de organização sem id externo | SIM para quota/preço/canal |
| **MARKET** | série com unidade e base · período de referência · materialidade | `(commodity, NUTS, período)` | NUTS2/3 · mês/campanha | `PARTIAL` — `IT-T1-001` (ISTAT) declara `SERIE_OFICIAL_DE_PRODUCAO` | materialidade e decisão afectada | NÃO para a série |
| **FUTURE** | sinal · sujeito · horizonte · incerteza · repetição | sujeito + tempo | conforme o sujeito | `PARTIAL` — datas de caducidade são o activo forte e existem | `FUTURE_DATE` misturado com sinal fraco | NÃO |
| **OPPORTUNITY** | nível A/B/C/D + janela + uso de PPP + dono da decisão | `(crop, target, area, janela) → PPP_USE → portfolio` | província · janela | **`NO`** acima do nível A | `PPP_USE` inexistente; janela não computável sem BBCH | **SIM** para C e D |

---

## 3 · O QUE A COLLECTION JÁ FAZ BEM, E NÃO DEVE SER MEXIDO

Uma auditoria que só lista buracos mente por omissão. Isto foi medido e está
certo:

```
1. RAW_OBSERVATION_ID no READY. Fechado contra PostgreSQL real, com a prova de
   que a alternativa (procurar por sha256) era ambigua.

2. A ESPECIE DA EVIDENCIA DECLARADA NO CONTRATO DE FONTE, antes de qualquer
   execucao, com LEIS ao lado:
       AGROCLIMATIC_SIGNAL != PEST_OCCURRENCE
       REGISTRY            != FIELD_SIGNAL
       TECHNICAL_GUIDELINE != CURRENT_FIELD_SIGNAL
       COMPANY_CLAIM       != REGULATORY_FACT   (inclusive para a ADAMA)
   Isto e mais maduro do que a maioria dos sistemas comerciais estudados.

3. `fonte_versao` NA CHAVE do registo regulatorio. E exactamente o que permite
   detectar mudanca sem apagar historia.

4. `base_denominador NOT NULL` e `derivacao.limitacao NOT NULL` no schema
   analitico, com `CONFOUNDER_OPEN` como estado de primeira classe.

5. `resposta_registrada.current_commercial_availability DEFAULT 'NAO_SEI'`,
   com o comentario «disponibilidade comercial NAO se deduz de registro».
   E a lei do §18 do enunciado, ja escrita em SQL, ha migrations.

6. `lacuna_candidata` com a constraint
   `zero_precisa_de_diagnostico_antes_de_virar_lacuna`.
   O schema RECUSA que um zero vire lacuna sem alguem ter olhado a chave.

7. A PORTA DIZ NAO_SEI EM VEZ DE NAO quando o vocabulario nao chega. Isso e
   `AUSENCIA DE EVIDENCIA != EVIDENCIA DE AUSENCIA` a correr, nao a ser citada.

8. O DICIONARIO AGRO preserva ORIGINAL + NORMALIZADO + EVIDENCIA + MATCH_TYPE,
   e RECUSA dar codigo de especie a um termo de grupo.
```

```
ESTA CASA NAO TEM UM PROBLEMA DE LEIS. TEM UM PROBLEMA DE ENDERECO:
AS LEIS ESTAO ESCRITAS EM SEIS SITIOS, E A ULTIMA PORTA NAO AS CONHECE.
```

---

## 4 · VEREDITOS

```
COLLECTION_READY_FOR_AGRO_INTELLIGENCE = PARTIAL
P0_COLLECTION_CHANGE_REQUIRED          = YES
```

### Porque `PARTIAL` e não `NO`

O `§41` diz que `READY = YES` exige que a matéria-prima **seja preservada quando
a fonte a fornece** e **atravesse a fronteira sem perda crítica**. A primeira
metade cumpre-se em quase tudo: o RAW está preservado, a linhagem existe, a
identidade da observação viaja, a espécie da evidência está declarada por fonte,
o registo regulatório tem versão na chave. **A segunda metade falha**, e falha
num sítio só.

### Porque não é `YES`

```
espécie da evidência ........ COLLECTED_BUT_LOST     ← crítico
cultura / problema (EPPO) ... COLLECTED_BUT_LOST     ← crítico
FACT_TIME / FACT_LOCATION ... não preenchidos pela rota forward
FACT_TIME pode ser satisfeito por PUBLISHED_AT no portão  ← violação de lei viva
`data` genérico vira FACT_TIME no contrato de saída       ← violação nova
ITEM_ID pode sair como "?"                                ← violação de lei
```

### Porque não é `NO`

```
Nada disto exige recolher outra vez. Tudo isto ja foi colhido.
E quatro dos itens em falta sao SOURCE_DOES_NOT_PROVIDE — e
SOURCE_DOES_NOT_PROVIDE != COLLECTION_BUG.
```

---

## 5 · `AGRO_INTELLIGENCE_ARCHITECTURE_READY = NO` — as perguntas que ficam abertas (`§40`)

| eixo | fechado? | o que falta |
|---|---|---|
| identity | **quase** | `PPP_USE` não tem identidade; produto/holder sem id externo |
| ontology | ✅ | direcção pronta, limites medidos |
| time | ❌ | fenologia e janela não são computáveis; `FACT_TIME` viola a lei no portão |
| geography | **quase** | falta a versão NUTS; a escada epidemiológica não existe |
| observation semantics | ❌ | espécie da evidência não atravessa |
| method / unit / scale | ❌ | nenhuma fonte pública os dá; não há onde os pôr |
| evidence independence | ❌ | sem identidade de ensaio/dataset, não é mensurável |
| uncertainty | **quase** | leis existem; sem método/denominador não há o que quantificar |
| zero / denominator | ❌ | `ZERO_PROVED` é inalcançável; falta o vocabulário da ISPM 8 |
| promotion | ❌ | 3 de 7 portões bloqueados; 0 de 7 reversões escrevíveis |
| human validation | **quase** | graus definidos; sem dono nomeado por transição |
| regulatory truth | **quase** | o acto oficial é preservado; o `PPP_USE` não |
| opportunity requirements | ❌ | níveis A-D definidos; B em diante não é provável |
| Collection input contract | ❌ | é o P0 |

```
SEIS EIXOS ABERTOS COM DUVIDA CRITICA.
O §40 DIZ: SE HOUVER DUVIDA CRITICA, «NO».
E «NO» AQUI NAO E UM FRACASSO — E A UNICA RESPOSTA QUE PERMITE
FECHAR OS SEIS SEM PRESSA E SEM MENTIRA.
```

---

## 6 · O P0

Está escrito, separado, e endereçado ao dono da Collection:
[`../../docs/operacao/COLLECTION-P0-CHANGE-REQUEST.md`](../../docs/operacao/COLLECTION-P0-CHANGE-REQUEST.md).

```
ONE CONCEPT -> ONE OWNER.
ESTA MISSAO NAO CONSERTA A COLLECTION. ELA ENTREGA A MEDICAO.
```
