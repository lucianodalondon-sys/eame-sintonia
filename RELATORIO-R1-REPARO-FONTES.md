# RELATÓRIO — MISSÃO R1 · REPARAR AS FONTES JÁ ACHADAS

Ramo `reparo-fontes-v2` sobre `origin/unificacao-v1` @ `98ec8fbf` (a M5G, já em produção), **sem SOC2**. A v1 (`reparo-fontes-v1` @ `ec00e332`) fica como história. Motor: `claude-opus-5-5`. Ver §7 para o que mudou da v1 para a v2.

```
READY na CÓPIA do livro vivo (foto 23/09 18:21Z)   143 -> 179  (+36)
READY no VIVO                                       NÃO INSTALADO — ver §5
NEW_FAILURES_BY_NAME                                0  (v2: base 98ec8fbf vs e07abe2d — curadoria 1→1 de 590→629; tests 79→71 de 5067)
MUTAÇÃO                                             42 mutantes · 37 mortos · 5 equivalentes declarados
SYSTEM_MAP_CHECK                                    PASS (cadeia)
```

## 1 · O que estava errado (medido na foto)

| grupo | quantas | causa medida |
|---|---|---|
| CONTRACTED_CANARY_FAILED | 400 | 344 EMPTY_LIST (molde WordPress: 369 dos 375 contratos), 27 capa, 25 contrato reprovado pelo validador |
| CANARY_PENDING | 102 | nenhuma tarefa aberta; 45 eram EMPTY_LIST re-rotuladas pela reconciliação |
| QUALIFY BLOCKED | 200 | 179 território NÃO SEI pelo nome · 21 YouTube barradas por um texto que o código já não tem |
| SEMANTIC_REVIEW | 198 | as mesmas 179 e outras; 0 com prova nova na casa (DECISOES-SEMANTICAS só dá PAIS≠IT para 7) |

- As 16 receitas da M6Pd **já estavam aplicadas** no vivo (14; IT-T10-018 e IT-T10-022 trocadas pela D10).
- «Aguarda qualificação pelo curator» é o texto do MOTIVO de toda QUALIFY que a ponte cria, não um impasse.

## 2 · O que mudou no código

- `curadoria/reparar_contrato.py` — inferência (≤ 4 pedidos, robots da casa, 2 s por anfitrião, segue redireccionamento) e a porta `aplicar()` (só ACQUISITION; guarda a anterior; validador da casa; PRECISA_DE_REMEDIR).
  Recusas com nome: ENTRADA_INSTITUCIONAL, ENTRADA_E_MATERIA, SEM_FAMILIA_DE_ITENS, FAMILIA_ESTATICA, FAMILIA_E_MENU, ITEM_NAO_E_MATERIA, DUPLICADA.
- `worker.py` — etapa REPAIR_CONTRACT (REPAIRING → CANARY_PENDING + VALIDATE_ROUTE; nunca promove).
- `gatilho_discovery.py` — Nível 0c REPARAR (20 por volta, 1 reparo por fonte; CANARY_PENDING sem tarefa volta a canariar; YouTube do texto antigo desbloqueia; SEMANTIC só volta com prova nova). **Discovery só com reparo pendente = 0** (pedido E).
- `canario.hrefs_da_entrada` — um só dono dos links que o canário vê.
- `scripts/reparo/medir_em_copia.py` e `juntar_bancas.py` — medição em 4 bancas, por fatia de anfitrião.

## 3 · Antes → depois, na cópia (`scripts/reparo/R1-ANTES-DEPOIS-EM-COPIA.json`)

| causa | READY novas | o resto |
|---|---|---|
| A · reparo do contrato | 33 (29 de CANARY_FAILED, 3 de CANARY_PENDING, 1 de RETRY) | 132 item não é matéria · 107 sem família · 76 a entrada é uma notícia · 37 página de serviço · 33 capa no canário · 29 sem identidade · 14 família estática · 10 duplicada · ~10 rede/robots/auth |
| B · re-canário (CANARY_PENDING sem tarefa) | 3 | 3 capa, 1 adiada |
| C · QUALIFY | 0 | 21 YouTube desbloqueadas → 5 ganham SOURCE_ID e ficam CANARY_PENDING (o canário é do Scrap) |
| D · SEMANTIC | 0 | 0 de 179 com prova da casa; ficam SEMANTIC_REVIEW (NÃO SEI) |

