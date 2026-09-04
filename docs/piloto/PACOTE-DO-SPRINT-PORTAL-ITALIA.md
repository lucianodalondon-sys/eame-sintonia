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

## 5 · RADAR AGORA — `VAZIO` para a Itália, e é melhor dizer isso

`Radar Agora` responde *"o que está acontecendo agora"*. Para a Espanha existe base: o RAIF
dá incidência medida, semanal, com 23 safras. **Para a Itália não há equivalente medido no
acervo.** O que a Itália tem é:

- registro regulatório — que é **estado**, não evento de campo, e de um snapshot de 24/08;
- 150 documentos sociais do piloto — dos quais **82 não são julgáveis** e nenhum tem legenda.

**Não há, hoje, dado italiano de campo com frescor para sustentar um "agora".** Colocar
qualquer coisa sob esse rótulo seria fabricar atualidade. O correto é a área existir **vazia e
declarada**: *"a Itália ainda não tem camada de campo medida — ver P-010 e P-011"*.

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

**A geografia italiana defensável é outra:** a matriz de cobertura dos sensores humanos —
117 células CROP×REGION×SPECIALTY, 72 `GOOD` · 29 `WEAK` · 16 `NONE`, em 16+ regiões, com as
lacunas nomeadas (a maior: `CEREAL × EMILIA-ROMAGNA × APHIDS`, zero sensores, com âncora ADAMA
`PIRIMICARB | FLONICAMID | LAMBDA-CYHALOTHRIN`).

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
| com legenda | **0** | idem |

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
| 6 | **Marcar Radar Agora como vazio e declarado** | §5 — a ausência para de parecer esquecimento | uma frase |

**Os passos 1–4 são de dado e vocabulário, não de desenho.** Nenhum deles depende de
descongelar o protótipo — e todos são pré-requisito para que qualquer tela seja defensável.

---

**Nada aqui foi coletado nesta rodada.** Todos os números vêm de arquivos já preservados no
repositório, medidos com `python3` sobre eles. Custo: zero.
