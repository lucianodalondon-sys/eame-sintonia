# LACUNAS-PARA-FONTES (D87) — para cada lacuna da Intelligence, fontes e perfis concretos, com prova

> Ramo `lacunas-para-fontes-v1`, a partir do **vivo `554c1ec1`** (LOTE 3). Missão: coordenação 22:05. **Sem rede.** A Sala
> só foi lida (`default_transaction_read_only=on`), para achar os bytes já guardados. A fila do vivo **não foi tocada**:
> sha256 `772b5564…` antes e depois. O registo foi numa **cópia**. **SEM MAPA.**
> Saída fora do Git: `C:/Users/London1/sintonia-sala-italia/lacunas-para-fontes/`.

## Em palavras simples

- **O que a Intelligence pediu:** li as duas rodadas (R1 06:36 e R2 10:56), o `R1-X-R2-E-FONTES.json` e o
  `FERRAMENTAS-DO-CASCO.md`. Os pedidos juntam-se em **6 lacunas**. Cada número abaixo foi conferido pelo script nos
  próprios livros da Intelligence.

  | # | Lacuna | O número que a prova |
  |---|---|---|
  | L1 | cultura e praga não viram campo | **5 de 5** boletins T3 perderam a cultura; **3** cruzamentos tentados, **0** possíveis |
  | L2 | região | só **3** fontes T3 na Sala |
  | L3 | período e fase | **0** fontes T1 (fenologia); **3** pedidos «sem ano» |
  | L4 | pesquisador | **0** fontes T6; **31** fontes T5, 25 delas com zero |
  | L5 | voz de campo | **0** fontes T8; as **4** T7 deram zero |
  | L6 | série de preço | **1** fonte de mercado só (myfruit.it deu 6 dos 9 sinais) |
- **O achado mais importante é que a maior parte das fontes já existe, mas não chegou à Sala.** É como ter a despensa
  cheia e o prato vazio. No livro do robô de fontes, estas já estão prontas para colher (`READY_FOR_COLLECTION`),
  e mesmo assim a Sala tem pouco ou nada delas:

  | Família | Prontas no robô | Na Sala |
  |---|---|---|
  | T1 fenologia | **7** | 0 |
  | T8 agricultores e imprensa técnica | **19** | 0 |
  | T3 boletins | **7** | 3 |
  | T10 mercado | **5** | 1 |

  Mandá-las para a coleta rende mais do que qualquer candidata nova. Isto é conselho, não ordem: quem decide a
  coleta é o coordenador.
- **Candidatas novas:** **91**, numa **cópia** da fila (CAND-1205 a CAND-1295). Todas passaram pela porta canónica
  e usam TIPOS que já existem. Cada uma leva a lacuna que tapa, o `PARA_QUE` e a prova de identidade.
  - **30 consórcios de defesa** (Condifesa e equivalentes) em **15 regiões**. Estão na lista oficial da Asnacodi e
    foram medidos pela P1g a 24/09. Nunca tinham entrado na fila. Servem para L1, L2 e L3: avisos de defesa por zona.
  - **48 perfis oficiais** (Facebook 18, YouTube 9, Instagram 13, LinkedIn 8) de fontes que **já colhemos**. A prova
    é a própria página da fonte, guardada no armazém, que liga o perfil. Voltei a abrir esses bytes e confirmei o
    endereço lá dentro, um a um.
    - Por família da fonte dona: rede técnica T7 23, mercado T10 11, fenologia T1 8, boletins T3 4, imprensa T8 2.
    - Exemplos: CONAF (a ordem dos agrónomos), FederBio, Copagri, CIA Puglia, ISMEA, AgroNotizie, Rivista di
      Agraria, Italia Olivicola, o canal ERmes Agricoltura e o Consorzio di Bonifica della Romagna.
  - **6 canais YouTube** de organizações agrícolas, da missão YT3. A página oficial do dono liga o canal.
  - **5 programas de ciência e mídia**, da missão research-media, nunca instalados. São os podcasts CREA «TEA alle
    5» e «Agrifuturo», os podcasts da Rete Rurale, o «Madre Terra» (Sole 24 Ore) e o canal agrifake.
  - **2 páginas de eventos com relatores nomeados**: CRPV e ANBI, da missão VOZES.
- **LinkedIn e Instagram de organizações:** os **21** ficam `POLICY_BLOCK`, com o trecho dos termos da plataforma,
  como a casa já faz (D15). A D24 abriu só perfis de **pessoa**. A D88 abriu contorno **técnico**, não os termos da
  plataforma. Se o dono os quiser abertos, basta um parâmetro (`--sociais-abertas`), já testado.
- **O que não entrou, e porquê:**
  - **24** endereços já estão na fila;
  - **2** são a mesma conta escrita de outra forma: o myfruit como `@myfruitvideo` e como `user/myfruitvideo`;
  - **4** estão fora do foco: Parmigiano, Sherwood (florestas), UNAITALIA (aves);
  - dos perfis achados no armazém, ficaram fora:
    - **46** botões de partilha;
    - **27** contas de X, Telegram ou TikTok, que não têm rota na casa;
    - **19** contas gerais de região, província ou CNR;
    - **17** de área animal ou de laticínios;
    - **153** de famílias fora destas lacunas (clima geral T2, ciência T5, política T12, concorrência T9, eventos T11).
