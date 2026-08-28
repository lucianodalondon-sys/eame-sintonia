# MISSÃO EAME 01 — DESCOBRIR O TERRITÓRIO E CONSTRUIR A PRIMEIRA PROVA VIVA

| Campo | Valor |
|---|---|
| **Repositório** | `lucianodalondon-sys/eame-sintonia` |
| **Escopo** | France · Spain · Italy · European common layer |
| **Status** | EM CURSO — Fase 0 concluída (casa preparada) |
| **Briefing recebido** | 2026-08-28 |
| **Última atualização** | 2026-08-28 |

---

## OBJETIVO

Esta é a primeira missão do SINTONIA EAME. **O objetivo não é construir o produto final.**

O objetivo é descobrir, com fontes e exemplos reais, tudo que poderemos potencialmente
observar, cruzar e transformar em ferramentas para a ADAMA EAME — e, ao mesmo tempo,
começar um protótipo mínimo do portal que funcione como **laboratório** das descobertas.

A missão precisa responder:

1. O que conseguimos saber hoje sobre agricultura, mercado, ciência, pessoas, clima,
   fitossanidade, regulatório e concorrência na França, Espanha e Itália?
2. Quais dessas informações conseguimos coletar de forma **repetível**?
3. O que conseguimos **cruzar**?
4. Quais ferramentas úteis para a ADAMA poderiam nascer desses cruzamentos?
5. Quais capacidades já conseguimos **demonstrar usando dados reais**?

---

## LEI CENTRAL

```
SOURCE → EVIDENCE → DATA → CROSSING → CAPABILITY → TOOL → PORTAL
```

Nunca: `PORTAL → inventar dado para preencher.`

---

## FASES

| Fase | O quê | Status |
|---|---|---|
| **0** | Preparar a casa — estrutura, documentos canônicos, regras | **CONCLUÍDA** |
| **1** | Investigar os 12 territórios (T1–T12) × 4 recortes, regra das 5 fontes | não iniciada |
| **2** | Capturar amostras reais das fontes GREEN/YELLOW importantes | não iniciada |
| **3** | Converter descoberta em capacidades (`docs/capacidades/`) | não iniciada |
| **4** | Testar cruzamentos (`docs/cruzamentos/`) | não iniciada |
| **5** | Qualificar ferramentas (`docs/ferramentas/`) | não iniciada |
| **6** | Protótipo vivo em `prototype/portal/` — só depois de exemplos reais suficientes | não iniciada |
| **7** | Casos WOW (`docs/apresentacao/`) — registro contínuo, meta 5–10 | não iniciada |
| **8** | People graph experimental — amostra inicial, teste de sustentabilidade técnica | não iniciada |

Os 12 territórios, a regra das cinco fontes e a ficha obrigatória da fonte vivem em
`docs/fontes/ATLAS-DE-FONTES-EAME.md` — não são reproduzidos aqui.

---

## PROTÓTIPO VIVO

Local: `prototype/portal/`. É **laboratório, não produto final**.

Seções possíveis: HOME, FRANCE, SPAIN, ITALY, CROPS, CLIMATE, PEST & DISEASE, SCIENCE,
PEOPLE, COMPETITORS, REGULATORY, OPPORTUNITIES, SOURCES.

**Não é obrigatório implementar todas.** Uma seção só é criada quando existe conteúdo real
que justifique sua existência. Todo bloco carrega estado visível REAL / DERIVED / DEMO /
CONCEPT (definidos em `docs/apresentacao/CASOS-PARA-APRESENTACAO.md`).

---

## PEOPLE GRAPH EXPERIMENTAL

Avaliar, com **amostra inicial apenas**, se é tecnicamente sustentável estruturar:

```
PERSON → ORGANIZATION → COUNTRY → REGION → CROP → TOPIC → PAPER → DOCUMENT → EVENT → SOCIAL PROFILE
```

O objetivo é descobrir se a rede se sustenta, não construí-la.

---

## NÃO FAZER NESTA MISSÃO

- banco definitivo;
- crawler em escala;
- scraping agressivo;
- ranking universal;
- classificador de IA definitivo;
- arquitetura complexa antecipada;
- design sofisticado;
- apresentação final;
- cópia automática de componentes do Sintonia Brasil.

---

## DISCIPLINA

- Branch dedicada; nunca direto em `main`.
- Commits pequenos e semanticamente claros.
- **Não apagar evidência anterior para tornar relatório mais bonito.**
- Hipótese que cai é registrada como caída, em `docs/capacidades/` §HIPÓTESES DERRUBADAS.
  Não se reescreve a história.
- Achado novo → documento canônico → evidência preservada → commit. Não fica só na conversa.
- Prioridade: **EVIDÊNCIA > CONTEXTO · ARQUIVO > MEMÓRIA DA CONVERSA · MEDIÇÃO > EXPLICAÇÃO**.

---

## CHECKPOINTS

Cada checkpoint informa: HEAD · arquivos alterados · achados novos · evidências novas ·
hipóteses derrubadas · decisões necessárias · próximo trabalho.
Não reproduzir o que já está registrado em arquivo — referenciar.

---

## PERGUNTA FINAL

A missão só termina quando pudermos responder:

> **Se tivéssemos que apresentar o SINTONIA EAME amanhã para a ADAMA, quais capacidades
> conseguiríamos demonstrar com dados reais e quais ainda seriam apenas visão?**

Separando rigorosamente COMPROVADO · INFERÊNCIA · HIPÓTESE · NÃO SEI.

O sucesso **não** se mede por quantidade de código. Mede-se por:
**capacidades reais descobertas + cruzamentos reais provados + casos reais capazes de
demonstrar valor para a ADAMA.**

---

## LACUNAS ABERTAS

Perguntas que a missão não responde sozinha — ver `docs/decisoes/DIARIO-DE-DECISOES.md`,
seção PERGUNTAS PENDENTES. A mais bloqueante: **P-003 — que dados do portfólio da ADAMA
EAME estarão disponíveis?**, sem a qual o cruzamento X-004
(REGULATORY + ADAMA PORTFOLIO + CROP + PEST) não pode ser testado.
