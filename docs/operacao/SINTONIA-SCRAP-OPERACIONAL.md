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

`FETCH_STORIES` é capacidade declarada da matriz desde 2026-09-09 (SCRAP-R2).
Comando: `py coleta/social_scrap.py stories --pagar`.

```
STORIES_CAPABILITY_READY   = PARTIAL   (falta só LIVE_SAMPLE)
LIVE_PROOF                 = NO — CREDENTIAL_MISSING neste ambiente
```

Tudo o que não depende da chave está pronto e testado: matriz, política de rota,
adaptador, normalizador, estados por perfil, dedupe e as travas. O que falta é
uma execução com a chave da Apify, que este ambiente não tem.

### A escada de rota, medida

| rota | estado | por quê |
|---|---|---|
| pública deslogada | `BLOCKED` | Instagram serve Story atrás de parede de login |
| Graph API oficial | `ROUTE_NOT_ALLOWED` | só entrega Story da **própria** conta, nunca de terceiro |
| `datavoyantlab/advanced-instagram-stories-scraper` | **ESCOLHIDO** | sem login, só perfil público, devolve `expiring_at` nativo |
| `muhammetakkurtt/instagram-scraper` | fallback | sem login, mas não documenta `expiring_at` |

Dois Actors foram **recusados por escrito**: o que exige o cookie `sessionid` de
uma conta real, e o `apify/instagram-scraper`, cujo `resultsType=stories`
devolvia **Reels** e foi depreciado pelo próprio publisher.

### Custo, pelo preço publicado

US$ 0,099 por execução + US$ 0,003 por perfil.

| contas | 1x/dia | 2x/dia |
|---|---|---|
| 10 | US$ 3,87/mês | US$ 7,74/mês |
| 25 | US$ 5,22/mês | US$ 10,44/mês |
| 50 | US$ 7,47/mês | US$ 14,94/mês |
| 100 | US$ 11,97/mês | US$ 23,94/mês |

Nenhum run foi executado. `ESTIMATED_SAVINGS = UNKNOWN`: não há custo anterior
comparável, porque esta casa nunca coletou Story.

### Limitações que já são conhecidas

- **Story em vídeo não transcreve ainda.** O transcritor local é indexado por
  `shortcode` e renova URL vencida relendo o embed público. Story não tem nem um
  nem outro: se a URL assinada morrer antes do download, não há segunda chance.
  O byte tem de ser baixado no mesmo run que o descobriu.
- **A URL do CDN é assinada e temporária.** Ela é pista, nunca evidência.
- **Perfil privado não é conta vazia**, e zero linha de um ator que falhou não é
  «não postou». Os dois têm estado próprio.

## As três leis que mordem

```
ROTA QUE FUNCIONA NÃO É ROTA PERMITIDA.
CAN DO != DID DO — só o ledger conta coleta.
ENTRADA QUE FALTA NÃO É FONTE QUE MUDOU.
```
