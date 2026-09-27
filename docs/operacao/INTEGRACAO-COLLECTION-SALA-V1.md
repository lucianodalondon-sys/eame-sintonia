# A CANDIDATA UNIFICADA COLLECTION + SALA — V1

> ⚠️ **NÃO É CANÔNICA AINDA.**
> **OS DOIS WORKFLOWS DE SUPABASE FORAM RETIRADOS PELO RED TEAM.** Eles estavam
> **aposentados de propósito** desde `a29ac0a9`, e a candidata tem um teste que
> o exige. Integrá-los foi um erro meu. Ver §5.4.
> O `scrap-social.yml` **já estava** na candidata, e numa versão mais nova que
> a da `main`.
> **SYSTEM MAP AINDA NÃO RECONCILIADO** — isso é a Fase 5.
> **OPEN_RED_TEAM_FINDING:** 6 READY fora da Sala canônica. Ver §6 e §7.

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

---

## 5 · ESTEIRAS OPERACIONAIS — medidas, e duas **não** entraram

### 5.1 · `scrap-social.yml` — já cá estava, e mais nova

A Fase 4A dizia que a candidata não o tinha. **Estava errado** — a medição veio
de um laço com `git rev-parse "<ref>:<path>"` que falha em silêncio. Com
`git ls-tree`, que é autoritativo:

| linha | blob | último toque |
|---|---|---|
| `origin/main` | `9cdaaa24` | `df165da9` · **08/09** |
| **candidata** | `6c33bc21` | `73cf4b72` · **14/09 14:54** |

A da candidata está **269 linhas à frente**: acrescenta as fases
`youtube-oficial`, `cutover`, `hardware` e `gpu-asr`, e a entrada `runner`.
Trazer a da `main` seria **regredir seis dias**.

```
SOURCE_BRANCH  (já presente) claude/big-collection-gate-01 → candidata
SOURCE_COMMIT  73cf4b72
TRIGGER        workflow_dispatch apenas — sem `push`, sem `schedule`
SECRETS        SUPABASE_DB_URL · YOUTUBE_DATA_API_KEY
ESCRITA EM SUPABASE  nenhuma (0 ocorrências de insert/storage)
GUARDAS        `if:` por fase (hardware · gpu-asr · sessao)
PRODUCTION_WRITE_RISK = LOW
```

### 5.2 · ⛔ `supabase-raw-roundtrip.yml` e `supabase-fichas-adama.yml` — **NÃO integrados**

Os dois estão ausentes da candidata, e os dois foram medidos. **A integração
foi recusada por risco de escrita em produção.**

```
                        raw-roundtrip          fichas-adama
fonte                   origin/main 3e9934e7   origin/main 4a5d2d2d
trigger                 workflow_dispatch      workflow_dispatch
                        + push: [o próprio]    + push: [o próprio]
runs-on                 ubuntu-latest          ubuntu-latest
secrets                 SUPABASE_URL · SUPABASE_SECRET_KEY · SUPABASE_DB_URL
environment:            NENHUM                 NENHUM
if: (guarda)            NENHUM                 NENHUM
SAME_PROJECT_CONFIRMED  NÃO                    NÃO
dry-run / descartável   NÃO                    NÃO
escreve                 insert collection_run  insert collection_run
                        insert raw_asset       insert raw_asset
                        POST storage/object/raw update collection_run set

PRODUCTION_WRITE_RISK = HIGH   nos dois
```

**Duas razões, e a segunda é decisiva:**

1. **Não há guarda nenhuma.** Nem `environment:`, nem `if:`, nem confirmação de
   projeto, nem modo descartável. Eles escrevem no que quer que os três
   `secrets` apontem. E a comparação condena: o `supabase-storage.yml`, que
   apenas **cria um balde**, tem a pré-verificação `SAME_PROJECT_CONFIRMED`;
   os dois que **escrevem dados** não têm nenhuma.

2. **Integrá-los seria executá-los.** O gatilho é
   `push: { paths: ['.github/workflows/<o próprio ficheiro>'] }`. Acrescentar o
   ficheiro à candidata e empurrar a branch **dispara o workflow** — que grava
   em `collection_run`, em `raw_asset` e no bucket `raw`. Esta missão proíbe
   executar workflows contra serviços reais, e o acto de os integrar seria
   exactamente isso.

