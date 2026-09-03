# Auditoria da régua comercial · as 37, medidas por fora

> Auditoria, não alteração. `v21_oportunidades.py` não foi tocado: portões,
> score, arquétipos, red team, status, dados e evidências estão como estavam.
> Todo número desta página sai de `scripts/auditoria_regua_comercial.py`, que lê
> `DESIGN-INGEST/OPPORTUNITIES.json` (do diretório reconstruído ou do zip
> versionado) e grava
> `data/samples/AUDITORIA-SOMBRA/AUDITORIA-REGUA-COMERCIAL-37.json`.
>
> `BUILD_ID` auditado: `V21-99226fbb90dcdbc2` · pacote lido do zip.

    MEDIR NÃO É MEXER. QUEM MEXE ANTES DE MEDIR NÃO SABE O QUE MUDOU.

---

## 0 · A pergunta, e por que ela não é a do motor

O motor pergunta **«esta convergência é defensável?»** e responde bem: os oito
portões e as nove perguntas do red team derrubam o que não se sustenta.

A auditoria pergunta outra coisa: **«esta convergência vende alguma coisa —
o quê, para qual problema, onde, e por que agora?»**

As duas perguntas não são a mesma, e a diferença entre elas é o achado.

---

## 1 · O RESULTADO, EM UMA LINHA

**As 9 oportunidades que o motor confirma são 9 oportunidades estratégicas.
Nenhuma delas é uma venda. E o único caso que responde às quatro perguntas
comerciais está classificado como `TO_VALIDATE`.**

| Classificação sombra | das 37 | das 9 confirmadas |
|---|---:|---:|
| `SALES_READY` | **1** | **0** |
| `SALES_PREPARE` | **3** | **0** |
| `STRATEGIC_OPPORTUNITY` | **19** | **9** |
| `TO_VALIDATE` | **14** | **0** |

A régua atual não separa **venda** de **preparação**. Ela separa
**defensável** de **não defensável** — e é excelente nisso. Só que o que sobra
depois do filtro é, quase inteiramente, calendário regulatório europeu e peso
econômico de cultura.

**Nenhum dos 11 casos `O1_FIELD_PRESSURE` foi confirmado. Nenhum dos 9
`O4_COMPETITIVE_OPENING`. Nenhum `O3` e nenhum `O6`.** As 9 confirmadas são
**6 × O5 regulatório** e **3 × O2 mercado** — os dois únicos arquétipos que
**não têm alvo agronômico**.

---

## 2 · AS 9 CONFIRMADAS, UMA A UMA

Ordem: as três de mercado primeiro, depois as seis regulatórias.

### 2.1 · `OPP_576D71D702F0` — milho · momento de mercado

| | |
|---|---|
| **ARQUÉTIPO** | `O2_MARKET_MOMENT` · status `ACT_NOW` · score 9 |
| **GATILHO EXTERNO** | **NÃO.** Cotação semanal de **milho forrageiro, €243,39/t**, semana 27/07–02/08/2026, publicada em 06/08 (`IT-MKT-023`), mais duas linhas de área do ISTAT |
| **PRODUTO COMERCIAL ADAMA** | **SIM** — Diode®, Lamdex® Extra, NICOGAN VO, PIRIMOR 50, TAIFUN MK CL PFNPE |
| **RÓTULO CULTURA × ALVO** | `NOT_APPLICABLE` — o caso não nomeia alvo |
| **GEOGRAFIA** | `NATIONAL`, herdada do próprio preço nacional |
| **TIMING** | **UNKNOWN.** `WINDOW_STATE=UNKNOWN`. O `ACT_NOW` vem da data de **publicação do preço** (27 dias), não de janela de aplicação |
| **FAMÍLIAS DE EVIDÊNCIA** | 2 — `MARKET_OBSERVATION` + `CROP_ECONOMIC_WEIGHT_CLAIM`. Ambas estatísticas; nenhuma observação de campo |
| **VEREDITO COMERCIAL** | `STRATEGIC_OPPORTUNITY` |
| **POR QUÊ** | preço de cereal não abre janela de aplicação de defensivo. O caso responde *«o milho pesa e a ADAMA tem 18 rótulos nele»* — que é priorização de portfólio, não motivo para ligar para o cliente esta semana |

