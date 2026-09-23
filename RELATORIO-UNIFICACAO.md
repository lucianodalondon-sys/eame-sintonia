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

---

# 3.ª PASSAGEM — UNIFICACAO-V1-C (23/09/2026)

Base c64316d6 (2.ª passagem aceite). Nenhuma coleta corrida; nenhum serviço vivo tocado.
Não puxados, de propósito: recollection-prova-v1 (R1), quarentena-naosei-v1 (Q1),
cutover-ensaio-v1 (X1), micro-caminho-v1 (A1).

| passo | junta / faz | commit |
|---|---|---|
| 1 | sementes-travao-v1 075501a0 (M2e fila windows + S2/S3 decisão semântica + S4 travão) | 238c5609 |
| 2 | multilingue-v1 9bf91789 (L1) | 1d902726 |
| 3 | contrato-unico-v1 808d554f (B1 prova viva, B2 promoção/despromoção, B3 contrato único) | a515d2ce |
| 4 | listing-detail-v3 a05d0bbe (LD1-LD3, aditamento V3, politica_nao_sei desligada) | 2abde1dd |
| — | D13 (opção B) | 4dcb26be |
| — | know-how §176-§191 | 7045cb0f |
| — | mapa: 4 peças duplicadas unidas; cadeia | 8fe122cb |
| — | provas da 3.ª passagem no provar_em_copia; este relatório; mapa | FINAL_HEAD |

## ENTREGA-C

```
PONTAS            = 4
CONFLITOS         = codigo 2 blocos + 4 extensoes:
                    · supervisor.py (liveness): o do servico (NAO SEI do tasklist fica
                      visivel) + a pergunta da ponte «o PID e python?» nos dois PIDs;
                    · test_supervisor.py: fica a classe Isolado da ponte (ja isola fila,
                      livro, lock, estado, PARAR, diario e pulso);
                    · aplicar_desbloqueio.py: 4 blocos B3 sobre o G1, todos extensoes
                      (assinatura do planear, retorno, escrita do livro do bot) — nenhuma
                      linha da base perdida; a V3 (LD) juntou limpo por cima.
                    Declarado: 1 lista de ficheiros da mesma peca (uniao).
                    Know-how: 6 blocos, uniao por significado.
                    Gerados e censos: lado da base, regerados pela cadeia.
DEFEITOS ESCONDIDOS = 2 novos (10.o e 11.o da unificacao):
                    10. o log do worker (WORKER-STDOUT.log, novo no M2e) era escrito por
                        test_gatilho_ocioso; test_decisao_semantica escrevia o pulso real e
                        deixava a pasta temporaria. Guarda: novo ficheiro + regra S.WORKER_LOG.
                    11. o enxerto do G1 na B3 declarou 4 pecas do mapa DUAS vezes
                        (C-DESBLOQUEIO-PACOTE, C-COORTE-MICRO-FUNIL, C-RECEITAS-PROPOSTA,
                        C-DETECTOR-CAPA-GABARITO): unidas, sem perder ficheiro nem texto.
SUITE antes       = c64316d6 (codigo igual a 5a16d077, medido): curadoria/ Ran 487 OK ·
                    tests/ Ran 5103, 93 testes vermelhos por nome
SUITE depois      = 8fe122cb: curadoria/ Ran 572 OK · tests/ Ran 5139, 91 testes vermelhos por nome
NEW_RED_BY_NAME   = 0. Sairam 2 (D13): test_a_fila_tem_as_241... e test_em_analise_diz_sempre...
PROVAS_COPIA      (8fe122cb, copia descartavel; ensaios numa segunda copia sem .git)
  ponte                         PASS  ENTRA/NUNCA_ENTROU/SAI; red team 17/17, SURVIVORS 0
  ponte B2 promocao/despromocao PASS  fotografia B1-SNAPSHOT-20260923T051430Z: elegiveis
                                      8 -> 20 (entram 20, saem 8); ficheiros reais intocados
  supervisor                    PASS  fila vazia -> IDLE, 0 workers; rc 0 nao e crash
  worker pendurado              PASS  ensaio real: PENDURADO=false, 0 bytes de stdout
  gatilho ocioso                PASS  ensaio real: 9/9 assercoes
  fila windows (leitor agressivo) PASS ensaio real: 1 worker de cada vez, 0 PermissionError
  discovery sementes + travao   PASS  test_discovery_sementes, test_travao_sementes
  decisao semantica             PASS  test_decisao_semantica + test_pais_das_candidatas;
                                      fotografia: 18 IT decididas / 7 fora de IT / 156 NAO SEI (181)
  multilingue                   PASS  test_admissao_multilingue. A re-medicao do gabarito
                                      (5/6 SIM, IT_VERDICTS_CHANGED 0) NAO foi re-corrida: a
                                      tabela de juncao nao esta no repo. admissao/ tem 0 linhas
                                      de diferenca contra 9bf91789, onde foi medida.
  pacote G1 blocos 1-3 + V3     PASS  1.a passagem 76 / 2.a 0 (abaixo)
  RETIRADA                      PASS  test_retirada_por_decisao
  modulos de prova juntos: 189/189
KNOW_HOW_TABLE    = abaixo
PACOTE_G1         = 1.a 76 (livro 66 + tabela 4 + livro do bot 6) / 2.a 0. Livro do portao =
                    copia desta linha; livro do bot = copia do vivo (075501a0, sha 70dfb300...);
                    --d10=A. 0 invariantes quebrados. Com o livro ensaiado: portao 19 -> 16
                    elegiveis, 5 recusadas por RETIRADA_POR_DECISAO.
SYSTEM_MAP_CHECK  = PASS
```

