# DEFEITOS HERDADOS DO PASSAPORTE ANTERIOR — medidos, não narrados

**Data:** 2026-09-06 · **Alvo:** `PASSPORT-1.0` (branch `claude/sintonia-information-passport-bbtps0`, `ce6add1`)
**Base de comparação:** `origin/sintonia/canonical` (`10af4a7`)
**Método:** somente leitura. Nenhum arquivo do acervo foi alterado, nenhuma coleta foi feita.

> **Este documento não herda narrativa.** Cada achado abaixo foi medido nesta missão, sobre
> o artefato gravado, e traz o comando que o reproduz. Achado contra o trabalho anterior
> recebeu o mesmo padrão de verificação que achado a favor — e três hipóteses minhas foram
> **derrubadas** pela medição, e estão registradas como tal na seção 9.

---

## RESUMO

| # | defeito | gravidade | estado |
|---|---|---|---|
| D1 | `UNKNOWN` promovido a `PROVED` no eixo tempo — 346 itens | **ALTA** | vivo |
| D2 | Identidade ausente colapsa unidades distintas — 3 linhas → 1 item | **ALTA** | vivo |
| D3 | Universo parcial — 33 registros e 144.802 caracteres fora do passaporte | **ALTA** | vivo |
| D4 | Valor da dimensão não tem campo — `CROP`/`ISSUE`/`TIME` moram em prosa | **ALTA** | vivo |
| D5 | Projeção arbitra conflito por recência, não por prova — 197 itens | **MÉDIA** | vivo |
| D6 | Data de publicação vira tempo do fato sem prova — 1.478 itens | **MÉDIA** | vivo |
| D7 | Três vocabulários de capacidade sem mapa declarado | **MÉDIA** | vivo |
| D8 | `_sabido()` cego para sentinela com sufixo — 1.312 valores no acervo | **ALTA** | causa raiz de D1 |
| D9 | Independência existe em `voz.py` e **não foi herdada** pelo passaporte | **ALTA** | transporte ausente |
| D10 | Profundidade de leitura não é estado — escopo mora em prosa | MÉDIA | lacuna |
| **D11** | **`CLAIM_ID` não é identidade — 12 de 22 colididos, 83% das rotas afetadas** | **ALTA** | **vivo e materializado** |
| D12 | `admitir()` não valida `raw_state` contra o vocabulário | **ALTA** | latente |
| D13 | Esquema do evento é aberto; `CAMPOS_EVENTO` é código morto | **ALTA** | latente |
| D14 | `REASON` carrega três vocabulários diferentes no mesmo campo | **ALTA** | vivo |
| D15 | `CAPTURE` aprova `NOT_PRESERVED` — 335 itens sobem sem bruto | MÉDIA | vivo |
| D16 | Vocabulários abertos nunca validados; gramática de `IDENTITY_BASIS` só em lambdas | **ALTA** | latente |

---

## D11 · `CLAIM_ID` NÃO É IDENTIDADE — e a colisão já aconteceu

**O defeito mais grave desta lista, porque atinge a camada que os cruzamentos vão usar.**

```python
# scripts/passaporte.py:94
def claim_id(item, ordinal):
    return 'CLAIM-%s-%02d' % (item.split('-', 1)[1], int(ordinal))

# scripts/passaporte.py:366
for i, texto in enumerate(claims, 1):      # ← reinicia em 1 a CADA extração
    cid = claim_id(item, i)
```

O identificador é `item + ordinal`, e o ordinal **recomeça em 1 toda vez**. Extrair claims
duas vezes do mesmo item produz os **mesmos** `CLAIM_ID` para textos diferentes.

**Não é risco. É ocorrência, medida no log gravado:**

```
eventos CLAIMS_EXTRACTED                              55
CLAIM_ID distintos                                    22
   colididos (mais de um texto no mesmo id)           12    ← 54%
   limpos                                             10

eventos de rota/consumo ligados a CLAIM_ID            72
   pendurados num CLAIM_ID COLIDIDO                   60    ← 83%
```

E o exemplo é o pior possível — dois casos que foram escritos **de propósito** para se
contradizerem, compartilhando um identificador:

```
CLAIM-3CA2E441A6D5FD7A-01   (item ITEM-3CA2E441A6D5FD7A)
   texto: CASE-005 — A safra francesa de 2024 vista pelo clima da própria janela
   texto: CASE-006 — A mesma pergunta, a janela errada, a resposta invertida
   rota : ROUTED_TO_CAPABILITY · COUNTRY_CROP_PULSE · DIRECT
   rota : CONSUMED_BY_CAPABILITY · COUNTRY_CROP_PULSE
   rota : ROUTED_TO_CAPABILITY · OPPORTUNITY · BLOCKED
```

**Não há como dizer qual dos dois foi consumido.** A tabela `CLAIM_ID × CAPABILITY_ID`,
que é o coração do roteamento multicapacidade, está 83% apoiada em identificador ambíguo.

> Ironia medida: o contrato acertou a identidade do **item** (base global, opaca, com
> teste) e errou a identidade do **claim** exatamente pelo motivo que ele mesmo proíbe —
> derivar identidade de posição.

---

## D12 · `admitir()` não valida `raw_state`

`selar()` recusa estado fora do vocabulário (`passaporte.py:318-324`). `admitir()` **não**:

```python
# scripts/passaporte.py:284-289 — os oito campos obrigatórios
faltando = [n for n, v in (
    ('IDENTITY_BASIS', identity_basis), ('COLLECTION_ID', collection_id),
    ('SOURCE_ID', source_id), ('SOURCE_FAMILY', source_family),
    ('SOURCE_REFERENCE', source_reference), ('CAPTURED_AT', captured_at),
    ('CONTENT_TYPE', content_type), ('ACTOR', actor),
) if not v]                                    # ← raw_state NÃO está na lista

# linha 301 — e vai direto para o evento, sem passar pelo vocabulário
ev = self._evento(iid, 'ITEM_CAPTURED', ..., to_state=raw_state, ...)
```

A porta que o contrato declara **fechada** (`FAIL_CLOSED`, §6) tem uma fresta no primeiro
evento de todo item. O portão exercita 11 recusas e **nenhuma delas é esta**.

---

## D13 · O esquema do evento é aberto, e o campo que o fecharia é código morto

```python
# scripts/passaporte.py:221
CAMPOS_EVENTO = ('EVENT_ID', 'ITEM_ID', 'EVENT_TYPE', 'TIMESTAMP', 'ACTOR', ...)
# grep CAMPOS_EVENTO no arquivo: 1 ocorrência — a própria definição

# scripts/passaporte.py:354
for k, v in (extra or {}).items():
    if v is not None:
        ev[k] = v                              # ← qualquer chave entra
```

O contrato §3 promete *"dez campos, sempre presentes"*. O código aceita qualquer chave via
`extra=`, e a tupla que declararia o esquema nunca é consultada. Foi por essa porta que
`CLAIM_ID`, `CAPABILITY_ID`, `RELEVANCE`, `BLOCKER`, `CONTENT_CHARS` e `IDENTITY_BASIS`
entraram — todos úteis, **nenhum declarado**.

---

## D14 · `REASON` é três campos disfarçados de um

| quando o evento é… | `REASON` carrega | vocabulário |
|---|---|---|
| `STOPPED_WITH_REASON` | código de motivo | **fechado** (`MOTIVOS`, validado em `passaporte.py:325`) |
| `CLAIMS_EXTRACTED` | o **texto da afirmação** | aberto (`passaporte.py:371`) |
| `ROUTED_TO_CAPABILITY` | o **porquê da rota** | aberto (`passaporte.py:387`) |
| `CROP_DECLARED` | o **valor da cultura** | aberto — ver D4 |
| `TIME_RESOLVED` | a **data** | aberto — ver D1 |

Cinco significados, um slot. Não existem `CLAIM_TEXT`, `ROUTING_WHY`, `CROP`, nem
`FACT_TIME` como campos próprios. É a mesma doença de D4, e a causa de D1: **quando valor
e motivo dividem campo, nenhuma trava consegue distinguir os dois.**

---

## D15 · `CAPTURE` aprova item cujo bruto não foi preservado

```python
# scripts/passaporte.py:551
if item['RAW_STATE'] in ('PRESERVED', 'NOT_PRESERVED'):
    return 'PASSED', None                      # ← NOT_PRESERVED passa, sem motivo
```

