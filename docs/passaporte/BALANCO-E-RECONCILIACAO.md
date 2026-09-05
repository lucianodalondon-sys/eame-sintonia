# BALANÇO E RECONCILIAÇÃO DO ACERVO — o estado real antes do Passaporte

**Data:** 2026-09-05 · **Somente leitura.** Nenhuma coleta foi feita para produzir este
balanço, nenhum ator foi executado, nenhum centavo foi gasto.

> A missão do Passaporte só podia começar depois disto. O que segue é o que o acervo
> **era** em 2026-09-05, medido arquivo a arquivo — não o que ele deveria ter virado.

---

## 1 · O QUE EXISTE

| granularidade | unidades | o que é |
|---|---|---|
| **CONTENT** | 2.608 | vídeos, comentários, posts, transcrições, boletins territoriais |
| **ORIGIN_CANDIDATE** | 323 | perfis, canais e contas coletados para provar identidade |
| **DATASET_SNAPSHOT** | 29 | registros oficiais, séries estatísticas e corpora científicos |
| **TOTAL** | **2.960** | unidades de informação no acervo |

Por coleção:

| COLLECTION_ID | unidades | composição |
|---|---|---|
| `EARLY_SIGNAL_EAME` | 1.409 | 383 vídeos · 912 comentários · 15 transcrições · 99 candidatos |
| `VOICE_ES` | 1.187 | 252 vídeos · 346 comentários · 372 posts · 15 transcrições · 202 origens |
| `YOUTUBE_JANELA` | 240 | 240 vídeos da grade pública |
| `TERRITORIAL` | 73 | 62 entradas de listagem · 11 corpos de boletim |
| `ACERVO_BASE` | 29 | snapshots de registro, estatística e ciência |
| `COMPETITOR_PUBLIC_COMM` | 22 | contas com identidade congelada |

E **185 arquivos** do acervo classificados, **0 sem classificação declarada**.

---

## 2 · O INCIDENTE, MEDIDO

```
TRANSCRIÇÕES NO ACERVO         30 objetos
CARACTERES                  1.005.157
    ES-T8-001                 705.149   15 transcrições, rota paga
    SENSOR-PILOT              300.008   15 transcrições, rota paga
LIDOS POR ALGUM PROCESSO            0
```

**O número fecha exatamente.** Ele não era desconhecido: `ES-T8-001-transcricoes.json`
declara `TOTAL_CHARS: 705149` e `SENSOR-PILOT/MEDICAO.json` declara
`TRANSCRIPT_CHARS: 300008`. Os dois estavam publicados, e nenhum dos dois estava errado.

**O que não existia era a pergunta.** Nenhum campo do repositório dizia se aquele texto
tinha sido lido. Ausência de selo e reprovação tinham exatamente a mesma cara: nenhuma.

### O classificador tocou o texto — e isso não é leitura

`scripts/sensor_medir.py::medir()` passa a transcrição para `classificar_conteudo()` e
para `lugar_do_fato()`. Um classificador **lexical** varreu 1.966 itens do acervo.

Ele conta como `LEXICALLY_SCANNED`, um selo mais fraco, e o contrato proíbe que ele vire
`READ` — **nunca**. O próprio artefato já dizia por quê:

> *"lexical. Polissemia produz falso positivo e nenhum portão automático detecta isso."*
> — `SENSOR-PILOT/MEDICAO.json`, `LIMITE_DO_CLASSIFICADOR`

Tratar varredura como leitura teria zerado a dívida no papel e deixado 1.005.157
caracteres exatamente onde estavam.

---

## 3 · O QUE A IDENTIDADE GLOBAL REVELOU — e ninguém sabia

Dar a cada unidade um `ITEM_ID` derivado de uma chave **global** (plataforma + id externo),
e não do arquivo em que ela mora, expôs uma coisa que nenhuma contagem anterior podia ver:

```
MESMO VÍDEO COLETADO POR DUAS MISSÕES        48
MESMO COMENTÁRIO COLETADO POR DUAS MISSÕES   79
MESMA ENTRADA TERRITORIAL EM DOIS LOTES      26
MESMO VÍDEO REPETIDO DENTRO DO LOTE B         9
DUPLICATAS ENTRE PERFIS                       2
                                            ---
REENCONTROS                                 164 itens, 167 capturas repetidas
```

