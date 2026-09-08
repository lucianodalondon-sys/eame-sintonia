# PESQUISA COMPARATIVA — SISTEMAS DE INTELIGÊNCIA E DE ENTREGA

```
DOCUMENT_STATUS   DRAFT
DOCUMENT_TYPE     CORE CONSTITUTION · fundamentação externa
RESEARCH_DATE     2026-09-08
IMPLEMENTATION    NONE
```

> **Regra desta pesquisa:** primeiro estudou-se o SINTONIA real, medido no código.
> Só depois se olhou para fora. Nenhum padrão externo entra por ser famoso.
>
> Cada ficha responde a **cinco perguntas**, e a quinta é a que mais importa:
> `SOURCE` · `URL` · `DATE` · `WHAT IT TEACHES` · **`WHAT DOES NOT TRANSFER`**.

---

## §0 · O QUE JÁ ESTAVA CERTO ANTES DE OLHAR PARA FORA

Antes das fichas, o resultado mais importante desta pesquisa:

**O SINTONIA já implementa, sem lhes chamar nomes, cinco padrões que a indústria
formalizou.** A pesquisa externa serviu sobretudo para **nomear** e para **encontrar as
duas ou três coisas que faltam**, não para importar arquitetura.

| padrão da indústria | onde já vive no SINTONIA, medido |
|---|---|
| Materialized View | `italy-handoff-v21.js`, regerado byte-idêntico por `site_v21_ingest.py` |
| Anti-Corruption Layer | `DISPLAY-LAYER-V1.json` — 103 regras entre o enum de máquina e a frase de ecrã |
| Ontology / semantic layer | `MODELO-DE-IDENTIDADE-EAME.md`, 7 entidades; `AM.cropResolve` como dona única da tabela de sinónimos |
| Intelligence Card | a ficha de oportunidade: `FACTS` · `CONNECTIONS` · `UNKNOWN` · `WHY_IT_MAY_MATTER` · `EVIDENCE` |
| Analytic tradecraft | separação `FACT` / `INTERPRETATION` / `ACTION`, e a régua de confiança em 9 dimensões |

---

## §1 · PALANTIR FOUNDRY — Ontology, Workshop, Object Views, Actions

```
SOURCE   Palantir Foundry — Ontology overview · Object Views overview
URL      https://www.palantir.com/docs/foundry/ontology/overview
         https://www.palantir.com/docs/foundry/object-views/overview
DATE     consultado 2026-09-08
```

### O que ensina

**1 · A ontologia separa-se em camada semântica e camada cinética.**
A *semântica* são `object types`, `link types` e `properties`; a *cinética* são
`action types` e `functions`. A documentação é explícita quanto ao ponto que interessa:
*«The Ontology sits on top of the digital assets integrated into the Palantir platform
(datasets, virtual tables, and models) and connects them to their real-world
counterparts.»*

**2 · As aplicações falam com a ontologia, nunca com os dados de origem.**
Workshop, Object Explorer e Object Views interagem com o modelo semântico unificado, não
com o *source data*. **É exatamente a fronteira `INTELLIGENCE ≠ CASCO` do §3 da Bíblia**,
implementada num produto comercial e a funcionar há anos.

**3 · Object Views — o mesmo objeto, vistas diferentes por fluxo de trabalho.**
Há *standard object views* (automáticas, do próprio tipo) e *configured object views*
(«fully customizable representations built using Workshop that you can configure to
provide contextualized experiences for specific workflows»). E há dois formatos: *full*
e *panel* — a mesma entidade como página inteira ou como painel embebido noutra
aplicação.

> **Isto é a confirmação industrial da cardinalidade M:N do §6 da Bíblia.**
> Um objeto, muitas vistas, por fluxo de trabalho e por papel — e **não** uma tela por
> departamento. É o padrão que o `L-16 · USER ROLE ≠ TOOL` descreve.

**4 · A separação `full` × `panel` valida a distinção `TOOL` × `SUPPORTING_VIEW`.**
Uma *panel view* é a mesma inteligência a servir a decisão de outra superfície. É
literalmente o papel que a Bíblia atribui a `Portfolio` dentro de `Opportunity Radar`.

### O que NÃO transfere

