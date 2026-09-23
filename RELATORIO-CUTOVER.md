# RELATÓRIO — COLLECTION: CUTOVER CONTROLADO PARA PRODUÇÃO V1

```
ACTUAL_LLM_MODEL         claude-opus-5
DATA                     2026-09-21 21:40 → 2026-09-22 02:30 (hora do Brasil)
ARVORE CANONICA          cutover-prod-v1 @ b41fa080  (partiu de 1593633f)
PRODUCAO                 C:\eame-sintonia-ops · ops/cutover-prod-v1 @ e7c72357
BIG_COLLECTION           NAO CORRIDA
```

---

## VEREDITO

```
CUTOVER_PROVEN = PARCIAL
```

**Não digo `YES`.** Oito dos dez critérios estão provados; dois não podem ser
provados por este caminho, e um deles descobriu um defeito a montante que o
cutover não causou mas passou a expor. Está tudo discriminado abaixo, item por
item, com o que foi medido e o que não foi.

```
OPS_CANONICAL_GATE                 YES     medido, corrido na producao
HARDCODED_SOURCE_LIST_REMOVED      YES     saiu de candidatas/italy_profiles.mjs
CANARY_RUN1_PASS                   YES     2 fontes · 2 HEALTHY · 0 FAILED
CANARY_RUN2_INCREMENTAL            NO      ← 0 SKIPPED_KNOWN, 32 refeitos
ESCRITA_CANONICA_NA_SALA           N/A     o caminho agendado nao tem passo de Sala
LEAKS                              0/0/0/0 provado por ID, nao por contagem
REFETCHES_CONTROLADOS              NO      ← 32 refetches desnecessarios medidos
PAID_USD                           0       nenhuma rota paga tocada
SCHEDULER_POINTS_TO_CANONICAL_PATH YES     provado por disparo real
ROLLBACK_PROVEN                    YES     restaurado e conferido byte a byte

BIG_COLLECTION_ALLOWED = NO
```

`BIG_COLLECTION_ALLOWED = NO` **declarado, nunca executado.** O motivo é um
número, não uma opinião: o canário tocou 2 fontes e produziu **71 versões novas
no armazém com zero palavras mudadas**. Multiplicar isso por 170 fontes antes de
consertar o comparador enche o armazém de cópias da nossa própria pegada.

---

## FASE 0 — KNOW-HOW CANÓNICO PUBLICADO

```
KNOW_HOW_DELTA = APLICADO · SINTONIA-EAME-KNOW-HOW.md §165
commit 220c3a0b · 222 linhas ACRESCENTADAS · 0 apagadas (git diff --numstat)
```

Medido antes, em `1593633f`:

```
PYTHONDONTWRITEBYTECODE   0 ocorrencias  →  3
MISSING_ROUTE             0 ocorrencias  →  4
```

As oito lições, cada uma com âncora verificada no código:

| # | Lição | Âncora |
|---|---|---|
| 1 | `git diff` não prova execução em Python — o `.pyc` valida-se por `(mtime em segundos, tamanho)` | `provas/red_team_duas_portas.py:246` · o `M05` trocava `SINAIS_MINIMOS = 2` por `= 1`, mesmo tamanho, mesmo segundo |
| 2 | Protocolo cache-safe: `PYTHONDONTWRITEBYTECODE=1` **+** apagar `__pycache__` ao aplicar **e** ao restaurar **+** processo novo | `_correr`, `_apagar_cache`, `_restaurar` |
| 3 | Teste tautológico — nenhum matador itera a estrutura que julga | `tests/test_a_regra_de_t10.py` · dicionário `EXPULSOS` escrito à mão |
| 4 | Atacar primeiro o código recém-escrito | três sobreviventes da série estavam na peça acabada de escrever |
| 5 | Cinco nomes, nunca dois | `coleta/executor_texto_de_html.py:19` · `coleta/ingresso.py:627,645` |
| 6 | A ordem dos executores não é prioridade | `coleta/ingresso.py:539-555` · mutante `M12` |
| 7 | Deduzir não é provar — `sha256`, nunca nome de pasta | `_sha` · sustenta `NAO_RESTAURADOS = []` |
| 8 | Substring em régua de vocabulário | `admissao/admissao.py:651` · `soci` casou em `sociale 22 · association 10 · social 9 · sociali 8`, e **nunca** em `soci` |

### Correcção ao ponto 5 da missão

A missão listava `BLOCKED_BY_CONTRACT`. Esse nome **não existe** nesta árvore. O
quarto estado é uma **família**, e o motivo faz parte do nome:
`BLOCKED_BY_ROBOTS`, `BLOCKED_BY_CREDENTIAL`, `BLOCKED_BY_BOT_PROTECTION`,
`BLOCKED_BY_CURATOR_INTAKE_GATE`, `BLOCKED_BY_RELEVANCE`, `BLOCKED_BY_HUMAN`.
Escrito na secção como `BLOCKED_BY_<motivo>`, com a razão.

### Porque §165 e não §160

O último § **desta linha** é o §159. Mas o ficheiro vive em **135 branches** e as
linhas divergiram. Censo por título distinto:

```
§160  DOIS titulos   18 + 2 branches
§161  um titulo      18 branches
§162  DOIS titulos   10 + 2 branches
§163  um titulo       8 branches
§164  TRES titulos    4 + 2 + 2 branches
§165  LIVRE           0 branches
```

