# BÍBLIA DE ENGENHARIA DA INTELLIGENCE — SINTONIA EAME

```text
BIBLE_ID = SINTONIA-INTELLIGENCE-BIBLE
VERSION = V0.1
STATUS = CANDIDATE_FOR_CANONICAL_REVIEW
DATE = 2026-09-13
IMPLEMENTATION_AUTHORIZED = NO
```

> Esta é a **Bíblia de Engenharia da Intelligence**, não um relatório, backlog, handoff, design de portal ou prova de implementação.
>
> Ela nasce como `CANDIDATE_FOR_CANONICAL_REVIEW` porque a governança mediu `CONTROL_PLANE_ATOMICITY = FAIL`: código, Bíblias, Know-how e registry ainda não formam um único snapshot canônico. Promovê-la silenciosamente a `CANONICAL` nesta branch criaria exatamente a divergência que o Control Plane foi criado para impedir.
>
> **Esta Bíblia declara como a Intelligence deve funcionar. Ela não prova que funciona.**

---

# 0. PAPEL, ESCOPO E AUTORIDADE

## 0.1 O que esta Bíblia possui

Esta Bíblia é candidata a possuir, após promoção explícita, as leis de:

- entrada e fronteira da Intelligence;
- identidade analítica;
- fatos, claims, evidências, hipóteses, sinais, crossings, findings e opportunities;
- lineage/proveniência analítica;
- dependência e independência de evidência;
- incerteza e alternativas;
- completude/universos;
- temporalidade e geografia na análise;
- Radar Futuro / horizon scanning;
- uso de IA/LLM na Intelligence;
- segurança da Intelligence;
- qualidade, observabilidade, avaliação e red team;
- relação Collection ↔ Intelligence ↔ Delivery.

## 0.2 O que esta Bíblia NÃO possui

Ela não possui:

- leis da Collection;
- identidade de RAW/RUN/STORAGE;
- aquisição direta;
- regras de Admission;
- UI/portal;
- Design System;
- deploy;
- execução comercial;
- decisão humana final;
- verdade sobre runtime atual.

## 0.3 Ordem canônica do projeto

```text
COLLECTION
→ INTELLIGENCE
→ INTELLIGENCE TOOLS / VALIDATION
→ CASCO / PORTAL
```

Portal não puxa arquitetura para trás.

---

# 1. DEFINIÇÃO DA INTELLIGENCE

## INT-LAW-001 — Intelligence começa na Sala de Espera

```text
INTELLIGENCE_INPUT = MATERIAL ADMITIDO / READY NA SALA DE ESPERA
```

Collection termina na Sala de Espera. Intelligence não redefine Admission para conseguir material mais conveniente.

## INT-LAW-002 — Intelligence transforma evidência em julgamento auditável

Intelligence não é “resumir documentos”.

Sua função é produzir, quando houver base:

```text
FACTS / CLAIMS
→ RELATIONS / CROSSINGS
→ SIGNALS
→ HYPOTHESES / ALTERNATIVES
→ FINDINGS / JUDGMENTS
→ OPPORTUNITIES / ATTENTION ITEMS / FUTURE SIGNALS
```

com lineage, incerteza, prova e limites explícitos.

## INT-LAW-003 — Intelligence pode concluir que não há ação defensável

```text
NO_DEFENSIBLE_ACTION_YET
```

é saída válida e desejável quando a evidência não suporta promoção.

Quantidade de cards não mede qualidade.

## INT-LAW-004 — Intelligence não fabrica necessidade de produto

Ausência de finding/opportunity não pode ser “corrigida” relaxando leis para abastecer portal.

## INT-LAW-005 — Verdade, relevância e acionabilidade são eixos diferentes

```text
TRUE != RELEVANT != ACTIONABLE
```

Algo pode ser verdadeiro e irrelevante, relevante e incerto, ou verdadeiro e fora da janela de ação.

---

# 2. FRONTEIRAS ENTRE DOMÍNIOS

## INT-LAW-010 — Collection Gap volta pela Collection canônica

Intelligence pode detectar:

```text
COLLECTION_GAP
```

mas não chama collector diretamente.

Fluxo:

```text
INTELLIGENCE
→ COLLECTION_GAP_REQUEST
→ ORCHESTRATOR CANÔNICO DA COLLECTION
→ COLLECTOR
→ RUN
→ RAW
→ DERIVED
→ STRUCTURED
→ ADMISSION
→ SALA DE ESPERA
→ INTELLIGENCE
```

## INT-LAW-011 — Collection existe ≠ família consultada

Ter material no acervo não prova que a Intelligence o consultou para a pergunta atual.

## INT-LAW-012 — Intelligence ≠ Delivery

Intelligence produz material analítico. Delivery/Casco decide como expor material autorizado.

## INT-LAW-013 — Portal não reconstrói Intelligence

Portal não pode:

- refazer crossing;
- completar relação ausente;
- recalcular independência;
- converter UNKNOWN em display-friendly PASS;
- reclassificar finding por conveniência.

