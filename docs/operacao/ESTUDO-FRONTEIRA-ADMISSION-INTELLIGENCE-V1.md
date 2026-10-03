# ESTUDO · A FRONTEIRA ENTRE ADMISSION E INTELLIGENCE

> **Isto é uma fotografia de estudo, não uma nova autoridade.** As leis continuam
> na [`BIBLIA-CANONICA-DA-COLETA.md`](../../BIBLIA-CANONICA-DA-COLETA.md); o método
> continua no [`README.md`](../../README.md); a decisão durável está em
> [`docs/decisoes/DIARIO-DE-DECISOES.md`](../decisoes/DIARIO-DE-DECISOES.md).
> Nada aqui revoga nada.

A pergunta que abriu esta missão:

> **«O julgamento `(item, universo)` deve continuar na Admission, ou deve ser
> movido para Intelligence?»**

A missão anterior mediu que uma lista plana de palavras não consegue dizer se um
documento é "T2 — Clima e tempo": ela memoriza o publicador e não generaliza
(`GENERALIZACAO = 0/10`, ver [`MEDICAO-DA-REGRA-T2.md`](MEDICAO-DA-REGRA-T2.md)).
Desse fracasso nasceu uma dúvida **estrutural**, não um bug: se o mecanismo falha,
talvez a responsabilidade esteja na camada errada.

---

## 0 · UMA ARMADILHA DE VOCABULÁRIO, ANTES DE TUDO

A pergunta da missão usa a palavra **"julgamento"**. A Bíblia usa essa palavra
para outra coisa:

> **COL-LAW-005** — *«`COLETAR` adquire evidência. `ADMITIR` decide se a evidência
> entra num universo. `JULGAR` combina e interpreta depois.»*

Portanto a decisão `(item, universo)` **não é** "julgamento" no vocabulário desta
casa: é **ADMITIR**. `JULGAR` é o ato seguinte, e já pertence à Intelligence.

    A PERGUNTA, TRADUZIDA PARA A LÍNGUA DA CASA, É:
    «ADMITIR DEVE CONTINUAR A SER UM ATO SEPARADO DE JULGAR?»

Escrita assim, ela já tem lei. O que **não** tinha resposta era a segunda metade —
se o **mecanismo** com que ADMITIR faz o seu trabalho é suficiente.

---

## 1 · AS AUTORIDADES INTERNAS, CITADAS ANTES DE REINTERPRETADAS

```
WHO_OWNS_COLLECTION   «COLETAR adquire evidência.»                    COL-LAW-005
WHO_OWNS_ADMISSION    «ADMITIR decide se a evidência entra num
                       universo.»                                     COL-LAW-005
WHO_OWNS_JUDGMENT     «JULGAR combina e interpreta depois.»           COL-LAW-005
```

**COL-LAW-005** acrescenta, e é decisivo:

> *«Um coletor **NÃO DEVE** descartar evidência por opinião semântica — essa
> opinião pertence a outra etapa.»*
>
> *«O coletor traz; a porta decide, uma vez por par (item, universo).»*

**COL-LAW-042 · A LEI DA ADMISSÃO:**

> *«A admissão **DEVE** produzir decisão auditável, com no mínimo: `item/artifact
> id` · `universe` · `rule` · `rule_version` · `outcome` · `reason` · `evidence` ·
> `decided_at`. Uma decisão por **par (item, universo)**, nunca uma por item.
> **TODAS** as decisões são guardadas — não só as que passaram.»*
>
> *«A VERSÃO DA REGRA É O QUE PERMITE REPROCESSAR.»*

**COL-LAW-043 · `WHAT_READY_MUST_CONTAIN`** — o contrato de saída é fixo, e a
inteligência recebe *«isto e mais nada»*:

```
ESTADO · ITEM_ID · UNIVERSO · TEXTO · SOURCE_ID
SOURCE_LOCATION · FACT_LOCATION · FACT_TIME · CAPTURED_AT
CORRIDA · ADMITIDO_POR
```

Verificado no código: `admissao/admissao.py :: pronto_para_inteligencia` devolve
exatamente esses 11 campos, e `UNIVERSO` vem de `decisao.universo`.

