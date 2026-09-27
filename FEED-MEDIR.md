# FEED-MEDIR — os 14 feeds, a janela de 24 h e o robots (D91)

> Missão da coordenação 22:05. Anexo D91, 22:32. Ramo `feed-medir-v1`, filho de
> `scrap-evolucao-v1 @ 3103f723`, o aceite para o LOTE 4. **Nada instalado, nenhum pedido à rede.**
>
> O vivo avançou para `554c1ec1` (22:25). Este ramo não é para instalar sozinho: vai junto com o
> SCRAP-EVOLUCAO no LOTE 4. A regra da janela (`ferramentas/big_collection/rodadas.py`) e a do teto
> (`provas/prova_teto_dominio.py`) são **idênticas** em `dc0de726` e em `554c1ec1`: diff vazio, conferido.

## 1 · Quem pode ser medido agora (medido às 22:11 de 26/09, hora de Brasília)

Regra das rodadas (D79): cada `TETO-ONDA.json` debaixo de `C:/Users/London1/sintonia-sala-italia/ondas`, mais
os `RECIBO*.json` de `C:/Users/London1/auditoria-madrugada`. Recibo com esses domínios: **nenhum**.
O instante de cada fonte vem do RUN_ID + SEGUNDOS. Saída: `provas/scrap_evolucao/JANELA-FEEDS.json`.

| fonte | domínio | estado | abre em (Brasília) | quem pediu por último |
|---|---|---|---|---|
| IT-T5-090 ISTAT | istat.it | **LIVRE_AGORA** | — | nenhum livro de onda; o robô vivo, em 24/09 |
| IT-T5-186 ENEA | enea.it | **LIVRE_AGORA** | — | onda 3, 25/09 19:46 |
| IT-T10-022 | zootecnicainternational.com | FECHADO | 27/09 20:01 | 4.ª onda, rodada 1 |
| IT-T12-117 | calabriaimpresa.eu | FECHADO | 27/09 20:03 | 4.ª onda, rodada 1 |
| IT-T12-137 | psrn.it | FECHADO | 27/09 20:03 | 4.ª onda, rodada 1 |
| IT-T12-130 | edagricole.it | FECHADO | 27/09 20:06 | 4.ª onda, rodada 1 |
| IT-T7-021 | etvilloresi.it | FECHADO | 27/09 20:07 | 4.ª onda, rodada 1 |
| IT-T7-033 | chianticlassico.com | FECHADO | 27/09 20:07 | 4.ª onda, rodada 1 |
| IT-T7-042 | consorziobalsamico.it | FECHADO | 27/09 20:08 | 4.ª onda, rodada 1 |
| IT-T7-049 | copagri.org | FECHADO | 27/09 20:10 | 4.ª onda, rodada 1 |
| IT-T7-125 | cia-puglia.it | FECHADO | 27/09 20:11 | 4.ª onda, rodada 1 |
| IT-T7-139 | florovivaistiitaliani.it | FECHADO | 27/09 20:11 | 4.ª onda, rodada 1 |
| IT-T9-009 | cifo.it | FECHADO | 27/09 20:13 | 4.ª onda, rodada 1 |
| IT-T9-021 | indire.it | FECHADO | 27/09 20:13 | 4.ª onda, rodada 1 |

**LIVRE_AGORA: 2 de 14.** A rodada 1 da 4.ª onda (20:01–20:14) tocou 12 dos 14.

Conferido também fora dos livros:
- **Robô vivo** (`observations.ndjson`, `CAPTURED_AT`): istat.it em 24/09 07:12; enea.it em 25/09 19:46.
  Bate com os livros.
- **Lista-mestra** (`LISTA-MESTRA-PESQUISADORES.md`): só repositórios de universidade (unimi, unito, unifi…).
  Nenhum dos 14 domínios.
- **Micro-provas:** o `MICRO-PROVA-ROTEIRO.md` (05:46) cita «enea.it na rodada 1 (5 pedidos)». É o **plano**
  da 4.ª onda, com 38 domínios. O livro da rodada que correu (33 domínios) **não** tem enea.it. Nenhum
  resultado de micro-prova das últimas 24 h cita os 14 domínios.
- ⚠️ **Limite:** só vejo o que deixou livro, recibo ou observação. Uma corrida com rede que não deixou
  nenhum dos três é invisível aqui — e também para as rodadas.
- ⚠️ **IT-T5-186 (ENEA)** só anuncia o feed de **um** evento (`/eventi/meeting-internazionali-0/feed`), não o do site.

## 2 · Os comandos (coordenador, com VPN IT)

Correr a partir de uma cópia do ramo `feed-medir-v1` (ex.: `C:/scrap-evo`).

**Passo 1 — a janela no instante de correr** (só leitura; os livros andam):
```
py provas/scrap_evolucao/feeds_janela.py --livros=C:/Users/London1/sintonia-sala-italia/ondas --recibos=C:/Users/London1/auditoria-madrugada
```
A última linha dá a lista: `LIVRE_AGORA n/14: IT-…,IT-…`.

