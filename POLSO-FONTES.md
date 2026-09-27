# POLSO-FONTES — as fontes públicas de preço que faltam

Missões da coordenação de 26/09 17:35 e 22:05. Ramo `nuvem-polso-mercato-v1`, **rebaseado sobre
`554c1ec1`** (base do LOTE 4, aviso das 22:25). No rebase, os commits «mapa: regerado» do POLSO-DI-MERCATO
saíram (conflito só nos gerados; a base ganhou) — o mapa deste ramo **não** está regerado sobre `554c1ec1`.
Depois do rebase: `tests.test_preco_de_mercado` OK e mutação 20/20 de novo.
**PRONTO-SEM-MAPA**: ficam sem peça no mapa (P9 pendente; são da peça `C-PRECO-DE-MERCADO`)
`scripts/polso_mercato/medir_fixtures.py`, `dominio_livre_24h.py`, `um_pedido_por_fonte.sh` e as provas JSON
deste relatório. Sem rede: tudo o que segue foi lido **no repo**. Onde o repo não
sabe, está escrito NAO SEI ou NAO VERIFICADO.

## Por que faltam fontes — medido no acervo

O leitor de preço (`leis/preco_de_mercado.py`) passado sobre o que a Collection **guardou**
(`data/collection-store/italy/IT-T10-*`, última versão de cada documento):

| fonte | documentos | com preço | observações | com PREÇO+PRAÇA+PERÍODO+UNIDADE |
|---|---|---|---|---|
| myfruit.it (IT-T10-018) | 39 | 5 | 82 | **0** |
| Plantgest (IT-T10-021) | 1 | 0 | 0 | 0 |
| Zootecnica Int. (IT-T10-022) | 10 | 0 | 0 | 0 |

As 82 observações do myfruit são quase todas **uva da tavola** (4 artigos) com preço, unidade e período, e
**nenhuma praça**: são preços de loja/online contados por jornalista. Nenhuma das 8 culturas do casco tem
preço com praça no acervo. Medida: `scripts/polso_mercato/POLSO-FONTES-FIXTURES-V1.json`.

As 8 culturas do casco (`italia-portale/client/italy-market-pulse.js`): frumento tenero · mais · frumento
duro · olivo · vite · pomodoro · barbabietola · melo.

## As cinco fontes

### 1 · ISMEA Mercati — `IT-T10-001` (fonte registada, status NEW; nada dela no acervo)

| | |
|---|---|
| sem login | páginas HTML com tabela, uma por produto: **médias nacionais** (semanais e mensais) e **cotações por praça** (`IDPagina/3111/ISUQC5/<praça>/…`). Os bancos «BD prezzi origine» e «BD prezzi ingrosso» por praça são interativos (só navegador). Sem API. |
| formato | HTML (tabela) + botão Excel; relatórios em PDF |
| frequência | semanal (praça e média semanal) · mensal (média mensal) |
| culturas do casco | **7 de 8**: frumento tenero (853, praças 3111), mais (853), frumento duro (854; CUN 13899; Foggia 3111), olivo (654 mensal origem, 656 atacado), vite (960/961 médias, 956 por praça), pomodoro **fresco** (501/507 — não é o de indústria), melo (558/559). **Barbabietola: não tem** (a própria busca da ISMEA não devolve filiera) |
| rota | do Brasil: GEO_IP_BLOCK. **Com VPN IT: HTTP 200** (`data/samples/IT-LASTMILE/IT-ROTA-COM_VPN_IT.json`, 2026-09-02) |
| fixtures no repo | 54 citações literais em `build/ITALY-REALITY-HANDOFF-V2/MARKET-OBSERVATIONS.json` (lidas em 02/09 por um agente — **não é acervo da Collection**). O leitor tira preço de 21. Ex.: «Bologna \| 27-08-26 \| Frumento tenero - Fino - n.s. \| 240,00 €/T \| 3,0% \| Franco magazzino - partenza» |
| o que falta | contrato de coleta (não existe); e, no leitor, **ler a tabela da ISMEA** (ver «O que o leitor ainda não lê») |

