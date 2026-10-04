# A PROMOÇÃO DA BÍBLIA — MEDIÇÃO DOS NOVE GATES

```
MISSAO      C-INT-NIGHT-01
ESPECIE     MEDICAO DE PORTOES. NAO PROMOVE.
MEDIDO_EM   2026-09-14
ESCOPO      SINTONIA ITALIA
```

> A missão estava autorizada a promover a Bíblia **somente se todos os gates
> técnicos passassem**.
>
> **Oito dos nove passam. O sexto reprova.**
>
> A regra do enunciado é explícita: «Não relaxar condição existente». Por isso
> a Bíblia **não foi promovida**, e por isso o runtime da Fase 3 **não começou**.

---

# 1 · A DECISÃO HUMANA, APLICADA

```
RELEVANCE = [A] APOSENTAR O NOME NU     ->  NAKED_RELEVANCE_RETIRED = YES
PRIORITY  = [A] APOSENTAR O NOME NU     ->  NAKED_PRIORITY_RETIRED  = YES
```

Aplicada na **fonte** — `provas/arbitragem_da_intelligence.py` — e não no
ficheiro gerado. No lugar dos dois nomes entraram os nove conceitos que eles
escondiam, cada um com o dono que já tinha:

| conceito | owner | módulo |
|---|---|---|
| `SOURCE_RELEVANCE` | COLLECTION | `leis/relevancia_da_fonte.py` |
| `ITEM_RELEVANCE` | COLLECTION | `admissao/admissao.py` |
| `CROP_RELEVANCE` | COLLECTION | rótulo vindo da fonte |
| `CASE_RELEVANCE` | INTELLIGENCE | `leis/adama_relevance.py` |
| `USER_DECISION_RELEVANCE` | `SEM_DONO_DECLARADO` | métrica `INT-LAW-251` |
| `REQUIREMENT_PRIORITY` | COLLECTION | `leis/gestao_da_coleta.py` |
| `PRIORITY_TIER` | COLLECTION | `leis/politica_da_coleta.py` |
| `COMMERCIAL_PRIORITY` | INTELLIGENCE | `motor/v21_comercial.py` |
| `WATCHLIST_PRIORITY` | INTELLIGENCE | — (`DEFINED_ONLY`) |

E um dicionário novo, `NOMES_APOSENTADOS`, guarda **o que cada nome cobria** e
**por que não tem dono**.

```
UM NOME APOSENTADO SEM A LISTA DO QUE ELE COBRIA
E UM APAGAMENTO COM OUTRO NOME.
```

## Versionamento — o V2 não foi reescrito

```
V2  a medicao ANTES da decisao   · SUPERSEDED_BY escrito dentro
V3  a medicao DEPOIS da decisao  · 32 conceitos · 0 pendentes · 0 conflitos
```

`test_o_V2_fica_como_historia_e_nao_foi_reescrito` segura-o nesse estado.

```
UM CENSO QUE MUDA DEPOIS DE MEDIDO DEIXA DE PODER SER CONFERIDO.
```

---

# 2 · OS NOVE GATES, MEDIDOS HOJE

| # | requisito (§31 da Bíblia) | prova | resultado |
|---|---|---|---|
| 1 | reconciliação com a Bíblia da Collection | `INT-LAW-000` dá `CLAIM/FACT` à Collection; a Bíblia da Coleta está nesta árvore | **PASS** |
| 2 | reconciliação com Motor V2 | 0 ocorrências de `CANDIDATE_FINDING`, `VALIDATION_QUEUE`, `ANALYTIC_HYPOTHESIS`, `INTELLIGENCE_RUN`, `COLLECTION_GAP` no Motor V2 | **PASS** |
| 3 | owner collision count = 0 | V3: 0 conflitos, 0 `HUMAN_DECISION_REQUIRED` | **PASS** |
| 4 | registo no Control Plane | as duas autoridades no registo; Sala de Controle na árvore | **PASS** |
| 5 | snapshot onde a autoridade não fique invisível | as 15 autoridades abrem aqui (`P1`, 3 testes) | **PASS** |
| 6 | **governance gate** | `controle/portao_do_controle.py` | **FAIL** |
| 7 | System Map pela cadeia canónica | `SYSTEM_MAP_CHECK=PASS` | **PASS** |
| 8 | know-how delta aplicado ao owner canónico | `§111`–`§114` no ficheiro canónico | **PASS** |
| 9 | aprovação explícita da promoção | o enunciado desta missão autoriza, condicionalmente aos gates 1–8 | **PASS condicional** |

```
BIBLE_PROMOTION_GATES_TOTAL = 9
BIBLE_PROMOTION_GATES_PASS  = 8
BIBLE_PROMOTION_GATES_FAIL  = 1
BIBLE_PROMOTION_GATES_HUMAN = 1  (o 9, e ele estava dado)

BIBLE_CANONICAL_PROMOTION_READY = NO
BIBLE_PROMOTED                  = NO
BIBLE_INITIAL_STATUS            = CANDIDATE_FOR_CANONICAL_REVIEW
BIBLE_FINAL_STATUS              = CANDIDATE_FOR_CANONICAL_REVIEW
```

