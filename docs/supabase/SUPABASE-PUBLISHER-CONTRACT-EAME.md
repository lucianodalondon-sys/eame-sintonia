# CONTRATO DO PUBLISHER — SINTONIA EAME

**Data:** 2026-08-31 · plano em `data/supabase/SUPABASE-PUBLISH-MAP.json`

```
FIRST_LOAD_EXECUTED = NO     COLLECTION_EXECUTED = NO     MIGRATION_APPLIED = NO
```

---

## 1 · OS SEIS PASSOS

```
CANONICAL FREEZE → VALIDATE → TRANSFORM → UPSERT → VALIDATE SHADOW → PUBLISH
```

| passo | o que faz | falha fecha? |
|---|---|---|
| **1 · FREEZE** | resolve cada commit fixo e confirma que o blob existe | sim |
| **2 · VALIDATE** | aplica os guards da mangueira ao artefato de entrada | **sim** |
| **3 · TRANSFORM** | adapta para o payload **canônico**, nunca para o alias do casco | sim |
| **4 · UPSERT** | grava por chave natural, idempotente | sim |
| **5 · SHADOW** | compara o publicado com o freeze, campo a campo | **sim** |
| **6 · PUBLISH** | marca `PUBLISHED` só se a sombra passou inteira | — |

**Guard reprovado é `FAIL_CLOSED`, nunca linha degradada.** Não existe "publica o que deu"
— publicar metade de uma família produz um estado que ninguém consegue interpretar.

E há um check no banco que impede o atalho:

```sql
CONSTRAINT publicado_exige_sombra_aprovada
  CHECK ((status <> 'PUBLISHED') OR (shadow_validation_passed = true))
```

---

## 2 · A LEI DE LEITURA

**Toda leitura é por `COMMIT_SHA` fixo.** Uma branch se move e responde diferente a cada
hora sem ninguém ter mudado nada.

Hoje há **uma entrada fora da lei**: H2 aponta para `origin/…italy-pilot`, que é uma
branch. Resolver o SHA e registrá-lo no mapa **antes** da primeira carga. Está declarado
como `SOURCE_COMMIT = RESOLVER_ANTES_DA_CARGA` — não escondido.

---

## 3 · IDEMPOTÊNCIA

Reexecutar a mesma versão **não duplica objeto, evidência, evento nem tradução**.

O mecanismo é chave natural estável por família — nunca uma chave gerada na carga:

| família | chave natural |
|---|---|
| `attention_object` | país + tipo + chave do tipo |
| `attention_object_representation` | `(attention_object_id, language)` |
| `evidence` | `SOURCE_ID` + snapshot + offset da passagem |
| `object_event` | `(attention_object_id, event_type, event_at, source_id)` |
| `content_translation` | `(canonical_entity_id, translation_language)` |
| `field_pressure_reading` | `(series_id, season, province)` |
| `convergence_leg` | `(proposition_id, signal_family, evidence_id)` |

> **Proibido usar título traduzido como chave.** O título muda por idioma e por revisão;
> a chave não pode. Um objeto cujo id dependesse do título viraria cinco objetos ao ganhar
> cinco idiomas — exatamente o que a regra congelada proíbe.

**Teste de idempotência:** rodar a mesma publicação duas vezes e comparar contagens de
todas as tabelas. Qualquer diferença é falha, não "atualização".

---

## 4 · O QUE O PUBLISHER DERIVA E O QUE ELE COPIA

**Deriva** (calcula na hora, nunca lê do artefato):

- `is_publishable` em `action` — `BUSINESS_DECISION` com zero linhas em `action_evidence`
  não é publicável. A regra se verifica **contando linhas**, não confiando num campo.
- estado de readiness — recalculado dos cinco requisitos, nunca copiado.
- contagem de famílias independentes — derivada das pernas, nunca armazenada.

**Copia** (preserva exatamente como a fonte declarou):

- `status_as_declared_by_source` — nunca reinterpretado.
- `original_text` e `source_language` — sem edição.
- `cannot_claim_list` de H4 — os sete "não pode afirmar" viajam com a linha.

---

## 5 · VERSIONAMENTO

Cada publicação registra, em `publish_run`:

```
PUBLISH_RUN_ID · PIPELINE_VERSION · SCHEMA_VERSION · PUBLISHED_AT · STATUS
SHADOW_VALIDATION_PASSED · FAILED_REASON
```

E em `publish_run_freeze`, N:N, os commits que a alimentaram:

```
REPOSITORY · PATH · COMMIT_SHA · HOSE_ID
```

Isso responde as duas perguntas que um banco sem história não responde:

> *Qual versão do pipeline colocou este objeto aqui?*
> *Com quais freezes?*

A view `v_publish_provenance` faz o caminho completo: objeto → execução → freeze → commit.

---

## 6 · ORDEM DA PRIMEIRA CARGA

```
1  ontology_term + ontology_term_label + source    nada existe sem termo e sem fonte
2  H9 content_entity                               guardrail transversal, ANTES do texto
3  H2 registro e prazo                             único objeto com decisão defensável
4  H1 territorial                                  único PHENOMENON_CASE com chave completa
5  H5 série + aresta de dependência para H1
6  H3 identidade + H4 atividade paga + aresta de derivação
7  H7 pessoas e publicações, com o portão de expertise
8  H6 creators, com entry_path_event vazia
9  H8 contas, todas em NOT_STARTED
```

**Por que essa ordem:** as arestas de dependência só podem ser gravadas depois das duas
pontas existirem. E H9 entra cedo porque nenhum texto deve chegar ao banco sem língua
declarada — mesmo que a língua declarada seja `UNKNOWN`.

---

## 7 · O QUE O PUBLISHER NUNCA FAZ

```
não coleta                       a coleta é outra etapa, com outra autorização
não traduz                       tradução exige decisão humana e proveniência própria
não inventa contagem             onde não pôde medir, escreve NOT_MEASURED
não soma linha com entidade      ROW ≠ ENTITY, e as duas viajam juntas
não escreve o alias do casco     traduz na fronteira, lendo ui_alias
não publica metade de família    guard reprovado fecha a execução inteira
```
