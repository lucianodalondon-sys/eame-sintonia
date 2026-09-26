# COLETA-CONTINUA — a coleta como serviço do vivo, 24 horas por dia (D86)

Ordem do dono (D86, `auditoria-madrugada/DECISOES-DONO-2026-09-23.md`): «o sintonia no futuro não vai parar
de rodar coleta 24 horas por dia, já se organize pra isso». **Desenho, não código.** Ramo
`coleta-continua-v1` sobre o vivo `dc0de726`. Sem rede, nada instalado. Os números são medidos (fonte
dita), e o que não se mediu diz NÃO SEI.

## 1. O que a noite de hoje ensinou (medido)

- **A rodada é a unidade errada.** O plano das 15 rodadas mete uma fonte de edagricole.it em **cada**
  rodada (edagricole tem 15 das 64 fontes). Com a janela de 24 h por domínio (D79), depois da R1 as
  R3–R15 ficam **todas** presas até ao dia seguinte, porque todas têm edagricole (e a R3–R5 também
  cia.it). Resultado: com rodadas, corre **1 por dia**. A unidade certa é a **fonte**, e a regra é **por
  domínio**.
- A janela já existe e está provada: `rodadas.ultima_visita_por_dominio` (ondas + recibos de outras
  missões + todos os domínios que a fonte toca) e `janela_fechada`. A ordem pelo rendimento também:
  `prioridade_do_rendimento`. O serviço **reutiliza** estas peças, não as copia.

## 2. O serviço: uma volta curta, repetida (sem arquitetura paralela)

**Onde vive:** um verbo novo no `ferramentas/big_collection/rodadas.py`, `--continuo --uma-volta`, que o
**agendador do Windows** chama a cada 15 min. É o mesmo mecanismo da tarefa `\SINTONIA-Italy-ForwardOnly`
que já existe. Não há um segundo supervisor nem um segundo coletor. A volta chama o `onda_web.py
--correr --fontes=<UMA>` de hoje, que chama o `micro_coleta` e o orquestrador de sempre.

**Porque uma volta curta e não um processo eterno:** hoje o PC reiniciou duas vezes (09:47 e ~10:20).
Uma volta sem estado em memória recomeça sozinha na tarefa seguinte. Tudo o que importa está nos livros.

**Uma volta, por ordem (a mesma do RODADA1-ROTEIRO, mas para UMA fonte):**

| # | passo | se falhar |
|---|---|---|
| 1 | trinco da volta (`COLETA-CONTINUA.lock`, com PID e hora; órfão > 30 min = aviso, não se apaga sozinho) | sai calado (outra volta a correr) |
| 2 | travões: `COLETA-CONTINUA-PARADA.flag` existe → sai; RAM livre < 5 GB → sai **sem** latch (tenta na próxima); `LOCK-PRIORIDADE.txt` de outro dono → sai | ver secção 4 |
| 3 | **escolher a próxima fonte** (`proxima_fonte`, função pura): da coorte congelada, as fontes cujos **todos** os domínios estão há ≥ 24 h sem pedido; entre elas, a de menor classe de prioridade (rendimento) e, no empate, a atendida há mais tempo (ordem justa) | nenhuma livre → sai, anota `NADA_LIVRE_ATE=<mais cedo>` |
| 4 | portão IT de consenso, `--sem-cache`, cache nova | **latch** (§4) |
| 5 | backup, se o último tiver mais de 24 h (§5) | **latch** |
| 6 | a corrida: `onda_web.py --correr --fontes=<SID> --saida=<ONDAS>/CONTINUA/<AAAAMMDD>/<HHMMSS>-<SID>`, com um livro do teto novo | o disjuntor da onda → latch |
| 7 | portão IT depois | **latch** |
| 8 | prova-teto independente da volta (`provas/prova_teto_dominio.py`) **e** do dia (soma dos livros das últimas 24 h por domínio ≤ 5) | FAIL ou NAO_SEI → **latch** |
| 9 | reconciliar a Sala, só SELECT (as funções do NOITE-CONTINUA, que bateram na 3.ª onda: raw 76 = 76, sala 14 = 14) | não bate → **latch** |
| 10 | uma linha em `<ONDAS>/CONTINUA/CONTINUA-<AAAAMMDD>.ndjson`: fonte, domínios, pedidos, docs novos, Sala antes/depois, portões, prova, porquê | — |

