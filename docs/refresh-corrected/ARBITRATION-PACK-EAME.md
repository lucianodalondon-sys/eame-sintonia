# ARBITRATION PACK · SINTONIA EAME

**Data:** 2026-08-31 · **Autocontido.** Quem ler isto não precisa da conversa.
**Branch:** `claude/eame-refresh-correction-pre-arbitration` · base `eb18c87` (testemunha V1)

```
READY_FOR_ARBITRATION = YES
FINAL_TOOL_SET_DECIDED = NO   ·   CASCO_V7_MODIFIED = NO   ·   NEW_COLLECTION = NO
```

---

# A · O QUE CHEGA À MESA

Quatro handoffs obrigatórios aceitos, um red team externo aceito, e **duas passagens de
correção** — a segunda delas corrigindo erros da primeira.

| | |
|---|---|
| **entradas** | Creator Map `248bd27` · Foresight `dc32ce0` · Territorial `11fd7b5` (handoff `4ea268d`) · Meta `acfd987` (handoff `a2fad2d`) |
| **opcionais** | Deep Corpus `a509c12` · Multilingual `1443f64` (guardrail) · RAIF em árvore |
| **suíte** | 504 provas, 0 falhas |
| **coleta nesta passagem** | zero. `NETWORK_REQUESTS = 0` |

---

# B · O ESTADO, SEM ENFEITE

```
PHENOMENON_CONVERGENCE ................. 0
IDENTITY_CONVERGENCE ................... 36 tuplas · 29 produtos
FULL_CASE_KEYS ......................... 1     IT × Grosseto × trigo duro × fusarium
ATTENTION_READY ........................ 0
ATTENTION_CANDIDATE_TEST ............... 3
CASE_ACT_NOW ........................... 0
REGULATORY_DEADLINE_REVIEW ............. 155 registros elegíveis
BUSINESS_DECISION ...................... 1 candidato (vencimentos IT)
DAILY_INTELLIGENCE_VALUE ............... NOT_PROVED
```

**Um `YES` na pergunta do tempo, em todo o acervo** — e é o mais modesto: a data de
vencimento é **publicada**, não prevista.

---

# C · AS QUATRO DECISÕES QUE PRECISAM DE ÁRBITRO

## C1 · O produto tem **um** tipo de objeto ou **quatro**?

Esta é a decisão estruturante, e ela veio desta passagem.

```
CASE                          país × região × cultura × problema × tempo      1
REGULATORY_DEADLINE           país × registro × produto × prazo             155
IDENTITY_CHAIN                competidor × país × produto                    36
LONGITUDINAL_FIELD_PRESSURE   país × região × cultura × problema × tempo      1
```

**A favor de um só:** todos respondem *"o que merece atenção?"*, e o casco tem uma
superfície para isso.
**Contra:** três deles **não têm cultura nem problema**, e o card de caso foi desenhado em
cima dessa chave. Forçá-los para dentro exigiria inventar cultura e problema — que é
exatamente o que os guards proíbem.

**Consequência de errar:** se forçar tudo em `CASE`, o produto passa a mostrar 155
vencimentos como se fossem casos de campo. Se separar demais, vira menu de dashboards —
`ESSENCE_RISK = HIGH`.

## C2 · Um recorte com **uma** família independente merece fila de atenção?

Hoje: `ATTENTION_READY = 0`, porque nenhum candidato responde *"o que mudou?"*.

**Se a resposta for sim**, o produto entrega 1 caso + 155 vencimentos e admite que a fila
é curta. **Se for não**, a fila fica **vazia** — e um produto de "o que merece atenção" com
fila vazia precisa de outra justificativa para existir.

**As duas respostas são defensáveis. Nenhuma é minha para dar.**

## C3 · Reconstruir cultura × alvo vale o custo?

```
rótulos italianos: manifesto 163 · em disco 139 · faltam 24 → RECOLLECTION_REQUIRED parcial
```

É a peça que destrava portfólio, regulatório e a ligação da camada de concorrente ao caso.

⚠️ **E não produz convergência de fenômeno.** Pela lei
`SEMANTIC_MISMATCH_NOT_CORROBORATION`, *"produto autorizado para trigo duro × fusarium"* é
**contexto**, não confirmação de que o fusarium existe no campo. Destrava contexto e ação —
não convergência.

## C4 · O produto honesto é **semanal**?

`DAILY_INTELLIGENCE_VALUE = NOT_PROVED` em todas as camadas; regulatório fica `PARCIAL`.

A latência medida reforça: o sistema lê documentos com **56 a 172 dias** (França) e **130
dias** (Itália). Um produto diário sobre fontes assim mediria o pipeline, não o mundo.

**Assumir cadência semanal é mais forte do que fingir diária** — mas é decisão de produto.

---

