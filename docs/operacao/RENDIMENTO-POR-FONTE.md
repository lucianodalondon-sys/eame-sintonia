# RENDIMENTO-POR-FONTE — o que a coleta traz que a Intelligence consegue cruzar

> Ramo `rendimento-fonte-v1` (a partir do vivo `69b0e23f`), **só documento e registos — nenhum código do
> sistema**. Missão: `auditoria-madrugada/missao-rendimento-por-fonte.txt`. Só leitura (Sala com
> `default_transaction_read_only=on`, armazém, livros), sem rede, sem coleta, nenhum Postgres ligado,
> nada instalado. Cópia deste ficheiro em `auditoria-madrugada/RENDIMENTO-POR-FONTE.md`.

## Resposta curta

- **Base:** os **1.246 documentos** guardados (sha256 distintos do bruto: 88 na Sala + 1.158 fora), lidos
  pela estrada do reprocesso com o extractor MAIS NOVO — o de `periodo-chaves-v1` @ `71d40788`
  (período, região sem nomes de órgão/empresa, cultura fora de T1). Ainda não instalado: é o melhor que
  o código sabe hoje.
- **Com as 3 chaves (FACT_TIME com ano + região + cultura): 6 de 1.246 (0,5%)**, de **3 fontes**: myfruit
  IT-T10-018 (2), Cifo IT-T9-009 (2), AgroNotizie IT-T1-021 (2). E os 2 da Cifo e os 2 da AgroNotizie são,
  cada par, a mesma página capturada duas vezes.
- **Coorte 64:** 43 fontes com bruto (325 documentos) → **4 com as 3 (1,2%)**, de 2 fontes. **21 fontes
  nunca foram guardadas** (entre elas as 14 do edagricole.it): rendimento NAO SEI, não zero.
- **As 18 sociais novas: 0 documentos guardados** — rendimento NAO SEI.
- **Os 41 canais YouTube: 612 documentos (metade do acervo) → 0 com as 3**, 2 com FACT_TIME. O texto
  guardado de um vídeo é **só o título** (60–100 letras).
- **Onde o extractor falha (30 lidos à mão):** 5 datas e 5 regiões que o texto TEM e o extractor não
  leu. O resto (21 datas) o texto simplesmente não tem — capas, páginas sem corpo, vídeos só com título.
- **A 4.ª onda:** todo o rendimento medido está na **rodada 1**. As rodadas 6–14 (edagricole.it) nunca
  foram medidas.

## 1. Tabela por fonte e por classe

Colunas: documentos (um por sha256 do bruto) · com texto lido · FACT_TIME com ano (= período provado) ·
região do facto · cultura · **as 3**. Percentagem sobre os documentos da fonte. Ordem: as 3, depois ≥ 2,
depois alguma chave. `TABELA.json` tem tudo, fonte a fonte, também as fontes fora das três coortes.

### Por coorte

| Coorte | Fontes | com bruto | Documentos | FACT_TIME c/ ano | região | cultura | **as 3** | fontes com algum item com as 3 |
|---|---|---|---|---|---|---|---|---|
| 64 (4.ª onda) | 64 | 43 | 325 | 21 (6,5%) | 37 (11,4%) | 24 (7,4%) | **4 (1,2%)** | 2 |
| 18 sociais novas | 18 | **0** | 0 | — | — | — | — | — |
| 41 canais YouTube | 41 | 41 | 612 | 2 (0,3%) | 6 (1,0%) | 41 (6,7%) | **0** | 0 |
| **Tudo** | — | — | 1.246 | 34 (2,7%) | 61 (4,9%) | 70 (5,6%) | **6 (0,5%)** | 3 |

### Por classe T*

