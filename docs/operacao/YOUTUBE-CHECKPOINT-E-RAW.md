# YOUTUBE — CHECKPOINT CANÔNICO E RAW QUE NÃO SOME

**2026-09-08** · Fecho de engenharia antes do primeiro piloto.
**Produção desta missão:** 0 chamadas YouTube · 0 quota · 0 Apify · 0 escrita no
Supabase de produção · 0 upload · 0 migration aplicada em produção.

---

## 1 · OS TRÊS BLOQUEADORES, MEDIDOS E FECHADOS

### 1.1 · `CHECKPOINT EXISTS ≠ CHECKPOINT USED`

O piloto obtinha o `Banco` e **o jogava fora** (`_banco`), passava
`conhecidos = []` e no fim gravava `linha['CHECKPOINT_ID'] = _identidade(cid)`.

> **UM HASH NÃO É UMA LINHA DE CHECKPOINT.**

`_identidade()` é cálculo puro — não toca banco nenhum. Chamar aquilo de
checkpoint observado era confundir *existir* com *ser usado*.

**Fechado:** nasceu `coleta_checkpoint.executar_unidade()` — **dentro do dono**,
sobre a **mesma tabela**, com as **mesmas travas**, e sem o pool de chaves.

### 1.2 · O workflow não injetava `SUPABASE_DB_URL`

**Fechado:** injetado, com **o mesmo nome de secret** que `supabase-conexao.yml`
já usa. Nome novo seria um segundo cofre para a mesma chave, e dois cofres divergem.

### 1.3 · `RAW_REFERENCE` apontava para arquivo que morre com o runner

> **RAW_REFERENCE PARA ARQUIVO QUE SOME NÃO É PROVENIÊNCIA.**

**Fechado:** a referência passou a carregar `SHA256` inteiro, `BYTES`,
`PRESERVATION` e `NOT_PRESERVED_REASON`. Enquanto o dono forward do G-42 não
tiver recebido o byte, o artefato **diz** `NOT_PRESERVED` — e com o hash a prova
pode ser reconciliada depois.

---

## 2 · POR QUE A OPERAÇÃO NASCEU NO DONO, E NÃO NO YOUTUBE

`coleta_checkpoint.coletar()` passa por `ap.executar_com_pool` — é a **estrada
paga**, que roda chave a chave e classifica falha de token. Uma API oficial não
tem pool: tem uma chave e uma quota.

> **REUTILIZAR O DONO NÃO É REUTILIZAR UMA FUNÇÃO QUE TEM OUTRA SEMÂNTICA.**

Então `executar_unidade()` nasceu **ao lado** de `coletar()`, no mesmo arquivo.
Nada em `youtube_oficial.py` escreve checkpoint.

### A ordem é a lei

```
PERSIST FIRST, THEN ADVANCE CHECKPOINT.
```

`unidades_feitas` e `itens_persistidos` só sobem **depois** que `persistir()`
devolveu — e o número que entra é o que ele devolveu, **o que foi salvo**, nunca o
que voltou da API. Há teste que lê a **ordem no código** e reprova se ela inverter.

---

## 3 · A UNIDADE DE TRABALHO

> **A UNIDADE NÃO É O CANAL. É O CANAL NUMA JANELA DE OBSERVAÇÃO.**

`checkpoint_coleta` é `UNIQUE (collection_target, input_hash)`, e um checkpoint
`CONCLUIDO` recusa gasto novo. Se a unidade fosse só o canal, um canal vigiado
hoje ficaria **trancado para sempre**.

Por isso a **janela** entra na entrada, e portanto no `input_hash`:

```
{PLATFORM, CHANNEL_ID, CAPABILITY, JANELA}
```

`RUN_ID` e `CAPTURED_AT` continuam **fora** — retomar por outra execução tem de
reencontrar a mesma linha. É a lei que `identidade_valida()` já impunha.

---

## 4 · O QUE SIGNIFICA "CONHECIDO"

> **«VI NA API» NÃO TORNA UM VÍDEO CONHECIDO.**

`conteudo_persistido()` lê `public.conteudo`, cuja `UNIQUE (canal_id, content_id)`
já era a identidade canônica. Uma linha existe **se e somente se** foi salva. Se o
processo morrer entre ver e salvar, o id **não** aparece — e a próxima execução o
reencontra.

