# SINTONIA ITALY · REALITY HANDOFF V2.1

> **Este arquivo mora aqui, no código, e é COPIADO para dentro do pacote pela
> cadeia de construção.** Ele já foi escrito uma vez direto na pasta do pacote e
> desapareceu no build seguinte: `v21_ingest.py` faz `rmtree` da pasta inteira
> antes de reescrevê-la.
>
> **A porta de entrada não pode morar dentro do que a construção apaga.**

**Leia esta página antes de abrir qualquer arquivo.** Ela tem três minutos de
leitura e evita os quatro erros que o pacote anterior deixou acontecer.

---

## 1 · O que você recebeu

Duas pastas. Elas não são duas versões da mesma coisa.

```
DESIGN-INGEST/       ← o Design carrega DAQUI. 25 arquivos. É o contrato.
INTERNAL-ARCHIVE/    ← o rastro do trabalho. Auditorias, planos, relatórios.
                       Não é lixo, e não é para a tela.
```

> **Se você abrir só uma pasta, abra a primeira. Se abrir as duas, não misture.**

O pacote V2 falhou exatamente aqui: entregou pesquisa e dado no mesmo lugar, e
quem foi montar tela teve de adivinhar qual arquivo era qual.

---

## 2 · Por onde começar, em ordem

| Passo | Arquivo | Para quê |
|---|---|---|
| 1 | `DESIGN-INGEST/APP-MANIFEST.json` | diz **qual arquivo carregar** para cada coleção, e qual arquivo antigo ele aposenta |
| 2 | `DESIGN-INGEST/CANONICAL-INTELLIGENCE-MASTER.json` | o índice de tudo: cada registro com um lugar só |
| 3 | os 23 arquivos de coleção | o dado em si |
| 4 | `ACCEPTANCE-REPORT.json` (na raiz) | todo contador do pacote, recontado dos arquivos |

Não existe "arquivo velho" e "arquivo novo" para escolher. O manifesto declara,
para cada coleção, o que ela substitui. Carregar os dois conta o mesmo fato duas
vezes.

**Os números deste README podem envelhecer. Os do `ACCEPTANCE-REPORT.json` não:
ele é recontado dos arquivos a cada build.** Quando os dois discordarem, o
relatório está certo.

---

## 3 · A regra que decide o que vai para a tela

Cada registro tem um campo `CLIENT_SAFE`, verdadeiro ou falso.

```
CLIENT_SAFE = true   →  pode sustentar uma afirmação visível ao cliente
CLIENT_SAFE = false  →  vive no corpus, aparece como RESEARCH_LEADS,
                        e NUNCA sustenta afirmação sozinho
```

Não é uma sugestão de estilo. É a diferença entre um portal que se pode
defender numa sala com o cliente e um que não se pode.

Cerca de **2.9 mil dos 6.7 mil registros** são client-safe. Os outros não são
lixo: são o corpus. Existem para o analista puxar uma pergunta, não para o
portal fechar uma resposta.

> **O dado que não foi conferido pode abrir uma pergunta.
> Não pode fechar uma afirmação.**

Como se lê o carimbo:

| `QA_STATUS` | `CLIENT_SAFE` | O que quer dizer |
|---|---|---|
| `QA_PASS` | ✅ | alguém conferiu e passou |
| `QA_CORRECTED` | ✅ | alguém conferiu, achou erro, corrigiu, e a correção está escrita |
| `EVIDENCE_DOCUMENTED` | ✅ | lido em documento oficial, com fonte e data |
| `EVIDENCE_SOURCED` | ✅ | capturado de fonte pública identificada, com URL e data |
| `QA_UNREVIEWED` | ❌ | ninguém conferiu. Pode estar certo. Ninguém sabe. |
| `EVIDENCE_DERIVED` | ❌ | leitura nossa sobre fatos — vai à tela só com o método declarado ao lado |
| `QA_REJECTED` | ❌ | conferido e reprovado. Fica no pacote para que ninguém o recolete achando que é novo. |

---

## 4 · Língua: você nunca precisa mostrar português

Esta é a mudança mais visível do V2.1.

Todo campo interpretativo que vai à tela tem **três formas**:

```json
"WHAT_IT_DOES_NOT_PROVE_IT": "non prova efficacia, raccomandazione né priorità.",
"WHAT_IT_DOES_NOT_PROVE_EN": "does not prove efficacy, recommendation or priority.",
"WHAT_IT_DOES_NOT_PROVE_ORIGINAL_RESEARCH_TEXT": "nao prova eficacia, recomendacao nem prioridade."
```

