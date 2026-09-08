# HANDOFF DE EMERGÊNCIA — COLLECTION FOUNDATION · 2026-09-08

> **Para quem chega sem a conversa anterior.** Este ficheiro é autossuficiente:
> lendo-o, dá para continuar. A conta que o escreveu estava a ficar sem usage.
>
> **Nenhum segredo aqui.** Sem tokens, sem URLs de banco, sem chaves.

---

## A · REPOSITÓRIO

```
https://github.com/lucianodalondon-sys/eame-sintonia.git
```

⚠️ **Há dois repositórios SINTONIA.** Brasil é o `portal-sintonia`; Itália/EAME é
este, o `eame-sintonia`. É fácil trabalhar no errado.

## B · BRANCH CANÓNICA DE TRABALHO

```
claude/collection-foundation-integration-v1
```

## C · HEAD REMOTO MEDIDO (2026-09-08)

```
51a265509da4246b7069297a55f8eefaf07a9874   M1A: congela a inteligencia que ja existia
82ef1deb1f85975b3ce7ccffdc439f8ee2b3e4f7   ausencia de referencia direta nao e ausencia de conexao
a8d4de7b...                                 os dois ultimos atalhos saem, 51 -> 35
a675bc3f...                                 o mapa passa a calcular, resultado zero estradas fechadas
```

**Local == remoto, `0 ahead / 0 behind`, worktree limpa** no momento em que isto
foi escrito. **Medir outra vez antes de escrever.**

## D · BRANCH DESTE HANDOFF

```
handoff/collection-foundation-20260908-51a26550
```

Criada a partir do HEAD remoto medido. **Não escrever trabalho de engenharia
aqui** — é só para o handoff sobreviver.

## E · WORKTREE

Limpa. Se estiver suja quando chegares, **medir antes de deitar fora**: já houve
trabalho bom por commitar nesta história.

---

## F · AS BRANCHES QUE COLIDIRAM — a história curta

Três linhas fizeram trabalho sobreposto sobre a coleta italiana:

| branch | HEAD | o que é |
|---|---|---|
| `claude/collection-foundation-integration-v1` | `51a26550` | **a canónica.** É aqui que se trabalha |
| `claude/italia-biblia-integracao-v1` | `0736171c` | linha paralela, **abandonada**. Fez um censo de estradas com numeração própria (`RC-01..RC-08`) incompatível com a canónica |
| `claude/scrap-social-na-biblia-v1` | `a1513382` | o trabalho social, **já integrado** na canónica |

E **dentro da canónica**, duas sessões trabalharam ao mesmo tempo, no mesmo dia,
no mesmo problema, sem se verem.

## G · O QUE FOI INCORPORADO

- **`ROUTE_MEMBERSHIPS`** (`SOURCE 1:N ROUTES`) — feito pela outra sessão em
  `a8d4de7b`/`82ef1deb`. 46 associações, com `WHAT_IS_MISSING` por associação.
- **O social** — `social_persistencia.py`, migration `023`, threads
  `PARTIAL_RESULTS`.
- **O modelo de estradas por etapas** — `system-map/data/estradas-it.model.json`,
  com `OWNER` / `STATE` / `EDGE` / `PROOF_KIND` / `PROOF_REF` por etapa.
- **A trava da inteligência** — feita nesta linha, em `51a26550`.

## H · O QUE FOI DESCARTADO POR SER REDUNDANTE

Uma implementação **paralela** de `ROUTE_MEMBERSHIPS`, escrita nesta conta antes
de se descobrir que a outra sessão já a tinha feito melhor (27 associações contra
46, e sem `WHAT_IS_MISSING`).

Está preservada, **não empurrada**, no branch **local** (não existe no remoto):

```
m1a-membership-redundante-nao-usar
```

⚠️ **Não a reaproveitar.** A da branch canónica é melhor. Está guardada só para
não se ter apagado história.

