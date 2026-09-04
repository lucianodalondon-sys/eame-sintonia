# PACOTE DO SPRINT — PORTAL ITÁLIA

**Data:** 2026-09-04 · **HEAD de partida:** `0fc50dd` · **Regra:** só entra o que é defensável hoje

> **Este documento responde a uma pergunta só: o que o Portal Itália pode dizer na segunda-feira
> sem que alguém consiga derrubar?** Ele não desenha tela. Ele separa o que tem prova do que
> não tem, e dá o texto de incerteza para o que fica no meio.
>
> **M7 está congelada (D-040).** Nenhuma afirmação aqui se apoia em legenda — nenhuma foi obtida.

---

## 0 · DUAS TRAVAS DE GOVERNANÇA QUE VALEM ANTES DE QUALQUER COISA

**`PROTOTYPE_FROZEN = SIM` (D-007).** `prototype/portal/` está congelado por decisão do
cliente: *"Claude descobre o produto. Claude Design desenha o produto."* Este pacote é a
descoberta **em texto**, que é o que D-007 pede. **Descongelar o protótipo é decisão do dono,
não minha** — e nada aqui depende disso.

**"Duas ferramentas e uma pergunta", não um menu.** `ARQUITETURA-DE-PRODUTO-ATUAL.md` é a
porta única de arquitetura de produto e proíbe explicitamente *"desenhar um menu de módulos
independentes"*. A lista de dez itens desta rodada **mapeia** sobre ela, e é assim que a li:

| item do sprint | onde ele já mora |
|---|---|
| Radar Agora | HOME — *"o que merece atenção agora?"* |
| Radar Futuro · portfólio/regulatório · concorrência | **MT1** · Regulatory & Expiry Exposure |
| geografia | **MT2** · Geographic Commercial Priority |
| **oportunidades** | **MT3** · e MT3 **nunca** se chama oportunidade — ver §3 |
| vozes | motor de apoio, hoje `PARCIAL` |
| mapa de ação departamental | campo `ADAMA_USERS` por área, já escrito |

---

## 1 · INGESTÃO DO ACERVO EXISTENTE — `PARCIAL`, e há um bloqueio de uma linha

### O bloqueio, medido

Três scripts codificam um caminho que **não existe neste checkout**:

```
scripts/ask_sintonia.py:19        data/raw/IT-T4-001/PROD_FTS_6_20260824.csv
scripts/normalize_substance.py:34 data/raw/IT-T4-001/PROD_FTS_6_20260824.csv
scripts/data_clock.py:25          data/raw/IT-T4-001/PROD_FTS_6_20260824.csv

em disco:                         data/raw/IT-T4-001/PROD_FTS.csv   (17.695 registros)
```

`scripts/chain.py:286` faz certo — varre `PROD_FTS*.csv` e acha. Os outros três não.
**Consequência já visível:** `DATA-CLOCK-manifest.json` marca `IT-T4-001` como `AUSENTE`
enquanto o dado está ali, com a contagem batendo (`products_total = 17695`).

> **Correção ao meu próprio rascunho:** o `AUSENTE` **não é um defeito italiano**. São
> **6 linhas em 3 fontes** — `FR-T4-001` ×3, `ES-T3-001` ×2, `IT-T4-001` ×1 — e a causa é
> `data/raw/` não ser versionado (D-003). Atinge a França mais que a Itália. O que **é**
> específico da Itália é o caminho errado nos três scripts.

O conserto é trivial, e a escolha não é: **renomear o arquivo com o carimbo de versão** (e o
carimbo passa a viver no nome, onde se vê) **ou fazer os três usarem o glob do `chain.py`**
(e o carimbo continua só dentro do JSON). `data/raw/` não é versionado por D-003 — então em
um clone novo o arquivo não existe de forma nenhuma, e **a amostra em `data/samples/` é a
evidência preservada**, não o CSV.

### O que já está ingerido e medido