## D13 (opção B) — aplicada

- **(1)** O teste das 241 olha **só** o grupo de 14/09, escrito no próprio teste:
  `DECIDIDA_EM = 2026-09-15`, a decisão da qualificação de 14/09 — 241 candidatas.
  Mutação: tirar a nota a CAND-0013 → o teste reprova.
- **(2)** As novas contam-se (grupo + novas = TOTAL = 476) e ficam à vista: sem nota, nunca
  PROMOVIDA, sem SOURCE_ID. Nota genérica copiada para várias → reprova (mutação). Nenhuma
  nota foi escrita para encher.
- **(3)** Sem capacidade não é recusa: a ponte escreve `CAPABILITY_BLOCK` (com
  `MOTIVO_DO_BLOQUEIO`) e o estado entra no vocabulário da porta. As 6 linhas Facebook já
  escritas foram corrigidas por `ferramentas/unificacao/aplicar_d13_capacidade.py`
  (guarda o estado e o motivo anteriores; idempotente). Mutações no código e no dado → reprovam.
- **Continua vermelho, fora da D13, e já o era na base:** 16 das 25 recusas revogadas a 14/09
  voltaram a RECUSADA por **POLICY** (LinkedIn 3, Instagram 13), e 25 RECUSADA POLICY citam
  na EVIDENCIA a sonda de 429 de 14/09. São duas regras a dizer coisas diferentes («não se
  recusa o que ninguém leu» contra «os TOS proíbem»). Proposta: a mesma forma da D13 — POLICY
  com estado próprio e a evidência da política no lugar da sonda. **Decisão do dono.**
- Se a falta de nota travar o caminho, volta ao dono como proposta de lei (D13). Medido
  nesta passagem: não há nenhum consumidor que leia `O_QUE_FALTA` para decidir.

## KNOW_HOW_TABLE (final, §170-§191)

