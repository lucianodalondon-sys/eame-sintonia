# Opportunity Engine V1.1 · a camada COMMERCIAL PRIORITY

> **Não substitui `OPPORTUNITY_STATE`.** Ele responde *«esta leitura se
> sustenta?»*. `COMMERCIAL_PRIORITY` responde *«isto é oportunidade comercial
> defensável para o portfólio ADAMA?»*. São perguntas diferentes, e um caso pode
> ser CONFIRMADO e não vender — como pode vender com um portão ainda aberto.
>
> Base: `claude/opportunity-radar-audit-hem6p2` · `757857c`.
> Nada foi implantado, e o portal não foi tocado.

    A PRIMEIRA PERGUNTA É SOBRE A EVIDÊNCIA. A SEGUNDA É SOBRE O NEGÓCIO.
    UMA RÉGUA SÓ NÃO RESPONDE AS DUAS.

---

## 1 · A causa-raiz dos quatro problemas

### D1 · o red team acusava a própria advertência

`red_team()` rodava `re.search(r'share|participac|quota', json.dumps(o))`. Mas
`o` já continha `WHAT_IT_DOES_NOT_PROVE`, que é o texto **fixo** do arquétipo O4
e diz *«COMUNICACAO NAO E **PARTICIPACAO** DE MERCADO. NAO prova investimento,
**share** nem resultado.»* A regex casava com o próprio aviso.

**Efeito medido:** os **9** casos `O4_COMPETITIVE_OPENING` eram inconfirmáveis
por construção. Nenhum deles carregava a constatação por mérito.

**Causa-raiz:** a regra media o **dicionário inteiro** do caso, incluindo texto
metodológico e a advertência contra o erro que ela procura.

**Conserto:** `_texto_afirmado(o)` restringe a leitura a `CAMPOS_AFIRMADOS` — o
que o caso **afirma** (`WHY_NOW`, `ADAMA_RELEVANCE`, `WHAT_IT_PROVES`, cultura,
alvo, geografia, produtos). Ficam de fora, por lista declarada:
`WHAT_IT_DOES_NOT_PROVE`, todo `*_LAW` e `*_MEANS`, `BLOCKING_GATES` e a
aritmética.

    O AVISO CONTRA UM ERRO NÃO É O ERRO.
    QUEM MEDE O PRÓPRIO TEXTO MEDE A SI MESMO.

Provas **T1** (a advertência não dispara) e **T2** (uma afirmação de *share* sem
evidência dispara), mais **T2b** (a afirmação em qualquer campo afirmado dispara).

### D2 · a geografia da autorização derrubava a geografia da afirmação

`portoes()` reunia os `REGION_IDS` de **todos** os apoios. O sinal de campo é
regional (`REGION_VENETO`); o rótulo ministerial é `GEO_ITALY`, porque a
autorização vale no país inteiro. Duas geografias, caso regional, portão fechado
por *«geografias que nao se contem»*.

**Efeito medido:** **7** casos `O1_FIELD_PRESSURE` regionais e provinciais
caíam — por causa da própria autorização que os tornava vendáveis.

**Causa-raiz:** um só campo respondia a três perguntas diferentes.

**Conserto:** três campos, três perguntas.

| campo | responde |
|---|---|
| `CLAIM_GEOGRAPHY` | onde a oportunidade **afirma** que o fato está |
| `FIELD_GEOGRAPHY` | onde **quem observou** declara estar |
| `PRODUCT_AUTHORIZATION_GEOGRAPHY` | onde o produto é **autorizado** |

O portão A passa a somar apenas `TIPOS_QUE_OBSERVAM`. O rótulo, o registro e a
substância ativa vivem em `TIPOS_DE_AUTORIZACAO` e não votam ali.

    RÓTULO NACIONAL CONTÉM A REGIÃO. CONTER NÃO É CONTRADIZER.

Provas **T3** (Veneto + rótulo Itália não é conflito) e **T4** (duas geografias
de **observação** continuam sendo conflito, e a autorização não promove o sinal
a nacional).

### crop × target · o par era produto cartesiano

O boletim traz uma lista plana de culturas e uma lista plana de alvos, e o motor
cruzava as duas. Um documento com dez culturas e um alvo normalizado produzia
dez pares.

**Reproduzido antes de corrigir** (`python3 scripts/v21_necessidade.py`):