| Classe | Itens | com texto | FACT_TIME c/ ano | região | cultura | as 3 | ≥ 2 |
|---|---|---|---|---|---|---|---|
| T1 | 34 | 18 | 2 (5,9%) | 5 (14,7%) | 4 (11,8%) | 2 | 2 |
| T2 | 134 | 115 | 7 (5,2%) | 10 (7,5%) | 1 (0,7%) | 0 | 4 |
| T3 | 26 | 14 | 1 (3,8%) | 1 (3,8%) | 0 (0%) | 0 | 0 |
| T4 | 1 | 0 | 0 (0%) | 0 (0%) | 0 (0%) | 0 | 0 |
| T5 | 211 | 100 | 7 (3,3%) | 8 (3,8%) | 7 (3,3%) | 0 | 5 |
| T7 | 424 | 305 | 1 (0,2%) | 13 (3,1%) | 8 (1,9%) | 0 | 2 |
| T8 | 50 | 46 | 0 (0%) | 1 (2%) | 12 (24%) | 0 | 0 |
| T9 | 58 | 55 | 3 (5,2%) | 5 (8,6%) | 10 (17,2%) | 2 | 3 |
| T10 | 141 | 83 | 10 (7,1%) | 15 (10,6%) | 21 (14,9%) | 2 | 12 |
| T11 | 31 | 31 | 1 (3,2%) | 1 (3,2%) | 0 (0%) | 0 | 1 |
| T12 | 136 | 133 | 2 (1,5%) | 2 (1,5%) | 7 (5,1%) | 0 | 1 |

A classe que mais rende é **T10 (mercado)**: 12 documentos com ≥ 2 chaves, quase todos da myfruit. T1
(boletins) tem a melhor taxa (2 de 34), mas só 18 T1 têm texto.

### Por fonte

**Coorte 64 (4.ª onda)** (64 fontes)

