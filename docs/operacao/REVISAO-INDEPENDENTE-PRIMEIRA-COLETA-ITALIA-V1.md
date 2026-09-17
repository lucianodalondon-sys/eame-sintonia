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

---

## 15 · ADENDO — O BLOCKER DO §14 FOI FECHADO NO CÓDIGO (2026-09-17)

> Registado aqui porque este ficheiro é o dono do blocker. O veredito do §14
> é histórico e **não muda**: descreve o run `35215565657` sobre o HEAD
> `c93f6920`. O fecho veio em missão própria (`CLI_POSTGRES_BINDING_FIX`),
> que **não** foi a do revisor do §14, e que **não** disparou o workflow:
>
> ```
> orquestrador/orquestrador.py::main()   compõe memoria + banco_do_rastro ANTES de correr()
>                                        (orquestrador/persistencia.py — lê SÓ BANCO_DESCARTAVEL_URL)
> guarda/banco_descartavel.py            a trava, UMA, no runtime (host/hostaddr/service/dbname; PG*)
> guarda/memoria_postgres.py             o adaptador Postgres canónico; provas/ e portas_live são subclasses
> provas/a_porta_cli_liga_o_banco.py     a porta como PROCESSO contra Postgres 16 real: 36 casos PASS
>                                        (RUN, raw_asset.id, storage_object, DERIVED, STRUCTURED, reuso,
>                                        recusa de Supabase/?host=/PGHOSTADDR, produção-sem-bancada)
> red team de arquitetura                19 ataques → 0 blockers; 3 achados fechados na mesma missão
> regressão                              11 vermelhos antes = 11 depois, pelos mesmos nomes · NEW_FAILURES = 0
> ```
>
> Detalhe no know-how §133. O que este adendo **não** diz: que o workflow
> chega à Sala. Isso só o `INDEPENDENT_WORKFLOW_CANARY_REPLAY_2` (IT-T3-002,
> sessão nova, quem consertou não dispara) pode dizer — e tem de exigir
> `RAW_OBSERVATIONS >= 1` e `PERSISTENCIA = DESCARTAVEL` no recibo, não
> `conclusion=success`. `TEARDOWN_FOOTPRINT` e `RECIBO_ITALIANO_NAO_VOLTA`
> (§14.9) ficam como estavam. `BIG_COLLECTION_AUTHORIZED = NO` continua.

---

## 16 · INDEPENDENT_WORKFLOW_CANARY_REPLAY_2 — 2026-09-17

> Segundo replay independente pelo **workflow real** (`sintonia-scrap.yml`,
> fase `italia-documento`, fonte `IT-T3-002`), por agente de sessão nova que
> **não** implementou o conserto do §15 e que **não corrigiu nada** durante o
> exame. A pergunta única: depois do `CLI_POSTGRES_BINDING_FIX`, o workflow
> real chega à Sala? **A pergunta ficou sem resposta**: o portão de egresso
> (5c) bloqueou a corrida ANTES da rede porque o runner saía por Brasil, e o
> passo 6 nunca correu. Veredito **BLOCKED**, não FAIL — a estrada não foi
> corrida; nada nela foi medido, nem a favor nem contra.

```
MISSÃO                 INDEPENDENT_WORKFLOW_CANARY_REPLAY_2 · IT-T3-002 · italia-documento
MEDIDO EM              2026-09-17 (dispatch 13:31:58Z · fim 13:36:03Z)
HEAD AUDITADO          b8e07e0375be92491e837cef9f12169dac2b3291  = REMOTE_COLLECTION_HEAD antes e depois
TRUNK                  origin/claude/it-trunk-v1 = 9d6dcbbd · merge-base = o trunk · 16 à frente / 0 atrás
WORKTREE               limpa antes e depois (0 ficheiros) · LOCAL_UNPUBLISHED 0

GITHUB_WORKFLOW_RUN_ID 35227662328 · run_attempt 1 · event workflow_dispatch · created_at 13:32:00Z
GITHUB_RUN_URL         https://github.com/lucianodalondon-sys/eame-sintonia/actions/runs/35227662328
GITHUB_RUN_HEAD_SHA    b8e07e03… — o auditado (o checkout imprime-o no log às 13:32:34Z)
RUNNER                 SINTONIA-EAME-LOCAL (input runner=1 · runner_id 21 · C:\actions-runner-eame)
                       antes do dispatch: os dois runners online e busy=false (API)
RUN_IDS_BEFORE         35215565657 (o replay 1, 11:25Z) — único run deste workflow nesta branch
GITHUB_RUN_CONCLUSION  failure   (passo 5c · portão de egresso · exit 1)

INDEPENDENT_WORKFLOW_CANARY_REPLAY_2 = BLOCKED
WORKFLOW_REAL_CANARY                 = NOT_RUN     (o passo 6 foi `skipped`; o orquestrador nunca correu)
WORKFLOW_FLOW_OBSERVED               = NO          (não observado — não «observado a partir-se»)
SOURCE_TO_SALA_REAL_OBSERVED         = YES         (§130 — mantido; este replay não o repete nem o reverte)
CLI_POSTGRES_BINDING_OBSERVED_IN_WORKFLOW = NOT_MEASURED
COLLECTION_INTEGRATION_CANDIDATE     = NO
BLOCKER                              = EGRESS_COUNTRY_CODE = BR no runner SINTONIA-EAME-LOCAL: o ProtonVPN
                                       desta máquina estava sem túnel ativo (só a placa Ethernet «Up»;
                                       IP público 177.95.91.48, Telefônica Brasil, São Paulo). O portão 5c
                                       respondeu EGRESS_GATE=BLOCKED e o workflow parou ali, por desenho.
BIG_COLLECTION_AUTHORIZED            = NO
```

**A frase que resume:** o workflow correu até ao portão de egresso e o
portão disse **não** — pela primeira vez numa corrida real. A bancada
descartável nasceu, as 31 migrations passaram, o Sala gate aprovou o
ambiente, e às 13:35:42Z o `superficie/rede.py --portao-de-egresso IT` mediu
`BR` e saiu com 1. O passo 6 (a fase) ficou `skipped`. Não houve orquestrador,
não houve rede de aquisição, não houve RUN, não houve linha em banco nenhum.
O conserto do §15 **não foi observado** — nem a funcionar nem a falhar.
`UNKNOWN` não vira PASS e não vira FAIL.

