# RELATORIO-UNIFICACAO — Missão 5: unificação real das linhas do Source Curator

Ramo `unificacao-v1` · worktree `orca/workspaces/eame-sintonia/unificacao-v1` ·
base 20c06500 (unificacao-plano-v1, contém a ponte 2018ed6a) · 22-23/09/2026.
Nenhuma coleta corrida. Nenhum serviço vivo tocado (supervisor PID 125352 e
observador PID 14960 continuam; os livros da worktree viva só foram LIDOS).

## Passos e commits

| passo | junta | commit |
|---|---|---|
| 1 | diagnóstico e22c2593 | 13436179 |
| 2 | rotas 3b5080b9 | f1c61481 |
| 3 | serviço 9a82197c (com gatilho ocioso) | 5881f7e9 |
| 4 | provas em cópia, suíte da base, know-how §174 | 4d14cc15 |
| 5 | mapa pela cadeia | 6b159d41, 91b5f38e |
| 5b | defeitos 7 e 8, metricas sincronizadas, este relatorio, mapa | FINAL_HEAD |

Não puxados (ainda a correr, entram depois como incremento): regua-t2-t12-v1,
worker-pendurado-v1, detector-capa-v1. **worker-pendurado-v1 já publicou §172**
no know-how — por isso o §159 do serviço foi para §173 (ver abaixo).

## ENTREGA

