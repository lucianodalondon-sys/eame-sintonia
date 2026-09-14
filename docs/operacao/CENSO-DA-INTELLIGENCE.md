# CENSO DA INTELLIGENCE — o retrato de hoje

> ## ⚠️ CORRIGIDO EM 13/09/2026 — TRÊS ACHADOS DESTE DOCUMENTO ESTÃO ERRADOS
>
> Este documento foi medido em `main`/`claude/funny-hypatia-y7ho5s`, que está
> **268 commits atrás** da linha funcional da Collection. A missão `C-ADM-I01`
> remediu na linha funcional (`claude/raw-observation-identity-3jbwco` @
> `247fbf25`, onde `admissao/admissao.py` tem **356 linhas a mais**) e provou
> que o seguinte é **FALSO ali**:
>
> | o que este documento diz | o que a linha funcional mede |
> |---|---|
> | «INTERSECÇÃO DE CHAVES = VAZIA» | **falso** — `IDENTIDADE_DA_FONTE` lê `SOURCE_ID`; a pergunta «origem» responde **SIM** |
> | «ADMISSÕES CONCEDIDAS = 0» | **falso** — o livro tem **36 SIM**, e o recall da porta dá **42/49 (85,7%)** |
> | «`RAW_OBSERVATION_ID` não existe» | **falso** — `RAW_OBSERVATION_ID = raw_asset.id`, migration `027`, produzido por `guarda/preservar_coleta.observacoes_confirmadas()` |
>
> As 506 decisões com `item = "?"` são resíduo da **regra versão 1** (corridas
> `XX-*`). Nas versões 2 e 3 há 307 decisões, e **as 36 SIM têm identidade real**.
>
> A porta fala minúsculas **por desenho**: quem traduz é
> `coleta/ingresso.py::para_a_porta()`, o dono único do vocabulário. Medir o
> ledger contra a porta *sem* passar pelo tradutor — que foi o que este
> documento fez — não mede a estrada, mede um atalho que não existe.
>
> **O que continua verdadeiro:** a Intelligence não consome nada, e o contrato
> `PRONTO_PARA_INTELIGENCIA` não carrega as referências de identidade. Mas isso
> **não é um defeito**: é `G-READY-02`, uma decisão em aberto e deliberadamente
> não tomada — ver `provas/a_sala_de_espera_nao_tem_morada.py` na linha funcional.


> Medido em 13/09/2026, na branch `claude/funny-hypatia-y7ho5s` @ `9dc23c61`
> (`main` @ `f437ff11`). Nenhum número aqui veio de memória, de handoff antigo
> ou de nome de ficheiro. Cada linha diz o comando que a produziu.
>
> **Esta é uma fotografia medida, não uma fonte de verdade.** Ela não decide
> nada, não promove nada a canónico e não substitui autoridade nenhuma. Quando
> divergir do repositório, é ela que está errada — remeça-se a medição.

Segue o precedente de [`CENSO-DA-COLETA.md`](CENSO-DA-COLETA.md).

---

## A · A RESPOSTA EM UMA FRASE

**O SINTONIA possui um motor de Intelligence grande, testado ao nível da regra e
inteiramente parado: 70 ficheiros de código que importam, 0 executados por
automação nenhuma, alimentados por uma pasta que não existe nesta árvore, e
servindo um portal a partir de um artefacto gerado numa branch que nunca foi
integrada.**

---

## B · VEREDITO

```text
CENTRAL_ENGINE            = PARTIAL   (existe, tem ordem escrita, e recusa correr aqui)
INTELLIGENCE_MATURITY     = FRAGMENTED
COLLECTION → INTELLIGENCE = DESLIGADO  (medido, não inferido)
```

**FRAGMENTED**, e não `FOUNDATION_ONLY` nem `PARTIALLY_INTEGRATED`, por três
medições que puxam em direções opostas:

- é mais que fundação — há 40 motores escritos, uma cadeia com ordem
  justificada passo a passo, 17 suites de teste verdes e um artefacto real a ser
  servido ao cliente;
- é menos que parcialmente integrado — **nenhuma automação corre um único
  motor**, e a fronteira `COLETA → INTELIGÊNCIA` não tem um só consumidor;
- e o que o portal mostra hoje **não foi produzido por esta árvore**.

---

## C · O ESTADO GIT