### 16.1 · Pré-portões (antes da rede)

```
STATIC_GATES                 = tests/test_porta_de_producao.py + tests/test_fase_italiana_no_workflow.py
                               + tests/test_a_porta_cli_liga_o_banco.py → 79 passed · 1 failed (72 s)
NEW_FAILURES_BEFORE_REPLAY   = 0   (a falha é a mesma do §14.10: separador de caminho do Windows,
                                    `NenhumEscritorAntigoSobrou::test_o_inventario_de_quem_fala_de_raw_asset_esta_fechado`)
WORKTREE depois dos testes   = 0 ficheiros (a suíte não escreveu no acervo)
interpretador                = /c/actions-runner-2/_work/_tool/Python/3.12.10/x64/python.exe com o
                               site-packages emprestado de Python312 (pytest 9.1.1); `py` desta máquina
                               imprime «Could not find platform independent libraries» e não tem pytest
```

O que os pré-portões **não** mediram, e deviam: o egresso da máquina. Ver
16.11.

### 16.2 · A ordem, provada por hora de início (API `jobs`, não o YAML)

| # | passo | início → fim (UTC) | conclusão | prova no log |
|---|---|---|---|---|
| 2 | checkout | 13:32:08 → 13:32:34 | success | `c93f6920..b8e07e03` fetch · imprime `b8e07e0375be92491e837cef9f12169dac2b3291` |
| 3 | 0 · o ref tem os scripts | 13:32:34 | success | `SCRIPTS_PRESENTES=YES` |
| 4 | 1 · interpretador | 13:32:34 | success | `INTERPRETADOR=py` |
| 9 | **5a-IT** · bancada nasce | 13:32:35 → 13:35:40 | success | `MIGRATION_001…007, 009…032=PASS` (31 linhas · 0 não-PASS) |
| 10 | **5b** · Sala gate | 13:35:40 → 13:35:41 | success | `SALA_DE_ESPERA=PASS · BACKEND=POSTGRES` · env do passo já traz `SINTONIA_SALA_DSN=***localhost:54329/descartavel` e `BANCO_DESCARTAVEL_URL=***localhost:54329/descartavel` |
| 11 | **5c** · egresso | 13:35:41 → 13:35:42 | **failure** | `EGRESS_COUNTRY_CODE=BR · EGRESS_REQUIRED=IT · EGRESS_GATE=BLOCKED` · `##[error]Process completed with exit code 1` |
| 12 | **6** · rodar a fase | 13:35:42 | **skipped** | — |
| 14 | 8 · devolver | 13:35:42 → 13:35:45 | success | `NADA_MUDOU=YES` — nenhum commit, nenhum push |
| 15 | **9z-IT** · bancada morre | 13:35:45 → 13:35:48 | success | `bancada destruida: cluster e ops-root removidos` |
| 16 | 9 · custo | 13:35:48 → 13:35:50 | success | `COST_USD_LIQUIDADO=0` |

`GATE_ORDER = 5a-IT → 5b → 5c ✗`. Os portões correram **antes** da rede de
aquisição — e um deles fechou. Passos 2, 3, 4, 5 e 7 `skipped` pela condição
de fase. Nenhum `continue-on-error`; o `|| true` do `pg_ctl stop` do 9z-IT é
o único que correu, e a amostragem física (16.3) prova que o stop aconteceu.

### 16.3 · O Postgres descartável, visto por fora (amostragem de 2 s nesta máquina)

```
13:32:36Z  passo 5a-IT   pg-italia-35227662328 existe · 54329 sem LISTEN · postgres.exe = 1     (initdb)
13:32:43Z … 13:35:44Z    LISTEN = 1 · postgres.exe = 6 · cluster em disco                        (vivo, migrations)
13:32:43Z … 13:35:40Z    contagens no banco (segunda ligação, só leitura): schema_migracao 30 → 31;
                         collection_run 0 · raw_asset 0 · storage_object 0 · derived_artifact 0 ·
                         documento_estruturado 0 · etapa_da_corrida 0 · sala_de_espera 0 — SEMPRE
13:35:44Z  passo 9z-IT   psql: «o sistema de banco de dados está desligando»
13:35:50Z  em diante     LISTEN = 0 · postgres.exe = 0 · cluster = 0 · ops-root = 0
```

```
POSTGRES_TEMP_STARTED = YES · HOST = 127.0.0.1 · PORT = 54329 · DATABASE = descartavel
MIGRATIONS = PASS · 31 (001–007, 009–032) · lidas no banco: schema_migracao = 31
ITALY_OPS_ROOT = $RUNNER_TEMP/ops-italia-35227662328 — declarado no env, NUNCA criado (o passo 6 não correu)
```

Ao contrário do §14.2, esta revisão **abriu** uma segunda ligação ao banco
descartável, só leitura, a cada 2 s, para que RAW/STORAGE/SALA pudessem ser
lidos no próprio banco e não só no recibo. Serviu para provar o zero: nada foi
escrito por ninguém.

### 16.4 · O corredor, elo a elo

| elo | resultado | prova |
|---|---|---|
| REQUEST | NOT_RUN | o `case italia-documento` do passo 6 nunca executou (`skipped`) |
| ORCHESTRATOR | NOT_RUN | `ORCHESTRATOR_CALLED = NO` — zero linhas de `orquestrador/orquestrador.py` em passo executado |
| RUN | NOT_RUN | `collection_run = 0` no banco durante toda a vida da bancada · `COLLECTION_RUN_ID = NENHUM` |
| RAW | NOT_RUN | `raw_asset = 0` · `RAW_OBSERVATIONS = 0` · `RAW_OBSERVATION_ID = NÃO EXISTE` |
| STORAGE | NOT_RUN | `storage_object = 0` · `STORAGE_REUSED = NOT_APPLICABLE` |
| DERIVED | NOT_RUN | `derived_artifact = 0` |
| STRUCTURED | NOT_RUN | `documento_estruturado = 0` |
| ADMISSION | NOT_RUN | sem item, sem decisão; `LIVRO-DE-DECISOES.json` do checkout do runner igual ao HEAD |
| READY | 0 | — |
| SALA_ROWS | 0 | `sala_de_espera = 0` |
| PERSISTENCIA.ESTADO | NOT_MEASURED | não há recibo: `RUN-MANIFEST.json` do checkout do runner igual ao HEAD |
| MEMORIA / BANCO_DO_RASTRO | NOT_MEASURED | idem |
| NETWORK_ACQUISITION | NO | a única rede desta corrida foi o `GET https://ipinfo.io/json` do portão |
| DIRECT_COLLECTOR_CALL | NO | `italy_pilot_collect.mjs` / `italy_executor.py` não aparecem em passo executado |

