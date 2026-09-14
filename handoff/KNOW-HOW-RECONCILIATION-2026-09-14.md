# RECONCILIAÇÃO DO KNOW-HOW CANÓNICO — 2026-09-14

```
MISSAO        C-KNOW-HOW-RECONCILIATION-V1
ESPECIE       AUDITORIA. NAO E O KNOW-HOW. NAO E FONTE DE VERDADE.
DONO CANONICO SINTONIA-EAME-KNOW-HOW.md  (um, e so um)
```

> ## ⚠️ ESTE FICHEIRO NÃO É UMA SEGUNDA FONTE DE VERDADE
>
> Ele é a **prova** de que a reconciliação aconteceu, e o registo de como cada
> decisão foi tomada. A lei vive em `SINTONIA-EAME-KNOW-HOW.md`, `§121`–`§141`.
> Se este relatório e o know-how discordarem, **o know-how vence** — e a
> discordância é um defeito deste ficheiro, não uma segunda opinião.
>
> ```
> UM RELATORIO PROMOVIDO A LEI E A DOENCA QUE ESTA MISSAO VEIO CURAR.
> ```

---

## 0 · BASE MEDIDA, NÃO HERDADA

```
START_BRANCH            claude/sintonia-eame-know-how-v1
START_HEAD              5705ac7bc704cc9c5b8925259a0a6a47f6eecc47
REMOTE_CANONICAL_HEAD   5705ac7bc704cc9c5b8925259a0a6a47f6eecc47   (iguais)
BASE_CANONICAL_BRANCH   claude/sintonia-eame-know-how-v1
BASE_CANONICAL_HEAD     5705ac7bc704cc9c5b8925259a0a6a47f6eecc47
RECONCILIATION_BRANCH   claude/know-how-reconciliation-v1
CANONICAL_FILE          SINTONIA-EAME-KNOW-HOW.md   (raiz do repositorio)
```

O enunciado dava `5705ac7b` como referência observada. **Git venceu, e
concordou.** O dono canónico não foi editado: a candidata vive noutra branch.

---

## 1 · CENSO — O NÚMERO DE ENTRADA ERA UMA HIPÓTESE, E FOI REMEDIDO

```
REFS_SCANNED                     20   (19 remotas + 1 local de rastreio)
DISTINCT_CONTENTS                15   (o enunciado supunha 16)
FIRST_DIVERGENT_SECTION          §61
HIGHEST_SECTION_ANYWHERE         §120
NEXT_SAFE_SECTION                §121
```

### 1.1 · As vinte referências

| ref | HEAD | blob | bytes | § | maior § |
|---|---|---|---|---|---|
| `origin/claude/sintonia-eame-know-how-v1` | `5705ac7b` | `0eca6fa7` | 546533 | 65 | §119 |
| `refs/heads/claude/sintonia-eame-know-how-v1` | `5705ac7b` | `0eca6fa7` | 546533 | 65 | §119 |
| `origin/claude/intelligence-pilot-v1` | `0aacefd0` | `edc43d5c` | 530154 | 66 | §120 |
| `origin/claude/intelligence-system-map-audit-v1` | `a67695d5` | `c070933c` | 524333 | 65 | §119 |
| `origin/claude/italy-source-isolation-jb6wed` | `89a5fdf4` | `07ceb9f7` | 520470 | 64 | §118 |
| `origin/claude/intelligence-object-model-v1` | `4cf43b0e` | `55821887` | 519481 | 64 | §118 |
| `origin/claude/control-plane-intelligence-night-v2` | `2b3d58d8` | `0c2df557` | 515728 | 63 | §117 |
| `origin/claude/intelligence-night-v1` | `207745da` | `0f057a40` | 502461 | 61 | §115 |
| `origin/claude/intelligence-atomicity-v1` | `187cdf37` | `4d599b2f` | 498449 | 60 | §114 |
| `origin/tmp/know-how-ready-address-20260913` | `39e685fc` | `08eab1dd` | 470152 | 54 | §108 |
| `origin/claude/wonderful-hamilton-m50ahv` | `6a9907e2` | `db4efe92` | 362846 | 41 | §95 |
| `origin/claude/sintonia-eame-know-how-v1-copy` | `db3d573c` | `2255deb3` | 216279 | 21 | §75 |
| `origin/tmp/another-mistake` | `db3d573c` | `2255deb3` | 216279 | 21 | §75 |
| `origin/tmp/third-mistake` | `db3d573c` | `2255deb3` | 216279 | 21 | §75 |
| `origin/tmp/fourth-mistake` | `db3d573c` | `2255deb3` | 216279 | 21 | §75 |
| `origin/tmp/fifth-mistake` | `db3d573c` | `2255deb3` | 216279 | 21 | §75 |
| `origin/tmp/unused` | `d9300363` | `dd9b514b` | 210720 | 20 | §74 |
| `origin/claude/know-how-sequence-v1` | `b5c457f8` | `e9161d7c` | 142973 | 7 | §61 |
| `origin/claude/know-how-merge-test-v1` | `b50c230d` | `3d4f5b49` | 141053 | 7 | §61 |
| `origin/claude/know-how-order-after-reader-gap-v1` | `7d46dedd` | `a4c3ad88` | 57268 | 0 | — |

