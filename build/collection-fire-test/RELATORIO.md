# PROVA DE FOGO DA COLLECTION — SINTONIA EAME · 2026-09-14

> Uma execução real, contra fontes reais, com a máquina que existe hoje.
> Nada aqui foi escrito à mão: cada número tem um ficheiro de prova ao lado.

---

## 0 · O ESTADO MEDIDO ANTES DE TOCAR EM NADA

```
INITIAL_BRANCH   claude/gifted-shannon-8u9l78
INITIAL_HEAD     f437ff1140fa97484ca9695b341fbe9ca0a9f050
INITIAL_WORKTREE limpo — zero ficheiros modificados
REMOTE_STATE     origin/main = f437ff11 — a branch e o ramo padrao eram o MESMO commit
```

As quatro camadas ficam separadas de propósito:

| camada | o que foi medido |
|---|---|
| **GIT** | `f437ff11`, worktree limpo, idêntico a `origin/main` |
| **RUNTIME** | Linux, Python 3.11.15, Node 22.22.2, 4 núcleos, **sem GPU** |
| **DATABASE** | **NÃO MEDIDO** — não há credenciais Supabase neste ambiente |
| **LIVE** | **NÃO TOCADO** — tudo correu num *worktree* descartável (§34) |

Egress medido por `ipinfo.io`: **Columbus, Ohio, US — AS396982 Google LLC**.
Não é Itália. Isso não é detalhe: molda metade dos resultados.

### Baseline (antes) → depois

| contador | antes | depois | delta |
|---|---:|---:|---:|
| RUN (ledger italiano) | 6 | 7 | **+1** |
| RUN (RUN-MANIFEST) | 13 | 13 | 0 |
| RAW_OBSERVATION | 144 | 179 | **+35** |
| RAW_OBJECT declarado | 35 | 69 | **+34** |
| objetos em `collection-store` | 10 | 44 | **+34** |
| objetos em `IT-SOURCE-SAMPLES` | 49 | 151 | **+102** |
| decisões de admissão | 506 | 590 | **+84** |
| **linhas na SALA DE ESPERA** | **0** | **6** | **+6** |

Prova: `evidencia/CONTADORES-ANTES.json`, `evidencia/CONTADORES-DEPOIS.json`.

> **A Sala de Espera estava vazia.** Em 506 decisões anteriores, ZERO foram `SIM`.
> Esta missão é a primeira vez que material atravessa a porta.

---

## 1 · O QUE ESTAVA QUEBRADO ANTES DE COMEÇAR

A coleta italiana **não arrancava**. Sete módulos da cadeia importavam vizinhos
pelo caminho antigo, de antes da reorganização das gavetas:

```
coleta/italy_pilot_collect.mjs     ./italy_contracts.mjs   → vive em regras/
coleta/italy_recurrent_collect.mjs ./italy_profiles.mjs    → vive em candidatas/
candidatas/italy_write_matrix.mjs  ./italy_source_health.mjs → vive em regras/
provas/italy_pilot_negativos.mjs   ./italy_pilot_collect.mjs → vive em coleta/
regras/italy_pilot_guards.mjs      ./italy_pilot_collect.mjs → vive em coleta/
regras/italy_scheduling_guards.mjs ./italy_profiles.mjs    → vive em candidatas/
regras/italy_contract_test.mjs     ./italy_accounting.mjs  → vive em provas/
```

`ERR_MODULE_NOT_FOUND` em todos. Ou seja: **o coletor canónico de WEB e PDF, o
entrypoint agendado, os controles negativos e as guardas do piloto estavam
inarrancáveis desde o commit `2640c5e`** — e nenhum teste apanhava isso, porque
nenhum teste os importa.

Correção aplicada: apenas os caminhos relativos (11 linhas em 7 ficheiros).
Nenhuma lógica mudou.

---

## 2 · TRÊS DEFEITOS QUE FABRICAVAM OU PERDIAM VERDADE

### 2.1 · O preservador afirmava uma origem que nunca mediu

`guarda/italy_preserve.mjs` escrevia, **literal no código**, em TODO manifesto:

```
EGRESS_IP   "205.147.30.20"
EGRESS_GEO  "Milano, Lombardia, IT — AS208172 Proton AG"
EGRESS_KIND "VPN_COMERCIAL — nao e ISP residencial italiano"
```

Independentemente de onde a captura corresse. Isto não é imprecisão: é **prova
fabricada**, e contamina tudo o que confia nela. Se esta missão não tivesse
corrigido, os 40 manifestos preservados hoje jurariam ter saído de Milão.

Corrigido: mede o egress; sem medição, `NAO SEI`. Prova no manifesto de hoje:
`"EGRESS_GEO": "Columbus, Ohio, US — AS396982 Google LLC"`.

### 2.2 · A porta de admissão carimbava publicação como tempo do fato

`admissao/admissao.py::_tem_quando` devolvia **«tem tempo do fato»** para
qualquer item que trouxesse só `published_at` — contra a lei central do projeto
(`PUBLICATION_TIME != FACT_TIME`). Um boletim publicado a 10 pode descrever
armadilha lida a 2.

Corrigido: distingue as duas e diz qual encontrou. **Nenhuma decisão SIM/NAO
mudou** — mudou a verdade escrita ao lado dela.

