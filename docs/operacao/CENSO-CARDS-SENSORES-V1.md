# CENSO DOS CARDS E DOS SENSORES — V1

> **A MATRIZ É A FONTE. ESTE FICHEIRO É A LEITURA DELA.**
>
> Todos os números vivem em [`data/derivados/MATRIZ-CARDS-SENSORES-V1.json`](../../data/derivados/MATRIZ-CARDS-SENSORES-V1.json),
> escrito por `system-map/scripts/censo_cards_sensores.py`. O que está aqui e
> não está lá é **julgamento** — as causas-raiz, a ordem e a resposta sobre a
> Phase 11 —, e julgamento não tem outro dono.
>
> Os números citados abaixo estão num bloco `MEDIDO` que
> `tests/test_censo_cards_sensores.py` compara, um a um, com o JSON. Um número
> que envelheça aqui **rebenta o teste**. É a única forma honesta de um
> documento humano citar uma medição de que não é dono.

---

## 1 · O QUE FOI MEDIDO, E O QUE NÃO FOI

Esta missão construiu o mapa. **Não** consertou nada, não abriu a Phase 11, não
tocou no portal, no SINTONIA SCRAP nem no banco vivo.

O censo não mediu nada de novo. Ele **juntou** oito censos que já existiam e fez
a pergunta que nenhum deles fazia sozinho:

```
QUE CARD PRECISA DE QUE SENSOR, E ATE ONDE O DADO CHEGA?
```

---

## 2 · «CARD» TEM TRÊS SIGNIFICADOS, E CONFUNDI-LOS ERA O PRIMEIRO RISCO

| espécie | o que é | quem já a conta |
|---|---|---|
| **peça do System Map** | módulo de arquitetura; `censo_da_topologia.py` chama-lhe `CARD_ID` | `system-map/data/topologia.generated.json` |
| **ferramenta do portal** | tela com contrato de bloco, consumidor e pergunta de negócio | `system-map/data/casco.generated.json` |
| **bloco visual** | marcação sem contrato de dados | ninguém, e está certo |

**O censo mede a espécie 2** — a única que é unidade operacional. A 1 é o mapa
do código e tem censo próprio; a 3 é marcação e não promete dado a ninguém.

> Nem todo elemento visual chamado *card* é uma unidade operacional.

---

## 3 · «SENSOR» NÃO É O QUE TEM `sensor` NO NOME

Havia dois ficheiros `regras/sensor_*.py`, e responder «dois» seria uma resposta
errada a uma pergunta certa. A espécie operacional é o **executor**: quem vai à
fonte e traz evidência. É esse que o censo conta.

---

## 4 · AS CINCO PROVAS, E OS CINCO NÚMEROS QUE ELAS DEIXAM

```
MEDIDO
AS_CINCO_PROVAS.EXISTE     = 58
AS_CINCO_PROVAS.CORRE      = 32
AS_CINCO_PROVAS.RODOU      = 2
AS_CINCO_PROVAS.PRODUZIU   = 2
AS_CINCO_PROVAS.ENTROU     = 0
```

| prova | pergunta | sobreviveram | medido por |
|---|---|---|---|
| EXISTE | há ficheiro? | 58 | `executores.generated.json` |
| CORRE | é chamável sem rede, sem pago, sem produção? | 32 | `executores.generated.json` |
| RODOU | deixou rastro de execução? | 2 | `provas-de-execucao.json` |
| PRODUZIU | o rastro tem saída com etapa observada? | 2 | `provas-de-execucao.json` |
| ENTROU | a saída atravessou a fronteira canónica? | 0 | `fronteira.observada.json` |

**Nenhum degrau empresta o seu `YES` ao seguinte.** É por isso que isto é uma
escada com cinco números e não um só. A queda de 58 para 32 é ambiente; a de 32
para 2 é instrumentação; a de 2 para 0 é arquitetura — e é a única que impede a
Collection de fechar.

Os dois que rodaram são `coleta/executor_texto_de_pdf.py` (modo `LEGACY_REPLAY`,
etapas `RAW → DERIVED`) e `coleta/rota_forward_documento.py` (modo `FORWARD`,
etapas `DERIVED → STRUCTURED → ADMISSION`). Ambos provados por teste, não por
corrida de produção.

