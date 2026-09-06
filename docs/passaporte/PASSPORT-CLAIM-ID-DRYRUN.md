# DRY-RUN FINAL DA REEMISSÃO DE `CLAIM_ID`

**Data:** 2026-09-06 · **Branch:** `claude/passport-tags-italy-v1`
**Regra:** `CLAIM-ID-2026-09-06` · **Esquema:** `C_hibrido`

> **NADA FOI ESCRITO.** `data/passaporte/EVENTOS.jsonl` está intacto (`git status` do
> worktree de referência: 0 pendentes). Este documento prepara a reemissão e para.

---

## 1 · AS PROVAS EXIGIDAS

```
CLAIMS_REAL                        =  55        ✓ exigido 55
NEW_CLAIM_IDS                      =  55        ✓ exigido 55
COLLISIONS_AFTER                   =   0        ✓ exigido 0

DIRECT_ROUTES_TOTAL                =  48        ✓ exigido 48
DIRECT_ROUTES_RECOVERED            =  48        ✓ exigido 48
DIRECT_ROUTES_WRONG                =   0        ✓ exigido 0

ROUTES_POINTING_TO_MISSING_CLAIM   =   0        ✓ exigido 0
ORPHANED_ROUTES                    =  32
OLD_EVENTS_MODIFIED                =   0
```

Reproduzir:

```bash
python3 scripts/passaporte_claim_id.py dry-run --passaporte <ref> --esquema C_hibrido
```

---

## 2 · A TABELA

Preview completo, uma linha por afirmação, em
[`PASSPORT-CLAIM-ID-DRYRUN.json`](PASSPORT-CLAIM-ID-DRYRUN.json) (`TABELA`), com as
colunas pedidas: `OLD_CLAIM_ID` · `NEW_CLAIM_ID` · `CASE_ID` · `CLAIM_TEXT` ·
`EVIDENCE_REFERENCE` · `ROUTES_DIRECT_RECOVERED` · `ROUTES_BLOCKED_RECOVERED` ·
`ROUTES_UNRECOVERABLE_SHARED` · `REASON`.

O caso-testemunha:

```
OLD  CLAIM-3CA2E441A6D5FD7A-01
NEW  CLAIM-3CA2E441A6D5FD7A-CASE-005-6F47AD64
     CASE-005 · DIRECT=1 CONSUMED=1 BLOCKED_REC=0 UNRECOVERABLE_SHARED=2
     "CASE-005 — A safra francesa de 2024 vista pelo clima da própria região"

OLD  CLAIM-3CA2E441A6D5FD7A-01
NEW  CLAIM-3CA2E441A6D5FD7A-CASE-006-BC890C64
     CASE-006 · DIRECT=1 CONSUMED=1 BLOCKED_REC=0 UNRECOVERABLE_SHARED=2
     "CASE-006 — A mesma pergunta, a janela errada, a resposta invertida"
```

> **`ROUTES_UNRECOVERABLE_SHARED` é compartilhada de propósito.** As duas linhas acima
> mostram `2`, e são as **mesmas** duas órfãs: elas poderiam pertencer a qualquer uma das
> afirmações, e é exatamente isso que não sabemos. **Somar a coluna conta duas vezes.**
> O total honesto é `ORPHANED_ROUTES = 32`.

### As órfãs permanecem órfãs, e o motivo é gravado

Nenhuma órfã recebe dono inventado. No estado proposto elas ficam:

```json
{"CLAIM_ID": null, "CLAIM_LINK_STATE": "ORPHANED",
 "REASON": "rota sem chave local dentro de CLAIM_ID ambíguo —
            a qual afirmação ela pertencia não foi gravado"}
```

As 32 são **todas** `ROUTED_TO_CAPABILITY` → `OPPORTUNITY` → `BLOCKED`. Nenhuma rota que
afirma relevância se perde.

---

## 3 · OS PORTÕES SOBRE O ESTADO PROPOSTO

Rodados sobre a **simulação** (33.886 eventos), não sobre o log:

```bash
python3 scripts/passaporte_claim_id.py dry-run --simulado build/simulacao/ESTADO-PROPOSTO.jsonl …
python3 scripts/passaporte_portao_etiquetas.py --eventos build/simulacao/ESTADO-PROPOSTO.jsonl …
```

| portão | histórico | **estado proposto** |
|---|---|---|
| `CLAIM_ID_GATE` | **FAIL** — 12 colisões, 120 rotas | **PASS** — 55 claims, 55 ids, 0 colisões, 0 rotas ambíguas |
| `EVIDENCE_STATE_GATE` | PASS | **PASS** — 346 → 0 |
| `UNIVERSE_COMPLETENESS` | FAIL | **FAIL** — `EXPECTED_UNIVERSE_NOT_DECLARED` |

```
CLAIM_ID_GATE_PROPOSED_STATE = PASS
```

O histórico continuar `FAIL` é **esperado e correto**: ele contém os ids antigos e é
append-only.

> **A simulação não é versionada.** São 12,8 MB regeneráveis por um comando, e um arquivo
> `.jsonl` de eventos no repositório poderia ser confundido com o log canônico.
> `build/simulacao/` entrou no `.gitignore` com esse motivo escrito.

---

## 4 · UNIVERSO

```
EXPECTED_UNIVERSE  = NÃO DECLARADO   ← ninguém no repositório declara qual deveria ser
SCANNED_UNIVERSE   = data/samples
FILES              = 421
RECORDS            = 26.061
FINGERPRINT        = 0813535703856bddeaf446ea17b13a8f87ce7abe

UNIVERSE_COMPLETENESS = FAIL
MOTIVO                = EXPECTED_UNIVERSE_NOT_DECLARED
```

A impressão digital diz **o que foi varrido**. Ela não diz, e não pode dizer, se isso é
tudo. Enquanto não houver dono que declare o universo esperado, o portão fica vermelho —
mesmo com a digital calculada. Foi assim que `TRANSCRICOES-C/D/E` passaram despercebidos.

---

## 5 · PLANO DE REEMISSÃO — preparado, **não executado**

```
EVENTS_TO_APPEND      = 187
   CLAIMS_REISSUED    =  55     eventos CLAIM_ID_REISSUED sobre CLAIMS_EXTRACTED
   ROUTES_REISSUED    = 100     eventos CLAIM_ID_REISSUED sobre rotas e consumos
   ORPHANS_DECLARED   =  32     eventos CLAIM_LINK_ORPHANED
OLD_EVENTS_MODIFIED   =   0
```

Dois tipos de evento novos, e só dois:

```
CLAIM_ID_REISSUED     OLD_CLAIM_ID → CLAIM_ID · TARGET_EVENT_ID · RULE_VERSION · REASON
CLAIM_LINK_ORPHANED   OLD_CLAIM_ID · CLAIM_ID=null · TO_STATE=ORPHANED · REASON
```

**Append-only de verdade:** nenhum evento antigo é editado ou apagado. A identidade nova
é derivada dobrando o log — o evento antigo continua dizendo o que dizia, e o evento novo
diz para onde aquela identidade passou a apontar.

Artefato de inspeção: [`PASSPORT-CLAIM-ID-DRYRUN.json`](PASSPORT-CLAIM-ID-DRYRUN.json),
campo `EVENTOS_A_ACRESCENTAR` — os 187, prontos para leitura antes de qualquer escrita.

---

## 6 · AS TRÊS DECISÕES DE PRODUTO

### 6.1 · `FAMILY_ID` — três nomes, nenhum deles `FAMILY_ID`

| nome | significado | dono existente | universo onde tem dado |
|---|---|---|---|
| `EVIDENCE_FAMILY` | **natureza** da evidência | `scripts/v2_dedup_e_familias.py:47` (`FAMILIA`) | 2 arquivos em `data/` · 13 em `build/` |
| `DATASET_FAMILY` | **local** do dataset | `scripts/it_acervo_inventario_v2.py:53` (`FAMILIAS`) | todo o acervo, por caminho |
| `SOURCE_FAMILY` | **método** de coleta | `CONTRATO-DO-PASSAPORTE §1.2` — já se chama assim | **zero** em `data/`; 3.127 no log do passaporte |

