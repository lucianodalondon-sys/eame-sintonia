# BÍBLIA DE ENGENHARIA DA INTELLIGENCE — SINTONIA EAME

```text
BIBLE_ID = SINTONIA-INTELLIGENCE-BIBLE
VERSION = V0.3
STATUS = CANONICAL
DATE = 2026-09-13
REVISED = 2026-09-14
PROMOTED = 2026-09-14
IMPLEMENTATION_AUTHORIZED = SOMENTE_A_PRIMEIRA_MISSAO_DA_SECAO_32_E_SUJEITA_AOS_GATES_UPSTREAM
```

> **V0.3 não reabre a promoção.** Ela acrescenta quatro secções — 34, 35, 36 e
> 37 — e não toca em nenhuma lei de 000 a 260. A fronteira de implementação é a
> mesma letra que a V0.2 declarou: uma missão, a da secção 32, e ainda
> dependente de gates que não são desta Bíblia para abrir.
>
> ```text
> ACRESCENTAR LEI != AUTORIZAR OBRA NOVA
> ```

> Esta é a **Bíblia de Engenharia da Intelligence**, não um relatório, backlog, handoff, design de portal ou prova de implementação.
>
> **Lei declarada não prova implementação.**

---

## O REGISTO DA PROMOÇÃO

Ela nasceu `CANDIDATE_FOR_CANONICAL_REVIEW` porque a governança mediu
`CONTROL_PLANE_ATOMICITY = FAIL`: código, Bíblias, Know-how e registry não
formavam um único snapshot canônico. Promovê-la naquela branch criaria a
divergência que o Control Plane existe para impedir.

Isso deixou de ser verdade, e não por decreto: `C-INT-ATOMICITY-01` integrou as
autoridades numa árvore só, e `C-CTRL-INT-NIGHT-02` pagou os dois bloqueadores
que restavam — nenhum dos quais era o que o nome dizia. As nove condições da
secção 31 foram re-medidas, uma a uma, e passaram todas.

```text
PROMOTED_BY   C-CTRL-INT-NIGHT-02 · autorização humana explícita no enunciado,
              condicional a 9/9 gates objetivos
GATES         9 / 9 PASS   (a 6 fechou com PORTAO_DO_CONTROLE=PASS · 22
              provas nesse instante; o portao tem 23 hoje, porque a propria
              promocao trouxe a prova BIBLE_STATUS_MATCHES_REGISTRY)
SUPERSEDES    A-BIBLIA-INTELIGENCIA — o «INVENTÁRIO DAS LEIS», que recusa o
              título no próprio cabeçalho. A relação é de IDENTIDADE, e a outra
              ponta declara-a de volta no registo.
```

**O que a promoção autoriza, e só isso.** `IMPLEMENTATION_AUTHORIZED = NO`
nasceu colado a `STATUS = CANDIDATE`: enquanto esta Bíblia fosse candidata,
implementar contra ela era construir sobre lei não aprovada. A secção 32 nomeia
a **primeira missão após promoção** e delimita-a. É essa, e mais nenhuma, que
esta promoção autoriza.

**E autorizar não é destrancar.** Esta Bíblia é a lei da Intelligence; ela não
manda nos portões da Collection, e não os abre. A missão da secção 32 continua
sujeita aos gates a montante — entre eles
[`docs/operacao/TRAVA-DA-INTELIGENCIA.json`](docs/operacao/TRAVA-DA-INTELIGENCIA.json),
que hoje mede `COLLECTION_FOUNDATION_CLOSED = NAO`, e o gate da própria secção
32, que exige **um item real** na Sala de Espera, hoje medida a zero.

```text
PROMOVER A LEI   != AUTORIZAR A OBRA
AUTORIZAR A OBRA != DESTRANCAR O PORTAO DE QUEM VEM ANTES
```

Tudo o resto — Intelligence Tools, Portal, UI, Opportunity, França, Espanha,
controlador EAME — continua fora, e continua a precisar dos gates da secção 26.

---

# 0. AUTORIDADE, ESCOPO E OWNER

## INT-LAW-000 — ONE CONCEPT → ONE OWNER

Esta Bíblia só pode possuir conceitos que não pertencem a outra autoridade canônica.

A reconciliação com `BIBLIA-CANONICA-DA-COLETA.md` V1.4 mostrou que a Collection já reserva o contrato factual `CLAIM / FACT` para separar artefato de fato extraído (`ARTIFACT → CLAIM`). Portanto:

```text
COLLECTION OWNS:
RAW / ARTIFACT / DERIVED / STRUCTURED / ADMISSION
SOURCE FACTUAL CLAIM / FACT EXTRAÍDO
IDENTIDADE E PROVENIÊNCIA DESSE CLAIM/FACT

INTELLIGENCE OWNS:
INTELLIGENCE_REQUEST
INTELLIGENCE_RUN
SUPPORT / CONTRADICTION RELATIONS
DEPENDENCY / INDEPENDENCE GRAPH
CROSSING
ANALYTIC_SIGNAL
ANALYTIC_ASSUMPTION
ANALYTIC_HYPOTHESIS
ANALYTIC_JUDGMENT / FINDING
OPPORTUNITY / ATTENTION ITEM / FUTURE SIGNAL
ANALYTIC_RECOMMENDATION
```

**Intelligence consome CLAIM/FACT admitido. Não fabrica um segundo CLAIM/FACT concorrente.**

Se no futuro o contrato factual mudar de owner, a mudança exige decisão arquitetural explícita e reconciliação das duas Bíblias.

## INT-LAW-001 — O que esta Bíblia governa

Após promoção explícita, esta Bíblia é candidata a governar:

- fronteira e entrada da Intelligence;
- identidade dos objetos analíticos;
- relação entre claims/evidências admitidas e julgamentos;
- dependência, independência, crossing e convergência;
- incerteza, premissas e alternativas;
- completude/universos na análise;
- temporalidade e geografia analíticas;
- Future Radar / horizon scanning;
- uso de IA/LLM;
- segurança da Intelligence;
- qualidade, observabilidade, evals e red team;
- saída para Intelligence Tools / Delivery.

## INT-LAW-002 — O que esta Bíblia não governa

Não possui:

- leis da Collection;
- SOURCE_ID / DOCUMENT_ID / RAW_OBSERVATION_ID;
- identidade de RUN da Collection;
- armazenamento RAW;
- aquisição;
- Admission;
- UI/portal;
- Design System;
- deploy;
- execução comercial;
- ação humana final;
- estado real do runtime.

## INT-LAW-003 — Ordem do SINTONIA

```text
COLLECTION
→ INTELLIGENCE
→ INTELLIGENCE TOOLS / VALIDATION
→ CASCO / PORTAL
```

Portal não puxa arquitetura para trás.

---

# 1. O QUE É INTELLIGENCE

## INT-LAW-010 — Intelligence começa na Sala de Espera

```text
INTELLIGENCE_INPUT = MATERIAL ADMITIDO / READY NA SALA DE ESPERA
```

Collection termina na Sala de Espera. Intelligence não redefine Admission para conseguir material conveniente.

## INT-LAW-011 — Intelligence é produção analítica auditável

Intelligence não é “resumir documentos”. Ela combina claims/fatos/evidências admitidos para produzir, quando houver base:

```text
SUPPORT / CONTRADICTION RELATIONS
→ DEPENDENCY / INDEPENDENCE GRAPH
→ CROSSINGS
→ ANALYTIC_SIGNALS
→ HYPOTHESES / ALTERNATIVES
→ FINDINGS / JUDGMENTS
→ OPPORTUNITIES / ATTENTION ITEMS / FUTURE SIGNALS
```

com lineage, incerteza e limites explícitos.

## INT-LAW-012 — NO_DEFENSIBLE_ACTION_YET é sucesso epistemológico

```text
NO_DEFENSIBLE_ACTION_YET
```

é saída válida quando a evidência não suporta promoção.

Quantidade de cards não mede qualidade.

## INT-LAW-013 — TRUE ≠ RELEVANT ≠ ACTIONABLE

Algo pode ser verdadeiro e irrelevante; relevante e incerto; verdadeiro e fora da janela operacional.

## INT-LAW-014 — Intelligence não fabrica necessidade

Ausência de opportunity não pode ser corrigida relaxando gates para abastecer portal.

---

# 2. FRONTEIRAS ENTRE COLLECTION, INTELLIGENCE E DELIVERY

## INT-LAW-020 — Collection Gap volta pela Collection canônica

Intelligence pode detectar `COLLECTION_GAP`, mas não chama collector diretamente.

```text
INTELLIGENCE
→ COLLECTION_GAP_REQUEST
→ COLLECTION ORCHESTRATOR
→ COLLECTOR
→ COLLECTION RUN
→ RAW
→ DERIVED
→ STRUCTURED
→ ADMISSION
→ SALA DE ESPERA
→ INTELLIGENCE
```

## INT-LAW-021 — COLLECTION EXISTS ≠ FAMILY CONSULTED

Existência de material/coleção não prova que a família foi consultada para a pergunta atual.

## INT-LAW-022 — Intelligence ≠ Delivery

Intelligence produz objetos analíticos. Delivery/Casco decide como expor objetos autorizados.

## INT-LAW-023 — Portal não reconstrói Intelligence

Portal não pode:

- refazer crossing;
- completar relação ausente;
- recalcular independência;
- converter UNKNOWN em PASS;
- reclassificar finding por conveniência.

## INT-LAW-024 — RECOMMENDATION ≠ ACTION

Por padrão:

```text
INTELLIGENCE MAY PROPOSE
INTELLIGENCE DOES NOT EXECUTE OPERATIONAL ACTION
```

Write/action exige owner, contrato, autorização e prova próprios.

---

# 3. IDENTIDADES ANALÍTICAS

## INT-LAW-030 — Não existe saco semântico único

Não comprimir:

```text
COLLECTION_CLAIM / FACT      ← upstream, owner Collection
INTELLIGENCE_REQUEST
INTELLIGENCE_RUN
SUPPORT_EDGE
CONTRADICTION_EDGE
ANALYTIC_ASSUMPTION
ANALYTIC_HYPOTHESIS
ANALYTIC_SIGNAL
CROSSING
ANALYTIC_JUDGMENT / FINDING
OPPORTUNITY
ANALYTIC_RECOMMENDATION
ACTION                        ← downstream, fora do baseline
```

Isso não obriga uma tabela para cada conceito; obriga identidades semânticas distintas.

## INT-LAW-031 — Claim factual consumido precisa de identidade global

Preservar a exigência do Motor Intelligence V2: toda claim factual consumida precisa de identidade estável, global, reproduzível e rastreável.

**Mas Intelligence não fabrica essa identidade se o contrato upstream não a possui.** Falta de identidade vira contract/collection gap.

## INT-LAW-032 — SUPPORT ≠ CLAIM

Uma relação de suporte diz que uma evidência/claim suporta outra unidade analítica. Ela não cria novo fato por si só.

## INT-LAW-033 — CONTRADICTION é first-class

Evidência material contrária precisa poder ser ligada explicitamente ao judgment que afeta.

## INT-LAW-034 — ANALYTIC_ASSUMPTION é explícita

Premissa usada para atravessar lacuna crítica nunca é renderizada como fato.

## INT-LAW-035 — HYPOTHESIS não vira FACT por repetição

Fontes repetindo hipótese, rumor ou mesma origem não promovem factualidade automaticamente.

## INT-LAW-036 — SIGNAL ≠ FINDING ≠ OPPORTUNITY

Signal é indicação relevante; finding é julgamento analítico; opportunity é promoção com gates adicionais.

## INT-LAW-037 — CROSSING é relação provada, não semelhança

Crossing requer chaves factuais compatíveis ou regra de equivalência explícita.

## INT-LAW-038 — FINDING/JUDGMENT precisa de decision trace auditável

Guardar artifacts compartilháveis:

- claims/evidências usadas;
- support/contradiction edges;
- premissas;
- alternativas materiais;
- regra/algoritmo/prompt versionado quando aplicável;
- rationale resumido verificável;
- gates e estados.

Não depender de chain-of-thought privado de modelo.

## INT-LAW-039 — Opportunity é objeto analítico, não card visual

