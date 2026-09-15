# C4H · PARAGEM POR CONCORRÊNCIA — e três premissas do briefing corrigidas

> **Esta missão parou antes da primeira linha de código, e parou pela regra que
> o próprio briefing escreveu no `§1`:**
>
> *«Se arquivo compartilhado tiver mudança concorrente: HARD STOP.»*
>
> Tem. E não é uma colisão de ficheiro — é uma colisão de **conceito**: outra
> aba já entregou, commitada, a metade de montante da tarefa do `§5`.

```
YOUTUBE_TOUCHED            = NO
MEDIA_COLLECTION_PIPELINE  = NOT_EXERCISED   (nunca PASS, nunca FAIL)
FULL_MEDIA_TO_WAITING_ROOM = NOT_PROVEN
HARD_STOP_REASON           = CONCURRENT_CHANGE_ON_SHARED_FILES (§1)
PAID_USD = 0 · APIFY_RUNS = 0 · NEW_VIDEO_ACQUISITION = NO
```

---

# A · GIT

| campo | valor |
|---|---|
| `BRANCH` | `claude/youtube-italia-caption-audio-8b460b` |
| `START_HEAD` | `b57f3df657d01b4779a0e67ff4483116668197e4` |
| `FINAL_HEAD` | o commit que traz este documento |
| `REMOTE_HEAD` | **não existe** — esta branch nunca foi publicada |
| `WORKTREE_CLEAN` | sim, no arranque |

---

# B · A COLISÃO, MEDIDA

A base desta missão (`origin/claude/local-gpu-on-current-collection-v1`) **andou
para a frente** entre a C4G e agora:

```
611e7cbf  (a minha base)
      └── 867a6f97  «a especie do video era apagada a entrada,
                     e o MP4 ia para o extrator de PDF»
```

Ficheiros que esse commit toca:

| ficheiro | é meu terreno? |
|---|---|
| **`coleta/ingresso.py`** | **SIM** — é a porta do `§5` |
| **`leis/artefato.py`** | **SIM** — é a lei de `CONTENT_TYPE` do `§5` |
| `tests/test_c4g_a_especie_do_video.py` | sim — é o teste nº 4 do `§12` |
| `docs/sintonia-scrap/C4G-O-CANO-INTERNO-DO-VIDEO.md` | entrega deles |
| 4 × `*.generated.json` | mapa |

### E o que eles escreveram é, literalmente, a lei que o `§15` me mandava registar

Do diff em `leis/artefato.py`:

```
DECLARADO PELO OBSERVADOR  >  DEDUZIDO DO NOME  >  NAO SEI.
```

O `§15` deste briefing pede: *«Registrar conhecimento durável confirmado,
especialmente se ainda não estiver: CONTENT_TYPE declarado pelo observador >
dedução pelo nome > UNKNOWN»*. **Já está.** Foi escrito por outra aba, no dono
certo, com a medição ao lado (um `.mp4` real de 9,2 MB cuja ficha saía
`NAO SEI`).

```
DUAS ABAS A ESCREVER A MESMA LEI NÃO PRODUZEM UMA LEI FORTE.
PRODUZEM DUAS LEIS, E A PARTIR DAÍ NENHUMA VALE.
```

Este repositório já paga essa conta: o know-how canônico existe em **16
documentos distintos**, e o `§118` está ocupado por quatro títulos diferentes.

### E há um terceiro trabalho vivo, na mesma pasta

```
C:/eame-sintonia   ->  branch claude/italy-forward-only-scheduling-v1
                       40 ficheiros sujos na árvore
```

Três frentes ao mesmo tempo. Não arbitrei nenhuma, como o `§14` manda.

### O número C4G já está ocupado duas vezes

```
docs/sintonia-scrap/C4G-O-CANO-INTERNO-DO-VIDEO.md       (deles, publicado)
docs/sintonia-scrap/C4G-A-LEGENDA-E-O-AUDIO-NAO-ABREM.md (meu, local)
```

**Reportado, não arbitrado.** Este documento tomou `C4H`, que foi medido livre
em todas as branches remotas.

---

# C · TRÊS PREMISSAS DO BRIEFING, CORRIGIDAS

## C1 · «Se houver gap entre DERIVED e SALA» — não há. A estrada existe.