Escrever §160 punha um **terceiro** texto num número que já tem dois. No dia da
reconciliação, quem cita «§164» cita três coisas incompatíveis, e a citação deixa
de ser prova. Fica o salto §159 → §165, visível e com a razão escrita.

### Correcção de percurso apanhada na Fase 0

`provas/red_team_duas_portas.py` dizia no cabeçalho que o único ataque que tenta
sair à rede é o `M10`. É o `M11`. Os mutantes foram renumerados e o cabeçalho
ficou para trás; o `M10` é o `FACT_LOCATION` e não toca na rede. Corrigido.

---

## FASE 1 — PRODUÇÃO, MEDIDA ANTES DE TOCAR

```
OPS_PATH                  C:\eame-sintonia-ops
OPS_BRANCH                ops/italy-forward-only-live
OPS_HEAD                  d43adc1b5986f207bebc7df1dbf76bc6127383f3
OPS_REMOTE_HEAD           d43adc1b5986f207bebc7df1dbf76bc6127383f3   IGUAL
OPS_GIT_STATUS            3 ficheiros de livro modificados + 1 lock nao rastreado

SCHEDULED_TASK_EXISTS     YES   \SINTONIA-Italy-ForwardOnly
SCHEDULED_TASK_ENABLED    YES
SCHEDULE                  de hora em hora, desde 2026-09-07 (janela: 20h Europe/Rome)
LAST_RUN_TIME             2026-09-21 21:00:01
LAST_RESULT               0
COMMAND                   C:\eame-sintonia-ops\scripts\italy-forward-only-live.cmd
WORKING_DIRECTORY         C:\eame-sintonia-ops  (posto pelo .cmd, nao pelo agendador)

ACTIVE_PROCESSES          0
ACTIVE_COLLECTION_RUN     NO
```

### ⚠️ ACHADO 1 — A PRODUÇÃO NÃO COLHIA HÁ 14 DIAS, COM O LOG A DIZER SAÚDE

```
.italy-forward-only.lock   pid 44960   at 2026-09-07T18:00:02.213Z
LOCK_PID_VIVO = NAO
```

O processo 44960 não existe. Medido excluindo a árvore da própria medição — a
primeira tentativa casou consigo mesma, porque o `powershell` da medição contém
a substring que procura.

Estados no log de execuções, contados:

```
343  SKIPPED_LOCK_HELD        «outra coleta ja esta rodando»
  4  COMPLETED
  2  SKIPPED_OUT_OF_WINDOW
  1  FAILED_PRECONDITION
---
350  ticks
```

Última coleta real: **2026-09-07T18:00:03Z**. Cada um dos 343 ticks escreveu
`RUNNER_HEALTH: HEALTHY` ao lado do `SKIPPED_LOCK_HELD`, e o Agendador devolveu
`Ultimo resultado: 0` de hora em hora, por 14 dias.

```
UM LOCK QUE NINGUEM SEGURA PARA A COLETA
E DEIXA O LOG A DIZER SAUDE.
```

O lock saiu na Fase 4, depois do backup.

---

## FASE 2 — CENSO DA CÓPIA OPS

A produção estava **1032 commits atrás** da linha canónica e 18 à frente na parte
dela (base comum `30138cad`). Não era uma versão antiga do mesmo: era outra forma
de árvore — `scripts/` onde a linha canónica tem `coleta/`, `admissao/`,
`curadoria/`, `regras/`.

```
OPS_MISSING_FILES   8 de 8 pecas de Collection

  curadoria/collection_gate.py         FALTAVA
  regras/incrementalidade.mjs          FALTAVA
  regras/motor_de_rota.mjs             FALTAVA
  coleta/executor_texto_de_html.py     FALTAVA
  coleta/ingresso.py                   FALTAVA
  admissao/admissao.py                 FALTAVA
  coleta/italy_executor.py             FALTAVA
  coleta/italy_recurrent_collect.mjs   FALTAVA (vivia em scripts/, versao velha)

OPS_STALE_FILES     scripts/italy_recurrent_collect.mjs   180 linhas
                    coleta/italy_recurrent_collect.mjs    258 linhas (canonica)

OPS_DIVERGENCES     nenhuma peca de Collection partilhada entre as duas linhas
```

### ⚠️ ACHADO 2 — OS DOIS LADOS ESCREVEM NO MESMO CAMINHO DE DADOS

Um checkout cego da linha canónica em `C:\eame-sintonia-ops` teria apagado
evidência real:

```
ARMAZEM   25 PDF da ARPAV (IT-T2-002) existiam SO na producao
          11 estavam nas duas linhas · 168 so na canonica

LIVROS    mesmo caminho, mesmo esquema, corridas DIFERENTES:
          runs.ndjson        7 na producao ·  58 na canonica
          observations.ndjson 175 na producao · 445 na canonica
```

---

## FASE 3 — BACKUP E ROLLBACK **PROVADO**

