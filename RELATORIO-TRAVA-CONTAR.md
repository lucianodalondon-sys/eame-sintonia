# RELATÓRIO — TRAVA-CONTAR (D57 / D59)

Ramo `trava-contar-v1`, a partir da produção `origin/servico-20260923-0923 @ df0865e6`. **Não instalado.**
Sem Intelligence: nada de motor, sinal, hipótese, finding, oportunidade, Casco ou Portal. A trava
(`docs/operacao/TRAVA-DA-INTELIGENCIA.json`) não foi editada. Sala não consultada. Vivo, produção e travas
(LOCK-*) não tocados. Rede fechada (proxy para 127.0.0.1:9 em todos os testes).

## 0 · Em uma linha

**A trava continua FECHADA.** Com as corridas de hoje contadas pelo resumo auditável (D59), o critério A passa de
**98 para 103** fontes com caminho provado (de 716) — e continua NÃO. A..N: **4 SIM · 8 NÃO · 2 sem medidor**
(igual). Condições de destrave: **1 de 5** (a 4.ª), e as outras 4 NÃO.

## 1 · Os medidores consertados, trazidos pela evidência (não junção cega)

`trava-medidores-v1 @ c821094d` sobre `df0865e6` (base comum `9848152c`):
- **código que os medidores mudam:** `system-map/scripts/censo_das_estradas_it.py`, `system-map/scripts/censo_do_congelamento.py`,
  `system-map/scripts/CADEIA-DO-MAPA.json` — a produção **não tocou** em nenhum dos três depois da base;
- **o único ficheiro mexido dos dois lados:** `tests/test_egresso_consenso.py` — o Git juntou sozinho; **26/26** na junção e na produção;
- **conflitos:** 14, **todos ficheiros gerados** (`*.generated.json`, `CENSO-DAS-LIGACOES-DA-COLLECTION.md`) — ficou o lado da
  produção; a cadeia do mapa regenera-os;
- **testes dos medidores:** na produção sem eles **FALHAM** (1 falha, 7 erros — `provas/medidores-ANTES.txt`); na junção **23/23**
  (`medidores-DEPOIS.txt`);
- **vizinhos** (`test_estradas_it` + `test_trava_da_inteligencia`, 35): **as mesmas 2 falhas** antes e depois — as violações reais do
  congelamento (N);
- **red team dos medidores sobre a produção:** o ensaio de mutação deles (`data/derivados/TRAVA-MEDIDORES-V1/mutacao.py.txt`) na cópia
  `C:/capa-base` com a junção: **21 de 21 mortos**, bytes repostos e conferidos (`provas/mutacao-medidores-sobre-producao.txt`).

## 2 · O resumo auditável da onda (D59)

**`ferramentas/big_collection/resumo_da_onda.py`** lê, só leitura, o que a onda já escreveu:
`ONDA-WEB-ESTADO.json` (linha de cada fonte) e `<fonte>/RELATORIO-PASSAGEM.json` (o relatório **daquela** corrida:
RAW = `CONTAGENS.RAW_CREATED`, DERIVED = `C4.COM_DERIVADO`, proveniência = `C4`, veredictos = `C7`). O relatório só vale se
o `RUN_IDS` dele for o da linha; senão é recusado e o número fica **UNKNOWN**. Escreve
`ferramentas/big_collection/ondas/<ONDA>-RESUMO.json`: RUN_ID, SOURCE_ID, STATUS, RAW, DERIVED, proveniência, veredictos
da Admission, GATE, EGRESSO, pedidos por domínio, porta e executor (lido no código: `coleta/italy_executor.py`), sha256 do
estado e de cada relatório. **Sem bytes, sem texto, sem DSN, sem caminhos de livros** (testado).

**`onda_web.py`** passa a gravar `RAW` e `DERIVED` na linha de cada fonte (como o disparador da 1.ª onda) e a escrever o
resumo no fim da onda e quando um disjuntor a pára. Se o resumo falhar, a onda não se desfaz: diz-se, e refaz-se depois.

**Os resumos de hoje** (gerados das pastas, só leitura): MICRO-V3 **6 corridas**, 2.ª onda **21 corridas** — **0 com RAW
UNKNOWN**: todas têm o relatório da própria corrida.

## 3 · O medidor lê os resumos pelo dono certo, e confere cada linha

