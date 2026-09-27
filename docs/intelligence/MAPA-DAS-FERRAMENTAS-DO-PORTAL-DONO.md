# 25. MAPA DAS FERRAMENTAS DO PORTAL

O portal SINTONIA ITÁLIA não é uma coleção de dashboards independentes.

Cada ferramenta é uma **forma específica de consumir inteligência já produzida pelo sistema**.

Fluxo conceitual:

SOURCES  
→ COLLECTION  
→ SALA DE ESPERA  
→ INTELLIGENCE  
→ CROSSINGS / SIGNALS / FINDINGS  
→ INTELLIGENCE TOOLS  
→ CASCO / PORTAL

O CASCO nunca deve tentar produzir o cruzamento.

Ele deve saber **qual cruzamento espera receber** para conseguir representar corretamente cada ferramenta.


# 26. OPPORTUNITY RADAR

## O QUE É

É a ferramenta que mostra:

**“Onde existe uma oportunidade comercial ou estratégica relevante agora?”**

É a camada mais acionável do portal.

Não é simplesmente uma lista de notícias.

Não é uma previsão genérica.

Não é Future Radar.

Uma oportunidade deve surgir quando várias dimensões independentes convergem de maneira defensável.


## CRUZAMENTO PRINCIPAL

O Opportunity Radar deve consumir cruzamentos entre, quando disponíveis:

CROP / AGRONOMIC WINDOW  
× CLIMATE  
× FIELD SIGNALS  
× LABEL / REGULATORY  
× ADAMA PORTFOLIO  
× MARKET  
× COMPETITOR  
× SCIENCE  
× GEOGRAPHY

Nem toda oportunidade precisa obrigatoriamente conter todas essas dimensões.

Mas ela deve nascer de um mecanismo de Intelligence que determine quais sinais realmente convergem.


## EXEMPLO CONCEITUAL

Não produzir isto no frontend:

“Vai chover → vender fungicida.”

O cruzamento esperado da Intelligence seria algo semelhante a:

chuva / umidade prevista  
× cultura em estágio suscetível  
× risco agronômico conhecido  
× região afetada  
× produto ADAMA autorizado para cultura + alvo  
× janela válida de aplicação  
× evidências disponíveis

→ possível oportunidade


## O CASCO DEVE MOSTRAR

- qual é a oportunidade;
- cultura;
- problema/alvo;
- região;
- janela temporal;
- motivo;
- sinais que convergiram;
- produtos ADAMA relacionados;
- limitações;
- evidências;
- data de atualização.

Se a Intelligence não classificou algo como oportunidade:

o CASCO não pode promovê-lo a oportunidade sozinho.


# 27. FUTURE RADAR

## O QUE É

Responde:

**“O que está surgindo hoje que pode se tornar relevante amanhã?”**

O Future Radar procura sinais antecipados.

Não precisa existir oportunidade comercial imediata.

Sua função é preparação estratégica.


## CRUZAMENTO PRINCIPAL

SCIENCE  
× FIELD / TECHNICAL SIGNALS  
× CLIMATE / ENVIRONMENTAL CHANGE  
× RESISTANCE  
× EMERGING PESTS / DISEASES  
× REGULATORY MOVEMENT  
× RESEARCH PROJECTS  
× GEOGRAPHY

Opcionalmente:

× PORTFOLIO

para entender relação futura com capacidades da ADAMA.


## PODE IDENTIFICAR

- resistência emergente;
- nova pressão fitossanitária;
- mudança geográfica;
- nova tecnologia;
- novas linhas de pesquisa;
- mudança de prática agrícola;
- tendência regulatória;
- problema agronômico crescente.


## NÃO CONFUNDIR COM OPPORTUNITY RADAR

Future Radar:

> “isso merece acompanhamento.”

Opportunity Radar:

> “há condições suficientes para uma oportunidade acionável.”

O CASCO deve deixar essa diferença visualmente clara.


# 28. CROP WINDOWS

## O QUE É

É o **relógio agronômico do Sintonia**.

Responde:

**“O que está acontecendo com determinada cultura agora e quais janelas agronômicas estão chegando?”**


## CRUZAMENTO PRINCIPAL

CROP  
× PHENOLOGY / BBCH  
× GEOGRAPHY  
× TIME  
× AGRONOMIC PROBLEM WINDOWS

Quando houver dados suficientes:

× CLIMATE


## DEVE PERMITIR ENTENDER

Para uma cultura/região:

- estágio provável;
- janela atual;
- próxima janela;
- problemas normalmente associados;
- período de atenção;
- sazonalidade.


## IMPORTANTE

Crop Windows não deve inventar fenologia precisa de uma lavoura específica quando o sistema só conhece uma janela regional.

A granularidade visual deve respeitar a granularidade do dado.


# 29. CLIMATE / APPLICATION WINDOWS

Quando existir como função ou componente do portal, responde:

**“Como as condições meteorológicas alteram risco agronômico e janela de intervenção?”**


## CRUZAMENTO PRINCIPAL

WEATHER OBSERVED  
× WEATHER FORECAST  
× GEOGRAPHY  
× CROP  
× PHENOLOGY  
× DISEASE / PEST CONDITIONS  
× APPLICATION CONDITIONS

E, posteriormente:

× PORTFOLIO / LABEL


## EXEMPLOS

umidade elevada  
× temperatura adequada  
× cultura suscetível  
× estágio fenológico

→ condição favorável a determinado problema

ou:

vento  
× chuva  
× temperatura

→ janela inadequada ou adequada para determinada operação


## REGRA

Clima isolado não é oportunidade.

Ele é uma variável de contexto usada por outros cruzamentos.


# 30. LABEL INTELLIGENCE

## O QUE É

Responde:

**“O que a ADAMA está legalmente autorizada a fazer com determinado produto?”**

É inteligência regulatória aplicada ao portfólio.


## MATÉRIA-PRIMA PRINCIPAL

REGULATORY DATA  
× PRODUCT  
× CROP  
× TARGET  
× COUNTRY  
× DOSE  
× PHI  
× RESTRICTIONS  
× AUTHORIZATION STATUS  
× VERSION / TIME


## CRUZAMENTOS IMPORTANTES

LABEL  
× PORTFOLIO

LABEL  
× CROP

LABEL  
× OPPORTUNITY

LABEL  
× GEOGRAPHY


## DEVE MOSTRAR

- produto;
- cultura;
- alvo;
- autorização;
- dose;
- restrições;
- PHI quando existente;
- país;
- versão/data;
- alterações relevantes.


## REGRA ABSOLUTA

O CASCO nunca pode inferir autorização.

Se o vínculo produto × cultura × alvo não estiver provado:

UNKNOWN / NÃO PROVADO.


# 31. PORTFOLIO INTELLIGENCE

## O QUE É

Responde:

**“Quais capacidades reais a ADAMA possui para responder a determinada necessidade?”**

Não é catálogo comercial.

É a representação inteligente do portfólio em relação às necessidades detectadas.


## CRUZAMENTO PRINCIPAL

PRODUCT  
× LABEL  
× CROP  
× TARGET  
× COUNTRY  
× MODE OF ACTION / CAPABILITY

Depois pode receber:

× OPPORTUNITY  
× CROP WINDOW  
× FUTURE SIGNAL


## EXEMPLO

problema agronômico X  
× cultura Y  
× Itália  
× produto autorizado

→ capacidade real do portfólio


## NÃO FAZER

Nunca sugerir produto simplesmente porque semanticamente parece relacionado.

Relação de portfólio deve ser provada.


# 32. MARKET PULSE / MARKET INTELLIGENCE

## O QUE É

Responde:

**“O que está mudando no mercado agrícola e por que isso pode importar?”**


## CRUZAMENTO PRINCIPAL

PRICE  
× PRODUCTION  
× AREA  
× YIELD  
× IMPORT / EXPORT  
× STOCK  
× DEMAND  
× COST  
× HARVEST  
× TIME  
× GEOGRAPHY


## PODE CRUZAR COM

CROP  
× MARKET

MARKET  
× PORTFOLIO

MARKET  
× OPPORTUNITY

MARKET  
× COMPETITOR


## DEVE MOSTRAR

- mudança observada;
- magnitude quando conhecida;
- período;
- região;
- possíveis implicações;
- evidências.


## CUIDADO

Correlação não significa causalidade.

A interface não deve dizer:

“X aconteceu por causa de Y”

a menos que a Intelligence tenha evidência suficiente.


# 33. FIELD VOICES

## O QUE É

Responde:

**“O que técnicos, pesquisadores, produtores ou outras pessoas relevantes estão relatando no campo?”**

É voz humana estruturada.

Não deve ser tratada automaticamente como prova de incidência.


## MATÉRIA-PRIMA

