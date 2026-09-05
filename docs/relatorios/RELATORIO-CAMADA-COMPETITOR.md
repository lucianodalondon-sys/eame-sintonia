# Concorrência vira camada — e a Meta Ads Library ganha nome próprio

`2026-08-30` · rodada de **CONTRATO / ARQUITETURA**. Nenhuma coleta, nenhum cron, nenhum
portal, nenhum score, nenhum dado competitivo inventado.

---

## O que mudou, em uma frase

Concorrência deixa de ser um "monitor de concorrentes" ao lado do produto e passa a ser
**uma das sete camadas** que um caso de convergência cruza — entrando com **duas colunas
independentes** que nunca se fundem.

```
CAMPO × CIÊNCIA × CLIMA × REGULATÓRIO × PORTFÓLIO ADAMA LOCAL × CONCORRÊNCIA × TEMPO
```

## A · Arquivos canônicos alterados

| arquivo | o que mudou |
|---|---|
| `data/samples/EAME-COMPETITOR-CONTRACT-V1.json` | **novo** — o contrato da camada |
| `docs/piloto/ARQUITETURA-DE-PRODUTO-ATUAL.md` | ganha a seção CONVERGÊNCIA. É o documento que vence quando dois discordam |
| `docs/ferramentas/ARQUITETURA-DE-INFORMACAO-EAME.md` | `ÁREA · COMPETITIVE` reescrita com os cinco estados e o quinto relógio |
| `docs/fontes/ATLAS-DE-FONTES-EAME.md` | ficha `EU-T9-002` da Meta Ads Library + separação obrigatória em T9 |
| `docs/cruzamentos/MATRIZ-DE-CRUZAMENTOS-EAME.md` | cruzamento `X-012`, `POSSÍVEL NÃO TESTADO` |
| `data/samples/DISPLAY-LAYER-V1.json` | +20 regras em PT/EN/ES para os estados novos |
| `tests/test_competitor_layer.py` | **novo** — 45 regressões |

O atlas passa de 36 para **37 SOURCE_IDs**, e os sete documentos que publicam esse número
foram sincronizados pelo dono (`scripts/metricas_canonicas.py`).

## B · Contrato da camada COMPETITOR

Duas perguntas, e **elas são duas de propósito**:

1. **QUEM TEM RESPOSTA?** — quais concorrentes têm resposta **registrada localmente** para
   `COUNTRY × CROP × ISSUE`. Fato administrativo, datado, verificável.
2. **QUEM ESTÁ SE MOVIMENTANDO AGORA?** — quem está anunciando, comunicando ou fazendo
   atividade técnica publicamente observável.

Fundir as duas produziria a frase mais cara possível — *"o concorrente está atacando este
problema"* — que **não está em nenhuma das duas fontes**.

### As leis

`REGISTRATION ≠ SALES` · `≠ STOCK` · `≠ COMMERCIAL AVAILABILITY` ·
`PORTFOLIO GLOBAL ≠ PORTFOLIO LOCAL` · `PUBLICIDADE ≠ DEMANDA` · `SILÊNCIO ≠ AUSÊNCIA` ·
`OBSERVATION_START ≠ ACTIVITY_START` · `FIRST SNAPSHOT ≠ NO CHANGE` ·
`PROVED ROUTE ≠ MARKET-WIDE BASELINE` · `AUSENTE_MEDIDO ≠ NÃO_TESTADO` ·
`WHO CAN INVESTIGATE NOW ≠ WHO SHOULD ACT NOW`

**Regra de admissão:** nenhum concorrente tem "resposta em ES/IT/FR" porque existe
globalmente ou porque tem o mesmo produto em outro país. Sem evidência do registro daquele
país, o estado é `NOT_PROVED` — **que é diferente de "não tem"**.

## C · O papel da META ADS LIBRARY

Ela é **nominal** (`EU-T9-002`), não escondida em "social media". Motivo: é a única fonte
identificada até aqui que registra **peça publicitária paga com anunciante identificado e
datas**. Isso é outra natureza de dado, não um canal a mais numa lista.

**Ela não é a Meta Graph API.** O que este repositório já mediu é a Graph API
(`EU-T8-001`, **400 sem token**), que serve para conteúdo orgânico e exige App Review. A
Ads Library nunca foi aberta aqui. Por isso o veredito é **`NÃO TESTADO`** — e não `RED`,
e muito menos `AUSENTE_MEDIDO`.

**Prova:** `ATIVAÇÃO PUBLICITÁRIA OBSERVADA`. Só isso.

| não prova | |
|---|---|
| `META AD ≠ SALES` | `META AD ≠ MARKET SHARE` |
| `META AD ≠ CAMPAIGN SUCCESS` | `META AD ≠ STOCK` |
| `META AD ≠ PRODUCT AVAILABILITY` | `META AD ≠ INVESTIMENTO` |