```
RAW_STATE na captura:  PRESERVED 2.625  ·  NOT_PRESERVED 335
```

**335 itens sobem a escada inteira sem bruto preservado e sem `REASON_CODE`.** O balanço
anterior declara isso como política consciente (D-003: bruto de rota gratuita e HTML pesado
vivem fora do Git) — e a política é legítima. O defeito é que ela é aplicada **em silêncio,
no verdicto**, em vez de virar um `STOPPED_WITH_REASON` com motivo declarado. Quem lê a
contabilidade não distingue *"o bruto está lá"* de *"decidimos não guardar o bruto"*.

---

## D16 · Vocabulários abertos, e a gramática da identidade em 18 lambdas

`CONTENT_TYPE`, `ITEM_CLASS`, `SOURCE_FAMILY`, `SOURCE_ID` e `COLLECTION_ID` são exigidos
como **não-vazios** e nunca validados contra vocabulário. O portão compara
`CONTENT_TYPE == 'TRANSCRIPT'` (`passaporte.py:751`) enquanto os próprios testes do portão
admitem `content_type='T'` (`passaporte_portao.py:88`) e `content_type='VIDEO'` (linha 149).

E a gramática de `IDENTITY_BASIS` — `PLATAFORMA:TIPO:ID_EXTERNO`, a coisa de que **toda**
identidade do sistema depende — não existe como constante nem como função. Ela vive em 18
lambdas embutidas no portão:

```python
# passaporte_portao.py:38
('ES-T8-001-videos.json', 'VIDEOS', lambda i: 'YOUTUBE:VIDEO:%s' % i['EXTERNAL_ID']),
# passaporte_portao.py:52
lambda i: 'YOUTUBE:TRANSCRIPT:%s:%s' % (bf._vid(i['SOURCE_URL']), i['CAPTION_SOURCE'])
```

`item_id()` aceita **qualquer** string (`passaporte.py:91`). O portão
`ITEMS_WITHOUT_PASSPORT` compara duas implementações da mesma gramática — e é essa
duplicação que o contrato chama de *"caminho independente"*. É uma boa prova de
consistência e uma **má** proteção de formato: as duas podem estar erradas do mesmo jeito.

---

## D8 · A CAUSA RAIZ — `_sabido()` é cego para a própria sentinela da casa

`scripts/passaporte_backfill.py:55`

```python
NAO_SEI = ('NÃO SEI', 'NAO SEI', 'NOT_KNOWN', 'NAO_DECLARADO', 'NOT_DECLARED',
           'UNKNOWN', '', None)

def _sabido(v):                                    # linha 68
    return v not in NAO_SEI and str(v).strip() != ''
```

A trava é **igualdade exata**. Mas a casa tem o hábito — bom, e escrito em regra — de dizer
*por que* não sabe. O acervo grava:

```
"NÃO SEI — a rota devolve so tempo relativo"
"NÃO SEI — o comentario raramente declara lugar"
"NÃO SEI — a afiliação não declara região no registro"
```

Nenhuma dessas strings pertence à tupla. Todas passam por `_sabido()` **como se fossem
valor conhecido**.

**Raio de alcance medido no acervo — 1.312 valores, 39 arquivos, 46 campos distintos:**

| campo | ocorrências | o que o valor diz |
|---|---:|---|
| `FACT_LOCATION` | 386 | *"o comentario raramente declara lugar"* |
| `DATE` | 346 | *"a rota devolve so tempo relativo"* |
| `REGION` | 155 | *"a afiliação não declara região no registro"* |
| `ROLE` | 142 | *"o índice não declara papel"* |
| `FACT_REGION` | 142 | *"a afiliação é do AUTOR, não do estudo"* |
| `ACT_OUTCOME` | 38 | *"só o título foi casado"* |
| `TRANSCRIPT_LANGUAGE` | 15 | *"a rota nao declara o idioma da legenda"* |
| … mais 39 campos | 88 | inclui `CROP`, `ISSUE`, `CULTURA`, `ALVO`, `DATA_DO_FATO`, `FACT_DATE` |

Reproduzir: `python3 scripts/passaporte_censo.py --acervo . --passaporte <ref>`, seção D8.

