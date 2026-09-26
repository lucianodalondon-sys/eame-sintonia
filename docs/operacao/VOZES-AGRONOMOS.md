# VOZES-AGRONOMOS — 30 fontes para a «Voci dal Campo», achadas no que já guardámos

> Ramo `vozes-agronomos-v1` (a partir do vivo `69b0e23f`), **só documento e registos**. Missão:
> `auditoria-madrugada/missao-vozes-agronomos.txt` (D84; ferramenta «Voci dal Campo» em
> `FERRAMENTAS-DO-CASCO.md`). **Sem rede**: só o repositório e o acervo (Sala só leitura, armazém só leitura,
> livros do vivo só leitura). Nada coletado, nada instalado.

## Resposta curta

- **30 fontes**: **22 pessoas com nome** no título do vídeo (em 9 canais já guardados) + **8 séries técnicas**
  (webinars e convegni) em que a pessoa ainda não tem nome.
- **Papel provado: 1 de 30** (Simon Pierce, página oficial da Università di Milano, já colhida pela P5). Nas
  outras 21 pessoas, o papel **só o título do vídeo diz** («Agronomo Fitopatologo», «Docente Università di
  Padova», «Rete tecnica CAI»…). Algumas podem nem ser técnicas (gestores de cooperativa/OP): está marcado.
  Contando só quem o título diz ser técnico ou académico, são **cerca de 11**, não 30.
- **Transcrição com rota aberta hoje: 0 de 30.** Todos os vídeos são de canais YouTube de terceiros:
  - a legenda de um canal de terceiro só sai com **permissão do dono** (`captions.download`);
  - separar o áudio é **proibido** pela cláusula III.I.7 das políticas do YouTube;
  - a D53 manda: «transcrição só quando o Scrap a trouxer; não inventar».
  O texto que **existe e se pode pedir** é a **descrição do vídeo** (API oficial, rota da D53) e o texto que
  o acompanha (artigo da revista, atas/slides do webinar). **Transcrição de verdade pede autorização dos
  donos dos canais** — é decisão do dono do SINTONIA, não da coleta.
- **Plano de pedidos**: **19 pedidos em 15 domínios, 1 ronda** (≤ 5 por domínio, D38), para provar o papel de
  cada pessoa na página da instituição + **1 chamada** `videos.list` à API do YouTube (descrições, datas,
  canais) pelo Scrap. Mais **4 sites a DESCOBRIR antes** (10 fontes), porque o domínio não está em nenhum livro
  nosso — **não se inventa endereço**.

## 1. Onde procurei

`data/derivados/VOZES-AGRONOMOS/titulos.py.txt` → `TITULOS.json`: para cada bruto de vídeo/podcast/webinar
guardado (Sala só leitura: `raw_asset` + `derived_artifact`), o título = a 1.ª linha do texto derivado no
armazém. **737 vídeos de 50 fontes.** Li os títulos à mão, filtrando por sinais de fala de pessoa
(«intervista», «prof.», «dott.», «agronomo», «tecnico», «università», nome + instituição). O detector
automático de nomes do script acerta pouco («Pomodoro da Industria» não é gente): **a lista é leitura
humana**; o script só junta a prova guardada (endereço e sha256 do bruto de cada vídeo).

Também procurei nas candidatas do vivo: webinars/podcasts fora do YouTube quase não existem (3 podcasts no
Spotify — ARPAE `CAND-0333`, Regione Lombardia settore agricolo `CAND-0290`/`CAND-0299` — sem conteúdo
guardado; a mesma regra de áudio do Spotify vale: não se baixa). A YT3 (`canais-pessoas-v1`) já tinha medido:
14 canais, **todos de organizações, 0 pessoas**.

## 2. As 30

Região = a da **pessoa ou organização** (onde fica), **nunca** a do facto.