**Uma fonte por volta** mantém cada volta curta (na 3.ª onda: 10–74 s por fonte), e o robô nunca espera.

## 3. Conviver com o robô de fontes, sem o PARAR horas

Medido no vivo (`dc0de726`), quem escreve em que livro:

| livro | robô (curadoria/*) | coleta (coleta/, admissao/, micro_coleta) |
|---|---|---|
| `curadoria/LIFECYCLE-*`, `READY-*`, `SOURCE-*`, `FONTES-CANDIDATAS` | **escreve** | **lê** (o portão da coleta) |
| `data/collection-ledger/italy/runs.ndjson`, `observations.ndjson` | não | **escreve** |
| `data/samples/LIVRO-DE-DECISOES.json` (Admissão) | não | **escreve** |
| a Sala (Postgres) e o armazém | não | **escreve** |
| `regras/italy_contracts_onboarded.json` | **escreve** (só ferramentas de onboarding: 8 ficheiros em `curadoria/`) | lê (e 4 ferramentas de ensaio) |

- **A leitura do portão é segura sem parar o robô.** O `LIFECYCLE-LEDGER` é escrito atomicamente
  (`curadoria/lifecycle.py::_gravar`: temporário, fsync, `os.replace`). Um leitor nunca apanha meio
  ficheiro.
- **Os outros livros do robô: NÃO SEI.** Só 8 de 147 ficheiros de `curadoria/` usam `os.replace`. Antes de
  instalar, medir quais dos livros que o portão lê são escritos sem troca atómica. Onde não for atómico,
  a volta lê com repetição (lê, espera 2 s, lê, compara o sha256) em vez de parar o robô.
- **O contrato do coletor** (`italy_contracts_onboarded.json`) é o único livro partilhado. O onboarding é
  manual. Proposta: o onboarding cria `ONBOARDING-EM-CURSO.flag`, e a volta salta enquanto existir.
- **O backup não precisa do robô parado.** O `pg_dump` lê uma fotografia consistente (MVCC do Postgres),
  e o robô não escreve na Sala.
- Conclusão: **`PARAR.flag` deixa de ser passo da coleta.** Fica para instalações e para o rollback.

## 4. Pára sozinha (latch), e quem a solta

| condição | ação |
|---|---|
| portão IT falha (antes ou depois) / VPN fora de IT | **latch** `COLETA-CONTINUA-PARADA.flag` com o porquê; nenhuma volta corre até uma pessoa apagar o ficheiro |
| prova-teto FAIL ou NAO_SEI (da volta ou do dia) | **latch** |
| backup falhado (`pg_dump` ≠ 0, ou `PROVA_VALE` falso na prova semanal) | **latch** |
| reconciliação não bate / disjuntor da onda (egresso, Sala desce, > 30 min, C6) | **latch** |
| 3 fontes seguidas FAILED | **latch** |
| RAM livre < 5 GB, Sala em baixo, LOCK-PRIORIDADE de outro | **salta a volta** (sem latch): tenta na próxima |

O latch é o mesmo mecanismo do `PARAR.flag`: um ficheiro com o porquê. Só se apaga à mão, com a decisão escrita.

## 5. Cadências

- **Backup da Sala:** `pg_dump -Fc` diário (a primeira volta depois das 00:00), 7 dias guardados, com
  sha256 e contagens. A **prova** do backup (restauro numa base descartável e md5 igual,
  `provar_backup_da_sala.py`) é **semanal**, porque é pesada e precisa da LOCK-PESADO. Hoje o roteiro faz a
  prova antes de cada rodada. Com dezenas de voltas por dia isso não cabe.
- **Intelligence:** uma vez por dia (06:00), sobre uma cópia da Sala, como a rodada 2 de hoje
  (EXPERIMENTAL / NAO_PARA_CLIENTE). O retorno dela (`R1-X-R2-E-FONTES.json`) volta a alimentar a
  `prioridade_do_rendimento` no dia seguinte.
- **Mapa:** o código do serviço entra pela cadeia do mapa como qualquer outro (peça `C-ONDA-WEB`).

## 6. Quanto rende por dia (com as 64 fontes de hoje)

Medido no plano instalado e na 3.ª onda (`ONDA3-WEB-20260925-1934`):

- **38 domínios** para 64 fontes. Os únicos com mais de uma fonte: edagricole.it 15 · cia.it 5 ·
  crea.gov.it 5 · enea.it 3 · arpacampania.it 2 · arpa.veneto.it 2.
- Com 1 fonte por domínio por 24 h: **até 38 corridas/dia e ~176 pedidos/dia** (máx. 5 por domínio).
- Rendimento na 3.ª onda: **2,0 docs novos por fonte** e **0,37 itens na Sala por fonte**. Projeção:
  **~76 docs novos/dia e ~14 itens na Sala/dia**.
  ⚠️ **NÃO SEI se aguenta.** A 3.ª onda veio ~11 h depois da 2.ª. Visitar a mesma fonte todos os dias
  pode dar sobretudo `SEEN_AGAIN` (já visto). A primeira semana mede a queda.
- **Ciclo completo:** 32 dos 38 domínios têm 1 fonte e são visitados **todos os dias**; edagricole.it
  leva **15 dias** para passar pelas 15 fontes; cia e crea 5 dias; enea 3.
- **Cada fonte nova** num domínio novo acrescenta +1 corrida/dia. Num domínio que já existe, alonga o
  ciclo dele. As candidatas da FILA-ÚNICA e os contratos novos entram quando a coorte for congelada de
  novo (a coorte continua a ser a única lista: G3).

## 7. O que falta construir (próxima missão, se aprovado)

1. `rodadas.proxima_fonte(...)` e `rodadas.uma_volta_continua(...)`, **puras** (como
   `supervisor.uma_volta_sup`): os testes chamam-nas e conferem a sequência.
2. `--continuo --uma-volta` no CLI, o latch, o trinco e o livro diário `CONTINUA-*.ndjson`.
3. Testes offline contra o servidor local (o arnês de `tests/test_rodadas.py` e de `ensaio_rodada.py`),
   com mutação: domínio ocupado não sai; latch não se solta sozinho; RAM baixa salta sem latch; a volta
   não deixa lock órfão; o teto do dia soma todas as voltas.
4. A tarefa do agendador (15 min) com o mesmo portão que a `\SINTONIA-Italy-ForwardOnly`.
5. **Medir antes de instalar:** a escrita atómica dos livros que o portão lê (§3); e a queda do
   rendimento com visitas diárias (§6).

## 8. D86-b e D86-c: LINHAS POR CANAL, EM PARALELO, com rodízio dentro de cada linha

D86-b (dono): «nosso foco não é somente sites… podemos intercalar esses sites pra dar respiro pra eles?»
D86-c (dono): «ou podemos fazer a coleta por canal e trabalhar em paralelo? equipe do instagram, equipe do
linkedin». O serviço da §2 passa a ser **uma linha por canal**, e cada uma é a mesma volta curta da §2 com
`--linha=<canal>`. Dentro de cada linha, **rodízio** de domínios e contas: o mesmo site nunca em voltas
seguidas. O comum (contador, VPN, entrega, Sala) é **um só** para todas.

### 8.1 As linhas (medido nos ramos e no vivo `dc0de726`, 26/09 ~18:15)

| linha | ferramenta (onde está) | fontes | limite da plataforma (medido) | pedidos/dia que aguenta | equipe dona (proposta) | para arrancar falta |
|---|---|---|---|---|---|---|
| **1 · Sites e boletins** (T3, T2, T7, T9, T12…) | `onda_web.py` + `rodadas.py` (**vivo**) | 64 na coorte, 38 domínios | 5/domínio/24 h (D38+D79), robots, pausa por host | ~176 (38 domínios) | COLETA-WEB | o verbo `--continuo` (§7) |
| **2 · Preços** (T10) | `leis/preco_de_mercado.py` (ramo `nuvem-polso-mercato-v1` 940b6d35) + myfruit.it no vivo | 1 no vivo (myfruit); + BMTI, Borsa Vercelli/Novara, Sala Mortara (**fora da fila de candidatas**) | 5/domínio/24 h | ~5 por domínio novo | MERCADO | instalar o polso; as 3 bolsas entrarem como candidatas e contrato |
| **3 · APIs científicas** (T6) | `pesquisadores_t6.py` (ramo `pesquisadores-t6-v1` 34713ccc) | 36 T6 no Atlas (0 com contrato); 12 pares cultura×praga | 5/domínio/rodada: openalex 12 pedidos = 3 rodadas; crossref 1 por 40 DOI; orcid 1 por pessoa. ⚠️ OpenAlex «Insufficient budget» com HTTP 200 (14/09): **NÃO SEI** se continua grátis | 5 por API por 24 h com a regra de hoje: 15/dia | CIENCIA | instalar; a regra de 5/24 h numa API oficial com quota própria é **decisão do dono** (a quota delas é maior) |
| **4 · Páginas de pesquisadores** (T6) | `seguir.py` (ramo `seguir-pesquisadores-v1` d0b1d06c) | 124 pessoas ligadas a obra T6 (de 278 do MUR) | orcid.org: 4 pessoas por rodada (robots + 4 = 5); páginas da universidade até 2 por pessoa; 3 s entre pedidos | ~5 em orcid.org + 5 por universidade | CIENCIA | instalar; o robô de fontes hoje só leva até ao fim canal YouTube e página web (dito no próprio relatório) |
| **5 · PDFs de monitorização** (T3 boletins fitossanitários) | `micro_prova_colisao.py` + `medir_contagens.py` (ramo `micro-prova-lote2b-v1` 365842a8) | 20 alvos (19 já são fontes, paradas no canário) | ≤ 5 por alvo, pausa 3 s; **fmach.it, agriligurianet.it, sardegnaagricoltura.it** já levaram pedidos hoje | ~100 (20 × 5) | COLETA-WEB (boletins) | instalar; a sonda vira contrato de monitorização das fontes que já existem |
| **6 · YouTube** | Scrap no vivo (`coleta/scrap_capacidades.py`: `youtube.search`, `.comments`, `.channel.discovery`, `.public_audio` **PROVEN**); **freio** (`coleta/teto_da_onda.py`) e **maestro** no ramo `lote3-social-v2` 17a52ef6 | 41 canais (roteiro canais-41); 9 presos em RETRY_AFTER | youtube.com + googlevideo.com = **um só orçamento** (D41); áudio público sem chave medido (D24: oEmbed 200, 5,8 MB de áudio); ~120 `/watch` e vem 429 | com 5/24 h em youtube.com: ~1 vídeo por dia (ver §8.7) | SOCIAL-VIDEO | freio (pacote 3) para o Scrap contar ANTES do pedido |
| **7 · LinkedIn** (1.ª classe, D86-d) | Scrap no vivo: `linkedin.org.posts`, `.org.video`, `.org.caption` **PROVEN** (D23, `docs/sintonia-scrap/D23-LINKEDIN-ORG-VIDEO.md`); pessoa com prova oficial (D24) | páginas de ORGANIZAÇÃO (limite `PUBLIC_ORG_VIDEO_ONLY`) | medido em 18 páginas italianas: `GET /company/<slug>/` 200, **10–18 activity ids** por página, **9 de 18 com ≥ 1 vídeo**; MP4 em `dms.licdn.com` (outro domínio); legenda VTT quando existe (gruppocaviro: 2 vídeos + 2 legendas); perfil de PESSOA sem prova oficial = authwall HTTP 999 (D24, não se contorna); robots do LinkedIn DISALLOWED, autorizado pelo dono (D23); US$ 0, sem login | 5/24 h em linkedin.com = ~5 páginas de organização por dia; os vídeos vão para licdn.com (orçamento próprio) | SOCIAL-TEXTO | freio (pacote 3); a lista de páginas de organização como fontes |
| **8 · Instagram** (1.ª classe, D86-d) | Scrap no vivo: `instagram.reel.capture`, `.reel.audio`, `.reel.transcribe` **PROVEN** sem login (D22; `data/samples/CANARIO-REELS-INSTAGRAM-V1.json`) | perfis públicos (canário: `bayer_italia`; `COMPETITOR-PUBLIC-COMM/CONTAS-V1`) | medido: lista por `instagram.com/<perfil>/embed/` (200, 323 KB, GraphQL com mídia), **3 de 3 reels de ponta a ponta** (RAW 3, DERIVED com texto 3), 527 s para os 3 (~3 min por reel, com ASR local), US$ 0, sem conta. **NÃO SEI** em que domínio vêm os bytes do reel (instagram.com ou CDN): decide se o 5/24 h é por perfil ou por plataforma | com 5/24 h em instagram.com: 1 lista por perfil → ~5 perfis/dia se a mídia vier de CDN; ~1 perfil/dia se vier de instagram.com | SOCIAL-IMAGEM | freio (pacote 3) também na rota do reel (hoje o freio cobre Scrap/yt-dlp; **medir** se cobre o reel) |
| **9 · Facebook** | `adaptador_facebook.py` no vivo; Biblioteca de Anúncios pela janela gráfica | NÃO SEI | a Biblioteca só abre na janela gráfica (medido antes) | NÃO SEI | SOCIAL-IMAGEM | uma rota sem janela, ou fica fora da coleta contínua |
| **10 · Clima** (T2) | boletins ARPA na linha 1; ARPAV API REST sem chave (medido antes); `t2-boletins-v1` (**não instalado**) | as ARPA da coorte (arpae, arpat, arpal, arpa.veneto, arpa.marche, arpacampania) | 5/domínio/24 h; ARPAV 401 no caminho dos boletins (medido) | ~30 | CLIMA | instalar t2-boletins-v1; a API ARPAV como receita |

**NÃO SEI dito:** quantas contas Facebook existem e prontas no vivo; em que domínio o Instagram serve os bytes do reel; se o OpenAlex ainda é grátis. Só rotas **US$ 0** (as fases Apify pagas estão proibidas).

> **Correção (D86-d, dono 18:20):** eu tinha posto Instagram e LinkedIn como «NÃO SEI» e por último, sem ler o que o Scrap já prova no vivo. Errado: os dois são linhas de 1.ª classe, com rendimento medido nos canários (acima). A ordem da §8.5 foi corrigida.
por linha; se o OpenAlex ainda é grátis. Nada disto foi medido nesta passagem (sem rede).

### 8.2 O que é COMUM a todas as linhas (um só de cada)

1. **Um só contador de teto por domínio (≤ 5 / 24 h).** Já há uma língua comum: o transporte web
   (`italy_pilot_collect.mjs`) e o freio social (`coleta/teto_da_onda.py`) falam **o mesmo livro**
   (`{"PEDIDOS_POR_DOMINIO": …}`), com o mesmo trinco `<livro>.trinco` e o mesmo `SINTONIA_TETO_POR_HOST`.
   Hoje o livro é **por onda**. Proposta: **um livro do dia móvel** comum a todas as linhas,
   `<ONDAS>/CONTINUA/TETO-24H.json`. Cada pedido de qualquer linha grava `{domínio, instante}` pelo mesmo
   trinco, e o corte é «pedidos das últimas 24 h ≥ 5 → não sai». A prova independente (`prova_teto_dominio`)
   passa a ler o dia inteiro de **todas** as linhas. Equivalências de domínio num sítio só
   (`MESMO_ORCAMENTO`: googlevideo.com = youtube.com, D41).
2. **Uma só saída VPN IT.** A VPN é da máquina, não da linha. Cada linha faz o portão antes e depois da
   sua volta. **Se uma linha vê fora de IT, o latch é GERAL** (`COLETA-CONTINUA-PARADA.flag` pára todas),
   porque as outras estão na mesma saída.
3. **Uma só fila de entrega e um só escritor na Sala.** Hoje cada corrida escreve na Sala pelo seu
   orquestrador. Com várias linhas em paralelo, seriam vários escritores. Proposta mínima: as linhas
   escrevem RAW, DERIVED e Admissão como hoje, e o **pousar na Sala** passa por **uma fila** (um ficheiro
   por item em `<ONDAS>/CONTINUA/FILA-SALA/`), esvaziada por **um só pousador** (uma linha própria,
   «SALA»). A Sala já é idempotente por documento. A reconciliação (§2, passo 9) passa a ler a fila e a Sala.
   Alternativa mais curta: um trinco `SALA.trinco` à volta do passo de pousar. Resolve a concorrência mas
   não dá uma fila legível. Recomendo a fila.
4. **Um só latch e um só livro diário** (`CONTINUA-<data>.ndjson`, com a coluna `LINHA`).

### 8.3 Quantas linhas cabem ao mesmo tempo (RAM)

Medido agora (18:15): **6 GB livres de 31,9**. Processos: python 20 processos, 646 MB no total (máx. 325
MB); node 6 processos, 1,9 GB (máx. 852 MB); postgres 206 MB. A regra da máquina é **≥ 5 GB livres** para
trabalho pesado. **Não medi** quanto gasta uma linha de coleta. Estimativa: python da linha + orquestrador
+ node do coletor + curl, cerca de 0,3–0,5 GB por linha web; a linha de YouTube com transcrição na GPU
gasta mais (NÃO SEI quanto de RAM).
- **Com 6 GB livres e o piso de 5 GB: cabe 1 linha, no máximo 2 leves.** Cada linha verifica a RAM antes
  da volta: abaixo do piso, salta a volta sem latch (§4).
- **Primeiro passo de qualquer arranque:** medir a RAM de UMA linha a correr (o pico, com o node do
  coletor), e só então abrir a 2.ª.

### 8.4 O rodízio dentro de cada linha (D86-b)

- Cada volta escolhe **domínio (ou conta) diferente da volta anterior da mesma linha**. Nunca o mesmo site
  em voltas seguidas, mesmo com orçamento.
- **Respiro mínimo por domínio:** 24 h entre visitas (a janela de hoje). Dentro das 24 h, os ≤ 5 pedidos
  vão **numa só volta**, e não em cinco voltas de 1.
- **Entre linhas:** a regra é por domínio, não por linha. Se duas linhas tocam o mesmo domínio (a ARPA na
  linha 1 e na 10; a universidade na 3 e na 4), o livro comum de 24 h (§8.2.1) **conta as duas juntas**.

### 8.5 Ordem de arranque (pelo rendimento da Intelligence, rodada 2)

1. **Linha 1 (sites/boletins)**: já está no vivo; T3 é «a família mais útil» e T2 vem logo a seguir.
2. **Linhas 8 e 7 (Instagram reels, LinkedIn de organização)**: rotas US$ 0 **PROVEN** no vivo (D22, D23), com texto
   medido (3/3 reels com transcrição; 9/18 páginas com vídeo). É T8 com nome e lugar, que é o conselho 4 da
   Intelligence. Falta só o freio (pacote 3) para o Scrap contar ANTES do pedido no livro comum.
3. **Linha 2 (preços)**: T10 deu 66,7 % dos sinais, mas é uma fonte só. O polso e as 3 bolsas tiram essa
   dependência.
4. **Linha 5 (PDFs de monitorização)**: é T3; 19 dos 20 alvos já são fontes.
5. **Linhas 3 e 4 (pesquisadores)**: T6, com local e período do estudo (conselho 3 da Intelligence).
6. **Linha 10 (clima)**: janelas T2 regionais (conselho 5).
7. **Linha 6 (YouTube)**: Scrap PROVEN no vivo; o orçamento youtube.com + googlevideo.com dá ~1 vídeo por dia.
8. **Linha 9 (Facebook)**: por último. Não há rota US$ 0 provada sem janela gráfica.

Com a RAM de hoje, as linhas arrancam **uma de cada vez**, nesta ordem, cada uma só depois de a anterior
ter um dia sem latch e a RAM dela estar medida.

### 8.7 ⚠️ Decisão do dono: o teto de 5/24 h numa PLATAFORMA

A regra de hoje é **por domínio registável**. Todos os perfis do Instagram são `instagram.com`, todas as
páginas do LinkedIn são `linkedin.com`, e todos os canais do YouTube são `youtube.com` (+ googlevideo.com,
D41). Aplicada tal e qual, a regra dá **~5 páginas de organização por dia no LinkedIn, ~1 a 5 perfis por
dia no Instagram e ~1 vídeo por dia no YouTube**, para a plataforma inteira. Isso choca com «as redes
captam tudo o que precisamos» (D86-d).

Opções, e a escolha é do dono:
- **A.** manter 5 por domínio por 24 h (o mais cortês, pouco volume nas redes);
- **B.** para as plataformas, 5 **por conta ou página** por 24 h, com um teto diário da plataforma declarado
  (por exemplo, 50 pedidos por dia no instagram.com), contado no mesmo livro comum;
- **C.** o limite que a própria plataforma publica, quando publica.

Sem a decisão, o desenho usa **A**: é a regra que está no código e nas provas.

### 8.6 Uma volta-exemplo de 24 h (números)

Com o que hoje está no vivo (linha 1) + as linhas 2, 3, 5 instaladas, **uma linha de cada vez** (RAM):

| hora | linha | o que faz | pedidos |
|---|---|---|---|
| 00:05 | — | backup diário da Sala (`pg_dump`) | 0 |
| 00:15–09:45 | 1 sites | 38 voltas de 15 min, 1 domínio por volta, em rodízio (T3/T2 primeiro, edagricole 1 fonte) | ~176 |
| 06:00 | — | Intelligence diária sobre uma cópia da Sala | 0 |
| 10:00–13:00 | 5 PDFs | 20 alvos × ≤ 5 (os já pedidos nas 24 h ficam para amanhã) | ≤ 100 |
| 13:00–14:00 | 2 preços | myfruit (se não pedido na linha 1 nas 24 h) + as bolsas | ~5–20 |
| 14:00–15:00 | 3 APIs científicas | openalex 5 · crossref ≤ 5 · orcid 5 | 15 |
| resto do dia | — | voltas «nada livre» (a janela de 24 h) | 0 |
| **total** | | | **~300–320 pedidos/dia**, nunca > 5 por domínio em 24 h |

Rendimento esperado da linha 1 (§6): ~76 docs e ~14 itens na Sala por dia, **NÃO SEI se aguenta**. As
outras linhas **não têm medida de rendimento** na Sala (nenhuma correu com rede para a Sala). O primeiro
dia de cada linha é a medida.

## EM PALAVRAS SIMPLES

- Hoje a coleta roda em «rodadas», e isso trava: um site com muitas fontes (edagricole) segura todas
  as rodadas. Esta noite só dá para rodar uma.
- A proposta é rodar **uma fonte de cada vez**, a cada 15 minutos. Sempre a melhor fonte cujo site não
  foi visitado nas últimas 24 horas. Assim a coleta não para nunca, e nenhum site recebe mais de 5
  visitas por dia.
- O robô que procura fontes novas **não precisa mais parar**. Cada um escreve nos seus próprios
  cadernos. Só há um caderno em comum, e para esse existe um aviso de «estou mexendo».
- Se a VPN sair da Itália, se a contagem de visitas der errado ou se o backup falhar, a coleta **para
  sozinha** e só volta quando uma pessoa liberar.
- Com as 64 fontes de hoje, a conta dá **até 38 visitas por dia**, ~76 páginas novas e ~14 itens para a
  Sala. Mas isso ainda precisa ser confirmado na prática: visitar todo dia pode trazer menos novidade.
- **Por canal, em paralelo (D86-c):** cada canal vira uma «linha» com a sua equipe: sites, preços,
  PDFs, pesquisadores, clima, YouTube, LinkedIn, Instagram, Facebook. Dentro de cada linha, os sites se
  revezam, e nenhum é visitado duas vezes seguidas (D86-b).
- **O que é de todas:** um só caderno que conta as visitas de todas as linhas juntas (no máximo 5 por
  site por dia), a mesma VPN (se cair para uma, param todas), e uma só porta de entrada na Sala.
- **Quantas ao mesmo tempo:** hoje sobram só ~6 GB de memória, e a regra pede 5 GB livres. Então é
  **uma linha de cada vez** até medirmos quanto cada uma gasta.
- **Ordem:** sites e boletins (já instalados) → **Instagram e LinkedIn** (o Scrap já provou: 3 de 3 reels
  com o texto falado; vídeos e legendas de páginas de empresa; tudo sem login e sem pagar) → preços → PDFs
  → pesquisadores → clima → YouTube → Facebook.
- **Corrigi um erro meu:** eu tinha posto Instagram e LinkedIn por último, como se não soubéssemos se
  funcionavam. O Scrap já tinha provado os dois.
- **Uma decisão para o dono:** a regra de «5 visitas por site por dia» vale para o instagram.com inteiro.
  Isso dá poucas contas por dia. Dá para manter assim, ou contar 5 por conta com um limite diário da
  plataforma.
- Só a linha de sites está instalada. As outras estão prontas em ramos, esperando instalação.
