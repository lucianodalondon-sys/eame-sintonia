# C7 · FACT_LOCATION MATCHER REPAIR — a entrega

A C6 deixou registado um defeito medido e **não** corrigido: o casador de lugar
mandava vídeos italianos para Espanha porque `la rioja` virava a raiz `rio`, e
`rio` casava dentro de `periodico`. A C7 foi consertá-lo.

Ao ir, encontrou três coisas que a C6 não sabia:

1. **não era um lugar infeliz.** 37 dos 59 lugares declarados casavam assim;
2. **os 230 nunca foram publicados.** O artefato no disco era de 2026-09-06 e o
   defeito entrou a 2026-09-07 — logo a frase da C6 «mudaria 230 registos
   publicados» estava errada;
3. **o artefato tinha erro seu**, de outra espécie e mais antiga: 117 registos
   publicados cuja frase de evidência é falsa.

```
AFETADOS NO CODIGO != ERRADOS NO ARTEFATO.
```

---

# A · GIT

| campo | valor |
|---|---|
| **BRANCH** | `claude/sintonia-fact-location-c7` |
| **SOURCE_BRANCH** | `claude/sintonia-scrap-text-provenance-c6` |
| **SOURCE_HEAD** (referência do coordenador) | `dab574b957c944e5b64b98537ace253597692936` |
| **ACTUAL_INITIAL_HEAD** (medido) | `dab574b957c944e5b64b98537ace253597692936` |
| **REMOTE_HEAD** (medido) | idem — local e remoto no mesmo ponto |
| **FINAL_HEAD** | o commit que traz este documento |
| **PUSH_STATE** | `PUSHED` · nenhum `force`, nenhuma reescrita |
| **WORKTREE** | `/home/user/eame-sintonia`, limpa na medição |
| **DRIFT** | **NENHUM** na branch da C6 |

O `fetch --all --prune` trouxe avanço em três frentes alheias
(`raw-observation-identity`, `t2-admission-rule-v1`, e a de know-how). **Nenhuma
foi fundida.** A de know-how tinha avançado para `506f5edf`, e por isso não se
partiu de `e219edc2` — foi lida antes de escrever.

Commits da missão, do mais antigo ao mais recente:

```
75d3a97d  C7: a beterraba virava Toledo, e «beaucoup» virava Beauce
079dd155  C7: o derivado volta a bater com a regua, e passa a dizer de quando e
7fe6f489  C7: uma prova da C6 apoiava-se no defeito que a C7 tirou
a55cbe42  System Map: regeneracao mecanica da C7
<este>    C7: a entrega
```

---

# B · OWNER

```
CURRENT_OWNER            regras/sensor_medir.py::lugar_do_fato
CANONICAL_OWNER_FOUND?   SIM — e por isso a pergunta valeu a pena
ACTION                   REUSAR A REGRA, NAO O MODULO
```

O repositório **tem** dono canônico do lugar do facto, em dois ficheiros:

- `leis/lugar_do_fato.py` — a **lei**: quatro espécies de lugar, escada de
  precisão, espécies de evidência, estados de recusa. Ele declara vocabulário e
  **de propósito não implementa leitor**: «o core não reimplementa o leitor».
- `leis/fato_local.py` — o **leitor italiano**, portado verbatim da Itália, com
  aviso no cabeçalho: «Atualizar este arquivo = repuxar da Itália, não editar
  aqui».

E `mencoes()` já tinha exactamente a regra que faltava, com a razão ao lado:

> Fronteira de palavra obrigatória: sem ela "Roma" casaria dentro de "Romagna" e
> "Bari" dentro de "Barletta" — **substring acidental foi um dos falsos
> positivos medidos no Brasil**.

Reusar o módulo inteiro não servia, por três razões medidas: o gazetteer dele é
só italiano; ele exige **âncora semântica** («constatata a», «sintomi osservati
in»), que é contrato mais forte do que o do sensor; e o ficheiro não se edita
aqui. Adotá-lo mudaria o significado de `COUNTRY_OF_FACT` — outra missão.

Então a C7 **copiou a regra e não o módulo**, e a prova reprova se os dois
deixarem de dizer o mesmo.

```
UMA CASA, UMA REGRA — MESMO QUANDO SAO DOIS LEITORES.
```

Havia mais duas tabelas `LUGARES` no repositório. As duas foram medidas e
**nenhuma tem este defeito**: `coleta/comunicacao_classificar.py` casa termo
curto com fronteira e termo longo como frase inteira; `motor/v21_traducao_trava.py`
não é matcher de facto, é guarda de tradução. Mexer nelas seria alterar contrato
que esta missão não mediu.

---

# C · O MATCHER ANTIGO, E POR QUE NÃO SERVE A LUGAR

`_raizes` · `_perto` · `_tem` são a peneira de **assunto**, e são boas nisso:

```python
_raizes('diserbo del mais')  ->  ['diser', 'ma']   # trunca de propósito
_perto(texto, pedacos)                             # e procura DENTRO da palavra
```

Truncar é virtude para assunto — `diserbo` apanha `diserbato`, `diserbante`, e a
ideia sobrevive à conjugação. Para nome próprio é ruína:

```
_raizes('la rioja')  ->  ['rio']
```

`la` é palavra de função e sai; `rioja` tem 5 letras e perde 2. Depois `_perto`
procura `rio` **dentro** de qualquer palavra — e encontra-o em 140 palavras
distintas deste acervo.

