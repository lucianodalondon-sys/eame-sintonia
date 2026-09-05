# IT-SUPABASE-RECOVERED-V1 · reconciliação e pacote de coleta

**Lote:** `IT-SUPABASE-RECOVERED-V1` — 195 objetos italianos preservados no Supabase
(bucket `raw`, prefixo `IT/adama-website/`), tratados como **leva de coleta externa
recuperada**, não como coleta nova.

**Pacote:** `CP-IT-SUPABASE-RECOVERED-V1-d26c1c295a3b` · estado `SEALED_SHADOW_ONLY`
**Captura (histórico preservado):** 2026-08-30T19:18:30Z → 2026-08-30T19:21:36Z
**Esta missão para no COLLECTION_PACKAGE.** Nada foi entregue à Inteligência.

---

## O que esta missão não tocou

| Alvo | Estado |
|---|---|
| Supabase | **não contactado** — não existe credencial neste ambiente |
| Motor de inteligência atual | inalterado |
| Portal | inalterado |
| Canário / `sintonia/canonical` | não tocados |
| Os 43 casos | não alterados |
| Escrita | só `data/recuperacao/` e `docs/recuperacao/`, na branch isolada |

O `PRE_PASSPORT` é `SHADOW_ONLY` e todo estado estrutural é `PROVISIONAL_V0`.

---

## Como a reconciliação foi feita sem ler nada

`data/raw/` é ignorado por política do repositório (D-003), então **nenhum dos 195
arquivos é um blob Git** — casar por conteúdo devolve 0, e isso é o esperado, não uma
falha. O cruzamento foi feito por **identificador**, contra as pontas das 48 refs
(2.744 blobs distintos, 314 MB), na ordem: SHA256 → URL de origem → identificador
documental (`/media/<id>/`) → caminho de storage → nome de arquivo → nome de produto.

A âncora é `data/samples/IT-CATALOGO/IT-ADAMA-PRESERVACAO-RELATORIO.json`
(branch `claude/adama-it-local-catalog`), que carrega os 195 SHA256 verificados no
round-trip: `GATE=CLOSED`, `SHA_VERIFIED=195`, `HASH_MISMATCH=0`,
`BYTES_VERIFIED_REMOTELY=80.714.570`.

**Nenhum PDF foi aberto nesta missão.** 58 objetos foram poupados de leitura por prova
de leitura anterior; os 137 restantes entram em fila de handoff, não de trabalho aqui.

---

## Contabilidade — fecha em 195

### Reconciliação (um estado principal por objeto, chaveado por `STORAGE_PATH`)

| Estado | N | Base |
|---|---:|---|
| `ALREADY_CONSUMED` | **53** | 51 PRODUCT_DOM parseados em `PRODUCTS-COMMERCIAL.json` (canônico) + 2 PDFs byte-idênticos a etiquetas ministeriais já lidas |
| `SAME_EVIDENCE_DIFFERENT_REPRESENTATION` | **95** | 90 PDFs com texto extraído no censo local + 5 artefatos de crawl com derivação `ROBOTS`/`ENUMERATION` |
| `AMBIGUOUS` | **40** | ETICHETTA cujo registro tem etiqueta ministerial lida no acervo, mas com SHA256 diferente |
| `KNOWN_NOT_CONSUMED` | **7** | catalogados no canônico por SHA256, sem nenhuma derivação de conteúdo |
| `ALREADY_ACCOUNTED` | 0 | — |
| `SUPABASE_ONLY` | 0 | — |
| `UNKNOWN` | 0 | — |
| **Total** | **195** | |

### Filtragem técnica de coleta (Fase 3)

| Decisão | N | Motivo |
|---|---:|---|
| `KEEP` | **186** | objeto válido, preservado e verificado byte a byte |
| `DEFER` | **9** | a extração de texto foi tentada e devolveu vazio (`CONTENT_READABLE=false`); precisa de resolução técnica |
| `REJECT_WITH_REASON` | **0** | — |
| `ERROR` | **0** | — |
| **INPUT** | **195** | fecha |

Nada foi rejeitado por juízo de valor. Os 5 artefatos de crawl (robots.txt, sitemap,
captura da home, dois manifestos) são **KEEP**: são prova de proveniência, não lixo
técnico — o `robots.txt` é justamente o que explica por que o censo documental é
incompleto.

Os 40 `AMBIGUOUS` são **KEEP**, não `DEFER`: são tecnicamente válidos. O que está em
aberto é a relação deles com outro documento, e isso é reconciliação, não filtro técnico.

### Conteúdo (Fase 5)

