# CENSO DOS CAMPOS EXISTENTES — antes de inventar qualquer etiqueta

**Data:** 2026-09-06 · **Escopo:** `COUNTRY_SCOPE = ITALY` · **Somente leitura**
**Método:** 12 varreduras independentes do repositório + medição direta sobre o acervo e
sobre `EVENTOS.jsonl`. **855 campos** localizados, **174 conflitos**, **222 achados de dívida**.

> **A pergunta deste censo não é *"que campos devemos criar?"*. É *"o que já existe, com
> que nome, e quem é o dono?"*** — porque criar um segundo dono para um campo que já tem
> dono é o defeito mais caro desta arquitetura, e o mais fácil de cometer.

---

## O ACHADO PRINCIPAL

**Quase nada precisa ser inventado. Quase tudo precisa ser transportado.**

O Sintonia EAME já tem, espalhados por regras, scripts e portões, os campos que os
cruzamentos futuros vão precisar — e vários deles são **mais fortes** que o equivalente
dentro do Passaporte. O que não existe é o **transporte** desses campos para o passaporte,
e um lugar declarado onde eles convivam.

| | |
|---|---:|
| conceitos-alvo do passaporte universal | 31 |
| já existem com dono canônico fora do passaporte | **19** |
| existem só como estado, sem o valor | 6 |
| existem em dois ou mais vocabulários que não conversam | 7 |
| realmente ausentes em todo o repositório | **4** |

---

## 1 · JÁ EXISTE, COM DONO — não criar nome novo

