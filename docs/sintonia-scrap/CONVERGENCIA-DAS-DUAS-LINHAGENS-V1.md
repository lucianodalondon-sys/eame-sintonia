# AN · AO — AS DUAS LINHAGENS, E COMO CONVERGEM SEM MERGE CEGO

> **MEDIDO_EM:** 2026-09-11. Cada linha tem `md5` de conteúdo, commit, ou o comando que a
> produziu. **Nada foi executado**: este documento propõe, não converge.
>
> **A · linhagem SCRAP** = `origin/claude/sintonia-scrap-stories-no-apify-v1` (`2d38a558`)
> **B · linhagem EAME** = `claude/jolly-archimedes-lqpvlf` (HEAD), onde correu a frente de Reels

---

## O MÉTODO NÃO PRECISA DE SER INVENTADO — A CASA JÁ O USOU

Em `ebcdb230` (2026-09-09) a linhagem B resolveu exatamente este problema, e escreveu como:

```
ferramentas/apify_contrato.py    importadores 0 · workflows 0
ferramentas/apify_recuperar.py   importadores 0 · workflows 0
e as saídas que as duas declaravam NUNCA existiram no disco.
```

> *«As duas saíram. SEM STUB: não fica um ficheiro vazio a dizer "deprecated", que seria
> código morto com outra roupa. O git guarda a história. […] A LEI NÃO MORRE COM O
> FICHEIRO. […] A ferramenta morta era o DUPLICADO; a viva ficou.»*

**O critério é medível e é este:** contar importadores · contar workflows · verificar se a
saída declarada existe no disco · perguntar quem é o dono vivo do CONCEITO. A lei
sobrevive ao ficheiro.

É o critério que a matriz abaixo aplica.

---

## AN · MAPA DAS DUAS LINHAGENS

`md5` dos primeiros 8 hex do conteúdo, medido com `git show <ref>:<path> | md5sum`.

| componente | A · SCRAP | B · HEAD | iguais? | conflito |
|---|---|---|---|---|
| `coleta/social_persistencia.py` | `841d2cd0` | `841d2cd0` | **SIM** | nenhum |
| `ferramentas/contrato_ator.py` | `8f77afaf` | `8f77afaf` | **SIM** | nenhum |
| `ferramentas/apify_pool.py` | `7a437ba2` | `7a437ba2` | **SIM** | nenhum |
| `coleta/social_rotas.py` | `a067b8b1` | `80c4caf3` | não | divergiu |
| `coleta/social_scrap.py` | `9e371617` | `4e5505f6` | não | A tem `stories()`, +70 linhas |
| `leis/social_matriz.py` | `5a163711` | `4968a06e` | não | divergiu |
| `guarda/social_sessao.py` | `aa031c9d` | `d2291820` | não | **A tem conserto de segredo que B não tem** |
| `coleta/social_envelope.py` | `22442ba7` | `d43f180a` | não | divergiu |
| `orquestrador/orquestrador.py` | `f0fe559a` | `a6412431` | não | **acima do SCRAP — fora de escopo** |
| `pedido/receitas.py` | `23633a48` | `164069ae` | não | B registou `fase=transcrever` |

### Só numa das linhagens

| componente | onde | função | prova viva |
|---|---|---|---|
| `ferramentas/fala_local.py` | **só B** | dono único de ASR | 47 testes · 4 transcrições reais |
| `ferramentas/reel_transcricao.py` | **só B** | cadeia Reel→transcript | 10 Reels, artefato commitado |
| `provas/reel_fala_qualidade.py` | **só B** | PASS/PARTIAL/FAIL por caso | corre, exit 0 |
| `coleta/story_local.py` | **só A** | rota de Story sem Apify | **NÃO** — teste bate em `127.0.0.1` com fixture |
| `coleta/instagram_stories.py` | **só A** | classe de Story | **NÃO** |
| `ferramentas/story_transcrever.py` | **só A** | 3.º reconhecedor | **NÃO** |
| `medidas/fato_local.py` · `lugar_do_fato.py` | **só A** | lugar do fato | — (B tem os mesmos nomes em `leis/`) |
| `ferramentas/apify_contrato.py` · `apify_recuperar.py` | **só A** | contrato de ator | **B apagou-os por medição** (`ebcdb230`) |

