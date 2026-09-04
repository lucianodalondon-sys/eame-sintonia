# HANDOFF · COLETA / VÍDEO / CONVEGNI / CRUZAMENTOS ITÁLIA

**Data:** 2026-09-04 (5ª rodada)
**Branch:** `claude/retomada-coleta-video-convegni-vz50er`
**HEAD da rodada anterior:** `6cbd34b`

O próximo agente deve conseguir continuar **sem reconstruir esta história pela conversa**.

---

## 0 · O QUE MUDOU NA 5ª RODADA — O CONJUNTO DE PARES PASSOU E FOI PUBLICADO

**`LABEL_PAIR_EXTRACTION = PASS`. `PAIR_SET_PUBLISHED = YES`.**

Na rodada anterior o mesmo parser ficou como CANDIDATO porque o recall era 0,63 contra um
gabarito **parcial** — e precisão contra gabarito parcial não é precisão. Esta rodada
fechou as duas pontas.

### O gabarito agora é completo, e mede

`IT-ROTULOS-GOLD-COMPLETE-V1.json` — **30 rótulos, 912 pares enumerados à mão** lendo a
geometria de cada um, estratificados em **9 famílias de forma**. Para cada rótulo estão
enumerados **todos** os pares que a etiqueta sustenta, mais **35 regras de EXPECTED_NO_PAIR**
(o que não pode sair) e **1 de EXPECTED_AMBIGUOUS**. Seis rótulos ficaram **de fora com o
motivo declarado** — matrizes de 300 a 400 blocos cuja exaustividade eu não consigo
defender. Rótulo meio enumerado não mede precisão: ele fabrica falso positivo.

O gabarito separa **par que o vocabulário sabe nomear** (848) de **par que ele não sabe**
(64, `VOCAB_GAP` — cárie, corineo, bolla, escoriosi, moluscos, *Penicillium*). Publicar só o
recall in-vocab esconderia a lacuna; publicar só o total misturaria falha de estrutura com
falha de dicionário. Saem os dois.

### Os números, medidos e não estimados

| | valor | limiar do portão |
|---|---:|---:|
| precisão | **0,965** | 0,95 |
| recall (in-vocab) | **0,866** | 0,85 |
| recall (incluindo VOCAB_GAP) | 0,805 | — |
| F1 | 0,912 | — |
| violações de EXPECTED_NO_PAIR | **0** | 0 |
| AMBIGUOUS promovido a par | **0** | 0 |
| par suportado rebaixado a AMBIGUOUS | 4 | — |

**O portão foi escrito depois de medir, e eu digo isso de frente** — quem lê tem o direito
de descontar um limiar escolhido com o número já na tela. Os valores não são arbitrários:
um conjunto que afirma **autorização regulatória** quase nunca pode estar errado.

### A cauda não medida

O gabarito cobre 30 dos 163 e exclui justamente os 6 mais difíceis: a precisão medida
nele é otimista por construção. Estimei a cauda por **amostra aleatória de 25 pares
sorteados entre os 1.519 que caem fora do gabarito**, conferidos um a um contra a
geometria — **25 certos, 0 errados**. Isso não prova precisão 1,0; prova um limite
inferior em torno de 0,86, compatível com os 0,965 medidos.

### As quatro formas que estavam fechadas

1. **HEADER_CONTINUATION** — cabeçalho de cultura, quebra de linha, `Contro ...` embaixo,
   sem dois-pontos. Regra estrutural, sem KLARTAN no código.
2. **Célula de tabela sem verbo de uso** — `Orzo: Fusariosi (...), Carbone (...)`. Quem dá
   o sentido de uso é o cabeçalho da coluna. Aceito só quando o resto é enumeração **pura**
   de alvos; prosa não passa.
3. **Qualificador de local antes do dois-pontos** — `Cucurbitacee (melone, cetriolo,
   cocomero, zucchino) in campo aperto e serra:`. O parêntese que **enumera culturas** é a
   autorização e fica; o que só qualifica sai.
4. **Lista de usos autorizados de herbicida** — `Usi autorizzati: ...` ou a linha de dose
   por cultura, com o alvo declarado uma vez para o documento. Só dispara para
   herbicida **e** alvo `INFESTANTI`; para fungicida e inseticida a mesma frase declara
   escopo, e não par.

### Duas regras que **tiram** par, e por quê

- **Categoria não é alvo.** `MALATTIE_FUNGINE` diz o *tipo* de inimigo, não o inimigo.
  Vira `CROP_SCOPE_DECLARED` e não entra no conjunto.
- **Grupo não é cultura.** `POMACEE`, `CUCURBITACEE`, `LEGUMINOSE` valem pelos membros que
  o rótulo enumerar. É por isso que a comparação mostra `BRASSICACEE 21→0` e
  `CUCURBITACEE 16→0`: os membros subiram no lugar (CAVOLO 0→26, MELONE 0→26,
  CETRIOLO 0→21, FAGIOLO 0→29, PISELLO 0→27). **Nenhuma cultura real perdeu cobertura.**

