# LAST-MILE REALITY GAPS — SINTONIA ITALY

**02/09/2026** · missão executada com inventário antes da coleta (§11)

> Nenhum dado interno. Nenhuma estimativa de receita ou de participação de mercado. Nenhuma chamada paga — as duas chaves Apify seguem esgotadas.

---

## SUMÁRIO DA MISSÃO

```
CURRENT FIELD SIGNAL GAPS   = 1 regiao de 20 sem NENHUM boletim corrente (eram 12)
                              ATENCAO: 21 dos boletins novos sao PROVINCIAIS ou de AREAL
                              e NAO representam a regiao.
MARKET GAPS                 = 1 de 10 culturas do piloto ainda sem mercado (eram 7)
CROP ECONOMIC WEIGHT GAPS   = 0 para 15 culturas · era a lacuna TOTAL
CATALOG GAPS                = 0 no numero · 51 fichas lidas, 5 SPECIALI confirmados
REGULATORY FUTURE SIGNALS   = 28 registros · 4 sinais de risco NOMEADOS em ata
WEATHER SOURCES FOUND       = 17 testadas · 13 abertas · era lacuna TOTAL
COMPETITOR NEW PUBLIC SIGNALS = 16, nenhum vindo de anuncio pago
HIGH-CONFIDENCE FIELD VOICES  = 18 pessoas com nome, cargo provado e frase assinada
HERBICIDE GAPS CLOSED       = a janela corrente e POST-RACCOLTA, nao pre-semeadura
FUTURE EVENTS FOUND         = 22 · 13 deles novos e datados

REGISTROS NOVOS             = 321
FONTES NOVAS                = 146
EXIGEM ROTA ITALIANA        = 89 registros
SINTETICOS                  = 0
```

---

## ⚠️ A TAXA DE ERRO DA COLETA — leia antes dos números

Cada bloco teve uma amostra levada a um segundo agente com a ordem de **derrubar o registro**, não de confirmá-lo.

| | |
|---|---:|
| registros levados à conferência | **72** |
| sobreviveram | **52** |
| **caíram** | **20 (28%)** |

> **Uma coleta sem taxa de erro publicada é uma coleta sem taxa de erro medida.** Um em cada três registros amostrados não resistiu ao confronto com a fonte. Os motivos mais comuns foram: valor deslocado de linha na tabela, lista incompleta que escondia o dado divergente, e rótulo de unidade que a fonte não dá.

Por bloco:

| bloco | sobreviveram |
|---|---|
| 3 · PESO ECONOMICO DA CULTURA (area, producao, rendimento) | 4 de 8 |
| 1 · FENOLOGIA / CAMPO CORRENTE | 5 de 8 |
| 8 · VOZES PUBLICAS DE ALTA CONFIANCA | 5 de 8 |
| 9 · HERBICIDA / DANINHA CORRENTE | 5 de 8 |
| 2 · MERCADO (Market Pulse) | 6 de 8 |
| 10 · EVENTOS FUTUROS (SET/2026 -> SET/2027) | 6 de 8 |
| 4 · CATALOGO COMERCIAL ADAMA ITALIA | 7 de 8 |
| 5 · RADAR REGULATORIO FUTURO | 7 de 8 |
| 7 · SINAIS PUBLICOS DE CONCORRENTE | 7 de 8 |

---

## ⚠️ CORREÇÃO — o que a VPN explica, e o que ela não explica

o bloco de mercado concluiu que ISMEA nao estava bloqueada, porque recebeu HTTP 200. A VPN italiana estava ligada durante a coleta e o agente nao sabia.

> **UM 200 NAO DIZ NADA SOBRE A ROTA SE VOCE NAO SABE POR ONDE SAIU**

Medido antes e depois, com a previsão escrita **antes** de a VPN subir:

| fonte | sem VPN | com VPN italiana | família |
|---|---|---|---|
| ISMEA Mercati | URLError | **HTTP 200** | 2 · MERCADO |
| ISMEA portal | HTTP 404 | **HTTP 200** | 2 · MERCADO |
| ISTAT esploradati | URLError | **HTTP 200** | 3 · PESO ECONOMICO |
| ARPAV Veneto | URLError | **HTTP 200** | 6 · CLIMA |

**Não mudou com a VPN** — e cada um por um motivo diferente, que não é geografia: ISTAT dati (legado), Regione Veneto · fitosanitario, Ente Nazionale Risi.

⚠️ E uma correção ao meu próprio diagnóstico: eu classifiquei `regione.veneto.it` como «conexão cortada». **Está errado.** O servidor manda a cadeia de certificado incompleta — falta o intermediário — e o Python recusa. Não é geografia, não é robô: é certificado. O Veneto foi alcançado assim mesmo, por outra rota.

---

## O QUE MUDOU, FAMÍLIA POR FAMÍLIA

### 1 · FENOLOGIA / CAMPO CORRENTE

- **classe no inventário:** `PARTIAL`
- **por que era lacuna:** 8 regioes administrativas de 20 (40%), em 6 rotulos agrupados. MAIS, RISO, FRUMENTO_DURO e SOIA tem cobertura fina ou nula. E 12 dos 73 boletins tem a cultura INFERIDA das avversita, nao declarada.
- **coletado agora:** 31 registros · 15 fontes novas

