# CAMADA DE VOZ — ESPANHA

**Missão 10A-ES · país fechado antes do próximo · França e Itália não foram abertas.**

Data de referência: **2026-08-29** · Cultura-âncora: **olivar** · Problema-âncora: **repilo
(*Venturia oleaginea*)**

---

## A. A PERGUNTA

A voz pública espanhola **muda ou reforça** uma decisão que o SINTONIA já consegue tomar
com registro, campo e ciência?

A resposta curta está no fim, em §V. Antes dela, o que foi medido.

---

## B. ORDEM CANÔNICA DE DESCOBERTA — E O QUE ELA CUSTOU

A missão fixou a ordem: **portão → censo → vídeo → pesquisadores → LinkedIn → cooperativas →
concorrentes → mídia técnica → Instagram → autoridades → reconciliação.**

Ela foi seguida no desenho. **Duas correções de 2026-08-29, vindas da auditoria adversarial:**

1. **O vídeo pagou — mas "antes de qualquer gasto em LinkedIn" era afirmação sem lastro.**
   O YouTube entregou 705.149 caracteres de fala técnica, e isso continua sendo o melhor
   retorno por unidade de custo da rodada. O que **não** se sustenta é a ordem: a busca de
   posts do LinkedIn e a coleta de vídeo saíram do **mesmo orçamento**, sem carimbo que as
   separe, e o registro git coloca a **camada científica antes do vídeo** (`3f65e00` corpus
   científico precede `3d963cd` YouTube). **Nada no repositório registra hora ou sequência de
   coleta por camada**, então a ordem de execução não é auditável — só a de desenho.
2. **O Instagram por último salvou dinheiro — e essa continua verificável.** Ele foi testado
   com 60 itens e reprovado por medida (§H), e o crédito que sobrou financiou a busca por
   cargo. A ordem aqui é auditável porque o teste do Instagram e a decisão de não escalar
   estão ambos registrados com o gasto medido.

> **Lição que virou requisito:** afirmar ordem de coleta exige **carimbo por camada**.
> `RUN_ID` agrupa registros entre si mas não os situa no tempo. Enquanto não houver manifesto
> de execução com data por camada, nenhuma afirmação de "X veio antes de Y" deve ser
> publicada.

**Apify não é uma camada de fonte. É uma ROTA DE COLETA** sobre camadas que existem sem ela.

---

## C. O QUE FOI COLETADO

| camada | origens únicas | conteúdo | estado |
|---|---:|---|---|
| **Ciência** (OpenAlex) | 380 instituições · **152 pesquisadores** ES | 1.771 trabalhos 2019-2026 | PROVED |
| **Vídeo** (YouTube) | **<!--M:VOICE_ES_YOUTUBE_ORIGINS-->157<!--/M--> canais** | 252 vídeos · 15 transcrições · 705.149 caracteres | PROVED |
| **LinkedIn** | **<!--M:VOICE_ES_LINKEDIN_ORIGINS-->202<!--/M--> perfis enriquecidos** · 179 declaram ES | 372 posts únicos (de 472 brutos) | PROVED (identidade) / PARTIAL (conteúdo) |
| **Mídia técnica + associações** | 18 rotas testadas · **<!--M:VOICE_ES_MEDIA_ROUTES_PROVED-->8<!--/M--> provadas** | 155 itens datados | PARTIAL |
| **Concorrentes** | 11 origens de indústria | 26 posts | PARTIAL |
| **Instagram** | 32 contas agronômicas | 60 itens | **FAILED_WITH_REASON** |

---

## D. IDENTIDADE ANTES DE CONTEÚDO — E O QUE ISSO CUSTOU EM NÚMEROS

A regra da missão: *não descobrir identidade apenas pelo post.* Ela foi aplicada
literalmente, e o preço dela é visível.

**Papel de uma PÁGINA** vem de `companyType` + `pageType` + `industries` — campos
estruturados que a própria origem declara.
**Papel de uma PESSOA** vem do `headline` + cargo atual declarado.

**Nunca entram na decisão de papel:** o nome da conta · a foto · o estilo do texto · o
idioma · a prosa livre (`about` / `description`).

### Por que a prosa livre foi excluída — três erros medidos

Um classificador anterior lia a prosa. Ele produziu, em 40 perfis:

