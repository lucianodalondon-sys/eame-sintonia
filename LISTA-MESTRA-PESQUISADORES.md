# LISTA-MESTRA-PESQUISADORES — o MUR como «Lattes italiano»

- **Ramo:** `lista-mestra-v1`, sobre `t6-para-sala-v1` (já rebaseado no vivo `278cd489`).
- **Sem rede, sem campo novo no contrato T6.** É uma **lista de identidade**, ao lado dele.
- **Entrada:** `auditoria-madrugada/MUR-07-AGRI-05-DOCENTES.json` (a coordenação baixou-o do CERCA
  UNIVERSITÀ do MUR; sha256 `5260432cd6e15754…`, 278 docentes, 07/AGRI-05 = patologia vegetal + entomologia).
- **Obras:** as 589 da consulta T6 (`foto-final`, sha256 em `FOTO-FINAL.sha256`).

## 1 · O MUR como LISTA MESTRA, cruzado com as 589 obras / 1.466 pessoas

`coleta/lista_mestra_mur.py --cruzar` → `data/derivados/LISTA-MESTRA/CRUZAMENTO-MUR-AGRI05.json`.

- **O MUR diz QUEM é, ONDE está e em que SETOR** (fonte oficial, não se corrige).
- **O OpenAlex diz o que PUBLICOU.** Erra a instituição (Bitron, Hospital) e parte pessoas em vários IDs.
- **A ligação é sempre NOME + UNIVERSIDADE:**
  - o apelido do MUR inteiro, com o nome ou a inicial;
  - a universidade do MUR tem de aparecer numa instituição italiana declarada **numa obra** da pessoa.

| Estado | Docentes | O que quer dizer |
|---|---|---|
| **MUR_E_OBRAS** | **127** | Ligado a um ID do OpenAlex com nome e universidade |
| VARIOS_IDS | 2 | O índice partiu a pessoa em 2 IDs (Mori/Verona; «A. Vitale» + «Alessandro Vitale»/Catânia): ficam os dois, sem fundir |
| SO_NOME | 4 | O nome bate, a universidade não: **não se liga** (ver abaixo) |
| NAO_ENCONTRADO | 145 | Ninguém com esse nome nas 589 obras |

**Os 129 ligados:**
- todos com um ORCID no índice; **101** com a pessoa provada (ORCID autodeclarado ou depositado pelo editor);
- por setor: 84 de patologia (AGRI-05/B) e 45 de entomologia (AGRI-05/A).

**Pares do casco nos trabalhos dos 129:**

| Par | Pessoas |
|---|---|
| vite × peronospora | 49 |
| pomodoro × botrite | 44 |
| vite × scafoideo | 34 |
| vite × botrite | 31 |
| vite × oidio | 24 |
| vite × tignoletta | 15 |
| pomodoro × peronospora | 12 |
| mais × piralide | 9 |
| mais × diabrotica | 5 |
| melo × carpocapsa | 2 |
| pomodoro × oidio | 1 |
| melo × oidio | 1 |

**Os 4 SO_NOME, lidos à mão:**
- Cornara (Bari) e Lucchetta (Padova): as obras deles não declaram instituição nenhuma.
- Mincuzzi (MUR: Bolonha): nas obras aparece Bari.
- Testa (MUR: Vanvitelli): nas obras aparecem CNR e Nápoles.

As quatro ficam fora até alguém confirmar. Pode ser mudança de universidade, e pode ser homónimo.

**Contra a sua conta de 114:**
- aqui são 129 porque a inicial do primeiro nome vale;
- 8 ligações foram por inicial (P. Casati, M. Cristina Digilio, P. Ermacora…), todas lidas e plausíveis;
- o apóstrofo do MUR («ZAPPALA'», «TURRA'») é tratado como acento.

**Os nomes do dono:**
- Domenico Bosco = `BOSCO Domenico`, Ordinario, Torino, AGRI-05/A. Está ligado, com 14 obras de flavescência.
  O «Daniele» do dono não existe no MUR.
- Zappalà e Antonio Biondi (Catânia) estão no MUR, mas **NAO_ENCONTRADO** nas 589: não publicam nos 12 pares.
  Vão à busca por pessoa.