### 2.2 · `OPP_8EA4F5C0D3F4` — cevada · momento de mercado

| | |
|---|---|
| **ARQUÉTIPO** | `O2_MARKET_MOMENT` · `ACT_NOW` · score 8 |
| **GATILHO EXTERNO** | **NÃO.** Cotação semanal de **cevada forrageira, €205,60/t** (`IT-MKT-022`), mesma semana, mesmo publicador |
| **PRODUTO COMERCIAL ADAMA** | **SIM** — MAXENTIS, Maganic® (mais 6 de registro) |
| **RÓTULO CULTURA × ALVO** | `NOT_APPLICABLE` |
| **GEOGRAFIA** | `NATIONAL` |
| **TIMING** | **UNKNOWN**, pelo mesmo motivo |
| **FAMÍLIAS DE EVIDÊNCIA** | **1** — `MARKET_OBSERVATION`, publicador único |
| **VEREDITO COMERCIAL** | `STRATEGIC_OPPORTUNITY` |
| **POR QUÊ** | é o caso mais fino das 9: uma única cotação semanal sustenta um `ACT_NOW`. A cevada é cultura real e o portfólio é forte — mas o gatilho é uma linha de preço |

### 2.3 · `OPP_AF16E6A6B8B3` — videira · momento de mercado

| | |
|---|---|
| **ARQUÉTIPO** | `O2_MARKET_MOMENT` · `FUTURE_PREPARATION` · score 9 |
| **GATILHO EXTERNO** | **NÃO.** Peso econômico (ISTAT) + cotações (BMTI, EC) |
| **PRODUTO COMERCIAL ADAMA** | **SIM** — BANJO, FOLPAN GOLD, Lamdex® Extra, MAVRIK SMART (25 rótulos na cultura) |
| **RÓTULO CULTURA × ALVO** | `NOT_APPLICABLE` |
| **GEOGRAFIA** | `NATIONAL` |
| **TIMING** | **exibe `2027-05-31`, e essa data está errada de natureza** — vem de `PREPARATION_WINDOW = «ate 2027-05-31, quando historicamente sai o ato»`. É data administrativa de publicação de decreto, apresentada num campo cuja lei diz *«`WINDOW_*` é a janela de APLICAÇÃO»* |
| **FAMÍLIAS DE EVIDÊNCIA** | 2, ambas econômicas |
| **VEREDITO COMERCIAL** | `STRATEGIC_OPPORTUNITY` |
| **POR QUÊ** | a videira é a cultura de maior portfólio ADAMA do pacote. O que falta é o problema: o caso não diz contra o quê |

### 2.4 – 2.9 · As seis `O5_REGULATORY_PREPARATION`

Todas com a mesma anatomia: um fato regulatório europeu (`RFF_*`), os produtos
ADAMA italianos que contêm a substância, e o par de rótulo. **Nenhuma tem alvo,
nenhuma tem geografia italiana, nenhuma tem janela de aplicação, e todas têm
exatamente 1 família externa de evidência.**

| ID | Substância | Data UE | Dias | Produtos ADAMA | Cultura | Veredito |
|---|---|---|---:|---:|---|---|
| `OPP_6E18A133EE14` | BUPIRIMATO | 2027-01-31 | **151** | 5 (NIMROD, NIMROD 250 EW…) | tomate | `STRATEGIC` |
| `OPP_2BDE8FC566CE` | FENPROPIDINA | 2027-05-15 | **255** | 1 (SPYRALE) | beterraba | `STRATEGIC` |
| `OPP_88CC35C57C7B` | IMAZAMOX | 2027-06-30 | **301** | 4 (DAVAI, EARLEX…) | soja | `STRATEGIC` |
| `OPP_E6200AA0FA63` | FLORASULAME | 2030-12-31 | **1.581** | 3 (ANTARKTIS, CLEAVE…) | cevada | `STRATEGIC` |
| `OPP_886307860F79` | MESOTRIONA | 2032-05-31 | **2.098** | 2 (DIODE, PYXIDES WG) | milho | `STRATEGIC` |
| `OPP_3965565ACFCC` | FOLPETE | **2039-10-31** | **4.807** | 13 (FOLPAN 80 WDG, FOLPAN GOLD…) | videira | `STRATEGIC` |

