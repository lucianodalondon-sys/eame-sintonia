# A completude da oportunidade · o que o cartão deixou de olhar

> Todo número deste relatório sai de `scripts/v21_completude_oportunidade.py`, que
> lê o pacote **servido** (`italia-portale/client/italy-handoff-v21.js`,
> `BUILD_ID V21-69bf448ac934a6d9`, 43 oportunidades), o instantâneo da reunião
> (`meeting-intelligence-snapshot.json`) e o pacote que chega ao browser
> (`italy-casa.js`) — e reconta do zero a cada corrida.
> Saída medida: `data/samples/IT-COMPLETUDE/IT-COMPLETUDE-OPORTUNIDADE.json`.

---

## 0 · O relato, e o que a medição achou

Chegou um relato: **uma oportunidade de VITE DA VINO mostrava um único produto
ADAMA**, havendo vários.

O relato está certo, e a causa não é a que ele sugere. O motor **não** escolhe um
produto cedo demais. Ele encontra vários, e há **quatro reduções em série** entre
o acervo e o ecrã — nenhuma delas visível de dentro da seguinte.

```
2.171  produtos ADAMA que o acervo tem para as culturas dos 43 cartões
  463  os que o rótulo ministerial autoriza para o PAR do caso
  280  os que sobrevivem ao corte  produtos[:12]  em v21_oportunidades.py
   65  os que chegam ao ecrã depois de cruzados com o catálogo comercial
```

> **UM PRODUTO NO ECRÃ NÃO É UMA ESCOLHA PRECOCE: É UM FUNIL SEM CONTADOR.**
> O que faltava não era procurar mais — era dizer, em cada degrau, quantos
> ficaram para trás e porquê.

---

## 1 · O caso-testemunha VITE DA VINO

| pergunta | resposta medida |
|---|---:|
| **`VITE_DA_VINO_TOTAL_PRODUCTS`** | **71** |
| rótulo ministerial (`CROP_ON_LABEL = VITE`) | 25 |
| registo ministerial ADAMA (`CROP_IDS ⊇ CROP_GRAPEVINE`) | 61 |
| censo do catálogo ADAMA, grafia «Vite da vino» | 15 |
| catálogo comercial **já no pacote** | 10 |

As quatro casas sobrepõem-se; **71** é a união, deduplicada por nome
normalizado.

### O que a Opportunity enxergou

| cartão | arquétipo | alvo | rótulo no par | no pacote | **no ecrã** |
|---|---|---|---:|---:|---:|
| `OPP_AA1A1FF77C8D` | O5 regulatório | — | 25 | 12 | **1** |
| `OPP_00C5B6E15185` | O6 ciência→campo | — | 25 | 12 | 4 |
| `OPP_BCD174C535AC` | O4 concorrência | — | 25 | 12 | 4 |
| `OPP_F383CF46E5BF` | O2 mercado | — | 25 | 12 | 4 |
| `OPP_D9B21D005CC3` · `DF0C3648893A` · `E138ECDFD7D2` | O1 campo | peronospora | 12 | 12 | 2 |
| `OPP_48C2731BAFD1` · `D11664591168` | O1 campo | scafoideo | 6 | 6 | 1 |
| `OPP_169BD86DB324` · `3C8C3960CC66` | O1 campo | tignoletta | 5 | 5 | 1 |
| `OPP_5F31A63F844D` · `F8106D5E1767` | O1 campo | botrite | 3 | 3 | 1 |
| `OPP_195919127658` · `C1735138E362` · `C5F7888EC524` | O1 campo | oídio | 2 | 2 | **0** |

O cartão do relato é `OPP_AA1A1FF77C8D`: **1 produto no ecrã** — FOLPAN GOLD —
com a razão escrita no próprio instantâneo:

```
PRIMARY_MATCH_REASON = "UNICO_PRODUTO_DO_CATALOGO_NO_PAR"
VALIDATION_STATE     = "LABEL_AND_CATALOG"
```