---

# 3 · O BLOQUEADOR, COM NOME E NÚMERO

`PORTAO_DO_CONTROLE=FAIL · 2 provas reprovadas`

## 3.1 · `UNREGISTERED_CANONICAL_DOCUMENT = 10` (tecto 0)

Dez documentos na árvore dizem-se lei e não estão no registo de autoridades.
Atribuídos um a um:

```
1  docs/intelligence/INTELLIGENCE-ARBITRATION-V1.md   ERA MEU — REGISTADO NESTA MISSAO
10 docs/operacao/*.md                                 JA ESTAVAM NO TRONCO dc00583d
```

Os dez restantes são documentos de **operação da Collection**:

```
A-CASA-DO-DERIVADO · CIRURGIA-OBJETO-E-OBSERVACAO ·
CONTRATO-DOS-STRUCTURED-TARGETS · ENCANAMENTO-DA-COLETA ·
IDENTIDADE-DA-OBSERVACAO-RAW · STRUCTURED-POR-ESPECIE-E-NOT-APPLICABLE ·
TOPOLOGIA-DA-COLETA · ...
```

Registá-los exige declarar `CONCEPT_OWNER`, `SCOPE` e `LIFECYCLE` de conceitos
da Collection. **Isso é decisão do dono da Collection**, e esta missão está
proibida de a tomar.

## 3.2 · `BROKEN_POINTER` — um ponteiro, e é de modelo

```
A-BIBLIA-ENG-INTELIGENCIA.SUPERSEDES = ['A-BIBLIA-INTELIGENCIA']
```

O censo classifica `SUPERSEDES` como `TEXT_POINTER` — aponta para **caminhos**.
O registo escreve-lhe um **CARD_ID**. E do outro lado, `A-BIBLIA-INTELIGENCIA`
tem `SUPERSEDED_BY = ['A-BIBLIA-ENG-INTELIGENCIA']`, também um CARD_ID.

```
O REGISTO USA CARD_ID PARA SUPERSESSAO.
O CENSO LE SUPERSEDES COMO CAMINHO.
OS DOIS ESTAO DENTRO DO CONTROL PLANE, E DISCORDAM.
```

Apontar para o caminho não resolve: `docs/biblia/BIBLIA-DA-INTELIGENCIA-EAME.md`
não existe nesta árvore — é uma autoridade legitimamente `STALE`, canónica
noutra branch. **O modelo não sabe representar «supersedi uma autoridade que
não mora aqui».**

Redesenhar isso é do dono do Control Plane.

---

# 4 · A CAUSA DE FUNDO — E É A QUARTA VEZ COM A MESMA FORMA

```
controle/CHAO-DO-CONTROLE.json   HEAD = a885769c54
git merge-base --is-ancestor a885769c54 HEAD   ->   FALSO
```

**O tecto `UNREGISTERED_CANONICAL_DOCUMENT = 0` foi medido noutra árvore.**
Foi fixado na branch da arbitragem, onde os dez documentos de `docs/operacao/`
não existiam. Aplicá-lo aqui não mede «piorou»: mede «é outra árvore».

E o gate **nunca tinha corrido nesta árvore**. A missão `C-INT-ATOMICITY-01`
integrou o portão de governança e o seu chão, declarou-se verde, e nunca o
executou.

```
IMPORTAR UM PORTAO NAO E PASSAR NELE.
E UM PORTAO COM O CHAO DE OUTRA CASA MEDE A MUDANCA DE CASA,
NAO A MUDANCA DE ESTADO.
```

É o mesmo defeito de `§111` (grafo truncado), `§112` (chave estrangeira para
ninguém) e `§114` (nome sobrecarregado): **um número correto lido contra a
fotografia errada.**

## O que NÃO foi feito, e porquê

```
NAO se correu `--fixar` para subir o tecto de 0 para 10.
O portao diz, de si proprio: «--fixar DESCE o teto — e ele nunca mais sobe».
Usa-lo aqui seria relaxar uma condicao, e o §9 do enunciado proibe-o.

    UM TECTO QUE SOBE QUANDO FALHA NAO E UM TECTO.
```

---

# 5 · O QUE ESTA MISSÃO CONSERTOU NO PORTÃO

Duas das quatro reprovações iniciais, e as duas eram minhas:

```
ANTES   BROKEN_POINTER = 2 · UNREGISTERED = 11
DEPOIS  BROKEN_POINTER = 1 · UNREGISTERED = 10
```

1. **`system-map/data/controle.generated.json` nunca tinha sido commitado.**
   `censo_do_controle.py` escreve-o e o gerador do mapa lê-o; a integração
   anterior nunca correu o censo, e o ficheiro ficou fora do Git. Agora está
   versionado, como os outros dezoito `.generated.json`.

