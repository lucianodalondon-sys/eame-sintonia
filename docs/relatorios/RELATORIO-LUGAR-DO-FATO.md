# O LUGAR DO FATO GANHA DONO — as cinco últimas cicatrizes

**Data:** 2026-08-30 · **Branch:** `claude/sintonia-eame-collection-es` · **Base:** `e2ae446`
**Banco:** PostgreSQL 16 local e descartável. **Supabase de produção não foi tocado.**

As cinco cicatrizes que a conferência de localização abriu duas rodadas atrás fecharam.
Nenhuma foi promovida para que isso acontecesse: a migration 018 deu à lei do lugar do
fato um dono capaz de expressá-la, e aposentou o dono antigo em vez de duplicá-lo.

---

## B · O MAPA EXATO — cada BR, a lei que ela é

Lido da matriz canônica, não inferido pelo número. **São cinco e não quatro** porque a
rodada da conferência resumiu quatro lacunas *não consertadas* (A, E, F, G) e uma
*parcialmente consertada*: BR-34 teve corrigida a metade que dava resposta errada — a
data de publicação virando `UNRELATED` — e permaneceu PARTIAL porque o **campo** do tempo
do fato não existia. Quatro intocadas + uma pela metade = cinco.

| BR | A lei | Dono antes | Lacuna | Mudança mínima |
|---|---|---|---|---|
| **BR-26** | `BASE ≠ OPERATING ≠ INFLUENCE ≠ FACT` | `conteudo.source_geografia_id` e `fact_geografia_id` (003) separavam **duas** das quatro | BASE, OPERATING e INFLUENCE colapsavam todos na praça da fonte | `origem_lugar`, com PAPEL em linha — a ação mínima que a própria conferência escrevera |
| **BR-30** | um conteúdo tem **0..N** lugares do fato | ninguém | `fact_geografia_id` é UMA coluna: 0..1 | `conteudo_lugar`, e a coluna antiga **aposentada** |
| **BR-31** | `GEO_PRECISION` é dado | `precisao_da_geografia()` (015): PAIS/REGIAO/PROVINCIA | a escada parava em PROVINCIA | município, localidade e coordenada na escada |
| **BR-32** | `TERRITORIAL_LIST ≠ FACT_LIST` | a guarda existia no eixo do **produto** (`ESPECTRO_DE_PRODUTO`) | não havia equivalente no eixo da **geografia** | papel `LISTA_TERRITORIAL` + lista branca das origens que sustentam o fato |
| **BR-34** | `PUBLISHED_AT ≠ FACT_TIME` | `f_relevancia_ao_caso` (017) já decidia numa direção só | faltava o **campo** do tempo do fato | `conteudo.fact_tempo_*`, reusando `resolucao_temporal` da 009 |

## C · ANTES E DEPOIS

| BR | antes | depois |
|---|---|---|
| BR-26 | PARTIAL | **PROVED** |
| BR-30 | ABSENT | **PROVED** |
| BR-31 | PARTIAL | **PROVED** |
| BR-32 | PARTIAL | **PROVED** |
| BR-34 | PARTIAL | **PROVED** |

Os cinco de infraestrutura (BR-14, BR-16, BR-19, BR-20, BR-21) **não foram reabertos** e
há teste de controle que reprova se algum sair de PROVED.

## D · AS QUATRO ESPÉCIES DE LUGAR

Duas tabelas, e não uma, porque as espécies têm **sujeitos diferentes**: BASE, OPERATING e
INFLUENCE são de quem fala; FACT é do que ele escreveu.

```
origem_lugar    (origem_id, geografia_id, papel, origem_do_dado, evidencia)
                 papel ∈ BASE · OPERATING · INFLUENCE      ← FACT não está aqui
conteudo_lugar  (conteudo_id, lugar_texto, geografia_id, papel, …)
                 papel ∈ FACT · EVENT · OPERATING_MENCIONADO · AREA_COMERCIAL
                       · LISTA_TERRITORIAL · MENCAO_APENAS · NAO_SEI
```

O caso obrigatório está no ensaio e coexiste sem sobrescrita: pesquisador **baseado** em
Foggia, instituição **atuando** nacionalmente, **audiência** italiana, **fato** em
Grosseto. `FACT` não existe no vocabulário de `origem_lugar` — não há como declarar que a
sede de alguém é o lugar de um fato, e a mutação confirma que a trava é o que segura.

## E · 0..N LUGARES DO FATO

`fact_places` é **array**. O documento de três províncias tem três linhas, cada uma com a
sua evidência e a sua âncora. E o dono antigo **não existe mais**:

> Deixar `conteudo.fact_geografia_id` viva ao lado da tabela criaria dois donos da mesma
> lei — o defeito que a 016 já cometeu uma vez, com um índice único que duplicava a chave
> natural da 003. Naquela vez o banco recusou. Aqui ninguém recusaria: as duas estruturas
> conviveriam em silêncio e um dia responderiam coisas diferentes.

Três views da 009 liam a coluna e foram refeitas sobre `v_conteudo_fact_country` — que é o
único dono da pergunta "que países o fato deste conteúdo toca", em vez de cada view
reimplementar o join e divergir com o tempo.

## F · A ESCADA DE PRECISÃO

`PAIS < REGIAO < PROVINCIA < MUNICIPIO < LOCALIDADE < COORDENADA`, derivada da **linha** e
nunca do texto. Cada país nomeia os degraus como quiser — o degrau é do contrato, o nome é
do país, e `COUNTRY_ISOLATION` continua intacta.

## G · `SOURCE_GEOGRAPHY ≠ ADMIN_GEOGRAPHY`

A lei que a Itália provou em texto real depois da conferência. `geografia.especie` separa
`ADMIN` de `DEFINIDA_PELA_FONTE`, `ZONA_AGRONOMICA` e `OUTRA`. *"l'Ovest"* é guardado
inteiro em `nome_da_fonte` e **não entra na escada administrativa**: a régua devolve
`ZONA_DEFINIDA_PELA_FONTE`, com ordem 0.

Ordem 0 não quer dizer "menos preciso que província". Quer dizer **incomparável** — e
`mais_especifico_que()` devolve `None`, não `False`, quando se tenta comparar os dois.

## H · `TERRITORIAL_LIST ≠ FACT_LIST`

*"operiamo in Torino, Piacenza e Bergamo"* fica no banco com `papel = LISTA_TERRITORIAL`.
Guardá-la é o que permite **provar** que ela não virou ocorrência — recusar sem rastro não
prova nada.

**E aqui o red team achou um defeito meu.** A primeira versão da 018 tinha *duas* travas:
a lista branca (`ESCRITO`/`CITADO`) e uma só para a lista territorial. A mutação mostrou
que a segunda **nunca disparava** — a lista já caía na primeira. Trava que nunca dispara é
pior que nenhuma: dá a impressão de que a lei tem guarda própria. Foi removida, e o
**conteúdo** da lista branca virou teste, porque alargá-la mataria três leis de uma vez
(`LOCAL_DA_FONTE`, `DEDUZIDO`, `TERRITORIAL_LIST`) sem que nada mais reprovasse.

## I · `OCCURRENCE ≠ INCIDENCE`

`tipo_de_evidencia` é obrigatório em todo lugar do fato, e
`f_ocorrencia_nao_e_incidencia()` devolve a contagem **por espécie** — nunca um total.
Cinco amostras de diagnóstico e um comunicado regional não fazem "seis ocorrências", e
nenhum dos dois autoriza dizer incidência. Nenhuma coluna de score nasceu.

## J · `ROW_PROVENANCE ≠ VALUE_PROVENANCE`

Cada linha de `conteudo_lugar` e de `origem_lugar` carrega a **sua** `origem_do_dado`,
`evidencia` e `ancora`. Um conteúdo pode ter BASE sustentada por perfil, OPERATING por bio
e FACT por frase do post — três proveniências, três linhas.

## K · TEMPO DO FATO

```
publicado_em          2026-02-13
fact_tempo_texto      stagione 2025
fact_tempo_resolucao  SEASON
fact_tempo_origem     AMARRADO_AO_ACONTECIMENTO
```

`PUBLICACAO` **não existe** no vocabulário de origem do tempo, e a ausência é a trava: não
há valor que permita declarar que o tempo do fato veio do carimbo. Uma série histórica
`2011-2025` não é uma safra, e o leitor italiano a descarta como `SERIES_RANGE_NOT_FACT_TIME`.

## L · `NOT_IN_GAZETTEER ≠ NOT_A_PLACE ≠ REJECTED_BY_LAW`

`lugar_texto` é obrigatório e `geografia_id` é opcional. Um comune que a lista auxiliar não
conhece continua no banco, com `estado_do_lugar = NAO_ESTA_NO_GAZETTEER` e precisão
`NOT_KNOWN`. A nossa lacuna não vira lacuna do mundo.

## M · CÓDIGO REUTILIZADO DA ITÁLIA · N · `DUPLICATE_OWNER_CREATED = NO`

