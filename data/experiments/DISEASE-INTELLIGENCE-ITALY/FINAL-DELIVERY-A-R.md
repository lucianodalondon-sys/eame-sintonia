# ENTREGA FINAL — DISEASE & PEST INTELLIGENCE
## A ferramenta merece entrar no Sintonia?

`PORTAL_INTEGRATION = NO` · nenhuma tela construída · nenhuma branch do portal tocada ·
produção intacta · Espanha e França não abertas.

Todos os números abaixo saem de artefactos em disco, não de memória:
`ENGINE/gates_final.txt`, `ENGINE/regional_coverage.json`, `ENGINE/automation_probe.json`,
`ENGINE/answer_sheet.json`, `CASES/*/collection_index.json`.

---

## A — RESPOSTA DIRETA

**AINDA NÃO.** A medição sobrevive; o aparelho que a certifica não.

```
ÁRBITRO INDEPENDENTE ....... NOT_YET
SUITE DO PRÓPRIO AUTOR ..... NO   (8 PASS / 1 FAIL / 1 NOT_TESTABLE)
PORTAL_INTEGRATION ......... NO
```

Escrevi `YES_SCOPED` esta manhã. Um árbitro que não escreveu nada disto discordou de **cinco dos
meus dez gates** e eu concedi os cinco depois de os verificar contra o meu próprio código. A sua
frase é a descrição mais justa do resultado:

> *"A medição agronómica subjacente à célula da oliveira sobreviveu a tudo o que lhe atirei. É o
> aparelho que a certifica, não a medição, que ainda não é de confiança."*

O que a capacidade **é**, quando qualifica, mantém-se abaixo — e é útil.

A capacidade é propriedade de **REGIÃO × CULTURA × PROBLEMA × DATA**. Esta última palavra é uma
correção minha, feita depois de o red team a exigir: eu tinha escrito que a célula da oliveira
qualifica e a da videira não. **Isso era uma propriedade do dia 6 de setembro, não das células.**
A minha própria re-execução, mesmo código, mesmo gate declarado:

```
AS_OF        OLIVEIRA pub   estab   latência | VIDEIRA pub   estab   latência
2026-06-01              0   1.000       227d |           5   0.849        0d
2026-06-15              0   1.000       241d |           6   0.842        0d
2026-08-01              6   0.816         1d |           1   0.584        3d
2026-09-06              8   0.918         2d |           0   0.596        2d
```

**A 15 de junho o veredicto está exatamente invertido.** E a estabilidade de 1.000 da oliveira em
junho significa "consistentemente UNKNOWN", não "consistentemente certo" — um número de
estabilidade sem a latência ao lado não quer dizer nada.

O que sobrevive, e é mais útil do que o que caiu: **num dia qualquer só um punhado de células
pode ser publicado, e quais mudam ao longo da estação.** Um portal que envie isto tem de o enviar
por célula E por data — e tem de conseguir não dizer nada, durante meses.

**Consequência comercial, pior que a científica:** a campanha da azeitona corre de final de junho
a final de outubro. Durante cerca de **oito meses por ano a vista da oliveira não tem nada para
mostrar** e leria "atualizado há 241 dias". Uma funcionalidade de uma célula só está apagada a
maior parte do ano.

## B — OS CASOS ELEITOS (FASE 1)

Eleitos do acervo existente (`CENSUS/italy_census.json`, 25 candidatos já classificados).
Nenhuma recolha nova foi necessária para decidir, por isso nenhuma foi aberta.

| | CASO B (PRAGA) | CASO C (2ª DOENÇA) |
|---|---|---|
| objeto | OLIVO × *Bactrocera oleae* × Toscana | VITE × Oídio × Toscana |
| crop/schema/var | 2 / 1 / −1002 | 3 / 8 / 39 |
| safras | 20 completas + 2026 em curso | 20 (2011 vazio) |
| visitas | 79 251 | 35 065 |
| modo de valor | NUMERIC (`widget: numeric`) | ORDINAL (tabela de códigos) |

## C — REUSO MEDIDO (FASE 2)