| Fonte | Rodada | Itens | com texto | FACT_TIME c/ ano | região | cultura | as 3 |
|---|---|---|---|---|---|---|---|
| IT-T10-018 | 1 | 60 | 33 | 9 (15%) | 9 (15%) | 12 (20%) | **2** (3,3%) |
| IT-T9-009 | 1 | 5 | 5 | 2 (40%) | 2 (40%) | 4 (80%) | **2** (40%) |
| IT-T2-034 | 1 | 10 | 10 | 1 (10%) | 3 (30%) | 1 (10%) | **0** (0%) |
| IT-T7-042 | 1 | 27 | 7 | 1 (3,7%) | 3 (11,1%) | 0 (0%) | **0** (0%) |
| IT-T2-051 | 1 | 9 | 9 | 2 (22,2%) | 2 (22,2%) | 0 (0%) | **0** (0%) |
| IT-T9-021 | 1 | 3 | 3 | 1 (33,3%) | 3 (100%) | 0 (0%) | **0** (0%) |
| IT-T2-032 | 1 | 5 | 5 | 2 (40%) | 1 (20%) | 0 (0%) | **0** (0%) |
| IT-T7-125 | 1 | 3 | 3 | 0 (0%) | 2 (66,7%) | 1 (33,3%) | **0** (0%) |
| IT-T10-021 | 1 | 7 | 6 | 1 (14,3%) | 1 (14,3%) | 2 (28,6%) | **0** (0%) |
| IT-T7-017 | 1 | 74 | 14 | 0 (0%) | 3 (4,1%) | 0 (0%) | **0** (0%) |
| IT-T5-186 | 3 | 3 | 3 | 1 (33,3%) | 2 (66,7%) | 0 (0%) | **0** (0%) |
| IT-T5-056 | 5 | 3 | 3 | 0 (0%) | 0 (0%) | 2 (66,7%) | **0** (0%) |
| IT-T7-019 | 1 | 3 | 3 | 0 (0%) | 1 (33,3%) | 1 (33,3%) | **0** (0%) |
| IT-T2-037 | 1 | 4 | 4 | 1 (25%) | 0 (0%) | 0 (0%) | **0** (0%) |
| IT-T5-160 | 1 | 3 | 3 | 0 (0%) | 1 (33,3%) | 0 (0%) | **0** (0%) |
| IT-T7-043 | 1 | 3 | 1 | 0 (0%) | 1 (33,3%) | 0 (0%) | **0** (0%) |
| IT-T7-049 | 1 | 3 | 3 | 0 (0%) | 1 (33,3%) | 0 (0%) | **0** (0%) |
| IT-T7-163 | 1 | 3 | 3 | 0 (0%) | 0 (0%) | 1 (33,3%) | **0** (0%) |
| IT-T7-112 | 4 | 2 | 2 | 0 (0%) | 1 (50%) | 0 (0%) | **0** (0%) |
| IT-T7-118 | 5 | 2 | 2 | 0 (0%) | 1 (50%) | 0 (0%) | **0** (0%) |
| IT-T10-022 | 1 | 23 | 4 | 0 (0%) | 0 (0%) | 0 (0%) | **0** (0%) |
| IT-T7-033 | 1 | 15 | 1 | 0 (0%) | 0 (0%) | 0 (0%) | **0** (0%) |
| IT-T7-021 | 1 | 5 | 5 | 0 (0%) | 0 (0%) | 0 (0%) | **0** (0%) |
| IT-T7-117 | 1 | 5 | 5 | 0 (0%) | 0 (0%) | 0 (0%) | **0** (0%) |
| IT-T2-006 | 2 | 4 | 4 | 0 (0%) | 0 (0%) | 0 (0%) | **0** (0%) |
| IT-T12-024 | 1 | 3 | 3 | 0 (0%) | 0 (0%) | 0 (0%) | **0** (0%) |
| IT-T12-129 | 1 | 3 | 3 | 0 (0%) | 0 (0%) | 0 (0%) | **0** (0%) |
| IT-T12-130 | 15 | 3 | 3 | 0 (0%) | 0 (0%) | 0 (0%) | **0** (0%) |
| IT-T2-145 | 1 | 3 | 3 | 0 (0%) | 0 (0%) | 0 (0%) | **0** (0%) |
| IT-T2-146 | 2 | 3 | 3 | 0 (0%) | 0 (0%) | 0 (0%) | **0** (0%) |
| IT-T5-167 | 4 | 3 | 3 | 0 (0%) | 0 (0%) | 0 (0%) | **0** (0%) |
| IT-T5-185 | 2 | 3 | 3 | 0 (0%) | 0 (0%) | 0 (0%) | **0** (0%) |
| IT-T7-048 | 1 | 3 | 3 | 0 (0%) | 0 (0%) | 0 (0%) | **0** (0%) |
| IT-T7-103 | 1 | 3 | 3 | 0 (0%) | 0 (0%) | 0 (0%) | **0** (0%) |
| IT-T7-139 | 1 | 3 | 3 | 0 (0%) | 0 (0%) | 0 (0%) | **0** (0%) |
| IT-T12-117 | 1 | 2 | 2 | 0 (0%) | 0 (0%) | 0 (0%) | **0** (0%) |
| IT-T5-025 | 1 | 2 | 2 | 0 (0%) | 0 (0%) | 0 (0%) | **0** (0%) |
| IT-T9-011 | 1 | 2 | 2 | 0 (0%) | 0 (0%) | 0 (0%) | **0** (0%) |
| IT-T12-137 | 1 | 1 | 1 | 0 (0%) | 0 (0%) | 0 (0%) | **0** (0%) |
| IT-T7-121 | 1 | 1 | 1 | 0 (0%) | 0 (0%) | 0 (0%) | **0** (0%) |
| IT-T7-135 | 3 | 1 | 1 | 0 (0%) | 0 (0%) | 0 (0%) | **0** (0%) |
| IT-T7-141 | 1 | 1 | 0 | 0 (0%) | 0 (0%) | 0 (0%) | **0** (0%) |
| IT-T8-062 | 1 | 1 | 0 | 0 (0%) | 0 (0%) | 0 (0%) | **0** (0%) |
| IT-T12-131 | 1 | 0 | — | NAO SEI (sem bruto) | NAO SEI | NAO SEI | NAO SEI |
| IT-T2-050 | 1 | 0 | — | NAO SEI (sem bruto) | NAO SEI | NAO SEI | NAO SEI |
| IT-T3-023 | 2 | 0 | — | NAO SEI (sem bruto) | NAO SEI | NAO SEI | NAO SEI |
| IT-T5-080 | 1 | 0 | — | NAO SEI (sem bruto) | NAO SEI | NAO SEI | NAO SEI |
| IT-T5-111 | 2 | 0 | — | NAO SEI (sem bruto) | NAO SEI | NAO SEI | NAO SEI |
| IT-T5-113 | 3 | 0 | — | NAO SEI (sem bruto) | NAO SEI | NAO SEI | NAO SEI |
| IT-T5-187 | 1 | 0 | — | NAO SEI (sem bruto) | NAO SEI | NAO SEI | NAO SEI |
| IT-T7-123 | 2 | 0 | — | NAO SEI (sem bruto) | NAO SEI | NAO SEI | NAO SEI |
| IT-T7-172 | 1 | 0 | — | NAO SEI (sem bruto) | NAO SEI | NAO SEI | NAO SEI |
| IT-T8-021 | 3 | 0 | — | NAO SEI (sem bruto) | NAO SEI | NAO SEI | NAO SEI |
| IT-T8-022 | 4 | 0 | — | NAO SEI (sem bruto) | NAO SEI | NAO SEI | NAO SEI |
| IT-T8-024 | 5 | 0 | — | NAO SEI (sem bruto) | NAO SEI | NAO SEI | NAO SEI |
| IT-T8-028 | 6 | 0 | — | NAO SEI (sem bruto) | NAO SEI | NAO SEI | NAO SEI |
| IT-T8-029 | 7 | 0 | — | NAO SEI (sem bruto) | NAO SEI | NAO SEI | NAO SEI |
| IT-T8-030 | 8 | 0 | — | NAO SEI (sem bruto) | NAO SEI | NAO SEI | NAO SEI |
| IT-T8-034 | 9 | 0 | — | NAO SEI (sem bruto) | NAO SEI | NAO SEI | NAO SEI |
| IT-T8-039 | 10 | 0 | — | NAO SEI (sem bruto) | NAO SEI | NAO SEI | NAO SEI |
| IT-T8-040 | 11 | 0 | — | NAO SEI (sem bruto) | NAO SEI | NAO SEI | NAO SEI |
| IT-T8-041 | 12 | 0 | — | NAO SEI (sem bruto) | NAO SEI | NAO SEI | NAO SEI |
| IT-T8-042 | 13 | 0 | — | NAO SEI (sem bruto) | NAO SEI | NAO SEI | NAO SEI |
| IT-T8-051 | 14 | 0 | — | NAO SEI (sem bruto) | NAO SEI | NAO SEI | NAO SEI |

