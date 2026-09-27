# SCRAP-EVOLUCAO-V1 — o que o Scrapling tinha de bom, como peças da coleta canónica

> Ordem do dono D89 (26/09 19:48), revista pela coordenação às 19:58 (`ESTUDO-SCRAPLING-UNIAO.md`, que vale
> mais) e acrescida às 20:25 (peça 6). Ramo `scrap-evolucao-v1`, a partir do vivo `dc0de726`.
> **Sem segundo coletor, sem motor de crawl, zero dependência nova.** Nada instalado; o mapa foi só
> declarado (`architecture.declared.json`), não regenerado.

## As peças

| peça | estado | onde |
|---|---|---|
| **A** descoberta por FEED (prioridade 1) | feita, provada com o coletor de verdade | `regras/motor_de_rota.mjs` (`FEED_DISCOVERY`), `coleta/italy_pilot_collect.mjs` |
| **B** cara de navegador, degrau (a) biblioteca padrão | feita, opcional por fonte | `regras/ROTA-NAVEGADOR.json`, `coleta/rota_navegador.py`, `curadoria/canario.py`, `curadoria/colher_prova_territorio.py` |
| B degrau (b) `curl_cffi` | **não feito** — só se um alvo medido o pedir | — |
| **C** sanitizar | **saiu da coleta**; nada se apaga do texto nem do RAW. Marcar texto escondido na entrada da Intelligence **não foi feito** (opcional; fora da coleta) | — |
| **D** ligações canónicas | feita e medida no acervo | `curadoria/colher_prova_territorio.py` |
| **E** espera com castigo | feita só onde faltava (`fila.py` já cumpria Retry-After) | `coleta/espera_por_dominio.py`, `coleta/scrap_http.py`, `colher_prova_territorio.py` |
| **F** `captura_xhr` | feita, provada com Chrome de verdade contra servidor local | `ferramentas/captura_xhr.py` |
| **6** navegador real (acréscimo 20:25) | **declarada e desligada** até a emenda `COL-LAW-220` | `coleta/scrap_capacidades.py`, `docs/sintonia-scrap/SCRAP-EVOLUCAO-P6-NAVEGADOR-REAL.md` |

### A · FEED_DISCOVERY
- Medido no acervo (sem rede): **14 de 44** fontes com páginas HTML guardadas anunciam feed no `<head>`
  (`provas/scrap_evolucao/FEEDS-NO-ACERVO.json`).
- O motor lê o feed (RSS e Atom, só biblioteca padrão). Filtra: mesmo site, sem paginação, sem feed de
  comentários, `LINK_PATTERN` se houver. Entrega no máximo 3 alvos (D40). Cabe no teto: robots + feed + 3 = 5 (D38).
- A data vem de `pubDate`/`dc:date`/`published` → `PUBLISHED_AT`, com a base «nível índice; nunca
  FACT_TIME». `updated` **não** conta como publicação. Item sem data → `PUBLISHED_AT = NAO SEI` com o porquê.
  `FACT_TIME` continua `UNKNOWN`.
- Provas: `regras/feed_discovery_test.mjs` 9/9. `provas/feed_local.mjs` 4/4: o coletor real contra um
  servidor local, que contou exatamente **5 pedidos**. `regras/motor_de_rota_test.mjs` 68/68: o teste que
  fixava 4 estratégias passou a 5, de propósito.
- **Nenhum contrato foi mudado para FEED_DISCOVERY.** Trocar é depois da medida com rede (comando abaixo).

### B · a rota com cara de navegador
- **Achado:** o coletor web já pedia com Chrome 140 + `it-IT`. O canário e a prova de território pediam
  com `Chrome/125.0` **sem** `Safari/`. Uma fonte que filtre pela cara do pedido deixava passar um e
  barrava o outro. Agora o UA tem **um dono**, `regras/ROTA-NAVEGADOR.json`, lido pelo Node e pelo Python.
