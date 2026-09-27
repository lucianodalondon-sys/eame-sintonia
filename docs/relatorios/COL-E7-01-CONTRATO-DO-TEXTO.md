# COL-E7-01 · O CONTRATO CANÓNICO DO TEXTO NA COLLECTION — a entrega

> **O objetivo:** fechar a primeira aresta perdida na integração SCRAP →
> Collection, sem a fechar com `texto = TEXT`.
>
> **O que o censo encontrou:** o contrato não faltava. Ele existia **de um lado
> da fronteira e não do outro**.

```
E1–E6 = PASS        E7 = STOP
FIRST_LOST_EDGE     E7_a_unidade_leva_texto_para_quem_julga
```

---

# A · GIT

| campo | valor |
|---|---|
| **BRANCH** | `claude/collection-e7-text-contract-0qk2gr` |
| **BASE** | `claude/collection-operational-readiness-overnight-v1` |
| **INITIAL_HEAD** (medido) | `822666002c12b1523876f3f4eb7336338b1b01a5` |
| **FINAL_HEAD** | o commit que traz este documento — um ficheiro nunca nomeia o commit que o contém |
| **WORKTREE** | `/home/user/eame-sintonia`, única e limpa |

**Drift medido, e não suposto:**

```
collection-operational-readiness-overnight-v1   822666002c12…   SEM DRIFT
sintonia-scrap-release-candidate-v1             de38f81639…     SEM DRIFT
sintonia-eame-know-how-v1                       edb5b37e -> d37238c4   DRIFT (§105 novo)
```

O know-how **andou** entre o briefing e esta missão. Foi lido antes de se
escrever uma linha; o §105 é de outra frente e não toca nesta.

**A branch do SCRAP não foi tocada.** Nenhum merge, nenhum cherry-pick.

> ⚠️ O nome da branch é `…-0qk2gr` e não `…-v1` como o briefing pedia: a branch
> de desenvolvimento é imposta ao ambiente desta sessão. O conteúdo é o da
> missão.

---

# B · CONTRACT

| campo | valor |
|---|---|
| **TEXT_OWNER** | `regras/proveniencia.py` |
| **TEXT_CONTRACT_OWNER_COUNT** | **1** — provado por varredura da árvore, não por afirmação |
| **CANONICAL_REPRESENTATION** | `TEXT_UNITS` — lista de unidades, não um campo |
| **TEXT_KIND_ENUM** | `AUTHOR_TEXT` · `NATIVE_CAPTION` · `TRANSCRIPT` · `ASR` · `PAGE_TEXT` · `DOCUMENT_TEXT` · `UNKNOWN` |
| **LANGUAGE_MODEL** | por unidade, sempre declarada, nunca herdada nem inferida |
| **ORIGINAL_TRANSLATION_MODEL** | `TEXT_RELATION` — eixo próprio; a tradução aponta para o original por morada |
| **LINEAGE_MODEL** | `RAW_OBSERVATION_ID` · `SOURCE_ARTIFACT` · `DERIVATION_METHOD` · `TOOL` · `MODEL` |

### O dono não foi escolhido: foi encontrado

`regras/proveniencia.py` é o dono da espécie de um texto derivado **desde a C6**,
e ela escreveu porquê: *«ONE CONCEPT -> ONE OWNER. E o dono da procedência de um
texto derivado não é quem o colheu primeiro: é quem governa procedência.»*

Só que esse bloco **não existia nesta linha**:

```
regras/proveniencia.py   SCRAP  24 316 bytes      Collection  20 437 bytes
TEXT_KIND                SCRAP  10 ocorrências    Collection   0
```

```
A LEI QUE FALTA PODE NÃO FALTAR: PODE ESTAR DO OUTRO LADO DA CERCA.
```

### Dois eixos, e a razão é estrutural

Os quatro nomes da C6 **não conseguem escrever o ASR traduzido**: um Whisper que
traduz enquanto ouve produz texto que não é `ASR_LOCAL` (não está na língua
falada) nem `NATIVE_CAPTION_TRANSLATED` (não é legenda da plataforma). Sem nome,
ele vai parar ao nome mais parecido.

