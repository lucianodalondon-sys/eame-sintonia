# MISSÃO P0 — CIRURGIA DE IDENTIDADE DA ENTREGA NA SALA

STATUS: DESPACHADA PELO COORDENADOR
BANCADA: `sala-identity-v1`
BRANCH: `sala-identity-v1`
BASE_HEAD: `3c0ad4d7a05aa82bd4e4c87fc2a3b25451a6fb13` (tip de `big-collection-release-v1`)
PRIORIDADE: P0

---

## ESTADO MEDIDO PELO COORDENADOR ANTES DO DESPACHO

Não é briefing: é medição. Mesmo assim, **remede tudo**. Nada aqui substitui a tua
própria medição.

```text
REPO                      lucianodalondon-sys/eame-sintonia (Orca id 21fd565e-...)
ORIGIN/MAIN               f437ff1140fa97484ca9695b341fbe9ca0a9f050 (2026-09-12)
BASE ESCOLHIDA            big-collection-release-v1 @ 3c0ad4d7 (árvore que produziu a BCR)
WORKTREES TOTAIS          86
ESCRITOR ATIVO MEDIDO     crop-e2e-v1 (agente a pensar, tail a mudar) — branch crop-e2e-v1
ESCRITOR OCIOSO           big-collection-release-v1 (sessão parada, worktree limpa)
ESCRITOR AMBÍGUO          source-curator-integration-v1 (status running, tail estático)
COLISÃO DE FICHEIROS      NENHUMA com o escopo desta missão
```

Colisão verificada ficheiro a ficheiro:

- `crop-e2e-v1` toca `provas/o_piloto_da_sala.py`, `data/derivados/*`, `docs/operacao/PILOTO-DA-SALA-*`, `system-map/data/*`. **Não toca** `admissao/sala_de_espera.py`, `orquestrador/orquestrador.py`, nem `supabase/migrations/*`.
- `source-curator-integration-v1` toca `orquestrador/orquestrador.py` (bloco `exigir_ready`), `curadoria/*`, `orquestrador/fontes_prontas.py`. **Não toca** `admissao/sala_de_espera.py` nem a linha 574 do orquestrador.

**Regra dura desta bancada:** se a correção tiver de tocar `orquestrador/orquestrador.py`,
faz a menor mudança possível e declara-a explicitamente como zona de fronteira com a
missão `source-curator-integration-v1`. Não reformates o ficheiro. Não toques
`curadoria/`, `orquestrador/fontes_prontas.py`, `provas/o_piloto_da_sala.py` nem
`data/derivados/`.

---

## PONTEIROS MEDIDOS (ponto de partida, a confirmar por ti)

```text
orquestrador/orquestrador.py:574
    item.update({"id": "derived:%s" % estruturado["DERIVED_ARTIFACT_ID"], ...

admissao/sala_de_espera.py
    ITEM_ID entra na Sala; chave primária medida é (run_id, ordem), NÃO (run_id, item_id)

supabase/migrations/031_a_sala_de_espera_ganha_dono_duravel.sql
    a própria migration já escreveu, em 2026:
      "ITEM_ID NÃO É IDENTIDADE GARANTIDA DENTRO DA CORRIDA"
      admissao.decidir() -> ITEM_ID = str(item.get("id") or item.get("url") or "?")
```

Isto **levanta** a hipótese; não a prova. A tua missão é provar ou refutar.

---

## OBJETIVO ÚNICO

Provar qual é a identidade canónica de uma entrega na Sala de Espera e reconciliar os
17 itens atribuídos à BCR, **sem perder dados e sem fabricar proveniência**.

Pergunta central:

> A Sala sabe distinguir corretamente uma nova entrega/observação de um artefato
> derivado já existente?

---

## FASE 0 — REMEDIR (obrigatório, antes de tudo)

```text
REPO =
BRANCH =
HEAD =
REMOTE_HEAD =
WORKTREE =
DIRTY =
SALA_TOTAL =
ACTIVE_WRITERS =
```

