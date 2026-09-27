# CASCO-AO-AR-R7 — o POTE-R7 vai ao ar (D114)

```text
DECISAO   D114 do dono: «portal vai ao ar hoje com o maximo de informacoes e cruzamoentos possiveis»
BASE      casco-real-v1 @ cb734f388 (+ insumos 05d398bf) · release/canonical = 27b9e674 (antepassado: fast-forward)
RAMO      claude/casco-r7-publication-yb7nsg
CORRIDA   IR-e09acab6365032523d6e · copia da Sala 27/09/2026 18:30 UTC · 242 READY · motor int-intake-g0v4-v1 @ a5db06c4
POTE      docs/casco/r7/POTE-R7.json · POTE_INTELLIGENCE_CASCO/v2 (gerador ce775ff5) · 47 objetos · 245 recusados
ANALISE   docs/casco/r7/ANALISE-R7.json · os 86 cruzamentos da MESMA corrida (trazido so este ficheiro de
          nuvem-cruzamentos-max-v1 @ a09d383d, blob 80001e9d — o pote v2 nao transporta o estado do cruzamento)
CONTRATO  nuvem-pote-v2-unico-v1 NAO esta PRONTO (cabeca 77da2476 = «insumos da missao»): fica o formato ce775ff5
          como esta; o leitor sintonia-pote-casco.js NAO foi mexido
```

## 1 · O que foi feito

| peca | ficheiro | o que faz |
|---|---|---|
| a porta com nome | `pacote/publicar_pote_aprovado.py` | copia POTE-R7 + ANALISE-R7 para o portal, **recusa** se os tres insumos se contradizem (corrida, contagens do manifesto, 86 = resumo, estados conhecidos); `--conferir` prova que o publicado e o dos insumos |
| o dado publicado | `italia-portale/client/sintonia-pote-publicado.js` (GERADO) | `window.SINTONIA_POTE_PUBLICADO` (decisao, SHA, origem) + o pote como `window.SINTONIA_POTE`; com `?pote=local` cala-se |
| a leitura | `italia-portale/client/sintonia-pote-publicacao.js` | faixa D114, recusados visiveis, os 86 cruzamentos, a sonda, as lacunas, o vazio do «field»; rotulo humano ao lado de cada codigo. Nao cruza, nao ordena, nao muda estado |
| a tela | `italia-portale/client/portale.html` | carrega publicado → leitor → publicacao; `_potePublicado`: menu conta o pote, relogio diz a copia da Sala, Rete Commerciale nao desenha; faixa D114 no topo, bloco de extras em baixo |
| as provas | `tests/test_pote_publicado.mjs` (58) · `italia-portale/audit/casco/pote-publicado-browser.mjs` (PP1, 11, no corredor `run.mjs`) | ver §5 |

As trancas continuam: `sintonia-pote.js`, o gerador `pote_intelligence_casco.py` e as pastas PARA-O-CASCO **nao** entram no ramo
nem no deploy (Q2 prova). So o pote aprovado em D114 atravessa, por uma porta com nome.

## 2 · Cada tela, antes × depois

Antes = o que esta no ar (sem pote). Depois = o pote R7. Numero = contador do menu.

