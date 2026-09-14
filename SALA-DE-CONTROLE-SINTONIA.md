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
| **COLETA** | BIBLIA CANONICA DA COLETA | nesta árvore | 🟢 CANONICAL |
| **INTELIGÊNCIA** | BIBLIA DA INTELIGENCIA | `origin/claude/integration-acervo-portal-v1` | 🔴 RECOVERY_PENDING |
| **INTELIGÊNCIA** | BIBLIA DE ENGENHARIA DA INTELLIGENCE | nesta árvore | 🟢 CANONICAL |
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
- **impressão do conteúdo medido** — `cc861488d8`
- **prova** — `git:HEAD:AGENTS.md`
- **quem aponta para ela** — `.github/copilot-instructions.md`, `.github/workflows/system-map.yml`, `BIBLIA-CANONICA-DA-COLETA.md`, `CLAUDE.md` *(+21)*
- **o que ela diz de si** — A lei escrita. Os outros ficheiros de instrucao apontam para aqui e nao a repetem.

  | relação | alvo | estado | prova |
  |---|---|---|---|
  | `GOVERNS` | `system-map/scripts/generate_system_map.py` | **OBSERVED** | `AGENTS.md:312` |
  | `GOVERNS` | `system-map/scripts/validate_system_map.py` | **OBSERVED** | `AGENTS.md:313` |
  | `GOVERNS` | `system-map/data/architecture.declared.json` | **OBSERVED** | `AGENTS.md:338` |
  | `GOVERNS` | `system-map/tests/test_system_map.py` | **OBSERVED** | `AGENTS.md:314` |
  | `GOVERNS` | `_gavetas.py` | **OBSERVED** | `AGENTS.md:550` |
  | `GOVERNS` | `regras/LEIA-ANTES-DE-COLETAR.md` | **OBSERVED** | `AGENTS.md:581` |
  | `GOVERNS` | `candidatas/fonte_nova.py` | **OBSERVED** | `AGENTS.md:610` |
  | `GOVERNS` | `controle/AUTORIDADES-CANONICAS.json` | **DECLARED** | *path_exists* |
  | `GOVERNS` | `controle/censo_do_controle.py` | **DECLARED** | *path_exists* |
  | `GOVERNS` | `controle/portao_do_controle.py` | **DECLARED** | *path_exists* |
  | `REFERENCES` | `docs/fontes/ATLAS-DE-FONTES-EAME.md` | **OBSERVED** | `AGENTS.md:622` |
  | `REFERENCES` | `docs/operacao/CONTRATOS-DAS-FONTES-EAME.md` | **OBSERVED** | `AGENTS.md:623` |
  | `REFERENCES` | `docs/fontes/INDICE-DE-FONTES.md` | **OBSERVED** | `AGENTS.md:627` |
  | `REFERENCES` | `system-map/README.md` | **OBSERVED** | `AGENTS.md:685` |
  | `REFERENCES` | `CLAUDE.md` | **OBSERVED** | `AGENTS.md:683` |
  | `REFERENCES` | `README.md` | **OBSERVED** | `AGENTS.md:684` |

#### 🟢 INSTRUCOES PERMANENTES DO PROJETO

- **conceito que possui** — `INSTRUCOES_PERMANENTES`
- **para que serve** — Regra que vale para todas as missoes futuras, sem depender de alguem lembrar na conversa. Dona da LEI DE DESIGN.
- **até onde vale** — Toda missao neste repositorio; e toda missao que toque em design, UI, casco, portal, icones.
- **onde vive** — [`CLAUDE.md`](CLAUDE.md)
- **estado declarado** — `CANONICAL`
- **estado medido** — `PRESENT_AND_POINTED` · está aqui, e alguém aponta para ela
- **impressão do conteúdo medido** — `b38c2989c5`
- **prova** — `git:HEAD:CLAUDE.md`
- **quem aponta para ela** — `AGENTS.md`, `BIBLIA-CANONICA-DA-COLETA.md`, `README.md`, `SINTONIA-EAME-KNOW-HOW.md` *(+13)*
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
- **impressão do conteúdo medido** — `b9e17e4cd9`
- **prova** — `git:HEAD:README.md`
- **quem aponta para ela** — `AGENTS.md`, `BIBLIA-CANONICA-DA-COLETA.md`, `CLAUDE.md`, `SINTONIA-EAME-KNOW-HOW.md` *(+11)*
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

#### 🟢 BIBLIA CANONICA DA COLETA

