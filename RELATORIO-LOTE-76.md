# RELATÓRIO — LOTE DE 76 · RAW → ADMISSION → SALA

Base `materia-prima-v1` @ `2a8a1933`. Corrida da coorte:
`OPS_forward-only-live_20260922185447_a9d037`.

```
ACTUAL_LLM_MODEL = claude-opus-5
NETWORK_ALLOWED  = NO      NETWORK_REQUESTS = 0     DNS_LOOKUPS_EXTERNAL = 0
NO_MANUAL_INSERT = YES     NO_BYPASS = YES          COST_USD = 0
```

---

## FASE 0 — O ACHADO, CONFIRMADO, E A CAUSA

### Confirmação, medida a medida

| medida | declarado no briefing | medido por mim |
|---|---|---|
| linhas da coorte no ledger de ficheiro | 76 | **76** ✅ |
| `NEW_DOCUMENT` | 29 | **29** ✅ |
| `SEEN_AGAIN` | 30 | **30** ✅ |
| `DOCUMENT_CHANGED_IN_PLACE` | 17 | **17** ✅ |
| bytes | 7 563 718 | **7 563 718** ✅ |
| `raw_asset` com `%a9d037%` | 0 | **0** ✅ |
| `raw_asset` criados hoje | 0 | **0** ✅ (o último era de 21/09 22:46Z) |
| `collection_run` com a9d037 | 0 | **0** ✅ |
| `sala_de_espera` | 56 | **56** ✅ |
| raw · storage · derived | 1329 · 1023 · 832 | **1329 · 1023 · 832** ✅ |

Base canónica localizada: **`sala_italia` em `127.0.0.1:54330`**
(`C:/Users/London1/sintonia-sala-italia`). É a única bancada operacional que a
casa autoriza — `guarda/banco_operacional.py:73` tem `BANCOS_OPERACIONAIS =
("sala_italia",)`.

### `PORQUE_NAO_FOI_A_BASE`

**Não houve falha. Há duas estradas, e os 76 foram pela que não passa pelo banco.**

```
PORQUE_NAO_FOI_A_BASE = O COLETOR QUE FEZ A CORRIDA NÃO ESCREVE raw_asset,
                        E NUNCA ESCREVEU. Não é avaria; é o desenho dele.
RAW_ASSET_OWNER       = guarda/preservar_coleta.preservar()
                        chamado por coleta/ingresso.py::receber()
                        NESTA CORRIDA: ninguém o chamou.
```

Prova, em três factos:

1. `coleta/italy_recurrent_collect.mjs` — o coletor agendado que produziu a
   a9d037 — **não tem uma linha de Postgres**. A única peça externa que ele
   invoca é `curadoria/collection_gate.py`. A lista de 19 etapas dele
   (linhas 12–19) vai de «lock» a «soltar lock», e a etapa que ele chama
   «storage» é *disco gravável + `git push`*: a durabilidade dele é o **Git**.
2. O dono do `raw_asset` é outra peça, na estrada Python
   (`orquestrador` → `coleta/ingresso.py` → `guarda/preservar_coleta`).
3. Isto é **estrutural, não incidental**: a base tem **388 corridas** e
   **zero** com o nome `OPS_forward-only-live_*`. Dos **59** `RUN_ID`
   distintos do ledger de ficheiro, só **6** existem também no banco.

```
COLHIDO E REGISTADO EM FICHEIRO != PERSISTIDO NA BASE CANÓNICA
```

### A ponte existia, e é canónica

`coleta/italy_executor.py::colher(run_id)` lê o ledger de ficheiro e os bytes
do armazém e declara o envelope que a porta canónica sabe ler. O próprio
ficheiro declara o propósito: *«Traduções 2, 3 e 4 — sem correr o coletor […]
sem a separação, provar a tradução obrigaria a haver rede.»*

Rota usada, **sem uma linha de código novo e sem rede**:

```
coleta/italy_executor.colher(OPS_..._a9d037)          → envelope
orquestrador --so-a-porta --colheita-da-corrida=...   → porta canónica
```

