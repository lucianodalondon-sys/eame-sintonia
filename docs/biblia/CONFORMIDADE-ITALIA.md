# ITALY_COLLECTION_COMPLIANCE_MATRIX — apêndice C da Bíblia

**Perfil:** `ITALY_PROFILE_V1` · **Bíblia:** `V1.3` · **Data:** 2026-09-07 · **HEAD medido:** `4b3c0d4` (integração)

> Esta matriz mede a **implementação italiana** contra as 104 leis canônicas. Ela não é a
> lei: a lei está em [`../../BIBLIA-CANONICA-DA-COLETA.md`](../../BIBLIA-CANONICA-DA-COLETA.md).
>
> **`LAW = CANONICAL` para todas as 104. Isto aqui mede outra coisa: se já funciona.**
> Confundir os dois é o erro que esta separação existe para impedir.

**Escopo declarado:** `CURRENT IMPLEMENTATION COUNTRY = IT`. Espanha e França **não** foram
alteradas, medidas nem portadas nesta missão.

---

## O PLACAR

| estado | V1 | V1.1 | **V1.3** | |
|---|---:|---:|---:|---|
| `IMPLEMENTED` | 21 | 24 | **37** | há código no caminho produtivo e prova executável |
| `PARTIAL` | 23 | 42 | **47** | existe em parte, ou existe para um caminho e não para os outros |
| `ABSENT` | 4 | 11 | **18** | é lei, e não há implementação nenhuma |
| `NOT_APPLICABLE` | 0 | 1 | **2** | a lei não se aplica ao perfil italiano de hoje |
| `UNKNOWN` | 0 | 0 | **0** | — |
| **total** | 48 | 78 | **104** | |

> **DUAS LEIS DESCERAM DE `IMPLEMENTED` PARA `PARTIAL` em 08/09/2026 — e ninguém desfez
> trabalho nenhum.** A COL-LAW-106 e a COL-LAW-210 tinham sido dadas por cumpridas medindo
> **uma** estrada, a do PDF. A Itália tem duas: o coletor piloto também corre, e as suas 6
> corridas não aparecem no mapa (`PILOT_RUN` = 0 ocorrências no estado gerado) nem têm
> estado de fecho no ledger. Pela definição do próprio placar, «existe para um caminho e não
> para os outros» é `PARTIAL`. **A estrada do PDF continua exatamente como estava.**

> **O `ABSENT` subiu de 4 para 11, e isso não é a Itália a piorar: é a régua a crescer.**
> Sete coisas que antes nem eram medidas ganharam nome. Lacuna com nome é lacuna que alguém
> pode fechar.

**E `NOT_APPLICABLE` não é `ABSENT`.** Marcar como falha uma lei que não se aplica a esta
fonte ou a este perfil seria inventar dívida — e dívida inventada faz o placar mentir para
o lado que parece rigoroso.

---

## A MATRIZ

