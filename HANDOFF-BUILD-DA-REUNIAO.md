# HANDOFF · BUILD DA REUNIÃO — onde parou, e o que falta

> Para colar como primeira mensagem numa conta Claude nova.
> **Não confie em nada daqui sem medir.** Cada número tem um comando ao lado.

```
REPOSITÓRIO   lucianodalondon-sys/eame-sintonia
BRANCH        claude/meeting-portal-final-pabok2
HEAD          f95b157
ESTADO        PARCIAL — as duas contradições estão FECHADAS, gates verdes,
              browser verificado. FALTA: deploy real e MEETING_FREEZE.
```

---

## 0 · O QUE ESTA SESSÃO DESCOBRIU PRIMEIRO, E QUE MUDA A LEITURA DO HANDOFF ANTERIOR

A versão anterior deste arquivo dizia `HEAD a15ac4e · portal ainda NÃO integrado`.
Isso estava certo **para o que havia no git**. Mas a mensagem que abriu esta
sessão listava muito mais trabalho como já feito: dicionário IT/EN, hero, seções
WHY COMMERCIAL / WHY NOW / WINDOW / ACTION MAP, render no navegador real.

**Esse trabalho nunca foi empurrado.** Medido:

```bash
git fetch --all --prune
for b in $(git branch -r --format='%(refname:short)'); do
  git ls-tree -r --name-only "$b" | grep -q meeting-labels && echo "HIT: $b"
done            # nenhum hit em nenhuma branch
git log --oneline HEAD --not --remotes   # vazio: nada por empurrar
git stash list; git worktree list        # vazios
```

`a54e287` era o commit mais novo de todo o repositório. O contêiner da conta
anterior levou consigo o que não foi commitado.

    O QUE NÃO ATRAVESSA O `git push` NÃO EXISTE PARA A CONTA SEGUINTE.

Esta sessão **não recomeçou do zero**: partiu de `a54e287`, preservou a casca
visual `a14b9e1` inteira e o snapshot já emitido, e refez apenas a camada de UI
que se tinha perdido. Nenhum commit de outra sessão foi apagado, nenhum
force-push foi feito, nenhuma branch foi resetada.

---

## 1 · OS TRÊS HEADs

| papel | branch | HEAD | o que é |
|---|---|---|---|
| **inteligência canônica** | `claude/opportunity-commercial-priority-v1` | `b3935bd` | o motor, os 43 casos, a catraca |
| **base visual (congelada)** | `claude/site-v21-ingest-recovery` | `a14b9e1` | BrandWell PASS, mobile PASS. **NÃO REDESENHAR** |
| **build da reunião (anterior)** | `claude/meeting-intelligence-integration` | `a54e287` | intacta, não tocada por esta sessão |
| **build da reunião (esta)** | `claude/meeting-portal-final-pabok2` | `f95b157` | criada de `a54e287` |

```bash
git merge-base --is-ancestor a14b9e1 HEAD && echo "a casca visual esta inteira"
git merge-base --is-ancestor a54e287 HEAD && echo "o trabalho anterior esta preservado"
```

⚠️ **A branch de deploy mudou de nome.** O briefing pedia deploy de
`claude/meeting-intelligence-integration`; esta conta foi instruída a
desenvolver em `claude/meeting-portal-final-pabok2`. As duas contêm o mesmo
trabalho — a segunda é descendente da primeira. Quem retomar decide qual publica.

---

## 2 · RECONSTRUIR O PACOTE — a sequência exata, e ela não é adivinhável

`build/ITALY-REALITY-HANDOFF-V2.1/` é **ignorado pelo git**. Ele é reconstruído,
e é construído numa branch e consumido noutra.

    O PACOTE SOBREVIVE AO `git checkout` PORQUE É IGNORADO.
    É ISSO QUE PERMITE CONSTRUIR NA CANÔNICA E LER NA VISUAL.