Identidade e estado da Opportunity independem da UI.

---

# 4. PROVENIÊNCIA E LINEAGE

## INT-LAW-040 — Todo analítico derivado aponta para inputs reais

Finding sem upstream reconstruível é inválido ou `LINEAGE_PARTIAL`.

## INT-LAW-041 — Lineage inclui dado + lógica + execução

Para reproduzir um resultado:

```text
QUAL INPUT ADMITIDO?
QUAL CLAIM/FACT?
QUAL SUPPORT/CONTRADICTION?
QUAL REGRA/ALGORITMO/PROMPT?
QUAL VERSÃO?
QUAL MODELO, SE HOUVE?
QUAIS PARÂMETROS?
QUAL UNIVERSO?
QUAL INTELLIGENCE_RUN?
QUAL OUTPUT?
```

## INT-LAW-042 — Participar do mesmo run não cria edge

```text
SAME_RUN(A,B) != A_DERIVED_FROM_B
```

Não inferir produto cartesiano entre inputs e outputs.

## INT-LAW-043 — DECLARED LINEAGE ≠ OBSERVED LINEAGE

Ambos podem existir; não podem ser fundidos silenciosamente.

## INT-LAW-044 — Limitação de lineage fica visível

```text
LINEAGE_STATE = COMPLETE | PARTIAL | UNKNOWN
```

Sem preencher por plausibilidade.

## INT-LAW-045 — Lineage deve permitir impact analysis

Mudança de contrato, taxonomia, regra ou normalização deve permitir identificar downstream afetado.

---

# 5. INTELLIGENCE RUN

## INT-LAW-050 — INTELLIGENCE_RUN != COLLECTION_RUN != FINDING

São conceitos diferentes.

## INT-LAW-051 — Toda execução tem identidade própria

Cada execução analítica precisa de `INTELLIGENCE_RUN_ID` ou contrato equivalente não ambíguo.

## INT-LAW-052 — Run preserva configuração efetiva

Conforme aplicável:

```text
CODE_VERSION
BIBLE_VERSION
RULESET_VERSION
MODEL / MODEL_VERSION
PROMPT / POLICY VERSION
PARAMETERS
INPUT REFERENCES
UNIVERSE
START / END
RESULT STATE
ERRORS
REUSE STATE
COST
```

## INT-LAW-053 — NOT_RUN ≠ ERROR ≠ EMPTY_RESULT ≠ NO_FINDING

Estados separados.

## INT-LAW-054 — Reuso precisa ser provado

Só reutilizar quando equivalência relevante for provada entre:

```text
INPUTS + LOGIC + PARAMETERS + REQUIRED_CONTEXT
```

“Parece a mesma pergunta” não é cache key.

---

# 6. QUALIDADE E CREDIBILIDADE DA EVIDÊNCIA

## INT-LAW-060 — Qualidade da fonte é contextual

Pergunta: **o que esta fonte prova para esta claim?** Não “esta fonte é boa em geral?”.

## INT-LAW-061 — Quatro eixos de evidência permanecem separados

```text
EVIDENCE_CLASS
EVIDENCE_STATE
EVIDENCE_STRENGTH
EVIDENCE_REASON
```

## INT-LAW-062 — PROVED exige razão compatível

```text
PROVED + UNKNOWN_REASON = INVALID
```

## INT-LAW-063 — Corpo ≠ chrome da página

Sidebar, menu, breadcrumbs, tags e recommendation widgets não provam fato no corpo.

## INT-LAW-064 — Snippet ≠ documento

Preview/trecho não substitui unidade completa quando contexto é necessário.

## INT-LAW-065 — Identidade ≠ expertise

Pessoa/organização identificada não se torna especialista específica sem prova temática.

## INT-LAW-066 — Identidade ≠ sinal

Conta/creator/empresa conhecida não prova comportamento, issue ou evento atual.

## INT-LAW-067 — Registro ≠ mercado

```text
REGISTRATION != SALES
REGISTRATION != COMMERCIAL_AVAILABILITY
REGISTRATION_COUNT != MARKET_SHARE
```

---

# 7. DEPENDÊNCIA E INDEPENDÊNCIA

## INT-LAW-070 — Grafo de dependências vem antes da convergência

Nenhuma contagem multi-sinal é publicada antes da análise de dependência suficiente.

## INT-LAW-071 — Mesmo originador não vira múltiplas fontes

Cópia/sindicação/republicação não cria independência.

## INT-LAW-072 — Mesmo documento, vistas diferentes, continua mesma evidência-base

Listing, metadata e corpo podem oferecer atributos distintos sem virarem fontes independentes.

## INT-LAW-073 — Mesmo dataset, transformações diferentes, não cria origem independente

Pode criar validação estrutural diferente, não nova fonte.

## INT-LAW-074 — Mesma entidade, observações diferentes, exige classificação

Tempo/canal diferente pode trazer nova observação; independência não é automática.

## INT-LAW-075 — Famílias não se comprimem

```text
EVIDENCE_FAMILY
DATASET_FAMILY
SOURCE_FAMILY
```

## INT-LAW-076 — Structural validation não infla independent source count

Catálogo, label e registro podem validar estrutura sem serem três sinais externos independentes.

## INT-LAW-077 — Convergência exige independência + compatibilidade

Verificar pelo menos:

- entidade;
- geografia;
- tempo;
- cultura/issue quando aplicável;
- dependência/originador;
- double counting.

---

# 8. NORMALIZAÇÃO E ENTITY RESOLUTION

## INT-LAW-080 — Normalização precede backfill/crossing massivo

## INT-LAW-081 — Similaridade textual não prova equivalência

Fixture madura:

```text
VITE
VITE DA VINO
VINE
```

não autoriza automaticamente `VITE DA TAVOLA`.

## INT-LAW-082 — Canonical concept ≠ local term

Preservar termo original e mapeamento multilíngue.

## INT-LAW-083 — Entity resolution não fabrica identidade da Collection

Nunca fabricar SOURCE_ID, DOCUMENT_ID ou equivalente upstream.

## INT-LAW-084 — Conflito de normalização permanece conflito

Não escolher “mais provável” para fazer crossing fechar.

---

# 9. CROSSINGS E CONVERGÊNCIA

## INT-LAW-090 — Crossing declara a pergunta que responde

## INT-LAW-091 — Missing join key bloqueia crossing

```text
CROSSING_STATE = NOT_POSSIBLE | UNKNOWN | PARTIAL
```

não closest-match silencioso.

## INT-LAW-092 — Métricas de convergência separadas

```text
EXTERNAL_SIGNAL_COUNT
INDEPENDENT_SOURCE_COUNT
STRUCTURAL_VALIDATION_COUNT
INTELLIGENCE_FAMILY_COUNT
```

## INT-LAW-093 — Score não substitui decomposição

Componentes e motivos permanecem acessíveis.

## INT-LAW-094 — Score alto não derrota gate duro

Gate epistemológico/segurança falho não é compensado por pontos.

## INT-LAW-095 — Correlação ≠ causalidade

Causalidade exige contrato/prova mais forte.

---

# 10. TEMPO E GEOGRAFIA

## INT-LAW-100 — Herda semântica madura

```text
SOURCE_LOCATION != FACT_LOCATION
FACT_TIME != PUBLICATION_TIME != OBSERVED_TIME != COLLECTED_TIME
```

Intelligence consome essas distinções; não as achata.

## INT-LAW-101 — Escopo da página ≠ local do fato

## INT-LAW-102 — Afiliação ≠ local do estudo

## INT-LAW-103 — Tempo participa da acionabilidade

Fato pode continuar verdadeiro e perder utilidade operacional.

## INT-LAW-104 — ACT_NOW exige janela compatível

Sem janela factual suficiente:

```text
ACT_NOW = NOT_PROVED
```

## INT-LAW-105 — Estado temporal explica motivo

Taxonomia final deve ser contratada antes do runtime. Estados candidatos:

```text
ACT_NOW
PLAN_NEXT_CYCLE
MONITOR
STALE_FOR_ACTION
UNKNOWN_WINDOW
```

---

# 11. UNIVERSOS, COMPLETUDE, ZERO E AUSÊNCIA

## INT-LAW-110 — Universo é definido pela pergunta

```text
UNIVERSE != DIRECTORY
```

## INT-LAW-111 — Completude exige contrato de universo

Para afirmar `COMPLETE`, `FULL_SCAN`, `ZERO` ou ausência forte:

```text
WHICH_UNIVERSE
UNIVERSE_OWNER
INCLUSION_RULE
EXPECTED_EXTENT
SCANNED_EXTENT
EXPECTED_FINGERPRINT
SCANNED_FINGERPRINT
COMPLETENESS_STATE
```

## INT-LAW-112 — ZERO_PROVED é estado exigente

Distinguir:

```text
ZERO_PROVED
NOT_FOUND_IN_SCANNED_UNIVERSE
UNIVERSE_INCOMPLETE
NOT_QUERIED
MATERIAL_NOT_USABLE
UNKNOWN
```

## INT-LAW-113 — Input vazio nunca prova completude

Gate crítico que passa vazio é inválido.

## INT-LAW-114 — Reprodutibilidade ≠ universo correto

Dois leitores concordarem prova reprodutibilidade da leitura, não decisão do universo.

---

# 12. INCERTEZA, JULGMENT E ALTERNATIVAS

## INT-LAW-120 — Informação upstream, premissa e julgamento ficam separados

```text
COLLECTION_CLAIM / FACT
ANALYTIC_ASSUMPTION
ANALYTIC_JUDGMENT
```

## INT-LAW-121 — Major judgment explica incerteza

Registrar, quando material:

- quantidade/qualidade de evidência;
- freshness;
- gaps;
- dependência de premissas;
- conflitos.

## INT-LAW-122 — Confidence ≠ probability

Confiança na base do judgment e probabilidade de evento são conceitos diferentes.

## INT-LAW-123 — Evidência contrária fica visível

Não descartar porque reduz score.

## INT-LAW-124 — Alto impacto + alta incerteza exige alternativas

Produzir hipóteses alternativas e indicadores que mudariam o judgment quando risco justificar.

## INT-LAW-125 — Mudança de judgment é explicada

```text
PREVIOUS_JUDGMENT
NEW_JUDGMENT
WHAT_CHANGED
WHY
NEW_EVIDENCE_OR_REASONING
```

## INT-LAW-126 — Judgment não faz advocacy

Não moldar conclusão para confirmar expectativa comercial, política ou de audiência.

---

# 13. FUTURO / HORIZON SCANNING

## INT-LAW-130 — WEAK_SIGNAL ≠ FORECAST

## INT-LAW-131 — FORECAST ≠ FACT

## INT-LAW-132 — SCENARIO ≠ PREDICTION

## INT-LAW-133 — FUTURE_DATE ≠ OPPORTUNITY

Calendário, expiry, safra ou janela futura isolados não criam Opportunity.

## INT-LAW-134 — Radar Futuro consulta corpus relevante

Mesma disciplina de consulta global e estados explícitos por família.

## INT-LAW-135 — Horizon item declara incerteza e horizonte

No mínimo:

- sinal observado;
- evidência;
- horizonte;
- impacto potencial;
- causas/grau de incerteza;
- indicadores que fortaleceriam/enfraqueceriam.

## INT-LAW-136 — História não prova repetição

Pattern histórico informa hipótese, não determina futuro.

---

# 14. FINDING, ATTENTION ITEM E OPPORTUNITY

## INT-LAW-140 — Finding responde pergunta analítica

Não existe finding genérico “interessante”.

## INT-LAW-141 — Relevância para decisão é explícita

Dizer para quem/qual decisão importa, sem fabricar ação.

## INT-LAW-142 — Opportunity consulta famílias aplicáveis

Preservar contrato vigente de estados, atualmente:

```text
MATCH
CROP_ONLY
NOT_FOUND
UNKNOWN
MATERIAL_EXISTENTE_NAO_UTILIZAVEL
```

Mudança de taxonomia exige contrato, não implementação silenciosa.

## INT-LAW-143 — Portfolio completeness quando aplicável

Opportunity comercial ligada à ADAMA deve contabilizar o portfólio do país/cultura conforme contrato vigente.

