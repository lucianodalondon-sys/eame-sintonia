# O PILOTO DA SALA DE ESPERA — a Intelligence pensou, e disse NÃO

> **Missão:** `C-INT-PILOT-SALA-V1`
> **Natureza:** piloto operacional **READ-ONLY**. Não é Intelligence
> operacional, não é Portal, não mexeu na Collection.
> **Medição:** `provas/o_piloto_da_sala.py`
> **Artefato máquina:** `data/derivados/O-PILOTO-DA-SALA.json`

---

## A RESPOSTA, ANTES DA PROVA

```text
SALA_TOTAL                     29
SALA_USABLE_FOR_INTELLIGENCE    7
SALA_WEAK                       7
SALA_INSUFFICIENT              15

CLAIM_CANDIDATES                0
FACT_CANDIDATES                 0
FINDINGS                        0
CROSSINGS_TENTADOS              3
CROSSINGS_POSSIVEIS             0
OPPORTUNITY_CANDIDATES          0
```

**O veredito é `NO_DEFENSIBLE_ACTION_YET`, e ele é um resultado, não uma
falha.** A FASE 12 do enunciado autorizou-o com todas as letras: *29 → 7 → 3
findings → 0 oportunidades é melhor que 29 → 100 insights inventados.*

Chegámos mais fundo do que o cenário pessimista e mais raso do que o otimista,
e por uma razão só — que é o achado desta missão:

> **O que trava a Intelligence não é volume, não é lógica, e não é a máquina.
> É UM CAMPO: a cultura agrícola não atravessa a fronteira.**

---

## A · O ESTADO MEDIDO

```text
REPO          lucianodalondon-sys/eame-sintonia
WORKTREE      C:/int-pilot-sala            (própria do Intelligence Owner)
BRANCH        claude/int-pilot-sala-v1
INITIAL_HEAD  370ce450f4aac60d56540e654c159faa7c907917
BASE          origin/claude/contract-provenance-cutover-v1
DIRTY_NA_BASE 0
```

⚠️ **Nenhuma worktree da Collection foi tocada.** `it-trunk-v1`, `cutover-v2`,
`sc-t8` e as restantes foram **lidas** e mais nada. A Collection continua a
trabalhar em paralelo, como o enunciado mandou.

### A Sala não estava onde a documentação dizia

Este foi o primeiro defeito, e ele custou metade da missão:

```text
DOCUMENTADO   data/samples/PRONTO-PARA-INTELIGENCIA/   ->  não existe,
              e nunca existiu em commit nenhum de ramo nenhum
CENSO V1      O-CENSO-DA-SALA-DE-ESPERA.json           ->  TOTAL = 0
COORTE        COORTE-DA-SALA-2026-09-14.json           ->  6 itens de um
              laboratório descartável que já não existe
REAL, HOJE    postgres 127.0.0.1:54330/sala_italia
              public.sala_de_espera                    ->  29 linhas
```

**Três artefatos commitados descrevem uma Sala vazia. A Sala real tem 29
itens.** Nenhum dos três mente: os três são fotografias honestas de instantes
anteriores ao backend Postgres entrar. Mas quem lesse o Git sem medir o runtime
concluiria `SALA = 0` e pararia.

```text
FOTOGRAFIA HISTÓRICA COMMITADA  !=  ESTADO OPERACIONAL PRESENTE
```

A Sala real é a que `admissao/sala_de_espera.py` declara canônica: **POSTGRES**,
nunca ficheiro. O ficheiro está aposentado e o próprio módulo diz porquê.

---

## B · O QUE HAVIA DENTRO DOS 29

| universo | itens | o que é | serve a pergunta agronômica? |
|---|---:|---|---|
| **T3** | 5 | boletins fitossanitários e agrometeorológicos regionais | **SIM** |
| **T5** | 22 | universidades e institutos — regulamentos, avisos, editais | quase nunca |
| **T7** | 1 | ordem profissional dos agrónomos (CONAF) | não |
| **T9** | 1 | concorrente (Koppert, ácaros predadores) | parcialmente |

Os 29 itens estão **todos** com contrato READY completo de 19 campos, todos
`estado_da_fila = WAITING`, todos `estagio = DOCUMENTO`, capturados entre
**2026-09-18** e **2026-09-20**.

### Os sete utilizáveis, e o que cada um traz

