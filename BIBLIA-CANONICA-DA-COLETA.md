# BÍBLIA CANÔNICA DA COLETA — SINTONIA

```
BIBLE_ID          SINTONIA-COLLECTION-BIBLE
VERSION           V1
STATUS            CANONICAL
EFFECTIVE_FROM    2026-09-07
CURRENT_PROFILE   ITALY_PROFILE_V1
CANONICAL_OWNER   este ficheiro, na raiz do repositório eame-sintonia
HEAD_AO_CONGELAR  56fdb8c
```

> **Esta é a constituição da coleta do SINTONIA.** Não é tutorial, não é descrição do
> código de hoje, não é proposta. É a lei que todo prompt futuro de coleta obedece.
>
> **Ela não recomeça a epistemologia do zero.** 63 leis e contratos maduros já existiam
> neste repositório e foram lidos, catalogados e incorporados — o censo está em
> [`docs/biblia/CENSO-DAS-LEIS-DA-COLETA.md`](docs/biblia/CENSO-DAS-LEIS-DA-COLETA.md).
> Onde uma lei já existia, esta Bíblia **aponta ou incorpora**; nunca cria uma segunda
> definição divergente.

## Relação com os outros donos de lei

| ficheiro | do que é dono |
|---|---|
| [`AGENTS.md`](AGENTS.md) | a lei do **System Map** e da prateleira. Esta Bíblia não a repete. |
| [`CLAUDE.md`](CLAUDE.md) | instruções permanentes e a lei de design |
| [`README.md`](README.md) | o método `SOURCE → EVIDENCE → … → PORTAL` e os 4 estados de evidência |
| **esta Bíblia** | **a lei da COLETA**: o que é coletar, quem manda, o que se preserva, como se prova |
| [`regras/LEIA-ANTES-DE-COLETAR.md`](regras/LEIA-ANTES-DE-COLETAR.md) | a porta de entrada gerada do mapa — lista as réguas vivas |

**Um dono. Múltiplos ponteiros.** Copiar uma lei daqui para outro ficheiro faz as duas
divergirem, e a partir daí nenhuma das duas vale.

---

## COMO LER UMA LEI

Cada lei tem um `ID` estável. **A numeração tem buracos de propósito:** `COL-LAW-NNN`
corresponde à secção `NNN` da missão fundacional que a criou, e essa rastreabilidade vale
mais que uma sequência bonita.

Palavras normativas: **DEVE** · **NÃO DEVE** · **PODE** · **RECOMENDADO**.

Cada lei carrega dois estados, e eles são coisas diferentes:

```
LAW_STATUS              CANONICAL   —  é lei
IMPLEMENTATION (IT)     IMPLEMENTED | PARTIAL | ABSENT | UNKNOWN   —  já funciona?
```

**«É lei» nunca significa «já funciona».** A matriz completa de conformidade da Itália está
em [`docs/biblia/CONFORMIDADE-ITALIA.md`](docs/biblia/CONFORMIDADE-ITALIA.md).

E cada lei declara a sua `ORIGEM`:

| origem | quer dizer |
|---|---|
| `EXISTING_SINTONIA_LAW` | já era lei aqui; a Bíblia aponta para o dono |
| `CONSOLIDATED_FROM_MULTIPLE` | existia espalhada e foi juntada |
| `ARCHITECTURAL_DECISION` | decisão fechada nesta missão |
| `ENGINEERING_PRINCIPLE` | princípio maduro de engenharia de ingestão, adotado |

---

# PARTE I · O QUE É A COLETA DO SINTONIA

## COL-LAW-005 · COLETAR NÃO É ADMITIR NEM JULGAR

**REGRA.** São três atos, com três donos.
`COLETAR` adquire evidência. `ADMITIR` decide se a evidência entra num universo.
`JULGAR` combina e interpreta depois.
Um coletor **NÃO DEVE** descartar evidência por opinião semântica — essa opinião pertence
a outra etapa. Exceção operacional (teto de volume, orçamento, tempo) **DEVE** ser
explícita e ficar registrada na corrida.

**POR QUÊ.** Enquanto o coletor julgava, o «não» não tinha testemunha: perdia-se o item e
perdia-se a informação de que aquela fonte entrega lixo. Na coleta seguinte gasta-se
máquina para redescobrir a mesma coisa.

**EXEMPLO.** O coletor de YouTube traz um vídeo sobre azeitona. Para o universo Ciência ele
pode ser `NÃO`; para Concorrente, `SIM`. O coletor traz; a porta decide, uma vez por par
(item, universo).

**VIOLAÇÃO.** `coleta/youtube_relevancia.py` era o único ficheiro em toda a coleta que
decidia relevância — dentro do coletor, para um canal de cinco.

**COMO PROVAR.** `py provas/testa_coleta_canonica.py` · o livro em
`data/samples/LIVRO-DE-DECISOES.json` tem uma linha por decisão, incluindo as negativas.

**CONTRATOS.** `admissao/admissao.py` · `pedido/orquestrador.py`
**ORIGEM.** `EXISTING_SINTONIA_LAW` (`docs/operacao/CENSO-DA-COLETA.md` §D)
**LAW_STATUS** `CANONICAL` · **IT** `PARTIAL`

---

# PARTE II · RAW, DERIVADO E LINHAGEM

## COL-LAW-006 · RAW PRIMEIRO

**REGRA.** `CAPTUROU → PRESERVA O ORIGINAL → DEPOIS DERIVA.`
O RAW **DEVE** ser gravado **antes** de qualquer normalização, extração, transcrição ou
classificação. O RAW **NÃO DEVE** ser sobrescrito por nenhum derivado.

**POR QUÊ.** Se o parser quebrar depois de o RAW estar gravado, a evidência sobrevive e o
parser conserta-se depois. Na ordem inversa, um parser com defeito apaga a única cópia.

**EXEMPLO.** A ordem obrigatória da execução italiana grava o RAW no passo 8 e torna-o
imutável no passo 11; normalizar é o passo 13.

**VIOLAÇÃO.** Ler o dataset de uma execução **ainda em curso** e gravar esse pedaço como
`RAW_EVIDENCE_STATE: PRESERVED` — 21 manifestos desta casa carregam
`"ERROR": "status da plataforma: READY."` por causa disso.

**COMO PROVAR.** `coleta/coletor.py` grava o RAW antes de normalizar ·
`docs/operacao/ITALY-FORWARD-ONLY-SCHEDULING-V1.md` §8 · campo
`RAW_PRESERVED_BEFORE_PARSE` em `data/collection-ledger/italy/observations.ndjson`

**ORIGEM.** `EXISTING_SINTONIA_LAW` · **LAW_STATUS** `CANONICAL` · **IT** `IMPLEMENTED`

---

## COL-LAW-007 · RAW NÃO É DERIVADO

**REGRA.** São espécies diferentes e **NÃO DEVEM** ocupar o mesmo campo:

```
PDF_RAW    ≠  PDF_TEXT
VIDEO_RAW  ≠  TRANSCRIPT
HTML_RAW   ≠  EXTRACTED_ARTICLE
API_RAW    ≠  NORMALIZED_RECORD
BROWSER_RENDERED_EXTRACT  ≠  RAW_PRESERVED
TRANSCRIPT_ORIGINAL       ≠  TRANSLATION
```

`TRANSLATION: null` significa **não traduzido**, nunca «igual ao original».

**POR QUÊ.** Um extrato de navegador é o que o navegador *renderizou*, não o que o servidor
*entregou*. Tratá-lo como RAW faz uma interpretação passar por evidência.

**VIOLAÇÃO.** `IT-T9-008` (ADAMA Itália) e `IT-T9-002` (Bayer): não há caminho honesto para
virar `RAW_PRESERVED` enquanto o servidor recusar cliente sem navegador. **Não forçar.**

**COMO PROVAR.** `docs/fontes/ITALY-SOURCE-CONTRACT-MATRIX-V1.md` ·
`node regras/italy_source_health.mjs --negativos`

**ORIGEM.** `EXISTING_SINTONIA_LAW` · **LAW_STATUS** `CANONICAL` · **IT** `IMPLEMENTED`

---

## COL-LAW-008 · DERIVAÇÃO TEM LINHAGEM

**REGRA.** Todo derivado **DEVE** responder `DERIVED_FROM = artifact_id`, e preservar quando
aplicável: `parent_artifact_id` · `derivation_type` · `derivation_actor` ·
`derivation_version` · `derived_at`.
Cópia órfã **NÃO DEVE** existir.

**POR QUÊ.** Sem pai, um texto extraído é indistinguível de um texto digitado.

**COMO PROVAR.** a cadeia inversa `CONTENT → RUN_ID → RUN_MANIFEST → INPUT / ACTOR /
DATASET / RAW`, exercida em `regras/proveniencia.py`.

**ORIGEM.** `CONSOLIDATED_FROM_MULTIPLE` · **LAW_STATUS** `CANONICAL` · **IT** `PARTIAL`
*(a cadeia existe para a rota paga; os derivados de PDF/HTML italianos não declaram `parent_artifact_id`)*

