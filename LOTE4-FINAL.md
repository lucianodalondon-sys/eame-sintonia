# LOTE4-FINAL — o lote 4 integrado sobre o vivo `2ef6fef8` (DATA-DO-FATO)

Ramo `claude/lote4-final-integration-l02r5q`, a partir de `integra-noite-v4 @ 1c7b154f`. Máquina da nuvem (Linux,
Python 3.11.15, Node 22.22.2, PyYAML presente), rede fechada nos testes (proxy numa porta morta). Livros vivos
intocados (`git diff --name-only 2ef6fef8 HEAD` não tem `curadoria/*-V1.json`, `data/collection-ledger`, nem
`candidatas/FONTES-CANDIDATAS.json`).

## 1 · A junção com `2ef6fef8`

**Já estava feita** no ramo: `d8839907` («junta vivo-data-do-fato 2ef6fef8»). `git merge-base --is-ancestor 2ef6fef8
HEAD` = sim → **instalável por fast-forward sobre `2ef6fef8`**. Nada perdido, medido ficheiro a ficheiro sobre o que o
`2ef6fef8` mudou desde `554c1ec1`: os 9 ficheiros de código/dados (`leis/fato_do_texto.py`, `scripts/lugar_fato/*`,
`tests/dados/data-do-fato/*`…) são **byte a byte iguais** no HEAD; os outros 14 são gerados do mapa (regerados aqui)
e `architecture.declared.json`, onde as 5 entradas novas da DATA-DO-FATO estão presentes (1 vez cada).

## 2 · O que entra (lista EXATA)

| # | pacote | SHA | dentro do HEAD |
|---|---|---|---|
| 0 | vivo-data-do-fato (o vivo) | `2ef6fef8` | sim (base do ff) |
| 1 | contador-24h-v1 | `4552a305` | sim |
| 2 | scrap-evolucao-v1 (peça 6 DESLIGADA) | `3103f723` | sim |
| 3 | lista-mestra-v1 | `3f7b43ef` | sim |
| 3a | t6-para-sala-v1 (dentro do lista-mestra; DA-21 1: FICA) | `ff9ba9f2` | sim |
| 4 | pesq-fora-do-mur-v1 | `389f9879` | sim |
| 5 | nuvem-polso-mercato-v1 | `89020be4` | sim |
| 6 | nuvem-voci-campo-v1 | `7c975a9c` | sim |
| 7 | nuvem-concorrenza-v1 | `778c21ff` | sim |
| 8 | nuvem-independencia-v1 | `eb3a7b1d` | sim |
| 9 | intelligence-bridge-v2 (pote único v2) | `ce775ff5` | sim |
| 10 | concurrency-meta-collection (Meta Ads recorrente) | `d447a47f` | sim |
| DA-21 (2) | ORCID → T6 sem perder o conserto do concorrenza | `3115bfcd` | sim |
| DA-21 (3) | o runtime não importa `provas/` (`coleta/dominio_registavel.py`) | `a6c7dfca` | sim |
| DA-21 (4) | `provas/contador_24h_local.mjs` sem `py` fixo | `1bdca628` | sim |
| — | micro-prova-lote2b-v1 | `005a24cd` | **FORA** (conflito de código, sem decisão) |
| — | lei-pesquisadores-v1 | `94524616` | **FORA** (conflito de código, sem decisão) |

Migrações: **nenhuma**. Commits desta missão (só mapa, prova e relatório; **nenhum código de runtime mexido**):
`a7acbed6` mapa regerado · `495c577b` mutação · `d8f0fde2` mapa regerado · o commit deste relatório (+ mapa).

## 3 · Bateria INTEIRA por nome — base `2ef6fef8` × ramo `d8f0fde2`

Todo ficheiro de teste rastreado (`test_*.py`/`*_test.py`, `provas/testa_*.py`, `*_test.mjs`, `system-map/tests/*.mjs`),
corrido da raiz; `system-map/` um de cada vez. Executor: `provas/integra_noite/bateria_inteira_por_nome.py`.
Resultados: `provas/integra_noite/lote4-final-base-2ef6fef8.json` e `…-ramo-d8f0fde2.json`. O nome de uma prova do
system-map compara-se sem o detalhe (os números que ela imprime crescem com a árvore).

| | base 2ef6fef8 | ramo d8f0fde2 |
|---|---|---|
| ficheiros de teste | 374 | 393 (+19 do lote 4) |
| testes corridos | 6.981 | 7.378 |
| ficheiros vermelhos | 74 | 74 |
| falhas por nome | 414 | 415 |

**414 herdadas · 0 consertadas · 1 NOVA:**

