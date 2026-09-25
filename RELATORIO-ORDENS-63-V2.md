# RELATÓRIO — ORDENS-63 v2 · D52 aplicada (em cópia)

Ramo `ordens-63-v2`, a partir de `ordens-63-v1 @ 7648c995`. **Não instalado.** Rede: 0 pedidos.

**D52 (bot Luciano):** as 62 = `RETIRADA_POR_DECISAO` (a marca da D9), por SOURCE_ID, nunca o domínio
`conaf.it` inteiro; nada apagado; reversível; cada uma com a sua prova; deixam de ser tentadas; voltam pelo
circuito do Curator. Palermo (IT-T7-226) fica activa.

## O caminho canónico

| peça | ficheiro:linha |
|---|---|
| a marca (a da D9) | `ESTADO_CATALOGO = RETIRADA_POR_DECISAO` + `CATALOGO_D9` no contrato do curador — a forma que o G1 escreveu (`scripts/desbloqueio/aplicar_desbloqueio.py:391`) |
| quem já a lia | `curadoria/collection_gate.py:144` (portão) · `regras/italy_contracts.mjs:677` (tabela do coletor) · `scripts/coorte_micro/funil.py:185` (micro) |
| a porta que a põe e a tira | `curadoria/retirar_por_decisao.py` — `aplicar` :64, `reverter` :95, a leitura única `retirada` :50 |
| a decisão, com a prova de cada uma | `curadoria/DECISAO-D52-RETIRAR-V1.json` — 62 SOURCE_ID, cada uma com o seu `EVIDENCE_REF` do robô (`EV-…-REPAIR_CONTRACT-…`), motivo, retrato da entrada e páginas lidas (gerado por `scripts/ordens_63/gerar_d52.py`) |
| o reparo automático deixa de as tentar | `curadoria/gatilho_discovery.py:341` |
| a alimentação à mão também as salta | `curadoria/alimentar_fila.py:50,55,63` — sem lhes escrever contrato novo («tem contrato» continua a contá-las) |

O G1 aplicou-se uma vez, no cutover; não havia porta para marcar depois. Esta é a mesma marca, com as mesmas
regras: só as fontes da decisão; só as duas chaves; o livro nunca ganha nem perde fontes.

## ⚠️ As 62 não estão no livro do curador DESTE repositório

Estão só no livro **vivo** (vieram da FILA-UNICA depois do corte). Por isso a D52 não é uma edição de ficheiro
neste ramo: é um comando a correr no vivo, na instalação (plano abaixo). Nenhuma está na tabela do coletor.
**0** observações delas no livro de coleta: a D2 (gaveta certa) não tem nada a mover.

## Testes e mutação

- `curadoria/test_retirar_por_decisao.py` **11/11**: a decisão tem 62 com prova própria; só as 62 mudam e só na
  marca; as 10 outras do `conaf.it` e Palermo não mudam; idempotente; reverter devolve os mesmos bytes (também em
  CRLF, como o vivo); outra marca não é pisada nem revertida; o invariante apanha campo fora da marca e marca em
  fonte fora da decisão; o gatilho deixa de as propor (as outras continuam); a alimentação à mão salta-as.
- `test_gatilho_discovery`, `test_abastecimento`, `test_impasse_b4`, `test_reparar_contrato`, `test_canario_detalhe`,
  `test_contrato_unico`: verdes; `tests.test_retirada_por_decisao` (D9): 4/4.
- **Mutação 8/8** (`scripts/ordens_63/MUTACAO-D52-V1.json`, cópia `C:/capa-base`). Um mutante morreu na 1.ª
  corrida pela razão errada (partia a sintaxe) — corrigido e repetido; agora cai no teste certo.

## Ensaio em cópia do vivo, rede fechada — `scripts/ordens_63/ENSAIO-D52-V1.json`

| medida | resultado |
|---|---|
| fontes no livro vivo copiado | 801 |
| mudaram | **62**, exactamente as da decisão |
| fontes `conaf.it` no livro / fora das 62 | 69 / 10 — **nenhuma das 10 mudou** |
| gatilho hoje (reparos DONE) | propõe 0 das 62 |
| gatilho com o último reparo das 62 FAILED há 2 dias (simulado) | **62 antes → 0 depois** |
| 2.ª corrida | igual (idempotente) |
| reverter | **sha256 igual ao original** |

## Plano de instalação — NÃO instalar

1. Instalar o código (writeset abaixo) pelo caminho normal (integração).
2. Guardar o livro vivo: cópia de `curadoria/italy_contracts_curator.json` + sha256.
3. Relatório sem escrever: `py curadoria/retirar_por_decisao.py --decisao D52` → deve dizer `{'APLICA': 62}`.
4. Aplicar: `py curadoria/retirar_por_decisao.py --decisao D52 --escrever`.
5. Conferir: 62 com `ESTADO_CATALOGO`; as 10 outras `conaf.it` iguais; o resto igual.

⚠️ O worker regrava este livro: aplicar com o robô parado (ou entre voltas), como no G1.

**Desfazer:** `py curadoria/retirar_por_decisao.py --decisao D52 --reverter --escrever` (tira só a marca da D52; o
livro volta byte a byte), ou repor a cópia do passo 2. O código novo sem a marca não muda nada: as travas só olham
para fontes marcadas.

**Writeset:** `curadoria/retirar_por_decisao.py` · `curadoria/DECISAO-D52-RETIRAR-V1.json` ·
`curadoria/gatilho_discovery.py` · `curadoria/alimentar_fila.py` · `curadoria/test_retirar_por_decisao.py` ·
`scripts/ordens_63/gerar_d52.py`, `mutar_d52.py`, `ensaio_d52.py` + `MUTACAO-D52-V1.json`, `ENSAIO-D52-V1.json` ·
relatórios.

## ⚠️ Erro meu, em duas entregas anteriores

- ORDENS-63: «o robô tenta repará-las a cada 24 h» — falso (correcção no relatório v1).
- **RECEITAS-182: «depois de instalado, o robô volta sozinho a tentar as 183»** — falso pela mesma razão: as 183 têm a
  tarefa de reparo DONE. Depois de instalar o conserto da RECEITAS-182, alguém tem de **enfileirar REPAIR_CONTRACT**
  para as fontes que se quer remedir (no mínimo as 4 medidas + Palermo; as 22 «lista com molde errado» para ver
  todas). Sem isso o conserto não é usado.
