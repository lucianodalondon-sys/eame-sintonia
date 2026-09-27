# FONTES-NOVAS-AGRO — 43 fontes novas, com prova, numa cópia da fila

Missão FONTES-NOVAS-AGRO (coordenação 22:30; D92 «força total» + D87 «as fontes descobrem, com a Intelligence»). Ramo
`fontes-novas-agro-v1`, sobre o vivo `554c1ec1`. **Só registos, sem código do sistema.** A fila do vivo **não foi
tocada** (sha256 igual antes e depois: `772b55647a02dc0d…`); tudo foi registado numa **cópia**
(`sintonia-sala-italia/fontes-novas-agro/copia-fila/candidatas/`, sha256 depois `058566dc26878265…`). Quem aplica
no vivo é o coordenador (secção 5).

## 1. De onde veio a lista
- A **LACUNAS-PARA-FONTES** da GAPS ainda **não saiu** — não a usei. Usei o que já existia:
  - **RELATORIO-RODADA-2** da Intelligence (`EXPD78-R2`): «mais T3 boletins regionais», «uma 2.ª fonte T10
    independente de myfruit.it (hoje 66,7% dos sinais de mercado vêm de uma fonte)», «T7 → T8: faltam técnicos com
    nome», «abrir T1/T2 regional», «menos T5 institucional».
  - **GAPS-CANDIDATAS** (24/25/09): o que a casa já tem (76 fito/agrometeo com contrato, 30 consorzi di difesa no lote
    2 da micro-prova) — **não os repeti**; e os gaps reais: preços em 19 de 21 regiões, vídeo com pessoa, DSS.
- **69 pistas** escritas à mão **antes** de abrir (`pistas.json`, `pistas2.json`): consorzi fitosanitari provinciali,
  associações de produtores, consorzi di tutela, mercados grossistas, câmaras de comércio (borsa merci), DSS/modelos.

## 2. Como se provou (rede só pelo portão da casa)
- Portão de egresso **IT PASS** antes e depois de cada leva.
- Cada pista: **robots.txt lido** + **1 página** pelo `coleta/scrap_http.py` (agente declarado, pausa de cortesia) —
  **≤ 2 pedidos por domínio**, bem abaixo do teto de 5/24 h. **Sem login, sem contorno** (a D88/`COL-LAW-220` ainda é
  proposta; não usei navegador nem fingerprint).
- Antes de abrir, cada domínio foi cruzado com os livros do vivo (fila de candidatas, contratos do Curator, onboarded,
  descoberta visitada, livro do ciclo de vida, fila única, Atlas): **conhecido → não se abre**.
- Da página oficial guardou-se: HTTP, **sha256** (bytes fora do Git, `SHA256SUMS.txt` com 37 ficheiros), título,
  **P.IVA/CF**, **sede**, as **âncoras** que o próprio site declara (boletim, preços, modelos) e os **links para as
  redes sociais** que o site aponta.

| | pistas |
|---|---|
| já conhecidas pela casa (não abertas) | **15** — agrion, ALSIA, ERSAF, meteotrentino, prosecco.it, CREA, Horta, CSO, Freshplaza, agricultura.it, Olivonews, Teatro Naturale, Fitogest, Il Nuovo Agricoltore, Italia Olivicola |
| não abriram | **17** — 13 queda de ligação ao ler o robots (`PortaoIndisponivel`: **não é recusa**, é NAO SEI), 3 robots ilegível (meteo.fvg.it, ismeamercati.it, cno.it), 1 endereço 404 (UCSC DI.PRO.VE.S.) |
| abriram | **37** |
| **selecionadas** | **43 candidatas**: 17 sites + 26 canais sociais |

## 3. As 43 (todas NOVAS na cópia — 0 já existiam)

### 3a. Sites — o endereço registado é a página que o próprio site aponta como boletim/preços
| # | fonte | T* | território (âmbito do órgão, não lugar do facto) | o que o site declara |
|---|---|---|---|---|
| 1 | Consorzio Fitosanitario Provinciale di **Modena** | T3 | provincia di Modena | bollettini produzione integrata · **modelli previsionali** · **monitoraggio captaspore** · notiziario fitopatologico |
| 2 | Consorzio Fitosanitario Provinciale di **Reggio Emilia** | T3 | provincia di Reggio Emilia | bollettino di produzione integrata e bio (2026) |
| 3 | Consorzio Fitosanitario di **Parma** | T3 | provincia di Parma | bollettini territoriali · modelli previsionali |
| 4 | Consorzio Fitosanitario di **Piacenza** | T3 | provincia di Piacenza | bollettini territoriali · modelli previsionali |
| 5 | **Fondazione Fojanini** (Sondrio) | T3 | Valtellina | difesa fitosanitaria vite/melo |
| 6 | **AIPO** — produttori olivicoli | T3/T10 | Veneto/Emilia-Romagna (âmbito exato NAO SEI) | notiziario olivicolo · frutticolo · melo/pero · **bollettino prezzi olio EVO** |
| 7 | Consorzio **Soave** | T3/T7 | zona DOC Soave (VR) | «Bollettini» |
| 8 | **Vignaioli Piemontesi** | T3/T7 | Piemonte | difesa fitosanitaria del vigneto |
| 9 | **Agricolus** (Perugia) | cadeia B | nacional | modelli previsionali · DSS |
| 10 | **CLAL** | T10 | nacional | riepilogo prezzi · quotazioni |
| 11 | **SogeMi** Milano | T10 | Milano | bollettini e report prezzi |
| 12 | **Italmercati** | T10 | rede nacional | «La Borsa della Spesa» **semanal** (25/09, 18/09, 11/09, 04/09) |
| 13 | **CCIAA Foggia** | T10 | provincia di Foggia | borsa merci prodotti cerealicoli |
| 14 | **CCIAA Verona** | T10 | provincia di Verona | borsa merci · rilevazione prezzi |
| 15 | **CAAT** Torino | T10 | Torino | il mercuriale dei prezzi |
| 16 | **CAAN** Napoli | T10 | Volla (NA) | listini ortofrutta |
| 17 | **CCIAA Monte Rosa Laghi Alto Piemonte** | T10 | Novara/Vercelli/Biella/VCO | listini prezzi (riso, cereali) |

