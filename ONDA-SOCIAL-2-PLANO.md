# ONDA-SOCIAL-2-PLANO — a onda social completa, depois da micro (26/09, SÓ PLANO)

Ramo `onda-social-2-v1` a partir do vivo `83de0ccd`. **Sem código novo nesta entrega** (as mudanças de código
estão descritas no §6, com dono); o ramo leva este plano e as provas em `ferramentas/onda_social_2/`.
Rede FECHADA em tudo o que correu (`HTTP(S)_PROXY=127.0.0.1:9`). Vivo só lido; nada instalado; Sala não tocada.

**De onde vêm os números:** uma cópia `C:/ens-os2` = `83de0ccd` + os 16 livros sujos do vivo copiados às 03:17
(sha256 em `ferramentas/onda_social_2/COPIA-LIVROS-VIVO.sha256`; o bot corria: é uma fotografia ficheiro a ficheiro).
Nela correu o caminho canónico (semear → QUALIFY → BUILD_CONTRACT → VALIDATE_ROUTE) em **todas** as elegíveis, com a
fila filtrada (`curadoria/ensaio_so_linkedin.py`). O que já aconteceu de verdade na rede vem do canário real de
24/09 (`curadoria/SOC-ONDA2-CANARIO-LINKEDIN-V1.json` do vivo) e da medida offline do yt-dlp (SOCIAL-QUALIFICAR).

## 1 · O universo, medido (candidatas sociais no livro vivo)

| | total | identidade + site oficial | depois do QUALIFY na cópia |
|---|---|---|---|
| **LinkedIn — organizações** | 44 | 40 | **37 com número e contrato** · 3 recusadas (território) · 4 sem identidade (`/showcase/`) |
| **LinkedIn — PESSOAS** | 24 | 0 | nenhuma entra: não há rota nem fase (§4) |
| **YouTube** | 82 | 64 | **9 novos** · 48 fontes que já existiam (49 candidatas: IT-T2-026 tem duas) · 1 repetida de um canal da micro · 5 recusados (território) · 18 não elegíveis |

- **As 3 + 5 recusas** são todas «território indeterminado pelo nome — SOURCE_ID fica UNKNOWN, sem fabricar»:
  LinkedIn Fieravicola (CAND-0096), Interpoma (0131), Valagro (0092); YouTube Granarolo (0193), Interpoma (0234),
  Società Entomologica Italiana (0221), Valagro (0183 — ⚠️ o endereço é `@syngenta`), «Canal YOUTUBE» (0300).
- **4 LinkedIn `/showcase/`** (Agrofarma 0109, Assofertilizzanti 0110, Rete Rurale Nazionale 0123, Edagricole 0099):
  a identidade só reconhece `/company/`. Decisão (§7).
- **18 YouTube não elegíveis:** 7 sem ligação provada ao site oficial (AgroNotizie, Agromoderni, ISMEA, L'Informatore
  Agrario, Noi Siamo Agricoltura, Stato Brado, e o único canal de PESSOA: Simon Pierce, UNIMI — CAND-1199) e 11 sem
  `channel_id` (listas de reprodução, `@handle` sem UC, `/user/` não resolvido).
- **Os 48 YouTube que já são fonte:** 39 estão nos 41 que a `legacy-99-v5` passa para a rota do Scrap. **9 não
  estão**: estão em `RETRY_AFTER` na rota ANTIGA de feed (`YOUTUBE_CHANNEL_FEED`, que o robots barra) — e **7 destes
  9 são de pesquisa**: Fondazione Navarra (IT-T5-042), UNIBO DISTAL (043), Fondazione Minoprio (044), ISPRA (045),
  UNIBA DiSSPA (047), UNICT Di3A (048), Univ. Bolzano (050); mais Cantina Riunite (IT-T7-016) e Confagricoltura
  Lombardia (IT-T7-018). **Sem mudança, os canais de pesquisa ficam de fora da onda.** (§6, C4)
- **Lugar da fonte (SOURCE_LOCATION)** nos 46 novos: COUNTRY 33, PROVINCE 2, **NÃO SEI 11** — pelo site oficial
  (`leis/lugar_da_organizacao.py`), nada preenchido à mão.

Tabela completa, conta a conta (número proposto, território e porquê, lugar e precisão):
`ferramentas/onda_social_2/ENSAIO-QUALIFY-TODAS.json`. ⚠️ **Os números são PROPOSTOS**: dependem da ordem em que se
semeia (semear 9 ou 40 dá números diferentes — medido); os que valem lêem-se no vivo depois.

