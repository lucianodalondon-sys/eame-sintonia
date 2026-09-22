# RELATÓRIO — CENSO DO CONTRATO DE RECOLLECTION V1

Base: `paridade-v1` @ `207fba7c` · missão `MISSAO-RECOLLECTION.md`
Big Collection **não executada**. Nenhuma coleta nova foi feita nesta missão.

```
ACTUAL_LLM_MODEL = claude-opus-5
NETWORK_REQUESTS = 0
NETWORK_REASON   = nao foi preciso. O acervo local tinha 445 observacoes e 120
                   enderecos com os bytes preservados das DUAS visitas; a
                   pergunta desta missao responde-se toda em disco.
```

---

## FASE 0–2 · A MEDIÇÃO DO DONO, CONFERIDA

Confirmada, número a número, lendo o próprio código e não o relatório anterior:

```
CONTRACTS_TOTAL         186
WITH_RECOLLECTION         7   IT-T3-002 IT-T3-010 IT-T3-008 IT-T3-005
                              IT-T4-001 IT-T2-004 IT-T2-002
  por valor                   IMMUTABLE 4 · MUTABLE 3 · TTL_SECONDS null nos 7
WITHOUT_RECOLLECTION    179
MUTABILIDADE            ["IMMUTABLE","MUTABLE","UNKNOWN"]   incrementalidade.mjs:104
```

Uma correção de facto, sobre um comentário e não sobre a medição do dono:
`regras/incrementalidade.mjs` dizia, na linha 102, *«Nenhum dos 186 contratos o
tem hoje»*, e `IT-T3-005` dizia *«Medido em 2026-09-22: 0 dos 186 contratos o
tinham»*. Eram sete. Os comentários estavam velhos; os números do dono estavam
certos. Ficaram corrigidos.

### O ACHADO — confirmado, e pior do que estava escrito

```
SILENT_NEVER_DEFAULT = YES
```

Corrida com os quatro casos possíveis, num processo novo:

| contrato | valor lido | `DECLARADO` | decisão |
|---|---|---|---|
| sem bloco `RECOLLECTION` | `UNKNOWN` | `false` | `SKIP_KNOWN` |
| com `UNKNOWN` escrito à mão | `UNKNOWN` | `true` | `SKIP_KNOWN` |
| com `IMMUTABLE` | `IMMUTABLE` | `true` | `SKIP_KNOWN` |
| com `MUTABLE` | `MUTABLE` | `true` | `REVALIDATE` |

A leitura da linha 115 estava **certa** — devolve `UNKNOWN`, que é honesto. O
defeito era a jusante, e é mais fundo do que o diagnóstico:

> `UNKNOWN` e `IMMUTABLE` davam **exactamente a mesma resposta**, para sempre,
> e sem deixar rasto. O campo `DECLARADO` — aquele que distinguia *«o dono
> sabe»* de *«ninguém sabe»* — **já era calculado na linha 128, e ninguém o
> lia.** A decisão deitava-o fora.

Sem TTL e sem validador guardado (o livro tem **zero** ETag e zero
Last-Modified em 445 observações), não havia segunda porta: o salto repetia-se
em todas as corridas, para sempre.

---

## FASE 3–4 · TOPOLOGIA POR EVIDÊNCIA

Ordem da evidência respeitada, e ela **mudou a resposta**. As medições vivem em
`medidas/recollection_censo.mjs`, `medidas/recollection_familias.mjs`,
`medidas/recollection_diff.mjs` e `medidas/recollection_topologia.mjs`.

### ⚠️ O PRIMEIRO ACHADO: 44 «mudanças» que não eram mudança nenhuma

Comparando as duas visitas guardadas de cada endereço, com o normalizador
como estava:

```
PARES_HTML_OLHADOS       83
VOLATILE_ONLY            39
MATERIAL_CHANGE          44      ← em tres fontes
```

Olhou-se para as 44, linha a linha. Nenhuma era texto editorial:

| família | linhas | fonte | o que era |
|---|---|---|---|
| `WPDM_CLIENT_ID` | 60 | IT-T7-017 | nonce do WordPress Download Manager |
| `WORDFENCE_HID` | 60 | IT-T7-017 | farol do Wordfence, `hid` sorteado |
| `DRUPAL_FORM_BUILD_ID` | 24 | IT-T5-049 | identificador de formulário por pedido |
| `ENTIDADES_DE_EMAIL` | 20 | IT-T7-042 | o mesmo e-mail, letras escapadas ao acaso |
| `DRUPAL_VIEW_DOM_ID` | 16 | IT-T5-049 | identificador de render da Views |
| `DRUPAL_THEME_TOKEN` | 8 | IT-T5-049 | token anti-falsificação do tema |

**`SEM_FAMILIA = 0`** — nenhuma linha ficou por explicar. É isso, e só isso,
que autorizou escrever regras novas.

As três primeiras famílias **já estavam nomeadas** no cabeçalho de
`regras/incrementalidade.mjs`, medidas pela CANONICAL-MICRO-V1 («52 nonce do
WordPress Download Manager», «52 farol de analytics com `hid` aleatório», «6
token do Drupal») — nomeadas lá, e **nunca implementadas** na lista que age
sobre elas.

> Uma família medida que não chega à lista que age sobre ela não está
> resolvida: está escrita.