### 2.3 · Um portão de dinheiro que estava escrito e nunca corria

`CONTRATOS.json` carrega, em cada ator, a lei
`MATCH VAZIO NÃO AUTORIZA GASTO. Fase paga não roda com APPROVED=NO`.
`fase_posts()` **nunca a leu**. Medido ao vivo: o portão REPROVOU YouTube e
LinkedIn, e as duas fases pagas correram logo a seguir, na mesma sessão, sem nada
as travar. Nada foi gasto porque não havia chave — a trava foi a falta de
dinheiro, não o portão.

```
REGRA ESCRITA NO ARTEFATO != REGRA EXECUTADA NO CAMINHO.
```

Corrigido: o portão corre ao vivo antes de qualquer execução paga. Provado:

```
CONTRATO REPROVADO · YOUTUBE — nenhuma execução paga foi disparada.
  o build 0.0.301 do ator `streamers~youtube-scraper` NÃO aceita a entrada
  desta casa (VALOR_FORA_DO_ENUM dateFilter).
```

---

## 3 · OS NÚMEROS DA PROVA

```
ATTEMPTED   201
COLLECTED   109
REUSED        8
BLOCKED      76
ERROR         5
NOT_FOUND     3
UNKNOWN       0
```

Reconciliação (§44): `109 + 8 + 76 + 5 + 3 + 0 = 201` ✔ **fecha exatamente**.

```
RUNS_CREATED              2   (ambos no ledger italiano)
RAW_CREATED              34
STORAGE_OBJECTS_CREATED 136   (34 no collection-store + 102 em IT-SOURCE-SAMPLES)
DERIVED_CREATED          84
STRUCTURED_CREATED       84
ADMITTED                  6
REJECTED                  4   (NAO — olhei e não serve para este universo)
NAO_SEI                  40
NAO_SE_APLICA            34
WAITING_ROOM_DELTA        6
```

**`ADMITTED = 6 = WAITING_ROOM_DELTA`** ✔

### Por tipo

| TIPO | tentado | colhido | reuso | bloqueado | erro | não achado | raw | structured | admitido | sala de espera |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| WEB | 36 | 26 | 2 | 3 | 2 | 3 | 31 | 26 | 2 | **2** |
| PDF | 38 | 32 | 6 | 0 | 0 | 0 | 38 | 32 | 4 | **4** |
| SCIENCE | 46 | 29 | 0 | 17 | 0 | 0 | 5 | 5 | 0 | 0 |
| VIDEO | 27 | 3 | 0 | 24 | 0 | 0 | 3 | 0 | 0 | 0 |
| YOUTUBE | 15 | 8 | 0 | 7 | 0 | 0 | 0 | 0 | 0 | 0 |
| FACEBOOK | 10 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 |
| COMPETITOR | 8 | 3 | 0 | 4 | 1 | 0 | 7 | 3 | 0 | 0 |
| LINKEDIN | 6 | 0 | 0 | 6 | 0 | 0 | 0 | 0 | 0 | 0 |
| MARKET | 6 | 4 | 0 | 0 | 2 | 0 | 4 | 4 | 0 | 0 |
| REELS | 5 | 0 | 0 | 5 | 0 | 0 | 0 | 0 | 0 | 0 |
| PRESS_EVENT | 4 | 4 | 0 | 0 | 0 | 0 | 4 | 4 | 0 | 0 |
| **TOTAL** | **201** | **109** | **8** | **76** | **5** | **3** | **92** | **74** | **6** | **6** |

Linha a linha em `ITEM-TRACE.csv` (201 linhas, 31 colunas).

---

## 4 · CAMINHO REAL PERCORRIDO NO SINTONIA

### Visão geral — só o que foi OBSERVADO nesta execução

```
                    ┌─ WEB ........... PROVEN   26 colhidos, 2 na Sala de Espera
                    ├─ PDF ........... PROVEN   32 colhidos, 4 na Sala de Espera
                    ├─ YOUTUBE ....... PARTIAL  canal e objetos SIM; legenda BLOCKED
                    ├─ INSTAGRAM ..... BLOCKED  contrato OK, credencial ausente
SOURCE / REQUEST ───┼─ REELS ......... BLOCKED  idem
                    ├─ LINKEDIN ...... BROKEN   contrato do ator reprovado
                    ├─ FACEBOOK ...... BLOCKED  contrato OK, credencial ausente
                    └─ SCIENCE ....... PARTIAL  ORCID SIM; OpenAlex deixou de ser grátis
                         ↓
                    ORCHESTRATOR ..... PROVEN   (só para os 4 executores registados)
                         ↓
                     COLLECTOR ....... PROVEN   (WEB/PDF) · BLOCKED (social/vídeo)
                         ↓
                        RUN .......... PROVEN   (só no piloto italiano e no orquestrador)
                         ↓
                 RAW OBSERVATION ..... PROVEN   34 criados, SHA256 antes do parse
                         ↓
                     STORAGE .......... PROVEN   136 objetos, bytes conferidos
                         ↓
                      DERIVED ......... PROVEN   84 textos, cada um aponta o seu RAW
                         ↓
                    STRUCTURED ........ PROVEN   84 registos — mas SEM CONTRATO (§6.4)
                         ↓
                     ADMISSION ........ PROVEN   84 decisões, 5 estados distintos
                         ↓
                  SALA DE ESPERA ...... PROVEN   6 linhas · era 0
```