---

# PARTE III · ENTIDADES FUNDAMENTAIS

## COL-LAW-009 · FONTE, ENDPOINT, ROTA, EXECUTOR, ITEM E ARTEFATO SÃO SEIS COISAS

**REGRA.** Nenhuma **DEVE** substituir outra num contrato.

| entidade | a pergunta que ela responde | exemplo |
|---|---|---|
| `SOURCE` | quem publica / mantém | ARPAV Veneto |
| `ENDPOINT` | onde tecnicamente se acessa | a URL do boletim da zona 7 |
| `ROUTE` | por que meio se chega | HTTP · navegador · Apify |
| `EXECUTOR` | que peça desta casa vai buscar | `coleta/italy_recurrent_collect.mjs` |
| `DISCOVERED ITEM` | o que se achou lá | o boletim da zona 7 de hoje |
| `ARTIFACT` | a evidência efetivamente preservada | o PDF, com SHA-256 |

**POR QUÊ.** Esta casa já respondeu isto errado: a gaveta chamada «OS VEÍCULOS» passou meses
sem conter um único veículo — as oito peças lá dentro eram todas **ações**. O teste usado
(*«sai para a rede?»*) não separava nada.

**REGRA IRMÃ, já madura.** **FERRAMENTA** é *com que* se viaja · **VEÍCULO** é *de onde* o
dado vem · **AÇÃO** é *quem vai buscar e guarda*. Três gavetas: `ferramentas/`, nenhuma,
`coleta/`.

**COMO PROVAR.** `AGENTS.md` §«Ferramenta, veículo e ação são TRÊS coisas» ·
`py system-map/tests/test_system_map.py`

**ORIGEM.** `EXISTING_SINTONIA_LAW` · **LAW_STATUS** `CANONICAL` · **IT** `IMPLEMENTED`

---

# PARTE IV · CONTROL PLANE — O PEDIDO E O ORQUESTRADOR

## COL-LAW-010 · UM PEDIDO NÃO CONHECE IMPLEMENTAÇÃO

**REGRA.** O `COLLECTION_REQUEST` diz **O QUE SE QUER**. **NÃO DEVE** conter: nome de
script, nome de função, `Apify`, `browser`, caminho de ficheiro ou detalhe de runner.
**PODE** conter: `target` · `country_scope` · `mode` · `trigger` · `filters` · `budget` ·
`priority` · `deadline` · `requested_by`.

**Acionamento e escopo são dois eixos, não um.** Uma coleta `TOTAL` pode ser `MANUAL`; uma
`INCREMENTAL` pode ser `AGENDADA`.

**POR QUÊ.** O censo mediu **79 pontos de entrada em 92 ficheiros de coleta**. Setenta e
nove maneiras de começar uma coleta não são «uma coleta»: são setenta e nove. Cada
consumidor ficava preso ao nome de um script, e trocar o executor por outro melhor obrigava
toda a casa a mudar.

**EXEMPLO.** `«colete materiais novos de pesquisadores da Espanha sobre cereais»` →
`alvo=T7 · acionamento=MANUAL · escopo=INCREMENTAL · filtros={pais: ES, tema: cereais}`.

**VIOLAÇÃO.** Um botão do GitHub Actions que conhece a linha de comando do script.

**O QUE NÃO SE FINGE.** `AUTOMATICO_EVENTO` está declarado porque a arquitetura o prevê e é
**recusado com o motivo escrito**, porque nenhum disparo por acontecimento foi medido neste
repositório. Aceitá-lo seria prometer o que ninguém cumpre.

**COMO PROVAR.** `py pedido/pedido.py "colete concorrentes"` · `provas/testa_coleta_canonica.py`

**ORIGEM.** `EXISTING_SINTONIA_LAW` (`pedido/pedido.py`) · **LAW_STATUS** `CANONICAL` · **IT** `IMPLEMENTED`

---

## COL-LAW-011 · UM ÚNICO DONO DA ORQUESTRAÇÃO

**REGRA.** A pergunta «COMO ATENDER ESTE PEDIDO?» **DEVE** ter um dono só: o
**ORQUESTRADOR**.
Botão **NÃO DEVE** escolher executor. SINTONIA SCRAP **NÃO DEVE** competir como segundo
cérebro. Executor **NÃO DEVE** reconstruir sozinho a intenção original.

**REGRA IRMÃ.** Toda responsabilidade tem um dono só. `ferramentas/apify_pool.py` é o dono
único de «quando trocar de chave»; reimplementar isso noutro sítio criaria duas verdades
sobre rotação, e a segunda divergiria na primeira pressa.

**POR QUÊ.** O censo mediu **0 peças que coordenam mais de um executor**. O máximo que uma
peça coordenava eram 2, e as duas eram do Instagram.

**COMO PROVAR.** `py pedido/orquestrador.py "colete materiais de pesquisadores" --so-plano`

**ORIGEM.** `EXISTING_SINTONIA_LAW` · **LAW_STATUS** `CANONICAL` · **IT** `PARTIAL`
*(o orquestrador existe e assina; as fontes italianas ainda não passam por ele)*

---

## COL-LAW-012 · O ORQUESTRADOR CONTROLA, NÃO TRANSPORTA DADO

**REGRA.** Dois planos, explícitos e separados.

```
CONTROL PLANE   ENTRADA → PEDIDO → ORQUESTRADOR → EXECUTOR
DATA PLANE      SOURCE → EXECUTOR → RAW → DERIVAÇÕES → ADMISSÃO → READY
```

O orquestrador **NÃO DEVE** precisar de abrir diretórios e adivinhar qual JSON representa a
coleta. Cada executor **DEVE** declarar onde larga o que traz (`larga_em`).

**POR QUÊ.** A pergunta «o que o YouTube colhe vai para onde?» não tinha resposta: ia para
uma pasta que ninguém lia. A porta de admissão estava construída e **ninguém entregava
nela** — só o teste.

> **UMA PORTA POR ONDE NINGUÉM PASSA NÃO É UMA PORTA. É UMA PAREDE COM MAÇANETA.**

**REGRA DO SÍTIO QUE NÃO EXISTE.** Quando o sítio declarado não existe, isso **NÃO DEVE**
ser escondido: é o fato mais útil que a corrida produziu, e sai escrito no recibo
(`COLHEITA_NAO_ENCONTRADA`).

**COMO PROVAR.** `pedido/orquestrador.py::a_colheita` · `pedido/receitas.py` campo `larga_em`

**ORIGEM.** `EXISTING_SINTONIA_LAW` · **LAW_STATUS** `CANONICAL` · **IT** `PARTIAL`

---

## COL-LAW-013 · TODO EXECUTOR TEM UM CONTRATO COMUM

**REGRA.** Independentemente do que colete, todo executor **DEVE** poder declarar:

```
CAPABILITIES   o que sei fazer
CHECK          consigo chegar lá agora? (sem gastar)
COLLECT        vai buscar
STATE          onde parei
OUTPUT         onde larguei, e em que forma
TRACE          o que aconteceu, com hora e custo
```

Protocolo externo **NÃO DEVE** ser copiado literalmente. Esta é a versão SINTONIA.

**CONTRATOS QUE NENHUMA CORRIDA DISPENSA** — já declarados em `pedido/receitas.py`:

| contrato | onde vive |
|---|---|
| procedência | `regras/proveniencia.py` |
| tempo do fato | `leis/data_clock.py` |
| lugar do fato | `medidas/fato_local.py` · `medidas/lugar_do_fato.py` |
| recibo da corrida | `data/samples/RUN-MANIFEST.json` |

**ORIGEM.** `CONSOLIDATED_FROM_MULTIPLE` · **LAW_STATUS** `CANONICAL` · **IT** `PARTIAL`

---

## COL-LAW-014 · CAPACIDADES DECLARADAS

**REGRA.** O executor **DEVE** declarar, quando aplicável: `executor_id` · `version` ·
`source_types` · `channels` · `countries` · `artifact_types` · `modes` · `routes` ·
`cost_class` · `supports_checkpoint` · `supports_retry` · `produces`.
O orquestrador **DEVE** decidir a partir de capacidade declarada, e não de uma lista
infinita de `if` cravados no código quando houver alternativa melhor.

**ESTADO HONESTO.** Hoje `pedido/receitas.py` declara `id`, `roda`, `larga_em`, `rotas`,
`o_que_traz`, `custo`, `argumentos_de_filtros` — seis dos doze. O resto **ainda não existe**.

**ORIGEM.** `ARCHITECTURAL_DECISION` · **LAW_STATUS** `CANONICAL` · **IT** `PARTIAL`

---

## COL-LAW-015 · RECEITA É POLÍTICA, NÃO SEGUNDO CÉREBRO

**REGRA.** O plano **DEVE** ser derivado, não escrito:

```
PEDIDO + SOURCE REGISTRY + EXECUTOR REGISTRY + ROUTE POLICY + STATE + COST POLICY  →  PLANO
```