### Por que os outros ficaram de fora

Não por não servirem. Por **não estarem no catálogo comercial do pacote** — e o
catálogo do pacote está incompleto (§3).

### Há diferença entre VITE, VITE DA VINO e outras grafias?

**Sim, e é ela que esconde produtos.** Três vocabulários, sem ponte:

| onde | grafia |
|---|---|
| rótulo ministerial | `VITE` (96 linhas de uso) |
| catálogo público ADAMA | `Vite da vino` (15 produtos) · `Vite da tavola` (12) |
| corpus de vídeo SENSOR-PILOT | `VINE` (213 vídeos) |

**Cinco produtos que declaram «Vite da vino» na própria ficha do site nunca
chegaram ao pacote como videira:**

| produto | como chegou ao pacote |
|---|---|
| Activus® ME | `CROP_IDS = [MAIS, POMODORO, RISO, SOIA]` — videira caiu |
| Leopard® 5 EC | `CROP_IDS = []` |
| Taifun® MK CL PFNPE | `CROP_IDS = []` |
| Nimrod® 250 EW | sem `CROP_IDS` |
| Cosayr® 200 SC | sem `CROP_IDS` |

### Algum produto biológico ou permitido em bio foi ignorado?

**NÃO SEI.** O acervo não carrega, em nenhuma das quatro casas, um campo que
declare regime biológico, bio-estimulante ou admissibilidade em agricultura
biológica. `CATEGORY` só distingue ERBICIDI / FUNGICIDI / INSETTICIDI / SPECIALI.
Responder outra coisa seria inventar o campo.

### Esses produtos têm relação com o problema, ou só com a cultura?

Esta é a pergunta certa, e a conta fecha nos 43 cartões
(`CONTA_DO_PORTFOLIO_FECHA_EM_TODAS = true`):

```
PRODUTOS_ADAMA_ENCONTRADOS = LIGADOS + NÃO_LIGADOS + NÃO_SEI
```

Para VITE, por alvo, **o que o rótulo ministerial nomeia** (classe A):

| alvo | produtos ligados |
|---|---|
| peronospora | AGHARTA · ANTERLEX · BADGER 45% WG · BANJO · CARSON 45% WG · DAUPHIN 45 · EMBRACE · FOLPAN GOLD · MOMENTUM PFNPE · MOXYL MK · SESTO GOLD · VANTEX (12) |
| afídeos | DURAVIS · ELTIRA · EVURE PRO · KLARTAN 20 EW · KLARTAN SMART · LAMDEX EXTRA · MAVRIK EW · MAVRIK SMART · TAU AL 240 EW (9) |
| scafoideo | EVURE PRO · KLARTAN 20 EW · KLARTAN SMART · MAVRIK EW · MAVRIK SMART · TAU AL 240 EW (6) |
| tignoletta | DURAVIS · ELTIRA · FORZA · LAMDEX EXTRA · NINJA (5) |
| botrite | AGHARTA · BANJO · EMBRACE (3) |
| oídio | CUSTODIA ULTRA · MIRADOR TURBO (2) |

Tudo o resto do universo de 71 é **B (não ligado ao alvo)** quando o cartão tem
alvo, ou **C (NÃO SEI)** quando não tem — porque sem alvo declarado nada permite
aceitar nem rejeitar.

> **PRODUTO DISPONÍVEL PARA VITE NÃO É PRODUTO INDICADO PARA ESTE CASO.**
> A conta fecha porque a classe C existe, não apesar de ela existir.

---

## 2 · O caso-testemunha MAIS

O acervo de concorrência está cheio de milho. **Isso não é necessidade
agronómica**, e o denominador prova-o.

| | |
|---|---:|
| **`MAIZE_COMPETITOR_ACTIVITIES`** | **70** |
| denominador — peças com cultura canónica declarada | 208 |
| denominador — corpus inteiro de concorrência | 577 |
| peças **sem** cultura declarada | 421 |
| **peças de milho ATIVAS hoje** | **2** |

