# IAB_ARCHITECTURE_STUDY — STUDY: ITALIAN AGRO BRAIN ARCHITECTURE V1

DATA           2026-09-27 (10:00–10:50 BRT)
AUTOR          SINTONIA LAB
PROJECT_HEAD   produção servico-20260923-0923 @ 554c1ec1 · linha IAB iab-v1 @ 0d074486 (= produção + 1 commit, só a carta)
MODO           só leitura. Nenhum schema, migration, código ou commit no projeto. Sala lida com transaction_read_only = on
               (DSN não impresso). Único ficheiro alterado fora de lab/: nenhum. Dentro do perfil do LAB: scripts/triangular.sh
               (conserto do verificador de motor — ver §4).
PASTA          lab/estudos/2026-09-27-IAB/ → PACOTE.md · triangulacao/resposta-{opus,gpt,deepseek}.md · TRIANGULACAO.txt ·
               TRIANGULACAO-REVERIFICADA.txt · BENCHMARK.md · CONFRONTO.md · medir_*.sh/.out · este ficheiro
LEGENDA        [M] medido nesta sessão · [H] escrito por outro documento, não re-medido · ESTIMATIVA = cálculo, não medição

------------------------------------------------------------------------------------------------------------------
## 1. ESTADO ATUAL RELEVANTE DO SINTONIA (FASE 0)

Sala `sala_italia` (PostgreSQL 16.4, 28,9 MB) [M]:
- migrações aplicadas 001…033 (sem 008); 034 e 036 existem no repo e NÃO estão aplicadas.
- 73 tabelas, 23 vistas. Com dados: raw_asset 2 205 (bruto ≈ 1,05 GB em disco, **todo capturado em 2026-09**),
  derived_artifact 1 116 (1 110 TEXT_EXTRACTION), documento_estruturado 1 112, collection_run 481, sala_de_espera 204,
  sala_de_espera_revisao 478, storage_object ~1 897, conteudo 3.
- **Vazias**: crop, issue, crop_issue, conteudo_crop_issue, geografia, observacao, derivacao, derivacao_observacao,
  boletim_fitossanitario, clima_observacao, substancia_ativa, registro_uso, pessoa, … (~60 no total).
- Identidade canônica que existe e funciona: raw_asset.id (= RAW_OBSERVATION_ID) + sha256 + document_key
  (2 023 preenchidos / 1 617 distintos; 182 FORWARD_IDENTITY_UNPROVEN) → derived_artifact (parent_sha256, producer,
  producer_version, parameters_hash) → documento_estruturado (**hash_texto = sha256 do derivado em 1 112/1 112**) →
  sala_de_espera (run_id, ordem), raw_observation_id 204/204.
- Onde vive FACT/CLAIM hoje: **em lugar nenhum como objeto.** `sala_de_espera.fato` = "NAO_SE_APLICA" em 204/204;
  `estagio` = DOCUMENTO em 204/204; `janela_declarada` tem as chaves CULTURA/FASE/REGIAO/… quase todas NAO SEI.
  A lei existe: COL-LAW-201 (artefato ≠ fato), COL-LAW-202 (ARTIFACT → CLAIM, «TARGET, nunca CURRENT», **IT ABSENT**),
  COL-LAW-203 (procedência até o valor), COL-LAW-502 (DOCUMENT READY ≠ FACT READY).
- Equivalente a entidade canônica: tabelas crop/issue/crop_issue (com eppo_code) e geografia (com espécie
  ADMIN/DEFINIDA_PELA_FONTE/ZONA_AGRONOMICA/OUTRA e escada de precisão, migr. 018) — **todas vazias na Itália**.
  Código: leis/fato_local.py (719 linhas; regiões/províncias; comune só pelo CSV oficial do ISTAT —
  **leis/dados/Elenco-comuni-italiani.csv NÃO existe na árvore** [M]), leis/lugar_do_fato.py, motor/normalize_agro.py
  (propõe EPPO e verifica na EPPO GD), coleta/eppo_gd.py.
