# BASE V2 E VEREDITO — MISSÃO 09

```
PILOT_INFORMATION_BASE_V1 = FROZEN, HISTÓRICA (1e3f5bb) — não reescrita
PILOT_INFORMATION_BASE_V2 = ABERTA — mudanças materiais confirmadas por reprodução
PILOT_UPDATEABILITY       = PROVED (MISSÃO 08, mantido)
PRODUCT_READINESS         = READY FOR DESIGN
BUSINESS_CASE             = PROMISING BUT UNPROVEN
```

**Data:** 2026-08-29

---

## 1 · POR QUE V2 E NÃO CORREÇÃO DA V1

A v1 é o que sabíamos em 29/08/2026, e continua onde está. **Nenhuma linha dela foi
reescrita.** A v2 existe porque três mudanças **materiais** foram confirmadas por
reprodução — não por relato:

| # | mudança | material porque |
|---|---|---|
| 1 | **CASE-013 muda de escopo e de leitura** | a série tem **23 safras**, não 11; Cádiz 2026 **não** é máximo histórico; a prioridade entre províncias se inverte ao entrar a área |
| 2 | **BQ2 nº 5 fecha em fonte primária** | `ES-00211 NEPTUNE` estava no export que já tínhamos e não havia sido lido |
| 3 | **Expiry radar passa a existir na Espanha** | `StrFechaCaducidad` já estava na amostra arquivada; a documentação dizia que a Espanha não tinha data de vencimento |

As demais correções (contagens, X-006, placar da matriz, resumo de fontes críticas) são
**correções de derivação**, não de fato: o número certo passou a ser calculado pelo dono.

---

## 2 · O RED TEAM, REPRODUZIDO — item a item

| afirmação | veredito | medida nossa |
|---|---|---|
| a amostra ES já tem `StrFechaCaducidad` | **CONFIRMADO** | 2.947 de 3.084; 1.991 dos 1.993 vigentes |
| dá para construir expiry radar na ES | **CONFIRMADO** | 486 em ≤6 meses · 1.004 em ≤12 · ADAMA 36 e 61 |
| existem `Vigente` com caducidade passada | **CONFIRMADO** | **34**, dos quais **3 ADAMA** |
| Neptune está no export primário | **CONFIRMADO** | `ES-00211`, e a ficha oficial dá **Olivo × Venturia oleaginea** |
| B16 mistura 1,19 com 1,17 | **CONFIRMADO** | 1,19 é média geral de 2023 (11 parcelas); a coorte é 1,17 (6 parcelas) |
| Huelva tem base fina | **CONFIRMADO** | 7 parcelas / 18 leituras contra 36 / 141 em Cádiz |
| números documentais desatualizados | **CONFIRMADO** | `25 provas` em 3 docs, `37` em 1; `31 SOURCE_IDs` em 2 |
| matriz declara 8 e mede 9 · 13 e mede 14 | **CONFIRMADO** | a célula escreve `DECK-001, 002, 003`: só o primeiro tem prefixo |
| ES-T4-005 fora do resumo CRITICAL | **CONFIRMADO** | o resumo listava a `EU-T2-001`, que é `USEFUL` |
| X-006 tem arredondamento inconsistente | **CONFIRMADO** | publicado 62,5/77,4; reexecutado dá **62,2/77,8** |
| ~18 capabilities são capabilities, não produtos | **CONFIRMADO** | sobraram **3** money tools; 4 mortas, 4 rebaixadas |
| Ask Sintonia é benchmark executado | **REFUTADO** | **5** perguntas executam; **35** são contrato escrito à mão |

**E dois achados que o red team não trouxe** — os dois maiores desta missão:

1. **A série do RAIF tem 23 safras (2003–2026, 148.964 leituras), não 11.** A MISSÃO 02 leu
   só os três arquivos modernos. Consequência: **Cádiz 2026 = 8,01 não é máximo histórico**
   (9,71 em 2013). Huelva 8,83 é.
2. **Cádiz e Huelva são as duas MENORES províncias de olivar da Andaluzia** — juntas 4,3%
   da área. O hero case priorizava a 4ª e a 5ª colocadas por exposição.

---

## 3 · RED TEAM FINAL — atacando as três MONEY TOOLS

### MT1 · REGULATORY & EXPIRY EXPOSURE

| pergunta | resposta |
|---|---|
| gera decisão? | **sim** — renovar ou deixar cair, e onde olhar o concorrente |
| gera ação? | **sim**, e com data oficial no calendário |
| gera dinheiro sem dado interno? | **indiretamente** — evita perda de janela. Não gera receita mensurável por nós |
| que passo depende da ADAMA? | saber se a renovação já está em curso — o registro não diz |
| é só produtividade? | **em parte, e isso é honesto**: substitui trabalho manual de acompanhar três registros nacionais |
| **objeção do CFO** | *"vocês me dizem que 36 registros meus vencem em 6 meses. Meu regulatório já sabe disso."* **Procede para o portfólio próprio.** O que ele não sabe é o **bloco do concorrente** na mesma cultura × alvo — e é aí que a ferramenta paga |