> **UM FICHEIRO QUE CORRE AO SER GUARDADO NÃO SE INTEGRA EM SILÊNCIO.**

**As dependências locais existem** — não é isso que bloqueia:

| workflow | dependência | na candidata |
|---|---|---|
| fichas-adama | `mapa_regfi` | ✅ `coleta/mapa_regfi.py` |
| fichas-adama | `_gavetas` | ✅ raiz |
| raw-roundtrip | `data/samples/raw-paid/` | ✅ 11 ficheiros |

E a versão certa do `fichas-adama` é a da `main`: difere da de
`italy-forward-only-scheduling-v1` por **uma linha** — o import passou de
`sys.path.insert(0,'scripts')` para `sys.path.insert(0,'.'); import _gavetas`,
por causa da reorganização de `b8321b07` (*"149 scripts saem de uma pasta só"*).
A da `main` é a compatível com esta árvore.

**O que falta para eles poderem entrar** — decisão sua, não minha:

- retirar o gatilho `push` (deixar só `workflow_dispatch`), **ou**
- acrescentar a pré-verificação `SAME_PROJECT_CONFIRMED` que o
  `supabase-storage.yml` já tem, **ou**
- declarar explicitamente que os `secrets` apontam para um projeto descartável.

Qualquer uma delas é uma alteração ao workflow, e nenhuma cabia nesta missão.

---

## 6 · OPEN_RED_TEAM_FINDING

```
READY_OUTSIDE_CANONICAL_SALA = 6
onde  data/derivados/A-COLLECTION-PRESERVA-O-FATO.json  /READY[0..5]
```

Herdado da BASE `e73cc8ff` — provado ao correr o mesmo censo contra a base pura
num clone descartável. Entrou em `317a384d`. **Não foi corrigido nesta missão**,
por ordem expressa: fica para a auditoria final da Fase 4.

O 14º teste do censo continua vermelho por causa dele, e deve continuar.

---

## 5.3 · OS DOIS WORKFLOWS DE SUPABASE — ENDURECIDOS E INTEGRADOS

> A §5.2 fica como registo do estado em que eles foram encontrados. Esta secção
> descreve o que entrou.

### O que estava errado, e continua verdade sobre a forma histórica

```
                        raw-roundtrip          fichas-adama
fonte                   origin/main b6a77ee5   origin/main b8321b07
blob                    3e9934e7               4a5d2d2d
trigger ORIGINAL        workflow_dispatch      workflow_dispatch
                        + push: [o próprio]    + push: [o próprio]
guarda ORIGINAL         NENHUMA                NENHUMA
PRODUCTION_WRITE_RISK   HIGH                   HIGH
```

> **UM FICHEIRO QUE CORRE AO SER GUARDADO NÃO É UMA ESTEIRA: É UM GATILHO.**

### O que mudou

**1 · O `push` saiu.** Sobra `workflow_dispatch` e mais nada — sem `schedule`,
sem `pull_request`, sem `repository_dispatch`. Medido: `push=0` nos dois.

**2 · Duas portas antes da primeira escrita**, e são diferentes de propósito:

| porta | o que exige | falha |
|---|---|---|
| `0a · portão humano` | o input `confirmar` tem de vir com `ESCREVER_NO_SUPABASE_CONFIRMADO`. O default é `NAO`. | `exit 1` |
| `0b · portão do alvo` | `SAME_PROJECT_CONFIRMED` — o mecanismo lido de `supabase-storage.yml`, sem alterar a lógica | `exit 1` / `SystemExit(1)` |

O input usa `type: choice` com `options:`, que é o padrão real desta casa —
`scrap-social.yml`, `apify-sensores.yml` e `comunicacao-publica.yml` já o usam.
**Nenhuma convenção foi inventada.**

### ⚠️ O QUE O PORTÃO DO ALVO **NÃO** PROVA

`SAME_PROJECT_CONFIRMED` extrai o ref do projeto do `SUPABASE_URL`
(`<ref>.supabase.co`) e do `SUPABASE_DB_URL` (`db.<ref>.supabase.` ou o
utilizador `postgres.<ref>`) e recusa se forem diferentes.

Isso apanha **a incoerência** — Storage num projeto e banco noutro. **Não prova
que o projeto seja descartável.** Se os dois segredos apontarem para produção,
eles concordam, e a porta abre.

> **COERÊNCIA DO ALVO ≠ ALVO SEGURO.**