E há uma autoridade a mais, fora da Bíblia, que decide esta pergunta sozinha.
[`AGENTS.md`](../../AGENTS.md), na lista de **«LEIS DO SINTONIA QUE O MAPA NÃO PODE
VIOLAR»**, escreve:

> *«consumidor não vira dono do gerador»*

A Intelligence é, por COL-LAW-043, **consumidora** do campo `UNIVERSO`. Movê-lo
para lá seria exatamente isso.

**COL-LAW-502** separa duas prontidões — `DOCUMENT READY` e `FACT READY` — e é a
prova de que esta casa **já** sabe pôr réguas diferentes em estágios diferentes
sem criar uma segunda porta.

---

## 2 · O ESTUDO EXTERNO

Seis sistemas, três famílias tecnológicas independentes. A pergunta posta a todos:
*onde termina a ingestão/validação e onde começa a classificação semântica?*

### A · Databricks / Microsoft — Medallion (lakehouse)

```
SYSTEM            Medallion architecture (Bronze / Silver / Gold)
OFFICIAL_SOURCE   https://learn.microsoft.com/en-us/azure/databricks/lakehouse/medallion
```

| | wording oficial |
|---|---|
| `WHAT_INGESTION_DOES` | *«Raw data ingestion»* · *«No data cleanup or validation is performed here»* · *«Contains and maintains the raw state of the data source in its original formats»* |
| `WHAT_VALIDATION_DOES` | Silver: *«Data cleaning and validation»* — schema enforcement, nulls, dedup, late-arriving data, type casting, joins |
| `WHERE_CLASSIFICATION_HAPPENS` | Gold: *«It contains semantically meaningful datasets that map to business functions and needs»* · *«Aligns with business logic and requirements»* |
| `WHERE_ENRICHMENT_HAPPENS` | Silver (normalização) e Gold (modelo de negócio e agregação) |
| `CAN_ONE_ITEM_HAVE_MULTIPLE_MEANINGS_OR_DESTINATIONS` | **SIM, explicitamente:** *«some customers create multiple gold layers to meet different business needs, such as HR, finance, and IT»* |
| `HOW_UNCERTAINTY_IS_HANDLED` | Silver *«quarantining invalid records»* — o duvidoso é posto de lado com registo, não descartado |
| `WHAT_IS_RELEVANT_TO_SINTONIA` | A separação é **por camada, não por opinião**: quem ingere não interpreta. E a multiplicidade de significados é resolvida com **vários Gold sobre um Silver**, nunca com um campo `tema` no Bronze |
| `WHAT_MUST_NOT_BE_COPIED` | A qualidade nominal (bronze/prata/ouro) como sinónimo de *confiança*. Aqui um documento pode ser impecável e continuar `NAO_SEI` |

### B · AWS — camadas do data lake

```
SYSTEM            AWS data lake layers (Raw / Stage / Analytics)
OFFICIAL_SOURCE   https://docs.aws.amazon.com/prescriptive-guidance/latest/
                  defining-bucket-names-data-lakes/data-layer-definitions.html
                  https://docs.aws.amazon.com/whitepapers/latest/building-data-lakes/
```

| | wording oficial |
|---|---|
| `WHAT_INGESTION_DOES` | *Raw*: *«Contains the raw, unprocessed data… you should keep the original file format and turn on versioning»*; o whitepaper chama-lhe *«the immutable copy of the data»* |
| `WHAT_VALIDATION_DOES` | *Stage*: *«An AWS Glue job reads the files from the raw layer and validates the data»*, e o metadado vai para o catálogo |
| `WHERE_CLASSIFICATION_HAPPENS` | Camada de processamento → *Analytics*: *«the aggregated data for your specific use cases»* |
| `WHERE_ENRICHMENT_HAPPENS` | *«creates datasets in the curated zone after cleaning, normalizing, standardizing, and enriching»* |
| `CAN_ONE_ITEM_HAVE_MULTIPLE_MEANINGS_OR_DESTINATIONS` | **SIM** — *«your specific use cases»*, plural, sobre um único cleaned |
| `HOW_UNCERTAINTY_IS_HANDLED` | Guardar tudo no cleaned *«provides the ability to replay downstream data processing in case of errors»* |
| `WHAT_IS_RELEVANT_TO_SINTONIA` | Reprocessar é um direito de arquitetura, não um favor. É a mesma razão pela qual a COL-LAW-042 guarda `rule_version` |
| `WHAT_MUST_NOT_BE_COPIED` | Raw como *«transient area»*. Nesta casa o RAW é permanente (COL-LAW-006) |