O caso do e-mail é de outra natureza e por isso **não** entrou na lista de
trechos voláteis. `info@consorziobalsamico.it` é publicado com um subconjunto
sorteado de letras em entidades HTML a cada visita — a mesma frase, noutra
grafia. Apagar não servia; traduzir sim. Ficou um passo próprio,
`canonicalizarEntidades()`, que **não perde informação** e deixa de fora os
cinco caracteres com significado em HTML (`& < > " '`), para não descodificar
duas vezes o que foi escapado uma.

Depois destas quatro regras: **83 de 83 pares `VOLATILE_ONLY`,
`MATERIAL_CHANGE = 0`, `NORMALIZADOR_SUSPEITO = 0`.**

### ⚠️ O SEGUNDO ACHADO: a prova mais visível era a mais fraca

```
INTERVALO ENTRE AS DUAS VISITAS COMPARADAS:  518s .. 524s   (8,7 minutos)
                                             em TODOS os 83 pares
```

«83 de 83 não mudaram» prova que o normalizador funciona. Sobre o que a fonte
faz numa semana **não prova nada**. Classificar por aqui daria `IMMUTABLE` a
três fontes — e teria sido o erro M2 do red team, cometido com ar de medição.

A evidência a sério estava dentro dos próprios bytes: `article:published_time`
e `article:modified_time`, próprios de cada artigo.

| fonte | docs com datas | editados >24h depois de publicados | maior atraso |
|---|---|---|---|
| IT-T7-017 riuniteciv | 26 | **19** | **72,0 dias** |
| IT-T7-042 consorziobalsamico | 7 | **3** | **27,1 dias** |
| IT-T10-022 zootecnica | 4 | **3** | **7,2 dias** |
| IT-T10-018 myfruit | 30 | — | as 30 datas são a hora da NOSSA visita |

Cada artigo traz **uma** data de publicação e **uma** de modificação, próprias,
posteriores à publicação e anteriores à nossa visita. Três fontes reescrevem
artigos já publicados. A quarta não diz nada: ali o campo «modificado em»
carrega a hora a que nós batemos à porta — a nossa pegada, não a fonte.

### ⚠️ O TERCEIRO ACHADO: «ADITIVO» não responde à pergunta que se faz

`UPDATE_BEHAVIOR: "ADITIVO"` diz como aparecem itens **novos**. Não diz se os
**velhos** são reescritos. São duas perguntas, e o campo só responde à
primeira.

A distinção que resolve está no que se descarrega:

- um **ficheiro** publicado (PDF, CSV, ODS) *é* a edição — o nome carrega a
  data ou o número, a edição seguinte ganha ficheiro próprio, e aquele
  ficheiro naquela morada não volta a ser tocado;
- uma **página** (HTML, extracto de navegador, metadados de vídeo) é uma
  vitrina: o item novo ganha morada própria **e** a morada antiga continua a
  ser servida por um sistema que a pode reescrever a qualquer momento.

Aplicar «ADITIVO → IMMUTABLE» sem esta distinção declarava cego o **catálogo
de produtos da ADAMA** (`IT-T9-008`), onde uma alteração de rótulo é
precisamente o facto regulatório que se quer ver. Ficou fora, e com ela
`IT-T5-002` e `IT-T8-001`.

---

## FASE 5–6 · O CENSO

Critérios escritos **antes** de preencher, no cabeçalho de
`medidas/recollection_topologia.mjs`:

```
HIGH    evidencia CONTRATO_MEDIDO ou DATAS_NO_DOCUMENTO, >= 5 documentos,
        veredicto coerente
MEDIUM  DATAS_NO_DOCUMENTO com 2 a 4 documentos, ou CONTRATO_MEDIDO com uma
        so edicao, ou data no caminho do endereco
LOW     so REVISITA_PRESERVADA ou FORMA_DO_ENDERECO
nenhuma nao se declara nada -> UNKNOWN, e BLOCKED_FOR_BIG_COLLECTION
```

Só se declara com `HIGH` ou `MEDIUM`. **`LOW` não declara** — uma declaração
fraca vale menos que nenhuma, porque compra a admissão à Big Collection ao
preço de um palpite.

### `DISCOVERY_RECOLLECTION` e `DETAIL_RECOLLECTION`

**O contrato real não os suporta em separado, e isso fica dito em vez de
fingido.** O bloco `RECOLLECTION` tem um só campo de mutabilidade,
`DETAIL_CONTENT`. O índice não precisa de campo: `decidirSobreIndice()`
devolve `FETCH` sem `if` nenhum — revisita-se **sempre**, por lei, e o red team
mata quem lhe tocar (ataque M3). A separação existe no comportamento; não
existe no vocabulário do contrato.

As 186 linhas vivem em `medidas/RECOLLECTION-CENSO-V1.json`, uma por
contrato, com todos os campos. Aqui ficam as 20 que carregam evidencia,
declaracao ou elegibilidade — as restantes 167 sao uma so linha repetida:
topologia `UNKNOWN`, `RECOLLECTION_PROPOSED = UNKNOWN`, `CONFIDENCE = NONE`,
`NEEDS_HUMAN_REVIEW = YES`, e `BLOCKED_FOR_BIG_COLLECTION`.