TRANSCRIPTS  
× TECHNICAL REPORTS  
× INTERVIEWS  
× FIELD OBSERVATIONS  
× PEOPLE  
× DATE  
× LOCATION


## CRUZAMENTO PRINCIPAL

FIELD VOICE  
× TOPIC / PROBLEM  
× CROP  
× GEOGRAPHY  
× TIME


## PODE CONTRIBUIR PARA

Future Radar

Opportunity Radar

Scientific Intelligence

Regional Intelligence


## REGRA

“Um agrônomo disse que há muita doença X”

não significa automaticamente:

“há alta incidência de doença X na região.”

O CASCO deve preservar essa diferença.


# 34. COMPETITOR WATCH

## O QUE É

Responde:

**“O que concorrentes estão fazendo, comunicando ou posicionando?”**


## MATÉRIA-PRIMA

COMPETITOR CONTENT  
× PRODUCT  
× CAMPAIGN  
× MESSAGE  
× CROP  
× TARGET  
× COUNTRY  
× TIME


## CRUZAMENTO PRINCIPAL

COMPETITOR  
× CROP

COMPETITOR  
× PRODUCT CATEGORY

COMPETITOR  
× REGION

COMPETITOR  
× TIME

E, quando relevante:

× ADAMA PORTFOLIO  
× MARKET  
× OPPORTUNITY


## DEVE MOSTRAR

- movimento;
- concorrente;
- contexto;
- cultura/alvo;
- período;
- geografia;
- evidência original.


## NÃO É

Uma ferramenta para dizer automaticamente:

“concorrente fez X, então ADAMA deve fazer Y.”

A decisão estratégica continua pertencendo às pessoas.


# 35. SCIENTIFIC INTELLIGENCE

## O QUE É

Não é biblioteca de papers.

Responde:

**“Que conhecimento científico novo pode alterar uma decisão agronômica ou estratégica?”**


## MATÉRIA-PRIMA

PAPERS  
× RESEARCH PROJECTS  
× AUTHORS  
× INSTITUTIONS  
× TOPICS  
× CROP  
× PEST / DISEASE  
× RESISTANCE  
× ACTIVE INGREDIENT  
× TIME


## CRUZAMENTO PRINCIPAL

SCIENCE  
× TOPIC  
× CROP  
× PROBLEM  
× GEOGRAPHY  
× TIME


## PODE ALIMENTAR

Future Radar

Opportunity Radar

Portfolio Intelligence

Crop Intelligence


## O CASCO DEVE PRIORIZAR

- descoberta;
- significado;
- aplicabilidade;
- força da evidência;
- contexto;
- origem científica.

Não simplesmente:

“Paper X publicado em revista Y.”


# 36. GEOGRAPHY / REGIONAL PULSE

Quando implementado, responde:

**“O que está acontecendo nesta região?”**


## CRUZAMENTO PRINCIPAL

FACT LOCATION  
× TIME  
× CROP  
× FIELD  
× CLIMATE  
× SCIENCE  
× MARKET  
× COMPETITOR  
× OPPORTUNITIES


## OBJETIVO

Transformar geografia em uma lente transversal.

Exemplo:

Emilia-Romagna

→ culturas relevantes  
→ janelas atuais  
→ sinais de campo  
→ clima  
→ mercado  
→ concorrência  
→ oportunidades


## REGRA

SOURCE_LOCATION não é FACT_LOCATION.

Nunca colocar no mapa como fato um local conhecido apenas porque a fonte está sediada naquele local.


# 37. SIGNAL ARCHIVE / INTELLIGENCE ARCHIVE

## O QUE É

É memória navegável dos sinais e findings produzidos pela Intelligence.

Responde:

**“O que o sistema já detectou anteriormente sobre este assunto?”**


## ORIGEM

SIGNALS  
× FINDINGS  
× TIME  
× STATUS  
× TOPIC  
× GEOGRAPHY


## NÃO É

repositório bruto de Collection.

Não deve misturar:

documentos coletados

com

inteligência produzida.


# 38. EVIDENCE VIEW

Pode ser uma ferramenta própria ou camada transversal.

Responde:

**“Por que o Sintonia acredita nisso?”**


## DEVE CONSEGUIR MOSTRAR

Finding

→ Crossing

→ Signals

→ Observations

→ Sources


Quando a arquitetura permitir, deve ser possível caminhar da conclusão até a evidência original.


# 39. ASK SINTONIA / SEARCH

Quando implementado, responde a perguntas usando o conhecimento admitido no sistema.

Não é um chatbot genérico.