### C · OCCRP Aleph · FollowTheMoney (jornalismo investigativo)

```
SYSTEM            Aleph + FollowTheMoney
OFFICIAL_SOURCE   https://docs.aleph.occrp.org/developers/
                  https://followthemoney.tech/explorer/schemata/Document/
                  https://github.com/alephdata/aleph/pull/1818  (o modelo do xref)
```

| | |
|---|---|
| `WHAT_INGESTION_DOES` | `ingest-file` *«extracts data from numerous formats (Word, PDF, Email, ZIP archives)»* e normaliza para o modelo FtM |
| `WHAT_VALIDATION_DOES` | Conformidade ao schema FtM. `Document` carrega `processingStatus`, `processingAgent`, `processingError` — o **estado do processamento é um campo do documento**, exatamente como nesta casa |
| `WHERE_CLASSIFICATION_HAPPENS` | **Depois**, e noutro componente: extração de entidades e `xref` (cross-referencing) são etapas separadas da ingestão |
| `WHERE_ENRICHMENT_HAPPENS` | No grafo, por relações — nunca sobrescrevendo o documento |
| `CAN_ONE_ITEM_HAVE_MULTIPLE_MEANINGS_OR_DESTINATIONS` | **SIM.** O schema `Document` *«inherits properties from two parent schemata: `Thing` and `Analyzable`»*, e a hierarquia é multi-raiz: cada schema pode ter **vários** pais |
| `HOW_UNCERTAINTY_IS_HANDLED` | O `xref` produz candidatos com um campo **`doubt`** — *«the smaller the doubt value, the more confident the system is»* — e há uma **pairwise judgement API**: a máquina propõe, a pessoa confirma ou rejeita |
| `WHAT_IS_RELEVANT_TO_SINTONIA` | É o sistema mais próximo do nosso problema: documentos heterogéneos, procedência que importa, e **um resultado automático que não é tratado como verdade final** |
| `WHAT_MUST_NOT_BE_COPIED` | O grafo de entidades inteiro. Esta casa ainda não tem sequer a regra de um universo — importar uma ontologia agora seria construir o telhado |

### D · OpenCTI (inteligência de ameaças)

```
SYSTEM            OpenCTI
OFFICIAL_SOURCE   https://docs.opencti.io/latest/reference/data-processing/
                  https://docs.opencti.io/latest/usage/enrichment/
```

| | |
|---|---|
| `WHAT_INGESTION_DOES` | *External import connectors* trazem dados de fora |
| `WHAT_VALIDATION_DOES` | Deduplicação e *merging*, *«preserving relationship integrity»* |
| `WHERE_CLASSIFICATION_HAPPENS` | Tipagem e *marking* (TLP, autor) no momento da entrada; a **análise** vem de outro tipo de conector |
| `WHERE_ENRICHMENT_HAPPENS` | *Internal enrichment connectors*, **um tipo de conector à parte**, que corre *«when a new object is created in the platform or on the user request»* |
| `CAN_ONE_ITEM_HAVE_MULTIPLE_MEANINGS_OR_DESTINATIONS` | **SIM** — um mesmo *Observable* sustenta vários *Indicators*, e vive em contentores diferentes |
| `HOW_UNCERTAINTY_IS_HANDLED` | *Confidence levels* por utilizador e por objeto; **inference rules** desativáveis, e *«deactivating a rule removes all relationships it generated»* |
| `WHAT_IS_RELEVANT_TO_SINTONIA` | O derivado sabe que é derivado, e é **reversível**. É a `rule_version` da COL-LAW-042 levada ao fim: desligar a regra apaga o que ela concluiu |
| `WHAT_MUST_NOT_BE_COPIED` | O STIX inteiro e a inferência automática por omissão. *«they are not activated by default»* — e aqui também não deviam ser |

### E · Azure AI Document Intelligence

```
SYSTEM            Azure AI Document Intelligence
OFFICIAL_SOURCE   https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/overview
```

