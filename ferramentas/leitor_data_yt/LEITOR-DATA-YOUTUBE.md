# LEITOR-DATA-YOUTUBE — a data de publicação que o YouTube escreve na página

Ramo `leitor-data-yt-v1`, a partir do vivo `83de0ccd`. **NÃO instalado.** Sem rede; Sala e RAW **não tocados**
(a medição usa as entradas da ACERVO-TEMPO-LUGAR, lidas antes da Sala por SELECT só-leitura, sha256 conferido).
Instalar = a ponta do ramo (o SHA de «PRONTO»).

## EM PALAVRAS SIMPLES

Cada página de vídeo do YouTube traz escrita, lá dentro, a data em que o vídeo foi publicado. Só que ela vem num
"cantinho" da página que o nosso leitor não olhava. Ensinei o leitor a olhar esse cantinho. Resultado, no material
que já temos guardado: **as coisas com data de publicação passam de 241 para 844** (de 1.158 fora da Sala). Nada do
que já tinha data mudou, e as outras três informações (onde fica a fonte, quando aconteceu o fato, onde aconteceu o
fato) ficaram **exatamente iguais**, dentro e fora da Sala. Conferi 20 vídeos um por um: nos 20, a data lida é a mesma
que o próprio YouTube mostra. A data de publicação **nunca** vira data do fato — um vídeo publicado no dia 17 sobre
algo que aconteceu no dia 13 continua com o fato no dia 13.

## 1 · O formato

Nas páginas `watch?v=…` guardadas no armazém:

```html
<meta itemprop="datePublished" content="2025-03-11T13:43:59-07:00">
<meta itemprop="uploadDate"    content="2025-03-11T13:43:59-07:00">
```

Medido nos 1.023 HTML com bytes do acervo (1.562 linhas de RAW, 1.246 conteúdos):

| | YouTube (612 páginas) | outros sites (411) |
|---|---|---|
| com `datePublished` | **603** | 27 (zootecnicainternational 22 · terraevita.edagricole 3 · protezionedellepiante 2) |
| com `uploadDate` | 603 — **sempre igual** ao `datePublished` | 2 |
| só `uploadDate` | **0** | 2 |
| forma | 603 com hora **e** fuso (ISO 8601) → precisão INSTANTE | 25 com fuso, 2 fora de ISO (não lidas) |

Nenhuma das 603 tinha a data em JSON-LD, `article:published_time` ou `<time>` — os três níveis que o leitor lia.

## 2 · O conserto

`coleta/executor_texto_de_html.tempo_de_publicacao` (o dono do PUBLISHED_AT da página):
- nível novo **3b**, `BASE_ITEMPROP = "meta itemprop datePublished"`, **depois do `<time>` e antes do índice**:
  `JSON-LD → meta article:published_time → <time> → meta itemprop datePublished → ÍNDICE`.
  Posto aí, só fala onde a D61 se calava: **nenhuma data já lida muda de valor nem de base** (medido: 0).
- as regras de sempre valem para ele: só ISO 8601; com hora e fuso = INSTANTE, só o dia = DIA; duas datas
  diferentes = AMBÍGUO, cala-se; o mesmo instante em dois fusos não é ambíguo.
- `uploadDate` **não** é lido: diz quando o ficheiro subiu, não quando foi publicado; e não acrescenta nada (acima).
- `admissao/reprocessar_tempo_lugar.CODIGO_DA_VERSAO` ganha `coleta/executor_texto_de_html.py`: o reprocessamento
  lê a página desde a DA-9, mas a versão que carimba cada revisão não incluía este ficheiro — um conserto nele sairia
  com o carimbo da versão antiga. Versão nova: `tempo-lugar@c43aa541…`.

A peça era da DA-6 (nuvem tempo-publicacao, inativa); o coordenador passou-a.

## 3 · Testes

| | resultado |
|---|---|
| `tests/test_leitor_data_youtube.py` (novo) | **10/10** — excerto real (IT-T7-015, raw 201; sha256 da página inteira conferido quando ela está na máquina), a ordem, «nada já lido muda», `uploadDate` não conta, ambíguo cala-se, prosa não se lê, só PUBLISHED_AT atravessa |
| `tests/test_tempo_e_lugar_da_publicacao.py` | **42/42** — o teste da ordem D61 passa a ter 5 níveis (comentado) |
| mutação (`mutar_leitor.py`) | **4/4 mortos**: sem o nível · o nível antes do `<time>` · `uploadDate` a contar · sem ambiguidade |
| os 25 ficheiros de teste de tempo/lugar, ramo × produção `83de0ccd` | **iguais por nome**; a única diferença é o teste novo; os vermelhos (`test_collection_gate` 1, o do mapa sem saída) já vêm da produção |
| `test_migracao_033_sala` · `test_tempo_e_lugar_atravessa` | 15/15 · 43/43 |

A amostra no Git é um **excerto**: só as 21 marcas `<meta itemprop>` da página (título, canal, contagens, datas,
países) — nada de texto de comentários. `.gitattributes`: `tests/dados/leitor-data-yt/** -text`.