```bash
# 1 · construir na inteligência canônica  (~13s)
git checkout claude/opportunity-commercial-priority-v1     # b3935bd
bash scripts/v21_cadeia.sh
python3 -c "import json;d=json.load(open('build/ITALY-REALITY-HANDOFF-V2.1/DESIGN-INGEST/OPPORTUNITIES.json'));print(d['BUILD_ID'],len(d['RECORDS']))"
# esperado: V21-358954754db5ea2f 43

# 2 · voltar para a branch da reunião — o pacote continua lá
git checkout claude/meeting-portal-final-pabok2

# 3 · reescrever a camada de dados do portal a partir do pacote
python3 scripts/site_v21_ingest.py          # italia-portale/client/italy-handoff-v21.js

# 4 · emitir o snapshot, declarando o HEAD da INTELIGÊNCIA
python3 scripts/meeting_snapshot.py --source-head b3935bd --cutoff 2026-09-04T00:52:54Z

# 5 · reescrever o dicionário IT/EN
python3 scripts/meeting_labels.py
```

⚠️ `--source-head` é obrigatório e validado. `git rev-parse HEAD` na branch da
reunião devolveria a casca visual, e o snapshot declararia procedência falsa.

**Convergência provada nesta sessão:** duas execuções independentes da cadeia,
com o diretório de saída apagado entre elas, produziram `BUILD_ID` idêntico e
`OPPORTUNITIES.json` byte a byte igual (ignorando `GENERATED_AT`). 0 violações
de contrato nas duas.

---

## 3 · AS DUAS CONTRADIÇÕES — o que eram, onde viviam, como foram fechadas

### 3.1 · O PRODUTO PRINCIPAL — **FECHADA**

Havia **três** coroações independentes, não duas:

| onde | linha | o que fazia |
|---|---|---|
| a scheda | `const primary = c.primary \|\| (verified[0] …)` | primeiro `VERIFIED_LABEL_MATCH` **em ordem de array** |
| o detalhe | `csProds.find(p => p.verdict === 'VERIFIED_LABEL_MATCH')` | primeiro verificado de uma lista construída **noutro sítio** |
| o detalhe, ripiego | `primaryLabel: … : csProductRows[0]` | **o primeiro produto qualquer** — nem sequer verificado |

Testemunha (botrite × vite × Emilia-Romagna, `OPP_5F31A63F844D`):
a scheda coroava **AGHARTA**, o motor diz **BANJO**, e o portfólio mostrava
**três** produtos onde `PORTFOLIO_MATCHES` declara **um**.

    A ORDEM DE UM ARRAY NÃO É UMA REGRA.

**Dono único agora:** `PRIMARY_MATCH`. Quando o motor não elege — 26 casos em 43,
com `PRIMARY_MATCH_REASON = SEM_REGRA_DEFENSAVEL_PARA_ESCOLHER` — **nenhuma** das
duas superfícies inventa: mostram-se todos os matches, em pé de igualdade.
`data-product` na scheda fica **vazio** nesses casos: é a casa de um NOME, e
«1 prodotti collegati» não é o nome de um produto.

### 3.2 · A JANELA — **FECHADA**

Havia **três** donos paralelos:

| onde | o que lia |
|---|---|
| o dome | `csWinRec` (fixture de calendário) e `WINDOW_START`/`WINDOW_END` |
| o herói, «COSA MANCA ANCORA» | a mesma ausência de datas → escrevia «Nessuna finestra dichiarata» |
| a linha alta do herói | `wsLabel — weLabel` → imprimia `— — —` |

As datas são **nulas em 43 casos de 43**. O ecrã dizia «não há janela» enquanto
o motor já declarava tipo, regra e estado — a regra existe em **16 de 43**.

    NÃO SE ESCONDE A CONTRADIÇÃO COM CSS: RETIRA-SE O CÁLCULO ANTIGO
    DO PAPEL QUE JÁ NÃO LHE PERTENCE.

Os três blocos continuam **visualmente onde estavam** e passaram a consumir
`WINDOW_DEFINED` / `WINDOW_OPEN_NOW` / `WINDOW_TYPE` / `WINDOW_RULE_STATE`.

⚠️ **`WINDOW_DEFINED` e `WINDOW_OPEN_NOW` continuam separados.** 16 casos têm
regra; só **2** têm a condição verificada agora. Fundi-los substituiria uma
contradição por outra.