```
PRE_CUTOVER_HEAD            d43adc1b5986f207bebc7df1dbf76bc6127383f3
PRE_CUTOVER_CONFIG_HASH     4b472cf5748abf733d492787816596c014f2627640d977fcf9e8863ec1999eaa
                            (scripts/italy_profiles.mjs)
PRE_CUTOVER_TASK_COMMAND    C:\eame-sintonia-ops\scripts\italy-forward-only-live.cmd

HARDCODED_SOURCE_LIST_PRESENT   YES
OWNER_FILE                      scripts/italy_profiles.mjs:7  (canonica: candidatas/italy_profiles.mjs:7)
CURRENT_SOURCE_SELECTION_PATH   PROFILE.SOURCES -> collection_gate --ids=<lista> -> executarRodada
```

Backup em `C:\Users\<utilizador>\auditoria-madrugada\BACKUP-PRE-CUTOVER-20260921\`,
fora do repositório, **sem segredos** (nenhum ficheiro de credencial rastreado; os
resultados de `grep secret|token` eram *design tokens* CSS):

- `ops-italy-forward-only-live.bundle` — 589 MB, `git bundle --all`
- `tarefa/SINTONIA-Italy-ForwardOnly.xml` — a tarefa exportada
- `arvore/` — o estado **não commitado** (o bundle não o leva) com sha256 de cada ficheiro

### `ROLLBACK_PROCEDURE_PROVEN = YES` — provado, não descrito

Restaurado do bundle para `C:\Users\<utilizador>\auditoria-madrugada\PROVA-ROLLBACK\`:

```
HEAD_RESTAURADO = HEAD_ESPERADO = d43adc1b                        BATE
ARMAZEM DA PRODUCAO   36 ficheiros   restaurados byte a byte  36/36
                                     em falta                     0
                                     diferentes                   0
BLOBS de livro e config                                          5/5 IGUAIS
```

⚠️ A primeira conferência dos 5 blobs deu **DIFERE** nos quatro. Era a armadilha
do CRLF: eu comparava `git show HEAD:<caminho>` (que dá o blob, com LF) contra o
ficheiro em disco (que o checkout converte para CRLF). Comparados blob contra
blob, os cinco batem.

---

## FASE 4 — A LINHA CANÓNICA INSTALADA, COM A EVIDÊNCIA TRAZIDA

Ramo novo `ops/cutover-prod-v1` a partir de `220c3a0b`, mais o que só a produção
tinha. **Não** foi checkout cego.

```
ARMAZEM   os 25 PDF da ARPAV voltaram por `git checkout ffee246a --`

LIVROS    uniao, nao escolha:
          runs.ndjson          7 + 58  -> 59    (1 so da producao)
          observations.ndjson  175 + 445 -> 476 (31 so da producao)
          logs/runs.log        350 + 1 -> 351   (350 so da producao)
```

```
DUAS HISTORIAS DO MESMO FICHEIRO NAO SAO DUAS VERSOES.
SAO DUAS PARTES, E ESCOLHER UMA APAGA A OUTRA.
```

### ⚠️ ACHADO 3 — UM CAMPO QUE SE REPETE NÃO É UMA CHAVE

A primeira união usou `DOCUMENT_VERSION_ID` como chave de
`observations.ndjson` e deu **213** linhas onde havia **476**. As 175 linhas da
produção carregam só **35** desses IDs: cada **revisita** escreve linha nova sobre
a **mesma versão** do documento. Aquele campo identifica a versão, não a
observação.

Deduplicar por ele apagava a história das revisitas — que é exactamente o que a
incrementalidade lê para decidir se refaz. A chave passou a ser a **linha
inteira**.

---

## FASE 5 — A LISTA FIXA SAIU

```
HARDCODED_SOURCE_LIST_REMOVED = YES
```

Estava em `candidatas/italy_profiles.mjs:7`:

```js
SOURCES: ["IT-T3-005", "IT-T2-002", "IT-T2-004"]
```

Medido contra o livro do Curator no dia: `IT-T3-005` em `SEMANTIC_REVIEW` (nunca
promovida), `IT-T2-002` e `IT-T2-004` em `READY_LEGACY`. **Nenhuma das três era
elegível, e a lista dizia que as três eram.**

### O defeito não era só a lista — era o papel do portão

Antes, o passo 6b perguntava `collection_gate.py --ids=<lista fixa>`. O portão
era **filtro** de uma lista de outra pessoa.

```
UM PORTAO QUE SO FILTRA UMA LISTA NAO DECIDE A POPULACAO.
DECIDE QUEM, DENTRO DA LISTA DE OUTRA PESSOA, PODE PASSAR.
```

Pergunta-se agora **sem `--ids`**. A resposta **é** a população:

```
COLLECTION_SOURCE_SELECTION   COLLECTION_GATE
COLLECTION_ELIGIBLE           8    IT-T10-018 IT-T10-022 IT-T5-041 IT-T5-049
                                   IT-T7-017 IT-T7-033 IT-T7-042 IT-T7-043