---

## FASE 1 — A COORTE, FECHADA

```
COHORT_TOTAL    = 76    (medido; bate com o declarado)
BYTES_EM_DISCO  = 76/76 — todos os RAW_PATH existem
CONTENT_TYPE    = text/html em 76/76
RAW_IN_DB (antes) = 0
```

Por fonte, do ledger e do banco — **as duas contagens batem**:

| SOURCE_ID | n |
|---|---|
| IT-T7-017 | 30 |
| IT-T7-033 | 15 |
| IT-T10-022 | 10 |
| IT-T7-042 | 10 |
| IT-T10-018 | 9 |
| IT-T10-021 | 1 |
| IT-T7-021 | 1 |
| **total** | **76** |

### `NOVOS` vs `JA_CONHECIDOS`

```
NOVOS           = 29   (NEW_DOCUMENT)
JA_CONHECIDOS   = 47   (30 SEEN_AGAIN + 17 DOCUMENT_CHANGED_IN_PLACE)
```

⚠️ Os 30 `SEEN_AGAIN` **não tinham `raw_asset` anterior**: como nenhuma corrida
`OPS_*` chegou alguma vez ao banco, «já visto» aqui refere-se ao **caderno de
ficheiro**, não ao acervo. No banco, os 76 são todos primeira vez.

**Dos que chegaram à Sala: 5, e os 5 são `NOVOS`** (`NEW_DOCUMENT`).

---

## FASES 2–4 — REDE, CAMINHO E TRANSFORMAÇÃO

```
NETWORK_REQUESTS = 0        nenhum item exigiu rede
NEEDS_RECOLLECTION = 0
```

Rede zero **por caminho de código**, não por confiança: `--so-a-porta` não
chama o executor (`orquestrador/orquestrador.py:880-890`), e a derivação lê
ficheiros locais. `COST_USD = 0`, `CAPTURE_METHOD = gratuito`.

Todos os 76 são `text/html` → dono canónico único, `executor_texto_de_html`.
Nenhum extrator novo foi criado.

```
DERIVED_CREATED = 76     REUSED = 0     NOT_APPLICABLE = 0     FAILED = 0
```

Texto extraído, medido: **76/76 com texto real** — mínimo 1 851, mediana 3 601,
máximo 11 459 caracteres. **Nenhuma transformação vazia atravessou.**

---

## ⚠️ O DEFEITO QUE ESTA MISSÃO ENCONTROU, E CORRIGIU

A primeira passagem deu **76 → 69 → 69 → 69**: sete documentos desapareciam
entre o `raw_asset` e a derivação **sem sair em lista nenhuma**
(`RECUSADOS = 0`, `SEM_BYTES_PARA_DERIVAR = 0`).

Causa, medida chamando `conferir_o_que_ficou_escrito()` diretamente contra o
banco vivo — os 7 divergiam **todos no mesmo campo e da mesma maneira**:

```
CAMPO          captured_at
NO_BANCO       2026-09-22T18:55:13.64Z
NESTA_CORRIDA  2026-09-22T18:55:13.640Z
```

É o **mesmo instante**. O Postgres não imprime o zero final dos milissegundos;
quem escreveu a linha imprime-o. `guarda/preservar_coleta.py::_difere()`
comparava **texto** (`str(a) != str(b)`) e devolvia `METADATA_CONFLICT` — o nome
reservado para «outros bytes no mesmo endereço», que é uma acusação sobre o
mundo. Os 7 eram exatamente as observações cujos milissegundos acabam em zero.

```
UM COMPARADOR QUE CHAMA CONFLITO AO MESMO VALOR
NÃO ESTÁ A CONFERIR: ESTÁ A INVENTAR DIVERGÊNCIA.
```

**Correção** (`5fc2979d`): `_instante()` reconhece só hora completa (regex
estreita — `"2026"`, `"1329"`, `"v1_7c93f9ee0a3b"` não passam) e só quando **os
dois** lados são hora se comparam instantes. Em tudo o resto, letra a letra,
como sempre. Aceita as duas formas de fuso (`+00` do Postgres, `+00:00` de quem
escreve). **Não afrouxa a conferência**: dois instantes diferentes continuam a
divergir.

