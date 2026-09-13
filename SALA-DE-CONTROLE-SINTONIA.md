# SALA DE CONTROLE — SINTONIA EAME

> **Este ficheiro é gerado.** Não o edite à mão: edite
> [`controle/AUTORIDADES-CANONICAS.json`](controle/AUTORIDADES-CANONICAS.json)
> e corra `py controle/censo_do_controle.py`.

Esta é a porta do **CONTROL PLANE**: quem governa cada parte da máquina,
onde essa autoridade vive, e se ela ainda manda hoje.

**Ela não repete lei nenhuma.** A lei do mapa vive em [`AGENTS.md`](AGENTS.md);
as instruções permanentes em [`CLAUDE.md`](CLAUDE.md); o método em
[`README.md`](README.md). Uma lei escrita em dois sítios diverge, e a partir
daí nenhuma das duas vale.

---

## OS TRÊS PLANOS

```
CONTROL PLANE      quem manda        governa, referencia, valida, observa
      ↓ governa (nunca dado)
OPERATIONAL PLANE  a máquina         COLETA → ESPERA → INTELIGÊNCIA → ENTREGA
      ↑ prova
EVIDENCE PLANE     o que comprova    git · código · banco · runtime · testes
```

O Control Plane **não é uma quarta etapa do dado**. Não existe
`DADO → CONTROL PLANE`: nenhum dado atravessa este plano. Ele governa a
máquina; a máquina é que corre.

O System Map atravessa os três. **Não é pai de nenhum** — é derivado deles.

---

## QUEM COMANDA CADA PARTE

| parte da máquina | autoridade | onde vive hoje | manda? |
|---|---|---|---|
| **COLETA** | BIBLIA CANONICA DA COLETA | `origin/claude/raw-observation-identity-3jbwco` | 🔴 CANONICAL |
| **INTELIGÊNCIA** | BIBLIA DA INTELIGENCIA | `origin/claude/integration-acervo-portal-v1` | 🔴 RECOVERY_PENDING |
| **INTELIGÊNCIA** | BIBLIA DE ENGENHARIA DA INTELLIGENCE | `origin/research/intelligence-bible-engineering-v1` | 🔴 CANDIDATE |
| **ENTREGA / CASCO** | BIBLIA DA ENTREGA / CASCO | `origin/research/delivery-bible-v1` | 🔴 CANDIDATE |

A leitura desta tabela é o resultado principal desta missão:
**nenhuma das três bíblias está nesta árvore.**

---

## O CATÁLOGO

### INSTRUÇÕES

#### 🟢 A LEI DO SYSTEM MAP

- **conceito que possui** — `LEI_DO_SYSTEM_MAP`
- **para que serve** — Dizer o que o System Map e, o que ele nunca pode fazer, e que gaveta guarda que etapa.
- **até onde vale** — Todo agente que altera arquitetura, fonte, coleta, fluxo, contrato, regua, motor ou superficie.
- **onde vive** — [`AGENTS.md`](AGENTS.md)
- **estado declarado** — `CANONICAL`
- **estado medido** — `PRESENT_AND_POINTED` · está aqui, e alguém aponta para ela
- **impressão do conteúdo medido** — `42a22207e7`
- **prova** — `git:HEAD:AGENTS.md`
- **quem aponta para ela** — `.github/copilot-instructions.md`, `.github/workflows/system-map.yml`, `CLAUDE.md`, `README.md` *(+11)*
- **o que ela diz de si** — A lei escrita. Os outros ficheiros de instrucao apontam para aqui e nao a repetem.

  | relação | alvo | estado | prova |
  |---|---|---|---|
  | `GOVERNS` | `system-map/scripts/generate_system_map.py` | **OBSERVED** | `AGENTS.md:83` |
  | `GOVERNS` | `system-map/scripts/validate_system_map.py` | **OBSERVED** | `AGENTS.md:84` |
  | `GOVERNS` | `system-map/data/architecture.declared.json` | **OBSERVED** | `AGENTS.md:108` |
  | `GOVERNS` | `system-map/tests/test_system_map.py` | **OBSERVED** | `AGENTS.md:87` |
  | `GOVERNS` | `_gavetas.py` | **OBSERVED** | `AGENTS.md:395` |
  | `GOVERNS` | `regras/LEIA-ANTES-DE-COLETAR.md` | **OBSERVED** | `AGENTS.md:425` |
  | `GOVERNS` | `candidatas/fonte_nova.py` | **OBSERVED** | `AGENTS.md:448` |
  | `GOVERNS` | `controle/AUTORIDADES-CANONICAS.json` | **OBSERVED** | `AGENTS.md:240` |
  | `GOVERNS` | `controle/censo_do_controle.py` | **OBSERVED** | `AGENTS.md:77` |
  | `GOVERNS` | `controle/portao_do_controle.py` | **OBSERVED** | `AGENTS.md:85` |
  | `REFERENCES` | `docs/fontes/ATLAS-DE-FONTES-EAME.md` | **OBSERVED** | `AGENTS.md:460` |
  | `REFERENCES` | `docs/operacao/CONTRATOS-DAS-FONTES-EAME.md` | **OBSERVED** | `AGENTS.md:461` |
  | `REFERENCES` | `docs/fontes/INDICE-DE-FONTES.md` | **OBSERVED** | `AGENTS.md:465` |
  | `REFERENCES` | `system-map/README.md` | **OBSERVED** | `AGENTS.md:523` |
  | `REFERENCES` | `CLAUDE.md` | **OBSERVED** | `AGENTS.md:521` |
  | `REFERENCES` | `README.md` | **OBSERVED** | `AGENTS.md:522` |

#### 🟢 INSTRUCOES PERMANENTES DO PROJETO

- **conceito que possui** — `INSTRUCOES_PERMANENTES`
- **para que serve** — Regra que vale para todas as missoes futuras, sem depender de alguem lembrar na conversa. Dona da LEI DE DESIGN.
- **até onde vale** — Toda missao neste repositorio; e toda missao que toque em design, UI, casco, portal, icones.
- **onde vive** — [`CLAUDE.md`](CLAUDE.md)
- **estado declarado** — `CANONICAL`
- **estado medido** — `PRESENT_AND_POINTED` · está aqui, e alguém aponta para ela
- **impressão do conteúdo medido** — `b38c2989c5`
- **prova** — `git:HEAD:CLAUDE.md`
- **quem aponta para ela** — `AGENTS.md`, `README.md`, `controle/AUTORIDADES-CANONICAS.json`, `controle/censo_do_controle.py` *(+7)*
- **o que ela diz de si** — Aponta para AGENTS.md como dono da lei do mapa, e possui sozinha a lei de design.

  | relação | alvo | estado | prova |
  |---|---|---|---|
  | `GOVERNS` | `docs/design/CONTRATO-DE-DESIGN-SINTONIA.md` | **OBSERVED** | `CLAUDE.md:98` |
  | `GOVERNS` | `italia-portale/client/_ds/adama-brandwell/tokens/colors.css` | **DECLARED** | *path_exists* |
  | `GOVERNS` | `italia-portale/client/_ds/adama-brandwell/styles.css` | **DECLARED** | *path_exists* |
  | `REFERENCES` | `AGENTS.md` | **OBSERVED** | `CLAUDE.md:5` |
  | `REFERENCES` | `README.md` | **OBSERVED** | `CLAUDE.md:26` |