ELIGIBLE_WITH_CONTRACT        7
ELIGIBLE_WITHOUT_CONTRACT     1    IT-T5-041
COLLECTION_REFUSED_TOTAL      79   77 READY_LEGACY · 2 HUMAN_REVIEW_REQUIRED
```

### Correcção a uma nota da minha própria memória

A memória deste projecto dizia «interseção **ZERO** entre as 8 elegíveis e as 7
do coletor». Nesta árvore isso é falso: o coletor tem **186 contratos**, e **7 das
8 elegíveis têm contrato**. Só `IT-T5-041` não tem. A nota foi medida noutra
árvore.

### Elegível não é alcançável — são duas perguntas

O passo 6 conferia contratos **antes** do portão, sobre a lista fixa: conferia o
caminho antes de saber o destino. Passou a 6c, sobre a população real:

```
ELEGIVEL SEM CONTRATO NAO E `FAILED` NEM `NOT_APPLICABLE`.
E `ELIGIBLE_WITHOUT_CONTRACT`, E FICA DITO.
```

Não para a corrida. As 7 seguem; a 1 fica dita, porque essa lista é a única que
diz onde falta trabalho.

### `NÃO SEI` onde antes ia o tamanho da lista

Oito saídas antecipadas escreviam `SOURCE_NOT_MEASURED = PROFILE.SOURCES.length`.
Antes do portão esse número não se sabe: passou a `null`.

```
`NAO SEI` E UM VALOR. `0` NO LUGAR DE `NAO SEI` E UMA MENTIRA.
```

### Vazamentos — provados por ID, não por contagem

`provas/o_cutover_nao_vaza.py`, **zero rede**:

```
READY_LEGACY_LEAK        0
HUMAN_REVIEW_LEAK        0
POLICY_BLOCK_LEAK        0
CAPABILITY_BLOCK_LEAK    0
CUTOVER_NAO_VAZA       YES
```

Cruza os **IDs** recusados com os **IDs** a colher. Duas contagens iguais não
provam que são os mesmos. Os quatro saem no relatório mesmo quando o motivo não
ocorreu: um vazamento que desaparece porque a lei não foi invocada não se
distingue de um que desaparece porque ninguém o mediu.

### A guarda 32 mudou de lei, e a nova é mais dura

A velha exigia que o perfil tivesse **exactamente** as três fontes escritas à
mão. Ela guardava a lista errada contra mudança.

```
UMA GUARDA QUE FISCALIZA UMA LISTA FIXA PROTEGE A LISTA, NAO A LEI.
```

A nova exige: perfil sem `SOURCES`, sem nenhum `SOURCE_ID` em campo nenhum,
`POPULACAO` declarada, e o coletor a perguntar sem `--ids`. Com controlo
**positivo** (um perfil de mentira com lista tem de reprovar) e **negativo** (um
ficheiro que só *explica* o defeito tem de passar). A busca ignora linhas de
comentário — sem isso, o comentário que explica o defeito era lido como
reincidência.

### `NEW_FAILURES = 0`, comparado por nome

```
BASE (copia limpa de 220c3a0b)   349 passaram · 73 falharam
DEPOIS DA FASE 5                 352 passaram · 73 falharam
so na minha: 0        so na base: 0
```

⚠️ A primeira comparação deu «0 falhas nos dois lados». O filtro não casava o
formato das linhas (`FALHA ...`, sem indentação). **Zero capturado não é zero
existente** — o marcador foi conferido antes de se acreditar na conta.

### Dois testes seguiram a lei nova, e mordem

`test_o_perfil_agendado_nao_promove_fonte_nenhuma` procurava
`BLOCKED_BY_CURATOR_INTAKE_GATE` no coletor. Aquele estado era o esperado
**enquanto** o perfil tinha lista. Sem lista, deixou de poder acontecer por essa
via.

```
ENQUANTO O PERFIL NOMEAVA FONTES, O MELHOR QUE O PORTAO PODIA
FAZER ERA DIZER NAO. AGORA ELE DIZ QUEM.
```

Na prova de **runtime**, o valor esperado deixou de sair do mesmo JSON que
fiscaliza: o portão é perguntado outra vez, **por outro caminho** (em processo,
`CG.elegiveis()`, contra o subprocesso que o coletor usa).

```
DOIS CAMINHOS INDEPENDENTES QUE DAO O MESMO NUMERO SAO UMA PROVA.
UM CAMINHO SO E UM ECO.
```

---

## FASE 6 — O CURADOR NÃO DISPARA COLLECTION

```
COLLECTION_AUTOMATIC_TRIGGER_FROM_CURATOR = NO     provado
SOURCE_CURATOR_AUTO                       = NO     ← medido, e a missao esperava YES
DISCOVERY_AUTO                            = NO     ← idem
```

O que foi medido nesta máquina:

- **Uma** tarefa agendada relacionada com o projecto: `\SINTONIA-Italy-ForwardOnly`,
  o lançador da coleta. (Os outros três resultados eram
  `\Microsoft\Windows\WwanSvc\OobeDiscovery` — falso positivo da substring
  «discovery».)
- **Nenhum** processo de curador ou supervisor a correr.
- **Nenhum** workflow do GitHub com agenda para curador ou descoberta.
- `.github/workflows/sintonia-scrap.yml` é `workflow_dispatch` (só à mão) e tem
  escrito no corpo: *«NUNCA se chama italy_pilot_collect.mjs daqui»*.
- `curadoria/test_collection_gate.py::NenhumCaminhoParaleloArrancaColeta` obriga
  **todo** caminho até ao coletor a estar classificado, e os de produção a
  perguntarem ao portão.

Ou seja: o curador **não** dispara coleta — mas também **não corre sozinho** nesta
máquina. O `YES` que a missão dava por conhecido não se confirma aqui.

---

## FASE 7 — TESTE OFFLINE NA PRÓPRIA CÓPIA DE PRODUÇÃO

Duas voltas, ambas com `--so-o-portao` (para no passo 6b, **nenhuma** fonte
tocada).

**Volta 1, com a lista fixa ainda ligada** — o resultado certo, e a prova de que a
instalação da Fase 4 estava viva (o coletor velho nunca perguntava ao portão):

```
RUN_STATE               BLOCKED_BY_CURATOR_INTAKE_GATE
COLLECTION_ELIGIBLE     0
COLLECTION_REFUSED      IT-T3-005:ESTADO_NAO_READY
                        IT-T2-002:READY_LEGACY
                        IT-T2-004:READY_LEGACY