| `SOURCE_ID` | obs | chars | o que é | valor |
|---|---:|---:|---|---|
| `IT-T3-008` | 36 | 62.677 | ARIF Puglia · Notiziario n.38 · 16–22/09/2026 | **o melhor item da Sala** |
| `IT-T3-008` | 9 | 62.895 | ARIF Puglia · Notiziario n.37 · 09–15/09/2026 | série temporal |
| `IT-T3-002` | 26 | 26.106 | Bollettino Fitosanitario Salerno n.27 · 16/09/2026 | cultura × praga × comune |
| `IT-T3-002` | 7 | 26.106 | **o mesmo documento, outra vez** | zero evidência nova |
| `IT-T3-010` | 1 | 24.744 | APOL Puglia · mosca da oliveira · 14–20/09/2026 + Disciplinare | limiar + s.a. |
| `IT-T5-010` | 77 | 209.994 | revista da Câmara de Comércio de Ferrara | **de 2010/2011** |
| `IT-T9-011` | 175 | 8.580 | Koppert Itália · ácaros predadores | sinal competitivo |

⚠️ **`IT-T5-010` é verdadeiro e inútil, e as duas coisas ao mesmo tempo.** Tem a
maior densidade agronômica bruta da Sala (196 ocorrências) e é de **2010**. A
régua de densidade apanhou-o; a janela factual mata-o.

```text
TRUE  !=  RELEVANT  !=  ACTIONABLE
```

Se este piloto pontuasse por densidade, o documento mais irrelevante da Sala
seria o segundo colocado.

---

## C · O CRUZAMENTO QUE QUASE ACONTECEU

O material para um cruzamento real **existe**, e está a um campo de distância.

### O que a Sala tem, lado a lado

```text
IT-T3-008 · ARIF   16–22/09/2026 · Puglia
   «Le alte temperature, superiori alle medie stagionali, stanno ostacolando
    lo sviluppo delle infestazioni attive della mosca (Bactrocera oleae)»
   «eventuali precipitazioni potrebbero favorirne la ripresa»
   «la situazione potrebbe rapidamente cambiare nel caso in cui dovessero
    arrivare piogge e abbassamenti termici»

IT-T3-010 · APOL   14–20/09/2026 · Puglia (Brindisi, Lecce, Taranto)
   «visto l'aumento dell'umidità e il calo termico che favoriscono l'attività
    della mosca dell'olivo»
   infestação 5% · STAZIONARIO · BASSO
   «non si ritiene giustificata l'esecuzione di un trattamento fitosanitario»
```

**Duas fontes, mesma região, semanas sobrepostas, mesma praga, e a mesma
mecânica agronômica: calor alto trava a mosca, chuva e queda térmica soltam-na.**
Isto é exatamente a hipótese da FASE 8 — clima → efeito agronômico → risco →
necessidade de produto — e ela aparece **escrita no material real**, não
fabricada por mim.

### E porque é que ela mesmo assim não passou

```text
EXTERNAL_SIGNAL_COUNT        2   (ARIF, APOL)
INDEPENDENT_SOURCE_COUNT     2   (organismos distintos; APOL não cita ARIF
                                  — medido: 0 ocorrências de «ARIF»,
                                  «Agenzia regionale», «Notiziario»)
STRUCTURAL_VALIDATION_COUNT  0
CONVERGÊNCIA DECLARÁVEL      NÃO
```

A independência é genuína. O que falta é outra coisa: **os dois documentos
dizem que a mosca está sob controlo, e ambos recomendam NÃO tratar.** O sinal
real é um sinal de *ausência de pressão*, com uma condição de reversão
declarada. Transformar isso em oportunidade comercial seria inverter o que a
evidência diz.

```text
SINAL DE QUE NÃO É PRECISO TRATAR  !=  OPORTUNIDADE DE VENDER TRATAMENTO
```

---

## D · O GATE DURO, E O QUE ELE MATOU

O piloto tentou **3 crossings** substância × rótulo ADAMA. Os três morreram, e
é aqui que a missão prova que a máquina epistemológica funciona.

### Candidato 1 — AZOXYSTROBIN (morto pelo rótulo)