### 2 · BMTI / CUN — `IT-T10-002` (fonte registada; a coleta dá EMPTY_LIST)

| | |
|---|---|
| sem login | newsletter mensal de cereais (HTML + PDF), **Listino CUN Grano duro** semanal (PDF, URL previsível `listinicun.it/listini//11/AAAA-MM-DD_Listino CUN Grano Duro DD.MM.AAAA.pdf`), «Comunicazione prezzi» semanal por **província/praça** (PDF), análise mensal do azeite (PDF), análise anual das uvas de vinho por praça camerale (PDF), índice mensal de preços de atacado. **API WordPress aberta** `/wp-json/wp/v2/posts` (1.773 posts, sem chave) |
| formato | HTML · PDF · JSON (API WordPress) |
| frequência | semanal (CUN, Comunicazione prezzi) · mensal (cereais, azeite) · anual (uvas) |
| culturas do casco | **5 de 8**: frumento duro, frumento tenero, mais, olivo, vite (uva) |
| rota | **aberta sem VPN** (HTTP 200 nas duas rodadas de rota) |
| fixtures no repo | `data/samples/IT-SOURCE-SAMPLES/IT-T10-002/46622` (HTML inteiro): o leitor tira **265 €/t · grano duro fino · CUN · INGROSSO · luglio**; `46647` só tem o rodapé |
| o que falta | **o contrato procura o endereço errado.** `regras/italy_contracts_onboarded.json`: `INDEX_URL=https://www.bmti.it` com `LINK_PATTERN` de notícia genérica (`news\|notizie\|comunicat\|…`); as páginas de preço são `/prezzi-cereali/<id>/`, `/olio-doliva-prezzi-e-analisi-di-mercato/<id>/` → EMPTY_LIST na BCR-2026-09-20. Trocar a entrada para a API (`?categories=30` = cereais) ou para esses caminhos |

### 3 · Borse merci das Câmaras de Comércio (CCIAA)

| | |
|---|---|
| quem | **Bologna** (`IT-T10-009`, registada, READY) · **Granaria — Borsa Merci di Milano** (`CAND-0157`, candidata EM_ANALISE) · **Vercelli/Novara** (pno.camcom.it) e **Pavia/Mortara** (paviaprezzi.it) — estas duas **não estão** na `FONTES-CANDIDATAS.json` |
| sem login | Vercelli: listino n.30 de 01/09/2026 em PDF; Pavia: CSV oficial de 31/07/2026 (handoff V2, `crop-summary-riso.md`). Milano: páginas `…/listino/<nome>-<data>/` públicas (o crawl achou `listino-bioenergetico-2026-09-08`); há uma «AREA MERCATO» **com login** (CAND-0496). Bologna: NAO SEI onde está o listino |
| formato | PDF (Vercelli/Novara) · CSV (Pavia) · HTML (Milano) · Bologna NAO SEI |
| frequência | semanal (sessões de bolsa; a API da Comissão Europeia devolve Bologna/Verona/Milano por semana) |
| culturas do casco | frumento tenero, mais, frumento duro (Bologna, Milano — pelas cotações que a Comissão Europeia republica); Vercelli/Pavia são **arroz**, que **não** é cultura do casco |
| fixtures no repo | nenhuma de listino. `IT-T10-009/MANIFEST.json` guardou a página «Servizio ispettivo», não preço |
| o que falta | **Bologna colhe o sítio errado**: o contrato lê `https://www.bo.camcom.gov.it/it/blog` (notícias da Câmara), não a Borsa Merci — a corrida «com sucesso» trouxe notícia, não preço. Milano: registar a fonte e fazer receita de listino. Vercelli/Pavia: entrar na fila só se o arroz entrar no casco |

