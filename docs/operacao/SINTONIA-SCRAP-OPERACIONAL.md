# SINTONIA SCRAP — a página operacional

Medido em **2026-09-09** (SCRAP-R1), nesta máquina, ao vivo.
Uma página só. Se ela crescer, alguém está usando o lugar errado.

## O que o SCRAP é

```
SINTONIA SCRAP = DISPATCHER DE ROTAS SOCIAIS
```

Quem pede diz **plataforma + capacidade + alvo**. Nunca diz ferramenta.
A escolha entre pública, API oficial, sessão local e Apify é da casa.

| papel | dono canônico |
|---|---|
| executor / fases | `coleta/social_scrap.py` |
| política de rota + adaptadores | `coleta/social_rotas.py` |
| matriz declarada (a lei) | `leis/social_matriz.py` |
| taxonomia de falha | `leis/falhas.py` |
| guarda de credencial + redação | `guarda/social_sessao.py`, `guarda/social_guarda.py` |
| ledger | `data/samples/SOCIAL-IT/LEDGER-SOCIAL-IT.json` |

## Os cinco comandos

```bash
py coleta/social_scrap.py censo      # o que existe declarado (32 capacidades)
py coleta/social_scrap.py gap        # onde a Apify ainda é necessária
py coleta/social_scrap.py piloto     # a prova pequena, ao vivo, US$ 0
py coleta/social_scrap.py ledger     # o que REALMENTE rodou
py coleta/social_scrap.py guarda     # nenhum segredo entrou no Git
```

`politica`, `sessao`, `portao <url>`, `video`, `authmodes` e `youtube*` completam a lista.

## O que dá para coletar HOJE, sem credencial e sem pagar

| plataforma | rota | prova viva de 2026-09-09 |
|---|---|---|
| MASTODON | pública (`SEARCH_HASHTAG`) | 6 execuções, 86 objetos |
| BLUESKY | pública (`DISCOVER_ACCOUNT`) | 2 execuções, 32 objetos |
| TELEGRAM | prévia pública | rodou; os 2 canais testados não existem |

Custo do piloto inteiro: **US$ 0,0000**. Zero chamada Apify.

## O que exige credencial (e a recusa é explícita)

`YOUTUBE` (Data API v3), `FACEBOOK`/`INSTAGRAM` (Graph), `THREADS`, `REDDIT`, `X` (paga).
Sem a chave, o estado é `CREDENTIAL_MISSING` e a coleta **para** — nunca cai para scraping.

## O que está bloqueado, e por quê

| plataforma | motivo |
|---|---|
| TIKTOK | robots nomeia ClaudeBot em `Disallow: /`; Termos §5 |
| LINKEDIN | User Agreement §8.2; só entra como DESCOBERTA indireta |
| X | `Disallow: /`; a rota permitida é a API paga |
| YouTube grátis | as 3 rotas que MEDIMOS funcionando estão em `Disallow` |

## STORIES

**Não há capacidade STORY declarada na matriz.** Nenhuma plataforma, nenhuma rota.
O único caminho conhecido é o enum `resultsType: "stories"` do ator
`apify~instagram-scraper 0.0.776` — **rota paga, nunca exercida por esta casa**, e
Story de terceiro não é conteúdo público. Ver `SCRAP-COLLECTION-INTEGRATION-HANDOFF.md`.

```
STORIES_READY = NO   ·   classe: PAID_ROUTE_ONLY + NO_LIVE_SAMPLE
```

## As três leis que mordem

```
ROTA QUE FUNCIONA NÃO É ROTA PERMITIDA.
CAN DO != DID DO — só o ledger conta coleta.
ENTRADA QUE FALTA NÃO É FONTE QUE MUDOU.
```