`receitas.py` **PODE** continuar existindo como módulo interno. **NÃO DEVE** ser tratada
como uma estação independente de topo.

**REGRA DO NÃO SEI HONESTO.** Se o pedido tocar 12 fontes e a casa souber percorrer 3, o
plano **DEVE** dizer «3 de 12» e **nomear as outras 9**. Devolver só as 3 e calar as 9 faz
uma coleta parcial parecer completa — o erro mais caro que este sistema pode cometer.

**MEDIDO.** 35 das 54 fontes italianas têm `access_method: NÃO SEI`.

**COMO PROVAR.** `py pedido/receitas.py "colete ciencia da Italia"` imprime
`fontes deste assunto`, `com caminho escrito`, `NAO SEI como se chega`.

**ORIGEM.** `EXISTING_SINTONIA_LAW` · **LAW_STATUS** `CANONICAL` · **IT** `IMPLEMENTED`

---

# PARTE V · INCREMENTAL, CHECKPOINT E RETRY

## COL-LAW-016 · ESTADO INCREMENTAL PERTENCE AO EXECUTOR

**REGRA.** O orquestrador conhece três escopos: `PONTUAL` · `INCREMENTAL` · `TOTAL`.
O executor conhece o **seu** checkpoint: cursor, último post, último vídeo,
`Last-Modified`, page token, ETag.
O orquestrador **NÃO DEVE** conhecer a semântica interna do cursor de cada fonte.

**ORIGEM.** `EXISTING_SINTONIA_LAW` · **LAW_STATUS** `CANONICAL` · **IT** `PARTIAL`

---

## COL-LAW-017 · CHECKPOINT, E A TRAVA DO GASTO

**REGRA.** Coleta longa **DEVE** poder retomar. `state_before` → `checkpoint` →
`state_after`.
Execução que cai após progresso comprovado **NÃO DEVE** reiniciar do zero.

**AS DUAS RECUSAS, já em código:**

```
SEM_CHECKPOINT_NAO_GASTEI          não há linha aberta  →  não chama o ator
JA_CONCLUIDO_NAO_PAGAR_DUAS_VEZES  já concluiu          →  não chama de novo
```

**A ORDEM QUE IMPORTA.** Persistir **antes** de dar a unidade por feita. Morrer entre as
duas coisas faz a unidade ser tentada de novo — o que é certo. A ordem inversa perde o que
já foi pago.

> `PROCESS_CRASH ≠ LOST_COLLECTION`

**COMO PROVAR.** `coleta/coleta_checkpoint.py` · `tests/test_coleta_resiliente.py`

**ORIGEM.** `EXISTING_SINTONIA_LAW` · **LAW_STATUS** `CANONICAL` · **IT** `IMPLEMENTED` *(a infraestrutura; ver COL-LAW-019 para o uso)*

---

## COL-LAW-025 · RETRY TEM CRITÉRIO

**REGRA.** `TRANSIENT ERROR` → retry controlado. `PERMANENT ERROR` → não repetir
inutilmente. Respeitar, quando a fonte oferecer: `Retry-After` · backoff · jitter ·
orçamento de retry.
**NÃO DEVE** ser construída plataforma pesada por causa disto.

**ORIGEM.** `ENGINEERING_PRINCIPLE` · **LAW_STATUS** `CANONICAL` · **IT** `ABSENT`

---

## COL-LAW-026 · CIRCUIT BREAKER — PROTEÇÃO DA FONTE

**REGRA.** Fonte ou rota que falha repetidamente **NÃO DEVE** ser martelada indefinidamente.
Estados: `HEALTHY` · `DEGRADED` · `BLOCKED` · `UNKNOWN`.
Implementação completa **NÃO** é exigida por esta Bíblia. A lei é.

**ORIGEM.** `ENGINEERING_PRINCIPLE` · **LAW_STATUS** `CANONICAL` · **IT** `ABSENT`

---

## COL-LAW-027 · QUARENTENA E REPLAY

**REGRA.** Erro definitivo **NÃO DEVE** significar «sumiu». **DEVE** ser possível preservar
`request/artifact` · `run_id` · `attempts` · `last_error` · `replayable`.
Usar a estrutura existente. **NÃO DEVE** ser criada fila complexa sem necessidade
comprovada.

**JÁ EXISTE, e é o embrião disto:** `py pedido/orquestrador.py --so-a-porta` leva a colheita
que **já existe** à peneira sem colher de novo. É o que permite reprocessar quando a regra
muda — sem isso, mudar a regra obrigaria a coletar tudo outra vez, ninguém o faria, e a
regra nova valeria só para o que viesse depois.

**ORIGEM.** `CONSOLIDATED_FROM_MULTIPLE` · **LAW_STATUS** `CANONICAL` · **IT** `PARTIAL`

---

# PARTE VI · CUSTO, ROTAS E FALLBACK

## COL-LAW-018 · A ROTA MAIS BARATA CAPAZ VEM PRIMEIRO

**REGRA.** Não há ordem global cega. A regra é:

> **USAR A ROTA DE MENOR CUSTO QUE CONSIGA CUMPRIR O CONTRATO DA FONTE.**

A `ROUTE POLICY` **PODE** variar por fonte, canal e capacidade.

**O PORTÃO GRÁTIS VEM ANTES DO GASTO.** Ler o `inputSchema` de um ator é um `GET`, custa
zero e não abre execução. Ele **DEVE** rodar antes de toda fase paga.

> `WRONG_INPUT_CONTRACT ≠ WRONG_PLATFORM` · `CONTRACT_MATCH ≠ USEFUL_DATA`

**POR QUÊ.** Oito execuções pagas desta casa foram queimadas mandando `searchQuery` a um
ator que não lê esse campo. A Apify **não recusa** campo estranho: ignora em silêncio e
devolve `SUCCEEDED` com um perfil qualquer — oito vezes o mesmo consultor de cibersegurança.

**COMO PROVAR.** `py ferramentas/contrato_ator.py apify~instagram-scraper`

**ORIGEM.** `CONSOLIDATED_FROM_MULTIPLE` · **LAW_STATUS** `CANONICAL` · **IT** `PARTIAL`

---

## COL-LAW-019 · APIFY É ROTA PAGA DE ESCALADA

**REGRA.** Na Itália, Apify **NÃO DEVE** ser o motor principal por omissão.
Quando usado, a corrida **DEVE** poder explicar:

```
WHY_PAID_ROUTE          por que foi preciso pagar
CHEAPER_ROUTE_ATTEMPTED que rota grátis se tentou
CHEAPER_ROUTE_RESULT    e o que ela devolveu
ESCALATION_REASON       o que na resposta dela obrigou a escalar
COST_USD                quanto custou
```

**AS TRÊS PALAVRAS DO CUSTO, e elas não se misturam:**

| valor | significa |
|---|---|
| `0` | **medido**: não gastou |
| `NÃO SEI` | **não medido** |
| `NOT_PRESERVED` | **confissão**: gastou e não guardou |

**A TRAVA QUE SOBREVIVE A UM BUG MEU.** `teto_usd → &maxTotalChargeUsd=` é do lado da
plataforma: funciona mesmo se o nosso código ler o custo errado.

**ORÇAMENTO POR CHAVE.** Cada chave descartável é um orçamento independente
(≈ US$ 5). Saldo de uma **NÃO DEVE** ser presumido para a seguinte. `KEY_STATUS ∈ ACTIVE ·
EXHAUSTED · ABANDONED`. O valor do token **NUNCA** entra em relatório, commit, fixture ou
manifesto.

**O ÚNICO LIMITE.** O gasto tem de servir à missão. **Não gastar só para esgotar a chave.**
O objetivo é máximo de inteligência útil por crédito — nunca máximo de registros por
crédito.

**ESTADO HONESTO.** ⚠️ Os cinco campos de escalada **não existem hoje** em nenhum ficheiro
deste repositório. Esta é lei futura, e a Bíblia diz isso em vez de fingir.

**CONTRATOS.** `docs/regras/POLITICA-DE-CHAVES-DESCARTAVEIS.md` ·
`ferramentas/apify_contrato.py` · `coleta/coletor.py`
**ORIGEM.** `ARCHITECTURAL_DECISION` + `EXISTING_SINTONIA_LAW`
**LAW_STATUS** `CANONICAL` · **IT** `ABSENT`

---

## COL-LAW-020 · ROTA BEM-SUCEDIDA TEM MEMÓRIA

**REGRA.** A fonte **PODE** preservar `last_successful_route` · `last_success` ·
`last_failure` · `route_verified_at`. O sistema **NÃO DEVE** ser obrigado a redescobrir a
melhor rota do zero em toda corrida.

**ORIGEM.** `ENGINEERING_PRINCIPLE` · **LAW_STATUS** `CANONICAL` · **IT** `ABSENT`

---

## COL-LAW-021 · NÃO COLETAR DE NOVO SEM NECESSIDADE

**REGRA.** Quando a fonte suportar, **DEVEM** ser usados: `ETag` · `Last-Modified` ·
checksum · id nativo do item · URL canônica · cursor.