| SOURCE_ID | UNIVERSE | ELEG. | TOPOLOGIA | ACTUAL | PROPOSTO | CONF. | EVIDENCE_TYPE | REVISAO |
|---|---|---|---|---|---|---|---|---|
| `IT-T10-022` | T10 | SIM | MIXED | MUTABLE | MUTABLE | MEDIUM | DATAS_NO_DOCUMENTO | NO |
| `IT-T2-001` | T2 | NAO | IMMUTABLE_DETAIL_URLS | IMMUTABLE | IMMUTABLE | HIGH | CONTRATO_MEDIDO | NO |
| `IT-T2-002` | T2 | NAO | MUTABLE_STABLE_URL | MUTABLE | MUTABLE | HIGH | CONTRATO_MEDIDO | NO |
| `IT-T2-004` | T2 | NAO | MUTABLE_STABLE_URL | MUTABLE | MUTABLE | HIGH | CONTRATO_MEDIDO | NO |
| `IT-T3-002` | T3 | NAO | IMMUTABLE_DETAIL_URLS | IMMUTABLE | IMMUTABLE | HIGH | CONTRATO_MEDIDO | NO |
| `IT-T3-005` | T3 | NAO | MUTABLE_STABLE_URL | MUTABLE | MUTABLE | HIGH | CONTRATO_MEDIDO | NO |
| `IT-T3-008` | T3 | NAO | IMMUTABLE_DETAIL_URLS | IMMUTABLE | IMMUTABLE | HIGH | CONTRATO_MEDIDO | NO |
| `IT-T3-010` | T3 | NAO | IMMUTABLE_DETAIL_URLS | IMMUTABLE | IMMUTABLE | HIGH | CONTRATO_MEDIDO | NO |
| `IT-T4-001` | T4 | NAO | IMMUTABLE_DETAIL_URLS | IMMUTABLE | IMMUTABLE | MEDIUM | CONTRATO_MEDIDO | NO |
| `IT-T7-002` | T7 | NAO | IMMUTABLE_DETAIL_URLS | IMMUTABLE | IMMUTABLE | HIGH | CONTRATO_MEDIDO | NO |
| `IT-T7-017` | T7 | SIM | MIXED | MUTABLE | MUTABLE | HIGH | DATAS_NO_DOCUMENTO | NO |
| `IT-T7-042` | T7 | SIM | MIXED | MUTABLE | MUTABLE | HIGH | DATAS_NO_DOCUMENTO | NO |
| `IT-T10-018` | T10 | SIM | LISTING_MUTABLE_DETAIL_IMMUTABLE | AUSENTE | UNKNOWN | LOW | FORMA_DO_ENDERECO | YES |
| `IT-T5-002` | T5 | NAO | LISTING_MUTABLE_DETAIL_IMMUTABLE | AUSENTE | UNKNOWN | LOW | FORMA_DO_ENDERECO | YES |
| `IT-T5-041` | NAO SEI | SIM | UNKNOWN | AUSENTE | UNKNOWN | NONE | SEM_EVIDENCIA | YES |
| `IT-T5-049` | T5 | SIM | MIXED | AUSENTE | UNKNOWN | LOW | FORMA_DO_ENDERECO | YES |
| `IT-T7-033` | T7 | SIM | UNKNOWN | AUSENTE | UNKNOWN | NONE | SEM_EVIDENCIA | YES |
| `IT-T7-043` | T7 | SIM | LISTING_MUTABLE_DETAIL_IMMUTABLE | AUSENTE | UNKNOWN | LOW | FORMA_DO_ENDERECO | YES |
| `IT-T8-001` | T8 | NAO | LISTING_MUTABLE_DETAIL_IMMUTABLE | AUSENTE | UNKNOWN | LOW | FORMA_DO_ENDERECO | YES |
| `IT-T9-008` | T9 | NAO | LISTING_MUTABLE_DETAIL_IMMUTABLE | AUSENTE | UNKNOWN | LOW | FORMA_DO_ENDERECO | YES |

**A evidência de cada uma, por extenso:**

- `IT-T10-018` — Myfruit.it
  um segmento proprio por item (30 enderecos); as 30 datas de modificacao sao a hora da NOSSA visita — nao dizem nada sobre a fonte
- `IT-T10-022` — Zootecnica International
  4 documentos com published+modified proprios; 3 editados mais de 24h depois de publicados; maior atraso 7.2 dias
- `IT-T2-001` — ARPAE Emilia-Romagna
  UPDATE_BEHAVIOR="ADITIVO" · 7D — provado por 7 edicoes seguidas na listagem · entrega PDF: o ficheiro publicado E a edicao
- `IT-T2-002` — ARPAV Veneto
  UPDATE_BEHAVIOR="SOBRESCRITA"
- `IT-T2-004` — SIAS — Servizio Informativo Agrometeorologico Siciliano
  UPDATE_BEHAVIOR="SOBRESCRITA — janela movel de 11 dias na mesma URL"
- `IT-T3-002` — Regione Campania — Servizio Fitosanitario Regionale
  UPDATE_BEHAVIOR="ADITIVO — cada edicao ganha arquivo proprio, a anterior permanece" · 7D — provado por 14 edicoes de SA em 2026 espacadas exatamente 7 dias · entrega PDF: o ficheiro publicado E a edicao
- `IT-T3-005` — Terre dell'Etruria — Societa Cooperativa Agricola
  UPDATE_BEHAVIOR="SOBRESCRITA — uma edicao por vez, a anterior desaparece"