É por isso que a primeira porta é humana, e por isso as duas **somam** em vez de
se substituírem: quem correr isto está a declarar que sabe para onde aponta.
Esta limitação fica escrita no cabeçalho dos dois ficheiros, não só aqui.

### Validação estática — 2/2 PASS

| workflow | trigger | 1ª escrita | último portão | portão antes? | fail-closed | verdict |
|---|---|---:|---:|:--:|:--:|:--:|
| `supabase-raw-roundtrip` | `workflow_dispatch` | linha 120 | linha 72 | **SIM** | **SIM** | **PASS** |
| `supabase-fichas-adama` | `workflow_dispatch` | linha 117 | linha 64 | **SIM** | **SIM** | **PASS** |

**Sem caminho alternativo:** cada ficheiro tem **um** job (`roundtrip`,
`fichas`) e **quatro** passos, nesta ordem — `checkout` → `0a` → `0b` →
escrita. Não há segundo job nem passo de escrita fora do caminho guardado.

**Dependências completas:** `coleta/mapa_regfi.py` · `_gavetas.py` ·
`data/samples/raw-paid/` (11 ficheiros rastreados).

```
EXTERNAL_ACTIONS_EXECUTED = NÃO
```

Nada foi disparado: nem GitHub Actions, nem Supabase, nem Storage, nem
migration, nem Vercel, nem Apify, nem coleta. A validação foi toda local e
estática.

---

## 5.4 · ⛔ O RED TEAM DERRUBOU A §5.3 — E TINHA RAZÃO

> As §5.2 e §5.3 ficam como registo do que eu pensei e do que fiz. **Esta
> secção diz o que estava errado.**

Eu integrei `supabase-raw-roundtrip.yml` e `supabase-fichas-adama.yml`,
endurecidos com duas portas. O red team correu a suíte inteira e apanhou:

```
tests/test_porta_de_producao.py
  class NenhumEscritorAntigoSobrou
    test_os_caminhos_antigos_nao_existem   FAILED na candidata · OK na BASE
```

**Aqueles dois ficheiros não estavam «em falta». Estavam APOSENTADOS**, no
commit `a29ac0a9` (11/09) — *"C-CLOSE-PHASE-10-BLOCKERS: o runtime aprende a
lei, e a trava sai do Python"* — que apagou os três de uma vez:

```
.github/workflows/supabase-fichas-adama.yml    -99
.github/workflows/supabase-raw-roundtrip.yml   -88
guarda/trava_do_escritor_antigo.sh             -71
```

E a casa **já tinha recusado exactamente a minha solução**. A docstring da
classe diz, por escrito:

> *"A VERSÃO ANTERIOR DESTE TESTE COBRAVA O OPOSTO: que cada caminho antigo
> CHAMASSE `trava_do_escritor_antigo.sh` antes de escrever. Era o teste certo
> para o estado errado — ele consagrava que os caminhos antigos continuavam lá,
> atrás de um guarda.*
>
> **UM CAMINHO BLOQUEADO AINDA É UM CAMINHO. E UM GUARDA É UMA COISA QUE ALGUÉM
> PODE TIRAR.**
>
> *Agora a invariante é mais forte e não precisa de guarda nenhum: eles não
> existem. E a razão não é de calendário — `adama-website` é uma ORGANIZAÇÃO,
> não um código de fonte do atlas, e sem `SOURCE_ID` real não há estado forward
> possível para aquelas linhas. Nunca houve."*

Eu pus um guarda onde a casa tinha decidido **apagar o caminho**. A minha
§5.3 argumentava que faltava «tirar o gatilho ou pôr o `SAME_PROJECT_CONFIRMED`»
— e a resposta certa era a terceira, que eu não considerei: **eles não voltam.**

### O que foi feito

Os dois ficheiros foram **removidos** nesta branch. Nada se perdeu: continuam
em `origin/main`, e a razão da aposentadoria está no `a29ac0a9`.

```
tests/test_porta_de_producao   BASE: FAILED (1)   fix: FAILED (1)   ← igual
  test_os_caminhos_antigos_nao_existem   antes: FAILED   depois: OK
```

A falha que resta em `test_porta_de_producao` é a herdada
(`test_o_inventario_de_quem_fala_de_raw_asset_esta_fechado`), idêntica na BASE.