- Intelligence: 204 → 24 no motor → 10 sinais → 3/0 crossings → 0 findings [H: AUDITORIA-INTELLIGENCE].
  Matéria-prima [M no Git]: EXTRATORES-V2-JUNTOS/ANTES-DEPOIS.txt, base 1 252 itens: CULTURA 77, PRAGA 8, FASE 14,
  **AS_4_CHAVES_JUNTAS 1**, pares cruzáveis entre fontes diferentes **0**.
- Contrato de entrada da Intelligence [M]: INTELLIGENCE-INPUT-CONTRACT-V1.md separa ENTRADA A (material admitido,
  dono Collection) de ENTRADA B (referência factual ADAMA, dono referencia/).
- Mapa de donos [M]: INTELLIGENCE-CONCEPT-OWNERSHIP-V3.json — 32 conceitos: 24 INTELLIGENCE, 7 COLLECTION, 1 SEM DONO.

## 2. PROBLEMAS (o que o Brain tem de resolver — e o que ele NÃO resolve)
P-A  Conhecimento some depois de cada corrida: nenhuma afirmação estruturada persiste com prova (fato = NAO_SE_APLICA 204/204).
P-B  Não há como consolidar «50 fontes dizem X» sem perder escopo (§9 × COL-LAW-202).
P-C  Não há vocabulário canônico povoado (crop/issue/geografia vazias; italiano→EPPO inexistente).
P-D  Não há «o que sabíamos quando» para conhecimento (só para campos da Sala, via revisões).
P-E  A Intelligence relê texto bruto a cada corrida e perde 180/204 por falta de chave.
NÃO RESOLVE  (e isto é o principal achado): falta de HISTÓRIA (todo o acervo é de set/2026) e falta de EXTRAÇÃO
             confiável (1/1 252 com as 4 chaves). O Brain organiza o que a Collection trouxer; não cria passado.

## 3. BENCHMARK (detalhe em BENCHMARK.md)
| referência | o que resolve | precisamos agora? | mínimo equivalente |
|---|---|---|---|
| OpenSanctions statements [lido] / Wikidata statements [lido] / FollowTheMoney [lido] | muitas fontes afirmando coisas sobre entidades; valor original + fonte + tempo por afirmação; merge reversível; afirmações divergentes coexistem com qualifiers/rank | **SIM, o padrão** | assertion escopada + evidência + alias com estado |
| Palantir Ontology [lido] | tipos de objeto + links + ações governadas sobre datasets | padrão sim, produto não | poucas tabelas tipadas + um escritor por conceito |
| OpenLineage [lido] · Unity Catalog · DataHub | lineage entre muitos jobs/sistemas | NÃO | FKs existentes (raw → derived → assertion) + producer_version |
| GraphRAG [lido] · LlamaIndex PG index | grafo e resumos gerados por LLM | NÃO (viola §19/§34, INT-LAW-160) | extração restrita + validação em código |
| Neo4j | travessia profunda em grafo grande | NÃO | tabelas de aresta + WITH RECURSIVE |
| pgvector [lido] | similaridade; busca exata por padrão | NÃO até teste | full text italiano + expansão por alias |
| Zep/Graphiti [abstract lido] · Snodgrass · event sourcing | tempo do fato × tempo do registro | o conceito sim | literal+precisão+intervalo; recorded_at append-only |
| EPPO · ISTAT · NUTS · AGROVOC | identidade oficial de praga/cultura e território | **SIM (EPPO, ISTAT)** | alias → código, com verificação; CSV ISTAT no lugar |
| W3C Web Annotation (TextQuote/TextPosition) [citado por Opus; não lido por mim] | âncora de trecho robusta | padrão sim | offsets + hash + citação curta |