## 2 · O que o canário real de 24/09 já disse (LinkedIn, 37 contas, teto 2)

- **14 contas deram vídeo (20 vídeos); 23 deram zero** — «ZERO LEGÍTIMO NÃO É FALHA»: a página que um convidado vê
  mostra só os posts mais recentes, e entre eles não havia vídeo. Tempo por conta: 9-17 s quando dá zero,
  32-171 s quando baixa vídeo.
- Com vídeo: ARPA VdA, ASSAM Marche, CIA, **CRPV**, Caviro, Certis Belchim, Grana Padano, **ISPRA**, Italmopa, Macfrut,
  Regione Piemonte, **SIA — Società Italiana di Agronomia**, **UNIBO DISTAL**, **UNIMI DiSAA**.
- ⚠️ **ARPA VdA e ISPRA trouxeram o MESMO vídeo** (679.948 bytes os dois): a ARPA partilha posts do ISPRA. A mesma
  coisa vai voltar a acontecer entre contas que se partilham; o bruto repete, o conteúdo é um só.

## 3 · Prioridade (D24: pesquisadores e agrónomos, organizações de pesquisa)

| nível | LinkedIn | YouTube |
|---|---|---|
| **P1 — pesquisa e agronomia** | SIA agronomia (CAND-0124, deu vídeo), CRPV (0093, deu vídeo), UNIBO DISTAL (0100, deu vídeo), CNR (0113), Fondazione Minoprio (0104), Univ. Bolzano (0132) · na micro: ISPRA, UNIMI DiSAA | na v5: CNR ISAFOM (IT-T5-037), UNINA Agraria (038), CRPV (040), **CONAF — agrónomos** (IT-T7-026) · na micro: crea.gov.it (CAND-0423) · **travados (C4): os 7 de pesquisa em RETRY** |
| **P2 — agências e instituições** | ARPA Lazio/Lombardia/Marche/Molise/Piemonte, ARPAT, APPA Trento, ASSAM, Regione Piemonte | ARPA (v5: IT-T2-025..028), Regiões (IT-T12-*), micro: ARPAT, arpae.it, Lombardia, Campania |
| **P3 — associações e consórcios** | Assosementi, Coldiretti, FederUnacoma, Valpolicella, Bonifica Piave, Olio Officina | v5: consórcios e associações (IT-T7-*) |
| **P4 — feiras, media, empresas** | SANA, SIMEI, Myfruit, WineNews, FreshPlaza, Koppert, Cifo | v5: T8/T9/T10/T11 |
| **Pessoas (D24)** | 24 perfis (CNR-IBBA ×6, UNIVR, UNIMI DISAA…) — **bloqueadas** (§4) | Simon Pierce (UNIMI) — falta a ligação oficial |

## 4 · Pessoas: onde está o nó (sem inventar)

- A casa **sabe** colher o vídeo de uma pessoa: `coleta/adaptador_linkedin.video_de_post_publico` (D24, rota
  `linkedin:post-publico-de-pessoa`, D41 com os três campos). Mas **só a partir do endereço de um POST**: a página
  do PERFIL (`/in/<slug>/`) responde **HTTP 999 com authwall** (medido e escrito no código) e não se contorna.
- As 24 candidatas têm **só o endereço do perfil**. Nenhuma fase do Scrap chama a rota de pessoa
  (`scrap_colheita.FASES` só tem `video-linkedin` de organização), e o semear não reconhece `/in/`.
- **Falta decidir DE ONDE vêm os endereços de posts** de cada pessoa sem login (§7, decisão 2). Sem isso, as
  pessoas não entram — e o plano não finge que entram.

## 5 · As rodadas (teto D38: 5 pedidos por domínio registável por onda)

Pedidos por unidade (medidos ou lidos, e de onde):
- **YouTube, 1 vídeo:** youtube.com 3 + googlevideo.com 1 por ~10 MiB de áudio — **o mesmo orçamento (D41)**.
  MEDIDO offline (SOCIAL-QUALIFICAR, yt-dlp 2026.08.19 sem deno). Vídeo até ~9 min = **4**; 10-19 min = 5; ≥20 = 6+.
  É o mínimo: um 403 com novas tentativas soma pedidos.
- **LinkedIn, 1 conta com `teto=1`:** linkedin.com 1 (página) + 1 (post, se houver vídeo) = 1 a 2; licdn.com 1 a 2.
  LIDO no código; o canário de 24/09 confirma a forma (zero = 1 pedido, rápido).

