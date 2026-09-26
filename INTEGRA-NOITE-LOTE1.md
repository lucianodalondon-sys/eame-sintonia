# INTEGRA-NOITE · LOTE 1 — um só pacote de instalação sobre o vivo `83de0ccd`

Ramo `integra-noite-v1`, a partir do **vivo `83de0ccd`** (C9). Oito pacotes juntos um a um (`--no-ff`, o SHA de
origem na mensagem), **um só mapa** no fim. **NÃO instalado** — quem instala é o coordenador.

## Os pacotes

| # | pacote | SHA | base | junção | testes do pacote (por NOME, contra o vivo, mesmos dados) |
|---|---|---|---|---|---|
| 1 | boletins-v3 | faf96b8d | 83de0ccd | limpa | 13 módulos · 63 testes Py + 5 provas Node · **0 novas** |
| 2 | social-micro-v1 | 6fb36898 | ce28040c | só gerados (14) | 3 módulos · 31 testes · 1 falha **herdada** (`test_scrap_rc01_release_candidate`, igual no vivo) · 0 novas |
| 3 | social-qualificar-v1 | 77880e2a | ce28040c | limpa | 1 módulo · 4 testes · 0 novas |
| 4 | prova-teto-social-v1 | 84a997a6 | ce28040c | só gerados (14) | 1 módulo · 22 testes · 0 novas |
| 5 | legacy-99-v5 | ed86cb97 | 83de0ccd | **1 conflito de CÓDIGO** (`curadoria/worker.py`) — **APROVADO pela coordenação 03:27, só este**: fica só o caminho da «página = boletim», sai o `canario_youtube_canal` (como o v5 e o `test_onda3_b_inerte` exigem) | 5 módulos · 54 testes · 0 novas |
| 6 | robo-diag-v1 | f06d245d | ce28040c | limpa | 1 módulo · 3 testes · 0 novas |
| 7 | leitor-data-yt-v1 | 4dd00308 | 83de0ccd | limpa | 2 módulos · 52 testes · 12 falhas **herdadas** (`test_tempo_e_lugar_da_publicacao`, as mesmas 12 no vivo) · 0 novas |
| 8 | acervo-tempo-lugar-v1 | 90a0f61f | 83de0ccd | só gerados (14) | sem testes de unidade; o ensaio da 034 (`provas/migracao_034_ensaio_copia.py`) precisa de Postgres descartável — **não corrido aqui** (o dono correu-o sob a LOCK-PESADO às 03:10, ver `ACERVO-TEMPO-LUGAR.md` §6) |

**Regressão geral** (`provas/boletins_data_local/testes_por_nome.py`, o mesmo corredor nas duas árvores, com os
MESMOS dados — `data/samples`, `data/collection-ledger`, `docs/` — e **rede fechada** por proxy numa porta morta):
47 módulos, 514 testes Python + 8 provas Node. **Falhas novas: 0. Herdadas: 91**, nome a nome iguais ao vivo:
`italy_contract_test` 77 · `test_tempo_e_lugar_da_publicacao` 12 · `test_collection_gate` 1 (os 3 caminhos sem
classificação) · `test_scrap_rc01_release_candidate` 1. Ficheiros: `provas/integra_noite/lote1-{ramo,vivo}.json`.

⚠️ Duas leituras enganadoras medidas e desfeitas: sem `docs/` na cópia, `test_prova_teto_social` dava 9 «novas»
(lê o Atlas de fontes); sem `data/collection-ledger`, a prova de contratos parava a meio (70 contra 77). Com os
mesmos dados nos dois lados, somem. O **red team da ponte não foi corrido no vivo** (nem aqui: escreve no livro).

## Conferências

| conferência | resultado |
|---|---|
| ff-only sobre `83de0ccd` | **SIM** — o vivo é antepassado do ramo |
| 16 livros vivos (os `M` da pasta viva) | **nenhum** nos 240 ficheiros do writeset; o writeset não toca `data/` |
| migração 034 | o ficheiro entra (`supabase/migrations/034_…sql` + `supabase/desfazer/034_desfazer.sql`), **NÃO se aplica** |
| mapa | UM só, pela cadeia (REGERAR · commit · VALIDAR · carimbo IGUAL) — ver o commit do mapa |

## Plano único de instalação (o coordenador instala; um escritor; sem rede)

**A · Código (tudo de uma vez, ff-only):**
1. `curadoria/PARAR.flag`; esperar a volta do bot acabar. Guardar `git rev-parse HEAD` (= `83de0ccd`) e `git status`
   (os 16 livros).
2. `git merge --ff-only origin/integra-noite-v1` na pasta viva.
3. Conferir que o `git status` dos 16 livros é o MESMO do passo 1.
4. `correr_a_cadeia.py VALIDAR` → PASS; `PORTOES_POS_COMMIT` → IGUAL. Repor os gerados que o validador reescreve
   **pelo nome** (`git checkout -- <ficheiro>`), **nunca** `git checkout -- .` (apagaria os livros).
5. Provas rápidas sem rede: `node regras/boletim_data_local_test.mjs` · `py -m unittest tests.test_onda3_b_inerte
   tests.test_prova_teto_social tests.test_semear_so_as_candidatas` · `cd curadoria && py -m unittest test_robo_diag
   test_regua_social test_pagina_boletim`.
6. Reiniciar o supervisor (o robo-diag muda `curadoria/supervisor.py`). **Nenhum pacote escreve nos livros só por
   ser instalado.**

**B · O que ESCREVE nos cadernos do robô — só com o bot PARADO, e por esta ordem** (cada passo é decisão do
coordenador; nenhum faz parte do passo A):
1. **legacy-99-v5 · B**: `py curadoria/importar_do_coletor.py --pelo-scrap --ids=<lote>` (grava contratos/ledger do
   bloco 4; tudo ou nada). Ver `ferramentas/legacy99v4/SEPARAR-A-B-V5.md` §«Plano» e §«A ordem com a SOCIAL-QUALIFICAR».
2. Tirar o `PARAR.flag` até a volta acabar; voltar a parar.
3. **social (micro + qualificar)**: `py curadoria/semear_qualify_social.py --candidatas <lote>` (só mostra) →
   `--aplicar --vivo` (LinkedIn; depois `--tipo YOUTUBE`). Ler os SOURCE_ID novos no livro vivo (`SOCIAL-MICRO-PLANO.md`).
4. Depois dos canários de cada conta (outra onda, teto D38): `py curadoria/regua_social.py --corridas <…> --aplicar
   --vivo`, bot parado.
5. **leitor-data-yt**: o reprocessamento `admissao/reprocessar_tempo_lugar.py … --aplicar` **grava na Sala** — é do
   dono (`ferramentas/leitor_data_yt/LEITOR-DATA-YOUTUBE.md` §6), com a sua previsão; decisão do coordenador.
6. **acervo-tempo-lugar**: a **migração 034 fica de fora** (decisão do dono/coordenador).
7. **boletins**: os 9 contratos propostos entram depois pela porta — decisão do dono.

**⚠️ Red team da ponte:** nunca na pasta viva (escreve `IT-T99-*` no livro de contratos). Se correr por engano:
parar o bot, guardar `git diff curadoria/italy_contracts_curator.json`, conferir que só há `IT-T99-*`, repor SÓ esse
ficheiro, religar (`provas/boletins_data_local/PLANO-INSTALACAO-BOLETINS-V2.md`).

**Desfazer (código):** `PARAR.flag`; guardar `git status`/`git diff`; `git reset --keep 83de0ccd`; reiniciar o
supervisor. Os passos B têm cada um o seu desfazer no plano do dono.