```
PENEIRA DE ASSUNTO TRUNCA PORQUE A IDEIA SOBREVIVE A CONJUGACAO.
NOME PROPRIO NAO SOBREVIVE A TRUNCAGEM — ELE VIRA OUTRO NOME.
```

---

# D · BASELINE

Medido no `ACTUAL_INITIAL_HEAD`, com o código de então:

```
TOTAL_VIDEOS                    1071
TOTAL_COMMENTS                  3688

VIDEOS_WITH_COUNTRY_OF_FACT      510      ES 334 · IT 148 · FR 28
COMMENTS_WITH_COUNTRY_OF_FACT    545      ES 255 · IT 186 · FR 104

LA_RIOJA_MATCHES videos          230
LA_RIOJA_MATCHES comments        149
```

```
230_REPRODUCED = YES — exactamente 230, no codigo.
```

---

# E · A DECOMPOSIÇÃO DOS 230

```
EXACT_PHRASE_MATCH        0
TOKEN_MATCH               0
FUZZY_ROOT_MATCH        230      <- todos
OTHER                     0
```

Nenhum dos 230 tinha o lugar escrito. As palavras que os produziram, contadas:

| palavra | ocorrências |
|---|---|
| `proprio` | 58 |
| `septoriose` | 48 |
| `periodo` | 40 |
| `agrario` | 31 |
| `fitosanitario` | 23 |
| `necessario` | 21 |
| `fusariosi` | 17 |
| `superiore` | 16 |
| `various` | 14 |

**O nome da doença virava a província.**

### E.2 · Mas os 230 nunca foram publicados

Aqui a C6 errou, e a C7 corrige:

```
la rioja entra na lista        2026-09-06   (com `_tem` de substring simples)
o casamento por raiz chega     2026-09-07   (commit 28c2bc0d, «a isca apanha a FALA»)
MEDICAO.json escrito pela ultima vez   2026-09-06
```

O artefato publicado tem **zero** evidências de «la rioja». O defeito estava
**latente**: em código desde 2026-09-07, à espera da próxima regeneração.

```
UM DEFEITO LATENTE E O QUE ESTOURA NA PROXIMA REGERACAO.
POR ISSO O CONSERTO TEM DE VIR ANTES DELA.
```

### E.3 · O artefato tinha erro seu, mais antigo

Auditando a frase de evidência de cada registo publicado — «o texto nomeia X»
tem de ter X escrito no texto:

| | publicados com país | evidência verdadeira | **evidência falsa** |
|---|---|---|---|
| vídeos | 236 | 175 | **61** |
| comentários | 131 | 75 | **56** |

Causa: `substring` simples, anterior à raiz truncada.

```
«aragon»   <- paragonabile
«jaen»     <- canalsurjaen        um handle de canal
«italia»   <- italiano            e IDIOMA != LUGAR DO FATO
«verona»   <- aipoverona          o nome do canal
«piemonte» <- piemontesi
```

```
REGISTOS PUBLICADOS ERRADOS = 117, e nao 230 — nem pela mesma causa.
```

---

# F · RED TEAM DE TODOS OS LUGARES

Não bastava consertar `la rioja` e deixar a próxima bomba no sítio. Cada um dos
59 lugares declarados foi medido contra os 4.759 textos.

**37 de 59 casavam por raiz.** Sete em nível crítico:

| lugar | país | raiz | CURRENT | EXACT | FUZZY_ONLY | o que apanhava |
|---|---|---|---|---|---|---|
| `la rioja` | ES | `rio` | 430 | 0 | **430** | `septoriose`, `fusariosi`, `periodo` |
| `verona` | IT | `vero` | 121 | 9 | **112** | `davvero`, `vero`, `ovvero` |
| `cadiz` | ES | `cad` | 105 | 1 | **104** | `cada`, `mercado`, `caduta` |
| `le marche` | IT | `marc` | 103 | 1 | **102** | `marco`, `marca`, `marciume` |
| `france` | FR | `fran` | 99 | 10 | **89** | `francesca`, `francesco` |
| `italia` | IT | `ital` | 147 | 76 | **71** | `italiana`, `digitale`, `vitale` |
| `beauce` | FR | `beau` | 54 | 0 | **54** | `beaucoup` (43x) |
| `cordoba` | ES | `cordo` | 56 | 10 | **46** | `ricordo`, `accordo` |
| `campania` | IT | `campan` | 28 | 3 | **25** | `campanella`, `campana` |
| `veneto` | IT | `vene` | 45 | 22 | **23** | `intervenendo` |
| `toledo` | ES | `tole` | 20 | 2 | **18** | `barbabietole`, `bietole` |
| `emilia` | IT | `emil` | 37 | 20 | **17** | `alchemillae` |
| `espana` | ES | `espa` | 13 | 3 | **10** | |
| `puglia` | IT | `pugl` | 23 | 14 | **9** | `decespugliatore` |
| `aragon` | ES | `arag` | 8 | 1 | **7** | `paragonabile` |

E mais 22 em risco baixo: `sicilia`←`siciliano`, `murcia`, `charente`←`charentais`,
`umbria`←`umbrella`, `huelva`←`huella`, `friuli`←`friulana`, `navarra`,
`piemonte`, `trentino`, `treviso`, `toscana`, `abruzzo`, `foggia`, `chianti`,
`lombardia`, `bourgogne`, `gironde`, `val de loire`, `languedoc`,
`regione marche`, `jaen`, `alto adige`.

