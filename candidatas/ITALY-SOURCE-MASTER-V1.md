# CATÁLOGO-MESTRE DE FONTES — ITÁLIA

**Data:** 2026-09-07 · **Missão:** ITÁLIA — ORGANIZAR, TESTAR E PROVAR FONTES
**Estado:** Fases A e B **concluídas**. Fases C a H **bloqueadas** — motivo medido abaixo.
**JSON canônico:** `../../candidatas/ITALY-SOURCE-MASTER-V1.json`

> Este documento é a **planilha de trabalho da Fase C**, não um veredito.
> **Nenhuma fonte aqui recebeu GREEN, YELLOW ou RED.** Todas estão `NOT_TESTED`.

---

## 0 · POR QUE NÃO HÁ VEREDITO

A missão determina que o acesso seja feito por
**SINTONIA SCRAP + BROWSER NORMAL + VPN LOCALIZADA NA ITÁLIA**.

Medido em 2026-09-07:

| ambiente | resultado |
|---|---|
| navegador interno deste app | sai de **Edimburgo, Escócia (GB)** — IP `188.240.57.237`, `baremetal.zare.com`, AS25369 Hydra Communications. É **datacenter**, não é Itália. |
| Chrome real do usuário | **não conectado** — extensão instalada, mas sem sessão iniciada; `list_connected_browsers` devolveu lista vazia em três tentativas |
| interpretador Python | **ausente no disco** — `py` resolve para `C:\actions-runner-2\...` inexistente e `AppData\Local\Programs\Python\Python312` não contém `python.exe` |
| Node | v24.18.0, disponível |

A **REGRA 0** da própria missão determina:

```
BLOCKED_EM_DATACENTER ≠ BLOCKED_EM_BROWSER_ITALIANO
```

Medir daqui produziria **RED falso**: mediria o bloqueio de Edimburgo, não o da Itália.
Por isso nenhuma fonte foi probada e nenhum veredito foi emitido.

### A assimetria que vale para a Fase C

| resultado de um IP não-italiano | vale? |
|---|---|
| **abriu e entregou documento** | **SIM** — se abre de fora, abre da Itália (exceto geo-bloqueio explícito) |
| **403 / WAF / bloqueio** | **NÃO** — sinal nulo; obrigatório remedir de IP italiano antes de qualquer RED |

Consequência: quando o Chrome italiano estiver ligado, a Fase C **não precisa começar do zero** —
este catálogo já diz o que abrir, em que ordem, e o que cada abertura precisa provar.

### Sem Python, a Fase H não roda aqui

`tests/` é Python (unittest/pytest). Nenhum `python.exe` existe nesta máquina.
A Fase H fica pendente **de ambiente**, não de decisão.

---

## 1 · O QUE JÁ EXISTIA (FASE A)

Fonte: `ATLAS-DE-FONTES-EAME.md`, estado de 2026-08-30 — **37 SOURCE_IDs** no total,
dos quais **6 são italianos**.

| SOURCE_ID | fonte | T | veredito no Atlas | observação |
|---|---|---|---|---|
| `IT-T1-001` | ISTAT — coltivazioni (SDMX) | T1 | **NÃO SEI** | `esploradati.istat.it` sem resposta; `sdmx.istat.it` 302 vazio |
| `IT-T3-001` | Bollettini produzione integrata — Emilia-Romagna | T3 | **YELLOW** | **1 das 20 regiões**; o Atlas já declara que tratar isso como "a Itália" é erro grosseiro |
| `IT-T4-001` | Ministero della Salute — prodotti fitosanitari | T4 | **GREEN** | 17.695 produtos · 3.712 em vigor · ADAMA ITALIA com 155 autorizações futuras. **Não traz cultura nem alvo.** |
| `IT-T9-001` | comunicação de concorrentes (ficha FR/ES/IT) | T9 | **NÃO SEI** | ficha **compartilhada entre 3 países** — não mede empresa a empresa |
| `IT-T11-001` | EIMA International | T11 | **YELLOW** | 47ª edição, 10–14/11/2026, Bologna |
| `IT-T13-001` | Registro Imprese / cooperative | T13 | **NÃO SEI** | ver §2 |

**Placar italiano antes desta missão: 1 GREEN · 2 YELLOW · 0 RED · 3 NÃO SEI.**

### Armadilha de contagem encontrada

Um `grep` por `IT-T\d+-\d+` no Atlas devolve **7** IDs. São **6**.
O sétimo, `IT-T12-001`, aparece na linha 131 apenas como **exemplo da convenção de SOURCE_ID** —
não é fonte. Registrado para que uma futura fonte italiana de T12 não pule esse número achando
que está ocupado. *(Por isso o PSP/PAC abaixo recebe `IT-T12-002`.)*