```
BASE_SUITE        = curadoria/ 315/315 · tests/ 4605 ok de 5013 corridos
                    (201 FAIL + 12 ERROR = 213 linhas vermelhas; 194 skipped; 1 expected failure)
                    medido em copia descartavel de 20c06500 (medir_suite.py)
UNIFIED_SUITE     = medido em copia de 91b5f38e (medir_suite.py):
                    curadoria/ Ran 469, FAILED 3 · tests/ Ran 5047, FAILED
                    (failures=548 contando subtestes, errors=12, skipped=194).
                    Por NOME de teste: curadoria/ 0 -> 3 vermelhos; tests/ 92 -> 96.
                    Depois da medicao, no commit final: os 3 de curadoria/ corrigidos
                    (defeitos 7 e 8 abaixo; test_supervisor + test_painel_pergunta_ao_so
                    + test_gatilho_ocioso 47/47) e test_metricas sincronizado
                    (metricas_canonicas --sync, DRIFT=0). A suite inteira NAO foi
                    corrida outra vez sobre o commit final (1 h): o que mudou depois
                    foi medido modulo a modulo.
NEW_RED_BY_NAME   = 4 testes, todos tests/test_fila_italia_decisoes:
                    test_a_fila_tem_as_241_e_nenhuma_ficou_sem_decisao,
                    test_as_25_recusas_de_14_09_estao_todas_revogadas_na_fila,
                    test_em_analise_diz_sempre_o_que_falta,
                    test_nenhuma_recusa_viva_assenta_em_429_ou_muro.
                    HERDADOS do servico, nao criados pela juncao: no proprio
                    9a82197c este ficheiro da 289 linhas vermelhas. A discovery do
                    servico escreveu 235 candidatas novas (241 -> 476) em
                    candidatas/FONTES-CANDIDATAS.json sem O_QUE_FALTA. Nao afrouxado.
                    Decisao pendente (dono/coordenador): o teste fixa a coorte de 241
                    de 14/09 — ou passa a ler so essa coorte, ou a discovery passa a
                    escrever O_QUE_FALTA. Tambem ja vermelhos por nome na base e com
                    mais subtestes agora: test_a_linhagem_do_ready_e_do_raw_asset
                    (vem do diagnostico: 66 vermelhas no proprio e22c2593).
CONFLICTS_RESOLVED = 63 ficheiros em conflito no git (diagnostico 16, rotas 15, servico 32):
                    codigo 6 ficheiros / 10 blocos (supervisor 7, status_live 1,
                    test_supervisor 2) + 3 add/add juntados pela base real 63b71421
                    com 0 blocos; livros 11 (9 do servico, 2 do diagnostico); gerados/censos/doc/know-how o resto
HIDDEN_DEFECTS_FIXED = 8: os 5 do plano + 3 novos, todos por causa do servico mais novo:
                    6. red_team_telemetria atacava «telemetria.py» por nome de ficheiro;
                    7. a escolha 4 do resolvedor (liveness pergunta se o PID e python)
                       deixou de se aplicar CALADA: as linhas sairam do bloco de conflito;
                       agora aplica-se ao ficheiro inteiro e rebenta se nao achar o alvo;
                    8. os ajudantes do crashloop da ponte «morriam» com rc 0, que desde o
                       gatilho ocioso e saida limpa: o bloqueio nunca chegava.
AUTH_BLOCK_TAUGHT = YES — 5 fontes (IT-T12-035/046/055/072/078) saem de UNKNOWN
                    para CAPABILITY_BLOCK; o rotulo AUTH_BLOCK fica no livro;
                    2 testes novos, mutante morto
TELEMETRIA_RENAME = curadoria/telemetria.py -> curadoria/telemetria_do_curador.py
                    chamadores (todos em curadoria/): cartao_de_fonte.py, status_live.py
                    (2 imports tardios), test_cartao_de_fonte.py, test_telemetria.py,
                    red_team_telemetria.py (7 alvos por texto).
                    Fora do repo, medidos e SEM chamador: orca-tools/operacao_live.py,
                    verificar_ciclo_ocioso.sh (chama supervisor.py --estado),
                    vigilante_lote76/materia/ponte.sh, tarefas agendadas do Windows.
                    O codigo vivo do servico importa-a de dentro de curadoria/; com a troca
                    de codigo passa a telemetria_do_curador junto — nao ha chamador externo.
CANARY_OWNER      = a regua dos quatro passos (ready_split.passos_da_promocao),
                    chamada pelo worker NA HORA da promocao; o canario do worker so traz a prova.
                    Resolveu sem os quatro passos = PASS_PARCIAL -> CONTRACTED_CANARY_FAILED
READY_CHANGED     = 0 linhas reescritas no livro (append-only) · 15 das 111 READY
                    vieram do canario do worker e NAO passam na regua: com a lei nova
                    nao teriam sido promovidas. COLLECTION_ELIGIBLE nao muda (19): o
                    portao ja exigia a regua.
RECONCILED_BOOKS  = (corte congelado do servico 23/09 03:07Z, ledger sha256 c3888c0b…)
                    READY_CURRENT 23 · READY_LEGACY 88 · RETRY 13 · DEGRADED 18 ·
                    POLICY_BLOCK 69 · CAPABILITY_BLOCK 35 · UNKNOWN 34 · NOT_READY 384
                    = 664 identidades. 256 transicoes acrescentadas, 186 provas
                    importadas, 0 cadeias ilegais, 2.a passagem planeia 0.
PONTE_PROOF       = PASS (copia) — ENTRA/NUNCA_ENTROU/SAI verdadeiros, LEGACY_LEAK 0,
                    idempotente; red team da ponte 17 ataques, 17 mortos, SURVIVORS 0
SUPERVISOR_PROOF  = PASS (copia) — fila vazia: IDLE, gatilho chamado 1 vez, 0 workers
                    lancados; worker que sai com rc 0: IDLE, 0 crashes contados;
                    --estado le; ponte_automatica --saude diz NUNCA_CORREU (verdade na copia)
SYSTEM_MAP_CHECK  = PASS (correr_a_cadeia REGERAR + VALIDAR; PORTOES_POS_COMMIT IGUAL)
FINAL_HEAD        = o HEAD de origin/unificacao-v1 (um ficheiro nao pode conter o hash do commit que o contem; o valor vai na entrega ao coordenador)
REMOTE_HEAD       = o HEAD de origin/unificacao-v1 (um ficheiro nao pode conter o hash do commit que o contem; o valor vai na entrega ao coordenador)
```

### A contagem 450/451 contra 445/446 (pedido do briefing)

