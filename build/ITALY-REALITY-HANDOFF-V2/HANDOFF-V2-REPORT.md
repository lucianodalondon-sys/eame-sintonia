# HANDOFF V2 — RELATÓRIO E VEREDICTO

**02/09/2026** · consolidação e portão de verdade · nenhuma coleta nova

---

## VEREDICTO (§23)

```
RAW LAST-MILE SAFE TO SEND DIRECTLY TO DESIGN     = NO
CANONICAL HANDOFF V2 CREATED                      = YES
ALL KNOWN CONFERENCE FAILURES REMOVED OR CORRECTE = YES  (34 de 34 quedas resolvidas)
NENHUM REGISTRO FICOU PENDENTE DE DECISAO         = YES  (0 pendentes)
DUPLICATE RAW/CORRECTED CLAIMS RESOLVED           = YES  (33 crus substituidos e movidos para a quarentena)
UNREVIEWED RECORDS BLOCKED FROM CLIENT ASSERTIONS = YES  (client-safe = so QA_PASS + QA_CORRECTED)
PREVIOUS REALITY HANDOFF PRESERVED                = YES  (3936 objetos em PREVIOUS-HANDOFF/)
NEW LAST-MILE INTELLIGENCE MERGED                 = YES  (10 familias)
SYNTHETIC RECORDS = 0                             = YES  (0)
CONFLICTS RESOLVED                                = YES  (1 conflito(s), 0 pendendo de humano)

READY TO SEND HANDOFF V2 TO CLAUDE DESIGN         = YES
```

✅ O SIM acima é **calculado**, não opinado: se sobrasse um registro pendente ou uma queda sem destino, ele viraria NÃO sozinho.

---

## §21 · MANIFESTO DE VALIDAÇÃO

```
PREVIOUS_HANDOFF_RECORDS_RETAINED                    = 3936
LAST_MILE_RAW_RECORDS                                = 321
LAST_MILE_AFTER_DEDUP                                = 320
RAW_CORRECTED_DUPLICATES_COLLAPSED                   = 1
LAST_MILE_QA_PASS                                    = 65
LAST_MILE_QA_CORRECTED                               = 33
LAST_MILE_QA_UNREVIEWED                              = 221
LAST_MILE_QA_REJECTED                                = 1
CONFLICTS_WITH_PREVIOUS_HANDOFF                      = 1
CONFLICTS_RESOLVED                                   = 1
CLIENT_SAFE_LAST_MILE_RECORDS                        = 98
CLIENT_SAFE_SOURCES                                  = 177
SYNTHETIC_RECORDS_IN_CANONICAL_HANDOFF               = 0
CLIENT_VISIBLE_CLAIMS_DRIVEN_BY_QA_UNREVIEWED        = 0
```

---

## §22 · A TAXA MEDIDA, SEM MAQUIAGEM

| | |
|---|---:|
| amostrados pela conferência | **104** |
| sobreviveram | **70** |
| **caíram** | **34 (32.7%)** |

⚠️ **Uma correção à própria missão.** O briefing cita 52/72 (28%). O número certo é **70/104 (32.7%)**. A diferença é minha: a montagem anterior perdeu a conferência de cinco blocos ao casar nome de família com nome de bloco (`clima` não bate com `METEOROLOGIA`). **A taxa real é pior do que a missão registra.**

> Os 321 são **registros de coleta externa real**. Não são 321 fatos validados de forma independente.

---

## O QUE FOI FEITO COM AS 34 QUEDAS

| destino | quantos |
|---|---:|
| reconstruídos como `QA_CORRECTED` | **33** |
| rejeitados | **1** |

Por causa do defeito:

| causa | quantos |
|---|---:|
| ATRIBUICAO_DE_FALA | 1 |

**Nenhum aviso pendurado.** O §5 proíbe, e o montador recusa: quando há reconstrução, o registro cru sai do feed e vai para `QUARANTINED-RECORDS.json` com a lista campo a campo do que mudou.

### Exemplos do que mudou de verdade

- **BBCH da videira no Vêneto** — a tabela estava deslocada uma linha. O `85-89` era da linha Corvine/Merlot, que o coletor omitiu inteira, e foi dado à Glera. Reconstruído com as quatro linhas. E ficou a ressalva permanente: `pdftotext -layout` é o único modo que produz esse erro — usar `-table`, `-simple` ou `-raw`.
- **Mosca da oliveira no Vêneto** — o registro listava 8 areais a 3–4% e o boletim lista **11**, sendo que o omitido de maior valor era o Litorale veneziano a 4–6%. Cortar o mais alto e chamar o resto de uniforme.
- **Preço do trigo em Verona** — semana errada: `224,50` é de outra semana; na semana correta o valor é `223,50`.
- **Concentração de área** — três porcentagens truncadas em vez de arredondadas, todas na direção de subdeclarar a concentração.