> **As duas mediram, em separado, `7` fontes com rota provada e a ARPAV com duas
> rotas.** Duas medições independentes com o mesmo resultado é a melhor
> confirmação que há.

## I · O QUE EXISTE SÓ NESTA LINHA

A **trava da inteligência**. Nenhuma outra branch a tem:

```
system-map/scripts/censo_do_congelamento.py     o censo, por espécie
docs/operacao/TRAVA-DA-INTELIGENCIA.json        o contrato + manifesto declarado
tests/test_trava_da_inteligencia.py             16 testes
provas/trava_da_inteligencia_morde.py           a prova de que ela reprova
```

---

## J · ONDE ESTÁ A TRAVA DA INTELIGÊNCIA

Dois donos, e é de propósito que sejam dois — **mas respondem a perguntas
diferentes**:

| ficheiro | o que decide |
|---|---|
| `leis/fundacao_da_coleta.py` | **o dono canónico.** Declara `COLLECTION_FOUNDATION_CLOSED` e as 6 áreas proibidas por nome |
| `docs/operacao/TRAVA-DA-INTELIGENCIA.json` | o manifesto: **quais artefatos** estão congelados, com o `sha` de cada um |

`tests/test_trava_da_inteligencia.py` exige que os dois **concordem** sobre
`COLLECTION_FOUNDATION_CLOSED`. Dois sítios a declarar o mesmo facto é deriva à
espera de acontecer.

**Hoje: `COLLECTION_FOUNDATION_CLOSED = NAO`.**

## K · QUE ARTEFATOS ELA CONGELA

```
221  artefatos mencionam inteligência
 73  CONGELADOS   →  10 IMPLEMENTATION (todos com marca forte) + 63 PORTAL_UI
148  fora         →  80 DATA_SAMPLE · 32 menção fraca · 24 saída gerada
                     ·  8 TEST ·  4 INSTRUMENT
```

`FROZEN_AT_HEAD = 82ef1deb...` — a marca **histórica**, o ponto em que a
fotografia foi tirada. **Não** é onde se mede: mede-se sempre a árvore de agora,
contra os `sha` guardados.

O `GIT_BLOB_SHA` vem de `git hash-object`, **não** de `sha256` do ficheiro em
disco: aqui é Windows com CRLF, o Git guarda LF, e já se publicou um sha errado
por medir do lado errado dessa conversão.

**Quatro regras que custaram a aprender, e que não se devem desfazer:**

1. **Não congelar `leis/fundacao_da_coleta.py`.** Ela nomeia as áreas proibidas
   *para as bloquear*. Congelá-la é trancar a própria fechadura.
2. **Sem marca forte, nada é `IMPLEMENTATION`.** O contrário congelava
   migrations `.sql` que só têm a palavra lá dentro.
3. **A régua é mais larga no portal, de propósito.** No código de coleta
   «signal» é palavra de passagem; na tela é o produto.
4. **Saída gerada não se congela** — congela-se o gerador. Senão a trava
   reprovaria sempre que alguém medisse o sistema.

## L · COMO PROVAR `TRAVA_MORDE`

```bash
cd /f/eame-sintonia && python provas/trava_da_inteligencia_morde.py
```

Espera-se `TRAVA_MORDE=PASS`. Ela viola a trava das duas maneiras possíveis —
mexer num artefato congelado, e escrever inteligência nova ao lado — exige que
reprove nas duas, desfaz e confere. **Deixa a worktree limpa.**

> **Uma trava que passa sempre é indistinguível de uma trava desligada.**

---

## M · SYSTEM MAP

```bash
python system-map/scripts/validate_system_map.py     # SYSTEM_MAP_CHECK=PASS
```

Cadeia (correr por esta ordem, e só depois validar):

```
scan_repo → scan_sources → scan_casco → censo_da_coleta → censo_do_corpus_it
→ censo_de_identidade_it → censo_do_armazem_it → censo_das_derivacoes
→ censo_das_estradas_it → censo_do_congelamento → pente_fino_da_coleta
→ generate_system_map
```