---

## 2 · DÍVIDA DE TAXONOMIA — `TAXONOMY_DEBT`

### O achado

A missão manda **não criar T13** e preservar T1–T12. **T13 já existe no acervo.**

- **Onde:** `docs/fontes/ATLAS-DE-FONTES-EAME.md`, seção *"T13 · DISTRIBUTION — FRANCE"* (linhas ~1269–1316)
- **Quando:** aberto na MISSÃO 03
- **Por quê:** a apresentação promete DISTRIBUTION como camada (DECK-008, DECK-021) e T1–T12 não a cobriam
- **Ocupantes:** `FR-T13-001` (**GREEN**, base SIRENE, 4.646 empresas no NAF 46.21Z) · `ES-T13-001` (NÃO SEI) · `IT-T13-001` (NÃO SEI)

### O que T13 é, de verdade

T13 não é um fenômeno novo. São **duas perguntas diferentes fundidas num território só**:

| pergunta | vai para | por quê | papel |
|---|---|---|---|
| **QUEM** distribui e **ONDE** está? | **T7** TECHNICAL NETWORK | a definição de T7 no próprio Atlas já inclui *"cooperativas, associações"*; `FR-T13-001` entrega identidade de entidade, que é exatamente o que T7 coleciona | `IDENTITY_SOURCE` |
| **QUANTO** flui, com que catálogo, a que preço? | **T10** MARKET / TRADE / INDUSTRY | volume, catálogo e acordo comercial são fato de comércio, não de rede | `MARKET_SOURCE` |

**Efeito prático:** hoje **100% do conteúdo real de T13** (`FR-T13-001`) migra para **T7**.
A perna T10 **nasce vazia** — e isso é informação, não perda: o próprio Atlas já registra que
`FR-T13-001` *"dá a rede, não o fluxo"*, e que afirmar volume a partir dela seria inventar.

### Por que NÃO migramos agora

A migração é **bloqueante**, e o custo foi medido:

1. **A regra do próprio acervo proíbe.** O Atlas declara: *"O ID, uma vez atribuído, não é reciclado."*
   Renomear `FR-T13-001` → `FR-T7-00X` quebra essa regra.
2. **Três testes travam a contagem:**
   - `tests/test_handoff.py:111` — `assert SOURCE_ID_COUNT == 37`, **hardcoded**
   - `tests/test_canonico.py:58` e `:353` — cabeçalho e total de SOURCE_IDs do Atlas
   - `tests/test_metricas.py:56` — o marcador `SOURCE_ID_COUNT` é replicado em `piloto/ENTRADA-PARA-CLAUDE-DESIGN.md` e outros arquivos
3. A missão determina: *"Só alterar artefatos canônicos se isso puder ser feito sem quebrar contratos/testes existentes."*

**Recomendação:** manter `FR-T13-001` com o ID que tem, registrar a dívida (este documento),
e fazer a migração numa missão própria que atualize Atlas + marcadores + 3 arquivos de teste
**na mesma mudança**. Decisão do Luciano.

**Esta missão não renomeou nada. Nenhum artefato canônico foi alterado.**

---

## 3 · O MODELO DE DOIS NÍVEIS (FASE B)

A ficha atual do Atlas tem `SOURCE_OWNER` como **texto livre**. Não dá para responder
*"quantos canais a Terre dell'Etruria tem?"* nem *"a FEM aparece em quantos territórios?"*.

Este catálogo separa:

```
OWNER          quem publica          → OWNER_KIND
SOURCE         o canal               → ACCESS_METHOD
TERRITORY      o que a rota mede     → T1..T12
SOURCE_ROLE    para que serve        → DISCOVERY / IDENTITY / FIELD_SIGNAL / ...
```

**Cooperativa é `OWNER_KIND`. Nunca território.**

**44 owners · 54 sources** — 4 já existiam, 1 a redefinir, 49 candidatas novas.
Distribuição por território: T1 1 · T2 5 · T3 12 · T4 1 · T5 5 · T7 12 · T9 8 · T10 5 · T11 4 · T12 1.
*(Conferido por script sobre o JSON: nenhum SOURCE_ID duplicado, nenhum OWNER_ID duplicado,
nenhuma fonte órfã de owner, nenhum veredito emitido.)*

Uma organização pode ter vários canais, sem ser duplicada:

| owner | canais | territórios |
|---|---|---|
| **Terre dell'Etruria** (COOPERATIVE) | monitoraggio mosca · bollettini tecnici · servizio agronomico | T3 · T3 · **T7** |
| **Fondazione Edmund Mach** (FOUNDATION) | boletim · OpenPub · extensão · eventos | T3 · T5 · T7 · T11 (+ T6 via `EU-T5-001`) |
| **MASAF** (AGÊNCIA NACIONAL) | lista OP/AOP · PSP-PAC | T7 · T12 |
| **ICQRF** (dentro do MASAF) | Cantina Italia · Frantoio Italia | T10 · T10 |
| **ISTAT** | coltivazioni · commercio estero | T1 · T10 |
| **ALSIA** | agrometeorologia · fitossanidade | T2 · T3 |
| **Campania SFR** | bollettini · SIMFITO | T3 · T3 |

E owners que **parecem um só e não são** — não fundir:

| par | por que separado |
|---|---|
| ARPAE **×** Emilia-Romagna Servizio Fitosanitario | mesma região, órgãos diferentes: ambiente (T2) × sanidade vegetal (T3) |
| AGRIOS **×** VOG | AGRIOS emite a diretriz técnica; VOG é a rede de produtores |
| SIAS **×** Sicilia Servizio Fitosanitario | mesma região, agrometeorologia × fitossanidade |

---

## 4 · CATÁLOGO-MESTRE

`STATUS`: `PRE` = já existia · `NEW` = candidata nova · `REDEF` = ID existente a redefinir
`ROLE`: `FS` FIELD_SIGNAL · `TG` TECHNICAL_GUIDANCE · `ID` IDENTITY · `DISC` DISCOVERY · `MKT` MARKET · `SCI` SCIENCE · `VAL` VALIDATION