- **conceito que possui** — `LEI_DA_COLETA`
- **para que serve** — A constituicao da COLETA: o que entra, com que carimbo, por que porta, e o que nunca pode passar.
- **até onde vale** — Todo o departamento de COLETA e a porta de admissao.
- **onde vive** — [`BIBLIA-CANONICA-DA-COLETA.md`](BIBLIA-CANONICA-DA-COLETA.md)
- **estado declarado** — `CANONICAL`
- **estado medido** — `PRESENT_AND_POINTED` · está aqui, e alguém aponta para ela
- **impressão do conteúdo medido** — `909ba45bac`
- **prova** — `git:HEAD:BIBLIA-CANONICA-DA-COLETA.md`
- **quem aponta para ela** — `AGENTS.md`, `BIBLIA-DE-ENGENHARIA-DA-INTELLIGENCE.md`, `README.md`, `SINTONIA-EAME-KNOW-HOW.md` *(+27)*
- **cópias divergentes medidas** — 3: `origin/claude/sintonia-eame-know-how-v1`, `origin/release/canonical`, `origin/claude/biblia-canonica-da-coleta`
- **o que ela diz de si** — AUSENTE DESTA ARVORE. A lei da coleta existe no Git e nao existe em `main` — quem clona `main` e le CLAUDE.md e mandado consultar um ficheiro que ali nao esta.

  | relação | alvo | estado | prova |
  |---|---|---|---|
  | `GOVERNS` | `admissao/admissao.py` | **OBSERVED** | `BIBLIA-CANONICA-DA-COLETA.md:110` |
  | `GOVERNS` | `regras/proveniencia.py` | **OBSERVED** | `BIBLIA-CANONICA-DA-COLETA.md:180` |
  | `GOVERNS` | `regras/sensor_coleta.py` | **OBSERVED** | `BIBLIA-CANONICA-DA-COLETA.md:1047` |
  | `GOVERNS` | `coleta/coletor.py` | **OBSERVED** | `BIBLIA-CANONICA-DA-COLETA.md:134` |
  | `GOVERNS` | `pedido/pedido.py` | **OBSERVED** | `BIBLIA-CANONICA-DA-COLETA.md:243` |

#### 🔴 BIBLIA DA INTELIGENCIA

- **conceito que possui** — `LEI_DA_INTELIGENCIA`
- **para que serve** — A constituicao da INTELIGENCIA: como dado bruto vira caso com dono, lugar e momento — e o que a transformacao nunca pode inventar.
- **até onde vale** — Todo o departamento de INTELIGENCIA: reguas, motor, provas.
- **onde vive** — `docs/biblia/BIBLIA-DA-INTELIGENCIA-EAME.md` — **não nesta árvore**; em `origin/claude/integration-acervo-portal-v1`
- **estado declarado** — `RECOVERY_PENDING`
- **estado medido** — `ABSENT_FROM_SNAPSHOT` · NÃO ESTÁ NESTA ÁRVORE — vive noutra linha
- **impressão do conteúdo medido** — `ac478fb7e0`
- **prova** — `git:origin/claude/integration-acervo-portal-v1:docs/biblia/BIBLIA-DA-INTELIGENCIA-EAME.md`
- **quem aponta para ela** — `controle/AUTORIDADES-CANONICAS.json`, `docs/intelligence/INTELLIGENCE-ARBITRATION-V1.md`, `docs/operacao/CENSO-DA-INTELLIGENCE.md`
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

#### 🟢 BIBLIA DE ENGENHARIA DA INTELLIGENCE

