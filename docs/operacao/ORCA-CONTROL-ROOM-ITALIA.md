# ORCA CONTROL ROOM — ITÁLIA

> **Este ficheiro não é arquitetura, e não é lei.** É o mapa das **bancadas**:
> quem trabalha onde, com que ramo, e para onde integra. A arquitetura vive em
> [`README.md`](../../README.md) §PRINCÍPIO; a lei do mapa em
> [`AGENTS.md`](../../AGENTS.md); as instruções permanentes em
> [`CLAUDE.md`](../../CLAUDE.md). **Uma lei escrita em dois sítios diverge, e a
> partir daí nenhuma das duas vale.**

```
MEDIDO EM    2026-09-15
TRUNK        claude/it-trunk-v1 @ 0063e46b
FASE 1       CLOSED  ·  FASE 2 CONTROLADA autorizada  ·  BIG COLLECTION não
```

---

## AS TRÊS PALAVRAS QUE NÃO SÃO SINÓNIMOS

Esta distinção é a razão de o ficheiro existir. Confundi-las transforma um
mapa de trabalho em arquitetura por acidente.

```
CASA / WORKTREE      a bancada permanente de um departamento
BRANCH               a linha de trabalho ACTUAL daquela bancada
CANONICAL_OWNER      a autoridade funcional MEDIDA — git, contrato, prova
TRUNK                o estado integrado e provado
```

> **UMA CASA PODE TROCAR DE BRANCH. UMA BRANCH ABERTA NO ORCA NÃO VIRA
> AUTORIDADE POR ESTAR ABERTA.**

E o inverso também: o SCRAP tem bancada própria e **não** é dono de nada —
a autoridade dele é a Collection. Bancada é onde se trabalha; dono é quem responde.

⚠️ **Quem governa o quê** não se decide aqui. Esse registo é o
`controle/AUTORIDADES-CANONICAS.json`, e a sua porta é
`SALA-DE-CONTROLE-SINTONIA.md` — **ambos vivem na linha da Intelligence e ainda
não estão no tronco**. Este ficheiro responde *quem trabalha onde*; aquele
responde *quem manda*. Não se substituem.

---

## O MAPA DAS BANCADAS

| # | HOUSE | ROLE | CANONICAL_OWNER | OWNER_HEAD | WORK_BRANCH | STATUS |
|---|---|---|---|---|---|---|
| 00 | **COORDENAÇÃO / TRUNK** | integração | `claude/it-trunk-v1` | `0063e46b` | — | **READY** |
| 01 | **SOURCES / ATLAS** | quem observamos | trunk | `0063e46b` | `claude/it-sources-atlas-v1` | **ACTIVE** |
| 02 | **COLLECTION + SALA** | a cadeia do dado | trunk | `0063e46b` | `claude/it-collection-sala-v1` | **ACTIVE** |
| 03 | **SCRAP** | aquisição especializada | **Collection** | `0063e46b` | `claude/it-scrap-v1` | **ACTIVE** |
| 04 | **ADAMA REFERENCE** | verdade de referência | trunk · `referencia/adama/` | `0063e46b` | `claude/it-adama-reference-v1` | **ACTIVE** |
| 05 | **INTELLIGENCE** | leitura do admitido | `claude/intelligence-bible-canonical-review-749b7c` | `384df035` | a própria | **NEEDS_RECONCILIATION** |
| 06 | **INTELLIGENCE TOOLS** | ferramenta de cruzamento | **nenhum** | — | — | **PARKED** |
| 07 | **SYSTEM MAP** | observa | trunk | `0063e46b` | — | **SUPPORT_ON_DEMAND** |
| 08 | **DATABASE** | sustenta | trunk · `supabase/` | `0063e46b` | — | **SUPPORT_ON_DEMAND** |
| 09 | **OPS** | entrega | trunk (`.github/workflows/`) | `0063e46b` | — | **SUPPORT_ON_DEMAND** |
| 10 | **PORTAL** | apresenta | trunk (absorvido) | `0063e46b` | — | **PARKED** |
| 11 | **KNOW-HOW** | governa conhecimento | `handoff/` no trunk | `0063e46b` | — | **SUPPORT_ON_DEMAND** |

### As bancadas no disco

