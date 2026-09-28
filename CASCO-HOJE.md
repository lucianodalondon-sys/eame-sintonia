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

Base = `60ee56b2` (worktree limpa). Final = esta branch (worktree limpa em `86bf292c` para a bateria inteira; os
consertos seguintes, re-medidos na árvore final). Mesma máquina, Chromium local (`/opt/pw-browsers`), playwright-core
1.56 instalado **fora** do repositório (nada entrou no Git). A linha de serviço trouxe ~250 testes Python que a base
não tinha: esses comparam-se com a **ponta de hhhj7t** (`c551062b`), a base deles.

| bateria | base | final |
|---|---|---|
| `tests/test_casco_hoje.mjs` (novo) | — | **48/48** |
| `tests/test_pote_publicado.mjs` | 58/58 (61 com o merge de japwor: Q2 reprovava) | **67/67** |
| `tests/test_pote_no_casco.mjs` | 93/93 | 93/93 |
| `audit/casco/d97-auditoria.mjs` | sai 1 (84 cruzamentos sem prova na tela, 13 rotas de legado) | **sai 0** (0 · 0 · 0 · 0) |
| PP1 `audit/casco/pote-publicado-browser.mjs` | 11/11 | **13/13** |
| `audit/run.mjs` (corredor do CI) | 73 PASS · B2 FAIL · W2, O1 N/M | **igual por nome** (B2 = `deployment.generated.json`, nasce no `npm run build`) |
| 84 portões `audit/*.mjs` + `audit/casco/*.mjs` por ficheiro | 39 com saída ≠ 0 | os **mesmos 39** por nome (`brandwell` passou por 0→1→0: conserto abaixo) + `sala-leitura`/`painel-operacao` da linha de serviço saem 2 = «uso:» (são geradores com argumentos, não portões) |
| `tests/*.py` presentes na base (69) | 10 falham | **7 das 10 continuam**, 3 passaram (`test_coleta_externa`, `test_comunicacao`, `test_portao`); **6 passam a falhar** (`test_canonico`, `test_metricas`, `test_migrations`, `test_o9_caminho_instrumentado`, `test_social_sessao`, `test_youtube_oficial`) — ver abaixo |
| `tests/*.py` novos (vindos do merge, ~246) | — | contra hhhj7t: **0 falhas novas** depois dos consertos, fora a causa única dos pares (abaixo) |
| `system-map/tests` | 1 falha (`test_system_map`) | as reprovações são as **mesmas por nome** que na ponta de hhhj7t (`test_system_map` 11, `test_reconciliacao_do_universo` 5, `test_ordem_por_dependencia` 1, `test_quatro_planos` 1); `test_cadeia_declara_io` **consertado** (reprovava lá também); `test_base_da_auditoria` ver abaixo |

**Consertados no caminho, apanhados pela comparação por nome**

- `brandwell BW1`: a faixa antiga «QUESTA SCHERMATA LEGGE» reaparecia em #etichette com `#7BE0A6` (fora da paleta
  ADAMA). Com o produto de ferramenta, a proveniência é dita pela faixa dele; a antiga esconde-se (`portale.html`).
- `test_ponte_intelligence_casco G1` / `test_pote_intelligence_casco A4`: o módulo da ponte declarava que o casco abre
  `#sala`/`#painel`; o casco que vai ao ar não as abre. Ajustada a **declaração** (`pacote/ponte_intelligence_casco.py`,
  `VISTAS_QUE_NAO_SAO_FERRAMENTA = {}`, com o texto antigo em comentário), não o teste.
- `test_acervo_organizado`: `AUDITORIA-D97-R7.json` e `INSUMOS-DECLARADOS-ACERVO.json` regerados pelos seus geradores
  (o segundo só mudou números de linha do motor, efeito do merge); `test_os_numeros_da_auditoria` ajustado de forma
  **DECLARADA** (item 9: a violação que ela registava foi fechada).
- `test_cadeia_declara_io`: `MEDIDO_VARRE` com os valores medidos (árvore juntada: 4044 rastreados, não 1726) e as
  leituras reais declaradas (`CENSO_DAS_ESTRADAS_IT`: `leis/*`, `motor/*`, `docs/fontes/*`; `CENSO_DA_TOPOLOGIA`: `*.js`).

