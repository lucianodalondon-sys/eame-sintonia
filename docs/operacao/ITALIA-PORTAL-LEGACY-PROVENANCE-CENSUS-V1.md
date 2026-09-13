# CENSO DE PROVENIÊNCIA DAS CAMADAS LEGADAS DO PORTAL ITALIANO · V1

> Missão `C-ITALIA-PORTAL-LEGACY-PROVENANCE-RECONCILIATION-V1`
> Escopo: **somente Itália.** Espanha e França não foram auditadas.
> Natureza: **auditoria.** Nada foi coletado, nada foi escrito em LIVE, o portal
> não foi alterado, a Sala real não foi tocada.

A pergunta não é «o que o portal mostra». É **«o que por trás do que o portal
mostra ainda tem original recuperável»**. As duas respostas divergem, e a
segunda não se lê num JSON do portal: lê-se andando para trás, do leitor até o
escritor, e do escritor até o que ele leu.

> **O PORTAL É CONSUMIDOR. O FICHEIRO QUE ELE CARREGA NÃO É RAW.**

Inventário medido, máquina-legível:
[`data/derivados/ITALIA-PORTAL-LEGACY-PROVENANCE-CENSUS-V1.json`](../../data/derivados/ITALIA-PORTAL-LEGACY-PROVENANCE-CENSUS-V1.json)

---

## PRIMEIRO, EM PORTUGUÊS FÁCIL

**1 · Quantas camadas antigas alimentam o portal italiano?**
**20.** São 19 ficheiros `.js` sob `italia-portale/client/` que põem um dado no ar
(`window.ALGUMA_COISA = …`), mais 1 ficheiro `.json` irmão. Destes, **18 são
mesmo carregados** por alguma página; **1 é construído e nunca carregado**
(`italy-v21.js`, 10,3 MB, nenhum `<script src>` o cita); e 1 é o JSON que só o
gerador e as auditorias leem.

**2 · Quantos têm original encontrado?**
**Nenhuma camada do portal é um original** — todas são derivadas ou apresentação.
Descendo até os originais que a cadeia nomeia: dos **339 objetos legados
referenciados**, **10 têm os bytes aqui** e conferem byte a byte contra o SHA-256
registado. Os outros **329 não estão neste ambiente**.

**3 · Quantos podemos reaproveitar sem recoletar?**
**10 objetos** — e destes, **6 são os mais fortes que existem**: o `DOCUMENT_ID`
deles foi **re-derivado dos próprios bytes**, sem rede, e deu exatamente igual ao
que o ledger canônico já dizia (6 conferem, 0 divergem). Os outros 4 precisam de
`pdftotext`, que não existe aqui.

**4 · Quantos precisam de recoleta?**
**304** — os 163 rótulos PDF do Ministero della Salute e os 141 documentos do
catálogo público ADAMA Itália. A boa notícia: **a recoleta seria verificável**,
porque de cada um já se conhece a URL, o SHA-256 e a data de captura. Não é
recomeçar do zero; é voltar à fonte com o gabarito na mão.

**5 · Quantos continuam UNKNOWN?**
**27** — 2 camadas do portal cujo escritor e montante ninguém prova
(`italy-real-intelligence.js`, `italy-catalog.js`) e 25 objetos raw cujo
`RAW_PATH` aponta para `C:/eame-sintonia-ops/…`, uma máquina de operação que não
é este repositório.

**6 · O que já existe no Supabase Storage?**
**NÃO SEI — e isto não é evasiva, é o resultado da medição.** Não há
`SUPABASE_URL` nem `SUPABASE_SECRET_KEY` neste ambiente (medido: as seis
variáveis estão ausentes). O baseline que a missão cita — «195 objetos, ~80,7 MB
em `IT/adama-website/`» — **não aparece em lado nenhum deste repositório** e não
foi confirmado nem desmentido aqui.

> ⚠️ **Armadilha medida.** O acervo italiano versionado em `data/samples/` tem
> **196 ficheiros e 79,4 MB** — quase igual a «195 e 80,7 MB». **São coisas
> diferentes.** Um é Git, o outro é um bucket. Somar ou casar os dois por causa
> da coincidência seria inventar correspondência.

**7 · O que já está na Collection canônica?**
A Collection italiana existe e é séria: **6 corridas, 144 observações, 35 objetos
raw distintos, 7 fontes com contrato**. Mas **no Supabase não há RAW italiano
nenhum**: os dois ficheiros de importação da Itália escrevem **0 `collection_run`
e 0 `raw_asset`** — só tabelas estruturadas. A Espanha, no mesmo diretório, tem
1 `collection_run` e 138 `raw_asset`. **A Itália entrou como STRUCTURED sem
nunca ter passado por RAW.**

**8 · Conseguimos fazer um canário completo até READY/Sala descartável?**
**Não. `LEGACY_CANARY = NOT_RUN`**, por três impedimentos medidos, não supostos:
não há servidor Postgres (só o cliente `psql`; `initdb` e `postgres` ausentes, e
o daemon do Docker não responde); não há credenciais Supabase; e **duas etapas do
caminho não têm dono nenhum no repositório** — `storage_object` e
`derived_artifact` não existem como tabela, módulo ou sequer menção (0 ocorrências
em 21 migrations e em todo o código).

**9 · Qual é o próximo passo mínimo para reconciliar o lote real?**
Nesta ordem, e só o primeiro é urgente:

1. **Consertar 9 imports quebrados** que tornam a coleta italiana inexecutável
   nesta linhagem — `coleta/italy_pilot_collect.mjs` importa
   `./italy_contracts.mjs`, que vive em `regras/`. Medido com `node`:
   `ERR_MODULE_NOT_FOUND`. Na linha funcional já está corrigido
   (`../regras/italy_contracts.mjs`); aqui não.
2. **Decidir o dono de `storage_object` e de `derived_artifact`** — sem eles não
   há caminho canônico até a Sala, e nenhum canário pode passar.
3. **Só então** levar os 10 originais que já conferem para uma corrida de
   reconciliação — nunca os 304 que precisam de recoleta, e nunca os JSON do
   portal.

---

## REGRA 0 · O ESTADO REAL, MEDIDO AGORA

```
CURRENT_BRANCH            claude/wizardly-wright-uoodqk
CURRENT_HEAD              f437ff1140fa97484ca9695b341fbe9ca0a9f050
WORKTREE_STATUS           limpo no arranque (git status --short vazio)

FUNCTIONAL_BRANCH         claude/raw-observation-identity-3jbwco
FUNCTIONAL_HEAD           84186dfaf6be8a52866efc4a440609985f7f4401  (2026-09-13 21:43)
                          HEAD **não** é ancestral do funcional
                          divergência medida: 9 commits aqui · 452 lá

KNOW_HOW_BRANCH           claude/sintonia-eame-know-how-v1
KNOW_HOW_HEAD             7b5e50cf807f728524007f92660d73a3d2e0de1f  (2026-09-13 22:47, §109)

PORTAL_BRANCHES_RELEVANTES
  claude/acervo-to-package-intelligence-v1   @ 5101073  gerador canônico do V2.1 (43 casos)
  sprint/publicacao-unica-5855cad            @ 5855cad  origem dos 4 handoffs BASE
  claude/human-agricultural-sensors-8fv0fw   @ 7501255  Human Sensors
  claude/retomada-coleta-video-convegni-vz50er @ 5703711 TOP3 Sensores
```