`scripts/fato_local.py` veio **portado verbatim** da branch da Itália, com nota de
proveniência. Ele é o **leitor italiano**: gazetteer, âncoras e meses em italiano, tudo do
piloto. A **lei** que ele exerce subiu para `scripts/lugar_do_fato.py`, no core, sem
vocabulário italiano nenhum — e há teste que reprova se `Toscana`, `constatat` ou
`campioni` aparecerem lá.

Os três lugares onde a lei existe — core, leitor, banco — são comparados por
`tests/test_lugar_do_fato.py`. O vocabulário do banco é lido **do banco**, não de uma
expressão regular sobre a migration: a primeira versão desse teste casava o `check` errado,
que é um parser de SQL improvisado dentro de um teste.

## O · P · BACKTESTS

Nenhuma fixture bonita: cada caso é a forma de um falso positivo já medido.

| origem | caso | resultado |
|---|---|---|
| Itália | Bergamo = sede, Grosseto = foco | só Grosseto é FACT; Bergamo é `MENCAO_APENAS` |
| Itália | convegno a Torino, relatore di Piacenza | os dois recusados; só Siena é FACT |
| Itália | *"l'Ovest"* | `ZONA_DEFINIDA_PELA_FONTE`, não região |
| Itália | 13/02/2026 + *stagione 2025* | `FACT_TIME = stagione 2025`; a publicação vira `PUBLICATION_STAMP` |
| Itália | série 2011–2025 | descartada como `SERIES_RANGE`, não vira safra |
| Brasil | lista territorial econômica | três lugares, zero ocorrências |
| Brasil | vários municípios num documento | três FACTs, não um |
| Brasil | endereço da fonte como FACT | recusado pela lista branca |
| Brasil | amostras positivas | `DIAGNOSTIC_SAMPLE`; `INCIDENCE = NOT_KNOWN` |
| EAME | Toscana / Grosseto | fonte em Foggia, fato na Toscana; nenhuma virou a outra |

## Q · R · REGRESSÕES E MUTAÇÕES

```
regressoes_calendario       45
regressoes_captura          19
regressoes_cicatrizes       33
regressoes_coleta           21
regressoes_lugar_do_fato    41
                           ───
                           159 afirmações · 0 falhas

mutações                    23 · todas pegaram · 0 erros
testes Python              643 · todos verdes
```

O red team correu os doze ataques da missão. Além do achado da trava redundante, ele
expôs um segundo defeito de método: **três mutações da suíte antiga apontavam para a coluna
aposentada e ERRAVAM em vez de rodar** — e o `grep "NAO PEGOU"` do CI não via a diferença
entre uma mutação que não pegou e uma que não chegou a existir. O CI agora reprova as duas.

## S · FRESH DATABASE

```
001–007 · 009 · 010–012 · 013 · [014 reservada] · 015 · 016 · 017 · 018 · 008 por último
```

16 migrations do zero, `008` conferindo no fim, fixture ES e quatro ensaios carregados, as
cinco suítes verdes e as 23 mutações pegando. O 014 continua vago de propósito.

## T–X · VEREDITO

```
LOCATION_CONTRACT_COMPLETE        YES   ← DERIVADO da matriz, não escrito
LOCATION_IS_PART_OF_COLLECTION_ENTRY_GATE   YES

CATALOG_IMPORT_ENGINEERING_GATE   READY     16/16 cicatrizes PROVED
EAME_COLLECTION_ENTRY_GATE        READY     35/35 cicatrizes PROVED

RAW_PRESERVATION_GATE             OPEN_EXTERNAL_REPAIR   → hoje CLOSED
  EXPECTED 196 · PRESENTES 185 · AUSENTES 11 · ÓRFÃOS 0 · HASH_MISMATCH 0
  HTTP 400 InvalidKey — object key com caractere não-ASCII
  reparo em curso na máquina espanhola · VERIFICADO_DAQUI = NO

IMPORT_CAN_BE_NEXT_MISSION        NO                     → hoje YES
```

`IMPORT_CAN_BE_NEXT_MISSION` exige o portão do catálogo READY **e** o RAW gate CLOSED. O
portão está READY; o RAW estava `OPEN_EXTERNAL_REPAIR`, com 11 dos 196 assets ainda fora
do bucket. Onze arquivos são poucos e o defeito tem causa nomeada — e importar com o bruto
incompleto é importar sem poder voltar à evidência.

> **FECHOU DEPOIS.** O reenvio dos ausentes na máquina espanhola levou os 196 ao bucket, e
> `IMPORT_CAN_BE_NEXT_MISSION` passou a **YES** pela derivação. Ver
> `docs/relatorios/RELATORIO-FECHAMENTO-RAW-ES.md`.

**Nada foi importado. Nada foi aplicado no Supabase. A instrução era parar aqui.**
