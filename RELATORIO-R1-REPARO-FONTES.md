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

## 10 · Revisão uma a uma das +46 READY (24/09, `scripts/reparo/R1-REVISAO-READY.json`)

Banca nova (foto do vivo 12:21Z + `reparo-fontes-v2`), reparo re-corrido só para as 46, portão de egresso por **consenso** (2×IT + 1×US = PASS; o portão antigo desta árvore só tinha o ipinfo, em 429). Detector capa/matéria = o instalado. **As 46 voltam a chegar a READY.** Depois reabri o item de cada uma e li título, h1, data e início do texto.

**27 LIMPAS · 19 SUSPEITAS.** Das limpas, 4 são artigos para assinantes (só o início é público) e 2 têm tema a confirmar.

| fonte | veredito | motivo |
|---|---|---|
| IT-T12-023 | SUSPEITA | página inicial de um projeto (Contratto di Fiume), fixa — não é notícia |
| IT-T12-042 | SUSPEITA | página de serviço: Área Pessoal de Tributos da Região |
| IT-T12-043 | SUSPEITA | página de serviço: prazos do imposto automóvel (fora do agro) |
| IT-T12-044 | SUSPEITA | página fixa de projeto PNRR («1000 Esperti»), sem fluxo de notícias |
| IT-T12-073 | SUSPEITA | página de projeto das Olimpíadas 2026 (comboios) — fora do agro |
| IT-T12-081 | SUSPEITA | página fixa institucional (Accordo per lo Sviluppo e la Coesione) |
| IT-T12-102 | SUSPEITA | repartição: página do Gabinete da Região |
| IT-T12-134 | SUSPEITA | página educativa fixa para alunos («Conosci la frutta») |
| IT-T2-033 | SUSPEITA | página temática fixa (campos eletromagnéticos), não notícia |
| IT-T2-063 | SUSPEITA | página fixa institucional (acreditação dos laboratórios) |
| IT-T2-070 | SUSPEITA | o texto lido é o do leitor Issuu («Transform any piece of content…»), não a publicação |
| IT-T5-041 | SUSPEITA | crpv.it reencaminha para a Ri.Nova; o texto lido é a apresentação institucional |
| IT-T7-031 | SUSPEITA | página de projeto/campanha (Being Organic in EU), não notícia |
| IT-T7-041 | SUSPEITA | página fixa de atividade do consórcio (difesa idraulica) |
| IT-T7-105 | SUSPEITA | página de serviço: lista fixa de feiras |
| IT-T7-150 | SUSPEITA | ficha de curso de formação (catálogo), não notícia |
| IT-T8-010 | SUSPEITA | página de serviço: descrição da newsletter UIVLex |
| IT-T9-015 | SUSPEITA | «Lavora con noi» — página de recrutamento |
| IT-T9-019 | SUSPEITA | o item é a própria listagem «Articoli e pubblicazioni», não uma matéria |
| IT-T12-024 | LIMPA | notícia/publicação datada ou com título de matéria |
| IT-T12-075 | LIMPA | notícia/publicação datada ou com título de matéria — ⚠️ notícia, mas de educação (tema a confirmar pelo dono) |
| IT-T12-104 | LIMPA | notícia/publicação datada ou com título de matéria |
| IT-T12-117 | LIMPA | notícia/publicação datada ou com título de matéria |
| IT-T12-129 | LIMPA | notícia/publicação datada ou com título de matéria |
| IT-T12-130 | LIMPA | notícia/publicação datada ou com título de matéria — ⚠️ artigo para assinantes: só o início é público |
| IT-T12-131 | LIMPA | notícia/publicação datada ou com título de matéria — ⚠️ artigo para assinantes: só o início é público |
| IT-T2-032 | LIMPA | notícia/publicação datada ou com título de matéria |
| IT-T2-037 | LIMPA | notícia/publicação datada ou com título de matéria |
| IT-T2-050 | LIMPA | notícia/publicação datada ou com título de matéria |
| IT-T3-023 | LIMPA | notícia/publicação datada ou com título de matéria — ⚠️ artigo para assinantes: só o início é público |
| IT-T5-056 | LIMPA | notícia/publicação datada ou com título de matéria |
| IT-T5-080 | LIMPA | notícia/publicação datada ou com título de matéria |
| IT-T5-104 | LIMPA | notícia/publicação datada ou com título de matéria — ⚠️ notícia universitária de algoritmos (tema a confirmar pelo dono) |
| IT-T5-111 | LIMPA | notícia/publicação datada ou com título de matéria |
| IT-T5-113 | LIMPA | notícia/publicação datada ou com título de matéria |
| IT-T7-019 | LIMPA | notícia/publicação datada ou com título de matéria |
| IT-T7-048 | LIMPA | notícia/publicação datada ou com título de matéria |
| IT-T7-049 | LIMPA | notícia/publicação datada ou com título de matéria |
| IT-T7-103 | LIMPA | notícia/publicação datada ou com título de matéria |
| IT-T7-125 | LIMPA | notícia/publicação datada ou com título de matéria |
| IT-T7-139 | LIMPA | notícia/publicação datada ou com título de matéria |
| IT-T7-163 | LIMPA | notícia/publicação datada ou com título de matéria |
| IT-T8-022 | LIMPA | notícia/publicação datada ou com título de matéria |
| IT-T8-024 | LIMPA | notícia/publicação datada ou com título de matéria |
| IT-T8-041 | LIMPA | notícia/publicação datada ou com título de matéria |
| IT-T8-042 | LIMPA | notícia/publicação datada ou com título de matéria — ⚠️ artigo para assinantes: só o início é público |

