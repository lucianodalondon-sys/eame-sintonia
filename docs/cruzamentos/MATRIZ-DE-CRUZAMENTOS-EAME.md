# MATRIZ DE CRUZAMENTOS — SINTONIA EAME

O valor do SINTONIA não está em nenhuma fonte isolada: está no que **duas ou mais fontes
juntas** revelam e nenhuma delas revela sozinha.

> **Não afirmar cruzamento apenas porque semanticamente parece interessante.**
> Clima + doença "parece" cruzar. A pergunta real é: **qual chave os une?**

**Estado:** MISSÃO 02 em curso — **3 COMPROVADOS, 4 PARCIAIS, 3 NÃO COMPÕEM, 1 POSSÍVEL NÃO TESTADO**.
**Última atualização:** 2026-08-28

---

## AS DUAS PERGUNTAS

Para cada cruzamento candidato:

1. **A + B realmente podem ser unidos?**
2. **Qual chave permite uni-los?**

Sem chave explícita e verificada, o cruzamento não é COMPROVADO. As chaves candidatas
costumam ser: geografia (região/NUTS/coordenada), tempo (data/janela), cultura, alvo
(praga/doença), substância ativa, produto, organização, pessoa, identificador de documento.

Atenção ao alinhamento das chaves: duas fontes podem ambas ter "região" e mesmo assim não
cruzar, se uma usa NUTS-2 e a outra departamento, ou se uma é semanal e a outra mensal.
**Granularidade incompatível é motivo legítimo de NÃO COMPÕE.**

---

## CLASSIFICAÇÃO

| Classe | Significado |
|---|---|
| **COMPROVADO** | Cruzamento executado sobre dado real, com chave identificada e exemplo preservado. |
| **POSSÍVEL MAS NÃO TESTADO** | Chave plausível e identificada, mas ninguém executou ainda. |
| **PARCIAL** | Une de fato, mas com cobertura ou granularidade limitada — e o limite está medido, não estimado. |
| **NÃO COMPÕE** | Testado e não une — chave ausente, granularidade incompatível, tempos irreconciliáveis. Exige motivo escrito. |
| **NÃO SEI** | Não foi possível avaliar. |

---

## FICHA DO CRUZAMENTO

```
CROSSING_ID:
COMPONENTS:         # A + B (+ C...)
SOURCES:            # SOURCE_IDs envolvidos
KEY:                # a chave que efetivamente une — ou por que não existe
GRANULARITY_MATCH:  # geografias e tempos são compatíveis?
WHAT_IT_REVEALS:    # o que aparece que nenhuma fonte sozinha mostra
REAL_EXAMPLE:
CAPABILITY:         # que capacidade este cruzamento habilita
CLASS:              # COMPROVADO | POSSÍVEL MAS NÃO TESTADO | NÃO COMPÕE | NÃO SEI
```

---

## CRUZAMENTOS CANDIDATOS (do briefing)

Listados como **candidatos a testar**, não como afirmações. Todos partem em `NÃO SEI`.

| ID | Cruzamento | Classe |
|---|---|---|
| X-001 | CLIMATE + REGION + CROP + DISEASE ALERT | **PARCIAL** (falta DISEASE ALERT) |
| X-002 | RESEARCHER + PAPER + CROP + PROBLEM | **COMPROVADO** |
| X-003 | COMPETITOR + PRODUCT + CROP + COMMUNICATION | **NÃO COMPÕE** (camada COMMUNICATION inacessível) |
| X-004 | REGULATORY + ADAMA PORTFOLIO + CROP + PEST | **COMPROVADO (FR)** |

> X-004 **foi resolvido para a França** sem dado interno: o registro oficial francês nomeia
> ADAMA FRANCE SAS como titular. Ver o registro abaixo. A camada de portfólio **comercial**
> continua fora de alcance.

---

## REGISTRO DE CRUZAMENTOS TESTADOS

### X-004 · REGULATORY + ADAMA PORTFOLIO + CROP + PEST — **COMPROVADO (França)**