**Uma onda = até 2 contas LinkedIn (`teto=1`) + 1 vídeo YouTube (≤ ~9 min)** — domínios diferentes, cada um dentro
de 5: linkedin.com ≤ 4, licdn.com ≤ 4, youtube.com+googlevideo.com = 4. Sequencial (D28: orquestrador → executor,
nada em paralelo). **Prova-teto a seguir a cada onda**; FAIL ou NAO_SEI → parar.

**Passagem A — largura (1 vídeo por conta/canal):**
- LinkedIn: as 28 contas fora da micro → **14 ondas** (P1 primeiro).
- YouTube: 9 (micro) + 41 (v5) = **50 canais → 50 ondas**; +7-9 se o C4 entrar.
- Como os dois domínios cabem na mesma onda, **a passagem A são ~50-59 ondas** (o YouTube manda).

**Passagem B — profundidade («o máximo»):** o que o convidado vê. LinkedIn: 1 conta por onda com `teto=2`
(linkedin.com 3, licdn.com 2-4) só nas 14+ que já deram vídeo. YouTube: mais 2 vídeos por canal = ~100-120 ondas.
As 23 contas de zero: re-sondar 1 vez por semana (1 pedido cada).

**Duração estimada (ESTIMATIVA, não medida como onda):** por onda ~3-6 min (2 contas LinkedIn: 20 s a 5 min, medido
em 24/09; 1 vídeo YouTube: descarga + ASR na GPU ~2-3 min, estimado; + portão de egresso e prova-teto ~1 min).
- Passagem A: **~50-59 ondas ≈ 3-6 h de máquina** → 1 dia de trabalho.
- Passagem B: **~100-120 ondas ≈ 6-12 h** → 2 dias, respeitando o YouTube (429 depois de ~120 páginas `/watch` —
  memória da casa): **≤ 60 vídeos YouTube por dia**.
- Mais o que não é máquina: listar os `VIDEO_ID` (§7, decisão 5), qualificação e instalação.

## 6 · O que muda no código (NÃO feito aqui; cada um com dono)

| | mudança | porquê | dono |
|---|---|---|---|
| **C1** | **executor de onda social** (como `ferramentas/big_collection/onda_web.py` para a web): corre o lote, lê o contador do `scrap_http` antes de cada fonte e **recusa** a que passaria de 5 por domínio; no YouTube só lança o yt-dlp se sobrar orçamento para `3 + fatias` | hoje o Scrap só **conta** (PROVA-TETO-SOCIAL); ninguém **trava** antes — o teto D38 só existe no transporte web | Scrap + coordenação |
| **C2** | o plano da onda social passa `teto=1` quando há 2 contas LinkedIn na onda | `plano_onda_social.py` copia `teto: 2` do contrato → 2 contas = 6 pedidos, passa o teto | Curator (plano social) |
| **C3** | yt-dlp: `--http-chunk-size 50M`, `--retries 1 --fragment-retries 1`, `--match-filter "duration<=540"` | vídeo até 50 MiB = 4 pedidos; um 403 não vira 10; vídeo longo não descarrega | Scrap (`ferramentas/youtube_transcrever.py`) |
| **C4** | levar os 9 canais em `RETRY_AFTER` (7 de pesquisa) para a rota do Scrap, como a v5 faz com os 41 | estão presos na rota de feed que o robots barra; a v5 só levou os que estavam READY | SEPARAR-A-B (legacy-99) |
| **C5** | pessoas: fase `video-post-linkedin` no Scrap (chama `video_de_post_publico`) + identidade de pessoa no QUALIFY | a rota existe no adaptador mas nenhuma fase a chama | Scrap + Curator — **só depois da decisão 2** |
| **C6** | `/showcase/` como identidade de organização | 4 contas oficiais ficam de fora | Curator — **só depois da decisão 3** |

## 7 · O que o dono precisa decidir

1. **Território das 8 recusadas** (3 LinkedIn + 5 YouTube, lista no §1) — ou deixá-las fora. O robô não adivinha.
2. **Pessoas (D24): de onde podem vir os endereços de POSTS** de cada pesquisador, sem login (ex.: posts que
   aparecem nas páginas das organizações onde trabalham; páginas de eventos/instituições que os citam; lista dada
   pelo dono). Sem esta decisão as 24 pessoas não entram.
3. **`/showcase/` conta como página da organização?** (Agrofarma, Assofertilizzanti, Rete Rurale, Edagricole)
4. **YouTube sem ligação oficial ou sem `channel_id`** (18): aceitar canais de MEDIA sem link no site (AgroNotizie,
   Informatore Agrario, ISMEA…)? E o canal de pessoa (Simon Pierce) — basta a página da universidade que o cita?