**`MAIZE_ACTIVE_ADVERTISERS`** — anunciantes no corpus histórico: BASF 22 ·
Corteva 20 · FMC 13 · Bayer 9 · UPL 3 · não declarado 3.
**Ativos agora: só Corteva, com duas peças** — e o texto delas é institucional,
não agronómico: *«C'è un campo che racconta 100 anni di rivoluzione nel mais»* e
*«Il pastone di mais è un alimento di alto valore…»*.

Temas comunicados: infestanti 11 · malattie 7 · parassiti 5 · Fusarium 4 ·
Amaranthus 2 · insetti 1. Produtos provados nas peças: Coragen 8 · Spectrum 8 ·
Arc 9 · Belanty 6 · Revysol 4 · Retengo 4 · outros.

Datas: de 2025-06-26 a 2026-08-14, com pico em 2026-03 (13) e 2026-07 (11).

**Há concentração temporal recente? NÃO SEI — e não se chama aumento.**
`COUNTRY_SEMANTICS = AD_REACHED_COUNTRY != AD_TARGETED_COUNTRY` em todas as 67
peças pagas, e não há série por ano que sirva de baseline.

**Geografia provável:** `REGION_IDS` = `GEO_ITALY` em 69 das 70. Uma única peça
tem região (`REGION_PIEMONTE`). **Alcance não é mira.**

### Janelas de MAIS

**`MAIZE_REGIONS_WITH_OPEN_WINDOW` = 0 — e o zero é do acervo, não do campo.**

O pacote inteiro tem **7 registos de janela**, e nenhum é de milho: seis de VITE
(flavescência dourada em Veneto, Lombardia, Piemonte, Trentino, Emilia-Romagna;
cocciniglie em Modena) e um de OLIVO (mosca).

Quais estão perto de abrir? Quais já fecharam? **NÃO SEI**, pela mesma razão.
Derivar janela de calendário seria inventar o facto que falta.

### Sinais de campo de MAIS — `MAIZE_CURRENT_FIELD_SIGNALS = 6`

| id | região | alvo | data | o que o boletim manda fazer |
|---|---|---|---|---|
| `IT-PHEN-048` | Friuli-Venezia Giulia | piralide | 2026-08-12 | **limiar declarado**: tratamento justificado acima de 3 oviposições/100 plantas |
| `IT-PHEN-022` | Lombardia | diabrotica | 2026-07-24 | **PROIBIÇÃO**: durante a floração vigora o *divieto* de inseticida, a bem das abelhas |
| `IT-COL-2609-LO-REGRA-MAIS` | Lombardia | diabrotica | 2026-01-01 | disciplinar de produção integrada |
| `IT-PHEN-014` | — | blast | 2026-08-28 | **sem recomendação de produto**: só monitorização |
| `IT-PHEN-005` · `IT-PHEN-003` | Emilia-Romagna | ticchiolatura | 2026-08 | — |

O motor lê a direção corretamente, e isso é crédito dele:

| cartão | direção | prioridade comercial |
|---|---|---|
| `OPP_9C600748BB1B` MAIS × piralide × **FVG** | `POSITIVE_PRESSURE` | **SALES_READY** |
| `OPP_81C053E9DCD3` MAIS × piralide × Lombardia | `TREATMENT_PROHIBITED` | TO_VALIDATE · `NEED_CLOSED` |
| `OPP_F6EEF5B32F65` MAIS × diabrotica × Lombardia | `TREATMENT_PROHIBITED` | TO_VALIDATE · `NEED_CLOSED` |

### O portfólio de MAIS

| | |
|---|---:|
| **`MAIZE_ADAMA_PRODUCTS_TOTAL`** | **43** |
| rótulo ministerial | 20 |
| registo ministerial | 36 |
| censo da ficha do site | 12 |
| catálogo no pacote | 6 |
| **`MAIZE_PRODUCTS_RELEVANT_TO_CURRENT_SIGNALS`** | **5** |