## INT-LAW-144 — Produto para cultura ≠ produto para alvo

Não chamar solução sem relação cultura × alvo provada.

## INT-LAW-145 — Estrutura não inventa pressão de campo

Autorização/portfolio/label contextualizam; não criam sinal de campo/demanda.

## INT-LAW-146 — DAILY_COLLECTION_VALUE ≠ DAILY_INTELLIGENCE_VALUE

Cadência da Collection não determina cadência de Intelligence.

---

# 15. COLLECTION GAP

## INT-LAW-150 — Gap é first-class

Declarar:

```text
QUESTION_BLOCKED
MISSING_FACT_OR_KEY
WHY_EXISTING_MATERIAL_IS_INSUFFICIENT
REQUIRED_SCOPE
URGENCY
```

## INT-LAW-151 — Intelligence pede prova, não escolhe rota de coleta

Collector/route pertencem à Collection.

## INT-LAW-152 — Reprocessar antes de recolher quando aplicável

Se informação pode existir no material preservado e falta extração/estrutura, avaliar reprocessamento antes de nova aquisição.

## INT-LAW-153 — Collection Gap ≠ Collection failure

Pergunta nova pode pedir dado fora do universo anterior.

---

# 16. IA / LLM NA INTELLIGENCE

## INT-LAW-160 — LLM é mecanismo, não fonte factual

Output de modelo aponta para claim/evidência upstream ou permanece hipótese/síntese.

## INT-LAW-161 — Conteúdo coletado é dado não confiável, não instrução

Web/PDF/comment/transcript pode conter instruções adversariais ou irrelevantes. Conteúdo de fonte não autoriza mudar ferramentas, políticas, segredos, escopo ou permissões.

## INT-LAW-162 — Model/prompt/policy version entram no lineage quando materiais

Mesmo input com modelo/prompt diferente pode produzir comportamento diferente.

## INT-LAW-163 — Saída de IA é distinguível de source evidence

Paráfrase/inferência não aparece como citação/fato bruto.

## INT-LAW-164 — IA deve poder recusar promoção

```text
UNKNOWN
INSUFFICIENT_EVIDENCE
CONFLICTING_EVIDENCE
NEEDS_REVIEW
```

são resultados válidos.

## INT-LAW-165 — Chain-of-thought privado não é dependência de auditoria

Guardar decision trace compartilhável, não raciocínio privado do modelo.

## INT-LAW-166 — Evals antes de confiança

Função material de IA precisa de positivos, negativos, contraditórios e adversariais.

## INT-LAW-167 — Model change exige regressão

Trocar provider/model/version sem regressão é mudança não medida.

---

# 17. HUMAN REVIEW E AUTONOMIA

## INT-LAW-170 — Autonomia é granular

Permissões separáveis para:

```text
READ
EXTRACT
CLASSIFY
PROPOSE_HYPOTHESIS
GENERATE_CANDIDATE_FINDING
PROMOTE_FINDING
PROPOSE_RECOMMENDATION
EXECUTE_ACTION
```

## INT-LAW-171 — Risco aumenta profundidade de revisão

Alto impacto, baixa confiança, novidade ou complexidade exigem review maior.

## INT-LAW-172 — Human approval não transforma base fraca em fato

Approval não apaga gaps/provenance.

## INT-LAW-173 — Challenge path independente

Findings importantes precisam de contestação/reviewer não dependente do mesmo produtor.

---

# 18. SEGURANÇA

## INT-LAW-180 — Security-by-design

Segurança entra em arquitetura, implementação, testes, deploy e operação.

## INT-LAW-181 — Least privilege

Intelligence recebe somente capacidades necessárias.

## INT-LAW-182 — AUTHENTICATION ≠ AUTHORIZATION

Identidade válida não implica acesso ao recurso/ação.

## INT-LAW-183 — READ ≠ DERIVE ≠ WRITE ≠ ACT

Capacidades separáveis e auditáveis.

## INT-LAW-184 — Default V1 é read/derive-first

Writes operacionais externos não fazem parte do baseline.

## INT-LAW-185 — Secrets ficam fora de prompt/repo/log

Usar secret management apropriado.

## INT-LAW-186 — Dados sensíveis seguem minimização e propósito

Só usar o necessário à pergunta autorizada.

## INT-LAW-187 — Provedor externo não recebe dados automaticamente

API/modelo externo exige política de dados compatível.

## INT-LAW-188 — Dependências são superfície de risco

Bibliotecas, modelos, connectors e APIs entram em inventário e processo de atualização/vulnerabilidade proporcional.

## INT-LAW-189 — Ações e promoções relevantes são auditáveis

Mudança de regra, promoção de finding, permissão e ação futura deixam trilha.

## INT-LAW-190 — Production não é laboratório

Mudança estrutural passa por ambiente apropriado, prova e preparação antes de LIVE.

---

# 19. QUALIDADE E OBSERVABILIDADE

## INT-LAW-200 — Qualidade é contínua

Monitorar quando mensurável:

```text
FRESHNESS
COMPLETENESS
CONTRACT / SCHEMA DRIFT
LINEAGE GAPS
FAMILY CONSULTATION GAPS
STATE DISTRIBUTION ANOMALIES
MODEL BEHAVIOR DRIFT
COST / LATENCY quando relevante
```

## INT-LAW-201 — Incidente não vira silêncio

Falha de qualidade produz estado explícito; não simplesmente remove item.

## INT-LAW-202 — Freshness é contextual

“Velho” depende da pergunta/janela, não de um número universal de dias.

## INT-LAW-203 — SYSTEM HEALTH ≠ ANALYTIC TRUTH

Pipeline saudável não prova finding correto.

---

# 20. HISTÓRIA, CORREÇÃO E FEEDBACK

## INT-LAW-210 — Histórico append-only por default

Correção não apaga estado anterior.

## INT-LAW-211 — ACTIVE_STATE pode mudar sem apagar HISTORICAL_STATE

## INT-LAW-212 — Correção registra causa

Distinguir erro de fonte, normalização, lógica, modelo, input ou interpretação.

## INT-LAW-213 — Outcome posterior não reescreve julgamento passado

Serve para calibrar futuras análises.

## INT-LAW-214 — Calibração usa ground truth legítimo

Não calibrar contra proxy que mede outra pergunta.

---

# 21. REPROCESSAMENTO E MUDANÇA

## INT-LAW-220 — New data e new logic são causas diferentes de recomputação

## INT-LAW-221 — Impact analysis antes de mudança estrutural

## INT-LAW-222 — Reprocessamento preserva origem Collection

Novo output analítico não muda identidade/proveniência upstream.

## INT-LAW-223 — Gap pode fechar por reprocessamento

Verificar antes de coletar de novo.

## INT-LAW-224 — Mudança semântica exige reconciliação/migration explícita

Renomear conceito/estado pode quebrar histórico sem alterar bytes.

---

# 22. SYSTEM MAP E CARDS

## INT-LAW-230 — System Map observa Intelligence

```text
SYSTEM_MAP != INTELLIGENCE_AUTHORITY
```

## INT-LAW-231 — CARD != FILE

Card representa responsabilidade/conceito.

## INT-LAW-232 — DECLARED ≠ OBSERVED

Capability declarada sem runtime não aparece como provada.

## INT-LAW-233 — Relações analíticas têm semântica própria

Conforme contratos futuros:

```text
SUPPORTS
CONTRADICTS
DERIVED_FROM
DEPENDS_ON
CROSSES_WITH
PROMOTES_TO
VALIDATES
```

Não comprimir em DATA/CONTROL.

## INT-LAW-234 — Navegação vertical chega à prova

Quando implementado:

```text
BIBLE / LAW
→ CONTRACT
→ COMPONENT
→ CODE
→ RUN
→ INPUT CLAIM/EVIDENCE
→ OUTPUT JUDGMENT
→ TEST / PROOF
```

Elo ausente = UNKNOWN.

---

# 23. INTELLIGENCE TOOLS / DELIVERY

## INT-LAW-240 — Tool consome Intelligence; não inventa Intelligence

## INT-LAW-241 — Tool exige pergunta + usuário + valor

“Temos dados” não justifica ferramenta.

## INT-LAW-242 — Capability pode não virar tool

Guardrails e mecanismos internos podem permanecer internos.

## INT-LAW-243 — Ask Sintonia não recebe bypass epistemológico

Interface conversacional segue os mesmos gates, provenance e estados.

## INT-LAW-244 — Explicabilidade mínima acompanha saída

Consumidor deve descobrir:

- por que apareceu;
- quais fatos sustentam;
- o que contradiz;
- o que é incerto;
- janela/escopo;
- o que mudaria o judgment.

---

# 24. AVALIAÇÃO

## INT-LAW-250 — “Parece bom” não é eval

## INT-LAW-251 — Métricas candidatas

Quando mensuráveis:

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

## INT-LAW-252 — Métrica inexistente = NOT_MEASURED

## INT-LAW-253 — Golden cases não bastam

Incluir negative/adversarial fixtures.

## INT-LAW-254 — Fixtures históricos precisam ser re-medidos

Números antigos não viram baseline atual sem reprodução.

---

# 25. RED TEAM MÍNIMO

Implementação material deve sobreviver, conforme aplicável:

```text
RT-INT-01  duplicar evidência em famílias diferentes para inflar convergência
RT-INT-02  usar sidebar/menu como corpo
RT-INT-03  SOURCE_LOCATION → FACT_LOCATION
RT-INT-04  PUBLICATION_TIME → FACT_TIME
RT-INT-05  NOT_FOUND → ZERO_PROVED sem universo
RT-INT-06  fato antigo → ACT_NOW
RT-INT-07  identidade → expertise
RT-INT-08  catálogo/registro → sinal independente
RT-INT-09  família existente mas não consultada → gate PASS
RT-INT-10  ocultar evidence contrária
RT-INT-11  output LLM sem support edge → fato/judgment provado
RT-INT-12  modelo/prompt mudou → reuso silencioso
RT-INT-13  read/analyze → write/action
RT-INT-14  correção → apagar histórico
RT-INT-15  data futura → forecast/opportunity
RT-INT-16  crossing sem join key factual
RT-INT-17  input vazio → PASS
RT-INT-18  validações dependentes → independência alta
RT-INT-19  cópias da mesma origem → múltiplas confirmações
RT-INT-20  finding sem reproduzir inputs + lógica + gates
RT-INT-21  portal reconstrói relação ausente
RT-INT-22  Collection Gap chama collector direto
RT-INT-23  UNKNOWN some na Delivery
RT-INT-24  geografia/tempo incompatível → opportunity
RT-INT-25  Intelligence fabrica CLAIM_ID upstream para destravar análise
```

Ataque só conta se atingiu alvo e teardown restaurou estado.

## 25.1 · ATAQUES DA FERRAMENTA (V0.3)

Alvo: a fronteira da secção 35.

```text
RT-TOOL-01  Delivery reconstrói um finding que a Intelligence não produziu
RT-TOOL-02  tool preenche UNKNOWN com valor por defeito, vazio ou placeholder
RT-TOOL-03  tool lê família de dados que nenhum INTELLIGENCE_RUN consultou
RT-TOOL-04  science/market/competitor implementam a MESMA lógica em três sítios
RT-TOOL-05  tool promove SIGNAL a FINDING, ou FINDING a OPPORTUNITY, ao renderizar
RT-TOOL-06  tool infere FACT_TIME/FACT_LOCATION que o objeto não trazia
RT-TOOL-07  filtro da tool muda o universo e o número continua a dizer-se completo
```

## 25.2 · ATAQUES DA PERFORMANCE DE FONTE (V0.3)

Alvo: a fronteira da secção 36.