Os quatro nomes **continuam a resolver** e decompõem-se no par que sempre foram.
Há prova de que `serve_para_original` responde o mesmo nas duas formas.

### `CAPTION` deixou de ser um valor

```
coleta/comunicacao_coleta.py   'TEXT_KIND': 'CAPTION'   = o que o AUTOR escreveu
regras/proveniencia.py (C6)    NATIVE_CAPTION_*         = a faixa de LEGENDA
```

```
DOIS SIGNIFICADOS NUM TOKEN NÃO SÃO UM VOCABULÁRIO:
SÃO UMA COLISÃO COM AR DE ACORDO.
```

---

# C · PRODUCERS

Medido nos produtores **reais** desta árvore — cinco espécies, um campo:

| produtor | põe em `TEXT` | espécie | declarado agora |
|---|---|---|---|
| `social_rotas.mastodon_tag` | `content` sem tags | autor | `AUTHOR_TEXT` · `ORIGINAL` · língua do autor |
| `social_rotas.mastodon_conta_statuses` | `content` sem tags | autor | `AUTHOR_TEXT` · `ORIGINAL` · língua do autor |
| `social_rotas.bluesky_feed_autor` | `record.text` | autor | `AUTHOR_TEXT` · `ORIGINAL` · `langs[0]` |
| `social_rotas.bluesky_buscar_contas` | `description` | **bio de perfil** | `AUTHOR_TEXT` · `ORIGINAL` · **sem língua** |
| `social_rotas.telegram_canal` | `_sem_tags(html)[:4000]` | **página raspada** | `PAGE_TEXT` · `ORIGINAL` |
| `youtube_oficial.buscar` | `snippet.description` | autor | `AUTHOR_TEXT` · `ORIGINAL` |
| `youtube_oficial.uploads_recentes` | `snippet.description` | autor | `AUTHOR_TEXT` · `ORIGINAL` |
| `youtube_oficial.metadata` | `snippet.description` | autor | `AUTHOR_TEXT` · `ORIGINAL` · `defaultLanguage` |
| `youtube_oficial._comentario` | `textOriginal` | comentário | `AUTHOR_TEXT` · `ORIGINAL` |
| `orquestrador` (rota documental) | texto de PDF | **extracção de máquina** | `DOCUMENT_TEXT` · linhagem com `RAW_ASSET_ID` |
| `adaptador_youtube.…_legenda_paga` *(linha do SCRAP)* | `it['transcript']` | **a FALA** | `TRANSCRIPT` |

**E o último já sabia que não sabia:** ele escreve
`'SPECIES': 'NOT_DECLARED_BY_PROVIDER'` dentro do `RAW`, porque o contrato não
tinha onde pôr a resposta.

```
UNKNOWN_PRODUCERS   quem não declarar continua a produzir envelope válido,
                    e a unidade nasce UNKNOWN / NOT_DECLARED.
                    O DEFEITO NÃO SE APAGA — PASSA A VER-SE.
```

### `defaultAudioLanguage` não é a língua da descrição

Um detalhe que só aparece a medir: `youtube_oficial.metadata` tem dois campos de
língua. `defaultAudioLanguage` fala do **áudio**; `defaultLanguage` fala dos
**metadados** — e a descrição é metadado. Dar ao texto a língua do áudio seria
declarar uma coisa medindo outra. A unidade leva `defaultLanguage`; a publicação
continua a levar o que sempre levou.

---

# D · ADMISSION

| campo | valor |
|---|---|
| **OLD_INPUT** | `item['texto']` |
| **NEW_INPUT** | `item['texto']` — **o mesmo** |
| **SELECTION_RULE** | `regras/proveniencia.escolher_para_leitura`, aplicada **uma vez** em `ingresso.para_a_porta` |
| **JUDGMENT_CHANGED** | **NO** |