## INT-LAW-014 — Recommendation ≠ Action

Por padrão:

```text
INTELLIGENCE MAY PROPOSE
INTELLIGENCE DOES NOT EXECUTE OPERATIONAL ACTION
```

Qualquer write/action futuro precisa de owner, contrato, autorização e prova separados.

---

# 3. IDENTIDADES ANALÍTICAS

## INT-LAW-020 — Um saco semântico único é proibido

Não comprimir:

```text
INTELLIGENCE_REQUEST
!= INTELLIGENCE_RUN
!= FACT
!= CLAIM
!= EVIDENCE
!= ASSUMPTION
!= HYPOTHESIS
!= SIGNAL
!= CROSSING
!= FINDING / JUDGMENT
!= OPPORTUNITY
!= RECOMMENDATION
!= ACTION
```

Isso não obriga 12 tabelas na primeira implementação. Obriga 12 conceitos semânticos distintos.

## INT-LAW-021 — FACT é proposição sobre o mundo com suporte factual

FACT não é texto do documento, nem opinião do analista, nem output de LLM.

## INT-LAW-022 — CLAIM é afirmação identificável e rastreável

Toda claim consumida pela Intelligence precisa de identidade estável e global dentro do sistema.

Proibido `CLAIM_ID` derivado apenas de posição, contador ou ordem de processamento.

## INT-LAW-023 — EVIDENCE é suporte, não conclusão

Evidence pode apoiar, contradizer ou contextualizar uma claim.

## INT-LAW-024 — ASSUMPTION é explícita

Premissa usada para atravessar lacuna crítica precisa ser registrada como premissa, não apresentada como fato.

## INT-LAW-025 — HYPOTHESIS não vira FACT por repetição

Várias fontes repetindo hipótese, rumor ou uma mesma origem não promovem automaticamente factualidade.

## INT-LAW-026 — SIGNAL é observação analiticamente relevante, não oportunidade

```text
SIGNAL != FINDING != OPPORTUNITY
```

## INT-LAW-027 — CROSSING é relação produzida por chaves compatíveis e lógica declarada

Dois materiais parecidos não são crossing sem chave factual compatível ou regra explícita.

## INT-LAW-028 — FINDING/JUDGMENT precisa de rationale auditável

Guardar rationale verificável, evidências, premissas, alternativas e gates; não depender de chain-of-thought privado de modelo.

## INT-LAW-029 — OPPORTUNITY tem identidade factual própria

Opportunity não pode ser apenas um card visual. Sua identidade precisa ser separável de sua renderização e de seu score.

---

# 4. PROVENIÊNCIA E LINEAGE

## INT-LAW-030 — Todo derivado aponta para seus inputs reais

Finding sem upstream identificável é inválido.

## INT-LAW-031 — Lineage inclui dados + lógica + execução

Para reproduzir um resultado, a Intelligence precisa poder responder:

```text
QUAL INPUT?
QUAL CLAIM/EVIDENCE?
QUAL REGRA/ALGORITMO/PROMPT?
QUAL VERSÃO?
QUAL MODELO, SE HOUVE?
QUAIS PARÂMETROS?
QUAL UNIVERSO?
QUAL RUN?
QUAL OUTPUT?
```

## INT-LAW-032 — Participar do mesmo run não cria edge

```text
SAME_RUN(A, B) != A_DERIVED_FROM_B
```

Não inferir produto cartesiano entre inputs e outputs.

## INT-LAW-033 — Declared lineage ≠ observed lineage

Relação declarada e relação observada possuem estados diferentes.

## INT-LAW-034 — Lineage incompleto fica visível

Quando não for possível reconstruir parte da cadeia:

```text
LINEAGE_STATE = PARTIAL / UNKNOWN
```

Nunca preencher por plausibilidade.

## INT-LAW-035 — Derivação deve permitir impact analysis

Antes de mudar contrato, normalização, taxonomia ou regra, deve ser possível identificar downstream potencialmente afetado.

---

# 5. RUN DA INTELLIGENCE

## INT-LAW-040 — RUN é execução, não produto analítico

```text
INTELLIGENCE_RUN != FINDING
```

## INT-LAW-041 — Toda execução tem identidade

Cada execução precisa de `INTELLIGENCE_RUN_ID` ou identidade equivalente não ambígua.

## INT-LAW-042 — Run preserva configuração efetiva

Registrar, conforme aplicável:

- versão de código;
- versão de regras;
- modelo;
- prompt/policy;
- parâmetros;
- inputs;
- universo;
- horário;
- resultado;
- erros;
- reuso;
- custo quando mensurável.

## INT-LAW-043 — NOT_RUN ≠ ERROR ≠ EMPTY_RESULT

Preservar estados separados.

## INT-LAW-044 — Reuso precisa ser provado

Reutilizar resultado apenas quando for demonstrada equivalência relevante entre:

```text
INPUTS + LOGIC + PARAMETERS + REQUIRED_CONTEXT
```

