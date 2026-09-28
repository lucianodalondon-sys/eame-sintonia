# PORTAL-PUBLICA-SOZINHO — D126, «portal publica sozinho»

> Base: produção `b273660` (`origin/servico-20260923-0923`). Branch: `claude/portal-auto-publish-1f67wu`.
> **Nada foi publicado de verdade.** O caminho inteiro foi ensaiado num anfitrião LOCAL (deployments + alias em
> 127.0.0.1). O CLI da Vercel **não existe** no contentor da missão e não há credencial: o deploy de PREVIEW na
> nuvem **não foi feito** — dependência que falta: `vercel` CLI instalado e logado (`vercel login` + `vercel link`).
> D97, D115, D122, D123 e D125 **não estão escritas no repositório**: segui o resumo delas no pedido da missão.

## 1 · O que foi feito, e onde

| o quê | onde |
|---|---|
| **A lei** (autoridade de deploy medida e declarada, conferências, regra de promoção, telas, registo) | `portoes/PUBLICACAO-AUTOMATICA.json` |
| **O publicador**: C0 pote → ANTES → montar (`git worktree`) → C1/C2/C3 → envelope só na cópia → C5 navegador → implantar → C6 no ar → voltar sozinho + ALERTA | `portoes/publicar_portal_sozinho.py:706` |
| C0 · o pote: forma+lei v2 (`validar_pote_v2`), nenhum objeto sem prova, **D123** caso→produto→bula, **D122** evento só com data, nada de dado cru, nada da demo, **promoção** | `portoes/publicar_portal_sozinho.py:111` (promoção `:190`) |
| C3 · os três jobs do portão do release, **lidos** de `release/canonical:.github/workflows/portao-do-release.yml` (não copiados); só o vermelho herdado e declarado passa (N1) | `portoes/publicar_portal_sozinho.py:358`, `:382`; contrato `:69` |
| C5/C6 · contagem por tela = a do pote, 43/44 antigos escondidos, a barra conta o pote, caixa «oggi» fora, SHA servido | `portoes/publicar_portal_sozinho.py:252`, contagem esperada `:235`, SHA no ar `:478` |
| a volta prova-se no ar por **duas** medidas (deployment atrás do endereço **e** SHA servido) | `portoes/publicar_portal_sozinho.py:822` |
| implantadores com a mesma interface: `EnsaioLocal` (ensaiado) e `VercelCLI` (**NÃO TESTADO**) | `portoes/publicar_portal_sozinho.py:519`, `:564` |
| o fotógrafo: fotos + contagens por tela (legado lido da própria página, barra, SHA, caixa «oggi») | `portoes/fotografar_portal.mjs` |
| **o lugar do pote publicado** (no Git: `null`; o envelope só existe na cópia implantada) | `italia-portale/client/sintonia-pote-publicado.js` |
| o casco lê o envelope como `?pote=local` (o local vence) | `italia-portale/client/sintonia-pote-casco.js:29` |
| a barra conta o pote (`contagemDaVista`); `field` mostra o porquê do pote, não a demo | `sintonia-pote-casco.js:187`, `:58`/`:177`; `portale.html:5934`, `:4064` |
| a caixa «oggi» (janelas de 02/09) sai com o pote | `italia-portale/client/portale.html:12265` |
| `PUBLICACOES/` fora do Git e do deploy | `.gitignore`, `.vercelignore` |
| testes (51) · mutação (44) · ensaio (7 cenários) | `tests/test_publicar_portal_sozinho.py`, `provas/portal_publica_sozinho/` |
| mapa: `C-PUBLICA-SOZINHO` (Z-PORTOES), `C-PROVA-PUBLICA-SOZINHO` (Z-PROVA), lugar em `C-PORTAL-MODELO` | `system-map/data/architecture.declared.json` |

### 1.1 · Caminho do pote até o deploy (pedido 1) — descoberto e declarado