## 4. TRÊS ANÁLISES INDEPENDENTES (cegas)
TRIANGULAÇÃO: **COMPLETA · MOTORES_RESPONDERAM = 3/3** — após reverificação. O script registrou 2/3 por um defeito DELE
(pegou «a última sessão» do state.db enquanto o coordenador rodava um teste paralelo `00-prova-gpt6` no mesmo perfil).
Prova independente em TRIANGULACAO-REVERIFICADA.txt: cada resposta = conteúdo da sessão certa, com modelo medido
(opus 20260927_100749_f56adb claude-opus-5-5/anthropic · gpt 20260927_101324_d955e7 gpt-5.6-sol/openai-codex ·
deepseek 20260927_102035_33c420 deepseek/deepseek-v4.1-flash/openrouter). Script consertado e re-testado nos dados reais (3/3 OK).

Resumo de cada um (texto integral em triangulacao/):
- **Opus 5.5** — Brain = COL-LAW-202 + vocabulário + objetos da Intelligence + vistas; separar status epistêmico de espécie;
  tabelas antigas apontam para identidade velha (`conteudo`); evidência = derived_artifact + offsets + hash; menor teste =
  10 boletins em JSON, parar se precisão < 80 %; canário míldio.
- **GPT-5.6 Sol** — mesmo núcleo; reusar tabelas tipadas; bitemporal simples; LLM candidato + validação determinística +
  humano no gold set; teste de refutação com 12 documentos estruturados à mão ANTES de qualquer LLM; canário míldio.
- **DeepSeek 4.1 Flash** — leu mais o repo: achou a ENTRADA A × B (referência), a escada geográfica (018), o CSV ISTAT
  ausente, o ANTES-DEPOIS (1/1 252), o mapa de donos; propôs CLAIM + ASSERTION; afirmou que canário histórico mede o acervo,
  não o Brain; teste cego «modo antigo × Brain». Errou ao pôr CONTRADICTS no Brain e ao estimar bytes sem índice real.
  Não conseguiu abrir a Sala (disse que não havia psql — há, em ~/orca/pgtmp/pgsql/bin; os números do pacote eram [M] meus).

## 5. DIVERGÊNCIAS (decididas por evidência — tabela completa em CONFRONTO.md §2)
D1 unidade: **ASSERTION escopada é o que se grava**; a proposição (s,p,o) é chave normalizada + vista (§9 sem perder escopo).
D2 entidades: reusar crop/issue pelo código/EPPO; nomes por língua em ALIAS (o `nome_es` fica como legado).
D3 conteudo_crop_issue: não reusar como evidência (aponta para `conteudo`, 3 linhas, identidade antiga) — só o vocabulário `relacao`.
D4 tipo epistêmico: 2 eixos (quem sustenta × o que é) + polaridade/modalidade.
D5 **camada C (referência oficial) — DeepSeek vence por evidência (INPUT-CONTRACT A×B)**.
D6 contradição = objeto da Intelligence (INT-LAW-030/033), ligando assertions.
D7 evidência = FK derived_artifact + offsets + hash do trecho + citação ≤200; nada copiado.
D8 bytes = 0,6–1,5 KB (âncora medida 977 B/linha na tabela de revisões).
D9 «o que sabíamos quando»: recorded_at × captured_at — decisão do dono.
Canário: os 3 escolheram míldio com base num número [H] do pacote; **a medição refutou** (ver §16).

## 6. RED TEAM (completo em CONFRONTO.md §4–§5)
A hipótese híbrida do dono é **certa como classificação e perigosa como camada**; «observed» é quase sempre «afirmado
pela fonte»; falta a classe C; §9 conflita com COL-LAW-202; o Brain nasce vazio se exigir as 4 chaves; risco de
cemitério de schemas (~60 tabelas vazias); o portão que deixou passar 11/12 ataques tem de ser consertado antes;
o recurso escasso é tempo humano (gold set, aliases).

## 7. ARQUITETURA RECOMENDADA
Não é um produto nem uma terceira camada. É **uma memória com três classes e dois donos, dentro do mesmo PostgreSQL**:

```
            ┌────────────── COLLECTION (dono) ──────────────┐     ┌──── INTELLIGENCE (dono) ────┐
RAW ─► DERIVED(texto, sha256) ─► ASSERTION (A: «a fonte X afirma») ─►  SUPPORT / CONTRADICTS /
                  ▲                 │  + EVIDENCE_SPAN (offsets+hash)   SIGNAL / FINDING / DERIVATION (B)
                  │                 │  + chave de proposição (s,p,o)      │  inputs = assertion_ids
                  │                 ▼                                    ▼
            REFERÊNCIA (C: registro oficial, rótulo ADAMA, aprovação UE — valid_from/valid_to; dono referencia/)
                  │
            VOCABULÁRIO: crop · issue · crop_issue · geografia · substancia_ativa · pessoa  +  ALIAS (termo original → código EPPO/ISTAT, estado)
                  │
            VISTAS DERIVADAS reconstruíveis: timeline por entidade, perfil regional, «proposição com N evidências»
```
Regras: escrita append-only (sem UPDATE/DELETE; correção = nova linha com causa); um escritor por classe;
LLM só propõe e nunca escreve; todo campo sem prova = NÃO SEI com razão; embeddings (se um dia) = índice reconstruível.

## 8. POSIÇÃO DO BRAIN NO FLUXO
`… → ADMISSÃO → READY (Sala) → [FACT READY: extração de ASSERTIONS, dono Collection, COL-LAW-502] → INTELLIGENCE consome
assertions + referência C → devolve derivados B → POTE → CASCO`.
O Brain NÃO é passo novo entre Sala e Intelligence: é a materialização da 2.ª porta que a Bíblia da Coleta já nomeou
(DOCUMENT READY → FACT READY) + a persistência dos objetos da Intelligence. O Casco continua lendo só o que passou pela
Intelligence (D97).

## 9. ALTERAÇÕES NECESSÁRIAS NA COLLECTION (o que preservar AGORA)
1. **Seções** do documento (título/subtítulo do boletim) no texto derivado — a cultura vem da seção (defeito ARIF medido).
2. Derivado «conteúdo principal» sem menu/rodapé, como FILHO do RAW (padrão 034), sem tocar o RAW.
3. Números de monitoramento como aparecem (1, 4, 11, 29), sem resumir.
4. Espécie por BLOCO (a mesma fonte tem OBSERVED_FIELD_SIGNAL e TECHNICAL_GUIDELINE).
5. Aplicar 034/036 (dívida já ensaiada) e o reprocesso de extração pronto (cultura 0→19/94 na cópia) [H].
6. Colocar o CSV oficial ISTAT em leis/dados/ (liga o degrau COMUNE já escrito e desligado).
7. Não descartar item sem FACT_TIME (D62/D100).
NÃO transformar Collection em Intelligence: a extração de assertion é leitura do que a fonte diz, nunca julgamento.

## 10. ALTERAÇÕES NECESSÁRIAS NA SALA
- Nenhuma etapa nova de admissão. A elegibilidade à extração é um valor de `estagio` / fila (COL-LAW-502, índice parcial
  `sala_de_espera_fato_a_espera` já existe na 032) — não uma porta que bloqueia.
- Registrar «extraído pela régua vN: n assertions ou 0» (revisão/derivado), para distinguir zero de não-processado.
- A Sala continua sem julgar relevância (031: «a Sala não julga»).

## 11. ALTERAÇÕES NECESSÁRIAS NA INTELLIGENCE
- Consumir assertion_ids + evidência + vocabulário; o pré-filtro passa de «documento com FACT_TIME» para «assertion com
  FACT_TIME» — e só para capacidades temporais (INT-LAW-091/104; D100).
- Gravar derivados com inputs = assertion_ids, rule_version, run_id (reusar `derivacao`, estendendo a entrada para assertion;
  reconciliar com FINDING/VALIDATION_STATE do OBJECT-MODEL antes — NÃO SEI se já reconciliado).