> **O RED TEAM NÃO SERVE PARA CONFIRMAR O QUE EU FIZ. SERVE PARA O PARTIR.**

---

## 7 · PERÍCIA DOS 6 READY — CAUSA RAIZ PROVADA

### O que os 6 são

**Três documentos, cada um duplicado exactamente.** Medido por `sha256` do
objecto serializado:

| índice | sha | `ITEM_ID` | `SOURCE_ID` |
|---|---|---|---|
| `[0]` e `[3]` | `6b659d72447c` | `CAMPANIA:SA:02-09-2026` | `IT-T3-002` |
| `[1]` e `[4]` | `79b50ea2726b` | `APOL:2026:N9:BR-COLLINA` | `IT-T3-010` |
| `[2]` e `[5]` | `1f43bab6bff4` | `ARIF:SETTIMANALE:2026:N36` | `IT-T3-008` |

Nos seis: `RAW_OBSERVATION_ID = "NAO SEI"`, `ESTAGIO = DOCUMENTO`,
`FATO = NAO_SE_APLICA`, `CORRIDA = REPROCESSAMENTO-LOCAL`.

### Por que são seis e não três

O livro do coletor tem **175 observações** e só **35 `RAW_SHA256` distintos** —
porque re-observar uma fonte e confirmar que o documento não mudou **é um facto
que se regista**, e está certo:

```
DOCUMENT_ID=ARPAV:Z01:20260903160930  VERSION=v1_f88c89d73d6  RESULT=BASELINE_DOCUMENT
DOCUMENT_ID=ARPAV:Z01:20260903160930  VERSION=v1_f88c89d73d6  RESULT=SEEN_AGAIN
DOCUMENT_ID=ARPAV:Z01:20260903160930  VERSION=v1_f88c89d73d6  RESULT=SEEN_AGAIN
```

`provas/a_collection_preserva_o_fato.py::correr()` itera sobre **observações** e
faz `prontos.append(pronto)` uma vez por observação admitida. Dos 30 recibos,
**6 foram admitidos (SIM) e 24 ficaram `NAO_SEI`** — e os 6 são
**3 `DOCUMENT_ID` × 2 observações**.

> **A PROVA CONTA OBSERVAÇÕES COMO SE FOSSEM DOCUMENTOS.**

### As respostas

```
SIX_READY_HAVE_CANONICAL_COUNTERPART = 0
     a Sala canónica (`data/samples/PRONTO-PARA-INTELIGENCIA`) NÃO EXISTE
     nesta árvore. Não há contrapartida porque não há Sala.
SIX_READY_ARE_IDENTICAL_COPIES       = SIM  (3 pares byte-a-byte)
SIX_READY_ARE_SEMANTIC_DUPLICATES    = SIM
SIX_READY_CONTAIN_UNIQUE_INFORMATION = NÃO  (3 documentos, 6 objectos)
SIX_READY_ARE_READ_BY_RUNTIME        = NÃO
SIX_READY_FILE_ROLE                  = PROOF
```

**WRITERS:** `provas/a_collection_preserva_o_fato.py` — e mais ninguém.
**READERS:** o próprio ficheiro de prova (para saber onde escrever) e este
documento. **RUNTIME_READERS: nenhum.** **TEST_READERS: nenhum.**

O próprio artefacto declara o que é:

```
SO_LEITURA   "YES — nada foi colhido, nenhuma observacao nova foi criada"
GENERATED_BY "provas/a_collection_preserva_o_fato.py"
PORTA_DA_SALA.ESCRITA_PROVADA  "NO"
```

### ROOT_CAUSE = **F · OUTRO_PROVADO**

Nenhuma das cinco etiquetas serve sozinha:

- **não é** `ARTEFATO_DE_PROVA_FORA_DO_ESCOPO_DO_CENSO` sozinho — os objectos
  têm mesmo a forma do contrato e o `ESTADO` do READY; a varredura está certa;
- **não é** `WRITER_GRAVA_NO_LUGAR_ERRADO` — a prova escreve no artefacto dela;
- **não é** `CENSO_VARRE_ESCOPO_ERRADO` — o censo encontra o que existe.

**É isto:** a prova emite um READY por **observação**, e `SEEN_AGAIN` é uma
re-observação legítima do **mesmo** documento. O censo vê seis objectos porque
seis existem — e diz a verdade.

### ⛔ POR QUE NÃO FOI CORRIGIDO

