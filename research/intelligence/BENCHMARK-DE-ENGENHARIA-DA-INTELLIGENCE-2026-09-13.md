# BENCHMARK DE ENGENHARIA DA INTELLIGENCE — SINTONIA EAME

**Data:** 2026-09-13  
**Status:** `NON_CANONICAL_RESEARCH_INPUT`  
**Missão:** preparar a Bíblia de Engenharia da Intelligence sem iniciar implementação.  
**Regra:** este documento orienta decisões; **não é autoridade arquitetural**. A autoridade só nasce quando uma decisão é incorporada à Bíblia/contrato/know-how apropriado.

---

# 0. PERGUNTA

Como construir uma Intelligence que transforme material admitido pela Collection em sinais, cruzamentos, findings e oportunidades úteis, sem:

- confundir volume com evidência;
- contar a mesma evidência várias vezes;
- inventar geografia, tempo, identidade ou causalidade;
- promover ausência aparente a zero;
- esconder incerteza;
- produzir recomendação porque o portal precisa de um card;
- misturar previsão com fato;
- misturar inteligência com coleta;
- permitir que LLM, UI ou score se tornem nova fonte de verdade;
- perder provenance/lineage ao derivar;
- criar automação insegura;
- depender de memória de chat ou de um analista específico.

---

# 1. AUTORIDADES INTERNAS E EVIDÊNCIA HISTÓRICA CONSULTADAS

Este benchmark não parte do zero. O SINTONIA já acumulou provas que valem mais do que opinião externa.

## 1.1 Refresh final de Intelligence EAME

Fonte histórica: `docs/refresh/FINAL-INTELLIGENCE-REFRESH-EAME.md` em `claude/eame-one-final-intelligence-refresh`.

Achados transferíveis:

- grafo de dependências deve vir **antes** da contagem de convergência;
- 5 de 6 alegações de convergência não sobreviveram ao grafo;
- duas leituras do mesmo documento não são duas fontes;
- duas observações da mesma entidade não são automaticamente duas famílias independentes;
- SCIENCE e RESEARCHER podem compartilhar a mesma origem e não devem inflar independência;
- sidebar/menu pode introduzir falso conteúdo no corpo;
- uma observação verdadeira pode ser inacionável por estar fora da janela temporal;
- identidade de concorrente/creator não é sinal sobre issue;
- capability de comparação temporal não prova valor operacional da cadência;
- ausência de chave de junção impede crossing mesmo quando cada lado está correto;
- reprocessar material preservado pode ter mais valor do que coletar de novo;
- `NO_DEFENSIBLE_ACTION_YET` precisa ser um resultado legítimo.

## 1.2 Motor Intelligence V2 — requisitos existentes

Fonte: `docs/intelligence/MOTOR-INTELLIGENCE-V2-REQUIREMENTS.md` em `claude/intelligence-backlog-canonical`.

Leis já maduras que precisam ser preservadas pela Bíblia:

- consulta global das famílias aplicáveis por Opportunity;
- `COLLECTION EXISTS != FAMILY CONSULTED`;
- completude de portfólio ADAMA por Opportunity;
- convergência separando `EXTERNAL_SIGNAL_COUNT`, `INDEPENDENT_SOURCE_COUNT`, `STRUCTURAL_VALIDATION_COUNT`, `INTELLIGENCE_FAMILY_COUNT`;
- Radar Futuro não nasce de data matemática;
- identidade global de CLAIM;
- histórico append-only;
- `EVIDENCE_CLASS`, `EVIDENCE_STATE`, `EVIDENCE_STRENGTH`, `EVIDENCE_REASON` separados;
- `EVIDENCE_FAMILY`, `DATASET_FAMILY`, `SOURCE_FAMILY` separados;
- universo definido pela pergunta, não pela pasta;
- completude exige universo declarado;
- `ZERO_PROVED != NOT_FOUND_IN_SCANNED_UNIVERSE`;
- capability map tem um dono;
- gate precisa saber falhar;
- normalização antes de backfill;
- sinal de pressão de doença != oportunidade comercial;
- ausência de evidência não gera ação.

## 1.3 Snapshot de Intelligence EAME

Fonte histórica: `docs/red-team/C-SNAPSHOT-DE-INTELIGENCIA-EAME.md`.

Lições:

- datasets nacionais têm assimetrias reais; mesma camada não possui a mesma forma/força em todos os países;
- READ_FAILURE não é ZERO;
- afiliação de pesquisador não é local do experimento;
- identidade provada de pessoa não é prova de expertise específica nem de fala pública;
- comentário pode medir demanda por informação e não estado do campo;
- contagens agronômicas precisam carregar `n`, cobertura e escopo;
- registro/autorização não prova venda, disponibilidade comercial ou participação de mercado.

---

# 2. BENCHMARK EXTERNO — O QUE VALE IMPORTAR COMO PRINCÍPIO

## 2.1 Databricks / Unity Catalog

Referências:

- https://docs.databricks.com/aws/en/data-governance/unity-catalog
- https://docs.databricks.com/aws/en/data-governance/unity-catalog/data-lineage
- https://docs.databricks.com/aws/en/data-governance/unity-catalog/data-quality-monitoring
- https://docs.databricks.com/aws/en/data-governance/unity-catalog/data-quality-monitoring/anomaly-detection

### O pulo do gato

Governança não é uma tela acima da plataforma. Ela opera **embaixo de cada interação**, aplicando controle de acesso, auditoria, discovery e lineage. Lineage é usado para impacto, root cause e dependências. Qualidade não é checada uma vez: freshness/completeness são observadas ao longo do tempo.

### Transferência para o SINTONIA

1. Todo produto da Intelligence precisa nascer governado e rastreável, não receber provenance depois.
2. Finding/Signal/Opportunity precisam carregar lineage até as observações admitidas que os sustentam.
3. Intelligence precisa monitorar freshness, cobertura, completude e drift dos seus próprios inputs/outputs.
4. Cobertura automática de lineage tem limites; limitação deve ficar explícita como `UNKNOWN/LIMITATION`, nunca parecer total.
5. Qualidade precisa ser proporcional à importância: não gastar a mesma profundidade de validação em todo material.

### O que NÃO copiar

- não transformar o SINTONIA em lakehouse;
- não copiar hierarquia catalog/schema/table para domínios onde ela não resolve a pergunta;
- não inferir que ter catálogo centralizado resolve qualidade analítica.

---

## 2.2 Palantir Foundry / Ontology

Referências:

- https://www.palantir.com/docs/foundry/architecture-center/ontology-system
- https://www.palantir.com/docs/foundry/ontology/why-ontology
- https://www.palantir.com/docs/foundry/architecture-center/aip-architecture

### O pulo do gato

A arquitetura modela decisões por quatro eixos conectados: **data + logic + action + security**. Também registra `decision lineage`: decisão, versão dos dados, aplicação/lógica e contexto. A IA pode preparar uma ação e entregar para revisão humana; autonomia é graduada, observada e pode aumentar ou diminuir.

### Transferência para o SINTONIA

1. Não basta `finding -> card`. Precisamos saber **qual lógica** transformou quais evidências em qual judgment.
2. Recommendation deve possuir lineage próprio separado do finding factual.
3. Intelligence deve parar antes da ação operacional por padrão; ação pode ser proposta, mas execução pertence a uma camada autorizada.
4. Autonomia de IA deve ser granular, explícita e reversível.
5. Feedback posterior pode melhorar calibragem, mas não deve reescrever silenciosamente o judgment histórico.

### O que NÃO copiar

- não criar uma mega-ontology antes de provar os conceitos do SINTONIA;
- não misturar read model e write/action model;
- não dar a um agente capacidade de escrita só porque ele consegue raciocinar sobre o dado.

---

## 2.3 OpenLineage

Referências:

- https://openlineage.io/docs/spec/facets/
- https://openlineage.io/docs/spec/facets/run-facets/
- https://openlineage.io/docs/spec/facets/job-facets/lineage/

### O pulo do gato

Lineage possui entidades pequenas e separadas (`Run`, `Job`, `Dataset`) enriquecidas por facets atômicas. A especificação permite declarar relações exatas e evita inferir um produto cartesiano entre todos os inputs e outputs de uma execução.

### Transferência para o SINTONIA

1. `INTELLIGENCE_RUN != RULE/LOGIC != INPUT != OUTPUT`.
2. Cada execução precisa de identidade própria.
3. Parâmetros, versões, modelo, prompt/policy e universo consultado devem ser facets/metadados explícitos do run.
4. Não inferir `A -> C` só porque A e C participaram da mesma execução.
5. Relação exata Claim/Evidence/Finding precisa ser first-class, não reconstruída pelo portal.