Sem o filtro FAMILIA_ESTATICA a mesma cópia deu 143 → 188 (`R1-ANTES-DEPOIS-EM-COPIA-SEM-FILTRO.json`); pelo menos 12 das 42 novas eram páginas fixas (accesso-civico, ufficio-gabinetto, area-personale-tributi).

## 4 · NÃO SEI e ressalvas

- ⚠️ Das 36 READY novas, ~5 continuam duvidosas (páginas fixas com título longo: IT-T12-134, IT-T2-063, IT-T7-105, IT-T7-041, IT-T12-044), e IT-T9-015 aponta para «lavora-con-noi» (contrato antigo, via B). **Ler antes de pôr numa onda da Big Collection (D25).**
- O filtro FAMILIA_ESTATICA é heurística declarada (vocabulário de publicação / número-ano-id / título ≥ 6 palavras). Na amostra tirou 12 fixas e 2 boas (issuu da ARPA Toscana, uma notícia da ARPAL).
- IT-T8-058 correu em todas as bancas (a tarefa já estava na fila da foto); contada uma vez.
- 29 SEM_IDENTIDADE: CANARY_FAILED sem contrato no livro do bot e sem alocação — o contrato vive noutra tabela.
- Mutantes equivalentes: `len(membros) < 2` (os grupos já têm ≥ 2), `PARAGRAPH ≥ 800` (CONTENT já o exige), a guarda `fora` do `aplicar` (defensiva), o filtro FLUXO no ramo da secção (`_seccoes` só devolve caminhos com vocabulário de notícia).

## 5 · Instalação — NÃO FEITA

A condição da missão era «INSTALAR se tudo verde». A suíte do commit novo foi morta pelo Claude Code por falta de memória na máquina. A base `280eb90b` mediu: curadoria 632/632 ok; tests 68 FAIL + 10 ERROR. Sem a comparação, NEW_FAILURES_BY_NAME = NÃO SEI, e não instalei.

Instalar leva também para produção a 6.ª passagem da unificação (SOC2, V1A…), porque o `worker.py` do reparo depende dela. O bot vivo está em `servico-20260923-0923 @ 3d62e87d`.

Plano (padrão B4), quando a suíte der verde:
1. Fotografar processos (supervisor vivo: PID 40520), sha256 dos livros, cópia em `C:\cutover\r1-<hora>\antes`.
2. `PARAR.flag` → o supervisor sai sozinho.
3. Na pasta do bot: `git checkout <R1> --` os `.py` de `curadoria/`, `candidatas/`, `scripts/receitas/`, `scripts/reparo/` que diferem de `3d62e87d`; commit só deles; os livros ficam com o sha256 de antes.
4. Portão de egresso IT → PASS → apagar `PARAR.flag` → `Start-Process powershell -NoExit` com `py curadoria/supervisor.py`.
5. Provar ao vivo: contar READY no livro a cada hora; esperado ≈ +36 em ~2 h de fila.

**DESFAZER:** `PARAR.flag`, repor `antes/`, relançar.

## 6 · Depois da queda da sessão (23/09 ~19:42) — a bateria completa e o writeset

- Suíte por NOME, uma de cada vez: `tests/` medida em `b862ef97` (depois dela só mudaram 2 testes em `curadoria/`); `curadoria/` medida em `491cc9ea`. **NEW_FAILURES_BY_NAME = 0.** Os 6 vermelhos da primeira medição eram `test_abastecimento` e `test_impasse_b4` a ler o livro real da árvore pelo gatilho; corrigido em `491cc9ea` (isolam livro e contratos).
- Writeset: `scripts/reparo/R1-WRITESET.json` — o que a instalação escreve (só código) e o que o bot passa a escrever em funcionamento.
- Ordem do coordenador: M5G primeiro; a R1 só depois, com OK. Refazer o diff contra o vivo depois da M5G (parte dos 25 ficheiros pode já ter entrado).