O portão §5A exige `FIX_DOES_NOT_REQUIRE_ARCHITECTURAL_CHOICE = SIM`. **É NÃO.**

A identidade canónica de um READY é `RAW_OBSERVATION_ID` (`COL-LAW-043`), e nos
seis ela é **`NAO SEI`**. Deduplicar por `DOCUMENT_ID` seria **substituir a
identidade canónica por outra** — exactamente o que esta casa proíbe:

> **UM FALLBACK QUE INVENTA IDENTIDADE NÃO É UM CONSERTO: É UMA IDENTIDADE NOVA.**

```
ROOT_CAUSE_PROVEN                      = SIM
FIX_SCOPE_IS_LOCAL                     = SIM
NO_DATA_LOSS_PROVEN                    = SIM
NO_UNIQUE_FACT_REMOVED                 = SIM
CANONICAL_SALA_REMAINS_COMPLETE        = NÃO SEI  (a Sala não existe aqui)
NO_EXTERNAL_ACTION_REQUIRED            = SIM
NO_SYSTEM_MAP_CHANGE_REQUIRED          = SIM
FIX_DOES_NOT_REQUIRE_ARCHITECTURAL_CHOICE = NÃO   ⛔

HUMAN_DECISION_REQUIRED_FOR_6_READY = SIM
```

### As três saídas, para decisão humana

| saída | o que implica |
|---|---|
| **A · a prova passa a contar documentos** | `prontos` passa a ser indexado por `DOCUMENT_ID`. Muda `ADMITIDOS: 6` → `3`. **Escolhe uma identidade que não é a canónica.** |
| **B · a Sala ganha morada e a prova compara** | `RAW_OBSERVATION_ID` deixa de ser `NAO SEI` e o problema desaparece na origem. **Exige `psql`/`fcntl`, que esta máquina não tem.** |
| **C · o censo distingue prova de Sala** | Precisa de um critério declarado — não de uma lista por nome de ficheiro, que §5B proíbe. |

Nenhuma cabe na regra «não escolher arquitectura sem o humano».

---

## 8 · A IDENTIDADE FECHADA — os 6 READY passam a 3

> Estratégia **B**, decidida pelo humano: resolver na camada de **identidade
> canônica**. Não por `DOCUMENT_ID`. Não escondendo no Censo. Não apagando.

### 8.1 · A lei, lida do dono

`BIBLIA-CANONICA-DA-COLETA.md`, secção *«`RAW_OBSERVATION_ID` — a linhagem
viaja, e viaja uma vez só»*:

> `RAW_OBSERVATION_ID = raw_asset.id`. Ausente: `NAO SEI`. **Nunca** derivado
> de `sha256`, URL, `storage_path`, filename ou `RUN_ID`.
>
> **TER RAW ≠ O READY CONSEGUIR PROVAR QUAL RAW É O SEU.**

`LAW_STATUS: CANONICAL`. E `raw_asset` (migration `001`) é **uma linha por
objecto guardado**: `id bigserial primary key`, `storage_path text not null
unique`.

### 8.2 · A matriz semântica

| entidade | identidade canônica |
|---|---|
| **DOCUMENTO** | `DOCUMENT_ID` — o nome do documento no mundo. **Não é identidade de observação.** |
| **OBSERVAÇÃO BRUTA** | `raw_asset.id`, via `RAW_OBSERVATION_ID` |
| **RE-OBSERVAÇÃO / `SEEN_AGAIN`** | **nenhuma própria** — não guarda objecto, não cria `raw_asset` |
| **READY** | herda `RAW_OBSERVATION_ID` do bruto de onde saiu |

**A resposta à pergunta A/B/C/D é `A`:** `BASELINE_DOCUMENT` e `SEEN_AGAIN` do
mesmo documento partilham o `RAW_OBSERVATION_ID`, porque **há um só
`raw_asset`**. E a coleta já o diz, sem interpretação:

```
BASELINE_DOCUMENT   RAW_OBJECT_CREATED=True    RAW_PATH=<caminho real>
SEEN_AGAIN          RAW_OBJECT_CREATED=False   RAW_PATH=None
```

**Medido nos 175 registos do livro, sem uma excepção:**

