# FEED-LIGADO — o feed substitui o índice, sem mudar o teto 5/domínio/24 h

> Missão do Scrap Engineer (27/09, respostas 1–4). Base: produção `18461b92d`.
> Ramo: `claude/feed-discovery-italy-sources-hr8vlb`. **Offline**: nenhum site visitado, nenhum livro vivo
> editado. O que muda a produção é **um pacote + um comando** para o coordenador (§4).

## 1 · O que foi medido antes de escrever (e contradiz a premissa)

| premissa da missão | o que esta árvore mostra |
|---|---|
| «as 14 fontes NÃO têm contrato em `curadoria/italy_contracts_curator.json` (só 10)» | Aqui ele tem **574** contratos e 11 das 14 estão lá — mas **não é ele que o coletor lê**. O contrato executável nasce de `regras/italy_contracts_onboarded.json` (uma linha por fonte), expandida por `contratoGenerico()` em `regras/italy_contracts.mjs:589` (o dono). **8 das 13** têm linha nessa tabela: IT-T10-022, IT-T12-137, IT-T5-090, IT-T7-021, IT-T7-033, IT-T7-042, IT-T9-009, IT-T9-021. **Sem linha**: IT-T12-117, IT-T7-049, IT-T7-125, IT-T7-139 (e IT-T5-186). A produção tem mais linhas do que esta árvore (174 HTML_LINK_DISCOVERY lá, 141 aqui): o modo seco diz quantas lá. |
| «Conditional GET com o ETag que **já é guardado**» | **Não era guardado.** Zero ocorrências de ETag no coletor; `regras/incrementalidade.mjs:241-244` já o dizia. Passa a ser guardado agora — mas **fora** do livro de observações (§2.5). |
| «medir SITEMAP_DECLARADO no acervo» | Os três livros que guardam robots.txt guardam-no **cortado** (120, 100 e 120 caracteres) e misturam **mensagens da casa** no mesmo campo (313× «robots inacessível…», 102× «HTTP 404…»). A medida é um **piso**, com NÃO SEI ao lado (§3). |
| IT-T5-186 (ENEA) | O único feed que o site anuncia é o de **um evento**. Não é o índice da fonte: fica fora do pacote (`LIGAR: false`, com o porquê). |
| IT-T7-049 | O contrato do Curator aponta `copagri.it`; o feed medido está em `copagri.org` (outro domínio registável). O teto conta pelo host **real** do pedido; hoje a fonte não tem linha na tabela. |

## 2 · O que foi feito (ficheiro:linha)

**2.1 · FEED_DISCOVERY pela porta canónica** — `regras/ligar_feeds.py` + `regras/FEED-LIGADO-PACOTE.json`
- Seco por omissão. Só troca a aquisição de uma linha **que já existe** (`regras/ligar_feeds.py:61`); fonte sem linha sai `SEM_LINHA_NA_TABELA` (`:71`) e continua a entrar só pela ponte (portão ELIGIBLE + canário). **Não cria contrato.**
- Linha ligada: `{STRATEGY: FEED_DISCOVERY, FEED_URL, INDEX_URL}`. O `INDEX_URL` fica porque a regra V1 da capa e o plano da onda o leem; **nunca é pedido**. O `LINK_PATTERN` antigo não passa (o molde `news|notizie|…` recusaria a morada de um post WordPress). Guarda `FEED_LIGADO.ACQUISITION_ANTERIOR`; `--desfazer` repõe os bytes da tabela (provado).
- `regras/italy_contracts.mjs:602`: a linha FEED expande com a entrada no feed e `DISCOVERY_METHOD` «FEED: …».
- FEED_URL = a mesma regra da medida do coordenador (`medir_feeds_com_rede.py::feeds`), conferida por teste.

**2.2 · Corpo vindo do feed — `BODY_FROM_FEED`**
- `regras/motor_de_rota.mjs:428` lê `<content:encoded>` (RSS) e `<content type=html>` (Atom). Só sai a camada do XML (CDATA, também o CDATA partido do WordPress); **nada se limpa** (o `<script>` e o texto escondido ficam). `<description>` é resumo: não conta.
- `regras/motor_de_rota.mjs:776-779`: o teto D40 (3) conta **matérias a pedir**. O item com corpo não bate à porta: entra à parte; o livro continua a mandar nele (o CONHECIDO não volta).
- `coleta/italy_pilot_collect.mjs:1293`: item com corpo = **zero pedidos**. Observação com `RAW_EVIDENCE_STATE: "BODY_FROM_FEED"` (`:1567`) + `BODY_FROM_FEED{CAMPO, FEED_URL, FEED_SHA256, NAO_E_A_PAGINA}`, ficheiro `<matéria>.body-from-feed.html`, identidade pelo URL do item, `PUBLISHED_AT` do feed (nível índice), `FACT_TIME: "UNKNOWN"` (`:1561`). A assinatura da página não se aplica ao recorte, e por isso ele nunca se diz página.
- `coleta/italy_executor.py:230`: o executor não lê o corpo do feed como página. A admissão decide como sempre.
- Item **sem** corpo: pedido da matéria, dentro do teto, como hoje.

