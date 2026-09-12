# C10.6B — O RUN SOBREVIVE AO PROCESSO

`C10_6B_DURABLE_RUN = PASS`

> A C10.6 provou que a cadeia de Reel aguenta um `os._exit()`. Ficou `PARTIAL`
> por um motivo só: o processo seguinte sabia ler a **gaveta**.
>
> ```
> UM FICHEIRO NO DISCO É UM RESULTADO. NÃO É UMA EXECUÇÃO.
> ```

---

## 1 · O QUE FALTAVA, E ONDE ELE ESTAVA

`RUN_STATE_PERSISTENCE = NOT_IMPLEMENTED`. O repositório já tinha os três donos;
a cadeia de Reel não tinha aresta para nenhum deles.

| conceito | dono | tabela | aresta do Reel **antes** |
|---|---|---|---|
| RUN | sem dono genérico em código (9 escritores) | `public.collection_run` | **NO** |
| CHECKPOINT | `coleta/coleta_checkpoint.py` | `public.checkpoint_coleta` | **NO** |
| STAGE TRACE | `medidas/rastro_da_coleta.py` | `public.etapa_da_corrida` | **NO** |
| TAXONOMIA DE FALHA | `leis/falhas.py` | — | YES (desde a C10.6) |

`coleta/scrap_executor.py` **declarava** `CHECKPOINT_BACKEND` e no mesmo
dicionário dizia `CURSORS = 'NOT_IMPLEMENTED'`.

    MODULE EXISTS != EDGE EXISTS != FLOW EXISTS.

---

## 2 · A RELAÇÃO ENTRE AS DUAS TABELAS NÃO ERA AMBÍGUA — ESTAVA ESCRITA

A migration 016 responde à FASE 3 com todas as letras:

> «Não é o mesmo grão que `collection_run`. Uma rodada é UMA execução do ator; o
> checkpoint é a UNIDADE DE TRABALHO, e ela pode atravessar várias execuções
> quando a chave roda. **Por isso `collection_run` aponta para cá, e não o
> contrário.**»

```
CHECKPOINT_TO_RUN_SEMANTICS    `checkpoint_coleta.run_id` — existe no schema e
                               NINGUÉM o escreve (medido no HEAD)
RUN_TO_CHECKPOINT_SEMANTICS    `collection_run.checkpoint_id` — «de qual unidade
                               de trabalho esta execução nasceu»
CAN_CHECKPOINT_HAVE_MULTIPLE_RUNS   YES
CANONICAL_DIRECTION_FOR_HISTORY     collection_run.checkpoint_id
SCHEMA_RELATION_AMBIGUITY           NO — o schema tem as duas colunas, o
                                    contrato declara uma direção, e o código
                                    só escreve essa
```

`checkpoint_coleta.run_id` fica **sem escritor, e de propósito**: escrevê-lo
diria que um checkpoint tem UMA run, que é o contrário do que a 016 declara.

---

## 3 · O FIT DO CONTRATO — NENHUMA COLUNA NOVA

`NEW_MIGRATION = NO`. Tudo o que a C10.6 disse ser preciso para retomar já tinha
representação honesta:

| NEED | OWNER / FIELD | FIT |
|---|---|---|
| RUN STATUS | `collection_run.status` (`rodando`·`concluida`·`vazia`·`parcial`·`falhou`) | **YES** |
| ATTEMPT | `etapa_da_corrida.tentativa` + `UNIQUE(run_id, etapa, tentativa)` | **YES** |
| LAST ERROR | `error_message_redacted` · `error_class` · `http_status` | **YES** |
| CANONICAL STATE | `etapa_da_corrida.canonical_state`, validado contra `falhas.ESTADOS` | **YES** |
| RETRYABLE | `leis/falhas.retentavel()` — derivado, não guardado | **YES** |
| LAST GOOD ARTIFACT | `etapa_da_corrida.last_good_artifact` | **YES** |
| RESUME POINT | as passagens + `checkpoint_coleta.ultima_unidade` | **YES** |
| CHECKPOINT STATE | `estado` · `unidades_feitas` · `itens_persistidos` | **YES** |
| PROCESS CRASH WITNESS | `estado='RUNNING'` **com `terminou_em` nulo** | **PARTIAL** |