#### 🟢 METODO E ESTADOS DE EVIDENCIA

- **conceito que possui** — `METODO_E_ESTADOS_DE_EVIDENCIA`
- **para que serve** — Dono da disciplina SOURCE -> EVIDENCE -> ... -> PORTAL e dos quatro estados de evidencia (COMPROVADO, INFERENCIA, HIPOTESE, NAO SEI).
- **até onde vale** — Todo registo do repositorio: fonte, dado, cruzamento, capacidade, afirmacao, tela.
- **onde vive** — [`README.md`](README.md)
- **estado declarado** — `CANONICAL`
- **estado medido** — `PRESENT_AND_POINTED` · está aqui, e alguém aponta para ela
- **impressão do conteúdo medido** — `5754471916`
- **prova** — `git:HEAD:README.md`
- **quem aponta para ela** — `AGENTS.md`, `CLAUDE.md`, `controle/AUTORIDADES-CANONICAS.json`, `controle/censo_do_controle.py` *(+3)*
- **o que ela diz de si** — O metodo. Nao repete a lei do mapa; aponta para AGENTS.md.
- **nota** — Aponta para `docs/08-decisoes/DIARIO-DE-DECISOES.md`, que nao existe. O diario vive em `docs/decisoes/`.

  | relação | alvo | estado | prova |
  |---|---|---|---|
  | `REFERENCES` | `AGENTS.md` | **OBSERVED** | `README.md:5` |
  | `REFERENCES` | `CLAUDE.md` | **OBSERVED** | `README.md:194` |
  | `REFERENCES` | `docs/descoberta/MISSAO-EAME-01.md` | **OBSERVED** | `README.md:137` |
  | `REFERENCES` | `docs/decisoes/DIARIO-DE-DECISOES.md` | **DECLARED** | *path_exists* |

#### 🟢 Ponteiro para a lei (Copilot e afins)

- **conceito que possui** — *nenhum — é ponteiro*
- **para que serve** — Levar qualquer agente que entre pelo GitHub ate AGENTS.md, sem repetir uma linha da lei.
- **até onde vale** — Agentes que leem `.github/`.
- **onde vive** — [`.github/copilot-instructions.md`](.github/copilot-instructions.md)
- **estado declarado** — `CANONICAL`
- **estado medido** — `PRESENT_AND_POINTED` · está aqui, e alguém aponta para ela
- **impressão do conteúdo medido** — `84b591b6c6`
- **prova** — `git:HEAD:.github/copilot-instructions.md`
- **quem aponta para ela** — `controle/AUTORIDADES-CANONICAS.json`
- **o que ela diz de si** — PONTEIRO. Nao possui conceito nenhum, e por isso nao pode colidir com AGENTS.md.

  | relação | alvo | estado | prova |
  |---|---|---|---|
  | `REFERENCES` | `AGENTS.md` | **OBSERVED** | `.github/copilot-instructions.md:3` |

### BÍBLIAS

#### 🔴 BIBLIA CANONICA DA COLETA

- **conceito que possui** — `LEI_DA_COLETA`
- **para que serve** — A constituicao da COLETA: o que entra, com que carimbo, por que porta, e o que nunca pode passar.
- **até onde vale** — Todo o departamento de COLETA e a porta de admissao.
- **onde vive** — `BIBLIA-CANONICA-DA-COLETA.md` — **não nesta árvore**; em `origin/claude/raw-observation-identity-3jbwco`
- **estado declarado** — `CANONICAL`
- **estado medido** — `ABSENT_FROM_SNAPSHOT` · NÃO ESTÁ NESTA ÁRVORE — vive noutra linha
- **impressão do conteúdo medido** — `909ba45bac`
- **prova** — `git:origin/claude/raw-observation-identity-3jbwco:BIBLIA-CANONICA-DA-COLETA.md`
- **quem aponta para ela** — `AGENTS.md`, `controle/AUTORIDADES-CANONICAS.json`, `controle/censo_do_controle.py`, `controle/red_team_do_controle.py` *(+1)*
- **cópias divergentes medidas** — 3: `origin/claude/sintonia-eame-know-how-v1`, `origin/release/canonical`, `origin/claude/biblia-canonica-da-coleta`
- **o que ela diz de si** — AUSENTE DESTA ARVORE. A lei da coleta existe no Git e nao existe em `main` — quem clona `main` e le CLAUDE.md e mandado consultar um ficheiro que ali nao esta.

  | relação | alvo | estado | prova |
  |---|---|---|---|
  | `GOVERNS` | `admissao/admissao.py` | **DECLARED** | *authority_absent* |
  | `GOVERNS` | `regras/proveniencia.py` | **DECLARED** | *authority_absent* |
  | `GOVERNS` | `regras/sensor_coleta.py` | **DECLARED** | *authority_absent* |
  | `GOVERNS` | `coleta/coletor.py` | **DECLARED** | *authority_absent* |
  | `GOVERNS` | `pedido/pedido.py` | **DECLARED** | *authority_absent* |

#### 🔴 BIBLIA DA INTELIGENCIA

- **conceito que possui** — `LEI_DA_INTELIGENCIA`
- **para que serve** — A constituicao da INTELIGENCIA: como dado bruto vira caso com dono, lugar e momento — e o que a transformacao nunca pode inventar.
- **até onde vale** — Todo o departamento de INTELIGENCIA: reguas, motor, provas.
- **onde vive** — `docs/biblia/BIBLIA-DA-INTELIGENCIA-EAME.md` — **não nesta árvore**; em `origin/claude/integration-acervo-portal-v1`
- **estado declarado** — `RECOVERY_PENDING`
- **estado medido** — `ABSENT_FROM_SNAPSHOT` · NÃO ESTÁ NESTA ÁRVORE — vive noutra linha
- **impressão do conteúdo medido** — `ac478fb7e0`
- **prova** — `git:origin/claude/integration-acervo-portal-v1:docs/biblia/BIBLIA-DA-INTELIGENCIA-EAME.md`
- **quem aponta para ela** — `controle/AUTORIDADES-CANONICAS.json`, `docs/operacao/CENSO-DA-INTELLIGENCE.md`
- **substituída por** — A-BIBLIA-ENG-INTELIGENCIA
- **o que ela diz de si** — NAO EXISTE. O ficheiro com este nome existe no Git, mas o seu proprio cabecalho recusa o titulo: diz-se `INVENTARIO_DE_LEIS · INPUT_TO_INTELLIGENCE_BIBLE` e escreve `O_QUE_ELE_AINDA_NAO_E: a Biblia de Engenharia da Inteligencia`. Um inventario das leis ja aprendidas nao e a constituicao que decide as proximas.
- **nota** — Fragmento util, nao autoridade. Nao reconstruir nesta missao. C-INT-ARB-01: o RECOVERY_PENDING fecha — a autoridade que faltava e A-BIBLIA-ENG-INTELIGENCIA (V0.2).

#### 🔴 BIBLIA DA ENTREGA / CASCO