```
CROSSING_ID:        X-004
COMPONENTS:         REGULATORY (autorização nacional) + PORTFOLIO (titular) + CROP + PEST
SOURCES:            FR-T4-001 (ANSES E-Phy)
KEY:                numero AMM (produto) → identifiant usage, decomposto em
                    Cultura * TipoTratamento * Alvo. O titular vem do mesmo registro.
                    Chave interna à fonte: o cruzamento acontece dentro do registro oficial.
GRANULARITY_MATCH:  SIM — todos os componentes vivem na mesma granularidade (país, produto,
                    uso). Não há descompasso geográfico nem temporal a reconciliar.
WHAT_IT_REVEALS:    Que a ADAMA pode legalmente atuar em 504 usos autorizados na França e
                    exatamente em quais pares cultura × alvo — e onde cada concorrente está.
REAL_EXAMPLE:       ADAMA FRANCE SAS: Vigne×Mildiou 17 usos, Vigne×Black rot 13,
                    Traitements généraux×Limaces 18, Blé×Septoriose 6.
                    Evidência: data/samples/FR-T4-001/FR-T4-001-adama-crop-target.json
CAPABILITY:         CAP-003, CAP-004, CAP-005
CLASS:              COMPROVADO
```

**As oito perguntas (§7):**
A · sujeito de A: o **produto autorizado** (nº AMM).
B · sujeito de B: o **uso autorizado** (cultura × alvo).
C · chave: nº AMM, ligação nativa dentro do registro.
D · granularidade: compatível — ambos nacionais e por produto.
E · período: compatível — mesma versão semanal do dataset.
F · **afirma fato**, não correlação: é o texto do ato administrativo, não inferência.
G · pergunta que passa a ser respondida: *"o que a ADAMA — ou o concorrente X — pode
legalmente vender na França, em que cultura e contra que alvo?"*
H · erro fácil de cometer: ler **presença regulatória** como **posição de mercado**.
Ver o RED TEAM em CAP-005.

**Ressalva sobre a camada PORTFOLIO:** o que foi cruzado é o portfólio **registrado**
(público). O portfólio **comercial** da ADAMA EAME (vendas, prioridade, pipeline)
permanece `NÃO TESTÁVEL COMPLETAMENTE` — não é público e não foi fornecido. Não foi inventado.

### X-005 · COMPETITOR + CROP + PEST via registro oficial — **COMPROVADO (França)**

```
CROSSING_ID:        X-005
COMPONENTS:         COMPETITOR (titular) + CROP + PEST + ACTIVE INGREDIENT
SOURCES:            FR-T4-001
KEY:                titulaire → nº AMM → identifiant usage; substância ativa no mesmo registro
GRANULARITY_MATCH:  SIM
WHAT_IT_REVEALS:    Um radar competitivo apoiado em ato administrativo, não em clipping:
                    quem tem direito de uso em cada combate agronômico, com que molécula.
REAL_EXAMPLE:       Vigne × Mildiou(s) — ADAMA 17, NUFARM 11, BAYER 8, UPL 7, SYNGENTA 5,
                    CORTEVA/DOW 3, BASF 2 (usos autorizados).
CAPABILITY:         CAP-005
CLASS:              COMPROVADO (para "usos autorizados"; NÃO para participação de mercado)
```

**Limite duro:** este cruzamento mede **direito de uso registrado**. Ele **não compõe** com
market share, faturamento ou adoção — essas variáveis não estão na fonte. Ver §8 da missão:
correlação não vira causalidade, e presença regulatória não vira liderança.

### X-006 · EU ACTIVE SUBSTANCE + NATIONAL PRODUCT AUTHORIZATION — **PARCIAL (testado, com limite medido)**

