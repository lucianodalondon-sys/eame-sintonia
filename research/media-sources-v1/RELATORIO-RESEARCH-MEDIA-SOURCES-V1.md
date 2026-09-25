# RESEARCH-MEDIA-SOURCES-V1 — podcasts, séries e vídeos de pesquisadores (IT)

**Base:** `origin/servico-20260923-0923 @ df0865e6` · **Ramo:** `research-media-sources-v1` · **Data:** 2026-09-25
**Egresso:** `superficie/rede.py::portao_de_egresso('IT')` = **PASS** (ipwho.is IT, ip-api IT; ifconfig.co discorda: US) — Proton, Milão.
**Rede:** 15 pedidos a 6 domínios (crea 3, reterurale 3, youtube 3, ilsole24ore 2, agronotizie 2, spreaker 2), máx. 3 por domínio, robots.txt lido antes, pausa 4 s, sem cookie/login. Registo: `PEDIDOS.jsonl`; bytes com sha256 em `prova/`.

## 1. Censo do que já existia (fila `candidatas/FONTES-CANDIDATAS.json`, 1199 linhas antes)

| TIPO | n | | ESTADO | n |
|---|---|---|---|---|
| ORGANIZACAO | 512 | | EM_ANALISE | 857 |
| BASE_OFICIAL | 382 | | CANDIDATA | 267 |
| CIENCIA | 84 | | POLICY_BLOCK | 69 |
| YOUTUBE | 82 | | CAPABILITY_BLOCK | 6 |
| LINKEDIN 68 · INSTAGRAM 26 · IMPRENSA 25 · FACEBOOK 20 | | | | |

Por **formato** (busca por palavra em NOME/URL/PARA_QUE/NOTA): podcast real **1** (sherwood.it, rádio registada por engano — já apontada em `curadoria/descobrir.py:1407`); Spotify **3** (CAND-0290/0299/0333, PAIS NAO SEI); rádio **3**; convegno/seminário **9**; boletim **88**; vídeo **91**; YouTube (tipo) **82**. Webinar como formato próprio: **0**.

### Capacidade: MISSING_ROUTE vs NOT_IMPLEMENTED

| Formato | Quem já tem | Veredito |
|---|---|---|
| Canal/vídeo YouTube | Curator `capturador.py` (canal→feed), contrato `VIDEO_METADATA`, D53 rota VIDEO, áudio YouTube (`test_c13_youtube_public_audio`) | **EXISTE** (feeds RSS com Disallow — ver LEGACY-99) |
| PDF / boletim | contrato `PDF`, D42 | **EXISTE** |
| Webinar gravado | só se estiver no YouTube ou página HTML; `coleta/comunicacao_classificar.py` só classifica a palavra | **EXISTE via YouTube/HTML**; sem rota própria |
| **Podcast (áudio RSS/Spreaker/Spotify)** | só a palavra `'PODCAST'` em `coleta/social_persistencia.py:76` (valor do banco); `validar_contratos.py:36` OUTPUTS = {HTML, PDF, VIDEO_METADATA}; `leis/regua_italia.py:461` lista `podcast+episodio` em PORTAS_SEM_DADO; `descobrir.py:998` bloqueia spotify.com | **NOT_IMPLEMENTED** — não há coletor nem saída de contrato para áudio de podcast. Não é MISSING_ROUTE: não existe capacidade sem chamador para ligar. |

Nada foi ligado: não havia capacidade existente sem chamador.

## 2. Novas candidatas (5), registadas por `candidatas/fonte_nova.registar`

| ID | Tipo | Formato | URL oficial | Exemplo datado | Propósito |
|---|---|---|---|---|---|
| CAND-1200 | CIENCIA | podcast (5 ep.) | crea.gov.it — «TEA alle 5» | página oficial 08/10/2025 (Biotech Week 2025) | TEA / melhoramento genético |
| CAND-1201 | CIENCIA | podcast | crea.gov.it — «Agrifuturo» (Life ADA) | 18/04/2023, 3.º episódio «Clima e impatto sull'agricoltura» | clima, fenologia → janelas (D29) |
| CAND-1202 | CIENCIA | podcast (4 séries) | reterurale.it/podcast | Spreaker 2024-09-20, 5.ª puntata PSP/AKIS, pesquisadoras CREA | PAC/AKIS (T12) |
| CAND-1203 | IMPRENSA | podcast semanal | podcast.ilsole24ore.com — «Madre Terra» | 2 dez 2024 «Speciale innovazione» (Biogas 4.0) | inovação, clima, mercados |
| CAND-1204 | YOUTUBE | vídeo + ex-podcast | youtube.com/channel/UCMfZsQVzUE4oF00c_0nzFVw (agrifake) | vídeo e0RWUj904Hk, uploadDate 2025-05-14 | divulgação agronómica com docentes UNIMI/UNIBS |

Proveniência completa em `NOTA` de cada linha (PAIS_PROVA, EXEMPLO_DATADO, ORG_JA_NA_FILA, CAPACIDADE, D24/D26).
Todas `ESTADO=CANDIDATA`, `SOURCE_ID=null`. Nenhum READY inventado.