- **conceito que possui** — `LEI_DA_ENTREGA`
- **para que serve** — A constituicao da ENTREGA: como se cria, testa, promove, funde e aposenta uma ferramenta do portal sem perder evidencia, autoridade nem NAO SEI.
- **até onde vale** — Pacote canonico, fronteira e portoes, superficies, as ferramentas do portal.
- **onde vive** — `docs/biblia/BIBLIA-DA-ENTREGA-EAME.md` — **não nesta árvore**; em `origin/research/delivery-bible-v1`
- **estado declarado** — `CANDIDATE`
- **estado medido** — `ABSENT_FROM_SNAPSHOT` · NÃO ESTÁ NESTA ÁRVORE — vive noutra linha
- **impressão do conteúdo medido** — `bb471910c6`
- **prova** — `git:origin/research/delivery-bible-v1:docs/biblia/BIBLIA-DA-ENTREGA-EAME.md`
- **quem aponta para ela** — `controle/AUTORIDADES-CANONICAS.json`
- **o que ela diz de si** — ESCRITA E NAO ACEITE. 2.738 linhas, quatro partes, benchmark de 16 sistemas — e o proprio cabecalho carimba `BIBLE_STATUS DRAFT`, `IMPLEMENTATION NONE`, `MERGES ZERO`. Nunca entrou em `main`; nenhuma peca da ENTREGA a obedece hoje.
- **nota** — CANDIDATE, nao CANONICAL: uma biblia que se declara DRAFT nao pode ser carimbada de lei por quem a cataloga.

  | relação | alvo | estado | prova |
  |---|---|---|---|
  | `GOVERNS` | `portoes/build_portal.py` | **DECLARED** | *authority_absent* |
  | `GOVERNS` | `portoes/site_v21_ingest.py` | **DECLARED** | *authority_absent* |
  | `GOVERNS` | `superficie/ask_sintonia.py` | **DECLARED** | *authority_absent* |

#### 🔴 BIBLIA DE ENGENHARIA DA INTELLIGENCE

- **conceito que possui** — `LEI_DA_INTELIGENCIA`
- **para que serve** — A constituicao da Intelligence: fronteiras, identidades analiticas, lineage, run, evidencia, dependencia, crossings, universos, incerteza e saida para a Entrega.
- **até onde vale** — Todo trabalho do lado Intelligence da fronteira COLLECTION -> SALA DE ESPERA -> INTELLIGENCE.
- **onde vive** — `BIBLIA-DE-ENGENHARIA-DA-INTELLIGENCE.md` — **não nesta árvore**; em `origin/research/intelligence-bible-engineering-v1`
- **estado declarado** — `CANDIDATE`
- **estado medido** — `ABSENT_FROM_SNAPSHOT` · NÃO ESTÁ NESTA ÁRVORE — vive noutra linha
- **impressão do conteúdo medido** — `9420760814`
- **prova** — `git:origin/research/intelligence-bible-engineering-v1:BIBLIA-DE-ENGENHARIA-DA-INTELLIGENCE.md`
- **quem aponta para ela** — `controle/AUTORIDADES-CANONICAS.json`, `docs/operacao/CENSO-DA-INTELLIGENCE.md`
- **o que ela diz de si** — CANDIDATE_FOR_CANONICAL_REVIEW, e ela propria declara IMPLEMENTATION_AUTHORIZED=NO. C-INT-ARB-01 mediu as 9 condicoes de promocao que ela fixa: a 2 (reconciliacao com Motor V2) fechou com 0 conflitos estruturais e a 4 (registo no Control Plane) e esta entrada. Bloqueia na 5: a autoridade vive numa branch lateral e nenhum commit contem Biblia + Motor V2 + censo + know-how + runtime.
- **nota** — NAO CONFUNDIR com A-BIBLIA-INTELIGENCIA: aquele ficheiro chama-se «INVENTARIO DAS LEIS — entrada para a Biblia» e recusa o titulo no proprio cabecalho. O seu §7 lista 12 blocos em falta; esta V0.2 cobre 9. Fora: KIT/KIQ, FIELD_VOICES, DECISION_TELEMETRY.

  | relação | alvo | estado | prova |
  |---|---|---|---|
  | `REFERENCES` | `docs/intelligence/MOTOR-INTELLIGENCE-V2-REQUIREMENTS.md` | **DECLARED** | *authority_absent* |
  | `REFERENCES` | `BIBLIA-CANONICA-DA-COLETA.md` | **DECLARED** | *authority_absent* |
  | `REFERENCES` | `docs/intelligence/INTELLIGENCE-ARBITRATION-V1.md` | **DECLARED** | *authority_absent* |
  | `SUPERSEDES` | `A-BIBLIA-INTELIGENCIA` | **DECLARED** | *authority_absent* |

### CONTRATOS

#### 🟢 CONTRATO DE DESIGN DO SINTONIA

- **conceito que possui** — `CONTRATO_DE_DESIGN`
- **para que serve** — Dizer o que a forma nao pode esconder: NAO SEI visivel, idade do dado ao lado do numero, facto != interpretacao != acao.
- **até onde vale** — Toda superficie que uma pessoa ve.
- **onde vive** — [`docs/design/CONTRATO-DE-DESIGN-SINTONIA.md`](docs/design/CONTRATO-DE-DESIGN-SINTONIA.md)
- **estado declarado** — `CANONICAL`
- **estado medido** — `PRESENT_AND_POINTED` · está aqui, e alguém aponta para ela
- **impressão do conteúdo medido** — `39df42260c`
- **prova** — `git:HEAD:docs/design/CONTRATO-DE-DESIGN-SINTONIA.md`
- **quem aponta para ela** — `CLAUDE.md`, `controle/AUTORIDADES-CANONICAS.json`, `controle/red_team_do_controle.py`
- **o que ela diz de si** — Identico em todas as dez linhas medidas — a unica autoridade do repositorio que nao divergiu. Vence o ADAMA Design System em conflito.

  | relação | alvo | estado | prova |
  |---|---|---|---|
  | `GOVERNS` | `superficie/ask_sintonia.py` | **DECLARED** | *path_exists* |
  | `GOVERNS` | `italia-portale/client/italy-app-model.js` | **DECLARED** | *path_exists* |

#### 🟢 ARQUITETURA DE PRODUTO ATUAL

- **conceito que possui** — `ARQUITETURA_DE_PRODUTO`
- **para que serve** — Vencer quando dois documentos discordarem sobre o que o produto e hoje.
- **até onde vale** — Produto e portal.
- **onde vive** — [`docs/piloto/ARQUITETURA-DE-PRODUTO-ATUAL.md`](docs/piloto/ARQUITETURA-DE-PRODUTO-ATUAL.md)
- **estado declarado** — `CANONICAL`
- **estado medido** — `PRESENT_AND_POINTED` · está aqui, e alguém aponta para ela
- **impressão do conteúdo medido** — `bb6355c401`
- **prova** — `git:HEAD:docs/piloto/ARQUITETURA-DE-PRODUTO-ATUAL.md`
- **quem aponta para ela** — `HANDOFF-CONTA-CLAUDE-SINTONIA-EAME.md`, `PORTAL-CAPABILITY-INVENTORY.md`, `PROMPT-PARA-NOVA-CONTA-CLAUDE.md`, `controle/AUTORIDADES-CANONICAS.json` *(+4)*
- **o que ela diz de si** — Identica em todas as dez linhas medidas.

