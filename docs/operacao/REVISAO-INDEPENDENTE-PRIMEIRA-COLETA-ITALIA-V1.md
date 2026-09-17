# REVISÃO INDEPENDENTE — PRIMEIRA COLETA CONTROLADA ITÁLIA V1

> **Este ficheiro é o dono canônico da revisão independente** da execução
> registada em `docs/operacao/PRIMEIRA-COLETA-CONTROLADA-ITALIA-V1.md` §10-C e
> em `system-map/data/primeira-coleta-controlada.observado.json`. A revisão foi
> feita por outro agente que **não** implementou nada do que aqui se audita, e
> **não corrigiu nada** durante a auditoria — os defeitos ficam nomeados para a
> missão seguinte.

```
MISSÃO                C-IT-INDEPENDENT-FIRST-COLLECTION-REVIEW-V1
MEDIDO EM             2026-09-17
HEAD AUDITADO         7d75e25a7a758cd4d9f62d71b40182a5a5cb944d
ESCOPO                9d6dcbbd..7d75e25a — 10 commits
WORKTREE              limpa antes e depois (0 ficheiros)

INDEPENDENT_FIRST_COLLECTION_REVIEW = FAIL
COLLECTION_INTEGRATION_CANDIDATE    = NO   (até fechar o BLOCKER-1)
SOURCE_TO_SALA_REAL_OBSERVED        = YES  — a alegação SOBREVIVEU à revisão
WORKFLOW_REPLAY                     = NÃO EXECUTADO (portão read-only = FAIL)
BIG_COLLECTION_AUTHORIZED           = NO
```

**A frase que resume:** a primeira coleta controlada **aconteceu e está bem
provada** — nenhum contraexemplo derrubou o observado. O que reprova a entrega
como candidata a trunk é **um defeito que ela mesma introduziu num teste de
segurança**: a isenção nova em `tests/test_porta_de_producao.py` opera sobre o
ficheiro inteiro quando promete operar sobre a linha, e com isso um escritor
novo de produção consegue se esconder. Prova da coleta ≠ candidatura da
entrega: a primeira fica de pé; a segunda espera o conserto.

---

## 1 · GIT

> ⚠️ **CORREÇÃO DE TOPOLOGIA — 2026-09-17.** A linha `REMOTE_TRUNK_HEAD real =
> c88690ca` da tabela abaixo está **ERRADA**: a revisão consultou
> `origin/claude/sintonia-eame-repo-setup-xccfob` (a branch que o ambiente
> rotula de «main») como se fosse o trunk. **Não é.** O trunk canônico é
> `claude/it-trunk-v1`, remedido diretamente no remoto em 2026-09-17:
>
> ```
> origin/claude/it-trunk-v1 = 9d6dcbbd08210b0c463b1cb25222edc4f8d45d9b
> MERGE_BASE                = 9d6dcbbd (o próprio trunk)
> COLLECTION                = 11 à frente · 0 atrás — fast-forward possível
> ```
>
> A frase «o trunk oficial andou 45 commits» descreve a branch errada e cai
> junto. O erro **não altera nada do resto**: o escopo auditado
> (`9d6dcbbd..7d75e25a`) já era o certo, porque `9d6dcbbd` era o trunk de
> verdade — a revisão acertou o intervalo pelo motivo errado. Blocker e prova
> SOURCE→SALA intactos. A tabela original fica abaixo, como foi escrita,
> porque apagar o erro apagaria a lição: **«main» de ambiente não é trunk de
> projeto; trunk se mede na branch nomeada pela coordenação.**

| medição | valor |
|---|---|
| `CURRENT_BRANCH` | `claude/it-collection-sala-v1` |
| `LOCAL_HEAD` = `REMOTE_COLLECTION_HEAD` | `7d75e25a` — nada por publicar |
| `REMOTE_TRUNK_HEAD` real | ~~`c88690ca`~~ — **ERRADO, ver a correção acima**: era outra branch |
| topologia | `9d6dcbbd` (o trunk esperado) **é ancestral** desta branch; ~~o trunk oficial andou 45 commits com missões alheias~~ (branch errada). Escopo auditado: os **10 commits** `9d6dcbbd..7d75e25a` — correto |
| `WORKTREE_DIRTY` | 0 · `LOCAL_UNPUBLISHED` | 0 |

## 2 · O DIFF INTEIRO, EXPLICADO

Os 10 commits: plano (`324878a0`), BG-04 na dona da Sala (`774e1e6d`), bancada
(`9941ef87`), BG-04 na casa toda (`f8447492`), BG-03/05/06 (`4b981316`), BG-01
workflow (`3c0b36bf`), 7º defeito stdin UTF-8 (`e087d985`), a execução
(`8cf2a272`), T3-008 em duas corridas (`5408b560`), peça do mapa (`7d75e25a`).
**Todos EXPECTED.** Verificado por diff que **não** entrou: mudança de
SOURCE_ID (Atlas intocado), SOURCE_OWNER, migration nova (`supabase/migrations`
intocada), Intelligence, Portal, deploy, LIVE, candidata promovida
(`candidatas/` intocada), contratos (`regras/` intocada), livro versionado
(`data/` sem um byte de diff — 175 observações antes e depois).

## 3 · A PROVA, RECONSTRUÍDA SEM O RESUMO

O `observado.json` tem 10 linhas: 6 corridas completas + a 2ª corrida de
T3-008 (com limites declarados) + 3 tentativas com erro preservadas. Contagem
fecha; `CORRIDAS_COM_ERRO_DO_MEDIDOR = 2` refere as duas RuntimeError (colunas
adivinhadas); a linha OSError 0x92 é o 7º defeito da estrada, documentado em
§7-C do plano — corrigido em `e087d985`, antes do canário que passou.

**Canário IT-T3-002 (`...234023`)** — cada elo pertence à mesma corrida:
rede real (observação no ledger com o RUN_ID, `HEALTHY`), egresso IT medido
pelo próprio coletor por corrida (`ipinfo.io` → `VPN_COUNTRY`, código nas
linhas 364/545 do coletor), RAW=1, STORAGE=1 (sha `d5aa781c…`), DERIVED=1,
STRUCTURED=1, ADMISSION `SIM`, SALA=1, **relida por outro processo** (a prova
sobe um `sys.executable -c` separado — processo real). `DOCUMENT_ID =
CAMPANIA:SA:09-09-2026` — nome nativo, não SHA. Só o storage_object é
partilhável entre corridas, **por desenho** (endereçamento por conteúdo).