**A admissão não foi alterada.** Nem uma linha. O briefing diz *«não alterar
Admission para acomodar SCRAP; a Collection deve entregar o contrato correto»*, e
é o que acontece: a porta continua a ler `texto`, e agora recebe-o com espécie ao
lado (`texto_especie`, `texto_relacao`, `texto_lingua`, `texto_unidade`,
`texto_escolha_porque`).

### A regra, e porque não podia ser «o primeiro»

`admissao._do_universo` casa contra léxico **italiano e português** — o próprio
ficheiro tem a medição: *«1 de 28 palavras aparecia lá»*. Entregar a tradução
inglesa a quem mede o original italiano **muda a resposta e não deixa marca**.

```
1 · ORIGINAL antes de TRANSLATED, e TRANSLATED antes de UNKNOWN
2 · depois, por quantas máquinas há entre o autor e o texto:
    AUTHOR_TEXT · NATIVE_CAPTION · TRANSCRIPT · ASR · PAGE_TEXT · DOCUMENT_TEXT · UNKNOWN
3 · empate só entre iguais nos dois eixos, e desempata a MORADA DECLARADA
```

### A prova de que o julgamento não mexeu

Não é uma afirmação: é um A/B contra um worktree **pristino** em `82266600`, com
o corpus italiano real da árvore.

```
58 itens × 3 universos = 174 vereditos
DIFERENÇAS = 0  (byte a byte)

T2 NAO_SE_APLICA  58        T7 SIM  42 · NAO_SEI 16
                            T9 NAO  42 · NAO_SEI 16
```

Itens **sem** `TEXT_UNITS` não tocam no bloco novo — `para_a_porta` salta-o
inteiro. O caminho antigo é, por construção, o caminho antigo.

---

# E · E1–E7

Com o código **real** da Collection, entrada controlada equivalente ao SCRAP,
storage inteiramente descartável, e **zero ficheiros escritos no checkout**:

| | CASE 1 autor | CASE 2 legenda | CASE 3 transcrição | CASE 4 desconhecido |
|---|---|---|---|---|
| E1 contrato aceita | PASS | PASS | PASS | PASS |
| E2 lei deixa passar | PASS | PASS | PASS | PASS |
| E3 ingresso aceita | PASS | PASS | PASS | PASS |
| E4 RAW preservado | PASS | PASS | PASS | PASS |
| E5 unidade canónica | PASS | PASS | PASS | PASS |
| E6 admissão julga | PASS | PASS | PASS | PASS |
| **E7 texto COM espécie** | **PASS** | **PASS** | **PASS** | **PASS** |
| espécie preservada | `AUTHOR_TEXT·ORIGINAL·it` | `NATIVE_CAPTION·ORIGINAL·it` | `TRANSCRIPT·UNKNOWN·UNKNOWN` | `UNKNOWN·UNKNOWN·UNKNOWN` |

```
TEXT_KIND_LOSS = 0
FIRST_LOST_EDGE = NENHUMA — o texto atravessa com espécie
FILES_WRITTEN_IN_CHECKOUT = 0
REAL_NETWORK = 0 · APIFY_RUNS = 0 · PAID_USD = 0
```

**No CASE 2 a tradução vem PRIMEIRO na lista, de propósito** — se a regra fosse
«o primeiro», o caso passava a inglês e ninguém via.

### E7 mede o contrato, e não o valor

A aresta antiga perguntava `bool(unidade.get('texto'))`. Com essa pergunta,
`texto = TEXT` teria passado — com a espécie apagada.

```
UMA ARESTA QUE SÓ PERGUNTA PELO VALOR NÃO MEDE O CONTRATO.
```

---

# F · RED TEAM

```
ATAQUES = 15        SURVIVORS = 0
```