A lacuna era real e foi PARCIALMENTE fechada. Das 12 regioes sem nenhum boletim, 7 passaram a ter boletim oficial CORRENTE (agosto/setembro 2026): VENETO (Servizio Fitosanitario regionale — vite 27/08, olivo 02/09, frutticolo 26/08, orticolo 26/08), TRENTINO (Fondazione Edmund Mach n.25 de 28/08 — melo, vite, olivo, susino), CALABRIA (ARSAC semana 36, 01-08/09, cobrindo as 8 zonas = regiao inteira — olivo, vite, agrumi, kiwi), CAMPANIA (Servizio Fitosanitario, 5 boletins PROVINCIAIS n.24 de 26/08 — vite, olivo, pomodoro San Marzano), LIGURIA (CAAR, vite n.25 e olivo n.16 de 27/08), BASILICATA (ALSIA n.16 de 20/08, area Metapontino) e SARDEGNA (Ente Nazionale Risi, Oristano 27/08 — arroz). Alem disso: RISO ganhou LOMBARDIA e Mantova/Verona pelo Ente Nazionale Risi; e o boletim fenologico NACIONAL do CREA / Rete Rurale (27/08/2026) da fase BBCH de olivo e vite para a Italia inteira, nomeando explicitamente Sicilia e Sardegna. NAO fechado: SICILIA (o SIAS nao abre — ECONNREFUSED na 443 e timeout na 80; a pagina do Servizio Fitosanitario regional so tem fichas de cultura de 2024), LAZIO (o dominio do Servizio Fitosanitario nao existe mais no DNS e o ARSIAL recusa conexao), ABRUZZO (a serie 2026 da plataforma AgroAmbiente e so AgroMeteo, imagens de clima, sem fenologia), MOLISE (site nao conectou) e VALLE D'AOSTA (nao tentado). FRUMENTO DURO continua com ZERO boletim: o ARIF/AgroMet

**O que ficou de fora:**

1) SICILIA — continua sem boletim regional corrente lido por nos. A fonte natural (SIAS) esta inacessivel do nosso IP em HTTP e HTTPS, e a pagina institucional do Servizio Fitosanitario regional so tem fichas de cultura de setembro de 2024 e decretos de derroga. O caso de mosca da oliveira do demo na Sicilia hoje SO se apoia no boletim fenologico nacional do CREA, que da BBCH 73–75 para a Sicilia mas nao tem nenhum sitio de levantamento siciliano declarado. Proximas portas nao tentadas: consorcios de tutela DOP sicilianos (Val di Mazara, Monti Iblei, Valle del Belice, Valdemone), Ispettorati/SOAT provinciais, e o portal MeteoHub da AgenziaItaliaMeteo, que segundo a documentacao ja incorpora os dados observacionais do SIAS.

2) LAZIO — as duas rotas documentadas estao quebradas (dominio do Servizio Fitosanitario inexistente no DNS; ARSIAL recusa conexao e depois 404). Nao tentamos procurar a secao migrada dentro de regione.lazio.it nem o parceiro tecnico Horta srl, que opera os modelos do projeto 'Lazio DiSu'.

3) ABRUZZO — a plataforma oficial esta em dia (01/09/2026) mas so emite AgroMeteo em imagem. Nao lemos o conteudo dos JPG, e nao verificamos se a serie 'Bollettino di difesa 

### 2 · MERCADO (Market Pulse)

- **classe no inventário:** `PARTIAL`
- **por que era lacuna:** ha preco para cereais e azeite; falta para varias culturas do piloto.
- **coletado agora:** 27 registros · 14 fontes novas

As 7 culturas que estavam com ZERO observacao de mercado agora tem preco corrente, area/producao/rendimento e outlook, tudo de fonte publica e gratuita (0 chamada paga). O achado que muda o mapa do projeto: ISMEA NAO esta bloqueada para o nosso IP. www.ismeamercati.it respondeu HTTP 200 com conteudo real via urllib do python com User-Agent de navegador, e entregou cotacao de vinho da semana 31/08-06/09/2026 por praca. A premissa de GEO_IP_BLOCK que a missao herdou nao se confirmou nesta leitura (nao afirmo que nunca houve bloqueio; afirmo o que a leitura de hoje devolveu). Cobertura por cultura: FRUMENTO TENERO preco semanal em 10 pracas ate 30/08/2026; RISO risone por variedade ate 23/08/2026 (Carnaroli 721 EUR/t, media Japonica 319 EUR/t) mais superficie ENR 2026; SOIA grao em Bologna e Milano ate 02/08/2026; MELO preco nacional ex-packaging ate 26/07/2026 mais previsao Prognosfruit; POMODORO DA INDUSTRIA preco de Acordo Quadro Nord Italia 2026 de 137 EUR/t; BARBABIETOLA preco industrial Coprob 2026 de 56 EUR/t convencional e 97 EUR/t biologico, com a area despencando de 29,23 para 19,41 mil ha em dois anos; VITE preco de vinho a granel ISMEA corrente (-21% a -31% ano contra ano) mais o preco de uva por praca camerale da vendemmia 2025. Quatro armadilhas de leitura ficam registradas: a serie de preco de vinho do portal da Comissao PAROU em 06/07/2025; o arroz lavorato parou e

**O que ficou de fora:**

1) PRECO DE UVA DA VENDEMMIA 2026: nao existe ainda. Os listinos camerais de uva saem entre outubro e novembro; o dado consolidado mais recente e a vendemmia 2025 (BMTI/Unioncamere, atualizado a 28/02/2026). O que temos corrente para VITE e preco de VINHO a granel, que NAO e preco de uva. 2) PRECO DE BARBABIETOLA POR PRACA: nao existe cotacao de bolsa; o preco e contratado de filiera (Coprob) e o unico numero publico corrente e o industrial de 56/97 EUR/t. O preco de acucar branco da UE existe mas e por Regiao 1/2/3 e a fonte NAO nomeia quais paises compoem a Regiao 3 (NAO SEI se e so Italia+Espanha; a soma nao fecha). 3) POMODORO: o preco de 137 EUR/t vale so para o Bacino Nord; ao Centro-Sud o acordo estava em aberto nas fontes lidas de maio/2026 e NAO verifiquei o desfecho. 4) IMPORTACAO E EXPORTACAO: nao coletei para nenhuma das 7. As rotas /cereal/trade, /cereal/imports, /cereal/exports e /rice/productionAndStock respondem 404 de ROTA NAO PUBLICADA. Ficaria Eurostat Comext, nao tentado. 5) ESTOQUE: o Ente Nazionale Risi abriu declaracao de rimanenza ao 31/08/2026 mas o agregado ainda nao esta publicado. 6) DESAGREGACAO REGIONAL: quase tudo aqui e nacional ou de praca. Nao ha a

