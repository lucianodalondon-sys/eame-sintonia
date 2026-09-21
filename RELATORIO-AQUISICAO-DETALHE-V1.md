# RELATÓRIO — AQUISIÇÃO REAL: LISTING → DETALHE (AQUISICAO-DETALHE-V1)

**Base:** `source-curator-integration-v1` @ `907ccd70` · **Bancada:** worktree `aquisicao-detalhe-v1`
**Corrido em:** 2026-09-20/21 · **HARD GATE:** `BIG_COLLECTION_ALLOWED = NO` (respeitado) · `PAID_USD = 0`

---

## 1 · RELATÓRIO MEDIDO

### 1.1 · A secção 0 da missão, reconfirmada

Todos os números da coordenação bateram com os meus, linha a linha (`links[0]` = 0 · MAX_TARGETS
na linha 356 · canário 18/185/18 · 126/105/104 · 49/55 · 27/27 · 5/6). Nenhum divergiu.

**Terceira causa, não prevista:** o motor devolve os `href` pela ordem do HTML e fica com o
primeiro que casa com `LINK_PATTERN` (`regras/motor_de_rota.mjs::ligacoesDoIndice`). Em 30 das
104 fontes o padrão é «qualquer caminho com 3+ palavras», sem palavra de notícia — e o primeiro
link do HTML é o menu. Medido no que a BCR colheu de facto (1 item por fonte):

```text
BCR_ALVO_MATERIA          30   uma matéria ou edição real
BCR_ALVO_LISTAGEM          9   a própria listagem, guardada como conteúdo   ← CAPA ≠ MATÉRIA
BCR_ALVO_INSTITUCIONAL    32   chi siamo, contatti, PEC, consiglio, sede
BCR_ALVO_PAPELADA_PDF     33   estatuto, tarifário, privacidade, brochura
```

### 1.2 · PASSO 1 — classificação (commit `d75c3263`, mapa `cacbb509`)

`curadoria/classificar_indice_104.py` → `CLASSIFICACAO-INDICE-104-V1.{json,md}`. Universo calculado
do estado actual; juízo por fonte com critério de vocabulário fechado; o script reprova se faltar ou
sobrar um juízo (a coordenação mutou-o e ele reprovou com exit 2).

```text
BOLETIM_SERIADO         8   (5 HAND do núcleo + ARSAC, ARPA Sicilia, Emilia-Romagna)
LISTAGEM_DE_NOTICIAS   52   (24 com listagem vista · 28 com itens vistos, listagem A_PROVAR)
NAO_SEI                44   (33 = todo o LOTE-PDF-INDICE: capa + pasta de uploads + papelada;
                            11 HTML só com páginas institucionais; 2 contratos duplicados)
```

### 1.3 · PASSO 2 — correção só da família de notícias (commit `83385fe7`, mapa `60bc3641`)

**Prova de rota primeiro** (`curadoria/provar_listagens.mjs` → `PROVA-DE-LISTAGENS-V1.json`):
52 GET, um por listagem proposta, teto 2 por domínio, controlo positivo à frente, **pela mesma
identidade com que a Collection bate à porta** (medido: Agronotizie devolve 403 ao UA
`SintoniaScrap` e 200 ao UA de navegador — provar com outra identidade prova outra coisa).
Egresso IT (Milão, Proton). Resultado: 35 listagens com 200 e mais de um link; 17 não.

**Correção** (`curadoria/aplicar_passo2.py` → `CONTRATOS-PASSO-2-V1.json`, cinco portões por fonte,
zero diff conferido linha a linha fora das corrigidas):

```text
CONTRACTS_FIXED                     21   INDEX_URL / LINK_PATTERN / MAX_TARGETS
CONTRACTS_DELIBERATELY_UNTOUCHED    83   8 BOLETIM_SERIADO · 44 NAO_SEI · 31 LISTAGEM não provada
MAX_TARGETS = min(N medido na 1ª página, TETO=30)     calculado; TETO é escolha com razão escrita
  distribuição: 30×5 · 20×2 · 15×2 · 13×2 · 11×3 · 10×2 · 14 · 7 · 6 · 4 · 2
```

