# FREIO-SOCIAL + CANAIS-PESQUISA — o que faltava no código antes da onda grande (26/09)

Dois ramos, sem rede (tudo contra servidores locais em 127.0.0.1; `HTTP(S)_PROXY=127.0.0.1:9`), vivo não tocado,
nada instalado. **SEM MAPA** (o coordenador: «não esperes, a INTEGRA regera»); os ficheiros novos de código já
estão declarados em `system-map/data/architecture.declared.json`.

| ramo | base | o que traz |
|---|---|---|
| **`freio-social-v1`** | `social-qualificar-v2` (f0d97dbd = vivo `83de0ccd` + social-micro + PROVA-TETO-SOCIAL) | 1 · o freio · 3 · dedup · 4 · C2 |
| **`canais-pesquisa-v1`** (494b7b36) | `legacy-99-v5` (ed86cb97) | 2 · os 9 canais presos no feed |

⚠️ **Porque o freio NÃO parte de `83de0ccd` direto:** o freio trava em cima do CONTADOR da PROVA-TETO-SOCIAL,
que só existe em `social-qualificar-v2` (ainda não instalado). Partir de `83de0ccd` era duplicar esses 4 commits.
Ordem de instalação: `social-qualificar-v2` → `freio-social-v1`, os dois **ff-only** sobre `83de0ccd`.

## 1 · O FREIO — o pedido que passaria do teto NÃO SAI

**Antes:** a web já travava antes do pedido (`coleta/italy_pilot_collect.mjs`: `tetoAtingido` + livro da onda em
`SINTONIA_TETO_ONDA`); o Scrap **só contava** depois (PROVA-TETO-SOCIAL); o yt-dlp era contado pelo
`--print-traffic`, depois. E nenhum dos dois juntava youtube.com + googlevideo.com (D41).

**Agora:**
- `coleta/teto_da_onda.py` (novo) — o freio do Scrap. Fala o **MESMO livro da onda** que a web
  (`{"PEDIDOS_POR_DOMINIO": …}`, o mesmo trinco `<livro>.trinco`, o mesmo `SINTONIA_TETO_POR_HOST`), por isso uma onda
  que misture web e redes paga tudo no mesmo sítio. `reservar(host)` lê, compara e gasta **dentro do trinco**
  (atómico entre processos) e **recusa** o que passaria do teto, com o registo da recusa.
  D41: `MESMO_ORCAMENTO = {"googlevideo.com": "youtube.com"}`.
- `coleta/scrap_http.py` — o pré-processador do abridor instalado (a porta única do Scrap) **reserva antes de
  contar**; sem lugar levanta `TetoDoDominio` (uma `RotaNaoPermitida`: é política nossa, não bloqueio da plataforma).
- `ferramentas/yt_dlp_com_freio.py` (novo) — o yt-dlp corre por aqui: cada `YoutubeDL.urlopen` (a porta de TODOS os
  pedidos do yt-dlp, extractores e descarregadores) reserva o lugar antes de sair. `ferramentas/youtube_transcrever.py`
  passa a chamá-lo em vez de `python -m yt_dlp` e recolhe as recusas do filho (ficheiro em `SINTONIA_TETO_RECUSAS`).
- `coleta/scrap_colheita.py` — nas fases sociais sem livro da onda, a corrida ganha um **livro próprio** (5 por
  domínio numa corrida sozinha) que morre com ela; as recusas vão para a linha do livro de corridas
  (`CORTESIA.RECUSAS` + `TETO_POR_DOMINIO`). As outras fases do Scrap não mudam (sem livro, não trava).
- `coleta/italy_pilot_collect.mjs` — a web conta pelo `orcamentoDe(host)` (D41), no mesmo livro.

**Provas (sem rede):**
- `tests/test_freio_social.py` (11): **F1** 8 tentativas → o servidor local recebe **exatamente 5** (robots + 4) e a
  6.ª levanta `TetoDoDominio`; livro `{"127.0.0.1": 5}`; a recusa escrita · **F2** a recusa fica na linha da corrida ·
  **F3** corrida social sozinha: livro próprio, 5, apagado no fim · **F4** sem livro não trava (8 pedidos passam) ·
  **F5** o yt-dlp REAL contra o YouTube de mentira, com youtube.com já em 2: saem **exatamente 3** pedidos (página,
  player, API) e o do googlevideo.com **não sai**; livro `{"youtube.com": 5}` · **F6** livro vazio: 4 pedidos, todos
  em `youtube.com` · **F7** o transcritor corre pelo freio e recolhe as recusas · **F8** 4 processos a reservar 3
  cada no mesmo livro: **exatamente 5** passam · **F9** sufixos e D41 iguais aos da web.
- `provas/teto_dominio_local.mjs` +3 (**D8a/b/c**): o transporte web REAL com `rr1---sn-x.googlevideo.com` a resolver
  para 127.0.0.1: com youtube.com esgotado, **0** pedidos ao googlevideo e motivo `TETO_DOMINIO`; com 3 gastos, **2**, e
  o livro soma em `youtube.com`. Prova local 10/10.