- `IT-T3-008` — ARIF Puglia — Agenzia regionale per le attivita irrigue e forestali
  UPDATE_BEHAVIOR="ADITIVO" · 7D — provado por 11 edicoes listadas (N26 24/06 ate N36 02/09) com espacamento exato de 7 dias · entrega PDF: o ficheiro publicado E a edicao
- `IT-T3-010` — A.P.OL. — Associazione tra Produttori Olivicoli, Lecce
  UPDATE_BEHAVIOR="ADITIVO" · 7D — provado pelas DATAS dentro dos documentos preservados (VALID_FROM 31/08 e 07/09 = 7 dias exatos) · entrega PDF: o ficheiro publicado E a edicao
- `IT-T4-001` — Ministero della Salute — Open Data
  UPDATE_BEHAVIOR="ADITIVO por data de arquivo" · NÃO SEI — uma unica data observada · entrega CSV: o ficheiro publicado E a edicao
- `IT-T5-002` — Fondazione Edmund Mach — OpenPub (IRIS/CINECA)
  UPDATE_BEHAVIOR="ADITIVO" diz que item novo ganha morada nova, mas a entrega e HTML — uma pagina, nao um ficheiro fechado. Ninguem mediu se a pagina antiga e reescrita.
- `IT-T5-041` — SEM CONTRATO
  o portao admite esta fonte e NAO existe contrato nenhum para ela — nao ha onde declarar RECOLLECTION, e nao ha quem saiba ir la buscar
- `IT-T5-049` — UNICT Di3A
  um segmento proprio por item (4 enderecos); os documentos nao declaram data de publicacao nem de modificacao · OLHADO A OLHO: 2 das 4 moradas observadas nao sao artigos, sao quadros de avisos que acumulam itens na MESMA morada: /notizie/avvisi-lezioni e /notizie/avvisi-esami-e-prove-itinere. As outras 2 sao artigos com segmento proprio. Declarar IMMUTABLE a esta fonte cegava os dois quadros.
- `IT-T7-002` — MASAF
  UPDATE_BEHAVIOR="ADITIVO" · 1Y — tres edicoes anuais na mesma pagina (31/12/2023, 31/12/2024 REV.3, 31/12/2025) · entrega ODS: o ficheiro publicado E a edicao
- `IT-T7-017` — Cantina Sociale Cooperativa Riunite e CIV
  26 documentos com published+modified proprios; 19 editados mais de 24h depois de publicados; maior atraso 72 dias
- `IT-T7-033` — Consorzio Vino Chianti Classico
  nenhuma observacao guardada
- `IT-T7-042` — Consorzio di Tutela dell'Aceto Balsamico di Modena
  7 documentos com published+modified proprios; 3 editados mais de 24h depois de publicados; maior atraso 27.1 dias
- `IT-T7-043` — Agrofarma
  data no caminho (2 enderecos); os documentos nao declaram data de publicacao nem de modificacao
- `IT-T8-001` — Image Line Network S.r.l.
  UPDATE_BEHAVIOR="ADITIVO" diz que item novo ganha morada nova, mas a entrega e VIDEO_METADATA + PUBLIC_AUDIO — uma pagina, nao um ficheiro fechado. Ninguem mediu se a pagina antiga e reescrita.
- `IT-T9-008` — ADAMA Italia S.r.l.
  UPDATE_BEHAVIOR="ADITIVO" diz que item novo ganha morada nova, mas a entrega e BROWSER_RENDERED_EXTRACT — uma pagina, nao um ficheiro fechado. Ninguem mediu se a pagina antiga e reescrita.

---

## FASE 7–8 · OS DOIS GRUPOS DE RISCO

```
SAME_URL_OVERWRITE_COUNT = 6
NEW_URL_PER_ITEM_COUNT   = 6
```

### Grupo 1 · a mesma morada recebe factos novos

| SOURCE_ID | URL_PATTERN | PROOF_OF_OVERWRITE | CURRENT_BEHAVIOR | REQUIRED_BEHAVIOR |
|---|---|---|---|---|
| `IT-T10-022` | `https://zootecnicainternational.com/news/` | 4 documentos com published+modified proprios; 3 editados mais de 24h depois de publicados; maior atraso 7.2 dias | `REVALIDATE` a cada corrida, razao `CONTRACT_DECLARES_MUTABLE` | revisitar o detalhe — e o que passou a acontecer |
| `IT-T2-002` | `https://www.arpa.veneto.it/dati-ambientali/bollettini/agrometeo/agrometeoinforma` | UPDATE_BEHAVIOR="SOBRESCRITA" | `REVALIDATE` a cada corrida, razao `CONTRACT_DECLARES_MUTABLE` | revisitar o detalhe — e o que passou a acontecer |
| `IT-T2-004` | `http://www.sias.regione.sicilia.it/NHEOWL0530_00.html` | UPDATE_BEHAVIOR="SOBRESCRITA — janela movel de 11 dias na mesma URL" | `REVALIDATE` a cada corrida, razao `CONTRACT_DECLARES_MUTABLE` | revisitar o detalhe — e o que passou a acontecer |
| `IT-T3-005` | `https://www.terretruria.it/monitoraggio` | UPDATE_BEHAVIOR="SOBRESCRITA — uma edicao por vez, a anterior desaparece" | `REVALIDATE` a cada corrida, razao `CONTRACT_DECLARES_MUTABLE` | revisitar o detalhe — e o que passou a acontecer |
| `IT-T7-017` | `https://www.riuniteciv.com/news-e-eventi/` | 26 documentos com published+modified proprios; 19 editados mais de 24h depois de publicados; maior atraso 72 dias | `REVALIDATE` a cada corrida, razao `CONTRACT_DECLARES_MUTABLE` | revisitar o detalhe — e o que passou a acontecer |
| `IT-T7-042` | `https://www.consorziobalsamico.it/news-blog/` | 7 documentos com published+modified proprios; 3 editados mais de 24h depois de publicados; maior atraso 27.1 dias | `REVALIDATE` a cada corrida, razao `CONTRACT_DECLARES_MUTABLE` | revisitar o detalhe — e o que passou a acontecer |

