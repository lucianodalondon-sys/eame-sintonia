# PODCAST-ESTUDO-V1 — o menor caminho para colher podcasts (estudo, NÃO instalado)

**Base:** vivo `origin/servico-20260923-0923 @ e5cd691f` · **Ramo:** `podcast-estudo-v1` · **Data:** 2026-09-25
**Rede:** fechada — 0 pedidos às fontes. **Sala:** não lida (a pergunta não pedia dados da Sala). **Vivo:** não tocado.
Provas de rede usadas: as 15 já guardadas no ramo `research-media-sources-v1` (`research/media-sources-v1/prova/`, sha256 em `PEDIDOS.jsonl`).

## 1. O que já existe (medido no código de e5cd691f)

| Peça | Existe? | Onde | Serve para podcast? |
|---|---|---|---|
| Transcrever áudio | **SIM** | `coleta/executor_transcricao_midia.py` (famílias `audio`/`video`, `NETWORK_REQUIRED=NO`, ASR em `ferramentas/fala_local.py`) | **SIM, sem mudar nada**: não sabe de onde o byte veio, por desenho |
| Mandar o áudio para o transcritor | **SIM** | `coleta/ingresso.py:657 executor_para(media_type)` → `audio/mpeg` cai na família `audio` | **SIM**, desde que o RAW chegue com `MEDIA_TYPE` |
| Baixar bytes com teto D38 | **SIM** | `coleta/italy_pilot_collect.mjs` (curl, sem `-L`: cada salto é um pedido ao seu domínio registável; teto por onda) | **SIM** para 1 feed + poucos episódios; ver riscos |
| Ler um feed | **SÓ Atom do YouTube** | `curadoria/capturador.py:547` (`<entry>`), `curadoria/canario.py:81` (`<yt:videoId>`) | **NÃO**: podcast é RSS 2.0 (`<item>`, `<pubDate>`, `<enclosure>`) — **nenhuma linha** da casa lê `<item>`/`enclosure` |
| Contrato com saída de áudio | **NÃO** | `curadoria/validar_contratos.py:38` `OUTPUTS = {HTML, PDF, VIDEO_METADATA}` | **NOT_IMPLEMENTED** |
| Data de publicação | **SIM para ISO** | `coleta/executor_texto_de_html.py:380 tempo_de_publicacao` / `normalizar_instante` | **NÃO para RSS**: `"Fri, 20 Sep 2024 07:26:29 +0000"` → `nao e ISO 8601` (medido) |
| Local da fonte | **SIM** | `leis/lugar_da_organizacao.py` (sede no cadastro-mestre → país no Atlas → NÃO SEI), chamado em `curadoria/worker.py:321` | **SIM**, pelo site oficial que aponta o feed |

**Veredito:** a metade de trás (bytes → transcrição → derivado) **já existe**. Faltam 3 peças na frente: **ler RSS**, **contrato com saída de áudio**, **converter a data RSS**. Nenhuma é arquitetura nova: cada uma é o irmão de uma peça que já existe para o YouTube.

## 2. Medidas desta missão (offline)

**Data (`normalizar_instante`, e5cd691f):**

| Entrada | Resultado |
|---|---|
| `Fri, 20 Sep 2024 07:26:29 +0000` (RSS) | `None — nao e ISO 8601` |
| `Mon, 02 Dec 2024 05:00:00 GMT` (RSS) | `None — nao e ISO 8601` |
| `2024-09-20 07:26:29` (página Spreaker, sem fuso) | `2024-09-20`, precisão DIA |
| `2025-05-14T09:01:03-07:00` (YouTube) | instante, precisão INSTANTE |

**Local da fonte (`lugar_da_organizacao`):**

| Site passado | Resultado |
|---|---|
| crea.gov.it | **Roma**, PROVINCE (cadastro-mestre IT-OWN-016) |
| reterurale.it | NÃO SEI (sem sede no cadastro nem país no Atlas) |
| ilsole24ore.com | NÃO SEI |
| spreaker.com, anchor.fm, open.spotify.com, podcasts.apple.com, linkedin.com, facebook.com | NÃO SEI (certo) |
| **youtube.com/…, instagram.com/…** | **ITALY, COUNTRY — ERRADO**: vem do país de OUTRAS fontes italianas cujo canal está no Atlas (IT-T10-017…, IT-T8-003) |

⚠️ **Armadilha latente, não defeito ativo:** hoje o único chamador (`worker.py:321`) passa o site declarado na ficha (`RSY.ligacao_oficial`), e na fila de e5cd691f **0 de 150** fichas YouTube/LinkedIn declaram um endereço de plataforma como site oficial. Mas uma rota de podcast que passasse o **host do feed** ou do canal cairia nela. Proposta: guarda de plataformas → NÃO SEI, com teste, **à parte** deste estudo.

## 3. As 5 fontes

