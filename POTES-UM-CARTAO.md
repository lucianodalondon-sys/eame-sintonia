# POTES-UM-CARTAO — um cartão por pergunta (D125)

**Missão:** D125, aprovada pelo dono em 27/09, por volta das 21:40 («potes, aprovo»).
**Base:** produção `b273660b6` (`origin/servico-20260923-0923`). **Branch:** `claude/potes-one-card-per-question-frzml5`.
**Desenho:** `docs/lab/IDENTIDADE-CRUZAMENTO.md` (`origin/claude/stable-crossing-identity-onfwdu @dccb0ec`), §11.2 e a ordem da §11.3.
**Rede:** nenhum site externo foi visitado. Os livros vivos não foram tocados.

---

## O que foi feito, na ordem da §11.3

| # | passo | onde (ficheiro:linha) |
|---|---|---|
| 1 | **Vocabulário único v1**: praga, cultura e lugar com código, alias e versão (`VOCAB-v1@<impressão>`, 239 termos). Nenhum termo foi inventado. As listas vêm de onde já existiam: o leitor de rótulos, o `MESMO_PROBLEMA` do boletim e o gazetteer do `fato_local`. Grupo ≠ espécie. «mosca» sozinho = NÃO SEI. | `motor/vocabulario_unico.py:71` cultura · `:97` praga · `:115` lugar · `:169` carimbo |
| 2 | **SG2 e FUT2 sem run.** O sinal é `sha(documento\|RAW\|FACT_TIME)`. O futuro é `sha(ISSUE\|lugar\|horizonte)`. Os IDs antigos (`SG-`, `R7-FUT-`) vão para `ALIAS`. | `motor/corrida_da_inteligencia.py:652` · `motor/motor_das_capacidades.py:691` |
| 3 | **`CROSSING_KEY` + `XQ-`** em `cruzamentos_max.py`: F1 (IT × substância × cultura), F2 (IT × cultura × praga), F3 (IT × substância × registo; o boletim-gatilho sai do ID e vira REFERÊNCIA). Os 96 `XMAX-` antigos ficam em ALIAS. A resposta da F1 vem do **rótulo** (`avaliar_rotulo`), nunca do «melhor link». | `motor/cruzamentos_max.py:1101` F1 · `:1129` F2 · `:1149` F3 · `:1160` avaliar_rotulo · `:1189` itens_do_pote |
| — | **Motor de identidade IDENT-v1**: chave, `NAO_SEI@doc`, evidência = documento, independência = originador, `consolidar`, `estado_vigente`, `fecho`, DAG e `delta`. | `motor/identidade_do_cruzamento.py:106` · `:188` · `:310` · `:397` · `:414` · `:470` |
| 4 | **Contrato do pote v2.1**, com gerador e validação. `CARTOES` guarda cada cartão **uma vez**. Cada compartimento guarda **só os IDS**. `DELTA` fica por cartão (NOVO / FORTALECEU / MUDOU_ESTADO / ENFRAQUECEU / SEM_REVISAO, com CAUSA e GATILHO). `SAIU` só com causa. `ANTERIOR` = RUN_ID + SHA256. `GRUPO` serve só para apresentação. `REFERENCIAS {CROSSING_ID, AVALIACAO_ID, PAPEL}` só apontam para baixo. `FECHO` conta cada documento e cada originador uma vez. | `pacote/pote_intelligence_casco.py:81` · `:898` v21_do_v2 · `:973` materializar · `:1004` conferir_pote_v21 · schema `docs/intelligence/pote-v2/POTE_INTELLIGENCE_CASCO-v2.1.schema.json` · `pacote/validar_pote_v2.py` |
| 5 | **DELTA pela opção A**: compara com o pote anterior **publicado**. O casamento é pelo ID ou pelo ALIAS, e por isso também funciona contra um pote v2 antigo. Linha de comando: `--v21 --anterior`. | `pacote/pote_intelligence_casco.py:1122` · `pacote/pote_cruzamentos_max.py` |
| 6 | **Red team promovido a `tests/`**: os 17 casos rodam contra o código real. Somam-se o teste **D125-3**, o teste «nenhum pote guarda cópia» e o casco em JS. | `tests/test_identidade_cruzamento.py` · `tests/test_pote_v21.py:105` T1 · `:120` T2 · `:137` T3 (D125-3) · `tests/test_pote_v21_no_casco.mjs` |
| — | **Casco**: o leitor do pote v2.1 **resolve** cada ID no cartão e **só mostra** o selo DELTA, o GRUPO, a RESPOSTA e os SAIRAM. Não compara potes e não calcula nada. | `italia-portale/client/sintonia-pote-casco.js:111` resolver · `:227` · `italia-portale/client/portale.html:3660` · `:3679` |
| — | **Bíblia da Intelligence V0.5**: INT-LAW-096, 097, 098 e 099 (§9), INT-LAW-215 e 216 (§20), mais os 4 pontos da D125 citados. Zero leis alteradas. O registo foi atualizado. | `BIBLIA-DE-ENGENHARIA-DA-INTELLIGENCE.md:613` · `:642` · `:1066` · `:1072` · `controle/AUTORIDADES-CANONICAS.json` |

