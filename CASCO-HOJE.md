# CASCO-HOJE — o mínimo honesto vai ao ar (D114 · D97)

```text
MISSAO    CASCO-HOJE-MINIMO-HONESTO · D114 (portal no ar hoje) · D97 (o casco so mostra o que o pote aprovou)
          pesquisa do LAB 27/09 PESQUISA-CRUZAMENTOS F.1 (citada pela missao; nao lida aqui)
RAMO      claude/casco-publication-minimum-5q7kbw  (base: claude/casco-r7-publication-yb7nsg @ 60ee56b2)
MERGES    origin/claude/organize-collection-system-japwor @ 0484e2dd  -> bcc7a61c
          origin/claude/single-reference-gateway-hhhj7t @ c551062b    -> 633ebff9
POTE      docs/casco/r7/POTE-R7.json · corrida IR-e09acab6365032523d6e · 25 objetos distintos (47 lugares em gavetas)
PORTA     motor/porta_da_referencia.py · registro PROD_FTS_6_20260831 (31/08) · ultima checagem 07/09 · PODE_ESTAR_DESATUALIZADO
```

## 1 · Os dois merges, e cada conflito

**japwor** (auditoria D97, aviso SHA/CRLF, Label Intelligence como produto de ferramenta): 12 conflitos, **todos em
ficheiros gerados do mapa** — resolvidos com a versão desta branch e regerados pela cadeia no fim.

**hhhj7t** (porta única: EDICAO / ULTIMA_CHECAGEM / ESTADO_FRESCOR). ⚠️ Não é um ramo pequeno: é a **linha de serviço
inteira** (`servico-20260923-0923` + 46), separada desta linha desde `1c99a48b` (09/09) — 2456 commits. Nenhuma
dependência da porta (`motor/porta_da_referencia.py`, `fontes/adama_referencia.py`, `motor/cruzamentos_max.py`,
`referencia/adama/*`) existia aqui, por isso só um merge real a trazia. 42 conflitos, resolvidos assim
(o commit do merge lista-os um a um):

| conflito | escolha | porquê |
|---|---|---|
| infra do mapa (workflow `system-map.yml`, `generate_system_map.py`, `censo_*`, `impressao_da_arvore.py`, `system-map/app/*` e cópia servida) | THEIRS | diff linha a linha: do nosso lado só comentários e versões antigas do mesmo código; os passos do workflow deles são superconjunto dos nossos |
| `CADEIA-DO-MAPA.json` | THEIRS em 15 hunks, OURS no último | o filtro do censo de sensores com as 7 gavetas que o código realmente varre (`censo_cards_sensores.py:281`) |
| `architecture.declared.json` | THEIRS, e depois **repostas peça a peça** pela P9 | `C-CI-RELEASE`, publicador, leitura, publicado, testes do pote |
| gerados / derivados / observados | THEIRS → regerados pela cadeia | nenhum gerado vale por merge |
| `italia-portale/client/portale.html` | OURS inteiro | o casco que vai ao ar é o desta linha; as vistas `#sala`/`#painel` da linha de serviço **não entram** (D97: o casco não lê a Sala) — os ficheiros delas chegam, nada os referencia |
| `audit/run.mjs`, `barras-de-busca.mjs`, `etichette-gate.mjs` | OURS | PP1 e o ajuste D114 `semPotePublicado` |
| `.gitattributes`, `.gitignore`, `client/.gitignore`, `client/.vercelignore`, `provas/o_forward_conta_se.py` | UNIÃO | acrescentos dos dois lados |
| `handoff/SYSTEM-MAP-SM-P1R.md` | OURS | secção do preview e nota dos números |

Efeito colateral declarado: o gerador do pote (`pacote/pote_intelligence_casco.py`) passou a estar no ramo (vive na
linha de serviço). Continua **fora do que é servido** (`outputDirectory = italia-portale/client`).

## 2 · O que aparece em cada tela — antes × depois