```
CROSSING_ID:        X-006
COMPONENTS:         EU-T4-001 (ato da UE por substância) + FR-T4-001 (produto nacional)
KEY CANDIDATA:      nome da substância ativa e/ou nº CAS.
                    E-Phy traz `substance_active_utf8.csv` com "Numero CAS" (1.337 linhas);
                    o ato da UE traz CAS no anexo (ex.: ácido pelargônico, CAS 112-05-0).
                    O CAS é, portanto, chave candidata forte — mas o CAS no ato da UE está
                    em texto corrido do anexo, não em campo estruturado.
GRANULARITY_MATCH:  ATENÇÃO — descompasso de sujeito: a UE regula SUBSTÂNCIA (nível UE);
                    a França autoriza PRODUTO (nível nacional). A relação é 1:N e a
                    expiração europeia não é a data de retirada do produto francês.
WHAT_IT_WOULD_REVEAL: quais produtos autorizados na França dependem de uma substância cuja
                    aprovação europeia expira em data conhecida — antecipação de perda.
CLASS:              PARCIAL
REAL_EXAMPLE:       CELEX 32026R1353 (15/06/2026) → CAS 70630-17-0 → E-Phy "Metalaxyl-M"
                    (INSCRITE) → 9 produtos autorizados na França → destes, 1 é da ADAMA:
                    PANDERO GOLD, AMM 2010398 (folpel 400 g/kg + metalaxil-M),
                    uso Vigne*Trt Part.Aer.*Mildiou(s), 2,0 kg/ha, autorizado.
                    Evidência: data/samples/X-006-eu-cas-to-ephy.json
```

**TESTADO — o que funcionou.** A cadeia completa fecha, ponta a ponta e de forma automática:

```
ato da UE (CELEX) → CAS → substância no E-Phy → produtos franceses → titular → cultura × alvo
```

**Por que PARCIAL e não COMPROVADO — os limites medidos, não estimados:**

| Medida | Resultado | Consequência |
|---|---|---|
| Atos da UE com CAS extraível do texto | **3 de 6** | Atos que só alteram o Reg. 540/2011 (prorrogação de período) citam a substância **pelo nome**, sem CAS no corpo. Para esses, a chave CAS não existe. |
| Casamento CAS → E-Phy, quando havia CAS | **3 de 4** | O CAS que falhou (67701-09-1) é de uma fração de ácidos graxos, não da substância principal do ato. |
| Substâncias do E-Phy que trazem nº CAS | **621 de 1.338** | Menos da metade. Para o resto, o casamento teria de ser por nome — e nome varia entre línguas e grafias. |

**Conclusão honesta:** a chave CAS é **real e funciona**, mas cobre apenas parte do universo.
Um cruzamento de produção precisaria de uma segunda chave (nome normalizado da substância)
e de medição da taxa de acerto dessa segunda chave. Enquanto isso não for feito, qualquer
número derivado deste cruzamento é **incompleto por construção** e assim deve aparecer.

**As oito perguntas (§7):**
A · sujeito de A: a **substância ativa**, no nível da União.
B · sujeito de B: o **produto comercial**, no nível nacional.
C · chave: **nº CAS** (verificada, cobertura parcial medida acima).
D · granularidade: **incompatível por natureza** — 1 substância : N produtos. O cruzamento
só é legítimo na direção substância → produtos, nunca produto → "situação europeia".
E · período: compatível, mas as datas **não** são a mesma coisa (ver H).
F · **afirma fato** (ambos são atos administrativos), com cobertura parcial.
G · pergunta respondida: *"que produtos autorizados na França — e de quem — dependem desta
substância cuja aprovação europeia tem data conhecida?"*
H · **erro fácil de cometer:** tratar a **data de expiração da aprovação europeia** como
**data de retirada do produto francês**. Não são a mesma data. A expiração europeia abre um
processo de renovação; a retirada nacional tem prazo próprio, com escoamento de estoque.
Confundir as duas produziria um alarme falso com data errada.



### X-007 · FRANCE cultura × alvo + SPAIN vocabulário EPPO — **PARCIAL**

```
CROSSING_ID:        X-007
COMPONENTS:         FR-T4-001 (uso autorizado: cultura × alvo em francês)
                    + ES-T4-001 (EPPO + nome científico)
KEY CANDIDATA:      código EPPO / nome científico
GRANULARITY_MATCH:  **NÃO, no vocabulário.** Ver abaixo.
CLASS:              PARCIAL
```