- **Medido:** a autoridade canônica é `release/canonical` → integração Git da Vercel (`system-map/CANONICAL-PUBLICATION.json`).
  O repositório é **público** e o pote tem dado real (`sintonia-pote.js` no `.gitignore` e `.vercelignore`): **pelo Git, não**.
- **Declarado:** o código continua a ir por `release/canonical`. O **pote** vai pelo CLI já logado, na máquina do
  coordenador, numa build **pré-construída** (`vercel build` + `vercel deploy --prebuilt [--prod]`) de uma cópia montada.
  Artefato gerado = envelope `SINTONIA_POTE_PUBLICADO/1` com `POTE_SHA256`; gate = C0…C5; SHA gravado no envelope,
  no registo e em `ULTIMA-PUBLICACAO.json`, e **relido do que está no ar** em C6.
- **Consequência, dita:** um merge novo em `release/canonical` implanta pelo Git uma build **sem** pote. A corrida
  seguinte do publicador mede isso no ar (SHA ≠), grava **ALERTA DERIVA** e republica. Ligar o merge ao publicador: dono.

### 1.2 · Regra de promoção (pedido 4) — **marcada para o dono ver**

`portoes/PUBLICACAO-AUTOMATICA.json:46` · `ESTADO = AGUARDA_DONO`. Um pote `EXPERIMENTAL · NAO_PARA_CLIENTE` vai a
**produção** só se: (1) a regra estiver `APROVADA_PELO_DONO` com `APROVADA_POR` e `APROVADA_EM`; (2) a corrida não
for sintética; (3) todas as conferências passarem. A marca **não** é apagada (o SHA publicado é o do pote da
Intelligence) e a faixa EXPERIMENTAL continua visível. **Hoje, `--modo producao` bloqueia sempre em `C0_PROMOCAO`.**

## 2 · Ensaio completo, sem publicar (anfitrião local; conferências reais; navegador real)

`provas/portal_publica_sozinho/ensaio.py` sobre `d63121db` → `provas/portal_publica_sozinho/ENSAIO-d63121db.json`.
Pote **sintético** (`tests/fixtures/pote/POTE-SINTETICO-PUBLICA-SOZINHO.json`).

| cenário | resultado | o que prova |
|---|---|---|
| A pote novo | **PUBLICADO** | C0–C6 todas PASS; C3 = build-gate + System Map REGERAR/VALIDAR + 73 portões (só **N1** herdado) |
| B o mesmo pote | **NADA_A_PUBLICAR** | não republica o que está no ar (nada se monta) |
| C segundo pote | **PUBLICADO** | o primeiro vira `POTE-ANTERIOR.js` com SHA `51ae6c08…` |
| D pote sem bula | **BLOQUEADO** | `C0_D123_CASO_PRODUTO_BULA`; nada vai ao ar |
| E página no ar sem contagem | **REVERTIDO** | C6 reprova (SHA, contagem, barra) → volta sozinha → volta **provada** → ALERTA `REVERTIDO` |
| F rollback que não roda | **ALERTA_CRITICO** | a volta «diz que rodou» e o alias não mudou → não provada → ALERTA crítico |
| G produção pelo ensaio | **BLOQUEADO** | `MODO`: produção só com implantador que publica de verdade |

C, E e F reusam as linhas C1/C2/C3 que A mediu **no mesmo commit** (dito na NOTA de cada registo); o resto é real.

**Antes → depois (cenário A), por tela** — objetos do pote · 43 antigos visíveis · 44 antigos visíveis:

| tela | antes | depois |
|---|---|---|
| radar (meeting / início) | 0 · **17** · 0 | **2** · 0 · 0 |
| radar futuro | 0 · 0 · **44** | **1** · 0 · 0 |
| arquivo / future · finestre · registro | 0 | 2 · 1 · 1 |
| market · voices · competitors · science · portfolio · etichette · field | 0 | 0 (NAO SEI · VUOTO · o porquê do pote) |
| barra | 17 · 173 · 44 · 166 · 29 · 157 · 79 · 577 · 88 · 1114 · 194 · 18 | 2 · 0 · 1 · 0 · 1 · 0 · 0 · 0 · 0 · 2 · 1 · 0 |
| caixa «oggi» | visível | fora |
| `/casa` (sem rota) | 43 · 44 | **43 · 44** — AVISO, não bloqueia (ver §5) |

**O ensaio achou dois defeitos meus antes de passar** (corrigidos em `d63121db`): `#field` abria o radar (o endereço
só aceita rotas de 1.º nível — o fotógrafo passou a clicar a voz da barra) e a caixa «oggi» com as janelas de 02/09
ao lado do pote.

## 3 · Testes — antes/depois, pelo NOME

`provas/int_r7/bateria_por_nome.py` (rede fechada), base `b273660` × ramo `6d460caa`.

| | base `b273660` | ramo `6d460caa` |
|---|---|---|
| módulos | 320 | 321 (+`test_publicar_portal_sozinho`) |
| testes | 7190 | 7241 |
| falhas por nome | 130 | 130 |

**Novas: 0. Sumidas: 0** (`--comparar`; JSONs em `provas/portal_publica_sozinho/BATERIA-*.json`). As 130 são as
herdadas da base, pelo nome (o LOTE7 mediu 131 na sua base; aqui a base mediu 130 — medido, não herdado).

Fora da bateria Python: `node tests/test_pote_no_casco.mjs` **118/118** (antes 118/118); `node system-map/tests/test_freshness.mjs` **PASS · 49**.
`tests/test_publicar_portal_sozinho.py` **51/51**. Nenhum teste existente foi ajustado.

## 4 · Mutação — `provas/portal_publica_sozinho/mutantes.py` → **44/44 mortos**

Worktree temporária do HEAD (o repo não é tocado). Os quatro que a missão nomeia: **pote inválido** (M01, M25),
**gate falhado** (M20, M21, M24, M26), **página no ar sem contagem** (M12, M13, M14, M19), **rollback que não roda**
(M29, M30, M31, M33) — e também D122/D123, prova, cru, demo, promoção, barra, «oggi», casco, `.gitignore`.
**Achado:** na 1.ª corrida **M28 (produção pelo anfitrião de ensaio) sobreviveu** — o teste era barrado pela promoção,
não pela regra do modo. Isolei o teste; morreu. Resultado em `provas/portal_publica_sozinho/MUTACAO.json`.
O fotógrafo (`.mjs`) não está nos mutantes: prova-o o ensaio, com **controlo negativo** (sem pote ele vê 17 e 44).

## 5 · NÃO SEI / por decidir (dono)

1. **Vercel real:** `VercelCLI` não testado (sem CLI nem credencial). Um preview protegido pela Vercel devolve 401 e a C6 reprova — NÃO SEI se o projeto tem proteção.
2. **Promoção** `AGUARDA_DONO` — produção bloqueia até o dono aprovar.
3. **`/casa`** responde por URL direto com os 43/44 (sem rota; o portão `VIEW_READS_ONLY_ITALY_CASA` proíbe-a de ler o pote). Medida e fotografada em cada publicação, **não bloqueia**. Tirá-la do deploy ou não: dono.
4. **D122 «Agenda»:** o nome da vista não foi mudado (o Radar Futuro mantém o nome). Aplicado: evento só com data (C0) e os 43/44 fora.
5. **D123 no clique:** provado nos dados (C0: produto + bula em toda OPORTUNIDADE); na tela as duas chaves aparecem no cartão (visto na foto do ensaio — a C5 não o confere); o **clique** caso→produto→bula no casco: NÃO SEI.
6. **Busca** do casco com pote: não medida (pode abrir um caso antigo).
7. Rótulo «AMBIENTE DIMOSTRATIVO» e a nota de demo no rodapé continuam (são avisos, não dados).
8. Vermelho herdado **N1** (72/73 na base) aceite por nome; se um dia passar, aparece no registo.
9. Merge em `release/canonical` → deriva (§1.1). Chamar o publicador depois de cada merge: dono.