```text
CURRENT_BRANCH  claude/funny-hypatia-y7ho5s
CURRENT_HEAD    9dc23c613fafe97dd68749e3782766d42bd11709
MAIN_HEAD       f437ff1140fa97484ca9695b341fbe9ca0a9f050
WORKTREE_STATE  limpo
REMOTE_STATE    206 branches remotas
```

**Duas linhas concorrentes estavam a mexer enquanto este censo corria**, e isso
fica registado em vez de resolvido em silêncio:

| linha | o que mudou durante a missão |
|---|---|
| `claude/sintonia-eame-know-how-v1` | `cc874c0b → 4f681db3`, 4 commits novos |
| `research/intelligence-bible-engineering-v1` | branch nova, 4 commits, descende de `9dc23c61` |

---

## D · O INVENTÁRIO

```text
codigo de Intelligence na arvore    70 ficheiros
  motor/                            38     leis/          10
  pacote/                           17     portoes/        2
  superficie/                        4     provas/         9

importam sem erro                   66 / 68 modulos python
tem chamador (import, cadeia, CI)   37
sem chamador nenhum                 26
CORRIDOS POR AUTOMACAO               0
```

| Capability | Family | Code | Wired | Ran | Proven | Input | Output | Consumer | Status |
|---|---|---|---|---|---|---|---|---|---|
| Cadeia V2.1 (orquestrador) | Motor | YES | YES | **NO** | NO | `build/…/DESIGN-INGEST` | pacote V2.1 | — | `CODE_PRESENT` · recusa correr |
| Ingestão V2.1 (A/B/C) | Motor | YES | YES | NOT_RUN | NO | `data/samples` + handoff V2 | DESIGN-INGEST | cadeia | `CODE_PRESENT` |
| Crossings | Crossing | YES | YES | NOT_RUN | PARTIAL | DESIGN-INGEST | crossings | cadeia | `CODE_PRESENT` |
| Motor de Oportunidade | Scorer | YES | YES | NOT_RUN | **YES (regra)** | DESIGN-INGEST | oportunidades | cadeia | `CODE_PRESENT` |
| Leitura comercial | Scorer | YES | YES | NOT_RUN | **YES (regra)** | pacote | prioridade | cadeia | `CODE_PRESENT` |
| Completude da oportunidade | Analyzer | YES | YES | NOT_RUN | **YES (regra)** | DESIGN-INGEST | completude | cadeia | `CODE_PRESENT` |
| Réguas V2.1 (procedência, geografia, tempo) | Rule | YES | YES | NOT_RUN | **YES** | pacote | carimbos | cadeia | `CODE_PRESENT` |
| Relevância ADAMA | Rule | YES | YES | NOT_RUN | **YES** | pacote | relevância | `it_casa_dados` | `CODE_PRESENT` |
| Ingestão no site | Orchestrator | YES | YES | NOT_RUN | NO | DESIGN-INGEST | `italy-handoff-v21.js` | portal | `CODE_PRESENT` |
| Dados da casa | Aggregator | YES | YES | NOT_RUN | NO | cliente + upstream | `italy-casa.js` + 3 | portal | `CODE_PRESENT` |
| Snapshot da reunião | Snapshot | YES | **NO** | NOT_RUN | NO | pacote | `meeting-intelligence-*` | portal | `ORPHAN` (sem chamador) |
| Cadeia V2 (legado) | Motor | YES | NO | NO | NO | — | — | — | `HISTORICAL` (7 ficheiros) |
| Last-mile (4 peças) | Report | YES | NO | NOT_RUN | NO | pacote | relatórios | — | `ORPHAN` |
| Label Intelligence | — | **NO** | — | — | — | — | — | — | **`ABSENT`** (ver H) |
| Collection Gap | — | **NO** | — | — | — | — | — | — | **`ABSENT`** (0 ocorrências) |

---

## E · O MOTOR CENTRAL

```text
CENTRAL_ENGINE = PARTIAL
```

**Existe um orquestrador**: `motor/v21_cadeia.sh`, com 15 etapas e a razão de
cada ordem escrita ao lado dela. É conhecimento real e raro.

**E ele recusa-se a correr.** Medido:

```bash
$ bash motor/v21_cadeia.sh
  CADEIA RECUSADA NESTA LINHAGEM.
  Esta branch e CONSUMIDORA da inteligencia, nao geradora.
  Gerador canonico : claude/opportunity-commercial-priority-v1 @ 55c2674
```

