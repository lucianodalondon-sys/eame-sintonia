# CONTRATO DE MATÉRIA-PRIMA DA INTELLIGENCE AGRÍCOLA — V1

```
MISSAO     C-INT-AGRO-BENCH-01
ESPECIE    REQUISITOS DERIVADOS DE BENCHMARK — NAO IMPLEMENTA NADA
MEDIDO_EM  2026-09-13
```

> **Este documento não desenha a Collection.** Ele diz **que informação tem de
> existir e sobreviver** para cada capacidade de Intelligence ser defensável, e
> **o que acontece quando falta**. Como persistir é decisão do dono da
> Collection, e não é tomada aqui (`§30` do enunciado).

Legenda de `WHAT_HAPPENS_IF_MISSING`:

```
BLOQUEIA      a capacidade nao pode ser produzida. A resposta certa e NAO_SEI.
DEGRADA       produz-se um nivel mais fraco, e o nivel tem de ser dito.
FALSIFICA     produz-se algo que PARECE a capacidade e nao e — o pior estado.
```

---

## 1 · DISEASE / PEST INTELLIGENCE

```
QUESTION
  Este problema esta a acontecer, nesta cultura, neste lugar, agora — e o que
  isso implica?

MINIMUM_ENTITIES
  PEST/DISEASE (EPPO) · CROP (EPPO) · AREA · OBSERVATION · SOURCE

MINIMUM_FACTS
  a ESPECIE da evidencia (observado / favoravel / modelado / confirmado)
  o VALOR, com UNIDADE e ESCALA
  o METODO de observacao e, quando houver, o metodo de DIAGNOSTICO
  o DENOMINADOR quando o valor for proporcao

JOIN_KEYS
  (EPPO_PEST, EPPO_CROP, AREA, TEMPO)   — e as quatro sao obrigatorias

TIME_REQUIREMENTS
  FACT_TIME real (nao PUBLISHED_AT) · e, quando a cultura importa, BBCH
  observado. Uma data de calendario sozinha DEGRADA.

GEO_REQUIREMENTS
  FACT_LOCATION com precisao declarada, na escada administrativa.
  SOURCE_LOCATION nunca promove.

METHOD_REQUIREMENTS
  OBRIGATORIO. Sem metodo, «12,5 %» nao e comparavel com «12,5 %».

PROVENANCE_REQUIREMENTS
  source_id · artefato · run · sha256 · linhagem ate ao RAW

VERSION_REQUIREMENTS
  versao da regra de normalizacao do par (praga, cultura)

DENOMINATOR_REQUIREMENTS
  OBRIGATORIO para prevalencia e para QUALQUER afirmacao de ausencia.
  A EFSA exige populacao-alvo, unidade de inspecao, design prevalence e
  sensibilidade do metodo. Nenhuma fonte publica EAME conhecida os declara.

INDEPENDENCE_REQUIREMENTS
  dois boletins da mesma ONPF regional NAO sao duas fontes independentes.

PRIVATE_DATA_REQUIRED?
  NAO para nivel 1-2. SIM para nivel 3-4 (ver DISEASE-INTELLIGENCE-LEVELS-V1).

WHAT_HAPPENS_IF_MISSING
  metodo/unidade ausentes ............ DEGRADA a «sinal relatado»
  denominador ausente ................ BLOQUEIA prevalencia e ausencia
  FACT_TIME ausente .................. BLOQUEIA acionabilidade (janela)
  especie de evidencia ausente ....... FALSIFICA — clima vira doenca
```

---

## 2 · SCIENTIFIC INTELLIGENCE