A última linha é a única com ressalva, e ela merece o nome próprio da secção 8.

---

## 4 · O QUE FOI PRECISO CONSTRUIR (E NÃO FOI UM CHECKPOINT NOVO)

### `RUNNING` estava no vocabulário e nenhum escritor o sabia escrever

`registrar()` escrevia a passagem **depois** de ela acontecer. É a forma certa
para quem chega ao fim, e não serve para quem não chega.

    UM ESTADO QUE NENHUM ESCRITOR ESCREVE SÓ EXISTE NO PAPEL.

A etapa passa a escrever-se em dois tempos, na **mesma linha**: `abrir_etapa()`
antes do trabalho, `fechar_etapa()` depois. A chave `(run_id, etapa, tentativa)`
continua única — não nascem duas linhas, e a tentativa anterior nunca é
sobrescrita porque a tentativa **muda**.

### O relator é a junta entre quem sabe onde e quem sabe escrever

A cadeia de Reel sabe onde os seus degraus começam. O que ela não sabe, e não
pode saber sem virar outra coisa, é que existe um Postgres do outro lado. Então
ela **relata**, e quem escreve é o dono do rastro.

    INSTRUMENTAR NÃO PODE SER CONDIÇÃO PARA FUNCIONAR.

Sem relator, `_SEM_RELATO` responde `None` a tudo e a cadeia corre exactamente
como sempre correu — os 47 testes dela não precisam de saber que isto existe.

### A ordem durável, inteira

```
ABRE CHECKPOINT → ABRE RUN → LIGA → TRABALHO (que relata) →
PERSISTE → AVANÇA CHECKPOINT → FECHA RUN
```

`PERSIST FIRST, THEN ADVANCE CHECKPOINT` ganhou uma irmã: **abrir a etapa antes
do trabalho**. Sem ela, quem morre a meio não deixa linha.

---

## 5 · A MATRIZ DE CRASH

PostgreSQL 16.13 descartável, migrations 001–026 pela cadeia canônica da casa,
`008` como conferência. Cinco mortes reais: `os._exit(97)` — sem `finally`, sem
`atexit`, sem flush, sem fechar a ligação.

    UMA EXCEÇÃO NÃO É UMA MORTE. UMA EXCEÇÃO TEM `finally`.

| | morte | exit | checkpoint | RUN | passagens | pendurada |
|---|---|---|---|---|---|---|
| **F0** | antes da primeira etapa | 97 | EM_CURSO | rodando | 0 | não |
| **F1** | `FETCH` aberta | 97 | EM_CURSO | rodando | 1 | **sim** |
| **F2** | `RAW` fechada, `DERIVED` não começou | 97 | EM_CURSO | rodando | 2 | não |
| **F3** | dentro da derivação | 97 | EM_CURSO | rodando | 3 | **sim** |
| **F4** | `DERIVED` persistido, RUN aberta | 97 | EM_CURSO | rodando | 3 | não |
| **OK** | — | 0 | CONCLUIDO | concluida | 3 | não |

### O que o processo B vê, lendo só o banco

Outro PID, outra sessão de Postgres (`pg_backend_pid()` diferente), nenhuma
variável, nenhum ficheiro temporário do morto.

| | F0 | F1 | F2 | F3 | F4 |
|---|---|---|---|---|---|
| vê o checkpoint | YES | YES | YES | YES | YES |
| vê a RUN morta | YES | YES | YES | YES | YES |
| vê a última etapa | — | FETCH/RUNNING | RAW/PASS | DERIVED/RUNNING | DERIVED/PASS |
| vê a tentativa | — | 0 | 0 | 0 | 0 |
| vê o último artefato bom | — | — | `RAW:…` | `RAW:…` | `DERIVED:…` |
| decide onde retomar | FETCH | FETCH | DERIVED | DERIVED | nada a fazer |

---

## 6 · F4 — O CASO PERIGOSO, VISÍVEL NO BANCO

Antes da retomada, com o `.txt` **já no disco**:

```
DERIVED (etapa)                    = PASS
DERIVED_EXISTS_BEFORE_RESUME       = YES   (1.514 bytes em data/samples/REEL-TRANSCRICOES/)
OLD_RUN_COMPLETED_BEFORE_RESUME    = NO    (status = rodando, finished_at nulo)
CHECKPOINT_COMPLETED_BEFORE_RESUME = NO    (EM_CURSO, unidades_feitas = 0)
```

    DERIVED EXISTS != RUN COMPLETED — E AGORA ESTÁ NO BANCO, NÃO NA INTENÇÃO.

**F3** é o outro lado: morte dentro do ASR. `PARTIAL_TRANSCRIPT_PUBLISHED = NO`
— o `_fechar` nunca correu, não há artefato derivado, e a etapa fica `RUNNING`
sem `output_count`.

---

## 7 · A RETOMADA

Três retomadas, com armadilha na rede: `urlopen` e qualquer `subprocess` que
cheire a transporte levantam.

| | F2 | F3 | F4 |
|---|---|---|---|
| SAME_CHECKPOINT | YES | YES | YES |
| NEW_RUN | `RUN-F2-B` | `RUN-F3-B` | `RUN-F4-B` |
| OLD_RUN_PRESERVED | YES (`rodando`) | YES (`rodando`) | YES (`rodando`) |
| RAW_REUSED | `MEDIA_JA_PRESERVADA` | idem | idem |
| NEW_REMOTE_ACQUISITION | NO | NO | NO |
| AUDIO_ONLY_ACQUISITION | `REUSED_NOT_ACQUIRED` | idem | idem |
| FINAL_RUN_STATUS | `vazia` | `concluida` | `concluida` |
| CHECKPOINT_COMPLETED | CONCLUIDO | CONCLUIDO | CONCLUIDO |
| INSTAGRAM_REQUESTS | 0 | 0 | 0 |

`vazia` em F2 não é defeito: aquele reel não tem fala, e o reconhecedor
correu e disse-o. `ZERO_RESULTS` é um resultado.

---

## 8 · A RUN MORTA FICA `rodando`, E ISSO NÃO É UM DESCUIDO

`RUN-F4` continua `rodando` para sempre. A tentação é marcá-la `falhou` na
retomada. O comentário da própria tabela proíbe:

> «PROVENIÊNCIA É PROSPECTIVA: não se preenche elo de execução passada. Inventar
> o elo depois seria fabricar proveniência.»

    UMA EXECUÇÃO QUE MORREU NÃO ESCREVE O PRÓPRIO FIM.
    E NINGUÉM ESCREVE POR ELA.

E não é só uma questão de direito: é de **conhecimento**. `EM_CURSO` e `rodando`
não distinguem «alguém está a correr agora» de «alguém morreu a correr». Sem
`lease`, `heartbeat` ou `pid+host` — colunas que não existem — nenhum leitor
sabe qual dos dois é.

O abandono **fica legível** na evidência que existe: uma etapa `RUNNING` que
ninguém fechou, ao lado de uma execução posterior no mesmo checkpoint que
concluiu. É a leitura certa, e é feita por gente.

```
MISSING_SEMANTIC   «esta execução está viva?» — liveness de uma RUN
CURRENT_OWNER      public.collection_run (migration 001)
WHY_IT_DOES_NOT_FIT  `status = rodando` é o último estado que a própria
                     execução escreveu. Não há campo que diga QUANDO ela deu
                     o último sinal, e sobrecarregar `updated_at` do
                     checkpoint com semântica de lease seria dar-lhe um
                     segundo significado.
MINIMAL_CONTRACT_DELTA  um carimbo de vida na `collection_run`
MIGRATION_REQUIRED      YES — e por isso NÃO foi feita nesta missão
BIBLE_CHANGE_REQUIRED   NO
RISK                    baixo: o trabalho duplicado é CPU local, e a
                        contabilidade do checkpoint já está protegida (§9)
```

---

## 9 · CONCORRÊNCIA — UMA CORRIDA REAL, ENCONTRADA E FECHADA

Dois processos de verdade, mesmo checkpoint, Postgres de verdade. **Antes**, 20
rodadas em 20 avançaram o checkpoint duas vezes:

```
pode_gastar   é uma função `stable` — uma leitura pura
entre a leitura e a escrita não há nada
os dois liam «podes», os dois faziam, os dois somavam +1
```

    LER «PODES» NÃO É TER TOMADO.
    ENTRE A PERGUNTA E A ESCRITA CABE OUTRO PROCESSO INTEIRO.

A correção não é um lock novo nem uma coluna nova: a pergunta e a escrita passam
a viajar na **mesma instrução** — `where estado <> 'CONCLUIDO' returning …`, o
`compare-and-set` que a tabela já permitia.

| 30 rodadas, 2 processos cada | antes | depois |
|---|---|---|
| DUPLICATE_RUNS | 0 | 0 |
| DUPLICATE_STAGE | 0 | 0 |
| CHECKPOINT_ADVANCED_TWICE | **20/20** | **0** |
| LOST_UPDATE | — | 0 |
| DEADLOCK | 0 | 0 |
| SERIALIZATION_FAILURE | 0 | 0 |
| o perdedor SABE que perdeu | não | **sim** (`JA_CONCLUIDO_POR_OUTRA_CORRIDA`) |

`CAN_BOTH_CLAIM_WORK` continua **YES**, e está declarado na §8: os dois fazem o
trabalho, mas o checkpoint deixou de mentir sobre quantas unidades foram feitas.

---

## 10 · DOIS DEFEITOS QUE SÓ O POSTGRES REAL APANHOU

### `psql` fala, e a fala virava dado

Um `update … returning` que não casa com linha nenhuma imprime o **seu próprio
recibo** em stdout — `UPDATE 0` — e o leitor devolvia-o como se fosse uma linha
de resultado. O `compare-and-set` lia `[['UPDATE 0']]`, achava que tinha ganho, e
os **dois** processos concorrentes diziam «avancei».

    ZERO LINHAS NÃO É UMA LINHA QUE DIZ ZERO.

Conserto: `-q`. É a mesma família do defeito que `pode_gastar` já carrega escrito
no corpo — ler a conversa do cliente de banco como se fosse a resposta do banco.

### Campo final vazio some no recorte

`pode_gastar` já tinha o aviso no corpo. `registrar()` e `fechar_etapa()` tinham
o mesmo buraco com `diagnostic_code`, que é nulo em quase toda passagem. Passam
a usar o idioma da casa: `coalesce(…, '-')` e um marcador que nunca é vazio.

---

## 11 · MUTAÇÃO — E A PROVA QUE NÃO PROVAVA

```
MUTANTS = 12    SURVIVORS = 0
```

A primeira corrida deu **nove sobreviventes**. A prova de Postgres imprimia o
estado e passava.

    UMA PROVA QUE MOSTRA O NÚMERO E NÃO O EXIGE MEDE O ECRÃ.

Sete invariantes passaram a ser **afirmadas**, e duas mutações eram inválidas —
não mudavam comportamento nenhum:

| mutação | quem a matou |
|---|---|
| M1 checkpoint avança antes de persistir | I1 (postgres) |
| M2 reutilizar `RUN_ID` na retomada | `test_20` |
| M3 apagar a gravação da etapa FAIL | I3 (postgres) |
| M4 apagar o `diagnostic_code` | I2 (postgres) |
| M5 RUN concluída porque DERIVED existe | `test_17` |
| M6 não criar RUN nova na retomada | a retomada (postgres) |
| M7 sobrescrever a tentativa 0 | I4 (postgres) |
| M8 remover a ligação RUN → CHECKPOINT | `test_20` |
| M9 ignorar `leis/falhas.py` e retentar 403 | `test_18` |
| M10 introduzir state JSON local | `test_3` |
| M11 `NOT_RUN` aparece como `PASS` | `test_19` |
| M12 o avanço deixa de ser condicional | `test_15` |

**M6 e M8 eram mutantes inválidos na primeira versão** — um renomeava uma função
e chamava o nome novo, o outro cortava uma das duas escritas da mesma ligação.

    UMA MUTAÇÃO QUE NÃO MUDA O QUE O CÓDIGO FAZ NÃO PROVA NADA.

E **M2 sobreviveu por causa de um segundo driver**: `executar_etapas`, com zero
chamadores, duplicava a sequência inteira. A mutação trocou o bloco de abertura
**daquele** e a suíte não caiu. Foi retirado.

    UM OWNER COM DUAS CÓPIAS DA MESMA ORDEM JÁ É DOIS.