| LEI | ESTADO | EVIDÊNCIA | O QUE FALTA | PRÓXIMO PASSO |
|---|---|---|---|---|
| `COL-LAW-005` coletar ≠ admitir ≠ julgar | `PARTIAL` | `admissao/admissao.py` existe e o orquestrador entrega nela | as fontes italianas não passam pelo orquestrador; entram pelo `italy_recurrent_collect.mjs` direto | G-05 |
| `COL-LAW-006` RAW primeiro | `IMPLEMENTED` | `RAW_PRESERVED_BEFORE_PARSE` em 144 observações; ordem §8 do agendamento | — | — |
| `COL-LAW-007` RAW ≠ derivado | `IMPLEMENTED` | `BROWSER_RENDERED_EXTRACT` é tipo próprio na matriz de contratos | — | — |
| `COL-LAW-008` derivação tem linhagem | `PARTIAL` | a cadeia inversa existe para a rota paga; e os **43 textos de PDF declaram linhagem completa** — `PARENT_ARTIFACT_ID`, `PARENT_SHA256`, `DERIVATION_TYPE`, executor, versão e `DERIVED_AT` (medido: 43/43) | os derivados de **HTML** italianos continuam sem `parent_artifact_id` | G-06 |
| `COL-LAW-009` seis entidades distintas | `IMPLEMENTED` | gavetas + `P2_PASTA_BATE_COM_MAPA` no CI | — | — |
| `COL-LAW-010` pedido não conhece implementação | `IMPLEMENTED` | `pedido/pedido.py`, recusa `AUTOMATICO_EVENTO` com motivo | — | — |
| `COL-LAW-011` um dono da orquestração | `PARTIAL` | `orquestrador/orquestrador.py` assina o recibo | nenhum executor italiano está no `EXECUTORES` da receita | **G-05** |
| `COL-LAW-012` controle ≠ dado | `PARTIAL` | `larga_em` declarado nos 4 executores da receita | os executores `.mjs` italianos não declaram onde largam | G-05 |
| `COL-LAW-013` contrato comum de executor | `PARTIAL` | os 4 contratos obrigatórios estão declarados | `CHECK` e `STATE` não existem como verbo comum | G-07 |
| `COL-LAW-014` capacidades declaradas | `PARTIAL` | 6 dos 12 campos em `receitas.py::EXECUTORES` | `cost_class`, `supports_checkpoint`, `supports_retry`, `countries`, `modes`, `artifact_types` | G-07 |
| `COL-LAW-015` receita é derivada | `IMPLEMENTED` | fontes vêm de `sources.generated.json`; o plano nomeia o que não sabe percorrer | — | — |
| `COL-LAW-016` estado incremental é do executor | `PARTIAL` | `checkpoint_coleta` existe para a rota paga | as 3 fontes `FORWARD_ONLY` não têm cursor: comparam hash | G-08 |
| `COL-LAW-017` checkpoint e trava do gasto | `IMPLEMENTED` | `coleta/coleta_checkpoint.py` + `tests/test_coleta_resiliente.py` | — | — |
| `COL-LAW-018` rota mais barata capaz primeiro | `PARTIAL` | o portão grátis do contrato do ator roda antes do gasto | não existe `ROUTE_POLICY`: há **um** executor por alvo | **G-04** |
| `COL-LAW-019` Apify é rota paga de escalada | `ABSENT` | política de chaves escrita; `maxTotalChargeUsd` em uso | os 5 campos (`WHY_PAID_ROUTE`, `CHEAPER_ROUTE_ATTEMPTED`, `CHEAPER_ROUTE_RESULT`, `ESCALATION_REASON`) **não existem em ficheiro nenhum** | **G-04** |
| `COL-LAW-020` rota bem-sucedida tem memória | `ABSENT` | — | `last_successful_route` não existe | G-09 |
| `COL-LAW-021` não coletar de novo sem necessidade | `PARTIAL` | hash por documento; `SEEN_AGAIN` com zero bytes guardados | não há `ETag`/`Last-Modified` **antes** do fetch: baixa-se para comparar | G-10 |
| `COL-LAW-022` toda corrida tem identidade | `PARTIAL` | 13 corridas no `RUN-MANIFEST`, 6 no ledger italiano | **dois formatos**; o italiano não tem `COST_USD` nem `STATUS` | **G-02** |
| `COL-LAW-023` reconciliação entre portas | `PARTIAL` | `padrao_da_coleta.py` mede 10 regras no CI | `DISCOVERED → EMITTED → RAW_LANDED → READY` não é medido em nenhuma corrida | **G-03** |
| `COL-LAW-024` zero inesperado não é sucesso | `IMPLEMENTED` | `SUCCEEDED`+0 itens vira `PARTIAL`; lista vazia é `FAILED` | — | — |
| `COL-LAW-025` retry tem critério | `ABSENT` | — | `TRANSIENT` vs `PERMANENT` não existe; não se lê `Retry-After` | G-11 |
| `COL-LAW-026` circuit breaker | `ABSENT` | — | nada impede martelar uma fonte que falha sempre | G-12 |
| `COL-LAW-027` quarentena e replay | `PARTIAL` | `--so-a-porta` reprocessa sem colher de novo | não há fila de quarentena com `attempts`/`last_error` | G-13 |
| `COL-LAW-028` a fonte tem saúde | `IMPLEMENTED` | `source_health.py` + `italy_source_health.mjs`, vocabulários idênticos | — | — |
| `COL-LAW-029` source drift e controle negativo | `IMPLEMENTED` | `--negativos` corrompe 8 documentos em memória e exige `FAILED` | — | — |
| `COL-LAW-030` mundo ≠ pipeline | `PARTIAL` | `COLLECTOR_VERSION` e `SOURCE_CONTRACT_VERSION` no ledger italiano | `PIPELINE_VERSION` não existe; o `RUN-MANIFEST` não tem nenhum dos três | G-02 |
| `COL-LAW-031` temporalidade | `PARTIAL` | `FACT_TIME` separado em 144 observações; `v21_datas.py` recusa prosa | ⚠️ `admissao/admissao.py:169` aceita `published_at` como tempo do fato | **G-01** |
| `COL-LAW-032` geografia | `IMPLEMENTED` | lei no core + leitor italiano + constraints da migration 015 | — | — |
| `COL-LAW-033` procedência | `IMPLEMENTED` | `RAW_SHA256` em 144 de 144 observações; contrato V2.1 falha fechado | — | — |
| `COL-LAW-034` identidade | `PARTIAL` | `identidade_valida()` recusa campos que mudam entre execuções | `ITEM_ID` e `ARTIFACT_ID` não são campos próprios no ledger italiano | G-06 |
| `COL-LAW-035` UNKNOWN | `IMPLEMENTED` | `P7_NAO_SEI_VIVE` no CI; `NOT_PRESERVED ≠ NÃO SEI` em código | ⚠️ cinco grafias do sentinela (C-003, decisão em aberto) | **G-14** |
| `COL-LAW-036` no_match não prova não | `PARTIAL` | `f_relevancia_ao_caso` derivada com motivo, sem score | a admissão italiana ainda usa lista de palavras direta | G-15 |
| `COL-LAW-037` erro não vira não | `IMPLEMENTED` | `VPN_FAILURE ≠ SOURCE_FAILURE` provado em operação real | — | — |
| `COL-LAW-038` dois eixos de resultado | `IMPLEMENTED` | `RESULTADOS` e `STATUS_RUN` são listas separadas | — | — |
| `COL-LAW-039` país | `PARTIAL` | `COUNTRY_SCOPE` no pedido; gaveta por país | o escopo não é conferido dentro do executor: nada barra um item ES numa corrida IT | G-16 |
| `COL-LAW-040` país não é língua | `PARTIAL` | `LANGUAGE` é campo próprio em `voz.py` | o ledger italiano não tem campo de língua | G-17 |
| `COL-LAW-041` vocabulário contextual | `PARTIAL` | as palavras da busca vivem em `regras/` e decidem `CROP`/`ISSUE` | a mesma lista serve busca e admissão | G-15 |
| `COL-LAW-042` admissão auditável | `PARTIAL` | o livro guarda item, universo, regra, versão, motivo, prova | as observações italianas nunca passaram pela porta | **G-05** |
| `COL-LAW-043` READY não é «terminou» | `PARTIAL` | contrato de saída fixo em `pronto_para_inteligencia()` | nenhum item italiano chegou a `PRONTO_PARA_INTELIGENCIA` | G-05 |
| `COL-LAW-044` armazenamento ≠ estado | `IMPLEMENTED` | D-003 + a exceção da rota não replicável, com `RAW-GATE-ES.json` | — | — |
| `COL-LAW-045` coleta manual tem contrato | `PARTIAL` | `CAPTURE_METHOD` existe no `RUN-MANIFEST` | `ACTOR_TYPE` não distingue pessoa de máquina | G-18 |
| `COL-LAW-046` lei do espelho | `IMPLEMENTED` | `P1_SEM_DRIFT` no CI, a cada push | — | — |
| `COL-LAW-047` o mapa é saída | `IMPLEMENTED` | `state.generated.json` regerado e conferido | — | — |
| `COL-LAW-048` tipos de conexão | `IMPLEMENTED` | `P5_ARESTA_PROVADA` exige ficheiro e linha | — | — |
| `COL-LAW-049` declared/code/observed | `PARTIAL` | `DECLARED` e `CODE` existem | `OBSERVED` não existe: nenhuma aresta é confirmada por corrida real | G-19 |
| `COL-LAW-050` current ≠ target | `IMPLEMENTED` | `official`/`futuro`/`legacy` são três estados no mapa | — | — |
| `COL-LAW-053` cadastro único de fonte | `IMPLEMENTED` | `sources.generated.json` reconcilia atlas e master italiano | — | — |
| `COL-LAW-069` nenhuma lei muda em silêncio | `IMPLEMENTED` | `py provas/valida_biblia.py` + diário de decisões | — | — |