---

## O RISCO QUE UM MERGE CEGO DISPARA, E QUE EU CONSEGUI PROVAR

`_gavetas.py` põe todas as gavetas em `sys.path`. Medido agora:

```
posição em sys.path:  medidas = 10   ·   leis = 11
```

`medidas` vem **antes** de `leis`. E os dois módulos do lugar do fato existem **em gavetas
diferentes, com conteúdo diferente**, um em cada linhagem:

| | A · SCRAP | B · HEAD |
|---|---|---|
| `fato_local` | `medidas/` · `d8c02e9dcc33` | `leis/` · `08a705b30f63` |
| `lugar_do_fato` | `medidas/` · `3779cd42c885` | `leis/` · `f38200560aa8` |

```
NUM MERGE, medidas/fato_local.py PASSA A SOMBREAR leis/fato_local.py — SEM ERRO,
SEM AVISO, e com conteúdo diferente. `import fato_local` muda de implementação
e ninguém é notificado.
```

Confirmei que hoje isso **não** acontece, e porquê: `import fato_local` resolve para
`leis/fato_local.py` apenas porque `medidas/fato_local.py` **não existe** no HEAD.

**Raio de impacto medido, e é pequeno:** um único ficheiro importa esses módulos em cada
linhagem — `tests/test_lugar_do_fato.py`. Não é sistémico. **Mas é silencioso**, e um teste
que passa a testar outra implementação sem dizer é pior do que um que falha.

> **Esta é a prova concreta de por que «resolver com merge» estava proibido.** O conflito
> não aparece como conflito de Git: os caminhos são diferentes, então o Git junta os dois
> em paz e o `sys.path` decide em silêncio.

---

## AO · CONVERGÊNCIA PROPOSTA — NÃO EXECUTADA

Ações: **KEEP** (fica como está) · **PORT** (levar de A para B) · **REFINE** (fica, mas
muda) · **REPLACE** (morre, e outro assume) · **ARCHIVE** (sai; o git guarda).

### Linha 1 · O que já está resolvido e não se toca

| componente | ação | porquê |
|---|---|---|
| `social_persistencia` · `contrato_ator` · `apify_pool` | **KEEP** | `md5` idêntico nas duas linhagens. Zero trabalho. |
| `orquestrador/orquestrador.py` | **KEEP, FORA DE ESCOPO** | `COL-LAW-011`: um único dono da orquestração. Está **acima** do SCRAP e não é absorvível por ele. |
| `ferramentas/apify_contrato.py` · `apify_recuperar.py` | **ARCHIVE** | já arquivados por medição em `ebcdb230`: 0 importadores, 0 workflows, saídas inexistentes. O dono vivo do conceito é `contrato_ator.py`. **Não re-importar.** |

### Linha 2 · O ASR — um dono, e ele já existe

| componente | ação | porquê |
|---|---|---|
| `ferramentas/fala_local.py` | **KEEP como ASR OWNER único** | é o único com medição escrita, trava de alucinação, trava de silêncio conferida contra a biblioteca, e 47 testes |
| `ferramentas/story_transcrever.py` | **REPLACE** | repete três decisões que B já mediu e reverteu: `beam_size=5`, texto vazio a sair `OK`, idioma sempre detetado |
| `instagram_transcrever` · `youtube_transcrever` | **REFINE** | já chamam o dono, mas guardam 6 constantes duplicadas cada |

**O defeito arquitetural a fechar, e ele é maior do que o terceiro dono:** há **quatro**
constantes de modelo independentes.

| caminho | modelo por omissão |
|---|---|
| `fala_local.MODELO_PADRAO` | `small` |
| `instagram_transcrever` (`IG_MODELO`) | `small` |
| `youtube_transcrever` | `small` |
| `reel_transcricao.MODELO_PADRAO` | **`medium`** |

```
O MESMO REEL SAI EM `medium` OU EM `small` CONFORME A PORTA POR ONDE ENTRA.
E `small` é justamente o que escreve «MICE» onde se disse «mais».
```

Recomendação: o modelo passa a ser **decisão do pedido**, resolvida pelo ASR OWNER, e
nenhum adapter volta a ter constante própria. **Não implementar agora.**