| não transfere | porquê |
|---|---|
| **Actions** — a camada cinética | O SINTONIA é `EXTERNAL-ONLY` por decisão do cliente (`P-003`, resolvida: *nenhum dado interno da ADAMA*). Não há sistema onde escrever. A camada cinética do SINTONIA é **a decisão da pessoa**, e ela vive fora do produto |
| **Ontology como banco operacional** | Foundry assume dados internos, escrita e permissões de escrita. Aqui a ontologia é de **factos públicos observados** — e a lei de identidade é mais rígida: `D-021`, «só APONTA», nunca cria segunda verdade |
| **Workshop como forma de construir telas** | é uma escolha de fornecedor; o casco do SINTONIA é HTML servido estático, e isso é uma vantagem: 12 portões executáveis correm sobre ele |
| **A palavra «Ontology» como marca** | o repositório já tem `MODELO-DE-IDENTIDADE-EAME.md` com 7 entidades. Renomear não acrescenta |

---

## §2 · RECORDED FUTURE — Intelligence Cards

```
SOURCE   Recorded Future — «Inside the Recorded Future Intelligence Card»
URL      https://www.recordedfuture.com/blog/intel-cards-overview
DATE     consultado 2026-09-08
```

### O que ensina

**1 · A unidade de entrega é a ENTIDADE, não o relatório.**
Um Intelligence Card é sobre uma entidade (IP, domínio, hash, CVE, malware, ator) e
funciona como **ponto de pivô**: *«Intelligence Cards can act as pivot points during your
assessment of an entity's criticality.»*

**2 · Toda regra de risco carrega a evidência que a disparou.**
*«Each risk rule trigger is based on specific, collected evidence and the sources are made
available in the Intelligence Card for further examination, ensuring transparency of
information.»*

> **É a lei `EVIDENCE_REQUIREMENT` do Product Contract**, e é a mesma disciplina do
> `EvidenceLink` do `CONTRATO-DE-DESIGN §5`: *todo número tem um*.

**3 · A ficha tem secções fixas.** Heading (nome exato + pseudónimos), risco, listas,
*timelines*, entidades relacionadas, perfil técnico. **Ordem fixa, blocos que não
desaparecem por estarem vazios** — que é textualmente a regra `CASE_DETAIL` do
`DESIGN-DATA-CONTRACT-V1`: *«ordem fixa; nenhum bloco omitido por estar vazio»*.

### O que NÃO transfere

| não transfere | porquê |
|---|---|
| **O RISK SCORE 0–99** | É o oposto do que este repositório decidiu, e a decisão está escrita: `RADAR-DO-FUTURO-CONTRACT-V1 §POR_QUE_SEM_SCORE` — *«um número único esconde qual camada sustenta o tema. Estados discretos obrigam a dizer qual perna existe.»* E a arquitetura proíbe explicitamente somar registo + anúncio + comunicação + atividade técnica num indicador |
| **As bandas «Very Malicious / Malicious / Suspicious»** | são um espaço de risco binário (bom/mau). No agro não existe: uma janela colturale aberta não é «má», e `ACT_NOW` **não ganha vermelho de alarme** — há um em dezoito linhas e é regulatório |
| **A cadência de segundos** | o relógio do agro é a safra. `COMPETITOR OBSERVATION CLOCK` mede meses |

> **O que transfere é a transparência da regra, não o número que ela produz.**

---

## §3 · DATAMINR — deteção em tempo real e briefings que se regeneram

```
SOURCE   Dataminr — First Alert · ReGenAI
URL      https://www.dataminr.com/products/first-alert/
DATE     consultado 2026-09-08
```

### O que ensina

**1 · Um evento evolui, e o artefacto de entrega evolui com ele.**
O ReGenAI *regenera briefings de evento em tempo real à medida que o evento se desenrola*.
**Isto é `§13 · SUPERSESSÃO` visto do lado do produto**: a ficha não é imutável — é
**versionada e substituída**, e o leitor tem de poder ver que mudou.

**2 · A previsão assenta em arquivo histórico.** As previsões de evolução baseiam-se em
padrões de mais de 10 anos de arquivo. **Confirma, de fora, a lei que este repositório já
paga:** *sem baseline, nada de «rises»*.

### O que NÃO transfere

| não transfere | porquê |
|---|---|
| **A previsão de evolução** | medido aqui, no backtest: **1 safra de antecedência no melhor caso, zero em dois de três**. Só o regulatório antecipa, e porque a data é publicada. Sem 10 anos de arquivo comparável, prever é inventar |
| **O «first alert» como promessa** | a régua de alerta deste repositório não abre a porta `BASELINE` em nenhuma família de conversa pública. Hoje o SINTONIA **não pode emitir `ALERT`**. Pode `WATCH` e `INVESTIGATE`. *«Chamar qualquer um dos dois de alerta seria vender feed como inteligência»* |
| **Multi-Modal Fusion como argumento** | fundir modalidades é exatamente o que a arquitetura proíbe: quatro observações de naturezas diferentes não se somam, porque o número esconderia **qual** delas está a acontecer |