- **conceito que possui** — `LEI_DA_INTELIGENCIA`
- **para que serve** — A constituicao da Intelligence: fronteiras, identidades analiticas, lineage, run, evidencia, dependencia, crossings, universos, incerteza e saida para a Entrega.
- **até onde vale** — Todo trabalho do lado Intelligence da fronteira COLLECTION -> SALA DE ESPERA -> INTELLIGENCE.
- **onde vive** — [`BIBLIA-DE-ENGENHARIA-DA-INTELLIGENCE.md`](BIBLIA-DE-ENGENHARIA-DA-INTELLIGENCE.md)
- **estado declarado** — `CANONICAL`
- **estado medido** — `PRESENT_AND_POINTED` · está aqui, e alguém aponta para ela
- **impressão do conteúdo medido** — `90e5207cb1`
- **prova** — `git:HEAD:BIBLIA-DE-ENGENHARIA-DA-INTELLIGENCE.md`
- **quem aponta para ela** — `SINTONIA-EAME-KNOW-HOW.md`, `controle/AUTORIDADES-CANONICAS.json`, `docs/intelligence/INTELLIGENCE-CONCEPT-OWNERSHIP-V1.json`, `docs/intelligence/INTELLIGENCE-OBJECT-MODEL-V1.json` *(+6)*
- **o que ela diz de si** — CANONICAL desde 2026-09-14, promovida por C-CTRL-INT-NIGHT-02 com as 9 condicoes da secao 31 re-medidas contra esta arvore: 9/9 PASS. A 5 fechou com a integracao de C-INT-ATOMICITY-01 — Biblia, Biblia da Coleta, know-how, arbitragem e registo coexistem num commit so. A 6 fechou quando os dois bloqueadores se revelaram inexistentes: dez MENCOES contadas como leis, e um CARD_ID lido como caminho. A canonica e esta copia, nesta arvore: CANONICAL_REF deixou de apontar para a branch lateral. IMPLEMENTATION_AUTHORIZED cobre apenas a primeira missao da secao 32, e ainda sujeita aos gates a montante (TRAVA-DA-INTELIGENCIA, e o item real que a propria secao 32 exige). C-INT-BIBLE-CONSISTENCY-01 separou o veredito historico de 2026-09-13 do veredito corrente: o texto declarava CANONICAL = NO tres paginas abaixo de um cabecalho CANONICAL.
- **nota** — NAO CONFUNDIR com A-BIBLIA-INTELIGENCIA: aquele ficheiro chama-se «INVENTARIO DAS LEIS — entrada para a Biblia» e recusa o titulo no proprio cabecalho. O seu §7 lista 12 blocos em falta; esta V0.2 cobre 9. Fora: KIT/KIQ, FIELD_VOICES, DECISION_TELEMETRY.

  | relação | alvo | estado | prova |
  |---|---|---|---|
  | `REFERENCES` | `docs/intelligence/MOTOR-INTELLIGENCE-V2-REQUIREMENTS.md` | **OBSERVED** | `BIBLIA-DE-ENGENHARIA-DA-INTELLIGENCE.md:1246` |
  | `REFERENCES` | `BIBLIA-CANONICA-DA-COLETA.md` | **OBSERVED** | `BIBLIA-DE-ENGENHARIA-DA-INTELLIGENCE.md:70` |
  | `REFERENCES` | `docs/intelligence/INTELLIGENCE-ARBITRATION-V1.md` | **DECLARED** | *path_exists* |
  | `SUPERSEDES` | `A-BIBLIA-INTELIGENCIA` | **OBSERVED** | `registo:A-BIBLIA-INTELIGENCIA.SUPERSEDED_BY` |

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
- **quem aponta para ela** — `AGENTS.md`, `BIBLIA-CANONICA-DA-COLETA.md`, `coleta/eu_regulatorio_executor.py`, `controle/AUTORIDADES-CANONICAS.json` *(+6)*
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
- **quem aponta para ela** — `AGENTS.md`, `BIBLIA-CANONICA-DA-COLETA.md`, `HANDOFF-CONTA-CLAUDE-SINTONIA-EAME.md`, `PROMPT-PARA-NOVA-CONTA-CLAUDE.md` *(+16)*
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
- **quem aponta para ela** — `HANDOFF-CONTA-CLAUDE-SINTONIA-EAME.md`, `PROMPT-PARA-NOVA-CONTA-CLAUDE.md`, `controle/AUTORIDADES-CANONICAS.json`, `docs/biblia/CENSO-DAS-LEIS-DA-COLETA.md` *(+2)*
- **o que ela diz de si** — Vive em `medidas/`. `tests/test_coleta_externa.py` procura-a em `docs/regras/` e nao a acha — quatro testes acordam com FileNotFoundError.
- **nota** — BROKEN_POINTER conhecido e medido; o conserto e do dono do teste, nao deste registo.

#### 🟢 MOTOR INTELLIGENCE V2 — REQUISITOS CANONICOS

