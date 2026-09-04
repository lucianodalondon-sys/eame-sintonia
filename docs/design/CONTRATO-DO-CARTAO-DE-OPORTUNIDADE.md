# O contrato mínimo de uma oportunidade comercial

> Contrato de informação, não de interface. O portal não foi tocado nesta
> rodada — nem casco, nem copy, nem layout.

```
BASE      claude/opportunity-commercial-priority-v1 · 0ddf52d
BUILD_ID  V21-473db7a54b90c382
TESTEMUNHA  botrite × videira × Emilia-Romagna  ·  OPP_5F31A63F844D
```

A tela mostrava, no mesmo cartão, `ACT NOW` e «no canonical window linked».
Não era erro de interface: os dois saíam do motor, e o motor estava certo em
publicar os dois — porque estava errado ao chamar um de `ACT NOW`.

```python
# o defeito, em duas linhas, no commit auditado
o['STATUS'] = estado_temporal(dias, arquetipo, jest != 'UNKNOWN')   # → WATCH
if o['STATUS'] == 'WATCH' and sidade is not None and sidade <= 30:
    o['STATUS'] = 'ACT_NOW'          # ← a IDADE DO BOLETIM virou urgência
```

    A DATA DO BOLETIM DIZ QUE O SINAL É CORRENTE.
    ELA NÃO DIZ QUANDO SE PULVERIZA. SÃO DOIS RELÓGIOS, E TINHAM UM NOME SÓ.

---

## 1 · O contrato mínimo

Um caso só pode ser chamado de **oportunidade comercial** quando as cinco
perguntas têm dono, e cada resposta aponta para um campo — nunca para um
adjetivo.

| # | pergunta | responde |
|---|---|---|
| 1 | **SINAL** — o que está acontecendo? | `CROP` · `TARGET` · `GEOGRAPHY` · `NEED_DIRECTION` · `NEED_EXCERPT` · `SIGNAL_DATE` · `SIGNAL_CURRENCY` |
| 2 | **OPORTUNIDADE** — por que isso importa à ADAMA? | `COMMERCIAL_PRIORITY` · `WHY_COMMERCIAL_CODES` · `PRODUCT_LINK_STATE` |
| 3 | **MOMENTO** — agir, preparar ou acompanhar? | `STATUS` · `ACTION_CHAIN_LINKS` · `COMMERCIAL_WINDOW` · `COMMERCIAL_TIMING_BASIS` |
| 4 | **PRODUTO** — qual solução está ligada? | `MATCHED_COMMERCIAL_PRODUCT_NAMES` · `ACTIVE_INGREDIENT_NAMES` · `MODE_OF_ACTION_CODES` · `LABEL_QUOTES` · `PRODUCT_RESTRICTIONS` |
| 5 | **AÇÃO** — quem faz o quê? | `ACTION_BY_DEPARTMENT` |

E duas leis atravessam as cinco:

> **NADA É INFERIDO DE «EXISTE PRODUTO NESSA CULTURA».**
> **O QUE NÃO SE SABE APARECE COM O NOME DO QUE FALTA — NUNCA EM BRANCO.**

---

## 2 · Campo a campo — o que já existe, o que se deriva, o que falta

`EXISTE` = já estava no pacote · `DERIVADO` = passou a existir nesta rodada, de
regra sobre dado que já havia · `COLETA` = precisa de fonte nova ·
`NÃO EXISTE` = não há e, em alguns casos, não deve haver.

### A · O QUE ESTÁ ACONTECENDO

| campo do contrato | estado | onde |
|---|---|---|
| cultura, alvo, região | **EXISTE** | `CROP` `TARGET` `GEOGRAPHY` |
| direção do sinal | **EXISTE** | `NEED_DIRECTION` + `NEED_EXCERPT` (a frase da fonte viaja junto) |
| quantidade / diversidade de evidências | **DERIVADO** | `COMMERCIAL_MAGNITUDE_DIMENSIONS.SINAIS_DE_CAMPO` e `.FONTES_INDEPENDENTES` |
| data / recência | **EXISTE + DERIVADO** | `SIGNAL_DATE` · `SIGNAL_CURRENCY` (CURRENT/RECENT/OLD) |
| **intensidade / força** | **COLETA** | o boletim declara **ocorrência e limiar**, não incidência medida. «ao ultrapassar 5% de cachos infestados» é gatilho, não medida. Transformá-lo em intensidade seria inventar um número. |

