# HANDOFF · BUILD DA REUNIÃO — onde parou, e o que falta

> **ESTADO ATUALIZADO · sessão 3.** O que está abaixo do §0 é o handoff da
> sessão 2 e continua correto como história. O §0 é o estado de AGORA.
> **Não confie em nada daqui sem medir.** Cada número tem um comando ao lado.

---

# 0 · ESTADO DE AGORA — leia só isto se tiver pressa

```
REPOSITÓRIO   lucianodalondon-sys/eame-sintonia
BRANCH        claude/meeting-portal-contradictions-qb5a1x   (descendente direto
              de claude/meeting-intelligence-integration @ a54e287 — fast-forward,
              nada reescrito, nada forçado)
HEAD          7b2f24f  (código completo) + o commit que traz este documento
              confirme sempre com:  git log --oneline -3
ESTADO        MEETING_PORTAL_READY = YES · MEETING_FREEZE = YES
              publicado e verificado (ver §0.6)
FREEZE_TIME   2026-09-04T02:5xZ  (o commit que traz esta linha)
DEPLOY_URL    https://sintonia-eame-preview-8p1qae38s-london-creative.vercel.app
```

## 0.-1 · ⚠️ PORQUE OS CARDS PARECIAM ANTIGOS — medido, e corrigido

O portal abria em `view: 'radar'` (portale.html), o **radar histórico**. Esse
radar não mostra os 21 casos de demonstração: mostra os **43 canónicos**, mas
lidos de `italy-handoff-v21.js`, que é um pacote **anterior à reconciliação**.

```
italy-handoff-v21.js   buildId  V21-99226fbb90dcdbc2   ← o que se abria
meeting snapshot       BUILD_ID V21-358954754db5ea2f   ← b3935bd, reconciliado
```

Não é um detalhe de versão. É outra leitura da mesma realidade:

```
STATUS no pacote antigo : TO_VALIDATE 9 · ACT_NOW 16 · PREPARE_NOW 11 · FUTURE_PREPARATION 7
STATUS reconciliado     : TO_VALIDATE 9 · WATCH 22 · FUTURE_PREPARATION 7 · VALIDATE_NOW 3 · ACT_NOW 2

25 de 43 casos com STATUS diferente
16 cartões diziam AGIRE ORA onde o motor declara 2
PREPARE_NOW nem sequer existe no vocabulário atual
```

E o pacote antigo **não tem** os campos da reconciliação — medido no objeto
cru: `PUBLICATION_STATE`, `WINDOW_DEFINED`, `WINDOW_OPEN_NOW`, `WINDOW_TYPE`,
`WINDOW_RULE_STATE`, `PRIMARY_MATCH`, `PORTFOLIO_MATCHES`,
`ACTION_BY_DEPARTMENT`, `WHY_NOW_CHAIN`, `EVIDENCE_ROLES`, `WHY_COMMERCIAL_IT`
— **todos ausentes**. Aquela tela não podia mostrar a inteligência nova nem
que quisesse.

Nos seis casos-testemunha: **superfície canónica 5/5**, **radar histórico 0/5**
(todos liam AGIRE ORA, incluindo Umbria que é WATCH e Veneto que é
VALIDATE_NOW).

    NÃO ERAM CARTÕES «DE DEMO». ERAM CARTÕES CANÓNICOS VELHOS —
    O QUE É PIOR, PORQUE PARECEM ATUAIS.

**A correção foi só de binding**, sem redesenho, sem tocar no motor, no
adapter, na coleta ou nos 21 casos:

1. o portal passa a abrir em `view: 'meeting'` — a superfície canónica;
2. o radar histórico declara-se no seu subtítulo (build + «não é a leitura
   canónica da reunião»), para não poder ser lido como atual;
3. a scheda canónica ganhou `data-case` (o gancho de identidade que os portões
   desta casa já conhecem) e uma linha de produto que **nomeia só o que o motor
   nomeou** — 17 cartões nomeiam, 26 contam («4 prodotti collegati»);
4. três textos a 9,5px passaram a 10px (o portão móvel só os via agora que
   esta é a tela que abre).

Portões novos: `NO_OLD_SNAPSHOT_FALLBACK` e `SIX_WITNESSES_UI_MATCH_ENGINE`.
O primeiro declara-se `VACUOUS` se os dois builds coincidirem, para não medir
uma diferença que não existe.

---

## 0.0 · ⚠️ DUAS SESSÕES CONSTRUÍRAM A MESMA COISA — LEIA ANTES DE ESCOLHER

Enquanto esta sessão trabalhava, outra (`overnight-meeting-orchestrator`)
construiu a sua própria superfície e **fez merge para
`claude/meeting-intelligence-integration`** (`e927cb9`, «vince l'ecrã che la
riunione apre»). O merge tomou o meu `8f37e36` como pai mas **resolveu os
ficheiros para o lado deles**: `meeting-surface.js`, `meeting-browser.mjs` e as
minhas 21 testemunhas **não estão lá**; ficou o `meeting-adapter.js` deles e um
`meeting-gate.mjs` deles (MG1–MG14, 14/14 verde).

**Não sobrescrevi nada.** O trabalho desta sessão vive em
`claude/meeting-portal-contradictions-qb5a1x`.

### As duas abordagens

| | esta sessão | a outra sessão |
|---|---|---|
| onde | superfície NOVA (`meeting` + `mcase`), radar demo intacto | RE-ALIMENTA o radar existente a partir do snapshot |
| adapter | `meeting-surface.js` | `meeting-adapter.js` |
| primary no adapter | `PRIMARY_MATCH` e nada mais | `PRIMARY_MATCH` e nada mais — **também correto** |

