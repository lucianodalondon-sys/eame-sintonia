# Plano de instalação · `bloqueadas-v1` (conserto do link com acento + ROBO-DIAGNOSTICO)

Ramo `bloqueadas-v1`, a partir do vivo `origin/servico-20260923-0923` @ `ce28040c`. **NÃO instalado.**
Só código: sem migração, sem livro, sem Sala.

## O que entra

| peça | commit | o que muda | testes |
|---|---|---|---|
| link com acento | `aa29196a` | `canario.url_segura` codifica só o que não é ASCII (e o espaço); usado em `canario.buscar` e `reparar_contrato.buscar_com_destino`. Antes: IT-T7-252 chegava ao teto de 5 com `UnicodeEncodeError` ANTES do pedido | `test_url_com_acento` 4/4 · mutação 2/2 · `test_reparar_contrato` 39/39 · `test_canario_detalhe` 14/14 |
| ROBO-DIAGNOSTICO | `f06d245d` | o painel do supervisor deixa de assustar: `WORKER_ALIVE=false` no ficheiro quando o worker sai; `HEARTBEAT_APLICA` / `HEARTBEAT_LEITURA` / `RESTARTS_TOTAL_CONTA` (só acrescenta; `HEARTBEAT_STALE` igual) | `test_robo_diag` 3/3 · mutação 2/2 · `test_status_liveness` 4/4 · `test_supervisor` 30/30 · `test_painel_pergunta_ao_so` 7/7 |
| classificação | `aa29196a` | `curadoria/bloqueadas_268.py` + `BLOQUEADAS-268-V1.json` — ferramenta SÓ DE LEITURA (não corre no robô) | — |

As duas peças de código não tocam os mesmos ficheiros (junção sem conflito).

## Passos

`VIVA=$HOME/orca/workspaces/eame-sintonia/source-curator-service-v1`. Nada pesado sem LOCK-PESADO e ≥5 GB.

1. **Pré-condição:** `git -C $VIVA rev-parse HEAD` = `ce28040c…` (se a INSTALAÇÃO-2 entrar antes, refazer a junção
   por cima dela: as duas não tocam os mesmos ficheiros — `canario.py`, `reparar_contrato.py`, `supervisor.py` ×
   `micro_coleta.py`, `admissao.py`, `entrada_final.py`, `system-map/scripts/`).
2. **Parar o robô** (`CUTOVER-RUNBOOK.md` passo 1) — o supervisor muda de código.
3. **Fotografia antes:** `git -C $VIVA status --short` e `sha256sum` desses ficheiros (livros operacionais).
4. **Guardar:** `git -C $VIVA diff > antes.patch`; stash com nome só se houver CÓDIGO sujo.
5. **Instalar:** `git -C $VIVA fetch origin bloqueadas-v1` e `git -C $VIVA merge --ff-only <SHA entregue>`.
6. **Testes no vivo**, rede fechada (`HTTP_PROXY=HTTPS_PROXY=http://127.0.0.1:9`), em `curadoria/`:
   `py -m unittest test_url_com_acento test_robo_diag test_status_liveness test_supervisor test_reparar_contrato test_canario_detalhe` → OK.
7. **Livros iguais** ao passo 3.
8. **Mapa:** `correr_a_cadeia.py VALIDAR` → `SYSTEM_MAP_CHECK=PASS`, carimbo IGUAL.
9. **Religar o robô.** `py curadoria/supervisor.py --estado` mostra `HEARTBEAT_APLICA`/`HEARTBEAT_LEITURA`.
10. **Re-enfileirar IT-T7-252** pelo caminho canónico (a tarefa está FAILED no teto; é o coordenador que decide
    re-medir). Esperado: o canário passa a pedir o link com `%C3%A0` em vez de rebentar.

### Desfazer

Robô parado; guardar `git status`/`git diff` e stash com nome; `git -C $VIVA reset --keep ce28040c`; `VALIDAR`;
religar. Sem Sala, sem livro.