`NOT_RUN` aqui é literal: não é «correu e não produziu», é «não correu».
`REUSED` não aparece em lado nenhum. `NAO_SEI` não foi convertido em nada.

### 16.5 · Produção — zero, por ausência de caminho executado

```
PRODUCTION_MIGRATIONS = 0        única chamada a cadeia_canonica.sh migrations: DSN descartável literal (yml l.354)
PRODUCTION_DB_WRITES = 0         nenhum passo executado escreve em banco; o único banco vivo era o descartável, e ficou a zero
PRODUCTION_SALA_WRITES = 0       a Sala não recebeu item; SINTONIA_SALA_DSN (descartável) estava no env do 5b e do 5c
PRODUCTION_COLLECTION_RUNS = 0   não houve RUN
LIVE_DEPLOY = 0                  passo 8: NADA_MUDOU=YES · origin/claude/it-collection-sala-v1 = b8e07e03 antes e depois
```

`SUPABASE_DB_URL` continua no env do job (mascarado), herdado por todos os
passos — a dívida de blindagem do §6a **permanece** e não foi tocada. Esta
revisão não fez SELECT nem ligação à produção.

### 16.6 · Teardown — prova física, não log

Medido nesta máquina às 13:37:43Z (100 s depois do fim) e reconfirmado:

```
TEARDOWN_STEP_EXECUTED        = YES  (9z-IT, always(), 13:35:45 → 13:35:48, success)
POSTGRES_PROCESS_LEFT_FOR_RUN = 0    (Win32_Process com CommandLine *35227662328*, EXCLUINDO a árvore de quem mede;
                                      tasklist postgres.exe = 0 · pg_ctl.exe = 0)
PORT_54329_LISTENING          = NO   (netstat: 0 linhas)
TEMP_CLUSTER_LEFT             = NO   (…\_temp\pg-italia-35227662328 não existe)
TEMP_OPS_ROOT_LEFT            = NO   (…\_temp\ops-italia-35227662328 nunca existiu; RUNNER_TEMP vazio; .pgpw ausente)
TEARDOWN                      = PASS
TEARDOWN_FOOTPRINT            = 0 nesta corrida (XX/ e data/colheita/ não nasceram: o passo 6 não correu)
                                — a dívida do §14.9 fica como estava, NÃO medida a favor
```

⚠️ A armadilha do §132 mordeu outra vez, mais fundo: a primeira contagem
deu **4** com o PID do PowerShell excluído — eram os três `bash.exe` da
cadeia da própria medição (o comando continha o run id) mais o PowerShell.
Excluir o PID de quem mede não chega; é a **árvore** de quem mede.

### 16.7 · Livro versionado e o checkout do runner

```
data/collection-ledger/italy/observations.ndjson   175 linhas · sha256 3ea37f88…  ANTES = DEPOIS
TRACKED_LEDGER_UNEXPECTED_DELTA = NO   (no worktree desta revisão: 0 ficheiros, antes e depois)
```

No checkout do runner (`C:\actions-runner-eame\_work\eame-sintonia\eame-sintonia`)
o `actions/checkout` desta corrida **apagou** a pegada do replay 1 (`XX/`,
`data/colheita/`, os dois JSON modificados) — confirma o «o checkout seguinte
limpa» do §14.9. Depois desta corrida: HEAD `b8e07e03`, 0 ficheiros
modificados, 0 ignorados fora do padrão. `RECIBO_GERADO = NO ·
RECIBO_ACESSIVEL_NO_RUNNER = NOT_APPLICABLE · RECIBO_RETORNADO_PELO_WORKFLOW = NO`
— a dívida `RECIBO_ITALIANO_NAO_VOLTA` não foi exercida.

### 16.8 · A causa, medida por fora do workflow

```
13:38:19Z  curl https://ipinfo.io/json (esta máquina)   ip 177.95.91.48 · São Paulo · country BR · AS27699 TELEFÔNICA BRASIL
13:38:19Z  superficie/rede.py --portao-de-egresso IT     EGRESS_COUNTRY_CODE=BR · EGRESS_GATE=BLOCKED (mesma resposta do 5c)
           HTTPS_PROXY / HTTP_PROXY                       vazios (a rota não está na variável — como no know-how)
           processos                                       ProtonVPN.Client.exe · ProtonVPNService.exe · ProtonVPN.NrptWatchdog.exe vivos
           adaptadores «Up»                                Ethernet (Intel I211) · Topaz Loopback — NENHUM túnel
```

O cliente da VPN está aberto e o túnel não. Não é defeito de código, de
workflow nem de bancada: é o ambiente de rede desta máquina neste momento.
O replay 1 (11:25Z) e a primeira coleta (§130) passaram no mesmo portão
porque a VPN estava ligada nessas horas.

### 16.9 · Red team do replay 2 (agente separado, só leitura)

Agente separado, só leitura, 23 ataques (os 22 do contrato + a causa). Leu o
log do job, a amostragem física, o diagnóstico do runner, o checkout do runner,
a API do GitHub e o repositório; não editou, não disparou, não correu nada.