---

## 2.4 W3C PROV-O

Referência:

- https://www.w3.org/TR/prov-o/

### O pulo do gato

Provenance precisa ser interoperável e capaz de distinguir coisas produzidas, atividades que as produziram e responsabilidade/agência associada.

### Transferência para o SINTONIA

A Bíblia deve preservar identidades distintas para:

- entidade/fato/evidência;
- atividade/run/derivação;
- agente/mecanismo/modelo/humano responsável;
- relações de geração, uso e derivação.

Não é necessário adotar PROV-O literalmente na V1. É necessário não criar um modelo incompatível com essas distinções maduras.

---

## 2.5 OpenMetadata

Referências:

- https://docs.open-metadata.org/v1.12.x/how-to-guides/data-quality-observability
- https://docs.open-metadata.org/v1.12.x/how-to-guides/data-lineage
- https://docs.open-metadata.org/v1.12.x/how-to-guides/data-lineage/column

### O pulo do gato

Discovery, lineage, profiling, testes, incidentes, alerts e root-cause analysis ficam próximos do ativo. O consumidor consegue ver upstream e downstream, estado de qualidade e histórico operacional no mesmo contexto.

### Transferência para o SINTONIA

1. Todo finding importante deve expor health/proof junto dele.
2. Falha de qualidade precisa abrir estado/incidente rastreável; não simplesmente fazer o card sumir.
3. Manual lineage e automatic lineage precisam ser distinguíveis.
4. Impact analysis deve preceder alterações de contrato/normalização/identidade.

---

## 2.6 Dagster / dbt

Referências:

- https://docs.dagster.io/
- https://docs.getdbt.com/

### O pulo do gato

Dagster trata ativos, lineage, observabilidade e testabilidade como partes do mesmo sistema. dbt distingue estado/artefato aplicado e usa state-aware execution para evitar reconstruções desnecessárias quando consegue provar que lógica e dados relevantes não mudaram.

### Transferência para o SINTONIA

1. `DEFINED != MATERIALIZED != OBSERVED != VALIDATED`.
2. Reuso só pode ocorrer quando equivalência do input + lógica + parâmetros estiver provada.
3. Um rerun não deve apagar lineage do run anterior.
4. Reprocessamento dirigido por mudança é preferível a recalcular tudo sem motivo.

---

## 2.7 ODNI ICD 203 — Analytic Standards

Referência oficial:

- https://www.dni.gov/files/documents/ICD/ICD-203.pdf

### O pulo do gato

A produção analítica madura não é apenas encontrar informação. Ela exige:

- objetividade;
- consciência de premissas e viés;
- consideração de informação contrária;
- oportunidade temporal;
- uso de todas as fontes relevantes disponíveis;
- avaliação de qualidade/credibilidade das fontes;
- explicitação de incerteza;
- separação entre informação, premissas e judgments;
- análise de alternativas;
- relevância para o usuário;
- argumentação lógica;
- explicação de mudança de judgment ao longo do tempo;
- revisão sistemática dos produtos analíticos.

### Transferência para o SINTONIA

Esse é provavelmente o benchmark externo mais diretamente aplicável ao **método analítico**.

A Bíblia precisa tornar first-class:

```text
SOURCE FACT
ASSUMPTION
HYPOTHESIS
JUDGMENT
ALTERNATIVE
UNCERTAINTY
CONTRARY_EVIDENCE
CHANGE_IN_JUDGMENT
```

Um LLM que entrega uma conclusão sem esses rastros não produziu Intelligence auditável.

---

## 2.8 CIA — Structured Analytic Techniques

Referência:

- https://www.cia.gov/resources/csi/books-monographs/a-tradecraft-primer/

### O pulo do gato

Informação incompleta e ambígua, complexidade e limitações cognitivas exigem técnicas estruturadas para reduzir vieses e tornar raciocínio examinável.

### Transferência para o SINTONIA

Para findings de alto impacto, baixa confiança, alta complexidade ou futuro incerto, exigir mecanismos como:

- premissas-chave explícitas;
- evidência pró e contra;
- hipóteses alternativas;
- indicadores que mudariam o judgment;
- red team/challenge analysis quando necessário.

Não precisa transformar cada item simples em um relatório de inteligência de Estado. Profundidade deve ser proporcional ao risco da decisão.

---

