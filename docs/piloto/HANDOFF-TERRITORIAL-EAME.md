# HANDOFF TERRITORIAL — EARLY SIGNAL EAME

**Missão 16 · rota territorial** · última rodada autorizada, executada em `2026-08-31`.
`DATASET_OWNER = EARLY_SIGNAL_EAME` · `MISSION_ID = 16-ROTA-TERRITORIAL`

> **Este handoff é consumido pelo `SOURCE_COMMIT` congelado**, nunca pelo HEAD de uma
> branch mutável. O commit está no fim deste documento.

```
TERRITORIAL_CAPABILITY   = PARTIAL
MANDATORY_HANDOFF_READY  = YES
MISSION_STATE            = FROZEN
MORE_COLLECTION_NEEDED   = NO
NEW_APIFY_RUNS           = 0
APIFY_COST_USD           = 0
OPERATIONAL_STOP_RULE    = NO_MORE_COLLECTION_AFTER_THIS_ROUND
```

---

## 1 · A PERGUNTA

> É possível observar, em fontes públicas territoriais, sinais suficientemente locais,
> datados e específicos de problema para alimentar um CASE em
> `COUNTRY × REGION × CROP × ISSUE × TIME`?

**Resposta: sim, o mecanismo funciona — e fecha em 1 dos 6 recortes.** O que trava não é
o acesso nem o território: é o **problema fitossanitário nomeado no corpo**.

---

## 2 · O QUE FUNCIONA

| Âncora | Cobertura | Base |
|---|---|---|
| `COUNTRY` | **22 / 22** | herdada do mandato declarado da fonte |
| `CROP` | **21 / 22** | nomeada no corpo, com trecho de evidência |
| `LOCALITY / REGION` | **15 / 22** | nomeada no corpo; nunca inferida do idioma |
| `TIME` | **12 / 22** | data no próprio documento |
| **`ISSUE`** | **5 / 22** | **o bloqueador** |
| **`FULL_TERRITORIAL_CASE_KEY`** | **1 / 22** | as cinco âncoras juntas |

**As 5 rotas vivas foram todas alcançadas e todas produziram corpo:**
`ES-RAIF` · `ES-OLIMERCA` · `IT-LAMMA` · `FR-VIGNEVIN` · `FR-ARVALIS`.
`SOURCE_ROUTE_PROVED = YES` em 5 de 5 — mas **rota provada não é sensor provado**, e a
distinção está registrada por fonte em `TERRITORIAL/FINAL.json → ACAO_2_FONTES`.

---

## 3 · ONDE FUNCIONA — o caso completo

**`IT · DURUM_WHEAT × FUSARIUM` — `CASE_SIGNAL_READY`**

```
FONTE      Consorzio LaMMA — Bollettino (Regione Toscana)
URL        https://www.lamma.toscana.it/previ/ita/agrometeo/html/Grosseto_ftsnt.html
COUNTRY    IT          REGION   Toscana — Provincia di Grosseto
CROP       CEREAL      ISSUE    SEPTORIA + FUSARIUM
TIME       2026-04-23  TIPO     FIELD_OBSERVATION
```

> *«Septoria — la septoria rimane la patologia principale. Nel nord si osservano livelli
> medi nel tenero e livelli elevati nel duro.»*
> *«Fusariosi — si segnala la comparsa di sintomi lievi nel frumento duro in alcune
> situazioni.»*

Sintoma **observado**, cultura distinguindo duro de tenero, província nomeada, data no
documento. É o que um CASE precisa, e veio de uma única fonte institucional.

---

## 4 · ONDE FALHA, E POR QUÊ

| Recorte | Estado | Por quê |
|---|---|---|
| `ES · OLIVE × REPILO` | `PARTIAL` | RAIF entrega país, região e cultura; **nas páginas medidas** o corpo não nomeia repilo |
| `ES · WHEAT × SEPTORIA` | `PARTIAL` | idem — nas mesmas páginas, a série está no XML de dados e não no texto publicado |
| `IT · VINE × FLAVESCENCE` | `PARTIAL` | o único item que a nomeava era um **quiz didático**, reprovado pelo guard |
| `IT · DURUM_WHEAT × FUSARIUM` | **`CASE_SIGNAL_READY`** | ver §3 |
| `FR · VINE × DOWNY_MILDEW` | `PARTIAL` | 11 corpos lidos; **nos corpos medidos** o *mildiou* aparece em catálogo de variedades, nota do cobre e história do século XIX — `CASE_READY_FIELD_BULLETIN = NOT_PROVED` **neste corpus** |
| `FR · WHEAT × SEPTORIA` | `PARTIAL` | **nos 2 corpos medidos** a ARVALIS entrega corpo e região, sem alvo nomeado |