**Gatilho externo:** PARCIAL nas seis. Uma data publicada no Jornal Oficial é
evento externo real — mas o próprio arquétipo declara
`EXPIRACAO DE APROVACAO NAO E NAO-RENOVACAO, NAO e risco e NAO e oportunidade`.
O motor concorda com a auditoria; só não tirou a consequência da própria frase.

**Produto comercial ADAMA:** SIM em cinco (há produto do catálogo comercial na
cultura); a sexta, `OPP_2BDE8FC566CE`, tem SPYRALE só no registro — a beterraba
tem catálogo comercial por outra via.

**Rótulo cultura × alvo:** `NOT_APPLICABLE` nas seis — não há alvo.

**Timing:** `FUTURE` nas seis, **por construção**. `estado_temporal()` devolve
`FUTURE_PREPARATION` para O5 antes de olhar qualquer data.

**Por quê o veredito é `STRATEGIC`, e não `TO_VALIDATE`:** para bupirimato,
fenpropidina e imazamox — 151, 255 e 301 dias — preparação regulatória é
trabalho real e datado, e cabe a `REGULATORY`, `PORTFOLIO` e `SUPPLY`. Para
folpete (**treze anos**), mesotriona (seis) e florasulame (quatro), o rótulo
`FUTURE_PREPARATION` é generoso: são linhas de cadastro.

    O PRAZO QUE NÃO CHEGA NÃO PREPARA NINGUÉM.

---

## 3 · O QUE A RÉGUA SUPERVALORIZA

**1 · A data europeia distante.** Seis das nove confirmadas são O5, e três
delas têm data a mais de quatro anos. O5 é o **único arquétipo que o portão C
não avalia** — `portoes()` abre com
`if o['ARCHETYPE'] != 'O5_REGULATORY_PREPARATION'` antes de checar tempo. E
como O5 não tem alvo, o portão D também não se aplica; e como sua evidência
vem de quatro publicadores distintos por natureza (EUR-Lex, ministério, FRAC,
HRAC), o red team de fonte única também não a alcança. **O5 não passa nos
portões: ela passa ao lado deles.**

**2 · O preço semanal de cereal como `ACT_NOW`.** As duas únicas confirmadas em
estado `ACT_NOW` do pacote inteiro (milho e cevada) têm por gatilho uma cotação
publicada 27 dias antes. `data_do_sinal()` lê `PUBLICATION_DATE` de
`MARKET_OBSERVATION` como prova de que o caso é corrente — e é, mas corrente
não é acionável.

    A DATA DO DOCUMENTO DIZ QUE ELE É DE HOJE. NÃO DIZ QUE HÁ O QUE FAZER HOJE.

**3 · O score, que premia justamente o que não vende.** Quatro casos empatam no
score máximo do motor (**11**) — e **os quatro têm o mesmo problema: o
documento não pede tratamento**.

| Caso de score 11 | O que o documento realmente diz |
|---|---|
| `OPP_20D89B04F64D` · pera × ticchiolatura · ER | nos **oito boletins** que o sustentam, o texto de intervenção **nunca menciona ticchiolatura**: fala de *maculatura bruna* |
| `OPP_DA4B5954F72A` · maçã × ticchiolatura · ER | os mesmos oito boletins; para macieira o texto é *colpo di fuoco* e *glomerella* |
| `OPP_3F736F0A9467` · videira × peronospora | *«In generale non necessari interventi»* · *«a defesa antiperonosporica pode ser suspensa»* |
| `OPP_68984FFD5ABF` · videira × *Scaphoideus* | *«a defesa contra Scaphoideus titanus pode considerar-se concluída»* |

Nos dois primeiros, `ISSUE_SCAB` entrou pela lista `PESTS_AND_DISEASES_CITED`
— que é o **inventário** do documento, não a recomendação dele.

    O SCORE ORDENA. ELE ORDENOU O QUE O MOTOR MEDIU,
    E O MOTOR NÃO MEDIU A DIREÇÃO DO TEXTO.

