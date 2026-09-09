# CENSO CANÔNICO DAS LEIS DA COLETA — apêndice A da Bíblia

**Data:** 2026-09-07 · **HEAD medido:** `56fdb8c` · **Ramo:** `claude/biblia-canonica-da-coleta`

> Este censo foi levantado **antes** de a Bíblia ser escrita, e é a prova de que ela não
> inventou uma segunda constituição. Cada linha aponta para um ficheiro que existe no
> repositório de hoje. Nada aqui foi lembrado; tudo foi lido.

**Nada foi apagado nesta missão.** `SUPERSEDE` e `MERGE` descrevem o destino canônico de
uma lei, não uma remoção de ficheiro.

---

## COMO LER A TABELA

| coluna | o que quer dizer |
|---|---|
| `IMPL` | existe código que a exerce |
| `TEST` | existe teste, portão ou contraexecutável que a prova |
| `USO` | algum caminho produtivo a chama hoje |
| `DESTINO` | `KEEP` fica como está · `MERGE` entra na Bíblia junto com outra · `SUPERSEDE` a Bíblia passa a ser o texto canônico e o ficheiro vira implementação · `LEGACY` ficou para trás · `CONFLICT` diverge de outra lei · `UNKNOWN` não deu para medir |

---

## 1 · AS CONSTITUIÇÕES QUE JÁ EXISTIAM

| ID | NOME | FICHEIRO | ESCOPO | IMPL | TEST | USO | DESTINO |
|---|---|---|---|---|---|---|---|
| CEN-001 | Lei do SINTONIA System Map | `AGENTS.md` | TRANSVERSAL | sim | `system-map/scripts/validate_system_map.py` | CI | **KEEP** — dono da lei do mapa; a Bíblia aponta, não repete |
| CEN-002 | Instruções permanentes do projeto | `CLAUDE.md` | TRANSVERSAL | — | — | sim | **KEEP** — dono do design; aponta para AGENTS.md |
| CEN-003 | Método `SOURCE → EVIDENCE → … → PORTAL` e os 4 estados de evidência | `README.md` | TRANSVERSAL | — | — | sim | **KEEP** — a Bíblia herda `COMPROVADO/INFERÊNCIA/HIPÓTESE/NÃO SEI` |
| CEN-004 | Porta de entrada da coleta (gerada do mapa) | `regras/LEIA-ANTES-DE-COLETAR.md` | COLETA | gerado | anti-drift | sim | **KEEP** — passa a apontar também para a Bíblia |
| CEN-005 | Regra de coleta externa EAME (23 secções) | `medidas/REGRA-DE-COLETA-EXTERNA-EAME.md` | COLETA | parcial | `medidas/portao.py` | sim | **SUPERSEDE parcial** — as leis universais sobem para a Bíblia; o detalhe operacional de vídeo/voz fica |
| CEN-006 | Diário de decisões | `docs/decisoes/DIARIO-DE-DECISOES.md` | TRANSVERSAL | — | — | sim | **KEEP** — é onde a mudança de lei se registra |

## 2 · TEMPO

| ID | NOME | FICHEIRO | IMPL | TEST | USO | DESTINO |
|---|---|---|---|---|---|---|
| CEN-010 | Contrato temporal V2.1 — prosa nunca vira data; `UNKNOWN` não entra em «próximos» | `leis/v21_datas.py` | sim | sim | motor V2.1 | **KEEP** → COL-LAW-031 |
| CEN-011 | DATA CLOCK — versão da fonte com `VERSION_DATE`, `COLLECTION_DATE`, `SHA256` | `leis/data_clock.py` | sim | manifesto | sim | **KEEP** → COL-LAW-031/029 |
| CEN-012 | `PUBLISHED_AT ≠ FACT_TIME` | `medidas/lugar_do_fato.py` · `AGENTS.md` | sim | `tests/test_lugar_do_fato.py` | sim | **MERGE** → COL-LAW-031 |
| CEN-013 | `OUTPUT_WRITTEN_AT` nunca vira `STARTED_AT`; ordem só com instante com fuso | `regras/proveniencia.py` · `medidas/PORTOES-DE-COLETA-10B.md` §H | sim | `tests/test_portao.py` | sim | **KEEP** → COL-LAW-031 |

## 3 · GEOGRAFIA