- **O que continua sem resposta:**
  - **Pesquisador em pessoa (T6):** a ponte do ORCID está parada, porque o robots.txt do ORCID proíbe robôs. A
    decisão é do dono. Por isso só entraram programas institucionais de ciência.
  - **Preço:**
    - a Italmercati e a Clal não têm nenhum byte nosso, e não as registei;
    - Vercelli e Pavia são de arroz, e o arroz não é cultura do casco;
    - o que falta mesmo é **consertar as receitas** do BMTI (IT-T10-002, degradado) e da Borsa Merci Bologna
      (IT-T10-009, lê o blog em vez do listino). A POLSO-FONTES já o mediu.
- **Testes:**
  - **10** testes novos passam; **10 de 10** estragos feitos de propósito foram pegos.
  - Testes da fila (`test_fila_italia_decisoes`, `test_porta_de_candidatas`, `test_medir_cutover`) com a cópia:
    **25** falhas de base antes. Depois, com a cópia registada: **+21**. São exatamente os 21 LinkedIn e Instagram
    em POLICY_BLOCK.
  - Estes 21 caem num conflito que **já existe** na casa. Uma prova diz que candidata nova não pode estar em
    POLICY_BLOCK (D13). Outra diz que LinkedIn e Instagram têm de estar (D15). As 25 falhas de base são o mesmo caso
    (CAND-1174 a 1198, do lote 3).
  - Com `--sociais-abertas`: **0** falhas novas, e **1** falha de base some.

## 1 · As propostas, lacuna a lacuna

| Lacuna | Candidatas novas (cópia) | Já existe e só precisa de coleta ou conserto (ponteiro) |
|---|---|---|
| **L1 cultura+praga** | 30 consórcios de defesa; Terra e Vita (Facebook/Instagram); CNR ISPA (Facebook); ERmes Agricoltura (YouTube) | **Reprocessar** os 3 T3 que já estão na Sala para a cultura sair do texto (pedido C1 da Intelligence). T3 READY fora da Sala: **IT-T3-011** (AGRIOS), **IT-T3-023**, **IT-T3-045**, **IT-T3-053**. Os 20 do lote 1 da GAPS (SFR/agrometeo) estão todos CONTRACTED_CANARY_FAILED por **forma** da página: precisam de receita, não de fonte nova |
| **L2 região** | os mesmos 30 consórcios: Puglia, Calábria, Emília, Piemonte, Lombardia, FVG, Trentino, Alto Ádige, Úmbria, Toscana, Abruzzo, Basilicata, Sardenha, Sicília, Marche, Vêneto | a tabela da P1g (90 células região × tipo) diz onde cada região já tem SFR/agrometeo registado |
| **L3 período/fase** | 30 consórcios; ARSAC Calábria (Instagram), ARSIAL (LinkedIn), Italia Olivicola, Rivista di Agraria (Instagram/YouTube), AgroNotizie (Facebook/Instagram/YouTube) | **T1 READY fora da Sala: 7**: IT-T1-005 Umbria, IT-T1-007 ARSIAL, IT-T1-009 Lazio, IT-T1-010 Abruzzo, IT-T1-016 Italia Olivicola, IT-T1-018 Rivista di Agraria, IT-T1-022 OlivoNews |
| **L4 pesquisador** | CREA «TEA alle 5», CREA «Agrifuturo», Rete Rurale podcast, Madre Terra (Sole 24 Ore), agrifake (YouTube) | a entrada T6 (t6-para-sala-v1, 589 trabalhos) e as 377 pessoas FEM/CREA/CNR (pesq-fora-do-mur-v1): **paradas pelo robots do ORCID** (decisão do dono) |
| **L5 voz de campo** | CONAF (Facebook/Instagram), FederBio, Copagri, Confcooperative, CIA Puglia (Facebook/Instagram/YouTube), Florovivaisti, Casalasco (LinkedIn), Est Ticino Villoresi (LinkedIn), Bonifica Romagna; 6 canais YT3 (Agroalimentare News, Agroter/Italiafruit, Biolchim, Diachem, Sipcam, Terremerse); CRPV e ANBI eventos | **T8 READY fora da Sala: 19** (ex.: IT-T8-021, 022, 024, 028–030, 032, 034…). Os 17 vídeos de canais T7/T8 do acervo com relatores (VOZES-PARA-SALA) |
| **L6 série de preço** | ISMEA (Facebook/Instagram/LinkedIn/YouTube), Borsa Merci Bologna (LinkedIn), Arancia Rossa IGP (Facebook), WineNews (Facebook/Instagram), myfruit (Facebook) | **T10 READY fora da Sala: 4** (IT-T10-010 CSO Italy, IT-T10-021 Plantgest, IT-T10-035; a IT-T10-022 é zootecnia, fora do foco). **Consertos:** IT-T10-002 BMTI (DEGRADED: procura notícia na casa; os preços estão em `/prezzi-cereali/`); IT-T10-009 Bologna (CONTRACTED_CANARY_FAILED: lê o blog); Granaria CAND-0157 → IT-T10-044 e CAND-0499 → IT-T10-028 (CONTRACTED_CANARY_FAILED) |

⚠️ Os canais de **empresa** (Biolchim, Diachem, Sipcam) têm técnicos da própria empresa. Não são voz independente.
Servem mais à **Concorrenza** do que às Voci dal Campo, e o `PARA_QUE` diz isso.

## 2 · Como se prova cada endereço (nada inventado)