| | |
|---|---:|
| pares cultura × alvo, cartesianos (V1) | **31** |
| pares **observados** (V1.1) | **12** |
| removidos | **22** |
| adicionados | **3** |

Entre os removidos: *beterraba × ticchiolatura*, *soja × ticchiolatura*,
*trigo × ticchiolatura*, *arroz × ticchiolatura*, *milho × ticchiolatura* — a
sarna é doença de pomáceas, e nenhuma frase de nenhum documento a atribuiu a
essas culturas. **O que impedia esses pares de virarem cartão não era um portão:
era a tabela de rótulo, que por acaso não tinha autorização para eles.** A
sanidade agronômica estava sendo feita por acidente.

**Conserto:** `v21_necessidade.pares_observados()` só emite um par quando a
fonte os escreveu juntos, por um de quatro métodos declarados:

| método | quando vale |
|---|---|
| `PAIR_IN_SAME_CLAUSE` | cultura e alvo na mesma oração |
| `PAIR_IN_DOCUMENT_TITLE` | o título do boletim nomeia os dois («*Piralide del mais*») |
| `CROP_FROM_PRECEDING_CLAUSE` | o boletim escreve por tópico e a cultura vale até a próxima ser nomeada |
| `CROP_FROM_SINGLE_CROP_DOCUMENT` | o documento declara uma cultura só |

E duas recusas, ambas com teste:

- **o alvo nunca vem do cabeçalho** do documento (T10b) — era daí que
  `ISSUE_SCAB` do inventário se espalhava por nove culturas;
- **sem cultura declarada não há par** (T10c) — ler prosa para adivinhar a
  cultura puxava `CROP_MAIZE` de «as estações agrometeorológicas **mais**
  próximas», onde *mais* é advérbio português e não a cultura italiana.

    LISTA DE CULTURAS × LISTA DE ALVOS NÃO É OBSERVAÇÃO.
    O PAR EXISTE ONDE A FONTE O ESCREVEU JUNTO.

### catálogo comercial · carregado e ignorado

`PRODUCTS-COMMERCIAL.json` era lido em `main()` e **nunca consultado**. Dos 77
produtos citados nas 37 oportunidades do V1, **os 77 saíam dos 163 do registro**.

**Conserto:** `v21_comercial.casar()` produz, em cada oportunidade:

```
MATCHED_COMMERCIAL_PRODUCT_IDS
MATCHED_COMMERCIAL_PRODUCT_NAMES
COMMERCIAL_PRODUCT_COUNT
```

A junção é por **número de registro** (`MATCHED_REGULATORY_ID` do catálogo
contra `REGISTRATION_NUMBER` do rótulo), nunca por nome — `Lamdex® Extra`,
`LAMDEX EXTRA` e `Lamdex Extra` são três grafias do mesmo registro. Dos 51 do
catálogo, **38** trazem número casável; os outros 13 ficam fora do índice e a
contagem os declara, em vez de casá-los por texto.

**As duas camadas continuam.** A regulatória prova o direito de uso; a comercial
responde «isto existe para vender hoje?».

    AUTORIZAÇÃO NÃO É CATÁLOGO, E CATÁLOGO NÃO É RÓTULO.
    O REGISTRO DIZ QUE PODE. O CATÁLOGO DIZ QUE HÁ. O RÓTULO DIZ PARA QUÊ.

Provas **T8** (produto do registro não vira comercial) e **T9** (produto do
catálogo é reconhecido), mais a prova de que a junção é por número e não por nome.

---

## 2 · NEED_DIRECTION · o defeito comercial mais importante

O motor detectava que a praga **aparece**. Não lia se o texto manda **agir**.

Oito estados, classificados por contexto de oração e nunca por palavra solta:

```
POSITIVE_PRESSURE · MONITOR · NEUTRAL_MENTION · NO_ACTION_RECOMMENDED
ACTION_SUSPENDED · WINDOW_CONCLUDED · TREATMENT_PROHIBITED · UNKNOWN
```

Os quatro últimos **fecham** a porta comercial. Entre orações do mesmo par,
**a que manda parar vence a que manda agir**.

As frases que a auditoria mediu, e o que a V1.1 faz com elas:

| frase da fonte | V1 | V1.1 |
|---|---|---|
| «In generale non necessari interventi» | pressão de campo, score 11 | `NO_ACTION_RECOMMENDED` |
| «a defesa antiperonosporica pode ser suspensa» | pressão de campo | `ACTION_SUSPENDED` |
| «pode considerar-se concluída» | pressão de campo, score 11 | `WINDOW_CONCLUDED` |
| «durante a floração vigora a proibição de intervenção» | pressão de campo, score 10 | `TREATMENT_PROHIBITED` |
| «danni in aumento anche in frutteti a gestione integrata» | pressão de campo | `POSITIVE_PRESSURE` |

**Não é palavra solta.** «Terzo volo di *Cydia pomonella* **terminato**, con
danni in aumento» não é janela concluída: o que terminou foi o voo, não a defesa.
Por isso os padrões de conclusão exigem a defesa, o tratamento ou a armadilha na
mesma expressão (prova **T6b**).

**A frase original viaja com o rótulo.** Cada caso guarda `NEED_DIRECTION`,
`NEED_EVIDENCE_ID`, `NEED_EXCERPT`, `NEED_METHOD` e `NEED_FIELD`. A
classificação é INTERPRETAÇÃO SINTONIA; a frase é a prova, e **não é traduzida**
— `NEED_EXCERPT` está declarado em `FONTE`, ao lado das citações.

    CLASSIFICAR NÃO É SUBSTITUIR. O TRECHO ORIGINAL VIAJA COM O RÓTULO.

**Uma decisão que vale registrar:** `CITATION` foi deixada **fora** das fontes de
direção. A citação do boletim empacota vários assuntos dentro das mesmas aspas —
«non sono necessari interventi. Fase calante dei voli della Tignoletta…» — e a
advertência de um alvo escorria para os outros três. A citação continua sendo a
prova do fato; ela não é a recomendação sobre ele.

Provas **T5**, **T5b**, **T5c**, **T6**, **T6b** e **T7**.

---

## 3 · A régua comercial, por portões semânticos

Cinco estados. Nenhum sai de soma de pontos.

```
1 · a fonte manda parar?              → TO_VALIDATE
2 · é preparação regulatória (O5)?    → STRATEGIC_OPPORTUNITY
3 · há produto do catálogo comercial? → não: TO_VALIDATE
4 · há alvo agronômico?
      sem rótulo no par               → TO_VALIDATE
      necessidade não positiva        → SALES_PREPARE (MONITOR) · TO_VALIDATE
      geografia não se sustenta       → SALES_PREPARE
      tempo para agir                 → SALES_READY
      tempo impreciso                 → SALES_PREPARE
5 · sem alvo, com abertura (O2/O4)    → COMMERCIAL_WATCH
```

**Não há número mínimo de famílias externas.** Uma fonte oficial forte que feche
necessidade, portfólio, geografia e tempo basta. Uma segunda família amplifica e
ordena — não autoriza.

    CORROBORAÇÃO É AMPLIFICADOR, NÃO CONTADOR CEGO.

**O score continua ordenando, e continua não promovendo.** Um 11 com a
necessidade fechada continua sendo um 11 com a necessidade fechada (prova
`test_score_alto_nao_promove_de_categoria`).

**O tempo comercial só conta janela de APLICAÇÃO.** A única janela que o parser
lia em todo o pacote era `PREPARATION_WINDOW = «ate 2027-05-31, quando
historicamente sai o ato»` — a data em que a região publica o decreto. Agora
`WINDOW_KIND` separa `APPLICATION` de `PREPARATION` e de `MONITORING`, e só a
primeira alimenta `COMMERCIAL_WINDOW`.

    DATA DE ATO NÃO É JANELA DE APLICAÇÃO.
    QUANDO SAI O DECRETO E QUANDO SE PULVERIZA SÃO DOIS RELÓGIOS.

Provas **T11** (uma fonte forte basta), **T11b** (a testemunha é `SALES_READY`
com uma família), **T12** (muitas famílias fracas não geram `SALES_READY`) e
**T12b** (necessidade fechada não vende por muito produto).

---

## 4 · Um defeito que quase entrou, e não entrou

A primeira versão desta camada escrevia
`'a fonte que sustenta o caso não manda agir: ACTION_SUSPENDED'` — **frase com
variável dentro**. Quatro frases diferentes para a mesma razão, uma por direção.
A memória de tradução chaveia pelo próprio texto em português: cada uma nasceria
sem irmã em italiano.

