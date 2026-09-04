# RADAR FUTURO · ESPECIFICAÇÃO DE SUPERFÍCIE

**Isto é uma especificação, não uma implementação.** O portal não vive nesta branch
(ver `OVERNIGHT-BASELINE.md` §2), e construí-lo aqui criaria uma segunda linhagem do
casco. Este documento entrega ao dono do frontend o contrato pronto: o que existe,
com que nome, em que estado, e o que **não** pode ser inventado na tela.

```
FONTE          data/samples/IT-FUTURO-V1/IT-FUTURO-RADAR-V1.json
ITENS          10 sinais · 7 COMPLETE · 3 PARTIAL
LEI            o frontend APRESENTA. Não recalcula estado, janela, prioridade
               nem produto primário.
```

## 1 · Onde cada coisa entra

Nenhuma aba nova. Nenhum «Radar Canônico» como ferramenta de cliente — canônico é
arquitetura interna. Existe **um** `RADAR DELLE OPPORTUNITÀ`.

| área existente | o que desta rodada entra | o que **não** entra |
|---|---|---|
| **RADAR DELLE OPPORTUNITÀ** | nada de novo. Os 43 casos do motor continuam sendo a fonte; o que mudou foi a camada de **portfólio** deles (28 casos ganham produto) | nenhum dos 10 sinais futuros. Sinal futuro não é oportunidade atual |
| **RADAR FUTURO** | os 10 sinais `ITF-001…ITF-010` | os 3.035 candidatos brutos. Candidato não é sinal |
| **FINESTRE CULTURALI** | os 7 sinais com `WINDOW_EXPECTED = YES` e a janela **esperada**, rotulada como esperada | os 3 com `WINDOW_EXPECTED = UNKNOWN` — a ausência aparece, não se preenche |
| **CONCORRENZA** | `ITF-004` (registro novo de herbicida de cereais) | o nome comercial: a ASR não permite lê-lo |
| **INTELLIGENCE SCIENTIFICA** | `ITF-003`, `ITF-008`, `ITF-010` — resistência, parasitoide, série de acaros | causalidade parasitoide → queda de capturas. Nenhuma fonte a afirma |
| **PORTAFOGLIO** | `ITF-007` como caso didático de `PORTFOLIO RELATION ≠ LABEL AUTHORIZATION` | difenoconazol em batata como se fosse autorizado |
| **VOCI DAL CAMPO** | as citações em italiano de cada sinal | tradução automática da citação. A citação é prova; prova não se traduz |
| **FONTI** | os 12 documentos de origem, com data e URL | os 120 documentos que ainda não viraram inteligência |
| **ARCHIVIO** | o censo do acervo (`IT-ACERVO-CENSO-V1.json`) | — |

## 2 · O cartão de sinal futuro — os campos, na ordem

O item 17 da missão pede que cada cartão responda dez perguntas. Todos os dez
campos existem no JSON; nenhum precisa ser calculado na tela.

| pergunta | campo | quando falta |
|---|---|---|
| O QUE | `FUTURE_SIGNAL` | nunca falta |
| ONDE | `REGION` + `REGION_WHY` | 1 de 10: mostrar «ambito nazionale — la fonte non regionalizza» |
| CULTURA | `CROP` | nunca falta |
| ALVO | `TARGET` | nunca falta |
| QUANDO | `EXPECTED_START`/`END`, `HORIZON_BUCKET` | nunca falta |
| POR QUÊ | `CONFIDENCE_WHY` | nunca falta |
| TRIGGER | `TRIGGER` **e** `INVALIDATION_TRIGGER` | nunca falta |
| JANELA FUTURA | `EXPECTED_WINDOW_*`, `WINDOW_DEPENDS_ON_FIELD_MEASUREMENT` | 3 de 10 |
| RESPOSTA ADAMA | `PORTFOLIO_MATCHES` (todos) + `PRIMARY_MATCH` | 3 sem produto |
| O QUE FAZER ANTES | `ACTION_MAP`, 5 departamentos | nunca falta |

**`EVIDENCE_TIME_STATE` é obrigatório no cartão.** Um sinal `OBSERVED_NOW` e um
`EXPECTED` não podem ter a mesma aparência: a distinção é o produto.

