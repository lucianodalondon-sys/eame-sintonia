# handoff/paused-v2 · MANIFESTO

**Isto NÃO é dado canônico.** É a saída **parcial** de agentes que estavam
rodando quando a missão foi pausada, em 2026-09-02.

> **Papel de trabalho parcial fica separado do dado canônico.** Misturar os dois
> é guardar o rascunho junto com o contrato assinado: um dia alguém pega o
> errado.

A versão legível por máquina deste mesmo conteúdo está em `MANIFESTO.json`.

---

## ACHADOS-DA-AUDITORIA-NAO-REFUTADOS.json

| | |
|---|---|
| **ORIGIN** | workflow `v21-auditar-pacote` (`wf_2c05414f-38d`) |
| **STATUS** | **PARCIAL** — 38 agentes concluíram; a fase de **refutação não rodou** |
| **INTEGRATED** | **NO** |
| **AUTHORITATIVE** | **NO** |

**Conteúdo:** 99 achados brutos de 12 dimensões de auditoria —
**35 `BLOQUEIA_ENTREGA` · 42 `CORRIGIR_ANTES` · 22 `ANOTAR`**.

### ⚠️ Por que nenhum deles está confirmado

Duas razões independentes, e as duas importam:

1. **A refutação não aconteceu.** O desenho previa 3 céticos independentes por
   achado, sobrevivendo só o que 2 de 3 não derrubassem. Essa fase foi
   interrompida.
2. **O pacote mudava enquanto era auditado.** Um dos próprios achados diz isso:
   *"SOURCES.json mudou 6 vezes durante a auditoria"*. Vários achados já foram
   corrigidos **depois** de medidos.

> **Um achado não refutado não é um defeito: é uma suspeita.** Tratar suspeita
> como defeito faz consertar o que não está quebrado. Tratar como ruído deixa o
> defeito passar. Os dois erros custam caro.

### NEXT ACTION

Reverificar os 35 `BLOQUEIA_ENTREGA` **um a um** contra o `DESIGN-INGEST` atual.
Um achado que não reproduzir já foi corrigido — registre isso e siga.

Provavelmente **já corrigidos** (mencionam estado antigo): os que falam de
`SOURCES`, de `_COLECOES.json` dentro do ingest, de cruzamentos sem
`CLIENT_SAFE`, e de campos em português.

Os que **soam reais e devem ser olhados primeiro**:

- `PROVINCIAL virou REGIONAL em 24 registros client-safe`
- `11 de 14 cruzamentos de rótulo casam a cultura certa com o problema errado`
- `um boletim do Friuli aparece carimbado também como Toscana`
- `«Trentino» virou «Trentino-Alto Adige»`
- `2.222 registros que vão à tela citam "fonte não declarada" como única fonte`

---

## auditoria-pacote.json

| | |
|---|---|
| **ORIGIN** | mesmo workflow — é o *journal* bruto dos 38 agentes |
| **STATUS** | BRUTO |
| **INTEGRATED** | **NO** |
| **AUTHORITATIVE** | **NO** |

Traz o resultado integral de cada agente, inclusive o campo `O_QUE_MEDI` com os
comandos e as contagens que ele rodou.

### NEXT ACTION

Consultar quando for reverificar um achado — aqui está **como ele foi medido na
primeira vez**.

---

## conferencia-de-sentido.json

| | |
|---|---|
| **ORIGIN** | workflow `v21-conferir-sentido` (`wf_2afbff77-eb9`) |
| **STATUS** | **VAZIO** — zero agentes concluíram antes da interrupção |
| **INTEGRATED** | **NO** |
| **AUTHORITATIVE** | **NO** |

**O que ele ia fazer:** ler as 1.017 traduções IT/EN e verificar o que nenhuma
trava mecânica alcança — se o **sentido** atravessou, não só se as peças estão
lá. Dois leitores por lote (um por língua) e um juiz para cada desvio marcado.

Os lotes de entrada foram preparados em `.tmp/v21_semantica/` (102 arquivos de 10
frases), mas **`.tmp/` não vai para o Git**.

### NEXT ACTION

Opcional, e de prioridade menor que a reverificação da auditoria. Se for refeito,
os lotes se regeram a partir de `data/i18n/v21-traducoes.json`.