| | wording oficial |
|---|---|
| `WHAT_INGESTION_DOES` | *Read*: *«Extract printed and handwritten text»* · *Layout*: *«Extract text, tables, and document structure»* |
| `WHAT_VALIDATION_DOES` | Tipagem forte dos campos — *«Each field… carries a value type… that determines how the raw text is normalized»* |
| `WHERE_CLASSIFICATION_HAPPENS` | **Num modelo próprio, treinado, à parte:** *«Custom classifiers identify document types **before invoking an extraction model**»* |
| `WHERE_ENRICHMENT_HAPPENS` | Nos modelos de extração, depois de o tipo estar decidido |
| `CAN_ONE_ITEM_HAVE_MULTIPLE_MEANINGS_OR_DESTINATIONS` | Sim — *composed models* combinam vários modelos sobre o mesmo documento |
| `HOW_UNCERTAINTY_IS_HANDLED` | Confiança por campo; o desenho recomendado encaminha o baixo-confiança para revisão humana |
| `WHAT_IS_RELEVANT_TO_SINTONIA` | **É a resposta mais direta à pergunta desta missão.** "Que tipo de documento é este?" é tratado como um **problema de classificação com dono próprio**, separado de "o que está escrito nele" |
| `WHAT_MUST_NOT_BE_COPIED` | O serviço. E sobretudo: um classificador **exige corpus rotulado e avaliação honesta** — o T2 mostrou que 10 positivos de 3 publicadores não chegam |

### F · Google Document AI

```
SYSTEM            Google Cloud Document AI
OFFICIAL_SOURCE   https://docs.cloud.google.com/document-ai/docs/processors-list
```

| | |
|---|---|
| `WHAT_INGESTION_DOES` | *Enterprise Document OCR*, *Form Parser*, *Layout Parser* — *«creates context-aware chunks»* |
| `WHERE_CLASSIFICATION_HAPPENS` | Numa **categoria de processador separada**, «Classify documents»: *«Custom Classifier: Train a model to classify a document type from a set of classes»* |
| `CAN_ONE_ITEM_HAVE_MULTIPLE_MEANINGS_OR_DESTINATIONS` | O *Custom Splitter* parte um ficheiro *«into individual, classified documents»* — um ficheiro, vários documentos, várias classes |
| `WHAT_IS_RELEVANT_TO_SINTONIA` | Confirma o padrão de forma independente da Microsoft: **classificar é um componente, não uma condição dentro do leitor** |
| `WHAT_MUST_NOT_BE_COPIED` | A dependência de serviço externo pago para uma decisão que tem de ser auditável e reproduzível offline |

---

## 3 · O PADRÃO COMUM, E ONDE ELES DIVERGEM

**O que os seis fazem igual:**

1. **Ingestão não interpreta.** Bronze *«no data cleanup or validation»*; Raw
   *«the immutable copy»*; `ingest-file` normaliza formato, não significado.
2. **Validação é estrutural, não semântica.** Silver/Stage perguntam *«dá para
   ler, está completo, está conforme»* — nunca *«é sobre o quê»*.
3. **Classificação semântica é um componente com dono próprio.** Gold, Analytics,
   `xref`, enrichment connectors, Custom Classifier. **Nenhum deles a põe dentro
   do leitor.**
4. **Um item pode ter vários significados e vários destinos.** Vários Gold sobre
   um Silver; vários *use cases* sobre um cleaned; multi-herança no FtM; vários
   Indicators sobre um Observable.
5. **A incerteza tem forma própria e sobrevive.** `doubt`, confidence levels,
   quarentena, revisão humana. **Nenhum deles converte incerteza em "não".**

**Onde divergem:** no *quão cedo* o tipo é decidido. Document AI e Document
Intelligence classificam **antes** de extrair (para escolher o extrator);
Medallion e AWS classificam **depois** de validar (para servir o consumidor).
Aleph e OpenCTI fazem as duas: tipam à entrada (schema/TLP) e **reinterpretam
depois** (xref, inference).

    A DIVERGÊNCIA NÃO É SOBRE QUEM DECIDE. É SOBRE QUANDO.
    QUE SEJA UM COMPONENTE PRÓPRIO, NISSO OS SEIS CONCORDAM.