> **A lição invertida, e é a mais útil das três:**
> um produto de *tempo real* torna o frescor visível por necessidade. Um produto de
> **ciclo de safra** tem de o tornar visível **por disciplina**, porque nada na
> experiência o obriga. Daí o §12.

---

## §4 · ALPHASENSE — entrega de pesquisa com citação ao nível da frase

```
SOURCE   AlphaSense — Smart Summaries
URL      https://www.alpha-sense.com/platform/smart-summaries/
DATE     consultado 2026-09-08
```

### O que ensina

**1 · Citação profunda, ao nível do trecho.** Cada afirmação de um resumo é clicável e
leva ao *snippet* exato do documento, chamada de conferência ou transcrição de onde saiu.

> **É a norma que a Bíblia adota para o `Ask Sintonia` (§11.2 A-03) e para o
> `EvidenceLink`.** E é atingível aqui: o payload de Label Intelligence já guarda a
> citação literal do PDF **e verifica que ela existe no documento** (regra R-18), com
> leitura em três modos de `pdftotext`.

**2 · A verificação é o produto, não um extra.** O argumento comercial é *«validate any
insight instantly»* — a capacidade de auditar é o que faz o resumo utilizável.

### O que NÃO transfere

| não transfere | porquê |
|---|---|
| **«no hallucinations» como afirmação** | é uma afirmação sobre um sistema generativo que nenhum portão pode provar. Aqui o equivalente medido e provável é outro: o benchmark do Ask tem **`WRONG ANSWER = 0`** e **14 recusas corretas** — porque a camada é determinística, não generativa. *«Não é chat. É consulta determinística sobre evidência preservada»* |
| **O sumário como unidade** | um sumário é uma projeção de leitura, não um Intelligence Product. Aqui a unidade é o **envelope versionado com `FORBIDDEN_CLAIMS`** |
| **A escala de fontes (10.000+)** | contar fontes é o que a home proíbe pelo nome |

---

## §5 · OPENCTI — confiança, fiabilidade e resolução de conflito

```
SOURCE   OpenCTI docs — Reliability and confidence
URL      https://docs.opencti.io/latest/usage/reliability-confidence/
DATE     consultado 2026-09-08
```

### O que ensina — e é a importação mais direta desta pesquisa

**1 · Fiabilidade da FONTE e credibilidade da INFORMAÇÃO são eixos distintos.**
Fiabilidade usa o *Admiralty Code* da NATO e mede a confiança na fonte, «based on the
technical capabilities or history of the source». Confiança mede a informação em si.

> **Mapeia quase um-para-um na régua de confiança de 9 dimensões que já existe:**
> `SOURCE QUALITY` é fiabilidade; `DIRECTNESS`, `INDEPENDENCE`, `NORMALIZATION CONFIDENCE`
> e `CONTRADICTION` são credibilidade.

**2 · A LEI DA MENOR CONFIANÇA.**
*«When 2 confidence levels are possible, we would always take the lowest one.»*

> **Adotada literalmente como `§5.3 L-CONF`:** um produto composto herda a **menor**
> confiança dos seus componentes **e nomeia qual componente a determinou**.
> Já existia uma versão disto no repositório sem estar escrita como lei: a
> `MOLECULE WATCH` declara «HIGH quando casou por CAS ou nome exato; **LOW** quando casou
> por sal ou fuzzy — e o método precisa de aparecer».

**3 · Confiança como controlo de escrita.** Um utilizador com confiança máxima baixa não
pode sobrescrever conhecimento de confiança alta.

### O que NÃO transfere

| não transfere | porquê |
|---|---|
| **Confiança como permissão de escrita** | no SINTONIA ninguém escreve pela interface. A escrita vive nos geradores, com sha e portão |
| **A escala Admiralty de 6 níveis** | seria um vocabulário paralelo à régua de 9 dimensões que já existe e que é **verificável dimensão a dimensão**. Uma letra A-F é mais compacta e menos auditável |
| **STIX como formato de troca** | o SINTONIA não troca inteligência com terceiros. Adotar STIX seria pagar um custo de conformidade sem consumidor |

---

## §6 · MISP — eventos, objetos, taxonomias e *sightings*

```
SOURCE   MISP Project — Data models
URL      https://www.misp-project.org/datamodels/
DATE     consultado 2026-09-08
```

### O que ensina

**1 · Vocabulário controlado separado do dado.** As *taxonomies* são «a set of already
defined classifications modeling estimative language, CSIRTs/CERTs classifications,
national classifications or threat model classification».

