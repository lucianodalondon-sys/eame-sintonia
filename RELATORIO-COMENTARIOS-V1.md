# COMENTARIOS-V1 — o comentário entra como asserção pública, com o pai nomeado (D106 + D107)

**Estado: PRONTO-SEM-MAPA.**

Ramo `comentarios-v1`, a partir do vivo `2ef6fef8`. Fonte do trabalho: `auditoria-madrugada/COMMENT-INTELLIGENCE-FASE1.md`
(§6 = a mudança mínima proposta) e as decisões do dono D106 (12:06) e D107 (12:28, `IAB-REGIONAL-LANGUAGE-INTELLIGENCE.md`
§5, §7, §19–22). **Sem rede.** Não colhi nada: o piloto e a medição do LinkedIn ficam em comando para o coordenador.

## O que fiz — ficheiro:linha

| # | peça pedida | o que ficou | onde |
|---|---|---|---|
| 1 | régua `COMMENT_COLLECTION_ELIGIBILITY` no pedido | `elegibilidade(pai, universo, …)`: julga o PAI **antes** do despacho, reusando `admissao._do_universo` + `PERGUNTAS_DO_UNIVERSO` (universo do pedido e temas T1–T4) e as entidades de `motor/matriz_recorte.py`. Níveis HIGH/MEDIUM/LOW/NO + **NAO_SEI** (ver «correção» abaixo). `VAI_COLHER` só com HIGH/MEDIUM e comentários ≠ 0 | `pedido/elegibilidade_comentario.py:113` |
| 1b | amostra diversa **com controlo** | `marcar()`: baldes RELEVANCIA · ENGAJAMENTO · CRONOLOGICA · DISCORDANTE · **CONTROLE** (fatia crua por hash estável, sem olhar o texto). **Marca, nunca apaga** | `pedido/elegibilidade_comentario.py:175` |
| 2 | `PUBLIC_ASSERTION` no envelope canónico | todo `COMMENT` nasce com `CLAIM_KIND=PUBLIC_ASSERTION`, `EVIDENCE_CLASS=FIELD_VOICE_OBSERVED`, `ORIGIN_STATUS=UNVERIFIED`, `AUTHOR_ROLE=UNKNOWN`, `NAO_E`. **Sem pai, não se monta** (falha fechado). O vocabulário é o que a casa já escrevia à mão em `regras/sensor_coleta.py` e `coleta/instagram_*` | `coleta/social_envelope.py:182`, `:191`, `:497` |
| 3 | `FACT_LOCATION` herdado do pai | `PARENT_CONTENT_ID` sempre. Lugar herdado **só** quando o pai o prova; senão `UNKNOWN`, com o porquê (resolve-se por junção na Sala). `COMMENT_AUTHOR_LOCATION = NAO_SE_COLETA`. O YouTube passa `YOUTUBE:<video>` | `coleta/social_envelope.py:191`, `coleta/youtube_oficial.py:789` |
| 4 | apelido do workflow para IT-T5/IT-T7 | `IT-T5-* → 'colete ciencia'`, `IT-T7-* → 'colete agronomos'`. São os apelidos do dono (`leis/territorios.py::APELIDOS`), e `pedido.alvo_de` traduz sozinho para T5 e T7 (testado). As 9 mensagens de `FONTE_SEM_APELIDO` atualizadas | `.github/workflows/sintonia-scrap.yml:543` |
| 5a | LinkedIn: rota **gratuita** de comentário | Cai a trava D24 do «comentário de terceiro». A URL de **listagem** de comentários passa de «conteúdo pessoal» a **porta trocada** (pede login). O comentário lê-se no JSON-LD da página **pública** do post: `comentarios_do_jsonld` guarda texto, data e **pseudónimo** (`LIP-`, o mesmo sal fora do Git do Instagram), com nome, url, avatar e mídia `REDACTED_BY_POLICY` | `coleta/adaptador_linkedin.py:1023`, `:1607` |
| 5b | matriz social | `LINKEDIN/FETCH_COMMENTS` nasce: `linkedin:post-publico:jsonld-comment`, custo zero, **POSSIBLE_NOT_PROVED**, `OWNER_AUTHORIZED=SIM`, `PLATFORM_POLICY_STATUS=DISALLOWED`, limite novo e **declarado** `PUBLIC_POST_COMMENTS_MINIMIZED` (o vocabulário é fechado e a matriz recusou-o até ser declarado). Instagram: nota da D106 na rota | `leis/social_matriz.py:305`, `:1118`, `:884` |
| 5c | Instagram | **Rota gratuita de TEXTO não existe** (já medido na matriz: a grátis dá o NÚMERO, nunca o TEXTO). O portão de dado pessoal **deixa de esperar o jurídico** (D106), mas o mesmo interruptor passa a ser **só o OK de GASTO**: por omissão continua fechado, agora pelo motivo certo, e o estado gravado passa a `BLOCKED_BY_SPEND_GATE` | `coleta/instagram_pessoal.py:119`, `coleta/instagram_coleta.py:461` |
| D107 | segunda finalidade do comentário | O envelope nasce com `AGRONOMIC_SIGNAL` e `LINGUISTIC_SIGNAL = NAO_AVALIADO` (o Scrap não julga), `PARENT_TOPIC`, `CANONICAL_ENTITIES`, `REGIONAL_LANGUAGE_EVIDENCE`, `REGION_IF_PROVEN` e `SPEAKER_LANGUAGE_LOCATION = UNKNOWN`. `marcar()` preenche: AGRONOMIC=YES quando nomeia entidade canónica; LINGUISTIC=YES quando tem frase própria (não se descarta comentário sem facto novo); **EXPLICIT só quando a própria fala diz o lugar** («qui in Puglia»), pelo gazetteer de `leis/fato_local.py`. **O lugar do post nunca vira a região de quem fala** (testado e com mutante) | `coleta/social_envelope.py:235`, `pedido/elegibilidade_comentario.py:175` |

