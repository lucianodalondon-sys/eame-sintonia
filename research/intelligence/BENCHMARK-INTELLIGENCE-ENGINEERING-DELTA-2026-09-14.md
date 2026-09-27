# BENCHMARK DE ENGENHARIA DA INTELLIGENCE — DELTA 2026-09-14

```
MISSAO      C-INT-BIBLE-TOOLS-SOURCEPERF-01
ESPECIE     BENCHMARK EXTERNO READ-ONLY — informa, nao governa
MEDIDO_EM   2026-09-14
ESTENDE     BENCHMARK-DE-ENGENHARIA-DA-INTELLIGENCE-2026-09-13.md
SUBSTITUI   nada
```

> **Este ficheiro não reescreve o de 2026-09-13.** Aquele é uma fotografia
> datada, e nesta casa fotografia datada sucede-se, não se corrige. Este
> acrescenta **quatro** fontes externas, e só quatro.

---

## 0 · A LACUNA, MEDIDA ANTES DE PESQUISAR

O enunciado da revisão listou sete benchmarks. Antes de abrir o navegador,
contou-se quantos já estavam cobertos — porque pesquisar outra vez o que já tem
dono é gastar tempo a produzir a segunda versão de uma coisa.

Medido com `grep -ril`, em `research/intelligence/`, `docs/intelligence/` e na
própria Bíblia:

| termo | ficheiros que o mencionavam |
|---|---|
| `MLflow` | **0** |
| `LangSmith` | **0** |
| `crawl` | **0** |
| `exploration` / `exploitation` | **0** |
| `bandit` / `multi-armed` | **0** |
| `LLM-as-judge` / `pairwise` | **0** |
| `AIP` | 1 (menção solta) |

E o que **já estava** coberto, na §29 da Bíblia V0.2, e por isso não se repetiu:
Databricks Unity Catalog · Palantir Foundry/Ontology · OpenLineage · W3C PROV-O ·
OpenMetadata · Dagster/dbt · **ODNI ICD 203** · CIA Structured Analytic
Techniques · **UK Government Office for Science Futures Toolkit** · NIST AI RMF ·
NIST SSDF · NIST Zero Trust.

```
DOS SETE DO ENUNCIADO, TRES JA TINHAM DONO.
PESQUISOU-SE O QUE FALTAVA, E SO ISSO.
```

---

## 1 · MLflow — GenAI Evaluation & Tracing

**Fonte:** <https://mlflow.org/docs/latest/genai/eval-monitor/>

### O modelo deles

- **Trace** é a unidade de observabilidade: captura latência, tokens e métricas
  de qualidade em cada passo da execução.
- **Scorer / Judge** é o critério de avaliação. Há juízes LLM prontos e
  ferramenta para construir os próprios.
- **Evaluation Dataset** é descrito como *«test database»* — repositório central
  de casos de teste, expectativas e dados de avaliação.
- **Offline** sobre dataset curado; **online** sobre produção, via tracing.
- Datasets de avaliação constroem-se **a partir de traces de produção**, e o
  feedback humano fica anexado ao trace com utilizador, timestamp e revisões.
- Suporta regressão e CI/CD.

### O pulo do gato

> **O trace de produção é a matéria-prima do teste de amanhã.** Não são dois
> sistemas — um de observabilidade e outro de avaliação. É um, e a seta vai da
> execução real para o conjunto de regressão.

### Transferência para o SINTONIA

- Sustenta `37.2` (o trace) e `37.3` (`FAILURE → TEST CASE`).
- O feedback humano **anexado ao trace, com autor e data** é exatamente o que a
  `INT-LAW-041` já exige do lineage, dito do lado da observabilidade. Não é lei
  nova: é confirmação externa de uma que já existia.

### O que NÃO copiar

- O vocabulário de «qualidade» genérica. No SINTONIA a pergunta não é «a resposta
  é boa?», é «a promoção era defensável?» — e as duas não se medem igual.
- O juiz LLM como avaliador por defeito. Ver §2.

---

## 2 · LangSmith — Evaluation & Observability

