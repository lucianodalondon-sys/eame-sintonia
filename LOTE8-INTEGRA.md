# LOTE8-INTEGRA — um lote de integração sobre a produção viva (dono 27/09 · bot Luciano)

```text
RAMO      claude/lote8-integra-zobt7p
BASE      b273660b6  (= origin/servico-20260923-0923, produção viva, LOTE7-INTEGRA) — ancestral deste ramo:
          a instalação é FAST-FORWARD
REDE      nenhuma. Nada colhido. Nada instalado. Livros vivos (curadoria/*-V1.json, data/collection-ledger,
          candidatas/FONTES-CANDIDATAS.json) NÃO tocados: `git diff --name-only b273660 HEAD` → 0 desses.
SHA FINAL a cabeça de origin/claude/lote8-integra-zobt7p (o commit que contém este ficheiro não pode conhecer o
          próprio SHA; o relatório da sessão di-lo). Código medido: 609a471 (depois dele só entram o harness da porta `4bc57cd`, provas, este relatório e o mapa)
MÉTODO    o do LOTE7-INTEGRA: merge aditivo ramo a ramo, conflito resolvido por regra escrita, bateria por nome
          antes/depois, mutação, mapa regerado pela cadeia, checklist com SHA final.
```

## 1 · Os merges (declarados, `--no-ff`, nenhuma história reescrita)

| # | ramo | cabeça | base do ramo | commit do merge | o que trouxe |
|---|---|---|---|---|---|
| 1 | `claude/coleta-continua-servico-dm3efk` | `e1bb56b` | `18461b92d` | `b77fef0` | coleta contínua D86: agendador por FONTE sobre o plano das rodadas (`ferramentas/big_collection/coleta_continua.py`), ensaio a seco, 50 testes |
| 2 | `claude/feed-discovery-italy-sources-hr8vlb` | `e18b75a` | `18461b92d` | `99a367c` | FEED-LIGADO: FEED_DISCOVERY pela porta (`regras/ligar_feeds.py` + pacote dos 13), BODY_FROM_FEED sem pedido, robots 1×/24 h, GET condicional (304 conta no teto), `Sitemap:` só medido |
| 3 | `claude/social-at-sala-7wu107` | `c3ebff7` | `18461b92d` | `23ba5b1` | SOCIAL até a Sala: desbloqueio pelas portas D22/D23/D24/D106, régua social por PROVAS, feed do canal YouTube (fechado pela matriz), entrada por URL achado |
| 4 | `claude/declare-problem-contract-lj7kfp` | `45b34db` | `c551062` | `93481d4` | contrato `PROBLEMA/v1` na Collection (dono `leis/afirmacao_da_fonte.py`), CAP-WIN e motor leem só pelo contrato, reprocessador da Sala |
| 5 | `claude/adama-linking-gateway-a2fewj` | `82c013e` | `c551062` (+ pote-v2 `8982ce4`) | `8d01ccb` | LIGAÇÃO-ADAMA D123: `ligacao_adama` na porta, 5 estados, o pote recusa sem ligação, fila BULAS_A_LER |
| 6 | `claude/acervo-intelligence-processing-148qau` | `33804ec` | `c551062` (+ pote-v2 `8982ce4`) | `71ce7a6` (+ `dcfd2ac`) | o acervo (2.080 itens) pelas capacidades da Intelligence até o pote v2 |

- Os ramos 5 e 6 trouxeram o pote-v2 **`8982ce4`**, o mesmo que o lote 7 já tinha: entrou sem conflito.
- **Não entraram (por ordem):** `nuvem/porteiro-dataset-oficial-v1` (sem entrega provada no Git),
  `claude/casco-publication-minimum-5q7kbw` (cancelada pelo dono), `claude/casco-r7-publication-yb7nsg` (desenha
  recusados), rete-voci.

## 2 · Conflitos — cada um com a sua regra