> **A quinta prova não se mede por sensor, e isso é um facto e não um limite
> meu.** O ledger de fluxo declara `POR_EXECUTOR = NOT_INSTRUMENTED`: guarda a
> observação e não quem a produziu. Perguntar-lhe «este sensor entrou na
> cadeia?» não tem resposta possível. O que se mede é o degrau: a fronteira não
> tem destino escrito nem consumidor, logo nenhuma saída a atravessou — e isso
> vale para os 58 de uma vez.

---

## 5 · OS ONZE CARDS

```
MEDIDO
CARDS_TOTAL                              = 11
CARDS_POR_ESTADO.ALIMENTADO_POR_REAL     = 1
CARDS_POR_ESTADO.MISTURA_REAL_E_FIXTURE  = 6
CARDS_POR_ESTADO.SEM_FONTE_DECLARADA     = 4
```

| card | nome | de onde vem | estado |
|---|---|---|---|
| `windows` | Finestre Colturali | REAL | **ALIMENTADO_POR_REAL** |
| `meeting` | Radar delle Opportunità | MISTURA | MISTURA_REAL_E_FIXTURE |
| `market` | Polso di Mercato | MISTURA | MISTURA_REAL_E_FIXTURE |
| `competitors` | Concorrenza | MISTURA | MISTURA_REAL_E_FIXTURE |
| `science` | Intelligence Scientifica | MISTURA | MISTURA_REAL_E_FIXTURE |
| `portfolio` | Portafoglio | MISTURA | MISTURA_REAL_E_FIXTURE |
| `archive` | Archivio | MISTURA | MISTURA_REAL_E_FIXTURE |
| `future` | Archivio segnali | NÃO SEI | SEM_FONTE_DECLARADA |
| `voices` | Voci dal Campo | NÃO SEI | SEM_FONTE_DECLARADA |
| `sources` | Registro delle fonti | NÃO SEI | SEM_FONTE_DECLARADA |
| `field` | Rete Commerciale di Campo | NÃO SEI | SEM_FONTE_DECLARADA |

**Um card fala de dado com procedência. Seis ilustram e medem ao mesmo tempo sem
dizer qual é qual. Quatro não declaram fonte nenhuma.**

### O degrau que este censo teve de acrescentar a si próprio

A primeira versão do gerador terminava a escada de estado em
`else ALIMENTADO_POR_REAL`. Com isso, o **Polso di Mercato** saía «real» porque
a sua única camada, `ITALY_MARKET`, não é fixture — mas também não é
classificada: o seu tipo é `NAO SEI`, e o contrato dela confessa por escrito que
ali há dado escrito à mão.

```
UM `else` NO FIM DE UMA ESCADA DE PROVA INVENTA A PROVA QUE FALTA.
```

O degrau `NAO_SEI_SE_E_REAL` existe desde então, para que a ausência de prova
tenha nome em vez de ser absorvida pelo caso mais favorável. Hoje nenhum card
cai nele — porque a confissão do contrato empurrou o Polso di Mercato para
`MISTURA`, que é onde ele sempre esteve.

---

## 6 · A MATRIZ É PEQUENA, E ISSO É A DESCOBERTA

Uma matriz 11 × 58 daria 638 células e a sensação de um mapa. Seria falsa. As
arestas que **existem** são as que o contrato de bloco declara, e elas apontam
para **camadas do portal** — nunca para um executor.

```
CARD  ->  CAMADA DO PORTAL  ->  (quem a produz?)  ->  SENSOR
                                 ^
                                 aqui a corrente parte
```

```
MEDIDO
CAMADAS_DO_PORTAL          = 15
CAMADAS_COM_GERADOR        = 5
ARESTAS_POR_CLASSE.PROVEN  = 1
ARESTAS_POR_CLASSE.BROKEN  = 21
ARESTAS_POR_CLASSE.MISSING = 4
```

- **PROVEN (1)** — `archive → ITALY_APP_MODEL`, gerada por `superficie/it_casa_dados.py`.
- **BROKEN (21)** — a camada é um ficheiro **commitado sem gerador nesta árvore**.
  Nenhum sensor a reescreve. `italy-ingested.js` abre com *"Generated from the
  normalized research package"* e `"BUILT":"2026-09-02"`; o gerador não está aqui.
- **MISSING (4)** — o card não declara camada nenhuma: `future`, `voices`,
  `sources`, `field`.

