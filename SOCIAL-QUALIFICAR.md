# SOCIAL-QUALIFICAR — números para as contas da micro social, pedidos do yt-dlp medidos, lote e instalação (25-26/09)

Ramo `social-qualificar-v1`, a partir de `social-micro-v1` @ 6fb36898 (que já parte do vivo `ce28040c`).
**Rede FECHADA** em tudo o que correu (`HTTP(S)_PROXY=127.0.0.1:9`); o único acesso à rede foi o `git push`.
Nada no vivo (só leitura: `git status --no-optional-locks` e cópia dos livros), nada na Sala, nada instalado.

## 1 · O caminho canónico, e porque NÃO é o `onboardar_rotas_provadas.py`

O «ENTRA=16» da onda3 é `curadoria/onboardar_rotas_provadas.py`: põe na tabela do COLETOR WEB
(`regras/italy_contracts_onboarded.json`) as fontes que o portão diz ELIGIBLE **e** que o canário WEB provou
(`ROTAS-ELEGIVEIS-V1.json`, ROUTE_PROVEN). Corrido na cópia, só a mostrar: **ENTRA=0 FICA=9**, e nenhuma das 18
contas sociais aparece — ele nem as vê, porque não são ELIGIBLE (`provas/social-qualificar/ONBOARDING-WEB-MOSTRAR.txt`).

O caminho canónico **das contas sociais** é o do robô de fontes, degrau a degrau, igual ao da web até ao canário:

`semear QUALIFY` → **QUALIFY** (número pelo registo de alocação) → **BUILD_CONTRACT** (contrato do Curator, com o
lugar pelo site oficial) → **VALIDATE_ROUTE** (a rota do Scrap na matriz dele) → `CANARY_PENDING`.

Aí o robô **para por desenho** (`curadoria/worker.py`, ramo VALIDATE_ROUTE): «a rota do Scrap para aqui: o canário
dela não é do Curator». O canário social É a micro (uma colheita do Scrap pedida pelo orquestrador), e a promoção a
READY é da régua social (`curadoria/regua_social.py --vivo`). **Consequência para a instalação:** semear no vivo
não põe o bot a ir à rede por estas contas.

## 2 · Contas e canais, com o número PROPOSTO

Ensaio na cópia `C:/ens-sq` (6fb36898 + os 16 livros sujos do vivo copiados às 23:43, cada JSON conferido inteiro),
fila FILTRADA ao lote (`curadoria/ensaio_so_linkedin.py`, que rebenta se aparecer tarefa com rede). Semeado com a
opção nova `--candidatas` (ver §5).

⚠️ **O número é PROPOSTO, não reservado.** O registo cunha `max+1` por território no instante do QUALIFY. Se o vivo
cunhar outros antes da instalação, os números andam. Os definitivos lêem-se no livro vivo depois (passo 5 do plano).

### LinkedIn — 9/9 com número e contrato, todas `CANARY_PENDING`

| candidata | conta | SOURCE_ID proposto | lugar da fonte (precisão) | porquê do território |
|---|---|---|---|---|
| CAND-0118 | `ispra_2` (ISPRA) | IT-T5-190 | ITALY (COUNTRY) | «Istituto» → T5 |
| CAND-0133 | `arpa-valle-d-aosta` | IT-T2-165 | ITALY (COUNTRY) | «ARPA» → T2 |
| CAND-0112 | `cia-agricoltori-italiani` | IT-T7-253 | ITALY (COUNTRY) | «CIA» → T7 |
| CAND-0103 | `consorzio-tutela-grana-padano` | IT-T7-254 | ITALY (COUNTRY) | «Consorzio» → T7 |
| CAND-0094 | `gruppocaviro` (Caviro) | IT-T9-025 | **NÃO SEI** (NAO DECLARADA) | «gruppo» → T9 |
| CAND-0114 | `certisbelchim-italia` | IT-T9-026 | ITALY (COUNTRY) | «Italia» → T9 |
| CAND-0119 | `italmopa` | IT-T7-255 | ITALY (COUNTRY) | «Associazione» → T7 |
| CAND-0097 | `macfrut-fiera` (Macfrut) | IT-T11-014 | **NÃO SEI** (NAO DECLARADA) | «Macfrut» → T11 |
| CAND-0105 | `dipartimento-di-scienze-agrarie-ambientali` (UNIMI DiSAA) | IT-T5-191 | ITALY (COUNTRY) | «Dipartimento» → T5 |

Rota no contrato: fase `video-linkedin`, `pagina` = a página da empresa, **`teto: 2`** (ver lote, §4).

