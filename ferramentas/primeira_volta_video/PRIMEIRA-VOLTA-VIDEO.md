# PRIMEIRA-VOLTA-VIDEO — os 10 canais com mais chance, e a 1.ª volta pronta a correr

Ramo `primeira-volta-video-v1`, a partir de `maestro-social-v2` @ 2111473a (= vivo `69b0e23f` +
freio-social-v2 + maestro): as ferramentas que a volta usa são as do **lote 3**. **Sem rede.** Vivo
e Sala real só lidos (Sala com `default_transaction_read_only=on`, DSN nunca impresso). **SEM MAPA.**

## Em palavras simples

- Olhei **59 contas**: os **41 canais** que já passaram ao Scrap e as **18 contas sociais novas**
  do vivo (9 LinkedIn + 9 YouTube).
- Para os 41 há **612 páginas de vídeo** guardadas na Sala (≈15 por canal, colhidas a 20/09),
  todas lidas com o sha256 conferido. As 18 novas **não têm nada guardado**: para elas a chance
  é **NÃO SEI**.
- Escolhi **10 canais**, um vídeo cada, lendo o que cada vídeo declara (título e descrição) e os
  números: quantos falam de **cultura + praga/doença**, quantos têm **pessoa com papel técnico**,
  quantos são **recentes** e **curtos**, e se há **legenda em italiano**.