**Medição a correr pela coordenação (não corri: é rede, D86-c):**
`py provas/comentarios_v1/medir_comentarios_linkedin.py <url do POST público> <pasta nova>`.
- Faz 1 pedido ao linkedin.com, com o portão de egresso IT antes e depois.
- Guarda os bytes com o sha256.
- Diz se a página pública serve `comment[]` no JSON-LD. Se servir, a rota passa a PROVED com essa prova; se não servir, fica escrito que não há rota gratuita.

## O piloto, julgado sem rede (`py pedido/elegibilidade_comentario.py piloto`)

Os 12 pais da FASE1 §7: **1 HIGH · 3 MEDIUM · 2 LOW · 6 NAO_SEI · 0 NO**. **Colhem 2:**
- `IT-T8-006 · w87w51fSWAw` (HIGH, milho e herbicida). O comando sai pronto:
  `gh workflow run sintonia-scrap.yml -f fase=comentarios-youtube -f fonte=IT-T8-006 -f video=w87w51fSWAw -f runner=2`
- `2ECn7o-Prc8` (MEDIUM, míldio do tomate). É **controlo** fora do atlas, fonte CANDIDATA, e por isso não sai comando canónico.

Os dois MEDIUM do CAI (`2cF0yHZXiMs`, `ioLYGSazexk`) **não colhem**: a fonte declara 0 comentários (`ZERO_DECLARADO_PELA_FONTE`). É o contraste que o piloto precisa.

⚠️ **Correção feita a mim, medida:** a primeira régua dava **NO** a «maculatura bruna del pero». A causa é que pera, tomate,
maçã e maculatura **não estão** nos vocabulários dos donos: o `matriz_recorte` só conhece 5 culturas, e a palavra também falta na régua da Admission.
Dizer NO seria transformar «não sei ler» em «não presta». Passou a **NAO_SEI** (`LACUNA_DE_VOCABULARIO`). NO fica só com
prova: o universo diz NÃO, ou os comentários estão desligados. 6 dos 12 pais do piloto caem nessa lacuna ou não têm
metadados no acervo. **Alargar o vocabulário é do dono dele**, não desta missão.

## Testes

- **Novos:** `tests/test_comentarios_v1.py`, 26 testes (envelope, YouTube, herança do lugar, amostra, D107, elegibilidade, piloto,
  matriz, leitor do LinkedIn, plano sem rota paga, porta trocada, portão do Instagram, workflow).
- **Três testes antigos ajustados, de forma DECLARADA e citando a D106** (nenhuma lei afrouxou):
  - `tests/test_d24_video_de_pessoa.py::test_8`: a listagem de comentários continua a morrer antes da rede, agora como porta trocada;
  - `tests/test_c13_route_gate.py`: a decisão nova registada em `DECISOES_NASCIDAS_DEPOIS`, que é o mecanismo do próprio teste;
  - `tests/test_c14c_permissao_instagram.py::test_3`: o sexto limite registado com a decisão que o criou.
- **Falhas herdadas, medidas na base `2ef6fef8`:** `test_c13_route_gate` já falha em 2 (YOUTUBE/INCREMENTAL), e 6 noutros
  módulos vizinhos (C2/C6/prontidão). Iguais antes e depois.
- **Bateria por nome, 48 módulos, base `2ef6fef8` × ramo, com rede fechada** (`provas/comentarios_v1/antes.json` e `depois.json`; corrida
  com a LOCK-PESADO às 15:20–15:37 de 27/09, com a prioridade passada pela coordenação):
  - testes corridos: **1.331 → 1.357**;
  - falhas **NOVAS: 0**;
  - **herdadas: 37**, iguais nome a nome nas duas árvores.