**DUAS COISAS DIFERENTES, e confundi-las custa dinheiro:**

```
DEDUP BEFORE FETCH   evita a chamada        →  economiza
DEDUP AFTER  FETCH   evita a linha repetida →  economiza contagem, não dinheiro
```

**A CHAVE.** `PLATFORM + EXTERNAL_ID`, ou chave natural declarada. **Texto semelhante NÃO É
CHAVE**: dois comentários idênticos podem ser dois comentários reais.

**AUSÊNCIA DE IDENTIDADE NÃO É IDENTIDADE PARTILHADA.** Três vídeos distintos sem `id`
viravam **um**, porque `EXTERNAL_ID = NÃO SEI` era usado como chave. A aritmética
`RAW 3 = ÚNICOS 1 + DUPLICATAS 2` **fechava**, e o portão dizia `PROVED` enquanto dois
vídeos reais eram contados como duplicata de um registro sem identidade.

**MEDIDO.** Dos 472 posts do corpus espanhol, **100 eram o mesmo `POST_ID`**. O número
publicado caiu de 54 para 26.

**COMO PROVAR.** `tests/test_portao.py` · `medidas/voz.py::pipeline_video`

**ORIGEM.** `EXISTING_SINTONIA_LAW` · **LAW_STATUS** `CANONICAL` · **IT** `PARTIAL`

---

# PARTE VII · A CORRIDA E A RECONCILIAÇÃO

## COL-LAW-022 · TODA CORRIDA TEM IDENTIDADE

**REGRA.** O contrato canônico da corrida é o **`RUN-MANIFEST`**, e ele resolve:

```
CONTENT → RUN_ID → RUN_MANIFEST → INPUT / ACTOR / DATASET / RAW
```

**DEVE** conter, no mínimo: `run_id` · `request_id` · `source_id` · `executor_id` ·
`executor_version` · `pipeline_version` · `started_at` · `finished_at` · `status` ·
`state_before` · `state_after` · `cost` · `counts` · `errors`.

**E os cinco campos que a Itália provou serem melhores** sobem para o contrato canônico:
`EGRESS_IP` · `COLLECTOR_VERSION` · `GIT_HEAD` · `SOURCE_CONTRACT_VERSION` · `IS_BASELINE`.

**O TEMPO É MEDIDO, NUNCA INFERIDO.** `STARTED_AT` e `FINISHED_AT` vêm da plataforma.
`OUTPUT_WRITTEN_AT` — a hora em que o coletor **gravou** — é medida real e **NUNCA** é
promovida a `STARTED_AT`. Horário de commit do git **não mede ordem de coleta**: mede ordem
de escrita. Ordem entre corridas só é dizível por **instante com fuso**, nunca por
comparação de texto: `09:00+02:00` é **antes** de `08:00Z`, e a comparação de string
responde o contrário.

**`NOT_PRESERVED` É CONFISSÃO, NÃO AUSÊNCIA.** É diferente de `NÃO SEI` (a fonte não
informa) e muito diferente de a chave sumir.

**NUNCA GRAVAR TOKEN.** Há teste que varre o manifesto atrás de padrão de credencial.

**CONFLITO CONHECIDO.** Existem hoje **dois** registros de corrida (C-002 na matriz de
conflitos). O `RUN-MANIFEST` é o canônico; a fusão é o gap G-02.

**ORIGEM.** `CONSOLIDATED_FROM_MULTIPLE` · **LAW_STATUS** `CANONICAL` · **IT** `PARTIAL`

---

## COL-LAW-023 · RECONCILIAÇÃO ENTRE PORTAS

**REGRA.** Toda corrida **DEVE** poder medir, quando aplicável:

```
DISCOVERED → EMITTED → RAW_LANDED → DERIVED → ADMISSION_SEEN → READY
                                                    ↘ UNKNOWN   ↘ ERROR
```

Se `EMITTED ≠ RAW_LANDED`, houve **perda entre etapas**, e isso **NÃO DEVE** desaparecer
dentro de uma métrica geral de sucesso.

**O CHÃO QUE NÃO DESCE.** `medidas/padrao_da_coleta.py` mede 10 regras a cada corrida do CI.
Ele **não** exige que esteja tudo certo hoje — exige **não piorar**. Um coletor novo sem
carimbo de data faz o número subir e o portão reprova, nomeando o ficheiro.

> **«ESTÁ TUDO CERTO» NÃO É EXECUTÁVEL HOJE. «NÃO PIOROU» É.**

**PORTÃO É DERIVADO, NUNCA DIGITADO.** E um nome que faz dois trabalhos produz um `READY`
falso: `EAME_COLLECTION_ENTRY_GATE` dizia READY ao lado de `LOCATION_CONTRACT_COMPLETE = NO`
porque um nome cobria duas coisas diferentes.

**A LIÇÃO QUE ATRAVESSA OS SEIS PORTÕES REFUTADOS.** Cinco dos seis verificavam **FORMA** e
eram lidos como se verificassem **VERDADE**. Contagem que fecha, campo preenchido, valor
dentro do contrato e string presente são **todos satisfeitos por dado falso**.
Um portão só vale pela propriedade que ele **exerce**.

**COMO PROVAR.** `py medidas/padrao_da_coleta.py` · `py medidas/portao.py --json` ·
`tests/test_portao.py`

**ORIGEM.** `EXISTING_SINTONIA_LAW` · **LAW_STATUS** `CANONICAL` · **IT** `PARTIAL`

---

## COL-LAW-024 · ZERO INESPERADO NÃO É SUCESSO AUTOMÁTICO

**REGRA.** Fonte que normalmente produz itens e de repente produz zero **PODE** ter sofrido
`SOURCE_DRIFT` · `PARSER_DRIFT` · `BLOCK` · `AUTH_FAILURE`.
`SUCCESS + ZERO` só é aceitável quando o zero é **plausível pelo contrato daquela fonte**.

> **LISTA VAZIA É FALHA, NÃO ZERO.**

**MEDIDO, e é o caso que obriga a lei.** Um ator devolveu `SUCCEEDED`, `exitCode` limpo e
**zero itens**, com `statusMessage: "free user run limit reached"`. Cota esgotada que se
apresenta como sucesso. Hoje `SUCCEEDED` com zero itens vira **`PARTIAL`**, carregando a
mensagem da plataforma.

**E OUTRO.** Seis rotas devolveram `HTTP 200` com zero `<item>`.

**PRIMEIRA OBSERVAÇÃO É `BASELINE_ESTABLISHED`, NUNCA `NO_CHANGE`.** Não se declara ausência
de mudança contra um baseline que não existia.

**CUIDADO COM A EXPECTATIVA.** A faixa esperada por fonte **NÃO DEVE** virar verdade sobre o
mundo. `DECLARED_FREQUENCY ≠ OBSERVED_FREQUENCY`: **declaração não é medição**. Nas fontes
italianas, a frequência observada só foi provada por datas de documento em **quatro** de
treze; nas outras é `NÃO SEI`, mesmo quando o site declara uma cadência.

**COMO PROVAR.** `medidas/source_health.py` · `regras/italy_source_health.mjs --negativos`

**ORIGEM.** `EXISTING_SINTONIA_LAW` · **LAW_STATUS** `CANONICAL` · **IT** `IMPLEMENTED`

---

# PARTE VIII · INTEGRIDADE, SAÚDE E DRIFT

## COL-LAW-028 · A FONTE TEM SAÚDE

**REGRA.** Quatro estados, e nenhum é sinônimo de outro:

| estado | condição |
|---|---|
| `HEALTHY` | respondeu · o tipo bate · **todos** os campos do contrato presentes · a chave de identidade existe, é única e não é vazia · volume na faixa |
| `DEGRADED` | usável, mas o contrato mudou: campo novo, identidade duplicada, volume fora de ±10% |
| `FAILED` | não respondeu · respondeu outro tipo · **lista vazia** · campo do contrato ausente |
| `UNKNOWN` | não foi verificada nesta execução — **não é sinônimo de saudável** |

> **`HTTP 200` NÃO BASTA PARA `HEALTHY`.** Há 200 com página de erro: status bom, corpo
> lixo. A checagem é de **schema e identidade**, nunca de status.

**SAÚDE DO CORREDOR ≠ SAÚDE DA FONTE.**

| situação | `RUNNER_HEALTH` | `SOURCE_HEALTH` |
|---|---|---|
| VPN caiu | `FAILED` | `NOT_MEASURED` |
| push falhou | `DEGRADED_STORAGE` | pode seguir `HEALTHY` |
| site devolveu HTML no lugar de PDF | `HEALTHY` | `FAILED` |
| trava ocupada | `HEALTHY` | `NOT_MEASURED` |

> `VPN_FAILURE ≠ SOURCE_FAILURE`. Terre, ARPAV e SIAS **nunca** são marcadas como falhas
> porque a nossa VPN caiu.

**A fonte PODE preservar:** `last_attempt` · `last_success` · `last_failure` ·
`last_change` · `last_successful_route` · `health` · `expected_min/max` quando válido.
`UNKNOWN` permanece `UNKNOWN`.