> A boa prática da casa — explicar a ignorância — é exatamente o que derrota a trava.
> A correção não é abandonar o hábito. É a trava passar a olhar o **prefixo**.

---

## D1 · `UNKNOWN` promovido a `PROVED` — 346 itens, no eixo tempo

`_tempo()` (linha 87) devolve `PROVED` para qualquer valor que passe por `_sabido()`:

```python
def _tempo(item, campo, relativo=None):
    if _sabido(item.get(campo)):
        return 'PROVED', item[campo]
```

Resultado gravado em `data/passaporte/EVENTOS.jsonl`:

```
TIME_RESOLVED · TO_STATE=RELATIVE_ONLY · motivo normal        1.231
TIME_RESOLVED · TO_STATE=PROVED        · motivo normal        1.132
TIME_RESOLVED · TO_STATE=NOT_KNOWN     · motivo normal          406
TIME_RESOLVED · TO_STATE=PROVED        · motivo "NÃO SEI …"     346   ← defeito
```

Evento real:

```json
{"EVENT_TYPE": "TIME_RESOLVED", "TO_STATE": "PROVED",
 "REASON": "NÃO SEI — a rota devolve so tempo relativo",
 "RULE_VERSION": "PASSPORT-1.0"}
```

**O estado diz PROVADO e o motivo diz NÃO SEI, no mesmo evento.** Isto contradiz a própria
§6.4 do balanço anterior (*"Não promoveu `UNKNOWN` a estado"*) — que era verdadeira para os
casos que ela examinou, e falsa para este.

### Por que a geografia escapou, e por que isso **não** é consolo

O mesmo `_sabido()` guarda `FACT_LOCATION` (linha 186). Medido: **zero** eventos
`GEOGRAPHY_PROVED` com valor-sentinela. A geografia não escapou por ter guarda melhor —
escapou porque os caminhos de comentário e post passam `geo=None` fixo (linhas 268, 311) e
nunca chegam a ler `FACT_LOCATION`. Os 378 valores envenenados estão no acervo, intactos,
esperando o dia em que alguém ligar aquele campo naquele caminho.

**D1 é um defeito vivo. Na geografia, é um defeito latente.**

---

## D2 · Identidade ausente colapsa unidades distintas

`ITEM_ID = sha1(IDENTITY_BASIS)`. Quando `EXTERNAL_ID` é `"NÃO SEI"`, a base vira
`YOUTUBE:PROFILE:NÃO SEI` — **a mesma para todos**.

Medido:

```
linhas de origem distintas com EXTERNAL_ID = "NÃO SEI"     3
   SENSOR-PILOT/CANAIS-A.json  linha 70
   SENSOR-PILOT/CANAIS-B.json  linha  4
   SENSOR-PILOT/CANAIS-B.json  linha 26

ITEM_ID gerado para essas 3 linhas                          1   (ITEM-AE69E8E56B0B32E7)
eventos ITEM_CAPTURED nesse item                            3   → RECOLLECTED = 2
```

As três viraram **um item recoletado três vezes**. Não há prova de que sejam o mesmo canal —
há prova de que os três não têm identificador. `RECOLLECTED` passa a contar uma repetição
que talvez nunca tenha existido.

### Extensão da identidade inválida no acervo

Medido em 26 arquivos, com o censo percorrendo as listas **inteiras** (sem teto):

| campo | ocorrências | leitura |
|---|---:|---|
| `PERSON_ID` | 2.496 | **honesto** — são vídeos; a linha tem `EXTERNAL_ID` válido próprio |
| `ENTITY_ID` | 107 | risco de colapso — `CREATOR-MAP-EAME` |
| `EXTERNAL_ID` | 51 | **48 em transcrições · 3 em canais (o colapso acima)** |
| `ACCOUNT_HANDLE` | 12 | `COMPETITOR-PUBLIC-COMM` |
| `CONTENT_ID` | 1 | `CREATOR-CONTENT-CORPUS-EAME` |

> **`NÃO SEI` não é defeito por si.** Em `MEDICAO.json`, `PERSON_ID = "NÃO SEI"` em 1.071
> vídeos é a resposta correta: não sabemos quem filmou, e cada linha guarda o próprio
> `EXTERNAL_ID` válido. O defeito nasce só quando o campo ignorado **é a chave**.