Nenhuma referência local não publicada carregava o ficheiro: a única `refs/heads`
é a de rastreio, e aponta para o mesmo blob da remota.

### 1.2 · A correcção que a remedição fez ao próprio enunciado

O relatório de entrada dizia **16 conteúdos** e **§118 com quatro significados**.
Medido contra os objectos do git:

```
16 conteudos  ->  15
§118 com 4    ->  §118 com 3 significados
```

Não foi erro de quem contou antes. **Cinco pares de secções diferiam apenas pelo
separador `---` no fim** — presente quando outra secção vinha a seguir, ausente
quando era a última do ficheiro. Diferença medida: 3 linhas, zero palavras.

```
§114  874c084fd560 vs f48a1fe29086   so o «---» final
§115  f240a70b0a68 vs 249774c444e0   so o «---» final
§117  9ce4f9a2e426 vs 4350c09dc3d6   so o «---» final
§118  5bab76cb6887 vs 1c022cb3e762   so o «---» final
§119  eba0c7318a4c vs 992b35254d45   so o «---» final
```

```
BYTES DIFERENTES != CONHECIMENTO DIFERENTE.
```

O mesmo artefato explica `§74`, `§75`, `§88`, `§90` e `§108`, que apareciam como
divergentes contra a linha canónica e são **idênticos**.

---

## 2 · AS TRÊS FAMÍLIAS DE COLISÃO

Divergência de *título* começa no `§61`. Colisão de *endereço* — conhecimentos
diferentes no mesmo número — acontece em três blocos:

### 2.1 · `§61` — uma decisão do dono apagada por uma missão funcional

| linha | §61 diz |
|---|---|
| canónica (e 12 outras) | A FONTE ATRAVESSA — E TRÊS MUTANTES QUE ENSINARAM A TESTAR |
| `know-how-sequence-v1` `b5c457f8` | **A ORDEM DO PROJETO FICA COLLECTION COMPLETA → COLETA GRANDE → INTELLIGENCE → CASCO** |

A segunda é uma **decisão do dono do projeto**, de 2026-09-11, com registo em
`docs/decisoes/ORDEM-DO-PROJETO-COLETA-INTELIGENCIA-CASCO-2026-09-11.md`, commit
`b44b3f0a`. Três horas depois, `b50c230d` escreveu outra coisa no mesmo `§61`.

**Prova de que continua a valer:** o registo de decisão **existe na árvore
canónica de hoje** (`git cat-file -e HEAD:docs/decisoes/ORDEM-...md` → existe) e
nenhum documento posterior o revoga. Não foi decidido por data: foi decidido pelo
artefato que a sustenta.

```
CURRENT_TRUTH = A ORDEM CONTINUA VALIDA.   ->  entrou como §121
```

### 2.2 · `§91`–`§95` — a linha META-OP / SCRAP-FLOW

`origin/claude/wonderful-hamilton-m50ahv` @ `6a9907e2` escreveu cinco secções em
`§91`–`§95` que nada têm a ver com as canónicas do mesmo número.

Esta linha **viu a colisão e escreveu-a**, duas vezes, no corpo das próprias
secções:

> ⚠️ **NUMERAÇÃO.** Medido nesta missão: o ramo canónico do know-how
> (`claude/sintonia-eame-know-how-v1` @ `72c59dbe`) tem §91, §92 e §93
> **diferentes** dos §91, §92 e §93 desta linha. Três colisões, três missões
> seguidas.

