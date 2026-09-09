# TRAVESSIA OPERACIONAL DA COLETA — o que foi MEDIDO antes de mexer

> Missão C-PLUMB-2. Este ficheiro é a **medição**, e só ela. Nada aqui foi
> decidido por leitura de documentação: cada linha tem ficheiro, número de
> linha ou saída de comando por trás.
>
>     PRIMEIRO A ÁGUA PASSA PELO CANO. DEPOIS O MAPA DESENHA O CANO.
>
> E antes de qualquer um dos dois: **medir por onde a água já corre hoje.**

---

## P21 · POR QUE RAW → DERIVED → STRUCTURED PRECISA DE POSTGRES HOJE

A pergunta foi feita com uma exigência: não responder «porque o código usa
banco». Essa resposta não separa nada. Há duas perguntas diferentes escondidas
numa só, e a missão obriga a separá-las:

    CURRENT IMPLEMENTATION NEEDS POSTGRES   o código de hoje usa
    THE CONTRACT REQUIRES POSTGRES          a lei exige

Medido contra **PostgreSQL 16.13**, com **23 migrations** aplicadas num banco
virgem e descartável (`008` fora, como toda a casa já faz — é a migration de
verificação, não de esquema). 88 tabelas em `public`.

### O que o esquema real diz

```
collection_run(run_id)  ←—  raw_asset(run_id)
        FOREIGN KEY (run_id) REFERENCES collection_run(run_id) ON DELETE RESTRICT

raw_asset(id, sha256)   ←—  derived_artifact(raw_asset_id, parent_sha256)
        CONSTRAINT o_pai_por_id_e_o_pai_por_sha_sao_o_mesmo
        FOREIGN KEY (raw_asset_id, parent_sha256) REFERENCES raw_asset(id, sha256)
        ON DELETE RESTRICT              -- e raw_asset_id é NOT NULL

raw_asset(id)           ←—  conteudo(raw_asset_id)
        FOREIGN KEY (raw_asset_id) REFERENCES raw_asset(id) ON DELETE SET NULL
```

E a identidade:

```
raw_asset.id   default  nextval('raw_asset_id_seq'::regclass)
```

Isso é o centro da resposta. **A unidade só existe como unidade dentro do
Postgres**, porque o número que a nomeia nasce de uma sequência do Postgres. Os
bytes existem no disco; a *unidade* não.

### O censo, etapa a etapa

| Etapa | Precisa de Postgres | Por quê, exatamente | O contrato exige? |
|---|---|---|---|
| **RAW** (bytes) | **NÃO** | `guarda.ArmazemLocal` escreve no disco e confere o sha. Nenhuma query decide nada. | NÃO |
| **RAW** (linha) | **SIM** | `IDENTITY` — `raw_asset.id` vem de `nextval`. `STORAGE` da procedência. `DEDUPE` por `raw_asset_storage_path_key UNIQUE (storage_path)`. | **SIM** |
| **DERIVED** | **SIM** | `IDENTITY` + `CONSTRAINT`: `derived_artifact.raw_asset_id` é `NOT NULL` e aponta para um id que só o banco cunha. A FK composta `(raw_asset_id, parent_sha256)` é uma **lei escrita como trava**: o pai por id e o pai por sha têm de ser o mesmo pai. | **SIM** |
| **DERIVED** (idempotência) | **SIM** | `derivacao_e_unica_por_regua UNIQUE NULLS NOT DISTINCT (parent_sha256, kind, producer, producer_version, parameters_hash, serie_posicao)`. É trava real, não verificação em Python. | **SIM** |
| **STRUCTURED** | **SIM** | `DEDUPE` por `conteudo_canal_id_content_id_key UNIQUE (canal_id, content_id)` — `coleta/social_persistencia.py` escreve `on conflict (canal_id, content_id)`. `RUN_ID`, `DATASET_ID` e `CAPTURED_AT` ficam **fora** da chave de propósito: se entrassem, a mesma obra viraria N conteúdos, um por corrida. | **SIM** |
| **STRUCTURED** (recusa) | não | `persistir_video(..., raw_durou=False)` devolve `RAW_NAO_DUROU` sem tocar no banco. A recusa é **semântica**, em Python: RAW VEM ANTES DE CONTEUDO. | NÃO |
| **ADMISSION** | **NÃO** | `admissao/admissao.py` — **0 ocorrências** de `banco` em 455 linhas. `decidir()`, `escrever()`, `pronto_para_inteligencia()` recebem e devolvem dicionários. | NÃO |
| **READY** | **NÃO** | O que aterra é um ficheiro JSON escrito por `orquestrador.pela_porta`. Nenhuma query. | NÃO |
| **RASTRO** (telemetria) | **SIM** | `etapa_da_corrida`, com `UNIQUE (run_id, etapa, tentativa)`. É o que faz a contagem de tentativas ser verdade e não opinião. | **SIM** |
| **RETOMADA** | **SIM** | `_tentativa()` em `coleta/rota_forward_documento.py`: `select coalesce(max(tentativa), -1) from public.etapa_da_corrida where run_id = %s and etapa = %s`. Sem isto, uma repetição não sabe que é repetição. | **SIM** |

