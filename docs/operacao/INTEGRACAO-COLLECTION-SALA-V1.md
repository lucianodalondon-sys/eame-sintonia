# A CANDIDATA UNIFICADA COLLECTION + SALA — V1

> ⚠️ **NÃO É CANÔNICA AINDA.**
> **WORKFLOWS OPERACIONAIS AINDA NÃO INTEGRADOS.**
> **SYSTEM MAP AINDA NÃO RECONCILIADO** — isso é a Fase 5.

**Branch:** `claude/collection-sala-unified-v1`
**Base original:** `e73cc8ff0669e6c060432e15b02c313793e5a48f` (`claude/big-collection-gate-01`)

---

## 1 · O QUE JÁ ESTÁ DENTRO

| # | commit | o que traz | fonte |
|---|---|---|---|
| 1 | `9a00e6c6` | **C4H unificada** — a ponte de mídia | BIG + `local-gpu` @ `06bd0efe` |
| 2 | `a7843e41` | **PG032** — migration com estado correto + provas Postgres | `claude/pg032-ready19-prova` @ `7e7c3bab` |
| 3 | `cfc1ed1e` | **Sala** — fronteira da coleta, prova da Sala canônica, delta de know-how | `claude/sala-truth-01` @ `14ca4537` |

O detalhe da C4H está em [`INTEGRACAO-C4H-SEMANTICA-V1.md`](INTEGRACAO-C4H-SEMANTICA-V1.md).

### PG032 — `a7843e41`

Commits fonte: `ebcda54f` · `7a055e1e` · `93ac0282` · `34eba04c` · `802c55d1`

Dois ficheiros, e **um deles não mudou onde importa**:

```
MIGRATION_032_COUNT                     = 1
MIGRATION_032_EXECUTABLE_SQL            = 40 linhas · sha256 dc7ca0905ce5a3c0
MIGRATION_032_EXECUTABLE_SQL_UNCHANGED  = SIM  (igual à BASE, medido de novo)
MIGRATION_EXECUTED                      = NÃO
```

O que muda é o cabeçalho de estado. A versão da BASE dizia `NÃO EXECUTADA` e,
três linhas abaixo, que *"foi aplicada e medida contra PostgreSQL DESCARTÁVEL"*
— duas afirmações que não podem ser verdade juntas. Agora diz
`DESIGNED=YES · DB_TESTED=YES · LIVE=NO`, com a corrida que sustenta:
PostgreSQL 16 descartável, `CASOS=91 PASS=91 FAIL=0`.

**EXCLUDED_FROM_PG032:** `5f1598d4` (System Map gerado) · `7e7c3bab` (handoff
histórico, preservado na branch de origem).

### Sala — `cfc1ed1e`

Commits fonte: `6ac09de1` · `14ca4537`

Seis ficheiros, **todos código humano**:

```
provas/a_fronteira_da_coleta.py                 +239
tests/test_fronteira_mede_a_sala_canonica.py    +341  (novo)
tests/test_fronteira_mede_producao.py            +44
system-map/scripts/censo_cards_sensores.py       +42
system-map/scripts/generate_system_map.py        +19
handoff/KNOW-HOW-DELTA-O-BACKEND-APOSENTADO.md  +163  (novo)
```

⚠️ `generate_system_map.py` é **código** e entra; os `*.generated.json` são
**saída** e ficam fora. A lei que produz o mapa não é o mapa que ela produziu.

**EXCLUDED_FROM_SALA:** nenhum ficheiro gerado veio nos commits fonte — não
houve nada a curar. A candidata não tinha tocado em nenhum dos seis desde a
separação em `611e7cbf`, logo foi avanço puro.

---

## 2 · O CENSO DA SALA — ENTROU, DEPOIS DE DUAS ADAPTAÇÕES DECLARADAS

> Esta secção substitui o bloqueio registado na primeira versão deste
> documento. O bloqueio era real; a decisão de o resolver foi autorizada, e a
> regra foi sempre a mesma: **ajustar a sonda, não regredir a casa.**

### 2.1 · A sonda de T7

```
OLD_T7_PROBE  "Ensaio de campo publicado com DOI"
NEW_T7_PROBE  "Boletim tecnico da cooperativa para os socios,
               assinado pelo agronomo de campo"
```

