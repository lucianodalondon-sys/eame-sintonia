# ARQUITETURA CANÔNICA DO SUPABASE — SINTONIA EAME

**Data:** 2026-08-31 · `SCHEMA_VERSION = 0.1.0-draft`

```
MIGRATION_APPLIED = NO      REAL_DATA_PUBLISHED = NO      V8_WIRED = NO
COLLECTION_EXECUTED = NO    FROZEN_INTELLIGENCE_CHANGED = NO
```

> Esta rodada **desenha e escreve** a camada operacional. Não aplica migration, não
> publica dado, não liga o casco.

---

## 0 · A DIVISÃO DE TRABALHO

```
FONTES → COLETA → RÉGUAS/GUARDS → INTELIGÊNCIA CANÔNICA VALIDADA
       → PUBLISHER → SUPABASE → API/SERVER → V8/VERCEL
```

| | **GitHub** | **Supabase** |
|---|---|---|
| é | engenharia, prova, código, réguas, ledgers, freezes, snapshots, commits | camada operacional de consumo |
| responde | *como chegamos a isto?* | *o que mostrar agora?* |
| muda | por commit revisado | por publicação idempotente |

**O V8 deixa de precisar ler JSON de branch do GitHub.** Isso é o ganho: hoje uma tela
que lê uma branch responde diferente a cada hora sem ninguém ter mudado nada.

---

## 1 · O QUE MANDA NO NOME

**O casco `index (11)` é consumidor, não autoridade ontológica.**

Ele usa oito nomes divergentes do contrato. Nenhum deles entra no banco:

```
TERRITORIAL_ATTENTION_OBJECT · PAID_ACTIVITY_EVIDENCE · LONGITUDINAL_FIELD_SERIES
ISSUE_EXPERT · COMPANY_PUBLIC_ACCOUNT · MULTILINGUAL_CONTENT_REPRESENTATION
REGULATORY_DEADLINE (como payload de H2) · COMPETITOR_IDENTITY_CHAIN (como payload de H3)
```

Os dois últimos são a armadilha mais fina: pegaram o **`OBJECT_TYPE`** e o usaram como
**`CANONICAL_PAYLOAD_TYPE`**. `REGULATORY_DEADLINE` é o tipo do objeto de atenção;
`REGISTRATION_DEADLINE` é o que a mangueira H2 carrega. Se o banco aceitasse a confusão,
ela viraria permanente.

Os aliases existem, declarados, na tabela **`ui_alias`** — o único lugar do banco onde
esses oito nomes aparecem. O adapter traduz na fronteira; o banco nunca aprende o alias.

> **Não desenhar o banco para compensar erro de casco.** Quando o casco corrigir, a
> tradução vira identidade e `ui_alias` fica só como registro do que já foi divergente.

---

## 2 · UM OBJETO, VÁRIAS REPRESENTAÇÕES

Regra congelada, e o schema a torna **impossível de violar**:

```
attention_object                 ← a verdade estruturada, UMA vez
attention_object_representation  ← o texto, por idioma
```

A chave de `attention_object` é `attention_object_id`, **neutra de idioma**. Não existe
coluna de idioma nessa tabela. `AO-001-PT` e `AO-001-EN` não são representáveis: teriam de
ser duas linhas com ids diferentes, e a chave natural do publisher deriva de país + tipo +
chave do tipo, nunca do título.

**O que NÃO se duplica por idioma:** ids, datas, números, países, culturas, problemas,
estados, guards, relações e tipos de ação. Cinco cópias de uma data são cinco chances de
divergir.

**O que se representa por idioma:** título, síntese, interpretação, razão da atenção, o que
sabemos, o que não sabemos, texto da ação.

**O que nunca sofre tradução:** `evidence.original_text`. Fica na língua da fonte, sempre,
fora da cadeia de fallback.

---

## 3 · QUATRO TIPOS, QUATRO TABELAS FILHAS

Uma mega-tabela com cem colunas para quatro tipos produziria colunas nulas que **parecem
lacunas** — e a arbitragem já decidiu que `NOT_APPLICABLE` não é lacuna.

```
attention_object (envelope comum)
├── phenomenon_case                       REQUIRED: região, cultura, problema, tempo
├── regulatory_deadline_object            REQUIRED: registro, prazo, status da fonte
├── competitor_identity_chain_object      REQUIRED: concordância de titular
└── longitudinal_field_pressure_object    REQUIRED: série, baseline, coorte
```

`regulatory_deadline_object` **não tem coluna de cultura nem de problema**. Não é omissão:
ausência de coluna é mais forte que coluna nula, porque nenhum `UPDATE` distraído consegue
preenchê-la depois.

