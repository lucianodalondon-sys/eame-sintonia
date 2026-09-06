# IDENTIDADE DAS AFIRMAÇÕES — correção do `CLAIM_ID` e os três portões

**Data:** 2026-09-06 · **Branch:** `claude/passport-tags-italy-v1` · **Somente leitura**
**Regra:** `CLAIM-ID-2026-09-06` · **Portões:** `ETIQUETAS-PORTAO-2026-09-06`

> Nada foi aplicado ao log. `data/passaporte/EVENTOS.jsonl` é append-only e **não foi
> tocado**. Esta missão entrega a medição, o esquema escolhido, a proposta de reemissão,
> os portões e as regressões. Aplicar a reemissão é outro ato, com outro comando.

---

## 1 · A COLISÃO COMPLETA

```
CLAIMS_TOTAL                          =  55
CLAIM_IDS_TOTAL                       =  22
COLLIDING_IDS                         =  12       (54% dos ids)
CLAIMS_ON_AMBIGUOUS_ID                =  45       (82% das afirmações)
ROUTES_TOTAL                          = 132
ROUTES_ON_AMBIGUOUS_ID                = 120       (91%)
ROTAS_ORFAS_EM_ID_AMBIGUO             =  32

COLISAO_MESMO_TEXTO                   =   0
COLISAO_TEXTO_DIFERENTE               =  12
COLISAO_COM_DIVERGENCIA_DE_CONTEXTO   =  12       (12 de 12)
```

> **Correção de um número que publiquei antes.** Eu havia dito *"72 rotas, 60 ambíguas
> (83%)"*. Aquilo contava tuplas deduplicadas. A contagem honesta de **eventos** é
> **132 rotas, 120 ambíguas — 91%.** Pior do que eu tinha dito.

### `COLISAO_CONTRADITORIA` — a resposta honesta é NÃO SEI

A missão pediu três baldes, e o terceiro é **contraditória**. Medi e **não posso
preencher**: nenhum documento do repositório declara que dois casos se contradizem, e
julgar contradição por conta própria seria inventar.

> **Corrijo aqui uma afirmação minha da entrega anterior.** Eu disse que `CASE-005` e
> `CASE-006` foram *"escritos de propósito para se contradizerem"*. **Está errado.** Li o
> título `"A mesma pergunta, a janela errada, a resposta invertida"` como se falasse dos
> dois casos entre si; ele fala de **dentro** do CASE-006 — usar a janela errada inverte
> a resposta *daquele* caso. Os dois casos são sobre países, anos e problemas diferentes.

No lugar do balde que não posso provar, medi um que **é provável e é o que quebra os
cruzamentos**: `COLISAO_COM_DIVERGENCIA_DE_CONTEXTO` — o contexto **declarado** dos casos
que dividem um id diverge em `COUNTRY`, `CROP`, `REGION`, `TIME` ou `PROBLEM`.
**Doze de doze divergem.**

```
COLISAO_CONTRADITORIA          = NÃO SEI  (contradição não é declarada em fonte nenhuma)
COLISAO_COM_DIVERGENCIA_DE_CONTEXTO = 12  (medido contra CASOS-PARA-APRESENTACAO.md)
```

### Tabela — as doze, com o contexto que diverge