---

## 4 · O QUE ESTA SESSÃO CONSTRUIU

```
scripts/meeting_labels.py                       gerador do dicionário
italia-portale/client/meeting-labels.js         IT+EN, 299 entradas, 49 famílias
italia-portale/audit/meeting-gate.mjs           22 testemunhas
```

E alterou:

```
scripts/meeting_snapshot.py        filtro recursivo + corte de referências internas
italia-portale/client/italy-app-model.js        o join canônico (o.engine) + AM.MEETING
italia-portale/client/portale.html              os três donos, e as seções novas
italia-portale/client/italy-handoff-v21.js      regerado de b3935bd (37 → 43)
italia-portale/audit/lib/harness.mjs            carrega a camada da reunião
italia-portale/audit/checks.mjs                 números de contrato → b3935bd
italia-portale/audit/opportunity-hub.mjs        OD6/OR1 mudam de interlocutor
italia-portale/audit/action-map-consistency.mjs AC0/AC4/AC5-8/AC12 idem
```

### 4.1 · O vazamento aninhado — **FECHADO**

A lista de permissão do snapshot olhava só a **primeira camada**: `r[c] = o[c]`
copiava o contentor inteiro. Sete campos permitidos são dicionários e listas, e
tudo o que lá vivia atravessava sem nunca ser julgado.

`ACTION_BY_DEPARTMENT.<dept>.NEXT_TRIGGER` — prosa de pesquisa em português —
chegava a **215 blocos de 215**.

    UMA LISTA DE PERMISSÃO QUE SÓ OLHA A PRIMEIRA CAMADA
    NÃO É UMA LISTA DE PERMISSÃO: É UMA PORTA ENTREABERTA.

Agora a permissão desce até à folha (`dict → dict → list → dict → folha`).
`NEXT_TRIGGER` não perde nada: **medido**, é `DEPENDENCY` dito em português —
185/185 em `SINAL_ATUAL`, 20/20 em `JANELA_ABERTA_AGORA`, 10/10 nos nulos.

Também saíram: `BRIEF_TEMPLATES` (frases-molde em português, substituídas por
`BRIEF_CODES`) e as referências internas dentro de `WHY_COMMERCIAL_IT/_EN` —
11 frases terminavam em «— vedi NEED_DIRECTION e la frase originale in
NEED_EXCERPT». Corta-se a subordinada, a principal fica intacta, e os nomes
cortados viajam em `__REFERS_TO_FIELDS` para o auditor ver que o reenvio existia.

```bash
# testemunha de profundidade: 0 prosa abaixo do nível 1
node italia-portale/audit/meeting-gate.mjs --json | python3 -c "
import json,sys;d=json.load(sys.stdin)
print([r['id'] for r in d['results'] if not r['pass']] or 'todos verdes')"
```

### 4.2 · Três defeitos que só os gates existentes viram

1. **`WHY_NOW_CHAIN.<elo>.FACT` é um campo MISTO** — data em `SINAL_ATUAL`,
   código do motor nos outros três. Imprimi-lo tal e qual pôs
   `ESTADIO_DECLARADO_NO_MESMO_DOCUMENTO` num ecrã italiano: 44 ocorrências.
2. **Contraste** — branco sobre o verde AGIRE ORA mede 2,57:1; e o tinteiro que
   `AREA_UI` declara para Market Development (`#7BE0A6`) foi pensado para a
   **superfície** do departamento, não para fundo neutro, onde sai da paleta.
   `UM INCHIOSTRO E VALIDO SU UN FONDO, NON IN ASSOLUTO.`
3. **O banco de provas carregava menos do que a página** — `harness.mjs` não
   listava `meeting-intelligence-snapshot.js`, logo `o.engine` era `null` nos 43
   e todos os gates mediam o portal de ontem. E `mkOpp` — a **projeção** que
   constrói o objeto das schedas — não nomeava `engine`, por isso a correção
   estava escrita e **não chegava ao ecrã que devia corrigir**.