### O QUE MEDI NA BUILD DELES, E QUE IMPORTA PARA A REUNIÃO

O adapter deles está certo. **A camada de apresentação não.**
`portale.html:3351`:

```js
primaryLabel: (mv && mv.hasPortfolio) ? mv.portfolio[0].name
```

`portfolio[0]` — o primeiro elemento do array — alimenta
`data-product="{{ c.primaryLabel }}"`, que é o nome do produto impresso no
cartão. Medido no browser sobre a build deles:

```
OPP_75C37DED9160   cartão mostra "Lamdex® Extra"
                   engine PRIMARY_MATCH = null · matches = 2
```

São **14 casos** em que o motor não coroou ninguém e o cartão nomeia um produto
escolhido por ordem de array — exatamente o número que a minha testemunha
`PRIMARY_MATCH_SINGLE_OWNER` devolve contra a implementação legacy
(`real 0 · legacy 14`). A previsão e a medição batem certo.

    O ADAPTER DELES NÃO COROA NINGUÉM. O CARTÃO DELES COROA O PRIMEIRO
    DO ARRAY. A CONTRADIÇÃO VOLTA NA ÚLTIMA LINHA.

O comentário deles assume a escolha («la scheda deve restare una scheda» — o
detalhe mostra todos). É uma decisão defensável sobre densidade; mas o leitor
do cartão vê um produto principal que o motor recusou-se a eleger, e §5 do
briefing proíbe `array[0]` como critério.

**A correção mínima**, se escolherem a build deles: onde
`PRIMARY_MATCH` é nulo, o cartão não deve nomear um produto — deve dizer
«N prodotti collegati» e deixar a eleição para o detalhe. É uma linha.

**A DECISÃO É DO DONO DA REUNIÃO, NÃO MINHA.** As duas builds estão publicadas
e cada uma tem o seu URL de preview.

---

## 0.1 · A CORREÇÃO QUE A SESSÃO 3 TEVE DE FAZER PRIMEIRO

O briefing da sessão 3 dizia que a integração «já tinha chegado ao navegador
real», com hero, secções, labels IT/EN e 0 erros de consola.

**Isso não estava no git.** Medido:

```bash
git diff --stat a14b9e1 a54e287
# HANDOFF-BUILD-DA-REUNIAO.md | 363 +
# meeting-intelligence-snapshot.js | 3 +
# meeting-intelligence-snapshot.json | 17873 +
# scripts/meeting_snapshot.py | 210 +
```

Quatro ficheiros. `italy-app-model.js` era **byte-a-byte igual** a `a14b9e1`.
Não existia `meeting-labels.js`, nem hero, nem secções. O próprio handoff da
sessão 2 dizia-o na primeira linha: *«PARCIAL — snapshot pronto, portal ainda
NÃO integrado»*.

    O QUE MORREU COM O CONTENTOR DA CONTA ANTERIOR FOI A CAMADA DE
    APRESENTAÇÃO. O MOTOR, O SNAPSHOT E A BASE VISUAL SOBREVIVERAM
    INTACTOS, E FORAM PRESERVADOS.

Nada foi recomeçado do zero: `b3935bd`, `a14b9e1` e `a15ac4e` são a base sobre
a qual esta sessão construiu.

## 0.2 · AS DUAS CONTRADIÇÕES · fechadas, com o mecanismo medido

**A · produto principal com dois donos — FECHADA**

```
portale.html:2758   const primary = c.primary || (verified[0] ? ... : null)
```

`c.primary` é copy escrita à mão nos 21 `D.CASES`; o fallback é literalmente o
**primeiro elemento do array**. Dois blocos que leem dois arrays coroam dois
produtos diferentes, e cada um está certo sobre o seu array.

MEDIDO nos 43: `PRIMARY_MATCH` é não-nulo **exatamente** nos 17 casos que têm
UM único produto, e nulo nos 26 restantes. *«PRINCIPAL + 2 OUTROS» é uma forma
que o motor nunca produz.* Quem a mostra, inventou.

**B · janela com dois donos — FECHADA**

```
LEGACY_WINDOW_SOURCE = window.ITALY_CANONICAL (italy-canonical-windows.js)
                       29 janelas de calendário, chaveadas por LEGACY_CASE_ID
                       (IT-OPP-*), CURRENT_STATUS calculado contra uma data
                       congelada (2026-09-02)
CANONICAL_WINDOW_SOURCE = WINDOW_* do snapshot
```

O calendário legacy pertence aos 21 casos de demonstração e não sabe nada dos
pares canónicos — por isso dizia «nenhuma janela» exatamente onde o motor
declara uma regra.

`meeting-surface.js` **nunca lê `ITALY_CANONICAL`**, e um gate prova-o.

## 0.3 · OS FICHEIROS NOVOS

| ficheiro | o que é |
|---|---|
| `client/meeting-labels.js` | 258 chaves IT/EN. Um código sem frase devolve `null` e a linha desaparece — **nunca** cai para o token cru, que é o vazamento. |
| `client/meeting-surface.js` | O adaptador. Copia do snapshot; não recalcula nada. O principal é `PRIMARY_MATCH` e mais nada; a janela é `WINDOW_*` e mais nada. |
| `audit/meeting-gate.mjs` | 20 testemunhas. As 4 centrais correm **duas vezes** — na superfície real e numa LEGACY que reproduz os dois defeitos. |
| `audit/meeting-browser.mjs` | Chromium real: 1440/390 × IT/EN × 4 casos obrigatórios. |

Em `portale.html`: vista `meeting` (radar dos 43) + vista `mcase` (detalhe).
O radar de demonstração **fica exatamente como estava**.