| # | ataque | veredito | prova |
|---|---|---|---|
| 1 | run não é o recém-despachado | REFUTADO | `created_at 13:32:00Z` · `run_number 7` · dispatch 13:31:58Z (2 s) · Worker diag traz o run id · só 2 runs nesta branch |
| 2 | SHA não é o auditado | REFUTADO | `head_sha b8e07e03…` · checkout imprime-o às 13:32:34Z · `HEAD is now at c93f6920` no log é o estado ANTES do fetch (o runner reaproveita a pasta) |
| 3 | banco não era descartável | REFUTADO | `initdb` em `_temp/pg-italia-<run>` · `-p 54329 -h 127.0.0.1` · as únicas URLs do log: 13× `***localhost:54329/descartavel` + 1× `postgres@localhost:54329/postgres` |
| 4–7, 9, 10, 13, 22 | PERSISTENCIA / memória / rastro / RAW de ficheiro / ID de SHA / storage inventado / Admission≠READY / REUSED | NÃO SE APLICA | o orquestrador nunca correu (passo 6 `skipped`); não há recibo; `collection_run = 0` |
| 8, 11, 12, 14 | raw_asset não escrito / DERIVED / STRUCTURED / Sala zero | CONFIRMADO COMO FACTO, NÃO DERRUBA | `0|0|0|0|0|0|0|31` às 13:35:40Z — é o que o revisor alega, porque a aquisição não aconteceu |
| 15 | Supabase usada em silêncio | REFUTADO | zero hosts fora de localhost/127.0.0.1/github/ipinfo no log · `SUPABASE_DB_URL` só no bloco `env:` mascarado · o único leitor executado é `sala_de_espera.py:741`, e `SINTONIA_SALA_DSN` (descartável) vem primeiro · `cadeia_canonica.sh` usa o argumento literal |
| 16 | gates depois da rede | REFUTADO | 5a-IT 13:32:35 → 5b 13:35:40 → 5c 13:35:41 → 6 skipped; a única rede antes dos portões é o `git fetch` do checkout; a única rede do 5c é o próprio checker |
| 17 | workflow chamou collector direto | REFUTADO | `italy_pilot_collect`/`italy_executor` só no eco do passo 0 (`[ -f "$f" ]`) e em comentário do YAML; passo 6 `skipped` |
| 18 | teardown deixou Postgres | REFUTADO | 13:41Z: netstat 0 · tasklist 0 · `_temp` vazio · 4 processos com o run id = a própria cadeia de medição do red team (bash→bash→bash→powershell); fora dela 0 |
| 19 | recurso temporário vivo | REFUTADO | `.pgpw` apagado no próprio 5a-IT · `ops-italia-<run>` nunca existiu (`ops=[]` nas 156 amostras) · `pg-italia-<run>` ausente |
| 20 | outro run confundido | REFUTADO, com ressalva | único run criado ≥ 13:25Z; o `system-map.yml` 35226510721 (13:21Z, mesma branch e SHA) corre em runners do GitHub (`ubuntu-latest`), não no runner 21 — ver nota abaixo |
| 21 | vermelho a esconder etapa | REFUTADO | Worker diag: 16 passos, UM `Step result: Failed` (o 5c, exit 1) · `continue-on-error` = 0 · os `\|\| true` (git add/pull do 8, pg_ctl stop do 9z-IT) provados inócuos · a 008 é saltada por desenho (`cadeia_canonica.sh:107`) e `schema_migracao = 31` |
| 23 | a causa: egresso BR, VPN desligada | CONFIRMADO | 5c: `EGRESS_COUNTRY_CODE=BR · EGRESS_GATE=BLOCKED` · medição própria 13:41:58Z: BR, São Paulo, Telefônica |

Livro versionado: 175 linhas, sha256 `3ea37f88…`, igual no worktree e no
checkout do runner; ponteiro remoto `b8e07e03` — nenhum push saiu deste run.

```
RED_TEAM_REPLAY_2_BLOCKERS = 0
```

O red team sobre o veredito: «BLOCKED é defensável e é o único veredito
honesto — a estrada nunca foi pisada, porque um portão anterior à aquisição
mediu o país errado e parou tudo como devia; FAIL seria dizer que a estrada
partiu, e ela não chegou a ser corrida.»

**Nota (ressalva do ataque 20), fora do escopo deste replay:** o run
`system-map.yml` 35226510721, disparado pelo push de `b8e07e03` às 13:21Z em
runners do GitHub, tinha `COLETA CHECK = failure` (13:22:41Z) e `MAP RULES
CHECK` em progresso quando o red team olhou. Não é este run, não é esta
máquina, não toca a 54329; fica nomeado para quem for dono do CI dessa
branch.

### 16.10 · O que este replay NÃO reescreve, e o que NÃO fez

- Não reescreve o §130 (a coleta aconteceu) nem o §14 (o replay 1 partiu-se
  em STORAGE) nem o §15 (o conserto existe no código e está provado como
  processo). O conserto **não foi observado no workflow** — nem bem nem mal.
- Não ligou a VPN, não repetiu o dispatch, não correu o orquestrador nem o
  coletor à mão, não fez replay 3. «Não repetir automaticamente» é do
  contrato desta missão; ligar a VPN é decisão de gente.
- Não corrigiu código, workflow, teste ou guarda. Nada mudou em `b8e07e03`
  além deste documento, do know-how e do mapa.

### 16.11 · O que a coordenação precisa de decidir antes do replay 3

1. **Ligar o túnel do ProtonVPN a um servidor italiano na máquina do runner**
   e medir, ANTES de despachar, `curl -s https://ipinfo.io/json` → `country: IT`.
   Custa 5 segundos; a corrida gasta 3 minutos a construir a bancada antes de
   fazer essa pergunta.
2. Só então `INDEPENDENT_WORKFLOW_CANARY_REPLAY_3`, por sessão nova, com o
   mesmo contrato: `RAW_OBSERVATIONS >= 1`, `PERSISTENCIA = DESCARTAVEL`,
   `SALA_ROWS >= 1`, teardown físico, red team.
3. Opcional, e **não** para este revisor decidir: um pré-portão de egresso
   antes do 5a-IT pouparia a bancada quando a VPN está desligada. A ordem
   atual (Sala primeiro, porque não custa rede) é deliberada e continua
   correta; o que se paga é uma bancada de 3 minutos construída para nada.

### 16.12 · Veredito

