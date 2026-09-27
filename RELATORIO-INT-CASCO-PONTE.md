# RELATÓRIO — PONTE INTELLIGENCE → CASCO (`nuvem-int-casco-ponte-v1`)

> **EXPERIMENTAL · NAO_PARA_CLIENTE.** Nada disto foi publicado. Nenhum deploy. Nenhum ficheiro do
> portal (`italia-portale/`) foi alterado. Base final = vivo **`2ef6fef8`** (data-do-fato, ff de 554c1ec1), por rebase limpo. PRONTO-SEM-MAPA.

## 1 · O que foi feito

Um **adaptador** que pega no livro de uma corrida da Intelligence já fechada e devolve **um payload com
as 12 ferramentas do casco**. Só atravessa o que tem prova, e a marca vai em tudo.

| o quê | onde |
|---|---|
| a marca `EXPERIMENTAL · NAO_PARA_CLIENTE` | `pacote/ponte_intelligence_casco.py:75` |
| prova = `ITEM_ID → RAW_OBSERVATION_ID → SOURCE_ID → DOCUMENT_ID` | `pacote/ponte_intelligence_casco.py:77` |
| as 12 ferramentas + chaves D84 de cada uma | `pacote/ponte_intelligence_casco.py:94` |
| vistas do casco que **não** são ferramenta (`sala`, `painel`) | `pacote/ponte_intelligence_casco.py:134` |
| linhagem com **todas** as entradas por `ITEM_ID` (defeito P1) | `pacote/ponte_intelligence_casco.py:155` |
| a prova tem de estar na LINEAGE da corrida, com G0 = PASSOU; ambígua → recusada | `pacote/ponte_intelligence_casco.py:170` e `:209` |
| cartão: chaves do contrato, `NAO SEI` por extenso, porquê/contradiz/incerteza | `pacote/ponte_intelligence_casco.py:215` |
| chave fora do contrato viaja **com valor**, à parte (defeito P4) | `pacote/ponte_intelligence_casco.py:232` |
| sinal sem ferramenta **não** ganha ferramenta (a ponte não escolhe) | `pacote/ponte_intelligence_casco.py:281` |
| só `EXPERIMENTAL_CANDIDATE` atravessa; nada se promove | `pacote/ponte_intelligence_casco.py:317` |
| portão de saída independente (marca, prova, `NAO SEI`, 12 ferramentas) | `pacote/ponte_intelligence_casco.py:365` |
| saída `.js` (global `window.SINTONIA_PONTE_EXPERIMENTAL`, **não ligado** ao `portale.html`) | `pacote/ponte_intelligence_casco.py:412` |
| **página local** `.html`: faixa fixa no topo + marca em cada cartão, texto escapado | `pacote/ponte_intelligence_casco.py:446` e `:465` |
| recusa escrever dentro de `italia-portale/` | `pacote/ponte_intelligence_casco.py:505` |
| testes (35) | `tests/test_ponte_intelligence_casco.py` |
| mutação (22 defeitos) | `provas/_mutantes_ponte_casco.py` |
| mapa declarado: `C-PONTE-INT-CASCO` (Z-PACOTE) e `C-PROVA-PONTE-CASCO` (Z-PROVA) | `system-map/data/architecture.declared.json:4374` e `:4394` |

**O contrato de entrada é NOVO e está declarado no próprio ficheiro.** Medido na base: a palavra
`EXPERIMENTAL_CANDIDATE` não existia no repositório nem na história do Git, e o motor
(`motor/corrida_da_inteligencia.py`) só produz `SIGNALS` com `ESTADO = SINAL`, sem ferramenta. A ponte aceita
esse livro (os sinais dele ficam em `RECUSADOS` com `SINAL_SEM_FERRAMENTA`) e declara o que o sucessor tem de
trazer: `ITENS_POR_FERRAMENTA`, `GAPS`, `SINTETICA`.

## 2 · As entradas de prova

