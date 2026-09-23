# MISSÃO — ABRIR A PORTA: CANDIDATAS → SOURCE CURATOR CONTÍNUO

**Base:** `source-curator-supervisor-v1` @ `8bbea01c` · local == remoto · worktree limpa
**Bancada:** worktree própria. **NÃO** trabalhar em `main`, nem na bancada do supervisor.

```text
HARD GATE   BIG_COLLECTION_ALLOWED = NO   ·   SALA_WRITES = 0
            Nenhuma promoção a READY fora do gate canónico.
```

---

## 0 · O QUE A COORDENAÇÃO MEDIU — confirme, não confie

Medido em `8bbea01c` antes de abrir esta bancada. **Reconfirme cada linha.
Se divergir, o seu número manda e diga-o pelo nome.**

```text
SUPERVISOR_PROCESS_REAL   PID 86172 vivo no SO (Get-CimInstance), não só no JSON
SOURCE_CURATOR_SERVICE    IDLE — vivo, fila sem trabalho elegível
QUEUE_DEPTH               38   (0 elegíveis · 1 BLOCKED de teste · 37 DONE)
CANDIDATES_TOTAL          241  (todas EM_ANALISE, todas IT, 0 URLs repetidas)
READY_FOR_COLLECTION      18   ← READY_LEGACY, régua antiga
```

### 0.1 · ⚠️ O BRIEFING DIZ QUE A PONTE NÃO EXISTE. ELA EXISTE — E ESTÁ A MEIO.

O briefing manda construir um `CANDIDATE_FEEDER` novo. **Não construa antes de ler isto.**
A cadeia já está montada e tem dono em cada troço:

```text
FONTES-CANDIDATAS.json  241
        │
        ▼  caracterizador.py          ← CORRE. parou a meio: 124 de 241
SOURCE-CHARACTERIZATION-V1.json  124   (ONBOARDING_READY: 98 YES · 26 NO)
        │
        ▼  emparelhar_com_atlas.py    ← FILTRA por ONBOARDING_READY == "YES"
CANDIDATE-TO-SOURCE-MATCH-V1.json  98
        │
        ▼  atribuir_source_id.py      ← CORRE. 84 com número · 13 sem território
SOURCE-ID-ALLOCATION-V1.json  NOVAS 84
        │
        ▼  alimentar_fila.py          ← lê ALLOCATION.NOVAS, não lê as candidatas
LIFECYCLE-QUEUE-V1.json
        │
        ▼  supervisor.py → worker.py → lifecycle
```

**O buraco não é onde o briefing supõe.** `alimentar_fila.py` não lê
`FONTES-CANDIDATAS.json` **por desenho** — quem lhe dá trabalho é a
`ALLOCATION`, e essa está alimentada.

```text
A PORTA NÃO ESTÁ FECHADA. A FILA A MONTANTE É QUE SECOU.
```

### 0.2 · ONDE ESTÁ REALMENTE O TRABALHO PARADO

```text
241 candidatas
 ├─  77  já têm contrato       — JÁ PROCESSADAS. Não são trabalho novo.
 ├─   7  têm SOURCE_ID e não têm contrato  ← ELEGÍVEIS JÁ, HOJE, sem código novo
 ├─  13  caracterizadas, sem território    — `NÃO SEI` deliberado
 ├─  27  caracterizadas, NO/pendentes
 └─ 117  NUNCA caracterizadas              ← O VERDADEIRO GARGALO
           ├─  75 SOCIAL (LinkedIn 44 · Instagram 25 · Facebook 6)
           └─  42 HTML   (Organização 19 · Base oficial 12 · Imprensa 9 · Ciência 2)
```

**Dizer «241 paradas» é falso.** O número honesto de trabalho novo é
**42 HTML + 7 prontas = 49** pelo caminho provado.

### 0.3 · ⚠️ AS 75 SOCIAIS NÃO SÃO O MESMO PROBLEMA

LinkedIn, Instagram e Facebook têm autenticação, política e robots próprios.
Tratá-las como HTML é contornar política, e isso o HARD STOP proíbe.

**Fora do escopo desta missão.** Classificar e registar como dívida, com o nome.

### 0.4 · O WORKER NÃO É LLM

Medido em `curadoria/worker.py`: zero `anthropic`, zero `api_key`, não sai para
a rede. Código determinístico. **`DEFAULT_SOURCE_CURATOR_MODEL` não se aplica**
ao supervisor/worker — correr custa 0 tokens.

LLM só entra se **você provar** que uma etapa precisa de semântica (§4).

---

## 1 · ENTRADA OBRIGATÓRIA

