# COMENTARIOS-BATERIA — a bateria, a mutação por regra e o mapa do COMENTARIOS-V1

**Estado: PRONTO.** Ramo `claude/comments-battery-tests-pt0d99`, sobre o COMENTARIOS-V1 `8274af36`, que por sua vez
parte da produção `2ef6fef8`. Sem rede externa. Nenhum livro vivo tocado.

## 1. Bateria por NOME contra `2ef6fef8`

A lista vem de `provas/comentarios_v1/testes_por_nome.py`: são **51 módulos** (a V1 falava em 48; a lista tem 51).
Na base existem 50, porque o `test_comentarios_v1` ainda não existia. A rede estava fechada (proxy numa porta morta).
Base e ramo rodaram em worktrees limpos, no mesmo lugar (`/tmp`).

| árvore | módulos | testes | falhas | **novas** | herdadas |
|---|---|---|---|---|---|
| base `2ef6fef8` | 50 | 1372 | 39 | — | — |
| V1 `8274af3` | 51 | 1397 | 41 | **2** | 39 |
| esta branch `6c0b260` | 51 | 1404 | 39 | **0** | 39 (as mesmas, pelo nome) |

**A bateria achou uma falha nova que a V1 não viu:**
`test_linkedin_build_01_local_first::test_21_provider_pago_nao_muda_politica` e `::test_M12_policy_ignored`, com
`PAID_NEEDED_FOR == ['COMMENTS_TEXT']`.

- **Causa (medida):** a V1 declarou `LINKEDIN/FETCH_COMMENTS` na matriz como rota **gratuita**
  (`custo zero`, D106). Só que a tabela `ONDE_SE_OBTEM` do adaptador continuava a dizer `COMMENTS_TEXT = PAID`.
  Enquanto a política recusava, isso dava BLOCKED. Com a política ALLOWED, o plano de aquisição passou a
  **pedir rota paga para comentário**, que é o contrário da D106-3.
- **Conserto no código, não no teste:** `coleta/adaptador_linkedin.py:548` passa a `FREE`, com o porquê. A matriz,
  que é a dona, continua a dizer `POSSIBLE_NOT_PROVED`.
- Os ficheiros estão em `provas/comentarios_bateria/bateria-{base-2ef6fef8,ramo-8274af3,ramo-6c0b260}.json`.

Nota de ambiente: `test_c3_youtube_cutover::test_gravar_raw_respeita_o_redirecionamento` falha nos worktrees em
`/tmp` (base e ramo) e passa na pasta principal. É um caminho relativo que depende de onde o repo está, e não
desta missão. Por isso comparei sempre no mesmo lugar.

`system-map/tests/test_system_map.py`: 10 reprovações, os mesmos nomes na base, na V1 e aqui. Há ainda
`scanner_e_deterministico`, que falha na primeira corrida em worktree destacado, **também na base**, e passa na
segunda. `test_freshness.mjs` PASS (49). `test_impressao_da_arvore.py` PASS.

## 2. Mutação — `provas/comentarios_bateria/`

- **As 14 da V1, repetidas aqui:** 14/14 mortos (`MUTACAO-V1-REPETIDA.json`).
- **23 novos, por regra** (`mutar_regras.py` → `MUTACAO-REGRAS.json`). Cada mutante só conta se fizer aparecer uma
  falha nova além das herdadas. Todos os ficheiros foram repostos pelos bytes (sha256 igual).

| regra | no `8274af3` (antes) | agora |
|---|---|---|
| PUBLIC_ASSERTION (evidência, origem, LinkedIn nasce POST) | 3/3 | 3/3 |
| LUGAR DO PAI (não herda, herda sem prova, **envelope perde o lugar**, pai errado) | 3/4 | 4/4 |
| SEM LUGAR DO COMENTARISTA (autor, **REGION_IF_PROVEN do pai**, **EXPLICIT sem fala**, **fala vira FACT_LOCATION**) | 1/4 | 4/4 |
| ELEGIBILIDADE (**HIGH sem registo**, LOW colhe, NAO_SEI colhe, **LOW→MEDIUM**, **NAO→NO some**, desligado, MEDIUM sem entidade) | 4/7 | 7/7 |
| CONTROLE (olha texto, **só relevantes**, **cortado a 1**, dos mais curtidos) | 2/4 | 4/4 |
| SEM ROTA PAGA (D106-3) | — | 1/1 |

**Na V1, 9 defeitos plantados passavam sem nenhum teste reprovar.** O resultado da V1 está gravado em
`MUTACAO-REGRAS-NO-8274af3.json`. Para matar esses 9 (e o N23), acrescentei 7 testes: `tests/test_comentarios_v1.py:243`
(`BateriaDasRegras`, linhas 247–293). Cada teste diz qual mutante mata. Não enfraqueci nenhum teste e nenhuma régua.

## 3. Cadeia do mapa

- `REGERAR` CADEIA=OK.
- `VALIDAR`: a 1.ª corrida deu **FAIL** em P9, com 6 ficheiros sem peça (5 da V1, que ficou PRONTO-SEM-MAPA, e o
  `mutar_regras.py`). Declarei duas peças em `system-map/data/architecture.declared.json:2307`
  (`C-ELEGIBILIDADE-COMENTARIO`, Z-PEDIDO) e `:2490` (`C-PROVA-COMENTARIOS`, Z-PROVA). As duas ficaram **PENDING** e
  sem carimbo: não reli por inteiro `medir_comentarios_linkedin.py`, e recarimbar sem reler é mentir.
- Depois disso, `REGERAR` → `VALIDAR`: **SYSTEM_MAP_CHECK=PASS**.
- `impressao_da_arvore.py --conferir-carimbo`: **IGUAL**. Conferido em `6c0b260`, e de novo no SHA final.

## O que NÃO está provado / fica para o dono

- A rota gratuita do LinkedIn continua candidata. A medição de rede fica com a coordenação, como na V1.
- **Observado e não mexido:** um pai com universo **SIM** mas sem entidade nem tema (por exemplo T9, «nuovo prodotto
  alla fiera») cai em `NAO_SEI` com o texto «LACUNA_DE_VOCABULARIO… nem a régua da Admissão reconhece». Só que a
  régua reconheceu. O nível pode até estar certo, mas o porquê está errado. A régua é da V1 e do dono, então fica
  registado para decisão.

## SHA

**PRONTO** = o último commit desta branch, o que traz este relatório. Um commit não contém o próprio SHA; o valor
está na mensagem final da sessão.

## EM PALAVRAS SIMPLES

- **Rodei as 51 baterias de teste** que a equipe não conseguiu rodar, na versão antiga e na nova, e comparei falha
  por falha pelo nome.
- **Achei 1 defeito real:** depois da mudança, o sistema passou a achar que comentário do LinkedIn **precisava de rota
  paga**, e a D106 diz que não se paga. Consertei. Agora há zero falhas novas.
- **Estraguei o código de propósito 37 vezes.** Na versão da equipe, 9 desses estragos passavam sem nenhum teste
  reclamar. Por exemplo: a região de quem comentou podia herdar o lugar do vídeo; a amostra de controle podia sumir
  quando nenhum comentário era "relevante"; uma fonte não registrada podia virar HIGH. Escrevi 7 testes novos, e agora
  os 37 estragos são apanhados.
- **O mapa do sistema foi regerado e validado (PASS)**, com as duas peças novas declaradas, e o carimbo bate com a árvore.

HARD STOP.