| entrada | sha256 (16) | resultado |
|---|---|---|
| corrida sintética **declarada** (só no teste, ids `SINT-`, `SINTETICA: true`) | — | 3 cartões, recusas testadas uma a uma |
| coorte real versionada (`research/intelligence/COORTE-DA-SALA-2026-09-14.json`) pelo motor verdadeiro | — | bloqueia em G0 → **0 cartões**, lacunas visíveis (teste D1) |
| livro real da R2 `LIVRO-IR-7e570c9eff94e402c720.json` (fora do Git) | `6c7b95ded039aff9` | **0 cartões · 9 recusados** (`SINAL_SEM_FERRAMENTA`) · 3 lacunas |
| entrada real da R2 montada pelo bot da Intelligence `PARA-O-CASCO-R2/ENTRADA-DA-PONTE-R2.json` (fora do Git) | `097bff4eebb3606b` | **9 cartões · 0 recusados** · conferência = 0 violações |

Os 9 cartões reais: Finestre Colturali 1 (ARIF Puglia, semana 07–13/09/2026, `CROP/REGION/ISSUE = NAO SEI`;
«Puglia» vai em *fora do contrato* como `FACT_LOCATION`, **não** vira `REGION_ID`) · Polso di Mercato 6 ·
Intelligence Scientifica 2. As outras 9 ferramentas: 0 cartões, com o motivo escrito.

**Páginas locais geradas (fora do Git; dado real da Sala não entra no repositório):**

```
C:/tmp/ponte/pagina-r2-real.html     2d160900f18af834…   9 cartões, 10 marcas (1 faixa + 9)
C:/tmp/ponte/pagina-r2-livro.html    ac4ed0addf86d5a0…   0 cartões, 9 recusados
C:/tmp/ponte/pagina-sintetica.html   2cb466dcac3efc81…   3 cartões (sintéticos, marcados)
C:/tmp/ponte/payload-r2-real.json    1a6451f2216c779a…
```

## 3 · Testes — antes/depois, pelo NOME, rede fechada

Corredor `provas/boletins_data_local/testes_por_nome.py`, mesmo corredor nas duas árvores (cópia limpa do vivo
`278cd489` em `C:/tmp/ponte/base-278` × ramo), mesmos dados versionados, proxy numa porta morta.

| | base 278cd489 | ramo |
|---|---|---|
| módulos · testes | 62 · 848 | 62 · 848 |
| falhas | 79 | 79 |
| **falhas novas** | — | **0** |
| herdadas (iguais nome a nome) | `italy_contract_test.mjs` 77 · `test_collection_gate` 1 · `test_reconciliar_livros` 1 | as mesmas |
| `test_atomicidade_da_intelligence` | 104 falhas, 5 nomes | 104 falhas, os mesmos 5 nomes |
| espinha · modelo de objetos · primeira corrida · mapa da intelligence | verdes | verdes |
| `test_ponte_intelligence_casco` | não existe | **35/35** |

**Ajustes de teste declarados (dos meus próprios testes, nenhum da casa):**
`A6` — o valor fora do contrato passou a viajar (defeito P4). `C5` — `field` saiu da lista. `G1` — o casco no ar
passou a abrir 14 vistas (lote 2); `sala` e `painel` estão nomeadas no módulo, e uma vista nova sem declaração
volta a reprovar.

## 4 · Mutação — 22/22 mortos na ponte (31/31 com o esqueleto, §8)

Planta cada defeito numa cópia em pasta temporária (o repositório não é tocado) e corre os 35 testes.
Mortos: sinal sem prova atravessa · **cartão sem a marca** · conferência cega à marca · `NAO SEI` vira vazio ·
promoção de estado · prova fora da corrida · G0 ignorado · `DOCUMENT_ID` não exigido · corrida `ERROR` dá cartão ·
duplicado conta 2× · a ponte completa chave · escreve no portal · `NAO SEI` escondido passa · cartão sem prova
passa · lacunas somem · ferramenta sem contrato desenha · **página sem a faixa** · página sem escapar texto ·
P1 de volta · P4 de volta · `CORRIDA_UPSTREAM` ignorada · ambiguidade resolvida a favor do PASSOU.