```text
OBSERVADO   IT-T3-010 · Disciplinare di Difesa Integrata Olivo Puglia 2026
            Azoxystrobin listado contra Occhio di pavone (Spilocaea oleagina)
ADAMA TEM   SIM — 5 produtos vivos: BLAISE ULTRA, CUSTODIA ULTRA, KOJAMI,
            MAXENTIS, MIRADOR TURBO
GATE        rótulo ADAMA autorizado para a cultura OLIVO?
RESPOSTA    NÃO — 0 usos autorizados
VEREDITO    CROSSING MORTO
```

Medido em `referencia/adama/AUTHORIZED-USES.json`: dos **2.030** usos
autorizados, **exatamente 1** tem `CROP_ON_LABEL = OLIVO` — o herbicida MORAINE,
contra infestantes. Nenhum fungicida, nenhum inseticida.

**Sem este gate, este piloto teria entregue uma oportunidade falsa hoje.** A
substância está no documento oficial, a ADAMA vende-a, e a conclusão errada era
a mais fácil de escrever.

### Candidato 2 — TAU-FLUVALINATE (morto pela cultura ausente)

```text
OBSERVADO   IT-T3-008 obs 9 e 36 · «In presenza di afidi intervenire con:
            deltametrina, lambdacialotrina, tauflufalinate, acetamiprid»
ADAMA TEM   SIM — 7 produtos vivos, 519 usos autorizados, 175 contra afídeos
            (KLARTAN, MAVRIK, EVURE PRO, TAU AL 240 EW)
GATE        para QUE cultura o boletim recomendava?
RESPOSTA    NÃO SEI
VEREDITO    NOT_POSSIBLE
```

E a razão é um defeito de extração, medido: o boletim da ARIF organiza-se por
cultura numa coluna lateral do PDF. O extrator trouxe `Situazione Fenologica`,
`Situazione Fitosanitaria` e `Programma di Difesa` — **e deixou para trás o
cabeçalho que diz de que cultura se está a falar.**

O texto que chegou à Sala lê-se assim:

```text
Situazione Fenologica:  Trapianto - sviluppo vegetativo.
Situazione Fitosanitaria: Presenza di afidi.
Programma di Difesa: ... deltametrina, lambdacialotrina, tauflufalinate ...
```

Qual cultura? **O item não diz.** E a diferença é comercial e regulatória:
tau-fluvalinate tem rótulo ADAMA para `MELO`, `VITE`, `PATATA`, `CAROTA`,
`BARBABIETOLA`, `COLZA`, `FRAGOLA`, `CUCURBITACEE`, `BRASSICACEE`,
`ERBA_MEDICA`, `LEGUMINOSE` — e **não** para olivo.

> Adivinhar a cultura aqui seria fabricar a chave que faz o join fechar.
> É precisamente o ataque que a INT-LAW-037 proíbe.

---

## E · A DEPENDÊNCIA — evidência que se repete não é evidência nova

Medido por impressão do texto:

```text
ITENS NA SALA          29
TEXTOS DISTINTOS       26
```

Três itens são cópias:

| md5 | itens | leitura |
|---|---|---|
| `7cf597a94884` | `IT-T5-034`, `IT-T5-035`, `IT-T5-036` | **três `SOURCE_ID` diferentes, um único documento** |
| `4640f0d5d0aa` | `IT-T3-002` obs 7 e obs 26 | mesma fonte, duas observações, bytes idênticos |

O primeiro é o mais perigoso: **três fontes distintas da Accademia dei
Georgofili entregando o mesmo ficheiro.** Um contador ingénuo de convergência
leria isto como *«três fontes independentes confirmam»* — e seriam zero.

```text
MESMO DOCUMENTO EM TRÊS VISTAS  !=  TRÊS EVIDÊNCIAS INDEPENDENTES
```

Isto não é defeito da Collection: as três fontes existem e cada uma foi
legitimamente observada. É um facto que a Intelligence **tem de contar**, e por
isso o artefato carrega `OBSERVACOES_DUPLICADAS` explicitamente.

---

## F · OS GAPS DA COLLECTION

Ordenados por quanto cada um custa à Intelligence. Nenhum foi despachado —
a FASE 10 proíbe, e a INT-LAW-020 também.

### GAP-01 · `CROP` não atravessa a fronteira — **BLOQUEADOR**