**O inventário de camadas do portal é idêntico nas duas linhas.** Entre `HEAD` e
o funcional só diferem `adama-relevance.js` e `italy-casa.js` (regerados) e o
System Map. O censo abaixo vale para ambas; onde diverge, está dito.

---

## O CARTÃO DO SYSTEM MAP

Localizado e medido — não lido da imagem.

```
id          C-PORTAL-DADOS
nome        Camadas de dado do portal
territorio  Z-SUPERFICIE      kind: surface      family: F-ENTREGA
status      PROVEN            ui_status: green
file_count  15                inbound: 4      outbound: 16
```

**O cartão não diz «ATENÇÃO / PENDÊNCIA».** Ele está `PROVEN` e `green`. A
descrição da missão não bate com o mapa medido, e o mapa medido vence.

Os 15 ficheiros que o cartão reclama **não são as 20 camadas deste censo**: o
cartão exclui de propósito 6 ficheiros grandes (`italy-app-model.js`,
`italy-v21.js`, `italy-casa.js`, `italy-i18n.js`, `italy-handoff-v21.js`,
`italy-ingested.js`) e inclui 2 geradores Python — um deles espanhol
(`superficie/es/proto_es.py`). Este censo partiu dos **entrypoints reais**
(`portale.html`, `casa.html`, `accesso.html`, `index.html`), não da lista do
cartão.

---

## FASE A · O QUE O PORTAL REALMENTE CONSOME

Ordem de carga **real**, lida de `portale.html` (21 `<script src>`, dos quais 3
são vendor/design-system e 1 é runtime sem dado):

| # | DATASET | GLOBAL | TIPO | GERADO? | GERADOR |
|--:|---|---|---|---|---|
| 1 | `italy-canonical-windows.js` | `ITALY_CANONICAL` | janelas de cultura | declarado | **montante ausente** |
| 2 | `italy-label-verdicts.js` | `ITALY_LABEL_VERDICTS` | rótulo | não | auditoria dos 163 rótulos |
| 3 | `italy-real-intelligence.js` | `ITALY_REAL` | ciência/pessoas | não | **UNKNOWN** |
| 4 | `italy-demo-data.js` | `ITALY_DEMO` | fixture sintético | não | PRNG semeado |
| 5 | `italy-briefs.js` | `ITALY_BRIEFS` | apresentação | não | código à mão |
| 6 | `italy-market-pulse.js` | `ITALY_MARKET` | vocabulário | não | **esvaziado de propósito** |
| 7 | `italy-science-business.js` | `ITALY_SCIENCE` | interpretação | não | código à mão |
| 8 | `italy-i18n.js` | `SINTONIA_I18N` | strings | não | código à mão |
| 9 | `italy-catalog.js` | `ITALY_CATALOG` | catálogo | declarado | **UNKNOWN** |
| 10 | `italy-ingested.js` | `ITALY_INGEST` | pacote normalizado | declarado | **montante ausente** |
| 11 | `italy-handoff-v21.js` | `ITALY_HANDOFF_V21` | pacote V2.1 | **sim** | `portoes/site_v21_ingest.py` |
| 12 | `italy-app-model.js` | `ITALY_APP_MODEL` | fronteira de ingestão | não | código à mão |
| 13 | `meeting-intelligence-snapshot.js` | `MEETING_INTELLIGENCE` | reunião | **sim** | `pacote/meeting_snapshot.py` |
| 14 | `meeting-labels.js` | `MEETING_LABELS` | dicionário IT/EN | não | código à mão |
| 15 | `adama-relevance.js` | `ADAMA_RELEVANCE` | veredito de lei | **sim** | `superficie/it_casa_dados.py` |
| 16 | `meeting-surface.js` | `MEETING_SURFACE` | apresentação | não | código à mão |
| 17 | `italy-casa.js` | `ITALY_CASA` | casa/reunião | **sim** | `superficie/it_casa_dados.py` |
| 18 | `italy-pdf.js` | `ITALY_PDF` | documento | não | código à mão |
| 19 | `italy-v21.js` | `ITALY_HANDOFF_V21` | **MORTO** | **sim** | `italia-portale/audit/build-v21.mjs` |
| 20 | `meeting-intelligence-snapshot.json` | — | irmão do #13 | **sim** | `pacote/meeting_snapshot.py` |

**Nenhum global fica sem leitor.** Foi medido um a um: os **20 globais**
declarados têm todos pelo menos um consumidor real — 0 órfãos.

**`italy-v21.js` é a exceção que importa.** Ele **define o mesmo global**
`ITALY_HANDOFF_V21` que o #11, é escrito por `build-v21.mjs`, ocupa 10,3 MB — e
**nenhum HTML o carrega**. Um gerador que ainda sabe gerar acaba por gerar: se
alguém o incluir, ele sobrescreve a fronteira de ingestão inteira.

---

## FASE B · CAMINHANDO PARA TRÁS

### O que o próprio artefato declara, e o que sobrevive à conferência

| DATASET | MONTANTE DECLARADO | EXISTE? |
|---|---|---|
| `italy-handoff-v21.js` | `build/ITALY-REALITY-HANDOFF-V2.1/DESIGN-INGEST/` | **não solto** — gitignored; existe um ZIP versionado |
| `italy-ingested.js` | `SINTONIA-ITALY-CLAUDE-DESIGN-PACK / 01_DATA_NORMALIZED` | **não** — 0 ocorrências no repo |
| `italy-canonical-windows.js` | `CANONICAL-CROP-WINDOWS-2026-09-02.json` | **não** — 0 ocorrências no repo |
| `italy-demo-data.js` | `ITALY-DEMO-PROVENANCE-MATRIX.md` | parcial — existe `PROVENANCE-MATRIX.json` |
| `support.js` | `dc-runtime/src/*.ts` | **não** — `dc-runtime` não existe |
| `italy-casa.js` | 6 handoffs em `client/upstream/` + snapshot | **sim**, todos os 6 presentes |

### O achado central: o ZIP versionado é outra safra

`build/SINTONIA-ITALY-REALITY-HANDOFF-V2.1.zip` (2,03 MB,
`sha256:04a6c86f…`) é idêntico em `HEAD` e em `5101073`. Rodando
`portoes/site_v21_ingest.py` contra ele **numa árvore isolada**, o próprio portão
recusa:

```
INGESTAO RECUSADA — o pacote nao prova a sua proveniencia:
  · BUILD_ID V21-99226fbb90dcdbc2 != V21-06c6421d001ea52a
  · CASOS 37 != 43
  · MEETING_SURFACE_RULE ausente
  · ESTADO REVOGADO PREPARE_NOW em 6 casos
```