```text
RT-SRC-01  fonte de muito volume domina o perfil sem produzir Intelligence útil
RT-SRC-02  fonte pequena e crítica desaparece do perfil por amostra pequena
RT-SRC-03  fonte nova nunca é amostrada, e a ausência de prova vira prova de ausência
RT-SRC-04  republicação da mesma origem conta como contribuição independente
RT-SRC-05  evidência contrária reduz a contribuição da fonte que a trouxe
RT-SRC-06  o mesmo item conta contribuição em três capacidades diferentes
RT-SRC-07  item sem lineage recebe crédito por ter estado no mesmo RUN
RT-SRC-08  fonte forte em regulatório é tratada como forte em tudo
RT-SRC-09  histórico antigo congela o perfil e ignora mudança na fonte
RT-SRC-10  Intelligence chama o collector diretamente
RT-SRC-11  Intelligence escreve no source registry ou inventa SOURCE_ID
RT-SRC-12  Collection passa a obedecer a um número único, sem contexto
RT-SRC-13  o conselho da Intelligence é lido como ordem e altera agenda sozinho
RT-SRC-14  fonte obrigatória perde vez por publicar pouco
```

Cada um destes catorze tem uma lei que o barra, e a secção 36 nomeia qual.
**Ataque sem lei que o barre é backlog, não red team.**

---

# 26. GATES DE UMA FUTURA INTELLIGENCE V1

Antes de:

```text
INTELLIGENCE_V1_READY = YES
```

exigir contratos/provas equivalentes a:

```text
WAITING_ROOM_INPUT_BOUNDARY          = PASS
UPSTREAM_CLAIM_IDENTITY              = PASS
INTELLIGENCE_RUN_IDENTITY            = PASS
PROVENANCE_LINEAGE                   = PASS
DEPENDENCY_GRAPH                     = PASS
INDEPENDENCE_ACCOUNTING              = PASS
TIME_SEMANTICS                       = PASS
GEOGRAPHY_SEMANTICS                  = PASS
UNIVERSE_COMPLETENESS                = PASS onde exigido
UNKNOWN_PRESERVATION                 = PASS
CONTRARY_EVIDENCE_HANDLING           = PASS
JUDGMENT_HISTORY                     = PASS
COLLECTION_GAP_CANONICAL_ROUTE       = PASS
LLM_OUTPUT_GUARD                     = PASS se LLM usado
SECURITY_BOUNDARY                    = PASS
RED_TEAM                             = PASS
REGRESSION                           = PASS
SYSTEM_MAP                           = PASS
```

## INT-LAW-260 — Gate crítico precisa saber falhar

Provar falhas com input vazio, missing input, duplicate identity, missing provenance, contradictory state, hidden UNKNOWN, universe mismatch, dependency inflation, stale actionability e unauthorized capability.

---

# 27. DEFINIÇÃO DE INTELLIGENCE V1 PRONTA

Intelligence V1 pode ser considerada pronta quando, para perguntas aprovadas e escopo declarado, consegue repetivelmente:

1. receber apenas material READY da Sala de Espera;
2. abrir `INTELLIGENCE_RUN` identificável;
3. consumir claims/fatos upstream sem fabricar identidade;
4. construir support/contradiction + lineage;
5. distinguir dependência/independência;
6. executar crossings com chaves provadas;
7. preservar tempo/geografia/proveniência;
8. produzir signal/finding/opportunity ou recusa epistemológica;
9. declarar incerteza, premissas e evidência contrária quando material;
10. detectar Collection Gap e voltar pela Collection canônica;
11. preservar história/reprocessamento;
12. passar red team e regressão;
13. expor resultados sem Delivery reconstruir verdade;
14. operar com controles de segurança/auditoria proporcionais.

Pronta não significa prever tudo nem encontrar oportunidade todos os dias.

---

# 28. PROIBIÇÕES ABSOLUTAS

```text
INTELLIGENCE MUST NOT COLLECT DIRECTLY.
INTELLIGENCE MUST NOT FABRICATE COLLECTION CLAIM/FACT IDENTITY.
INTELLIGENCE MUST NOT FABRICATE SOURCE_ID OR DOCUMENT_ID.
INTELLIGENCE MUST NOT TURN UNKNOWN INTO FACT.
INTELLIGENCE MUST NOT TURN NOT_FOUND INTO ZERO WITHOUT DECLARED UNIVERSE.
INTELLIGENCE MUST NOT COUNT DEPENDENT EVIDENCE AS INDEPENDENT.
INTELLIGENCE MUST NOT TURN STRUCTURAL VALIDATION INTO FIELD SIGNAL.
INTELLIGENCE MUST NOT TURN FUTURE DATE INTO FORECAST.
INTELLIGENCE MUST NOT TURN FORECAST INTO FACT.
INTELLIGENCE MUST NOT TURN IDENTITY INTO EXPERTISE.
INTELLIGENCE MUST NOT TURN TRUE-BUT-STALE INTO ACT_NOW.
INTELLIGENCE MUST NOT HIDE CONTRARY EVIDENCE.
INTELLIGENCE MUST NOT USE LLM AS FACTUAL SOURCE.
INTELLIGENCE MUST NOT GRANT WRITE/ACTION BECAUSE READ/ANALYZE WAS GRANTED.
INTELLIGENCE MUST NOT LET PORTAL REBUILD ITS TRUTH.
INTELLIGENCE MUST NOT PASS A CRITICAL GATE ON EMPTY INPUT.
INTELLIGENCE MUST NOT REWRITE HISTORY SILENTLY.
```

Acrescentadas em V0.3, e todas da mesma família — a Intelligence **mede** a
coleta, e não manda nela:

```text
INTELLIGENCE MUST NOT CALL A COLLECTOR.
INTELLIGENCE MUST NOT WRITE TO THE SOURCE REGISTRY.
INTELLIGENCE MUST NOT CHANGE A COLLECTION SCHEDULE OR QUOTA.
INTELLIGENCE MUST NOT CREDIT A SOURCE WITHOUT LINEAGE.
INTELLIGENCE MUST NOT REDUCE A SOURCE PROFILE FOR CONTRARY EVIDENCE.
INTELLIGENCE MUST NOT COLLAPSE SOURCE CONTRIBUTION INTO ONE GLOBAL NUMBER.
INTELLIGENCE MUST NOT LET A TOOL PROMOTE AN ANALYTIC OBJECT.
```

---

# 29. ORIGEM DAS LEIS V0.2

## Interno

- `BIBLIA-CANONICA-DA-COLETA.md` V1.4 — owner upstream e fronteira factual;
- `docs/refresh/FINAL-INTELLIGENCE-REFRESH-EAME.md` — dependência, falsas convergências, contexto, tempo, gaps;
- `docs/red-team/C-SNAPSHOT-DE-INTELIGENCIA-EAME.md` — assimetrias, limites de fontes e leituras falsas;
- `docs/intelligence/MOTOR-INTELLIGENCE-V2-REQUIREMENTS.md` — requisitos futuros maduros;
- Know-how e leis transversais do SINTONIA.

## Benchmark externo

- Databricks Unity Catalog — governance, lineage, quality;
- Palantir Foundry/Ontology — data + logic + action + security, decision lineage;
- OpenLineage — Run/Job/Dataset e lineage explícito;
- W3C PROV-O — provenance interoperável;
- OpenMetadata — lineage, quality, incidents, observability;
- Dagster/dbt — assets/state, observability, testability;
- ODNI ICD 203 — analytic standards;
- CIA Structured Analytic Techniques — structured analysis;
- UK Government Office for Science Futures Toolkit — horizon scanning;
- NIST AI RMF / GenAI Profile — AI risk lifecycle;
- NIST SSDF — secure SDLC;
- NIST Zero Trust — no implicit trust.

Detalhes e URLs:

`research/intelligence/BENCHMARK-DE-ENGENHARIA-DA-INTELLIGENCE-2026-09-13.md`

Benchmark informa; não governa.

## Benchmark externo acrescentado em V0.3

Quatro, e entraram porque nenhum documento desta casa os mencionava — medido
antes de pesquisar, com `grep`, em `research/intelligence/` e
`docs/intelligence/`: `MLflow` 0 ficheiros, `LangSmith` 0, `crawl` 0,
`exploration`/`exploitation` 0.

- **MLflow GenAI Evaluation / Tracing** — trace, scorer/judge, evaluation
  dataset, avaliação offline × monitorização em produção, dataset construído a
  partir de traces reais;
- **LangSmith Evaluation / Observability** — as quatro espécies de avaliador
  (humano · determinístico · LLM-as-judge · pairwise), reference-free ×
  reference-based, annotation queue, e o aviso de que o LLM-as-judge precisa de
  ser ele próprio validado;
- **Palantir AIP Evals** — evaluation suite, test case, evaluation function
  como grader sobre função-alvo;
- **Microsoft Research — Web Crawl Scheduling** (SIGIR 2019 · NeurIPS 2019 ·
  ICML 2020) — *partial change observability*, importância × taxa de mudança
  como dois eixos separados, restrições de politeness/largura de banda, e o
  compromisso exploração × exploração-do-conhecido declarado como tal.

Detalhes, transferências e recusas:

`research/intelligence/BENCHMARK-INTELLIGENCE-ENGINEERING-DELTA-2026-09-14.md`

O de 2026-09-13 não foi reescrito. É uma fotografia datada, e nesta casa
fotografia datada sucede-se, não se corrige.

---

# 30. RELAÇÃO COM MOTOR INTELLIGENCE V2

`docs/intelligence/MOTOR-INTELLIGENCE-V2-REQUIREMENTS.md` contém requisitos maduros e não deve ser apagado.

Mas, após promoção desta Bíblia, não podem existir dois owners da mesma lei.

Estratégia de reconciliação a decidir:

```text
BIBLE = CONSTITUTION / PRINCIPLES / BOUNDARIES
MOTOR-V2-REQUIREMENTS = SUBORDINATE IMPLEMENTATION CONTRACT
```

Qualquer requisito do Motor V2 que contradiga a Bíblia deve ser resolvido explicitamente antes de implementação.

---

# 31. PROMOÇÃO PARA CANONICAL

V0.2 só muda de:

```text
CANDIDATE_FOR_CANONICAL_REVIEW
```

para:

```text
CANONICAL
```

após:

1. reconciliação completa com Collection Bible vigente;
2. reconciliação com Motor V2 e contratos existentes;
3. owner collision count = 0;
4. registro no Control Plane/Sala de Controle;
5. integração em snapshot onde a autoridade não fique invisível numa branch lateral;
6. governance gate;
7. System Map atualizado pela cadeia canônica, nunca por edição manual de gerados;
8. Know-how delta aplicado ao owner canônico;
9. aprovação explícita da promoção.

As nove foram medidas em `C-CTRL-INT-NIGHT-02`, contra esta árvore:

```text
INTELLIGENCE_BIBLE_STATUS = CANONICAL
BIBLE_PROMOTION_GATES     = 9 / 9 PASS
PROMOTED_AT               = 2026-09-14
```

A condição 5 — «integração em snapshot onde a autoridade não fique invisível
numa branch lateral» — foi a última a fechar, e fechou porque esta Bíblia, a
Bíblia da Coleta, o know-how canônico, a arbitragem e o registo passaram a
coexistir num commit só. A condição 6 fechou quando se descobriu que os dois
defeitos que a mantinham aberta não existiam: dez menções contadas como leis, e
um `CARD_ID` lido como caminho de ficheiro.

> **Promoção não é implementação.** O que esta linha muda é quem é a lei — não
> o que já está construído. `INTELLIGENCE_RUNTIME_IMPLEMENTED` continua a ser
> medido, nunca declarado.

---

# 32. PRIMEIRA MISSÃO APÓS PROMOÇÃO — NÃO EXECUTAR AGORA

Pergunta mínima:

> Qual é o contrato mínimo de entrada/saída e identidade de um `INTELLIGENCE_RUN` consumindo **um claim/fato real e admitido** da Sala de Espera, sem produzir Opportunity ainda?

Gate:

```text
ONE REAL WAITING_ROOM ITEM
→ UPSTREAM CLAIM/FACT IDENTITY PRESERVED
→ ONE IDENTIFIED INTELLIGENCE_RUN
→ PROVEN INPUT LINEAGE
→ NO DIRECT COLLECTION
→ NO ANALYTIC JUDGMENT FABRICATION
```

Depois HARD STOP.