### E a casa já tinha a trava certa — o passaporte é que não a usou

```python
# scripts/voz.py:77
SEM_ID_ESTRUTURAL = '__SEM_ID_ESTRUTURAL__'

# scripts/voz.py:106
if tem_id_estrutural(reg):
    return (reg.get('PLATFORM'), reg.get('EXTERNAL_ID'))
return (reg.get('PLATFORM'), SEM_ID_ESTRUTURAL, posicao)      # ← a POSIÇÃO entra na chave
```

Sem id, `voz.py` põe a **posição** na chave de dedupe: dois registros sem identificador
recebem chaves diferentes e **não colapsam**. É fail-closed correto, e já estava escrito.

O passaporte derivou `ITEM_ID = sha1(IDENTITY_BASIS)` sem esse desempate. **O defeito não
é falta de solução na casa — é a solução não ter sido herdada.** A correção é conhecida e
tem endereço.

---

## D3 · Universo parcial — 144.802 caracteres fora do passaporte

O passaporte foi construído sobre uma cópia do acervo que não continha três arquivos.

```
TRANSCRICOES-C.json   entrou no repo em  2026-09-02   commit 3cf38f2
TRANSCRICOES-D.json   entrou no repo em  2026-09-02   commit 3cf38f2
TRANSCRICOES-E.json   entrou no repo em  2026-09-02   commit e877123

branch do passaporte (ce6add1, 2026-09-05):  contém A e B apenas
origin/sintonia/canonical (10af4a7):         contém A, B, C, D e E
INVENTARIO do backfill (linhas 999-1000):    declara A e B apenas
```

Consequência medida:

```
registros de transcrição no acervo canônico          48
   com passaporte                                    15   (300.008 caracteres)
   SEM passaporte                                    33   (144.802 caracteres em 13 deles;
                                                           20 são REQUESTED_EMPTY, sem texto)
```

E a medição do próprio acervo já dizia o número certo:

```
SENSOR-PILOT/MEDICAO.json  →  TRANSCRIPTS_AVAILABLE = 28 · TRANSCRIPT_CHARS = 444810
canário do passaporte      →  30 transcrições        · 1.005.157 caracteres
```

### O portão não mentiu — e é por isso que o achado importa

Na branch onde o passaporte foi construído, `ACERVO_DECLARADO` estava **certo**: C, D e E
não existiam ali. O canário `1.005.157` era verdadeiro sobre aquele universo.

O defeito não é o portão. É que **o universo do passaporte é menor que o universo
canônico, e nada no artefato diz isso.** Um portão verde sobre um universo parcial tem
exatamente a mesma cara de um portão verde sobre o universo inteiro.

---

## D4 · O valor da dimensão não tem campo — ele mora em prosa

Chaves presentes em `EVENTOS.jsonl` (33.886 eventos, censo completo):

```
PRESENTES  ACTOR · EVENT_ID · EVENT_TYPE · EVIDENCE_REFERENCE · FROM_STATE · ITEM_ID
           REASON · RULE_VERSION · TIMESTAMP · TO_STATE · CAPTURED_AT · COLLECTION_ID
           CONTENT_TYPE · IDENTITY_BASIS · ITEM_CLASS · SOURCE_FAMILY · SOURCE_ID
           SOURCE_REFERENCE · DERIVED_FROM · PARENT_ITEM_ID · CLAIM_ID · CAPABILITY_ID
           RELEVANCE · CONTENT_CHARS · BLOCKER

AUSENTES   CROP · ISSUE · ISSUE_TYPE · COUNTRY · REGION · SUBREGION
           TIME_START · TIME_END · PROOF_STATE · OBSERVATION_STATE
           INDEPENDENCE_STATE · FAMILY_ID · LINEAGE_ID
           RELATIONSHIP_ID · CROSSING_ID · ADAMA_RELATION · PRODUCT_RELATION
```

O passaporte guarda **o estado da prova** de cada eixo, e **nunca o valor do eixo**.
`CROP_STATE = DECLARED` não diz qual cultura. O valor foi para `REASON`, que é texto livre:

```
CROP_DECLARED · DECLARED · reason='VINE'        145
CROP_DECLARED · DECLARED · reason="['VINE']"     43   ← mesma cultura, outra grafia
CROP_DECLARED · DECLARED · reason='OLIVE'       278
CROP_DECLARED · DECLARED · reason="['OLIVE']"    13   ← idem
CROP_DECLARED · DECLARED · reason='CEREAL'      136
CROP_DECLARED · DECLARED · reason="['CEREAL']"   29   ← idem
```

**`VINE` e `['VINE']` são a mesma videira gravada de duas formas dentro do artefato
canônico.** Um cruzamento que perguntasse *"mesma cultura?"* diria não.

> Este é, sozinho, o motivo pelo qual `FULL_BACKFILL` não pode ser recomendado: o schema
> atual não tem onde pôr a resposta das perguntas que os cruzamentos precisam fazer.

---

## D5 · A projeção arbitra conflito por recência

O log é append-only e isso está **provado**: 33.886 eventos, zero `EVENT_ID` repetido, zero
regressão não declarada, história preservada em 197 itens com dois ou mais selos de
identidade e 153 com dois ou mais selos de leitura.

Mas a dobra (`passaporte.py:509`) é:

```python
campo = ESCRITA[e['EVENT_TYPE']]
if campo and e['TO_STATE']:
    p[iid][campo] = e['TO_STATE']          # último selo vence, sempre
```

Conflito real, preservado no log e resolvido em silêncio na projeção:

```
ITEM-9636B5B466402AD2
  IDENTITY_PROVED     → PROVED       ator=scripts/voz.py
      "papel declarado pelo canal: COMPANY"          ev=YOUTUBE:UCL-MDKZ-_TvaR8MpgAhKZjA
  IDENTITY_NOT_PROVED → NOT_PROVED   ator=scripts/sensor_canal_identidade.py
      "veio da busca «repilo del olivo | …»"         ev=https://youtube.com/@SyngentaES
```

Dois atores discordam. A projeção fica com o **último escrito**, não com o mais forte, e
não existe estado que diga *"há conflito aqui"*. Nos 13 casos medidos a recência levou ao
lado seguro (`PROVED → NOT_PROVED`); isso foi **sorte de ordem**, não regra.

---

## D6 · Data de publicação vira tempo, sem dizer que tempo é

`_tempo()` é chamado com `PUBLICATION_DATE` (linhas 184, 233, 309) e `PUBLISHED_AT`
(linhas 391, 601, 657). Nos snapshots, com `CAPTURED_AT` (linha 842).

```
TIME_STATE = PROVED         1.478 itens
TIME_STATE = RELATIVE_ONLY  1.231 itens
TIME_STATE = NOT_KNOWN        406 itens
```

Não há defeito de honestidade: o campo se chama `TIME_STATE` e o contrato nunca prometeu
que fosse tempo do fato. O defeito é de **ambiguidade** — existe **um** eixo de tempo, e
ele não diz se é publicação, observação, captura ou vigência. Um cruzamento que perguntar
*"janela de tempo compatível?"* comparará datas de publicação achando que compara datas de
fato.

**Contraste, e ele é elogioso:** a geografia **tem** essa distinção, escrita motivo a
motivo no próprio log —

```
318  "nenhum lugar nomeado no texto — idioma não é lugar"
240  "COUNTRY_SCOPE é escopo da CONTA, não lugar do fato"
202  "país declarado pela própria origem; idioma não é país"
 99  "país da PESSOA procurada, não do fato"
```

A lei `SOURCE_LOCATION != FACT_LOCATION` já está aplicada por item. **A mesma disciplina
nunca foi aplicada ao tempo.**

---

## D7 · Três vocabulários de capacidade, nenhum mapa declarado

| vocabulário | quantos | dono | natureza |
|---|---:|---|---|
| `CAP-001` … `CAP-022` | 22 | `docs/capacidades/ATLAS-DE-CAPACIDADES-EAME.md` | capacidades como verbo |
| 10 `ÁREA ·` | 10 | `docs/ferramentas/ARQUITETURA-DE-INFORMACAO-EAME.md` | áreas de informação |
| 16 nomes | 16 | `CONTRATO-DO-PASSAPORTE.md §2.5` | destino de roteamento |