Etapas **UNKNOWN** (não medidas nesta missão): a Sala de Espera em **banco**
(Supabase) — sem credenciais, nada foi tocado.

### EXEMPLO 1 — PDF · caminho completo, IDs reais

```
1  FONTE      IT-T3-002 · Regione Campania — Servizio Fitosanitario Regionale
2  ÍNDICE     https://agricoltura.regione.campania.it/.../SA_2026.html   HTTP 200
3  ITEM       .../bollettini_2026/pdf/SA-09-09.pdf
4  COLETOR    coleta/italy_pilot_collect.mjs
5  RUN_ID     PILOT_RUN_20260914141155_5a1a3b
6  BYTES      validados ANTES do parse — assinatura %PDF confere com o contrato
7  RAW        DOCUMENT_ID     CAMPANIA:SA:09-09-2026
              RAW_OBSERVATION v1_d5aa781c258d
              SHA256          d5aa781c258dc0016960861d3ab1737ca3fd5d260699e52d1794565ace33d085
8  STORAGE    data/collection-store/italy/IT-T3-002/CAMPANIA_SA_09-09-2026/v1_d5aa781c258d/SA-09-09.pdf
9  DERIVED    DER-f7c1963931019e36   (pdftotext -layout · 31.930 caracteres)
10 STRUCTURED STR-d027269632a5f97a
11 ADMISSION  SIM · regra «pertence ao universo» v1 · universo T3
12 SALA       FIRE-TEST-ADMISSAO-2026-09-14-T3 #3
   PUBLICATION_TIME 2026-09-09
   FACT_TIME        NAO SEI — o boletim não data a observação de campo
```

### EXEMPLO 2 — WEB/CSV · caminho completo

```
IT-T4-001 · Ministero della Salute — banca dati prodotti fitosanitari
 → PROD_FTS_6_20260914.csv
 → RUN PILOT_RUN_20260914141155_5a1a3b
 → DOCUMENT_ID MINSALUTE:FTS6:20260914 · RAW v1_d8f20c7383d1
 → SHA256 d8f20c7383d15372a69622b1aa91d627b363f0540f96a260dcdc7895d5430f30
 → data/collection-store/italy/IT-T4-001/MINSALUTE_FTS6_20260914/v1_d8f20c7383d1/PROD_FTS_6_20260914.csv
 → DER-c085b334691363ec → STR-0319ea739ad66f0f
 → ADMISSION SIM (T4) → SALA FIRE-TEST-ADMISSAO-2026-09-14-T4 #2
```

### EXEMPLO 3 — VÍDEO TRANSCRITO · até onde chegou

```
 1 URL        https://coldiretti-video.s3.eu-central-1.amazonaws.com/CAI/consorziagrari.mp4
 2 DONO       IT-T7-003 · Consorzi Agrari d'Italia (o vídeo está embebido na homepage dele)
 3 COLETOR    guarda/italy_preserve.mjs
 4 RUN        NOT_APPLICABLE — este coletor não escreve RUN  ◀ lacuna medida
 5 RAW        HTTP 200 · 8.584.254 bytes · video/mp4
              SHA256 80eb0dbb7f250a030b0b9e81b22768d18f73415fbb5829d858132a09cab3b20d
 6 STORAGE    data/samples/IT-SOURCE-SAMPLES/IT-T7-003-VIDEO-CAI/consorziagrari.mp4
 7 LEGENDA    AUSENTE — ffprobe listou 2 faixas (h264 + aac) e NENHUMA de legenda.
              Ausência PROVADA no contentor, não presumida.
 8 ÁUDIO      extraído por ffmpeg · 16 kHz mono · 275,1 s
 9 TRANSCRIÇÃO faster-whisper small · int8 · CPU · 58 segmentos · 4.289 caracteres
              sha256 do texto: bb84b71f17c3a396cdc6cf9e…
10 IDIOMA     it — DETECTADO (p=0,970), nunca assumido pelo país da fonte
11 TRADUÇÃO   EN, 55 segmentos, em campo SEPARADO, apontando
              SOURCE_TEXT_REFERENCE = TRANSCRIPT_ORIGINAL@sha256:bb84b71f…
              O original NUNCA foi sobrescrito.
12 STRUCTURED NOT_RUN   ◀ a transcrição de vídeo não está ligada à porta
13 ADMISSION  NOT_RUN
14 SALA       NOT_REACHED
```

Prova: `evidencia/VIDEO-TRANSCRICAO-E-TRADUCAO.json`.
Primeira frase real transcrita: *«Consorzi Agrari d'Italia, lab strategico
dell'agricoltura italiana.»*

### EXEMPLO 4 — INSTAGRAM/REEL · onde parou