Os sinais automáticos (`CAMINHO_DE_SERVICO`, `SEM_DATA`) só apontam; 4 foram falsos («contributi» casa «tribut», «corso di aggiornamento» é notícia). O veredito é da leitura.
Para a REND: o contrato reparado de cada fonte (INDEX_URL, LINK_PATTERN) e o item lido estão no mesmo JSON.

## 11 · Plano de instalação da R1 revista sobre o vivo atual (24/09, `5c4daf5a`)

O vivo passou a `5c4daf5a` (EGR: portão de egresso por consenso). Juntei-o em `reparo-fontes-v2` (`df1e9f87`, mapa em `e7cba2d6`): o ramo já traz o portão novo e a instalação entra sem conflito.

**Ensaio em cópia fiel** (`C:/ens-r1`: worktree em `5c4daf5a` + os 14 livros sujos do vivo, só lidos; apagada no fim):

```
1. merge --no-ff e7cba2d6                rc=0  conflitos=0
2. livros sujos (14)                     IGUAIS byte a byte
3. arvore vs e7cba2d6                    0 ficheiros diferentes; rota_do_scrap_youtube nao carrega
4. 598 contratos validos, 0 invalidos; a espera: 505 (432 REPAIR_CONTRACT + 73 VALIDATE_ROUTE)
5. testes na copia instalada: 136, 1 FAIL = test_nivel_da_fila.test_5 (pre-existente); livros IGUAIS
6. DESFAZER git reset --keep 5c4daf5a    rc=0  0 codigo diferente  livros IGUAIS
```

**Quantas READY saem** (4 bancas com rede, foto do vivo 20:28Z, portão por consenso = PASS IT; `scripts/reparo/R1-INSTALACAO-ENSAIO-5c4daf5a.json`):

```
READY                                        143 -> 168  (+25 = 21 limpas + 4 ACESSO_PARCIAL) = o esperado
limpas/parciais que nao chegaram             0
retidas pela revisao                         21 (16 servico/institucional, 2 texto nao e materia,
                                                1 lista como item -> CANARY_FAILED; 2 tema -> SEMANTIC_REVIEW)
REVISAO_PENDENTE (reparada, ninguem leu)     1 = IT-T8-058 (Agrisole)
nota ACESSO_PARCIAL no livro                 inteira (IT-T8-042: «... · ACESSO_PARCIAL: artigo para assinantes: só o início é público»)
```

**Passos** (padrão B4/M2e; só com o OK do coordenador, um escritor no vivo):
1. Fotografar processos (1 supervisor, 1 ponte), sha256 dos 14 livros sujos, cópia em `C:\cutover\r1-<hora>\antes`.
2. `PARAR.flag` → o supervisor sai sozinho; confirmar 0 worker.
3. No ramo do bot: `git merge --no-ff origin/reparo-fontes-v2`; conferir os livros com o sha256 de antes; push.
4. Portão de egresso por consenso = PASS IT → apagar `PARAR.flag` → relançar o supervisor como hoje.
5. Provar ao vivo: tarefas REPAIR_CONTRACT a aparecer na fila; READY a subir para ~168 em 2–3 h; as 21 retidas com o motivo no livro.