### Linha 3 · A segurança

| componente | ação | porquê |
|---|---|---|
| `guarda/social_sessao.redigir()` | **PORT de A → B** | `GUARD GAP = PROVEN` · `LIVE PASSWORD LEAK = NOT_REPRODUCED`. A tem a regra `_CREDENCIAL_NA_URL`; B não. |

Medido: `redigir('postgresql://postgres:SenhaSecreta123@…')` devolve a senha **intacta** em
`social_sessao` **e** em `apify_pool`, no HEAD. Na rota viva que consegui reproduzir
(`coleta_checkpoint` → `psql` → `stderr`) a senha **não** apareceu.

> Não importado nesta missão, de propósito: importar código de A é convergir, e convergir
> não é desta missão. Entra como **PORT prioritário** na próxima.

### Linha 4 · O lugar do fato — resolver ANTES de qualquer merge

| componente | ação | porquê |
|---|---|---|
| `fato_local` · `lugar_do_fato` | **REFINE — decidir a gaveta primeiro** | duas gavetas, dois conteúdos, e `medidas` sombreia `leis` em silêncio |

**Pré-requisito de qualquer convergência:** escolher UMA gaveta e UM conteúdo, antes de as
duas árvores se tocarem. É a única linha desta matriz que bloqueia as outras.

### Linha 5 · Stories — capacidade real, cadeia sem fio

| componente | ação | porquê |
|---|---|---|
| `coleta/story_local.py` · `instagram_stories.py` | **KEEP em A, e LIGAR** | a medição de A é genuína e valiosa: no Story o texto de ecrã é pixel, logo o áudio deixa de ser exceção |
| a ligação | **REFINE** | não há entrada em `ADAPTADORES` para `('INSTAGRAM','FETCH_STORIES')`, e o teste bate em `127.0.0.1` com fixture |

```
STORIES_CAPABILITY_READY = PARTIAL, e o bloqueio NÃO é só «falta amostra viva»:
falta o adapter, falta o fio, e o teste nunca falou com o Instagram.
```

### Linha 6 · O roteador

| componente | ação | porquê |
|---|---|---|
| `coleta/social_rotas.py` | **KEEP como SCRAP ADAPTER ROUTER** | já é `(PLATAFORMA, CAPACIDADE) → adapter`, com portão de robots, de permissão e de sessão |
| `leis/social_matriz.py` | **REFINE** | declara `PROVED` para rotas que nunca correram e aponta provas para ficheiros inexistentes; **e não tem a rota `yt-dlp`** |
| `pedido/receitas.py` | **REFINE** | `fase=transcrever` existe só em B |

---

## AU · A FRONTEIRA, E DE QUE LADO CADA COISA FICA

`COL-LAW-011` decide isto e não é negociável: **um único dono da orquestração.**

```
COLLECTION_REQUEST                    ← COL-LAW-010: diz O QUE se quer, nunca COMO
        │
        ▼
ORQUESTRADOR CANÓNICO                 ← COL-LAW-011: o único cérebro
orquestrador/orquestrador.py            escolhe EXECUTOR a partir de capacidade declarada
        │
        ├── outros executores
        └── SINTONIA SCRAP EXECUTOR   ← um executor entre vários
                │
                ▼
        SCRAP ADAPTER ROUTER          ← coleta/social_rotas.py
        responde a UMA pergunta só:
        «dado que já escolheram SCRAP + capacidade, que adapter/provider executa?»
```

**O SCRAP nunca decide se o pedido devia existir.** Decide apenas como o cumpre.

### AT · O contrato do SCRAP como executor — `COL-LAW-013`, já canónico

| verbo | o que o SCRAP responde | onde já existe |
|---|---|---|
| `CAPABILITIES` | plataformas × capacidades × rotas | `leis/social_matriz.py` |
| `CHECK` | consigo chegar agora, sem gastar? | `contrato_ator.portao()` · `social_sessao.preflight()` |
| `COLLECT` | vai buscar | `social_rotas.executar()` |
| `STATE` | onde parei | **buraco** — `COL-LAW-016` exige e o cursor é interno |
| `OUTPUT` | onde larguei, e em que forma | `social_envelope` |
| `TRACE` | o que aconteceu, com hora e custo | `registro` de `social_rotas` |