O mesmo defeito estava latente em `started_at` e nos outros dois chamadores
de `_difere` nesta peça.

Prova: **13 casos, 8 deles controlos negativos** que têm de continuar a divergir
— 1 segundo, **1 milissegundo**, dia diferente, mesmo relógio noutro fuso, hora
contra texto, texto, número, sha parecido. Todos divergem. Contra o banco vivo:
`POST_WRITE_METADATA_MATCH` **69 → 76**, `DIVERGENTES` **7 → 0**.

⚠️ **Isto não fez entrar mais ninguém na Sala.** `SALA_DELTA = +5` antes e
depois. Fez os 7 serem **julgados** em vez de sumirem: dos 7, seis `NAO` e um
`NAO_SEI`. É outra coisa, e vale por si.

---

## FASES 5–6 — ADMISSÃO E SALA

A base foi reposta ao estado pré-corrida (`PRE-LOTE76.dump` — raw 1329,
storage 1023, derived 832, sala 56, run 388: bate exatamente com a medição do
dono) e a porta canónica correu **uma vez**, já com a correção.

Corrida: **`XX-T10-2026-09-22-193411-0a8a01dbc999da85`**

```
colheita encontrada   76
INGRESSO              PARA_A_PORTA 76 · PRESERVADOS 76 · RECUSADOS 0
                      PARA_A_DERIVACAO 76 · SEM_BYTES 0
DERIVACAO             PASSED 76 · REJECTED 0 · ERROR 0 · NOT_RUN 0   → PASS
ESTRUTURACAO          76 estruturados
ADMISSAO              76 julgados
```

**Nenhum degrau perde gente.** 76 → 76 → 76 → 76.

```
ADMISSION_SIM      =  5
ADMISSION_NAO      = 47
ADMISSION_NAO_SEI  = 24
ADMISSION_ERRO     =  0
ADMISSION_NAO_SE_APLICA = 0

SALA_BEFORE = 56    SALA_AFTER = 61    SALA_DELTA = +5
```

Estado do banco: raw 1329→**1405** (+76) · storage 1023→**1097** ·
derived 832→**908** (+76) · run 388→**389**.

### As 5 linhas novas da Sala, com o trilho inteiro

| ordem | SOURCE_ID | RAW | STORAGE | DERIVED | ADMISSION_ID | SALA (item_id) | veredito | estado |
|---|---|---|---|---|---|---|---|---|
| 0 | IT-T10-018 | 1331 | 1331 | 834 | derived:834 | derived:834 | SIM | WAITING |
| 1 | IT-T10-018 | 1330 | 1330 | 835 | derived:835 | derived:835 | SIM | WAITING |
| 2 | IT-T10-018 | 1333 | 1333 | 836 | derived:836 | derived:836 | SIM | WAITING |
| 3 | IT-T10-018 | 1334 | 1334 | 839 | derived:839 | derived:839 | SIM | WAITING |
| 4 | IT-T10-018 | 1332 | 1332 | 841 | derived:841 | derived:841 | SIM | WAITING |

`RUN_ID` das cinco: `XX-T10-2026-09-22-193411-0a8a01dbc999da85`.
`OBSERVATION_ID` = `raw_asset.id` (a casa não tem outro).

---

## FASE 7 — O QUE NÃO ENTROU, E PORQUÊ

**Uma única regra decidiu os 76: `pertence ao universo`.** Nenhum outro portão
reprovou ninguém — os 76 passaram em *legível*, *origem* e *linhagem*.

```
MISSING_ROUTE      = 0      MISSING_RULE       = 0
MISSING_CAPABILITY = 0      BAD_CONTENT        = 0
ERRO               = 0      NAO_SE_APLICA      = 0
```

A régua exige **2 sinais** de vocabulário do universo no texto. Pareto, por
quantos sinais o texto tinha:

| veredito | sinais encontrados | n |
|---|---|---|
| SIM | 6 | 1 |
| SIM | 3 | 2 |
| SIM | 2 | 2 |
| NAO_SEI | 1 (indício, não sinal) | 8 |
| NAO_SEI | outro motivo da mesma regra | 16 |
| NAO | 0 | 47 |

O motivo do `NAO_SEI` de um sinal, nas palavras da própria régua: *«uma palavra
solta pode ser acidente de substring, citação de passagem ou cabeçalho. É
indício, não sinal — e indício não promove nem rejeita.»*

### ⚠️ UMA FALHA DE MEDIÇÃO MINHA, DECLARADA

A coorte atravessa **dois universos** — 56 documentos de fontes **T7** e 20 de
fontes **T10** — e eu corri a porta **uma vez, com `universo=T10`**. O universo
é *«que pergunta a porta faz ao conteúdo»*. Logo, **56 documentos foram
perguntados pela pergunta errada.**

Medi o efeito, julgando cada documento pelo **seu** universo — leitura pura,
`adm.decidir()` **sem** `adm.escrever()`, nada foi escrito:

| | SIM | NAO_SEI | NAO |
|---|---|---|---|
| T10 (20) — pergunta certa nas duas medições | 5 | 14 | 1 |
| T7 (56) — **pergunta T10** (o que ficou escrito) | 0 | 10 | 46 |
| T7 (56) — **pergunta T7** (a correta, medida) | **0** | **36** | **20** |

**`ADMISSION_SIM` continua 5 nos dois casos.** Corrigir a pergunta não põe um
único documento a mais na Sala; move 26 documentos T7 de «não» para «não sei».

**Por isso não corri a segunda passagem.** Ela acrescentaria 76 observações
novas ao acervo para **zero** ganho na Sala. Registo a dívida em vez de a pagar
com lixo:

```
DIVIDA: os vereditos T7 escritos (46 NAO, 10 NAO_SEI) respondem à pergunta
        T10. A leitura correta é 20 NAO / 36 NAO_SEI, e está MEDIDA, não
        escrita. Nenhum deles seria SIM.
```

---

## FASES 8–9 — TEMPO, LUGAR E PROVENIÊNCIA

```
FACT_TIME      UNKNOWN   76/76      FACT_LOCATION  UNKNOWN  76/76
REGION         UNKNOWN              CROP           UNKNOWN
```

`FACT_TIME` traz motivo declarado pela fonte em todos os 76: *«UNKNOWN —
identidade pelo endereço; a fonte não expõe data do facto por regra genérica»*.

⚠️ **`FACT_TIME != CAPTURED_AT` em 76/76** — verificado valor a valor. A fonte
não expõe data do facto e **nada foi preenchido para parecer completo**. Nas 5
linhas da Sala, `fact_time`, `fact_location` e `source_location` estão todos
`NAO SEI`, que é ausência declarada.

```
PROVENANCE_COMPLETE = YES
```

Provado por junção real no banco para as 5 linhas admitidas:
`SOURCE → RUN → OBSERVATION → RAW → STORAGE → DERIVED → ADMISSION → SALA`,
sem um elo nulo. E para a coorte inteira: **76 raw · 76 com storage · 76 com
derived**.

---

## FASES 10–13 — NÃO REGREDIR, PROVAS, MAPA

```
UNNECESSARY_REFETCHES = 0    nada foi recolhido; zero idas à fonte
NEW_FAILURES          = 0
```

`tests.test_preservar_coleta` · `test_preservar_coleta_no_banco` ·
`test_preservar_derivado` · `test_a_collection_preserva_o_fato`:
**146 provas, 1 vermelho**. Esse vermelho é
`test_o_raw_tem_um_caller_e_e_a_porta_canonica`, que compara
`coleta\ingresso.py` com `coleta/ingresso.py` — **separador de caminho do
Windows**. Provado pré-existente: corri-o contra o ficheiro da base
(`772b2329`, antes da minha correção) e falha igual.