- É opcional por fonte: `ACQUISITION.ROTA_HTTP = "NAVEGADOR"` no contrato, ou `ROTA_HTTP` na ficha da
  prova de território. Sem o campo, nada muda (`DECLARADA`).
- A rota fica na proveniência: o resultado do canário e cada PROVA levam `ROTA_HTTP` e
  `ROTA_HTTP_DESCRICAO`, que cita `COL-LAW-704`. A lei não foi repetida: `scrap_http.py` ganhou uma nota a
  dizer que, para material público, a frase «não finge ser navegador» foi substituída pela `COL-LAW-704`.
- **Referer desligado:** a ficha não tem Referer, e há um teste que o impede de voltar.
- `scrap_http.py` continua a identificar-se com o seu AGENTE (é o portão do censo social).

### D · ligações
Comparação nas páginas HTML do acervo vivo (**423** hoje; a missão falava em 371 — o acervo cresceu).
Sem rede; cada página foi lida com o endereço de onde veio. Resultado em `provas/scrap_evolucao/LINKS-NO-ACERVO.json`.

| | antes | depois |
|---|---|---|
| ligações encontradas | 26.000 | 18.336 |
| `<link>` (estilo, ícone, feed) tratado como página | 7.313 | 0 |
| `<use>` (ícone SVG) tratado como página | 50 | 0 |
| `&amp;` não desfeito (o antigo pediria endereço que não existe) | 136 | 0 |
| a mesma página em duas grafias (fica uma) | 364 | — |

- **A escolha da prova muda em 113 das 423 páginas, em 7 sites.** Em **111** o antigo gastava um pedido
  do teto num ficheiro que não é página (ex.: um CSS «combine» do myfruit.it). Nas outras 2, o antigo
  cortava o endereço no apóstrofo (`come-si-legge-un&`) e o novo acerta.
- Das 56 que só o antigo via e o novo não vê, a amostra lida mostra só não-páginas: `data-href` de
  anúncio (`clickhere.jsp`) e `.css`.
- PDF passa sempre pelo extrator. ⚠️ A regra seguinte, `_parece_conteudo`, continua a pôr PDF de lado
  como «conteúdo» da prova de território. **Não mexi:** é outra decisão.

### E · espera com castigo
- Depois de 403, 429, 503 ou ligação cortada (WinError 10054), a espera **daquele domínio** dobra, até 120 s.
- `Retry-After` é cumprido, em segundos ou como data. Se pedir mais que o máximo, a peça marca `DESISTIR`.
- Uma resposta boa desce a espera para metade, nunca abaixo da base.
- **Nunca gera pedido a mais:** esperar não é tentar de novo.
- No `scrap_http` a pausa normal continua 1 s. Na prova de território continua 3 s.

### F · captura_xhr
- O Chrome abre a página **uma vez**. Cada pedido dele passa por um porteiro **antes de sair**:
  - imagem, fonte, CSS e mídia nunca saem;
  - o resto conta no teto do domínio, e o robots também conta;
  - passado o teto, o pedido é recusado e não sai da máquina.
- As respostas JSON viram uma **proposta** `STATIC_ENDPOINT`. Só um GET com 200 vira proposta.
  - O dono confirma com 1 pedido HTTP sem navegador.
  - Daí em diante, os bytes vêm do servidor: o RAW continua honesto.
- Perfil novo e vazio a cada corrida: nenhum cookie de ninguém.
- Prova com Chrome de verdade, sem internet: com o teto em 3, o servidor viu **só** `/` e `/api/notizie.json`.
  CSS, imagem e os JSON seguintes nunca chegaram lá.

### 6 · navegador real (patchright), acréscimo 20:25
- Declarada `web.page.browser_rendered`: `PARTIAL` (uma corrida, uma classe), `LOCAL / BROWSER_REAL_REQUIRED`.
- O corpo tem o rótulo `BROWSER_RENDERED_EXTRACT` (`COL-LAW-007`). O validador recusa uma página desenhada
  sem esse rótulo.