| § | título (abreviado) | origem |
|---|---|---|
| §170 | REPETIR O QUE NADA MUDOU NÃO É PERSISTÊNCIA | serviço (abastecimento) |
| §171 | SAIR NÃO É MORRER | serviço (gatilho ocioso) |
| §172 | UM CANO SEM LEITOR NÃO É UM LOG | worker-pendurado-v1 (M2d) |
| §173 | REGISTADO NÃO É RASTEJADO | discovery-sementes-v2 (C1) |
| §174 | A MESMA RECONCILIAÇÃO DUAS VEZES… (+174-1) | unificação |
| §175 | SAÚDE NÃO É PRODUTIVIDADE | serviço (era §159) |
| §176 | RECEITAS-1 · O PADRÃO DE MORADA ESTAVA EM MOLDE | desbloqueio-coorte (receitas) |
| §177 | RECEITAS-2 · CORRIGIR A RECEITA NÃO PÕE UMA FONTE PRONTA | desbloqueio-coorte (receitas) |
| §178 | COORTE-1 · O FUNIL CORTA ANTES DA RELEVÂNCIA | desbloqueio-coorte (coorte-micro) |
| §179 | DESBLOQUEIO-1 · O COLETOR TEM A SUA CÓPIA DA RECEITA | desbloqueio-coorte (G1) |
| §180 | A PEÇA EXISTIA E NÃO ESTAVA LIGADA | qualify-semantico (S1) |
| §181 | UM LEITOR A OLHAR NÃO É UM ESCRITOR A MAIS | fila-windows (M2e) |
| §182 | UMA PONTE QUE ATRAVESSA NÃO É UMA PONTE QUE PROMOVE | contrato-unico (B1/B2) |
| §183 | UMA RECEITA APROVADA NO GABARITO NÃO SE MEDE NO MESMO GABARITO | listing-detail (LD1) |
| §184 | UM CONTRATO, UM DONO | contrato-unico (B2/B3) |
| §185 | UMA DECISÃO SEM PROVA É UMA OPINIÃO | semantico-opus (S2/S3) |
| §186 | O CUSTO DE UMA REGRA DE MORADA | listing-detail (LD2) |
| §187 | A PROVA DA ROTA ENVELHECE | contrato-unico (B3) |
| §188 | MULTILINGUE-1 · A MESMA RÉGUA NA LÍNGUA DO TEXTO | multilingue (L1) |
| §189 | UM ERRO DE CONTRATO APANHA-SE NO CONTRATO | listing-detail (LD3) |
| §190 | REDIRECIONAR NO PROCESSO NÃO ISOLA O FILHO | semantico-opus (S3) |
| §191 | UMA SEMENTE É UMA ORGANIZAÇÃO, NÃO UMA PÁGINA | sementes-travao (S4) |

A ordem de chegada é a data do primeiro commit (em qualquer ref) que trouxe o título. Cada
secção renumerada leva uma linha a dizer de onde veio. Nada apagado. Próximo livre: **§192**.

## SWITCH_PLAN — actualizado na 3.ª passagem

**Medido agora (23/09):** supervisor **PID 98512** (arrancou às 04:29); observador
**PID 14960** (ponte-curador-v1); a pasta viva está em **075501a0 (sementes-travao-v1)** —
**contido nesta linha**. Trocar já **não** tira nada de produção (M2e, S2, S3, S4 estão cá).
11 ficheiros sujos na pasta viva.

Ainda em curso e fora da linha: R1, Q1, X1, A1. Se algum destes for para produção antes
da troca, a condição volta: medir o HEAD vivo no passo 1 e confirmar
`git merge-base --is-ancestor <HEAD vivo> <FINAL_HEAD>`.

1. **Medir na hora:** PIDs (pelo PID exacto) e HEAD da pasta viva; exigir que o HEAD vivo seja
   ancestral do FINAL_HEAD (senão: parar aqui).
2. `PARAR.flag` na pasta viva; confirmar que o supervisor do passo 1 saiu.
3. Corte final com o bot parado (`congelar_livros_do_servico.py`), mais cópia com sha256 de
   `italy_contracts_curator.json` (do bot) e de `candidatas/FONTES-CANDIDATAS.json`.
4. **Pacote G1 com o bot parado**, blocos 1-3 + V3:
   `py scripts/desbloqueio/aplicar_desbloqueio.py --livro=curadoria/italy_contracts_curator.json
   --tabela=regras/italy_contracts_onboarded.json --livro-bot=<corte>/italy_contracts_curator.json
   --d10=A --escrever` na worktree unificada; correr outra vez e exigir `ESCRITO: 0`
   (ensaiado hoje: 76 → 0).
5. D13 sobre a porta viva: `py ferramentas/unificacao/aplicar_d13_capacidade.py --porta
   <copia da porta viva> --escrever` (idempotente).
6. Reconciliar (`reconciliar_livros.py --livro-servico <corte> --livro-ponte
   curadoria/LIFECYCLE-LEDGER-V1.json --aplicar`), unir livros (`unir_livros_do_servico.py`),
   `interface_collection.py`, cadeia do mapa, push, LOCAL == REMOTO.