O `§8` foi escrito a contar com um buraco. Medido, ele fechou-se antes desta
missão:

```
coleta/rota_forward_documento.py   (a «M2»)
    DERIVED -> STRUCTURED -> ADMISSION -> READY -> SALA
```

Ela chama `espera.pousar()` na linha 381, distingue `PASSED` de `REUSED`,
escreve `NOT_RUN` quando a porta diz não — e não `FAIL` — e escolhe código de
diagnóstico por tipo de falha. **Está completa, e com telemetria por etapa.**

⚠️ **E o cabeçalho dela mente sobre ela própria.** A docstring ainda diz
*«A M2 termina em ADMISSION, e terminar em ADMISSION e a verdade»*, e
`coleta/derivacao_forward.py` ainda diz *«não há dono forward ligado a
`derived_artifact` a jusante»*. As duas frases eram verdade quando foram
escritas e hoje são falsas.

```
LI O CÓDIGO E NÃO O COMENTÁRIO, E A RESPOSTA INVERTEU-SE.
UM COMENTÁRIO DESACTUALIZADO CUSTA A MISSÃO SEGUINTE INTEIRA — ele estava a
fazer o `§8` planear arquitectura para uma estrada que já estava construída.
```

**Consequência para quem continuar:** o `§8` não precisa de nova arquitectura.
Precisa de **ligar o executor de mídia à M2**, e mais nada.

## C2 · «Usar o Postgres descartável» — ele não existe nesta máquina, e o SQLite não serve

```
psql · pg_ctl · initdb   ->  ausentes
docker                   ->  ausente
psycopg2 · psycopg       ->  ausentes
```

Existe `guarda/memoria_descartavel.py`, e eu esperei que servisse. **Não serve,
e a outra aba tinha razão.** Ele é SQLite, e o próprio ficheiro declara
`NÃO É Postgres. E não finge ser` — traduz só as tabelas que a garantia de
escrita toca. A M2 pede `public.etapa_da_corrida` e `public.conteudo`, que não
estão lá.

Medido a correr a bateria da M2 nesta máquina:

```
Ran 26 tests  ·  OK (skipped=23)
motivo: «sem PostgreSQL descartavel: BANCO_DESCARTAVEL_URL nao definida»
```

O próprio ficheiro de teste escreve, na linha 459: **`SKIP != PASS`**. Um
`OK` com 23 de 26 saltados é exactamente o verde que mente.

**A única rota real é o CI:** `.github/workflows/banco-descartavel.yml`,
`ubuntu-latest`, `postgres:16`, com `workflow_dispatch`. Correr lá exige
publicar a branch — e publicar a branch é o que o `§1` bloqueia.

## C3 · «O vídeo Bayer já preservado» — existe, e não é onde o briefing sugere

```
C:/eame-sintonia/data/samples/INSTAGRAM-TRANSCRICOES/audio-cache/DcNkh7LCW4u.mp4
9 218 753 bytes · h264+aac · 29,7 s
```

Está **fora do Git** e **fora deste worktree** (a árvore desta missão tem
`0` ficheiros de mídia). É um reel do `bayer_italia`, chegou pelo Instagram, e
foi a outra aba que o localizou e o mediu.

⚠️ **Ele não é canário desta missão por um motivo que não é técnico:** quem o
está a usar, agora, é a outra aba. Dois donos sobre o mesmo canário produzem
duas linhagens para o mesmo `sha256`.

E existe um segundo conjunto, esse sim órfão, que **não** tem proveniência
nenhuma no repositório:

```
C:/eame-sintonia/.tmp/mp4/   4 ficheiros, 46 MB
  DclUKbGDaEM.mp4  2,05 MB   7,27 s
  DcqdwWGFK58.mp4  41,2 MB  109,8 s
  DcqdwWGFK58.wav / teste.wav
```

`grep` por esses dois IDs em toda a árvore: **zero ocorrências**. Nenhum código
escreve em `.tmp/mp4`. São bytes reais sem registo — e usá-los obrigaria a
inventar a identidade que o `§3` e o `§11` proíbem inventar.

---

# D · O QUE FALTA, DEPOIS DE TUDO ISTO

