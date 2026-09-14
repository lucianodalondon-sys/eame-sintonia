# CENSO DA INFRAESTRUTURA — apêndice F da Bíblia

**Data:** 2026-09-08 · **HEAD medido:** `73e7270` · **Ramo:** `claude/biblia-canonica-da-coleta`

> **Medido, não presumido.** Este censo foi levantado **antes** de qualquer lei desta emenda
> ser escrita, e cada número pode ser conferido rodando o comando ao lado. Duas das
> conclusões contrariam o que a missão esperava encontrar — e estão registradas assim.

---

# A · CENSO DO GITHUB

## Workflows — 11, e **nenhum agendado**

```bash
grep -rn "cron:" .github/workflows/     # devolve VAZIO
```

| workflow | dono | gatilho | runner | papel |
|---|---|---|---|---|
| `system-map.yml` | `C-CI-MAPA` | dispatch · **push** · PR | ubuntu | portão: regera o mapa, valida, corre as provas |
| `supabase-migrate.yml` | `C-CI-PERSIST` | dispatch | ubuntu | aplica a cadeia canônica de migrations |
| `supabase-conexao.yml` | `C-CI-PERSIST` | dispatch | ubuntu | **só lê** — nunca escreve, nunca imprime segredo |
| `supabase-storage.yml` | `C-CI-PERSIST` | dispatch | ubuntu | cria o bucket privado `raw` e para |
| `supabase-raw-roundtrip.yml` | `C-CI-PERSIST` | dispatch | ubuntu | prova RAW: Git → Storage → Postgres → download → hash |
| `supabase-fichas-adama.yml` | `C-CI-PERSIST` | dispatch | ubuntu | fichas MAPA → Storage → `raw_asset` |
| `calendario-regressoes.yml` | `C-CI-REGRESSAO` | dispatch | ubuntu | regressões do calendário |
| `apify-conexao.yml` | `C-CI-COLETA` | dispatch | **self-hosted Windows** | conexão da rota paga |
| `apify-sensores.yml` | `C-CI-COLETA` | dispatch | condicional | sensores |
| `comunicacao-publica.yml` | `C-CI-COLETA` | dispatch | **self-hosted Windows** | coleta de comunicação pública |
| `sintonia-scrap.yml` | `C-CI-COLETA` | dispatch | condicional | o despachador |

**ACHADO 1 — o GitHub Actions não agenda nada.** Os 11 workflows são `workflow_dispatch`;
`system-map.yml` também corre em `push` e `pull_request`. **Zero `cron`.**

O único agendamento real do SINTONIA **não está no GitHub**: é o Agendador de Tarefas do
Windows, na máquina do Luciano (`SINTONIA-Italy-ForwardOnly`, de hora em hora). E o motivo
está medido e escrito em `docs/operacao/ITALY-FORWARD-ONLY-SCHEDULING-V1.md` §3: o runner do
GitHub **sai por datacenter dos EUA/Europa, não pela VPN italiana**, e toda a coleta provada
depende do IP italiano.

> Mover a coleta para a nuvem por conveniência invalidaria a única coisa que torna a medição
> confiável.

## Segredos — 4, nenhum no repositório

```
secrets.APIFY_TOKEN_POOL · secrets.SUPABASE_URL
secrets.SUPABASE_SECRET_KEY · secrets.SUPABASE_DB_URL
```

Vivem **só** como segredo do GitHub Actions. `tests/test_migrations.py:144` já proíbe
`SUPABASE_URL`, `SUPABASE_KEY`, `postgresql://` e `psycopg` dentro das migrations, e
`system-map.yml` §6 varre o que vai ser publicado atrás de padrão de credencial.

## O que está versionado em Git

| o quê | onde | veredito |
|---|---|---|
| a Bíblia, contratos, leis, réguas | raiz · `leis/` · `regras/` · `medidas/` | **CANONICAL** |
| código (1.151 ficheiros rastreados) | as 15 gavetas | **CANONICAL** |
| schema e 21 migrations | `supabase/migrations/` | **CANONICAL** |
| provas e mutações SQL | `supabase/tests/` | **CANONICAL** |
| SQL de importação gerado | `supabase/importacoes/` | **CANONICAL** — auditável antes de rodar |
| o mapa gerado | `system-map/data/*.generated.json` | **CANONICAL** (saída derivada) |
| amostras e evidência de rota não replicável | `data/samples/` | **CANONICAL** (D-003 + REGRA §14) |
| **o recibo e as observações da Itália** | `data/collection-ledger/italy/*.ndjson` | ⚠️ ver ACHADO 3 |
| **os bytes brutos da Itália** | `data/collection-store/italy/**` — 11 ficheiros, **12 MB** | ⚠️ ver ACHADO 3 |