“Parece a mesma pergunta” não é cache key.

---

# 6. QUALIDADE E CREDIBILIDADE DA EVIDÊNCIA

## INT-LAW-050 — Fonte tem qualidade contextual, não reputação absoluta

Avaliar o que a fonte prova para aquela claim.

## INT-LAW-051 — Quatro eixos de evidência permanecem separados

Preservar o contrato maduro:

```text
EVIDENCE_CLASS
EVIDENCE_STATE
EVIDENCE_STRENGTH
EVIDENCE_REASON
```

## INT-LAW-052 — PROVED exige razão semanticamente compatível

```text
PROVED + UNKNOWN_REASON = INVALID
```

## INT-LAW-053 — Conteúdo do corpo ≠ chrome da página

Sidebar, menu, breadcrumbs, tags, recommendation widgets e texto de navegação não provam fato no corpo.

## INT-LAW-054 — Snippet ≠ documento completo

Trecho de busca ou preview não substitui leitura da unidade necessária quando a conclusão depende do contexto ausente.

## INT-LAW-055 — Identidade ≠ expertise

Pessoa/organização identificada não se torna especialista específica de cultura/issue sem prova.

## INT-LAW-056 — Identidade ≠ sinal

Conta/creator/empresa conhecida não prova comportamento, issue ou evento atual.

## INT-LAW-057 — Registro ≠ mercado

```text
REGISTRATION != SALES
REGISTRATION != COMMERCIAL_AVAILABILITY
REGISTRATION_COUNT != MARKET_SHARE
```

---

# 7. DEPENDÊNCIA E INDEPENDÊNCIA

## INT-LAW-060 — Grafo de dependências vem antes de convergência

Nenhuma contagem multi-sinal é publicada antes de resolver dependência suficiente entre as pernas.

## INT-LAW-061 — Mesmo originador não vira múltiplas fontes

Reprodução/sindicação/cópia da mesma origem não cria independência.

## INT-LAW-062 — Mesmo documento, vistas diferentes, continua sendo a mesma evidência-base

Index, listing, metadata e corpo podem oferecer atributos diferentes, mas não viram fontes independentes automaticamente.

## INT-LAW-063 — Mesmo dataset, transformações diferentes, não cria fonte independente

Transformação pode criar validação distinta, não origem independente.

## INT-LAW-064 — Mesma entidade, observações diferentes, precisa de classificação explícita

Observações em tempos/canais diferentes podem ter valor próprio, mas não recebem independência por default.

## INT-LAW-065 — Famílias precisam ser semanticamente separadas

Preservar:

```text
EVIDENCE_FAMILY
DATASET_FAMILY
SOURCE_FAMILY
```

## INT-LAW-066 — Structural validation não infla independent source count

Catálogo, label e registro podem validar estrutura sem se tornarem três sinais externos independentes.

## INT-LAW-067 — Convergência mede independência e compatibilidade

Convergência exige pelo menos:

- compatibilidade factual;
- dependência analisada;
- tempo compatível;
- geografia compatível;
- entidades compatíveis;
- ausência de double counting crítico.

---

# 8. NORMALIZAÇÃO E ENTITY RESOLUTION

## INT-LAW-070 — Normalização precede backfill e cruzamento massivo

Identidades equivalentes precisam de regra/prova antes de multiplicar relações.

## INT-LAW-071 — Similaridade textual não prova equivalência

Exemplo-testemunha já maduro:

```text
VITE
VITE DA VINO
VINE
```

podem ter relação, mas `VITE DA TAVOLA` exige decisão própria.

## INT-LAW-072 — Canonical concept ≠ local term

Multilíngue deve mapear termos locais para conceitos sem apagar o original.

## INT-LAW-073 — Resolver entidade não autoriza fabricar SOURCE_ID/DOCUMENT_ID

Identidade da Collection continua governada pela Bíblia da Collection.

## INT-LAW-074 — Conflito de normalização permanece conflito

Não escolher “o mais provável” para fazer crossing fechar.

---

# 9. CROSSINGS E CONVERGÊNCIA

## INT-LAW-080 — Crossing precisa declarar pergunta

Cada crossing existe para responder uma pergunta explícita.

## INT-LAW-081 — Missing join key bloqueia crossing

Se uma chave necessária não estiver provada:

```text
CROSSING_STATE = NOT_POSSIBLE / UNKNOWN / PARTIAL
```

não “closest match”.

## INT-LAW-082 — Métricas de convergência ficam separadas

Preservar:

```text
EXTERNAL_SIGNAL_COUNT
INDEPENDENT_SOURCE_COUNT
STRUCTURAL_VALIDATION_COUNT
INTELLIGENCE_FAMILY_COUNT
```

## INT-LAW-083 — Score não substitui decomposição

Se houver score, seus componentes e razões devem continuar acessíveis.

## INT-LAW-084 — Score alto não derrota gate duro

Gate epistemológico/segurança falho não pode ser compensado por soma de pontos.