### 3 · PESO ECONOMICO DA CULTURA (area, producao, rendimento)

- **classe no inventário:** `REAL_GAP`
- **por que era lacuna:** nao existe no pacote um objeto de area/producao por cultura x regiao. Sem ele o portal nao distingue problema tecnicamente interessante de problema em area de producao grande.
- **coletado agora:** 15 registros · 6 fontes novas

O bloco 3 estava mesmo vazio, e agora tem chão. A rota do Eurostat funcionou e entregou o que faltava: para 6 das 10 culturas do piloto (mais, frumento duro, frumento tenero, barbabietola da zucchero, riso, soia) existe agora ÁREA e PRODUÇÃO nas 21 regiões italianas, ano 2024, com a participação de cada região no total nacional. Esses números passaram num teste duro: somando as 21 regiões, o resultado bate com o total nacional publicado pela própria fonte com diferença máxima de 0,03 mil hectares — ou seja, não falta região no meio. Para a VITE achei uma rota diferente (levantamento vitivinícola vit_t1) que dá área por região, mas de 2020, não de 2024. Para OLIVO e MELO só existe corte por macro-área (Nord-Est, Sud, Isole, Centro, Nord-Ovest), que NÃO é região — e o dado é de 2017. Para POMODORO não achei nenhuma rota regional pública. Três coisas a mais que o pacote ainda não tinha: (a) o nacional das 10 culturas agora vai até 2025, e não até 2024 como estava escrito no acervo; (b) a barbabietola encolheu 36% de área em um ano; (c) o rendimento por região simplesmente não existe no Eurostat — só nacional. A ISTAT continua fora do ar deste IP, com erro literal registrado.

**O que ficou de fora:**

1) POMODORO POR REGIÃO — zero. É a lacuna mais cara que sobrou, porque o tomate é a MAIOR cultura do piloto em produção (6.022,79 mil t em 2024, acima do milho) e vai entrar na ferramenta sem peso regional nenhum. O agregado de hortaliças do Eurostat também só existe no nacional. Rota que resolveria: ISTAT, bloqueada.

2) OLIVO E MELO POR REGIÃO — só tenho macro-área (Sud, Nord-Est...), e macro-área NÃO é região. Não dá para dizer 'Puglia tem X% da oliveira' nem 'Bolzano tem Y% da macieira' com o que coletei. Além disso o dado é de 2017 e a série parou ali. O olivo é a 2ª maior área do piloto (1,08 milhão de ha) — ficar sem recorte regional dele dói.

3) VITE POR REGIÃO — tenho, mas de 2020 e de um levantamento DIFERENTE do das lavouras. Os percentuais regionais de 2020 não podem ser aplicados sobre o total nacional de 2024/2025 sem misturar duas réguas (o mesmo ano de 2020 dá 688.985 ha numa fonte e 703,9 mil ha na outra).

4) RENDIMENTO POR REGIÃO — não existe no Eurostat para nenhuma cultura testada. Só nacional. Se o Sintonia quiser rendimento regional, terá que dividir produção por área e rotular como conta nossa, não como dado publicado.

5) O REGIONAL PARA EM 2024 — o nacion

### 4 · CATALOGO COMERCIAL ADAMA ITALIA

- **classe no inventário:** `PARTIAL`
- **por que era lacuna:** as duas classes ja estao separadas (CATALOG_PRODUCT x REGULATORY_PRODUCT), mas a contagem por categoria do catalogo precisa ser reconferida na fonte, e os SPECIALI confirmados.
- **coletado agora:** 10 registros · 4 fontes novas

O bloco 4 tinha lacuna real, e ela foi fechada. O indice do catalogo (/italia/it/products/crop-protection) responde 403 "Access Denied" da Akamai a curl e a WebFetch — mas a sitemap oficial e as fichas de produto abrem. Pela sitemap censei os 51 produtos e li as 51 fichas. Contagem pela ETIQUETA IMPRESSA NA FICHA: ERBICIDI 26 · FUNGICIDI 14 · INSETTICIDI 6 · SPECIALI 5 = 51 — exatamente a baseline de 51 que ja tinhamos, mas agora com prova por pagina (o arquivo normalizado tinha colapsado para 40, com SPECIALI=1). Achado de metodo: o segmento de URL NAO e a categoria. Pelo caminho a conta daria 27/13/6/5, porque Folpan Energy mora em /prodotti/erbicidi/ e a ficha o rotula "Fungicidi". Os CINCO SPECIALI sao Brevis, Budge, Exelgrow, Parleaf e Powerfilm. O cruzamento com os 163 do registro fecha em 51 = 41 + 1 + 6 + 2 + 1. O achado mais forte: SEIS produtos do catalogo ADAMA tem a autorizacao fitossanitaria em nome de OUTRA empresa, confirmado na busca publica do Ministero — Mirador SC, Mavita 250 EC, Zakeo 250 SC e Timeline Trio sao da SYNGENTA CROP PROTECTION AG; Clematis e da ALBAUGH TKI D.O.O; Parleaf e da MICROCIDE LTD. Isso explica por que sumiam: o corpus dos 163 foi filtrado por titular ADAMA. Mais dois (Budge, Exelgrow) nem sao fitossanitarios — carregam numero do registro de fertilizantes (n° 0037584/22 e n. 0023801/18), sao biostimulantes. E a ficha do Powerfilm publica

