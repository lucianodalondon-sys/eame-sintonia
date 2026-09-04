# Piloto dos cinco vãos — e a contagem da suíte que não fechava

```
FIVE_GAP_PILOT = PASS
HEAD inicial   209335e · BUILD_ID V21-ea0d941dc39f6b49
HEAD final     este    · BUILD_ID V21-7285e903bfb1c147
```

Cinco perguntas escritas antes da coleta. **Cinco respostas** — duas mudaram o
resultado, três disseram «não», e um «não» também é resposta.

    UMA COLETA QUE VOLTA COM «NÃO» RESPONDEU À PERGUNTA.
    QUEM NÃO REGISTRA O «NÃO» PERGUNTA DE NOVO NO MÊS SEGUINTE.

---

## Passo zero · a equação da suíte

Os números não fechavam porque são **dois universos**, e ninguém tinha dito qual
era qual. `python3 scripts/v21_contagem_da_suite.py` imprime a equação e falha se
ela não fechar.

```
UNIVERSO 1 · DESCOBERTOS            745
   menos NUNCA EXECUTADOS            -5   ← classe abortada no setUpClass
UNIVERSO 2 · EXECUTADOS (testsRun)  740

   PASSOU                           718
   FALHOU                             7
   ERRO (o caso rodou e deu erro)      1
   PULADOS                            14
   XFAIL / XPASS                    0 / 0
   ────────────────────────────────────
   soma                              740   ✓
```

**Os «2 erros» são duas coisas diferentes**, e é daí que vinha a confusão:

| entrada | é um caso? | conta em `testsRun`? |
|---|---|---|
| `_FailedTest` · `test_comunicacao` — módulo que não importa | **sim** | sim |
| `_ErrorHolder` · `setUpClass` de `TestContraOArtefatoReal` | **não** | **não** |

`TestContraOArtefatoReal` tem **5** métodos. O `setUpClass` levanta (o branch
`origin/claude/adama-es-local-browser` não existe neste clone raso), o unittest
registra **um** `_ErrorHolder` e **nenhum** dos 5 roda. Daí `745 − 5 = 740`.

    UM NÚMERO SEM DENOMINADOR NÃO É UMA MEDIDA: É UM ADJETIVO.

Nenhum teste foi corrigido para fechar número.

---

## Os cinco escolhidos — do vão medido, não da facilidade da fonte

Quatro do **tipo B** (regra declarada, estado desconhecido) e um do **tipo A**
(regra ausente). Os dois problemas não foram misturados.

| # | tipo | caso | `SALES_READY` | fato exato que faltava |
|---|---|---|---|---|
| 1 | B | traça-da-uva × videira · Emilia-Romagna | sim | % corrente de cachos infestados, contra a soglia de 5% |
| 2 | B | carpocapsa × macieira · Veneto | sim | fase corrente do voo de *Cydia pomonella* |
| 3 | B | piralide × milho · Friuli | sim | posturas por 100 plantas, contra o limiar de 3 |
| 4 | B | botrite × videira · Toscana | sim | se a vinha está na fase de maior suscetibilidade |
| 5 | **A** | traça-da-uva × videira · Umbria | não | **qual condição** define o momento nesta região |

---

## Pergunta, fonte e resposta — um por um

### 1 · traça-da-uva × videira · Emilia-Romagna

**PERGUNTA** — «A percentagem de cachos infestados por tignoletta está acima de
5% agora na Emilia-Romagna?»

**FONTE** — Consorzio Fitosanitario Provinciale di Reggio Emilia, *Diario di
terza generazione*, **atualizado em 3 de setembro de 2026**.

> «Soglie per i trattamenti in terza generazione: **5% di grappoli con uova e/o
> fori** per tutte le aziende» · «il quadro a livello territoriale sembra essere
> tuttora **tendenzialmente buono**, nella generalità dei casi, con le dovute
> eccezioni» · SMS n.55 del 28/08/2026: «la III gen. sta terminando».

**RESPOSTA: sim — e é um NÃO.** `EVIDENCE_ROLE = WEAKENS`.
`WINDOW_OPEN_NOW` continua `UNKNOWN`: a fonte descreve o quadro territorial, não
mede a parcela, e o motor recusa transformar «tendencialmente buono» em
percentagem. **STATUS: `VALIDATE_NOW` → `VALIDATE_NOW`.**

### 2 · carpocapsa × macieira · Veneto

**PERGUNTA** — «A fase do voo de *Cydia pomonella* justifica intervenção agora?»

**FONTE** — Regione del Veneto, Bollettino COLTURE FRUTTICOLE **n. 25 del
03/09/2026**.

> «Cydia pomonella: **terzo volo terminato**. Si segnala la presenza di **danni
> in aumento** anche nei frutteti a gestione integrata… **continuare la difesa**
> con prodotti ad azione larvicida» · «Fase fenologica: **prossima la raccolta
> della Golden**»