## 2.9 UK Government Office for Science — Futures Toolkit / Horizon Scanning

Referências:

- https://www.gov.uk/government/publications/futures-toolkit-for-policy-makers-and-analysts/the-futures-toolkit-html
- https://www.gov.uk/government/publications/horizon-scanning-template/horizon-scanning-template

### O pulo do gato

Horizon scanning procura sinais emergentes e mudanças potenciais, mas separa topic/signal, escala de impacto, certeza e horizonte temporal. É ferramenta para lidar com futuros incertos, não máquina de converter data futura em previsão.

### Transferência para o SINTONIA

```text
WEAK_SIGNAL != FORECAST
FORECAST != FACT
SCENARIO != PREDICTION
FUTURE_DATE != OPPORTUNITY
```

Radar Futuro deve declarar:

- sinal observado;
- evidência;
- horizonte;
- impacto potencial;
- incerteza;
- condições/indicadores que fariam o sinal ganhar ou perder força.

---

# 3. SEGURANÇA — BENCHMARK EXTERNO

## 3.1 NIST AI RMF + GenAI Profile

Referências:

- https://www.nist.gov/itl/ai-risk-management-framework
- https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence

### Transferência

Risco de IA deve ser tratado ao longo do lifecycle, com governança, medição e gestão explícitas. Para o SINTONIA:

- uso de LLM é componente sob avaliação, não oráculo;
- modelos/prompts/policies precisam de versionamento e evals;
- outputs gerados por IA precisam ser distinguíveis de evidência de fonte;
- mudança de modelo pode mudar comportamento sem mudar dados;
- riscos de hallucination, overconfidence e information integrity precisam de testes próprios;
- informação sensível não pode ser enviada a provedor/modelo sem autorização e política explícita.

## 3.2 NIST SSDF

Referência:

- https://csrc.nist.gov/pubs/sp/800/218/final

### Transferência

Segurança precisa entrar no ciclo normal de engenharia. A Bible não deve dizer apenas “seja seguro”; deve exigir que mudanças relevantes passem por:

- preparação do ambiente de desenvolvimento;
- proteção de código e artefatos;
- produção de software bem protegido;
- resposta a vulnerabilidades e causas-raiz;
- dependências e supply chain sob controle.

## 3.3 NIST Zero Trust

Referência:

- https://csrc.nist.gov/pubs/sp/800/207/final

### Transferência

Nenhuma confiança implícita porque componente está “dentro do SINTONIA”.

```text
AUTHENTICATED != AUTHORIZED
CAN READ != CAN WRITE
CAN ANALYZE != CAN ACT
HUMAN PERMISSION != AGENT PERMISSION
```

Permissões devem seguir recurso, identidade e propósito. Intelligence V1 deve ser read/derive-first; qualquer ação/escrita operacional exige contrato e autorização separados.

---

# 4. PADRÕES QUE SE REPETEM NOS MELHORES SISTEMAS

O benchmark converge em nove princípios:

1. **SEMÂNTICA PRIMEIRO.** Entidades e relações explícitas antes de score/UI.
2. **LINEAGE FIRST-CLASS.** Resultado sem origem e lógica é produto quebrado.
3. **DECLARED != OBSERVED.** Catálogo/contrato não prova execução.
4. **QUALITY CONTÍNUA.** Freshness, completude e drift precisam ser observados.
5. **DECISION CONTEXT.** O valor aparece quando análise responde uma decisão real.
6. **UNCERTAINTY EXPLÍCITA.** Incerteza não é bug; esconder incerteza é bug.
7. **HUMAN/AI BOUNDARY.** IA pode auxiliar, mas autonomia precisa ser limitada e provada.
8. **SECURITY CROSS-CUTTING.** Segurança atravessa data, lógica e ação.
9. **LEARNING WITHOUT HISTORY REWRITE.** Feedback melhora futuras decisões sem adulterar o passado.

---

# 5. ANTI-PADRÕES QUE O SINTONIA PRECISA PROIBIR

## AP-01 · COUNTING THE SAME THING TWICE

Mesmo dado, dataset, documento, fonte derivada ou entidade não pode virar múltiplas pernas independentes.

## AP-02 · SCORE HIDES THE EVIDENCE

Score é projeção derivada. Nunca pode substituir evidência, reasoning ou incerteza.

## AP-03 · LLM AS SOURCE

LLM não é fonte factual de mundo. É mecanismo de transformação/raciocínio cuja saída precisa de lineage e validação.

