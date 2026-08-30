# ESPANHA INTEGRADA — regulatório e catálogo em produção

**Data:** 2026-08-30 · **Branch:** `claude/sintonia-eame-collection-es`
**HEAD aplicado em produção:** `4222f7e` · **Handoff usado:** `claude/adama-es-local-browser @ fec5ead`

```
ADAMA_ES_REGULATORY_INTEGRATED        YES
ADAMA_ES_CATALOG_INTEGRATED           YES
ADAMA_ES_INTEGRATED_INTO_EAME_ACERVO  YES

SPAIN_FOUNDATION_PHASE = COMPLETE
```

---

## A produção parou na primeira tentativa, e foi a melhor coisa que aconteceu

O primeiro dispatch **falhou na migration 007**, limpo: 001–006 SKIP, 007 FAIL, imports
pulados, **zero escrita**. E o inventário do run mediu o estado real da produção, que eu
supunha errado:

```
PUBLIC_TABLE_COUNT  26     ← eu supunha 30
ROWS_TOTAL         109
crop_calendar      não existe → a produção estava em 001–009, não em 001–012
```

**A causa:** a 007 cria views com `create or replace`, e a 009 e a 018 as redefinem com
outra forma. Reaplicar a 007 sobre a forma nova é recusado — *cannot drop columns from view*.

**A causa da causa**, achada ao tentar provar o replay sobre a cadeia completa, é pior: a
015 tem `add column if not exists fact_geografia_origem`, e a **018 aposenta essa coluna**.
Reaplicar a 015 a **ressuscitaria**. Um replay podia desfazer uma aposentadoria em silêncio.

**A solução foi a padrão, não o remendo:** `scripts/cadeia_canonica.sh` passou a manter um
livro-razão, `public.schema_migracao`. Ele é infraestrutura do *aplicador*, não schema de
domínio — por isso nasce no script e não numa migration, e por isso o pré-voo derivado o
conhece pelo nome em vez de tratá-lo como objeto criado à mão no painel.

O bootstrap é honesto: num banco que já tem migrations e nenhum registro, a primeira
passada aplica o que falta e **anota o que já existia a partir da resposta do banco**
(*already exists*), não de suposição sobre até onde alguém foi. Foi exatamente a suposição
errada que me fez achar que a produção estava em 012.

**O que eu declarei READY e não estava: `PRODUCTION_MIGRATION_PATH`.** Eu provei a cadeia
num banco limpo e chamei o caminho de pronto. Produção não é um banco limpo. O CI agora tem
o passo `4i`, que prova os dois cenários que faltavam — estado parcial 001–009 e cadeia
completa reaplicada — e em cada um exige que `fact_geografia_*` continue com **zero**
colunas. A aposentadoria da 018 tem de sobreviver ao replay.

## B · A prova RAW recebida

Handoff `fec5ead`: cada um dos 196 objetos foi **baixado de volta** do bucket e teve o
sha256 recalculado contra o local.

```
ASSETS_ESPERADOS   196     SHA_VERIFIED  196
HASH_MISMATCH        0     NAO_BAIXARAM    0
BYTES              304.482.907

RAW_PRESERVATION_GATE       CLOSED
RAW_CONTENT_INTEGRITY_GATE  CLOSED
```

Isso resolve o `media 2981` — o que recebeu **520**, onde gravação parcial era plausível:
os bytes que aquele 520 deixou são os certos, e o 520 foi perda de **resposta**, não de
gravação. A lei `PRESENTE_NO_INVENTARIO ≠ BYTES_CONFERIDOS` **fica**; o que caiu foi a
pendência neste conjunto. `PROVA = EXTERNA`, `VERIFICADO_DAQUI = NO` — esta branch não
enviou nem verificou nada.

## C · O denominador ROPF, medido

**96** fichas, **96** REG distintos, de **188** registros ADAMA no ROPF. Os **92 cancelados
não estão no artefato**: não foram coletados. `NOT_COLLECTED ≠ NOT_REGISTERED`, e a
diferença está escrita no próprio SQL do import.

As duas formas de id que o registro espanhol usa convivem sem conversão: **62 numéricas**,
**34 no formato ES-NNNNN**.

## D–F · `ES_REGULATORY_IMPORT_V1`

Gerador determinístico (`scripts/regulatorio_importar.py`), SQL byte a byte reproduzível,
**zero** UPDATE/DELETE/TRUNCATE, todo INSERT com `ON CONFLICT` sobre a chave de **captura**
da 013. Idempotente em três execuções. Dezenove afirmações e o red team dos dez ataques.