RUNNER_HEALTH           HEALTHY
```

`RUNNER_HEALTH` continua `HEALTHY`, e está certo: quem disse não foi o portão, e
dizer não é a função dele. Culpar a pista por o guarda ter mandado parar era o
defeito antigo.

**Volta 2, depois da Fase 5:**

```
COLLECTION_GATE_USED             YES
HARDCODED_SOURCE_LIST_USED       NO
INCREMENTALITY_PRESENT           YES   regras/incrementalidade.mjs
HTML_ROUTE_PRESENT               YES   coleta/executor_texto_de_html.py
                                       e ligado em coleta/ingresso.py:556
T10_RULE_PRESENT                 YES   admissao/admissao.py
MOTOR_DE_ROTA_PRESENT            YES   regras/motor_de_rota.mjs
NEW_FAILURES                     0

RUN_STATE                        GATE_ONLY_NO_COLLECTION
COLLECTION_ELIGIBLE              8
ELIGIBLE_WITH_CONTRACT           7
SOURCE_ATTEMPTED                 0
```

---

## FASE 8 — O AGENDADOR

### ⚠️ ACHADO 4 — O CUTOVER PARTIU O AGENDADOR, E O AGENDADOR JÁ APONTAVA A LADO NENHUM

A tarefa apontava para `C:\eame-sintonia-ops\scripts\italy-forward-only-live.cmd`.
A Fase 4 instalou a linha canónica, e `scripts/` desapareceu. Medido logo depois:
`Ultimo resultado: 1` (antes era 0).

E o lançador canónico, em `ferramentas/`, chamava
`node scripts\italy_recurrent_collect.mjs` — **também** um caminho que já não
existe. O coletor vive em `coleta/`.

```
UM LANCADOR QUE APONTA PARA UM FICHEIRO QUE NAO EXISTE
FALHA DE HORA EM HORA SEM COLHER NADA E SEM DIZER PORQUE.
```

Nenhuma coleta se perdeu com isso: a produção já não colhia desde 2026-09-07 por
causa do lock órfão.

```
SCHEDULED_TASK_COMMAND_BEFORE   C:\eame-sintonia-ops\scripts\italy-forward-only-live.cmd
SCHEDULED_TASK_COMMAND_AFTER    C:\eame-sintonia-ops\ferramentas\italy-forward-only-live.cmd
LANCADOR_CHAMA_AGORA            node coleta\italy_recurrent_collect.mjs --profile forward-only-live --gate-hour

CADENCIA_ANTES                  1 hora
CADENCIA_DEPOIS                 1 hora     PRESERVADA
MODO_DE_LOGON                   interativo apenas (inalterado)
```

Nenhuma frequência nova foi inventada.

### `SCHEDULER_POINTS_TO_CANONICAL_PATH = YES` — provado por disparo real

`schtasks /Change` avisou que a senha de «executar como» está vazia. Em vez de
confiar no aviso, disparei a tarefa:

```
Ultimo resultado   0   (era 1)

o que ela escreveu:
  STARTED              2026-09-22T01:56:00.504Z
  RUN_STATE            SKIPPED_OUT_OF_WINDOW
  RUNNER_HEALTH        HEALTHY
  HORA_EM_ROMA         3
  SOURCE_ATTEMPTED     0
  SOURCE_NOT_MEASURED  null
  reason               sao 3h em Europe/Rome; a janela e 20h
```

Prova inofensiva de propósito: fora da janela das 20h, o coletor salta sem tocar
em fonte nenhuma. E `SOURCE_NOT_MEASURED = null` é o `NÃO SEI` novo a funcionar.

---

## FASES 9–11 — O CANÁRIO DE PRODUÇÃO, DUAS PASSAGENS

```
EGRESSO      146.70.182.38 · IT · Milan · AS9009 M247 Europe SRL
             dois medidores: ipinfo.io e ifconfig.co, ambos IT
PAID_USD     0     nenhuma rota paga tocada

PASSAGEM 1   OPS_forward-only-live_20260922020109_0d088d    96 s
PASSAGEM 2   OPS_forward-only-live_20260922020511_8be761   120 s

CANARY_LIMIT     2
CANARY_SUBSET    IT-T10-018 · IT-T10-022
CANARY_LEFT_OUT  IT-T5-049 · IT-T7-017 · IT-T7-033 · IT-T7-042 · IT-T7-043