**Os 2 defeitos da POC do LAB foram corrigidos e ficam presos por teste:**
- (1) Quando a mesma origem troca NO → YES, a relação é `TEMPORAL_CHANGE` e o estado vigente passa a ser YES, com o NO guardado no histórico. Nunca vira «CONFLITANTE». Código em `identidade_do_cruzamento.py:188`, testes P1 e P1b.
- (2) O estado da F1 é o do **rótulo**. Em FOLPET × VITE os dois links ficam à vista (UNRESOLVED e YES_A_CONFIRMAR) e a resposta é `SIM_A_CONFIRMAR`, com `RESPOSTA_DITA_POR = ROTULO`. Testes P2, P2b e R4.

## Provas nos dados do repo (R7) — `python3 provas/potes_um_cartao/medir_r7.py` → `MEDICAO-R7.json`

| | antes | depois |
|---|---|---|
| POTE-R7 publicado (`0189967826ea…`) | 47 objetos nos compartimentos, 25 IDs distintos | **25 cartões** em 47 lugares (10 SG2 · 10 FUT2 · 3 REND · 2 XQ) |
| Arquivo | 22 objetos, **22 cópias** de outros compartimentos | 22 IDs, **0 cópias** |
| Cruzamentos R7 (portfolio) | 96 objetos por link | **83 perguntas** (81 F1 + 2 F2), 0 IDs repetidos, 96 ALIAS guardados |
| OLIVO × mosca da oliveira | **13** cartões | **1** cartão · 13 links · 13 documentos · 10 SOURCE_ID |
| FOLPET × VITE | 2 cartões com respostas diferentes | 1 cartão · os 2 estados nos links · resposta do rótulo |
| tau-fluvalinato ARIF n.37 e n.38 (cultura NÃO SEI) | 2 | **continuam 2** (NÃO SEI ≠ NÃO SEI), com o **mesmo GRUPO** |
| DELTA contra o POTE-R7 publicado | — | 25 de 25 casam pelo ALIAS → SEM_REVISAO 25 · 0 «sumidos» |

⚠️ O POTE-R7 publicado é **anterior** ao contrato v2 único: a lei v2 de hoje reprova-o com 170 violações (medido). Por isso, sobre ele, a conta é **só uma medição de identidade** (`ENTRADA = POTE_V2_SO_MEDICAO`). Não é um pote novo conferido. O pote v2.1 **conferido** está provado nas corridas sintéticas (R6-equivalente: 92 cartões) e no teste D125-3.

## Testes — bateria inteira por nome (`provas/int_r7/bateria_por_nome.py`, rede fechada)

| | módulos | testes | falhas por nome |
|---|---|---|---|
| base `b273660` | 320 | 7190 | 130 |
| depois `7f8e8c1e` (código + mapa regerado) | 322 | 7237 | 130 |