| artefato | número | estado |
|---|---|---|
| `IT-T4-001/IT-T4-001-adama-expiries.json` | 17.695 produtos · 3.712 vigentes · 155 ADAMA com vencimento futuro | `COMPROVADO`, **com ressalva de critério** (§2) |
| `IT-HUMAN-SENSORS/ENTITIES.json` | 221 entidades | `COMPROVADO` |
| `IT-HUMAN-SENSORS/SOURCES.json` | **334 fontes** — 243 ligadas a entidade, **91 órfãs** · 89 canais monitoráveis | `COMPROVADO` |
| `IT-HUMAN-SENSORS/COVERAGE.json` | 117 células CROP×REGION×SPECIALTY — 72 GOOD · 29 WEAK · 16 NONE | `COMPROVADO` |
| `IT-HUMAN-SENSORS/PILOT-MEASUREMENT.json` | 150 documentos · 7 operacionais · **82 não julgáveis** | `COMPROVADO` |
| `COMPETITOR-azoxy-prothio-italy.json` · `CROSS-MARKET-prothioconazole-cereal.json` | casos IT já documentados | `COMPROVADO` |

---

## 2 · O NÚMERO ITALIANO TEM DOIS EIXOS, E A HOME PUBLICA UM SÓ

`build_portal.py:189` leva para a home: *"155 autorizações ADAMA na Itália têm vencimento
futuro"*. O `chain.py:389` já tinha escrito a lei que esse número viola:

> **"Os dois são defensáveis; publicar sem o critério não é."**

Medido por mim sobre `PROD_FTS.csv`, a mesma pergunta tem **quatro** respostas:

| | STRICT — só estados com "Autorizzato" | AMPLIADO — + `Ri-registrato` / `Rinnovato` |
|---|---|---|
| **ADAMA — as 5 razões sociais** | 89 | **155** ← é este que está na home |
| **só `ADAMA ITALIA S.R.L.`** | 39 | 77 |

*(vigentes com vencimento futuro na data do snapshot, 24/08/2026)*

As cinco razões sociais são reais e distintas: `ADAMA ITALIA S.R.L.` · `ADAMA AGAN LTD` ·
`ADAMA DEUTSCHLAND GMBH` · `ADAMA IRVITA N.V.` · `ADAMA MAKHTESHIM LTD`. Agrupá-las é
**julgamento humano** (é o que `chain.py` chama de `by_group_HUMAN_JUDGMENT`), não um fato do
registro — e é exatamente a lacuna DECK-015.

> **Regra para a tela:** todo número de vigência italiano carrega **dois eixos declarados** —
> *qual critério de vigência* e *qual ADAMA*. Sem os dois, o número não vai para a tela.

### E há um caso pior que "número sem dono": um número **certo** sem dono

O card italiano da home diz, hoje:

> *"58 delas vencem em até 6 meses (37,4%), contra 20,9% do mercado."*

Esses três valores estão **digitados à mão** em `scripts/build_portal.py:191`, dentro de um
bloco marcado `REAL`. **Eu os reproduzi, e eles estão certos** — critério AMPLIADO, as cinco
razões sociais ADAMA somadas, snapshot de 24/08:

```
AMPLIADO · ADAMA×5 · futuro=155 · ≤6 meses=58 · 37,4%      ← bate
AMPLIADO · mercado · futuro=3466 · ≤6 meses=724 · 20,9%    ← bate
```

Estar certo não os salva. **Nenhum arquivo em `data/samples/` contém 58, 37,4 ou 20,9** — para
auditá-los é preciso re-derivar de um CSV que não é versionado. E a docstring do próprio script
promete o contrário:

> *"Regra do protótipo: nenhum número é digitado à mão neste script."*

Medido falso em pelo menos dois pontos: a linha 191 (o card italiano) e a linha 66
(`peaks = {'Huelva': 26.4, 'Cordoba': 6.4, 'Cadiz (Jerez)': 0.0}`, que alimenta um bloco também
marcado `REAL`). **E o teste não pega:** `tests/test_evidence.py` verifica que o *caminho* da
evidência existe — nunca que o número exibido veio dele.

> **Um número certo que ninguém consegue auditar é pior que um errado:** o errado alguém
> derruba; este passa no teste, parece rastreável e não é. E ele escolhe em silêncio os dois
> eixos desta seção.

**E o eixo tem um terceiro degrau, que eu só vi ao reconciliar uma diferença de 1:**