---

## 5 · GATES — estado medido

| gate | resultado |
|---|---|
| `audit/run.mjs` | **69/71** (baseline desta missão: 66/71) |
| `audit/meeting-gate.mjs` | **22/22** |
| `brandwell` | **5/5** — BW1 BW2 BW3 TY1 TY2 |
| `internal-token` | **6/6** · 0 no lugar de etiqueta, 0 na prosa, IT e EN |
| `mobile` | **15/15** — MB1…MB8 + a jornada J1…J7 a 390px |
| `opportunity-hub` | **8/8** · JANELA REAL 5, correctamente ligada 5 (era 0/0) |
| `action-map-consistency` | **14/14** |
| `rtv-gate` | **11/11** |
| `pdf-gate` | **9/9** |
| `link-asset` | **6/6** |
| `future-ruler` | **3/3** |
| `acceptance` | **READY FOR CANONICAL HANDOFF V2.1 = YES** |
| `cta-navigation` | **PASS** · 995 clicáveis · 873 julgados · 873 vivos · **0 mortos** · 0 console errors · 0 pedidos falhados |

⚠️ **Dois gates precisavam de dependências que não estavam instaladas**, e por
isso morriam no `import` — um `exit=1` que parecia falha de ambiente e escondia
defeitos reais. `pdf-gate` e `rtv-gate` precisam de `pdfjs-dist`; todos os de
browser precisam de `playwright-core`. Instalar **os dois de uma vez**, porque
`npm i --no-save` poda o que não está no comando:

```bash
npm i --no-save --no-audit --no-fund playwright-core@1.55.0 pdfjs-dist
```

    UM PORTAO QUE MORRE NO IMPORT NAO ESTA A VIGIAR NADA,
    E O SEU VERMELHO PARECE-SE COM O DE UM AMBIENTE MAL POSTO.

Assim que correu, `pdf-gate` encontrou duas fugas verdadeiras no PDF que vai
para a mão de um cliente — a ficha de campo do revendedor: «Stato attuale
ACT_NOW.» e uma frase que nomeava `SOURCE_IDS`. Ambas viviam em
`italy-briefs.js`, ficheiro que esta missão não tinha tocado.

**Os dois que continuam vermelhos já estavam vermelhos antes desta missão** e
não lhe pertencem:

- `B3` — `vendor/jspdf-2.5.2.umd.min.js:86` cita um URL cdnjs **dentro de um
  comentário** do próprio ficheiro. Não é uma dependência de runtime.
- `DS1` — o interruptor de cenários demonstrativos não muda contagem nenhuma, e
  o próprio check declara-se vacuoso.

### Números de contrato — actualizados, não afrouxados

    V21-99226fbb90dcdbc2   37 · 9 verificadas · 28 a validar · 17 despromovidas
    V21-358954754db5ea2f   43 · 33 verificadas · 10 a validar · 4 despromovidas

    UM NÚMERO DE CONTRATO ACTUALIZA-SE QUANDO O CONTRATO MUDA,
    E NUNCA QUANDO A MEDIDA DESILUDE.

`H3`, `W2` e `O1` passaram de FAIL para PASS. Nenhum check passou de PASS a FAIL.

---

## 6 · O SNAPSHOT — números medidos

```
SOURCE_HEAD     b3935bd
BUILD_ID        V21-358954754db5ea2f
MEETING_CUTOFF  2026-09-04T00:52:54Z
TOTAL_CASES     43

STATUS                  WATCH 22 · TO_VALIDATE 9 · FUTURE_PREPARATION 7
                        VALIDATE_NOW 3 · ACT_NOW 2
COMMERCIAL_PRIORITY     TO_VALIDATE 17 · COMMERCIAL_WATCH 13
                        STRATEGIC_OPPORTUNITY 8 · SALES_READY 5
PUBLICATION_STATE       VALIDATION_REQUIRED 38 · PUBLISHABLE 5
WINDOW_DEFINED          NO 27 · YES 16
WINDOW_OPEN_NOW         UNKNOWN 41 · YES 2 · NO 0
WINDOW_RULE_STATE       NOT_DECLARED 26 · DECLARED 15
                        DELEGATED_TO_FARM 1 · ADMINISTRATIVE_ONLY 1
PRIMARY_MATCH           presente 17 · ausente 26
ACTION_STATE (215)      NO_ACTION 116 · VALIDATE 47 · WATCH 42 · ACT 7 · PREPARE 3
```