**O que foi verificado.** O lado espanhol está pronto: 492 culturas e 1.381 pragas com
código EPPO e nome científico. Os alvos que a França mais registra têm correspondência
exata no lado espanhol:

| França (nome comum) | EPPO | Espanha / nome científico |
|---|---|---|
| Vigne × Mildiou(s) | VITVI × PLASVI | Mildiu de la vid — *Plasmopara viticola* |
| Blé × Septoriose(s) | TRZAX × SEPTTR | Septoriosis del trigo — *Zymoseptoria tritici* |
| Vigne × Black rot | VITVI × GUIGBI | Black rot — *Phyllosticta ampelicida* |
| Vigne × Oïdium | VITVI × UNCINE | Oídio de la vid — *Erysiphe necator* |

**Por que PARCIAL e não COMPROVADO — o obstáculo é real e foi medido.**
O E-Phy francês **não tem código EPPO nem nome científico**: verificado, nenhum dos 10
arquivos do pacote traz esses campos. O lado francês só oferece **231 nomes comuns em
francês** — e boa parte deles é **grupo, não espécie**: `Mildiou(s)`, `Oïdium(s)`,
`Rouille(s)`, `Champignons (pythiacées)`, `Chenilles phytophages`. `Mildiou(s)` em videira é
*Plasmopara viticola*, mas `Mildiou(s)` em batata é *Phytophthora infestans*.

Logo o mapeamento **não é 1:1**, é **muitos-para-muitos e dependente da cultura**. Ele só se
resolve com a dupla (cultura, alvo), nunca com o alvo sozinho.

**O que falta:** construir e **medir** um dicionário FR(cultura,alvo) → EPPO. Só depois de
medida a taxa de acerto este cruzamento pode subir para COMPROVADO. Enquanto isso, qualquer
comparação França × Espanha × Itália por praga é **incompleta por construção**.

**As oito perguntas (§7) — os pontos que decidem:**
D · granularidade: **incompatível** (grupo francês × espécie espanhola).
F · afirma **fato** de vocabulário, não correlação.
H · erro fácil: somar "usos contra míldio" da França com "autorizações contra *Plasmopara
viticola*" da Espanha como se fossem a mesma contagem. **Não são.**

### X-008 · Comparação T4 entre FRANCE, SPAIN e ITALY — **NÃO COMPÕE (hoje)**

```
CROSSING_ID:        X-008
COMPONENTS:         FR-T4-001 + IT-T4-001 + ES-T4-003
KEY:                não existe chave comum utilizável hoje
CLASS:              NÃO COMPÕE
```

**Motivo, medido e não estimado:** as três fontes nacionais **não cobrem os mesmos campos**.

| | produto | titular | cultura × alvo | vencimento | EPPO |
|---|---|---|---|---|---|
| FRANCE | ✅ | ✅ | ✅ | ❌ | ❌ |
| ITALY | ✅ | ✅ | ❌ | ✅ | ❌ |
| SPAIN | ❌ | — | ❌ | ❌ | ✅ (só vocabulário) |

Uma pergunta como *"em que países a ADAMA tem registro contra míldio da videira?"* **não pode
ser respondida hoje**: a Itália não publica cultura × alvo e a Espanha não publica o registro
de produtos em formato aberto. Qualquer tela que insinue uma comparação dos três países em
T4 estaria mostrando uma equivalência que não existe.

**O que destravaria:** (a) a etichetta italiana em formato processável; (b) um dump aberto do
registro espanhol, ou autorização de uso da consulta do MAPA (ES-T4-003, hoje `NÃO SEI /
REQUER REVISÃO`); (c) o dicionário FR→EPPO de X-007.


### X-001 · CLIMATE + REGION + CROP (+ DISEASE ALERT) — **PARCIAL**