| `CLAIM_ID` | claims | casos | capacidades | rotas (órfãs) | o que diverge |
|---|---:|---|---|---:|---|
| `…3CA2E441A6D5FD7A-01` | 2 | CASE-005, 006 | COUNTRY_CROP_PULSE, OPPORTUNITY | 6 (2) | **COUNTRY: FRANCE ≠ SPAIN** · REGION · TIME · PROBLEM |
| `…578D988FA7D06864-01` | 4 | CASE-001, 002, 011, 014 | COMPETITOR, PORTFOLIO, REGULATORY, OPPORTUNITY | 13 (3) | COUNTRY · **CROP: cereal ≠ videira** · TIME · PROBLEM |
| `…6361C0445977B78B-01` | 5 | CASE-007, 008, 012, 013, 016 | PHYTOSANITARY, OPPORTUNITY | 9 (3) | **CROP: Olivar ≠ Vid** · REGION · TIME · PROBLEM |
| `…6C27C1AB6CAEF95B-01` | 5 | CASE-007, 008, 012, 013, 016 | PHYTOSANITARY, OPPORTUNITY | 9 (3) | idem |
| `…E163C1F6855DE7CD-01` | 5 | CASE-007, 008, 012, 013, 016 | PHYTOSANITARY, OPPORTUNITY | 9 (3) | idem |
| `…87691938C0652597-01` | 4 | CASE-001, 002, 011, 014 | COMPETITOR, PORTFOLIO, REGULATORY, OPPORTUNITY | 13 (3) | COUNTRY · CROP · TIME · PROBLEM |
| `…95FA2AFC5C6B8670-01` | 4 | idem | idem | 13 (3) | idem |
| `…A5898A371B7C03E0-01` | 4 | idem | idem | 13 (3) | idem |
| `…BCFC03E10FACB8BD-01` | 4 | idem | idem | 13 (3) | idem |
| `…F4D84D66770EEA32-01` | 4 | idem | idem | 13 (3) | idem |
| `…63BB2D08C441ABC3-01` | 2 | CASE-003, 014 | REGULATORY, OPPORTUNITY | 3 (1) | **COUNTRY: ITALY ≠ EU→FR·IT·(ES)** · CROP · PROBLEM |
| `…AAB6AFD1D7513063-01` | 2 | CASE-009, 010 | SCIENCE, OPPORTUNITY | 6 (2) | **COUNTRY: ITALY ≠ SPAIN** · **CROP: Trigo ≠ Vid** · PROBLEM |

Tabela completa com textos: `python3 scripts/passaporte_claim_id.py medir --passaporte <ref>`

### O dano é menor do que parece — e a razão importa

```
ROUTED_TO_CAPABILITY · DIRECT   · REASON contém o CASE   →  48 de 48   RECUPERÁVEL
ROUTED_TO_CAPABILITY · BLOCKED  · REASON genérico        →  36 de 36   NÃO recuperável
CONSUMED_BY_CAPABILITY          · EVIDENCE tem o CASE    →  48 de 48   RECUPERÁVEL
```

**Toda rota que afirma relevância (`DIRECT`) carrega o caso no próprio motivo** —
*"a área que sustenta REGULATORY lista CASE-001 em REAL_EXAMPLES"*. Ela é reatribuível.

As 32 não-reatribuíveis são **todas** `OPPORTUNITY` + `BLOCKED`, com o mesmo motivo
genérico para todas. Perder a qual afirmação cada uma pertencia custa pouco: o bloqueio é
universal por contrato. **Mas há um resto que não fecha:** 13 claims sob ids ambíguos não
têm rota `OPPORTUNITY` correspondente, e **não dá para saber quais**.

---

## 2 · O ESQUEMA ESCOLHIDO — e o custo dele, declarado

Três esquemas, medidos sobre os 55 claims reais e quatro contraexemplos:

| esquema | ids | colisões | estável | separa textos sob a mesma chave | separa itens | sobrevive a correção de digitação |
|---|---:|---:|---|---|---|---|
| **A** estrutural `ITEM+CASE` | 55 | 0 | sim | **não** | sim | **sim** |
| **B** content-addressed | 55 | 0 | sim | sim | sim | **não** |
| **C** híbrido `ITEM+CASE+hash` | 55 | 0 | sim | **sim** | sim | **não** |

**Escolhido: C.** Ele dá tudo o que B dá e ainda deixa o caso legível no identificador:

```
A   CLAIM-3CA2E441A6D5FD7A-CASE-005            ← colide se o mesmo caso render dois textos
B   CLAIM-99FED4B0A1DC2882                     ← opaco; não dá para auditar a olho
C   CLAIM-3CA2E441A6D5FD7A-CASE-005-6F47AD64   ← escolhido
```