**Identidades e reexecução (`...234309`):** RUN_1 ≠ RUN_2; observações
distintas (raw_asset 1 e 3); SHA igual porque bytes iguais; `DERIVED=0` com
`ETAPAS.DERIVED=PASS` é **REUSED legítimo** — `coleta/rota_forward_documento.py:164`
marca REOBSERVADO como balde `reused` com etapa PASS, e a contagem por run_id
dá zero porque o artefato pende da raw_asset da 1ª corrida. `VERDICT = COHERENT`.

**T3-008:** duas corridas, duas provas, **nenhuma prova emprestada**. A 1ª
(`...234422`): `ETAPAS.RAW=FAIL` com RAW=1 no banco não é contradição — 
`coleta/ingresso.py:1228` marca FAIL quando o erro de memória impede a
confirmação, mesmo com a linha persistida: falha conservadora. A 2ª
(`...234734`): campos que o corredor não mediu estão `NAO MEDIDO`, incluindo a
releitura por outro processo. Nenhum texto do projeto diz «a primeira corrida
recuperou».

**As seis:** `6/6 EXECUTADAS` nunca é vendido como `6/6 READY`. T4-001 →
`NOT_APPLICABLE` (CSV); T2-004 → `NOT_APPLICABLE` (HTML); T2-002 →
`NAO_SE_APLICA` ×4 (decisão registada `MEDICAO-DA-REGRA-T2.md`); T3-002 e
T3-010 → Sala; T3-008 → o histórico acima. Zero observações de IT-T3-005.

**Limite honesto da evidência primária:** os OPS_ROOT temporários e o banco
descartável foram destruídos como o desenho manda — o `observado.json` é a
consolidação e nada no repositório a contradiz, mas os RESULTADO.json
primários já não existem. É exatamente por isso que o replay pelo workflow
real continua **necessário** (e ficou por fazer — ver §7).

## 4 · SEMÂNTICA DE STATUS E ERROR

- `RUN_STATUS_MEANS = PROCESS_EXIT_STATUS` do executor
  (`orquestrador/orquestrador.py:875`). Pipeline mora em `etapa_da_corrida`.
  `SUCCESS_WITH_STAGE_FAIL_IS_VALID = YES` **pelo contrato escrito** — dívida
  já nomeada (CW-08 / G-RUN-02): confunde quem opera, não corrompe dado.
- `ERROR_FIELD_SEMANTICS = FAIL (defeito de observabilidade, não bloqueante)`
  — o campo guarda a **cauda do stderr** (`orquestrador.py:896`), e o próprio
  orquestrador imprime «ERRO (nao e rejeicao)». O texto «Could not find
  platform independent libraries» foi reproduzido nesta revisão num `py -c`
  qualquer desta máquina: é ruído ambiental do Python local, não erro da
  corrida. Dívida: renomear/filtrar antes da escala, porque cinco réguas leem
  o recibo.

## 5 · OS PORTÕES BG, RECONFERIDOS

| gate | reexecutado nesta revisão | resultado |
|---|---|---|
| BG-01 | `test_fase_italiana_no_workflow` **15/15** + leitura do YAML | ordem física provada: bancada 5a-IT (l.339) → Sala 5b (l.364) → egresso 5c (l.376) → aquisição 6 (l.381); só orquestrador é chamado (l.454; o coletor aparece uma vez, em comentário); teardown 9z-IT `always()` (l.649). ⚠️ `WORKFLOW_CODE_EXISTS=YES · TESTED=YES · EXECUTED=NO` — os 15 testes leem YAML; nenhum executa o workflow |
| BG-03 | `test_italia_na_porta_canonica` **22/22**; 19 deles executam Node real com path `C:` | ⚠️ o commit `4b981316` afirma prova «com espaço e acento» que **não existe versionada**. Esta revisão provou o mecanismo à parte: `pathToFileURL` + import em diretório `prova bg03 açênto\módulo têste.mjs` → OK. Falta o teste no repo |
| BG-04 | censo AST próprio, independente da guarda | 63 chamadas ativas: **57 certas, 6 erradas — todas em `provas/*.sh`**, que rodam em ubuntu (glibc permuta) ou não têm chamador. ⚠️ a guarda `test_psql_argv` só varre shell de `motor/` e `.github/workflows/` — «em toda a casa» é verdadeiro para Python e para o shell que roda no Windows, não para `provas/*.sh`. O único psql de workflow Windows (l.352) está certo |
| BG-05 | `test_o_pedido_nao_mente` **14/14** + leitura de `receitas.py`/`orquestrador.py` | T4+fonte vai ao italiano (promoção por consumo de filtros, sort estável); `FILTRO_NAO_CONSUMIDO` retorna **antes** do subprocess (l.791-810 vs l.861); T4 sem fonte continua no `regulatorio-eu`, declarado |
| BG-06 | `test_fontes_explicitas_no_coletor` **8/8** | coletor sem fonte → `FONTES_AUSENTES`; CLI sem `--fonte` → exit 2; workflow sem `fonte` → exit 2. ⚠️ duas notas: (a) pela rota do orquestrador, T2/T3 têm `filtros_por_omissao` com **fonte aprovada** (IT-T2-002, IT-T3-010) — default de UMA aprovada, declarado, não é a lista das sete; (b) `candidatas/italy_profiles.mjs` mantém IT-T3-005 no perfil-padrão do corredor **recorrente** (`italy_recurrent_collect.mjs`) — declarado como decisão de outra missão, fora da rota do piloto, mas é um caminho onde a candidata corre sem ninguém a nomear na chamada. Capacidade ≠ autorização: fica nomeado |

`NEW_FAILURES = 0` · `NEW_ERRORS = 0` — 89 testes dirigidos: 88 verdes; a única
falha (`test_alvo_estruturado` test_13, campo CONTENT_TYPE) é **pré-existente**
(o campo entrou em `3f18a01c`, ancestral do trunk esperado; o próprio commit
`4b981316` a declara). Os 10 commits **reduziram** vermelhos (BG-03 derrubava 24).

## 6 · PRODUÇÃO — OS DOIS ATAQUES

### 6a · Fallback silencioso: **NO no artefato commitado — com defesa de uma linha**

