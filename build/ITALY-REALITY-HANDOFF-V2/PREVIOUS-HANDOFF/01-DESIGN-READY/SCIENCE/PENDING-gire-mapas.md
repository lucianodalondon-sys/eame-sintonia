# GIRE — MAPAS NACIONAIS DE RESISTÊNCIA

**Pendência FECHADA.** Os 22 mapas foram abertos e lidos. Eles **não são imagem**: são camadas vetoriais GML com nome do *comune*, **REGIÃO** e um campo de contagem. A lacuna anterior tinha uma causa única e concreta, documentada abaixo.

Coleta em 02/09/2026, saindo de IP brasileiro (`179.172.231.127`, AS26599 Telefônica Brasil, São Paulo — `ipinfo.io`). Nenhum 403, nenhum WAF. O obstáculo não era de rede.

---

## 1. POR QUE OS MAPAS NÃO ABRIAM: o link do site aponta para um domínio que não existe mais

No índice de espécies, cada link "Mappa" é um `javascript:finestra(...)` para **`cl2.agriserv.org`**:

> `Mappa (frumento) <a class="redColor" href=javascript:finestra('http://cl2.agriserv.org/agri_test/index.php/mappe_stat/gire/index.php?map=1&id_GenSp=203,202,201&id_HRAC=1&id_colt=3,4&pop=1')>ACCasi</a>`
> — HTML de `http://gire.mlib.cnr.it/index.php?sel=specieCoinvolte`, linha 260

**`agriserv.org` está em NXDOMAIN — o domínio inteiro, não só o subdomínio.** Confirmado em 5 caminhos independentes (resolvedor local 192.168.15.1; `8.8.8.8`; `1.1.1.1`; DoH Google; DoH Cloudflare). A resposta vem do próprio registro `.org`:

> `{"Status":3,...,"Authority":[{"name":"org","type":6,...,"data":"a0.org.afilias-nst.info. hostmaster.donuts.email. ..."}]}`
> — `https://cloudflare-dns.com/dns-query?name=cl2.agriserv.org&type=A`

`curl` devolve `HTTP=000` (sem conexão). **Não é bloqueio de IP** — Status 3 é NXDOMAIN autoritativo do TLD. Uma janela gráfica falharia igual.

**Mas a mesma aplicação está viva em outro host, e o próprio GIRE já aponta para ele.** No menu do site, "Mappe di resistenza" leva a:

> `href="http://agrovoltaico.org/agri_test/index.php/mappe/pagedef/IT"`

O site foi migrado pela metade: o **menu** foi atualizado para `agrovoltaico.org`, os **links por espécie** ficaram no `cl2.agriserv.org` morto. Trocando o host na mesma query string, os 22 mapas abrem (HTTP 200). Foi o que fiz.

`agriserv.eu` (site do desenvolvedor, citado no rodapé da aplicação) resolve normalmente em `81.91.86.14` — só o domínio `.org` caducou.

---

## 2. O QUE O MAPA MOSTRA — a unidade é o COMUNE, e é qualitativo por decisão do GIRE

Da página de apresentação do sistema (iMAR), citação literal:

> "Il sistema si basa sulla mappa ISTAT dei comuni italiani. La missione del GIRE non é quella di fornire il numero di popolazioni resistenti, ma dare un'indicazione delle aree interessate dai vari tipi di resistenza sul territorio nazionale. Le mappe, pertanto, **non forniscono indicazioni quantitative ma qualitative**, cioé il territorio di un comune é colorato quando é stata confermata la presenza di una popolazione resistente ad almeno un erbicida."
> — `http://agrovoltaico.org/agri_test/index.php/mappe/pagedef/IT`

Isto é decisivo para a régua do piloto: **o mapa não é um mapa de incidência.** Um comune pintado = pelo menos um caso confirmado ali, nada além. Um comune pintado e um comune vizinho branco não dizem "mais" e "menos".

### Estrutura técnica lida

O mapa é OpenLayers sobre um GML gerado por requisição:

> `<script>file2gml_js[0]='/agri_test/gml/gmlFile_A_e250ab32ecac2a7c3302051232149f5d.gml'; </script>`

Cada `featureMember` traz `<ogr:nome_comuni>`, `<ogr:regioni>`, `<ogr:numerosita>`, `<ogr:id>` (código ISTAT). Exemplo real:

> `F0 {'id': '1018', 'nome_comuni': 'Alessandria', 'regioni': 'PIEMONTE', 'numerosita': '1'}`

**O campo `numerosita` existe no dado mas está deliberadamente escondido na interface.** Em `js/map4agriinfest3.js` a linha que o exibiria está comentada:

> `var titles = new Array("--"`
> `//"<b style='':>N. =</b>"+ numerosita + "<b style='':>&nbsp; casi osservati</b>",`

Ou seja: o popup só mostra `Nome comune`. Coerente com a frase "non forniscono indicazioni quantitative". **Recomendo não usar `numerosita` como número no pacote** — o rótulo "casi osservati" está num trecho de código desligado, sem definição publicada e sem período de referência.

### Legenda (chave de cores, literal do código)

> `fillColors={A:"red", B:"blue", C1:"#00FF00", C2:"#00CC00", C3:"#006600", F2:"aqua", G:"sienna", H:"olive", O:"brown"}`

| id_HRAC na URL | Grupo HRAC | Rótulo impresso no mapa | Cor |
|---|---|---|---|
| 1 | A | `ACCase inhib. (A)` | vermelho |
| 2 | B | `ALS inhib. (B)` | azul |
| 4 | C2 | *(rótulo vem vazio)* | `#00CC00` |
| 11 | G | `EPSPs inhib. (G)` | sienna |
| 19 | O | `Synthetic Auxins (O)` | brown |

---

## 3. OS 22 MAPAS — regiões marcadas, uma linha por mapa

Contagem = *comuni* distintos marcados naquela camada. **Fonte:** GIRE® — Banca dati sulla resistenza agli erbicidi in Italia, mapas estáticos iMAR. **Geografia:** Itália, unidade *comune* (mapa ISTAT). **Data de publicação da aplicação de mapas:** "Ultimo aggiornamento in data 30/10/2022." **Período de referência dos casos: NÃO DECLARADO** (ver seção 7). **Data de acesso:** 02/09/2026.