| SOURCE_ID | owner | OWNER_KIND | T | ROLE | região | culturas | ACCESS | STATUS | veredito |
|---|---|---|---|---|---|---|---|---|---|
| `IT-T1-001` | ISTAT | agência nacional | T1 | VAL | nacional | todas | NÃO SEI | PRE | **NOT_TESTED** |
| `IT-T2-001` | ARPAE | agência regional | T2 | FS | Emilia-Romagna | transversal | NÃO SEI | NEW | **NOT_TESTED** |
| `IT-T2-002` | ARPAV | agência regional | T2 | FS | Veneto | transversal | NÃO SEI | NEW | **NOT_TESTED** |
| `IT-T2-003` | CNR-IBE | pesquisa | T2 | FS | nacional | transversal | NÃO SEI | NEW | **NOT_TESTED** |
| `IT-T2-004` | SIAS | agência regional | T2 | FS | Sicilia | transversal | NÃO SEI | NEW | **NOT_TESTED** |
| `IT-T2-005` | ALSIA | agência regional | T2 | FS | Basilicata | transversal | NÃO SEI | NEW | **NOT_TESTED** |
| `IT-T3-001` | ER Serv. Fitosanitario | agência regional | T3 | TG | Emilia-Romagna | múltiplas | PDF semanal | PRE | **NOT_RETESTED** |
| `IT-T3-002` | Campania SFR | agência regional | T3 | FS | Campania | múltiplas | NÃO SEI | NEW | **NOT_TESTED** |
| `IT-T3-003` | Campania SFR | agência regional | T3 | FS | Campania | NÃO SEI | NÃO SEI | NEW | **NOT_TESTED** |
| `IT-T3-004` | ALSIA | agência regional | T3 | FS | Basilicata | NÃO SEI | NÃO SEI | NEW | **NOT_TESTED** |
| **`IT-T3-005`** | **Terre dell'Etruria** | **cooperativa** | **T3** | **FS** | **Toscana** | **OLIVE** | NÃO SEI | NEW | **NOT_TESTED** |
| `IT-T3-006` | Terre dell'Etruria | cooperativa | T3 | TG | Toscana | múltiplas | NÃO SEI | NEW | **NOT_TESTED** |
| `IT-T3-007` | Sicilia Serv. Fitosan. | agência regional | T3 | TG | Sicilia | múltiplas | NÃO SEI | NEW | **NOT_TESTED** |
| `IT-T3-008` | ARIF Puglia | agência regional | T3 | FS | Puglia | OLIVE · DURUM | NÃO SEI | NEW | **NOT_TESTED** |
| `IT-T3-009` | Assoproli Bari | producer org | T3 | FS | Puglia (BA) | OLIVE | NÃO SEI | NEW | **NOT_TESTED** |
| `IT-T3-010` | APOL Lecce | producer org | T3 | FS | Puglia (LE) | OLIVE | NÃO SEI | NEW | **NOT_TESTED** |
| `IT-T3-011` | AGRIOS | rede técnica | T3 | TG | Südtirol | APPLE | NÃO SEI | NEW | **NOT_TESTED** |
| `IT-T3-012` | FEM | fundação | T3 | TG | Trentino | GRAPE · APPLE | NÃO SEI | NEW | **NOT_TESTED** |
| `IT-T4-001` | Min. della Salute | agência nacional | T4 | VAL | nacional | — | CSV direto | PRE | **NOT_RETESTED** |
| `IT-T5-001` | CREA | pesquisa | T5 | SCI | nacional | MAIZE | NÃO SEI | NEW | **NOT_TESTED** |
| `IT-T5-002` | FEM | fundação | T5 | SCI | Trentino | GRAPE · APPLE | NÃO SEI | NEW | **NOT_TESTED** |
| `IT-T5-003` | Giornate Fitopatologiche | soc. científica | T5 | SCI | nacional | múltiplas | NÃO SEI | NEW | **NOT_TESTED** |
| `IT-T5-004` | CNR IRIS | pesquisa | T5 | SCI | nacional | transversal | NÃO SEI | NEW | **NOT_TESTED** |
| `IT-T5-005` | SIRFI | soc. científica | T5 | SCI | nacional | transversal | NÃO SEI | NEW | **NOT_TESTED** |
| `IT-T7-001` | Terre dell'Etruria | cooperativa | T7 | ID | Toscana | OLIVE+ | NÃO SEI | NEW | **NOT_TESTED** |
| **`IT-T7-002`** | **MASAF** | **agência nacional** | **T7** | **ID** | **nacional** | por setor | NÃO SEI | NEW | **NOT_TESTED** |
| `IT-T7-003` | CAI | consórcio | T7 | TG | nacional | múltiplas | NÃO SEI | NEW | **NOT_TESTED** |
| `IT-T7-004` | Apo Conerpo | AOP | T7 | ID | ER + nacional | hortofrutícolas | NÃO SEI | NEW | **NOT_TESTED** |
| `IT-T7-005` | Agrintesa | cooperativa | T7 | ID | Emilia-Romagna | frutícolas | NÃO SEI | NEW | **NOT_TESTED** |
| `IT-T7-006` | FEM | fundação | T7 | ID | Trentino | GRAPE · APPLE | NÃO SEI | NEW | **NOT_TESTED** |
| `IT-T7-007` | Apofruit | cooperativa | T7 | TG | ER + nacional | frutícolas | PDF (esperado) | NEW | **NOT_TESTED** |
| `IT-T7-008` | Ortofruit Italia | producer org | T7 | ID | Piemonte | frutícolas | NÃO SEI | NEW | **NOT_TESTED** |
| `IT-T7-009` | VOG | cooperativa | T7 | ID | Südtirol | APPLE | NÃO SEI | NEW | **NOT_TESTED** |
| `IT-T7-010` | Melinda | consórcio | T7 | ID | Val di Non | APPLE | NÃO SEI | NEW | **NOT_TESTED** |
| `IT-T7-011` | CAVIT | cooperativa | T7 | ID | Trentino | GRAPE | NÃO SEI | NEW | **NOT_TESTED** |
| `IT-T7-012` | PICA | sistema técnico | T7 | ID | Trentino | GRAPE | NÃO SEI | NEW | **NOT_TESTED** |
| `IT-T9-001` | BASF Italia | empresa | T9 | DISC | nacional | múltiplas | NÃO SEI | **REDEF** | **NOT_TESTED** |
| `IT-T9-002` | Bayer CS Italia | empresa | T9 | DISC | nacional | múltiplas | NÃO SEI | NEW | **NOT_TESTED** |
| `IT-T9-003` | Syngenta Italia | empresa | T9 | DISC | nacional | múltiplas | NÃO SEI | NEW | **NOT_TESTED** |
| `IT-T9-004` | Corteva Italia | empresa | T9 | DISC | nacional | múltiplas | NÃO SEI | NEW | **NOT_TESTED** |
| `IT-T9-005` | Nufarm Italia | empresa | T9 | DISC | nacional | múltiplas | NÃO SEI | NEW | **NOT_TESTED** |
| `IT-T9-006` | FMC Italia | empresa | T9 | DISC | nacional | múltiplas | NÃO SEI | NEW | **NOT_TESTED** |
| `IT-T9-007` | UPL Italia | empresa | T9 | DISC | nacional | múltiplas | NÃO SEI | NEW | **NOT_TESTED** |
| `IT-T9-008` | ADAMA Italia | empresa (SELF) | T9 | DISC | nacional | múltiplas | NÃO SEI | NEW | **NOT_TESTED** |
| **`IT-T10-001`** | **ISMEA** | **agência nacional** | **T10** | **MKT** | **nacional** | múltiplas | NÃO SEI | NEW | **NOT_TESTED** |
| `IT-T10-002` | BMTI | soc. consortil | T10 | MKT | nacional | DURUM · SOFT · MAIZE | NÃO SEI | NEW | **NOT_TESTED** |
| `IT-T10-003` | ISTAT | agência nacional | T10 | MKT | nacional | por commodity | NÃO SEI | NEW | **NOT_TESTED** |
| `IT-T10-004` | ICQRF | agência nacional | T10 | MKT | nacional/regional | GRAPE (vinho) | NÃO SEI | NEW | **NOT_TESTED** |
| `IT-T10-005` | ICQRF | agência nacional | T10 | MKT | nacional/regional | OLIVE (azeite) | NÃO SEI | NEW | **NOT_TESTED** |
| `IT-T11-001` | FederUnacoma | assoc. setorial | T11 | DISC | Bologna | transversal | HTML | PRE | **NOT_RETESTED** |
| `IT-T11-002` | Unione Italiana Vini | assoc. setorial | T11 | DISC | itinerante | GRAPE | NÃO SEI | NEW | **NOT_TESTED** |
| `IT-T11-003` | Veronafiere | empresa | T11 | DISC | Verona | transversal | NÃO SEI | NEW | **NOT_TESTED** |
| `IT-T11-004` | FEM | fundação | T11 | DISC | Trentino | GRAPE · APPLE | NÃO SEI | NEW | **NOT_TESTED** |
| `IT-T12-002` | MASAF | agência nacional | T12 | TG | nacional | transversal | NÃO SEI | NEW | **NOT_TESTED** |