2. **`docs/intelligence/INTELLIGENCE-ARBITRATION-V1.md` não estava no registo.**
   É documento da Intelligence, trazido pela minha própria integração.
   Registado como `A-ARBITRAGEM-INTELIGENCIA`, com `GOVERNS` a apontar para o
   resultado vivo (`INTELLIGENCE-CONCEPT-OWNERSHIP-V3.json`).

   ⚠️ E ao registá-lo repeti o erro do §3.2: escrevi CARD_IDs em `GOVERNS` e
   `REFERENCES`. O portão apanhou-me na mesma corrida, e a correcção foi
   usar caminhos.

```
O PORTAO DE OUTRA FRENTE APANHOU-ME DUAS VEZES NA MESMA HORA.
E DAS DUAS TINHA RAZAO.
```

---

# 6 · CONSEQUÊNCIA: A FASE 3 NÃO COMEÇOU

O `GATE 2` do enunciado é inequívoco:

> Se `BIBLE_CANONICAL_PROMOTION_READY = NO`: **NÃO implementar runtime novo.**

Portanto:

```
INTELLIGENCE_RUN_IMPLEMENTED     = NO
INTELLIGENCE_REQUEST             = DEFINED_ONLY
SIGNAL · SCREENING · CROSSING    = inalterados
ANALYTIC_HYPOTHESIS              = DEFINED_ONLY
VALIDATION_STATE                 = DEFINED_ONLY
FINDING · REVERSAL               = inalterados
INTELLIGENCE_REQUIREMENT         = DEFINED_ONLY

REAL_ITALY_DRY_RUN               = NOT_RUN
REASON                           = a Fase 5 depende da Fase 3, que nao comecou
CASOS ITALIA A–H                 = NOT_RUN pelo mesmo motivo
```

**Nenhuma fixture italiana foi escrita**, porque uma fixture sem runtime que a
consuma é documentação com extensão `.py`.

```
MAIS FIXTURES SEM RUNTIME NAO E MAIS PROVA. E MAIS SUPERFICIE.
```

---

# 7 · O QUE NÃO MUDOU

```
COLLECTION_RUNTIME   INTACTO — 0 ficheiros de coleta/, admissao/, guarda/,
                     leis/, orquestrador/ alterados
PORTAL               INTACTO
LIVE                 0 leituras · 0 escritas
MIGRATIONS           INTACTAS · nenhuma criada
FRANCE · SPAIN       NAO TOCADOS
EAME_CONTROLLER      NAO EXISTE, e nao foi comecado
SALES_READY          NAO RENOMEADO — divida registada, §2 do enunciado
BIBLIA               NAO PROMOVIDA
```

---

# 8 · O PRÓXIMO PASSO MÍNIMO — UMA MISSÃO

```
C-CTRL-FLOOR-01   (frente CONTROL PLANE, nao INTELLIGENCE)

   Re-fixar o chao do Control Plane contra a arvore integrada e resolver o
   modelo de supersessao (CARD_ID vs TEXT_POINTER), registando os dez
   documentos de docs/operacao/ com os seus donos reais.

   NAO promove a Biblia. NAO implementa runtime. NAO toca Collection runtime.
```

**Porquê esta, e porquê não é da Intelligence:** o único gate que falta é o de
governança, e as duas causas vivem no Control Plane — um chão medido noutra
árvore, e um modelo de ponteiro que discorda de si próprio. A Intelligence não
pode consertar nenhuma das duas sem declarar donos de conceitos da Collection.

```
DEPOIS DESSA MISSAO, A PROMOCAO DA BIBLIA E UM COMANDO,
E O RUNTIME DA INTELLIGENCE DEIXA DE TER BLOQUEADOR.
```

---

# 9 · O QUE FICA EM NÃO SEI

```
NAO_SEI  quem possui cada um dos dez documentos de docs/operacao/. Tem dono
         real — sao da Collection — mas nomea-lo aqui seria invenção.

NAO_SEI  se o modelo certo para supersessao e CARD_ID ou caminho. Os dois
         lados do Control Plane discordam, e a decisao e do dono dele.

MEDIDO   a Sala de Espera desta arvore esta VAZIA:
         data/samples/PRONTO-PARA-INTELIGENCIA/  ->  0 ficheiros

         Ha 17 pastas `data/samples/IT-*` com material italiano (ARPAV Veneto,
         bollettini, catalogo, ciencia, cruzamento...), mas NENHUMA delas
         atravessou a porta de admissao para a morada READY.

         Logo, mesmo com o runtime pronto, a Fase 5 teria corrido sobre zero
         itens. O bloqueio da Fase 3 escondeu um segundo bloqueio que estava
         atras dele.

             MATERIAL NA ARVORE != MATERIAL ADMITIDO.
             E A SALA DE ESPERA VAZIA NAO E UM DEFEITO DA INTELLIGENCE:
             E O ESTADO DA COLLECTION, MEDIDO.

NAO_SEI  o custo de uma execucao de Intelligence. Nao ha execucao.
         COST = UNKNOWN, e nao 0.
```