```text
QUESTION_BLOCKED   substância recomendada × cultura × rótulo autorizado
MISSING_KEY        CROP
PORQUE             o contrato READY de 19 campos não tem campo de cultura;
                   e no caso da ARIF a cultura nem sobrevive à extração do PDF
IMPACTO            mata 100% dos crossings fitossanitários
REPROCESS_FIRST    SIM — os bytes estão preservados no armazém; isto é
                   re-derivação, não recoleta
```

**Este é o gap que decide se a próxima Big Collection alimenta Intelligence ou
só enche a Sala.**

### GAP-02 · `FACT_TIME` = `NAO SEI` em 29/29

```text
MEDIDO             FACT_TIME_CONHECIDO = 0 · FACT_LOCATION_CONHECIDO = 0
                   FACT_TIME_IGUAL_PUBLISHED = 0   (nada foi fabricado)
IMPACTO            nenhum ACT_NOW é defensável; a janela factual não existe
CONSEQUÊNCIA REAL  `IT-T5-010`, de 2010, não pode ser separado por regra dos
                   boletins de setembro de 2026 — só por leitura humana
```

⚠️ **O `NAO SEI` aqui é a Collection a acertar, não a falhar.** Os documentos
*trazem* data — «N° 27 del 16/09/2026», «14/09/2026 - 20/09/2026» — mas
ninguém promoveu essa data a `FACT_TIME`, e promovê-la sem regra seria
transformar tempo de publicação em tempo do facto. O gap é a **regra que
falta**, não o campo por preencher.

### GAP-03 · `EVIDENCE_CLASS` = `NAO SEI` em 29/29

Um boletim oficial de serviço fitossanitário regional e um edital de tutoria
universitária entram na Sala com exatamente a mesma credibilidade declarada.
A Intelligence tem de reclassificar por conta própria — que é o que o campo
`DENSIDADE_AGRO` deste piloto faz, e é uma muleta, não uma solução.

### GAP-04 · `run_id` começado por `XX` — identidade de país perdida

```text
XX-T3-2026-09-18-171909-b66be5e4276b76f7   ->  IT-T3-002
XX-T3-2026-09-18-171937-6f76511ca75100a5   ->  IT-T3-008
XX-T3-2026-09-18-134205-772b57c43c0130fe   ->  IT-T3-010
```

Três das cinco corridas T3 — **as três agronomicamente mais valiosas da Sala** —
carregam `XX` onde as outras 26 carregam `IT`. O `SOURCE_ID` diz `IT`; o
`RUN_ID` diz `XX`.

> Não corrigi. A identidade da corrida é da Collection (COL-LAW-022), e a
> Intelligence reescrever `XX` para `IT` seria cunhar identidade upstream.
> Fica registado como defeito de Collection, com os três IDs exatos.

### GAP-05 · a Sala não distingue documento agronômico de documento administrativo

**22 dos 29 itens (76%) são T5 universitário.** Regulamentos de ITS, políticas
de acesso aberto, avisos de seleção de tutores, guias de arquivo institucional.
São material real, preservado e legitimamente admitido — e não respondem a
nenhuma pergunta agronômica.

Isto **não é erro de admissão**: `admitido_por = "pertence ao universo v5"`, e
eles pertencem mesmo. É o universo que é largo para esta pergunta.

---

## G · FEEDBACK DE FONTES

Evidência para o futuro Bot de Fontes. **Não é ranking** — a
INT-LAW-036 exige contribuição contextual, não score global.

| `SOURCE_ID` | itens | utilizáveis | que espécie de evidência produziu |
|---|---:|---:|---|
| `IT-T3-008` · ARIF Puglia | 2 | **2** | clima **+** fitossanitário **+** fenologia **+** s.a., por cultura e semana, com série (n.37, n.38) |
| `IT-T3-002` · Fitosanitario Salerno | 2 | 1 útil, 1 duplicado | cultura × praga × comune × empresa × limiar de intervenção |
| `IT-T3-010` · APOL Puglia | 1 | **1** | praga × comprensório × % infestação × tendência × Disciplinare com s.a. |
| `IT-T9-011` · Koppert | 1 | 1 parcial | sinal competitivo — biológico contra o mesmo problema |
| `IT-T5-010` · CCIAA Ferrara | 1 | 0 | agronômico mas de **2010** — fora de qualquer janela |
| `IT-T5-034/035/036` · Georgofili | 3 | 0 | **o mesmo documento três vezes** |
| restantes 17 `IT-T5-*`, `IT-T7-013` | 17 | 0 | administrativo universitário |