- **conceito que possui** — `CONTRATO_DO_MOTOR_DE_INTELIGENCIA`
- **para que serve** — Requisitos, gates, estados e proibicoes contra os quais MOTOR_V2_READY e julgado.
- **até onde vale** — A implementacao de um motor de Intelligence. Nao governa a constituicao.
- **onde vive** — [`docs/intelligence/MOTOR-INTELLIGENCE-V2-REQUIREMENTS.md`](docs/intelligence/MOTOR-INTELLIGENCE-V2-REQUIREMENTS.md)
- **estado declarado** — `SUBORDINATE`
- **estado medido** — `PRESENT_AND_POINTED` · está aqui, e alguém aponta para ela
- **impressão do conteúdo medido** — `def980dea0`
- **prova** — `git:HEAD:docs/intelligence/MOTOR-INTELLIGENCE-V2-REQUIREMENTS.md`
- **quem aponta para ela** — `BIBLIA-DE-ENGENHARIA-DA-INTELLIGENCE.md`, `controle/AUTORIDADES-CANONICAS.json`, `docs/intelligence/INTELLIGENCE-CONCEPT-OWNERSHIP-V1.json`, `provas/arbitragem_da_intelligence.py` *(+1)*
- **o que ela diz de si** — SUBORDINATE_IMPLEMENTATION_CONTRACT, arbitrado em C-INT-ARB-01. Testado conceito a conceito contra a Biblia V0.2: 0 conflitos estruturais. A INT-LAW-031 cita-o e PRESERVA a sua exigencia de identidade global de claim, acrescentando a fronteira de que a Intelligence nao fabrica essa identidade se o upstream nao a tem.
- **nota** — Nao apagar: contem requisitos maduros e casos-testemunha que a Biblia nao desce a detalhar.

  | relação | alvo | estado | prova |
  |---|---|---|---|
  | `REFERENCES` | `BIBLIA-DE-ENGENHARIA-DA-INTELLIGENCE.md` | **DECLARED** | *path_exists* |
  | `REFERENCES` | `docs/intelligence/BACKLOG-OBRIGATORIO.md` | **DECLARED** | *path_exists* |

#### 🟢 MODELO DE OBJETOS DA INTELLIGENCE

- **conceito que possui** — `MODELO_DE_OBJETOS_DA_INTELIGENCIA`
- **para que serve** — O que cada coisa da Intelligence E — especie, dono, quem cria, estados, transicoes permitidas, transicoes proibidas e portoes de promocao. Nao governa comportamento: governa FORMA.
- **até onde vale** — Os objetos da Intelligence, os dominios da Italia sobre a espinha comum, e a fronteira das ferramentas futuras.
- **onde vive** — [`docs/intelligence/INTELLIGENCE-OBJECT-MODEL-V1.json`](docs/intelligence/INTELLIGENCE-OBJECT-MODEL-V1.json)
- **estado declarado** — `SUBORDINATE`
- **estado medido** — `PRESENT_AND_POINTED` · está aqui, e alguém aponta para ela
- **impressão do conteúdo medido** — `e849cf7e6a`
- **prova** — `git:HEAD:docs/intelligence/INTELLIGENCE-OBJECT-MODEL-V1.json`
- **quem aponta para ela** — `controle/AUTORIDADES-CANONICAS.json`, `provas/modelo_de_objetos_da_intelligence.py`, `system-map/data/architecture.declared.json`, `tests/test_o_mapa_da_intelligence_nao_mente.py`
- **o que ela diz de si** — SUBORDINATE_CONTRACT de C-INT-OBJECT-MODEL-01. NAO e canonico e nao compete com a Biblia: ela e a lei, este ficheiro diz a forma dos objetos que ela governa. 25 objetos, 18 aliases arbitrados, 8 portoes, 14 transicoes permitidas, 19 proibidas, 8 dominios da Italia e 8 ferramentas com fronteira escrita. BIBLE_CHANGE_REQUIRED = NO.
- **nota** — DECLARADO, nao gerado: especie de objeto e transicao permitida sao decisoes humanas. Quem confere que a declaracao se sustenta e provas/modelo_de_objetos_da_intelligence.py; quem a ataca e tests/test_modelo_de_objetos_da_intelligence.py.

  | relação | alvo | estado | prova |
  |---|---|---|---|
  | `REFERENCES` | `BIBLIA-DE-ENGENHARIA-DA-INTELLIGENCE.md` | **OBSERVED** | `docs/intelligence/INTELLIGENCE-OBJECT-MODEL-V1.json:5` |
  | `REFERENCES` | `docs/intelligence/INTELLIGENCE-CONCEPT-OWNERSHIP-V3.json` | **OBSERVED** | `docs/intelligence/INTELLIGENCE-OBJECT-MODEL-V1.json:16` |
  | `REFERENCES` | `provas/espinha_da_intelligence.py` | **OBSERVED** | `docs/intelligence/INTELLIGENCE-OBJECT-MODEL-V1.json:41` |

#### 🟢 ARBITRAGEM DA INTELLIGENCE CANONICA