```
Conta  bayer_italia (IDENTITY PROVED · LOCAL_COUNTRY_PROVED · lote congelado)
  ↓
coleta/comunicacao_coleta.py posts INSTAGRAM
  ↓
PORTÃO DE CONTRATO  apify~instagram-scraper build 0.0.781 → APROVADO
  ↓
POOL DE CREDENCIAIS  APIFY_TOKEN_POOL = vazio
  ↓
POOL_STATE = POOL_EMPTY · ACCOUNTS_DONE 0 · ACCOUNTS_PENDING 5
APIFY_RUNS 0 · COST_USD 0
  ↓
RUN         NOT_CREATED
RAW         NOT_CREATED
ADMISSION   NOT_RUN
SALA        NOT_REACHED
```

O artefato diz, textualmente: *«este zero fala da nossa credencial, nunca da
empresa observada»*. **Não virou «a Bayer não publica».**

### EXEMPLO 5 — LINKEDIN · onde parou

```
6 contas OFICIAIS PROVADAS (Bayer IT, BASF ES/IT, Nufarm ES/IT/FR)
  ↓
Nenhuma é LOCAL_COUNTRY_PROVED → o lote congelado não as admite
  ↓ "ausência de conta provada LOCAL — não é ausência de comunicação"
E, em paralelo, o portão de contrato REPROVA o ator:
   harvestapi~linkedin-post-search build 0.0.111
   · `companyUrls` não existe no schema
   · `maxItems`   não existe no schema
   · `postedLimit='30d'` fora do enum ['any','1h','24h','week','month',…]
  ↓
RUN NOT_CREATED · RAW NOT_CREATED · SALA NOT_REACHED
```

Dois bloqueios independentes, ambos registados. Nenhum vira rejeição.

### EXEMPLO 6 — BLOQUEADO · YouTube legenda

```
24 vídeos de 8 canais provados
  ↓ coleta/youtube_janela.py legendas
porta barata (urllib)  → HTTP 429 deste IP de datacenter
porta do navegador     → Chromium 141 encontrado, mas
                         "Running as root without --no-sandbox is not supported"
  ↓
CAPTION_STATE = PORTA_NAO_ABRIU   (24/24)
CAPTION_STATE = AUSENTE           (0/24)   ◀ a distinção que importa
  ↓
RAW NOT_CREATED · ADMISSION NOT_RUN · SALA NOT_REACHED
```

E a terceira porta, `yt-dlp`: *«Sign in to confirm you're not a bot»*.
Três portas independentes fechadas — e o sistema **nunca** escreveu «sem legenda».

### EXEMPLO 7 — ERRO e REJEIÇÃO, que são coisas diferentes

```
ERRO (a máquina não conseguiu olhar)
  IT-T2-004 · SIAS Sicília
   → HTTP 503, 114 bytes
   → OBSERVATION_RESULT TRANSPORT_OR_EMPTY · HEALTH_STATE FAILED · retries 1
   → RAW NOT_CREATED, e a fonte NÃO leva a culpa da ferramenta

  IT-T10-001 · ISMEA Mercati  →  falha de verificação TLS (com CA do sistema E do proxy)
  IT-T10-003 · COEWEB ISTAT   →  idem
  IT-T7-010  · Melinda        →  connection reset by peer
  IT-T9-006  · FMC Agro       →  CONNECT tunnel failed 502

REJEIÇÃO (a máquina olhou e disse não)
  4 itens · resultado NAO
  motivo: «não encontrei nada de "T3" neste item. Isto é um NAO para ESTE
           universo — o mesmo item pode ser SIM noutro.»

BLOQUEIO (a porta da plataforma fechou)
  IT-T9-002 Bayer · IT-T9-003 Syngenta · IT-T9-005 Nufarm · IT-T9-008 ADAMA → HTTP 403
  (o próprio `italy_probe.mjs` classifica 403-para-curl como INCONCLUSIVO,
   exigindo reteste em navegador — que não existe neste ambiente)

NÃO TENTADO (não há rota declarada)
  IT-T3-003 · IT-T3-010 · IT-T7-012 → a ficha da fonte diz URL = "NÃO SEI"
```

---

## 5 · REUSO, RETRY E CRASH

**REUSO** — o piloto correu **duas vezes** contra as mesmas fontes, com minutos
de intervalo:

```
SOURCES_ATTEMPTED 5 · SEEN_AGAIN 8 · NEW_DOCUMENTS 0 · RAW_OBJECTS_CREATED 0
```

8 de 8 reconhecidos. Zero RAW duplicado. Zero fingimento de coleta nova.

**RETRY** — a política só repete falha de **transporte**:
`TRANSITORIOS = [28, 35, 52, 56, 7]`. Medido: ligação recusada → curl sai com 7,
que está na lista → repetição permitida. E o inverso, medido na corrida real:
SIAS devolveu **HTTP 503** — falha do servidor, não do transporte — e o coletor
registou `retries: 1`, **sem repetição cega**.

**CRASH** — controle negativo N5: o parser rebenta depois do download e o RAW
continua intacto. A ordem do coletor é `download → bytes → sha → RAW → manifesto
→ parse`, e só por isso a falha do intérprete não destrói a prova.

---

## 6 · RED TEAM

### 6.1 · Bateria desta missão — 14 ataques, 14 resistidos