**O custo, dito antes de alguém descobrir em produção:** corrigir uma vírgula no texto de
uma afirmação **muda o id**. Isso não é defeito, é a definição de content-addressing — e é
o que a missão pediu (*"diferente quando o conteúdo factual é diferente"*). A mitigação é
que o prefixo `ITEM+CASE` **não muda**: uma revisão de texto aparece como o mesmo item e o
mesmo caso com hash novo, e continua rastreável.

**Ressalva de contrato:** o `PASSPORT-1.0` argumenta que id legível *"vira caminho na
cabeça de quem lê"*. O argumento vale contra colocar **caminho de arquivo** no id. `CASE-005`
não é local — é a chave de afirmação que a própria fonte declara. E o hash mantém o id
preso ao conteúdo. Mesmo assim: **é um desvio do princípio de opacidade, e está declarado.**

---

## 3 · O CASO-TESTEMUNHA — obrigatório, e passa

```
ANTES   CLAIM-3CA2E441A6D5FD7A-01
          ├── CASE-005 · FRANCE · trigo · colapso de rendimento 2024
          ├── CASE-006 · SPAIN  · trigo · seca de 2023
          ├── ROUTED   → COUNTRY_CROP_PULSE · DIRECT      ← de qual dos dois?
          ├── CONSUMED → COUNTRY_CROP_PULSE (CASE-005)
          ├── ROUTED   → COUNTRY_CROP_PULSE · DIRECT
          └── CONSUMED → COUNTRY_CROP_PULSE (CASE-006)

DEPOIS  CLAIM-3CA2E441A6D5FD7A-CASE-005-6F47AD64   ← França, identidade própria
        CLAIM-3CA2E441A6D5FD7A-CASE-006-BC890C64   ← Espanha, identidade própria
```

As quatro condições exigidas: França tem identidade própria ✓ · Espanha tem identidade
própria ✓ · nenhuma rota `DIRECT`/`CONSUMED` consome a outra por engano ✓ · e os dois casos
continuam distintos, com o contexto declarado divergindo em cinco eixos ✓.
Exercido em `tests/test_claim_id_e_portoes.py::test_caso_testemunha_case_005_e_case_006_ganham_identidade_propria`.

---

## 4 · OS TRÊS PORTÕES

`python3 scripts/passaporte_portao_etiquetas.py --acervo . --passaporte <ref>`

| portão | resultado | por quê |
|---|---|---|
| `CLAIM_ID_GATE` | **FAIL** | 12 ids colididos, 120 rotas dependentes — **no log histórico, que não foi reescrito** |
| `EVIDENCE_STATE_GATE` | **PASS** | 346 → **0** contradições sob a regra nova |
| `UNIVERSE_COMPLETENESS` | **FAIL** | nenhum universo declarado foi apresentado — e ausência de declaração **não é PASS** |

```
ROUTING_PUBLISHABLE = NO
```

O `CLAIM_ID_GATE` **tem de continuar vermelho** enquanto o log não for reemitido. Um portão
que ficasse verde por causa da existência de uma proposta seria pior do que não ter portão.

---

## 5 · ESTADO DA EVIDÊNCIA — o campo decide, a prosa explica

O acervo funde as duas coisas num valor só. A correção separa:

```
EVIDENCE_STATE   ∈ PROVED · UNKNOWN · CONTRADICTED · NOT_AVAILABLE · NOT_APPLICABLE · ERROR
EVIDENCE_REASON  texto livre — explica, e NUNCA decide
```

A migração é **declarada e fechada**, e olha **só o prefixo** delimitado por separador —
não busca substring no corpo:

```
1. o valor canônico É uma sentinela              → (UNKNOWN, sem razão)
2. o valor tem <sentinela><separador><razão>     → (UNKNOWN, razão extraída)
3. qualquer outro valor                          → (PROVED, sem razão)
```

Contraprova exercida — o que **não pode** virar ausência:

```
'FRANCE — Centre-Val de Loire'                        → PROVED   (FRANCE não é sentinela)
'REPILO - Venturia oleaginea'                         → PROVED
'o autor diz que não sabe a região do estudo'         → PROVED   (fala sobre não saber ≠ não saber)
'NAO SEI se isso importa — frase de uma afirmação'    → PROVED   (o prefixo não é sentinela)
```