| # | Pessoa | Papel (só pelo título, salvo V22) | Cultura / problema | Região da pessoa/organização | Canal | Vídeo guardado | Provar o papel em |
|---|---|---|---|---|---|---|---|
| V01 | Silverio Pachioli | Agronomo Fitopatologo | olivo · difesa | NAO SEI | L'Informatore Agrario `IT-T8-006` | «Oliveto Smart a Fieragricola 2026 - Intervista a Silverio Pachioli – Agronomo Fitopatologo» | DESCOBRIR: site da L'Informatore Agrario (dominio fora dos nossos livros) |
| V02 | Valerio Nadal | Condifesa (qual: NAO SEI) | vite · difesa | NAO SEI | L'Informatore Agrario `IT-T8-006` | «Vite in Campo 2026 - Intervista a Valerio Nadal (Condifesa)» | DESCOBRIR: site da L'Informatore Agrario (dominio fora dos nossos livros) |
| V03 | Giulia Zuecco | Docente Universita di Padova | olivo | Veneto | L'Informatore Agrario `IT-T8-006` | «Oliveto Smart a Fieragricola 2026 - Intervista a Giulia Zuecco – Docente Università di Pad» | dafnae.unipd.it |
| V04 | Silvia Toffolati | Universita di Milano | vite | Lombardia | L'Informatore Agrario `IT-T8-006` | «Vite in Campo 2026 - Intervista a Silvia Toffolati (Università di Milano)» | unimi.it |
| V05 | Riccardo Castaldi | Terremerse (papel: NAO SEI) | vite | Emilia-Romagna | L'Informatore Agrario `IT-T8-006` | «Vite in Campo 2026 - Intervista a Riccardo Castaldi (Terremerse)» | terremerse.it |
| V06 | Enzo Gambin | direttore Aipo (produttori olivicoli) | olivo | Veneto | L'Informatore Agrario `IT-T8-006` | «Oliveto Smart a Fieragricola 2026 - Intervista a Enzo Gambin, direttore Aipo» | DESCOBRIR: site da Aipo (dominio fora dos nossos livros) |
| V07 | Gabriele Posenato | Cadis 1898 (papel: NAO SEI) | vite | Veneto | L'Informatore Agrario `IT-T8-006` | «Vite in Campo 2026 - Intervista a Gabriele Posenato (Cadis 1898)» | DESCOBRIR: site da L'Informatore Agrario (dominio fora dos nossos livros) |
| V08 | Silvano Nicolato | Cantine Vitevis (papel: NAO SEI) | vite | Veneto | L'Informatore Agrario `IT-T8-006` | «Vite in Campo 2026 - Intervista a Silvano Nicolato (Cantine Vitevis)» | DESCOBRIR: site da L'Informatore Agrario (dominio fora dos nossos livros) |
| V09 | Hannes Tauber | VOG - Home of apples (papel: NAO SEI) | melo | Alto Adige | Myfruit.it `IT-T10-017` | «MyfruitTV intervista Hannes Tauber / VOG - Home of apples» | DESCOBRIR: site da VOG (dominio fora dos nossos livros) |
| V10 | Filomena Vocca | OP Solco Maggiore (papel: NAO SEI) | ortaggi | NAO SEI | Myfruit.it `IT-T10-017` | «MyfruitTV videointervista Filomena Vocca / Op Solco Maggiore» | myfruit.it |
| V11 | Hanspeter Felder | Cooperativa produttori sementi Val Pusteria | patata da seme | Alto Adige | Myfruit.it `IT-T10-017` | «MyfruitTV videointervista Hanspeter Felder / Cooperativa dei produttori sementi della Val » | myfruit.it |
| V12 | Matteo Gnocato | Rete tecnica CAI | tecnico di campo (cultura: NAO SEI) | NAO SEI | Consorzi Agrari d'Italia `IT-T9-016` | «Matteo Gnocato / Rete tecnica CAI» | DESCOBRIR: site dos Consorzi Agrari d'Italia (dominio fora dos nossos livros) |
| V13 | Amedeo Coppo | Responsabile Sviluppo Grandi Colture CAI | cereali · grandi colture | NAO SEI | Consorzi Agrari d'Italia `IT-T9-016` | «Amedeo Coppo / Responsabile Sviluppo Grandi Colture» | DESCOBRIR: site dos Consorzi Agrari d'Italia (dominio fora dos nossos livros) |
| V14 | Donato Cillis | Area R&S agricoltura di precisione CAI | agricoltura di precisione | NAO SEI | Consorzi Agrari d'Italia `IT-T9-016` | «Donato Cillis / Area R&S agricoltura di precisione» | DESCOBRIR: site dos Consorzi Agrari d'Italia (dominio fora dos nossos livros) |
| V15 | Stefano Forbicini | Responsabile Concimi e Sementi CAI | concimi · sementi | NAO SEI | Consorzi Agrari d'Italia `IT-T9-016` | «AF-X1 / Stefano Forbicini - Responsabile Concimi e Sementi» | DESCOBRIR: site dos Consorzi Agrari d'Italia (dominio fora dos nossos livros) |
| V16 | Pietro Baroncini | Conserve Italia (papel: NAO SEI) | drupacee · campagna 2026 | Emilia-Romagna | Conserve Italia `IT-T9-014` | «Campagna drupacee 2026, la frutta c'è: il punto di Pietro Baroncini» | conserveitalia.it |
| V17 | Ernesto Comite | Dipartimento di Agraria UNINA | NAO SEI (so o nome no titulo) | Campania | UNINA Dipartimento di Agraria `IT-T5-038` | «Dipartimento di Agraria - Ernesto Comite» | agraria.unina.it |
| V18 | Mario Enrico Pe | (Georgofili; instituicao: NAO SEI no titulo) | grano | NAO SEI | Georgofili INFO `IT-T7-035` | «Marina Carcea e Mario Enrico Pè - Che ne sai tu di un campo di grano» | georgofili.it |
| V19 | Marina Carcea | (Georgofili; instituicao: NAO SEI no titulo) | grano | NAO SEI | Georgofili INFO `IT-T7-035` | «Marina Carcea e Mario Enrico Pè - Che ne sai tu di un campo di grano» | georgofili.it |
| V20 | Bruno Basso | AGRILAB 2026 (instituicao: NAO SEI no titulo) | agronomia digitale (NAO SEI) | NAO SEI | Terra e Vita `IT-T8-004` | «AGRILAB 2026, INTERVISTA A BRUNO BASSO» | terraevita.edagricole.it |
| V21 | Angelo Basile | Dott., CNR-ISAFOM | suolo · acqua | Campania | CNR ISAFOM `IT-T5-037` | «Dott. Angelo Basile - CNR-ISAFOM» | isafom.cnr.it ⛔ sem cnr.it (coordenacao 10:13) |
| V22 | Simon Pierce | Universita di Milano DISAA — PROVADO (pagina oficial, P5) | ecologia vegetale (NAO SEI a cultura) | Lombardia | candidata (sem SOURCE_ID) `CAND-1199` | — | unimi.it |
| V23 | NAO SEI (relatores do webinar) | tecnici/ricercatori CRPV | patata · elateridi; albicocco · fitosanitario; gelate | Emilia-Romagna | CRPV `IT-T5-040` | «Webinar "Patate: strategie sostenibili contro gli elateridi" Emepaclima 26.11.2025» | crpv.it |
| V24 | NAO SEI (relatores) | agronomi CONAF | difesa delle colture · prescrizione fitofarmaci · droni | NACIONAL | CONAF `IT-T7-026` | «Conoscere le minacce per ipotizzare la strategia di difesa - Sostenibilità e difesa delle » | conaf.it |
| V25 | NAO SEI (quem apresenta) | Consorzio Brunello (agronomo?: NAO SEI) | vite (Sangiovese) · annata agronomica | Toscana | Consorzio del Vino Brunello di Montalcino `IT-T7-034` | «Benvenuto Brunello 2024 - Presentazione Annata Agronomica 2024» | consorziobrunellodimontalcino.it |
| V26 | NAO SEI (tecnici AMAP) | tecnici AMAP Marche | olivo · mosca delle olive; patata | Marche | ASSAM Marche `IT-T12-008` | «AMAP a convegno: la difesa della mosca delle olive» | amap.marche.it |
| V27 | NAO SEI (tecnici Koppert) | tecnici Koppert (concorrente T9) | agrumi · melone (afide) · pomodoro (Fusarium) | NAO SEI | Koppert Italia `IT-T9-017` | «Gestione dell'afide su melone con parassitoidi e predatori Koppert» | koppert.it |
| V28 | NAO SEI | Conserve Italia / Unibo (Progetto Agrometeo) | cimice asiatica · irrigazione frutteto | Emilia-Romagna | Conserve Italia `IT-T9-014` | «Difesa contro la cimice asiatica: consigli utili» | conserveitalia.it |
| V29 | NAO SEI (relatores) | Rete Rurale / CREA | monitoraggio fenologico (castagno, tiglio) · SQNPI produzione integrata | NACIONAL | Pianeta PSR `IT-T12-011` | «Corso online sul monitoraggio fenologico del castagno - 3 giugno 2026.» | reterurale.it |
| V30 | NAO SEI (relatores) | ANBI (Macfrut 2025) | DSS · stress climatici · irrigazione | NACIONAL | ANBI `IT-T7-023` | «AGRONOMIA MODERNA: DSS, Sensoristica e Digital Twin in Agricoltura - MACFRUT 2025» | anbi.it |