> **O pacote que o portal serve não está guardado em lado nenhum deste
> repositório.** O ZIP é uma safra anterior (37 casos); o portal serve 43.

E isso **não é um buraco** — é o desenho. `italia-portale/audit/INGESTION-REPRODUCTION.json`
regista que a cadeia foi corrida **duas vezes em worktrees limpos** em `5101073`
(branch `claude/acervo-to-package-intelligence-v1`, commit que existe e está
datado `2026-09-07 01:41:30` — exatamente o `MEETING_CUTOFF` carimbado no
snapshot), com **34/34 hashes idênticos**. E os insumos dessa cadeia
(`build/ITALY-REALITY-HANDOFF-V2`, `data/samples/IT-LASTMILE`,
`IT-ISTAT-COLTIVAZIONI`, `IT-CATALOGO`) **estão todos versionados**.

> **ESTE PACOTE NÃO SE GUARDA — GERA-SE.** O pai é uma cadeia pinada num commit,
> com 34 hashes para conferir. Isso é pai provado, não pai ausente.

### Os pins do upstream — conferidos contra disco **e** contra git

| ARTEFATO | CLASSE | DISCO = PIN | BLOB NO COMMIT = PIN |
|---|---|---|---|
| `IT-FUTURO-HANDOFF-LINHA-B-V1.json` | BASE | ✅ | ✅ |
| `IT-HANDOFF-LINHA-B-SINAIS_DE_CAMPO-V1.json` | BASE | ✅ | ✅ |
| `IT-HANDOFF-LINHA-B-FONTES-V1.json` | BASE | ✅ | ✅ |
| `IT-HANDOFF-LINHA-B-FITOSSANITARIO-V1.json` | BASE | ✅ | ✅ |
| `IT-TOP3-SENSORES-V1.json` | ENRIQ. | ❌ **DERIVOU** | ✅ |
| `IT-PORTAL-SPRINT-HANDOFF-HUMAN-SENSORS-V1.json` | ENRIQ. | ❌ **DERIVOU** | ✅ |

**4/6 conferem; 2/6 derivaram** — e derivaram **nas duas linhas** (medido também
no funcional), portanto não é artefato desta sessão. A deriva é rastreável commit
a commit:

```
IT-TOP3-SENSORES-V1.json      0edbbd43 bf134391…  ← o que o pin declara
                              b8321b07 6e01c45b…  ← mudou aqui
                              HEAD     6e01c45b…
HUMAN-SENSORS-V1.json         0edbbd43 1283b4f7…  ← o que o pin declara
                              b8321b07 8ce250d6…
                              e251ace0 8bb9818e…  ← mudou de novo
                              HEAD     8bb9818e…
```

`e251ace0` mexeu no handoff e **não** regerou `italy-casa.js`. Resultado: o
pacote que o browser carrega declara consumir bytes que já não estão naquele
caminho, e o portão `PINS_REFEITOS` de `audit/casa-gate.mjs` — que compara pin,
declaração **e** disco — reprova hoje.

**Isto é reconciliável**: os bytes que o pin declara continuam recuperáveis nos
commits pinados (`5703711`, `7501255`), conferidos nesta auditoria.

---

## FASE C · SUPABASE STORAGE ITÁLIA — **NÃO MEDIDO**

Medição das credenciais neste ambiente:

```
SUPABASE_URL              AUSENTE       SUPABASE_ANON_KEY    AUSENTE
SUPABASE_SECRET_KEY       AUSENTE       SUPABASE_DB_URL      AUSENTE
SUPABASE_SERVICE_ROLE_KEY AUSENTE       DATABASE_URL         AUSENTE
```

```
SUPABASE_IT_OBJECTS_MATCHED = NÃO SEI — não medido, sem credencial
```

**Os números do baseline não foram reproduzidos e não são repetidos aqui como
se fossem medição.** Nenhum documento deste repositório descreve
«195 objetos / 80,7 MB / PRODUCT_DOM / CAPTURE / MANIFEST» — procurado e não
encontrado. Ausência de prova não é prova de ausência: o bucket pode muito bem
conter tudo aquilo. Só não foi visto daqui.

**O que se sabe do bucket, por precedente versionado:** o padrão de caminho
existe e está provado para a **Espanha** —
`ES/adama-website/ADAMA-ES-<hash12>/<hash16>-<nome>.pdf`, 138 linhas de
`raw_asset` em `supabase/importacoes/ADAMA-ES-CATALOGO-2026-08-30.sql`. O
`IT/adama-website/` da missão é o análogo italiano desse mesmo desenho.

---

## FASE D · MANIFESTOS E EVIDÊNCIA DE ORIGEM

Dois manifestos prometem original italiano. Ambos foram medidos **contra os
bytes**, não contra o caminho que escrevem.

| MANIFESTO | ITENS | COM SHA256 | COM URL | BYTES AQUI |
|---|--:|--:|--:|--:|
| `data/raw/IT-ROTULOS/_MANIFESTO.json` | 163 | 163 | 163 | **0** |
| `research/adama-italy-product-intelligence-deep/LABEL-MANIFEST.json` | 141 | 141 | 141 | **0** |

**304 documentos com proveniência completa e zero bytes.** `data/raw/*` é
gitignored por decisão D-003 («o bruto pesado vai para Storage; o Git guarda hash
e manifesto»), e a política foi cumprida: o manifesto ficou, os bytes saíram.

A rota de recuperação **já foi tentada por uma missão anterior**, e o registo é
honesto — `DOCUMENTS_RECOVERED: 0`, com `ADAMA_MEDIA_DOWNLOAD` devolvendo 403,
`SUPABASE_BUCKET` sem credenciais e `GIT_HISTORY` ausente.

**Reconferido de forma independente nesta auditoria, sem confiar no relato:**

```
git log --all --diff-filter=A -- 'data/raw/IT/**'        → vazio
git rev-list --all --objects | grep adama-website        → vazio
find / -name '*.pdf' -path '*adama*'                     → vazio
find / -name '002732.pdf'                                → vazio
```

**Nenhum dos 304 PDFs entrou no Git em qualquer branch, nunca.** Confirmado.

> **`IT/adama-website/…` é endereço físico. Não é `SOURCE_ID`.** Nenhuma linha
> deste censo transformou um caminho de bucket em identidade de fonte.

---

## FASE E · CLASSIFICAÇÃO

### Camadas do portal (20)

| CLASSE | N | QUAIS |
|---|--:|---|
| `DERIVED_WITH_PROVEN_PARENT` | 4 | `italy-handoff-v21.js`, `meeting-intelligence-snapshot.js`, `…​.json`, `italy-casa.js` |
| `DERIVED_ORPHAN` | 4 | `italy-canonical-windows.js`, `italy-label-verdicts.js`, `italy-ingested.js`, `italy-v21.js` |
| `SUPPORT_NOT_OBSERVATION` | 10 | demo-data, briefs, market-pulse, science-business, i18n, app-model, meeting-labels, adama-relevance, meeting-surface, italy-pdf |
| `UNKNOWN` | 2 | `italy-real-intelligence.js`, `italy-catalog.js` |
| `RECONCILIABLE_ORIGINAL` | **0** | — nenhuma camada do portal é um original |