⚠️ **Em Windows, o gerador reescreve ficheiros com CRLF** e cria 25 mil linhas de
diff falso em `italia-portale/client/system-map/{index.html,map.css,map.js}` —
esses estão marcados `-text` no `.gitattributes`. **Restaurar esses três antes de
commitar** e normalizar os restantes para LF. Medir com
`git diff --ignore-cr-at-eol` para ver a mudança real.

## N · ROUTE CLASSES

```
ROUTE_CLASSES_MODELED            12
ROUTE_CLASSES_ARCHITECTURE_CLOSED 0      ← nenhuma fechada
ROUTE_CLASSES_WITH_PROVEN_MEMBERSHIP 2   ← RC-1, RC-9
ROUTE_CLASSES_REQUIRED_TOTAL     UNKNOWN ← e continua desconhecido de propósito
OBSERVED    RC-1, RC-2
DB_TESTED   RC-5
BLOCKED     RC-6, RC-7, RC-8   (com razão escrita)
DEBT        RC-9               (Git como estado operacional, contra P-011)
```

## O · FONTES

```
TOTAL                              54
SOURCES_WITH_PROVEN_ROUTE           7
SOURCES_WITH_ONLY_CANDIDATE_ROUTE  24
SOURCES_ROUTE_UNKNOWN              23
SOURCES_BLOCKED                     0
```

## P · CADA NÚMERO RESPONDE A UMA PERGUNTA DIFERENTE

⚠️ **Este é o erro mais fácil de repetir neste projeto.** Durante semanas, `51`
foi publicado como se respondesse a tudo.

| número | a pergunta a que responde |
|---:|---|
| `SOURCE_VERDICT_UNKNOWN` = **51** | «esta fonte **presta**?» — julgamento sobre o *conteúdo* |
| `ACCESS_METHOD_UNKNOWN` = **35** | «por onde se **entra**?» — a porta |
| `SOURCES_WITHOUT_PROVEN_ROUTE` = **47** | «alguma cadeia já foi **percorrida** de ponta a ponta?» |
| `SOURCES_ONLY_CANDIDATE` = **24** | dessas 47, quantas têm ao menos uma **pista** |
| `SOURCES_ROUTE_UNKNOWN` = **23** | dessas 47, quantas **não têm nada** |
| `ROUTE_MEMBERSHIPS_PROVEN` = **8** | pares (fonte, estrada) com prova — **8 para 7 fontes**, porque uma tem duas |
| `ROUTE_MEMBERSHIPS_CANDIDATE` = **34** | pares com pista, sem prova |
| `ROUTE_MEMBERSHIPS_DECLARED` = **4** | pares que o catálogo **afirma**, sem provar |
| `ROUTE_CLASSES_MODELED` = **12** | quantas estradas alguém **desenhou** |
| `ROUTE_CLASSES_WITH_PROVEN_MEMBERSHIP` = **2** | quantas alguém **percorreu** |
| `ROUTE_CLASSES_REQUIRED_TOTAL` = **UNKNOWN** | quantas o sistema **precisa** — e ninguém sabe |

> **O número que desceu (51 → 35 → 23) é sobre PISTAS, não sobre PROVAS.**
> Continuam **47** fontes sem caminho percorrido. O que desceu foi quantas não
> têm sequer uma pista. **Pista não é rota.**

## Q · ARPAV — `IT-T2-002` — e as suas duas rotas

A fonte que desmentiu o modelo `SOURCE → uma ROUTE_CLASS`:

| estrada | prova | onde se confere |
|---|---|---|
| `RC-1` OFFICIAL_HTTP_DOCUMENT | canário: `raw_asset 890`, `derived_artifact 1`, retry `REUSED` | **o banco** |
| `RC-9` GIT_LEDGER | 124 observações | `data/collection-ledger/italy/observations.ndjson` |