**22 dos 59 já estavam limpos** — e estavam por acaso, não por lei.

---

# G · O CONTRATO DO MATCHER NOVO

```python
_FRONTEIRA = r'(?<![0-9a-z])%s(?![0-9a-z])'

def _nomeia_lugar(texto, nome):
    partes = [re.escape(p) for p in _n(nome).split()]
    return re.search(_FRONTEIRA % r'\s+'.join(partes), texto) is not None
```

- **uma palavra** casa como token inteiro. `rio` não casa dentro de `periodico`;
- **várias palavras** exigem a frase declarada, na ordem. `rioja` sozinho não é
  `la rioja`, e `adige alto` não é `alto adige`;
- **só o espaço é elástico** (`\s+`), para que uma quebra de linha não apague
  `la\nrioja`;
- **acento e caixa** caem na normalização que já existia. Isso é grafia da mesma
  palavra;
- **nada é truncado.**

```
NORMALIZAR != STEMMING.
```

A regra de fronteira é a de `leis/fato_local.py::mencoes`, literal. Há prova que
reprova se as duas divergirem.

**Não foram criados aliases.** A lista continua a ser declaração, com as suas
cicatrizes: `le marche` e `regione marche` em vez de `marche`, porque `marche` é
palavra francesa comum — medido, `marche` nu apanharia 7 «ça marche» neste
acervo. `catalunya` e `cataluna` continuam duas entradas, que é o padrão certo.

**A ordem de desempate não mudou**, de propósito (§14): primeiro país da tabela,
primeiro nome da lista. Corrigir o casamento e mexer na precedência na mesma
missão daria dois efeitos num delta só.

---

# H · SENTINELAS POSITIVAS

Todos casam, com o país certo:

```
La Rioja -> ES      Verona -> IT        Trentino -> IT
Champagne -> FR     Bordeaux -> FR      Val de Loire -> FR
Alto Adige -> IT    Le Marche -> IT     Regione Marche -> IT
Cotes du Rhone -> FR
```

E dentro de frase inteira, que é onde eles vivem:

```
«Flavescenza dorata: diffusione nel territorio veneto»       -> IT
«Le vin de Champagne face au mildiou»                        -> FR
«El olivar de La Rioja y el repilo»                          -> ES
```

Acento, caixa, pontuação ao lado, hífen e quebra de linha não quebram nada:
`Córdoba`, `ANDALUCÍA`, `(Verona)`, `#Trentino`, `Emilia-Romagna`, `la\nrioja`.

---

# I · SENTINELAS NEGATIVAS

Os cinco obrigatórios, mais doze que o censo encontrou depois — cada um vindo de
ocorrência **real** no acervo:

```
Periodico olivo 1 Maggio 2026        periodico -> rio
calendario fitosanitario             calendario -> rio
various periods prior to harvest     period/prior -> rio
superior                             superior -> rio
scenarios                            scenarios -> rio
septoriose du ble                    o nome da DOENCA
fusariosi del frumento               idem
barbabietole da zucchero             a BETERRABA -> tole
beaucoup de pluie cette annee        «muito» -> beau
davvero interessante, grazie         «deveras» -> vero
ricordo bene quel anno               «recordo» -> cordo
ho parlato con Francesco ieri        o NOME DA PESSOA -> fran
marciume del grappolo                marciume -> marc
ca marche tres bien                  a cicatriz original da lista
il decespugliatore nuovo             decespugliatore -> pugl
mercado del aceite de oliva          mercado -> cad
campanella in fiore                  campanella -> campan
```

Todos saem `NOT_KNOWN`. E o gentílico também:

```
tecnica italiana · grano italiano · un collega abruzzese
varieta siciliana · cuisine francaise            ->  NOT_KNOWN
```

```
COUNTRY_OF_PERSON != COUNTRY_OF_FACT.
```

---

# J · VIDEO DELTA

Medido com os dois casadores a correr lado a lado sobre os mesmos 1.071 textos —
o antigo **carregado do worktree pristino**, não reescrito de memória.

```
UNCHANGED                  665
KNOWN_TO_UNKNOWN           326
COUNTRY_TO_COUNTRY          71
UNKNOWN_TO_KNOWN             0
SAME_COUNTRY_OTHER_PLACE     9
```

---

# K · COMMENT DELTA

`lugar_do_fato` também serve comentários, e por isso foram medidos à parte.
Corrigir vídeo não era suficiente.

```
UNCHANGED                 3199
KNOWN_TO_UNKNOWN           467
COUNTRY_TO_COUNTRY          17
UNKNOWN_TO_KNOWN             0
SAME_COUNTRY_OTHER_PLACE     5
```

### K.2 · A revisão humana dos que mudam de país (§18)

Os 88 foram abertos um a um. **Todos** foram para o país certo:

```
Flavescenza dorata – Diffusione nel territorio veneto      ES -> IT
CONTRASTO ALLA FLAVESCENZA DORATA DELLA VITE               ES -> IT
Septoriose du ble : observer pour decider                  ES -> FR
Mildiou et black-rot : comment proteger votre vignoble ?   ES -> FR
Viticulture Bio : ... Sylvain Destrieux (Gironde)          ES -> FR
Puntata 12, La barbabietola da zucchero 1                  ES -> IT
Io scrivo dal Trentino. Anche noi ...                      ES -> IT
```