⚠️ **Contagens só dos 43.** `D.CASES` — os ~21 casos de apresentação escritos à
mão — continuam onde estavam e **não entram em nenhuma contagem canônica**.
`AM.MEETING` conta os casos, não declara números.

---

## 7 · A ORDEM DO RADAR — uma correção que ninguém tinha pedido

O radar ordena «publicáveis primeiro» desde o dia em que alguém mediu que as
nove convergências caíam nas posições 2, 5, 15, 17, 18, 19, 23, 29 e 35. A regra
estava certa e **a chave envelheceu**: `convergence` distinguia 9 em 37, distingue
33 em 43, e já não discrimina.

Medido: **três dos cinco** casos `PUBLICATION_STATE = PUBLISHABLE` caíam atrás
de «VEDI TUTTE 43».

    PUBLICADO E ATRÁS DE UM BOTÃO NÃO É PUBLICADO.

A primeira chave passou a ser o veredito de publicação. Nenhum caso promovido,
escondido ou reclassificado; as contagens continuam 43 / 5 / 38.

---

## 8 · OS CASOS TESTEMUNHA — verificados no navegador real

| | caso | `OPPORTUNITY_ID` | verificado no ecrã |
|---|---|---|---|
| **A** | botrite × vite × Emilia-Romagna | `OPP_5F31A63F844D` | `ACT_NOW` · regra pré-colheita · **Aperta ora** · BANJO como principal · PUBLISHABLE |
| **B** | botrite × vite × Toscana | `OPP_F8106D5E1767` | `ACT_NOW` sustentado |
| **C** | tignoletta × vite × Umbria | `OPP_169BD86DB324` | `WATCH` · cadeia com elos que **não** fecham |
| **D** | carpocapsa × macieira × Veneto | `OPP_75C37DED9160` | `STAGE_ENDED` **e** `CONTINUE_RECOMMENDED` na mesma tela, sem se confundirem |
| **F** | scafoideo × vite × Toscana | `OPP_D11664591168` | **«Obbligo amministrativo — non è una finestra agronomica»** · `OPEN_NOW=UNKNOWN` como «Stato attuale non ancora misurato» |

**`RULE_DELEGATED_TO_FARM` existe em 1 caso de 43** — e é o **mesmo**
`OPP_75C37DED9160` da carpocapsa. Verificado no navegador, nas duas línguas e
nas duas larguras: «La decisione dipende dall'osservazione in campo» /
«The decision depends on farm-level observation». Sem token interno, e não
apresentado como erro.

**Thresholds (§14 do briefing):** este build **não publica percentagem nenhuma**
— `THRESHOLD_STATE` só toma `NOT_APPLICABLE` e `NOT_DECLARED`. Os 5% de
Emilia-Romagna não podem aparecer na Umbria porque nenhum número de limiar chega
a qualquer ecrã. A Umbria mostra `WATCH`, que é o que o motor sustenta.

---

## 9 · EVIDÊNCIA NEGATIVA — o que o motor **não** publica

O briefing pede um caso com `WEAKENS` e um com `CLOSES`/`CONTRADICTS`.

**Medido: este build do motor não emite esses papéis.** O vocabulário real de
`EVIDENCE_ROLES` é: `SUPPORTS_SIGNAL`, `SUPPORTS_WINDOW`, `SUPPORTS_DIRECTION`,
`SUPPORTS_PRODUCT_MATCH`, `SUPPORTS_COMMERCIAL_ACTION`,
`SUPPORTS_REGIONAL_CONTEXT`, `BACKGROUND_ONLY`.

    UM PAPEL QUE O MOTOR NÃO EMITE NÃO SE INVENTA NA TELA.