**2.3 · Sitemap de graça** — `coleta/italy_pilot_collect.mjs:638` guarda as linhas `Sitemap:` do robots que já é pedido; saem no resumo da corrida (`CORTESIA.ROBOTS[origem].SITEMAPS`, `:1672`). **Nenhum pedido sai por elas.** Estratégia nova: não declarada (§3).

**2.4 · Robots uma vez por domínio por 24 h** — `coleta/italy_pilot_collect.mjs:664-715`
- O robots lido fica em `<SINTONIA_TETO_24H>.robots.json` (ao lado do livro de 24 h de `coleta/reserva_24h.py`; o livro das reservas **não muda de forma** — o gémeo Python reescreve-o só com `RESERVAS[]`).
- Reusa-se só **LIDO** (o texto inteiro, relido pelo mesmo leitor) e **AUSENTE** (404/410 = sem proibição, a regra da casa desde a A5).
- **Nunca vira permissão**: ILEGÍVEL, INDISPONÍVEL, entrada velha (> 24 h), entrada sem texto, livro que não é JSON → **pede-se o robots outra vez**. ⚠️ Li «robots ausente nunca vira permissão» como «robots que não está no livro, ou que o livro não sabe dizer, nunca vira permissão». O 404 continua a valer como permissão (regra da A5); se o dono quiser o 404 como recusa, é outra decisão.

**2.5 · GET condicional** — `coleta/italy_pilot_collect.mjs:749-830`
- `If-None-Match`/`If-Modified-Since` com a cópia da última resposta 200 (bytes + ETag + Last-Modified, `data/collection-cache/italy/http/`). Um 304 devolve essa cópia, e **só** se o sha256 bater.
- **O 304 é um pedido**: sai por `umaIda()` (`:513`), reserva no livro de 24 h e conta no teto do domínio.
- Só serve a um pedido **que já ia acontecer**: o índice/feed (`:895`, revisitado sempre por lei) e a matéria que a regra já mandou REVALIDATE (`:1340`). ⚠️ **O ETag NÃO vai para o livro de observações, de propósito**: `memoriaDosDetalhes()` leria `HTTP_ETAG` e `decidirSobreDetalhe()` passaria a devolver REVALIDATE com CONDITIONAL_REQUEST_AVAILABLE para toda matéria conhecida — revisitar tudo, gastando o teto. É o contrário do pedido.

## 3 · Sitemap medido no acervo (sem rede)

`provas/scrap_evolucao/medir_sitemap_no_acervo.py` → `SITEMAP-NO-ACERVO.json`

| | |
|---|---|
| **SITEMAP_DECLARADO** | **180/279** fontes (robots inteiro ou com a linha visível) |
| NÃO SEI | **42** (texto cortado no livro, sem a linha à vista) |
| nas 13 do feed | 6 com Sitemap · 5 sem · 2 NÃO SEI |

É piso. Declarar SITEMAP como estratégia exige **caso medido** com rede: não foi feito.

## 4 · Para o coordenador: instalar e correr 1 volta (VPN IT)

```powershell
# 0) na árvore de produção (18461b92d) — se o merge recusar por ficheiro local, PARE e diga qual
git fetch origin claude/feed-discovery-italy-sources-hr8vlb
git merge --ff-only origin/claude/feed-discovery-italy-sources-hr8vlb

# 1) SECO: o que muda na tabela VIVA + a previsão medida com os corpos de 27/09 (não escreve nada)
mkdir C:/Users/London1/auditoria-madrugada/feed-ligado
py regras/ligar_feeds.py --conferir-feeds=C:/Users/London1/auditoria-madrugada/scrap-evolucao/feeds-2709 > C:/Users/London1/auditoria-madrugada/feed-ligado/SECO.json

# 2) APLICAR (troca só as linhas LIGAR; guarda o caminho de volta em cada linha)
py regras/ligar_feeds.py --aplicar > C:/Users/London1/auditoria-madrugada/feed-ligado/APLICADO.json

# 3) UMA volta, com VPN IT, só as fontes LIGAR do APLICADO.json, com o livro de 24 h das rodadas
$env:SINTONIA_TETO_24H = "<o mesmo TETO-24H.json que as rodadas usam em --teto-24h>"
py ferramentas/big_collection/onda_web.py --correr --sha256=<sha da coorte congelada> --fontes=<IDs LIGAR, separados por vírgula> --saida=C:/Users/London1/auditoria-madrugada/feed-ligado/onda-1

# 4) prova independente do teto (lê o livro de corridas, não o contador de quem é verificado)
py provas/prova_teto_dominio.py --livro data/collection-ledger/italy/runs.ndjson --onda C:/Users/London1/auditoria-madrugada/feed-ligado/onda-1/ONDA-WEB-ESTADO.json

# se algo correr mal: volta atrás byte a byte
py regras/ligar_feeds.py --desfazer
```