E os dois lugares que só existem **depois** — `gironde` e `chianti` — não foram
inventados: estavam escritos (`(Gironde)`, `ad Ama in Chianti`) e estavam tapados
por um falso positivo que casava primeiro na ordem.

### K.3 · A amostra estratificada dos que vão para UNKNOWN

Das 793 quedas, o nome só aparece escrito em **75**. Abertas todas:

| o que é | quantos | veredito |
|---|---|---|
| gentílico (`italiano`, `siciliano`, `abruzzese`) | 55 | recusa **correcta** — fala da pessoa |
| handle ou domínio (`canalsurjaen`, `francetvinfo`) | 16 | recusa **correcta** — fala da fonte |
| outro | 4 | ver abaixo |

Dos 4 restantes: `decespugliatore` e `aipoverona` são falso positivo do antigo; os
outros dois são `«un caro saluto dalle Marche»` — que é origem da pessoa, não
lugar do facto.

Varrendo as 793 pelo núcleo do nome como token inteiro, sobram 12 candidatos, e
7 deles são o francês `ça marche`. **A perda genuína é de 3 menções em 4.759
textos**, duas delas saudações.

A lista declara `le marche` e não `dalle marche`. Ampliá-la é decisão de quem
declara a lista — fica em **R**, por decidir, e não feita em silêncio.

---

# L · DISTRIBUIÇÃO ANTES / DEPOIS

Do **artefato publicado** para o artefato regenerado:

| | ANTES | DEPOIS |
|---|---|---|
| `VIDEOS_COM_COUNTRY_OF_FACT` | 236 | 184 |
| vídeos ES | 33 | 31 |
| vídeos IT | 171 | 128 |
| vídeos FR | 32 | 25 |
| vídeos `NOT_KNOWN` | 835 | 887 |
| `COMMENTS_COM_COUNTRY_OF_FACT` | 131 | 78 |
| comentários ES | 11 | 8 |
| comentários IT | 82 | 64 |
| comentários FR | 38 | 6 |
| comentários `NOT_KNOWN` | 3557 | 3610 |

### L.2 · ⚠ Esta tabela **não** é o efeito da C7

O artefato era de 2026-09-06 e a régua mudou três vezes desde então. Medindo em
**três** pontos em vez de dois:

```
publicado, codigo de 2026-09-06        236 videos com pais
codigo de HOJE, geografia ANTIGA       510      <- 5 dias de deriva alheia
codigo de HOJE, geografia NOVA         184      <- o efeito da C7
```

```
EFEITO DA C7            510 -> 184   (-326)
DERIVA ANTERIOR         236 -> 510   (+274)
```

Na mesma regeneração o tipo de conteúdo também se move — `RESEARCH_COMMUNICATION`
de 11 para 284, `NOISE` de 567 para 84 — e **nada disso é da C7**: medida zero
divergência em `classificar_conteudo` (1115 itens) e `classificar_comentario`
(3737 itens), contra o módulo antigo carregado do worktree pristino.

```
COMPARAR O ARTEFATO VELHO COM O NOVO MEDE TUDO O QUE MUDOU DESDE ELE,
E ATRIBUI A ESTA MISSAO O QUE E DE OUTRAS.
```

---

# M · MEDICAO.JSON

```
REGENERATED = YES
```

**Porquê:** o portão do §22 passou nos seis. E porque o artefato já estava errado
por conta própria (117 registos com evidência falsa, secção E.3) — deixá-lo como
estava seria preservar erro publicado para não mexer no número.

```
P1  bug reproduzido                            230, exactamente
P2  falsos positivos eliminados                17 de 17 sentinelas negativas
P3  positivos verdadeiros preservados          10 de 10; perda genuina 3 / 4759
P4  red team de TODOS os lugares               59 medidos, 37 defeituosos
P5  nenhum pais inventado                      UNKNOWN_TO_KNOWN = 0
P6  regressao lexical fora da geografia        0 em 4852 itens
```

**Lineage.** O artefato passou a declarar o que não declarava:

```
ARTIFACT_KIND     DERIVED
PARENT_ARTIFACTS  15 ficheiros (VIDEOS/COMENTARIOS/TRANSCRICOES A-E)
CAPTURED_AT       2026-09-11
DERIVED_AT        2026-09-11T12:58:34Z
GEOGRAPHY_RULER   a regua que produziu estes numeros, escrita por extenso
```

```
ARTEFATO DERIVADO SEM HORA DE DERIVACAO ENVELHECE EM SEGREDO.
A REGUA MUDA O NUMERO — ENTAO O NUMERO TEM DE DIZER QUE REGUA O FEZ.
```

**O bruto não foi tocado.** `data/raw/**` intacto, e há prova que o verifica.

---

# N · O GATE DA C6

```
TRANSCRIPT_KIND_GATE_PRESERVED = YES
```

`medir()` continua a chamar `pv.serve_para_original` antes de deixar a
transcrição chegar ao lugar do facto, e a prova lê isso da árvore sintática.

Uma prova da C6 **teve** de ser reparada, e isso está na secção Q.

---

# O · TESTS

