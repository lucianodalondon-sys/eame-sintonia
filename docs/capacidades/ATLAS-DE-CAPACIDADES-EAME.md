# ATLAS DE CAPACIDADES — SINTONIA EAME

Fonte não é capacidade. Este atlas converte descoberta em **o que conseguimos saber**.

> "Existe um portal francês de alertas fitossanitários" é uma fonte.
> "Detectar alertas fitossanitários regionais em trigo na França" é uma capacidade.
> A segunda só entra aqui quando a primeira está provada com exemplo real.

**Estado:** MISSÃO 02 em curso — **2 capacidades COMPROVADAS**.
**Última atualização:** 2026-08-28

---

## FICHA DA CAPACIDADE

```
CAPABILITY:          # frase única, verificável. "Detectar X, em Y, para Z."
SOURCE:              # SOURCE_ID(s) do ATLAS DE FONTES que a sustentam
COUNTRY:
CROP:
GEOGRAPHY:           # granularidade REAL alcançada
TIME:                # janela temporal coberta
UPDATE_FREQUENCY:
CAN_AUTOMATE:        # SIM | NÃO | PARCIAL | NÃO SEI
CAN_HISTORY:         # dá para reconstruir série histórica?
CONFIDENCE:          # COMPROVADO | INFERÊNCIA | HIPÓTESE | NÃO SEI
ADAMA_DECISION:      # que decisão real da ADAMA isso informa
REAL_EXAMPLE:        # o caso concreto que prova a capacidade
```

Uma capacidade sem `REAL_EXAMPLE` **não pode** ter `CONFIDENCE: COMPROVADO`.

---

## MATRIZ DE USUÁRIOS ADAMA

Cada capacidade marca seus **possíveis** consumidores. O caminho é
**DADO → DECISÃO → POSSÍVEL USUÁRIO**, nessa ordem.

| Usuário | Sigla |
|---|---|
| EAME Management | EAME |
| Country Management | COUNTRY |
| Marketing | MKT |
| Commercial | COM |
| Market Development | MD |
| Regulatory | REG |
| Portfolio | PORT |
| Technical | TEC |
| R&D | RND |
| Communication | COMM |

**Não criar módulo por departamento ainda.** A matriz aqui é de identificação, não de arquitetura.

---

## REGISTRO DE CAPACIDADES

### CAP-001 · Vigiar toda decisão da UE sobre substância ativa, com data e identificador

```
CAPABILITY:          Detectar, de forma repetível e datada, todo ato da UE que aprove,
                     renove, altere ou retire uma substância ativa fitossanitária —
                     com identificador oficial (CELEX), data e texto integral.
SOURCE:              EU-T4-001 (CELLAR / Publications Office)
COUNTRY:             EUROPE (camada EU ACTIVE SUBSTANCE)
CROP:                não aplicável — o ato regula substância, não cultura
GEOGRAPHY:           União Europeia. NÃO desce a país, região ou cultura.
TIME:                todo o acervo CELEX; verificado de 2026-01 a 2026-07
UPDATE_FREQUENCY:    contínua (cada edição do Jornal Oficial)
CAN_AUTOMATE:        SIM — SPARQL público + content negotiation, sem chave, sem scraping.
                     Reproduzível por `scripts/cellar.sh`.
CAN_HISTORY:         SIM — série histórica completa por CELEX
CONFIDENCE:          COMPROVADO
ADAMA_DECISION:      REGULATORY: antecipar perda de substância e janela de expiração.
                     PORTFOLIO: ler o calendário de expirações do mercado europeu.
                     R&D / MARKET DEVELOPMENT: ver o que sai e abre espaço.
REAL_EXAMPLE:        CELEX 32026R1696 (14/07/2026) — renovação do ácido pelargônico,
                     CAS 112-05-0, CIPAC 888, aprovação 01/10/2026, expiração 30/09/2041.
                     Evidência: data/samples/EU-T4-001/
USERS:               REG (primário) · PORT · RND · MD · EAME
```

**Limite declarado:** esta capacidade prova o **ato europeu**. Ela **não** informa se existe
produto comercial autorizado em França, Espanha ou Itália, nem para que cultura ou alvo.
Isso é a camada NATIONAL PRODUCT AUTHORIZATION, ainda não investigada.

### CAP-002 · Ler o mesmo fato regulatório em EN, FR, ES e IT sem perder o original

```
CAPABILITY:          Obter o texto integral oficial de um mesmo ato regulatório da UE em
                     inglês, francês, espanhol e italiano, preservando o original de cada
                     língua e mantendo o mesmo identificador de documento.
SOURCE:              EU-T4-001
COUNTRY:             EUROPE (com leitura direta para FRANCE, SPAIN, ITALY)
GEOGRAPHY:           UE
TIME:                acervo CELEX
UPDATE_FREQUENCY:    contínua
CAN_AUTOMATE:        SIM — mesmo endpoint, header Accept-Language
CAN_HISTORY:         SIM
CONFIDENCE:          COMPROVADO
ADAMA_DECISION:      COMMUNICATION / COUNTRY MANAGEMENT: falar do mesmo fato regulatório
                     na língua de cada país usando a redação oficial daquele país, e não
                     uma tradução nossa.
REAL_EXAMPLE:        CELEX 32026R1696 obtido em eng (13.892 car.), fra (15.590),
                     spa (15.667) e ita (15.181). Títulos oficiais preservados em
                     data/samples/EU-T4-001/evidence-32026R1696.json
USERS:               COMM · COUNTRY · REG · MKT
```

**Por que isso importa:** resolve o requisito multilíngue da missão (§14) na sua forma mais
forte — não guardamos tradução, guardamos **a versão oficial em cada língua**, com o mesmo
CELEX ligando as quatro. `NORMALIZED_ENGLISH` aqui não é tradução automática: é a versão EN
oficial.

### Placar

| CONFIDENCE | Quantidade |
|---|---|
| COMPROVADO | 2 |
| INFERÊNCIA | 0 |
| HIPÓTESE | 0 |
| NÃO SEI | 0 |

### Cobertura por país

| | COMPROVADO | INFERÊNCIA | HIPÓTESE | NÃO SEI |
|---|---|---|---|---|
| EUROPE | 2 | 0 | 0 | 0 |
| FRANCE | 0 | 0 | 0 | 0 |
| SPAIN | 0 | 0 | 0 | 0 |
| ITALY | 0 | 0 | 0 | 0 |

---

## HIPÓTESES DERRUBADAS

Capacidade que caiu **permanece registrada aqui**, com o motivo e a data. Não se reescreve
a história para o relatório ficar mais bonito.

| ID | Capacidade que se supôs | Por que caiu | Data |
|---|---|---|---|
| *(nenhuma ainda)* | | | |