### B · POR QUE IMPORTA COMERCIALMENTE

| campo do contrato | estado | onde |
|---|---|---|
| necessidade do produtor | **EXISTE** | `NEED_DIRECTION` + `NEED_EXCERPT` + `NEED_METHOD` |
| vínculo com o portfólio | **EXISTE** | `PRODUCT_LINK_STATE` (`VERIFIED_LABEL_MATCH`) |
| produtos candidatos | **EXISTE** | `PRODUCT_RELATIONSHIPS` (rótulo, 163) e `MATCHED_COMMERCIAL_PRODUCT_NAMES` (catálogo, 51) — **duas camadas, nunca fundidas** |
| força do vínculo | **DERIVADO** | `PRODUCT_MATCH_CONFIDENCE`; o eixo região é nacional por construção e está dito em `PRODUCT_AUTHORIZATION_GEOGRAPHY` |
| restrições conhecidas | **DERIVADO** | `PRODUCT_RESTRICTIONS` — expiração de aprovação europeia com data e `EVIDENCE_ID` |
| restrições de rótulo (nº de aplicações, intervalo de segurança) | **NÃO EXISTE estruturado** | estão dentro de `LABEL_QUOTES` («È consentita una sola applicazione all'anno»). Estruturar por regex é interpretar bula, e **bula não se interpreta por regex** |

### C · JANELA / TIMING

| campo do contrato | estado | onde |
|---|---|---|
| janela agronômica | **EXISTE (vazia hoje)** | `WINDOW_START` `WINDOW_END` `WINDOW_KIND` `WINDOW_FIELD` |
| estado da janela | **EXISTE**, com outro vocabulário | `COMMERCIAL_WINDOW` ∈ `ACT_NOW · PREPARE_NOW · FUTURE · CLOSED · UNKNOWN`. **Proposta:** renomear para `OPEN · APPROACHING · FUTURE · CLOSED · UNKNOWN` — é vocabulário de estado, não de ação, e hoje o mesmo nome serve às duas coisas. **Não renomeado agora: o portal lê este enum.** |
| tempo para agir | **EXISTE** | `DAYS_REMAINING` |
| fonte da janela | **EXISTE** | `WINDOW_FIELD` + o `IT-WIN-*` em `WHY_NOW_CHAIN.JANELA_COMPATIVEL.EVIDENCE` |
| **janela para os casos reais** | **COLETA** | medido na rodada anterior: 17 combinações cultura × alvo × região precisam de janela, **0 têm**. As fontes regionais declaram o momento **fenologicamente** («in preraccolta»), não em datas |

### D · TAMANHO / RELEVÂNCIA

| dimensão | estado | onde |
|---|---|---|
| nº de sinais · fontes independentes · extensão regional | **DERIVADO** | `COMMERCIAL_MAGNITUDE_DIMENSIONS` |
| área oficial da cultura na região | **QA, não coleta** | as linhas ISTAT existem (videira Emilia-Romagna 2026: 52.769 ha) mas estão `CLIENT_SAFE=false`, `QA_UNREVIEWED`. O dado está no acervo; **falta a revisão que o libera** |
| recorrência (o par se repete no tempo?) | **COLETA** | o acervo é um retrato, não uma série. Precisa de boletins da mesma praça em semanas sucessivas |
| importância da cultura para o portfólio | **NÃO EXISTE — e não deve** | é dado interno ADAMA. O SINTONIA é externo por premissa |
| TAM / SAM / dinheiro | **PROIBIDO** | não há fonte. `COMMERCIAL_MAGNITUDE = UNKNOWN` quando não há dimensão contável |

### E · O QUE A ADAMA PODE FAZER

**DERIVADO** — `ACTION_BY_DEPARTMENT`, um código por departamento, cada um com o
`WHY_CODE` que o convocou:

| departamento | ações possíveis |
|---|---|
| `MARKET_DEVELOPMENT` | `VALIDATE_WINDOW_IN_REGION` · `CONFIRM_RECOMMENDATION_IN_FIELD` · `NO_MOVEMENT` |
| `COMMERCIAL` | `CONTACT_NOW` (só com `ACT_NOW`) · `PREPARE` · `NO_MOVEMENT` |
| `MARKETING` | `MESSAGE_AVAILABLE` (só com `EXTERNAL_MATERIAL_READY = YES`) · `PREPARE_INTERNAL_ONLY` · `NO_MOVEMENT` |
| `TECHNICAL_SCIENTIFIC` | `ESTABLISH_APPLICATION_WINDOW` · `RESOLVE_AMBIGUOUS_DIRECTION` · `CLASSIFY_MODE_OF_ACTION` · `NO_MOVEMENT` |
| `SUPPLY` | `WATCH_REGULATORY_DATE` · **`NOT_CONVENED`** |

> **PRESSÃO AGRONÔMICA NÃO É PEDIDO. CONVOCAR SUPPLY SEM FATO É INVENTAR UM.**

`SUPPLY` só é convocado quando há **fato publicado com data** sobre substância
ligada ao caso — hoje, apenas expiração de aprovação europeia. Sem isso,
`NOT_CONVENED · SEM_BASE_FACTUAL`. `T37` prova isso no pacote inteiro.

**«Necessidade de material/demonstração»** fica fora: se existe material físico
é dado interno. O que o motor pode responder é outra pergunta —
`EXTERNAL_MATERIAL_READY`: *este caso pode sair da ADAMA?*

### F · CONFIANÇA — quatro, nunca uma

| campo | responde | derivação |
|---|---|---|
| `SIGNAL_CONFIDENCE` | o que foi observado se sustenta? | fontes independentes × recência |
| `WINDOW_CONFIDENCE` | quando agir é conhecido? | `ALTA` só com janela de **aplicação**; `NENHUMA` sem janela |
| `PRODUCT_MATCH_CONFIDENCE` | o vínculo com o portfólio é firme? | rótulo verificado × presença no catálogo |
| `COMMERCIAL_PRIORITY` | isto é oportunidade comercial defensável? | os portões semânticos da V1.1 |

Uma confiança só obrigaria a uma média entre coisas que não se somam: **o sinal
pode ser forte e a janela inexistente**, e a média esconderia as duas. Foi
exatamente o que aconteceu no cartão da testemunha.

### G · POR QUE AGORA — obrigatório para ACT NOW

**DERIVADO** — `WHY_NOW_CODES` e `WHY_NOW_CHAIN`, com o identificador da
evidência de cada elo.

---

## 3 · A regra executável do ACT NOW

```
SINAL ATUAL + JANELA COMPATÍVEL + VÍNCULO COM PORTFÓLIO + TEMPO PARA AÇÃO
= ACT_NOW
```

```python
def elos_de_agora(o):
    return {
     'SINAL_ATUAL':           idade <= 30 and NEED_DIRECTION in NECESSIDADE_POSITIVA,
     'JANELA_COMPATIVEL':     WINDOW_KIND == 'APPLICATION' and WINDOW_STATE != 'UNKNOWN',
     'VINCULO_COM_PORTFOLIO': TARGET and PRODUCT_LINK_STATE == VERIFIED_LABEL_MATCH
                              and COMMERCIAL_PRODUCT_COUNT > 0,
     'TEMPO_PARA_ACAO':       DAYS_REMAINING is not None and 0 <= DAYS_REMAINING <= 30,
    }
```

Cada elo tem um teste que o derruba sozinho (`T32`). `T33` prova que a idade do
sinal — 0, 1, 7 ou 29 dias — **nunca** produz `ACT_NOW` sem janela. `T34` percorre
o pacote e exige, de todo `ACT_NOW`, a cadeia fechada e `WINDOW_KIND =
APPLICATION`.

**E o tempo não foi apagado dos casos — foi renomeado.** O boletim de ontem que
manda intervir declara um momento; ele não declara uma janela. As duas coisas
são verdade, e agora têm nomes diferentes:

| campo | de onde vem |
|---|---|
| `COMMERCIAL_WINDOW` | **só** de janela de aplicação com datas |
| `SIGNAL_CURRENCY` | idade do documento que sustenta o caso |
| `COMMERCIAL_TIMING_BASIS` | `APPLICATION_WINDOW` · `CURRENT_SOURCE_RECOMMENDATION` · `NONE` |

`ACT_NOW` exige o primeiro. `COMMERCIAL_PRIORITY` aceita o segundo — **e o
cartão diz qual dos dois foi**, em `COMMERCIAL_TIMING_BASIS` e no código
`TIME_FROM_SOURCE_RECOMMENDATION`.

---

## 4 · Os estados de ação permitidos

| estado | quando |
|---|---|
| `ACT_NOW` | os quatro elos fechados |
| `PREPARE_NOW` | janela de aplicação existe e abre entre 31 e 120 dias |
| `FUTURE_PREPARATION` | janela a mais de 120 dias, ou arquétipo regulatório (O5) |
| **`VALIDATE_NOW`** ⟵ novo | necessidade positiva corrente **e** produto ligado, **sem janela**: o que falta tem nome |
| `WATCH` | sinal não corrente, ou nada acima se sustenta |
| `TO_VALIDATE` | portão de evidência aberto (mantido como estava) |

**`INVESTIGATE_NOW` não foi criado.** A missão o oferecia; nenhuma regra o
sustenta hoje: caso com leitura incompleta já cai em `TO_VALIDATE` (portão
aberto) ou `WATCH`. Criar um estado que nenhum caso ocupa é vocabulário, não
contrato.

---

## 5 · A testemunha, campo a campo

### `OPP_5F31A63F844D` · botrite × videira × Emilia-Romagna

**O QUE SABEMOS**

| | |
|---|---|
| direção | `POSITIVE_PRESSURE` |
| frase da fonte | «Vite/botrite: intervir em pre-colheita com Fenhexamid (max 2) ou alternativas biologicas.» |
| quem disse | `IT-PHEN-001` — Bollettino di produzione integrata e biologica, Modena n. 28, 01/09/2026 |
| como o par foi formado | `PAIR_IN_SAME_CLAUSE` — cultura e alvo na mesma oração |
| recência | `CURRENT` — 1 dia |
| evidências | 8 sinais de campo · 3 fontes independentes · o mesmo par em 2 regiões |

**O QUE NÃO SABEMOS**

| | |
|---|---|
| janela de aplicação | **NÃO SEI** — nenhuma janela do acervo declara esta cultura, este alvo e esta região |
| intensidade | **NÃO SEI** — o boletim declara ocorrência, não incidência |
| área oficial | **NÃO SEI** — a linha ISTAT existe e não é client-safe |
| elos que faltam | `JANELA_COMPATIVEL` · `TEMPO_PARA_ACAO` |

**POR QUE É OPORTUNIDADE** — `COMMERCIAL_PRIORITY = SALES_READY`, razões
`ALL_GATES_CLOSE` + `TIME_FROM_SOURCE_RECOMMENDATION`. `OPPORTUNITY_CONFIRMED`,
nenhum portão aberto, nenhum achado de red team.

**QUAL PRODUTO** — rótulo ministerial em `AGHARTA`, `BANJO`, `EMBRACE`; **um só
está no catálogo comercial: `BANJO`**. Substância `FLUAZINAM`, modo de ação
**FRAC 29**, modo de emprego citado no rótulo («applicare preventivamente alla
dose di 100-150 ml/hl… È consentita una sola applicazione all'anno»). Restrição
publicada: aprovação europeia de fluazinam expira em **2027-11-30**
(`AI_FLUAZINAM`).

> ⚠️ A tela dizia «mode of action = not known» e «application = not known». Os
> dois estavam no acervo, ligados pelo número de registro `013905` — a mesma
> junção que o catálogo comercial já usava. O cartão é que não carregava o campo.
>
>     «NÃO SEI» DITO POR QUEM NÃO FOI OLHAR NÃO É «NÃO SEI»: É DESCUIDO.

**QUAL É A JANELA** — `WINDOW_STATE = UNKNOWN`, `WINDOW_KIND = null`,
`COMMERCIAL_WINDOW = UNKNOWN`, `WINDOW_CONFIDENCE = NENHUMA`. O tempo vem de
`CURRENT_SOURCE_RECOMMENDATION`.

**QUAL É A AÇÃO** — `STATUS = VALIDATE_NOW`. **O `ACT NOW` foi retirado deste
caso**, como a missão exigiu, porque a cadeia não fecha.

**POR QUE AGORA** — `WHY_NOW_CODES = ['SEM_JANELA_COMPATIVEL',
'SEM_TEMPO_PARA_ACAO']`. Não há «por que agora»: há «por que ainda não».

**QUEM DEVE AGIR**

| departamento | ação | porque |
|---|---|---|
| MARKET DEVELOPMENT | `VALIDATE_WINDOW_IN_REGION` | sem janela compatível |
| COMMERCIAL | `PREPARE` | prioridade comercial sem tempo provado |
| MARKETING | `MESSAGE_AVAILABLE` | `EXTERNAL_MATERIAL_READY = YES` |
| TECHNICAL / SCIENTIFIC | `ESTABLISH_APPLICATION_WINDOW` | sem janela compatível |
| SUPPLY | `WATCH_REGULATORY_DATE` | data regulatória em ativo ligado (2027-11-30) |

Ficha executável: `python3 scripts/v21_ficha_de_oportunidade.py`, gravada em
`data/samples/AUDITORIA-SOMBRA/V113-FICHA-DA-TESTEMUNHA.json`.

---

## 6 · O que mudou no pacote inteiro

| | antes | depois |
|---|---|---|
| `ACT_NOW` | **16** | **0** |
| `PREPARE_NOW` | 11 | 0 |
| `VALIDATE_NOW` | — | **5** |
| `WATCH` | 0 | 22 |
| `FUTURE_PREPARATION` | 7 | 7 |
| `TO_VALIDATE` | 9 | 9 |
| `COMMERCIAL_PRIORITY = SALES_READY` | 5 | **5** |
| `EXTERNAL_MATERIAL_READY = YES` | 5 | **5** |
| casos | 43 | 43 |

**Os 16 `ACT_NOW` caíram porque nenhum tinha janela de aplicação.** Nenhum caso
nasceu, nenhum morreu, e a régua comercial não mudou de limiar: os mesmos 5
continuam `SALES_READY`, agora dizendo **qual relógio** os sustenta.

Os 5 `VALIDATE_NOW` são exatamente os 5 `SALES_READY`:

```
OPP_5F31A63F844D  videira × botrite       Emilia-Romagna
OPP_3C8C3960CC66  videira × traça-da-uva  Emilia-Romagna
OPP_F8106D5E1767  videira × botrite       Toscana
OPP_75C37DED9160  macieira × carpocapsa   Veneto
OPP_9C600748BB1B  milho × piralide        Friuli-Venezia Giulia
```

E o que falta neles é **uma coisa só, e é a mesma**: a janela de aplicação da
região — as 5 primeiras combinações do vão medido na rodada anterior.

---

## 7 · Nenhum estado nasce de «existe produto relacionado»

`T36`, executável, em duas metades:

1. um caso sintético com **3 produtos do catálogo**, rótulo verificado e
   geografia que se sustenta, mas `NEED_DIRECTION = UNKNOWN`, **não** vira
   `SALES_READY` nem `ACT_NOW`;
2. no pacote inteiro, todo `SALES_READY` tem `NEED_DIRECTION` positiva, alvo
   declarado e produto de catálogo — os três, sempre.

    O RÓTULO AUTORIZA. O CATÁLOGO OFERECE. NENHUM DOS DOIS PEDE.
    QUEM PEDE É O BOLETIM, E SÓ ELE.

---

## 8 · Suíte

**729 descobertos · 724 executados · 6 falhas · 2 erros** — as mesmas 8
anteriores a esta linha de missões. Provas da camada comercial: **66/66**.
Cadeia `EXIT=0`, 0 violações de contrato, 0 campos só em português.

```
portal / casco = NÃO TOCADO      copy = NÃO ALTERADA
thresholds     = NÃO ALTERADOS   merge = NÃO      publicação = NÃO
```