- ⚠️ É um **indício**, não uma prova: a prova é a transcrição, depois da volta. Só **1 canal**
  (L'Informatore Agrario) é forte de verdade: 6 de 15 vídeos com cultura + praga + pessoa com
  nome e papel. Os outros 9 têm 0 a 2 vídeos assim.
- A 1.ª volta são **10 ondas**, uma por canal, **4 pedidos** cada ao YouTube (3 a `youtube.com` +
  1 a `googlevideo.com`, que contam juntos): **dentro do teto de 5**. **0** à API do Google: vai
  pelo **áudio público** (`audio-youtube`), que não precisa da chave nem do conserto P1.
- A transcrição corre **nesta máquina, com a placa de vídeo**: conferido hoje que o
  `faster-whisper` carrega no Python 3.12 e vê a GPU (1 placa). ~**47 min** de áudio no total.
- A retenção **D20 (30 dias) não se aplica** a esta rota: ela vale só para o que vem da API oficial.

## 1 · O universo e o que já está guardado

`UNIVERSO-59.json` (lido do vivo `69b0e23f`): 41 `CANAIS-41` (todos `SCRAP_FASE` · `canal-youtube` ·
`CANARY_PENDING`) + 18 `CONTAS-18` (9 `video-linkedin`, 9 `canal-youtube`, todas `CANARY_PENDING`).

`VIDEOS-GUARDADOS.json` (`videos_guardados.py`): as páginas `/watch` que a Sala guardou
(`raw_asset`, só leitura) e o ficheiro no armazém com o sha256 conferido. **612 lidas, 0 NAO_SEI**;
603 com título e data; 518 com descrição do autor; 532 com legenda. Cada campo é o que a página
declara (`ytInitialPlayerResponse`): nada inventado.

## 2 · Como se ordenou (`pontuar.py`, as listas de palavras estão no código)

Por vídeo: **CULTURA** (nomeia uma cultura) · **PROBLEMA** (praga, doença, infestante, «difesa»)
· **VOZ** (agronomo, ricercatore, prof., dott., intervista, webinar…) · **REGIAO** · **CURTO**
(≤ 540 s, o limite do baixador do freio) · **LEGENDA_IT** · **RECENTE** (12 meses antes de 20/09).
«Útil» = CULTURA + PROBLEMA + VOZ. Ordem: úteis recentes e curtos → úteis → cultura+praga →
recência. Tabela completa: `PONTUACAO.json`.

Duas correções minhas, feitas antes de escolher: a 1.ª lista de palavras apagava os espaços dentro
dos termos («mosca delle olive» nunca casava) e não tinha plurais (patate, pomodori, olive).
Os títulos foram lidos à mão depois da contagem: **a escolha final é número + leitura**, e o porquê
de cada um está escrito.

## 3 · Os 10 escolhidos (`VOLTA-1.tsv`)

| # | Fonte | Para | Vídeo da 1.ª volta | s | Porquê |
|---|---|---|---|---|---|
| 1 | IT-T8-006 L'Informatore Agrario | Voci | `CJkSwEuSP-o` Oliveto Smart — Intervista a Silverio Pachioli, agronomo fitopatologo (30/06/26) | 198 | 6/15 úteis, todos recentes e curtos; entrevistas com nome e papel |
| 2 | IT-T12-008 ASSAM Marche | Voci | `-37WbH5uyY8` AMAP a convegno: la difesa della mosca delle olive (15/07/26) | 191 | serviço regional; entrevistas com nome |
| 3 | IT-T5-040 CRPV | Scientifica | `kwdnOzbJV8Y` Approcci innovativi per la difesa delle piante ortofrutticole (04/12/25) | 326 | centro de pesquisa; webinars técnicos (os melhores são longos) |
| 4 | IT-T7-026 CONAF | Voci | `5tysjcD2H3M` Conoscere le minacce… strategia di difesa (21/05/25) | **805** | ordem dos agrónomos. ⚠️ passa de 540 s: ver §5 |
| 5 | IT-T8-004 Terra e Vita (Edagricole) | Voci | `s-x7v5HkA4g` …climate change in viticoltura (11/09/26) | 253 | imprensa técnica; entrevistas com pesquisadores |
| 6 | IT-T7-034 Consorzio Brunello | Voci | `x29XBSKzbD4` Presentazione Annata agronomica 2025 (26/11/25) | 155 | cultura (vinha) + lugar explícitos |
| 7 | IT-T9-014 Conserve Italia | Scientifica | `D317qbCYAcU` Miglioramento genetico di pesche e percoche (01/09/26) | 293 | projeto de melhoramento genético |
| 8 | IT-T7-025 CIA | Voci | `bmf0luQcjRY` Intervento su siccità di Stefano Calderoni (06/08/26) | 184 | dirigentes com nome, cultura e região; problema **abiótico** (vale para Voci, não para praga) |
| 9 | IT-T10-017 Myfruit | Voci | `OcRfQTiia3Y` Basilicata: dove nascono le fragole premium (13/04/26) | 208 | produtores + cultura + região; sem praga |
| 10 | IT-T9-017 Koppert Italia | Concorrenza (+Voci) | `JNkhc4s00tY` Biocontrollo su agrumi con Koppert (10/11/25) | 184 | técnicos por cultura; **empresa**: voz comercial, não neutra |

Todos com legenda italiana na página guardada. Os números por canal (guardados, úteis,
cultura+praga, recentes, curtos, último vídeo) estão no `VOLTA-1.tsv`.

**Ficaram de fora, com o porquê:** Georgofili (IT-T7-035) — pesquisadores, mas as palestras
guardadas duram de 43 min a 5,7 h (o baixador recusa acima de 540 s; as mais longas passariam
do teto de pedidos) e as curtas são visitas virtuais a exposições; Regione Piemonte/Toscana,
Pianeta PSR — títulos administrativos ou sem cultura/praga; Coldiretti — campanhas («Difendiamo
l'olio»), não voz técnica; CNR ISAFOM, UNINA — último vídeo guardado de 2020 e 2023.

**As 18 contas novas: NÃO SEI.** Nada guardado. Pelos nomes, as que mais prometem para uma 2.ª
volta são UNIMI DiSAA e ISPRA (LinkedIn, T5), Olio Officina (IT-T5-192) e os canais de ARPAT/ARPAE
e das Regiões Lombardia/Campania (IT-T2-166/167, IT-T12-152/153) — **isto é palpite pelo nome**,
não medida. As LinkedIn são páginas de organização: vídeo de pessoa identificada só pela D80.

## 4 · A 1.ª volta — pedidos, transcrição, retenção

**Quando:** logo que o **lote 3** (freio-social-v2 + maestro-social-v2 + canais-41-runbook-v1)
estiver no vivo, VPN IT, **depois** da micro social (D80 2c) e **nunca** na mesma janela dela.

**Plano a seco** (`MAESTRO-SOCIAL-PLANO.json`, `--so-plano --canario`, cópia deste ramo com os
livros do vivo): **10 ondas, 1 vídeo cada, previsto `{"youtube.com": 4}` por onda,
`TODAS_CABEM: true`**, teto 5 por domínio na onda.

| Domínio | Pedidos por vídeo | Na volta (10) | Teto |
|---|---|---|---|
| `youtube.com` (página + player + API interna) | 3 | 30 | 5 por onda |
| `googlevideo.com` (o áudio, 1 fatia de 50M) | 1 | 10 | conta no mesmo balde do youtube.com |
| `googleapis.com` | 0 | 0 | — |
| portão de egresso (`superficie/rede.py`) | antes e depois de cada fonte | — | não é da fonte |

Medido pela bancada do freio (servidor local, yt-dlp real): áudio até 25 MiB = **4 pedidos**;
vídeo acima do limite de duração = **3** e nada ao googlevideo (`VIDEO_LONGO_DEMAIS`).

**O comando** (o coordenador; pasta nova):

```bash
py superficie/rede.py --portao-de-egresso IT
SINTONIA_YT_DURACAO_MAX_S=900 SINTONIA_ASR_DEVICE=GPU \
py ferramentas/maestro_social/maestro_social.py --correr --autorizado-pelo-dono --canario \
   --saida=<pasta nova> \
   --fontes=IT-T8-006,IT-T12-008,IT-T5-040,IT-T7-026,IT-T8-004,IT-T7-034,IT-T9-014,IT-T7-025,IT-T10-017,IT-T9-017 \
   --videos=IT-T8-006:CJkSwEuSP-o,IT-T12-008:-37WbH5uyY8,IT-T5-040:kwdnOzbJV8Y,IT-T7-026:5tysjcD2H3M,IT-T8-004:s-x7v5HkA4g,IT-T7-034:x29XBSKzbD4,IT-T9-014:D317qbCYAcU,IT-T7-025:bmf0luQcjRY,IT-T10-017:OcRfQTiia3Y,IT-T9-017:JNkhc4s00tY
# a meio: o mesmo comando com --retomar
py ferramentas/maestro_social/maestro_social.py --relatorio --estado=<pasta>/MAESTRO-SOCIAL-ESTADO.json
```

O maestro pára sozinho: fora de IT, > 30 min, 3 FAILED seguidas, livro da onda acima do teto,
prova-teto ≠ PASS.

**Transcrição:** não é um passo à parte. Depois de o áudio ser guardado (RAW), a derivação do
ingresso (`coleta/ingresso.py` → `coleta/executor_transcricao_midia.py`) pede o texto ao dono
único do ASR, `ferramentas/fala_local.py` (`faster-whisper`, modelo `small` por omissão, em
`~/.sintonia-libs`). ⚠️ O dispositivo por omissão é **CPU** (`SINTONIA_ASR_DEVICE`): o comando
acima põe `GPU`. Conferido hoje: `ctranslate2 4.8.2` vê **1** placa CUDA e `faster_whisper`
importa no Python 3.12.10 (a nota antiga «ASR falha no 3.12» já não vale). Áudio total
**2 797 s ≈ 47 min**; **tempo de transcrição: NÃO SEI**, não medido hoje. As páginas guardadas
têm legenda italiana automática nos 10; a legenda **não** substitui a transcrição (é outra rota).

**Retenção:** `coleta/social_envelope.retencao_da_rota` só põe prazo às rotas
`youtube-data-api-v3:*` (D20: 30 dias, renovar ou apagar). O `audio-youtube` não é dessa rota:
**sem prazo D20**, e a D20 não mexe em áudio/transcrição local (D20.2). Se a volta usar a listagem
`canal-youtube` (API, com a chave no GitHub), esses itens levam o prazo de 30 dias.

**O juízo depois da volta** é o do `CANAIS-41-RUNBOOK` (§5–6): `regua_social` com a D36 (o recibo
`audio-youtube` satisfaz o contrato `canal-youtube` com as 4 provas canal→vídeo→áudio) e a D53
(página, título, data, canal); o `para_aplicar.py` separa defeito nosso de falha da fonte.

## 5 · O que precisa de decisão

- **CONAF (805 s):** o baixador recusa acima de 540 s. Com `SINTONIA_YT_DURACAO_MAX_S=900` só
  nesta volta: estimativa ≈13 MB de áudio a ~130 kbit/s (não medido), 1 fatia de 50M, 4 pedidos
  (o teto não muda). Nenhum dos outros 9 está
  entre 540 e 900 s. **Sem essa decisão:** trocar para `AttwCVnZBjg` (102 s, mais fraco:
  «Isole di calore l'appello degli agronomi») e tirar a variável do comando.
- **Koppert** é concorrência (T9): entra como voz técnica, marcada como comercial.
- As páginas são de 20/09: um vídeo pode ter sido tirado desde então (o recibo di-lo; a D53 reprova).

## 6 · O que isto não prova

- Que os vídeos rendem: título e descrição são indício; a transcrição é que diz se há pessoa +
  cultura + problema + lugar + tempo.
- As 18 contas novas: sem medida.
- Tempo de transcrição e pedidos reais: o que está aqui é previsto pelo plano e pela bancada do freio.
