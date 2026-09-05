# Radar Futuro · o contrato de superfície dos 45 `ITFC-`

```
SURFACE_CONTRACT   = PASS   (30/30 · scripts/it_futuro_contrato_da_superficie.py)
CHECKPOINT         = 0eed31a  ·  congelamento 707b684 / 9560823
COLEÇÃO CANÓNICA   = ITFC-  ·  45
READY_FOR_PORTAL   = decisão do dono, não deste documento
```

⚠️ **Este contrato não julga nenhum sinal.** Ele traduz estados **já congelados**
em comportamento de superfície. Onde o congelamento não decidiu, o campo diz
`DECISAO_EM_ABERTO` e o consumidor reprova — em vez de adivinhar.

---

## 1 · Por que um congelamento não bastava

Os 45 fecharam com estado, veredito, janela, gatilho e limitações. Nada disso diz
o que a tela faz com eles. Um `PARCIAL` tanto pode ser um cartão com aviso como
pode ser invisível, e o congelamento não mandava nem uma coisa nem outra.

    ENQUANTO A REGRA DE SUPERFÍCIE NÃO ESTIVER ESCRITA, CADA CONSUMIDOR
    INVENTA A SUA — E TODOS ACHAM QUE ESTÃO A OBEDECER.

## 2 · As duas populações não se misturam

| coleção | n | estado |
|---|---|---|
| **`ITFC-`** | **45** | **canónica para esta superfície** |
| `ITF-` | 10 | `POPULACAO_DISTINTA_SEM_CONTRATO_ATUAL_PARA_ESTA_SUPERFICIE` |

Os 10 `ITF-` são outra coisa — MELO×ERIOSOMA, PERO×PSILLE, FRUMENTO×INFESTANTI.
Não se apagam, não são falsos, não se redefinem retroativamente. **Não entram na
mesma grelha** até terem contrato próprio.

## 3 · Os três estados de veredito

| estado | renderiza? | contexto | aviso |
|---|---|---|---|
| `SINAL_COMPLETO` | **sim** | cartão inteiro | — |
| `PARCIAL` | **sim** | cartão, **nunca no TOP_3**, nunca como completo | `LETTURA_PARZIALE` |
| `DERRUBADO` | **não** | histórico e auditoria, **fora da reunião** | — |

Cada linha cita o congelamento, não a minha opinião. `PARCIAL` é «o núcleo
aguenta e falta-lhe coisa» — núcleo que aguenta é mostrável, e **o que falta tem
de aparecer com ele**: `DEFEITOS_ENCONTRADOS`, `CORRECOES_OBRIGATORIAS`,
`C_NAO_SABEMOS`. `DERRUBADO` é «isto não se apresenta».

## 4 · Os estados temporais

```
existem     PREPARAR (23 na superfície)   MONITORAR (21)
AGIR_AGORA  0 — valor MEDIDO, não arredondado
```

As fontes são de Out/2025 a Mai/2026 e a leitura é de Set/2026. Um cartão que
diga «aja agora» sobre este material **mente sobre o calendário**.

- `PREPARAR` nunca pode parecer `AGIR_AGORA` — nada que implique aplicação,
  tratamento ou decisão de campo para hoje.
- `MONITORAR` nunca pode parecer recomendação de intervenção — é vigilância
  sobre um gatilho nomeado.

*(23 e não 24 porque `ITFC-027` é `PREPARAR` e é o `DERRUBADO`: sai da superfície.
23 + 21 = 44 = 45 − 1.)*

## 5 · O que cada cartão preserva

Evidência (`F_CITACAO_VERBATIM` + `F_CITACAO_CONFERIDA`) · fonte · data · região ·
cultura/alvo · janela (`T_JANELA_DE_APLICACAO` + `T_BASE_DA_JANELA`) · `TRIGGER` ·
`INVALIDATION_TRIGGER` · estado · limitações · **o que ainda não sabemos**.

Ausência de **valor** é permitida e aparece como `NÃO SEI` com motivo. Ausência
de **campo** não é: reprova.

## 6 · Dependência de portfólio quebrada

    DEPENDÊNCIA QUEBRADA APARECE COMO LIMITAÇÃO, NUNCA COMO ZERO INVENTADO.

A rota viva «temos algo para X?» tem defeito conhecido e **não pode ser
consultada** para fabricar resposta. A classe sai de uma regra mecânica —
`ADAMA_PAIR_EXISTS` cruzado com um regex sobre alvo e cultura — e não de
atribuição à mão:

| classe | n | o cartão pode |
|---|---|---|
| `MEDIDO_EXISTE` | 20 | citar o portfólio medido |
| `MEDIDO_ZERO` | 16 | citar o zero, **com numerador e denominador** |
| `DECLARADO_UNKNOWN` | 3 | mostrar UNKNOWN e o bloqueador; **não usar o par** |
| `EVIDENCIA_CONGELADA` | 2 | usar **só** evidência congelada; consulta viva proibida |
| `CEGO_SEM_CLASSE` | 3 | dizer que o NÃO é **cego**, não ausência real |

**8 dos 44 na superfície** carregam limitação declarada: `ITFC-007`, `ITFC-009`,
`ITFC-010`, `ITFC-011`, `ITFC-016`, `ITFC-021`, `ITFC-023`, `ITFC-028`. O defeito
de vocabulário fica **congelado e por corrigir**, com dono canónico por
identificar — duas camadas, dois donos, e responder nas duas cria o segundo dono
que se evitou a semana inteira.

## 7 · O consumidor burro

`scripts/it_futuro_contrato_da_superficie.py` não sabe agronomia, não releu
nenhum sinal e não tem opinião sobre nenhum dos 45. Abre o contrato, obedece
literalmente, conta nos artefactos congelados. Se precisar de **uma** decisão que
o contrato não declarou: `CONTRACT = FAIL`, e o defeito é do contrato.

Os números esperados **não saem do contrato** — são o critério aprovado e estão
no script. Se saíssem de lá, provariam apenas que o contrato concorda consigo
mesmo.

**Ele reprova de verdade.** Três controlos negativos, medidos:

```
PARCIAL sem RENDERIZAVEL      → FAIL  «ausente é adivinhação»
DERRUBADO posto na grelha     → FAIL  «o congelamento diz isto não se apresenta»
uma DECISAO_EM_ABERTO         → FAIL
```

O segundo desses controlos apanhou um defeito meu: a primeira versão **relatava**
`DROPPED_RENDERABLE` e não o **impunha** — bastava editar o contrato para pôr o
derrubado na reunião e o portão dizia `PASS`.

    UM PORTÃO QUE CONTA O QUE NÃO IMPEDE NÃO É PORTÃO.

## 8 · O que este contrato não faz

Não reabre os 45, não promove estado, não recalcula o `TOP_3` (é lista
congelada: `ITFC-009`, `ITFC-016`, `ITFC-018`), não corrige o vocabulário, não
integra nada no portal e não declara `READY_FOR_PORTAL`. Essa decisão é do dono.