### Grupo 2 · morada nova por item — e a descoberta, provada ou não

| SOURCE_ID | rota declarada | a descoberta foi provada? |
|---|---|---|
| `IT-T2-001` | PREDICTABLE_ROUTE | NAO SEI — nunca observada nesta arvore |
| `IT-T3-002` | PREDICTABLE_ROUTE | 3 observacoes, nenhuma falha de descoberta |
| `IT-T3-008` | PREDICTABLE_ROUTE | 3 observacoes, nenhuma falha de descoberta |
| `IT-T3-010` | DISCOVERED_ROUTE | 3 observacoes boas e 19 DISCOVERY_FAILED |
| `IT-T4-001` | PREDICTABLE_ROUTE | 3 observacoes, nenhuma falha de descoberta |
| `IT-T7-002` | DISCOVERED_ROUTE | NAO SEI — nunca observada nesta arvore |

---

## FASE 9 · A LEI REPOSTA

```
RECOLLECTION_UNKNOWN  ≠  NEVER_RECOLLECT
```

A correção **reutiliza o mecanismo que já existia** — o campo `DECLARADO`, que
era calculado e deitado fora. Não há enum novo de mutabilidade: `MUTABILIDADE`
continua a ser `["IMMUTABLE","MUTABLE","UNKNOWN"]`, palavra por palavra.

**E porque a correção não é «`UNKNOWN` passa a revisitar».** Seria trocar uma
avaria por outra maior: 174 contratos não declaram nada, e todos passariam a
bater à porta em todas as corridas, sem razão nomeada e sem nada para trazer.
A paridade acabara de provar `UNNECESSARY_REFETCHES = 0`; isso apagava a prova
e gastava a rede.

> Saltar o que muda cega a casa.
> Revisitar tudo o que não se conhece inunda-a.

A terceira porta, que é a que o briefing pediu: **o salto por ignorância
continua a ser um salto — mas deixa de ser calado.**

```
COBERTURA_DE_REVISITA = ["DECLARADA", "BLOCKED_FOR_BIG_COLLECTION"]
```

O que mudou, em concreto:

1. `recolheitaDoContrato()` — `UNKNOWN` escrito à mão deixa de contar como
   declarado. Carimbar «ainda não sei» não pode valer o mesmo que medir.
2. `decidirSobreDetalhe()` — o `SKIP_KNOWN` passa a dizer **porquê**:
   `COBERTURA: "DECLARADA"` ou `"BLOCKED_FOR_BIG_COLLECTION"`, e o segundo traz
   `AVISO` em texto.
3. `censoDasDecisoes()` — contador novo `DETAIL_SKIPPED_UNDECLARED`: a medida
   da cegueira que a corrida está a acumular.
4. `admissivelNaBigCollection()` — a porta. Devolve um **facto contável**, não
   uma excepção: um bloqueio tem de poder ser contado, listado e mostrado ao
   dono; uma excepção só pararia a corrida.

**A ida à rede não mudou em nenhum dos quatro casos.** Está provado abaixo.

---

## FASE 10–11 · PREENCHER E CONTAR

```
PARETO POR TOPOLOGIA — 186 contratos + 1 elegivel sem contrato = 187 linhas
   169  UNKNOWN
     6  IMMUTABLE_DETAIL_URLS
     5  LISTING_MUTABLE_DETAIL_IMMUTABLE
     4  MIXED
     3  MUTABLE_STABLE_URL

WITH_RECOLLECTION_BEFORE      7
WITH_RECOLLECTION_AFTER      12    IMMUTABLE 6 · MUTABLE 6
UNKNOWN_RECOLLECTION_AFTER   175    todos BLOCKED_FOR_BIG_COLLECTION
   dos quais SEM CONTRATO      1    IT-T5-041
```

---

## FASE 12 · RED TEAM

```
ATAQUES 12 · KILLED 12 · RED_TEAM_SURVIVORS 0
```

Os dez mínimos do briefing, mais dois que esta missão acrescentou por ter
encontrado o defeito. Protocolo cache-safe §165 traduzido para Node — o **mesmo
ficheiro de protocolo** de `provas/paridade_red_team.mjs`, de propósito: duas
casas de protocolo divergem, e a partir daí nenhuma vale.

`NODE_DISABLE_COMPILE_CACHE=1` · processo novo por ataque · diff provado ·
**sonda a provar que o mutante correu** · restauro em `finally` e conferido no
fim (`git diff` contra o índice, nunca `--porcelain`).

