# METODO-PUGLIA — o laboratório da Puglia fecha, e as correções viram método (D112)

```
DECISAO          D112 · VEREDITO PUGLIA = APROVADO COM CORRECOES
BASE             2ef6fef (produção)  ·  branch claude/metodo-puglia-rm5sdo
GOLD             tests/fixtures/puglia/GOLD-FIXTURE-PUGLIA-V1.json  (10 casos · 12 fichas · selado)
BIBLIA COLETA    V1.4 → V1.5   (105 → 108 leis)
BIBLIA INTEL     V0.3 → V0.4   (+2 leis, 0 alteradas)
```

## 1 · Leis alteradas

| lei | onde | o quê |
|---|---|---|
| `COL-LAW-032` (emenda) | `BIBLIA-CANONICA-DA-COLETA.md:816` e `:833` | `LOCATION_SOURCE = TEXT · SECTION_HEADER · VISUAL_HEADER_CANDIDATE · UNRESOLVED`; `VISUAL_HEADER_CANDIDATE` nunca sustenta `FACT_LOCATION`; `LOCATION_EXPRESSION_RAW` + `UNRESOLVED`, nunca ponto artificial. IT `IMPLEMENTED → PARTIAL` |
| `COL-LAW-221` (nova) | `BIBLIA-CANONICA-DA-COLETA.md:2965` | `ENTITY_SOURCE = SPAN · PARAGRAPH_CONTEXT · SECTION_TITLE · DOCUMENT_TITLE · UNKNOWN`; concorrente ou troca de secção → `UNKNOWN` |
| `COL-LAW-222` (nova) | `BIBLIA-CANONICA-DA-COLETA.md:2996` | a ficha não acrescenta nem corta; qualificadores são afirmação; entidades juntas preservadas; tradução nunca é evidência; FONTE × `INTERPRETACAO_DO_SISTEMA` |
| `COL-LAW-223` (nova) | `BIBLIA-CANONICA-DA-COLETA.md:3022` | `PREVISAO ≠ FATO_OBSERVADO ≠ RECOMENDACAO`; frases vizinhas de espécies diferentes = afirmações diferentes |
| `INT-LAW-078` (nova) | `BIBLIA-DE-ENGENHARIA-DA-INTELLIGENCE.md:515` | mesma redação em N territórios = N aplicações, 1 instituição |
| `INT-LAW-079` (nova) | `BIBLIA-DE-ENGENHARIA-DA-INTELLIGENCE.md:528` | `DIVERGENT_RECOMMENDATIONS` + `CONTRADICTION_STATUS = UNRESOLVED`; `TEMPORAL_CHANGE_IN_RECOMMENDATION` não é contradição e não prova campo |

Histórico constitucional: `BIBLIA-CANONICA-DA-COLETA.md:25` (linha V1.5, cita D112) ·
Intelligence §33.4. Diário: `docs/decisoes/DIARIO-DE-DECISOES.md:1467` (D112 — razão e
evidência ficam lá, não nas leis). Matriz: `docs/biblia/CONFORMIDADE-ITALIA.md:89` e `:214`.
Registo: `controle/AUTORIDADES-CANONICAS.json` (cartão da Intelligence → `V0.4`).

`COL-LAW-219` («medição declarada») **não existe nesta árvore** — procurada antes de escrever.
Por isso a fidelidade virou lei nova (222), e o `220` ficou livre para não colidir com outra linha.

## 2 · Código e teste

- `leis/lugar_do_fato.py:84` vocabulário `LOCATION_SOURCES`; `:133` `fact_location()` — a trava.
- `leis/afirmacao_da_fonte.py` — `ENTITY_SOURCES` (`:38`), `procedencia_da_entidade` (`:42`),
  `ESPECIES_DA_AFIRMACAO` (`:65`), `relacao` (`:86`), lint `fidelidade` (`:174`). Não é extrator.
- `tests/test_metodo_puglia.py` — 28 testes, sem rede: (i) 12/12 trechos batem com
  `SPAN_SHA256` e o ficheiro está selado; (ii) C01 · C05 · C06 (`VISUAL_HEADER_CANDIDATE`) →
  `UNRESOLVED`; (iii) o lint reprova C05 e C06 e aprova C02 · C08 · C10 — e concorda com o Q1
  do dono em 9 de 9 fichas; (iv) os extratores atuais contra o gold.

## 3 · O que o código ATUAL cumpre, e o que NÃO cumpre (backlog medido)