```
CREATED=True   com RAW_PATH   ->  35   (BASELINE_DOCUMENT 10 + NEW_DOCUMENT 25)
CREATED=False  sem RAW_PATH   -> 109   (SEEN_AGAIN, todas)
CREATED=None   sem RAW_PATH   ->  31   (DISCOVERY_FAILED 19 + TRANSPORT_OR_EMPTY 12)
```

E **35 objectos guardados = 35 impressões digitais distintas**. É essa
igualdade que autoriza dizer *um objecto guardado = um `raw_asset`*.

### 8.3 · Por que `NAO SEI` — e por que isso **não** era o defeito

`raw_asset.id` é `bigserial`: **quem o atribui é o Postgres**. O livro do
coletor é um ficheiro NDJSON com 26 campos, e **nenhum deles é o id** — tem
`RAW_PATH` e `RAW_SHA256`, e a lei proíbe expressamente derivar o id deles.

```
IDENTITY_CONTRACT_IMPLEMENTED   = SIM  (admissao.py:1007 lê item["raw_asset_id"])
IDENTITY_CONTRACT_PROVEN_IN_DB  = SIM  (migration 001 + prova PG032)
IDENTITY_CONTRACT_USED_BY_PROOF = SIM  (a prova nunca o escreve à mão)
```

> **O `NAO SEI` ERA A LEI A FUNCIONAR.**
> **O DEFEITO ERA EMITIR DOIS `NAO SEI` PARA O MESMO BRUTO.**

`WHY_PSQL_REQUIRED` — só o Postgres cria `raw_asset.id`. `PROOF_REQUIREMENT`:
seria preciso para o campo deixar de ser `NAO SEI`, **não** para fechar a
duplicação.
`WHY_FCNTL_REQUIRED` — o backend de ficheiro da Sala usa `fcntl`, que não
existe em Windows. `LEGACY_REQUIREMENT`, e igualmente desnecessário aqui.

**Nenhum dos dois foi preciso.** Zero escrita externa.

### 8.4 · O conserto

`provas/a_collection_preserva_o_fato.py::correr()` emitia um READY por
**observação**. Passa a emitir um por **bruto guardado**:

```python
guardou_bruto = o.get("RAW_OBJECT_CREATED") is True
if pronto is not None and guardou_bruto:
    prontos.append(pronto)
```

E o recibo passa a carregar `RAW_OBJECT_CREATED`, para a pergunta *«de que
bruto é este recibo?»* ter resposta auditável.

```
OBSERVACOES_NO_LIVRO  175 -> 175      RECIBOS  30 -> 30
ADMITIDOS               6 ->   3      READY     6 ->  3   (3 distintos)
recibos de re-observação preservados: 23
```

> **NÃO SE APAGA HISTÓRIA. DEIXA-SE DE CONTAR DUAS VEZES O MESMO BRUTO.**

`NEW_IDENTITY_CREATED = NÃO` — `RAW_OBJECT_CREATED` é campo que a coleta já
escrevia. Nenhum `document_identity`, `dedupe_id` ou equivalente nasceu.

### 8.5 · A prova morde — teste mutacional

`tests/test_a_linhagem_do_ready_e_do_raw_asset.py` (11 casos) reprova em
`2dde8fed` e passa aqui. Em cópia descartável fora dos worktrees:

| mutação | resultado |
|---|---|
| repor o defeito (um READY por observação) | **FAILED** (2) |
| deduplicar por `DOCUMENT_ID` (identidade paralela) | **FAILED** (2) |
| fabricar a linhagem a partir do `sha` | **FAILED** (2) |
| não propagar a linhagem ao recibo | **FAILED** (8) |
| controlo, sem mutação | **OK** |

O teste rejeita **também** as soluções erradas — não só a ausência de solução.

### 8.6 · O Censo, sem lhe mudar as regras

```
READY_OUTSIDE_CANONICAL_SALA   6 -> 3
RED_TEAM_SURVIVORS             1 -> 1
```

**A dupla contagem morreu; o sobrevivente fica** — e está certo assim. O
ataque nº 1 tem duas partes, e só uma foi fechada:

- *contado duas vezes* → **resolvido**;
- *segunda representação* → **continua**, porque os 3 objectos ainda têm a
  forma do READY e vivem fora da Sala canônica — que **não existe nesta
  árvore**.

Fechar a segunda metade exige um critério declarado que distinga *prova* de
*Sala*, e isso é decisão de arquitectura — não cabe aqui, e §5B proíbe
resolvê-la por lista de nomes de ficheiro.