Este projeto já cometeu isso duas vezes. Corrigido antes de fechar:
`WHY_COMMERCIAL_CODES` guarda o código estável, `WHY_COMMERCIAL` guarda a frase
**fixa**, e o valor variável já vive estruturado em `NEED_DIRECTION`,
`COMMERCIAL_WINDOW` e `COMMERCIAL_PRODUCT_COUNT`.

    O CÓDIGO É DADO. A FRASE É TEXTO. MISTURÁ-LOS PERDE OS DOIS.

As 26 frases fixas da camada foram traduzidas à mão para IT e EN e entraram na
memória; `NEED_EXCERPT` **não** entrou, porque é a palavra da fonte.

---

## 3b · E o caso é POR REGIÃO — a consequência que a medição impôs

Ao trocar o par cartesiano pelo par observado, apareceu um fato que o V1 não
podia ver: **7 dos 12 pares observados têm DIREÇÃO DIFERENTE em regiões
diferentes.**

| par | região | direção |
|---|---|---|
| videira × botrite | Emilia-Romagna | `POSITIVE_PRESSURE` — «*intervir em pré-colheita com Fenhexamid*» |
| | Toscana | `ACTION_SUSPENDED` |
| milho × piralide | Friuli-Venezia Giulia | `POSITIVE_PRESSURE` — «*tratamento justificado quando posturas > 3 por 100 plantas*» |
| | Lombardia | `TREATMENT_PROHIBITED` — «*durante a floração vigora a proibição*» |

O serviço fitossanitário italiano **é regional por construção**. Juntar duas
regiões num caso «nacional» e depois deixar a mais restritiva vencer faz duas
coisas erradas de uma vez: **promove geografia** — que é o que o portão A existe
para impedir — e **apaga a oportunidade real da outra região**.

    DUAS REGIÕES QUE DISCORDAM NÃO SÃO UM CASO NACIONAL:
    SÃO DOIS CASOS, E CADA UM ESTÁ CERTO ONDE ESTÁ.

`O1` passou a emitir um caso por região, com a direção lida sobre os apoios
daquela região. Um sinal sem região declarada não funda caso nenhum — ele não
tem geografia para alegar — mas continua contando como apoio onde a região já
existe.

**Efeito medido:** `O1` foi de 11 para **17** casos, e `SALES_READY` de 1 para
**4**. Os três recuperados são exatamente as regiões cuja oportunidade a fusão
nacional estava apagando.

---

## 4b · O caso testemunha · `OPP_75C37DED9160`

Maçã × carpocapsa · Veneto. A auditoria o apontou como o único caso do pacote
que respondia às quatro perguntas comerciais, e que estava em `TO_VALIDATE` por
causa do defeito D2. Depois dos consertos, medido no pacote reconstruído:

| campo | valor |
|---|---|
| `OPPORTUNITY_STATE` | `OPPORTUNITY_CONFIRMED` · `BLOCKING_GATES` vazio |
| **`COMMERCIAL_PRIORITY`** | **`SALES_READY`** |
| `NEED_DIRECTION` | `POSITIVE_PRESSURE` |
| `NEED_EVIDENCE_ID` | `IT-CAN-D9582B1FD6` (boletim frutícola do Veneto) |
| `NEED_METHOD` | `CROP_FROM_SINGLE_CROP_DOCUMENT` |
| `NEED_EXCERPT` | «…reporta terceiro voo de *Cydia pomonella* terminado com **danos em aumento** também em pomares de manejo integrado.» |
| `COMMERCIAL_PRODUCT_COUNT` | **2** |
| `MATCHED_COMMERCIAL_PRODUCT_NAMES` | **Lamdex® Extra · MAVRIK SMART** |
| `CLAIM_GEOGRAPHY` | `REGION_VENETO` |
| `FIELD_GEOGRAPHY` | `['REGION_VENETO']` |
| `PRODUCT_AUTHORIZATION_GEOGRAPHY` | `['GEO_ITALY']` |
| `CLAIM_GEOGRAPHY_HOLDS` | `true` — «a observação cabe na geografia alegada e fala por ela» |
| `COMMERCIAL_WINDOW` | `ACT_NOW`, derivado de `SIGNAL_DATE` |
| `WHY_COMMERCIAL` | necessidade positiva corrente, produto do catálogo com rótulo no par, geografia que se sustenta e tempo para agir |