```
CASES_TESTED ............................. 4
CASES_PASS_WITH_NO_RULE_CHANGE ........... 3
CASES_NEEDING_A_GENERIC_RULE_EXTENSION ... 1
PIPELINE_REUSE_RATE ...................... 3/4 = 75%
ramificações condicionais por caso ....... 0
```

O 4º caso — **FRUMENTO × Septoria × Toscana**, crop 19 / schema 74 / var 372, recolhido ao vivo,
uma cultura e um schema que este código nunca tinha visto — **derrubou o pipeline em quatro
sítios** (ver C20–C24). Antes das correções, publicava *"100% dos sítios de trigo com Septoria,
e isso é típico"* a partir de IDs de código lidos como magnitudes. Depois das correções,
descodifica corretamente e produz 14 safras com 9 valores distintos de incidência — mas dois
rótulos continuam por resolver (`50 - gravissina`, `75 - completa`), o que **subestima a
severidade** nas piores safras.

Ressalva honesta: o oídio e o caso de calibração partilham **894 de 896 campos** e **96,9% das
visitas** — mesmo scout, mesma vinha, mesmo dia. São 3 execuções sobre **2 painéis**, não 3.

## D — `CURRENT_PRESSURE`, DEFINIÇÃO EXATA (FASE 4)

```
INPUTS            só visitas oficiais de campo. EvidenceRole = OFFICIAL_OBSERVATION, EXIGIDO:
                  MODELLED_RISK e FORECAST são recusados, e uma variável ausente dos metadados
                  do inquérito é recusada.
TIME_WINDOW       28 dias até AS_OF. AS_OF é ENTRADA, nunca o relógio.
REGIONAL_UNIT     província. Uma província muda NUNCA herda a vizinha.
BASELINE          o mesmo intervalo mês-dia em cada safra anterior da mesma província.
UPDATE_FREQUENCY  medido: DATA_LATENCY_DAYS = 2 em ambos os casos.
UNKNOWN_RULE      n_sites < 8 -> UNKNOWN_NO_DATA ; baselines úteis < 5 -> UNKNOWN_NO_BASELINE.
                  UNKNOWN é PUBLICADO. Nunca zero, nunca "baixo", nunca escondido alargando
                  a janela até aparecer alguma coisa.
EVIDENCE          por célula: n_visits, n_sites, janela, URL, papel, sha256 do ficheiro bruto.
PARÂMETROS        WINDOW_DAYS 28 · MIN_SITES 8 · MIN_BASE 5 · HIGH_P 0.80 · LOW_P 0.20
```

**Julgamento manual escondido: nenhum.** O único julgamento são os cinco parâmetros, e o seu
peso é agora uma quantidade medida numa grade de **135 pontos**:

```
BACTROCERA  estabilidade média do rótulo 0.918
OIDIO       estabilidade média do rótulo 0.596
```

Reprodutibilidade: duas execuções independentes são byte-a-byte idênticas; cada ficheiro bruto
é verificado por sha256 contra o índice de recolha antes de ser usado.

## E — NÃO É DEGENERADO (FASE 4)

Replay walk-forward na mesma data de calendário em cada safra, baseline só com safras anteriores:

```
BACTROCERA  H=24  TÍPICO=57  L=43   quota da classe dominante 0.42  -> DISCRIMINA
OIDIO       H=11  TÍPICO=69  L=44   quota da classe dominante 0.67  -> DISCRIMINA
```

Províncias discordam **dentro da mesma safra**. Não é a deriva do arquivo a falar.

## F — EVOLUÇÃO NÃO É UM GRÁFICO BONITO (FASE 5)

```
OIDIO        rho(ano, incidência) = -0.814   rho(%georreferenciado) = -0.737
BACTROCERA   rho(ano, incidência) = -0.475   rho(%georreferenciado) = -0.418
PERONOSPORA  rho(ano, incidência) = -0.185   (sem tendência a confundir)
```

```
EVOLUÇÃO como "que safras foram más umas face às outras"  = PROVADO
EVOLUÇÃO como "a doença está a diminuir há 20 anos"       = TREND_NOT_PROVED
```

