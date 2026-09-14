# Como montar a lista de compradores de uma região — métodos, testados um a um

**Data:** 2026-09-14 · **Território de teste:** Vêneto · **Para quem:** o RTV que vai trabalhar a região.

**A pergunta que este documento responde:** o cruzamento do SINTONIA encontra o **problema**, liga ao
**portfólio** e chega a **possíveis compradores** — mas parou na província. O que falta para chegar
**ao comprador**, com localização, o que ele compra, que tamanho tem, e o resto que o RTV usa?

---

## 0 · Onde a cadeia quebra hoje — dito com precisão

```
PROBLEMA          → PORTFÓLIO           → DEMANDA              → COMPRADOR
(bollettino,        (registro IT-T4-001,   (ARPAV IT-T10-001,     (???)
 decreto, GIRE)      rótulo, cultura×alvo)   província × registro)
   COMPROVADO          COMPROVADO              COMPROVADO          ✗ NÃO SEI
```

As três primeiras pernas estão fechadas e medidas. A quarta não é fraca por falta de esforço: **a
declaração de venda é publicada agregada por província**, e o nome de quem vendeu é justamente o campo
que a fonte oculta. Quem quiser o comprador tem de **entrar por outra porta**. Este documento é o mapa
dessas portas — **12**, cada uma testada ou com o teste descrito.

**O que já existe sem nenhum dado novo:** `data/samples/IT-VENETO-CANALE/IT-VENETO-PACOTE-RTV-POR-PROVINCIA.json`
— por província: demanda declarada, mix por tipo, quem domina a prateleira, onde a ADAMA está, e quais
produtos ADAMA **vendidos no Vêneto não aparecem naquela província**. É pacote de rota, não de conta.

---

## 1 · A ficha do comprador — o contrato de campos

Contrato completo em [`FICHA-DO-COMPRADOR-CONTRATO.json`](FICHA-DO-COMPRADOR-CONTRATO.json):
**35 campos em 6 blocos**, cada um com fonte, método e estado.

| Bloco | O que responde | Campos-chave |
|---|---|---|
| **A · Identidade** | quem é | **P.IVA** (chave primária), razão social, tipo de canal, rede/grupo, ATECO |
| **B · Localização** | onde o RTV vai | sede + **coordenada**, lista de pontos de venda, raio de influência, província-chave |
| **C · Tamanho** | quanto pesa | faturamento e ano, **compra de agrofármaco**, funcionários, n.º de PdV, sócios/clientes, ha servidos, **tier** |
| **D · O que compra** | com quem ele já trabalha | categorias, **marcas conhecidas**, marca própria e quem a registra, **SKUs do catálogo ligados ao n.º de registro**, janela de compra |
| **E · Território que ele atende** | por que ele compraria | culturas, **problemas ativos e obrigações legais**, demanda declarada da província, **produto ADAMA que responde**, white space |
| **F · Ativação** | por onde entrar | técnicos próprios, campo experimental, eventos, publicidade ativa, ADAMA presente?, movimento recente |

**A chave primária é a P.IVA.** Nome muda, sede muda, placa muda; P.IVA não. É ela que liga Registro
Imprese, balanço, PEC — e o próprio registro fitossanitário, quando o comprador também é titular
(caso da Geofin).

**Regra de preenchimento:** todo campo carrega **fonte + data + estado**. Campo sem fonte fica
`NÃO SEI` — não se preenche por plausibilidade, e a idade do dado viaja colada ao número.

---

## 2 · Os 12 métodos, com o que cada um preenche

Legenda de custo: **€0** grátis · **€** baixo · **€€€** contrato. Legenda de teste: ✅ testado nesta
sessão · ⏳ descrito, não executado.

### M1 · Autorizações de venda das ULSS — *a porta da frente, e a única que dá o universo inteiro*
- **Preenche:** A (identidade) + B (endereço) de **todos os 531**.
- **Como:** a autorização de venda de fitossanitários é emitida pelo **Dipartimento di Prevenzione da
  ULSS** (D.Lgs 150/2012). São **9 ULSS** no Vêneto. Pedido de **accesso civico generalizzato**
  (FOIA italiano, D.Lgs 33/2013 art. 5): elenco dos titulares de autorização, com sede.
- **Custo:** €0. **Prazo:** 30 dias por ente, prorrogáveis.
- **Risco:** resposta em PDF sem estrutura; alguma ULSS pode negar por dado pessoal de empresa
  individual. **Legalidade:** pedido previsto em lei.
- **Estado:** ⏳ — a região **confirmadamente não publica** o elenco (verificado na página oficial).

### M2 · Registro Imprese por ATECO — *o atalho pago que resolve A + C num dia*
- **Preenche:** A, B (sede), C (faturamento, funcionários, forma jurídica).
- **Como:** extração por **ATECO 46.75.0** (produtos químicos) / **46.85.01** (fertilizantes e outros
  produtos químicos para agricultura) / **47.76.1**, filtrada por província.