| # | ataque | resultado |
|---|---|---|
| RT1 | URL morta (domínio inexistente) | falha de rede registada, **nenhum RAW** |
| RT2 | HTTP 200 que é página de erro | status e bytes REAIS (404/82 KB), `NOT_PRESERVED` |
| RT3 | redirect | `URL_EFETIVA` (`https://fmach.it/`) guardada ao lado da pedida |
| RT4 | ficheiro `.pdf` cujos bytes são HTML | `ALERTA: A EXTENSAO MENTE` + `NOT_PRESERVED` |
| RT5 | item que a ferramenta não conseguiu ler | `ERRO`, nunca `NAO` |
| RT6 | item sem tempo nenhum | `NAO_SEI`, nunca `NAO` |
| RT7 | só data de publicação | entra, mas o tempo do fato fica `NAO SEI` |
| RT8 | mesmo item em dois universos | T7=SIM, T4=NAO — decisões independentes |
| RT9 | inventar o resultado `TALVEZ` | `ValueError` — enum fechado |
| RT10 | falha de storage (ENOTDIR, vale para root) | erro propaga, não é engolido |
| RT11 | falha de transporte real | código 7, dentro de `TRANSITORIOS` |
| RT12 | HTTP 503 real | `FAILED` com status real, `retries=1` |
| RT13 | bytes idênticos em duas fontes | 3 grupos; `SOURCE_ID` continua distinto |
| RT14 | YouTube inalcançável | `PORTA_NAO_ABRIU`, **nunca** `AUSENTE` |

### 6.2 · Controles negativos canónicos — 7 de 8

`provas/italy_pilot_negativos.mjs`: N1–N5, N7, N8 atingiram o ramo esperado.

**N6 falhou no laboratório e passa no repositório principal.** Causa provada: N6
lê a ÚLTIMA observação real do SIAS, e o SIAS devolveu HTTP 503 durante esta
missão. **Não é regressão de código — é o estado real da fonte.** Isso revela,
porém, uma fragilidade do controle: *um teste cujo veredito depende de um site de
terceiros estar no ar não é um controle negativo, é um sensor.*

---

## 7 · O QUE ESTA PROVA ENCONTROU DE ESTRUTURAL

### 7.1 · O executor social do SCRAP está registado e não é entregável

`.github/workflows/scrap-social.yml` **está em `origin/main`**. Os três coletores
que ele invoca **não estão**:

```
coleta/social_scrap.py      AUSENTE em main   (existe em ~37 ramos de funcionalidade)
guarda/social_guarda.py     AUSENTE em main   (idem)
coleta/youtube_oficial.py   AUSENTE em main   (idem)
```

O próprio workflow tem um passo que confere a presença desses ficheiros — logo
**ele falha na sua própria verificação prévia**. E despacha para o runner
`["self-hosted","Windows","X64","eame-sintonia-local"]`, a máquina que tem a GPU.

```
FICHEIRO REGISTADO != CAPACIDADE ENTREGUE.
```

Este workflow também estava **invisível ao System Map** (violação `P9`
pré-existente). Foi declarado nesta missão como `C-SCRAP-SOCIAL`.

### 7.2 · Duas taxonomias de território incompatíveis

`pedido/pedido.py` e o atlas de fontes discordam sobre o significado de **cinco**
códigos:

| código | atlas (`canonical_territories`) | `pedido/pedido.py` |
|---|---|---|
| T5 | SCIENCE | Preço e mercado |
| T7 | TECHNICAL NETWORK | Ciência e ensaio |
| T10 | MARKET / TRADE / INDUSTRY | Política e subsídio |
| T11 | EVENTS | Solo e água |
| T12 | POLICY | Substância ativa |

Consequência medida ao vivo: pedir **«colete ciência da Itália»** devolve as **12
fontes de rede técnica** (cooperativas e consórcios), chamando-lhes «Ciencia e
ensaio», e manda o coletor científico (`corpus_pesquisador.py`, OpenAlex/ORCID)
correr sobre elas. **As 5 fontes científicas reais ficam invisíveis ao pedido.**

```
ONE CONCEPT → ONE OWNER — violado, em silêncio.
```

### 7.3 · 25 RAW que o ledger jura existir e não estão no repositório

De 69 observações com `RAW_OBJECT_CREATED = true`, **25 apontam para
`C:/eame-sintonia-ops/...`** — caminho absoluto de Windows, da máquina do
operador. Esses objetos nunca entraram no Git. A tentativa de derivar texto
deles falhou nas 25, com `RAW declarado mas ausente nesta árvore`.

O `italy_recurrent_collect.mjs` declara a lei
`LOCAL_COMMIT != REMOTE_DURABILITY` no próprio cabeçalho. Está violada na prática.

### 7.4 · Não existe contrato do registo STRUCTURED

Procurado no repositório inteiro: **nenhum esquema, nenhuma validação**. A porta
lê chaves por tentativa e erro:

```python
item.get("texto") or item.get("title") or item.get("nome")
item.get("source_id") or item.get("fonte") or item.get("url")
item.get("captured_at", "NAO SEI")
```

Prova do dano, nesta própria execução: o registo que construí traz
`collected_time`, e a porta lê `captured_at`. Resultado — as 6 linhas da Sala de
Espera saíram com **`CAPTURED_AT: NAO SEI`** apesar de o valor existir e estar
medido. Um campo presente perdeu-se em silêncio porque nada obriga o nome.