| # | ataque | o que o mata |
|---|---|---|
| 1 | legenda tratada como transcrição | valores distintos + espécie atravessa até à porta |
| 2 | transcrição tratada como legenda | idem, e traduzir **não muda a espécie** |
| 3 | ASR tratado como texto do autor | valores distintos; ASR sem ferramenta é recusado |
| 4 | tradução tratada como original | tradução sem `TRANSLATED_FROM` é recusada |
| 5 | original substituído pela tradução | a ordem canónica escolhe o original |
| 6 | língua inferida do texto | língua só declarada; a da publicação não desce |
| 7 | `UNKNOWN` promovido | invariante **bicondicional** espécie ↔ base |
| 8 | linhagem removida | unidade sem `LINEAGE` é recusada |
| 9 | `RAW_OBSERVATION_ID` perdido | campo exigido; ausência declarada, nunca calada |
| 10 | SHA como identidade | `TEXT_UNIT_ID` com cara de hash é recusado |
| 11 | campo legado a ignorar o contrato | `ingresso.TextoEmConflito` |
| 12 | Admission pelo caminho antigo | a porta lê o que o selector escolheu |
| 13 | dois mappers para o mesmo conceito | varredura: **um** ficheiro declara `TEXT_KINDS` |
| 14 | ausência a virar string vazia | sem texto legível **não há campo** `texto` |
| 15 | «o primeiro» sem regra | ordem canónica + motivo escrito no item |

### Dois achados do red team contra o meu próprio código

**A guarda do `INFER` era código morto.** Estava depois da verificação de
vocabulário, que já barra `INFERRED_FROM_TEXT`. Nunca corria.

```
UMA GUARDA QUE NUNCA CORRE NÃO PROTEGE NADA,
E ENSINA O PRÓXIMO LEITOR A CONFIAR NELA.
```

**A invariante do `UNKNOWN` só guardava um lado.** Exigia base `NOT_DECLARED`
para espécie desconhecida — e deixava passar o contrário: uma unidade que
ninguém declarou a dizer-se `AUTHOR_TEXT`. **É por aí que a promoção silenciosa
entra**: não pela porta de quem admite não saber, mas pela de quem passa a
afirmar. Agora é bicondicional.

```
ESPÉCIE CONHECIDA <-> ALGUÉM A DECLAROU.
AS DUAS IMPLICAÇÕES, OU A QUE FALTA É POR ONDE SE PASSA.
```

---

# G · MUTATION

```
MUTANTES = 6 eixos        SURVIVORS = 0
```

`TEXT_KIND` · `TEXT_RELATION` · a base · o método de derivação · a **ordem da
escolha** · o tratamento do `UNKNOWN`.

A mutação da ordem é a que prova que a regra decide: trocar
`ORDEM_DA_RELACAO` faz a porta ler a tradução em vez do original. Se trocá-la não
mudasse nada, a ordem seria decorativa.

---

# H · REGRESSION

Medido no **mesmo ambiente**, com o mesmo comando
(`python3 -m unittest discover -s tests`):

```
BASE_TOTAL      2633        FINAL_TOTAL     2698
BASE_FAILURES     20        FINAL_FAILURES    15
BASE_ERRORS        2        FINAL_ERRORS       2
BASE_SKIPS       183        FINAL_SKIPS      183

NEW_FAILURES       0
FIXED_FAILURES     5
```

**65 provas novas.** Comparação por **identidade**, não por quantidade: os testes
vermelhos finais são exactamente os mesmos da base, pelo nome.

As 5 que ficaram verdes são marcadores `TEST_COUNT_CURRENT` desactualizados
(declaravam `1.651` numa suíte de 2 633). O sync é o mecanismo declarado da casa
— *«o teste reprova, o sync conserta»* — e a minha mudança mexeu no número
publicado, portanto corrigi-lo é arrumação, não âmbito novo.

---

# I · SYSTEM MAP

A cadeia foi **lida** de `CADEIA-DO-MAPA.json` e corrida inteira — sete passos de
regeneração e um de validação, sem assumir quantos eram.

O validador reprovou à primeira, e tinha razão nas duas:

```
P9_CODIGO_DECLARADO   a prova nova não pertencia a peça nenhuma
P1_SEM_DRIFT          o mapa commitado era o da árvore anterior
```