- **conceito que possui** — `ARBITRAGEM_DE_CONCEITOS_DA_INTELIGENCIA`
- **para que serve** — Quem possui cada conceito da Intelligence, e contra que fotografia isso foi medido. Nao governa comportamento: governa NOMES.
- **até onde vale** — Os conceitos da Intelligence e a fronteira deles com Collection e Delivery.
- **onde vive** — [`docs/intelligence/INTELLIGENCE-ARBITRATION-V1.md`](docs/intelligence/INTELLIGENCE-ARBITRATION-V1.md)
- **estado declarado** — `CANONICAL`
- **estado medido** — `PRESENT_AND_POINTED` · está aqui, e alguém aponta para ela
- **impressão do conteúdo medido** — `98d105e0bb`
- **prova** — `git:HEAD:docs/intelligence/INTELLIGENCE-ARBITRATION-V1.md`
- **quem aponta para ela** — `SINTONIA-EAME-KNOW-HOW.md`, `controle/AUTORIDADES-CANONICAS.json`, `provas/arbitragem_da_intelligence.py`, `system-map/data/architecture.declared.json`
- **o que ela diz de si** — CANONICAL
- **nota** — Integrada por C-INT-ATOMICITY-01. O resultado VIVO da arbitragem e INTELLIGENCE-CONCEPT-OWNERSHIP-V3.json, gerado por provas/arbitragem_da_intelligence.py; o V1 e V2 ficam como historia.

  | relação | alvo | estado | prova |
  |---|---|---|---|
  | `GOVERNS` | `docs/intelligence/INTELLIGENCE-CONCEPT-OWNERSHIP-V3.json` | **DECLARED** | *path_exists* |
  | `REFERENCES` | `BIBLIA-DE-ENGENHARIA-DA-INTELLIGENCE.md` | **DECLARED** | *path_exists* |
  | `REFERENCES` | `docs/intelligence/MOTOR-INTELLIGENCE-V2-REQUIREMENTS.md` | **DECLARED** | *path_exists* |

### DECISÕES

#### 🟢 DIARIO DE DECISOES

- **conceito que possui** — `DIARIO_DE_DECISOES`
- **para que serve** — Toda decisao, com data e motivo. Decisao que fica so na conversa nao existe.
- **até onde vale** — Todo o projeto.
- **onde vive** — [`docs/decisoes/DIARIO-DE-DECISOES.md`](docs/decisoes/DIARIO-DE-DECISOES.md)
- **estado declarado** — `CANONICAL`
- **estado medido** — `PRESENT_AND_POINTED` · está aqui, e alguém aponta para ela
- **impressão do conteúdo medido** — `66ee36ef28`
- **prova** — `git:HEAD:docs/decisoes/DIARIO-DE-DECISOES.md`
- **quem aponta para ela** — `BIBLIA-CANONICA-DA-COLETA.md`, `HANDOFF-CONTA-CLAUDE-SINTONIA-EAME.md`, `PROMPT-PARA-NOVA-CONTA-CLAUDE.md`, `SINTONIA-EAME-KNOW-HOW.md` *(+10)*
- **cópias divergentes medidas** — 6: `origin/claude/raw-observation-identity-3jbwco`, `origin/claude/sintonia-eame-know-how-v1`, `origin/release/canonical`, `origin/claude/integration-acervo-portal-v1`, `origin/research/delivery-bible-v1`, `origin/claude/biblia-canonica-da-coleta`
- **o que ela diz de si** — Seis versoes distintas medidas em dez linhas — a autoridade mais divergida do repositorio.

### KNOW-HOW

#### 🟢 SINTONIA EAME KNOW-HOW

- **conceito que possui** — `KNOW_HOW`
- **para que serve** — O conhecimento duravel: o que se aprendeu, porque, com que prova e com que consequencia.
- **até onde vale** — Todo o projeto. UM SO — nao existe segundo know-how permitido.
- **onde vive** — [`SINTONIA-EAME-KNOW-HOW.md`](SINTONIA-EAME-KNOW-HOW.md)
- **estado declarado** — `CANONICAL`
- **estado medido** — `PRESENT_AND_POINTED` · está aqui, e alguém aponta para ela
- **impressão do conteúdo medido** — `c070933cb3`
- **prova** — `git:HEAD:SINTONIA-EAME-KNOW-HOW.md`
- **quem aponta para ela** — `BIBLIA-DE-ENGENHARIA-DA-INTELLIGENCE.md`, `controle/AUTORIDADES-CANONICAS.json`, `controle/red_team_do_controle.py`, `docs/sintonia-scrap/C3-YOUTUBE-RUNTIME-CUTOVER.md` *(+3)*
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
- **impressão do conteúdo medido** — `dff3e09c86`
- **prova** — `git:HEAD:controle/AUTORIDADES-CANONICAS.json`
- **quem aponta para ela** — `SINTONIA-EAME-KNOW-HOW.md`, `controle/censo_do_controle.py`, `controle/portao_do_controle.py`, `docs/intelligence/INTELLIGENCE-ARBITRATION-V1.md` *(+5)*
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
- **quem aponta para ela** — `controle/AUTORIDADES-CANONICAS.json`, `controle/censo_do_controle.py`, `controle/portao_do_controle.py`, `provas/arbitragem_da_intelligence.py`
- **o que ela diz de si** — GERADA do registo e do censo. Editar a mao e escrever uma verdade que nenhum medidor confirma.