**4 · O par cultura × alvo, que é produto cartesiano.** O motor cruza a lista
plana `CROP_IDS` com a lista plana `ISSUE_IDS` do **mesmo documento**. Um
boletim que cobre 10 culturas e tem um alvo normalizado gera 10 pares. Daí
nascem, nos sinais de campo, pares como *beterraba × ticchiolatura* e *soja ×
ticchiolatura* — 13 ocorrências cada. **O que impede esses pares de virarem
cartão não é um portão: é a tabela de rótulo, que por acaso não tem
autorização para eles.** A sanidade agronômica está sendo feita por acidente.

**5 · Três casos em que o motor leu o sinal ao contrário.**

| Caso | Score | O que o documento diz |
|---|---:|---|
| `OPP_F6EEF5B32F65` · milho × diabrótica · Lombardia | 10 | *«durante a floração **vigora a proibição** de intervenção fitoiátrica com inseticidas, para tutela das abelhas»* — **uma proibição de tratar virou pressão de campo** |
| `OPP_3F736F0A9467` · videira × peronospora | 11 | *«In generale **non necessari interventi**»* e *«a defesa antiperonosporica **pode ser suspensa**»* |
| `OPP_4C39CCC05EEB` · arroz × *Echinochloa* | 7 | a resistência italiana documentada é **aos inibidores da ACCase (grupo A)** (`IT-RES-025`), com resistência múltipla A+B (`IT-RES-026`). O motor apresenta `MODOS_DE_ACAO: ['A']` como **relevância ADAMA** — oferece o modo de ação a que a planta resiste |

O motor lê que a praga **aparece**. Ele não lê se o texto manda **agir**.

---

## 4 · O QUE A RÉGUA SUBVALORIZA

**`OPP_75C37DED9160` — maçã × carpocapsa · Veneto — o único `SALES_READY` do
pacote, e está em `TO_VALIDATE`.**

O boletim frutícola do Veneto, corrente, declara o terceiro voo de *Cydia
pomonella* terminado com **«danni in aumento anche in frutteti a gestione
integrata»** — ou seja, **a solução em uso está falhando, dito pelo serviço
oficial**. A região é declarada e representada. Há rótulo ministerial
verificado no par maçã × carpocapsa e **dois produtos do catálogo comercial no
par**: Lamdex® Extra e MAVRIK SMART.

Necessidade + portfólio + onde + por que agora. As quatro fecham.

O portão que o derruba é `A_GEOGRAFIA · apoios em geografias que nao se contem`
— e o motivo é um defeito, não um julgamento (§5).

**Mais três casos que a régua rebaixa por defeito, não por mérito:**

| Caso | Sombra | O que a régua não viu |
|---|---|---|
| `OPP_9C600748BB1B` · milho × piralide · FVG | `SALES_PREPARE` | a ERSA declara **limiar** («posturas > 3 por 100 plantas»), início do voo da 3ª geração e pico esperado. É o **único O1 regional com `REGION_REPRESENTS=true` e alvo**. Derrubado pelo mesmo portão A |
| `OPP_56F19FD9F62B` · maçã × percevejo | `SALES_PREPARE` | *«la strategia di difesa dovrà essere puntuale»*, com hora do dia e intervalo de segurança. Rótulo e catálogo (MAVRIK SMART) fecham. O que falta de verdade é **onde**: a fonte tem `GEOGRAPHIC_SCOPE=NAO_SEI` |
| `OPP_68984FFD5ABF` · videira × *Scaphoideus* | `SALES_PREPARE` | a defesa 2026 fechou, mas a obrigação recorre por norma e a próxima janela existe **em forma** no pacote: `REGULATORY_WINDOW = «2 tratamentos, 1ª janela 08–19/06»`. Campanha 2027 com data — e o campo nunca é lido |

