# IDENTIDADE DO ARTEFATO — CAMINHO · CAPTURA · CONTEÚDO · CÓPIA · DERIVADO

**Censo e decisão de modelo** · 2026-09-08 · ramo `claude/italia-biblia-integracao-v1`

> **Nada foi escrito, copiado, migrado ou apagado.** Zero `INSERT`/`UPDATE`/`DELETE`, zero
> upload, zero migration aplicada, zero DDL. Este documento mede e decide — não executa.

---

## O ERRO QUE ESTE CENSO CORRIGE

O censo anterior contou certo e explicou errado:

```
49 caminhos de PDF  →  43 conteúdos SHA-256 diferentes
```

e concluiu, em prosa, que os seis excedentes eram *«o mesmo documento guardado em dois
sítios»* — a loja do coletor e a amostra versionada. Isso era um palpite lido no **nome da
pasta**, com cara de facto medido.

> ## CAMINHO DIFERENTE NÃO PROVA CAPTURA DIFERENTE.
> ## SHA IGUAL NÃO PROVA A MESMA CAPTURA.

A decisão passou a ser tomada pela **prova de captura** de cada caminho, em
[`censo_de_identidade_it.py`](../../system-map/scripts/censo_de_identidade_it.py).

---

## A · AS CINCO ESPÉCIES

| espécie | o que é | identidade | pode repetir? | quem a cria |
|---|---|---|---|---|
| **CONTENT** | os bytes | `SHA-256` | não — é o que dá identidade | ninguém; nasce da fonte |
| **CAPTURE** | uma ida à fonte, num instante, por uma rota | `(registo, corrida/pacote, URL, quando)` | **sim** — o mesmo conteúdo pode ser buscado 10 vezes | o coletor, ou a mão com `curl` |
| **STORAGE COPY** | um lugar onde os bytes ficaram | o caminho / `storage_path` | **sim** — e o caminho muda sem o conteúdo mudar | quem escreveu no disco |
| **ARTIFACT** | o objeto preservado com a sua procedência | `SINTONIA ID` estável | — | a corrida |
| **DERIVED ARTIFACT** | o que uma ferramenta fez a partir de um pai | `SHA-256` do filho + pai | sim, uma por versão de ferramenta | o executor |

**Nenhuma chave nasceu por conveniência.** O caminho **não** é identidade de conteúdo
(muda de nome sozinho). O `SHA-256` **não** é identidade de captura (duas idas trazem o
mesmo hash). A URL **não** é identidade de fonte (COL-LAW-205).

---

## B · OS SEIS GRUPOS REPETIDOS — CLASSIFICADOS PELA PROVA

```
6 grupos com mais de uma cópia

6 de 6   INDEPENDENT_CAPTURES_SAME_CONTENT
0 de 6   SAME_CAPTURE_MULTIPLE_STORAGE_COPIES
0 de 6   UNKNOWN
```

| conteúdo | captura A | captura B | intervalo |
|---|---|---|---|
| `0c2723e66201` | amostra `curl` 07/09 13:49:59Z | coletor piloto 07/09 15:37:53Z | 1 h 48 |
| `3d3c1bc0e963` | amostra `curl` 07/09 14:31:58Z | coletor piloto 07/09 15:37:44Z | 1 h 06 |
| `420e08ef15be` | **pacote VPN 02/09**, via Fitogest | amostra `curl` 07/09 13:49:59Z | **5 dias, outra rota** |
| `59da05274359` | amostra `curl` 07/09 14:49:05Z | coletor piloto 07/09 15:37:57Z | 0 h 49 |
| `e612807928b5` | amostra `curl` 07/09 14:36:30Z | coletor piloto 07/09 15:38:27Z | 1 h 02 |
| `f88c89d73d6a` | amostra `curl` 07/09 14:31:58Z | coletor piloto 07/09 15:37:42Z | 1 h 06 |

**A prova não é auto-declarada.** O próprio servidor datou a resposta:

```
HTTP/1.1 200 OK
date: Mon, 07 Sep 2026 13:49:52 GMT
last-modified: Thu, 03 Sep 2026 13:54:16 GMT
```

— em `data/samples/IT-SOURCE-SAMPLES/IT-T3-002/SA-02-09.pdf.headers.txt`. É um terceiro a
confirmar a hora, não nós.

> **E isto vale mais do que a contagem.** Duas capturas do mesmo byte em dias diferentes são
> a prova de que **o documento não mudou nesse intervalo**. Um esquema que guardasse «um
> caminho por conteúdo» apagaria uma captura verdadeira, e com ela essa prova.

### O que ficou por provar

