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

---

## O QUE ACONTECE SE A PORTA RECEBER `memoria=` — MEDIDO

Antes de decidir modelo, mediu-se a coisa mais barata de medir: **passar o
argumento que o orquestrador não passa.** Nenhuma linha de código foi alterada.

Contra o Postgres 16 descartável, com `guarda/portas_live.MemoriaSupabase`
apontada à URL descartável:

| | sem `memoria=` (produção hoje) | com `memoria=` |
|---|---|---|
| `RUN_STATE` | `PARTIAL` | `COMPLETE` |
| `PENDENCIA` | `UPLOAD_PENDING_METADATA` | `PRESERVED_AND_REGISTERED` |
| `FALTOU` | `banco_diz_concluida`, `campos_batem_apos_escrita`, `memoria_aplicada`, `reconciliacao_observada` | `[]` |
| reconciliação | não houve | `2 == 2 == 2`, o último de um `SELECT` |

E as sete perguntas do §48, feitas por um **processo novo** depois de o anterior
morrer:

```
UNIDADES_REENCONTRADAS: 2
DE_QUE_CORRIDA_VEIO   : run-p21-com-memoria
QUANDO_FOI_COLHIDO    : 2026-09-09T00:00:00Z
QUAL_O_SHA_CONFERIDO  : 45c0dc215ae06dedbbaf7d63  (DECLARADO, comparável)
ONDE_ESTAO_OS_BYTES   : IT/it-t2-001/OBSERVATION/45c0dc21…
JA_FOI_DERIVADO       : NÃO   (derived_artifact = 0)
JA_FOI_ESTRUTURADO    : NÃO   (conteudo = 0)
ESTA_PENDENTE         : SIM — há raw_asset sem derived_artifact
```

**Sete `NAO SEI` viraram sete respostas.** O que faltava não era arquitetura: era
um argumento.

### E não é preciso uma quarta `Memoria`

Mediu-se também se a porta de **produção** fala com um Postgres descartável:

```
classe             : MemoriaSupabase
modulo             : guarda.portas_live
e MemoriaDoDerivado: True
contar raw_asset   : 0
corrida escrita    : rodando
started_at lido    : 2026-09-09T00:00:00Z
```

`guarda/portas_live.MemoriaSupabase` **não tem nada de Supabase por dentro**: não
faz HTTP, não conhece a API, não lê bucket. É `psql` com uma URL, e a própria
docstring já o diz — «O Postgres de produção, falado por `psql`». O único traço
de Supabase é o *nome da classe* e o nome da variável de ambiente por omissão,
`SUPABASE_DB_URL`.

    A PORTA DE PRODUÇÃO JÁ É GENÉRICA.
    O QUE MUDA ENTRE PROVA E PRODUÇÃO É A URL, E MAIS NADA.

Isso resolve `TEST PATH = PRODUCTION PATH` sem construir nada — e sem SQLite,
que a missão proíbe introduzir por impulso e que aqui nem faria falta.

Fica registado o único desconforto honesto: **o nome mente um bocado.** Uma
classe chamada `MemoriaSupabase` que corre contra um banco local descartável não
descreve o que faz. É uma questão de nome, não de arquitetura, e não se resolve
sozinha.

---

## O QUE A TRAVESSIA EXIGE DA UNIDADE — E O SEU LIMITE

`derivar()` chama `deriv.correr()` com esta unidade, e só com esta:

```python
[{'RAW_ASSET_ID': unidade['RAW_ASSET_ID'], 'PDF': unidade['PDF']}]
```

Duas coisas ficam medidas, e as duas importam:

1. **`RAW_ASSET_ID`** é o id do banco. Confirma o censo pelo lado do chamador:
   sem a linha de `raw_asset`, `derivar()` não tem sequer o que passar. E
   `derivacao_forward.correr` escreve-o na própria docstring: «`run_id` tem de
   existir em `collection_run`. A `024` tem chave estrangeira e o banco recusa
   se não existir; **não se contorna**.»

2. **`PDF`** é um caminho para um documento. A travessia que existe é a do
   **documento** — o ficheiro chama-se `rota_forward_documento.py` e não esconde
   isso. Uma observação social em JSON não tem PDF para derivar.

    EXISTE UMA TRAVESSIA. ELA É A DO DOCUMENTO.
    DIZER «A TRAVESSIA» SEM DIZER «DO DOCUMENTO» SERIA PROMETER MAIS
    DO QUE ESTÁ ESCRITO.

A régua de derivação em si é injectável (`correr(..., derivar=None)` cai em
`ex.derivar_um`), portanto o dono não está preso a PDF por dentro. Mas a **forma
da unidade** que ele aceita hoje está, e é isso que limita o alcance de qualquer
travessia que se ligue nesta missão.

---

## A TRAVESSIA JÁ ATRAVESSA — CONTRA POSTGRES DE VERDADE

`provas/a_rota_m2_atravessa.py` foi **corrido**, não lido, contra o Postgres 16
descartável com as 23 migrations aplicadas por ela própria num banco virgem, e
com um PDF real da loja (`IT-T2-002`, boletim agrometeorológico da ARPAV):