```
QUESTION
  A ciencia diz alguma coisa sobre esta cultura/problema que mude o que
  fazemos — e quantas evidencias INDEPENDENTES ha?

MINIMUM_ENTITIES
  STUDY · PUBLICATION · TRIAL · TREATMENT · CONTROL · OBSERVED_VARIABLE ·
  GROUP/AFFILIATION · LOCATION · SEASON

MINIMUM_FACTS
  desenho experimental · repeticao · tratamento vs controlo ·
  variavel (trait x method x scale) com unidade · resultado · local · ano

JOIN_KEYS
  DOI (publicacao) · trial/investigation id (ensaio) · ORCID/afiliacao (grupo)
  ⚠️ SAO TRES CHAVES DIFERENTES, e e a diferenca entre elas que mede
  independencia.

TIME_REQUIREMENTS
  ANO/CAMPANHA do ensaio ≠ ano de publicacao. Um ensaio de 2019 publicado em
  2026 e um facto de 2019.

GEO_REQUIREMENTS
  local do ENSAIO ≠ afiliacao do autor (`INT-LAW-102`)

METHOD_REQUIREMENTS
  OBRIGATORIO (MIAPPE/Crop Ontology). Sem metodo, dois resultados nao sao
  comparaveis nem contraditorios: sao incomensuraveis.

PROVENANCE_REQUIREMENTS
  DOI + o documento. `COL-LAW-218`: preprint, publicado e corrigido podem ser
  o mesmo trabalho canonico sem serem o mesmo artefato.

INDEPENDENCE_REQUIREMENTS
  O NUCLEO DESTA CAPACIDADE. Tres papers NAO sao tres evidencias se
  partilharem ensaio, dataset, grupo ou se um citar o outro.
  GRAFO DE DEPENDENCIA ANTES DA CONVERGENCIA.

PRIVATE_DATA_REQUIRED?
  NAO — mas o texto integral atras de paywall e um limite real.

WHAT_HAPPENS_IF_MISSING
  metodo/escala ausentes ............. BLOQUEIA comparacao
  ensaio nao identificavel ........... FALSIFICA independencia (o erro caro)
  ano do ensaio ausente .............. DEGRADA
```

---

## 3 · REGULATORY INTELLIGENCE

```
QUESTION
  O que mudou, ou vai mudar, na autorizacao — e a quem isso afeta?

MINIMUM_ENTITIES
  ACTIVE_SUBSTANCE · PRODUCT · REGISTRATION · HOLDER · LEGAL_ACT · COUNTRY

MINIMUM_FACTS
  estado de aprovacao + data + regulamento que o estabelece
  estado administrativo do produto + data do decreto + caducidade
  o ATO OFICIAL (documento), nao so a linha na base

JOIN_KEYS
  (pais, registration_id) · nome ISO da substancia (+ CAS)

TIME_REQUIREMENTS
  VALID_FROM / VALID_TO explicitos · periodo de escoamento quando existir.
  Esta e a capacidade onde o TEMPO FUTURO e o produto.

GEO_REQUIREMENTS
  PAIS. A autorizacao e nacional; a aprovacao da substancia e da UE.
  PAIS != ZONA != UE, e nenhuma promove a outra.

METHOD_REQUIREMENTS
  n/a

PROVENANCE_REQUIREMENTS
  OBRIGATORIO E REFORCADO. A EU Pesticides Database declara «no legal value».
  A proveniencia tem de chegar ao ATO.

VERSION_REQUIREMENTS
  OBRIGATORIO: `fonte_versao` ja e chave em `registro_regulatorio`
  (`UNIQUE (pais, registration_id, fonte_versao)`) — e isso esta certo.

DENOMINATOR_REQUIREMENTS
  Para dizer «N produtos afetados», e preciso o universo: que base, que data,
  que filtro. `INT-LAW-111`.

INDEPENDENCE_REQUIREMENTS
  n/a — ha uma autoridade, e ela nao precisa de corroboracao.

PRIVATE_DATA_REQUIRED?
  NAO.

WHAT_HAPPENS_IF_MISSING
  ato oficial ausente ................ DEGRADA a «a base diz»
  versao da fonte ausente ............ BLOQUEIA deteccao de mudanca
  universo nao declarado ............. FALSIFICA contagens
```