Não é avaria: é uma trava deliberada, e está certa. Corrida aqui, a cadeia
produziria `V21-5d312cb90a0de01d` — uma safra que o próprio contrato lista como
velha.

**A trava tem uma contradição medida.** Duas autoridades nomeiam geradores
diferentes:

| autoridade | gerador que nomeia |
|---|---|
| `motor/v21_cadeia.sh` | `claude/opportunity-commercial-priority-v1 @ 55c2674` |
| `italia-portale/audit/CANONICAL-PACKAGE-CONTRACT.json` | `claude/acervo-to-package-intelligence-v1 @ 51010733` |

E o contrato classifica a safra de `55c2674` (`V21-69bf448ac934a6d9`) como
**STALE**. Ou seja: **a cadeia manda ir buscar o gerador a uma linhagem que o
contrato já aposentou.** Quem manda fica **indeterminado** até alguém arbitrar.

**Segundo bloqueio, independente do primeiro:** a pasta de entrada de toda a
cadeia — `build/ITALY-REALITY-HANDOFF-V2.1/` — **não existe nesta árvore**, e
está no `.gitignore` (linha 49). Ela vive apenas dentro de
`build/SINTONIA-ITALY-REALITY-HANDOFF-V2.1.zip` (32 entradas `DESIGN-INGEST/`).
O portão da build confirma-o sozinho:

```text
PASS  PACOTE_LOCAL_NAO_E_SAFRA_VELHA   o pacote no disco, se houver, e o canonico  [AUSENTE]
```

---

## F · O INPUT REAL — a Intelligence lê a Sala de Espera?

```text
NAO. MEDIDO, NAO INFERIDO.
```

| mecanismo | INPUT_DECLARED | INPUT_OBSERVED |
|---|---|---|
| `motor/v21_ingest.py` | — | `data/samples/IT-LASTMILE`, `IT-ISTAT-COLTIVAZIONI`, `build/ITALY-REALITY-HANDOFF-V2/PREVIOUS-HANDOFF` |
| `motor/v21_crossings.py` | — | `build/ITALY-REALITY-HANDOFF-V2.1/DESIGN-INGEST` |
| `motor/v21_oportunidades.py` | — | `build/…/DESIGN-INGEST` |
| `portoes/site_v21_ingest.py` | — | `build/…/DESIGN-INGEST` |

**Nenhum motor lê `guarda/` (a Sala de Espera), `data/collection-store` ou
`data/collection-ledger`.** Quem lê esses é só a Coleta:

```text
data/collection-store   -> coleta/italy_pilot_collect.mjs, coleta/italy_recurrent_collect.mjs
data/collection-ledger  -> coleta/, regras/, medidas/, provas/, system-map/
```

### E o pior detalhe: `PRONTO_PARA_INTELIGENCIA` é escrito e nunca lido

`admissao/admissao.py:242` emite `ESTADO: PRONTO_PARA_INTELIGENCIA`. A varredura
de todo o repositório encontra o termo em cinco sítios — e **os cinco são da
Coleta**:

```text
admissao/admissao.py           quem emite
pedido/pedido.py               o vocabulario
pedido/orquestrador.py         quem carimba o recibo
provas/testa_coleta_canonica.py  o teste que fecha o caminho DA COLETA
system-map/…declared.json      a descricao da peca
```

```text
CONSUMIDORES NA INTELIGENCIA: ZERO.
```

A fronteira canónica da missão (`COLLECTION → SALA DE ESPERA → INTELLIGENCE`)
**não está implementada**. A Coleta chega a READY; a Intelligence começa noutro
sítio. São duas ilhas.

---

## G · O OUTPUT REAL

O que é servido ao portal, e quem o produz:

| artefacto | produtor no repo | classificação |
|---|---|---|
| `italy-handoff-v21.js` (8,3 MB) | `portoes/site_v21_ingest.py` | `REPRODUCIBLE_GENERATED` — mas só na linhagem geradora |
| `italy-app-model.js` | `portoes/site_v21_ingest.py` | `REPRODUCIBLE_GENERATED` |
| `italy-casa.js`, `adama-relevance.js` | `superficie/it_casa_dados.py` | `REPRODUCIBLE_GENERATED` |
| `meeting-intelligence-snapshot.{js,json}` | `pacote/meeting_snapshot.py` | `REPRODUCIBLE_GENERATED` · produtor **sem chamador** |
| `italy-real-intelligence.js` | **nenhum** | `STATIC_SNAPSHOT_WITHOUT_PRODUCER` |
| `italy-market-pulse.js` | **nenhum** | `STATIC_SNAPSHOT_WITHOUT_PRODUCER` |
| `italy-science-business.js` | **nenhum** | `STATIC_SNAPSHOT_WITHOUT_PRODUCER` |
| `italy-label-verdicts.js` | **nenhum** | `MANUAL` (ver H) |
| `italy-briefs.js`, `italy-catalog.js`, `italy-canonical-windows.js`, `italy-ingested.js` | **nenhum** | `STATIC_SNAPSHOT_WITHOUT_PRODUCER` |
| `italy-v21.js` (10,3 MB) | `italia-portale/audit/build-v21.mjs` | **`ORPHAN`** — nenhuma página o carrega |

**8 dos 14 ficheiros de dado do portal não têm produtor no repositório.**

`italy-v21.js` é o maior ficheiro do cliente, carrega `V21-843baf4229d93598`
(`BUILT_AT 2026-09-02` — uma safra que não está no contrato nem na lista de
safras velhas conhecidas) e **não é carregado por `portale.html`, `casa.html`,
`index.html` nem `accesso.html`**. São 10,3 MB de safra desconhecida servidos e
nunca lidos.

---

## H · CROSSINGS · SIGNALS · FINDINGS · LABEL · COLLECTION GAP

| conceito | tem definição? | tem produtor? | tem store? | tem owner? | veredito |
|---|---|---|---|---|---|
| **CROSSING** | SIM | `motor/v21_crossings.py` | DESIGN-INGEST | SIM | conceito real, 8 invariantes provadas antes de emitir |
| **SIGNAL** | não | — | — | não | **nome de campo**, não conceito: `SIGNALS`, `SIGNAL_DATE`, `FIELD_SIGNAL` dentro dos registos |
| **FINDING** | não | — | — | não | **nome de campo**: existe só como `RED_TEAM_FINDINGS` dentro do motor de oportunidade |
| **COLLECTION GAP** | não | não | não | não | **`ABSENT`** — 0 ocorrências em todo o código |
| **LACUNA** | sim | `pacote/lastmile_*` | — | sim | é «o que ficou de fora de um briefing», **não** é collection gap |

`ONE CONCEPT → ONE OWNER` não é violado aqui: `SIGNAL` e `FINDING` simplesmente
**não são conceitos** neste repositório. Tratá-los como se fossem seria inventar
uma camada que ninguém construiu.

### LABEL INTELLIGENCE — a separação pedida

```text
LABEL DATA          EXISTE   data/samples/IT-ROTULOS/IT-ROTULOS-PARES.json (2,4 MB)
                             + IT-CENSO-DE-TERMOS.json — saída da COLETA
LABEL ANALYSIS      EXISTE   feita UMA vez, em 02/09/2026, por auditoria manual
                             de 163 rótulos oficiais italianos
LABEL INTELLIGENCE  ABSENTE  nenhum código recalcula, compara ou cruza veredictos
LABEL UI            EXISTE   italy-label-verdicts.js aplica a tabela congelada
```

O próprio ficheiro diz o que é, no cabeçalho:

> *«The presentation layer APPLIES these verdicts. It must never research, infer
> or promote a product relationship on its own.»*

**Isto é honesto e está certo como camada de apresentação.** Mas não é um
mecanismo: é um julgamento humano de um dia, congelado num ficheiro, sem
produtor que o refaça.

---

## I · O PORTAL — rastreamento reverso

`portale.html` carrega 18 scripts. A cadeia até ao mecanismo:

```text
CADEIA COMPLETA (produtor no repo, mas gerador fora desta linhagem)
  Radar delle Opportunità / Portafoglio / Concorrenza / Archivio
    -> window.ITALY_HANDOFF_V21  (italy-app-model.js + italy-handoff-v21.js)
       -> portoes/site_v21_ingest.py            [WIRED]
          -> build/…/DESIGN-INGEST              [AUSENTE nesta arvore]
             -> motor/v21_cadeia.sh             [RECUSA CORRER AQUI]

  Casa / relevância
    -> window.ITALY_CASA, window.ADAMA_RELEVANCE
       -> superficie/it_casa_dados.py           [WIRED]

CADEIA QUEBRADA (o ponto exato)
  Intelligence Scientifica  -> italy-science-business.js   -> ✗ SEM PRODUTOR
  Polso di Mercato          -> window.ITALY_MARKET         -> ✗ SEM PRODUTOR
  (sem nome no mapa)        -> italy-real-intelligence.js  -> ✗ SEM PRODUTOR
  Finestre Colturali        -> window.ITALY_CANONICAL      -> ✗ SEM PRODUTOR
  Archivio segnali          -> italy-ingested.js           -> ✗ SEM PRODUTOR
  verdictos de rótulo       -> window.ITALY_LABEL_VERDICTS -> ✗ MANUAL, 02/09
```