- **Mutação `provas/_mutantes_freio_social.py`: 14/14 mortos** (freio, D41 nos dois lados, yt-dlp, recusas, livro
  próprio, dedup, C2).
- **Regressão:** as 31 suítes de Scrap/YouTube/LinkedIn/teto/onda/social: **as mesmas 14 falhas antes e depois**
  (base f0d97dbd: 781 testes; ramo: 792), comparadas linha a linha. São falhas herdadas desta máquina (Apify/C2/C3 do
  YouTube oficial, sessão social, rc01/sr02, colisão de nome curto).

**O que o freio NÃO resolve:** quem conduz a onda tem de NOMEAR o livro (`SINTONIA_TETO_ONDA`) para todas as
corridas da onda — a web faz isso no `onda_web.py`; do lado social ainda não há condutor (C1, abaixo). Sem livro
nomeado, cada corrida social tem o seu 5 (o livro próprio), e duas corridas da mesma onda somam 10.

## 2 · Os canais de pesquisa presos no caminho antigo → caminho do Scrap

- **Medido (cópia dos livros do vivo 83de0ccd, 04:06):** 9 canais com contrato `YOUTUBE_CHANNEL_FEED` em
  `RETRY_AFTER`, sem tarefa na fila — 7 de pesquisa (IT-T5-042 Navarra, 043 UNIBO DISTAL, 044 Minoprio, 045 ISPRA,
  047 UNIBA, 048 UNICT, 050 Bolzano) + IT-T7-016, IT-T7-018. O plano da v5 só olha READY_LEGACY.
- **O bloco 4 da v5 já os aceitava** (`rota_do_scrap` decide pela estratégia do contrato, não pelo estado): 9/9
  `APLICA`, 0 saltos. Só a entrada do plano os deixava de fora.
- **Mudança (em `canais-pesquisa-v1`, por cima da v5):** `importar_do_coletor.planear` acrescenta os `PRESO_NO_FEED`
  ao `PELO_SCRAP`; `pelo_scrap` usa o MESMO bloco 4 e um `remedir_presos` (CANARY_PENDING + VALIDATE_ROUTE), porque
  o `ready_split.remedir` só age em READY. **Sem duplicar:** o runbook dos 41 não muda; `importar_do_coletor.py`
  passa a mostrar `PELO_SCRAP=50`.
- **Ensaio na cópia:** 9/9 `SCRAP_FASE canal-youtube` com o `CHANNEL_ID`; o worker (fila filtrada aos 9) correu
  9 `VALIDATE_ROUTE:OK`; 9/9 `CANARY_PENDING`; 0 tarefas abertas; 0 rede.
- Testes `tests/test_canais_presos_no_feed.py` (3) + os da v5 (`test_youtube_pelo_scrap`, `test_importar_do_coletor`):
  28 OK. Mutação à mão 3/3 mortos (plano sem presos · remedir que não regista · os presos no remedir de READY).
- Aviso deixado à bancada CANAIS-41-RUNBOOK: `auditoria-madrugada/AVISO-CANAIS-PESQUISA-PARA-CANAIS-41.txt`.

## 3 · Dedup social — o mesmo vídeo em duas contas

- **Medido nos dados reais de 24/09:** ARPA VdA e ISPRA têm **POSTS diferentes** (activity 7507360685509607424 e
  7507010113581314048) e o **MESMO vídeo** (`urn:li:digitalmediaAsset:D4D05AQH1yJW2COxvNQ`). Por isso a identidade do
  vídeo no LinkedIn é o **URN do asset**, não o do post (a missão dizia «URN do post»: não chega, os posts são dois).
- `leis/identidade_do_video.py` (nova): YouTube = o id do vídeo (11 caracteres); LinkedIn = `ASSET_URN`. Mais nada
  (título, tamanho e sha dos bytes não identificam). **UNKNOWN não funde**: sem identidade → `NAO SEI` com o porquê, e
  nunca igual a nada.
- `coleta/scrap_colheita.colher` (fases sociais): cada unidade leva `VIDEO_IDENTITY` (+ base) e, se o vídeo já foi
  visto noutra publicação, `MESMO_VIDEO_QUE` = {SOURCE_ID, RUN_ID, DOCUMENT_ID, POST} do primeiro. Registo:
  `data/collection-ledger/italy/VIDEOS-SOCIAIS.ndjson` (o primeiro fica). **Nada se apaga** (D62): a partilha é um facto.
- Testes `tests/test_dedup_video_social.py` (8) com os dois objetos reais (`tests/dados/videos-partilhados-arpa-ispra.json`).
- ⚠️ **Não chega à Sala:** a Sala guarda por (corrida, ordem) e não tem coluna para isto — pedido ao dono abaixo.

## 4 · As 6 mudanças do ONDA-SOCIAL-2-PLANO