## 5 · O que ficou por decidir (do dono) e o que NÃO SEI

1. **Duas portas para a mesma fronteira.** O lote 2 trouxe `italia-portale/audit/casco/INTELLIGENCE-EXPERIMENTAL-CONTRATO.json`
   (`CASCO_ENTRADA_INTELLIGENCE_EXPERIMENTAL/1`): por item da Sala (`<run_id>#<ordem>`), com EMENDA EXP-D78 e
   fotografia da Sala. Esta ponte é por ferramenta. **Não emiti o formato do casco**: não tenho a EMENDA nem a
   chave `<run_id>#<ordem>`, e preenchê-las seria fabricar. Qual das duas fica — decisão do dono.
2. **Esse contrato diz que a Intelligence está BLOQUEADA** e que a EMENDA EXP-D78 espera 2 assinaturas. A R2
   existe na mesma. Se estava autorizada: **NÃO SEI** (não é desta missão).
3. **Radar Futuro, Registro delle fonti, Archivio, Archivio segnali: sem contrato D84** → a ponte recusa cartão
   (P2, P3, P5 do bot da Intelligence). Os 10 factos sobre o futuro precisam de outra espécie de objeto.
4. **D84 não está escrita no repositório.** As chaves de cada ferramenta vêm do resumo do pedido da missão.
5. **Design:** os tokens vêm do extrato ADAMA ligado (não copiado). O Claude Design não foi consultado (sem rede
   externa). `ADAMA_DESIGN_SYSTEM_MATCH = NOT_FOUND` (no extrato local) · `NEW_PATTERN_REQUIRED = YES` para a faixa
   EXPERIMENTAL — se existe componente oficial equivalente: **NÃO SEI**.
6. **Portafoglio e Etichette** recebem o mesmo contrato T4 (D84 fala de «Portafoglio/Label» como um só).

## 6 · Erros meus, ditos

- A lista das 12 ferramentas saiu primeiro do inventário antigo (`casa`/`field`); corrigida para o casco no ar.
- A primeira bateria de testes (de manhã) correu **sem a LOCK-PESADO**. As medições que contam (secção 3)
  correram com ela, às 16:14.

## 7 · Mapa

**Estado final: PRONTO-SEM-MAPA sobre o vivo `2ef6fef8` (27/09, data-do-fato; rebase limpo de 9 commits sobre 554c1ec1 + 2; mesmos 171 testes leves verdes e mutação 31/31 sobre ele).**

- Sobre `278cd489` o mapa foi regerado e validado duas vezes: `SYSTEM_MAP_CHECK=PASS` e carimbo `IGUAL`
  (commits `4ebc6f06` e `780fa38a`, guardados no ramo local `backup/int-casco-ponte-780fa38a`).
- O vivo avançou para `554c1ec1` às 22:25. Os 7 commits de código foram reaplicados sobre ele **sem conflito**; os
  dois commits de mapa ficaram de fora, porque eram mapa de outra árvore.
- A regra nova da coordenação (`FILA-PESADO.md`, 22:05) diz que **o mapa não entra na fila** e que a INTEGRA o
  regenera uma vez por lote. Por isso **não corri a cadeia sobre `554c1ec1`**. As duas peças novas estão declaradas
  em `architecture.declared.json` (`C-PONTE-INT-CASCO`, `C-PROVA-PONTE-CASCO`) e entraram sem conflito.
- **Testes sobre `554c1ec1`:** leves, sim — ponte + esqueleto + espinha + modelo de objetos + primeira corrida =
  **171/171**; mutação **31/31**. A bateria pesada por nome (848 testes) **não** foi repetida sobre `554c1ec1`: a
  missão não está na fila do pesado. A última medida (sobre `278cd489`) deu 0 falhas novas. Os commits só
  **acrescentam** ficheiros que nenhum teste dessa bateria carrega; mesmo assim, para `554c1ec1` isso é **NÃO
  MEDIDO**.