**Entregue a menos, de propósito:** «Futura terra» (Chora/Image Line) — AgroNotizie respondeu **403**, sem prova oficial; fora. «SEMI» (Syngenta) — empresa concorrente, não pesquisador; fora. Georgofili YouTube — **já na fila**; fora. Fondazione Mach YouTube — sem identidade de canal provada nesta missão (canal não aberto); fora. BotaniCAST / Storie di piante — não agro/pesquisa provada; fora.

### Ressalvas
- CAND-1201 é de 2023: atividade atual **NÃO SEI**.
- CAND-1203: a página mostra **1 episódio**; o resto do arquivo **NÃO SEI**.
- CAND-1204 é um creator (pessoa, D24): só a identidade pública do canal; a série 2025 sobre peste suína africana é saúde animal → **fora de foco** (D26).
- IDs `CAND-nnnn` são `len+1` desta cópia; na produção podem colidir com outra lane (ver memória «CAND-nnnn colide entre lanes»). Ao juntar, **deduplicar por URL**, não por ID.
- Dedupe foi feito contra a fila e todo o Git desta base (`git grep`), **não** contra a produção viva (proibido tocar).

## 3. Pareto de bloqueios até READY

| # | Bloqueio | Afeta | Tipo |
|---|---|---|---|
| 1 | Podcast/áudio sem saída de contrato nem coletor | 1200, 1201, 1202, 1203 (4/5) | NOT_IMPLEMENTED |
| 2 | Feeds RSS do YouTube com Disallow no robots → canal sem listagem | 1204 (1/5) | política/rota (LEGACY-99) |
| 3 | Sem contrato no Curator (qualify → contrato → rota → canário) | 5/5 | trabalho normal do Curator (D28) |
| 4 | Página oficial é uma notícia, não o índice da série (1200, 1201) | 2/5 | receita/alvo |
| 5 | Atividade recente não provada | 1201, 1203 | revisita |

Menor passo com maior efeito: uma rota **PODCAST_EPISODE_METADATA** (página pública do episódio: título, data, série — no desenho da D53) destrava 4 das 5. Precisa de decisão do dono; não foi criada aqui.

## 4. Provas
- URLs duplicadas na fila depois: **0** (1204 linhas, chave `normalizar`); IDs duplicados: **0**.
- Veterinária/IZS/zooprofiláctico em NOME/URL/PARA_QUE das 5: **0**.
- `py -m unittest tests.test_porta_de_candidatas`: **17/17 OK**.
- sha256 dos 15 bytes de prova, lidos do índice do Git: **15/15 iguais** ao `PEDIDOS.jsonl` (`.gitattributes -text`).
- ⚠️ O validador do mapa foi corrido uma vez **sem** a LOCK-PESADO (erro meu); a cadeia REGERAR correu depois com a chave.

## 5. Instalação: replay canónico, NUNCA o JSON da bancada

⚠️ A linha viva `source-curator-service-v1` já tem **1204** candidatas (a base desta bancada tinha 1199). Os IDs CAND-1200..1204 desta bancada **colidem** com os dela. O `candidatas/FONTES-CANDIDATAS.json` deste ramo é **prova da bancada**; não se faz merge que o substitua.

Instalar = `py research/media-sources-v1/replay.py --fila <fila viva> --gravar`, que chama `candidatas/fonte_nova.registar` para cada achado de `ACHADOS.json`. Dedup = o do dono (`normalizar(URL)`); o ID é o que a porta der na fila alvo. Sem `--gravar` só mede. Fila inexistente = falha alta (defeito apanhado no ensaio: a porta criava uma fila vazia).

| | Descobertas | Novas registadas | Dedup |
|---|---|---|---|
| Bancada (base 1199) | 5 | 5 (CAND-1200..1204) | 0 |
| Clone do vivo (1204, sha256 `772b5564…0605`), 1.ª vez | 5 | 5 → CAND-1205..1209 (1204→1209) | 0 |
| Clone do vivo, 2.ª vez | 5 | 0 | 5 (mesmos IDs) |

IDs/URLs duplicados no clone depois: 0/0. Ficheiro vivo antes e depois: mesmo sha256 (não tocado).
Testes: `py -m unittest research/media-sources-v1/test_replay.py` — 4/4 OK (medir não escreve; duas gravações idempotentes; URL com outra grafia vira DEDUP e o ID da bancada não se transporta; fila inexistente falha).
Os números 1205..1209 valem só para o vivo **tal como estava agora**; se ele crescer antes da instalação, os IDs mudam — é o esperado.

### 5.1 Prova da colisão e das 5 ARPAE intactas
No vivo, CAND-1200..1204 = 5 fontes ARPAE (`simc.arpae.it/status`, `infomet2`, `rt_data`, `dext3r`, `simclog2`). Replay no clone: as 5 ARPAE têm o **mesmo sha256 de linha** antes e depois (`PROVA-ARPAE-INTACTAS.txt`); **0 de 1204** linhas do vivo alteradas; os 5 achados recebem da porta CAND-1205..1209. O replay agora compara toda linha antiga e **falha alto** se alguma mudar (`LINHAS_ANTIGAS_ALTERADAS`); só o dedup do dono pode acrescentar `VISTA_TAMBEM_POR` à linha repetida, e isso sai listado à parte. Nenhum ID foi reescrito à mão. Testes: 5/5 OK (novo: IDs ocupados por outra lane ficam intactos).