```
INDEPENDENT_WORKFLOW_CANARY_REPLAY_2       = BLOCKED
WORKFLOW_REAL_CANARY                       = NOT_RUN
WORKFLOW_EXECUTED                          = PARTIAL (até ao portão de egresso, inclusive)
WORKFLOW_FLOW_OBSERVED                     = NO
SOURCE_TO_SALA_REAL_OBSERVED               = YES (§130, mantido)
CLI_POSTGRES_BINDING_OBSERVED_IN_WORKFLOW  = NOT_MEASURED
COLLECTION_INTEGRATION_CANDIDATE           = NO
BLOCKER                                    = EGRESS_COUNTRY_CODE = BR (ProtonVPN sem túnel na máquina do runner) — portão 5c fechou antes da rede
BIG_COLLECTION_AUTHORIZED                  = NO
NENHUMA CORREÇÃO FUNCIONAL                 = feita por este replay
```

## 17 · INDEPENDENT_WORKFLOW_CANARY_REPLAY_3 — 2026-09-17

> Terceiro replay independente pelo **workflow real** (`sintonia-scrap.yml`,
> fase `italia-documento`, fonte `IT-T3-002`), por agente de sessão nova, com
> o túnel do ProtonVPN ligado à mão pelo operador ANTES da missão e medido de
> novo ANTES do dispatch. A pergunta única: depois do `CLI_POSTGRES_BINDING_FIX`
> (§15), o workflow real chega à Sala quando consegue passar o portão IT?
> **A resposta é não, e desta vez a estrada foi corrida**: os três portões
> (bancada, Sala, egresso) passaram, o passo 6 correu, o orquestrador ligou a
> `MemoriaPostgres` — e a primeira chamada ao `psql` a partir do Python morreu
> com «programa não encontrado». Veredito **FAIL**, não BLOCKED. Nenhuma
> correção foi feita.

```
MISSÃO                 INDEPENDENT_WORKFLOW_CANARY_REPLAY_3 · IT-T3-002 · italia-documento
MEDIDO EM              2026-09-17 (dispatch 14:12:23Z · fim 14:16:57Z)
MODEL_EFFECTIVE        Fable 5.1 (claude-fable-5-1) · effort high
HEAD AUDITADO          350921524f4fcc8bd81450f0159efc513fd0d220  = REMOTE_COLLECTION_HEAD antes e depois
TRUNK                  origin/claude/it-trunk-v1 = 9d6dcbbd · merge-base = o trunk · 17 à frente / 0 atrás
WORKTREE               limpa antes e depois (0 ficheiros) · LOCAL_UNPUBLISHED 0

EGRESS_BEFORE_DISPATCH ipinfo 14:12:18Z → 205.147.30.6 · Milan · Lombardy · IT · AS208172 Proton AG
                       (processos ProtonVPN.Client/WireGuardService vivos; a mesma leitura durante a
                       corrida às 14:13:37Z e depois dela às 14:23Z)
                       ⚠ ifconfig.co diz «US» para o MESMO IP: discordância entre bases de geolocalização.
                       O portão do workflow (`superficie/rede.py:175`) mede pelo ipinfo — e só por ele.

GITHUB_WORKFLOW_RUN_ID 35232024024 · run_number 8 · run_attempt 1 · event workflow_dispatch · created_at 14:12:26Z
GITHUB_RUN_URL         https://github.com/lucianodalondon-sys/eame-sintonia/actions/runs/35232024024
GITHUB_RUN_HEAD_SHA    35092152… — o auditado
RUNNER                 SINTONIA-EAME-LOCAL (input runner=1 · runner_id 21 · C:\actions-runner-eame)
                       antes do dispatch: os dois runners online e busy=false (API)
RUN_IDS_BEFORE         35227662328 (replay 2, 13:32Z, failure) · 35215565657 (replay 1, 11:25Z, success)
GITHUB_RUN_CONCLUSION  failure   (passo 6 · rodar a fase · exit 1 · 7,3 s)

INDEPENDENT_WORKFLOW_CANARY_REPLAY_3      = FAIL
WORKFLOW_REAL_CANARY                      = FAIL
WORKFLOW_EXECUTED                         = YES         (todos os passos correram; o 6 falhou)
WORKFLOW_FLOW_OBSERVED                    = YES         (observado A PARTIR-SE — na primeira chamada ao psql)
SOURCE_TO_SALA_REAL_OBSERVED              = YES         (§130 — mantido; este replay não o repete nem o reverte)
CLI_POSTGRES_BINDING_OBSERVED_IN_WORKFLOW = YES         (a pilha de erro prova `MemoriaPostgres` ligada pela porta CLI)
COLLECTION_INTEGRATION_CANDIDATE          = NO
BLOCKER                                   = passo 6: `guarda/memoria_postgres.py:117 _psql` → `subprocess.run(["psql", …])`
                                            → `FileNotFoundError [WinError 2]`. O executável `psql` não foi
                                            encontrado pelo Python dentro do job. Zero linhas no banco
                                            descartável. Mecanismo de raiz: NÃO PROVADO (ver 17.5).
BIG_COLLECTION_AUTHORIZED                 = NO
```

**A frase que resume:** o workflow atravessou os três portões, o orquestrador
adquiriu IT-T3-002 da rede (boletim novo, `SA-16-09.pdf`, 814.266 bytes,
14:16:32Z), guardou os bytes em ficheiro e, ao ir escrever a primeira linha no
banco descartável, não encontrou o `psql`. Adquiriu — e não preservou. O
conserto do §133 **foi consumido** (a memória ligada era Postgres), e é
exatamente por ter sido consumido que a corrida caiu onde nunca tinha caído.

### 17.1 · A ordem, provada por hora de início (API `jobs`, não o YAML)