**DESFAZER:** `PARAR.flag` → `git reset --keep 5c4daf5a` → relançar. O que o bot já escreveu fica no livro (append-only); cada contrato reparado guarda o anterior em `REPARO_DE_CONTRATO.ACQUISITION_ANTERIOR`.

**Falta:** repetir SÓ o ensaio com a junção da IA-CUR (conserto do leitor do canário em `canario.py`; o ramo dela já tem a R1 antiga `9c05877e`) quando ela publicar a medição do livro inteiro.

## 12 · Ajuste antes da instalação: o vivo passou a `55b50a63` (régua T2)

Juntei `55b50a63` (= `origin/regua-t2-v1` @ `84c235da` + testes EGR) em `reparo-fontes-v2` (`ba3d2153`); só conflitavam gerados, regerados pela cadeia com LOCK-PESADO (`3de79d75`).

**Ensaio em cópia fiel** (`C:/ens-r1`: worktree em `55b50a63` + os 14 livros sujos do vivo; apagada no fim):

```
1. merge --no-ff 3de79d75               rc=0  conflitos=0
2. livros sujos (14)                    IGUAIS byte a byte
3. arvore vs 3de79d75                   0 ficheiros diferentes; rota_do_scrap_youtube nao carrega
4. 598 contratos validos; a espera 505 (432 REPAIR_CONTRACT + 73 VALIDATE_ROUTE); READY vivo 143
5. testes R1 + curador: 136, 1 FAIL = test_nivel_da_fila.test_5 (pre-existente)
   regua T2 (test_a_regra_de_t2, test_gabarito_t2_t12, test_regua_t2): 42/42 OK; livros IGUAIS
6. DESFAZER git reset --keep 55b50a63   rc=0  0 codigo diferente  livros IGUAIS
```

**READY esperadas: 25** (143 → 168). ⚠️ Não re-contei com rede sobre `55b50a63`: a VPN caiu para o Brasil (portão por consenso BR, BR, US = BLOCKED, medido 4× entre 22:00 e 22:10Z). O número da §11 vale para esta instalação porque as duas entradas são as mesmas: o código do robô é idêntico (`git diff e7cba2d6 3de79d75 -- curadoria candidatas superficie` = 0 linhas — a régua T2 não toca nesses directórios) e os 14 livros do vivo são iguais byte a byte aos da medição das 20:28Z. O que pode mudar é só o que os sites respondem hoje.

**Instalar:** `PARAR.flag` → `git merge --no-ff origin/reparo-fontes-v2` no ramo do bot → conferir livros → portão por consenso = PASS IT → relançar. **Desfazer:** `PARAR.flag` → `git reset --keep 55b50a63` → relançar.

## 14 · REVISAO-15 — as 15 em «revisão pendente» depois da instalação (25/09, ramo `reparo-fontes-v3`)

Ramo novo a partir da produção (`origin/servico-20260923-0923` @ `7cdb7ea4`). As 15 são fontes que a R1 reparou no vivo e a régua aprovou, mas ninguém tinha lido (quase todas das janelas D29: fitossanitário e agrometeo). Li cada uma pelo endereço do item e pelo retrato guardados no vivo; para 5 em que o endereço não chegava, 1 pedido por domínio (5 pedidos, portão por consenso = PASS IT, robots da casa; páginas com sha256 em `scripts/reparo/R1-REVISAO-15.json`).

**3 LIMPAS · 11 SUSPEITAS · 1 NÃO SEI**