Nenhum recorte é `NOT_PROVED`. Onde não fechou, o estado correto é
**`SIGNAL_NOT_PROVED_IN_MEASURED_CORPUS`** — não *"não existe sinal"*.

**Nenhum recorte foi substituído.** `ES · OLIVE × REPILO` continuou repilo e terminou
`PARTIAL`, em vez de virar Xylella.

---

## 5 · OS QUATRO GUARDS, E O DEFEITO REAL QUE CRIOU CADA UM

| Guard | Disparos | Defeito medido que o originou |
|---|---:|---|
| `BINARY_NOT_DOCUMENT` | 1 | o RAIF devolveu um **ZIP de XML com 27,6 milhões de caracteres** e o extrator casou `FUSARIUM` dentro de bytes comprimidos |
| `SIDEBAR_NOT_BODY` | 4 | no `vignevin.com` o `ISSUE` vinha da lista de **artigos relacionados**, não do artigo |
| `ORG_NAME_NOT_LOCALITY` | 1 | *"Vignerons Bio Nouvelle-Aquitaine"* é o nome de quem publica, não o lugar do fato |
| `EDUCATIONAL_QUIZ_NOT_FIELD_SIGNAL` | — | **`PASS`** — nenhuma chave completa desta rodada é conteúdo didático |

`DUPLICATES_INTERCEPTED = 2`. O mesmo documento nunca conta duas vezes.

---

## 6 · O QUE A RODADA ANTERIOR MEDIU ERRADO

A medição de `ISSUE = 15%` e chave completa `= 8%` foi feita sobre texto **que não era o
documento**:

- **7 de 13** itens eram a **página de índice** da publicação. O boletim da Junta de
  Extremadura tem 9 páginas em PDF e o que foi lido foram 1.106 caracteres de menu.
  O `CROP = 100%` daquela rodada veio da **navegação** — *"Frutales Vid Olivar Hortícolas"*.
- **6 de 13** tinham corpo real de 20.000 a 33.000 caracteres, dos quais **1.500 foram
  preservados**. O alvo podia estar nos 94% descartados.

Reprocessados sem rede, os 13 dão `ISSUE_IN_BODY = NOT_KNOWN` em **13 de 13** — não porque
a fonte cale, mas porque o corpo nunca foi capturado. Detalhe item a item em
`TERRITORIAL/FINAL.json → ACAO_1_REPROCESSAMENTO_DOS_13`.

E a **única chave completa** daquela rodada era o artigo
*"Flavescenza, sicuri di riconoscere i sintomi? Mettetevi alla prova"* — um quiz com onze
fotos. Fica registrado como **regressão negativa permanente**.

```
OLD_ISSUE_COVERAGE            = 15% de 13 corpos  (texto que não era o documento)
NEW_ISSUE_COVERAGE            = 23% de 22 corpos  (5 / 22, corpo real)
OLD_EFFECTIVE_FULL_CASE_KEY   = 0
NEW_EFFECTIVE_FULL_CASE_KEY   = 1 / 22
```

---

## 7 · REGRAS QUE O CONSUMIDOR TEM DE HERDAR

- **`LISTING_ROLE = DISCOVERY_INDEX_ONLY`.** A passagem de listagem acha URL e prova que a
  fonte tem atividade. Ela **não entra em nenhum denominador** de cobertura. Os 62 itens de
  listagem não são itens medidos.
- **`FULL_TERRITORIAL_CASE_KEY` exige `LOCALITY`.** `COUNTRY × CROP × ISSUE × TIME` é chave
  intermediária (**4 / 22**) e não pode ser chamada de completa.
- **`ISSUE` nunca vem do recorte da missão.** Um documento achado na busca de
  `ES · OLIVE × REPILO` não recebe `ISSUE = REPILO` por isso. O corpo sustenta ou o campo
  fica `NOT_KNOWN`.