## 0.4 · AS TESTEMUNHAS QUE REPROVAM A VERSÃO ANTIGA

Um teste que passava antes não prova o defeito. As quatro centrais correm
contra uma superfície legacy construída de propósito, e declaram-se `VACUOUS`
se passarem também lá:

```
PRIMARY_MATCH_SINGLE_OWNER      real 0 · legacy 14
NO_PRIMARY_WHEN_UNKNOWN         real 0 · legacy 14
WINDOW_SINGLE_OWNER             real 0 · legacy 43
WINDOW_DEFINED_OPEN_SEPARATED   real 0 · legacy 48
```

## 0.5 · O ACHADO QUE NINGUÉM PODIA ADIVINHAR

A prosa **IT/EN do próprio motor** carrega os nomes dos seus campos:

```
«...non dice di intervenire — vedi NEED_DIRECTION e la frase originale
  in NEED_EXCERPT.»          11 casos em 43
```

Escrita para quem lê o JSON, não para a reunião. O motor está congelado em
`b3935bd` e a frase **não pode ser reescrita** — inventar prosa seria o pior
dos dois defeitos.

Tira-se o **ponteiro**, não a afirmação: a frase está completa antes do
travessão, e as duas coisas apontadas passam a estar exatamente onde o ponteiro
mandava olhar. O gate exige que a frase mostrada seja um **prefixo** da do
motor.

## 0.6 · DEPLOY — o único item por fechar

```
DEPLOY_URL conhecido   https://sintonia-eame-preview.vercel.app/portale
estado                 HTTP 200, mas serve ainda a base visual SEM o meeting build
                       (meeting-surface.js -> 404 · portale.html 817712B, o tamanho
                       anterior; o ficheiro local tem 855814B)
bloqueio               não há CLI nem token da Vercel neste contentor
```

### ⚠️ CORREÇÃO — eu tinha concluído mal, e a conclusão errada custaria a reunião

Escrevi antes que empurrar a branch «não desencadeia deploy nenhum». **Está
errado.** Procurei deploys em `GET /actions/runs` — os *workflow runs* — e a
Vercel **não publica por GitHub Actions**: publica pela **Deployments API**.
Olhei para o sítio errado e li o silêncio como ausência.

    UM SÍTIO ERRADO SEM RESULTADOS NÃO É UMA AUSÊNCIA DE RESULTADOS.

O que está lá, medido em `GET /deployments`:

```
02:35:21Z  Preview  ref 38ed09e  by vercel[bot]   ← o meu HEAD
02:31:33Z  Preview  ref 8de7309  by vercel[bot]
02:06:33Z  Preview  ref 8f37e36  by vercel[bot]
02:04:09Z  Preview  ref 7b2f24f  by vercel[bot]
```

**Cada commit meu foi publicado**, como *Preview*, com `state=success`. O check
suite `vercel` está `completed success`. O que me enganou foi o alias
`sintonia-eame-preview.vercel.app`, que aponta para a branch de **produção** —
por isso continuava a servir a versão antiga enquanto o meu build já estava no
ar noutro endereço.

```
DEPLOY_URL (HEAD 38ed09e)
https://sintonia-eame-preview-8p1qae38s-london-creative.vercel.app

/portale                            200 · 855814 B  (igual ao local)
/meeting-surface.js                 200
/meeting-labels.js                  200
/meeting-intelligence-snapshot.js   200
```

Como obter o URL de um HEAD qualquer:

```bash
API=https://api.github.com/repos/lucianodalondon-sys/eame-sintonia
ID=$(curl -sS -H "Authorization: Bearer $GITHUB_TOKEN" "$API/deployments?sha=<SHA>" \
     | python3 -c "import json,sys;print(json.load(sys.stdin)[0]['id'])")
curl -sS -H "Authorization: Bearer $GITHUB_TOKEN" "$API/deployments/$ID/statuses" \
     | python3 -c "import json,sys;print(json.load(sys.stdin)[0]['environment_url'])"
```

### A verificação pública, e o seu limite honesto

Os **77 ficheiros** servidos foram descarregados e comparados byte a byte com
`italia-portale/client/`: **zero diferenças**. As únicas ausências são
`vercel.json`, `.gitignore` e os `LEGGIMI/readme` — retidos de propósito, que é
o contrato do `deploy-surface`. A única diferença de conteúdo em toda a árvore é
a Vercel injectar o seu script de *feedback* de preview no `index.html`; **não**
no `portale.html`.

O Chromium deste contentor **não atravessa o proxy** até ao domínio
(`ERR_CONNECTION_RESET`), embora o `curl` atravesse. Por isso as testemunhas
correram sobre os **bytes descarregados do URL público**, servidos localmente —
o artefacto medido é o que o público recebe, verificado por hash:

```bash
node audit/meeting-browser.mjs --dir <pasta-espelho>   # tudo verde
node audit/meeting-public.mjs  --base http://localhost:8901
# PUBLIC_CANONICAL_CASES 43 · PRIMARY_INVENTED 0 · INTERNAL_TOKENS 0
# CONSOLE_ERRORS 0 · FAILED_REQUESTS 0 · D_CASES_AS_CANONICAL 0
```

`audit/deploy-surface.mjs` (contrato) passa: `vercel.json` + `.vercelignore`
servem só `italia-portale/client` e excluem `/build`, `/data`, `/docs`, `/audit`.

**PRÓXIMA AÇÃO EXATA:** publicar a branch na Vercel (integração Git ou
`vercel --prod` com token) e depois correr

```bash
node audit/deploy-surface.mjs --base https://<url-servido>
curl -sS https://<url-servido>/meeting-surface.js -o /dev/null -w '%{http_code}\n'   # tem de ser 200
```