**`ROUTE_CLASS` é propriedade do par (FONTE, CADEIA) — não da fonte.**

⚠️ A prova da `RC-1` **não está neste repositório**. Os censos leem ficheiros;
essa prova vive em `collection_run` / `raw_asset` / `derived_artifact`. Quem
quiser confirmar tem de abrir o banco.

## R · RC-1 · OFFICIAL_HTTP_DOCUMENT

```
JÁ EXISTE (observado)  DISCOVER · FETCH · RAW · RUN · DERIVED
NÃO SE APLICA          CHECKPOINT  (download único: não há cursor a guardar)
FALTA                  STRUCTURED · ADMISSION
ARCHITECTURE_CLOSED    NÃO
```

> O documento chega, é preservado, é derivado — **e para**. A cadeia tem um fim
> que não é uma porta: é um beco.

⚠️ `guarda/importar_italia.py` **existe** e escreve estrutura, mas **não lê
`derived_artifact` nem `raw_asset`**. `admissao/admissao.py` tem chamadores, mas
nenhum recebe a saída da RC-1.

    OWNER EXISTS ≠ OWNER CONNECTED.

**É a estrada com mais retorno para fechar**: é a única com tudo o resto provado.

## S · RC-5 · REGULATORY_BULK_IMPORT

```
JÁ EXISTE   RUN · STRUCTURED   (ambos LIVE_SCHEMA)
FALTA       DISCOVER · FETCH · RAW · ADMISSION
ARCHITECTURE_CLOSED  NÃO
```

    LIVE SCHEMA ≠ COLLECTION CLOSED.

Os dados chegam ao importador **sem passar por bruto nenhum**. Ter tabela viva
não é ter coleta.

## T · MIGRATION 023

```
supabase/migrations/023_comentario_tem_id_e_a_thread_tem_pai.sql
```

**Existe no repositório. `DB_TESTED` em Postgres descartável. NÃO está aplicada
em produção.** Não aplicar sem missão que o autorize por escrito.

## U · PRODUÇÃO — o que foi e não foi aplicado

| | |
|---|---|
| aplicada | migration `022` (o derivado ganha casa) · blob `230be77d...` |
| **não** aplicada | `023` |
| escrito em produção | **um** canário italiano: 1 `collection_run`, `raw_asset 890`, `derived_artifact 1` |

⚠️ **`022` está LIVE. Não editar um byte dela** — migration aplicada é artefato
imutável. Se mudar, vira outro artefato e o ledger deixa de bater.

**Esta sessão escreveu ZERO em produção.**

## V · INTELIGÊNCIA

**CONGELADA.** 0 implementação, 0 escritas, 0 ativação.

Permitido: **ler**, pesquisar, escrever contratos. **Bloqueado: implementar.**

A trava **não** impede: ler código, preservar histórico, corrigir defeito que
ameace dados, medir o que a inteligência futura vai esperar da coleta.

## W · ABA BÍBLIA / DELIVERY

**PARADA.** Não mergear.

```
claude/italia-biblia-integracao-v1     0736171c
claude/biblia-canonica-da-coleta       37020bcc
claude/integration-acervo-portal-v1    11d2c3dd
claude/acervo-to-package-intelligence-v1  fb96f49d
```

O sensor ACERVO→PORTAL e a entrega vivem nessa linha. **Delivery vem depois da
Inteligência, que vem depois da fundação fechar.**

---

## X · A ORDEM DECIDIDA PELO DONO DO PROJETO

```
M1
  → OBSERVABILITY + DIAGNOSTICS + FLOW LINEAGE
    + COLLECTION MANAGEMENT + EVOLUTION FOUNDATION
      → M2
        → DEMAIS ROTAS
          → COLLECTION_FOUNDATION_CLOSED
            → INTELLIGENCE
              → DELIVERY
                → CONTINUOUS EVOLUTION
```

**Não começar a M2** antes de a observabilidade ter o mínimo fechado.

## Y · COLISÕES JÁ OCORRIDAS, E A REGRA