- `tests/test_fundacao_da_coleta.py::test_nenhum_ficheiro_de_inteligencia_foi_tocado` —
  `INTELLIGENCE_IMPLEMENTATION != 0: ['motor/v21_oportunidades.py']`. **Causa:** o pacote **nuvem-independencia-v1**
  (`eb3a7b1d`, commit `6b577706`) acrescenta ~40 linhas ao motor V2.1 (`motor/v21_oportunidades.py:237-255`,
  `:733-752`, `:762-769`, `:1028-1040`, `:1089-1098`: `TIPOS_ESTRUTURAIS`, `dependencia`, teto por originador). O teste
  (`tests/test_fundacao_da_coleta.py:79-82`) mede o diff contra `origin/claude/italia-biblia-integracao-v1`
  (`:23`); no LOTE4-VERIFICAR esse ref não existia na máquina (lá falhava `test_a_base_de_comparacao_existe`, isto é,
  **não mediu**); aqui existe nos dois lados, por isso a base é comparável e o teste mede. **Não consertado** — é
  decisão do dono: ou o INDEPENDENCIA tem licença para tocar o motor congelado (e o teste é de uma missão antiga e se
  atualiza DECLARADO), ou o pacote sai. `RELATORIO-INDEPENDENCIA-FONTES.md:40` declara a mudança no motor; nenhuma
  autorização do congelamento está citada lá.

As 4 falhas reais do LOTE4-VERIFICAR **passam** no ramo: `test_pesquisadores_t6` 24/24, `test_a_porta_cli_liga_o_banco`
23/23, `test_contador_24h` 17/17 em Linux (sem shim `py`), `test_M5_o_ponto_fixo…` verde.

Nota: `system-map/tests/test_cadeia_declara_io.py::toda_leitura_real_e_explicada…` falha nos dois lados com o
MESMO conjunto de órfãs (5 = 5, re-corrido com a lista inteira), mas a CONTAGEM varia entre corridas (5/10/11/12) —
a prova é instável; herdada, não desta integração.

## 4 · Cadeia do mapa

`correr_a_cadeia.py REGERAR` → `CADEIA=OK` · `VALIDAR` → **`SYSTEM_MAP_CHECK=PASS`** · commit dos gerados ·
`impressao_da_arvore.py --conferir-carimbo` → **`IGUAL`** (medido em `a7acbed6` e `d8f0fde2`; corre outra vez depois
deste relatório, que é fonte rastreada). Os 2 ficheiros novos (`mutacao_lote4_final.py`,
`bateria_inteira_por_nome.py`) ficam na mesma peça que `mutacao_da21.py`.

## 5 · Mutação dos 4 consertos da DA-21

`provas/integra_noite/mutacao_lote4_final.py` → `mutacao-lote4-final-RESULTADO.txt` (numa worktree à parte; cada
ficheiro reposto, sha256 conferido; a cópia limpa passa antes): **7/7 MORTOS**.

| mutante | teste que apanha |
|---|---|
| O1 regra ORCID→T6 desligada · O2 ORCID lê só nome + casa · O3 todas as regras voltam a ler o endereço inteiro | `test_pesquisadores_t6` + `test_comunicacao_concorrenza` (2 falhas cada) |
| D1 `coleta/reserva_24h.py` · **D2** `coleta/rota_navegador.py` · **D3** `coleta/espera_por_dominio.py` voltam a importar `provas/` | `ORuntimeNaoImportaProvasEHaUmAdaptador` (1 falha cada) |
| **P1** `provas/contador_24h_local.mjs` volta a `const PY = "py"` | `test_contador_24h::test_prova_adversarial_A1_a_A4` — `spawn py ENOENT` (Linux) |

D2, D3 e P1 são novos (a mutação da DA-21 só tinha D1 e nenhum mutante do conserto 4). O «NÃO SEI» do conserto 4 em
Linux fecha-se: limpo passa, mutado morre.

## 6 · PRONTO

**PRONTO = a ponta da branch `claude/lote4-final-integration-l02r5q`** (o commit deste relatório + o mapa regerado;
o SHA vai no fecho da missão — um ficheiro não carrega o SHA do commit que o contém). Instalável por
`git merge --ff-only` sobre `2ef6fef8`. Plano de instalação: `INTEGRA-NOITE-LOTE4.md §6` (inalterado).
**Condição aberta:** a 1 falha nova (§3, independencia × motor congelado) — o coordenador aceita-a declarada ou tira
o pacote 8 antes de instalar.

## EM PALAVRAS SIMPLES

O lote 4 já tinha a versão de produção nova dentro, e nada dela se perdeu. Corri todos os testes do projeto na
produção e no lote 4 e comparei nome por nome: só aparece uma falha nova — o pacote «independência» mexe num
ficheiro do motor de inteligência que está congelado, e há um teste que vigia isso. Não mexi: é decisão do dono. Os
quatro consertos da DA-21 funcionam e os testes apanham quando alguém os desfaz (7 de 7 sabotagens apanhadas). O mapa
passa no validador e o carimbo bate.