> **É o `X-007-canonical-agro-dictionary.json` e o `EPPO NORMALIZER` deste repositório** —
> e é a razão pela qual o `EPPO NORMALIZER` é declarado **infraestrutura, não tela**:
> *«sem isto não existe visão EAME — existem três visões nacionais soltas»*.

**2 · *Sighting* — «vi isto, aqui, agora» é um facto distinto do indicador.**
Um indicador é uma coisa; a observação de que ele apareceu num sítio e num momento é outra.

> **Esta é a distinção que falta em `Field Voices`.**
> 79 vozes não são 79 factos sobre o campo: são 79 *sightings*. E um *sighting* precisa
> de **denominador** — 79 de quantos? — que é exatamente o `UNKNOWN` que bloqueia S-07.
> `AD-18` já paga a lição noutro contexto: `CENSO E AMOSTRA NÃO SÃO A MESMA AUSÊNCIA`.

**3 · Níveis de distribuição por objeto.** Cada *cluster* carrega a sua regra de partilha.
Corresponde ao `SECURITY` e ao `CLIENT_SAFE` do Product Contract — e o repositório já o
usa: **8 de 577 atividades de concorrente estão retidas por `CLIENT_SAFE = false`**.

### O que NÃO transfere

| não transfere | porquê |
|---|---|
| **Partilha entre comunidades** | não há comunidade. A partilha é ADAMA-interna |
| **Galaxies / clusters de ator** | o modelo de identidade daqui é de **empresas e registos regulatórios**, com regras societárias explícitas — `D-024` recusa agrupar razões sociais antecessoras, e **conta-as** |

---

## §7 · IBM i2 E O FLUXO DE TRABALHO DO ANALISTA

```
SOURCE   literatura de análise de ligações e de fluxo de trabalho analítico
DATE     consultado 2026-09-08 · fonte secundária, declarado
```

### O que ensina

O padrão de **investigação por expansão a partir de uma entidade**: começar num nó,
expandir ligações, marcar o que interessa, e produzir um artefacto.

> **É a `INVESTIGATION_VIEW` da §10 da Bíblia**, e é a classe correta para o `Archive`
> (1114) e para o `Competitor Watch` como camada. Não são ferramentas de decisão: são
> superfícies de varrimento.

### O que NÃO transfere

A expansão livre de grafo. Aqui **a ligação é declarada, não adivinhada** — regra medida:
*«O ligame é declarado, não adivinhado. Onde a coppia não se resolve, o bloco não procura
— declara que não pode procurar.»* E `issueIds` está vazio em 577/577, pelo que ligar
concorrente a alvo por texto livre seria a *juntura frágil* que o controlo A3 proíbe.

> **`FONTE SECUNDÁRIA` — esta ficha não assenta em documentação primária consultada.
> É a mais fraca das dez, e fica declarada como tal.**

---

## §8 · CQRS

```
SOURCE   Martin Fowler — CQRS
URL      https://martinfowler.com/bliki/CQRS.html
DATE     consultado 2026-09-08
```

### O que ensina

*«CQRS stands for Command Query Responsibility Segregation»* — modelos separados para
atualizar e para ler.

### O que NÃO transfere — e este é o caso em que o aviso vale mais do que o padrão

Fowler é invulgarmente direto:

> *«you should be very cautious about using CQRS»*
> *«the majority of cases I've run into have not been so good, with CQRS seen as a
> significant force for getting a software system into serious difficulties»*
> *«Many systems do fit a CRUD mental model, and so should be done in that style.»*

| não transfere | porquê |
|---|---|
| **O *command model*** | o casco do SINTONIA **não escreve**. Metade do padrão não tem contraparte |
| **CQRS aplicado ao sistema inteiro** | Fowler limita-o a *bounded contexts*. Aqui o *bounded context* é a entrega, e ela já é só-leitura por construção |
| **O nome** | chamar `READ MODEL` aos potes importaria a expectativa de um *write model* que não existe. **É a razão principal pela qual a Bíblia escolheu `DELIVERY_PROJECTION` e não `TOOL READ MODEL`** |

**O que transfere:** a *ideia* de que a forma de leitura é legitimamente diferente da
forma de origem, e que essa diferença é desenho, não dívida.

---

## §9 · MATERIALIZED VIEW — o padrão que dá a lei dos «potes»

```
SOURCE   Microsoft Azure Architecture Center — Materialized View pattern
URL      https://learn.microsoft.com/en-us/azure/architecture/patterns/materialized-view
DATE     documento datado 2022-07-28 · consultado 2026-09-08
```

### O que ensina — a citação que vira lei constitucional