**Dono da taxonomia:** o **Atlas**, e ele fala por dois sítios que concordam —
`leis/territorios.py` (`TERRITORIOS`) e a tabela da linha 51 de
`docs/fontes/ATLAS-DE-FONTES-EAME.md`:

| | |
|---|---|
| **T7** | TECHNICAL NETWORK — agrônomos, advisors, crop specialists, consultores, extensão, institutos técnicos, **cooperativas**, associações |
| **T5** | SCIENCE — papers, estudos, trials, institutos, universidades |

A sonda antiga passava porque `T7` carregava o léxico de CIÊNCIA — por
`pedido/pedido.py` dizer que `T7` era «Ciência e ensaio». Era a quarta cópia da
taxonomia, e estava errada.

**Medido, e não suposto:**

| frase | T7 | T5 | outros |
|---|:--:|:--:|:--:|
| nova (cooperativa/sócios/agrônomo) | **SIM** | não | **nenhum** |
| antiga (ensaio/DOI) | **NÃO** | **SIM** | nenhum |

A nova cai em T7 **e em mais nenhum território** — não é ambígua, e não foi
moldada para o teste: é o que uma fonte T7 realmente publica.

> **A SONDA NÃO SE ESCOLHE PARA PASSAR: ESCOLHE-SE PARA PERTENCER.**

### 2.2 · O molde do teste era de ontem

Com a sonda corrigida, 12 dos 13 problemas desapareceram. Sobrou um, e a causa
era da mesma família: **o contrato READY passou de 11 para 19 campos** —
`RAW_OBSERVATION_ID`, `ESTAGIO`, `FACT_TIME_BASIS`, `FACT_LOCATION_BASIS`,
`PUBLISHED_AT`, `OBSERVED_AT`, `SOURCE_DECLARED_EVIDENCE_CLASS`, `FATO` — no
commit `13feb273` da própria BIG, *"contrato READY de 19 campos"*.

O fixture `unidade()` do teste escrevia as **onze** chaves à mão. O censo
mediu-a e contou-a como **LEGADO** — que é exactamente o que ela era.

> **O CENSO NÃO ESTAVA ERRADO: O MOLDE DO TESTE É QUE ERA DE ONTEM.**

E a lista escrita à mão era a mesma falta que `_campos_do_contrato()` se recusa
a cometer. A forma passa a sair de `self.campos`, que vem do construtor do
dono; os campos que o teste não nomeia ficam `NAO SEI` — nunca vazio, nunca
zero. **Nenhuma asserção foi enfraquecida:** os valores que cada teste verifica
continuam os mesmos.

### 2.3 · ⚠️ O QUE O CENSO ENCONTROU, E QUE NÃO SE APAGA

O 14º teste **continua vermelho**, e deve continuar:

```
RED_TEAM   15 ataques · 1 sobrevivente
ataque 1 · «mesmo item em duas representacoes contado duas vezes»  SOBREVIVEU
           varridos 465 ficheiros: 6 objectos READY fora da sala canonica
BIG_COLLECTION_CAN_START = UNKNOWN
```

Os 6 estão todos em `data/derivados/A-COLLECTION-PRESERVA-O-FATO.json`,
`/READY[0]` a `/READY[5]`.

**A condição é herdada, e está provada:** corri o censo — com a sonda já
corrigida — contra a BASE `e73cc8ff` **pura**, num clone descartável fora dos
worktrees. Deu **exactamente o mesmo**: 6 fora da sala, 1 sobrevivente,
`UNKNOWN`, saída 1. O ficheiro entrou em `317a384d` (14/09 17:30), da própria
BIG, muito antes desta integração.

```
FAIL_NEW       = 0   nada regrediu por causa desta integração
FAIL_INHERITED = 1   uma verdade pré-existente que passou a ser visível
```

A saída do censo é `0 if RED_TEAM_SURVIVORS == 0 else 1`. O teste
`test_duas_corridas_dao_o_MESMO_relatorio_byte_a_byte` afirma `returncode == 0`
e por isso reprova. **Não mexi nessa asserção.** Torná-la verde seria apagar o
único sinal de que há READY em duas representações — e o censo existe
precisamente para o dar.

O relatório commitado (`data/derivados/O-CENSO-DA-SALA-DE-ESPERA.json`) é o que
mede **esta** árvore, não o que veio de `b67e6f07`.

---

## 2-bis · REGISTO HISTÓRICO — o bloqueio original