O Design mostra `_IT` ou `_EN`. O `_ORIGINAL_RESEARCH_TEXT` fica embaixo, para
auditoria — nunca vai à tela.

Alguns registros ganharam um campo a mais, `*_PROMOVIDO_DE`. Eles são os que
guardavam a ressalva **só** dentro do bloco `RESEARCH`, em português, sem campo
nenhum na tela. A ressalva subiu, traduzida, e o bloco `RESEARCH` continua
intacto embaixo. O motivo é simples:

> **Se a única cópia da ressalva está numa língua que a tela não mostra, a tela
> não mostra a ressalva. E ressalva que não aparece é ressalva que não existe.**

### O que NÃO foi traduzido, de propósito

A citação. O comentário do agricultor em italiano, o texto do anúncio, a palavra
impressa no rótulo, o nome científico.

> **A citação é o documento. A leitura é a nossa opinião sobre ele.
> Só a segunda muda de língua.**

Traduzir a citação apagaria o que a fonte de fato disse — e é a fonte que
sustenta tudo. Os campos `TEXT_ORIGINAL`, `CREATIVE_TEXT`, `DESCRIPTION`,
`SPECIES_IT`, `PHENOLOGICAL_STAGE_DECLARED` e os trechos marcados `literal:`
ficam na língua em que foram publicados.

### Como se sabe que a tradução não mentiu

Passou por uma trava automática (`scripts/v21_traducao_trava.py`) que confere,
frase por frase: número preservado, data preservada, negação preservada, nome de
lugar preservado, palavra de incerteza preservada, CAIXA ALTA preservada.

A trava tem um teste próprio (`tests/test_v21_traducao_trava.py`) com mentiras
plantadas de propósito — uma para cada proibição — porque ela foi corrigida seis
vezes até parar de reprovar tradução correta, e

> **uma trava corrigida até passar pode ter virado um carimbo.**

O que ela **não** consegue conferir está escrito no cabeçalho dela, em vez de
escondido.

---

## 5 · As leis do domínio, que o Design tem de respeitar na tela

Estas não são preferências. Cada uma já foi quebrada por alguém, e o erro custou
credibilidade.

| Lei | O que ela impede |
|---|---|
| `ANÚNCIO ALCANÇOU O PAÍS ≠ ANÚNCIO MIRAVA O PAÍS` | dizer que a campanha era para a Itália porque foi vista lá |
| `COMENTÁRIO ≠ AGRICULTOR` | tratar quem comentou num vídeo como produtor rural |
| `TERMO DA CULTURA PRESENTE ≠ AUTORIZADO NA CULTURA` | ler o texto de marketing como se fosse o rótulo |
| `PRORROGAÇÃO ≠ RENOVAÇÃO` | anunciar que a substância foi renovada quando só ganhou prazo |
| `CONDIÇÃO ≠ PRESENÇA` | ler alerta de seca como se fosse presença de doença |
| `PROVINCIAL ≠ REGIONAL` | um boletim de Trento virar "Trentino-Alto Adige" |
| `PIAZZA ≠ NACIONAL` | preço de três praças virar "preço da Itália" |
| `CATÁLOGO ≠ TITULAR DE REGISTRO` | quem vende e quem registra são papéis diferentes |
| `VOZ ≠ INCIDÊNCIA` | contar comentários como se fossem casos no campo |
| `COMUNICAÇÃO ≠ PARTICIPAÇÃO DE MERCADO` | ler quem fala mais como quem vende mais |
| `CRUZAMENTO ≠ OPORTUNIDADE` | e esta é a mais importante de todas |

### A última merece parágrafo próprio

Os 20 registros em `CLIENT-SAFE-CROSSINGS.json` **não são oportunidades
comerciais**. Um cruzamento diz: *estes dois fatos, ambos conferidos, falam da
mesma cultura.* Só isso. Não prova demanda, não prova que o produto resolve o
problema, não prova que alguém vai comprar.

**E o nome do arquivo pede uma explicação.** "Client-safe" ali qualifica o
**apoio**, não o cruzamento: a invariante D prova que todo fato que o sustenta
passou no portão. Mas o cruzamento em si não foi lido em fonte nenhuma — fomos
nós que juntamos dois fatos e dissemos que falam da mesma cultura. Isso é
derivação, e derivação não passa no portão.

> **A regra vale para o que nós mesmos produzimos, ou não é regra.**

