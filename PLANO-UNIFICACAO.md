# PLANO-UNIFICACAO — Missão 5-PREP (só leitura, sem merge)

Medido em 22/09/2026 sobre refs locais depois de `git fetch`. Ferramenta:
`ferramentas/unificacao/censo_lanes.py` (só leitura; `git merge-file -p` em
temporários fora do repo). Saída integral: `ferramentas/unificacao/censo-2026-09-22.json`.
Nenhum merge, rebase, cherry-pick ou reset foi feito.

## 1. Lanes

| lane | ref | HEAD | entra? |
|---|---|---|---|
| ponte | ponte-curador-v1 | 2018ed6a | **BASE** |
| serviço (= abastecimento) | source-curator-service-v1 / abastecimento-bot-v1 | 779ac8f6 | SIM |
| diagnóstico | diagnostico-sala-v1 (worktree em micro-prep-v1) | 44c873ff | SIM |
| rotas | rotas-elegiveis-v1 | **88ce30a8** (era 46c517c5 no início desta medição — continua a correr) | SIM, medir de novo no fim |
| lote-76 | lote-76-v1 | db146ddb | NÃO em separado — é ancestral de diagnostico (0 commits exclusivos) |

Merge-bases e commits exclusivos (A só / B só):

| par | merge-base | só A | só B |
|---|---|---|---|
| ponte · serviço | 8bbea01c | 128 | 23 |
| ponte · rotas | 2e098f14 | 14 | 7 |
| ponte · diagnóstico | 14e4d4fb | 31 | 32 |
| ponte · lote76 | 14e4d4fb | 31 | 28 |
| serviço · rotas | 8bbea01c | 23 | 121 |
| serviço · diagnóstico | 8bbea01c | 23 | 129 |
| rotas · diagnóstico | 14e4d4fb | 24 | 32 |
| diagnóstico · lote76 | db146ddb | 4 | 0 |
| qualquer · produção | 30138cad | ~1080 | 18 |

Nota: `source-curator-service-v1` local = 779ac8f6, remoto = 41655f3a (o
fast-forward do coordenador ainda não foi publicado).

**Excluídas (e porquê):**
- `micro-collection-v1` (4fdabf82), `canonical-micro-v1` (4c0c62b3): já são
  ancestrais da ponte — 0 commits por trazer.
- `lote-76-v1`: contida em diagnostico-sala-v1.
- `ops/italy-forward-only-live` (remoto d43adc1b; local ffee246a à frente, não
  publicado): é a âncora de rollback da produção, linhagem separada desde
  30138cad (18 commits: livro de execuções do agendador + coletor
  operacional). Juntar produção ao trunk é outra missão e decisão do dono.
- `claude/sintonia-eame-repo-setup-xccfob` ("main" por nome): 45 commits só
  dela, parada desde 03/09, merge-base 96933996, 1209 commits atrás da ponte.
  Fora do âmbito.
- As outras ~90 worktrees: não tocam `curadoria/` nesta janela ou já estão
  contidas na ponte; não foram pedidas. Se a missão 5 quiser alargar,
  acrescentar a `LANES` no script e voltar a correr.

## 2. Censo ficheiro a ficheiro

Contra a base comum das 5 (8bbea01c):
`FILES_MULTI_LANE = 410 · IDENTICAL = 362 · ONE_SIDE = 0 · DIVERGENT = 48`
(gerado 16 · livro 17 · código 11 · doc 3 · know-how 1).

O número que interessa é **contra a base proposta** (a ponte), lane a lane —
ficheiros que a lane E a ponte mudaram desde o merge-base delas:

| lane | tocados nos dois | divergentes | código com conflito real |
|---|---|---|---|
| serviço | 38 | 34 (13 gerado, 10 livro, 7 código, 3 doc, 1 know-how) | **6** |
| diagnóstico | 19 | 19 (14 gerado, 2 livro, 1 código, 2 doc) | 0 |
| rotas | 14 | 14 (12 gerado, 1 doc, 1 know-how) | 0 |
| lote76 | 18 | 18 (contida no diagnóstico) | 0 |

### Regras de resolução

- **Gerado** (`system-map/data/*.generated.json`, `architecture.declared.json`,
  `italia-portale/client/system-map/state.generated.json`): não se junta.
  Fica o lado da base; no fim regera-se com `py system-map/scripts/correr_a_cadeia.py`
  (o gerador sozinho não varre — ver memória). `architecture.declared.json` é
  a excepção: é declarado à mão, une-se por peça (ID).
