# RELATÓRIO — OS 3 GARGALOS DA BIG COLLECTION 2 (STORAGE → TESTES → HTML)

Data: 2026-09-20 · Branch: `claude/contract-provenance-cutover-v1` · Bancada: `orca/workspaces/eame-sintonia/cutover-v2`
Despacho: `MISSAO-GARGALOS-BC2.md` · A Big Collection 2 **não** foi repetida.

> Não medido = `NOT_MEASURED`. Não alcançado = `NOT_REACHED`. Nenhum número plausível.

## 0 · Confirmação da secção 0

| alegação do coordenador | medido por mim |
|---|---|
| HEAD = REMOTE = `b4ff70ae`, 0/0 | confirmado (`git fetch` + `rev-parse`) |
| bancada limpa | 1 ficheiro solto: o próprio `MISSAO-GARGALOS-BC2.md` |
| `XX/` 86 ficheiros · 68 MB; acervo 93 · 77 MB | confirmado (86 / 68 MB; 93 / 77 MB) |
| 4 chamadas `rmtree` | confirmado: 3 em `XX/` (2 no teste da fronteira, 1 na prova) + 1 em `BALCAO`; mais 1 `BALCAO` em `test_italia_na_porta_canonica` |
| `ArmazemLocal` em ≥ 10 ficheiros | confirmado: 3 de produção + 12 provas + 5 testes |

## 1–2 · Storage: o owner e a separação

| campo | valor |
|---|---|
| `OPERATIONAL_STORAGE_OWNER` | `guarda/preservar_coleta.py` — `Armazem` (produção remota: `guarda/portas_live.ArmazemSupabase`, bucket `raw`; bancada local: `ArmazemLocal`). Nenhum segundo storage foi inventado |
| `OPERATIONAL_STORAGE_ROOT` | `%USERPROFILE%\sintonia-sala-italia\armazem` (fora da árvore, fora de Temp, ao lado do cluster da Sala), com o marcador `ARMAZEM_OPERACIONAL.json`; declarada por `SINTONIA_ARMAZEM_RAIZ` |
| `TEST_STORAGE_OWNER` | o mesmo dono (`ArmazemLocal`), na raiz da árvore |
| `TEST_STORAGE_ROOT` | `<repo>/XX/` (resíduo de medição, `.gitignore`) ou a pasta temporária que o próprio teste cria |
| regra implementada | `raiz_do_armazem_local(estado, env)`: modo OPERACIONAL **exige** a variável (falha fechado: `ArmazemOperacionalSemRaiz`); raiz dentro da árvore é recusada; nos outros modos a variável é **ignorada** e a raiz é a árvore. A persistência declara a raiz no recibo (`ARMAZEM_RAIZ`); o orquestrador cria o armazém dessa raiz |
| guarda defensiva | `apagar_armazem_de_medicao(caminho, dentro_de=)`: só apaga `<árvore>/XX` ou dentro do tempdir do teste; recusa fechado marcador (nele ou num pai), raiz declarada e qualquer outro caminho. Os 3 `rmtree(XX)` passam por ela |
| o que ficou fora | `BALCAO` (`data/colheita/italia`, envelopes do executor, `.gitignore`) continua a ser apagado por 3 cleanups — não é storage de bytes, mas é onde vivem os envelopes das corridas; anotado como pendência |

## 3 · Restaurar e provar

| campo | valor |
|---|---|
| objectos em `storage_object` | 123 |
| `OPERATIONAL_BYTES_EXPECTED` | 100 (123 − 23 envelopes JSON de observações falhadas) |
| `OPERATIONAL_BYTES_PRESENT` (`PRESENT_MATCH`) | **93** — os 107 da BC2 estão inteiros (86 documentos + 21 `NO_BYTES_EXPECTED`) |
| `PRESENT_MISMATCH` / `SHA_MISMATCH` | 0 / 0 |
| `MISSING_EXPECTED_BYTES` | **7**, todos anteriores à BC2 (ids 6, 9, 11, 12, 19, 25, 28; 18–19/09; SIAS ×2, Puglia N36, LinkedIn mp4 ×2, YouTube wav, monitoraggio). Linhagem: corridas de readiness/LinkedIn/YouTube noutras bancadas; os bytes nunca existiram nesta árvore nem no acervo. Não inventados |
| `NO_BYTES_EXPECTED` | 23 (envelopes `.json` de observações sem documento) |
| tabela completa | `%TEMP%\cutover-final\restauro_operacional.json` (STORAGE_ID · PATH · SHA256_DB · SHA256_BYTES · STATUS) |