Fonte: `origin/claude/censo-sala-espera-big-collection-x0ut2y` @ `b67e6f07`
(commits `9ffd829e` · `b67e6f07`).

Trouxe os 4 ficheiros legítimos, deixei de fora os 8 carimbos obsoletos — e os
testes reprovaram: **12 erros + 1 falha**.

Não é defeito da integração. É um **conflito semântico real**:

| | árvore do censo (13/09) | candidata (14/09) |
|---|---|---|
| a sonda envia `"Ensaio de campo publicado com DOI"` a `T7` | **SIM** — *"fala de doi, ensaio — que é do que T7 trata"* | **NÃO** — *"fala claramente de outro universo (T5: doi, ensaio)"* |
| teste `test_o_censo_da_sala_de_espera` | **14 OK** | **12 erros + 1 falha** |

**A candidata é que está certa.** O `admissao/admissao.py` da candidata
(+541 linhas face à árvore do censo) corrigiu uma taxonomia errada, e
escreveu porquê:

> *"`T7` carregava o léxico de CIÊNCIA — porque `pedido/pedido.py` dizia que
> `T7` era «Ciência e ensaio». No Atlas, que é o dono, `T7` é TECHNICAL NETWORK
> e o léxico de ciência é de `T5`."*
>
> **UMA CHAVE DE DICIONÁRIO TAMBÉM É UMA DECLARAÇÃO DE TAXONOMIA.**

A sonda do censo copiou o exemplo antigo — que a própria `admissao.py` da
candidata ainda tem, esquecido, no seu bloco `__main__` (linha 1070).

E o censo recusa-se a medir em vez de fingir, por desenho:

> *"Cair para uma lista escrita à mão seria transformar «a porta mudou» em «o
> censo mediu na mesma». SEM O CONSTRUTOR NÃO HÁ CONTRATO PARA MEDIR CONTRA.
> **Ajustar a sonda, e não o censo.**"*

**A correção é de uma linha** — trocar o texto da sonda por vocabulário de T7
(`cooperativa`, `agrónomo`, `assistência técnica`, `sócios`). Mas isso decide
**o que o censo passa a medir**, e é decisão declarada, não silenciosa. Por
isso parei aqui.

**EXCLUDED_FROM_CENSO:** tudo, nesta missão. E, mesmo quando entrar, ficam de
fora os **8 carimbos** `<!--M:TEST_COUNT_CURRENT-->3.874→3.888` — a candidata
já está em **3.952**, e importá-los seria regredir o contador.

---

## 3 · TESTES

| suíte | resultado | |
|---|---|---|
| `test_c4h_ponte_de_midia` | **OK** | C4H não regrediu |
| `test_c4h_executor_de_midia` | **OK** (29) | idem |
| `test_c4g_a_especie_do_video` | **OK** | idem |
| `test_forward_instrumentado` | **OK** | ingresso/derivação |
| `test_fronteira_mede_a_sala_canonica` | **OK** | Sala |
| `test_fronteira_mede_producao` | **OK** | Sala |
| `test_proveniencia` | FAILED (5) | **herdado** — as mesmas 5 por nome na BASE |

```
TESTS_FAIL_NEW = 0
C4H_STILL_GREEN = SIM
```

### NOT_RUN_EXTERNAL

| o quê | porquê |
|---|---|
| `provas/a_sala_sobrevive_ao_processo.py` | exige `BANCO_DESCARTAVEL_URL`. Declara-se `NOT_RUN` e escreve que **NOT_RUN não é PASS**. Não foi corrida contra banco nenhum. |
| migration `032` | **não executada**. |

### FAIL_INHERITED de ambiente

`provas/a_fronteira_da_coleta.py` recusa-se a correr nesta máquina: o `grep` do
Windows não aceita `{0,4}` sem `-E`. Falha de forma **idêntica** na fonte
`sala-truth-01` e na BASE `e73cc8ff`, e o ficheiro é byte a byte igual ao da
fonte (`764b0d05`). E recusa em vez de imprimir zero — *"um censo que não mediu
não pode imprimir zero"*.

---

## 4 · O QUE FALTA

1. **Censo da Sala** — bloqueado no conflito de taxonomia acima.
2. **Workflows operacionais** — `scrap-social.yml`, `supabase-raw-roundtrip.yml`,
   `supabase-fichas-adama.yml`. Próxima missão.
3. **System Map** — deliberadamente não reconciliado. Fase 5.