Remedição:

```
VALORES_FUNDIDOS_NO_ACERVO           = 1.398   em 54 campos
TRATADOS_COMO_CONHECIDOS_ANTES       = 1.398
TRATADOS_COMO_CONHECIDOS_DEPOIS      =     0

PROVED_WITH_UNKNOWN_REASON_BEFORE    =   346   (todos em TIME_RESOLVED)
PROVED_WITH_UNKNOWN_REASON_AFTER     =     0
```

> **1.398 e não 1.312.** O censo anterior contava com uma regra mais frouxa e excluía
> menos campos. Este portão exclui `*_EVIDENCE`, `*_REASON`, `*_WHY` — campos cuja função
> **é** explicar — e exige espaço depois do separador. É o número que o portão usa.

---

## 6 · UNIVERSO — impressão digital, e a recusa de PASS sobre subconjunto

```
UNIVERSE_FILE_COUNT    = 421
UNIVERSE_RECORD_COUNT  = 26.061
UNIVERSE_FINGERPRINT   = 0813535703856bddeaf446ea17b13a8f87ce7abe
```

Provado nos dois sentidos, com canário:

```
universo declarado == universo real            → PASS
+1 arquivo que ninguém declarou                → FAIL
   "universo lido ≠ universo declarado — PASS sobre subconjunto recusado"
nenhum universo declarado                      → FAIL
   "NAO_MEDIDO — ausência de declaração NÃO é PASS"
```

É isso que impede o que aconteceu com `TRANSCRICOES-C/D/E`: um portão verde sobre um
universo menor tinha exatamente a mesma cara de um portão verde sobre o universo inteiro.

---

## 7 · TRANSPORTE, NÃO RECRIAÇÃO

Nenhuma lógica de dono existente foi reescrita. `tests/test_claim_id_e_portoes.py` trava
isso: todo conceito `HERDADO`/`TRANSPORTE_AUSENTE` tem de nomear o dono, e o vocabulário
de `INDEPENDENCE_STATE` é conferido **contra `scripts/voz.py`** — se alguém o reinventar
aqui, o teste cai.

```
EXISTING_CONCEPT_OWNERS = 19/31
TRULY_MISSING_CONCEPTS  =  4/31   OBSERVATION_STATE · PROOF_STATE · RELATIONSHIP_ID · UNKNOWN_FIELDS
```

---

## 8 · COBERTURA — não subiu, e não devia subir

`13,7%` continua `13,7%`. Nenhuma regra foi relaxada. Os estados de ausência ficam
separados, como pedido: `PROVED` · `UNKNOWN` · `NOT_AVAILABLE` · `NOT_NORMALIZED` ·
`NOT_APPLICABLE`.

`FULL_BACKFILL` continua **NO** — e agora com teste: `test_sem_normalizacao_eles_sao_diferentes_e_o_backfill_fica_proibido`
falha se alguém liberar o backfill enquanto `VINE` e `["VINE"]` forem tratados como
culturas diferentes.

---

## 9 · AS TRÊS DECISÕES DE PRODUTO — instrumentadas, não decididas

### 9.1 · `FAMILY_ID` — três conceitos lado a lado

| | **A · família SEMÂNTICA** | **B · família por CAMINHO** | **C · família de ROTA** |
|---|---|---|---|
| **dono** | `scripts/v2_dedup_e_familias.py:47` | `scripts/it_acervo_inventario_v2.py:53` | `CONTRATO-DO-PASSAPORTE §1.2` |
| **pergunta** | o que este dado **significa**? | onde este arquivo **mora**? | **como** isto foi coletado? |
| **chave** | nome do bloco de dados | regex sobre o caminho | rota de coleta |
| **tamanho** | 12 famílias, 14 blocos | 13 famílias | 8 famílias |
| **cardinalidade** | N blocos → 1 família | 1 caminho → 1 família (primeira que casar) | 1 item → 1 família |
| **exemplo real** | `fenologia` e `boletins-regioes-fechadas` → **`CURRENT_FIELD_SIGNALS`** | `IT-ROTULOS│IT-VOCAB│productRelationships` → **`ROTULOS_PORTFOLIO`** | `PLATFORM_PUBLIC_PAID_ROUTE` |
| **onde é usado** | dedupe e agrupamento de fatos | inventário do acervo | passaporte, contabilidade |
| **defeito conhecido** | `OUTRA` como balde de sobra | mistura caminho e conteúdo (`productRelationships` não é caminho) | não cobre acervo fora do passaporte |