```
3.711   "Autorizzato*" + "Ri-registrato*" + "Rinnovato*"        ← minha contagem
3.712   o que o artefato publica                                 ← critério não declarado
3.714   tudo que não é "Revocato" nem "Scaduto"
```

Os três números diferem por **cinco registros**, e eles têm nome: `Sospeso` (3) e
`Autorizzato provvisoriamente` (2). **Uma autorização suspensa não está vigente nem revogada** —
é o caso genuinamente ambíguo, e nenhum dos três critérios diz o que faz com ela. Não é erro de
contagem: é uma decisão de vocabulário que ninguém tomou ainda.

Enquanto ela não for tomada: **`NÃO SEI` para `Sospeso`**, declarado, em vez de somado em
silêncio a um dos lados.

*(Também no dataset, e ainda não usado: `Autorizzato in deroga (art. 53 Reg. 1107/2009)` — 19
registros. Na Espanha essa é uma capacidade inteira, "necessidade sem solução autorizada". Na
Itália são 19 linhas que ninguém abriu.)*

---

## 3 · A ITÁLIA SABE UMA COISA QUE A ESPANHA NÃO SABE

O acervo espanhol proíbe ler `EXPIRED` como `WITHDRAWN` — e prova por quê: 34 registros
`Vigente` com caducidade passada. **A Itália publica a coluna que falta à Espanha:**

```
stato_amministrativo   Revocato 13.216 · Autorizzato 1.181 · Ri-registrato 1.052 · Scaduto 765 · ...
motivo_della revoca    data_decreto_revoca    data_decorrenza_revoca
```

`Revocato` e `Scaduto` são **estados administrativos separados**. E a prova de que a distinção
importa está no próprio dado: **223 autorizações estão `Revocato` com data de vencimento ainda
no futuro** — 22 delas ADAMA, algumas com vencimento em 2040. Quem ordenar por
`data_scadenza_autorizzazione` sem olhar o estado vai contar produto revogado como vivo.

**A ressalva, que é grande:** dos 13.216 `Revocato`, só **1.119 trazem motivo** e **907 trazem
data de decreto**. A coluna existe; o preenchimento é de ~8%. Então:

- **`COMPROVADO`:** a Itália separa revogação de vencimento, e 223 casos mostram a diferença.
- **`NÃO SEI`:** *por que* a maioria foi revogada. Sem motivo declarado, não se infere.

---

## 4 · RADAR FUTURO — `PARCIAL`, e o relógio é parte do fato

A Itália publica `data_scadenza_autorizzazione`. Isso torna o Radar Futuro a área **mais
madura** do Portal Itália — o backtest já dizia que *só o regulatório antecipa, e porque a
data é publicada*.

**Mas o snapshot é de 24/08/2026 e hoje é 04/09/2026.** A lista `adama_next_expiries` traz 20
datas e para em 31/10/2026. **Sete delas já passaram.** `build_portal.py:136` mostra as dez
primeiras — ou seja, uma tela de *"próximos vencimentos"* exibiria hoje **sete vencimentos
passados como futuros**.

```
2026-08-31  LAMDEX EXTRA · LUMA-KL · FORZA · NINJA · DURAVIS · ELTIRA · ARRODIM   ← já passaram
2026-09-30  CONTATTO 320                                                          ← ainda futuro
```

E o efeito no agregado: os **155** de 24/08 são **148** hoje.

> **Regra para a tela:** *futuro* se calcula contra a data de leitura, não contra a data do
> snapshot — e a data do snapshot aparece ao lado do número. **Um radar de futuro construído
> sobre um passado é pior que radar nenhum.**

---

## 5 · RADAR AGORA — `QUASE VAZIO`, e o que sobra não pode se chamar "agora"

`Radar Agora` responde *"o que está acontecendo agora"*. Para a Espanha existe base: o RAIF
dá incidência medida, semanal, com 23 safras. **Para a Itália não há equivalente medido no
acervo.** O que a Itália tem é:

- registro regulatório — que é **estado**, não evento de campo, e de um snapshot de 24/08;
- 150 documentos sociais do piloto — dos quais **82 não são julgáveis** e nenhum tem legenda.

E há uma razão mais básica que a falta de campo, medida nos próprios documentos:

```
PUBLICATION_DATE = NOT_KNOWN   em 150 de 150
REGION           = "NÃO SEI"   em 150 de 150
CROP             = "NÃO SEI"   em 101 de 150
```

**Nenhum documento do piloto tem data de publicação.** Sem data não há "agora": não dá nem
para ordenar.

**Mas existe um sinal grosso, e ele muda o veredito de VAZIO para QUASE:** o campo
`PUBLICATION_RELATIVE` está preenchido — *"hace 2 semanas"* (11), *"hace 1 mes"* (16),
*"hace 1 año"* (19), *"hace 10 años"* (10). É idade **relativa**, em espanhol, como o YouTube a
serviu. Dá para **ordenar por faixa de recência**; não dá para **datar nada**.

**E não são 150 utilizáveis, são 147:** três valores são lixo de DOM que entrou no campo —
`Añadir a la cola`, `48 K visualizaciones`, `18 K visualizaciones`. Precisam ser recusados na
leitura, não exibidos.

**Há ainda um fato que fecha a porta do "agora" por outro lado:** `ULTIMA_COLETA = None` em
**243 de 243** fontes. **Nenhuma fonte italiana foi coletada duas vezes.** Sem segunda
passagem não existe linha de base, e sem linha de base não existe "mudou" — só "é assim".

E a camada que converteria relativo em data exata é, por desenho, a página do vídeo — que é
justamente a camada congelada em D-040. O `youtube_janela.py` já dizia isso antes de nós:
*"a grade dá data RELATIVA. Quem precisa do dia exato abre a página do vídeo."*

> **Veredito honesto do Radar Agora italiano:** pode existir como **ordenação por faixa de
> recência, sem nenhuma data na tela**, e sem chamar isso de "agora". Qualquer data exibida
> seria inventada. E a camada de campo medida — a que daria um "agora" de verdade — continua
> não existindo para a Itália (P-010, P-011).

---

## 6 · CONCORRÊNCIA — `PRONTO` no registro, e a história italiana não é a espanhola

Na Espanha a manchete era *"Syngenta 37 e ADAMA 36 são os dois titulares mais expostos"*.
**Na Itália a ADAMA não está no topo.** Titulares por autorizações vigentes com vencimento
futuro (critério AMPLIADO, snapshot 24/08):

```
SHARDA CROPCHEM ESPANA S.L.        231
NUFARM ITALIA S.R.L.               171
GOWAN ITALIA S.R.L.                163
SYNGENTA ITALIA S.P.A.             152
CORTEVA AGRISCIENCE ITALIA S.R.L.  132
BAYER CROPSCIENCE S.R.L.           122
...
ADAMA (5 razões sociais somadas)   155   ← só existe como número se alguém agrupar
```

**Duas ressalvas obrigatórias:** contagem de registros **não é participação de mercado** (regra
já escrita); e a posição da ADAMA depende do agrupamento das cinco razões sociais — um
julgamento humano, não um fato.

### E há um caso italiano completo, não amostrado — o melhor material da apresentação

Filtrei o registro por `AZOXYSTROBIN` **e** `PROTHIOCONAZOLE` no mesmo produto. São
**exatamente quatro**, todos vigentes — a lista é o universo, não uma amostra:

| produto | registro | titular | vencimento |
|---|---|---|---|
| MAXENTIS | 018067 | ADAMA ITALIA S.R.L. | **31/05/2027** |
| KOJAMI | 019095 | ADAMA ITALIA S.R.L. | **31/05/2027** |
| PROMINO XTRA | 019093 | CAC CHEMICAL GMBH | **31/03/2028** |
| AMISTAR ERA 240 EC | 019194 | CAC CHEMICAL GMBH | **31/03/2028** |

**O concorrente tem dez meses a mais de janela, na mesma dupla de substâncias.** É um fato
datado, de fonte oficial, com o universo fechado — e não precisa de nenhuma camada que não
temos.

> **A ressalva que impede o erro fácil:** o ato europeu do protioconazol e o registro italiano
> **não são duas fontes independentes**. O nacional deriva do europeu. Tratá-los como duas
> confirmações infla a confiança de um fato que tem uma origem só.