Onze dos dezesseis nomes do passaporte aparecem **zero vezes** no atlas de capacidades:
`OPPORTUNITY` · `EARLY_SIGNAL` · `PHYTOSANITARY` · `WINDOWS` · `COMPETITOR` · `SCIENCE` ·
`HUMAN_SENSORS` · `MARKET_DEVELOPMENT` · `MARKETING` · `SUPPLY` · `COUNTRY_CROP_PULSE` ·
`FUTURE_PLANNING` · `ASK_SINTONIA`.

Existe um mapa — **só em código**, sem documento:

```python
# scripts/passaporte_backfill.py:858
AREA_PARA_CAPACIDADE = {
    'REGULATORY': 'REGULATORY',        'MOLECULE': 'PORTFOLIO',
    'PEST & DISEASE': 'PHYTOSANITARY', 'SCIENCE & EXPERTS': 'SCIENCE',
    'CROPS & CLIMATE': 'COUNTRY_CROP_PULSE', 'COMPETITIVE': 'COMPETITOR',
    'MARKET': 'MARKET_DEVELOPMENT',    'DISTRIBUTION': 'COMMERCIAL',
    'FIELD VOICES': 'HUMAN_SENSORS',   'EVIDENCE & SOURCES': 'ASK_SINTONIA',
}
```

Ele cobre 10 dos 16 nomes. Cinco capacidades ficam **inalcançáveis** por qualquer rota
automática (`EARLY_SIGNAL`, `WINDOWS`, `MARKETING`, `SUPPLY`, `FUTURE_PLANNING`);
`OPPORTUNITY` é inalcançável **de propósito** e declarado. E `CAP-001…CAP-022` não é
referenciado em lugar nenhum do passaporte.

Roteamento realmente gravado: **84 eventos sobre 2.960 itens**.

```
OPPORTUNITY 36 (todos BLOCKED) · REGULATORY 19 · PHYTOSANITARY 9 · PORTFOLIO 6
COMPETITOR 6 · SCIENCE 5 · COUNTRY_CROP_PULSE 3
```

---

## D9 · A independência existe na casa, e **não entrou** no passaporte

> **Correção.** A primeira redação deste documento dizia que independência *não existia*.
> Está errado, e o censo derrubou. Ela existe, com dono, vocabulário e portão medido.

`LINEAGE_STATE` do passaporte (`ROOT` · `RESOLVED` · `BROKEN` · `UNKNOWN`) é **parentesco
de derivação**, não independência. Os motivos gravados provam a semântica:

```
991  "recostura por VIDEO_ID — o join da coleta procurou por URL e falhou"
671  "vídeo é raiz"          372  "post é raiz"
252  "vídeo é raiz; transcrição e comentário derivam dele"
202  "origem é raiz"         101  "item territorial é raiz"
```

Mas a independência **já tem dono**, fora do passaporte:

```
scripts/voz.py:50
    ORIGINALIDADE = ['ORIGINAL', 'RESHARE', 'SYNDICATED', 'UNKNOWN']

docs/regras/REGRA-DE-COLETA-EXTERNA-EAME.md:152
    "…independentes. Separar ORIGINAL · RESHARE · SYNDICATED · UNKNOWN."

docs/operacao/PORTOES-DE-COLETA-10B.md:22   ← e é MEDIDO, com portão PROVED
    VIDEO_ORIGINALITY = PROVED
    241 UNKNOWN · 9 SYNDICATED · 2 RESHARE — todos explícitos
    "RESHARE exige marca textual de republicação. SYNDICATED exige o mesmo título
     em canais DIFERENTES."
```

**O defeito real, então, é mais estreito e mais fácil de corrigir do que eu escrevi:**
o passaporte tem um eixo de linhagem que responde *parentesco* e **nenhum evento
transporta `VIDEO_ORIGINALITY` para dentro dele**. `INDEPENDENCE_STATE` não precisa ser
inventado — precisa ser **herdado** de `voz.py`, e estendido de vídeo para as outras
famílias, onde ainda não existe.

Enquanto não for transportado, nenhum cruzamento pode contar convergência a partir do
passaporte — só pode contar coincidência.

---

## D10 · Profundidade de leitura não é estado

```
CONTENT_SCANNED → LEXICALLY_SCANNED   2.121
CONTENT_READ    → READ                   22
TRANSCRIPT_READ → READ                    0   ← tipo de evento declarado, nunca emitido
```

