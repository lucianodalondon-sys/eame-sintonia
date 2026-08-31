# MODELO DE PROVENIÊNCIA — SUPABASE SINTONIA EAME

**Data:** 2026-08-31

---

## 1 · A CADEIA QUE PRECISA FECHAR

```
OBJECT → CLAIM/OBSERVATION → EVIDENCE → SOURCE → SOURCE SNAPSHOT
       → PIPELINE VERSION/COMMIT → ORIGINAL
```

Toda inteligência publicada precisa percorrer essa cadeia inteira. A view
`v_publish_provenance` faz o caminho numa consulta.

---

## 2 · DUAS PROVENIÊNCIAS, E ELAS NÃO SE SUBSTITUEM

Esta é a decisão mais importante deste documento.

```
source_provenance     de onde a EVIDÊNCIA veio no mundo
storage_provenance    de onde a LINHA foi lida ou entregue
```

**Por que separadas:** quando o dado já estiver no Supabase, `SOURCE_BACKEND = SUPABASE`
descreveria a **entrega**. Se fosse o único campo, ele apagaria a origem externa real — e
o portal passaria a dizer que a fonte de um boletim andaluz é "Supabase".

| | `source_provenance` | `storage_provenance` |
|---|---|---|
| responde | *de onde veio o fato?* | *de onde li esta linha?* |
| aponta para | `source`, `source_snapshot`, `original_ref` | GitHub ou Supabase |
| muda quando | nunca — o fato tem uma origem | a cada republicação |

**Não perder a origem externa real** é a regra. `storage_provenance` é transporte;
`source_provenance` é história.

---

## 3 · O ENVELOPE DE ARMAZENAMENTO

Um discriminador, dois conjuntos que **nunca se misturam**:

```
SOURCE_BACKEND = GITHUB
  REPOSITORY · PATH · COMMIT_SHA · HASH · SOURCE_ID · AS_OF_DATE

SOURCE_BACKEND = SUPABASE
  SCHEMA · TABLE_OR_VIEW · PRIMARY_KEY · SNAPSHOT_ID · CAPTURED_AT · SOURCE_ID · AS_OF_DATE
```

Três checks garantem no banco:

```sql
github_exige_commit_e_caminho    -- GITHUB sem repository/path/commit_sha é recusado
supabase_exige_tabela_e_chave    -- SUPABASE sem schema/table/pk é recusado
backends_nao_se_misturam         -- repository E table_or_view preenchidos juntos é recusado
```

O terceiro é o que impede a linha híbrida — aquela que parece completa e não é nenhuma das
duas.

---

## 4 · UMA UI, DOIS BACKENDS

**Não existe "tela do GitHub" e "tela do Supabase".** A view `v_evidence_drawer` devolve o
mesmo formato nos dois casos; muda o rótulo do campo, não o componente.

O casco recebe **entidade canônica já resolvida**. Ele não sabe — e não precisa saber — de
onde veio.

---

## 5 · LEITURA SEMPRE POR COMMIT FIXO

```
PINNED_READ_RULE: leitura GitHub é sempre por COMMIT_SHA
```

Uma branch se move e responde diferente a cada hora sem ninguém ter mudado nada. Um
dashboard que lê uma branch é um dashboard que muda sozinho.

**Uma exceção declarada hoje:** H2 aponta para `origin/…italy-pilot`. Está registrado no
mapa como `SOURCE_COMMIT = RESOLVER_ANTES_DA_CARGA` — não corrigido em silêncio, e não
escondido.

---

## 6 · EVIDÊNCIA COMPARTILHADA, NUNCA COPIADA

Uma evidência é usada por:

```
um objeto · uma perna de convergência · uma base de ação
um evento de timeline · uma relação entre objetos
```

Todas as cinco apontam para a **mesma linha** em `evidence`. Duplicar fisicamente por uso
criaria cinco verdades que divergem na primeira correção.

`EVIDENCE_ID` é estável: deriva de `SOURCE_ID` + snapshot + offset da passagem. Reexecutar
a publicação não gera um id novo.

**O que `evidence` preserva:**

```
SOURCE_ID · SOURCE_LOCATION · FACT_LOCATION · SOURCE_PUBLISHED_AT · CAPTURED_AT
EVIDENCE_LEVEL · ORIGINAL_TEXT · SOURCE_LANGUAGE
DOCUMENT_EXCERPT · PASSAGE_START/END · SOURCE_URL
```

`SOURCE_LOCATION` e `FACT_LOCATION` são campos distintos, e há razão: uma publicação
francesa pode descrever um fato espanhol, e isso nunca move o fato de país.

Os offsets andam em par — há check para isso. Meio offset não localiza nada.

---

## 7 · OS CINCO RELÓGIOS DA FONTE

`source_clock` guarda cinco coisas que costumam ser confundidas numa só:

```
SOURCE_STATUS                 acesso, licença e rota — nunca agregado num número
LATEST_SOURCE_PUBLICATION     data da versão na origem
LATEST_CAPTURE                quando o portal capturou
OBSERVATION_AGE_DAYS          idade do FATO observado
PIPELINE_LATENCY              o atraso do nosso cano
```

**Idade da observação não é latência de pipeline.** Fundir as duas já foi um erro do
produto.

E há um check contra o zero falso:

```sql
CONSTRAINT latencia_sem_medicao_e_nula
  CHECK ((pipeline_latency_state = 'PROVED') OR (pipeline_latency_seconds IS NULL))
```

**Sem instrumentação não existe zero.** Latência só ganha valor quando houver duas capturas
e o estado for `PROVED`; até lá, `NOT_MEASURED` com o campo nulo.

---

## 8 · SEGREDO NENHUM ATRAVESSA

```
NUNCA no frontend: SERVICE_ROLE_KEY · secret · token · senha · chave privada
```

O portal fala com um servidor; o servidor fala com o Supabase. `storage_provenance` guarda
**referências** — repositório, caminho, commit, tabela, chave — nunca credenciais.

Há teste que varre os bytes do casco procurando segredo. Hoje ele não carrega nenhum.
