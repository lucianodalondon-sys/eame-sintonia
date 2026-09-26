# INTEGRA-NOITE · LOTE 2 — um só pacote sobre o lote 1 (`69b0e23f`)

Ramo `integra-noite-v2`, a partir de `origin/integra-noite-v1` @ `69b0e23f` (o lote 1, instalado no vivo às 05:25).
**NÃO instalado.** Estado: **PARADO à espera de decisão** (§4: 1 falha nova da soma int-consertos × quatro-chaves) — 11 pacotes juntos. **Decisão da coordenação 06:40:** o `freio-social-v1` fica FORA (o dono refaz o ramo sobre o lote 1; entra num LOTE 3). Fecha-se o lote 2 com os 11.

## 1 · O drift P1 ao instalar o lote 1 (pergunta da coordenação 05:55) — RESPOSTA

`VALIDAR` no vivo deu `P1_SEM_DRIFT FAIL` com o carimbo IGUAL (log `C:/Users/London1/AppData/Local/Temp/validar-lote1.txt`).
**O drift vem SÓ dos livros/dados vivos, não de código.** Prova (só leitura na pasta viva, HEAD = `69b0e23f`):

| `FILES[i]` (em `system-map/data/architecture.generated.json`) | ficheiro | sha «commitado» = blob no HEAD? | sha «regerado» = o ficheiro na pasta viva hoje? | é um dos 16 livros? |
|---|---|---|---|---|
| 235 | `candidatas/FONTES-CANDIDATAS.json` | `c15d700d` = `git rev-parse HEAD:…` **IGUAL** | `9c2dc29a` = `git hash-object …` **IGUAL** | sim (`M`) |
| 342 | `curadoria/BRIDGE-LEDGER-V1.json` | `f54ec3e8` **IGUAL** | `f4091eaf` **IGUAL** | sim (`M`) |
| 362 | `curadoria/DISCOVERY-SIGNAL-V1.json` | `2693ec70` **IGUAL** | `4309596e` **IGUAL** | sim (`M`) |
| 363 | `curadoria/DISCOVERY-VISITED.json` | `4e3e353c` **IGUAL** | `f46fedc4` **IGUAL** | sim (`M`) |

- `COLETAS_FEITAS` sai de `system-map/scripts/scan_sources.py` (`coletas_feitas`), que lê
  `data/samples/RUN-MANIFEST.json` e `data/collection-ledger/italy/runs.ndjson` — **dois dos 16 livros**.
  Medido: `RUN-MANIFEST.json` tem **49** corridas no HEAD e **146** na pasta viva (= o 49 → 146 do log);
  `runs.ndjson` 59 → 155 linhas. As diferenças por país/custo/rendimento são as mesmas corridas.
- Ou seja: o mapa foi commitado com os livros **como estão no Git**; o `VALIDAR` na pasta viva regera-o com os
  livros **como o robô os deixou** (sha com o filtro de fim de linha do Git — o mesmo que o mapa usa). O código
  não entra: os 4 ficheiros são `.json` de dados, e nenhum ficheiro de código aparece no drift.
- **Consequência para as instalações:** no vivo, com o robô a escrever, o `P1_SEM_DRIFT` vai SEMPRE acusar estes
  livros. Para conferir o mapa instalado sem esse ruído: `PORTOES_POS_COMMIT` (a impressão do carimbo, que deu
  IGUAL) é a prova certa na pasta viva; o `VALIDAR` completo corre-se numa cópia limpa do commit (sem os livros
  sujos), ou aceita-se o P1 **só** se a lista de diferenças for exactamente os ficheiros `M` do `git status`.

Comandos para repetir (só leitura, na pasta viva):
```
git rev-parse HEAD:<ficheiro>      # = o sha «commitado»
git hash-object -- <ficheiro>      # = o sha «regerado» (com o filtro do Git, como o mapa)
```

## 2 · O teste que falhou no vivo (`tests.test_semear_so_as_candidatas`, 3 FAIL, rc=2 RECUSADO)