Cadeia auditada: `SUPABASE_DB_URL` está no env do **job** (workflow l.181) e a
fase italiana o herda. A ordem de resolução da Sala é
`SINTONIA_SALA_DSN` → `SUPABASE_DB_URL` (`admissao/sala_de_espera.py:741`).
**Porém**, no workflow commitado não existe caminho executável até a aquisição
sem a DSN descartável: o passo 5a-IT roda `set -eu`, sem pipes, **zero**
`continue-on-error` no ficheiro inteiro — qualquer falha antes do
`echo >> GITHUB_ENV` mata o job, e 5b/5c/6 não têm `always()`.

O que fica nomeado como dívida de blindagem (**antes da escala**):
1. o portão 5b (`exigir_canonica`, l.785-799 da Sala) **não distingue
   descartável de produção** — daria PASS a uma DSN Supabase;
2. a trava `_e_descartavel` tem furo por query string: 
   `...@localhost/descartavel?host=db.X.supabase.co` passa a trava e a libpq
   conecta no host do `?host=` — **provado com psql 16.4 real** contra hosts
   inalcançáveis (pré-existente, não introduzido pelos 10 commits);
3. `medidas/scanner_da_coleta.py:140` cai para `SUPABASE_DB_URL` se rodado à
   mão sem `BANCO_DESCARTAVEL_URL` (só SELECTs; sem chamador em workflow).

### 6b · A guarda da porta: **GUARD_WEAKENED = YES — o BLOCKER**

`tests/test_porta_de_producao.py` (entrou em `8cf2a272`): a isenção nova
promete ser «ESTREITA: só a MESMA linha», mas `sem_comentarios()` (l.52-53)
faz `" ".join(...)` — o ficheiro vira **UMA linha** antes de
`escreve_producao()` fazer `splitlines()`. Provado empiricamente nesta revisão,
com a lógica literal do teste:

```
sintonia-scrap.yml + passo malicioso
  `bash motor/cadeia_canonica.sh migrations "$SUPABASE_DB_URL"`
     → guarda nova: NÃO ACUSA        → regra antiga: ACUSAVA

ficheiro novo com escritor + isca benigna
  (`echo '...@localhost:54329/descartavel'` em qualquer outra linha)
     → guarda nova: NÃO ACUSA

controle sem isca                    → ACUSA (a guarda não morreu; furou)
```

Consequência: `sintonia-scrap.yml` está **permanentemente isento** do detector
de `cadeia_canonica.sh migrations/importacoes` (as strings benignas do 5a-IT
isentam o ficheiro inteiro), e **qualquer** workflow evade com uma isca. Só
`SUPABASE_SECRET_KEY` continua a acusar sempre. Uma isenção era necessária
(a alternativa — pôr o sintonia-scrap na lista `ESCRITORES` — era pior), mas a
implementada é mais permissiva do que o necessário: a granularidade de linha
física era alcançável.

**Conserto mínimo (para a próxima missão, não feito aqui):** aplicar a isenção
sobre as **linhas físicas** do YAML (filtrar comentários linha a linha, sem
join) — e um teste-contraexemplo com o escritor malicioso acima, que hoje
passaria e não pode passar.

## 7 · O REPLAY QUE NÃO ACONTECEU

O contrato da missão de revisão manda: portão read-only FAIL → **não corrigir,
não fazer o replay**. Pré-condições que já estavam prontas e ficam medidas para
a próxima missão: runners `SINTONIA-EAME-LOCAL` e `-LOCAL-2` **online** e
livres (API do GitHub, 2026-09-17); egresso desta máquina **IT** (Milão,
`205.147.30.28`); a fase `italia-documento` despachável contra
`claude/it-collection-sala-v1` com `fonte=IT-T3-002`. O replay canário continua
sendo **a prova que falta** do BG-01 em execução (hoje: código + testes de
YAML, `WORKFLOW_EXECUTED = NO`) e deve rodar na missão que fechar o BLOCKER-1
— registrado como `INDEPENDENT_WORKFLOW_CANARY_REPLAY`, sem reescrever a
história da primeira coleta.

## 8 · MIGRATIONS, LIVRO, RETRY/CRASH, DERIVADORES

- **Migrations:** `MIGRATION_FILES = 32` · `MIGRATIONS_EXPECTED = 31` — a 008
  é verificação e fica fora do aplicador **por desenho** (`cadeia_canonica.sh`
  l.107 `grep -v '/008_'`). «31/31» é aritmética honesta. Notas: o cabeçalho do
  script diz «aplica 001-007 e 009-018» (desatualizado); a 008 não tem corrida
  registada na bancada descartável — «objetos conferidos» do §130 vem das
  consultas da prova, não da 008. Num replay: contar `MIGRATION_NNN=PASS` na
  saída **e** `select count(*) from schema_migracao` = 31.
- **Livro-de-decisões (544 revertidas):** `BLOCKS_SCALE`. A Admissão escreve
  TODAS as decisões (COL-LAW-042) em `data/samples/LIVRO-DE-DECISOES.json`,
  caminho **fixo** (`admissao/admissao.py:79`) — `ITALY_OPS_ROOT` redireciona o
  coletor, não a Admissão. As 544 nunca entraram no git (reversão na worktree);
  apontavam para `derived:<id>` de um banco já destruído. A prova do piloto
  não depende delas (o por-corrida vive no observado); perdeu-se o grão
  item-a-item, cuja âncora já não referenciava nada. Antes da escala o destino
  tem de ser redirecionável/durável — P-011 já mede o problema.
- **Retry/Crash:** nenhum texto os chama de PASS — `NOT_OBSERVED` e
  `NOT_RUN_WITH_REASON` em todos os registros. `RETRY_BEFORE_SCALE_REQUIRED =
  YES` (COL-LAW-025 é CANONICAL com implementação `ABSENT` — escalar sem
  backoff/orçamento viola lei viva) · `CRASH_RECOVERY_BEFORE_SCALE_REQUIRED =
  YES` (dívida explícita «antes da Big Collection», plano §10-C).
- **Derivadores:** paradas declaradas em quatro camadas (plano §5, critério 8,
  §10-C, §130). A Bíblia **não** exige classe aprovada → READY (COL-LAW-035
  legitima `NOT_APPLICABLE`). `BLOCKS_PILOT = NO` ·
  `BLOCKS_BIG_FOR_ALL = NO` · `BLOCKS_BIG_FOR_CSV_HTML_T2 = YES`.

## 9 · SYSTEM MAP

```
REGERAR_EXIT = 0        (correr_a_cadeia.py REGERAR, exit capturado direto)
VALIDAR_EXIT = 0        (correr_a_cadeia.py VALIDAR, idem)
SYSTEM_MAP_CHECK = PASS · «o mapa corresponde ao repositorio»
```