### A resposta em uma frase

> **RAW → DERIVED → STRUCTURED precisa de Postgres hoje não porque a derivação
> precise de uma query, mas porque a IDENTIDADE da unidade e a IDEMPOTÊNCIA de
> cada etapa são travas reais do esquema — e `derived_artifact.raw_asset_id` é
> `NOT NULL`. Sem a linha de `raw_asset`, DERIVED é impossível de escrever.
> ADMISSION e READY não precisam de banco nenhum, e medir isso é o que impede
> de arrastar o banco para onde ele não faz falta.**

---

## §48 · O RAW LOCAL É UM CHECKPOINT DURÁVEL?

Medido com dois processos separados de verdade — o primeiro morre com
`os._exit(0)` logo depois de RAW, o segundo nasce e só vê o que ficou escrito.

**Processo 1** (`memoria=None`, `ArmazemLocal`, sem banco):

```
ACEITES  : 2
RECUSAS  : []
RUN_STATE: PARTIAL
PENDENCIA: UPLOAD_PENDING_METADATA
FALTOU   : banco_diz_concluida, campos_batem_apos_escrita,
           memoria_aplicada, reconciliacao_observada
```

**O que ficou no disco**, e mais nada:

```
LOJA/IT/it-t2-001/OBSERVATION/45c0dc21…-45c0dc21…-45c0dc215ae0….json
LOJA/IT/it-t2-002/OBSERVATION/832c8eb0…-832c8eb0…-832c8eb021e7….json
```

Ficheiros que não são bytes de observação: **0**. Fichas do contrato no disco:
**0**. O conteúdo guardado é o **item original do coletor** — não a ficha
`leis/artefato.Artefato`. A ficha existiu em memória, no recibo, e morreu com o
processo.

**Processo 2**, nascido depois, perguntando o que está pendente:

```
BYTES_ENCONTRADOS   : 2
DE_QUE_CORRIDA_VEIO : NAO SEI  (o endereço tem ['IT','it-t2-001','OBSERVATION'])
QUANDO_FOI_COLHIDO  : NAO SEI  (mtime do ficheiro != COLLECTED_AT declarado)
QUAL_O_SHA_CONFERIDO: posso RECALCULAR, mas não há sha DECLARADO para comparar
JA_FOI_DERIVADO     : NAO SEI
JA_FOI_ESTRUTURADO  : NAO SEI
JA_FOI_ADMITIDO     : NAO SEI
ESTA_PENDENTE       : NAO SEI
```

### Veredito

    O RAW LOCAL NÃO É CHECKPOINT DURÁVEL.
    OS BYTES SOBREVIVEM. A UNIDADE NÃO.

E o mais importante: **o código já sabe disso e já o diz**. `PENDENCIA =
UPLOAD_PENDING_METADATA` é exatamente o nome deste estado — byte durável,
unidade por registar. Não foi preciso inventar vocabulário para o descrever; foi
preciso reparar que ninguém estava a ler o que ele já dizia.

O SQL que ligaria tudo é **gerado e deitado fora**:

```sql
insert into public.collection_run (run_id, platform, actor, …) values (…)
  on conflict (run_id) do nothing;
insert into public.raw_asset (run_id, storage_path, media_type, bytes,
                              sha256, captured_at, source_url) values (…)
  on conflict (storage_path) do nothing;
```

`guarda/preservar_coleta.py` produz este SQL em todas as corridas. Com
`memoria=None`, ninguém o aplica.

---

## P23 · QUEM É O DONO DA TRAVESSIA — MEDIDO ANTES DE CRIAR

O checkpoint P23 existe para uma razão: **não criar um dono que já existe.**

```
coleta/rota_forward_documento.py:287
    def atravessar(banco, *, unidade, run_id, armazem, memoria, canal_id,
                   universo=UNIVERSO_PADRAO)
        """A rota inteira, NUMA execucao: DERIVED → STRUCTURED → ADMISSION."""
```

Ela está **completa** e é honesta: se a derivação não entrega, para em DERIVED e
diz `PORQUE_PAROU`; se STRUCTURED não passa, ADMISSION sai `NOT_RUN` e não
`FAIL`, porque `NOT_RUN != ERROR`.

**Chamadores em produção: ZERO. Chamadores em qualquer sítio: ZERO.**

Nem a prova que existe para a atravessar lhe chama, e diz porquê
(`provas/a_rota_m2_atravessa.py:359`):