**As 18 sociais novas (SOCIAL-QUALIFICAR)** (18 fontes)

| Fonte | Itens | com texto | FACT_TIME c/ ano | região | cultura | as 3 |
|---|---|---|---|---|---|---|
| IT-T11-014 | 0 | — | NAO SEI (sem bruto) | NAO SEI | NAO SEI | NAO SEI |
| IT-T12-152 | 0 | — | NAO SEI (sem bruto) | NAO SEI | NAO SEI | NAO SEI |
| IT-T12-153 | 0 | — | NAO SEI (sem bruto) | NAO SEI | NAO SEI | NAO SEI |
| IT-T2-165 | 0 | — | NAO SEI (sem bruto) | NAO SEI | NAO SEI | NAO SEI |
| IT-T2-166 | 0 | — | NAO SEI (sem bruto) | NAO SEI | NAO SEI | NAO SEI |
| IT-T2-167 | 0 | — | NAO SEI (sem bruto) | NAO SEI | NAO SEI | NAO SEI |
| IT-T5-190 | 0 | — | NAO SEI (sem bruto) | NAO SEI | NAO SEI | NAO SEI |
| IT-T5-191 | 0 | — | NAO SEI (sem bruto) | NAO SEI | NAO SEI | NAO SEI |
| IT-T5-192 | 0 | — | NAO SEI (sem bruto) | NAO SEI | NAO SEI | NAO SEI |
| IT-T5-193 | 0 | — | NAO SEI (sem bruto) | NAO SEI | NAO SEI | NAO SEI |
| IT-T7-253 | 0 | — | NAO SEI (sem bruto) | NAO SEI | NAO SEI | NAO SEI |
| IT-T7-254 | 0 | — | NAO SEI (sem bruto) | NAO SEI | NAO SEI | NAO SEI |
| IT-T7-255 | 0 | — | NAO SEI (sem bruto) | NAO SEI | NAO SEI | NAO SEI |
| IT-T7-256 | 0 | — | NAO SEI (sem bruto) | NAO SEI | NAO SEI | NAO SEI |
| IT-T7-257 | 0 | — | NAO SEI (sem bruto) | NAO SEI | NAO SEI | NAO SEI |
| IT-T9-025 | 0 | — | NAO SEI (sem bruto) | NAO SEI | NAO SEI | NAO SEI |
| IT-T9-026 | 0 | — | NAO SEI (sem bruto) | NAO SEI | NAO SEI | NAO SEI |
| IT-T9-027 | 0 | — | NAO SEI (sem bruto) | NAO SEI | NAO SEI | NAO SEI |