---

## §19 · OS CRUZAMENTOS AGORA POSSÍVEIS

**19 cruzamentos**, cada um com os IDs canônicos exatos dos dois lados:

| cruzamento | quantos |
|---|---:|
| COMPETITOR_SIGNAL × CROP_WINDOW × ADAMA_PORTFOLIO | 3 |
| CURRENT_HERBICIDE_PHASE × VERIFIED_LABEL_USE × RESISTANCE | 3 |
| FIELD_SIGNAL × CROP_ECONOMIC_WEIGHT × VERIFIED_LABEL_USE | 4 |
| MARKET_CONTEXT × REGION_CROP_WEIGHT × CURRENT_FIELD_SIGNAL | 3 |
| PUBLIC_VOICE × CROP_ISSUE × SCIENCE × RESISTANCE | 1 |
| REGULATORY_FUTURE × ACTIVE_INGREDIENT × CATALOG_PRODUCT | 5 |

⚠️ **Um cruzamento não é uma oportunidade.** É a constatação de que duas camadas falam do mesmo par cultura × região. Quem decide se aquilo vale é uma pessoa, olhando os IDs.

E o portão do §4 vale aqui também: só `QA_PASS` e `QA_CORRECTED` entram no lado que **sustenta**. Sem isso o portão vazaria pela porta dos fundos.

---

## §9 · O QUE FOI PRESERVADO

`PREVIOUS-HANDOFF/` traz o pacote anterior **inteiro**: 3936 objetos com ID em `01-DESIGN-READY`, mais a prosa, os manifestos e os índices.

Nada foi reescrito, resumido nem filtrado — nem os 2.030 pares de uso de rótulo, nem as 561 atividades de concorrente, nem as 58 vozes de plateia.

⚠️ **O portão de QA é sobre a camada nova.** Aplicá-lo retroativamente ao pacote anterior rebaixaria trabalho que já tem a sua própria proveniência.

---

## §6 · A DEDUPLICAÇÃO, E POR QUE ELA DEU QUASE NADA

A missão esperava sobreposição entre os dois fluxos, e ela **existe no nível do documento**: 14 URLs foram lidas por mais de um bloco.

Mas ao abrir caso a caso, os registros descrevem **fatos diferentes do mesmo documento**:

- boletim VITE do Vêneto, 27/08 → um é a **fase fenológica**, o outro é a **recomendação de controle** da flavescência
- ISMEA trigo tenro → um é **preço por produto**, o outro **por qualidade**
- ARPAE 24/08 → um é **chuva acumulada**, o outro **água no solo**

> **Dois fatos do mesmo documento não são o mesmo fato.** A duplicata que o §6 teme é a mesma *observação* colhida duas vezes.

Fundir teria perdido metade da informação. **Colapsado: 1** — o boletim ARSAC da semana 35, conferido à mão.

⚠️ E uma nota de método: a busca automática por semelhança de citação devolveu 3 candidatos e **2 eram falso positivo** — o ISMEA repete o cabeçalho da página em recortes diferentes. Um limiar que erra dois em três não é um limiar; é um palpite. A fusão foi **declarada**, não inferida.

---

## §18 · A ROTA NÃO É DEPENDÊNCIA DO PORTAL

Três fontes só abriram por saída italiana — ISMEA Mercati, ISTAT esploradati e ARPAV. Isso está em `SOURCES.json` como **infraestrutura de coleta**, para automação futura.

**O portal consome dado já guardado e nunca precisa da VPN para renderizar.**

---

## O QUE CONTINUA VALENDO COMO LIMITE

| limite | por quê |
|---|---|
| 221 registros são `QA_UNREVIEWED` | não foram à segunda passada. São fonte real e nada mais. |
| a fase de herbicida é da Emília-Romanha | boletim datado de 19–20/08. **Não se generaliza para a Itália.** |
| 21 boletins são provinciais ou de areal | não representam a região. |
| o vínculo comercial dos 6 produtos de outro titular | **desconhecido**, e continua assim. |
| venda, share, estoque | dado interno. O projeto é externo por decisão. |