---

## A MATRIZ — LEIS DA EMENDA V1.1

> `APLICA-SE` responde: **esta lei vale para o perfil italiano de hoje?** Uma lei que não se
> aplica não conta como falha.

### PARTE XVI — a placa de vídeo

| LEI | APLICA-SE | ESTADO | EVIDÊNCIA | O QUE FALTA | PRÓXIMO PASSO |
|---|---|---|---|---|---|
| `COL-LAW-101` tudo renderizável | SIM | `PARTIAL` | 109 peças e 357 ligações; a estrada do PDF renderiza ocorrências, conteúdos, entrada, derivados, OCR, erro, perda e estado da corrida — tudo derivado da medição | as outras estradas ainda não expõem contagens; `HEALTH` por peça não existe | G-37 |
| `COL-LAW-102` as quatro verdades | SIM | `PARTIAL` | `DECLARED` e `CODE` medidos; `EXPECTED` para o não provado | `OBSERVED` e `BIBLE` não existem no estado do mapa | **G-19** |
| `COL-LAW-103` derivável não se escreve | SIM | `PARTIAL` | `state.generated.json`, `portao.py` e `portoes_eame.py` derivam tudo | `COMPLIANCE` e `GAP` estão em Markdown escrito à mão — este ficheiro | **G-21** |
| `COL-LAW-104` componente renderizável | SIM | `PARTIAL` | na estrada do PDF: `COUNTS`, `LAST_ERROR`, `RUN_ID` e a ressalva de `COST` aparecem, com a medição de origem citada | `HEALTH` e `APPLICABLE_LAWS` por peça continuam ausentes; e só a estrada do PDF os expõe | G-37 |
| `COL-LAW-105` conexão renderizável | SIM | `PARTIAL` | `TYPE` + `EVIDENCE` (ficheiro e linha) em todas as 325 | `OBSERVED`, `COUNT_IN/OUT`, `LOST`, `ARTIFACT_TYPE` não existem | G-19 |
| `COL-LAW-106` corrida renderizável | SIM | `PARTIAL` | **na estrada do PDF está inteiro:** a corrida aparece no mapa com `RUN_ID`, `ROUTE`, `STATE_BEFORE/AFTER`, pré-voo, contagens por etapa, `LOST`, OCR e erro | **as 6 corridas do coletor piloto não aparecem em lado nenhum do mapa** — medido: `PILOT_RUN` ocorre **0 vezes** em `state.generated.json`. Uma estrada renderizável de duas é `PARTIAL` pela definição do placar | G-38 |
| `COL-LAW-107` a perda aparece na aresta | SIM | `PARTIAL` | na estrada do PDF a seta diz «entraram 43, saíram 43, PERDIDOS 0» e explica que a conta é entre etapas comparáveis | vale só para esta estrada; nas outras a reconciliação ainda não existe (G-03) | G-03 |
| `COL-LAW-108` quatro vistas, uma verdade | SIM | `PARTIAL` | uma fonte só (`state.generated.json`); há filtro de vista (`views`) | faltam as vistas RUN, PROBLEMAS e BÍBLIA | G-21 |
| `COL-LAW-109` zoom; layout não governa | SIM | `IMPLEMENTED` | três níveis na app: faixa → peça → raio-X com ficheiro e linha | — | — |
| `COL-LAW-110` observabilidade por nascimento | SIM | `IMPLEMENTED` | `P9_CODIGO_DECLARADO` reprova peça invisível, em cada push | — | — |
| `COL-LAW-111` não é segunda verdade | SIM | `IMPLEMENTED` | o gerador lê código, contratos e medições; `P1_SEM_DRIFT` prova | — | — |
| `COL-LAW-112` evidência navegável | SIM | `PARTIAL` | `P5_ARESTA_PROVADA` e `P5_PROVA_APONTAVEL` exigem ficheiro e linha reais | o lado do `RUN` e o do `COMPLIANCE` não apontam para nada | G-19 |