O número certo é **450 de 451**: o `unittest` correu 451 e reprovou 1
(`Ran 451 tests … FAILED (failures=1)`). O JSON dizia 445/446 porque o leitor do
ensaio só reconhece um teste quando a linha `nome (modulo) ... ok` sai inteira;
5 testes escrevem no ecrã a meio dessa linha e sumiram da contagem por nome (na
base, 1 pela mesma razão: 310 contra 311). Nesta missão, «ok/total» vem do resumo
do `unittest`, e a comparação por nome faz-se só pelas linhas `FAIL:`/`ERROR:`.

## O que mudou em relação ao plano

- **Serviço 9a82197c (e não 779ac8f6).** Traz o gatilho ocioso: rc 0 do worker é
  saída limpa. O resolvedor ganhou um bloco: o `test_crash_com_progresso` usa o
  ajudante `_popen` da ponte com `sys.exit(1)` do serviço — com `pass` (rc 0) o
  teste deixava de medir uma morte.
- **Livros LIFECYCLE-LEDGER no passo 1.** Ponte e diagnóstico tinham aplicado a
  mesma reconciliação a partir de cópias diferentes do livro do bot. Unido por
  estado (`unir_ledger.py`): 77 aplicadas, 70 absorvidas, 9 em conflito (a ponte já
  estava mais à frente — as 9 são passos intermédios que o diagnóstico registou e
  a ponte já tinha ultrapassado), só acréscimos.
- **Livros do serviço no passo 3** (`unir_livros_do_servico.py`, por chave):
  BRIDGE-LEDGER 147+205=352 · DISCOVERY-VISITED 244 visitados / 828 rejeitados ·
  LIFECYCLE-EVIDENCE 1445 (485 diferiam só no carimbo IMPORTADO_DE da ponte — o
  mesmo facto) · contratos 283 · READY-BATCHES 5. **13 conflitos listados** em
  `m5/livros-passo3-servico.json`: 9 contratos (IT-T7-017, IT-T10-018, IT-T12-013,
  IT-T5-049, IT-T7-033, IT-T10-022, IT-T7-041/042/043) ficam com a rota
  AQUISICAO-DETALHE da ponte, mais nova; 3 domínios visitados ficam com a data da
  ponte; o READY-BATCH-002 do serviço (8 fontes, 22/09) era outro lote com o mesmo
  número — entra como READY-BATCH-005. A fila fica a do serviço: as 28 tarefas só da
  ponte estavam todas DONE.
- **§159 do serviço → §173**, não §172.
- **Canário das rotas (passo 2): NÃO corrido.** Bate à rede, e a missão proíbe
  coleta; a relevância e o censo das rotas entraram como estavam provados na lane.

## SWITCH_PLAN — para o coordenador trocar o serviço vivo

Pré-condição: aviso ao coordenador (decisão 3 do dono). O bot pára por poucos minutos.

1. **Medir antes** (na worktree viva `source-curator-service-v1`):
   `py curadoria/supervisor.py --estado` (guardar); `git status --short` (os 10 sujos);
   PIDs vivos: supervisor 125352, observador 14960 (`ponte_automatica.py --servir
   --intervalo 20`, a correr na worktree `ponte-curador-v1`).
2. **Parar:** criar `curadoria/PARAR.flag` na worktree viva; esperar o supervisor
   sair (o worker sai limpo, rc 0); confirmar por `tasklist` que 125352 e qualquer
   `ciclo_continuo.py` já não existem. Parar o observador 14960 (é um servidor em
   laço; matar o PID exacto, nunca por substring).
3. **Corte final** (o bot já parado, deve bater à primeira):
   `py ferramentas/unificacao/congelar_livros_do_servico.py --origem <viva>/curadoria
   --destino %TEMP%\corte-final-<hora>`. Guardar também, fora do Git, cópia de
   `candidatas/FONTES-CANDIDATAS.json`, `BRIDGE-LEDGER-V1.json`,
   `DISCOVERY-VISITED.json`, `READY-BATCHES-V1.json`, `SOURCE-ID-ALLOCATION-V1.json`
   da viva (os sujos que o corte não leva), com sha256.