7. Trocar o código na pasta viva (mesma pasta; ramo novo no FINAL_HEAD).
8. Relançar o supervisor e o observador (o observador a partir de unificacao-v1).
9. Medir: `supervisor.py --estado` (RUNNING ou IDLE, `PID_CHECK_NAO_SEI` vazio);
   `WORKER-HEARTBEAT.json` a avançar; `WORKER-STDOUT.log` a crescer; no portão, 5 recusadas
   por `RETIRADA_POR_DECISAO` e elegíveis perto de 16; `PASS_PARCIAL` nas voltas (lei do canário).
10. **Desfazer:** `PARAR.flag`; voltar a pasta viva ao HEAD medido no passo 1; repor os
   livros do corte e as cópias do passo 3 (conferir sha256); relançar.

---

# 4.ª PASSAGEM — UNIFICACAO-V1-D (23/09/2026) — PRONTA PARA O CUTOVER

Base fe61a34b (3.ª passagem aceite). Nenhuma coleta corrida; nenhum serviço vivo tocado.
Não puxados, de propósito: detector-erro-v1 (D1), ttl-mutable-v1 (T1), micro-pronta-v1 (A2),
cutover-ensaio-v1 (X1).

| passo | junta / faz | commit |
|---|---|---|
| 1 | recollection-prova-v2 0ac7947b (R1 + R2) | 67d3183e |
| 2 | quarentena-naosei-v1 c37c2423 (Q1; D11 liga a quarentena na porta) | 5756ee90 |
| — | D15 (opção A): LinkedIn/Instagram = POLICY_BLOCK com o trecho dos termos | 2b5e30ab |
| — | know-how §195, mapa, métricas, provas | até FINAL_HEAD |

## ENTREGA-D

```
PONTAS            = 2
CONFLITOS         = codigo 4 blocos, todos da Q1 x LD3, resolvidos pela D11 (ligar):
                    · politica_nao_sei.py: ACTIVA = QUARENTENA (a LD3 deixara PASSA «ate a decisao»);
                    · test_politica_nao_sei.py (3 blocos): os testes da LD3 que exigiam a politica
                      DESLIGADA passam a exigir QUARENTENA e ligada SO na porta
                      (admissao/admissao.py). O gate de FONTE da LD3 (retrato_html) nao muda.
                    · a regra «ligada so na porta» conta o NOME da politica como chamador: a minha
                      provar_em_copia.py escrevia-o; passou a correr esses testes por padrao
                      (a regra nao foi afrouxada).
                    R2 x LD2/LD3 na coleta: R2 mexe em coleta/italy_pilot_collect.mjs, Q1 em
                    coleta/executor_texto_de_html.py; a LD nao tocou em nenhum dos dois — sem
                    sobreposicao. Know-how: 2 blocos, uniao; R1, R2, Q1 recebem §192, §193, §194.
SUITE             = antes 8fe122cb: curadoria/ Ran 572 OK · tests/ Ran 5139, 91 testes vermelhos por nome
                    depois 5f514c9f: curadoria/ Ran 572 OK · tests/ Ran 5164, 90 testes vermelhos por nome
                    NEW_RED_BY_NAME = 0. Por nome sairam 2 (D15: test_as_25_recusas... e
                    test_nenhuma_recusa_viva...429...) e apareceu 1 que NAO e do codigo:
                    test_M5_o_ponto_fixo... exige o carimbo do mapa igual a arvore, e 5f514c9f
                    (commit de ferramenta) ainda nao tinha passado pela cadeia. Depois da cadeia,
                    no FINAL_HEAD: IMPRESSAO_DO_CARIMBO=IGUAL e o teste passa (medido).
PROVAS_COPIA      (77077dee, copia descartavel; ensaios numa copia sem .git)
  ponte + red team 17/17 · ponte B2 (fotografia: 8 -> 20) · supervisor · worker pendurado ·
  gatilho ocioso 9/9 · fila windows (1 worker, 0 PermissionError) · sementes + travao ·
  decisao semantica · multilingue · G1 · RETIRADA · 183/183 modulos                 PASS
  R1/R2 provas node: recollection_http_local 15/15 · recollection_indice_local 13/13 ·
  recollection_timeout_local 8/8                                                    PASS
  Q1: test_quarentena_naosei + test_politica_nao_sei 28/28                          PASS
  REVALIDAR (offline, livro do bot depois do G1): 6 candidatas CONTRATO_NOVO
  (IT-T7-017, IT-T10-018, IT-T7-033, IT-T10-022, IT-T7-042, IT-T7-043); o limite e 5 por volta:
  5 na 1.a volta, 1 na 2.a                                                          PASS
D15               = aplicada (abaixo)
SYSTEM_MAP_CHECK  = PASS
```