O que olhar no `runs.ndjson` da volta: `contadores.BODY_FROM_FEED` (documentos sem pedido),
`ROBOTS_FROM_24H_BOOK`, `NOT_MODIFIED_304`, `CORTESIA.PEDIDOS_POR_DOMINIO` (≤ 5) e `CORTESIA.ROBOTS[*].SITEMAPS`.
O onda_web já tem o portão de egresso IT antes/depois e o disjuntor de > 5 por domínio.

## 5 · A previsão (documentos/domínio/dia)

| | antes (HTML_LINK_DISCOVERY) | depois (FEED_DISCOVERY) |
|---|---|---|
| pedidos por domínio em 24 h | robots + índice + ≤ 3 matérias = 5 | robots + feed + ≤ 3 matérias = 5 (**o mesmo teto**) |
| documentos na 1.ª volta | ≤ 3 (medido hoje: 0,4–0,6 doc/pedido) | **C + min(3, S)** — C = itens com texto completo no feed |
| documentos por dia (regime) | min(3, publicados/dia) | **C₇/7 + min(3, S₇/7)** |
| robots re-pedido por outro processo no mesmo domínio | 1 pedido (custou 1 documento no cia.it) | 0 (livro de 24 h) → **+1 documento** |
| 304 | — | **não poupa pedido** (conta no teto); poupa bytes |

Com os números que o coordenador mediu (489 itens em 13 feeds, 179 com texto completo), a **média** é
**13,8 itens com corpo por feed**: 1.ª volta ≈ **3 + 13,8 ≈ 16,8 documentos/domínio** contra **3**. A média
esconde a distribuição (há feed com todos os itens com corpo e feed com nenhum): **por fonte, NÃO SEI aqui**
— os corpos estão só na máquina do coordenador. O passo 1 do §4 calcula-o por fonte (C, S, C₇, S₇ pelas datas
`pubDate` dos últimos 7 dias) e a soma em `PREVISAO`. ⚠️ O «antes» do regime é um **teto do índice** (supõe
que a página de índice anuncia os mesmos itens que o feed).

## 6 · Provas

- `regras/feed_discovery_test.mjs` **14/14** (9 de antes + 5 novos: corpo exato, Atom, D40 conta pedidos, livro manda no item com corpo, FACT_TIME).
- `provas/scrap_evolucao/feed_ligado_local.mjs` **12/12** — o coletor real (curl) contra servidores em 127.0.0.1, com o livro de 24 h; **quem conta é o servidor**. Três corridas: 3 pedidos (robots + feed + 1 matéria; 2 BODY_FROM_FEED) → 1 pedido (robots do livro; feed 304) → 1 pedido (feed mudou) e a matéria nova **recusada pelo teto** — o 304 contou. Servidor e livro: **exatamente 5** no domínio. Robots em HTML não dá permissão, não vai ao livro e é pedido de novo; entrada `LIDO` sem texto não é permissão; livro não-JSON não é permissão; `Sitemap:` no resumo sem pedido; validador do último bloco (não do proxy).
- `tests/test_feed_ligado.py` **8/8** (instalador, desfazer byte a byte, pacote = regra da medida, contrato expandido, previsão pelas datas, executor, sitemap Node = Python).
- **Mutação `provas/scrap_evolucao/mutantes_feed_ligado.py`: 21/21 mortos** (`MUTANTES-FEED-LIGADO.json`), bytes repostos por sha256. Os quatro da missão: feed fora do teto · BODY_FROM_FEED rotulado como página · robots ilegível = permissão · 304 fora do teto → **todos apanhados**. Um mutante sobreviveu na 1.ª ronda (a previsão: o fixture dava 3 nos dois casos) — o **fixture** foi reforçado, não a régua afrouxada.
- Vizinhos: mutação SCRAP-EVOLUCAO **26/26**; red team da cortesia **16/17 no ramo = 16/17 na base** (K6 tem âncora partida desde antes: 0 ocorrências em `18461b9`). Uma âncora que **eu** parti (K8, passou a aparecer 2×) foi consertada no meu código, não na prova.
- ⚠️ Herdado, não mexido: `provas/teto_dominio_mutacao.py` M7 com âncora partida já em `18461b9`.

