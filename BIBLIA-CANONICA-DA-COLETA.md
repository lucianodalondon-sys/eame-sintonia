# BÍBLIA CANÔNICA DA COLETA — SINTONIA

```
BIBLE_ID          SINTONIA-COLLECTION-BIBLE
VERSION           V1.4
STATUS            CANONICAL
EFFECTIVE_FROM    2026-09-07
CURRENT_PROFILE   ITALY_PROFILE_V1
CANONICAL_OWNER   este ficheiro, na raiz do repositório eame-sintonia
HEAD_AO_CONGELAR  56fdb8c
```

## HISTÓRICO CONSTITUCIONAL

Nenhuma lei muda em silêncio — é a COL-LAW-069. Toda emenda entra aqui e no
[`docs/decisoes/DIARIO-DE-DECISOES.md`](docs/decisoes/DIARIO-DE-DECISOES.md).

| versão | data | o que mudou | leis |
|---|---|---|---|
| **V1** | 2026-09-07 | a constituição inicial, consolidando 63 leis maduras já existentes | 48 |
| **V1.1** | 2026-09-07 | **duas emendas**: a lei da observabilidade (PARTE XVI — o System Map é a placa de vídeo do SINTONIA, e tudo tem de ser renderizável) e as leis roubadas de sistemas maduros de coleta (PARTE XVII — artefato ≠ fato, watermark, run completa, reparo, três eixos de confiança) | **78** (+30) |
| **V1.2** | 2026-09-08 | **a infraestrutura entra na lei**: o papel canônico do GitHub e do Supabase (PARTE XVIII — infraestrutura não é autoridade semântica) e o Plano de Referência (PARTE XIX — dado de referência não é configuração, e tem história) | **100** (+22) |
| **V1.3** | 2026-09-08 | **a integração**: a Bíblia e a engenharia italiana passam a viver no mesmo HEAD, e a primeira estrada real (PDF → texto → porta) foi medida contra a lei. Quatro leis novas (PARTE XX) para os quatro pontos onde a lei não bastava; as outras três questões já estavam resolvidas | **104** (+4) |
| **V1.4** | 2026-09-09 | **o cartão ganha contrato**: a PARTE XXI escreve o que um componente **é** — dono, tipo, portas, autoridade, e o que ele **não pode decidir**. Ela não reorganiza cartão nenhum e não toca no universo que está a ser censado: governa a reorganização futura | **121** (+17) |

**Nenhuma lei foi apagada em nenhuma emenda.** Emendas absorvidas por leis existentes, em vez
de virarem lei nova, estão registradas em
[`docs/biblia/EMENDA-V1-1.md`](docs/biblia/EMENDA-V1-1.md) e
[`docs/biblia/EMENDA-V1-2.md`](docs/biblia/EMENDA-V1-2.md) e
[`docs/biblia/RECONCILIACAO-INTEGRACAO.md`](docs/biblia/RECONCILIACAO-INTEGRACAO.md) e
[`system-map/contracts/CARD-CONTRACT-V1.md`](system-map/contracts/CARD-CONTRACT-V1.md).

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

**CONTRATOS.** `admissao/admissao.py` · `orquestrador/orquestrador.py`
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

**COMO PROVAR.** `py orquestrador/orquestrador.py "colete materiais de pesquisadores" --so-plano`

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

**COMO PROVAR.** `orquestrador/orquestrador.py::a_colheita` · `pedido/receitas.py` campo `larga_em`

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
| lugar do fato | `leis/fato_local.py` · `leis/lugar_do_fato.py` |
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

**JÁ EXISTE, e é o embrião disto:** `py orquestrador/orquestrador.py --so-a-porta` leva a colheita
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

**HISTÓRICO.** Até 2026-09-09 esta lei nomeava a ferramenta apify_contrato.py, que foi
removida do repositório por estar morta: zero importadores, zero execuções, e a saída que
declarava nunca existiu no disco. O CONCEITO — **ler o contrato do ator de graça antes de
gastar** — continua canônico, e o dono vivo dele é `ferramentas/contrato_ator.py`, que a
esteira importa em runtime.

> **UMA LEI NÃO DEPENDE DE UM NOME DE FICHEIRO. DEPENDE DO QUE ELA EXIGE.**

**CONTRATOS.** `docs/regras/POLITICA-DE-CHAVES-DESCARTAVEIS.md` ·
`ferramentas/contrato_ator.py` · `coleta/coletor.py`
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
`leis/fato_local.py:411` declara que *«`published_at` NUNCA o preenche»*. Ver C-001. Gap
**G-01**.

**CONTRATOS.** `leis/v21_datas.py` · `leis/data_clock.py` · `leis/fato_local.py::tempo_do_fato`
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

