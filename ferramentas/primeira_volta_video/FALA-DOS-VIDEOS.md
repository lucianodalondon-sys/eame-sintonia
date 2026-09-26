# FALA-DOS-VIDEOS — quanto da fala já temos, e quanto custa transcrever os 50 mais promissores

Ramo `primeira-volta-video-v1`. **Sem rede.** Sala real só lida (`default_transaction_read_only=on`,
DSN nunca impresso); armazém só lido. **SEM MAPA.**

## Em palavras simples

- **Fala guardada hoje: 0 de 737 vídeos.** Nenhum tem transcrição. A Sala inteira tem só 2
  transcrições, e nenhuma é destes vídeos: são um post do LinkedIn de Espanha e um áudio de teste.
- Dos 737:
  - **612** são páginas de vídeo com título, data, duração e descrição;
  - **125** são **registos de falha** (`status 429` = o YouTube mandou parar), dos 9 canais de
    pesquisa (UNIBO, ISPRA, UNIBA, UNICT, Univ. Bolzano, Minoprio…): **sem título nem duração**.
- **Legenda:** 532 das 612 páginas dizem que o YouTube **tem** legenda (quase sempre a automática,
  em italiano). Mas o **texto** da legenda não está guardado. Baixá-lo de um canal de terceiros está
  **NÃO** na matriz de regras (`captions.download`: exige permissão do dono do canal). O caminho que
  sobra é o áudio público + transcrição nesta máquina (D17.4).
- **Os 50 mais promissores** dos canais técnicos (a regra está no código):
  - **14** já vão nas voltas 1 e 2: não se pedem outra vez;
  - **32** novos, em **7 voltas**: ~**8,1 h** de áudio, **96** pedidos a `youtube.com` + **36** a
    `googlevideo.com`, **≈ 14 min de placa de vídeo** (≈ 100 min se fosse no processador);
  - **4** não cabem no teto de 5 pedidos: palestras de 2,7 a 3,7 h do Georgofili e da AMAP.
- ⚠️ Os números de tempo e de pedidos longos são **estimativas**: o tamanho do áudio só se sabe no
  pedido (hipótese de 128 kbit/s; a 160 kbit/s mais 2 vídeos passam do teto), e a velocidade da
  placa é a medida de 14/09 (34 vezes o tempo real, modelo `small`).

## 1 · O que se mediu (Sala, só leitura)

| | Vídeos | Derivado guardado |
|---|---|---|
| Páginas `/watch` (`text/html`) | 612 | `TEXT_EXTRACTION` (o texto da página) em 612; **transcrição em 0** |
| Registos JSON (`application/json`) | 125 | nenhum — são falhas `429`/`TRANSPORT_OR_EMPTY` de 20/09 (IT-T5-042…050, IT-T7-016/018) |
| **Total** | **737** (50 fontes) | **transcrição: 0** |

Transcrições na Sala inteira: **2** (`ES-T8-002`, post LinkedIn; `IT-T8-001`, áudio `NAO SEI`). Fora
da Sala, nenhum dos 737 identificadores aparece junto de uma transcrição no repositório (só em
páginas de notícia que incorporam o vídeo e nas listas do Curator). O `leitor-data-yt` (no vivo pela
INTEGRA-NOITE) lê a **data** de publicação da página, não a fala.

## 2 · Os 50 (`FALA-50.json`, `fala_dos_videos.py`)

Canais técnicos: CRPV, CONAF, L'Informatore Agrario (entrevistas Condifesa/universidades), Terra e
Vita, ASSAM/AMAP, ARSAC, Pianeta PSR (Rete Rurale/CREA), Georgofili, UNINA, Conserve Italia, CAI,
ANBI e consorzi di bonifica, consorzi di tutela, Regiões, Koppert (concorrente, marcado). **CNR fora**
(coordenação 10:13).

Entra um vídeo com **problema** (praga, doença, «difesa»…), ou com **cultura + (pessoa OU formato de
palestra)**. Sai propaganda e administração (lista no código). Pontos: problema 3, cultura 2, voz 2,
recente 1, palestra 1 — com as correcções da 2.ª lista (descrição partilhada do evento não conta;
«fitopatologo» é papel, não problema). **52 vídeos passam; os 50 de mais pontos**, até 10 por canal.

| | N | Áudio | youtube.com | googlevideo.com | GPU (small) |
|---|---|---|---|---|---|
| Já nas voltas 1/2 | 14 | — | — | — | — |
| **A pedir na FALA** | **32** | 29 019 s ≈ 8,1 h | 96 | 36 | ≈ 852 s ≈ 14 min |
| Não cabem no teto | 4 | 46 847 s ≈ 13 h | — | — | — |