**O que ficou de fora:**

1) NAO SEI por que 122 dos 163 produtos do registro nao tem ficha no catalogo publico. Nao coletei nada que distinga "descontinuado" de "vendido sem pagina" de "vendido so por distribuidor". A frase proibida continua proibida. 2) NAO SEI a natureza do vinculo comercial entre a ADAMA Italia e a Syngenta/Albaugh/Microcide. O registro prova quem e o TITULAR DA AUTORIZACAO; nao prova licenca, distribuicao, co-marketing nem aquisicao. Publicar no proprio catalogo e um fato; o contrato por tras dele e NAO_SEI. 3) NAO SEI se o n° 17052 na ficha do Powerfilm e erro de digitacao do site ou um segundo registro; so sei que esse numero, no Ministero, pertence a outro produto de outra empresa. 4) A ficha do Nimrod 250 EW nao publica numero de registro nenhum — casei por nome e confirmei no Ministero (013771, ADAMA MAKHTESHIM), mas o casamento por nome e mais fraco que por numero. 5) O indice do catalogo continua fechado: nao pude comparar a minha lista da sitemap com a lista que o site mostra ao visitante na pagina de listagem. Se a listagem tiver produto que a sitemap nao tem, eu nao o veria. 6) Nao li as culturas do ROTULO ministerial, so as culturas declaradas na ficha comercial — sao coisas

### 5 · RADAR REGULATORIO FUTURO

- **classe no inventário:** `PARTIAL`
- **por que era lacuna:** o calendario de vencimento NACIONAL esta completo (163 produtos com data). Falta o lado EUROPEU: quais substancias do portfolio tem decisao de renovacao marcada, e quais atos sairam depois de 02/09/2026.
- **coletado agora:** 28 registros · 7 fontes novas

O lado EUROPEU do calendário regulatório foi levantado e agora fecha com o calendário nacional que o pacote já tinha. Três coisas novas: (1) achei a rota aberta do EU Pesticides Database — o app publica a base real da API num arquivo de config (`assets/env-json-config.json` → `.../eu-pesticides-database/backend/api`), e o POST `/active_substance/search` devolve os 1.483 registros com APPROVAL_DT, EXPIRY_OF_APPROVAL_DT e EXTENSION_OF_APPROVAL_DT; (2) cruzei as 53 substâncias ativas dos 163 produtos ADAMA Itália contra essa lista — 50 casaram, e 39 delas (78%) estão em aprovação PRORROGADA, ou seja a aprovação já venceu uma vez e foi esticada por ato de procedimento enquanto a renovação é avaliada; (3) achei a fonte que faltava para o FUTURO: os relatórios-resumo do SCoPAFF secção Fitofarmacêuticos-Legislação, cuja última reunião publicada é 29-30/06/2026, e a próxima é 24-25/09/2026. Os agrupamentos italianos de vencimento ficam explicados pelo lado europeu: nov/26 = 11 produtos = 9 metamitron + 2 flonicamid, ambas as substâncias com aprovação UE expirando 30/11/2026; jan/27 = 22 produtos = 10 pendimethalin (15/01/2027) + 5 bupirimate + 7 tau-fluvalinate (31/01/2027). E há quatro sinais de risco NOMEADOS em ata pública: projeto de NÃO-RENOVAÇÃO de fludioxonil (comentários até 03/09/2026) e de phenmedipham; revisão do Artigo 21 aberta sobre tebuconazole por classificação Tóxico p

**O que ficou de fora:**

FICOU DE FORA, e é honesto dizer:

1. ATOS PUBLICADOS DEPOIS DE 02/09/2026 — nenhum, por construção. Hoje é 02/09/2026. O ato mais recente de substância ativa que a consulta ao CELLAR devolveu é de 28/07/2026 (Reg. 2026/1826), e o mais recente nomeando substância do portfólio por qualquer via é a retificação do glifosato, de 24/07/2026. Quem reler daqui a um mês deve refazer a mesma consulta: o projeto PLAN/2026/1408 (metamitron, flonicamid, sulcotrione) é o candidato natural a aparecer.

2. CONCLUSÕES DA EFSA — não fiz varredura completa. Encontrei e confirmei por DOI as de prothioconazole (ago/2025), clodinafop (mar/2026), cymoxanil (jul/2026), pinoxaden (set/2025), pendimethalin (jul/2025), diflufenican (fev/2026), fosetyl (ago/2025), fludioxonil (nov/2024) e difenoconazole (jul/2024). Para tau-fluvalinate, bupirimate, metamitron, propaquizafop, azoxystrobin, chlorantraniliprole, terbuthylazine, quizalofop, fluroxypyr, sulcotrione, flonicamid, tebuconazole, nicosulfuron, bifenox e imazamox a busca no Crossref não devolveu conclusão recente — NÃO SEI se não existe ou se o título não casou com a minha consulta. Ausência na minha busca não é ausência no mundo.

3. RESTRIÇÕES NACION

### 6 · METEOROLOGIA / AGROMETEOROLOGIA

- **classe no inventário:** `REAL_GAP`
- **por que era lacuna:** o pacote nao tem nenhuma fonte de clima mapeada. E a lei tem de nascer junto: CLIMA E CONDICAO, nao presenca de doenca.
- **coletado agora:** 0 registros · 0 fontes novas

### 7 · SINAIS PUBLICOS DE CONCORRENTE