- CONTRADICTS e SUPPORT entre assertions, sem escolher vencedor.
- Nunca editar assertion; pode recusá-la.

## 12. MODELO DE CONHECIMENTO (conceitual — NÃO é schema; nomes a decidir na engenharia)
```
ASSERTION        id · proposicao_key (hash de s,p,o normalizados) · sujeito(entidade|NAO SEI) · predicado (vocabulário fechado)
                 · objeto(entidade|valor+unidade+denominador) · polaridade · modalidade
                 · STATUS_EPISTEMICO (AFIRMADO_PELA_FONTE | MEDIDO_PELA_FONTE | NAO SEI)
                 · ESPECIE (OCORRENCIA | VALOR_DE_MONITORAMENTO | RECOMENDACAO | PREVISAO | REGRA_DE_MODELO | EVENTO | RELACAO …)
                 · fact_time_literal · fact_time_basis · fact_time_precision · fact_time_range
                 · lugares (0..N, papel FACT/SOURCE, precisão, texto original) · extrator + versão · recorded_at
                 · schema_version · knowledge_model_version
EVIDENCE_SPAN    assertion_id → derived_artifact_id · char_start · char_end · span_sha256 · citação ≤200 · seção
ALIAS            termo original · língua · entidade/código (EPPO|ISTAT|CAS|ORCID) · estado (PROPOSTO|VERIFICADO|AMBIGUO|REJEITADO) · fonte da verificação
REFERÊNCIA (C)   reusar tabelas de registro/rótulo/aprovação UE com valid_from/valid_to
DERIVADO (B)     reusar/estender `derivacao` + tabela de inputs (assertion_ids) + limitacao NOT NULL
```
Prematuros (não criar no V1): EVENT como tabela, RULE como tabela, SUMMARY materializado, entidade genérica, vetor, grafo.

## 13. TECNOLOGIA MÍNIMA
PostgreSQL 16 que já existe: tabelas + FKs + daterange + full text `italian` (stemmer de fábrica) + GIN + WITH RECURSIVE.
Gatilho anti-UPDATE (padrão já usado). Nada de Neo4j, GraphRAG, LlamaIndex, OpenLineage, DataHub. pgvector só se o
teste de recall (§17) passar.

## 14. CUSTO ESTIMADO (ESTIMATIVA)
- Bytes: **0,6–1,5 KB por assertion + 1 evidência, com índices**. Âncora medida: tabela de revisões da Sala =
  466 944 B / 478 linhas ≈ 977 B/linha (append-only, valor médio 128 B, máx 780 B). 1 112 documentos × ~10 assertions ≈
  7–17 MB; comparável ao banco atual (28,9 MB) e 0,1 % do bruto (1,05 GB). **Tamanho não é o risco.**
- Tokens: texto médio 7 924 caracteres ≈ 2 000–2 600 tokens; com instruções e saída ≈ 3–5 mil tokens/documento por passada;
  1 112 documentos ≈ 3–6 milhões de tokens; camada determinística ≈ 0. Medir em 10 documentos antes de extrapolar.
- Custo dominante: **tempo humano** (gold set ~20 documentos; verificação de ~50–100 aliases italiano→EPPO). NÃO SEI quem faz.
- Custo deste estudo: ver CUSTO.md (DeepSeek US$ 0,039; Opus e GPT por assinatura, US$ 0 registrado).

## 15. RISCOS
1. Cristalizar erro de extração com aparência de canônico (menu no corpo 30/30; 4/10 sinais com data errada).
2. Brain vazio por exigir chaves completas (1/1 252).
3. Cemitério de schemas (~60 tabelas vazias hoje).
4. Portão sem validação de conteúdo (11/12) alimentando o Brain.
5. Consolidação falsa (escopo diferente fundido) e contradição falsa (escopo diferente tratado como conflito).
6. Fusão errada de entidades (VITE × VITE DA TAVOLA: mesmo táxon EPPO — a distinção tem de morar no vocabulário).
7. Injeção indireta via texto coletado (OWASP LLM01) — mitigada estruturalmente pela citação verbatim obrigatória.
8. Sem dono do vocabulário agronômico (lacuna de lei: nem Collection nem Intelligence o declaram).
9. Expectativa de «5 anos de história» que o acervo não tem.