As 31 LISTAGEM não tocadas, por motivo: 7 sem `robots.txt` legível pelo portão da casa (não é
recusa) · 4 com rota inferida 404 · 1×403 · 1×500 · 7 com 200 mas zero itens no HTML servido
(**Agronotizie incluída**: 61 KB, 5 categorias, 0 artigos — JavaScript ou outro caminho) · 5 hubs
de sub-secções · 6 onde a sonda só guardou 5 amostras e eram menu (limitação da sonda, já
corrigida: guarda agora todos os `href`). 4 destas (Umbria, Villoresi, Lazio, Umbria-agricoltura)
caem para `NAO_SEI` pela regra do PASSO 1 (listagem alcançada sem itens).

**BUG DE PADRÃO, dito pelo nome:** em `IT-T12-013` (Regione Piemonte) a palavra `bollettin` do
padrão genérico casava com `/governo/bollettino/` e a Collection colhia o **Bollettino Ufficiale**
por acidente. Não era escolha de família: era o padrão. O padrão novo só aceita
`/web/temi/agricoltura/<secção>/<slug>` e o não-item declarado é exactamente o Bollettino.

A divergência da fotografia do curator (`italy_contracts_curator.json`, 9 fontes) fica **declarada**
no registo, com o ANTES igual à fotografia; `tests/test_integracao_04a_curator.py` passa a exigir o
registo em vez de silêncio.

### 1.4 · PASSO 3 — canário contra a realidade

Uma corrida pela porta canónica da Collection (`coleta/italy_pilot_collect.mjs`),
`RUN_ID = CANARIO-AQD-P3-20260921T011226Z-4f654777`, 10 fontes, egresso IT, `PAID_USD = 0`.

| SOURCE_ID | classe | corrigida | visíveis 1ª pág. | antes (docs) | depois (obs) | novos | seen | changed | derivação (HTML_KIND) | data explícita |
|---|---|---|---|---|---|---|---|---|---|---|
| IT-T1-021 Agronotizie | LISTAGEM (não provada) | NÃO | — | 1 | 1 | 0 | 1 | 0 | a listagem outra vez (CAPA_PROVAVEL no retrato) | 0/1 |
| IT-T1-022 OlivoNews | LISTAGEM | SIM (13) | 13 | 1 | 12 | 12 | 0 | 0 | CONTENT 12/12 | 12/12 |
| IT-T3-010 APOL | BOLETIM (controlo −) | NÃO | — | 2 | **1** | 0 | 1 | 0 | PDF | — |
| IT-T2-001 ARPAE | BOLETIM (controlo −) | NÃO | — | 1 | **1** | 0 | 1 | 0 | PDF | — |
| IT-T3-005 Terre dell'Etruria | STATIC (fora das 104) | NÃO | — | 1 | 1 | 1 | 0 | 0 | CONTENT | 0/1 |
| IT-T2-006 ARPAC | LISTAGEM | SIM (20) | 20 | 1 | 20 | 19 | 0 | 1 | CONTENT 19 · NAV 1 | 0/20 |
| IT-T9-009 Cifo | LISTAGEM | SIM (15) | 15 | 1 | 15 | 14 | 0 | 1 | CONTENT 13 · NAV 2 | 15/15 |
| IT-T7-042 Balsamico | LISTAGEM | SIM (10) | 10 | 1 | 10 | 9 | 0 | 1 | CONTENT 10 | 10/10 |
| IT-T12-013 Piemonte | LISTAGEM | SIM (30) | 31* | 1 | 15 | 15 | 0 | 0 | NAV 12 · CONTENT 3 | 2/15 (+12 só `og:updated_time`) |
| IT-T10-018 Myfruit | LISTAGEM | SIM (30) | 37* | 1 | 29 | 29 | 0 | 0 | CONTENT 25 · MIXED 4 | 29/29 |

\* contagem de 1ª página que inclui secções que o padrão novo exclui de propósito.

```text
SOURCES_CANARIED             10
LISTINGS_FOUND               10 / 10   (HEALTHY 10, FAILED 0)
DETAIL_LINKS_DISCOVERED     105        (101 nas 6 listagens corrigidas)
DETAIL_ITEMS_SELECTED       105        (nenhuma fonte bateu no MAX_TARGETS abaixo do que enumerou)
DETAIL_ITEMS_COLLECTED      105        (RAW_OBJECTS_CREATED 105: 99 NEW + 3 CHANGED_IN_PLACE + 3 SEEN_AGAIN)
CONTROLO_NEGATIVO_MANTEVE_1  YES       (APOL 1, ARPAE 1 — SEEN_AGAIN; a correção não vazou)
RAW_CORRECT_PAGE             matéria em 82/101 (CONTENT), navegação em 15 (12 são páginas de secção
                             da Regione Piemonte com corpo de ~2.700 caracteres), mista em 4.
                             Agronotizie: continua a trazer a CAPA — contraprova cumprida: a correção
                             às cegas NÃO foi feita porque o HTML servido não anuncia artigos.
DERIVED_HAS_BODY             101/101 TEXT_LAYER_PRESENT pelo executor da casa (offline)
RECALL_CANARIO_ANTES         6 / 126   (6 listagens corrigidas: 1 documento cada na BCR)
RECALL_CANARIO_DEPOIS        101 / 126 (os 25 em falta são secções/menu que o padrão exclui)
```