| | caso | resultado |
|---|---|---|
| ✅ CUMPRE | C01 · C05 · C06 · C08 | `fato_local` e `fato_do_texto` não inventam lugar onde o dono pediu `UNRESOLVED` |
| ❌ NÃO | C04 | «zona costiera del Gargano» está na frase; o código dá `NAO SEI` |
| ❌ NÃO | C02 · C03 · C07 | não há conceito de `SECTION_HEADER`; os três dão `NAO SEI` |
| ❌ NÃO | todos | a saída dos extratores não tem `LOCATION_SOURCE` |
| ❌ NÃO | C08 | ninguém guarda `LOCATION_EXPRESSION_RAW` |
| ❌ NÃO | todos | nenhum código de extração emite `ENTITY_SOURCE` |

As cinco linhas ❌ são `expectedFailure` **declarados** em
`tests/test_metodo_puglia.py:356-382`. O esperado do dono não foi tocado. Se alguém
consertar, o teste reprova como «unexpected success» até a marca ser tirada.

⚠️ Parte do C02 · C03 · C07 é também do fixture: o cabeçalho `COMPRENSORIO …` não está no
`CONTEXTO_ANTES` gravado, então o extrator nunca o vê. O backlog é duplo: a coleta tem de
preservar a secção, e o extrator tem de a ler.

## 4 · Mutação

`provas/mutacao_metodo_puglia.py` — 6 mutantes plantados nos ficheiros reais, 6 apanhados,
`SURVIVORS = 0`: VISUAL_HEADER vira FACT_LOCATION · ENTITY_SOURCE sai da lei · SPAN sem nome
no trecho · lint ignora colchete · lint ignora qualificador · esperado do dono alterado.

## 5 · Bateria por nome, antes e depois

Todos os `tests/test_*.py` (unittest, módulo a módulo, rede fechada) + todos os
`system-map/tests/*`, em worktrees limpas de `2ef6fef` (antes) e `c4bba5a` (depois).

```
ANTES   5933 testes · 132 vermelhos · 1 expectedFailure
DEPOIS  5961 testes · 131 vermelhos · 6 expectedFailure   (+28 = test_metodo_puglia)
NEW_FAILURES_BY_NAME = []          SO_ANTES = []
CURADA  test_o_controle_separa_lei_de_mencao …test_M5_o_ponto_fixo… — causa NÃO SEI
```

A primeira passagem «depois» (`52da843`) deu **4 falhas novas**, e foram tratadas pelo nome:

- `test_B9_a_biblia_real_desta_arvore_nao_se_contradiz` — **defeito meu**: o §33.4 dizia
  `IMPLEMENTATION_AUTHORIZED = inalterado`. Corrigido copiando a cadeia do cabeçalho letra a
  letra, como a V0.3 fez. O teste não foi tocado.
- `test_T2_T3_nenhuma_lei_perdida_nem_renumerada` (bloco 2xx 18 → 21),
  `test_a_matriz_declara_o_head_e_a_versao_medidos` (V1.4/105 → V1.5/108),
  `test_o_total_nao_esta_escrito_a_mao` (registo 105 → 108) — testes que cravam a versão e
  dizem no próprio texto que «só sobem por emenda registada». **Ajuste DECLARADO**, com
  comentário a citar D112 em cada um; nenhuma asserção foi afrouxada, e a lista de leis que
  não podem desaparecer ganhou as três novas.

Não regerado, e dito: `data/derivados/COLLECTION-V1-CLOSE-GATES.json` continua a registar
`LAW_TOTAL = 105` — é uma fotografia com o seu `MEASURED_HEAD`, de outra missão.

## 6 · Mapa

`correr_a_cadeia.py REGERAR` → `VALIDAR`: `SYSTEM_MAP_CHECK=PASS`;
`impressao_da_arvore.py --conferir-carimbo`: `IGUAL`. Peça nova `C-AFIRMACAO-DA-FONTE`
(`Z-REGUAS`) fica ⚪ **NÃO SEI** — nada em produção importa o contrato, e é a verdade; o
scanner não foi mexido para a pintar. A mutação entrou em `C-PROVA-COLETA`.

## 7 · SHA

Trabalho: `52da843` + `c4bba5a`. O SHA final é o do commit que traz este relatório e o mapa
regerado por cima dele (dito na entrega; um ficheiro não pode conter o SHA do próprio commit).

## EM PALAVRAS SIMPLES

O dono corrigiu à mão doze fichas da Puglia e disse o que estava errado. Agora isso é regra:
lugar que só aparece na imagem da página não vira lugar do fato; cada praga ou cultura diz se
o nome estava mesmo na frase ou veio do título; a ficha não pode inventar nem cortar pedaços
da frase; previsão, observação e recomendação são coisas diferentes; e duas fontes que dizem
números diferentes ainda não estão «a contradizer-se». Há um teste que lê as respostas do dono
e confere as regras. As regras estão certas; o código que lê os boletins ainda **não** as
cumpre em cinco pontos — e o teste mostra quais, em vez de esconder.