**O que a V1 não importa, declarado:** os 993 rótulos de cultivo e 195 de agente das fichas.
`registro_uso` não tem onde guardar o rótulo publicado quando o casamento com o vocabulário
canônico não acontece — e hoje há 3 culturas semeadas. Importá-los agora descartaria a
maioria em silêncio. `catalogo_produto_cultivo` acertou nisso preservando `rotulo_publicado`
ao lado do `crop_id` nulo; `registro_uso` precisa do mesmo antes de receber usos.

## G–I · Contadores medidos **do banco real**

| | esperado | produção |
|---|---|---|
| `ROPF_RECORDS` | 96 | **96** |
| `ROPF_ONLY_RESOLVED` | 52 | **52** |
| produtos | 56 | **56** |
| documentos | 147 | **147** |
| relações de cultivo | 711 | **711** |
| declaradas / citadas | 588 / 123 | **588 / 123** |
| crop × issue | 5 | **5** |
| crop × dose | 26 | **26** |
| janelas | 3 | **3** |
| `LOCAL_REGISTERED` | 44 | **44** |
| `LOCAL_PRESENT_BUT_REGISTRATION_NOT_PROVED` | 12 | **12** |

O workflow compara cada par e **falha** se divergir. Passou. Nenhuma das 52 `ROPF_ONLY` tem
produto — `ROPF_ONLY ≠ ADAMA_PRODUCT`.

## J–L · Ordem, workflow e CI

```
001–007 · 009 · 010–012 · 013 · 014 · 015 · 016 · 017 · 018 · 008 por último
                      depois: regulatório ES → catálogo ES
```

**Uma ordem só:** `scripts/cadeia_canonica.sh` é o único dono dela, e o workflow de produção
e o CI chamam o mesmo script. O pré-voo deixou de ser lista fixa de contagens (`0|23|26|30`,
que já estava para trás) e passou a perguntar o que importa — *o `public` contém algo que
este repositório não cria?* — derivado das migrations.

## M–S · Produção

```
PUBLIC_TABLE_COUNT   26 → 51        ROWS_TOTAL  109 → 1.932
PUBLIC_VIEW_COUNT          16       CHECK_CONSTRAINTS   104
RLS_ENABLED_TABLE_COUNT    51       UNIQUE_INDEXES      100

regressoes_regulatorio_es   PASS
regressoes_catalogo_es      33/33 PASS  ← contra o banco REAL
AVASTEL_BYTES        158.083.718
NEPTUNE_DOCS_COM_RAW           3
```

Round-trip, isolação de país e o red team inteiro rodaram **em produção**, não em ensaio:
todo produto é `ES`, consultas `IT` e `FR` devolvem zero, `disponibilidade_comercial`
continua vazia, e nenhum dos 12 não-provados virou `NOT_REGISTERED` — o estado nem existe
no vocabulário.

## T–V · O que continua como estava

**CUPROXI FLO:** `ES-00979` no registro, `19232` no catálogo, ligados por
`MATCHED_WITH_EVIDENCE`. **Não fundidos.**

**NEPTUNE:** `ES-00211`, com os três PDFs no acervo e apontando para os objetos preservados.

**`ES-CASE-001` = OPEN.** `REGULATORY_RECORD_AVAILABLE ≠ CASE_RESOLVED` e
`PRESERVED_PDF ≠ CASE_RESOLVED`. A importação organiza evidência; não fabrica veredito.

`COMMERCIAL_AVAILABILITY = NOT_KNOWN` onde não provada. Nenhum portal, nenhum score,
nenhuma oportunidade comercial inventada.

## Duas coisas que a produção tem e que este relatório não arredonda

**Os quatro relógios estão com zero linhas** (`crop_calendar`, `issue_window`,
`registro_uso_janela`, `freshness_regra`). Isso é correto e esperado: a fixture
`es_calendario_mvp.sql` é *fixture*, não dado de produção, e não foi aplicada. O calendário
agronômico espanhol continua sendo outra entrega.

**`crop_local` e `issue_local` estão vazios em produção**, então os `crop_id` das 711
relações de cultivo estão nulos e os **rótulos publicados estão todos preservados** — que é
exatamente a lei `NO_FUZZY_SILENT_MATCH`. O número 711 conta relações, não casamentos. Semear
o vocabulário MAPA é o próximo passo natural, e é uma decisão de modelagem própria.

---

**`SPAIN_FOUNDATION_PHASE = COMPLETE`.** Nenhuma missão nova aberta, nenhum portal,
nenhuma coleta iniciada.