Esses avisos foram **preservados verbatim** na candidata. Renumerá-los apagaria a
prova de que a doença foi vista antes de ser tratada.

### 2.3 · `§111`–`§120` — a linha Intelligence

Sete referências partilham um bloco `§111`–`§120` que colide com o `§111`–`§119`
canónico. Dentro dela, o `§118` tem dois donos distintos (`italy-source-isolation`
e `intelligence-object-model`), e com o canónico faz **três significados no mesmo
endereço**:

| §118 em | diz |
|---|---|
| canónica | A FERRAMENTA PARTIDA MENTE COMO SE FOSSE UM ACHADO |
| `italy-source-isolation-jb6wed` | CONHECER UMA FONTE E AUTORIZAR UMA FONTE SÃO A MESMA PERGUNTA ATÉ ALGUÉM AS SEPARAR |
| `intelligence-object-model-v1` / `-pilot` / `-system-map-audit` | UM MUNDO FECHADO TORNA INVISÍVEL APAGAR UMA PROIBIÇÃO |

---

## 3 · CLASSIFICAÇÃO — CADA CONTEÚDO, UMA CLASSE

```
CANONICAL_KEEP      65   as §55-§119 da linha canonica, mais o prefacio §0-§54
DUPLICATE           10   as 5 gemeas do «---» + as 5 mesmas-secoes re-contadas
COMPLEMENTARY       17   conhecimento provado, ausente da linha canonica
SUPERSEDED           2   a4c3ad88 (subconjunto) + a decisao FILE_WAITING_ROOM_WINS
CONFLICT             2   §61 e a morada da Sala — ambos resolvidos por prova
FALSE_OR_UNPROVEN    0
HISTORICAL_ONLY      1   a4c3ad88, so no relatorio
UNCLASSIFIED         0
```

### 3.1 · Os 17 COMPLEMENTARY, e para onde foram

| novo § | era § | origem | HEAD | lei |
|---|---|---|---|---|
| §121 | §61 | `know-how-sequence-v1` | `b5c457f8` | A ORDEM DO PROJETO FICA COLLECTION COMPLETA → COLETA GRANDE → INTELLIGENCE → CASCO |
| §122 | §91 | `wonderful-hamilton-m50ahv` | `6a9907e2` | UMA ROTA OFICIAL QUE NINGUÉM MODELOU NÃO ESTÁ BLOQUEADA: ESTÁ POR OLHAR |
| §123 | §92 | `wonderful-hamilton-m50ahv` | `6a9907e2` | UMA PORTA ÚNICA É A MELHOR NOTÍCIA QUE UMA TRAVA PODE RECEBER |
| §124 | §93 | `wonderful-hamilton-m50ahv` | `6a9907e2` | UM MÓDULO QUE NÃO CONSEGUE GASTAR AINDA NÃO É UM CAMINHO QUE PASSA PELA CASA |
| §125 | §94 | `wonderful-hamilton-m50ahv` | `6a9907e2` | UMA ROTA QUE NÃO COMPRA NADA AINDA TEM DE OBEDECER A TUDO |
| §126 | §95 | `wonderful-hamilton-m50ahv` | `6a9907e2` | UMA SONDA QUE CONFIRMA UM SEGREDO NÃO PROVA QUE ELE É USADO |
| §127 | §111 | `intelligence-pilot-v1` | `0aacefd0` | UM GRAFO TRUNCADO RESPONDE «NÃO EXISTE» ÀS PERGUNTAS QUE NÃO SABE RESPONDER |
| §128 | §112 | `intelligence-pilot-v1` | `0aacefd0` | UM CONTRATO COM UMA CHAVE ESTRANGEIRA PARA NINGUÉM ESTÁ A DESCREVER UM DONO QUE AINDA NÃO CHEGOU |
| §129 | §113 | `intelligence-pilot-v1` | `0aacefd0` | UM PORTÃO QUE PRENDE O TRABALHO CERTO É UM PORTÃO QUE ALGUÉM DESLIGA |
| §130 | §114 | `intelligence-pilot-v1` | `0aacefd0` | UM CONCEITO SEM DONO E UM NOME COM DONOS A MAIS DÃO A MESMA LEITURA — E EXIGEM O CONTRÁRIO |
| §131 | §115 | `intelligence-pilot-v1` | `0aacefd0` | IMPORTAR UM PORTÃO NÃO É PASSAR NELE |
| §132 | §116 | `intelligence-pilot-v1` | `0aacefd0` | MENCIONAR UMA LEI NÃO É PROMULGAR UMA |
| §133 | §117 | `intelligence-pilot-v1` | `0aacefd0` | PROMOVER É UMA EDIÇÃO EM VÁRIOS SÍTIOS — E EU MUDEI DOIS DE TRÊS |
| §134 | §118 | `italy-source-isolation-jb6wed` | `89a5fdf4` | CONHECER UMA FONTE E AUTORIZAR UMA FONTE SÃO A MESMA PERGUNTA ATÉ ALGUÉM AS SEPARAR |
| §135 | §118 | `intelligence-pilot-v1` | `0aacefd0` | UM MUNDO FECHADO TORNA INVISÍVEL APAGAR UMA PROIBIÇÃO |
| §136 | §119 | `intelligence-pilot-v1` | `0aacefd0` | UM MAPA QUE MOSTRA A MÁQUINA E ESCONDE A LEI ENSINA QUE A MÁQUINA É A LEI |
| §137 | §120 | `intelligence-pilot-v1` | `0aacefd0` | A COLLECTION MEDIU CERTO CONTRA A FOTOGRAFIA DELA |