**Denominador obrigatório:** toda contagem viaja com o que foi consultado — quais
anunciantes, qual país, qual período, qual termo. *"A Syngenta tem 14 anúncios"* sem isso
é um número sem denominador.

**O que ela fecharia:** `X-003` (COMPETITOR + PRODUCT + CROP + COMMUNICATION) está
`NÃO COMPÕE` desde a MISSÃO 02 porque a perna COMMUNICATION não existe. Esta é a primeira
rota candidata a essa perna que **não** exige varrer site com proteção anti-robô. Virou o
cruzamento `X-012`.

## D · Como COMPETITOR entra na convergência

| coluna | fonte | estado hoje |
|---|---|---|
| RESPOSTA REGISTRADA | registro oficial nacional | `DEMONSTRABLE` — é o `X-005`, COMPROVADO |
| ATIVAÇÃO OBSERVADA | comunicação · Meta Ads Library · atividade técnica | `PLANNED` — sem dado em nenhum país |

### As cinco perguntas que todo caso futuro faz

1. quem tem resposta?
2. quem está anunciando?
3. quem começou primeiro?
4. isso coincide com campo, ciência ou janela agronômica?
5. **ainda existe tempo para agir?**

A quinta é a mais difícil, e ela liga a camada nova ao calendário agronômico da rodada
anterior: só tem resposta com resolução temporal suficiente. Com `APPROXIMATE` ou sem
fenologia observada, a resposta é `NOT_KNOWN` — **e continua útil, porque diz o que falta
medir**.

### O quinto relógio

`COMPETITOR OBSERVATION CLOCK` — `FIRST_OBSERVED` · `LAST_OBSERVED` · `CHANGE_OBSERVED` ·
`SOURCE_DATE` · `AS_OF_DATE`.

Os quatro do calendário continuam quatro. Este é o **quinto**, e não se funde com nenhum —
em particular não com o `REGISTERED_PRODUCT_WINDOW`, que fala do que o rótulo autoriza. O
frescor continua **derivado de `AS_OF_DATE`**, nunca persistido: gravar "há 12 dias" seria
gravar um fato que muda sozinho.

Ele existe para uma pergunta: **quem viu primeiro?** — comparando sinal de ciência, sinal
de campo, sinal competitivo, ativação, janela agronômica e janela comercial quando
conhecida. Ativação **antes** do sinal de campo é uma história; **depois** é outra.

**O limite duro:** `FIRST_OBSERVED` é quando **nós** observamos, não quando o concorrente
começou. Sem série histórica da própria fonte, a diferença entre as duas coisas é
exatamente o tamanho do erro.

## E · Estados e campos mínimos

Cinco estados, e **os quatro primeiros nunca se somam**:

`COMPETITOR_REGISTERED_RESPONSE` · `COMPETITOR_PAID_META_ACTIVITY` ·
`COMPETITOR_PUBLIC_COMMUNICATION` · `COMPETITOR_TECHNICAL_ACTIVITY` · `NOT_KNOWN`

Somar as quatro num indicador destruiria exatamente a informação que torna a camada útil:
**qual delas está acontecendo**. É por isso que não há score.

**COMPETITOR_RESPONSE** — obrigatórios: `COUNTRY` · `COMPETITOR_ENTITY` · `PRODUCT` ·
`REGISTRATION_ID` (a chave é o número, nunca o nome comercial) · `ACTIVE_INGREDIENT` ·
`AUTHORIZED_CROP` · `REGULATORY_STATUS` · `OFFICIAL_SOURCE` · `SOURCE_DATE` · `EVIDENCE`.
Opcionais com motivo escrito: `AUTHORIZED_TARGET` (quando falta, a linha é de nível cultura
e **não some da resposta**), `AUTHORIZED_WINDOW` com `TEMPORAL_RESOLUTION` junto,
`EXPIRY_DATE` (`EXPIRY ≠ WITHDRAWAL`), e `COMPETITOR_GROUP` — que fica `NÃO SEI` porque
agrupar razão social em grupo econômico **ainda não foi medido** neste repositório
(`DECK-015`).

**COMPETITOR_ACTIVATION** — obrigatórios: `COUNTRY` · `COMPETITOR_ENTITY` ·
`ACTIVATION_STATE` · `CHANNEL` · `CLAIM_TEXT_ORIGINAL` (texto literal, idioma original) ·
`FIRST_OBSERVED` · `LAST_OBSERVED` · `PIECES_OBSERVED` **com denominador** · `SOURCE_DATE`
· `EVIDENCE`. `PRODUCT` só quando identificável na própria peça — deduzir o produto pela
cultura seria inventar.

## F · Três exemplos conceituais — **capacidade, não dado**

| caso | composição | saída |
|---|---|---|
| **1 · COMPETITIVE CONVERGENCE WORTH INVESTIGATING** | sinal de campo + janela + resposta ADAMA + concorrentes com resposta + ativação Meta | `PRIORITY TO INVESTIGATE` |
| **2 · POSSIBLE EARLY WINDOW** | sinal começando + todos com resposta registrada + nenhuma ativação observada | *"o sinal pode estar surgindo antes de forte ativação pública competitiva"* |
| **3 · POSSIBLE PRE-POSITIONING SIGNAL** | concorrente anuncia + ciência aponta + campo silencioso | uma pergunta, e a resposta padrão é `NÃO SEI` |