**Defeito de dado a corrigir antes de qualquer tela:** o nome `UPL HOLDINGS COÃPERATIEF U.A.`
vem corrompido na origem (mojibake de UTF-8 lido como Latin-1). Nome de empresa errado na tela
é erro que o cliente vê primeiro.

---

## 7 · PORTFÓLIO — `PARCIAL`, e falta a coluna que mais importa

`attivita` classifica o produto: `FUNGICIDA` 3.903 · `DISERBANTE` 2.307 · `INSETTICIDA` 2.009 ·
`FITOREGOLATORE` 458 · `NEMATOCIDA` 233 · ... e **`-` em 7.595 registros**, que é `NÃO SEI`,
não "outros".

**O que a Itália não publica: `coltura × avversità`.** As 26 colunas do dataset não têm cultura
nem alvo (P-010). Então o Portal Itália **não pode** responder *"que produto é autorizado para
esta cultura contra esta doença"* — que é justamente o que a França publica e a Itália não.
A assimetria entre países é fato do produto, e a tela tem de mostrá-la em vez de escondê-la.

---

## 8 · GEOGRAFIA — `PARCIAL`, com uma armadilha que precisa ser dita em voz alta

O registro italiano traz `comune_sede_legale` e `provincia_sede_legale`. **É o endereço da sede
do titular** — geografia `BASE` de uma empresa, não onde o produto é usado nem onde há
problema. Medido, entre as 3.711 vigentes:

```
-                1.899   ← 51% não têm província nenhuma
MILANO             506
BERGAMO            291
BOLOGNA            216
RAVENNA            194
```

Um mapa da Itália pintado com isso mostra **onde ficam os escritórios das empresas de
defensivo**. Não é geografia agronômica, e apresentá-la como tal seria erro de categoria.

**E os documentos coletados não ajudam:** `REGION = "NÃO SEI — o título não declara região"`
em **150 de 150**. A geografia simplesmente não foi medida nesse corpus.

**A geografia italiana defensável é outra:** a matriz de cobertura dos sensores humanos —
117 células CROP×REGION×SPECIALTY, 72 `GOOD` · 29 `WEAK` · 16 `NONE`, em 16+ regiões, com as
lacunas nomeadas (a maior: `CEREAL × EMILIA-ROMAGNA × APHIDS`, zero sensores, com âncora ADAMA
`PIRIMICARB | FLONICAMID | LAMBDA-CYHALOTHRIN`).

> **Mais da metade desse 72 é uma regra, não um sensor — e a regra não estava publicada.**
> Uma organização territorial Tier A/B **sem especialidade declarada** cobre todas as
> especialidades da sua cultura naquela região (o bollettino é multi-alvo por construção).
> São **36 sensores de 171**. Medido, desligando a expansão sobre os mesmos dados:
>
> ```
> COM expansão (publicado)   GOOD 72 · WEAK 29 · NONE 16
> SEM expansão               GOOD 30 · WEAK 43 · NONE 44
> ```
>
> A regra é defensável; publicá-la escondida não era. **Corrigido nesta rodada:** `COVERAGE.json`
> agora declara a expansão no próprio campo `RULE` e publica `BY_STATE_SEM_EXPANSAO`. Os
> números não mudaram — mudou o que dá para saber sobre eles.

> **E ela responde a uma pergunta diferente da que parece.** Diz **onde temos olhos**, não onde
> há problema. Uma célula `NONE` é uma lacuna nossa, não uma região sem doença.

---

## 9 · VOZES — `PARCIAL`, e o número honesto é 7 em 150

| medida | valor | arquivo |
|---|---|---|
| entidades italianas | 221 | `ENTITIES.json` |
| fontes | **334** — 243 ligadas · **91 órfãs** · **89 monitoráveis** | `SOURCES.json` |
| documentos do piloto | 150 | `PILOT-MEASUREMENT.json` |
| com valor operacional | **7** (1 FIELD_SIGNAL · 4 TECHNICAL · 2 RESEARCH) | idem |
| **não julgáveis só pelo título** | **82** | idem |
| **existência de legenda** | **`NÃO SEI` em 150 de 150** — ver abaixo | idem |

### `HAS_CAPTION = 0` é um valor padrão, não uma medição

