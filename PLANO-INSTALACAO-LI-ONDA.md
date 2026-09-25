# PLANO DE INSTALAÇÃO — LI-ONDA (a onda social do LinkedIn) na produção

Missão: `auditoria-madrugada/missao-li-onda.txt`. Ramo `social-onda2-v1`. **Nada instalado: quem instala é o coordenador.**
Produção medida em 25/09 ~02:00: bot `servico-20260923-0923` @ **5ba9647e** (R1 instalada), com 14 livros em uso;
ponte `cutover-20260923-0923` @ **84c235da**, com 3 livros em uso.

## Decisões tomadas — D37 (bot Luciano, 25/09)
1. **Robots do LinkedIn:** a D23 cobre o robots.txt **só** para vídeo público de ORGANIZAÇÃO no LinkedIn.
   Cada objeto leva campos SEPARADOS. Feito em `coleta/adaptador_linkedin.politica_do_objeto`, usada no bruto e no envelope:
   `OWNER_AUTHORIZED=SIM` · `PLATFORM_POLICY_STATUS=DISALLOWED` · `ROBOTS_STATUS=DISALLOW_ALL` · `ROBOTS_URL=https://www.linkedin.com/robots.txt`
   · `ROBOTS_MEDIDO_EM=2026-09-08` (a medição do cabeçalho de `leis/social_matriz.py`) · `DECISAO_DO_ROBOTS=D37`.
   Medido antes: o objeto do canário de 24/09 tinha os dois primeiros e NÃO tinha `ROBOTS_*`.
   Teste `tests/test_d37_campos_de_politica.py` (4) e mutação `provas/_mutantes_d37.py` **6/6 mortos**.
   ⚠️ Para o coordenador: a rota de VÍDEO DE PESSOA no LinkedIn (D24) também bate num robots proibido. Pela D37/D34
   ela deixa de estar coberta, mas o código dela continua ligado (`video_de_post_publico`). Não mexi — é decisão.
   Os objetos do canário de 24/09 foram julgados antes da D37 e não têm `ROBOTS_*`. Os da onda já os levam.
2. **População 344 → 857 aprovada.** `fonte_do_atlas` só RECONHECE o SOURCE_ID do registo canónico de alocação.
   Não promove, não cria READY: quem promove continua a ser a régua social com o canário.

**Ordem (D35.4):** a LI-ONDA instala-se DEPOIS da 2.ª onda web.

## O que vai para a produção
`social-onda2-v1` (sobre `cffaad2d`, que já está na produção): SOC2 (a mesma `cac84a45` da CUR-PRONTA), SOC4 1–2
(Scrap para todo território; @handle resolvidos), QUALIFY LinkedIn (D23) + ligação oficial obrigatória, contrato
`video-linkedin`, `regua_social.py`, `SOCIAL/v1` no portão (`ready_split` + `collection_gate`), `plano_onda_social.py`,
`semear_qualify_social.py`, `fonte_do_atlas` 3.º emissor, `superficie/rede.py` de consenso (idêntico à produção) e o mapa.

## Ensaio (feito, 25/09 ~02:00) — cópia fiel do vivo em `C:/ens-li/bot`
Worktree em 5ba9647e + os 14 livros do vivo (copiados só para leitura; foto em `C:/ens-li/foto`, sha em `C:/ens-li/foto.sha`).
O `git merge` é recusado a esta sessão pela permissão da máquina: a junção foi **calculada** com
`git merge-tree --write-tree 5ba9647e social-onda2-v1` e os 58 ficheiros de código foram postos na cópia a partir
dessa árvore. As 15 geradas do mapa ficaram na versão da produção.

```
JUNCAO bot   (5ba9647e + social-onda2-v1)  conflitos de CODIGO = 0; so geradas do mapa (13 json + 2 docs)
JUNCAO ponte (84c235da + social-onda2-v1)  conflitos de CODIGO = 0; idem
LIVROS tocados pela juncao                 bot 0 de 14 · ponte 0 de 3
TESTES na copia instalada                  247 corridos, 247 OK (17 suites: social, worker, portao, ready_split, atlas, t10...)
PORTAO com os livros vivos (antes)         READY 144 · elegiveis 38
semear_qualify_social --aplicar            40 QUALIFY novas
worker (sem rede)                          QUALIFY 37 OK + 3 BLOCK (territorio NAO SEI) · BUILD_CONTRACT 37 · VALIDATE_ROUTE 37
numeros cunhados                           37 — IGUAIS, um a um, aos do ensaio de 24/09 (mesmo slug -> mesmo SOURCE_ID)
regua_social (provas do canario de 24/09)  9 READY · 23 ZERO legitimo · 5 FALHA
PORTAO depois                              READY 153 · elegiveis 47  (+9, todas video-linkedin)
DESFAZER (codigo fora)                     so os 14 livros ficam sujos; sha256 14/14 iguais
```
O canário de 24/09 serve à produção porque os números saíram iguais. Voltar a bater em 37 páginas violaria o
limite desta noite (≤ 5 visitas por site).