| ID | NOME | FICHEIRO | IMPL | TEST | USO | DESTINO |
|---|---|---|---|---|---|---|
| CEN-020 | A lei do lugar do fato, independente de idioma — 4 espécies, escada de precisão | `medidas/lugar_do_fato.py` | sim | sim | sim | **KEEP** → COL-LAW-032 |
| CEN-021 | O leitor italiano do lugar do fato (gazetteer IT) | `medidas/fato_local.py` | sim | sim | piloto IT | **KEEP** — implementação de país, não lei |
| CEN-022 | Contrato de geografia V2.1 — `PROVINCIAL ≠ REGIONAL`, cruzamento não alega mais que o apoio | `leis/v21_geografia_contrato.py` | sim | falha fechada (exit 1) | motor V2.1 | **KEEP** → COL-LAW-032 |
| CEN-023 | Como se soube o lugar: `ESCRITO/CITADO/DA_FONTE/DEDUZIDO`, com `DA_FONTE` e `DEDUZIDO` proibidos de sustentar fato | `supabase/` migration 015 · `docs/regras/BRAZIL-LESSONS-TRANSFER-EAME.md` | sim | constraints do banco | sim | **KEEP** → COL-LAW-032 |

## 4 · PROCEDÊNCIA E IDENTIDADE

| ID | NOME | FICHEIRO | IMPL | TEST | USO | DESTINO |
|---|---|---|---|---|---|---|
| CEN-030 | `CONTENT → RUN_ID → RUN_MANIFEST → INPUT/ACTOR/DATASET/RAW`; `NOT_PRESERVED ≠ NÃO SEI`; nunca gravar token | `regras/proveniencia.py` | sim | `tests/test_portao.py` | 5 réguas leem | **KEEP** → COL-LAW-033 |
| CEN-031 | Contrato de procedência V2.1 — o carimbo não promete o que o registro não tem | `leis/v21_procedencia_contrato.py` | sim | falha fechada | motor V2.1 | **KEEP** → COL-LAW-033 |
| CEN-032 | Carimbar origem / religar procedência | `leis/v21_carimbar_origem.py` · `leis/v21_procedencia_religar.py` | sim | sim | motor V2.1 | **KEEP** |
| CEN-033 | As sete entidades de identidade regulatória — nunca colapsar | `docs/regras/MODELO-DE-IDENTIDADE-EAME.md` | parcial | — | sim | **KEEP** → COL-LAW-034 |
| CEN-034 | `NAME ≠ HANDLE ≠ PROFILE ≠ PERSON ≠ ORGANIZATION`; identidade nunca por similaridade textual | `medidas/REGRA-DE-COLETA-EXTERNA-EAME.md` §9 · `regras/comunicacao_identidade.py` | sim | sim | sim | **MERGE** → COL-LAW-034 |
| CEN-035 | Dedupe estrutural: `PLATFORM + EXTERNAL_ID`; ausência de identidade **não** é identidade partilhada | `medidas/voz.py` · `medidas/PORTOES-DE-COLETA-10B.md` §D | sim | `tests/test_portao.py` (P2 refutado e corrigido) | sim | **KEEP** → COL-LAW-021/034 |
| CEN-036 | Identidade de checkpoint não pode conter `TOKEN`/`RUN_ID`/`DATASET_ID`/`CAPTURED_AT` | `coleta/coleta_checkpoint.py` | sim | `tests/test_coleta_resiliente.py` | coleta paga | **KEEP** → COL-LAW-016/034 |

## 5 · RAW, DERIVADO E PRESERVAÇÃO

| ID | NOME | FICHEIRO | IMPL | TEST | USO | DESTINO |
|---|---|---|---|---|---|---|
| CEN-040 | RAW antes de normalizar, sempre; `RAW → NORMALIZED → ANALYTICAL` | `coleta/coletor.py` | sim | 4 execuções contra API real | rota paga | **KEEP** → COL-LAW-006/007 |
| CEN-041 | `PAID_RAW_POLICY` — rota não replicável entra em `data/samples/` (versionado); `data/raw/` é cache (D-003) | `medidas/REGRA-DE-COLETA-EXTERNA-EAME.md` §14 · `docs/decisoes/DIARIO-DE-DECISOES.md` D-003 | sim | `medidas/portao.py` | sim | **KEEP** → COL-LAW-044 |
| CEN-042 | Dataset vazio **é** evidência: `PRESERVED`, não `NOT_PRESERVED` | `medidas/PORTOES-DE-COLETA-10B.md` §C | sim | sim | sim | **KEEP** → COL-LAW-024/037 |
| CEN-043 | `BROWSER_RENDERED_EXTRACT ≠ RAW_PRESERVED` | `docs/fontes/ITALY-SOURCE-CONTRACT-MATRIX-V1.md` | sim | `regras/italy_source_health.mjs --negativos` | IT | **KEEP** → COL-LAW-007 |
| CEN-044 | Ordem obrigatória da execução italiana: RAW no passo 8, imutável no 11, parser depois | `docs/operacao/ITALY-FORWARD-ONLY-SCHEDULING-V1.md` §8 | sim | operação real | IT | **KEEP** → COL-LAW-006 |
| CEN-045 | `TRANSCRIPT_ORIGINAL` e `TRANSLATION` são campos separados; tradução nunca substitui evidência | `medidas/REGRA-DE-COLETA-EXTERNA-EAME.md` §4 | sim | `medidas/voz.py` | ES | **KEEP** → COL-LAW-007 |