## INT-LAW-085 — Correlação ≠ causalidade

Claim causal exige contrato/prova mais forte do que associação ou coocorrência.

---

# 10. TEMPO E GEOGRAFIA

## INT-LAW-090 — Herda separações maduras

```text
SOURCE_LOCATION != FACT_LOCATION
FACT_TIME != PUBLICATION_TIME != OBSERVED_TIME != COLLECTED_TIME
```

## INT-LAW-091 — Escopo da página ≠ local do fato

País da página/conta/fonte não prova país onde o fato ocorreu.

## INT-LAW-092 — Afiliação ≠ local do estudo

Instituição/autoria não prova localização experimental.

## INT-LAW-093 — Tempo participa da acionabilidade

Um fato pode permanecer factual e perder utilidade operacional.

## INT-LAW-094 — ACT_NOW exige janela compatível

Sem janela factual suficiente:

```text
ACT_NOW = NOT_PROVED
```

## INT-LAW-095 — Estado temporal precisa explicar o motivo

Exemplos possíveis:

```text
ACT_NOW
PLAN_NEXT_CYCLE
MONITOR
STALE_FOR_ACTION
UNKNOWN_WINDOW
```

A taxonomia final deve ser contratada antes do runtime.

---

# 11. UNIVERSOS, COMPLETUDE, ZERO E AUSÊNCIA

## INT-LAW-100 — Universo é definido pela pergunta

```text
UNIVERSE != DIRECTORY
```

## INT-LAW-101 — Completude exige contrato de universo

Para afirmar `COMPLETE`, `FULL_SCAN`, `ZERO` ou `NOT_FOUND` com força de ausência, declarar pelo menos:

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

## INT-LAW-102 — ZERO_PROVED é estado raro e exigente

Preservar distinções:

```text
ZERO_PROVED
NOT_FOUND_IN_SCANNED_UNIVERSE
UNIVERSE_INCOMPLETE
NOT_QUERIED
MATERIAL_NOT_USABLE
UNKNOWN
```

## INT-LAW-103 — Input vazio nunca prova completude

Gate crítico que passa com input vazio é inválido.

## INT-LAW-104 — Reprodutibilidade ≠ decisão de universo

Dois leitores concordarem na mesma contagem prova leitura reprodutível; não prova que o universo escolhido é o correto.

---

# 12. INCERTEZA, JULGMENT E ALTERNATIVAS

## INT-LAW-110 — Informação, premissa e julgamento ficam separados

```text
UNDERLYING_INFORMATION
ASSUMPTION
JUDGMENT
```

não podem ser renderizados como equivalentes.

## INT-LAW-111 — Major judgment explica incerteza

Registrar causas relevantes de incerteza:

- quantidade de evidência;
- qualidade;
- freshness;
- gaps;
- dependência de premissas;
- conflitos.

## INT-LAW-112 — Confidence ≠ probability

Confiança na base do judgment e probabilidade de um evento são conceitos diferentes.

## INT-LAW-113 — Contradictory evidence fica visível

Informação material contrária não pode ser descartada porque reduz score.

## INT-LAW-114 — High-impact uncertainty exige alternativas

Quando risco/impacto justificar, produzir hipóteses alternativas e indicadores que mudariam o judgment.

## INT-LAW-115 — Judgment novo explica mudança

Quando um judgment muda, registrar:

```text
PREVIOUS_JUDGMENT
NEW_JUDGMENT
WHAT_CHANGED
WHY
NEW_EVIDENCE_OR_REASONING
```

## INT-LAW-116 — Independência de audiência/comercial

Judgment não deve ser moldado para confirmar o que Marketing, Sales ou direção desejam ouvir.

---

# 13. FUTURO / HORIZON SCANNING

## INT-LAW-120 — Weak signal ≠ forecast

```text
WEAK_SIGNAL != FORECAST
```

## INT-LAW-121 — Forecast ≠ fact

```text
FORECAST != OBSERVED_FACT
```

## INT-LAW-122 — Scenario ≠ prediction

Cenário explora possibilidade; não afirma ocorrência.

## INT-LAW-123 — Future date não cria opportunity

Calendário, expiry, safra ou janela futura isolados não são oportunidade.

## INT-LAW-124 — Radar Futuro consulta corpus relevante

Mesma disciplina de consulta global e estados explícitos por família se aplica ao futuro.

## INT-LAW-125 — Horizon item declara horizonte e incerteza

No mínimo:

- o sinal;
- evidência;
- horizonte temporal;
- impacto potencial;
- grau/causas de incerteza;
- indicadores que fortaleceriam/enfraqueceriam o cenário.

## INT-LAW-126 — História não prova repetição

Pattern histórico pode informar hipótese, não determinar recorrência futura.

---

# 14. FINDING, ATTENTION ITEM E OPPORTUNITY

## INT-LAW-130 — Finding responde uma pergunta analítica

Não criar finding genérico “interessante”.

## INT-LAW-131 — Relevância para decisão é explícita