### PARTE XVII — as leis roubadas

| LEI | APLICA-SE | ESTADO | EVIDÊNCIA | O QUE FALTA | PRÓXIMO PASSO |
|---|---|---|---|---|---|
| `COL-LAW-201` **artefato não é fato** | SIM | `PARTIAL` | o ledger italiano guarda `SOURCE_DATE`, `FACT_TIME` e `RAW_SHA256` por documento | `FACT_TIME` mora no **artefato**, não num claim; e a admissão ainda aceita `published_at` (C-001) | **G-01 → G-22** |
| `COL-LAW-202` `ARTIFACT → CLAIM` | SIM | `ABSENT` | — | não existe entidade de claim. É `TARGET` declarado | G-22 |
| `COL-LAW-203` procedência até o valor | SIM | `PARTIAL` | `PROVENANCE_RECOVERED_VIA`; o contrato V2.1 recusa carimbo que promete o que não tem | normalização de cultura/produto não guarda `ORIGINAL_VALUE` ao lado | G-23 |
| `COL-LAW-204` dedupe não destrói história | SIM | `PARTIAL` | `WITHOUT_STRUCTURAL_ID_COUNT` publicado; duplicata→canônico preservada em `voz.py` | não há `CANONICAL ENTITY` com registros de origem por baixo | G-23 |
| `COL-LAW-205` fonte ≠ endpoint | SIM | `PARTIAL` | 13 contratos italianos declaram rota, saída e identidade por endpoint | fonte e endpoint são a mesma linha no registro; `ETag` e checksum estão na fonte | **G-24** |
| `COL-LAW-206` três identidades | SIM | `PARTIAL` | `SOURCE_ID` estável (`IT-T3-005`) separado da URL; `DOCUMENT_ID ≠ BYTE_ID` | `SOURCE_NATIVE_ID` não é campo; não há histórico de rekey | G-24 |
| `COL-LAW-207` descobrir ≠ buscar ≠ derivar | SIM | `ABSENT` | — | as três são um passo só; por isso a ARPAV baixa 12,8 MB para depois ver que nada mudou | **G-25** |
| `COL-LAW-208` o registry é a memória | SIM | `PARTIAL` | `sources.generated.json` reconcilia atlas e master; health e cadência existem | `LAST_ATTEMPT/SUCCESS/FAILURE/CHANGE` e `LAST_SUCCESSFUL_ROUTE` não são campos da ficha | G-24 |
| `COL-LAW-209` corrida é história | SIM | `ABSENT` | — | não há `PARENT_RUN_ID` nem `REPAIR_REASON` | G-26 |
| `COL-LAW-210` `COMPLETE` só no fim | SIM | `PARTIAL` | **na estrada do PDF está inteiro:** `RUN_STATE` nasce de seis condições medidas e é escrito por último (G-38) | **o ledger do coletor piloto não tem estado de fecho nenhum** — medido: as 6 linhas de `runs.ndjson` têm `STARTED_AT`/`FINISHED_AT` e nenhum campo de `COMPLETE`. Quem lê aquele ledger continua a inferir fim pela existência de ficheiros | **G-26** |
| `COL-LAW-211` configuração congelada | SIM | `PARTIAL` | `COLLECTOR_VERSION`, `GIT_HEAD`, `SOURCE_CONTRACT_VERSION` no ledger italiano | `PLAN_VERSION`, `CONFIG_HASH`, `BIBLE_VERSION`, `VOCABULARY_VERSION` não existem | G-02 |
| `COL-LAW-212` watermark | SIM | `ABSENT` | — | a coleta olha «agora»; não há `WINDOW_START/END` | G-27 |
| `COL-LAW-213` incremental não é só somar | SIM | `ABSENT` | — | só há `CREATE`; sumiço não é distinguido de deleção | G-27 |
| `COL-LAW-214` zero tem semântica | SIM | `PARTIAL` | lista vazia é `FAILED`; `SEEN_AGAIN` é zero esperado e guarda zero bytes | as três palavras não são valores gravados | G-28 |
| `COL-LAW-215` fail loud | SIM | `PARTIAL` | `--negativos`; contrato do ator recusa campo desconhecido; falha fechada em toda a casa | schema drift não tem estado próprio: cai em `FAILED` genérico | G-28 |
| `COL-LAW-216` três eixos de confiança | SIM | `PARTIAL` | `SOURCE_HEALTH` inteiro e medido | `SOURCE_RELIABILITY` e `CLAIM_CONFIDENCE` não existem — e é **certo** que não existam antes do claim | G-22 |
| `COL-LAW-217` `FIRST_SEEN` / `LAST_SEEN` | SIM | `ABSENT` | — | `CAPTURED_AT` faz as vezes dos dois, e não é nenhum deles | G-23 |
| `COL-LAW-218` bulk ≠ API pontual | **NÃO** | `NOT_APPLICABLE` | — | ciência não está no perfil italiano de hoje. **Não é dívida** | quando a ciência entrar |