4. **Commitar o corte** numa worktree NOVA, branch `livros-servico-corte-AAAAMMDD` a
   partir de 9a82197c (§5.4 do plano; nunca na viva).
5. **Reconciliar na unificação** (worktree unificacao-v1):
   - `py curadoria/reconciliar_livros.py --livro-servico <corte-final>
     --livro-ponte curadoria/LIFECYCLE-LEDGER-V1.json --aplicar` e conferir
     «SEGUNDA_PASSAGEM_PLANEIA 0» e «CADEIAS_ILEGAIS_NAO_IMPORTADAS []»;
   - `py ferramentas/unificacao/unir_livros_do_servico.py HEAD livros-servico-corte-AAAAMMDD
     --escrever --relatorio ...` (fila, evidência, bridge, visitados, contratos, lotes);
   - `py curadoria/interface_collection.py` (READY-SOURCES);
   - commit; `correr_a_cadeia.py REGERAR` → `VALIDAR` → commit → `PORTOES_POS_COMMIT`;
     push; LOCAL == REMOTO.
6. **Trocar o código na pasta viva** (o observador tem `LANE_DO_BOT` escrito com o
   caminho `…/source-curator-service-v1`: a pasta NÃO muda de nome):
   na viva, `git checkout -- .` só DEPOIS de conferir que os sha256 do corte batem
   com os ficheiros sujos; `git switch -c source-curator-service-v2 <FINAL_HEAD
   do passo 5>` (unificacao-v1 já está em uso noutra worktree, não pode ser
   checkout duas vezes). Os ficheiros de runtime ignorados (SUPERVISOR-STATE,
   RUN-LOG, TELEMETRY-CHECKPOINT-HISTORY) ficam.
7. **Relançar:** apagar `PARAR.flag`; na viva, com o MESMO python
   (`C:\actions-runner-2\_work\_tool\Python\3.12.10\x64\python.exe`),
   `curadoria/supervisor.py` em segundo plano. Observador: `py
   curadoria/ponte_automatica.py --servir --intervalo 20` a partir da worktree
   unificacao-v1 (a ponte-curador-v1 fica com código velho).
8. **Medir depois** (5-10 min): `supervisor.py --estado` → SOURCE_CURATOR_SERVICE
   RUNNING ou IDLE, SERVICE_DIAGNOSIS coerente, HEARTBEAT_FRESH; RUN-LOG com
   VOLTA e, no fim da fila, `WORKER_OCIOSO_SAIU` → `WORKER_SAIU_LIMPO` sem
   CRASHES_SEM_PROGRESSO; nenhum `AttributeError` de telemetria no RUN-LOG;
   `ponte_automatica.py --saude` → a trabalhar; `interface_collection.py` →
   COLLECTION_ELIGIBLE não desce (19 nesta medição); PASS_PARCIAL aparece nos
   RESULTADOS da volta (lei nova do canário) — esperado, não é avaria.
9. **Desfazer** (se 8 falhar): `PARAR.flag`; na viva `git switch
   source-curator-service-v1` (9a82197c); repor os livros do corte final (copiar de
   volta, conferir sha256 contra CORTE.json); apagar PARAR.flag; relançar o
   supervisor; relançar o observador na ponte-curador-v1. Nada do ramo unificado
   se apaga.

## Riscos que ficam

- 26 bloqueios «rejeitados por velhos» e 34 UNKNOWN continuam por remedir (pedem rede).
- A lei do canário muda o que o bot escreve: fontes YouTube (sem gate de detalhe)
  deixam de subir a READY pela via do worker; ficam CONTRACTED_CANARY_FAILED com
  o porquê. Hoje já não eram elegíveis; o número de READY vai parar de crescer por
  READY que o portão recusava.
- A fila unida é a do serviço à hora do git; a viva já tem mais. É o passo 5 do
  SWITCH_PLAN que a põe em dia.

## RETIRADA_POR_DECISAO (aviso do coordenador, G1 @ 8946d898)