Sobre `italy-canonical-windows.js`: o montante declarado
(`CANONICAL-CROP-WINDOWS-2026-09-02.json`) não existe, e o artefato sobrevivente
mais próximo **não serve como substituto** — o ficheiro do portal tem **29
janelas** com IDs `IT-WIN-0001` (4 dígitos); o `CROP-WINDOWS.json` do ZIP tem
**7 registos** com IDs `IT-WIN-001` (3 dígitos). Espaços de identificador
diferentes e contagens diferentes. Casá-los seria fabricar linhagem.

### Corpus de originais que a cadeia nomeia (339)

| CLASSE | N | O QUÊ |
|---|--:|---|
| `RECONCILIABLE_ORIGINAL` | **6** | raw do `collection-store` com `DOCUMENT_ID` re-derivado dos bytes |
| `RECONCILIABLE_WITH_UNKNOWN_FIELDS` | **4** | raw presente e SHA confere; identidade exige `pdftotext` (ausente aqui) |
| `RECOLLECT_REQUIRED` | **304** | 163 rótulos Ministero + 141 documentos ADAMA — URL e SHA conhecidos |
| `UNKNOWN` | **25** | `RAW_PATH` aponta para `C:/eame-sintonia-ops/…` |
| `SUPPORT_NOT_OBSERVATION` | **6** | os handoffs Linha-B: listas de autorização, não conteúdo |

---

## FASE F · O PORTAL NÃO É EVIDÊNCIA

Os handoffs Linha-B parecem dado e **não são**. Medidos campo a campo, a maior
lista de `IT-HANDOFF-LINHA-B-FONTES-V1.json` (`ENTRADAS_AUTORIZADAS`, 91
registos) tem exatamente estes campos:

```
ID · SUBCONJUNTO · DESTINO · AVISO · LIMITES
```

Nenhum conteúdo. Nenhuma URL. Nenhuma data de fato. É uma **lista de quais IDs
podem ser desenhados e com que ressalva** — e o próprio ficheiro assina isso:
«empacota o que o contrato já aprovou. Não recalcula julgamento.»

> **MANIFESTO NÃO É CONTEÚDO. LISTA DE AUTORIZAÇÃO NÃO É OBSERVAÇÃO.**
> Promover qualquer um dos 6 a RAW encheria a Collection de ponteiros.

A proveniência que eles declaram foi conferida: os três
`SOURCE_ARTIFACT_HASHES` batem como **`sha256[:32]`** contra os blobs em
`5855cad` (`be52cf12…`, `ea1e4338…`, `e78e80ce…`). São hashes verdadeiros,
**truncados a 128 bits** e rotulados `sha256:` — o que é mais fraco do que o
rótulo promete, e fica registado. `data/samples/IT-FONTES-V1/` já não existe em
`HEAD`; é recuperável em `5855cad`.

---

## FASE G · O CAMINHO ATÉ A SALA — ONDE ELE PARTE

| ETAPA | DONO EXISTE? | MEDIÇÃO |
|---|---|---|
| `RECONCILIATION RUN` | ⚠️ **parcial** | tabela `collection_run` existe (migration 001). Escritor italiano `coleta/italy_pilot_collect.mjs` **não importa** nesta linhagem |
| `STORAGE OBJECT` | ❌ **NÃO EXISTE** | `storage_object`: **0 ocorrências** em todo o repositório |
| `RAW OBSERVATION` | ✅ | `raw_asset` existe; `RAW_OBSERVATION_ID = raw_asset.id` respeitado |
| `DERIVED` | ❌ **NÃO EXISTE** | `derived_artifact`: **0 ocorrências** em todo o repositório |
| `STRUCTURED` | ✅ | `registro_regulatorio`, `catalogo_produto`, `boletim_fitossanitario`, … |
| `ADMISSION` | ⚠️ **parcial** | `admissao/admissao.py` decide por par (item, universo) e escreve `data/samples/LIVRO-DE-DECISOES.json` — **ficheiro, não tabela** |
| `READY` | ❌ **sem dono** | nenhuma tabela, nenhum módulo |
| `SALA DE ESPERA` | ❌ **sem endereço** | `guarda/` é a metáfora documentada, não um armazém endereçável |

```
CAN_REACH_WAITING_ROOM      = 0
BLOCKED_BEFORE_WAITING_ROOM = 339   (todos)
```

### O blocker executável, medido

```
$ node -e "import('./coleta/italy_pilot_collect.mjs')"
IMPORT FALHOU: ERR_MODULE_NOT_FOUND
  Cannot find module '/home/user/eame-sintonia/coleta/italy_contracts.mjs'
```

São **9 imports quebrados**, todos da mesma causa — o commit `b8321b07` («149
scripts saem de uma pasta só e vão para a gaveta do que são») moveu os módulos e
não atualizou quem os importa:

```
candidatas/italy_write_matrix.mjs  -> ./italy_contracts.mjs · ./italy_source_health.mjs
coleta/italy_pilot_collect.mjs     -> ./italy_contracts.mjs
coleta/italy_recurrent_collect.mjs -> ./italy_contracts.mjs · ./italy_profiles.mjs
provas/italy_pilot_negativos.mjs   -> ./italy_contracts.mjs · ./italy_pilot_collect.mjs
regras/italy_pilot_guards.mjs      -> ./italy_pilot_collect.mjs
regras/italy_scheduling_guards.mjs -> ./italy_profiles.mjs
```

**Na linha funcional já está corrigido** (`../regras/italy_contracts.mjs`). Não é
regressão desta missão; é dívida que esta linhagem carrega.

### E o achado que decide tudo: a Itália nunca teve RAW canônico

| IMPORTAÇÃO | `collection_run` | `raw_asset` | `catalogo_captura` |
|---|--:|--:|--:|
| `IT-CAMADAS-2026-09-02.sql` | **0** | **0** | **0** |
| `IT-LASTMILE-2026-09-02.sql` | **0** | **0** | **0** |
| `ADAMA-ES-CATALOGO-2026-08-30.sql` | 1 | **138** | 1 |

Os 163 registos regulatórios italianos entram assim — repare no que **não** está
na lista de colunas:

```sql
insert into public.registro_regulatorio
  (pais, registration_id, nome_comercial, titular, formulado,
   estado, fecha_caducidad, fonte, fonte_versao, capturado_em)
```

`raw_asset_id` **existe na tabela e não é preenchido**.

> **A Itália entrou como STRUCTURED sem nunca ter passado por RAW.**
> `CANONICAL_RAW_ALREADY_EXISTS = 0` · `CANONICAL_RAW_MISSING = 339`