- **Rota alcançável ≠ sinal territorial.** As duas coisas vivem em campos separados.
- **`NOT_FOUND_IN_MEASURED_CORPUS` nunca vira `DOES_NOT_EXIST`.** Toda ausência é afirmada
  com o escopo do que foi lido: quantos corpos, de quais fontes, em que rodada. Uma fonte
  não lida não é uma fonte silenciosa.

---

## 8 · O QUE O TERRITORIAL PODE E NÃO PODE ALIMENTAR

| PODE CONTRIBUIR | NÃO PODE PROVAR |
|---|---|
| `LOCALITY` — 15/22, com base declarada | `ADAMA_PRODUCT_FIT` |
| `CROP` — 21/22 | `COMPETITOR_CAUSALITY` |
| `COUNTRY` — 22/22 | `MARKET_OPPORTUNITY` |
| `TIME` — 12/22 | `ACTION_DECISION` |
| `ISSUE` — 5/22, e é a limitação | `INCIDENCE` — o boletim relata ocorrência, nunca denominador |
| observação de campo com citação verificável | `TREND` · `OUTBREAK` — uma captura não é série |

---

## 9 · LIMITAÇÕES EXATAS

1. **`ISSUE` em 5 / 22.** Serviços que publicam dados abertos (RAIF) põem o alvo no **XML**,
   não no texto da página. A rota de texto não alcança o alvo dessas fontes.
2. **`TIME` em 12 / 22.** Páginas institucionais frequentemente não datam o corpo.
3. **França — escopo estrito da afirmação.** Nos **11 corpos medidos** de `FR-VIGNEVIN` e
   `FR-ARVALIS` nesta rodada, `CASE_READY_FIELD_BULLETIN = NOT_PROVED`: o que foi lido é
   catálogo de variedades, nota técnica e conteúdo histórico. **Isto não afirma o que essas
   instituições publicam em geral**, nem que a França não tenha boletim de campo — afirma
   apenas o que estes 11 corpos contêm. O `BSV`, que é a rota nacional de boletim de campo,
   **não foi lido nesta rodada** e segue sem itens datados nas rotas antes testadas:
   `SIGNAL_NOT_PROVED_IN_MEASURED_CORPUS`, nunca `NO_SIGNAL_EXISTS`.
4. **Uma única fonte fechou caso.** LaMMA é 1 de 5. A capacidade está demonstrada por
   **uma** instância, não por recorrência.
5. **`ES-RAIF` trouxe páginas de 2017 e 2018** junto das de 2026 — o portal de dados
   abertos mistura vintages, e a data do documento nem sempre é a do fato.

---

## 10 · POR QUE `PARTIAL` E NÃO `PROVED_WITH_LIMITATIONS`

O mecanismo está provado ponta a ponta: **existe** um documento público, territorial,
datado, com cultura e alvo nomeados e sintoma observado, e ele foi recuperado por rota
gratuita e reproduzível.

Mas **1 de 6 recortes** e **1 de 22 corpos** não é *"parte relevante dos recortes"*, e
`ISSUE` a 23% é exatamente a não-conclusão que a definição de `PARTIAL` nomeia. O sensor
prova `LOCALITY`, `CROP` e `COUNTRY`; não fecha `ISSUE` nem `FULL_CASE_KEY`.

**Nenhuma coleta adicional foi feita para melhorar este número**, e nenhuma deve ser.

---

## 11 · ARTEFATOS CONGELADOS

| Arquivo | Conteúdo |
|---|---|
| `data/samples/TERRITORIAL/CORPO-R2.json` | 25 corpos lidos das 5 fontes vivas, texto e evidência |
| `data/samples/TERRITORIAL/FINAL.json` | ação 1, guards, medição final, estado por recorte |
| `scripts/territorial_corpo.py` | leitura de corpo — HTTP direto, zero Apify |
| `scripts/territorial_redteam.py` | os quatro guards e a medição |
| `data/samples/TERRITORIAL/MEDICAO.json` | medição da rodada anterior, **preservada, não reescrita** |

Os artefatos da rodada anterior **não foram apagados**. A comparação entre eles é a prova
de que o defeito era de captura, não da fonte.

---

## 12 · COMMIT CONGELADO

```
SOURCE_COMMIT   11fd7b54e27adaaebed18f049f90b80b05806943
BRANCH          claude/sintonia-essencia-convergencia-kn83zy
MERGED          NO
```