Medido: a palavra `RETIRADA_POR_DECISAO` não existe em nenhum ficheiro desta linha
(`git grep` = 0). Vem de desbloqueio-coorte-v1, que não entrou nesta passagem.
Fica para a 2.ª passagem, junto com essa lane: o Collection Gate
(`curadoria/collection_gate.py`) e a tabela do coletor
(`regras/italy_contracts_onboarded.json`) têm de recusar a marca com motivo
explícito, com teste que morda (mutante: tirar a recusa → o teste reprova).

## 2.ª passagem (pedida pelo coordenador)

worker-pendurado-v1 (14f68f30, em produção, traz §172), discovery-sementes-v2
(5b8f400c, em produção), desbloqueio-coorte-v1 (pacote do cutover),
catalogo-proposta-v1 (0644a916), regua-t2-t12-v1, detector-capa-v1.

---

# 2.ª PASSAGEM — UNIFICACAO-V1-B (23/09/2026)

Base 2cfdc3b3 (1.ª passagem aceite). Nenhuma coleta corrida; nenhum serviço vivo tocado.
Não puxados, de propósito: fila-windows-v1 (M2e), multilingue-v1 (L1), ponte-prova-viva-v1 (B1).
As secções «RETIRADA_POR_DECISAO» e «2.ª passagem» acima ficam como registo da 1.ª; o que
aconteceu com elas está aqui.

| passo | junta / faz | commit |
|---|---|---|
| 1 | micro-prep-v1 75185e09 (resumo do gabarito) | 2679843e |
| 2 | qualify-semantico-v1 5aaf7810 (M2d worker pendurado + C1 sementes + know-how S1) | 283a6ece |
| 3 | desbloqueio-coorte-v1 06d25deb (detector-capa, receitas, coorte-micro, pacote G1) | b74d6ccc |
| — | RETIRADA_POR_DECISAO no portão e no coletor | 8ae62ec7 |
| 4 | catalogo-proposta-v1 0644a916 (régua T2/T12 + PROPOSTA-CATALOGO-V1) | 718b5863 |
| 5 | provar_em_copia com ensaios reais, métricas, mapa pela cadeia | 7177cdb9, 5a16d077 |
| 6 | este relatório, know-how 174-1, mapa | FINAL_HEAD |

## ENTREGA-B

```
PONTAS_JUNTAS     = 4
CONFLITOS         = codigo: 1 bloco (curadoria/supervisor.py, _ultimo_heartbeat): fica a
                    estrutura do servico (batimento = max(diario, pulso por tarefa)) com a
                    docstring da ponte em _heartbeat_do_diario; o filtro ORIGEM=SUPERVISOR
                    ja estava no corpo comum e fica. Know-how: 3 blocos, uniao por
                    significado (tabela abaixo). Gerados e censos: lado da base, regerados
                    pela cadeia. Livros: 0 conflitos (as 4 pontas nao commitaram livros do bot).
HIDDEN_DEFECT     = 9.o da unificacao: o pulso real do worker (WORKER-HEARTBEAT.json) era
                    escrito por 3 ficheiros de teste e lido por 7. Numa pasta com o bot vivo
                    faria um worker pendurado parecer vivo. 10 ficheiros corrigidos; a guarda
                    do isolamento protege o ficheiro e exige W.PULSO / S.PULSO redirecionados.
BASE_SUITE        = 2cfdc3b3: curadoria/ Ran 469, OK · tests/ Ran 5047, 93 testes vermelhos por nome
UNIFIED_SUITE     = 5a16d077: curadoria/ Ran 487, OK · tests/ Ran 5103, 93 testes vermelhos por nome
NEW_RED_BY_NAME   = 0 (nenhum novo, nenhum sumiu)
RETIRADA_GATE     = YES. collection_gate.avaliar recusa com MOTIVO RETIRADA_POR_DECISAO (le o
                    contrato do livro corrente, nunca o git); regras/italy_contracts.mjs nao faz
                    contrato de linha retirada e expoe RETIRADAS_POR_DECISAO.
                    tests/test_retirada_por_decisao.py: 4 testes (o coletor corre numa copia
                    de regras/). Mutacao: 2 mutantes, 2 mortos.
NOTA_235          = NAO SEI + proposta (abaixo). O teste continua a olhar TODAS.
PACOTE_G1_ENSAIO  = 1.a passagem 73 (livro 68 + tabela 5) / 2.a passagem 0, sobre copia do
                    livro vivo (servico @ 409eeb8e, sha 9c14afed...) e a tabela desta linha.
                    0 invariantes quebrados. Com o livro ensaiado, o portao recusa 5 READY por
                    RETIRADA_POR_DECISAO (IT-T12-041/057/074/086/095); elegiveis 19 -> 16
                    (sai IT-T5-041 porque o pacote lhe muda a rota depois da promocao, regua
                    LEGACY; entra IT-T7-100 porque o livro vivo tem um contrato que esta linha nao tem).
PONTE_PROOF       = PASS (copia; red team 17/17, SURVIVORS 0)
SUPERVISOR_PROOF  = PASS (copia)
GATILHO_OCIOSO    = PASS (ensaio real, copia sem .git: 9/9 assercoes)
WORKER_PENDURADO_PROOF = PASS (ensaio real: PENDURADO=false, 0 bytes de stdout, WORKER_OCIOSO_SAIU)
DISCOVERY_PROOF   = PASS (test_discovery_sementes + gatilho + pendurado: 28/28 na copia)
SYSTEM_MAP_CHECK  = PASS
```

