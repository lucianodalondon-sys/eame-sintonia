# C10.3 · PLATAFORMA NÃO É LOCALIZAÇÃO

```
MEDIDO_EM      = 2026-09-11
C10_3_LOCATION = PASS
INSTAGRAM_AUDIO_ONLY = PROVEN  (não regrediu)
```

> Evidência de missão. Não é Bíblia, não é MASTER, não substitui contrato.

---

## A · O DEFEITO

`_ficha_raw()` fazia:

```python
SOURCE_LOCATION = ident.get('PLATFORM', NAO_SEI)      # → INSTAGRAM
```

E produzia `SOURCE_LOCATION = INSTAGRAM`, que é semanticamente impossível: o
Instagram é um sistema onde a publicação existe, não um sítio no mundo onde a
fonte está.

O mais duro é que o comentário **imediatamente acima daquela linha** já dizia a
lei certa: *«ONDE A FONTE ESTÁ != ONDE O FATO ACONTECEU»*.

```
CONTRACT_TEXT != IMPLEMENTATION. O comentário não corrige o código.
```

---

## B · A CASA JÁ TINHA DECIDIDO ISTO — QUATRO VEZES

O censo encontrou a mesma lei escrita em quatro módulos vizinhos, e a cadeia de
Reel era a única que não obedecia:

| autoridade | o que diz |
|---|---|
| `coleta/youtube_oficial.py` | *«`regionCode` e `relevanceLanguage` moldam o RANKING. Eles NÃO provam que o autor está na Itália — por isso o objeto sai com `SOURCE_LOCATION=UNKNOWN` mesmo com `regionCode=IT`»* |
| `coleta/social_envelope.py` | *«`LANGUAGE=it` e `SOURCE_LOCATION=IT` são campos DIFERENTES e nenhum dos dois é derivado do outro… LÍNGUA ITALIANA NÃO PROVA ITÁLIA. `UNKNOWN` É MAIS BARATO QUE ERRADO»* |
| `coleta/golden_path_pdf.py` | *«não se põe `fact_location` a partir de `COUNTRY_SCOPE`»* |
| `coleta/social_scrap.py` | *«COUNTRY_SCOPE=IT É O QUE EU PEDI. NÃO É O QUE EU PROVEI»* |

---

## C · CENSO

### PRODUTORES do contrato tipado — um só, e era o defeito

| ficheiro | papel | veredito |
|---|---|---|
| `ferramentas/reel_transcricao.py:705` | **PRODUCER** | **o defeito** — corrigido aqui |
| `leis/artefato.py:283-284` | **TRANSPORTER** | `derivado_de` herda do pai; não deriva |

Nenhum outro passa `SOURCE_LOCATION=` a um `Artefato`.

### CONSUMIDORES

| ficheiro | papel | nota |
|---|---|---|
| `provas/o_encanamento_tem_uma_porta.py:120` | **JUDGE** | já prova que `ingresso.ficha` não inventa `FACT_LOCATION` |
| `admissao/admissao.py:522-523` | **TRANSPORTER** | lê `source_location`/`fact_location` do item; não deriva |
| `coleta/social_scrap.py:180` | **CONSUMER** | conta objetos por `SOURCE_LOCATION` — **de envelope social**, não da ficha de Reel; não foi afetado |
| `leis/artefato.py:330` | **JUDGE** | valida `FACT_LOCATION` quando declarado |

### DÍVIDA REGISTADA, E NÃO CORRIGIDA

Há uma segunda população que põe nomes de plataforma em `SOURCE_LOCATION`:
`medidas/voz.py` (`'plataforma global'`), `regras/sensor_coleta.py`
(`'YouTube'`, `'LinkedIn e YouTube'`, `'Apify'`), `superficie/rede.py`
(`'interno'`).

São **cabeçalhos de artefato de auditoria**, não instâncias do contrato tipado —
outra espécie de objeto, com outro dono. A §4 manda registar e não ampliar, e é
o que fica feito.