**E um caso que é subvalorizado pelo motivo certo, e vale registrar:**
`OPP_EA2AE1EFB775` (tomate × peronospora · Veneto) tem o melhor gatilho do
pacote — chuvas de 17–23/08 criaram *«condizioni ideali per lo sviluppo di
nuove infezioni»* e o boletim **recomenda tratar os lotes com colheita prevista
em 25–30 dias**: necessidade, região e janela, todas declaradas. O que falta é o
produto: **nenhum item do catálogo comercial público tem rótulo no par tomate ×
peronospora**, embora exista no registro ministerial. É exatamente a distinção
51 × 163, e aqui ela funcionou.

**E a ausência maior de todas: o trigo duro não existe no motor.**
Há **0 rótulos** com `CROP_DURUM_WHEAT` — a normalização colapsa *frumento* em
`CROP_WHEAT_GENERIC`. A cultura mais italiana do portfólio de cereal, e onde
vivem MAXENTIS, MAGANIC e SORATEL, **não pode ser nomeada** por este motor.

---

## 5 · DOIS DEFEITOS, REPRODUZIDOS

Ambos são verificados por `scripts/auditoria_regua_comercial.py`, no bloco
`DEFEITOS_REPRODUZIDOS`. Nenhum foi corrigido.

### D1 · O red team de O4 dispara na própria frase do arquétipo

`red_team()` roda a regex `share|participac|quota` sobre `json.dumps(o)`. Mas
`o` já contém `WHAT_IT_DOES_NOT_PROVE`, que é o texto **fixo** de O4 e diz
*«COMUNICACAO NAO E **PARTICIPACAO** DE MERCADO. NAO prova investimento,
**share** nem resultado.»* A regex casa com o próprio aviso.

**Efeito: nenhum dos 9 casos `O4_COMPETITIVE_OPENING` pode ser confirmado, por
construção.** Os 9 carregam a mesma constatação de red team, e nenhum a mereceu.

    O AVISO CONTRA UM ERRO NÃO É O ERRO.
    QUEM MEDE O PRÓPRIO TEXTO MEDE A SI MESMO.

### D2 · O portão A trata o rótulo nacional como geografia concorrente

`portoes()` reúne os `REGION_IDS` de **todos** os apoios. O sinal de campo é
regional (`REGION_VENETO`); o rótulo ministerial é `GEO_ITALY`. São duas
geografias, o caso é regional, e o portão fecha por *«geografias que nao se
contem»*.

**Efeito: a autorização nacional — que é justamente o que torna o caso regional
vendável — passa a derrubar o caso.** Sete casos, todos `O1_FIELD_PRESSURE`
regionais ou provinciais: `OPP_20D89B04F64D`, `OPP_75C37DED9160`,
`OPP_9C600748BB1B`, `OPP_DA4B5954F72A`, `OPP_EA2AE1EFB775`, `OPP_F139E05A9F3A`,
`OPP_F6EEF5B32F65`.

    ROTULO NACIONAL CONTEM A REGIAO. CONTER NAO E CONTRADIZER.

A intenção do portão está certa — *apoio provincial não fala pela região* — e
ela já é coberta pela primeira metade do próprio portão A, que testa
`REGION_REPRESENTS`. A segunda metade é que se enganou de conjunto.

---

## 6 · A QUALIDADE DA CONVERGÊNCIA, MEDIDA

O relatório do motor celebra **515 IDs de evidência distintos**. Isso conta
documentos, não famílias.

Descontando o lado ADAMA — rótulo, registro e substância ativa **provam
portfólio, não corroboram sinal** — sobram:

| Famílias externas por caso | Casos |
|---:|---:|
| 1 | **30** |
| 2 | **7** |
| 3 ou mais | **0** |

**Nenhum dos 37 casos tem três famílias independentes.** Trinta têm uma só. A
convergência que o motor executa é um **join de dois lados** — sinal externo ×
rótulo ADAMA — e não uma convergência de evidência.

Isso não invalida os casos: como a auditoria pediu, *FIELD + LABEL + TIMING* já
basta para uma oportunidade forte, e é exatamente o que `OPP_75C37DED9160` tem.
Mas explica por que o red team quase nunca encontra contradição: **não há
segunda família para contradizer a primeira.**

---