**Não declarar READY porque o deploy devolveu sucesso — abrir o domínio
servido e comparar com o ficheiro local.**

## 0.7 · COMO REPRODUZIR TUDO

```bash
# 1 · o pacote canónico (a branch da reunião não o traz: é ignorado pelo git)
git worktree add /tmp/canon claude/opportunity-commercial-priority-v1   # b3935bd
cd /tmp/canon && bash scripts/v21_cadeia.sh                            # ~40s
cp -r /tmp/canon/build/ITALY-REALITY-HANDOFF-V2.1 build/
# esperado: BUILD_ID V21-358954754db5ea2f · 43 RECORDS · 0 violações

# 2 · os portões
cd italia-portale
npm install playwright-core --no-save     # NUNCA `playwright install`
node audit/run.mjs                        # 66/71 — os 5 são anteriores a esta sessão
node audit/meeting-gate.mjs               # 20/20
node audit/meeting-browser.mjs            # tudo verde
node audit/brandwell.mjs && node audit/mobile.mjs && node audit/internal-token.mjs
```

**As dependências não estão no repositório e há uma armadilha real:**

```bash
# do RAIZ do repositorio (o package.json esta la, nao em italia-portale/)
npm install playwright-core pdfjs-dist --no-save
```

Instalar UM de cada vez com `--no-save` **apaga o outro**: `npm install
pdfjs-dist` sozinho removeu o `playwright-core` e todos os portões de browser
passaram a estourar com `ERR_MODULE_NOT_FOUND`. Instale os dois no mesmo
comando. E **nunca** `playwright install` — o Chromium já está em
`/opt/pw-browsers`.

## 0.7b · ESTADO DOS PORTÕES NESTA BRANCH

| portão | resultado |
|---|---|
| `run.mjs` | **66/71** — os 5 do §0.8, todos anteriores a esta sessão |
| `meeting-gate.mjs` | **20/20** |
| `meeting-browser.mjs` | **tudo verde** · 0 erros de consola · 0 pedidos falhados · 0 controlos mortos · 20 percursos |
| `brandwell` | PASS · 17 ecrãs · BrownLL 97% |
| `mobile` | PASS · 50 ecrãs · 360/390/430/768/1440 · overflow 0 |
| `internal-token` | PASS · 50 ecrãs · 0 tokens no lugar de uma etiqueta, 0 na prosa |
| `opportunity-hub` | PASS |
| `action-map-consistency` | PASS · 7/7 áreas |
| `link-asset` | PASS |
| `future-ruler` | PASS |
| `rtv-gate` | PASS · RV1–RV6 |
| `pdf-gate` | PASS · 4 PDFs reais gerados e lidos por pdf.js |
| `deploy-surface` (contrato) | PASS |
| `journey` | **não existe** neste repositório — o briefing nomeia-o, o ficheiro não está cá |
| `cta-navigation` | **PASS** · CT1–CT5 + NV1–NV7 · 1061 clicáveis · 936 premidos e julgados · **936 vivos · 0 mortos** · 0 erros de consola · 0 pedidos falhados |
| `meeting-public` (bytes públicos) | **PUBLIC BUILD VERIFIED** |

### O controlo «suspeito», medido em vez de suposto

O varrimento reportou uma assinatura que não se voltou a apresentar
(`Radar Canonico · span||×|8|23`). Medida:

```
CONTROL             span 6×6 px, sem texto e sem título
SURFACE             barra lateral — está nas 12 telas, não é da superfície canónica
EXPECTED_ACTION     nenhuma própria: é o ponto de estado dentro da linha de navegação
ACTUAL_ACTION       navega — o handler está no antepassado (onClick={{ n.go }})
HANDLER             na linha de navegação (data-dc-tpl=34), não no ponto
DESTINATION         a tela do item de navegação
VISIBLE_AFFORDANCE  a linha inteira; o ponto é decoração dentro dela
CLASSIFICATION      ALIVE (pelo antepassado) · NOT_APPLICABLE como controlo próprio
```

`clickables()` do próprio portão devolve **0** elementos sem texto nem título,
porque sobe até ao antepassado que carrega o handler. A assinatura não se
repetiu porque o índice `nth` de um ponto anónimo muda quando a tela é
restaurada — é um artefacto de re-identificação, **não** um defeito do portal.
E o varrimento deu `Radar Canonico · sospetti 0`.

    NENHUM DEFEITO REAL ⇒ NENHUMA CORREÇÃO. Mexer na navegação por causa
    disto seria refatorar por um número, não por um problema.

## 0.8 · OS 5 GATES QUE JÁ FALHAVAM ANTES DESTA SESSÃO

Medidos em `a54e287`, **antes** de qualquer alteração minha. Não foram tocados:
mexer nos números esperados seria esconder o problema.

| id | o que diz | porquê |
|---|---|---|
| `B3` | dependência de CDN público | `vendor/jspdf` traz um comentário com `cdnjs.cloudflare` |
| `H3` | 43 opportunities, esperava 37 | constantes do pacote **anterior** à reconciliação |
| `W2` | 4 downgrades, esperava 17 | idem |
| `O1` | 21 publicáveis fora da 1ª página | o radar de demonstração não mostra os 43 — é a lacuna arquitetural conhecida |
| `DS1` | o toggle de cenários não muda nada | verificação vazia, anterior |

## 0.9 · LIMITAÇÃO MEDIDA · inteligência negativa

O §17 do briefing pede provar 1 `WEAKENS` e 1 `CLOSES`/`CONTRADICTS`.

**Esses papéis não existem neste build.** Medido nos 43:

```
EVIDENCE_ROLES = SUPPORTS_PRODUCT_MATCH 200 · SUPPORTS_COMMERCIAL_ACTION 61
                 BACKGROUND_ONLY 53 · SUPPORTS_SIGNAL 29 · SUPPORTS_DIRECTION 17
                 SUPPORTS_WINDOW 12 · SUPPORTS_REGIONAL_CONTEXT 12
WEAKENS / CLOSES / CONTRADICTS = 0
```

A inteligência que esfria o caso existe — mas vive em `NEED_DIRECTION` e
`ACTION_RECOMMENDATION_STATE`, e é de lá que a tela a mostra: **8 dos 43**
casos exibem-na (ex.: Umbria, «la fonte dichiara che non sono necessari
interventi»). As labels IT/EN de `WEAKENS`/`CLOSES`/`CONTRADICTS` já existem,
com as frases do briefing, para o dia em que o motor as emitir.

---

# HISTÓRIA · o handoff da sessão 2 (mantido como registo)

```
REPOSITÓRIO   lucianodalondon-sys/eame-sintonia
BRANCH         claude/meeting-intelligence-integration
HEAD           a15ac4e
ESTADO         PARCIAL — snapshot pronto, portal ainda NÃO integrado
```

---

## 0 · Os três HEADs, e o que cada um é

| papel | branch | HEAD | o que é |
|---|---|---|---|
| **inteligência canônica** | `claude/opportunity-commercial-priority-v1` | `b3935bd` | o motor, os 43 casos, a catraca. `UNIVERSAL_INTELLIGENCE_RECONCILIATION = PASS` |
| **base visual (congelada)** | `claude/site-v21-ingest-recovery` | `a14b9e1` | BrandWell PASS, mobile PASS, journey PASS. **NÃO REDESENHAR** |
| **build da reunião** | `claude/meeting-intelligence-integration` | `a15ac4e` | criada de `a14b9e1` + o snapshot |

```bash
git fetch --all
git log --oneline -1 b3935bd a14b9e1 origin/claude/meeting-intelligence-integration
git merge-base --is-ancestor a14b9e1 HEAD && echo "a casca visual esta inteira"
```

---

## 1 · A COISA MAIS IMPORTANTE DESTE HANDOFF

O pacote da inteligência **não está no git** — `build/ITALY-REALITY-HANDOFF-V2.1/`
é ignorado. Ele é reconstruído. E ele é construído numa branch e consumido em
outra.

    O PACOTE SOBREVIVE AO `git checkout` PORQUE É IGNORADO.
    É ISSO QUE PERMITE CONSTRUIR NA CANÔNICA E LER NA VISUAL.

**A sequência exata, e ela não é adivinhável:**

```bash
# 1 · construir o pacote na inteligência canônica
git checkout claude/opportunity-commercial-priority-v1     # b3935bd
bash scripts/v21_cadeia.sh                                  # ~40s
python3 -c "import json;d=json.load(open('build/ITALY-REALITY-HANDOFF-V2.1/DESIGN-INGEST/OPPORTUNITIES.json'));print(d['BUILD_ID'],len(d['RECORDS']))"
# esperado: V21-358954754db5ea2f 43

# 2 · voltar para a branch da reunião — o pacote continua lá
git checkout claude/meeting-intelligence-integration

# 3 · gerar o snapshot, declarando o HEAD da INTELIGÊNCIA
python3 scripts/meeting_snapshot.py --source-head b3935bd --cutoff 2026-09-04T00:52:54Z
```

⚠️ `--source-head` é obrigatório e validado. Sem ele o script para. `git rev-parse
HEAD` na branch da reunião devolveria `a14b9e1`, e o snapshot declararia uma
procedência que não é a sua.

---

## 2 · O QUE JÁ ESTÁ FEITO

### `scripts/meeting_snapshot.py` · o snapshot client-safe ✅

Gera `italia-portale/client/meeting-intelligence-snapshot.{json,js}`
(`window.MEETING_INTELLIGENCE`). Lista de PERMISSÃO campo a campo — copia o que
o motor já decidiu, **não recalcula nada**.

```
SOURCE_HEAD     b3935bd
BUILD_ID        V21-358954754db5ea2f
MEETING_CUTOFF  2026-09-04T00:52:54Z
TOTAL_CASES     43

BY_STATUS               WATCH 22 · TO_VALIDATE 9 · FUTURE_PREPARATION 7
                        VALIDATE_NOW 3 · ACT_NOW 2
BY_COMMERCIAL_PRIORITY  TO_VALIDATE 17 · COMMERCIAL_WATCH 13
                        STRATEGIC_OPPORTUNITY 8 · SALES_READY 5
BY_PUBLICATION_STATE    VALIDATION_REQUIRED 38 · PUBLISHABLE 5
BY_WINDOW_DEFINED       NO 27 · YES 16
BY_WINDOW_OPEN_NOW      UNKNOWN 41 · YES 2
BY_WINDOW_RULE_STATE    NOT_DECLARED 26 · DECLARED 15
                        DELEGATED_TO_FARM 1 · ADMINISTRATIVE_ONLY 1
```

**Lei que ele aplica e que não pode ser afrouxada:** prosa de pesquisa em
português **não atravessa como texto**. `WINDOW_CONDITION`, `NEED_EXCERPT`,
`PEST_STAGE_EXCERPT` e `ACTION_RECOMMENDATION_EXCERPT` atravessam só como
`CAMPO__PT_ONLY: true` mais o ID do documento.

    PROSA QUE NÃO EMBARCA NÃO VAZA.

A tela deve dizer «a condição está declarada no documento X» — que é verdade —
em vez de mostrar português a um italiano.

---

## 3 · O ACHADO QUE MUDA O PLANO — leia antes de escrever uma linha