**Nenhum conclui oportunidade comercial.**

O caso 2 nunca é `WHITE SPACE`, `COMPETITIVE ADVANTAGE` nem `SALES OPPORTUNITY` — e traz
uma ressalva obrigatória: *"nenhuma ativação observada"* só vale **com o denominador do que
foi consultado**. Sem ele, é `NÃO_TESTADO` disfarçado de descoberta.

O caso 3 não separa antecipação de rotina sem série histórica do mesmo anunciante — e a
**primeira captura nunca sustenta essa separação**. É a mesma lei que já governa o Radar do
Futuro: `FIRST SNAPSHOT ≠ NO CHANGE`.

Os três estão marcados `DATA = NOT_YET_COLLECTED`, com **o que falta** escrito em cada um.

## G · Impacto no mapa de ações

`WHO CAN INVESTIGATE NOW ≠ WHO SHOULD ACT NOW`

| público | recebe | quando |
|---|---|---|
| **MARKET DEVELOPMENT** — decisor central | investigar mudança competitiva e convergência | sempre que a camada muda de estado |
| **MARKETING** | comparar claims, mensagens, canais e timing | quando há ativação observada com texto original preservado |
| **REGULATORY / PORTFOLIO** | comparar respostas autorizadas | sempre — é a perna já provada |
| **SCIENCE / TECHNICAL** | avaliar diferenças técnicas | quando há ingrediente ativo e modo de ação dos dois lados |
| **COMMERCIAL** | **nada por padrão** | só quando a janela comercial puder ser sustentada — hoje `NOT_KNOWN` por contrato |
| **SUPPLY** | **nada** | só com informação interna, que este produto não tem |

O Sintonia diz **onde olhar primeiro**, com evidência. Não diz o que fazer.

## H · O que permanece NOT_YET_COLLECTED

| o quê | estado | países |
|---|---|---|
| qualquer peça da Meta Ads Library | `NÃO_TESTADO` | ES · IT · FR |
| comunicação pública de Syngenta, BASF e Corteva | `BLOQUEADO_MEDIDO` — 403 / 502 / 404 | ES · IT · FR |
| linha de base de ativação competitiva | `NOT_COLLECTED` | ES · IT · FR |
| agrupamento de razão social em grupo econômico | `NÃO_MEDIDO` (`DECK-015`) | ES · IT · FR |
| série histórica de ativação | `NOT_COLLECTED` | ES · IT · FR |

**403 não é ausência de comunicação.** A rota está bloqueada; o concorrente pode estar
comunicando normalmente onde não conseguimos ler.

## I · Próximo passo futuro — **não executado**

Abrir a Meta Ads Library **uma vez**, para **um par já escolhido** (ES × olivar × repilo),
com **um anunciante**, só para medir o que a fonte devolve. É o par onde as outras seis
camadas já têm dado real, então a sétima pode ser avaliada sem construir nada em volta.

Responderia quatro coisas: a rota funciona sem credencial paga? · o anunciante é
identificável como o concorrente, e não como uma agência? · há data de primeira e última
veiculação? · o produto é identificável na peça, ou só a marca institucional?

**Não faria:** coleta em massa · cron · base de concorrentes · painel · score.

Continua **não executado** — a missão proíbe coleta, e medir uma fonte é coleta.

## Uma honestidade, pela quinta vez

Escrevi um teste que proíbe citar concorrente sem dado medido. Ele reprovou na frase que
**ensina a lei**: *"'Procurei na Meta Ads Library e a Syngenta não anuncia' é uma afirmação;
'nunca abri a Meta Ads Library' é outra"* — dentro do campo `O_ERRO_MAIS_CARO_AQUI`.

É a quinta vez neste projeto que uma lista de termos proibidos dispara na própria
proibição. A correção é sempre a mesma e já virou padrão: percorrer campo a campo e ignorar
os campos cujo **nome** os marca como regra, motivo ou exemplo de erro.

E ele **também pegou um defeito real na mesma rodada**: a linha "comunicação pública de
Syngenta, BASF e Corteva" citava três empresas com a medição (403/502/404) no campo vizinho,
não na mesma frase. Afirmação e evidência agora viajam juntas.

---

```
COMPETITOR_LAYER_IN_ARCHITECTURE = YES
META_EXPLICIT_SOURCE             = YES
MASS_COLLECTION_STARTED          = NO
PORTAL_WORK_STARTED              = NO
SCORE_CREATED                    = NO
```

`CAPABILITY = PLANNED` para ativação · `DEMONSTRABLE` para resposta registrada ·
`DATA COVERAGE = NOT_YET_COMPLETE`.
