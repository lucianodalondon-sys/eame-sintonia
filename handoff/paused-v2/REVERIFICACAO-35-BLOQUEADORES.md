# §12 · Os 35 bloqueadores, reverificados — COMPLETO

> O passo que o handoff mandava dar. **Está dado.**
>
> Todo número aqui sai de `handoff/paused-v2/REVERIFICACAO-LEDGER.json`, que se
> reconstrói da evidência bruta: `python3 scripts/v21_reverificacao_ledger.py`

---

## 1 · Como foi feito

A auditoria original produziu 99 achados e **parou antes da refutação**. O desenho
previa três céticos por achado; nenhum rodou. O handoff é explícito:

> **Um achado não refutado não é um defeito: é uma suspeita.**

A refutação rodou agora, em 9 grupos temáticos — agrupados por **medição
compartilhada**, não por conveniência: B05 e B12 são os mesmos registros
Friuli↔Toscana; B13, B25 e B35 são uma só pergunta de província; B01, B28 e B33
são o mesmo portão. Medir o grupo uma vez impede três vereditos que se contradizem.

Por grupo: **um leitor mede** → **dois céticos independentes** atacam (um refaz a
conta do zero, outro aceita os números e ataca o julgamento) → **um juiz** mede o
ponto exato da divergência quando algum cético derruba. Nenhum agente podia editar
arquivo: a fase era só medição.

**A refutação não foi carimbo.** Ela mudou o veredito em 3 dos 35:

| Achado | Primeira leitura | Veredito final | Quem decidiu |
|---|---|---|---|
| B11 | `ALREADY_FIXED` | **`NEEDS_CORRECTION`** | juiz |
| B17 | `CONFIRMED_BLOCKER` | **`NEEDS_CORRECTION`** | juiz |
| B24 | `NEEDS_CORRECTION` | **`CONFIRMED_BLOCKER`** | juiz |

Mudou nos dois sentidos — um agravou, dois aliviaram. É o que uma refutação
honesta parece.

---

## 2 · O resultado

```
CONFIRMED_BLOCKER  15
NEEDS_CORRECTION   16
ALREADY_FIXED       4
FALSE_POSITIVE      0
                   ──
                   35
```

### A previsão de quem retomou estava errada

Ao retomar, escrevi que *"espero que boa parte caia como ALREADY_FIXED ou
FALSE_POSITIVE"*, porque a auditoria correu enquanto o pacote era reescrito.
**Caíram quatro, e nenhum foi falso positivo.**

O padrão que explica: a reescrita corrigiu exatamente o que o auditor viu quebrar
na frente dele — os cruzamentos sem carimbo (B01, B33), o README que sumira (B27),
a camada de tradução que não existia às 15:02 e existia às 15:07 (B21) — e **não
tocou em mais nada**. A regra do handoff continua de pé; mas neste lote a suspeita
quase sempre tinha razão. O crédito é da auditoria pausada.

---

## 3 · Os 15 que bloqueiam, por causa-raiz

Não são 15 consertos. São **seis**.

### R1 · A geografia promovida — B05, B06, B12, B13 *(+ B25, B35 menores)*

O maior bloco, e a lei está escrita no cabeçalho do arquivo que a quebra.

- **18 registros client-safe** carregam par de regiões que **nenhum documento
  cobre**: boletins das províncias marchigianas carimbados `REGION_UMBRIA`;
  boletins da Úmbria carimbados `REGION_MARCHE`; boletins provinciais da Toscana
  carimbados `REGION_FRIULI_VENEZIA_GIULIA`; boletins da ERSA Friuli carimbados
  `REGION_TOSCANA`.
- **14 registros** de escopo `REGIONAL` trazem nome de província no próprio título.
- «Trentino» virou «Trentino-Alto Adige»; Bolzano e Trento entram como região e
  carregam o ID da região inteira — somar duplica o Trentino.

> **PROVINCIAL ≠ REGIONAL.** Um boletim de Grosseto não fala pela Toscana, e muito
> menos pelo Friuli.

**Conserto:** re-derivar `REGION_IDS` do documento que cada registro cita, criar
`PROVINCE_IDS`, e proibir promoção no `v21_normalizar.py`. **Nunca** por
casamento de texto — foi assim que o `TOP-CROSSINGS` do V2 morreu.

### R2 · A sentinela que promete fonte — B07, B08, B19 *(+ B10)*

**2.217** registros client-safe (não 2.222 — meu número manda) citam
`SRC_NAO_DECLARADA` como única fonte, com `SOURCE_URLS=[]`, e exibem ao lado um
texto de tela que diz *"com fonte e data"* / *"com URL e data"*. Nos cruzamentos:
**129 de 175** apoios, atingindo **18 dos 20** (o achado dizia 16).

**O que a auditoria não mediu, e muda o conserto:** **2.213 dos 2.217 têm
procedência real recuperável dentro do próprio pacote**, sem coleta nova — 1.512
resolvem por `REGISTRATION_NUMBER` em `PRODUCTS-REGULATORY`, 621 têm URL no
próprio corpo, 701 resolvem por `SOURCE_ID` legado. **Sobram 4** sem endereço:
`IT-WIN-001`, `IT-WIN-002`, `IT-WIN-004`, `IT-WIN-005`.

