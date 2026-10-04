# `ALLOWED_STRUCTURED_TARGETS` — o que cada fonte está autorizada a produzir

**C-PLAN-A5.2 · decisão de contrato · 2026-09-10 · ramo `claude/raw-observation-identity-3jbwco`**

> **Nada foi implementado.** Zero runtime, zero banco, zero migration, zero `source_document`,
> zero T-32, zero registo T-06, zero Admission, zero READY, zero System Map, zero Bíblia.
> **E nenhum contrato de fonte foi alterado.**

Fecha o bloqueio **D1**: *`ALLOWED_STRUCTURED_TARGETS` não existe nos contratos de fonte.*

```
LOCAL_HEAD = REMOTE_HEAD = 2e1c80ced485c13a2ecc9dd124cc629692a24109
WORKTREE   = limpa   ·   DIVERGENCE = 0
```

---

## 1 · O ESTADO MEDIDO DOS 13 CONTRATOS

```
SOURCE_CONTRACT_COUNT = 13          regras/italy_contracts.mjs
campos declarados                   63 nomes distintos ao todo
contratos com ALLOWED_STRUCTURED_TARGETS   0 de 13
contratos com DOCUMENT_ID_RULE             13 de 13   (e há guarda que o exige)
```

A guarda já existe e corre em CI:

```js
// regras/italy_contract_test.mjs:188
T("todo contrato declara DOCUMENT_ID_RULE (DOCUMENT_ID != BYTE_ID)",
  ct.every(([, c]) => !!c.DOCUMENT_ID_RULE));
```

> **O padrão «campo obrigatório no contrato de fonte, com guarda que reprova» já está em
> produção.** O campo novo entra por esse padrão, não por um mecanismo inventado.

### Onde o segundo grão está declarado hoje — confirmado, sem nova auditoria

| fonte | como escreve o segundo grão |
|---|---|
| `IT-T3-005` | campo próprio: `IDENTITY_KEYS_DO_PONTO = ["point_id","lat","lon","sampling_date"]` |
| `IT-T4-001` | prosa no campo do documento: `"MINSALUTE:FTS6:{AAAAMMDD} · **por linha**: {num_registrazione}"` |
| `IT-T7-002` | prosa no campo do documento: `"MASAF:OP:{DATA_DA_EDICAO} · **por linha**: {CODICE_IT}"` |
| `IT-T2-004` | a chave da **linha** a ocupar o campo do documento: `SIAS:{TABLE_TYPE}:{STATION}:{WINDOW_END}` |
| `IT-T1-001` | idem: `ISTAT:{DATAFLOW}:{REF_AREA}:{TYPE_OF_CROP}:{TIME_PERIOD}` |

```
CONTRACTS_WITH_SECOND_GRAIN_CURRENT = 5
```

---

## 2 · O CAMPO

```
ALLOWED_STRUCTURED_TARGETS_FIELD_NAME = ALLOWED_STRUCTURED_TARGETS
ALLOWED_STRUCTURED_TARGETS_TYPE       = LISTA FECHADA (array) de CONCEPT_ID,
                                        de vocabulário fechado, ordem irrelevante,
                                        sem repetições
ALLOWED_STRUCTURED_TARGETS_OWNER      = o CONTRATO DE FONTE
```

**Array é a forma nativa deste ficheiro**, não uma escolha nova: `IDENTITY_KEYS`,
`EXPECTED_COLUMNS`, `CAMPOS_POR_PONTO` e `CAMPOS_A_EXTRAIR` já são arrays nos mesmos objectos.

**Nunca um valor singular.** A A4 mediu `ONE_TO_MANY` com dado real: `IT-T2-004` produz um
documento **e** 1045 linhas na mesma observação. Um campo singular obrigaria a escolher qual
das duas espécies é «a» espécie — e a resposta é as duas.

### Quem escreve o campo, na prática

Ninguém novo. `regras/italy_contracts.mjs` já tem dono operacional: **gente, por commit**,
com `regras/italy_contract_test.mjs` a reprovar. É a mesma disciplina de
`pedido/receitas.py::EXECUTORES` — *«entra quando prova que percorre a rota; sai quando
deixa de a percorrer»*. **Não se cria autoridade nova para um campo novo num ficheiro que
já tem dono.**

---

## 3 · O VOCABULÁRIO — só conceitos fechados entram

