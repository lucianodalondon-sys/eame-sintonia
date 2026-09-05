# SINTONIA EAME

Repositório dedicado **exclusivamente** ao SINTONIA EAME.

Escopo inicial:

- **France**
- **Spain**
- **Italy**
- **European common layer** (camada comum europeia)

---

## PROPÓSITO

Descobrir e provar quais capacidades de inteligência podem formar um SINTONIA para a
**ADAMA EAME** utilizando **dados reais** de França, Espanha, Itália e fontes europeias.

Descobrir **e provar**. Uma capacidade só existe neste repositório quando está provada
contra fonte real.

---

## PRINCÍPIO

```
SOURCE
  → EVIDENCE
    → DATA
      → CROSSING
        → CAPABILITY
          → TOOL
            → PORTAL
```

**Nunca o contrário.**

Não se parte da tela para procurar o dado.
Não se parte da capacidade desejada para procurar a fonte que a justifique.
Parte-se da fonte que existe, do que ela realmente comprova, do dado que dela sai,
do cruzamento que esse dado permite, da capacidade que esse cruzamento sustenta,
da ferramenta que entrega essa capacidade e só então do portal que a apresenta.

---

## ESTADOS DE EVIDÊNCIA

Todo registro deste repositório — fonte, dado, cruzamento, capacidade, afirmação —
carrega **obrigatoriamente** um destes quatro estados:

| Estado | Significado |
|---|---|
| **COMPROVADO** | Verificado contra fonte real, com exemplo real preservado e método de acesso descrito. |
| **INFERÊNCIA** | Derivado logicamente de algo COMPROVADO, mas não verificado diretamente. A derivação precisa estar escrita. |
| **HIPÓTESE** | Suposição plausível ainda não testada. Precisa dizer como seria testada. |
| **NÃO SEI** | Desconhecido. Registrar como NÃO SEI é resultado válido e obrigatório — não preencher com suposição. |

Rebaixar de COMPROVADO para HIPÓTESE é sempre permitido e nunca é retrocesso.
Subir de HIPÓTESE para COMPROVADO exige evidência preservável anexada.

---

## ESTADOS DO PROTÓTIPO

Toda tela, gráfico, número ou demonstração do protótipo carrega **visivelmente** um destes estados:

| Estado | Significado |
|---|---|
| **REAL DATA** | Dado real, de fonte real, rastreável até a fonte. |
| **REAL DATA + DERIVED ANALYSIS** | Base de dado real, com análise/derivação por cima. A derivação precisa estar declarada. |
| **DEMONSTRATION** | Estrutura real, dado ilustrativo. Serve para mostrar a forma, não para afirmar o fato. |
| **CONCEPT ONLY** | Conceito. Não há dado por trás. |

O estado acompanha a tela dentro do próprio protótipo — não só na documentação.

---

## REGRA

> **Nenhuma tela bonita deve ser considerada evidência de que uma capacidade existe.**

Toda capacidade precisa apontar para:

1. **fonte** — qual é, quem publica, onde vive;
2. **exemplo real** — um caso concreto, não uma descrição do que existiria;
3. **método de acesso** — como se chega ao dado (portal, API, download, consulta, licença);
4. **evidência preservável** — algo que sobrevive à reunião: arquivo, captura, registro, amostra;
5. **possível utilização pela ADAMA** — para que serve, para quem, em que decisão.

Capacidade sem os cinco itens não é capacidade: é HIPÓTESE, e assim deve estar registrada.

---

## RELAÇÃO COM O SINTONIA BRASIL

O Sintonia Brasil é **referência metodológica e fonte de aprendizados**.

Este repositório **não é uma cópia** do Sintonia Brasil. Portanto:

- **não** copiar código automaticamente;
- **não** copiar réguas ainda instáveis;
- **não** copiar banco;
- **não** copiar classificadores;
- **não** alterar o repositório brasileiro.

O que se aproveita do Brasil é **método** — a disciplina de fonte→evidência, o rigor de
estados, o formato de prova. O que **não** se aproveita é artefato pronto.
Realidade regulatória, fontes, idiomas, mercado e dados da EAME são outros.