## D15 (opção A) — aplicada

- **(1)** LinkedIn e Instagram ficam `POLICY_BLOCK` na porta — o estado que a ponte já
  escrevia no livro, não um novo. A ponte (`curadoria/ponte_candidatas.py`) escreve-o;
  o vocabulário da porta declara-o (`fonte_nova.ESTADO_POLICY_BLOCK`).
- **(2)** A prova é o trecho dos termos, com endereço e data, e o sha256 da página guardada:
  - LinkedIn — https://www.linkedin.com/legal/user-agreement (em vigor 3/11/2025), lido
    2026-09-23T09:42Z por curl (200): «Develop, support or use software, devices, scripts,
    robots or any other means or processes (such as crawlers, browser plugins and add-ons or
    any other technology) to scrape or copy the Services, including profiles and other data
    from the Services;»
  - Instagram — https://help.instagram.com/581066165581870 (em vigor 1/1/2025), lido
    2026-09-23T09:44Z por Chrome headless `--dump-dom` (o curl deu 400 e a página só tem o
    texto depois do JavaScript): «You can't attempt to create accounts or access or collect
    information in unauthorized ways. This includes creating accounts or accessing or
    collecting information in an automated way without our express permission, regardless of
    whether such automated access or collection is undertaken while logged-in to an Instagram
    account.»
  - Ficheiros: `candidatas/PROVA-TERMOS-REDES-SOCIAIS-V1.json` e `candidatas/prova-termos/`
    (marcados `-text` para o sha256 bater em qualquer checkout). A sonda de 14/09 (429) fica
    em `EVIDENCIA_HISTORICA`.
- **(3)** `PROXIMA_EXPANSAO_PEOPLE_SOCIAL = 69` (44 LinkedIn + 25 Instagram), visível no teste
  e no `fonte_nova.py` (listagem). Fora de pronta, recusada e em análise; só saem com acesso
  autorizado pelo dono.
- **(4)** Teste `TestOsTermosProibemEProvamSe` + teste da ponte. Mutações: marcar RECUSADA,
  marcar EM_ANALISE, usar o 429 como prova, adulterar o sha256, a ponte voltar a escrever
  RECUSADA → **5 de 5 reprovam**.
- **(5)** Facebook continua `CAPABILITY_BLOCK` (6). Há ainda **14 Facebook em EM_ANALISE** que
  nunca passaram pela ponte (já registado antes); a D13/D15 não as mencionam e ficaram como
  estão.
- As 69 linhas já escritas foram corrigidas por `ferramentas/unificacao/aplicar_d15_politica.py`
  (idempotente; guarda o estado e o motivo anteriores). Com isto, os dois vermelhos que
  vinham da base no mesmo ficheiro (`test_as_25_recusas…`, `test_nenhuma_recusa_viva…429…`)
  passaram a verde.

## SWITCH_PLAN — substituído pelo CUTOVER-RUNBOOK.md da X1

**O plano da troca é o `CUTOVER-RUNBOOK.md` do ramo `origin/cutover-ensaio-v1` (d07fff36),
ensaiado em cópia pela X1 (`RELATORIO-CUTOVER-ENSAIO.md`).** Este relatório não escreve outro.
Os SWITCH_PLAN das passagens 1 a 3, acima, ficam só como registo.

A X1 ensaiou o meu plano e achou 6 defeitos, que o runbook corrige:
1. o passo 4 escrevia na cópia protegida dos livros e o passo 6 recusava-a (rc 3);
2. perderia 430 candidatas e 302 SOURCE_ID que só o livro vivo tem;
3. perderia as 6 marcas D10;
4. 7 fontes D10 ficavam sem tarefa (incluindo IT-T5-049);
5. o portão dá 29 elegíveis, não perto de 16 como eu escrevi;
6. o observador era relançado sem `--lane`.