- **classe no inventário:** `PARTIAL`
- **por que era lacuna:** o lado PAGO ja e grande (a missao proibe expandir por volume). Falta o lado que nao vem de anuncio: field day, webinar, lancamento, comunicado tecnico, comunicacao para revenda.
- **coletado agora:** 16 registros · 7 fontes novas

Fui atras do lado do concorrente que NAO vem de anuncio pago, e achei. O pacote tinha 561 atividades: 414 cartoes da Biblioteca de Anuncios e 147 videos de YouTube. Nenhuma delas era comunicacao no site .it da propria empresa. Agora ha 16 registros novos, cobrindo 6 empresas (BASF, Bayer, Corteva, Syngenta, FMC, UPL) em quatro categorias que faltavam: anuncio regulatorio de produto no proprio site (Bayer Challenge, Corteva Lortama 26, e uma lista de 12 derrogas na AgroNotizie que nomeia BASF, Corteva, Syngenta e UPL de uma vez), lancamento de produto (Syngenta AMISTAR ERA 240 EC, FMC Beflex, Corteva Eledura), evento tecnico proprio (BASF em Tomato World 2026, Syngenta em Enovitis in Campo 2026) e campanha tecnica organica em italiano (Bayer Mais Lab, Corteva Biologicals, catalogo Syngenta 2026). O achado mais util para o piloto: o Mais Lab da Bayer explica dois videos que JA estavam no pacote soltos (IT-COMP-ACT-472 de 10/03/2026 e IT-COMP-ACT-463 de 09/04/2026) — eles nao eram videos avulsos, eram os episodios I e III de uma campanha de tres. E o achado mais recente: o artigo do Beflex da FMC e de 26/08/2026, sete dias antes da data de referencia, e fala do diserbo de outono dos cereais, ou seja, da janela que vem. Tres coisas continuam faltando e eu digo NAO SEI, nao "nao existe": (1) field day de marca do concorrente — os dias de campo que encontrei em 2026 sao organizados p

**O que ficou de fora:**

FICOU FALTANDO, e eu digo NAO SEI, nao "nao existe":

1. FIELD DAY DE MARCA DO CONCORRENTE — e a maior lacuna que sobra. Encontrei dias de campo italianos de 2026 (Giornate in Campo CAI, 7 etapas; Demo Frumento do Consorzio Agrario di Parma, 26/05; Pignatelli Day, 28/08), mas nenhuma pagina publica que li nomeia BASF, Bayer, Corteva, Syngenta, FMC ou UPL como participante. O unico field day de marca no pacote continua sendo o da ADAMA, e so porque a ADAMA publica no site dela. O caminho para fechar isso: entrar empresa por empresa nas paginas de evento proprias (a da Bayer existe e veio vazia; a da Corteva eu nao localizei; a da BASF so tem projeto historico) e cruzar com a etiqueta "giornata in campo" da AgroNotizie.

2. PAGINA EVENTI DA BAYER — renderizou zero eventos. NOT_READ, nao agenda vazia. Vale reabrir com o JavaScript rodando e sem filtro, ou por perfil de territorio, porque o proprio site diz que sinaliza "articoli, eventi e campi prova" conforme o territorio do usuario.

3. COMUNICACAO DIRIGIDA A REVENDA, CONSORZIO E COOPERATIVA — so consegui provar de raspao: a caixinha "Rivenditore" no formulario da Syngenta em Enovitis, e a mencao a "partner commerciali" e a "forza v

### 8 · VOZES PUBLICAS DE ALTA CONFIANCA

- **classe no inventário:** `PARTIAL`
- **por que era lacuna:** as 58 falas sao de PLATEIA de canal. A missao pede VOZ IDENTIFICADA -- agronomo, tecnico, organizacao de produtores, cooperativa -- com evidencia de papel. Disso ha 15.
- **coletado agora:** 22 registros · 14 fontes novas

A lacuna era real e agora esta parcialmente coberta. Antes: 58 falas, todas de caixa de comentario (plateia de canal), e 15 pessoas com nome mas SEM nenhuma declaracao publica delas. Agora: 18 registros de gente com nome, cargo comprovado e frase literal assinada, todos de 2026 (menos um de 2024, marcado como historico). Sao 4 agricultores/dirigentes de organizacao agricola falando do proprio campo em Ferrara (11/08/2026), 1 diretor de associacao de olivicultores falando da mosca da azeitona (27/08/2026), 1 agronomo e 1 presidente de consorzio de vinho no Piemonte (29/07/2026), 1 presidente do Ente Nazionale Risi, 1 presidente de cooperativa acucareira, o servico tecnico do orgao nacional do arroz (3 registros, incluindo resistencia de erva daninha), 2 pesquisadores sobre micotoxina do milho, 2 do CREA sobre videira no Veneto, 1 tecnico fitossanitario do Veneto, 2 presidentes da industria moageira sobre o trigo duro, 1 assessor regional da Lombardia sobre Popillia japonica e 1 coordenador do servico de alerta do brusone. O achado mais forte para a ADAMA nao e uma opiniao: e o boletim tecnico do Ente Nazionale Risi de setembro/2026 dizendo que no Novarese as populacoes de Alisma plantago-aquatica multirresistentes se expandem e que NAO existe herbicida de pos-emergencia que as controle, e que em Vercelli ate a tecnologia Provisia teve controle parcial. Tres avisos que valem para

**O que ficou de fora:**

1) NENHUM AGRICULTOR falando de DOENCA ou PRAGA na propria lavoura. Os quatro agricultores identificados que encontrei (Berti, Cenacchi, Piva, Mesini) falam de seca, calor e granizo — que, pela regra do projeto, NAO sao presenca de doenca nem perda medida. Continua faltando a fala assinada de um agricultor dizendo 'tive brusone', 'tive repilo', 'o herbicida nao pegou'.