| erro | causa |
|---|---|
| `Oleo Revista` → **RESEARCHER** | a palavra "investigador" aparecia numa notícia citada |
| `ASCENZA España` → **RESEARCH_INSTITUTION** | o token `imida` casou **dentro de um nome químico** (ftalimida) |
| `IAS-CSIC` → **PUBLIC_AUTHORITY** | "Consejería" aparecia como terceiro citado |
| pessoas → **COMPANY** | por trabalharem numa `S.L.` |

Aquele classificador reportava **100% de cobertura de papel**. A cobertura era falsa: os
papéis estavam errados. Trocado pelos campos estruturados, a cobertura caiu para o número
verdadeiro — **<!--M:VOICE_ES_LINKEDIN_ROLE_COVERAGE-->67<!--/M-->% (120 de 179)** — com **17 AMBIGUOUS** e **42 NOT_DECLARED** visíveis.

**Cobertura que sobe porque o classificador ficou permissivo não é cobertura. É ruído
contado como sinal.**

### AMBIGUOUS é um estado real

Quando dois papéis distintos são declarados — *"Gerente de Olipe | OLIVARERA LOS PEDROCHES
SCA"* é `COMPANY_EXECUTIVE` **e** `COOPERATIVE` — não se desempata por ordem de regex.
Declara-se ambíguo. São 17 casos.

### O preço mais caro da regra

**`Grupo de Aerobiología. Universidad de Córdoba`** publicou o post mais relevante de todo o
corpus LinkedIn: detecção de esporos de *Venturia oleaginea*. O perfil tem `headline` vazio.

Pela regra, ele sai como **NOT_DECLARED**. E sai mesmo — o nome da conta diz "Universidad de
Córdoba", e o nome não decide papel.

**Isto é o custo da regra, não uma falha dela.** A identidade dessa origem tem de vir de
outra camada — e vem: o mesmo grupo aparece no corpus científico OpenAlex com afiliação
declarada. **Identidade se resolve cruzando camadas, nunca lendo o post com mais boa
vontade.**

---

## E. AS DUAS ROTAS DE DESCOBERTA NÃO ENTREGAM A MESMA COISA

| | POST_SEARCH | TITLE_SEARCH |
|---|---|---|
| critério de entrada | **publicou** sobre o tema | **declara** o cargo |
| perfis | 115 | 87 |
| vozes técnicas verificadas | 16 | 51 |
| viés | favorece páginas de empresa | favorece quem preenche o cargo |
| geografia | livre | **pedida na consulta** |

Das 92 origens ES da rota de posts, **42 eram páginas de empresa (46%)**. A conclusão é da
camada, não do método: **no LinkedIn espanhol, quem publica sobre olivar é sobretudo
fornecedor.** A voz técnica individual existe, mas não é ela que domina o feed por termo.

Foi por isso que a segunda rota foi aberta.

---

## F. PUBLIC_TECHNICAL_VOICE — <!--M:VOICE_ES_PUBLIC_TECHNICAL_VOICES-->67<!--/M--> verificadas

**Definição:** país declarado ES · papel declarado técnico ou institucional · tópico agrícola
declarado.

**Não é INFLUENCER.** Alcance não entra na definição, em nenhum ponto.

| papel | n |
|---|---:|
| TECHNICAL_ADVISER | 52 |
| PUBLIC_AUTHORITY | 4 |
| RESEARCHER | 3 |
| EDUCATION_INSTITUTION | 2 |
| TECHNICAL_MEDIA | 2 |
| COOPERATIVE | 2 |
| PUBLIC_RESEARCH_INSTITUTION | 1 |
| PRODUCER_ORGANISATION | 1 |

A meta era 20+. São 67. **E o número maior é o menos informativo dos dois.**

### QUANTIDADE NÃO É REPRESENTATIVIDADE

- **52 das 67** são `TECHNICAL_ADVISER` trazidos por **filtro de cargo**. O filtro achou
  quem preenche o campo, não quem é relevante.
- **44 das 67** estão na Andaluzia porque **a Andaluzia foi pedida** em 3 das 11 consultas.
  A distribuição geográfica desta tabela mede o **desenho da consulta**, não o território.
- Só **<!--M:VOICE_ES_OLIVE_TECHNICAL_VOICES-->16<!--/M-->** declaram tópico `OLIVE`. Só **7** declaram `PLANT_HEALTH`.

**O número acionável para o Lab A não é <!--M:VOICE_ES_PUBLIC_TECHNICAL_VOICES-->67<!--/M-->. É <!--M:VOICE_ES_OLIVE_TECHNICAL_VOICES-->16<!--/M-->.** E dos 16, quatro são institucionais
(cooperativa, DOP, fundação, revista) e onze são assessores técnicos individuais.