O que esta passagem entrega ao runbook, sem o mudar: as ferramentas `aplicar_d13_capacidade.py`
e `aplicar_d15_politica.py` (idempotentes, com `--porta`), a prova dos termos
(`candidatas/PROVA-TERMOS-REDES-SOCIAIS-V1.json` + `candidatas/prova-termos/`), e a medida
offline do REVALIDAR (6 candidatas CONTRATO_NOVO, 5 por volta). A X2 ensaia sobre o FINAL_HEAD
desta passagem.

---

# 5.ª PASSAGEM — UNIFICACAO-V1-E (23/09/2026)

Base 516132fe (4.ª passagem aceite). Nenhuma coleta corrida; nenhum serviço vivo tocado.
**A linha descende de 05fd018a** (`origin/cutover-ensaio-v1`, o FINAL da troca real X3): o que
esta passagem trouxe entra no vivo por fast-forward.
Fora, de propósito: `v1-ligada` (não existe no origin), scrap-portas-v1, sala-duplicados-v1 (A3),
curator-youtube-v1 (SOC2), youtube-regua-t8-v1 (YT2).

| passo | junta / faz | commit |
|---|---|---|
| 1 | ttl-mutable-v1 8ee85e5a (T1: TTL 3 dias para Riunite/Zootecnica) | 023eaa18 |
| 2 | micro-pronta-v2 b3f548eb (A2: coorte do portão, RAW ≠ falha, backup da Sala, MICRO-RUNBOOK) | b8056918 |
| 3 | social-prontidao-v1 ffef59cf (SOC1: prova de prontidão social, termos com sha256) | 5983ffe5 |
| 4 | youtube-oficial-v1 7f651aa7 (YT1: canário YouTube) | 6096726a |
| — | know-how §196-§199 | 65e5c615 |
| 5 | cutover-ensaio-v1 05fd018a (X2: observador com `--lane` e trava) | (ver git log) |
| — | defeito escondido da A2 no portão; mapa | 75e9ce3e |
| — | este relatório; mapa | FINAL_HEAD |

## ENTREGA-E