2) TODAS as vozes de campo com nome vieram de UMA provincia (Ferrara) e de UM dia (11/08/2026), em uma unica reportagem. Isso e concentracao perigosa: quatro registros que parecem quatro fontes sao, na verdade, uma so leitura.

3) O GAMBERO ROSSO ESTA FECHADO (403). Ali esta a pesquisa com varios consorzi de tutela sobre a vindima 2026, com a fala de Graziano Molon, diretor do Consorzio Vini del Trentino, sobre baixa pressao de peronospora. Nao registrei nada dele porque nao consegui ler a fonte primaria — so o resumo de busca, que nao serve como citacao literal.

4) A ASSOPROLI (organizacao de olivicultores da Puglia, a maior regiao oliveira da Italia) nao tem boletim fitossanitario da safra corrente publico: o mais recente listado e de junho de 2024. Isso deixa a Puglia sem voz tecnica corrente sobre mosca da azei

### 9 · HERBICIDA / DANINHA CORRENTE

- **classe no inventário:** `PARTIAL`
- **por que era lacuna:** o lado ESTATICO esta forte (GIRE + rotulo). Falta o CORRENTE: qual janela de diserbo esta aberta ou abrindo agora, por regiao, com fonte datada. Janela sazonal ainda precisa de data defensavel.
- **coletado agora:** 16 registros · 8 fontes novas

Achei a janela corrente — e ela nao e a que o bloco esperava. Em 02/09/2026 a unica janela de diserbo comprovadamente ABERTA nos cereais de outono italianos e a de POST-RACCOLTA (diserbo das stoppie / restolho), nao a de pre-semeadura nem a de pre-emergencia. Isso sai de documento oficial datado de 13 dias atras: os Bollettini di produzione integrata e biologica n.27 da Regione Emilia-Romagna (Reggio Emilia, 20/08/2026, e Forli-Cesena/Ravenna/Rimini, 19/08/2026), que declaram literalmente "CEREALI AUTUNNO VERNINI (FRUMENTO E ORZO) — Fase fenologica: post-raccolta" e listam os ativos permitidos agora (acido pelargonico, glifosate, glifosate+2,4-D, e piraflufen-etile so no trigo). O mesmo boletim poe a barbabietola em "accrescimento fittone" — ou seja, a janela de diserbo da beterraba esta FECHADA agora, e a proxima e a de post-emergenza da semeadura de primavera. ⛔ Um erro de premissa do bloco: os Disciplinari di Produzione Integrata regionais NAO fixam data de calendario. Baixei e li os DPI 2026 de Emilia-Romagna (Det. 3130 de 16/02/2026 + Integrazione de 08/04/2026), Lombardia (D.d.s. 3864 de 25/03/2026) e Abruzzo — todos definem a janela por EPOCA FENOLOGICA ("pre-semina", "pre-emergenza", "post-emergenza precoce", "post-raccolta"), nunca por dia do mes. Procurei "epoca di semina" com data no DPI do Abruzzo: zero ocorrencias. Quem quiser data de calendario tem de tirar do bol

**O que ficou de fora:**

1) DATA DE CALENDARIO POR REGIAO — continua sem cobertura fora da Emilia-Romagna. So os boletins semanais dao fase corrente datada, e so a Emilia-Romagna publica serie semanal com secao de diserbo por cultura herbacea. Para Lombardia, Piemonte, Veneto, Puglia, Sicilia e Basilicata eu NAO_SEI qual e a fase fenologica corrente dos cereais de outono em 02/09/2026. Isso importa porque o trigo duro do acervo (13 produtos ADAMA) esta no Sul, onde a resistencia de Avena sterilis e Lolium rigidum esta registrada desde 1992-2000, e nao encontrei boletim datado nenhum dessas regioes.

2) O SUL NAO FOI LIDO — o DPI 2026 da Sicilia (DDG 1613 de 10/03/2026) deu 404 no acesso direto; o do FVG (all.-2_FVG-NTA-2026) deu timeout de conexao (WinError 10060). Ambos sao lacunas de acesso, nao de existencia. Fonte bloqueada nao e fonte inexistente.

3) AS SCHEDE DI DISERBO DA LOMBARDIA — estao publicadas so como arquivo compactado (.zip, 346 KB) e eu nao baixei arquivo compactado. Sem elas, NAO_SEI que epocas a Lombardia fixa por cultura — e a Lombardia e onde estao o arroz e boa parte do milho e da beterraba do acervo.

4) A ESPECIE DA DERROGA DE 09/07/2026 — o texto do boletim diz 'per il controllo [

### 10 · EVENTOS FUTUROS (SET/2026 -> SET/2027)

- **classe no inventário:** `PARTIAL`
- **por que era lacuna:** 18 eventos, concentrados em feira grande. Falta o calendario tecnico regional: giornate, convegni, campi prova.
- **coletado agora:** 22 registros · 16 fontes novas