Os 48 vídeos e os 79 comentários foram comprados **duas vezes**: uma pela rodada
espanhola `ES-T8-001` e outra pelo piloto de sensores `SENSOR-PILOT`. As duas missões
mediram os próprios números corretamente. Nenhuma das duas podia saber da outra, porque
a identidade de um vídeo era a linha do arquivo onde ele estava.

**O reencontro não vira item novo.** O `ITEM_ID` é o mesmo, o histórico ganha um segundo
`ITEM_CAPTURED` e `RECOLLECTED` sobe. Contar 2 seria inventar informação que não existe;
esconder o segundo seria perder a única prova de que se pagou duas vezes.

---

## 4 · ONDE O ACERVO REALMENTE ESTÁ

Contabilidade por estágio, derivada — quem entra num estágio é exatamente quem passou no
anterior:

| estágio | entrada | passou | parou com motivo | pendente | erro |
|---|---:|---:|---:|---:|---:|
| CAPTURE | 2.960 | 2.960 | 0 | 0 | 0 |
| NORMALIZATION | 2.960 | 2.954 | 0 | 6 | 0 |
| DEDUP | 2.954 | 2.954 | 0 | 0 | 0 |
| CONTENT_ACQUISITION | 2.954 | 2.024 | 67 | 863 | 0 |
| **INTELLIGENCE_READING** | **2.024** | **16** | **0** | **2.008** | **0** |
| CLAIM_EXTRACTION | 16 | 16 | 0 | 0 | 0 |
| ROUTING | 16 | 12 | 0 | 4 | 0 |
| CONSUMPTION | 12 | 12 | 0 | 0 | 0 |

**O gargalo tem nome e endereço: `INTELLIGENCE_READING`.** 2.008 unidades com conteúdo
disponível e não lido — 99,2% de tudo o que chegou até lá.

Ciclo de vida, e ele fecha:

```
TOTAL_ENTERED  2.960
   ACTIVE      1.993
   DEFERRED      930   ← conteúdo não pedido ou vazio; DEFER não é reprovação
   REJECTED       25   ← homônimos declarados, com evidência por item
   COMPLETED      12
   ERROR           0
```

Motivo de parada, por item — **nenhum item parou em silêncio**:

| REASON_CODE | itens |
|---|---:|
| `CONTENT_NOT_PROCESSED` | 1.983 |
| `TRANSCRIPT_PENDING` | 863 |
| `CONTENT_NOT_AVAILABLE` | 67 |
| `FALSE_POSITIVE` | 25 |
| `NORMALIZATION_PENDING` | 6 |
| `NOT_ROUTED` | 4 |
| — (concluído) | 12 |

---

## 5 · O QUE O ACERVO PROVA, CAMPO A CAMPO

| campo | distribuição |
|---|---|
| `RAW_STATE` | PRESERVED 2.625 · NOT_PRESERVED 335 |
| `CONTENT_STATE` | AVAILABLE 2.030 · NOT_TESTED 863 · ABSENT 62 · REQUESTED_EMPTY 5 |
| `CONTENT_READ_STATE` | LEXICALLY_SCANNED 1.966 · NOT_READ 972 · **READ 22** |
| `IDENTITY_STATE` | NOT_PROVED 2.294 · PROVED 624 · NOT_APPLICABLE 30 · PLAUSIBLE 12 |
| `GEOGRAPHY_STATE` | NOT_KNOWN 2.427 · PROVED 533 |
| `TIME_STATE` | PROVED 1.339 · RELATIVE_ONLY 1.231 · NOT_KNOWN 390 |
| `CONSUMPTION_STATE` | PENDING 2.938 · CONSUMED 16 · ORPHAN_INTELLIGENCE 6 |

`NOT_TESTED` é o estado mais caro da tabela: **863 unidades onde ninguém sequer perguntou
se havia conteúdo.** 240 delas são a janela do YouTube inteira — `LEGENDA_NAO_TESTADA`,
240 de 240, declarado pela própria `FILA-WHISPER.json`.