Dono: `system-map/scripts/censo_das_estradas_it.py` (`provas_dos_resumos`, `conferir_linha`). Uma linha só prova estrada
se **todas** passarem, pela ordem: correu · STATUS SUCCESS · RAW e DERIVED números (UNKNOWN não) · RAW ≥ 1 e DERIVED ≥ 1 ·
proveniência inteira · **RUN_ID existe no livro de corridas do coletor** · o livro não diz FAILED · **RAW igual a
`RAW_OBJECTS_CREATED` do livro** · **a fonte aparece no livro de observações dessa corrida**. Um resumo posto na pasta de
cima (fora de `ondas/`) **não** conta pelo caminho antigo sem conferência.

O livro lido é o do sítio onde o medidor corre: `ITALY_OPS_ROOT` se dito (o mesmo que o `micro_coleta` usa), senão
`data/collection-ledger/italy/` desta árvore. Sai publicado qual foi, com o sha256 dos dois ficheiros.

⚠️ Isto não é aceitar «o ledger em Git» como **prova** (continua recusado): o livro só **confere** o resumo por RUN_ID,
que é único por corrida.

## 4 · Antes / depois

| | livro de corridas | A: provadas · bloqueadas · NÃO SEI (de 716) | conferência dos resumos |
|---|---|---|---|
| **antes** (junção, sem resumos) | Git | **98 · 29 · 589** | — |
| resumos no Git, livro do Git | Git (sem as corridas de hoje) | 98 · 29 · 589 | 19 linhas recusadas `RUN_ID_AUSENTE_NO_LIVRO` — **como deve** |
| **depois** (resumos + livro operacional, só leitura) | `ITALY_OPS_ROOT` = árvore do robô | **103 · 29 · 584** | **19 conferidas**; 7 não correram, 7 sem documento novo, 1 FAILED |

**As 5 que mudaram** (`provas/A-FONTES-QUE-MUDARAM.json`): IT-T10-021, IT-T2-034, IT-T2-051, IT-T7-017 (MICRO-V3) e IT-T7-112
(2.ª onda) — NÃO SEI → RC-1, cada uma com o RUN_ID e o resumo. **As 14 conferidas que não mudaram A:** 3 já provadas
(IT-T10-018, IT-T7-021, IT-T7-117), 2 sem contrato no livro do coletor (IT-T2-032, IT-T2-037), 4 fora das 716 (IT-T2-145,
IT-T5-160, IT-T5-167, IT-T5-185 — o livro de estados do Curator no Git é anterior a elas), e as restantes repetidas entre as
duas ondas.

## 5 · A..N e as 5 condições, em processo novo

`censo_dos_donos.py`, `censo_do_congelamento.py`, `censo_das_estradas_it.py`, cada um no seu processo; leitura por
`scripts/trava_contar/medir_a_n.py` (não mede nada por conta própria). `TRAVA-A-N-LIVRO-OPERACIONAL.json` e `…-LIVRO-DO-GIT.json`.

| | critério | hoje | prova |
|---|---|---|---|
| A | fonte IT com classe provada ou bloqueio | **NÃO** | 103 · 29 · **584 NÃO SEI** (livro operacional); 98/29/589 só com o Git |
| B | nenhum writer improvisado | sem medidor | — |
| C | RAW tem um dono | **NÃO** | 4 escrevem |
| D | a corrida tem contrato | SIM | 1 dono |
| E | checkpoint com um dono | **NÃO** | 2 escrevem |
| F | derivado com um dono | SIM | 1 dono |
| G | persistência estruturada com dono | **NÃO** | etapa STRUCTURED em UNKNOWN em RC-3, 4, 10, 11, 12 |
| H | escolha de rota não espalhada | **NÃO** | ROUTE_MODEL 6 escritores · ORQUESTRADOR **15** (eram 13) |
| I | Apify não é omissão | SIM | default 0, reserva 5 |
| J | Git não é estado operacional | **NÃO** | 580 linhas de `ndjson` no Git (521 + 59) |
| K | retry não fabrica sucesso | sem medidor | — |
| L | UNKNOWN continua UNKNOWN | SIM | total necessário UNKNOWN mantido; 584 NÃO SEI publicados |
| M | o mapa representa tudo | **NÃO** | **210 de 249** componentes pendentes (mapa da produção; a cadeia não foi corrida) |
| N | inteligência congelada | **NÃO** | 16 mudaram · 0 sumiram · 5 novos |