---

## 4 · LABEL INTELLIGENCE

```
QUESTION
  Este produto pode ser usado nesta cultura, contra este alvo, nesta dose,
  neste estadio, com esta restricao?

MINIMUM_ENTITIES
  PPP_USE (a tupla de SEIS da EPPO PP 1/248) · PRODUCT · REGISTRATION · LABEL

MINIMUM_FACTS
  CROP/CROP_GROUP · TREATED_OBJECT · TARGET · CROP_DESTINATION ·
  LOCATION_OF_USE · TREATMENT
  + dose · n.º de aplicacoes · intervalo · estadio (BBCH) · PHI · restricoes

JOIN_KEYS
  (registration_id, versao_do_rotulo, indice_do_uso)
  ⚠️ O USO PRECISA DE IDENTIDADE PROPRIA. Sem ela nao se consegue dizer «este
  uso mudou» — so «o rotulo mudou».

TIME_REQUIREMENTS
  versao do rotulo, com data. A base italiana mostra «a ultima etichetta
  autorizzata»: a anterior desaparece da vista, e perde-se se nao for guardada.

GEO_REQUIREMENTS
  PAIS

METHOD_REQUIREMENTS
  n/a — mas TREATMENT (o metodo de aplicacao) faz parte da identidade do uso

PROVENANCE_REQUIREMENTS
  o PDF do rotulo, com sha256

DENOMINATOR_REQUIREMENTS
  Para «cobertura de portfolio», o denominador e o conjunto de usos
  AUTORIZADOS naquele pais para aquele par — e ele e conhecivel.

PRIVATE_DATA_REQUIRED?
  NAO.

WHAT_HAPPENS_IF_MISSING
  guardar so (produto, cultura) ....... FALSIFICA — perde destino, local,
                                        objecto e tratamento, e responde «sim»
                                        a perguntas que o rotulo nao autoriza
  estadio/PHI ausentes ................ BLOQUEIA recomendacao
  versoes anteriores nao guardadas .... BLOQUEIA historico regulatorio
```

---

## 5 · PORTFOLIO INTELLIGENCE

```
QUESTION
  O que a ADAMA tem, para que serve, e onde ha buraco?

MINIMUM_ENTITIES
  REGISTERED_PORTFOLIO · COMMERCIAL_PORTFOLIO · AGRONOMIC_RESPONSE · PIPELINE

⚠️ SAO QUATRO COISAS, E SO A PRIMEIRA E PUBLICA.

  REGISTERED_PORTFOLIO   publico    o que esta autorizado
  COMMERCIAL_PORTFOLIO   INTERNO    o que esta a venda, com preco e stock
  AGRONOMIC_RESPONSE     MISTO      o que funciona, e quanto — exige ensaio
  PIPELINE               INTERNO    o que vem

JOIN_KEYS
  (pais, registration_id) -> PPP_USE -> (EPPO_CROP, EPPO_TARGET)

DENOMINATOR_REQUIREMENTS
  «buraco de portfolio» e uma afirmacao de AUSENCIA. Exige o universo dos usos
  autorizados naquele pais — que e conhecivel — e a declaracao do filtro.

PRIVATE_DATA_REQUIRED?
  SIM, para tudo o que nao seja o registado.

WHAT_HAPPENS_IF_MISSING
  inferir comercial do registado ...... FALSIFICA. Um registo caducado pode
                                        continuar a vender-se no periodo de
                                        escoamento; um registo activo pode
                                        nunca ter sido comercializado nesse pais
```

---

## 6 · COMPETITOR INTELLIGENCE