**O FUNCIONAL e o refresh futuro consomem este commit**, não o HEAD da branch. Os cinco
artefatos do §11 estão todos dentro dele. Qualquer commit posterior nesta branch é
trabalho de outra missão e não faz parte deste handoff.


---

## 13 · SELO SEMÂNTICO FINAL — duas verificações documentais

Executadas em `2026-08-31` sobre material **já preservado**. Nenhuma rede, nenhuma coleta,
nenhum extrator reaberto.

### 13.1 · A testemunha do caso italiano — `FUSARIUM_ISSUE_EVIDENCE_PROVED = YES`

A pergunta era legítima: *«Si segnala la comparsa di sintomi lievi nel frumento duro»*
prova cultura, sintoma, tempo e lugar — **não prova, sozinha, que o alvo é Fusarium**.

O corpo preservado responde. `Fusariosi` é o **cabeçalho da seção**, e o texto é contíguo:

> «… Il quadro evidenzia una diffusione generalizzata con intensità variabile.
> **Fusariosi** Si segnala la comparsa di sintomi lievi nel frumento duro in alcune
> situazioni, mentre il tenero resta esente. **Rischio fusariosi da modello.** Il rischio
> risulta elevato nelle classi precoci e medie del frumento tenero nel sud …»

Três coisas se sustentam nessa passagem única:

1. **`Fusariosi` é o alvo declarado da seção**, imediatamente antes da observação — não vem
   do nome do recorte, nem da busca, nem de barra lateral, nem de menu, nem de metadado.
2. **O próprio documento separa observação de modelo.** *«Si segnala la comparsa di
   sintomi»* é sintoma visto; *«Rischio fusariosi da modello»* é saída de modelo, e vem
   depois, nomeada como tal. A observação que sustenta o caso é a primeira.
3. **A cultura é distinguida dentro da própria frase** — *duro* com sintoma, *tenero*
   isento. Não é uma menção genérica a cereal.

```
IT_DURUM_WHEAT_FUSARIUM        = CASE_SIGNAL_READY   (mantido)
FUSARIUM_ISSUE_EVIDENCE_PROVED = YES
ISSUE_EVIDENCE                 = lamma.toscana.it/previ/ita/agrometeo/html/Grosseto_ftsnt.html
                                 seção "Fusariosi", posição 1.125 do corpo preservado,
                                 contígua à observação, no mesmo documento e contexto
```

### 13.2 · Escopo das afirmações sobre a França — `FRENCH_CORPUS_CLAIM_SCOPED = YES`

Três frases foram reescritas por dizerem mais do que a medição sustenta:

| Antes | Depois |
|---|---|
| «o *mildiou* … **nunca** como observação corrente» | «**nos corpos medidos** … `CASE_READY_FIELD_BULLETIN = NOT_PROVED` **neste corpus**» |
| «**IFV e ARVALIS publicam** catálogo, nota técnica e história — não boletim de campo» | «nos **11 corpos medidos** … **isto não afirma o que essas instituições publicam em geral**» |
| «o corpo das páginas de dataset **nunca nomeia** repilo» | «**nas páginas medidas** o corpo não nomeia repilo» |

O que **permanece medido e verdadeiro**, sem alteração:

```
VIGNEVIN_ROUTE_REACHABLE = YES     (9 corpos lidos)
ARVALIS_ROUTE_REACHABLE  = YES     (2 corpos lidos)
SOURCE_ROUTE_REACHABLE  ≠  CASE_READY_TERRITORIAL_SIGNAL
```

O `BSV` — a rota francesa que de fato publica boletim de campo — **não foi lida nesta
rodada**. Não estava entre as cinco autorizadas. Sua ausência do corpus é escolha de escopo,
não evidência sobre a França.

### 13.3 · O que estas verificações não mudaram

```
TERRITORIAL_CAPABILITY  = PARTIAL        (inalterado)
MANDATORY_HANDOFF_READY = YES            (inalterado)
UNIQUE_BODY_ANALYZED_ITEMS = 22          WITH_ISSUE = 5/22
SLICES_CASE_SIGNAL_READY = 1             SLICES_PARTIAL = 5   SLICES_NOT_PROVED = 0
WITH_FULL_TERRITORIAL_CASE_KEY = 1/22
MISSION_STATE = PARKED                   MORE_COLLECTION_NEEDED = NO
```

Nenhuma coleta foi feita para defender o caso, e nenhuma seria permitida se ele tivesse
caído.