### MT2 · GEOGRAPHIC COMMERCIAL PRIORITY

| pergunta | resposta |
|---|---|
| gera decisão? | **sim** — onde ativar assistência técnica na próxima safra |
| gera ação? | **sim**, e barata: deslocar atenção, não construir fábrica |
| gera dinheiro sem dado interno? | **não demonstrável.** Pressão não é demanda |
| que passo depende da ADAMA? | se a região já é atendida — o SINTONIA não sabe onde há equipe |
| **objeção do CFO** | *"Sevilla subiu 2,5×. E daí? Quanto vendo lá?"* **Sem resposta nossa.** O que se entrega é **ordem de prioridade entre 7 províncias com denominador declarado** — e a ordem mudou quando o denominador entrou. Isso é decisão, não receita |
| **objeção mais dura** | a antecipação é de **uma safra no melhor caso e zero em dois de três**. Vender isto como *early warning* seria falso |

### MT3 · PUBLIC ACTIVATION GAP

| pergunta | resposta |
|---|---|
| gera decisão? | **não sozinha.** Gera uma pergunta bem posta |
| gera dinheiro? | **não demonstrável, e não deve ser prometido** |
| **objeção do CFO** | *"vocês encontraram que não encontraram nada."* **Procede.** Por isso a saída é `ACTIVATION QUESTION` e não oportunidade. Fica no pacote por ser barata e por ser a única frente que sobrevive sem dado interno **como pergunta** |

---

## 4 · PRODUCT READINESS — **READY FOR DESIGN**

Os sete requisitos da regra, um a um:

| # | requisito | estado |
|---|---|---|
| 1 | quais 2–3 money tools entram | **MT1 · MT2 · MT3** (a terceira só como pergunta) |
| 2 | quais capabilities ficam por baixo | science radar · expert network · climate context · entity intelligence · data clock · change events · normalizações |
| 3 | quais dados reais alimentam | 5 fontes CRITICAL, todas primárias, todas com contrato escrito |
| 4 | quais claims são seguros | 14 safe claims e 20 proibidas, com auditoria de 7 palavras |
| 5 | quais métricas de piloto | LEAD TIME · PRIORITIZATION · FALSE-POSITIVE AVOIDANCE (medidas) · RESEARCH SAVING (não medida) |
| 6 | quais oportunidades são só perguntas | **MT3 inteira**, e as três perguntas do §9 do business case |
| 7 | quais dados internos faltam | **nenhum é pedido.** A premissa fechou a porta e o produto foi redesenhado sem ela |

**Está fechado.** O Design não precisa descobrir produto — precisa desenhar três respostas
cujo conteúdo, limites e evidência já estão escritos.

---

## 5 · BUSINESS CASE — **PROMISING BUT UNPROVEN**

**Não é STRONG**, e a retórica não vai mudar isso:

- a antecipação de campo é de **uma safra**, e falha em dois de três casos;
- `ECONOMIC_VALUE_PROVED` é **inalcançável** sem dado interno — por premissa, não por falha;
- o `RESEARCH SAVING`, que é o KPI mais defensável sem dado da ADAMA, **ainda não foi medido**;
- uma das três ferramentas entrega **pergunta**, não resposta.

**Não é GOOD INTELLIGENCE / WEAK PRODUCT**, e isto mudou nesta missão:

- o produto passou a ter **denominador** — a prioridade entre províncias se inverteu quando
  a área entrou, e isso é exatamente o que um cliente paga para saber;
- o `lead time` regulatório **não é inferido**: 486 vencimentos com data oficial;
- a inteligência **derrubou** duas prioridades que ela própria havia produzido — e um
  sistema que corrige a si mesmo é vendável de um jeito que um painel bonito não é.

---

## 6 · MENOR PRÓXIMO PASSO

Não é missão, não é coleta e não é design.

> **Medir o `RESEARCH SAVING` em um caso.** Cronometrar quanto tempo um analista leva para
> reconstruir manualmente, das fontes públicas, a resposta que a MT1 dá em uma execução —
> os 486 vencimentos espanhóis por titular, cultura e substância.

É o único KPI que fecha **inteiramente sem dado da ADAMA** e o único que produz um número
que um CFO aceita sem confiar em nós. E enquanto isso não existir, o business case
permanece `PROMISING BUT UNPROVEN` — corretamente.