### YouTube — 12 pedidos: 9 números novos, 1 repetido, 2 recusados

| candidata | canal (site oficial que aponta) | SOURCE_ID proposto | lugar da fonte (precisão) |
|---|---|---|---|
| CAND-0190 | Cifo `UC4A5UdkaIvcbaA7z1mz-YdA` (cifo.it) | IT-T9-027 | ITALY (COUNTRY) |
| CAND-0219 | Olio Officina `UCXUG407gp3CnWnfS3ycijhA` (olioofficina.it) | IT-T5-192 | ITALY (COUNTRY) |
| CAND-0469 | ARPAT `UCLgMADPaG6fhrykcnxOQgAg` | IT-T2-166 | ITALY (COUNTRY) |
| CAND-0335 | `UCCMlh614oidOkq-HNSa9RVA` (arpae.it) | IT-T2-167 | Bologna (PROVINCE) |
| CAND-0332 | o MESMO canal da CAND-0335 | **nenhum novo** — «o canal já é IT-T2-167» | — |
| CAND-0423 | `UCJ8RdeFgPyGA8eyVHulEiOg` (crea.gov.it) | IT-T5-193 | Roma (PROVINCE) |
| CAND-0289 | Regione Lombardia `UCk532NeXL1DMlQH3z50N0jg` | IT-T12-152 | **NÃO SEI** |
| CAND-0377 | Regione Campania `UCfhOFwAOCiAhiftm4ipqEHg` | IT-T12-153 | **NÃO SEI** |
| CAND-0873 | `UC5eILrioLv2z6RHTzwYO7cA` (emiliaromagna.cia.it) | IT-T7-256 | **NÃO SEI** |
| CAND-0877 | `UCQWIF1XMefEjq2nj30TiPSQ` (emiliaromagna.cia.it) | IT-T7-257 | **NÃO SEI** |
| CAND-0221 | Società Entomologica Italiana | **RECUSADA** — território indeterminado pelo nome; «SOURCE_ID fica UNKNOWN, sem fabricar; precisa de decisão semântica» | — |
| CAND-0300 | «Canal YOUTUBE em youtube.com» | **RECUSADA** — mesmo motivo | — |

«NÃO SEI» no lugar = o site oficial não tem sede no cadastro-mestre nem ficha com país no Atlas
(`leis/lugar_da_organizacao.py`); **não se preencheu à mão.** As duas recusas e os lugares NÃO SEI esperam decisão
do dono, não do código.

Rota no contrato: fase `canal-youtube` (`canal_id`). Para a micro, a colheita é `audio-youtube` de um vídeo (a D36
aceita as duas fases como equivalentes). ⚠️ **Buraco que continua:** o `VIDEO_ID` sai da `canal-youtube`, cuja chave
só existe no GitHub Actions; na micro o vídeo é escolhido por quem corre e fica escrito no pedido.

Provas: `provas/social-qualificar/ENSAIO-QUALIFY-LINKEDIN.json`, `ENSAIO-QUALIFY-YOUTUBE.json`.

## 3 · Pedidos por vídeo do yt-dlp — MEDIDOS, sem rede

`provas/social-qualificar/medir_yt_dlp_offline.py`: um intermediário local recebe TODO o tráfego do yt-dlp (termina
o TLS com certificado próprio) e responde como youtube.com e googlevideo.com. **Nunca repassa nada.** O yt-dlp corre
com os mesmos argumentos de `ferramentas/youtube_transcrever._audio`. Conta-se dos dois lados; **o servidor e o
`--print-traffic` (a leitura que o Scrap usa) bateram em 5 de 5 casos.**

Máquina: yt-dlp **2026.08.19**, **sem deno** → o yt-dlp usa um só cliente (`visionos`).

| caso | youtube.com | googlevideo.com | **total D41** |
|---|---|---|---|
| áudio de 3 MiB (~3 min) | 3 | 1 | **4** |
| áudio de 10 MiB | 3 | 2 | **5** |
| áudio de 25 MiB (~25 min) | 3 | 3 | **6 — passa o teto** |
| 25 MiB com `--extractor-args youtube:player_skip=webpage` | 2 | 3 | 5 |
| 25 MiB com `--http-chunk-size 50M` | 3 | 1 | 4 |

Os 3 do youtube.com são: a página `/watch`, o ficheiro do player (`/s/player/…/base.js`) e a API
`/youtubei/v1/player` (cliente VISIONOS). O googlevideo.com leva **1 pedido por fatia de ~10 MiB** (o yt-dlp corta
em 10 MiB com um pouco de sorteio para baixo: a 1.ª fatia medida foi de 9,7 MiB). Regra:
**pedidos = 3 + arredondar-para-cima(tamanho do áudio ÷ ~9,7 MiB).** Áudio de ~1 MiB por minuto → até ~9 min = 4.

