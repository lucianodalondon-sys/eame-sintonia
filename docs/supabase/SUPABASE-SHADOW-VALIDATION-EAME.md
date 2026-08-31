# VALIDAÇÃO EM SOMBRA — SINTONIA EAME

**Data:** 2026-08-31 · **antes de o V8 consumir produção**

---

## 1 · A PERGUNTA

```
CANONICAL SOURCE OUTPUT   ==   SUPABASE PUBLISHED STATE   ?
```

Não *"tem o mesmo tamanho?"*. **Tem o mesmo significado?**

---

## 2 · CONTAGEM IGUAL NÃO PROVA NADA

O erro que esta validação existe para impedir:

> O freeze do GitHub diz `AO-IT-001` com estado `ATTENTION_CANDIDATE_TEST`.
> O Supabase diz `AO-IT-001` com estado `ATTENTION_READY`.
> **A contagem bate. O produto está errado.**

Um objeto promovido de candidato a pronto por um adapter distraído passaria em qualquer
validação que só contasse linhas — e apareceria na fila de atenção como se tivesse
atravessado os cinco portões.

Por isso a validação é **campo a campo**, e não linha a linha.

---

## 3 · O QUE SE COMPARA, POR FAMÍLIA

| dimensão | o que se verifica |
|---|---|
| **row count** | número de linhas |
| **entity count** | número de entidades distintas — `ROW ≠ ENTITY` |
| **object ids** | o conjunto exato, não o tamanho dele |
| **evidence ids** | o conjunto exato |
| **states** | `attention_state`, `field_state`, `agreement_state`, `content_collection_stage` |
| **dates** | `source_published_at`, `captured_at`, `deadline_date`, `event_at` |
| **relations** | arestas de dependência e relações entre objetos |
| **actions** | `action_type` canônico e a base de evidência |
| **translations** | quais existem e quais não — zero é um resultado a verificar |

**Conjunto exato, não tamanho.** Dois conjuntos de 22 ids podem não ter um id em comum.

---

## 4 · ONDE O RESULTADO FICA

`shadow_validation`, uma linha por verificação:

```
PUBLISH_RUN_ID · FAMILY · CHECK_NAME · EXPECTED · FOUND · PASSED · CHECKED_AT
```

`EXPECTED` e `FOUND` ficam **guardados**, não só o veredito. Um `PASSED = false` sem os dois
valores é um alarme que ninguém consegue investigar.

---

## 5 · FALHA FECHA

```sql
CONSTRAINT publicado_exige_sombra_aprovada
  CHECK ((status <> 'PUBLISHED') OR (shadow_validation_passed = true))
```

**Se qualquer semântica mudar, `PUBLISH = FAIL_CLOSED`.** O banco recusa marcar
`PUBLISHED` sem a sombra aprovada — não depende de disciplina de quem roda o publisher.

E `FAILED_CLOSED` é um estado que se lê: `failed_reason` diz qual família e qual
verificação.

---

## 6 · AS VERIFICAÇÕES QUE JÁ SE SABE ESCREVER

Estas não dependem de rodar a carga para serem definidas:

```
H1  o conjunto de observation_id bate com o freeze
    nenhum phenomenon_case com pareamento PROVED sem pairing_evidence_id

H2  toda deadline_date é futura na data do freeze
    expiry_is_withdrawal = false em 100% das linhas
    nenhum regulatory_deadline_object com max_authorized_action = BUSINESS_DECISION

H3  competitor_product_identity = 36
    attention_object do tipo COMPETITOR_IDENTITY_CHAIN = 0
    nenhuma linha com agreement_state = PROVED e urbole_guard_result = NOT_RUN

H4  toda linha tem array_length(cannot_claim_list) >= 6

H5  field_pressure_reading = 148.964 · count(distinct season) = 23
    nenhuma leitura com n nulo ou n <= 0
    a aresta H5→H1 com SOURCE_DEPENDENCY existe

H6  person_creator e farm_business_entity contados SEPARADOS
    entry_path_event existe e está vazia

H7  issue_expertise com state = PROVED → 0
    nenhuma linha PROVED sem evidence_id

H8  company_local_account = 22, todas em NOT_STARTED
    company_public_content = 0

H9  content_translation = 0
    nenhuma evidence com source_language fora do vocabulário fechado

GERAL  toda evidence alcançável por source_provenance até um source_id
       todo attention_object alcançável por storage_provenance até um commit_sha
       nenhum tipo persistido pertence à lista de aliases do casco
```

---

## 7 · A VERIFICAÇÃO QUE PRECISA RODAR DUAS VEZES

**Idempotência** não se prova numa execução.

```
1  publicar
2  guardar as contagens de todas as tabelas
3  publicar de novo, mesma versão, mesmos freezes
4  comparar
```

Qualquer diferença é **falha**, não "atualização". Reexecutar a mesma versão não pode
duplicar objeto, evidência, evento nem tradução.

---

## 8 · O QUE A SOMBRA NÃO CONSEGUE PEGAR

Honestidade sobre o limite desta validação:

1. **Erro que existe nos dois lados.** Se o freeze estiver errado, a sombra confirma o erro
   com precisão. Ela prova fidelidade da cópia, não verdade do original.
2. **Semântica que ninguém pensou em verificar.** A lista da seção 6 cobre o que já se
   sabe errar. O que ainda não errou não está lá.
3. **Comportamento de leitura.** A sombra compara estado armazenado. Se uma view derivar
   errado, a tabela está certa e a tela mente — por isso `v_convergence_state` e
   `v_attention_readiness` também precisam de teste próprio quando tiverem corpo.

> Item 3 é o mais provável de morder. A validação olha para o banco; o usuário olha para a
> view.