> **«NÃO EXECUTAR AGORA» continua verdade — e já não pela razão original.**
> Escrito enquanto esta Bíblia era candidata, o «agora» queria dizer *antes da
> promoção*. A promoção aconteceu a 2026-09-14, e esta missão passou a ser a
> única autorizada. Continua a não poder correr, e agora por gates a montante
> que foram **medidos**, não presumidos:
>
> | gate | medido em 2026-09-14 |
> |---|---|
> | `TRAVA-DA-INTELIGENCIA.json` | `COLLECTION_FOUNDATION_CLOSED = NAO` — 0 de 12 classes de estrada com arquitetura fechada, e `ROUTE_CLASSES_REQUIRED_TOTAL` ainda `UNKNOWN` |
> | `ONE REAL WAITING_ROOM ITEM` (gate acima) | 0 itens — `data/samples/PRONTO-PARA-INTELIGENCIA/` não existe |
>
> Nenhum dos dois é desta Bíblia para abrir.

---

# 33. VEREDITO

Esta secção carrega **três fotografias**: a candidatura, a promoção e a revisão
V0.3. A diferença entre a primeira e a segunda é a promoção; entre a segunda e a
terceira, **só a lei** — nenhuma das medições de máquina mudou, e a terceira
diz isso letra a letra.
Elas nunca se fundem: a de baixo não corrige a de cima, sucede-a.

```text
ANTES != AGORA
```

## ⚠️ 33.1 · VEREDITO HISTÓRICO — V0.2 COMO CANDIDATA, 2026-09-13

> **Esta é a fotografia do dia em que a Bíblia foi escrita, antes da promoção.**
> Não é o estado de hoje, e não se reescreve: um veredito que muda depois de
> emitido deixa de poder ser conferido.

```text
VEREDITO = HISTORICO
DATA     = 2026-09-13
ENGINEERING_BIBLE_WRITTEN = YES
COLLECTION_OWNER_COLLISION_FOUND = YES
COLLECTION_OWNER_COLLISION_CORRECTED_IN_CANDIDATE = YES
CANONICAL = NO
RUNTIME_IMPLEMENTED = NO
COLLECTION_CHANGED = NO
INTELLIGENCE_IMPLEMENTATION_STARTED = NO
PORTAL_CHANGED = NO
LIVE_CHANGED = NO
KNOW_HOW_DELTA = ATUALIZACAO NECESSARIA APOS PROMOCAO/INTEGRACAO
```

Duas linhas desta fotografia deixaram de descrever o presente, e é por isso que
ela está marcada: `CANONICAL = NO` foi substituído pela promoção de 2026-09-14, e
o `KNOW_HOW_DELTA` que ela pedia foi aplicado — vive em `SINTONIA-EAME-KNOW-HOW.md`,
§116. As outras sete continuam verdade, e continuam medidas abaixo.

## ⚠️ 33.2 · VEREDITO HISTÓRICO — V0.2 PROMOVIDA, 2026-09-14

> **Esta é a fotografia da promoção.** Foi corrente até à revisão V0.3, do mesmo
> dia, e deixou de o ser por uma razão só: a lei ganhou quatro secções. **Nenhuma
> das dez linhas abaixo mudou de valor** — e é precisamente por isso que ela fica
> aqui inteira, em vez de ser reescrita. Quem quiser conferir que a V0.3 não
> comprou autorização nenhuma compara-a com a 33.3, linha a linha.

```text
VEREDITO = HISTORICO
DATA     = 2026-09-14
BIBLE_STATUS = CANONICAL
BIBLE_PROMOTION_GATES = 9 / 9 PASS
IMPLEMENTATION_AUTHORIZED = SOMENTE_A_PRIMEIRA_MISSAO_DA_SECAO_32_E_SUJEITA_AOS_GATES_UPSTREAM
INTELLIGENCE_RUNTIME_IMPLEMENTED = NO
INTELLIGENCE_IMPLEMENTATION_STARTED = NO
REAL_ITALY_FLOW_OBSERVED = NO
COLLECTION_FOUNDATION_CLOSED = NAO
COLLECTION_CHANGED = NO
PORTAL_CHANGED = NO
LIVE_CHANGED = NO
KNOW_HOW_DELTA = APLICADO · SINTONIA-EAME-KNOW-HOW.md §116
```

**As cinco primeiras linhas são verdade ao mesmo tempo, e isso não é
contradição nenhuma.** Ser lei e estar construído são perguntas diferentes:

| linha | a pergunta a que ela responde |
|---|---|
| `BIBLE_STATUS` | quem manda na Intelligence |
| `INTELLIGENCE_RUNTIME_IMPLEMENTED` | o que existe construído |
| `IMPLEMENTATION_AUTHORIZED` | o que se pode começar a construir |
| `REAL_ITALY_FLOW_OBSERVED` | o que já se viu correr sobre dado real |

Uma constituição recém promovida governa código que ainda não existe. É o estado
normal de uma lei nova — e confundir `CANONICAL = YES` com
`RUNTIME_IMPLEMENTED = YES` seria a forma mais rápida de esta Bíblia passar a
mentir.

## 33.3 · VEREDITO CORRENTE — V0.3, 2026-09-14

```text
VEREDITO = CORRENTE
DATA     = 2026-09-14
BIBLE_STATUS = CANONICAL
BIBLE_VERSION_BEFORE = V0.2
BIBLE_VERSION_AFTER  = V0.3
BIBLE_PROMOTION_GATES = 9 / 9 PASS
IMPLEMENTATION_AUTHORIZED = SOMENTE_A_PRIMEIRA_MISSAO_DA_SECAO_32_E_SUJEITA_AOS_GATES_UPSTREAM
SECOES_ACRESCENTADAS = 34 · 35 · 36 · 37
LEIS_ACRESCENTADAS = 21   (270..273 · 280..284 · 290..299 · 300..301)
LEIS_TOTAL = 172          (era 151)
LEIS_ALTERADAS = 0        (000..260 intactas, letra a letra)
LEIS_COM_ID_DUPLICADO = 0
LEIS_RECUSADAS_POR_JA_TEREM_DONO = 4
INTELLIGENCE_RUNTIME_IMPLEMENTED = NO
INTELLIGENCE_IMPLEMENTATION_STARTED = NO
SOURCE_PERFORMANCE_IMPLEMENTED = NO
REAL_ITALY_FLOW_OBSERVED = NO
COLLECTION_FOUNDATION_CLOSED = NAO
COLLECTION_CHANGED = NO
COLLECTION_SCHEDULE_CHANGED = NO
SOURCE_REGISTRY_CHANGED = NO
PORTAL_CHANGED = NO
MENU_CHANGED = NO
LIVE_CHANGED = NO
MIGRATION_CREATED = NO
KNOW_HOW_DELTA = ENTREGUE COMO DELTA · handoff/KNOW-HOW-DELTA-SOURCE-PERFORMANCE.md
```

**As quatro linhas que interessam a quem desconfia desta revisão.**
`LEIS_ALTERADAS = 0` diz que nada do que já valia foi mexido.
`IMPLEMENTATION_AUTHORIZED` é a mesma cadeia de caracteres da V0.2 — copiada, não
reescrita. `SOURCE_PERFORMANCE_IMPLEMENTED = NO` diz que a secção 36 descreve um
contrato e não um programa. E `COLLECTION_SCHEDULE_CHANGED = NO` diz que
**nenhuma coleta real mudou de prioridade por causa deste ficheiro**.

`LEIS_RECUSADAS_POR_JA_TEREM_DONO = 4` é a linha de que mais me orgulho, e a
razão está na INT-LAW-000: quatro leis que o enunciado mandou avaliar **não**
foram escritas, porque já existiam com outro nome. Escrevê-las teria dado uma
Bíblia mais gorda e uma casa com dois donos para a mesma regra. Estão nomeadas
na secção 37.4, com a lei que já as cobria.

A Intelligence do SINTONIA deve ser uma **máquina de produção analítica auditável**.

Ela precisa provar:

```text
O QUE SABE
QUAL CLAIM/FACT UPSTREAM SUSTENTA
POR QUE O JUDGMENT É DEFENSÁVEL
DE ONDE VEIO
O QUE DEPENDE DA MESMA ORIGEM
O QUE É PREMISSA
O QUE É INCERTO
O QUE CONTRADIZ
QUAL É A JANELA
QUAL É O ESCOPO
O QUE MUDARIA O JUDGMENT
E QUANDO A RESPOSTA CORRETA É NÃO AGIR AINDA
```

---

# 34. CAPACIDADES DE INTELLIGENCE

> Uma **capacidade** é uma pergunta de negócio que a Intelligence sabe responder
> com prova. Não é uma tela, não é uma tabela e não é uma pasta. As telas de hoje
> são evidência de que existe produto; **não são a lista das capacidades**, e a
> secção 35 explica porquê.

## INT-LAW-270 — CAPABILITY ≠ TOOL ≠ SURFACE

```text
CAPABILITY   a pergunta que sabemos responder com prova
TOOL         o instrumento que deixa alguém usar a resposta
SURFACE      o sítio onde ela aparece
```

Os três contam-se em separado. Uma capacidade pode existir sem tool
(`INT-LAW-242`), e **uma surface pode existir sem capacidade nenhuma por trás** —
que é o caso medido hoje, e está na secção 35.2.

## INT-LAW-271 — TOOL EXISTS ≠ INTELLIGENCE EXISTS

A existência de um card, de uma rota, de um menu ou de um ecrã **não é prova** de
que a capacidade correspondente existe.

```text
CARD RENDERIZA != PERGUNTA RESPONDIDA
FIXTURE NO ECRA != FACTO NO ECRA
```

Prova de capacidade é um `INTELLIGENCE_RUN` com lineage, não um screenshot.

## INT-LAW-272 — Toda capacidade declara o contrato abaixo, inteiro

Uma capacidade sem `HARD_GATES` declarados é um desejo. Sem
`REQUIRED_JOIN_KEYS`, é um crossing por semelhança (`INT-LAW-037`). Sem
`MUST_NOT_DO`, é uma licença aberta.

```text
CAPABILITY_ID
PURPOSE
BUSINESS_QUESTION
INPUT_ANALYTIC_OBJECTS
OUTPUT_ANALYTIC_OBJECTS
REQUIRED_DATA_FAMILIES
REQUIRED_JOIN_KEYS
HARD_GATES
UNCERTAINTY_REQUIREMENTS
LINEAGE_REQUIREMENTS
CAN_FEED
MUST_NOT_DO
```

Os objetos de `INPUT`/`OUTPUT` saem do vocabulário fechado da `INT-LAW-030`.
**Nenhuma capacidade inventa um objeto novo.**

## INT-LAW-273 — A cadeia epistemológica não se salta

```text
FACT  →  SIGNAL  →  FINDING  →  OPPORTUNITY
```

Cada seta é uma promoção, e cada promoção tem gate próprio (`INT-LAW-036`). Uma
capacidade declara **onde entra e onde sai**, e não pode entregar na saída um
degrau que não conquistou.

E a cadeia ortogonal, que nenhuma capacidade pode comprimir (`INT-LAW-013`):

```text
TRUE  ≠  RELEVANT  ≠  ACTIONABLE
```

## 34.1 · AS NOVE CAPACIDADES

Nove, e não «as do menu»: duas do menu não são capacidades, e uma capacidade
necessária **não tem menu nenhum**. A conta está em 35.2.

---

### `CAP-OPP` · OPPORTUNITY INTELLIGENCE

```text
PURPOSE            decidir quando uma convergencia merece investigacao humana
BUSINESS_QUESTION  o que mudou que justifica a ADAMA olhar para isto agora,
                   nesta cultura, nesta regiao, nesta janela?
INPUT              ANALYTIC_SIGNAL · CROSSING · SUPPORT_EDGE ·
                   CONTRADICTION_EDGE · ANALYTIC_JUDGMENT
OUTPUT             OPPORTUNITY  |  NO_DEFENSIBLE_ACTION_YET
FAMILIAS           agronomica · regulatoria · comercial · campo · cientifica
JOIN_KEYS          CROP_ID x ISSUE_ID x REGION_ID x TIME_WINDOW
HARD_GATES         INT-LAW-142 familias aplicaveis consultadas
                   INT-LAW-077 independencia + compatibilidade
                   INT-LAW-104 janela compativel com ACT_NOW
                   INT-LAW-091 sem join key factual, nao ha crossing
INCERTEZA          nivel (A·B·C·D) e parte do OBJETO, nunca do texto
LINEAGE            COMPLETE exigido; PARTIAL desqualifica a promocao
CAN_FEED           delivery de oportunidade · SOURCE_ANALYTIC_CONTRIBUTION
MUST_NOT_DO        promover sem janela · fabricar pressao de campo a partir de
                   estrutura (INT-LAW-145) · esconder evidencia contraria
```