| # | ataque | morto pela prova |
|---|---|---|
| M1 | o salto cego volta a ser indistinguível do informado | contrato ausente e contrato IMMUTABLE não dão a MESMA resposta |
| M11 | carimbar `UNKNOWN` à mão compra a admissão | UNKNOWN escrito à mão não compra a admissão |
| M6 | a porta deixa entrar quem não declarou | admissivelNaBigCollection bloqueia quem não declarou |
| M3 | o índice deixa de se revisitar | o índice continua a revisitar-se sempre |
| M7 | um endereço que falhou nunca mais é tentado | os QUATRO resultados sem documento NÃO contam |
| M5 | a memória passa a ser indexada pela identidade | os CINCO resultados com documento contam todos como conhecido |
| M8 | tudo o que se conhece passa a ser revisitado | UNNECESSARY_REFETCHES continua ZERO |
| M10 | o salto conhecido vira ida à rede | nenhum valor de RECOLLECTION faz FETCH |
| M-CENSO | o censo deixa de contar o salto cego | o censo separa o salto informado do salto cego |
| M9 | mudança real em morada estável nunca é detectada | o TEXTO a mudar ⇒ MATERIAL_CHANGE |
| M2/M4 | uma regra volátil alarga-se até comer o corpo da matéria | o TEXTO a mudar ⇒ MATERIAL_CHANGE |
| M12 | a canonicalização come os cinco caracteres de HTML | os cinco caracteres com significado em HTML não se traduzem |

### ⚠️ Um sobrevivente fabricado, e como se apanhou

Na primeira corrida, M7 e M8 saíram `SURVIVOR`. **Não eram.** Os dois morreram
nas três suítes; o arnês é que só guardava as **4 primeiras** linhas de falha,
e a prova que interessava em M8 era a **sétima**. O arnês concluía «morreu pela
prova errada» e escrevia `SURVIVOR`.

> Truncar a evidência é fabricar um sobrevivente.

Corrigido no arnês (guarda todas as falhas), e **sem afrouxar** a verificação
de que o mutante morre pela prova certa — que é a que impede um mutante morto
por acaso de passar por morto de propósito.

`provas/RECOLLECTION-RED-TEAM-V1.json` guarda os doze recibos.

---

## FASE 13 · REGRESSÃO

```
NEW_FAILURES = 0
```

**Comparado por NOME, nunca por número** — e num caso o número teria mentido
nas duas direções.

### As suítes de regras (`.mjs`)

| suíte | base (`HEAD` limpo) | depois | novas falhas |
|---|---|---|---|
| `regras/italy_contract_test.mjs` | 352 ok · **73 falham** | 352 ok · **73 falham** | **0**, conferido nome a nome |
| `regras/incrementalidade_test.mjs` | 23 ok · 0 falham | 23 ok · 0 falham | 0 |
| `regras/paridade_test.mjs` | 31 ok · 0 falham | 31 ok · 0 falham | 0 |
| `regras/motor_de_rota_test.mjs` | 47 ok · 0 falham | 47 ok · 0 falham | 0 |
| `regras/recollection_test.mjs` | *(não existia)* | **31 ok · 0 falham** | — |

As 73 falhas de `italy_contract_test.mjs` **já chegam vermelhas no `HEAD`** —
medidas com a minha alteração fora da árvore, antes de qualquer conclusão. Os
73 nomes são os mesmos antes e depois: nenhum entrou, nenhum saiu.

### A suíte Python — 219 módulos, um a um

Corrida **módulo a módulo, com prazo próprio de 90 s cada**, nos dois estados.
A primeira tentativa foi num processo único com os 219 módulos, e **pendurou**
num teste da curadoria que lança um worker real contra a rede — treze minutos
sem uma linha. Um módulo pendurado escondia os outros 218; o prazo por módulo
resolve isso e ainda permite atribuir cada falha ao seu nome.

| | base | depois |
|---|---|---|
| módulos OK | 159 | 160 |
| módulos com prazo esgotado | 7 | 4 |
| linhas de falha | 157 | 164 |

Os três módulos que «ganharam» falhas eram **exactamente** os três que tinham
esgotado o prazo na base: não falharam de novo — é que na base nem chegaram ao
fim. Repetidos com 300–500 s **nos dois estados**, dão o mesmo:

| módulo | base | depois |
|---|---|---|
| `tests.test_a_collection_preserva_o_fato` | OK | OK |
| `tests.test_a_linhagem_do_ready_e_do_raw_asset` | 6 falhas | 6 falhas |
| `tests.test_a_porta_cli_liga_o_banco` | 1 falha | 1 falha |
| `tests.test_cliente_postgres` | 1 falha | 1 falha |
| `tests.test_social_sessao` | 2 falhas | 2 falhas |
| `tests.test_atomicidade_da_intelligence` | **103 falhas** | **103 falhas**, os mesmos nomes |
| `tests.test_o_controle_separa_lei_de_mencao` | prazo esgotado | prazo esgotado |

### ⚠️ A trava da Intelligence quase foi mordida por acidente

`provas/arbitragem_da_intelligence.py` faz `git grep` sobre a árvore
**inteira** à procura de termos da Intelligence, e conta quem os menciona por
camada. Dois dos meus ficheiros entram nessa conta:

- `CONFIDENCE` — que é termo da Intelligence **e** uma coluna que a própria
  missão pediu na tabela do censo;
- `BUILD_ID` — que casa dentro de `DRUPAL_FORM_BUILD_ID`, o nome de uma regra
  nova do normalizador, e não tem nada a ver com pacotes da Intelligence.