`SALA_TOTAL` mede-se no banco, com o mesmo cliente PostgreSQL que o runtime usa.
**Se o banco não estiver alcançável desta bancada:** não simules, não uses fixture como
se fosse o banco, não inventes o número. Declara

```text
DB_REACHABLE = NO
SALA_TOTAL = NOT_MEASURABLE
```

e reporta imediatamente ao coordenador antes de continuar para a FASE 1. Fases de
leitura de código (3, 4, 9) podem prosseguir; fases que dependem das linhas reais
(1, 2, 6) ficam `BLOCKED`.

---

## FASE 1 — CENSO DOS 17

Identificar os 17 itens atribuídos à BCR pela fronteira temporal/canónica **provada**
(não por suposição de janela). Para cada um:

```text
SALA_ROW_ID · ITEM_ID · ADMISSION_ID · RUN_ID · OBSERVATION_ID
RAW_ASSET_ID · DERIVED_ARTIFACT_ID · SOURCE_ID · CONTENT_SHA
CREATED_AT · ADMITTED_AT
```

Não reconstruir identidade apenas por `item_id`.

## FASE 2 — OS 5 SUSPEITOS

Para cada um dos 5 que apontam para derivados de corridas anteriores à BCR, provar:

- qual RUN produziu a observação;
- qual OBSERVATION foi admitida;
- qual DERIVED foi utilizado;
- se o DERIVED foi reutilizado de corrida anterior;
- se essa reutilização é permitida;
- se a Sala preservou ou perdeu a identidade da nova entrega.

Classificar **individualmente**, sem inferência generosa:

```text
VALID_REUSE · IDENTITY_COLLISION · BROKEN_PROVENANCE · AUDIT_FALSE_POSITIVE · UNKNOWN
```

## FASE 3 — IDENTIDADES CANÓNICAS

Ler migrations, leis e owners atuais. Responder:

```text
WHAT_IDENTIFIES_STORAGE_OBJECT =
WHAT_IDENTIFIES_CONTENT =
WHAT_IDENTIFIES_OBSERVATION =
WHAT_IDENTIFIES_ADMISSION =
WHAT_IDENTIFIES_WAITING_ROOM_DELIVERY =
```

Preservar: `RUN ≠ OBSERVATION ≠ CONTENT ≠ STORAGE OBJECT`.
SHA256 identifica bytes. `storage_path` é endereço. DERIVED_ARTIFACT **não** vira
automaticamente identidade de nova observação/entrega.
Não criar segunda ontologia se já existir owner canónico.

## FASE 4 — ITEM_ID

```text
ITEM_ID_CURRENT_SEMANTICS =
ITEM_ID_ACTUAL_USAGE =
ITEM_ID_IS_UNIQUE_FOR_DELIVERY =
```

Se `item_id = derived:<id>` for semanticamente incorreto para identidade de entrega,
corrigir no owner apropriado com a **menor mudança possível**.
NÃO usar SHA como fallback. NÃO usar `storage_path` como identidade.

## FASE 5 — IDEMPOTÊNCIA CORRETA

Provar dois casos, que **têm de coexistir**:

- CASO A — mesma admissão / retry → NÃO cria segunda entrega.
- CASO B — nova RUN / nova observação legítima sobre conteúdo já conhecido → preserva
  nova identidade de ocorrência sem duplicar conteúdo/storage desnecessariamente.

## FASE 6 — RECONCILIAR OS 17

Só depois do modelo estar provado. Cada entrega válida aponta para RUN, OBSERVATION,
ADMISSION, DERIVED e SOURCE corretos. Não alterar conteúdo. Não apagar linha
silenciosamente. Colisão histórica: preservar evidência anterior e registar a correção.

## FASE 7 — NÃO TOCAR NOS 41 DERIVADOS

Outra missão. Não restaurar, não recoletar, não fabricar, não procurar raiz histórica,
não misturar. Apenas garantir que a identidade da Sala não depende de fingir que esses
artefatos existem.

## FASE 8 — CONSUMIDOR INCREMENTAL