**Passo 2 — medir só as livres: 1 pedido ao robots + 1 ao feed, por fonte:**
```
py provas/scrap_evolucao/medir_feeds_com_rede.py --livros=C:/Users/London1/sintonia-sala-italia/ondas --recibos=C:/Users/London1/auditoria-madrugada --saida=C:/Users/London1/auditoria-madrugada/feed-medir/r1 --so=IT-T5-090,IT-T5-186
```
- O egresso é provado uma vez, no começo. Sem IT, nada sai.
- Por fonte, pelo portão (`coleta/rota_navegador.medir`): janela 24 h → robots vivo → feed.
- Robots que proíbe o feed = o feed não é pedido. Custo: 1 pedido.
- Saída: `CORPO.bin` + `RECIBO-ROTA-NAVEGADOR.json` por fonte, e `MEDIDA-FEEDS.json` com HTTP, bytes, itens,
  itens do próprio site e itens com data de publicação (`pubDate`/`dc:date`/`published`; `updated` não conta).
  A data é publicação no nível do índice, **nunca** FACT_TIME.
- ⚠️ Os recibos fecham istat.it e enea.it por 24 h para a coleta.
- As outras 12 medem-se depois de **27/09 20:14**, com o mesmo passo 1 e o `--so` que ele devolver.
- Sem `--so`, as fechadas param sozinhas no portão (0 pedidos, `PAROU: JANELA_24H`).

## 3 · D91 — o robots em todas as páginas comuns

Conferido no código e **provado sem rede**. Em dois pontos o robots **não** era cumprido em todas as
páginas, e foi consertado:

| peça | robots | prova |
|---|---|---|
| **Feed**, pelo coletor | ✅ já cumpria: `baixar()` → `licenca()` pede licença antes do feed e de cada item | `provas/feed_robots_local.mjs` 2/2: item proibido e feed proibido nunca chegam ao servidor |
| **Medir os feeds / Piemonte** (`rota_navegador.medir`) | ✅ o robots vivo antes do pedido; proibido = 0 pedidos à página | testes B3 |
| **Prova de território** (`colher_prova_territorio`) | ✅ já cumpria: a entrada e cada ligação passam por `can_fetch` | testes existentes |
| **Canário** (com ou sem cara de navegador) | ⚠️ **não cumpria no item.** O worker só lia o robots da **entrada** do contrato; o canário abria o item sem perguntar. **Consertado:** dentro de um canário web, cada endereço pede licença (uma leitura por site). Proibido = não sai (`ROBOTS_PROIBE`); robots ilegível = não sai (`ROBOTS_ILEGIVEL`) | 3 testes novos |
| **captura_xhr** | ⚠️ **só a página de entrada.** **Consertado:** cada pedido do navegador (página, scripts, dados) pede licença ao robots do seu site; site novo = o robots dele é lido e conta no teto dele. E o `favicon.ico`, que o Chrome pede sozinho e gastava teto, passou a não sair | 3 testes, 1 com Chrome de verdade: o JSON proibido não chegou ao servidor |
| **Peça 6** (navegador real) | desligada. A condição ficou escrita (doc P6 + `scrap_capacidades.py`): cada página pede licença, com o mesmo porteiro | — |

⚠️ Três coisas que **não** mudei e deixo para decisão:
1. **O canário do feed do YouTube** continua sem robots. O worker manda a rota do Scrap à matriz dele (SOC2).
   Se o feed RSS do YouTube conta como «API pública oficial documentada» da D91: **NÃO SEI**.
2. **`scrap_http.permitido`** (usado pelo `medir`) julga o robots com o nome do agente da casa
   (`SintoniaScrap`), mas o pedido sai com a cara do Chrome. Regras para `*` valem igual. Uma regra escrita
   só para «Mozilla» ou «Chrome» não seria vista. É raro, mas existe.
3. **O `canario_stealth.py` da coordenação** (20:25, fora do repositório) não lia robots. Foi 1 pedido de
   medição por site; os 3 sites não foram conferidos.

## 4 · Provas
- Testes: `test_scrap_evolucao` 47 · `test_captura_xhr` 11 (2 com Chrome) · `test_feed_discovery` 3
  (inclui o robots no coletor). **61, todos OK.**
- Curadoria vizinha (canário, prova de território, boletins, receitas: 8 suítes): OK.
- Mutação: ver `provas/scrap_evolucao/MUTANTES.json`, com 7 sabotagens novas (D91 e FEED-MEDIR).

## EM PALAVRAS SIMPLES

**Quem dá para medir agora.** Dos 14 sites que têm "lista de novidades" (feed), **só 2 estão liberados
agora**: ISTAT e ENEA. Os outros 12 foram visitados hoje entre 20:01 e 20:14 pela coleta da noite. A
regra é esperar 24 horas antes de voltar ao mesmo site, então eles só reabrem **amanhã, 27/09, entre
20:01 e 20:14**. Deixei dois comandos: o primeiro confere na hora quem está livre (a lista muda com o
tempo); o segundo mede só os livres, com 2 visitas por site — a permissão do site e a lista.

**A permissão do site (robots).** Todo site tem um bilhete na porta dizendo onde o robô pode entrar.
Conferi cada peça nova:
- O robô de coleta já lia o bilhete antes de cada visita, inclusive nas listas de novidades. Provei com
  um site de mentira: a página proibida nunca foi visitada.
- **Achei dois buracos e fechei.**
  - O testador de fontes lia o bilhete da porta de entrada, mas depois abria uma notícia lá dentro sem
    olhar de novo. Agora olha antes de cada página.
  - A ferramenta que abre o site no Chrome só olhava o bilhete da página principal. Agora cada coisa
    que o Chrome tenta buscar precisa de permissão.
- A peça do navegador disfarçado continua desligada. Já está escrito que, quando for ligada, vai
  precisar olhar o bilhete em toda página.

**O que eu não sei.** Não sei se a lista de vídeos do YouTube conta como "serviço oficial" (que segue
regras próprias) ou como página comum. Deixei como estava, esperando a decisão.