```bash
BIBLIA-CANONICA-DA-COLETA.md        # a lei
AGENTS.md                           # lei do System Map — aplica-se a si
regras/LEIA-ANTES-DE-COLETAR.md     # réguas vivas
```

---

## 2 · O TRABALHO

### PASSO 1 — CONFIRMAR A CADEIA (read-only, sem rede)

Reconfirme §0.1 e §0.2 correndo os módulos em modo de leitura.
Diga, pelo nome, se a cadeia que medi é a cadeia real.

**Entregue a tabela dos 5 baldes e PARE para a coordenação ver.**

⚠️ Se concluir que um `CANDIDATE_FEEDER` novo **é mesmo** necessário, diga
**porquê** contra a cadeia existente. Duplicar o que existe cria segunda verdade.

### PASSO 2 — AS 7 QUE JÁ PODEM ENTRAR HOJE

Têm `SOURCE_ID` e não têm contrato — `BUILD_CONTRACT` sabe fazê-las:

```text
IT-T5-041 CRPV · IT-T9-015 Conserve Italia · IT-T7-038 Valpolicella
IT-T5-051 UNIRC · IT-T9-019 SCAM · IT-T9-020 Sipcam · IT-T5-054 Legacoop
```

Enfileire, deixe o supervisor trabalhar, meça o desfecho de cada uma.
**Isto prova a cadeia inteira sem escrever código novo.**

### PASSO 3 — DESTRAVAR A CARACTERIZAÇÃO DAS 42 HTML

Só depois do PASSO 2 verde.

Descubra **porque** o caracterizador parou nas 124. Uma destas é verdade:
orçamento, falha, corte deliberado ou nunca ter sido corrido sobre elas.
**Meça — não suponha.**

Retome pelas **42 HTML**, em lotes, com rede moderada:

- **controlo positivo primeiro**: se o leitor falha, nenhuma fonte é condenada;
- `NÃO SEI` é resultado válido e obrigatório quando é o caso;
- 403 é resposta da fonte, não convite a contornar. Registe e siga;
- sem scraping agressivo. Cadência canónica.

### PASSO 4 — LLM SÓ COM PROVA DE NECESSIDADE

**Determinístico primeiro, sempre.** Não gaste modelo onde código chega.

Se e só se uma etapa exigir semântica que o código não resolve, crie o estado
explícito `NEEDS_LLM` e diga **qual** decisão precisa de juízo.

```text
DEFAULT_LLM_WORKER_MODEL = SONNET
Opus só por escalonamento reproduzível, com ESCALATION_REASON escrito.
Sonnet NÃO decide READY. O gate decide.
```

Se nenhuma etapa precisar de LLM nesta missão, **diga isso** e entregue
`SONNET_USED = 0`. Zero honesto é melhor que gasto decorativo.

### PASSO 5 — IDEMPOTÊNCIA, PROVADA A ATACAR

Medi: 0 URLs repetidas dentro das 241, mas **77 já existem como contrato**.
O risco de duplicar identidade é real.

Prove com ataque, não com afirmação:

1. mesma candidata duas vezes → uma tarefa ativa;
2. candidata cuja URL já é contrato → **não** cria identidade nova;
3. URL inválida → falha fechada;
4. mesma organização, canal diferente → pode ser unidade distinta, quando
   semanticamente correto;
5. worker morto a meio → tarefa durável, retomada;
6. fila vazia → `IDLE`, não morte;
7. supervisor reiniciado → recupera.

Persista `CANDIDATE_ID → TASK_ID → SOURCE_ID`.

⚠️ `emparelhar_com_atlas.py` já carrega um controlo positivo medido
(`@AgroNotizie` ↔ `@agronotizietv`, a mesma fonte com endereços diferentes).
**Não o enfraqueça.** Um `==` literal entre URLs devolveu «0 de 98 já existem» —
um zero redondo e falso que teria duplicado `IT-T8-001`.

### PASSO 6 — INTEGRAR O GATE DE DETALHE

`aquisicao-detalhe-v1` @ `f98f234c` (**remeça**) provou:

```text
RECALL_CANARIO   6/126 → 101/126
controlo negativo  APOL 1 · ARPAE 1
gate CAPA != MATERIA provado por mutação (neutralizado ⇒ teste reprova)
```

Nenhuma fonte nova promovida a READY sem este gate. **Sem merge cego** —
integrar semanticamente, no owner certo.

```text
LISTAGEM_DE_NOTICIAS  READY exige INDEX_URL real → DETAIL_LINKS → ITEM → BODY útil
                      homepage 200 NÃO basta
BOLETIM_SERIADO       MAX_TARGETS = 1 continua correto
```

### PASSO 7 — SEPARAR OS DOIS READY

