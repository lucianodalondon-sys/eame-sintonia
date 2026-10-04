# MISSÃO 03 — CARACTERIZAÇÃO REPRESENTATIVA · RELATÓRIO

```
MISSAO        SOURCE-CURATOR-03-CARACTERIZACAO-REPRESENTATIVA
DATA          2026-09-20
BRANCH        claude/bot-de-fontes-v2-plano
WORKTREE      C:/bot-fontes-v2
INITIAL_HEAD  ac6d6401
REMOTE_HEAD   ac6d6401  (push feito no inicio desta missao, como pedido)
EGRESSO       205.147.30.6 · Milano, IT · AS208172
```

A pergunta desta missão era deixar de responder «a URL abriu» e passar a
responder «eu conheço esta fonte».

---

## 1 · A LEI QUE ORGANIZA TUDO

Três estados distintos, medidos em separado. Uma fonte pode ter o primeiro e
não ter os outros dois, e dizer isso é o trabalho — não um defeito.

```
CONNECTIVITY_PROVEN   124   a fonte responde e devolve conteudo real
SOURCE_CHARACTERIZED  124   sabe-se o que publica, com que ritmo e sobre o que
ONBOARDING_READY       98   pode entrar em coleta recorrente ja
```

As 26 que não estão prontas **não são recusas**. Cada uma diz de quem é o
serviço que falta.

---

## 2 · O QUE FOI MEDIDO

```
TARGET_SOURCES              124

REPRESENTATIVE_SAMPLES       124
TOTAL_SAMPLE_ITEMS           717
AVG_SAMPLE_ITEMS_PER_SOURCE  5.78
MEDIAN_SAMPLE_ITEMS          4.0

SOURCE_PATTERN_STABLE         99
PATTERN_NOT_STABLE             6
SAMPLE_BUDGET_REACHED         48

EXPECTED_YIELD_MEASURED       79
EXPECTED_YIELD_UNKNOWN        45
```

A amostragem é adaptativa: começa em 3, para quando o padrão estabiliza, sobe
até 10 quando não estabiliza. **O tecto é limite, não meta** — a mediana ficou
em 4 itens, ou seja, a maioria das fontes revelou o seu padrão cedo.

### Estado final

```
ONBOARDING_READY          98
NEEDS_MORE_SAMPLING       11
CAPABILITY_BLOCK          14
POLICY_BLOCK               0     ← medido, não «não se aplica»
SEMANTIC_REVIEW_REQUIRED   1
UNKNOWN                    0
```

### Por família

```
YOUTUBE     59 READY · 1 SEMANTIC_REVIEW
HTML_SITE   39 READY · 11 NEEDS_MORE_SAMPLING
FACEBOOK              14 CAPABILITY_BLOCK
```

---

## 3 · ACTIVIDADE — E A CADÊNCIA QUE DELA DECORRE

```
ACTIVE_HIGH_FREQUENCY   12   →  DAILY
ACTIVE_MEDIUM_FREQUENCY 27   →  WEEKLY
ACTIVE_LOW_FREQUENCY    23   →  MONTHLY
DORMANT                 22   →  QUARTERLY_WATCH
UNKNOWN                 40   →  MONTHLY_PROBE
```

**22 fontes estão paradas há mais de um ano.** Nenhuma foi recusada por isso:

> `LOW_YIELD != LOW_VALUE` · `DORMANT != IRRELEVANT`

Uma fonte parada continua dona do que publicou. O que muda é a **cadência**,
não a relevância — e `QUARTERLY_WATCH` significa «vigiar se acorda», não
«coletar regularmente».

As 40 `UNKNOWN` recebem `MONTHLY_PROBE`: uma sonda **para medir**, não para
colher. Ainda não se sabe o ritmo delas, e fingir que se sabe seria pior.

A cadência não usa valor nenhum — a Intelligence ainda não existe, e nenhum
ramo desta decisão pode depender dela.

---

## 4 · RENDIMENTO E HISTÓRICO

```
EXPECTED_YIELD medido em          79 fontes
mediana                           0.16 itens/semana  (≈ 1 item cada 6 semanas)
máximo                            4.7 itens/semana
HISTORICAL_DEPTH observado em     93 fontes
```

A mediana baixa é um facto sobre o universo, não um defeito: são boletins
técnicos e institucionais, não redações diárias. Algumas têm **mais de 10 anos**
de arquivo acessível.

---

## 5 · COBERTURA TEMÁTICA