## 16. PLANO DE PILOTO
Medição que decide o canário [M]:
| tema | Sala (204) | acervo (1 112) | observações |
|---|---|---|---|
| mosca-da-oliveira | 5 (todos T3/boletins), 3 com Puglia/Úmbria | 8, de 4 fontes | anos citados no texto 2021–2026 |
| míldio × videira (amplo IT/EN) | 35, **31 são estudos T5**, 4 boletins/notícias | 3, de 2 fontes | **0** com Emilia-Romagna/Veneto |
| captura do acervo | — | 2 205/2 205 em 2026-09 | **não há série multi-ano de nada** |

FIRST_CANARY = **mosca-da-oliveira (Bactrocera oleae) × oliveira × Puglia** (ARIF N38 + APOL Brindisi/Lecce, fontes
independentes, mesma semana; já auditado; resposta esperada NO_DEFENSIBLE_ACTION_YET e PORTFOLIO NOT_FOUND).
Míldio × videira fica como 2.º canário, de CAP-SCI (estudos), não de ocorrência regional.

Fases (nenhuma exige schema no banco real):
- **F0 refutação estrutural (1 dia, sem LLM)**: humano estrutura em JSON as assertions de ~12 documentos T3 (os 5 de
  mosca + outros boletins T3); responder 6 perguntas fixas por consulta ao JSON. Se o modelo não representar tempo, lugar,
  evidência e espécie → modelo refutado.
- **F1 extração**: gold set ~20 documentos (2 revisores); comparar dicionário+regra × LLM restrito com citação verbatim ×
  híbrido; medir precisão/recall por campo.
- **F2 prova de valor (§45)**: ~10 perguntas respondíveis HOJE; MODO ANTIGO (arquivos → LLM) × BRAIN (assertions →
  evidência → LLM), mesmo modelo, julgamento cego.
- **F3 histórico**: a pergunta «história em N anos» é feita e a resposta correta é NÃO SEI + lacuna nomeada (acervo de
  set/2026). Isso é PASS de arquitetura, não FAIL.

## 17. CRITÉRIOS DE SUCESSO
PASS (todos): 100 % das assertions com span que verifica verbatim e volta até raw_asset; 0 fusão falsa de entidade no gold;
0 troca SOURCE_LOCATION × FACT_LOCATION e published_at × fact_time; precisão de assertion ≥ 90 % (ocorrência/recomendação);
≥ 5/6 perguntas respondidas ou recusadas corretamente; F2: Brain ≥ modo antigo em precisão e em NÃO SEI correto, com
≥ 30 % menos tokens ou tempo; a pergunta histórica devolve NÃO SEI com lacuna.
FAIL imediato: qualquer fato sem evidência; risco/previsão virando ocorrência; tempo ou lugar inventado; precisão < 80 %
com seção e sem menu; F2 empata em rastreabilidade e NÃO SEI (então o Brain é custo, não valor).
Vetor: só entra se, em ~40 perguntas com gold, FTS+alias+vetor superar FTS+alias em ≥ 10 pontos de recall@10 sem perder precisão.
(Limiares são proposta do LAB, não medição.)

------------------------------------------------------------------------------------------------------------------
## BLOCO DE ENTREGA (§ «EXECUTAR AGORA» da carta IAB)

