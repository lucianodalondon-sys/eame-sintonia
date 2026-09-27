# PLANO DESTRAVAR-FONTES — o que destrava o robô de fontes hoje, e o que não destrava

Ramo **`destravar-fontes-v1`**, feito sobre o vivo `554c1ec1` e **reaplicado sobre o vivo `2ef6fef8`** (27/09 10:52; rebase limpo,
nenhum ficheiro em comum além da declaração do mapa). Feito a 26/09 (22:30–23:55 -03), **sem rede**.
Nada foi escrito no vivo: só li `status_live.py`, o livro, a fila e as fichas (sha256 dos 18 livros
conferidos na cópia). Instalar = `git merge --ff-only` (o ramo desce de `2ef6fef8`). **PRONTO-SEM-MAPA.**

## 0 · O diagnóstico, em números medidos no vivo (01:27Z)

`QUEUE_ELIGIBLE_NOW=0`, `CANDIDATE_BACKLOG=0`, `SEMANTIC_REVIEW=240`, `CANARY_PENDING=59`, `HUMAN_REVIEW_REQUIRED=7`.

| As 240 em SEMANTIC_REVIEW | quantas | o que são |
|---|---:|---|
| candidata **já numerada** | **20** | a linha `CAND-…` nunca foi fechada; o número dela já anda (4 READY, 16 CONTRACTED_CANARY_FAILED). O painel conta-as a mais — **não precisam de nada** |
| QUALIFY **BLOCKED** «território indeterminado» / «decidido fora de IT» | **217** | exactamente as que a **D80** reabre |
| fontes `IT-…` «contrato executável sem ficha no Atlas» | **3** | IT-T12-075, IT-T3-005, IT-T5-104 — decisão humana, não tocadas |

| As 59 em CANARY_PENDING | quantas | porque não avançam |
|---|---:|---|
| rota do Scrap (`SCRAP_FASE`): **9 LinkedIn + 50 YouTube** | **59** | **por desenho**: o canário delas é uma colheita do Scrap, e o Curator **não** o enfileira (`curadoria/worker.py:937`, «o canario dela nao e do Curator»). Todas têm `VALIDATE_ROUTE DONE` e nenhuma tarefa aberta → a fila fica a 0. Só **4/59** têm alguma corrida no livro de coleta. Quem as avança é o **maestro social** (`--canario`), que só corre com autorização do dono, VPN IT e teto 5/domínio; o YouTube precisa de `VIDEO_ID` à mão (a chave da API só vive no GitHub) |

**A regra D80 já existia e não estava instalada.** O ramo `d80-v1` (223cce7f, PRONTO-SEM-MAPA desde 26/09 de manhã)
tinha a porta de recusa reversível, o prefixo fora de IT e a herança do mesmo site. Trouxe-o para cima do vivo
(cherry-pick limpo, sem conflito) e acrescentei **uma 2.ª lista** pela mesma regra.

## 1 · O que muda neste ramo

| | onde | o quê |
|---|---|---|
| D80 inteira | `candidatas/fonte_nova.py`, `curadoria/worker.py`, `decisao_semantica.py`, `rota_do_scrap_youtube.py`, `aplicar_d80.py`, `ensaio_d80.py`, `D80-LISTA-V1.json` | como em `PLANO-D80.md` (ramo d80-v1), sem mudança |
| 2.ª lista | `curadoria/DESTRAVAR-LISTA-V1.json` | **9 não-fontes** das que continuavam NAO SEI depois da D80: 1 página de contactos, 3 leis soltas do Normattiva (rodapé «trasparenza» do CREA), 1 decreto solto de 2001, 1 login do RENTRI, 1 crédito de agência web, 2 fundos/seguradora de saúde (já lidos «fora do agro» em DECISOES-SEMANTICAS-V1). Cada uma com motivo; reversível |
| `--lista=` | `curadoria/aplicar_d80.py` (+ `--lista2=` no `ensaio_d80.py`) | a ferramenta lê a lista dada; sem a opção, a de sempre. `--reverter --lista=X` só desfaz as linhas de X |
| números de ensaio | `curadoria/ENSAIO-D80-V1.json` → `ferramentas/destravar_fontes/ENSAIO-D80-V1-DE-69b0e23f.json` | ⚠️ o numerador fora de IT faz max+1 sobre **todos** os `curadoria/*.json`; o ensaio antigo ali dentro «gastava» EU-T12-002/003, INT-T12-001/002 e o real sairia EU-T12-**004**. Fora de `curadoria/`, volta a sair `-002` |

