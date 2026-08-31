# MODELO MULTILÍNGUE — SUPABASE SINTONIA EAME

**Data:** 2026-08-31 · herda `MULTILINGUAL_CONTRACT_V1` (commit `1443f643`) sem alterá-lo

---

## 1 · A REGRA QUE O SCHEMA TORNA IMPOSSÍVEL DE VIOLAR

```
1 ATTENTION_OBJECT = 1 identidade canônica, NEUTRA DE IDIOMA
```

Nunca `AO-001-PT`, `AO-001-EN`, `AO-001-ES`, `AO-001-FR`, `AO-001-IT`.

**Como o banco garante:** `attention_object` não tem coluna de idioma. Nenhuma. Para
existir `AO-001-PT` seria preciso criar uma linha com outro `attention_object_id` — e a
chave natural do publisher deriva de país + tipo + chave do tipo, **nunca do título**.

```
attention_object                  ← estrutura, UMA vez
attention_object_representation   ← texto, por idioma, PK (object_id, language)
```

---

## 2 · O QUE NÃO SE DUPLICA

**Fato estruturado — existe uma vez:**

```
ids · datas · números · países · culturas · problemas · estados
guards · relações · tipos de ação · resoluções temporais · geometrias
```

Cinco cópias de uma data são cinco chances de divergir. Uma cultura vira `ontology_term`
com código EPPO; o nome dela em cada língua vive em `ontology_term_label`. Sem isso,
*mildiu* e *downy mildew* seriam dois problemas diferentes.

**Representação linguística — existe por idioma:**

```
title · summary · interpretation · attention_reason
what_we_know · what_we_dont_know · action_text · why_text
```

---

## 3 · AS CINCO LÍNGUAS DO CONTRATO, SEPARADAS

O contrato tem cinco papéis de língua, e o casco só implementou um. Aqui os cinco têm
lugar:

| papel | onde vive |
|---|---|
| `SOURCE_LANGUAGE` | `evidence.source_language`, `content_entity.source_language` |
| `ARTIFACT_LANGUAGE` | `source_snapshot.artifact_language` |
| `UI_LANGUAGE` | não é dado: é preferência do cliente, viaja no pedido |
| `DISPLAY_LANGUAGE` | resposta do RPC, com `FALLBACK_USED` junto |
| `TRANSLATION_TARGET_LANGUAGE` | `content_translation.translation_language` |

**Vocabulário fechado:** `pt · en · es · fr · it · MULTILINGUAL · UNKNOWN`. É um enum —
língua fora dele **recusa a criação da linha**, não a degrada.

---

## 4 · ORIGINAL E TRADUÇÃO EM TABELAS DIFERENTES

```
content_entity        canonical_entity_id · source_language · original_text
content_translation   (canonical_entity_id, translation_language) · translated_text
                      translation_provenance · translation_quality · translated_at
                      source_text_hash
```

**Por que duas tabelas e não duas colunas:** com colunas, um `UPDATE` distraído sobrescreve
o original. Com tabelas separadas, apagar o original exige um `DELETE` na tabela errada — e
a chave estrangeira reclama.

`source_text_hash` guarda o hash do original no momento da tradução. Se o original mudar, a
tradução fica detectavelmente obsoleta em vez de silenciosamente errada.

**A tradução nunca entra sozinha.** Sem `content_entity`, não há a que se referir.

---

## 5 · `UNKNOWN` CONTINUA `UNKNOWN`

`source_language` tem default `'UNKNOWN'` — não `NULL`, não `'—'`.

Isso importa porque o ledger diz o que é hoje:

```
SOURCE_RECORD_LANGUAGE_COVERAGE = MEASURED_ZERO_DECLARED
283 de 5.998 registros têm o campo de língua · ZERO têm valor declarado
```

**A maioria do acervo entra como `UNKNOWN`, e esse é o estado correto.** O casco
`index (11)` renderiza `—` quando a língua falta; `—` é um traço, não um estado. No banco
não existe essa opção: o enum não tem `—`.

---

## 6 · FALLBACK DECLARADO, NUNCA FINGIDO

```
CADEIA:  <pedido> → en → pt
```

Toda resposta declara três coisas:

```
REQUESTED_LANGUAGE · DISPLAY_LANGUAGE · FALLBACK_USED
```

**Permitido:**

```json
{"REQUESTED_LANGUAGE": "fr", "DISPLAY_LANGUAGE": "en", "FALLBACK_USED": "YES",
 "FALLBACK_CHAIN": ["fr", "en"]}
```

**Proibido:** devolver o texto em inglês dizendo `DISPLAY_LANGUAGE = fr`. Fingir que FR
existe é pior do que não ter FR — o usuário francês leria inglês achando que é a versão
dele.

**Sem nenhuma língua da cadeia:**

```json
{"FALLBACK_USED": "NO_REPRESENTATION_AVAILABLE", "text": null}
```

Nunca traduzir na hora para preencher. **Não existe tradução em runtime.**

A política vive num lugar só: o RPC `resolve_representation`. Uma implementação, não uma
por view — senão cada view inventa a sua e elas divergem.

---

## 7 · A EVIDÊNCIA FICA FORA DA CADEIA

`evidence.original_text` **nunca sofre fallback.** É exibido na língua da fonte, sempre,
qualquer que seja o `DISPLAY_LANGUAGE` pedido.

A tradução aparece **abaixo**, marcada como tradução, com `translation_provenance`
visível — e o botão de voltar ao original sempre presente.

> Uma publicação francesa pode descrever um fato espanhol. `evidence` tem os dois campos
> separados — `source_location_country` e `fact_location_geo_id` — e isso nunca move o
> fato de país.

---

## 8 · O QUE ESTE MODELO NÃO AUTORIZA

```
traduzir o acervo                    não autorizado, e o schema não precisa disso
tradução por IA em runtime           menu, botão, filtro e estado vêm de dicionário
inferir língua por heurística        UNKNOWN é honesto; um palpite não é
usar rótulo como identificador       CANONICAL_ID ≠ DISPLAY_LABEL
```

`content_translation` **nasce vazia**, e isso é `EMPTY_VALID` — consulta válida, resultado
vazio, porque traduzir não foi autorizado.