Finding deve dizer para quem/qual decisão ele importa, sem fabricar ação.

## INT-LAW-132 — Opportunity cruza todas as famílias aplicáveis disponíveis

Preservar estado explícito por família:

```text
MATCH
CROP_ONLY
NOT_FOUND
UNKNOWN
MATERIAL_EXISTENTE_NAO_UTILIZAVEL
```

Taxonomia pode evoluir por contrato, não por implementação silenciosa.

## INT-LAW-133 — Portfolio completeness permanece obrigatório quando aplicável

Para Opportunity comercial ligada a ADAMA, produtos relevantes do país/cultura precisam ser contabilizados conforme contrato vigente.

## INT-LAW-134 — Produto para cultura ≠ produto para alvo

Não chamar “solução” sem relação cultura × alvo provada.

## INT-LAW-135 — Opportunity não nasce de uma fonte estrutural sozinha

Autorização/portfolio/label podem contextualizar; não inventam pressão de campo ou demanda.

## INT-LAW-136 — DAILY_COLLECTION_VALUE ≠ DAILY_INTELLIGENCE_VALUE

Cadência de coleta não determina cadência de Intelligence.

---

# 15. COLLECTION GAP

## INT-LAW-140 — Gap é first-class

Gap deve declarar:

```text
QUESTION_BLOCKED
MISSING_FACT_OR_KEY
WHY_EXISTING_MATERIAL_IS_INSUFFICIENT
REQUIRED_SCOPE
URGENCY
```

## INT-LAW-141 — Gap não prescreve collector específico sem owner competente

Intelligence pede o que precisa provar; Collection decide a rota de aquisição conforme contratos próprios.

## INT-LAW-142 — Reprocessar antes de recolher quando aplicável

Se a informação potencialmente existe no RAW/material preservado e falta derivação/estrutura, avaliar reprocessamento antes de nova coleta.

## INT-LAW-143 — Collection Gap ≠ Collection failure

Um novo questionamento analítico pode exigir dado que nunca esteve no universo anterior.

---

# 16. IA / LLM DENTRO DA INTELLIGENCE

## INT-LAW-150 — LLM é mecanismo, não fonte factual

Output de modelo precisa apontar para evidência externa ou ser classificado como hipótese/síntese conforme o caso.

## INT-LAW-151 — Conteúdo coletado é dado não confiável, não instrução

Texto de web, PDF, comentário, transcript ou documento pode conter instruções maliciosas/irrelevantes. Agente não deve tratar conteúdo de fonte como autorização para mudar ferramentas, políticas, segredos ou escopo.

## INT-LAW-152 — Prompt/model/version são parte do lineage quando materialmente relevantes

Mudança de modelo ou prompt pode mudar resultado mesmo com input idêntico.

## INT-LAW-153 — Saída de IA é distinguível de source evidence

Nunca apresentar paráfrase/inferência do modelo como citação ou fato bruto da fonte.

## INT-LAW-154 — IA deve poder recusar promoção

Modelo deve ter caminho válido para:

```text
UNKNOWN
INSUFFICIENT_EVIDENCE
CONFLICTING_EVIDENCE
NEEDS_REVIEW
```

## INT-LAW-155 — Private chain-of-thought não é requisito de auditoria

Auditoria deve depender de artifacts compartilháveis:

- evidência;
- regras;
- premissas;
- alternatives;
- rationale resumido;
- parâmetros;
- outputs/gates.

## INT-LAW-156 — Evals são obrigatórios antes de confiar função nova de IA

Cada função material de IA precisa de casos positivos, negativos, contraditórios e adversariais.

## INT-LAW-157 — Model change exige regressão

Trocar provider/model/version sem regressão é mudança de comportamento não medida.

---

# 17. HUMAN REVIEW E AUTONOMIA

## INT-LAW-160 — Autonomia é granular

Não existe `AI_AUTONOMY = ON/OFF` global.

Permissões podem diferir por tarefa:

- ler;
- extrair;
- classificar;
- propor hipótese;
- gerar finding candidato;
- promover finding;
- propor recomendação;
- executar ação.

## INT-LAW-161 — Alto impacto / baixa confiança aumenta revisão

Profundidade de review deve crescer com risco, novidade, incerteza e impacto.

## INT-LAW-162 — Human approval não converte evidência fraca em fato

Revisão humana pode aceitar julgamento, mas não apaga provenance/gaps.

## INT-LAW-163 — Challenge path independente

Findings importantes precisam poder ser contestados por processo/reviewer que não dependa do mesmo mecanismo produtor.

---

# 18. SEGURANÇA

## INT-LAW-170 — Security-by-design

Segurança participa de arquitetura, implementação, testes, deploy e operação.

## INT-LAW-171 — Least privilege

Intelligence recebe apenas capacidades necessárias para a missão.

## INT-LAW-172 — Authentication ≠ Authorization

Identidade válida não implica permissão para recurso/ação.

## INT-LAW-173 — READ ≠ DERIVE ≠ WRITE ≠ ACT