| Espécies no painel | Cultura | HRAC | Legenda | Comuni | Regiões marcadas (nº de comuni) |
|---|---|---|---|---|---|
| Alisma plantago-aquatica | riso | B | ALS inhib. (B) | 42 | Piemonte (29), Lombardia (13) |
| Amaranthus hybridus; palmeri; retroflexus; spp.; tuberculatus | dicot. estive | B | ALS inhib. (B) | 80 | Friuli-Venezia Giulia (45), Veneto (24), Emilia-Romagna (8), Lombardia (3) |
| Avena fatua; spp.; sterilis | frumento | A | ACCase inhib. (A) | 59 | Emilia-Romagna (18), Marche (15), Puglia (12), Sicilia (8), Basilicata (3), Piemonte (1), Abruzzo (1), Molise (1) |
| Avena fatua; spp.; sterilis | frumento | B | ALS inhib. (B) | 18 | Puglia (7), Marche (5), Emilia-Romagna (3), Sicilia (2), Basilicata (1) |
| Conyza spp. | colt. arboree | G | EPSPs inhib. (G) | 11 | Emilia-Romagna (4), Piemonte (2), Veneto (2), Puglia (2), Sicilia (1) |
| Cyperus difformis | riso | B | ALS inhib. (B) | 30 | Piemonte (15), Lombardia (11), Veneto (1), Emilia-Romagna (1), Calabria (1), Sardegna (1) |
| Digitaria sanguinalis | dicotiledoni estive | A | ACCase inhib. (A) | 1 | Veneto (1) |
| Echinochloa crus-galli; spp. | mais | B | ALS inhib. (B) | 32 | Veneto (12), Piemonte (8), Emilia-Romagna (7), Lombardia (3), Toscana (1), Abruzzo (1) |
| Echinochloa spp. | Riso | A | ACCase inhib. (A) | 8 | Piemonte (5), Emilia-Romagna (2), Lombardia (1) |
| Echinochloa crus-galli; erecta; hispidula; spp. | Riso | B | ALS inhib. (B) | 87 | Piemonte (37), Lombardia (37), Emilia-Romagna (5), Veneto (4), Sardegna (3), Calabria (1) |
| **(painel vazio)** | Riso | C2 | **(vazia)** | **0** | **(nenhuma)** — ver 3.1 |
| Lolium multiflorum; rigidum; spp. | frumento | A | ACCase inhib. (A) | 49 | Toscana (12), Marche (8), Lazio (6), Puglia (6), Emilia-Romagna (5), Lombardia (3), Piemonte (2), Umbria (2), Abruzzo (2), Veneto (1), Campania (1), Basilicata (1) |
| Lolium multiflorum; spp. | frumento | B | ALS inhib. (B) | 15 | Marche (6), Toscana (5), Lazio (2), Piemonte (1), Emilia-Romagna (1) |
| Lolium spp. | medica | A | ACCase inhib. (A) | 3 | Emilia-Romagna (3) |
| Lolium rigidum; spp. | colt. arboree | G | EPSPs inhib. (G) | 15 | Puglia (6), Piemonte (4), Trentino-Alto Adige (1), Veneto (1), Emilia-Romagna (1), Toscana (1), Calabria (1) |
| Oryza sativa | riso | B | ALS inhib. (B) | 53 | Lombardia (29), Piemonte (23), Emilia-Romagna (1) |
| Papaver rhoeas | frumento | B | ALS inhib. (B) | 45 | Sicilia (10), Puglia (9), Emilia-Romagna (6), Veneto (4), Toscana (4), Marche (3), Lazio (3), Piemonte (2), Lombardia (1), Umbria (1), Basilicata (1), Sardegna (1) |
| Papaver rhoeas | frumento | O | Synthetic Auxins (O) | 1 | Lazio (1) |
| Phalaris brachystachys; paradoxa; spp. | frumento | A | ACCase inhib. (A) | 7 | Puglia (4), Marche (1), Lazio (1), Molise (1) |
| Schoenoplectus mucronatus | riso | B | ALS inhib. (B) | 45 | Piemonte (31), Lombardia (13), Veneto (1) |
| Sinapis arvensis | frumento | B | ALS inhib. (B) | 9 | Sicilia (3), Toscana (2), Lazio (2), Emilia-Romagna (1), Marche (1) |
| Sorghum halepense | dicot. estive | A | ACCase inhib. (A) | 9 | Lombardia (5), Veneto (3), Friuli-Venezia Giulia (1) |

### 3.1 O mapa vazio — Echinochloa / Riso / Propanile (C2) — é um ESTADO, não um zero

A página monta a camada e gera o GML, mas o GML volta **válido e sem nenhuma feature**, com *bounding box* zerada:

> `<gml:coord><gml:X>0</gml:X><gml:Y>0</gml:Y></gml:coord>`
> — `gmlFile_C2_9fe37ae8f27be68fa6a27dc386a09a71.gml`, 494 bytes

E o rótulo da legenda vem vazio: `descrizione_HRAC[0]='';`. A página troca o painel de informação por um `<span id='avviso'>` vazio.

O site oferece o link "Mappa (Riso) Propanile", **e o mapa abre sem nada pintado e sem legenda.** Não sei se a base não tem registro para essa combinação ou se a consulta está quebrada (o rótulo vazio sugere falha de junção no banco). **Isso não autoriza dizer que não há casos.**

---

## 4. TABELA-RESUMO: região × mecanismo

Comuni distintos marcados, somando todos os 22 mapas (um comune que aparece em dois mapas do mesmo mecanismo conta duas vezes se espécie/cultura diferem).

| Região | A (ACCase) | B (ALS) | G (EPSP) | O (auxinas) | C2 | Total |
|---|---:|---:|---:|---:|---:|---:|
| Piemonte | 8 | 146 | 6 | 0 | 0 | **160** |
| Lombardia | 9 | 110 | 0 | 0 | 0 | **119** |
| Emilia-Romagna | 28 | 33 | 5 | 0 | 0 | **66** |
| Veneto | 5 | 46 | 3 | 0 | 0 | **54** |
| Friuli-Venezia Giulia | 1 | 45 | 0 | 0 | 0 | **46** |
| Puglia | 22 | 16 | 8 | 0 | 0 | **46** |
| Marche | 24 | 15 | 0 | 0 | 0 | **39** |
| Toscana | 12 | 12 | 1 | 0 | 0 | **25** |
| Sicilia | 8 | 15 | 1 | 0 | 0 | **24** |
| Lazio | 7 | 7 | 0 | 1 | 0 | **15** |
| Basilicata | 4 | 2 | 0 | 0 | 0 | **6** |
| Sardegna | 0 | 5 | 0 | 0 | 0 | **5** |
| Abruzzo | 3 | 1 | 0 | 0 | 0 | **4** |
| Calabria | 0 | 2 | 1 | 0 | 0 | **3** |
| Umbria | 2 | 1 | 0 | 0 | 0 | **3** |
| Molise | 2 | 0 | 0 | 0 | 0 | **2** |
| Campania | 1 | 0 | 0 | 0 | 0 | **1** |
| Trentino-Alto Adige | 0 | 0 | 1 | 0 | 0 | **1** |
| **Soma** | **136** | **456** | **26** | **1** | **0** | **619** |

