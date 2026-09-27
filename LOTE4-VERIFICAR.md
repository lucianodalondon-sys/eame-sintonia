# LOTE4-VERIFICAR — bateria inteira, cadeia do mapa, achados

Ramo `claude/lote4-verificar-ekdj83`, a partir de `abe77c39` (integra-noite-v4, lote 4 junto). Base de comparação:
o vivo **`554c1ec1`**. Máquina da nuvem (Linux, Python 3.11.15, Node 22.22.2, PyYAML presente), rede fechada nos
testes (proxy numa porta morta, como `testes_por_nome.py`).

## 1 · Bateria INTEIRA, por nome

Não a lista curada: **todo** ficheiro de teste rastreado — `test_*.py` / `*_test.py` em qualquer pasta, `provas/testa_*.py`,
`*_test.mjs` e `system-map/tests/*.mjs`; cada um corrido a partir da raiz (`python3 <f>` / `node <f>`), falha lida pelo
nome (`FAIL:`/`ERROR:`), e ficheiro sem nome de teste conta pelo código de saída.
Resultados: `provas/integra_noite/lote4-verificar-base-554c1ec1.json` e `…-ramo-abe77c39.json`.

| | base 554c1ec1 | ramo abe77c39 |
|---|---|---|
| ficheiros de teste | 373 | 388 (+15 do lote 4) |
| testes corridos | 6.967 | 7.237 |
| ficheiros vermelhos | 77 | 80 |
| falhas por nome | 158 | 163 |

**158 herdadas** (mesmo nome nos dois lados) · **0 consertadas** · **5 novas**. As 5 foram re-corridas sozinhas
(sem paralelismo) em `abe77c39` e no HEAD com o mapa regerado:

| # | falha nova | causa | no HEAD final |
|---|---|---|---|
| 1 | `tests/test_o_controle_separa_lei_de_mencao.py::test_M5_o_ponto_fixo_existe_e_esta_alcancado_nesta_arvore` | o mapa commitado estava atrás da árvore (o lote 4 entrou sem regerar) | **PASSA** (mapa regerado, §2) |
| 2–3 | `tests/test_pesquisadores_t6.py::test_registo_orcid_e_t6_com_ou_sem_instituicao_no_nome` e `::test_a_ficha_da_candidata_passa_pelo_qualify_como_t6` (`'NAO SEI' != 'T6'`) | **DEFEITO REAL** — choque lista-mestra × concorrenza (a decisão 3.3 do INTEGRA-NOITE-LOTE4.md): a regra T6 exige o iD no caminho, `curadoria/atribuir_source_id.py:70`, e `_nome_e_casa` (`curadoria/atribuir_source_id.py:96-111`) só entrega nome + host | FALHA — não consertado (é decisão do dono) |
| 4 | `tests/test_a_porta_cli_liga_o_banco.py::test_1_nenhum_modulo_de_runtime_importa_provas` | **DEFEITO REAL, não visto antes** — runtime importa `provas/` por nome nu: `coleta/rota_navegador.py:143` e `coleta/espera_por_dominio.py:44` (scrap-evolucao) e `coleta/reserva_24h.py:37` (contador-24h), todos `import prova_teto_dominio`. O teste já existia na base; a bateria curada do lote 4 não o corria | FALHA — não consertado |
| 5 | `tests/test_contador_24h.py::test_prova_adversarial_A1_a_A4` | **DEPENDÊNCIA EM FALTA: o launcher `py`** — `provas/contador_24h_local.mjs:75` faz `spawn("py", …)`; em Linux não há `py` (`spawn py ENOENT`). Com um shim declarado `py → python3` no PATH (só para medir, fora do repo) o teste passa (17/17) | FALHA aqui por ambiente; no Windows NÃO SEI (não corri lá) |

A falha da cópia (`test_comunicacao_concorrenza.test_561`, lida em `build/`) **não** aparece: esta bateria corre em
worktree com a árvore inteira — 31 testes, verde.

**Depois do conserto do mapa**, `system-map/tests/*` re-corridos no HEAD `368b0b4`: as provas reprovadas pelo nome
(`reprovada(s): …`) são **as mesmas da base** (`test_system_map` 11 = 11, `test_cadeia_declara_io` 2 = 2,
`test_base_da_auditoria` 1 = 1, `test_topologia_persistida` 2 = 2). `test_impressao_verificavel` saiu vermelho na corrida
paralela (outro teste regerou `architecture.generated.json` na mesma worktree) e **sozinho passa: 102 provas, 0 falhas**.
Limite desta comparação: 5 ficheiros do system-map (`test_ordem_por_dependencia`,
`test_quatro_planos`, `test_reconciliacao_do_universo`, `test_verdade_da_collection_actual`, `verificar_a_tela.mjs`)
não escrevem nomes legíveis — já eram vermelhos na base e compararam-se **só pelo código de saída**: pelo nome, NÃO SEI.