NÃO rodar Intelligence. Apenas provar que um consumidor incremental, após esta correção,
distingue JÁ PROCESSADO de NOVA ENTREGA REAL sem depender apenas de `derived_id`.

```text
SAFE_FOR_INCREMENTAL_CONSUMER = YES/NO
```

## FASE 9 — FUTURO `SALA_ITEM_ADMITTED`

NÃO implementar evento. Apenas provar que identidade deve viajar nele:

```text
FUTURE_EVENT_ENTITY_ID =
FUTURE_IDEMPOTENCY_KEY =
```

Basear no modelo canónico, não em conveniência técnica.

## FASE 10 — TESTES OBRIGATÓRIOS

1. retry da mesma admissão não duplica entrega;
2. nova observação sobre mesmos bytes preserva identidade nova;
3. reutilizar DERIVED não rouba proveniência da nova observação;
4. SHA nunca vira observation id;
5. `derived_id` não substitui delivery/admission identity indevidamente;
6. consumidor incremental não confunde conteúdo velho com entrega nova;
7. os 29 itens anteriores permanecem;
8. nenhuma linha legítima da BCR desaparece.

```text
NEW_FAILURES =
```

Distinguir **obrigatoriamente** `NEW_FAILURES = 0` de `ALL_GATES_GREEN = YES/NO`.
A auditoria já mostrou dívida histórica P5 (control-plane). **Não mascarar.**
Baseline compara nomes de falhas na mesma árvore e no mesmo ambiente.

## SYSTEM MAP

Se a correção alterar identidade ou ligação arquitetural real: regenerar pelo fluxo
canónico completo. Se não alterar: não gerar churn.

```text
SYSTEM_MAP_CHECK =
```

Não usar `SYSTEM_MAP_CHECK` sozinho como prova de runtime.

---

## ENTREGA OBRIGATÓRIA

```text
INITIAL_HEAD =
FINAL_HEAD =
REMOTE_HEAD =
WORKTREE_CLEAN =

SALA_BEFORE =
SALA_AFTER =

BCR_ROWS_AUDITED = 17
BCR_ROWS_VALID =
BCR_ROWS_IDENTITY_COLLISION =
BCR_ROWS_UNKNOWN =

SUSPECTED_5_VALID =
SUSPECTED_5_BROKEN =

CURRENT_ITEM_ID_SEMANTICS =
CANONICAL_DELIVERY_IDENTITY =

PROVENANCE_RECONCILED =

SAFE_FOR_INCREMENTAL_CONSUMER =
SAFE_FOR_SALA_ITEM_ADMITTED_EVENT =

DATA_DELETED = 0
NEW_COLLECTION_RUNS = 0
NETWORK_REQUESTS = 0
PAID_USD = 0

NEW_FAILURES =
ALL_GATES_GREEN =
SYSTEM_MAP_CHECK =
KNOW_HOW_DELTA =
```

## EM PALAVRAS SIMPLES (secção obrigatória no fim)

O dono do projeto não é engenheiro. Explica, sem jargão:

1. por que os 5 apontavam para derivados antigos;
2. se isso era reutilização correta ou identidade errada;
3. qual é a identidade correta de algo que entra na Sala;
4. se os 17 continuam a ser 17 entregas legítimas;
5. se a Intelligence conseguirá distinguir item velho de entrega nova;
6. se já é seguro criar futuramente `SALA_ITEM_ADMITTED`.

---

## HARD STOP

NÃO: rodar Collection · corrigir os 41 derivados · corrigir os 289 NÃO_SEI ·
corrigir P5 · mexer em Source Curator (`curadoria/`, `fontes_prontas.py`) ·
mexer em Intelligence · construir event bus · mexer no Portal ·
tocar `main` · tocar outras worktrees.

FOCO ÚNICO: **A SALA PRECISA DE SABER QUEM É CADA ENTREGA.**

Sem prova suficiente: `NÃO SEI / PRECISA MEDIR`. Nunca converter inferência em facto.