**CONTRATOS.** `leis/lugar_do_fato.py` (a lei, sem idioma) · `leis/fato_local.py` (o
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
| `REFERENCE_SET` | — | **ABSENT** — definição em Git, registros na memória operacional (COL-LAW-406) |
| `STORAGE_LOCATION` | bucket `raw` (privado) + tabela `raw_asset` | existe (ES) · a Itália não usa (G-30) |

### O que a emenda V1.1 mudou nos contratos — e o que ela recusou criar

> **Princípio aplicado:** *não criar entidade nova se um campo ou uma relação resolve.*
> Das quatro entidades candidatas, **uma** entra como contrato próprio e **três** não.

| candidata | veredito | porquê |
|---|---|---|
| `CLAIM / FACT` | ✅ **contrato próprio** (`TARGET`) | é a única que resolve um problema que nenhum campo resolve: o artefato e o fato têm **tempos e lugares diferentes** e cardinalidade `1:N`. Um documento pode carregar cinco fatos. Não cabe em campo. |
| `REPAIR_RUN` | ❌ **é uma RUN** | um `PARENT_RUN_ID` + `REPAIR_REASON` na RUN resolvem. Uma segunda entidade daria dois formatos de corrida — o erro que a C-002 já custou. |
| `DISCOVERY_RESULT` | ❌ **é uma capacidade** | `DISCOVER` é capacidade do executor (COL-LAW-207) e o resultado dela cabe nos `COUNTS` da RUN (`DISCOVERED`). |
| `STATEMENT / ASSERTION` | ❌ **por enquanto, campos** | `ORIGINAL_VALUE` + `PROVENANCE` ao lado do valor normalizado resolvem o caso de hoje (COL-LAW-203). Vira entidade **se e quando** um valor canônico precisar de compor várias evidências concorrentes. |

**E dois contratos existentes foram revistos:**

| contrato | revisão |
|---|---|
| `SOURCE` | passa a distinguir **`SOURCE` · `ENDPOINT` · `ROUTE`** (COL-LAW-205). Uma fonte tem vários endpoints. `ETag`, checksum, *schema fingerprint*, estado de acesso e `last_successful_route` pertencem ao **endpoint**; país, publisher e health institucional pertencem à **fonte**. |
| `COLLECTION_ARTIFACT` | **`FACT_TIME` e `FACT_LOCATION` deixam de ser esperados por omissão** (COL-LAW-201). Eles só aparecem no artefato quando o artefato **é** o fato, ou quando o contrato os vincula explicitamente. Para fato extraído, o caminho é `ARTIFACT → CLAIM`. |
| `EXECUTOR` | ganha as capacidades **`DISCOVER` · `FETCH` · `DERIVE`** (COL-LAW-207). Um executor pode implementar apenas uma. |
| `RUN` | ganha `PLAN_VERSION` · `CONFIG_HASH` · `BIBLE_VERSION` · `ROUTE_POLICY_VERSION` · `VOCABULARY_VERSION` · `MODE` · `WINDOW_START` · `WINDOW_END/WATERMARK` · `PARENT_RUN_ID` · `FINAL_MANIFEST_STATE` (COL-LAW-209 · 210 · 211 · 212). |

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

# PARTE XVI · A PLACA DE VÍDEO DO SINTONIA

> **Emenda V1.1.** O System Map deixa de ser «o mapa da arquitetura» e passa a ser a
> **camada oficial de observabilidade visual** do SINTONIA.
>
> ```
> O SISTEMA REAL é a máquina.
> O SYSTEM MAP é a placa de vídeo que transforma o estado interno
> em algo que uma pessoa consegue enxergar.
>
> SISTEMA REAL → CAMADA DE OBSERVABILIDADE → SYSTEM MAP → HUMANO
> ```
>
> Esta parte **não repete** a PARTE XIII (COL-LAW-046 a 050), que continua valendo. Ela
> acrescenta o que faltava: **o contrato do que se consegue ver.**

## COL-LAW-101 · TUDO DEVE SER RENDERIZÁVEL

**REGRA.** Toda responsabilidade arquitetural relevante **DEVE** fornecer informação
suficiente para ser representada no System Map.

> **`TUDO É RENDERIZÁVEL` ≠ `TUDO APARECE AO MESMO TEMPO`.**
> A UI escolhe o nível de detalhe. A arquitetura escolhe o que existe para ser mostrado.

**POR QUÊ.** Se algo importante acontece dentro do SINTONIA e não conseguimos enxergá-lo,
**a engenharia está incompleta** — não é um problema de tela, é um problema de contrato.

**VIOLAÇÃO.** Uma peça que roda, gasta e produz dado, e sobre a qual o mapa só consegue
dizer «o ficheiro existe».

**ORIGEM.** `ARCHITECTURAL_DECISION` · **LAW_STATUS** `CANONICAL` · **IT** `PARTIAL`

---

## COL-LAW-102 · AS QUATRO VERDADES

**REGRA.** O System Map **DEVE** conseguir distinguir quatro dimensões, e **NÃO DEVE**
confundi-las:

| verdade | a pergunta que responde |
|---|---|
| `DECLARED` | o contrato diz que **pode** existir |
| `CODE` | há implementação real que **permite** |
| `OBSERVED` | uma execução real **provou** que aconteceu |
| `BIBLE` | a Bíblia **exige** que exista, ou que se comporte assim |

Esta lei **estende** COL-LAW-049, que definia as três primeiras. `BIBLE` é a quarta, e é o
que permite ao mapa mostrar **o que deveria ser**, e não só o que é.

**EXEMPLO.**

```
SINTONIA SCRAP · CAN USE APIFY
  DECLARED = YES     a ficha do executor declara a rota
  CODE     = YES     há implementação que chama a Apify
  OBSERVED = NO      a última corrida não a usou
  BIBLE    = COL-LAW-019 exige explicar por que se pagou
```

`CAN USE APIFY = YES` **NÃO** significa `LAST RUN USED APIFY = YES`.

**ORIGEM.** `ARCHITECTURAL_DECISION` · **LAW_STATUS** `CANONICAL` · **IT** `PARTIAL`

---

## COL-LAW-103 · ESTADO DERIVÁVEL NÃO SE ESCREVE À MÃO

**REGRA.** A camada de observabilidade **DEVE** derivar, e **NÃO DEVE** aceitar escritos à
mão:

| estado | é |
|---|---|
| `CURRENT` | o que existe agora |
| `TARGET` | o que a Bíblia exige |
| `HEALTH` | se está funcionando |
| `COMPLIANCE` | se cumpre a Bíblia |
| `GAP` | a diferença entre `TARGET` e `CURRENT` |

**POR QUÊ.** É a mesma lei que já governa `state.generated.json` e os portões
(`medidas/portao.py`): **portão derivado, nunca digitado**. Um `GAP` escrito à mão é uma
opinião com cara de medição.

**ORIGEM.** `EXISTING_SINTONIA_LAW` · **LAW_STATUS** `CANONICAL` · **IT** `PARTIAL`

---

## COL-LAW-104 · CONTRATO DE COMPONENTE RENDERIZÁVEL

**REGRA.** Um componente **DEVE** poder declarar, **quando aplicável**:

```
COMPONENT_ID · NAME · ROLE · OWNER · ZONE
INPUTS · OUTPUTS
READS · WRITES · CONTROLS · RULES
SOURCES · ROUTES · EXECUTORS · ARTIFACT_TYPES
APPLICABLE_LAWS · IMPLEMENTATION_STATUS
LAST_RUN · LAST_SUCCESS · LAST_ERROR
COUNTS · COST · HEALTH · ISSUES · EVIDENCE
```

Campo inaplicável **NÃO DEVE** ser preenchido com dado falso: usa-se `UNKNOWN` ou
`NOT_APPLICABLE`, e são coisas diferentes (COL-LAW-035).

**ORIGEM.** `ARCHITECTURAL_DECISION` · **LAW_STATUS** `CANONICAL` · **IT** `PARTIAL`

---

## COL-LAW-105 · CONTRATO DE CONEXÃO RENDERIZÁVEL

**REGRA.** Uma ligação **DEVE** poder declarar, quando aplicável:

```
EDGE_ID · FROM · TO
TYPE ∈ DATA · CONTROL · READ · RULE · WRITE · PROOF · CODE
DECLARED  ∈ YES/NO/UNKNOWN
CODE      ∈ YES/NO/UNKNOWN
OBSERVED  ∈ YES/NO/UNKNOWN
LAST_OBSERVED_RUN · ARTIFACT_TYPE
COUNT_IN · COUNT_OUT · LOST
STATUS · EVIDENCE
```

> **NÃO DEVE ser inventado `DATA` a partir de `CODE`.** Que uma peça importe outra prova
> `CODE`; não prova que dado atravessou a linha.

**E PROXIMIDADE NÃO CRIA RELAÇÃO.** Duas entradas e duas saídas **não** implicam que todas
as entradas alimentam todas as saídas. Toda aresta é explícita e comprovada — é a
COL-LAW-048, e ela vale aqui inteira.

**ORIGEM.** `CONSOLIDATED_FROM_MULTIPLE` · **LAW_STATUS** `CANONICAL` · **IT** `PARTIAL`

---

## COL-LAW-106 · CONTRATO DE CORRIDA RENDERIZÁVEL

**REGRA.** Uma corrida **DEVE** poder ser desenhada com:

```
RUN_ID · REQUEST_ID · SOURCE_ID · EXECUTOR_ID · ROUTE
STARTED_AT · FINISHED_AT · STATUS
STATE_BEFORE · STATE_AFTER
DISCOVERED · EMITTED · RAW_LANDED · DERIVED · ADMISSION_SEEN · READY
UNKNOWN · ERROR · LOST
COST · ARTIFACTS · ERRORS · TRACE
```

**Reutilizar o `RUN-MANIFEST` antes de criar estrutura nova** — é a COL-LAW-022.

**ORIGEM.** `CONSOLIDATED_FROM_MULTIPLE` · **FECHADO PARA UMA ESTRADA, EM 08/09/2026.**
Faltavam `STATE_BEFORE/AFTER` e `ROUTE`: passaram a existir e a ser renderizados, com o
pre-voo e as versoes de engenharia ao lado.

**E CORRIGIDO NO MESMO DIA.** A lei tinha sido dada por cumprida medindo **uma** estrada. As
6 corridas do coletor piloto nao aparecem no mapa — `PILOT_RUN` ocorre **zero** vezes no
estado gerado. Uma estrada renderizavel de duas nao e a lei cumprida.

**LAW_STATUS** `CANONICAL` · **IT** `PARTIAL`

---

## COL-LAW-107 · A PERDA TEM DE APARECER NA ARESTA

**REGRA.** Perda mensurável entre etapas **DEVE** poder aparecer no mapa, **na ligação onde
ocorreu**.

```
EMITTED = 27
RAW_LANDED = 21
        ↓
LOST = 6      e o mapa mostra em QUAL aresta
```

> **NADA DESAPARECE SILENCIOSAMENTE ENTRE ETAPAS.**

É a COL-LAW-023 (reconciliação) tornada **visível**. Uma perda que só existe numa tabela
que ninguém abre é, na prática, uma perda escondida.

**MEDIDO — e já vale para uma estrada.** Na estrada do PDF a seta diz, derivado da medição:
*«entraram 43 documentos, saíram 43 textos. PERDIDOS: 0. A conta é entre etapas comparáveis
(documentos × textos), nunca ocorrências menos conteúdos»*. Nas outras estradas a
reconciliação ainda não existe (G-03), e por isso a lei fica `PARTIAL` e não `IMPLEMENTED`.

**ORIGEM.** `ARCHITECTURAL_DECISION` · **LAW_STATUS** `CANONICAL` · **IT** `PARTIAL`

---

## COL-LAW-108 · QUATRO VISTAS, UMA VERDADE SÓ

**REGRA.** O mesmo estado **DEVE** poder ser lido em quatro vistas:

| vista | mostra |
|---|---|
| **ARQUITETURA** | como o SINTONIA está ligado |
| **AO VIVO / RUN** | o que aconteceu numa corrida real |
| **PROBLEMAS** | `ERROR` · `LOST` · `DEGRADED` · `MISSING` · `BYPASS` · `UNKNOWN` · `NON_COMPLIANCE` |
| **BÍBLIA** | `CURRENT` vs `TARGET` vs `COMPLIANCE` |

**NÃO DEVEM** ser criados quatro bancos, quatro geradores nem quatro mapas. **É uma verdade
com filtros diferentes.**

**NÃO DEVE** ser criado visual paralelo — `biblia-map.html`, `research-map.html`,
`collection-v2-map.html` e afins são proibidos. O visual oficial é um só.

**ORIGEM.** `ARCHITECTURAL_DECISION` · **LAW_STATUS** `CANONICAL` · **IT** `PARTIAL`

---

## COL-LAW-109 · NÍVEIS DE ZOOM, E O LAYOUT NÃO MANDA

**REGRA.** Três níveis:

```
ALTO          responsabilidades
INTERMEDIÁRIO fontes · executores · rotas · artefatos · estados
RAIO-X        ficheiros · funções · workflows · arestas técnicas · evidência · runs · commits · leis
```

> **LAYOUT NÃO GOVERNA ARQUITETURA.** Se uma relação existe e é feia de desenhar, a relação
> continua existindo. O desenho é que se ajusta.

**ORIGEM.** `ARCHITECTURAL_DECISION` · **LAW_STATUS** `CANONICAL` · **IT** `IMPLEMENTED`

---

## COL-LAW-110 · OBSERVABILIDADE POR NASCIMENTO

**REGRA.** Toda peça criada depois desta Bíblia **DEVE** nascer observável. A definição de
pronto passa a ser:

```
FUNCTIONAL + TESTED + PROVEN + OBSERVABLE
+ SYSTEM MAP PARITY PASS + BIBLE COMPLIANCE KNOWN
```

**Componente invisível ao mapa NÃO DEVE ser aceite.** Já há dente para isto: o validador
reprova código de arquitetura que nenhuma peça do mapa reivindica
(`P9_CODIGO_DECLARADO`).

**ORIGEM.** `ARCHITECTURAL_DECISION` · **LAW_STATUS** `CANONICAL` · **IT** `IMPLEMENTED`

---

## COL-LAW-111 · A CAMADA DE OBSERVABILIDADE NÃO É UMA SEGUNDA VERDADE

**REGRA.** A arquitetura da «placa de vídeo» é:

```
CÓDIGO · CONTRATOS · REGISTRIES · BÍBLIA · RUN MANIFESTS
DECISION LEDGER · ISSUES · MEASUREMENTS
                    ↓
      CAMADA DE OBSERVABILIDADE / NORMALIZAÇÃO
                    ↓
              SYSTEM MAP STATE
                    ↓
                  VISUAL
```

A camada **normaliza verdades que já existem**. Ela **NÃO DEVE** passar a ser dona de
nenhuma delas. `state.generated.json` continua **saída**, nunca fonte primária.

**E NÃO DEVE SER INSTALADA TELEMETRIA PESADA** só para cumprir esta lei: nem OpenLineage
server, nem Kafka, nem Grafana, nem Prometheus, nem Temporal. Primeiro reutilizar o que já
existe — `RUN-MANIFEST`, contratos, registries, o livro de decisões, os geradores do mapa e
as medições. **A Bíblia define o contrato; a implementação é incremental.**

**ORIGEM.** `ENGINEERING_PRINCIPLE` + `EXISTING_SINTONIA_LAW` · **LAW_STATUS** `CANONICAL` · **IT** `IMPLEMENTED`

---

## COL-LAW-112 · TODA AFIRMAÇÃO DO MAPA TEM EVIDÊNCIA NAVEGÁVEL

**REGRA.** Toda afirmação `CURRENT` importante **DEVE** carregar evidência que se possa
abrir: `FILE` · `LINE` · `SNIPPET` · `CONTRACT` · `RUN` · `ARTIFACT` · `MEASUREMENT`.

```
OBSERVED    tem de apontar para um RUN
COMPLIANCE  tem de apontar para LAW + EVIDENCE
```

**JÁ EXISTE metade disto:** `P5_ARESTA_PROVADA` e `P5_PROVA_APONTAVEL` exigem ficheiro e
linha que existam. O que falta é o lado do `RUN`.

**ORIGEM.** `EXISTING_SINTONIA_LAW` · **LAW_STATUS** `CANONICAL` · **IT** `PARTIAL`

---

# PARTE XVII · AS LEIS ROUBADAS

> **Emenda V1.1.** Vieram do estudo de sistemas maduros que enfrentam o mesmo problema:
> OpenSanctions · OCCRP Aleph · Memorious · FollowTheMoney · Nomenklatura · GDELT ·
> Media Cloud · OpenCTI · OpenAlex · OpenAIRE · Crossref · Common Crawl · Browsertrix ·
> Scrapy · Crawlee · OpenLineage.
>
> ## ROUBAMOS AS LEIS. NÃO TROUXEMOS AS PLATAFORMAS.
>
> Nenhuma delas foi instalada, e nenhuma será. O SINTONIA **não é um grande scraper**: é um
> sistema em que as fontes são conhecidas, os executores são substituíveis, o bruto é
> preservado, os derivados têm linhagem, as decisões são auditáveis e as falhas aparecem.

## COL-LAW-201 · ARTEFATO NÃO É FATO

**REGRA, e é a mais importante desta emenda:**

```
COLLECTION ARTIFACT  ≠  CLAIM  ≠  FACT
```

Um PDF, post, vídeo, artigo ou JSON é **EVIDÊNCIA**. Ele **NÃO É** automaticamente «o fato».

E daí decorre a quem cada campo pertence:

| campo | dono |
|---|---|
| `PUBLISHED_AT` | o **artefato/publicação** |
| `SOURCE_LOCATION` | a **fonte/artefato**, quando comprovado |
| `FACT_TIME` | o **fato/claim extraído**, quando aplicável |
| `FACT_LOCATION` | o **fato/claim extraído**, quando aplicável |

**EXEMPLO.** Uma notícia publicada em **Roma** no dia **07/09** relata uma geada em
**Bolonha** no dia **03/09**. São quatro valores verdadeiros ao mesmo tempo, e nenhum
substitui outro.

> **NÃO DEVE ser exigido que todo RAW tenha `FACT_TIME` ou `FACT_LOCATION`.** Um boletim
> não «acontece» em lugar nenhum: ele **relata**. `UNKNOWN` é válido, e muitas vezes é a
> única resposta honesta ao nível do artefato.

**O QUE ISTO CORRIGE NA V1.** A COL-LAW-031 e a COL-LAW-032 estavam certas e incompletas:
diziam que os campos são diferentes, e não diziam **de quem cada um é**. Sem isso, a
pressão prática era pendurar `FACT_TIME` no documento — e foi exatamente essa pressão que
produziu o defeito C-001.

**ORIGEM.** `ENGINEERING_PRINCIPLE` (FollowTheMoney · OpenSanctions) · **LAW_STATUS** `CANONICAL` · **IT** `PARTIAL`

---

## COL-LAW-202 · O MODELO ARTEFATO → CLAIM

**REGRA, conceitual.**

```
ARTIFACT  ──evidence_for──►  CLAIM / FACT
```

Um claim **DEVE** poder preservar, quando aplicável:

```
CLAIM_ID · PARENT_ARTIFACT_ID · EVIDENCE_SPAN / EVIDENCE_REFERENCE
SUBJECT · PREDICATE · OBJECT
FACT_TIME · FACT_LOCATION
CONFIDENCE (quando houver contrato) · PROVENANCE
```

> ⚠️ **Extração de claim é `TARGET`, nunca `CURRENT`.** Ela **não existe** hoje no SINTONIA,
> e o mapa **NÃO DEVE** desenhá-la como se existisse. Esta missão não a implementa.

**ORIGEM.** `ENGINEERING_PRINCIPLE` · **LAW_STATUS** `CANONICAL` · **IT** `ABSENT`

---

## COL-LAW-203 · A PROCEDÊNCIA CHEGA ATÉ O VALOR

**REGRA.** A procedência **NÃO DEVE** parar no documento. Quando um valor canônico nasce de
evidência, tem de ser possível responder: **qual fonte disse · qual artefato disse · qual
era o valor original · qual valor normalizado saiu · quando o SINTONIA viu · qual regra
produziu a normalização.**

```
CANONICAL     WHEAT
ORIGINAL      "frumento tenero"
SOURCE        registro oficial X · artefato Y · run Z
TRANSFORM     regra de normalização vN
```

> ## NORMALIZAÇÃO NÃO DESTRÓI O VALOR ORIGINAL.
> Vale para cultura, produto, organização, molécula, lugar, nome — **qualquer conceito**.

**POR QUÊ.** Quando a regra de normalização estiver errada — e uma delas estará — só é
possível reprocessar se o valor original ainda existir. Sem ele, o erro vira permanente e
invisível.

**A ESTRUTURA CONCEITUAL** (não obriga entidade nova hoje): `ENTITY` · `PROPERTY` · `VALUE`
· `ORIGINAL_VALUE` · `SOURCE` · `ARTIFACT` · `LANGUAGE` · `FIRST_SEEN` · `LAST_SEEN` ·
`PROVENANCE`. É o que permite um valor canônico ser **composto de várias evidências** sem
reescrever nenhuma delas.

**ORIGEM.** `ENGINEERING_PRINCIPLE` (Nomenklatura · FollowTheMoney) · **LAW_STATUS** `CANONICAL` · **IT** `PARTIAL`

---

## COL-LAW-204 · DEDUPE NÃO DESTRÓI A HISTÓRIA

**REGRA.**

```
SOURCE RECORD  ≠  CANONICAL ENTITY

CANONICAL ENTITY
   ├── SOURCE RECORD A
   └── SOURCE RECORD B
```

Se dois registros forem julgados a mesma entidade, um **NÃO DEVE** sobrescrever o outro. Os
registros de origem ficam; a **decisão de identidade** é uma camada separada.

**POR QUÊ.** Decisão de identidade é revista — e quando for, a evidência original tem de
continuar intacta para se poder decidir de novo. Um dedupe que apaga o perdedor torna o
erro irreversível.

**LIGA-SE A** COL-LAW-021 (a chave de dedupe) e COL-LAW-034 (identidade nunca por
similaridade textual). Aquelas dizem **como se decide**; esta diz **o que não se destrói ao
decidir**.

**ORIGEM.** `ENGINEERING_PRINCIPLE` (OpenSanctions) · **LAW_STATUS** `CANONICAL` · **IT** `PARTIAL`

---

## COL-LAW-205 · A FONTE É ESTÁVEL; O ENDPOINT É SUBSTITUÍVEL

**REGRA.**

```
SOURCE    a instituição / publisher / origem lógica    — estável
ENDPOINT  o meio técnico de acesso de hoje            — substituível
```

Uma fonte **PODE** ter vários endpoints: site, RSS, API, sitemap, YouTube, repositório.
Trocar um raspador de HTML por uma API oficial **NÃO CRIA** uma fonte nova — cria um
endpoint novo na mesma fonte, e isso **DEVE** aparecer no Source Registry.

**REGRA DE ARRUMAÇÃO.** Informação que pertence ao endpoint **NÃO DEVE** ser posta na fonte.
`ETag`, checksum, schema fingerprint, `last_successful_route` e estado de acesso são do
**endpoint**. Health institucional, país e publisher são da **fonte**.
**A ficha da fonte não é uma lixeira de campos.**

**ORIGEM.** `ENGINEERING_PRINCIPLE` (Memorious · Aleph) · **LAW_STATUS** `CANONICAL` · **IT** `PARTIAL`

---

## COL-LAW-206 · TRÊS IDENTIDADES, E A URL NÃO É UMA DELAS

**REGRA.**

```
SOURCE_NATIVE_ID       o id que a própria fonte dá
SINTONIA_STABLE_ID     o nosso, e ele não muda
CANONICAL_URL / SOURCE_URL   um endereço — que muda
```

URL ou *slug* mutável **NÃO DEVE** ser usado como identidade canônica quando houver
alternativa.
Se a fonte mudar o seu id, **DEVE** ser preservado o mapeamento/histórico —
**NÃO DEVE** ser reidentificado o acervo inteiro em silêncio.

**ORIGEM.** `ENGINEERING_PRINCIPLE` (Crossref · OpenAlex) · **LAW_STATUS** `CANONICAL` · **IT** `PARTIAL`

---

## COL-LAW-207 · DESCOBRIR ≠ BUSCAR ≠ DERIVAR

**REGRA.** Três capacidades distintas, e um executor **PODE** implementar só uma:

| capacidade | o que faz | custo típico |
|---|---|---|
| `DISCOVER` | descobre **quais itens existem** ou são novos | barato |
| `FETCH` | obtém o **conteúdo/evidência** | caro |
| `DERIVE` | produz texto, transcrição, metadata | médio |

**EXEMPLO.** Um leitor de RSS descobre 7 endereços · um buscador de HTTP traz as 7 páginas ·
um extrator de PDF gera o texto. Três peças, três capacidades.

**POR QUÊ.** É o que permite **descobrir barato antes de buscar caro** — a base prática da
COL-LAW-018 (a rota mais barata capaz vem primeiro) e da COL-LAW-021 (não coletar de novo
sem necessidade). Hoje a Itália baixa ~12,8 MB por corrida **para depois descobrir** que
nada mudou, porque descobrir e buscar são a mesma coisa no código.

**E ISTO NÃO CRIA TRÊS ORQUESTRADORES.** O dono continua sendo um só (COL-LAW-011): ele
decide qual capacidade precisa, qual executor a cumpre e por qual rota. O executor executa
a capacidade.

**ORIGEM.** `ENGINEERING_PRINCIPLE` (Memorious · Scrapy · Crawlee) · **LAW_STATUS** `CANONICAL` · **IT** `ABSENT`

---

## COL-LAW-208 · O SOURCE REGISTRY É A MEMÓRIA DA COLETA

**REGRA.**

```
ORQUESTRADOR    = CÉREBRO   (decide)
SOURCE REGISTRY = MEMÓRIA   (lembra)
```

A ficha **DEVE** poder representar, quando aplicável: `SOURCE_ID` · `NAME` · `PUBLISHER` ·
`COUNTRY_SCOPE` · `SOURCE_TYPE` · `ENDPOINTS` · `DISCOVERY_METHODS` · `FETCH_METHODS` ·
`PREFERRED_ROUTE` · `FALLBACK_ROUTES` · `UPDATE_FREQUENCY` · `CHANGE_RATE` ·
`LAST_ATTEMPT` · `LAST_SUCCESS` · `LAST_FAILURE` · `LAST_CHANGE` ·
`LAST_SUCCESSFUL_ROUTE` · `HEALTH` · `EXPECTED_MIN` · `EXPECTED_MAX` · `ETAG` ·
`LAST_MODIFIED` · `CHECKSUM` · `STATE/CHECKPOINT` · `DEPRECATED` · `PROVENANCE`.

`UNKNOWN` é permitido. **Não é exigido que tudo esteja implementado hoje.**

**ORIGEM.** `CONSOLIDATED_FROM_MULTIPLE` · **LAW_STATUS** `CANONICAL` · **IT** `PARTIAL`

---

## COL-LAW-209 · A CORRIDA É HISTÓRIA, E HISTÓRIA NÃO SE REESCREVE

**REGRA.** Uma corrida passada **NÃO DEVE** ser reescrita para parecer que sempre funcionou.
Correção posterior cria uma **corrida de reparo**:

```
REPAIR_RUN
  PARENT_RUN_ID · REPAIR_REASON · REPAIRED_SCOPE · RESULT

RUN A (PARTIAL) ──repaired_by──► RUN B (COMPLETE)
```

O mapa **DEVE** poder mostrar as duas, ligadas. **O erro histórico não se apaga.**

**POR QUÊ.** É a mesma lei que já produziu `NOT_PRESERVED` como *confissão* em vez de
ausência (COL-LAW-022). Uma corrida limpa demais no passado é uma corrida que alguém
limpou.

**ORIGEM.** `ENGINEERING_PRINCIPLE` (OpenLineage) · **LAW_STATUS** `CANONICAL` · **IT** `ABSENT`

---

## COL-LAW-210 · A CORRIDA SÓ FICA COMPLETE NO FIM

**REGRA.** Fechamento atômico, e nesta ordem:

```
ARTEFATOS PRIMEIRO → RECONCILIAÇÃO → MANIFEST COMPLETE POR ÚLTIMO
```

Estados: `RUNNING` · `PARTIAL` · `FAILED` · `COMPLETE`.
`COMPLETE` **somente** quando: a execução terminou · os outputs esperados foram registrados
· as contagens foram reconciliadas · os erros conhecidos foram registrados · o manifesto
final foi fechado.

> ## A EXISTÊNCIA DE FICHEIROS NUMA PASTA NÃO PROVA QUE A CORRIDA TERMINOU.

**E NINGUÉM CONSOME PARCIAL COMO COMPLETA.** Derivação, admissão e `READY` **NÃO DEVEM**
presumir «há ficheiros numa pasta» = «corrida completa». Têm de respeitar o fechamento
canônico.

**MEDIDO, e é o caso que obriga a lei.** Este repositório já leu o dataset de uma execução
**ainda em curso** e gravou o pedaço como `PRESERVED`: 21 manifestos carregam
`"ERROR": "status da plataforma: READY."` — status transitório lido como fim.

**ORIGEM.** `EXISTING_SINTONIA_LAW` + `ENGINEERING_PRINCIPLE` · **FECHADO EM 08/09/2026 (G-38), para esta estrada.** `RUN_STATE` nasce de seis condicoes
**medidas** — executor terminou · outputs aterrados · reconciliacao feita · erros
contabilizados · bruto intacto · estado antes e depois — e e escrito **por ultimo**. Se o
processo morrer antes, o ficheiro na pasta nunca chega a dizer `COMPLETE`.

**E CORRIGIDO NO MESMO DIA.** «Para esta estrada» estava escrito aqui e foi lido como se
fosse o perfil inteiro. Nao e: as 6 linhas do `runs.ndjson` do coletor piloto nao tem campo
de fecho nenhum, e quem as le continua a inferir o fim pela existencia de ficheiros —
exatamente o que esta lei proibe.

**LAW_STATUS** `CANONICAL` · **IT** `PARTIAL`

---

## COL-LAW-211 · A CONFIGURAÇÃO DA CORRIDA FICA CONGELADA

**REGRA.** A corrida **DEVE** preservar o que foi **realmente usado naquele momento**:

```
PLAN_VERSION · CONFIG_HASH · EXECUTOR_VERSION · PIPELINE_VERSION
BIBLE_VERSION · ROUTE_POLICY_VERSION · VOCABULARY_VERSION
```

**POR QUÊ.** Para conseguir responder, daqui a seis meses: **«por que esta corrida fez
isso?»** O código de hoje **NÃO DEVE** ser usado como reconstrução do passado — ele já mudou.

**LIGA-SE A** COL-LAW-030 (mudança do mundo ≠ mudança do pipeline). Aquela separa as
versões; esta manda **carimbá-las na corrida**.

**ORIGEM.** `ENGINEERING_PRINCIPLE` (OpenLineage) · **LAW_STATUS** `CANONICAL` · **IT** `PARTIAL`

---

## COL-LAW-212 · O INCREMENTAL FECHA A JANELA ANTES DE ENTRAR

**REGRA.** Uma corrida incremental **DEVE** poder congelar uma janela:

```
WINDOW_START  ·  WINDOW_END / WATERMARK
```

**NÃO DEVE** consultar «até agora» enquanto «agora» continua a andar.

**EXEMPLO.** A corrida começa às 22:00 e fixa `WATERMARK = 21:55`. Ela trabalha apenas do
checkpoint anterior até 21:55. A corrida seguinte pega dali.

**`WATERMARK` NÃO É `RUN_FINISHED_AT`.** São coisas diferentes: um é o limite do que se
decidiu olhar; o outro é quando se parou de trabalhar.

**SOBREPOSIÇÃO CONTROLADA É PERMITIDA.** Se a corrida A terminou em 21:55, a corrida B
**PODE** recomeçar em 21:50 — a deduplicação por id/hash resolve a repetição.

> **Melhor uma repetição auditável do que um item perdido em silêncio.**

Não é obrigatória globalmente: é estratégia **por fonte**.

**PAGINAÇÃO INSTÁVEL PRECISA DE PROTEÇÃO.** Quando a fonte muda enquanto é paginada,
**DEVE** ser detectado o que for detectável: contagem de páginas mudou · total mudou ·
página vazia inesperada · cursor inconsistente · item repetido · item pulado.
Respostas possíveis: retry · janela menor · ordenação estável · abortar como `PARTIAL` ·
reconciliar. **`COMPLETE` em silêncio, não.**

**ORIGEM.** `ENGINEERING_PRINCIPLE` (GDELT · Media Cloud · OpenAIRE) · **LAW_STATUS** `CANONICAL` · **IT** `ABSENT`

---

## COL-LAW-213 · INCREMENTAL NÃO É SÓ SOMAR

**REGRA.** O incremental **PODE** envolver `CREATE` · `UPDATE` · `DELETE` · `MERGE`.

> ## «NÃO APARECEU NESTA CORRIDA» NÃO PROVA `DELETE`.

Deleção exige evento explícito, ou reconciliação adequada, ou evidência canônica
equivalente. É a COL-LAW-035 aplicada ao incremental: **ausência de evidência não é
evidência de ausência** — e aqui a ausência é especialmente traiçoeira, porque uma consulta
mal formada produz exatamente o mesmo silêncio que um item removido.

**E `TOTAL` É REDE DE SEGURANÇA.** `PONTUAL` · `INCREMENTAL` · `TOTAL` continuam válidos, e
**incremental não é automaticamente superior**. Se para uma fonte a recarga completa é mais
simples, mais barata e mais segura, ela **PODE** ser a melhor estratégia. Uma passagem
`TOTAL` periódica reconcilia a cópia inteira.

**ORIGEM.** `ENGINEERING_PRINCIPLE` · **LAW_STATUS** `CANONICAL` · **IT** `ABSENT`

---

## COL-LAW-214 · ZERO TEM SEMÂNTICA

**REGRA.** `0 itens` **NÃO DEVE** ser um estado só. Classificar:

```
EXPECTED_ZERO     o contrato da fonte prevê este zero
UNEXPECTED_ZERO   ela costuma entregar, e hoje não entregou
UNKNOWN_ZERO      não há base para dizer se é normal
```

`UNEXPECTED_ZERO` **PODE** indicar `SOURCE_DRIFT` · `PARSER_DRIFT` · `BLOCK` ·
`AUTH_ERROR` · `QUERY_ERROR`.

**E A EXPECTATIVA NÃO É VERDADE SOBRE O MUNDO.** `expected_min`/`expected_max` servem para
detectar **anomalia técnica**. Não declaram que a fonte «deve ter» 100 fatos.
**NÃO DEVE** ser fabricado dado para satisfazer expectativa — é a fronteira que
COL-LAW-024 já traçava, e esta lei dá-lhe as três palavras que faltavam.

**ORIGEM.** `CONSOLIDATED_FROM_MULTIPLE` · **LAW_STATUS** `CANONICAL` · **IT** `PARTIAL`

---

## COL-LAW-215 · FAIL LOUD — O NOSSO BUG NÃO VIRA `UNKNOWN` DO MUNDO

**REGRA.** Distinguir:

| | |
|---|---|
| **WORLD UNKNOWN** | a fonte não informou o lugar → `UNKNOWN` |
| **SYSTEM CONTRACT BROKEN** | o nosso parser esperava `product_id` e o schema mudou → `SOURCE_SCHEMA_DRIFT` / `ERROR` |

> **Bug de implementação NÃO DEVE virar desconhecimento do mundo.** Um `UNKNOWN` educado
> sobre um defeito nosso é a forma mais barata de nunca o consertar — ninguém investiga uma
> resposta que parece legítima.

**E CONFIGURAÇÃO INVÁLIDA NÃO PODE SER IGNORADA.** Campo desconhecido, chave errada, enum
inválido ou capacidade inexistente **NÃO DEVEM** ser ignorados em silêncio enquanto se
continua a produzir dado incompleto. **Falha alta, ou `UNKNOWN` explícito** — conforme a
natureza.

**MEDIDO.** A Apify **não recusa** campo estranho: ignora e cobra. Oito execuções pagas
desta casa foram queimadas assim.

**ORIGEM.** `ENGINEERING_PRINCIPLE` + `EXISTING_SINTONIA_LAW` · **LAW_STATUS** `CANONICAL` · **IT** `PARTIAL`

---

## COL-LAW-216 · TRÊS EIXOS DE CONFIANÇA, E NENHUM PREENCHE O OUTRO

**REGRA.**

| eixo | a pergunta |
|---|---|
| `SOURCE_HEALTH` | **consigo coletar tecnicamente?** |
| `SOURCE_RELIABILITY` | **que autoridade e que histórico tem esta fonte?** |
| `CLAIM_CONFIDENCE` | **que confiança há neste fato específico?** |

Uma fonte **saudável** pode ser pouco confiável. Uma fonte **confiável** pode publicar um
claim errado. Uma fonte **bloqueada** continua institucionalmente confiável.

> **A COLETA NÃO APAGA RAW POR BAIXA CONFIANÇA.** Reliability e confidence **NÃO DEVEM**
> fazer o coletor destruir evidência. O bruto fica; a avaliação é de outra camada
> (COL-LAW-005).

**O QUE ISTO CORRIGE.** A COL-LAW-028 definia só o primeiro eixo, e o nome «saúde» convidava
a ser lido como «qualidade». São coisas diferentes.

**ORIGEM.** `ENGINEERING_PRINCIPLE` (OpenSanctions · OpenCTI) · **LAW_STATUS** `CANONICAL` · **IT** `PARTIAL`

---

## COL-LAW-217 · `FIRST_SEEN` E `LAST_SEEN` SÃO DO SINTONIA

**REGRA.** Dois tempos internos, e eles **NÃO SÃO** nenhum dos outros:

```
SINTONIA_FIRST_SEEN   a primeira vez que o sistema observou aquele valor/claim
SINTONIA_LAST_SEEN    a última vez que o observou
```

Não confundir **«apareceu agora»** com **«nós o coletamos agora»**.

**A MATRIZ COMPLETA DO TEMPO** fica assim, e cada um tem dono:

| tempo | dono |
|---|---|
| `FACT_TIME` | o fato/claim |
| `PUBLISHED_AT` | a publicação/artefato |
| `OBSERVED_AT` | a fonte |
| `COLLECTED_AT` | a coleta |
| `DERIVED_AT` | a derivação |
| `SINTONIA_FIRST_SEEN` / `SINTONIA_LAST_SEEN` | o SINTONIA |
| `RUN_STARTED_AT` / `RUN_FINISHED_AT` | a corrida |

**Não é exigido que toda entidade tenha todos.** É exigido que o dono de cada um seja claro.
Isto **estende** a COL-LAW-031, que tinha quatro.

**ORIGEM.** `ENGINEERING_PRINCIPLE` (OpenSanctions) · **LAW_STATUS** `CANONICAL` · **IT** `ABSENT`

---

## COL-LAW-218 · BULK NÃO É API PONTUAL

**REGRA.** A política **PODE** ser diferente por modo:

| modo | rota adequada |
|---|---|
| carga inicial completa | **snapshot / bulk**, quando existir |
| incremental | API · change feed · janela |
| pontual | consulta / API |

**NÃO DEVE** ser usada API de cursor para baixar centenas de milhões de registros quando
existe snapshot apropriado.

**E VERSÃO CIENTÍFICA NÃO É «DUPLICATA PARA APAGAR».** *Preprint*, versão publicada e versão
corrigida **PODEM** representar o mesmo trabalho canônico sem serem o mesmo artefato. A
coleta **preserva as instâncias**; a canonicalização decide a relação depois — e é a
COL-LAW-204 que garante que decidir não destrói.

> ⚠️ **Ciência não foi implementada nesta missão.** Só a lei foi consolidada.

**ORIGEM.** `ENGINEERING_PRINCIPLE` (OpenAlex · OpenAIRE · Crossref · Common Crawl) · **LAW_STATUS** `CANONICAL` · **IT** `NOT_APPLICABLE`

---

# PARTE XVIII · A INFRAESTRUTURA

> **Emenda V1.2.** O SINTONIA já tem casa: **GitHub** e **Supabase**. Esta parte não cria
> uma segunda — dá a cada uma um papel claro, e proíbe que uma faça o trabalho da outra.
>
> ```
> GITHUB      =  AUTORIDADE DE ENGENHARIA
> SUPABASE    =  MEMÓRIA OPERACIONAL E PERSISTÊNCIA ESTRUTURADA
> SYSTEM MAP  =  OBSERVABILIDADE VISUAL
> A BÍBLIA    =  A LEI QUE GOVERNA OS TRÊS
> ```
>
> Estas leis foram escritas **depois** de medir, e duas delas contrariam o que se esperava
> encontrar. O censo está em
> [`docs/biblia/CENSO-DA-INFRAESTRUTURA.md`](docs/biblia/CENSO-DA-INFRAESTRUTURA.md).

## COL-LAW-301 · INFRAESTRUTURA NÃO É AUTORIDADE SEMÂNTICA

**REGRA.**

```
INFRASTRUCTURE  ≠  SEMANTIC AUTHORITY
TABLE           ≠  CANONICAL TRUTH
```

Uma tabela existir **NÃO** torna o que está nela canônico. Um script conseguir fazer
`INSERT` **NÃO** lhe dá autoridade para decidir o que é verdade.

**POR QUÊ.** É a mesma lei que já governa o mapa — *«declaração não promove a verde»* — dita
para o banco. Quem decide o que é canônico são os **contratos, as leis, os donos, a
admissão, a canonicalização e a evidência**. Nunca «está numa tabela».

**ORIGEM.** `ARCHITECTURAL_DECISION` · **LAW_STATUS** `CANONICAL` · **IT** `IMPLEMENTED`

---

## COL-LAW-302 · O GITHUB GUARDA A ENGENHARIA

**REGRA.** O GitHub é o lugar canônico, quando aplicável, de:
**código · a Bíblia · contratos · schemas · testes · validadores · geradores · migrations ·
definições de CI/CD · workflows · configuração versionada · histórico de mudança ·
identidade de commit/release.**

Em uma frase, o GitHub responde:

> ## «QUAL ENGENHARIA ESTAVA VALENDO?»

**MEDIDO, e já é assim.** 1.151 ficheiros rastreados · 21 migrations versionadas · a ordem
da cadeia num dono só (`motor/cadeia_canonica.sh`) · o SQL de importação **gerado e
versionado antes de correr**, porque *«o SQL é AUDITÁVEL: ele entra no Git, alguém lê antes
de rodar»*.

**ORIGEM.** `EXISTING_SINTONIA_LAW` · **LAW_STATUS** `CANONICAL` · **IT** `IMPLEMENTED`

---

## COL-LAW-303 · O GITHUB NÃO É BANCO OPERACIONAL

**REGRA.** **PODEM** viver em Git, quando fizer sentido: fixtures · configurações canônicas
pequenas · contratos · amostras de teste · manifestos versionados · pequenos ativos de
referência · evidência de rota **não replicável** (COL-LAW-044).

**NÃO DEVEM** viver em Git só porque é simples escrever um JSON:

```
RUN STATE
estado operacional de alta rotatividade
datasets mutáveis grandes
atualizações frequentes de saúde
atualizações frequentes de referência
```

**POR QUÊ, e o número dói.** O Git **não esquece**. Um ficheiro apagado continua a pesar em
cada clone, para sempre. Escrever estado de corrida em Git é escolher carregar todas as
corridas de todos os dias, para sempre, em cada máquina que clonar.

**⚠️ VIOLAÇÃO VIVA, medida hoje.** `coleta/italy_recurrent_collect.mjs:144` faz
`git add data/collection-ledger data/collection-store`: o recibo, as 144 observações **e os
bytes** (11 ficheiros, **12 MB**) entram no Git — enquanto `collection_run`, `raw_asset` e o
bucket `raw` existem, estão provados, e ficam vazios. Ver ACHADO 3 do censo. Gap **G-30**.

**NADA FOI MIGRADO NESTA MISSÃO.** A lei fica escrita; a mudança é outra missão.

**ORIGEM.** `ENGINEERING_PRINCIPLE` · **LAW_STATUS** `CANONICAL` · **IT** `ABSENT`

---

## COL-LAW-304 · O SUPABASE É A MEMÓRIA OPERACIONAL

**REGRA.** O Supabase **PODE** ser a persistência estruturada, quando coerente com os
contratos canônicos, de: **Source Registry · Endpoint Registry · Reference Sets ·
Reference Records · metadata de corrida · metadata de artefato · linhagem ·
estado/checkpoints · saúde · issues operacionais · livro de decisões · dado canônico
estruturado · `FIRST_SEEN`/`LAST_SEEN` · janelas de validade · contagens · custo.**

Em uma frase, o Supabase responde:

> ## «O QUE ACONTECEU, E COMO ESTÁ AGORA?»

**ORIGEM.** `ARCHITECTURAL_DECISION` · **LAW_STATUS** `CANONICAL` · **IT** `PARTIAL`

---

## COL-LAW-305 · O SUPABASE GUARDA; NÃO JULGA

**REGRA.**

> ## SUPABASE STORES. SUPABASE DOES NOT JUDGE.

O banco **NÃO DEVE** ser tratado como o dono da verdade só por ser onde a linha ficou. A
verdade canônica é decidida por contrato, lei, dono, admissão, canonicalização, evidência e
decisão registrada.

**LIGA-SE A** COL-LAW-035 (o `UNKNOWN`) e COL-LAW-042 (a admissão): uma linha gravada sem
passar pela porta é uma linha sem decisão — e uma decisão que ninguém tomou não vira verdade
por ficar guardada.

**ORIGEM.** `ARCHITECTURAL_DECISION` · **LAW_STATUS** `CANONICAL` · **IT** `IMPLEMENTED`

---

## COL-LAW-306 · NINGUÉM ESCREVE NO CANÔNICO POR CONHECER A TABELA

**REGRA.** Um executor, importador ou coletor **NÃO DEVE** escrever no estado canônico só
porque conhece `SUPABASE_URL`, `SUPABASE_KEY` e o nome da tabela. Toda escrita canônica
atravessa o dono apropriado:

```
EXECUTOR → CONTRATO DE ARTEFATO → ADMISSÃO / DONO → CANONICAL STORE → SUPABASE

REFERENCE SUPPLY → VALIDAÇÃO → DONO DA REFERÊNCIA → REFERENCE STORE → SUPABASE
```

**MEDIDO — e a casa já cumpre, por um caminho que vale a pena preservar.** Os 7 caminhos de
escrita medidos são **todos canônicos** e **há zero bypasses**. O padrão é:

```
artefato → gerador → .sql VERSIONADO em supabase/importacoes/ → GitHub Actions → Supabase
```

E funciona porque **o segredo não existe fora do runner**. A engenharia acidental virou lei:
*«o que vai para o Git é reprodutível; o que foi digitado no banco, não»*.

**ORIGEM.** `EXISTING_SINTONIA_LAW` · **LAW_STATUS** `CANONICAL` · **IT** `IMPLEMENTED`

---

## COL-LAW-307 · A CORRIDA SE LIGA À ENGENHARIA QUE A PRODUZIU

**REGRA.** Toda corrida **DEVE** poder registrar, quando materialmente relevante:

```
RUN_ID · GIT_COMMIT · PIPELINE_VERSION · EXECUTOR_VERSION
CONFIG_HASH · PLAN_VERSION · BIBLE_VERSION
ROUTE_POLICY_VERSION · VOCABULARY_VERSION
```

para que se possa ler `DATA ↔ RUN ↔ ENGINEERING VERSION`.

> ## `GIT COMMIT` NÃO É `OBSERVED RUN`.
> Um commit prova **que código existia**. Não prova que **aquela corrida o usou**. `OBSERVED`
> exige corrida real **mais** o registro explícito da versão (COL-LAW-102 · 112).

**E O PASSADO NÃO MUDA QUANDO O GIT ANDA.** Se o repositório avança, a corrida antiga
continua ligada à versão antiga. **NÃO DEVE** ser reconstruída com o código de hoje —
é a COL-LAW-209 e a COL-LAW-211 aplicadas à infraestrutura.

**MEDIDO.** O ledger italiano guarda `GIT_HEAD`; o `RUN-MANIFEST` europeu **não guarda
nenhuma versão de engenharia**. Gap **G-02**.

**ORIGEM.** `CONSOLIDATED_FROM_MULTIPLE` · **LAW_STATUS** `CANONICAL` · **IT** `PARTIAL`

---

## COL-LAW-308 · MIGRATION VERSIONADA, E FICHEIRO NÃO É ESTADO APLICADO

**REGRA.** Toda mudança de schema **DEVE** ter histórico de engenharia — preferencialmente
uma migration versionada em Git.

E três coisas **NÃO DEVEM** ser confundidas:

| | |
|---|---|
| `DECLARED DATABASE SCHEMA` | o que a migration no Git diz |
| `CODE EXPECTATION` | o que o código espera encontrar |
| `ACTUAL DATABASE STATE` | o que o banco tem de verdade |

> **A migration existir no Git NÃO prova que ela foi aplicada.**

Quando as duas divergirem, isso é **`INFRASTRUCTURE_DRIFT`** — estado operacional. **NÃO É**
`WORLD UNKNOWN`: não é o mundo que não sabemos, é a nossa casa que está diferente do
desenho. Confundir os dois é a COL-LAW-215 outra vez.

**MEDIDO, e já é bom.** 21 migrations versionadas · a `008` é a **última** e confere o que as
outras escreveram · `supabase-migrate.yml` tem pré-voo que **recusa escrever num banco que
não está como esperado** e para no primeiro erro, *«sem improvisar conserto no banco»*.

**ORIGEM.** `EXISTING_SINTONIA_LAW` · **LAW_STATUS** `CANONICAL` · **IT** `IMPLEMENTED`

---

## COL-LAW-309 · O GITHUB ACTIONS É EXECUÇÃO, NÃO ORQUESTRADOR

**REGRA.** O GitHub Actions **PODE**: agendar · disparar · testar · validar · executar ·
publicar · fazer deploy · regerar · barrar.

**NÃO DEVE** decidir: que fonte é relevante · que executor usar semanticamente · qual
fallback lógico seguir · o que é admissível · qual verdade vence · qual item é relevante ·
qual entidade é canônica.

> ## YAML NÃO É UM SEGUNDO ORQUESTRADOR.

Um workflow **PODE** acionar um `COLLECTION REQUEST`, e daí em diante quem manda é o
**ORQUESTRADOR** (COL-LAW-011). O botão não escolhe o executor.

**MEDIDO.** 11 workflows, e nenhum decide relevância ou rota. O risco é real mas ainda não
se concretizou.

**ORIGEM.** `ARCHITECTURAL_DECISION` · **LAW_STATUS** `CANONICAL` · **IT** `IMPLEMENTED`

---

## COL-LAW-310 · AGENDA NÃO É POLÍTICA DE COLETA

**REGRA.**

```
SCHEDULE  ≠  COLLECTION POLICY
```

Um relógio pode dizer **«rode às 08:00»**. **NÃO DEVE** significar automaticamente
**«colete tudo»**. O modo (`PONTUAL` · `INCREMENTAL` · `TOTAL`), a política de atualização e
o `DUE / NOT DUE` pertencem ao **pedido e à fonte** — nunca ao gatilho.

**MEDIDO, e a Itália já faz isto certo por necessidade.** O gatilho do Windows dispara **de
hora em hora**, e quem decide se é a hora é o coletor, comparando com `Europe/Rome` — *«o
fuso mora no código, não no agendador»*. O relógio pergunta; a política responde.

**E o único relógio do SINTONIA não está no GitHub.** Zero `cron` nos 11 workflows: o
agendamento real é o Agendador de Tarefas do Windows, porque **o runner do GitHub sai por
datacenter e a coleta italiana precisa sair pela VPN italiana**. Não é preguiça: é a
medição.

**ORIGEM.** `CONSOLIDATED_FROM_MULTIPLE` · **LAW_STATUS** `CANONICAL` · **IT** `IMPLEMENTED`

---

## COL-LAW-311 · BYTES NÃO SÃO METADATA

**REGRA.**

```
ARTEFATO BINÁRIO / RAW GRANDE   ≠   METADATA DO ARTEFATO
```

PDF, vídeo, captura de HTML, WARC e imagem **PODEM** viver numa camada de armazenamento de
objetos. A metadata estruturada — `ARTIFACT_ID` · `CONTENT_ID` · `SHA256` · `SOURCE_ID` ·
`RUN_ID` · `STORAGE_LOCATION` · `PROVENANCE` · `SIZE` · `CONTENT_TYPE` — **PODE** viver no
banco.

> ## O CAMINHO É ENDEREÇO, NUNCA IDENTIDADE.
> A identidade é `run_id + sha256 + metadata`. Mudar o objeto de lugar **não** muda o que ele
> é.

**Esta Bíblia NÃO decreta onde os bytes ficam.** Git, Supabase Storage, sistema de ficheiros
ou outro — é decisão da missão de armazenamento, com medição própria.

**MEDIDO, e a lei já está implementada de um lado.** O bucket `raw` é privado, **um para o
EAME inteiro**, com o país no *path* e não na identidade; e `supabase-raw-roundtrip.yml`
prova a volta inteira — Git → Storage → Postgres → download → hash confere. **A Itália não
usa nada disso** (G-30).

**ORIGEM.** `EXISTING_SINTONIA_LAW` · **LAW_STATUS** `CANONICAL` · **IT** `PARTIAL`

---

## COL-LAW-312 · SEGREDO NÃO ATRAVESSA

**REGRA.** Credencial **NÃO DEVE** entrar em: a Bíblia · o estado do System Map · commits ·
logs · manifestos de corrida expostos · trechos de evidência.

O visual **PODE** mostrar `CREDENTIAL REQUIRED` e `CREDENTIAL AVAILABLE/UNAVAILABLE` quando
for seguro. **Nunca o valor.**

**MEDIDO, e há três dentes já mordendo:** `tests/test_migrations.py:144` proíbe
`SUPABASE_URL`, `SUPABASE_KEY`, `postgresql://` e `psycopg` nas migrations ·
`system-map.yml` §6 varre o que vai ser publicado atrás de padrão de credencial ·
`supabase-conexao.yml` devolve **booleano, nunca valor**, e diz explicitamente que **não
depende** do mascaramento do GitHub.

**ORIGEM.** `EXISTING_SINTONIA_LAW` · **LAW_STATUS** `CANONICAL` · **IT** `IMPLEMENTED`

---

## COL-LAW-313 · AMBIENTE FAZ PARTE DA IDENTIDADE DA CORRIDA

**REGRA.** Quando existirem ambientes (`DEV` · `PREVIEW` · `PRODUCTION` ou equivalentes),
uma corrida **DEVE** poder dizer em qual correu. **Uma corrida de preview NÃO DEVE** parecer
uma de produção.

**MEDIDO:** hoje **não há ambientes declarados** — um projeto Supabase só. `NOT_APPLICABLE`
enquanto for verdade, e a lei fica escrita para quando deixar de ser.

**ORIGEM.** `ENGINEERING_PRINCIPLE` · **LAW_STATUS** `CANONICAL` · **IT** `NOT_APPLICABLE`

---

## COL-LAW-314 · DEPLOY NÃO DECIDE QUAL DADO É VERDADE

**REGRA.** Publicar software ou interface **NÃO** determina qual dataset é canônico. Quatro
coisas separadas:

```
CODE DEPLOYMENT  ·  DATA STATE  ·  REFERENCE VERSION  ·  RUN STATE
```

**ORIGEM.** `ARCHITECTURAL_DECISION` · **LAW_STATUS** `CANONICAL` · **IT** `IMPLEMENTED`

---

## COL-LAW-315 · CONCEITO NÃO É IMPLEMENTAÇÃO FÍSICA

**REGRA.** A semântica do SINTONIA **NÃO DEVE** ficar presa ao fornecedor.
`REFERENCE SET`, `SOURCE`, `RUN`, `ARTIFACT` e `DECISION` são conceitos **do SINTONIA**;
«a tabela X do Supabase» é a implementação de hoje.

**E ISTO NÃO AUTORIZA ABSTRAÇÃO PREMATURA.** **NÃO DEVE** ser construída agora uma camada
`DatabaseProviderInterface` nem framework equivalente. Portabilidade aqui significa uma coisa
só: **manter o conceito separado da tabela no vocabulário e nos contratos.** Nada mais.

**ORIGEM.** `ENGINEERING_PRINCIPLE` · **LAW_STATUS** `CANONICAL` · **IT** `IMPLEMENTED`

---

## COL-LAW-316 · O MAPA MOSTRA RESPONSABILIDADE, NÃO SCHEMA

**REGRA.** GitHub e Supabase **DEVEM** aparecer como **infraestrutura** — nunca como fonte de
inteligência.
A visão principal mostra **responsabilidades**. As tabelas físicas vivem no **raio-X**.

> **A arquitetura governa o visual. O schema do banco não.**

O mapa **DEVE** poder distinguir `DATABASE` · `TABLE/LOGICAL STORE` · `REFERENCE SET` ·
`RUN STORE` · `STATE STORE` · `CANONICAL STORE` sem transformar cada tabela numa avenida.

**ORIGEM.** `ARCHITECTURAL_DECISION` · **LAW_STATUS** `CANONICAL` · **IT** `PARTIAL`

---

# PARTE XIX · O PLANO DE REFERÊNCIA

> **Emenda V1.2.** O contexto que se consulta muitas vezes e muda devagar — portfólio,
> produtos, substâncias, culturas, concorrentes, geografia — não é sinal diário e não é
> configuração. É uma terceira coisa, e até agora não tinha nome nesta casa.
>
> ⚠️ **Medido: o Reference Plane NÃO EXISTE hoje.** Não há tabela, política de atualização
> nem dono. É `TARGET` inteiro, e o mapa **não** o desenha como `CURRENT`.

## COL-LAW-401 · DADO DE REFERÊNCIA NÃO É CONFIGURAÇÃO

**REGRA.**

| | é | muda por |
|---|---|---|
| **REFERENCE DATA** | a lista de produtos ADAMA de hoje | atualização de dado — **sem deploy** |
| **CONFIGURATION / LEI** | a regra que diz como validar um produto | commit versionado |

Confundir os dois faz uma de duas coisas erradas: ou obriga um deploy para corrigir uma
lista, ou deixa uma lei mudar sem ninguém aprovar.

**ORIGEM.** `ENGINEERING_PRINCIPLE` · **LAW_STATUS** `CANONICAL` · **IT** `ABSENT`

---

## COL-LAW-402 · ABASTECER REFERÊNCIA TAMBÉM É COLETA

**REGRA.** A referência não nasce sozinha:

```
SOURCE → REFERENCE SUPPLY → VALIDATION → REFERENCE OWNER → REFERENCE MASTER
```

Vale todo o resto da Bíblia — procedência, RAW primeiro, decisão auditável. O que muda é a
**cadência e o contrato**. **NÃO DEVE** ser misturada com o sinal diário: um boletim de
praga e o portfólio comercial não se atualizam pelo mesmo relógio nem pelo mesmo motivo.

**ORIGEM.** `ARCHITECTURAL_DECISION` · **LAW_STATUS** `CANONICAL` · **IT** `ABSENT`

---

## COL-LAW-403 · TODA REFERÊNCIA DECLARA A SUA AUTORIDADE

**REGRA.** Cada Reference Set **DEVE** dizer de onde vem a sua autoridade:

| autoridade | exemplo |
|---|---|
| `AUTHORITATIVE_INTERNAL` | o portfólio comercial da ADAMA — quem manda é a ADAMA |
| `AUTHORITATIVE_EXTERNAL` | a autorização regulatória — quem manda é o órgão |
| `DERIVED_REFERENCE` | um sinônimo canônico criado pelo próprio SINTONIA |

Um `DERIVED_REFERENCE` **NÃO DEVE** ser apresentado como se fosse fato externo.

**ORIGEM.** `ENGINEERING_PRINCIPLE` · **LAW_STATUS** `CANONICAL` · **IT** `ABSENT`

---

## COL-LAW-404 · CONFERIR NÃO É MUDAR

**REGRA.** Todo Reference Set **DEVE** poder declarar a sua política de atualização —
`MANUAL` · `DAILY` · `WEEKLY` · `MONTHLY` · `QUARTERLY` · `ON_CHANGE` · `EVENT_DRIVEN` ·
`UNKNOWN` — e três tempos:

```
LAST_CHECKED   quando eu fui olhar
LAST_CHANGED   quando ela mudou de verdade
NEXT_DUE       quando devo olhar de novo
```

> ## `LAST_CHECKED` ≠ `LAST_CHANGED`.
> Olhar hoje e não ter mudado é uma resposta útil, e evita reprocessar o mundo inteiro por
> nada. É a mesma família da COL-LAW-029 (`NO_NEW_VERSION` ≠ `SOURCE_FAILED`).

Esta Bíblia **NÃO fixa frequências**: a cadência é da fonte, não do gosto de quem escreve.

**ORIGEM.** `CONSOLIDATED_FROM_MULTIPLE` · **LAW_STATUS** `CANONICAL` · **IT** `ABSENT`

---

## COL-LAW-405 · A REFERÊNCIA TEM HISTÓRIA

**REGRA.** Quando o histórico for materialmente relevante, o Reference Set **DEVE** preservar
validade temporal: `VALID_FROM` · `VALID_TO`. **NÃO DEVE** sobrescrever o passado em
silêncio.

**EXEMPLO, e é o caso que obriga a lei.** Um produto estava ativo em 2024 e deixou de estar
em 2026. Uma análise de 2024 que use o portfólio de 2026 responde a pergunta errada — e
parece certa.

**O MODELO DEVE PERMITIR `REFERENCE AS OF FACT_TIME`.** Não é preciso implementar agora; é
preciso não fechar a porta. Um Reference Set que só guarda o «agora» a fecha para sempre.

**LIGA-SE A** COL-LAW-201 (o fato tem tempo próprio) e COL-LAW-217 (`FIRST_SEEN`/`LAST_SEEN`).

**ORIGEM.** `ENGINEERING_PRINCIPLE` · **LAW_STATUS** `CANONICAL` · **IT** `ABSENT`

---

## COL-LAW-406 · A DEFINIÇÃO É DA ENGENHARIA; OS REGISTROS SÃO DA MEMÓRIA

**REGRA.** O Reference Plane mora nos dois lados, e cada lado guarda o que é seu:

| GitHub — a engenharia | Supabase — a memória operacional |
|---|---|
| schema · contrato · migration | os registros |
| regras de validação | versões e validade |
| a **definição** do Reference Set | `LAST_CHECKED` · `LAST_CHANGED` · `NEXT_DUE` |
| a autoridade declarada | saúde · procedência |

**NENHUMA TABELA FOI CRIADA NESTA MISSÃO.** A lei define onde cada coisa deve morar; a
construção é outra missão.

**ORIGEM.** `ARCHITECTURAL_DECISION` · **LAW_STATUS** `CANONICAL` · **IT** `ABSENT`

---

# PARTE XX · O QUE A PRIMEIRA ESTRADA ENSINOU

> **Emenda V1.3.** Quatro leis, e nenhuma delas foi inventada: **as quatro nasceram de
> medir a primeira estrada real da coleta italiana** (PDF guardado → texto derivado → porta)
> contra a Bíblia, e de encontrar quatro pontos onde a lei ainda não dizia o suficiente.
>
> As outras três questões constitucionais dessa integração — `ARTIFACT ≠ FACT`,
> `RUN COMPLETE` e os papéis de GitHub/Supabase — **já estavam resolvidas** por leis
> existentes, e por isso não viraram lei nova. A conta está em
> [`docs/biblia/RECONCILIACAO-INTEGRACAO.md`](docs/biblia/RECONCILIACAO-INTEGRACAO.md).

## COL-LAW-501 · OCORRÊNCIA NÃO É CONTEÚDO

**REGRA.**

```
OCCURRENCE / CAPTURE / SOURCE RECORD   ≠   CONTENT / BLOB / BYTES
```

Dois caminhos com o **mesmo** `SHA256` são **um conteúdo** e **duas ocorrências**. Uma
ocorrência tem fonte, corrida e momento próprios; o conteúdo tem só a sua impressão digital.

Uma contagem **NÃO DEVE** subtrair uma da outra:

```
ERRADO      49 entraram · 43 saíram  →  6 perdidos
CERTO       RAW OCCURRENCES  49
            UNIQUE CONTENT   43
            SAME-CONTENT OCCURRENCES  6
            LOST              0
```

**PRECISÃO ACRESCENTADA EM 08/09/2026 — são QUATRO espécies, não duas.** «Ocorrência» estava
a fazer o trabalho de duas palavras ao mesmo tempo, e por isso deixava passar um erro:

```
CONTENT        os bytes.       identidade = SHA-256.       não tem data nem dono
CAPTURE        uma ida à fonte. identidade = (registo, corrida, URL, quando)
STORAGE COPY   um lugar no disco. identidade = o caminho.  o caminho muda sozinho
DERIVED        o que uma ferramenta fez a partir de um conteúdo pai
```

> **CAMINHO DIFERENTE NÃO PROVA CAPTURA DIFERENTE.**
> **SHA IGUAL NÃO PROVA A MESMA CAPTURA.**

Nenhuma das duas se decide olhando para o nome da pasta. Decide-se pela **prova de captura**
do caminho: um recibo com quem foi buscar, quando, por que rota, e o que o servidor
respondeu. Sem esse recibo o caso é `UNKNOWN`, e `UNKNOWN` fica `UNKNOWN`.

**MEDIDO, e é o caso que obriga a lei.** Os 49 PDFs italianos têm **43 conteúdos únicos**. A
leitura anterior dizia que os 6 repetidos eram «sempre o mesmo par, a loja e a amostra» — e
**estava errada nas duas metades**. Medido em `system-map/scripts/censo_de_identidade_it.py`:

```
6 grupos com mais de uma cópia
6 de 6  →  INDEPENDENT_CAPTURES_SAME_CONTENT
0 de 6  →  SAME_CAPTURE_MULTIPLE_STORAGE_COPIES
0 de 6  →  UNKNOWN
```

São **duas idas reais à fonte** que trouxeram os mesmos bytes — separadas por uma a duas
horas (a mão com `curl` e depois o coletor piloto), e num dos casos por **cinco dias e uma
rota inteiramente diferente** (o pacote VPN de 02/09 via Fitogest e a amostra de 07/09 direta
do sítio da Campania). A prova não é auto-declarada: o próprio servidor datou a resposta —
`date: Mon, 07 Sep 2026 13:49:52 GMT` em `SA-02-09.pdf.headers.txt`.

**E isso vale mais do que a contagem.** Duas capturas do mesmo byte em dias diferentes são a
prova de que **o documento não mudou nesse intervalo**. Um esquema que guardasse «um caminho
por conteúdo» apagaria uma captura verdadeira, e com ela essa prova.

> **Mesmo conteúdo não é a mesma coleta.** Duas fontes podem publicar o mesmo PDF: são dois
> fatos sobre o mundo (as duas publicaram) e um conteúdo só.

**LIGA-SE A** COL-LAW-204 (dedupe não destrói a história) e COL-LAW-311 (o caminho é
endereço, a identidade é o hash). Aquelas dizem *não destrua*; esta diz *não confunda ao
contar*.

**ORIGEM.** `CONSOLIDATED_FROM_MULTIPLE` · **LAW_STATUS** `CANONICAL` · **IT** `IMPLEMENTED`

---

## COL-LAW-502 · DOCUMENTO PRONTO NÃO É FATO PRONTO

**REGRA.** São duas prontidões, em dois estágios, e **NÃO DEVEM** ser medidas pela mesma
pergunta:

| | pergunta | exige |
|---|---|---|
| `DOCUMENT READY` | este documento está apto para a **próxima transformação**? | ter sido lido, ter pai provado, ter procedência e impressão digital |
| `FACT READY` | este **fato** está completo? | `FACT_TIME` e `FACT_LOCATION` do fato — que pertencem ao **claim**, não ao documento |

Cobrar `FACT_TIME` de um documento é aplicar a régua do fato ao artefato — o que a
COL-LAW-201 já proíbe. **A resposta certa a uma pergunta que não se aplica é
`NAO_SE_APLICA`, não `NAO_SEI`.**

**MEDIDO, e é exatamente o que acontece hoje.** Os 43 textos derivados chegam à porta com
`FACT_TIME = "NAO SEI"` — nunca fabricado, e isso está certo. A porta pergunta *«tem tempo
do fato?»* (`admissao/admissao.py:169`) e devolve `NAO_SEI` aos 43.

> **Os 43 `NAO_SEI` não são um defeito dos documentos. São a porta a fazer, no estágio do
> documento, uma pergunta que é do estágio do fato.**

**E A PORTA JÁ SABE FAZER ISTO CERTO NOUTRO SÍTIO.** Para ficha de conta e de catálogo ela
já responde `NAO_SE_APLICA`, com a frase: *«a pergunta não se aplica — o que está aqui é o
registo de ONDE se pode coletar, não o que se coletou»*. É o mesmo mecanismo.

**NÃO DEVE** ser criado estado novo para isto: os cinco resultados da COL-LAW-038 já
bastam. **NÃO DEVE** ser inventada data para deixar os 43 verdes (COL-LAW-031 · 035).

**AÇÃO:** gap **G-22**, e **não foi corrigido nesta missão** — é runtime da porta.

**ORIGEM.** `CONSOLIDATED_FROM_MULTIPLE` · **FECHADO EM 08/09/2026 (G-22).** A porta le o ESTAGIO do item e faz as perguntas
aplicaveis: DOCUMENTO responde por legivel, origem e linhagem; FATO responde tambem pelo
tempo do fato. Nao se criou segunda porta. Os 43 derivados passaram de «todos NAO_SEI por
falta de FACT_TIME» para 18 SIM · 19 NAO · 6 NAO_SEI — resposta semantica, com prova, e
sem nenhuma data inventada.

**LAW_STATUS** `CANONICAL` · **IT** `IMPLEMENTED`

---

## COL-LAW-503 · FERRAMENTA QUE FALTA NÃO É DOCUMENTO QUEBRADO

**REGRA.**

```
EXECUTOR_UNAVAILABLE · CAPABILITY_UNAVAILABLE · PREFLIGHT_ERROR
        ≠
ARTIFACT_EXTRACTION_ERROR
```

Quando a capacidade não existe na máquina, a corrida **DEVE** falhar **no pré-voo** — antes
de tocar nos documentos. **NÃO DEVE** percorrer N artefatos e marcá-los como defeituosos.

> **É a COL-LAW-215 aplicada à ferramenta: o nosso bug não vira defeito do mundo.** Um
> `EXTRACTION_ERROR` em 43 documentos sãos leva alguém a investigar 43 PDFs quando o que
> falta é um programa.

**MEDIDO.** `coleta/executor_texto_de_pdf.py:140-141`: sem `pdftotext`, **todo** PDF volta
com `EXTRACTION_ERROR`. O **motivo** é honesto (`"FERRAMENTA_AUSENTE: pdftotext"`) e o
cabeçalho do ficheiro até declara a intenção certa — mas o **contador** que sobe é o do erro
de extração. A intenção está escrita; a medição não a acompanha.

**Nesta máquina `pdftotext` existe**, e os 43 saíram com `0 EXTRACTION_ERROR`. O defeito é
condicional, e por isso mais perigoso: só aparece onde a ferramenta falta.

**NÃO DEVE** ser instalada ferramenta nenhuma para «resolver» isto. A correção é de
**semântica e de ordem**: pré-voo primeiro.

**AÇÃO:** gap **G-34**, não corrigido nesta missão.

**ORIGEM.** `CONSOLIDATED_FROM_MULTIPLE` · **FECHADO EM 08/09/2026 (G-34).** A corrida verifica a capacidade no passo 0. Sem
`pdftotext` ela para com `FAILED_PRECONDITION` e `EXECUTOR_UNAVAILABLE`, **sem tocar em
nenhum documento** — provado por teste que retira a capacidade e mede
`RAW_EXTRACTION_ERROR = 0`. Nada foi instalado.

**LAW_STATUS** `CANONICAL` · **IT** `IMPLEMENTED`

---

## COL-LAW-504 · A ÁRVORE ESCANEADA NÃO É O COMMIT QUE PUBLICA O MAPA

**REGRA.** São duas perguntas diferentes, e **NÃO DEVEM** partilhar um campo:

```
SOURCE_HEAD / SOURCE_TREE   qual árvore real foi escaneada?
MAP_ARTIFACT_COMMIT         em que commit o artefato do mapa foi publicado?
```

E **NÃO DEVE** ser perseguida a igualdade `SOURCE_HEAD == FINAL_HEAD`: ela é **circular por
construção**. O mapa é gerado a partir de uma árvore; commitá-lo cria um commit novo; o
carimbo fica velho no instante em que é gravado. Perseguir isso produz um commit de carimbo
atrás do outro, para sempre.

**MEDIDO.** O modelo de hoje tem **um campo só** — `PROVENANCE.HEAD` — a fazer os dois
trabalhos. E o ramo da engenharia carrega **três commits** chamados literalmente
*«carimbo do HEAD nos ficheiros gerados»*: é a perseguição, registrada na história.

> **É o mesmo defeito do `EAME_COLLECTION_ENTRY_GATE`: um nome a fazer dois trabalhos.** A
> casa já pagou por ele uma vez.

**A SAÍDA NÃO É UM CARIMBO MELHOR: É PARAR DE COMPARAR COMMITS.** O que identifica a árvore
escaneada de forma estável é a **impressão digital do conteúdo** (`SOURCE_TREE_FINGERPRINT`),
que não muda quando o commit muda de nome. O `MAP_ARTIFACT_COMMIT` é opcional e só se sabe
**depois** de commitar.

**NÃO IMPLEMENTADO NESTA MISSÃO.** A lei define o modelo; mexer no gerador é outra missão.
Gap **G-35**.

**ORIGEM.** `ARCHITECTURAL_DECISION` · **LAW_STATUS** `CANONICAL` · **IT** `ABSENT`

---

# PARTE XXI · A LEI DOS COMPONENTES E DOS CARTÕES — CARD CONTRACT V1

> **Emenda V1.4.** Esta parte **não reorganiza cartão nenhum**. Ela escreve a lei que
> governará a reorganização futura — e que impedirá que os cartões voltem a ficar
> desarrumados depois de arrumados.
>
> ```
> COL-LAW-104   o que um componente tem de conseguir MOSTRAR
> PARTE XXI     o que um componente É, e o que ele NÃO PODE decidir
> ```
>
> **Ela não cria uma segunda autoridade sobre componentes.** A COL-LAW-104 (contrato de
> componente renderizável) e a COL-LAW-105 (contrato de conexão renderizável) continuam
> inteiras e continuam a ser o contrato de **exibição**. Esta parte acrescenta o que
> faltava do outro lado: o contrato de **responsabilidade**. Onde a 104 diz `ROLE`, esta
> parte define o que um papel é; onde a 105 diz `TYPE`, esta parte **não** redefine nada —
> aponta para a COL-LAW-048, que já é a dona dessa taxonomia.
>
> **E ela não recomeça do zero.** Quase tudo aqui já tinha sido descoberto a medir esta
> árvore, uma frase de cada vez: *«uma gaveta não é uma função»*, *«um import não é um
> carimbo»*, *«executar a corrida não é ser a autoridade sobre a procedência dela»*,
> *«um dono eleito por ordem alfabética não é um dono»*. Estavam espalhadas por relatórios
> de missão, onde nenhum portão as alcança. Aqui viram lei, com nome e número.
>
> **O universo censado não muda por causa desta parte.** Os 130 componentes declarados, os
> 157 cartões e as 608 arestas de hoje continuam exactamente como estão. O censo mede uma
> fotografia; mexer nela a meio da medição faria com que ninguém soubesse mais qual das
> duas coisas mudou o resultado.

## COL-LAW-601 · CARTÃO NÃO É FICHEIRO

**REGRA.** Um cartão do System Map representa uma **responsabilidade arquitetural
identificável**, com dono, tipo, fronteira, entradas, saídas e autoridade explícita.
**NÃO É** um ficheiro, uma pasta, um módulo, nem um agrupamento de imports.

```
1 ficheiro   PODE implementar 1 cartão, PARTE de 1 cartão, ou conter subcomponentes
1 cartão     PODE possuir vários ficheiros
```

**AGRUPAMENTO NÃO CRIA RESPONSABILIDADE.** Estar na mesma pasta, estar no mesmo ficheiro,
ou importar-se um ao outro **NÃO DEVE** ser lido como prova de que duas coisas são a mesma
responsabilidade.

> **UMA GAVETA NÃO É UMA FUNÇÃO.**

**POR QUÊ.** A prateleira (`AGENTS.md`) diz onde um ficheiro **mora**. Ela nunca disse o
que a peça **faz** — e durante meses o mapa deixou a pasta responder por ela. A gaveta
«OS VEÍCULOS» passou meses sem conter um único veículo (COL-LAW-009), e a divisão entre
`regras/` e `medidas/` só parou de ser palpite quando passou a ser medida pelo que cada
peça **produz** e por **quem a consome** — nunca pela pasta.

**VIOLAÇÃO MEDIDA, HOJE, NESTA ÁRVORE.** A gaveta continua a discordar da função em peças
que ninguém errou de propósito: `C-INGRESSO` — a porta de entrada da coleta — é do tipo
`gate` e vive em `Z-ACOES`, a zona dos executores; `C-DONO-DA-ESCRITA` e
`C-DONO-DO-DERIVADO` guardam estágios diferentes e estão ambos como `engine`. Nenhuma
destas é uma peça mal feita. São peças cujo **tipo** e cuja **gaveta** respondem a
perguntas diferentes, e hoje só uma delas está escrita.

**COMO PROVAR.** `P8_UM_DONO` e `P9_CODIGO_DECLARADO` em
`system-map/scripts/validate_system_map.py` já provam a metade fácil: todo ficheiro de
código pertence a um cartão, e nenhum a dois. A outra metade — que o cartão é uma
responsabilidade, e não um saco de ficheiros — é o que esta parte passa a exigir.

**CONTRATOS.** `system-map/data/architecture.declared.json` ·
`system-map/contracts/CARD-CONTRACT-V1.md`
**ORIGEM.** `CONSOLIDATED_FROM_MULTIPLE` · **LAW_STATUS** `CANONICAL` · **IT** `PARTIAL`

---

## COL-LAW-602 · TODO CARTÃO RESPONDE A UMA PERGUNTA — `OWNS_QUESTION`

**REGRA.** Todo cartão canônico **DEVE** declarar identidade e responsabilidade:

```
IDENTIDADE        CARD_ID · NAME · TYPE · OWNER · LIFECYCLE
RESPONSABILIDADE  PURPOSE · OWNS_QUESTION
```

`OWNS_QUESTION` é **a pergunta principal cuja autoridade pertence àquele cartão**. É o
teste mais curto de que o cartão existe por um motivo, e não por um ficheiro.

**DUAS PEÇAS NÃO PODEM SER DONAS DA MESMA PERGUNTA.** Se forem, ou uma é subcomponente da
outra, ou há duas verdades — e a segunda envelhece calada. É a mesma lei do dono único que
já governa a orquestração (COL-LAW-011) e o cadastro da fonte (COL-LAW-053).

**EXEMPLO — perguntas desta árvore, e não perguntas inventadas:**

| cartão | `OWNS_QUESTION` |
|---|---|
| `C-PEDIDO` | «o que foi solicitado?» |
| `C-ORQUESTRADOR` | «como atender este pedido?» |
| `C-INGRESSO` | «por onde entra o que foi colhido?» |
| `C-DONO-DA-ESCRITA` | «que unidade bruta ficou preservada?» |
| `C-ADMISSAO` | «isto entra neste universo, não entra, ou NÃO SEI?» |
| `C-PROCEDENCIA` | «de onde veio isto, e em que corrida?» |

**VIOLAÇÃO MEDIDA.** Três peças escreviam `data/samples/RUN-MANIFEST.json`, e o mapa
elegia dono **por ordem alfabética**: o dono mudou sozinho de uma peça para outra sem
ninguém tocar no repositório.

> **UM DONO ELEITO POR ORDEM ALFABÉTICA NÃO É UM DONO.**
> **EXECUTAR A CORRIDA NÃO É SER A AUTORIDADE SOBRE A PROCEDÊNCIA DELA.**

**COMO PROVAR.** `P8_DONO_CANONICO` já prova o caso do artefato com dono declarado
(`CANONICAL_OWNERS` em `system-map/data/state.generated.json`). Para a **pergunta** não há
prova nenhuma: nenhum dos 130 componentes declarados desta árvore declara `OWNS_QUESTION`.

**ORIGEM.** `ARCHITECTURAL_DECISION` · **LAW_STATUS** `CANONICAL` · **IT** `ABSENT`

---

## COL-LAW-603 · AS PORTAS DO CARTÃO

**REGRA.** Todo cartão **DEVE** poder declarar, **quando aplicável**, as suas portas:

```
CONTROL_IN   CONTROL_OUT      quem manda em mim · em quem eu mando
DATA_IN      DATA_OUT         o que atravessa a linha, nos dois sentidos
POLICY_IN    POLICY_OUT       a regra que recebo · a decisão que publico
CONFIG_IN                     o que me parametriza sem me mandar
READS        WRITES           o que leio · o que escrevo
STATE_OUT                     onde parei
PROOF_OUT                     a evidência que deixo
META_OUT                      o que digo sobre mim — contagens, custo, tempo
```

**AUSÊNCIA É AUSÊNCIA.** Porta inaplicável **NÃO DEVE** ser preenchida para deixar o
desenho simétrico. `UNKNOWN` e `NOT_APPLICABLE` são coisas diferentes (COL-LAW-035), e
inventar porta é, do lado do cartão, o que a COL-LAW-105 já proíbe do lado da aresta.

> **DUAS ENTRADAS E DUAS SAÍDAS NÃO IMPLICAM QUE TODAS AS ENTRADAS ALIMENTAM TODAS AS
> SAÍDAS.**

**RELAÇÃO COM A COL-LAW-104.** A 104 lista o que o cartão tem de **mostrar** —
`INPUTS` · `OUTPUTS` · `READS` · `WRITES` · `CONTROLS` · `RULES`. Esta lei diz **de que
natureza** é cada porta, para que uma ligação de controle não entre pela porta do dado. É
a mesma lista, separada pelos dois planos que a COL-LAW-012 já separa.

**ORIGEM.** `ARCHITECTURAL_DECISION` · **LAW_STATUS** `CANONICAL` · **IT** `ABSENT`

---

## COL-LAW-604 · `DECIDES` E `MUST_NOT_DECIDE`

**REGRA.** Todo cartão **DEVE** declarar as duas listas:

```
DECIDES           as decisões que lhe pertencem
MUST_NOT_DECIDE   as decisões que, se ele tomar, são defeito de arquitetura
```

**Se o runtime provar que um componente toma uma decisão declarada como proibida, isso
DEVE ser tratável como `ARCHITECTURE_MISMATCH`** — e **NÃO DEVE** ser resolvido apagando a
proibição para o mapa ficar verde.

**POR QUÊ.** Sem a segunda lista, toda peça parece bem-comportada: vê-se o que ela faz,
nunca o que ela não devia estar a fazer. Com a segunda lista, um defeito antigo ganha nome
na primeira medição — e nome é o que permite fechá-lo.

**VIOLAÇÃO MEDIDA.** «Como atender este pedido» é decidido em **três** sítios: a receita
escolhe fonte, rota e executor; o orquestrador escolhe executor; e o SINTONIA SCRAP escolhe
a rota da fase (`COL-010`, em `system-map/data/SYSTEM-MAP-COLLECTION-ISSUES.json`). A
COL-LAW-011 já proibia isto desde a V1. O que faltava era o campo onde a proibição se
escreve **por cartão**, para deixar de ser uma frase que só um humano atento aplica.

**ORIGEM.** `ARCHITECTURAL_DECISION` · **LAW_STATUS** `CANONICAL` · **IT** `ABSENT`

---

## COL-LAW-605 · OS TIPOS CANÔNICOS DE CARTÃO

**REGRA.** `UM TIPO → UM SIGNIFICADO.` Todo cartão **DEVE** declarar um `TYPE`, e o `TYPE`
**DEVE** vir desta lista. **Nenhum tipo aqui foi inventado:** cada um tem gaveta na
prateleira (`AGENTS.md`) ou papel já medido nesta árvore.

| `TYPE` | na língua da casa | decide | **NÃO DEVE** decidir |
|---|---|---|---|
| `TRIGGER` | a entrada · o botão | **quando** começa | qual ferramenta, qual rota, qual executor |
| `CONTRACT` | o pedido · a ficha | **o que** se quer | como se faz |
| `REGISTRY` | o cadastro (`fontes/` · `candidatas/`) | **que opções existem** | qual opção se usa |
| `POLICY` | a receita · a política | **qual opção se usa** | executar a opção que escolheu |
| `ORCHESTRATOR` | o orquestrador | **quem faz o quê, e em que ordem** | transportar dado, julgar conteúdo |
| `EXECUTOR` | a ação (`coleta/`) | **como realizar esta aquisição** | se o item pertence ao universo |
| `TOOL` | a ferramenta (`ferramentas/`) | **como se faz tecnicamente este pedaço** | o que colher, de onde, quando |
| `ADAPTER` | o tradutor do que vem de fora | **como o de fora vira o contrato de casa** | o que o de fora significa |
| `GATE` | a porta (`admissao/` · `portoes/`) | **entra · não entra · NÃO SEI** | qual alternativa usar quando recusa |
| `RULE` | a régua que carimba (`regras/`) | **o que fica escrito no item ao entrar** | se o item entra |
| `TRANSFORM` | o motor (`motor/`) | **que representação sai desta** | ocupar o lugar do original preservado |
| `STORE` | a guarda (`guarda/`) | **que unidade fica preservada, e de que estágio** | o que a unidade significa |
| `MEASURE` | a régua que mede (`medidas/`) | **o que aconteceu nesta etapa** | barrar, escolher, corrigir |
| `PROOF` | a prova (`provas/` · `tests/`) | **isto é verdade** | mudar aquilo que mede |
| `SURFACE` | a tela · o pacote (`superficie/` · `pacote/`) | **como uma pessoa vê isto** | recalcular a decisão do motor |
| `EXTERNAL` | o veículo — de onde o dado vem | **nada desta casa** | tudo |

**TIPO NÃO É GAVETA, E NÃO É FAMÍLIA.** São três eixos, e já há prova disso: quem carimba
vive em **duas** famílias diferentes. Os três papéis já medidos nesta árvore —
`STAMPS` 3 · `MEASURES` 15 · `DECLARES` 11 — são a leitura fina do que aqui se chama
`RULE` e `MEASURE`, e foram decididos pelo que a peça produz e por quem a consome.

**ANTES DE CRIAR UM TIPO NOVO: procurar o equivalente.** É a mesma disciplina da PARTE XIV.
Dezenas de tipos são a mesma coisa que nenhum tipo.

**⚠️ `ARCHETYPE` NÃO É PALAVRA LIVRE.** Ela já tem dono nesta casa — os arquétipos de
oportunidade do motor V2.1 (`O3_RESISTANCE_MOA` · `O4_COMPETITIVE_OPENING` ·
`O5_REGULATORY_PREPARATION`). O tipo do cartão chama-se `TYPE`, e nunca `ARCHETYPE`.

**ESTADO HONESTO.** O mapa de hoje já tem um campo de tipo — `kind` —, e ele **não é esta
taxonomia**. São 12 valores para 130 componentes, e **63 deles estão no valor genérico**:

```
engine 63 · contract 25 · gate 16 · test 6 · workflow 6 · library 5
surface 4 · proof 1 · chain 1 · artifact 1 · store 1 · scanner 1
```

Dois desses valores — `proof` e `scanner` — nasceram depois dos outros, um de cada vez, sem
lista fechada a que obedecer. **A conversão para esta taxonomia é trabalho futuro, e não
foi feita aqui.** E `artifact` não é tipo de cartão nenhum: artefato é **entidade**
(COL-LAW-009), não responsabilidade.

**ORIGEM.** `CONSOLIDATED_FROM_MULTIPLE` · **LAW_STATUS** `CANONICAL` · **IT** `PARTIAL`

---

## COL-LAW-606 · MEDIR NÃO É FAZER — A LEI DO SENSOR

**REGRA.** `MEASURE` **observa** uma operação. Ele **NÃO DEVE** tornar-se executor da
operação que observa.

Se um componente **escolhe ferramenta**, **abre rota**, **chama coletor** ou **executa
aquisição**, ele **NÃO DEVE** ser classificado como `MEASURE` só porque também mede.

> **MEDIR NÃO É FILTRAR, E TAMBÉM NÃO É COLHER.**

**POR QUÊ.** Uma régua que mede não barra nada: ela conta quanto falta. Pô-la no caminho
faz parecer que há peneira onde só há termômetro — e foi exactamente essa confusão que
deixou a coleta anos sem porta de admissão.

**COMO PROVAR.** `regua_que_carimba_nao_e_regua_que_mede`, em
`system-map/tests/test_system_map.py`. A pergunta dela era indecidível enquanto olhava quem
importa quem; ficou decidível quando passou a olhar o que a peça **produz** e **quem
consome** o que ela produz.

**ORIGEM.** `EXISTING_SINTONIA_LAW` (`AGENTS.md`, §«Régua que carimba não é régua que
mede») · **LAW_STATUS** `CANONICAL` · **IT** `PARTIAL`

---

## COL-LAW-607 · COORDENAR NÃO É TRANSPORTAR — A LEI DO ORQUESTRADOR

**REGRA.** `ORCHESTRATOR` **coordena componentes**. Coordenação **NÃO É**:

```
transporte · scraping · HTTP · armazenamento · julgamento de conteúdo
```

Um componente que faz qualquer uma dessas coisas **NÃO DEVE** ser tipado `ORCHESTRATOR`
por também coordenar.

**Esta lei é a COL-LAW-011 e a COL-LAW-012 ditas no vocabulário do cartão** — não é uma
segunda lei sobre o orquestrador. E ela **NÃO DEVE** codificar detalhe do runtime de hoje:
o nome do ficheiro pode mudar; a separação dos dois planos, não.

**COMO PROVAR.** `orquestrador/orquestrador.py` · `provas/testa_coleta_canonica.py`
**ORIGEM.** `EXISTING_SINTONIA_LAW` · **LAW_STATUS** `CANONICAL` · **IT** `PARTIAL`

---

## COL-LAW-608 · REGISTRO ≠ POLÍTICA ≠ PORTÃO

**REGRA.** São três autoridades, e juntá-las esconde a mais importante das três.

| | responde | **não** responde |
|---|---|---|
| `REGISTRY` | «que opções, fatos ou configuração canônica existem?» | qual se usa |
| `POLICY` | «qual opção se usa, e segundo que regra?» | se o resultado pode entrar |
| `GATE` | «entra, não entra, ou NÃO SEI?» | qual alternativa usar |

**UM PORTÃO NÃO ESCOLHE ALTERNATIVA AO RECUSAR.** Recusar e propor são duas decisões, e a
segunda pertence à `POLICY`. Um portão que sugere o caminho seguinte deixou de ser portão.

**E O `NÃO SEI` É RESULTADO VÁLIDO DO PORTÃO** — nunca um `NÃO` disfarçado (COL-LAW-035).

**COMO PROVAR.** `admissao/admissao.py` (portão) · `pedido/receitas.py` (política) ·
`system-map/data/sources.generated.json` (registro)
**ORIGEM.** `CONSOLIDATED_FROM_MULTIPLE` · **LAW_STATUS** `CANONICAL` · **IT** `PARTIAL`

---

## COL-LAW-609 · EXECUTOR ≠ FERRAMENTA ≠ ADAPTADOR

**REGRA.** Três coisas, três donos.

```
EXECUTOR   faz o trabalho de domínio           — vai buscar, e guarda
TOOL       fornece capacidade técnica          — com que se viaja
ADAPTER    traduz um serviço externo para o contrato interno
```

**O facto de um executor usar Apify, navegador ou API NÃO transforma a ferramenta em dona
da decisão de domínio.** A ferramenta responde «como se faz tecnicamente»; ela nunca
responde «o que colher, de onde, quando».

**Esta lei estende a regra irmã já madura** — `FERRAMENTA` · `VEÍCULO` · `AÇÃO`
(COL-LAW-009) — acrescentando `ADAPTER`, que hoje **não tem gaveta própria** e vive
diluído dentro de `ferramentas/`. Enquanto não tiver, `ADAPTER` é tipo declarado e não
gaveta — e isso **DEVE** ficar dito, em vez de escondido.

**VIOLAÇÃO MEDIDA.** Dois botões chamam a Apify **pelo nome**
(`.github/workflows/apify-conexao.yml` e `.github/workflows/apify-sensores.yml`). Um botão
devia dizer **o quê**; nunca **qual ferramenta** (`COL-008`).

**COMO PROVAR.** `P2_PASTA_BATE_COM_MAPA` · `ferramentas/apify_pool.py` ·
`ferramentas/contrato_ator.py`
**ORIGEM.** `EXISTING_SINTONIA_LAW` · **LAW_STATUS** `CANONICAL` · **IT** `PARTIAL`

---

## COL-LAW-610 · A GUARDA PRESERVA; A TRANSFORMAÇÃO PRODUZ OUTRA REPRESENTAÇÃO

**REGRA.**

```
STORE      preserva uma unidade — e diz QUAL estágio preserva
TRANSFORM  recebe uma representação e produz outra, com linhagem
```

`RAW` ≠ `DERIVED` ≠ `STRUCTURED`. O nome genérico «guarda» **NÃO DEVE** fazer desaparecer
o estágio que está a ser preservado: um cartão `STORE` **DEVE** dizer de que estágio é
dono, e dois estágios diferentes **não** são o mesmo cartão só por viverem na mesma gaveta.

**POR QUÊ.** É a COL-LAW-006 e a COL-LAW-007 no vocabulário do cartão. A esteira medida tem
dono para o `RAW` (`guarda/preservar_coleta.py`) e dono para o `DERIVED`
(`guarda/preservar_derivado.py`) — e o `STRUCTURED` tem **cinco escritores e nenhum dono
único**. Sem esta lei, os três cabiam num cartão chamado «a guarda», e o buraco do meio
desaparecia do mapa por arrumação.

**COMO PROVAR.** `docs/operacao/TOPOLOGIA-DA-COLETA.md` §3 — a esteira, dono a dono.
**ORIGEM.** `CONSOLIDATED_FROM_MULTIPLE` · **LAW_STATUS** `CANONICAL` · **IT** `PARTIAL`

---

## COL-LAW-611 · SUBCOMPONENTES — SIMPLICIDADE VISUAL NÃO É OCULTAÇÃO ARQUITETURAL

**REGRA.** Nem toda unidade técnica precisa de virar cartão principal no mapa. Um cartão
**PODE** ter `SUBCOMPONENTS`.

**Mas subcomponente com autoridade própria relevante DEVE continuar visível e
inspecionável.** O mapa principal **PODE** mostrar só o componente; ao abrir, as partes
relevantes **DEVEM** aparecer.

> **VISUAL SIMPLICITY ≠ ARCHITECTURAL HIDING.**

**É a COL-LAW-109 (níveis de zoom) aplicada ao cartão**, e o limite dela é a COL-LAW-101: a
UI escolhe o nível de detalhe; a arquitetura escolhe o que existe para ser mostrado.
Esconder uma autoridade dentro de outra por ficar bonito é a única maneira de o mapa
emagrecer sem o sistema emagrecer.

**ORIGEM.** `ARCHITECTURAL_DECISION` · **LAW_STATUS** `CANONICAL` · **IT** `ABSENT`

---

## COL-LAW-612 · A ARESTA TEM SIGNIFICADO

**REGRA.** Uma aresta **NÃO É** `A → B`. Toda aresta **DEVE** declarar:

```
FROM · TO · TYPE · DIRECTION
```

e, **quando aplicável**, `PAYLOAD` / `CONTRACT` — o que atravessa a linha, e sob que
contrato.

**A TAXONOMIA DO `TYPE` É A DA COL-LAW-048, E NÃO UMA SEGUNDA.** Sete valores, já medidos
e já publicados no estado gerado:

```
READ 171 · PROOF 170 · RULE 91 · CODE 70 · CONTROL 63 · DATA 36 · WRITE 7
```

`POLICY` **não entra como oitavo nome**: a decisão de política atravessa como `RULE`, que é
o nome que esta casa já usa e já mede. `CONFIG` e `META` **não entram**: nenhuma aresta
desta árvore foi medida como uma delas, e categoria sem referente é vocabulário que
envelhece antes de ser usado. Entram no dia em que uma medição as exigir — é a mesma
disciplina que recusou três das quatro entidades candidatas na emenda V1.1.

**`DIRECTION` É A DIREÇÃO DO QUE ATRAVESSA, NÃO A DA CHAMADA.** A ação chama o YouTube, e
isso é controlo; o que atravessa a linha é a colheita, e ela corre ao contrário
(COL-LAW-048).

**ORIGEM.** `CONSOLIDATED_FROM_MULTIPLE` · **LAW_STATUS** `CANONICAL` · **IT** `PARTIAL`

---

## COL-LAW-613 · AS LEIS ANTI-FALSO-POSITIVO DO CARTÃO E DA ARESTA

**REGRA.** Nenhuma destas equivalências **DEVE** ser feita — nem por scanner, nem por
pessoa, nem por desenho:

```
IMPORT              ≠ CONTROL
IMPORT              ≠ DATA FLOW
READ                ≠ WRITE
PROOF               ≠ RUNTIME
TEST CALLER         ≠ PRODUCTION CALLER
COMMENT             ≠ EDGE
DOCSTRING           ≠ EDGE
NOME DE COMPONENTE  ≠ EVIDÊNCIA DE RESPONSABILIDADE
MODULE EXISTS       ≠ EDGE EXISTS ≠ FLOW EXISTS
DECLARED            ≠ OBSERVED
```

**Nenhuma delas foi suposta.** Cada uma custou uma medição, e todas foram medidas sobre
arestas que o mapa publicava como `PROVEN`:

| equivalência | o que ela produziu, medido |
|---|---|
| `DOCSTRING` = aresta | 3 arestas cuja prova era uma linha **dentro de um docstring** — duas delas o varredor a ler a própria documentação |
| `COMMENT` = aresta | a prova de `V-LINKEDIN → C-SCRAP-SOCIAL` era uma linha do bloco **adversarial**, que existe para provar aquela rota **fechada** |
| `NOME` = evidência | 4 arestas nasceram de o código **nomear** um canal; nomear não é ter vindo por ele |
| `READ` = `WRITE` | um `=>` de JavaScript apanhado por uma regra que procurava `>` fez 4 leituras virarem escritas — e uma delas publicava o **leitor** de um livro como seu **autor** |
| `IMPORT` = carimbo | a seta do import aponta ao contrário da dependência, e por isso não decide papel nenhum |

> **UM IMPORT NÃO É UM CARIMBO.**
> **O CÓDIGO NOMEAR UM CANAL NÃO É ALGO TER VINDO POR ELE.**

**Sem prova: `UNKNOWN`.** Ausência de prova não é prova de ausência — e também não é prova
de presença.

**COMO PROVAR.** `P5_ARESTA_PROVADA` · `P5_PROVA_APONTAVEL` · `P5_PROVA_TEM_CONTEUDO` ·
`P7_NAO_SEI_VIVE`
**ORIGEM.** `CONSOLIDATED_FROM_MULTIPLE` · **LAW_STATUS** `CANONICAL` · **IT** `PARTIAL`

---

## COL-LAW-614 · CICLO DE VIDA E EVIDÊNCIA SÃO DOIS EIXOS

**REGRA.** Um cartão carrega **dois** estados, e eles **NÃO DEVEM** ser misturados:

```
LIFECYCLE   PROPOSED · ACTIVE · DEPRECATED · RETIRED      — que lugar ele ocupa
EVIDENCE    DECLARED · CODE · OBSERVED · BIBLE · UNKNOWN  — o que se consegue provar
```

O eixo da evidência **é o da COL-LAW-102**, e não um novo. `WIRED` **não entra como nome
novo**: é exactamente o que esta casa já chama `CODE` — «há implementação real que
permite». Dois nomes para um conceito é o começo de duas verdades.

**Um componente PODE ser `ACTIVE` + `CODE` sem ser `OBSERVED`.** «Está ligado» nunca
significa «já correu» — é a mesma separação que a Bíblia inteira faz entre `LAW_STATUS` e
`IMPLEMENTATION`.

**`DEPRECATED` NÃO É `PROPOSED`, E `RETIRED` NÃO É `FUTURO`.** A casa já pagou por esta
confusão: legado é o que morreu; futuro é o que está pronto e parado. Marcar o piloto de
Espanha como legado seria enterrá-lo vivo (COL-LAW-050).

**ESTADO HONESTO.** Hoje existe metade: as quatro verdades da COL-LAW-102, os quatro
estados de exibição (`PROVEN` · `PENDING` · `BROKEN` · `UNKNOWN`) e os três estados de rota
(`official` · `futuro` · `legacy`). **`LIFECYCLE` não existe como campo de cartão**, e os
dois eixos ainda não estão separados no contrato.

**ORIGEM.** `CONSOLIDATED_FROM_MULTIPLE` · **LAW_STATUS** `CANONICAL` · **IT** `PARTIAL`

---

## COL-LAW-615 · NENHUM CARTÃO NASCE NO DESENHO

**REGRA.** Um cartão **NÃO DEVE** ser criado directamente no desenho do System Map. O
caminho canônico é:

```
NECESSIDADE → CARD CONTRACT → VALIDAÇÃO → CHECAGEM ARQUITETURAL
            → EVIDÊNCIA DE RUNTIME → SYSTEM MAP
```

**O System Map apresenta. Ele não é autoridade por desenho.** É a COL-LAW-047 e o
`AGENTS.md` §«MUDAR PELO MAPA — NÃO» ditos do lado de quem **cria** a peça, e não do lado
de quem a **mostra**.

> **NUNCA `browser → desenha seta → vira verdade`.**

**A definição de pronto continua a ser a da COL-LAW-110** —
`FUNCTIONAL + TESTED + PROVEN + OBSERVABLE + SYSTEM MAP PARITY PASS + BIBLE COMPLIANCE
KNOWN`. Esta lei acrescenta o degrau que vem **antes** de tudo isso: o contrato do cartão.

**ORIGEM.** `CONSOLIDATED_FROM_MULTIPLE` · **LAW_STATUS** `CANONICAL` · **IT** `PARTIAL`

---

## COL-LAW-616 · DUAS AUTORIDADES NUM CARTÃO É `SPLIT_CANDIDATE`

**REGRA.** Se um componente possuir **duas ou mais autoridades primárias independentes**,
ele **DEVE** ser auditado como `SPLIT_CANDIDATE`.

**Isto é um sinal forte, não uma regra burra.** `SPLIT_CANDIDATE` **NÃO É** split
automático: quem decide é a evidência — os chamadores, o que a peça produz, e quem consome
o que ela produz.

**PRECEDENTE MEDIDO.** `C-GESTAO-COLETA` juntava duas autoridades distintas. Os chamadores
provaram que eram duas coisas, e os nomes vieram da função real: `C-POLITICA-COLETA` («o
que colher, quando, e se já temos» — 1 chamador, e é um teste) e `C-DIAGNOSTICO` («onde o
fluxo parou e quem tem de agir» — 17 códigos, chamado por runtime, provas e testes).

**COMO PROVAR.** `system-map/scripts/censo_da_topologia.py` mede chamadores e consumo;
`docs/operacao/TOPOLOGIA-DA-COLETA.md` §3A guarda o caso.
**ORIGEM.** `ARCHITECTURAL_DECISION` · **LAW_STATUS** `CANONICAL` · **IT** `ABSENT`

---

## COL-LAW-617 · MERGE EXIGE AUTORIDADE REALMENTE ÚNICA

**REGRA.** Dois cartões **NÃO DEVEM** ser unidos só porque:

```
estão no mesmo ficheiro · estão na mesma pasta
um chama o outro · têm nomes parecidos
```

`MERGE` exige **responsabilidade arquitetural realmente única**: a mesma `OWNS_QUESTION`,
o mesmo `DECIDES`, a mesma fronteira.

**POR QUÊ.** É a COL-LAW-601 lida ao contrário: se agrupamento não cria responsabilidade,
agrupamento também não a funde. Cinco peças desta árvore chamam-se «SINTONIA SCRAP» e
divergiam só no fim do rótulo; medidas, eram **cinco papéis distintos** — despacho de
aquisição, despacho de rota, executor, guarda de credencial e regras. Fundi-las por nome
teria apagado quatro autoridades de uma vez.

**COMO PROVAR.** `docs/operacao/TOPOLOGIA-DA-COLETA.md` §4 — o dossiê do SINTONIA SCRAP.
**ORIGEM.** `ARCHITECTURAL_DECISION` · **LAW_STATUS** `CANONICAL` · **IT** `ABSENT`

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
| E | [`docs/biblia/EMENDA-V1-1.md`](docs/biblia/EMENDA-V1-1.md) — o registro constitucional da V1.1 |
| F | [`docs/biblia/CENSO-DA-INFRAESTRUTURA.md`](docs/biblia/CENSO-DA-INFRAESTRUTURA.md) — GitHub e Supabase medidos, antes de a lei ser escrita |
| G | [`docs/biblia/EMENDA-V1-2.md`](docs/biblia/EMENDA-V1-2.md) — o registro constitucional da V1.2 |
| H | [`docs/biblia/RECONCILIACAO-INTEGRACAO.md`](docs/biblia/RECONCILIACAO-INTEGRACAO.md) — a V1.3: a lei confrontada com a primeira estrada real, questão por questão |
| I | [`system-map/contracts/CARD-CONTRACT-V1.md`](system-map/contracts/CARD-CONTRACT-V1.md) — a V1.4: o CARD CONTRACT em forma operacional, o vocabulário de hoje medido contra ele, e o que foi recusado |

**Validadores:** `py provas/valida_biblia.py` · `py tests/test_biblia.py`