| conceito | nome canônico | dono | vocabulário |
|---|---|---|---|
| `FACT_LOCATION` | `FACT_LOCATION` + `_PRECISION` + `_EVIDENCE` + `_ANCHOR` + `_ORIGIN` | `scripts/fato_local.py` | `GAZETTEER` · `DECLARED_BY_TEXT` · `DOCUMENT_SCOPE` |
| recusa de lugar | 3 estados de recusa | `scripts/fato_local.py:118` | `PLACE_MENTION_NOT_FACT` · `TERRITORIAL_LIST_NOT_FACT` · `NEGATED_OBSERVATION_NOT_FACT` |
| `ENTITY_LOCATION` | `origem_lugar.papel` | `supabase/migrations/018_o_lugar_do_fato_ganha_dono.sql` | `BASE` · `OPERATING` · `INFLUENCE` |
| **`INDEPENDENCE_STATE`** | `ORIGINALIDADE` / `VIDEO_ORIGINALITY` | `scripts/voz.py:50` · regra em `REGRA-DE-COLETA-EXTERNA-EAME.md:152` | `ORIGINAL` · `RESHARE` · `SYNDICATED` · `UNKNOWN` |
| identidade sem id (fail-closed) | `SEM_ID_ESTRUTURAL` + posição na chave | `scripts/voz.py:77,106` | `__SEM_ID_ESTRUTURAL__` |
| `CROP` (modelo completo) | `CROP_ALL` · `CROP_PRIMARY` · `CROP_CARDINALITY` · `CROP_RESOLUTION_STATE` · `CROP_EVIDENCE` | `docs/regras/POLITICA-CANONICA-DE-CROP.md` (`CROP-D1-2026-09-05`) | `NONE·SINGLE·MULTI` / `RESOLVED·AMBIGUOUS·UNKNOWN·NO_CROP·ERROR` |
| `ISSUE_TYPE` | `ISSUE_TYPE` / `categoryOf()` | `italia-portale/client/italy-app-model.js` | `PEST` · `DISEASE` · `WEED` · `unknown` |
| `ISSUE` (taxonomia) | `ISSUE_ID` + `DONO_DA_TAXONOMIA` | `data/samples/IT-ROTULOS-V1/IT-VOCAB-HANDOFF-V1.json` | `ISSUE_SMUT` · `ISSUE_SCAB` · `ISSUE_DOWNY_MILDEW` … |
| `CLAIM_TYPE` | `FACT` · `INTERPRETATION` · `ACTION` | `docs/regras/REGUA-DE-ALERTA-EAME.md` | fechado |
| `CLAIM_TYPE` (comentário) | 5 tipos de fala de campo | `docs/regras/REGRA-DE-COLETA-EXTERNA-EAME.md` | `FIELD_OBSERVATION` · `TECHNICAL_QUESTION` · `PRODUCT_QUESTION` · `PROBLEM_REPORT` · `TECHNICAL_DISCUSSION` |
| `CLAIM_TYPE` (mudança) | `CHANGE_TYPE` | `docs/regras/REGUA-DE-CHANGE-EVENT-EAME.md` | 6 tipos de mudança de registro |
| `PROOF_STATE` (embrião) | `EVIDENCE_CLASS` | acervo, 90 arquivos | `PRIMARY_SOURCE_RAW` · `PRIMARY_SOURCE_PROBE` · `OFFICIAL_DOCUMENT` · `OFFICIAL_STATISTIC` · `SCIENTIFIC_LITERATURE` · `REGULATORY_FACT` · `DERIVED_INTERPRETATION` · `DERIVED_SCOPE` · `DERIVED_MEASUREMENT` · `DERIVED_IDENTITY` |
| `PROOF_STATE` (por campo) | tabela *"Qualidade de fonte, declarada campo a campo"* | `docs/regras/MODELO-DE-IDENTIDADE-EAME.md` | `PRIMÁRIA` · secundária |
| `ENTITY_ID` (7 papéis) | `REGISTRATION_ID` · `REFERENCE_PRODUCT` · `REFERENCE_HOLDER` · `MANUFACTURER` · `MANUFACTURING_SITE` · `COMMON_DENOMINATION` · `CONCESSIONAIRE` | `docs/regras/MODELO-DE-IDENTIDADE-EAME.md` | **nunca colapsar** |
| `ENTITY_ID` (tipo) | `ENTITY_KIND` | `scripts/creators.py` | `PERSON_CREATOR` · `FARM_BUSINESS` · `FARMER_FAMILY_ACCOUNT` · `MEDIA_ACCOUNT` · `ORGANIZATION` · `OTHER` |
| `CROSSING_ID` | `X-###` · `IT-X-ANO-NNN` | `docs/fontes/ATLAS-DE-FONTES-EAME.md` · `scripts/it_cruzamentos.py` | `X-001` · `X-003` … |
| `CROSSING` (tipo) | `CROSSING_TYPE` | `data/samples/IT-CRUZAMENTO-V1/IT-CRUZAMENTOS-V1.json` | `FIELD_BULLETIN x PUBLIC_VOICE_TRANSCRIPT x ADAMA_LABEL_PAIR` … |
| `CROSSING` (veredito) | `LEADS` · `COINCIDES` · `LAGS` · `NO_RELIABLE_SIGNAL` | `docs/regras/REGRA-DE-COLETA-EXTERNA-EAME.md` | fechado |
| `ADAMA_RELATION` | `ADAMA_RELATION` | `scripts/it_cruzamentos.py` | `LINHA_DA_TABELA` · `BLOCO_DA_CULTURA` · `DECLARACAO_DE_PRODUTO` · `SUBSTANCIA_ATIVA` |
| `SOURCE_FAMILY` | `SOURCE_FAMILY` | `CONTRATO-DO-PASSAPORTE.md §1.2` | 8 famílias |
| `EVIDENCE_POINTER` | `EVIDENCE_REFERENCE` · `RAW_EVIDENCE_PATH` · `RAW_HTML_PATH` | passaporte · `POLITICA-CANONICA-DE-RAW.md` | — |

---

## 2 · EXISTE SÓ O ESTADO, NUNCA O VALOR

No Passaporte, seis eixos guardam *quão provado está* e **não guardam o quê**.

| eixo | o que o passaporte guarda | onde o valor foi parar |
|---|---|---|
| `CROP_STATE` | `DECLARED` · `NOT_KNOWN` · … | `REASON`, texto livre |
| `ISSUE_STATE` | idem | `REASON`, texto livre |
| `GEOGRAPHY_STATE` | `PROVED` · `NOT_KNOWN` · … | `EVIDENCE_REFERENCE` |
| `TIME_STATE` | `PROVED` · `RELATIVE_ONLY` · … | `REASON` |
| `IDENTITY_STATE` | `PROVED` · `PLAUSIBLE` · … | `IDENTITY_BASIS`, string composta |
| `CLAIM_STATE` | `EXTRACTED` · … | `REASON` |