---

# B · CENSO DO SUPABASE

## Schema — 21 migrations versionadas, e a ordem tem um dono só

```
001 fundacao_geografia_e_proveniencia   →  collection_run · raw_asset
002 identidade_pessoa_org_canal              …
015 cicatrizes_do_brasil                →  as constraints do lugar do fato
016 checkpoint_e_unidade_analitica      →  checkpoint_coleta
020 fonte_externa_e_estado_de_rota      →  fonte_externa
021 fato_externo_publicado
```

A ordem **não** vive no workflow: vive em `motor/cadeia_canonica.sh`, e o CI lê de lá —
*«duas listas de passos em dois arquivos divergem»*.
A `008` é a **última**, não a oitava: ela confere o que as outras escreveram.

## Storage — existe, e a lei dos bytes já está implementada

Bucket **`raw`**, privado, **um para o EAME inteiro** — não um por país.

> **O país vive no PATH do objeto** (`ES/<route>/<run_id>/<asset>`), **e o path é ENDEREÇO,
> nunca identidade**: a identidade continua sendo `run_id` + `sha256` + metadata na tabela
> `raw_asset`.

`supabase-raw-roundtrip.yml` prova a volta inteira: Git → Storage → Postgres → download →
hash confere.

## Quem escreve — e a resposta contraria o que se esperava

**ACHADO 2 — quase ninguém escreve direto no Supabase. O padrão da casa é outro:**

```
artefato JSON  →  gerador  →  ficheiro .sql VERSIONADO em supabase/importacoes/
                                        →  GitHub Actions (que tem o segredo)  →  Supabase
```

E o motivo está escrito nos próprios ficheiros, em `pacote/lastmile_para_supabase.py`:

> *«As credenciais do Supabase existem **só** como segredo do GitHub Actions. Esta sessão não
> as tem, e não deve tê-las. Então o trabalho é: produzir o ficheiro, versionar, e deixar o
> runner aplicar.»*
> **O QUE VAI PARA O GIT É REPRODUZÍVEL. O QUE FOI DIGITADO NO BANCO, NÃO.**

E em `guarda/catalogo_importar.py`:

> *«Por que gera SQL em vez de falar direto com o banco: o SQL é AUDITÁVEL. Ele entra no Git,
> alguém lê antes de rodar. Um importador que só existe como processo não deixa rastro do que
> fez.»*

### Os caminhos de escrita, medidos

| # | produtor | escreve o quê | como chega ao Supabase | classificação |
|---|---|---|---|---|
| 1 | `guarda/catalogo_importar.py` | catálogo ADAMA ES (7 tabelas) | gera `.sql` idempotente com `ON CONFLICT` sobre chave **natural** | **CANONICAL** |
| 2 | `guarda/importar_italia.py` | substância, aprovação UE, registro IT, resistência | gera `.sql`, **não executa nada** | **CANONICAL** |
| 3 | `coleta/regulatorio_importar.py` | `registro_regulatorio` + `collection_run` ES | gera `.sql` com gerador, chave natural e prova | **CANONICAL** |
| 4 | `pacote/lastmile_para_supabase.py` | boletim, clima, estatística, evento, fonte externa | gera `.sql` versionado | **CANONICAL** |
| 5 | `coleta/ropf_pre_requisito.py` | pré-requisito do catálogo | gera **ENSAIO**, em banco descartável por contrato — e diz isso | **CANONICAL** (declaradamente não é importação) |
| 6 | `coleta/coleta_checkpoint.py` | `checkpoint_coleta` | **fala direto com o banco** via `psql`, com DSN dado pelo chamador | **CANONICAL** — é o dono declarado do estado |
| 7 | `guarda/catalogo_importar.py --aplicar` | o mesmo `.sql` do #1 | **executa**, exige `SUPABASE_DB_URL` | **CANONICAL** — mesmo ficheiro auditável |