- Grassi e Tonina **não estão no MUR**: são da FEM, e a FEM não é universidade (ver §3).

## 2 · A consulta por PESSOA para os 149 (145 + 4), a correr na rede

`py coleta/lista_mestra_mur.py --rede --rodada=N --mur=<MUR> --rodadas=<foto-final> --saida=<pasta>`

**1.ª e 2.ª rodadas, ORCID:**
- a busca pública (`/v3.0/expanded-search/`) leva **20 pessoas por pedido** (apelido E nome, em OU);
- são **8 pedidos para as 149**: 5 na 1.ª rodada, 3 na 2.ª;
- uma pessoa só ganha ORCID se apelido, nome **e universidade** baterem;
- o acento volta ao nome («Zappalà»).

**2.ª/3.ª rodada, OpenAlex:**
- `/authors?filter=orcid:a|b|…` leva **50 ORCID por pedido**;
- traz a instituição atual, o número de obras e os **temas** de cada pessoa;
- são **≤ 3 pedidos**.

**A seguir, as obras:**
- a Consulta 2 do T6 (`--rede2`), por pessoa;
- pela **prioridade medida nos temas**: quantos temas do autor falam do casco (vite, melo, mais, pomodoro, peronóspora, oídio, botrite, fitoplasma, cicadelídeo, traça, praga, fungicida…).

**Ordem das rodadas:**
- **entomologia primeiro**: 5 dos 8 problemas do casco são insetos, e só 45 entomólogos estão ligados, contra 84 em falta;
- dentro do setor, a ordem do MUR (alfabética). **Não é ranking de pessoa.**

**Teto:** 5 por domínio por rodada, contado antes de pedir (`assert`). Um corpo de erro para o domínio e não vira zero.

⚠️ **Nenhuma resposta real da busca ORCID existe na casa.** Os campos (`expanded-result`, `orcid-id`,
`family-names`, `institution-name`) são os da API pública, e a 1.ª rodada prova-os. O teste usa uma resposta **sintética**.

**Testes** (`tests/test_lista_mestra_mur.py`, 5, sem rede):
- homónimo noutra universidade → SO_NOME, não ligado;
- inicial + apelido composto (A. M. De Luca) → ligado;
- 2 IDs na mesma universidade → VARIOS_IDS;
- o apóstrofo;
- a busca ORCID recusa o mesmo nome noutra universidade;
- lotes de 20 com teto 5 (130 pessoas → 5 + 2 pedidos).

## 3 · Que outros setores baixar, e quem fica FORA do MUR

**Outros setores do CERCA UNIVERSITÀ**, pelo que o casco pergunta:

| Prioridade | Setor (SSD 2015; o código 2024 confirma-se no próprio MUR) | Porquê |
|---|---|---|
| 1 | **AGR/03** Arboricoltura generale e coltivazioni arboree | vite e melo: fenologia, janelas |
| 1 | **AGR/02** Agronomia e coltivazioni erbacee | mais e pomodoro de campo; plantas daninhas |
| 2 | **AGR/04** Orticoltura e floricoltura | pomodoro em estufa |
| 2 | **AGR/16** Microbiologia agraria | agentes de biocontrolo (Trichoderma, Bacillus, Aureobasidium) |
| 3 | AGR/07 Genetica agraria | resistência da planta (Rpv/Ren, 67 obras nas 589) |
| 3 | AGR/13 Chimica agraria | resíduos, solo, cobre |

⚠️ Os nomes «AGRI-01 agronomia, AGRI-02 colture, AGRI-03 arboree» da coordenação **não foram verificados aqui**
(sem rede). No ficheiro do MUR, cada linha traz o `SSD2015` ao lado do `SSD 2024`: o mapa entre os dois lê-se lá.

**Fora do MUR** (o MUR só tem universidades), com a prova que existe nesta casa:

| Casa | O que é | Onde está a lista | Prova no repositório |
|---|---|---|---|
| **CNR** (IPSP, ISPA, IBBR, IBE, ISAFOM, IRET) | Institutos de pesquisa; o IPSP é o 2.º grupo em vite × scafoideo | O **IRIS do CNR** (`iris.cnr.it`), catálogo de produção por autor; e as páginas de pessoal de cada instituto | `iris.cnr.it` em 4 ficheiros; os sites dos institutos visitados na P1 (`pesquisadores-v2`) |
| **CREA** (12 centros) | Rede de pesquisa agrária do ministério | Páginas de pessoa `crea.gov.it/web/<centro>/-/<nome>` | **58 perfis com HTTP 200** (P1d, `PESQUISADORES-P1D-CREA-PERFIS.json`, 24/09): difesa-e-certificazione 4, viticoltura-e-enologia 7, olivicoltura-frutticoltura 7, orticoltura 4, cerealicoltura 3… |
| **FEM** (Fondazione Edmund Mach) | Grassi, Tonina, Anfora, Ioriatti, Perazzolli | O pessoal em `fmach.it` | `fmach.it` visitado na P1 |
| **IZS** | Institutos zooprofiláticos | — | **Fora do foco** por decisão do dono (23/09: fora veterinária, IZS, saúde animal) |

Nenhuma destas listas foi baixada nesta missão (sem rede).

## 4 · O IRIS de cada universidade (o «currículo de publicações»)

- **4 endereços estão PROVADOS no repositório:** Milano `air.unimi.it`, Torino `iris.unito.it`, Firenze `flore.unifi.it`, Bologna `cris.unibo.it`.
- **Os outros 29 são a morada habitual do IRIS**, escritos de memória e marcados **A_CONFIRMAR**. São um dado da lista (campo `IRIS` / `IRIS_ESTADO` de cada docente).

| Universidade | IRIS | Estado |
|---|---|---|
| Milano | https://air.unimi.it | provado |
| Torino | https://iris.unito.it | provado |
| Firenze | https://flore.unifi.it | provado |
| Bologna | https://cris.unibo.it | provado |
| Padova | https://www.research.unipd.it | a confirmar |
| Napoli Federico II | https://www.iris.unina.it | a confirmar |
| Catania | https://www.iris.unict.it | a confirmar |
| Bari | https://ricerca.uniba.it | a confirmar |
| Palermo | https://iris.unipa.it | a confirmar |
| Sassari | https://iris.uniss.it | a confirmar |
| Tuscia | https://dspace.unitus.it | a confirmar |
| Pisa | https://arpi.unipi.it | a confirmar |
| Udine | https://air.uniud.it | a confirmar |
| Cattolica | https://publicatt.unicatt.it | a confirmar |
| Perugia | https://research.unipg.it | a confirmar |
| Basilicata | https://iris.unibas.it | a confirmar |
| Molise | https://iris.unimol.it | a confirmar |
| Politecnica Marche | https://iris.univpm.it | a confirmar |
| Mediterranea Reggio Calabria | https://iris.unirc.it | a confirmar |
| Trento | https://iris.unitn.it | a confirmar |
| Foggia | https://iris.unifg.it | a confirmar |
| Bolzano | https://bia.unibz.it | a confirmar |
| Roma Sapienza | https://iris.uniroma1.it | a confirmar |
| Modena e Reggio Emilia | https://iris.unimore.it | a confirmar |
| Verona | https://iris.univr.it | a confirmar |
| Ferrara | https://sfera.unife.it | a confirmar |
| Brescia | https://iris.unibs.it | a confirmar |
| Salerno | https://www.iris.unisa.it | a confirmar |
| Siena | https://usiena-air.unisi.it | a confirmar |
| Teramo | https://iris.unite.it | a confirmar |
| Salento | https://iris.unisalento.it | a confirmar |
| Sant'Anna | https://www.iris.sssup.it | a confirmar |
| Vanvitelli | https://iris.unicampania.it | a confirmar |

## Limites

1. **A universidade do MUR tem de aparecer numa obra.** Quem mudou de universidade, ou publica sem declarar instituição, fica SO_NOME até confirmação (4 casos).
2. **A busca ORCID em lote não está provada com uma resposta real.**
3. **Os códigos de setor 2024 e 29 dos 33 IRIS estão por confirmar** (sem rede).
4. **Mapa não corrido** (PRONTO-SEM-MAPA).
