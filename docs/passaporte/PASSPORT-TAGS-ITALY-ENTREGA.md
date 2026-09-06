# PASSAPORTE / ETIQUETAS UNIVERSAIS — ENTREGA

**Missão:** organizar toda evidência do Sintonia sob taxonomia universal e reutilizável
**Escopo:** `COUNTRY_SCOPE = ITALY` · `PROJECT = SINTONIA_EAME_ITALY`
**Data:** 2026-09-06 · **Somente leitura sobre o acervo.** Nenhuma coleta, nenhum backfill,
nenhum centavo gasto, nenhum arquivo do acervo alterado.

---

## A · REPOSITORY

```
https://github.com/lucianodalondon-sys/eame-sintonia.git
```

Confirmado por `git remote -v` antes de qualquer escrita. Havia **14 pastas** com nome
`eame-sintonia*` no disco; **uma só** é repositório Git com este origin.

## B · LOCAL_PATH

```
C:\eame-sintonia-passport        worktree desta missão (novo)
C:\eame-sintonia-passport-ref    worktree só-leitura do PASSPORT-1.0 (novo, destacado)
C:\eame-sintonia                 checkout principal — NÃO TOCADO
```

> `C:\eame-sintonia` estava com **39 arquivos modificados** de outra missão
> (`claude/eame-competitor-public-communication`, Instagram e comunicação de concorrente).
> Por isso esta missão nasceu num **worktree separado**: nada dela encostou naquele
> trabalho em curso.

## C · BASE_BRANCH / BASE_HEAD

```
BASE_BRANCH = origin/sintonia/canonical
BASE_HEAD   = 10af4a7accff88494eb097978c171601994a3422
              "ledger: o selo do PASSO 03, com a prova do push"  ·  2026-09-06 06:04 UTC
```

## D · MISSION_BRANCH / HEAD

```
MISSION_BRANCH = claude/passport-tags-italy-v1     (nova; não existia)
```

Três commits, todos nesta branch. **Nada foi empurrado para `sintonia/canonical`.**

## E · ESTADO DO PASSAPORTE ANTERIOR

`PASSPORT-1.0`, branch `claude/sintonia-information-passport-bbtps0` (`ce6add1`,
2026-09-05). **Não está em `canonical`** — nunca foi integrada.

| artefato | tamanho |
|---|---|
| `docs/passaporte/CONTRATO-DO-PASSAPORTE.md` | 438 linhas, 9 seções |
| `data/passaporte/EVENTOS.jsonl` | **33.886 eventos**, 12,8 MB, 2.960 itens |
| `scripts/passaporte*.py` | 2.422 linhas em 4 arquivos |
| `tests/test_passaporte.py` | 333 linhas |

**É trabalho sério, e três coisas dele são excelentes e devem ser mantidas inteiras:**

1. `LEXICALLY_SCANNED` como estado próprio que **nunca** satisfaz leitura;
2. `ORPHAN_INTELLIGENCE` como estado com nome, em vez de silêncio;
3. `OPPORTUNITY` nascendo `BLOCKED`, de propósito e declarado.

Append-only **verificado**: 33.886 eventos, zero `EVENT_ID` repetido, história preservada
em 197 itens com dois ou mais selos de identidade.

## F · DEFEITOS HERDADOS

Dezesseis, medidos e reproduzíveis — detalhe em [`PASSPORT-DEFEITOS-HERDADOS.md`](PASSPORT-DEFEITOS-HERDADOS.md).

### Os que já se materializaram no artefato gravado