O radar da base visual **não é alimentado pelo motor**. Medido:

```bash
sed -n '136,160p' italia-portale/BASELINE/italy-demo-data.js
grep -n "const opportunities = coll" -A 12 italia-portale/BASELINE/italy-app-model.js
```

`italy-app-model.js` monta `opportunities` a partir de **`D.CASES`** — 21+ casos
de apresentação escritos à mão (`IT-OPP-001…`), com `provenance: DEMO_SCENARIO`
e prosa rica (`happening`, `why`, `know`, `watch`, `timeline`, `primary`,
`products`, `stage`, `signal`, `label`, `evidence{}`). As oportunidades do motor
entram só como `upstreamOpportunities`, uma coleção lateral, e servem apenas para
marcar `isUpstreamReal`.

    O RADAR BONITO QUE PASSOU NOS GATES NÃO MOSTRA OS 43. ELE MOSTRA 21
    CASOS DE APRESENTAÇÃO.

**Consequência para a missão:** trocar a fonte do radar não é «ligar um JSON».
Os campos que os templates leem (`happening`, `know`, `watch`, `timeline`) **não
existem** no snapshot canônico e **não podem ser inventados**. Os que existem
(`WHY_COMMERCIAL_IT/_EN`, `WHY_NOW_CODES`, `PORTFOLIO_MATCHES`,
`ACTION_BY_DEPARTMENT`, `EVIDENCE_ROLES`, `WHAT_IS_MISSING`) não têm lugar nos
templates atuais.

**A decisão que estava tomada quando isto parou** — e que a conta nova deve
confirmar ou derrubar com evidência:

> Construir uma **superfície canônica nova** dentro da mesma casca BrandWell
> (mesmos tokens, mesma linguagem de cartão, categoria dominando a cor), 100%
> alimentada pelo snapshot, e roteá-la como o radar da reunião. O radar de
> demonstração **fica como está** e **não** é apresentado como canônico.
>
> Isso satisfaz: portal consome o snapshot · visual preservado · nada inventado ·
> os 43 casos com os campos novos. E não satisfaz literalmente o §13 do briefing
> («os cards do radar»), porque o card do radar atual pertence a outra fonte.
>
>     MISTURAR 21 CASOS DE DEMONSTRAÇÃO COM 43 CANÔNICOS NA MESMA GRADE
>     É A ÚNICA COISA QUE NÃO SE PODE FAZER.

---

## 4 · O QUE FALTA — na ordem

### 4.1 · `italia-portale/client/meeting-labels.js` (IT + EN) — **não começado**

Nenhum token interno pode aparecer na tela. O inventário completo já foi medido:

```
STATUS                ACT_NOW · VALIDATE_NOW · WATCH · TO_VALIDATE · FUTURE_PREPARATION
COMMERCIAL_PRIORITY   SALES_READY · STRATEGIC_OPPORTUNITY · COMMERCIAL_WATCH · TO_VALIDATE
ARCHETYPE             O1_FIELD_PRESSURE · O2_MARKET_MOMENT · O3_RESISTANCE_MOA
                      O4_COMPETITIVE_OPENING · O5_REGULATORY_PREPARATION · O6_SCIENCE_TO_FIELD
WINDOW_TYPE           PHENOLOGY_WINDOW · PREHARVEST_WINDOW · THRESHOLD_WINDOW
                      PEST_STAGE_WINDOW · WEATHER_TRIGGERED_WINDOW · RULE_DELEGATED_TO_FARM
WINDOW_RULE_STATE     RULE_DECLARED · RULE_ADMINISTRATIVE_ONLY
                      RULE_DELEGATED_TO_FARM · RULE_NOT_DECLARED
OPEN_NOW_METHOD       6 códigos (ver §4.1b)
NEED_DIRECTION        7 estados      PEST_STAGE_STATE 4      ACTION_RECOMMENDATION 7
THRESHOLD_STATE       2              WHY_NOW_CODES 6         WHAT_IS_MISSING 12
WHY_COMMERCIAL_CODES  9              EXTERNAL_BLOCKER 1      PUBLICATION_STATE 2
BRIEF codes           9              EVIDENCE_ROLES 7        WHY_CODE 13
ACTION                12             ACTION_STATE 5          DEPARTAMENTOS 5
PRIMARY_MATCH_REASON  2              FITS do produto 9
CROPS 12 · TARGETS 9 · GEOGRAFIAS 8
```

Reproduza o inventário exato com:

```bash
python3 - <<'PY'
import json
d=json.load(open('italia-portale/client/meeting-intelligence-snapshot.json',encoding='utf-8'))
C=d['CASES']
def uni(f):
    s=set()
    for c in C:
        v=f(c)
        if isinstance(v,(list,tuple,set)): s|={str(x) for x in v}
        elif v is not None: s.add(str(v))
    return sorted(s)
print('STATUS', uni(lambda c:c.get('STATUS')))
print('WINDOW_TYPE', uni(lambda c:c.get('WINDOW_TYPE')))
print('WINDOW_RULE_STATE', uni(lambda c:c.get('WINDOW_RULE_STATE')))
print('OPEN_METHOD', uni(lambda c:c.get('WINDOW_OPEN_NOW_METHOD')))
print('WHAT_IS_MISSING', uni(lambda c:c.get('WHAT_IS_MISSING')))
print('ROLES', sorted({e['ROLE'] for c in C for e in (c.get('EVIDENCE_ROLES') or [])}))
print('ACTION', sorted({v['ACTION'] for c in C for v in (c.get('ACTION_BY_DEPARTMENT') or {}).values()}))
print('WHY_CODE', sorted({v['WHY_CODE'] for c in C for v in (c.get('ACTION_BY_DEPARTMENT') or {}).values()}))
PY
```