**11 das 49 cópias não têm prova de captura em registo nenhum** — 9 em
`data/samples/IT-ARPAV-VENETO/` e 2 em `data/samples/PIEMONTE-FD/`. Pacotes antigos, sem
manifesto. Isso não afeta a contagem nem os seis grupos (nenhuma delas é repetida), mas é
procedência em falta e fica registada como **G-40**. `UNKNOWN` continua `UNKNOWN`.

---

## C · O SUPABASE — O QUE O ESQUEMA VERSIONADO PROVA

### Base de prova desta sessão

| | |
|---|---|
| **Esquema versionado** (`supabase/migrations/001–021`) | ✅ lido e medido aqui |
| **Banco LIVE** | ❌ **sem credencial nesta sessão** |
| **Medição LIVE do coordenador** | registada como `EXTERNAL_MEASUREMENT`, **não** como observação nossa |

`LIVE_STATE = PARTIAL`. Subiu de `UNKNOWN` porque agora há **duas** fontes que concordam
sobre a estrutura — o esquema versionado, que esta sessão leu, e a medição externa. Não sobe
a `KNOWN` porque as **linhas** (8 / 251 / 0 / 0) esta sessão não as viu.

### `raw_asset` — o diagnóstico anterior estava errado

| pergunta | resposta | prova |
|---|---|---|
| `sha256` é `UNIQUE`? | **NÃO** | `001:119` — `create index raw_hash_idx on public.raw_asset (sha256)`. Índice, não trava |
| `storage_path` é `UNIQUE`? | **SIM** | `001:106` — `text not null unique` |
| duas linhas com o mesmo `sha256`? | **SIM, permitido** | não há constraint que o proíba |
| qual é o grão? | **um objeto guardado**, com a captura que o trouxe na mesma linha | `storage_path` é a chave; `run_id`, `captured_at` e `source_url` descrevem a ida |

> **Correção explícita.** O censo P-011 de ontem escreveu que `raw_asset` *«guarda um caminho
> por conteúdo»* e que os 6 pares **não cabiam lá**. Está errado, e o erro foi meu: eu li o
> `unique` do `storage_path` como se fosse do `sha256`. **É o contrário.** A tabela guarda um
> caminho por **caminho**, e aceita o mesmo conteúdo em quantas linhas forem precisas.

**Consequência:** os 49 caminhos entram como **49 linhas** de `raw_asset`, com 43 valores
distintos de `sha256`, **sem alterar uma vírgula do esquema**.

E a fusão CAPTURA+CÓPIA numa linha só é inofensiva **para todos os casos que temos**: os 6
grupos são `INDEPENDENT_CAPTURES`, ou seja **uma captura → uma cópia** em cada linha. A fusão
só quebraria no caso `SAME_CAPTURE_MULTIPLE_STORAGE_COPIES`, e desse temos **zero**.

> **Não se constrói tabela para um caso que a medição diz não existir.** Se ele aparecer um
> dia, aparece com prova, e aí decide-se — é a REGRA ZERO aplicada ao esquema.

### `conteudo_visto_em` — resolve o conceito, na entidade errada

```sql
conteudo_id + run_id + visto_em      UNIQUE (conteudo_id, run_id)
```

O comentário da 016 já diz a lei madura: *«o mesmo conteúdo visto em duas rodadas são DUAS
observações e UM conteúdo»* — exatamente o que os nossos 6 grupos provam.

**Mas `conteudo_id` não são bytes.** É uma linha de `public.conteudo`, cuja chave é
`UNIQUE (canal_id, content_id)` — **canal + id da plataforma**. É a espécie «item de canal»
(um vídeo, um post), não a espécie «blob». O `hash_conteudo` está lá, mas só como **índice**,
não como identidade.

**Veredito: `PARCIAL`.** O conceito está resolvido e escrito; a entidade em que ele vive é
outra. Para os PDFs italianos, o papel de «duas observações, um conteúdo» já é desempenhado
por **duas linhas de `raw_asset` com o mesmo `sha256`** — e isso não precisa de tabela nova.

> **Não colapsar `conteudo` com `CONTENT`.** Um PDF de uma região italiana não tem canal nem
> `content_id` de plataforma. Forçá-lo para dentro de `conteudo` obrigaria a inventar um
> canal falso — dado inventado para caber num esquema é a pior espécie de dívida.

---

## D · O DERIVADO — a única dívida real

O contrato do derivado **já existe inteiro nos ficheiros**. Medido em
`data/derivados/REGISTO-DE-ARTEFATOS.json`: **43 de 43** com linhagem completa —