- ⚠️ **A bateria apanhou um defeito meu, e ele foi consertado.** Na 1.ª corrida houve **2 falhas novas** em
  `test_linkedin_build_01_local_first` (`test_21`, `test_M12`). A causa: `ONDE_SE_OBTEM['COMMENTS_TEXT']` estava como
  **PAID** («texto é evento cobrado à parte»). Com a matriz passando a ALLOWED, o planeador passou a **recomendar a rota
  paga**, que a D106-3 proíbe sem OK. Passou a **FREE** (a rota da página pública), com teste próprio e mutante M15
  (`coleta/adaptador_linkedin.py`, `ONDE_SE_OBTEM`). A 2.ª corrida deu 0 novas.

## Mutação — `provas/comentarios_v1/MUTACAO.json`

**15 de 15 mortos**, e os 6 ficheiros foram repostos iguais (sha256). O mutante só conta se fizer aparecer falha **nova**, além
das falhas herdadas. Os 15:
- o comentário vira FACT;
- o comentário sem pai passa;
- o COMMENT perde a asserção;
- o YouTube não nomeia o pai;
- **o lugar do pai vira o de quem fala**;
- o controlo some;
- a amostra apaga;
- a lacuna volta a NO;
- o zero declarado colhe;
- o LinkedIn guarda o nome do autor;
- a listagem deixa de ser recusada;
- **o Instagram abre o gasto por omissão**;
- o LinkedIn é declarado PROVED sem prova;
- o apelido T7 some;
- **o plano volta a mandar pagar o texto do comentário** (M15).

## O que NÃO está provado, e o que fica para decisão

- **Rota gratuita do LinkedIn:** candidata, não provada. Nenhum HTML com esse bloco está guardado nesta árvore.
- **A régua não está ligada dentro da fase.** A fase `comentarios-youtube` continua a colher UM vídeo nomeado. A régua corre
  no pedido, antes do despacho: pôr o universo dentro da fase obrigaria todas as outras fases da mesma receita a aceitar
  o filtro. E o `marcar()` também não está ligado ao orquestrador: é quem integra que decide onde corre, depois da colheita e antes da porta.
- **YouTube: o nome e o id do canal de quem comenta continuam no RAW** (`AUTHOR_DISPLAY_NAME`, `AUTHOR_CHANNEL_ID`). A D106
  pede «sem perfil/avatar/mídia» e «pseudónimo onde já existe»; no YouTube não existia. Estender o pseudónimo ao YouTube é
  **decisão aberta**, e escrevo-a em vez de a tomar.
- **Retenção** dos comentários: continua `UNDECLARED_PENDING_LEGAL_REVIEW`. A D106 dispensou a espera do jurídico para coletar,
  mas não fixou prazo.
- Limiares escolhidos, **não medidos** contra gabarito: 5 por balde, controlo 1 em 5, 6 palavras para sinal linguístico.
  STRONG_CONTEXT e WEAK_CONTEXT (D107 §7) não são medidos por esta régua e ficam UNKNOWN.

## SHA

O SHA final é o do último commit do ramo `comentarios-v1` no GitHub, o que traz este relatório (um commit não contém o
próprio SHA). **O mapa NÃO foi regerado (PRONTO-SEM-MAPA):** fica para a instalação, que regera uma vez só.

## EM PALAVRAS SIMPLES

- **Comentário agora entra com etiqueta de «opinião de alguém», nunca de «fato».** E sempre com o endereço do vídeo ou
  post a que responde. Sem isso, o sistema recusa montá-lo.
- **O lugar é do vídeo, não de quem comentou.** Se o vídeo é sobre o Veneto, isso não diz que quem comentou é do Veneto.
  A região da pessoa só entra se ela mesma escrever «aqui na Puglia».
- **Antes de colher, uma régua decide se o vídeo vale a pena.** Ela usa as mesmas perguntas que a porta da Sala já faz. Quando o
  vocabulário não conhece o tema (pera, tomate, maçã), ela diz «não sei», e não «não presta».
- **Dos comentários colhidos, separo 5 «gavetas»** (os mais relevantes, os mais curtidos, os mais recentes, os que
  discordam) **e uma fatia sorteada sem olhar o texto**, para saber o que a seleção deixou de fora. Nada é apagado.
- **Comentário sem fato novo mas com frase boa fica marcado como «valor de linguagem»** (D107).
- **LinkedIn:** a regra que proibia comentário caiu. Há um caminho grátis (o post público traz os comentários escondidos
  num bloco da página), mas **ainda precisa de 1 teste com a internet**. Deixei o comando pronto.
- **Instagram:** comentário escrito só sai pela rota **paga**. A D106 liberou o dado pessoal, mas não liberou gastar dinheiro.
  Por isso continua fechado até alguém dizer «pode gastar».
- **Estraguei o código de propósito 15 vezes, e os testes apanharam as 15.** A bateria completa (1.357 testes) não mostrou
  nenhuma falha nova — e na 1.ª passada apanhou um erro meu: o LinkedIn passava a sugerir pagar pelo comentário. Consertado.

HARD STOP.