Estado das 11 ferramentas segundo o próprio System Map: **1 verde, 6 amarelas,
4 em NÃO SEI**.

> **UMA TELA CHAMADA «INTELLIGENCE SCIENTIFICA» NÃO É INTELLIGENCE.**
> `italy-science-business.js` é um ficheiro de dados de 19 KB que ninguém no
> repositório sabe reproduzir.

---

## J · ARQUEOLOGIA DE BRANCHES

**Nenhuma branch de Intelligence está integrada em `main`. Nenhuma.**

| branch | HEAD | à frente | atrás | merged |
|---|---|---|---|---|
| `claude/disease-local-collection-italy` | `39f51c93` | 401 | 97 | não |
| `claude/disease-intelligence-italy-overnight` | `a4d19ddf` | 337 | 97 | não |
| `claude/meeting-intelligence-integration` | `014b929c` | 281 | 97 | não |
| `claude/acervo-to-package-intelligence-v1` | `fb96f49d` | 242 | 97 | não |
| `claude/opportunity-commercial-priority-v1` | `9d783cec` | 227 | 97 | não |
| `claude/label-intelligence-v1-italy` | `6afba2ef` | 189 | 97 | não |
| `claude/visible-intelligence-v1` | `a4fb6d81` | 31 | 50 | não |
| `research/intelligence-bible-engineering-v1` | `7ae1b510` | 8 | 0 | não |

*(29 branches medidas; as 8 acima são as de maior massa.)*

### E o obstáculo que ninguém vê ao olhar para os commits

```text
main                                        motor/ = 38 ficheiros   scripts/ = 1
claude/acervo-to-package-intelligence-v1    motor/ =  0             scripts/ = 170
claude/opportunity-commercial-priority-v1   motor/ =  0             scripts/ = 162
claude/visible-intelligence-v1              motor/ =  0             scripts/ = 146
```

`main` **re-arrumou a prateleira inteira** (a lei das gavetas de `AGENTS.md`)
enquanto as linhagens que geram a Intelligence continuaram em `scripts/`. Entre
`main` e o gerador canónico há, ao mesmo tempo:

- ~150 ficheiros renomeados;
- 227 a 242 commits de lógica.

E o conteúdo também divergiu — não é só o caminho:

```text
main:motor/v21_oportunidades.py  vs  linhagem:scripts/v21_oportunidades.py
    +116  -1374     ← main tem 1374 linhas A MENOS
main:motor/v21_comercial.py       +92   -105
main:motor/v21_crossings.py        +3     -2
```

**A cópia do motor de oportunidade que vive em `main` é 1.374 linhas mais pobre
que a do gerador canónico.** Isto confirma, por medição independente, o aviso
que a própria cadeia escreve sobre si.

---

## K · DUPLICAÇÕES

| conceito | A | B | ancestral | consumidor de hoje | quem manda, medido |
|---|---|---|---|---|---|
| motor de oportunidade | `main:motor/v21_oportunidades.py` | `linhagem:scripts/v21_oportunidades.py` | `56fdb8ca` | o artefacto vem de B | **B**, por contrato |
| gerador canónico | cadeia diz `55c2674` | contrato diz `51010733` | — | o portão usa o contrato | **INDETERMINADO** — as duas autoridades discordam |
| cadeia | `motor/v21_cadeia.sh` (Intelligence) | `motor/cadeia_canonica.sh` (banco) | — | só a segunda corre no CI | não são a mesma coisa — nomes parecidos, domínios diferentes |
| pacote embarcado | `italy-handoff-v21.js` (canónico) | `italy-v21.js` (safra desconhecida) | — | só o primeiro é carregado | **A** |

---

## L · CÓDIGO SEM CHAMADOR