Capacidades devem ser separáveis e auditáveis.

## INT-LAW-174 — Default da Intelligence é read/derive-first

Writes operacionais externos não fazem parte do baseline da Intelligence V1.

## INT-LAW-175 — Segredos nunca entram em prompt/artefato sem necessidade e política

Secrets ficam em mecanismo próprio de secret management; nunca em repo, log ou dataset por conveniência.

## INT-LAW-176 — Dados sensíveis seguem minimização e purpose limitation

Só usar informação necessária à pergunta autorizada.

## INT-LAW-177 — Provedor externo não recebe dados automaticamente

Envio a API/modelo externo exige política/contrato de dados compatível.

## INT-LAW-178 — Dependências fazem parte da superfície de risco

Bibliotecas, modelos, serviços, connectors e APIs precisam de inventário e processo de atualização/vulnerabilidade proporcional ao risco.

## INT-LAW-179 — Auditoria de ações é obrigatória

Acesso, mudança de regra, promoção de finding, alteração de permissão e ação futura relevante precisam ser auditáveis.

## INT-LAW-180 — Production não é laboratório

Mudança estrutural segue ambiente descartável/preparação/prova antes de LIVE.

---

# 19. QUALIDADE, OBSERVABILIDADE E SAÚDE

## INT-LAW-190 — Qualidade é contínua

Monitorar, quando mensurável:

- freshness;
- completeness;
- schema/contract drift;
- lineage gaps;
- falhas de family consultation;
- distribuição anômala de estados;
- mudança de comportamento do modelo;
- custo/latência quando relevante.

## INT-LAW-191 — Incidente não vira silêncio

Quando qualidade falha, produzir estado explícito; não esconder item ou apresentar último valor como atual sem marcação.

## INT-LAW-192 — Freshness é contextual

“Velho” depende da pergunta e da janela, não apenas de dias fixos globais.

## INT-LAW-193 — Health não é truth

Pipeline saudável não prova que finding está correto.

## INT-LAW-194 — Truth evaluation e system health são camadas diferentes

Ambas importam e devem ser distinguíveis.

---

# 20. HISTÓRIA, CORREÇÕES E FEEDBACK

## INT-LAW-200 — Histórico é append-only por default

Correção não apaga estado anterior.

## INT-LAW-201 — ACTIVE_STATE pode mudar sem apagar HISTORICAL_STATE

Consumidor precisa saber qual é o estado vigente e como chegou nele.

## INT-LAW-202 — Correção registra causa

Erro de fonte, normalização, lógica, modelo, input ou interpretação devem ser distinguíveis.

## INT-LAW-203 — Feedback posterior não altera retroativamente o julgamento

Outcome posterior serve para calibrar o sistema, não para fingir que o sistema sabia antes.

## INT-LAW-204 — Medir calibração quando houver ground truth legítimo

Confidence buckets e tipos de judgment podem ser comparados ao resultado posterior quando semanticamente válido.

---

# 21. REPROCESSAMENTO, REUSO E MUDANÇA

## INT-LAW-210 — New data e new logic são causas distintas de recomputação

## INT-LAW-211 — Alteração upstream deve permitir localizar downstream afetado

## INT-LAW-212 — Reprocessamento preserva origem

Novo derived não muda identidade/proveniência do material de Collection que o originou.

## INT-LAW-213 — Reprocessar material existente pode fechar gap

Não abrir aquisição nova antes de verificar se o gap é de extração/estrutura.

## INT-LAW-214 — Mudança semântica exige migration/reconciliation explícita

Renomear estado/campo/conceito pode quebrar histórico mesmo sem alterar bytes de evidência.

---

# 22. SYSTEM MAP E CARDS

## INT-LAW-220 — System Map observa Intelligence

```text
SYSTEM MAP != INTELLIGENCE AUTHORITY
```

## INT-LAW-221 — Card != file

Card representa responsabilidade/conceito.

## INT-LAW-222 — Declared ≠ observed no mapa

Capability declarada sem runtime não aparece como provada.

## INT-LAW-223 — Relações analíticas têm tipo próprio

Exemplos a contratar/usar conforme modelo vigente:

```text
SUPPORTS
CONTRADICTS
DERIVED_FROM
DEPENDS_ON
CROSSES_WITH
PROMOTES_TO
VALIDATES
OBSERVES
```

Não comprimir tudo em DATA/CONTROL.

## INT-LAW-224 — Vertical navigation deve chegar à prova

Quando implementado, deve ser possível navegar:

```text
BIBLE / LAW
→ CONTRACT
→ COMPONENT
→ CODE
→ RUN
→ INPUT EVIDENCE
→ OUTPUT FINDING
→ TEST / PROOF
```

Elo ausente permanece `UNKNOWN`.

---

# 23. INTELLIGENCE TOOLS / DELIVERY

## INT-LAW-230 — Tool consome Intelligence; não inventa Intelligence

## INT-LAW-231 — Ferramenta só nasce quando pergunta + usuário + valor são provados

