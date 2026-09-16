# RED TEAM DA ARBITRAGEM DA INTELLIGENCE

```
MISSAO   C-INT-ARB-01 · 2026-09-13
ALVO     a arbitragem, e nao a maquina
```

> Dois destes doze ataques derrubaram conclusões minhas. Ficam escritos com o
> erro à vista.

---

## 1 · «escolheu owner pela quantidade de arquivos»

**DEFENDIDO — e foi precisamente isso que o censo tinha feito.**

O censo deu `OPPORTUNITY_OWNER = NÃO SEI` porque contou massa: 50 ficheiros em
`italia-portale`, 29 em `build`. A arbitragem não escolheu o maior — leu
**comportamento**:

```
quem descobre convergencias e aplica oito portoes    motor/v21_oportunidades.py
quem guarda                                          build/OPPORTUNITIES.json
quem le CLIENT_SAFE sem recalcular                   italy-app-model.js
```

O portal tem a maior massa e **não** é o dono.

```
MASSA NAO E PROPRIEDADE.
```

---

## 2 · «chamou apresentação de criação»

**DEFENDIDO, com medição.** `italy-app-model.js` tem 5 124 linhas e **1**
ocorrência de cálculo; lê `CLIENT_SAFE` (13×) e `RENDERABLE_WITH_METHOD` (5×) —
portões decididos a montante. É projeção.

E há autoridade prévia: `INT-LAW-023` — «Portal não reconstrói Intelligence».

---

## 3 · «chamou artefato congelado de owner»

**DEFENDIDO.** `build/…/OPPORTUNITIES.json` foi classificado
`OPPORTUNITY_STORAGE`, nunca owner. Um ficheiro que não decide nada não pode
possuir o conceito que carrega.

---

## 4 · «promoveu Bible sem resolver Motor V2»

**DEFENDIDO — a Bíblia não foi promovida.**

```
BIBLE_PROMOTION_READY = NO
```

A relação com o Motor V2 **foi** resolvida (0 conflitos estruturais). O
bloqueador é outro, e é a condição 5 da própria Bíblia: cinco branches, nenhum
commit contém todas.

---

## 5 · «deu FACT/CLAIM para Intelligence porque o arquivo tem claim no nome»

**DEFENDIDO, e é o ataque que a missão mandou fazer.**

`FACT_CLAIM_COLLISION = NAME_COLLISION`, provado por comportamento:

```
grep CLAIM_ID motor/*.py        →  VAZIO
grep sha256|uuid|hashlib no ficheiro  →  VAZIO
ids sobre que opera             →  IT-CAN-… (upstream, ja existentes)
```

O ficheiro julga se uma alegação é **sobre o mundo** ou **sobre o encanamento**.
Isso é `CLAIM_DOMAIN_JUDGMENT`, e o `SOURCE_FACT/CLAIM` fica com a Collection por
`INT-LAW-000`.

---

## 6 · «criou uma segunda identidade factual»

**DEFENDIDO.** Nenhum conceito novo cunha identidade factual.
`CLAIM_DOMAIN_JUDGMENT` herda explicitamente o ID upstream — está escrito no
campo `CANONICAL_IDENTITY` do JSON de propriedade: *«herda o ID upstream; não
cunha novo»*.

---

## 7 · «chamou import de fluxo»

**DEFENDIDO, e virou achado contra o instrumento.** Nenhuma aresta foi promovida
por import. Pelo contrário: a arbitragem define `IMPORT_OBSERVED` como um nível
**abaixo** de `CALL_OBSERVED`, e mede que hoje há 34 imports e **zero** chamadas.

---

## 8 · «chamou portão de motor de Intelligence»

**❌ DERROU-ME. Corrigido.**

Eu tinha os três `lineage_*` como `PROVEN_OPERATIONAL` no censo, por os portões
correrem e passarem. Verdade — mas isso prova que **o portão** funciona, não que
haja motor analítico ali.

`build-gate.mjs` e `stale-generator-gate.mjs` verificam proveniência de um
pacote. Isso é **governança**, não produção analítica. Daí
`MOVE_TO_GOVERNANCE` para os três, e não `KEEP_CANONICAL`.

```
UM PORTAO QUE GUARDA A INTELIGENCIA NAO E INTELIGENCIA,
DA MESMA FORMA QUE O PORTEIRO NAO E O INQUILINO.
```

---

## 9 · «declarou canonical uma branch não integrada»

**DEFENDIDO.** Nada foi declarado canónico. O gerador canónico
(`51010733`) não foi *declarado* por mim — foi **medido**: é o que dois portões
executáveis aceitam, e a alternativa (`55c2674`) está listada como safra velha
pelo documento que os portões leem.

E a Bíblia continua `CANDIDATE`.

---

## 10 · «usou System Map como autoridade da arquitetura»

**DEFENDIDO, e a arbitragem faz o contrário.** O mapa forneceu a **população**
(12 peças) e nada mais. Onde ele afirma, a arbitragem contradiz: as 82 arestas
`PROVEN` são recusadas como prova de fluxo, com a contagem que as desmonta.

```
O MAPA DIZ QUEM ESTA NA SALA. NAO DIZ QUEM MANDA NELA.
```

---

## 11 · «confundiu CAN DO com DID DO»

**DEFENDIDO, e está na classificação.** O caminho directo
`normalize_agro → eppo_gd` é `KEEP_BUT_BLOCK`, com as duas metades separadas:

```
existe em codigo e alcanca a rede     CAN DO
0 chamadores, nenhuma rota o anda     DID DO = NAO
```

Também: `INTELLIGENCE_RUN` e `COLLECTION_GAP` ficam `CONTRACT_READY = YES` e
`IMPLEMENTED = NO`, sem confundir contrato com implementação.

---

## 12 · «tomou decisão humana nova onde um ADR anterior já decidia»

**❌ DERRUBOU-ME. Corrigido.**

Ia declarar `INTELLIGENCE_TEST_RUNNER = unittest` como **decisão desta missão**.
Procurando primeiro, encontrei-a já tomada:

```
docs/decisoes/DIARIO-DE-DECISOES.md  D-009
  todo total publicado num documento canonico tem de ter uma prova que o derive
  → tests/test_canonico.py conta a suite com unittest.defaultTestLoader.discover
```

Mais 5 workflows a correr `python3 -m unittest`, pytest não declarado em
requirements nem instalado, e 148 de 152 ficheiros já em unittest.

Reclassificado: **auditoria de decisão existente**, não decisão nova. A escolha
do runner não era minha para fazer — já estava feita, e a Intelligence é a única
área que a quebra.

```
UMA DECISAO QUE JA EXISTE E TOMADA OUTRA VEZ
PASSA A EXISTIR DUAS VEZES, E DIVERGE NA TERCEIRA.
```

---

## PLACAR

```
ATAQUES               12
DEFENDIDOS            10
DERRUBARAM             2   (8 · 12)
CORRIGIDOS ANTES DE FECHAR  2
```

Os dois que passaram têm formas diferentes, e ambas valem a pena guardar:

- o **8** confundiu *guardar* com *produzir* — o portão que protege a Intelligence
  não é Intelligence;
- o **12** ia criar uma segunda decisão onde já havia uma, que é o mesmo pecado
  que esta arbitragem existe para resolver, cometido pelo árbitro.