| merge | conflitos | regra |
|---|---|---|
| 1 | 14, **todos gerados** (`system-map/data/*.generated.json`, `state` do cliente, CENSO) | **R1 · gerado em conflito → lado do HEAD, REGERADO pela cadeia no fim** (gerado não se edita à mão) |
| 2 | gerados (INDICE, CENSO, LEIA-ANTES) + `architecture.declared.json` (C-IT-COLETA, C-IT-CONTRATOS) | R1 · e **R2 · as duas linhas acrescentaram frase ao FIM do mesmo `what` → união** (texto do HEAD + frase do ramo) |
| 3 | só gerados | R1 |
| 4 | só gerados; o resto entrou **igual ao ramo** (numstat conferido) | R1 |
| 5 | gerados + `architecture.declared.json` C-INT-PORTA-REFERENCIA (`what` do GRÃO do lote 7 × LIGAÇÃO-ADAMA; `why_here` só o ramo mudou) | R1 · R2 · **R3 · campo que só um lado mudou → o desse lado** |
| 6 | só gerados | R1 |

Linhas apagadas conferidas em cada merge (`git diff --numstat | awk '$2>0'`): só as que o próprio ramo apagou.
Os ajustes de teste que entraram são os **declarados pelos ramos** (test_d36 12/13/15 e test_as_duas_portas_do_scrap
no social; test_cap_win, test_porta_unica_referencia, test_boletim_do_campo, test_estudo_chaves e o sintético R7 no
PROBLEMA; fixtures do pote na LIGAÇÃO-ADAMA).

## 3 · As junções que só aparecem com os ramos juntos (e o que foi feito)

| # | junção | medido | feito | onde |
|---|---|---|---|---|
| J1 | **LIGAÇÃO-ADAMA × porta única do lote 7** | o ramo 5 nasceu sem ver a regra do GRÃO e reescrevia `NIVEIS_QUE_AUTORIZAM`/`DECLARACAO_DE_PRODUTO` dentro da porta (~l.501). A 2.ª atribuição **rebinda o global**: a linha do dono (`:102`) ficava morta — mudar a regra no dono não mudava nada | a redefinição saiu; a ligação lê o dono | `motor/porta_da_referencia.py:500` (nota), `:102` (dono) · teste `tests/test_porta_unica_referencia.py:599` J1–J3 (uma atribuição; mudar o dono muda a ligação; ligação e `autorizados` concordam par a par) |
| J2 | **LIGAÇÃO-ADAMA × PROBLEMA/v1** | os consumidores que perguntam a ligação (CAP-WIN `par_em_campo`, motor `_objeto_do_futuro`) já leem o PROBLEMA **pelo contrato** (`AF.problema_da_chave`) antes de o passar à porta — o merge juntou as duas linhas certas | nada a mudar; conferido e testado (373 + 490 testes das duas suítes juntas, OK) | `motor/cap_win.py:392-432`, `motor/motor_das_capacidades.py:672-704` |
| J3 | **acervo × LIGAÇÃO-ADAMA** | o motor passou a pedir `ctx["REF"]` e o pote recusa `SEM_LIGACAO_ADAMA`: o acervo rebentava (`KeyError: 'REF'`, 3 erros) | ctx com a porta aberta; concorrente leva a ligação que `concorrencia_meta` já pediu à porta (substância do criativo); mercado pela porta com as chaves do objeto (CROP_ID NÃO SEI → FALTA CULTURA); voz por `voce_dal_campo.extrair(referencia=…)`; o Archivio leva a ligação do objeto de origem. `POTE-ACERVO.json` **regerado**: mesmos objetos (561 competitors · 2 future · 563 archive · 2 sources; 77 recusados PROVA_INCOMPLETA), agora ligados (todos `NAO_SEI`, FALTA CULTURA); `validar_pote_v2` PASSA | `pacote/acervo_na_intelligence.py:469, 542, 587, 619, 662, 719` · ajuste de teste **declarado** `tests/test_acervo_na_intelligence.py:316` (C8 ganha `REF=None`; nenhuma asserção muda) |
| J4 | **linha-busca (lote 5) → social por URL achado** | o social lê `POSTS-PARA-O-SCRAP.jsonl` num ramo que não tinha a linha-busca. Formato compatível — **mas** a linha-busca mandava `instagram.com/<conta>/reel/<código>` (a forma do transcritor e a que o social lê) para PISTAS-DE-CONTA: esse Reel nunca chegava ao Scrap | conta opcional no molde `POSTS` | `coleta/linha_busca.py:177-182` |
| J5 | **coleta contínua × linha-busca** | a coleta contínua mede se cada linha chama a reserva de 24 h. Na árvore dela a BUSCA não existia; nesta existe e **não reserva** | nada a mudar: fica `ESPERA_LIGACAO` por `SEM_RESERVA_24H` (não entra no rodízio só por o ficheiro ter aparecido); SITES continua LIGADA depois do FEED-LIGADO | testado |
| J6 | **FEED-LIGADO × `regras/paridade_test.mjs`** | falha **nova** na bateria Node (o ramo só correu a Python): a chamada virou `await baixar(alvo.url, 2, {condicional})` e a âncora textual `await baixar(alvo.url)` sumiu. A regra continua verdadeira (decisão `:1271`, download `:1340`) | âncora = prefixo da chamada, e a regra ficou **mais forte**: TODA chamada que baixa o alvo vem depois da decisão. **AJUSTE DECLARADO** (decisão: GET condicional do FEED-LIGADO, aprovado neste lote) | `regras/paridade_test.mjs:274` |

