# RELATÓRIO — FECHO DOS RESÍDUOS DA BIG COLLECTION 2

Data: 2026-09-20 · Branch: `claude/contract-provenance-cutover-v1` · Bancada: `orca/workspaces/eame-sintonia/cutover-v2`
Despacho: `MISSAO-RESIDUOS-BC2.md` · Missão de fecho; nenhuma coleta nova; Admission intocada.

> Não medido = `NOT_MEASURED`. Não alcançado = `NOT_REACHED`. Nenhum número plausível.

## 0 · Confirmação da secção 0

| alegação | medido por mim |
|---|---|
| HEAD = REMOTE = `a6a9809f`, 0/0, DIRTY 0 | confirmado; 1 ficheiro solto: o próprio `MISSAO-RESIDUOS-BC2.md` |
| `data/colheita/italia` não existe; `data/colheita/` tem `_prova/` e `scrap/`; 0 rastreados; `.gitignore:89` | confirmado com os meus olhos (`test -d`, `git ls-files`, `sed -n 86,90p`) |
| herdado: HTML 42/4/0 · Sala 17→28 · sentinela · reconciliação 0 | reconfirmado no banco (Sala 28 antes desta missão) |

## 1 · `data/colheita/italia` — classificação e os 3 cleanups

| campo | valor |
|---|---|
| o que é | o **BALCÃO** entre o executor e a porta: `colheita.json` (reescrito a cada corrida) e `RETORNO.<run>.json` (o envelope da corrida, consumido pelo orquestrador na mesma corrida) |
| classificação | **GENERATED · RECONSTRUCTIBLE · TEMPORARY** — não OPERATIONAL, não TEST-ONLY |
| prova de reconstrução (não a frase do `.gitignore`) | `italy_executor.colher(run_id)` refaz o envelope a partir do ledger append-only (traduções 2–4). Medido nesta bancada: os cleanups apagaram os 46 envelopes da BC2 e eles voltaram a existir para o reprocessamento sem rede; depois das provas destrutivas desta missão a pasta voltou a não existir, sem perda |
| pode existir ali conteúdo operacional não-reconstruível? | **Não.** Tudo o que o envelope carrega nasce do ledger (`observacoes_da_corrida` + `traduzir`); o que não está no ledger (código de saída e stderr do coletor) está no `RUN-MANIFEST.json`. Um envelope «ainda não consumido» é reconstruível na mesma |
| `CLEANUPS_FOUND` | 3 sobre `BALCAO` (`tests/test_estagio_atravessa_a_fronteira.py:371`, `tests/test_italia_na_porta_canonica.py:109`, `provas/so_a_colheita_atravessa.py:194`) |
| `CLEANUPS_DANGEROUS_BEFORE` / `AFTER` | **0 / 0** |
| `CLEANUPS_FIXED` | **0** — de propósito: proteger o que se reconstrói custa manutenção e ensina a lição errada. Documentado no know-how §161 |
| risco residual, dito | um cleanup a correr **ao mesmo tempo** que uma corrida real na mesma árvore apaga o envelope antes de a porta o ler; a corrida falha com nome (`ENVELOPE_INVALIDO`/colheita não encontrada) e repete-se. É concorrência de bancada, não perda de dado |

## 2 · Os 4 HTML que «falharam a gravar»

Retomado da consulta de identidade (que devolvia a linha *a posteriori*): logo a falha não era de chave nem de bytes, era de **comparação**. Chamada directa a `conferir_o_que_ficou_escrito()` com o plano real e a memória real, só leitura, `NETWORK_CALLS = 0`:

| `RAW_ID` | `SOURCE_ID` | `FAILURE_STAGE` | `FAILURE_REASON` | `BYTES_PRESENT` | `HTML_PARSE_RESULT` | `WRITE_RESULT` (antes → depois) |
|---|---|---|---|---|---|---|
| 46 | IT-T2-007 | RAW (pós-escrita) | `METADATA_CONFLICT` em `captured_at`: banco `11:09:03.44Z` vs item `11:09:03.440Z` | sim (3.828.444 B, sha igual) | TEXT_LAYER_PRESENT, CONTENT, 56.830 chars | linha escrita mas não confirmada → **DERIVED PASS**, adm. `NAO_SE_APLICA` |
| 49 | IT-T2-010 | RAW (pós-escrita) | idem: `…38.01Z` vs `…38.010Z` | sim (72.592 B) | PRESENT | → **DERIVED PASS**, `NAO_SE_APLICA` |
| 70 | IT-T3-019 | RAW (pós-escrita) | idem: `…46.43Z` vs `…46.430Z` | sim (71.908 B) | PRESENT | → **DERIVED PASS**, `NAO` |
| 100 | IT-T5-035 | RAW (pós-escrita) | idem: `…33.19Z` vs `…33.190Z` | sim (102.744 B) | PRESENT | → **DERIVED PASS**, **`SIM`** (entrou na Sala) |