**Um defeito real, achado medindo o schema aplicado e não decorando:** minha
consulta usava `k.platform`, e a coluna chama-se **`plataforma`**. O nome errado
daria **zero conhecidos em silêncio**, e a coleta refaria tudo todo dia sem
ninguém perceber. Há teste que trava a coluna.

---

## 5 · PROVA EM POSTGRES DESCARTÁVEL

21 das 22 migrations aplicadas num Postgres 16 descartável (a `008` é verificação
pós-aplicação). **11 casos, todos verdes:**

| caso | prova |
|---|---|
| A | unidade concluída → **0 chamadas à API** |
| B | checkpoint aberto → chamada permitida |
| C | visto e não persistido → `itens_persistidos = 0` |
| D | persistido → contador sobe, estado `CONCLUIDO` |
| E | **crash antes de persistir** → `feitas=0`, estado `PARCIAL`, e a próxima tentativa **refaz** |
| F | reencontro idempotente — uma linha, não duas |
| G | mesma unidade não gasta duas vezes |
| H | **janela nova abre checkpoint novo** — monitoramento não trava |
| I | `RUN_ID` não muda a identidade |
| J | `KNOWN` vem do persistido; e a coluna existe |

### Pré-voo reproduzido por conta própria

A medição externa do coordenador disse SIM/0/SIM/SIM. **Reproduzi no descartável:**

```
checkpoint_coleta existe              SIM
pode_gastar(text,text) existe         SIM
collection_run.checkpoint_id existe   SIM
conteudo existe                       SIM
CHECKPOINT_ROWS_BEFORE                0
```

E contra um banco **vazio** o pré-voo devolve `NÃO` nos quatro — ele recusa, não
assume.

---

## 6 · OS DOIS MODOS, E A DIFERENÇA É O ASSUNTO

| | `youtube-piloto` (OPERATIONAL) | `youtube-piloto-oneshot` (ONE_SHOT) |
|---|---|---|
| checkpoint | usa o canônico | **não usa, não escreve** |
| alega retomada | sim | **não** |
| exige `SUPABASE_DB_URL` | **sim** | não |
| prova | API, quota, comentários, custo, rota **e incremental** | API, quota, comentários, custo, rota |
| **não** prova | — | **retomada operacional** |

> Um ONE-SHOT rotulado OPERATIONAL seria a mentira mais cara desta casa: alguém
> confiaria numa memória que não existe. Há teste que reprova se os dois rótulos
> colapsarem.

---

## 7 · VEREDITO

| # | condição | estado |
|---|---|---|
| 1 | `checkpoint_coleta` LIVE | **SIM** (externo) · reproduzido em descartável |
| 2 | Banco **usado**, não só obtido | ✅ `executar_unidade` |
| 3 | `KNOWN` = persistido | ✅ `conteudo_persistido` |
| 4 | unidade não trava monitoramento | ✅ janela no `input_hash` |
| 5 | workflow injeta o DSN canônico | ✅ |
| 6 | `RAW_REFERENCE` não fica pendurado | ✅ declarado `NOT_PRESERVED` + `SHA256` |
| 7 | Apify não é fallback | ✅ |
| 8 | baseline sem regressão | ✅ `NEW_FAILURES = 0` |
| 9 | segredo não vaza | ✅ pré-voo só devolve booleano |

```
PILOT_READY = SIM  — para ser disparado no RUNNER.
PILOTO EXECUTADO NESTA SESSÃO = NÃO.
```

**Nesta sessão não há chave da API nem DSN**, então nada foi coletado e nenhum
número de coleta é reportado. O piloto é **um dispatch**:

- **`scrap-social.yml` → fase `youtube-piloto`** (operacional; exige os dois secrets)
- ou **`youtube-piloto-oneshot`** (só a chave; não alega retomada)

---

## 8 · SYSTEM MAP

```
CHECKPOINT   LIVE_SCHEMA = OBSERVED (externo + descartável)
             USAGE       = NOT_OBSERVED
RAW          FORWARD_OWNER = G-42 · estado do byte = NOT_PRESERVED, declarado
YOUTUBE      SEARCH/GENERAL buckets = DECLARED · uso = NOT_OBSERVED
```

`USAGE` só sobe para `OBSERVED` depois de um piloto **operacional** que
realmente escreva uma linha. **CAN DO ≠ DID DO.**