## 2 · O ENSAIO (cópia do vivo, rede FECHADA) — `ferramentas/destravar_fontes/ENSAIO-DESTRAVAR-V1.json`

Cópia = worktree deste ramo + os 18 livros sujos do vivo (copiados às ~01:30Z, sha256 18/18). **0 tentativas de rede.**

| Medida | Resultado |
|---|---|
| a seco | lote A (D80): 113/113 PRONTA, 102 a recusar · lote B (2.ª lista): 9/9 PRONTA, 9 a recusar |
| QUALIFY reabertas | **217** (7 «fora de IT» + 210 «indeterminado») |
| QUALIFY corridas | 217 → **111** «RECUSADA pela porta» · **7** número fora de IT e PARA · **3** OK · **96** continuam NAO SEI |
| números IT novos | **IT-T2-168** Linee guida SNPA (site IT-T2-108) · **IT-T2-169** ARSARP pubblicazioni · **IT-T8-071** Agraria Sassari eventi → BUILD_CONTRACT 3/3 OK → CANARY_PENDING (HTML: o Curator canaria-as sozinho, com rede) |
| números fora de IT | EU-T12-002 biostimulants.eu · INT-T12-001 croplife.org · EU-T12-003 fertilizerseurope.com · GR-T5-001 Benaki · FR-T5-001 INRAE · INT-T5-001 CIMMYT · INT-T12-002 FAO — CAPABILITY_BLOCK, 0 contratos |
| **elegíveis novas no ensaio** | **0** — READY só pelo canário, e o canário precisa de rede. Máximo possível depois do canário: **+3** (NAO SEI se passam) |
| `--reverter` (A e B) | 111 revertidas; **1204/1204 fichas iguais** à cópia intocada (tirando o rasto `RECUSAS_REVERTIDAS`) |

**Em números honestos:** o comando de hoje **não** põe fontes elegíveis por si. Tira 111 lixos do caminho, dá número a
3 fontes italianas que o robô canaria sozinho (com rede) e deixa 96 com o passo exacto que falta
(`ferramentas/destravar_fontes/NAO-SEI-96.json`). O que enche a fila **hoje** é o canário social (secção 4).

## 3 · O COMANDO — lotes A e B (coordenador, robô PARADO, um só escritor)

```bash
V=C:/Users/London1/orca/workspaces/eame-sintonia/source-curator-service-v1
R=C:/Users/London1/auditoria-madrugada/DESTRAVAR ; mkdir -p $R
# 1. Parar o robô — CUTOVER-RUNBOOK.md passo 1 (PARAR.flag e esperar o supervisor sair).
# 2. Instalar (só código + listas + ensaio; nenhum livro vivo é tocado pelo merge)
git -C $V fetch origin destravar-fontes-v1 && git -C $V rev-parse FETCH_HEAD   # = SHA do relatório
git -C $V merge --ff-only FETCH_HEAD
cd $V
# 3. A SECO — confere cada linha contra as fichas de AGORA (nada é gravado)
py curadoria/aplicar_d80.py --recibo=$R/A-A-SECO.json
#    esperar: POR_AGORA PRONTA=113, A_RECUSAR=102, QUALIFY_A_REABRIR {fora de IT: 7, indeterminado: ~210}
py curadoria/aplicar_d80.py --lista=curadoria/DESTRAVAR-LISTA-V1.json --recibo=$R/B-A-SECO.json
#    esperar: PRONTA=9, A_RECUSAR=9
#    (linhas que o robô mudou desde a montagem NAO se tocam: aparecem como ESTADO_MUDOU/JA_RECUSADA)
# 4. APLICAR — primeiro A, depois B (a reabertura das QUALIFY acontece em A; B só recusa)
py curadoria/aplicar_d80.py --aplicar --recibo=$R/A-APLICAR.json                                   # RECUSADAS 102
py curadoria/aplicar_d80.py --aplicar --lista=curadoria/DESTRAVAR-LISTA-V1.json --recibo=$R/B-APLICAR.json   # RECUSADAS 9
sha256sum $R/*.json
# 5. Portão IT e religar — CUTOVER-RUNBOOK.md passo 8
py superficie/rede.py --portao-de-egresso IT      # EGRESS_GATE=PASS, senão não religar
rm $V/curadoria/PARAR.flag    # e o supervisor pelo meio de hoje (py curadoria/supervisor.py, cwd $V)
```