*(`IT-T13-001` não aparece nesta tabela: seu território está em dívida — ver §2.)*

**RECORRÊNCIA e AUTOMATION_FEASIBILITY** ficam fora da tabela de propósito.
A missão determina: *não inferir frequência por uma única data*. Sem uma única captura feita,
toda coluna de frequência seria invenção. Todas valem **`NÃO SEI`** até a Fase C.

---

## 5 · DUPLICIDADES E DECISÕES PENDENTES

### Fontes já existentes, reaproveitadas sem conflito
`IT-T1-001` · `IT-T3-001` · `IT-T4-001` · `IT-T11-001`

### Fontes existentes que exigem decisão sua

| ID | problema | proposta | o que trava |
|---|---|---|---|
| `IT-T9-001` | é ficha **compartilhada FR/ES/IT** e não mede empresa a empresa, como a missão exige | reatribuir a **BASF Italia** e abrir `IT-T9-002..008`; a ficha compartilhada continua valendo para FR e ES | o ID já está no placar de 37 e em `test_handoff.py:111` |
| `IT-T13-001` | território proibido por esta missão | ver §2 | mesma trava de contagem |

### Sobreposições a medir ANTES de operacionalizar

| candidata nova | já existe | a pergunta honesta |
|---|---|---|
| `IT-T10-001` ISMEA | `EU-T10-001` DG AGRI (**GREEN**, já dá 16 praças italianas de cereais) | o que a ISMEA acrescenta **fora de cereal**? Se for só cereal, é duplicação. |
| `IT-T5-004` CNR IRIS | `EU-T5-001` OpenAlex (**GREEN**, já filtra afiliação italiana) | IRIS traz tipo documental que o OpenAlex não cobre (relatório técnico, projeto)? |
| `IT-T10-003` ISTAT comércio exterior | `EU-T10-003` Eurostat (**NÃO SEI**, por consulta malformada) | **consertar a consulta do Eurostat pode ser mais barato** que abrir rota nova |

---

## 6 · O QUE CADA FONTE PRECISA PROVAR NA FASE C

Regra da missão: **homepage institucional não conta como amostra.**

### As três com maior valor esperado

**`IT-T3-005` — Terre dell'Etruria · monitoraggio mosca dell'olivo** *(prioridade 1)*
Precisa entregar: `data · ponto · local · fenologia · captura/amostra · infestação · alerta · recomendação`.
É a **única candidata identificada nesta missão a dar sinal de campo medido por ponto em olivo** —
a granularidade que hoje, no acervo inteiro, só a RAIF andaluza (`ES-T3-001`) entrega.
Classes de evidência a **não** fundir: `OBSERVED_FIELD_SIGNAL` (a captura) e `COOPERATIVE_GUIDANCE` (a recomendação).
**Não prova:** venda · estoque · market share · uso realizado · produto ADAMA comprado · incidência nacional.

**`IT-T7-002` — MASAF · elenco OP/AOP riconosciute** *(prioridade 5)*
É `DISCOVERY / IDENTITY`, **não sinal agronômico**. Tratar a lista de OP do MASAF como sinal de
campo é exatamente o erro que a missão nomeia. Mas é o **denominador** sem o qual toda contagem
de cooperativa italiana fica sem base.
**Prova:** quais organizações o Estado reconhece, em que setor e região. **Não prova:** atividade, volume, influência.