## 3 · As frases, IT e EN — sem token interno na tela

| estado | IT | EN |
|---|---|---|
| `OBSERVED_NOW` | «Osservato ora» | «Observed now» |
| `EXPECTED` | «Atteso — non ancora osservato» | «Expected — not yet observed» |
| `ANNOUNCED` | «Annunciato; l'esito non è noto» | «Announced; the outcome is not known» |
| `HYPOTHESIS` | «Ipotesi nostra, non della fonte» | «Our hypothesis, not the source's» |
| `WINDOW_EXPECTED=UNKNOWN` | «Finestra non dichiarata dalla fonte» | «Window not declared by the source» |
| `WINDOW_DEPENDS_ON_FIELD_MEASUREMENT=YES` | «Dipende dall'osservazione in campo» | «Depends on farm-level observation» |
| `PRIMARY_MATCH=null` | «Più prodotti sostenuti allo stesso modo» | «Several products equally supported» |
| `ADAMA_LOCAL_RESPONSE=NO` | «Nessun prodotto autorizzato per questa coppia» | «No authorised product for this pair» |
| `NOT_IN_SOURCE` | «La fonte non lo dice» | «The source does not say» |
| `NOT_COLLECTED` | «Non ancora raccolto» | «Not yet collected» |

Estas duas últimas são a regra do item 19: quando não há valor, o motivo aparece.
**Não inventar prosa para preencher cartão.**

## 4 · O que a tela nunca faz

1. **Não escolhe produto primário.** `PRIMARY_MATCH` é `null` em 7 dos 10 sinais e
   em 32 das 43 oportunidades. `null` significa *mostrar todos sem hierarquia* —
   nunca «principal + N outros».
2. **Não promove a `ACT_NOW`.** Nenhum dos 10 sinais é ACT_NOW. Sinal futuro
   sustenta `PREPARE_NOW`, `VALIDATE_BEFORE_WINDOW`, `WATCH_TRIGGER`,
   `MARKET_DEVELOPMENT_VALIDATE`, `COMMERCIAL_PREPARE`, `MARKETING_PREPARE`,
   `SUPPLY_PREPARE`.
3. **Não esconde Desenvolvimento de Mercado dentro de Comercial.** São dois
   departamentos, e em 5 dos 10 sinais a ação de Desenvolvimento de Mercado é a
   única que existe antes da janela.
4. **Não trata previsão como ocorrência.** `ITF-008` e `ITF-010` trazem
   `DERIVED_CLAIM_TIME_STATE = HYPOTHESIS` e contrafator declarado.
5. **Não traduz a citação italiana.** `QUOTE_IT` é evidência.

## 5 · Inteligência negativa é para mostrar

`ITF-008` diz que a demanda de inseticida contra cimice pode **encolher** onde o
Trissolcus se estabelecer. Um radar que só sabe crescer não é um radar. O cartão
deve dizê-lo com a mesma clareza dos que crescem.

## 6 · O que falta para publicar

| bloqueio | dono | o que destrava |
|---|---|---|
| o portal não está nesta branch | quem mantém `claude/meeting-intelligence-integration` | integrar esta fonte lá, não aqui |
| camada de canal inexistente | coleta | 3 ações comerciais dependem dela |
| dívida de leitura dos rótulos-matriz | parser | `ITF-009` depende dela para saber o que a ADAMA autoriza em VITE × TIGNOLE |
| 29 documentos com sinal, não lidos | leitura à mão | fila já ordenada em `IT-ACERVO-CENSO-V1.json` |


## 7 · A matriz dos dez casos

Gerada de `IT-FUTURO-RADAR-V1.json`; nenhum campo foi digitado à mão aqui.