## 4 · Prova de não-destruição

| campo | valor |
|---|---|
| sentinela | o armazém operacional inteiro (136 ficheiros, marcador incluído; sha do `37_boll_agro_20260914.pdf` registado antes) |
| suíte destrutiva | os módulos com `rmtree` correram (e a suíte inteira, §16) com `SINTONIA_ARMAZEM_RAIZ` declarada |
| depois | 136 ficheiros, o mesmo sha (`a869a9a9813dfc6f…`); resíduo `XX/` da árvore: 0 (morreu como devia) |
| `TEST_CAN_DELETE_OPERATIONAL_STORAGE` | **NO** |
| teste permanente | `tests/test_armazem_operacional_protegido.py` (12 provas): sem raiz falha fechado; raiz dentro da árvore recusada; sem memória a variável é ignorada; limpeza recusa marcador/raiz/alheio; o resíduo morre e a sentinela sobrevive |
| medido durante a missão | a primeira versão da regra usava a variável em todos os modos: a suíte (AUSENTE) ia escrever resíduo dentro do operacional. Parada aos 15 s, 136 antes e depois, regra fechada antes de a deixar correr |

## 5 · As 10 expectativas obsoletas

| `TEST` | `OLD_EXPECTATION` | `WHY_STALE` | `REAL_INVARIANT` |
|---|---|---|---|
| `test_source_id_wiring_gap.test_o_recibo_da_coleta_e_um_estagio_da_trilha` | `com_recibo == 7` | 7 = fontes do piloto no dia; a BC2 pôs o IT-T3-011 no ledger | `{itens com recibo} == {itens cujo sha está no ledger}`, não vazio |
| `test_estradas_it.test_T8_o_markdown_nao_contradiz_o_estado_gerado` | markdown 7/24/23 | o JSON gerado deriva do ledger e andou (11/21/22) | já era relacional (md == JSON); o JSON foi regerado pelo passo `CENSO_DAS_ESTRADAS` (o `validate_system_map` não o corre) e o md sincronizado |
| `test_a_collection_preserva_o_fato.test_a_fronteira_recusa_ficar_calada…` | `SOURCE_LOCATION` transportado em todos | «Terlano (BZ)» (IT-T3-011) não está no gazetteer → `NAO SEI` honesto; e uma observação `IDENTITY_FAILED` atravessava a fronteira | transportado ⇔ valor conhecido; `NAO SEI` leva `BASE` e não está em falta. **Dono corrigido:** a prova deixa de reprocessar observações sem `DOCUMENT_ID` |
| `test_legado_fora_do_fluxo.test_hoje_nenhum_dos_treze_tem_equivalente` | `CANONICAL_EQUIVALENTS == 0` | a BC2 colheu pela porta um PDF igual a um dos treze | equivalentes == corpos cujo sha está no ledger, cada um com disposição `EQUIVALENTE` |
| `…test_preservar_nao_e_admitir` | `LEGACY_KEEP == 13` | um dos treze passou a `EQUIVALENTE` | disposições cobrem todos os corpos; `LEGACY_KEEP` = corpo existe ∧ sem equivalente ∧ recoleta ≠ SIM |
| `…test_o_documento_provar_o_publicador_nao_prova_a_aquisicao` · `…test_os_cinco_campos_de_aquisicao_sao_medidos_a_parte` | os cinco `ORIGINAL_*` False | o **dono** (`provas/o_legado_fora_do_fluxo.py`) fazia `aquisicao_provada = bool(obs)`: equivalência de bytes promovia a proveniência | **bug real corrigido no dono:** `EQUIVALÊNCIA NÃO TRANSFERE PROVENIÊNCIA`; os testes ficam como estavam |
| `test_a_linhagem_do_ready_e_do_raw_asset.test_quem_criou_objecto_tem_caminho…` | `criou ⇔ tem caminho` | **conflito de lei antigo:** o coletor escreve `RAW_PATH` em `SEEN_AGAIN` de propósito («NÃO CRIEI AGORA ≠ NÃO HÁ BYTES») | **decisão escrita:** `RAW_OBJECT_CREATED` = «materializei agora?», `RAW_PATH` = «onde estão os bytes?»; criou ⇒ caminho; caminho ⇒ documento e sha; falhou ⇒ nenhum |
| `…test_reobservacao_nunca_guarda_objecto_novo` | `SEEN_AGAIN ⇒ RAW_OBJECT_CREATED False` e caminho de uma anterior | o ledger é rastreado e o armazém não é inteiro: uma árvore nova volta a materializar os mesmos bytes | `SEEN_AGAIN ⇒` existe anterior do mesmo documento com o **mesmo sha**; se ambas apontam ficheiro, mesmo nome |
| `…test_um_objecto_guardado_por_impressao_digital` | criados == shas distintos (livro inteiro) | o mesmo sha pode ser criado em duas árvores; bytes iguais em duas fontes | por corrida, `(fonte, sha)` criado no máximo uma vez; todo criado tem sha e caminho |