| Estado | N |
|---|---:|
| `CONTENT_READ` | 53 |
| `CONTENT_PARTIAL` | 133 |
| `CONTENT_UNREADABLE` | 9 |
| **Total** | **195** |

`CONTENT_PARTIAL` é literal: o censo local extraiu texto de 130 PDFs e usou esse texto
só para decidir tipo de documento (84 casos) e detectar produtos nomeados (16 casos).
O corpo do rótulo — doses, culturas, prescrições — nunca foi capturado.

---

## As quatro camadas

| Pergunta | Resposta |
|---|---|
| **A · existe no Git/acervo?** | Sim para 190/195 por SHA256 em `sintonia/canonical` (`LABEL-MANIFEST.json` 139 + `PRODUCTS-COMMERCIAL.json` 51). Os 5 restantes existem em forma derivada, só na branch local. |
| **B · existe como evidência/derivação no motor?** | 51 consumidos de verdade; 2 lidos por outra rota; 90 com derivação rasa presa a uma branch; 7 sem derivação. |
| **C · sustenta algum dos 43 casos?** | **Não.** Nenhum dos 43 casos de `italia-portale/client/meeting-intelligence-snapshot.json` cita um destes objetos por SHA256, storage path ou `media/<id>`. Os casos resolvem evidência contra outro corpus (`IT-LBL-*` → `data/samples/IT-ROTULOS-V1/`, chaveado por número de registro). A sobreposição é de 4 nomes de produto em 14. |
| **D · aparece no portal?** | Só na superfície. Em 434 blobs de portal nas 48 refs: **zero** SHA256, **zero** `IT/adama-website`, **zero** URLs `media/<id>/download`. O portal cita produto por URL pública, nome e número de registro ministerial. Aparecer no portal **não prova** passagem pelo motor. |

---

## Custo e run

`COST_STATE = FREE_PROVED`. Todo artefato de custo do repositório
(`RUN-MANIFEST*.json`, `corrigir_custo.py`, `recuperar-runs-pagos.yml`,
`data/samples/raw-paid/*`) tem **zero** ocorrências de "adama" e é escopado a atores
Apify de LinkedIn/YouTube/Instagram. O relatório de preservação declara captura por
Chrome local *headed* (`BROWSER_ROUTE.STATE = HEADED_ONLY`) contra catálogo público, e
preservação por runner self-hosted. Não há vendor pagável na rota.

`RUN_STATE = NO_COLLECTION_RUN_ROW_IN_DB` — a preservação foi feita por
`scripts/adama_it_preservar.py`, sem linha de run no banco.

`GENUINELY_NEW_TO_ACERVO = 0`. Nenhum dos 195 é novidade para o acervo.

---

## O que a verificação adversarial derrubou

Seis afirmações foram submetidas a céticos independentes com instrução de refutar. Duas
caíram, e as duas mudaram a classificação:

1. **"Nenhum PDF foi parseado"** — falso. Dois objetos (`050f6cf2…` Avastel / media 6766
   e `55634b79…` Mavrik Smart / media 4041) são **byte-idênticos** a etiquetas
   ministeriais lidas por inteiro em `data/samples/IT-ROTULOS-V1/testo/*.txt` +
   `geometria/*.xml.gz` nas branches `sprint/*`, com data de rótulo extraída
   (2025-06-27 e 2025-07-30). O `PARSE_STATE=NOT_PARSED` do canônico descreve a rota
   adama.com (bloqueada por 403), não o repositório inteiro.

2. **"Os 5 artefatos de crawl são SUPABASE_ONLY"** — falso. Conteúdo derivado do sitemap
   e do robots.txt está commitado em ~16 refs, incluindo `sintonia/canonical`
   (`ALL_DOCUMENTS_ROUTE_STATE=ROBOTS_DISALLOWED` nos 51 produtos). Só os bytes crus são
   exclusivos do Supabase — e por esse critério todos os 195 seriam.

O crítico de completude ainda derrubou a partição original: **130 dos 139 PDFs tiveram
texto extraído** pelo censo local, então "nunca parseado" era falso para 130 objetos, não
só para os 2. A partição foi refeita sobre isso.

Sobrevivem com alta confiança: o consumo real dos 51 PRODUCT_DOM, a ausência de ligação
com os 43 casos, a natureza gratuita da coleta e a superficialidade do portal.

---

## Achado estrutural: regressão de linhagem

O registro **rico** deste lote — `IT-ADAMA-CATALOG-CENSUS.json`, com texto extraído de
130 PDFs, blocos `ROBOTS` e `ENUMERATION`, linhas de dose e janela — existe em **uma
única ref**: `claude/adama-it-local-catalog`.