```text
READY_LEGACY  = 18   régua antiga. NÃO apagar, NÃO misturar.
READY_CURRENT = as que passarem pelo gate de detalhe
```

### PASSO 8 — GATILHO DE FILA BAIXA

Defina `CANDIDATE_LOW_WATERMARK` e emita `DISCOVERY_NEEDED` ao cruzá-lo.

**Não construa o motor de Discovery nesta missão.** Deixe o gatilho pronto e o
estado explícito — fingir serviço infinito é pior que dizer que falta.

### PASSO 9 — PAINEL QUE NÃO MENTE

Medido, e é o achado que originou tudo: o `STATUS-LIVE.json` dizia
`RUNNING`/`WORKER_ALIVE: true` com `WORKER_PID: 97820` — **PID inexistente**.

```text
FICHEIRO DIZ RUNNING != PROCESSO EXISTE.
```

O painel pergunta ao SO. Nunca herda verde de um ficheiro velho. Distinga
`STOPPED_FINISHED` de `STOPPED_BROKEN` de `IDLE`.

Já existe `C:\Users\<utilizador>\orca-tools\operacao_live.py` (da coordenação, fora
do repo) que mede assim. **Reutilize a ideia**; se o painel viver no repo,
declare-o no System Map.

---

## 3 · BLOCO DE ENTREGA

```text
INITIAL_HEAD =            FINAL_HEAD =            REMOTE_HEAD =
WORKTREE_CLEAN =

CADEIA_CONFIRMADA =              (a cadeia de §0.1 é a real? SIM/NÃO + onde diverge)
FEEDER_NOVO_NECESSARIO = SIM/NÃO + porquê contra o existente

CANDIDATES_TOTAL = 241
  JA_COM_CONTRATO =        COM_SOURCE_ID_SEM_CONTRATO =
  CARACTERIZADAS_NAO_READY =   SEM_TERRITORIO =
  NUNCA_CARACTERIZADAS =       destas SOCIAL =        HTML =

PASSO2_ENFILEIRADAS =    PROCESSADAS =    OK =    RETRY =    BLOCKED =
PASSO3_CARACTERIZADAS_NOVAS =    NAO_SEI =    403/POLICY =

DETERMINISTIC_RESOLVED =   NEEDS_LLM =   SONNET_USED =   OPUS_ESCALATIONS =
LLM_JUSTIFICADO =          (porque foi preciso, ou 0 e porquê não)

DEDUP_PROVEN =             (pelos 7 ataques, por nome)
CONTROLO_POSITIVO_ATLAS_INTACTO =
DETAIL_GATE_INTEGRATED =
READY_LEGACY =    READY_CURRENT =
READY_PROMOTED_WITHOUT_CURRENT_GATE = 0

SUPERVISOR_RUNNING_REAL =      (PID medido no SO, não no JSON)
CONTINUOUS_LOOP_PROVEN =       (matar worker → recupera; fila vazia → IDLE)
CANDIDATE_LOW_WATERMARK =      DISCOVERY_NEEDED_EMITIDO =

BIG_COLLECTION_RUNS = 0        SALA_WRITES = 0
NEW_FAILURES =                 (por NOME, contra baseline da mesma árvore)
SYSTEM_MAP_CHECK =             KNOW_HOW_DELTA =         PAID_USD =
```

---

## 4 · COMO FECHAR

**HARD STOP** no limite. Não continuar para Big Collection, Sala, Intelligence
ou Portal. Achado não bloqueante vira **dívida registada**, não missão nova.

Gate que falha: **reporte**. Não conserte em silêncio para obter PASS.
Um PASS comprado é pior que um FAIL honesto — o FAIL a coordenação lê.

### 4.1 · O RELATÓRIO TEM DUAS PARTES, NESTA ORDEM

1. **RELATÓRIO MEDIDO** — estado, evidência, problema, próxima ação, com commits e gates.
2. **EM LINGUAGEM SIMPLES** — secção final **obrigatória**, sem jargão. O dono do
   projeto não é engenheiro: a parte técnica é a prova, a parte simples é o que
   ele lê para decidir. Termo técnico inevitável vem traduzido na mesma frase.
   `NÃO SEI` diz-se assim: «isto ainda não foi medido, portanto não sei».

Responda lá, em palavras simples:

1. porque é que as candidatas estavam paradas — e quantas estavam **mesmo**?
2. a porta já existia ou foi preciso abri-la?
3. quantas o canário processou, e no que deram?
4. alguma precisou de inteligência artificial? porquê?
5. as fontes novas chegaram mesmo à matéria, ou pararam na capa?
6. o Bot continua sozinho depois do fim do turno?
7. o que acontece quando as candidatas acabarem?
8. as redes sociais ficaram de fora — porquê, e o que falta para entrarem?