> «AQUI NAO SE CHAMA `atravessar()`, E A RAZAO E BOA. […] Esta prova ja derivou
> acima, de proposito, para poder conferir o `derived_artifact` campo a campo
> antes de o texto seguir. Chamar `atravessar()` agora derivaria uma SEGUNDA vez
> na mesma corrida.»

E o executor de PDF já tinha declarado o buraco em voz alta
(`coleta/executor_texto_de_pdf.py:415`):

> «Enquanto ninguém atravessar STRUCTURED e ADMISSION, este caminho termina em
> DERIVED. E terminar em DERIVED é a verdade.»

**Conclusão de P23: não se cria dono de travessia. Existe um, está escrito, está
correto e não tem chamador. O trabalho é ligação, não construção.**

---

## O CAMINHO DE PRODUÇÃO, COMO ELE É HOJE

`orquestrador/orquestrador.py`, linhas 311–316:

```python
if itens and (so_a_porta or not seco):
    recibo["INGRESSO"] = pela_entrada(itens, recibo)      # 311  RAW
if itens and (so_a_porta or not seco):
    r = pela_porta(itens, p.alvo, recibo["RUN_ID"])       # 313  ADMISSION
```

E em `pela_porta` (linha 138):

```python
decisoes = [adm.decidir(x, universo, corrida=run_id) for x in itens]
```

O argumento é **`itens`** — os dicionários crus que o coletor largou. Não são as
unidades que passaram por RAW. Ou seja:

    HOJE A PRODUÇÃO FAZ:   RAW  ─────────────────────────────►  ADMISSION
    E O CANO DIZ:          RAW → DERIVED → STRUCTURED → ADMISSION → READY

**DERIVED e STRUCTURED não correm em produção. São saltados.** E a admissão
julga o item cru, não o preservado: a etapa RAW acontece ao lado do caminho, não
dentro dele. É o mesmo defeito que a C-PLUMB-1 fechou uma etapa antes, um degrau
acima.

Além disso, `pela_entrada` (linha 117) chama:

```python
r = ing.receber(itens, corrida=recibo, armazem=armazem, raiz=str(RAIZ))
```

sem `memoria=`. O parâmetro fica no valor por omissão, `None`. A própria função
já tinha escrito a costura à espera de alguém:

> «Quando houver banco, ele entra por `memoria=` sem esta funcao mudar.»

---

## O DEFEITO DE FORMA QUE SE REPETE, UM ANDAR ACIMA

A C-PLUMB-1 encontrou isto sobre o armazém:

> «A PORTA DO ARMAZEM TINHA DUAS IMPLEMENTACOES: uma DE MENTIRA, para provar, e
> a da Supabase, que e producao remota. Nao havia nenhuma que corresse aqui —
> e essa e uma das razoes por que nenhum ficheiro de producao chamava
> `preservar()`.»
>
>     UM DONO QUE SO SABE ESCREVER LONGE
>     E UM DONO QUE NINGUEM CHAMA DE PERTO.

A medição desta missão encontra **exatamente a mesma forma** na porta seguinte,
a `Memoria`:

| Implementação de `Memoria` | Onde vive | O que é |
|---|---|---|
| `MemoriaDescartavel` | `guarda/memoria_descartavel.py` | **SQLite.** Declara-se: «NÃO É Postgres. E não finge ser.» Peça de prova. |
| `MemoriaPostgres` | `provas/preservar_coleta_no_postgres.py` | Postgres a sério — mas **recusa-se a arrancar** contra qualquer coisa que não seja um banco descartável local. Vive na gaveta das provas. Só testes a importam. |
| `MemoriaSupabase` | `guarda/portas_live.py` | Produção remota. Precisa de rede e credencial. |

    TRÊS MEMÓRIAS, E NENHUMA QUE UMA CORRIDA LOCAL DE PRODUÇÃO POSSA USAR
    CONTRA UM POSTGRES REAL.

É por isso que a linha de `raw_asset` nunca é escrita fora de uma prova. Não é
descuido do orquestrador: é que não havia por onde.

---

## O QUE ISTO DECIDE, E O QUE NÃO DECIDE

Decide a entrada de P22: o buraco medido **não** é «falta um orquestrador» nem
«falta um dono de travessia». É, por esta ordem:

1. a linha de `raw_asset` não é escrita em produção — logo a unidade não existe;
2. sem essa linha, `atravessar()` não pode sequer ser chamada;
3. `pela_porta` contorna as duas etapas do meio e julga o item cru.

Não decide qual dos dois modelos — A (síncrono) ou B (RAW durável, depois
processador) — fecha isto. Essa é a decisão de P22, e ela vem a seguir, com
estas medições em cima da mesa e não sem elas.