### 4 · Mercati all'ingrosso ortofrutticoli (Italmercati, CAAB Bologna, …)

| | |
|---|---|
| no repo | **nada**: `Italmercati`, `CAAB`, «mercato all'ingrosso» — 0 ocorrências fora das minhas. Os dois caminhos conhecidos no repo são indiretos: o «BD prezzi ingrosso» da ISMEA (por praça, só navegador) e a «App prezzi ortofrutta ingrosso» da BMTI |
| culturas do casco | as que só o atacado de fruta e verdura cobre: **melo** e **pomodoro fresco** — NAO VERIFICADO |
| o que falta | tudo: medir se publicam listino aberto, formato e frequência. O comando abaixo é o primeiro pedido |

### 5 · Clal

| | |
|---|---|
| no repo | **nada** (0 ocorrências). Pelo que sei fora do repo, é um portal de **lácteos** (leite, queijo, manteiga) e parte é paga — **NAO VERIFICADO** |
| culturas do casco | NAO SEI; provavelmente nenhuma (o casco não tem lácteos). Talvez mais/soja como ração — NAO VERIFICADO |
| o que falta | um pedido para ver o que é aberto. **Prioridade baixa** para o casco |

**Fora da lista, mas já no casco:** a API do *EC Agri-food Data Portal* é a fonte dos 77 preços que o casco
mostra hoje, e **não é fonte registada da Collection** (não está em T10 nem nas candidatas;
existe `coleta/agrifood_ue.py`). Atenção à independência (INT-LAW-071): os preços italianos que ela publica
vêm das mesmas borse merci (Bologna, Verona, Milano) — não conta como segunda origem delas.

## Comandos — 1 pedido por fonte, só quando o domínio está livre há 24 h

Pedido da coordenação (26/09 22:05). **Um comando só**, que confere e depois pede:

```bash
bash scripts/polso_mercato/um_pedido_por_fonte.sh               # confere os livros vivos e pede SÓ aos livres
bash scripts/polso_mercato/um_pedido_por_fonte.sh --so-conferir # só a conferência, sem rede
```

O que ele faz, por ordem:

1. **Confere os livros vivos** (só leitura) com `scripts/polso_mercato/dominio_livre_24h.py`: a árvore do
   robô (`source-curator-service-v1`) e a da ponte (`ponte-viva`). Procura o domínio escrito **e** os IDs que
   o representam (o coletor escreve o ID, não o URL — a Granaria tem 11 SOURCE_ID na alocação viva:
   IT-T10-023/025–030/034–036/044 e IT-T7-079). Um registo só conta se tiver carimbo ISO nas últimas 24 h.
2. **Pede uma vez a cada domínio LIVRE nos dois livros** (curl GET, sem login, 60 s), guarda os bytes e o
   sha256 em `C:/Users/London1/auditoria-madrugada/polso-fontes/<data-hora>/`. Domínio ocupado é saltado com
   a hora em que fica livre.
3. **Lê sem rede** cada ficheiro com o leitor de preço.

**Falha fechada**: se a conferência do robô não produzir resultado, **nenhum** pedido é feito; um domínio
que a conferência não conhece também não é pedido. Os três defeitos que o teste sem rede apanhou e que
estão consertados: o caminho `/c/...` que o Python do Windows não lê; a conferência que morria e deixava o
resto seguir (tudo contaria como livre); e o leitor a reler os próprios `.precos.json`.

### A conferência de hoje (27/09, 10:44 de Brasília — janela desde 26/09 10:40)

| domínio | robô | ponte | pode pedir? |
|---|---|---|---|
| ismeamercati.it | livre | livre | **sim** — precisa VPN IT |
| bmti.it | livre | livre | **sim** |
| granariamilano.it | **OCUPADO** — 12 registos, o último 26/09 22:29:39Z (`LIFECYCLE-LEDGER-V1`: reparo do IT-T10-030, `…/newsletter/febbraio-2026/`) | livre | **só depois de 27/09 22:29:39Z = 19:29:39 de Brasília** |
| italmercati.it | livre | livre | **sim** (URL NAO VERIFICADO) |
| clal.it | livre | livre | **sim** (URL NAO VERIFICADO) |