# D · O QUE ESTA PASSAGEM CORRIGIU

**Do red team externo — quatro, todos confirmados:**

1. parser quebrava `FR_VINE_DOWNY_MILDEW` em `VINE_DOWNY` × `MILDEW`;
2. o card do CASE 001 exibia a citação de **septória** num caso de **fusariose**;
3. *"o míldio francês veio de barra lateral"* era largo demais — ele **sobrevive em 4
   itens**, e o bloqueador real é **localidade**;
4. `LAST_90D` = **164**, não 280 — eu havia copiado do briefing.

**Do coordenador — três:** RAIF entra no escopo · `ACT_NOW` ganha escopo · medido separado
de escrito.

**Da própria passagem — dois, meus:**

5. **o corpo dos documentos não está preservado** (só 3.000 caracteres de trecho). Minha
   primeira execução devolveu `fenologia = 0` em 22 de 22, e o zero parecia resultado;
6. o teste de "sem rede" reprovava o próprio script por causa de um **comentário** que
   dizia *"nenhum Apify"* — confundia menção com uso. Refeito com AST.

---

# E · AS LEIS QUE O ÁRBITRO HERDA

```
CONVERGENCE_REQUIRES = SAME_PROPOSITION + INDEPENDENT_EVIDENCE
SEMANTIC_MISMATCH_NOT_CORROBORATION
SAME_INDEX ≠ SAME_EVIDENCE           SAME_PUBLISHER ≠ INDEPENDENT_OBSERVATION
2 CARDS ≠ 2 INDEPENDENT SIGNALS      ROW ≠ ENTITY
CROP_ISSUE_PAIRING_NOT_PROVEN        um documento multi-boletim não autoriza cartesiano
OBSERVATION_STAGE ≠ CURRENT_STAGE    PIPELINE_LATENCY ≠ AGE_OF_OBSERVATION
EXPIRY ≠ WITHDRAWAL                  EXPIRY_DATE_REACHED ≠ PRODUCT_DISCONTINUED
IDENTITY_PROVED ≠ ISSUE_EXPERTISE_PROVED
CREATOR ACTIVATION ROUTE ≠ CREATOR ISSUE EVIDENCE
PAGE_COUNTRY_SCOPE ≠ AD_DELIVERY_COUNTRY
IDENTITY IS NOT SIGNAL               NOT_MEASURABLE ≠ NOT_PROVED
CENTRAL_USER_ABSORPTION_GUARD        ocupar a tabela ≠ ser usuário central
```

Cada uma custou uma medição. **Reabrir sem evidência nova é refazer o erro.**

---

# F · O QUE ESTÁ CONGELADO

```
CASCO V7 ..................... byte a byte, SHA-256 a31ea184…87c6a
MULTILINGUAL_CONTRACT_V1 ..... FROZEN em 1443f643
REFRESH_V1_WITNESS ........... eb18c87 — não reescrito
os quatro handoffs ........... ACCEPTED, fixados por commit
ADAMA DISEASE ICONS .......... existem no design system do Claude Design
                               crosswalk NOT_MEASURED · binding NOT_IMPLEMENTED
```

---

# G · BLOQUEADORES EXATOS

```
1  cultura × alvo ausente nos 3 registros nacionais — trava portfólio, regulatório
   e a ligação da camada de concorrente ao caso
2  24 dos 163 rótulos italianos ausentes do disco → RECOLLECTION_REQUIRED parcial
3  localidade ausente em 7 dos 11 itens franceses — o problema está no corpo de 4
4  problema ausente no corpo em 10 de 10 itens espanhóis
5  corpo completo dos 22 documentos NÃO preservado — só 3.000 caracteres de trecho
6  captura única: latência de regime não é separável da idade do documento
7  corpus científico só espanhol — expertise de IT e FR fica NOT_READY, não NOT_PROVED
8  independência RAIF ↔ territorial NOT_PROVED — linhagem parcela-a-parcela não preservada
9  conteúdo das 22 contas de concorrente NOT_STARTED
10 nenhuma camada tem duas leituras com intervalo real → "o que mudou?" sem resposta
```

**Nenhum deles se resolve com fonte nova.** Cinco se resolvem com reprocessamento de
material já preservado; três exigem uma segunda captura; dois são estruturais.

---

# H · A PERGUNTA QUE FICA PARA O ÁRBITRO

> Depois de quatro handoffs, um red team e duas correções, o SINTONIA entrega **um caso,
> 155 vencimentos e 36 cadeias de identidade** — com **zero** convergência de fenômeno e
> **uma** decisão de negócio defensável.
>
> **Isso é um produto em estágio inicial com disciplina rara, ou é uma disciplina rara sem
> produto?**

As duas leituras cabem na mesma evidência. **Escolher é arbitragem, não medição** — e é por
isso que este pacote para aqui.