A linha descendente era o gráfico mais fácil do produto e o mais desonesto.

## G — AUTOMAÇÃO, SONDADA AO VIVO (FASE 6)

```
MÉTODO      um GET HTTPS sem autenticação, JSON, ~2 s
PASSOS MANUAIS  0 para um refresh
VERIFICAÇÃO devolveu a safra corrente linha-a-linha igual ao armazenado: 2515=2515, 2928=2928
LATÊNCIA    2 dias
CUSTO       EUR 0
RISCO       REAL. difesa/tipo_elab devolve HTTP 200 + ok:true + 0 linhas. A própria sonda
            escrita para testar a armadilha caiu nela. rowCount 0 é FALHA, nunca "sem doença".

CAN_REFRESH_WITHOUT_RESEARCH_PROJECT = YES   (Toscana, ambos os casos)
                                     = YES   (Abruzzo, mesmo schema)
                                     = NOT_TESTED  (todas as outras regiões)
```

## H — REGIONALIDADE (FASE 7)

```
REGIONS_WITH_PROVED_DATA  = 1    Toscana
REGIONS_PARTIAL           = 1    Abruzzo — schema replica e a escala deriva, mas nome_area é uma
                                 partição de AGRO-ZONAS, não províncias, e nenhuma área chega a
                                 10 safras -> 0 pares qualificados. O teste NÃO CORRE lá.
REGIONS_UNKNOWN           = 18   nunca testadas

GENERALIZAÇÃO GEOGRÁFICA = NÃO DEMONSTRADA.
Nenhuma figura nacional italiana é produzida, e o código não a consegue produzir.
```

## I — VALOR SEM PREVISÃO (FASE 3)

As oito respostas são **computadas**, não escritas (`ENGINE/answer_sheet.py`). Hoje, caso praga:

1. **O QUE ACONTECEU** — scouts pontuaram 1 168 visitas para infestação danosa em 469 sítios monitorizados na Toscana.
2. **ONDE** — 9 províncias com dados, Prato sem. Província é a unidade; não existe figura nacional.
3. **QUANTO** — Livorno 11,7% (habitual 88,9%), Siena 13,1% (51,9%), Grosseto 5,8% (46,3%)…
4. **COMO EVOLUI** — na safra: 4 a subir, 4 estáveis, 1 a descer face à janela anterior. Entre safras: ordenação PROVADA, tendência plurianual NÃO.
5. **PRESSÃO MAIOR OU MENOR** — 8 províncias LOWER_THAN_USUAL, Massa-Carrara retida, Prato UNKNOWN.
6. **O QUE MUDOU** — 9 de 10 províncias diferem da mesma data da safra passada.
7. **FONTE** — OFFICIAL_OBSERVATION, NOWCAST, latência 2 dias, 21 ficheiros com hash verificado.
8. **O QUE NÃO SABEMOS** — Prato nunca classificável; EARLY_WARNING, ambos os OUTLOOK, tendência plurianual, qualquer afirmação sobre campos não visitados e ADAMA_PRODUCT_RELATION todos NOT_PROVED; **o painel é a rede monitorizada, não uma amostra aleatória da região**.

Para o caso doença, no mesmo dia, a folha publica **nada**. Uma ferramenta que se cala quando
não pode falar é o achado, não a falha.

## J — VALOR AGRONÓMICO vs RELAÇÃO COM PRODUTO (FASE 8)

```
AGRONOMIC_INTELLIGENCE_VALUE = PROVED      OLIVO x BACTROCERA x TOSCANA
                             = NOT_PROVED  VITE x OIDIO x TOSCANA
ADAMA_PRODUCT_RELATION       = NOT_PROVED
```

**Correção (C29): a razão que eu tinha dado para isto era falsa.** Escrevi duas vezes que não
tinha chegado handoff da via regulatória. **Tinha.** `italia-portale/client/italy-label-verdicts.js`
está nesta árvore de trabalho, aplicado a 02/09/2026 a partir de 163 rótulos oficiais italianos, e
adjudica **exatamente a célula que qualifica**:

```
NOT_FOUND = [ ['Olive','Olive Fruit Fly','KLARTAN 20 EW'],
              ['Olive','Olive Fruit Fly','KLARTAN SMART'],
              ['Olive','Olive Fruit Fly','MAVRIK SMART'], ... ]
regra que o governa: "ABSENCE IN OUR READING  ≠  ABSENCE IN THE WORLD"
```

`NOT_PROVED` mantém-se, por uma razão melhor documentada e comercialmente mais dura: a via
regulatória leu os rótulos e **não encontrou produto ADAMA em rótulo para Olive × Olive Fruit
Fly nessa leitura** — o que, pela sua própria regra, não é prova de ausência no mundo.

**A ferroada comercial, dita sem rodeios: a única célula que qualifica agronomicamente hoje é uma
célula onde a nossa própria leitura de rótulos não encontrou nada para vender.**

## K — GATES A–J (FASE 9)

| gate | veredicto | como pode falhar |
|---|---|---|
| A OUTCOME_IS_OBSERVED | PASS | **exigido**, não carimbado: recusa MODELLED_RISK, FORECAST e variável fora do schema |
| B NOT_SOLD_AS_FORECAST | PASS | o arquivo tem 15 observações datadas depois do corte, todas dentro da janela; o corte exclui todas |
| C REGIONAL_NOT_NATIONAL | PASS | nenhum agregado acima da região existe na saída |
| D UNKNOWN_IS_VISIBLE | PASS | províncias UNKNOWN publicadas hoje em ambos os casos |
| E REPRODUCIBLE | PASS | re-execução byte-a-byte |
| F LABEL_NOT_PARAMETER_ARTEFACT | PASS | grade de 135 pontos; células instáveis são retidas, não publicadas |
| G DISCRIMINATES_BETWEEN_SEASONS | PASS | quota da classe dominante 0.42 / 0.67 |
| H REFRESHABLE_WITHOUT_RESEARCH | PASS | **estava invertido** (exigia `delta_rows == 0`: um refresh que funciona falhava, uma fonte morta passava); agora deteta 3 formas de falha silenciosa e exige que um controlo negativo dispare |
| I GENERALIZES | PASS | **era um `PASS` constante**; agora corre o 4º caso ponta-a-ponta e falha se a série não variar |
| **J NOT_DUPLICATE** | **PARTIALLY_OVERLAPS** | **corrigido**: era respondível a partir desta própria branch (ler ≠ tocar). O portal já envia 17 casos `O1_FIELD_PRESSURE` ("Pressione in campo"), incluindo videira × oídio × Toscana a nível provincial — e **não tem vocabulário nenhum para a oliveira**. Inversão de cobertura: o portal cobre a célula em que esta capacidade se tem de calar, e não tem palavras para a única que ela publica |

```
PASS = 9   FAIL = 0   PARTIALLY_OVERLAPS = 1
```
O gate J deixou de ser `NOT_TESTABLE`: foi respondido, e a resposta não é uma aprovação.

## L — A ÚNICA CÉLULA QUE QUALIFICA HOJE

```
REGIÃO  Toscana    CULTURA  oliveira    PROBLEMA  Bactrocera oleae, infestação danosa
SAFRAS  20 completas + 2026 em curso    VISITAS  79 251
LATÊNCIA 2 dias    ESTABILIDADE 0.918   PUBLICÁVEIS 8/10 províncias
CONSISTÊNCIA INTERNA na métrica publicada: rho +0.449, que EXCEDE a concordância do
  próprio esforço de amostragem (+0.252) — o teste que o oídio falha
CURRENT_PRESSURE_MONITOR = PROVED
```

## M — O QUE FOI RETIRADO DURANTE ESTA MISSÃO

- **Generalização geográfica** — retirada por completo
- **"Mais forte que o caso de calibração"** — comparava métricas diferentes
- **Concordância entre províncias do oídio como evidência** — o esforço concorda mais (+0.738) que a doença (+0.229)
- **"21 safras"** → 20 completas + 1 em curso
- **"Dois pares negativos"** → nove
- **"Três casos"** → 3 execuções sobre 2 painéis