`STALE_TESTS_FOUND` = 10 · `STALE_TESTS_FIXED` = 10 (9 por invariante + 1 conflito de lei decidido por escrito) · donos corrigidos: 2 (`o_legado_fora_do_fluxo.py`, `a_collection_preserva_o_fato.py`) · números mágicos trocados por outros números: **0**.

Ficou fora, por não estar entre as 10 e já ser vermelha na base: `test_a_linhagem….test_a_contagem_de_observacoes_no_livro_nao_muda` (`175 != 300`) — contagem fixa sobre o ledger; candidata à mesma regra numa missão própria.

## 6 · Reconciliar os contadores da BC2

| `NAME` | `OWNER` | `GRAIN` | `WHAT_IT_COUNTS` | retry? | canário? | sem documento? | storage reutilizado? | pré-existente? | `TIME_WINDOW` | valor |
|---|---|---|---|---|---|---|---|---|---|---|
| `REQUESTS_SELECTED` | driver `bc2.py` | pedido | fontes escolhidas | — | não | — | — | não | lote | **113** |
| `SOURCE_REQUESTS_EXECUTED` | driver | pedido | invocações do orquestrador | 2.ª passagem só das 42 que morreram na receita (não conta duas vezes) | não | sim | — | não | lote | **113** |
| `RUNS_CREATED` | `collection_run` (Sala) | corrida | linhas de corrida | não | inclui 2 corridas de prova do IT-T2-001 | sim | — | não | 11:04–11:29Z | **111** = 109 pedidos + 2 provas; 4 pedidos morreram no executor antes de a corrida nascer (IT-T1-005, IT-T1-011, IT-T2-006, IT-T5-032) |
| `SOURCES_WITH_SUCCESS` | driver ↔ ledger | fonte | 1.ª observação `HEALTHY` | — | não | não | — | não | lote | **90** (o «91» conta corridas RAW PASS/PARTIAL, que inclui a prova e o IT-T3-011 parcial) |
| `SOURCES_WITH_FAILURE` | driver ↔ ledger | fonte | sem documento | — | não | sim | — | não | lote | **23** = 17 `DISCOVERY_FAILED` + 2 `TRANSPORT` + 4 corrida morta (o «20» excluía-lhe as 4 sem corrida ou as 2 de transporte, conforme o grão) |
| `RAW_OBSERVATIONS_CREATED` | `raw_asset` | observação | linhas, **incluindo** envelopes JSON de observações falhadas e as corridas de prova | — | sim | sim | — | não | 11:04–11:29Z | **116** = 93 documentos + 21 envelopes + 2 prova |
| ledger `observations` | ledger italiano | observação | uma linha por alvo (ARPAV 4 zonas, AGRIOS 3) | — | não | sim (17+2+2) | — | não | 113 corridas | **114** |
| `raw_objects_created` (ledger) | coletor | ficheiro | `RAW_OBJECT_CREATED = true` | — | não | não | não | não | 113 corridas | **93** |
| `STORAGE_OBJECTS_CREATED` / `REUSED` | `storage_object` | objecto por sha | novos / já existentes | — | sim | sim (JSON) | sim | — | 11:04–11:29Z | **107 / 7** |