“Temos dados” não justifica ferramenta.

## INT-LAW-232 — Uma capability pode existir sem virar tool

Alguns mecanismos devem permanecer internos/guardrails.

## INT-LAW-233 — Ask Sintonia não recebe bypass epistemológico

Interface conversacional segue os mesmos gates, provenance e estados da Intelligence.

## INT-LAW-234 — Explicabilidade mínima acompanha saída

Consumidor precisa conseguir descobrir:

- por que apareceu;
- quais fatos sustentam;
- o que é incerto;
- qual janela/escopo;
- o que mudaria o judgment.

---

# 24. AVALIAÇÃO

## INT-LAW-240 — “Parece bom” não é eval

Avaliação precisa de fixtures/casos e critérios.

## INT-LAW-241 — Métricas recomendadas

Conforme se tornem mensuráveis:

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

## INT-LAW-242 — Métrica inexistente = NOT_MEASURED

Não fabricar baseline.

## INT-LAW-243 — Golden cases não bastam

Incluir adversarial/negative fixtures.

## INT-LAW-244 — Casos-testemunha maduros permanecem regressão

Exemplos do Motor V2 podem continuar fixtures quando aplicáveis, mas devem ser medidos contra dados atuais antes de qualquer afirmação quantitativa.

---

# 25. RED TEAM MÍNIMO

Toda implementação material de Intelligence deve ser atacada, conforme aplicável, contra:

```text
RT-INT-01  duplicar evidência em famílias diferentes para inflar convergência
RT-INT-02  usar sidebar/menu como corpo
RT-INT-03  SOURCE_LOCATION → FACT_LOCATION
RT-INT-04  PUBLICATION_TIME → FACT_TIME
RT-INT-05  NOT_FOUND → ZERO_PROVED sem universo
RT-INT-06  fato antigo → ACT_NOW
RT-INT-07  identidade → expertise
RT-INT-08  catálogo/registro → sinal de campo independente
RT-INT-09  family existente mas não consultada → gate PASS
RT-INT-10  ocultar contradictory evidence
RT-INT-11  output LLM sem support edge → FACT
RT-INT-12  modelo/prompt mudou → reuso silencioso
RT-INT-13  permissão read/analyze → write/action
RT-INT-14  correção → apagar finding histórico
RT-INT-15  data futura → forecast/opportunity
RT-INT-16  crossing sem join key factual
RT-INT-17  input vazio → PASS
RT-INT-18  múltiplas validações dependentes → score de independência alto
RT-INT-19  múltiplas cópias da mesma origem → hipótese promovida
RT-INT-20  finding sem reprodução de input + lógica + gates
RT-INT-21  portal reconstrói relação que motor não produziu
RT-INT-22  Collection Gap chama collector direto
RT-INT-23  UNKNOWN desaparece na renderização
RT-INT-24  factualidade correta mas geografia/tempo incompatíveis → oportunidade
```

Ataque só conta quando mutação realmente atingiu o alvo e teardown restaurou o estado inicial.

---

# 26. GATES MÍNIMOS DE UMA FUTURA INTELLIGENCE V1

Antes de `INTELLIGENCE_V1_READY = YES`, exigir contratos/provas equivalentes a:

```text
WAITING_ROOM_INPUT_BOUNDARY          = PASS
INTELLIGENCE_RUN_IDENTITY            = PASS
CLAIM_IDENTITY                       = PASS
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

## INT-LAW-260 — Gates críticos precisam saber falhar

Provar pelo menos falhas de:

- input vazio;
- missing file/input;
- duplicate claim;
- missing provenance;
- contradictory state;
- unknown escondido;
- universe mismatch;
- dependency inflation;
- stale actionability;
- unauthorized capability.

---

# 27. DEFINIÇÃO DE “INTELLIGENCE V1 PRONTA”

Intelligence V1 pode ser considerada pronta quando, para perguntas aprovadas e escopo declarado, a máquina consegue repetivelmente:

1. receber apenas material admissível da Sala de Espera;
2. abrir um Intelligence Run identificável;
3. resolver entidades/claims necessárias sem fabricar identidade;
4. construir lineage de evidência;
5. distinguir dependência/independência;
6. executar crossings com chaves provadas;
7. preservar tempo/geografia/proveniência;
8. produzir signal/finding/opportunity ou recusa epistemológica explícita;
9. declarar incerteza, premissas e evidência contrária quando material;
10. detectar Collection Gap e devolvê-lo à Collection canônica;
11. preservar histórico/reprocessamento;
12. passar red team e regressão;
13. expor resultados a ferramentas sem o portal reconstruir a lógica;
14. operar com controles de segurança e auditoria proporcionais ao risco.

“Pronta” não significa prever tudo, nem encontrar oportunidade todo dia.

---

# 28. PROIBIÇÕES ABSOLUTAS

```text
INTELLIGENCE MUST NOT COLLECT DIRECTLY.
INTELLIGENCE MUST NOT FABRICATE SOURCE_ID OR DOCUMENT_ID.
INTELLIGENCE MUST NOT TURN UNKNOWN INTO FACT.
INTELLIGENCE MUST NOT TURN NOT_FOUND INTO ZERO WITHOUT A DECLARED UNIVERSE.
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