```
PONTAS            = 5 (T1, A2, SOC1, YT1 + cutover-ensaio-v1 pedida a meio)
CONFLITOS         = 0 de codigo. Know-how: 5 blocos, uniao. Docs com marcadores de metricas
                    (HANDOFF, docs/piloto, docs/apresentacao...): lado da base e --sync.
                    Gerados e censos: lado da base, regerados pela cadeia.
                    SOC1 guarda 4 paginas de termos em candidatas/prova-termos/ (ja -text pela
                    D15): os 4 sha256 do PROVA-TERMOS-SOC1-V1.json batem depois da juncao.
                    T1 mexe na tabela do coletor (regras/italy_contracts_onboarded.json):
                    italy_contract_test com as mesmas 76 falhas da base; RETIRADA verde.
DEFEITOS ESCONDIDOS = 2 (12.o e 13.o da unificacao):
                    12. a A2 trouxe scripts/micro_coleta/ensaio_offline.py,
                    um caminho novo ate ao coletor italiano sem classificacao no portao
                    (test_collection_gate). Isso punha VERMELHA a suite de base do red team da
                    ponte: o red team saia com rc 1 («BASE suite=False») apesar de 17/17 mortos —
                    mortos contra uma base vermelha nao provam nada. Declarado MANUAL_TOOL (o
                    ensaio desvia toda a rede para 127.0.0.1 e usa um Postgres descartavel).
                    Ja estava vermelho na propria b3f548eb.
                    13. a SOC1 escrevia a chave PERMITIDA na sua prova (copia da matriz), e a
                    regra «so a matriz declara PERMITIDA» (test_c10_4_route_gate) via ali um
                    segundo portao. A chave passou a PERMITIDA_NA_MATRIZ (prova, fixture e JSON
                    da SOC1). Ja estava vermelho na propria ffef59cf. A regra nao mudou.
SUITE             = antes 5f514c9f (4.a): curadoria/ Ran 572 OK · tests/ Ran 5164, 90 vermelhos por nome
                    depois 75e9ce3e: curadoria/ Ran 576 OK · tests/ 90 vermelhos por nome
                    Por nome: saiu test_M5_o_ponto_fixo (o commit medido ja passou pela cadeia);
                    entrou test_so_a_matriz_declara_permitida, herdado da SOC1 — corrigido a
                    seguir (defeito 13) e re-medido modulo a modulo: test_c10_4_route_gate +
                    test_prontidao_social_v1 44/44. NEW_RED_BY_NAME no FINAL_HEAD = 0.
                    A suite inteira nao foi corrida outra vez depois desse conserto (1 h).
PROVAS_COPIA      (75e9ce3e, copia descartavel; ensaios numa copia sem .git) — todas PASS
  ponte · red team 17/17 com BASE verde · ponte B2 · supervisor · worker pendurado ·
  gatilho ocioso · fila windows · 183/183 modulos de prova · NAO SEI/quarentena 28/28 ·
  R1/R2 node 15/15, 13/13, 8/8
  novas desta passagem (aad63db1, copia): ttl_mutable_local 12/0 · incrementalidade_test 31/0 ·
  test_ensaio_offline_micro + test_micro_coleta_instrumento + test_prontidao_social_v1 65/65
  X2 (1f3159da): test_ponte_automatica + guarda 22/22 · test_medir_cutover 11/11
KNOW_HOW_TABLE    = §196 TTL-1 · MUTABLE COM PRAZO (T1; chegou sem numero)
                    §197 A COORTE VEM DO PORTAO, A FALHA NAO E DOCUMENTO (A2; era §196)
                    §198 O SCRAP DIZ «CONSIGO», A PORTA DIZ «NAO PODES» (SOC1; ja era §198)
                    §199 YT1 · O SOM DO YOUTUBE ATRAVESSA ATE AO TEXTO (YT1; era §196;
                         RELATORIO-YT1-CANARIO.md aponta agora para §199)
                    §200 UM PLANO SEGUIDO A LETRA NUMA COPIA NAO E UM PLANO ENSAIADO (X1; sem numero)
                    §201 A CASA DA PONTE NAO PODE SER A PASTA DO BOT (X2; era §196)
                    Ordem: §196-§199 por ordem de chegada; X1/X2 chegaram depois de §199 estar
                    publicado nesta linha e foram para o proximo livre depois do maior.
                    Nada apagado. Proximo livre: §202.
SYSTEM_MAP_CHECK  = PASS
FINAL_HEAD        = (na entrega ao coordenador) — para a X2/X3: descende de 05fd018a
```

O plano da troca continua a ser o `CUTOVER-RUNBOOK.md` (X1/X2). Os 2 vermelhos conhecidos de
`tests/test_fila_italia_decisoes` (amostras e população de SOURCE_ID) estão com a A3 e não foram
mexidos.

---

# 6.ª PASSAGEM — UNIFICACAO-V1-F (23/09/2026) — com tela azul a meio

Base 940f3b14 (5.ª passagem). Worktree nova: **`unificacao-v1-f`** (a `unificacao-v1` antiga foi
usada por outra sessão, ver abaixo). Nenhuma coleta; nenhum serviço vivo tocado; nada na Sala real.
D25 (a Big Collection não espera pelas fontes; coorte = READY do portão no arranque): não muda
código desta junção — o portão está verde e é ele que dá a coorte.

| passo | junta / faz | commit |
|---|---|---|
| 1 | sala-duplicados-v1 a0111921 (A3: Sala idempotente por documento) | 6dfc75a5 |
| 2 | micro-rede-real-v1 dbbd7271 (A4: micro com rede real) | a21901a2 |
| 3 | v1-ligada 039c0160 (V1A; traz K1 receitas V4 e D1 detector D14) | 22ae87ee |
| — | retira o que a sessão P1 escreveu nesta worktree | accd8f44 |
| 4 | retencao-youtube-v1 f899ed7f (SOC3 + SOC2) — **depois retirada** | f07349e3 → revert 63169df3 |
| — | know-how §202-§208, métricas, mapa | até FINAL_HEAD |

## ENTREGA-F