E há um check que vale a pena ler em voz alta:

```sql
CONSTRAINT prazo_nao_autoriza_decisao_de_negocio
  CHECK (max_authorized_action <> 'BUSINESS_DECISION')
```

O banco recusa, em nível de estrutura, que um vencimento regulatório autorize decisão
comercial. A lei *"expiração não é retirada"* deixou de ser um parágrafo num documento.

---

## 4 · READINESS REPRODUZÍVEL

`ATTENTION_READY` **não é um booleano escrito à mão.** Os cinco requisitos ficam em
`attention_readiness`, um por linha:

```
VALID_EVIDENCE · OBJECT_SPECIFIC_TRIGGER · TIME_RELEVANCE
DECISION_QUESTION · DECISION_OWNER
```

A view `v_attention_readiness` recalcula o estado e devolve **quais portões bloquearam**.
É isso que permite a fila vazia dizer *por que* está vazia — hoje `ATTENTION_READY = 0`, e
o motivo é que nenhuma camada tem duas leituras com intervalo real.

---

## 5 · AS NOVE MANGUEIRAS CABEM SEM ALIAS

| # | tipo canônico persistido | tabela |
|---|---|---|
| H1 | `TERRITORIAL_OBSERVATION` | `territorial_observation` |
| H2 | `REGISTRATION_DEADLINE` | `registration_deadline` |
| H3 | `COMPETITOR_PRODUCT_IDENTITY` | `competitor_product_identity` |
| H4 | `OBSERVED_PAID_ACTIVITY` | `observed_paid_activity` |
| H5 | `FIELD_PRESSURE_SERIES` | `field_pressure_series` |
| H6 | `PERSON_CREATOR` · `FARM_BUSINESS_ENTITY` · `CREATOR_CONTENT_PROFILE` | três tabelas |
| H7 | `SCIENTIFIC_PERSON` | `scientific_person` |
| H8 | `COMPANY_LOCAL_ACCOUNT` | `company_local_account` |
| H9 | `CONTENT_ENTITY` · `CONTENT_TRANSLATION` · `ONTOLOGY_TERM` | três tabelas |

**H6 tem três tabelas porque tem três payloads.** `CREATOR_CONTENT_PROFILE` não aparece em
lugar nenhum do casco — e aqui existe, porque canal não é pessoa e uma pessoa pode ter
vários canais.

---

## 6 · OS TRÊS SUBRECEPTORES, COM PAI DECLARADO

O casco escreveu `H7·CIÊNCIA`, `H2·PORTFÓLIO` e `H6·CAMPO` — strings que nenhum adapter
casa com `H7`, `H2` ou `H6`. Aqui a relação é um **campo separado**:

```
scientific_publication          PARENT_HOSE_ID = H7
issue_expertise                 PARENT_HOSE_ID = H7
local_adama_portfolio_context   PARENT_HOSE_ID = H2
field_voice_observation         PARENT_HOSE_ID = H6
```

**Por que cada um existe:**

- **`scientific_publication`** — pessoa não é publicação. Sem esta tabela, a camada Ciência
  de um caso seria preenchida com pesquisadores, e o produto diria que há ciência por trás
  do caso porque encontrou um autor.
- **`local_adama_portfolio_context`** — H2 carrega o prazo de um registro de **qualquer
  titular**, inclusive de concorrente. Sem esta tabela, alguém liga H2 no bloco Portfólio e
  o portal passa a dizer que a ADAMA tem produto porque um registro qualquer tem prazo.
  Há um check que garante `is_context_not_evidence = true`.
- **`field_voice_observation`** — entidade não é observação. Sem ela, voz de campo é uma
  lista de nomes, e nome não é sinal.

E **`issue_expertise`** é uma relação `pessoa × cultura × problema × evidência × estado` —
não uma coluna na pessoa. Alguém pode ser autoridade em repilo na oliveira e não ser em
míldio na vinha. Modelar como relação é o que dá dentes ao portão.

---

## 7 · CONVERGÊNCIA SEM CONTADOR

`convergence_proposition` **não tem coluna `independent_family_count`.**

A contagem é derivada em `v_convergence_state`, contando famílias distintas entre pernas
com `independence_state = 'INDEPENDENT'`. Um contador manual pode divergir das pernas — e
foi exatamente assim que cinco das seis convergências da V1 viraram uma só.

Dois checks sustentam a lei:

```sql
dependente_declara_o_tipo_e_o_alvo   -- DEPENDENT exige dependency_type ≠ INDEPENDENT_SOURCE
                                     -- e depends_on_leg_id preenchido
independente_nao_tem_alvo            -- INDEPENDENT não pode apontar para outra perna
```