**Prova de ortogonalidade, medida em 302 registros reais:** 8 de 14 `DATASET_FAMILY`
recebem **mais de um** valor de natureza de evidência.

```
CONCORRENCIA      → DERIVED_IDENTITY · DERIVED_SCOPE · PRIMARY_DECLARED_LINK · …
FONTES            → DERIVED_INTERPRETATION · PRIMARY_SOURCE_PROBE · SOURCE_HEALTH · …
GEOGRAFIA         → DERIVED_MEASUREMENT · PRIMARY_SOURCE · PRIMARY_SOURCE_PROBE · …
MERCADO           → OFFICIAL_MARKET_OBSERVATION · …
ROTULOS_PORTFOLIO → OFFICIAL_DOCUMENT · …
```

**E os três nem cobrem o mesmo universo.** Um `FAMILY_ID` único não misturaria só os
recortes — misturaria as **coberturas**, e o número resultante pareceria total sem ser
total de nada.

Nenhum dado foi migrado. `python3 scripts/passaporte_decisoes.py familias --acervo .`

> **Correção de uma frase que eu quase escrevi:** ia dizer que `BLOCO` *"não existe em
> `data/`"*. Existe — em dois arquivos (`IT-V2/IT-V2-CANONICO.json` e
> `IT-V2/IT-V2-QA-ATRIBUIDO.json`). Não é ausente; é **confinado ao V2**.

### 6.2 · `EVIDENCE_CLASS` — natureza, força e estado são três campos

```
EVIDENCE_CLASS     natureza   EVC-DOC · EVC-STAT · EVC-SCI · EVC-REG · EVC-MKT ·
                              EVC-FIELD · EVC-TABLE · EVC-IDENT · EVC-INTERP ·
                              EVC-SCOPE · EVC-MEAS · EVC-PROBE · EVC-RAW ·
                              EVC-DIR · EVC-CORPUS · EVC-COMM
EVIDENCE_STRENGTH  força      PRIMARY · OFFICIAL · SCIENTIFIC · DERIVED · UNKNOWN
EVIDENCE_STATE     estado     PROVED · UNKNOWN · CONTRADICTED · NOT_AVAILABLE ·
                              NOT_APPLICABLE · ERROR
```

O código é `EVC-###`, **neutro de idioma**. Português, italiano e inglês são
apresentação. O conflito medido some no código interno:

```
OFFICIAL_DOCUMENT (2.030)  →  EVC-DOC / OFFICIAL
DOCUMENTO_OFICIAL (2.030)  →  EVC-DOC / OFFICIAL       ← o mesmo par
```

**Mapeados: 18 de 24 valores.** E os 6 que sobram são o achado, não a sobra —
**o campo `EVIDENCE_CLASS` está carregando três conceitos ao mesmo tempo:**

| valor | o que é de verdade | ação |
|---|---|---|
| `PUBLIC_FREE_ROUTE` (2) | **rota de coleta**, não natureza | mover para `SOURCE_FAMILY` |
| `HUMAN_DECISION` (1) | decisão nossa, não evidência sobre o mundo | **NÃO SEI** — precisa de dono |
| `PRESERVATION_MANIFEST` (1) | declaração sobre o nosso processo | **NÃO SEI** — precisa de dono |
| `SOURCE_HEALTH` (1) | medição sobre a **fonte**, não sobre o mundo | **NÃO SEI** — precisa de dono |
| `PRIMARY_SOURCE_CONVERGENCE` (1) | o nome diz `PRIMARY`; convergência é **derivada** | **NÃO SEI** — os eixos brigam |
| `PRIMARY_DECLARED_LINK` (1) | declarado por nós (`DERIVED`) ou pela fonte (`PRIMARY`)? | **NÃO SEI** — decidir quem declara |