**A frase útil, no formato que a FASE 9 pediu:**

> `IT-T3-008` (ARIF Puglia) produziu, num único documento, evidência
> meteorológica observada e prevista **e** evidência fitossanitária por cultura
> com substância ativa nomeada, para a mesma região e a mesma semana — e
> entregou duas edições consecutivas, o que permite série temporal.
> **É a fonte de maior valor analítico da Sala.**

E a que interessa ao Bot de Fontes tanto quanto:

> O bloco `IT-T5` entregou **22 itens e 0 utilizáveis** para a pergunta
> agronômica. Isto não diz «fontes más» — diz que **o universo T5 está a ser
> colhido sem filtro de pergunta**. Se a Big Collection escalar T5 na proporção
> atual, ela multiplica volume sem multiplicar Intelligence.

```text
SOURCE PRODUCED CONTENT  !=  SOURCE PRODUCED USEFUL INTELLIGENCE
HIGH VOLUME              !=  HIGH VALUE
```

⚠️ **Nenhum `SOURCE_COLLECTION_ADVICE` foi emitido.** Esse owner não está
implementado, e inventá-lo aqui criaria um segundo dono.

---

## H · OS TESTES (FASE 15)

Todos contra a Sala real, com o cliente real.

| # | o que prova | como | veredito |
|---|---|---|---|
| 1 | Intelligence não lê item não admitido | AST do piloto: tabelas lidas = `{sala_de_espera}`. 171 `raw_asset` fora da Sala ficaram invisíveis | **PASS** |
| 2 | evidence/provenance não se perde | `SALA_SEM_RAW_OBS = 0` · `RAW_INEXISTENTE = 0` · `RUN_INEXISTENTE = 0` | **PASS** |
| 3 | UNKNOWN não vira valor inventado | `FACT_TIME_CONHECIDO = 0` no artefato, 29 `NAO SEI` preservados | **PASS** |
| 4 | `FACT_TIME` não nasce de publication time | `FACT_TIME_IGUAL_PUBLISHED = 0` | **PASS** |
| 5 | `FACT_LOCATION` não nasce de source location | `FACT_LOC_IGUAL_SOURCE_LOC = 0` | **PASS** |
| 6 | reprocessamento não duplica | 3 execuções acumuladas → 3 crossings únicos | **PASS** |
| 7 | mesmo input, resultado determinístico | 2 artefatos **byte-a-byte idênticos** (25.526 B) | **PASS** |

```text
NEW_FAILURES = 0
```

### Red team — e o ataque que tinha de ter contraprova

| # | ataque | resultado |
|---|---|---|
| RT-1 | a Intelligence lê item não admitido? | **REFUTADO** — só `sala_de_espera` |
| RT-2 | o piloto escreve em algum sítio? | **REFUTADO** — 0 SQL de escrita; 1 `open(w)`, o `--json` |
| RT-3 | vai à rede / chama coletor? | **REFUTADO** — 0 imports de rede |
| RT-4 | `UNKNOWN` desaparece no artefato? | **REFUTADO** — `NAO SEI` sobrevive |
| RT-5 | **o gate é uma parede que diz NÃO a tudo?** | **REFUTADO com contraprova** |

⚠️ **RT-5 é o que valida os outros quatro.** Um gate que reprova tudo passa em
qualquer teste negativo e não vale nada. A contraprova mostra que a lógica
distingue três estados diferentes:

```text
CROP = MELO   ->  PODERIA fechar     (rótulo ADAMA existe)
CROP = OLIVO  ->  fecharia em NÃO    (rótulo ADAMA não existe)
CROP ausente  ->  NOT_POSSIBLE       (nem sim nem não)
```

> **O que falta é o DADO, não a lógica.** A máquina epistemológica funciona;
> ela está a ser alimentada com um item que não carrega a chave.

---

## I · O TESTE DE VALOR (FASE 13)

**A · O Sintonia extraiu informação útil da Sala?**
`PARTIAL`. Extraiu estrutura, dependência, classificação, e matou duas
conclusões falsas. Não extraiu facto acionável.

**B · Produziu finding sustentado por evidência?**
`NÃO` — zero `FINDING`. Produziu 3 `EVIDENCE_LINKED_OBSERVATION`, que é o
degrau anterior e é o degrau honesto.