O robô faz o resto: 217 QUALIFY → 111 recusadas + 7 números fora de IT (param) + 3 IT → contrato → rota → canário.
Se o dono disser a mãe do MASAF, acrescentar `--mae=masaf.gov.it=<SOURCE_ID>` nos passos 3 e 4 do lote A (entram mais 7).

**Desfazer** (robô parado): `py curadoria/aplicar_d80.py --reverter --lista=curadoria/DESTRAVAR-LISTA-V1.json --recibo=$R/B-REVERTER.json`
e depois `py curadoria/aplicar_d80.py --reverter --recibo=$R/A-REVERTER.json`. Números já cunhados **não se apagam**
(nunca reciclar); o código volta com `git -C $V reset --keep 2ef6fef8` (depois de guardar status/diff).

## 4 · As 59 CANARY_PENDING — o comando que já existe no vivo (precisa de ordem do dono)

```bash
cd $V
py ferramentas/maestro_social/maestro_social.py --so-plano --canario          # 50 ondas, FORA_DA_ONDA=[] (a seco: ferramentas/destravar_fontes/MAESTRO-PLANO-CANARIO-A-SECO.txt)
py ferramentas/maestro_social/maestro_social.py --correr --canario --autorizado-pelo-dono \
   --saida=C:/Users/London1/auditoria-madrugada/MAESTRO-CANARIO-<data> [--videos=IT-T7-015:<VIDEO_ID>,...]
```

- **9 LinkedIn** (ondas 01–05) correm já — `video-linkedin` pelo Scrap, 1 conta por pedido, 4 pedidos/domínio.
- **50 YouTube**: sem `YOUTUBE_DATA_API_KEY` no ambiente (só no GitHub Actions), cada canal precisa de um
  `VIDEO_ID` dado à mão em `--videos=`; sem ele a fonte **não corre** (`SEM_VIDEO_E_SEM_CHAVE`, não é FAILED).
- Disjuntores do próprio maestro: egresso fora de IT antes/depois, >30 min, 3 FAILED seguidas, teto da onda, prova-teto ≠ PASS.

## 5 · As 96 que continuam NAO SEI — `ferramentas/destravar_fontes/NAO-SEI-96.json`

| passo que falta | quantas |
|---|---:|
| REDE: 1 INSTITUCIONAL + 2 CONTEÚDO pela saída IT (≤5/site) → `DECISOES-SEMANTICAS-V1` | 69 |
| REDE: provas + PAÍS pela prova (se fora de IT, pára no número D80(ii)) | 11 |
| REDE: na janela do robots (Rete Rurale, 01–03 UTC) | 1 |
| DONO: mãe do site masaf.gov.it | 10 |
| DONO: dúvida de identidade (ISTAT, EIMA ×2) | 3 |
| DONO: identidade trocada registada (OP Alegra, Sherwood) | 2 |

Prioridade D84 dentro das de rede: **5 boletins** (Agriligurianet, LaMMA, Condifesa Lombardia NE, FEM bollettini,
Liguria bollettini), depois 19 de ciência, 11 da rede técnica, 61 outras.

## 6 · Provas

- **Testes pelo nome** (33 ficheiros que importam as peças mudadas, em cópias limpas, rede fechada):
  antes (554c1ec1) 538 testes, 1 falha · depois 562 testes (+24 do `test_d80`), **a mesma 1 falha**.
  De novo sobre `2ef6fef8`: antes 538, depois 586 (o `test_d80` entrou 2× na lista: +48 = 2×24), **a mesma 1 falha**
  (`test_zz_guarda_isolamento … test_1_estatico_todo_o_teste_que_toca_estado_redireciona`, texto idêntico).
  **0 falhas novas.**
- `test_d80`: 24/24 (22 da D80 + 2 da 2.ª lista), livros da cópia intactos (sha256 100/100).
- **Mutação** da opção nova: 2/2 colhidos (de novo sobre 2ef6fef8) (`--lista` ignorada; recibo sem o nome da lista). A D80 trazia 15/15.
- O vivo: nada escrito (lido em `554c1ec1`). O ensaio da secção 2 é sobre os livros de 27/09 ~01:30Z; o a seco
  do passo 3 é que confere contra as fichas do momento da aplicação.