### PORTÕES DE GOVERNANÇA

#### 🟢 Validador do System Map

- **conceito que possui** — `PORTAO_DO_SYSTEM_MAP`
- **para que serve** — Provar que o mapa commitado e o que esta arvore produz — e reprovar quando nao e.
- **até onde vale** — Todo push e todo pull request.
- **onde vive** — [`system-map/scripts/validate_system_map.py`](system-map/scripts/validate_system_map.py)
- **estado declarado** — `CANONICAL`
- **estado medido** — `PRESENT_AND_POINTED` · está aqui, e alguém aponta para ela
- **impressão do conteúdo medido** — `a0b488c120`
- **prova** — `git:HEAD:system-map/scripts/validate_system_map.py`
- **quem aponta para ela** — `.github/copilot-instructions.md`, `.github/workflows/system-map.yml`, `AGENTS.md`, `CLAUDE.md` *(+13)*
- **o que ela diz de si** — Falha fechado: erro inesperado tambem e FAIL.

  | relação | alvo | estado | prova |
  |---|---|---|---|
  | `VALIDATES` | `system-map/data/architecture.declared.json` | **OBSERVED** | `system-map/scripts/validate_system_map.py:436` |
  | `VALIDATES` | `system-map/data/state.generated.json` | **DECLARED** | *path_exists* |

#### 🟢 Portao do Control Plane

- **conceito que possui** — `PORTAO_DO_CONTROL_PLANE`
- **para que serve** — Reprovar autoridade que desapareceu, duplicou, divergiu, foi apontada errado, ou foi carimbada de canonica depois de superseded.
- **até onde vale** — O registo das autoridades e a arvore em que ele vive.
- **onde vive** — [`controle/portao_do_controle.py`](controle/portao_do_controle.py)
- **estado declarado** — `CANONICAL`
- **estado medido** — `PRESENT_AND_POINTED` · está aqui, e alguém aponta para ela
- **impressão do conteúdo medido** — `a76b9628f4`
- **prova** — `git:HEAD:controle/portao_do_controle.py`
- **quem aponta para ela** — `SINTONIA-EAME-KNOW-HOW.md`, `controle/AUTORIDADES-CANONICAS.json`, `controle/censo_do_controle.py`, `docs/operacao/CENSO-DA-INTELLIGENCE.md` *(+1)*
- **o que ela diz de si** — Falha fechado.

  | relação | alvo | estado | prova |
  |---|---|---|---|
  | `VALIDATES` | `controle/AUTORIDADES-CANONICAS.json` | **OBSERVED** | `controle/portao_do_controle.py:12` |
  | `VALIDATES` | `system-map/data/controle.generated.json` | **DECLARED** | *path_exists* |

#### 🟢 Testes das regras do mapa

- **conceito que possui** — `TESTES_DO_SYSTEM_MAP`
- **para que serve** — Provar que as regras do mapa nao afrouxaram entre uma missao e a seguinte.
- **até onde vale** — O gerador e o validador.
- **onde vive** — [`system-map/tests/test_system_map.py`](system-map/tests/test_system_map.py)
- **estado declarado** — `CANONICAL`
- **estado medido** — `PRESENT_AND_POINTED` · está aqui, e alguém aponta para ela
- **impressão do conteúdo medido** — `503f9fee64`
- **prova** — `git:HEAD:system-map/tests/test_system_map.py`
- **quem aponta para ela** — `.github/workflows/system-map.yml`, `AGENTS.md`, `BIBLIA-CANONICA-DA-COLETA.md`, `controle/AUTORIDADES-CANONICAS.json` *(+4)*
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
- **impressão do conteúdo medido** — `3c07f20a1a`
- **prova** — `git:HEAD:provas/testa_coleta_canonica.py`
- **quem aponta para ela** — `.github/workflows/system-map.yml`, `BIBLIA-CANONICA-DA-COLETA.md`, `controle/AUTORIDADES-CANONICAS.json`, `docs/biblia/CENSO-DAS-LEIS-DA-COLETA.md` *(+7)*
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
- **quem aponta para ela** — `.github/workflows/system-map.yml`, `BIBLIA-CANONICA-DA-COLETA.md`, `controle/AUTORIDADES-CANONICAS.json`, `docs/biblia/CENSO-DAS-LEIS-DA-COLETA.md` *(+6)*
- **o que ela diz de si** — Corre no CI, passo 3.

### POLÍTICA

#### 🟢 Os dentes da lei — workflow do System Map