> Procurou-se quem **escreve**, não quem **menciona**. `harness.mjs` e
> `checks.mjs` citam todas as camadas porque as **auditam**. Contar uma
> auditoria como geração pintaria a matriz inteira de verde por causa do
> auditor.

---

## 7 · A FRONTEIRA — ONDE A COLLECTION DEVIA TERMINAR

```
MEDIDO
A_FRONTEIRA.CONTRATO        = COL-LAW-043
A_FRONTEIRA.READY_PRODUZIDO = false
A_FRONTEIRA.CONSUMIDORES    = 0
A_FRONTEIRA.GAP             = READY_NUNCA_PRODUZIDO
```

O contrato existe e tem dono (`admissao/admissao.py :: pronto_para_inteligencia()`).
Tem **um** produtor em runtime (`orquestrador/orquestrador.py`, só por linha de
comando — nenhum workflow o chama). O destino
`data/samples/PRONTO-PARA-INTELIGENCIA/<RUN_ID>.json` **não existe**. Consumidores: **zero**.

> **CORRIGIDO EM 2026-09-11 (C-MADRUGADA-CR1).** Este gap chamava-se
> `READY_SEM_CONSUMIDOR`, e esse nome estava errado por inteiro. O medidor
> derivava o diagnóstico **do consumidor**, quando `READY CONSUMER = 0` é o
> alvo de fechamento declarado. Red team com o medidor real: o estado-alvo
> (READY produzido, zero consumidores) saía com o **mesmo** diagnóstico de nada
> ter sido produzido, e um consumidor artificial **sem produção nenhuma**
> limpava o gap.
>
> Zero consumidores nunca foi o defeito. O defeito é que **nunca foi produzido
> um READY**, e é esse que o gap nomeia agora. Prova em
> `provas/o_corte_de_cr1.py` e `tests/test_fronteira_mede_producao.py`.

```
COLLECTION TERMINA NA SALA DE ESPERA.
E A SALA DE ESPERA NUNCA RECEBEU NINGUEM.
```

---

## 8 · AS CAUSAS-RAIZ

Vinte e três defeitos abertos, 26 arestas e cinco degraus não são vinte e três
problemas. São **nove**. Agrupar não é arredondar: é dizer onde uma correcção
fecha várias linhas de uma vez.

```
MEDIDO
ISSUES_DA_COLETA.abertos = 23
ISSUES_DA_COLETA.total   = 30
```

### CR-1 · O QUE CHEGA À PORTA É O ÍNDICE DA COLHEITA, NÃO A COLHEITA
`COL-015` · `COL-003` · `COL-004` · `COL-013`

> **REESCRITO EM 2026-09-11 (C-MADRUGADA-CR1). A versão anterior desta causa
> dizia «a cadeia canónica está cortada em duas juntas», e isso foi MEDIDO E
> REFUTADO.** Ficou aqui o que a medição mostrou.

A cadeia **corre inteira**. Numa única corrida real, sem rede e sem banco
(`orq.correr(pedido, so_a_porta=True)`), oito estações ficaram provadas por
execução controlada: pedido, plano, escolha de executor, saída encontrada,
ingresso, RAW preservado, item na porta, decisão da porta. Nada está cortado.

O que corta é outra coisa, e é mais precisa:

```
larga_em  ->  _MANIFESTO.json     o INDICE dos documentos descarregados
              CORPUS-*.json       o CATALOGO de pessoas
              CONTAS-V1.json      a ficha de ONDE se pode coletar
```

`a_colheita()` tem uma heurística genérica — «uma lista, ou o primeiro campo do
ficheiro que seja lista de fichas» — e ela transforma **linhas de um índice** em
pseudo-itens. A porta recusa-os, e recusa-os **bem**, com o vocabulário certo.

```
O INDICE DE UMA COLHEITA NAO E A COLHEITA.
E UM RECIBO — E UM RECIBO NAO SE ADMITE, LE-SE.
```

Medido sobre todo o material que as receitas alcançam hoje:

| resultado da porta | itens |
|---|---|
| `NAO_SEI` («o item veio sem texto nenhum») | 182 |
| `NAO_SE_APLICA` («é ficha de conta ou de catálogo») | 71 |
| `SIM` | **0** |

Duas das cinco receitas apontam `larga_em` para pastas que **não existem**
nesta árvore. E `data/raw/IT-ROTULOS/` contém **só** `_MANIFESTO.json`: os 163
PDF que ele indexa não estão cá.