```
SCIENCE                  34
AGRICULTURAL_NEWS        24
MARKET                   24
CLIMATE                  13
REGULATORY               13
PORTFOLIO                12
TECHNICAL_FIELD_SIGNAL    7
PHYTOSANITARY             6
COMPETITOR_COMMUNICATION  3
UNKNOWN                  55
```

```
RELEVANCE_YES      71
RELEVANCE_UNKNOWN  53
RELEVANCE_NO        0
```

**Zero `RELEVANCE_NO`** é resultado, não omissão. Declarar uma fonte irrelevante
exige prova de que não serve; não ter conseguido extrair sinal temático é falta
de medida, e isso chama-se `UNKNOWN`.

---

## 6 · OS QUATRO DEFEITOS QUE ESTA CORRIDA ENCONTROU

Todos vieram de olhar para a saída real. Cada um tem teste que falha se voltar.

### 6.1 · A ficha dizia «Valagro», o canal é da Syngenta

`CAND-0183` está registada como *Valagro — Youtube ufficiale* e aponta para
`youtube.com/@syngenta`. Os vídeos são todos da Syngenta. A Valagro foi
absorvida, e o canal é do comprador.

A captura funciona. O conteúdo é real. **A ficha é que está errada sobre quem a
fonte é** — e uma captura com HTTP 200 nunca acusaria isto, porque não há nada
avariado.

> **REBRANDING E AQUISIÇÃO NÃO PARTEM O ENDEREÇO: PARTEM A IDENTIDADE.**

Promover assim poria no Atlas uma ficha com o nome do vendido e o conteúdo do
comprador, e o erro atravessaria calado. É a **única** das 124 que sobe a
humano, e sobe por mérito próprio: ambiguidade semântica genuína, que nenhuma
amostragem adicional resolve.

### 6.2 · 981 KB de Facebook davam 58 caracteres legíveis

O conteúdo é montado por JavaScript; 189 blocos `<script>` não dizem nada a
quem lê o HTML. Mas a página declara-se nas metatags públicas:

```
og:description = «Provincia autonoma di Trento - Pagina Ufficiale,
                  Trento. Follower: 105.998 …»
```

Passou de 58 → 762 caracteres. Sem isto, 14 fontes reais ficariam «sem sinal
temático» por defeito do leitor — a repetição exacta do erro que já custou caro
nesta casa. **Não contorna muro nenhum**: são metatags servidas a qualquer
cliente anónimo.

### 6.3 · 19 fontes com UM item passavam a READY

A regra de «universo inteiro» aceitava `n=1`. Mas um item não é um padrão — é
precisamente a premissa desta missão:

> **UM REAL_EXAMPLE PROVA QUE A FONTE FUNCIONA.
> NÃO PROVA O QUE ELA NORMALMENTE PUBLICA.**

Aceitar `n=1` como «conhecida» seria refazer, uma camada acima, o erro que esta
missão existe para corrigir. Passaram a exigir ≥2.

### 6.4 · As 14 do Facebook escapavam ao bloqueio de capacidade

A sonda anónima devolveu bytes, logo `BROWSER_REQUIRED = NAO SEI`. Mas a rota de
**coleta recorrente** exige navegador. Lidas só pelo primeiro campo, 14 fontes
sem rota construída ficavam `ONBOARDING_READY`.

> **CAPTURAR UMA AMOSTRA != TER ROTA DE COLETA.**

Causa raiz: a rota era copiada da missão 02 **depois** de decidir. Caíam em
`NEEDS_MORE_SAMPLING` — o rótulo certo pelo motivo errado, que é pior do que um
rótulo errado, porque parece bem.

### 6.5 · Um zero que não aparecia

`POLICY_BLOCK` não constava da tabela porque `Counter` omite chaves nunca
ocorridas. Uma categoria ausente lê-se como «não se aplica» em vez de
«mediu-se e deu zero». Agora publica-se o zero.

---

## 7 · RECONCILIAR O «97» E O NOVO BATCH

```
PROMOTE_TOTAL        124
OLD_NEXT_BATCH        97   = 60 YOUTUBE_FEED + 37 HTML_PUBLIC
OLD_BATCH_EXCLUDED    27   = 14 FACEBOOK + 13 HTML com ramo de índice
```

Depois de caracterizar:

```
NEW_NEXT_BATCH_SIZE   87
```

**WHY_THE_NUMBER_CHANGED** — o batch antigo contava conectividade; o novo conta
conhecimento. Três movimentos:

```
−1   CAND-0183 · identidade por resolver (Valagro/Syngenta)
−11  HTML com n=1 ou padrão instável · precisam de mais amostra
+2   HTML que o batch antigo excluía e que a amostragem provou estáveis
```