---

## D · O QUE MUDOU

```python
SOURCE_LOCATION = _ou(ident.get('SOURCE_LOCATION'), NAO_SEI)
FACT_LOCATION   = _ou(ident.get('FACT_LOCATION'),   NAO_SEI)
NOTES['PLATFORM'] = ident.get('PLATFORM', NAO_SEI)
```

Cada eixo transporta só a **sua** evidência. O normalizador é o `_ou` que o
próprio módulo já usava para `PUBLISHED_AT` — reusado, não reinventado.

**A plataforma saiu de `SOURCE_LOCATION`, não foi apagada.** Mudou para as
notas, ao lado do `POST_ID`, que é o outro metadado de plataforma. A ficha
continua a responder «de qual plataforma veio?». O dono do conceito continua a
ser `coleta/social_envelope.py`, que dedupla por `PLATFORM + NATIVE_ID`.

---

## E · OS CASOS, EXECUTADOS

| caso | PLATFORM | COUNTRY_SCOPE | SOURCE_LOCATION | FACT_LOCATION |
|---|---|---|---|---|
| **A** plataforma + escopo, sem geografia | INSTAGRAM | IT | `NAO SEI` | `NAO SEI` |
| **B** `SOURCE_LOCATION` provado | INSTAGRAM | IT | **IT** | `NAO SEI` |
| **C** fonte IT, facto ES provado | INSTAGRAM | `NAO SEI` | **IT** | **ES** |
| **D** conta «Syngenta Italia» | INSTAGRAM | `NAO SEI` | `NAO SEI` | `NAO SEI` |
| **E** só `COUNTRY_SCOPE=IT` | INSTAGRAM | IT | `NAO SEI` | `NAO SEI` |
| **F** idioma italiano declarado | INSTAGRAM | IT | `NAO SEI` | `NAO SEI` |
| **G** URL com `/it/` | INSTAGRAM | `NAO SEI` | `NAO SEI` | `NAO SEI` |

O caso **C** é o que a Bíblia usa: uma revista italiana noticia uma praga
espanhola. Os dois campos ficam diferentes, e é por isso que são dois campos.

E o caso **B** carrega a regra que a §12 exige: **provar onde a fonte está nunca
prova onde o facto aconteceu.**

---

## F · O REEL REAL

Sem descoberta nova, sem rede, sobre a sentinela que a casa já conhece:

```
PLATFORM         INSTAGRAM
COUNTRY_SCOPE    NAO SEI
SOURCE_LOCATION  NAO SEI
FACT_LOCATION    NAO SEI
SOURCE_ID        NAO SEI
SOURCE_URL       https://www.instagram.com/reel/C-63RfHoJTU/
POST_ID          C-63RfHoJTU
MEDIA_KIND       AUDIO
ARTIFACT_ID      RAW-290e577995b09a62
```

Medido: `identidade_do_url` **não traz campo de geografia nenhum**. Zero. Se a
cadeia enchesse `SOURCE_LOCATION`, seria do nada.

```
NENHUMA GEOGRAFIA É PASS, NÃO É FALHA.
```

---

## G · RED TEAM — sete mutações, sete quedas

| # | mutação | resultado |
|---|---|---|
| 1 | **`SOURCE_LOCATION = PLATFORM`** (obrigatória) | **FAILED** (12 testes) |
| 2 | **`FACT_LOCATION = SOURCE_LOCATION`** (obrigatória) | **FAILED** (3) |
| 3 | `COUNTRY_SCOPE` vira `SOURCE_LOCATION` | **FAILED** |
| 4 | `COUNTRY_SCOPE` vira `FACT_LOCATION` | **FAILED** |
| 5 | o nome da conta vira localização | **FAILED** |
| 6 | o idioma vira localização do facto | **FAILED** |
| 7 | a plataforma desaparece das notas | **FAILED** (2) |

