# FLUXO DE DADOS DA INTELLIGENCE — ITÁLIA

```
MISSAO     C-INT-DATA-DEMAND-IT-01
ESPECIE    MAPA DE LEITURA — NAO DECLARA ARQUITETURA, DESENHA A QUE JA FOI DECLARADA
MEDIDO_EM  2026-09-14
IRMAO      DATA-DEMAND-MATRIX-ITALY.md   (a matriz; este e o mapa)
```

> A ordem é a do `README`, e nunca a inversa:
> `SOURCE → EVIDENCE → DATA → CROSSING → CAPABILITY → TOOL → PORTAL`.
>
> Este ficheiro lê-se **da esquerda para a direita**. Ler da direita para a esquerda —
> partir da tela para procurar o dado — é o erro que a `REGRA ZERO` proíbe.

---

## O MAPA

```
DADO  ─────────────────▶  INTELLIGENCE  ─────▶  CRUZAMENTO  ─────▶  FERRAMENTA
```

| DADO (família) | n.º | INTELLIGENCE que produz | CRUZAMENTO | FERRAMENTA(S) que consomem | estado |
|---|---:|---|---|---|---|
| boletim fitossanitário regional | 122 | `OBSERVED_FIELD_SIGNAL` | `X-FIELD-x-PORTFOLIO` | Opportunity · Portfolio | 🟢 POSSIBLE |
| boletim + janela | 122 / 7 | janela composta | `X-FIELD-x-JANELA` | Crop Windows · Opportunity | 🟡 PARTIAL |
| rótulo oficial ADAMA | 2.030 | `LABEL_FACT` | `X-JANELA-x-PORTFOLIO` | Label Int. · Portfolio · Opportunity | 🟡 PARTIAL |
| registo nacional + substância | 47 / 203 | `REGULATORY_FACT` | `X-REGULATORIO-x-PORTFOLIO` | Portfolio · Future Radar | 🟢 POSSIBLE |
| resistência confirmada | 34 | `SCIENCE_SIGNAL` | `X-RESISTENCIA-x-PORTFOLIO` | Scientific Int. · Portfolio | 🟢 POSSIBLE |
| preço por praça | 157 | contexto de mercado | `X-MERCADO-x-CULTURA` | Market Pulse | 🟡 PARTIAL |
| publicação científica | 88 | `SCIENCE_SIGNAL` | `X-FIELD-x-SCIENCE` | Scientific Int. · Opportunity | 🔴 NOT_POSSIBLE |
| publicação científica | 88 | `SCIENCE_SIGNAL` | `X-CIENCIA-x-PORTFOLIO` | Scientific Int. · Portfolio | 🔴 NOT_POSSIBLE |
| série agrometeorológica | 44 | `AGROCLIMATIC_SIGNAL` | `X-FIELD-x-CLIMA` | Crop Windows · Opportunity | 🔴 NOT_POSSIBLE |
| comunicação de concorrente | 577 | `COMPANY_CLAIM` | `X-CONCORRENCIA-x-CAMPO` | Competitor Watch | 🔴 NOT_POSSIBLE |
| comunicação de concorrente | 577 | `COMPANY_CLAIM` | `X-CONCORRENCIA-x-PORTFOLIO` | Competitor Watch · Portfolio | 🔴 NOT_POSSIBLE |
| voz pública | 79 | candidata a `OBSERVED_FIELD_SIGNAL` | `X-VOZ-x-CAMPO` | Field Voices · Opportunity | 🔴 NOT_POSSIBLE |
| **registo de concorrente** | **0** | `REGULATORY_FACT` | — | Competitor Watch · Label Int. | ⚫ **A FAMÍLIA NÃO EXISTE** |
| **rótulo de concorrente** | **0** | `LABEL_FACT` | — | Label Intelligence | ⚫ **A FAMÍLIA NÃO EXISTE** |

```
🟢 3    🟡 3    🔴 6    ⚫ 2 familias inexistentes
```

---

## ONDE O FLUXO SE PARTE, E É SEMPRE NO MESMO SÍTIO

```
        DADO                    INTELLIGENCE              CRUZAMENTO
   ┌─────────────┐          ┌─────────────────┐       ┌──────────────┐
   │  o boletim  │          │  o sinal existe │       │   e aqui     │
   │  diz o nome │ ───OK──▶ │  e tem quando   │ ──X──▶│   para       │
   │  da praga   │          │  e tem onde     │       │              │
   └─────────────┘          └─────────────────┘       └──────────────┘
                                                        falta ISSUE_ID
```

Seis cruzamentos morrem entre `INTELLIGENCE` e `CRUZAMENTO` — **nunca antes**. Não é
problema de fonte, nem de coleta, nem de volume:

```
172 nomes de praga e doenca citados em texto livre nos boletins
 24 ISSUE_IDs normalizados em todo o pacote

O DADO CHEGOU. A IDENTIDADE NAO FOI CUNHADA.
```

---

## UMA FAMÍLIA, MUITAS FERRAMENTAS — E É DE PROPÓSITO

Quatro famílias recolhidas **uma vez** alimentam as nove superfícies. Recolher a mesma
coisa cinco vezes, uma por ferramenta, seria o desperdício que este mapa existe para
impedir.

```
BOLETIM FITOSSANITARIO REGIONAL
   ├── Crop Windows ............. fase fenologica observada
   ├── Opportunity Radar ........ o sinal de campo da convergencia
   ├── Competitor Watch ......... o campo contra o que a empresa anuncia
   ├── Field Voices ............. a voz tecnica com data e lugar
   └── Disease Intelligence ..... o nivel da regua que a entrada sustenta

ROTULO OFICIAL
   ├── Portfolio ................ o uso autorizado
   ├── Label Intelligence ....... o par cultura x alvo, com dose e epoca
   ├── Crop Windows ............. a janela do rotulo
   ├── Opportunity Radar ........ a resposta registada
   └── Competitor Watch ......... a mesma leitura, sem filtro de titular

REGISTO NACIONAL DE PRODUTO
   ├── Portfolio ................ identidade, titular, validade
   ├── Future Radar ............. a caducidade como facto datado
   ├── Label Intelligence ....... a versao na chave
   └── Competitor Watch ......... quem mais esta registado

PUBLICACAO CIENTIFICA
   ├── Scientific Intelligence .. a evidencia e a sua independencia
   ├── Future Radar ............. o sinal fraco com horizonte
   └── Opportunity Radar ........ o que apoia ou contradiz
```

---

## AS DUAS COLUNAS QUE NUNCA SE SOMAM

A concorrência entra **duas vezes**, e as duas nunca partilham contagem:

```
REGULATORY_FACT                      COMPANY_CLAIM
registo nacional                     comunicacao da empresa
autoridade                           alegacao
0 registos hoje                      577 registos hoje
alimenta MT1                         alimenta MT3 (exploratoria)

              COMPANY_CLAIM != REGULATORY_FACT
```

Somá-las num indicador esconderia **qual** das duas está a acontecer — e são justamente as
duas que respondem a perguntas opostas: *quem pode* e *quem está a falar*.

---

## O QUE ESTE MAPA NÃO É

```
NAO e arquitetura. A arquitetura vive em AGRO-CROSSING-GRAPH-V1.md e na Biblia.
NAO e desenho. Nenhuma decisao de UI, casco, icone ou navegacao e tomada aqui.
NAO e plano de coleta. A rota pertence a Collection (INT-LAW-151).
NAO e promessa. Um cruzamento 🟢 diz que a chave existe — nao que o achado existe.
```