**COMO PROVAR.** `py medidas/source_health.py` · `docs/operacao/CONTRATOS-DAS-FONTES-EAME.md`

**ORIGEM.** `EXISTING_SINTONIA_LAW` · **LAW_STATUS** `CANONICAL` · **IT** `IMPLEMENTED`

---

## COL-LAW-029 · SOURCE DRIFT — E A LEI DO CONTROLE NEGATIVO

**REGRA.** **DEVE** ser detectada mudança na *estrutura* da fonte, sem confundir isso com
mudança *do mundo*. Quando aplicável: `ETag` · checksum · hash do DOM · impressão digital do
schema · campos esperados · contagem esperada.
O hash **DEVE** mirar a parte relevante, não necessariamente a página inteira.

**AS CINCO PALAVRAS DA VERSÃO:**

```
BASELINE_ESTABLISHED    primeira versão — NUNCA «NO_CHANGE»
NO_NEW_VERSION          não publicou desde a última coleta
NEW_VERSION_IDENTICAL   publicou, e é byte a byte igual
NEW_VERSION_CHANGED     publicou e mudou  →  SÓ AQUI roda o detector de eventos
SOURCE_FAILED           não deu para saber  —  NÃO é «NO_NEW_VERSION»
```

**O erro que estes cinco estados existem para impedir:** uma fonte que caiu produzir a mesma
saída de uma fonte que não mudou, e o radar dizer «nada mudou» quando o que houve foi «não
consegui olhar».

**`SAME_URL ≠ SAME_DOCUMENT`** — hash novo é observação nova.
**`DOCUMENT_ID ≠ BYTE_ID`** — identidade semântica não é SHA-256.

> ### TESTE QUE NUNCA VIU VERMELHO NÃO É TESTE.
> `node regras/italy_source_health.mjs --negativos` corrompe o documento **em memória, nunca
> no disco**, e exige que a saúde caia para `FAILED`. Oito documentos foram corrompidos de
> propósito e os oito reprovaram. Um PDF que virou «Access denied» com `HTTP 200` reprovou.

**ORIGEM.** `EXISTING_SINTONIA_LAW` · **LAW_STATUS** `CANONICAL` · **IT** `IMPLEMENTED`

---

## COL-LAW-030 · MUDANÇA DO MUNDO ≠ MUDANÇA DO PIPELINE

**REGRA.** **DEVEM** ser preservados separadamente: `SOURCE_VERSION` · `COLLECTOR_VERSION` ·
`PIPELINE_VERSION`.
Uma correção de parser **NÃO DEVE** poder parecer, no futuro, um evento real do mercado.

**ORIGEM.** `ENGINEERING_PRINCIPLE` + `EXISTING_SINTONIA_LAW` · **LAW_STATUS** `CANONICAL` · **IT** `PARTIAL`

---

# PARTE IX · TEMPO, GEOGRAFIA E PROCEDÊNCIA

## COL-LAW-031 · LEI CANÔNICA DE TEMPORALIDADE

**REGRA.** Quatro tempos, e nenhum preenche o outro:

| campo | pergunta |
|---|---|
| `FACT_TIME` | quando o fato aconteceu |
| `PUBLISHED_AT` | quando foi publicado |
| `OBSERVED_AT` | quando a fonte o observou/registrou |
| `CAPTURED_AT` / `COLLECTED_AT` | quando o SINTONIA capturou |

> ## `FACT_TIME = PUBLISHED_AT` É PROIBIDO.
> Não por conveniência, não por omissão, não por *fallback*. Se não se sabe: **`UNKNOWN`**.

**PROSA NUNCA VIRA DATA.** `DATE_PARSE_STATE ∈ EXACT · MONTH_ONLY · RANGE · UNKNOWN`, e
`UNKNOWN` **nunca** entra em «próximos» nem em «passados».

**POR QUÊ, medido.** `FUTURE-EVENTS.json` declarava ser um subconjunto «com data a partir de
02/09/2026», e **21 dos 23 registros não tinham campo de data nenhum**. O filtro comparava
texto: `"NAO_SEI — pagina sem data de publicacao visivel"` começa por `N`, e

> **`'N' > '2'` EM ORDEM DE TEXTO, E ISSO NÃO É UMA DATA NO FUTURO.**

**PRECISÃO VIAJA COM A DATA.** Se a fonte prova o mês, não se inventa o dia.

**⚠️ VIOLAÇÃO VIVA, hoje, neste repositório.** `admissao/admissao.py:169` aceita
`published_at` como resposta à pergunta «tem tempo do fato», enquanto
`medidas/fato_local.py:411` declara que *«`published_at` NUNCA o preenche»*. Ver C-001. Gap
**G-01**.

**CONTRATOS.** `leis/v21_datas.py` · `leis/data_clock.py` · `medidas/fato_local.py::tempo_do_fato`
**ORIGEM.** `EXISTING_SINTONIA_LAW` · **LAW_STATUS** `CANONICAL` · **IT** `PARTIAL`

---

## COL-LAW-032 · LEI CANÔNICA DE GEOGRAFIA

**REGRA.** Quatro espécies de lugar, e **nenhuma promove a outra**:

```
BASE       onde a pessoa ou entidade está estabelecida
OPERATING  onde ela atua
INFLUENCE  onde está a audiência dela
FACT       onde o acontecimento relatado ocorreu

BASE ≠ OPERATING ≠ INFLUENCE ≠ FACT
SOURCE_LOCATION ≠ FACT_LOCATION
```

**MENÇÃO NÃO É FATO.** `PLACE_MENTION ≠ FACT_LOCATION`. Achar um topônimo no texto não
localiza nada. `FACT` exige relação semântica entre **acontecimento** e **lugar**, sustentada
por linguagem — *«constatata a»*, *«sintomi osservati in»*. Preposição e proximidade não
bastam: *«convegno a Bologna»* tem as duas e não diz nada sobre onde a doença está.

**COMO SE SOUBE É PARTE DO FATO:**

```
ESCRITO   o texto afirma o lugar do fato
CITADO    o nome aparece no meio — o balde mais fraco
DA_FONTE  veio do cadastro da fonte   ⛔ PROIBIDO sustentar fato
DEDUZIDO  a inteligência inferiu      ⛔ PROIBIDO sustentar fato
```

**PRECISÃO NÃO SOBE NEM DESCE SOZINHA.** Escada: `PAIS → REGIAO → PROVINCIA → MUNICIPIO →
LOCALIDADE → COORDENADA`. Se a fonte prova Toscana, não se inventa Grosseto; se prova
Grosseto, não se reduz para Itália. `PROVINCIAL ≠ REGIONAL`, e um cruzamento **NÃO DEVE**
alegar mais do que o seu apoio mais fraco.
Zona definida pela fonte fica **fora da escada** — não é «menos precisa que província», é
outra coisa.

**EXEMPLO.** Uma fonte em Milano relata evento em Bologna:
`SOURCE_LOCATION = Milano` · `FACT_LOCATION = Bologna`. As duas linhas convivem; nenhuma
vira a outra.

**A CICATRIZ QUE GOVERNA TODAS.** No Brasil, a região do **canal** carimbava a região de cada
documento. O padrão número 1 do portal publicou 44 pessoas «discutindo nematoide de café»
numa praça com 7.868 hectares de café — contra 1,1 milhão de hectares na região que o
sistema chamava de outra coisa. **E a lei já estava escrita no `CLAUDE.md` deles.**

> **LEI QUE NINGUÉM MEDE É COMENTÁRIO.**

**CONTRATOS.** `medidas/lugar_do_fato.py` (a lei, sem idioma) · `medidas/fato_local.py` (o
leitor italiano) · `leis/v21_geografia_contrato.py` (o contador que falha fechado) ·
migration 015 (as constraints)
**ORIGEM.** `EXISTING_SINTONIA_LAW` · **LAW_STATUS** `CANONICAL` · **IT** `IMPLEMENTED`

---

## COL-LAW-033 · LEI DE PROCEDÊNCIA

**REGRA.** Todo artefato **DEVE** poder provar, quando aplicável: `source_id` ·
`source_url`/`endpoint` · `publisher` · `run_id` · `collector`/`executor` ·
`collector_version` · `collected_at` · `sha256` · `parent_artifact_id` · linhagem.

> **A PROCEDÊNCIA SÓ VALE SE FOR POSTA NA COLETA. Depois é tarde:** o dado já entrou sem
> ela e ninguém recupera a origem.

> **TESTEMUNHO NÃO É PROVA.** Sem SHA-256, nada distingue o documento guardado de uma cópia
> trocada.

**O CARIMBO NÃO PODE PROMETER O QUE O REGISTRO NÃO TEM.** 2.217 registros mostravam na tela
«record acquisito da fonte pubblica identificata, **con URL e data**» tendo `SOURCE_URLS`
vazio e `REFERENCE_DATE` nulo.