| condição de destrave | hoje | porquê |
|---|---|---|
| 1 · os 14 cumpridos | NÃO | 4 de 14 |
| 2 · nenhuma classe necessária em UNKNOWN | NÃO | o conjunto das necessárias é UNKNOWN; 5 classes nem observadas (RC-3, 4, 10, 11, 12) |
| 3 · nenhuma necessária aberta | NÃO | 8 abertas (RC-1, 2, 3, 4, 5, 10, 11, 12) |
| 4 · nenhuma bloqueada sem decisão escrita | SIM* | RC-6, 7, 8 bloqueadas, cada uma com motivo escrito — *mas o conjunto das necessárias é desconhecido |
| 5 · o total necessário deixou de ser NÃO SEI | NÃO | `ROUTE_CLASSES_REQUIRED_TOTAL = UNKNOWN` |

A medição anterior escreveu «0 de 5» sem detalhar; lida condição a condição hoje dá 1 de 5. **É diferença de leitura,
não mudança do sistema.**

## 6 · Testes e red team

- `tests/test_trava_contar.py` **20/20**: resumo forjado (RUN_ID que o livro não tem), RAW 0, DERIVED 0, UNKNOWN, `True` no lugar de
  número, RAW que não bate com o livro, fonte que o livro não observou, livro FAILED, proveniência partida ou desconhecida,
  sem livro nada conta, resumo na pasta de cima não conta, ficheiro que não é resumo ignorado; o gerador não inventa (relatório
  de outra corrida recusado → UNKNOWN; sem relatório e sem número → UNKNOWN), não copia caminhos do estado, lê o executor no
  código; o `onda_web` grava RAW/DERIVED e escreve o resumo nos dois fins.
- **Mutação 10/10** (`scripts/trava_contar/MUTACAO-TRAVA-CONTAR-V1.json`): aceitar RUN_ID ausente, não comparar RAW, aceitar RAW 0,
  aceitar UNKNOWN, não conferir a fonte, ignorar FAILED, ignorar proveniência, contar o resumo pela pasta de cima, aceitar
  relatório de outra corrida, trocar UNKNOWN por 0.
- Medidores + vizinhos + egresso: **84 testes, as mesmas 2 falhas** (N) da produção. Red team dos medidores: **21/21**.

## 7 · Plano de instalação — NÃO instalar

1. Juntar `trava-contar-v1` à produção (traz `df0865e6` + os medidores + o D59).
2. Cadeia do mapa (LOCK-PESADO, ≥ 5 GB): regenera os 14 gerados. **Não a corri** (a missão pede não tocar em travas).
3. Na árvore do robô, o medidor lê o livro de corridas **dela** (`data/collection-ledger/italy/`) — é o operacional, e por isso
   lá o A dá 103. Num clone só do Git, sem `ITALY_OPS_ROOT`, dá 98: o resumo existe mas não há livro para o conferir.
4. Daqui em diante cada onda escreve o seu resumo sozinha; entrar no Git é commit do coordenador (`ferramentas/big_collection/ondas/`).

**Desfazer:** reverter o commit de junção na produção (`git revert -m 1 <sha>`); os resumos são ficheiros inertes — sem eles o A volta a 98.
O `onda_web` antigo continua a correr sem RAW/DERIVED; nada mais depende disto.

**Writeset:** `system-map/scripts/censo_das_estradas_it.py` (+ `censo_do_congelamento.py`, `CADEIA-DO-MAPA.json`, dos medidores) ·
`ferramentas/big_collection/onda_web.py` · `ferramentas/big_collection/resumo_da_onda.py` · `ferramentas/big_collection/ondas/*-RESUMO.json` ·
`tests/test_trava_contar.py` · `tests/test_os_medidores_da_trava_veem.py` · `scripts/trava_contar/*` · docs e provas dos medidores ·
`system-map/data/architecture.declared.json` · gerados (`donos`, `congelamento`, `estradas-it` re-corridos com o livro do Git).

## 8 · PARA A REUNIÃO — o que falta, em números

- **A:** 584 das 716 fontes ainda sem caminho provado nem bloqueio escrito. Cada corrida com documento conta agora sozinha
  (resumo + conferência); as ondas de hoje deram +5.
- **C, E, H:** 4, 2 e 6 + 15 escritores têm de passar a 1 dono cada (a Bíblia já escolheu quem).
- **G:** 5 classes de estrada sem etapa de dado organizado.
- **J:** 580 linhas de estado operacional no Git (e 122 a mais à espera no computador do robô).
- **M:** 210 de 249 peças do mapa por conferir.
- **N:** 21 ficheiros do congelamento — 5 avanços proibidos por desfazer, 3 à espera do dono, 1 por julgar.
- **B, K:** 2 medidores por construir.
- **Condições:** falta saber **quantas classes de estrada são necessárias** — enquanto isso for NÃO SEI, 3 das 5 condições não podem ser cumpridas.