#### 🟢 CONTRATOS DAS FONTES

- **conceito que possui** — `CONTRATO_DAS_FONTES`
- **para que serve** — O que cada fonte promete entregar, e o que ela nao prova.
- **até onde vale** — Toda fonte que sobe ao degrau CONTRATADA.
- **onde vive** — [`docs/operacao/CONTRATOS-DAS-FONTES-EAME.md`](docs/operacao/CONTRATOS-DAS-FONTES-EAME.md)
- **estado declarado** — `CANONICAL`
- **estado medido** — `PRESENT_AND_POINTED` · está aqui, e alguém aponta para ela
- **impressão do conteúdo medido** — `1aa96613c2`
- **prova** — `git:HEAD:docs/operacao/CONTRATOS-DAS-FONTES-EAME.md`
- **quem aponta para ela** — `AGENTS.md`, `controle/AUTORIDADES-CANONICAS.json`, `medidas/padrao_da_coleta.py`, `system-map/data/architecture.declared.json` *(+2)*
- **o que ela diz de si** — Terceiro degrau da escada da fonte, entre o atlas e o workflow.

  | relação | alvo | estado | prova |
  |---|---|---|---|
  | `GOVERNS` | `regras/italy_contracts.mjs` | **DECLARED** | *path_exists* |

#### 🟢 ATLAS DE FONTES EAME

- **conceito que possui** — `ACERVO_DE_FONTES`
- **para que serve** — O capital parado da casa: que fonte existe, quem publica, onde vive, o que ela entrega — com evidencia guardada.
- **até onde vale** — Toda fonte REGISTADA.
- **onde vive** — [`docs/fontes/ATLAS-DE-FONTES-EAME.md`](docs/fontes/ATLAS-DE-FONTES-EAME.md)
- **estado declarado** — `CANONICAL`
- **estado medido** — `PRESENT_AND_POINTED` · está aqui, e alguém aponta para ela
- **impressão do conteúdo medido** — `508a4ca185`
- **prova** — `git:HEAD:docs/fontes/ATLAS-DE-FONTES-EAME.md`
- **quem aponta para ela** — `AGENTS.md`, `HANDOFF-CONTA-CLAUDE-SINTONIA-EAME.md`, `PROMPT-PARA-NOVA-CONTA-CLAUDE.md`, `candidatas/FONTES-CANDIDATAS.json` *(+12)*
- **o que ela diz de si** — Segundo degrau. Uma linha so existe aqui depois de alguem abrir a fonte e guardar evidencia.

#### 🟢 REGRA DE COLETA EXTERNA

- **conceito que possui** — `REGRA_DE_COLETA_EXTERNA`
- **para que serve** — O que se pode e o que nao se pode ir buscar la fora.
- **até onde vale** — Toda acao de coleta que sai para a rede.
- **onde vive** — [`medidas/REGRA-DE-COLETA-EXTERNA-EAME.md`](medidas/REGRA-DE-COLETA-EXTERNA-EAME.md)
- **estado declarado** — `CANONICAL`
- **estado medido** — `PRESENT_AND_POINTED` · está aqui, e alguém aponta para ela
- **impressão do conteúdo medido** — `ce98fc51bb`
- **prova** — `git:HEAD:medidas/REGRA-DE-COLETA-EXTERNA-EAME.md`
- **quem aponta para ela** — `HANDOFF-CONTA-CLAUDE-SINTONIA-EAME.md`, `PROMPT-PARA-NOVA-CONTA-CLAUDE.md`, `controle/AUTORIDADES-CANONICAS.json`, `system-map/data/architecture.declared.json`
- **o que ela diz de si** — Vive em `medidas/`. `tests/test_coleta_externa.py` procura-a em `docs/regras/` e nao a acha — quatro testes acordam com FileNotFoundError.
- **nota** — BROKEN_POINTER conhecido e medido; o conserto e do dono do teste, nao deste registo.

#### 🔴 MOTOR INTELLIGENCE V2 — REQUISITOS CANONICOS

- **conceito que possui** — `CONTRATO_DO_MOTOR_DE_INTELIGENCIA`
- **para que serve** — Requisitos, gates, estados e proibicoes contra os quais MOTOR_V2_READY e julgado.
- **até onde vale** — A implementacao de um motor de Intelligence. Nao governa a constituicao.
- **onde vive** — `docs/intelligence/MOTOR-INTELLIGENCE-V2-REQUIREMENTS.md` — **não nesta árvore**; em `origin/claude/intelligence-backlog-canonical`
- **estado declarado** — `SUBORDINATE`
- **estado medido** — `ABSENT_FROM_SNAPSHOT` · NÃO ESTÁ NESTA ÁRVORE — vive noutra linha
- **impressão do conteúdo medido** — `def980dea0`
- **prova** — `git:origin/claude/intelligence-backlog-canonical:docs/intelligence/MOTOR-INTELLIGENCE-V2-REQUIREMENTS.md`
- **quem aponta para ela** — `controle/AUTORIDADES-CANONICAS.json`, `docs/operacao/RECONCILIACAO-DA-INTELLIGENCE.md`
- **o que ela diz de si** — SUBORDINATE_IMPLEMENTATION_CONTRACT, arbitrado em C-INT-ARB-01. Testado conceito a conceito contra a Biblia V0.2: 0 conflitos estruturais. A INT-LAW-031 cita-o e PRESERVA a sua exigencia de identidade global de claim, acrescentando a fronteira de que a Intelligence nao fabrica essa identidade se o upstream nao a tem.
- **nota** — Nao apagar: contem requisitos maduros e casos-testemunha que a Biblia nao desce a detalhar.

  | relação | alvo | estado | prova |
  |---|---|---|---|
  | `REFERENCES` | `BIBLIA-DE-ENGENHARIA-DA-INTELLIGENCE.md` | **DECLARED** | *authority_absent* |
  | `REFERENCES` | `docs/intelligence/BACKLOG-OBRIGATORIO.md` | **DECLARED** | *authority_absent* |

### DECISÕES

#### 🟢 DIARIO DE DECISOES

- **conceito que possui** — `DIARIO_DE_DECISOES`
- **para que serve** — Toda decisao, com data e motivo. Decisao que fica so na conversa nao existe.
- **até onde vale** — Todo o projeto.
- **onde vive** — [`docs/decisoes/DIARIO-DE-DECISOES.md`](docs/decisoes/DIARIO-DE-DECISOES.md)
- **estado declarado** — `CANONICAL`
- **estado medido** — `PRESENT_AND_POINTED` · está aqui, e alguém aponta para ela
- **impressão do conteúdo medido** — `8c7007535d`
- **prova** — `git:HEAD:docs/decisoes/DIARIO-DE-DECISOES.md`
- **quem aponta para ela** — `HANDOFF-CONTA-CLAUDE-SINTONIA-EAME.md`, `PROMPT-PARA-NOVA-CONTA-CLAUDE.md`, `controle/AUTORIDADES-CANONICAS.json`, `docs/descoberta/MISSAO-EAME-01.md` *(+2)*
- **cópias divergentes medidas** — 6: `origin/claude/raw-observation-identity-3jbwco`, `origin/claude/sintonia-eame-know-how-v1`, `origin/release/canonical`, `origin/claude/integration-acervo-portal-v1`, `origin/research/delivery-bible-v1`, `origin/claude/biblia-canonica-da-coleta`
- **o que ela diz de si** — Seis versoes distintas medidas em dez linhas — a autoridade mais divergida do repositorio.