26 dos 63 módulos não têm chamador nenhum — nem import, nem cadeia, nem
workflow, nem teste:

```text
HISTORICAL   motor/v2_*.py (7)          a cadeia V2, marcada legado no mapa
ORPHAN       pacote/lastmile_*.py (4)   relatórios de última milha
ORPHAN       pacote/meeting_snapshot.py PRODUZ artefacto servido, e ninguém o chama
ORPHAN       motor/normalize_*.py (2)   motor/consolidar_leque.py, matriz_recorte.py
ORPHAN       leis/regua_italia.py       24 KB · leis/auditoria_regua_comercial.py 31 KB
BROKEN       pacote/v21_handoff_json.py caminho fixo `C:/eame-sintonia` — não corre em Linux
BROKEN       motor/v21_reavaliar_35.py  não importa: FileNotFoundError
```

**Nada foi apagado.** `motor/v21_tm_colher.py` também carrega um caminho de
Windows (`C:\Users\London1\AppData\Local`), mas com `os.environ.get` à frente —
degrada, não parte.

---

## M · PROVAS EXECUTADAS NESTA MISSÃO

```text
importacao de 68 modulos            66 OK · 2 FileNotFoundError
npm run build (portao da build)     PASS
    ARTEFACTO_SERVIDO_E_CANONICO    V21-06c6421d001ea52a
    PACOTE_LOCAL_NAO_E_SAFRA_VELHA  AUSENTE
bash motor/v21_cadeia.sh            RECUSADO (trava deliberada)
17 suites de teste de Intelligence  17 PASS · ~300 asserções
```

As 17 suites verdes provam **a regra**, não a cadeia: `test_prioridade_comercial`
e `test_completude_oportunidade` importam `v21_oportunidades`, `v21_comercial` e
`v21_necessidade` e exercitam-nos com fixtures próprias. **Nenhum teste corre um
motor de ponta a ponta por subprocesso.**

```text
PROVEN ao nivel da REGRA      SIM
OBSERVED ao nivel da CADEIA   NAO  (NOT_RUN — a entrada nao existe nesta arvore)
```

### NOT_RUN, e porquê

| não corrido | motivo |
|---|---|
| cadeia V2.1 completa | trava de linhagem + `DESIGN-INGEST` ausente; re-hidratar do ZIP produziria uma safra que o contrato recusa |
| `cadeia_canonica.sh` | exige `PSQL_URL` de um banco real — fora do read-only |
| qualquer coleta | custo externo |

---

## N · A BÍBLIA DE INTELLIGENCE

```text
INTELLIGENCE_BIBLE = FOUND_FRAGMENTS_ONLY  (a antiga, procurada por esta missão)
                   + FOUND_EXACT           (uma candidata NOVA, escrita hoje)
```

**A antiga** — `docs/biblia/BIBLIA-DA-INTELIGENCIA-EAME.md`, em
`claude/integration-acervo-portal-v1 @ 11d2c3dd`, 621 linhas. O cabeçalho recusa
o próprio título:

```text
CLASSIFICACAO           DRAFT · INVENTARIO_DE_LEIS · INPUT_TO_INTELLIGENCE_BIBLE
O_QUE_ELE_AINDA_NAO_E   a Biblia de Engenharia da Inteligencia
```

Um commit anterior (`256003a0`) chamava-lhe Bíblia; `11d2c3dd` corrigiu-se, com
a mensagem *«um inventario chamado de biblia»*. **A Bíblia de engenharia antiga
nunca existiu** — o que existe é o inventário das leis já aprendidas.

**A nova** — `BIBLIA-DE-ENGENHARIA-DA-INTELLIGENCE.md`, em
`research/intelligence-bible-engineering-v1 @ 7ae1b510`, **1.335 linhas, escrita
em 13/09/2026**, com benchmark (671 linhas) e red team (415 linhas) ao lado. Ela
carimba-se:

```text
VERSION = V0.2
STATUS = CANDIDATE_FOR_CANONICAL_REVIEW
IMPLEMENTATION_AUTHORIZED = NO
```

**Não foi promovida a canónica por este censo, e não deve ser por ninguém sem
revisão.** Ela própria diz porquê: `CONTROL_PLANE_ATOMICITY = FAIL`.

---

## O · SYSTEM MAP — o que bate e o que não