Isto eu escrevi errado no primeiro rascunho e a auditoria pegou. Abri `LEGENDAS.json`:

```
10 itens · 10 PORTA_NAO_ABRIU · todos do MESMO canal (IT-S-000064, 1 de 15)
motivo idêntico nos dez: "NAVEGADOR_NAO_ALCANCADO: sem Chrome nesta máquina"
```

**140 dos 150 documentos nunca foram tentados. E nenhum vídeo respondeu "não há faixa".**
O `False` em 150/150 é o valor com que o campo nasce, não o resultado de uma medida — e
dizer *"nenhum desses vídeos tem legenda"* seria exatamente a lei 1 de D-040 violada, agora
num caso ainda mais fraco: ali o player foi negado; aqui **a porta nem abriu**.

**Texto correto para a tela:** *"Existência de legenda: **NÃO SEI em 150 de 150**. Dez
tentativas, num único canal, e a porta não abriu. Nenhum vídeo respondeu 'não há legenda'."*

### E os 61 saem do mesmo classificador que os 82

O arquivo declara o próprio limite: `LIMITE_DO_CLASSIFICADOR = "LEXICAL sobre título +
legenda. Polissemia produz falso positivo e nenhum portão automático detecta. Todo item
carrega o trecho; verificação é humana."`

**Não há legenda, e a verificação humana não foi executada.** Então o classificador rodou
sobre metade do que foi desenhado para ler — e os 61 e os 82 vêm da **mesma passada**.
Proteger um número e publicar o outro como se fosse mais sólido é incoerente.

**Texto correto:** *"61 por casamento lexical de título, não verificados."*

### Os papéis, contados como pessoas e não como linhas

| medida | valor |
|---|---|
| entradas de papel | 278 |
| entradas com estado `PROVADO` | 114 |
| **entidades com ≥1 papel provado** | **90** de 221 |
| papéis provados: `pesquisador` 64 · `professor` 36 · `estudante` 9 | |
| **papéis de campo provados: `tecnico` 3 · `cooperativa` 2** | **5 no total** |
| **`agronomo`, `produtor`, `consultor` provados** | **0** |

**114 é contagem de linhas, não de gente.** E o número que a tela precisa carregar é o
último: **zero agrônomos, produtores ou consultores com papel provado por campo estruturado.**
O grupo A de 8 canais usa `PROVADO` **ou** `PROBABLE`; só `PROVADO`, o campo encolhe a 5.

### As 91 fontes órfãs não são um estoque de reserva

`QUALIFICADO = false` em **91/91**; `PAIS = NÃO SEI` em **67**; e **16 declaram Estados
Unidos** (mais AU 2, Irlanda 2, CA 1, Pakistan 1). Nenhuma é sensor italiano qualificado, e
cada registro diz isso de si mesmo.

**Os 82 são o número mais importante desta seção, e não podem sumir da tela.** Eles não são
`OFF_TOPIC` — `OFF_TOPIC` exige evidência positiva de assunto não-agrícola (D-032). Eles são
`NÃO SEI`, com motivo: *"título insuficiente e sem legenda; não foi medido"*.

- **Esconder os 82** = mentir por omissão: 7 em 68 parece muito melhor que 7 em 150.
- **Classificá-los** = mentir por invenção.

**Bloqueio jurídico aberto (P-012):** a camada nomeia pessoas com afiliação e ORCID. Qualquer
tela que liste gente identificada precisa de revisão GDPR **antes**, não depois.

---

## 10 · OPORTUNIDADES — o rótulo é proibido, e não é preciosismo

`ARQUITETURA-DE-PRODUTO-ATUAL.md` proíbe, nesta ordem: `SALES OPPORTUNITY` · `UNDERUSED ASSET`
· `WHITE SPACE CONFIRMED`. MT3 entrega **`ACTIVATION QUESTION`** — uma pergunta que a ADAMA
responde, não uma conclusão que nós entregamos.

E para a Itália há um degrau a mais: MT3 cruza **força registrada × atividade pública
observada**, e a atividade pública italiana observada hoje é **7 documentos úteis em 150, com
82 ilegíveis**. Com essa base, nem a pergunta se sustenta ainda.