**Fonte:** <https://docs.langchain.com/langsmith/evaluation-concepts>

### O modelo deles

Quatro espécies de avaliador, nomeadas:

| espécie | quando |
|---|---|
| **Human** | revisão manual, organizada em *annotation queue* |
| **Code** (determinístico) | regra verificável — «compila», «não está vazio» |
| **LLM-as-judge** | pontua saída, com ou sem referência |
| **Pairwise** | compara duas versões da aplicação |

E dois eixos que não se confundem:

- **reference-based** × **reference-free** — ter ou não resposta esperada;
- **offline** (dataset curado, com resposta) × **online** (tráfego real, sem
  resposta, à procura de anomalia e padrão).

### Os dois avisos, que são o mais valioso

1. **Sobre pairwise:** recomendam-no quando pontuar em absoluto é difícil e
   comparar é fácil. O exemplo deles é sumarização — *escolher o mais informativo
   de dois resumos é mais fácil do que dar nota a um.*
2. **Sobre LLM-as-judge:** avisam que estes avaliadores *«exigem revisão cuidada
   das notas e afinação do prompt»* — ou seja, **o juiz precisa de ser validado
   antes de julgar.**

### Transferência para o SINTONIA

- Origem direta da `INT-LAW-300` (a espécie da prova segue a natureza da
  pergunta) e da `INT-LAW-301` (o juiz LLM não é o padrão, e é ele próprio
  avaliado).
- O par offline/online da `37.1` sai daqui e do MLflow, e os dois concordam.

### O que NÃO copiar

- **A hierarquia implícita.** Na documentação deles as quatro espécies são
  alternativas de conveniência. No SINTONIA não são: onde existe prova
  determinística, é ela que manda, e usar um LLM ali é trocar uma resposta
  verificável por uma plausível. A `INT-LAW-301` escreve essa ordem, que a fonte
  não escreve.

---

## 3 · Palantir AIP Evals

**Fonte:** <https://palantir.com/docs/foundry/aip-evals/overview/>

### O modelo deles

- **Evaluation suite** = casos de teste + função-alvo + funções de avaliação.
- **Test case** = conjunto definido de entradas e saídas esperadas.
- **Evaluation function** = o *grader*, que compara saída real com esperada.
- **Target function** = o que está a ser testado.

### Transferência

Confirma a forma de `37.1` OFFLINE: suite, caso, grader, alvo. É vocabulário
convergente com MLflow e LangSmith — três produtos independentes com a mesma
estrutura é sinal de que a estrutura não é moda.

### O que NÃO se conseguiu medir, e diz-se

A página consultada **não detalha** guardrails de IA nem human-in-the-loop. A
Foundry/Ontology já estava benchmarkada na V0.2; o que a camada AIP acrescenta em
governança **não foi verificado aqui**.

```
AIP_GUARDRAILS_E_HUMAN_IN_THE_LOOP = NAO MEDIDO
```

---

## 4 · Microsoft Research — Web Crawl Scheduling

**Fontes:**
<https://www.microsoft.com/en-us/research/project/web-crawl-scheduling/> ·
<https://github.com/microsoft/Optimal-Freshness-Crawl-Scheduling>

Três artigos: *Optimal Freshness Crawl Under Politeness Constraints* (SIGIR
2019) · *Staying up to date with online content changes using reinforcement
learning for scheduling* (NeurIPS 2019) · *Online Learning for Active Cache
Synchronization* (ICML 2020).

**É o benchmark mais importante deste delta**, e o único que trata exatamente a
pergunta da secção 36 da Bíblia: como decidir onde voltar, quando o orçamento não
chega para voltar a todo o lado.

### 4.1 · Observabilidade parcial

> *«for most URLs, a search engine finds out whether they have changed only when
> it crawls them.»*

Só se descobre que uma fonte mudou **indo lá**.

E é aqui que está o laço que se fecha sozinho, e que o SINTONIA tinha de barrar
por lei: uma fonte que se deixa de coletar deixa de produzir prova, a falta de
prova parece fraqueza, e a fraqueza aparente justifica não voltar lá. **O sistema
confirma a si próprio uma medida que nunca fez.**