```
BASE_TOTAL      2059        FINAL_TOTAL     2079
BASE_FAILURES     22        FINAL_FAILURES    22
BASE_ERRORS        1        FINAL_ERRORS       1
BASE_SKIPS       178        FINAL_SKIPS      178
BASE_MODULES      81        FINAL_MODULES     82

NEW_FAILURES       0
```

As 23 vermelhas finais são as mesmas 23 da base — os mesmos 16 testes. As quatro
linhas que mudam são o mesmo marcador desactualizado a citar a contagem nova
(`2.063` → `2.083`): é o total de testes que mexeu, não a falha.

**20 provas novas.**

Baseline e final foram medidos **no mesmo método e no mesmo tipo de sítio** —
cada um num worktree próprio, um em `dab574b9` e outro no head da C7. Medir a
base numa árvore e o fim noutra compararia duas coisas diferentes; a C6 já tinha
perdido uma medição a atravessar o próprio commit.

---

# P · SYSTEM MAP

```
WORKFLOW_SOURCE   .github/workflows/system-map.yml
STEPS_EXECUTED    22, extraidos do workflow — nao escritos de memoria
RESULT            SYSTEM_MAP_CHECK = PASS · 22 de 22 provas
PENDING_PIECES    99 de 161 — nenhuma mudou de estado nesta missao
```

`C-PALAVRAS` continua `PENDING` desde a C6: o sha de `regras/sensor_medir.py` que
uma pessoa conferiu contra a descrição continua a não bater, e a C7 mexeu no
ficheiro outra vez.

**Não foi recarimbado.** Duas missões seguidas a mexer no mesmo ficheiro não
somam a uma revisão humana.

```
UM VERDE QUE O PROPRIO AUTOR REPOE NAO E REVISAO. E ASSINATURA EM BRANCO.
```

---

# Q · REGRESSIONS

**Uma, e foi corrigida na origem.**

A prova viva do portão de espécie da C6 usava texto inglês com «prior period»,
«superior», «various» e «scenarios». Aquelas palavras mudavam o país **porque a
raiz `rio` casava dentro delas**. Consertado o casador, a prova deixou de
reproduzir — e a própria prova dizia, no `assert`, «confirme antes de apagar
esta prova».

Não foi apagada. O texto passou a **nomear** um lugar, que é o que um texto
original faria, e a prova voltou a medir o que lhe compete: se a **espécie**
decide a entrada do texto.

```
UMA PROVA QUE SE APOIA NUM DEFEITO MORRE QUANDO O DEFEITO MORRE.
A PERGUNTA CERTA E SE ELA AINDA MEDE A LEI, NAO SE ELA AINDA PASSA.
```

Fora isso: `_raizes`, `_perto`, `_tem`, `_n`, `classificar_conteudo`,
`classificar_comentario` estão **byte a byte** iguais ao head da C6 — comparados
por árvore sintática, não por leitura — e `PISO_DA_RAIZ` e `JANELA_DE_PALAVRAS`
continuam 5 e 18.

---

# R · UNKNOWNs

Coisas medidas que a C7 **não** decidiu, por não serem dela:

1. **as formas articuladas de «Marche».** `dalle marche`, `delle marche` e
   `nelle marche` casariam 4 textos e nenhum «ça marche» — medido. Mas ampliar a
   lista é declaração, e declaração é de quem a mantém. Fica por decidir.
2. **gentílico é lugar do facto?** 55 quedas são `italiano`, `siciliano`,
   `abruzzese`. Hoje a resposta é não, e a lei sustenta-a
   (`COUNTRY_OF_PERSON != COUNTRY_OF_FACT`). Se a casa quiser o contrário, é
   entrada declarada, não stemming de volta.
3. **a ordem quando há dois lugares.** Hoje: primeiro país da tabela, primeiro
   nome da lista. Está documentado e **não** foi mexido. Se for defeito, é de
   outra missão.
4. **as três tabelas `LUGARES`.** Três módulos declaram lugares. Nenhum dos
   outros dois tem este defeito, mas «um conceito, um dono» continua por
   cumprir aqui.

---

# S · O QUE NÃO MUDOU

O gate de política do YouTube da C5. Os Actors. A GPU e o reconhecedor local da
C4. A rota de transcrição. O orquestrador, o schema da coleta, as migrations, o
Admission, a Intelligence, o portal, o deploy e a `main`.

E, dentro do próprio ficheiro: a peneira de assunto, que continua a truncar
porque é isso que ela tem de fazer.

---

# T · KNOW_HOW_DELTA

```
KNOW_HOW_DELTA = ATUALIZAÇÃO NECESSÁRIA → registrada no know-how canônico
```

Duas escritas, e a branch mexeu-se entre elas — por isso são dois pares de heads
medidos, não um herdado.

```
BRANCH        claude/sintonia-eame-know-how-v1
FICHEIRO      HANDOFF-ATUAL-SINTONIA-EAME.md

a missao      INITIAL_HEAD  506f5edf6c6aac09fdb6f2032ed76ddfae833044
              FINAL_HEAD    5a819a13b1365b93ea5b5bf0fa10aa24ee9d1c11

o fechamento  INITIAL_HEAD  a198a6877366ae8d9211f5ce1931e05b0afc2ba0
              FINAL_HEAD    834a920614b1c4d003a66bebd8f8570a71b5281a
```