Ligados a piralide **e** a diabrotica (o mesmo conjunto): DURAVIS · ELTIRA ·
FORZA · LAMDEX EXTRA · NINJA.
Só ligados à cultura: 38. NÃO SEI: 0 — porque estes cartões têm alvo.

### O caso `MAIS × PIRALIDE × FRIULI-VENEZIA GIULIA`

Existe: `OPP_9C600748BB1B`, ancorado em `IT-PHEN-048`.
**Cinco produtos autorizados no par. Um no ecrã** — Lamdex® Extra, o único que
casa com o catálogo comercial por número de registo. DURAVIS, ELTIRA, FORZA e
NINJA caem por não estarem no catálogo de 51 produtos, **não** por não servirem.

### Mapa factual

| região | cultura | janela | sinal de campo | sinal de concorrência | produto ADAMA | convergência | estado |
|---|---|---|---|---|---|---|---|
| Friuli-Venezia Giulia | MAIS | **NÃO SEI** (sem registo) | piralide, limiar declarado, 2026-08-12 | nenhum regional | 5 no par · 1 no ecrã | campo + portfólio | **AVALIAR AGORA** |
| Lombardia | MAIS | NÃO SEI | diabrotica — **proibição na floração** | nenhum regional | 5 no par · 1 no ecrã | campo diz NÃO | **JANELA ENCERRADA** (proibição declarada) |
| Emilia-Romagna | MAIS | NÃO SEI | ticchiolatura, sem guia | nenhum regional | 43 na cultura | só cultura | **SEM BASE SUFICIENTE** |
| Piemonte | MAIS | NÃO SEI | nenhum | 1 peça paga | 43 na cultura | nenhuma | **SEM BASE SUFICIENTE** |
| Itália (nacional) | MAIS | NÃO SEI | — | 70 peças, 2 ativas | 43 na cultura | nenhuma | **MONITORAR** |

**`MAIZE_REGIONS_WITH_COMPETITOR_AND_FIELD_CONVERGENCE` = 0.**
A concorrência é nacional em 69 das 70 peças; o campo é regional. As duas camadas
nunca se encontram na mesma geografia provável.

```
TOP_MAIZE_REGION_TO_WATCH_NOW = FRIULI-VENEZIA GIULIA
MOTIVO = é a única região onde um boletim oficial declara um LIMIAR de
         tratamento para piralide, e onde a direção do sinal é positiva.
PROVAS = IT-PHEN-048 (ERSA FVG, 2026-08-12) · OPP_9C600748BB1B ·
         5 produtos ADAMA com o par no rótulo ministerial
NÃO PROVA = incidência, área afetada, nem que o produtor vá tratar.
            E NÃO foi escolhida por volume de anúncio: o milho é a cultura
            mais anunciada do corpus e isso não entrou nesta decisão.
```

---

## 3 · O defeito que estreita o portfólio: o catálogo perdeu 92% das culturas

`CROPS_DECLARED_ON_SITE` não responde «que culturas a ficha do produto declara».
Responde «em que **página de cultura** encontrei este produto» — e só sete
páginas de cultura foram lidas.

| | |
|---|---:|
| pares produto × cultura no censo (`CROPS_DECLARED_ON_PAGE`) | **711** |
| pares produto × cultura no pacote (`CROPS_DECLARED_ON_SITE`) | **55** |
| **pares perdidos** | **656** |
| culturas distintas no censo | 149 |
| culturas distintas no pacote | **7** |

As sete sobreviventes: CEREALI · MAIS · POMACEE · POMODORO · RISO · SOIA · VITE.

O próprio `scripts/adama_catalogo_montar.py` já declara o limite, e com todas as
letras:

> `CULTURA_LEIA_ASSIM`: «chegamos a este produto por link de outra ficha, não por
> página de cultura. Não ter cultura aqui **NÃO significa** que ele não tenha.»

> **A DECLARAÇÃO ESTAVA CERTA. O CONSUMIDOR A JUSANTE É QUE NÃO A LEU.**
> `PORTFOLIO_MATCHES` transforma ausência-no-catálogo em exclusão-no-ecrã, e a
> ausência é do nosso rastreio, não do catálogo.

---

## 4 · O corte de doze, que ninguém declara

`scripts/v21_oportunidades.py:574`

```python
'PRODUCT_RELATIONSHIPS': produtos[:12],
```

Sem aviso, sem contador, sem campo que diga quantos ficaram de fora.

- **19 dos 43 cartões** perdem produtos aqui.
- **184 produtos** caem no total.
- O pior: `OPP_2BDE8FC566CE` (beterraba) — 23 autorizados, **1** no cartão.

O mesmo ficheiro faz o mesmo com as fontes na linha 844: `SOURCE_URLS[:12]`.

---

## 5 · A terceira redução, no ecrã

`PORTFOLIO_MATCHES` só deixa passar produtos com
`VALIDATION_STATE = LABEL_AND_CATALOG` — rótulo **e** catálogo. Dos 280 produtos
que o pacote leva, **65 chegam ao ecrã**; **215 caem aqui**.

Esse cruzamento é defensável como regra comercial — o que não é defensável é ele
correr contra o catálogo mutilado do §3, e sem dizer quantos excluiu.

---

## 6 · O vazamento inverso: produtos a mais, na cultura errada

O arquétipo O5 dá cultura ao cartão com
`crops[0] if len(crops) == 1 else None` (linha 777), mas lista **todos** os
produtos que contêm a substância que expira — sem filtrar por cultura.

| cartão | cultura do cartão | produto listado | onde está autorizado |
|---|---|---|---|
| `OPP_6E18A133EE14` | POMODORO | VINETO | videira |
| `OPP_88CC35C57C7B` | SOIA | POSTSCRIPT 80 · 80 XL | milho, arroz, girassol |
| `OPP_AA1A1FF77C8D` | **VITE** | STAVENTO | frumento |
| `OPP_AA1A1FF77C8D` | **VITE** | SOLOFOL AP | sem cultura declarada |
| `OPP_E6200AA0FA63` | ORZO | ANTARKTIS | sem cultura declarada |

**4 cartões, 6 produtos.** É o erro de agregar-e-afirmar: verdadeiro do conjunto
de uma substância, afirmado do membro de uma cultura.

---

## 7 · A completude de cruzamento — 26 famílias contra 43 cartões

`43_OPPORTUNITIES_FULL_ACERVO_SCAN = SIM` (pela medição desta missão).
`TOTAL_CROSSINGS_FOUND = 122` matches fortes (cultura **e** alvo/região).

| família | MATCH | só cultura | não encontrado | material não utilizável |
|---|---:|---:|---:|---:|
| PESO_ECONOMICO_HISTORICO | 39 | — | 4 | — |
| CATALOGO_ADAMA_CENSO | 41 | — | 2 | — |
| PRODUTO_ADAMA_ROTULO | 18 | 24 | 1 | — |
| SINAL_DE_CAMPO | 17 | 22 | 4 | — |
| CLIMA | 2 | 22 | 19 | — |
| EVENTOS | 2 | 21 | 20 | — |
| JANELA_DE_CULTURA | 2 | 17 | 24 | — |
| RESISTENCIA | 1 | 11 | 31 | — |
| CONCORRENCIA | — | 36 | 7 | — |
| MERCADO | — | 36 | 7 | — |
| REGISTRO_ROTULO | — | 38 | 5 | — |
| VOZES_PUBLICAS | — | 37 | 6 | — |
| PORTFOLIO_COMERCIAL | — | 33 | 10 | — |
| NOTICIAS | — | 26 | 17 | — |
| PESQUISADORES | — | 25 | 18 | — |
| CANAIS_CREATORS | — | 22 | 21 | — |
| CIENCIA | — | 19 | 24 | — |
| EVENTOS_FUTUROS | — | 16 | 27 | — |
| SINAL_FUTURO | — | 6 | 37 | — |
| REGULATORIO · REGULATORIO_FUTURO | — | — | 43 | — |
| SUBSTANCIA_ATIVA · RELACOES · CRUZAMENTOS_CLIENT_SAFE | — | — | 43 | — |
| **VIDEOS** | — | — | 5 | **38** |
| **TRANSCRICOES** | — | — | — | **43** |