## 4 · Antes → depois (só leitura; `ferramentas/leitor_data_yt/medida/`)

Mesmas entradas nos dois lados (`C:/Users/London1/reproc-acervo/`, sha256 em `entradas.sha256`: raw.json, derivados.json,
sala.json); 31 raízes de bytes; 177 livros do coletor. «Antes» = árvore `83de0ccd`; «depois» = este ramo.
**Conferência:** o meu «antes» dá exatamente os números da ACERVO (241/11/66/79 fora; 44/4/20/18 na Sala).

| | fora da Sala (1.158) antes → depois | Sala (88 conteúdos, 94 linhas) antes → depois |
|---|---|---|
| **data de publicação** | **241 → 844** (+603, todas pela base nova) | 44 → 44 |
| lugar da fonte | 11 → 11 | 4 → 4 |
| data do fato | 66 → 66 | 20 → 20 |
| lugar do fato | 79 → 79 | 18 → 18 |
| itens com outro dos 3 campos mudado | **0** | **0** |
| data de publicação já lida que mudou | **0** | **0** |
| data do fato calculada a partir da publicação (D63) | 0 → 0 | 2 → 2 |

⚠️ **O que muda sem mudar valor:** onde o PUBLISHED_AT continua `NAO SEI`, o texto do porquê (a BASE) passa a dizer
também `meta itemprop datePublished: ausente` — 108 conteúdos fora e **30 na Sala**. É texto de explicação, não
valor; num reprocessamento da Sala viraria 30 revisões de base (ver §6).

Grandes ficheiros fora do Git (sha256 em `medida/FORA-DO-GIT.sha256`): `C:/Users/London1/reproc-acervo/leitor-data-yt/antes.json`
(`bea3814f…`) e `depois.json` (`f8cd8d33…`). Para refazer: `bash ferramentas/leitor_data_yt/medir_antes_depois.sh 83de0ccd <ramo> <pasta>`
e `py ferramentas/leitor_data_yt/comparar.py <pasta> C:/Users/London1/reproc-acervo/previsao.json`.

## 5 · 20 lidos à mão (`medida/LIDOS-A-MAO-20.json`; 20 dos 603, sorteio com semente fixa)

| fonte | raw | lida | player (`publishDate`) | visível | título |
|---|---|---|---|---|---|
| IT-T5-037 | 410 | 2020-11-03T03:50:01-08:00 | igual | 3 nov 2020 | OT4CLIMA Contributo SPA Lab ISAFOM |
| IT-T2-027 | 383 | 2026-06-03T02:47:15-07:00 | igual | 3 giu 2026 | "L'aria in parole semplici": È migliorata l'aria in Lombardia |
| IT-T2-025 | 352 | 2024-12-13T00:49:16-08:00 | igual | 13 dic 2024 | Seminario ARPA Lazio - ANCI Lazio su materiali da scavo |
| IT-T12-016 | 1070 | 2024-01-31T06:21:44-08:00 | igual | 31 gen 2024 | Cosa posso fare per te? Intervista a Luca |
| IT-T7-030 | 703 | 2025-04-01T05:55:35-07:00 | igual | 1 apr 2025 | Zucchero Biologico 100% italiano |
| IT-T12-010 | 987 | 2020-12-24T01:43:18-08:00 | igual | 24 dic 2020 | Natale 2020, il messaggio del presidente Toma |
| IT-T7-026 | 658 | 2026-05-18T09:55:47-07:00 | igual | 18 mag 2026 | Una professione dai molti percorsi |
| IT-T2-026 | 372 | 2024-03-19T03:09:54-07:00 | igual | 19 mar 2024 | Le polveri sottili o particolato atmosferico |
| IT-T7-020 | 586 | 2024-09-17T03:11:07-07:00 | igual | 17 set 2024 | 140esimo Panperduto e Canale Villoresi, **13 settembre** 2024 |
| IT-T8-006 | 849 | 2026-04-02T03:34:46-07:00 | igual | 2 apr 2026 | Vite a Guyot: potatura invernale |
| IT-T12-008 | 977 | 2026-05-04T06:04:10-07:00 | igual | 4 mag 2026 | La Comunità del Mare: Intervista a Emidio Del Zompo |
| IT-T7-032 | 721 | 2025-07-30T07:37:12-07:00 | igual | 30 lug 2025 | FEST 1920X1080 |
| IT-T7-030 | 700 | 2026-04-16T01:55:41-07:00 | igual | 16 apr 2026 | Intervista a Maria Grazia Mammuccini (FederBio) |
| IT-T7-022 | 600 | 2026-06-25T02:04:18-07:00 | igual | 25 giu 2026 | Grana Padano Love · Corsa DE |
| IT-T9-017 | 887 | 2025-09-07T15:00:37-07:00 | igual | 7 set 2025 | Original Story Jose Belda · Koppert |
| IT-T2-027 | 389 | 2026-05-05T05:50:50-07:00 | igual | 5 mag 2026 | L'aria in parole semplici: le cause dell'inquinamento |
| IT-T7-037 | 786 | 2018-07-06T07:38:15-07:00 | igual | 6 lug 2018 | Consorzio Valpolicella · Conferenza Stampa **4 lug** |
| IT-T12-012 | 1026 | 2026-07-27T23:40:44-07:00 | igual | 27 lug 2026 | SRE01 - Modulo 3: Ricavi, Costi e Margine |
| IT-T7-027 | 674 | 2026-07-21T11:10:45-07:00 | igual | 21 lug 2026 | GRANO · il punto della situazione |
| IT-T12-016 | 1063 | 2024-11-27T01:31:41-08:00 | igual | 27 nov 2024 | Cooperattiva · la società cooperativa |