A regeneração alterou 13 ficheiros **apenas em carimbo** (`GENERATED_AT` /
`HEAD_DA_MEDICAO` avançando para 7d75e25a — a convenção da casa); zero deriva
semântica; restaurados para manter a worktree fiel ao HEAD auditado. A peça
nova é a prova-corredor registada como componente em `architecture.declared.json`;
o estado do corredor deriva do `observado.json` commitado (artefato medido),
não de declaração de código.

## 10 · DISCREPÂNCIAS (nenhuma além do BLOCKER derruba a prova)

| # | onde | o que | gravidade |
|---|---|---|---|
| D1 | `tests/test_porta_de_producao.py` | isenção de ficheiro inteiro vendida como de linha; evasão por isca provada | **BLOCKER-1** |
| D2 | know-how, linha 13 (cabeçalho) | «4 unidades na Sala relidas por outro processo» — o observado mostra 4 na Sala e **3 relidas** (T3-008: NAO MEDIDO) | corrigida nesta revisão (§131) |
| D3 | commit `4b981316` | prova «com espaço e acento» afirmada e não versionada; mecanismo provado à parte nesta revisão | dívida de teste |
| D4 | commit `f8447492` («toda a casa») | 6 chamadas psql com DSN à frente restam em `provas/*.sh`, fora do perímetro da guarda | dívida |
| D5 | `motor/cadeia_canonica.sh` cabeçalho | comentário desatualizado (001-018) | cosmética |
| D6 | recibo do orquestrador | campo `ERROR` guarda stderr ambiental benigno | dívida de observabilidade |

## 11 · DÍVIDAS PARA ESCALA

| dívida | BLOCKS_INTEGRATION | BLOCKS_BIG_COLLECTION | porquê |
|---|:-:|:-:|---|
| **GUARDA DA PORTA (BLOCKER-1)** | **YES** | YES | teste de segurança mais permissivo do que o necessário; esconde escritor novo |
| PSQL_SPAWN_FLAKE | NO | YES | §130 já o nomeia «próximo candidato a investigação»; em escala o transiente vira taxa |
| TEARDOWN_PORT_RISK | NO | NO | `pg_ctl \|\| true` pode prender a 54329, mas a corrida seguinte **falha fechada** sem tocar produção; endurecer é recomendado, não bloqueante |
| ADMISSION_LEDGER_NOT_ENV_REDIRECTABLE | NO | YES | ou toda corrida polui o livro versionado, ou reverte-se à mão — e reverter em produção destrói a trilha da COL-LAW-042 |
| RETRY_NOT_OBSERVED | NO | YES | COL-LAW-025 CANONICAL · IT ABSENT |
| CRASH_RECOVERY_NOT_PROVEN | NO | YES | dívida explícita «antes da Big Collection» |
| CSV_DERIVATION | NO | YES (classe CSV) | preserva mas nunca produz READY |
| HTML_DERIVATION | NO | YES (classe HTML) | idem |
| T2_ADMISSION_RULE | NO | YES (classe T2) | `MEDICAO-DA-REGRA-T2`: regra não existe; 0/10 em publicador não visto |
| blindagem: 5b não distingue produção · `_e_descartavel` furo `?host=` · ERROR=stderr · IT-T3-005 no perfil-padrão do recorrente · teste espaço/acento · guarda psql em `provas/*.sh` | NO | antes da escala | defesa em profundidade e calibração de leitura |

## 12 · VEREDITO

```
INDEPENDENT_FIRST_COLLECTION_REVIEW = FAIL
BLOCKERS                            = 1 (guarda da porta de produção — §6b)
COLLECTION_INTEGRATION_CANDIDATE    = NO, até o conserto do BLOCKER-1
                                      por missão que não seja este revisor
SOURCE_TO_SALA_REAL_OBSERVED        = YES — sustentado; nenhum contraexemplo
                                      desta revisão o derrubou
FIRST_CONTROLLED_COLLECTION         = a prova fica DE PÉ; a candidatura espera
WORKFLOW_REPLAY                     = pendente, pré-condições medidas (§7)
BIG_COLLECTION_AUTHORIZED           = NO
NENHUMA CORREÇÃO FUNCIONAL          = feita por esta revisão
```

Caminho para a candidatura: (1) consertar a isenção da guarda com
granularidade de linha física + teste-contraexemplo; (2) rodar o
`INDEPENDENT_WORKFLOW_CANARY_REPLAY` (IT-T3-002, fase `italia-documento`) com
teardown medido fisicamente; (3) só então fast-forward na coordenação.

---

## 13 · ADENDO — O BLOCKER-1 FOI FECHADO (2026-09-17)

> Registrado aqui porque este ficheiro é o dono do blocker. O veredito acima
> é histórico e **não muda**: descreve o HEAD `7d75e25a`. O fecho veio em
> missão própria, commit **`7f7d31ef`** («collection: fechar a isencao da
> porta de producao por linha real»), que este revisor **não** revisou — a
> validação foi red team independente, em **4 rounds até zero**:
>
> | round | o que caiu |
> |---|---|
> | 1 | a 1ª versão do conserto: espaço dobrado furava o gatilho; `run: >` dobrava fora da vista; isca completa na mesma linha isentava o escritor |
> | 2 | a 2ª versão: cabeçalhos de fold `>2` e `> # comentário` não dobravam |
> | 3 | a 3ª versão: plain/quoted scalar multilinha dobra sem sinal nenhum |
> | 4 | **nada — RED_TEAM_GUARD_BLOCKERS = 0**, FP = 0 nos 17 workflows reais, isenção falsa não costurável |
>
> Cada furo dos 4 rounds ficou como regressão versionada (testes 13-17 da
> classe `AIsencaoDaBancadaEEstreitaDeVerdade`). Limite declarado que
> permanece: ofuscação de shell no token do script — fronteira de qualquer
> guarda estática por texto, idêntica à da guarda antiga; a blindagem de
> runtime (portão 5b distinguir produção; `_e_descartavel` e o `?host=`)
> segue como dívida nomeada da escala (§11).
>
> `INDEPENDENT_REVIEW_BLOCKER_1 = CLOSED` · o que falta para a candidatura
> agora é **só** o item (2): o replay canário pelo workflow real, por missão
> independente. `BIG_COLLECTION_AUTHORIZED = NO` continua.


---

## 14 · INDEPENDENT_WORKFLOW_CANARY_REPLAY — 2026-09-17