**Contraprova exigida pela missão (Agronotizie):** o canário terminou de novo na página índice
(`SEEN_AGAIN` da listagem). É o comportamento esperado de um contrato **não corrigido**, e é por
isso que o gate CAPA ≠ MATÉRIA (1.7) existe: com o coletor de agora essa observação sai `DEGRADED`
com `CAPA_NAO_E_MATERIA`, não `HEALTHY`. O `PASSO 2` não a corrigiu porque a listagem servida em
HTML não tem artigos: corrigir a rota sem itens visíveis seria supor.

**Uma segunda contraprova, não pedida:** o canário canónico do curator (`canario_do_motor.mjs`)
dá `AUTH · HTTP 403` em Agronotizie porque usa a identidade `SintoniaScrap`, enquanto a Collection
entra com 200. **Canário com identidade diferente da coleta mede outra porta.** Fica como dívida do
Source Curator (decisão de política: identidade honesta vs. identidade da coleta).

### 1.5 · PASSO 4 — incrementalidade

**Medido primeiro.** `SEEN_AGAIN` existe e funciona: as 3 refetches byte-idênticas do canário não
viraram conteúdo novo. O que faltava tem dois nomes:

1. **Dedup antes do fetch** (COL-LAW-021): o coletor não manda `If-None-Match`/`If-Modified-Since`.
   Medido com 3 HEAD: nenhuma das fontes amostradas (Cifo, OlivoNews, Balsamico) envia `ETag` nem
   `Last-Modified` (Balsamico responde 403 a HEAD). Implementar condicional aqui não pouparia nada
   — **não construído**, e dito porquê.
2. **Versão-fantasma por markup**: 2 dos 3 `DOCUMENT_CHANGED_IN_PLACE` do canário (ARPAC, Balsamico)
   tinham o **mesmo texto visível** (sha do texto igual) com bytes diferentes. Uma «mudança real»
   que não era. Construído o mínimo: `coleta/retrato_html.mjs` dá ao coletor `TEXT_SHA256`
   (identidade de conteúdo ao lado da de bytes) e `CONTENT_CHANGE ∈ MARKUP_ONLY · TEXT_CHANGED ·
   UNKNOWN`, com contador `MARKUP_ONLY_REOBSERVATIONS` por corrida. O RAW novo continua a ser
   guardado (RAW BEFORE PARSE); só deixa de contar como conteúdo útil novo. Vocabulário do
   `OBSERVATION_RESULT` intocado. RUN ≠ OBSERVATION ≠ CONTENT ≠ STORAGE OBJECT continua de pé.

```text
WASTEFUL_REOBSERVATION_BEFORE   5 / 105 fetches   (3 SEEN_AGAIN + 2 CHANGED_IN_PLACE só de markup),
                                                   medidos no canário com o coletor como estava
WASTEFUL_REOBSERVATION_AFTER    5 / 105 fetches — os mesmos, agora contados POR NOME
                                (MARKUP_ONLY_REOBSERVATIONS); provado sem rede em
                                tests/test_capa_nao_e_materia.py (3 corridas: BASELINE → MARKUP_ONLY
                                → TEXT_CHANGED). NÃO re-medido em rede: o fetch não desceu porque
                                as fontes não dão cabeçalho condicional.
```

### 1.6 · PASSO 5 — YouTube

Reconfirmado no acervo (`%USERPROFILE%\sintonia-sala-italia\acervo-coletor-bcr`):

```text
YT_RAW_FILES = 612 · 714,6 MB · média 1.196 KB · 41 fontes · transcrições = 0
(coordenação: 612 / 714,6 MB — igual; o dono dizia 737 / 715 MB)
```