| # | defeito | número |
|---|---|---|
| **D11** | **`CLAIM_ID` não é identidade — o ordinal reinicia a cada extração** | **12 de 22 colididos · 83% das rotas penduradas em id ambíguo** |
| **D1** | `TIME_RESOLVED → PROVED` com motivo literal *"NÃO SEI"* | **346 eventos** |
| **D3** | universo parcial: 3 arquivos do acervo canônico fora do passaporte | **33 registros, 144.802 caracteres** |
| **D2** | identidade ausente colapsa linhas distintas | 3 linhas → 1 item |
| **D4** | o valor da dimensão mora em prosa; `'VINE'` e `"['VINE']"` coexistem | 87 eventos |
| **D5** | a projeção arbitra conflito por recência, sem estado de conflito | 197 itens |
| **D6** | `PUBLISHED_AT` vira tempo sem dizer que tempo é | 1.478 itens |
| **D15** | `CAPTURE` aprova `NOT_PRESERVED` sem motivo declarado | 335 itens |
| **D14** | `REASON` carrega cinco significados no mesmo campo | 5 vocabulários |

### Os que são fresta aberta, ainda não exercida

| # | defeito | onde |
|---|---|---|
| **D8** | causa raiz de D1: `_sabido()` é igualdade exata e não vê sentinela com sufixo | **1.312 valores, 46 campos** |
| **D12** | `admitir()` não valida `raw_state` — a porta fechada tem fresta no 1º evento | `passaporte.py:284` |
| **D13** | esquema do evento é aberto; `CAMPOS_EVENTO` é código morto | `passaporte.py:221,354` |
| **D16** | vocabulários nunca validados; gramática de `IDENTITY_BASIS` em 18 lambdas | `passaporte_portao.py:38-64` |
| **D7** | três vocabulários de capacidade, mapa só em código | 22 · 10 · 16 |
| **D9** | independência existe em `voz.py` e não foi **transportada** | portão mede 241/9/2 |
| **D10** | profundidade de leitura não é estado; `TRANSCRIPT_READ` nunca emitido | 0 eventos |

**Quatro hipóteses minhas foram derrubadas pela medição** e estão registradas como tal na
§9 daquele documento — inclusive uma derrubada pelo meu próprio script de censo.

> **D11 é o achado que muda a conclusão.** Antes dele, a camada de roteamento parecia
> pequena mas sadia (48 rotas, motivo declarado, `OPPORTUNITY` bloqueado de propósito).
> Medida a identidade do claim, 83% dessas rotas apontam para um identificador que carrega
> mais de uma afirmação — inclusive um par de casos escritos **de propósito** para se
> contradizerem. A camada não é pequena e sadia: é pequena e ambígua.

## G · HIERARQUIA UNIVERSAL CONGELADA

[`PASSPORT-HIERARCHY.md`](PASSPORT-HIERARCHY.md). Onze camadas, transcritas da missão sem
invenção, com três leis: *nenhuma camada empresta força para a de baixo*; *camada pulada é
`UNKNOWN`, nunca satisfeita*; *`CROSSINGS` exige `INDEPENDENCE` resolvida*.

E a distinção que faltava: **hierarquia** (do que o item é feito), **escada de estágios**
(o que aconteceu com ele) e **fluxo de produto** (como vira uso) são **três eixos**, não
três concorrentes.

## H · SCHEMA UNIVERSAL · I · TAXONOMIA DOS ESTADOS

[`PASSPORT-FIELD-MAPPING.json`](PASSPORT-FIELD-MAPPING.json) — 31 conceitos, cada um com
`ORIGEM` (`HERDADO` · `TRANSPORTE_AUSENTE` · `SO_ESTADO` · `CONFLITO` · `AUSENTE`),
dono, vocabulário e recomendação.

## J · CENSO · K · MAPPING OLD → CANONICAL

[`PASSPORT-FIELD-CENSUS.md`](PASSPORT-FIELD-CENSUS.md) — **855 campos**, **174 conflitos**,
**222 achados de dívida**, em 12 varreduras independentes.

> ### O achado principal
> **Quase nada precisa ser inventado. Quase tudo precisa ser transportado.**