**Subiu, e subiu pelos quatro consertos ao mesmo tempo:** D2 abriu o portão A
(as três geografias deixaram de ser somadas); o par cultura × alvo passou a ser
o observado; o catálogo comercial passou a ser consultado; e a direção do texto
passou a ser lida — «danos em aumento» é `POSITIVE_PRESSURE`, e «voo terminado»
não é janela concluída.

**O que ele ainda não tem, e a ficha declara:** uma segunda família externa. É
um caso de **um publicador**. A régua não o exige — corroboração é amplificador
— mas a fragilidade fica escrita, e é exatamente onde a camada VOCI entraria
(há **14** vozes de maçã no pacote).

---

## 4c · O resultado, medido

`BUILD_ID` antes `V21-99226fbb90dcdbc2` · depois `V21-9776b29c58195ad6`.
Cadeia completa, `EXIT=0`, **0 violações** em QA, geografia e procedência,
**0 campos ainda só em português**.

| | antes | depois |
|---|---:|---:|
| total de oportunidades | 37 | **43** |
| `OPPORTUNITY_CONFIRMED` | 9 | **21** |
| `OPPORTUNITY_CANDIDATE` | 28 | 22 |
| com produto do catálogo comercial | *não medido* | **31 de 43** |

Saíram **7**, entraram **13**, permaneceram **30**. Todas as saídas e entradas
são `O1_FIELD_PRESSURE`, e cada uma tem razão factual (lista completa em
`data/samples/AUDITORIA-SOMBRA/V11-ANTES-E-DEPOIS.json`):

- **saíram por não serem par observado:** pera × ticchiolatura, maçã ×
  ticchiolatura (nenhum dos oito boletins de Emilia-Romagna recomenda nada
  contra ticchiolatura), tomate × oídio (a recomendação era sobre *radicchio*),
  maçã × percevejo (o alvo aparece só como «percevejo», fora do léxico);
- **saíram por virarem casos regionais:** videira × peronospora, videira ×
  *Scaphoideus* e videira × tignoletta, que eram um caso nacional cada e agora
  são um por região;
- **entraram** treze casos regionais, cada um com o apoio e a direção do próprio
  serviço regional.

### `COMMERCIAL_PRIORITY`

| | |
|---|---:|
| `SALES_READY` | **4** |
| `SALES_PREPARE` | **0** |
| `COMMERCIAL_WATCH` | **13** |
| `STRATEGIC_OPPORTUNITY` | **8** |
| `TO_VALIDATE` | **18** |

`SALES_PREPARE` em zero **não é um estado morto**: é o que os dados deram nesta
data de referência. Todo caso com necessidade positiva ou tinha janela para agir
(virou `SALES_READY`) ou não tinha produto comercial no par (caiu para
`TO_VALIDATE`). Nenhum caiu no meio.

### Os quatro `SALES_READY`

| ID | par | região | a frase que sustenta | produtos do catálogo |
|---|---|---|---|---|
| `OPP_1A9962A3A2BC` | videira × botrite | Emilia-Romagna | «*Vite/botrite: intervir em pré-colheita com Fenhexamid*» | BANJO |
| `OPP_0C8669B0E849` | videira × tignoletta | Emilia-Romagna | «*ao ultrapassar 5% de cachos infestados, intervir*» | Lamdex® Extra |
| `OPP_75C37DED9160` | maçã × carpocapsa | Veneto | «*danos em aumento também em pomares de manejo integrado*» | Lamdex® Extra · MAVRIK SMART |
| `OPP_9C600748BB1B` | milho × piralide | Friuli-V.G. | «*tratamento insecticida justificado quando posturas > 3 por 100 plantas*» | Lamdex® Extra |

E os mesmos pares, noutra região, **corretamente fechados**: videira × botrite
na Toscana é `ACTION_SUSPENDED`; milho × piralide na Lombardia é
`TREATMENT_PROHIBITED`. Os dois são `TO_VALIDATE`, e a régua diz por quê.

### Os 9 VERIFIED do V1, na régua comercial

| | |
|---|---:|
| `SALES_READY` | **0** |
| `SALES_PREPARE` | **0** |
| `COMMERCIAL_WATCH` | **3** (os três de preço de cereal) |
| `STRATEGIC_OPPORTUNITY` | **6** (as seis datas europeias) |