```
PONTAS JUNTAS     = 3: A3, A4, V1A (com K1 e D1 dentro)
FORA (declarado)  = SOC3+SOC2 (f899ed7f): juntada, medida e RETIRADA por revert — a propria
                    lane reprova 4 leis da casa (SQL da Sala fora do dono, 2.o dialeto psql no
                    runtime, migration 033 sem marca de proposta, migration nova desde o tronco).
                    A 033 nao se corrige aqui: o sha256 e guardado pela cadeia do banco e NAO SEI
                    se ja foi aplicada. Ref confirmada: f899ed7f esta em origin/retencao-youtube-v1.
                  = REELS scrap-portas-v1: 0c3bd0a2 (ultimo antes da queda) tem 27 vermelhos
                    proprios nos testes do Scrap (a decisao do Instagram mudou para ALLOWED e os
                    testes antigos exigem NAO; o teste novo das duas portas rebenta a ler o
                    workflow); o head no origin passou a um CHECKPOINT pos-queda com
                    data/samples/RUN-MANIFEST.json CORTADO A MEIO (JSON invalido na linha 19349).
                  = LINKEDIN scrap-linkedin-v1: 8f3ddca5 (ultimo antes da queda) tem 14 vermelhos
                    nesses testes (a base tem 5); o head no origin e tambem um CHECKPOINT pos-queda.
CONFLITOS         = 0 de codigo nas 3 que ficaram; test_collection_gate por uniao (SOC3, depois
                    revertida). Know-how por uniao; gerados e censos pela cadeia.
DEFEITOS          = 2 corrigidos: coleta/retrato_html.mjs (V1A) cita o coletor e nao estava
                    declarado no portao (declarado LIBRARY); a guarda de isolamento passou a
                    aceitar redirecionamento por tabela `(W, "PULSO")` + setattr (alarme falso nos
                    testes da SOC2; mutacao: tirar a entrada da tabela -> reprova).
INCIDENTES        = (1) as 12:4x a sessao P1 «pesquisadores» fez `checkout -b pesquisadores-v1`
                    NESTA worktree e escreveu 4 ficheiros (pesquisadores.py, PESQUISADORES-PROOF,
                    FONTES-CANDIDATAS +306 linhas, DISCOVERY-VISITED); os meus merges cairam no ramo
                    dela e um `git add -A` levou os ficheiros dela. Retirados em accd8f44; o trabalho
                    dela ficou inteiro no ramo local pesquisadores-v1 @ a803d6b7 e em
                    %TEMP%/m5/intruso-1247. A unificacao mudou para a worktree unificacao-v1-f.
                    (2) tela azul 12:50: repositorio integro (0 objetos em falta na linha; fsck limpo);
                    a juncao da SOC3 que estava aberta retomou-se sem perda.
SUITE             = UMA vez, em de4dec2b: curadoria/ Ran 618 OK · tests/ 91 vermelhos por nome.
                    Contra a 5.a (75e9ce3e, 90): sairam 3 (os 2 da fila italiana — A3 — e o da
                    PERMITIDA); entraram 4, todos da SOC3. Depois do revert (63169df3) os 4
                    medidos de novo, modulo a modulo, numa copia: ja nao reprovam.
NEW_RED_BY_NAME   = 0 no FINAL_HEAD (a suite inteira nao correu de novo depois do revert: 1 h).
PROVAS_COPIA      (de4dec2b) todas PASS: ponte, red team 17/17 com base verde, B2, supervisor,
                  worker pendurado, gatilho ocioso, fila windows, 183 + 28 modulos, R1/R2 node
                  15/13/8. A3 41/41 · A4 5/5 + portao · V1A+K1+D1 133/133.
KNOW_HOW_TABLE    = §202 D1 · §203 K1 (era §196) · §204 V1A (era §197) · §205 SOC2 (era §199;
                    codigo fora) · §206 A3 (era §197) · §207 SOC3 (era §200; codigo fora) ·
                    §208 A4 (era §198). Proximo livre: §209.
SYSTEM_MAP_CHECK  = PASS
FINAL_HEAD        = na entrega (descende de 05fd018a)
```

Pronto para instalar no vivo pelo `CUTOVER-RUNBOOK.md`, com o bot quieto.