---

## G. MÍDIA TÉCNICA E ASSOCIAÇÕES — 8 de 18 rotas

18 rotas públicas testadas. Nenhuma é documentada como API pública: todas são
**PUBLIC APPLICATION ROUTE** (feed).

| estado | n | o que significa |
|---|---:|---|
| PROVED | 8 | devolve itens datados |
| FAILED_WITH_REASON | 6 | ver abaixo |
| NOT_REACHED | 4 | 404 / 403 / gateway |

**HTTP 200 não bastou — de novo.** Seis rotas devolveram **200 com zero `<item>`**: são
páginas HTML, não feeds. Contar 200 como sucesso teria inventado seis fontes vivas.

**Três certificados não validam** (CITOLIVA, COAG, eComercio Agrario). Isso ficou registrado
como **estado da fonte**. A verificação **não** foi desligada para contornar.

A melhor rota — **Oleo Revista** — devolve 50 itens datados, **29 deles on-topic**. Suficiente
para um relógio de publicação. Insuficiente para censo do setor.

---

## H. INSTAGRAM — reprovado por medida, não por preconceito

A missão pediu julgamento empírico. Ele foi feito: 3 hashtags, 60 itens.

| hashtag | itens | agronômicos | contas |
|---|---:|---:|---:|
| `#olivar` | 20 | 20 | 18 |
| `#sanidadvegetal` | 20 | 19 | 15 |
| `#repilo` | 20 | **0** | **1** |

**`#repilo` está 100% capturada por um homônimo comercial:** `repilouk`, empresa britânica
de gestão de avaliações online. Vinte itens, zero agronomia.
**O nome da doença também é uma marca. Casar termo não é casar assunto — e está muito longe
de ser identidade.**

**Idioma não é país.** Em `#sanidadvegetal`, as contas mais frequentes declaram México
(`cesavegro`), Argentina (`argenpapa`) e LatAm (`agrolatam`). Todas escrevem em espanhol.

**A medida decisiva:** das 32 contas agronômicas, **24 não declaram país nenhum**, 3 declaram
fora da Espanha, **<!--M:VOICE_ES_INSTAGRAM_ACCOUNTS_DECLARING_ES-->5<!--/M--> declaram Espanha**.

**Veredito `INSTAGRAM_ES` = FAILED_WITH_REASON.** Não por falta de volume — 39 de 60 itens são
agronômicos. Falha na **identidade**, que é o primeiro requisito.
**Reabrir apenas se** outra camada fornecer uma lista de contas ES já identificadas. Aí o
Instagram vira conteúdo sobre identidade conhecida, não descoberta.

---

## I. CONCORRENTES — uma observação, com o denominador à vista

11 origens de indústria de proteção de cultivos, 26 posts.

> **Correção de 2026-08-29.** Este documento publicou antes **14 origens e 54 posts**. Os dois
> números estavam inflados, por duas causas distintas que vale separar:
>
> 1. **Sem dedupe estrutural: 54 → 29.** Dos 472 posts do corpus, **100 eram o mesmo
>    `POST_ID`** devolvido por consultas diferentes. Quase metade dos posts de indústria era
>    duplicata contada como evidência independente.
> 2. **Funcionário não é canal: 29 → 26 posts, 14 → 11 origens.** A regra antiga casava a
>    marca também no *headline do autor*, então três pessoas entravam como se fossem o canal
>    da empresa — um Business Development da FMC, um Regional Sales Manager da UPL e uma
>    Technical Account Manager da BASF. O headline de um funcionário nomeia o empregador; isso
>    não transforma o post em comunicação da empresa.
>    **NAME ≠ PROFILE ≠ PERSON ≠ ORGANIZATION.**
>
> A observação qualitativa não mudou de sinal. A base sim: 26 posts sustentam menos do que
> 54 pareciam sustentar.

**O denominador não é "tudo que estas empresas publicam".** É "posts que casaram com as
nossas 18 consultas técnicas". **Nenhuma afirmação de *share of voice* pode sair daqui.**

Dentro desse recorte: ADAMA España aparece com 4 posts, todos marcados `AGRONOMIA` e
**nenhum** marcado `SUSTENTABILIDADE`; ASCENZA marca sustentabilidade em 6 de 6 e UPL em 3 de 3.

