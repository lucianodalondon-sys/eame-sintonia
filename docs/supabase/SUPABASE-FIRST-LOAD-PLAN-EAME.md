# PLANO DE PRIMEIRA CARGA — SINTONIA EAME

**Data:** 2026-08-31 · plano executável em `data/supabase/SUPABASE-PUBLISH-MAP.json`

```
FIRST_LOAD_EXECUTED = NO      COLLECTION_EXECUTED = NO      MIGRATION_APPLIED = NO
```

> **Nada foi recolhido.** Toda entrada abaixo já existe congelada num commit fixo.

---

## 1 · AS NOVE ENTRADAS

| # | payload canônico | commit fixo | contagem esperada |
|---|---|---|---|
| **H1** | `TERRITORIAL_OBSERVATION` | `11fd7b5` (handoff `4ea268d`) | 22 observações · objetos `NOT_MEASURED` |
| **H2** | `REGISTRATION_DEADLINE` | ⚠️ **branch, resolver SHA** | prazos `NOT_MEASURED` · 163 rótulos, 24 ausentes |
| **H3** | `COMPETITOR_PRODUCT_IDENTITY` | `dc32ce0` (freeze `25194e3`) | 36 tuplas · **0 objetos** |
| **H4** | `OBSERVED_PAID_ACTIVITY` | `acfd987` (handoff `a2fad2d`) | `NOT_MEASURED` |
| **H5** | `FIELD_PRESSURE_SERIES` | `ad041d7` | **148.964 leituras · 23 safras** |
| **H6** | `PERSON_CREATOR` + 2 | `248bd27` + `a509c12` | 164 em 90 dias · entidades `NOT_MEASURED` |
| **H7** | `SCIENTIFIC_PERSON` | `ad041d7` | pessoas `NOT_MEASURED` · **0 com expertise provada** |
| **H8** | `COMPANY_LOCAL_ACCOUNT` | `c25e44b` | **22 contas · 0 conteúdo** |
| **H9** | `CONTENT_ENTITY` + 2 | `1443f643` | **0 traduções** |

---

## 2 · OS QUATRO ZEROS QUE SÃO RESULTADO, NÃO FALHA

**H3 · 0 objetos de atenção.** As 36 tuplas existem. Nenhuma tem
`OBJECT_SPECIFIC_TRIGGER`: o gatilho exige mudança observada entre **duas** leituras com
intervalo real, e houve uma captura só.

**H7 · 0 pessoas com expertise provada.** A view `v_issue_expert` devolve vazio, com o
motivo. Ninguém aparece como especialista do problema — que é exatamente o portão
funcionando.

**H8 · 0 conteúdo.** `CONTENT_COLLECTION_STAGE = NOT_STARTED` nas 22 contas. Zero conteúdo
coletado **não é** ausência de comunicação da empresa.

**H9 · 0 traduções.** O acervo não foi traduzido e traduzir não está autorizado.
`content_translation` nasce vazia, e isso é `EMPTY_VALID`.

> Os quatro zeros precisam chegar ao V8 **com o motivo junto**. Um zero sem motivo é
> indistinguível de um cano quebrado.

---

## 3 · O QUE NÃO PODE SER AFIRMADO AINDA

`NOT_MEASURED` aparece sete vezes no mapa, de propósito. O caso mais claro é H1:

> 22 itens territoriais foram reprocessados. Quantos viram `ATTENTION_OBJECT` depende do
> guard de pareamento rodar na carga. **Afirmar o número antes de rodar seria inventá-lo.**

O guard exige que o termo da cultura apareça **dentro da passagem** que sustenta o
problema. Documento multi-boletim não autoriza produto cartesiano. Quantas das 22 passam,
só a execução diz.

---

## 4 · UMA ENTRADA FORA DA LEI, DECLARADA

**H2 aponta para `origin/…italy-pilot`, que é uma branch.**

A lei de leitura exige `COMMIT_SHA` fixo. Está registrado no mapa como
`SOURCE_COMMIT = RESOLVER_ANTES_DA_CARGA` — não corrigido em silêncio com um SHA
adivinhado, e não escondido.

**Resolver e registrar antes da primeira carga.** É o único bloqueador do plano que depende
de uma ação e não de uma decisão.

---

## 5 · OS NÚMEROS DO LEDGER NÃO SE DUPLICAM

```
RAIF_SEASONS_AVAILABLE = 23        RAIF_READINGS_TOTAL = 148.964
```

Esses números **não viram coluna em tabela nenhuma**. São derivados por consulta:

```sql
select count(*) as readings, count(distinct season) as seasons
from field_pressure_reading r join field_pressure_series s using (series_id)
where s.source_id = 'RAIF'
```

E comparados com o dono, que continua sendo `scripts/metricas_canonicas.py`. **O Supabase
reproduz; não redefine.** Se a consulta der outro número, o problema é da carga — não é uma
segunda opinião sobre o total.

---

## 6 · A CONTAGEM PROIBIDA

H6 tem duas famílias, e a validação devolve duas linhas:

```sql
select 'person_creator' as kind, count(*) from person_creator
union all
select 'farm_business_entity', count(*) from farm_business_entity
```

**Proibido somar as duas linhas num número só.** `PERSON_CREATOR ≠ FARM_BUSINESS_ENTITY`, e
a soma nunca se chama `CREATORS_READY`.

E `ROW ≠ ENTITY`: a inflação medida foi de **2,6×**. As duas contagens sempre viajam
juntas.

---

## 7 · AS DUAS ARESTAS DE DEPENDÊNCIA

Precisam ser gravadas na carga, depois das duas pontas existirem:

```
H3 → H4    DERIVATION_DEPENDENCY   a perna META da cadeia É o anúncio da Meta
H5 → H1    SOURCE_DEPENDENCY       o RAIF publica os dois lados
```

Sem elas, duas pernas que são a mesma evidência vista de outro ângulo contariam como duas
famílias. **Foi esse erro que fez cinco das seis convergências da V1 virarem uma só.**

---

## 8 · ORDEM

```
1  ontology_term + ontology_term_label + source
2  H9 content_entity
3  H2 registro e prazo
4  H1 territorial
5  H5 série + aresta H5→H1
6  H3 identidade + H4 atividade paga + aresta H3→H4
7  H7 pessoas e publicações
8  H6 creators, com entry_path_event vazia
9  H8 contas, todas em NOT_STARTED
```

**Por quê:** arestas exigem as duas pontas. E H9 entra cedo porque nenhum texto deve chegar
ao banco sem língua declarada — mesmo que seja `UNKNOWN`.

---

## 9 · O QUE ACONTECE SE UM GUARD REPROVAR

`FAIL_CLOSED`. A execução inteira para, `publish_run.status = 'FAILED_CLOSED'`, e
`failed_reason` diz qual guard e em que família.

**Não existe "publica o que deu".** Publicar metade de uma família produz um estado que
ninguém consegue interpretar depois — e que parece completo.