**427 comuni distintos** (região + nome) aparecem marcados no conjunto dos 22 mapas; 619 marcações comune×camada.

**18 regiões aparecem. Liguria e Valle d'Aosta não aparecem em nenhum mapa** — e isto não é um acaso dos mapas estáticos: o menu suspenso de região do sistema **dinâmico** oferece exatamente as mesmas 18, sem Liguria e sem Valle d'Aosta. Ou seja, essas duas regiões não estão na base. Não sei se é ausência de casos, ausência de amostragem, ou recorte de escopo.

---

## 5. O SISTEMA DINÂMICO REVELA QUE OS 22 MAPAS SÃO UM SUBCONJUNTO

Na página `http://agrovoltaico.org/agri_test/index.php/mappe/gire/` (base OpenStreetMap) os quatro filtros trazem:

- **Espécies: 31.** Nove não têm mapa estático no índice: *Alopecurus myosuroides*, *Amaranthus spp.*, *Avena fatua*, *Avena spp.*, *Echinochloa erecta*, *Echinochloa hispidula*, *Echinochloa spp.*, *Phalaris brachystachys*, *Phalaris spp.*, *Panicum dichotomiflorum*, *Cyperus esculentus*.
- **Regiões: 18** (as mesmas da tabela acima).
- **Culturas: 19** — `agric. conservativa: non lavorazione, arboree, arboree: nocciolo, arboree: olivo, arboree: vite, bietola, dicotiledoni estive, dicotiledoni estive: soia, favino, foraggere: medica, foraggere: trifoglio, frumento, frumento: frumento duro, frumento: frumento tenero, girasole, mais, orzo, riso, terreno incolto`.
- **Tipo de resistência: 8 opções de "Resistenza singola" + 8 de "Resistenza multipla".**

**Existe mapa de RESISTÊNCIA MÚLTIPLA e eu não o li.** Os rótulos do menu vêm **vazios no HTML** (só o `+` sobrevive: `<option value="14"> + + </option>`) — são imagens/símbolos que não renderizam em texto. Não consegui saber quais combinações são as 8, nem gerar essas camadas.

---

## 6. AS DUAS PÁGINAS PEDIDAS

### 6.1 "Linee guida specifiche" — `index.php?sel=lineeGuidaSpec`

Página é um índice de **10 PDFs**. Todos baixados (HTTP 200) e com texto extraível — nenhum é imagem. Texto salvo no repositório.

| Guia | PDF | Data no documento | Caracteres |
|---|---|---|---|
| Cereali autunno-vernini | `Linee_guida_cereali.pdf` | "aggiornate a Marzo 2026" | 16.022 |
| Riso | `Linee_guida_riso.pdf` | "aggiornate a marzo 2026" | 24.937 |
| Colture arboree | `Linee_guida_arboree.pdf` | "aggiornate al 2 marzo 2026" | 15.224 |
| Colture sarchiate | `Linee_guida_colture_sarchiate.pdf` | "aggiornate a Marzo 2026" | 20.869 |
| Riso tollerante (Clearfield®/FullPage®/Provisia®/Max-Ace®) | `Linee_guida_Clearfield_Provisia_2026.pdf` | "(marzo 2026)" | 13.941 |
| Barbabietola CONVISO® SMART | `Linee_guida_Conviso_Smart.pdf` | "aggiornate a Marzo 2026" | 8.736 |
| Agricoltura conservativa | `linee_guida_agricoltura_conservativa.pdf` | **sem data no texto** | 9.925 |
| Amaranthus em soia | `linee_guida_AMA_soia_marzo2022.pdf` | "aggiornate a marzo 2022" | 9.509 |
| Erba medica (FOP) | `linee_guida_medica.pdf` | **sem data no texto** | 6.273 |
| Girasole tolerante ALS | `linee_guida_girasole_2016.pdf` | "aggiornate ad aprile 2016" | 3.597 |