**Os 41 canais YouTube do Scrap** (41 fontes)

| Fonte | Itens | com texto | FACT_TIME c/ ano | região | cultura | as 3 |
|---|---|---|---|---|---|---|
| IT-T10-017 | 15 | 15 | 0 (0%) | 2 (13,3%) | 6 (40%) | **0** (0%) |
| IT-T12-011 | 15 | 15 | 2 (13,3%) | 0 (0%) | 1 (6,7%) | **0** (0%) |
| IT-T8-006 | 15 | 15 | 0 (0%) | 0 (0%) | 12 (80%) | **0** (0%) |
| IT-T5-040 | 15 | 15 | 0 (0%) | 0 (0%) | 4 (26,7%) | **0** (0%) |
| IT-T9-017 | 15 | 15 | 0 (0%) | 0 (0%) | 4 (26,7%) | **0** (0%) |
| IT-T12-007 | 15 | 15 | 0 (0%) | 0 (0%) | 3 (20%) | **0** (0%) |
| IT-T12-008 | 15 | 15 | 0 (0%) | 0 (0%) | 3 (20%) | **0** (0%) |
| IT-T7-027 | 15 | 15 | 0 (0%) | 0 (0%) | 2 (13,3%) | **0** (0%) |
| IT-T9-014 | 15 | 15 | 0 (0%) | 0 (0%) | 2 (13,3%) | **0** (0%) |
| IT-T12-014 | 15 | 15 | 0 (0%) | 1 (6,7%) | 0 (0%) | **0** (0%) |
| IT-T12-016 | 15 | 15 | 0 (0%) | 1 (6,7%) | 0 (0%) | **0** (0%) |
| IT-T2-026 | 15 | 15 | 0 (0%) | 1 (6,7%) | 0 (0%) | **0** (0%) |
| IT-T5-037 | 15 | 15 | 0 (0%) | 0 (0%) | 1 (6,7%) | **0** (0%) |
| IT-T7-022 | 15 | 15 | 0 (0%) | 0 (0%) | 1 (6,7%) | **0** (0%) |
| IT-T7-028 | 15 | 15 | 0 (0%) | 0 (0%) | 1 (6,7%) | **0** (0%) |
| IT-T7-035 | 15 | 15 | 0 (0%) | 0 (0%) | 1 (6,7%) | **0** (0%) |
| IT-T8-005 | 15 | 15 | 0 (0%) | 1 (6,7%) | 0 (0%) | **0** (0%) |
| IT-T10-019 | 15 | 15 | 0 (0%) | 0 (0%) | 0 (0%) | **0** (0%) |
| IT-T11-006 | 15 | 15 | 0 (0%) | 0 (0%) | 0 (0%) | **0** (0%) |
| IT-T11-007 | 15 | 15 | 0 (0%) | 0 (0%) | 0 (0%) | **0** (0%) |
| IT-T12-012 | 15 | 15 | 0 (0%) | 0 (0%) | 0 (0%) | **0** (0%) |
| IT-T12-015 | 15 | 15 | 0 (0%) | 0 (0%) | 0 (0%) | **0** (0%) |
| IT-T2-027 | 15 | 15 | 0 (0%) | 0 (0%) | 0 (0%) | **0** (0%) |
| IT-T2-028 | 15 | 15 | 0 (0%) | 0 (0%) | 0 (0%) | **0** (0%) |
| IT-T5-038 | 15 | 15 | 0 (0%) | 0 (0%) | 0 (0%) | **0** (0%) |
| IT-T7-015 | 15 | 15 | 0 (0%) | 0 (0%) | 0 (0%) | **0** (0%) |
| IT-T7-020 | 15 | 15 | 0 (0%) | 0 (0%) | 0 (0%) | **0** (0%) |
| IT-T7-023 | 15 | 15 | 0 (0%) | 0 (0%) | 0 (0%) | **0** (0%) |
| IT-T7-024 | 15 | 15 | 0 (0%) | 0 (0%) | 0 (0%) | **0** (0%) |
| IT-T7-025 | 15 | 15 | 0 (0%) | 0 (0%) | 0 (0%) | **0** (0%) |
| IT-T7-026 | 15 | 15 | 0 (0%) | 0 (0%) | 0 (0%) | **0** (0%) |
| IT-T7-030 | 15 | 15 | 0 (0%) | 0 (0%) | 0 (0%) | **0** (0%) |
| IT-T7-032 | 15 | 15 | 0 (0%) | 0 (0%) | 0 (0%) | **0** (0%) |
| IT-T7-034 | 15 | 15 | 0 (0%) | 0 (0%) | 0 (0%) | **0** (0%) |
| IT-T7-036 | 15 | 15 | 0 (0%) | 0 (0%) | 0 (0%) | **0** (0%) |
| IT-T7-037 | 15 | 15 | 0 (0%) | 0 (0%) | 0 (0%) | **0** (0%) |
| IT-T7-039 | 15 | 15 | 0 (0%) | 0 (0%) | 0 (0%) | **0** (0%) |
| IT-T8-004 | 15 | 15 | 0 (0%) | 0 (0%) | 0 (0%) | **0** (0%) |
| IT-T9-016 | 15 | 15 | 0 (0%) | 0 (0%) | 0 (0%) | **0** (0%) |
| IT-T2-025 | 14 | 14 | 0 (0%) | 0 (0%) | 0 (0%) | **0** (0%) |
| IT-T12-010 | 13 | 13 | 0 (0%) | 0 (0%) | 0 (0%) | **0** (0%) |