| `CONCEPT_ID` | dono | store | entra na lista? |
|---|---|---|---|
| `SOURCE_DOCUMENT` | a criar (A5.1) | a criar (A5.1) | **SIM** — conceito fechado |
| `SOCIAL_CONTENT` | `social_persistencia.py` | `conteudo` | **SIM** |
| `SOCIAL_COMMENT` | `social_persistencia.py` | `comentario` | **SIM** |
| `SOCIAL_TRANSCRIPT` | alvo fechado; writer por escrever | `transcricao` | **SIM** |
| `REGULATORY_REGISTRATION` | `importar_italia.py` | `registro_regulatorio` | **SIM** |
| `CATALOG_PRODUCT_DOCUMENT` | `catalogo_importar.py` | `catalogo_produto_documento` | **SIM** |
| `AGROCLIMATIC_MEASUREMENT` | ✖ | ✖ | **NÃO** — candidato, `NÃO SEI` |
| `FIELD_MONITORING_POINT` | ✖ | ✖ | **NÃO** — candidato, `NÃO SEI` |

**Candidato não vira conceito por conveniência.** Uma fonte que só produz um candidato fica
com a lista sem ele, e o segundo grão continua declarado onde está — não se apaga nada.

### ⚠️ Achado: há uma família fora do censo da A4

`supabase/migrations/021` criou seis tabelas de «facto publicado por terceiro»
(`estatistica_agricola`, `mercado_observacao`, `clima_observacao`,
`boletim_fitossanitario`, `sinal_regulatorio_futuro`, `evento_setorial`) e elas **têm
writer**: `pacote/lastmile_para_supabase.py`.

O censo da A4 limitou-se aos writers que a rota forward toca, e por isso não as viu. Elas
podem conter conceitos fecháveis — em particular para `IT-T1-001` (ISTAT → estatística
agrícola). **Mas todas escrevem por `fonte_id` e nenhuma carrega `run_id` nem
`raw_asset_id`** — a mesma falta de proveniência de corrida que a A5.1 mediu em
`boletim_fitossanitario`.

**Não as promovo aqui.** Fica registado como o próximo censo a fazer, e **nenhuma delas
entra no vocabulário desta missão.**

---

## 4 · O MAPA DAS 13 FONTES

A regra aplicada: entra na lista o alvo que tem **conceito fechado** *e* **evidência de que
esta fonte realmente produz aquela espécie**.

E a evidência de `SOURCE_DOCUMENT` é dura: o coletor **construiu de facto** um
`DOCUMENT_ID` e um `DOCUMENT_VERSION_ID` a partir de bytes reais.

| `SOURCE_ID` | grão declarado hoje | `ALLOWED NOW` | `UNRESOLVED` |
|---|---|---|---|
| `IT-T2-002` | documento | `SOURCE_DOCUMENT` | — |
| `IT-T3-002` | documento | `SOURCE_DOCUMENT` | — |
| `IT-T3-008` | documento | `SOURCE_DOCUMENT` | — |
| `IT-T3-010` | documento | `SOURCE_DOCUMENT` | — |
| `IT-T3-005` | documento **+ ponto** | `SOURCE_DOCUMENT` | ponto de monitorização |
| `IT-T2-004` | documento **+ linha** | `SOURCE_DOCUMENT` | medição estação·data·variável |
| `IT-T4-001` | documento **+ linha** | `SOURCE_DOCUMENT` · `REGULATORY_REGISTRATION` | — |
| `IT-T1-001` | linha (série ISTAT) | — | documento **e** linha |
| `IT-T2-001` | documento | — | documento |
| `IT-T3-011` | documento | — | documento |
| `IT-T5-002` | documento | — | documento |
| `IT-T7-002` | documento **+ linha** | — | documento **e** registo de organização |
| `IT-T9-008` | documento | — | documento |

```
SOURCE_DOCUMENT_ALLOWED_SOURCE_COUNT = 7
SOURCE_DOCUMENT_ALLOWED_SOURCE_IDS   = IT-T2-002 · IT-T2-004 · IT-T3-002 · IT-T3-005
                                       IT-T3-008 · IT-T3-010 · IT-T4-001
```

### Por que 7 e não 13 — a fronteira é onde o código pára, e isso foi medido

```
fontes com DOCUMENT_ID_RULE declarada          13 / 13
fontes com documento REALMENTE construído       7 / 13
fontes com `documentIdDe()` no coletor          7 / 13   ← exactamente as mesmas
   (coleta/italy_pilot_collect.mjs:185-227: TERRETRURIA · ARPAV · SIAS
    CAMPANIA · APOL · ARIF · MINSALUTE)
```

**A fronteira não é arbitrária: é exactamente onde o coletor pára.** As outras 6 declaram a
regra e ninguém a correu.