```
A ROTA, NUMA CORRIDA SO
  DERIVED     PASS · {'PASSED': 1}
  STRUCTURED  OK
  ADMISSION   correu · a porta respondeu: NAO_SEI

ROTA_M2_ATRAVESSA=PASS          21 casos, 21 PASS
  raw_asset_id=1  ->  derived_artifact id=1  ->  conteudo  ->  decisao
  arestas observadas: [('DERIVED','STRUCTURED'), ('STRUCTURED','ADMISSION')]
```

**DERIVED → STRUCTURED → ADMISSION não é uma promessa: corre hoje, com o
artefato a viajar entre as etapas e as duas arestas com os dois topos no banco.**

E a mesma prova nomeia, sem eufemismo, o que falta:

```
A9  sem topo: [('RAW','DERIVED')] · RAW_FORWARD_NAO_EMITE e gap declarado do O9R
A13 nenhum READY nasceu em corrida nenhuma · ADMISSION PASS != READY PASS
    o que NAO prova: producao, nem READY. A rota termina em ADMISSION.
```

## OS TRÊS BURACOS, JÁ DECLARADOS PELA PRÓPRIA CASA

Não foi preciso descobri-los. `coleta/derivacao_forward.py:153` já os tinha
escrito num tuplo `GAPS`, legível por AST:

| Gap declarado | O que diz | O que a missão tem de fazer |
|---|---|---|
| `RAW_FORWARD_NAO_EMITE` | «`guarda/preservar_coleta.py` escreve `raw_asset` e não emite rastro. A etapa RAW existe, tem dono e corre — **e é muda**.» | fazer a etapa RAW falar: uma passagem no rastro, para a aresta `RAW → DERIVED` ganhar o topo de cima |
| `READY_NAO_TEM_DONO` | «READY TEM contrato (COL-LAW-043, 11 campos) · TEM dono (`admissao.pronto_para_inteligencia()`) · TEM **0 produtores em runtime** · TEM 0 consumidores» | READY tem produtor — é `orquestrador.pela_porta`. O defeito não é falta de dono: é que ele produz READY **a partir do item cru** |
| (não estava no tuplo) | `atravessar()` tem zero chamadores | ligar, não construir |

    OS TRÊS BURACOS ESTAVAM ESCRITOS NO REPOSITÓRIO.
    O QUE FALTAVA NÃO ERA DESCOBRI-LOS. ERA FECHÁ-LOS.

## AS TRÊS PORTAS QUE A TRAVESSIA PEDE — TODAS EXISTEM

`atravessar(banco, *, unidade, run_id, armazem, memoria, canal_id, universo)`
pede três portas, e nenhuma precisa de ser construída:

| Porta | Implementação | Onde vive | Interface |
|---|---|---|---|
| `armazem` | `ArmazemLocal` | `guarda/preservar_coleta.py` | `existe · enviar · ler` |
| `memoria` | `MemoriaSupabase` | `guarda/portas_live.py` | `aplicar · corrida · objeto_em · objetos_da_corrida · raw_por_id · derivado_com_identidade` |
| `banco` | `Banco(dsn)` | `coleta/coleta_checkpoint.py` | `executa(sql) -> linhas` |

As três falam `psql` ou disco. Nenhuma precisa de driver instalado, e a casa já
tem essa regra escrita: «instalar um pacote global só para um teste passar
continua proibido». `pdftotext 24.02.0` está presente, portanto a régua de
derivação é real e não um esqueleto.

## O ALCANCE HONESTO: T4 É A ROTA QUE FECHA

`pedido/receitas.py` declara quatro executores. Só um larga documentos:

| | executor | o que traz |
|---|---|---|
| T7 | `corpus-pesquisador` | obra publicada, JSON |
| **T4** | **`rotulos-oficiais`** | **«o rótulo oficial do produto, como PDF»** |
| T3 | `eppo` | ficha de praga, JSON |
| T9 | `comunicacao-publica` | post social, JSON |

A travessia que existe é a do documento e pede `{'RAW_ASSET_ID', 'PDF'}`. Logo,
**a rota que consegue fechar RAW → READY em produção é a T4**, e as outras três
param onde a régua de derivação delas não existe.

Isso não é uma desculpa para as saltar em silêncio. Uma unidade sem régua de
derivação tem de sair com nome — `NOT_RUN` e um motivo — e não desaparecer do
caminho como se nunca tivesse entrado:

    AUSÊNCIA DE RÉGUA NÃO É AUTORIZAÇÃO PARA PULAR ETAPA.
    É EXATAMENTE A MESMA LEI QUE A MISSÃO ESCREVEU SOBRE A AUSÊNCIA DE BANCO.

---

## A ÁGUA PASSOU PELO CANO — E O CANO TEM UM FURO QUE SÓ SE VÊ MOLHADO

Correu-se o caminho de produção a sério, sem rede e sem custo:

```
py orquestrador/orquestrador.py "colete rotulos" --so-a-porta

CORRIDA SUCCESS · XX-T4-2026-09-09-151703
  executor coleta/rotulos_baixar.py @ b8321b07
  colheita encontrada: 163 item(ns)
  pela porta de admissao: NAO_SEI 163
```

E o recibo que ficou escrito:

```json
"INGRESSO": {"PRESERVADOS": 163, "RECUSADOS": 0,
             "RUN_STATE": "PARTIAL",
             "BANCO": "NAO MEDIDO — nao houve leitura do banco"},
"ADMISSAO": {"itens": 163, "por_resultado": {"NAO_SEI": 163}, "prontos": 0},
"ITEM_COUNT_RAW": 163, "ITEM_COUNT_NORMALIZED": 0,
"ESTADO_DOS_ITENS": "NA_PORTA"
```

Três coisas ficam medidas de uma vez, e a terceira não se via de nenhuma outra
maneira.

**Primeira.** `DERIVED` e `STRUCTURED` não aparecem no recibo porque **não
correram**. A corrida vai de RAW a ADMISSION num salto, como o código já dizia.

**Segunda.** `RUN_STATE: PARTIAL` e `BANCO: NAO MEDIDO` — a corrida é honesta
sobre o que não fez. Não finge ter registado.

**Terceira, e esta é nova.** Ficheiros que aterraram no disco: **um**.

```
XX/nao-sei/OBSERVATION/c71063d1972a3844-…-_MANIFESTO.json
```

O recibo diz `PRESERVADOS: 163`. O disco tem **um objecto**. Mediu-se o porquê,
ficha a ficha:

```
ITENS DA COLHEITA          : 163
com _de                    : 163
valores de _de distintos   : 1
FICHAS                     : 163
STORAGE_LOCATION distintos : 1     <- data/raw/IT-ROTULOS/_MANIFESTO.json
SHA256 distintos           : 1
bytes de cada ficha        : [63040]
```

A causa está em duas linhas que se leem, cada uma, muito bem sozinhas.
`orquestrador.a_colheita` carimba a **procedência** de cada item:

```python
x.setdefault("_de", f.relative_to(RAIZ).as_posix())   # orquestrador.py:97
```

E `ingresso.ficha` lê esse mesmo campo como **identidade**:

```python
caminho = item.get("STORAGE_LOCATION") or item.get("_de") or ""   # ingresso.py:…
if abs_ and os.path.isfile(abs_):
    return art.raw_do_disco(abs_, raiz, **comum)
```

    UM CAMPO DIZ «DE QUE FICHEIRO EU VIM».
    O OUTRO LADO LÊ «EU SOU ESSE FICHEIRO».

O resultado é que o RAW preservado do rótulo do produto `GOLTIX`, registo
`002732`, é **o manifesto inteiro dos 163 rótulos** — e o mesmo para os outros
162. A etapa RAW corre, devolve `SUCCESS`, e preserva o contentor no lugar do
conteúdo.

E `PRESERVADOS: 163` conta **fichas aceites**, não objectos preservados. É a lei
da casa a ser quebrada pela própria casa:

    DECLARED != OBSERVED.

Isto não aparece em teste nenhum, porque nenhum teste alimenta a porta com um
ficheiro que contém muitos itens — que é exatamente o formato em que quatro dos
quatro executores desta casa largam o que colhem. **Só apareceu porque a água
passou pelo cano.**

### E o furo não é do T4. É de todos.

Mediu-se a mesma coisa para os quatro executores que a casa declara, cada um com
o que está realmente largado nesta árvore:

| alvo | executor | itens | objectos distintos | veredito |
|---|---|---:|---:|---|
| T3 | `eppo` | 0 | — | nada largado nesta árvore |
| T4 | `rotulos-oficiais` | 163 | **1** | colapsa 163 → 1 |
| T7 | `corpus-pesquisador` | 12 | **1** | colapsa 12 → 1 |
| T9 | `comunicacao-publica` | 78 | **4** | colapsa 78 → 4 |

**253 itens. 6 objectos.** E os seis não são itens: são os ficheiros-contentor em
que os itens vieram — um por ficheiro lido.

    HOJE, NENHUM ITEM DESTA CASA TEM RAW PRÓPRIO.
    TODOS TÊM, COMO RAW, A CAIXA EM QUE CHEGARAM.

A porta que a C-PLUMB-1 construiu está certa no que decidiu fazer — recusa com
nome, não julga, não inventa `FACT_TIME`. O que ela não previu foi a forma em que
esta casa entrega: **um ficheiro com muitos itens lá dentro**, que é a forma de
quatro em quatro executores. E é por isso que P24 não pode começar por ligar
`RAW → DERIVED`: ligar a seta agora derivaria 253 vezes o mesmo contentor.

    PRIMEIRO O RAW TEM DE SER DA UNIDADE.
    UMA SETA CERTA A PARTIR DE UM RAW ERRADO CONTINUA A LEVAR AO SÍTIO ERRADO.