**A consequência é aritmética, não retórica.** O mesmo valor aparece em duas grafias
dentro do artefato canônico:

```
'VINE'      145        vs   "['VINE']"     43
'OLIVE'     278        vs   "['OLIVE']"    13
'CEREAL'    136        vs   "['CEREAL']"   29
'DURUM_WHEAT' 73       vs   "['DURUM_WHEAT']" 2
```

Dos 97 eventos gravados com colchete, **87 são uma cultura só serializada como lista** e
apenas **10 são multi-cultura de verdade** (`['CEREAL','VINE']` 6, `['OLIVE','CEREAL','VINE']` 3,
`['OLIVE','VINE']` 1). Um cruzamento que perguntasse *"mesma cultura?"* perderia 87 itens
por grafia e teria de fazer *parsing de repr de Python* nos outros 10.

**A `POLITICA-CANONICA-DE-CROP.md` já resolveu isso** — `CROP_ALL` + `CROP_CARDINALITY`
tornam `MULTI` um estado normal, não uma string. As duas peças foram escritas **no mesmo
dia, 2026-09-05, em branches diferentes**, e não se conhecem.

---

## 3 · CONFLITOS — o mesmo conceito com vocabulários que não conversam

### 3.1 · Capacidade — três listas, um mapa escondido

| lista | tamanho | dono |
|---|---:|---|
| `CAP-001` … `CAP-022` | 22 | `docs/capacidades/ATLAS-DE-CAPACIDADES-EAME.md` |
| `ÁREA ·` (REGULATORY, MOLECULE, PEST & DISEASE, …) | 10 | `docs/ferramentas/ARQUITETURA-DE-INFORMACAO-EAME.md` |
| `CAPABILITY_ID` (OPPORTUNITY, EARLY_SIGNAL, …) | 16 | `CONTRATO-DO-PASSAPORTE.md §2.5` |

Treze dos dezesseis nomes do passaporte aparecem **zero vezes** no atlas de capacidades.
O único mapa existente vive em código, sem documento — `passaporte_backfill.py:858`,
`AREA_PARA_CAPACIDADE`, ligando 10 áreas a 10 capacidades. Cinco capacidades ficam
inalcançáveis por qualquer rota (`EARLY_SIGNAL`, `WINDOWS`, `MARKETING`, `SUPPLY`,
`FUTURE_PLANNING`) e `OPPORTUNITY` é inalcançável **de propósito**, declarado.

**Recomendação:** `ATLAS-DE-CAPACIDADES-EAME.md` é o dono canônico. O mapa
`ÁREA → CAPABILITY_ID → CAP-###` precisa sair do código e virar documento.
Esta missão **não** cria capacidade nova; onde não houver mapa, `UNKNOWN_CAPABILITY`.

### 3.2 · Duas grafias para o mesmo valor

| campo | grafia A | grafia B | onde |
|---|---|---|---|
| `EVIDENCE_CLASS` | `OFFICIAL_DOCUMENT` (2.030) | `DOCUMENTO_OFICIAL` (2.030) | `IT-RADAR-V21` vs `IT-ROTULOS` — um arquivo cada, uma língua cada |
| `CROP` (chave) | `CROP` — `VINE`/`OLIVE`/`CEREAL` | `crop` — `C1110`/`VITE`/`OLIVO`/`olivo` | maiúscula/minúscula, inglês/italiano/código |
| ausência | `NÃO SEI` (2.673 em `CROP`) | `NOT_KNOWN` (451 em `CROP`) | **mesmo campo, duas sentinelas** |
| ausência | `NÃO SEI` (473 em `COUNTRY_OF_FACT`) | `NOT_KNOWN` (5.642) | idem |

### 3.3 · Famílias — dois vocabulários concorrentes

```
scripts/v2_dedup_e_familias.py       10 famílias SEMÂNTICAS
    CURRENT_FIELD_SIGNALS · MARKET_OBSERVATIONS · CROP_ECONOMIC_WEIGHT · …

scripts/it_acervo_inventario_v2.py   13 famílias por REGEX DE CAMINHO
    RADAR_FUTURO · ROTULOS_PORTFOLIO · SINAIS_DE_CAMPO · FITOSSANITARIO · …
```