Ataques ao código novo, com controlo negativo (13 casos, 8 negativos): todos
resistem — ver a secção do defeito.

Ataques do briefing, medidos nesta corrida:

| ataque | resultado |
|---|---|
| HTML salta a transformação | **não passa** — 76/76 derivados, texto real, mínimo 1 851 caracteres |
| admissão vira `SIM` automático | **não passa** — 5 de 76; 71 recusados com regra nomeada |
| RAW entra direto na Sala | **não passa** — toda linha da Sala tem `derived:NNN` e junção completa |
| `SOURCE_ID` perde-se | **não passa** — 7 fontes no ledger, as mesmas 7 no `raw_asset` |
| `RUN_ID` errado é aceite | **não passa** — `_procurar_a_observacao` chaveia por `run_id` |
| `FACT_TIME` herda `PUBLISHED_AT` | **não passa** — `FACT_TIME != CAPTURED_AT` em 76/76 |
| `FACT_LOCATION` herda `SOURCE_LOCATION` | **não passa** — ambos `NAO SEI`, nenhum preenchido |
| transformação vazia entra | **não passa** — zero itens sem texto |
| falha some do Pareto | **era verdade, e foi isto que corrigi** — 7 sumiam; agora 0 |
| alguma etapa tenta rede | **não passa** — `--so-a-porta` não chama o executor |

### `SYSTEM_MAP_CHECK = FAIL` — medido, e **não é regressão minha**

Cadeia canónica corrida como `AGENTS.md` manda:
`correr_a_cadeia.py REGERAR` → **`CADEIA=OK`, 20/20 passos**.
`correr_a_cadeia.py VALIDAR` → **`SYSTEM_MAP_CHECK=FAIL`, 1 prova reprovada**.

A prova reprovada é `P9_CODIGO_DECLARADO`, e o ficheiro é
`provas/recollection_red_team_estrito.mjs`, que não tem peça no mapa.

Prova de que é herdado:

* entrou no commit **`42708647`**, anterior à base `2a8a1933` desta missão;
* `git diff --name-only 2a8a1933..HEAD` dá **4 ficheiros**, e nenhum é `.mjs`:
  `RELATORIO-LOTE-76.md`, `data/samples/LIVRO-DE-DECISOES.json`,
  `data/samples/RUN-MANIFEST.json`, `guarda/preservar_coleta.py`.

A minha alteração de código **não muda a rota**: não cria ficheiro, não
importa nada fora da biblioteca padrão (`re`, `datetime`) e não cria aresta.
Procurei no diff regenerado do mapa: `preservar_coleta`, `_difere` e
`_instante` **não aparecem em lado nenhum**.

O mapa foi regenerado e commitado (`76c09369`). Das 1024 linhas do diff, só a
entrada de `RELATORIO-LOTE-76.md` é minha; o resto é drift de trabalho alheio
que ninguém tinha regenerado (os HTML do `collection-store` da colheita
a9d037, do commit `0ccefb62`, e ficheiros de `curadoria/`).

Declarar a peça do `.mjs` é de quem o escreveu — **não alarguei o âmbito desta
missão para lhe mexer**.

---

## DÍVIDA REGISTADA, NÃO RESOLVIDA

```
ELIGIBLE_WITHOUT_CONTRACT = 8      (herdada; não tocada — não era precisa)
VEREDITOS T7 COM PERGUNTA T10 = 56 (medidos corrigidos; nenhum seria SIM)
CORRIDA FICA EM «rodando»          o orquestrador não fecha collection_run.
                                   Vale para todas as 389, não só esta.
6 CAMPOS DO MANIFESTO NOT_PRESERVED DATASET_ID · EVIDENCE_PATH ·
                                   OUTPUT_WRITTEN_AT · RAW_EVIDENCE_PATH ·
                                   RAW_EVIDENCE_STATE · SOURCE_VERSION
```

---

## VEREDITO

```
RUN_ADMISSION_SALA_PROVEN = YES
```