- Só para as fontes medidas: IT-T9-002, IT-T9-003, IT-T9-008.
- **Está desligada:** `promete_resultado` responde NÃO até `COL-LAW-220` entrar em `EMENDAS_EM_VIGOR`.
- ⚠️ **NÃO SEI se a COL-LAW-220 já foi aprovada.** Só a encontrei como **texto proposto**
  (`ESTUDO-ORQUESTRACAO-24H-LUCIANO.md`: «aprovadas para PROPOR»). Não está na Bíblia deste ramo nem no
  `lei-pesquisadores-v1`.
- Memória por página, medida aqui sem internet (é um **piso**, `RAM-NAVEGADOR.json`):

| instante | memória em uso | memória só do navegador |
|---|---|---|
| navegador vazio | 344 MB | 260 MB |
| com uma página | 485 a 796 MB | 278 a 316 MB |

- O patchright **não** entrou no repositório; a medida usou `C:/g/scrapling-estudo/.venv-full`.

## Provas
- Testes novos: `tests/test_scrap_evolucao.py` 37 · `tests/test_captura_xhr.py` 8 (1 com Chrome) ·
  `tests/test_feed_discovery.py` 2 (corre os dois ficheiros Node). Todos passam.
- **Mutação: 26 de 26 mortos** (`provas/scrap_evolucao/MUTANTES.json`). Cada regra nova foi estragada de
  propósito e algum teste acusou. Os bytes originais foram repostos e conferidos por sha256.
- Vizinhos:
  - 33 suítes do Scrap (`tests/test_c1*`, `test_scrap_*`, `test_as_duas_portas_do_scrap`) dão **o mesmo
    resultado que em `dc0de726`**, linha a linha.
  - Os vermelhos dessas suítes já existiam no vivo: falta `yaml` nesta máquina; `mutacao.py` em três gavetas.
  - 8 suítes da curadoria (canário, prova de território, boletins, receitas): OK.

## Comandos para a coordenação (com rede, VPN IT)

⚠️ Cada comando grava um recibo. As rodadas leem-no, e **o domínio fica 24 h fechado para a coleta**.

**Piemonte — a página que devolvia 52 bytes, com a rota nova: robots + 1 pedido:**
```
py coleta/rota_navegador.py --medir=https://dashboard01.green-planet.it/ --livros=<pasta das ondas> --recibos=C:/Users/London1/auditoria-madrugada --saida=C:/Users/London1/auditoria-madrugada/scrap-evolucao/piemonte
```
Sucesso = `HTTP 200` com `BYTES` bem acima de 52 e a página inteira em `CORPO.bin`.

**Os 14 feeds — 1 pedido por fonte (+ robots):**
```
py provas/scrap_evolucao/medir_feeds_com_rede.py --livros=<pasta das ondas> --recibos=C:/Users/London1/auditoria-madrugada --saida=C:/Users/London1/auditoria-madrugada/scrap-evolucao/feeds
```
Resposta em `MEDIDA-FEEDS.json`: itens, itens do próprio site, itens com data de publicação.
Obs.: IT-T5-186 (ENEA) só anuncia o feed de **um** evento.

**captura_xhr — IT-T7-164 (pecorinoromano.com) e IT-T3-008 (agrometeopuglia.it):**
```
py ferramentas/captura_xhr.py --url=https://www.pecorinoromano.com/ --source-id=IT-T7-164 --livros=<pasta das ondas> --recibos=C:/Users/London1/auditoria-madrugada --saida=C:/Users/London1/auditoria-madrugada/scrap-evolucao/xhr-T7-164
py ferramentas/captura_xhr.py --url=https://www.agrometeopuglia.it/bollettini --source-id=IT-T3-008 --livros=<pasta das ondas> --recibos=C:/Users/London1/auditoria-madrugada --saida=C:/Users/London1/auditoria-madrugada/scrap-evolucao/xhr-T3-008
```
- Abre o Chrome com janela e perfil novo.
- No máximo 5 pedidos por domínio, contando o robots.
- `PROPOSTAS` traz o endereço do JSON, se houver.
- ⚠️ Nomes de fora (analytics, CDN) contam no **teto deles**, não no da fonte; saem no recibo.
- `<pasta das ondas>` = a mesma que as rodadas usam em `--livros-do-dia`.