## AP-04 · PORTAL REBUILDS INTELLIGENCE

Portal não cruza, reclassifica ou completa relações que a Intelligence não produziu.

## AP-05 · FUTURE DATE BECOMES FORECAST

Data/janela/calendário não prova evento futuro nem oportunidade.

## AP-06 · MISSING BECOMES ZERO

Sem universo completo, zero não existe como conclusão.

## AP-07 · FRESH BUT USELESS

Coleta diária não prova valor analítico diário.

## AP-08 · TRUE BUT TOO LATE

Fato verdadeiro fora da janela não pode aparecer como `ACT_NOW`.

## AP-09 · IDENTITY BECOMES EXPERTISE OR SIGNAL

Pessoa/empresa/conta identificada não prova autoridade temática, comportamento ou sinal.

## AP-10 · STRUCTURAL VALIDATION BECOMES INDEPENDENT SIGNAL

Registro, catálogo e label podem validar estrutura sem constituir três confirmações independentes.

## AP-11 · HIDDEN JOIN FAILURE

Se dois lados não compartilham chave factual provada, crossing é `NOT_POSSIBLE/UNKNOWN`, não aproximação silenciosa.

## AP-12 · CURRENT OUTPUT OVERWRITES HISTORY

Correção cria nova versão/evento; não apaga judgment anterior.

## AP-13 · AI CAN READ, THEREFORE AI CAN ACT

Permissão analítica não implica permissão operacional.

---

# 6. MODELO CONCEITUAL RECOMENDADO

A espinha recomendada para a Intelligence é:

```text
SALA DE ESPERA
    ↓
INTELLIGENCE REQUEST / QUESTION
    ↓
INPUT RESOLUTION
    ↓
FACT / CLAIM / EVIDENCE GRAPH
    ↓
DEPENDENCY + INDEPENDENCE GRAPH
    ↓
NORMALIZATION / ENTITY RESOLUTION
    ↓
CROSSINGS
    ↓
SIGNALS
    ↓
HYPOTHESES / ALTERNATIVES
    ↓
FINDINGS / JUDGMENTS
    ↓
TEMPORAL + GEOGRAPHIC + COMPLETENESS GATES
    ↓
OPPORTUNITY / ATTENTION ITEM / FUTURE SIGNAL
    ↓
INTELLIGENCE PACKAGE
    ↓
INTELLIGENCE TOOLS / DELIVERY
```

Sempre lateralmente:

```text
PROVENANCE
UNCERTAINTY
CONTRARY EVIDENCE
RUN / VERSION / PARAMETERS
SECURITY
QUALITY / OBSERVABILITY
```

E com retorno controlado:

```text
INTELLIGENCE
  ↓ detects
COLLECTION GAP REQUEST
  ↓
CANONICAL COLLECTION FLOW
```

Nunca Intelligence -> collector direto.

---

# 7. IDENTIDADES QUE NÃO DEVEM SER COMPRIMIDAS

Proposta para decisão na Bíblia:

```text
INTELLIGENCE_RUN
!= INTELLIGENCE_REQUEST
!= FACT
!= CLAIM
!= EVIDENCE
!= ASSUMPTION
!= HYPOTHESIS
!= SIGNAL
!= CROSSING
!= FINDING/JUDGMENT
!= OPPORTUNITY
!= RECOMMENDATION
!= ACTION
```

O ponto não é criar 11 tabelas imediatamente. É impedir que um único `card` ou `finding` vire saco semântico que não pode ser auditado.

---

# 8. “PULOS DO GATO” MAIS IMPORTANTES PARA O SINTONIA

## 8.1 Construir o grafo de dependências antes do motor de score

Score depois. Independência primeiro.

## 8.2 Preservar a cadeia de raciocínio auditável sem depender de chain-of-thought privado

Guardar:

- evidências usadas;
- premissas declaradas;
- regras/algoritmo/prompt versionado;
- alternativas consideradas;
- rationale resumido e verificável;
- evidência contrária;
- estados/gates.

Não é necessário nem desejável depender de raciocínio privado de modelo.

## 8.3 Trabalhar com “universe contracts”

Toda afirmação de completude/zero/ausência precisa saber qual universo deveria ter sido lido e qual realmente foi lido.

## 8.4 Tratar tempo como parte da acionabilidade, não só metadata