⚠️ **O que esta medida NÃO cobre (é o MÍNIMO, não o máximo):** as respostas são sintéticas. O YouTube real pode
acrescentar pedidos que um servidor bem-comportado não provoca — **403 no stream com novas tentativas (o yt-dlp
tenta de novo até 10 vezes por omissão)**, PO token, redireccionamento. Uma primeira versão do servidor, que
respondia 404 à API `/next`, fez o yt-dlp repetir 4 vezes: **um erro vira pedidos a mais.** E se alguém instalar o
deno, o yt-dlp passa a usar 2 clientes (`visionos` + `web`) e o número muda — tem de se medir outra vez.

## 4 · LOTE FINAL (o que cabe em 5 por domínio por onda)

- **YouTube: 1 canal por onda, 1 vídeo de até ~9 min** → 4 pedidos (folga de 1). Entre 10 e 19 min = 5 (sem
  folga); 20 min ou mais = 6 ou mais (**não cabe**). Ordem: IT-T9-027 Cifo, IT-T5-192 Olio Officina, IT-T2-166
  ARPAT, IT-T2-167 (arpae.it), IT-T5-193 (crea.gov.it); depois os 4 com lugar NÃO SEI.
  Propostas para ganhar folga (**não feitas** — mexem no `youtube_transcrever.py`, que é do Scrap):
  `--http-chunk-size 50M` (qualquer áudio até 50 MiB = 4), `--retries 0 --fragment-retries 0` (um 403 não vira
  10 pedidos), `--match-filter "duration<=540"` (vídeo longo não chega a descarregar).
- **LinkedIn: 2 contas por onda, com `teto=1` no pedido.** ⚠️ Achado: o contrato escreve `teto: 2`, e o plano da
  onda social copia o teto do contrato. Com teto 2, cada conta pede ao linkedin.com 1 página da empresa + 2 páginas
  de post = 3; **duas contas = 6, passam o teto.** Com `teto=1`: 2 por conta, 4 por onda (folga de 1); licdn.com
  2 a 4. Estes números do LinkedIn são LIDOS NO CÓDIGO (`coleta/adaptador_linkedin.video_da_pagina_publica`), **não
  medidos**; a 1.ª onda mede. Alternativa sem mexer no pedido: 1 conta por onda com teto 2 (3 pedidos).
  Ondas: L1 IT-T5-190 ISPRA + IT-T2-165 ARPA VdA · L2 IT-T7-253 CIA + IT-T7-254 Grana Padano · L3 IT-T9-025 Caviro +
  IT-T9-026 Certis Belchim · L4 IT-T7-255 Italmopa + IT-T11-014 Macfrut · L5 IT-T5-191 UNIMI DiSAA.
- **Prova-teto a seguir a cada onda** (`provas/prova_teto_dominio.py` sobre o `runs.ndjson`). FAIL ou NAO_SEI → parar.

## 5 · O que mudou no código

- `curadoria/semear_qualify_social.py --candidatas CAND-a,CAND-b`: semeia **só** o lote. Sem ele entram todas as
  elegíveis: **40 LinkedIn e 64 YouTube** no livro de 23:43, e há canais que já são fonte no vivo por outro endereço
  (ex.: o canal do ISPRA já é IT-T5-045). Pedida e não elegível → não entra, e diz-se qual.
  Teste `tests/test_semear_so_as_candidatas.py` (4); sem o filtro, 3 dos 4 caem (mutação à mão).
- Suítes sociais: 63 testes OK (`curadoria.test_regua_social`, `curadoria.test_soc_onda2_social`,
  `tests.test_prova_teto_social`, `tests.test_social_bruto_leva_a_evidencia`, `tests.test_semear_so_as_candidatas`).

## 6 · PLANO DE INSTALAÇÃO ÚNICO (social-micro + qualificar) — para o coordenador

⚠️ **SUBSTITUÍDO (26/09 02:08):** o vivo passou a `83de0ccd` (C9). A ordem que vale é a do
`PLANO-INSTALACAO-SOCIAL.md` (ramo `social-qualificar-v2`, ff-only sobre `83de0ccd`, com a legacy-99-v5). O texto
abaixo fica como estava, medido sobre `ce28040c`.

Medido: `ce28040c` é antepassado de `social-qualificar-v1`, e os 39 ficheiros que o pacote muda **não incluem
nenhum** dos 16 livros sujos do vivo → **`--ff-only` serve**, sem tocar no que o bot está a escrever.