Por isso cada cruzamento vem assim:

```json
"QA_STATUS": "EVIDENCE_DERIVED",
"CLIENT_SAFE": false,
"ALL_SUPPORT_CLIENT_SAFE": true,
"RENDERABLE_WITH_METHOD": true,
"RENDER_RULE": "pode aparecer na tela, mas SEMPRE com WHAT_IT_DOES_NOT_PROVE
                visível ao lado — nunca atrás de um «saiba mais»."
```

⚠️ **Consequência prática para quem monta a tela:** se a interface filtrar por
`CLIENT_SAFE=true`, ela não mostra **nenhum** cruzamento. Filtre por
`RENDERABLE_WITH_METHOD`. E o `COUNT_CLIENT_SAFE` do arquivo diz `0`, de
propósito — um cabeçalho que promete mais do que o registro entrega é o pior
tipo de erro, porque só aparece na tela do cliente.

---

## 6 · O que mudou desde o V2

O V2 foi recusado por quatro defeitos. Os quatro estão fechados:

**1. Havia dois pacotes, não um.** O handoff anterior e a coleta last-mile
estavam empacotados lado a lado, sem índice comum. Agora há um só registro
central, com **zero IDs duplicados**.

**2. Os cruzamentos tinham junção falsa.** O V2 casava cultura por texto livre —
"riso" batia dentro de "compa*riso*n". Resultado: **36 IDs com cultura errada** e
**7 dos 19 cruzamentos apoiados em registro não conferido**. Foram jogados fora e
refeitos a partir de identificadores normalizados, com oito invariantes provadas
por programa antes de qualquer cruzamento sair:

```
0 cultura divergente   ·   0 apoio não-client-safe   ·   0 ID órfão
```

**3. Faltavam os dados granulares.** As 2.945 linhas atômicas do ISTAT tinham
sido resumidas em 33 afirmações; as linhas sumiram. Estão de volta — e carimbadas
`LAST_MILE`, não `DERIVED`, porque vieram de fora e não de cálculo nosso.

**4. Papel de trabalho estava misturado com dado.** Histórias de demo, planos
"fake-to-real", auditorias e quarentena estão em `INTERNAL-ARCHIVE/`.
`DESIGN-INGEST/` tem **zero** arquivos de pesquisa.

### E dois defeitos que só apareceram aqui

**5. A chave das fontes não ligava em nada.** As fontes estavam cadastradas sob
`IT-SRC-MINISTERO` e `SRCX_ARPAE_IT`, enquanto as 23 coleções citavam
`SRC_ARPAE_IT`. De 13.280 citações de fonte no pacote, **56% não encontravam
ninguém**. Agora a chave primária é a mesma que o pacote já citava, o
identificador antigo continua resolvendo por `ID_ALIASES`, e **todas as citações
resolvem**.

**6. Os cruzamentos não tinham carimbo.** O cabeçalho declarava 20 client-safe e
os registros não traziam `CLIENT_SAFE` nem `QA_STATUS` — a tela teria filtrado
os 20 e mostrado vazio. Ver o §5.

---

## 7 · O que este pacote NÃO tem, e não vai ter

Dito aqui para ninguém procurar:

- **Nada de dado interno da ADAMA.** Sem CRM, sem vendas, sem estoque, sem
  sell-in, sem sell-out, sem pedido, sem mensagem interna de campo. O SINTONIA
  é inteligência **externa**: tudo aqui é público e tem URL.
- **Nenhuma estimativa de faturamento.**
- **Nenhuma estimativa de participação de mercado da ADAMA.**
- **Nenhuma inferência de presença atual a partir de sazonalidade histórica.**
  "Costuma acontecer em agosto" não é "está acontecendo".

Se alguém pedir qualquer um dos quatro, a resposta é que o dado não existe neste
pacote — e não porque faltou coletar.

---

## 8 · Onde estão as coisas