- **conceito que possui** — `CI_DO_SYSTEM_MAP`
- **para que serve** — Transformar a lei escrita em AGENTS.md num portao que reprova, e nao num pedido por favor.
- **até onde vale** — Todo push e todo pull request.
- **onde vive** — [`.github/workflows/system-map.yml`](.github/workflows/system-map.yml)
- **estado declarado** — `CANONICAL`
- **estado medido** — `PRESENT_AND_POINTED` · está aqui, e alguém aponta para ela
- **impressão do conteúdo medido** — `c46fa6462a`
- **prova** — `git:HEAD:.github/workflows/system-map.yml`
- **quem aponta para ela** — `AGENTS.md`, `SINTONIA-EAME-KNOW-HOW.md`, `controle/AUTORIDADES-CANONICAS.json`, `docs/sintonia-scrap/C6-ESPECIE-DO-TEXTO.md` *(+5)*
- **o que ela diz de si** — TEXTO NAO REPROVA NADA. WORKFLOW REPROVA.

  | relação | alvo | estado | prova |
  |---|---|---|---|
  | `REFERENCES` | `system-map/scripts/scan_repo.py` | **OBSERVED** | `.github/workflows/system-map.yml:125` |
  | `REFERENCES` | `system-map/scripts/generate_system_map.py` | **OBSERVED** | `.github/workflows/system-map.yml:167` |
  | `REFERENCES` | `system-map/scripts/validate_system_map.py` | **OBSERVED** | `.github/workflows/system-map.yml:184` |
  | `REFERENCES` | `medidas/padrao_da_coleta.py` | **OBSERVED** | `.github/workflows/system-map.yml:443` |
  | `REFERENCES` | `system-map/tests/test_system_map.py` | **OBSERVED** | `.github/workflows/system-map.yml:300` |
  | `REFERENCES` | `provas/testa_coleta_canonica.py` | **OBSERVED** | `.github/workflows/system-map.yml:422` |

### OBSERVADORES

#### 🟢 Scanner do repositorio

- **conceito que possui** — `MEDICAO_DA_ARVORE`
- **para que serve** — Medir ficheiros, imports, chamadas, workflows e artefactos — sem que ninguem os declare a mao.
- **até onde vale** — A arvore inteira.
- **onde vive** — [`system-map/scripts/scan_repo.py`](system-map/scripts/scan_repo.py)
- **estado declarado** — `CANONICAL`
- **estado medido** — `PRESENT_AND_POINTED` · está aqui, e alguém aponta para ela
- **impressão do conteúdo medido** — `20523161e0`
- **prova** — `git:HEAD:system-map/scripts/scan_repo.py`
- **quem aponta para ela** — `.github/workflows/system-map.yml`, `controle/AUTORIDADES-CANONICAS.json`, `docs/sintonia-scrap/C3-YOUTUBE-RUNTIME-CUTOVER.md`, `docs/sintonia-scrap/C4-RUNNER-LOCAL-GPU-ASR.md` *(+4)*
- **o que ela diz de si** — Mede. Nao decide. O que ele nao consegue saber fica no ficheiro declarado.

  | relação | alvo | estado | prova |
  |---|---|---|---|
  | `OBSERVES` | `_gavetas.py` | **OBSERVED** | `system-map/scripts/scan_repo.py:52` |

#### 🟢 Gerador do System Map

- **conceito que possui** — `PROJECAO_DA_ARQUITETURA`
- **para que serve** — Juntar o que foi medido com o que foi declarado e produzir a projecao.
- **até onde vale** — O mapa.
- **onde vive** — [`system-map/scripts/generate_system_map.py`](system-map/scripts/generate_system_map.py)
- **estado declarado** — `CANONICAL`
- **estado medido** — `PRESENT_AND_POINTED` · está aqui, e alguém aponta para ela
- **impressão do conteúdo medido** — `02a01be583`
- **prova** — `git:HEAD:system-map/scripts/generate_system_map.py`
- **quem aponta para ela** — `.github/copilot-instructions.md`, `.github/workflows/system-map.yml`, `AGENTS.md`, `CLAUDE.md` *(+18)*
- **o que ela diz de si** — DERIVADO. O mapa nasce do repo; o repo nunca nasce do mapa. Este ficheiro NAO e dono de arquitetura nenhuma — e o consumidor dela.

  | relação | alvo | estado | prova |
  |---|---|---|---|
  | `OBSERVES` | `system-map/data/architecture.declared.json` | **OBSERVED** | `system-map/scripts/generate_system_map.py:3114` |
  | `OBSERVES` | `controle/AUTORIDADES-CANONICAS.json` | **DECLARED** | *path_exists* |

#### 🟢 Censo do Control Plane