| Origem | Quantas | Prova |
|---|---|---|
| perfis ligados pela página oficial de uma fonte já colhida | 48 | página guardada no armazém (endereço + sha256). O script **reabre os bytes** pelo sha256 e confirma que o endereço do perfil está lá (`conferir_nos_bytes`) |
| 30 consórcios | 30 | a tabela da P1g (`origin/janelas-regioes-v1:curadoria/JANELAS-REGIOES-V1.json`, visto em asnacodi.it/le-sedi-condifesa/) e o lote 2 da GAPS-CANDIDATAS |
| canais YT3 | 6 | a página oficial do dono (endereço + sha256 em `DESCOBERTA-CANAIS-PESSOAS-V1.json`) |
| research-media | 5 | `ACHADOS.json` do ramo: página oficial com sha256 |
| eventos CRPV/ANBI | 2 | link nas páginas colhidas na ronda 1 da VOZES (`PLANO-PROGRAMAS.json`) |

O script também confirma que cada endereço está **escrito dentro** da prova citada (`prova_contem`). Sem isso, a
proposta não se regista.

## 3 · Os comandos (o coordenador aplica no vivo)

```bash
B=<clone de origin/lacunas-para-fontes-v1>
V=C:/Users/London1/orca/workspaces/eame-sintonia/source-curator-service-v1
# 1 · propor de novo contra a fila VIVA de agora (sem rede; a Sala só leitura, para reabrir os bytes)
py $B/ferramentas/lacunas/lacunas_para_fontes.py --propor --fila=$V/candidatas/FONTES-CANDIDATAS.json \
   --saida=$B/data/derivados/LACUNAS-PARA-FONTES/PROPOSTAS.json
# 2 · registar numa cópia e conferir (o script RECUSA escrever em candidatas/FONTES-CANDIDATAS.json)
cp $V/candidatas/FONTES-CANDIDATAS.json /tmp/copia.json
py $B/ferramentas/lacunas/lacunas_para_fontes.py --registar --propostas=$B/data/derivados/LACUNAS-PARA-FONTES/PROPOSTAS.json \
   --fila=/tmp/copia.json                      # [--sociais-abertas] se o dono abrir LinkedIn/Instagram de org
# 3 · aplicar no vivo = trocar a fila pela cópia conferida (decisão do coordenador)
```

⚠️ A fila do vivo **muda sozinha**: o robô escreve nela, e a cópia de trabalho do vivo não é igual ao commit
`554c1ec1`. Os CAND-ids nascem pelo tamanho da fila. Por isso o passo 1 tem de ser corrido **na hora de aplicar**.
Não serve juntar esta cópia.

## 4 · Os ficheiros

- `ferramentas/lacunas/lacunas_para_fontes.py`: as lacunas conferidas, as propostas, o registo numa cópia.
- `ferramentas/lacunas/varrer_sociais.py`: tira do armazém os perfis que cada fonte liga (1.322 páginas HTML,
  334 sem ficheiro no disco; ~25 min).
- `ferramentas/lacunas/ler_sala.py`: leitor só-leitura.
- `data/derivados/LACUNAS-PARA-FONTES/`:
  - `SOCIAIS-NO-ARMAZEM.json`: 123 fontes com perfis;
  - `PROPOSTAS.json`: 121 propostas, com os ponteiros e os descartes contados.
- Fora do Git (`sintonia-sala-italia/lacunas-para-fontes/`):
  - `FONTES-CANDIDATAS-COPIA.json` (sha256 `8eb15663…`, 1.295 linhas);
  - `FONTES-CANDIDATAS-COPIA-SOCIAIS-ABERTAS.json`;
  - `FILA-VIVO-SHA256-ANTES/DEPOIS.txt`;
  - `TESTES-FILA-ANTES/DEPOIS*.txt`.
- `tests/test_lacunas_para_fontes.py`: 10 testes. `ferramentas/lacunas/mutar.py.txt`: 10 de 10.

## 5 · O que isto não prova

- Nenhum perfil foi aberto: não se sabe se publica com frequência, nem se tem técnico com nome. Isso é o canário
  do robô.
- Os 30 consórcios: a P1g viu a página com data recente. **NÃO SEI** se publicam avisos de defesa datados ou só
  seguro contra granizo. É o `FALTA_PROVAR` de cada um.
- A lista dos «prontos fora da Sala» vem do último estado de cada fonte no livro do Curator. **NÃO SEI** porque a
  coorte da coleta não os inclui: a GAPS-CANDIDATAS já tinha achado 9 assim e ficou sem resposta.

## Anexo · as 91 candidatas na cópia