→ **5 serviços de defesa provinciais/locais com boletim** (a família que mais rende, RODADA-2) e **8 fontes de
preços** em 6 regiões — hoje o mercado depende de **uma** fonte.

### 3b. Canais sociais — identidade provada porque o **site oficial aponta para eles** (regra D21)
- **YouTube (11):** Agricolus, Agrintesa, Apofruit, Melinda, Consorzio Franciacorta, Consorzio Soave, Consorzio Prosecco
  DOC, Italmercati, CLAL, CAAT, CCIAA Foggia.
- **LinkedIn (10):** Agricolus, Agrintesa, Apofruit, VOG, Italia Ortofrutta, Consorzio Franciacorta, Consorzio Prosecco
  DOC, Italmercati, CLAL, SogeMi.
- **Instagram (5):** Agrintesa, Melinda, Italia Ortofrutta, Consorzio Soave, Consorzio Prosecco DOC.

Cada linha leva na `NOTA`: o site que aponta, o sha256 da página, a P.IVA/sede quando a página a mostra, e «D87: descoberto
pelas fontes, o Scrap só captura». São **organizações**, não pessoas: técnico com nome continua um gap (secção 6).

## 4. O que ficou de fora, e porquê
- **Abriram mas não entram:** Mercafir, MOF Fondi, Veronamercato, CCIAA Bari, APOT, Melinda/VOG/Apofruit/Agrintesa/Italia
  Ortofrutta/Franciacorta/Prosecco DOC como **site** (a página não aponta boletim nem preço — entram só os canais) ·
  **CAAB** Bologna (os «listini prezzi» pedem **login**) · **fruitecom** (é uma agência de comunicação, não uma fonte) ·
  xFarm, METOS/Pessl, Aedit (vendedores; nada verificável na página) · agroambiente.info e meteo.fmach.it (a página vem
  vazia sem JavaScript — **NAO SEI**, podem ser boas; com a D88 aprovada, reabrir).
- **Não abriram:** as 17 da tabela acima. As 13 de «queda de ligação» não são fontes mortas (a lição
  `falha-de-ligacao-nao-e-fonte-morta`); ISMEA Mercati é a mais importante delas (robots ilegível) — **reabrir**.

## 5. Para o coordenador aplicar no vivo
```bash
cd <ramo fontes-novas-agro-v1>/data/derivados/FONTES-NOVAS-AGRO
PYTHONUTF8=1 py aplicar.py.txt C:/Users/London1/orca/workspaces/eame-sintonia/source-curator-service-v1/candidatas
```
Usa a porta canónica (`candidatas/fonte_nova.registar`); a chave é o URL normalizado, por isso correr duas vezes não
duplica. ⚠️ Os `CANDIDATA_ID` da cópia (CAND-1205..1247) **não valem para o vivo**: o número sai do tamanho da fila no
momento (memória `cand-ids-colidem-entre-lanes`) — no vivo nascem outros. O que identifica cada uma é o URL.
LinkedIn e Instagram entram com o estado que a porta lhes der (D15/D22–D24).

## 6. Limites declarados
- **Candidata não é fonte.** Nenhuma destas foi a um canário nem tem contrato; a forma (HTML/PDF, D42) de cada boletim
  não foi aberta — só a página que o aponta.
- **Italmercati**: o endereço registado é o artigo de 25/09; a série é semanal, mas o índice não foi aberto (NAO SEI
  qual é) — o canário deve procurar a lista.
- **Técnicos com nome** (T8) e **vídeo com pessoa identificada**: 0 nesta missão. Os canais são de organizações.
- **ISMEA, CNO, OSMER FVG, Beratungsring, Assomela**: fontes provavelmente fortes que ficaram por abrir.
- A **LACUNAS-PARA-FONTES** pode mudar a prioridade quando sair.

## EM PALAVRAS SIMPLES
- **O que fiz:** procurei fontes novas de informação agrícola italiana que ainda não temos, abri a página oficial de
  cada uma (no máximo 2 visitas por site, pela VPN italiana, respeitando as regras do site) e guardei a prova de quem é
  e de onde é.
- **Achei 43:** 5 serviços de defesa das plantas de províncias com boletim (Modena, Reggio Emilia, Parma, Piacenza,
  Sondrio) e mais 3 de viticultura e oliva; 8 fontes de **preços** (mercados atacadistas e bolsas de Milão, Turim,
  Nápoles, Foggia, Verona, Novara e duas nacionais) — hoje dependemos de uma só; 1 empresa de modelos de previsão de
  doenças; e 26 canais de YouTube, LinkedIn e Instagram de cooperativas e consórcios, cada um provado porque o site
  oficial aponta para ele.
- **O que não mexi:** a fila de verdade do robô. Registei tudo numa **cópia**; o coordenador aplica com um comando.
- **O que pode dar errado:** isto são **pistas provadas**, não fontes prontas — ainda precisam do teste de coleta. E 17
  sites não abriram (a maioria por queda de ligação, o que não quer dizer que não existam).