> O correto para a Itália: **`NO PUBLIC ACTIVITY MEASURED IN SEARCHED SOURCES`** — nunca
> *"concorrente silencioso"*, nunca *"espaço livre"*.

---

## 11 · MAPA DE AÇÃO DEPARTAMENTAL — semente existe, mapa não

`ARQUITETURA-DE-INFORMACAO-EAME.md` já nomeia o consumidor de cada área no campo
`ADAMA_USERS`: `REGULATORY` · `PORTFOLIO` · `MD` · `TECHNICAL` · `COMMERCIAL` · `MARKETING` ·
`R&D` · `COUNTRY` · `EAME`. É o esqueleto certo — mas está escrito para o acervo **inteiro**,
não para a Itália.

Cruzando com o que este documento mediu:

| departamento | tem material italiano defensável hoje? |
|---|---|
| **REGULATORY** | **SIM** — vencimentos, revogação, estado administrativo (§2, §3, §4) |
| **PORTFOLIO** | **SIM, parcial** — `attivita` e substâncias; **sem cultura×alvo** (§7) |
| **MD / COUNTRY** | **NÃO** — depende de campo medido, que a Itália não tem (§5) |
| **TECHNICAL** | **NÃO** — mesma causa |
| **MARKETING** | **NÃO** — MT3 não se sustenta com 7 em 150 (§10) |
| **R&D** | **PARCIAL** — a camada científica existe; a ponte com o campo, não |

---

## 12 · O QUE NÃO PODE SER DITO NA APRESENTAÇÃO

| alguém vai querer dizer | por que não pode | o que se diz no lugar |
|---|---|---|
| *"155 autorizações ADAMA vencendo"* | sem critério e sem dizer qual ADAMA; são 4 números | *"155 — critério AMPLIADO, cinco razões sociais somadas, snapshot de 24/08"* |
| *"próximos vencimentos"* mostrando 31/08 | 7 dos 20 já passaram | futuro contra a data de leitura, com a data do snapshot ao lado |
| *"X produtos foram retirados do mercado"* | `Revocato` sem motivo em 92% dos casos | *"revogados; motivo declarado em 1.119 de 13.216"* |
| *"a ADAMA é a mais exposta na Itália"* | é a 4ª agrupada, e não entra no top 10 desagregada | a tabela inteira, com o critério de agrupamento visível |
| um mapa da Itália pintado pelo registro | é endereço de sede, e 51% está vazio | mapa de **cobertura de sensores**, dito como "onde temos olhos" |
| *"61 documentos relevantes de 150"* | 82 não foram julgados | *"7 operacionais · 61 relevantes · **82 não medidos**, de 150"* |
| *"oportunidade"* / *"espaço livre"* | proibido pela arquitetura | `ACTIVATION QUESTION`, ou nada |
| *"58 vencem em 6 meses — 37,4% contra 20,9% do mercado"* | está certo **e** está digitado à mão em `build_portal.py:191`; não existe em arquivo nenhum | ou vira artefato auditável, ou sai da tela |
| *"nenhum número da tela foi digitado à mão"* (docstring do script e rodapé do portal) | falso em pelo menos `build_portal.py:66` e `:191` | corrigir a afirmação **ou** o script — nunca deixar as duas |
| *"temos um Portal Itália"* | dos 16 blocos do protótipo, **1 é italiano** (ES 6 · UE/multi 7 · FR 2 · IT 1) | *"um portal EAME com um bloco italiano"* |
| *"o portal está no ar"* | não há pipeline de publicação: nenhum dos 10 workflows menciona portal, build ou deploy | *"gera um HTML estático, reproduzível, não publicado"* |
| qualquer data em documento social italiano | `PUBLICATION_DATE = NOT_KNOWN` em 150 de 150 | faixa de recência (*"há ~2 semanas"*), nunca uma data |
| qualquer região vinda dos documentos | `REGION = NÃO SEI` em 150 de 150 | a matriz de cobertura, dita como *"onde temos olhos"* |
| *"esses vídeos não têm legenda"* / `HAS_CAPTION = 0` | 140 de 150 **nunca foram tentados**; os 10 tentados deram `PORTA_NAO_ABRIU`, todos do mesmo canal | *"existência de legenda: NÃO SEI em 150 de 150"* |
| *"61 documentos relevantes"* sem ressalva | mesmo classificador dos 82, sem legenda e sem verificação humana | *"61 por casamento lexical de título, não verificados"* |
| *"114 pesquisadores italianos"* | 114 são **entradas de papel**, não pessoas | *"90 entidades com ≥1 papel provado, de 221"* |
| *"temos agrônomos e produtores na base"* | provados por campo estruturado: **zero** | *"5 papéis de campo provados: 3 técnicos, 2 cooperativas"* |
| *"cobertura BOA em 72 células"* sem a regra | 42 das 72 dependem da expansão territorial | *"72 com a expansão declarada; 30 sem ela"* |
| *"mais 91 canais monitoráveis"* | `QUALIFICADO = false` em 91/91; 16 declaram os EUA | *"91 descobertos, não qualificados, sem entidade"* |
| qualquer recência da camada territorial | a leitura de data estava truncando 70% das datas ISO | agora corrigida — mas **remedir antes de exibir** |
| qualquer coisa vinda de legenda | nenhuma legenda foi obtida (D-040) | silêncio — e a lei 5 de D-040 explica por quê |

