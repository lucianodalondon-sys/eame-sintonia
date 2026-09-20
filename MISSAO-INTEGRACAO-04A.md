# MISSÃO — INTEGRAR O HANDOFF 04A: SOMENTE AS 18 FONTES HTML REALMENTE READY

```
BANCADA      C:/Users/London1/orca/workspaces/eame-sintonia/curator-04a-integration
BRANCH       curator-04a-integration
BASE         claude/contract-provenance-cutover-v1 @ 370ce450   (HEAD real, medido)
FONTE        claude/bot-de-fontes-v2-plano @ 376c0d9b           (HEAD real, medido)
WORKTREE DO CURATOR (leitura)  C:/bot-fontes-v2
```

**Git vence qualquer handoff, incluindo este ficheiro.** Tudo abaixo marcado como
`MEDIDO` foi medido pelo coordenador em 2026-09-20. **Confirma cada valor com os teus
próprios olhos antes de agir sobre ele** — não confies, reconfirma.

---

## 0 · O QUE O COORDENADOR JÁ MEDIU (confirmar, não confiar)

### Git

```
MEDIDO   origin/claude/bot-de-fontes-v2-plano   = 376c0d9b  (bate com o handoff)
MEDIDO   origin/claude/contract-provenance-cutover-v1 = 370ce450
MEDIDO   merge-base(curator, coordinator)       = 606974c3  (= origin/claude/it-trunk-v1)
MEDIDO   curator é 6 commits à frente de it-trunk-v1, 0 atrás
MEDIDO   coordinator é 25 commits à frente de it-trunk-v1
MEDIDO   INTERSECÇÃO DE FICHEIROS ENTRE OS DOIS LADOS = VAZIA (39 vs 57 ficheiros)
MEDIDO   o coordinator NÃO tocou em docs/fontes/ATLAS-DE-FONTES-EAME.md desde a base
MEDIDO   nenhuma branch remota (das 80 varridas) contém curadoria/ além da do curator
MEDIDO   nenhuma branch liga italy_contracts_curator.json a regras/ — trabalho não duplicado
```

### Os números do handoff 04A, reproduzidos do JSON (não do markdown)

Lidos de `curadoria/READY-FOR-COLLECTION-V1.json` @ 376c0d9b:

```
MEDIDO   FONTES no ficheiro                      77
MEDIDO   STATE = READY_FOR_COLLECTION            18   ← todas LOTE-HTML-ARTIGO
MEDIDO   STATE = CONTRACT_READY_ROUTE_BLOCKED    50   ← todas LOTE-YOUTUBE-FEED
MEDIDO   STATE = CONTRACTED_CANARY_FAILED         9
MEDIDO   ROBOTS_GATE_EXECUTED = YES              77/77
MEDIDO   ROBOTS_GATE_RESULT: ALLOWED 27 · DISALLOWED 50 · UNKNOWN 0
MEDIDO   BLOCK_REASON = ROBOTS_DISALLOWED_ROUTE  50/50
MEDIDO   canário HTML: PASS 18 · FAIL 9, com CONTROLO_POSITIVO OK (HTTP 200)
```

Os números batem com o handoff. **FASE 1 DO PEDIDO ESTÁ RECONCILIADA — não precisas
de a repetir, mas confirma o `git show` do ficheiro.**

### Identidade — zero colisão medida

```
MEDIDO   os 18 SOURCE_ID são distintos entre si
MEDIDO   COLISÃO dos 18 com regras/italy_contracts_onboarded.json (105 IDs) = 0
MEDIDO   COLISÃO dos 50 com o mesmo ficheiro = 0
MEDIDO   COLISÃO dos 77 contratos do curator com o onboarded = 0
MEDIDO   Atlas do curator = 268 fichas; Atlas do coordinator = 184; NOVAS = 84
MEDIDO   as 18 estão todas no Atlas do curator e NENHUMA já existia no do coordinator
```

### As 18, medidas uma a uma