Secção 15: cinco lições da missão (15.1–15.5), mais duas do fechamento —
**15.6**, a frente sem receita que o orquestrador não alcança, e **15.7**, o laço
que se procura a si próprio.

Entre a escrita da missão e a do fechamento, a branch andou **três commits** por
outras frentes (`f6725b1e`, `ae47a506`, `a198a687`), todos noutro ficheiro. Foi
relida antes de cada escrita. Nada foi sobrescrito, e a secção 15 chegou intacta
ao fim.

---

# U · GEOGRAPHY VERDICT

```
FACT_LOCATION_MATCHER                = PASS
PUBLISHED_DERIVED_GEOGRAPHY_REPAIRED = YES
```

---

# V · READY_TO_LEAVE_YOUTUBE_FRONT

```
READY_TO_LEAVE_YOUTUBE_FRONT = YES
```

As quatro capacidades oficiais da C3 estão pela rota oficial. Transcrição e
mídia estão bloqueadas por **autorização**, não por técnica, e a C5 fechou isso
com as políticas citadas. O texto que existe tem a procedência protegida pela
C6. E a geografia deixou de fabricar país por substring.

O que fica aberto no YouTube não se resolve com mais engenharia: resolve-se com
autorização que a casa não tem.

---

# W · SCRAP × COLLECTION CANÔNICA

Secção de **fechamento**, e só de leitura. Nada aqui foi integrado, mergeado ou
corrigido: o contrato da frente paralela foi lido no checkpoint
`07fcafbb2d162f36931f3bce83dc1cba705c7e51`, com `git show`, sem tocar na
Collection.

O que o contrato diz, confirmado **por leitura** e não por expectativa:

```
COLHEITA · MANIFEST · CATALOG · RUN_RECEIPT · PLAN · UNKNOWN
ENTRAM_NO_INGRESSO = (COLHEITA,)     <- so a colheita atravessa. As outras leem-se.

SOURCE_ID     obrigatorio e provado — «NAO SEI» nao serve para colheita
DOCUMENT_ID   pode faltar; nao pode ser fabricado. sha256, cara de hash e
              endereco do ficheiro sao recusados por nome
RUN_ID        pertence ao envelope — RUN_MISMATCH se a unidade disser outro
PAYLOAD       estado explicito: PRESENTE · AUSENTE · NAO_SE_APLICA
```

**Primeiro facto, e ele governa a secção inteira:**

```
leis/retorno_da_coleta.py NAO EXISTE nesta branch.
Existe so em 07fcafbb, na frente paralela.
```

Nesta árvore, quem decide o que é colheita é `orquestrador/orquestrador.py::a_colheita`
— a heurística genérica que o próprio contrato novo foi escrito para substituir,
e cujo preço a frente paralela já mediu em `FALSE_HARVEST_TOTAL = 253`.

---

## W.1 · COL-LAW-505

```
C7_USES_RETURN_ENVELOPE_AT_RUNTIME  = NOT_APPLICABLE_TO_C7
COL_LAW_505_STATUS                  = NOT_APPLICABLE_TO_C7_RUNTIME
```

**Prova.** Os cinco ficheiros que a C7 tocou são `regras/sensor_medir.py`,
`tests/test_c6_especie_do_texto.py`, `tests/test_c7_lugar_do_fato.py`,
`data/samples/SENSOR-PILOT/MEDICAO.json` e este documento. Nenhum importa
`retorno_da_coleta`, `ingresso` ou `orquestrador` — medido na árvore sintática,
contagem **0**. E o módulo do envelope nem sequer está nesta branch.

E a distinção que o briefing pediu para não colapsar:

```
SCRAP_EXECUTOR_COL_LAW_505_COMPATIBILITY = UNKNOWN
```

Não `PROVEN` e não `PARTIAL`. Com o módulo ausente desta árvore, não há contra o
quê medir compatibilidade aqui. O que **se** pode dizer, medido pelo censo do
próprio mapa, é que nenhum executor de YouTube usa contrato de artefacto:

```
coleta/adaptador_youtube.py     USA_CONTRATO_ARTEFATO = false
coleta/youtube_janela.py        USA_CONTRATO_ARTEFATO = false
coleta/youtube_oficial.py       USA_CONTRATO_ARTEFATO = false
coleta/youtube_relevancia.py    USA_CONTRATO_ARTEFATO = false

POR_ESTADO: NOT_INSTRUMENTED 57 · NOT_APPLICABLE 11 · INSTRUMENTED 2 · PARTIAL 1
```

```
C7 NAO ATRAVESSAR O ENVELOPE NAO PROVA QUE O SCRAP O CUMPRE.
UMA MISSAO DERIVED NAO E CREDENCIAL DO EXECUTOR.
```

Nenhum adapter foi implementado nesta missão.

---

## W.2 · COLHEITA ≠ SUPORTE

```
C7_PRODUCES_EXECUTOR_HARVEST = NO
C7_PRODUCES_DERIVED          = YES
```

**Prova.** O único artefacto que a C7 escreveu declara-se, no próprio ficheiro:

```
EVIDENCE_CLASS  = DERIVED_MEASUREMENT
ARTIFACT_KIND   = DERIVED
source          = derivado do material ja coletado — nenhuma execucao nova
APIFY_RUNS      = 0
COST_USD        = 0
```