E não é por falta de bytes — medi: as 6 têm amostra preservada em
`data/samples/IT-SOURCE-SAMPLES/<SOURCE_ID>/MANIFEST.json`, com `SHA256`, `BYTES`, `MIME`,
`SOURCE_URL` e, em 5 de 6, `SOURCE_DATE` e `ORIGINAL_TITLE`. O que **não** têm é
`DOCUMENT_ID` nem `DOCUMENT_VERSION_ID`.

> **Bytes guardados provam que a fonte entrega. Não provam que a fonte entrega um DOCUMENTO
> IDENTIFICADO** — para isso alguém tem de correr a regra. É a mesma distinção que esta
> casa faz há missões: `MODULE EXISTS != EDGE EXISTS != FLOW EXISTS`.

**Remédio nomeado, e é pequeno:** implementar `documentIdDe()` para as 6, correr, e elas
passam a poder declarar. Não é decisão — é trabalho, e **não é desta missão**.

Detalhe medido que vale a pena: `IT-T2-004` e `IT-T4-001` têm `IDENTITY_KEYS` de **linha**, e
mesmo assim o coletor produziu documento — `SIAS:PRECIPITAZIONE_GIORNALIERA:WINDOW_END_2026-09-05`
e `MINSALUTE:FTS6:20260907`, ambos **sem** a parte da linha. O código já separava os dois
grãos na prática; o contrato é que não tinha onde o escrever.

---

## 5 · O SEGUNDO GRÃO, UM A UM

| fonte | segundo grão | tem conceito canónico? | pode mover para a lista? |
|---|---|---|---|
| `IT-T4-001` | `num_registrazione` — autorização do Ministero | **SIM** · `REGULATORY_REGISTRATION` | **SIM** |
| `IT-T3-005` | `point_id · lat · lon · sampling_date` | **NÃO** · candidato `FIELD_MONITORING_POINT` | `KEEP_AS_UNRESOLVED` |
| `IT-T2-004` | `table_type · station · window_end` | **NÃO** · candidato `AGROCLIMATIC_MEASUREMENT` | `KEEP_AS_UNRESOLVED` |
| `IT-T7-002` | `CODICE_IT` — organização de produtores | **NÃO** · sem conceito | `KEEP_AS_UNRESOLVED` |
| `IT-T1-001` | `DATAFLOW · REF_AREA · TYPE_OF_CROP · TIME_PERIOD` | **NÃO** nesta missão · ver §3 | `KEEP_AS_UNRESOLVED` |

```
CONTRACTS_WITH_CANONICAL_SECOND_TARGET  = 1   (IT-T4-001)
CONTRACTS_WITH_UNRESOLVED_SECOND_TARGET = 4
```

---

## 6 · O QUE A LISTA SUBSTITUI — e o que não pode apagar

> ## A LISTA DECLARA O **TIPO**. AS CHAVES DECLARAM A **IDENTIDADE**.
> São duas perguntas, e a lista não responde à segunda.

```
ALLOWED_STRUCTURED_TARGETS   que ESPÉCIES esta fonte pode produzir      TIPO
DOCUMENT_ID_RULE             como se nomeia o documento                 IDENTIDADE
IDENTITY_KEYS                que campos formam essa identidade          IDENTIDADE
IDENTITY_KEYS_DO_PONTO       a identidade do SEGUNDO grão               IDENTIDADE
```

**Nada da notação de identidade se apaga.** O que a lista corrige é a **contrabandagem**: as
duas prosas `«· por linha: …»` e as duas `IDENTITY_KEYS` de linha metidas no campo do
documento existem porque o tipo não tinha campo — e não porque a identidade estivesse a
mais.

Regra futura, e é uma trava contra perda silenciosa:

```
Nenhuma linha de prosa de segundo grão se apaga
ANTES de a identidade daquele segundo alvo ter onde morar.
```

E `IDENTITY_KEYS_DO_PONTO` do `IT-T3-005` é a prova de que a casa já queria uma identidade
**por alvo** — foi o único contrato que a inventou sozinho. O desenho desse par
(alvo ↔ identidade) **não é desta missão**.

---

## 7 · A TRAVA E OS SEUS ESTADOS

```
RESOLVED_STRUCTURED_TARGET  ∈  ALLOWED_STRUCTURED_TARGETS      ← invariante
```

| situação | código | estado | fallback |
|---|---|---|---|
| alvo resolvido fora da lista | `STRUCTURED_TARGET_NOT_ALLOWED` | `FAIL` | **nenhum** |
| contrato sem o campo | `STRUCTURED_TARGET_NOT_DECLARED` | `FAIL` | **nenhum** |
| alvo permitido, dono não ligado | `OWNER_NOT_CONNECTED` — **já existe** | `FAIL` | **nenhum** |