```
CROSSING_ID:        X-001
COMPONENTS:         CLIMATE (EU-T2-001) + REGION (EU-T2-002 / NUTS2) + CROP (EU-T1-001)
                    + DISEASE ALERT (**ausente — T3 ainda não investigado**)
SOURCES:            EU-T1-001, EU-T1-002, EU-T2-001, EU-T2-002
KEY:                **código NUTS 2** — presente nativamente no Eurostat e no GISCO;
                    o clima é anexado à região pelo ponto-rótulo GISCO daquele NUTS 2.
                    Segunda chave: **ano**, comum às duas fontes.
GRANULARITY_MATCH:  PARCIAL. Área e região casam em NUTS 2. O clima é de **um ponto**
                    dentro da região, não uma média regional. O rendimento não existe
                    em NUTS 2 — só por país.
WHAT_IT_REVEALS:    quanta área de uma cultura está numa região e que exposição climática
                    essa região teve na janela sensível daquela cultura, ano a ano.
REAL_EXAMPLE:       Trigo comum, janela 01/05–30/06, dias com Tmáx ≥ 30 °C:
                    ES41 (771,8 mil ha) — 11 (2022) → 6 (2023) → 4 (2024)
                    FRB0 (544,6 mil ha) — 5 → 3 → 0, com chuva 118 → 103 → **231 mm**
                    FRI3 (283,7 mil ha) — 13 → 3 → 0
                    Evidência: data/samples/X-001-nuts2-heat-vs-wheat.json
CAPABILITY:         CAP-010, CAP-012, CAP-013
CLASS:              PARCIAL
```

**As oito perguntas (§7):**
A · sujeito de A: a **região NUTS 2 num ano**, com sua área de cultura.
B · sujeito de B: a **série climática diária** de um ponto dessa região.
C · chave: **código NUTS 2 + ano**. Real, nativa nas duas fontes, sem heurística.
D · granularidade: **parcialmente compatível** — a região é a mesma, mas o clima é pontual
e o rendimento é nacional. Este é o ponto fraco do cruzamento, e é estrutural.
E · período: compatível — ambos anuais, 2000–2024 do lado da área.
F · **afirma exposição, não impacto.** O cruzamento diz *"esta região, que tem tanta área de
trigo, teve tantos dias de calor na janela de enchimento"*. Não diz o que isso causou.
G · pergunta respondida: *"onde está a cultura e a que clima ela esteve exposta, por ano?"*
H · **erro fácil de cometer:** ler a coincidência como causa — e, pior, escolher a janela
que confirma a narrativa. Ver CAP-013: em Castilla y León, a janela de enchimento de grão
sugere que 2023 foi **menos** seco que 2022, quando a seca real de 2023 estava em
fevereiro–abril e o rendimento nacional foi o pior da série.

**Por que PARCIAL e não COMPROVADO:** falta o quarto componente do cruzamento original —
**DISEASE ALERT** — porque T3 ainda não foi investigado. E o clima é aproximação por ponto.
Os três componentes existentes compõem de fato, com chave real e sem inferência.


### X-009 · CLIMATE → DISEASE (o clima explica onde a doença apareceu?) — **NÃO COMPÕE**

```
CROSSING_ID:        X-009
COMPONENTS:         CLIMATE (EU-T2-001) → DISEASE INCIDENCE (ES-T3-001)
SOURCES:            NASA POWER (ponto por província) + RAIF Andalucía (parcela)
KEY:                província + safra 2026
CLASS:              **NÃO COMPÕE** — para a pergunta causal. Ver abaixo.
```

**O teste.** Míldio da videira (PLASVI) na Andaluzia, safra 2026. Clima acumulado na janela
15/03–31/05, medido no ponto representativo de cada província:

| Província | chuva | dias com ≥1 mm | UR média | **míldio (pico medido)** |
|---|---|---|---|---|
| **Huelva** | 55,4 mm | 12 | 66,6% | **26,4%** |
| **Córdoba** | 65,1 mm | 12 | 66,1% | **6,4%** |
| **Cádiz** | 48,9 mm | 8 | **74,2%** | **≈0%** |