| | o que é | estado | dono |
|---|---|---|---|
| **C1** | condutor da onda social (como o `onda_web.py`) | **o freio está feito** (1); o condutor que nomeia o livro, corre o lote pelo orquestrador e chama a prova-teto no fim **não** — pedido abaixo | Scrap + coordenação |
| **C2** | a onda pede `teto=1` por conta LinkedIn | **FEITO** (`curadoria/plano_onda_social.py`, que é meu): `pedido_de` põe `teto=1` (o contrato fica `teto: 2`); `rodadas()` monta 2 LinkedIn + 1 YouTube por onda com o previsto por domínio e diz se cabe (com teto 2, 2 contas = 6 → não cabe). `tests/test_plano_onda_social_c2.py` (6) + 2 mutantes | eu |
| **C3** | flags do yt-dlp | **pedido** — com o freio, um vídeo grande já não passa do teto: é **recusado**. As flags evitam a recusa (e o áudio perdido) | Scrap (`youtube_transcrever.py`) |
| **C4** | canais presos no feed | **FEITO** (2) | SEPARAR-A-B aceita/junta |
| **C5** | pessoas LinkedIn | espera a decisão do dono (de onde vêm os posts) | Scrap + Curator |
| **C6** | `/showcase/` | espera a decisão do dono | Curator |

## PEDIDOS AOS DONOS (escritos aqui; o coordenador encaminha)

1. **Scrap — C1, o condutor da onda social.** Um `ferramentas/onda_social.py` que: cria o livro da onda e o exporta
   em `SINTONIA_TETO_ONDA` para todas as corridas; corre as `RODADAS` de `plano_onda_social.plano()` pelo
   orquestrador (D28, sequencial); no fim de cada onda chama `provas/prova_teto_dominio.py` sobre as linhas; pára em
   FAIL/NAO_SEI. O freio já garante que nada passa; o condutor garante que a onda SOMA num livro só.
2. **Scrap — C3.** Em `youtube_transcrever._audio`: `--http-chunk-size 50M` (vídeo até 50 MiB = 4 pedidos),
   `--retries 1 --fragment-retries 1` (um 403 não gasta o teto), `--match-filter "duration<=540"` (vídeo longo não
   chega a descarregar). Medido offline: sem elas, um vídeo de 25 min pede 6 → o freio recusa o 6.º e o áudio fica
   por fazer.
3. **Dono da Sala — MESMO_VIDEO_QUE.** Uma migração que acrescente `video_identity` e `mesmo_video_que` (jsonb) a
   `sala_de_espera`, e o `admissao.unidade` a copiá-los do item (hoje o Scrap já os escreve na unidade). Sem isto a
   Inteligência conta a partilha da ARPA e o original do ISPRA como dois vídeos.
4. **SEPARAR-A-B / CANAIS-41 — C4.** Juntar `canais-pesquisa-v1` (ff sobre `legacy-99-v5` ed86cb97) e contar os 9 nas
   rodadas.
5. **Condutor da web (onda_web) — nada a mudar:** a D41 entra pelo `orcamentoDe` no transporte; o `onda_web.py` já
   nomeia o livro.

## Provas fora do Git
- Cópia dos livros do vivo para o ensaio dos canais: `C:/canais-pq` (worktree `canais-pesquisa-v1`, livros sujos
  copiados às 04:06; sha256 antes do ensaio em `C:/soc2/cpq-antes.sha256`).

## EM PALAVRAS SIMPLES

- **O freio.** Antes, o sistema contava os pedidos **depois** — como descobrir que passou do limite quando já
  passou. Agora, antes de cada pedido sair, ele pergunta ao "caderno da rodada" se ainda há vaga naquele site. Se não
  há, o pedido **não sai**, e fica anotado por quê. Vale para o LinkedIn, para o YouTube (contando o site do vídeo e o
  site do streaming como um só) e para os sites normais. Testei com um servidor dentro do computador: o 6.º pedido
  nunca chegou.
- **Os canais de pesquisa.** Os 7 canais de pesquisa do YouTube (ISPRA, UNIBO, Bolzano…) mais 2 estavam presos num
  caminho que não funciona. Mudei a porta de entrada para eles seguirem o caminho novo, o mesmo dos outros 41. Na
  cópia, os 9 ficaram prontos para o teste, sem ir à internet.
- **Vídeo repetido.** A ARPA partilhou um vídeo do ISPRA. São dois posts, mas um vídeo só. Agora cada vídeo tem
  "RG" (a identidade que a própria plataforma dá), e o segundo post diz "este vídeo é o mesmo daquele". Nada é
  apagado. Se o "RG" não existe, o sistema não junta nada — não chuta.
- **O que ainda falta (de outros donos):** o "maestro" que conduz a rodada social inteira, ajustes no baixador de
  vídeo para não desperdiçar vagas, e uma coluna na Sala para guardar o "é o mesmo vídeo".
- **Nada foi instalado, coletado ou mexido no vivo.**