A inteligência negativa **existe e aparece**, noutros campos que o motor emite
mesmo: `NEED_DIRECTION = NO_ACTION_RECOMMENDED / ACTION_SUSPENDED /
TREATMENT_PROHIBITED / WINDOW_CONCLUDED`, `ACTION_RECOMMENDATION_STATE =
NOT_NEEDED_DECLARED / PROHIBITED_DECLARED / SUSPEND_RECOMMENDED /
CONCLUDED_DECLARED`, `WHY_COMMERCIAL_CODES = NEED_CLOSED / NEED_NOT_POSITIVE`.
`BACKGROUND_ONLY` também é mostrado, e não filtrado.

Os três tokens (`WEAKENS`, `CLOSES`, `CONTRADICTS`) já estão traduzidos em IT+EN
no dicionário: se o motor os emitir, a tela lê-os sem alteração nenhuma.

---

## 10 · O QUE FALTA — na ordem

1. **Deploy real** da branch `claude/meeting-portal-final-pabok2`, directório
   `italia-portale/client/`.

   ⚠️ **Esta sessão não conseguiu fazê-lo, e não o contornou.** O `vercel` CLI
   não está instalado, não há `VERCEL_TOKEN` no ambiente, não há `.vercel/` no
   repositório nem credencial em `~/.vercel/`. Quem retomar precisa de um token
   Vercel com acesso ao projeto:

   ```bash
   cd italia-portale/client && vercel --prod
   # preset Other · build command: nenhum · output directory: .
   ```

       UM DEPLOY QUE NAO SE PODE FAZER DECLARA-SE, NAO SE SIMULA.

2. **Não declarar READY porque o deploy devolveu sucesso** — abrir o domínio
   servido, comparar com o ficheiro local, e registar `DEPLOY_URL`,
   `PORTAL_HEAD`, `INTELLIGENCE_SOURCE_HEAD`, `SNAPSHOT_BUILD_ID`.
3. **`MEETING_FREEZE = YES`** só depois disso.

---

## 11 · O QUE NÃO SE FAZ

```
NOVA COLETA = NÃO          PORTAL VISUAL: NÃO REDESENHAR
THRESHOLDS = NÃO ALTERAR   SEGUNDO MOTOR = NÃO CRIAR
PRODUÇÃO = NÃO TOCAR       MERGE EM MAIN = NÃO
FORCE-PUSH = NÃO           RESET DE BRANCH ALHEIA = NÃO
```

O portal **não recalcula** `STATUS`, `COMMERCIAL_PRIORITY`, `WHY_NOW`,
`WINDOW_DEFINED`, `WINDOW_OPEN_NOW`, `WINDOW_TYPE`, product match, evidence role,
action map nem `PUBLICATION_STATE`. **Ele só apresenta.**

Fica para depois da reunião, por BACKFILL: os casos que dependem de medição no
pomar · arroz × giavone · os 16 registos sem coleção · ISTAT 2026 · a política
`AREA_OFICIAL_ANO` (`DECISION_REQUIRED`, e **nenhum** dos 43 usa área hoje).

`PUBLISHABLE 5 / VALIDATION_REQUIRED 38` **não** vira «mostrar 5 e esconder 38».
Mostram-se todos, e o estado fica visível em cada um.

---

## 12 · ARMADILHAS QUE VÃO CUSTAR TEMPO

1. **`c.canonical` já significava «janela canônica do fixture».** O join do motor
   chama-se `o.engine` **por isso**. Duas coisas diferentes com o mesmo nome são
   um bug à espera.
2. **`mkOpp` é uma PROJEÇÃO.** Constrói o objeto das schedas campo a campo. O que
   ela não nomear **não chega ao ecrã**, por muito correto que esteja o modelo.
3. **`audit/lib/harness.mjs` tem a sua própria lista de ficheiros.** Se a página
   carregar um script novo e o harness não, os gates medem outra página.