**O que quebra se receberem o mesmo nome:** um item de `SENSOR-PILOT` é
`SENSORES_HUMANOS` em B e `PLATFORM_PUBLIC_PAID_ROUTE` em C **ao mesmo tempo, sem
contradição** — são respostas a perguntas diferentes. Chamar as três de `FAMILY_ID`
faria um `GROUP BY FAMILY_ID` misturar três recortes e produzir um número que parece
total e não é de nada.

```
FAMILY_ID_DECISION_INPUT_READY = SIM
DECISAO                        = NÃO TOMADA — precisa de dono humano
RECOMENDAÇÃO PARA DISCUSSÃO    = nenhuma das três fica com FAMILY_ID puro:
                                 SEMANTIC_FAMILY · STORAGE_FAMILY · SOURCE_FAMILY
```

### 9.2 · `EVIDENCE_CLASS` — códigos internos, tradução só na tela

O conflito medido: `OFFICIAL_DOCUMENT` (2.030) e `DOCUMENTO_OFICIAL` (2.030) são o mesmo
valor em duas línguas. A correção **não** é escolher inglês ou português — é o
identificador não ser palavra de língua nenhuma.

| código interno | o que é | valores de hoje que entram |
|---|---|---|
| `EVC-P01` | fonte primária, bruto preservado | `PRIMARY_SOURCE_RAW` |
| `EVC-P02` | fonte primária, sonda/consulta | `PRIMARY_SOURCE_PROBE` |
| `EVC-O01` | documento oficial | `OFFICIAL_DOCUMENT` · `DOCUMENTO_OFICIAL` |
| `EVC-O02` | estatística oficial | `OFFICIAL_STATISTIC` |
| `EVC-O03` | observação oficial de mercado | `OFFICIAL_MARKET_OBSERVATION` |
| `EVC-O04` | fato regulatório | `REGULATORY_FACT` |
| `EVC-O05` | declaração de autoridade técnica | `TECHNICAL_AUTHORITY_DECLARATION` |
| `EVC-S01` | literatura científica | `SCIENTIFIC_LITERATURE` |
| `EVC-D01` | interpretação derivada | `DERIVED_INTERPRETATION` |
| `EVC-D02` | escopo derivado | `DERIVED_SCOPE` |
| `EVC-D03` | medição derivada | `DERIVED_MEASUREMENT` |
| `EVC-D04` | identidade derivada | `DERIVED_IDENTITY` |
| `EVC-T01` | cultura em tabela de uso autorizado | `CROP_IN_AUTHORIZED_USE_TABLE` |

A letra é o eixo (**P**rimária · **O**ficial · **S**ciência · **D**erivada · **T**abela) e
carrega a força da prova. `EVC-D*` **nunca** pode ser lido como observação — é a semente de
`PROOF_STATE` e de `OBSERVATION_STATE`, que hoje não existem.

```
EVIDENCE_CLASS_INTERNAL_CODES = SIM (proposta; nenhum dado foi convertido)
```

### 9.3 · `CAPABILITY_MAP` — o dono, medido

