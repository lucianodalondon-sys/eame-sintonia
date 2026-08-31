# PLANO DE ROW LEVEL SECURITY — SINTONIA EAME

**Data:** 2026-08-31 · **desenhado, não implementado**

```
RLS_ENABLED_NA_MIGRATION = SIM (todas as 57 tabelas)
POLITICAS_CONCRETAS = entram com a autenticação, na rodada de wiring
```

---

## 1 · POR QUE RLS EM TODAS AS TABELAS, INCLUSIVE AS VAZIAS

Num projeto Supabase, **uma tabela sem RLS fica legível pela chave anônima.** Não é
descuido teórico: é o comportamento padrão.

A migration liga `ROW LEVEL SECURITY` em todas as 57. Sem política, o acesso é negado —
**o padrão seguro é negar e abrir depois**, nunca o contrário.

Isso vale também para as tabelas que nascem vazias (`content_translation`,
`company_public_content`, `entry_path_event`). Uma tabela vazia hoje é uma tabela cheia
depois, e ninguém volta para ligar RLS.

---

## 2 · TRÊS PAPÉIS

| papel | lê | escreve | onde vive |
|---|---|---|---|
| **`publisher_role`** | tudo | inteligência canônica | só no backend, com service role |
| **`portal_reader`** | o que o país dele autoriza | `entry_path_event` e nada mais | servidor do portal |
| **`anon`** | **nada** de inteligência | nada | navegador |

**O usuário do portal não escreve inteligência canônica.** Nem objeto, nem evidência, nem
estado, nem ação. A única escrita que o portal faz é telemetria de rota — e ela não é
inteligência.

---

## 3 · A REGRA QUE NÃO SE NEGOCIA

```
SERVICE_ROLE_KEY nunca vai para o frontend.
```

A cadeia é: **navegador → servidor → Supabase**. O navegador nunca fala direto com o banco
usando chave de serviço.

Isso não é preferência de arquitetura: `SERVICE_ROLE_KEY` ignora RLS por definição. Enviá-la
ao navegador transformaria todo o plano deste documento em decoração.

---

## 4 · ISOLAMENTO POR PAÍS

A lei do produto — *dados de um país nunca aparecem dentro de outro; cruzamentos só na
camada EAME, e apenas nas dimensões declaradas comparáveis* — precisa ser **aplicável no
banco**, não só respeitada na tela.

Toda tabela com coluna `country` pode receber política de país. As principais:

```
attention_object · evidence · geo_anchor · source · registration
company_local_account · field_pressure_series · person · organization
territorial_observation · competitor_product_identity · local_adama_portfolio_context
farm_business_entity · entry_path_event
```

A política concreta entra com a autenticação. O que esta rodada garante é que **a coluna
existe onde precisa existir** — RLS não pode ser adicionada depois se o schema não tiver
por onde filtrar.

---

## 5 · MULTI-TENANT DEPOIS, SEM REFAZER

Hoje o piloto é EAME e não há cliente múltiplo. **Não implementar autenticação complexa
agora.**

Mas o schema não pode impedir depois. O caminho previsto:

1. adicionar `tenant_id` às tabelas raiz (`attention_object`, `evidence`, `source`);
2. as tabelas filhas herdam por chave estrangeira — não precisam da coluna;
3. as políticas passam a filtrar por `tenant_id` **e** `country`.

**Por que funciona sem refazer:** as filhas têm PK que referencia a raiz. `phenomenon_case`
não precisa saber de tenant: quem sabe é `attention_object`, e a filha só existe se a raiz
existir.

---

## 6 · O QUE FICA FORA DO BANCO

`entry_path_event` é a única tabela de telemetria, e ela guarda o mínimo:

```
entry_path · attention_object_id · crop_term_id · region · country · occurred_at
```

**Sem `user_id`, sem sessão, sem IP.** Só a rota, o recorte e a hora.

Isso responde a pergunta que a arbitragem deixou em aberto — *o Marketing chega ao Creator
pela busca ou pelo objeto?* — sem construir analytics invasivo e sem criar PII que depois
precisaria de tratamento GDPR próprio.

> Coletar menos é a decisão mais difícil de reverter na direção certa. Um campo que não
> existe não vaza.

---

## 7 · GDPR DENTRO DO SCHEMA

`person.gdpr_treatment_state` tem quatro estados: `NOT_STARTED · IN_REVIEW · CLEARED ·
RESTRICTED`.

E há um check em `field_voice_observation`:

```sql
CONSTRAINT pessoa_identificada_exige_gdpr_tratado
  CHECK ((entity_kind <> 'PERSON_CREATOR') OR (gdpr_treatment_state <> 'NOT_STARTED'))
```

**Observação de pessoa identificada com GDPR não iniciado é recusada na gravação** — não
depende de alguém lembrar de filtrar na tela.

`farm_business_entity` fica de fora dessa exigência de propósito: negócio não é pessoa
física, e tratá-lo como se fosse diluiria a proteção de quem precisa dela.

---

## 8 · O QUE ESTE PLANO AINDA NÃO RESOLVE

1. **As políticas concretas não estão escritas.** Escrever `CREATE POLICY` sem saber como a
   autenticação vai identificar o país do usuário produziria política que não roda.
2. **Não há instância.** Este plano não foi exercido contra um banco real.
3. **Auditoria de acesso** — quem leu o quê — não está desenhada. Entra quando houver
   usuário real.