- **Dono:** `orquestrador/orquestrador.py :: a_colheita()` + o `larga_em` das receitas
- **Camada:** COLETA
- **Sensores afectados:** 58
- **Prova:** `provas/o_corte_de_cr1.py` · `provas/so_a_colheita_atravessa.py`

### CR-1 — OS CINCO DEGRAUS, E ONDE ELA ESTÁ HOJE

> **FECHADO EM 2026-09-11 (C-IMPL-EXECUTOR-RETURN-RUNTIME-V1) o degrau 2, e
> mais nenhum.** «O runtime respeita o contrato» não é «a Collection fechou»,
> e juntar as duas frases seria repetir o erro que este censo existe para não
> cometer.

| degrau | estado | prova |
|---|---|---|
| `CONTRACT_DEFINED` | **SIM** | `COL-LAW-505` · `leis/retorno_da_coleta.py` |
| `RUNTIME_CONNECTED` | **SIM** | a heurística saiu do orquestrador; `so_o_que_entra()` decide |
| `PAYLOAD_AVAILABLE` | **NÃO** | 4 de 5 executores sem payload nesta árvore |
| `REAL_HARVEST_OBSERVED` | **NÃO** | nenhuma corrida real declarou colheita |
| `READY_PRODUCED` | **NÃO** | zero |

```
FALSE_HARVEST_ANTES   253
FALSE_HARVEST_DEPOIS    0
SUPPORT_ITEMS_BLOCKED   8
```

O número caiu de 253 para zero **sem se perder um único item real** — porque
não havia nenhum. O que havia era índice, catálogo, plano e recibo a viajar com
cara de observação.

```
DEIXAR DE CONTAR O QUE NAO EXISTIA NAO E PERDER DADO.
E PARAR DE MENTIR SOBRE ELE.
```

**O que a ligação tornou visível, e não criou:** a unidade italiana chega à
porta com `SOURCE_ID` maiúsculo, que é o nome do contrato em
`coleta/ingresso.py :: DO_COLETOR`. E `admissao/admissao.py :: _tem_origem`
procura `source_id` minúsculo. Dois nomes para o mesmo campo, invisíveis até
hoje porque nenhuma unidade italiana tinha chegado à porta. **Não foi
corrigido**: mexer na admissão para conseguir verde é o que esta missão estava
proibida de fazer.

### CR-2 · A FRONTEIRA NUNCA PRODUZIU UM READY
fronteira `READY_NUNCA_PRODUZIDO`

Ver secção 7. É a razão literal pela qual a Collection não fecha: fechar a
Collection é entregar na Sala de Espera, e nunca ninguém entregou.

> **Medido em 2026-09-11:** a cadeia `EXECUTOR → INGRESSO → ADMISSÃO` **corre
> inteira** — não está cortada. 253 itens reais atravessaram-na e a porta
> julgou todos. Nenhum foi admitido, porque o que lhe chega não é colheita: é
> o **índice** da colheita. Ver `provas/o_corte_de_cr1.py`.

- **Dono:** `admissao/admissao.py`
- **Camada:** FRONTEIRA
- **Cards afectados:** 11 (nada do que mostram pode ter vindo por aqui)
- **Sensores afectados:** 58
- **Depende de:** CR-1 (produzir) e CR-8 (o que se produz ser admissível)

### CR-3 · AS CAMADAS DO PORTAL SÃO FICHEIROS COMMITADOS SEM GERADOR
21 arestas `BROKEN`

Quinze camadas, cinco com gerador — e as cinco pertencem todas ao mesmo
ficheiro (`superficie/it_casa_dados.py`). As restantes dez são bytes commitados.
Mesmo com a cadeia inteira reparada, **nenhum sensor conseguiria reescrever o
que o card lê**.

- **Dono:** `superficie/`
- **Camada:** PORTAL
- **Cards afectados:** 7 (todos os que declaram camada)
- **Risco:** os artefactos de inteligência congelados nunca descongelam sozinhos.

```
MEDIDO
ARTEFATOS_DE_INTELIGENCIA_CONGELADOS = 73
```

### CR-4 · QUATRO CARDS NÃO TÊM CONTRATO DE BLOCO
4 arestas `MISSING`

`future`, `voices`, `sources`, `field`. Não é que a fonte esteja errada: não há
pergunta escrita. Não se pode sequer perguntar que sensor os alimenta.