> `NO_DEFENSIBLE_ACTION_YET` é saída de primeira classe aqui, e não uma falha
> (`INT-LAW-012`). Um dia sem oportunidade é um resultado.

---

### `CAP-PORT` · PORTFOLIO INTELLIGENCE

```text
PURPOSE            saber o que a ADAMA pode legalmente oferecer, onde e ate quando
BUSINESS_QUESTION  para esta cultura e este alvo, o que temos registado, com que
                   rotulo, com que restricao e com que prazo?
INPUT              COLLECTION_FACT (registo) · CROSSING
OUTPUT             ANALYTIC_JUDGMENT sobre cobertura e lacuna de portfolio
FAMILIAS           regulatoria · rotulo · comercial
JOIN_KEYS          PRODUCT_ID x CROP_ID x TARGET_ID x REGISTRATION_VERSION x GEO
HARD_GATES         INT-LAW-143 completude quando aplicavel
                   INT-LAW-144 produto para cultura != produto para alvo
                   INT-LAW-067 registo != mercado
PRESERVA           product · crop · target · registration · label · restriction ·
                   expiry · geography — oito, e nenhum se deduz dos outros
INCERTEZA          disponibilidade comercial nasce NAO_SEI e so muda com prova
LINEAGE            versao do registo entra na chave, nao no rodape
CAN_FEED           CAP-OPP · CAP-LABEL · CAP-COMP
MUST_NOT_DO        tratar registado como disponivel · tratar catalogo como venda
```

---

### `CAP-FUT` · FUTURE / HORIZON INTELLIGENCE

```text
PURPOSE            ver cedo o que ainda nao e facto, sem o promover a facto
BUSINESS_QUESTION  o que esta a formar-se que muda a decisao dentro do horizonte
                   declarado — e com que forca?
INPUT              COLLECTION_FACT · ANALYTIC_SIGNAL · ANALYTIC_HYPOTHESIS
OUTPUT             FUTURE_SIGNAL com horizonte e incerteza declarados
FAMILIAS           regulatoria · cientifica · mercado · campo
JOIN_KEYS          ISSUE_ID x GEO x HORIZON_WINDOW
HARD_GATES         INT-LAW-130..133  weak signal != forecast != facto !=
                   oportunidade; data futura nao e nenhum dos quatro
                   INT-LAW-134 consultar corpus relevante
                   INT-LAW-136 historia nao prova repeticao
PRESERVA           signal · horizon · potential impact · uncertainty ·
                   indicadores que REFORCAM · indicadores que ENFRAQUECEM
INCERTEZA          obrigatoria e explicita (INT-LAW-135)
LINEAGE            COMPLETE ou PARTIAL declarado
CAN_FEED           CAP-OPP (como hipotese, nunca como facto)
MUST_NOT_DO        misturar FACTO PRESENTE SOBRE O FUTURO (caducidade datada de
                   registo) com SINAL FRACO. Sao duas especies, e hoje o card
                   `future` mistura-as — medido, e por corrigir
```

> Os **indicadores que enfraquecem** são obrigatórios e não decorativos: um radar
> que só sabe fortalecer sinais é um radar que nunca apaga nada.

---

### `CAP-LABEL` · LABEL INTELLIGENCE

```text
PURPOSE            saber o que o rotulo autoriza, na letra dele
BUSINESS_QUESTION  para este produto, nesta cultura, contra este alvo: que dose,
                   que momento, que restricao — e face a que alternativa?
INPUT              COLLECTION_FACT (rotulo autorizado) · CROSSING
OUTPUT             ANALYTIC_JUDGMENT de comparabilidade de uso
FAMILIAS           rotulo · regulatoria
JOIN_KEYS          PRODUCT_ID x CROP_ID x TARGET_ID x AI_ID x MOA x REG_VERSION
HARD_GATES         INT-LAW-062 PROVED exige razao compativel
                   INT-LAW-082 conceito canonico != termo local
                   INT-LAW-081 semelhanca textual nao prova equivalencia
PRESERVA           product · crop · target · dose · timing · restriction ·
                   active ingredient · MOA · registration/version ·
                   comparabilidade
INCERTEZA          comparabilidade entre rotulos de paises diferentes nasce
                   NAO_SEI
LINEAGE            aponta para o documento de rotulo, nao para o resumo dele
CAN_FEED           CAP-PORT · CAP-WIN · CAP-OPP
MUST_NOT_DO        normalizar dose entre jurisdicoes sem contrato · tratar
                   snippet como documento (INT-LAW-064)
```

> ⚠️ **Medido:** `LABEL INTELLIGENCE` **não é um card do portal.** Existe o
> material (`LABEL-USES.json`, `LABEL-MANIFEST.json`, a tabela `registro_uso`) e
> não existe a ferramenta. `MATERIAL ≠ FERRAMENTA`, e por isso a capacidade
> entra aqui **sem** tool declarada.

---

### `CAP-WIN` · AGRONOMIC / CROP WINDOW INTELLIGENCE

```text
PURPOSE            dizer QUANDO, que e o eixo que torna qualquer achado acionavel
BUSINESS_QUESTION  nesta cultura e nesta regiao, qual e a janela em que agir
                   ainda faz diferenca?
INPUT              COLLECTION_FACT (fenologia · clima · rotulo) · CROSSING
OUTPUT             ANALYTIC_JUDGMENT de janela, com estado temporal
FAMILIAS           agronomica · climatica · rotulo · regulatoria
JOIN_KEYS          CROP_ID x REGION_ID x PHENOLOGY_STAGE x TIME_WINDOW
HARD_GATES         INT-LAW-100..105 semantica de tempo e geografia
                   INT-LAW-104 ACT_NOW exige janela compativel
PRESERVA           crop · region · phenology · issue · window · contexto
                   meteorologico/climatico · restricao regulatoria de aplicacao
INCERTEZA          data de calendario NAO chega — a fenologia manda
LINEAGE            COMPLETE
CAN_FEED           CAP-OPP (e e a que mais alimenta) · CAP-FIELD
MUST_NOT_DO        tratar data de calendario como janela · tratar janela de um
                   ano como janela deste
```

> A janela é a **única** capacidade sem a qual `ACT_NOW` não existe. É também a
> única superfície hoje `ALIMENTADO_POR_REAL` — uma em onze.

---

### `CAP-MKT` · MARKET INTELLIGENCE

```text
PURPOSE            dar contexto economico sem o confundir com facto comercial
BUSINESS_QUESTION  o que mudou no mercado que altera a materialidade de uma
                   decisao — e qual e o limite de atribuicao dessa leitura?
INPUT              COLLECTION_FACT (preco · area · producao · comercio)
OUTPUT             contexto; e MARKET_FINDING so com os cinco gates abaixo
FAMILIAS           mercado · comercial · agronomica
JOIN_KEYS          CROP_ID x GEO x PERIOD x UNIT
HARD_GATES         CHANGE + MATERIALITY + CONTEXT + DECISION_AFFECTED +
                   ATTRIBUTION_LIMIT — os cinco, ou fica contexto
                   INT-LAW-067 registo != mercado
NUNCA CONFUNDE     registration · availability · sales · volume · price ·
                   market share — sao SEIS perguntas distintas
INCERTEZA          atribuicao declarada sempre
LINEAGE            unidade e denominador entram no lineage
CAN_FEED           CAP-OPP (como materialidade, nunca como gatilho sozinho)
MUST_NOT_DO        virar produto analitico por estar num card · deduzir venda a
                   partir de registo · comparar precos sem unidade e periodo
```

> ⚠️ Das seis palavras acima, **cinco** já foram usadas como se fossem a sexta em
> algum ponto desta casa. É a confusão mais barata e mais cara do projeto.

---

### `CAP-FIELD` · FIELD INTELLIGENCE

```text
PURPOSE            trazer observacao humana de campo sem a promover a incidencia
BUSINESS_QUESTION  quem viu o que, onde, quando — e o que isso prova e nao prova?
INPUT              COLLECTION_FACT (voz de campo) · SUPPORT/CONTRADICTION_EDGE
OUTPUT             ANALYTIC_SIGNAL de nivel 1, nunca mais do que isso sozinho
FAMILIAS           campo · agronomica
JOIN_KEYS          SPEAKER_ID x CROP_ID x ISSUE_ID x FACT_LOCATION x FACT_TIME
HARD_GATES         INT-LAW-065 identidade != expertise
                   INT-LAW-066 identidade != sinal
                   INT-LAW-101 escopo da pagina != local do facto
                   INT-LAW-071 mesmo originador nao vira multiplas fontes
PRESERVA           speaker/entity · role · prova de expertise · fact location ·
                   fact time · crop · issue · observacao · proveniencia ·
                   independencia — dez, e a independencia e a que mais se perde
INCERTEZA          sem metodo e sem denominador, VOZ DE CAMPO NAO E INCIDENCIA
LINEAGE            COMPLETE, e com o grafo de dependencia entre falantes
CAN_FEED           CAP-OPP · CAP-WIN · CAP-FUT
MUST_NOT_DO        contar tres partilhas do mesmo post como tres observacoes ·
                   inferir localizacao do facto a partir do perfil
```

---

### `CAP-COMP` · COMPETITIVE INTELLIGENCE

```text
PURPOSE            ver o concorrente sem confundir o que ele DIZ com o que E
BUSINESS_QUESTION  o que mudou no lado deles que altera a nossa decisao?
INPUT              COLLECTION_FACT (registo · comunicacao) · CROSSING
OUTPUT             ANALYTIC_SIGNAL · ANALYTIC_JUDGMENT, com a camada carimbada
FAMILIAS           regulatoria · comunicacao publica · mercado · cientifica
JOIN_KEYS          COMPANY_ID x PRODUCT_ID x CROP_ID x GEO x TIME
HARD_GATES         COMPANY_CLAIM != REGULATORY_FACT — e as duas camadas NUNCA
                   partilham contagem
                   INT-LAW-068..077 dependencia e independencia
SEPARA SEMPRE      registration · label · launch · communication · atividade
                   tecnica · evento · facto de mercado · interpretacao analitica
                   — oito, e a oitava e nossa, nao deles
INCERTEZA          comunicacao e alegacao ate prova em contrario
LINEAGE            a camada (REGULATORIO | COMUNICACAO) entra na chave
CAN_FEED           CAP-OPP · CAP-FUT · CAP-MKT
MUST_NOT_DO        somar registo e anuncio no mesmo contador · ler silencio como
                   ausencia (INT-LAW-112)
```

---

### `CAP-SCI` · SCIENTIFIC INTELLIGENCE

```text
PURPOSE            medir forca de evidencia, que e onde a independencia se decide
BUSINESS_QUESTION  o que a ciencia sustenta, com que forca, e replicado por quem?
INPUT              COLLECTION_FACT (paper · ensaio) · SUPPORT/CONTRADICTION_EDGE
OUTPUT             ANALYTIC_JUDGMENT de forca de evidencia
FAMILIAS           cientifica · agronomica · regulatoria
JOIN_KEYS          DOI | TRIAL_ID x RESEARCHER_ID x INSTITUTION_ID x MOLECULE x
                   CROP_ID x ISSUE_ID
HARD_GATES         INT-LAW-072 mesmo documento, vistas diferentes, mesma base
                   INT-LAW-073 mesmo dataset, transformacoes diferentes, mesma
                   origem
                   INT-LAW-102 afiliacao != local do estudo
PRESERVA           paper/study · researcher · institution · crop · issue ·
                   molecule · method · result · forca de evidencia ·
                   replicacao/independencia · tempo e geografia quando aplicavel
INCERTEZA          replicacao ausente e declarada, nao omitida
LINEAGE            COMPLETE; sem DOI/trial_id a atravessar a fronteira, o
                   lineage e PARTIAL e diz-se
CAN_FEED           CAP-OPP · CAP-FUT · CAP-LABEL
MUST_NOT_DO        contar tres papers do mesmo ensaio como tres evidencias
```