O escopo da varredura está na prosa, não no estado:

> `"classificador lexical sobre título e descrição; texto: …"`

O eixo tem três valores e não distingue *li o título* de *li o corpo* de *li a
transcrição*. Os 22 `READ` são todos de registro/estatística
(`REGISTRY_PROJECTION`, `REGISTRY_DUMP`, `MONITORING_SERIES`, `STATISTICAL_SERIES`, …):
**nenhum vídeo, nenhum comentário e nenhuma transcrição foi lido.**

---

## 9 · O QUE EU ACHEI QUE ERA DEFEITO E NÃO ERA

Registrado porque achado contra o trabalho anterior tem de ter o mesmo padrão de prova que
achado a favor.

| hipótese minha | medição | veredito |
|---|---|---|
| *"As 48 transcrições do SENSOR-PILOT ficaram todas fora do passaporte"* | 15 estão dentro; 33 fora | **derrubada** — corrigido para 33 |
| *"`UNIT_COUNT` foi prometido no contrato e não existe no log"* | existe 29 vezes, dentro de `EVIDENCE_REFERENCE` como texto | **derrubada** — a promessa foi cumprida, de forma fraca (não é campo tipado, não é consultável como número) |
| *"O log tem colapso de identidade: uma base servindo vários itens"* | zero bases com mais de um `ITEM_ID` | **derrubada** — o colapso é o oposto: várias linhas de origem para **um** item (D2) |
| *"O raio de D8 são 893 valores em 6 campos"* | 1.312 em 46 campos | **derrubada pelo meu próprio script** — a primeira varredura truncava listas e somava só os arquivos que imprimia. O censo definitivo percorre as listas inteiras e soma todos os arquivos; a truncagem, se existir, passa a ser impressa |
| *"Independência entre fontes não existe em lugar nenhum"* | existe em `voz.py:50` (`ORIGINAL·RESHARE·SYNDICATED·UNKNOWN`), com regra em `REGRA-DE-COLETA-EXTERNA-EAME.md:152` e portão `VIDEO_ORIGINALITY = PROVED` medindo 241/9/2 | **derrubada** — D9 reescrito: o defeito é de **transporte** para o passaporte, não de ausência |
| *"Não há defesa contra colapso por identidade ausente"* | `voz.py:106` já põe a posição na chave quando não há id (`__SEM_ID_ESTRUTURAL__`) | **derrubada** — D2 reescrito: a trava existe e não foi herdada |
| *"Não existe distinção entre local da fonte e local do fato"* | `scripts/fato_local.py` (51 KB) é dono de `FACT_LOCATION` com precisão, âncora, gazetteer e três estados de **recusa** (`PLACE_MENTION_NOT_FACT`, `TERRITORIAL_LIST_NOT_FACT`, `NEGATED_OBSERVATION_NOT_FACT`), mais a migração `018_o_lugar_do_fato_ganha_dono.sql` | **derrubada** — existe, e é mais forte do que o passaporte |

E o que foi medido **a favor** do trabalho anterior, com a mesma régua:

- append-only **verdadeiro** — 33.886 eventos, zero `EVENT_ID` repetido, história preservada;
- `LEXICALLY_SCANNED` como estado próprio, que nunca satisfaz leitura — **a decisão mais
  acertada do contrato**, e ela sozinha já paga a missão anterior;
- `SOURCE_LOCATION != FACT_LOCATION` aplicado por item, com motivo escrito;
- `ORPHAN_INTELLIGENCE` como estado nomeado, e não como silêncio;
- `OPPORTUNITY` nascendo `BLOCKED`, de propósito e declarado;
- as quatro recusas de invenção da §6 do balanço — verificadas, e três delas verdadeiras.

---

## COMO REPRODUZIR

Todos os números acima saem de leitura pura sobre dois caminhos:

```
C:\eame-sintonia-passport       worktree em claude/passport-tags-italy-v1 (base: sintonia/canonical)
C:\eame-sintonia-passport-ref   worktree destacado em ce6add1 (PASSPORT-1.0)
```

Os scripts de medição desta missão vivem em `scripts/passaporte_censo.py` e não escrevem
nada — nem no acervo, nem no log de eventos.