Antes = base `60ee56b2` (o que a missão CASCO-AO-AR-R7 deixou pronto). Depois = esta branch. Números medidos no
sandbox dos testes (o mesmo casco montado), e conferidos no Chromium (PP1).

| tela | antes | depois |
|---|---|---|
| **Portafoglio** | 2 objetos do pote + **os 86 cruzamentos** na tela (80 recusados + 4 ausentes misturados) | **2 cruzamentos que SÃO objeto do pote** (`INCROCI CHE SONO OGGETTO DEL POTE · 2 di 86`), estado literal (`GRANA INCOMPATIBILE · PARTIAL_GRAO_INCOMPATIVEL`), chaves NÃO SEI em âmbar, id `PROVVISORIO (D119)`; aba **«RIFIUTATI · 84»** só por clique, com o motivo (79 `PROVA_INCOMPLETA` · 1 `ITEM_BLOQUEADO_EM_G0` · 4 `AUSENTE_DO_POTE`); carimbo **«referenza ADAMA: registro del 31/08, ultima verifica 07/09, PUÒ ESSERE NON AGGIORNATO · PODE_ESTAR_DESATUALIZADO»** (datas da porta) e «uso dichiarato a livello di prodotto (DECLARACAO_DE_PRODUTO): da confermare, mai "autorizzato"» |
| **Label Intelligence** (`#etichette`) | o compartimento portfolio do pote (menu **2**) + os mesmos 86 cruzamentos | **PRODOTTO DI STRUMENTO · SINTONIA — LABEL INTELLIGENCE — non è una corsa della Intelligence**; istantanea del registro **31/08** (PROD_FTS_6_20260831) · ultima verifica 07/09 · PODE_ESTAR_DESATUALIZADO · sigillo d27278de…; menu **166**; os cartões são os do payload selado (166 / 210 / 54), byte a byte |
| **Radar delle Opportunità** | «VUOTO · SEM_OBJETOS_NESTA_CORRIDA» | **«0 OPPORTUNITÀ DIFENDIBILI IN QUESTA CORSA»** (contado nas OPORTUNIDADE do pote) + PORQUE_VAZIO + exemplo **olivo × mosca → NO_DEFENSIBLE_ACTION_YET** (janela NO, agir NÃO, 13 itens, 1 apoio). Os **43** casos do snapshot V2.1 de 07/09 (BY_STATUS: **2 `ACT_NOW`**, medido em `meeting-intelligence-snapshot.js`) não aparecem; a lista `#msignals` que ainda os mostrava também saiu |
| **Radar Futuro** | 10 FATO_PRESENTE_SOBRE_O_FUTURO | **0** com chave de domínio provada («zero qui non prova assenza») + secção **«AGENDA · EVENTI DATATI — non è il Radar Futuro · 10»**, tracejada. Os 44 ITFC do legado: escondidos |
| **Busca** («vite») | **58** resultados do modelo V2.1 + demo | **2** — só objetos do pote (um por objeto distinto) |
| **12 vistas de detalhe** (mcase, window, company, cproduct, event, theme, person, product, source, signal, case, brief) | abriam o registo legado | **fechadas**, com «NON SO · questa scheda legge il modello precedente… LEGADO_V21_VISIVEL = false». `#etichetta` abre: é a Label Intelligence |
| **barra lateral** | oggetti **47** · incroci **86** · rifiutati 245 | oggetti **25** (distintos) · incroci nel pote **2** · rifiutati 245 |
| **pote falha** (esperado e não chegou) | casco antigo + **demo** (Rete Commerciale simulada, relógio 02 SET) | **NON SO** em toda rota, relógio «DATI AL · NAO SEI», nenhuma demo, nenhuma Rete Commerciale |
| Rete Commerciale | vazio do pote, SIMULATO | igual |
| Finestre, Polso, Voci, Concorrenza, Scientifica, Archivio, Fonti | pote R7 | iguais (Archivio: os 2 CROSSING levam `PROVVISORIO`) |