```
00  C:\Users\London1\orca\workspaces\eame-sintonia\it-trunk-v1
01  C:\Users\London1\orca\workspaces\eame-sintonia\it-sources-atlas
02  C:\Users\London1\orca\workspaces\eame-sintonia\it-collection-sala
03  C:\Users\London1\orca\workspaces\eame-sintonia\it-scrap
04  C:\Users\London1\orca\workspaces\eame-sintonia\it-adama-reference
05  C:\eame-sintonia\.claude\worktrees\intelligence-bible-canonical-review-749b7c
```

⚠️ A bancada 05 é a **do próprio dono** — não foi criado alias nem ramo novo,
para não nascer uma segunda autoridade de Intelligence. Ela vive sob
`C:\eame-sintonia`, que está **sujo com 40 ficheiros** — mas é worktree
independente e está **limpo**. O pai sujo não a afecta; mover a bancada para a
raiz do Orca é decisão de coordenação, não requisito.

---

## CONTRATO DE ENTRADA E SAÍDA

| HOUSE | INPUT | OUTPUT |
|---|---|---|
| **01 SOURCES** | descoberta · evidência de fonte | `SOURCE_ID` + ficha no Atlas + contrato |
| **02 COLLECTION** | pedido + `SOURCE_ID` | observação · raw · derivado · READY na Sala |
| **03 SCRAP** | pedido de aquisição especializada | colheita entregue à Collection |
| **04 REFERENCE** | fontes oficiais · snapshots | verdade de referência ligada por `ADAMA_PRODUCT_ID` |
| **05 INTELLIGENCE** | material admitido + referências | findings · crossings · prova de capacidade |

---

## PATHS — O QUE CADA BANCADA PODE TOCAR

A intenção é **prevenir acidente, não falsificar arquitetura**. O código real
cruza pastas, e onde cruza está escrito como coordenação, não como muro.

### 01 · SOURCES / ATLAS
```
PODE       docs/fontes/ · candidatas/ · regras/contratos_de_fonte.py
           regras/italy_contracts.mjs · leis/fonte_do_atlas.py
           leis/territorios.py · data/samples/IT-SOURCE-SAMPLES/
NÃO PODE   coleta/ · admissao/ · guarda/ · supabase/ · referencia/ · italia-portale/
COORDENA   leis/  (partilhada com Collection) · tests/ · provas/
```

### 02 · COLLECTION + SALA
```
PODE       coleta/ · admissao/ · guarda/ · orquestrador/ · pedido/ · portoes/
           leis/ · regras/ · medidas/ · supabase/migrations/
NÃO PODE   docs/fontes/ATLAS-*  ·  referencia/  ·  motor/  ·  italia-portale/
COORDENA   tests/ · provas/ · data/derivados/
```

### 03 · SCRAP
```
PODE       coleta/scrap_*.py · coleta/social_*.py · docs/sintonia-scrap/
           .github/workflows/sintonia-scrap.yml · ferramentas/
NÃO PODE   admissao/ · guarda/ · docs/fontes/ · referencia/ · motor/
COORDENA   coleta/  (é a casa da Collection — o Scrap vive lá dentro)
```
> **ARCHITECTURAL_OWNER = COLLECTION · SCRAP_IS_SECOND_COLLECTION = NÃO.**
> A bancada é uma *lane de trabalho*, não uma segunda autoridade.

### 04 · ADAMA REFERENCE
```
PODE       referencia/ · fontes/adama_*.py · data/samples/IT-DOSE-ROTULO/
           research/adama-italy-product-intelligence-deep/  (só leitura)
NÃO PODE   coleta/ · admissao/ · guarda/ · docs/fontes/ATLAS-* · motor/ · italia-portale/
COORDENA   tests/ · provas/ · system-map/data/architecture.declared.json
```

### 05 · INTELLIGENCE
```
PODE       motor/ · controle/ · BIBLIA-DE-ENGENHARIA-DA-INTELLIGENCE.md
           docs/intelligence/ · research/
NÃO PODE   coleta/ · admissao/ · guarda/ · referencia/ · docs/fontes/ATLAS-*
COORDENA   system-map/data/*  · docs/piloto/  (os 23 disputados, medidos abaixo)
```

---

## CONCORRÊNCIA MEDIDA — OS 23 DISPUTADOS

Medido entre o trunk e a linha da Intelligence (merge-base `f888776d`, 13/09):