## O que falta (não é desta missão)
- Trocar contratos para `FEED_DISCOVERY` e marcar fontes com `ROTA_HTTP = NAVEGADOR`: depois das medidas com rede.
- `curl_cffi` (degrau b): só se um alvo medido falhar com cabeçalhos.
  O pacote já descarregado está em `C:/g/sintonia-libs-evo`, 5,6 MB, fora do repositório e não usado.
- Peça 6: a emenda, a dependência e o adaptador.
- Marcar texto escondido na entrada da Intelligence (peça C, opcional).

## EM PALAVRAS SIMPLES

**Feed (a novidade principal).** Muitos sites têm uma "lista de novidades" automática, chamada feed. É
como o cardápio do dia pregado na porta do restaurante: em vez de entrar e procurar prato por prato, a
gente lê o cardápio. Contei nas páginas que já temos: **14 de 44 sites** têm esse cardápio. O robô agora
sabe ler o cardápio e pegar as 3 notícias mais novas, sem passar do limite de 5 visitas por site. A data
que o cardápio mostra é a **data em que a notícia foi publicada**, não a data do que aconteceu na lavoura.
Quando o cardápio não diz a data, o robô escreve "NÃO SEI".

**Cara de navegador.** Alguns sites só abrem para quem chega "parecendo" um navegador comum. O robô
principal já chegava assim. Os ajudantes (o que testa fontes e o que junta provas) chegavam com outra
cara, e podiam ser barrados onde o robô passava. Agora todos usam a mesma cara, escrita num lugar só. Ela
só é usada quando a fonte pede, e o registro sempre diz que foi usada. Não fingimos ter vindo do Google.

**Links.** Quem junta provas agora só segue links em que uma pessoa clicaria. Antes, em 111 páginas, ele
gastava uma das 5 visitas num arquivo de enfeite do site (cor, ícone). Isso acabou.

**Paciência.** Se um site diz "calma, volte depois", o robô agora espera o dobro, ou o tempo que o site
pediu. Ele nunca bate mais vezes por causa disso.

**Páginas feitas com JavaScript.** Algumas páginas chegam vazias e se montam sozinhas no navegador,
buscando os dados numa "gaveta" escondida. A ferramenta nova abre a página uma vez no Chrome, descobre
onde fica essa gaveta e anota o endereço. Depois o robô busca direto na gaveta, sem navegador. Testei com
o Chrome de verdade, sem internet, e o limite de visitas funcionou.

**Navegador "disfarçado" (peça 6).** A coordenação provou que ele abre ADAMA, Bayer e Syngenta. Deixei
isso escrito no lugar certo, mas **desligado**. A regra que autoriza (COL-LAW-220) ainda está só
proposta — pelo menos em tudo que eu consigo ler. Cada página nesse navegador gasta perto de **meio a
quase 1 GB de memória**, e isso é o mínimo; com internet, gasta mais. O que ele devolve fica marcado como
"página desenhada pelo navegador", que é diferente do arquivo original do site.

**Nada foi apagado.** A ideia de "limpar texto escondido" foi abandonada. Ela apagaria justamente as
linhas que avisam de pragas.

**Conferência.** Estraguei de propósito cada regra nova, uma de cada vez: **26 de 26** estragos foram
pegos pelos testes. Os testes antigos deram o mesmo resultado de antes.