**C · Produziu oportunidade candidata defensável?**
`NÃO`. `ADAMA_PRODUCT_MATCH = UNKNOWN` em todos os casos, e num deles
(azoxystrobin × olivo) o match foi **ativamente refutado** pelo rótulo.

**D · Que campos mais limitaram a Intelligence?**
```text
1º  CROP            ausente do contrato READY   -> mata todo crossing
2º  FACT_TIME       NAO SEI em 29/29            -> mata todo ACT_NOW
3º  FACT_LOCATION   NAO SEI em 29/29            -> mata todo recorte regional
4º  EVIDENCE_CLASS  NAO SEI em 29/29            -> boletim = edital
```

**E · A próxima Big Collection já alimenta esta cadeia automaticamente?**
`PARCIALMENTE`, e a parte que falta é conhecida:

```text
JÁ FUNCIONA     Sala persistente · contrato de 19 campos · linhagem íntegra ·
                identidade preservada · incremental por --desde
AINDA NÃO       CROP · FACT_TIME · FACT_LOCATION · EVIDENCE_CLASS
```

Sem os quatro, escalar a Big Collection multiplica itens `WAITING` sem
multiplicar crossings. **Com `CROP` resolvido, o crossing fitossanitário
fecha na próxima corrida** — a referência ADAMA já está pronta e provada.

**F · O que falta para isto virar Intelligence operacional recorrente?**
```text
1. CROP no contrato READY, ou re-derivação que o preserve  (Collection)
2. regra declarada FACT_TIME <- data do documento           (Collection)
3. INTELLIGENCE_RUN como objeto real com identidade         (Intelligence)
4. destravar TRAVA-DA-INTELIGENCIA                          (não é desta Bíblia)
```

---

## J · A AUTOMAÇÃO MÍNIMA (FASE 14)

Provada, não descrita:

```bash
export PGPASSFILE=<pgpass do dono da Sala>
export SINTONIA_PSQL=<caminho nativo do psql>

python3 provas/o_piloto_da_sala.py --dsn "$SALA_DSN"                  # tudo
python3 provas/o_piloto_da_sala.py --dsn "$SALA_DSN" --desde 2026-09-20  # só novos
```

Medido: `--desde 2026-09-20` devolveu **25 de 29** — o incremento real.
Sem scheduler, sem daemon, sem plataforma nova.

---

## K · O QUE ESTA MISSÃO **NÃO** FEZ

```text
NÃO mexeu na Collection          nenhuma worktree da Collection foi escrita
NÃO procurou fontes              0 acessos à rede, provado por AST
NÃO alterou Admission            admissao/ intocado
NÃO construiu Portal             0 ficheiros em italia-portale/
NÃO releu RAW para contornar     171 raw_asset fora da Sala ficaram invisíveis
NÃO despachou COLLECTION_GAP     os 5 gaps ficam escritos, não despachados
NÃO criou owner novo             FACT, FINDING, OPPORTUNITY continuam sem dono
NÃO destravou nada               TRAVA-DA-INTELIGENCIA continua NAO
```

### E não promoveu o piloto a Intelligence

```text
INTELLIGENCE_RUN implementado        NÃO
CLAIM/FACT owner implementado        NÃO   (tabelas existem, 0 linhas)
SALA -> CLAIM/FACT path              NÃO EXISTE
```

Medido no banco: `boletim_fitossanitario 0` · `crop 0` · `crop_issue 0` ·
`issue 0` · `clima_observacao 0` · `geografia 0` · `lacuna_candidata 0`.

**O schema analítico existe inteiro e está vazio.** Por isso tudo o que este
piloto emite sai como `EVIDENCE_LINKED_OBSERVATION`, e nunca como `FACT`.

```text
SCHEMA EXISTS  !=  WRITER USES IT
```

---

## L · O PRÓXIMO PASSO MÍNIMO

**Um só, e é da Collection:**

> Fazer `CROP` atravessar a fronteira para os itens `IT-T3`, por
> **re-derivação** dos bytes já preservados — não por recoleta.

Quando esse campo chegar à Sala, este mesmo script, sem uma linha alterada,
passa a fechar o crossing fitossanitário. A referência ADAMA está pronta
(2.030 usos autorizados, 602 registos, 163 vivos) e a lógica está provada pela
contraprova RT-5.