| Fonte | Feed de podcast | robots | Data por episódio | Local da fonte | Caminho |
|---|---|---|---|---|---|
| Rete Rurale | `spreaker.com/show/5506797/episodes/feed` (anunciado na página) | **ALLOW** (medido) | página: 9/9 com `published_at`; feed: NÃO SEI (não aberto) | NÃO SEI (falta sede no cadastro) | **RSS → áudio → transcrição** |
| Madre Terra | `anchor.fm/s/724a46c0/podcast/rss` (via link da página) | **NÃO MEDIDO** | página: 1 episódio (2 dic 2024) | NÃO SEI | RSS, depois de medir robots |
| Agrifuturo | show no Spreaker não identificado (a página liga o ep. 3 em `spreaker.com/user/17008151/…`) | Spreaker ALLOW | NÃO SEI | Roma (CREA) | achar o show primeiro |
| TEA alle 5 | **NÃO SEI** onde estão os episódios | — | NÃO SEI | Roma (CREA) | parado até achar os episódios |
| agrifake | não é podcast desde 2025 (só YouTube); feed do YouTube **DISALLOW** (medido) | — | página do vídeo: `uploadDate` exato | NÃO SEI (sem site oficial; **nunca** pelo canal) | **rota YouTube que já existe** (D53) + áudio que já existe |

## 4. Proposta — o menor caminho (nada disto instalado)

1. **Contrato (Curator)**: `OUTPUTS` += `AUDIO` e um molde `contrato_podcast` **irmão** do molde YouTube de `curadoria/escrever_contratos.py:120-155`:
   `FEED_URL`, `CAPTURES.item FROM FEED FIELD guid` (sem guid → `enclosure url`), `DOCUMENT_ID = {SOURCE_ID}:POD:{guid}`, `TIME_RULE: pubDate = PUBLICATION_TIME, NÃO é FACT_TIME`, `FACT_LOCATION_RULE: UNKNOWN — nunca pelo feed nem pelo publicador`, `EXPECTED_FAILURES: feed sem <item> = EMPTY_LIST; item sem enclosure audio/* = FAILED`, `MAX_TARGETS` pequeno.
2. **Leitor de `<item>`** ao lado do leitor de `<entry>` em `curadoria/capturador.py`: título, `pubDate`, `guid`, `enclosure url/type/length`, cada um do SEU bloco (a mesma lição do `<entry>`).
3. **Data**: `pubDate` (RFC 822) → ISO com `email.utils.parsedate_to_datetime` (biblioteca padrão, sem rede) **antes** de `normalizar_instante`; `PUBLICATION_TIME_BASIS = RSS_PUBDATE`; o texto original guardado. Sem fuso ou ilegível = NÃO SEI. **Não** mexer em `normalizar_instante` (é o dono das datas HTML).
4. **Download**: o coletor que já existe, 1 pedido ao feed + o `enclosure` de poucos episódios por onda. Cada salto de redirecionamento é um pedido ao seu domínio (a CDN do áudio conta no seu próprio teto). Robots de **cada** domínio antes.
5. **Transcrição**: nada a fazer: `audio/mpeg` já cai em `executor_transcricao_midia` pela família. Com a placa de vídeo, como o resto da casa.
6. **Local da fonte**: `lugar_da_organizacao(<site oficial que aponta o feed>)`, nunca o host do feed. Para RRN e Sole 24 Ore dá NÃO SEI até alguém pôr a sede no cadastro-mestre com prova.
7. **Local e data do fato**: pela Admissão, do **texto transcrito**, como qualquer texto (D62/D63/D64). Episódio sem lugar **não** é descartado.

## 5. Riscos e o que não sei

- **Tamanho do mp3**: um episódio de ~28 min tem dezenas de MB; o curl do coletor tem `--max-time 90`. **NÃO SEI** se chega: medir num episódio antes de ligar.
- **ASR no Python 3.12**: memória da casa diz que as bibliotecas do ASR são cp311, então no 3.12 o áudio fica sem texto. Dívida conhecida, não é deste estudo.
- **Feeds não abertos**: se o RSS da RRN tem `pubDate`/`enclosure` em cada item é **NÃO SEI** até 1 pedido.
- **Anchor.fm**: robots não medido.
- **Pessoas (D24)**: convidados falam nos episódios; guarda-se o episódio como publicado pelo publicador, sem recolher dados dos convidados.
- **Veterinária (D26)**: episódios de saúde animal (ex.: série de peste suína do agrifake) ficam fora pela Admissão/tema, não pelo canal inteiro.

## 6. Para medir o que falta (só com autorização de rede)
1 pedido cada, robots antes, D38: (a) feed RRN no Spreaker; (b) robots + feed anchor.fm (Madre Terra); (c) página do ep. 3 do Agrifuturo no Spreaker, para achar o show.