---

## A MATRIZ — LEIS DA EMENDA V1.2

### PARTE XVIII — a infraestrutura

| LEI | APLICA-SE | ESTADO | EVIDÊNCIA | O QUE FALTA | PRÓXIMO PASSO |
|---|---|---|---|---|---|
| `COL-LAW-301` infra ≠ autoridade semântica | SIM | `IMPLEMENTED` | nenhum consumidor trata tabela como verdade: a admissão e o livro de decisões são os donos | — | — |
| `COL-LAW-302` GitHub guarda a engenharia | SIM | `IMPLEMENTED` | 1.151 ficheiros · 21 migrations · ordem da cadeia num dono só · SQL gerado e versionado antes de correr | — | — |
| `COL-LAW-303` GitHub não é banco operacional | SIM | `ABSENT` | — | ⚠️ recibo, 144 observações e **12 MB de bytes** da Itália vivem em Git (`italy_recurrent_collect.mjs:144`) | **G-30** |
| `COL-LAW-304` Supabase é a memória operacional | SIM | `PARTIAL` | `collection_run`, `raw_asset`, `checkpoint_coleta`, `fonte_externa` existem e o caminho ES os povoa | a Itália não escreve em nenhum deles | **G-30** |
| `COL-LAW-305` Supabase guarda, não julga | SIM | `IMPLEMENTED` | nenhum caminho promove linha a canônica por estar gravada | — | — |
| `COL-LAW-306` ninguém escreve por conhecer a tabela | SIM | `IMPLEMENTED` | **7 caminhos medidos, 7 canônicos, 0 bypasses**; a credencial só existe no runner | — | — |
| `COL-LAW-307` corrida ligada à engenharia | SIM | `PARTIAL` | o ledger italiano guarda `GIT_HEAD`, `COLLECTOR_VERSION`, `SOURCE_CONTRACT_VERSION` | o `RUN-MANIFEST` europeu não guarda versão de engenharia nenhuma | **G-02** |
| `COL-LAW-308` migration versionada ≠ aplicada | SIM | `IMPLEMENTED` | 21 migrations · a `008` confere o banco REAL · pré-voo recusa banco fora do esperado | — | — |
| `COL-LAW-309` Actions não é orquestrador | SIM | `IMPLEMENTED` | 11 workflows, nenhum decide relevância, rota ou admissibilidade | — | — |
| `COL-LAW-310` agenda ≠ política | SIM | `IMPLEMENTED` | gatilho de hora em hora + `--gate-hour` compara `Europe/Rome` no código; **zero cron** no GitHub | — | — |
| `COL-LAW-311` bytes ≠ metadata | SIM | `PARTIAL` | bucket `raw` privado, path é endereço e não identidade, round-trip provado com hash | a Itália guarda os bytes em Git e não escreve `raw_asset` | **G-30** |
| `COL-LAW-312` segredo não atravessa | SIM | `IMPLEMENTED` | 3 travas: `test_migrations.py:144` · varredura no publicado · `supabase-conexao` devolve booleano | — | — |
| `COL-LAW-313` ambiente na identidade da corrida | **NÃO** | `NOT_APPLICABLE` | não há `DEV`/`PREVIEW`/`PRODUCTION` declarados — um projeto só | **não é dívida** | quando houver ambientes |
| `COL-LAW-314` deploy ≠ verdade do dado | SIM | `IMPLEMENTED` | a Vercel publica `italia-portale/client`; nenhum dataset é canônico por estar publicado | — | — |
| `COL-LAW-315` conceito ≠ tabela | SIM | `IMPLEMENTED` | os contratos falam de `SOURCE`, `RUN`, `ARTIFACT` — nunca de nome de tabela | — | — |
| `COL-LAW-316` mapa mostra responsabilidade | SIM | `PARTIAL` | a visão principal tem 99 peças por responsabilidade; nenhuma tabela física é avenida | o raio-X não mostra tabela, bucket nem store | G-31 |

