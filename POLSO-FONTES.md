# POLSO-FONTES — as fontes públicas de preço que faltam

Missão da coordenação, 17:35. Ramo `nuvem-polso-mercato-v1`, sobre `940b6d359` (POLSO-DI-MERCATO).
**PRONTO-SEM-MAPA**: há um script novo (`scripts/polso_mercato/medir_fixtures.py`) sem peça no mapa (P9
pendente; é da peça `C-PRECO-DE-MERCADO`). Sem rede: tudo o que segue foi lido **no repo**. Onde o repo não
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

## Comandos — 1 pedido por fonte, para correr com a VPN IT

Um `curl` por fonte, só leitura, sem login, com os bytes guardados e o sha256 ao lado. Depois, o leitor lê o
ficheiro **sem rede**. Pasta sugerida: `C:/Users/London1/auditoria-madrugada/polso-fontes/`.

```bash
OUT=C:/Users/London1/auditoria-madrugada/polso-fontes; mkdir -p $OUT
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36"
pede() { curl -sS -L -A "$UA" --max-time 60 -o "$OUT/$1" -w "$1 HTTP=%{http_code} BYTES=%{size_download} URL=%{url_effective}\n" "$2"; sha256sum "$OUT/$1"; }

# 1 · ISMEA — preços de cereais (frumento tenero + mais), médias e praças      [precisa VPN IT]
pede ismea-853.html "https://www.ismeamercati.it/flex/cm/pages/ServeBLOB.php/L/IT/IDPagina/853"
# 2 · BMTI — a última análise de cereais pela API aberta (categoria 30)          [sem VPN]
pede bmti-cereali.json "https://www.bmti.it/wp-json/wp/v2/posts?categories=30&per_page=1"
# 3 · Borsa Merci di Milano — índice dos listini (endereço NAO VERIFICADO; o crawl viu /listino/<nome>-<data>/)
pede granaria-listino.html "https://www.granariamilano.it/listino/"
# 4 · Italmercati — página inicial, para achar o listino (NAO VERIFICADO)
pede italmercati.html "https://www.italmercati.it/"
# 5 · Clal — página inicial, para ver o que é aberto (NAO VERIFICADO)
pede clal.html "https://www.clal.it/"

# depois, SEM rede: o leitor de preço sobre cada ficheiro
for f in ismea-853.html bmti-cereali.json granaria-listino.html italmercati.html clal.html; do
  echo "== $f"; PYTHONIOENCODING=utf-8 py leis/preco_de_mercado.py "$OUT/$f" | py -c "import json,sys; r=json.load(sys.stdin); print(len(r['OBSERVACOES']),'observacoes'); [print(' ',o['COMMODITY'],'|',o['PRACA'],'|',o['PERIODO'],'|',o['PRECO_TEXTO'],'|',o['ESTAGIO']) for o in r['OBSERVACOES'][:5]]"
done
```

São **5 pedidos, 1 por domínio** (teto D38: 5/domínio/rodada). Nenhum destes domínios está na lista proibida
(CNR, Coldiretti, ANGA, Unaprol).

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

Deixei os 5 comandos prontos (um por site). Você roda com a VPN e depois o meu leitor lê os arquivos sem
internet.
