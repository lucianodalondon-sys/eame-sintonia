# BÍBLIA DE ENGENHARIA DA INTELLIGENCE — SINTONIA EAME

```text
BIBLE_ID = SINTONIA-INTELLIGENCE-BIBLE
VERSION = V0.2
STATUS = CANONICAL
DATE = 2026-09-13
PROMOTED = 2026-09-14
IMPLEMENTATION_AUTHORIZED = SOMENTE_A_PRIMEIRA_MISSAO_DA_SECAO_32
```

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
GATES         9 / 9 PASS   (a 6 fechou com PORTAO_DO_CONTROLE=PASS · 22 provas)
SUPERSEDES    A-BIBLIA-INTELIGENCIA — o «INVENTÁRIO DAS LEIS», que recusa o
              título no próprio cabeçalho. A relação é de IDENTIDADE, e a outra
              ponta declara-a de volta no registo.
```

**O que a promoção autoriza, e só isso.** `IMPLEMENTATION_AUTHORIZED = NO`
nasceu colado a `STATUS = CANDIDATE`: enquanto esta Bíblia fosse candidata,
implementar contra ela era construir sobre lei não aprovada. A secção 32 nomeia
a **primeira missão após promoção** e delimita-a. É essa, e mais nenhuma, que
esta promoção autoriza.

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

---

# 33. VEREDITO V0.2

```text
ENGINEERING_BIBLE_WRITTEN = YES
COLLECTION_OWNER_COLLISION_FOUND = YES
COLLECTION_OWNER_COLLISION_CORRECTED_IN_CANDIDATE = YES
CANONICAL = NO
RUNTIME_IMPLEMENTED = NO
COLLECTION_CHANGED = NO
INTELLIGENCE_IMPLEMENTATION_STARTED = NO
PORTAL_CHANGED = NO
LIVE_CHANGED = NO
```

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

`KNOW_HOW_DELTA = ATUALIZAÇÃO NECESSÁRIA APÓS PROMOÇÃO/INTEGRAÇÃO`

**HARD STOP — esta Bíblia não autoriza iniciar implementação da Intelligence.**