| # | passo | início → fim (UTC) | conclusão | prova no log |
|---|-------|--------------------|-----------|--------------|
| 2 | checkout | 14:12:42 → 14:13:04 | success | ref `claude/it-collection-sala-v1` |
| 3 | 0 · o ref tem os scripts | 14:13:04 → 14:13:05 | success | `SCRIPTS_PRESENTES=YES` |
| 4 | 1 · interpretador | 14:13:05 → 14:13:06 | success | `INTERPRETADOR=py` |
| 5–8 | 2, 3, 4, 5 | 14:13:06 | skipped | condição de fase |
| 9 | 5a-IT · bancada nasce | 14:13:06 → 14:16:23 | success | `MIGRATION_001…007, 009…032 = PASS` (31 linhas, 14:13:28 → 14:16:18) |
| 10 | 5b · Sala gate | 14:16:23 → 14:16:23 | success | `SALA_DE_ESPERA=PASS · BACKEND=POSTGRES` |
| 11 | 5c · egresso | 14:16:23 → 14:16:25 | success | `EGRESS_COUNTRY_CODE: IT · EGRESS_REQUIRED: IT · EGRESS_GATE: PASS` · `CHECKER: https://ipinfo.io/json` |
| 12 | 6 · rodar a fase | 14:16:25 → 14:16:33 | **failure** | `FASE=italia-documento · RUNNER=SINTONIA-EAME-LOCAL` → traceback → `exit code 1` |
| 13 | 7 · liquidar | 14:16:33 | skipped | só fase paga |
| 14 | 8 · devolver | 14:16:33 → 14:16:34 | success | `NADA_MUDOU=YES · a fase nao produziu arquivo novo` |
| 15 | 9z-IT · bancada morre | 14:16:34 → 14:16:36 | success | `bancada destruida: cluster e ops-root removidos` |
| 16 | 9 · custo | 14:16:36 → 14:16:37 | success | `COST_USD_LIQUIDADO=0` |

`GATE_ORDER = 5a-IT → 5b → 5c → 6 ✗ → 8 → 9z-IT`. Os portões correram
ANTES da rede: a aquisição de IT-T3-002 aconteceu dentro do passo 6
(`COLLECTION_RUN_STARTED_AT 14:16:26.814Z`), depois de o 5c ter dito PASS
às 14:16:25. Nenhum portão correu depois da rede.

### 17.2 · O banco descartável

```
POSTGRES_TEMP_STARTED  = YES   porta 127.0.0.1:54329 LISTENING (PID 74456) medida na máquina às 14:13:37Z;
                               6 processos postgres.exe nesse instante; cluster `_temp\pg-italia-35232024024` presente
HOST / DATABASE / PORT = localhost · descartavel · 54329   (env do job: `***localhost:54329/descartavel`)
MIGRATIONS             = 31 aplicadas (001–007, 009–032; a 008 é verificação e o aplicador salta-a) · 0 falhadas
                         (contagem no banco NÃO medida: o cluster morreu no 9z-IT antes de qualquer leitura)
PERSISTENCIA_ESTADO    = DESCARTAVEL — por inferência forte, não por impressão: a linha `persistencia: …`
                         nunca chegou a ser impressa (o crash antecede `orquestrador.py:1080`), mas a pilha
                         de erro passa por `memoria_postgres.py:197 copia_em`, e `MemoriaPostgres` só nasce
                         no ramo DESCARTAVEL de `orquestrador/persistencia.py:145-150`, que exige
                         `BANCO_DESCARTAVEL_URL` provada descartável (`guarda/banco_descartavel.py`).
MEMORIA                = MemoriaPostgres   (pela pilha)
BANCO_DO_RASTRO        = Banco (coleta_checkpoint) — composto no mesmo ramo; NÃO exercido antes do crash
BANCO_DESCARTAVEL_URL  = consumida pela porta CLI: YES (é a única variável que `dependencias_do_runtime` lê)
```

### 17.3 · O corredor, elo a elo

| elo | resultado | prova |
|-----|-----------|-------|
| REQUEST | `colete pragas --filtro pais=IT --filtro fonte=IT-T3-002` | passo 6, ramo `italia-documento` do YAML |
| ORCHESTRATOR | CALLED = YES · DIRECT_COLLECTOR_CALL_BY_WORKFLOW = NO | o YAML só chama `orquestrador/orquestrador.py`; a pilha nasce em `main:1076` |
| EXECUTOR | `italia-recorrente @ adapter-v1` · ESTADO SUCCESS | `data/colheita/italia/IT-T3-2026-09-17-141626-b9586dcaa2c7281b/RETORNO.json` no checkout do runner (escrito 14:16:32Z) |
| RUN | COLLECTION_RUN_ID = `IT-T3-2026-09-17-141626-b9586dcaa2c7281b` · cunhado pelo orquestrador · **linha no banco: NÃO** | o `insert` da corrida vive em `preservar_coleta.py:1314`, depois do ponto do crash (`:1303`) |
| NETWORK_ACQUISITION | **YES** · `https://agricoltura.regione.campania.it/difesa/bollettini/bollettini_2026/pdf/SA-16-09.pdf` · 814.266 bytes · `application/pdf` · sha256 `c5ae3bfe76d9…0bdc` · SOURCE_DATE 2026-09-16 · CAPTURED_AT 14:16:32.734Z | `colheita.json` + `RETORNO.json` no checkout do runner; é um documento NOVO (o replay 1 trouxe o `SA-02-09`) |
| RAW | RAW_OBSERVATIONS = **0** · RAW_OBSERVATION_ID = **inexistente** · bytes em ficheiro: SIM | `enviar_os_bytes` (`preservar_coleta.py:1283`) escreveu `XX/it-t3-002/DOCUMENT/c5ae3bfe76d9bef6-…-SA-16-09.pdf` (814.266 bytes, pasta ignorada pelo Git) e o ops-root (destruído no 9z-IT); a primeira leitura ao banco (`copia_em`) foi a que rebentou |
| STORAGE | STORAGE_OBJECTS = 0 no banco · STORAGE_REUSED = NÃO SE APLICA | nenhuma linha escrita |
| DERIVED | NOT_RUN | `pela_derivacao` em `orquestrador.py:972`, depois do crash em `:956` |
| STRUCTURED | NOT_RUN | `pela_estruturacao` em `:988` |
| ADMISSION | NOT_RUN | `pela_porta` em `:1008` |
| READY | 0 | nunca chegou |
| SALA_ROWS | **0** | nunca chegou |

### 17.4 · O erro, tal como o log o mostra

