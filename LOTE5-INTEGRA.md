# LOTE5-INTEGRA — comentários + busca no Actions + linha-busca sobre o lote 4 final (`18461b92`)

**Base:** `18461b92` (lote 4 final, fast-forward do vivo `2ef6fef8`, já com a bateria e o mapa).
**Ramo:** `claude/lote5-integra-merge-3320ja`. **SHA para fast-forward sobre `18461b92`:** ver §8 (o último
commit deste ramo; o relatório não consegue citar o próprio SHA).

## 1 · O que entra (lista exata)

| # | Ramo | Cabeça | Commits próprios | Como entrou |
|---|---|---|---|---|
| 1 | `origin/busca-no-actions-v1` | `e56b79c7` | 6 (`17a8b26`…`e56b79c`) + a história da linha-busca até `99eebc26` | merge `5adb9288` (1º commit da nuvem, sem conflito) |
| 2 | `origin/linha-busca-v1` | `0aec3898` | 3 novos sobre `99eebc26` (`e0586ce`, `641162e`, `0aec389`) | merge `9d7d2335` (1º commit da nuvem, sem conflito) |
| 3 | `origin/claude/comments-battery-tests-pt0d99` (contém `comentarios-v1`) | `a4423f26` | 11 (`c7d8118f`…`a4423f26`) | merge `98756872` (**feito aqui**; tinha conflito) |

Mais três commits desta missão:

- `62c793c8` — peças no mapa, prova no Postgres, script de mutação, mapa regerado;
- `71fb9714` — 2 testes de junção, mapa regerado;
- o commit deste relatório, com os resultados e o mapa regerado.

**Ordem declarada:** a missão pedia comentários → busca-no-actions → linha-busca. O 1º commit da nuvem
(`docs/nuvem/nuvem-lote5-integra-v1-MERGES.txt`) já tinha mesclado busca-no-actions e linha-busca e deixou comentários
pendente por conflito. Por isso ele entrou por último. Os três ramos não partilham ficheiro-fonte (§2), então a
ordem não muda o resultado.

## 2 · Conflitos — resolvidos pelo significado

O merge da bateria de comentários deu **15 conflitos, todos em ficheiros GERADOS**:

- `system-map/data/*.generated.json` (13);
- `italia-portale/client/system-map/state.generated.json`;
- `docs/fontes/INDICE-DE-FONTES.md` e `docs/operacao/CENSO-DAS-LIGACOES-DA-COLLECTION.md` (os dois dizem
  «Este ficheiro é gerado»).

**Resolução:** gerado não se mescla à mão. Ficou o lado HEAD, provisório, e a cadeia reescreveu-o
(`correr_a_cadeia.py REGERAR`, em `62c793c8`). Fontes, código, testes e docs escritos à mão mesclaram sem conflito.
`system-map/data/architecture.declared.json` auto-mesclou (lote 4 + as peças `C-ELEGIBILIDADE-COMENTARIO` e
`C-PROVA-COMENTARIOS`). A mutação J2-a prova que a peça de comentários sobreviveu ao merge.

**Junção de código:** só `coleta/linha_busca.py` foi tocado por dois ramos (busca-no-actions: `main()`,
`--sem-portao-it`, tesoura, transporte da API; linha-busca: `admitir(raw_asset_id)`, `colher --pousar` →
`linha_busca_raw.repousar`). O git mesclou sem conflito, e os dois lados estão presentes:

- `coleta/linha_busca.py:141` — `admitir(raw_asset_id)`;
- `coleta/linha_busca.py:284` — `colher --pousar` → `repousar`;
- `coleta/linha_busca.py:355` — a tesoura;
- `coleta/linha_busca.py:405` — `--sem-portao-it`.

**Dívida herdada, fechada aqui:** linha-busca e busca-no-actions vieram «SEM MAPA», com 30 ficheiros sem peça
(`P9_CODIGO_DECLARADO` FAIL). Declarei 4 peças em `system-map/data/architecture.declared.json`:

| Peça | Linha |
|---|---|
| `C-LINHA-BUSCA` | `:5893` |
| `C-LINHA-BUSCA-FERRAMENTAS` | `:5912` |
| `C-CI-LINHA-BUSCA` | `:5951` |
| `C-PROVA-LINHA-BUSCA` | `:5967` |

`mutacao_lote5_integra.py` entrou em `C-PROVA-COLETA`.

## 3 · Bateria INTEIRA por nome — base `18461b92` × ramo `71fb9714`

Mesmo executor e mesmo método do LOTE4-FINAL: `provas/integra_noite/bateria_inteira_por_nome.py`, 2 workers, com a
rede cortada por proxy morto. Cada lado correu numa worktree destacada. Resultados em
`provas/integra_noite/lote5-base-18461b92.json` e `lote5-ramo-71fb9714.json`.

| | base 18461b92 | ramo 71fb9714 |
|---|---|---|
| ficheiros de teste | 393 | 396 (+`test_comentarios_v1` 32, `test_linha_busca` 23, `test_busca_no_actions` 30 — todos verdes) |
| testes corridos | 7.378 | 7.463 |
| ficheiros vermelhos | 74 | 74 (os mesmos) |
| falhas por nome | 433 | 433 |

Pelo nome (as provas do system-map comparam-se sem os números): **432 herdadas · 0 consertadas · 0 NOVAS.**