### Re-ensaio sobre a produção 7b769819 (FILA-ÚNICA), 25/09 ~03:00 — `C:/ens-li2`
```
JUNCAO bot (7b769819 + social-onda2-v1)   conflitos de CODIGO = 0 · livros tocados 0 de 14
candidatas LinkedIn                        44 -> 68 (FILA-UNICA); com identidade provada: 40 (as 24 novas nao tem site oficial a apontar)
worker FILTRADO so LinkedIn, proxy fechado QUALIFY 37 OK + 3 BLOCK · BUILD_CONTRACT 37 · VALIDATE_ROUTE 37 · so tarefas sem rede
numeros                                    37 IGUAIS aos de 24/09
regua                                      9 READY · 23 ZERO · 5 FALHA
PORTAO                                     elegiveis 46 -> 55 (+9)
```
⚠️ **INCIDENTE (25/09 02:38–02:48, meu):** a primeira tentativa deste re-ensaio correu `worker.correr()` sem filtro.
A fila viva tinha ~200 tarefas de outras frentes, e a cópia fez 81 VALIDATE_ROUTE + 83 CANARY em 52 sites reais
(alguns com mais de 5 visitas). Parado por TaskStop + Stop-Process. Nada escrito na produção. Os livros da cópia
foram repostos da foto e o ensaio refeito com `curadoria/ensaio_so_linkedin.py`, que filtra a fila e rebenta
se aparecer tarefa com rede. **Para a instalação:** a semeadura no vivo põe as 40 na MESMA fila que o bot já tem,
e ele trata-as pela ordem de prioridade dele; os números podem sair diferentes se o bot qualificar outras
candidatas antes — o passo 6 (conferir os números) existe por isso.

### Bateria antes/depois sobre a produção 7b769819 (livros originais, sem rede), 25/09 ~04:15
```
producao pura (C:/ens-base)            276 testes · 27 falhas
producao + social-onda2-v1 (ens-base2) 367 testes · 27 falhas — as MESMAS; 0 novas, 0 sumidas
as 27 de base                          26 em tests.test_fila_italia_decisoes (25 candidatas CAND-1174..1198 sem nota
                                       + o guarda D24) = FILA-UNICA · 1 em test_reconciliar_livros.test_zy_censo
                                       (1047 != 1065, igual com e sem o meu codigo)
DESFAZER no re-ensaio                  so os 14 livros sujos; sha256 14/14 iguais
```
⚠️ **O que o re-ensaio apanhou, e já está consertado (commit cb183ea9):** com as 9 promovidas no livro, os testes do
portão que leem o livro real reprovavam 22 vezes. Eles exigiam que toda elegível fosse `DETAIL/v1` com INDEX_URL e os
quatro passos. A reconciliação da ponte e o red team do ciclo de vida chamavam READY_LEGACY à promoção social.
Agora: o painel do portão conta `READY_SOCIAL_TOTAL` à parte; `reconciliar_livros` e `red_team_lifecycle` aceitam
`REGUAS_QUE_ADMITEM`; os testes do portão leem a prova social (veredito READY da régua, fase do contrato).
**Isto falharia na produção logo depois do passo 7 (régua), e não na instalação.**
A lista congelada da Grande Coleta (`ferramentas/big_collection/coorte_unica.py`) é só para a web: parte do plano do
coletor web. A onda social tem a sua própria lista (`plano_onda_social.py`) e não passa por ali.

## WRITESET

| peça | na INSTALAÇÃO escreve | em FUNCIONAMENTO passa a escrever | livros do vivo tocados na instalação |
|---|---|---|---|
| bot | código de `curadoria/`, `leis/fonte_do_atlas.py`, `pedido/receitas.py`, `coleta/italy_pilot_collect.mjs`, `coleta/adaptador_linkedin.py` (D37: campos de robots em cada objeto), `regras/italy_contracts.mjs`, `scripts/desbloqueio/`, `provas/`, testes, docs, workflows, mapa (73 ficheiros na junção) | **nada novo por si.** Depois da SEMEADURA (passo 5), o worker escreve os livros de sempre: `SOURCE-ID-ALLOCATION` (+37), `italy_contracts_curator.json` (+37 contratos `SCRAP_FASE`), `LIFECYCLE-LEDGER/-QUEUE/-EVIDENCE` | 0 de 14 |
| ponte | a mesma junção sobre 84c235da | nada novo (lê o portão com `SOCIAL/v1`) | 0 de 3 |
| semear (passo 5) | `LIFECYCLE-QUEUE-V1.json` (+40 QUALIFY), **só com o bot parado** | — | 1 (a fila), por um escritor |
| régua (passo 7) | `LIFECYCLE-LEDGER/-EVIDENCE` (+9 READY, +5 FALHA), **só com o bot parado** | — | 2, por um escritor |