É uma diferença de **vocabulário observada num recorte por termo**. Não é medida de
estratégia, de investimento nem de resultado.

---

## J. RECONCILIAÇÃO — duas camadas independentes, a mesma régua

A régua de campo é o **índice de exposição** (ha de olivar × incidência de repilo), que ordena
províncias — nunca dimensiona mercado.

| camada | ρ vs incidência | ρ vs área | ρ vs **índice de exposição** |
|---|---:|---:|---:|
| YouTube (n=8) | 0,214 | 0,607 | **<!--M:VOICE_ES_RHO_YOUTUBE_EXPOSURE-->0,964<!--/M-->** |
| LinkedIn, rota de posts (n=6) | 0,543 | 0,543 | **<!--M:VOICE_ES_RHO_LINKEDIN_EXPOSURE-->0,943<!--/M-->** |

**Só a rota de posts entrou.** A rota de títulos pediu "Andalusia, Spain" em metade das
consultas; correlacionar a geografia dela com a régua mediria o desenho da consulta. Seria
circular.

Duas camadas coletadas por rotas diferentes, com origens diferentes, concordam com o
**índice de exposição** e **não** com a incidência isolada.

**O que isto NÃO prova:**
- **Não prova antecipação.** As duas medidas são do mesmo período. Concordância de ordem não
  é antecedência. **PRESSÃO DE CAMPO ≠ ALERTA ANTECIPADO DE 6-12 MESES** continua valendo.
- **O confundidor de Córdoba segue aberto.** Córdoba concentra IAS-CSIC, a Universidade de
  Córdoba e a ETSIAM. Densidade institucional é explicação rival para Córdoba liderar a voz,
  e ela **não** foi separada da exposição agronômica.

---

## K. ESTADOS POR PLATAFORMA

| veredito | estado | razão |
|---|---|---|
| `RESEARCHERS_ES` | **PROVED** | 152 pesquisadores com afiliação ES declarada. Eram 153: um registro com 58 organizações declaradas contra mediana 2 era um id de autor conflacionado e saiu |
| `YOUTUBE_ES` | **PROVED** | 157 origens, transcrição recuperável, ORIGIN_ID estável |
| `LINKEDIN_ES` | **PROVED** (identidade) · **PARTIAL** (conteúdo) | país e papel saem de campos declarados, com cobertura medida; o corpus de posts é busca por termo, não censo |
| `MEDIA_ES` | **PARTIAL** | 8 de 18 rotas provadas |
| `COMPETITOR_VOICE_ES` | **PARTIAL** | denominador é o recorte, não a empresa |
| `INSTAGRAM_ES` | **FAILED_WITH_REASON** | identidade ausente em 24 de 32 contas; hashtag-alvo capturada por homônimo |
| **`VOICE_ES`** | **PARTIAL — utilizável para ORDENAR e CORROBORAR, não para DIMENSIONAR** | ver §V |

---

## V. VEREDITO — a voz muda ou reforça a decisão?

**Ela REFORÇA. Não muda. E ainda não antecipa.**

**Reforça** porque duas camadas independentes ordenam as províncias como o índice de exposição
ordena (ρ 0,96 e 0,94), sem terem visto a régua. Uma decisão de priorização geográfica tomada
com registro e campo sai da camada de voz **com mais uma testemunha independente**.

**Não muda** porque nenhuma província troca de posição por causa da voz. A voz concorda; não
corrige.

**Não antecipa** porque nada aqui foi medido no tempo. Concordância de ordem no mesmo período
não é sinal precoce, e chamá-la assim seria a palavra maior que o dado.

### O que a camada de voz passa a entregar, hoje

1. **Corroboração independente** da ordem geográfica de exposição.
2. **16 vozes técnicas de olivar** com país e papel declarados e verificáveis — nomes com
   origem rastreável, não perfis inferidos.
3. **Um relógio de publicação** em 8 rotas de mídia datadas.
4. **Uma linha-base de vocabulário** de concorrentes, com o denominador declarado.

### O que ela não entrega, e não deve ser pedido dela

Tamanho de mercado · demanda · intenção de compra · antecipação · *share of voice*.

---

## X. O QUE FICOU ABERTO

1. **O confundidor de Córdoba** — densidade institucional vs exposição agronômica, não separados.
2. **Conteúdo do LinkedIn** — falta a rota de posts *por origem*, que transformaria
   `LINKEDIN_ES` de PARTIAL em PROVED também no conteúdo.