| | |
|---|---:|
| já existem com dono canônico fora do passaporte | **19 de 31** |
| existem só como estado, sem o valor | 6 |
| têm dois ou mais vocabulários que não conversam | 7 |
| **realmente ausentes em todo o repositório** | **4** |

Os quatro ausentes: `OBSERVATION_STATE` · `PROOF_STATE` · `RELATIONSHIP_ID` ·
`UNKNOWN_FIELDS`.

## L · PILOTO

[`PASSPORT-PILOTO-MEDICAO.json`](PASSPORT-PILOTO-MEDICAO.json) · `scripts/passaporte_piloto.py`

Amostra estratificada, 10 famílias por natureza de evidência, 25 registros cada.
Nenhuma família fácil foi escolhida sozinha; `IT-ROTULOS*` ficou **fora de propósito**
(é Label Intelligence, fora do escopo).

```
ITEMS_TESTED                          =   250
FIELDS_POPULATED_FROM_EXISTING_PROOF  = 1.200   (13,7% de 8.750)
FIELDS_UNKNOWN                        = 7.550   (86,3%)
EIXOS QUE NENHUM REGISTRO PREENCHE    =    16 de 35
```

| família | cobertura | | família | cobertura |
|---|---:|---|---|---:|
| field_sensor | 32,5% | | regulatory | 12,8% |
| territorial | 22,5% | | competitor | 12,0% |
| science | 14,3% | | phytosanitary | 11,4% |
| market | 14,3% | | creator/voz pública | 8,8% |
| news/event | 5,7% | | climate | 2,9% |

## M · CONFLITOS ENCONTRADOS

- **Capacidade:** `CAP-001…CAP-022` (22, atlas) × 10 `ÁREA` × 16 `CAPABILITY_ID`
  (passaporte). Treze dos dezesseis nomes do passaporte aparecem **zero vezes** no atlas.
  O único mapa vive em `passaporte_backfill.py:858`, sem documento.
- **Cultura:** `POLITICA-CANONICA-DE-CROP.md` (`CROP_ALL`/`CROP_PRIMARY`/`CROP_CARDINALITY`/
  `CROP_RESOLUTION_STATE`/`CROP_EVIDENCE`) e o `CROP_STATE` do passaporte foram escritos
  **no mesmo dia, 2026-09-05, em branches diferentes**, e não se conhecem.
- **Ausência:** `NÃO SEI` e `NOT_KNOWN` convivem no mesmo campo (2.673 × 451 em `CROP`;
  473 × 5.642 em `COUNTRY_OF_FACT`).
- **Língua:** `OFFICIAL_DOCUMENT` (2.030) e `DOCUMENTO_OFICIAL` (2.030).
- **Família:** três conceitos com o mesmo nome — 10 semânticas, 13 por caminho, 8 de rota.
- **O token `PROVED`:** significa coisa diferente em `IDENTITY_STATE`, `GEOGRAPHY_STATE` e
  `TIME_STATE`. Filtrar por `PROVED` sem nomear o eixo devolve resposta errada **em silêncio**.

## N · IDENTIDADE

`IDENTITY_SAFE = NO`

O erro antigo **ainda existe**: 51 `EXTERNAL_ID`, 107 `ENTITY_ID` e 12 `ACCOUNT_HANDLE`
com valor que não é identidade. Três linhas distintas do `SENSOR-PILOT` colapsaram num
`ITEM_ID` só.

**Mas 2.496 `PERSON_ID = "NÃO SEI"` são honestos** — são vídeos, não sabemos quem filmou,
e cada linha guarda o próprio `EXTERNAL_ID` válido. `NÃO SEI` só vira defeito quando o
campo ignorado **é a chave**.

E a casa **já tem a trava certa**: `voz.py:106` põe a posição na chave quando não há id
(`__SEM_ID_ESTRUTURAL__`), e por isso não colapsa. O passaporte não herdou.

## O · GEOGRAFIA