> ⚠️ **Bloqueio medido:** sem `DOI`/`trial_id`/afiliação a atravessar a fronteira
> da Collection, esta capacidade **não consegue** distinguir três artigos de um
> ensaio. Isso é um `COLLECTION_GAP` (`INT-LAW-150`), e não um defeito de
> análise.

---

# 35. A FERRAMENTA NÃO CONSTRÓI INTELLIGENCE

## INT-LAW-280 — A TOOL DOES NOT BUILD INTELLIGENCE

A `INT-LAW-240` já dizia que a tool consome e não inventa. Esta diz **o que ela
pode fazer**, em lista fechada, e a fronteira passa a ser verificável em vez de
subentendida.

```text
INTELLIGENCE → ANALYTIC OBJECT → INTELLIGENCE TOOL → DELIVERY / PORTAL
```

A ferramenta **pode**, e só:

```text
FILTER     escolher um subconjunto do que ja existe
NAVIGATE   ir de um objeto ao objeto ligado, por aresta que ja existe
COMPARE    por lado a lado dois objetos ja produzidos
EXPLAIN    mostrar a prova, a incerteza e o que contradiz
RENDER     desenhar
```

A ferramenta **não pode**, nunca:

```text
FABRICAR CROSSING
COMPLETAR UNKNOWN
INFERIR INDEPENDENCIA
PROMOVER SIGNAL A FINDING
PROMOVER FINDING A OPPORTUNITY
FABRICAR FACT, FACT_LOCATION OU FACT_TIME
RECALCULAR LOGICA ESCONDIDA
```

> As cinco permitidas têm uma propriedade em comum, e é ela a lei: **nenhuma
> cria informação.** Filtrar, navegar, comparar, explicar e desenhar operam sobre
> o que já foi produzido e provado a montante. No dia em que uma sexta operação
> aparecer nesta lista, a pergunta a fazer é se ela cria informação — e, se
> criar, ela não é da ferramenta.

## INT-LAW-281 — Um filtro que muda o universo declara-o

Filtrar é permitido; **filtrar e continuar a dizer o número antigo não é.** Se a
tool estreita o conjunto, o `UNIVERSE` do que ela mostra mudou, e a completude
declarada tem de mudar com ele (`INT-LAW-111`).

## INT-LAW-282 — Lógica repetida em duas tools é uma lógica sem dono

Se `science`, `market` e `competitor` calculam a mesma coisa cada um à sua
maneira, não existem três implementações: existem **três verdades**, e nenhuma é
auditável. A lógica sobe para a Intelligence e as três consomem-na.

## 35.0 · OS SETE ATAQUES DA FERRAMENTA, E A LEI QUE BARRA CADA UM

| ataque | barrado por |
|---|---|
| `RT-TOOL-01` Delivery reconstrói finding | `INT-LAW-023` · `INT-LAW-280` |
| `RT-TOOL-02` tool preenche `UNKNOWN` | `INT-LAW-044` · `INT-LAW-280` |
| `RT-TOOL-03` tool lê família não consultada | `INT-LAW-021` · `INT-LAW-284` |
| `RT-TOOL-04` mesma lógica em três tools | `INT-LAW-282` |
| `RT-TOOL-05` tool promove objeto analítico | `INT-LAW-036` · `INT-LAW-280` |
| `RT-TOOL-06` tool infere tempo/lugar do facto | `INT-LAW-101` · `INT-LAW-280` |
| `RT-TOOL-07` filtro muda universo, número não muda | `INT-LAW-281` · `INT-LAW-111` |

## 35.1 · DATA DEMAND CONTRACT

## INT-LAW-283 — Capacidade declara a demanda; não a presume

```text
CAPABILITY
  → ANALYTIC QUESTION
  → REQUIRED CROSSINGS
  → REQUIRED DATA FAMILIES
  → REQUIRED JOIN KEYS
  → COLLECTION GAP
```

## INT-LAW-284 — Os quatro estados do dado não se confundem

`DATA EXISTS` não é um estado útil sozinho. São quatro perguntas, e respondem-se
uma a uma:

```text
DATA_EXISTS             existe alguma coisa guardada
DATA_QUERIED            esta pergunta foi-lhe realmente feita
DATA_CAN_JOIN           as chaves atravessam, e provou-se
DATA_SUPPORTS_ANALYSIS  o que atravessou sustenta a conclusao
```

Só o quarto autoriza uma capacidade a concluir. Os três primeiros são degraus, e
cada degrau que falta tem nome próprio: o segundo é a `INT-LAW-021`, o terceiro é
a `INT-LAW-091`, o quarto é a `INT-LAW-142`.

> **Por que quatro e não um.** Um sistema que só sabe perguntar «temos o dado?»
> responde «sim» e conclui em cima de uma tabela que ninguém consultou, com uma
> chave que não atravessa. Os quatro estados existem para que a resposta «sim»
> tenha de dizer *sim a quê*.

## 35.2 · O PORTAL NÃO DEFINE A ARQUITETURA

As superfícies de hoje são **evidência de produto existente**, e isso não é o
mesmo que autoridade arquitetural (`INT-LAW-271`).

Medido em `data/derivados/MATRIZ-CARDS-SENSORES-V1.json`, re-executado a
2026-09-14 pelo gerador próprio da casa:

```text
CARDS_TOTAL              11
ALIMENTADO_POR_REAL       1     windows
MISTURA_REAL_E_FIXTURE    6
SEM_FONTE_DECLARADA       4
```

E a conta que interessa a esta Bíblia:

```text
CAPACIDADES DEFINIDAS NA SECCAO 34    9
CARDS NO PORTAL                      11
CAPACIDADE SEM CARD NENHUM            1   CAP-LABEL
CARDS SEM CAPACIDADE ANALITICA        3   archive · sources · field
```

A classificação arquitetural de cada card, uma a uma, **já tem dono** e não se
repete aqui: `research/intelligence/AGRO-INTELLIGENCE-TOOL-ROLES-V1.md`. A
tradução para o papel canónico está em
`research/intelligence/INTELLIGENCE-CAPABILITIES-AND-TOOLS.md`.

> **Nenhuma decisão de design, UI, visual ou de menu é tomada nesta Bíblia.**
> Classificar função arquitetural é outra coisa, e o portal não muda por causa
> deste ficheiro.

---

# 36. SOURCE PERFORMANCE INTELLIGENCE

> **Capacidade interna.** Não é card, não é menu, não é tela. A `INT-LAW-242` já
> autoriza uma capacidade a permanecer interna, e esta permanece.

## 36.1 · A FRONTEIRA, MEDIDA ANTES DE ESCRITA

Antes de nomear seja o que for, procurou-se dono. **Havia**, e isso mudou o
desenho:

```text
SOURCE_RELEVANCE       OWNER = COLLECTION   leis/relevancia_da_fonte.py
REQUIREMENT_PRIORITY   OWNER = COLLECTION   leis/gestao_da_coleta.py
PRIORITY_TIER          OWNER = COLLECTION   leis/politica_da_coleta.py
```

Os três estão `OWNER_PROVEN` no registo de conceitos. E o primeiro responde a
uma pergunta que **não é** a desta secção:

```text
SOURCE_RELEVANCE          «esta fonte vale ser acompanhada PARA ESTE PROPOSITO?»
                          decisao do par (FONTE, PROPOSITO), ANTES do gasto
SOURCE PERFORMANCE        «o que esta fonte PRODUZIU, medido depois?»
                          observacao retrospetiva, DEPOIS do gasto
```

Uma é uma **porta**; a outra é uma **fita métrica**. Uma decide se se vai; a
outra conta o que se trouxe. Confundi-las daria dois donos à mesma regra, e a
`INT-LAW-000` proíbe-o.

## INT-LAW-290 — SOURCE PERFORMANCE mede; não decide

```text
SOURCE PERFORMANCE RECOMMENDS
COLLECTION DECIDES
```

A Intelligence observa a jusante e aconselha. Quem decide o que coletar, quando e
por que rota é a Collection, como já dizem a `INT-LAW-024` e a `INT-LAW-151`.

## INT-LAW-291 — SOURCE PRODUCED CONTENT ≠ SOURCE PRODUCED USEFUL INTELLIGENCE

Bytes, ficheiros, itens admitidos e linhas coletadas medem **atividade**. Nenhum
deles mede valor analítico.

## INT-LAW-292 — HIGH VOLUME ≠ HIGH VALUE

Uma fonte que produz muito e cruza pouco é uma fonte cara. O perfil separa
sempre o quanto veio do quanto serviu, e nunca deixa o primeiro eleger o
segundo.

## INT-LAW-293 — O valor de uma fonte é contextual

Corolário da `INT-LAW-060`, que já governa a qualidade evidencial da fonte por
claim. Esta estende-o à **contribuição medida**:

```text
SOURCE_GLOBAL_SCORE = truth        PROIBIDO
```

A mesma fonte pode ser excelente para regulatório, fraca para mercado, inútil
para campo e crítica para segurança. O máximo permitido é um resumo **derivado**
de perfis contextuais, com os componentes visíveis e decomponíveis
(`INT-LAW-093`).

## INT-LAW-294 — Sem lineage, a contribuição é UNKNOWN

Atribuir valor exige a cadeia inteira, provada:

```text
SOURCE → OBSERVATION → CLAIM/FACT → INTELLIGENCE_RUN → CROSSING
       → SIGNAL / FINDING / OPPORTUNITY
```

Falhando um elo:

```text
CONTRIBUTION = UNKNOWN
```

E `UNKNOWN` fica `UNKNOWN`: não é zero, não é média, não se preenche por
plausibilidade (`INT-LAW-044`). A `INT-LAW-042` já diz o resto — **estar no mesmo
run não cria aresta**, e portanto não cria crédito.

## INT-LAW-295 — CONTRADICTION CAN CREATE ANALYTIC VALUE

Uma fonte que derrubou uma Opportunity errada **produziu valor**. Registam-se em
separado, e nunca se somam num saldo:

```text
SUPPORT_VALUE         sustentou uma conclusao que se manteve
CONTRADICTION_VALUE   impediu uma conclusao que se teria revelado errada
```

Baixar o perfil de uma fonte por ela contradizer é ensinar o sistema a preferir
fontes concordantes — que é a definição de um sistema que deixa de aprender. A
`INT-LAW-123` já proíbe esconder evidência contrária; esta proíbe **penalizá-la**.

## INT-LAW-296 — LOW FREQUENCY ≠ LOW IMPORTANCE

Taxa de mudança e importância são **dois eixos**, e um não substitui o outro.
Uma fonte regulatória oficial que publica quatro vezes por ano não é uma fonte
fraca: é uma fonte rara e decisiva.

Categorias protegidas, cuja posição não depende do perfil:

```text
MANDATORY_SOURCE                    obrigacao legal ou de contrato
STRATEGIC_SOURCE                    decisao humana declarada e datada
LOW_FREQUENCY_HIGH_IMPORTANCE       raridade nao e fraqueza
```

## INT-LAW-297 — PRIORITIZATION MUST PRESERVE EXPLORATION

O risco é um laço que se fecha sozinho: se só se coleta quem já provou valor,
quem nunca foi amostrado nunca prova nada, e a ausência de prova passa a
funcionar como prova de ausência.

```text
EXPLOITATION   aproveitar o que ja se provou util
EXPLORATION    manter capacidade para fonte nova, pouco amostrada ou
               estrategicamente necessaria
```

**A quota não se fixa aqui.** Escolher um número antes de haver medição seria
inventar a medida que esta secção existe para exigir.

E o motivo é mais fundo do que prudência: a observabilidade é **parcial** — só se
descobre que uma fonte mudou indo lá. Uma fonte não amostrada não produz um
perfil baixo; produz **nenhum perfil**. Os dois estados não se confundem:

```text
SAMPLE_SIZE = 0   →   PERFIL = UNKNOWN    (nunca «fraco»)
```

## INT-LAW-298 — HISTORICAL HIGH YIELD ≠ FUTURE GUARANTEE