`BIG_COLLECTION_METRICS_RECONCILED = YES` · `METRIC_GRAINS = pedido · corrida · fonte · observação · ficheiro · objecto (por sha)` — nenhum foi igualado à força; nenhum bug de owner nestes contadores.

## 7–13 · Os HTML

| campo | valor |
|---|---|
| causa (medida, não assumida) | **B** — nenhum executor declarava `text/html` (`ingresso.executor_para("text/html") → None`), logo `DERIVACAO_ESPECIE_NAO_SUPORTADA` → `NOT_APPLICABLE`; **E** parcial — 13 páginas são navegação (medido, não filtrado). Não A, C nem D |
| capacidade existente? | nenhuma em produção (só um `HTMLParser` no scanner do mapa). Sem segundo parser: nasceu o primeiro, `coleta/executor_texto_de_html.py` (`html.parser` da biblioteca-padrão, mesma ficha e ponte forward do executor de PDF, `NETWORK_REQUIRED: NO`), registado em `_DONOS_DA_DERIVACAO` |
| `HTML_NOT_APPLICABLE_BEFORE` | **42** na BC2 (o «58» = 42 HTML + 15 JSON de falhas + 1 CSV) · HTML colhidos na BC2: 46 (4 não chegaram à derivação por outra razão) · HTML no banco: 49 (3 pré-BC2) |
| `HTML_PIPELINE_CANARY` | PASS — conteúdo (IT-T9-009 artigo, IT-T5-033 notícia: CONTENT), complexa (IT-T2-007, 3,8 MB: CONTENT/PRESENT), sem conteúdo útil (IT-T1-002 lista de comunicados: NAVIGATION); 14 provas unitárias sem rede |
| rota do reprocessamento | `italy_executor.colher(run)` reconstrói o envelope do ledger → `orquestrador --so-a-porta --colheita-da-corrida=<run> --filtro pais=IT --filtro fonte=X --filtro universo=T` → corrida nova → ingresso (RAW reutilizado) → DERIVED (executor de HTML) → STRUCTURED → Admissão → Sala. Bancada OPERACIONAL + `SINTONIA_ARMAZEM_RAIZ` |
| `NETWORK_ACQUISITION_CALLS_DURING_REPROCESS` | **0** — o executor de coleta não é chamado com `--so-a-porta`; `HTTP(S)_PROXY=127.0.0.1:9` (porta morta) em todas as 50 passagens, nenhuma falhou por rede; `COST_USD` 0 em todas |
| `HTML_REPROCESS_ATTEMPTED` | **46** |
| `HTML_DERIVED_CREATED` / `REUSED` / `FAILED` | **42** / 0 / **4** |
| `HTML_STILL_NOT_APPLICABLE` | **0** |
| os 4 `FAILED` | IT-T2-007, IT-T2-010, IT-T3-019, IT-T5-035: etapa RAW `FAIL` (`RAW_PERSISTENCE_FAILED`, balde `unknown`, sem mensagem), determinístico (2 passagens), com a linha `raw_asset` escrita, bytes e endereço iguais aos dos 42 que passaram, e a consulta de identidade a devolver a linha *a posteriori*. Causa **NÃO SEI**; não forçado |
| `TEXT_BYTES` | 246.654 bytes de texto derivado (42 ficheiros) · `HTML_KIND`: CONTENT 27 · NAVIGATION 13 · MIXED 6 |
| tabela por documento | `data/derivados/HTML-REPROCESSO-2026-09-20.json` (RAW_ID · SOURCE_ID · HTML_KIND · CONTENT_EXTRACTABLE · DERIVATION_RESULT · TEXT_BYTES · ADMISSION_INPUT_READY · antes/depois) |
| `ADMISSION_BEFORE` / `AFTER` (só os 46) | NAO_SEI 46 → **SIM 11 · NAO 4 · NAO_SEI 7 · NAO_SE_APLICA 24** (régua intocada: nenhuma keyword, threshold, universo ou regra mudou) |
| `NEW_SIM` / `NEW_SALA_ITEMS` | **11 / 11** (T5 ×9, T7-013, T9-011); Sala 17 → **28** |
| gate da Sala | `SIM_WITHOUT_SALA` 0 · `SALA_WITHOUT_SIM` 0 · `NAO_SEI_IN_SALA` 0 · `NAO_SE_APLICA_IN_SALA` 0 |
| mudaram de veredito | 39 de 46 (11 para SIM, 4 para NAO, 24 para NAO_SE_APLICA por falta de régua T1/T2/T10/T11/T12); 7 continuam NAO_SEI depois de legíveis — resultado honesto |