```
File "…\orquestrador\orquestrador.py", line 1076, in main         recibo = correr(p, …, memoria=runtime.memoria, …)
File "…\orquestrador\orquestrador.py", line 956,  in correr       recibo["INGRESSO"] = pela_entrada(itens, recibo, memoria=memoria, …)
File "…\orquestrador\orquestrador.py", line 244,  in pela_entrada r = ing.receber(itens, corrida=recibo, armazem=armazem, memoria=memoria, …)
File "…\coleta\ingresso.py",           line 1332, in receber      recibo = preservar(_corrida_completa(corrida), para_o_raw, armazem, …
File "…\guarda\preservar_coleta.py",   line 1303, in preservar    ja_la = conferir_o_que_ja_existe(run, plano, memoria)
File "…\guarda\preservar_coleta.py",   line 678,  in conferir_…   copia = memoria.copia_em(caminho)
File "…\guarda\memoria_postgres.py",   line 197,  in copia_em     linhas = self._linhas(
File "…\guarda\memoria_postgres.py",   line 151,  in _linhas      for linha in self._psql(sql).splitlines():
File "…\guarda\memoria_postgres.py",   line 117,  in _psql        r = subprocess.run(cmd, input=sql, capture_output=True, text=True,
  … subprocess.py:1538 _execute_child → _winapi.CreateProcess
FileNotFoundError: [WinError 2] O sistema não pode encontrar o arquivo especificado
##[error]Process completed with exit code 1.                       (14:16:33.08Z · processo 65700 · 7,33 s)
```

`cmd = ["psql", "-X", "-q", "-A", "-t", "-F", …, "-f", "-", url]`. O que
falhou foi o `CreateProcess` — o Windows não localizou um executável chamado
`psql` — e **não** uma ligação recusada: um servidor morto teria sido um
`psql` encontrado, a correr e a sair com código ≠ 0, e a linha seguinte
(`memoria_postgres.py:119-120`) levantaria `IOError` com o `stderr` do
`psql`. Foi outra exceção. Logo, o servidor descartável não foi sequer
interrogado.

### 17.5 · O que está provado e o que NÃO está sobre a causa

```
PROVADO      o Python do passo 6 não encontrou `psql` no PATH do job.
PROVADO      o 5a-IT escreveu a pasta do psql no GITHUB_PATH na forma POSIX:
             `echo "$PGBIN" >> "$GITHUB_PATH"`, com PGBIN=/c/Users/London1/orca/pgtmp/pgsql/bin
             (sintonia-scrap.yml:343,360). As migrations no MESMO passo não dependem disso:
             `PATH="$PGBIN:$PATH" bash motor/cadeia_canonica.sh migrations …` (:354).
PROVADO      o 5b (Sala gate) NÃO abre ligação: `exigir_canonica → estado_operacional → backend()`
             só lê variáveis e constrói `_Postgres(url)` (`sala_de_espera.py:741-799, 457-458`).
             O primeiro `psql` lançado a partir do Python em todo o job foi o do passo 6.
             UM PORTÃO QUE MEDE CONFIGURAÇÃO NÃO MEDE CONETIVIDADE.
NÃO PROVADO  o mecanismo. Reprodução local, só leitura, com ambiente limpo à maneira do runner
             (PowerShell sem variáveis MSYS, PATH mínimo com o prefixo POSIX, `bash --noprofile
             --norc`, depois `py`): `which psql` acha; `shutil.which("psql")` acha;
             `subprocess.run(["psql","--version"])` devolve 0 e «psql (PostgreSQL) 16.4».
             Ou seja: se o runner tivesse aplicado a linha do GITHUB_PATH ao passo 6, o psql
             teria sido encontrado. Nem o log do run (688 linhas) nem o Worker log do runner
             registam a aplicação (ou não) do prepend. Candidatos, sem prova: o runner não
             aplicou o prepend; aplicou-o numa forma que o CreateProcess não lê; outra coisa.
FACTO SOLTO  o Worker log mostra, no fim do 5a-IT (14:16:23Z), «Scan all processes … Kill process
             '72132'» — o runner matou a árvore do processo do passo que arrancou o postgres.
             Se o servidor sobreviveu até ao passo 6 NÃO foi medido nesta corrida (a minha
             amostra de 14:13:37Z é anterior). Não é a causa do crash (17.4), mas fica aberto.
```

### 17.6 · Produção

```
PRODUCTION_DB_WRITES = 0 · PRODUCTION_MIGRATIONS = 0 · PRODUCTION_SALA_WRITES = 0 · PRODUCTION_COLLECTION_RUNS = 0
```
Provado pelo caminho: `SINTONIA_SALA_DSN` (descartável) vence `SUPABASE_DB_URL`
em `sala_de_espera.py:741`; `persistencia.py` lê só `BANCO_DESCARTAVEL_URL`
e nunca cai para o cofre; e nenhum `psql` chegou a correr — logo nenhum banco,
de espécie nenhuma, foi contactado. Produção não foi consultada por este revisor.

### 17.7 · Teardown, medido na máquina (14:23:33Z)

```
TEARDOWN_STEP_EXECUTED       = YES   (9z-IT, always(), 14:16:34 → 14:16:36)
POSTGRES_PROCESS_LEFT_FOR_RUN = 0    (tasklist postgres.exe/pg_ctl.exe = 0; Win32_Process com o run id na
                                      linha de comando = 4, TODOS da cadeia de medição: 3 bash.exe + 1 powershell.exe
                                      — a armadilha do §14.7/§16.6, de novo; número honesto 0)
PORT_54329_LISTENING         = 0
TEMP_CLUSTER_LEFT            = NO    (_temp\pg-italia-35232024024 ausente)
TEMP_OPS_ROOT_LEFT           = NO    (_temp\ops-italia-35232024024 ausente — e com ele os bytes preservados
                                      «no ops-root», que o colheita.json declarava em STORAGE_LOCATION)
PEGADA FORA DO _temp         = `XX/it-t3-002/DOCUMENT/c5ae3bfe…-SA-16-09.pdf` e `data/colheita/italia/…` no
                               checkout do runner — ambos ignorados pelo Git (.gitignore:89,99); `git status`
                               do checkout: 0 linhas. O checkout do run seguinte apaga-os (§134, item 4).
```

### 17.8 · Ledger e remoto

```
data/collection-ledger/italy/observations.ndjson  antes 3ea37f88… (175 linhas) · depois 3ea37f88… (175)
                                                  no worktree E no checkout do runner (o recibo nunca foi escrito:
                                                  `guardar_recibo` vem depois do crash)
data/samples/RUN-MANIFEST.json (runner)           antes 89f3ce41… · depois 89f3ce41…
REMOTE_COLLECTION_HEAD                            35092152… antes e depois (o passo 8 disse NADA_MUDOU=YES)
TRACKED_LEDGER_UNEXPECTED_DELTA                   = NO
```