- **conceito que possui** — `MEDICAO_DO_CONTROL_PLANE`
- **para que serve** — Medir, para cada autoridade declarada: se o caminho existe, que SHA tem, quando mudou, quem aponta para ela, e que arestas tem prova.
- **até onde vale** — O registo das autoridades.
- **onde vive** — [`controle/censo_do_controle.py`](controle/censo_do_controle.py)
- **estado declarado** — `CANONICAL`
- **estado medido** — `PRESENT_AND_POINTED` · está aqui, e alguém aponta para ela
- **impressão do conteúdo medido** — `282a4285d9`
- **prova** — `git:HEAD:controle/censo_do_controle.py`
- **quem aponta para ela** — `controle/AUTORIDADES-CANONICAS.json`, `controle/portao_do_controle.py`, `tests/test_atomicidade_da_intelligence.py`
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
- **impressão do conteúdo medido** — `f76b472add`
- **prova** — `git:HEAD:system-map/scripts/censo_da_coleta.py`
- **quem aponta para ela** — `.github/workflows/system-map.yml`, `SINTONIA-EAME-KNOW-HOW.md`, `controle/AUTORIDADES-CANONICAS.json`, `docs/operacao/CENSO-DA-COLETA.md` *(+5)*
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
- **quem aponta para ela** — `.github/workflows/system-map.yml`, `controle/AUTORIDADES-CANONICAS.json`, `system-map/data/architecture.declared.json`, `system-map/scripts/CADEIA-DO-MAPA.json`
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
- **quem aponta para ela** — `controle/AUTORIDADES-CANONICAS.json`, `system-map/data/architecture.declared.json`
- **o que ela diz de si** — MEMORIA. Nao manda em nada; conta o que aconteceu.

#### 🟢 Handoff de conta

- **conceito que possui** — *nenhum — é ponteiro*
- **para que serve** — Passar o repositorio para outra conta quando a que o construiu acabou.
- **até onde vale** — Uma transicao de conta.
- **onde vive** — [`HANDOFF-CONTA-CLAUDE-SINTONIA-EAME.md`](HANDOFF-CONTA-CLAUDE-SINTONIA-EAME.md)
- **estado declarado** — `HISTORICAL`
- **estado medido** — `PRESENT_AND_POINTED` · está aqui, e alguém aponta para ela
- **impressão do conteúdo medido** — `c130434137`
- **prova** — `git:HEAD:HANDOFF-CONTA-CLAUDE-SINTONIA-EAME.md`
- **quem aponta para ela** — `PROMPT-PARA-NOVA-CONTA-CLAUDE.md`, `SINTONIA-EAME-KNOW-HOW.md`, `controle/AUTORIDADES-CANONICAS.json`, `tests/test_atomicidade_da_intelligence.py` *(+2)*
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
- **quem aponta para ela** — `SINTONIA-EAME-KNOW-HOW.md`, `controle/AUTORIDADES-CANONICAS.json`, `pacote/v21_handoff_json.py`
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
- **quem aponta para ela** — `SINTONIA-EAME-KNOW-HOW.md`, `controle/AUTORIDADES-CANONICAS.json`, `docs/design/REVISAO-COMMERCIAL-PRIORITY-V11.md`, `tests/test_handoff.py`
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
- **quem aponta para ela** — `controle/AUTORIDADES-CANONICAS.json`
- **o que ela diz de si** — MEMORIA. Diz «dono canonico» a falar do dono de OUTRA coisa — o gerador do pacote — e nao a reivindicar-se dono de nada.
- **nota** — Aparecia como UNREGISTERED_CANONICAL_DOCUMENT porque a varredura procura a frase, e nao a intencao. Registado como HANDOFF: e assim que a varredura passa a saber que ele nao manda.

---

## O QUE ESTÁ EM FALTA, DITO NA CARA

| autoridade | estado | vive em |
|---|---|---|
| BIBLIA DA INTELIGENCIA | `RECOVERY_PENDING` / `ABSENT_FROM_SNAPSHOT` | `origin/claude/integration-acervo-portal-v1` |
| BIBLIA DA ENTREGA / CASCO | `CANDIDATE` / `ABSENT_FROM_SNAPSHOT` | `origin/research/delivery-bible-v1` |

**Um ficheiro existir não prova que ele ainda manda — e não estar aqui não
prova que ele não existe.** As linhas acima foram medidas no git, não
presumidas: cada uma diz a ref onde a autoridade realmente está.

---

## DECLARADO ≠ OBSERVADO

O censo mediu **64** relações de governo declaradas neste
registo. Delas, **42** têm prova apontável
(ficheiro e linha dentro do texto da própria autoridade) e
**22** continuam apenas declaradas.

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