Todas: `OUTPUT_TYPE=HTML` · `BATCH_ID=LOTE-HTML-ARTIGO` ·
`ACQUISITION.STRATEGY=HTML_LINK_DISCOVERY` · `ACCESS_INSTRUMENT=HTTP` ·
`AUTH_REQUIRED=false` · `BROWSER_REQUIRED=false` · `JS_REQUIRED=false` ·
`ROBOTS_GATE_RESULT=ALLOWED` · canário `PASS=true` com `DOCUMENT_ID` resolvido ·
chaves de `ACQUISITION` = `{STRATEGY, MATCH, INDEX_URL, LINK_PATTERN, MAX_TARGETS}`.

```
IT-T5-039  IT-T7-017  IT-T7-021  IT-T12-009  IT-T7-031  IT-T10-018
IT-T12-013 IT-T5-049  IT-T7-033  IT-T10-020  IT-T10-021 IT-T8-008
IT-T10-022 IT-T7-040  IT-T7-041  IT-T7-042   IT-T2-030  IT-T7-043
```

### ACHADO DO COORDENADOR — O MOTOR SABE EXECUTAR AS 18

```
MEDIDO   regras/motor_de_rota.mjs → ESTRATEGIAS inclui "HTML_LINK_DISCOVERY"
MEDIDO   o motor valida INDEX_URL e LINK_PATTERN para essa estratégia (linhas 182-184)
MEDIDO   as 18 usam exactamente a forma que contratoGenerico() já expande
MEDIDO   "YOUTUBE_CHANNEL_FEED" NÃO existe em motor_de_rota.mjs, italy_contracts.mjs
         nem coleta/italy_pilot_collect.mjs → as 50 não teriam sequer executor
```

Isto é uma **medição, não um veredito**: confirma-a e decide tu se as 18 são de facto
executáveis pela rota canónica. O contra-exemplo que a inverteria: algum campo que
`contratoGenerico()` exija e as linhas do curator não tragam.

### Evidência dos canários

```
MEDIDO   curadoria/evidencia/ está no .gitignore do curator — NÃO está commitada
MEDIDO   os bytes EXISTEM no disco em C:/bot-fontes-v2/curadoria/evidencia/ (131 pastas)
MEDIDO   a prova versionada é REAL-EXAMPLE-MANIFEST-V1.json (sha256 por ficheiro)
```

O próprio `.gitignore` do curator declara a intenção: *«na promoção, os bytes mudam para
o caminho canónico `data/samples/IT-SOURCE-SAMPLES/<SOURCE_ID>/`»*. **Decide tu** se
promover os bytes das 18 faz parte desta missão ou é passo separado; se decidires não
promover, di-lo explicitamente no relatório em vez de ficar em silêncio.

---

## 1 · O OBJECTIVO, E O QUE ELE NÃO É

Integrar **somente as 18 fontes HTML READY_FOR_COLLECTION** no trunk de trabalho
(`curator-04a-integration`, nascida de `claude/contract-provenance-cutover-v1`).

```
INTEGRAR FONTE  !=  COLETAR FONTE
```

Nenhuma Big Collection nesta missão. Nenhuma corrida. Nenhum RUN, RAW, Admission ou Sala.

---

## 2 · LINHA VERMELHA — O YOUTUBE NÃO SE TOCA

As 50 fontes YouTube ficam **preservadas e bloqueadas**. É PROIBIDO:

- usar `youtube.com/feeds/videos.xml`;
- criar workaround, rota alternativa ou executor específico;
- usar cookie, login, sessão ou pedir API key;
- inventar `LOCAL_YTDLP` para YouTube;
- alterar `BLOCK_REASON`;
- chamar qualquer das 50 de `READY`;
- apagar SOURCE_ID, fichas do Atlas, contratos ou caracterização das 50.

Estado a preservar, tal como está:

```
YOUTUBE_BLOCKED = 50   ·   BLOCK_REASON = ROBOTS_DISALLOWED_ROUTE
SOURCE_CHARACTERIZED = YES · CONTRACT_READY = YES · CANONICAL_ROUTE_READY = NO
```

Os 50 contratos podem permanecer no ficheiro da curadoria como registo. O que **não**
pode é qualquer um deles entrar na tabela que o motor lê como colectável.

---

## 3 · PROVA PRÉ-INTEGRAÇÃO — as 18, uma a uma

Antes de escrever seja o que for, produz e regista a tabela determinística:

```
SOURCE_ID · CANDIDATE_ID · SOURCE_NAME · ENDPOINT(INDEX_URL) · CONTRACT(hash)
CADENCE · CANARY_RESULT · ROBOTS_GATE · DOCUMENT_ID do canário
```

E os seis gates por fonte, todos verdes ou a fonte não entra:

```
CONTRACT_VALID · ROUTE_ALLOWED · ROBOTS_GATE · CANARY_PASS
SOURCE_ID_PRESENT · IDENTITY_RESOLVED
```

**Nenhuma fonte vira READY porque o HTTP respondeu.** Se alguma das 18 falhar um gate,
ela NÃO entra, e tu reportas qual e porquê — não corriges para obter verde.

---

## 4 · RECONCILIAÇÃO — Atlas e contratos

### Atlas (`docs/fontes/ATLAS-DE-FONTES-EAME.md`)

O curator acrescenta 84 fichas num bloco novo no fim
(`## ONDA SOURCE CURATOR — 2026-09-20`). Medido: o coordinator não tocou no ficheiro.

Para cada SOURCE_ID que fores integrar:

- **já existe igual** → não duplicar;
- **existe com divergência** → classificar a divergência e reportar, não fundir às cegas;
- **é novo** → integrar preservando o owner canónico.

`MESMA_ORGANIZACAO` preserva-se. **Nunca fundir dois SOURCE_ID só por pertencerem à
mesma organização** — canal e site são duas fontes (`COL-LAW-034`, e o caso
`IT-T8-001` canal vs `IT-T1-021` site está escrito no handoff).

**Decisão tua, a justificar:** integrar as 84 fichas (o bloco inteiro, que é a unidade
que o curator escreveu e inclui as 50 bloqueadas como fichas caracterizadas) ou só as
18. Argumento de cada lado, medido por ti, escrito no relatório. A regra que manda:
caracterização preservada não é o mesmo que fonte declarada colectável — o Atlas
regista fontes conhecidas, a tabela de contratos regista fontes que a casa sabe buscar.

### Contratos

`curadoria/italy_contracts_curator.json` tem 77 contratos. **Integrar como colectáveis
SOMENTE os 18 HTML READY.**

O dono do contrato continua a ser `regras/italy_contracts.mjs`. Medido: ele já lê
`italy_contracts_onboarded.json` via `readFileSync` (linha ~727) e expande cada linha
com `contratoGenerico()`. Há portanto pelo menos dois caminhos possíveis:

1. acrescentar as 18 linhas à tabela `italy_contracts_onboarded.json` existente;
2. carregar uma segunda tabela a partir do ficheiro da curadoria.

**Mede e escolhe**, com a razão escrita. Critério que manda: **não criar uma segunda
fonte de verdade permanente**. Se escolheres (2), o ficheiro tem de ser configuração
lida pelo dono único, nunca uma segunda autoridade — e nesse caso tem de conter
**apenas** as 18, ou o carregador tem de filtrar por estado de forma que o motor não
consiga alcançar as 50 por acidente. Prova isso com um teste.

Atenção ao formato: as linhas do `onboarded.json` têm as chaves
`{SOURCE_ID, OWNER, NAME, TERRITORY, BATCH_ID, OUTPUT_TYPE, ACQUISITION, EVIDENCE, SONDAGEM}`.
Os contratos do curator têm muito mais campos. Traduzir para o vocabulário do dono é
trabalho legítimo; **inventar valor que a curadoria não mediu não é**. `NAO SEI` e
`UNKNOWN` preservam-se como estão — não os substituas por defaults que parecem melhores.

---

## 5 · INTEGRAÇÃO

Aplicação **semântica**, nunca merge cego. Medido: a intersecção de ficheiros entre os
dois lados é vazia, logo não deve haver conflito — se aparecer algum, **não resolvas
por `ours`/`theirs` sem inspecionar**; classifica pelo owner do ficheiro.

Ficheiros de área própria da curadoria (`curadoria/*`) não colidem com nada. Decide se
os trazes todos (é o registo da missão 04/04A e a prova dos canários) ou só o
necessário, e justifica.

---

## 6 · TESTES E SYSTEM MAP

1. **Baseline primeiro.** Corre a bateria no HEAD da base (`370ce450`) ANTES de editar,
   guarda os nomes das falhas. Falha nova = regressão; falha igual ao baseline = dívida
   pré-existente. Compara **por nome**, nunca por contagem.