**O resultado derruba a intuição.** Córdoba teve **mais chuva** que Huelva e **quatro vezes
menos** doença. Cádiz teve a **maior umidade média das três** e praticamente **nenhuma**
doença. A ordenação climática **não reproduz** a ordenação epidemiológica em nenhuma das
três variáveis testadas.

**Por que isto é NÃO COMPÕE e não "resultado ruim":** o cruzamento **une** tecnicamente —
a chave província + safra funciona, os dois lados existem e são datados. O que **não se
sustenta** é a **inferência** que todo mundo quer fazer em cima dele. Registrado como
NÃO COMPÕE **para a pergunta causal**; a mesma composição continua válida para
**descrever exposição e incidência lado a lado**, desde que a tela não sugira causa.

**O que poderia explicar a diferença — e que nós não medimos:**
variedade e sensibilidade do material; manejo de canópia; **programa de fungicida aplicado**
(a RAIF registra tratamentos, e nós não os cruzamos); microclima real da parcela contra o
ponto único da província; irrigação; histórico de inóculo. Nenhuma dessas hipóteses foi
testada. Listá-las é obrigação; escolher uma sem dado seria fabricar inteligência.

**As oito perguntas (§7):**
F · **não afirma fato nem correlação útil.** Com três províncias, não há sequer amostra para
falar em correlação.
H · **erro fácil — e é o erro mais provável de toda a missão:** montar a tela "chuva ×
doença" e deixar o observador concluir que a chuva causou o surto. A §8 da missão proíbe
exatamente isso, e agora temos o dado que mostra por quê.

### X-001 · atualização — o quarto componente entrou

O componente **DISEASE ALERT**, que faltava em X-001, existe e foi obtido (ES-T3-001).
A composição `CLIMATE + REGION + CROP + DISEASE` agora é **executável** para a Andaluzia:
os quatro lados são reais, datados e ligáveis por província e safra.

X-001 permanece **PARCIAL**, por três motivos medidos e não estimados:
1. o quarto componente só existe para **uma região de um país** (Andaluzia), não para FR/IT;
2. o clima continua sendo **um ponto**, não média regional;
3. e, principalmente, **X-009**: os quatro lados compõem, mas a leitura causal que
   justificaria a ferramenta **não se sustenta nos dados**.


### X-002 · RESEARCHER + PAPER + CROP + PROBLEM — **COMPROVADO (com vocabulário controlado)**

```
CROSSING_ID:        X-002
COMPONENTS:         pesquisador + trabalho + cultura + problema (+ instituição, + país)
SOURCES:            EU-T5-001 (OpenAlex)
KEY:                identificador de autor do OpenAlex, ligando trabalhos ao mesmo nome;
                    o problema entra pela consulta; o país pela afiliação.
GRANULARITY_MATCH:  SIM dentro da fonte — autor, trabalho, instituição e ano são nativos.
WHAT_IT_REVEALS:    quem sustenta um tema ao longo do tempo, e em que instituição —
                    em vez de quem publicou uma vez.
REAL_EXAMPLE:       Itália × videira × míldio: Toffolatti (17, Milano),
                    Perazzolli (12, Edmund Mach), Maddalena (11), Rossi (10, Cattolica).
                    França × resistência a herbicidas: Délye (9) e mais três do mesmo
                    laboratório INRAE Agroécologie.
CAPABILITY:         CAP-017, CAP-018
CLASS:              **COMPROVADO** — condicionado a vocabulário controlado (ver X-010)
```

**As oito perguntas — os pontos que decidem:**
D · granularidade compatível; tudo vive na mesma fonte.
F · **afirma fato** (autoria e afiliação), **não** autoridade. Publicar muito não é ser a
autoridade principal — a §8 da missão proíbe essa conversão, e ela não foi feita.
H · erro fácil: usar consulta larga e obter a rede errada. Medido em CAP-018.

### X-010 · Vocabulário controlado como pré-requisito do people graph — **PARCIAL**