### PARTE XIX — o plano de referência

| LEI | APLICA-SE | ESTADO | EVIDÊNCIA | O QUE FALTA | PRÓXIMO PASSO |
|---|---|---|---|---|---|
| `COL-LAW-401` referência ≠ configuração | SIM | `ABSENT` | — | não existe Reference Set; o catálogo ADAMA ES importado é o parente mais próximo | **G-32** |
| `COL-LAW-402` abastecer referência é coleta | SIM | `ABSENT` | — | nenhuma cadeia `REFERENCE SUPPLY → VALIDATION → OWNER` | G-32 |
| `COL-LAW-403` referência declara autoridade | SIM | `ABSENT` | — | `AUTHORITATIVE_INTERNAL/EXTERNAL/DERIVED` não é campo em lado nenhum | G-32 |
| `COL-LAW-404` conferir ≠ mudar | SIM | `ABSENT` | — | `LAST_CHECKED`, `LAST_CHANGED` e `NEXT_DUE` não existem | G-32 |
| `COL-LAW-405` a referência tem história | SIM | `ABSENT` | — | sem `VALID_FROM`/`VALID_TO`, uma análise de 2024 usaria o portfólio de 2026 | **G-33** |
| `COL-LAW-406` definição no Git, registros na memória | SIM | `ABSENT` | — | nada construído dos dois lados | G-32 |


---

## A MATRIZ — LEIS DA EMENDA V1.3 (a integração)

> Estas quatro nasceram de medir a **primeira estrada real** contra a lei. O estado delas foi
> medido no Golden Path reproduzido nesta árvore, não copiado.

| LEI | APLICA-SE | ESTADO | EVIDÊNCIA | O QUE FALTA | PRÓXIMO PASSO |
|---|---|---|---|---|---|
| `COL-LAW-501` ocorrência ≠ conteúdo | SIM | `IMPLEMENTED` | 49 cópias · 43 conteúdos · 24 capturas distintas · `LOST = 0`, e os 6 grupos repetidos classificados pela **prova de captura**: 6/6 `INDEPENDENT_CAPTURES_SAME_CONTENT` (`censo_de_identidade_it.py`) | **11 das 49 cópias não têm prova de captura em registo nenhum** — não afeta a contagem, mas é procedência em falta | **G-40** |
| `COL-LAW-502` documento pronto ≠ fato pronto | SIM | `IMPLEMENTED` | a porta lê o ESTÁGIO e pergunta o que se aplica; 43 → 18 SIM · 19 NÃO · 6 NÃO_SEI, sem data inventada | — | — |
| `COL-LAW-503` ferramenta ausente ≠ documento quebrado | SIM | `IMPLEMENTED` | pré-voo no passo 0: sem a ferramenta a corrida para com `FAILED_PRECONDITION`, zero documentos tocados | — | — |
| `COL-LAW-504` árvore escaneada ≠ commit do mapa | SIM | `ABSENT` | ⚠️ um campo só (`PROVENANCE.HEAD`) para duas perguntas; 3 commits de «carimbo do HEAD» na história do ramo | `SOURCE_TREE_FINGERPRINT` e `MAP_ARTIFACT_COMMIT` separados | **G-35** |


---

# OS 10 MAIORES GAPS — RECALCULADOS NA V1.1, POR DEPENDÊNCIA

> **Não por facilidade.** Cada um só pode ser feito depois de o anterior estar de pé.
> A emenda V1.1 **mudou a ordem**: três gaps novos entraram à frente de gaps antigos,
> porque sem eles os antigos seriam construídos sobre um modelo errado.

### 1 · G-01 · `published_at` deixa de responder «quando o fato aconteceu»
`admissao/admissao.py:169` · **1 linha.**
Continua primeiro, e a V1.1 reforça o motivo: com a COL-LAW-201 sabemos agora que
`published_at` é do **artefato** e `FACT_TIME` é do **fato** — são de donos diferentes, não
são dois nomes para a mesma coisa. É o único gap que **piora sozinho**: cada item admitido
com tempo de fato falso é um item que alguém terá de reabrir.
**Destrava:** COL-LAW-031 · 201.

### 2 · G-22 · o artefato deixa de fingir que é o fato
**Gap novo, e ele passa à frente de quase tudo.**
Hoje o ledger italiano pendura `FACT_TIME` no documento. Enquanto o modelo for esse, cada
coisa construída em cima herda a confusão — inclusive a admissão, a inteligência e o mapa.
Não exige implementar extração de claim: exige **parar de exigir `FACT_TIME` no artefato** e
declarar `ARTIFACT → CLAIM` como o caminho do fato.
**Destrava:** COL-LAW-201 · 202 · 216 (os outros dois eixos de confiança só existem quando
existe claim).