Fato pode continuar verdadeiro e deixar de ser útil para ação imediata.

## 8.5 Calibrar Intelligence por resultado posterior

Quando houver outcome legítimo, comparar judgment anterior com o que ocorreu. Não para reescrever passado; para medir calibração.

## 8.6 Separar “relevance” de “truth”

Algo pode ser verdadeiro e irrelevante; relevante e incerto; recente e fraco; antigo e estruturalmente importante.

## 8.7 Introduzir challenge path

Findings de alto impacto devem poder ser contestados por um mecanismo separado do produtor original.

## 8.8 Fazer `NO_DEFENSIBLE_ACTION_YET` ser sucesso epistemológico

O sistema precisa ser recompensado por se recusar a exagerar.

---

# 9. MÉTRICAS QUE FAZEM SENTIDO

Não medir Intelligence por “quantos cards gerou”. Medir por:

```text
PROVENANCE_COMPLETENESS
SOURCE_INDEPENDENCE_ACCURACY
FALSE_CONVERGENCE_RATE
FACTUAL_ERROR_RATE
UNKNOWN_PRESERVATION_RATE
TEMPORAL_ACTIONABILITY_ACCURACY
GEOGRAPHIC_GROUNDING_RATE
UNIVERSE_COMPLETENESS_RATE
CONTRARY_EVIDENCE_COVERAGE
JUDGMENT_CHANGE_TRACEABILITY
REPRODUCIBILITY_RATE
COLLECTION_GAP_PRECISION
CALIBRATION_BY_CONFIDENCE_BUCKET
USER_DECISION_RELEVANCE
SECURITY_POLICY_VIOLATIONS
```

Algumas métricas só serão mensuráveis depois de existir runtime. Até lá: `NOT_MEASURED`.

---

# 10. RED TEAM RECOMENDADO PARA A BÍBLIA

A implementação futura precisa sobreviver a ataques conceituais como:

1. duplicar uma evidência em duas famílias e tentar inflar convergência;
2. transformar sidebar/menu em conteúdo do fato;
3. trocar SOURCE_LOCATION por FACT_LOCATION;
4. trocar PUBLICATION_TIME por FACT_TIME;
5. transformar `NOT_FOUND` em `ZERO_PROVED` sem universo;
6. produzir ACT_NOW para evidência antiga fora da janela;
7. chamar identidade de especialista sem corpus temático;
8. usar catálogo/registro como sinal de campo independente;
9. produzir oportunidade com família aplicável não consultada;
10. ocultar evidência contrária;
11. fazer LLM produzir fato sem support edge;
12. reexecutar com modelo/prompt diferente e reutilizar output anterior como se fosse equivalente;
13. permitir escrita/ação a um agente autorizado apenas para leitura/análise;
14. reescrever finding histórico após correção;
15. produzir forecast a partir de data futura sem modelo/evidência apropriada;
16. cruzar datasets que não compartilham chave factual provada;
17. declarar `PASS` com input vazio;
18. criar score alto a partir de várias validações estruturais dependentes;
19. promover hipótese a fato porque apareceu em muitas fontes que copiaram a mesma origem;
20. entregar finding sem conseguir reconstruir inputs, versão de lógica e gates.

---

# 11. CONCLUSÃO DO BENCHMARK

A Intelligence do SINTONIA não deve ser concebida como “um modelo que lê tudo e acha oportunidades”.

A arquitetura madura é mais próxima de:

> **uma máquina de produção analítica auditável, com grafo de evidência e dependência, provenance completa, incerteza explícita, crossing controlado, gates de completude/tempo/geografia, challenge path e segurança por design.**

O LLM pode participar de tarefas delimitadas — extração, normalização, classificação, geração de hipóteses, síntese — mas não ganha autoridade factual por ser inteligente.

O melhor “pulo do gato” encontrado no benchmark é também compatível com a história interna do projeto:

```text
A QUALIDADE DA INTELLIGENCE NÃO VEM DE TER MAIS FONTES.
VEM DE SABER O QUE CADA FONTE REALMENTE PROVA,
O QUE DEPENDE DO MESMO ORIGINADOR,
QUAL PERGUNTA ESTÁ SENDO RESPONDIDA,
E QUAL PARTE CONTINUA DESCONHECIDA.
```

---

`BENCHMARK_STATUS = COMPLETE_FOR_BIBLE_V0.1`

Este documento não autoriza implementação.