1. `touch curadoria/PARAR.flag` no vivo e esperar a volta do bot acabar.
2. `git fetch origin && git merge --ff-only origin/social-qualificar-v1` (traz a PROVA-TETO-SOCIAL, o conserto da
   precisão na Sala, o filtro `--candidatas` e as provas). Se o vivo já não estiver em `ce28040c`, **parar** e refazer
   o ff sobre o novo HEAD (não forçar).
3. Mostrar primeiro, sem `--aplicar`:
   `py curadoria/semear_qualify_social.py --candidatas CAND-0118,CAND-0133,CAND-0112,CAND-0103,CAND-0094,CAND-0114,CAND-0119,CAND-0097,CAND-0105`
   `py curadoria/semear_qualify_social.py --tipo YOUTUBE --candidatas CAND-0190,CAND-0219,CAND-0469,CAND-0335,CAND-0423,CAND-0289,CAND-0377,CAND-0873,CAND-0877`
   (sem as 2 recusadas e sem a 0332 repetida). Conferir 9 + 9 e nenhuma «NAO ELEGIVEIS».
4. Repetir os dois com `--aplicar --vivo`. Tirar o `PARAR.flag`. O bot faz QUALIFY → contrato → rota e **para em
   CANARY_PENDING** (sem rede para estas contas).
5. Ler no livro vivo (`curadoria/SOURCE-ID-ALLOCATION-V1.json`, por `CANDIDATE_ID`) os números que ficaram — podem
   não ser os propostos — e escrever com eles a fila filtrada da micro.
6. A micro (missão própria, rede autorizada): lote do §4, prova-teto a cada onda.
7. Depois dos canários: `py curadoria/regua_social.py --corridas <resultados.json> --aplicar --vivo`, com o bot
   parado, para READY_FOR_COLLECTION.

Desfazer os passos 3-4: o semear só abre tarefas QUALIFY; enquanto o bot estiver parado, é repor os livros da
fotografia tirada no passo 1.

## 7 · MAPA

A cadeia do mapa corre DEPOIS deste ficheiro estar escrito, com LOCK-PESADO, e o resultado é o commit dela
(«mapa: regerado pela cadeia (SOC-QUALIFICAR)») logo a seguir a este. Não se escreve aqui: mudar este ficheiro
depois mudaria o carimbo do mapa (foi o que me aconteceu na SOCIAL-MICRO-PREP). O veredito vai no relatório final.

## 8 · PROVAS FORA DO GIT

| caminho | o que é |
|---|---|
| `C:/ens-sq` (worktree, detached 6fb36898 + 16 livros do vivo às 23:43) | a cópia do ensaio; sha256 (12 primeiros) dos livros copiados: FONTES-CANDIDATAS 772b55647a02 · SOURCE-ID-ALLOCATION a993f8bf7cb6 · italy_contracts_curator 85c1b635ae28 · LIFECYCLE-QUEUE e0ec73fd3ada |

## EM PALAVRAS SIMPLES

- **As contas ganharam "número de fonte" num ensaio.** Numa cópia do robô, com a internet desligada, as 9 contas do
  LinkedIn e 9 canais do YouTube ganharam número e contrato. É como tirar CPF: agora cada uma tem identidade. Mas
  o número é **proposto** — no dia de instalar pode sair outro, se o robô de verdade der números a outras antes.
- **Onde não havia prova, ficou "NÃO SEI".** Em 6 contas o robô não achou onde fica a empresa e não inventou.
  2 canais foram recusados porque nem o assunto deu para saber pelo nome. Esses esperam uma decisão sua.
- **Contei quantos pedidos o YouTube custa, sem internet.** Montei um "YouTube de mentira" dentro do computador.
  Cada vídeo custa **3 pedidos + 1 para cada ~10 MB de som**. Vídeo curto (até ~9 min) = 4 pedidos, cabe no limite
  de 5. Vídeo de 25 minutos = 6, **não cabe**. O YouTube de verdade pode pedir mais se der erro — o número medido
  é o mínimo.
- **Achei uma armadilha no LinkedIn.** O contrato manda pegar até 2 vídeos por conta. Com 2 contas por rodada isso
  dá 6 pedidos ao LinkedIn — passa do limite. Na micro, o pedido tem de dizer "só 1 vídeo por conta".
- **Instalar é simples e seguro:** o pacote encaixa direto em cima do que está rodando, sem mexer nos cadernos
  que o robô está escrevendo. E o robô não sai à internet por causa dessas contas: ele para e espera a micro.
- **Nada foi instalado, nada foi coletado, a Sala não foi tocada.**