## 2. Trinta sem FACT_TIME, lidos à mão

Escolha ao acaso (semente `20260926`), com texto e sem FACT_TIME, no máximo 2 por fonte: 18 da coorte 64,
8 dos 41 canais, 4 de fora. Para cada um li o título, o porquê do extractor, os trechos com data e os
lugares do corpo (`AMOSTRA-30.json`); o veredito, item a item, está em `LEITURA-A-MAO-30.json`.

| Data do facto | Itens | Região do facto | Itens |
|---|---|---|---|
| **o texto TEM e o extractor falhou** | **5** | **o texto TEM e o extractor falhou** | **5** |
| só a data do comunicado («Roma, 7 agosto 2026 –») — é publicação, a lei manda NAO SEI | 3 | dada e certa (1 com um lugar a mais) | 1 |
| dia sem ano — NAO SEI certo | 1 | discutível (sede da empresa perfilada) | 1 |
| o texto não tem | 21 | o texto não tem (ou só país / estrangeiro / quem publica) | 23 |

Na coorte 64: **4 de 18** com data que o extractor perdeu; nos 41 canais: **1 de 8** (os outros 7 são só título).

### Os padrões onde o extractor falha (propostas — nada foi mudado)

| Padrão | Exemplo real | Data | Região |
|---|---|---|---|
| **A. título curto fica fora do corpo** — `corpo()` exige ≥ 8 palavras por linha; num vídeo o texto guardado é SÓ o título | «Bilancio Vini d'Abruzzo 2020» (IT-T7-015) · «Potatura dell'olivo: a Macerata la 9a selezione studenti» (IT-T12-008) | ✔ | ✔✔ |
| **B. acontecimento sem âncora agro** — incêndio, «evento atmosferico» (este é descartado como `ANCORA_DENTRO_DE_OUTRA`) | «Venti forti dell'11 maggio 2026 in provincia di Verona» (IT-T12-024) · «nella prima mattinata del 7 settembre 2026 … a Pontenure» (IT-T2-051) | ✔✔ | |
| **C. comune fora do gazetteer** — o gazetteer só tem regiões e províncias; a sigla «(PC)» não é lida | «Pontenure (PC)», «Finale Emilia» (IT-T2-051) | | ✔✔ |
| **D. «in provincia di X»** não é âncora de lugar | IT-T12-024 | | ✔ |
| **E. ano dentro do nome do evento** | «World Championship 2019 … 7 medaglie d'oro» (IT-T7-017) | ✔ | |
| **F. semana com ano + dia sem ano** | «settimana 39/2026, effettuata oggi 22 settembre» (IT-T10-018) | ✔ | |