- **Novas: 0. Sumidas: 0.** As 130 falhas são as herdadas da base, comparadas pelo nome.
- 2 módulos novos, **0 falhas**: `test_identidade_cruzamento` 30 · `test_pote_v21` 17 (este corre `test_pote_v21_no_casco.mjs`, 12/12).
- Módulos tocados, todos verdes: `test_cruzamentos_max` 55 · `test_pote_v2_unico` 38 · `test_pote_intelligence_casco` 45 (inclui `test_pote_no_casco.mjs` 118/118) · `test_motor_das_capacidades` 64.
- Nenhum teste foi enfraquecido nem editado. Um ficheiro gerado foi regerado de forma **declarada**: `docs/intelligence/r7/CRUZAMENTOS-MAX-ITENS-DO-POTE.json`. O teste X4 exige que ele seja o que o código produz, e a D125 muda o formato para um objeto por pergunta. O formato antigo ficou guardado em `provas/potes_um_cartao/ITENS-XMAX-ANTES-b273660.json`.
- JSON: `provas/potes_um_cartao/BATERIA-BASE-b273660.json` e `BATERIA-DEPOIS-7f8e8c1e.json`.

## Mutação

| script | mortos |
|---|---|
| `provas/_mutantes_identidade.py` (novo): os 9 do LAB (M1–M9) plantados no **código real** + 16 da D125 | **25/25** |
| `provas/_mutantes_cruzamentos_max.py` (antigo, sem alteração): os mutantes antigos continuam a plantar-se no código novo | **31/31** |

Na primeira rodada, o D7 («ANTERIOR sem SHA256 aceite») ficou **VIVO**. O teste passava por causa de outra guarda (a conferência de saída) e não distinguia qual guarda tinha apanhado o defeito. O T8 foi **fortalecido** para exigir a guarda de entrada, e a de saída passou a ser testada à parte. Depois disso: 25/25. Saídas em `provas/potes_um_cartao/MUTACAO-*.txt`.

## System Map

`correr_a_cadeia.py REGERAR` → `VALIDAR` = **SYSTEM_MAP_CHECK=PASS** · `impressao_da_arvore.py --conferir-carimbo` = **IGUAL**.
Declarei duas peças novas: `C-IDENTIDADE-DO-CRUZAMENTO` (Z-MOTOR) e `C-PROVA-IDENTIDADE` (Z-PROVA). As frases das 6 peças tocadas foram atualizadas.
**Não recarimbei (`--stamp`).** Esse comando carimba *todos* os ficheiros do repo como relidos, e eu só reli os meus. Recarimbar sem reler é o que o AGENTS.md proíbe. Por isso as peças que toquei podem aparecer 🟡 («mudou depois da declaração»), e isso é a verdade.

## Design

`ADAMA_DESIGN_SYSTEM_MATCH = NÃO SEI`. O Design System vive no Claude Design, um site externo, e a missão proíbe visitar sites externos. O selo do DELTA, a linha do GRUPO e a lista SAIRAM **reutilizam** os estilos que já existiam no bloco do pote (mesmas cores e tamanhos das linhas vizinhas). Nenhum componente, ícone ou cor novos: `NEW_PATTERN_REQUIRED = NO`. Isto precisa de uma conferência humana no DS.

## NÃO SEI / o que ficou de fora (dito, não escondido)