5. **Como listar os `VIDEO_ID`**: a fase `canal-youtube` usa a API oficial, cuja chave só existe no GitHub Actions.
   Correr a listagem lá? E a API (`googleapis.com`) conta para o D38? Listar 50 canais = ~100 pedidos à API numa
   corrida só.
6. **Cadência**: quantas ondas por hora/dia (a casa não tem regra de intervalo entre ondas; proponho ≤ 60 vídeos
   YouTube/dia e uma onda a cada ~10 min).
7. **Lugar NÃO SEI em 11 contas**: coletar assim (D62 diz sim: nunca descartar por falta de dado) — ou o dono
   acrescenta a sede ao cadastro-mestre (fonte, não palpite).

## 8 · Ordem da onda (depois da micro)

0. Micro social (SOCIAL-QUALIFICAR) e instalação de `social-qualificar-v2` + `legacy-99-v5`
   (`PLANO-INSTALACAO-SOCIAL.md`).
1. **Q1 — qualificar as 28 LinkedIn restantes** pelo caminho canónico, com o bot parado, num só lote:
   `py curadoria/semear_qualify_social.py --candidatas CAND-0093,CAND-0095,CAND-0098,CAND-0100,CAND-0101,CAND-0102,CAND-0104,CAND-0106,CAND-0107,CAND-0108,CAND-0111,CAND-0113,CAND-0115,CAND-0116,CAND-0117,CAND-0120,CAND-0121,CAND-0122,CAND-0124,CAND-0125,CAND-0126,CAND-0127,CAND-0128,CAND-0129,CAND-0130,CAND-0132,CAND-0134,CAND-0135`
   (mostrar → `--aplicar --vivo`). O bot pára em `CANARY_PENDING` — sem rede (rota do Scrap).
2. **C1 + C2** instalados (sem eles, nenhuma onda de mais de 1 conta).
3. **Passagem A** (§5), P1 primeiro; régua social (`regua_social.py --vivo`, SOCIAL/v1 + D36 + D53) depois de cada
   lote de ondas, com o bot parado.
4. **C4** e as decisões 1-5 → Q2 com o que elas abrirem.
5. **Passagem B.**

## Provas (no ramo, `ferramentas/onda_social_2/`)
`INVENTARIO-SOCIAL-VIVO.json` (as 150 candidatas sociais, identidade e ligação) · `ENSAIO-QUALIFY-TODAS.json`
(o resultado conta a conta) · `ENSAIO-QUALIFY-LINKEDIN-40.json` / `-YOUTUBE-64.json` (saída do ensaio) ·
`COPIA-LIVROS-VIVO.sha256`. Fora do Git: a cópia `C:/ens-os2`.

## EM PALAVRAS SIMPLES

- **Quantas contas dá para coletar:** 37 páginas de organizações no LinkedIn e 50 canais no YouTube (59 se
  destravarmos 9). Os perfis de **pessoas** (24 pesquisadores) ainda **não** dá.
- **Por que as pessoas não entram:** o LinkedIn fecha a página do perfil para quem não faz login (dá "erro 999").
  A gente só consegue pegar o vídeo se tiver o endereço de um **post** da pessoa — e hoje não temos nenhum. Você
  precisa decidir de onde esses endereços podem vir.
- **Um achado importante:** 7 canais de **pesquisa** no YouTube (ISPRA, UNIBO, Bolzano…) estão presos num caminho
  antigo que não funciona mais. Se ninguém os mudar de caminho, justamente os de pesquisa ficam de fora.
- **Como é uma rodada:** 2 contas do LinkedIn + 1 vídeo curto do YouTube, sem passar de 5 pedidos por site.
  A primeira volta (1 vídeo de cada) dá **umas 50 a 59 rodadas, cerca de 1 dia de máquina**. Pegar mais vídeos de
  cada uma leva **mais uns 2 dias**. Isso é **estimativa**, não medida.
- **Falta um "freio" no código:** hoje o sistema conta os pedidos depois, mas não impede o pedido que passaria do
  limite. Antes da onda grande, precisa desse freio (e de pedir 1 vídeo por conta no LinkedIn).
- **Você decide 7 coisas** (lista no §7): as 8 contas cujo assunto o robô não descobriu, de onde vêm os posts das
  pessoas, e mais 5.
- **Nada foi coletado, instalado ou mexido no vivo.** Os números de fonte da tabela são propostos: mudam conforme a
  ordem em que se instala.