E nem a aplicação está provada: o próprio cabeçalho do SQL diz
«NAO EXECUTADO nesta sessao: as credenciais do Supabase sao secrets do GitHub
Actions e nao existem aqui». **Ficheiro SQL escrito ≠ linha no banco.**

---

## FASE H + I · CANÁRIO

```
LEGACY_CANARY = NOT_RUN
```

Não por escolha — por três impedimentos medidos:

```
psql      /usr/bin/psql      ✅ cliente
postgres  AUSENTE            ❌ sem servidor
initdb    AUSENTE            ❌ não dá para criar cluster descartável
docker    /usr/bin/docker    ⚠️ presente, DAEMON INDISPONIVEL
credenciais Supabase         ❌ as seis variáveis ausentes
storage_object · derived_artifact  ❌ sem dono no repositório
```

```
CANARY_RUN_CREATED              NÃO          CANARY_STRUCTURED            NÃO
CANARY_RAW_CREATED              NÃO          CANARY_ADMISSION             NÃO
CANARY_STORAGE_LINKED           NÃO          CANARY_READY                 NÃO
CANARY_DERIVED                  NÃO          CANARY_WAITING_ROOM_DISPOSABLE NÃO

CANARY_READY_TO_RAW      = NOT_RUN
CANARY_RAW_TO_STORAGE    = NOT_RUN
CANARY_READY_TO_STORAGE  = NOT_RUN

SOURCE_ID_FABRICATION          = 0
DOCUMENT_ID_FABRICATION        = 0
RAW_OBSERVATION_ID_FABRICATION = 0
LIVE_WRITES                    = 0
REAL_WAITING_ROOM_ITEMS_CREATED= 0
```

### O que **foi** provado, sem banco e sem rede

O lado de **entrada** do canário está pronto e verificado. Re-derivando a
identidade a partir dos bytes preservados, com a mesma lógica do coletor:

```
CONFERE  IT-T2-002  ARPAV:Z01:20260903160930          sha=ok  id=ok
CONFERE  IT-T2-002  ARPAV:Z09:20260902152638          sha=ok  id=ok
CONFERE  IT-T2-002  ARPAV:Z16:20260903160912          sha=ok  id=ok
CONFERE  IT-T2-002  ARPAV:Z24:20260902152048          sha=ok  id=ok
CONFERE  IT-T2-004  SIAS:…:WINDOW_END_2026-09-05      sha=ok  id=ok
CONFERE  IT-T3-005  TERRETRURIA:31-08-2026:06-09-2026 sha=ok  id=ok
PULADO   IT-T3-002 · IT-T3-008 · IT-T3-010 · IT-T4-001  (exigem pdftotext)
─────────────────────────────────────────────────────────────────────
CONFEREM=6   DIVERGEM=0   PULADOS=4
```

**Seis originais italianos cuja identidade semântica se reconstrói dos próprios
bytes, sem rede e sem confiar em caminho nenhum.** É o material mais forte que
existe para uma futura reconciliação — e é exatamente o que a FASE H pediria,
faltando só o banco onde pousar.

### FASE I · qual operação seria legítima

```
REGISTER_EXISTING_OBJECT   → BLOQUEADO. Não há `storage_object`, e nenhuma
                             medição prova que os bytes estão no bucket.
READ_AND_REPRESERVE        → LEGÍTIMO para os 10 objetos cujos bytes estão
                             aqui e conferem contra o SHA registado.
BLOCKED                    → para os 329 restantes.
```

**Não existe atalho de legado.** Declarar um objeto do bucket como
`storage_object` canônico porque o caminho parece certo é exatamente o ataque
17 — e sem `storage_object` no repositório, nem seria possível.

---

## FASE J · O QUE O PORTAL LÊ HOJE

Nada foi alterado no portal. Esta é a lista para substituição futura.

| EDGE | N | DATASETS |
|---|--:|---|
| `LEGACY_DIRECT_READ` | 12 | canonical-windows, label-verdicts, real-intelligence, demo-data, market-pulse, science-business, catalog, ingested, handoff-v21, briefs, app-model, pdf |
| `GENERATED_FROM_CANONICAL` | 4 | `italy-casa.js`, `adama-relevance.js`, `meeting-intelligence-snapshot.{js,json}` |
| `CANONICAL_READ` | **0** | **nenhum consumidor do portal lê a Collection canônica** |
| `UNKNOWN` | 4 | `italy-i18n.js`, `meeting-labels.js`, `meeting-surface.js`, `italy-v21.js` (morto) |

> **Zero.** Nenhuma tela do portal italiano lê hoje `data/collection-ledger/` ou
> `data/collection-store/`. As 144 observações e os 35 objetos raw da Collection
> canônica **não chegam a nenhuma tela**. O portal e a Collection são, hoje, dois
> mundos que não se tocam.

---

## TABELA FINAL

Abreviado: `S_ID`/`D_ID` = estado de SOURCE_ID / DOCUMENT_ID · `PROV` = proveniência ·
`COLL` = estado na Collection canônica · `SALA` = chega à Sala?