## Os passos (coordenador)

**0 · Fora do vivo:** criar `FINAL` = junção de `5ba9647e` com `origin/social-onda2-v1`. As 15 geradas levam `--theirs`,
e depois a cadeia do mapa (REGERAR → commit → VALIDAR → PORTOES_POS_COMMIT) sob o LOCK-PESADO. `SYSTEM_MAP_CHECK=PASS`.
Publicar `FINAL`.
**1 · Medir antes:** bot @ 5ba9647e e ponte @ 84c235da; só os 14 e os 3 livros sujos; um supervisor, um observador; worker IDLE.
**2 · Parar** (`PARAR.flag`) e **foto dos livros** (como no M5G, passo 2).
**3 · Bot:** `git merge --no-ff FINAL` → 0 conflitos. **Ponte:** a mesma junção. Conferir os livros contra a foto: nada «MUDOU».
**4 · Relançar e deixar correr** até o worker ficar IDLE.
**5 · Semear (bot parado):** `py curadoria/semear_qualify_social.py --aplicar --vivo` → «40 novas». Relançar. O worker faz
QUALIFY → BUILD_CONTRACT → VALIDATE_ROUTE sem rede. Esperado: 37 CANARY_PENDING, com os mesmos números do ensaio.
**6 · Conferir os números:** os slugs das 37 → SOURCE_ID têm de ser os do ensaio (`curadoria/SOC-ONDA2-ENSAIO-QUALIFY-V1.json`).
Se algum diferir, as provas de 24/09 não servem para esse número: canário novo só para ele (≤ 5 por noite).
**7 · Régua (bot parado):** `py curadoria/regua_social.py --corridas <resultados do canario> --envelopes <envelopes> --aplicar --vivo`
→ 9 READY. Relançar. Portão: 38 → 47.
**8 · Onda (D37 tomada; só DEPOIS da 2.ª onda web, D35.4):** `py curadoria/plano_onda_social.py` (só plano) e depois a mesma lista pelo orquestrador,
com o Pedido montado em processo, **em 2 lotes (5 + 4), ≥ 1 h entre lotes** (≤ 5 visitas por site por noite).

### ↩️ DESFAZER
Código: `git -C $VIVA reset -q --keep 5ba9647e` e `git -C $CASA reset -q --keep 84c235da`. Livros: iguais à foto (provado no ensaio).
Depois da semeadura e da régua, o livro guarda as transições (append-only). Desfazê-las é repor a foto do passo 2 — decisão do coordenador.

## A onda LinkedIn — só plano (`plano_onda_social.py` na cópia da produção)
9 pedidos, um por conta, todos `video-linkedin` → `scrap-colheita` (`correr(so_plano=True)` = PLANO, 0 filtros perdidos):
IT-T11-014, IT-T2-137, IT-T5-160, IT-T5-164, IT-T7-167, IT-T7-171, IT-T7-173, IT-T9-024, IT-T9-025.
Rede: portão de consenso ANTES e DEPOIS de cada pedido; por pedido, 1 página linkedin.com + até 2 MP4 e 2 legendas
em dms.licdn.com; sem login, sem conta, sem pagamento; teto 2 por conta.

**Previsão honesta** (medida no canário destas 9, teto 2): **12 vídeos**, **7 com legenda**, **2 itens na Sala**
(a Admissão decide; foi o que passou no canário), cerca de **12 minutos** de relógio. Ressalvas:
- a página anónima mostra poucos posts — com teto 2, o máximo é 18;
- o LinkedIn pode servir muro de login a qualquer visita (vira FALHA, não se contorna);
- **os itens entram com DOCUMENT_ID = NÃO SEI**: a regra do nome do documento vive na tabela do coletor, e os
  contratos do Curator não chegam lá. A identidade da plataforma (ACTIVITY_ID) vem inteira. Dono: CUR-PRONTA/coordenador.

## Fora desta instalação (bloqueios nomeados)
- YouTube: 0 prontas (a chave só existe no GitHub; o item de áudio vem sem data, autorização e canal). Dono: engenheiro do Scrap.
- Instagram: 0 (não há rota para listar uma conta). Dono: o dono do projeto (decisão nova).
- A ponte continua a não enfileirar LinkedIn (D15). A semeadura é única; o caminho contínuo exige mexer na D15.