### 7.5 · O OpenAlex deixou de ser a rota gratuita que os coletores declaram

Três coletores declaram no cabeçalho «rota REST gratuita, sem chave». Medido hoje,
17 vezes:

```json
{"error":"Rate limit exceeded",
 "message":"Insufficient budget. This request costs $0.001 but you only have $0 remaining."}
```

Não é reputação de IP. É **modelo de negócio novo da plataforma**. ORCID (HTTP 200)
e Crossref (HTTP 200) continuam abertos.

### 7.6 · A transcrição por GPU não está versionada

Os dois donos canónicos fixam CPU **no código**:

```python
ferramentas/youtube_transcrever.py:191   WhisperModel(modelo, device='cpu', compute_type='int8', …)
ferramentas/instagram_transcrever.py:247 WhisperModel(modelo, device='cpu', compute_type='int8', …)
```

Não há nenhuma referência a CUDA/GPU em todo o repositório. A operação usa a placa
de vídeo de `eame-sintonia-local`, e essa configuração vive **fora do Git**.
Quem clonar o repo transcreve em CPU e não saberá porquê.

---

## 8 · REGRESSÃO

```
Suite completa, 28 testes, no INITIAL_HEAD e depois das correções:

PRE_EXISTING_FAILURE  6   test_coleta_externa · test_comunicacao · test_evidence
                          test_handoff · test_portao · test_proveniencia
NEW_FAILURE           0
CURADAS               0
```

Prova: `BASELINE-TESTS.txt` (medido em `f437ff11`, antes de tocar em nada).

### O teste de contrato italiano passou de «não corre» para «corre e acusa 5»

`regras/italy_contract_test.mjs` não arrancava no `INITIAL_HEAD`
(`ERR_MODULE_NOT_FOUND` em `./italy_accounting.mjs`). Com os imports corrigidos:

```
349 passaram · 5 falharam
```

As 5 falhas são todas da mesma espécie — exigem prova de que um controle negativo
foi **realmente executado**, lendo o log de operação em
`C:/eame-sintonia-ops/data/collection-ledger/italy/logs/runs.log`:

```
FALHA  existe controle negativo REAL de VPN nao italiana      — 0 execucoes
FALHA  existe controle negativo REAL de push quebrado         — 0 execucoes
FALHA  existe controle negativo REAL de trava ocupada         — 0 execucoes
FALHA  existe execucao que PULOU por estar fora da janela de Roma
FALHA  houve execucao com 0 novos que ainda assim registrou observacoes
```

Esse log vive na máquina do operador e não está no Git — a mesma raiz do achado
7.3. Não são defeitos de código: são **provas em falta**. E não são `NEW_FAILURE`:
antes desta missão o ficheiro nem chegava a correr.

### System Map

```
cadeia canónica completa, como o CI a corre:
  scan_repo              SCAN=OK · HEAD=f437ff11 · arquivos=1143 · arestas=1539
  scan_sources           GREEN=16 · NAO SEI=5 · YELLOW=2
  scan_casco             OK
  censo_da_coleta        OK
  pente_fino_da_coleta   OK
  generate_system_map    MAPA=OK · peças=98 (🟢64 🟡30 🔴0 ⚪4) · ligações=330

  validate               SYSTEM_MAP_CHECK=PASS
  tests                  TESTES_SYSTEM_MAP=PASS
```

**No `INITIAL_HEAD` o portão do System Map já estava REPROVADO**, com `P1_SEM_DRIFT`
e `P9_CODIGO_DECLARADO` a falhar (o órfão era `scrap-social.yml`). Esta missão
deixa-o a **PASSAR**.

*Achado de método:* correr só `generate_system_map.py` não converge — o CI corre
**cinco scanners antes**. Sem eles o mapa fica meio regenerado e o `P1` nunca fecha.

### Sobre o `--stamp`: recusado de propósito

Quatro peças caíram para 🟡 porque esta missão editou os ficheiros delas
(`C-ADMISSAO`, `C-COLETA-PUBLICA`, `C-IT-CONTAS`, `C-REGRA-COLETA`). Reli as quatro
descrições e todas continuam verdadeiras. Mas `--stamp` carimba **435 ficheiros de
uma vez** como «lidos por gente» — e chegou a promover `C-SCRAP-SOCIAL` a 🟢, o que
seria falso: os coletores dele não existem em `main`.

```
Recarimbar sem reler é o único jeito de mentir neste sistema. — AGENTS.md
```

O carimbo foi **revertido**. As quatro peças ficam 🟡, que é a verdade: alguém deve
reler e recarimbar uma a uma.

*Nota de ficheiros servidos:* o gerador, correndo em Linux, reescreve
`italia-portale/client/system-map/{index.html,map.js,map.css}` trocando CRLF por LF
— 19.331 linhas de diferença que são **só fim-de-linha**, reproduzível no HEAD
limpo, e que o `.gitattributes` (`italia-portale/client/** -text`) existe para
evitar. Esses três foram restaurados. O `state.generated.json` servido tem mudança
real de conteúdo e vai no commit (+375/−162).