Em 2026-09-08, duas sessões trabalharam na mesma branch, no mesmo problema, ao
mesmo tempo. A segunda só descobriu quando o `push` foi **recusado** — depois de
gastar a missão inteira.

**A regra:**

1. `git fetch` e medir branch/HEAD **antes de começar** — não no fim.
2. `git fetch` outra vez **antes de cada commit**.
3. **Nunca** `git push --force`.
4. Se o remoto andou: preservar o próprio trabalho num branch local, `reset` para
   o remoto, e **reaplicar só o contributo único**.
5. Se a outra sessão fez o mesmo melhor: **não duplicar.** Ficar com o melhor por
   medição, e dizê-lo.
6. Guardar trabalho por commitar num `patch` **fora** do repositório — dentro,
   contamina censos que leem ficheiros não rastreados.

## Z · COMANDOS MÍNIMOS PARA VERIFICAR TUDO

```bash
cd /f/eame-sintonia
git fetch origin
git rev-parse --abbrev-ref HEAD && git rev-parse HEAD
git rev-list --left-right --count HEAD...origin/claude/collection-foundation-integration-v1
git status --porcelain
python system-map/scripts/censo_das_estradas_it.py
python system-map/scripts/censo_do_congelamento.py
python system-map/scripts/validate_system_map.py
python provas/trava_da_inteligencia_morde.py
python -m unittest discover -s tests -q
```

⚠️ Neste Windows o Python é `py`, e `PYTHONIOENCODING=utf-8` é preciso para o
gerador não rebentar a imprimir emoji.

## AA · FALHAS HERDADAS CONHECIDAS

**`python -m unittest discover -s tests` dá 71 falhas — e 71 é a linha de base.**
São anteriores a este trabalho. A casa corre os testes pela cadeia, não por
`discover`. **Medir a linha de base antes de culpar uma mudança:**

```bash
git stash push -u -q && python -m unittest discover -s tests -q 2>&1 | grep -cE "^(ERROR|FAIL):" ; git stash pop -q
```

`system-map/tests/test_system_map.py` **passa quando corrido directamente** e
falha em modo `discover` (corre duas vezes e a verificação de determinismo
compara um ficheiro reescrito no meio). Não é falha real.

## AB · PRÓXIMA MISSÃO

**OBSERVABILITY + DIAGNOSTICS + FLOW LINEAGE + COLLECTION MANAGEMENT +
EVOLUTION FOUNDATION**, por checkpoints:

```
O1  censo dos donos (REUSE FIRST — não criar schema antes de o censo fechar)
O2  contrato de telemetria (sem instalar OTel/Grafana/Prometheus)
O3  scanner mínimo local, com fixture, sem rede
O4  relatórios por run/hora/source/route/executor/stage
O5  collection management (contratos; sem AI live)
O6  source learning (ciclo de vida; sem SOURCE_SCORE mágico)
O7  evolution foundation (só a espinha; sem ML/bandit/auto-promoção)
O8  System Map: sem dado → NOT_MEASURED, nunca verde por silêncio
```

**Leis para esta missão:**

```
MODULE WORKS ≠ EDGE WORKS ≠ FLOW WORKS
INPUT ≠ OUTPUT quando o grão muda
100% não precisa CHEGAR — 100% precisa ser EXPLICADO
UNACCOUNTED_INPUT deve ser 0
ERROR ≠ REJECTED · UNKNOWN ≠ ZERO · NOT_RUN ≠ ERROR
```

## AC · RISCOS E CONTRADIÇÕES AINDA ABERTAS

### ⚠️ 1 · Contradição sobre o que «M1 fechada» significa — **por resolver**

| onde | o que diz |
|---|---|
| `82ef1deb` + o mapa (secção G) | **M1 = FECHADA**, com `UNKNOWN` residual honesto: a fundação é gate por **classes de estrada**, não exige zero `UNKNOWN` por fonte |
| `51a26550` (o teste da trava) | exige `SOURCES_ROUTE_UNKNOWN = 0` **e** `SOURCES_WITH_ONLY_CANDIDATE_ROUTE = 0` para destravar |