Por canal, os 32: Koppert 7 (concorrente: voz técnica **comercial**), CRPV 6, L'Informatore Agrario 4,
Pianeta PSR 4, CONAF 3, Conserve Italia 3, Georgofili 1, Terra e Vita 1, AMAP 1, Prosecco DOC 1, ANBI 1.
Os melhores: webinars do CRPV (elaterídeos na batata, 56 min; damasco fitossanitário, 94 min; cimice
asiatica), a jornada «Sostenibilità e difesa delle colture» da CONAF (drones, prescrição de
fitofármacos), «Che ne sai tu di un campo di grano» (Georgofili, 43 min), o webinar ANBI sobre defesa
contra stress climático (57 min), o curso da Rete Rurale sobre fenologia do castanheiro (86 min).

## 3 · O custo de um vídeo (a regra, no código)

- **youtube.com: 3** pedidos (página, player, API interna) — medido pela bancada do freio.
- **googlevideo.com: 1 por fatia de 50 MB** (`--http-chunk-size 50M`). Áudio a 128 kbit/s ≈ 0,96 MB/min:
  até ~52 min = 1 fatia; até ~104 min = 2 fatias.
- **Teto:** os dois contam no MESMO balde (`googlevideo.com` → `youtube.com`), **5 por onda**. Até
  2 fatias cabe (5); 3 fatias = 6 **não cabe** → os 4 de 2,7–3,7 h ficam de fora. Com 160 kbit/s, mais
  2 (os de 86 e 94 min) passariam a não caber: **o pedido real é que diz**.
- **Limite de duração do baixador:** 540 s por omissão. Cada volta leva o seu
  `SINTONIA_YT_DURACAO_MAX_S` (o maior vídeo dela, arredondado ao minuto): até 5 700 s na F02.
- **GPU:** `faster-whisper small` a **34,07×** o tempo real na GTX 1080 (medido a 14/09 sobre 460,9 s de
  áudio real; CPU 4,84×). ⚠️ O texto da placa **não é igual** ao do processador (diferiu em 4 de 6
  peças); qual está certo **não foi medido**. `large-v3-turbo` está em cache e cabe (pico 3,2 GB de 8),
  mas a velocidade dele aqui **não foi medida**.

## 4 · O plano (depois do lote 3, das voltas 1 e 2; uma volta de cada vez)

`VOLTAS-FALA.txt` tem os 7 comandos prontos. Cada fonte aparece **uma** vez por volta (o maestro aceita
um vídeo por fonte por corrida); cada volta leva `SINTONIA_ASR_DEVICE=GPU` e o seu limite de duração.

| Volta | Vídeos | Áudio | Maior |
|---|---|---|---|
| F01 | 11 | 12 043 s | 3 403 s |
| F02 | 6 | 7 422 s | 5 634 s |
| F03 | 6 | 2 291 s | 1 070 s |
| F04 | 4 | 6 197 s | 5 175 s |
| F05 | 2 | 173 s | 134 s |
| F06 | 2 | 781 s | 692 s |
| F07 | 1 | 112 s | 112 s |

Antes de cada volta: portão de egresso IT. O maestro faz uma onda por vídeo (32 ondas no total), com o
freio antes do pedido e a prova-teto depois de cada onda.

⚠️ **O 429 do YouTube.** Os 125 registos de falha são exactamente isto: o coletor antigo pediu as
páginas dos 9 canais de pesquisa de uma vez (20/09) e levou `429`. A memória da casa mede-o por volta
de 120 páginas `/watch` seguidas. As 7 voltas somam 32 páginas: **uma volta por vez, com pausa entre
elas**, e parar à primeira resposta 429.

## 5 · Os 9 canais de pesquisa (125 vídeos sem título)

Não se escolhe o que não se vê. Para os ordenar, o mais barato é **1 pedido de metadados por lote de
50 vídeos à API oficial** (`videos.list`: 3 chamadas para os 125, 3 unidades de quota, **0**
`youtube.com`), pela fase `video-youtube` do Scrap — que precisa da chave (só no GitHub) e dos grupos
T5/T7 aceites no workflow (o P2 do CANAIS-41-RUNBOOK). Pedir as 125 páginas `/watch` repetiria o 429.
Além disso, estes 9 canais ainda estão na rota antiga do feed no vivo (`canais-pesquisa-v1` não
instalado).

## 6 · O que isto não prova

- Que a fala tem cultura + praga + região: os títulos só dizem que o assunto promete.
- O tamanho real do áudio (logo, 2 dos longos podem não caber) e o tempo real da placa nesta volta.
- A qualidade da transcrição (GPU ≠ CPU, sem referência).