### KNOW-HOW

#### 🔴 SINTONIA EAME KNOW-HOW

- **conceito que possui** — `KNOW_HOW`
- **para que serve** — O conhecimento duravel: o que se aprendeu, porque, com que prova e com que consequencia.
- **até onde vale** — Todo o projeto. UM SO — nao existe segundo know-how permitido.
- **onde vive** — `SINTONIA-EAME-KNOW-HOW.md` — **não nesta árvore**; em `origin/claude/sintonia-eame-know-how-v1`
- **estado declarado** — `CANONICAL`
- **estado medido** — `ABSENT_FROM_SNAPSHOT` · NÃO ESTÁ NESTA ÁRVORE — vive noutra linha
- **impressão do conteúdo medido** — `212c4210f4`
- **prova** — `git:origin/claude/sintonia-eame-know-how-v1:SINTONIA-EAME-KNOW-HOW.md`
- **quem aponta para ela** — `AGENTS.md`, `controle/AUTORIDADES-CANONICAS.json`
- **cópias divergentes medidas** — 1: `origin/claude/sintonia-eame-know-how-v1-copy`
- **o que ela diz de si** — AUSENTE DESTA ARVORE. O dono verdadeiro vive numa branch lateral; `main` nao tem know-how nenhum.
- **nota** — A copia esta 50 commits atras do dono. Escrever um SINTONIA-EAME-KNOW-HOW.md novo em `main` criaria a terceira versao — e isso e o ataque RT04.

### REGISTO

#### 🟢 Registo das autoridades canonicas

- **conceito que possui** — `REGISTO_DAS_AUTORIDADES`
- **para que serve** — Ser o indice de quem manda: um conceito, um dono, um ciclo de vida, um caminho.
- **até onde vale** — O Control Plane.
- **onde vive** — [`controle/AUTORIDADES-CANONICAS.json`](controle/AUTORIDADES-CANONICAS.json)
- **estado declarado** — `CANONICAL`
- **estado medido** — `PRESENT_AND_POINTED` · está aqui, e alguém aponta para ela
- **impressão do conteúdo medido** — `7a31f6ced5`
- **prova** — `git:HEAD:controle/AUTORIDADES-CANONICAS.json`
- **quem aponta para ela** — `AGENTS.md`, `controle/censo_do_controle.py`, `controle/portao_do_controle.py`, `system-map/data/architecture.declared.json` *(+1)*
- **o que ela diz de si** — INDICE, NAO BIBLIA. Nao possui nenhuma lei; possui a lista de quem possui.

#### 🟢 Sala de Controle do SINTONIA

- **conceito que possui** — `PONTO_DE_ENTRADA_DO_CONTROL_PLANE`
- **para que serve** — A porta por onde uma pessoa entra e descobre quem governa cada parte da maquina.
- **até onde vale** — Todo agente ou pessoa que abre o repositorio.
- **onde vive** — [`SALA-DE-CONTROLE-SINTONIA.md`](SALA-DE-CONTROLE-SINTONIA.md)
- **estado declarado** — `CANONICAL`
- **estado medido** — `PRESENT_AND_POINTED` · está aqui, e alguém aponta para ela
- **impressão do conteúdo medido** — *não se mede a si própria: o valor mudaria por ser escrito aqui*
- **prova** — `git:HEAD:SALA-DE-CONTROLE-SINTONIA.md`
- **quem aponta para ela** — `.github/workflows/system-map.yml`, `AGENTS.md`, `controle/AUTORIDADES-CANONICAS.json`, `controle/censo_do_controle.py` *(+1)*
- **o que ela diz de si** — GERADA do registo e do censo. Editar a mao e escrever uma verdade que nenhum medidor confirma.

### PORTÕES DE GOVERNANÇA

#### 🟢 Validador do System Map

- **conceito que possui** — `PORTAO_DO_SYSTEM_MAP`
- **para que serve** — Provar que o mapa commitado e o que esta arvore produz — e reprovar quando nao e.
- **até onde vale** — Todo push e todo pull request.
- **onde vive** — [`system-map/scripts/validate_system_map.py`](system-map/scripts/validate_system_map.py)
- **estado declarado** — `CANONICAL`
- **estado medido** — `PRESENT_AND_POINTED` · está aqui, e alguém aponta para ela
- **impressão do conteúdo medido** — `ce78f61dbe`
- **prova** — `git:HEAD:system-map/scripts/validate_system_map.py`
- **quem aponta para ela** — `.github/copilot-instructions.md`, `.github/workflows/system-map.yml`, `AGENTS.md`, `CLAUDE.md` *(+5)*
- **o que ela diz de si** — Falha fechado: erro inesperado tambem e FAIL.

  | relação | alvo | estado | prova |
  |---|---|---|---|
  | `VALIDATES` | `system-map/data/architecture.declared.json` | **OBSERVED** | `system-map/scripts/validate_system_map.py:319` |
  | `VALIDATES` | `system-map/data/state.generated.json` | **DECLARED** | *path_exists* |

#### 🟢 Portao do Control Plane

- **conceito que possui** — `PORTAO_DO_CONTROL_PLANE`
- **para que serve** — Reprovar autoridade que desapareceu, duplicou, divergiu, foi apontada errado, ou foi carimbada de canonica depois de superseded.
- **até onde vale** — O registo das autoridades e a arvore em que ele vive.
- **onde vive** — [`controle/portao_do_controle.py`](controle/portao_do_controle.py)
- **estado declarado** — `CANONICAL`
- **estado medido** — `PRESENT_AND_POINTED` · está aqui, e alguém aponta para ela
- **impressão do conteúdo medido** — `746b8846bb`
- **prova** — `git:HEAD:controle/portao_do_controle.py`
- **quem aponta para ela** — `.github/workflows/system-map.yml`, `AGENTS.md`, `controle/AUTORIDADES-CANONICAS.json`, `controle/censo_do_controle.py` *(+2)*
- **o que ela diz de si** — Falha fechado.

  | relação | alvo | estado | prova |
  |---|---|---|---|
  | `VALIDATES` | `controle/AUTORIDADES-CANONICAS.json` | **OBSERVED** | `controle/portao_do_controle.py:11` |
  | `VALIDATES` | `system-map/data/controle.generated.json` | **DECLARED** | *path_exists* |

#### 🟢 Testes das regras do mapa