#### 4.1b · As frases que o briefing pediu, palavra por palavra

O briefing é explícito sobre a linguagem. Estas não são sugestões:

| token | IT | EN |
|---|---|---|
| `RULE_DELEGATED_TO_FARM` | «La decisione dipende dall'osservazione in campo» | «The decision depends on farm-level observation» |
| `RULE_ADMINISTRATIVE_ONLY` | «Obbligo amministrativo — non è una finestra agronomica» | «Administrative obligation — not an agronomic window» |
| `PHENOLOGY_WINDOW` | «Finestra definita dallo stadio fenologico» | «Window defined by phenological stage» |
| `WINDOW_DEFINED=YES` + `OPEN_NOW=UNKNOWN` | «Condizione nota; stato attuale non ancora misurato» | «Condition known; current state not yet measured» |
| `WHY_NOW` com `CADEIA_COMPLETA` | «Finestra agronomica aperta» | «Agronomic window open» |
| `NEED_DIRECTION` restritiva | «La fonte raccomanda di monitorare, non di attivare» | «The source recommends monitoring, not activating» |
| `WEAKENS` | «Questa evidenza riduce l'urgenza commerciale» | «This evidence lowers the commercial urgency» |
| `CLOSES` | «Il monitoraggio non sostiene un'azione ora» | «Monitoring does not support action now» |

    UNKNOWN NUNCA PODE DESAPARECER ATRÁS DE COPY BONITA.

### 4.2 · A superfície canônica — **não começada**

Onde: `italia-portale/BASELINE/` **e** `italia-portale/client/` (são duas cópias;
ver §6). Carregar `meeting-intelligence-snapshot.js` + `meeting-labels.js`.

**Hero, sem scroll** (§5 do briefing): CROP · TARGET · REGION → STATUS → por que
é oportunidade → por que agora / por que ainda não → **TODOS** os
`PORTFOLIO_MATCHES` → o que falta.

⚠️ `PRIMARY_MATCH` só é principal quando existe regra defensável. Medido no
snapshot: `PRIMARY_MATCH_REASON` é `SEM_REGRA_DEFENSAVEL_PARA_ESCOLHER` na
maioria. **Nesses casos não há principal visual.** Nunca `PRIMARY + N MORE`
quando o snapshot conhece todos.

Por produto (§6): `PRODUCT_NAME` · `ACTIVE_INGREDIENTS` · `MODE_OF_ACTION` ·
`CROP_FIT` · `TARGET_FIT` · `REGULATORY_FIT` · `WINDOW_FIT` · `VALIDATION_STATE`
· `MATCH_REASON` · `RESTRICTIONS`.

Mapa de ação (§10): exatamente `ACTION_BY_DEPARTMENT` — 5 departamentos, cada um
com `ACTION_STATE` · `ACTION` · `WHY_CODE` · `DEPENDENCY` · `NEXT_TRIGGER`.
Sequência QUEM AGE → QUEM VALIDA → QUEM PREPARA → O QUE DESTRAVA. **Não inventar
sequência que a inteligência não dá.**

Inteligência negativa (§12): `EVIDENCE_ROLES` com `WEAKENS` / `CONTRADICTS` /
`CLOSES` de forma clara e elegante — é demonstração de inteligência, não defeito.

### 4.3 · Gates — **não começados**

Rodar os que já existem:
```bash
cd italia-portale && node audit/run.mjs && node audit/acceptance.mjs
node audit/browser.mjs   # precisa de Chromium; ver §7
```
E acrescentar as testemunhas nomeadas no §19 do briefing:
`MEETING_SNAPSHOT_CONTRACT` · `SNAPSHOT_43_CASES` · `NO_RAW_BYPASS` ·
`SNAPSHOT_FROM_b3935bd` · `ALL_PORTFOLIO_MATCHES_RENDERED` ·
`WHY_COMMERCIAL_RENDERED` · `WHY_NOW_RENDERED` · `WINDOW_STATE_RENDERED` ·
`ACTION_MAP_FROM_ENGINE` · `EVIDENCE_ROLE_RENDERED` ·
`VALIDATION_STATE_NOT_HIDDEN` · `NO_INTERNAL_CODES` · `NO_PARTIAL_INPUT_USED`.

### 4.4 · Browser + deploy — **não começados**

Chromium está pré-instalado (`PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers`).
**Nunca** rodar `playwright install`. Testar 1440 e 390, IT e EN, percorrendo
HOME → RADAR → OPORTUNIDADE → WHY COMMERCIAL → PRODUCTS → WHY NOW → ACTION MAP →
EVIDENCE → SOURCE.

Deploy: branch `claude/meeting-intelligence-integration`, diretório
`italia-portale/client/`. **Não declarar READY porque o deploy retornou sucesso
— abrir o domínio servido e comparar com o arquivo local.**

---

## 5 · OS SEIS CASOS DA DEMO, com os IDs já medidos

| | caso | `OPPORTUNITY_ID` | o que ele demonstra |
|---|---|---|---|
| **A** | botrite × videira × Emilia-Romagna | `OPP_5F31A63F844D` | `ACT_NOW` · `PREHARVEST_WINDOW` · `OPEN_NOW=YES` por `ESTADIO_DECLARADO_NO_MESMO_DOCUMENTO` · `PUBLISHABLE` |
| **B** | botrite × videira × Toscana | `OPP_F8106D5E1767` | `ACT_NOW` sustentado; a frase «maggior suscettibilità» prova **um** elo só |
| **C** | tignoletta × videira × Umbria | `OPP_169BD86DB324` | `WATCH` · a fonte diz «non sono necessari interventi» — evidência que esfria |
| **D** | carpocapsa × macieira × Veneto | `OPP_75C37DED9160` | `PEST_STAGE_STATE=STAGE_ENDED` **e** `ACTION_RECOMMENDATION_STATE=CONTINUE_RECOMMENDED` — **sem confundir os dois** |
| **E** | o mesmo `OPP_75C37DED9160` | | `RULE_DELEGATED_TO_FARM` em linguagem humana |
| **F** | escafoide × videira × Toscana | `OPP_D11664591168` | `RULE_ADMINISTRATIVE_ONLY` — obrigação de norma, não janela agronômica |