> Replay independente pelo **workflow real** (`sintonia-scrap.yml`, fase
> `italia-documento`, fonte `IT-T3-002`), por agente que **não** implementou
> nem consertou nada do que aqui se mede, e que **não corrigiu nada** durante
> o exame. Evidência primária: o run do GitHub, os logs dele, o recibo que a
> corrida escreveu no workspace do runner, e a medição física desta máquina
> durante e depois do run.

```
MISSÃO                 INDEPENDENT_WORKFLOW_CANARY_REPLAY · IT-T3-002 · italia-documento
MEDIDO EM              2026-09-17 (dispatch 11:25:00Z · fim 11:30:00Z)
HEAD AUDITADO          c93f6920c65649c6a5e65ce6a055411a81e6943c  = REMOTE_COLLECTION_HEAD antes e depois
TRUNK                  origin/claude/it-trunk-v1 = 9d6dcbbd · merge-base = o trunk · 13 à frente / 0 atrás
WORKTREE               limpa antes e depois (0 ficheiros) · LOCAL_UNPUBLISHED 0

GITHUB_WORKFLOW_RUN_ID 35215565657 · run_attempt 1 · event workflow_dispatch
GITHUB_RUN_URL         https://github.com/lucianodalondon-sys/eame-sintonia/actions/runs/35215565657
GITHUB_RUN_HEAD_SHA    c93f6920… — o auditado (checkout imprime o SHA no log)
RUNNER                 SINTONIA-EAME-LOCAL (input runner=1 · runner_id 21 · C:\actions-runner-eame)
                       antes do dispatch: os dois runners online e busy=false (API)
RUN_IDS_BEFORE         nenhum run deste workflow nesta branch; 5 runs antigos noutras branches
GITHUB_RUN_CONCLUSION  success

INDEPENDENT_WORKFLOW_CANARY_REPLAY = FAIL
WORKFLOW_EXECUTED                  = YES
WORKFLOW_FLOW_OBSERVED             = NO
SOURCE_TO_SALA_REAL_OBSERVED       = YES  (§130 — mantido; este replay não o repete nem o reverte)
COLLECTION_INTEGRATION_CANDIDATE   = NO
BLOCKER                            = a porta de linha de comando do orquestrador NÃO liga o banco:
                                     `orquestrador/orquestrador.py:1052` chama `correr()` sem
                                     `memoria=` e sem `banco_do_rastro=` (defaults None, l.758)
                                     → RAW nunca chega a `raw_asset` → DERIVED e STRUCTURED não
                                     correm → ADMISSION = NAO_SEI («sem texto nenhum») → SALA = 0
BIG_COLLECTION_AUTHORIZED          = NO
```

**A frase que resume:** o workflow **executou**, na ordem certa, com Postgres
descartável, 31 migrations, Sala gate e egresso IT **antes** da rede,
orquestrador chamado, fonte explícita, RUN cunhada pelo dono, PDF novo
adquirido pela rede e preservado em ficheiro, teardown físico limpo e produção
intocada. E a estrada **partiu-se no elo STORAGE**: o banco que o passo 5a-IT
construiu e o passo 5b aprovou nunca recebeu uma linha, porque a porta CLI do
orquestrador não sabe que ele existe. A primeira coleta (§130) passou por
**outra porta** — o corredor `provas/primeira_coleta_controlada_italia.py:134`
chamava `orq.correr(p, memoria=MemoriaPostgres(URL), banco_do_rastro=Banco(URL))`
em processo. `WORKFLOW_CODE_EXISTS = YES · TESTED = YES · EXECUTED = YES ·
FLOW_OBSERVED = NO`.

### 14.1 · A ordem, provada por hora de início (API `jobs`, não o YAML)

| # | passo | início → fim (UTC) | conclusão | prova no log |
|---|---|---|---|---|
| 2 | checkout | 11:25:19 → 11:26:12 | success | `checkout -B claude/it-collection-sala-v1 …` · imprime `c93f6920…` |
| 3 | 0 · o ref tem os scripts | 11:26:12 | success | `SCRIPTS_PRESENTES=YES` |
| 4 | 1 · interpretador | 11:26:12 → 11:26:13 | success | `INTERPRETADOR=py` |
| 9 | **5a-IT** · bancada nasce | 11:26:13 → 11:29:26 | success | `MIGRATION_001…007, 009…032 = PASS` (31 linhas; a 008 fora por desenho) |
| 10 | **5b** · Sala gate | 11:29:26 → 11:29:28 | success | `SALA_DE_ESPERA=PASS · BACKEND=POSTGRES` · env do passo já traz `SINTONIA_SALA_DSN=***localhost:54329/descartavel` |
| 11 | **5c** · egresso | 11:29:28 → 11:29:31 | success | `EGRESS_COUNTRY_CODE=IT · EGRESS_REQUIRED=IT · EGRESS_GATE=PASS` (ipinfo.io) |
| 12 | **6** · rodar a fase | 11:29:31 → 11:29:40 | success | `FASE=italia-documento · RUNNER=SINTONIA-EAME-LOCAL · REF=claude/it-collection-sala-v1` |
| 14 | 8 · devolver | 11:29:40 → 11:29:42 | success | `NADA_MUDOU=YES` — nenhum commit, nenhum push |
| 15 | **9z-IT** · bancada morre | 11:29:42 → 11:29:45 | success | `bancada destruida: cluster e ops-root removidos` |
| 16 | 9 · custo | 11:29:45 | success | `COST_USD_LIQUIDADO=0` |

`GATE_ORDER = 5a-IT → 5b → 5c → 6 → 9z-IT`, **observada** e não só declarada.
Os passos 2, 3, 4, 5 e 7 foram `skipped` pela condição de fase, como o YAML
manda. Nenhum `continue-on-error`; o único `|| true` que correu nesta corrida
é o `pg_ctl stop` do 9z-IT, e a amostragem física (abaixo) prova que o stop
aconteceu de verdade.

### 14.2 · O Postgres descartável, visto por fora

Amostragem a cada 20 s **nesta máquina** (o runner 1 corre aqui), durante o run:

```
11:26:19  passo 5a-IT   pg-italia-35215565657 existe · porta 54329 sem LISTEN · postgres.exe = 1   (initdb)
11:26:39 … 11:29:24     idem · porta 54329 LISTEN · postgres.exe = 6–7                              (cluster vivo, migrations)
11:29:44  passo 9z-IT   cluster ainda em disco · ops-italia-35215565657 existe · LISTEN = 0 · postgres.exe = 0
11:30:04  completed     cluster = 0 · ops-root = 0 · LISTEN = 0 · postgres.exe = 0
```