E as quatro que vieram de deltas nunca integrados, ou da própria reconciliação:

| § | origem | o que é |
|---|---|---|
| §138 | delta `5aa7a77c` — O FERRO NEGOCIADO | GPU/ASR: o tipo de cálculo negoceia-se |
| §139 | delta `52acf72d` — O CAMPO QUE NÃO ATRAVESSA | Collection → Sala: dez leis |
| §140 | delta `a28cade2` — A MORADA DA SALA | **só o método**; a decisão foi amputada |
| §141 | esta missão | a lei do contador partilhado, e a guarda |

### 3.2 · Como as 86 linhas de renumeração foram conferidas

O corpo das 17 secções importadas **não foi reescrito**. Só mudaram:

```
1 · o cabecalho  # §ANTIGO ·  ->  # §NOVO ·
2 · as sub-numeracoes  ## ANTIGO.x ·  ->  ## NOVO.x ·
3 · as referencias a IRMAS DA MESMA LINHA
```

Total: **86 linhas alteradas**, cada uma impressa e conferida à mão. Nenhuma
referência a uma secção canónica (`§60.7`, `§86.4`, `§109`, …) foi tocada: o mapa
de renumeração só conhece os números da própria família.

Os blocos `> ⚠️ NUMERAÇÃO` de `§125` e `§126` ficaram **verbatim**, porque
citam os dois lados da colisão ao mesmo tempo e nomeiam branch e commit: são
auto-desambiguantes, e reescrevê-los destruiria a prova.

---

## 4 · DELTAS — `DELTA EXISTS != DELTA APPLIED`

```
DELTAS_FOUND      15 blobs / 13 nomes distintos
DELTAS_APPLIED     3
DELTAS_SUPERSEDED  3
DELTAS_BLOCKED     9   (revistos, classificados, NAO aplicados — listados abaixo)
UNREVIEWED_DELTAS  0
```