### 17.9 · Red team (agente separado, só leitura, 25 ataques)

| # | ataque | veredito | prova |
|---|--------|----------|-------|
| 1 | run não é a despachada | REFUTADO | `created_at 14:12:26Z` · dispatch 14:12:23Z · `run_number 8` · env `ops-italia-35232024024` no passo 6 |
| 2 | SHA não é o auditado | REFUTADO | `headSha 35092152…` = HEAD local = remoto |
| 3 | runner errado | REFUTADO | `RUNNER=SINTONIA-EAME-LOCAL` · caminhos `C:\actions-runner-eame\…` |
| 4 | egresso não IT (ifconfig.co diz US) | REFUTADO | o portão mede pelo ipinfo e só por ele (`rede.py:175`); `EGRESS_GATE: PASS` |
| 5 | portões depois da rede | REFUTADO | 5b/5c às 14:16:23-25; aquisição às 14:16:26-32 dentro do 6 |
| 6 | Supabase usada | REFUTADO | crash em `MemoriaPostgres(localhost:54329/descartavel)`; nenhum psql correu |
| 7 | PERSISTENCIA não DESCARTAVEL | REFUTADO (por inferência) | `MemoriaPostgres` só nasce no ramo DESCARTAVEL (`persistencia.py:145-150`) |
| 8 | memoria None | REFUTADO | `preservar_coleta.py:1302 if memoria is not None:` guarda o ponto do crash |
| 9 | banco_do_rastro None | REFUTADO (não exercido) | composto no mesmo ramo (`:148`) |
| 10 | RUN inexistente no banco | CONFIRMADO COMO FACTO | insert em `:1314`, depois do crash |
| 11 | RAW só em ficheiro | CONFIRMADO COMO FACTO | `XX/…SA-16-09.pdf` existe; `raw_asset` = 0 |
| 12 | raw_asset zero | CONFIRMADO COMO FACTO | idem |
| 13 | ID vindo de SHA | NÃO SE APLICA | nenhuma linha, nenhum id |
| 14 | storage inventado | REFUTADO | `ArmazemLocal.enviar` escreve bytes reais com guarda de caminho |
| 15 | DERIVED não executado | CONFIRMADO COMO FACTO | `:972` depois do crash |
| 16 | STRUCTURED não executado | CONFIRMADO COMO FACTO | `:988` |
| 17 | Admissão ≠ READY | NÃO SE APLICA | `:1008` nunca alcançado |
| 18 | Sala zero | CONFIRMADO COMO FACTO | idem |
| 19 | teardown falso | REFUTADO | medições do 17.7 |
| 20 | outro workflow confundido (system-map 35229862059 em curso) | REFUTADO | corre em runner da GitHub; não toca esta máquina |
| 21 | conclusion a esconder passo partido | REFUTADO | `failure` É o passo partido, com exit 1 real |
| 22 | REUSED chamado NEW | NÃO SE APLICA | nenhuma decisão de reuso chegou a existir |
| 23 | causa = servidor morto pelo kill do 5a-IT | REFUTADO | servidor morto ⇒ `IOError` com stderr do psql (`:119-120`); observado ⇒ `FileNotFoundError` do `CreateProcess` |
| 24 | 5b prova conetividade | CONFIRMADO: NÃO PROVA | só configuração (`sala_de_espera.py:741-799`) |
| 25 | prepend POSIX aplicado? | NÃO PROVADO | nenhuma linha de log; reprodução local não reproduz a falha |

`RED_TEAM_REPLAY_3_BLOCKERS = 0`. O red team apertou a frase da causa
(«psql não encontrado no PATH do job; mecanismo de raiz não provado») e
acrescentou o facto de a aquisição de rede ter acontecido antes do crash.

### 17.10 · Testes (portões estáticos, os mesmos dos §14/§16)

```
tests/test_porta_de_producao.py + tests/test_fase_italiana_no_workflow.py + tests/test_a_porta_cli_liga_o_banco.py
→ 79 passed · 1 failed (78 s) · a falha é a mesma, pelo nome
  (`NenhumEscritorAntigoSobrou::test_o_inventario_de_quem_fala_de_raw_asset_esta_fechado`, separador do Windows)
NEW_FAILURES = 0 · NEW_ERRORS = 0 · worktree depois dos testes: 0 ficheiros
interpretador: /c/actions-runner-2/_work/_tool/Python/3.12.10/x64/python.exe + site-packages emprestado de Python312
```

### 17.11 · O que este replay NÃO reescreve, e o que NÃO fez

- Não reescreve o §130 (a coleta aconteceu por outra porta), o §14 (replay 1),
  o §15 (o conserto existe e foi consumido) nem o §16 (replay 2).
- Não corrigiu código, workflow, teste ou guarda. Não disparou replay 4. Não
  correu orquestrador nem coletor à mão. Não tocou produção, migration LIVE,
  Intelligence, Portal, deploy ou trunk.
- Não recuperou os bytes do `SA-16-09.pdf` para o acervo: estão numa pasta
  ignorada do checkout do runner e o próximo checkout apaga-os. Isso é uma
  decisão de coordenação, não do revisor.

### 17.12 · Veredito

```
INDEPENDENT_WORKFLOW_CANARY_REPLAY_3       = FAIL
WORKFLOW_REAL_CANARY                       = FAIL
WORKFLOW_EXECUTED                          = YES
WORKFLOW_FLOW_OBSERVED                     = YES (observado a partir-se na primeira chamada ao psql)
SOURCE_TO_SALA_REAL_OBSERVED               = YES (§130, mantido)
CLI_POSTGRES_BINDING_OBSERVED_IN_WORKFLOW  = YES (ligado — e foi a ligação que rebentou)
COLLECTION_INTEGRATION_CANDIDATE           = NO
BLOCKER                                    = passo 6: `subprocess.run(["psql", …])` em `guarda/memoria_postgres.py:117`
                                             → FileNotFoundError [WinError 2]. O psql não está no PATH que o Python
                                             do job vê. Adquirido da rede: SIM. Preservado no banco: NÃO. Sala: 0.
BIG_COLLECTION_AUTHORIZED                  = NO
NENHUMA CORREÇÃO FUNCIONAL                 = feita por este replay
```