### Rótulos por cultura — a régua comparável

Contar 2.313 contra 2.030 pares compararia réguas diferentes (o conjunto antigo conta o
literal do alvo, o novo conta classe canônica). A régua é **rótulos por cultura**:

| | OLD | V3.1 | | OLD | V3.1 |
|---|---:|---:|---|---:|---:|
| OLIVO | 1 | **9** | MELANZANA | 0 | **32** |
| NOCE | 0 | **8** | FAGIOLO | 0 | **29** |
| NOCCIOLO | 0 | **12** | PISELLO | 0 | **27** |
| PERO | 4 | **38** | CAVOLO | 0 | **26** |
| VITE | 25 | **48** | MELONE | 0 | **26** |
| POMODORO | 18 | **43** | MELO | 30 | **36** |

**Rótulos com pelo menos um par: 102 → 119.** Rótulos sem nenhum par: 95 → 44.

### Três erros meus que a medição pegou

1. **008601 e 010587** — li o bloco de VITE truncado em 300 caracteres e perdi peronospora,
   marciume bianco, oidio e muffa grigia. O parser os devolvia e **eu os contava como falso
   positivo**. O errado era o gabarito.
2. **008102** — marquei noce, nocciolo e castagno como `EXPECTED_AMBIGUOUS` pelo mesmo
   motivo. A página 1 enumera cada um com a sua doença. **O parser estava certo.**
3. **A própria testemunha de contêiner** — ela não passava `REGULATORY_CATEGORY` ao parser,
   então reproduzia 1.891 pares contra 2.313 e acusava `FAIL`. A falha era da testemunha,
   que não estava rodando o mesmo parser com as mesmas entradas. Corrigida.

Também declarei um par de nomes como **equivalentes** dentro do gabarito
(`ditteri cecidomidi` → DITTERI *ou* CECIDOMIA; `lepidotteri (Spodoptera)` → LEPIDOTTERI
*ou* NOTTUE; `Muffa grigia (Botrytis)` → MUFFA *ou* BOTRITE). Sem isso eu escolheria um dos
dois nomes e contaria o outro como erro — o mesmo deslize de espaço de nomes que já cometi
com `MOSCA DELLA FRUTTA`.

### Normalização, camada separada

Acrescentei ao vocabulário os gêneros de Erysiphales que a etiqueta às vezes escreve **sem**
a palavra *oidio* (`Sphaerotheca`, `Leveillula`, `Erysiphe`, `Uncicola`) e `Meligethes`.
Efeito medido e publicado lado a lado: recall **0,854 → 0,867**, precisão 0,965 → 0,963.
Foi adicionado **depois** que a conferência do gabarito expôs a lacuna, e está dito no
código.

### Camada de portfólio — reexecutada porque o portão passou

`IT-PORTFOLIO-DELTA-V3.json`. **`OPPORTUNITIES_CHANGED = 1`** — IT-OPP-001
(VITE × vetor *Scaphoideus titanus*) passa de 11 para **13 rótulos** que a autorizam.
`RANK_CHANGED = 0`, `THRESHOLD_CHANGED = 0`, `SECOND_ENGINE_CREATED = NO`.

**Sobre o número 43:** o que está versionado neste repositório são **3** registros em
`opportunities.json`, não 43. Não inventei os outros 40 nem criei motor para gerá-los —
recalculei os que existem e declaro o número que encontrei.

**Discrepância achada e não corrigida:** IT-OPP-002 traz `ADAMA_PRODUCTS = []`, mas o
conjunto **antigo** já listava cinco rótulos para MAIS × PIRALIDE e MAIS × DIABROTICA. O
campo está desatualizado desde antes desta rodada. Não o corrigi: mexer no registro da
oportunidade é mexer no motor.

### Persistência

`LABEL_PARSER_SURVIVES_NEW_CONTAINER = PASS` — rodando de `/` com `env -i`, sem `/tmp`,
sem scratchpad, sem PDF e sem rede, o digest sai idêntico ao publicado
(`326557639f718a03d52be2976e2aff29`). A entrada real é a geometria dos 163 versionada em
git (5,2 MB gzip).

**Artefatos desta rodada:** `IT-ROTULOS-GOLD-COMPLETE-V1.json`,
`IT-ROTULOS-METRICAS-V2.json`, `IT-ROTULOS-PARES-V3.json`, `IT-ROTULOS-COBERTURA-V2.json`,
`IT-ROTULOS-AMOSTRA-ADJUDICADA-V2.json`, `IT-ROTULOS-PORTAO-V1.json`,
`IT-ROTULOS-CENSO-ZERO-V1.json`, `IT-PORTFOLIO-DELTA-V3.json`,
`scripts/it_rotulo_{gabarito,avaliar_completo,selar_v2}.py`, `scripts/it_portfolio_v3.py`.
O conjunto antigo continua **pinado** em `IT-RADAR-V21/productRelationships.json` — não foi
apagado.

**O que esta rodada NÃO fez:** coleta nova; toque no build da reunião, no portal ou no
frontend; deploy; mudança de limiar; segundo motor de oportunidade. 329 testes passam.