**`IT-T10-004/005` — ICQRF · Cantina Italia e Frantoio Italia**
São das **pouquíssimas candidatas a ESTOQUE DECLARADO** em todo o acervo — o Atlas registra estoque
como coisa que nenhuma fonte prova. `Frantoio Italia` casa com `IT-T3-005` pelo lado do mercado: a
mosca de um lado, o azeite estocado do outro.

### Regras de classificação que a Fase C não pode violar

```
SINTOMA OBSERVADO      ≠  RISCO MODELADO
RECOMENDAÇÃO           ≠  TRATAMENTO REALIZADO
PRODUTO CITADO         ≠  PRODUTO AUTORIZADO
AUTORIZADO             ≠  COMERCIALMENTE DISPONÍVEL
MEDIA_SIGNAL           ≠  FIELD_SIGNAL
DISCIPLINARE           ≠  CURRENT_FIELD_SIGNAL
COMPANY_CLAIM          ≠  REGULATORY_FACT
SOURCE_LOCATION        ≠  FACT_LOCATION
```

O caso concreto de `SOURCE_LOCATION ≠ FACT_LOCATION` neste catálogo: **Apo Conerpo** tem sede em
Bologna e associadas em várias regiões. O endereço da organização **não** é a geografia do fenômeno.

### Restrições duras

- **`IT-T7-012` PICA** — testar **somente o que for público**. Se o sistema existir mas os dados
  forem privados, classificar `PUBLIC_CAPABILITY`. **Não tentar contornar autenticação.**
- **`IT-T3-003` SIMFITO** — mesma regra.
- **`IT-T7-001`** e demais fichas com nomes de agrônomos — **GDPR: pessoas físicas identificadas.**
  `NÃO SEI / REQUER REVISÃO`, alinhado com a pendência P-008/P-009 já aberta no acervo.

---

## 7 · LACUNAS QUE ESTE CATÁLOGO NÃO FECHA

- **T8 FARMERS & INFLUENCERS — nenhuma fonte italiana catalogada.** A missão pede busca dirigida só
  para `DURUM_WHEAT`, `MAIZE` e `OLIVE`, e proíbe coleta horizontal. Sem navegador italiano não houve
  descoberta. O acervo já registra que `FIELD AUTHORITY` e `COMMERCIAL INFLUENCE` **não têm fonte em
  país nenhum** — a Itália não muda isso.
- **T6 RESEARCHERS — nenhuma ficha italiana nova.** Por desenho: `EU-T5-001` (OpenAlex, GREEN) já
  serve T6 por `CROP × ISSUE × INSTITUTION × TERRITORY`, e a missão proíbe ranking. Abrir ficha
  italiana de T6 seria duplicar.
- **DISTRIBUTION (o antigo T13) na Itália** — continua `NÃO SEI`. A perna "fluxo" está vazia nos três países.
- **Cultura × alvo na Itália** — `IT-T4-001` é GREEN mas não traz cultura nem alvo (estão na etichetta,
  fora do dataset). A assimetria com a França **permanece**, e nenhuma fonte deste catálogo a resolve.

---

## 8 · PRÓXIMO PASSO

1. **Ligar o Chrome com VPN italiana** — confirmar `"country": "IT"` em `ipinfo.io/json` antes de tudo.
2. Rodar a Fase C na ordem de prioridade da missão, começando por `IT-T3-005`.
3. Aplicar a assimetria do §0: `abriu` → registra; `bloqueou` → `NÃO SEI`, **nunca RED**.
4. Só então Fases D–G.
5. **Restaurar o Python** desta máquina antes da Fase H.
6. **Decidir** as duas pendências de ID do §5 — elas exigem mexer no placar canônico.

---

## 9 · A PERGUNTA CENTRAL

Para cada fonte: *"Se o SINTONIA coletar esta fonte toda vez que ela mudar, qual decisão concreta
da ADAMA ficará melhor informada?"*

Este catálogo **não responde** essa pergunta ainda — responder sem amostra seria opinião.
O que ele faz é deixar cada fonte com a pergunta escrita ao lado, para que a Fase C responda
com documento na mão.

---

# 10 · FASES C–G EXECUTADAS — 2026-09-07

**Ambiente:** VPN italiana confirmada (`205.147.30.20 · Milano · IT · AS208172 Proton AG`).
**Método:** `curl` com User-Agent de navegador, saindo pelo IP italiano. A extensão do Chrome
não chegou a parear — mas descobriu-se que **não era pré-requisito**: a VPN é do sistema
inteiro, e o `curl` sai pela Itália igual.

## 10.1 · A regra de assimetria desta rodada

A REGRA 0 diz `BLOCKED_EM_DATACENTER ≠ BLOCKED_EM_BROWSER_ITALIANO`. Esta rodada acrescenta
uma terceira categoria, pelo mesmo raciocínio:

```
ACCESS_OK no curl italiano   →  sinal FORTE. Se abre para curl, abre para navegador.
BLOCKED no curl italiano     →  sinal FRACO. Muitos sites recusam curl e aceitam navegador.
                                 BLOCKED_EM_CURL_ITALIANO ≠ BLOCKED_EM_BROWSER_ITALIANO.
```

Por isso **nenhum RED foi emitido nesta missão**. Bloqueio virou `NÃO SEI — reteste em navegador`.

## 10.2 · Probe de acesso — 43 URLs distintas, 54 fontes

`data/samples/IT-PROBE/probe-fase-c.json`

| resultado | quantas | leitura |
|---|---|---|
| `ACCESS_OK` | 31 | abriu com corpo real |
| `ACCESS_OK_MAS_MAGRO` | 2 | 200 com casca (ALSIA = meta-refresh; SIAS = frameset antigo) |
| `BLOCKED_PARA_CURL` | 4 | ARIF Puglia, Bayer, Syngenta, ADAMA — **inconclusivo** |
| `NETWORK_ERROR` | 5 | ver §10.3 — **três eram endereço errado no catálogo, não bloqueio** |
| `ROTA_INEXISTENTE` | 1 | ARPAE — URL do catálogo devolve 404; a rota viva foi achada |

## 10.3 · Correções de endereço encontradas

| fonte | o que o catálogo dizia | o que é de verdade |
|---|---|---|
| ARPAE (T2) | `arpae.it/it/temi-ambientali/meteo/agrometeo` → **404** | `arpae.it/it/temi-ambientali/meteo/report-meteo/bollettini-e-rapporti-agrometeo/bollettini-agrometeo` |
| Campania (T3) | `www.agricoltura.regione.campania.it` → **erro de certificado** | `agricoltura.regione.campania.it` (sem `www`) → 200 |
| FEM OpenPub (T5) | `publications.fmach.it` → **nome não existe** | `openpub.fmach.it` → 200 |
| ISTAT (T1) | portal `esploradati.istat.it` exige JavaScript e chegou a dar erro de servidor | a **API SDMX 2.1** do mesmo domínio funciona sem chave |
| FMC Italia (T9) | `www.fmcagro.it` → **nome não existe** | `NÃO SEI` — nenhuma variante testada resolveu |
| CAI (T7) | `consorziagrariditalia.it` → conexão derrubada | `NÃO SEI` — reteste em navegador |
| Giornate Fitopatologiche (T5/T11) | um único owner | os PDFs moram em **`aipp.it`** — são **duas** organizações |

## 10.4 · Amostras preservadas — Fase D

Todas em `data/samples/IT-SOURCE-SAMPLES/<SOURCE_ID>/`, com `MANIFEST.json`
(MIME · BYTES · SHA256 · assinatura real dos bytes · o que prova · o que **não** prova).

| SOURCE_ID | fonte | amostra | recorrência | veredito | P |
|---|---|---|---|---|---|
| `IT-T3-002` | Campania — bollettini fitosanitari | 3 PDFs (SA 02-09 e 26-08, NA 02-09) | **WEEKLY provado** — 14 edições de 7 em 7 dias na página de 2026 | **GREEN** | P0 |
| `IT-T2-001` | ARPAE — bollettino agrometeo | 2 PDFs (n.35 e n.34) | **WEEKLY provado** — numeração sequencial + 7 dias | **GREEN** | P0 |
| `IT-T4-001` | Ministero della Salute — fitosanitari | CSV 4,6 MB (17.696 linhas) + dicionário | `NÃO SEI` — nome traz data de hoje, mas só uma data observada | **GREEN** | P0 |
| `IT-T1-001` | ISTAT — coltivazioni por província | CSV SDMX (77.363 linhas, 233 culturas) | ANNUAL declarado, não medido | **GREEN** | P0 |
| `IT-T3-005` | Terre dell'Etruria — mosca dell'olivo | HTML 274 KB + 139 pontos | `NÃO SEI` — site não guarda arquivo | `NÃO SEI` | P0 candidato |
| `IT-T10-002` | BMTI — prezzi e analisi | 2 HTML (cereais 24/08, azeite) | `NÃO SEI` | **YELLOW** | P1 |
| `IT-T5-003` | Giornate Fitopatologiche / AIPP | 2 PDFs (bilancio olivo Basilicata e Marche) | ANNUAL / EVENT_DRIVEN | **YELLOW** | P1 |

## 10.5 · Fontes que exigem navegador — não são RED

Ficam `NÃO SEI` com motivo escrito, esperando a extensão do Chrome:

```
AGRIOS (T3)              site sem links no HTML cru — provável JavaScript
SIAS Sicilia (T2)        frameset antigo, conteúdo fora do HTML servido
ARPAV zone (T2)          a escolha da zona é JavaScript; a cadência declarada é 2x/semana
MASAF OP/AOP (T7)        a lista de OP não apareceu por navegação simples
ALSIA fitosanitari (T3)  a página é descrição de serviço, não arquivo de documento
ARIF Puglia · Bayer · Syngenta · ADAMA (T3/T9)   403 para curl — inconclusivo
CAI (T7)                 conexão derrubada — inconclusivo
```

---

# 11 · FECHAMENTO — QUATRO CORREÇÕES E UMA LEI · 2026-09-07

Escritas **depois** da rodada, corrigindo formulações minhas que estavam erradas ou ambíguas.
Nenhum byte de amostra foi tocado. Só classificação.

## 11.1 · Ministero della Salute — não é "só descoberta"

Eu escrevi *"entregam só descoberta e identidade"*. **Errado.**

```
TERRITORY   = T4 REGULATORY
OWNER_KIND  = OFFICIAL_NATIONAL_AGENCY
SOURCE_ROLE = REGULATORY_PRIMARY
```

É o registro oficial de autorização — a fonte que separa `COMPANY_CLAIM` de `REGULATORY_FACT`.
Serve **também** como identidade (quem é o titular) e validação, mas isso é uso secundário.

## 11.2 · Giornate Fitopatologiche / AIPP — três territórios, dois donos

Eu escrevi *"só descoberta e identidade"*. **Errado.** A mesma origem alimenta três leituras:

| território | o que a amostra entrega |
|---|---|
| **T5 SCIENCE** | o balanço fitossanitário da campanha, por região e cultura |
| **T6 RESEARCHERS** | nome, e-mail institucional, órgão e região de quem assina |
| **T11 EVENTS** | o ciclo *"I Giovedì dell'AIPP"* e as Giornate — data e sessão |

**Uma fonte, três territórios alimentados.** Não duplicar o `SOURCE_ID`; a origem é única.

E os **donos são dois**: o link está em `giornatefitopatologiche.it`, mas os PDFs moram em
`aipp.it/wp-content/uploads/`. Não fundir. *(O `OWNER_KIND` de cada um é provisório —
não foi medido no estatuto das entidades nesta rodada.)*

## 11.3 · ARPAE — clima não vira praga

```
TERRITORY      = T2 CLIMATE / WATER / SOIL
EVIDENCE_CLASS = AGROCLIMATIC_SIGNAL

AGROCLIMATIC_SIGNAL ≠ PEST_OCCURRENCE
```

Eu tinha classificado como `OBSERVED_FIELD_SIGNAL`, o que abre porta para promoção indevida.
O boletim **pode** ajudar a interpretar pressão agronômica — explicar por que a praga apertou.
**Não pode**, sozinho nem combinado, virar ocorrência de praga. Chuva e temperatura não são inseto.

## 11.4 · "47 sem teste" era ambíguo — e o número estava errado

Porta medida não é fonte não testada. Os quatro estados, com os números reais:

| estado | n | o que significa |
|---|---|---|
| rotas no catálogo | **54** | — |
| `ROUTE_PROBED` | **51** | a porta foi medida do IP italiano |
| `SAMPLE_CAPTURED` | **7** | um documento real foi baixado, além da homepage |
| `RAW_PRESERVED` | **7** | está no disco com MIME/BYTES/SHA256, e o hash confere |
| `ANALYTICALLY_CLASSIFIED` | **7** | tem veredito, recorrência, o que prova e o que **não** prova |
| **probadas sem amostra** | **44** | testadas na porta, não na entrega |
| **nunca tocadas** | **3** | `IT-T3-003` · `IT-T3-010` · `IT-T7-012` — o catálogo não tem URL para elas |

`51 + 3 = 54`. As 7 com amostra estão **dentro** das 51, não são grupo separado.

## 11.5 · LEI PERMANENTE — endereço errado não é bloqueio

```
ROUTE_NOT_FOUND        ≠  SOURCE_BLOCKED
OLD_URL_FAILURE        ≠  CURRENT_SOURCE_FAILURE
```

Nesta rodada, **7 supostos bloqueios eram endereço errado no nosso próprio catálogo** — um
`www` a mais, um host morto, um caminho antigo. Se ninguém conferisse, virariam
*"a Itália bloqueia"*.

**Antes de escrever `BLOCKED`, é obrigatório:**

1. verificar o domínio oficial;
2. localizar a página canônica atual;
3. conferir redirects;
4. procurar o link atual a partir da homepage ou da busca do próprio site;
5. só então registrar bloqueio.

**Erro de catálogo nosso nunca vira defeito da fonte.**
Irmã da lei já registrada: `BLOCKED_EM_CURL_ITALIANO ≠ BLOCKED_EM_BROWSER_ITALIANO`.