**Bateria inteira por nome** (`provas/integra_noite/bateria_inteira_por_nome.py`, worktrees limpas):

| | base `18461b9` | ramo `5fd3656` |
|---|---|---|
| ficheiros de teste | 393 | 394 (+ `tests/test_feed_ligado.py`) |
| testes corridos | 7.373 | 7.381 |
| ficheiros vermelhos | 77 | 77 |
| falhas por nome | 334 | 337 |

A parte `system-map/` da base foi corrida **duas vezes** (na 1.ª eu corri o red team da cortesia na mesma
worktree enquanto ela corria — podia estar contaminada); vale a 2.ª, limpa. Comparação **pelo nome**:

- **NOVA e minha, consertada:** `regras/paridade_test.mjs` «a DECISAO vem ANTES do download». O teste procura o
  texto `await baixar(alvo.url)`, e a chamada ganhou argumentos (§2.5). **Ajuste DECLARADO no teste**
  (`regras/paridade_test.mjs:274-277`, com o comentário a citar esta decisão): a âncora passa a ser o prefixo da
  mesma chamada (uma só ocorrência). Provado que a guarda **continua a morder**: com o download posto antes da
  decisão, o teste reprova. Depois do ajuste: 28/0.
- **Varia entre corridas, não é deste ramo:** `system-map/tests/test_topologia_persistida.py` (5 nomes no ramo;
  na base, 3 na 1.ª corrida e 0 na 2.ª). Sozinho, numa worktree limpa: **129 provas · 0 falhas na base e no
  ramo**. Depende do estado da árvore deixado pelos testes anteriores da mesma corrida serial.
- **Saíram (não fui eu que as consertei; também variam):** `test_impressao_verificavel.py` (variou entre as
  duas corridas da base) e `tests/test_o9_caminho_instrumentado.py`.
- **Nenhuma outra falha nova.** As restantes 331 são herdadas, com o mesmo nome.

**System Map**: `correr_a_cadeia.py REGERAR` → `VALIDAR` = **SYSTEM_MAP_CHECK=PASS**; commit dos gerados;
`impressao_da_arvore.py --conferir-carimbo` = **IGUAL**. Não recarimbei (`--stamp`): C-IT-CONTRATOS já estava
PENDING por mudanças anteriores de outros, e carimbar diria que reli o que não reli.

## 7 · Limites (NÃO SEI)

- A versão do curl da produção: NÃO SEI — por isso os cabeçalhos da resposta vêm por `-D` (todas as versões), não por `%header{}` (≥ 7.84).
- Os números por fonte: NÃO SEI aqui (§5).
- As ferramentas do Curator (canário, `importar_do_coletor`) falam HTML_LINK_DISCOVERY: não provam uma linha FEED (saem `CANARIO_NAO_PROVA`). O caminho de volta é `--desfazer`.
- Se a página de uma matéria for pedida depois do corpo do feed (só por REVALIDATE), o mesmo DOCUMENT_ID pode sair DOCUMENT_CHANGED_IN_PLACE (feed ≠ página). Não medido.

## EM PALAVRAS SIMPLES

Cada site pode receber **5 visitas por dia**, e isso não mudou. Antes, o robô gastava uma visita para ler as
regras do site, outra para abrir a página de notícias, e as outras três para abrir três notícias: no máximo
**3 notícias por site por dia**.

Agora, em 8 sites (contados nesta cópia do projeto; na produção o comando seco diz quantos — 4 ainda não têm
contrato pronto, e o da ENEA não tem lista de verdade), em vez da página de notícias o robô lê o **feed** — a lista automática de novidades. Em muitos feeds a notícia **já vem
inteira dentro da lista**. Essas o robô guarda **sem gastar visita nenhuma**, com uma etiqueta que diz
«veio do feed, não é a página». As que vêm só com o título continuam a ser abertas, até 3.

As regras do site (o robots) passam a valer **por um dia**: se outro robô da casa já as leu hoje, não se pede
de novo — e isso devolve uma visita. Mas se as regras não puderem ser lidas, o robô **não entra**.

E quando o robô volta ao feed, pergunta «mudou alguma coisa?». Se não mudou, o site responde curto — mas essa
pergunta **também conta como visita**. Não se faz batota com o limite.

Resultado esperado: na primeira volta, perto de **17 notícias por site em vez de 3** (é uma média; site a site
só se sabe quando o coordenador correr o comando com os feeds que ele já baixou). Nenhum texto foi limpo nem
apagado.