O registro **pobre** — `LABEL-MANIFEST.json`, com `PARSE_STATE=NOT_PARSED` nas 141
entradas — é o que chegou a `sintonia/canonical`, e está em 15 refs.

**O canônico afirma menos do que o acervo de fato sabe.** Quem consultar só o canônico
vai concluir que nada foi lido, e vai reler 130 PDFs sem necessidade. Isto é um risco de
desperdício, não um detalhe de arquivo.

---

## Limitações declaradas

- Supabase não foi contactado: não há credencial neste ambiente.
- Os bytes dos 195 não são alcançáveis daqui (`data/raw/` ignorado; adama.com devolve
  403, registrado em `LABEL-MANIFEST.RECOVERY`). **Nenhum conteúdo foi lido nesta missão.**
- O censo é incompleto por `robots.txt`: a rota `*/ajax/` que lista "Tutti i documenti"
  de cada produto nunca foi buscada. **Podem existir documentos além destes 139.**
- 195 objetos carregam **194 SHA256 distintos** — o mesmo PDF de 138.284 bytes é servido
  como dois documentos (Postscript 80 XL e Davai). A partição é chaveada por
  `STORAGE_PATH`, nunca por hash. O acervo já registrou isso como fato a preservar.
- Os 40 `AMBIGUOUS` exigem comparação de **versão** de rótulo, não só de registro.
- Não se sabe por que 9 PDFs devolveram texto vazio.
- A varredura cobriu as pontas das 48 refs; ~71 blobs existem só em commits
  intermediários e não foram pesquisados.

---

## Fila de leitura — handoff, não trabalho pendente

`READ_QUEUE_SIZE = 137` (70,3% dos 195) · `AVOIDED_READING = 58`

A fila **não é executável neste ambiente** e não deve ser interpretada como crosswalk
fraco: 190 dos 195 casaram em **Tier A (SHA256)**. A fila é grande porque o acervo
genuinamente nunca leu o corpo destes documentos — é um achado, não uma lacuna de método.

Ordem de leitura quando houver acesso aos bytes: `ESTENSIONE_USO` → `COMUNICAZIONE` →
`ETICHETTA` → `SCHEDA_DI_SICUREZZA` → `BROCHURE` → `LEAFLET`. Texto nativo primeiro;
OCR só para os `CONTENT_UNREADABLE`; nunca chamar modelo onde o parser determinístico
resolve.

---

## `READY_FOR_INTELLIGENCE = NO`

O pacote está contabilizado, selado e íntegro — mas a entrega depende de acesso aos
bytes e, pela ordem acordada, de fechar antes o canário, a linhagem canônica e a
inteligência já processada.

### `NEXT_RECOMMENDED_ACTION`

Avaliar obrigatoriamente `claude/adama-it-local-catalog` no **P0.2 · PASSO 02**, contra o
HEAD canônico atual.

**NÃO promover automaticamente.**

Primeiro medir:

- ganho incremental;
- preservação dos registros ricos já existentes;
- conflitos semânticos;
- perda;
- regressões;
- consumidores afetados, quando aplicável.

Somente se passar os portões do P0.2: integrar → reconciliar novamente o
`COLLECTION_PACKAGE` → recalcular a `READ_QUEUE` → então determinar quantos documentos
realmente ainda precisam ser lidos.

**`READ_QUEUE = 137` é teto provisório, não medida final.** 130 desses documentos já têm
texto extraído numa ref que ainda não foi integrada; o número real só se conhece depois
da reconciliação pós-integração.

**`REUSE_PROVED_EXISTING_READING_BEFORE_NEW_READING = SIM`.** Honrado neste lote: 58
objetos poupados de releitura, 0 lidos nesta missão.

---

## Entregáveis

| Arquivo | Conteúdo |
|---|---|
| `data/recuperacao/IT-SUPABASE-RECOVERED-V1-CROSSWALK.jsonl` | 195 linhas · quatro camadas, método e evidência por objeto |
| `data/recuperacao/IT-SUPABASE-RECOVERED-V1-ENVELOPE.jsonl` | 195 linhas · envelope de coleta + decisão técnica |
| `data/recuperacao/IT-SUPABASE-RECOVERED-V1-PRE-PASSPORT.jsonl` | 195 linhas · pré-passaporte `PROVISIONAL_V0` |
| `data/recuperacao/IT-SUPABASE-RECOVERED-V1-READ-QUEUE.json` | fila de 137, priorizada |
| `data/recuperacao/IT-SUPABASE-RECOVERED-V1-COLLECTION-PACKAGE.json` | pacote formal selado |