- **conceito que possui** — `TESTES_DO_SYSTEM_MAP`
- **para que serve** — Provar que as regras do mapa nao afrouxaram entre uma missao e a seguinte.
- **até onde vale** — O gerador e o validador.
- **onde vive** — [`system-map/tests/test_system_map.py`](system-map/tests/test_system_map.py)
- **estado declarado** — `CANONICAL`
- **estado medido** — `PRESENT_AND_POINTED` · está aqui, e alguém aponta para ela
- **impressão do conteúdo medido** — `0f24994734`
- **prova** — `git:HEAD:system-map/tests/test_system_map.py`
- **quem aponta para ela** — `.github/workflows/system-map.yml`, `AGENTS.md`, `controle/AUTORIDADES-CANONICAS.json`, `system-map/README.md` *(+1)*
- **o que ela diz de si** — Corre no CI, passo 4.

  | relação | alvo | estado | prova |
  |---|---|---|---|
  | `VALIDATES` | `system-map/scripts/generate_system_map.py` | **DECLARED** | *path_exists* |

#### 🟢 As sete maneiras de o caminho da coleta mentir

- **conceito que possui** — `PORTAO_DA_COLETA_CANONICA`
- **para que serve** — Fechar as sete formas conhecidas de «erro» virar «rejeicao» e «nao sei» virar «nao».
- **até onde vale** — O caminho da coleta.
- **onde vive** — [`provas/testa_coleta_canonica.py`](provas/testa_coleta_canonica.py)
- **estado declarado** — `CANONICAL`
- **estado medido** — `PRESENT_AND_POINTED` · está aqui, e alguém aponta para ela
- **impressão do conteúdo medido** — `4f6ce8d858`
- **prova** — `git:HEAD:provas/testa_coleta_canonica.py`
- **quem aponta para ela** — `.github/workflows/system-map.yml`, `controle/AUTORIDADES-CANONICAS.json`, `docs/operacao/CENSO-DA-INTELLIGENCE.md`, `system-map/data/architecture.declared.json`
- **o que ela diz de si** — Corre no CI, passo 4b.

#### 🟢 O padrao do departamento de coleta

- **conceito que possui** — `PADRAO_DA_COLETA`
- **para que serve** — Reprovar quando o padrao do departamento de coleta piora.
- **até onde vale** — COLETA.
- **onde vive** — [`medidas/padrao_da_coleta.py`](medidas/padrao_da_coleta.py)
- **estado declarado** — `CANONICAL`
- **estado medido** — `PRESENT_AND_POINTED` · está aqui, e alguém aponta para ela
- **impressão do conteúdo medido** — `e6a12f1f60`
- **prova** — `git:HEAD:medidas/padrao_da_coleta.py`
- **quem aponta para ela** — `.github/workflows/system-map.yml`, `controle/AUTORIDADES-CANONICAS.json`, `docs/operacao/CENSO-DA-COLETA.md`, `medidas/PADRAO-DA-COLETA-CHAO.json` *(+2)*
- **o que ela diz de si** — Corre no CI, passo 3.

### POLÍTICA

#### 🟢 Os dentes da lei — workflow do System Map

- **conceito que possui** — `CI_DO_SYSTEM_MAP`
- **para que serve** — Transformar a lei escrita em AGENTS.md num portao que reprova, e nao num pedido por favor.
- **até onde vale** — Todo push e todo pull request.
- **onde vive** — [`.github/workflows/system-map.yml`](.github/workflows/system-map.yml)
- **estado declarado** — `CANONICAL`
- **estado medido** — `PRESENT_AND_POINTED` · está aqui, e alguém aponta para ela
- **impressão do conteúdo medido** — `b2b2caff21`
- **prova** — `git:HEAD:.github/workflows/system-map.yml`
- **quem aponta para ela** — `AGENTS.md`, `controle/AUTORIDADES-CANONICAS.json`, `system-map/data/architecture.declared.json`
- **o que ela diz de si** — TEXTO NAO REPROVA NADA. WORKFLOW REPROVA.

  | relação | alvo | estado | prova |
  |---|---|---|---|
  | `REFERENCES` | `system-map/scripts/scan_repo.py` | **OBSERVED** | `.github/workflows/system-map.yml:71` |
  | `REFERENCES` | `system-map/scripts/generate_system_map.py` | **OBSERVED** | `.github/workflows/system-map.yml:76` |
  | `REFERENCES` | `system-map/scripts/validate_system_map.py` | **OBSERVED** | `.github/workflows/system-map.yml:84` |
  | `REFERENCES` | `medidas/padrao_da_coleta.py` | **OBSERVED** | `.github/workflows/system-map.yml:87` |
  | `REFERENCES` | `system-map/tests/test_system_map.py` | **OBSERVED** | `.github/workflows/system-map.yml:90` |
  | `REFERENCES` | `provas/testa_coleta_canonica.py` | **OBSERVED** | `.github/workflows/system-map.yml:96` |

### OBSERVADORES

#### 🟢 Scanner do repositorio

- **conceito que possui** — `MEDICAO_DA_ARVORE`
- **para que serve** — Medir ficheiros, imports, chamadas, workflows e artefactos — sem que ninguem os declare a mao.
- **até onde vale** — A arvore inteira.
- **onde vive** — [`system-map/scripts/scan_repo.py`](system-map/scripts/scan_repo.py)
- **estado declarado** — `CANONICAL`
- **estado medido** — `PRESENT_AND_POINTED` · está aqui, e alguém aponta para ela
- **impressão do conteúdo medido** — `2721f4eace`
- **prova** — `git:HEAD:system-map/scripts/scan_repo.py`
- **quem aponta para ela** — `.github/workflows/system-map.yml`, `AGENTS.md`, `controle/AUTORIDADES-CANONICAS.json`, `system-map/README.md` *(+1)*
- **o que ela diz de si** — Mede. Nao decide. O que ele nao consegue saber fica no ficheiro declarado.

  | relação | alvo | estado | prova |
  |---|---|---|---|
  | `OBSERVES` | `_gavetas.py` | **OBSERVED** | `system-map/scripts/scan_repo.py:49` |

#### 🟢 Gerador do System Map

- **conceito que possui** — `PROJECAO_DA_ARQUITETURA`
- **para que serve** — Juntar o que foi medido com o que foi declarado e produzir a projecao.
- **até onde vale** — O mapa.
- **onde vive** — [`system-map/scripts/generate_system_map.py`](system-map/scripts/generate_system_map.py)
- **estado declarado** — `CANONICAL`
- **estado medido** — `PRESENT_AND_POINTED` · está aqui, e alguém aponta para ela
- **impressão do conteúdo medido** — `f5e721ab6a`
- **prova** — `git:HEAD:system-map/scripts/generate_system_map.py`
- **quem aponta para ela** — `.github/copilot-instructions.md`, `.github/workflows/system-map.yml`, `AGENTS.md`, `CLAUDE.md` *(+9)*
- **o que ela diz de si** — DERIVADO. O mapa nasce do repo; o repo nunca nasce do mapa. Este ficheiro NAO e dono de arquitetura nenhuma — e o consumidor dela.

  | relação | alvo | estado | prova |
  |---|---|---|---|
  | `OBSERVES` | `system-map/data/architecture.declared.json` | **OBSERVED** | `system-map/scripts/generate_system_map.py:1817` |
  | `OBSERVES` | `controle/AUTORIDADES-CANONICAS.json` | **OBSERVED** | `system-map/scripts/generate_system_map.py:1207` |

#### 🟢 Censo do Control Plane