Dos 98 READY, 11 ficam fora do batch por exigirem **ramo de índice** — pequena
adaptação de rota, não bloqueio.

---

## 8 · OS 2 ENDPOINTS (COL-LAW-205)

```
IT-T1-008 · IT-T1-012
```

Continuam fora de tudo isto. Não são fontes novas: são endereços adicionais de
fontes já no Atlas. **Nenhuma SOURCE nova foi criada** para eles.

---

## 9 · O QUE NÃO FOI TOCADO

```
FONTES-CANDIDATAS.json    não aberto para escrita · 0 transições
italy_contracts.mjs       intocado
italy_pilot_collect.mjs   intocado
System Map                não regenerado
Big Collection            intocada
LinkedIn 44 / Instagram 25  zero pedidos de rede
MERGE                     não feito
```

---

## 10 · TESTES

```
test_capturador.py       22  exit=0
test_correr_lote.py       6  exit=0
test_caracterizador.py   29  exit=0
─────────────────────────────────
TOTAL                    57  NEW_FAILURES = 0
```

Os 35 anteriores foram preservados. Os 22 novos cobrem exactamente as regras que
esta missão acrescentou, com ênfase nas que impedem um juízo errado:

```
fonte homogénea estabiliza cedo          fonte heterogénea pede mais amostra
um item não tem padrão                   fonte pequena usa universo inteiro
low yield não vira reject                dormant não vira irrelevante
«não li» != «não serve»                  listagem != item
plataforma != identidade de fonte        published do canal != do vídeo
identidade errada sobe a humano          exige navegador = CAPABILITY_BLOCK
```

### Red team — 14 PASS, 0 FAIL

```
PASS  soma dos estados = 124 exactamente
PASS  nenhum READY com amostra < 2
PASS  nenhum READY exigindo navegador
PASS  22 DORMANT e nenhuma marcada irrelevante
PASS  todas as 717 amostras existem no disco
PASS  0 RELEVANCE=NO · 0 REJECT
PASS  nenhuma cadência usa valor
PASS  LinkedIn/Instagram ausentes do dataset
```

---

## 11 · ARTEFATO

`curadoria/SOURCE-CHARACTERIZATION-V1.json`

Referencia `CANDIDATE_ID` e, quando aplicável, `MATCHED_SOURCE_ID`.
**Não é Source Registry.** Não substitui o Atlas nem a fila — é a caracterização
que os alimenta quando a promoção for autorizada.

---

## 12 · EM LINGUAGEM SIMPLES

**1. Quantas fontes conhecemos mesmo agora.** **124.** De cada uma sabemos o que
publica, com que frequência, sobre que temas, que regiões cobre e há quanto
tempo existe. Foram lidos **717 documentos reais** — uma média de quase 6 por
fonte.

**2. Quantas apenas abriram.** Nenhuma ficou só nisso. Antes desta missão, as
124 tinham *um* documento cada — provava que funcionavam, não o que costumam
publicar.

**3. Quantas têm padrão suficientemente conhecido.** **99** mostraram um padrão
estável. Quase sempre bastaram 3 ou 4 documentos: quando uma fonte é coerente,
revela-se depressa.

**4. Quanto tendem a produzir.** Em 79 deu para medir. A mediana é **um item
cada seis semanas** — são boletins técnicos, não jornais. Algumas têm mais de
dez anos de arquivo.

**5. Quantas estão dormentes.** **22**, paradas há mais de um ano. Nenhuma foi
descartada: continuam a valer pelo que publicaram. Só passam a ser visitadas de
três em três meses em vez de todos os dias.

**6. Quantas precisam mesmo de gente.** **Uma.** A ficha diz «Valagro», o canal
é da Syngenta — a empresa foi comprada. Tudo funciona; o que está errado é o
nome. Nenhum robô decide como rebaptizar uma fonte.

**7. Quantas estão prontas para onboarding.** **98 prontas**, das quais **87
entram já** no próximo lote. As outras 11 precisam de um pequeno ajuste de rota.
E **14 do Facebook** esperam por uma capacidade que não temos — isso é serviço
do engenheiro de coleta, não juízo sobre a fonte.

---

**A lição desta corrida.** Quase promovi 19 fontes por terem *um* documento, e
14 por terem respondido a uma sonda que a coleta real não consegue repetir. Em
ambos os casos o número ficava melhor e a verdade ficava pior.

> **Responder não é publicar. Uma amostra não é uma rota. Um exemplo não é um padrão.**