Capability de transcrição: `coleta/executor_transcricao_midia.py` (ficha: `ffmpeg + faster-whisper`,
dono do ASR `ferramentas/fala_local.py`) e `coleta/adaptador_youtube.py` **existem**. Nesta máquina:
`yt-dlp` e `ffmpeg` no PATH; `faster_whisper` e `whisper` **não instalados**. O próprio adaptador
regista que o `robots.txt` do YouTube barra os caminhos por onde o `yt-dlp` passa
(`ROBOTS_STATUS = RESTRICTED`, não é parecer jurídico). **Nenhum canário de vídeo foi corrido.**

```text
YOUTUBE_TRANSCRIPTION_CAPABILITY = EXISTS_UNPROVEN
YOUTUBE_WATCH_HTML_AS_CONTENT    = YES  (hoje: 612 páginas guardadas como documento; derivação dá
                                   «sem texto nenhum»). Fica dito pelo nome: YouTube está READY
                                   para descoberta/metadata e NÃO para tratar watch HTML como
                                   conteúdo final. Não mudei os contratos YouTube nesta missão.
```

### 1.7 · PASSO 6 e PASSO 7 — PUBLISHED_AT e o gate CAPA ≠ MATÉRIA

**PUBLISHED_AT.** Medido nas 87 páginas de artigo do canário: 66 declaram a data de publicação
(`article:published_time` em 12+15+10+29; `<time datetime>` em 2 da Piemonte; ARPAC 0/20).
`coleta/executor_texto_de_html.py` passa a devolver nas medidas `PUBLISHED_AT` e
`PUBLISHED_AT_BASIS` — só o que a página **declara**; `og:updated_time` fica de fora (é «actualizado»);
prosa nunca vira data. **`FACT_TIME` não foi tocado, não tem fallback, e o executor não o conhece**
(`tests/test_published_at_do_html.py`, 8 provas, com os casos negativos).

```text
PUBLISHED_AT_PRESERVED   = YES nas medidas da derivação (66/87 no canário); a observação RAW
                           continua sem ela (é a etapa certa: RAW ≠ DERIVADO)
FACT_TIME_CONTAMINATED   = NO
```

**Gate CAPA ≠ MATÉRIA.** `coleta/retrato_html.mjs::gateCapaNaoEMateria`: um contrato que declara
itens de detalhe (`HTML_LINK_DISCOVERY` + `OUTPUT_TYPE HTML`) não guarda uma capa como conteúdo
final. A observação sai `DEGRADED` com `CAPA_NAO_E_MATERIA` pelo nome; o RAW fica. Casos que o
fazem falhar: `tests/test_capa_nao_e_materia.py` (10 provas: listagem sintética → `CAPA_PROVAVEL`
→ gate reprova; artigo passa; rota fixa e PDF não são julgados). Contraprova real, offline: a
listagem de Agronotizie do canário → `CAPA_PROVAVEL`, gate reprova; o artigo de OlivoNews → `MATERIA_PROVAVEL`.
Limiar partilhado com `_kind` do executor Python; divergência conhecida: o retrato Node conta só
`<p>` como parágrafo, o Python conta mais blocos — a mesma página pode sair `CONTENT` num e
`NAVIGATION` no outro (aconteceu com a listagem de Agronotizie). Dívida registada.

### 1.8 · PASSO 8 — o gate de READY do Source Curator

`curadoria/canario_do_motor.mjs` (o canário que o worker do curator corre) passa, para contratos
`HTML_LINK_DISCOVERY`, a **abrir um item real**: bytes com a assinatura declarada e, se HTML, retrato
sem capa. Devolve `DETAIL_ENUMERATED` e `ITEM_ABERTO`; `PASS` só com item aberto e sem gate.
Nada é guardado (VALIDAR ≠ COLETAR). Provado ao vivo: `IT-T9-009` PASS (15 alvos, item
`MATERIA_PROVAVEL`); `IT-T1-021` FAIL (`AUTH 403` na identidade do canário — ver 1.4). O dono do
READY continua a ser o Curator (lifecycle 19/19, interface 7/7, integração 29/29).

### 1.9 · Baseline externo