| DOMÍNIO | PORTAL_DATASET | CONSUMER | WRITER | UPSTREAM | ORIG? | ONDE | S_ID | D_ID | PROV | COLL | CLASSE | SALA | BLOCKER |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| CASOS | `meeting-intelligence-snapshot.js` | meeting-surface | `pacote/meeting_snapshot.py` | `OPPORTUNITIES.json` @5101073 | não | cadeia @commit | **FABRICADO** (20 `SRC_*`) | UNKNOWN | PARCIAL | ausente | `DERIVED_WITH_PROVEN_PARENT` | ❌ | S_ID de host |
| CASOS | `italy-casa.js` | portale, casa | `superficie/it_casa_dados.py` | 6 handoffs pinados | não | git (4/6 em disco) | UNKNOWN | UNKNOWN | PARCIAL | ausente | `DERIVED_WITH_PROVEN_PARENT` | ❌ | 2 pins derivados |
| TUDO | `italy-handoff-v21.js` | app-model | `portoes/site_v21_ingest.py` | `DESIGN-INGEST/` @5101073 | não | cadeia @commit | **FABRICADO** (196 `SRC_*`) | UNKNOWN | PARCIAL | ausente | `DERIVED_WITH_PROVEN_PARENT` | ❌ | S_ID de host |
| CATÁLOGO | `italy-ingested.js` | app-model, market | **UNKNOWN** | DESIGN-PACK — **ausente** | não | — | UNKNOWN | UNKNOWN | UNKNOWN | ausente | `DERIVED_ORPHAN` | ❌ | montante ausente |
| CATÁLOGO | `italy-catalog.js` | app-model | **UNKNOWN** | **UNKNOWN** | não | — | UNKNOWN | UNKNOWN | UNKNOWN | ausente | `UNKNOWN` | ❌ | escritor desconhecido |
| RÓTULOS | `italy-label-verdicts.js` | demo-data, app-model | auditoria à mão | 163 PDF Ministero | **não** | manifesto sem bytes | **PROVADO** (registro) | **PROVADO** | **COMPLETA** | ausente | `DERIVED_ORPHAN` | ❌ | 0/163 bytes |
| RÓTULOS | *(corpus)* 163 PDF | — | `coleta/rotulos_baixar.py` | EtichettaServlet | **não** | — | **PROVADO** | **PROVADO** | **COMPLETA** | ausente | `RECOLLECT_REQUIRED` | ❌ | bytes fora daqui |
| CATÁLOGO | *(corpus)* 141 doc ADAMA | — | pesquisa deep | adama.com/italia | **não** | — | **PROVADO** | PARCIAL | **COMPLETA** | ausente | `RECOLLECT_REQUIRED` | ❌ | 403 + sem credencial |
| CIÊNCIA | `italy-real-intelligence.js` | demo-data, app-model | **UNKNOWN** | «project brief» — ausente | não | — | UNKNOWN | UNKNOWN | UNKNOWN | ausente | `UNKNOWN` | ❌ | montante ausente |
| JANELAS | `italy-canonical-windows.js` | 5 leitores | **UNKNOWN** | `CANONICAL-CROP-WINDOWS…` — ausente | não | — | UNKNOWN | UNKNOWN | UNKNOWN | ausente | `DERIVED_ORPHAN` | ❌ | outro espaço de ID |
| MERCADO | `italy-market-pulse.js` | app-model | à mão (esvaziado) | — | n/a | — | n/a | n/a | n/a | n/a | `SUPPORT_NOT_OBSERVATION` | n/a | — |
| CASOS | `italy-demo-data.js` | app-model, portale | PRNG semeado | — | n/a | — | n/a | n/a | n/a | n/a | `SUPPORT_NOT_OBSERVATION` | n/a | sintético |
| — | `italy-v21.js` **(morto)** | **nenhum HTML** | `audit/build-v21.mjs` | `DESIGN-INGEST/` | não | — | UNKNOWN | UNKNOWN | UNKNOWN | ausente | `DERIVED_ORPHAN` | ❌ | gerador sem leitor |
| CAMPO | *(Collection)* 10 raw | **nenhum** | `coleta/italy_pilot_collect.mjs` | 7 fontes com contrato | **SIM** | `data/collection-store/` | **PROVADO** | **6 dos bytes** | **COMPLETA** | **no ledger** | `RECONCILIABLE_ORIGINAL` (6) / `…UNKNOWN_FIELDS` (4) | ❌ | sem `storage_object` |
| CAMPO | *(Collection)* 25 raw | — | idem | idem | **não** | `C:/eame-sintonia-ops/` | **PROVADO** | **PROVADO** | **COMPLETA** | **no ledger** | `UNKNOWN` | ❌ | fora do repositório |
| SUPORTE | 6 handoffs `upstream/` | `it_casa_dados.py` | Linha B @5855cad | `data/samples/IT-*-V1/` | n/a | git @5855cad | n/a | n/a | PARCIAL | n/a | `SUPPORT_NOT_OBSERVATION` | n/a | lista, não conteúdo |

---

## CONTAGENS

```
PORTAL_DATASETS_TOTAL                 20      (19 .js com global + 1 .json irmão)
  carregados por algum HTML           18
  construídos e nunca carregados       1      italy-v21.js
PORTAL_DATASETS_WITH_PROVEN_WRITER     6
PORTAL_DATASETS_WITH_UNKNOWN_WRITER   14      (8 destes são código à mão, por desenho)

LEGACY_OBJECTS_REFERENCED            339      163 + 141 + 35
ORIGINALS_FOUND                       10
ORIGINALS_NOT_FOUND                  329

RECONCILIABLE_ORIGINAL                 6
RECONCILIABLE_WITH_UNKNOWN_FIELDS      4
DERIVED_WITH_PROVEN_PARENT             4
DERIVED_ORPHAN                         4
SUPPORT_NOT_OBSERVATION               16      10 do portal + 6 handoffs
RECOLLECT_REQUIRED                   304
UNKNOWN                               27      2 do portal + 25 raw fora do repo

SUPABASE_IT_OBJECTS_MATCHED    NÃO SEI — não medido, sem credencial
GIT_OBJECTS_MATCHED                   10      bytes presentes E sha conferido

SOURCE_ID_PROVEN                       7      fontes com contrato (13 declaradas, 7 no piloto)
SOURCE_ID_UNKNOWN / FABRICADO        216      196 em handoff-v21 + 20 no snapshot

DOCUMENT_ID_PROVEN                    35      declarados no ledger
  destes, re-derivados dos bytes       6
DOCUMENT_ID_UNKNOWN                  304      os dois corpora de manifesto

CANONICAL_RAW_ALREADY_EXISTS           0
CANONICAL_RAW_MISSING                339

CAN_REACH_WAITING_ROOM                 0
BLOCKED_BEFORE_WAITING_ROOM          339
```

---

## RED TEAM · 20 ATAQUES, 0 SOBREVIVENTES

| # | ATAQUE | RESULTADO | PROVA |
|--:|---|---|---|
| 1 | caminho usado como `SOURCE_ID` | **MORTO** | `IT/adama-website/…` fica como endereço; `SOURCE_ID` sai de `regras/italy_contracts.mjs` |
| 2 | filename usado como `DOCUMENT_ID` | **MORTO — e achou dívida real** | das 7 fontes-piloto: **3** derivam o ID só do conteúdo (T3-005, T2-002, T2-004), **3** usam o nome do ficheiro (T3-002, T3-008, T3-010) e **1** usa metadado de descoberta (T4-001). Registado como `DOCUMENT_ID_FROM_ROUTE_FILENAME`, não como provado-pelo-conteúdo |
| 3 | SHA usado como observação | **MORTO** | 144 observações sobre 35 objetos; `SEEN_AGAIN`=109. Bytes iguais, observações distintas |
| 4 | JSON do portal tratado como RAW | **MORTO** | 0 camadas classificadas `RECONCILIABLE_ORIGINAL` |
| 5 | derivado tratado como original | **MORTO** | `DERIVED_WITH_PROVEN_PARENT` ≠ original; pai é cadeia@commit |
| 6 | manifesto tratado como conteúdo | **MORTO** | 6 handoffs → `SUPPORT_NOT_OBSERVATION`; campos medidos: `ID·SUBCONJUNTO·DESTINO·AVISO·LIMITES` |
| 7 | `PRODUCT_DOM` como fato | **MORTO** | os 141 são documentos de catálogo; `CURRENT_LABEL_STATUS: UNKNOWN` em 141/141 |
| 8 | dois objetos com o mesmo SHA | **MORTO** | 35 SHA repetidos, **todos** mapeando a 1 par `(SOURCE_ID, DOCUMENT_ID)`. Zero colisão de identidade |
| 9 | original ausente, derivado presente | **MORTO** | 4 `DERIVED_ORPHAN` nomeados, nenhum promovido |
| 10 | `SOURCE_LOCATION` → `FACT_LOCATION` | **MORTO** | `GEOGRAPHY-CONTRACT.json`: 6.455 checados, 0 violações. Nenhuma linha aqui promoveu |
| 11 | publication time → `FACT_TIME` | **MORTO** | 132/144 com `FACT_TIME` `UNKNOWN` **e o motivo escrito** |
| 12 | `UNKNOWN` → valor provável | **MORTO** | FASE C fica `NÃO SEI`; o baseline 195/80,7 MB não foi repetido como medição |
| 13 | ficheiro manual contado como reconciliável | **MORTO** | demo-data, i18n, labels → `SUPPORT_NOT_OBSERVATION` |
| 14 | portal reader contado como produtor | **MORTO** | `it_casa_dados.py` **lê** labels/surface/snapshot e **escreve** só 2 ficheiros — separado linha a linha |
| 15 | gerador declarado sem execução provada | **MORTO — e derrubou uma suposição** | corrido em árvore isolada: o portão **recusou** o ZIP (37≠43 casos) |
| 16 | storage object contado como raw observation | **MORTO** | `raw_asset` ≠ bytes; 25 `RAW_PATH` registados e ausentes |
| 17 | objeto do bucket como `storage_object` canônico | **MORTO** | `storage_object` **não existe** — 0 ocorrências no repositório |
| 18 | READY criado sem Admission | **MORTO** | nenhum READY criado; `CANARY = NOT_RUN` |
| 19 | item de suporte chegando à Sala | **MORTO** | `CAN_REACH_WAITING_ROOM = 0` |
| 20 | dado ES/FR contaminando o censo IT | **MORTO** | 0 observações não-`IT-` no ledger; o `proto_es.py` do cartão foi excluído por escrito |