## NOTA_235 — porque é NÃO SEI, e a proposta

Procurado pela ordem pedida:
- **Bíblia** (BIBLIA-CANONICA-DA-COLETA.md e docs/biblia/): a COL-LAW-053 define a escada
  CANDIDATA → REGISTADA → CONTRATADA → AUTOMÁTICA; nenhuma lei exige `O_QUE_FALTA` numa
  candidata EM_ANALISE.
- **Know-how**: nenhuma secção o exige.
- **System Map**: a regra vive só no código de UMA peça, `candidatas/decidir_fila_italia.py`
  («REGRA 3 · o resto fica EM_ANALISE, com o que falta escrito»), e em
  `docs/arquitetura/BOT-DE-FONTES-V2-PLANO.md`, que se declara «NÃO É LEI».

Medido: as 235 foram registadas pela discovery (205 por `curadoria/crawl_sementes`, 30 por
`descobrir.py`) em estado CANDIDATA. Quem as põe em EM_ANALISE é a **ponte**
(`curadoria/ponte_candidatas.py`, linhas 200 e 215), quando cria a tarefa QUALIFY, sem
escrever o que falta. 144 delas têm ainda MOTIVO_DA_RECUSA preenchido com ESTADO EM_ANALISE:
uma linha que diz duas coisas.

Os outros 3 vermelhos do mesmo ficheiro não são desta nota. Fixam a coorte de 241 de 14/09
(«se mudar, tem de mudar com motivo escrito») e as 25 recusas revogadas a 14/09. Dessas 25,
o serviço voltou a pôr as redes sociais em RECUSADA (FACEBOOK_CAPABILITY_BLOCK), mas deixou
no PORQUE o texto «RECUSA ANTERIOR REVOGADA» e na EVIDENCIA a sonda de 429.

**Proposta (decisão do dono):**
1. Elevar a REGRA 3 a lei (Bíblia ou know-how): «EM_ANALISE diz sempre o que falta».
2. Sendo lei: quem põe EM_ANALISE escreve a nota. É a ponte, na mesma linha em que muda o
   estado: `O_QUE_FALTA = "QUALIFY pelo curator (tarefa T…)"`, ou, para tipo desconhecido, o
   motivo que ela já escreve no BRIDGE-LEDGER. O teste continua a olhar todas.
3. Separar a coorte da população: o teste das 241 passa a ler a coorte de 14/09 pela
   DECIDIDA_EM (é o que ele diz medir); as novas são outra população, com a sua própria prova.
4. Redes sociais: CAPABILITY_BLOCK é «fonte boa, sem capacidade», não recusa. Deviam ter o seu
   próprio estado, e não RECUSADA com um PORQUE que diz o contrário.