| J7 | **social × lei 04a do curador** | falha **nova** na bateria Python intermédia: `coleta/social_por_url_achado.py` abria `curadoria/italy_contracts_curator.json` (a coleta não lê o registo do curador) | teste intacto; a leitura mudou-se para o dono dos livros e a coleta pergunta-lhe | `curadoria/desbloquear_social.py` (`livros_de_identidade`), `coleta/social_por_url_achado.py:120-130` |
| J8 | **PROBLEMA/v1 × harness de mutação da porta** | a cópia limpa de `provas/porta_unica_referencia/mutantes.py` reprovava (`FileNotFoundError …/ES-T4-001/eppo-dictionary.json`): o contrato PROBLEMA lê a tabela EPPO nos testes da porta | a cópia leva a tabela; nenhum mutante nem teste mudou | `provas/porta_unica_referencia/mutantes.py:28-30` |

Testes das junções: `tests/test_lote8_juncoes.py` (J-ACERVO 4, J-BUSCA 2, J-LINHAS 2).

### O P6 de `tests/test_pote_no_casco.mjs` — defeito do TESTE, não da regra

O `.vercelignore` não tem `-text` no `.gitattributes`; com `core.autocrlf` no Windows sai do checkout com CRLF.
`split('\n')` deixava `\r` no fim de cada linha e o `includes()` reprovava uma regra **que está lá**. Agora
`split(/\r?\n/)` (`tests/test_pote_no_casco.mjs:172-176`). Provado numa cópia com o `.vercelignore` em CRLF: teste
antigo **117/118** (P6 FAIL), corrigido **118/118**; com a linha tirada do `.vercelignore`, o corrigido reprova P6
(continua a morder).

## 4 · Bateria inteira por nome (`provas/int_r7/bateria_por_nome.py`, rede fechada, worktrees limpas)

| | módulos | testes | falhas por nome |
|---|---|---|---|
| base `b273660` (produção, worktree limpa) | 320 | 7190 | 131 |
| intermédia `7641675` (merges + junções J1–J5, mapa regerado) | 330 | 7434 | 131 |
| **final `609a471`** (código final, mapa regerado) | **330** | **7434** | **130** |

- **Novas: 0. Sumidas: 1.** A sumida é `test_o9_caminho_instrumentado.test_O9_1_o_censo_elege_este_caminho` e **não
  é conserto**: o censo desempata pelo nº de linhas, e as 4 linhas que o FEED-LIGADO pôs em `coleta/italy_executor.py`
  voltaram a eleger `coleta/executor_texto_de_pdf.py`. Coincidência medida, declarada.
