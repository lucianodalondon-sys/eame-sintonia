# C-PG-032 — HANDOFF · A MISSÃO PARA AQUI, E NADA FICA SÓ NA CABEÇA DE QUEM SAIU

    ESCRITO EM   2026-09-14
    ESTADO       PAUSADA POR DECISÃO DO DONO — não bloqueada, não falhada
    CONTINUA EM  outra aba

Este ficheiro existe porque **memória de sessão não é durabilidade**. O que não
estiver escrito aqui deixa de existir no minuto em que a aba fechar.

    UMA COISA PROVADA E NÃO ESCRITA VOLTA A SER UMA COISA POR PROVAR.

---

## 1 · ONDE ESTÁ O TRABALHO

    WORKTREE     C:/pg032
    BRANCH       claude/pg032-ready19-prova
    HEAD         5f1598d40e1cca1c334b8ca65d0975f41ce2e2d7
    REMOTO       origin/claude/pg032-ready19-prova @ 5f1598d4   (igual · nada por empurrar)
    ÁRVORE       limpa

⚠️ **O trabalho NÃO está na branch da base.** A base é
`claude/collection-preserve-facts-2139eb` @ `4708f772`, que pertence a **outra
sessão viva**, com worktree próprio em
`C:/eame-sintonia/.claude/worktrees/collection-preserve-facts-2139eb`.

Esta branch nasceu ao lado dela, do mesmo commit, porque escrever no worktree de
outra sessão é atropelá-la. **Juntar as duas é decisão humana** — não é dívida
técnica, é uma escolha que ninguém tomou ainda.

### Os seis commits desta missão

    ebcda54f  a 032 dizia as duas coisas, e a prova media o contrato de ontem
    7a055e1e  o Postgres real recusou a minha suposicao: nome do contrato != nome da coluna
    93ac0282  a morada livre nao se adivinha: (run_id, ordem) ja estava ocupada
    34eba04c  a prova montava a ambiguidade por uma porta que a COL-LAW-034 fechou
    802c55d1  DB_TESTED = YES, e agora ha corrida para o sustentar
    5f1598d4  mapa: regerado sobre a arvore com a prova da 032

---

## 2 · O QUE FICOU PROVADO — COM A PROVA, NÃO COM A AFIRMAÇÃO

    MIGRATION_032                          = PASS
    READY_19_POSTGRES                      = PROVEN
    WAITING_ROOM_DURABILITY_WITH_19_FIELDS = PROVEN

    ONDE     GitHub Actions · workflow `banco-descartavel`
    CORRIDAS 34901780026  (prova) · 34902464048  (confirmação após carimbar)
    PASSO    `2b5`  → success nas duas
    NÚMERO   CASOS = 91 · PASS = 91 · FAIL = 0
    BANCO    postgres:16, service container, DESCARTÁVEL — nunca LIVE

    LIVE_TOUCHED = NO
    NEW_FAILURES = 0     (regressão local: 3786 testes · 139 vermelhos antes · 138 depois)

O banco foi aplicado pela **cadeia canónica** (`motor/cadeia_canonica.sh
migrations`), `001…032` em banco limpo, na ordem real — **não** por `psql -f 032`
solto. A diferença importa: um ficheiro que corre sozinho prova o ficheiro, não
prova a cadeia.

### As três leis que o Postgres real ensinou

1. **Nome no contrato ≠ nome da coluna.** `ESTADO` não é coluna nenhuma — é a
   *condição de entrada*, validada em `pousar()`. `CORRIDA` é a coluna `run_id`.
   Os dois estão declarados como excepção com o motivo escrito, em
   `provas/a_sala_sobrevive_ao_processo.py :: NAO_SAO_COLUNA`.

2. **Um estado escrito duas vezes deixou de medir.** A 032 abria com
   `NÃO EXECUTADA` e afirmava três linhas abaixo que tinha sido medida contra
   PostgreSQL descartável. Agora há uma linha só, e ela aponta para a corrida.

3. **Uma prova que monta o cenário por uma porta que fechou deixa de medir o que
   guardava.** O bloco `RUN-AMBIGUO` construía ambiguidade com itens sem `id` —
   caminho que a `COL-LAW-034` fechou. Foi reescrito para a ambiguidade nascer de
   forma legítima (dois itens que a *fonte* nomeou igual) e ganhou um caso próprio
   para a lei nova. **Nada foi afrouxado para ficar verde.**

### O 19 deixou de ser um número escrito à mão

`provas/a_sala_sobrevive_ao_processo.py` dizia `12`, copiado do contrato. Uma
cópia de um contrato é uma fotografia dele, e fotografia não envelhece junto.
Agora compara-se com o dono:

    sorted(pronta) == sorted(espera.CAMPOS_READY)

e o 19 sai como **consequência**, nunca como segunda lista.

---

## 3 · O QUE CONTINUA VERMELHO — E POR QUE NÃO FOI TOCADO

Três coisas. **Nenhuma nasceu nesta missão**, e as três estão medidas contra o
commit base para o provar.

### 3.1 · `banco-descartavel`, passo `2b6` — `No module named 'yaml'`

    PASSO      2b6 · o egresso mede-se ANTES de adquirir
    CAUSA      falta a dependência `yaml` no runner
    IDADE      falha há dias, antes desta missão
    DECISÃO    o brief §8 PROÍBE corrigir: «Isso é um bloqueio real e separado.
               NÃO corrigir nesta missão.»