- **conceito que possui** — `MEDICAO_DO_CONTROL_PLANE`
- **para que serve** — Medir, para cada autoridade declarada: se o caminho existe, que SHA tem, quando mudou, quem aponta para ela, e que arestas tem prova.
- **até onde vale** — O registo das autoridades.
- **onde vive** — [`controle/censo_do_controle.py`](controle/censo_do_controle.py)
- **estado declarado** — `CANONICAL`
- **estado medido** — `PRESENT_AND_POINTED` · está aqui, e alguém aponta para ela
- **impressão do conteúdo medido** — `9c14af304f`
- **prova** — `git:HEAD:controle/censo_do_controle.py`
- **quem aponta para ela** — `.github/workflows/system-map.yml`, `AGENTS.md`, `controle/AUTORIDADES-CANONICAS.json`, `controle/portao_do_controle.py` *(+2)*
- **o que ela diz de si** — Ele e quem escreve OBSERVED. O registo declarado nunca escreve.

  | relação | alvo | estado | prova |
  |---|---|---|---|
  | `OBSERVES` | `controle/AUTORIDADES-CANONICAS.json` | **OBSERVED** | `controle/censo_do_controle.py:8` |

#### 🟢 Censo da coleta

- **conceito que possui** — `CENSO_DA_COLETA`
- **para que serve** — Medir o estado real do departamento de coleta.
- **até onde vale** — COLETA.
- **onde vive** — [`system-map/scripts/censo_da_coleta.py`](system-map/scripts/censo_da_coleta.py)
- **estado declarado** — `CANONICAL`
- **estado medido** — `PRESENT_AND_POINTED` · está aqui, e alguém aponta para ela
- **impressão do conteúdo medido** — `3fa99e2b21`
- **prova** — `git:HEAD:system-map/scripts/censo_da_coleta.py`
- **quem aponta para ela** — `.github/workflows/system-map.yml`, `AGENTS.md`, `controle/AUTORIDADES-CANONICAS.json`, `docs/operacao/CENSO-DA-COLETA.md` *(+1)*
- **o que ela diz de si** — Mede.

#### 🟢 Pente fino da coleta

- **conceito que possui** — `PENTE_FINO_DA_COLETA`
- **para que serve** — A segunda passagem sobre o que a coleta trouxe.
- **até onde vale** — COLETA.
- **onde vive** — [`system-map/scripts/pente_fino_da_coleta.py`](system-map/scripts/pente_fino_da_coleta.py)
- **estado declarado** — `CANONICAL`
- **estado medido** — `PRESENT_AND_POINTED` · está aqui, e alguém aponta para ela
- **impressão do conteúdo medido** — `7c6f8bd541`
- **prova** — `git:HEAD:system-map/scripts/pente_fino_da_coleta.py`
- **quem aponta para ela** — `.github/workflows/system-map.yml`, `AGENTS.md`, `controle/AUTORIDADES-CANONICAS.json`, `system-map/data/architecture.declared.json`
- **o que ela diz de si** — Mede.

### HANDOFFS — memória, **não** autoridade

#### 🟢 Handoff · build da reuniao

- **conceito que possui** — *nenhum — é ponteiro*
- **para que serve** — Onde a build da reuniao parou e o que faltava.
- **até onde vale** — Uma sessao.
- **onde vive** — [`HANDOFF-BUILD-DA-REUNIAO.md`](HANDOFF-BUILD-DA-REUNIAO.md)
- **estado declarado** — `HISTORICAL`
- **estado medido** — `PRESENT_AND_POINTED` · está aqui, e alguém aponta para ela
- **impressão do conteúdo medido** — `d0fbc49d24`
- **prova** — `git:HEAD:HANDOFF-BUILD-DA-REUNIAO.md`
- **quem aponta para ela** — `controle/AUTORIDADES-CANONICAS.json`, `docs/operacao/INTELLIGENCE-MAP-UNIVERSE.json`, `system-map/data/architecture.declared.json`
- **o que ela diz de si** — MEMORIA. Nao manda em nada; conta o que aconteceu.

#### 🟢 Handoff de conta

- **conceito que possui** — *nenhum — é ponteiro*
- **para que serve** — Passar o repositorio para outra conta quando a que o construiu acabou.
- **até onde vale** — Uma transicao de conta.
- **onde vive** — [`HANDOFF-CONTA-CLAUDE-SINTONIA-EAME.md`](HANDOFF-CONTA-CLAUDE-SINTONIA-EAME.md)
- **estado declarado** — `HISTORICAL`
- **estado medido** — `PRESENT_AND_POINTED` · está aqui, e alguém aponta para ela
- **impressão do conteúdo medido** — `e301b36612`
- **prova** — `git:HEAD:HANDOFF-CONTA-CLAUDE-SINTONIA-EAME.md`
- **quem aponta para ela** — `PROMPT-PARA-NOVA-CONTA-CLAUDE.md`, `controle/AUTORIDADES-CANONICAS.json`, `tests/test_handoff.py`, `tests/test_metricas.py`
- **o que ela diz de si** — MEMORIA.

#### 🟢 Handoff · V2 em pausa

- **conceito que possui** — *nenhum — é ponteiro*
- **para que serve** — O estado em que a V2 foi parada.
- **até onde vale** — A linha V2.
- **onde vive** — [`HANDOFF-V2-PAUSE.md`](HANDOFF-V2-PAUSE.md)
- **estado declarado** — `HISTORICAL`
- **estado medido** — `PRESENT_AND_POINTED` · está aqui, e alguém aponta para ela
- **impressão do conteúdo medido** — `0e19eef562`
- **prova** — `git:HEAD:HANDOFF-V2-PAUSE.md`
- **quem aponta para ela** — `controle/AUTORIDADES-CANONICAS.json`, `docs/operacao/INTELLIGENCE-MAP-UNIVERSE.json`, `pacote/v21_handoff_json.py`
- **o que ela diz de si** — MEMORIA.

#### 🟢 Depois do portal

- **conceito que possui** — *nenhum — é ponteiro*
- **para que serve** — O que ficou por fazer em 06-09-2026, e porque.
- **até onde vale** — Um dia.
- **onde vive** — [`DEPOIS-DO-PORTAL.md`](DEPOIS-DO-PORTAL.md)
- **estado declarado** — `HISTORICAL`
- **estado medido** — `PRESENT_AND_POINTED` · está aqui, e alguém aponta para ela
- **impressão do conteúdo medido** — `bdf3477ab8`
- **prova** — `git:HEAD:DEPOIS-DO-PORTAL.md`
- **quem aponta para ela** — `controle/AUTORIDADES-CANONICAS.json`
- **o que ela diz de si** — MEMORIA.

#### 🟢 Prompt para a nova conta

- **conceito que possui** — *nenhum — é ponteiro*
- **para que serve** — O texto a colar na primeira mensagem de uma conta nova.
- **até onde vale** — Arranque de conta.
- **onde vive** — [`PROMPT-PARA-NOVA-CONTA-CLAUDE.md`](PROMPT-PARA-NOVA-CONTA-CLAUDE.md)
- **estado declarado** — `HISTORICAL`
- **estado medido** — `PRESENT_AND_POINTED` · está aqui, e alguém aponta para ela
- **impressão do conteúdo medido** — `42d1c565e9`
- **prova** — `git:HEAD:PROMPT-PARA-NOVA-CONTA-CLAUDE.md`
- **quem aponta para ela** — `controle/AUTORIDADES-CANONICAS.json`, `docs/design/REVISAO-COMMERCIAL-PRIORITY-V11.md`, `tests/test_handoff.py`
- **o que ela diz de si** — MEMORIA.