> *«A key point is that a materialized view and the data it contains is **completely
> disposable** because it can be **entirely rebuilt from the source data stores**.
> A materialized view is **never updated directly by an application**, and so it's a
> specialized cache.»*

Três propriedades, e as três são exatamente o que o dono quer dizer com «pote»:

```
P-01  descartável e reconstruível        →  POTE ≠ SOURCE OF TRUTH
P-02  nenhuma aplicação escreve nela     →  o casco não escreve
P-03  é uma cache especializada          →  não é um segundo original
```

E os avisos do padrão mapeiam nas leis que faltavam:

| aviso do padrão | lei que gera |
|---|---|
| «consider the impact on data consistency … the copy won't be fully consistent with the original» | **`AS_OF` é obrigatório.** Uma projeção sem `AS_OF` não sabe a que pergunta responde |
| «materialized views tend to be tailored to one, or a small number of queries» | **uma projeção por superfície é normal, não duplicação.** É o oposto de `AP-06 · TOOL PER DATASET` |
| «a view can be rebuilt if lost … it can be stored in a less reliable location» | **`IS_SOURCE_OF_TRUTH = false` é uma constante, e existe para ser lida** |
| «how and when the view will be updated … a scheduled task, an external trigger, or a manual action» | **`REBUILD_COMMAND` é campo obrigatório da ficha da projeção** |

### O que NÃO transfere

O foco em **desempenho**. Aqui a projeção não existe para acelerar consulta: existe para
**impedir que o casco recalcule inteligência**. O ganho é de autoridade, não de latência.

> **Adotado com uma exigência a mais que o padrão não tem:**
> `P-04 · a regeneração é PROVADA, não assumida — byte a byte, por portão.`
> Já implementado: `site_v21_ingest.py` produz artefacto byte-idêntico com o portão de
> proveniência ligado; `etichette-gate.mjs` recalcula o `CONTENT_SHA256`.

---

## §10 · EVENT SOURCING

```
SOURCE   Martin Fowler — Event Sourcing
URL      https://martinfowler.com/eaaDev/EventSourcing.html
DATE     consultado 2026-09-08
```

### O que ensina

*«Capture all changes to an application state as a sequence of events.»* Daí decorre
*«we can determine the application state at any point in time»*, e a capacidade de
corrigir o passado: *«if we find a past event was incorrect, we can compute the
consequences by reversing it and later events and then replaying the new event.»*

> **A segunda citação é `§13 · CORRECTS` e `INVALIDATES` da Bíblia**, e é exatamente o
> que `V-01` exige: *uma afirmação retratada é corrigida no lugar onde estava, com a data
> e o motivo — não apagada.*

### O que NÃO transfere

Fowler avisa: *«it's not a natural choice and to use it means that you expect to get some
form of return.»*

| não transfere | porquê |
|---|---|
| **Event store como fundação** | o SINTONIA resolve o mesmo problema com **snapshots versionados com sha**, e resolve-o melhor para o seu caso: o `CHANGE EVENT` nasce de **comparar duas versões arquivadas do mesmo documento público**, não de um log interno |
| **Replay** | «external systems don't understand replays». Aqui os sistemas externos são **fontes oficiais que não se podem re-executar**: o ROPF publica só o último trâmite. Medido: **4 das 5 renomeações já seriam invisíveis hoje** — *«o arquivo não é redundância da fonte: em quatro casos de cinco, é a ÚNICA rota»* |

> **A lição transferida em uma linha:**
> o SINTONIA não faz *event sourcing* do seu estado; faz **arquivo versionado da
> realidade externa**. É mais barato e é o único que funciona quando a fonte sobrescreve
> o seu próprio passado.

---

## §11 · BACKEND FOR FRONTEND

```
SOURCE   Sam Newman — Backends For Frontends
URL      https://samnewman.io/patterns/architectural/bff/
DATE     padrão de 2015 · consultado 2026-09-08
```

### O que ensina

Um *backend* por experiência de utilizador, em vez de uma API genérica. O BFF está
acoplado a uma experiência e é mantido pela mesma equipa que a interface.

> **É a justificação de engenharia para «uma projeção por superfície».**
> Um modelo único que servisse as 12 superfícies teria de ser o superconjunto de todas —
> e um superconjunto é precisamente onde nasce o `AP-06 · TOOL PER DATASET`.

### O que NÃO transfere

| não transfere | porquê |
|---|---|
| **Um serviço por BFF** | são ficheiros gerados, não serviços. O custo operacional do padrão não se paga aqui |
| **«mantido pela equipa da UI»** | seria a porta aberta para a UI decidir a semântica. **A projeção é gerada pelo lado da inteligência e o casco só a lê** — é `L-11` |