**20/20** batem com o player e com a data visível; **20/20** com a data do fato igual à de antes. Dois mostram por que
publicação ≠ fato: o Panperduto de **13/9** publicado a **17/9**; a conferência de imprensa de **4/7** publicada a **6/7**.

⚠️ **Ressalva (não é regressão hoje):** o YouTube escreve a hora no fuso da Califórnia (`-07:00`/`-08:00`). O valor
fica como INSTANTE, certo. Mas `leis/fato_do_texto.publicacao_provada` usa só o **dia escrito** para ancorar
«ieri/oggi» (D63) e para descartar a data do texto igual à publicação — um vídeo das 23:40 na Califórnia (IT-T12-012)
já é o dia seguinte na Itália. Medido hoje: 0 datas do fato calculadas mudaram. Fica para o dono do leitor do fato.

## 6 · Plano de instalação e de reprocessamento (executa: o coordenador; um escritor)

```bash
VIVO=/c/Users/London1/orca/workspaces/eame-sintonia/source-curator-service-v1
RAMO=<SHA de PRONTO = ponta de origin/leitor-data-yt-v1>
D=$(date +%Y%m%d-%H%M); CORTE=/c/cutover/leitor-data-yt-$D; mkdir -p $CORTE
LIVROS=$(git -C $VIVO --no-optional-locks status --short | grep '^ M' | awk '{print $2}' | tr '\n' ' ')
```

1. **Parar o robô** — `PARAR.flag`; 0 processos `supervisor|worker|ponte_automatica|observador`. ⏱️
2. **Ponto de partida** — `git -C $VIVO rev-parse --short HEAD` = **83de0ccd** (senão PARAR).
3. **Backup** — livros sujos para `$CORTE` + `SHA256-ANTES.txt` + `HEAD-ANTES.txt`.
4. **O ramo não toca livros** — `git -C $VIVO fetch origin leitor-data-yt-v1 && git -C $VIVO diff --name-only HEAD $RAMO -- $LIVROS | wc -l` → **0**.
5. **Merge** — `git -C $VIVO merge --ff-only $RAMO`.
6. **Livros iguais** — `sha256sum` = `SHA256-ANTES.txt`.
7. **A amostra sem conversão de linha** — `git -C $VIVO check-attr text tests/dados/leitor-data-yt/it-t7-015-raw201-itemprop.html` → `unset`.
8. **Testes** — `py -B tests/test_leitor_data_youtube.py` (10) · `py -B tests/test_tempo_e_lugar_da_publicacao.py` (42) ·
   `py -B tests/test_tempo_e_lugar_atravessa.py` (43) · `py -B tests/test_migracao_033_sala.py` (15).
9. **Mapa** — com a LOCK-PESADO: `py system-map/scripts/correr_a_cadeia.py VALIDAR` → PASS.
10. **Push** — `git -C $VIVO push origin HEAD:servico-20260923-0923`.
11. **Religar o robô** — `rm PARAR.flag`. ⏱️ **Daqui em diante, toda página do YouTube coletada já sai com PUBLISHED_AT** (o executor corre na coleta).
12. **Sala (reprocessamento) — conferir, não aplicar por omissão** —
    `py admissao/reprocessar_tempo_lugar.py --livros "<glob>" --raizes "<raizes>" --saida $CORTE/reproc-sala.json` (sem `--aplicar`)
    → esperado **pela previsão do §4** (a ferramenta de reprocessamento NÃO foi corrida contra a Sala nesta missão):
    0 valores novos nos 4 campos; só 30 bases de `NAO SEI` com o texto novo. Aplicar (`--aplicar`) grava
    essas 30 revisões de base, com o carimbo da versão nova — **decisão do coordenador**; não muda nenhum valor.
13. **Acervo fora da Sala (os 603)** — o derivado novo TEMPO_LUGAR (RAW intocado) depende da **034** proposta pela
    ACERVO-TEMPO-LUGAR e do escritor dos derivados, que **ainda não existem** (decisão do dono). Quando existirem, a entrada
    é a previsão já medida aqui (`depois.json`, sha256 acima) refeita com o código instalado.

**DESFAZER**: `PARAR.flag` → `git -C $VIVO reset --keep $(cat $CORTE/HEAD-ANTES.txt)` → repor os livros de `$CORTE` → conferir
`SHA256-ANTES.txt` → religar. Se o passo 12 aplicou revisões: elas ficam (a Sala é append-only por revisão); o
valor de cada campo não mudou. Se já houve push: não forçar; o coordenador decide.