```
CROSSING_ID:        X-010
COMPONENTS:         EPPO/nome científico (ES-T4-001) + consulta científica (EU-T5-001)
KEY:                nome científico do patógeno ou da cultura
CLASS:              PARCIAL
```

**O que funciona:** o dicionário EPPO da Espanha entrega o nome científico exato
(PLASVI = *Plasmopara viticola*, SEPTTR = *Zymoseptoria tritici*), e usar esse nome como
consulta no OpenAlex produz a rede de especialistas correta — comprovado em CAP-018.

**O que falta:** o elo entre o nome comum usado nas fontes de campo e o nome científico.
A RAIF já traz o científico junto (`"Mildiu... Plasmopara viticola"`), mas o E-Phy francês
**não** (X-007). Enquanto isso, um alerta de campo francês não se conecta automaticamente
à literatura sobre o mesmo patógeno.

**Cadeia que já fecha hoje, ponta a ponta, com vocabulário:**
`praga na Andaluzia (RAIF) → nome científico → EPPO → literatura e pesquisadores (OpenAlex)`.
**Cadeia que ainda não fecha:** a mesma partindo da França.


### X-003 · COMPETITOR + PRODUCT + CROP + COMMUNICATION — **NÃO COMPÕE (hoje)**

```
CROSSING_ID:        X-003
COMPONENTS:         concorrente + produto + cultura + **comunicação**
SOURCES:            FR-T4-001 (as três primeiras pernas, provadas em X-005)
                    + camada de comunicação: **inexistente**
CLASS:              NÃO COMPÕE
```

**Motivo medido:** a perna COMMUNICATION não foi obtida. `syngenta.fr` devolveu **403**,
`agriculture.basf.fr` **502**, `corteva.it` **404**. Vencer essa barreira exigiria varredura
de sites com proteção anti-robô — proibida pela §16 desta missão.

**Mas o cruzamento tem um substituto provado.** As três outras pernas — concorrente, produto
e cultura × alvo — compõem perfeitamente pelo **registro oficial** (X-005, COMPROVADO).
A pergunta *"em que problemas agronômicos o concorrente está presente?"* já tem resposta
defensável. A que continua sem resposta é *"sobre o que ele está falando"*.

**Leitura estratégica:** presença regulatória é **fato administrativo**, verificável e
datado. Comunicação é **intenção**, e mesmo obtida seria matéria mais frágil. A missão
pediu para não fazer clipping genérico; o dado disponível empurra exatamente para lá.


### X-011 · EVENT + COMPETITOR + RESEARCHER — **POSSÍVEL NÃO TESTADO**

```
CROSSING_ID:        X-011
COMPONENTS:         evento (catálogo de expositores e programa) + concorrente + pesquisador
SOURCES:            IT-T11-001 (EIMA) + FR-T4-001/IT-T4-001 (titulares) + EU-T5-001 (autores)
KEY CANDIDATA:      nome da empresa (expositor × titular de registro) e
                    nome da pessoa (palestrante × autor)
CLASS:              POSSÍVEL NÃO TESTADO
```

**Por que é plausível:** a EIMA 2026 (10–14/11/2026, Bologna) publica catálogo de expositores;
o registro italiano publica os titulares de autorização; o OpenAlex publica os autores. Os três
usam nomes próprios como chave.

**Por que não foi testado:** casar **nome de empresa** entre um catálogo de feira e um registro
oficial é notoriamente sujo — "ADAMA ITALIA S.R.L." no registro pode ser "Adama" no catálogo.
A taxa de acerto teria de ser medida antes de qualquer afirmação, e o catálogo não foi baixado.

**Prioridade:** baixa. T11 é a família mais pobre em formato e a de menor valor relativo
entre as investigadas.


### Placar

| Classe | Quantidade |
|---|---|
| COMPROVADO | 3 |
| PARCIAL | 4 |
| POSSÍVEL MAS NÃO TESTADO | 1 |
| NÃO COMPÕE | 3 |
| NÃO SEI | 0 |