2. `NEW_FAILURES` tem de ser medido, não assumido.
3. **System Map:** se tocares em ficheiro que pertence ao mapa, regenera pela cadeia
   canónica — `git add` dos ficheiros novos ANTES de correr a cadeia, depois `git add`
   do gerado, depois commit. O handoff avisa que a regeneração é necessária do lado de
   cá depois de integrar o Atlas.
4. Se o mapa reprovar, separa `CONTENT_DRIFT` de `PROVENANCE_DRIFT` (o segundo é só o
   nome da branch no `state.generated.json` e cura-se regenerando já nesta bancada).
5. `SYSTEM_MAP_CHECK` esperado `PASS`. Se falhar, separa NEW de PREEXISTING e **reporta
   a falha** — não corrijas código só para o mapa ficar verde.

---

## 7 · KNOW-HOW

Se registares secção nova em `SINTONIA-EAME-KNOW-HOW.md`, mede o `§N` livre em **todas
as lanes abertas**, não só nesta — lanes paralelas nascem do mesmo trunk e escolhem o
mesmo número. Varre as branches candidatas com
`git show <branch>:SINTONIA-EAME-KNOW-HOW.md | grep -o "^# §[0-9]*"`.
Saltar um número é grátis; dois §N diferentes com o mesmo endereço não.

Declara `KNOW_HOW_DELTA` no fecho, mesmo que seja `NENHUM`.

---

## 8 · BLOCO DE ENTREGA (obrigatório, valores medidos)

```
INITIAL_HEAD =            FINAL_HEAD =            REMOTE_HEAD =
SOURCE_CURATOR_HEAD_USED =
MODEL_EFFECTIVE =

HTML_READY_INPUT            = 18
HTML_SOURCES_INTEGRATED     =
HTML_CONTRACTS_INTEGRATED   =
ATLAS_FICHAS_INTEGRADAS     =        (e quais, e porquê esse critério)

YOUTUBE_BLOCKED_PRESERVED   = 50
YOUTUBE_READY_INTEGRATED    = 0
DUPLICATE_SOURCE_IDS_CREATED= 0

TESTS_RUN / PASSED / FAILED / SKIPPED =
NEW_FAILURES =                       (comparados por NOME contra o baseline de 370ce450)
BASELINE_FAILURES =
SYSTEM_MAP_CHECK =
KNOW_HOW_DELTA =

WORKTREE =      PUSH_STATE =      LOCAL==REMOTE =
NETWORK_REQUESTS =     PAID_USD =
```

Fecha também com uma secção **EM LINGUAGEM SIMPLES**, sem jargão, respondendo:

1. quantas fontes novas entraram;
2. quantos contratos foram integrados;
3. quantas YouTube ficaram conscientemente de fora;
4. porque ficaram de fora;
5. se o sistema está pronto para uma nova Big Collection com essas 18.

---

## 9 · REGRAS DE CONDUTA

- **Só tu escreves nesta bancada.** Auxiliares fazem leitura, auditoria e red team.
- Não edites `main` nem qualquer outra branch. Trabalha só em `curator-04a-integration`.
- Não corras Big Collection, não colhas, não toques em Admission nem na Sala.
- Defeito que encontrares fora do escopo: **documenta** (`BLOCKER`, `OWNER`,
  `MINIMUM_FIX`) e **não corrijas**. Ampliar escopo é decisão do dono.
- `NÃO SEI` é resultado válido e obrigatório quando é o caso. Ausência de prova não vira
  zero, não, sucesso nem inexistência.
- Se um gate falhar, reporta a falha. **Nunca corrijas silenciosamente para obter PASS.**
- Commit e push no fim. Verifica `LOCAL == REMOTE` por `git rev-parse` após novo
  `fetch` — a saída do `push` é relato, o `rev-parse` é prova.

---

## 10 · HARD STOP

Quando as 18 estiverem integradas, provadas e publicadas:

```
NEXT_BIG_COLLECTION_ELIGIBLE_NEW_SOURCES = 18
```

**PARA AQUI.** Não corras a Big Collection. Integração autorizada não autoriza a
execução seguinte. Entrega ao dono e espera.