*Nota medida:* o gerador precisa de **duas passagens** para convergir quando uma
peça nova é declarada, porque ele também regenera
`regras/LEIA-ANTES-DE-COLETAR.md`, que entra no próprio hash. E, correndo em
Linux, reescreve `italia-portale/client/system-map/*` trocando CRLF por LF — uma
alteração de 19.331 linhas que é **só fim-de-linha** e que `.gitattributes`
existe precisamente para evitar. Esses ficheiros foram restaurados; a alteração
é pré-existente e reproduz-se no HEAD limpo.

---

## 9 · O QUE NÃO FOI FEITO, DE PROPÓSITO

- **Nenhum Intelligence.** A missão termina na Sala de Espera (§26).
- **Nenhuma segunda Collection.** Nenhum coletor novo, nenhum banco paralelo.
- **Nenhum SOURCE_ID nem DOCUMENT_ID fabricado.** As 3 fontes sem URL ficaram
  `NOT_ATTEMPTED_NO_ROUTE`; a imprensa técnica (Terra e Vita, AgroNotizie) não
  foi coletada porque não existe na base qualificada.
- **Nenhum ficheiro trazido de outro ramo.** Os coletores do SCRAP social existem
  noutros ramos e **não** foram puxados (AGENTS.md avisa que isso apaga trabalho
  em silêncio).
- **Nenhuma escrita em produção.** Tudo num *worktree* descartável.

---

## 10 · EM PALAVRAS SIMPLES, PARA QUEM NÃO PROGRAMA

**Tentámos ir buscar 201 coisas.**

- **109** conseguimos trazer.
- **8** já tínhamos, e a máquina reconheceu isso em vez de fingir que eram novas.
- **76** estavam trancadas.
- **5** deram erro de ligação.
- **3** nem tentámos, porque a ficha da fonte não diz onde é que ela mora.

Guardámos **34 documentos originais novos**, com a impressão digital de cada um.
Tratámos **84** desses documentos, transformando-os em texto. Organizámos os
**84** em fichas. A porta de entrada olhou para todas e disse **sim a 6**. E essas
**6 chegaram mesmo à Sala de Espera** — que estava vazia antes desta missão.

### Um exemplo, passo a passo

1. O serviço fitossanitário da Campânia publica um boletim por província.
2. O coletor abriu a página do índice e encontrou o PDF de Salerno, de 9 de setembro.
3. Nasceu a corrida **PILOT_RUN_20260914141155_5a1a3b**.
4. Antes de abrir o ficheiro, a máquina conferiu que os bytes eram mesmo um PDF —
   e só depois o guardou, com a impressão digital `d5aa781c…`.
5. O original ficou em `data/collection-store/italy/IT-T3-002/CAMPANIA_SA_09-09-2026/`.
6. Só então o texto foi extraído: 31.930 letras.
7. Os dados foram organizados numa ficha.
8. A porta perguntou «isto fala de praga e doença?» e encontrou as palavras. Disse sim.
9. Entrou na Sala de Espera como o item **#3** do ficheiro `…-T3`.

E — isto é o mais importante — a máquina escreveu ao lado: **«não sei quando o
fato aconteceu»**. O boletim tem data de publicação, mas não diz em que dia a
armadilha foi lida no campo. Ela não inventou.

### E o vídeo?

1. Encontrámos um vídeo real no site dos Consorzi Agrari d'Italia.
2. Guardámos o ficheiro inteiro, 8,5 MB, com impressão digital.
   Conferimos contra a impressão digital do próprio servidor: **bate exatamente**.
3. Perguntámos ao ficheiro se tinha legenda. **Não tinha** — e isso ficou provado,
   não suposto.
4. Tirámos o áudio e transcrevemos: 4 minutos e 35 segundos, 58 trechos.
5. A máquina **descobriu sozinha** que era italiano, com 97% de confiança.
   Não assumiu «é uma fonte italiana, logo é italiano».
6. Traduzimos para inglês num campo **separado**, que aponta para o original.
   O original nunca foi apagado.
7. **E aqui o caminho parou.** A transcrição não está ligada à porta de entrada.
   O vídeo foi colhido e tratado, mas não chegou à Sala de Espera.

### E as redes sociais?

- **Instagram e Facebook**: a máquina verificou que sabe falar com a ferramenta
  certa, confirmou as 15 contas oficiais, e parou porque **não há chave de acesso
  neste ambiente**. Escreveu «0 contas olhadas, 15 pendentes, 0 dólares gastos».
  Não escreveu «estas empresas não publicam nada».
- **LinkedIn**: parou por dois motivos. Nenhuma das 6 contas oficiais é da
  subsidiária local, e a ferramenta externa mudou de formato — os campos que
  mandamos já não existem lá.
- **YouTube**: conseguimos ler os 8 canais e 240 vídeos (título, duração, data).
  Mas as legendas **não**: as três portas possíveis estão fechadas para um
  computador de centro de dados.

---

## 11 · FECHAMENTO

**1 · O que fizemos?** Pusemos a Collection inteira sob pressão com 201 tentativas
reais contra fontes reais italianas, em oito formatos diferentes, e seguimos cada
uma até onde ela chegou.