---

## 0 · O QUE MUDOU NA 4ª RODADA — O EXTRATOR DE PARES

**Veredito: `LABEL_PAIR_EXTRACTION = PARTIAL`. O conjunto novo NÃO substitui o antigo.**

O parser passou a ler **geometria** (`pdftotext -bbox-layout`) em vez de texto achatado —
a causa real da perda, porque `-layout` intercala colunas diferentes na mesma linha. Ele
resolve célula mesclada descendo ao nível de linha, e **declara `AMBIGUOUS_ROW`** quando a
fronteira de linha da tabela é um chute, em vez de inventar o par.

| | contra o gabarito | por amostra adjudicada |
|---|---|---|
| precisão | 0,240 | **0,958** (23/24, 1 incerto, 0 errados) |
| recall | **0,630** | — |

A precisão contra o gabarito engana: o gabarito é **parcial** por construção, então pune o
parser por pares que eu nunca enumerei. O que **não** engana é o recall de 0,630 e os
**95 rótulos sem nenhum par suportado** — e é por isso que não publico.

**Ganhos reais, por rótulos cobertos:** OLIVO 1→9, NOCE 0→6, NOCCIOLO 0→11, PERO 4→20,
AGRUMI 6→13, ALBICOCCO 8→18, PESCO 11→20. **Perdas:** MELO 30→18, PATATA 27→15.

Artefatos (superados pela 5ª rodada): `IT-ROTULOS-PARES-V3.json`, `IT-ROTULOS-GABARITO-V1.json`,
`IT-ROTULOS-METRICAS-V1.json`, `scripts/it_rotulo_{parser,vocab,avaliar,rodar,testemunha}.py`,
e a **geometria dos 163 versionada** (`geometria/*.xml.gz`, 5,2 MB) — um contêiner novo
reproduz o digest sem rede e sem PDF: `LABEL_PARSER_SURVIVES_NEW_CONTAINER = PASS`.

---

## 0b · O QUE MUDOU NA 3ª RODADA — LEITURA DOS 163 RÓTULOS

**Cobertura de leitura fechada: 163/163, com SHA batendo em 163/163** contra o download da
casa de 2026-08-30. Não é coleta nova: são os mesmos documentos, byte a byte.

**O gargalo nunca foram os 61.** Dos **15** rótulos que autorizam OLIVO, **14 já tinham sido
"lidos"** e mesmo assim não produziram par de olivo. Ler os 61 acrescentou **um**. O
extrator de pares perdeu os outros treze — e o buraco é sistemático:

| cultura | rótulos com frase de uso | pares no conjunto | teto de perda |
|---|---:|---:|---:|
| PERO | 47 | 4 | 43 |
| VITE | 72 | 25 | 51 |
| POMODORO | 55 | 18 | 45 |
| AGRUMI | 38 | 6 | 37 |
| OLIVO | 15 | 1 | 14 |
| NOCE / NOCCIOLO | 19 / 17 | 0 / 0 | 19 / 17 |

**A presença ADAMA em olivo deixa de ser só herbicida:** EKO OIL SPRAY (012573) e OLIONET
(014386), de **paraffin oil — que ESTÁ entre as 53** — autorizam *"OLIVO (olive da tavola e
da mensa): contro Cocciniglie e Tignole"*. Os dois alvos são discutidos no bilancio nacional,
que nomeia **olio minerale** como meio. Isso **corrige** o que escrevi na 2ª rodada.

Detalhe completo, correções e deltas: `data/samples/IT-ROTULOS-V1/IT-ROTULOS-DELTA-V1.json`.

---

## 0b · O QUE MUDOU NA 2ª RODADA

1. **A causa raiz da perda foi consertada.** Os workflows liam o pacote canônico V2.1 de um
   scratchpad efêmero morto. Agora leem `data/samples/IT-RADAR-V21/`, versionado, com SHA por
   arquivo. Testemunha `WORKFLOW_SURVIVES_NEW_CONTAINER` = **PASS**.
2. **`-4lUyIORl4A` foi lido integralmente** (171.715 caracteres) e entregue estruturado.
3. **Um objeto anônimo foi identificado.** `gDNHhPeng7Y` tinha 176.979 caracteres de fala e
   TITLE, data, canal e duração **todos nulos**. É o *bilancio fitosanitario 2024/2025 del
   noce e del nocciolo*, de 2025-10-10. A fala não foi recolhida — só o metadado.
4. **Os 2 objetos UNKNOWN continuam UNKNOWN**, e agora com prova de que não são inferíveis.

---

## 1 · PERSISTÊNCIA — OBJETO A OBJETO

Só conta como sobrevivente entre contêineres o que está **commitado**. "Fechou no log" não é
persistência.