---

## 12 · RED TEAM

```
ATTACKS = 25    POSITIVE_FINDINGS = 0    RED_TEAM_RESULT = PASS
```

Um ataque deu positivo e não era a casa: contava as etapas que morreram a meio
como contabilidade em falta. Uma etapa `RUNNING` cujo processo morreu tem entrada
1 e destino nenhum — e isso é a contabilidade a **funcionar**.

    UMA ETAPA QUE MORREU A MEIO TEM ENTRADA SEM DESTINO.
    DIZÊ-LO É A CONTABILIDADE, NÃO O BURACO.

---

## 13 · RETRY — O DONO NÃO MUDOU

| sinal | estado canônico | retentável | tentativas |
|---|---|---|---|
| HTTP 403 | `AUTH_EXPIRED` / `BLOCKED` | não | 1 |
| HTTP 404 | `SOURCE_GONE` | não | 1 |
| HTTP 429 | `RATE_LIMITED` | sim | 4 |
| HTTP 500 | `SOURCE_UNAVAILABLE` | sim | 4 |
| timeout | `TRANSIENT_NETWORK_ERROR` | sim | 4 |
| policy NOT_ALLOWED | `ROUTE_NOT_ALLOWED` | — | **0 chamadas de rede** |
| desconhecido | `UNKNOWN_ERROR` | não | 1 |

O checkpoint **registra** a execução; ele não decide se repetir adianta.

---

## 14 · O QUE NÃO MUDOU

- `leis/social_matriz.py` intocado — `INSTAGRAM/FETCH_TRANSCRIPT = ROUTE_NOT_ALLOWED`;
- `NEW_MIGRATION = NO` · `LIVE_TOUCHED = NO` · nenhum deploy;
- Admission, Source Relevance, Intelligence e Portal intocados;
- `TRANSCRIPTION_LIVE_OWNER_COUNT = 1` · `ASR_OWNERS = 1` · `VIDEO_FALLBACK = NO`;
- nenhum `SOURCE_ID` ou `DOCUMENT_ID` fabricado.

### Dívidas declaradas

1. **Liveness de uma RUN** (§8) — a única coisa que exige migration.
2. **`COLLECTION_RUN = DONO_DUPLICADO`** — o mapa já o registava antes desta
   missão: nove ficheiros escrevem naquela tabela e não há dono genérico de
   «abrir uma execução». Esta missão acrescenta o **primeiro** escritor
   genérico, dentro do dono da durabilidade, e não resolve o resto.
3. **`coletar()` e `executar_unidade()`** — as duas estradas antigas do
   checkpoint têm a mesma corrida de leitura-e-escrita que a §9 fechou na
   estrada nova. Não foram tocadas: `executar_unidade` tem zero chamadores e
   `coletar` é a estrada paga, que esta missão não exercita.

---

## 15 · VEREDITO

```
C10_6B_DURABLE_RUN      = PASS
RUN_STATE_PERSISTENCE   = IMPLEMENTED
REEL_RUN_EDGE           = YES      (antes: NO)
REEL_CHECKPOINT_EDGE    = YES      (antes: NO)
REEL_STAGE_TRACE_EDGE   = YES      (antes: NO)
POSTGRES_VERSION        = 16.13    DISPOSABLE = YES    LIVE_TOUCHED = NO
MIGRATIONS_APPLIED      = 001–026 (008 como conferência)   NEW_MIGRATION = NO
CRASHES                 = 5 reais, exit 97
MUTANTS = 12            SURVIVORS = 0
ATTACKS = 25            RED_TEAM_RESULT = PASS
TESTS_BEFORE = 2321     TESTS_AFTER = 2341    NEW_FAILURES = 0
SYSTEM_MAP_CHECK        = PASS (7 passos + 1 validação, lidos do CADEIA-DO-MAPA)
NETWORK_REAL = 0  INSTAGRAM_REQUESTS = 0  APIFY_RUNS = 0  PAID_RUNS = 0  COST_USD = 0
```

**A C10.6 deixa de ter `RUN_STATE_PERSISTENCE = NOT_IMPLEMENTED` como bloqueio.**