**O que o texto NÃO tem (21 de 30)** — não é defeito do extractor: páginas sem corpo (menu), vídeos só
com título, páginas institucionais/de lei/de história, capas. E **3 comunicados** cuja única data é a
linha de data («Roma, 4 agosto 2026 –»): hoje a lei lê-a como publicação; se for também a data do
facto (a declaração foi nesse dia), é decisão do dono, não do extractor.

## 3. Proposta de ORDEM das 15 rodadas (só proposta; quem decide é o dono)

As rodadas são as do plano (`origin/c2-juiz-v1` `ferramentas/big_collection/onda4/`,
`auditoria-madrugada/C2-ONDA4/rodadas.txt`): **as mesmas fontes em cada rodada, o mesmo teto (5 por
domínio) e a mesma janela de 24 h**. Só muda a ordem. `RODADAS.json`.

| Rodada | Fontes | com bruto | Documentos medidos | as 3 | ≥ 2 | alguma | Pedidos previstos |
|---|---|---|---|---|---|---|---|
| **1** | 38 | 33 | 298 | **4** | **17** | 54 | 174 |
| 3 | 4 | 2 | 4 | 0 | 0 | 3 | 19 |
| 5 | 3 | 2 | 5 | 0 | 0 | 3 | 15 |
| 4 | 3 | 2 | 5 | 0 | 0 | 1 | 15 |
| 2 | 6 | 3 | 10 | 0 | 0 | 0 | 28 |
| 15 | 1 (IT-T12-130) | 1 | 3 | 0 | 0 | 0 | 5 |
| 6–14 | 1 cada (edagricole.it IT-T8-028…051) | **0** | 0 | NAO SEI | NAO SEI | NAO SEI | 5 cada |

**Ordem proposta: 1 → 3 → 5 → 4 → 2 → 15 → 6 … 14.**
- A rodada 1 já é a primeira e leva todo o rendimento medido (myfruit, Cifo, ARPAL, ARPA Marche, ARPAE,
  Consorzio Balsamico, CIA Puglia, Didacta).
- As rodadas 6–14 **não se medem sem coletar**: o edagricole.it nunca foi guardado. Pô-las no fim não é
  dizer que rendem 0 — é dizer que NÃO SEI. Se o dono quiser saber, uma só delas (por exemplo a 6)
  mede o edagricole inteiro.
- ⚠️ Com 3–10 documentos por rodada (2–5), a diferença entre 3, 5 e 4 é pequena: é ordenar por pouco.

### Fontes que sairiam por rendimento 0 (só proposta)

Critério: **bruto guardado com ≥ 3 documentos com texto, e 0 nas 3 chaves**. Com menos de 3 documentos,
não há medida para decidir (fica). E sai da lista quem teve um **defeito do extractor** na leitura à mão
(o zero é nosso, não da fonte).