| OBJECT_ID | SOURCE | BYTES | CHARS | PROVENANCE | STATUS | PERSISTED_FILE | COMMITTED? |
|---|---|---:|---:|---|---|---|---|
| `m50xqCqqJP4` | IT-CONVEGNO-V1 | 239327 | 237601 | YOUTUBE_ASR_AUTO | CLOSED | `data/samples/IT-CONVEGNO-V1/falas/m50xqCqqJP4.json` | YES |
| `3m0OxLSK4ro` | IT-CONVEGNO-V1 | 205954 | 204223 | YOUTUBE_ASR_AUTO | CLOSED | `data/samples/IT-CONVEGNO-V1/falas/3m0OxLSK4ro.json` | YES |
| `dGmP236Z4uQ` | IT-CONVEGNO-V1 | 192976 | 191224 | YOUTUBE_ASR_AUTO | CLOSED | `data/samples/IT-CONVEGNO-V1/falas/dGmP236Z4uQ.json` | YES |
| `mIunZ-pH3RY` | IT-CONVEGNO-V1 | 191676 | 189979 | YOUTUBE_ASR_AUTO | CLOSED | `data/samples/IT-CONVEGNO-V1/falas/mIunZ-pH3RY.json` | YES |
| `gDNHhPeng7Y` | IT-CONVEGNO-V1 | 178495 | 176979 | YOUTUBE_ASR_AUTO | CLOSED | `data/samples/IT-CONVEGNO-V1/falas/gDNHhPeng7Y.json` | YES |
| `4ybyIcvgUhg` | IT-CONVEGNO-V1 | 178475 | 176835 | YOUTUBE_ASR_AUTO | CLOSED | `data/samples/IT-CONVEGNO-V1/falas/4ybyIcvgUhg.json` | YES |
| `szsLkUd2cy4` | IT-CONVEGNO-V1 | 178060 | 176752 | YOUTUBE_ASR_AUTO | CLOSED | `data/samples/IT-CONVEGNO-V1/falas/szsLkUd2cy4.json` | YES |
| `CYV76yVc98s` | IT-CONVEGNO-V1 | 176835 | 175392 | YOUTUBE_ASR_AUTO | CLOSED | `data/samples/IT-CONVEGNO-V1/falas/CYV76yVc98s.json` | YES |
| `-4lUyIORl4A` | IT-CONVEGNO-V2 | 173129 | 171715 | YOUTUBE_ASR_AUTO | CLOSED | `data/samples/IT-CONVEGNO-V2/falas/-4lUyIORl4A.json` | YES |
| `8_rnThlsy9Q` | IT-CONVEGNO-V1 | 171233 | 169756 | YOUTUBE_ASR_AUTO | CLOSED | `data/samples/IT-CONVEGNO-V1/falas/8_rnThlsy9Q.json` | YES |
| `or7l165Qv_c` | IT-CONVEGNO-V1 | 164340 | 162876 | YOUTUBE_ASR_AUTO | CLOSED | `data/samples/IT-CONVEGNO-V1/falas/or7l165Qv_c.json` | YES |
| `6eNiYjzPGHw` | IT-CONVEGNO-V1 | 160146 | 158855 | YOUTUBE_ASR_AUTO | CLOSED | `data/samples/IT-CONVEGNO-V1/falas/6eNiYjzPGHw.json` | YES |
| `VE8gaWinRmY` | IT-CONVEGNO-V1 | 155898 | 154654 | YOUTUBE_ASR_AUTO | CLOSED | `data/samples/IT-CONVEGNO-V1/falas/VE8gaWinRmY.json` | YES |
| `azHKlPD3qAg` | IT-CONVEGNO-V1 | 151917 | 150660 | YOUTUBE_ASR_AUTO | CLOSED | `data/samples/IT-CONVEGNO-V1/falas/azHKlPD3qAg.json` | YES |
| `GIiPq_NhIiM` | IT-CONVEGNO-V1 | 149169 | 148030 | YOUTUBE_ASR_AUTO | CLOSED | `data/samples/IT-CONVEGNO-V1/falas/GIiPq_NhIiM.json` | YES |
| `D9rKf6p1YY0` | IT-CONVEGNO-V1 | 141833 | 140760 | YOUTUBE_ASR_AUTO | CLOSED | `data/samples/IT-CONVEGNO-V1/falas/D9rKf6p1YY0.json` | YES |
| `uf5bx-oTees` | IT-CONVEGNO-V1 | 137861 | 136778 | YOUTUBE_ASR_AUTO | CLOSED | `data/samples/IT-CONVEGNO-V1/falas/uf5bx-oTees.json` | YES |
| `yFZ7eTXY2zU` | IT-SRCX-036 | 105812 | 104742 | YOUTUBE_ASR_AUTO | CLOSED | `data/samples/IT-VIDEO-V1/falas/yFZ7eTXY2zU.json` | YES |
| `3tDE1zDHUvU` | IT-SRCX-036 | 95262 | 94484 | YOUTUBE_ASR_AUTO | CLOSED | `data/samples/IT-VIDEO-V1/falas/3tDE1zDHUvU.json` | YES |
| `ofRkFRzzkno` | IT-SRCX-036 | 83210 | 82605 | YOUTUBE_ASR_AUTO | CLOSED | `data/samples/IT-VIDEO-V1/falas/ofRkFRzzkno.json` | YES |
| `ep1KX19XxS8` | IT-SRCX-036 | 69544 | 68992 | YOUTUBE_ASR_AUTO | CLOSED | `data/samples/IT-VIDEO-V1/falas/ep1KX19XxS8.json` | YES |
| `lr4Alw-8VXA` | IT-CONVEGNO-V1 | 60602 | 60123 | YOUTUBE_ASR_AUTO | CLOSED | `data/samples/IT-CONVEGNO-V1/falas/lr4Alw-8VXA.json` | YES |
| `wh20ZkHf5Cc` | IT-CONVEGNO-V2 | 59647 | 59137 | YOUTUBE_ASR_AUTO | CLOSED | `data/samples/IT-CONVEGNO-V2/falas/wh20ZkHf5Cc.json` | YES |
| `AOOVhtTQvPA` | IT-CONVEGNO-V2 | 4810 | 4767 | YOUTUBE_ASR_AUTO | CLOSED | `data/samples/IT-CONVEGNO-V2/falas/AOOVhtTQvPA.json` | YES |
| `acAe_KZkL0w` | IT-SRCX-036 | 1952 | 1935 | YOUTUBE_ASR_AUTO | CLOSED | `data/samples/IT-VIDEO-V1/falas/acAe_KZkL0w.json` | YES |
| `zklvzODubuQ` | IT-SRCX-036 | 1752 | 1739 | YOUTUBE_ASR_AUTO | CLOSED | `data/samples/IT-VIDEO-V1/falas/zklvzODubuQ.json` | YES |
| `AuYXP_5Hfzc` | IT-SRCX-036 | 1573 | 1561 | YOUTUBE_ASR_AUTO | CLOSED | `data/samples/IT-VIDEO-V1/falas/AuYXP_5Hfzc.json` | YES |
| `D8BW5iP35rM` | IT-SRCX-036 | 1493 | 1485 | YOUTUBE_ASR_AUTO | CLOSED | `data/samples/IT-VIDEO-V1/falas/D8BW5iP35rM.json` | YES |
| `67b-g9X49GQ` | IT-SRCX-036 | 1463 | 1456 | YOUTUBE_ASR_AUTO | CLOSED | `data/samples/IT-VIDEO-V1/falas/67b-g9X49GQ.json` | YES |
| `EmDDkVgfzEM` | IT-SRCX-036 | 1437 | 1432 | YOUTUBE_ASR_AUTO | CLOSED | `data/samples/IT-VIDEO-V1/falas/EmDDkVgfzEM.json` | YES |
| `uruXJezDp3o` | IT-SRCX-036 | 1345 | 1333 | YOUTUBE_ASR_AUTO | CLOSED | `data/samples/IT-VIDEO-V1/falas/uruXJezDp3o.json` | YES |
| `HD4ZaIURPso` | IT-SRCX-036 | 1261 | 1246 | YOUTUBE_ASR_AUTO | CLOSED | `data/samples/IT-VIDEO-V1/falas/HD4ZaIURPso.json` | YES |
| `AEF-A2AVP7E` | IT-SRCX-036 | 1131 | 1119 | YOUTUBE_ASR_AUTO | CLOSED | `data/samples/IT-VIDEO-V1/falas/AEF-A2AVP7E.json` | YES |
| `2jgjJQqcr-s` | IT-SRCX-036 | 1116 | 1104 | YOUTUBE_ASR_AUTO | CLOSED | `data/samples/IT-VIDEO-V1/falas/2jgjJQqcr-s.json` | YES |
| `ah8sT9hB7HU` | IT-SRCX-036 | 651 | 645 | YOUTUBE_ASR_AUTO | CLOSED | `data/samples/IT-VIDEO-V1/falas/ah8sT9hB7HU.json` | YES |
| `f0Tzdu2j67E` | IT-SRCX-036 | 611 | 606 | YOUTUBE_ASR_AUTO | CLOSED | `data/samples/IT-VIDEO-V1/falas/f0Tzdu2j67E.json` | YES |
| `INGnJtElzkg` | IT-SRCX-036 | 553 | 550 | YOUTUBE_ASR_AUTO | CLOSED | `data/samples/IT-VIDEO-V1/falas/INGnJtElzkg.json` | YES |
| `SlTx6OqFiGA` | IT-SRCX-036 | 532 | 524 | YOUTUBE_ASR_AUTO | CLOSED | `data/samples/IT-VIDEO-V1/falas/SlTx6OqFiGA.json` | YES |