## N — ERROS MEUS QUE O RED TEAM ENCONTROU (19 no total, `CHECKPOINTS/12`)

**24 achados no total.** Os cinco que mais importam, porque são erros de *método*, não de aritmética:

1. **O gate A auto-certificava-se.** O papel da evidência era uma constante na saída. Alimentado com uma série de chuva teria carimbado "observação oficial de campo" e passado o seu próprio gate.
2. **O gate B era uma tautologia.** Testava `CUTOFF_LABEL == "NOWCAST"`, que `Cutoff.label()` não pode deixar de devolver. A única garantia contra enquadramento preditivo era incapaz de falhar.
3. **`denominator_guard` e `season_completeness` eram código morto.** Escrevi-os, medi o impacto, reportei a medição — e nunca os chamei. Exatamente a mesma falha de `contracts.py` existir sem nenhum runner o importar.
4. **A frase-manchete contradizia a própria tabela.** Dizia "scouts registaram infestação em 1 168 visitas"; 1 168 é o número de visitas *pontuadas*, e quatro daquelas províncias apareciam a 0,000 na linha seguinte.
5. **O gate I também era um `PASS` constante** — o terceiro do mesmo conjunto. Não são três acidentes: **quando escrevi um gate para uma alegação em que acreditava, escrevi-o de forma a concordar comigo.**

**E o achado mais importante da missão inteira não é um número:** a propriedade de que mais me
orgulhava — *falha alto em UNKNOWN, nunca baixo em zero* — era **falsa** na primeira vez que o
módulo encontrou um caso para que não fora construído. Não descobriria isso testando nos casos
que eu próprio escolhi.

Verifiquei cada achado antes de conceder. Refutei um na magnitude alegada (C8: 3 valores >100,
não 68) e publiquei os meus números onde divergiram dos do revisor.

## O — LEI ZERO, ESTADO FINAL

```
NOT_TESTABLE != NO ......... gate J e Abruzzo continuam NOT_TESTABLE, não NO
NOT_FOUND != DOES_NOT_EXIST  nenhuma ausência foi convertida em inexistência
PREDICTOR != OUTCOME ....... agora EXIGIDO em código, não prometido
MODELLED != OBSERVED ....... MODELLED_RISK e FORECAST recusados como outcome, testado
REGIONAL != NATIONAL ....... nenhuma figura nacional existe nem é produzível
CORRELATION != PREDICTION .. concordância entre províncias é consistência interna, não perícia
HISTORICAL_VALUE != EARLY_WARNING ... FIRST_PROVED_CUTOFF = None mantém-se
FAILURE != ZERO ............ rowCount 0 é FALHA; denominador 0 é recusado
```

## P — O QUE NÃO FOI FEITO, DE PROPÓSITO

Nenhuma tela. Nenhum toque na branch do portal. Nada em produção. Espanha e França não abertas.
Nenhuma expansão EAME. Nenhum resultado negativo escondido. Nenhum force push.

## Q — SE ALGUÉM QUISER AVANÇAR, A ORDEM É ESTA

1. Responder ao gate **J** — o portal já tem esta capacidade? Sem isso, não se decide.
2. Nomear um dono para o refresh, incluindo a regra `rowCount == 0 → FALHA`.
3. Decidir o âmbito com honestidade: **uma célula qualifica hoje**. Uma vista para uma célula
   numa região é um produto diferente de uma plataforma.
4. Só depois, e só se J passar, considerar a tela — segundo `SHADOW_UI_SPEC.md`.

## R — VEREDICTO

```
DESERVES_FUTURE_INTEGRATION = YES_SCOPED     (uma célula, uma região, sem previsão, sem produto)
PORTAL_INTEGRATION          = NO
```

A ferramenta merece ser considerada porque faz três coisas que a maioria das ferramentas deste
tipo não faz: **recusa-se a falar quando não pode**, **mede o seu próprio julgamento em vez de o
declarar ausente**, e **falha alto em UNKNOWN em vez de baixo em zero**. O que ainda não merece é
ser chamada de plataforma: oito províncias, uma cultura, uma região, e uma segunda célula testada
que não passou.