E `dependency_edge` guarda o grafo **fora** da convergência de um caso: `H3 → H4` por
`DERIVATION_DEPENDENCY` e `H5 → H1` por `SOURCE_DEPENDENCY` são propriedades do sistema,
não de um objeto.

---

## 8 · O QUE O BANCO SE RECUSA A SABER

`LOAD_STATE` foi separado em três, e só um pedaço vira coluna:

```
DATA_STATE      READY · EMPTY_VALID · NOT_STARTED · NOT_AVAILABLE · BLOCKED   ← no banco
PIPELINE_STATE  NOT_STARTED · RUNNING · PARTIAL · COMPLETE · BLOCKED · FAILED  ← no banco
REQUEST_STATE   UNWIRED · LOADING · ERROR_FAIL_CLOSED                          ← NÃO
```

**`LOADING` numa tabela transformaria uma requisição em andamento em fato sobre o mundo.**
E `UNWIRED` é propriedade da ligação, não do dado: uma linha existir já prova que a rota
foi ligada.

Os três de fora vivem no receptor do V8, em memória. O receptor começa `UNWIRED`; ao chamar
vira `LOADING`; a resposta traz o `data_state` do banco; falha de transporte vira
`ERROR_FAIL_CLOSED` **sem nunca degradar para `EMPTY_VALID`**.

> Um enum criado para a tela não pode contaminar o banco como estado de inteligência.

---

## 9 · GEOGRAFIA QUE NÃO MENTE

Três checks em `geo_anchor`:

```sql
point_exige_geometria       -- GEO_RESOLUTION = POINT sem geometria é recusado
geometria_exige_origem      -- geometria sem geometry_source_id é recusada
locality_text_nao_e_point   -- LOCALITY_TEXT nunca carrega geometria
```

O terceiro é o que impede a geocodificação silenciosa. Uma localidade em texto continua
texto até alguém declarar de onde veio a coordenada.

---

## 10 · MÉDIA NUNCA VIAJA SEM O N

`field_pressure_reading.n` é `NOT NULL` com `CHECK (n > 0)`. Não é possível gravar uma
leitura sem o denominador.

E os números do ledger **não são duplicados em tabela**: `RAIF_SEASONS_AVAILABLE = 23` e
`RAIF_READINGS_TOTAL = 148964` são derivados por consulta e comparados com o dono, que
continua sendo `scripts/metricas_canonicas.py`. O Supabase reproduz; não redefine.

---

## 11 · A FORMA DO BANCO

```
TABELAS = 57      VIEWS = 13      RPCs = 4      ENUMS = 27
COLUNAS = 417     CHECKS = 31     CHAVES ESTRANGEIRAS = 112
```

Todos derivados de `data/supabase/SUPABASE-CANONICAL-SCHEMA.json` por
`scripts/supabase_schema.py`. A migration e o dicionário de dados **saem do JSON** — escrever
os três à mão criaria três verdades que divergem no primeiro dia.

---

## 12 · O QUE ESTA ARQUITETURA NÃO RESOLVE

Honestidade antes da próxima rodada:

1. **O corpo dos views e RPCs não foi escrito.** Só as assinaturas, o que leem e o que
   derivam. Escrever o corpo antes de ter uma instância é escrever sem poder rodar.
2. **`H2` aponta para uma branch, não para um commit.** O mapa de mangueiras diz
   `origin/…italy-pilot`. A lei de leitura exige SHA fixo — resolver antes da primeira carga.
3. **Nenhum número de carga foi afirmado** onde não podia ser: `NOT_MEASURED` aparece
   várias vezes no plano de primeira carga, de propósito.
4. **RLS está desenhada, não implementada.** As políticas concretas entram com a
   autenticação.
5. **Os 12 bloqueadores do casco continuam de pé.** Eles não bloqueiam este desenho;
   bloqueiam o wiring.

---

## LEITURA RELACIONADA

- [Dicionário de dados](SUPABASE-DATA-DICTIONARY-EAME.md) — gerado
- [Contrato do publisher](SUPABASE-PUBLISHER-CONTRACT-EAME.md)
- [Modelo multilíngue](SUPABASE-MULTILINGUAL-MODEL-EAME.md)
- [Modelo de proveniência](SUPABASE-PROVENANCE-MODEL-EAME.md)
- [Plano de RLS](SUPABASE-RLS-PLAN-EAME.md)
- [Plano de primeira carga](SUPABASE-FIRST-LOAD-PLAN-EAME.md)
- [Validação em sombra](SUPABASE-SHADOW-VALIDATION-EAME.md)