Capturas (Chromium, 1440 px) feitas durante a missão: Portafoglio, aba rifiutati, Radar, Radar Futuro, Label
Intelligence e pote ausente — ficaram fora do repositório (scratchpad). Descrição acima; o PP1 reprova se qualquer
uma destas telas deixar de dizer o que diz.

### Bandeiras do dono (desligadas)

`italia-portale/client/sintonia-pote-publicacao.js` → `BANDEIRAS`:

```js
var BANDEIRAS = { LEGADO_V21_VISIVEL: false, ITFC_LEGADO_VISIVEL: false };
```

Ligar é trocar `false` por `true` (só `true` liga). O legado volta **selado**: «LEGADO 07/09 · SENZA FINESTRA PROVATA —
acceso dal proprietario». Não há parâmetro de endereço: um visitante não chega ao legado por um link.

## 3 · NÃO SEI, e o que ficou de fora

| o que | porquê |
|---|---|
| a pesquisa do LAB 27/09 (PESQUISA-CRUZAMENTOS F.1) | citada pela missão; não está neste repositório — não a li |
| D119 (identidade estável do cruzamento) | não está escrita no repo; o texto da marca cita a missão |
| `LINK_LEVEL` por cruzamento na tela | o pote R7 não o transporta (vive no `CRUZAMENTOS-MAX.json` da linha de serviço, que **não é pote**). Mostrá-lo seria ler fora do pote. A tela diz a regra geral: DECLARACAO_DE_PRODUTO = da confermare |
| se a Label Intelligence diz «autorizzato» num par que na porta é DECLARACAO_DE_PRODUTO | o payload selado (06/09) é anterior à porta e não tem `LINK_LEVEL`; os números ficaram idênticos por ordem da missão. **NÃO SEI** par a par |
| o frescor | medido no dia da D114 (27/09), declarado (`HOJE_VEIO_DE = DECLARADO`), não no dia do visitante. Daqui a dias a tela continua a dizer «20 dias»: a publicação seguinte recalcula |
| os testes Python trazidos pelo merge | ver §4: comparados contra a ponta de hhhj7t, não contra a base (lá não existiam) |

## 4 · Testes — antes × depois, pelo nome

@@TESTES@@

## 5 · Mutação

@@MUTACAO@@

## 6 · Mapa

`python3 system-map/scripts/correr_a_cadeia.py REGERAR` → commit dos gerados → `VALIDAR` = **SYSTEM_MAP_CHECK=PASS**
→ `impressao_da_arvore.py --conferir-carimbo` = **IGUAL** (SHA final no fim). Peças repostas depois do merge:
`C-CI-RELEASE`; `C-LASTMILE` (+publicador, adaptador da Label, inventário do acervo); `C-PORTAL-MODELO` (+leitura);
`C-PORTAL-DADOS` (+publicado); `C-AUDIT-CASCO` (+`test_pote_publicado.mjs`, `test_casco_hoje.mjs`). Não corri
`--stamp`.

## 7 · Publicação — o COMANDO que o coordenador corre (eu NÃO publiquei)

A Vercel publica `release/canonical` (produção) pela integração Git; o `portao-do-release.yml` corre no PR e no
push para essa branch. `release/canonical` (27b9e674) é antepassado desta branch: **fast-forward**.

```bash
git fetch origin release/canonical claude/casco-publication-minimum-5q7kbw
git merge-base --is-ancestor origin/release/canonical origin/claude/casco-publication-minimum-5q7kbw && echo FF_OK
git push origin origin/claude/casco-publication-minimum-5q7kbw:refs/heads/release/canonical   # so fast-forward
```

⚠️ Este fast-forward leva para produção **também a linha de serviço inteira** trazida pelo merge de hhhj7t (§1). É o
que a missão mandou juntar; o coordenador decide se o empurra assim.

## EM PALAVRAS SIMPLES

@@SIMPLES@@