## FLUXO ESPERADO

PERGUNTA

→ RETRIEVAL / INTELLIGENCE

→ RESULTADOS

→ EVIDÊNCIAS

→ RESPOSTA


## DEVE DIFERENCIAR

- dado encontrado;
- inferência;
- ausência de dado;
- incerteza.


## REGRA

Se não houver evidência:

não completar por criatividade.


# 40. RELAÇÃO ENTRE AS FERRAMENTAS

As ferramentas não devem viver isoladas.

Um mesmo objeto pode aparecer em diversas lentes.

Exemplo:

Scientific Intelligence detecta:

resistência emergente.

Isso pode gerar:

→ Future Radar

Depois, meses mais tarde:

Field Voices detecta relatos compatíveis.

Crop Windows entra em período crítico.

Clima cria condições favoráveis.

Label Intelligence confirma um produto ADAMA autorizado.

Portfolio Intelligence encontra capacidade correspondente.

A Intelligence pode então produzir:

→ Opportunity Radar


Portanto:

SCIENCE
→ FUTURE SIGNAL

FIELD
→ CONFIRMAÇÃO CONTEXTUAL

CROP + CLIMATE
→ JANELA

LABEL + PORTFOLIO
→ CAPACIDADE ADAMA

MARKET + COMPETITOR
→ CONTEXTO COMERCIAL

CONVERGÊNCIA
→ OPPORTUNITY


Essa lógica deve orientar a navegação do CASCO.


# 41. A HOME NÃO PRODUZ INTELIGÊNCIA

A Home é uma síntese.

Ela pode receber:

- oportunidades prioritárias;
- sinais futuros relevantes;
- mudanças regulatórias;
- janelas agronômicas;
- movimentos de mercado;
- movimentos concorrentes;
- novidades científicas.

Mas essas informações devem vir das respectivas ferramentas/intelligence.

A Home não deve ter regras próprias escondidas.


# 42. ACTION MAP

Quando o portal usar Action Map ou camada equivalente, ele deve ser consequência da inteligência.

Pode apresentar algo como:

ACONTECIMENTO

→ POR QUE IMPORTA

→ JANELA

→ RELAÇÃO COM ADAMA

→ EVIDÊNCIAS

→ POSSÍVEIS ÁREAS INTERNAS ENVOLVIDAS


Nunca transformar isso automaticamente em uma ordem:

“ADAMA deve fazer X.”

O portal informa e estrutura.

A decisão é humana.


# 43. PRINCÍPIO DE COMPOSIÇÃO

Uma ferramenta do portal deve ser definida sempre por quatro contratos:

### A. PERGUNTA

Qual pergunta esta ferramenta responde?

### B. ENTRADA

Qual tipo de Intelligence / Crossing / Signal ela recebe?

### C. REPRESENTAÇÃO

Como o usuário entende esse resultado?

### D. PROVENIÊNCIA

Como ele consegue verificar de onde veio?

Se uma nova ferramenta não consegue responder claramente esses quatro pontos:

ela ainda não está suficientemente definida para virar CASCO.


# 44. PROIBIÇÃO DE CROSSING NO FRONTEND

Não implemente no JavaScript/UI regras como:

IF chuva > X
AND cultura = tomate
THEN oportunidade = fungicida

Isso pertence à Intelligence.

O CASCO deve receber algo semanticamente equivalente a:

OPPORTUNITY_FINDING {
  opportunity_id,
  title,
  crop,
  target,
  geography,
  time_window,
  contributing_signals,
  portfolio_relationships,
  evidence,
  limitations,
  status
}

e representar isso.

A estrutura exata deve obedecer ao contrato real existente no repositório.

Este exemplo não autoriza criar schema novo.


# 45. SE A FERRAMENTA EXISTIR VISUALMENTE MAS O CROSSING NÃO EXISTIR

Classifique:

`CASCO SEM CONTRATO DE INTELLIGENCE`

Não crie inteligência artificialmente para preencher a página.

Reporte:

- nome da ferramenta;
- pergunta que deveria responder;
- entrada necessária;
- entrada que realmente existe;
- diferença;
- provável Intelligence responsável.


# 46. REGRA MAIS IMPORTANTE DAS FERRAMENTAS

O portal não é:

dados → tela.

O fluxo correto é:

DADOS

→ INTELLIGENCE

→ CRUZAMENTOS

→ FINDINGS / SIGNALS

→ FERRAMENTAS

→ CASCO


Sempre preserve essa separação.