---

## 4 · A MATRIZ DE DECISÃO

| QUESTION | INTERNAL_LAW | EXTERNAL_PATTERN | CONFLICT? | VERDICT |
|---|---|---|---|---|
| Quem é dono da decisão `(item, universo)`? | COL-LAW-005: *«ADMITIR decide se a evidência entra num universo»*; COL-LAW-042: decisão por par, auditável | A decisão de tipo/destino é sempre um componente próprio, entre validação e consumo — nunca dentro do coletor nem dentro do consumidor | **NÃO** | **A Admission continua dona.** A lei interna e os seis sistemas dizem a mesma coisa |
| Isso pertence à Intelligence? | COL-LAW-043: a Intelligence recebe `UNIVERSO` **já decidido**, e *«isto e mais nada»*. AGENTS.md: *«consumidor não vira dono do gerador»* | Gold/Analytics **consomem** a classificação; não é o consumidor que a produz | **NÃO** | **NÃO se move.** Mover partiria o contrato de 11 campos, porque `UNIVERSO` é um deles |
| O mecanismo atual (lista plana de palavras) chega? | Nenhuma lei prescreve o mecanismo. COL-LAW-042 só exige regra, versão e prova | Todos usam modelo treinado e avaliado, ou regra estruturada, ou humano — **nenhum usa lista de palavras** | **NÃO** (a lei não é contrariada; está subespecificada) | **NÃO CHEGA.** Medido: `GENERALIZACAO = 0/10` |
| Um documento pode ser de dois universos? | COL-LAW-042: *«uma decisão por par (item, universo), nunca uma por item»* | FtM: multi-herança. Medallion: vários Gold. OpenCTI: vários Indicators | **NÃO** | **Já é permitido**, e está provado abaixo |
| A incerteza pode ficar por resolver? | COL-LAW-042 e os cinco resultados: `NAO_SEI` e `NAO_SE_APLICA` são respostas | `doubt`, confidence, quarentena, revisão humana | **NÃO** | Esta casa já está **à frente** de vários: o `NAO_SEI` é de primeira classe |

### `PADRÃO EXTERNO NÃO REVOGA LEI CANÔNICA EM SILÊNCIO`

Nenhum conflito apareceu. O padrão externo **confirma** COL-LAW-005, 042 e 043 e
não toca em nenhuma. Por isso:

```
ARCHITECTURAL_DECISION_REQUIRED = NO
BIBLE_CHANGE_REQUIRED           = NO
```

---

## 5 · MULTIPERTENÇA — PROVADO, NÃO SUPOSTO

> «Um documento ser T2 e T3 ao mesmo tempo exige nova arquitetura?»

```bash
py - <<'EOF'
import sys; sys.path.insert(0,'.')
import _gavetas, admissao as adm
item = {"id":"PROVA-MULTI","artifact_type":"RAW","url":"https://x.it/a",
        "source_id":"IT-T3-002","captured_at":"2026-09-03T00:00:00Z",
        "texto":"bollettino fitosanitario: la malattia del fungo e il decreto "
                "del ministero di autorizzazione"}
for u in ("T3","T4","T7"):
    d = adm.decidir(item, u, corrida="PROVA")
    print(f"({d.item}, {d.universo}) = {d.resultado}  ·  {d.motivo[:60]}")
EOF
```

Saída real, nesta árvore:

```
(PROVA-MULTI, T3) = SIM   ·  fala de fungo, malattia — que e do que «T3» trata
(PROVA-MULTI, T4) = SIM   ·  fala de ministero, decreto, autorizzazione — …
(PROVA-MULTI, T7) = NAO   ·  nao fala de «T7», e fala claramente de outro universo
```

Três decisões independentes para **um** item, cada uma com o seu motivo e a sua
`rule_version`. E não é só teoria: o livro real
(`data/samples/LIVRO-DE-DECISOES.json`, 813 decisões) já tem **44 itens com mais
de uma decisão**, e pelo menos um com decisões em `T4`, `T7` e `T9`.

```
MULTI_UNIVERSE_REQUIRES_ARCH_CHANGE = NO
```