- ⚠️ Medida intermédia, dita: sobre `7641675` houve **1 nova**,
  `test_integracao_04a_curator.test_a_pasta_coleta_nao_tem_executor_para_o_feed` — `coleta/social_por_url_achado.py`
  (ramo 3, que não correu esta suíte) abria `curadoria/italy_contracts_curator.json`, e a lei do teste diz que a coleta
  não lê o registo do curador. **Teste intacto**; a leitura passou para o dono dos livros:
  `curadoria/desbloquear_social.py::livros_de_identidade`, e a coleta pergunta-lhe
  (`coleta/social_por_url_achado.py:120-130`). Em `609a471` passa.
- 10 módulos novos, **0 falhas**: `test_coleta_continua` 50 · `test_ligacao_adama` 38 · `test_chave_problema` 35 ·
  `test_acervo_na_intelligence` 32 · `test_regua_social_por_provas` 22 · `test_social_por_url_achado` 20 ·
  `test_youtube_feed_sem_chave` 17 · `test_desbloquear_social` 11 · `test_feed_ligado` 8 · `test_lote8_juncoes` 8.
  `test_porta_unica_referencia` 43 → 46 (+3 da J1).
- As 130 herdadas são da base, pelo nome (lista inteira no JSON). A bateria da base mediu 320/7190/131 — **os mesmos
  números** do DEPOIS do lote 7 (`d0e0901`): a produção é aquilo que o lote 7 entregou.

Fora da bateria Python — todos os `.mjs` de teste (`regras/*test.mjs`, `tests/*.mjs`, `system-map/tests/*.mjs`),
comparados pelo nome da linha que falha:

| | ficheiros | falhas por nome |
|---|---|---|
| base `b273660` | 11 | 82 (todas `regras/italy_contract_test.mjs`) + `verificar_a_tela.mjs` RC=1 sem teste corrido (`ERR_MODULE_NOT_FOUND`) |
| intermédia `7641675` | 11 | 83 — **1 nova**: `regras/paridade_test.mjs` «a DECISAO vem ANTES do download» (J6, §3) |
| **final `609a471`** | 11 | **82 — novas 0, sumidas 0** |

Executor: `provas/lote8_integra/bateria_node_por_nome.py` (cada `.mjs` num processo, rede fechada).

JSON: `provas/lote8_integra/BATERIA-BASE-b273660.json`, `…/BATERIA-DEPOIS-7641675.json`, `…/BATERIA-DEPOIS-609a471.json`,
`…/NODE-BASE-b273660.json`, `…/NODE-DEPOIS-7641675.json`, `…/NODE-DEPOIS-609a471.json`.

## 5 · Mutação

**Junções** — `provas/lote8_integra/mutacao_lote8.py` sobre `609a471` → `MUTACAO-JUNCOES-LOTE8.json`: **14/14 MORTOS**,
cada um pelo teste certo:

| mutante | apanhado por |
|---|---|
| G1 a ligação redefine o grão (igual) · G2 (com DECLARAÇÃO) · G3 lista própria de níveis | `J1` · `C3`+`J1` · `J2` |
| A1 acervo sem a porta no ctx · A2 concorrente sem ligação · A3 mercado com ligação à mão · A4 voz sem a porta · A5 arquivo perde a ligação | `KeyError`/`C9` · `A5`/`B1` · `JA1` · `JA2` · `A5` |
| B1 busca sem a conta no Reel | `JB1`, `JB2` |
| L1 linha entra só por o ficheiro existir | `JL2` |
| D1/D2 download (simples/condicional) antes da decisão | paridade «a DECISAO vem ANTES do download» |
| S1 a coleta volta a ler o registo do curador | `test_a_pasta_coleta_nao_tem_executor_para_o_feed` |
| P6 volta ao `split('\n')` com checkout CRLF | `P6 sintonia-pote.js esta no .gitignore … .vercelignore` |

**Suítes próprias dos ramos e as do lote 7 que tocam peças mexidas** (árvore integrada; log em
`provas/lote8_integra/MUTACAO-SUITES-LOTE8.txt`) — **0 VIVOS**:

| peça | suíte | resultado |
|---|---|---|
| coleta contínua | `provas/coleta_continua_mutacao.py` | **29/29** |
| FEED-LIGADO | `provas/scrap_evolucao/mutantes_feed_ligado.py` | **21/21** |
| social até a Sala | `provas/_mutantes_social_ate_a_sala.py` | **37/37** (livros vivos mudados 0; refeita no código final) |
| D36 (ajuste do social) | `provas/_mutantes_d36_equivalencia.py` | **9/9** |
| PROBLEMA/v1 | `provas/chave_problema/mutacao_chave_problema.py` | **16/16** |
| LIGAÇÃO-ADAMA | `provas/ligacao_adama/mutantes.py` | **25/25** |
| acervo | `provas/acervo_na_intelligence/mutantes.py` | **18/18** |
| porta única + grão (lote 7) | `provas/porta_unica_referencia/mutantes.py` | **29/29** (em `4bc57cd`, depois da J8; antes a cópia limpa reprovava — RC=2, sem veredito) |
| cruzamentos-max | `provas/_mutantes_cruzamentos_max.py` | **31/31** |
| pote v2 único | `provas/pote_v2/mutantes_pote_v2_unico.py` | **25/25** |
| pote no casco | `provas/_mutantes_pote_casco.py` | **29/29** |
| busca no Actions (linha-busca mexida) | `provas/busca_no_actions/mutantes_busca_actions.py` | **17/17** |
| scrap-evolução (coletor mexido) | `provas/scrap_evolucao/mutantes_scrap_evolucao.py` | **26/26** |

Total: **14 + 312 = 326 mortos, 0 vivos.**

## 6 · System Map

`python3 system-map/scripts/correr_a_cadeia.py REGERAR` (depois do `git add`) · `VALIDAR` =
**SYSTEM_MAP_CHECK=PASS** · `impressao_da_arvore.py --conferir-carimbo` = **IGUAL** (conferido depois do último
commit). Os gerados em conflito nos 6 merges foram todos refeitos pela cadeia. Metadata declarada: frases de
`C-ACERVO-NA-INTELLIGENCE`, `C-INT-PORTA-REFERENCIA`, `C-LINHA-BUSCA`, `C-PROVA-COLETA` (+ `LOTE8-INTEGRA.md`,
`provas/lote8_integra/*`). Sem `--stamp`: as peças tocadas e não relidas ficam 🟡, que é a verdade.

## 7 · CHECKLIST DE INSTALAÇÃO NO VIVO (coordenador — **não instalado por esta sessão**)

```bash
VIVA=/c/Users/London1/orca/workspaces/eame-sintonia/source-curator-service-v1   # bot, servico-20260923-0923
C=/c/inst/$(date +%Y%m%d-%H%M)-lote8; mkdir -p $C/livros
FINAL=$(git -C $VIVA fetch -q origin && git -C $VIVA rev-parse origin/claude/lote8-integra-zobt7p); echo $FINAL
```