## 15 · Reconciliação (janela do reprocessamento 13:09Z→)

`RAW_SEM_RUN` 0 · `RAW_SEM_SOURCE` 0 · `RAW_SEM_STORAGE` 0 · `ZERO_BYTE_RAW` 0 · `MISSING_EXPECTED_BYTES` 0 (BC2; 7 pré-BC2 declarados em §3) · `SHA_MISMATCH` 0 · `ORPHAN_DERIVED` 0 · `ORPHAN_ADMISSION` 0 · `ORPHAN_SALA` 0 · corridas 50 (46 + 4 repetições) · `STORAGE_OBJECTS_REUSED` 50 · `DERIVED_CREATED` 42 · `PAID_USD` 0.
`RECONCILIATION_STRUCTURAL_ERRORS = 0`.

## 16–17 · Testes e mapa

| campo | valor |
|---|---|
| `PRISTINE_FAILURES` | 119 nomes (base `606974c3`, Ran 4949, failures=105, errors=14) |
| `FINAL_FAILURES` | 86 nomes (Ran 4975 · failures=106 · errors=14 · skipped=190), suíte inteira corrida COM `SINTONIA_ARMAZEM_RAIZ` declarada |
| `NEW_FAILURES` | **0** por nome depois de duas re-medições por módulo: a suíte inteira mostrou 2 nomes novos — `test_c4g….test_a_porta_conhece_pdf_E_midia_e_nada_mais` (trava de método: a espécie nova `text/html` tem de ser declarada nessa prova; declarada, 12/12) e `test_M5_o_ponto_fixo_existe_e_esta_alcancado_nesta_arvore` (o carimbo do mapa, que só fecha com a cadeia depois do último commit; ver §17) — e 1 nome da base sarou (`test_quem_criou_objecto_tem_caminho…`) |
| `SYSTEM_MAP_CHECK` | PASS ·  conferido depois do commit do mapa que se segue a este ficheiro (se esta linha estivesse errada, o portão 2b e o test_M5 diriam DIFERENTE — ver a mensagem final da sessão) |
| `KNOW_HOW_DELTA` | §160 |

## Commits e entrega

| campo | valor |
|---|---|
| `INITIAL_HEAD` | `b4ff70ae` |
| `FINAL_HEAD` / `REMOTE_HEAD` | o commit do mapa que se segue ao commit deste ficheiro (`git log -1`); igual no remoto — SHA exacto na mensagem final |
| `WORKTREE` | `cutover-v2` (limpa no fim; o `MISSAO-GARGALOS-BC2.md` entra na árvore) |
| `COMMITS` | 5 até este relatório (+ os do relatório e do mapa que se lhe seguem) · `PUSH_STATE` = `LOCAL == REMOTE = YES` · sem force |
| `MODEL_EFFECTIVE` | claude-fable-5-1 |

