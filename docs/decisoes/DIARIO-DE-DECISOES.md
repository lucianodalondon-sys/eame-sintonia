# DIÁRIO DE DECISÕES — SINTONIA EAME

Registro cronológico de **toda** decisão que afeta o repositório: estrutura, método,
escopo, fonte, ferramenta, corte.

Regras do diário:

- Uma decisão por entrada, com **data**, **motivo** e **estado**.
- Decisão revertida **não se apaga**: abre-se nova entrada que a revoga, citando a original.
- Decisão tomada por falta de informação é marcada como **SUPOSIÇÃO ASSUMIDA** e vira
  pergunta pendente até ser confirmada por quem tem autoridade.
- Nenhuma decisão de produto é registrada aqui sem ter sido dada por quem decide.

**Formato:**

```
### D-000 — Título
- Data:
- Estado: DECIDIDO | SUPOSIÇÃO ASSUMIDA | REVOGADA (por D-000) | PENDENTE
- Contexto:
- Decisão:
- Motivo:
- Consequência:
- Quem decidiu:
```

---

### D-001 — Repositório próprio, sem herdar artefatos do Sintonia Brasil
- **Data:** 2026-08-28
- **Estado:** DECIDIDO
- **Contexto:** Existe um Sintonia Brasil em operação, com código, réguas, banco e classificadores.
- **Decisão:** O SINTONIA EAME nasce em repositório próprio e vazio. O Brasil entra apenas
  como referência metodológica. Não se copia código, régua instável, banco ou classificador,
  e não se altera o repositório brasileiro.
- **Motivo:** Realidade regulatória, fontes, idiomas e mercado da EAME são outros; herdar
  artefato pronto importaria pressupostos brasileiros não verificados na Europa.
- **Consequência:** Todo aproveitamento vindo do Brasil precisa de entrada própria neste diário.
- **Quem decidiu:** Enunciado da tarefa.

### D-002 — Estrutura inicial de pastas conforme sugerida
- **Data:** 2026-08-28
- **Estado:** DECIDIDO
- **Contexto:** Primeira tarefa é preparar a casa antes de pesquisar ou implementar.
- **Decisão:** Adotada a estrutura sugerida: `docs/` (01 a 08), `data/` (samples, raw,
  normalized), `research/` (europe, france, spain, italy, people, competitors),
  `prototype/portal`, `tests/`, `scripts/`.
- **Motivo:** A estrutura já reflete a cadeia SOURCE → … → PORTAL e o recorte por país.
- **Consequência:** Diretórios ainda sem conteúdo carregam `.gitkeep` para existirem no versionamento.
- **Quem decidiu:** Enunciado da tarefa.

### D-003 — `data/raw` e `data/normalized` fora do versionamento
- **Data:** 2026-08-28
- **Estado:** SUPOSIÇÃO ASSUMIDA
- **Contexto:** Não houve instrução sobre o que versionar dentro de `data/`.
- **Decisão:** `data/raw/` e `data/normalized/` ficam ignorados pelo Git (exceto os
  `.gitkeep`). `data/samples/` é versionado.
- **Motivo:** Bruto e normalizado tendem a ser grandes, refazíveis e sujeitos a licença de
  redistribuição; amostras pequenas com procedência são justamente o que precisa viajar
  junto com a evidência.
- **Consequência:** Evidência preservável de uma fonte deve ir para `data/samples/`, não
  para `data/raw/`. Se alguma fonte exigir versionar bruto, revogar esta entrada.
- **Quem decidiu:** Assumido na ausência de instrução — **confirmar**.

### D-005 — Estrutura de `docs/` realinhada ao briefing da MISSÃO EAME 01
- **Data:** 2026-08-28
- **Estado:** DECIDIDO (revoga parcialmente D-002)
- **Contexto:** D-002 adotou `docs/01-descoberta` … `docs/08-decisoes`, com prefixos
  numéricos e uma pasta `06-arquitetura`. O briefing da MISSÃO EAME 01, recebido depois,
  especifica `docs/descoberta`, `fontes`, `capacidades`, `cruzamentos`, `ferramentas`,
  `decisoes`, `apresentacao` — sem prefixos e sem pasta de arquitetura — e diz
  "não criar estrutura adicional sem necessidade comprovada".
- **Decisão:** Pastas renomeadas para a forma do briefing; `06-arquitetura` removida.
- **Motivo:** O briefing da missão é a especificação vigente e é mais restritivo.
  Arquitetura não tem necessidade comprovada nesta fase.
- **Consequência:** Os caminhos de D-002 não valem mais. Se o desenho técnico precisar de
  lugar próprio mais adiante, abre-se nova entrada justificando a necessidade.
- **Quem decidiu:** Briefing MISSÃO EAME 01, §0 e §17.

### D-006 — Documentos canônicos como memória externa
- **Data:** 2026-08-28
- **Estado:** DECIDIDO
- **Contexto:** Instrução de modo de execução com economia de contexto.
- **Decisão:** Todo achado é gravado imediatamente no documento canônico correspondente,
  com a evidência preservada e commit próprio. Nada de inventário grande vivendo só no
  contexto da conversa. Checkpoints referenciam arquivo em vez de reproduzir conteúdo.
- **Motivo:** Evidência sobrevive à conversa; contexto não.
- **Consequência:** Prioridade operacional: EVIDÊNCIA > CONTEXTO, ARQUIVO > MEMÓRIA,
  MEDIÇÃO > EXPLICAÇÃO.
- **Quem decidiu:** Instrução do usuário (modo de execução).

### D-004 — Documentos-base criados como esqueleto, sem conteúdo inventado
- **Data:** 2026-08-28
- **Estado:** DECIDIDO
- **Contexto:** Os documentos de fontes, capacidades, cruzamentos, ferramentas e casos de
  apresentação foram pedidos antes de qualquer pesquisa.
- **Decisão:** Cada um nasce com propósito, regra de preenchimento e formato de ficha —
  e com o registro de fontes/capacidades **vazio**.
- **Motivo:** Preencher exemplos plausíveis antes de pesquisar violaria o princípio
  SOURCE → EVIDENCE e contaminaria o atlas com conteúdo que ninguém verificou.
- **Consequência:** Os atlas mostram zero registros. Isso é o estado correto da Fase 0.
- **Quem decidiu:** Enunciado da tarefa (princípio e regra).

---

## PERGUNTAS PENDENTES

| # | Pergunta | Bloqueia | Aberta em |
|---|---|---|---|
| P-001 | Confirmar D-003 (versionar ou não `data/raw`). | Política de evidência | 2026-08-28 |
| P-002 | Quem é a audiência da apresentação e qual a data-alvo? | `07-apresentacao` | 2026-08-28 |
| P-003 | Que dados internos da ADAMA EAME estarão disponíveis? | `02-fontes` | 2026-08-28 |
| P-004 | Idioma exigido nos entregáveis finais? | Todos os docs | 2026-08-28 |
| P-005 | Restrições jurídicas / GDPR / licença aplicáveis ao uso pretendido? | `02-fontes`, `03-capacidades` | 2026-08-28 |