| `c2bJ4IqqXek` | IT-CONVEGNO-V2 | 0 | 0 | NENHUMA — sem legenda em idioma algum | BLOCKED | `data/samples/IT-CONVEGNO-V2/testemunhas/c2bJ4IqqXek.witness.json` | YES (o *bloqueio*) |
| UNKNOWN (2 objetos) | — | — | 28.473 no total | — | LOST | — | NO |

TOTAL: 38 objetos fechados · 3414654 caracteres · 3443081 bytes


**Verificação rápida:**

```bash
python3 scripts/radar_v21.py verificar    # SHA de cada arquivo do pacote canônico
python3 scripts/radar_v21.py testemunha   # WORKFLOW_SURVIVES_NEW_CONTAINER
python3 -m pytest tests/ -q               # 329 passed, 4676 subtests
```

---

## 2 · O RESGATE (o que fiz e por quê)

Três objetos tinham **fechado** na conta anterior e **nunca foram commitados**. Recolhi
exatamente esses três, pela **mesma rota** (`youtube.com/api/timedtext`, json3, sem
credencial, sem cookie, 0 USD).

**Isto não é recoletar os 22.** Os 17 objetos de `IT-CONVEGNO-V1` não foram tocados: mesmo
sha, mesma data de captura, mesma proveniência.