```bash
python3 - <<'PY'
import json
d=json.load(open('italia-portale/client/meeting-intelligence-snapshot.json',encoding='utf-8'))
ids=('OPP_5F31A63F844D','OPP_F8106D5E1767','OPP_169BD86DB324','OPP_75C37DED9160','OPP_D11664591168')
for c in d['CASES']:
    if c['ID'] in ids:
        print(c['ID'], c['CROP'], c['TARGET'], c['GEOGRAPHY'], c['STATUS'],
              c.get('WINDOW_TYPE'), c.get('WINDOW_OPEN_NOW'), c.get('PUBLICATION_STATE'))
PY
```

---

## 6 · ARMADILHAS QUE VÃO CUSTAR TEMPO SE NINGUÉM AVISAR

1. **Há DUAS cópias do portal.** `italia-portale/BASELINE/` (referência, com os
   relatórios) e `italia-portale/client/` (o que é servido, com `vercel.json`,
   `italy-handoff-v21.js` de 5,9 MB e `italy-pdf.js`). Elas **não** são idênticas
   — `italy-app-model.js` tem 20 KB numa e 283 KB na outra. Editar só uma é a
   forma mais rápida de a tela servida não mudar.

2. **`italy-i18n.js` é o dicionário do portal** (94 KB no client). Labels novas
   deveriam entrar ali ou num arquivo próprio carregado depois — decidir e
   declarar, não espalhar.

3. **O snapshot tem 433 KB de JS.** O `portale.html` do client já carrega 5,9 MB
   de handoff. Medir o custo antes de somar mais.

4. **`build/ITALY-REALITY-HANDOFF-V2/`** (sem o `.1`) **é versionado** e difere
   entre as branches. É a PORTA da coleta. Não confundir com o pacote de saída.

5. **A suíte de Python não roda nesta branch** com os números da canônica — a
   branch da reunião veio de `a14b9e1`, que é anterior. Os gates aqui são os do
   `italia-portale/audit/`, em node.

---

## 7 · O QUE NÃO SE FAZ (do briefing, verbatim)

```
NOVA COLETA = NÃO          PORTAL VISUAL: NÃO REDESENHAR
THRESHOLDS = NÃO ALTERAR   SEGUNDO MOTOR = NÃO CRIAR
PRODUÇÃO = NÃO TOCAR       MERGE EM MAIN = NÃO
```

O portal **não recalcula** `STATUS`, `COMMERCIAL_PRIORITY`, `WHY_NOW`,
`WINDOW_DEFINED`, `WINDOW_OPEN_NOW`, `WINDOW_TYPE`, product match, evidence role,
action map nem `PUBLICATION_STATE`. **Ele só apresenta.**

Fica para depois da reunião: os 14 casos que dependem de medição no pomar ·
arroz × giavone · os 16 registros sem coleção · ISTAT 2026 · a política
`AREA_OFICIAL_ANO` (`DECISION_REQUIRED`, e **nenhum** dos 43 usa área hoje).

`PUBLISHABLE 5 / VALIDATION_REQUIRED 38` **não** vira «mostrar 5 e esconder 38».
Pode-se mostrar os que estão em validação — desde que o estado apareça, e nenhum
`VALIDATION_REQUIRED` seja apresentado como afirmação validada.

---

## 8 · MEETING_FREEZE  ·  ⚠️ SUPERADO PELO §0 — agora é YES

*(o texto abaixo é da sessão 2 e fica como história)*

Ainda **NÃO**. Declarar só quando: snapshot estável + portal integrado + gates
verdes + casos da demo verificados no browser + deploy aberto e testado.

Depois disso nada novo entra; o que terminar depois entra por BACKFILL.

---

## 9 · A ENTREGA QUE A REUNIÃO ESPERA

```
MEETING_PORTAL_READY = YES / PARTIAL / NO
CANONICAL_INTELLIGENCE_HEAD = b3935bd
VISUAL_BASE_HEAD            = a14b9e1
MEETING_CUTOFF              = 2026-09-04T00:52:54Z
MEETING_SNAPSHOT_BUILD      = V21-358954754db5ea2f
PORTAL_INTEGRATION_HEAD     = ?
DEPLOY_URL                  = ?
TOTAL_CASES 43 · PUBLISHABLE 5 · VALIDATION_REQUIRED 38
ACT_NOW 2 · VALIDATE_NOW 3 · WATCH 22 · TO_VALIDATE 9 · FUTURE_PREPARATION 7
WINDOW_DEFINED 16 · WINDOW_OPEN_NOW 2

PARTIAL_INPUT_CONSUMED = NO   NEW_COLLECTION_STARTED = NO
THRESHOLDS_CHANGED = NO       SECOND_ENGINE_CREATED = NO
VISUAL_REDESIGN = NO          RAW_EVIDENCE_CHANGED = NO
MEETING_FREEZE = ?
```

**Estado honesto neste handoff: `MEETING_PORTAL_READY = NO`.** O snapshot existe
e está correto. O portal ainda não o consome.