A sétima existe porque corrigir não pode custar informação: se `PLATFORM`
sumisse da ficha, a correção teria trocado uma mentira por um buraco.

Os testes medem o **objeto produzido**, nunca o texto do ficheiro — uma
sentinela ancorada no texto mede o texto, não a lei.

---

## H · O QUE NÃO REGREDIU

| frente | prova |
|---|---|
| **Áudio-only (C10)** | ao vivo, dois Reels: `VIDEO_STREAMS = 0`, `AUDIO_STREAMS = 1`, `VIDEO_BYTES_DOWNLOADED = 0`, transcript com pai `RAW-cbe61ce32241a744`. `PROVEN` |
| **`SOURCE_ID` (C10.1)** | nunca nasce de URL; sem prova fica no sentinela |
| **Origin gate (C10.2)** | 32 testes das duas suítes, `OK` |

E não se tocou em `yt-dlp`, seletor, ASR, GPU, modelo, fallback, Facebook,
LinkedIn, YouTube, X, portal, Collection nem Supabase.

---

## I · REGRESSÃO

| momento | testes | falhas |
|---|---:|---:|
| baseline | 341 | 10 |
| depois, com os 18 novos | 359 | **10** |

O conjunto de falhas é **idêntico**: cinco de `test_evidence` e cinco de
`test_proveniencia`, entulho anterior já contado desde a C9.

```
NEW_FAILURES     = 0
SYSTEM_MAP_CHECK = PASS
```

---

## J · PARENT_GATE_DEBT

```
PARENT_GATE_DEBT = CONFIRMED
```

Reproduzida só por leitura, como a §18 manda, e **não corrigida**:

```
parent_artifact_id = "NAO_SEI"  →  NAO_SEI   (apanhado)
parent_artifact_id = "NAO SEI"  →  SIM       (passa)
```

E `artefato.NAO_SEI` é exatamente `"NAO SEI"`, com espaço — a grafia que passa.

---

## K · DESCONHECIDO

- se algum Reel traz geografia declarada pela plataforma (nenhum dos medidos traz);
- de onde viria um `SOURCE_LOCATION` provado para uma conta de Instagram;
- quantas amostras publicadas carregam `SOURCE_LOCATION` com nome de plataforma
  da população de auditoria.

---

## L · RISCO RESTANTE

1. **`_ou` normaliza quatro grafias, não seis.** Ele apanha `None`, `''`,
   `NOT_KNOWN` e `NAO SEI`; deixa passar `NAO_SEI` com sublinhado e `UNKNOWN`.
   Não é mentira — as duas continuam confissões que `_identifica` recusa — mas é
   grafia misturada no mesmo campo. Alargá-lo mudaria também `PUBLISHED_AT`, que
   esta missão não mediu.
2. **`PARENT_GATE_DEBT`**, acima.
3. **A população de auditoria** continua a escrever nomes de plataforma em
   `SOURCE_LOCATION`. Outro dono, outra espécie de objeto.
4. **A cadeia continua sem atravessar o portão canônico de rotas.**

---

## M · VEREDITO

```
C10_3_LOCATION       = PASS
INSTAGRAM_AUDIO_ONLY = PROVEN
NEW_FAILURES         = 0
SYSTEM_MAP_CHECK     = PASS
PARENT_GATE_DEBT     = CONFIRMED (registada, não corrigida)
KNOW_HOW_DELTA       = NENHUM
BÍBLIA/CONTRATO      = NÃO precisa mudar

PRÓXIMO PASSO MÍNIMO = ligar a capacidade Instagram audio-only
                       ao portão canônico de rotas

HARD STOP.
```

`KNOW_HOW_DELTA = NENHUM`: as leis `SOURCE_LOCATION != FACT_LOCATION` e
`COUNTRY_SCOPE != SOURCE_LOCATION` já existem, e estavam escritas em quatro
módulos. O que houve foi uma implementação a contradizer o comentário que tinha
por cima. Corrigir uma violação de lei conhecida não é aprendizado novo.