**A parte mais forte do sistema, e melhor do que o passaporte.**
`scripts/fato_local.py` (51 KB) é dono de `FACT_LOCATION` com precisão, âncora, gazetteer
e **três estados de recusa** (`PLACE_MENTION_NOT_FACT`, `TERRITORIAL_LIST_NOT_FACT`,
`NEGATED_OBSERVATION_NOT_FACT`). A migração `018_o_lugar_do_fato_ganha_dono.sql` dá papel
ao lugar da entidade (`BASE`/`OPERATING`/`INFLUENCE`).

E a lei está aplicada **por item**, com o motivo gravado no log:

```
318  "nenhum lugar nomeado no texto — idioma não é lugar"
240  "COUNTRY_SCOPE é escopo da CONTA, não lugar do fato"
 99  "país da PESSOA procurada, não do fato"
```

O passaporte, porém, guarda **um** `GEOGRAPHY_STATE` e **nenhum lugar**.

## P · TEMPO

**O eixo mais fraco, e o contraste com a geografia é a prova.** Existe **um** `TIME_STATE`
alimentado indistintamente por `PUBLICATION_DATE`, `PUBLISHED_AT` e até `CAPTURED_AT`.
A data do fato nunca teve eixo. No piloto, `OBSERVED_AT` foi preenchido em **0 de 250**.

## Q · LINEAGE / INDEPENDÊNCIA

`LINEAGE_STATE` do passaporte é **parentesco** (vídeo → transcrição), provado pelos motivos
gravados. A **independência** existe, com dono e portão medido —
`voz.py:50`, `ORIGINAL · RESHARE · SYNDICATED · UNKNOWN`, `VIDEO_ORIGINALITY = PROVED`,
241 `UNKNOWN` · 9 `SYNDICATED` · 2 `RESHARE` — e **não chega ao passaporte**. Existe só
para vídeo; boletim, post e documento não têm equivalente.

## R · READINESS PARA CRUZAMENTOS FUTUROS

`CROSSING_READY = NO`, e agora com número em vez de opinião.

| a pergunta que o cruzamento precisa fazer | tem resposta hoje? |
|---|---|
| mesma cultura? | **5,2%** dos registros · e `VINE` ≠ `['VINE']` no artefato canônico |
| mesmo problema? | **0,8%** |
| geografia compatível? | `FACT_LOCATION` 46% · `COUNTRY_OF_FACT` 3,6% |
| tempo compatível? | `CAPTURED_AT` 86% — **mas é captura, não fato**; `OBSERVED_AT` 0% |
| observação ou modelo? | **0%** — o campo não existe |
| mesma linhagem? independentes? | **0%** — existe na casa, não no passaporte |
| qual a força da prova? | `PROOF_STATE` 0% · **`EVIDENCE_CLASS` 54,8%, semente pronta** |
| qual capacidade consome? | **0%** — e três vocabulários sem mapa |

## S · RED_TEAM

24 leis exercidas em código — `tests/test_passaporte_etiquetas.py`, **24 passaram, 0 falharam**.

> **Ressalva honesta:** não há `pytest` nem `pip` neste ambiente. Os testes foram escritos
> para rodar **sem dependência** (`python3 tests/test_passaporte_etiquetas.py`) e assim
> foram executados. A suíte antiga do repositório **não pôde ser rodada aqui** — isso é
> `NAO_MEDIDO`, não é "passou".

Uma das leis pegou um defeito **meu**: `PROOF_STATE` estava declarado `AUSENTE` sem
declarar a busca que provou a ausência. Corrigido.

## T · PASSPORT_REQUIRED

```
PASSPORT_REQUIRED = NO
```

Inalterado, como a missão exige. E, medido, ele **não poderia** ser ativado:

```
IDENTITY_SAFE          = NO    51 EXTERNAL_ID inválidos · 1 colapso vivo
SCOPE_KNOWN            = NO    3 arquivos do acervo canônico fora do universo
SCHEMA_STABLE          = NO    CROP, TEMPO e CAPABILITY com vocabulários concorrentes
BACKFILL_REPRODUCIBLE  = SIM   BACKFILL_AT é constante declarada
NO_SILENT_COLLAPSE     = NO    3 linhas → 1 item
UNKNOWN_PRESERVED      = NO    346 UNKNOWN promovidos a PROVED
LINEAGE_MODEL_USABLE   = NO    independência não transportada
```

> **Atenção:** o `CONTRATO-DO-PASSAPORTE.md §9` declara `PASSPORT_REQUIRED = YES`. Essa
> declaração vive numa branch que **não está em `canonical`** e, pelas sete medidas acima,
> **não deve ser ativada**. É a contradição mais importante desta entrega.

## U · FULL_BACKFILL_RECOMMENDATION

```
FULL_BACKFILL_RECOMMENDATION = NO
```

Não é conservadorismo: um backfill total hoje gravaria `'VINE'` e `"['VINE']"` como
culturas diferentes, `PUBLISHED_AT` como tempo do fato em 1.478 itens, e `UNKNOWN` como
`PROVED` em 346. **Backfill sobre schema instável fabrica dívida com cara de dado.**

## V · NEXT_SAFE_STEP

Nesta ordem, e nenhum deles é coleta:

1. **Consertar `CLAIM_ID` (D11).** É o mais grave e o mais barato: derivar de
   `sha1(ITEM_ID + texto do claim)`, nunca do ordinal. Os 22 ids gravados precisam ser
   **reemitidos**, não corrigidos no lugar — o log é append-only. Enquanto isso não for
   feito, **nenhuma tabela `CLAIM_ID × CAPABILITY_ID` deve ser lida como verdade.**
2. **Corrigir `_sabido()`** para reconhecer a sentinela com sufixo (D8). É uma função, e
   destrava D1. Os 1.312 valores do acervo **não mudam** — muda quem os lê.
3. **Fechar a porta de entrada (D12, D13, D16):** validar `raw_state` em `admitir()`,
   usar `CAMPOS_EVENTO` como lista branca, e tirar a gramática de `IDENTITY_BASIS` das 18
   lambdas para uma função com teste.
4. **Herdar de `voz.py:106`** o desempate por posição na derivação de `ITEM_ID` (D2).
5. **Declarar o mapa `ÁREA → CAPABILITY_ID → CAP-###`** em documento, tirando-o do código.
   Sem inventar capacidade.
6. **Quebrar `TIME_STATE`** em `PUBLISHED_AT` · `OBSERVED_AT` · `CAPTURED_AT` ·
   `VALID_FROM` · `VALID_UNTIL`, cada um com estado próprio.
7. **Adotar `POLITICA-CANONICA-DE-CROP.md`** no passaporte e aposentar `CROP_STATE`.
8. **Transportar `ORIGINALIDADE`** para o passaporte e estendê-la além de vídeo.
9. **Dar campo próprio ao que hoje divide `REASON`** (D14): `CLAIM_TEXT`, `ROUTING_WHY`,
   `CROP`, `FACT_TIME`.
10. Só então reavaliar `FULL_BACKFILL`.

**Decisões que não são minhas e ficam abertas:** qual dos três conceitos fica com o nome
`FAMILY_ID`; qual língua vence em `EVIDENCE_CLASS`; e quem é o dono do mapa de capacidades.

## W · REMOTE_HEAD

Registrado no fim desta missão, em `PASSPORT-ESTADO-FINAL.txt`.

---

## O QUE ESTA MISSÃO **NÃO** FEZ

Portal · Vercel · produção · `CLIENT-DEMO` · Disease Intelligence · Label Intelligence ·
Supabase · coleta paga · ferramenta nova · recálculo de inteligência · cruzamento ·
backfill · `sintonia/canonical`.

**E não tocou nos 39 arquivos da missão em curso em `C:\eame-sintonia`.**