| delta | blob | classe | prova |
|---|---|---|---|
| `KNOW-HOW-DELTA-PAPEL-E-LEITURA-HUMANA.md` | `40c164fe` | **APPLIED** | a lei vive no `§115` canónico |
| `KNOW-HOW-DELTA-ORDEM-POR-DEPENDENCIA.md` | `799ba94b` | **APPLIED** | a lei vive no `§114` canónico |
| `KNOW-HOW-DELTA-INTELLIGENCE-SPINE.md` | `840a0d2a` | **APPLIED** (noutra linha) | declara `APLICADO_EM §111-§113`; medido: é o `§111` da linha Intelligence, agora `§127`–`§129` |
| `KNOW-HOW-DELTA-INTELLIGENCE-SPINE.md` | `004b5ba7` | **SUPERSEDED** | versão anterior de `840a0d2a`, sem a correcção do clone raso |
| `KNOW-HOW-DELTA-108-CONTROL-PLANE.md` | `e80a7d84` | **SUPERSEDED** | fixava `§108`; `e2073197` corrige para `§<PRÓXIMO LIVRE>` porque outra missão levou o `§108` |
| `KNOW-HOW-DELTA-107-RECUPERACAO.md` | `8745f0f1` | **SUPERSEDED** | o `§111` canónico é `C-RESTORE-PROOF-BEFORE-LIVE-V2`, a missão sucessora, e cita o `SAME_CLASS_RESTORE = NO` da V1 que produziu este delta. As leis `107.1` e `107.3` aparecem lá, absorvidas |
| `KNOW-HOW-DELTA-O-FERRO-NEGOCIADO.md` | `5aa7a77c` | **APPLIED AGORA** → `§138` | provas conferidas; ver §5 abaixo |
| `KNOW-HOW-DELTA-O-CAMPO-QUE-NAO-ATRAVESSA.md` | `52acf72d` | **APPLIED AGORA** → `§139` | dez leis medidas nesta árvore |
| `KNOW-HOW-DELTA-MORADA-DA-SALA-DE-ESPERA.md` | `a28cade2` | **APPLIED EM PARTE** → `§140` | método entra; decisão `FILE_WAITING_ROOM_WINS` **não** entra |
| `KNOW-HOW-DELTA-ENDERECO-OFICIAL.md` | `72c8b864` | **NOT_APPLIED** | nenhuma das suas leis existe em variante nenhuma |
| `KNOW-HOW-DELTA-A-TRAVESSIA-OBSERVADA.md` | `973e7fdd` | **NOT_APPLIED** | idem |
| `KNOW-HOW-DELTA-AGRO-INTELLIGENCE.md` | `a1442f2b` | **NOT_APPLIED** | idem |
| `KNOW-HOW-DELTA-108-CONTROL-PLANE.md` | `e2073197` | **NOT_APPLIED** | idem |
| `KNOW-HOW-DELTA-A-BASE-DA-AUDITORIA.md` | `f199fb5c` | **NOT_APPLIED** | idem |
| `KNOW-HOW-DELTA-ARBITRAGEM-DA-INTELLIGENCE.md` | `fb2eda8f` | **NOT_APPLIED** | idem |

**Método da medição:** para cada delta, o título da lei e três a seis marcas
distintivas do corpo foram procurados nos **15 conteúdos** do censo. Zero
ocorrências ⇒ `NOT_APPLIED`. Ocorrência com número ⇒ `APPLIED`, com o `§` ao lado.
Caminhos de ficheiro partilhados **não** contam como aplicação: um delta e uma
secção podem falar do mesmo `.py` sem que a lei tenha entrado.

### 4.1 · Porque seis ficam por aplicar, e isso não é abandono

Aplicar um delta é escrever lei nova, e a lei do `§141.4` diz que se aplica
**um de cada vez, com prova, e testando entre cada um**. Esta missão aplicou os
três que o enunciado nomeou (`§11` e `§12` do briefing) e parou. Os restantes
seis ficam em `handoff/` das suas linhas, revistos e classificados, para o dono
do know-how integrar em série.

```
DELTAS_BLOCKED, por nome:
  KNOW-HOW-DELTA-ENDERECO-OFICIAL.md            72c8b864
  KNOW-HOW-DELTA-A-TRAVESSIA-OBSERVADA.md       973e7fdd
  KNOW-HOW-DELTA-AGRO-INTELLIGENCE.md           a1442f2b
  KNOW-HOW-DELTA-108-CONTROL-PLANE.md           e2073197
  KNOW-HOW-DELTA-A-BASE-DA-AUDITORIA.md         f199fb5c
  KNOW-HOW-DELTA-ARBITRAGEM-DA-INTELLIGENCE.md  fb2eda8f
MOTIVO: fora do escopo nomeado desta missao. Nao ha prova contra eles.
```

Nenhum deles existe em `handoff/` **desta** branch — vivem nas branches que os
produziram. Por isso a guarda os não vê, e por isso ficam nomeados aqui.

---

## 5 · OS DOIS CONFLITOS REAIS, E COMO FORAM DECIDIDOS

### 5.1 · `§61` — qual das duas é a lei de hoje?

```
A diz  «A FONTE ATRAVESSA — e tres mutantes» (13 linhas)
B diz  «A ORDEM DO PROJETO FICA COLLECTION -> COLETA GRANDE -> INTELLIGENCE -> CASCO»
```

Não é um conflito de conteúdo: são **dois conhecimentos diferentes** que
partilharam um número. Ambos são verdade. `A` fica onde está (`§61`); `B` entra
como `§121`.

