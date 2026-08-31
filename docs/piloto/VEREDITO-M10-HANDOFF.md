# VEREDITO DA MISSÃO 10 — prova de utilidade e handoff V2

```
PRODUCT_READINESS = READY FOR DESIGN
BUSINESS_CASE     = PROMISING BUT UNPROVEN → sustentado, com uma prova a mais e uma a menos
RESEARCH_SAVING   = PARCIALMENTE PROVADO (passos), NÃO PROVADO (tempo)
TESTES_REAIS = <!--M:TEST_COUNT_CURRENT-->1.007<!--/M-->
```

**Data:** 2026-08-29

---

## 1 · O QUE ESTA MISSÃO REALMENTE PROVOU

| KPI | estado |
|---|---|
| **PRIORITIZATION** | **PROVADO.** Duas fontes públicas trocam a 1ª e a 2ª colocadas, e revelam a única província robusta às duas réguas |
| **FALSE-SIGNAL AVOIDANCE** | **PROVADO.** A prioridade que o próprio repositório sustentava por três missões caiu quando o denominador entrou |
| **RESEARCH SAVING** | **PARCIAL.** 7 toques → 1, 3 julgamentos → 0, 3 oportunidades de erro → 0 · **mas 7/8 campos → 4/8** |
| **LEAD TIME** | **FORTE no regulatório** (data publicada, 6–12 meses) · **MODESTO no campo** (1 safra, e zero em dois de três) |
| **EXTERNAL OPPORTUNITY DISCOVERY** | **PROVADO.** *"Onde a pressão importa"* não existia em nenhuma das duas fontes sozinha |

**E o que ela deixou de provar, de propósito:** o **tempo**. O analista da rota manual fui
eu, e eu escrevo o filtro certo de primeira. Estimar quanto um humano levaria seria inventar
número. `ELAPSED_SECONDS = INVALID`, escrito no próprio protocolo.

---

## 2 · RED TEAM FINAL — as três perguntas que derrubariam cada ferramenta

### MT1 · *"Por que o Regulatory da ADAMA não faria isso sozinho?"*

**Faria — para o portfólio dele.** É a objeção mais forte da missão e ela **procede** na
metade própria: 36 vencimentos ADAMA em ≤6 meses é coisa que um regulatório competente já
acompanha.

**O que ele não vê sozinho é a outra coluna.** `Syngenta 37` na mesma janela, e o
bloco por titular × cultura × substância nos três países. Isso não está no sistema interno
de ninguém — está espalhado por três registros nacionais com rotas diferentes.

**Veredito: MANTIDA**, com a promessa corrigida: *exposição do concorrente*, não *calendário
do próprio portfólio*.

### MT2 · *"Por que `ha × incidência` não é um índice arbitrário?"*

**Em parte é** — e a resposta honesta tem três partes:

1. **É arbitrário como escolha de fórmula.** Poderia ser `ha × Δincidência`, ou ponderado
   por valor da cultura. **Nada prova que multiplicar é a operação certa.**
2. **Não é arbitrário como direção.** Qualquer denominador de escala move Huelva e Cádiz
   para baixo, porque elas são **as duas menores** — 4,3% da área. A conclusão sobrevive à
   troca de fórmula.
3. **O teste que importa não é o índice, é a robustez.** Sevilla aparece no top-3 das
   **duas** réguas — nível e exposição. É essa concordância, não o número, que sustenta a
   prioridade.

**Veredito: MANTIDA**, com o índice rebaixado a **critério de ordenação declarado**, nunca
a métrica de negócio. E a régua correta seria **área tratada**, que não é pública.

### MT3 · *"Por que ausência pública não é ausência comercial?"*

**Não é, e nós não temos como saber a diferença.** Um produto pode vender por canal técnico
sem uma linha publicada. Três dos cinco majors devolveram 403 — o que mede o nosso acesso,
não o comportamento deles.

**Veredito: MANTIDA APENAS COMO PERGUNTA.** Se em algum momento aparecer como *oportunidade*
num documento ou numa tela, está errado.

---

## 3 · A PROMESSA ORIGINAL, RECONCILIADA

O deck prometia **LOCAL SIGNALS · CONNECTED CONTEXT · BETTER TIMING**.

| promessa | veredito medido |
|---|---|
| **LOCAL SIGNALS** | **SIM** — parcela, semana, província; 23 safras |
| **CONNECTED CONTEXT** | **SIM, e é a parte mais forte** — foi a conexão que mudou a decisão (CASE-016) |
| **BETTER TIMING** | **FORTE no regulatório · MODESTO e NÃO GERAL no campo** |

> **`BETTER TIMING` não pode virar `PREDICTIVE EARLY WARNING`.** O backtest mediu: uma
> safra no melhor caso, zero em dois de três, 14 disparos dos quais 11 sem evento depois.

---

## 4 · PRODUCT READINESS — **READY FOR DESIGN**, mantido

Os sete requisitos continuam fechados, e dois ficaram mais fortes: a arquitetura tem
**porta única** (`ARQUITETURA-DE-PRODUTO-ATUAL.md`, com teste que exige os três documentos
antigos apontando para ela) e a **home** tem cinco classes de item com exemplo real, sem
KPI decorativo.

## 5 · BUSINESS CASE — **PROMISING BUT UNPROVEN**, sustentado

Não subiu para `STRONG`, e a razão é a mesma de antes mais uma nova:

- `ECONOMIC_VALUE_PROVED` continua **inalcançável por premissa**;
- o `RESEARCH SAVING` ficou **parcialmente** provado — e a parte que faltou é a que o
  produto **ainda não faz** (4 dos 8 campos);
- o tempo, que seria o argumento mais vendável, **foi descartado por honestidade**.

Não caiu para `GOOD INTELLIGENCE / WEAK PRODUCT` porque **PRIORITIZATION** e
**FALSE-SIGNAL AVOIDANCE** passaram de hipótese a medida, e as duas são exatamente o que se
paga numa inteligência externa.

---

## 6 · MENOR PRÓXIMO PASSO

Não é missão, não é coleta, não é design.

> **Fechar os quatro campos que o benchmark localizou:** `BY_HOLDER`, `TOP_HOLDERS` e
> `BY_SUBSTANCE` saem do snapshot que já está em disco. Só `CROP_COVERAGE` custa coleta
> (972 requisições, ~15 min, medidas).

Com os quatro, a MT1 passa de **4/8 para 8/8** e o `RESEARCH SAVING` deixa de ser parcial —
sem uma fonte nova, sem um país novo e sem um dado da ADAMA.