---

## §12 · ANTI-CORRUPTION LAYER

```
SOURCE   Microsoft Azure Architecture Center — Anti-Corruption Layer pattern
         (Eric Evans, Domain-Driven Design)
URL      https://learn.microsoft.com/en-us/azure/architecture/patterns/anti-corruption-layer
DATE     documento atualizado 2026-05-28 · consultado 2026-09-08
```

### O que ensina

> *«Isolate the different subsystems by placing an anti-corruption layer between them.
> This layer translates communication between the two systems.»*
> E o aviso: *«Avoid placing business rules or orchestration in the layer.»*

### Onde já vive no SINTONIA

**`DISPLAY-LAYER-V1.json` é uma ACL, escrita antes de alguém lhe chamar isso.** 103
regras entre o enum de máquina (maiúsculas, sem acentos, por segurança de codificação) e
a frase de ecrã. E carrega a regra que o padrão exige e não formula tão bem:

> *«Nenhuma tradução pode mudar o que o campo afirma. Uma frase de exibição só pode ser
> **MAIS EXPLÍCITA** que o enum, **nunca mais conclusiva**.»*

Isso é o *«avoid placing business rules in the layer»* dito com precisão semântica em vez
de arquitetural. **O SINTONIA tem aqui uma formulação melhor do que a fonte.**

### O que NÃO transfere

A ACL como estratégia de migração temporária. Aqui a camada é **permanente por
construção**: enquanto houver enum de máquina e leitor humano, há tradução — e a
tradução é um lugar onde a verdade pode escorregar.

---

## §13 · ICD 203 — *Analytic Standards*

```
SOURCE   Intelligence Community Directive 203 — Analytic Standards (ODNI)
URL      https://www.intelligence.gov/assets/documents/intelligence-community-directives/ICD_203.pdf
         (texto de referência consultado em https://github.com/wesinator/ICD203-intel-analysis)
DATE     consultado 2026-09-08
```

### O que ensina — a norma mais importante desta pesquisa

**1 · Léxico fechado de probabilidade, com bandas.** Duas fileiras de sete termos, com
percentagens declaradas — e o aviso de que *«analysts are strongly encouraged not to mix
terms from different rows»*.

**2 · A proibição que vira lei:**
> *«products that express an analyst's confidence … using a "confidence level" … must not
> combine a confidence level and a degree of likelihood … in the same sentence»*

**3 · A distinção que ela protege.** A probabilidade é sobre **o mundo**. A confiança é
sobre **a nossa base de evidência**. «Muito provável, com baixa confiança» é uma frase
coerente e informativa; colapsá-las destrói a informação.

> **Adotado inteiro em `§5.2`, com uma restrição a mais que a ICD 203 não tem:**
> `LIKELIHOOD` só existe sobre produto cuja evidência sustente uma **série**.
> Sem série, `LIKELIHOOD = NOT_ASSESSABLE`.
> Consequência declarada: **hoje nenhuma família do SINTONIA pode emitir `LIKELIHOOD`
> exceto a regulatória** — e essa não precisa, porque a data é publicada.

### O que NÃO transfere

| não transfere | porquê |
|---|---|
| **A obrigação de emitir juízo** | a IC produz avaliações porque o decisor as pede. Aqui `NÃO SEI` é resposta válida e obrigatória, e o benchmark do Ask trata **14 recusas corretas como resultado positivo** |
| **A cadeia de comando como fonte de autoridade** | aqui a autoridade é **documental**: um documento nomeado e datado, ou `UNKNOWN` |
| **O vocabulário em inglês na interface** | o `DISPLAY-LAYER` decide a frase por idioma; o enum é a lei |

---

## §14 · FEATURE / PRODUCT LIFECYCLE — *toggles* e dívida de inventário

```
SOURCE   Pete Hodgson (martinfowler.com) — Feature Toggles
URL      https://martinfowler.com/articles/feature-toggles.html
DATE     consultado 2026-09-08
```

### O que ensina

Quatro categorias, com longevidade e dinamismo diferentes: *release* (dias a semanas),
*experiment* (horas a semanas), *ops* (curto, alguns permanentes como *kill switch*),
*permissioning* (anos).

E a lição de gestão:
> *«Savvy teams view their Feature Toggles in their codebase as inventory which comes with
> a carrying cost and seek to keep that inventory as low as possible.»*
> Estratégias: tarefas automáticas de remoção, datas de expiração, *time bombs* que
> reprovam testes, e um limite ao número simultâneo.