---

## Para o dono, em linguagem simples

**(1) Onde os documentos ficam guardados agora.** Numa pasta própria, fora do repositório e fora da pasta temporária do Windows: `sintonia-sala-italia\armazem`, ao lado do banco da Sala. É a mesma pasta para sempre, não a pasta de trabalho de uma sessão. Dentro dela há um ficheiro-marcador que diz «isto é operacional». Os 107 documentos da Big Collection 2 estão lá inteiros, conferidos byte a byte. Faltam 7 ficheiros mais antigos, de 18 e 19 de setembro, que nunca chegaram a esta máquina; não inventei nenhum.

**(2) Porque é que os testes já não conseguem apagá-los.** Antes, o programa oficial guardava os documentos na pasta `XX` dentro do repositório, que é a mesma pasta onde os testes deitam o lixo deles e que limpam no fim. Agora há duas regras: quando o banco é o operacional, o programa **tem** de receber uma pasta fora do repositório, senão recusa-se a correr; e os testes só podem apagar a pasta `XX` do repositório ou a pasta temporária que eles próprios criaram. Se alguém tentar apagar uma pasta com o marcador, o programa recusa. Provei-o com uma sentinela: corri os testes que apagam, e o armazém continuou com os mesmos 136 ficheiros.

**(3) O que eram as 10 falhas.** Não eram erros no programa. Eram testes que tinham um número escrito à mão («são 7 fontes», «são 13 documentos antigos», «nenhum tem equivalente») que era verdade no dia em que foram escritos e deixou de ser quando a coleta cresceu. Reescrevi-os para dizerem a regra em vez do número: «as fontes com recibo são as que estão no livro», «cada documento antigo tem uma e só uma disposição». Uma das dez era um desacordo entre dois documentos da casa sobre o que significa «vi outra vez»; decidi por escrito qual vale e porquê. E encontrei dois erros reais em ferramentas de prova, que corrigi: uma dava proveniência a um documento antigo só porque outro igual foi recolhido hoje; a outra julgava documentos sem identidade.

**(4) Porque é que 113 e 111 eram números diferentes.** Contavam coisas diferentes. 113 são os pedidos que fiz; 111 são as corridas que o banco registou: 109 dos pedidos, mais 2 corridas de teste que fiz antes do lote com a mesma fonte. Os 4 pedidos que faltam morreram no programa de coleta antes de o banco abrir uma corrida. O mesmo vale para 90/91 e 116/114/93: fonte não é corrida, corrida não é observação, observação não é ficheiro, e um envelope de uma tentativa falhada conta como linha no banco mas não como documento. Escrevi o quadro com o grão de cada número.

**(5) Quantas das 58 páginas conseguimos finalmente ler.** As 58 eram 42 páginas HTML mais 16 outras coisas (envelopes de falhas e um CSV). Páginas HTML recolhidas: 46. Dei à casa a peça que faltava, que transforma uma página em texto sem ir à internet, e passei as 46 outra vez pelo caminho oficial, sem nenhuma ligação à rede e sem gastar nada: **42 ficaram legíveis**; 4 não passaram por uma falha na etapa de guardar cuja causa não consegui provar, e ficou anotada.

**(6) Quantas mudaram de veredito depois de serem realmente lidas.** 39 das 46. Antes, todas as 46 eram «não sei» porque a régua nunca tinha visto texto. Depois: **11 passaram a SIM** e entraram na Sala (que passou de 17 para 28 documentos), 4 foram recusadas com NÃO, 24 ficaram «não se aplica» porque não existe régua escrita para esses territórios, e 7 continuam «não sei» mesmo lidas — o que é honesto. Não mexi na régua para fazer subir nenhum número.