- **Dono:** `italia-portale/audit/blocks/`
- **Camada:** PORTAL
- **Cards afectados:** 4

### CR-5 · O LEDGER NÃO GUARDA QUEM CORREU NEM QUE ETAPA FOI
fluxo `POR_EXECUTOR` · `POR_ETAPA` · `CUSTO` = `NOT_INSTRUMENTED`

```
MEDIDO
OBSERVACOES_NO_LEDGER = 144
CORRIDAS_NO_LEDGER    = 6
```

144 observações, nenhuma atribuível a um executor. E todas as 144 são da rota
`RC-9` (`GIT_LEDGER`) — que o próprio censo de fluxo classifica como **dívida, e
não estrada a fechar**. É por isso que a prova `RODOU` só tem 2 de 58: ela só
pode vir de testes.

- **Dono:** `orquestrador/` + `pedido/receitas.py`
- **Camada:** TELEMETRIA
- **Sensores afectados:** 58
- **Porque importa mais do que parece:** sem isto, nenhuma correcção das outras oito se consegue **provar** em produção.

### CR-6 · «COMO ATENDER ESTE PEDIDO» TEM VÁRIOS DONOS
`COL-010` · `COL-011` · `COL-001` · `COL-008` · `COL-014`

A decisão de rota vive em três sítios; «colher Instagram» tem quatro portas; o
SINTONIA SCRAP chama dez scripts pelo nome sem passar pelo orquestrador; dois
botões escolhem a ferramenta em vez de dizerem o que querem.

```
UMA RESPONSABILIDADE COM TRES DONOS NAO TEM DONO.
```

- **Dono:** `orquestrador/orquestrador.py`
- **Camada:** COLETA
- **Risco:** cada correcção de CR-1 tem hoje de aterrar em três sítios, ou diverge.

### CR-7 · O ATLAS DE FONTES ESTÁ QUASE TODO POR ABRIR
`COL-005` · `COL-007` · `COL-009` · `COL-017`

```
MEDIDO
FONTES_NO_ATLAS         = 23
FONTES_COM_CONTRATO     = 5
FONTES_JA_COLETADAS     = 4
FONTES_NUNCA_COLETADAS  = 22
```

Vinte e três fontes declaradas, cinco com contrato, quatro alguma vez colhidas.
O LinkedIn tem seis contas em ficha e **zero** autorizadas. A política «grátis
primeiro» aparece em texto em dois ficheiros e em **código em nenhum**.

- **Dono:** `coleta/` + o atlas de fontes
- **Camada:** COLETA
- **Nota:** `DECLARED EDGE ≠ OBSERVED EDGE` — o atlas descreve intenção, não capacidade.

### CR-8 · O ACERVO EXISTENTE TEM DÍVIDA DE PROCEDÊNCIA
`COL-027` · `COL-028` · `COL-030` · `COL-024`

Nenhum dos 43 textos derivados tem `FACT_TIME`, e a porta devolve 43 `NÃO SEI`
pela mesma regra. Seis PDF existem duas vezes em disco com o mesmo SHA256. Três
textos tirados de PDF à mão não têm pai comprovado.

- **Dono:** `guarda/`
- **Camada:** RAW / DERIVADO
- **Porque bloqueia:** `COL-027` é o que impede o `READY` de produzir seja o que for. CR-2 pode ficar pronto e continuar vazio por causa desta.

### CR-9 · PEÇAS DECLARADAS QUE NINGUÉM CHAMA
`COL-006` · `COL-022` · `COL-019`

`voz.pipeline_video()` é descrito como caminho obrigatório e um HANDOFF
chama-lhe «FECHADO»; medido hoje, nenhum ficheiro de produção o chama. «O lugar
do fato — CARIMBADO NA COLETA» não é importado por coletor nenhum.

```
MODULE EXISTS != EDGE EXISTS != FLOW EXISTS.
```

- **Dono:** vários
- **Risco:** documentação que promete um caminho que não existe custa mais do que caminho nenhum.

### O QUE FICOU FORA DAS NOVE

Três defeitos abertos não partilham causa com nenhum outro e ficam singulares —
agrupá-los à força seria fabricar uma causa: `COL-025` (medição de recall da
porta), `COL-026` (corrida entre dois regeneradores do mapa), `COL-029`
(`pdftotext` é ferramenta de fora do Python e não existe no CI).