```
POSTGRES_TEMP_STARTED = YES · DATABASE = descartavel · HOST = 127.0.0.1 · PORT = 54329
MIGRATIONS_STARTED = YES · MIGRATIONS_APPLIED = 31 (001–007, 009–032) · MIGRATIONS_FAILED = 0
```

A contagem 31/31 é a mesma aritmética honesta do §8 (a 008 é verificação e o
aplicador salta-a). `select count(*) from schema_migracao` **não** foi medido:
o banco morreu no 9z-IT, por desenho, e esta revisão não abriu segunda ligação.

### 14.3 · A fase 6 — o que o workflow pediu e o que a máquina fez

```
FASE = italia-documento · SOURCE_ID = IT-T3-002 (explícito: FONTE_IT='IT-T3-002' no log)
ASSUNTO = colete pragas · FILTRO_PAIS = IT · FILTRO_FONTE = IT-T3-002
ORCHESTRATOR_CALLED = YES            py orquestrador/orquestrador.py "colete pragas" --filtro pais=IT --filtro fonte=IT-T3-002
COLLECTOR_DIRECTLY_CALLED_BY_WORKFLOW = NO   (o coletor só aparece no COMANDO do recibo, chamado PELO executor)
RUN_ID = IT-T3-2026-09-17-112933-23c76a2063b482c3   cunhado pelo orquestrador; o executor recebe-o por --run-id
EXECUTOR = coleta/italy_executor.py @ b9dfd3d2 · de 11:29:33Z a 11:29:40Z
NETWORK_ACQUISITION_OBSERVED = YES   OBSERVATIONS = 1 · BASELINE_DOCUMENT · HEALTH_STATE = HEALTHY · COST_USD = 0
```

O item adquirido é **novo** — não é reuso dos bytes do §130:

```
url            https://agricoltura.regione.campania.it/difesa/bollettini/bollettini_2026/pdf/SA-16-09.pdf
DOCUMENT_ID    CAMPANIA:SA:16-09-2026        (§130 tinha CAMPANIA:SA:09-09-2026 — o boletim da semana seguinte)
SHA256         c5ae3bfe76d9…                 (§130: d5aa781c…)  · BYTES 814266 · application/pdf · SOURCE_DATE 2026-09-16
RAW_OBSERVATION_ID   = NÃO EXISTE — nenhuma linha em raw_asset (ver 14.4)
DOCUMENT_ID_PROVENANCE = nome nativo do boletim (documentIdDe() em coleta/italy_pilot_collect.mjs); não é SHA
STORAGE_REUSED = NO · NEW_OBSERVATION = NO (no banco) · RAW em ficheiro = SIM (OPS_ROOT, destruído no 9z-IT)
```

### 14.4 · Onde a estrada partiu — o recibo da corrida, sem o resumo

O recibo que o orquestrador escreveu (`data/samples/RUN-MANIFEST.json`, no
workspace do runner, **não commitado**):

```
INGRESSO.PARA_A_PORTA        1 item  · RAW_OBJECT_CREATED true · RAW_PRESERVED_BEFORE_PARSE true
                             STORAGE_LOCATION ../../_temp/ops-italia-35215565657/data/collection-store/italy/IT-T3-002/…/SA-16-09.pdf
INGRESSO.PARA_A_DERIVACAO    []
INGRESSO.RUN_STATE           PARTIAL
INGRESSO.RASTRO              NAO_EMITIDO
INGRESSO.BANCO               "NAO MEDIDO — nao houve leitura do banco"
DERIVACAO.CHAMADO            false  · "nenhuma observacao preservada nesta corrida para derivar"
ESTRUTURACAO.CHAMADO         false
ADMISSAO                     itens 1 · NAO_SEI 1 · prontos 0 · espera null
LIVRO-DE-DECISOES            +1 decisão: NAO_SEI · regra «legivel» · «o item veio sem texto nenhum»
```

E a causa, lida no código do HEAD auditado, **sem alterar nada**:

| onde | o que diz |
|---|---|
| `orquestrador/orquestrador.py:1052` | `main()` chama `correr(p, so_plano=…, seco=…, so_a_porta=…, colheita_da_corrida=…)` — **sem** `memoria=` e **sem** `banco_do_rastro=` |
| `orquestrador/orquestrador.py:757-758` | `def correr(…, memoria=None, banco_do_rastro=None, …)` |
| `orquestrador.py` · `coleta/ingresso.py` · `guarda/preservar_coleta.py` · `coleta/derivacao_forward.py` | **0** ocorrências de `os.environ`/`getenv` — `BANCO_DESCARTAVEL_URL` e `SINTONIA_SALA_DSN`, que o 5a-IT exporta, nunca são lidos pela estrada |
| repositório inteiro, fora de `provas/` e `tests/` | **0** construções de `MemoriaPostgres(` |
| `guarda/preservar_coleta.py:1302/1348` | `RAW_OBSERVATIONS` só existe quando `memoria is not None` |
| `coleta/ingresso.py:1367` (comentário do dono) | «Sem banco, `preservar()` nao devolve `RAW_OBSERVATIONS` e a lista sai vazia» |
| `provas/primeira_coleta_controlada_italia.py:134` | a primeira coleta chamou `orq.correr(p, memoria=_pg.MemoriaPostgres(URL), banco_do_rastro=cc.Banco(URL))` — **em processo, banco ligado pelo corredor** |

Consequência exata: pela porta que o workflow usa, o `raw_asset` nunca nasce;
`unidades_para_a_derivacao()` (`ingresso.py:674`) só entrega o que o banco
confirmou; DERIVED e STRUCTURED não são chamados; a admissão julga o item da
entrada — um PDF sem texto — e responde `NAO_SEI`, com razão; a Sala recebe 0.
O próprio orquestrador já tinha escrito este furo no passado (comentário em
`orquestrador.py:961-967`, «UMA ETAPA QUE CORRE DEPOIS DO BURACO NAO FECHA O
BURACO») — fechou-o para a derivação e deixou aberta a **ligação do banco na
porta CLI**. Nenhum dos 15 testes de `test_fase_italiana_no_workflow.py`
podia apanhar isto: leem YAML.

**Alternativas consideradas e descartadas:** não é o `PSQL_SPAWN_FLAKE` (esse
regista `RAW_PERSISTENCE_FAILED`; aqui `RASTRO=NAO_EMITIDO` e `BANCO=NAO
MEDIDO`, isto é, o banco nem foi tentado); não é derivador ausente (a derivação
**não foi chamada**, `CHAMADO=false`); não é o Sala gate (passou, mas mede o
ambiente, não a estrada).