O terceiro já está no registo (`leis/diagnostico.py`) e diz exactamente isto:
*«há dono declarado para a etapa e ele não toca o artefato. OWNER EXISTS != EDGE EXISTS.»*

**Dois códigos novos, um reaproveitado, e nenhum quarto** — não há caso medido que os três
não cubram.

---

## 8 · A LISTA VAZIA

```
EMPTY_ALLOWED_LIST_VALID   = YES
EMPTY_ALLOWED_LIST_MEANING = «esta fonte NÃO está autorizada a produzir STRUCTURED nenhum»
                             A travessia termina legitimamente em DERIVED.
```

E o que ela **não** significa, dito para não virar esconderijo:

```
[]        decisão tomada: nada a estruturar        VÁLIDO
ausente   decisão NÃO tomada                        FAIL · STRUCTURED_TARGET_NOT_DECLARED
```

**Duas coisas diferentes, dois sinais diferentes.** Uma lista vazia nunca pode ser usada
para dizer «ainda não decidi» — a ausência do campo é que diz isso, e ela reprova.

⚠️ **Medido: zero casos hoje.** Nenhuma das 13 fontes é conhecidamente uma fonte
só-RAW/DERIVED. `[]` é válido por contrato e **não tem utilizador**; se aparecer um, aparece
com razão escrita.

---

## 9 · VERSIONAMENTO

```
CHANGE_REQUIRES_CONTRACT_VERSION_BUMP = YES
```

E a razão é medida, não estilística: **cada corrida já grava a versão do conjunto de
contratos** no seu recibo —

```
data/collection-ledger/italy/runs.ndjson
  "SOURCE_CONTRACT_VERSION": "italy-contracts-v1"    (6 de 6 corridas)
```

Mudar `ALLOWED_STRUCTURED_TARGETS` muda **o que uma corrida está autorizada a produzir**.
Sem subir a versão, duas corridas com o mesmo carimbo `italy-contracts-v1` teriam
autorizações diferentes — e a comparação entre elas passaria a mentir sem ninguém reparar.

É a mesma lei que `CORPO_VERSAO` já aplica em `social_persistencia.py`: *«a versão é o que
torna uma mudança futura visível; mudar os campos sem mexer nela faria todo o acervo parecer
ter sofrido drift de uma vez.»*

---

## 10 · O PRIMEIRO SLICE

Para `RAW → DERIVED → SOURCE_DOCUMENT → ADMISSION`, precisam declarar
`ALLOWED_STRUCTURED_TARGETS = [SOURCE_DOCUMENT]`:

```
IT-T2-002   IT-T3-002   IT-T3-008   IT-T3-010   IT-T3-005
IT-T2-004   IT-T4-001  ← este declara [SOURCE_DOCUMENT, REGULATORY_REGISTRATION]
```

**7 contratos.** As outras 6 ficam sem o campo até alguém correr a regra de identidade
delas — e sem o campo elas **reprovam** em vez de passarem caladas.

O slice mais estreito possível usa uma só: `IT-T2-002` (ARPAV) tem 29 versões documentais
medidas, 124 observações e derivados reais. Não é obrigatório declarar as 7 para começar.

---

## 11 · ENTREGA