**A prova de que são os mesmos objetos é `CHARS_DELTA = 0` nos três:**

| ID | caracteres medidos agora | medidos pela conta anterior | delta |
|---|---|---|---|
| `wh20ZkHf5Cc` | 59.137 | 59.137 | **0** |
| `AOOVhtTQvPA` | 4.767 | 4.767 | **0** |
| `-4lUyIORl4A` | 171.715 | 171.715 | **0** |

Se fosse outra faixa de legenda, outro idioma ou outra passagem do ASR, o número não bateria.

Testemunhas HTTP linha a linha: `data/samples/IT-CONVEGNO-V2/testemunhas/*.witness.json`.

---

## 3 · FIX-06 REMEDIDO, E O LIMITE **NÃO** FOI ALARGADO

`-4lUyIORl4A` levou bot-check nas tentativas 1 e 2 e devolveu **HTTP 200 com 3.155.193 B na
tentativa 3**, depois de espera, sem credencial. `c2bJ4IqqXek` levou bot-check em 4 tentativas
de metadado e abriu na 5ª.

**A metade "fila" do FIX-06 foi confirmada por outra conta, em outro contêiner, com outra
instalação do yt-dlp.** A metade "muro" **não foi testada de novo, de propósito**.

```
youtube.com/api/timedtext  LEGENDA  ->  bot-check que CEDE à espera     = FILA
googlevideo.com            BINÁRIO  ->  HTTP 403 da política de saída   = MURO
```

**Nenhuma segunda regra foi criada.** O FIX-06 já carrega o próprio limite escrito dentro
dele, em `data/samples/IT-FONTES-V1/IT-FONTES-DESCOBERTA-V1.json` →
`CORRECTIONS_TO_MY_OWN_MEASUREMENTS` → `FIX-06` → `E_O_LIMITE_DESTA_PROPRIA_CORRECAO`.
Duplicar a conclusão em dois lugares faria as duas divergirem com o tempo.

---

## 4 · `c2bJ4IqqXek` — BLOQUEIO LEGÍTIMO, CONFIRMADO SEM GASTAR TENTATIVA

**Estado:** `NO_ITALIAN_CAPTION` + `AUDIO_BINARY_EGRESS_BLOCKED`

Remedição desta conta — **só metadado, zero bytes de mídia pedidos**:

- `CAPTION_LANGS_OFFERED` voltou **vazia**. Não é apenas "sem legenda italiana": este objeto
  **não oferece legenda em idioma nenhum**. O diagnóstico anterior fica confirmado e mais preciso.
- `AUDIO_ONLY_FORMATS` = **48, 106, 129 kbps** — exatamente os três da medição anterior.
- `DURATION_S` = 15.388 (4h16) — confere.
- `AUDIO_BINARY_ATTEMPTED` = **false**.

**A rota alternativa permitida foi testada UMA vez, e era ler a política, não repetir o
caminho bloqueado:** `$HTTPS_PROXY/__agentproxy/status` devolve `selective=false`,
`toolScoped=false`, `recentRelayFailures=[]`. Não há allowlist por host para acionar. A rota
de áudio local desta casa (`scripts/it_audio.py`, `IT-VOZ-AUDIO`) busca MP3 de host de
podcast e não serve para vídeo do YouTube. **Não existe nesta casa rota que obtenha o áudio
sem passar por googlevideo.com.**

Não desliguei verificação TLS e não removi `HTTPS_PROXY`.

Se o áudio um dia abrir, o caminho é `download → whisper local → SINTONIA_WHISPER_LOCAL`,
e **não** `YOUTUBE_ASR_AUTO`, que para este objeto não existe.

---

## 5 · O BURACO QUE **NÃO** FECHEI

O FIX-06 declara **22 objetos e 3.075.569 caracteres**. A conta fecha assim:

```
convegno em git ............ 17 obj   2.811.477 ch
resgatados nesta conta .....  3 obj     235.619 ch
                             -----------------------
subtotal ................... 20 obj   3.047.096 ch
declarado no FIX-06 ........ 22 obj   3.075.569 ch
FALTA ......................  2 obj      28.473 ch
```

**Os ids desses 2 objetos não estão escritos em nenhum arquivo versionado.**

Nesta 2ª rodada a busca foi exaustiva e está fechada:

- `28473` / `28.473` **não aparece literalmente** em nenhum artefato de nenhuma branch (as
  três ocorrências encontradas são coincidências de dígitos num bundle minificado do jsPDF e
  num arquivo de eventos de concorrente, mais os meus próprios artefatos desta missão);
- a única menção a "22 objetos" em todo o repositório é o próprio texto do FIX-06, que **não
  os enumera**;
- contra **todos os 38 objetos commitados**, nenhum objeto isolado, nenhum par e nenhum trio
  soma 28.473 caracteres.

A aritmética foi usada apenas para **descartar**, nunca para inferir identidade. Inventar dois
ids para fechar a conta seria pior que declarar o buraco.

```
OBJECT_ID   = UNKNOWN
PERSISTENCE = LOST
RECOVERY    = NOT_POSSIBLE_WITH_CURRENT_EVIDENCE
```

---

## 6 · O QUE AINDA ESTÁ PENDENTE

### Três grupos de cruzamento

| GROUP_ID | STATUS | INPUTS | OUTPUT PERSISTIDO? | PRÓXIMA AÇÃO |
|---|---|---|---|---|
| `pomacee-drupacee` | **CLOSED** | — | SIM | nada |
| `vite` | **LOST** (output) | íntegros em git | NÃO | refazer |
| `seminativi` | **LOST** (output) | íntegros em git | NÃO | refazer |
| `olivo-agrumi` | **LOST** (output) | íntegros em git | NÃO | refazer |

### Doze leituras de convegno (lotes A–F do `convegno-shard`)

Estavam no ar quando os créditos acabaram. **Output perdido; inputs íntegros.**

**Os INPUTS estão todos em git** — as 38 falas e os arquivos de sinais. **Os OUTPUTS não.**
Refazer é possível e custa fan-out novo, que a missão restringe. **Não refiz por decisão, e
não por esquecimento:** a missão manda não reabrir fan-out amplo, e o handoff é mais valioso
que uma rodada parcial que a próxima troca de conta perderia de novo.

**A dependência de scratchpad efêmero foi CONSERTADA nesta rodada.** A constante `SC` dos
workflows apontava para `b6cc5475-…`, morto. Agora:

- o pacote canônico vive em `data/samples/IT-RADAR-V21/`, **versionado**;
- `MANIFEST.json` guarda ref, path e **blob SHA** de origem por arquivo, e o SHA é endereçado
  por conteúdo — se a origem mudar, `verificar` acusa em vez de divergir em silêncio;
- `activeIngredients.json` é **derivado** dos 163 registros, nunca digitado de memória — o
  defeito que originou o FIX-05;
- `python3 scripts/radar_v21.py testemunha` prova, a partir de `/` e com ambiente vazio, que
  um processo novo sem scratchpad nenhum encontra o pacote, lê as 53 substâncias, os 2.030
  pares e reproduz a assimetria do OLIVO. **WORKFLOW_SURVIVES_NEW_CONTAINER = PASS.**

---

## 7 · ARQUIVOS QUE **NÃO** PODEM SER REGENERADOS

Se algum destes se perder, ele volta só recoletando — e alguns nem isso:

```
data/samples/IT-CONVEGNO-V1/falas/*.json          17 falas · 2.811.477 ch
data/samples/IT-CONVEGNO-V2/falas/*.json           3 falas ·   235.619 ch  (o resgate)
data/samples/IT-VIDEO-V1/falas/*.json             18 falas ·   367.558 ch
data/samples/IT-CAMPO-V1/IT-CAMPO-SINAIS-VERIFICADOS-V1.json    21 sinais sobreviventes
data/samples/IT-CAMPO-V1/IT-CAMPO-SINAIS-VERIFICADOS-V2.json    19 sinais sobreviventes
data/samples/IT-CRUZAMENTO-V1/IT-CRUZAMENTOS-V1.json             7 cruzamentos
data/samples/IT-CRUZAMENTO-V2/IT-CRUZAMENTOS-V2.json     grupo pomacee-drupacee INTEIRO
data/samples/IT-FONTES-V1/IT-FONTES-DESCOBERTA-V1.json   FIX-01..06 e os bloqueios medidos
data/samples/IT-VOZ-AUDIO-V1/ e V2/                      transcrições whisper local
data/samples/IT-INSTAGRAM-V1/ V2/ V3/                    transcrições whisper local
```

```
data/samples/IT-RADAR-V21/*.json            o pacote canonico ADAMA V2.1, PINADO com SHA
data/samples/IT-CONVEGNO-V2/IT-OLIVO-LEITURA-V2.json    a leitura integral do olivo I
data/samples/IT-HANDOFF-CANONICO-V1/*.json  handoff estruturado para a trilha canonica
scripts/radar_v21.py                        o resolver que tira os workflows do caminho morto
```

`IT-CRUZAMENTOS-V2.json` é o mais insubstituível: os **11 descartes com motivo** e os **2
refutados** valem tanto quanto os 2 sobreviventes, e nenhum deles se reconstrói por inferência.

---

## 8 · COMANDOS EXATOS DE RETOMADA