### O que transfere — e é mais forte do que parece

> **Uma superfície `EXPERIMENT` ou `EXPLORATORY_TOOL` é inventário com custo de posse.**
> Sem data de expiração, todo estado temporário torna-se permanente por omissão.

Daí duas leis para o §9 da Bíblia:

```
LC-04  Todo estado EXPLORATORY, PILOT ou EXPERIMENT carrega uma DATA DE REVISÃO.
       Chegada a data, ou promove, ou rebaixa, ou reafirma com motivo novo.
LC-05  Uma superfície DEPRECATED carrega a data em que sai.
       «Deprecated» sem data é «current» com má consciência.
```

**Precedente medido de que a ausência disto custa:** as vistas `case` e `brief`
continuam a renderizar, com `legacyCaseId` a resolver **0 de 43** — legado sem data de
saída, e portanto sem saída.

### O que NÃO transfere

*Toggles* por pedido e coortes de utilizador. O SINTONIA não tem sessão com coorte, e o
`PILOT` aqui significa **utilizadores nomeados a decidir com a ferramenta**, não tráfego
dividido.

---

## §15 · DECISION INTELLIGENCE E SISTEMAS DE DECISÃO AUDITÁVEIS

```
SOURCE   corpo de literatura sobre decision intelligence e auditabilidade
DATE     consultado 2026-09-08 · síntese, declarada como tal
```

### O que ensina

A disciplina insiste em ligar **decisão → ação → resultado**, e não em produzir *insight*.
Um sistema auditável tem de conseguir reconstruir **que informação estava disponível no
momento da decisão** — não a informação de hoje.

> **É a razão do `AS_OF` e do `PASSO 1` da regra de seleção:**
> *«capturado_em <= as_of. Não se responde uma pergunta de abril com evidência de agosto.
> `FUTURE_CAPTURE_CANNOT_RESOLVE_PAST_QUESTION`.»*
>
> Esta regra, já escrita em `CAPTURE-VS-REGISTRATION-CONTRACT-V1`, é **auditabilidade de
> decisão implementada como constraint**, e é mais rigorosa do que a maior parte do que a
> literatura descreve.

### O que NÃO transfere

| não transfere | porquê |
|---|---|
| **Otimização e recomendação automática** | `EXTERNAL-ONLY`: sem dados internos não há função-objetivo. E a promessa do produto é `prioridade defensável`, não faturação |
| **«decisões por segundo»** | o ciclo aqui é a safra |
| **Fechar o ciclo com o resultado** | `OUTCOME` é uma observação futura e hoje é `NÃO SEI` em todas as famílias. O campo existe para guardar o dia em que deixar de ser |

---

## §16 · TABELA DE TRANSFERÊNCIA — o que entra e o que fica de fora

| # | fonte | o que ENTRA na Bíblia | onde | o que NÃO transfere |
|---|---|---|---|---|
| 1 | Palantir Foundry | camada semântica ≠ aplicação; um objeto, muitas *object views*; *full* × *panel* | §3, §6 M:N, §10 | Actions · ontologia operacional · Workshop |
| 2 | Recorded Future | evidência por regra, com fonte clicável; ficha com secções fixas | §7 `EVIDENCE_REQUIREMENT` | **risk score 0–99** · escalas bom/mau |
| 3 | Dataminr | o artefacto de entrega **regenera-se** quando o evento evolui | §13 | previsão · «first alert» · fusão multi-modal |
| 4 | AlphaSense | citação ao nível do trecho como norma de entrega | §11.2 A-03 | «no hallucinations» · o sumário como unidade |
| 5 | OpenCTI | fiabilidade ≠ confiança; **a menor vence** | §5.3 `L-CONF` | confiança como permissão de escrita · Admiralty · STIX |
| 6 | MISP | vocabulário controlado separado do dado; ***sighting*** com denominador | §5, S-07 | partilha entre comunidades · galaxies |
| 7 | IBM i2 | investigação por expansão → `INVESTIGATION_VIEW` | §10 | expansão livre de grafo |
| 8 | CQRS | a forma de leitura é legitimamente diferente da de origem | §6 | *command model* · o **nome** |
| 9 | Materialized View | **descartável · nunca escrita pela aplicação · cache especializada** | §6 P-01…P-04 | o foco em desempenho |
| 10 | Event Sourcing | corrigir o passado sem apagar | §13 `CORRECTS` | event store · replay |
| 11 | BFF | uma projeção por experiência | §6 | um serviço por BFF · dono do lado da UI |
| 12 | Anti-Corruption Layer | tradução sem regra de negócio | §3 teste da deriva | ACL como migração temporária |
| 13 | **ICD 203** | **léxico fechado de likelihood + a proibição de os misturar** | §5.2 | obrigação de emitir juízo · cadeia de comando |
| 14 | Feature Toggles | estado temporário é **inventário com custo de posse** | §9 LC-04/LC-05 | *toggles* por pedido e coortes |
| 15 | Decision Intelligence | reconstruir o que se sabia **no momento da decisão** | §12 `AS_OF` | otimização · fechar o ciclo hoje |