| CAND (cópia) | Estado | Tipo | Nome | Endereço | Lacunas | Prova de identidade |
|---|---|---|---|---|---|---|
| CAND-1225 | CANDIDATA | FACEBOOK | CNR ISPA — Istituto di Scienze delle Produzioni Alimentari — pagina Fa | https://www.facebook.com/Ispacnr | L1, L2 | https://www.ispa.cnr.it/sede-ispa-di-bari (sha256 5a0b12f272ff…) |
| CAND-1226 | CANDIDATA | FACEBOOK | terraevita.edagricole.it (IT-T3-023) — pagina Facebook | https://www.facebook.com/terraevita.magazine | L1, L2 | https://terraevita.edagricole.it/agrofarmaci-difesa/pero-e-tornata-la-fillossera/ (sha256 5775d72e81b0…) |
| CAND-1227 | POLICY_BLOCK | INSTAGRAM | terraevita.edagricole.it (IT-T3-023) — perfil Instagram | https://www.instagram.com/edagricole_official | L1, L2 | https://terraevita.edagricole.it/agrofarmaci-difesa/pero-e-tornata-la-fillossera/ (sha256 5775d72e81b0…) |
| CAND-1263 | CANDIDATA | ORGANIZACAO | Agridifesa del Mediterraneo | https://agridifesadelmediterraneo.eu/ | L1, L2, L3 | gaps-candidatas-v1:data/derivados/GAPS-CANDIDATAS/MICRO-PROVA-GAPS-LOTE2-CONSORZI.json |
| CAND-1259 | CANDIDATA | ORGANIZACAO | CODIMA Mantova | https://www.codima.info/ | L1, L2, L3 | gaps-candidatas-v1:data/derivados/GAPS-CANDIDATAS/MICRO-PROVA-GAPS-LOTE2-CONSORZI.json |
| CAND-1254 | CANDIDATA | ORGANIZACAO | CODIPACAL — Consorzio di difesa Calabria | https://codipacal.it/ | L1, L2, L3 | gaps-candidatas-v1:data/derivados/GAPS-CANDIDATAS/MICRO-PROVA-GAPS-LOTE2-CONSORZI.json |
| CAND-1270 | CANDIDATA | ORGANIZACAO | CODIPE — Consorzio di difesa (Abruzzo) | https://www.codipe.it/ | L1, L2, L3 | gaps-candidatas-v1:data/derivados/GAPS-CANDIDATAS/MICRO-PROVA-GAPS-LOTE2-CONSORZI.json |
| CAND-1271 | CANDIDATA | ORGANIZACAO | CODIPRA Toscano | https://www.codipratoscano.it/ | L1, L2, L3 | gaps-candidatas-v1:data/derivados/GAPS-CANDIDATAS/MICRO-PROVA-GAPS-LOTE2-CONSORZI.json |
| CAND-1260 | CANDIDATA | ORGANIZACAO | CODIPRA Trento | https://www.codipratn.it/ | L1, L2, L3 | gaps-candidatas-v1:data/derivados/GAPS-CANDIDATAS/MICRO-PROVA-GAPS-LOTE2-CONSORZI.json |
| CAND-1268 | CANDIDATA | ORGANIZACAO | CODIVE | https://www.codive.it/ | L1, L2, L3 | gaps-candidatas-v1:data/derivados/GAPS-CANDIDATAS/MICRO-PROVA-GAPS-LOTE2-CONSORZI.json |
| CAND-1267 | CANDIDATA | ORGANIZACAO | COPROVI | https://www.coprovi.it/ | L1, L2, L3 | gaps-candidatas-v1:data/derivados/GAPS-CANDIDATAS/MICRO-PROVA-GAPS-LOTE2-CONSORZI.json |
| CAND-1265 | CANDIDATA | ORGANIZACAO | COSMAN Piemonte | https://www.cosmanpiemonte.it/ | L1, L2, L3 | gaps-candidatas-v1:data/derivados/GAPS-CANDIDATAS/MICRO-PROVA-GAPS-LOTE2-CONSORZI.json |
| CAND-1278 | CANDIDATA | ORGANIZACAO | Condifesa (condifesa.it) | https://www.condifesa.it/ | L1, L2, L3 | gaps-candidatas-v1:data/derivados/GAPS-CANDIDATAS/MICRO-PROVA-GAPS-LOTE2-CONSORZI.json |
| CAND-1279 | CANDIDATA | ORGANIZACAO | Condifesa Ancona Macerata | https://www.condifesaanmc.it/ | L1, L2, L3 | gaps-candidatas-v1:data/derivados/GAPS-CANDIDATAS/MICRO-PROVA-GAPS-LOTE2-CONSORZI.json |
| CAND-1272 | CANDIDATA | ORGANIZACAO | Condifesa Basilicata | https://www.condifesa-basilicata.it/ | L1, L2, L3 | gaps-candidatas-v1:data/derivados/GAPS-CANDIDATAS/MICRO-PROVA-GAPS-LOTE2-CONSORZI.json |
| CAND-1257 | CANDIDATA | ORGANIZACAO | Condifesa Brescia | https://www.condifesabrescia.it/ | L1, L2, L3 | gaps-candidatas-v1:data/derivados/GAPS-CANDIDATAS/MICRO-PROVA-GAPS-LOTE2-CONSORZI.json |
| CAND-1280 | CANDIDATA | ORGANIZACAO | Condifesa Cagliari | https://www.condifesaca.it/home.html | L1, L2, L3 | gaps-candidatas-v1:data/derivados/GAPS-CANDIDATAS/MICRO-PROVA-GAPS-LOTE2-CONSORZI.json |
| CAND-1275 | CANDIDATA | ORGANIZACAO | Condifesa Catania | https://www.condifesacatania.it/ | L1, L2, L3 | gaps-candidatas-v1:data/derivados/GAPS-CANDIDATAS/MICRO-PROVA-GAPS-LOTE2-CONSORZI.json |
| CAND-1261 | CANDIDATA | ORGANIZACAO | Condifesa Cuneo | https://www.condifesacuneo.it/ | L1, L2, L3 | gaps-candidatas-v1:data/derivados/GAPS-CANDIDATAS/MICRO-PROVA-GAPS-LOTE2-CONSORZI.json |
| CAND-1262 | CANDIDATA | ORGANIZACAO | Condifesa Emilia | https://condifesa-emilia.it/ | L1, L2, L3 | gaps-candidatas-v1:data/derivados/GAPS-CANDIDATAS/MICRO-PROVA-GAPS-LOTE2-CONSORZI.json |
| CAND-1258 | CANDIDATA | ORGANIZACAO | Condifesa FVG | https://www.condifesafvg.it/ | L1, L2, L3 | gaps-candidatas-v1:data/derivados/GAPS-CANDIDATAS/MICRO-PROVA-GAPS-LOTE2-CONSORZI.json |
| CAND-1253 | CANDIDATA | ORGANIZACAO | Condifesa Foggia | http://www.condifesafoggia.it/ | L1, L2, L3 | gaps-candidatas-v1:data/derivados/GAPS-CANDIDATAS/MICRO-PROVA-GAPS-LOTE2-CONSORZI.json |
| CAND-1269 | CANDIDATA | ORGANIZACAO | Condifesa Lombardia (federazione) | https://www.condifesalombardia.it/ | L1, L2, L3 | gaps-candidatas-v1:data/derivados/GAPS-CANDIDATAS/MICRO-PROVA-GAPS-LOTE2-CONSORZI.json |
| CAND-1273 | CANDIDATA | ORGANIZACAO | Condifesa Milano Lodi | https://www.condifesa-mi-lo.it/ | L1, L2, L3 | gaps-candidatas-v1:data/derivados/GAPS-CANDIDATAS/MICRO-PROVA-GAPS-LOTE2-CONSORZI.json |
| CAND-1255 | CANDIDATA | ORGANIZACAO | Condifesa Modena | https://www.condifesamodena.it/ | L1, L2, L3 | gaps-candidatas-v1:data/derivados/GAPS-CANDIDATAS/MICRO-PROVA-GAPS-LOTE2-CONSORZI.json |
| CAND-1276 | CANDIDATA | ORGANIZACAO | Condifesa Novara | https://www.condifesanovara.it/ | L1, L2, L3 | gaps-candidatas-v1:data/derivados/GAPS-CANDIDATAS/MICRO-PROVA-GAPS-LOTE2-CONSORZI.json |
| CAND-1277 | CANDIDATA | ORGANIZACAO | Condifesa Oristano | https://www.condifesaor.it/ | L1, L2, L3 | gaps-candidatas-v1:data/derivados/GAPS-CANDIDATAS/MICRO-PROVA-GAPS-LOTE2-CONSORZI.json |
| CAND-1281 | CANDIDATA | ORGANIZACAO | Condifesa Piemonte | https://www.condifesapiemonte.com/ | L1, L2, L3 | gaps-candidatas-v1:data/derivados/GAPS-CANDIDATAS/MICRO-PROVA-GAPS-LOTE2-CONSORZI.json |
| CAND-1274 | CANDIDATA | ORGANIZACAO | Condifesa Sassari | http://www.condifesa.sassari.it/ | L1, L2, L3 | gaps-candidatas-v1:data/derivados/GAPS-CANDIDATAS/MICRO-PROVA-GAPS-LOTE2-CONSORZI.json |
| CAND-1264 | CANDIDATA | ORGANIZACAO | Condifesa Umbria | https://www.condifesaumbria.it/ | L1, L2, L3 | gaps-candidatas-v1:data/derivados/GAPS-CANDIDATAS/MICRO-PROVA-GAPS-LOTE2-CONSORZI.json |
| CAND-1282 | CANDIDATA | ORGANIZACAO | Condifesa Veneto Est | https://condifesavenetoest.it/ | L1, L2, L3 | gaps-candidatas-v1:data/derivados/GAPS-CANDIDATAS/MICRO-PROVA-GAPS-LOTE2-CONSORZI.json |
| CAND-1256 | CANDIDATA | ORGANIZACAO | Condifesa Vercelli Biella | https://www.condifesa-vcbi.it/ | L1, L2, L3 | gaps-candidatas-v1:data/derivados/GAPS-CANDIDATAS/MICRO-PROVA-GAPS-LOTE2-CONSORZI.json |
| CAND-1266 | CANDIDATA | ORGANIZACAO | Hagelschutzkonsortium (Alto Adige) | https://www.hagelschutzkonsortium.com/ | L1, L2, L3 | gaps-candidatas-v1:data/derivados/GAPS-CANDIDATAS/MICRO-PROVA-GAPS-LOTE2-CONSORZI.json |
| CAND-1224 | CANDIDATA | YOUTUBE | Emilia-Romagna — Servizio Fitosanitario — canal YouTube | https://www.youtube.com/user/Ermesagricoltura | L1, L2 | https://agricoltura.regione.emilia-romagna.it/piani-programmi-progetti (sha256 18ffea3450bd…) |
| CAND-1210 | CANDIDATA | FACEBOOK | AgroNotizie — Image Line — pagina Facebook | https://www.facebook.com/agronotizie | L3 | https://agronotizie.imagelinenetwork.com/notizie-agricoltura-attualita/ (sha256 75a6073b37f1…) |
| CAND-1207 | CANDIDATA | FACEBOOK | Italia Olivicola — pagina Facebook | https://www.facebook.com/italiaolivicolacn | L3 | https://www.italiaolivicola.it/consiglio-di-amministrazione/ (sha256 2483b872cdcb…) |
| CAND-1205 | POLICY_BLOCK | INSTAGRAM | ARSAC Calabria — Azienda Regionale per lo Sviluppo dell'Agricoltura Ca | https://www.instagram.com/arsacweb | L3 | https://arsac.calabria.it/arsac-chi-siamo/ (sha256 0ce7e01d16cc…) |
| CAND-1211 | POLICY_BLOCK | INSTAGRAM | AgroNotizie — Image Line — perfil Instagram | https://www.instagram.com/agronotizie | L3 | https://agronotizie.imagelinenetwork.com/notizie-agricoltura-attualita/ (sha256 75a6073b37f1…) |
| CAND-1208 | POLICY_BLOCK | INSTAGRAM | Rivista di Agraria — perfil Instagram | http://www.instagram.com/agrariaorg | L3 | https://www.rivistadiagraria.org/sezioni/animali-da-compagnia/ (sha256 c10ff98d48b1…) |
| CAND-1206 | POLICY_BLOCK | LINKEDIN | ARSIAL — Agenzia Regionale Sviluppo Innovazione Agricoltura Lazio — pa | https://www.linkedin.com/company/arsial-agenzia-regionale-per-lo-sviluppo-e-l-innovazione-dell-agricoltura-del-lazio | L3 | https://www.arsial.it/pubblicazioni-e-ricerche (sha256 e4aa69c8ee80…) |
| CAND-1212 | CANDIDATA | YOUTUBE | AgroNotizie — Image Line — canal YouTube | https://www.youtube.com/user/agronotizietv | L3 | https://agronotizie.imagelinenetwork.com/notizie-agricoltura-attualita/ (sha256 75a6073b37f1…) |
| CAND-1209 | CANDIDATA | YOUTUBE | Rivista di Agraria — canal YouTube | https://www.youtube.com/user/AgrariaOrg | L3 | https://www.rivistadiagraria.org/sezioni/animali-da-compagnia/ (sha256 c10ff98d48b1…) |
| CAND-1289 | CANDIDATA | CIENCIA | CREA - podcast «TEA alle 5» (serie di 5 episodi sulle Tecniche di Evol | https://www.crea.gov.it/-/il-podcast-del-crea-tea-alle-5-un-format-originale-realizzato-in-occasione-della-biotech-week | L4 | research-media-sources-v1:research/media-sources-v1/ACHADOS.json |
| CAND-1290 | CANDIDATA | CIENCIA | CREA Politiche e Bioeconomia - podcast «Agrifuturo» (Life ADA, adattam | https://www.crea.gov.it/en/web/politiche-e-bioeconomia/-/clima-e-impatto-sull-agricoltura-il-terzo-episodio-del-podcast-agrifuturo-1 | L4 | research-media-sources-v1:research/media-sources-v1/ACHADOS.json |
| CAND-1291 | CANDIDATA | CIENCIA | Rete Rurale Nazionale / Rete PAC - I podcast della Rete Rurale Naziona | https://www.reterurale.it/podcast | L4 | research-media-sources-v1:research/media-sources-v1/ACHADOS.json |
| CAND-1292 | CANDIDATA | IMPRENSA | Radio 24 / Il Sole 24 Ore - «Madre Terra, l'agricoltura in podcast» | https://podcast.ilsole24ore.com/serie/madre-terra--l-agricoltura-podcast-AFkCnd1 | L4 | research-media-sources-v1:research/media-sources-v1/ACHADOS.json |
| CAND-1293 | CANDIDATA | YOUTUBE | agrifake - agricoltura, piante e ambiente (canale YouTube di divulgazi | https://www.youtube.com/channel/UCMfZsQVzUE4oF00c_0nzFVw | L4 | research-media-sources-v1:research/media-sources-v1/ACHADOS.json |
| CAND-1251 | CANDIDATA | FACEBOOK | Agroalimentare News — pagina Facebook | https://www.facebook.com/redazione.agroalimentarenews | L5 | https://www.agroalimentarenews.com/notizie/agroalimentarenews/gli-imprenditori-del-gusto/ (sha256 72b70fdf42da |
| CAND-1236 | CANDIDATA | FACEBOOK | Agrofarma — Federchimica — pagina Facebook | https://www.facebook.com/Agrofarma.agricolturamodomio | L5 | https://agrofarma.federchimica.it/news-ed-eventi/dettaglio-news/2026/06/08/agrofarma-e-federbio-lanciano-il-ma |
| CAND-1228 | CANDIDATA | FACEBOOK | CONAF — Consiglio Ordine Nazionale Dottori Agronomi e Forestali — pagi | https://www.facebook.com/agronomiforestali | L5 | https://www.conaf.it/consiglio-dellordine-nazionale/ (sha256 05342a7aa1d7…) |
| CAND-1233 | CANDIDATA | FACEBOOK | Consorzio di Bonifica della Romagna — pagina Facebook | https://www.facebook.com/bonificadellaromagna | L5 | https://www.bonificaromagna.it/news/settimana-nazionale-della-bonifica-e-della-irrigazione-16-24-maggio-2026 ( |
| CAND-1231 | CANDIDATA | FACEBOOK | FederBio — pagina Facebook | https://www.facebook.com/FederBioItalia | L5 | https://feder.bio/progetti/being-organic-eu-choose-the-european-organic-leaf-for-better-world/ (sha256 394a362 |
| CAND-1245 | CANDIDATA | FACEBOOK | cia-puglia.it (IT-T7-125) — pagina Facebook | https://www.facebook.com/ciaagricoltoripuglia | L5 | https://cia-puglia.it/2023/02/25/emergenza-cinghiali-focus-di-cia-due-mari-con-lassessore-pentassuglia/ (sha25 |
| CAND-1244 | CANDIDATA | FACEBOOK | cia.it (IT-T7-112) — pagina Facebook | https://www.facebook.com/CiaLaspesaincampagna | L5 | https://www.cia.it/news/notizie/agia-cia-umbria-primo-insediamento-dei-giovani-agricoltori-70-mila-sono-unoppo |
| CAND-1240 | CANDIDATA | FACEBOOK | confcooperative.it (IT-T7-103) — pagina Facebook | https://www.facebook.com/confcooperative | L5 | https://www.confcooperative.it/LInformazione/Le-notizie/appalti-pubblici-confcooperative-meglio-la-direttiva-d |
| CAND-1237 | CANDIDATA | FACEBOOK | copagri.org (IT-T7-049) — pagina Facebook | https://www.facebook.com/CopagriAgricoltura | L5 | https://copagri.org/2026/09/11/cordoglio-bonino/ (sha256 4dfe79a1e85a…) |
| CAND-1248 | CANDIDATA | FACEBOOK | florovivaistiitaliani.it (IT-T7-139) — pagina Facebook | https://www.facebook.com/florovivaistiitaliani | L5 | https://www.florovivaistiitaliani.it/inevidenza/buone-notizie-detrazione-per-il-gasolio-anche-per-le-serre-flo |
| CAND-1229 | POLICY_BLOCK | INSTAGRAM | CONAF — Consiglio Ordine Nazionale Dottori Agronomi e Forestali — perf | https://www.instagram.com/ordine_agronomi_e_forestali | L5 | https://www.conaf.it/consiglio-dellordine-nazionale/ (sha256 05342a7aa1d7…) |
| CAND-1234 | POLICY_BLOCK | INSTAGRAM | Consorzio di Bonifica della Romagna — perfil Instagram | https://www.instagram.com/bonificadellaromagna | L5 | https://www.bonificaromagna.it/news/settimana-nazionale-della-bonifica-e-della-irrigazione-16-24-maggio-2026 ( |
| CAND-1232 | POLICY_BLOCK | INSTAGRAM | FederBio — perfil Instagram | https://www.instagram.com/federbioitalia | L5 | https://feder.bio/progetti/being-organic-eu-choose-the-european-organic-leaf-for-better-world/ (sha256 394a362 |
| CAND-1246 | POLICY_BLOCK | INSTAGRAM | cia-puglia.it (IT-T7-125) — perfil Instagram | https://www.instagram.com/ciapuglia | L5 | https://cia-puglia.it/2023/02/25/emergenza-cinghiali-focus-di-cia-due-mari-con-lassessore-pentassuglia/ (sha25 |
| CAND-1241 | POLICY_BLOCK | INSTAGRAM | confcooperative.it (IT-T7-103) — perfil Instagram | https://www.instagram.com/confcooperative_nazionale | L5 | https://www.confcooperative.it/LInformazione/Le-notizie/appalti-pubblici-confcooperative-meglio-la-direttiva-d |
| CAND-1238 | POLICY_BLOCK | INSTAGRAM | copagri.org (IT-T7-049) — perfil Instagram | https://www.instagram.com/copagri_agricoltura | L5 | https://copagri.org/2026/09/11/cordoglio-bonino/ (sha256 4dfe79a1e85a…) |
| CAND-1249 | POLICY_BLOCK | INSTAGRAM | florovivaistiitaliani.it (IT-T7-139) — perfil Instagram | https://www.instagram.com/florovivaisti.italiani | L5 | https://www.florovivaistiitaliani.it/inevidenza/buone-notizie-detrazione-per-il-gasolio-anche-per-le-serre-flo |
| CAND-1230 | POLICY_BLOCK | LINKEDIN | Consorzio di Bonifica Est Ticino Villoresi — pagina LinkedIn | https://www.linkedin.com/company/est-ticino-villoresi | L5 | https://etvilloresi.it/news/imprese/la-carovana-del-po-un-viaggio-per-raccontare-il-grande-fiume/ (sha256 9c35 |
| CAND-1235 | POLICY_BLOCK | LINKEDIN | Consorzio di Bonifica della Romagna — pagina LinkedIn | https://www.linkedin.com/company/consorzio-di-bonifica-della-romagna | L5 | https://www.bonificaromagna.it/news/settimana-nazionale-della-bonifica-e-della-irrigazione-16-24-maggio-2026 ( |
| CAND-1250 | POLICY_BLOCK | LINKEDIN | casalasco.com (IT-T7-163) — pagina LinkedIn | https://it.linkedin.com/company/gruppo-casalasco | L5 | https://www.casalasco.com/it/news/a-tuttofood-2026-con-filiera-integrata-e-nuove-referenze (sha256 c4bf3d292ea |
| CAND-1242 | POLICY_BLOCK | LINKEDIN | confcooperative.it (IT-T7-103) — pagina LinkedIn | https://www.linkedin.com/company/confcooperative-nazionale | L5 | https://www.confcooperative.it/LInformazione/Le-notizie/appalti-pubblici-confcooperative-meglio-la-direttiva-d |
| CAND-1239 | POLICY_BLOCK | LINKEDIN | copagri.org (IT-T7-049) — pagina LinkedIn | https://www.linkedin.com/company/7091586 | L5 | https://copagri.org/2026/09/11/cordoglio-bonino/ (sha256 4dfe79a1e85a…) |
| CAND-1295 | CANDIDATA | ORGANIZACAO | ANBI — eventi | https://www.anbi.it/p/eventi | L5 | vozes-agronomos-v1:data/derivados/VOZES-AGRONOMOS/PLANO-PROGRAMAS.json |
| CAND-1294 | CANDIDATA | ORGANIZACAO | CRPV — eventi e webinar | https://www.crpv.it/it/eventi/ | L5 | vozes-agronomos-v1:data/derivados/VOZES-AGRONOMOS/PLANO-PROGRAMAS.json |
| CAND-1252 | CANDIDATA | YOUTUBE | Agroalimentare News — canal YouTube | https://www.youtube.com/@AgroalimentareNews-i2o | L5 | https://www.agroalimentarenews.com/notizie/agroalimentarenews/gli-imprenditori-del-gusto/ (sha256 72b70fdf42da |
| CAND-1283 | CANDIDATA | YOUTUBE | Agroter / Italiafruit News — canal YouTube | https://www.youtube.com/user/AgroterVideo | L5 | https://www.italiafruit.net/ (sha256 61b4bd233e91…) |
| CAND-1285 | CANDIDATA | YOUTUBE | Biolchim — canal YouTube | https://www.youtube.com/@BiolchimSpA | L5 | https://www.biolchim.com/ (sha256 f923d593ec41…) |
| CAND-1286 | CANDIDATA | YOUTUBE | Diachem — canal YouTube | https://www.youtube.com/@diachem | L5 | https://www.diachem.it/ (sha256 4f7e72b1cbe8…) |
| CAND-1284 | CANDIDATA | YOUTUBE | PSR Calabria — canal YouTube do Programa de Desenvolvimento Rural | https://www.youtube.com/channel/UCE3BgIE0ztA9PXEv6oxI-LQ | L5 | http://www.calabriapsr.it/ (sha256 ff0a94a0b7c4…) |
| CAND-1287 | CANDIDATA | YOUTUBE | Sipcam Italia — canal YouTube | https://www.youtube.com/channel/UC8Uto03To7JFiY6HM1PAb7Q | L5 | https://www.sipcam.com/it/it/ (sha256 db7699e96c99…) |
| CAND-1288 | CANDIDATA | YOUTUBE | Terremerse — canal YouTube | https://www.youtube.com/user/TerremerseCoop | L5 | https://terremerse.it/ (sha256 e2d87a055577…) |
| CAND-1247 | CANDIDATA | YOUTUBE | cia-puglia.it (IT-T7-125) — canal YouTube | https://www.youtube.com/channel/UCM8JcsONXN0CtvzVlg5gu_Q | L5 | https://cia-puglia.it/2023/02/25/emergenza-cinghiali-focus-di-cia-due-mari-con-lassessore-pentassuglia/ (sha25 |
| CAND-1243 | CANDIDATA | YOUTUBE | confcooperative.it (IT-T7-103) — canal YouTube | https://www.youtube.com/channel/UCa-kAP4a07ZVO2z1im4JCEw | L5 | https://www.confcooperative.it/LInformazione/Le-notizie/appalti-pubblici-confcooperative-meglio-la-direttiva-d |
| CAND-1219 | CANDIDATA | FACEBOOK | Consorzio di Tutela Arancia Rossa di Sicilia IGP — pagina Facebook | https://www.facebook.com/aranciarossadisiciliaigp | L6 | https://www.tutelaaranciarossa.it/la-storia-arancia/ (sha256 a0458ef9bf57…) |
| CAND-1214 | CANDIDATA | FACEBOOK | ISMEA — Istituto di Servizi per il Mercato Agricolo Alimentare — pagin | https://www.facebook.com/IsmeaOfficial | L6 | https://www.ismea.it/istituto-di-servizi-per-il-mercato-agricolo-alimentare (sha256 2acfda246430…) |
| CAND-1220 | CANDIDATA | FACEBOOK | Myfruit.it — pagina Facebook | https://www.facebook.com/myfruit.webmagazine | L6 | https://www.myfruit.it/news/aldi-in-uk-il-super-hub-dellortofrutta (sha256 a2fb09ab323e…) |
| CAND-1221 | CANDIDATA | FACEBOOK | WineNews — pagina Facebook | https://www.facebook.com/winenewsit | L6 | https://winenews.it/it/rassegna-stampa/dicono-di-noi/ (sha256 75891c27a738…) |
| CAND-1215 | POLICY_BLOCK | INSTAGRAM | ISMEA — Istituto di Servizi per il Mercato Agricolo Alimentare — perfi | https://www.instagram.com/ismeaofficial | L6 | https://www.ismea.it/istituto-di-servizi-per-il-mercato-agricolo-alimentare (sha256 2acfda246430…) |
| CAND-1222 | POLICY_BLOCK | INSTAGRAM | WineNews — perfil Instagram | https://www.instagram.com/winenewsit | L6 | https://winenews.it/it/rassegna-stampa/dicono-di-noi/ (sha256 75891c27a738…) |
| CAND-1217 | POLICY_BLOCK | LINKEDIN | Borsa Merci Bologna — Camera di Commercio — pagina LinkedIn | https://www.linkedin.com/company/camera-di-commercio-di-bologna | L6 | https://www.bo.camcom.gov.it/it/blog/un-milione-di-euro-trattenere-i-giovani-bologna-domande-entro-il-1610 (sh |
| CAND-1213 | POLICY_BLOCK | LINKEDIN | ISMEA — Istituto di Servizi per il Mercato Agricolo Alimentare — pagin | https://it.linkedin.com/company/ismeaofficial | L6 | https://www.ismea.it/istituto-di-servizi-per-il-mercato-agricolo-alimentare (sha256 2acfda246430…) |
| CAND-1218 | CANDIDATA | YOUTUBE | Borsa Merci Bologna — Camera di Commercio — canal YouTube | https://www.youtube.com/channel/UCjet0E9KAYODh3PKT9TV29w | L6 | https://www.bo.camcom.gov.it/it/blog/un-milione-di-euro-trattenere-i-giovani-bologna-domande-entro-il-1610 (sh |
| CAND-1216 | CANDIDATA | YOUTUBE | ISMEA — Istituto di Servizi per il Mercato Agricolo Alimentare — canal | https://www.youtube.com/user/IsmeaServizi | L6 | https://www.ismea.it/istituto-di-servizi-per-il-mercato-agricolo-alimentare (sha256 2acfda246430…) |
| CAND-1223 | CANDIDATA | YOUTUBE | Plantgest — banca dati varieta — canal YouTube | http://www.youtube.com/channel/UCXvOIVSOJkpAR4OadfgDlBw | L6 | https://plantgest.imagelinenetwork.com/it/eventi/giornate-tecniche-sul-noce-da-frutto/63565 (sha256 7775b48cb1 |