Família por significado e família por caminho de arquivo são coisas diferentes com o mesmo
nome. Nenhuma das duas é `SOURCE_FAMILY` do passaporte (8 famílias de **rota de coleta**).
São **três** eixos chamados "família".

### 3.4 · Valor e motivo no mesmo campo

```
REGION = "NÃO SEI — a afiliação não declara região no registro"
DATE   = "NÃO SEI — a rota devolve so tempo relativo"
```

O hábito é bom — dizer *por que* não se sabe. O lugar é errado: valor e motivo no mesmo
campo derrotam qualquer trava de igualdade, e **derrotaram** (`PASSPORT-DEFEITOS-HERDADOS.md`,
D8: 1.312 valores, 46 campos). O motivo precisa de campo próprio (`*_EVIDENCE`,
que `fato_local.py` e `POLITICA-CANONICA-DE-CROP.md` já fazem certo).

---

## 4 · REALMENTE AUSENTE — aqui, e só aqui, se cria nome novo

| conceito | busca feita | veredito |
|---|---|---|
| **`OBSERVATION_STATE`** (observado × modelado × inferido × cenário × proxy) | `grep` em `docs/`, `scripts/`, `data/`; `OBSERVATION_TYPE` existe mas é *tipo de comunicação* (`FIELD_OBSERVATION`, `TECHNICAL_ALERT`, `REGULATORY_UPDATE`) e é `OTHER` em 96 de 114 casos | **AUSENTE** — nada distingue *"modelo prevê risco"* de *"doença observada"* |
| **`PROOF_STATE`** como eixo único e comparável | existem 3 vocabulários por dimensão que **não se comparam** (`IDENTITY_STATE` 5 valores, `GEOGRAPHY_STATE` 4, `TIME_STATE` 4) e um `CONFIDENCE` livre | **AUSENTE** — ver 4.1 |
| **`RELATIONSHIP_ID`** | zero ocorrências no passaporte; `CROSSING_ID` existe, relação binária provada não | **AUSENTE** |
| **`UNKNOWN_FIELDS`** | zero ocorrências | **AUSENTE** — não há lista de *quais* campos ficaram desconhecidos por item |

### 4.1 · `CONFIDENCE` é a escala vaga que a missão proíbe — e quem a escreveu já sabia

```
HIGH    326        MEDIUM   70        LOW    2
NONE    148        None     13
```

E oito valores de texto livre, que são a coisa mais informativa do campo:

```
"HIGH para a Andaluzia · NÃO SEI para o resto da Espanha"
"HIGH para a contagem · LOW para qualquer leitura de mercado"
"HIGH_ON_PROVENANCE_UNREAD_ON_CONTENT"
"MEDIUM — depende de vocabulário controlado"
```

**Quem escreveu isso estava lutando contra o próprio campo.** Um escalar não cabe a
resposta, porque a força da prova **é por eixo**, não por item — que é exatamente a FASE 7
desta missão. `CONFIDENCE` não deve ser normalizado: deve ser **substituído** por
`PROOF_STATE` por eixo, e os oito textos livres são a especificação de aceitação.

---

## 5 · O QUE ESTE CENSO NÃO ALCANÇOU

Declarado para que a ausência de medida não vire ausência de problema.

- `scripts/` tem 244 arquivos; a varredura leu integralmente ~20 e usou `grep` no resto.
- `data/` tem 960 arquivos; o censo de chaves cobriu os `.json`/`.jsonl` legíveis e
  **percorreu as listas inteiras**, mas não leu conteúdo de texto.
- `italia-portale/` (165 arquivos) foi lido por `grep` de nomes de campo, não integralmente.
- `build/` foi deliberadamente **excluído** — é saída, não fonte.
- Nada de `IT-ROTULOS*` foi analisado como conteúdo: é Label Intelligence, **fora do escopo
  desta missão** por regra explícita. Aparece aqui só como *dono de vocabulário de `ISSUE_ID`*.