---

## §17 · O QUE A PESQUISA EXTERNA **NÃO** RESOLVEU

Cinco perguntas do SINTONIA para as quais nenhum dos quinze sistemas ofereceu resposta
transferível:

| # | pergunta | por que nenhum ajuda |
|---|---|---|
| N-01 | **Quando é que uma capacidade provada num país autoriza uma tela noutro?** | todos assumem um domínio homogéneo. Aqui a lei é o contrário: `X-008` diz que só **duas** dimensões são comparáveis entre os três países, e uma tela «overview» hoje **fabricaria uniformidade** |
| N-02 | **Como medir valor de decisão sem dados internos?** | todos os modelos de valor assumem acesso ao resultado (venda, incidente evitado, ROI). `EXTERNAL-ONLY` fecha essa porta por decisão do cliente |
| N-03 | **O que é uma superfície de evidência para o CLIENTE?** | a indústria divide em «produto» e «admin». `Source Register` é nem uma nem outra: é prova, para o cliente. A classe `EVIDENCE_EXPLORER` **teve de ser inventada aqui** |
| N-04 | **Como versionar uma LEI que reclassifica dados que não mudaram?** | os sistemas versionam dados e modelos, não **réguas de elegibilidade**. `13 → 17` sobre os mesmos 43 casos não tem análogo em nenhuma das quinze fontes |
| N-05 | **Como declarar que uma fonte recusa o robô sem afirmar ausência?** | `NOT_OBSERVED_IN_TMVIEW`, `403 ≠ ausência de comunicação`, `NÃO COLETADO ≠ NÃO EXISTE`. Este vocabulário é **originalmente deste repositório** e não foi encontrado formalizado em nenhuma fonte externa |

> **Três das cinco leis mais importantes desta Bíblia — `N-03`, `N-04`, `N-05` — não vêm
> de fora. Vêm de defeitos que este repositório cometeu, mediu e corrigiu.**
>
> É o resultado que justifica a ordem da missão: **estudar o SINTONIA real primeiro.**
> Quem tivesse começado por Palantir teria importado uma ontologia com *actions* que não
> existem, e quem tivesse começado por Recorded Future teria importado um *score* que o
> repositório já provou não poder produzir.

---

## §18 · NOTA DE MÉTODO E LIMITAÇÕES

**Fontes primárias consultadas diretamente (documentação oficial ou do autor do padrão):**
Palantir Foundry ×2 · Martin Fowler ×3 (CQRS, Event Sourcing, Feature Toggles) ·
Microsoft Azure Architecture Center ×2 (Materialized View, Anti-Corruption Layer) ·
OpenCTI ×2 · MISP ×1 · Recorded Future ×1 · Sam Newman ×1. **Total: 13.**

**Fontes consultadas por via secundária, e declaradas:** ICD 203 (o PDF oficial da ODNI
devolveu 301 → 301 → 404; o texto foi verificado num repositório de referência público e
confirmado por pesquisa independente — as bandas e a proibição batem nas duas rotas) ·
Dataminr e AlphaSense (páginas de produto, não documentação técnica) · IBM i2 e Decision
Intelligence (síntese de literatura).

**Limitações declaradas:**

1. **`SEM DOCUMENTAÇÃO PRIMÁRIA ≠ SEM VALIDADE`, mas também `≠ PROVADO`.** As fichas §3,
   §4, §7 e §15 são as mais fracas e estão marcadas.
2. **Páginas de produto são material de marketing.** Dataminr e AlphaSense descrevem o que
   vendem, não o que medem. Foi por isso que a coluna `WHAT DOES NOT TRANSFER` nessas duas
   fichas é a mais longa.
3. **Nenhum destes sistemas foi executado.** A comparação é de arquitetura declarada
   contra arquitetura declarada.
4. **Não se pesquisou nenhum sistema de inteligência agro.** É uma lacuna real: nenhuma
   das quinze fontes opera no domínio agronómico, e a assimetria país-a-país (`N-01`) pode
   ter resposta noutro sítio que esta pesquisa não procurou.

> **`NÃO PESQUISADO ≠ NÃO EXISTE`.**