SOURCE_ATTEMPTED  2    HEALTHY 2    DEGRADED 0    FAILED 0
```

### O instrumento do canário

`--canario-limite N` corta o **tamanho** da população; **não** escolhe fontes. A
população continua a sair inteira do portão, o limite fica depois dele, e a ordem
é alfabética para a segunda passagem cair sobre a mesma gente.

```
UM LIMITE QUE ESCOLHE QUAIS E UMA LISTA FIXA COM OUTRO NOME.
UM LIMITE QUE SO DIZ QUANTAS E UM LIMITE.
```

Inerte sem a bandeira (conferido). Número inválido dá `FAILED_PRECONDITION`, nunca
«limite ignorado».

### O que as duas passagens mediram

```
                            ANTES   APOS 1   APOS 2
armazem (ficheiros)          204      236      275
observacoes no livro         476      508      547
corridas no livro             59       60       61

RUN1_DETAIL_REQUESTS         32
RUN2_DETAIL_REQUESTS         39
nos dois (refeitos)          32
so na passagem 2              7
RUN2_SKIPPED_KNOWN            0     ← nada foi saltado por ja se conhecer
RUN2_REVALIDATED             39
UNNECESSARY_REFETCHES        32
bytes descarregados          3,86 MB + 4,53 MB = 8,4 MB
```

Todas as observações das duas corridas saíram `DOCUMENT_CHANGED_IN_PLACE` — 32 na
primeira, 39 na segunda. **Zero `SEEN_AGAIN`.**

### ⚠️ ACHADO 5 — 71 VERSÕES NOVAS SEM UMA PALAVRA MUDADA

Medido documento a documento, **tirando toda a marcação** e comparando o **texto
visível** (`provas/a_mudanca_e_nossa_pegada.py`, zero rede):

```
TEXTO_IGUAL      39 de 39
TEXTO_DIFERENTE   0 de 39
VEREDITO = A_MUDANCA_E_NOSSA_PEGADA
```

**Nenhuma palavra mudou em nenhum.** De onde vinha o «mudou», classificado linha a
linha:

```
23 documentos   SO rasto da nossa visita
                  · article:modified_time carimbado com a hora do NOSSO
                    pedido (2026-09-22T02:01:44 = a corrida)
                  · contador de visualizacoes 132 -> 134 (as nossas duas visitas)
                  · _session_key e _token do formulario, novos a cada pedido
                22 destes 32 tem o MESMO numero de bytes nos dois lados

 9 documentos   banners a rodar em zootecnicainternational.com: `zoote-target`
                com id novo por pedido, links de patrocinador com utm_source,
                imagem do banner, e os `</a>`/`</div>` que se deslocaram
```

```
UM SITE QUE CARIMBA A HORA DE QUEM O VISITA DEVOLVE UM FICHEIRO
DIFERENTE A CADA VISITA SEM TER MUDADO NADA.
QUEM COMPARA BYTES CONTA A PROPRIA PEGADA COMO NOTICIA.
```

⚠️ A **própria medição** foi corrigida duas vezes:

1. Deu «9 com mudança real». Ao olhar as linhas que ela contou, as 9 eram
   publicidade. Padrões apertados, com a razão ao lado de cada um.
   *Um classificador generoso devolve «mudou» e ninguém confere.*
2. Depois de o canário ser commitado, imprimia `0 de 0` — que se lê como «nenhuma
   mudança encontrada» e queria dizer «nada havia para comparar». Agora sai com
   código 2 e diz a frase inteira. *Zero comparado não é zero mudado.*

A prova **forte** não é a classificação por padrão: é o texto visível, que não
precisa de conhecer os padrões de antemão.

### Achado menor — a listagem também não é estável

A passagem 2 trouxe 7 artigos de `IT-T10-018` que a passagem 1 não trouxe, com 4
minutos de intervalo.

### O que o canário provou, e o que não pôde provar

| Prova pedida | Resultado |
|---|---|
| seleção pelo gate real | **SIM** · `COLLECTION_SOURCE_SELECTION = COLLECTION_GATE` |
| matéria real | **SIM** · 8,4 MB de HTML real, 2 fontes HEALTHY |
| sem refetch desnecessário | **NÃO** · 32 refetches com texto idêntico |
| RAW criado/reutilizado | **criado** (71) · **reutilizado 0** |
| dedup de storage | **NÃO** · 71 versões novas de conteúdo idêntico |
| rota HTML | presente e ligada; não exercida (o caminho agendado não deriva) |
| juízo real da admissão | **N/A** · o caminho agendado não tem passo de admissão |
| escrita canónica na Sala | **N/A** · ver abaixo |
| sem bypass | **SIM** · nenhuma fonte fora dos elegíveis foi tocada |

### `SALA_BEFORE = SALA_AFTER` — e isto NÃO é rota em falta escondida

Medido: o caminho agendado (`italy_recurrent_collect.mjs` →
`italy_pilot_collect.mjs`) vai de **FONTE → RAW → ARMAZÉM → LIVRO**. Ele **não
chama** `coleta/ingresso.py` nem `admissao/admissao.py`.

A perna **ADMISSION → SALA** é o **outro** caminho de produção declarado:
`coleta/italy_executor.py`, chamado por `pedido/receitas.py`. Os dois estão
classificados como `PRODUCTION_PATH` no mapa e no teste do portão, e ambos
perguntam ao portão.

Isto é desenho, não falha — e digo-o com a ressalva: **este cutover não provou a
perna da Sala**, porque o caminho que ele cortou não passa por lá. Quem quiser
essa prova tem de correr o segundo caminho de produção, e isso é outra missão.

Nota de ambiente: dois Postgres escutam em `127.0.0.1:54329` e `:54330`, mas
**nenhuma** variável da Sala está posta (`SINTONIA_SALA_BACKEND`,
`SINTONIA_SALA_DSN`, `SINTONIA_COLLECTION_DSN` todas vazias). Mesmo um caminho que
quisesse a Sala cairia em `FICHEIRO` por omissão.

### Sem push

Corrido com `--no-git`: `RUN_STORAGE_STATE = NOT_ATTEMPTED_NO_GIT`. O perfil ainda
aponta `OPS_BRANCH` para `ops/italy-forward-only-live`, e empurrar o `HEAD` desta
branch para lá sem perguntar era mexer no ramo antigo da produção. Os bytes ficam
commitados em `ops/cutover-prod-v1`.

---

## FASE 12 — RED TEAM

**Nenhuma mutação no estado de produção real.** Os ataques correram na árvore
canónica (`cutover-prod-v1`), que é uma cópia separada de
`C:\eame-sintonia-ops`. Protocolo cache-safe do §165 em cada volta: base verde
conferida antes (um matador já vermelho mata tudo e não guarda nada), `git diff` a
provar a mutação, `__pycache__` apagado **ao aplicar e ao restaurar**, processo
Python novo.

```
MC01  o portao nao recusa ninguem                 MORTO
MC02  fonte sem contrato entra na coleta          MORTO
MC03  a selecao deixa de sair do portao           MORTO
MC04  o portao volta a filtrar uma lista          MORTO