## 6 · PEDIDO, ORQUESTRAÇÃO E EXECUTOR

| ID | NOME | FICHEIRO | IMPL | TEST | USO | DESTINO |
|---|---|---|---|---|---|---|
| CEN-050 | O pedido de coleta — alvo, acionamento, escopo, filtros; nenhum chamador conhece `coletor_x.py` | `pedido/pedido.py` | sim | `provas/testa_coleta_canonica.py` | sim | **KEEP** → COL-LAW-010 |
| CEN-051 | Acionamento e escopo são dois eixos, não um; `AUTOMATICO_EVENTO` recusado porque não existe | `pedido/pedido.py` | sim | sim | sim | **KEEP** → COL-LAW-010/016 |
| CEN-052 | O orquestrador escolhe e assina o recibo; não coleta | `orquestrador/orquestrador.py` | sim | `provas/testa_coleta_canonica.py` | sim | **KEEP** → COL-LAW-011/012 |
| CEN-053 | A receita é **derivada** do atlas, não escrita; o `NÃO SEI` é o produto mais importante | `pedido/receitas.py` | sim | sim | sim | **KEEP** → COL-LAW-015 |
| CEN-054 | Contratos obrigatórios de toda corrida (procedência · tempo · lugar · recibo) | `pedido/receitas.py` `CONTRATOS_OBRIGATORIOS` | sim | sim | sim | **KEEP** → COL-LAW-013 |
| CEN-055 | Ferramenta ≠ veículo ≠ ação — três coisas, três gavetas | `AGENTS.md` | sim | `system-map/tests/test_system_map.py` | CI | **KEEP** → COL-LAW-009 |

## 7 · ADMISSÃO E DECISÃO

| ID | NOME | FICHEIRO | IMPL | TEST | USO | DESTINO |
|---|---|---|---|---|---|---|
| CEN-060 | A porta de admissão — decisão por par (item, universo), nunca por item | `admissao/admissao.py` | sim | `provas/testa_coleta_canonica.py` | sim | **KEEP** → COL-LAW-042 |
| CEN-061 | Os cinco resultados `SIM/NAO/NAO_SEI/NAO_SE_APLICA/ERRO` | `admissao/admissao.py` | sim | sim | sim | **KEEP** → COL-LAW-038 |
| CEN-062 | O livro de decisões — item, universo, regra, versão, resultado, motivo, prova, corrida | `data/samples/LIVRO-DE-DECISOES.json` | sim | sim | sim | **KEEP** → COL-LAW-042 |
| CEN-063 | Contrato de saída `PRONTO_PARA_INTELIGENCIA` | `admissao/admissao.py::pronto_para_inteligencia` | sim | sim | sim | **KEEP** → COL-LAW-043 |
| CEN-064 | Relevância ao caso é derivada com motivo escrito, **nunca** score | `supabase/` migration 015 `f_relevancia_ao_caso` | sim | teste que reprova coluna `score` | sim | **KEEP** → COL-LAW-036 |

## 8 · CUSTO, ROTA E FALLBACK