| # | passo | comando / critério | 🛑 pára se |
|---|---|---|---|
| 0 | **Medir** | `git -C $VIVA rev-parse HEAD` = `b273660b66c1d693aadeb60c5bf8e82d0b066b62`; `git -C $VIVA merge-base --is-ancestor HEAD $FINAL` sai 0; `$FINAL` = o SHA final da sessão. Um só supervisor, worker IDLE (`py curadoria/supervisor.py --estado`). Nenhuma tarefa `SINTONIA-COLETA-CONTINUA*` criada ainda (`schtasks /Query /TN SINTONIA-COLETA-CONTINUA` → não existe) | HEAD diferente (a produção andou: refazer o ensaio) · não é ancestral |
| 1 | **Robô parado** | `PARAR.flag` com marca própria; esperar o supervisor sair (`--estado` → parado, confirmado no SO); parar o observador da ponte. A tarefa `SINTONIA-Arranque` não toca flag alheio | supervisor não sai |
| 2 | **Backup dos livros sujos** | `(cd $VIVA && git status --short \| awk '{print $2}' \| while read f; do find "$f" -type f; done) > $C/lista`; `while read f; do mkdir -p $C/livros/$(dirname "$f"); cp "$VIVA/$f" "$C/livros/$f"; done < $C/lista`; `(cd $C && find livros -type f \| xargs sha256sum) > $C/foto.sha`. E a Sala: `backup_sala.cmd` (com `PROVA_VALE: true`) | cópia falha · backup sem PROVA_VALE |
| 3 | **Tocam livro vivo?** | `git -C $VIVA diff --name-only HEAD $FINAL -- $(cat $C/lista)` **vazio** (medido aqui: o lote não traz nenhum `curadoria/*-V1.json`, `data/collection-ledger`, `candidatas/FONTES-CANDIDATAS.json`, nem `regras/italy_contracts_onboarded.json`) | sai algum nome |
| 4 | **Fast-forward** | `git -C $VIVA merge --ff-only $FINAL` (de b273660b6 até ao SHA final; sem merge, sem conflito) | recusa o ff |
| 5 | **LIVROS_IGUAIS** | `(cd $C && sed 's# livros/# '"$VIVA"'/#' foto.sha \| sha256sum -c)` (ou `cmp` um a um): tudo `OK` → `LIVROS_IGUAIS` | algum MUDOU → DESFAZER |
| 6 | **Testes pós-instalação** (rede fechada) | `py -m unittest tests.test_lote8_juncoes tests.test_coleta_continua tests.test_feed_ligado tests.test_desbloquear_social tests.test_regua_social_por_provas tests.test_social_por_url_achado tests.test_youtube_feed_sem_chave tests.test_chave_problema tests.test_ligacao_adama tests.test_acervo_na_intelligence tests.test_porta_unica_referencia tests.test_cap_win tests.test_cruzamentos_max tests.test_pote_v2_unico tests.test_pote_intelligence_casco tests.test_linha_busca tests.test_rodadas tests.test_contador_24h tests.test_onda_web` → OK; `node regras/feed_discovery_test.mjs`, `node regras/paridade_test.mjs`, `node regras/cadencia_da_referencia_test.mjs`, `node tests/test_pote_no_casco.mjs` (**118/118 no Windows** — é a prova viva do P6) → 0 falhas; `py pacote/acervo_na_intelligence.py --conferir` → `True`. Opcional: bateria inteira por nome contra a base medida **na mesma máquina** — 0 novas | falha nova → DESFAZER |
| 7 | **Mapa** | `py system-map/scripts/impressao_da_arvore.py --conferir-carimbo` = `IGUAL` | DIFERENTE |
| 8 | **Religar** | tirar o flag; `Stop-ScheduledTask SINTONIA-Arranque; Start-ScheduledTask SINTONIA-Arranque`; `py curadoria/supervisor.py --estado` → RUNNING/IDLE, um só | não volta |
| 9 | **Publicar** | push de `servico-20260923-0923` (agora = `$FINAL`) | — |

**↩️ DESFAZER** — `PARAR.flag`; `git -C $VIVA reset -q --keep b273660b6`; conferir a foto (`sha256sum -c`);
relançar como no passo 8.

### 7b · COMO LIGAR A COLETA CONTÍNUA NO AGENDADOR — MODO CANÁRIO (1 ciclo)

Depois do passo 9, **e só com o robô de volta RUNNING**. Nada disto corre sozinho com a instalação.