```
CURRENT_TRUTH = AMBOS.  O conflito era de ENDERECO, e nao de facto.
```

### 5.2 · A morada da Sala de Espera — ficheiro ou tabela?

```
a28cade2 diz   FILE_WAITING_ROOM_WINS         (delta, nunca integrado)
§110 canonico  tabela public.sala_de_espera, migration 031
```

Este **é** um conflito de facto. Resolvido por prova, e não por data:

- o `§110` é da missão `C-SALA-PERSISTENTE-E-PREFLIGHT-REAL-V1`, **posterior**;
- ele **nomeia** a `ADR-SALA-DE-ESPERA-V1` e diz o que ela decidiu bem (o meio) e
  o que ela nunca respondeu (a sobrevivência depois do runner acabar);
- traz medição própria: 67 casos e 30 ataques contra PostgreSQL 16 descartável.

```
CURRENT_TRUTH = TABELA.   FILE_WAITING_ROOM_WINS = SUPERSEDED.
```

O `§140` entra **amputado**: leva o método daquela missão, e diz na primeira
linha que a decisão dela já não é lei.

```
UNRESOLVED_CONFLICTS = 0
UNKNOWN              = 0
```

Há um `UNKNOWN` **dentro** de `§138`, e ele é do assunto, não da reconciliação:
`GPU_QUALITY_BENCHMARK = BLOCKED_MISSING_MEDIA`, e portanto
`WINNER = UNKNOWN` entre CPU e GPU. Fica escrito como desconhecido, que é o que é.

---

## 6 · RED TEAM — VINTE ATAQUES

| # | ataque | veredito |
|---|---|---|
| 1 | duas secções com o mesmo número | **morto** — `SEM_DUPLICADOS` e medição direta: 0 |
| 2 | mesmo conteúdo com número diferente | **morto** — 0 hashes de corpo repetidos em 86 secções |
| 3 | dois conteúdos diferentes com o mesmo número | **morto** — era a doença; 17 reendereçados |
| 4 | secção mais nova mas falsa | **morto** — `FILE_WAITING_ROOM_WINS` recusada apesar de vir de delta |
| 5 | secção antiga ainda correta | **morto** — `§61`/ORDEM restaurada como `§121`, com o registo de decisão a prová-la |
| 6 | delta já aplicado | **morto** — `40c164fe`, `799ba94b`, `840a0d2a` identificados e não re-aplicados |
| 7 | delta parcialmente aplicado | **morto** — `840a0d2a` aterrou na linha Intelligence; entrou por `§127`–`§129`, não duas vezes |
| 8 | branch histórica com conteúdo obsoleto | **morto** — `a4c3ad88` é subconjunto estrito do prefácio canónico; nada importado |
| 9 | branch nova com conhecimento não provado | **morto** — as 17 têm secção `PROVA` ou medição citada |
| 10 | título igual com corpo diferente | **morto** — 5 pares, todos o separador `---`; nenhum é conhecimento |
| 11 | corpo igual com título diferente | **morto** — 0 encontrados |
| 12 | conflito sem prova | **morto** — 2 conflitos, 2 com prova; 0 `UNKNOWN` de reconciliação |
| 13 | referência local não publicada | **morto** — a única `refs/heads` aponta para o mesmo blob da remota |
| 14 | ficheiro `KNOW-HOW-V2` concorrente | **morto** — `UM_SO_FICHEIRO` na guarda, com autoteste que o injecta |
| 15 | novo `§` calculado olhando só a branch atual | **morto** — `§120` medido em `intelligence-pilot-v1`, não na canónica; `NEXT_SAFE = §121` |
| 16 | outra sessão move o HEAD durante a missão | **morto** — re-medido antes do commit; ver `§8` |
| 17 | push não-fast-forward | **morto** — branch nova, sem `--force` |
| 18 | conhecimento importante perdido por dedupe | **morto** — as 17 conferidas uma a uma na candidata final |
| 19 | conteúdo histórico promovido a lei atual | **morto** — `§140` amputada; `a4c3ad88` só aqui |
| 20 | relatório tratado como fonte canónica | **morto** — o aviso no topo deste ficheiro, e a guarda exclui-o da leitura de deltas |

```
RED_TEAM_SURVIVORS = 0
```

