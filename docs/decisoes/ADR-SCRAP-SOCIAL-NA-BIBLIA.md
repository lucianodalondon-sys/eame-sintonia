# ADR — O SCRAP SOCIAL ENTRA NA ÁRVORE CANÔNICA

**Data:** 2026-09-08 · **Estado:** IMPLEMENTADO · **Piloto real:** NÃO EXECUTADO

---

## 1 · O QUE FOI MEDIDO

| | valor medido | informado |
|---|---|---|
| SCRAP HEAD | `417af227` | confere |
| **Bíblia HEAD** | **`fbeb796c`** | `e3ae1bcb` — **avançou 1 commit** |
| `merge-base` | `350a4fe7` | confere |
| commits SCRAP próprios | **9** | confere |
| **commits Bíblia próprios** | **89** | 88 |

`e3ae1bcb` é ancestral de `fbeb796c` — a Bíblia só andou para a frente, sem divergir.

**Nenhum arquivo do SCRAP existia na Bíblia.** Os 9 commits estavam inteiramente
ausentes, e `scripts/` **não existe mais** na árvore canônica. Um merge bruto teria
ressuscitado uma gaveta morta.

---

## 2 · O PORTE — GAVETA POR GAVETA

`_gavetas.py` é o shim canônico de import. Cada peça foi para a gaveta do que ela **é**:

| de | para | por quê |
|---|---|---|
| `scripts/falhas.py` | **`leis/falhas.py`** | vocabulário canônico é lei |
| `scripts/social_matriz.py` | **`leis/social_matriz.py`** | registro declarativo: capacidade **e** quota |
| `scripts/social_rotas.py` · `social_scrap.py` · `social_envelope.py` · `youtube_oficial.py` | **`coleta/`** | executores |
| `scripts/social_sessao.py` · `social_guarda.py` | **`guarda/`** | segredo e sessão |
| ponte `canonico()` | **`ferramentas/apify_pool.py`** | onde o pool vive |
| `sintonia-scrap.yml` | **`.github/workflows/scrap-social.yml`** | ver §3 |

Imports convertidos de `sys.path.insert(HERE)` para `import _gavetas`, nos módulos
**e** nos quatro testes.

### Uma colisão de nome, resolvida por renomear o meu

`sintonia-scrap.yml` **já existia na Bíblia**, e é **outro workflow**: o piloto
italiano com navegador, transcrição e pool da Apify. Mesmo nome, significado
diferente. O executor social virou **`scrap-social.yml`** — quem chegou depois muda
de nome.

### Uma lacuna do porte, achada por teste

O `.gitignore` da Bíblia não tinha as regras de perfil de navegador que o commit
`946107d` acrescentou. `test_gitignore_cobre_perfil_de_navegador` reprovou, e as
regras foram portadas. **Sem o teste, a segunda tranca do segredo teria ficado para trás.**

---

## 3 · O ACHADO BLOQUEADOR

`youtube_oficial.py` gravava `YOUTUBE-CHECKPOINT.json` em `data/samples/SOCIAL-IT/`,
e o workflow fazia `git add -A` naquela pasta depois de cada piloto. O estado que
decide o que a **próxima** execução vai buscar entrava no repositório e crescia a
cada corrida.

```
GIT NÃO É BANCO OPERACIONAL.
```

`docs/operacao/P-011-DADO-OPERACIONAL-NO-GIT.md` já tinha medido a lei: pode ficar no
Git schema, contrato, código e amostra justificada — **não** checkpoint, run state ou
ledger operacional. *"O Git não esquece. Um ficheiro apagado continua a pesar em cada
clone, para sempre."*

### O erro conceitual por trás

A missão anterior reusou `identidade_valida()` do checkpoint canônico e guardou o
estado num JSON ao lado. Isso é:

```
REUTILIZAR UMA FUNÇÃO DO CHECKPOINT CANÔNICO
NÃO É REUTILIZAR O CHECKPOINT CANÔNICO.
```

A lei foi emprestada; a **durabilidade** ficou noutro dono. Durabilidade tem um dono só.

### O conserto