**Herdada do lote 4, não consertada aqui (como manda a missão):** `tests/test_fundacao_da_coleta.py`:

- `test_nenhum_ficheiro_de_inteligencia_foi_tocado` → `['motor/v21_oportunidades.py'] != []`, o INDEPENDENCIA toca
  o motor congelado. Continua a ser decisão do dono (LOTE4-FINAL §3);
- `test_o_portal_nao_ganhou_implementacao` também falha, **idêntico na base**.

A mensagem é igual nos dois lados.

## 4 · A linha-busca num Postgres DESCARTÁVEL na máquina da nuvem

A prova é `provas/linha_busca_raw_no_postgres_descartavel.py`, com resultado em
`provas/integra_noite/lote5-prova-linha-busca-pg.json`. Os passos:

1. `initdb` novo (PG 16, com `runuser postgres` porque o initdb recusa root, `:47`), porto livre, banco `descartavel`;
2. o schema vem das migrations **do repo**, pela cadeia canônica (`:88`): **34 MIGRATION_*=PASS**;
3. os dados são SINTÉTICOS: a fixture `ferramentas/linha_busca/fixtures/teste`, colhida com transporte falso e a rede
   recusada;
4. corre `coleta/linha_busca_raw.py --repousar --pousar` **duas vezes** na mesma corrida (`:124`);
5. no fim para o cluster, apaga os dados e apaga exatamente os bytes que o `storage_object` registrou na árvore
   (no modo descartável, o dono do RAW escreve na árvore de propósito).

| Pergunta | Resultado |
|---|---|
| a corrida nasce | `collection_run`: `LINHA-BUSCA-RAW-SINTETICA-LOTE5 · HTTP direto · coleta/linha_busca.py · concluida` |
| o raw_asset nasce | 1 linha, 1 sha256 (`storage_object` 1) |
| o item pousa ligado ao raw | `sala_de_espera` 1 linha com `raw_observation_id`; join `raw_asset.id = raw_observation_id AND run_id = run_id` → **1** |
| a 2ª passada insere 0 | contagens iguais (1/1/1/1); a Sala diz `REUSED`, `INSERIDAS: 0` |

## 5 · Mutação dos pontos de junção — 10/10

O script é `provas/integra_noite/mutacao_lote5_integra.py`, com resultado em
`provas/integra_noite/mutacao-lote5-integra-RESULTADO.txt`. Corre numa worktree destacada. Cada assassino passa
limpo antes de receber o mutante.

| Mutante | O que planta | Quem mata |
|---|---|---|
| J1-a | `colher --pousar` pousa direto na Sala | `test_linha_busca` |
| J1-b | `--sem-portao-it` sem restrição | `test_busca_no_actions` |
| J1-c | a tesoura sai do erro | `test_busca_no_actions` |
| J1-d | a API usa o transporte de páginas | `test_busca_no_actions` (3) |
| J1-e | `RAW_ASSET_ID` = None | `test_linha_busca` |
| J3-a | pousa noutra corrida | Postgres: `sala_de_espera_run_id_fkey` |
| J3-b | salta o dono do RAW e inventa o id | Postgres: `sala_de_espera_run_id_fkey`, **o defeito original** |
| J2-a | some a peça `C-PROVA-COMENTARIOS` | validador do mapa |
| J2-b | some a peça `C-LINHA-BUSCA` | validador do mapa |
| J4-a | gerado velho (`18461b92`) | validador do mapa |

**A 1ª passada, sobre `62c793c8`, deu 8/10.** J1-a e J1-c ficaram VIVOS: nenhum teste provava essas duas junções.
Entraram 2 testes, **acrescentados**; nenhum teste existente mudou:

- `tests/test_linha_busca.py:281`;
- `tests/test_busca_no_actions.py:152`.

Depois deles, 10/10 em `71fb9714`.

## 6 · Mapa

- `correr_a_cadeia.py REGERAR` → `CADEIA=OK`;
- `VALIDAR` → `SYSTEM_MAP_CHECK=PASS`;
- `impressao_da_arvore.py --conferir-carimbo` → `IGUAL`.

Os valores finais estão em §8.

## 7 · Dependências

Postgres 16 (`/usr/lib/postgresql/16/bin`), PyYAML e node v22 estavam presentes. `psycopg2` não está instalado, e
não faz falta: a Sala e a memória falam pelo `psql`.

## 8 · Fecho

O SHA final e o carimbo estão na mensagem do último commit e no relatório da sessão. Aplicação:
`git merge --ff-only <SHA>` sobre `18461b92`.

## EM PALAVRAS SIMPLES

Juntei os três pacotes (comentários, busca pelo GitHub e a linha de busca que antes batia na trava do banco). As
brigas do merge eram só em ficheiros que a máquina gera, e a máquina gerou-os de novo.

Corri todos os testes antes e depois, nome por nome, e não apareceu nenhuma falha nova. A única falha conhecida do
lote 4 continua lá, igual, à espera da decisão do dono.

Num banco de verdade, criado do zero na nuvem e com dados de mentira, a linha de busca faz o que devia: registra a
corrida, guarda a página e só então põe o item na Sala, ligado a ela. Repetir não duplica nada.

Estraguei de propósito os 10 pontos onde os pacotes se encontram, e os testes pegaram todos. Nos dois primeiros que
ninguém pegava, escrevi o teste que faltava.