**A auditoria continua de pé.** Corrigir os defeitos não transformou nenhuma das
nove em venda — porque nenhuma delas nomeia um problema agronômico. O que mudou
é que agora elas dizem isso de si mesmas.

### Os que eram `TO_VALIDATE` no V1 e subiram comercialmente

**12** casos: **2** para `SALES_READY` (maçã × carpocapsa no Veneto e milho ×
piralide na FVG — os dois que a auditoria apontara) e **10** para
`COMMERCIAL_WATCH`, dos quais 7 são os `O4` que o defeito D1 mantinha
inconfirmáveis.

### Qualidade da convergência

| famílias externas | antes | depois |
|---|---:|---:|
| 1 | 30 | 27 |
| 2 | 7 | **16** |
| 3 ou mais | 0 | 0 |

`SALES_READY` sustentado por: **2 casos com uma família forte**, **2 casos com
duas**. A régua não exigiu duas de ninguém — e os dois de família única passaram
porque necessidade, portfólio, geografia e tempo fecham.

**Continua não havendo nenhum caso com três famílias.** É o mesmo teto da
auditoria, e é onde a camada VOCI entraria.

### Direção da necessidade, nas 43

`UNKNOWN` 26 (os arquétipos sem alvo) · `POSITIVE_PRESSURE` 5 ·
`NEUTRAL_MENTION` 4 · `ACTION_SUSPENDED` 3 · `NO_ACTION_RECOMMENDED` 2 ·
`TREATMENT_PROHIBITED` 2 · `WINDOW_CONCLUDED` 1.

**Oito casos que o V1 lia como pressão de campo são, medidos, documentos que
mandam parar.**

### Um resíduo honesto

Dois dos quatro `SALES_READY` (os de Emilia-Romagna) são
`OPPORTUNITY_CANDIDATE`, não `CONFIRMED`: carregam
`A_GEOGRAFIA` e `F_PROCEDENCIA` abertos. A causa **não** é o sinal de campo — é
o registro de janela (`IT-WIN-001`, `IT-WIN-002`), que cobre várias regiões e
tem `PROVENANCE_STATE: UNRECOVERABLE`.

Não mexi no portão para fazer as duas colunas concordarem. **É exatamente o que
a missão pediu:** um caso pode ser comercialmente pronto e ainda ter um portão
de evidência aberto, e as duas coisas devem aparecer lado a lado.

---

## 5 · DURUM WHEAT · veredito

**`HONEST_UNKNOWN`, com a causa localizada — e não é o que a auditoria supunha.**

A auditoria da régua registrou *«0 rótulos com `CROP_DURUM_WHEAT` — a
normalização colapsa frumento em `CROP_WHEAT_GENERIC`»*. Perguntando ao dado, a
causa é outra:

| | |
|---|---:|
| produtos ADAMA no registro italiano com `CROP_DURUM_WHEAT` declarado | **14** |
| desses, quantos têm **algum** par de rótulo extraído | **0** |
| pares de rótulo cujo `CROP_ON_LABEL` é `FRUMENTO` | **176** |
| pares de rótulo com trigo duro | **0** |

Os 14 são TOPIK 240 EC, TOPIK 80 EC, VIP, VIP 80 EC, TRACE, RAVENAS, CELIO,
CELIO 80 EC, HAWK, MAKURI, **SEEDRON**, DICURAN PLUS, **EDAPTIS** e MEZAYO —
todos com `AUTHORIZATION_HOLDER: ADAMA ITALIA S.R.L.`, e **SEEDRON e EDAPTIS
estão no catálogo comercial dos 51**.

Então:

- **A** — existe identidade equivalente comprovável? **NÃO SEI, e não se infere.**
  Os 176 rótulos que dizem `FRUMENTO` dizem literalmente isso: a linha da tabela
  de uso é «frumento, segale, triticale, orzo e avena». Mapear
  `frumento → frumento duro` seria inventar o que a etiqueta não diz.
- **B** — é defeito de normalização? **NÃO.** O léxico já distingue
  `CROP_DURUM_WHEAT` de `CROP_SOFT_WHEAT` e de `CROP_WHEAT_GENERIC`, e a camada
  de **produto** usa essa distinção corretamente nos 14.