| campo | valor |
|---|---|
| causa real | `guarda/preservar_coleta._difere` comparava `captured_at` como **texto**; o Postgres corta os zeros à direita dos microssegundos. As quatro eram exactamente as observações com milissegundos terminados em zero; as 42 que passaram não tinham |
| correcção (pequena, reutilizável, no dono) | `_instante()` + `_difere`: instantes ISO-8601 comparam-se como instantes; tudo o resto como antes. `tests/test_conferencia_compara_instantes.py` (5 provas, o caso real) |
| `HTML_FAILED_BEFORE` / `HTML_RECOVERED` / `HTML_STILL_FAILED` | **4 / 4 / 0** |
| efeito nos 46 | `HTML_DERIVED` 46/46 · texto derivado 331.862 bytes · Admission (régua intocada) antes `NAO_SEI` 46 → depois **SIM 12 · NAO 5 · NAO_SEI 3 · NAO_SE_APLICA 26** · Sala **28 → 29** |
| tabela por documento | `data/derivados/HTML-REPROCESSO-2026-09-20.json` (refeita) |
| achado lateral, não tocado | `ingresso.ficha()` rebenta («multiple values for CONTENT_TYPE») quando o ficheiro do `STORAGE_LOCATION` falta e o item declara `CONTENT_TYPE` — o caminho de fallback para o JSON |

## 3 · Os 7 históricos sem bytes — dívida conhecida

Indexados **1.094 ficheiros locais** em 9 raízes (`data/samples`, `data/collection-store`, `data/raw`, `data/derivados`, os dois armazéns em `sintonia-sala-italia`, `%TEMP%\sc-readiness`, `cutover-live`, `cutover-canarios`): **0 coincidências de sha**.

| `OBJECT_ID` | `SOURCE_ID` | `RUN_ID` | `EXPECTED_BYTES` | `WHY_MISSING` | local? | só rede? | `HISTORICAL_ONLY` |
|---|---|---|---|---|---|---|---|
| 6 | IT-T2-004 (SIAS) | `XX-T3-2026-09-18-171902…` | 80.015 | corrida de canário de 18/09 noutra bancada; `XX/` daquela árvore não existe | não | **não** — a página é reescrita todos os dias; estes bytes não voltam | sim |
| 9 | IT-T3-008 (Puglia N37) | `XX-T3-2026-09-18-17…` | 2.711.642 | idem | não | sim (PDF estático; não se foi buscar) | sim |
| 11, 12 | ES-T8-002 (LinkedIn mp4, mesmo sha) | `ES-T8-2026-09-18-1633…` e 5 corridas 1636–1648 | 2.427.559 | provas LinkedIn de 18/09 noutra bancada | não | política fechada (LinkedIn) | sim |
| 19 | IT-T8-001 (YouTube wav) | `XX-T8-2026-09-19-2223…` e `2243…` | 3.755.766 | provas YouTube de 19/09 | não | política fechada (YouTube) | sim |
| 25 | IT-T2-004 (SIAS) | `IT-T2-2026-09-19-234952…` | 79.999 | canário de 19/09 | não | não (reescrita diária) | sim |
| 28 | IT-T3-005 (monitoraggio) | `IT-T3-2026-09-19-235132…` | 275.040 | canário de 19/09 | não | não (reescrita semanal, sobrescrita) | sim |

`HISTORICAL_MISSING_BYTES = 7` · `HISTORICAL_RECOVERABLE = 0` (de dados locais) · `HISTORICAL_IRRECOVERABLE = 7` sem rede (1 recuperável só com rede e sem política nova: id 9). Nenhum ficheiro inventado; nenhuma rede aberta. Não são necessários à integridade **atual**: nenhum READY, derivado ou item da Sala depende deles (`MISSING_LINEAGE` 0, `ORPHAN_*` 0).

## 4 · Gates