```
PARENT_ARTIFACT_ID · PARENT_SHA256 · DERIVATION_TYPE
EXECUTOR_ID · EXECUTOR_VERSION · PIPELINE_VERSION · DERIVED_AT
```

e 6 deles declaram **mais de um lugar do pai** em `PARENT_STORAGE_LOCATIONS` — o mesmo facto
dos seis grupos, visto do lado do filho.

### O que existe no banco, e por que não serve

| tabela | o que é | serve? |
|---|---|---|
| `transcricao` (003) | derivado, mas **de vídeo**: chave `conteudo_id + idioma + caption_source` | ❌ é o filho errado |
| `catalogo_produto_documento` (014) | documento de produto, com `raw_asset_id` e estado de download | ❌ é catálogo de fabricante, não derivação |
| `derivacao` (005) | **conclusão analítica** — `pergunta`/`resposta`/`limitação` | ❌ o nome engana: é raciocínio, não artefato |

**Não existe estrutura genérica de artefato derivado.** É a única lacuna que o censo
encontrou.

> ### E `raw_asset` NÃO PODE VIRAR A TABELA UNIVERSAL.
> Seria fácil acrescentar-lhe `parent_sha256` e meter lá o texto derivado. Seria também
> apagar a `COL-LAW-007` — **RAW não é DERIVADO** — dentro da tabela chamada `raw_asset`.
> Uma tabela chamada «bruto» com filhos dentro mente para todo o leitor futuro. **Não fazer.**

---

## E · A DECISÃO DE ESQUEMA — O MENOR DELTA POSSÍVEL

> ## RESPOSTA: **C — `ADICIONAR_APENAS_DERIVED_ARTIFACT`**

| opção | veredito |
|---|---|
| **A** `SCHEMA_ATUAL_JA_BASTA` | quase — falha só no derivado |
| **B** reusar tudo + extensão de `RUN` | as colunas de `RUN` são conforto, não bloqueio |
| **C** só `derived_artifact` | ✅ **escolhida** |
| **D** `STORAGE_COPY` | ❌ **não é preciso** — `raw_asset` já é esse grão |
| **E** `CAPTURE_OCCURRENCE` | ❌ **não é preciso** — `sha256` não-único já permite N capturas por conteúdo |

### O que pensávamos precisar e NÃO precisamos

**A tabela de ocorrência.** O censo de ontem deu-a como bloqueador. Ela não existe porque
não é necessária: a trava que a tornaria necessária (`sha256 UNIQUE`) **nunca esteve lá**.

### O que cabe hoje, sem tocar em nada

| o quê | onde | como |
|---|---|---|
| 6 corridas do piloto + a corrida do Golden Path | `collection_run` | `run_id`, `actor`, `started_at`, `finished_at`, `capture_method` |
| `COST_BASIS` da estrada gratuita | `cost_method` | ⚠️ o valor `ROTA_GRATUITA_PROVADA` **não está no enum** — decisão do dono |
| 49 cópias / 24 capturas / 43 conteúdos | `raw_asset` | 49 linhas, `storage_path` único, `sha256` repetido onde tem de ser |
| bytes | bucket `raw` (privado) | `storage_path` aponta lá |

### O que NÃO cabe

| o quê | por quê |
|---|---|
| 43 textos derivados | não há tabela de artefato derivado |
| `RUN_STATE` + `COMPLETION_BASIS` | não há coluna — cabe num `jsonb`, ou colunas próprias |
| `STATE_BEFORE` / `STATE_AFTER` | idem |
| `GIT_COMMIT` · `BIBLE_VERSION` · `PREFLIGHT` | idem (é a COL-LAW-211, que já está `PARTIAL`) |

---

## F · A MIGRATION FUTURA — PROJETADA, NÃO APLICADA

⚠️ **Este SQL não foi executado em lado nenhum.** É aditivo: sem `DROP`, sem `DELETE`, sem
`ALTER` destrutivo. Fica aqui para ser testado num Postgres local e descartável primeiro.