**Ajustes DECLARADOS de testes (citando a missão)** — nenhum com uma asserção de conteúdo a menos:
`test_pote_publicado` Q2 (o gerador veio com o merge ordenado; a lei «só este pote vai ao ar» passa a medir-se no
`outputDirectory`), Q3/Q5/Q11 (#etichette é produto de ferramenta), Q4 (2 na tela + 84 na aba, as mesmas provas sobre a
união, +4 provas novas), Q7 (25 distintos · 2 no pote · menu da Label 166 · Radar Futuro 0), Q9 (a linha «incroci»
conta o pote carregado); PP1 (idem); `d97-auditoria.mjs` (mede a tela, reconhece a busca no pote e o produto de
ferramenta, +medida 4: pote ausente); `drive.mjs` (quem pede `semPotePublicado` liga as bandeiras do dono pela página).
Nomes que por isso mudaram na lista: 9 (Q2, Q3×2, Q4×4, Q7, e um Q8 do japwor).

**O que NÃO consegui pôr verde, e porquê**

| falha | porquê | o que resolve |
|---|---|---|
| `test_adama_referencia` (3 erros) e `test_porta_unica_referencia` (sai 1) | **conflito semântico entre as duas linhas, em DADO**: `data/samples/IT-ROTULOS/IT-ROTULOS-PARES.json` só mudou nesta linha (5402 pares, V2.1 `8b35a8fa`); o construtor da referência (`fontes/adama_referencia.py:368`) foi escrito contra a edição de 2030 pares e **recusa** colar citações a pares diferentes. A porta (leitura) continua a funcionar — o carimbo na tela vem dela | reconstruir a referência numa edição nova (a missão de manutenção que a própria porta nomeia, `nuvem-referencia-manutencao-v1`). Não o fiz: é dado novo |
| `test_canonico`, `test_metricas`, `test_migrations`, `test_o9_caminho_instrumentado`, `test_social_sessao`, `test_youtube_oficial` | passavam na base; falham **idênticos, pelo nome e pela mensagem**, na ponta de hhhj7t — vêm com a linha de serviço | a linha de serviço (fora desta missão) |
| `test_base_da_auditoria · FUNCTIONAL_COLLECTION_DIFF_FROM_BASE_e_zero` | busquei a ref que ele pede (`claude/sala-persistente-preflight-real-v1`) e ele passou a medir: a árvore juntada tem código funcional da linha do release (workflows) que a base da coleção não tem. Na ponta de hhhj7t reprovava por CANNOT_MEASURE | é efeito direto do merge ordenado; decisão do dono sobre qual é a «base da auditoria» desta branch |

## 5 · Mutação

22 defeitos plantados, um de cada vez, numa worktree descartável (o repositório não foi tocado); morto = algum de
`test_casco_hoje.mjs`, `test_pote_publicado.mjs`, `d97-auditoria.mjs` sai ≠ 0. **22/22 mortos.** Lista, âncoras e quem
apanhou cada um: `docs/casco/CASCO-HOJE-MUTACAO.json`.

Entre eles os três que a missão pede: **religar o legado** (M01 V2.1 por omissão, M02 ITFC, M21/M22 legado com o pote
sem bandeira, M09 busca, M10 detalhes, M11 pote ausente → demo, M17 `#msignals`), **somar gavetas** (M03, M16 barra a
contar 86) e **mostrar recusado** (M04 os 86 na tela, M05 aba rifiutati por omissão). E ainda: data do carimbo escrita
a mão (M06), carimbo sem frescor (M07), sem PROVVISORIO (M08), radar sem a sonda (M12), futuro sem a Agenda (M13, M19),
selo da Label que não confere (M14), «autorizzato» no uso declarado pelo produto (M15), carimbo pelo relógio (M18),
cruzamentos por cima da ferramenta (M20).

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

O portal passa a mostrar só o que a Inteligência aprovou nesta rodada. No Portafoglio ficam os 2 cruzamentos que
têm prova completa; os outros 84 não somem, vão para uma aba «rejeitados» com o motivo de cada um. A Label
Intelligence volta, mas dizendo o que é: o produto de uma ferramenta, com a data do registro (31/08) e o aviso de que
pode estar desatualizado. O Radar diz «0 oportunidades defensáveis» e mostra porquê, com o exemplo da oliveira e da
mosca. O Radar Futuro separa o que é de agronomia (nada, hoje) da agenda de eventos. A busca e as fichas antigas não
aparecem mais — o dono pode ligá-las de volta com uma chave, e elas voltam carimbadas «legado 07/09». Se o pote não
carregar, a tela diz «não sei» em vez de mostrar a demonstração. Juntar a linha de serviço trouxe a porta das datas,
mas também 9 testes que já estavam vermelhos lá (6 Python, 3 do mapa) e um conflito de dados na referência que só uma edição nova resolve.