**Design:** Claude Design **não consultado** (a missão proíbe sites externos). Nenhum componente novo: escondi uma
caixa existente, troquei números e acrescentei atributos `data-*`.
```
ADAMA_DESIGN_SYSTEM_MATCH = NAO SEI (nao consultado)
NEW_PATTERN_REQUIRED = NO
```

## 6 · Mapa

`correr_a_cadeia.py REGERAR` → `CADEIA=OK` · `VALIDAR` → **`SYSTEM_MAP_CHECK=PASS`** · commit ·
`impressao_da_arvore.py --conferir-carimbo` → **`IGUAL`**.

## 7 · O comando que o coordenador liga no agendador

Uma vez: `vercel login`, `vercel link` (projeto `sintonia-eame-preview`, time `london-creative`), `npm install --no-save playwright-core`,
`pip install pyyaml`. Depois de a branch chegar a `release/canonical` (o casco de lá ainda não lê o pote publicado —
até lá a C5 reprova, e nada vai ao ar).

**Ensaio (nunca sai da máquina):**
```bash
py portoes/publicar_portal_sozinho.py --pote italia-portale/client/sintonia-pote.js --modo ensaio
```
**Preview na Vercel (primeiro, para ver):**
```bash
py portoes/publicar_portal_sozinho.py --pote italia-portale/client/sintonia-pote.js --modo preview --arvore origin/release/canonical
```
**Agendador (Windows, a cada 30 min) — produção, depois de o dono aprovar a promoção:**
```bat
schtasks /create /sc minute /mo 30 /tn SINTONIA-PUBLICA-SOZINHO /tr "cmd /c cd /d C:\CAMINHO\eame-sintonia && git fetch -q origin release/canonical && py portoes\publicar_portal_sozinho.py --pote italia-portale\client\sintonia-pote.js --modo producao --arvore origin/release/canonical >> PUBLICACOES\agendador.log 2>&1"
```
Saídas: `0` publicado/nada a publicar · `1` bloqueado (nada foi ao ar) · `2` revertido (ALERTA) · `3` ALERTA_CRITICO.
O dono vê tudo em `PUBLICACOES/<data>/<hora>-<sha>/` (fotos `ANTES/` `DEPOIS/`, `REGISTO.json`, `POTE-PUBLICADO.js`,
`POTE-ANTERIOR.js`), `PUBLICACOES/ULTIMA-PUBLICACAO.json` (o ANTERIOR do DELTA da D125) e `PUBLICACOES/ALERTAS.jsonl`.

## EM PALAVRAS SIMPLES

Agora existe um «publicador» que faz sozinho o que antes esperava o dono olhar. Quando a Intelligence entrega um
pote novo, ele confere o pote, monta o portal que já existe com ele, abre cada tela num navegador e conta: cada tela
tem de mostrar exatamente o que o pote tem, e nenhuma das 43 oportunidades nem dos 44 futuros antigos. Só então
publica. Depois olha o site no ar; se algo não bate, volta sozinho para a versão anterior e grava um ALERTA. Cada
vez guarda fotos de antes e depois e o pote anterior com a sua impressão digital (SHA), fora do Git.

Foi tudo ensaiado **na máquina**, sem publicar nada: publicou, recusou o repetido, recusou o pote sem bula, voltou
sozinho quando a página no ar veio sem contagem, e gritou quando a volta não funcionou. Para ir à produção faltam
duas coisas: o **dono aprovar a regra de promoção** (hoje ela diz «aguarda o dono») e o **CLI da Vercel** logado na
máquina do coordenador — que aqui não existe, por isso a parte da Vercel está escrita mas **não testada**.
