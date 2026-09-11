# CENSO DOS ACTORS · E O CUSTO, NAS TRÊS PALAVRAS DA LEI

> **MEDIDO_EM:** 2026-09-11, a partir das fontes primárias do repositório.
> **FONTES:** `data/samples/SENSOR-PILOT/RUNS-{A,B,C,D,E}.json` · `data/samples/RUN-MANIFEST.json`
> **MÉTODO:** soma programática, não leitura de prosa. Cada número abaixo é reproduzível.

---

## A DISTINÇÃO QUE FECHA O CENSO

```
CITADO NO CÓDIGO   ≠   EXECUTADO   ≠   AINDA NECESSÁRIO
```

| medida | valor |
|---|---|
| actors **citados** no código (HEAD e ponta SCRAP, idêntico) | **13** |
| actors com **execução registada** em artefato | **8** |
| citados **e** executados | **7** |
| **executados mas NÃO citados** — órfão de execução | **1** |
| citados e **nunca** executados | **6** |
| universo real | **14** |

### O órfão

`instagram-hashtag-scraper` correu **1 vez**, trouxe **60 itens**, e **não é citado em
nenhum ficheiro do repositório**. Alguém o correu e o código já não sabe que ele existe.

### Os seis que nunca correram

```
apify~facebook-posts-scraper          apify~instagram-scraper
apify~instagram-profile-scraper       scrapesmith~instagram-comments-scraper
apify~instagram-reel-scraper          starvibe~youtube-video-transcript
```

> Nenhum destes seis pode ser «aposentado com economia»: **nunca gastaram nada.**
> Aposentá-los é higiene de código, não poupança.

---

## O CUSTO, NAS TRÊS PALAVRAS DE `COL-LAW-019`

A lei diz que `0`, `NÃO SEI` e `NOT_PRESERVED` **não se misturam**. Contadas:

| palavra | significado na lei | runs |
|---|---|---|
| **medido** (`0` ou valor) | gastou, e registou | US$ **12,8140** |
| `0` medido | não gastou | 55 runs |
| **`NOT_PRESERVED`** | **confissão: gastou e não guardou** | **25 runs** |
| `NÃO SEI` | não medido | 0 runs |

```
O TOTAL REAL É ≥ US$ 12,81. QUANTO PASSA DISSO É «NÃO SEI», E A LEI OBRIGA A
DIZÊ-LO ASSIM — não a arredondar para 12,81 nem a estimar.
```

Dos 25 `NOT_PRESERVED`, **19 são do mesmo actor**: `pintostudio~youtube-transcript-scraper`.

> **Correção a mim próprio.** No relatório interino escrevi «US$ 12,81» como o gasto
> histórico. Está incompleto: é o **piso medido**. Um agente contestou o número dizendo que
> só existia em prosa de docstring — **isso estava errado**, os valores são floats legíveis
> por máquina em `SENSOR-PILOT/RUNS-*.json` (ex.: `streamers~youtube-comments-scraper`, run
> `SENSOR-CM-E-0-p1`, `COST_USD = 1.9`, 887 itens, 2026-09-02). Mas a contestação fez
> aparecer os 25 `NOT_PRESERVED`, que eu não tinha contado. O número certo é **≥ 12,81**.

---

## O LIVRO DOS OITO QUE CORRERAM

Estados reais do artefato: `SUCCESS` · `PARTIAL` · `FAILED` (58 · 22 · 19 no total).

| actor | runs | US$ medido | `NOT_PRESERVED` | itens | SUCCESS | PARTIAL | FAILED |
|---|---|---|---|---|---|---|---|
| `streamers~youtube-comments-scraper` | 11 | **7,7280** | 1 | 4.083 | 7 | 3 | 0 |
| `streamers~youtube-scraper` | 30 | **4,4720** | 1 | 1.425 | 12 | **17** | 0 |
| `harvestapi~linkedin-profile-scraper` | 1 | 0,4840 | 0 | 120 | 1 | 0 | 0 |
| `pintostudio~youtube-transcript-scraper` | 49 | 0,1300 | **20** | 48 | 28 | 1 | **19** |
| `harvestapi~linkedin-profile-search-by-name` | 12 | 0 | 0 | 44 | 11 | 1 | 0 |
| `harvestapi~linkedin-post-search` | 1 | 0 | 1 | 472 | 1 | 0 | 0 |
| `harvestapi~linkedin-profile-search` | 3 | 0 | 1 | 106 | 1 | 2 | 0 |
| `instagram-hashtag-scraper` (órfão) | 1 | 0 | 1 | 60 | 1 | 0 | 0 |

### O que estes números dizem, e não é só preço

```
96,2% DO GASTO MEDIDO É YOUTUBE — e é também onde a fiabilidade é pior.
```

- `streamers~youtube-scraper`: **17 de 29 runs saíram `PARTIAL`** (59%). Pagou-se 4,47 por
  uma rota que devolve incompleto na maioria das corridas.
- `pintostudio~youtube-transcript-scraper`: **19 de 48 `FAILED`** (40%), 48 itens ao todo, e
  **20 runs que gastaram sem registar quanto**. É o actor com pior relação de tudo:
  mais corridas que qualquer outro, quase nenhum produto, e o custo por medir.

> Um actor com 40% de falha e o custo por registar não é uma dependência: é uma dívida.

### E há um defeito de proveniência por baixo