**As duas não podem ser canónicas ao mesmo tempo.**

**A decisão do dono:** vale a primeira. M1 fecha com `UNKNOWN` residual honesto,
desde que a evidência barata tenha sido esgotada, `UNKNOWN` não tenha virado
`BLOCKED` artificialmente, e cada residual nomeie a próxima prova.

**Portanto o teste da trava está a inventar um critério mais forte que a lei
canónica, e isso é o defeito a corrigir.** A trava deve **consumir** o veredito
de `leis/fundacao_da_coleta.py`, não redefinir o que «fundação fechada»
significa.

    ONE QUESTION → ONE OWNER.

Separar em três sinais distintos:

```
M1_CLASSIFICATION_PASS        = CLOSED       (a classificação acabou)
SOURCE_NETWORK_COVERAGE       = INCOMPLETE   (47 sem rota provada — dívida visível)
COLLECTION_FOUNDATION_CLOSED  = NO           (as estradas continuam abertas)
```

⚠️ Isto **não** significa que `UNKNOWN` deixou de importar. Continua dívida
operacional visível no System Map.

### 2 · `RC-9 GIT_LEDGER` é dívida, não estrada

Estado operacional em Git, contra a `P-011`. Não é para fechar: é para **mudar de
dono**, daqui para a frente, sem apagar história.

### 3 · O ledger esconde mais de uma cadeia

As fontes da `RC-9` diferem em `MIME_ASSINATURA` (`PDF` / `HTML` / `TEXTO`) e uma
delas tem `DISCOVERY_DEGRADED = INDEX_REQUIRES_BROWSER`. **Mesmo script não é
mesma estrada.** Mas quatro formatos também não são quatro estradas só por serem
quatro: separar exige comparar `AUTH`, `DISCOVER`, `FETCH`, forma do bruto,
modelo incremental e derivação.

### 4 · Ciência: metadado não é artigo

`SCIENCE_METADATA_API` traz **metadado**. Trazer o **texto integral** é outra
cadeia — outra origem, outro objeto, outro custo (parte é fechada por
assinatura). Não fingir que metadado coletado é paper coletado.

### 5 · O probe italiano só mediu a porta

`data/samples/IT-PROBE/probe-fase-c.json`, de 2026-09-07, saída **Milano · IT**,
43 URLs. Os 31 `ACCESS_OK` vieram **todos** em `text/html`: páginas de entrada,
não documentos.

    FRONT_DOOR_ACCESS ≠ DOCUMENT_ROUTE.

⚠️ **Não repetir o probe de uma máquina com saída não italiana.** Um `403` visto
do país errado não é bloqueio — é um artefato da localização, e marcaria como
fechada uma porta que está aberta.

## AD · O QUE NÃO SE DEVE FAZER

- **Não** mergear a branch Bíblia/Delivery
- **Não** implementar Inteligência (ler e escrever contratos: pode)
- **Não** corrigir o Portal
- **Não** correr Apify, nem gastar API paga, nem quota relevante
- **Não** fazer coleta grande
- **Não** escrever produção
- **Não** aplicar a migration `023`
- **Não** editar a migration `022` (está LIVE)
- **Não** `git push --force`
- **Não** `git add -A` às cegas
- **Não** apagar história
- **Não** esconder colisão
- **Não** marcar fonte como `BLOCKED` sem alguém ter tentado e **escrito porquê**
- **Não** publicar «o SINTONIA tem N estradas» como facto fechado enquanto
  `ROUTE_CLASSES_REQUIRED_TOTAL` for `UNKNOWN`

---

## A REGRA QUE VALE MAIS DO QUE ESTE FICHEIRO

    UNKNOWN HONESTO É MELHOR QUE MAPA COMPLETO POR PALPITE.