MUTANTES 4 · MUTANT_APPLIED 4 · MUTANT_KILLED 4 · SURVIVORS 0
RESTAURADOS 4/4 · arvore limpa no fim
```

Somado ao red team da série anterior, que continua verde nesta árvore:

```
provas/RED-TEAM-DUAS-PORTAS-V1.json   14 mutantes · 14 mortos · SURVIVORS 0
```

`SURVIVORS = 0` diz que **os testes guardam o que dizem guardar**. Não diz que os
testes cobrem tudo o que importa — e o Achado 5 é a prova disso: nenhum teste
existente reprova um comparador que conta a nossa própria pegada como notícia.

---

## MAPA

```
SYSTEM_MAP_CHECK = PASS
cadeia canonica: correr_a_cadeia.py REGERAR + VALIDAR
```

`P9_CODIGO_DECLARADO` reprovou com dois ficheiros que o mapa não conhecia. Peça
nova `C-PROVA-CUTOVER` em `Z-PROVA`, com as duas provas e as duas saídas JSON.
Peça própria, e não dentro de `C-PROVA-ROTA-DO-HTML`: provam outra coisa.

```
CODIGO NOVO SEM PECA NO MAPA E ARQUITETURA INVISIVEL.
```

---

## O QUE FICOU EM ABERTO

1. **O comparador de mudança conta a nossa pegada** (Achado 5). É o bloqueio da
   Big Collection. Consertar antes de escalar: comparar depois de normalizar o
   que é rasto de máquina, ou comparar o texto visível.
2. **`SOURCE_CURATOR_AUTO = NO` e `DISCOVERY_AUTO = NO`** nesta máquina. A missão
   dava-os por `YES`. Nada dispara o curador sozinho.
3. **`IT-T5-041` é elegível e não tem contrato.** Fica declarado em
   `ELIGIBLE_WITHOUT_CONTRACT`; ninguém a colhe.
4. **A listagem de `IT-T10-018` não é estável** entre corridas a 4 minutos.
5. **A perna ADMISSION → SALA não foi provada** por este cutover, porque o
   caminho agendado não passa por lá.
6. **O perfil aponta `OPS_BRANCH` para `ops/italy-forward-only-live`**, e a
   produção corre agora em `ops/cutover-prod-v1`. Alinhar antes de deixar o
   agendador empurrar sozinho.
7. **§160–§164 continuam com títulos em colisão** noutras branches. O §165 evita
   agravar; não resolve.

---

## EM PALAVRAS SIMPLES

Pensa na coleta como um **motorista** que vai todos os dias buscar jornais a
bancas na Itália.

**Onde estava a lista fixa, e se saiu.** O motorista levava um papel escrito à mão
com o nome de **três bancas**. Esse papel estava num ficheiro do computador
(`candidatas/italy_profiles.mjs`, linha 7). O problema é que o papel nunca falou
com o **fiscal** — o fiscal é quem decide quais bancas estão em condições de
serem visitadas. Fomos perguntar ao fiscal sobre as três bancas do papel: ele
disse **não** às três. Uma nunca tinha sido aprovada, e duas tinham sido aprovadas
com uma régua antiga, de antes de a régua de hoje existir.

**Sim, o papel saiu.** Agora o motorista chega, pergunta ao fiscal «quem posso
visitar hoje?» e o fiscal dá a lista. Hoje o fiscal diz **8 bancas**. Recusa 79.
Das 8 que ele aprova, o motorista sabe o caminho para **7** — a oitava
(`IT-T5-041`) fica escrita num papel à parte que diz «aprovada, mas ainda não
sabemos chegar lá». Não a escondemos.

**Se o agendador passou à linha canónica.** Passou — e no caminho descobri duas
coisas piores. Primeira: o despertador que manda o motorista sair **apontava para
uma garagem que já não existe**, e por isso falhava de hora em hora. Segunda, e
mais grave: **o motorista não saía da garagem há 14 dias**. Havia um cone de
trânsito esquecido na porta desde 7 de Setembro, posto por uma viagem que já tinha
acabado. O cone dizia «já tem alguém a sair, espera». De hora em hora, durante 14
dias, o registo escreveu *«tudo bem, saúde perfeita»* e não saiu ninguém. Tirei o
cone (guardei uma cópia dele antes), corrigi a garagem, e depois **disparei o
despertador para ver se funciona**: funcionou. Ele saiu, olhou o relógio de Roma,
viu que eram 3 da manhã e não 8 da noite, e voltou — que é exactamente o que devia
fazer.

**Quantas fontes e documentos no canário.** Não mandei o motorista a todas. Mandei
a **2 bancas**, e escrevi por extenso quais **5** ficaram de fora. Ele trouxe **32
jornais** na primeira viagem e **39** na segunda. Descarregou 8,4 megabytes. Não
gastou um centavo — nenhuma das bancas cobra.

**Quantos chegaram à Sala.** **Nenhum**, e aqui preciso de ser muito claro, porque
é fácil ler isto como avaria. A Sala é o **arquivo organizado** onde o material
fica utilizável. O caminho que este cutover consertou **não vai até lá** — ele vai
da banca até ao **depósito** (guarda o jornal inteiro, como veio, com a hora e a
prova de que é aquele). Levar do depósito ao arquivo é **outro caminho**, com
outro dono, que existe e está declarado. Não é uma ponte que falta e que eu
escondi: é uma ponte que fica noutra estrada. Mas também quer dizer que **este
canário não provou essa parte**, e não vou dizer que provou.

**O que mudou na segunda corrida — e aqui está o achado que importa.** Devia ter
mudado tudo. A segunda viagem, 4 minutos depois, devia ter olhado para os 32
jornais e dito *«estes já tenho, não preciso»*. Não disse. Disse que **todos os 32
tinham mudado**, e guardou 32 cópias novas.

Fui ver **palavra por palavra**. Tirei toda a formatação e comparei só o texto que
uma pessoa leria. Resultado: **39 de 39 jornais com o texto exactamente igual.
Nem uma palavra mudou. Nem uma.**

O que tinha mudado era isto: a banca **escreve na capa a hora em que tu chegaste**.
E tem um contador de visitas na capa que subiu de 132 para 134 — as nossas duas
visitas. E um número de senha que muda a cada pessoa que entra. Em 9 dos jornais,
o que mudou foram os **anúncios**, que rodam sozinhos.

É como tirar duas fotografias ao mesmo quadro na parede, com um relógio digital
no canto, e concluir que o quadro foi repintado porque o relógio está diferente.

```
QUEM COMPARA A FOLHA INTEIRA CONTA A PRÓPRIA PEGADA COMO NOTÍCIA.
```

**Se houve refetch inútil.** Sim: **32**. E o depósito engordou de 204 para **275**
ficheiros — **71 cópias novas sem uma palavra nova**. Isto **não** é defeito do
cutover. O cutover fez a escolha das bancas vir do fiscal, e essa parte funcionou.
Este é um defeito **mais antigo**, na maneira de comparar, que só apareceu porque
mandei o motorista sair **duas vezes seguidas** — que é para isso que serve um
canário.

**Se há vazamento.** **Zero**, nos quatro tipos. Nenhuma das 79 bancas que o
fiscal recusou entrou na viagem. E não confirmei isso contando — contei **nome por
nome**, porque duas contagens iguais não provam que são as mesmas bancas.

**Se o rollback está provado.** Está, e não por eu dizer. Antes de tocar em nada,
fiz uma **cópia inteira** da produção (589 MB) fora do repositório, sem nenhuma
senha lá dentro. Depois **restaurei essa cópia num sítio limpo** e conferi: os 36
ficheiros de material que a produção tinha voltaram **todos**, byte a byte, sem
faltar nem um. Se algo desta noite estiver errado, dá-se para trás.

Uma coisa que quase estraguei, e que vale dizer: a produção tinha **25 PDFs da
ARPAV** que a linha nova **não tinha**. Se eu tivesse instalado a linha nova por
cima, à bruta, esses 25 desapareciam. Trouxe-os de volta à mão. E os **livros de
registo** dos dois lados — que são cadernos onde só se acrescenta linhas, nunca se
apaga — **juntei** em vez de escolher um. Escolher um lado num caderno de
acrescentar apaga o outro lado: eram 31 observações e 350 registos que só existiam
do lado da produção.

**E se pode começar a Big Collection.**

```
BIG_COLLECTION_ALLOWED = NO
```

**Não.** Não porque o cutover falhou — a parte do fiscal funcionou e está provada.
É por causa do comparador. Com **2 bancas** e **duas viagens** ele já produziu 71
cópias iguais. Fazer isso com **170 bancas**, de hora em hora, enche o depósito de
fotografias do mesmo quadro — e no dia em que alguém perguntar «quantas notícias
novas tivemos esta semana?», o número vai estar enorme e vai estar errado.

Primeiro conserta-se a maneira de comparar. Depois escala.