4. **Há DUAS cópias do portal.** `italia-portale/client/` é a **servida** —
   provado por `audit/lib/drive.mjs`, que serve exatamente essa pasta, e pelo
   `vercel.json` + `.vercelignore` que só lá existem. `BASELINE/` é referência
   (o seu `italy-app-model.js` tem 20 KB e nem sequer lê o V2.1; o servido tem
   283 KB). **O handoff anterior mediu o `BASELINE/` e concluiu que o radar era
   alimentado por `D.CASES` — isso é verdade no BASELINE e falso no servido.**
5. **O radar abre em 12 schedas** e oferece «VEDI TUTTE 43». Um gate que só olhe
   as 12 diz PASS sobre um portal que perdeu 31. `clickText` do drive não abre
   esse botão (sobe para um ancestral que não trata o clique) — clicar no `span`
   folha directamente.
6. **Os gates de browser precisam de dois pacotes que não estão no
   `package.json`**, e sem eles morrem no `import` com um `exit=1` que se
   confunde com falha de ambiente:
   `npm i --no-save --no-audit --no-fund playwright-core@1.55.0 pdfjs-dist`.
   **Os dois no mesmo comando** — `--no-save` poda o que não estiver lá.
   Não foram acrescentados às dependências de propósito: o deploy Vercel
   instalaria ~50 MB que o site não usa. Chromium está em
   `/opt/pw-browsers/chromium-1194`. **Nunca** correr `playwright install`.
7. **`italy-briefs.js` também é uma superfície de cliente.** Gera o PDF da ficha
   de campo do revendedor, e o que lá se escreve não passa pelos templates do
   `portale.html` — as duas fugas de token que `pdf-gate` encontrou viviam lá.

---

## 13 · A ENTREGA

```
MEETING_PORTAL_READY        = PARTIAL (falta deploy verificado)
BRANCH                      = claude/meeting-portal-final-pabok2
HEAD_INICIAL                = a54e287
HEAD_FINAL                  = f95b157
INTELLIGENCE_SOURCE_HEAD    = b3935bd
VISUAL_BASE_HEAD            = a14b9e1
MEETING_CUTOFF              = 2026-09-04T00:52:54Z
SNAPSHOT_BUILD_ID           = V21-358954754db5ea2f
TOTAL_CANONICAL_CASES       = 43

PRIMARY_PRODUCT_CONTRADICTION = CLOSED
WINDOW_CONTRADICTION          = CLOSED

PUBLISHABLE 5 · VALIDATION_REQUIRED 38
ACT_NOW 2 · VALIDATE_NOW 3 · WATCH 22 · TO_VALIDATE 9 · FUTURE_PREPARATION 7
WINDOW_DEFINED 16 · OPEN_NOW YES 2 · NO 0 · UNKNOWN 41

IT = PASS      EN = PASS      DESKTOP = PASS      MOBILE = PASS
BRANDWELL = PASS   INTERNAL_TOKEN = PASS   CTA = PASS (0 mortos)
DEPLOY_URL = NAO FEITO — sem credencial Vercel nesta sessao

WORK_RESTARTED_FROM_ZERO   = NO
FRONTEND_INVENTED_PRIMARY  = NO
FRONTEND_RECALCULATED_WINDOW = NO
PARTIAL_INPUT_CONSUMED     = NO
NEW_COLLECTION_STARTED     = NO
THRESHOLDS_CHANGED         = NO
SECOND_ENGINE_CREATED      = NO
VISUAL_REDESIGN            = NO
RAW_EVIDENCE_CHANGED       = NO
FORCE_PUSH                 = NO
MEETING_FREEZE             = NO   ← só depois do deploy verificado
```

**Estado honesto:** as duas contradições estão fechadas e provadas por um gate
que **reprova a versão anterior** — corrido contra o ecrã e o modelo de
`a54e287`, falha 15 dos 22 testemunhos, e nomeia as duas contradições palavra
por palavra («the hero says «no window» while WINDOW_DEFINED=YES», «AGHARTA is
presented as portfolio and is not in PORTFOLIO_MATCHES»).

    UM TESTE QUE NÃO PARTE O BUG ANTIGO NÃO É TESTEMUNHA SUFICIENTE.

O portal consome o snapshot. Falta publicá-lo e olhar para o que foi servido.