`STARTED_AT` também vem `NOT_PRESERVED` em vários registos. Não é só o custo que não foi
guardado — **é a hora**. Um run sem hora e sem custo não se audita, não se repete e não se
cobra. `COL-LAW-019` chama a isto confissão, e é a palavra certa.

---

## YOUTUBE — O QUE OS ACTORS VENDEM, E O QUE JÁ FOI OBTIDO DE GRAÇA HOJE

As quatro capacidades que os quatro actors de YouTube vendem foram todas obtidas hoje
neste contentor, sem login, sem cookies e sem Apify:

| capacidade | actor que a vende | rota grátis provada hoje | estado |
|---|---|---|---|
| discovery de canal | `streamers~youtube-scraper` | `yt-dlp --flat-playlist` com `player_client=android` | **PROVEN** |
| discovery por busca | `streamers~youtube-scraper` | `yt-dlp ytsearch` · API `search.list` | **PROVEN** |
| metadados / métricas | `streamers~youtube-scraper` | `yt-dlp --print` · API `videos.list` (1 unidade) | **PROVEN** |
| comentários com thread | `streamers~youtube-comments-scraper` | `yt-dlp --write-comments` · API `commentThreads` | **PROVEN** |
| legenda manual | `pintostudio~*` / `starvibe~*` | `yt-dlp --write-subs` | **PROVEN** |
| legenda automática | `pintostudio~*` / `starvibe~*` | `yt-dlp --write-auto-subs` | **PROVEN** |
| bytes de mídia | — | `yt-dlp -f bestaudio` | **BLOCKED** (403 deste IP) |
| legenda pela API oficial | — | `captions.download` | **BLOCKED** (exige ser dono do vídeo) |

### A qualidade paga é pior que a grátis, e está medido

O artefato pago `data/samples/raw-paid/ES-T8-001-youtube-transcripts.raw.json.gz` tem
**20 itens, dos quais 5 vieram com transcript vazio** — 25% de falha, paga. A rota
`yt-dlp --write-auto-subs` devolveu VTT não vazio nos dois vídeos testados hoje.

---

## ZERO APIFY — A MATRIZ POR CAPACIDADE, NÃO POR PLATAFORMA

Uma coluna só mentiria. São cinco.

| capacidade | `ZERO_APIFY_TECH` | `ZERO_PAID_EXT` | `ZERO_BROWSER` | `ZERO_LOGIN` | `PRODUCTION_READY` |
|---|---|---|---|---|---|
| YouTube · discovery de canal | **YES** | YES | YES | YES | **REQUIRES_REVIEW** |
| YouTube · busca | **YES** | YES | YES | YES | **REQUIRES_REVIEW** |
| YouTube · metadados | **YES** | YES | YES | YES | REQUIRES_REVIEW |
| YouTube · comentários | **YES** | YES | YES | YES | REQUIRES_REVIEW |
| YouTube · legendas | **YES** | YES | YES | YES | REQUIRES_REVIEW |
| YouTube · bytes de mídia | **NO** (403) | NO | UNKNOWN | UNKNOWN | NO |
| LinkedIn · discovery recente | **YES** | YES | YES | YES | **REQUIRES_REVIEW** |
| LinkedIn · discovery histórico | **UNKNOWN** | UNKNOWN | UNKNOWN | UNKNOWN | NO |
| LinkedIn · post direto | **YES** | YES | YES | YES | REQUIRES_REVIEW |
| LinkedIn · vídeo nativo | **YES** | YES | YES | YES | REQUIRES_REVIEW |
| LinkedIn · legenda nativa | **YES** | YES | YES | YES | REQUIRES_REVIEW |
| Instagram · captura de Reel direto | **YES** | YES | YES | YES | **PARTIAL** (retry ~1 em 6) |
| Instagram · discovery de perfil | **PARTIAL** | PARTIAL | NO neste IP | YES | **NO** |
| Instagram · Stories | **UNKNOWN** | UNKNOWN | NO | **NO** | NO |
| Instagram · comentários | **NO** | NO | UNKNOWN | UNKNOWN | NO |

> `REQUIRES_REVIEW` em quase toda a coluna de produção **não é hesitação**: é o eixo de
> política, que nenhuma medição técnica resolve. Ver `AQ` em `ESTADO-REAL-V1.md`.

### Por que o zero-Apify do YouTube ainda não está liberado

Tecnicamente as quatro capacidades estão cobertas. O que falta **não é capacidade**:

1. `leis/social_matriz.py` classifica a rota, e a classificação de `yt-dlp` **não existe lá**.
2. O `robots.txt` do YouTube barra `/youtubei/`, `/results`, `/comment` e `/get_video` —
   exatamente os endpoints por onde `yt-dlp` passa. É `ROBOTS_STATUS = RESTRICTED`,
   **não** um parecer jurídico.
3. A API oficial é a única rota que o próprio repo classifica como `PERMITIDA`, e ela
   **não** cobre legendas (`captions.download` exige ser dono do vídeo).

```
O YOUTUBE É, AO MESMO TEMPO, O MAIOR GASTO (96,2%), A PIOR FIABILIDADE PAGA
(17 PARTIAL em 29, 19 FAILED em 48) E O ÚNICO ROBOTS.TXT QUE NÃO É BLOQUEIO
TOTAL. É onde a decisão vale mais e custa menos para tomar.
```

**Não implementado. Nenhum actor foi desligado nesta missão.**