| | |
|---|---|
| **A** `BRANCH` | `claude/raw-observation-identity-3jbwco` |
| **B** `INITIAL_HEAD` | `2e1c80ced485c13a2ecc9dd124cc629692a24109` |
| **D** `WORKTREE` | limpa |
| **E** `SOURCE_CONTRACT_COUNT` | **13** |
| **F** `ALLOWED_STRUCTURED_TARGETS_FIELD_NAME` | `ALLOWED_STRUCTURED_TARGETS` |
| **G** `ALLOWED_STRUCTURED_TARGETS_TYPE` | lista fechada (array) de `CONCEPT_ID`, vocabulário fechado |
| **H** `ALLOWED_STRUCTURED_TARGETS_OWNER` | contrato de fonte · mantido por gente, por commit, com guarda |
| **I** `SOURCE_DOCUMENT_ALLOWED_SOURCE_COUNT` | **7** |
| **J** `SOURCE_DOCUMENT_ALLOWED_SOURCE_IDS` | `IT-T2-002 · IT-T2-004 · IT-T3-002 · IT-T3-005 · IT-T3-008 · IT-T3-010 · IT-T4-001` |
| **K** `CONTRACTS_WITH_SECOND_GRAIN_CURRENT` | **5** |
| **L** `CONTRACTS_WITH_CANONICAL_SECOND_TARGET` | **1** — `IT-T4-001` |
| **M** `CONTRACTS_WITH_UNRESOLVED_SECOND_TARGET` | **4** |
| **N** `EMPTY_ALLOWED_LIST_VALID` | **YES** |
| **O** `EMPTY_ALLOWED_LIST_MEANING` | não autorizada a produzir STRUCTURED; termina em DERIVED. **Nunca** «ainda não decidi» |
| **P** `TARGET_NOT_ALLOWED_BEHAVIOR` | `STRUCTURED_TARGET_NOT_ALLOWED` · `FAIL` · sem fallback |
| **Q** `TARGET_NOT_DECLARED_BEHAVIOR` | `STRUCTURED_TARGET_NOT_DECLARED` · `FAIL` · sem fallback |
| **R** `CHANGE_REQUIRES_CONTRACT_VERSION_BUMP` | **YES** — a corrida já carimba `SOURCE_CONTRACT_VERSION` |
| **S** `CURRENT_CONTRACTS_CHANGED` | **0** |
| **T** `RUNTIME_FILES_CHANGED` | **0** |
| **U** `DATABASE_MUTATIONS` | **0** |
| **V** `SYSTEM_MAP_CHANGED` | **0** |
| **W** `BIBLE_CHANGED` | **0** |
| **X** `UNRESOLVED_CRITICAL_A5_2_QUESTIONS` | **0** |

### O que continua `NÃO SEI` — e nenhum bloqueia o slice

1. Espécie canónica de `FIELD_MONITORING_POINT` e `AGROCLIMATIC_MEASUREMENT`.
2. Conceito para o registo de organizações do MASAF (`IT-T7-002`).
3. Se a família da migration 021 contém conceitos fecháveis — censo por fazer (§3).
4. Onde mora a identidade do **segundo** alvo, quando ele existir (§6).

---

## 12 · VEREDITO

```
ALLOWED_STRUCTURED_TARGETS_FIELD  = CLOSED
SOURCE_CONTRACT_MAPPING           = CLOSED   13 fontes mapeadas
SOURCE_DOCUMENT_ALLOWED_SOURCES   = CLOSED   7 de 13, com evidência dura
SECOND_GRAIN_MIGRATION_SEMANTICS  = CLOSED   nada se apaga antes de haver casa
FAILURE_SEMANTICS                 = CLOSED   2 códigos novos + 1 existente
VERSIONING_RULE                   = CLOSED   bump obrigatório

C-PLAN-A5.2 = PASS
```

O próximo programador altera os contratos sem decidir de novo: **qual campo criar**, **qual
tipo usar**, **quais fontes recebem `SOURCE_DOCUMENT`**, **que outros alvos já estão
provados**, **como tratar alvo proibido**, **como tratar contrato sem declaração** e **se
precisa subir versão**.

---

## 13 · EM PALAVRAS FÁCEIS

1. **O que é `ALLOWED_STRUCTURED_TARGETS`?** A lista do que cada fonte tem autorização para
   virar. Não o que ela traz — o que ela pode virar depois de estruturada.

2. **Por que cada fonte precisa dela?** Para que ninguém a jusante tenha de adivinhar. Sem a
   lista, alguém olharia para o ficheiro e decidiria por conta própria — e adivinhar é o que
   esta casa recusa.

3. **Uma fonte pode produzir mais de uma coisa?** Pode, e produz. O SIAS traz um documento e
   mil linhas na mesma ida. Por isso é lista, e não um valor só.

4. **Quem decide quais tipos ela pode produzir?** O contrato da fonte, escrito por gente,
   com a guarda a reprovar quem esquecer.

5. **O T-32 pode escolher um tipo fora da lista?** Não. Fora da lista é falha, com nome, e
   sem plano B.

6. **Quantas fontes podem produzir `SOURCE_DOCUMENT`?** Sete das treze. As outras seis
   declaram a regra de identidade e ninguém a correu — a fronteira é exactamente onde o
   código do coletor pára.

7. **E os tipos que ainda não sabemos nomear?** Ficam de fora da lista e continuam
   declarados onde estão. Nada se apaga por não ter nome ainda.

8. **Algum contrato foi alterado?** Nenhum. Esta missão decide; não escreve.

9. **Qual é o próximo passo?** O **D2**: pôr o alvo já resolvido dentro da unidade que o
   executor entrega.

> **HARD STOP.** O campo, o mapa das 13 fontes, a trava e o versionamento estão fechados.
> Não se alteram contratos. Não se inicia a A5.3.