```bash
cd /home/user/eame-sintonia
git fetch origin claude/retomada-coleta-video-convegni-vz50er
git checkout claude/retomada-coleta-video-convegni-vz50er

# dependências (o contêiner vem limpo)
pip3 install yt-dlp pytest

# a suíte que tem de continuar verde
python3 -m pytest tests/ -q          # esperado: 329 passed, 4676 subtests

# conferir que os três resgatados continuam com delta 0
python3 -c "import json,glob
for p in sorted(glob.glob('data/samples/IT-CONVEGNO-V2/falas/*.json')):
    d=json.load(open(p)); print(d['EXTERNAL_ID'], d['TRANSCRIPT_LENGTH'], 'delta', d['CHARS_DELTA'])"

# a rota de coleta que funciona (paciente, sem credencial, 0 USD)
#   scripts/it_video.py :: _fala_youtube()   — legenda, É FILA
#   scripts/it_video.py :: _fala_local()     — áudio+whisper, SÓ com IT_VIDEO_AUDIO=1
#                                              e bloqueado por egresso neste ambiente
```

**NÃO rodar** nada que peça binário de `googlevideo.com` neste ambiente: são 403 garantidos.

---

## 9 · GAPS RESTANTES

1. **2 objetos / 28.473 caracteres** — `UNKNOWN`, busca exaustiva fechada (§5).
2. **3 grupos de cruzamento** e **22 objetos nunca lidos** (~2,1 milhões de caracteres) sem
   output. Inventário completo, com custo e valor por item, em
   `data/samples/IT-HANDOFF-CANONICO-V1/IT-TRABALHO-PERDIDO-V1.json`.
3. **`c2bJ4IqqXek`** bloqueado por egresso (§4). Sem legenda em idioma algum.
4. **136 dos 150 bollettini de 2026** ainda sem texto extraído. Toda afirmação sobre "quando a
   instituição falou pela primeira vez" carrega esse limite.
5. **61 dos 163 registros ADAMA sem rótulo lido.** É a ressalva que impede fechar a assimetria
   do OLIVO, e é barata de resolver — ver §10.
6. **Uma molécula ilegível.** Em `-4lUyIORl4A`, o único ponto de toda a sessão onde uma
   molécula ADAMA poderia aparecer está deformado pelo ASR (`"di disconolo"`). **Recusei** ler
   como *difenoconazolo*. Conferido mesmo assim: os dois registros ADAMA de difenoconazole
   (SPYRALE 009757, MAGANIC 017955) têm rótulo **lido** e nenhum traz olivo — nem a leitura
   favorável abriria rota.

---

## 10 · PRÓXIMA AÇÃO EXATA

**Ler os 61 rótulos ADAMA que nunca foram lidos, procurando OLIVO e as culturas declaradas
vazias.** É leitura de documento, não fan-out; custa muito menos que um grupo de cruzamento; e
resolve de uma vez a ressalva que hoje contamina *todas* as afirmações de ausência desta casa —
inclusive a assimetria do OLIVO, que a leitura desta rodada deslocou para "mercado" sem poder
fechar.

Só depois, e com decisão do dono da missão sobre o custo, reabrir fan-out **nesta ordem**:

| # | O quê | Por quê |
|---|---|---|
| 1 | grupo **seminativi** + `mIunZ-pH3RY`, `dGmP236Z4uQ` | maior peso de rótulo do radar (BARBABIETOLA 239, FRUMENTO 176, ORZO 131, MAIS 112, PATATA 100) e zero cobertura. Agora há material dos **dois lados**: os bilanci externos e o webinar da própria ADAMA sobre cereais, que nomeia AVASTEL, mesosulfuron e pinoxaden. |
| 2 | grupo **vite** + `8_rnThlsy9Q`, `VE8gaWinRmY`, `6eNiYjzPGHw` | 6 dos 19 sinais de fala verificados são de VITE, e é a única cultura com gravação independente do **norte e do sul** — responde a pergunta que a missão pediu e ninguém respondeu. |
| 3 | `CYV76yVc98s` (fragola e piccoli frutti) | pode **corrigir** uma conclusão atual: o vazio declarado de CILIEGIO apoia-se justamente nesta gravação. |
| 4–9 | agrumi, GF 19 marzo, olivo II, webinars ANVE, noce/nocciolo, droni | ver o inventário; noce e nocciolo têm **zero** pares de rótulo, conferido. |

A infraestrutura já não é obstáculo: o `SC` morto foi consertado e há testemunha de que um
processo novo, sem scratchpad nenhum, encontra e lê o pacote canônico.

---

## 11 · FRONTEIRAS RESPEITADAS

Portal, design, Vercel, produção e o snapshot congelado da reunião: **intocados**. Nenhum
resultado desta missão foi inserido no portal de amanhã. O meeting build usa cutoff próprio e
estes resultados entram depois via backfill.

`STATUS_CHANGES = 0`. `SCORE_CHANGES = 0`. Nenhum segundo Opportunity Engine foi criado.
Esta missão coleta e estrutura evidência; ela não decide prioridade comercial.