| CASO | O QUE MUDA | ONDE | QUANDO | TRIGGER | CULTURA | ALVO | JANELA | ADAMA | DES.MERCADO | COMERCIAL | MKT | SUPPLY | CONF | ESTADO |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **ITF-001** | A campanha 2026 abre sem estrategia definida contra Eriosoma lanig… | Piemonte | 181_365 | publicacao (ou ausencia) de autorizacao … | MELO | ERIOSOMA_LANIGERUM | 2026-03→2026-06 | no (0) | MARKET_DEVELOPMENT_VALIDATE | WATCH_TRIGGER | WATCH_TRIGGER | WATCH_TRIGGER | MEDIUM | COMPLETE |
| **ITF-002** | Revogacoes recentes deixam a psila do pero sem ferramentas: "nao s… | Piemonte | 181_365 | primeira geracao de psila na retomada ve… | PERO | PSILLE | 2026-02→2026-05 | sì (8) | VALIDATE_BEFORE_WINDOW | COMMERCIAL_PREPARE | MARKETING_PREPARE | SUPPLY_PREPARE | MEDIUM | COMPLETE |
| **ITF-003** | Resistencia multipla a varios mecanismos de acao em Lolium, Papave… | Puglia (Foggia, Bari) | NEXT_SEASON | semeadura de outono-inverno 2026/27 e a … | FRUMENTO | INFESTANTI | 2026-10→2027-02 | sì (5) | MARKET_DEVELOPMENT_VALIDATE | COMMERCIAL_PREPARE | MARKETING_PREPARE | SUPPLY_PREPARE | HIGH | COMPLETE |
| **ITF-004** | Um concorrente registra herbicida novo de cereais com piroxsulam +… | UNKNOWN | NEXT_SEASON | a primeira campanha comercial do produto… | FRUMENTO | INFESTANTI | 2026-11→2027-03 | sì (2) | MARKET_DEVELOPMENT_VALIDATE | WATCH_TRIGGER | WATCH_TRIGGER | WATCH_TRIGGER | MEDIUM | PARTIAL |
| **ITF-005** | Cyperus deixou de ser emergente e esta INSTALADO nos solos arenoso… | Emilia-Romagna (Ferrar | NEXT_SEASON | a semeadura do cereal obrigatorio na rot… | PATATA | INFESTANTI | 2026-10→2026-12 | no (0) | MARKET_DEVELOPMENT_VALIDATE | COMMERCIAL_PREPARE | MARKETING_PREPARE | WATCH_TRIGGER | HIGH | COMPLETE |
| **ITF-006** | A producao integrada do olivo nas Marche esta no teto: em 2025 for… | Marche | 181_365 | pedido de deroga da campanha 2026 ao dis… | OLIVO | MOSCA | 2026-07→2026-09 | ? (0) | MARKET_DEVELOPMENT_VALIDATE | WATCH_TRIGGER | WATCH_TRIGGER | WATCH_TRIGGER | MEDIUM | COMPLETE |
| **ITF-007** | A alternariose da batata consome deroga: em 2024 foi concedida na … | Emilia-Romagna | 181_365 | pedido de deroga da campanha 2026, se ho… | PATATA | ALTERNARIA | 2026-06→2026-08 | no (0) | MARKET_DEVELOPMENT_VALIDATE | WATCH_TRIGGER | WATCH_TRIGGER | WATCH_TRIGGER | HIGH | COMPLETE |
| **ITF-008** | O lancamento do parasitoide Trissolcus japonicus (vespa samurai) c… | Veneto, Friuli, Marche | 181_365 | serie de capturas de 2026 nas armadilhas… | MELO, PERO | CIMICI | non dichiarata | sì (2) | WATCH_TRIGGER | WATCH_TRIGGER | WATCH_TRIGGER | SUPPLY_PREPARE | MEDIUM | PARTIAL |
| **ITF-009** | Lobesia botrana (tignoletta) teve em 2025 um incremento nitido em … | Nord Italia (Barbera e | 181_365 | primeiro voo de adultos em meados de mai… | VITE | TIGNOLE | 2026-05→2026-07 | sì (3) | VALIDATE_BEFORE_WINDOW | COMMERCIAL_PREPARE | MARKETING_PREPARE | SUPPLY_PREPARE | HIGH | COMPLETE |
| **ITF-010** | Os acaros tetraniquideos, sobretudo o ragnetto giallo, sobem de fo… | Nord Italia | 181_365 | monitoramento de sintomas de 2026 confir… | VITE | ACARI | non dichiarata | sì (2) | WATCH_TRIGGER | WATCH_TRIGGER | WATCH_TRIGGER | WATCH_TRIGGER | MEDIUM | PARTIAL |