## 7 · A MENOR ALTERAÇÃO QUE CRIA `COMMERCIAL PRIORITY`

Não mexer em portão, score, arquétipo, red team nem estado. **Acrescentar um
campo derivado ao lado do que já existe**, e ordenar por ele.

    COMMERCIAL_PRIORITY não substitui OPPORTUNITY_STATE.
    Um diz se a leitura se sustenta; o outro, se ela vende.

**O campo, com quatro perguntas e nada mais:**

```
COMMERCIAL_PRIORITY = f(
    NEED_IS_DIRECTIONAL,     # a fonte manda AGIR, não suspender nem proibir
    PRODUCT_IS_COMMERCIAL,   # há produto dos 51 com rótulo no par cultura × alvo
    GEOGRAPHY_HOLDS,         # a alegação cabe no âmbito de quem a sustenta
    WINDOW_IS_APPLICATION,   # a janela é de aplicação, não data de ato
)
```

**Os quatro insumos já existem no pacote e nenhum exige coleta nova:**

| Insumo | De onde sai hoje | O que falta |
|---|---|---|
| `NEED_IS_DIRECTIONAL` | `INTERVENTION_GUIDANCE` dos boletins — campo já preenchido em 86 sinais client-safe | ser **lido**. Hoje o motor lê `PESTS_AND_DISEASES_CITED` (inventário) e ignora a recomendação |
| `PRODUCT_IS_COMMERCIAL` | `PRODUCTS-COMMERCIAL.json` (51) → `MATCHED_REGULATORY_ID` → `PRODUCT-RELATIONSHIPS` | ser **usado**. O arquivo é carregado por `main()` e **nunca consultado**: os 51 não tocam o motor. Os 77 produtos citados nas 37 saem todos dos 163 |
| `GEOGRAPHY_HOLDS` | `GEOGRAPHIC_SCOPE` + `REGION_REPRESENTS` do sinal de campo | separar do rótulo (D2) |
| `WINDOW_IS_APPLICATION` | `REGULATORY_WINDOW` («1ª janela 08–19/06») e `INTERVENTION_GUIDANCE` | distinguir de `PREPARATION_WINDOW`, que hoje é a **única** janela que o parser aceita — e é data de ato |

**Três correções de defeito, que não são mudança de régua:**
1. no red team de O4, medir o **conteúdo do caso**, não o dicionário completo
   de `o` (D1);
2. no portão A, calcular `geos` **só sobre os apoios que declaram geografia de
   observação** (D2);
3. no leitor de janela, **não aceitar `PREPARATION_WINDOW` como
   `WINDOW_*`** — é data administrativa, e a lei do campo já diz isso.

**Uma correção de dado, fora do motor:** normalizar `ISSUE_IDS` **por cultura**
dentro do boletim, em vez de uma lista plana por documento. Hoje 483 menções de
praga viram **12 alvos distintos**, e o par cultura × alvo é cartesiano.

**O que NÃO fazer:** não afrouxar `CLIENT_SAFE`, não confirmar por score, e não
transformar O5 em urgência. A lei do client-safe é o que dá credibilidade ao
resto.

---

## 8 · O QUE A CAMADA VOCI / SINTONIA SCRAP PODE MELHORAR

**Hoje ela não entra no motor.** `PUBLIC-VOICES.json` é carregado por `main()`
e nunca indexado por nenhum arquétipo. A única referência a `PUBLIC_VOICE` está
numa regra de red team — que **nunca dispara**, porque nenhuma voz jamais entra
como apoio.

São **79 vozes, 65 client-safe**, e elas cobrem exatamente as culturas dos
casos mais fracos em corroboração:

| Cultura | Vozes | Casos que ganhariam segunda família |
|---|---:|---|
| videira | 18 | `OPP_3F736F0A9467`, `OPP_68984FFD5ABF`, `OPP_C37A1FD2742E`, `OPP_31C59C08CBAB` |
| maçã | 14 | **`OPP_75C37DED9160`** (o único `SALES_READY`, hoje com 1 publicador), `OPP_56F19FD9F62B` |
| milho | 13 | `OPP_9C600748BB1B`, `OPP_F6EEF5B32F65` |
| tomate | 12 | `OPP_EA2AE1EFB775` |
| oliveira | 10 | `OPP_568684853264`, `OPP_EE1E2A3869EE` |