| tela | antes | depois |
|---|---|---|
| Radar delle Opportunità | 17 · snapshot V21 de 07/09 | **0 · VAZIO · SEM_OBJETOS_NESTA_CORRIDA** (com o porque) |
| Portafoglio | 173 · pacote V2.1 | **2 objetos + os 86 cruzamentos** (5 A CONFIRMAR · 29 NO · 48 grao incompativel · 4 sem cultura), cada um com prova (URL, data de publicacao, chave da Sala, trecho) e o que o pote fez com ele; 80 recusados visiveis |
| Label Intelligence | 166 · payload selado | **o mesmo compartimento portfolio** (o pote diz VISTAS_DO_CASCO = portfolio, etichette) |
| Radar Futuro | 44 · pacote da casa | **10 FATO_PRESENTE_SOBRE_O_FUTURO** (tracejado, nunca oportunidade) |
| Finestre Colturali | 29 · norma canonica | **2 sinais ARIF** + 4 recusados + **a sonda olivo × mosca** (13 itens, 1 apoio valido, WINDOW_OPEN_NOW = NO, ACT_NOW = NAO, NO_DEFENSIBLE_ACTION_YET) — marcada EXPERIMENTAL, «nao e janela instalada» |
| Polso di Mercato | 157 | **6 sinais** (preco, unidade, praca = NAO SEI) |
| Voci dal Campo | 79 | **0 · VAZIO** com o porque |
| Concorrenza | 577 | **0 · VAZIO** com o porque |
| Intelligence Scientifica | 88 | **2 sinais** (DOI/ORCID = NAO SEI) |
| Archivio (e #future) | 1114 | **22 objetos** + 89 recusados |
| Registro delle fonti | 194 | **3 rendimentos de fonte** + 72 recusados + o que as 38 novas trouxeram (28 fontes, 23 candidatas, 9 sinais datados) + D112 + **213 lacunas** da corrida |
| Rete Commerciale di Campo | 18 · demo | **nao desenha**: «SIMULATO — la simulazione non è mostrata» + VAZIO · CASCO_SEM_CONTRATO_DE_INTELLIGENCE |
| relogio lateral | «DATI AL · 02 SET» + 3 KPI do legado | **«DATI AL · 27 SET 2026 18:30 UTC»** (copia da Sala) · corrida R7 · 47 objetos · 86 cruzamentos · 245 recusados |

Marcas visiveis: EXPERIMENTAL em toda vista (faixa do pote + faixa D114) · **A CONFIRMAR** so nos 5 sim · NAO SEI em amarelo
onde falta prova · **FONTE CANDIDATA** nos 47 cruzamentos da extensao declarada · data real de cada prova (publicado /
colhido / tempo do fato), nunca «oggi».

⚠️ **O que saiu do ar, e porque.** A precedencia do pote (D95/D96, ja no codigo da base: «SNAPSHOT AO LADO DO POTE E DUAS
VERDADES NA MESMA TELA») tira das 12 rotas o legado: as 17 oportunidades do snapshot V21 de 07/09, os 166 rotulos selados, os
44 do Radar Futuro, etc. Nao revoguei essa regra. **Se o dono quiser o legado de volta ao lado, e decisao dele** (por
exemplo uma rota propria, marcada «istantanea 07/09»); a mudanca e uma linha em `_poteTemPrecedencia`.

## 3 · O que ficou NAO SEI, e porque

| o que | porque |
|---|---|
| 80 dos 82 cruzamentos enviados, **incluindo os 5 «sim»**, nao sao objetos do pote | defeito C1 da Coleta: as 38 novas nao tem `document_key` → DOCUMENT_ID em falta → o pote recusa (PROVA_INCOMPLETA). A tela mostra-os a partir da ANALISE, com «RIFIUTATO DAL POTE · falta DOCUMENT_ID» |
| 4 cruzamentos NOT_POSSIBLE nao estao no pote nem como recusa | o gerador nao os enviou; a tela diz «ASSENTE DAL POTE» |
| CROP_ID, PRODUCT_ID, TARGET_ID, REGION_ID quase sempre NAO SEI | o READY nao tem ENTITY_SOURCE nem LOCATION_SOURCE (0/242); cultura do documento nao vira CROP_ID (D112) |
| data de publicacao NAO SEI em 77 dos 86 cruzamentos, e em 20 provas do pote | a fonte nao a deu; nunca e preenchida com a data da colheita |
| o SHA do POTE-R7 deste ramo **nao confere** com o MANIFESTO-R7 (0189967… ≠ 2610af4…) | as contagens por compartimento e por motivo conferem; o byte a byte nao. `conferir_pote` do dono (ramo nuvem-pote-v2-unico-v1) sobre ESTE ficheiro: **0 violacoes**. Dito na tela, em amarelo |
| se os 5 «sim» valem | as regras X3w/X3h nasceram nesta rodada, depois de ver os dados: **precisam de regressao** (relatorio R7 §3) |
| D114 escrita no repositorio | so existe na mensagem da missao; o publicado cita-a como tal (`DATA_BASE`) |
| SOURCE_HEAD e CORTE na linha da corrida aparecem como JSON | e o leitor ce775ff5, que nao mexi; a faixa D114 mostra-os formatados |

Pessoa nomeada: um objeto do Radar Futuro cita, de um anuncio publico de seminario, o nome e cargo de um dirigente publico.
Vem do pote tal como a Intelligence o escreveu; **a decidir pelo coordenador** se vai ao ar assim.

## 4 · Ajustes DECLARADOS de portoes (citando D114)

BB1 (barras de busca), ET1 (Label Intelligence), `meeting-browser`, `opportunity-hub`, `quarantatre` e a viagem J do `mobile`
medem a interface do **legado**, que a precedencia tira das rotas por omissao. Passam a abri-la no estado **sem pote
publicado** (`drive.mjs · semPotePublicado`: o ficheiro e respondido vazio — o estado de todo deploy antes de D114), **sem
uma assercao a menos**. O que vai ao ar por omissao passa a ser medido pelo **PP1**, novo, no corredor. Para reverter:
tirar a bandeira.

## 5 · Testes, antes × depois (por nome)

Base = `cb734f38`+insumos (`05d398bf`), num worktree limpo; depois = este ramo. Mesma maquina, mesmo Chromium local
(`/opt/pw-browsers`, playwright-core 1.56 ja instalado — nada baixado).

| bateria | base | depois |
|---|---|---|
| `npm run build` (como a Vercel) | OK · SYSTEM_MAP_CHECK=PASS | OK · SYSTEM_MAP_CHECK=PASS |
| `node italia-portale/audit/run.mjs` (corredor do CI) | 73/73 + 2 N/M (W2, O1) | **74/74** + as mesmas 2 N/M (+PP1) |
| `tests/test_pote_no_casco.mjs` | 93/93 | 93/93 |
| `tests/test_pote_publicado.mjs` (novo) | — | **58/58** |
| `audit/casco/pote-publicado-browser.mjs` PP1 (novo) | — | **11/11** |
| 17 portoes `audit/casco/*.mjs` + 15 portoes de browser avulsos (nenhum workflow os chama) | 14 com saida ≠ 0 | **13** — os mesmos por nome menos `brandwell` (passou a 0); nenhum passou de 0 para ≠ 0 |
| system-map/tests (11) + 3 testes Python que leem o cliente | falhas: test_system_map (4), test_adama_relevance (2), test_fundacao_da_coleta (1) | as mesmas por nome (test_system_map: 3, subconjunto das 4) |

Comparacao sub-prova a sub-prova (base PASS → depois nao PASS), depois dos consertos:

| sub-prova | porque | estado |
|---|---|---|
| internal-token **IT3** (18) | o cartao mostra `SOURCE_ID` (ex. `IT-T3-008`) sem o nome da fonte: o pote nao o traz, e junta-lo ao registo de fontes seria a tela a cruzar (INT-LAW-023) | **NAO SEI declarado** — pedido ao dono do pote: nome da fonte na prova |
| mobile **MB5** | «nome do produto no cartao nao cortado»: `NO SLOTS` — o radar servido nao tem cartao de produto; o portao nao tem o que medir | por construcao (o portao ja saia 1 na base) |

Consertados no caminho, apanhados pela comparacao: BW3 (titulo do pote em MAIUSCULAS, ADAMA), IT1 (32 na base → 8),
rolagem horizontal a 390 px (1025 px → 390), aresta com evidencia emprestada (QUATRO_PLANOS). Passaram a passar sobre a
base: brandwell BW1 e BW3, action-map AC1–AC4.

**Mutacao** (worktree descartavel; 18 defeitos plantados um a um; morto = algum teste reprova): **18/18 mortos** —
«NO» com A CONFIRMAR, ordem trocada, candidata trocada, estado recalculado, recusados de outro compartimento, pote de outra
corrida, NAO SEI sem destaque, SHA dito conferido, menu a contar o legado, relogio de 02/09, Rete Commerciale de volta, marca
sem `data-marca`, linha da corrida sem quebra a 390 px, `?pote=local` ignorado, estado mudado a mao no publicado, insumo que
contradiz o manifesto, `sintonia-pote.js` fora do `.gitignore`, sonda ausente.

**Mapa**: cadeia `correr_a_cadeia.py REGERAR` → commit → `VALIDAR` = SYSTEM_MAP_CHECK=PASS → `impressao_da_arvore.py
--conferir-carimbo` = IGUAL (ver o SHA final no fim da missao). Ficheiros novos declarados: C-LASTMILE (publicador),
C-PORTAL-DADOS (publicado), C-PORTAL-MODELO (leitura), C-AUDIT-CASCO (teste + PP1). Nao corri `--stamp` (carimba o repo
inteiro); as pecas que mexi ficam 🟡 ate uma leitura humana.

## 6 · Publicacao — para o coordenador (eu NAO fiz push em release/canonical)

```bash
git fetch origin release/canonical claude/casco-r7-publication-yb7nsg
git merge-base --is-ancestor origin/release/canonical origin/claude/casco-r7-publication-yb7nsg && echo FF_OK
git push origin origin/claude/casco-r7-publication-yb7nsg:refs/heads/release/canonical   # so fast-forward
```

## EM PALAVRAS SIMPLES

O portal passa a mostrar o que a Inteligencia produziu na rodada 7, e so isso: 47 achados com a prova de onde cada um veio
(link e data), os 86 cruzamentos «rotulo ADAMA × boletim» com o estado de cada um — 5 «sim, a confirmar», nenhum ainda
certo — e, onde nao ha nada, a razao escrita. Tudo marcado como experimental. A rede comercial inventada nao aparece. Os
numeros antigos de 07/09 saem da tela, porque mostra-los ao lado dos de hoje seria contar duas historias.