**HARD STOP.** Não inicio a próxima missão.

---

## EM PALAVRAS SIMPLES

**1 · O que havia dentro das 29 coisas da Sala?**
Vinte e nove documentos italianos, todos guardados corretamente. Cinco são
boletins agrícolas de verdade — o tipo de papel que diz «esta semana, nesta
região, esta praga está assim». Vinte e dois são papelada de universidade:
regulamentos, editais, avisos. Um é de um concorrente. Um é de uma ordem
profissional.

**2 · Quantas serviram mesmo?**
Sete. E dessas sete, três são as que realmente valem: dois boletins da Puglia
(da agência ARIF) e um sobre a mosca da oliveira. Um oitavo parecia bom — tem
mais palavras agrícolas que todos os outros — até se ver que é uma revista de
**2010**. Verdadeiro, e velho de dezasseis anos.

**3 · Que informação nova o Sintonia conseguiu produzir?**
A mais valiosa foi uma **recusa**. O sistema encontrou um produto que a ADAMA
vende (azoxystrobin), encontrou-o recomendado num documento oficial italiano
sobre oliveiras, e ia dizer «aqui está uma oportunidade». Então foi verificar o
registo oficial dos rótulos e descobriu: **a ADAMA não tem esse produto
autorizado para oliveira em Itália.** Zero autorizações. A venda seria ilegal.

O sistema apagou a própria conclusão antes de a mostrar. É para isto que ele
existe.

Descobriu também que três «fontes» diferentes estavam a entregar exatamente o
mesmo ficheiro — se alguém contasse «três fontes concordam», estaria a contar
a mesma coisa três vezes.

**4 · Apareceu alguma oportunidade interessante?**
Não, e não é má notícia. Os dois boletins independentes dizem a mesma coisa: o
calor está a travar a mosca da oliveira e **não vale a pena tratar agora**.
Vender tratamento contra isso seria vender contra a evidência.

Mas os dois deixam um aviso igual: *se vier chuva e a temperatura cair, a
situação muda depressa*. Isso é a coisa mais interessante que a Sala tem — e é
uma coisa para **vigiar**, não para vender hoje.

**5 · O que mais está a faltar nos dados?**
Uma coisa só, e é quase caricata: **falta dizer de que planta se está a falar.**

O boletim da ARIF diz «há pulgões, use tau-fluvalinate». A ADAMA tem esse
produto, com sete marcas vivas em Itália. Mas o texto que chegou não diz se os
pulgões estão na maçã, na batata ou na vinha — essa informação estava numa
coluna lateral do PDF e perdeu-se ao converter para texto. E a diferença
importa: o produto está autorizado para maçã e para vinha, **não** para
oliveira.

Sem saber a planta, o sistema recusa-se a responder. E faz bem.

Falta também a **data do facto**: os documentos trazem a data escrita lá
dentro, mas ninguém ainda deu a ordem formal «esta data é a data do que
aconteceu». Por isso o sistema não consegue, sozinho, separar um boletim desta
semana de uma revista de 2010.

**6 · Que tipo de fonte deu informação útil?**
As agências agrícolas regionais — ARIF da Puglia, Serviço Fitossanitário de
Salerno, a associação de produtores de azeitona APOL. Um único documento da
ARIF traz o tempo que fez, o tempo que vai fazer, que pragas apareceram, em que
planta, e que produtos usar. É a melhor fonte que temos.

As universidades deram 22 documentos e **zero** informação agrícola aproveitável.
Não são fontes más — estão a ser recolhidas sem se perguntar primeiro para que
servem.

**7 · A próxima Big Collection já pode alimentar isto automaticamente?**
Metade sim. O caminho está construído e testado: a Sala guarda bem, nada se
perde, a linhagem aguenta, e já sei processar só o que é novo sem repetir o
antigo (testado: 29 itens no total, 25 novos).

A outra metade depende daquele campo em falta. **Se a próxima recolha trouxer
a planta junto com a recomendação, este mesmo programa — sem mudar uma linha —
passa a produzir cruzamentos a sério.** Os dados da ADAMA já estão prontos e à
espera: 602 registos, 2.030 usos autorizados, tudo verificado.

Não é preciso construir nada de novo. É preciso passar um campo pela porta.