Por isso a base deste módulo foi medida com **tudo** revertido — os quatro
ficheiros alterados, os seis novos tirados do índice e do disco, e o know-how
devolvido ao `HEAD` — e não apenas com o JSON reposto. Deu 103 nas duas
medições, com os mesmos nomes. A trava não se mexeu.

**O que isto não prova:** a trava já reprova 103 provas no `HEAD`, e esta
missão não a arruma. Continua vermelha, como estava.

### O que a própria medição sujou, e ficou limpo

A suíte reescreve `data/derivados/O-CENSO-DA-SALA-DE-ESPERA.json` ao correr —
66 linhas mudadas. Foi devolvido ao estado do índice depois das medições. A
árvore entregue não leva resíduo de medição.

---

## FASE 14 · MAPA

<!-- MAPA -->

---

## FASE 15 · ATLAS — como cada fonte publica, em português

Sem sigla e sem enum. É assim que cada uma das doze fontes classificadas
publica, dito como se diria a uma pessoa:

**As que abrem morada nova de cada vez — e a antiga fica quieta**

- **`IT-T3-002` · Região da Campânia** — publica cada boletim num ficheiro
  novo, com a data no próprio nome. Catorze edições seguidas, de sete em sete
  dias exactos. O boletim da semana passada continua onde estava, igual.
- **`IT-T3-008` · ARIF Puglia** — o mesmo, com número e data no nome do
  ficheiro. Onze edições contadas, às quartas-feiras.
- **`IT-T3-010` · APOL, Lecce** — um ficheiro novo por edição. **Mas** a página
  que os lista já nos fechou a porta: dezanove tentativas seguidas recusadas
  numa hora de 14 de setembro. Voltou a abrir. Fica debaixo de olho.
- **`IT-T4-001` · Ministério da Saúde** — uma folha de dados nova por data, com
  a data no nome.
- **`IT-T2-001` · ARPAE Emília-Romanha** — um PDF novo por edição, de sete em
  sete dias.
- **`IT-T7-002` · MASAF** — uma folha por ano. Quando corrigem, a correção
  ganha nome próprio («REV.3») em vez de apagar a anterior.

**As que escrevem sempre na mesma morada, por cima do que lá estava**

- **`IT-T3-005` · Terre dell'Etruria** — há uma página só. A edição nova apaga
  a anterior, e não existe arquivo: o que não se apanhar a tempo, perde-se.
- **`IT-T2-002` · ARPAV Veneto** — a mesma página, reescrita a cada edição.
- **`IT-T2-004` · SIAS Sicília** — a mesma página, com uma janela de onze dias
  que vai andando: todos os dias entra um dia novo e sai o mais velho.

**As que fazem as duas coisas ao mesmo tempo — e são as que quase nos enganaram**

- **`IT-T7-017` · Cantine Riunite & CIV** — cada notícia nova tem morada
  própria, como seria de esperar. Só que **voltam a mexer nas notícias
  antigas**: de vinte e seis artigos, dezanove foram editados mais de um dia
  depois de publicados, e um deles setenta e dois dias depois. A morada não
  muda quando isso acontece.
- **`IT-T7-042` · Consórcio do Aceto Balsâmico de Módena** — o mesmo, em três
  de sete artigos, com um editado vinte e sete dias depois.
- **`IT-T10-022` · Zootecnica International** — o mesmo, em três de quatro, com
  uma semana de intervalo.

**As que ainda não sabemos ler** — cinco das oito que hoje estão aprovadas para
colher, e as outras cento e sessenta e nove. Dessas cinco, duas merecem nome:

- **`IT-T10-018` · myfruit** — as páginas dizem «modificado em», mas a hora que
  lá está é a hora a que **nós** batemos à porta. O campo não fala da fonte,
  fala de nós. Não dá para classificar por aqui.
- **`IT-T5-049` · Universidade de Catânia** — é meio e meio. Duas das quatro
  moradas que colhemos são artigos; as outras duas são **quadros de avisos**
  («avisos de aulas», «avisos de exames») que vão acumulando coisas novas na
  mesma morada. Dizer que esta fonte «não muda» cegava os dois quadros.
- **`IT-T5-041`** — esta é de outra natureza: está aprovada para colher e **não
  tem contrato nenhum**. Não há onde declarar como se revisita, e não há quem
  saiba ir lá buscar.

---

## FASE 16 · KNOW-HOW

`KNOW_HOW_DELTA` publicado em secção nova do canónico. Ver
`SINTONIA-EAME-KNOW-HOW.md`.

---

## GATE