**O ENDEREÇO DO EDITOR NUNCA ENTRA COMO ENDEREÇO DO ITEM.**
**QUEM FOI RELIGADO TEM DE DIZER POR ONDE** (`PROVENANCE_RECOVERED_VIA`).

**CONTRATOS.** `regras/proveniencia.py` · `leis/v21_procedencia_contrato.py` ·
`leis/v21_carimbar_origem.py` · `leis/v21_procedencia_religar.py`
**ORIGEM.** `EXISTING_SINTONIA_LAW` · **LAW_STATUS** `CANONICAL` · **IT** `IMPLEMENTED`

---

## COL-LAW-034 · LEI DE IDENTIDADE

**REGRA.** Cinco identidades, separadas: `SOURCE_ID` · `ITEM_ID` · `ARTIFACT_ID` ·
`RUN_ID` · `REQUEST_ID`.
`"?"` e a string vazia **NÃO DEVEM** ser usados como identidade. `UNKNOWN` fica explícito.

```
NAME ≠ HANDLE ≠ PROFILE ≠ PERSON ≠ ORGANIZATION
ORIGIN_ID ≠ CHANNEL_ID ≠ CONTENT_ID
```

**IDENTIDADE NUNCA POR SIMILARIDADE TEXTUAL.** Medido duas vezes:
`linkedin.com/company/adama/` devolve uma **incorporadora imobiliária romena**; e três
funcionários — FMC, UPL, BASF — foram contados como o canal da empresa porque o *headline*
deles nomeia o empregador. **O headline nomeia o empregador; não transforma o post em
comunicação da empresa.**
E no cruzamento ciência↔voz, o método frouxo casou «Universitat de Barcelona» com uma
unidade de pesquisa em tuberculose. Foi **medido e descartado**, não publicado.

**ORIGEM ≠ CONTEÚDO.** Uma pessoa com 50 vídeos é **1 origem e 50 conteúdos**. As duas
contagens nunca se somam nem se trocam.

**A IDENTIDADE DO CHECKPOINT NÃO PODE MUDAR ENTRE EXECUÇÕES.** `TOKEN`, `RUN_ID`,
`DATASET_ID` e `CAPTURED_AT` **NÃO DEVEM** entrar nela — retomar por outra chave duplicaria
a coleta inteira.

**SETE ENTIDADES NO REGULATÓRIO, nunca colapsadas:** `REGISTRATION_ID` ·
`REFERENCE_PRODUCT` · `REFERENCE_HOLDER` · `MANUFACTURER` · `MANUFACTURING_SITE` ·
`COMMON_DENOMINATION` · `CONCESSIONAIRE`. `BRAND` não é a oitava: é o **papel** de duas
delas.

**CONTRATOS.** `docs/regras/MODELO-DE-IDENTIDADE-EAME.md` · `regras/comunicacao_identidade.py` ·
`coleta/coleta_checkpoint.py::identidade_valida`
**ORIGEM.** `CONSOLIDATED_FROM_MULTIPLE` · **LAW_STATUS** `CANONICAL` · **IT** `PARTIAL`

---

# PARTE X · UNKNOWN, ERRO E RESULTADO

## COL-LAW-035 · A LEI DO UNKNOWN

**REGRA, absoluta:**

> # AUSÊNCIA DE EVIDÊNCIA ≠ EVIDÊNCIA DE AUSÊNCIA.

Não encontrou → `UNKNOWN`. Não conseguiu ler → `ERROR` ou `UNKNOWN`, conforme a causa.
**NÃO DEVEM** ser inferidos em silêncio: país · língua · tempo · lugar · identidade ·
autorização · relevância.

**«Não encontrámos nesta leitura»** — nunca **«não existe»**.

**REGISTRAR DESCONHECIDO É RESULTADO VÁLIDO E OBRIGATÓRIO.** Rebaixar de `COMPROVADO` para
`HIPÓTESE` é sempre permitido e nunca é retrocesso.

**AS TRÊS PALAVRAS QUE NÃO SÃO SINÔNIMOS:**

```
NÃO SEI         a fonte não informa
NOT_PRESERVED   existiu e não foi guardado — é confissão
NOT_APPLICABLE  a pergunta não faz sentido para este item
```

**⚠️ DECISÃO EM ABERTO.** O sentinela do desconhecido tem hoje **cinco grafias** neste
repositório (`NAO_SEI` 344 · `NOT_KNOWN` 123 · `UNKNOWN` 95 · `NÃO SEI` 57 · `NAO SEI` 35).
A Bíblia fixa o **significado** e declara a **grafia** como `DECISION_REQUIRED` (C-003).
Qualquer comparação nova que teste só uma das cinco aceita um desconhecido como conhecido,
**sem dar erro**.

**ORIGEM.** `EXISTING_SINTONIA_LAW` · **LAW_STATUS** `CANONICAL` · **IT** `IMPLEMENTED`

---

## COL-LAW-036 · A LEI DO NO_MATCH

**REGRA.** `NO_TERM_MATCH` sozinho **NÃO PROVA** `NO` nem `IRRELEVANT`.
Se a única evidência é a ausência de palavra-chave → **`UNKNOWN`**.
`NO` exige **evidência positiva de exclusão** prevista pela régua.

> `KEYWORD_MATCH ≠ RELEVANT_EVIDENCE` · `QUERY_MATCH ≠ PROVED_TOPIC`

**E O CONTRÁRIO TAMBÉM.** Contagem alta com régua limpa continua não distinguindo sentido:
*leiteiro* é gado, *cupim* é o meme, *murcha* é seca, *tiririca* é grama de jardim, *caruru*
é comida — e as cinco voltaram altas na segunda medição.

**RELEVÂNCIA NÃO É SCORE.** É derivada, com o motivo escrito:
`EXACT_SIGNAL` · `NEIGHBOURING_SIGNAL` · `CONTEXT_ONLY` · `RETROSPECTIVE` · `UNRELATED`.
Há teste que reprova se aparecer **coluna** chamada `score`.

**E O DENOMINADOR PRECISA APARECER.** «posts que casaram com as nossas consultas» **nunca** é
«tudo que a empresa publica».

**ORIGEM.** `EXISTING_SINTONIA_LAW` · **LAW_STATUS** `CANONICAL` · **IT** `PARTIAL`

---

## COL-LAW-037 · A LEI DO ERROR

**REGRA.** Erro operacional — timeout · `HTTP 500` · crash do navegador · crash do parser ·
falha da Apify · falha do runner · problema de credencial — **NÃO DEVE** virar `NO`,
`REJECTED` ou `NOT_RELEVANT`.

> **Rejeitado é «olhei e não serve». Erro é «não consegui olhar».** Tratar os dois como o
> mesmo faz uma falha de rede parecer um julgamento, e a fonte leva a culpa pela ferramenta.

**A TABELA DO `FAIL CLOSED` — cada linha custou uma medição:**

| não é | |
|---|---|
| falha de leitura | ≠ zero |
| falha de scraping | ≠ ausência de conteúdo |
| `403` | ≠ empresa silenciosa |
| nenhum resultado do Actor | ≠ nenhum resultado na plataforma |
| transcrição indisponível | ≠ vídeo sem conteúdo técnico |
| `HTTP 200` | ≠ fonte viva |
| `SUCCEEDED` da plataforma | ≠ execução bem-sucedida |
| **dataset vazio** | ≠ bruto perdido — o array vazio **É** a evidência, e vai para `PRESERVED` |
| certificado que não valida | ≠ motivo para desligar verificação — é **estado da fonte** |
| `ROUTE_NOT_FOUND` | ≠ `SOURCE_BLOCKED` — endereço errado nosso não é bloqueio da fonte |
| `ACCESS_CLASSIFICATION` | ≠ `ANALYTIC_VERDICT` — estado de porta não é veredito |
| `VPN_FAILURE` | ≠ `SOURCE_FAILURE` |

**SEPARAR O MUNDO, A INSTALAÇÃO E NÓS:**

```
RESPONDEU_COM_EVIDENCIA · RESPONDEU_SEM_O_CAMPO            ← o mundo
LOGIN_WALL · THROTTLED · NOT_FOUND · ACCESS_FAILURE        ← a instalação
PARSER_FAILURE · SEM_CHECKPOINT_NAO_GASTEI · NAO_TESTADO   ← nós
```

**A cicatriz, textual:** *«não li vestido de não há, desta vez PAGO: 299 fichas contadas
como "o perfil não declara lugar" quando ninguém chegou a perguntar»*.

**ORIGEM.** `EXISTING_SINTONIA_LAW` · **LAW_STATUS** `CANONICAL` · **IT** `IMPLEMENTED`

---

## COL-LAW-038 · RESULTADOS CANÔNICOS — DOIS EIXOS, NUNCA MISTURADOS

**REGRA.**

```
EIXO SEMÂNTICO (a decisão)     SIM · NAO · NAO_SEI · NAO_SE_APLICA · ERRO
EIXO OPERACIONAL (a corrida)   SUCCESS · PARTIAL · FAILED · RUNNING · NOT_PRESERVED
```