| # | passo | comando / critério | 🛑 pára se |
|---|---|---|---|
| C0 | **CNR (decisão do dono, em aberto)** | o plano corre `IT-T5-160` (cnr.it) na rodada 15; a mensagem de 26/09 dizia «sem CNR» e o `ORDEM-RENDIMENTO-ONDA4.md` deixou tirá-la como decisão. **Este lote NÃO a tirou.** Se for para tirar: tirar do plano/coorte ANTES de C1 | decisão por tomar e CNR na lista do ensaio |
| C1 | **Ensaio a seco com os livros reais** (0 rede) | `py ferramentas\big_collection\ensaio_coleta_continua.py --plano=%O%\ONDA4-RODADAS\RODADAS-PLANO.json --estado-rodadas=%O%\ONDA4-RODADAS\RODADAS-ESTADO.json --livros-do-dia=%O% --recibos=%SI%\vozes-agronomos,%SI%\micro-prova,%SI%\pesquisadores-t6` → ler a lista de fontes livres e os `ABRE_EM` | lista inesperada |
| C2 | **VPN IT** | ProtonVPN num servidor italiano; medir `country: IT` antes (o portão do ciclo mede de novo, consenso de 3) | não é IT |
| C3 | **Ficheiro de arranque** | `%SI%\coleta_continua.cmd` como em `ferramentas/big_collection/onda4/COLETA-CONTINUA.md` §1, **com `--um-ciclo --max-fontes=1`** (canário: 1 ciclo, 1 fonte) e `--teto-24h=%SI%\TETO-24H.json` (o mesmo livro que o transporte reserva) | — |
| C4 | **Agendar UMA vez** | `schtasks /Create /TN "SINTONIA-COLETA-CONTINUA-CANARIO" /SC ONCE /ST <HH:MM> /TR "%SI%\coleta_continua.cmd" /F` (ou correr o `.cmd` à mão). **Não** criar a tarefa de 30 min ainda. **Não** correr `rodadas.py --correr` depois disto | — |
| C5 | **Backup** | o próprio ciclo faz `provar_backup_da_sala.py` e **PARA** sem `PROVA_VALE: true` (`BACKUP_SEM_PROVA_VALE`) | PARA |
| C6 | **Prova-teto** | última linha de `%O%\COLETA-CONTINUA\CICLOS.ndjson`: as duas PROVA-TETO (`do ciclo` e `24 h`) = PASS, `PEDIDOS_POR_DOMINIO` ≤ 5 (**freio temporário**, D124), reconciliação da Sala = PASS, robô antes = depois = RUNNING, `PARA` vazio. `py ferramentas\big_collection\coleta_continua.py --estado --base=%O%\COLETA-CONTINUA` | qualquer FAIL/NAO_SEI · PARA preenchido (ler `PAROU`; só `--rearmar --porque=…` depois de resolver) |
| C7 | **Só depois, e por decisão:** o serviço | `schtasks /Create /TN "SINTONIA-COLETA-CONTINUA" /SC MINUTE /MO 30 /TR "%SI%\coleta_continua.cmd" /F` com o `.cmd` sem `--max-fontes=1`. Desligar: `PARAR-COLETA.flag` ou `schtasks /Change /TN … /DISABLE` | — |

⚠️ **D124 — o 5 é FREIO TEMPORÁRIO.** O dono decidiu que o teto fixo 5/domínio/24 h **deixou de ser regra**
(teto adaptativo pelo sinal medido do site, por outra equipe: `nuvem-teto-adaptativo-v1`). Neste lote o 5 fica
no código **sem ser reescrito**, como freio temporário (bot Luciano) — escrito assim em
`ferramentas/big_collection/onda4/CONTADOR-24H.md`, `COLETA-CONTINUA.md`, `FEED-LIGADO.md` e no KNOW-HOW §222.

⚠️ **O que a instalação muda no comportamento vivo:**
(a) todo objeto que chega ao pote leva `LIGACAO_ADAMA` da porta, e o pote **recusa** `SEM_LIGACAO_ADAMA`/`FORA_DA_PORTA`;
(b) CAP-WIN e o motor leem o PROBLEMA **só** pelo contrato `PROBLEMA/v1` — item com o bloco antigo (lista) sai
`NOT_POSSIBLE` até o reprocessador correr (`admissao/reprocessar_problema.py`, seco por omissão; `--aplicar` com o
cuidado de `MIGRACAO-SALA.md`); (c) o coletor passa a guardar robots em `<SINTONIA_TETO_24H>.robots.json` e a cópia
do GET condicional em `data/collection-cache/italy/http/` (**não está no `.gitignore`**: vai aparecer como não
rastreado no `git status` do vivo); (d) a régua social passa a julgar por PROVAS. **Não mudam sozinhos:** o feed só
se liga com `py regras/ligar_feeds.py --aplicar` (FEED-LIGADO.md §4; ele escreve na tabela rastreada
`regras/italy_contracts_onboarded.json` e tem `--desfazer`); o desbloqueio social só com
`curadoria/desbloquear_social.py --aplicar --vivo`; a coleta contínua só pelo §7b.