- **Sim, a regressão «mesmos dados» do lote 1 correu numa pasta com outro nome** (`…/Temp/jf-prod`): o script
  `semear_qualify_social.py` só se julga «no vivo» se o caminho tiver `source-curator-service-v1`; lá não tinha,
  e o teste passou. Na pasta viva recusou de verdade.
- **Consertado no teste** (`965275aa`; o script não muda): o caminho (`S.RAIZ`) e o `PARAR.flag` são fixados no
  teste, e há 4 testes novos da trava do vivo (sem `--vivo` recusa; com `--vivo` e o robô a correr recusa; com
  `--vivo` e o robô parado semeia só o lote; fora do vivo sem `--copia` recusa). **8/8** na pasta de trabalho **e
  numa pasta com o nome do vivo**; com a trava desligada (mutante), 2 dos testes novos morrem.
- A regressão por nome do lote 2 corre também numa pasta chamada `source-curator-service-v1`.

## 3 · Os pacotes (em curso)

| # | pacote | SHA | junção |
|---|---|---|---|
| 1 | conserto-regua-v1 | a139caad | limpa |
| 2 | c2-juiz-v1 | f6f3bb2f | `.gitattributes`: as duas linhas ficam (`tests/dados/leitor-data-yt/**` e `tests/dados/c2-juiz/**` `-text`) — não é código; cada uma protege os bytes de amostras |
| 3 | rodadas-v1 | bc77648e | limpa |
| 4 | trava-sede-v2 | 1a2e5d55 | limpa |
| 5 | quatro-chaves-v2 | b2870420 | só gerado (1) |
| 6 | bloqueadas-v1 | 889b2166 | só gerado (1) |
| 7 | destravar-v1 | a935a191 | só gerado (1) |
| 8 | casco-leitura-v1 | b83b930f | limpa |
| 9 | casco-painel-v1 | 2744073c | limpa |
| 10 | canais-pesquisa-v1 | 494b7b36 | limpa (independente do freio) |
| 11 | int-consertos-v1 | 60faa7cb | limpa (só código; nada ativado) |
| — | **freio-social-v1** | **d1074533** | **PARADO — conflito de CÓDIGO** em `coleta/scrap_colheita.py` (4 blocos), `ferramentas/youtube_transcrever.py` (4), `coleta/scrap_http.py` (1), `SOCIAL-QUALIFICAR.md` (1). O freio traz a SUA cópia da prova-teto (`af2bb4e4`) — a que entrou no lote 1 foi `6bd3da95` (prova-teto-social `84a997a6`) — mais o teto D38 no pedido (`4faaa035`) e o dedup pelo vídeo (`379aab98`). Decisão pedida à coordenação |

O `freio-social-v1` (linha «—» acima) **sai do lote 2** (coordenação 06:40): vai para o LOTE 3, refeito pelo dono sobre o lote 1.

## 4 · Testes por NOME contra o vivo `69b0e23f` (mesmos dados, rede fechada, pastas chamadas `source-curator-service-v1`)

Corredor `provas/boletins_data_local/testes_por_nome.py`; o lado «vivo» é o ramo com os 110 ficheiros do writeset
repostos na versão `69b0e23f`. Dados iguais nos dois lados (`data/samples`, `data/collection-ledger`, `docs/`).
Resultado: `provas/integra_noite/lote2-{ramo,vivo}.json` (sha256 `26db411e…` / `faf83a88…`).

- 55 módulos Python + 8 provas Node. **767** testes Python no ramo, **616** no vivo (os módulos novos não existem lá).
- **Herdadas (iguais nome a nome no vivo): 92** — `italy_contract_test` 77 · `test_tempo_e_lugar_da_publicacao` 12 ·
  `test_collection_gate` 1 · `test_scrap_rc01_release_candidate` 1 · `test_a_primeira_corrida_da_inteligencia` 1.