**As guias são mais recentes e mais geograficamente precisas que os mapas** — os mapas são de 2022, as guias de março de 2026, e trazem casos de 2024 e 2025 que os mapas ainda não mostram. Citações literais, sempre com a geografia que o próprio texto usa (Lei 4 — província não é região):

> "Nel 2025 è stato accertato il primo caso di resistenza multipla agli inibitori dell'ALS e ACCasi in mais in Emilia-Romagna nel comune di Lagosanto in provincia di Ferrara." — *Linee guida colture sarchiate*, marzo 2026

> "Nel 2024 è stata accerta una popolazione di Panicum dichotomiflorum resistente agli erbicidi inibitori dell'ALS (imazamox e nicosulfuron) in mais campionata in Piemonte nel comune di Santhià in provincia di Vercelli." — *idem*

> "Nel 2025 è stata accertata la presenza di una popolazione di riso crodo resistente sia a cicloxydim che a quizalofop-P-ethyl; la popolazione proviene dalla provincia di Vercelli, più precisamente da risaie all'interno del comune di Lignana. Si tratta del primo caso in Italia." — *Linee guida Clearfield/Provisia*, marzo 2026

> "Nel 2024, inoltre, è stata confermata la presenza dei primi due casi di Echinochloa spp con resistenza incrociata a tutti e quattro gli inibitori ACCasi autorizzati per il riso in Italia (cyhalofop-ethyl, profoxydim, cicloxydim e quizalofop-ethyl)." — *Linee guida riso*, marzo 2026

> "In aggiunta, sono stati recentemente confermati in Veneto tre casi di Amaranthus palmeri resistente agli erbicidi inibitori dell'ALS." — *Linee guida colture sarchiate* e *AMA soia*

> "nel 2024 sono state accertate due popolazione di Sorghum halepense resistenti agli erbicidi inibitori dell'ACCasi: la prima in Veneto nella provincia di Vicenza con resistenza incrociata alle classi 'fop' e 'dim', mentre la seconda in Fiuli-Venezia Giulia nella provincia di Udine con resistenza alla sola classe dei 'fop'." — *Linee guida colture sarchiate*

> "La resistenza agli erbicidi in agricoltura conservativa in Italia interessa il Lolium spp. ed il glifosate nella parte orientale della provincia di Venezia. Nella primavera 2015 è stata segnalata..." — *Linee guida agricoltura conservativa*

> "...arrivavano da colture di vite ma anche nocciolo in provincia di Asti, da oliveti nella Puglia centro-meridionale e Calabria e, di recente da frutteti della provincia di Bolzano. Per quanto riguarda la Conyza sp., i primi casi sono stati osservati in un oliveto della provincia di Bari ed un agrumeto della provincia di Catania." — *Linee guida arboree*, 2 marzo 2026

**Ponte direta com os mapas** — as guias explicam por que o mapa é sempre incompleto:

> "È comunque buona norma, alla comparsa dei primi casi di minore sensibilità agli erbicidi di post emergenza sopra elencati, prelevare semi delle popolazioni individuate e **segnalare al gruppo GIRE la loro presenza**, per promuovere le misure necessarie al contenimento della diffusione del problema resistenze ed **aggiornare le mappe esistenti con i dati raccolti**." — *Linee guida cereali*, marzo 2026

E a própria guia lista, entre as escolhas que agravam o problema: *"Non segnalare la presenza di popolazioni non sensibili ai prodotti impiegati"*. **O mapa é alimentado por notificação voluntária.** Comune branco = ninguém notificou; pode ou não significar ausência.

### 6.2 "Classificazione erbicidi" — `documentsSource/Classificazione_erbicidi.html`

