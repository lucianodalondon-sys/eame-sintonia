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

| medição | valor |
|---|---|
| `CURRENT_BRANCH` | `claude/it-collection-sala-v1` |
| `LOCAL_HEAD` = `REMOTE_COLLECTION_HEAD` | `7d75e25a` — nada por publicar |
| `REMOTE_TRUNK_HEAD` real | `c88690ca` — **mudou** desde a fotografia da coordenação (`9d6dcbbd`) |
| topologia | `9d6dcbbd` (o trunk esperado) **é ancestral** desta branch; o trunk oficial andou 45 commits com missões alheias (sensores, creators). Escopo auditado: os **10 commits** `9d6dcbbd..7d75e25a` |
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