**Conserto:** religar os 2.213 e, para os 4, trocar o texto do carimbo — não o
carimbo. E `SRC_ADAMA_COM` está `BLOCKED` sustentando 66 registros client-safe:
**FONTE BLOQUEADA ≠ FONTE INEXISTENTE**, mas o texto tem de dizer qual das duas.

### R3 · O README promete o que o pacote não cumpre — B02, B09, B15

- *"Sete das dez culturas do piloto não têm dado de mercado"* — o próprio arquivo
  interno diz que eram sete e hoje é **uma**. O README ficou no número velho.
- *"`SOURCES.json` guarda o teste de rota **de cada fonte**"* — nas **31 fontes
  client-safe** os campos `ACCESS_EVIDENCE` e `REQUIRES_ITALIAN_ROUTE` **não estão
  vazios: não existem**. Inclui `SRC_SALUTE_GOV_IT`, que sustenta as 163 linhas
  regulatórias. O teste de rota é artefato exclusivo da rodada `LAST_MILE` (98/152).
- O `ACCEPTANCE-REPORT` se dá atestado limpo em separação porque mede **nome de
  arquivo**, nunca o conteúdo dos `RECORDS`.

> **O relatório que só mede o que sabe medir não está errado. Está incompleto — e
> parece completo.**

### R4 · O cruzamento que junta o que não se junta — B04, B14

O cruzamento de mercado da oliveira usa **preço de azeite**, de outra região.
E os 17 cruzamentos client-safe declaram **provada a invariante C** (geografia
nunca promovida) apoiando-se justamente nos registros de R1.

> **Declarar provado o que não foi medido é pior que não declarar.**

*(Nota: `INVARIANTS` tem 7 chaves — A, C, D, E, F, G, H. Não existe B. O README
fala em "oito invariantes".)*

### R5 · Papel de trabalho como inteligência — B16

Dois registros `CLIENT_SAFE=true` em `REGULATORY-FUTURE` **não são sinal
regulatório: são a receita de como raspar o site da UE**. A mesma URL está
cadastrada em `SOURCES.json` como `CLIENT_SAFE=false`. O pacote contradiz a
própria §18.

### R6 · A vista que mente sobre o próprio filtro — B31 *(+ B24)*

`FUTURE-EVENTS` diz ser *"subconjunto com data a partir de 02/09/2026"*, e **21 dos
23 registros não têm campo de data nenhum**. O filtro real, em
`v21_ingest_b.py:302`, é comparação de **string** sobre `REFERENCE_DATE` — campo de
procedência em prosa livre. Qualquer valor começando por letra (`"NAO_SEI — página
sem data..."`) é lexicograficamente maior que `"2026-09-02"` e entra.

E B24: existe **1** registro client-safe sem nenhum campo de tela
(`IT-CAN-54305CD76F`), não 48 — mas ele leva a ressalva de lei só no bloco
`RESEARCH`, que a tela não mostra.

---

## 4 · Três defeitos que nenhum dos 99 achados tinha visto

Apareceram porque os céticos mediram o que ninguém lhes pediu:

1. **`SOURCES.json`, cabeçalho.** `BY_QA` e `BY_ORIGIN` declaram somar **177**; o
   corpo tem **185**, e a classe `DERIVED_V2_1` nem aparece na quebra. O
   `ACCEPTANCE-REPORT` não vê porque só confere `COUNT_TOTAL` e
   `COUNT_CLIENT_SAFE`, nunca `BY_QA`/`BY_ORIGIN`.
2. **A língua declarada vs. a medida.** O relatório diz
   `AINDA_SO_EM_PORTUGUES: 0`. Há **312 valores client-safe** em campos que os
   próprios cabeçalhos listam em `LOCALIZED_FIELDS` e que existem **sem** irmão
   `_IT`. O relatório mediu o conjunto que ele traduziu, não o que promete.
3. **Sem identidade de build.** Os 25 arquivos trazem `BUILT_AT: "2026-09-02"` —
   só data, sem hora — e **zero** `BUILD_ID` ou hash. Duas pastas com conteúdo
   diferente dizem, as duas, a mesma coisa.

---

## 5 · O que NÃO se faz para fazer isto sumir

- **Não rebaixar `CLIENT_SAFE` para zerar contador.** Em quase todos os 15 o fato
  é verdadeiro e a fonte existe; o que falta é a ressalva. **Rebaixar não é a
  correção; a correção é dizer a verdade inteira.**
- **Não promover `QA_UNREVIEWED`** para fechar afirmação.
- **Não rodar passo do meio da cadeia.** `v21_ingest.py` faz `rmtree` e apaga em
  silêncio carimbo, rechaveamento e tradução. Roda-se `v21_cadeia.sh` inteiro.
- **Não juntar por nome aproximado.** Foi o método que matou o `TOP-CROSSINGS`.
- **Não recolher dado novo.** Os 2.213 endereços já estão dentro do pacote.

---

## 6 · Estado

| | |
|---|---|
| reverificados | **35 de 35** |
| exigem ação no dado | **31** (15 bloqueiam + 16 corrigem) |
| encerrados sem ação | **4** (`ALREADY_FIXED`) |
| corrigidos no dado até agora | **0** — medir vem antes de mexer |

**Próximo passo:** aplicar R1–R6 pela cadeia inteira, na ordem em que uma correção
não desfaz a outra — geografia antes dos cruzamentos, porque os cruzamentos
declaram a invariante que a geografia quebra.