- **C** — não existe rótulo ADAMA correspondente? **NÃO SE PODE DIZER.** É uma
  **lacuna de cobertura da extração de rótulos**: as tabelas de uso desses 14
  registros nunca foram extraídas.

    A AUSÊNCIA NÃO ESTAVA NA NORMALIZAÇÃO NEM NO MERCADO.
    ESTAVA NA COLETA — E UMA LACUNA DE COLETA NÃO É UM FATO SOBRE O MUNDO.

**O que resolve:** extrair as tabelas de uso dos 14 registros em
`fitosanitari.salute.gov.it` (o `LABEL_URL` de cada um já está no pacote). É
coleta, e está fora desta missão. **Nada foi mapeado.**

---

## 5b · A suíte

| | antes | depois |
|---|---:|---:|
| testes executados | 658 | **692** (+34 da camada comercial) |
| falhas | 13 | **7** |
| erros | 2 | **2** |

**Nenhuma regressão nova.** As 7 falhas e os 2 erros que restam são anteriores a
esta missão (procedência de amostras em `data/samples/`, gate de import ES,
sentinela de contagem do handoff). As 6 falhas que sumiram eram desvio de
marcador de métrica, resolvido com a ferramenta que o próprio teste manda rodar
(`scripts/metricas_canonicas.py --sync`) — o desvio tinha piorado porque os meus
34 testes mudaram a contagem.

---

## 6 · O que continua valendo, e não foi afrouxado

- `CLIENT_SAFE = false` em **todas**, sem exceção (prova
  `test_client_safe_continua_falso_em_todas`).
- Nenhum campo infere revenda, sell-in, sell-out, pedido, estoque, margem,
  pipeline ou intenção de compra — e toda oportunidade carrega
  `COMMERCIAL_DOES_NOT_PROVE` dizendo isso (duas provas de invariante).
- Data regulatória ≠ risco comercial · comunicação de concorrente ≠ participação
  de mercado · ciência ≠ presença corrente no campo · literatura de resistência ≠
  incidência corrente · voz pública ≠ tendência regional · relação de portfólio ≠
  autorização de rótulo.
- **Pressão agronômica não é demanda.** É oportunidade comercial externa a
  examinar.

---

## 7 · O que esta versão NÃO consertou

- **A camada VOCI continua fora.** 79 vozes carregadas, zero indexadas. Os três
  bloqueios estão medidos em [`VOCI-COMMERCIAL-READINESS.md`](VOCI-COMMERCIAL-READINESS.md).
- **O léxico de alvos cobre menos da metade do que os boletins nomeiam.** Dos
  **483** termos de praga citados nos 86 sinais client-safe, **296 não têm
  `ISSUE_ID`** — *Colpo di fuoco batterico*, *Maculatura bruna*, *Glomerella*,
  *Psilla*, *Monilia*, *Mal dell'esca*, *Ragnetto rosso*, *Cydia molesta*…
  Esse é o teto medido da cobertura de `O1`, e ele não é modelagem: é vocabulário.
- **A inversão de modo de ação em O3 continua.** A resistência italiana de
  *Echinochloa crus-galli* documentada é **aos inibidores da ACCase (grupo A)**,
  e o arquétipo cita `MODOS_DE_ACAO: ['A']` como relevância ADAMA. A régua
  comercial não deixa o caso subir — falta necessidade positiva corrente — mas
  o motor continua sem comparar o MoA resistido com o MoA oferecido.
- **A trava de tradução tinha vocabulário curto**, e reprovou três traduções
  corretas minhas: `NEG_IT` conhecia `mancano` e `mancanza` mas não `manca` — a
  terceira pessoa do singular, a forma mais comum; `NEG_EN` conhecia `lack` e
  `absence` mas não `missing` nem `absent`. Corrigido **na lista, nunca na
  frase** — é o defeito que o próprio arquivo já documentava duas vezes
  («*uma trava que reprova o certo ensina a ignorar trava*»).
- **O `BUILD_ID` do zip versionado não é reproduzido pela cadeia**, embora os 30
  arquivos do `DESIGN-INGEST` sejam idênticos registro a registro. O zip carrega
  `V21-99226fbb90dcdbc2`; a cadeia converge para outro valor e o mantém estável
  entre execuções. É anterior a esta missão e não afeta contagem nenhuma.