| | |
|---|---|
| `MAP_TRUE` | as 29 peças de Intelligence existem, com os ficheiros que o mapa cita |
| `MAP_TRUE` | `lineage_consumer` / `lineage_generator` / `lineage_stale` dizem exatamente o que medi |
| **delta** | `C-CADEIA-V21` é **verde** com o motivo *«algum workflow ou a cadeia canónica manda rodar isto»* |

O verde não é falso — no contrato do mapa, ele significa **WIRED** («alguém manda
correr isto»), e é verdade. Mas para uma peça de motor esse verde lê-se como
*«isto corre»*, e **não corre**: a cadeia recusa-se nesta linhagem e a entrada
dela não existe.

```text
O MAPA NAO TEM ESTADO PARA «LIGADO MAS IMPEDIDO DE CORRER AQUI».
```

Delta a registar (**não aplicado nesta missão**, que é read-only): distinguir
`WIRED` de `RAN` para peças do tipo motor/cadeia, ou dar-lhes um estado próprio
para «fenced». Enquanto não existir, um leitor honesto do mapa conclui que a
Intelligence está operacional.

### E um falso positivo do portão do Control Plane, encontrado por este censo

`controle/portao_do_controle.py` marca como `UNREGISTERED_CANONICAL_DOCUMENT`
qualquer `.md` que contenha um dos termos com que um documento se declara lei —
a lista vive em `SE_DIZ_LEI`, nesse mesmo ficheiro, e não é copiada para aqui:
uma lista em dois sítios diverge. A regra existe para apanhar um documento que
**se declara** lei.

Este censo tropeçou nela ao **citar** esses termos como dado medido, numa tabela.
O documento não reivindica nada — e mesmo assim o portão reprovou.

```text
O PORTAO PROCURA A PALAVRA, E NAO A INTENCAO.
```

Está certo assim: adivinhar intenção a partir de texto deixa passar uma lei a
mais e barra uma a menos. Mas falta-lhe uma espécie para **relatório de medição**,
que cita autoridades sem ser uma. Delta registado; **não aplicado aqui**, porque
mexer no portão é alterar código e esta missão é de leitura.

*(Contornado nesta entrega reescrevendo a tabela — o facto medido é o mesmo.)*

E a demonstração fecha-se sozinha: **a frase que explicava o falso positivo
provocava o falso positivo**, porque citava os termos. Foi preciso trocá-la por
um ponteiro para a lista real. O portão está certo; falta-lhe é a espécie.

---

## P · O QUE CONTINUA DESCONHECIDO

```text
NAO SEI  se a safra V21-843baf4229d93598 em italy-v21.js (10,3 MB) alguma vez foi
         servida, ou se nasceu orfa — nao esta em contrato nenhum
NAO SEI  qual das duas autoridades tem razao sobre o gerador canonico
NAO SEI  se os 8 ficheiros sem produtor tiveram produtor nalguma branch — medi
         que nao ha nenhum NESTA arvore, nao que nunca tenha havido
NAO SEI  o que ha de Intelligence util nas 21 branches de menor massa
NAO SEI  se a Biblia V0.2 de hoje descreve a maquina que existe ou a desejada
```

---

## Q · O MENOR BLOQUEIO ESTRUTURAL

Não é falta de motor. Não é falta de regra. Não é falta de teste.

```text
A INTELLIGENCE NAO TEM ENTRADA.
```

Duas coisas, e a segunda é consequência da primeira:

1. **`PRONTO_PARA_INTELIGENCIA` não tem um único leitor.** A Coleta termina; nada
   pega. Enquanto isso for verdade, qualquer motor novo terá de inventar a sua
   própria entrada — que é exatamente como nasceram os 8 ficheiros sem produtor.

2. **A entrada que os motores realmente esperam (`build/…/DESIGN-INGEST`) é uma
   pasta ignorada pelo git, produzida noutra linhagem.** Por isso a Intelligence
   só corre onde essa pasta existe, e essa não é a linha padrão.

> **O menor bloqueio estrutural é um contrato de entrada da Intelligence que leia
> a Sala de Espera.** Sem ele, integrar as branches só multiplica ilhas.

---

## R · O QUE ESTE CENSO NÃO FEZ

Nenhuma arquitetura nova, nenhuma Bíblia, nenhum refactor, nenhum merge, nenhum
ficheiro movido ou apagado, nenhum card criado à mão, nenhuma aresta inventada no
System Map, nenhuma alteração ao portal ou à Coleta.