**`COL-LAW-016` decide o checkpoint:** o orquestrador conhece `PONTUAL · INCREMENTAL ·
TOTAL`; o cursor do Instagram, o `since_id` do X e o page token do YouTube são **do
executor** e não sobem. O `STATE` é o buraco declarado.

**`COL-LAW-019` decide a rota paga.** Quando o SCRAP escalar para Apify, a corrida tem de
explicar `WHY_PAID_ROUTE` · `CHEAPER_ROUTE_ATTEMPTED` · `CHEAPER_ROUTE_RESULT` ·
`ESCALATION_REASON` · `COST_USD`. Hoje `social_rotas` regista `ROTA_ESCOLHIDA` e `COST_USD`,
mas **não** regista por que a rota barata não serviu.

---

## AR · TRANSCRIPTION_ONLY vs EVIDENCE_CAPTURE

São dois modos, e confundi-los foi o que quase transformou uma poupança de banda numa
política de preservação.

| | `TRANSCRIPTION_ONLY` | `EVIDENCE_CAPTURE` |
|---|---|---|
| cadeia | post → resolve → **faixa de áudio** → ASR | post → **vídeo original** → storage object → áudio derivado → transcript |
| objetivo | banda, tempo, disco | preservação, auditoria, reprocessamento |
| medido (1 Reel de 34 s) | **362.479 B** | 1.788.869 B |
| transcrição | **idêntica** (343 chars, string igual) | idêntica |
| 1.000 Reels | **910 MB** | 4.492 MB |
| o RAW original | **não existe** | existe, com SHA256 |
| dá para reprocessar com outro modelo? | **só o áudio** | **sim, do original** |
| serve de evidência do que foi publicado? | **não** | sim |

```
AUDIO-ONLY NÃO É «RAW MAIS PEQUENO». É OUTRA COISA.
O áudio é DERIVED. Descartar o vídeo é uma decisão de preservação, não de banda.
```

**Quando cada um basta:**

- `TRANSCRIPTION_ONLY` quando a pergunta é *«sobre o que esta conta fala?»* — varrimento,
  triagem, classificação. O transcript é o produto; o vídeo não é citado.
- `EVIDENCE_CAPTURE` quando o item vai **sustentar uma afirmação** — quando alguém vai
  dizer «o concorrente anunciou X no dia Y» e isso precisa de se conferir contra o segundo
  exato. Aí o original é a prova, e `SHA256` identifica os **bytes**, nunca a observação.

A `CAPABILITY-MATRIX` já escrevera «nunca baixar vídeo». **Está certa para o primeiro modo
e errada para o segundo** — e a diferença é a que `COL-LAW` inteira protege:
`RAW != DERIVED`.

### E o defeito de contrato que isto revela

Medido: **111 registos** com `RAW_EVIDENCE_PATH`, **11 existem**, **100 não**; **80**
declaram `PRESERVED`. A causa é política (`.gitignore:26`, decisão D-003), **não perda**.

```
PROVENANCE/STORAGE CONTRACT GAP — e não RAW DATA LOSS.
```

O registo tem `RAW_EVIDENCE_PATH` e `RAW_EVIDENCE_STATE`, e **nenhum campo que diga onde**.
`PRESERVED` aponta para um caminho que o repositório exclui de propósito. Quem lê não
distingue preservado-no-Storage de perdido.

**As quatro perguntas que o coordenador fez, respondidas até onde a medição alcança:**

| pergunta | resposta |
|---|---|
| que campo devia apontar para o storage object? | um `STORAGE_URI` verificável, separado de `RAW_EVIDENCE_PATH` |
| isso já existe na Collection? | **`leis/artefato.py` tem `STORAGE_LOCATION` + `SHA256`.** O `RUN-MANIFEST` não o usa. |
| quem é o dono do endereço? | a Collection, não o SCRAP — `raw_asset.storage_path` |
| o SCRAP fornece ou persiste? | **fornece.** Entrega bytes + `SHA256` + identidade da plataforma; quem endereça é a Collection |

**Não redesenhar a Collection nesta missão.** Fica registado como buraco de contrato.