- **Custo:** €€€ (InfoCamere/Cerved/Atoka). **Testado:** o open data público da InfoCamere é
  **contagem agregada, sem nomes** — ✅ verificado; nome exige extração paga.
- **Por que vale:** é a **única rota rápida e completa** com faturamento junto.

### M3 · Balanços e agregadores — *tamanho, quando o nome já se conhece*
- **Preenche:** C. **Custo:** €0–€.
- ✅ **Testado e funcionou:** CATB **€118 mi** (2024) e **€18,1 mi de antiparassitari**; Agrinordest
  **€398 mi** (2022); Geofin **€12,7 mi** (2024), 20–49 funcionários.
- **Limite medido:** fontes divergem (Agrinordest aparece como €398 mi e como ">€450 mi"). Divergência
  se registra, não se escolhe a mais bonita.

### M4 · Sites, store locators e páginas de parceiros — *o que o próprio comprador declara*
- **Preenche:** B (pontos de venda), D (marcas), F (técnicos, campo experimental).
- ✅ **Testado, com resultado desigual:**
  - **Geofin** publica os parceiros: **BASF, Bayer, FMC, Gowan, Ascenza/Sapec, Sharda, Sipcam,
    Syngenta, Agrobio, Cheminova** — e **não** a ADAMA;
  - **CAI** publica categorias e marca própria (**Maniflow, Sequra WG, Actileaf**) e **~40 técnicos**;
  - **Agrinordest** declara **~80 pontos de venda** e **mais de 100 campos experimentais/ano** em 7
    províncias, mas **não publica a lista de endereços** → `NÃO SEI`, fecha-se pedindo;
  - **Consorzio Agrario di Treviso e Belluno**: site devolve **HTTP 202 vazio** a acesso automatizado.

### M5 · OpenStreetMap (Overpass) + Nominatim — *localização de graça, cobertura parcial*
- **Preenche:** B (coordenada, endereço, telefone, horário).
- ✅ **Testado e entregue nesta sessão** (`data/samples/IT-VENETO-CANALE/IT-VENETO-OSM-PONTOS-CANAL.json`):
  **177 pontos** (`shop=agrarian` 47 · `shop=garden_centre` 130), **153 com nome**, 79 com rua,
  **57 com telefone**, 38 com site, todos com coordenada e província por geocodificação reversa.
- **E funcionou onde mais doía:** o OSM **localizou 3 filiais do Consorzio Agrario di Treviso e Belluno**
  (Treviso, Montebelluna, Feltre) e **2 do Consorzio Agrario del Nordest** (Montecchia di Crosara/VR,
  Conselve/PD) — exatamente o campo B que nenhum dos dois publica. Mais nomes independentes reais:
  *Formenti Agricoltura* (VR), *Agri Parolin* (Cittadella/PD), *Agraria di Cavallino* (VE).
- **Limite medido, não estimado:** 177 pontos contra **531 titulares** = no máximo **33%** de cobertura,
  e boa parte é garden centre de varejo. **Rovigo devolveu ZERO pontos** — ausência do mapa, não do
  mercado, justamente na província de maior quota ADAMA. Serve como **camada de localização**, nunca
  como lista-mãe. Licença **ODbL** (atribuição obrigatória a © OpenStreetMap contributors).

| Província | Pontos no OSM | Declarações de venda (ARPAV 2022) |
|---|---:|---:|
| Padova | 39 | 103 |
| Verona | 33 | 92 |
| Treviso | 29 | 126 |
| Vicenza | 28 | 99 |
| Venezia | 26 | 69 |
| Belluno | 22 | 16 |
| **Rovigo** | **0** | 45 |

### M6 · Catálogo e e-commerce do próprio revendedor — *a melhor prova do que ele compra*
- **Preenche:** D inteiro, no nível de SKU.
- **Como:** cada produto listado no site do revendedor traz o **nome comercial**; o nome bate no
  registro oficial e devolve **número de registro → titular → substância → tipo (fungicida/diserbante/
  inseticida)**. É o mesmo cruzamento que já roda: **100% do volume vêneto casou** com o registro.
- **Custo:** €0. **Estado:** ⏳ para as revendas (a de Treviso bloqueia robô); ✅ já funcionou no
  caminho inverso — foi assim que se descobriu que o "marchio proprio" do CAI é registro da **Manica,
  Sumitomo e Agrauxine**.
- **Cuidado:** catálogo diz o que ele **vende**, não quanto compra. É presença, não volume.

### M7 · Meta Ads Library — *quem anuncia, o quê e onde, com data*
- **Preenche:** D (marcas que ele empurra), F (ativação, sazonalidade).
- **Por que é barata:** o acervo **já tem 414 anúncios italianos** coletados; falta filtrar
  **anunciante = revenda/consórcio do Vêneto** em vez de fabricante.
- **Estado:** ⏳ — é o cruzamento **X-012** já registrado como "possível não testado".

