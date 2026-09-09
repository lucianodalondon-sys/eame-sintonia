# PILOTO DE COLETA RECORRENTE — ITÁLIA V1

**Data:** 2026-09-07 · **Branch:** `claude/italy-recurrent-source-pilot-v1`
**Base:** `claude/italy-source-contracts-v1` @ `9726ddc`

A pergunta desta missão não era descobrir fontes. Era: **o SINTONIA consegue voltar amanhã,
reconhecer o que já viu, capturar só o que é novo, preservar versões e perceber quebra — sem
transformar ausência ou falha em dado?**

Não há agendamento. Nenhum cron, timer, action ou daemon foi criado.

---

## 0 · Uma lei minha que estava errada, corrigida antes do piloto

Eu havia escrito nos contratos: *"hash repetido = DEGRADED / fonte parada"*. **Perigoso.**

Uma fonte semanal consultada duas vezes no mesmo dia **deve** devolver o mesmo documento.
Isso é o comportamento correto, não uma falha.

```
SAME_HASH  ≠  DEGRADED
NO_CHANGE  ≠  FAILURE
```

Atraso só existe quando houver **as quatro coisas juntas**: `EXPECTED_UPDATE` +
`DEADLINE PROVADA` + `DEADLINE VENCIDA` + `SEM NOVA VERSÃO`.

Estados corretos: `NO_CHANGE` · `EXPECTED_NO_CHANGE` · `UPDATE_DUE` · `OVERDUE_UPDATE` ·
`CADENCE_UNKNOWN`.

---

## 1 · As leis que o coletor obedece

```
CAPTURE            ≠  DOCUMENT               uma execução pode ver o mesmo doc 10x
DOCUMENT_ID        ≠  BYTE_ID                identidade semântica ≠ SHA256
SAME_URL           ≠  SAME_DOCUMENT          URL fixa carrega versões diferentes
SAME_HASH          ≠  DEGRADED
NO_CHANGE          ≠  FAILURE
NEW_HASH           ≠  NEW_SEMANTIC_FACT      byte mudou não é fato agronômico novo
MOVING_WINDOW      ≠  NEW_DATASET_EVERY_DAY
FIRST_RUN          =  BASELINE
SOURCE_HEALTH      ≠  SOURCE_VERDICT
PARSER_FAILURE MUST NOT DESTROY CAPTURED_RAW
```

**Ordem obrigatória, especialmente para as `FORWARD_ONLY`:**

```
DOWNLOAD → VALIDAÇÃO DE BYTES → SHA256 → RAW PRESERVADO → MANIFESTO → PARSE → ANÁLISE
```

Se o parser quebrar depois, o RAW já está salvo.

---

## 2 · Os quatro casos de versionamento

| caso | condição | resultado | guarda bytes? |
|---|---|---|---|
| **A** | mesmo `DOCUMENT_ID`, mesmo SHA | `SEEN_AGAIN` | **não** — só nova observação |
| **B** | mesmo `DOCUMENT_ID`, SHA novo | `DOCUMENT_CHANGED_IN_PLACE` | **sim**, nova versão. Nunca sobrescreve |
| **C** | `DOCUMENT_ID` novo | `NEW_DOCUMENT` (ou `BASELINE_DOCUMENT` na 1ª) | sim |
| **D** | `DOCUMENT_ID` novo, SHA já visto | `SEMANTIC_ID_CHANGED_SAME_BYTES` | sim, e preserva a relação — **não** decide sozinho que é duplicado |

---

## 3 · O ledger

`data/collection-ledger/italy/observations.ndjson` — append-only, é **o índice explícito**.
O histórico nunca é reconstruído lendo nome de arquivo.

`data/collection-ledger/italy/runs.ndjson` — uma linha por execução, com `RUN_ID`,
`VPN_COUNTRY`, `EGRESS_IP`, `GIT_HEAD`, versão do coletor e do contrato, e os contadores.

RAW imutável em `data/collection-store/italy/{SOURCE_ID}/{DOCUMENT_ID}/{VERSION_ID}/`.

---

## 4 · Três bugs meus que a primeira execução expôs

A primeira tentativa deu **3 FAILED**. Nenhum era da fonte:

| fonte | o que eu fiz de errado |
|---|---|
| Campania | os `href` do índice são **relativos** (`pdf/SA-02-09.pdf`); meu regex exigia caminho absoluto |
| APOL | `pdftotext 4.06` **não aceita stdin**; era preciso gravar um temporário |
| Puglia | **o índice de `agrometeopuglia.it` é JavaScript** — o `curl` não vê os links, embora os PDFs baixem |

O caso da Puglia é um achado, não um bug: o índice exige navegador, os documentos não.
O coletor cai para a **rota previsível que o contrato já documentava** e grava
`DISCOVERY_DEGRADED = INDEX_REQUIRES_BROWSER` no ledger. **Não é chute silencioso.**

E o mais importante: nas três, o coletor **recusou-se a inventar**. Índice vazio virou
`EMPTY_LIST → FAILED`, nunca "zero documentos".

---

## 5 · Proposta de operação — ENTREGUE, NÃO ATIVADA

Preservação e análise são cadências **diferentes**. Para as `FORWARD_ONLY` faz sentido
capturar todo dia e analisar toda semana: o que não for capturado hoje some.

| fonte | `PRESERVATION_CADENCE` | `ANALYSIS_CADENCE` | por quê |
|---|---|---|---|
| `IT-T3-005` Terre dell'Etruria | **diária** | semanal | `FORWARD_ONLY`. Uma edição por vez, sem arquivo. Se perder a semana, os 139 pontos somem |
| `IT-T2-002` ARPAV (32 zonas) | **diária** | semanal | `FORWARD_ONLY`. Nome fixo, conteúdo sobrescrito. Zonas publicam em dias diferentes |
| `IT-T2-004` SIAS Sicília | **diária** | semanal | `FORWARD_ONLY`. Janela móvel de 11 dias; perder 11 dias seguidos é perder tudo |
| `IT-T3-002` Campania | semanal (2×/semana na temporada) | semanal | cadência 7D **provada**; tem arquivo, dá para buscar depois |
| `IT-T3-010` APOL Lecce | semanal (2×/semana) | semanal | 7D **provado**; tem arquivo de duas temporadas |
| `IT-T3-008` ARIF Puglia | semanal (2×/semana) | semanal | 7D **provado**; sai às quartas |
| `IT-T4-001` Ministero | semanal | mensal | registro regulatório; o nome do arquivo carrega a data. Só baixar se a versão mudar |

**Por que 2× por semana e não 1× nas de cadência provada:** publicar às quartas é o padrão
observado, não uma garantia. Duas passadas dão folga sem custo real — `SEEN_AGAIN` não baixa
nada.

**Nenhuma cadência foi inventada.** Onde o contrato não provou, `EXPECTED_NEXT_UPDATE = UNKNOWN`
e a fonte **não pode ser acusada de atraso**.

---

## 6 · Se não coletarmos hoje

Três fontes perdem o documento para sempre: `IT-T3-005`, `IT-T2-002`, `IT-T2-004`.
As quatro restantes têm arquivo e podem ser buscadas depois.

Detectar a quebra **não é** recuperar o documento. Para as três `FORWARD_ONLY`, a preservação
tem de vir antes de qualquer análise — e é exatamente essa a ordem do coletor.