Mapear os seis teria escondido o defeito. Ficam `NÃO SEI`, com o motivo escrito.
Mapa em [`PASSPORT-EVIDENCE-CLASS-MAPA.json`](PASSPORT-EVIDENCE-CLASS-MAPA.json).

### 6.3 · `CAPABILITY_MAP` — confirmado por contagem

```
ATLAS-DE-CAPACIDADES-EAME.md         22 CAP distintos, 26 ocorrências   → VOCABULÁRIO
CONTRATO-DE-PROVA-DA-APRESENTACAO.md  3 linhas com CAP e CASE juntos    → RELAÇÃO
ARQUITETURA-DE-INFORMACAO-EAME.md    12 CAP, mas liga a ÁREA, não a CASE
italia-portale/                       0 ocorrências de CAP-xxx ou CAPABILITY_ID
```

```
CAPABILITY_MAP_OWNER = docs/apresentacao/CONTRATO-DE-PROVA-DA-APRESENTACAO.md
                       (relação capacidade → caso/evidência, campo CURRENT_EVIDENCE)
```

**O portal apenas renderiza — medido, zero ocorrências.** Há teste que cai se ele passar
a declarar. O que continua fora do lugar é `AREA_PARA_CAPACIDADE`, escondido em
`passaporte_backfill.py:858`.

---

## 7 · ENTREGA

```
BRANCH = claude/passport-tags-italy-v1
HEAD   = (ver git rev-parse HEAD)

CLAIMS_REAL                    =  55
NEW_CLAIM_IDS                  =  55
COLLISIONS_AFTER               =   0

DIRECT_ROUTES_RECOVERED        = 48/48
WRONG_DIRECT_ROUTES            =   0
ORPHANED_ROUTES                =  32   (todas OPPORTUNITY/BLOCKED)

CLAIM_ID_GATE_PROPOSED_STATE   = PASS
EVIDENCE_STATE_GATE            = PASS
UNIVERSE_COMPLETENESS          = FAIL  · EXPECTED_UNIVERSE_NOT_DECLARED

FAMILY_CONCEPTS_SEPARATED      = SIM   (EVIDENCE_FAMILY · DATASET_FAMILY · SOURCE_FAMILY)
EVIDENCE_CLASS_STATE_SEPARATED = SIM   (natureza · força · estado, em três campos)
CAPABILITY_MAP_OWNER           = docs/apresentacao/CONTRATO-DE-PROVA-DA-APRESENTACAO.md

EVENTS_TO_APPEND               = 187
CANONICAL_TOUCHED              = NÃO
EVENTOS_JSONL_TOUCHED          = NÃO

TESTS                          = 67 (28 leis + 39 regressões) · 67 passando

SAFE_TO_REISSUE                = SIM, com as três ressalvas abaixo
```

### `SAFE_TO_REISSUE = SIM` — e o que isso quer dizer

As provas técnicas passam: 55 identidades, zero colisões, zero rotas erradas, zero rotas
apontando para claim inexistente, zero eventos antigos modificados, e o portão passa no
estado proposto. **A operação é reversível por construção** — é só acréscimo.

**Não quer dizer que o passaporte fica pronto.** Quer dizer que *esta* correção pode ser
aplicada sem perder nada além do que já está declarado como perdido.

### BLOCKERS

1. **32 rotas perdem o vínculo, e 13 afirmações ficam sem saber se tiveram bloqueio de
   `OPPORTUNITY`.** É perda real. É preferível à ambiguidade — e continua sendo perda.
2. **`UNIVERSE_COMPLETENESS = FAIL`** e não pode ser resolvido por mim: exige um dono que
   declare qual é o universo esperado.
3. **Seis valores de `EVIDENCE_CLASS` ficam `NÃO SEI`**, três deles porque o campo está
   carregando conceito que não é dele.
4. `AREA_PARA_CAPACIDADE` continua em código, competindo com o dono declarado.
5. Sem `pytest`/`pip` neste ambiente: a suíte antiga do repositório é `NAO_MEDIDO`.
6. **A reemissão não foi executada.** Aguardando autorização.