A prova entrou em `C-PROVA-COLETA`. E uma linha regerada **não é ruído**:
`regras/LEIA-ANTES-DE-COLETAR.md` passou a listar `C-INGRESSO` entre quem importa
a lei da procedência em runtime — medido pelo scanner, porque a porta passou
mesmo a depender do dono da espécie do texto.

```
SYSTEM_MAP_CHECK = PASS
```

---

# J · KNOW-HOW

**Medido antes de escrever:** `edb5b37e -> d37238c4`. O §104.6 já regista
*«passar texto é passar espécie, não só valor»* — **não se duplica**.

O que esta missão acrescenta é o que só apareceu ao **fechar** a aresta, e vai
proposto como **§106** para a branch canónica do know-how (que esta missão não
toca, por não ser a sua branch de desenvolvimento):

```
KNOW_HOW_DELTA = §106 proposto — ver abaixo
```

## §106 · O CONTRATO QUE FALTAVA ESTAVA DO OUTRO LADO DA CERCA

### 106.1 · MEDIR SE A LEI EXISTE ANTES DE A INVENTAR

O §104.6 fecha dizendo que a segunda decisão *«precisa de vocabulário que a porta
hoje não tem»*. Tinha — noutra branch. `regras/proveniencia.py` governa a espécie
do texto desde a C6, e a linha da Collection nunca recebeu esse bloco.

```
A LEI QUE FALTA PODE NÃO FALTAR: PODE ESTAR DO OUTRO LADO DA CERCA.
ANTES DE INVENTAR VOCABULÁRIO, PROCURAR O DONO NO GIT INTEIRO.
```

Inventar teria dado **dois donos** do mesmo conceito — que é exactamente o
defeito que a C6 tinha acabado de curar.

### 106.2 · UM TOKEN COM DOIS DONOS É UMA COLISÃO COM AR DE ACORDO

`CAPTION` significava «o que o autor escreveu» em `comunicacao_coleta.py` e «a
faixa de legenda do vídeo» na C6. A lei `CAPTION != TRANSCRIPT` estava escrita
**com um token que não tinha significado único** — o ataque já vivia no
dicionário, antes de haver código.

```
UMA LEI ESCRITA COM UM TOKEN DE DOIS DONOS NÃO SEPARA NADA.
```

### 106.3 · QUANDO UM NOME NÃO TEM PAR, O EIXO ESTÁ DOBRADO

`NATIVE_CAPTION_ORIGINAL` tem par; `ASR_LOCAL` não tem. Essa assimetria não é
estética: é a prova de que dois eixos estavam somados num nome só — e a
combinação que falta **vai parar ao nome mais parecido**, em silêncio.

```
UM NOME SEM PAR NUM VOCABULÁRIO SIMÉTRICO É UM EIXO POR SEPARAR.
```

### 106.4 · UMA INVARIANTE COM UMA IMPLICAÇÃO GUARDADA É UMA PORTA COM UMA DOBRADIÇA

Guardar «espécie desconhecida ⟹ ninguém declarou» e não o contrário deixa entrar
«ninguém declarou ⟹ e mesmo assim é `AUTHOR_TEXT`». **A promoção silenciosa não
entra pela porta de quem admite não saber: entra pela de quem passa a afirmar.**

```
ESPÉCIE CONHECIDA <-> ALGUÉM A DECLAROU. AS DUAS IMPLICAÇÕES, OU
A QUE FALTA É POR ONDE SE PASSA.
```

### 106.5 · UMA GUARDA DEPOIS DA LISTA FECHADA NUNCA CORRE

Verificar «a base contém `INFER`?» **depois** de verificar «a base está na
lista?» é código morto: a lista já barrou o valor. Uma guarda que nunca corre é
pior do que nenhuma — ensina o próximo leitor a confiar nela.

```
LEI SOBRE UM VALOR QUE A LISTA JÁ RECUSOU MEDE-SE NA LISTA, NÃO NO VALOR.
```

### 106.6 · «O PRIMEIRO DA LISTA» É UMA REGRA QUE NINGUÉM DECIDIU

Quando N unidades chegam e quem julga lê uma, há sempre uma regra. A questão é se
ela está escrita.