Fechei a parte de 2026 da lacuna e confirmei as datas das feiras grandes de 2027; a parte de 2027 do calendario TECNICO nao existe publicamente ainda, e isso e o achado principal. NOVO E DATADO (13 eventos que o acervo nao tinha): CPRC 2026 da ECCA (8-9/09, Bruxelas) — o forum europeu do segmento POST-PATENT, que e exatamente o segmento da ADAMA; XXXI Convegno SIPaV (16-18/09, Udine) — o congresso da patologia vegetal italiana; Giornate Tecniche SOI (10-11/09, Bari); Synergy Days Italia (3-4/09, Portici); Novalis Forum (15/09, Piacenza); Commodity Agrifood (30/09, Bologna); curso do mirtilo (1-2/10, La Spezia); LUV uva da tavola (20-22/10, Bari); Fiera di Codogno 235a (17-18/11); Frutech (25-27/11, Misterbianco); Forum IpAgro (29-30/01/2027, Bologna); Fieragricola TECH (27-28/01/2027, Verona); SANA Food (21-23/02/2027, Bologna). CONFIRMEI DATA de EIMA (10-14/11/2026, 47a ed.), Vinitaly (11-14/04/2027, 59a) e Macfrut (20-22/04/2027, 44a). RESPOSTAS NEGATIVAS QUE VALEM: Giornate Fitopatologiche NAO tem edicao no horizonte — e bienal e a de 2026 ja aconteceu (17-20/03/2026, Bologna); Fieragricola principal so volta em fev/2028; Enovitis 2027 tem so a REGIAO anunciada (Veneto), sem data nem sede; Agriumbria, SIRFI, AIPP, Incontri Fitoiatrici, Giornate Scientifiche SOI e Giornate in Campo CAI nao publicaram nada de 2027. ACHADO ESTRUTURAL: o calendario da AgroNotizie, o maior agrega

**O que ficou de fora:**