**O que ficou de fora, e porquê** (lido nos títulos): políticos e dirigentes (Assosementi «tracciabilità»,
presidentes de associação na TV — CIA, FederBio), pescadores («La Comunità del Mare» da AMAP, «Gente di mare»
da Coldiretti), educadores de vinho (Valpolicella Wine Talks), marketing (Grana Padano), aerobiologia de
pólen (ARPA Marche — não é cultura), cursos e apresentações de departamento (UNINA, Chianti Classico).
**Coldiretti e CNR**: a coordenação (10:13) fechou-os nesta rede; o Dott. Angelo Basile (CNR-ISAFOM, V21) fica
na lista **sem pedido**. **D52**: as ordens provinciais de agrónomos foram retiradas; o canal nacional da
CONAF (IT-T7-026, V24) não é uma delas.

## 3. Plano de pedidos por domínio (NÃO executado)

Um pedido por pessoa/série, à página institucional que prova o papel (e, para as séries, ao programa do
webinar/convegno que diz quem falou). Os vídeos **não** se pedem um a um em `youtube.com/watch` (dá 429 depois
de ~120 páginas, e a D53 diz que a prova do vídeo é página pública + título + data + canal): **uma** chamada
`videos.list` com os 21 ids devolve descrição, data e canal. A chave da API só existe no segredo do GitHub
(roteiro CANAIS-41) — corre pelo Scrap, não daqui.