**Três consertos de contrato antes que ela sirva de evidência — e todos são de
extração, não de coleta:**

1. **`ISSUE_IDS` está vazio nas 79.** O alvo existe em texto livre (`ISSUE:
   FLAVESCENCE`, `ISSUE: FUSARIUM`) e nunca foi normalizado. Sem `ISSUE_IDS`
   não há par cultura × alvo, e sem par a voz não se liga a caso nenhum.
2. **A data é relativa.** `DATE_RELATIVE: «1 year ago»`, `«4 years ago»`, com
   `REFERENCE_DATE: NAO SEI`. O portão C rejeita, e com razão.
3. **A região falta em 64 das 79.** Sem região a voz não sustenta alegação
   regional — só nacional, e aí promove geografia.

**O que ela pode e o que não pode fazer, resolvido isso:**

- **Pode:** ser a **segunda família independente** que os 30 casos de família
  única não têm — e é a única fonte no pacote que fala em **primeira pessoa do
  campo**. `KIND: FIRST_PERSON_FIELD_REPORT` é justamente o tipo de sinal que
  um boletim oficial não carrega: relato de quem aplicou.
- **Pode:** confirmar direção. O boletim diz *«suspender»*; se a voz diz que
  ainda há pressão, isso é discordância mensurável entre serviço e campo — e é
  inteligência real.
- **Não pode:** virar incidência. O próprio registro já escreve
  *«não prova que quem escreveu é produtor; não prova ocorrência no campo»*, e
  a regra de red team que existe para isso (`voz isolada tratada como
  incidência`) está certa e deve **passar a poder disparar**.

**E o alvo mais óbvio:** as vozes trazem `CASE_ID: IT-DURUM_WHEAT-FUSARIUM`.
O trigo duro × fusariose é o caso italiano por excelência, e **não existe no
motor** porque não existe rótulo com `CROP_DURUM_WHEAT`. A camada VOCI já tem
a necessidade; falta a normalização de cultura do lado do rótulo.

---

## 9 · O QUE ESTA AUDITORIA NÃO DIZ

- **Não diz que o motor está errado.** Os oito portões e as nove perguntas
  fazem o que prometem, e a lei do client-safe não foi afrouxada em nenhum
  ponto. O que falta não é rigor: é uma **segunda pergunta**.
- **Não diz que as 9 confirmadas devem sair.** Elas são preparação legítima de
  portfólio, supply e regulatório. Devem parar de ocupar o topo de uma lista
  que o comercial lê como *«ligue para o cliente»*.
- **Não diz que `OPP_75C37DED9160` é uma venda garantida.** Diz que é o único
  caso do pacote que **responde às quatro perguntas** — e que tem uma
  fragilidade declarada: um único publicador.
- **Não mede demanda, sell-in, estoque, pedido nem pipeline.** Nada aqui vem de
  dado interno da ADAMA, e nada aqui é inferido dele.

---

## 10 · COMO REPRODUZIR

```bash
python3 scripts/auditoria_regua_comercial.py
```

Lê o pacote (diretório reconstruído ou `build/SINTONIA-ITALY-REALITY-HANDOFF-V2.1.zip`),
verifica a coerência interna da classificação — uma `SALES_READY` sem produto
comercial, sem rótulo no par, sem gatilho ou sem geografia **falha e não grava**
— e escreve `data/samples/AUDITORIA-SOMBRA/AUDITORIA-REGUA-COMERCIAL-37.json`.

Cada ficha traz três blocos separados de propósito:

- **`MOTOR`** — o que o motor decidiu, copiado sem alteração;
- **`MEASURED`** — o que sai do pacote por join de ID e reproduz sozinho;
- **`REVIEWED`** — a leitura do texto da fonte, **com o ID do apoio que a
  justifica ao lado**.

    JULGAMENTO SEM O ID DA EVIDÊNCIA AO LADO
    É OPINIÃO COM CARA DE MEDIÇÃO.