---

## 9 · A ORDEM — POR IMPACTO SISTÉMICO, NÃO POR FACILIDADE VISUAL

| # | causa | porque está aqui |
|---|---|---|
| 1 | **CR-1** cadeia cortada | enquanto não houver ligação, todas as outras oito são melhorias num sistema que não entrega |
| 2 | **CR-2** fronteira sem o outro lado | é a definição de «fechar a Collection» |
| 3 | **CR-8** dívida de procedência | CR-2 pode ficar pronta e continuar vazia por causa desta |
| 4 | **CR-5** ledger cego | sem isto nenhuma das correcções acima se prova em produção |
| 5 | **CR-6** rota com vários donos | cada correcção de CR-1 aterra hoje em três sítios |
| 6 | **CR-3** camadas sem gerador | é o portal, e o portal só importa depois de haver o que mostrar |
| 7 | **CR-7** atlas por abrir | aumenta o alcance, não desbloqueia nada |
| 8 | **CR-4** cards sem contrato | quatro perguntas por escrever; barato e não bloqueia |
| 9 | **CR-9** declarado e não chamado | limpeza de verdade, não de código |

O portal está em sexto **de propósito**. Consertá-lo primeiro daria a aparência
de um sistema a funcionar sobre uma cadeia que continua cortada — e é
exactamente o defeito que este censo existe para não repetir.

---

## 10 · A PHASE 11 É NECESSÁRIA ANTES DE FECHAR A COLLECTION?

```
PHASE11_REQUIRED_BEFORE_COLLECTION_CLOSE = NO
```

A Phase 11 é a **retirada da coluna `raw_asset.storage_path`**. A pergunta é se
ela bloqueia o fecho da Collection. Medido:

1. **O endereço já não é identidade.** A migration 027 está aplicada no banco
   canónico: `UNIQUE(storage_path)` caiu, a chave da tentativa existe com
   `NULLS NOT DISTINCT`, e sete campos de identidade são imutáveis por trigger.
   `provas/auditoria_live.sh` secção G cobra esse contrato a cada corrida.
2. **Nenhum escritor vivo a usa como chave.** O inventário fechado em
   `tests/test_porta_de_producao.py` tem três ficheiros a falar de `raw_asset`:
   `preservar_coleta.py` (ESCREVE), `catalogo_importar.py` (GERA),
   `memoria_descartavel.py` (LÊ). No escritor, `storage_path` é coluna de carga
   e não chave — a busca é por `storage_object_id`.
3. **Nenhum leitor devolve «a primeira linha do endereço».**
   `tests/test_leitores_depois_da_fase_10.py` prova-o numa bancada com uma cópia
   e duas observações.
4. **O único SQL que ainda trata o endereço como chave está morto.**
   `catalogo_importar.py` emite `on conflict (storage_path) do nothing` e um
   `select id from raw_asset where storage_path=...`. Esse SQL **não se aplica a
   banco nenhum desde a 026**: falha na primeira linha, em `identity_state` NOT
   NULL. O ficheiro gerado é registo histórico do que foi importado, não uma
   capacidade.

**Logo a coluna é hoje peso morto, não risco activo.** Nenhuma das nove
causas-raiz depende de a retirar, e nenhuma delas fica mais fácil com ela
retirada.

### O limite desta resposta, dito em voz alta

O escritor forward **nunca escreveu no banco vivo**: 252 linhas legadas, zero
forward. A prova de que ele não usa o endereço como chave é prova do **código** e
da bancada local, não de tráfego de produção. Se o primeiro `forward` real
mostrar outra coisa, esta resposta muda — e o sentinela
`COLUNA_STORAGE_PATH_AINDA_EXISTE`, já na auditoria viva, é quem a irá cobrar.

---

## 11 · O QUE ESTE CENSO **NÃO** RESPONDE

- **Que sensor alimenta que card.** Não há uma única aresta card→sensor no
  sistema. A corrente parte na camada do portal (CR-3), e desenhar a seta na
  mesma seria inventá-la.
- **Se os 144 registos do ledger vieram de algum dos 58 sensores.** O ledger não
  guarda o executor (CR-5). `UNKNOWN` não vira facto.
- **Quanto do que os cards mostram é real.** Seis dos onze misturam sem dizer
  qual é qual; o censo diz que misturam, não em que proporção.