---

## 13 · A MENOR SEQUÊNCIA ATÉ UMA APRESENTAÇÃO DEFENSÁVEL

Sem coleta nova, sem legenda, sem Twitter/LinkedIn, sem escala. Em ordem de dependência:

| # | passo | destrava | custo |
|---|---|---|---|
| 1 | **Consertar o caminho do CSV italiano** (3 scripts) | a ingestão italiana volta a rodar; o data clock para de mentir `AUSENTE` | uma linha × 3 |
| 2 | **Carimbar critério e recorte em todo número italiano** | §2, §6 e §7 param de ser refutáveis | reescrever o artefato com os dois eixos |
| 3 | **Recalcular "futuro" contra a data de leitura** | §4 — o Radar Futuro deixa de mostrar passado | pequeno, e é o de maior risco se ficar de fora |
| 4 | **Declarar `Revocato` × `Scaduto` como estados distintos** | §3 — a vantagem italiana sobre a espanhola vira tela | vocabulário, não código |
| 5 | **Escrever o texto de incerteza dos 82** e prendê-lo em teste | §9 — o número honesto sobrevive a quem quiser arredondá-lo | um teste |
| 6 | **Marcar Radar Agora como faixa de recência, sem data** | §5 — a ausência para de parecer esquecimento, e o sinal que existe é usado sem virar mentira | uma frase e uma ordenação |
| 7 | **Remedir a camada territorial** com a leitura de data consertada | qualquer número de recência italiano; hoje todos estão enviesados para trás | rodar de novo, sem coleta nova |
| 8 | **Tirar os nove números digitados de `build_portal.py`** — ou derivá-los, ou removê-los | §2 — a promessa do rodapé volta a ser verdadeira, e o teste passa a significar algo | médio; e é o único que toca o protótipo congelado, então **é decisão do dono** |

**Já feito nesta rodada, sem esperar o sprint:**

| o quê | o que muda |
|---|---|
| **Leitura de data da camada territorial consertada** (`fonte_territorial.py`) | `datas_no_texto('2026-08-24')` devolvia `2026-08-02`. Alternância *leftmost-first* truncava o dia ao dígito das dezenas: **257 das 365 datas ISO de 2026 voltavam erradas, sempre para trás.** Em `dd/mm/aaaa`, nenhuma — por isso ninguém viu. Três chamadores, zero testes. Agora: 0 erradas em quatro formatos, preso por `tests/test_datas.py` |
| **`COVERAGE.json` passou a declarar a regra que produz o número** | 72 `GOOD` com a expansão territorial, 30 sem. O campo `RULE` agora diz isso e o artefato publica `BY_STATE_SEM_EXPANSAO` |

**Os passos 1–4 são de dado e vocabulário, não de desenho.** Nenhum deles depende de
descongelar o protótipo — e todos são pré-requisito para que qualquer tela seja defensável.

---

**Nada aqui foi coletado nesta rodada.** Todos os números vêm de arquivos já preservados no
repositório, medidos com `python3` sobre eles. Custo: zero.