Provas: `scripts/polso_mercato/DOMINIO-LIVRE-24H-ROBO-20260927.json` e `…-PONTE-20260927.json`
(1.612 ficheiros lidos na árvore do robô).

**O que esta conferência NÃO vê:** pedidos feitos fora destes livros (outra sessão, `curl` à mão, o coletor
de outra worktree) — «LIVRE» quer dizer «os livros lidos não registam», não «ninguém pediu». E a hora
de hoje fica velha: o comando **refaz a conferência na hora em que corre**; esta tabela é só a foto de hoje.

Os URL, um por domínio (estão no script):

| domínio | URL | o que se espera |
|---|---|---|
| ismeamercati.it | `https://www.ismeamercati.it/flex/cm/pages/ServeBLOB.php/L/IT/IDPagina/853` | preços de cereais (frumento tenero, mais) |
| bmti.it | `https://www.bmti.it/wp-json/wp/v2/posts?categories=30&per_page=1` | a última análise de cereais (JSON) |
| granariamilano.it | `https://www.granariamilano.it/listino/` | índice dos listini — NAO VERIFICADO |
| italmercati.it | `https://www.italmercati.it/` | página inicial — NAO VERIFICADO |
| clal.it | `https://www.clal.it/` | página inicial — NAO VERIFICADO |

## O que o leitor ainda não lê (medido nas fixtures reais)

Passado nas 54 citações da ISMEA: tira preço de 21, e **0** com as quatro chaves. Não é a fonte que falha — a
linha da ISMEA escreve praça, data e unidade. É o leitor:

1. **Praça na primeira coluna da tabela** («Bologna | 27-08-26 | … | 240,00 €/T») não é lida: o leitor só
   conhece «mercato di X», «borsa merci di X», «CUN».
2. **Período «2026-8-4»** (ano-mês-semana da ISMEA) não é lido.
3. **Unidades** «€/100Kg» (Comissão Europeia) e «€/Ettogrado» (vinho da ISMEA) não são reconhecidas.
4. **JSON** (API da Comissão e do WordPress da BMTI) precisa de leitor estruturado, não de texto.

Nenhum destes foi mexido aqui: a missão era a lista de fontes, e o leitor está na fila do lote 4 com o SHA
`940b6d359`. Ficam como o próximo passo do leitor, com as linhas reais acima como casos de teste.

## EM PALAVRAS SIMPLES

Hoje a única fonte de preço que a coleta guarda é o myfruit. Ele fala de preço, mas nunca diz **em que
mercado**: é como saber que o tomate custa 3 reais sem saber se foi na feira ou no supermercado. Das 82
fichas de preço que tirei dele, 0 dizem o mercado.

As fontes que dizem o mercado já são conhecidas, e duas já estão cadastradas:
- **ISMEA**: cobre 7 das 8 culturas do casco (falta a beterraba). Só abre com a VPN italiana.
- **BMTI**: abre sem VPN. A coleta dela está procurando na gaveta errada: procura notícias, e os preços
  estão noutra pasta do site.
- **Bolsa de Bologna**: também está cadastrada, mas o robô lê o blog da Câmara de Comércio, e não a tabela
  de preços.
- **Atacados de fruta e Clal**: o repositório não sabe nada deles. Deixei um comando de 1 pedido para cada.

Deixei um comando só. Antes de pedir, ele olha nos livros do robô se alguém visitou o site nas últimas 24
horas; se visitou, não pede e diz a hora em que fica livre. Hoje, 4 dos 5 sites estão livres; a Bolsa de
Milão só fica livre às 19:29 (Brasília), porque o robô passou lá ontem às 19:29.