Um **NÃO DEVE** ser escrito no campo do outro.

**E RELEVÂNCIA NÃO É UM BOOLEANO UNIVERSAL.** O mesmo vídeo pode ser ouro para Ciência,
ruído para Concorrência e `NAO_SEI` para Regulatório. Guardar `relevante=true` no item
obriga a escolher um dono para a verdade, e o segundo universo que perguntar recebe a
resposta do primeiro. A decisão é sempre do **par (item, universo)**.

**COMO PROVAR.** `admissao/admissao.py::RESULTADOS` · `regras/proveniencia.py::STATUS_RUN`

**ORIGEM.** `EXISTING_SINTONIA_LAW` · **LAW_STATUS** `CANONICAL` · **IT** `IMPLEMENTED`

---

# PARTE XI · PAÍS, LÍNGUA E VOCABULÁRIO

## COL-LAW-039 · LEI DE PAÍS

**REGRA.** `COUNTRY_SCOPE` entra **cedo, no Pedido**. Fonte, rota e executor **DEVEM**
respeitar esse escopo.
A proteção **DEVE** existir no código e no contrato — **NÃO DEVE** depender de um botão
escondido para impedir vazamento.

**PAÍS É DIMENSÃO, NÃO PASTA ESQUECIDA.** O que vale para um país não vale automaticamente
para os outros. A camada europeia é o que **comprovadamente** vale para todos.
Peça que serve um país só mora em `<gaveta>/<país>/`; a gaveta continua dizendo a **etapa**.

**ORIGEM.** `EXISTING_SINTONIA_LAW` · **LAW_STATUS** `CANONICAL` · **IT** `PARTIAL`

---

## COL-LAW-040 · PAÍS NÃO É LÍNGUA

**REGRA.** `COUNTRY_SCOPE = IT` **NÃO IMPLICA** `ITEM_LANGUAGE = IT`.
Um item italiano **PODE** legitimamente estar em `IT`, `EN` ou outro idioma.
`LANGUAGE` é propriedade separada, e **UNKNOWN não vira IT por omissão**.

**ORIGEM.** `ARCHITECTURAL_DECISION` + `EXISTING_SINTONIA_LAW` · **LAW_STATUS** `CANONICAL` · **IT** `PARTIAL`

---

## COL-LAW-041 · VOCABULÁRIO É CONTEXTUAL

**REGRA.** Quatro responsabilidades, quatro vocabulários possíveis:
`SEARCH` · `EXTRACTION` · `CLASSIFICATION` · `ADMISSION`.
A mesma lista **NÃO DEVE** ser usada automaticamente nas quatro.
Vocabulário de país **NÃO DEVE** vazar em silêncio para fora do seu escopo.
Termos científicos, internacionais, marcas e nomes próprios **PODEM** ser partilhados.

**POR QUÊ.** Buscar *«septoria wheat»* na França devolve literatura internacional, não a
conversa técnica francesa. E `CROP` e `ISSUE` de cada item saem **desta consulta**, nunca de
leitura livre do título — é o que torna a linha auditável.

**CONTRATOS.** `regras/rotulos_censo.py` · `regras/sensor_coleta.py` · `regras/sensor_medir.py`
**ORIGEM.** `EXISTING_SINTONIA_LAW` · **LAW_STATUS** `CANONICAL` · **IT** `PARTIAL`

---

# PARTE XII · ADMISSÃO E READY

## COL-LAW-042 · A LEI DA ADMISSÃO

**REGRA.** A admissão **DEVE** produzir decisão auditável, com no mínimo:
`item/artifact id` · `universe` · `rule` · `rule_version` · `outcome` · `reason` ·
`evidence` · `decided_at`.
Uma decisão por **par (item, universo)**, nunca uma por item.
**TODAS** as decisões são guardadas — não só as que passaram.

**A ORDEM DAS PERGUNTAS É PARTE DA LEI.** As que apuram se **dá para olhar** vêm primeiro,
porque não se julga o que não se leu.

**`discarded=true` NÃO SERVE PARA NADA:** não diz por quê, nem por qual regra, nem com que
prova, nem se a regra mudou. Descarte sem testemunha é trabalho perdido duas vezes.

**A VERSÃO DA REGRA É O QUE PERMITE REPROCESSAR.** Com ela guardada, «reprocessa tudo o que
a versão 1 rejeitou» é uma operação; sem ela, é uma coleta inteira de novo.

**NÃO É ITEM ≠ ITEM VAZIO.** Uma ficha de conta ou de catálogo não é uma coisa colhida:
é o registro de **onde se pode coletar**. Responder-lhe `NAO_SEI` é dar uma resposta educada
a uma pergunta que não se devia ter feito — e por isso ninguém vai investigar. O resultado
certo é `NAO_SE_APLICA`.

**CONTRATOS.** `admissao/admissao.py` · `data/samples/LIVRO-DE-DECISOES.json`
**ORIGEM.** `EXISTING_SINTONIA_LAW` · **LAW_STATUS** `CANONICAL` · **IT** `PARTIAL`

---

## COL-LAW-043 · READY NÃO É «O SCRIPT TERMINOU»

**REGRA.** `READY_FOR_INTELIGENCIA` significa que os **contratos obrigatórios** da coleta e
da preparação foram satisfeitos. **NÃO DEVE** significar «o ficheiro existe» nem «o workflow
terminou».

O contrato de saída é fixo, e a inteligência recebe **isto e mais nada**:

```
ESTADO · ITEM_ID · UNIVERSO · TEXTO · SOURCE_ID
SOURCE_LOCATION · FACT_LOCATION · FACT_TIME · CAPTURED_AT
CORRIDA · ADMITIDO_POR
```

Ela não sabe — nem precisa de saber — qual raspador trouxe, qual API, qual veículo, nem que
remendo foi preciso. Se amanhã o executor for outro, **este contrato não muda**.

> **COLETA NÃO É INTELIGÊNCIA.** 10.000 vídeos coletados não são sucesso. O alvo é: **QUEM**
> disse **O QUÊ** sobre **QUE CULTURA** e **QUE PROBLEMA**, **ONDE**, **QUANDO**, **DE QUE
> PAPEL** e **COM QUE EVIDÊNCIA**.
> Corolário medido: 67 vozes técnicas verificadas, das quais **16** falam de olivar. O número
> acionável é o segundo. **Quantidade não é representatividade.**

**ORIGEM.** `EXISTING_SINTONIA_LAW` · **LAW_STATUS** `CANONICAL` · **IT** `PARTIAL`

---

## COL-LAW-044 · ARMAZENAMENTO NÃO É ESTADO LÓGICO

**REGRA.** Duas perguntas diferentes, dois campos:

```
ONDE ESTÁ   Supabase · git · data/raw · data/samples · object storage
EM QUE ESTADO   RAW · DERIVED · ADMITTED · READY · QUARANTINED
```

**A REGRA DO BRUTO, e a exceção que a rota paga cria:**

| caso | onde |
|---|---|
| rota **replicável** (a cadeia refaz) | `data/raw/` — cache, fora do git (**D-003**) |
| rota **não replicável** (chave descartável morre) | `data/samples/` — **versionado** |

A premissa de D-003 é que o bruto se refaz. Para chave descartável ela é **falsa**: ou a
evidência é versionada, ou perde-se.

**ORIGEM.** `CONSOLIDATED_FROM_MULTIPLE` (D-003 + REGRA §14) · **LAW_STATUS** `CANONICAL` · **IT** `IMPLEMENTED`

---

## COL-LAW-045 · COLETA MANUAL OU ASSISTIDA TAMBÉM TEM CONTRATO

**REGRA.** Coleta feita por pessoa, por Claude, por navegador assistido ou por outro agente
**NÃO DEVE** fingir que é automatizada — e **DEVE** entrar pelo mesmo contrato de evidência.
Preservar: `ACTOR_TYPE` · `ACTOR` · `METHOD` · `SOURCE` · `RUN/REQUEST` · `ARTIFACT` ·
`PROVENANCE`.

**ORIGEM.** `ARCHITECTURAL_DECISION` · **LAW_STATUS** `CANONICAL` · **IT** `PARTIAL`

---

# PARTE XIII · O SYSTEM MAP

> Esta parte **não repete** [`AGENTS.md`](AGENTS.md), que é o dono da lei do mapa. Ela
> declara só o que a coleta acrescenta.

## COL-LAW-046 · A LEI DO ESPELHO

**REGRA.** `SISTEMA REAL ⇄ SYSTEM MAP`. O mapa **NÃO É** documentação posterior: é a
representação verificável da arquitetura real.
Se o sistema mudou, o mapa muda. Se o mapa afirma uma relação, o sistema tem de prová-la.

**ORIGEM.** `EXISTING_SINTONIA_LAW` (`AGENTS.md`) · **LAW_STATUS** `CANONICAL` · **IT** `IMPLEMENTED`

---

## COL-LAW-047 · O MAPA NÃO É FONTE DE VERDADE PRIMÁRIA