```
RED_TEAM_ATTACKS   = 20
RED_TEAM_SURVIVORS = 0
```

---

## SYSTEM_MAP_DEFECT

Registados, **não corrigidos** — a correção é da linha própria do System Map.

```
SYSTEM_MAP_DEFECT_1 · o mapa JÁ ESTAVA VERMELHO antes desta missão
    Medido em árvore pristina (git status vazio, mapa restaurado):
        SYSTEM_MAP_CHECK=FAIL · 2 provas reprovadas
          P1_SEM_DRIFT          files_code_dir 433→434 · files_code_unclaimed 0→1
          P9_CODIGO_DECLARADO   .github/workflows/scrap-social.yml
    Causa única: scrap-social.yml não está em architecture.declared.json.
    Introduzido por df165da9 («registrar o workflow scrap-social no ramo padrão»).
    DELTA DESTA MISSÃO = ZERO: o detalhe da falha é idêntico byte a byte com
    e sem os dois artefatos da entrega — porque nenhum deles é código, não
    criam aresta, não criam dono e não mudam arquitetura.
    NÃO foi regerado de propósito: esta missão está proibida de editar o mapa,
    e regerar aqui absorveria em silêncio um defeito pendente de outra linha.

SYSTEM_MAP_DEFECT_2 · C-PORTAL-DADOS mede país errado
    paises = {ESPANHA: 1} · paises_dado = {ESPANHA: 4} · pais = TRANSVERSAL
    13 dos 15 ficheiros do cartão são italianos. A Itália não aparece na contagem.

SYSTEM_MAP_DEFECT_3 · o cartão exclui as camadas maiores
    `exclude` remove 6 ficheiros, entre eles os dois maiores do portal
    (italy-handoff-v21.js 8,3 MB e italy-v21.js 10,3 MB).
    O cartão chamado «Camadas de dado do portal» não cobre as maiores.

SYSTEM_MAP_DEFECT_4 · italy-v21.js aparece no mapa sem leitor
    Nenhum HTML o carrega; o mapa não marca a aresta como morta.

SYSTEM_MAP_DEFECT_5 · validate_system_map.py regenera em cima dos ficheiros
    Correr o validador modifica 8 ficheiros versionados (carimbo de branch/HEAD).
    Um validador que suja a árvore de trabalho não pode ser corrido antes de commit
    sem um `git checkout --` a seguir. Foi o que se fez aqui.
```

**Nenhum ficheiro do System Map foi alterado por esta missão.** O validador foi
corrido, e as suas escritas foram revertidas com `git checkout -- system-map/data
italia-portale/client/system-map`.

---

## DEFEITOS DE CADEIA (fora do System Map)

```
DEFEITO_1 · 9 imports quebrados deixam a coleta italiana inexecutável
            nesta linhagem. Corrigido na linha funcional. Medido com node.

DEFEITO_2 · 2 dos 6 pins do upstream não batem com os bytes em disco,
            nas duas linhas. O portão PINS_REFEITOS reprova hoje.
            Bytes recuperáveis nos commits pinados.

DEFEITO_3 · motor/v21_cadeia.sh aponta para o gerador canônico ERRADO:
            diz `claude/opportunity-commercial-priority-v1 @ 55c2674`
            (a safra de 37 casos), enquanto site_v21_ingest.py e
            INGESTION-REPRODUCTION.json dizem
            `claude/acervo-to-package-intelligence-v1 @ 5101073` (43 casos).
            Dois ponteiros para o mesmo conceito, um deles vencido.

DEFEITO_4 · SOURCE_IDS do pacote V2.1 são fabricados do host da URL
            (`sid()` em scripts/v21_ingest.py @5101073:
             'SRC_' + host maiúsculo). 196 IDs distintos atravessaram
            para o portal. `SRC_DOI_ORG` (769 ocorrências) nomeia um
            resolvedor, não um editor; `SRC_YOUTUBE` e `SRC_YOUTUBE_COM`
            são duas identidades para a mesma fonte.
            → É a razão nº 1 pela qual a camada V2.1 não pode ser
              reconciliada como está.

DEFEITO_5 · SOURCE_ARTIFACT_HASHES dos handoffs Linha-B são sha256
            truncados a 32 hex (128 bits) rotulados «sha256:».
            Conferem como sha256[:32]; o rótulo promete mais do que entrega.
```

---

## KNOW_HOW_DELTA

```
KNOW_HOW_DELTA = ATUALIZAÇÃO NECESSÁRIA
```

Medido contra `claude/sintonia-eame-know-how-v1 @ 7b5e50cf` (§109, o mais
recente). Nenhum dos aprendizados abaixo está lá — procurado por termo e não
encontrado. **Nada foi escrito na branch do know-how**: ela andou durante esta
missão (§108 → §109 no mesmo dia) e sobrescrever aprendizado paralelo seria pior
do que atrasar o registo.

**Proposta, em `O QUE mudou → POR QUÊ → PROVA → CONSEQUÊNCIA`:**