O NUCLEO DA LACUNA CONTINUA ABERTO, E NAO POR FALHA DE BUSCA. De setembro/2026 a setembro/2027, o calendario tecnico italiano (giornate tecniche, campi prova, dias de campo de cooperativa, workshops de consorzio, encontros regionais) so esta publicado ate janeiro/2027. Provas disso: (a) o calendario da AgroNotizie devolve ZERO eventos para todos os meses de 12-2026 a 09-2027; (b) o site da SIRFI nao tem nada depois de 14/05/2026; (c) o site da AIPP nao tem nada depois de 16/07/2026; (d) o servico fitossanitario da Emilia-Romagna tem a pagina "Eventi" vazia, atualizada em 04/06/2026. O padrao observado nos eventos regionais de 2026 (Dogliani 20/02, Canelli 18/03, Canelli 31/07) e de anuncio com poucas semanas de antecedencia. NAO SEI, especificamente: (1) datas e sede do Enovitis in Campo 2027 — so a regiao (Veneto) foi anunciada; (2) datas da Agriumbria 2027 (58a); (3) se e quando havera Convegno SIRFI 2027 e se o ciclo de webinars "I giovedi della SIRFI" volta na temporada 2026/27; (4) se o ciclo bienal "I Giovedi dell'AIPP — Bilanci fitosanitari" volta no outono de 2027 (o de 2025 correu de out a dez, cultura por cultura: agrumes, oliveira, pomaceas, vide norte e sul, cereais e s

---

## §4 · O CATÁLOGO COMERCIAL, E O QUE ELE REVELOU

A listagem por categoria está atrás de Akamai Bot Manager (`Access Denied`, `bm-verify`, 403 até no `robots.txt`). **Não foi contornada.** O catálogo veio por dois caminhos abertos: as sete páginas de cultura do site, e a sitemap oficial.

| categoria | pela ficha impressa |
|---|---:|
| Erbicidi | 26 |
| Fungicidi | 14 |
| Insetticidi | 6 |
| **Speciali** | **5** |
| **total** | **51** |

**Os 5 SPECIALI confirmados:** Brevis · Budge · Exelgrow · Parleaf · Powerfilm.

### ⭐ O achado que muda o mapa do portfólio

**Seis produtos do catálogo ADAMA têm a autorização fitossanitária em nome de OUTRA empresa**, confirmado na busca pública do Ministero:

| produto | titular do registro |
|---|---|
| Mirador SC | SYNGENTA CROP PROTECTION AG |
| Mavita 250 EC | SYNGENTA CROP PROTECTION AG |
| Zakeo 250 SC | SYNGENTA CROP PROTECTION AG |
| Timeline Trio | SYNGENTA CROP PROTECTION AG |
| Clematis | ALBAUGH TKI D.O.O |
| Parleaf | MICROCIDE LTD |

Eles sumiam do corpus porque **os 163 foram filtrados por titular ADAMA**. Ou seja: o universo comercial da ADAMA Itália é maior que o universo regulatório em nome dela.

E mais dois — **Budge e Exelgrow** — nem são fitossanitários: carregam número de registro de fertilizante. São bioestimulantes.

⚠️ **Um erro de método vale a pena registrar:** o segmento da URL **não é** a categoria. `Folpan Energy` mora em `/prodotti/erbicidi/` e a ficha o rotula **Fungicidi**. Contar pelo caminho daria 27/13/6/5 em vez de 26/14/6/5.

---

## MOST IMPORTANT NEW REAL DATA FOR CLIENT DEMO


**1. O peso econômico de cada cultura, por região**

983 linhas do ISTAT (cubo `101_1015 Coltivazioni`): 20 regiões + Itália, 15 culturas, 2024–2026, área em hectares e produção em quintais. Passou o teste de censo: a soma das 20 regiões bate com o total nacional. Agora o portal separa «praga em 200 ha» de «praga em 200 mil ha» — trigo duro tem 1.134.227 ha, e a barbabietola tem 18.680 ha em toda a Itália.

**2. O Vêneto deixou de ser um vazio**

O demo tem três casos no Vêneto e o pacote não tinha um boletim. Agora tem boletins do Servizio Fitosanitario de agosto e setembro de 2026 — vite 27/08, olivo 02/09, frutícola e hortícola 26/08.

**3. O calendário de vencimento ganhou causa europeia**

39 das 50 substâncias do portfólio (78%) estão em aprovação PRORROGADA — já venceu uma vez e foi esticada. E os agrupamentos italianos ficam explicados: nov/26 = 9 metamitron + 2 flonicamid; jan/27 = 10 pendimethalin + 5 bupirimate + 7 tau-fluvalinate.

**4. Quatro sinais de risco NOMEADOS em ata pública**

Não-renovação em rascunho para **fludioxonil** (comentários até 03/09/2026) e **fenmedifam**; revisão do Artigo 21 aberta sobre **tebuconazol** por classificação Tóxico para Reprodução 1B; e a Comissão registrando que para **clodinafop** uma não-renovação «provavelmente seria proposta». ⚠️ Prorrogação não é renovação, e nenhum destes é decisão tomada.

**5. A janela de herbicida corrente não era a que se supunha**

Em 02/09/2026 a única janela de diserbo comprovadamente aberta nos cereais de outono é a de **post-raccolta** (restolho), não pré-semeadura nem pré-emergência. Sai de boletim oficial datado de 19–20/08/2026.

**6. Dezoito vozes com nome, cargo provado e frase assinada**

Antes havia 58 falas de caixa de comentário e 15 pessoas sem nenhuma declaração. Agora há agricultores, dirigentes de organização, agrônomos, presidentes de consórcio e o serviço técnico do órgão nacional do arroz.

**7. Preço corrente para 6 das 7 culturas que estavam zeradas**

Só a barbabietola continua sem. E o ISMEA — a autoridade do setor — falou com este projeto pela primeira vez.

**8. Seis produtos do catálogo registrados em nome de outra empresa**

O universo comercial é maior que o regulatório filtrado por titular ADAMA.

---

## TOP 10 NEW CROSSINGS NOW POSSIBLE

Cada um só existe porque **duas** camadas novas se encontraram. Nenhum é uma afirmação: são perguntas que o portal agora consegue formular com lastro.

1. **convergência × peso econômico da região** — «este par cultura×alvo aparece numa região que responde por N% da área italiana da cultura» — antes o portal não sabia se a região era grande
2. **vencimento nacional × aprovação europeia × prorrogação** — os 101 produtos que vencem em 12 meses agora se separam entre os que dependem de substância prorrogada e os que não
3. **sinal de não-renovação × produtos do portfólio × cultura** — fludioxonil, fenmedifam, tebuconazol e clodinafop puxam produtos e culturas concretas
4. **boletim corrente do Vêneto × os três casos do demo no Vêneto** — pela primeira vez o caso tem evidência de campo da própria região
5. **janela de diserbo declarada × fase fenológica × produto de rótulo** — a janela post-raccolta cruza com os herbicidas autorizados para ela
6. **resistência GIRE × janela corrente × mecanismo do produto** — arroz × Echinochloa × ACCase, com a janela datada
7. **voz identificada × par cultura×alvo × região** — uma frase assinada por alguém com cargo, sobre o mesmo par que a régua achou
8. **clima como CONDIÇÃO × região × cultura** — ⚠️ e só como condição — nunca como presença de doença
9. **catálogo comercial × registro × titular** — o que a ADAMA vende, o que está registrado, e em nome de quem
10. **evento futuro × concorrente × cultura** — quem estará onde, quando a fonte publica — nunca inferido do ano passado

---

## O QUE CONTINUA FALTANDO, E POR QUÊ

| lacuna | motivo | é esforço ou é natureza? |
|---|---|---|
| 1 regiões sem boletim corrente | fonte fora do ar, DNS morto ou só imagem | esforço — as portas estão listadas |
| **frumento duro: zero boletim** | em ago/set já foi colhido; e a fonte da maior produtora descontinuou a fitopatologia em 2018 | **natureza** — a coleta certa é entre novembro e junho |
| barbabietola sem mercado | nenhuma fonte pública encontrada | esforço |
| pomodoro sem área regional | ISTAT tem, mas a chamada não voltou com corte regional | esforço |
| olivo e melo: área só por macro-área e de 2017 | o corte regional não existe nessa fonte | esforço — o ISTAT tem `OLIVTAB_OIL` e `APPLE` |
| Sicília sem boletim regional | o SIAS não abre em HTTPS | esforço |
| venda, share, estoque | dado interno, e o projeto é externo por decisão | **natureza** |

**Região ainda sem nenhum boletim corrente:** Valle d'Aosta.

⚠️ **A ressalva que o número esconde:** de 12 regiões sem nada passamos a 1. Mas **muitos dos boletins novos são PROVINCIAIS ou de AREAL** — a Campânia são cinco documentos provinciais separados, a Basilicata cobre só o Metapontino, a Sardenha só Oristano, e o Trentino só a província de Trento (o Sudtirol, maior área de maçã da Itália, continua sem fonte lida). `BOLETIM PROVINCIAL NÃO REPRESENTA A REGIÃO.` A cobertura subiu; o censo, não.

**Regiões alcançadas nesta missão:** Abruzzo, Basilicata, Calabria, Campania, Lazio, Liguria, Molise, Sardegna, Sicilia, Trentino-Alto Adige, Veneto.

---

## OS ARQUIVOS

```
research/italy-lastmile/LAST-MILE-REALITY-GAPS.md    este relatorio
research/italy-lastmile/LAST-MILE-REALITY-GAPS.json  as lacunas, por familia
research/italy-lastmile/NEW-REAL-DATA.json           321 registros
research/italy-lastmile/NEW-REAL-SOURCES.json        146 fontes, estado MEDIDO
data/samples/IT-ISTAT-COLTIVAZIONI/                  983 linhas de area/producao
data/samples/IT-LASTMILE/IT-ADAMA-CATALOGO.json      catalogo comercial
data/samples/IT-LASTMILE/IT-ROTA-*.json              o teste de rota, antes e depois
```