**A ressalva honesta, porque sem ela isto seria meia verdade.** O *runtime* não
exercita isso: `orquestrador/orquestrador.py :: pela_porta(itens, universo,
run_id)` recebe **um** universo, o `alvo` do pedido. Portanto:

```
MODELO E LIVRO      suportam multipertença  ·  PROVADO
RUNTIME             pergunta um universo por corrida  ·  MEDIDO
```

A diferença entre os dois **não é arquitetural** — é a mesma corrida repetida com
outro alvo. É exatamente a distinção que esta missão foi obrigada a manter:
**dono não é implementação**.

---

## 6 · QUE TIPO DE PROBLEMA FICOU

Comparação **conceptual**. Nenhum classificador foi construído nesta missão.

| mecanismo | explicável | determinístico | depende da fonte | dá para testar | o que o T2 mostrou |
|---|---|---|---|---|---|
| lista plana de palavras | alta | total | não | fácil | **reprovado**: memoriza o publicador, `0/10` fora dele |
| regras estruturadas (grupos, contagem, negação) | alta | total | não | fácil | não testável hoje — a Admission pára na primeira palavra |
| auto-declaração do documento | **altíssima** | total | não | fácil | promissor: os títulos declaram-se («Bollettino Fitosanitario» vs «Meteo Veneto»). Mas o SIAS não tem prosa nenhuma |
| metadado da fonte/documento | alta | total | **total** | fácil | **reprovado por contraexemplo**: a ARPAV publica T2 **e** T3 |
| classificador multi-rótulo | baixa | sim (dado o modelo) | não | exige corpus e held-out | possível, e é o que a indústria faz — mas 10 positivos de 3 publicadores não treinam nada |
| classificador LLM/semântico | baixa | **não** | não | difícil | colide com a necessidade de `rule_version` reprocessável |
| híbrido (regra + abstenção + revisão) | média | parcial | parcial | médio | **é para onde o estudo aponta** — é o `doubt` do Aleph com o `NAO_SEI` desta casa |
| revisão humana / abstenção | total | n/a | não | n/a | **já existe**: `NAO_SEI` e `NAO_SE_APLICA` |

```
CURRENT_MECHANISM_FIT_FOR_PURPOSE = NO
```

**Porquê, em uma frase.** Uma lista plana casa subcadeias e devolve `SIM` na
primeira que encontra; não sabe distinguir *o assunto do documento* de *uma
palavra que lá aparece*, e a medição de T2 mostrou que é precisamente essa a
distinção que faz falta.

**O que isto NÃO autoriza.** Não autoriza trocar o mecanismo já. Trocá-lo exige
corpus rotulado com held-out honesto — e a missão de T2 provou que esta árvore
ainda não o tem.

---

## 7 · ACHADOS LATERAIS — afetam a decisão?

| achado | afeta a decisão arquitetural? |
|---|---|
| `lancio` casa dentro de `bilancio` (sem fronteira de palavra) | **Não.** É um defeito do mecanismo, e o mecanismo já está declarado insuficiente. Reforça, não altera |
| `territory` da fonte ≠ `universo` do documento | **Sim, e é o achado que mais pesa.** É o contraexemplo ARPAV, e é o que reprova o desenho "metadado da fonte" |
| fontes potencialmente multi-território | **Não.** A multipertença já é permitida pela COL-LAW-042 |
| ARIF ambíguo (meteorologia + fitossanidade num PDF) | **Não.** O `NAO_SEI` já é a resposta certa, e o modelo de par já a suporta |
| `README.md` item 4 aponta para `docs/08-decisoes/…`, que não existe (é `docs/decisoes/`) | **Não.** Registado e **não corrigido** — não era esta missão |

---

## 8 · O QUE FICA EM ABERTO

```
UNKNOWN_REMAINING
  · qual mecanismo substitui a lista plana — o estudo diz de que FAMÍLIA ele é
    (regra estruturada + abstenção, com revisão), não qual é
  · se existe corpus rotulado suficiente nesta árvore para treinar ou avaliar
    seja o que for. A medição de T2 sugere que NÃO
  · se «documento SOBRE X» merece lei própria, ou se é consequência de leis
    que já existem
```

Nenhuma destas se resolve navegando mais. Resolvem-se com material.
