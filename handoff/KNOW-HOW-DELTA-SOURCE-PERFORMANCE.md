# KNOW-HOW DELTA — A INTELLIGENCE MEDE A FONTE, E NÃO MANDA NELA

```
MISSAO       C-INT-BIBLE-TOOLS-SOURCEPERF-01
DATA         2026-09-14
DESTINO      SINTONIA-EAME-KNOW-HOW.md — secao nova, a numerar pelo dono
ESTADO       DELTA POR APLICAR
```

---

## ⚠️ POR QUE ISTO É UM DELTA, E NÃO UMA EDIÇÃO DIRETA

O know-how canónico **não está nesta árvore**. Medido no registo de autoridades:

```
A-KNOWHOW
  CANONICAL_PATH   SINTONIA-EAME-KNOW-HOW.md
  CANONICAL_REF    origin/claude/sintonia-eame-know-how-v1
  NOTA DO REGISTO  «A copia esta 50 commits atras do dono. Escrever um
                   SINTONIA-EAME-KNOW-HOW.md novo em `main` criaria a terceira
                   versao — e isso e o ataque RT04.»
```

Escrever no ficheiro que está aqui produziria a terceira cabeça. O delta segue o
precedente da casa — `handoff/KNOW-HOW-DELTA-*.md`, quatro antes deste — e
aplica-o quem é dono do ficheiro.

---

## O APRENDIZADO

### O QUÊ

A Intelligence passa a medir a **contribuição a jusante** de cada fonte: o que
ela produziu depois de atravessar a fronteira, por contexto, e com lineage
provado do princípio ao fim.

### POR QUÊ

Quantidade coletada não mede valor analítico. Bytes, ficheiros e itens admitidos
medem **atividade**. Uma fonte pode entregar muito e cruzar nada; outra pode
entregar quatro documentos por ano e ser a única que fecha um crossing
regulatório.

```
SOURCE PRODUCED CONTENT != SOURCE PRODUCED USEFUL INTELLIGENCE
HIGH VOLUME             != HIGH VALUE
```

### A PROVA

- **Fronteira medida antes de escrita.** `SOURCE_RELEVANCE` já tinha dono —
  `COLLECTION`, módulo `leis/relevancia_da_fonte.py`, estado `OWNER_PROVEN`. E
  responde a outra pergunta: *«esta fonte vale ser acompanhada para este
  propósito?»*, decidida **antes do gasto**. A medição de contribuição é **depois
  do gasto**. Uma é porta, a outra é fita métrica.
- **Benchmark externo.** Microsoft Research, Web Crawl Scheduling (SIGIR 2019 ·
  NeurIPS 2019 · ICML 2020): observabilidade parcial, importância e taxa de
  mudança como dois eixos separados, e o compromisso exploração ×
  exploração-do-conhecido dito com esse nome.
- **Arquitetura revisada.** Bíblia da Intelligence V0.3, secção 36, com 11 leis
  (`INT-LAW-290..299` e `INT-LAW-302`) e 15 ataques de red team, cada um com a
  lei que o barra.

### A CONSEQUÊNCIA

A Collection poderá, no futuro, receber um **conselho contextual** sobre fontes
sem entregar o seu ownership à Intelligence.

```
INTELLIGENCE
  → SOURCE_COLLECTION_ADVICE
  → FRONTEIRA CANONICA DA COLLECTION
  → ORQUESTRADOR DA COLLECTION
  → proxima coleta
```

```
SOURCE PERFORMANCE RECOMMENDS
COLLECTION DECIDES
```

---

## AS TRÊS COISAS QUE VALE A PENA NÃO REAPRENDER

### 1 · A ausência de prova não é prova de ausência — e o sistema fecha esse laço sozinho

Da Microsoft Research: *só se descobre que uma fonte mudou indo lá.* Se se
prioriza apenas quem já provou valor, quem nunca foi amostrado nunca prova nada,
e a falta de prova passa a parecer fraqueza. O sistema confirma a si próprio uma
medida que nunca fez.

Por isso `SAMPLE_SIZE = 0` dá `PERFIL = UNKNOWN`, **nunca «fraco»** — e por isso
a quota de exploração ficou **por escolher**: fixar uma percentagem sem medição
seria inventar exatamente a medida que a lei existe para exigir.

### 2 · Evidência contrária é valor, e penalizá-la ensina o sistema a concordar

Uma fonte que derrubou uma Opportunity errada produziu valor. `SUPPORT_VALUE` e
`CONTRADICTION_VALUE` registam-se em separado e **nunca se somam num saldo** —
somá-los deixaria a segunda a descontar da primeira, que é o mesmo que preferir
fontes concordantes.

### 3 · A palavra escolhida faz o trabalho de a lei não ter de ser relida