| Domínio | Pedidos | Rondas | Fontes |
|---|---|---|---|
| conserveitalia.it | 2 | 1 | V16,V28 |
| georgofili.it | 2 | 1 | V18,V19 |
| myfruit.it | 2 | 1 | V10,V11 |
| unimi.it | 2 | 1 | V04,V22 |
| agraria.unina.it | 1 | 1 | V17 |
| amap.marche.it | 1 | 1 | V26 |
| anbi.it | 1 | 1 | V30 |
| conaf.it | 1 | 1 | V24 |
| consorziobrunellodimontalcino.it | 1 | 1 | V25 |
| crpv.it | 1 | 1 | V23 |
| dafnae.unipd.it | 1 | 1 | V03 |
| koppert.it | 1 | 1 | V27 |
| reterurale.it | 1 | 1 | V29 |
| terraevita.edagricole.it | 1 | 1 | V20 |
| terremerse.it | 1 | 1 | V05 |
| www.googleapis.com (YouTube Data API, via Scrap/D53) | 1 | 1 | videos.list com 29 ids (descricao, data, canal) |

**Total: 19 pedidos em 15 domínios + 1 chamada à API, 1 ronda**, nunca mais de 2 por domínio.

⚠️ `reterurale.it` (V29): o robots.txt da Rete Rurale só aceita visitas entre **01h e 03h UTC** (medido no MICRO-PROVA-LOTE1) — esse pedido vai nessa janela.

**Descobrir antes** (o site do dono não está em nenhum livro nosso; o canal YouTube está):

| O que descobrir primeiro | Fontes |
|---|---|
| DESCOBRIR: site da L'Informatore Agrario (dominio fora dos nossos livros) | V01, V02, V07, V08 |
| DESCOBRIR: site da Aipo (dominio fora dos nossos livros) | V06 |
| DESCOBRIR: site da VOG (dominio fora dos nossos livros) | V09 |
| DESCOBRIR: site dos Consorzi Agrari d'Italia (dominio fora dos nossos livros) | V12, V13, V14, V15 |

## 4. O que isto quer dizer para a «Voci dal Campo»

1. **As pessoas existem** nos vídeos que já guardámos: agrónomos, docentes, técnicos de consórcio e de
   cooperativa, a falar de **olivo, vite, melo, drupacee, patata, cereais**.
2. **O papel quase nunca está provado** — o título é a única prova. 20 pedidos numa ronda resolvem isso.
3. **A fala não vira texto sem autorização.** A «Voci dal Campo» pede citação original ou transcrição: com
   YouTube de terceiros, isso só abre por (a) autorização do dono do canal, ou (b) fontes em que a pessoa
   fala **em texto** — artigos assinados, atas de webinar, **boletins fitossanitários assinados por
   técnicos** (o tipo 1 da D84, já no lote da GAPS-CANDIDATAS). A (b) já está ao alcance; a (a) é decisão do
   dono.
4. Canais que mais rendem pessoas por vídeo: **L'Informatore Agrario** (8 pessoas em 15 vídeos),
   **Consorzi Agrari d'Italia** (9 em 15, quase todos técnicos/responsáveis), **myfruit** (entrevistas a
   OP/cooperativas).

## Ficheiros (todos no ramo, só registos)

| Ficheiro | O quê |
|---|---|
| `data/derivados/VOZES-AGRONOMOS/titulos.py.txt` → `TITULOS.json` | os 737 títulos de vídeo guardados, por fonte, com endereço e sha256 do bruto |
| `…/vozes.py.txt` → `VOZES.json` | as 30 fichas (lista humana), o plano de pedidos e o que descobrir antes |
| `…/ler_sala.py.txt` | leitor só-leitura da Sala (DSN nunca impresso) |

Mapa: não regerado (PRONTO-SEM-MAPA; este ramo não tem código do sistema).