É por isto que o job `banco-descartavel` continua a aparecer **vermelho** mesmo
com o `2b5` verde. Ler o job pelo cabeçalho engana; ler pelo passo, não.

    JOB VERMELHO != O MEU PASSO VERMELHO.

### 3.2 · `SECURITY CHECK` — `NEW_TABLE_WITHOUT_RLS`

    CORRIDA NESTA BRANCH   34904585004  @ 5f1598d4  → failure
    CORRIDA NA BASE        34897504602  @ 4708f772  → failure, MESMA causa
    MARCADOR               public.sala_de_espera
    FICHEIRO               supabase/migrations/031_a_sala_de_espera_ganha_dono_duravel.sql
    PORQUÊ                 tabela criada sem declaração de RLS na migration

Medido: esta missão **não tocou** na 031 nem em `security/`. A regressão entra com
o commit `caaf6311` da linha base, que criou a tabela.

⚠️ **Isto é um item aberto de verdade, e não meu para fechar.** A Sala de Espera
existe sem RLS declarado. Quem continuar decide entre declarar a política ou
`python3 security/ratchet.py --freeze` — e a segunda opção **é uma decisão
registada**, não um silenciamento: o ratchet guarda quem a moveu.

### 3.3 · Carimbo da árvore — `IMPRESSAO_DO_CARIMBO = DIFERENTE`

    FICHEIROS EM QUE disco != índice : 1
    data/samples/SOCIAL-IT/raw-free/LINKEDIN/
        identidade-https---imagelinenetwork.com__9e40b34272e2139f.txt

Defeito conhecido de Windows: `impressao_da_arvore.do_disco()` usa
`git hash-object`, que aplica filtros, e devolve um SHA que o git nunca guarda
para um ficheiro com bytes NUL depois dos 8 KiB.

**A correcção já existe** — preferir o SHA do índice para ficheiros limpos e
rastreados — mas vive noutra branch, `claude/local-gpu-on-current-collection-v1`.
Portá-la para cá seria trabalho de outra linha, feito de lado. Não foi portada.

O `validate_system_map.py` passa (`SYSTEM_MAP_CHECK = PASS`); o que não bate é o
carimbo, que é outra medição.

### 3.4 · Uma corrida ainda a decorrer quando isto foi escrito

    system-map  34904585013  @ 5f1598d4  → in_progress

Não esperei por ela. Quem continuar deve lê-la antes de assumir verde.

---

## 4 · O QUE A PRÓXIMA ABA **NÃO** DEVE FAZER

Estas não são precauções genéricas — são os limites que o dono escreveu, e que
continuam de pé depois da pausa.

    NÃO aplicar a 032 em LIVE. NÃO usar produção como laboratório.
    NÃO instalar PostgreSQL nesta máquina.
    NÃO consertar o `yaml` do 2b6 dentro desta missão.
    NÃO alterar o workflow do CI aqui.
    NÃO instalar dependências de conveniência para o vermelho passar.
    NÃO redesenhar o contrato READY, nem acrescentar campos.
    NÃO tocar em Inteligência.
    NÃO iniciar Big Collection nem fontes novas.
    NÃO mergear, cherry-pick, force-push ou reescrever histórico desta branch.

⚠️ E o mais fácil de esquecer: **a 032 já não se edita a partir do dia em que for a
produção.** O livro-razão da cadeia canónica guarda o hash do ficheiro. Mudar uma
vírgula parte a cadeia. Isso está escrito dentro da própria migration.

---

## 5 · MISSÕES VIZINHAS QUE ESTA PAUSA NÃO RESOLVE

Para quem abrir a aba seguinte e precisar do mapa à volta:

- **C4H-SYNTH · a ponte de média.** Worktree `C:/eame-gpu-current`, branch
  `claude/local-gpu-on-current-collection-v1` @ `06bd0efe`, limpa e empurrada.
  Lá vivem `coleta/executor_transcricao_midia.py`, a negociação de `compute_type`
  em `ferramentas/fala_local.py`, e a correcção do carimbo da árvore descrita em
  §3.3. **Continuam a existir duas implementações concorrentes da ponte** — a
  arbitragem C4H-ARB não foi fechada por decreto.

- **A aba paralela de YouTube.** `YOUTUBE_TOUCHED = NO` em toda esta missão, e
  assim deve continuar até alguém decidir o contrário. Worktrees
  `youtube-acquisition-authorized-7e2e67` e `youtube-italia-caption-audio-8b460b`.

---

## 6 · COMO RETOMAR, EM TRÊS PASSOS

    1. git -C C:/pg032 fetch origin && git -C C:/pg032 status
       → confirmar que 5f1598d4 continua a ser o HEAD dos dois lados.
       Se não for, alguém mexeu — LER antes de escrever.

    2. gh run list --branch claude/pg032-ready19-prova --limit 10
       → ler o `2b5`, não o cabeçalho do job. Ver §3.1.

    3. Decidir, com o dono, UMA de três:
       a) juntar esta branch à linha da Colecção   (decisão humana, §1)
       b) atacar o RLS da Sala de Espera           (item aberto real, §3.2)
       c) atacar o `yaml` do 2b6                   (bloqueio separado, §3.1)

    NÃO RETOMAR POR «CONTINUAR DE ONDE PAROU». Parou de propósito.