| ID | NOME | FICHEIRO | IMPL | TEST | USO | DESTINO |
|---|---|---|---|---|---|---|
| CEN-070 | Política de chaves descartáveis Apify — orçamento por chave, `ACTIVE/EXHAUSTED/ABANDONED` | `docs/regras/POLITICA-DE-CHAVES-DESCARTAVEIS.md` | parcial | — | sim | **KEEP** → COL-LAW-019 |
| CEN-071 | Contrato do ator lido de graça **antes** de gastar; `CONTRACT_MATCH ≠ USEFUL_DATA` | `ferramentas/apify_contrato.py` · `ferramentas/contrato_ator.py` | sim | sim | rota paga | **KEEP** → COL-LAW-018/019 |
| CEN-072 | `SEM_CHECKPOINT_NAO_GASTEI` e `JA_CONCLUIDO_NAO_PAGAR_DUAS_VEZES` | `coleta/coleta_checkpoint.py` | sim | `tests/test_coleta_resiliente.py` | coleta paga | **KEEP** → COL-LAW-017/021 |
| CEN-073 | `teto_usd → maxTotalChargeUsd`; trava do lado da plataforma | `coleta/coletor.py` | sim | sim | rota paga | **KEEP** → COL-LAW-019 |
| CEN-074 | Fluxo obrigatório `DISCOVERY → TESTE PEQUENO → MEDIÇÃO → ESCOLHA → ESCALA` | `medidas/REGRA-DE-COLETA-EXTERNA-EAME.md` §21 | parcial | — | sim | **MERGE** → COL-LAW-018 |
| CEN-075 | `apify_pool.py` é o dono único da rotação de chave | `ferramentas/apify_pool.py` | sim | sim | sim | **KEEP** → COL-LAW-011 |

## 9 · SAÚDE, DRIFT E RECONCILIAÇÃO

| ID | NOME | FICHEIRO | IMPL | TEST | USO | DESTINO |
|---|---|---|---|---|---|---|
| CEN-080 | Saúde de fonte `HEALTHY/DEGRADED/FAILED/UNKNOWN`; `HTTP 200` não basta; lista vazia é `FAILED` | `medidas/source_health.py` | sim | sim | sim | **KEEP** → COL-LAW-028 |
| CEN-081 | Estado de versão — `BASELINE_ESTABLISHED` nunca é `NO_CHANGE`; `SOURCE_FAILED ≠ NO_NEW_VERSION` | `medidas/source_health.py` | sim | sim | sim | **KEEP** → COL-LAW-024/029 |
| CEN-082 | O chão que não desce — 10 regras medidas a cada corrida | `medidas/padrao_da_coleta.py` · `medidas/PADRAO-DA-COLETA-CHAO.json` | sim | CI | sim | **KEEP** → COL-LAW-023 |
| CEN-083 | Saúde do corredor ≠ saúde da fonte; `VPN_FAILURE ≠ SOURCE_FAILURE` | `docs/operacao/ITALY-FORWARD-ONLY-SCHEDULING-V1.md` §9 | sim | operação | IT | **KEEP** → COL-LAW-037/028 |
| CEN-084 | Os 13 contratos executáveis das fontes italianas + controles negativos | `regras/italy_contracts.mjs` · `regras/italy_source_health.mjs` | sim | `--negativos` | IT | **KEEP** → COL-LAW-029 |
| CEN-085 | `DECLARED_FREQUENCY ≠ OBSERVED_FREQUENCY`; declaração não é medição | `docs/fontes/ITALY-SOURCE-CONTRACT-MATRIX-V1.md` | sim | sim | IT | **KEEP** → COL-LAW-024 |
| CEN-086 | Portões derivados, nunca digitados; nome que faz dois trabalhos produz `READY` falso | `medidas/portao.py` · `medidas/portoes_eame.py` | sim | `tests/test_portao.py` | sim | **KEEP** → COL-LAW-023 |
| CEN-087 | 25 cicatrizes do Brasil com testemunha executável; sem testemunha cai para `NOT_MEASURED` | `medidas/cicatrizes_brasil.py` · `docs/regras/BRAZIL-LESSONS-TRANSFER-EAME.md` | sim | mutação | sim | **KEEP** |

## 10 · UNKNOWN, ERRO E AUSÊNCIA