# 29. BENCHMARKS QUE INFORMARAM V0.1

Esta Bíblia foi sintetizada de:

## Evidência e leis internas

- `docs/refresh/FINAL-INTELLIGENCE-REFRESH-EAME.md`
- `docs/red-team/C-SNAPSHOT-DE-INTELIGENCIA-EAME.md`
- `docs/intelligence/MOTOR-INTELLIGENCE-V2-REQUIREMENTS.md`
- leis maduras de identidade, tempo, geografia, procedência, prova e Collection do SINTONIA.

## Referências externas de engenharia

- Databricks Unity Catalog — governance, lineage, data quality;
- Palantir Foundry/Ontology — data + logic + action + security e decision lineage;
- OpenLineage — Run/Job/Dataset e lineage explícito;
- W3C PROV-O — provenance interoperável;
- OpenMetadata — lineage, quality, incidents e observabilidade;
- Dagster/dbt — asset/state-aware engineering, observabilidade e testabilidade;
- ODNI ICD 203 — analytic standards;
- CIA Structured Analytic Techniques — análise estruturada e mitigação de vieses;
- UK Government Office for Science Futures Toolkit — horizon scanning e futuros sob incerteza;
- NIST AI RMF / GenAI Profile — risco de IA ao longo do lifecycle;
- NIST SSDF — desenvolvimento seguro integrado ao SDLC;
- NIST Zero Trust — ausência de confiança implícita e autorização por recurso/identidade.

Detalhes e URLs estão em:

`research/intelligence/BENCHMARK-DE-ENGENHARIA-DA-INTELLIGENCE-2026-09-13.md`

Benchmark não é autoridade. Esta Bíblia só incorpora princípios que foram reconciliados com as leis e provas do SINTONIA.

---

# 30. PROMOÇÃO PARA CANONICAL

Esta V0.1 só pode mudar de:

```text
CANDIDATE_FOR_CANONICAL_REVIEW
```

para:

```text
CANONICAL
```

após, no mínimo:

1. reconciliar com a Bíblia da Collection vigente;
2. reconciliar com contratos de Intelligence já existentes;
3. resolver colisões de owner com `MOTOR-INTELLIGENCE-V2-REQUIREMENTS.md` — este deve virar contrato subordinado/referenciado, não segunda Bíblia concorrente;
4. registrar a autoridade na Sala de Controle/registry canônico;
5. integrar em snapshot onde a autoridade não fique presa a branch lateral invisível;
6. executar governance gate;
7. atualizar System Map por cadeia canônica, sem edição manual de gerados;
8. registrar o delta no Know-how canônico;
9. aprovação explícita da promoção.

Até lá:

```text
INTELLIGENCE_BIBLE_STATUS = CANDIDATE
```

---

# 31. PRIMEIRA MISSÃO APÓS PROMOÇÃO — NÃO EXECUTAR AGORA

A primeira missão futura não deve ser “construir o motor inteiro”.

Ela deve responder uma única pergunta:

> Qual é o **contrato mínimo de entrada/saída e identidade** de um `INTELLIGENCE_RUN` consumindo um item real da Sala de Espera, sem produzir Opportunity ainda?

Gate sugerido:

```text
ONE REAL WAITING_ROOM ITEM
→ ONE IDENTIFIED INTELLIGENCE_RUN
→ PROVEN INPUT LINEAGE
→ NO DIRECT COLLECTION
→ NO JUDGMENT FABRICATION
```

Depois HARD STOP.

---

# 32. VEREDITO DA BÍBLIA V0.1

```text
ENGINEERING_BIBLE_WRITTEN = YES
CANONICAL = NO
RUNTIME_IMPLEMENTED = NO
COLLECTION_CHANGED = NO
INTELLIGENCE_IMPLEMENTATION_STARTED = NO
PORTAL_CHANGED = NO
LIVE_CHANGED = NO
```

A Intelligence do SINTONIA deve ser uma **máquina de produção analítica auditável**.

Ela não ganha qualidade por falar com mais confiança.

Ela ganha qualidade quando consegue provar:

```text
O QUE SABE
POR QUE SABE
DE ONDE VEIO
O QUE DEPENDE DA MESMA ORIGEM
O QUE É PREMISSA
O QUE É INCERTO
O QUE CONTRADIZ
QUAL É A JANELA
QUAL É O ESCOPO
O QUE MUDARIA O JULGAMENTO
E QUANDO A RESPOSTA CORRETA É NÃO AGIR AINDA
```

---

`KNOW_HOW_DELTA = ATUALIZAÇÃO NECESSÁRIA APÓS PROMOÇÃO/INTEGRAÇÃO`

**HARD STOP — esta Bíblia não autoriza iniciar a implementação da Intelligence.**