Coorte fechada (76, medida, não ajustada) · rede 0 · transformação provada
(76/76 com texto real) · admissão real pela porta canónica (76 julgados, 0
bypass, 0 INSERT à mão) · escrita canónica na Sala (+5) · proveniência completa
· `NEW_FAILURES` 0 · a única falha de medição está declarada acima e **não
altera o número de admitidos**.

⚠️ **Com duas ressalvas declaradas, e nenhuma delas é minha:**

```
SYSTEM_MAP_CHECK = FAIL   P9 num .mjs do commit 42708647, anterior à base.
                          Provado herdado; não toquei em nenhum .mjs.
SUITE            = 1 vermelho  separador de caminho do Windows; provado
                          pré-existente contra o ficheiro da base.
LOCAL == REMOTE  = NÃO MEDIDO  não fiz push; não me foi pedido.
```

Cópias de segurança: `PRE-LOTE76.dump` (pré-escrita) e
`POS-LOTE76-PARCIAL.dump`, em `C:/Users/London1/sintonia-sala-italia/backups/`.

---

## EM PALAVRAS SIMPLES

**Quantos eram mesmo?** 76. O número estava certo, e os 76 ficheiros estavam
todos no disco.

**Porque não estavam no banco?** Porque o programa que os foi buscar nunca fala
com o banco — nunca falou. É como ter duas portarias no mesmo prédio: uma anota
quem entra num caderno de papel, a outra no computador. Eles entraram pela do
caderno. O computador não ficou a saber porque ninguém passou por lá. Não houve
avaria nenhuma.

**Quantos foram transformados em texto?** Os 76. Todos tinham texto de verdade
lá dentro — o mais curto com 1 851 letras, o mais comprido com 11 459.

**Quantos foram aprovados?** 5.

**Quantos estão na Sala agora?** A Sala tinha 56, agora tem 61.

**Porque é que os outros 71 não entraram?** Por uma razão só, e é sempre a
mesma: **não falam do assunto**. O porteiro pede que o texto tenha pelo menos
duas palavras do tema para o aceitar. 47 não tinham nenhuma. 24 tinham pouco de
mais para o porteiro se decidir, e ele disse «não sei» em vez de inventar uma
resposta. Não faltou peça nenhuma, não houve erro, não houve ficheiro
estragado. O porteiro olhou para todos e decidiu.

**Que peça falta?** Nenhuma para fazer este trabalho. Mas encontrei uma peça
**avariada** e arranjei-a: a parte que confere se a linha ficou bem escrita
comparava as horas como se fossem palavras. O banco escreve `18:55:13.64` e o
programa escreve `18:55:13.640` — é o mesmo segundo, mas escrito com um zero a
mais. Por causa desse zero, 7 documentos eram dados como estragados e
desapareciam sem ninguém dar por isso. Agora os 7 são julgados como os outros.
Nenhum deles entrou na Sala — mas antes nem sequer chegavam a ser olhados, e
isso é diferente de serem recusados.

**Houve internet?** Não. Zero. Nada foi buscado outra vez; usei os ficheiros
que já estavam no disco desde ontem à noite.

**A identidade sobreviveu do site até à Sala?** Sim. Para cada um dos 5 que
entraram consigo ir da Sala até ao endereço do site, passo a passo, sem nenhum
elo em falta. E o mais importante: **onde não se sabe, está escrito «não sei»**.
A data em que a notícia aconteceu e o sítio onde aconteceu não estão em lado
nenhum — a fonte não os publica — e ninguém os inventou para o relatório ficar
bonito.

**Uma coisa que fiz mal, e digo-a.** A coleta tinha documentos de dois assuntos
diferentes, e eu fiz a pergunta de um só assunto a todos. 56 documentos ouviram
a pergunta errada. Fui medir o que teria acontecido com a pergunta certa:
**nenhum deles teria entrado na Sala à mesma**. Mudava só quantos ficavam em
«não» e quantos em «não sei». Por isso não voltei a correr tudo — teria enchido
o arquivo com 76 registos repetidos sem ganhar um único documento.