**REGRA.** `state.generated.json` é **saída**. **NÃO DEVE** ser editado à mão.

```
CÓDIGO · CONTRATOS · REGISTRIES · MANIFESTS · MEDIÇÕES  →  GERADOR  →  SYSTEM MAP
```

E nunca `browser → desenha seta → vira verdade`.

**ORIGEM.** `EXISTING_SINTONIA_LAW` · **LAW_STATUS** `CANONICAL` · **IT** `IMPLEMENTED`

---

## COL-LAW-048 · TIPOS DE CONEXÃO

**REGRA.** A taxonomia consolidada — `DATA` · `CONTROL` · `READ` · `RULE` · `WRITE` ·
`PROOF` · `CODE` — **DEVE** ser preservada.
`IMPORT` **NÃO DEVE** virar fluxo de dados. `READ` **NÃO DEVE** virar `DATA`.
Seta **NÃO DEVE** ser inventada. Sem prova: `UNKNOWN`.

**E A SETA SEGUE O DADO.** A ação chama o YouTube (isso é controlo), mas o que atravessa a
linha é a colheita, e ela corre no sentido contrário:
`YOUTUBE → colher o YouTube → o ficheiro onde ela guarda`.

**ORIGEM.** `EXISTING_SINTONIA_LAW` · **LAW_STATUS** `CANONICAL` · **IT** `IMPLEMENTED`

---

## COL-LAW-049 · DECLARED / CODE / OBSERVED

**REGRA.** Três níveis de certeza sobre uma ligação:

| nível | quer dizer |
|---|---|
| `DECLARED` | o contrato diz que **pode** acontecer |
| `CODE` | há implementação que **permite** |
| `OBSERVED` | uma corrida real **provou** que aconteceu |

**Declaração não promove a verde.** Se o mapa disser que A alimenta B e o scanner não achar
linha que prove, a ligação fica `EXPECTED` e o estado cai para 🟡 com o motivo escrito.

Isto permitirá ao mapa, no futuro, mostrar `CAN DO ≠ DID DO`. Implementação total **não** é
exigida agora.

**ESTADO HONESTO.** `DECLARED` e `CODE` existem hoje (`architecture.declared.json` +
scanner). `OBSERVED` **não existe** — nenhuma aresta do mapa é hoje confirmada por uma
corrida real.

**ORIGEM.** `ARCHITECTURAL_DECISION` · **LAW_STATUS** `CANONICAL` · **IT** `PARTIAL`

---

## COL-LAW-050 · CURRENT ≠ TARGET

**REGRA.** A Bíblia **PODE** definir arquitetura futura. O mapa **NÃO DEVE** afirmar que ela
já existe. `CURRENT` e `TARGET/PROPOSED` são campos diferentes.

**E `futuro` NÃO É `legacy`.** Legado é o que morreu; futuro é o que está pronto e parado.
Marcar o piloto de Espanha como legado seria enterrá-lo vivo.

**ORIGEM.** `EXISTING_SINTONIA_LAW` · **LAW_STATUS** `CANONICAL` · **IT** `IMPLEMENTED`

---

# PARTE XIV · OS CONTRATOS MÍNIMOS

> **ANTES DE CRIAR UM SCHEMA NOVO: procurar o equivalente existente.** Se já existir,
> reutilizar e consolidar. **Não criar dez JSONs novos para parecer organizado.**

| contrato | dono canônico hoje | estado |
|---|---|---|
| `COLLECTION_REQUEST` | `pedido/pedido.py` | existe |
| `SOURCE` | `docs/fontes/ATLAS-DE-FONTES-EAME.md` + `candidatas/ITALY-SOURCE-MASTER-V1.json`, reconciliados em `system-map/data/sources.generated.json` | existe |
| `ENDPOINT` | `regras/italy_contracts.mjs` | existe (IT) |
| `EXECUTOR` | `pedido/receitas.py::EXECUTORES` | parcial (6 de 12 campos) |
| `RUN` | `data/samples/RUN-MANIFEST.json` | existe · **dois formatos** (C-002) |
| `STATE/CHECKPOINT` | `coleta/coleta_checkpoint.py` + tabela `checkpoint_coleta` | existe |
| `COLLECTION_ARTIFACT` | `data/collection-ledger/italy/observations.ndjson` | existe (IT) |
| `DERIVED_ARTIFACT` | — | **ABSENT** |
| `DECISION` | `data/samples/LIVRO-DE-DECISOES.json` | existe |
| `ROUTE_POLICY` | — | **ABSENT** |

## COL-LAW-053 · A FONTE TEM UM CADASTRO ÚNICO, E ELE É RECONCILIADO

**REGRA.** Duas listas a responder «que fontes temos» são duas verdades, e a segunda
envelhece calada. **DEVE** haver uma leitura única, e ela **DEVE** ser derivada.
Hoje: `system-map/data/sources.generated.json`, e é dela que `pedido/receitas.py` lê.

**FONTE NASCE; NÃO APARECE PRONTA.** A escada tem quatro degraus, e pular um é afirmar que
se sabe o que a fonte entrega sem ter olhado:

```
1 CANDIDATA   candidatas/FONTES-CANDIDATAS.json
2 REGISTADA   docs/fontes/ATLAS-DE-FONTES-EAME.md    (com exemplo real guardado)
3 CONTRATADA  docs/operacao/CONTRATOS-DAS-FONTES-EAME.md
4 AUTOMÁTICA  .github/workflows/
```

**O ACERVO É CAPITAL PARADO.** Consulta-se **antes** de coletar. Não se coleta para
descobrir o que já se sabe.

**ORIGEM.** `EXISTING_SINTONIA_LAW` · **LAW_STATUS** `CANONICAL` · **IT** `IMPLEMENTED`

---

# PARTE XV · GOVERNANÇA

## COL-LAW-069 · NENHUMA LEI MUDA EM SILÊNCIO

**REGRA.** Alterar uma lei desta Bíblia **DEVE** registrar:

```
LAW_ID · BEFORE · AFTER · WHY · EVIDENCE · IMPACT · VERSION
```

no `docs/decisoes/DIARIO-DE-DECISOES.md`, e subir a `VERSION` da Bíblia.
**Código pode mudar muitas vezes. Lei muda conscientemente.**

**E RECARIMBAR SEM RELER É O ÚNICO JEITO DE MENTIR NESTE SISTEMA.** Não fazer isso.

**COMO PROVAR.** `py provas/valida_biblia.py`

**ORIGEM.** `ARCHITECTURAL_DECISION` · **LAW_STATUS** `CANONICAL` · **IT** `IMPLEMENTED`

---

# A ARQUITETURA CANÔNICA

```
════════════════════ CONTROL PLANE ════════════════════

        ENTRADA (pessoa · relógio · [evento: NÃO EXISTE])
                        │
                 COLLECTION REQUEST      ← o QUÊ, nunca o COMO
                        │
                  ORQUESTRADOR           ← dono único do COMO
             ┌──────────┼──────────┐
      SOURCE REGISTRY   │   EXECUTOR REGISTRY
        ROUTE POLICY    │       STATE
                   COST POLICY
                        │
                    EXECUTOR

═════════════════════ DATA PLANE ══════════════════════

   SOURCE ──► EXECUTOR ──► RAW / LANDING ──► DERIVAÇÕES
                                                 │
                                            ADMISSÃO
                                                 │
                                    CANONICAL / READY

════════════════════ PROOF PLANE ══════════════════════

   RUN · PROVENANCE · CHECKPOINT · COUNTS · COST · ERRORS
   HEALTH · SOURCE DRIFT · QUARANTINE · DECISION LEDGER
```

**O que a seta significa:** no Control Plane a seta é **controle** (quem manda em quem);
no Data Plane a seta é **dado** (o que atravessa a linha). Nunca se trocam — COL-LAW-048.

---

# OS PRINCÍPIOS QUE ATRAVESSAM TODAS AS LEIS

```
UM DONO POR RESPONSABILIDADE
MENOS CAMINHOS
CONTRATOS CLAROS
EVIDÊNCIA PRESERVADA
FALHA VISÍVEL
NADA SILENCIOSO
```

E a frase que resume por que esta Bíblia existe:

> ## LEI QUE NINGUÉM MEDE É COMENTÁRIO.

---

## APÊNDICES

| | |
|---|---|
| A | [`docs/biblia/CENSO-DAS-LEIS-DA-COLETA.md`](docs/biblia/CENSO-DAS-LEIS-DA-COLETA.md) — 63 leis maduras catalogadas |
| B | [`docs/biblia/MATRIZ-DE-CONFLITOS.md`](docs/biblia/MATRIZ-DE-CONFLITOS.md) — 8 conflitos, com ficheiro e linha |
| C | [`docs/biblia/CONFORMIDADE-ITALIA.md`](docs/biblia/CONFORMIDADE-ITALIA.md) — lei × implementação, e os 10 gaps |
| D | [`docs/biblia/leis.json`](docs/biblia/leis.json) — o registro legível por máquina |

**Validador:** `py provas/valida_biblia.py`