## KNOW_HOW_TABLE (§170 em diante, nesta linha)

| § | título | origem | nota |
|---|---|---|---|
| §170 | REPETIR O QUE NADA MUDOU NÃO É PERSISTÊNCIA | serviço (abastecimento) | — |
| §171 | SAIR NÃO É MORRER | serviço (gatilho ocioso) | — |
| §172 | UM CANO SEM LEITOR NÃO É UM LOG, É UM TRAVÃO | worker-pendurado-v1 | — |
| §173 | REGISTADO NÃO É RASTEJADO | discovery-sementes-v2 | — |
| §174 | A MESMA RECONCILIAÇÃO DUAS VEZES NÃO SÃO DOIS FACTOS | esta unificação | + 174-1 (2.ª passagem: o pulso) |
| §175 | SAÚDE NÃO É PRODUTIVIDADE | serviço (era §159) | renumerada duas vezes: §159 → §173 (1.ª) → §175 (2.ª) |
| § (sem número) | A PEÇA EXISTIA E NÃO ESTAVA LIGADA | qualify-semantico-v1 (S1) | fica sem número, como veio |
| 168-16 a 168-18 | régua T2/T12 | catalogo-proposta-v1 | subsecções do §168 |
| RECEITAS-1/2, COORTE-1, DESBLOQUEIO-1 | — | desbloqueio-coorte-v1 | subsecções sem número, depois do §167 |

Nenhuma secção apagada. Próximo número livre: **§176** — medir de novo antes da 3.ª passagem.

## SWITCH_PLAN — actualizado na 2.ª passagem

**Medido agora (23/09):** supervisor **PID 103316** (arrancou às 02:28; já não é 80704);
observador **PID 14960** (`ponte_automatica.py --servir --intervalo 20`, em ponte-curador-v1);
a pasta viva está em **409eeb8e = fila-windows-v1 (M2e)**, com 11 ficheiros sujos.

⚠️ **Condição nova.** O serviço vivo já corre o M2e, que ficou fora desta passagem. Trocar
para `unificacao-v1` agora **tiraria o M2e de produção**. Ou se junta fila-windows-v1 primeiro
(3.ª passagem), ou o dono aceita essa regressão por escrito.

Os 9 passos da 1.ª passagem continuam, com estas mudanças:
1. **Medir na hora** os PIDs (tasklist, pelo PID exacto, nunca por substring) e o HEAD da
   pasta viva. Os deste relatório já mudaram duas vezes durante a missão.
2. Parar pela `PARAR.flag`; confirmar que o supervisor medido no passo 1 saiu.
3. Corte final com o bot parado, mais cópia com sha256 de `italy_contracts_curator.json`
   da pasta viva e da tabela `regras/italy_contracts_onboarded.json`.
4. **Pacote G1 com o bot parado**, sobre o livro do corte e a tabela da linha unificada:
   `py scripts/desbloqueio/aplicar_desbloqueio.py --livro=<corte>/italy_contracts_curator.json
   --tabela=regras/italy_contracts_onboarded.json --escrever`. Correr outra vez e exigir
   `ESCRITO: 0`. Ensaiado hoje: 73 → 0.
5. Reconciliar (`reconciliar_livros.py --livro-servico … --aplicar`), unir os livros
   (`unir_livros_do_servico.py`), `interface_collection.py`, cadeia, push, LOCAL == REMOTO.
6. Trocar o código na pasta viva (a mesma pasta, ramo novo no HEAD final).
7. Relançar o supervisor e o observador (o observador a partir de unificacao-v1).
8. Medir o de antes e mais: `WORKER-HEARTBEAT.json` a avançar por tarefa; o motivo
   `RETIRADA_POR_DECISAO` no portão para as 5 retiradas; elegíveis perto de 16.
9. **Desfazer: volta ao HEAD medido no passo 1** (hoje seria 409eeb8e, não 9a82197c), com os
   livros do corte (conferir sha256) e a tabela copiada no passo 3.