Os ataques 1, 2, 3, 4, 10, 11, 18 correm sozinhos e reprovam se voltarem a ser
verdade — 8 medições automáticas sobre a candidata, todas a zero.

---

## 7 · A PROTEÇÃO — `provas/o_know_how_tem_um_dono.py`

Sete perguntas, sem rede e sem banco:

```
1 · UM_SO_FICHEIRO    nenhum segundo know-how concorrente na arvore
2 · SEM_DUPLICADOS    nenhum numero de seccao repetido
3 · SEMPRE_A_SUBIR    nenhuma numeracao regressiva
4 · SEM_BURACO        nenhum buraco nao declarado em NUMEROS_QUEIMADOS
5 · SUB_BATE          «## N.x» vive dentro do §N que o contem
6 · DELTA_NAO_ALOCA   nenhum delta pendente cita um § que ja e de outro dono
7 · DELTA_NAO_REPETE  nenhum delta ja aplicado continua a pedir integracao
```

`--autoteste` injeta um defeito de cada espécie numa cópia temporária e exige que
**exactamente** a pergunta certa acenda, mais um **controlo positivo** que exige
que uma árvore limpa não acenda nada.

```
KNOW_HOW_GUARD   = PASS
AUTOTESTE        = PASS   (7 mutacoes + 1 controlo positivo)
```

### 7.1 · O que a guarda não consegue, dito antes de alguém descobrir

```
NAO impede que uma missao edite o ficheiro numa branch dela.
   Git nao tem dono por ficheiro. Ela apanha o RESULTADO, nao o ACTO.
NAO decide qual de dois conhecimentos em conflito e o verdadeiro.
```

O autoteste apanhou **dois defeitos reais na primeira corrida**, e ambos foram
consertados no medidor: a guarda não lia `§<PRÓXIMO LIVRE>` (a forma que os
deltas usam) e portanto nunca apanhava um delta já aplicado; e a expectativa do
teste exigia que um duplicado acendesse só um alarme, quando um duplicado é, por
força, também uma numeração que não sobe.

```
UM FALSO POSITIVO CONSERTA-SE NO MEDIDOR, E NAO NA PROSA DO RELATORIO.
```

### 7.2 · `§120` fica queimado

```
NUMEROS_QUEIMADOS = {120}
motivo: foi «A COLLECTION MEDIU CERTO CONTRA A FOTOGRAFIA DELA» em
        claude/intelligence-pilot-v1, e esta agora no §137.
```

Um buraco na numeração é mais barato do que um endereço com dois passados.

---

## 8 · CONCORRÊNCIA

```
BASE_CANONICAL_HEAD                   5705ac7bc704cc9c5b8925259a0a6a47f6eecc47
REMOTE_CANONICAL_HEAD (antes do push) ver secao final da entrega
CANONICAL_REMOTE_MOVED_DURING_MISSION ver secao final da entrega
```

Se a linha canónica tiver mexido, a regra é reconciliar contra o novo HEAD ou
parar. **Não há `--force` nesta missão**, e a branch de trabalho é nova.

---

## 9 · TESTE DE COMPLETUDE

```
CANONICAL_KNOW_HOW_FILES   1
DUPLICATE_SECTION_NUMBERS  0
UNCLASSIFIED_VARIANTS      0
UNREVIEWED_DELTAS          0
UNRESOLVED_CONFLICTS       0
KNOW_HOW_GUARD             PASS
RED_TEAM_SURVIVORS         0
SECCOES NA CANDIDATA       86   (§55 .. §141, mais o prefacio §0-§54)
SECCOES ESTAVEIS MEXIDAS   0
LINHAS APAGADAS DO FICHEIRO 2   (as duas do cabecalho de data)
```

---

## 10 · O QUE ESTA MISSÃO **NÃO** FEZ

```
NAO integrou a candidata no dono canonico. Isso e decisao separada.
NAO apagou nenhuma branch divergente.
NAO tocou Collection, GPU, Sala, Intelligence, Portal nem LIVE.
NAO mexeu na Biblia nem no contrato de design.
NAO aplicou os seis deltas fora do escopo nomeado.
NAO renumerou nada de §0 a §119.
```

```
BIBLE_CHANGE     = NENHUMA
CONTRACT_CHANGE  = NENHUMA
KNOW_HOW_DELTA   = NENHUM   (esta missao E o dono, e escreveu no ficheiro)
```