IAB_STATUS = ESTUDO CONCLUÍDO · CONCEITO VÁLIDO COMO CLASSIFICAÇÃO, NÃO COMO CAMADA NOVA · NADA IMPLEMENTADO · aguarda decisões do dono
LAB_STUDY = lab/estudos/2026-09-27-IAB/IAB_ARCHITECTURE_STUDY.md (+ PACOTE, 3 respostas cegas, BENCHMARK, CONFRONTO)
MODELS_USED = Claude Opus 5.5 · GPT-5.6 Sol · DeepSeek 4.1 Flash — 3/3 (reverificado; o script disse 2/3 por defeito próprio, consertado)
CURRENT_GIT_HEAD = estudo feito sobre produção 554c1ec1bb232b8a3298e3cfb330c8de86413134 · iab-v1 0d0744861e9a874c3f9ffe938a78222d39f88d3a · portal 27b9e674
                   DELTA durante o estudo (medido ao fechar, ~10:50): produção avançou para 2ef6fef86 (+2 commits «DATA-DO-FATO»: o ano de INÍCIO de uma atividade/série não é o tempo do fato — conserta o caso Xylella «2013»). Não muda nenhuma conclusão; reforça o risco 1 (erro de extração cristalizado) como já em correção.
PROPOSED_POSITION_IN_PIPELINE = READY (Sala) → FACT READY (assertions, dono Collection, COL-LAW-502) → Intelligence (derivados, dono Intelligence) → Pote → Casco; referência oficial (C) lateral, dono referencia/. Não é terceira camada.
COLLECTION_CHANGES_REQUIRED = preservar seções; derivado «conteúdo principal» sem menu; números como aparecem; espécie por bloco; aplicar 034/036 e o reprocesso pronto; CSV ISTAT em leis/dados/; extrator de assertions com citação verbatim (depois do piloto); nunca descartar sem FACT_TIME
INTELLIGENCE_CHANGES_REQUIRED = consumir assertion_ids; bloqueio temporal por capacidade, não por item; derivados com inputs=assertion_ids + rule_version (reusar `derivacao`); SUPPORT/CONTRADICTS entre assertions sem vencedor; nunca editar assertion
PROPOSED_STORAGE_MODEL = PostgreSQL existente: ASSERTION + EVIDENCE_SPAN (novas) · ALIAS (nova, filha do vocabulário) · crop/issue/crop_issue/geografia/substancia_ativa/pessoa/derivacao (reusar, estender) · referência C com validade · vistas reconstruíveis · append-only · sem grafo/vetor no V1
ESTIMATED_BYTES_PER_ITEM = 0,6–1,5 KB por assertion + 1 evidência, com índices — ESTIMATIVA ancorada na tabela de revisões da Sala (466 944 B / 478 linhas ≈ 977 B/linha, medido); a medir com pg_column_size no piloto
FIRST_CANARY = mosca-da-oliveira × oliveira × Puglia (ARIF + APOL; 5 boletins T3 na Sala, 8 no acervo) — ESTRUTURAL; histórico = NÃO SEI + lacuna. Míldio × videira × ER/Veneto REJEITADO como 1.º: 0 documentos regionais (31 de 35 são estudos).
DOCUMENTATION_CHANGES = (dono decide) Bíblia da Coleta: COL-LAW-202 TARGET→CURRENT; ativar a cláusula da l.1409 (STATEMENT/ASSERTION vira entidade); declarar dono do vocabulário agronômico. Bíblia da Intelligence: seção «consumo de assertions» e classe C. Um CONTRATO subordinado (padrão docs/intelligence/*-CONTRACT-V1.md), não uma terceira Bíblia. System Map: peças em COLETA (extração de assertions) e INTELIGÊNCIA (derivados) — AGENTS.md só admite 3 faixas. Know-how: § com este estudo como ponteiro.
NEXT_SAFE_STEP = F0: estruturar à mão, em JSON fora do banco, as assertions de ~12 boletins T3 (incluindo os 5 de mosca) e responder 6 perguntas fixas — 1 dia, zero schema, zero LLM, zero risco para a produção. Antes: 4 decisões do dono (abaixo).

DECISÕES QUE SÃO DO DONO
1. Quem é dono do vocabulário agronômico (cultura, praga, molécula, lugar)? Hoje nenhuma lei declara.
2. Autoriza COL-LAW-202 passar de TARGET para CURRENT (e ASSERTION como entidade)?
3. «O que sabíamos em tal data» = o que estava extraído (recorded) ou o que estava coletado (captured)?
4. Quem dá o tempo humano do gold set (~20 documentos) e da verificação italiano→EPPO?

## GATE §49 — o que o ESTUDO já consegue afirmar
ITALIAN_AGRO_BRAIN_CONCEPT_VALID = YES como conceito (3/3 motores + Bíblias já preveem CLAIM/FACT); NÃO PROVADO em execução
OBSERVED_DERIVED_SEPARATED       = YES no desenho (A afirmado × B derivado × C referência, donos distintos); NÃO SEI em execução
RAW_IDENTITY_REUSED              = YES no desenho (FK para derived_artifact → raw_asset; hash_texto = sha256 1 112/1 112); NÃO SEI em execução
PROVENANCE_END_TO_END            = NÃO SEI (desenho permite; exige piloto)
TEMPORAL_MODEL_VALID             = NÃO SEI (desenho herdado do que a Sala já faz; exige piloto)
GEOGRAPHY_MODEL_VALID            = PARCIAL — escada e leitor existem; degrau COMUNE desligado (CSV ISTAT ausente) → NO para comune hoje
LOW_STORAGE_OVERHEAD             = YES — ESTIMATIVA ancorada (0,6–1,5 KB/item; < banco atual)
HISTORICAL_CANARY                = NÃO EXECUTADO; previsão medida: FAIL por falta de acervo (tudo capturado em set/2026) — não por arquitetura
KNOWLEDGE_RETRIEVABLE            = NÃO SEI
CLAIM_TO_EVIDENCE                = NÃO SEI (desenho com citação verbatim + hash torna o teste possível)

HARD STOP. Nenhum schema, migration, código ou commit foi criado no projeto.

## EM PALAVRAS SIMPLES
O senhor pediu para estudar uma «memória agrícola» que lembre por anos o que o Sintonia aprende. Três inteligências
diferentes analisaram o mesmo material sem ver umas às outras, e eu confrontei o que elas disseram com medições no banco.

O que concluímos:
- A ideia é boa, e as regras do projeto já a previam. Mas ela não deve virar um «prédio novo» ao lado da coleta e da
  inteligência: é encher gavetas que já existem (e estão vazias) e acrescentar duas ou três. Prédio novo = a mesma verdade
  em dois lugares.
- A sua divisão entre «observado» e «concluído» está certa, mas falta uma terceira gaveta: «o que é oficial» (produto
  autorizado, registro). Se misturar, o sistema poderia «provar» uma doença mostrando uma lista de produtos.
- Quase tudo que coletamos não é «observado por nós»: é «o boletim X disse». A memória tem de guardar sempre quem disse,
  onde está escrito e com que certeza — e só aceitar uma frase se ela existir, letra por letra, no documento.
- Cabe folgado: cerca de 1 KB por conhecimento, menos que o banco atual inteiro.
- O ponto mais importante: hoje **não existe material para contar história de anos**. Tudo o que temos foi coletado em
  setembro de 2026. Um teste do tipo «conte a história da praga nos últimos 5 anos» vai falhar por falta de papel, não por
  falta de memória. As três inteligências sugeriram testar com míldio da videira; eu conferi e, dos 35 textos, 31 são
  estudos científicos e nenhum fala de Emilia-Romagna ou Veneto. Por isso recomendo começar pela mosca-da-oliveira na
  Puglia, onde temos boletins de duas fontes diferentes na mesma semana.
- Próximo passo seguro (1 dia, sem mexer em nada): alguém organiza à mão uns 12 boletins e vemos se as perguntas saem
  certas. Antes disso, preciso de 4 decisões suas (listadas acima).