⚠️ **Achado de integração:** o `t6-para-sala-v1` está no INTEGRA-NOITE-LOTE4.md como **FORA**, mas **entrou**: o
`lista-mestra-v1` (`3f7b43ef`) contém `ff9ba9f2` (`git merge-base --is-ancestor ff9ba9f2 3f7b43ef` = sim). Estão na
árvore `coleta/pesquisadores_t6_executor.py`, `ferramentas/t6_para_sala/*`, `provas/o_pedido_t6_atravessa.py`,
`provas/ensaio_t6_na_copia_da_sala.py`. Decisão do dono: aceitar ou tirar.

## 2 · A cadeia do mapa

1. `correr_a_cadeia.py REGERAR` → `CADEIA=OK`.
2. `VALIDAR` → **FAIL**: `P9_CODIGO_DECLARADO`, 14 ficheiros de código do lote 4 sem peça (o validador só mostra 10;
   a lista inteira vem de `state.generated.json → UNCLAIMED_CODE_FILES`).
3. Conserto **só de mapa** em `system-map/data/architecture.declared.json` — 6 peças novas e 3 ficheiros em peças
   existentes, cada uma na gaveta do seu ficheiro:
   - `C-PESQUISADORES-T6` (Z-ACOES): `coleta/pesquisadores_t6.py`, `coleta/pesquisadores_t6_executor.py`
   - `C-LISTA-MESTRA-MUR` (Z-ACOES): `coleta/lista_mestra_mur.py`
   - `C-CONTADOR-24H` (Z-ACOES): `coleta/reserva_24h.py`
   - `C-PROVA-CONTADOR-24H` (Z-PROVA): `provas/contador_24h_{executor,local}.mjs`, `provas/contador_24h_mutacao.py`
   - `C-PROVA-T6-ATRAVESSA` (Z-PROVA): `provas/o_pedido_t6_atravessa.py`, `provas/ensaio_t6_na_copia_da_sala.py`
   - `C-T6-PARA-SALA-MEDIDAS` (Z-FERRAMENTAS): `ferramentas/t6_para_sala/*.py`
   - `+ C-SEGUIR-PESQUISADORES`: `…/fixtures/pagina-rossi.html` · `+ C-PRECO-DE-MERCADO`: `scripts/polso_mercato/medir_fixtures.py`
     · `+ C-TESTES`: `tests/fixtures/pesquisadores_t6/montar.py`

   **Sem `--stamp`**: as frases foram escritas pela leitura do topo de cada ficheiro, por agente — a leitura humana fica
   por fazer, e as peças ficam 🟡 PENDING, que é a verdade.
4. `REGERAR` → OK · `VALIDAR` → **`SYSTEM_MAP_CHECK=PASS`** · commit dos gerados · `impressao_da_arvore.py
   --conferir-carimbo` → **`IGUAL`**. Este relatório é fonte rastreada: a cadeia corre outra vez depois dele (§4).

## 3 · Mutação

| mutante (numa worktree à parte, nunca publicado) | quem apanha | |
|---|---|---|
| tirar a peça `C-CONTADOR-24H` | `P9_CODIGO_DECLARADO` FAIL | MORTO |
| pôr `ferramentas/t6_para_sala/medir_modelos_resistencia.py` numa peça de Z-ACOES | `P2_PASTA_BATE_COM_MAPA` FAIL | MORTO |
| mudar um ficheiro rastreado e commitar sem regerar | `--conferir-carimbo` = `DIFERENTE` | MORTO |
| `provas/contador_24h_mutacao.py` (10 mutantes do código do contador; com o shim `py`) | `tests/test_contador_24h.py` | **10/10 MORTOS** |

Sem o shim a mutação do contador nem começa («a cópia limpa não passa») — a mesma falta do `py` da linha 5.

## 4 · Estado

Nada de código do lote 4 foi alterado; nenhum teste foi mexido; livros vivos intocados.
**Falta, para o lote 4 ficar PRONTO:** decisão 3.3 (ORCID/T6), os três `import prova_teto_dominio` do runtime
(mover a regra `dominio_registavel` para uma gaveta de runtime, ou declarar a dívida — decisão de quem é dono),
`py` em `provas/contador_24h_local.mjs:75`, e o t6-para-sala que entrou sem ser pedido.

## EM PALAVRAS SIMPLES

Corri todos os testes do projeto na versão de antes e na versão do lote 4 e comparei nome por nome. Das 5 falhas novas,
uma era só o mapa atrasado — regerei o mapa e ela sumiu. Sobram 4 que são problemas de verdade e ficam para o dono:
a regra que manda o ORCID para T6 foi desfeita por outro pacote (2 testes); três ficheiros de coleta passaram a
depender de uma pasta de provas, o que a regra do projeto proíbe; e uma prova chama o programa `py`, que só existe
no Windows. O mapa agora conhece os 14 ficheiros novos e passa no validador. E um pacote que devia ficar de fora
(t6-para-sala) entrou escondido dentro de outro.