→ Origem direta da `INT-LAW-297`, e da distinção que ela obriga:

```
SAMPLE_SIZE = 0  →  PERFIL = UNKNOWN     e NUNCA «fraco»
```

### 4.2 · Importância e taxa de mudança são dois eixos

O problema deles lida com *«vastly different importance and change frequency
characteristics»*, e a patente descreve a função de custo a receber
**separadamente** o *importance score* e o *change rate*.

→ Origem direta da `INT-LAW-296` — `LOW FREQUENCY ≠ LOW IMPORTANCE`. Uma fonte
regulatória oficial que publica quatro vezes por ano tem taxa de mudança baixa e
importância alta. Um sistema com um eixo só não consegue dizer isso.

### 4.3 · Restrições que a prioridade não atravessa

*Politeness constraints* e largura de banda são limites duros: *«the crawler
cannot react to every individual predicted or actual change»*.

→ Confirma a forma das categorias protegidas da `INT-LAW-296`: há posições que
não se calculam a partir do perfil, decidem-se acima dele.

### 4.4 · Exploração × exploração-do-conhecido, dita com esse nome

Eles enquadram-no como *«exploration-exploitation tradeoff»*: aprender os
parâmetros do modelo de mudança **enquanto** se cumprem objetivos de frescura e
completude — um *«constrained learning and optimization problem»*.

→ Origem da `INT-LAW-297`, e da recusa em fixar a quota: eles resolvem-na com
algoritmos sobre dados medidos ao longo de 14 semanas. Escolher uma percentagem
sem medição nenhuma seria inventar o número que a lei existe para exigir.

### O que NÃO copiar

- **O objetivo.** A função de custo deles é *frescura do índice*. A nossa é
  *valor analítico produzido*, que não é uma função de quão recente é a página.
  `FRESH BUT USELESS` já é um anti-padrão desta casa (AP-07).
- **A automação do laço.** Eles fecham o laço na máquina: o agendador aprende e
  reagenda. No SINTONIA o laço é **interrompido de propósito** — a Intelligence
  aconselha, a Collection decide (`INT-LAW-290`). Copiar a automação seria
  entregar a agenda da coleta a quem não é dono dela.
- **O pressuposto de escala.** Eles operam sobre milhares de milhões de URLs,
  onde a média tem significado. O SINTONIA opera sobre dezenas de fontes, onde
  `SAMPLE_SIZE` é pequeno e uma média engana. Daí `SAMPLE_SIZE` e `CONFIDENCE`
  governarem todas as outras métricas em `36.3`.

---

## 5 · O QUE ESTE DELTA PRODUZIU NA LEI

| lei nova | veio de |
|---|---|
| `INT-LAW-296` LOW FREQUENCY ≠ LOW IMPORTANCE | MS Research 4.2 + 4.3 |
| `INT-LAW-297` PRIORITIZATION MUST PRESERVE EXPLORATION | MS Research 4.1 + 4.4 |
| `INT-LAW-300` espécie da prova segue a pergunta | LangSmith §2 |
| `INT-LAW-301` LLM-as-judge não é o padrão, e é avaliado | LangSmith §2 (aviso) |
| `37.1` offline × online | MLflow §1 + LangSmith §2 |
| `37.2` trace | MLflow §1 |
| `37.3` FAILURE → TEST CASE | MLflow §1 |

E o que foi **rejeitado**, com motivo, está em cada secção acima sob *«O que NÃO
copiar»*. São cinco rejeições, e a mais importante é a 4.4: **o laço automático**.

---

## 6 · DESCONHECIDOS DECLARADOS

```
AIP_GUARDRAILS_E_HUMAN_IN_THE_LOOP     NAO MEDIDO
QUOTA DE EXPLORACAO                    NAO ESCOLHIDA — falta medicao propria
CONCORDANCIA LLM-JUIZ x HUMANO         NAO MEDIDA nesta casa, para nenhuma classe
CUSTO REAL POR ITEM UTIL               NAO MEDIDO — depende de lineage que ainda
                                       nao atravessa
```

Benchmark informa; **não governa**.