## 8 · Limites declarados

- **CNR:** decisão do dono, não retirada por esta sessão (§7b C0).
- **FEED-LIGADO.md** chegou com `BATERIA_PLACEHOLDER` (o ramo não fechou o relatório); a bateria deste lote cobre-o.
  Nesta árvore 8 das 13 fontes do pacote têm linha na tabela; na produção o seco diz quantas.
- **SOCIAL-ATÉ-A-SALA** não tem relatório `.md` no ramo; o que ele faz está nos commits `0b69ecc`/`c3ebff7`.
- **Acervo:** a parte científica (851), transcrições (184), boletins (133), vozes (79), notícias, agromet e sinais
  **não atravessaram a régua** (sem tempo do facto / sem prova admitida) e ficam fora do pote, contadas com o motivo
  (`RESUMO-ACERVO.json`). Nada do acervo vai ao portal: `POTE-ACERVO.json` não é referido em `italia-portale/`; as
  mudanças de `portale.html`/casco no ramo 6 são as do pote-v2 já instalado no lote 7.
- Todos os 1.128 objetos do POTE-ACERVO saem com ligação `NAO_SEI` (FALTA CULTURA): a porta não inventa cultura.
- Coleta contínua: só a linha SITES está ligada ao livro de 24 h; BUSCA/CIÊNCIA/SOCIAL/PESQUISADORES ficam
  `ESPERA_LIGACAO`. `RoboReal`/`backup_real`/`reconciliar_real` **NÃO SEI** contra o Windows/Postgres reais — o canário
  §7b é a primeira medida.
- `system-map/tests/verificar_a_tela.mjs` falha igual na base e aqui (`ERR_MODULE_NOT_FOUND`: precisa da bancada do
  navegador); `regras/italy_contract_test.mjs` 82 falhas herdadas, as mesmas pelo nome.
- `--stamp` do mapa não foi corrido.

## EM PALAVRAS SIMPLES

Juntei numa árvore só, em cima do que está a rodar hoje, as seis entregas aprovadas: a coleta que anda **fonte a
fonte** em vez de turma a turma, o **feed** que traz notícias inteiras sem gastar visita, o caminho das **redes
sociais até a Sala**, a **praga como chave** da coleta, a **etiqueta da bula ADAMA** em todo fato, e o **acervo
antigo** passando pela Inteligência (nada dele vai direto ao portal).

Cada entrega tinha sido testada sozinha. Juntas, conferi oito encaixes; seis precisavam de conserto: a etiqueta da bula tinha
reescrito por cima a regra do «grão» (quem mandava deixou de mandar — voltou a haver um dono só); o acervo quebrava
porque agora todo fato precisa da etiqueta (pus a etiqueta, feita pela porta oficial; todos dizem «não sei» porque
falta a cultura); a busca mandava um tipo de endereço de Reel para o lugar errado; o social lia um caderno que é do
curador (agora pergunta ao curador); e dois testes/ferramentas tinham âncoras velhas. Corrigi também o teste P6 que
falhava no Windows por causa do fim de linha — o defeito era do teste, não da regra.

Resultado: nenhum teste que passava passou a falhar (Python e Node, comparados pelo nome). Estraguei o código de
326 jeitos de propósito e os testes pegaram os 326. O limite de 5 visitas por site continua no código, mas agora
escrito como **freio temporário** (decisão do dono, D124), até o teto adaptativo chegar. A CNR continua no plano —
é decisão sua. **Nada foi instalado:** o checklist do §7 é para o coordenador, e a coleta contínua liga-se primeiro
em **canário de 1 ciclo** (§7b).