Nenhum `MANIFEST`, `CATALOG`, `RUN_RECEIPT` ou `PLAN` foi promovido a observação
por esta missão. A C7 não emitiu envelope de retorno nenhum.

E uma verificação que valia a pena fazer, porque o risco era real: **`SENSOR-PILOT`
não é `larga_em` de receita nenhuma.** As cinco declaradas largam em
`data/colheita/italia/`, `data/raw/IT-ROTULOS`, `data/samples/COMPETITOR-PUBLIC-COMM`,
`data/samples/IT-PRAGAS`, `data/samples/REEL-TRANSCRICOES` e
`RESEARCHER-CORPUS-EAME-V1.json`. O artefacto regenerado pela C7 não pode ser
varrido pela heurística de colheita, porque ela nunca olha para aquela pasta.

---

## W.3 · RUN_ID

```
WHERE_RUN_ID_IS_BORN_FOR_SCRAP =
    orquestrador/orquestrador.py::novo_run_id(pedido)   — para a rota canonica
    regras/proveniencia.py::novo_run(run_id, ...)       — quem o REGISTA
    regras/sensor_coleta.py                             — a frente do sensor
                                                          carrega RUN_ID vindo
                                                          do manifesto, nao o cria

C7_RUN_ID = NOT_APPLICABLE
```

**Prova.** `regras/sensor_medir.py` — o módulo que a C7 alterou — não nomeia
`RUN_ID` em lado nenhum. A C7 não abre corrida, não fecha corrida e não escreve
no manifesto.

Separando os três níveis, que era o que o briefing pedia:

| | estado | evidência |
|---|---|---|
| `MODULE EXISTS` | **YES** | `novo_run_id` e `novo_run` existem e têm dono |
| `EDGE EXISTS` | **YES** | `orquestrador` importa `proveniencia` e `ingresso` |
| `FLOW EXISTS` | **PARCIAL** | ver W.9 — há 20 corridas no manifesto, mas a fronteira nunca foi atravessada |

```
NAO SE INVENTA PROVA GLOBAL DO SCRAP A PARTIR DE UMA MISSAO DERIVED.
```

---

## W.4 · RAW

```
C7_TOUCHES_RAW = NO
```

**Prova.** `git diff --stat dab574b9 HEAD -- data/raw` sai **vazio**, e
`git status --short -- data/raw` sai vazio. Há ainda prova na suíte que reprova
se `data/raw` se mexer.

```
SCRAP_RAW_PRESERVATION_CONTRACT = PARTIAL
```

Não `PROVEN`. O que está provado é que há manifesto de preservação com sha256
por ficheiro e que o bruto pago sobrevive — e há prova disso na suíte. O que
**não** está provado é a cadeia inteira `captura → RAW original → DERIVED` para
o SCRAP, porque a parte de cima dela nunca foi exercida por aqui. A lei está
respeitada; a cadeia completa não está medida.

---

## W.5 · SOURCE_ID

```
C7_FABRICATES_SOURCE_ID = NO
```

**Prova.** O diff da C7 em `regras/sensor_medir.py` não contém uma única linha
adicionada com `SOURCE_ID` — contagem **0**. O `SOURCE_ID` do artefacto
(`SENSOR-PILOT/MEDICAO`) é o que já lá estava, herdado, e não foi tocado.

Para o SCRAP, a lei lida no contrato: `SOURCE_ID` vem da identidade canônica da
fonte, e nunca de URL, slug, hash ou caminho. A C7 não tem opinião sobre isso
porque não cria fontes.

---

## W.6 · DOCUMENT_ID

```
FABRICATED_DOCUMENT_ID = NO
```

**Prova.** Mesma contagem: **0** linhas adicionadas com `DOCUMENT_ID`. A C7 não
escreve identidade documental nenhuma.

A lei, lida no contrato e transcrita aqui para não se perder:

```
SHA256 NAO E IDENTIDADE DOCUMENTAL.
storage_path NAO E IDENTIDADE.
```

Nenhum de `SHA` · `URL` · `filename` · `timestamp` · `slug` · `storage_path`
pode virar `DOCUMENT_ID`. E a razão está medida do outro lado: 35 valores de
`sha256` aparecem em observações **distintas** — um `DOCUMENT_ID` tirado do sha
colaria duas observações legítimas numa só.

---

## W.7 · MODELO PARALELO

```
PARALLEL_RUN_MODEL      = NO
PARALLEL_RAW_MODEL      = NO
PARALLEL_IDENTITY_MODEL = NO
PARALLEL_WAITING_ROOM   = NO
```

**Prova.** A C7 não criou modelo nenhum: alterou uma função de casamento de
texto, regenerou um derivado com o dono que já existia (`regras/sensor_medir.py`,
o mesmo script que sempre escreveu aquele ficheiro) e acrescentou-lhe campos de
linhagem. Não há segunda corrida, segundo bruto, segunda identidade nem sala de
espera nova.

Os campos de linhagem acrescentados (`ARTIFACT_KIND`, `PARENT_ARTIFACTS`,
`CAPTURED_AT`, `DERIVED_AT`, `GEOGRAPHY_RULER`) seguem o padrão que a C6 já tinha
usado no artefacto irmão da mesma pasta. Reaproveitar o padrão da casa é o
contrário de criar um modelo paralelo.

---

## W.8 · CLASSIFICAÇÃO TEMÁTICA