Tabela completa **Grupo HRAC → Meccanismo d'azione → Famiglia chimica → Principio attivo**, lida na íntegra (147.841 bytes brutos, 4.029 de texto). Grupos presentes: **A, B, C1, C2, C3, D, E, F1, F2, F3, G, H, K1, K2, K3, L, N, O, Z**. (Sem F4, sem I, sem J, sem M.) O grupo **L aparece duplicado** no HTML, com o mesmo conteúdo (`Benzammidi / isoxaben`) — na primeira vez também com `Chinoline / Quinclorac ***`.

Três notas de rodapé regem a leitura:

> "(*) principio attivo non commercializzato al momento"
> "(**) uso straordinario per 120 giorni, dal 1 Aprile al 29 Luglio"
> "(***) uso straordinario per 120 giorni, dal 17 Aprile"

**Isto amarra o mapa vazio do Propanile.** Na tabela, `Propanil` está no grupo **C2 / Uree+Ammidi**, marcado `**` — uso extraordinário de 120 dias. É a única substância C2 com essa marca, junto de `isoproturon *` (não comercializado). Não afirmo relação causal, mas registro que o único mapa vazio é o do único mecanismo cuja substância está sob autorização excepcional.

**Alerta de proveniência — este arquivo é mais velho do que parece.** É um HTML exportado do Word e os metadados internos estão intactos:

> `<o:LastAuthor>Scarabel</o:LastAuthor>` · `<o:Company>The Dow Chemical Company</o:Company>` · `<o:Created>2014-04-24T13:42:00Z</o:Created>` · `<o:LastSaved>2014-04-24T13:42:00Z</o:LastSaved>`

O corpo do arquivo traz ainda `2012-11-20T16:03:00Z`, `DALLAVALLE@dow.com` e "Lista esbicidi aggiornata". **A página de classificação de herbicidas que o GIRE publica hoje foi salva pela última vez em 24/04/2014, num documento de origem Dow Chemical.** A página que a hospeda diz "Ultimo aggiornamento in data 26/08/2026", mas isso é o rodapé do site, não do documento. Quem usar essa tabela como lista de substâncias autorizadas hoje vai errar por 12 anos.

---

## 7. TRÊS DATAS DIFERENTES — não confundir

| O quê | Data | Citação |
|---|---|---|
| Rodapé do site GIRE | 26/08/2026 | "Ultimo aggiornamento in data 26/08/2026" |
| Aplicação de mapas (iMAR) | 30/10/2022 | "Ultimo aggiornamento in data 30/10/2022. Applicazione realizzata da AgriSERV" |
| Tabela de classificação HRAC | 24/04/2014 | `<o:LastSaved>2014-04-24T13:42:00Z</o:LastSaved>` |
| Linee guida (a maioria) | março/2026 | ver 6.1 |

**O carimbo que aparece dentro do mapa é armadilha.** Cada mapa exibe `<div class='bluTit'>02 Sep 26 - 08:14</div>` — é a **hora em que eu pedi a página**, não a data do dado. Reabri o mesmo mapa três vezes e o carimbo mudou junto com o relógio.

O site também avisa que saiu do ar por mais de um mês:

> "Alcuni utenti si saranno già accorti che il sito GIRE non ha funzionato per più di un mese a causa di problemi tecnici con il server."

**Forma de citação exigida pela fonte** (o site proíbe uso sem citar: *"E' vietato l'uso del materiale pubblicato in questo sito, a meno che non venga citata la fonte"*):

> GIRE®. Gruppo Italiano di lavoro sulla Resistenza agli Erbicidi, 2026. Banca dati sulla resistenza agli erbicidi in Italia. Disponibile in rete: www.resistenzaerbicidi.it (visitato il: 2026-09-02)

---

## 8. ARQUIVOS GRAVADOS