```
PEGAR NO PRIMEIRO É UMA REGRA QUE NINGUÉM DECIDIU, QUE NINGUÉM
CONSEGUE LER, E QUE MUDA QUANDO A ORDEM MUDA.
```

E a escolha tem de ficar **escrita no item**: sem isso, quem lê o veredito não
consegue saber que texto o sustentou.

### 106.7 · ONDE UM CAMPO PASSA NÃO É DE QUEM ELE É

Pôr `TEXT_UNITS` na lista dos campos que o coletor declara pareceu óbvio e
rebentou: essa lista alimenta a **ficha do artefato**, e a ficha é metadado, não
conteúdo. O ficheiro já o dizia — *«o item manda no conteúdo»*. O texto atravessa
porque o tradutor deixa passar intacto o que não está no mapa de nomes.

```
ACRESCENTAR UM CAMPO A UMA LISTA PORQUE ELE PRECISA DE VIAJAR
É CONFUNDIR «POR ONDE PASSA» COM «DE QUEM É».
```

### 106.8 · A TRAVESSIA APLICA-SE ONDE TODAS AS ROTAS PASSAM

A escolha do texto esteve, por um momento, em `unidade_para_a_porta`. A rota
documental **nunca passa por lá** — o documento estruturado ficaria sem espécie e
a rota social com ela. Duas rotas a entregar coisas diferentes à mesma porta é o
defeito que o tradutor único já tinha curado para os dez nomes do contrato comum.

```
UMA TRAVESSIA, UM TRADUTOR, NA FRONTEIRA. O TEXTO NÃO É EXCEPÇÃO.
```

### 106.9 · CONSEQUÊNCIA

```
· antes de inventar vocabulário, procurar o dono no git inteiro
· token com dois significados não separa nada — renomear é a cura
· nome sem par num vocabulário simétrico é eixo por separar
· invariante guarda-se nas duas direcções, ou a que falta é a entrada
· guarda depois da lista fechada é código morto com ar de lei
· escolher entre N exige regra escrita, e a escolha fica no item
· campo que precisa de viajar não pertence à lista da ficha
· a travessia aplica-se onde TODAS as rotas passam
```

**Medido:** 15 ataques · 0 sobreviventes · 6 eixos mutados · 0 sobreviventes ·
`NEW_FAILURES = 0` · 174 vereditos reais byte a byte iguais ·
`REAL_NETWORK = 0` · `PAID_USD = 0`.

---

# K · O QUE FICA PARA O COORDENADOR

```
SCRAP_MAPPER_PENDING    uma linha em `coleta/scrap_colheita.py`:
                            fora[pv.CAMPO_DAS_UNIDADES] = pv.unidades_do_envelope(objeto)
                        A branch do SCRAP não se toca nesta missão.
                        Até lá, o envelope do SCRAP atravessa pela ponte do
                        legado — com espécie UNKNOWN. Não perde texto;
                        declara que não sabe.

KNOW_HOW_§106           proposto aqui; a branch canónica do know-how não é a
                        branch de desenvolvimento desta missão.

G-ENV-02 · G-RUN-02     dívidas da linha da Collection. E7 não dependia delas,
                        e não foram tocadas.
```

## CRITÉRIO DE PASS

```
TEXT_CONTRACT_OWNER_COUNT       = 1
TEXT_KIND_PRESERVED             = PASS
LANGUAGE_PRESERVED              = PASS
ORIGINAL_TRANSLATION_SEPARATED  = PASS
CAPTION_TRANSCRIPT_SEPARATED    = PASS
LINEAGE_PRESERVED               = PASS
UNKNOWN_NOT_PROMOTED            = PASS

E1 = E2 = E3 = E4 = E5 = E6 = E7 = PASS

SURVIVING_ATTACKS               = 0
SURVIVING_MEANINGFUL_MUTANTS    = 0
NEW_FAILURES                    = 0
SYSTEM_MAP_CHECK                = PASS

TEXT_CONTRACT   = PASS
COLLECTION_E7   = PASS
VERDICT         = PASS
```