**RESPOSTA: sim.** O voo que a condição nomeia **terminou**, e o boletim não
declara a fase do seguinte. A ordem de continuar a defesa entra como **direção**,
não como janela aberta. **STATUS: `VALIDATE_NOW` → `VALIDATE_NOW`.**

### 3 · piralide × milho · Friuli-Venezia Giulia

**PERGUNTA** — «As posturas estão acima de 3 por 100 plantas agora?»

**FONTE** — índice ERSA FVG, verificado em 03/09/2026. O último boletim de milho
é o **n.15 de 12/08/2026**; o **n.16, de 03/09/2026, é de cereais de
outono-inverno**.

**RESPOSTA: sim — a série do milho fechou para a temporada.** Nenhum registro
novo foi criado: inventar um seria o único jeito de mudar o estado.
**STATUS: `VALIDATE_NOW` → `VALIDATE_NOW`.**

### 4 · botrite × videira · Toscana ⟵ **mudou**

**PERGUNTA** — «A vinha está na fase de maior suscetibilidade à botrite agora?»

**FONTE** — Regione Toscana, Servizio Fitosanitario, *Bollettino Vite Integrato*,
provincia di Siena, **03/09/2026** (lido pela API pública do agroambiente).

> **«Siamo nella fase di maggior suscettibilità a questa malattia.** In
> previsione di piogge, innalzamento dell'umidità e in caso di grappoli
> danneggiati, è possibile intervenire con prodotti antibotritici microbiologici,
> bicarbonato di potassio o terpeni…» · «Fenologia: la fase fenologica prevalente
> è "maturazione"».

**RESPOSTA: sim, e no presente.** A fonte declara ela mesma que a condição está
satisfeita — não houve dedução nossa.

```
WINDOW_DEFINED   YES → YES
WINDOW_OPEN_NOW  UNKNOWN → YES   (FONTE_DECLARA_A_CONDICAO_COMO_PRESENTE)
STATUS           VALIDATE_NOW → ACT_NOW
```

    QUANDO A FONTE ESCREVE «ESTAMOS NA FASE», LER ISSO NÃO É INFERIR.
    INFERÊNCIA SERIA CONCLUIR SEM ELA TER ESCRITO.

### 5 · traça-da-uva × videira · Umbria ⟵ **mudou**

**PERGUNTA** — «Qual condição técnica determina o momento de intervenção contra
tignoletta em videira na Umbria?»

**FONTE** — Regione Umbria, Servizio Fitosanitario Regionale, *Bollettino
Fitosanitario della VITE* **n. 21 del 28/08/2026**, válido para Perugia e Terni.

> «Tignoletta della vite (Lobesia botrana) **soglia di intervento: 10-15% di
> grappoli con uova e/o larve**.» · «FOCUS SETTIMANALE: **In generale non sono
> necessari interventi.** Fase calante dei voli.»

**RESPOSTA: sim — e a regra é OUTRA.** A Umbria declara **10–15%**; a
Emilia-Romagna, **5%**. Copiar a regra de uma região para a outra teria sido um
erro de fato — e é por isso que a chave da janela carrega a região.

    A REGRA É REGIONAL PORQUE O SERVIÇO É REGIONAL.

```
WINDOW_DEFINED   NO → YES  (THRESHOLD_WINDOW, 10-15%)
NEED_DIRECTION   NEUTRAL_MENTION → NO_ACTION_RECOMMENDED
STATUS           WATCH → WATCH
```

O estado continua `WATCH` porque a fonte diz que não são necessários
intervenções. **Isso é a resposta certa, não uma falha da coleta.**

---

## Quantos responderam · e o que mudou

| | |
|---|---|
| perguntas feitas | **5** |
| perguntas respondidas pela fonte | **5** |
| registros novos criados | **4** (o item 3 não gerou registro: não há o que colher) |
| casos que mudaram de estado | **1** (Toscana) |
| casos que ganharam regra de janela | **1** (Umbria) |
| casos que ganharam evidência sem mudar de estado | **2** (Emilia-Romagna, Veneto) |

### Backfill completo — todo o acervo reprocessado

| | 209335e | agora |
|---|---|---|
| CASOS | 43 | **43** |
| `ACT_NOW` | 1 | **2** |
| `VALIDATE_NOW` | 4 | **3** |
| `WATCH` | 22 | 22 |
| `FUTURE_PREPARATION` | 7 | 7 |
| `TO_VALIDATE` | 9 | 9 |
| `SALES_READY` | 5 | **5** |
| `EXTERNAL_MATERIAL_READY = YES` | 5 | **5** |
| `WINDOW_DEFINED = YES` | 6 | **7** |
| `WINDOW_OPEN_NOW = YES` | 1 | **2** |