> **1 · UM PACOTE QUE SE GERA NÃO SE PROCURA GUARDADO**
> *Mudou:* parou-se de tratar «o artefato não está no Git» como linhagem perdida.
> *Por quê:* duas sessões bloquearam à espera de um pacote «autêntico» commitado
> que nunca ia existir.
> *Prova:* o ZIP versionado carrega 37 casos e `V21-99226fbb90dcdbc2`; o portal
> serve 43 e `V21-06c6421d001ea52a`. A cadeia em `5101073` reproduz o segundo,
> 2× em worktrees limpos, 34/34 hashes idênticos.
> *Consequência:* pai provado pode ser **uma cadeia pinada num commit**, não só
> um ficheiro. O que se exige é o recibo com hashes — não o arquivo.

> **2 · UM ID DERIVADO DO HOST É UM AGRUPADOR, NUNCA UMA FONTE**
> *Mudou:* `SRC_<HOST>` deixa de contar como `SOURCE_ID`.
> *Por quê:* host não é editor, e o mesmo editor tem vários hosts.
> *Prova:* `sid()` fabrica de URL; 196 `SRC_*` atravessaram; `SRC_DOI_ORG` (769×)
> é um resolvedor; `SRC_YOUTUBE` e `SRC_YOUTUBE_COM` coexistem.
> *Consequência:* toda a camada V2.1 fica fora da Collection até rechavear
> contra o registo de fontes com contrato.

> **3 · UM CAMINHO ABSOLUTO DE OUTRA MÁQUINA É UMA PROMESSA, NÃO UM ACERVO**
> *Mudou:* `RAW_PATH` passa a ser medido contra a existência dos bytes.
> *Por quê:* o ledger dizia `RAW_OBJECT_CREATED: true` para 35 objetos.
> *Prova:* 25 dos 35 apontam para `C:/eame-sintonia-ops/…`; 10 existem e os 10
> conferem contra o SHA.
> *Consequência:* `RAW_PRESERVED_BEFORE_PARSE` prova ordem, não localização.
> Quem lê o ledger tem de perguntar «presente **onde**».

> **4 · STRUCTURED SEM RAW É UMA CASA SEM ALICERCE — E NÃO RECLAMA**
> *Mudou:* passou-se a contar `raw_asset` por país antes de dizer que um país
> «está na Collection».
> *Por quê:* a Itália parecia carregada e não estava.
> *Prova:* as duas importações italianas escrevem 0 `collection_run` e 0
> `raw_asset`; a espanhola escreve 1 e 138. `registro_regulatorio` italiano omite
> `raw_asset_id`, que a tabela tem.
> *Consequência:* «país importado» tem de significar RAW presente. 163 registos
> regulatórios italianos não têm observação nenhuma por trás.

---

## VEREDITO

```
ITALIA_PORTAL_LEGACY_CENSUS       = PASS
      as 20 camadas foram medidas a partir dos entrypoints reais; cada uma
      recebeu uma classe e um blocker nomeado. FASE C ficou NÃO SEI por falta
      de credencial — declarado, não contornado.

ITALIA_LEGACY_RECONCILIATION_READY = NO
      não por falta de material: por falta de dono.
      `storage_object` e `derived_artifact` não existem no repositório,
      READY não tem dono, a Sala não tem endereço, e a coleta italiana
      não importa nesta linhagem.
      Há 6 originais prontos e 0 caminhos até a Sala.

LEGACY_CANARY                      = NOT_RUN
      sem servidor Postgres, sem daemon Docker, sem credencial Supabase e
      sem dono para duas etapas do caminho.
```

---

## ATERRAGEM

```
BRANCH        claude/wizardly-wright-uoodqk
START_HEAD    f437ff1140fa97484ca9695b341fbe9ca0a9f050
WORKTREE      limpo além dos dois artefatos desta missão
PUSH_STATE    ver o commit desta entrega

NÃO foi feito fast-forward para a linha funcional.
NÃO foi tocado claude/raw-observation-identity-3jbwco.
NÃO foi alterado o portal, o System Map, o Intelligence, nem a Sala real.
NÃO foi iniciada Big Collection, nem recoleta, nem SCRAP, nem rota paga.
LIVE_WRITES = 0.
```

**Nota sobre a branch.** A missão sugeriu
`claude/italia-portal-legacy-provenance-v1`; a branch designada desta sessão é
`claude/wizardly-wright-uoodqk`. As duas satisfazem o requisito de isolamento
(nenhuma é a linha funcional). Ficou a designada, e fica dito para o coordenador
não a procurar pelo outro nome.

**Nota sobre o gerador.** O inventário JSON foi produzido por um script
determinístico (duas corridas, mesmo `sha256`). Ele **não foi commitado**: em
`scripts/` reintroduziria a gaveta que `b8321b07` acabou de esvaziar, e em
qualquer outra gaveta exigiria declarar uma peça nova no System Map — que esta
missão está proibida de editar. A secção seguinte substitui-o: cada número tem o
comando que o refaz.

---

## COMO REFAZER CADA NÚMERO

```bash
# ordem de carga real do portal
grep -oE '<script[^>]*src="[^"]+"' italia-portale/client/portale.html

# camadas que definem dado, e quem as lê
grep -l 'window\.[A-Z_]\+ *=' italia-portale/client/*.js

# italy-v21.js não é carregado por nenhum HTML
grep -l "italy-v21" italia-portale/client/*.html italia-portale/BASELINE/*.html

# o ZIP versionado é outra safra (o portão recusa)
python3 portoes/site_v21_ingest.py     # numa árvore isolada com o ZIP extraído

# pins: disco × pin × blob no commit
python3 -c "import json;print(json.load(open('italia-portale/client/upstream/UPSTREAM-PINS.json'))['PINS'])"
sha256sum italia-portale/client/upstream/*.json

# SOURCE_ID fabricados que atravessaram
grep -oE '"SRC_[A-Z0-9_]+"' italia-portale/client/italy-handoff-v21.js | sort -u | wc -l

# Itália nunca teve RAW canônico
grep -c 'insert into public.raw_asset' supabase/importacoes/IT-*.sql
grep -c 'insert into public.raw_asset' supabase/importacoes/ADAMA-ES-CATALOGO-2026-08-30.sql

# storage_object e derived_artifact não existem
grep -rn "storage_object\|derived_artifact" supabase/ --include='*.sql'

# a coleta italiana não importa nesta linhagem
node -e "import('./coleta/italy_pilot_collect.mjs').catch(e=>console.log(e.code))"

# ledger: observações, objetos raw, bytes presentes
wc -l data/collection-ledger/italy/observations.ndjson
git ls-files data/collection-store | wc -l

# os dois manifestos sem bytes
python3 -c "import json;d=json.load(open('data/raw/IT-ROTULOS/_MANIFESTO.json'));print(d['TOTAL'])"
ls data/raw/IT-ROTULOS/

# nenhum PDF do adama-website entrou no Git, em branch nenhuma
git rev-list --all --objects | grep -i adama-website
```

---

## HARD STOP

A missão termina aqui. Não foi iniciada reconciliação em LIVE, não foram movidos
os 195 ficheiros do bucket (que aliás não foram sequer vistos), não foi populada
a Sala real, não foi iniciada Big Collection nem Intelligence, e o portal está
byte a byte como estava.

A decisão de integração volta ao coordenador.