O perfil pondera `RECENCY`, `CHANGE_RATE`, `CURRENT_RELEVANCE` e `CONTEXT`. Uma
fonte excelente há dois anos pode ter mudado de dono, de formato ou de conteúdo.

O histórico **não se apaga** (`INT-LAW-210`): decai no peso, permanece no registo.

## INT-LAW-299 — Um item contribui uma vez por capacidade, e a duplicação é visível

O mesmo conteúdo a alimentar três capacidades não é três contribuições. A
contagem é por `(SOURCE, CONTEXT, CAPABILITY)` e a sobreposição entre capacidades
é declarada, nunca somada. É a `INT-LAW-075` — as famílias não se comprimem —
aplicada à contagem de crédito.

## 36.2 · OS OBJETOS, E POR QUE SE CHAMAM ASSIM

```text
SOURCE_ANALYTIC_CONTRIBUTION   uma aresta provada de lineage, de uma fonte ate
                               um objeto analitico. A unidade atomica.
SOURCE_CONTRIBUTION_PROFILE    o agregado contextual dessas arestas.
                               (o «SOURCE_PERFORMANCE_PROFILE» do enunciado)
SOURCE_COLLECTION_ADVICE       o que a Intelligence entrega a Collection.
                               (o «..._PRIORITY_RECOMMENDATION» do enunciado)
```

> **Por que não «PRIORITY» no nome.** `PRIORITY` foi **aposentado como nome
> sobrecarregado** por decisão humana datada de 2026-09-14, e as prioridades que
> restam — `PRIORITY_TIER`, `REQUIREMENT_PRIORITY` — são da Collection, com
> módulo e prova. Um objeto da Intelligence chamado `..._PRIORITY_...` leria-se,
> seis meses depois, como se a Intelligence tivesse uma prioridade própria. Tem
> um **conselho**. A palavra faz o trabalho de a lei não ter de ser relida.

O perfil é sempre contextual. Nunca existe fora de um contexto:

```text
SOURCE · COUNTRY · DATA_FAMILY · CROP · ISSUE ·
ANALYTIC_CAPABILITY · QUESTION_CLASS · TIME_WINDOW
```

## 36.3 · AS MÉTRICAS

Agrupadas pelo que **medem**, porque misturar os quatro grupos é como se produz
um número único que engana:

```text
ATIVIDADE — quanto veio (nao mede valor: INT-LAW-291)
    COLLECTION_ATTEMPTS · COLLECTION_SUCCESS_RATE · ADMISSION_YIELD

UTILIDADE ANALITICA — quanto serviu
    USABLE_INTELLIGENCE_YIELD · UNIQUE_CLAIM_YIELD · NOVELTY_YIELD
    DUPLICATION_RATE · CROSSING_CONTRIBUTION · TOOL_COVERAGE

EFEITO NO JULGAMENTO — o que mudou por causa dela
    INDEPENDENCE_CONTRIBUTION · SUPPORT_CONTRIBUTION
    CONTRADICTION_CONTRIBUTION · SIGNAL_CONTRIBUTION
    FINDING_CONTRIBUTION · OPPORTUNITY_CONTRIBUTION

APTIDAO — se da para usar
    FACT_TIME_COVERAGE · FACT_LOCATION_COVERAGE · JOIN_KEY_COMPLETENESS
    FRESHNESS · UPDATE_FREQUENCY · LATENCY · ERROR_RATE · BLOCK_RATE
    STABILITY · COST_PER_USEFUL_ITEM

CONFIANCA NA PROPRIA MEDICAO
    SAMPLE_SIZE · CONFIDENCE
```

**Nenhuma família é obrigada a todas.** Uma métrica que não se aplica declara-se
`NOT_APPLICABLE`; uma que se aplica e não foi medida declara-se `NOT_MEASURED`
(`INT-LAW-252`). As duas não são a mesma coisa, e nenhuma é zero.

E os dois últimos governam todos os outros: um perfil com `SAMPLE_SIZE` de três
itens não é um perfil fraco — é um perfil que ainda não existe.

## 36.4 · O CONTRATO DE SAÍDA PARA A COLLECTION

```text
SOURCE_COLLECTION_ADVICE
    SOURCE_ID                      da Collection, LIDO — nunca criado
    CONTEXT                        os oito eixos de 36.2
    EVIDENCE_WINDOW                de quando ate quando se mediu
    CONTRIBUTION_PROFILE           o perfil, com componentes visiveis
    SUGGESTED_DIRECTION            MORE | SAME | LESS | INVESTIGATE | UNKNOWN
    REASON                         em texto, ligado a lineage
    CONFIDENCE
    SAMPLE_SIZE
    FRESHNESS
    EXPLORATION_STATE              NEVER_SAMPLED | UNDER_SAMPLED | ESTABLISHED
    PROTECTED_CATEGORY             se aplicavel (INT-LAW-296)
    GENERATED_BY_INTELLIGENCE_RUN
    LINEAGE
```

`SUGGESTED_DIRECTION` é uma **direção**, não um número e não um lugar numa fila.
Não existe aqui um campo com o valor final da prioridade, e a ausência é
deliberada: um número atravessaria a fronteira e seria obedecido.

O percurso, e os dois pontos onde ele **não** pode encurtar:

```text
INTELLIGENCE
  → SOURCE_COLLECTION_ADVICE
  → FRONTEIRA CANONICA DA COLLECTION     ← nao se salta
  → ORQUESTRADOR DA COLLECTION           ← quem decide
  → proxima coleta
```

```text
INTELLIGENCE NAO altera agenda.
INTELLIGENCE NAO chama collector.
INTELLIGENCE NAO altera SOURCE_ID.
INTELLIGENCE NAO assume ownership do source registry.
```

**A implementação do consumo deste conselho pela Collection fica fora desta
Bíblia**, e fora da autorização da secção 32. Esta secção descreve o que a
Intelligence entrega — não o que a Collection faz com isso.

## 36.5 · OS CATORZE ATAQUES, E A LEI QUE BARRA CADA UM

| ataque | barrado por |
|---|---|
| `RT-SRC-01` volume domina | `INT-LAW-292` |
| `RT-SRC-02` fonte pequena desaparece | `INT-LAW-296` |
| `RT-SRC-03` fonte nova nunca testada | `INT-LAW-297` |
| `RT-SRC-04` republicação vira independência | `INT-LAW-071` · `INT-LAW-072` |
| `RT-SRC-05` contrária é penalizada | `INT-LAW-295` |
| `RT-SRC-06` conta em três capacidades | `INT-LAW-299` |
| `RT-SRC-07` crédito por mesmo run | `INT-LAW-042` · `INT-LAW-294` |
| `RT-SRC-08` bom em regulatório, bom em tudo | `INT-LAW-293` |
| `RT-SRC-09` histórico congela | `INT-LAW-298` |
| `RT-SRC-10` chama collector | `INT-LAW-290` · §28 |
| `RT-SRC-11` escreve no registry | `INT-LAW-290` · §28 |
| `RT-SRC-12` número único sem contexto | `INT-LAW-293` |
| `RT-SRC-13` conselho lido como ordem | `INT-LAW-290` · `INT-LAW-024` |
| `RT-SRC-14` obrigatória perde vez | `INT-LAW-296` |

---

# 37. AVALIAÇÃO CONTÍNUA DA INTELLIGENCE

A secção 24 diz **que** se avalia e com que métricas. Esta diz **quando** e **com
que espécie de prova**.

## 37.1 · OS DOIS MOMENTOS

```text
OFFLINE EVAL   antes de mudar regra, modelo ou prompt.
               Conjunto fixo, resposta conhecida, comparavel entre versoes.

ONLINE EVAL    sobre execucoes reais, onde nao ha resposta conhecida.
               Mede padrao, anomalia e deriva — nunca «acerto».
```

Os dois não se substituem: o offline responde «esta mudança piorou?», o online
responde «alguma coisa mudou no mundo?».

## 37.2 · O TRACE

Toda execução deixa rasto com inputs, outputs, passos intermédios, versão e
custo. É a `INT-LAW-041` — lineage é dado **mais** lógica **mais** execução —
dita do lado da observabilidade.

Sem trace não há eval possível: não se avalia o que não se consegue reconstruir.

## 37.3 · FAILURE → TEST CASE

```text
CASO REAL QUE EXPOS UM ERRO  →  CASO DE REGRESSAO
```

Um defeito encontrado uma vez e não fixado num teste é um defeito que volta. Esta
é a ponte entre o online e o offline: o online encontra, o offline passa a
guardar.

## INT-LAW-300 — A espécie da prova segue a natureza da pergunta

Quatro avaliadores, e a escolha não é de gosto:

```text
DETERMINISTIC   ha resposta verificavel por regra
                (chave atravessa? campo existe? universo declarado?)
HUMAN           exige julgamento de dominio ou de risco
LLM             ha escala e a resposta e textual
PAIRWISE        pontuar em absoluto e dificil, comparar duas versoes e facil
```

## INT-LAW-301 — LLM-as-judge não é a prova por defeito, e ele próprio é avaliado

Um avaliador de LLM é um mecanismo (`INT-LAW-160`), não uma autoridade. Antes de
se confiar nele para uma classe de perguntas, mede-se a **concordância dele com
julgamento humano** nessa classe. Um juiz não validado não valida nada.

E onde existir prova determinística, é ela que manda: usar um LLM para responder
a uma pergunta que uma regra responde é trocar uma resposta verificável por uma
resposta plausível.

## 37.4 · AS QUATRO LEIS QUE NÃO FORAM ESCRITAS

O enunciado da revisão mandou avaliar onze leis candidatas. Sete entraram. Quatro
**não**, e a razão é a mesma para as quatro: já existiam, com outro nome, e
escrevê-las outra vez criaria o segundo dono que a `INT-LAW-000` proíbe.

| candidata | já era | e diz |
|---|---|---|
| `DATA EXISTS != DATA WAS CONSULTED` | `INT-LAW-021` | existência de material não prova que a família foi consultada |
| `PORTAL DOES NOT RECONSTRUCT INTELLIGENCE` | `INT-LAW-023` | Portal não reconstrói Intelligence |
| `SOURCE VALUE IS CONTEXTUAL` | `INT-LAW-060` | qualidade da fonte é contextual — a `INT-LAW-293` **estende**, e cita |
| `SAME RUN != CONTRIBUTION` | `INT-LAW-042` | participar do mesmo run não cria aresta |

> **Uma Bíblia que cresce por acumulação deixa de ser lei e passa a ser
> arquivo.** Recusar quatro leis é trabalho da mesma natureza que escrever sete.

---

## HARD STOP

**Esta Bíblia autoriza exatamente uma obra: a primeira missão da secção 32 — um
`INTELLIGENCE_RUN` identificado sobre UM item real da Sala de Espera, com
linhagem provada, sem coleta direta e sem fabricar julgamento. Mais nada.**

E autoriza-a **sujeita aos gates a montante**, que não são desta Bíblia para
abrir e que hoje estão fechados:

```text
TRAVA-DA-INTELIGENCIA   COLLECTION_FOUNDATION_CLOSED = NAO
SALA DE ESPERA          0 itens reais
```

Enquanto qualquer um dos dois assim estiver, a missão da secção 32 está
autorizada por esta lei **e bloqueada pela máquina** — que é um estado coerente,
e o estado de hoje.

Fora dessa missão, nada: sem Intelligence Tools, sem Portal, sem UI, sem
Opportunity, sem França, sem Espanha, sem controlador EAME. Esses continuam a
precisar dos gates da secção 26, e nenhum deles foi aberto.

**E a V0.3 não abriu nenhum.** As secções 34, 35, 36 e 37 descrevem contratos —
capacidades, fronteira da ferramenta, performance de fonte e avaliação. Descrever
não é autorizar:

```text
SOURCE PERFORMANCE                  NAO IMPLEMENTAR
CONSUMO DO CONSELHO PELA COLLECTION NAO IMPLEMENTAR
INTELLIGENCE TOOLS                  NAO IMPLEMENTAR
PRIORIDADES REAIS DE COLETA         NAO ALTERAR
```

A fronteira desta Bíblia continua a ser exatamente uma obra, a da **secção 32**,
e continua sujeita aos dois gates acima, que hoje estão fechados.