- O `montar_entrada_r7.py:99` do desenho **não existe no repo**: ficou fora do Git, na máquina do coordenador. O FUT2 foi aplicado no equivalente que está no repo (`motor_das_capacidades.py`). Se o script local continuar a cunhar `FUT-` com o run, o pote migra o ID (`identificar`) e guarda o antigo em ALIAS.
- A Coleta ainda não entrega o campo **ORIGINADOR**. A independência usa o `SOURCE_ID` como *proxy declarado* (`PROXY_SOURCE_ID:`), e isso **superconta**. NÃO SEI quanto.
- **Agenda = `windows`** (Finestre Colturali) é uma inferência minha. O dono pode ter querido outro pote.
- **EPPO**: não foram usados códigos EPPO. A lista `MESMO_PROBLEMA` declara «não é EPPO».
- **F3 (concorrência)**: hoje tem 0 objetos (LACUNA-3, a referência não tem o mercado). A chave e a REFERÊNCIA estão prontas, mas não foram exercidas com dados reais.
- Nos cartões com NÃO SEI, o documento do `NAO_SEI@` é o `DOCUMENT_ID`, ou a URL, ou a chave da Sala: o que a Coleta entregou naquele ponto. Um NÃO SEI migrado do pote v2 (DOC:) e o mesmo NÃO SEI vindo do motor (URL:) podem ganhar nomes diferentes. Nunca se juntam por engano (é essa a regra), mas a continuidade entre corridas desses cartões não está provada.
- **A opção B** (tabela append-only no Postgres) não foi feita, como o desenho pede: A agora, B depois.
- **O pote v2.1 da R7 real** não foi gerado aqui: a LINEAGE da R7 vive fora do repo. O comando está abaixo.

## Comando de instalação (coordenador)

```bash
git fetch origin claude/potes-one-card-per-question-frzml5
git merge --no-ff origin/claude/potes-one-card-per-question-frzml5      # na linha de serviço
py -m unittest tests.test_identidade_cruzamento tests.test_pote_v21 tests.test_cruzamentos_max tests.test_pote_v2_unico tests.test_pote_intelligence_casco
node tests/test_pote_v21_no_casco.mjs
py provas/potes_um_cartao/medir_r7.py                 # 47 -> 25 · 13 -> 1 · arquivo 0 copias
py provas/_mutantes_identidade.py                     # 25/25 mortos
# a primeira corrida v2.1 com a R7 local, DELTA contra o pote PUBLICADO (opcao A):
py pacote/pote_cruzamentos_max.py --entrada ENTRADA-DO-POTE-R7.json --saida POTE-R7-V21.json \
   --anterior docs/intelligence/r7/POTE-R7-PUBLICADO.json
py pacote/validar_pote_v2.py POTE-R7-V21.json
# para o casco (fora do Git e do deploy):
py pacote/pote_cruzamentos_max.py --entrada ENTRADA-DO-POTE-R7.json --saida italia-portale/client/sintonia-pote.js \
   --anterior docs/intelligence/r7/POTE-R7-PUBLICADO.json
py system-map/scripts/correr_a_cadeia.py VALIDAR       # SYSTEM_MAP_CHECK=PASS
```
Se aparecer uma falha nova pelo nome contra `provas/potes_um_cartao/BATERIA-DEPOIS-*.json` → desfazer o merge.

---

## EM PALAVRAS SIMPLES

Antes, cada cartão recebia o nome **do papel de onde veio e da rodada** em que foi feito. Por isso a mesma pergunta
virava vários cartões: 13 só para «a bula cobre a mosca da oliveira?». E o Arquivo guardava **cópias** de 22
cartões que já estavam noutras gavetas.

Agora o cartão tem o nome **da pergunta**. Informação nova sobre a mesma pergunta entra como **mais uma prova** no
mesmo cartão. Cada cartão existe **uma vez só**, e as gavetas (Rótulo, Oportunidade, Agenda, Arquivo…) guardam só
o **número dele**. Quando chega um documento novo, o cartão muda uma vez e todas as gavetas que o mostram mudam
juntas, com o mesmo selo («reforçado por tal documento»). O portal só mostra esse selo: não calcula nada.

Nos dados reais: 47 lugares viraram 25 cartões, as 13 moscas viraram 1, e o Arquivo ficou sem cópias. Onde não
sabemos a cultura, os cartões **não se juntam**, e isso é o certo. Quebrei a regra de propósito de 25 jeitos, e os
testes pegaram os 25.