```sql
-- ═══════════════════════════════════════════════════════════════════════
-- MIGRATION 022 (PROJETADA — NÃO EXECUTADA)
-- O ARTEFATO DERIVADO GANHA CASA
--
-- RAW != DERIVED e por isso NAO entra em raw_asset. Uma tabela chamada
-- "bruto" com filhos la dentro mentiria para todo leitor futuro.
--
-- O pai identifica-se pelos BYTES (sha256), nao pelo caminho: o mesmo
-- conteudo foi capturado duas vezes e vive em dois caminhos, e o filho e
-- do CONTEUDO, nao de uma das copias.
-- ═══════════════════════════════════════════════════════════════════════

create table if not exists public.derived_artifact (
  id                bigserial primary key,
  run_id            text not null references public.collection_run(run_id) on delete restrict,

  -- O PAI E O CONTEUDO, NAO A COPIA. parent_raw_asset_id e opcional e diz
  -- apenas "foi desta copia que se leu" — nunca substitui o sha256.
  parent_sha256     char(64) not null,
  parent_raw_asset_id bigint references public.raw_asset(id) on delete set null,

  derivation_type   text not null check (derivation_type in
                    ('TEXT_EXTRACTION','OCR','TRANSLATION','TABLE_EXTRACTION','OTHER')),
  derivation_actor  text not null,          -- texto-de-pdf
  derivation_version text not null,         -- 1
  pipeline_version  text not null,
  derived_at        timestamptz not null,

  sha256            char(64) not null,      -- do FILHO
  bytes             bigint not null,
  media_type        text not null,
  storage_path      text unique,            -- NULL enquanto o byte nao subiu

  state             text not null check (state in
                    ('TEXT_LAYER_PRESENT','NEEDS_OCR','EXTRACTION_ERROR')),
  error             text,

  -- MESMO PAI + MESMA FERRAMENTA + MESMA VERSAO = MESMO FILHO. Reprocessar
  -- com a MESMA versao nao cria linha nova; mudar de versao cria.
  CONSTRAINT derivado_unico_por_pai_e_versao
    UNIQUE (parent_sha256, derivation_type, derivation_actor, derivation_version),

  -- ERRO NAO VIRA BYTE. Um filho que falhou nao pode fingir que tem conteudo.
  CONSTRAINT erro_nao_vira_byte_preservado
    CHECK (state <> 'EXTRACTION_ERROR' OR (storage_path IS NULL AND error IS NOT NULL))
);

create index derived_parent_idx on public.derived_artifact (parent_sha256);
create index derived_run_idx    on public.derived_artifact (run_id);
alter table public.derived_artifact enable row level security;

comment on table public.derived_artifact is
  'O que uma ferramenta fez a partir de um conteudo bruto. RAW nao e DERIVED: por isso '
  'esta tabela existe em vez de uma coluna em raw_asset. O pai identifica-se pelos bytes, '
  'porque o mesmo conteudo pode estar em mais de um caminho.';

comment on column public.derived_artifact.parent_raw_asset_id is
  'De QUAL copia se leu, quando se sabe. Informativo. A linhagem verdadeira e o '
  'parent_sha256 — a copia pode ser apagada sem que o filho perca o pai.';
```

---

## G · O QUE ESTA MISSÃO NÃO FEZ, DE PROPÓSITO

```
migration aplicada          0
escritas no Supabase        0
uploads para o bucket       0
deletes                     0
bytes italianos copiados    0
corrida italiana LIVE       0
tabela criada por reflexo   0
```

A Itália **não** foi migrada. Esta missão termina **antes** da primeira escrita italiana.

---

## H · ACHADO DE INFRAESTRUTURA — DERIVA DOS CABEÇALHOS

**21 de 21 migrations dizem `NÃO EXECUTADA` no cabeçalho.** A medição externa mostra
`conteudo_visto_em` (criada pela 016) **existente no banco**, e `collection_run` com linhas.
Logo, pelo menos 001–016 **estão aplicadas**.

Isto é **deriva de comentário**, não ausência de esquema.

> **Migration é história e não se reescreve.** Corrigir 21 cabeçalhos apagaria o que era
> verdade no dia em que foram escritos. O que falta é outra coisa: um lugar onde se leia
> **o que está aplicado agora** — e esse lugar não é o cabeçalho de um ficheiro de 2026-08.

Registado como **G-41**. Nenhuma migration foi alterada.

---

## I · CUSTO — registado, não reaberto

`collection_run` tem `cost_usd` + `cost_method`, com `custo_declarado_diz_como_foi_medido` e
`NULL ≠ 0`. Se a estrada italiana escrever `0.0`, precisa de um método compatível — e
`ROTA_GRATUITA_PROVADA` **não está no enum de quatro valores**. **Decisão do dono, e não
bloqueia este modelo.**

---

## J · O QUE AINDA TEM DE SER PROVADO ANTES DE COPIAR UM BYTE

1. Ler o banco **LIVE** desta sessão, com credencial — `LIVE_STATE` tem de chegar a `KNOWN`.
2. Testar a `022` num Postgres local e descartável, do zero.
3. Decidir `ROTA_GRATUITA_PROVADA` no enum de `cost_method`.
4. Conferir `sha256` de cada byte copiado, um a um, depois da cópia.
5. Contar no **destino**: 49 cópias · 43 conteúdos · 43 derivados · `LOST = 0`.