| Fonte | Documentos (com texto) | O que se viu |
|---|---|---|
| IT-T10-022 | 23 (4) | 19 sem texto |
| IT-T12-129 | 3 (3) | normativa (leis regionais) |
| IT-T12-130 | 3 (3) | política (PAC 2028) — **é edagricole.it** (Terra e Vita) |
| IT-T2-006 | 4 (4) | — |
| IT-T2-145 | 3 (3) | — |
| IT-T2-146 | 3 (3) | — |
| IT-T5-167 | 3 (3) | página sem corpo (CREA, infraestruturas) |
| IT-T5-185 | 3 (3) | — |
| IT-T7-021 | 5 (5) | — |
| IT-T7-048 | 3 (3) | capa («Chi siamo», já na FECHO-ONDA3) |
| IT-T7-103 | 3 (3) | — |
| IT-T7-117 | 5 (5) | páginas fiscais (CAF CIA) |
| IT-T7-139 | 3 (3) | comunicados com só a linha de data |

**Ficam, apesar do zero:** IT-T12-024 e IT-T2-051 (os zeros são falhas do extractor — padrões B, C, D),
e as fontes com < 3 documentos com texto (IT-T12-117, IT-T12-137, IT-T5-025, IT-T7-033, IT-T7-121,
IT-T7-135, IT-T7-141, IT-T8-062, IT-T9-011). ⚠️ Três documentos por fonte é pouco: «0 em 3» não prova que a
fonte nunca dá chaves; prova que as páginas que o coletor escolheu não deram.

## 4. COLLECTION GAPS (INT-LAW-150/151) — o tipo de fonte que falta (sem rota nem coletor)

Medido acima: as chaves aparecem juntas em **boletins com cultura + zona + data** (AgroNotizie T1),
**observatórios de preço com mercado + dia + produto** (myfruit T10) e **eventos técnicos com
feira + data + cultura** (Cifo T9). O que falta:

1. **Boletins fitossanitários regionais (T1) guardados.** 34 documentos T1 em 1.246, 18 com texto, e
   7 fontes T1 bloqueadas sem receita web. É a classe com a melhor taxa (2 em 34) e a que traz FASE
   (a única classe com régua de fase).
2. **Avisos dos Serviços Fitossanitários Regionais** (avvisi per coltura e zona, com data de emissão e
   de validade): cultura + região + período no próprio formato.
3. **Listas de preços com praça e dia** (mercados ortofrutícolas, câmaras de comércio): o formato da
   myfruit (a fonte que mais rende) em mais praças.
4. **Declarações de calamidade / reconhecimento de eventos** (decretos regionais e do MASAF com data do
   evento, província e culturas danificadas) — o IT-T12-024 mostra que existem e trazem data + lugar.
5. **Boletins agrometeorológicos por área e cultura** (T2 agrometeo): as ARPA de hoje trazem sobretudo
   notícias de ambiente (incêndios, qualidade do ar), sem cultura.
6. **Vídeo com descrição ou transcrição**, não só título: 612 documentos YouTube rendem 0 com as 3 porque
   só o título foi guardado. (É uma falta de CONTEÚDO da fonte guardada; a rota não se escolhe aqui.)

## Ficheiros (todos no ramo, só registos)

| Ficheiro | O quê |
|---|---|
| `data/derivados/RENDIMENTO-POR-FONTE/tabela.py.txt` → `TABELA.json` | por fonte, classe e coorte (lê a MEDIDA de `periodo-chaves-v1@71d40788` pelo git) |
| `…/amostra30.py.txt` → `AMOSTRA-30.json` | os 30 sem FACT_TIME, com o porquê do extractor e os trechos |
| `…/LEITURA-A-MAO-30.json` | o veredito humano, item a item |
| `…/rodadas.py.txt` → `RODADAS.json` | rendimento por rodada e a ordem proposta |

Mapa: não regerado; este ramo não tem código do sistema.