### M8 · ARPAV por província — *a régua de demanda que já está fechada*
- **Preenche:** E (demanda, mix por tipo, quem domina, white space).
- ✅ **COMPROVADO e no repositório.** Serve para **dimensionar** o comprador que se achar: um ponto de
  venda em Rovigo joga num mercado em que a ADAMA tem **14,72%** do volume; em Verona, **5,48%**.

### M9 · Beneficiários PAC (AVEPA/AGEA) + SQNPI — *os clientes do seu cliente*
- **Preenche:** E (fazendas no raio: nome, comune, valor recebido) e C (tamanho indireto).
- ✅ **Existe e é público:** a AGEA publica beneficiários por obrigação do Reg. (UE) 2021/2116, e a
  **AVEPA** mantém "elenco dei beneficiari" (devolveu **503** no momento do teste — instabilidade, não
  ausência). O **SQNPI** publica as empresas certificadas em produção integrada.
- ⚠️ **Freio obrigatório:** boa parte dos beneficiários é **pessoa física**. Isso cai na regra de
  `docs/regras/LIMITES-DE-DADO-PESSOAL-EAME.md` e na pendência **P-008**, ainda aberta. Coletar para
  **agregar por comune** é uma coisa; expor lista nominal de agricultores em tela é outra, e **não está
  liberado**.

### M10 · Associações e redes — *pertencimento, e uma lista pronta quando existe*
- **Preenche:** A (rede), e às vezes a própria lista.
- **Compag** (federação nacional das revendas agrárias), **CAI**, **Confcooperative**, **Legacoop
  Veneto** (tem "elenco associate" público). ✅ verificado que Compag **não publica** o elenco de
  associados — fecha-se com um pedido à federação (Bolonha).

### M11 · Imprensa técnica e local — *movimento, e números que ninguém mais publica*
- **Preenche:** C (quando o balanço vira notícia), F (fusões, investimentos, gestão).
- ✅ **Testado:** foi assim que saíram os **€18,1 mi de antiparassitari** do Consorzio Agrario di
  Treviso e Belluno e a **incorporação da Cantina di Monteforte pelo Collis em nov/2025**.

### M12 · OP, consorzi di tutela e cooperativas — *o agregador de produtor por cultura*
- **Preenche:** C (sócios, hectares), E (cultura).
- ✅ Parcial: **16 OP + 1 AOP** hortifrutícolas, **3.356 sócios**, **14.765 ha**, VPC **€427 mi** — mas
  o elenco baixável do portal da região é um **.doc de 27/11/2014**. Lista atual: pedido à Direzione
  Agroalimentare.

---

## 3 · A montagem recomendada — espinha + enriquecimento

**Não existe uma fonte que entregue a lista pronta.** Existe **uma espinha** e **camadas que a
engordam**:

```
ESPINHA (escolher uma)
  M1 FOIA às 9 ULSS  ......... €0, 30-60 dias, universo COMPLETO (531)
  M2 Registro Imprese ATECO .. €€€, 1 dia, quase completo + faturamento
  M10 Associações ............ €0, rápido, cobertura parcial

        +  M3 balanço → TAMANHO
        +  M4 site/locator → PONTOS DE VENDA e MARCAS
        +  M5 OSM/Nominatim → COORDENADA
        +  M6 catálogo → O QUE COMPRA (SKU → registro → tipo → titular)
        +  M7 Meta Ads → O QUE ELE EMPURRA, com data
        +  M8 ARPAV → O MERCADO EM VOLTA DELE
        +  M9 PAC/SQNPI → OS CLIENTES DELE (com freio de GDPR)
        +  M11 imprensa → MOVIMENTO
```

**Ordem prática, se a decisão for hoje:**

1. **M2 agora** (é dinheiro pequeno perto de uma visita de RTV mal dirigida) — dá 80% da ficha em um
   dia, com P.IVA, endereço e faturamento;
2. **M4 + M6 em cima dos 30 maiores** — marcas e SKUs, que é o que diz se há espaço para a ADAMA;
3. **M8 já está pronto** — entra como contexto de cada ficha sem custo nenhum;
4. **M1 em paralelo**, porque é o único que fecha o universo e não depende de fornecedor;
5. **M9 por último e com parecer** — é o mais rico e o mais perigoso.

---

## 4 · O que muda no SINTONIA

O cruzamento passa a ter **quatro pernas declaradas**, e a quarta tem um **estado honesto**:
`PARCIAL — fecha até a província; o comprador exige M1 ou M2`. Ficha registrada na matriz de
cruzamentos como **X-013**.

**O que o RTV leva hoje, sem nenhum dado novo:** por província, o problema ativo com base legal, o
produto ADAMA que responde, a demanda declarada, quem domina a prateleira e o que do portfólio **não
aparece ali**. É pouco para uma carteira; é muito para uma rota.

**O que o RTV não leva hoje:** nome, endereço e telefone de quem compra. Isso custa **um pedido
(M1)** ou **uma extração (M2)** — e nenhuma das duas é pesquisa: são decisão.
