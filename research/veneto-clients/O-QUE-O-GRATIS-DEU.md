# Puxei tudo o que é grátis — e isto foi o que veio

**Data:** 2026-09-14 · **Recorte:** Vêneto · **Registro completo:** `data/samples/IT-VENETO-CANALE/SONDAGEM-DE-FONTES-GRATIS.json`

**13 rotas gratuitas sondadas.** Regra que governou a sondagem: *rota bloqueada não é fonte
inexistente; HTTP 200 não é conteúdo lido; "não encontrámos nesta leitura" não é "não existe".*

---

## O que veio inteiro

### 1 · Onze anos de venda declarada (2015–2025)
Não era um ano: a ARPAV publica **todos os anos desde 2015**, e os onze estão preservados no
repositório com sha256. Mais: o ficheiro de **2015** carrega duas coisas que os outros não têm —
a **AZIENDA ULSS** (geografia mais fina que a província, e é a ULSS quem licencia o vendedor) e
uma tabela de **356 substâncias ativas** com quantidade vendida.

**O achado da série:**

| | 2015 | 2016 | 2020 | 2022 | 2024 | **2025** |
|---|---:|---:|---:|---:|---:|---:|
| Mercado declarado (kg/l) | 16,6 mi | 16,9 mi | 16,5 mi | 13,3 mi | 17,3 mi | 16,3 mi |
| Volume grupo ADAMA | 1,58 mi | 1,71 mi | 1,56 mi | 1,22 mi | 1,40 mi | **1,12 mi** |
| Quota em volume | 9,49% | **10,12%** | 9,46% | 9,19% | 8,07% | **6,88%** |
| Produtos ADAMA vendidos | 204 | 182 | 149 | 129 | 124 | **107** |

**Em onze anos: o mercado caiu 2,3% e o volume dos produtos do grupo ADAMA caiu 29,1%.** A quota
em volume está no mínimo da série e o número de produtos com venda declarada caiu quase à metade.

⚠️ **A ressalva que viaja junto:** o titular de cada produto é o do registro de **hoje**, aplicado
a todos os anos. A série mede a evolução do **portfólio de hoje** no tempo — não diz que marca
estava na prateleira em 2015. Parte da queda pode ser portfólio que mudou de dono, e isso só se
separa com o histórico de titularidade.

### 2 · A camada de localização — 294 pontos
Do OpenStreetMap: **294 pontos** de canal agrícola no Vêneto, **69 de provável canal
profissional**, **103 com telefone**, 135 com rua. Entre eles, **25 consorzi agrari nomeados**,
com comune e telefone — **incluindo filiais que nem o Consorzio Agrario di Treviso e Belluno nem
o do Nordest publicam nos próprios sites**.

⚠️ **Não é censo:** 294 contra **531 titulares de autorização** é teto de cobertura, e **Rovigo
aparece com 2 pontos** — ausência do mapa, não do mercado, justamente na província onde a ADAMA
tem a maior quota.

---

## O que veio e ficou de fora — de propósito

**Operadores biológicos do Vêneto** (`dati.veneto.it`): CSV real, 1.611 registos, com
**DENOMINAZIONE, INDIRIZZO, COMUNE, PROVINCIA, CUAA e PARTITA IVA** — a chave primária da ficha
do comprador, de graça.

**Não entrou no repositório**, por duas razões: o dado é **de 31/12/2010** (quinze anos), e boa
parte dos registos é **pessoa física** — "AGOSTINI CELESTINO" é gente, não empresa. A regra está
em `docs/regras/LIMITES-DE-DADO-PESSOAL-EAME.md` e a pendência **P-008** continua aberta. A ficha
da fonte fica registada; o ficheiro, não.

O mesmo freio vale para **AGEA/PAC** e **SQNPI**: existem, são públicos, e são majoritariamente
nome de agricultor.

---

## O que não veio

| Rota | O que aconteceu |
|---|---|
| **AVEPA — beneficiários** | HTTP 503 e conexão resetada, em dois momentos. `ROUTE_BLOCKED`, não "não serve" |
| **Elenco das revendas do Vêneto** | **não existe público** — a autorização é de cada ULSS e a região não publica |
| **Compag — associados** | não publica |
| **CAI / Nordest — lista de lojas** | declara ~80 pontos e publica só a sede |
| **InfoCamere open data** | só contagem agregada; nome exige extração paga |
| **Outras regiões italianas** | só relatórios em PDF (Lombardia, 2011). O Vêneto pode ser a exceção — não testei região a região |

---

## O que o grátis não dá, e quanto custa

**Nenhuma das 13 rotas devolve o nome dos 531.** Isso continua custando:

- **€0** — accesso civico às 9 ULSS, ~30 dias, devolve o universo exato;
- **€5 + €0,12 por empresa** — Registro Imprese, lista "Esteso", CSV no mesmo dia, com
  faturamento e nº de funcionários dentro.

E há uma coisa que o grátis deu e que ninguém tinha pedido: **a França publica o equivalente
nacional** (BNV-D, por departamento, licença aberta, ficheiro atualizado em 13/09/2026). A mesma
capacidade, num país inteiro, sem custo.