### 14.5 · O corredor, elo a elo

| elo | resultado | prova |
|---|---|---|
| REQUEST | PASS | pedido com fonte explícita, `PEDIDO.filtros = {pais: IT, fonte: IT-T3-002}` |
| ORCHESTRATOR | PASS | recibo assinado, RUN_ID do dono, executor escolhido pelo consumo de filtros |
| EXECUTOR | PASS | `italia-recorrente → coleta/italy_executor.py @ b9dfd3d2` |
| RUN | PASS | `IT-T3-2026-09-17-112933-23c76a2063b482c3` · STATUS SUCCESS |
| RAW (ficheiro) | PASS | 814 266 bytes no OPS_ROOT, sha `c5ae3bfe…`, `RAW_PRESERVED_BEFORE_PARSE=true` |
| **STORAGE (banco)** | **FAIL** | `raw_asset` nunca escrito: `BANCO=NAO MEDIDO`, `RASTRO=NAO_EMITIDO`, `PARA_A_DERIVACAO=[]` |
| DERIVED | NOT_RUN | `DERIVACAO.CHAMADO=false` |
| STRUCTURED | NOT_RUN | `ESTRUTURACAO.CHAMADO=false` |
| ADMISSION | coerente com o que recebeu: `NAO_SEI 1` | item sem texto; a resposta certa para a pergunta errada |
| READY | 0 | `prontos 0` |
| SALA_ROWS | 0 | `espera null` |
| SALA_READ_OTHER_PROCESS | NOT_APPLICABLE | não há linha para reler |

`REUSED` não aparece em lado nenhum, e não foi convertido em nada.
`UNKNOWN` não foi convertido em `PASS`.

### 14.6 · Produção — zero, por ausência de caminho executado

```
PRODUCTION_MIGRATIONS = 0        única chamada a cadeia_canonica.sh migrations: DSN descartável literal (yml l.354)
PRODUCTION_DB_WRITES = 0         nenhum banco recebeu raw_asset nesta corrida (14.4); SINTONIA_SALA_DSN (descartável)
                                 precede SUPABASE_DB_URL na Sala (sala_de_espera.py:741), e a Sala não foi escrita (prontos 0)
PRODUCTION_COLLECTION_RUNS = 0   o recibo foi para o RUN-MANIFEST do workspace do runner, não commitado
PRODUCTION_SALA_WRITES = 0
LIVE_DEPLOY = 0                  passo 8: NADA_MUDOU=YES · origin/claude/it-collection-sala-v1 = c93f6920 depois do run
```

`SUPABASE_DB_URL` continua no env do job (mascarado) e herdado por todos os
passos — a dívida de blindagem do §6a (5b não distingue produção; furo
`?host=`) **permanece** e não foi tocada. Esta revisão não fez SELECT nem
ligação à produção.

### 14.7 · Teardown — prova física, não log

Medido nesta máquina em 11:30:34Z (65 s depois do fim), e reconfirmado:

```
TEARDOWN_STEP_EXECUTED        = YES  (9z-IT, always(), 11:29:42 → 11:29:45, success)
POSTGRES_PROCESS_LEFT_FOR_RUN = 0    (Win32_Process com CommandLine *pg-italia-35215565657*, excluindo o PID da medição;
                                      tasklist postgres.exe/pg_ctl.exe = 0)
PORT_54329_LISTENING          = NO   (netstat: 0 linhas em qualquer estado)
TEMP_CLUSTER_LEFT             = NO   (C:\actions-runner-eame\_work\_temp\pg-italia-35215565657 não existe)
TEMP_OPS_ROOT_LEFT            = NO   (…\ops-italia-35215565657 não existe; RUNNER_TEMP vazio; .pgpw ausente)
PEGADA_FORA_DO_TEMP           = SIM  (XX/ e data/colheita/ no checkout do runner — ver 14.9, item 3; não é o que o contrato mede, e fica nomeado)
```

⚠️ Armadilha medida e registada: a **primeira** contagem de processos deu `1`
— era o próprio `powershell` da medição, cuja linha de comando continha o
nome do cluster. Excluir o PID de quem mede é obrigatório. Ver §132 do
know-how.

### 14.8 · Livro versionado e o workspace do runner

```
data/collection-ledger/italy/observations.ndjson   175 linhas · sha256 3ea37f88…  ANTES = DEPOIS
TRACKED_LEDGER_UNEXPECTED_DELTA = NO   (no worktree desta revisão: 0 ficheiros)
```

No **workspace do runner** (`C:\actions-runner-eame\_work\eame-sintonia\eame-sintonia`,
efémero, limpo pelo próximo checkout) a corrida deixou dois ficheiros
rastreados modificados e **não commitados**: `data/samples/RUN-MANIFEST.json`
(+139, o recibo) e `data/samples/LIVRO-DE-DECISOES.json` (+18, a decisão
NAO_SEI). É a dívida já nomeada `ADMISSION_LEDGER_NOT_ENV_REDIRECTABLE` (§8,
§11) — e o RUN-MANIFEST tem o mesmo caminho fixo. Classificado como
**esperado por dívida conhecida**, não como delta inesperado; o passo 8 não os
leva (só adiciona `INSTAGRAM-*`/`YOUTUBE-*`/`SCRAP-*`).

### 14.9 · Red team do replay (agente separado, só leitura)

Agente separado, só leitura, 23 ataques (os 22 do contrato + a leitura da
causa). Resultado: **0 blockers** contra a prova, e a causa raiz **confirmada**
de forma independente (`orquestrador.py:1050-1052` sem `memoria`/`banco_do_rastro`;
zero leituras de ambiente em orquestrador/ingresso/preservar; `MemoriaPostgres`
só em `provas/` e `tests/`; `preservar_coleta.py:1346-1347` devolve `[]` sem
memória). O que o red team acrescentou, e esta revisão adota:

1. **CANNOT_MEASURE honesto:** banco descartável, OPS_ROOT e `servidor.log`
   foram destruídos por desenho. O `created_at` exacto e «nenhum run anterior
   nesta branch» o red team não pôde ver (o `gh` do processo dele estava
   deslogado — a credencial ficou só na memória desta sessão); esta revisão
   mediu-os pela API autenticada **antes** do dispatch (cabeçalho: nenhum run
   nesta branch, 5 noutras — coerente com o `run_number 6` do Worker log do
   runner, `_diag/Worker_20260917-112513-utc.log`).