## 7 · R1 v2 — sobre a M5G, sem SOC2 (24/09)

A M5G entrou na produção (bot `8eec2e2a`, árvore igual a `origin/unificacao-v1` @ `98ec8fbf`). Essa linha **retirou a SOC2**. A v1 da R1 foi feita numa base que ainda a tinha, e instalá-la ficheiro a ficheiro traria a SOC2 de volta. Por isso a v2:

- **Junção:** os 8 commits de código da R1 aplicados por `cherry-pick -x` sobre `98ec8fbf`. Um conflito, só na declaração do mapa, resolvido à mão.
- **O worker não importa `rota_do_scrap_youtube`** (o ficheiro nem existe na árvore; medido na cópia: módulo não carregado).
- **Saiu o desbloqueio das QUALIFY do YouTube.** O worker desta linha escreve exactamente o texto antigo («YouTube exige channel_id…»); reabri-las seria um eco sem fim (reabre → barra → reabre). Teste novo prova que ficam barradas. Efeito medido na v1: 0 READY (5 SOURCE_ID em CANARY_PENDING) — o número de READY da cópia (143 → 179) não depende dele.
- **Bateria por NOME** (uma de cada vez): base `98ec8fbf` vs `e07abe2d` → **NEW_FAILURES_BY_NAME = 0**. Curadoria 1 vermelho antes e depois (`test_reconciliar_livros.test_zy_censo_dos_livros_reais`). Tests: 79 → 71; os 8 que passaram a verde são GPU/ASR (`test_c4_gpu_local`, `test_c4b_gpu_execucao`, `test_c4h_ponte_de_midia`, `test_cadeia_do_audio_offline`) — ambiente da máquina, não a R1.
- **Ensaio em cópia fiel do vivo** (como o plano da M5G): worktree em `8eec2e2a` + os 14 ficheiros sujos do vivo copiados (só leitura no vivo; JSON conferido).

```
1. merge --no-ff e07abe2d            rc=0  conflitos=0
2. livros sujos (14)                  IGUAIS byte a byte
3. arvore vs e07abe2d                 0 ficheiros diferentes
4. worker/gatilho/supervisor importam; rota_do_scrap_youtube NAO carregado
   598 contratos validos, 0 invalidos
   reparo elegivel no livro vivo copiado: 504 (432 REPAIR_CONTRACT + 72 VALIDATE_ROUTE)
5. testes na copia instalada: 121 corridos, 1 FAIL = test_nivel_da_fila.test_5
   (o mesmo FAIL em 8eec2e2a sem instalar nada — ja dito no plano da M5G); livros IGUAIS depois
6. DESFAZER git reset --keep 8eec2e2a  rc=0  0 codigo diferente  livros IGUAIS
   (a copia C:/ens-r1 foi apagada no fim; o vivo nao foi tocado)
```

- **Writeset novo:** `scripts/reparo/R1-WRITESET.json` (v2). Instala por `git merge --no-ff reparo-fontes-v2` no ramo do bot, nunca por `checkout` de ficheiros. Escreve 12 ficheiros de código + a declaração e os gerados do mapa; nenhum livro na instalação. Em funcionamento: contratos, livro de estado, fila, evidência. **Já não escreve** `SOURCE-ID-ALLOCATION-V1.json` (isso vinha do YouTube).
- **NÃO instalado.** Ordem do coordenador: a R1 só com OK dele, um escritor no vivo de cada vez.

## 8 · Reensaio sobre o vivo atual (24/09, D28)

O vivo passou a `fca4f2b6` (= `8eec2e2a` + BC4b `ebe000fb` + docs BC5 `4a5afc27`). Só o mapa se sobrepunha à R1: juntei `fca4f2b6` em `reparo-fontes-v2` (`17240355`; declaração do mapa unida, gerados pela cadeia em `3be6265a`), para a instalação entrar sem conflito.

Cópia fiel (`C:/ens-r1`: worktree em `fca4f2b6` + os 14 ficheiros sujos do vivo, só lidos):