### 3 · G-05 · a coleta italiana entra pelo pedido e sai pela porta
`coleta/italy_recurrent_collect.mjs` → `pedido/receitas.py::EXECUTORES`.
A Itália é um caminho paralelo: colhe, preserva e mede saúde, e **nunca passa pela
admissão**. Continua sendo a peça de que quase todo o resto depende — mas vem **depois** do
G-22, senão o caminho novo carrega o modelo velho para dentro da porta.
**Destrava:** COL-LAW-005 · 011 · 012 · 042 · 043.

### 4 · G-24 · a fonte deixa de ser o endpoint
`SOURCE` × `ENDPOINT` no registro (COL-LAW-205 · 206 · 208).
`ETag`, checksum, *schema fingerprint* e `last_successful_route` são do **endpoint** e hoje
estão na fonte. **Pré-requisito do G-25 e do G-09:** não se escolhe rota nem se lembra rota
sem ter onde as pendurar.
**Destrava:** COL-LAW-205 · 206 · 208 · 020.

### 5 · G-25 · descobrir deixa de custar o preço de buscar
`DISCOVER` · `FETCH` · `DERIVE` como capacidades separadas (COL-LAW-207).
É o gap com retorno mais direto e medido: a ARPAV baixa **~12,8 MB por corrida** para depois
descobrir que nada mudou. Depende do G-24 (endpoint) e do G-07 (capacidades declaradas).
**Destrava:** COL-LAW-207 · 021 · 018.

### 6 · G-02 · um formato de corrida só, com a configuração congelada
`RUN-MANIFEST` + os 5 campos italianos + `PLAN_VERSION` · `CONFIG_HASH` · `BIBLE_VERSION` ·
`ROUTE_POLICY_VERSION` · `VOCABULARY_VERSION` (COL-LAW-022 · 211).
Depois do G-05 há um caminho só, e é aí que faz sentido haver um recibo só.
**Destrava:** COL-LAW-022 · 030 · 211.

### 7 · G-26 · a corrida sabe quando acabou, e o passado não se reescreve
`RUNNING/PARTIAL/FAILED/COMPLETE` com fechamento atômico, e `PARENT_RUN_ID` para o reparo
(COL-LAW-209 · 210). Só é possível depois de haver um formato de corrida só (G-02).
**Destrava:** COL-LAW-209 · 210 · 013.

### 8 · G-03 · a reconciliação `DISCOVERED → READY`, e a perda visível na aresta
Só é medível com um caminho inteiro (G-05), um recibo só (G-02) e um fim de corrida
confiável (G-26). Sem ela, `EMITTED ≠ RAW_LANDED` continua invisível.
**Destrava:** COL-LAW-023 · 107.

### 9 · G-07 → G-04 · capacidades declaradas, e então a política de rota
`cost_class` · `supports_checkpoint` · `supports_retry` · `countries` · `modes` ·
`artifact_types`, e só depois a `ROUTE_POLICY` com os cinco campos de escalada paga.
**A ordem importa:** não há como escolher a rota mais barata **capaz** sem que cada executor
diga do que é capaz e quanto custa.
**Destrava:** COL-LAW-013 · 014 · 018 · 019.

### 10 · G-27 · o incremental fecha a janela, e sabe que apagar existe
`WINDOW_START/WATERMARK` + `CREATE/UPDATE/DELETE/MERGE` (COL-LAW-212 · 213).
Vem por último entre os grandes porque exige tudo o de cima: corrida com estado, fim
confiável e reconciliação. Fazê-lo antes produziria janelas fechadas sobre corridas que não
sabem quando acabaram.
**Destrava:** COL-LAW-212 · 213 · 016.

> **E há um item que não é engenharia: G-14, a grafia do desconhecido** (C-003). É decisão
> do dono, pode ser tomada a qualquer momento, e quanto mais tarde, mais dado terá de ser
> migrado.

---

## A V1.2 ACRESCENTA UM GAP AO TOPO — E ELE ANDA JUNTO COM O G-02

### G-30 · a memória operacional da Itália sai do Git e vai para onde ela já existe

`data/collection-ledger` + `data/collection-store` → `collection_run` + `raw_asset` +
bucket `raw`.

Hoje a Itália grava recibo, 144 observações **e 12 MB de bytes** dentro do Git, enquanto as
três estruturas certas existem, estão provadas por round-trip com conferência de hash, e
estão vazias. **O Git não esquece:** cada corrida que entra fica em cada clone, para sempre.

**Ele não é um gap novo: é o G-02 visto pela infraestrutura.** «Dois formatos de corrida» e
«duas memórias operacionais» são a mesma fratura. Fazer os dois separados seria fazer duas
vezes — por isso **G-02 e G-30 passam a ser a mesma missão**, e a ordem não muda:

```
1 G-01   ·  2 G-22  ·  3 G-05  ·  4 G-24  ·  5 G-25
6 G-02 + G-30 (a mesma missão)  ·  7 G-26  ·  8 G-03  ·  9 G-07→G-04  ·  10 G-27
```

### E dois gaps novos que NÃO entram no topo, de propósito

| gap | o quê | por que não é prioridade agora |
|---|---|---|
| **G-32** | construir o Plano de Referência (COL-LAW-401 a 406) | não bloqueia a coleta italiana de hoje. Vira prioridade no dia em que o portfólio ADAMA entrar — e aí vira **a** prioridade |
| **G-33** | validade histórica da referência (`VALID_FROM`/`VALID_TO`) | é parte do G-32, e a lei existe para que ninguém construa a referência sem ela e feche a porta |

> **Não priorizar o Reference Plane agora é uma decisão, não um esquecimento.** Ele está
> `ABSENT` inteiro e escrito por completo — para que quando for construído, nasça certo.

---

## O QUE MUDOU NA ORDEM, DA V1 PARA A V1.1

| | V1 | V1.1 |
|---|---|---|
| 1º | G-01 | G-01 *(mesmo)* |
| 2º | G-05 | **G-22** — o artefato deixa de fingir que é o fato *(novo)* |
| 3º | G-02 | G-05 |
| 4º | G-03 | **G-24** — fonte ≠ endpoint *(novo)* |
| 5º | G-07 | **G-25** — descobrir ≠ buscar *(novo)* |

**Três gaps novos entraram no topo.** Todos pelo mesmo motivo: são **modelo**, não
funcionalidade. Construir automação sobre um modelo errado é o jeito mais caro de descobrir
que ele estava errado.

---

## OS GAPS MENORES, registrados e não priorizados

`G-39` **falta a tabela `derived_artifact` no Supabase** — é a **única** lacuna de esquema que
o censo de identidade encontrou; SQL projetado e **não aplicado** em
[`../operacao/IDENTIDADE-DO-ARTEFATO.md`](../operacao/IDENTIDADE-DO-ARTEFATO.md) §F ·
`G-40` **11 das 49 cópias de PDF não têm prova de captura em registo nenhum** — 9 em
`IT-ARPAV-VENETO`, 2 em `PIEMONTE-FD`, pacotes antigos sem manifesto; não afeta contagem
nem os 6 grupos, mas é procedência em falta · `G-41` **21 de 21 migrations dizem `NÃO
EXECUTADA` no cabeçalho e pelo menos 001–016 estão aplicadas** — é deriva de comentário, não
ausência de esquema; **migration é história e não se reescreve**, o que falta é um lugar que
diga o que está aplicado agora ·
`G-37` contagens renderizáveis nas OUTRAS estradas · `G-38` `STATE_BEFORE/AFTER` e `ROUTE` na corrida · `G-36` **o chão da coleta está reprovando desde `a32799c`** — `COLLECTED_AT` e `SOURCE_LOCATION` ficam `NAO SEI` nas 43 fichas derivadas; medido em worktree destacado, não foi a integração · `G-34` pré-voo antes de tocar em documento · `G-35` árvore escaneada separada do commit do mapa · `G-31` o raio-X mostra tabela, bucket e store do lado físico · `G-29` **`tem_teste` procura a aresta do teste no sentido errado** em
`generate_system_map.py:1825` — 3 peças ficam 🟡 tendo teste real; medido e registrado em
[`EMENDA-V1-1.md`](EMENDA-V1-1.md), **não consertado nesta missão** ·
`G-19` arestas `OBSERVED` e evidência de RUN no mapa · `G-20` corrida, custo e contagens
renderizáveis por peça · `G-21` `COMPLIANCE`/`GAP` derivados em vez de escritos à mão ·
`G-23` `ORIGINAL_VALUE` e `FIRST_SEEN`/`LAST_SEEN` ao lado do normalizado ·
`G-28` semântica do zero e estado próprio de *schema drift* ·
`G-06` linhagem de derivado (`parent_artifact_id`) · `G-08` cursor para as `FORWARD_ONLY` ·
`G-13` fila de quarentena · `G-15` vocabulário separado por responsabilidade ·
`G-16` escopo de país conferido dentro do executor · `G-17` língua no ledger italiano ·
`G-18` `ACTOR_TYPE` distingue pessoa de máquina · `G-19` arestas `OBSERVED` no mapa.

---

## O QUE ESTA MISSÃO DELIBERADAMENTE NÃO FEZ

- **Não consertou nenhum dos gaps.** Missão fundacional (§65 do briefing).
- **Não tocou em Espanha nem em França.** Nenhum perfil deles foi construído.
- **Não reescreveu** `pedido/`, `coleta/`, `admissao/`, `ferramentas/`, `regras/`,
  `guarda/` nem workflow de coleta.
- **Não apagou nada.** Nenhuma lei antiga foi removida; o censo registra 58 `KEEP`.
- **Não instalou plataforma** — nem Airbyte, nem Dagster, nem Temporal, nem Prefect, nem
  Kafka. Os princípios foram adotados; as plataformas, não.