| gate | valor |
|---|---|
| `TEST_CAN_DELETE_OPERATIONAL_STORAGE` | **NO — re-provado**: 140 ficheiros e o mesmo sha antes e depois dos 3 módulos destrutivos + a prova + a suíte inteira; resíduo `XX/` 0 no fim |
| `SHA_MISMATCH` | 0 (46/46 HTML rematerializados conferidos; 93 objectos operacionais `PRESENT_MATCH`) |
| `RECONCILIATION_STRUCTURAL_ERRORS` | **0** — janela do reprocessamento: 54 corridas, 54 RAW (storage reutilizado 54, criado 0), 46 derivados, `RAW_SEM_RUN/SOURCE/STORAGE` 0, `ZERO_BYTE` 0, `MISSING_LINEAGE` 0/0, `ORPHAN_ADMISSION/SALA` 0, `NAO_SEI_IN_SALA` 0; dia inteiro igual |
| `NEW_FAILURES` | **0** por nome. Suíte inteira depois da correcção (Ran 4980 · failures=105 · errors=14 · skipped=190), com `SINTONIA_ARMAZEM_RAIZ` declarada: 85 nomes vermelhos = 85 da base `606974c3`; 1 nome novo (`test_M5_o_ponto_fixo…`, o carimbo do mapa, que só fecha com a cadeia depois do último commit — re-provado por módulo a seguir ao commit do mapa) e 1 da base sarou (`test_quem_criou_objecto…`) |
| `SYSTEM_MAP_CHECK` | PASS · `IMPRESSAO_DO_CARIMBO=IGUAL` conferido depois do commit do mapa que se segue a este ficheiro (se estivesse errado, o portão 2b e o test_M5 diriam DIFERENTE — ver a mensagem final) |
| `PAID_USD` | 0 |

## Entrega

| campo | valor |
|---|---|
| `INITIAL_HEAD` | `a6a9809f` |
| `FINAL_HEAD` / `REMOTE_HEAD` | o commit do mapa que se segue ao commit deste ficheiro; igual no remoto — SHA exacto na mensagem final |
| `WORKTREE` | `cutover-v2`, limpa no fim |
| `COMMITS` | 2 até este relatório (+ os do relatório e do mapa que se lhe seguem) · `PUSH_STATE` = `LOCAL == REMOTE = YES` · sem force |
| `KNOW_HOW_DELTA` | §161 |
| `MODEL_EFFECTIVE` | claude-fable-5-1 |

---

## Para o dono, em linguagem simples

**(1) O que ainda podia apagar dados.** Três limpezas de testes apagam a pasta `data/colheita/italia`. Fui ver o que lá vive: é o balcão onde o programa de coleta pousa o «recibo» de cada corrida para a porta o ler a seguir. Esse recibo é feito **a partir do livro** da coleta, que ninguém apaga, e refaz-se com um comando — provei-o: os 46 recibos que as limpezas tinham apagado voltaram a existir quando precisei deles, sem ir à internet. Por isso não pus cadeado nenhum: cadeado em coisa que se refaz só dá trabalho e ensina a proteger o que não precisa. Os documentos a sério continuam na pasta protegida da missão anterior, e voltei a provar que os testes não lhe tocam (140 ficheiros antes e depois, byte a byte).

**(2) O que aconteceu aos 4 HTML.** Tinham gravado. O que falhava era a conferência a seguir à gravação: comparava a hora da recolha como texto, e o banco escreve `03.44` onde o programa escrevia `03.440`. Só falhavam as quatro páginas cuja hora acabava em zero. Corrigi a comparação (hora compara-se com hora), pus um teste, e passei as quatro outra vez sem internet: as quatro ficaram legíveis, e uma delas entrou na Sala (28 → 29). Os 46 HTML da coleta estão agora todos derivados; 12 admitidos, 5 recusados, 26 «não se aplica» (sem régua para esses territórios), 3 «não sei» honestos.

**(3) O que são os 7 ficheiros históricos.** São recolhas de 18 e 19 de setembro feitas noutras pastas de trabalho, antes da Big Collection 2, cujos ficheiros nunca chegaram a esta máquina. Procurei-os por impressão digital em 1.094 ficheiros locais: nenhum. Duas são páginas que mudam todos os dias (os bytes daquele dia já não existem em lado nenhum), duas são vídeo do LinkedIn e uma é áudio do YouTube (áreas fechadas por política), e uma é um PDF da Puglia que voltaria pela internet, mas não fui buscá-lo só para pôr um zero. Ficam registados como dívida conhecida; nada de hoje depende deles.

**(4) A Collection está estável para seguir?** Sim, com um nome para o que falta: os testes já não apagam o armazém, os 46 HTML estão lidos, a conferência já não inventa conflitos, a reconciliação está a zero, o custo é zero. O que continua aberto, pelo nome: as 24 páginas «não se aplica» esperam régua escrita para T1, T2, T10, T11 e T12; o caminho de fallback do ingresso rebenta se um ficheiro faltar (anotado, não tocado); e os 7 históricos são dívida, não bloqueio.