---

## 6 · AS QUATRO COISAS QUE O BACKFILL SE RECUSOU A INVENTAR

1. **Não inventou leitura.** Existe classificador; classificador não é leitor. `READ` só
   foi selado onde um **caso publicado** nomeia a fonte e publica um número derivado dela.
   Resultado: 22 itens `READ` num acervo de 2.960.

2. **Não inventou consumo.** `ES-X-VOICE-FIELD.json` cruzou as datas dos 252 vídeos
   espanhóis com o RAIF. Seria fácil selar 252 consumos. Não é consumo da inteligência do
   item — é um agregado sobre metadados, e o resultado foi `NO_RELIABLE_SIGNAL`. Zero
   consumos foram selados a partir dele.

3. **Não inventou identidade.** Quatro perfis de LinkedIn com o nome *Massimo Blandino*
   estão no acervo. Todos `NOT_PROVED`: nome bate, cidade não. Ficaram `NOT_PROVED`.

4. **Não promoveu `UNKNOWN` a estado.** O que o artefato não prova saiu `UNKNOWN` ou
   `PENDING`. Estado reconstruído sem prova teria a mesma cara do estado medido, e é essa
   semelhança que destrói a confiança.

---

## 7 · LACUNAS DECLARADAS

| lacuna | consequência | por que fica assim |
|---|---|---|
| `EU-T2-001`, `EU-T2-002`, `IT-T3-001` são citados por casos e **não têm snapshot preservado** | 3 fontes citadas sem passaporte próprio | preservar exigiria coleta nova, proibida nesta missão |
| as 100 duplicatas colapsadas de `ES-T8-002` não têm registro por item | o reencontro delas não é contável | o colapso aconteceu antes do artefato; só a contagem agregada sobreviveu |
| `ES-T5-002` entra como **um** snapshot com `UNIT_COUNT = 1.771` documentos | os 1.771 papers não têm passaporte individual | nenhuma decisão do pipeline é tomada por documento; a regra de granularidade e o caminho de subida estão no contrato |
| `RAW_STATE = NOT_PRESERVED` em 335 itens (240 da janela do YouTube, 73 territoriais, 22 contas) | o bruto não está no Git | política declarada (D-003 e `.gitignore`): bruto de rota gratuita e HTML pesado vivem fora do pack |

Nenhuma dessas lacunas é silenciosa: as três primeiras saem impressas pelo próprio portão.

---

## 8 · DEPOIS DA IMPLEMENTAÇÃO — as quatro provas da missão

```
ITEMS_WITHOUT_PASSPORT                              = 0
UNEXPLAINED_STAGE_DROPS                             = 0
TRANSCRIPT_AVAILABLE_BUT_UNTRACKED                  = 0
VALID_INTELLIGENCE_WITH_UNKNOWN_CONSUMPTION_STATE   = 0
```

Derivadas por `scripts/passaporte_portao.py`, que roda dez portões e devolve
`PASSPORT_ENFORCEMENT = ACTIVE` só quando os dez passam.

`ITEMS_WITHOUT_PASSPORT` não é auto-declarado: as 2.931 chaves naturais são **relidas do
acervo por um caminho independente** do que emitiu os eventos, dentro do próprio portão.
Duas implementações que discordarem derrubam o portão.

---

## 9 · A DÍVIDA, COM NOME

```
TRANSCRIPT_AVAILABLE_NOT_READ        30      ← 1.005.157 caracteres
CONTENT_AVAILABLE_NOT_READ        2.008
READ_WITHOUT_CLAIM                    0
CLAIMS_WITHOUT_ROUTING                6
ROUTED_NOT_CONSUMED                   0
ORPHAN_INTELLIGENCE                   6
```

`ORPHAN_INTELLIGENCE = 6` é um achado, não um defeito do painel: seis snapshots
produziram inteligência publicada em caso real (`CASE-004`, `CASE-015`) e **nenhuma área
de informação os lista em `REAL_EXAMPLES`**. São inteligência válida sem consumidor
declarado. Antes deste contrato eles simplesmente não apareciam em lugar nenhum.