```
OPPORTUNITIES_WITH_VIDEO_MATCH            = 5   (par cultura × alvo no corpus)
OPPORTUNITIES_WITH_TECHNICIAN_MATCH       = 25  (pesquisadores, por tema)
OPPORTUNITIES_WITH_SCIENCE_MATCH          = 19  (só cultura; 0 no par com alvo)
OPPORTUNITIES_WITH_COMPETITOR_MATCH       = 36  (só cultura)
OPPORTUNITIES_WITH_MULTISOURCE_CONVERGENCE = 18 (≥ 3 famílias com match forte)
```

### O terceiro estado, que não é zero

**`MATERIAL_EXISTENTE_NAO_UTILIZAVEL`** — existe, e não serve:

- **1.115 vídeos** em `data/samples/SENSOR-PILOT/`, nunca ingeridos no pacote.
  E o par cultura×alvo deles vem do **termo de busca**, não do conteúdo:
  `CROP_ISSUE_BASIS = "declarado pela consulta, não lido do título"`.
- **48 transcrições pedidas, 1 com texto.** As outras 47 são `REQUESTED_EMPTY` —
  um estado, não uma ausência.
- **3.737 comentários** e **102 canais**, no mesmo corpus, no mesmo estado.

> **CONTAR ISTO COMO ZERO MENTE SOBRE O ACERVO.**
> **CONTAR COMO MATCH MENTE SOBRE A EVIDÊNCIA.**

### As famílias que o motor nem carrega

O motor carrega **14** coleções. Existem no pacote e **nunca são lidas**:

`AGROMET-CONDITIONS` (clima) · `EVENTS` · `FUTURE-EVENTS` · `FUTURE-SIGNALS` ·
`NEWS` · `PUBLIC-CHANNELS` (creators) · `REGULATORY-FUTURE` · `RESEARCHERS` ·
`RELATIONSHIPS` · `CLIENT-SAFE-CROSSINGS` · `SOURCES`

E uma que é carregada e **deitada fora**: `PUBLIC-VOICES` entra em `main()`
(linha 383) e nunca é indexada nem passada a arquétipo nenhum. Consequência
direta: a regra de red team da linha 372 — *«voz isolada tratada como
incidência»* — **nunca pode disparar**, porque nenhuma voz chega à evidência.

Fora do pacote, e nunca ingeridos: o corpus de vídeo/transcrição/comentário e o
censo do catálogo ADAMA.

---

## 8 · O que este relatório NÃO prova

- Não prova que algum dos produtos omitidos **deva** aparecer no cartão. Prova
  que ninguém contou quantos eram e ninguém declarou porquê ficaram fora.
- Não prova incidência, área afetada, nem intenção de compra em caso nenhum.
- Não prova que a lacuna do catálogo seja lacuna do catálogo: é lacuna do
  **nosso rastreio** do catálogo.
- Não prova nada sobre regime biológico ou bio-estimulante: **NÃO SEI**, o campo
  não existe no acervo.
- Não classifica os 71 produtos de VITE um a um contra o facto de cada cartão por
  leitura humana. Classifica-os pela **prova que existe**: o rótulo ministerial
  nomeia, ou não nomeia, o par cultura × alvo. Onde não há alvo, é NÃO SEI.