| fonte | veredito | motivo |
|---|---|---|
| IT-T2-157 | LIMPA | notícia do Serviço Agrometeo Regional das Marcas (AMAP), datada 18/03/2026 — o tema da fonte |
| IT-T7-171 | LIMPA | notícia do Collegio dei Periti Agrari (CREA: IA com imagens RGB para o NDVI), datada 12/02/2026 |
| IT-T8-064 | LIMPA | artigo da revista Italus Hortus (SOI) sobre biossegurança da videira, 2024 |
| IT-T2-135 | ALVO_ERRADO | arquivo de boletins agrometeo da ARPA Lombardia, mas o padrão reparado aponta para «temi-ambientali/rifiuti» (gestão de resíduos) |
| IT-T3-030 | ALVO_ERRADO | fonte de boletins de defesa da flavescência dourada; o padrão aponta para o guia do besouro japonês (scarabeo-giapponese) |
| IT-T3-041 | ALVO_ERRADO | Serviço Fitossanitário do Lazio; o padrão aponta para «qualità produzioni» (produtos certificados), não para avisos fitossanitários |
| IT-T5-189 | ALVO_ERRADO | Dip. Scienze Agrarie de Palermo, mas o item é a 110.ª Targa Florio (corrida de automóveis) na «terza missione» da universidade |
| IT-T8-058 | ALVO_ERRADO | fonte Agrisole, mas o padrão pega todo o Sole 24 Ore (/art/); o item é a Acea no Peru (águas residuais), não agro |
| IT-T8-060 | LISTA_COMO_ITEM | o item é o arquivo de notícias do ano 2019 (notizie?y=2019), uma listagem, não uma notícia |
| IT-T7-168 | NAO_SEI | entrada «aiia_news», mas o padrão pega páginas de congressos (item: congresso AIIA 2022); não sei se é o fluxo que se quer desta fonte |
| IT-T2-159 | SERVICO_OU_INSTITUCIONAL | «Le attività» do SIARL: página fixa a descrever o serviço, não boletim nem notícia |
| IT-T3-047 | SERVICO_OU_INSTITUCIONAL | página fixa de serviço do fitossanitário do Piemonte (registo de atividades de produção/comércio de vegetais), não aviso |
| IT-T3-049 | SERVICO_OU_INSTITUCIONAL | o item é «Accessibilità e uso del sito» da Região Toscana, não o fitossanitário |
| IT-T3-052 | SERVICO_OU_INSTITUCIONAL | página fixa do fitossanitário do Veneto («attività vivaistica»), não aviso nem boletim |
| IT-T7-219 | SERVICO_OU_INSTITUCIONAL | página de procedimento («come richiedere l'accreditamento di un evento formativo»), não notícia |

**Mecanismo (o mesmo da R1, sem promover à mão):**
- as 15 entram em `curadoria/REVISAO-READY-V1.json`, com `REVISTO_EM`;
- classes novas na trava: `ALVO_ERRADO` (o padrão aponta para outro tema ou secção) e `NAO_SEI` — as duas retêm com o motivo no livro;
- ⚠️ buraco achado: estas fontes já tinham sido reparadas e estavam paradas; nada as voltava a medir. O gatilho passa a re-medir **uma vez** (VALIDATE_ROUTE) a fonte cuja leitura (`REVISTO_EM`) é mais nova que o último canário. A LIMPA sai READY pela régua; a SUSPEITA fica com `REVISAO_R1: <classe>: <motivo>` no livro.

**Ensaio em cópia fiel do vivo `7cdb7ea4`** (rede fechada; `C:/ens-r15`, apagada):

```
1. merge --no-ff f5281334              rc=0  conflitos=0   (so 5 ficheiros: revisao, gatilho, trava, teste, prova)
2. livros sujos (14)                   IGUAIS byte a byte
3. testes: 140, 1 FAIL = test_nivel_da_fila.test_5 (pre-existente); livros IGUAIS
4. decisao com os contratos do vivo:   as 15 voltam a ser medidas (15 VALIDATE_ROUTE, 0 outras)
                                       3 promovem se o canario passar (IT-T2-157, IT-T7-171, IT-T8-064)
                                       12 retidas: 5 ALVO_ERRADO, 5 servico, 1 lista, 1 NAO_SEI
5. DESFAZER git reset --keep 7cdb7ea4  rc=0  0 codigo diferente  livros IGUAIS
```

**Quantas ficam prontas:** +3 (183 → 186), se o canário de hoje ainda passar nas 3 — é rede, e o site pode ter mudado. Testes: 105 dos ficheiros afectados + 5 novos; mutação 5/5.