2. O ataque 12 foi confirmado com uma descarga própria do PDF (GET público,
   **fora** do pipeline, guardado fora do repositório): 814 266 bytes, sha
   `c5ae3bfe…`, `%PDF-1.7` — boletim semanal genuinamente novo. Fica registado
   porque é uma segunda ida à fonte, feita pelo revisor e não pela máquina.
3. **A pegada da corrida é maior que o teardown.** Fora do `_temp`, no
   checkout do runner (ignorados pelo git, `!!`): `XX/it-t3-002/DOCUMENT/c5ae3bfe76d9bef6-…-SA-16-09.pdf`
   (814 266 B, o mesmo sha — a cópia do `ArmazemLocal(RAIZ)`),
   `data/colheita/italia/colheita.json`, `data/colheita/italia/<RUN_ID>/RETORNO.json`,
   mais os dois JSON rastreados modificados (14.8). «cluster e ops-root
   removidos» é literalmente verdade; o 9z-IT **não cobre** o armazém nem a
   colheita. O checkout seguinte limpa (`git clean -ffdx`); o teardown não.
   Dívida nomeada: `TEARDOWN_FOOTPRINT`.
4. `NADA_MUDOU=YES` não prova que nada foi produzido: o passo 8 só stagea
   `INSTAGRAM-*`/`YOUTUBE-*`/`SCRAP-*`, logo o **recibo** da fase italiana
   (`RUN-MANIFEST.json`) nunca volta ao repositório por esta porta — e «o que
   não tem recibo não aconteceu» é lei do próprio orquestrador. Hoje o recibo
   vive no workspace do runner até o checkout seguinte o apagar. Dívida
   nomeada: `RECIBO_ITALIANO_NAO_VOLTA`. Esta revisão copiou-o para fora do
   repositório antes que isso acontecesse (excerto em 14.4).
5. Nenhum teste podia apanhar o blocker: `test_fase_italiana_no_workflow.py:130`
   só verifica que o YAML **nomeia** `orquestrador/orquestrador.py`; nenhum
   teste abre a porta CLI em subprocesso contra um banco.
6. Alternativas descartadas de forma independente: o psql nunca foi lançado
   (sem memória não há SQL); o derivador usa `pdftotext`
   (`executor_texto_de_pdf.py:131`), presente na máquina, e **não foi
   chamado**; os bytes estavam presentes (`PAYLOAD.ESTADO=PRESENTE`); o campo
   `ERROR` é ruído de stderr do `py` (D6).
7. O ficheiro de evidência consolidada desta revisão ainda não existia quando o
   red team arrancou (foi escrito segundos depois); ele trabalhou só com os
   logs, os diffs e os diagnósticos locais do runner — o que reforça a
   independência da confirmação.

```
RED_TEAM_REPLAY_BLOCKERS = 0
```

### 14.10 · Testes, antes e depois

```
py 3.12.10 (tool-cache do runner) + pytest 9.1.1 (site-packages emprestado — o Python312 desta máquina está sem python.exe)
antes  : tests/test_porta_de_producao.py + tests/test_fase_italiana_no_workflow.py → 56 passed · 1 failed
depois : idem → 56 passed · 1 failed (a mesma)
NEW_FAILURES = 0 · NEW_ERRORS = 0
PRODUCTION_GUARD = PASS (41/42; a falha é pré-existente) · WORKFLOW_STATIC_GATE = PASS (15/15)
```

A única falha — `NenhumEscritorAntigoSobrou::test_o_inventario_de_quem_fala_de_raw_asset_esta_fechado`
— compara `guarda\…` com `guarda/…` (separador do Windows) e **falha igual num
worktree do trunk `9d6dcbbd` nesta máquina**: pré-existente, só Windows, não
introduzida pelos 13 commits. Não foi corrigida (não é desta missão).

### 14.11 · O que este replay NÃO reescreve

- A primeira coleta (§130) **aconteceu** e a sua prova continua de pé:
  `SOURCE_TO_SALA_REAL_OBSERVED = YES`. Ela passou pela porta em processo do
  corredor, e o corredor ligou o banco. Este replay mede **outra porta** — a
  do workflow — e essa não liga.
- O BLOCKER-1 (§6b) continua **fechado**; a guarda passou 41/42 com a mesma
  falha de base.
- Nada foi corrigido: workflow, Python, testes, guardas, orquestrador e
  coletor estão como em `c93f6920`.

### 14.12 · Conserto mínimo — nomeado, NÃO feito, para missão que não seja este revisor

1. A porta CLI do orquestrador tem de ligar o banco quando o ambiente o
   declara (`BANCO_DESCARTAVEL_URL` / `SINTONIA_SALA_DSN`, com a trava
   `_e_descartavel` — e a mesma trava que hoje só vive em `provas/`), ou o
   workflow tem de chamar a porta que liga. Decisão de desenho da
   coordenação: **uma** porta, não duas.
2. Um teste que **execute** a porta CLI contra um banco descartável e exija
   `RAW_OBSERVATIONS ≥ 1` — os 15 testes do YAML não veem isto, e a estrada
   já se partiu neste sítio duas vezes antes (comentários em
   `orquestrador.py:940-967`).
3. Só depois: novo `INDEPENDENT_WORKFLOW_CANARY_REPLAY`, por missão
   independente, com o mesmo teardown físico.
4. Dívidas não bloqueantes, nomeadas pelo red team: `TEARDOWN_FOOTPRINT`
   (9z-IT não cobre `XX/` nem `data/colheita/`) e `RECIBO_ITALIANO_NAO_VOLTA`
   (o passo 8 nunca devolve o `RUN-MANIFEST.json` da fase italiana).

### 14.13 · Veredito

```
INDEPENDENT_WORKFLOW_CANARY_REPLAY = FAIL
WORKFLOW_REAL_CANARY               = FAIL
WORKFLOW_EXECUTED                  = YES
WORKFLOW_FLOW_OBSERVED             = NO
SOURCE_TO_SALA_REAL_OBSERVED       = YES (§130, mantido)
COLLECTION_INTEGRATION_CANDIDATE   = NO
BLOCKER                            = orquestrador.main() não liga memoria/banco_do_rastro → STORAGE nunca acontece pela porta do workflow
BIG_COLLECTION_AUTHORIZED          = NO
NENHUMA CORREÇÃO FUNCIONAL         = feita por este replay
```