```
QUESTION
  O que o concorrente esta a fazer que muda o que devemos fazer?

MINIMUM_ENTITIES
  COMPANY · PRODUCT · REGISTRATION · COMMUNICATION · EVENT

MINIMUM_FACTS
  a ESPECIE do facto: registo (autoridade) vs comunicacao (company claim)
  ⚠️ O contrato da fonte IT-T9-008 ja escreve a lei:
     «COMPANY_CLAIM != REGULATORY_FACT — vale inclusive para a ADAMA»

JOIN_KEYS
  holder/titular -> registration -> produto -> (cultura, alvo)

IDENTITY
  O PONTO FRACO. A `COL-LAW-034` ja tem a cicatriz medida: tres funcionarios de
  FMC, UPL e BASF foram contados como o canal da empresa porque o headline
  deles nomeia o empregador.
  NOME DE EMPRESA NAO E IDENTIDADE DE EMPRESA.

PRIVATE_DATA_REQUIRED?
  NAO para registo e comunicacao. SIM para quota, preco e canal.

WHAT_HAPPENS_IF_MISSING
  identidade por semelhanca textual ... FALSIFICA
  anuncio tratado como facto ......... FALSIFICA
```

---

## 7 · MARKET INTELLIGENCE

```
QUESTION
  Uma variacao de preco/producao/area/comercio muda alguma decisao nossa?

MINIMUM_ENTITIES
  COMMODITY · GEOGRAPHY · PERIOD · SERIES · VALUE

MINIMUM_FACTS
  serie com unidade, base, e revisao declarada
  a distancia entre a serie e a decisao (a serie e CONTEXTO por defeito)

TIME_REQUIREMENTS
  periodo de referencia ≠ periodo de publicacao ≠ campanha agricola

GEO_REQUIREMENTS
  NUTS/pais, com versao NUTS

DENOMINATOR_REQUIREMENTS
  MATERIALIDADE: uma variacao so e um achado contra uma base. «Subiu 8 %» sem
  base historica nao e nada.

HIPOTESE A TESTAR (do enunciado), e ela sobreviveu:
  CHANGE + MATERIALITY + CONTEXT + DECISION_AFFECTED
  — e o benchmark acrescenta um quinto termo:
  + ATTRIBUTION_LIMIT  (o que esta variacao NAO prova)

PRIVATE_DATA_REQUIRED?
  NAO para a serie. SIM para ligar a serie a uma decisao comercial ADAMA.

WHAT_HAPPENS_IF_MISSING
  materialidade ausente .............. FALSIFICA (dashboard vira intelligence)
  decisao afetada ausente ............ DEGRADA a contexto, e deve DIZE-LO
```

---

## 8 · FUTURE / HORIZON INTELLIGENCE

```
QUESTION
  O que ainda nao aconteceu e nos obriga a preparar alguma coisa?

MINIMUM_ENTITIES
  SIGNAL · SOURCE · SUBJECT (praga/substancia/regra) · HORIZON

MINIMUM_FACTS
  o que foi observado (nao o que foi previsto)
  o HORIZONTE e a INCERTEZA declarados (`INT-LAW-135`)
  a REPETICAO — o sinal voltou a aparecer?

⚠️ A LEI QUE O BENCHMARK IMPOE:
  FUTURE_DATE != FUTURE INTELLIGENCE.
  Uma data de caducidade e um FACTO PRESENTE sobre o futuro, e e a coisa mais
  solida que temos. Um sinal fraco e outra coisa, e nao se misturam.

TIME_REQUIREMENTS
  data do sinal + horizonte + data de revisao

INDEPENDENCE_REQUIREMENTS
  CRITICO. 392 -> 27 na EFSA. A repeticao por copia nao e repeticao.

PRIVATE_DATA_REQUIRED?
  NAO.

WHAT_HAPPENS_IF_MISSING
  horizonte ausente .................. BLOQUEIA
  repeticao nao medivel .............. DEGRADA a «um sinal»
  sinal promovido a achado ........... FALSIFICA (93 % de erro, medido na EFSA)
```

---

## 9 · OPPORTUNITY INTELLIGENCE