**Quem apenas LÊ** (`psql -tAc`, consulta): `guarda/es/adama_es_gate.py` (*«Ele NÃO importa
nada. Nenhuma linha vai para o banco canônico»*) · `leis/calendario_handoff.py` ·
`guarda/sql_conferir.py` · `medidas/portoes_eame.py` · `medidas/cicatrizes_brasil.py` ·
`provas/inventario_esperado.py`.

### Bypasses **para dentro** do Supabase: **ZERO**

```
caminhos de escrita medidos      7
canônicos                        7
bypasses                         0
```

Nenhum produtor escreve numa tabela canônica por conhecer o nome dela. O segredo não existe
fora do runner, e isso — por acidente feliz de engenharia — já implementa a lei que esta
emenda queria escrever.

---

# C · ACHADO 3 — O BYPASS EXISTE, MAS É NO SENTIDO CONTRÁRIO

> **A Itália não fura o Supabase. Ela passa por fora dele, para dentro do Git.**

`coleta/italy_recurrent_collect.mjs:144` faz:

```javascript
git(["add", "data/collection-ledger", "data/collection-store"]);
```

| o que a Itália grava | onde | o que o Supabase já tem para isso |
|---|---|---|
| recibo de corrida (6 corridas) | `data/collection-ledger/italy/runs.ndjson` | tabela **`collection_run`** (migration 001) |
| observação por documento (144) | `data/collection-ledger/italy/observations.ndjson` | tabela **`raw_asset`** (migration 001) |
| **os bytes** — 11 PDFs e HTMLs, **12 MB** | `data/collection-store/italy/**` | bucket **`raw`** + `raw_asset`, com round-trip provado |

**Nenhum ficheiro `.mjs` italiano menciona `raw_asset`, `collection_run` ou Supabase.**

Isto é a mesma fratura da **C-002** (dois formatos de corrida), vista pelo lado da
infraestrutura: **duas memórias operacionais para a mesma pergunta**. A espanhola é o banco;
a italiana é o Git.

### Por que isso importa, com número

| | |
|---|---|
| ficheiros de bytes no Git hoje | **11** · **12 MB** |
| commits que tocaram o ledger | 1 (o piloto ainda não corre em cadência) |
| custo por corrida da ARPAV | **~12,8 MB** para as 32 zonas |
| cadência declarada da ARPAV | 2× por semana na temporada |

Em dia sem publicação o resultado é `SEEN_AGAIN` e **zero bytes** são guardados — o piloto já
faz isso certo. Mas quando publica, entra tudo no Git. **E history do Git não se apaga:**
um ficheiro removido continua a pesar em cada clone, para sempre.

**Status:** `ISSUE` medido, registrado, **não corrigido nesta missão**.

---

# D · O QUE NÃO EXISTE — e por isso não foi inventado

| | medido |
|---|---|
| ambientes `DEV` / `PREVIEW` / `PRODUCTION` | **não declarados**. Um projeto Supabase só |
| GitHub Releases | nenhuma |
| GitHub Actions próprias (`.github/actions/`) | vazio |
| `cron` em qualquer workflow | **zero** |
| Reference Sets (portfolio, produto, cultura como base de referência viva) | **não existem** — há o *catálogo* ADAMA ES importado, que é o parente mais próximo |
| tabela de `reference_set` / `refresh policy` | **não existe** |
| ligação `RUN → GIT_COMMIT` no `RUN-MANIFEST` | **não existe** (o ledger italiano tem `GIT_HEAD`; o manifesto europeu não) |

---

## RESUMO EM SEIS LINHAS

1. **GitHub já é a autoridade de engenharia**, e isso não foi decidido: foi medido.
2. **GitHub já é o portão do Supabase**, porque o segredo só existe lá dentro.
3. **Bypass para o Supabase: zero.** A missão esperava encontrar; não há.
4. **O bypass real é ao contrário:** a Itália escreve recibo, metadata e **bytes** no Git,
   ignorando `collection_run`, `raw_asset` e o bucket `raw` que já existem e já foram
   provados.
5. **O GitHub Actions não agenda nada** — o único relógio do SINTONIA é o Windows do Luciano,
   e por um motivo bom (o IP tem de ser italiano).
6. **Reference Plane não existe** em lado nenhum. É `TARGET` inteiro.