- `C:\eame-sintonia\data\samples\IT-GIRE-MAPAS\gire-mapas-nacionais.json` — 98.942 bytes. Os 22 mapas, cada um com URL original e URL viva, legenda, cor, espécies do painel, caminho do GML, e a lista completa dos comuni com `id` ISTAT, `nome_comuni`, `regioni`, `numerosita`.
- `C:\eame-sintonia\data\samples\IT-GIRE-MAPAS\linee-guida\` — 10 arquivos `.txt`, texto integral das guias.
- `C:\eame-sintonia\scripts\gire_mapas.py` — o coletor. Faz a troca de host `cl2.agriserv.org` → `agrovoltaico.org` e reexecuta tudo. Sem credencial, sem custo.

Nota operacional para quem rodar de novo: os nomes dos GML são hashes gerados **por requisição** (a mesma consulta devolveu `gmlFile_A_e250ab32...` e depois `gmlFile_A_9edbf436...`). Não dá para guardar a URL do GML e buscar depois — tem que abrir o mapa e o GML no mesmo fôlego, que é o que o script faz. O servidor devolve HTTP 500 esporádico (aconteceu 1 vez em 22, com *Oryza*, e passou na primeira retentativa).

---

## O QUE CONTINUA NÃO SEI

1. **Qual é o período de referência dos mapas.** Nenhuma página, nenhum GML e nenhum popup declaram de quando são os casos, nem a data do caso mais antigo ou mais recente. A aplicação diz "Ultimo aggiornamento in data 30/10/2022" — mas isso é a data da *aplicação*, não do *dado*. Sem isso, nenhum número desta pesquisa pode ir para o pacote como série temporal.
2. **O que exatamente é `numerosita`.** O campo existe em todo comune. O único rótulo que já existiu para ele — "casi osservati" — está numa linha comentada do JavaScript. Não achei definição publicada, nem denominador, nem janela de tempo. Somei os valores só para conferir a leitura; **não recomendo publicar essa soma.**
3. **Os 8 mapas de resistência múltipla.** Existem no sistema dinâmico (`<optgroup label="Resistenza multipla">`, valores 9 a 16), mas os rótulos vêm vazios no HTML — são imagens. Não sei quais combinações de mecanismo são, e não gerei essas camadas. É o próximo passo óbvio, e provavelmente exige janela gráfica para ler os ícones.
4. **Por que o mapa Echinochloa/Riso/Propanile (C2) volta vazio.** GML válido, zero features, legenda vazia. Pode ser base sem registro; pode ser consulta quebrada. Não distingui as duas hipóteses.
5. **Se Liguria e Valle d'Aosta estão ausentes por não terem casos ou por não estarem no escopo.** Elas não aparecem em nenhum mapa **e** não constam do menu de regiões do sistema dinâmico. A ausência é da base, não da minha leitura — mas o motivo não está escrito em lugar nenhum.
6. **A página "Istruzioni" dos mapas não renderiza.** `http://agrovoltaico.org/agri_test/index.php/mappe/istruzioni/` devolve HTTP 200 mas o corpo é só ruído de PHP (`Undefined offset: 0 · Filename: views/istruzioni.php · Line Number: 218`). A versão em `gire.ipsp.cnr.it` dá 404. **A explicação oficial da legenda está inacessível** — a chave de cores que apresentei foi lida do código-fonte do mapa (`fillColors={...}`), não de uma página de instruções. É leitura de código, não documentação da fonte.
7. **Nove espécies do sistema dinâmico não têm mapa estático** (*Alopecurus myosuroides*, *Avena fatua*, *Panicum dichotomiflorum*, *Cyperus esculentus*, *Phalaris brachystachys*, *Echinochloa erecta*, *Echinochloa hispidula*, e as entradas `spp.`). Não gerei os mapas delas.
8. **Não confrontei os mapas com as guias.** As guias de março/2026 citam casos de 2024 e 2025 (Lagosanto/FE, Santhià/VC, Lignana/VC, Vicenza, Udine) que os mapas de 2022 não podem conter. Não verifiquei comune a comune quais casos das guias já estão pintados e quais não estão.
9. **Não cruzei nada disso com registro de produto nem com a base europeia de substâncias.** Não usei `cellar.sh` nem `texto_fonte.py eu` nesta rodada — a pendência era sobre os mapas. As substâncias que aparecem aqui (glifosato, cicloxydim, quizalofop-P-ethyl, imazamox, nicosulfuron, cyhalofop-butyl, profoxydim, propanil, propyzamide) estão citadas como o GIRE as escreve, sem qualquer verificação de status regulatório atual.
10. **Nenhuma afirmação sobre ocorrência, incidência, venda ou demanda foi feita e nenhuma pode ser derivada daqui.** O que este relatório diz é: *o GIRE publica um mapa e o mapa marca estes comuni destas regiões, com esta legenda, por notificação voluntária, e sem período de referência declarado.*