| candidato | evidência | veredito |
|---|---|---|
| `docs/capacidades/ATLAS-DE-CAPACIDADES-EAME.md` | define `CAP-001…CAP-022`; 26 referências | **dono do VOCABULÁRIO** |
| `docs/apresentacao/CONTRATO-DE-PROVA-DA-APRESENTACAO.md` | 14 blocos `DECK-xxx` com `CURRENT_EVIDENCE: CAP-012, CAP-013, CASE-005, CASE-006` | **dono da RELAÇÃO capacidade ↔ evidência** |
| `docs/ferramentas/ARQUITETURA-DE-INFORMACAO-EAME.md` | 10 áreas com `REAL_EXAMPLES: CASE-xxx` | dono da relação **área ↔ caso** |
| `scripts/passaporte_backfill.py:858` | `AREA_PARA_CAPACIDADE`, só em código | **terceiro mapa, não declarado — competidor** |
| `italia-portale/` | `grep CAPABILITY_ID│CAP-0` nos `client/*.js` = **zero** | **apenas renderiza** |

```
CAPABILITY_MAP_OWNER = docs/apresentacao/CONTRATO-DE-PROVA-DA-APRESENTACAO.md
                       (relação CAPABILITY ↔ EVIDENCE/CASE, campo CURRENT_EVIDENCE)
                       vocabulário: docs/capacidades/ATLAS-DE-CAPACIDADES-EAME.md
```

A regra preferencial da missão — *o motor/contrato de inteligência é dono, o portal apenas
renderiza* — **é confirmada pelo repositório**, não contrariada. O que precisa sair de cena
é o `AREA_PARA_CAPACIDADE` escondido no código do backfill.

---

## ENTREGA

```
CLAIMS_TOTAL                          =  55
CLAIM_IDS_BEFORE                      =  22
CLAIM_IDS_AFTER                       =  55        (proposta; nada aplicado)
COLLIDING_IDS_BEFORE                  =  12
COLLIDING_IDS_AFTER                   =   0

ROUTES_TOTAL                          = 132
ROUTES_AMBIGUOUS_BEFORE               = 120
ROUTES_AMBIGUOUS_AFTER                =   0
ROUTES_NAO_REATRIBUIVEIS              =  32        ← trocamos certeza falsa por lacuna declarada
CLAIMS_SEM_ROTA_OPPORTUNITY_IDENTIFICAVEL = 13

CLAIM_ID_GATE                         = FAIL       (no log histórico, que não foi reescrito)

PROVED_UNKNOWN_CONTRADICTIONS_BEFORE  = 346
PROVED_UNKNOWN_CONTRADICTIONS_AFTER   =   0

UNIVERSE_COMPLETENESS                 = FAIL       (nenhum universo declarado apresentado)
UNIVERSE_FINGERPRINT                  = 0813535703856bddeaf446ea17b13a8f87ce7abe

EXISTING_CONCEPT_OWNERS               = 19/31
TRULY_MISSING_CONCEPTS                =  4/31

PASSPORT_REQUIRED                     = NO
FULL_BACKFILL                         = NO

FAMILY_ID_DECISION_INPUT_READY        = SIM
EVIDENCE_CLASS_INTERNAL_CODES         = SIM
CAPABILITY_MAP_OWNER                  = docs/apresentacao/CONTRATO-DE-PROVA-DA-APRESENTACAO.md

TESTS                                 = 53 (28 leis + 25 regressões) · 53 passando
```

### BLOCKERS

1. **A reemissão não foi aplicada** — e não deve ser por mim sozinho. O log é append-only:
   reemitir significa **acrescentar** 155 eventos com `RULE_VERSION = CLAIM-ID-2026-09-06`,
   não editar os antigos. É um ato que muda o artefato canônico e precisa de decisão.
2. **32 rotas perdem o vínculo com a afirmação** e 13 claims ficam sem saber se tiveram
   bloqueio de `OPPORTUNITY`. É perda real, e é preferível à ambiguidade — mas é perda.
3. **`FAMILY_ID` sem dono.** Três conceitos prontos para decisão humana.
4. **`AREA_PARA_CAPACIDADE` continua no código**, competindo com o contrato de prova.
5. Sem `pytest` nem `pip` neste ambiente: a suíte antiga do repositório **não pôde ser
   rodada** — `NAO_MEDIDO`, não "passou".
6. **O passaporte não está pronto.** Os testes locais passam; isso prova as leis, não o
   acervo.