```text
RECALL_VS_BASELINE_EXTERNO = NOT_COMPARABLE
```
Porquê: o baseline (17 fontes, 326/2/324, snapshot 2026-09-20T23:16Z) é da versão anterior da
Collection, só 1ª página, com fontes parcialmente NOT_MEASURED e sem lista de SOURCE_ID que eu
consiga cruzar com as 10 do canário. Conjunto, janela e definição de item não são compatíveis.
Nenhuma percentagem foi fabricada. O canário tem a sua própria medição antes/depois (1.4).
`PRIMARY_LOSS_STAGE`: ENUMERATION naquela fotografia, SELECTION nesta — o defeito evoluiu; a
causa histórica não sobrescreve a actual, e `links[0]` continua em 0 ocorrências.

### 1.10 · Gates, provas e regressão

```text
NEW_FAILURES                 = 0 por nome, contra a base 907ccd70 medida nesta máquina:
  system-map/tests/test_system_map.py    base 7 FAIL · agora 6–7 (os mesmos nomes; scanner_e_deterministico é instável)
  regras/italy_contract_test.mjs         346 ok / 94 FALHA nos dois; nomes idênticos (uma mensagem
                                          traz o nº de RAW da «segunda rodada», que o canário mudou de 15 para 105)
  medidas/padrao_da_coleta.py            idêntico (5 FAIL herdados, 2 ok)
  tests/test_integracao_04a_curator.py   base 1 FAIL (código em curadoria/) · agora o mesmo 1
  tests/test_alvo_estruturado_resolvido  base FAIL test_13 (CONTENT_TYPE não declarado) · agora PASS,
                                          com os campos novos DECLARADOS por nome
  novos: test_capa_nao_e_materia 10/10 · test_published_at_do_html 8/8 · executor HTML 14/14 ·
         curator 29/29 · lifecycle 19/19 · interface 7/7 · motor 45/45 · cutover 50/50
SYSTEM_MAP_CHECK             = PASS (ver commit do mapa desta entrega) · carimbo IGUAL
KNOW_HOW_DELTA               = §164 em SINTONIA-EAME-KNOW-HOW.md
REDE USADA                   = 49 GET + 3 HEAD (PASSO 2) · 115 GET (canário) · 4 GET (canário do motor) · ipinfo
RAW DO CANÁRIO               = 105 ficheiros, 15,1 MB, movidos para o acervo
                               (data/collection-ledger/italy/pastas-movidas-2026-09-21-aquisicao-detalhe.json)
```

### 1.11 · Dívidas registadas (não são missão nova)

- 44 `NAO_SEI` (33 PDF-INDICE, 11 HTML): recuração pelo Source Curator — o que a fonte publica como fluxo.
- 3 boletins da tabela com rota/padrão errados (ARSAC, ARPA Sicilia, Emilia-Romagna): rota da edição em vez do arquivo; arquivo inteiro guardado como documento.
- 31 listagens não provadas (motivos em `CONTRATOS-PASSO-2-V1.json`); 7 delas por `robots.txt` ilegível no portão da casa — re-tentar; 6 por limitação da sonda, já corrigida.
- Agronotizie: listagem sem artigos no HTML servido — precisa de rota/instrumento (JS?) medido, não suposto.
- Rivista di Agraria: listagem presa ao ano 2026 (o padrão já aceita qualquer ano).
- Canário do curator com identidade diferente da coleta (`SintoniaScrap` vs navegador).
- Retrato Node vs `_kind` Python: contagem de parágrafo diverge.
- Regione Piemonte: 12 de 15 itens colhidos são páginas de secção com muita navegação — o padrão aceita `<secção>/<slug>`; a família «notícia» ali é por provar.
- YouTube: watch HTML como conteúdo final continua; transcrição EXISTS_UNPROVEN.
- `test_nenhum_ficheiro_de_codigo_em_curadoria` reprova desde 333174d5 (o motor do curator vive em `curadoria/`); esta missão pôs lá mais 3 scripts — a lei e a pasta discordam, e alguém tem de decidir.

---

## 2 · BLOCO DE ENTREGA