- **Livro/ledger** (LIFECYCLE-LEDGER/EVIDENCE/QUEUE, READY-*, SOURCE-ID-ALLOCATION,
  BRIDGE-LEDGER, DISCOVERY-*, RECONCILIACAO-V1, italy_contracts_curator.json,
  data/collection-ledger/*): reconciliação SEMÂNTICA por SOURCE_ID, classe
  antes do rótulo, nunca escolher um lado. A ferramenta já existe:
  `curadoria/reconciliar_livros.py` (na ponte; ausente no serviço). **Atenção:**
  ela lê B e B2 em commits FIXOS (f98f234c, 63b71421). Para a missão 5 tem de
  aceitar o livro do serviço (corte congelado, §5) como terceiro livro por
  parâmetro — REF fixo mata a ponte futura calada (memória
  ponte-do-curador-estado-sem-prova). `italy_contracts_curator.json` tem 3 blobs
  (dfa22abf / 9ad61e61 / b312d1ee): une-se por SOURCE_ID do contrato;
  contrato diferente para o mesmo ID = conflito listado, não resolvido à mão.
- **Código**: três vias. Conflitos reais (linhas no resultado de
  `merge-file`, ponte ← serviço):
  - `curadoria/descobrir.py` — 10 blocos (l. 90, 103, 116, 132, 213, 922, 1658, 1979, 2001, 2040)
  - `curadoria/supervisor.py` — 5 (362, 454, 588, 631, 648)
  - `curadoria/status_live.py` — 1 (42)
  - `curadoria/test_discovery.py` — 16 (5 … 836)
  - `curadoria/test_ponte_candidatas.py` — 6 (3, 17, 49, 89, 111, 174)
  - `curadoria/test_supervisor.py` — 1 (213)

  Juntam sem conflito: `worker.py` (serviço), `provar_ponte_curador.py`,
  `red_team_ponte_curador.py`, `reconciliar_livros.py` (diagnóstico/lote76).
  Origem provável dos conflitos: o serviço mexeu no discovery/supervisor
  (ADDENDUM-01..04, serviço contínuo, abastecimento) e a ponte também
  (§169, --saude, observador). Os testes em conflito resolvem-se DEPOIS do
  código, e corre-se a suíte com os dois conjuntos de provas.
- **Doc**: `curadoria/.gitignore` (união de linhas), `docs/fontes/INDICE-DE-FONTES.md`
  e `docs/operacao/CENSO-DAS-LIGACOES-DA-COLLECTION.md` (são censos: regerar
  se houver gerador; senão união por linha de fonte).
- **Know-how** (`SINTONIA-EAME-KNOW-HOW.md`, 842.783 bytes na ponte · 793.343 no
  serviço · 838.184 rotas · 818.322 diagnóstico): união de secções por §.
  **1 colisão de número:** §159 = «A PORTA EXISTIA — O QUE SECOU FOI A FILA A
  MONTANTE» (ponte/diag/rotas/lote76) vs «SAÚDE NÃO É PRODUTIVIDADE — A
  OBSERVABILIDADE DO SOURCE CURATOR» (serviço). O §170 do serviço não colide
  (a ponte vai até §169), mas a próxima secção nova de qualquer lane tem de
  ser §171+. Proposta: a do serviço passa a §159-B (ou ao próximo número livre)
  com nota «renumerada na unificação»; nenhuma secção apagada.

## 3. Base proposta

`PROPOSED_BASE = ponte-curador-v1 @ 2018ed6a`.

Porquê: contém já micro-collection, canonical-micro, o ponto de partida das
rotas (2e098f14) e do diagnóstico/lote-76 (14e4d4fb); tem 128 commits que o
serviço não tem contra 23 do serviço; traz `reconciliar_livros.py` (a
ferramenta da reconciliação); diagnóstico e rotas juntam-se a ela SEM
conflito de código. Qualquer outra base obrigaria a resolver mais. "main" por
nome está parada desde 03/09.

## 4. Ordem e portões

Trabalho num branch novo `unificacao-v1` a partir de 2018ed6a, numa worktree
nova (nunca na da ponte — o observador PID 14960 escreve nela, ver §5).
Medir a base de testes ANTES (a suíte já falha sozinha no Windows; comparar
por nome, e as duas bases — memórias o-trunk-ja-chega-vermelho e
suite-no-windows-ja-falha-sozinha). Nunca duas medições ao mesmo tempo.

| passo | junta | gate |
|---|---|---|
| 0 | — | suíte da base medida por nome; `correr_a_cadeia.py` → SYSTEM_MAP_CHECK=PASS na base |
| 1 | diagnóstico (inclui lote-76) | 0 conflitos de código; livros LIFECYCLE-LEDGER e RECONCILIACAO pela `reconciliar_livros.py`; suíte sem vermelho NOVO por nome; mapa regerado PASS |
| 2 | rotas (re-medir o HEAD) | idem; know-how sem colisão; canário das rotas (bancada, não produção) |
| 3 | serviço (779ac8f6, não o remoto 41655f3a) | 6 conflitos resolvidos à mão com lista; livros do serviço + corte congelado (§5) reconciliados por SOURCE_ID; test_abastecimento 14/14; test_supervisor/test_discovery/test_ponte_candidatas verdes; suíte sem vermelho novo |
| 4 | — | `provar_ponte_curador.py` e red team da ponte em cópia isolada com fila vazia (a suíte do curator lança worker real que bate à rede); prova do supervisor (`--saude`, uma_volta_sup observável) em cópia, sem tocar nos PIDs vivos |
| 5 | — | regenerar mapa pela cadeia, SYSTEM_MAP_CHECK=PASS, LOCAL==REMOTO |

Passar o serviço vivo para o branch unificado (parar/relançar supervisor) é
um passo À PARTE, depois do 5, e decisão do dono.

## 5. Os 5 ficheiros sujos do serviço vivo

Na worktree source-curator-service-v1: LIFECYCLE-LEDGER, LIFECYCLE-EVIDENCE,
LIFECYCLE-QUEUE, RED-TEAM-TELEMETRIA (escritos pelo bot) e `telemetria.py`
(só fim-de-linha CRLF — não é mudança; não se commita). Também nesta
worktree (ponte) o `LIFECYCLE-LEDGER-V1.json` está sujo (+485 linhas), escrito
pelo observador — não foi incluído em nenhum commit desta missão.

**Congelar sem parar o bot** (`LIVE_BOOK_FREEZE_PLAN`):
1. Cada livro é gravado atomicamente (`lifecycle._gravar`: temporário + fsync +
   `os.replace`), por isso copiar UM ficheiro dá sempre um ficheiro inteiro.
   Mas os três livros são gravados em momentos diferentes: o corte tem de ser
   coerente entre eles.
2. Copiar os 4 livros para fora (`%TEMP%\corte-livros-<hora>`), calcular sha256;
   esperar ~30 s; copiar outra vez. Se os 4 sha forem iguais nas duas leituras,
   o corte está parado entre voltas → aceitar. Se não, repetir (máx. 10).
3. Validar o corte sem rede: JSON abre; cada SOURCE_ID da fila existe no
   ledger; cada estado do ledger tem evidência (a régua do reconciliar).
4. Quem commita: **o coordenador**, numa worktree NOVA em branch
   `livros-servico-corte-AAAAMMDD` a partir de 779ac8f6 — nunca na worktree
   viva (commitar lá mexe no índice que o bot partilha). O bot continua a
   escrever; o que escrever depois do corte entra num corte seguinte ou na
   reconciliação final antes da troca.
5. A missão 5 reconcilia ESSE corte (ref fixo, com hash) — e o corte final
   repete-se imediatamente antes da troca do serviço.

## 6. Riscos e decisões do dono

Riscos:
- rotas ainda corre: o censo dela mudará (46c517c5 → 88ce30a8 durante esta medição).
- o bot continua a escrever: qualquer corte envelhece; por isso há corte final.
- `reconciliar_livros.py` com REF fixo não vê livros novos → tem de ser parametrizado antes.
- a suíte chega vermelha na base; "verde" só se mede por nome contra a base.
- a suíte do curator pode colher de verdade (rede) se corrida na worktree real.

**OWNER_DECISIONS (Luciano):**
1. Aceitar a ponte (2018ed6a) como base.
2. Renumeração do §159 do serviço (proposta: próximo número livre, com nota).
3. Quando parar o bot para o corte final e trocar o serviço para o branch unificado.
4. Se a produção (`ops/italy-forward-only-live`) e a "main" antiga entram numa missão posterior ou ficam como estão.
5. Publicar o fast-forward local do serviço (779ac8f6) no remoto antes da missão 5.
