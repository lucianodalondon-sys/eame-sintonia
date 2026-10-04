# docs/intelligence

Documentação canônica do **Motor Intelligence V2**.

| Arquivo | Papel |
|---|---|
| [`MOTOR-INTELLIGENCE-V2-REQUIREMENTS.md`](./MOTOR-INTELLIGENCE-V2-REQUIREMENTS.md) | contrato canônico de requisitos |
| [`BACKLOG-OBRIGATORIO.md`](./BACKLOG-OBRIGATORIO.md) | dívida e ações obrigatórias antes de Motor V2 Ready |

## Como usar

- **Requisitos** declaram a lei: gates, estados, proibições. Implementação que
  não consegue cumprir abre item no backlog — não relaxa o requisito.
- **Backlog** registra o que falta. Enquanto houver item `BLOCKING` ou item não
  classificado, `MOTOR_V2_READY` permanece `NÃO`.

Estado atual:

```
MOTOR_V2_READY   = NÃO
BACKLOG_REVIEWED = NÃO
```
