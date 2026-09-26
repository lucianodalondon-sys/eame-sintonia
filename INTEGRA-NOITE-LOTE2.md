# INTEGRA-NOITE · LOTE 2 — um só pacote sobre o lote 1 (`69b0e23f`)

Ramo `integra-noite-v2`, a partir de `origin/integra-noite-v1` @ `69b0e23f` (o lote 1, instalado no vivo às 05:25).
**NÃO instalado.** Estado: **em curso** — 11 pacotes juntos. **Decisão da coordenação 06:40:** o `freio-social-v1` fica FORA (o dono refaz o ramo sobre o lote 1; entra num LOTE 3). Fecha-se o lote 2 com os 11.

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

Testes por nome (em curso, duas pastas com o nome do vivo, mesmos dados, rede fechada), 16 livros, mapa e plano: a seguir.