`PRIORITY` foi aposentado como nome sobrecarregado por decisão humana datada de
2026-09-14. As prioridades que restam — `PRIORITY_TIER`, `REQUIREMENT_PRIORITY` —
são da Collection, com módulo e prova.

Um objeto da Intelligence chamado `..._PRIORITY_...` leria-se, seis meses depois,
como se a Intelligence tivesse uma prioridade própria. Chama-se
`SOURCE_COLLECTION_ADVICE`, e o contrato **não tem campo com o número final da
prioridade** — tem uma direção (`REPROCESS_FIRST | MORE | SAME | LESS |
INVESTIGATE | UNKNOWN`). A ausência é deliberada: um número atravessaria a
fronteira e seria obedecido.

---

## E UMA QUARTA, SOBRE COMO SE ESCREVE LEI

O enunciado mandou avaliar **onze** leis candidatas. Sete entraram; **quatro não**,
por já existirem com outro nome: `INT-LAW-021`, `INT-LAW-023`, `INT-LAW-060` e
`INT-LAW-042`.

```
UMA BIBLIA QUE CRESCE POR ACUMULACAO DEIXA DE SER LEI E PASSA A SER ARQUIVO.
```

Recusar as quatro foi trabalho da mesma natureza que escrever as sete — e é o que
a `INT-LAW-000` (um conceito, um dono) obriga.

---

# ADENDA — C-INT-BIBLE-RECONCILIATION-01 (2026-09-14)

## 1 · UM RELATÓRIO QUE DIZ «NÃO EMPURREI» NÃO PROVA QUE A BRANCH NÃO EXISTE

O fecho da missão anterior declarou, de boa-fé, que nada tinha sido empurrado:
`git ls-remote` daquele instante devolveu vazio. Horas depois a branch **estava**
no GitHub, no mesmo `2b5ec12f`.

Daí nasceu uma missão inteira para «recuperar» trabalho que nunca se perdeu.

**A medição que faltava não era de igualdade de hash, era de ancestralidade:**

```bash
git merge-base --is-ancestor <ponta-canonica> HEAD && echo CONTIDA
git rev-list --count HEAD..<ponta-canonica>      # quantos me faltam
git rev-list --count <ponta-canonica>..HEAD      # quantos tenho a mais
```

Medido: `0c26981b` (ponta canónica) é **ancestral** de `2b5ec12f`. Zero atrás,
dezassete à frente. Não havia divergência nenhuma — havia uma branch por
integrar.

```
HASH DIFERENTE != LINHA DIVERGENTE
BRANCH POR INTEGRAR != TRABALHO PERDIDO
```

**Consequência:** antes de declarar perda e reconstruir de memória, medir
ancestralidade. Reconstruir «21 leis» porque um relatório disse 21 teria criado
uma segunda Bíblia a partir de uma lembrança.

## 2 · O CONSELHO DE FONTE PODIA MANDAR COLETAR O QUE JÁ ESTAVA CÁ

A secção 36 nasceu sem citar a `INT-LAW-152` — *reprocessar antes de recolher*.

Não era defeito teórico. A medição da demanda de dados da Itália, do mesmo dia,
diz:

```
REGISTOS JA RECOLHIDOS   7.078
CRUZAMENTOS              12   ·  3 POSSIBLE · 3 PARTIAL · 6 NOT_POSSIBLE
OS 6 IMPOSSIVEIS         falham todos pelo MESMO campo: ISSUE_ID
VOCABULARIO              24 ISSUE_ID distintos contra 172 nomes em texto livre
```

> «o nome citado ja esta no material recolhido. Falta identidade, nao falta fonte.»

Um perfil de contribuição corrido sobre este estado veria seis cruzamentos a
falhar e diria `MORE` a seis fontes — **e estaria errado nas seis**. Nenhuma
coleta nova produz um `ISSUE_ID`.

Fechado pela `INT-LAW-302`: `MORE` exige `REPROCESSING_CHECKED = SIM`, e
`REPROCESS_FIRST` passou a ser direção de primeira classe.

```
FALTA DE CHAVE PARECE FALTA DE DADO,
E A CONFUSAO ENTRE AS DUAS PAGA-SE EM COLETA.
```

## 3 · E UMA CITAÇÃO PARA LEI QUE NÃO EXISTIA

O texto da V0.3 citava `INT-LAW-068`. A secção de dependência começa na `070`.
Ninguém tinha reparado porque **nenhuma prova da casa verifica que uma lei
citada existe** — o `valida_biblia.py` faz isso para a Bíblia da Coleta
(`B7_REFERENCIA_EXISTE`), e não há equivalente para a da Intelligence.

A verificação que o apanhou, e que vale a pena repetir, expande intervalos
(`INT-LAW-070..077`) antes de comparar com as leis definidas por `## INT-LAW-`.

**Candidato a prova nova:** `B7` da Intelligence. Não foi criado nesta missão —
criar prova é obra, e esta missão era de reconciliação.