- `test_semear_so_as_candidatas`: vivo 3 FAIL (a falha do lote 1) → ramo 8/8 (o conserto de §2).
- Por pacote, todos verdes no ramo: conserto-regua 10 · c2-juiz 15 · rodadas 29 · trava-sede (`test_soc_tempo_publicacao_e_lugar`
  14) · quatro-chaves (`test_quatro_chaves` 11, `_na_sala` 22, `test_sala_por_nome` 9, `test_a_linhagem_do_ready` 13) ·
  bloqueadas (`test_url_com_acento` 4, `test_robo_diag` 3) · destravar (`test_colher_prova_territorio` 8, `test_sonda_um_pedido` 5) ·
  canais-pesquisa (`test_canais_presos_no_feed` 3) · int-consertos (`test_espinha_da_intelligence` 42).
- ⛔ **1 falha NOVA — PARADO, decisão pedida à coordenação:**
  `tests.test_os_consertos_da_intelligence.D8_UmaListaSo.test_o_itempronto_cobre_todos_os_campos_do_dono`
  → `AttributeError: 'ItemPronto' object has no attribute 'JANELA_DECLARADA'`.
  - **Cada pacote sozinho passa** (int-consertos em `60faa7cb`: 27/27 OK). A falha nasce da **soma** de dois pacotes:
    o int-consertos (D8) fez a espinha ler a lista de campos do DONO (`CAMPOS_READY` em `admissao/sala_de_espera.py`);
    o quatro-chaves-v2 acrescentou a essa lista o campo `JANELA_DECLARADA`; o molde `ItemPronto`
    (`provas/espinha_da_intelligence.py`) não o tem. Não houve conflito de ficheiro na junção — é um conflito de
    código entre pacotes, e o teste existe precisamente para o apanhar.
  - **Proposta (1 linha, não aplicada):** em `ItemPronto`, um bloco «a das quatro chaves (quatro-chaves-v2)» com
    `JANELA_DECLARADA: Any = NAO_SEI` — o mesmo molde dos campos que chegaram com a 033 e com o PRESERVE-FACTS
    («um campo que passou a existir não é um campo que passou a estar preenchido»). Alternativa: o default ser o
    `JANELA_NAO_MEDIDA` do dono — mas isso faria a espinha copiar um valor da Collection, o que ela hoje evita.

## 5 · Casco (casco-leitura + casco-painel) — sem testes de unidade

- `node --check` OK em `audit/casco/sala-leitura.mjs`, `audit/casco/painel-operacao.mjs`, `client/italy-sala-leitura.js`;
  os dois JSON do contrato da Intelligence EXPERIMENTAL leem-se.
- Portão `link-asset` (Chromium local, rede fechada), ramo × vivo `69b0e23f`, cada um numa cópia: **6/6 PASS nos dois**
  (0 pedidos ≥400, 0 ficheiros em falta, 0 links malformados, 0 imagens partidas, 0 erros de consola). Telas: **16 no
  ramo, 14 no vivo** (+`#sala`, +`#painel`); 161 links externos iguais. Provas:
  `provas/integra_noite/lote2-casco-link-asset-{ramo,vivo}.json`.
  ⚠️ Como corri: `playwright-core` não está no repo; usei uma cópia (1.62.1) doutra pasta desta máquina e, **só nas
  cópias temporárias** do `audit/`, apontei o `drive.mjs` para o Chromium 1243 já instalado. O repo não mudou.

## 6 · Conferências (feitas)

| conferência | resultado |
|---|---|
| ff-only sobre `69b0e23f` | **SIM** |
| writeset | 110 ficheiros (`provas/integra_noite/writeset-lote2.txt`) |
| 16 livros vivos no writeset | **0** |
| `data/` no writeset | 21 — todas provas NOVAS do quatro-chaves em `data/derivados/QUATRO-CHAVES-*`; nenhum livro |
| ficheiros do writeset soltos ou `M` na pasta viva | **0** (medido antes do reinício: vivo em `69b0e23f`, 16 `M`) |
| migrações | **nenhuma** no writeset |

## 7 · Falta (depois da decisão sobre §4)

conserto (se aprovado) → testes do int-consertos + quatro-chaves outra vez → UM mapa (LOCK-PESADO) → plano único → PRONTO.