| ID | NOME | FICHEIRO | IMPL | TEST | USO | DESTINO |
|---|---|---|---|---|---|---|
| CEN-090 | «NÃO SEI continua NÃO SEI»; ausência de prova não é prova de ausência | `AGENTS.md` · `regras/LEIA-ANTES-DE-COLETAR.md` | sim | `P7_NAO_SEI_VIVE` | CI | **KEEP** → COL-LAW-035 |
| CEN-091 | `FAIL CLOSED` — a tabela dos «não é» (403, 200, `SUCCEEDED`, transcript, dataset vazio) | `medidas/REGRA-DE-COLETA-EXTERNA-EAME.md` §15 | sim | `medidas/portao.py` | sim | **KEEP** → COL-LAW-037 |
| CEN-092 | `tentativa_de_coleta` separa o mundo, a instalação e nós | `supabase/` migration · `BRAZIL-LESSONS-TRANSFER-EAME.md` | sim | vocabulário recusado pelo banco | sim | **KEEP** → COL-LAW-037 |
| CEN-093 | `ACCESS_CLASSIFICATION ≠ ANALYTIC_VERDICT`; `ROUTE_NOT_FOUND ≠ SOURCE_BLOCKED` | `regras/LEIA-ANTES-DE-COLETAR.md` | sim | contratos IT | sim | **KEEP** → COL-LAW-037 |
| CEN-094 | `KEYWORD_MATCH ≠ RELEVANT_EVIDENCE` → `CONTEXT_ONLY` | migration 015 `f_relevancia_ao_caso` | sim | sim | sim | **KEEP** → COL-LAW-036 |

## 11 · PAÍS, LÍNGUA E VOCABULÁRIO

| ID | NOME | FICHEIRO | IMPL | TEST | USO | DESTINO |
|---|---|---|---|---|---|---|
| CEN-100 | `COUNTRY_ISOLATION_COMPLETE` — país é dimensão, não pasta esquecida | `README.md` · `supabase/` · `BRAZIL-LESSONS-TRANSFER-EAME.md` | sim | teste de isolamento | sim | **KEEP** → COL-LAW-039 |
| CEN-101 | País dentro da gaveta: `<gaveta>/<país>/`; peça transversal fica na raiz | `AGENTS.md` | sim | `P2_PASTA_BATE_COM_MAPA` | CI | **KEEP** → COL-LAW-039 |
| CEN-102 | As palavras que a busca digita, por país-cultura-problema | `regras/rotulos_censo.py` · `regras/sensor_coleta.py` · `regras/sensor_medir.py` | sim | sim | sim | **KEEP** → COL-LAW-041 |
| CEN-103 | `LANGUAGE` é campo próprio e fica `NÃO SEI` quando não provado | `medidas/voz.py` `CAMPOS_VIDEO` | sim | `voz.cobertura()` | ES | **KEEP** → COL-LAW-040 |

## 12 · MAPA E GOVERNANÇA

| ID | NOME | FICHEIRO | IMPL | TEST | USO | DESTINO |
|---|---|---|---|---|---|---|
| CEN-110 | O mapa é derivado do repo; o repo não é derivado do mapa | `AGENTS.md` | sim | `P1_SEM_DRIFT` | CI | **KEEP** → COL-LAW-046/047 |
| CEN-111 | `state.generated.json` é saída; não se edita à mão | `AGENTS.md` · `system-map/scripts/generate_system_map.py` | sim | `P1_SEM_DRIFT` | CI | **KEEP** → COL-LAW-047 |
| CEN-112 | Taxonomia de ligações e «declaração não promove a verde» | `system-map/data/architecture.declared.json` `NOTA` | sim | `P5_ARESTA_PROVADA` · `P7` | CI | **KEEP** → COL-LAW-048/049 |
| CEN-113 | Três estados: `official` · `futuro` · `legacy` — futuro não é legado | `AGENTS.md` | sim | — | sim | **KEEP** → COL-LAW-050 |
| CEN-114 | Recarimbar sem reler é o único jeito de mentir neste sistema | `AGENTS.md` | sim | `P6_VERDE_NAO_E_VELHO` | CI | **KEEP** → COL-LAW-069 |

## 13 · O QUE O CENSO DE COLETA JÁ TINHA MEDIDO

`docs/operacao/CENSO-DA-COLETA.md` (07/09/2026) mediu, e a Bíblia adota os números:

| medido | número |
|---|---|
| ficheiros de código na coleta | 92 |
| pontos de entrada | 79 |
| executores que saem para fora | 18 |
| peças que coordenam mais de um executor | 0 |
| ficheiros que decidem relevância | 1 |
| quem escreve o recibo por código | 0 (antes do orquestrador) |
| fontes italianas com `access_method: NÃO SEI` | 35 de 54 |

---

## CONTAGEM

| | |
|---|---|
| leis/contratos maduros catalogados | **63** |
| `KEEP` | **58** |
| `MERGE` | **3** |
| `SUPERSEDE` (parcial) | **1** |
| `LEGACY` | **0** |
| `CONFLICT` | **1** (CEN-005 §14 vs D-003 — resolvido; ver a matriz de conflitos) |

**Nenhum ficheiro foi apagado, movido ou reescrito nesta missão.**