`BACKFILL_PREVIEW`: **41 SEM_MUDANÇA · 1 PROMOÇÃO · 1 CORREÇÃO · 0
REBAIXAMENTO**. Nenhum efeito colateral: a coleta dirigida tocou exatamente os
casos que ela perguntou.

---

## Oportunidades NÃO alteradas, e por quê

- **41 casos** não têm relação com nenhuma das cinco perguntas — nenhuma
  evidência nova os alcança.
- **Emilia-Romagna (traça)** e **Veneto (carpocapsa)** ganharam apoio novo e
  continuam `VALIDATE_NOW`: a fonte respondeu, e a resposta não abre a janela.
- **Friuli (piralide)** não tem fonte nova publicada.
- `SALES_READY` continua **5**: nenhuma das coletas mexeu na régua comercial.

---

## O que foi preciso mudar no motor — e o que não

**Uma regra nova, medida antes de existir:** `FONTE_DECLARA_A_CONDICAO_COMO_PRESENTE`.
Quando a oração traz «siamo nella fase», «se está na fase», «é o momento de», a
condição está declarada como satisfeita **pela fonte**. É leitura, não dedução, e
está pinada em `T41`/`T41b`.

**E uma correção na porta:** a ingestão de last-mile não carregava
`PHENOLOGICAL_STAGE_DECLARED`. O boletim novo entrava sem o estádio que ele
próprio publica.

    O QUE A FONTE DECLARA E A PORTA NÃO CARREGA NÃO EXISTE LÁ DENTRO.

**Thresholds: nenhum.** `v21_comercial.py` não foi tocado.

---

## Passo 8 · QA do ISTAT — sem coletar nada

| pergunta | resposta |
|---|---|
| **qual dado já existe?** | **2.945 linhas** do ISTAT (`IT1:101_1015(1.0)`), 2024–2026, 21 geografias, três indicadores: `AREA` 983 · `PRODUCTION` 981 · `YIELD` 981 |
| **por que não é utilizável?** | todas entraram como `QA_UNREVIEWED`, e `CLIENT_SAFE` deriva de `QA_STATUS`. **Não é falta de dado: é falta de carimbo.** |
| **qual teste falta?** | os três que agora existem — `T45` (nenhuma chave duplicada), `T45b` (o rendimento bate com produção ÷ área), `T45c` (unidade constante por indicador) |
| **qual correção seria necessária?** | promover a `QA_PASS` as linhas que passam nos três testes. Medido: **0 chaves duplicadas · 981 de 983 triplas coerentes dentro de 2% · unidade única por indicador**. **NÃO aplicado nesta rodada** — é decisão de QA, não de coleta. |

---

## Custo do piloto

| | |
|---|---|
| perguntas | 5 |
| fontes consultadas | 6 sítios oficiais regionais (ER/Reggio Emilia, Veneto, ERSA FVG, Toscana, Umbria, ER/Modena) |
| documentos baixados | 4 PDF + 1 API JSON |
| custo monetário | **0,00** — todas as fontes são públicas e abertas |
| registros criados | 4 sinais de campo + 8 pares de tradução |
| execuções da cadeia | 5 (incluindo duas de diagnóstico e uma no worktree do commit anterior) |

---

## Próximos vãos recomendados — de novo cinco, dirigidos

1. **piralide × milho · Friuli** — a série fechou; a pergunta migra para
   *«quando a ERSA reabre o monitoramento do milho?»* — coleta de calendário de
   publicação, não de boletim.
2. **carpocapsa × macieira · Veneto** — a fase do **quarto** voo, no boletim da
   próxima semana.
3. **traça-da-uva × videira · Emilia-Romagna** — o diário da **quarta** geração
   de Reggio Emilia, quando publicado.
4. **QA do ISTAT** — rodar os três testes e promover o que passar (libera
   `AREA_OFICIAL` nos 43 cartões).
5. **os 12 `WINDOW_RULE_MISSING`** — começar pelos dois de videira × peronospora
   em regiões que já têm portfólio, procurando o *disciplinare di produzione
   integrata* regional, que é onde a regra costuma estar escrita.

---

## Confirmação

```
PORTAL         = NÃO TOCADO
DESIGN         = NÃO TOCADO
VERCEL         = NÃO TOCADO
PRODUÇÃO       = NÃO TOCADA
THRESHOLDS     = NÃO ALTERADOS
NOVA COLETA AMPLA = NÃO — cinco perguntas, quatro registros
```

Suíte: **745 descobertos · 740 executados · 718 passaram · 6 falhas · 2 erros ·
14 pulados** — as mesmas 8 ocorrências anteriores a esta linha de missões.
Provas da camada: **82/82**. Cadeia `EXIT=0`, 0 violações de contrato, 0 campos
só em português.