```
1. merge --no-ff 3be6265a              rc=0  conflitos=0
2. livros sujos (14)                   IGUAIS byte a byte
3. arvore vs 3be6265a                  0 ficheiros diferentes; rota_do_scrap_youtube nao existe / nao carrega
4. 598 contratos validos, 0 invalidos; reparo elegivel: 505 (432 REPAIR_CONTRACT + 73 VALIDATE_ROUTE)
5. testes na copia instalada: 121, 1 FAIL = test_nivel_da_fila.test_5 (pre-existente); livros IGUAIS
6. DESFAZER git reset --keep fca4f2b6  rc=0  0 codigo diferente  livros IGUAIS
```

### 8.1 · Medição com rede na cópia do vivo atual (`scripts/reparo/R1-REENSAIO-ANTES-DEPOIS-fca4f2b6.json`)

Foto do vivo `%TEMP%/r1v3-snap-20260924T122126Z` (bot parado pela BC5), 4 bancas em `3be6265a` por fatia de anfitrião, portão de egresso IT = PASS antes de arrancar; robots da casa, 2 s entre pedidos ao mesmo anfitrião.

```
READY na copia                       143 -> 189  (+46)
das 432 «para consertar»             29 READY · 389 CONTRACTED_CANARY_FAILED (recusa com motivo) · 11 robots proibe · 3 AUTH
das 73 «testar de novo»              17 READY (6 so com o re-canario; 11 depois de reparadas)
fontes contadas em duas bancas       0
```

Motivo final das que não chegaram (reparo): 148 item não é matéria · 117 sem família de itens · 78 a entrada é uma notícia · 44 página de serviço · 40 capa no canário · 29 sem identidade · 17 família estática · 10 duplicada · 10 robots.

⚠️ Continua a valer §4: parte das READY novas pode ser página fixa de título longo (IT-T12-134, IT-T2-063, IT-T7-105, IT-T7-041, IT-T12-044 estão na lista) e IT-T9-015 aponta para «lavora-con-noi». Ler antes de uma onda da Big Collection.

**Pronto para instalar** depois da 1.ª onda, com o OK do coordenador: `git merge --no-ff reparo-fontes-v2` no ramo do bot; desfazer `git reset --keep fca4f2b6`.

## 9 · Provas fora do Git (regra nova da coordenação, 24/09)

- Baterias por nome: resumo com a lista de vermelhos por nome em `scripts/reparo/R1-SUITE-POR-NOME.json` (no ramo); os ficheiros completos ficam em `%TEMP%` com o sha256 escrito nesse JSON.
- Fotos dos livros do vivo usadas nas medições (dados de produção, 13 MB cada, não se versionam):

| foto | LIFECYCLE-LEDGER-V1.json | LIFECYCLE-QUEUE-V1.json | italy_contracts_curator.json |
|---|---|---|---|
| `%TEMP%/r1v3-snap-20260924T122126Z` (reensaio) | `c63fe0fbfb3519d7ab83fde1b73fc5586cc29730ca2e08c30e59745df729d461` | `4786b390277ca0e2a7ab334fd36d62a8adca77768ffe65da560063035fa3111b` | `a7abd28091abdef10f49ae4e86bf38887fdc1847ffc3f5cb779eee25c86abc84` |
| `%TEMP%/r1-snap-20260923T182146Z` (1.ª medição) | `1931bc2ea9f86412b790923bf44c8cc84c608318bba3db7903f6a629c1632aa6` | `aabe131ffb33342d8c279125b081bb19b9e812622058976b3fb7923eacd3540d` | `a7abd28091abdef10f49ae4e86bf38887fdc1847ffc3f5cb779eee25c86abc84` |

- Ensaio em cópia fiel: sha256 dos 14 livros sujos antes/depois em `%TEMP%/r1v3-sha-antes.txt` (`83fbf6505c14d6fcd378bddc231367ea7da12b5b88b2a9dcbc6ebe15cdc4b848`); a cópia `C:/ens-r1` e as bancas foram apagadas.
- O resultado de cada medição com rede está no ramo: `R1-REENSAIO-ANTES-DEPOIS-fca4f2b6.json`, `R1-ANTES-DEPOIS-EM-COPIA.json`, `R1-ANTES-DEPOIS-EM-COPIA-SEM-FILTRO.json`.

