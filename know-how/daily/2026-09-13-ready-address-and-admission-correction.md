# 2026-09-13 — Admission atual, READY e G-READY-02

Este arquivo pertence à trilha canônica `know-how/daily/`. Registra somente o delta durável desta missão; não cria um segundo KNOW-HOW e não substitui `SINTONIA-EAME-KNOW-HOW.md`.

## O QUE mudou no entendimento

A medição anterior feita sobre a branch de governança ficou stale em três pontos importantes quando comparada com a Collection funcional atual (`claude/raw-observation-identity-3jbwco`):

1. `RAW_OBSERVATION_ID` existe e é canonicamente `raw_asset.id`.
2. A Admission funcional não tem a suposta interseção vazia de vocabulário: `coleta/ingresso.py::para_a_porta()` é o tradutor canônico da fronteira, e `admissao.py` já aceita parte do vocabulário canônico/legado por desenho.
3. `ADMISSÕES = 0` não descreve mais o estado funcional: há decisões `SIM` recentes e a medição de recall da porta reporta 42/49.

A lição metodológica é durável:

> MEDIR O CONSUMIDOR SEM PASSAR PELO TRADUTOR CANÔNICO DA FRONTEIRA MEDE UM ATALHO QUE NÃO EXISTE.

E:

> UM RELATÓRIO DE GOVERNANÇA PODE ENVELHECER ENQUANTO A LINHA FUNCIONAL CONTINUA A EVOLUIR; PARA ESTADO ATUAL, REMEDIR A LINHA FUNCIONAL.

## O problema real remanescente

O blocker atual não é a leitura da Admission. É `G-READY-02`: onde a unidade `PRONTO_PARA_INTELIGENCIA` pousa de forma canônica para poder ser descoberta e consumida pela Intelligence.

A Collection já possui:

- contrato READY com owner único em `admissao.pronto_para_inteligencia()`;
- 11 campos fixos conforme `COL-LAW-043`;
- rota/orquestrador que já sabe construir READY;
- uma morada em ficheiro implementada: `data/samples/PRONTO-PARA-INTELIGENCIA/<RUN_ID>.json`.

O que permanece uma decisão arquitetural é se essa espera canônica continua em ficheiro ou ganha armazenamento transacional próprio.

A prova `provas/a_sala_de_espera_nao_tem_morada.py` mede duas saídas legítimas:

### A — reutilizar a morada em ficheiro existente

Vantagens:
- um owner e um destino já existentes;
- zero migration;
- a rota forward já tem `item` e `Decisao` em mãos.

Limitações medidas:
- não oferece naturalmente FK, unicidade e transação de PostgreSQL;
- concorrência e crash/retry não recebem a mesma classe de prova que uma espera transacional.

### B — dar à Sala de Espera uma tabela/armazenamento transacional

Vantagens:
- unicidade, concorrência e crash/retry podem ser provados contra PostgreSQL;
- READY fica ao lado das demais etapas persistidas da estrada.

Consequências:
- nasce uma segunda morada enquanto a saída em ficheiro continuar existindo;
- é obrigatório resolver ONE CONCEPT → ONE OWNER e decidir qual morada permanece canônica;
- a decisão de Admission hoje não possui surrogate persistido próprio, então a relação entre decisão e READY também precisa ser tratada explicitamente, sem inventar identidade por URL/SHA/path.

## Leis que a decisão não pode quebrar

- `RAW_OBSERVATION_ID = raw_asset.id`.
- READY não pode ganhar `storage_path` ou outra morada física dentro do envelope só para resolver descoberta.
- `COL-LAW-043` mantém o contrato READY nos 11 campos canônicos até decisão constitucional explícita em contrário.
- endereço físico ≠ identidade.
- SOURCE_ID não se fabrica.
- DOCUMENT_ID não se fabrica.
- mesmo conteúdo pode pertencer a observações diferentes.
- Collection owns Admission, READY e Sala de Espera; Intelligence é consumidora read-only no boundary inicial.
- `G-READY-02` deve ser decidido antes de criar `INTELLIGENCE_RUN` ou ligar motores.

## PROVA

- Collection funcional medida em `claude/raw-observation-identity-3jbwco` @ `247fbf25958da5bb66a0316b43b73dc80c699d0b` no fechamento da missão que encontrou o delta.
- `provas/a_sala_de_espera_nao_tem_morada.py` documenta e mede `G-READY-01` / `G-READY-02`, o owner do READY, a morada em ficheiro existente e as duas alternativas de arquitetura.
- A tentativa de adicionar referências/morada ao envelope READY causou regressão em provas canônicas e foi corretamente revertida.

## CONSEQUÊNCIA

O próximo passo não é alterar Admission nem começar Intelligence. É uma missão pequena de decisão arquitetural para `G-READY-02`, baseada nas autoridades atuais e em prova real de concorrência/crash/retry quando necessário.

Somente depois de a morada canônica da Sala de Espera estar decidida e provada deve existir a primeira prova:

`READY real → consumidor read-only → INTELLIGENCE_RUN`.

KNOW_HOW_DELTA = ATUALIZADO