#### 🟢 Casco client-demo

- **conceito que possui** — *nenhum — é ponteiro*
- **para que serve** — O que ja estava feito no casco, o que faltava, o que passou a estar certo.
- **até onde vale** — Uma missao de casco.
- **onde vive** — [`CASCO-CLIENT-DEMO.md`](CASCO-CLIENT-DEMO.md)
- **estado declarado** — `HISTORICAL`
- **estado medido** — `PRESENT_AND_POINTED` · está aqui, e alguém aponta para ela
- **impressão do conteúdo medido** — `1bd04ffdcc`
- **prova** — `git:HEAD:CASCO-CLIENT-DEMO.md`
- **quem aponta para ela** — `controle/AUTORIDADES-CANONICAS.json`, `docs/design/HANDOFF-OPPORTUNITY-CANONICAL-FIX.md`
- **o que ela diz de si** — MEMORIA. Nao e a Biblia da Entrega, apesar de falar de casco.

#### 🟢 Inventario de capacidades do portal

- **conceito que possui** — *nenhum — é ponteiro*
- **para que serve** — O que a navegacao mostra hoje, e com que autoridade.
- **até onde vale** — O portal de um dia.
- **onde vive** — [`PORTAL-CAPABILITY-INVENTORY.md`](PORTAL-CAPABILITY-INVENTORY.md)
- **estado declarado** — `HISTORICAL`
- **estado medido** — `PRESENT_AND_POINTED` · está aqui, e alguém aponta para ela
- **impressão do conteúdo medido** — `03b0da54fb`
- **prova** — `git:HEAD:PORTAL-CAPABILITY-INVENTORY.md`
- **quem aponta para ela** — `controle/AUTORIDADES-CANONICAS.json`
- **o que ela diz de si** — MEMORIA.

#### 🟢 Handoff · delta de know-how §108

- **conceito que possui** — *nenhum — é ponteiro*
- **para que serve** — Levar o §108 ate a linha do know-how, que esta missao nao tem autorizacao para escrever.
- **até onde vale** — Uma integracao.
- **onde vive** — [`handoff/KNOW-HOW-DELTA-108-CONTROL-PLANE.md`](handoff/KNOW-HOW-DELTA-108-CONTROL-PLANE.md)
- **estado declarado** — `HISTORICAL`
- **estado medido** — `PRESENT_AND_POINTED` · está aqui, e alguém aponta para ela
- **impressão do conteúdo medido** — `e20731975c`
- **prova** — `git:HEAD:handoff/KNOW-HOW-DELTA-108-CONTROL-PLANE.md`
- **quem aponta para ela** — `controle/AUTORIDADES-CANONICAS.json`
- **o que ela diz de si** — MEMORIA, e nao know-how. Escrever aqui um SINTONIA-EAME-KNOW-HOW.md novo criaria a TERCEIRA versao dele — e isso e o ataque RT04, que o portao desta missao reprova.
- **nota** — Segue o precedente de `handoff/KNOW-HOW-DELTA-107-RECUPERACAO.md`. O dono verdadeiro vive em origin/claude/sintonia-eame-know-how-v1.

#### 🟢 Handoff · correcoes de Opportunity para a linhagem geradora

- **conceito que possui** — *nenhum — é ponteiro*
- **para que serve** — Levar as correcoes do motor de Oportunidade ate a linhagem que gera o pacote canonico.
- **até onde vale** — Uma integracao entre duas branches.
- **onde vive** — [`docs/design/HANDOFF-OPPORTUNITY-CANONICAL-FIX.md`](docs/design/HANDOFF-OPPORTUNITY-CANONICAL-FIX.md)
- **estado declarado** — `HISTORICAL`
- **estado medido** — `PRESENT_AND_POINTED` · está aqui, e alguém aponta para ela
- **impressão do conteúdo medido** — `e55e81caf6`
- **prova** — `git:HEAD:docs/design/HANDOFF-OPPORTUNITY-CANONICAL-FIX.md`
- **quem aponta para ela** — `controle/AUTORIDADES-CANONICAS.json`, `docs/operacao/INTELLIGENCE-MAP-UNIVERSE.json`
- **o que ela diz de si** — MEMORIA. Diz «dono canonico» a falar do dono de OUTRA coisa — o gerador do pacote — e nao a reivindicar-se dono de nada.
- **nota** — Aparecia como UNREGISTERED_CANONICAL_DOCUMENT porque a varredura procura a frase, e nao a intencao. Registado como HANDOFF: e assim que a varredura passa a saber que ele nao manda.

---

## O QUE ESTÁ EM FALTA, DITO NA CARA

| autoridade | estado | vive em |
|---|---|---|
| BIBLIA CANONICA DA COLETA | `CANONICAL` / `ABSENT_FROM_SNAPSHOT` | `origin/claude/raw-observation-identity-3jbwco` |
| BIBLIA DA INTELIGENCIA | `RECOVERY_PENDING` / `ABSENT_FROM_SNAPSHOT` | `origin/claude/integration-acervo-portal-v1` |
| BIBLIA DA ENTREGA / CASCO | `CANDIDATE` / `ABSENT_FROM_SNAPSHOT` | `origin/research/delivery-bible-v1` |
| SINTONIA EAME KNOW-HOW | `CANONICAL` / `ABSENT_FROM_SNAPSHOT` | `origin/claude/sintonia-eame-know-how-v1` |
| BIBLIA DE ENGENHARIA DA INTELLIGENCE | `CANDIDATE` / `ABSENT_FROM_SNAPSHOT` | `origin/research/intelligence-bible-engineering-v1` |
| MOTOR INTELLIGENCE V2 — REQUISITOS CANONICOS | `SUBORDINATE` / `ABSENT_FROM_SNAPSHOT` | `origin/claude/intelligence-backlog-canonical` |

**Um ficheiro existir não prova que ele ainda manda — e não estar aqui não
prova que ele não existe.** As linhas acima foram medidas no git, não
presumidas: cada uma diz a ref onde a autoridade realmente está.

---

## DECLARADO ≠ OBSERVADO

O censo mediu **58** relações de governo declaradas neste
registo. Delas, **35** têm prova apontável
(ficheiro e linha dentro do texto da própria autoridade) e
**23** continuam apenas declaradas.

Uma relação declarada **não passa a observada por estar desenhada**. Quem
prova que uma lei governa uma peça é o texto da lei a nomear a peça — não o
mundo a mencionar a peça, e não o ficheiro existir.

---

## COMO A INTEGRIDADE DISTO É VALIDADA

```bash
py controle/censo_do_controle.py     # mede o registo contra a árvore
py controle/portao_do_controle.py    # reprova quem mentir
```

O portão corre no CI, no mesmo workflow do mapa. **Texto não reprova nada;
portão reprova.**