```
QUESTION
  Ha aqui alguma coisa que valha a pena a ADAMA fazer, e que possamos
  DEFENDER?

⚠️ ESTA CAPACIDADE E A SOMA DAS OUTRAS, E POR ISSO E A MAIS FACIL DE FALSIFICAR.

MINIMUM_ENTITIES
  PROBLEM (EPPO) · CROP (EPPO) · AREA · WINDOW · PPP_USE · PORTFOLIO ·
  DECISION_OWNER

MINIMUM_FACTS, por nivel — E OS NIVEIS NAO SE MISTURAM:

  NIVEL A · OPORTUNIDADE AGRONOMICA
    existe problema + existe janela + existe resposta agronomica conhecida
    REQUER: disease/pest nivel >= 2 · crop window · ciencia ou guideline
    PUBLICO: SIM

  NIVEL B · OPORTUNIDADE DE PORTFOLIO REGISTADO
    A + a ADAMA tem uso autorizado que cobre (cultura, alvo, pais)
    REQUER: LABEL INTELLIGENCE completa (a tupla de seis)
    PUBLICO: SIM

  NIVEL C · OPORTUNIDADE COMERCIAL
    B + o produto esta a venda, com stock, preco e canal
    REQUER: dado interno ADAMA
    PUBLICO: NAO

  NIVEL D · OPORTUNIDADE DE VENDA
    C + existe um cliente identificavel, com area, cultura e historico
    REQUER: identidade do agricultor + ligacao campo->operador + CRM
    PUBLICO: NAO — e e isto que a DTN vende, com dado proprietario de 95 %+
             dos agricultores dos EUA

JOIN_KEYS
  (EPPO_CROP, EPPO_TARGET, AREA, JANELA) -> PPP_USE -> PORTFOLIO

TIME_REQUIREMENTS
  A JANELA E O CAMPO QUE DECIDE. E ela nao e uma data: e
  (fenologia da cultura) ∩ (janela de infeccao) ∩ (janela de aplicacao do
  rotulo) ∩ (janela de preparacao comercial).

PRIVATE_DATA_REQUIRED?
  NAO para A e B. SIM, obrigatoriamente, para C e D.

WHAT_HAPPENS_IF_MISSING
  janela ausente ..................... BLOQUEIA (nao ha acionabilidade)
  nivel nao declarado ................ FALSIFICA — e este e o pior erro
                                       possivel desta casa, porque uma
                                       oportunidade de nivel A apresentada como
                                       nivel D e uma promessa que o dado nao
                                       sustenta
```

---

## 10 · O DENOMINADOR COMUM DAS NOVE

Se houver uma frase para levar:

```
TODAS AS NOVE EXIGEM QUE A ESPECIE DA EVIDENCIA VIAJE COM ELA.

OBSERVADO · FAVORAVEL · MODELADO · CONFIRMADO
REGISTO · COMUNICACAO · GUIDELINE · SERIE OFICIAL

Esta casa JA declara isso — no contrato de fonte, com
`EVIDENCE_CLASS`, e com leis escritas ao lado:

  IT-T2-001/002/003  AGROCLIMATIC_SIGNAL != PEST_OCCURRENCE
  IT-T3-011          REGISTRY != FIELD_SIGNAL
  IT-T5-002          TECHNICAL_GUIDELINE != CURRENT_FIELD_SIGNAL
  IT-T9-008          COMPANY_CLAIM != REGULATORY_FACT

E NENHUMA DELAS ATRAVESSA A FRONTEIRA ATE A INTELLIGENCE.
O contrato de saida da Admission (COL-LAW-043) nao tem campo onde a especie
da evidencia caiba.
```

Isso é o P0. Está em
[`../../docs/operacao/COLLECTION-P0-CHANGE-REQUEST.md`](../../docs/operacao/COLLECTION-P0-CHANGE-REQUEST.md).