O censo do `§4` deu uma resposta limpa, e é a única boa notícia operacional:

```
coleta/executor_transcricao_midia.py   NÃO EXISTE em NENHUMA branch
ferramentas/fala_local.py              EXISTE — dono único de FALA -> TEXTO
coleta/rota_forward_documento.py       EXISTE — DERIVED -> ... -> SALA
leis/artefato.py + coleta/ingresso.py  JÁ CORRIGIDOS pela outra aba
```

**Falta exactamente uma peça**, e ela é pequena: a ponte que recebe
`audio/*` ou `video/*`, chama `fala_local`, e entrega o derivado ao dono
canônico — depois ligada à M2.

```
A MISSÃO C4H É MENOR DO QUE O BRIEFING DELA. E É POR ISSO QUE NÃO PODE
SER FEITA DUAS VEZES: A PEÇA QUE FALTA CABE NUMA MISSÃO SÓ, E TEM DE TER
UM DONO SÓ.
```

---

# E · ENTREGA

```
A. GIT                  START b57f3df6 · FINAL este commit · REMOTE não existe
B. ISOLAMENTO           YOUTUBE_TOUCHED = NO
                        nenhum ficheiro, workflow, branch, prova ou SOURCE_ID
                        de YouTube foi lido para alterar, nem alterado
C. EXECUTOR             NÃO CRIADO — `executor_transcricao_midia` continua sem
                        dono em todas as branches; quem transcreve é e continua
                        a ser `ferramentas/fala_local.py`
D. POSTGRES             NENHUM. Local não tem; SQLite não substitui; CI exige
                        publicar a branch, que o §1 bloqueia
E. PROVA E2E            RAW        NOT_PROVEN
                        DERIVED    NOT_PROVEN
                        STRUCTURED NOT_PROVEN
                        ADMISSION  NOT_PROVEN
                        READY      NOT_PROVEN
                        SALA       NOT_PROVEN
                        (todas por NOT_EXERCISED, nenhuma por falha medida)
F. RETRY                NOT_EXERCISED
G. RED TEAM             18 ataques · 0 exercitados · 0 sobreviventes
                        NOT_EXERCISED != PASS, e nenhum é reportado como morto
                        excepto o último: «qualquer arquivo YouTube é alterado»
                        -> MORTO, medido: git status limpo, zero ficheiros de
                        YouTube no diff desta missão
H. REGRESSÃO            nenhuma alteração de código; suíte não mexida
I. SYSTEM MAP           não regenerado por prova nova — não houve prova nova.
                        Drift concorrente reportado, não arbitrado (§14)
J. DESCONHECIDOS        · proveniência dos 4 ficheiros em `.tmp/mp4`
                        · se a outra aba vai ela própria criar o executor
                        · se a M2 corre de ponta a ponta no CI (nunca medido)
K. RISCO RESTANTE       duplicar trabalho commitado, e criar um segundo dono
                        de `CONTENT_TYPE` — o defeito que este repositório já
                        carrega em 16 cópias do know-how
L. KNOW_HOW_DELTA       NENHUM
                        (a lei que o §15 pedia já foi escrita pela outra aba,
                        em `leis/artefato.py`, no dono certo)
M. BIBLE_CHANGE_REQUIRED     NO
   CONTRACT_CHANGE_REQUIRED  NO
N. VEREDITO
   MEDIA_COLLECTION_PIPELINE  = NOT_EXERCISED
   FULL_MEDIA_TO_WAITING_ROOM = NOT_PROVEN
```

---

# F · O QUE DESBLOQUEIA, E É DECISÃO DE GENTE

A pergunta não é técnica. É de propriedade:

```
QUEM É O DONO DA PONTE DE MÍDIA — esta aba, ou a que já commitou a
correcção da espécie?
```

Decidido isso, o caminho é curto e já está medido:

```
1 · o dono escolhido cria `coleta/executor_transcricao_midia.py`
    sobre 867a6f97 (não sobre 611e7cbf)
2 · liga-o à M2, que já vai até à Sala
3 · publica a branch e corre `banco-descartavel.yml` (workflow_dispatch)
4 · a prova de fogo do §9 corre lá, contra postgres:16 de verdade
```

Nada disto precisa de arquitectura nova. Precisa de **um dono**.