```
DESIGN-INGEST/
  APP-MANIFEST.json                    ← comece aqui
  CANONICAL-INTELLIGENCE-MASTER.json   ← o índice de tudo

  CROP-ECONOMIC-WEIGHT.json    2978    área e produção por região (ISTAT/Eurostat)
  PRODUCT-RELATIONSHIPS.json   2030    par produto × cultura × alvo, com a
                                       força do vínculo declarada
  COMPETITOR-ACTIVITIES.json    577    comunicação pública de concorrentes
  SOURCES.json                  185    de onde cada coisa veio, e se a rota abriu
  PRODUCTS-REGULATORY.json      163    rótulos do Ministero, lidos em PDF
  MARKET-OBSERVATIONS.json      157    preço de praça, com o escopo declarado
  CURRENT-FIELD-SIGNALS.json    122    boletins fitossanitários correntes
  SCIENCE.json                   88    literatura
  PUBLIC-VOICES.json             79    o que se falou em público
  PUBLIC-CHANNELS.json           62    onde se fala
  RESEARCHERS.json               60    quem publica
  PRODUCTS-COMMERCIAL.json       51    catálogo comercial ADAMA Italia
  AGROMET-CONDITIONS.json        44    clima — que é CONDIÇÃO, não presença
  EVENTS.json                    40    encontros do setor
  RESISTANCE.json                34    resistência documentada
  REGULATORY-FUTURE.json         28    o que está em consulta, não decidido
  FUTURE-EVENTS.json             23    ⚠️ RECORTE de EVENTS, não coleção nova
  CLIENT-SAFE-CROSSINGS.json     20    os cruzamentos — leia o §5 antes
  RELATIONSHIPS.json             20    ⚠️ espelho dos cruzamentos, por desenho
  NEWS.json                       8    notícia
  CROP-WINDOWS.json               7    janelas de lotta obbligatoria
  OPPORTUNITIES.json              3    ⚠️ nenhum é client-safe
  FUTURE-SIGNALS.json             3    sinal futuro
```

⚠️ **`FUTURE-EVENTS.json` e `RELATIONSHIPS.json` são vistas, não coleções.**
Carregá-las junto com `EVENTS.json` e `CLIENT-SAFE-CROSSINGS.json` conta o mesmo
registro duas vezes. Por isso não entram no registro central — o índice diz isso
em `VIEWS_NOT_INDEXED`.

---

## 9 · Quando você achar que faltou alguma coisa

Antes de pedir mais coleta, olhe se a ausência não é o resultado.

Antes, sete das dez culturas do piloto não tinham dado de mercado. **Hoje as dez
têm** — a rodada *last-mile* fechou essa lacuna, e esta frase ficou desatualizada
até a reverificação apanhá-la. Uma região continua sem boletim corrente. Isso não
é buraco de coleta: é censo. Foi procurado, e não existe fonte pública.

Sobre o teste de rota, o número exato, porque o anterior prometia demais:
`SOURCES.json` guarda **o que aconteceu** (`ACCESS_EVIDENCE`) e **por onde a
requisição saiu** (`REQUIRES_ITALIAN_ROUTE`) em **128 das 185 fontes**. As **185**
trazem `ACCESS_STATE` ou `ACCESS_STATUS`, que responde "a rota abriu?" — e só
isso. Nas **31 fontes client-safe**, herdadas do handoff anterior, existe apenas
`ACCESS_STATUS`: elas nunca passaram pela medição de rota, que é artefato da
rodada *last-mile*.

> **O TESTE DE ROTA NÃO COBRE "CADA FONTE". COBRE AS QUE FORAM MEDIDAS.**
> Dizer "cada" numa página que o Design lê é prometer uma checagem que não
> existe para a fonte que ele estiver olhando.

E uma rodada só não responde "por onde saiu": um coletor já concluiu que o ISMEA
nunca fora bloqueado porque recebeu HTTP 200 — com a VPN ligada, sem saber. Por
isso `ROUTE_EVIDENCE_NOTE` diz, em cada fonte medida, se houve uma rodada ou duas.

Há também duas fontes que **não são fontes**: `SRC_NAO_DECLARADA` e
`SRC_DESCONHECIDA` aparecem como sentinelas, com `IS_SOURCE: false`. Elas marcam
"este registro não declarou origem". A tela mostra o aviso, **nunca um link** —
porque link que não abre o usuário lê como defeito do portal, e não como
ausência declarada do dado.

> **A ausência de dado é um dado — desde que se tenha procurado direito e se diga
> onde se procurou.**

---

## 10 · Como o pacote se reconstrói

```bash
bash scripts/v21_cadeia.sh
```

A ordem importa e não é adivinhável: o passo 1 apaga a pasta inteira e reescreve
as coleções. Rodar um passo do meio sozinho apaga em silêncio o carimbo de
origem, o rechaveamento das fontes e as traduções já aplicadas — nada quebra,
nada reclama, e o pacote fica com menos do que tinha, parecendo inteiro.

> **O passo que apaga sem avisar é pior que o passo que falha. O que falha, se vê.**
