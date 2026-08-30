# SUPABASE — PRONTIDÃO DO MAPA DE CREATORS

**Data:** 2026-08-30 · **Estado:** **PROPOSTA. Nenhuma tabela criada.**

---

## O QUE FOI VERIFICADO ANTES DE PROPOR

Instrução do dono: *não criar tabela correndo sem antes verificar o schema atual*.
Verificação feita, e o resultado é ele próprio um achado:

| verificação | resultado |
|---|---|
| workflows `supabase-*` registados no GitHub Actions | **5** (`conexao`, `migrate`, `storage`, `raw-roundtrip`, `fichas-adama`) |
| ficheiros desses workflows na árvore do branch **padrão** | **NENHUM** |
| ficheiros `.sql` ou `migration` no repositório | **NENHUM** |
| referência a `supabase` em `scripts/` ou `docs/` | **NENHUMA** |

> Um workflow permanece **registado** no GitHub depois de o ficheiro ser removido. É o que
> se vê aqui: os cinco workflows existem no registo do Actions e **as suas definições não
> estão na árvore atual**.

**Conclusão:** não há, hoje, destino canónico do Supabase visível neste repositório para o
Mapa de Creators. Portanto **não se documenta um contrato existente — propõe-se um mínimo.**

E vale dizer o que isto **não** significa: não significa que o Supabase EAME não exista.
Significa que **este repositório não mostra o schema dele**. Se ele existir noutro lugar, a
proposta abaixo deve ser confrontada com o schema real **antes** de qualquer migração.

---

## A REGRA QUE A PROPOSTA OBEDECE

> **Não criar um segundo dono da pessoa.**

Se o SINTONIA EAME já tiver uma entidade de PESSOA (o universo de sensores do EARLY SIGNAL
tem identidades de pesquisadores), o Mapa de Creators **não** cria outra. Ele acrescenta o
**papel** de canal a uma pessoa que já existe — que é exatamente o que `SENSOR_ROLE_LINK`
faz hoje no JSON, como ponteiro e nunca como fusão.

---

## MIGRAÇÃO MÍNIMA PROPOSTA — 7 entidades

Separadas porque cada uma muda com **frequência diferente** e tem **dono diferente**.
Juntá-las numa tabela só faria uma medição de atividade sobrescrever uma prova de identidade.

| entidade | o que guarda | muda quando |
|---|---|---|
| `creator_entity` | a pessoa OU a empresa · `ACTIVATION_ENTITY_TYPE` · país · região | raramente |
| `public_channel` | plataforma · handle · URL · `HANDLE_EXISTS` · fonte do handle | raramente |
| `crop_proof` | cultura · classe A–D · URL · data · texto · força | a cada nova prova |
| `activity_observation` | `LAST_ACTIVITY_DATE` · posts 30/90d · `AS_OF_DATE` | **a cada medição** |
| `public_contact` | tipo de rota · valor publicado pelo próprio · fonte | raramente |
| `brand_relationship` | marca · `RELATION_TYPE` · `RELATIONSHIP_STATE` · categoria · data | por descoberta |
| `activation_state` | estado derivado · as seis provas · pendências `MISSING_*` | **derivado, nunca digitado** |

### Três colunas que precisam existir em qualquer versão

- **`ACTIVATION_ENTITY_TYPE`** em `creator_entity` — sem ela, pessoa e empresa voltam a
  somar-se, que é o erro que a rodada 4 corrigiu.
- **`AS_OF_DATE`** em `activity_observation` — atividade sem data não é atividade.
- **`SOURCE_URL` + `DECLARATION_TYPE`** em `crop_proof` — a natureza da prova
  (auto-declarada, conteúdo recorrente, produção documentada) é parte da prova.

### O que **não** deve ir para o banco

Nada derivado que possa ser recalculado: `ACTIVATION_STATE`, `AUDIENCE_FIT_FOR_ADAMA` e as
seis provas são **função** das outras tabelas. Persisti-los cria uma segunda verdade que
envelhece em silêncio. Se forem materializados por desempenho, que seja como **view**.

---

## PRÓXIMO PASSO — e ele não é meu

1. Alguém com acesso confirma se existe schema EAME no Supabase e qual é.
2. Se existir entidade de pessoa, esta proposta **reduz-se** a acrescentar papel e canais.
3. Só então uma migração é escrita — contra o schema real, não contra esta proposta.

**Nenhuma tabela foi criada. Nenhuma migração foi executada.**