Qualquer reaproveitamento vindo do Brasil deve ser registrado no
`docs/08-decisoes/DIARIO-DE-DECISOES.md`, dizendo o que foi trazido e por quê.

---

## O QUE **NÃO** COMEÇA AGORA

Explicitamente fora de escopo nesta fase:

- crawler massivo;
- banco definitivo;
- IA de classificação;
- dashboard complexo;
- design final;
- coleta em escala.

**Primeiro preparar a casa. Depois a missão.**

A missão em curso é a **MISSÃO EAME 01 — DESCOBRIR O TERRITÓRIO E CONSTRUIR A PRIMEIRA
PROVA VIVA**, definida em `docs/descoberta/MISSAO-EAME-01.md`.

Esta primeira entrega é **apenas estrutura**: pastas, documentos-base e regras de trabalho.
Nenhuma fonte foi pesquisada, nenhum dado foi coletado, nenhuma capacidade foi afirmada.

---

## ESTRUTURA DO REPOSITÓRIO

```
/
├── README.md
├── docs/
│   ├── descoberta/     MISSAO-EAME-01.md — a missão, seu recorte e seu estado
│   ├── fontes/         ATLAS-DE-FONTES-EAME.md — o que existe e como se acessa
│   ├── capacidades/    ATLAS-DE-CAPACIDADES-EAME.md — o que dá para saber, provado
│   ├── cruzamentos/    MATRIZ-DE-CRUZAMENTOS-EAME.md — A + B, e com que chave
│   ├── ferramentas/    CATALOGO-DE-FERRAMENTAS-EAME.md — com o que se faz
│   ├── decisoes/       DIARIO-DE-DECISOES.md — toda decisão, com data e motivo
│   ├── passaporte/     CONTRATO-DO-PASSAPORTE.md — identidade, estado e histórico de
│   │                   toda unidade de informação (D-013)
│   └── apresentacao/   CASOS-PARA-APRESENTACAO.md — o que se mostra e com que estado
├── research/
│   ├── europe/         camada comum europeia
│   ├── france/
│   ├── spain/
│   ├── italy/
│   ├── people/         pesquisadores, técnicos, produtores, influencers
│   └── competitors/
├── data/
│   ├── samples/        amostras reais, com procedência (versionado)
│   ├── passaporte/     EVENTOS.jsonl — o log append-only que é dono do estado de
│   │                   cada unidade de informação
│   ├── raw/            bruto, como saiu da fonte (não versionado)
│   └── normalized/     normalizado (não versionado)
├── prototype/
│   └── portal/         protótipo vivo — laboratório, não produto
├── scripts/
└── tests/
```

**Não criar estrutura adicional sem necessidade comprovada.**

Os documentos canônicos acima são a **memória externa** do projeto. Achado novo vai para o
documento canônico e para o commit — não fica só na conversa.

---

## COMO TRABALHAR AQUI

1. **Nada entra sem estado.** Fonte, dado, capacidade, tela: cada um com seu estado declarado.
2. **NÃO SEI é resposta.** Preferível a preencher com plausibilidade.
3. **Evidência antes de afirmação.** Se não sobrou artefato preservável, não é COMPROVADO.
4. **Decisão vai para o diário.** `docs/08-decisoes/DIARIO-DE-DECISOES.md`, sempre com data e motivo.
5. **País é dimensão, não pasta esquecida.** França, Espanha e Itália têm realidades diferentes;
   o que vale para um não vale automaticamente para os outros. A camada europeia é o que
   comprovadamente vale para todos.
6. **Legalidade e licença fazem parte da ficha da fonte.** Acesso técnico possível não é
   permissão de uso.
7. **Nada entra sem passaporte.** Toda unidade de informação recebe `ITEM_ID` permanente
   na entrada, e o estado dela é projeção de um histórico append-only. Informação nova sem
   passaporte é `REJECT_PIPELINE`, nunca `WARN_AND_CONTINUE`. Contrato em
   `docs/passaporte/CONTRATO-DO-PASSAPORTE.md` (D-013); portão em
   `python3 scripts/passaporte_portao.py`.