`checkpoint_ler/gravar/atualizar` e `cache_de_playlists` **deixaram de existir**.
No lugar: `checkpoint_disponivel()`, que devolve `(estado, banco)` do dono canônico —
`coleta/coleta_checkpoint.py` sobre `checkpoint_coleta`. Sem DSN, devolve
**`CHECKPOINT_CANONICAL_NOT_LIVE` e `None`** — e **não abre** um segundo dono durável.

`cache_da_execucao()` sobrevive como cache **de RAM**, com o nome dizendo o que é.

**Nada foi apagado do histórico:** `YOUTUBE-CHECKPOINT.json` nunca chegou a ser
rastreado nesta árvore.

---

## 4 · CHECKPOINT CANÔNICO — O ESTADO HONESTO

| pergunta | resposta medida |
|---|---|
| `checkpoint_coleta` existe no schema versionado? | **SIM** — `supabase/migrations/016_checkpoint_e_unidade_analitica.sql` (e verificado em `008`) |
| Existe LIVE? | **NÃO SEI** |
| Por quê? | Nenhuma credencial de banco neste ambiente (`SUPABASE_DB_URL`, `DATABASE_URL`, `PGHOST` — todas ausentes). `psql` está instalado; o que falta é o DSN |

P-011 já declarava `LIVE_STATE = PARTIAL` e *"as linhas do banco esta sessão não as
viu"*. **Não posso provar que não está LIVE — só que não consigo ver.** E
`UNKNOWN nunca vira SIM`: sem prova, a retomada não é reivindicada.

**Nenhuma migration foi aplicada.** Não é missão desta.

---

## 5 · RAW E OS DOIS MODOS

| modo | RAW | metadata | checkpoint |
|---|---|---|---|
| **PILOT_SAMPLE** (hoje) | `data/samples/SOCIAL-IT/raw-free`, amostra pequena e classificada | ficheiros **nomeados** no Git | **nenhum no Git** |
| **OPERATIONAL_COLLECTION** (alvo, G-42) | Supabase Storage + `raw_asset` | `collection_run` | `checkpoint_coleta` |

O workflow deixou de usar `git add -A` numa pasta: agora adiciona **três ficheiros
nomeados**, e tem uma **trava de execução** que aborta a corrida se algo com
`CHECKPOINT` no nome aparecer no índice. `-A` leva o que alguém puser lá amanhã — e é
assim que checkpoint volta pelo lado.

---

## 6 · A TRAVA BLOQUEADORA

`TestGitNaoEBancoOperacional` reprova se qualquer módulo de `coleta/`, `leis/`,
`guarda/` ou `ferramentas/` **gravar ou ler** um ficheiro de checkpoint, e se o
workflow voltar a commitar a pasta inteira.

Ela procura o **ato** (`env.gravar(ARQUIVO_CHECKPOINT`, `git add -A data/samples` em
linha executável), nunca a palavra num comentário — a narrativa que explica o defeito
removido continua permitida, porque **apagar a memória do erro não é consertar o erro**.

Injetei as duas regressões de propósito: **as duas foram pegas**.

---

## 7 · VEREDITO

| # | condição | estado |
|---|---|---|
| 1 | código SCRAP na branch canônica | ✅ |
| 2 | quota com um dono (`leis/social_matriz`) | ✅ |
| 3 | secret wiring correto, sem vazamento | ✅ |
| 4 | nenhum checkpoint operacional no Git | ✅ |
| 5 | **checkpoint canônico com caminho real** | ❌ **`NÃO SEI` se está LIVE** |
| 6 | RAW do piloto com destino correto | ✅ (PILOT_SAMPLE declarado) |
| 7 | Apify não é fallback | ✅ |
| 8 | baseline sem regressão | ✅ `NEW_FAILURES = 0` |
| 9 | System Map parity | ✅ `TARGET/TESTED`, não `OBSERVED` |

```
PILOT_READY = NÃO
```

**Bloqueio único restante:** provar `checkpoint_coleta` LIVE — ou declarar o piloto
explicitamente **ONE-SHOT**, sem alegar retomada. As duas saídas existem; nenhuma é
desta missão.

---

## 8 · PRODUÇÃO DESTA MISSÃO

`YOUTUBE API CALLS = 0` · `SEARCH CALLS = 0` · `GENERAL UNITS = 0` ·
`APIFY CALLS = 0` · `SUPABASE WRITES = 0` · `STORAGE UPLOADS = 0` ·
`MIGRATIONS LIVE = 0`