```
COLLECTION_ELIGIBLE           8   (curadoria/collection_gate.py)
  com RECOLLECTION declarada  3   IT-T7-017 IT-T10-022 IT-T7-042
  BLOCKED_FOR_BIG_COLLECTION  5   IT-T10-018 IT-T5-049 IT-T7-033 IT-T7-043 IT-T5-041

RECOLLECTION_COVERAGE = 8/8  comportamento EXPLICITO e seguro
                        3/8  declarado (colhe e revisita)
                        5/8  bloqueado  (nao entra ate ser classificado)
```
- `IT-T10-018` — **BLOCKED_FOR_BIG_COLLECTION** — RECOLLECTION nao declarado — sem isso a fonte colhe uma vez e nunca mais e revisitada, e ninguem daria por isso
- `IT-T10-022` — **DECLARADA** — o contrato declara DETAIL_CONTENT=MUTABLE
- `IT-T5-041` — **BLOCKED_FOR_BIG_COLLECTION** — RECOLLECTION nao declarado — sem isso a fonte colhe uma vez e nunca mais e revisitada, e ninguem daria por isso
- `IT-T5-049` — **BLOCKED_FOR_BIG_COLLECTION** — RECOLLECTION nao declarado — sem isso a fonte colhe uma vez e nunca mais e revisitada, e ninguem daria por isso
- `IT-T7-017` — **DECLARADA** — o contrato declara DETAIL_CONTENT=MUTABLE
- `IT-T7-033` — **BLOCKED_FOR_BIG_COLLECTION** — RECOLLECTION nao declarado — sem isso a fonte colhe uma vez e nunca mais e revisitada, e ninguem daria por isso
- `IT-T7-042` — **DECLARADA** — o contrato declara DETAIL_CONTENT=MUTABLE
- `IT-T7-043` — **BLOCKED_FOR_BIG_COLLECTION** — RECOLLECTION nao declarado — sem isso a fonte colhe uma vez e nunca mais e revisitada, e ninguem daria por isso

---

## EM PALAVRAS SIMPLES

Imagine que o sistema é um carteiro que vai buscar jornais a 186 bancas.

**O problema que havia.** O carteiro tinha uma regra: *«se já fui a esta banca
e trouxe o jornal, não volto lá».* Para uma banca que só põe jornais **novos**
na prateleira, isso está certo — o jornal de ontem não muda. Mas há bancas que
**riscam e reescrevem o jornal que já lá está**. A essas, o carteiro não
voltava. Nunca mais.

E o pior: o carteiro tratava **da mesma maneira** duas coisas muito diferentes:

- *«eu sei que esta banca nunca muda o jornal»* — e
- *«eu não faço ideia do que esta banca faz»*.

As duas davam «não volto lá». **Em 179 das 186 bancas, ninguém tinha feito
ideia nenhuma** — e todas elas eram tratadas como se alguém tivesse
verificado. O sistema ficava cego e ninguém dava por isso, porque em lado
nenhum aparecia um número a dizê-lo.

**Quantas fontes são de cada tipo.** Hoje, das 186:

- **6 abrem morada nova de cada vez** — cada boletim é um ficheiro novo, com a
  data no nome. A estas o carteiro pode não voltar, e está certo.
- **3 escrevem sempre na mesma morada, por cima** — a edição nova apaga a
  anterior. A estas o carteiro **tem** de voltar.
- **3 fazem as duas coisas** — abrem morada nova para a notícia nova, mas
  depois voltam a mexer nas antigas. Uma delas mexeu numa notícia **setenta e
  dois dias** depois de a publicar. A estas também tem de voltar.
- **174 ainda não sabemos** — e é a maioria, de longe.

**Como o sistema vai saber quando voltar.** Cada banca passa a ter um bilhete
que diz uma de duas coisas: *«esta nunca muda»* ou *«esta muda»*. Quem não tem
bilhete **não entra na colheita grande** — fica de fora, com o nome numa lista,
até alguém ir lá ver. Deixou de ser um esquecimento silencioso e passou a ser
uma porta fechada com um papel colado.

**Alguma pode ficar cega?** Das 8 que hoje estão aprovadas para colher: 3 têm
bilhete e serão revisitadas; 5 estão barradas por não terem. **Nenhuma entra às
escuras.** Uma dessas cinco, a `IT-T5-041`, está aprovada e nem sequer tem
contrato — está aprovada uma banca cuja morada ninguém escreveu.

**O comportamento perigoso foi corrigido?** Sim, e sem partir o que já
funcionava. O carteiro **não passou a bater a mais portas**: continua a saltar
exactamente as mesmas de antes, e a conta de idas desnecessárias continua em
zero. O que mudou é que, quando ele salta por ignorância, isso fica **escrito e
contado** — e essa banca não entra na colheita grande.

**Três coisas que quase nos enganaram, e que vale a pena o dono saber:**

1. Tínhamos 83 comparações a dizer «nada mudou». Pareciam prova de que as
   fontes eram estáveis. Só que as duas visitas comparadas estavam a **8,7
   minutos** de distância uma da outra. Isso não prova nada sobre uma semana.
   Três fontes que essa conta dava como «não muda» carregam, dentro das
   próprias páginas, a prova de que mudam ao fim de semanas.
2. Outras 44 comparações diziam «mudou» — e **nenhuma** era mudança a sério.
   Eram códigos aleatórios que os sites põem a cada visita. Sem isso corrigido,
   três fontes teriam sido marcadas como «muda sempre» e passariam a ser
   visitadas todos os dias, para nada.
3. Uma página do catálogo da **ADAMA** ia ser marcada como «nunca muda», por
   causa de uma regra que parecia razoável. Uma mudança de rótulo é exactamente
   o que queremos ver nessa página. Ficou de fora.

**A colheita grande está pronta deste ponto de vista?** Sim — no sentido
estrito: nenhuma fonte entra às cegas. Mas com uma ressalva que não se deve
arredondar para cima: **das 8 aprovadas, só 3 têm bilhete.** Se a colheita
grande arrancasse hoje, as outras 5 ficavam de fora. Isso é seguro — é melhor
do que colhê-las e nunca mais lá voltar — mas é muito menos do que 8, e não é
a mesma coisa que «está tudo resolvido».

**A Big Collection não foi executada.** Nada foi colhido nesta missão, e não se
tocou na rede uma única vez.