| FILE / PATH | HOUSE_A | HOUSE_B | WHY | COORDINATION_REQUIRED |
|---|---|---|---|---|
| `system-map/data/*.generated.json` (15) | qualquer | qualquer | são **gerados** | **NÃO** — regenerar após integrar |
| `italia-portale/client/system-map/state.generated.json` | System Map | — | cópia servida, gerada | **NÃO** |
| `docs/piloto/*.md` (4) | Intelligence | trunk | narrativa do piloto | **SIM** |
| `docs/apresentacao/PILOTO-CLASSIFICACAO.md` | Intelligence | trunk | idem | **SIM** |
| `docs/ferramentas/ARQUITETURA-DE-INFORMACAO-EAME.md` | Intelligence | trunk | idem | **SIM** |
| `docs/relatorios/RELATORIO-PORTAO-DE-ENTRADA-DA-COLETA.md` | Intelligence | Collection | relatório do portão | **SIM** |
| `HANDOFF-CONTA-CLAUDE-SINTONIA-EAME.md` | Intelligence | trunk | handoff de conta | **SIM** |
| `data/derivados/MATRIZ-CARDS-SENSORES-V1.json` | Intelligence | trunk | derivado | **SIM** |

```
COLISÕES EM CÓDIGO ENTRE INTELLIGENCE E O TRUNK = 0
```
Zero em `coleta/` · `admissao/` · `guarda/` · `supabase/` · `referencia/` ·
`leis/` · `regras/` · `tests/` · `provas/`. **Collection e Intelligence podem
correr ao mesmo tempo.**

### Áreas historicamente partilhadas — a regra

```
docs/     ·  tests/  ·  provas/  ·  data/derivados/
```
Ninguém é dono. Quem toca, declara no handoff. Ficheiro novo entra com o nome
da casa no assunto do commit.

### Ficheiros gerados — não se fundem à mão

```
system-map/data/*.generated.json      ·  italia-portale/client/system-map/
docs/fontes/INDICE-DE-FONTES.md       ·  regras/LEIA-ANTES-DE-COLETAR.md
docs/operacao/CENSO-DAS-LIGACOES-DA-COLLECTION.md
SALA-DE-CONTROLE-SINTONIA.md          ·  referencia/adama/*.json
```
> **A AUTORIDADE É O GERADOR, NUNCA O ARTEFACTO.** Em conflito, regenera-se
> pela cadeia canónica depois de integrar — nunca se resolve o diff à mão.

---

## POLÍTICA DE INTEGRAÇÃO — medida, não inventada

```
HOUSE_TO_TRUNK_INTEGRATION_POLICY = MERGE, com adoção selectiva quando a
                                    candidata está longe demais
```

**A evidência.** O trunk tem **16 merges** na sua história, com integrações
nomeadas — `C-GATE-01: a candidata integrada`, `o SCRAP entra na Collection`,
`E7 aterra na linha funcional atual`. Merge é a convenção quando a candidata é
descendente ou irmã próxima e se quer o conteúdo inteiro.

**Mas há o segundo precedente, e também é desta casa:** a FASE 1B trouxe o Atlas
por **adopção selectiva de caminhos** (`git checkout <ref> -- <paths>`), porque a
candidata estava 377 commits atrás e só parte dela era desejada. Medir a
ancestralidade e os ficheiros disputados é o que decide qual das duas se usa.

```
NÃO É POLÍTICA DESTA CASA:  rebase do trunk  ·  cherry-pick de pacote inteiro
```

**Nada entra no trunk por «parecer pronto».** Entra com: escopo fechado ·
testes com base medida e `NEW_FAILURES = 0` · red team quando aplicável ·
contratos respeitados · handoff com veredito.

---

## PRÓXIMA MISSÃO POR CASA

| HOUSE | NEXT_MISSION |
|---|---|
| 01 SOURCES | continuidade de qualificação, **sem coleta** |
| 02 COLLECTION | **FASE 2 — certificação controlada, `IT-T4-001`** |
| 03 SCRAP | aguarda a FASE 2 fechar antes de rota especializada |
| 04 REFERENCE | histórico e drift (51 vs 55), **sem Change Engine** |
| 05 INTELLIGENCE | **reconciliar a linha com trunk / Sala / ADAMA Reference** |
| 06 TOOLS | nenhuma — `PARKED_WAITING_FOR_CAPABILITY` |
| 07–11 | nenhuma — sob pedido |

---

## O QUE ESTE FICHEIRO NÃO DECIDE

- **não decide** quem governa — isso é `controle/AUTORIDADES-CANONICAS.json`;
- **não decide** a ordem do dado — isso é `README.md` §PRINCÍPIO;
- **não decide** o que é lei — isso é `AGENTS.md` e a Bíblia da Coleta;
- **não decide** que uma branch é dona por estar aberta no Orca.