**2 · O que funcionou?** O caminho de sites e PDFs funciona de ponta a ponta:
pedido → coletor → corrida → original guardado → texto → ficha → porta → Sala de
Espera. O reconhecimento de material repetido funciona. A separação entre erro,
bloqueio e rejeição funciona. O vídeo foi transcrito, com idioma detectado e
tradução separada do original.

**3 · O que quebrou?** A cadeia italiana estava **inarrancável** (imports
partidos). O preservador **fabricava** a origem geográfica. A porta de admissão
**carimbava publicação como tempo do fato**. O portão que impede gasto com
ferramenta errada **estava escrito e nunca corria**. O executor social do SCRAP
**está registado no ramo padrão sem os coletores que ele chama**. Cinco códigos de
território **significam coisas diferentes** em dois sítios do mesmo sistema.

**4 · Quantas coisas chegaram à Sala de Espera?** **6** — de 0. São 3 documentos
oficiais italianos em 2 edições cada: boletins fitossanitários da Campânia e da
Puglia, e a base de autorizações do Ministero della Salute.

**5 · Vídeo e redes sociais funcionaram?** Vídeo: **até meio**. Colhemos,
preservamos, transcrevemos, detectámos idioma e traduzimos — mas não chega à Sala
de Espera, porque não existe ligação entre a transcrição e a porta. Redes sociais:
**não**, e por três razões distintas e bem registadas — falta de credencial
(Instagram, Facebook), contrato do ator desatualizado (LinkedIn, YouTube pago) e
bloqueio de plataforma a IP de centro de dados (legendas do YouTube).

**6 · Onde a máquina ainda é fraca?**
- Só dois componentes escrevem recibo de corrida. Metade da coleta corre sem RUN.
- Não existe contrato do registo `STRUCTURED` — campos perdem-se por nome.
- A porta de admissão só tem régua escrita para 4 universos (T3, T4, T7, T9).
  Nesta missão, **34 itens** saíram `NAO_SE_APLICA` por falta de régua para T2.
- 25 RAW existem só na máquina do operador.
- A identidade de documento é escrita à mão, fonte a fonte: escalar exige código novo.

**7 · O que continua desconhecido?**
- A Sala de Espera **em banco** (Supabase) — sem credenciais, nada foi medido.
- O comportamento a partir de **IP italiano** — quatro 403 e o bloqueio do YouTube
  são inconclusivos de um IP de centro de dados.
- O que a rota paga da Apify entrega de facto — nenhuma execução foi disparada.
- A transcrição por **GPU** — não existe no Git; não pôde ser observada.

**8 · Qual risco ficou?** O maior é o `scrap-social.yml`: um botão despachável no
ramo padrão que chama três ficheiros ausentes. Quem o disparar recebe uma falha e
pode lê-la como «as redes não entregam». O segundo é a colisão de territórios:
uma coleta de ciência pedida hoje corre sobre cooperativas, e **ninguém é avisado**.

**9 · KNOW_HOW_DELTA?**

```
KNOW_HOW_DELTA = ATUALIZAÇÃO NECESSÁRIA
```

Seis aprendizados duráveis, cada um com O QUÊ → POR QUÊ → PROVA → CONSEQUÊNCIA,
registados na secção 7 deste relatório:

1. OpenAlex deixou de ser rota gratuita (`$0 remaining`).
2. YouTube fecha as três portas a IP de centro de dados (urllib 429, navegador
   sem sandbox, yt-dlp bot check) — confirma o que o próprio `scrap-social.yml`
   já media em 2026-09-08.
3. Os atores Apify de LinkedIn e YouTube mudaram de schema; a entrada desta casa
   já não é aceite.
4. `scrap-social.yml` está em `main` sem os seus coletores.
5. Cinco códigos de território colidem entre `pedido/` e o atlas.
6. A rota de GPU da transcrição não está versionada.

**10 · Bíblia/contrato precisa mudar?** Sim, em dois pontos:
- é preciso um **contrato do registo STRUCTURED** (hoje não existe nenhum);
- é preciso decidir **um dono** para a taxonomia de territórios.

**11 · Qual é o próximo passo mínimo?** Declarar `larga_em` para o YouTube e para
a transcrição de vídeo em `pedido/receitas.py`. É a alteração mais pequena que
converte «colhido e tratado» em «chegou à Sala de Espera» para vídeo — e usa o
caminho canónico que já existe, sem construir nada novo.

---

## 12 · VEREDITO

```
VEREDITO = PARTIAL
```

**A Collection leva sites e PDFs de ponta a ponta até à Sala de Espera, preserva
os originais com impressão digital, reconhece repetição e nunca inventou um dado
para passar — mas vídeo, Instagram, LinkedIn, Facebook e YouTube ficam pelo
caminho, cada um por um motivo diferente e corretamente registado.**

O que sustenta o PARTIAL e não o FAIL: **201 tentativas, reconciliação exata, 14
de 14 ataques resistidos, zero falhas novas de regressão, e nenhum zero disfarçado
de facto.** Em todos os 76 bloqueios, a máquina escreveu «não consegui olhar» — e
nunca «olhei e não há».

O que impede o PASS: a Sala de Espera recebeu **6 de 201**, e nenhum item de
vídeo ou de rede social chegou lá. A máquina é honesta em toda a extensão que
percorre; a extensão é que ainda é curta.

```
HARD STOP
```