```text
SOURCES_CLASSIFIED            = 104
  BOLETIM_SERIADO             = 8
  LISTAGEM_DE_NOTICIAS        = 52
  NAO_SEI                     = 44

CONTRACTS_FIXED               = 21
CONTRACTS_DELIBERATELY_UNTOUCHED = 83  (8 boletim · 44 NAO_SEI · 31 listagem não provada)

SOURCES_CANARIED              = 10
LISTINGS_FOUND                = 10
DETAIL_LINKS_DISCOVERED       = 105
DETAIL_ITEMS_SELECTED         = 105
DETAIL_ITEMS_COLLECTED        = 105  (99 novos · 3 mudados no sítio · 3 revistos)
CONTROLO_NEGATIVO_MANTEVE_1   = YES

WASTEFUL_REOBSERVATION_BEFORE = 5 / 105 fetches
WASTEFUL_REOBSERVATION_AFTER  = 5 / 105 fetches, agora contados por nome (MARKUP_ONLY); fetch não desceu — fontes sem ETag/Last-Modified

YOUTUBE_WATCH_HTML_AS_CONTENT = YES  (612 · 714,6 MB · 0 transcrições; declarado: não é conteúdo final)
YOUTUBE_TRANSCRIPTION_CAPABILITY = EXISTS_UNPROVEN

PUBLISHED_AT_PRESERVED        = YES (medidas da derivação; 66/87 páginas do canário)
FACT_TIME_CONTAMINATED        = NO

RECALL_VS_BASELINE_EXTERNO    = NOT_COMPARABLE (conjunto, janela e definição de item incompatíveis)
RECALL_CANARIO_ANTES          = 6 / 126
RECALL_CANARIO_DEPOIS         = 101 / 126

DETAIL_COLLECTION_PROVEN      = YES (6 fontes, 99 matérias novas, 101/101 com texto derivado)
NEW_FAILURES                  = 0 (por nome, contra 907ccd70)
SYSTEM_MAP_CHECK              = PASS
KNOW_HOW_DELTA                = §164
BIG_COLLECTION_ALLOWED        = NO
PAID_USD                      = 0
```

---

## 3 · EM LINGUAGEM SIMPLES

Imagine uma banca de jornais. Antes, o Sintonia ia à porta da loja, apanhava o primeiro papel que
via na entrada e voltava. Quase sempre era o cartaz da loja, não um jornal.

1. **Antes colhíamos capa ou matéria?** Nas 104 fontes olhadas, só em 30 era uma matéria de
   verdade. Em 32 era uma página do tipo «quem somos», em 9 era a própria estante guardada como se
   fosse um jornal, e em 33 era um papel administrativo em PDF.
2. **Que fontes foram corrigidas, e quais deliberadamente não?** Corrigi 21 estantes de notícias
   onde provei, abrindo a página, que a estante existe e tem mais do que um jornal. Não mexi nos
   8 boletins semanais, porque neles trazer só o último é o certo. Não mexi nas 44 onde não sei o que
   a fonte publica. E não mexi em 31 estantes que não consegui provar, cada uma com o motivo escrito.
3. **Quantas matérias reais o Sintonia passou a encontrar?** No teste com 6 estantes corrigidas,
   antes trazia 6 documentos, 1 por estante. Agora trouxe 101, e 99 eram novos. Os dois boletins de
   controlo continuaram a trazer 1 cada, como devem.
4. **O mesmo conteúdo deixou de ser buscado repetidamente?** Em parte. Quando a página volta igual
   byte a byte, já não conta como novo, e isso já funcionava. Descobri que 2 páginas voltaram com o
   mesmo texto e bytes diferentes, e o sistema chamava-lhes «mudança». Agora tem nome: mudança só de
   embrulho, não de conteúdo. Mas a ida à fonte não diminuiu, porque estes sites não dão o sinal
   que permitiria perguntar «mudou?» sem descarregar. Isso ainda não foi medido depois, portanto não sei.
5. **O YouTube continua a guardar HTML inútil?** Sim. São 612 páginas, 714,6 MB, e nenhuma
   transcrição. A ferramenta de transcrever existe no repositório, mas nesta máquina falta o motor
   de reconhecimento de fala e o próprio YouTube barra o caminho de descarregar áudio. Não a testei.
6. **A data de publicação passou a sobreviver?** Sim, quando a página a declara. Em 66 das 87
   matérias do teste ela estava escrita e agora é guardada com o nome certo. E a «data do facto»
   continua vazia quando não se sabe, como a lei manda.
7. **A Collection já merece nova rodada pequena de prova?** Sim, nas 21 fontes corrigidas, e só
   nelas. Antes de qualquer rodada grande, faltam: re-tentar as 7 estantes que o porteiro de robots
   não conseguiu ler, decidir a identidade com que o canário bate à porta, e resolver a Agronotizie,
   cuja estante não mostra jornais sem JavaScript.

Isto ainda não foi medido, portanto não sei: se a correção aguenta quando as fontes publicam
coisa nova amanhã (a segunda corrida nas 21 é a prova que falta).