3. **42 origens NOT_DECLARED** — resolver por cruzamento com OpenAlex e com o registro, nunca
   lendo o post.
4. **10 rotas de mídia** não provadas.
5. **Teste temporal** — a única forma de responder à pergunta da antecipação é congelar esta
   linha-base hoje e medir de novo. A linha-base está congelada (`BASELINE_ESTABLISHED`).

---

## Z. O QUE A REGRA DE COLETA EXTERNA MUDOU AQUI — 2026-08-29

A [`REGRA-DE-COLETA-EXTERNA-EAME.md`](../regras/REGRA-DE-COLETA-EXTERNA-EAME.md) foi aplicada
a esta camada logo depois de escrita. **Ela pegou dois erros nossos e abriu duas perguntas que
antes não tinham dado.**

### O que ela corrigiu

| | antes | agora | causa |
|---|---|---|---|
| corpus de posts | 472 | **372** | 100 eram o mesmo `POST_ID` de consultas diferentes |
| origens de indústria | 14 | **11** | três *funcionários* contados como canal da empresa |
| posts de indústria | 54 | **26** | as duas causas acima somadas |

### O que ela preservou — e quase se perdeu

O bruto desta camada veio de **rota paga com chave descartável**. A decisão D-003 mantém
`data/raw/` fora do git porque o bruto é cache reproduzível — mas **esta rota não se replica**:
a chave morre. As 705.149 caracteres de transcrição e os 252 registros por vídeo estavam
apenas no scratchpad efêmero. Agora estão em `data/samples/`, versionados.

### O que ela tornou possível perguntar

Antes a camada só tinha agregados. Com `PUBLICATION_DATE` em 252 de 252 registros, duas
perguntas ganharam dado — **e as duas respostas foram negativas**:

| cruzamento | estado | por quê |
|---|---|---|
| **VIDEO × FIELD** | `NO_RELIABLE_SIGNAL` | o ρ mais alto (0,442, voz antecipando uma safra) **não passa** do crítico de 0,648 a n=10, e os sinais se invertem entre defasagens |
| **VIDEO × SCIENCE** | `NOT_REACHED` | 1 candidato por nome, nenhum confirmado; por instituição o método estrito dá zero e o frouxo produz falso positivo demonstrável |

**Nenhuma das duas refuta a camada.** A concordância geográfica (§J) continua de pé. O que
elas dizem é que a voz **não antecipa no tempo** e que o elo com a ciência **não se constrói
com nome** — precisa de identificador declarado (ORCID, ROR), que as plataformas não publicam.

### O que ela acrescentou

- **346 comentários** dos 48 vídeos on-topic — e a medida de que **148 são pergunta contra 22
  de observação de campo**. A camada mede **demanda por informação técnica**, não estado do
  campo. Usá-la como sensor de campo seria ler a pergunta como se fosse resposta.
- **Baseline por canal** para os 157, em `BASELINE_ESTABLISHED` — porque um baseline agregado
  não detecta `NEW_VIDEO` de um canal específico.

---

## Y. FRANÇA E ITÁLIA

**Não foram abertas.** Nenhuma consulta, nenhuma coleta, nenhuma conclusão cross-market.

A Espanha está fechada no estado descrito acima. O próximo país começa quando este for
aceito — não antes.

### ADENDO 2026-09-03 — a Itália foi aberta, e este parágrafo passa a ser histórico

A frase acima descreve o estado **daquela missão**, e continua verdadeira sobre ela. Não é
mais o estado do repositório.

A camada de voz italiana foi aberta em 2026-09-03 pela missão de descoberta de fontes
(`docs/descoberta/MISSAO-FONTES-ITALIA-2026-09-03.md`), com o mesmo motor de transcrição e
o mesmo contrato de campos:

- **9 objetos de áudio público italiano**, 118,7 minutos, **103.404 caracteres** de fala,
  transcritos **localmente** com `faster-whisper small`, idioma `it` **declarado**, custo
  **0,00 USD** — `data/samples/IT-VOZ-AUDIO-V1/`.
- **França continua não aberta.**

**Nenhuma conclusão cross-market foi produzida**, e a lei desta seção continua valendo: a voz
não antecipa no tempo (`NO_RELIABLE_SIGNAL`), e concordância geográfica não é antecipação
temporal. O que a Itália acrescentou foi **cobertura**, não uma revisão desse veredito.
