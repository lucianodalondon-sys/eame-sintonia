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
