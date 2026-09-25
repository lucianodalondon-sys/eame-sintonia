# ROBOTS-INTEGRADO · plano de instalação (NÃO instalado)

Ramo `claude/robots-rfc9309-integration-9am18y` = produção **`290e7349`** + `origin/robots-rfc9309-v1`
(`9057284`), juntos no merge `bbba4ff`. O relatório da medição e da D39 continua em
[`RELATORIO-ROBOTS-RFC.md`](RELATORIO-ROBOTS-RFC.md); este ficheiro só diz **como instalar e como desfazer**
sobre esta base. O SHA exato a instalar é a cabeça deste ramo no momento da instalação (um ficheiro
commitado não conhece o próprio SHA).

## O que a integração fez

- **Conflitos só em gerados** (14: `system-map/data/*.generated.json`, o espelho do portal,
  `INDICE-DE-FONTES.md`, `CENSO-DAS-LIGACOES-DA-COLLECTION.md`) — resolvidos pela cadeia
  (`correr_a_cadeia.py REGERAR`), nunca à mão.
- **Código sem conflito.** `coleta/italy_pilot_collect.mjs` mudou dos dois lados e fundiu-se sozinho:
  o teto por domínio registável da base (D38) e os estados D39 do robots convivem em `licenca()`.
- **Teste novo** `AGuardaDoRobotsInteiro` em `tests/test_robots_rfc9309.py`: o `ROBOTS_SHA256` da prova
  é o do robots **inteiro** e a regra que decide pode vir depois do caractere 120.
- **`mutantes_d39.py` corrigido:** o critério Node («não aparece `FALHAS=0`») matava qualquer mutante
  de graça nesta base, porque a C5 da prova local do coletor **já falha na produção 290e7349 sem
  mutação**. Agora morto = falha **nova**, comparada pelo nome. 10/10 continuam mortos.
- **`mutantes_integrado.py`** (novo): 2.º leitor plantado (S1–S3), portão que decide sem o dono
  (S4–S5), guarda sha256 estragada (H1–H3): 8/8 mortos.

## Writeset (o que muda na produção)

```
A coleta/robots_rfc9309.py              M coleta/scrap_http.py
M coleta/italy_pilot_collect.mjs        M curadoria/gate_de_rota.py
M curadoria/descobrir.py                M curadoria/worker.py
M provas/cortesia_http_local.mjs        M provas/medir_validadores_coorte.py
M tests/test_c10_5_collection_flow.py   M tests/test_integracao_04a_curator.py
A tests/test_robots_rfc9309.py          A provas/robots_rfc/* (12 ficheiros)
M system-map/data/architecture.declared.json
M system-map/* · italia-portale/client/system-map/* · 2 docs gerados (pela cadeia)
```

**Nenhum livro vivo é tocado** (`curadoria/*-V1.json` de estado, `data/collection-ledger`,
`candidatas/FONTES-CANDIDATAS.json`, fila). Confere-se no passo 3.

## Plano (quando o dono mandar — só depois do MICRO / 2.ª onda, D39)

1. **Parar o bot entre voltas** (supervisor). Anotar `git rev-parse HEAD` do serviço (= `ANTES`)
   e guardar `git status` + `git diff` do serviço.
2. **Copiar os livros vivos** do serviço para fora da árvore (`LIFECYCLE-LEDGER-V1.json`,
   `LIFECYCLE-QUEUE-V1.json`, `data/collection-ledger/`) e anotar o sha256 de cada um.
3. **Na produção:** `git merge --no-ff claude/robots-rfc9309-integration-9am18y`. Conferir que nenhum
   livro vivo está no diff: `git diff --name-only ANTES HEAD | grep -E "V1\.json|collection-ledger|FONTES-CANDIDATAS"` → vazio.
   Se a produção andou depois de `290e7349` e houver conflito **de código**: parar e chamar o dono.
   Conflito só em gerados: `python3 system-map/scripts/correr_a_cadeia.py REGERAR` e commit.
4. **Portões do mapa:** `correr_a_cadeia.py VALIDAR` → `SYSTEM_MAP_CHECK=PASS`; depois do commit,
   `python3 system-map/scripts/impressao_da_arvore.py --conferir-carimbo` → `IGUAL`.
5. **No serviço:** `git merge --ff-only <cabeça da produção>` (ficheiros locais: `git reset --keep`,
   **nunca** `--hard`).
6. **Provas no serviço, sem rede:** `py -m unittest tests.test_robots_rfc9309` (23 OK);
   `node provas/cortesia_http_local.mjs` (esperado **30 ok / 1 falha = C5**, a mesma da produção de
   hoje — qualquer outra falha é nova e manda desfazer); `py provas/robots_rfc/mutantes_d39.py .` (10/10);
   `py provas/robots_rfc/mutantes_integrado.py .` (8/8).
7. **Conferir os livros vivos** contra o sha256 do passo 2 (a instalação não os pode ter mexido).
8. **Religar o bot.**
9. **Só com ordem separada do dono — enfileirar as 52:**
   `py provas/robots_rfc/enfileirar_as_52.py` (só mostra) e, conferido, `--aplicar`.
   Ensaio só-mostrar sobre **cópia** do livro vivo desta base (290e7349), 25/09:
   **52 mudam · 47 entram (8 READY à frente, prioridade 85; as outras 39 com 57) · 5 fora** por não terem
   contrato no livro do robô (IT-T10-007, IT-T10-044, IT-T11-005, IT-T3-018, IT-T9-023). Sobre
   `7cdb7ea4` eram 49/3: duas fontes a mais ficaram só na tabela do coletor. A IT-T11-005 (simei.it)
   continua READY sem contrato — **decisão do dono**: importar o contrato ou rever o READY.
   ⚠️ Uma READY cuja VALIDATE_ROUTE passe desce a CANARY_PENDING e volta a canariar.

## Desfazer

- **Antes do passo 9** (só código mudou): no serviço, `git reset --keep ANTES`; na produção,
  `git revert -m 1 <sha do merge do passo 3>` e regerar o mapa pela cadeia (`REGERAR`, `VALIDAR`,
  commit, `--conferir-carimbo`). Os livros vivos não foram tocados — conferir o sha256 do passo 2.
- **Depois do passo 9** (a fila ganhou tarefas): além do de cima, as tarefas `VALIDATE_ROUTE` com motivo
  `D39 re-medir robots` que ainda estejam `PENDING` cancelam-se pela porta da fila; as que já correram
  mudaram o livro de estados pela régua e **não se desfazem à mão** — o caminho de volta é o da régua
  (voltar a canariar / reparar). Por isso o passo 9 é uma ordem à parte.
- Em qualquer caso, a cópia dos livros do passo 2 é a prova do estado anterior, não um atalho para
  sobrescrever o livro vivo.