```
SCRAP_THEMATIC_CLASSIFIER_CREATED = NO
T2_T3_T7_T9_DECISION_IN_SCRAP     = NO
```

**Prova.** `classificar_conteudo` e `classificar_comentario` estão **byte a byte**
iguais ao head da C6 — comparados por árvore sintática — e medida a sua saída em
todo o acervo, deu **zero divergência** em 1115 vídeos e 3737 comentários.

E a distinção que o briefing pediu, que é a única coisa que importa aqui:

```
FACT_LOCATION extraction  !=  thematic admission
```

A C7 extrai evidência geográfica: «este texto escreve o nome deste lugar». Não
decide universo temático, não admite nada e não julga relevância. Aliás, o efeito
da missão foi **reduzir** o que se afirma, não alargar.

---

## W.9 · O CAMINHO ATÉ À COLLECTION

Cada seta com o seu estado. Nada promovido de desejado a observado.

| seta | estado | evidência |
|---|---|---|
| `COLLECTION_REQUEST → ORCHESTRATOR` | **OBSERVED** | `pedido/receitas.py` declara 5 executores; `orquestrador::novo_run_id(p: Pedido)` |
| `ORCHESTRATOR → SCRAP EXECUTOR` | **OBSERVED, parcial** | corrida `XX-T9-2026-09-07-193647`, ator `coleta/comunicacao_coleta.py`, `STATUS OK`, 78 itens |
| `ORCHESTRATOR → SCRAP EXECUTOR (YouTube)` | **UNKNOWN** | **não há receita de YouTube**. As 5 declaradas não o incluem |
| `SCRAP EXECUTOR → ADAPTER` | **OBSERVED** | 6 adapters em `coleta/adaptador_*.py` |
| `ADAPTER → PROVIDER` | **OBSERVED** | 3 corridas Apify de YouTube no manifesto, 252 · 346 · 20 itens |
| `→ executor return envelope` | **UNKNOWN** | o módulo não existe nesta branch |
| `→ canonical Collection flow` | **DECLARED, não observado** | ver abaixo |

A última seta é a que não fecha, e a medição é da própria casa, em
`system-map/data/fronteira.observada.json`:

```
DONO                   admissao/admissao.py :: pronto_para_inteligencia()
PRODUTORES_EM_RUNTIME  ['orquestrador/orquestrador.py']
CONSUMIDORES           []
DESTINO                data/samples/PRONTO-PARA-INTELIGENCIA/<RUN_ID>.json
DESTINO_EXISTE         False
GAP                    READY_SEM_CONSUMIDOR
```

A pasta de destino **não existe**. Nada atravessou.

**E a frente do YouTube que as missões C3 a C7 construíram não tem receita.**
Ela é alcançável por quem a chama à mão; não é alcançável pelo orquestrador.

```
UM EXECUTOR SEM RECEITA NAO ESTA LIGADO AO ORQUESTRADOR.
ESTA AO LADO DELE.
```

---

## W.10 · OS TRÊS NÍVEIS DE PROVA

| prova | estado | evidência |
|---|---|---|
| `SCRAP MODULE EXISTS` | **YES** | 6 adapters, 4 executores de YouTube, `comunicacao_coleta.py`, `social_matriz.py`; 71 executores no censo |
| `SCRAP → Collection EDGE EXISTS` | **PARTIAL** | `orquestrador` é o **único** módulo que importa `ingresso`. Nenhum módulo do SCRAP lá chega por importação — medido por travessia do grafo. A ligação é por **pasta declarada** (`larga_em`), lida por `a_colheita()`, não por chamada |
| `SCRAP → Collection FLOW EXISTS` | **NO** | `DESTINO_EXISTE = False`, `CONSUMIDORES = []`, `GAP = READY_SEM_CONSUMIDOR` |

```
MODULE EXISTS != EDGE EXISTS != FLOW EXISTS
```

Dito sem arredondar: **o módulo existe, a aresta existe por pasta e não por
chamada, e o fluxo não existe.** A porta está construída e continua sem ninguém
a atravessá-la — que é, palavra por palavra, o que o próprio orquestrador já
tinha escrito sobre si mesmo:

```
UMA PORTA POR ONDE NINGUEM PASSA NAO E UMA PORTA.
E UMA PAREDE COM MACANETA.
```

---

## W.11 · CONFLITO

```
CONFLICT = NONE
```

A C7 não introduz incompatibilidade com o contrato canônico. É uma missão
`DERIVED`: não emite colheita, não abre corrida, não fabrica identidade, não
toca no bruto e não atravessa a porta.

Duas coisas **medidas** que não são conflito da C7 e ficam registadas porque
foram vistas, não porque sejam desta missão:

1. **esta branch tem a heurística antiga de colheita.**
   `orquestrador::a_colheita` continua a ler `larga_em` e a adivinhar o que é
   colheita. É exactamente o que `leis/retorno_da_coleta.py` foi escrito para
   substituir, e a frente paralela já mediu o preço: `FALSE_HARVEST_TOTAL = 253`,
   `REAL_HARVEST_ITEMS = 0`. Não é da C7 e não foi tocado.
2. **a frente do YouTube não tem receita.** Sem ela, o orquestrador não a alcança.

```
RECOMMENDED_NEXT_STEP  não é desta missão declarar. As duas ficam como
                       estado medido, para quem decidir a ordem das frentes.
```