## 8 · Adenda (ordem da coordenação 17:35) — esqueleto de «Intelligence Scientifica»

`pacote/esqueleto_scientifica.py` · testes `tests/test_esqueleto_scientifica.py` (11) · mutação +9 (E1–E9) →
**31/31** no total (o E4 sobreviveu na 1.ª volta — os campos IRIS e TRIAL_ID não eram olhados; teste A4b acrescentado).

**Natureza: PRE_SALA.** Material fora da Sala → **não é Intelligence** (INT-LAW-010), não passa pela ponte (não há
LINEAGE com G0) e diz isso na faixa da página.

| entrada (fora do Git) | sha256 (16) |
|---|---|
| `CRUZAMENTO-MUR-AGRI05.json` (ramo `lista-mestra-v1` @ `d225efa2`, lido por `git show`) | `afa712f6195f25da` |
| `pesquisadores-t6/foto-final/UNIDADES-T6.json` — **589** obras (= `FOTO-FINAL.sha256`) | `25cbc1e7dd3a263e` |
| `T6-PRE-MEDICAO/PRE-MEDICAO-CAP-SCI.json` — mediu **432** obras (versão ANTERIOR, sha `3279488a…`) | verificado pelo SHA256SUMS da pasta |

Regras: **tema** = par que está na consulta **e** no texto (nunca só pela cultura) · **pesquisador** = identidade do
MUR, ligado ao estudo **só** pelo OPENALEX_ID que a lista mestra provou · `SO_NOME` (4) fora, com o motivo ·
`VARIOS_IDS` sem fundir · publicação ≠ período do estudo · afiliação ≠ local do estudo · **independência não se
calcula**: aparece a da pré-medição, com a base escrita («432, não as 589»).

Resultado (página local `C:/tmp/ponte/esqueleto-scientifica.html`, `47d7da1ef9f72d06…`):
12 temas · 119 pesquisadores MUR distintos · 55 obras sem tema do casco no texto. Pesquisadores por tema **iguais**
à tabela da `LISTA-MESTRA-PESQUISADORES.md` (vite×peronospora 49 · pomodoro×botrite 44 · vite×scafoideo 34 ·
vite×botrite 31 · vite×oidio 24 · vite×tignoletta 15 · pomodoro×peronospora 12 · mais×piralide 9 · mais×diabrotica 5 ·
melo×carpocapsa 2 · pomodoro×oidio 1 · melo×oidio 1). BOSCO Domenico (Ordinario, Torino): 14 estudos em vite×scafoideo.

⚠️ Em pomodoro×botrite a pré-medição contou 3 obras; a foto tem 74. A independência dessa linha é de outra base, e a
página diz qual. Refazer a pré-medição sobre as 589 é do dono dela, não desta missão.

**A atualizar depois da rodada desta noite:** a página experimental da ponte (§2) com a nova saída da Intelligence.

## EM PALAVRAS SIMPLES

A Intelligence é a cozinha; o portal é a vitrine. Eu fiz o **garçom** que leva o prato da cozinha para a vitrine.

- Ele só leva prato que tem **nota fiscal** (a prova, até o documento de onde veio). Prato sem nota fica na
  cozinha, com um bilhete dizendo por quê.
- Todo prato vai com uma **etiqueta vermelha**: «EXPERIMENTAL — não é para o cliente». Tirar a etiqueta faz o
  teste falhar (provei plantando esse defeito de propósito).
- O garçom **não cozinha**: não inventa ingrediente, não completa o que falta. Onde a cozinha não sabe, ele
  escreve «NÃO SEI» bem grande.
- Com a comida de verdade da rodada 2: **9 pratos na vitrine**, todos com nota e etiqueta. Nada foi publicado:
  a vitrine é uma página só no seu computador.
- O que muda para você: há **duas portas** para a cozinha falar com a vitrine (a minha e uma que o lote 2
  trouxe). Alguém tem de escolher uma.
