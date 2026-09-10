# SINTONIA EAME — KNOW HOW · LOTE 09

> Aprendizados reutilizáveis do censo Collection no snapshot `572647dce8a38b8835aafa6f9e3e42d2652fbcd9`. Não altera a fotografia auditada e não substitui Bíblia, runtime, provas ou System Map.

## CHECKPOINT

```text
LOTE_09_CLOSED = YES
CARDS_AUDITED = 6/6
AUDITED_COLLECTION_NODES = 50 / 64
AUDITED_DECLARED = 49 / 54
AUDITED_SYNTHETIC = 1 / 10
REMAINING_DECLARED = 5
REMAINING_SYNTHETIC = 9
```

Cards:

```text
C-ESTRADA-PDF
C-LEITORES
C-IT-TEXTO-PESQUISAVEL
C-CORPUS
C-PALAVRAS
C-FRONTEIRA-TELEMETRIA
```

## LIÇÃO 1 — COMPONENTES PRÓXIMOS NO MAPA NÃO FORMAM NECESSARIAMENTE UMA PIPELINE

O lote mostrou que documento, leitores, texto pesquisável, corpus, semântica e telemetria não formam uma única esteira. Existem rotas desconectadas e condutores independentes.

Regra reutilizável:

> Nunca inferir pipeline por proximidade visual ou afinidade temática. Cada transição precisa de caller, contrato de dados e evidência de runtime próprios.

## LIÇÃO 2 — GOLDEN PATH NÃO É PRODUÇÃO

`C-ESTRADA-PDF` é um driver/reconciliador de corrida com observação real, mas sem caller de produção. Ele lê PDF já preservado, roda extração e Admission, mas não passa por Ingresso, não chega a STRUCTURED nem READY.

Regra:

> Golden path prova uma travessia específica; não promove essa travessia a caminho canônico de produção.

## LIÇÃO 3 — CAPACIDADE DE LEITURA PRECISA DE OWNER E INTERFACE COMUM

Foram encontrados quatro mecanismos independentes para abrir PDF: `pdftotext`, `pdftotext -layout`, parser zlib/regex e `pypdf`. Não existe owner da escolha nem contrato comum de saída.

Regra:

> Formato não define implementação canônica. Reader deve receber documento e devolver uma unidade comum; seleção de reader precisa ter owner explícito. Extração semântica não deve ficar escondida dentro de um reader.

## LIÇÃO 4 — LEITOR NÃO É EXTRATOR SEMÂNTICO

`ferramentas/italy_extract_fields.mjs` produz DOCUMENT_ID, datas, fenologia, capturas, nível, tendência, praga e substância ativa. Isso é STRUCTURED/semantic extraction, não simples leitura.

Regra:

> READ = obter conteúdo. TRANSFORM/EXTRACT = atribuir estrutura/significado. Misturar os dois cria autoridade invisível e dificulta portabilidade.

## LIÇÃO 5 — PASTA DE TEXTOS NÃO É STORE SÓ POR ESTAR NO MAPA

`C-IT-TEXTO-PESQUISAVEL` é um recorte de 20 `.txt`, sem writer, chave, contrato, índice ou owner de persistência. Apenas 6 têm elo local verificável com PDF; 8 são traduções PT sem pai declarado.

Regra:

> STORE exige unidade, identidade, writer/owner e contrato. Um glob de arquivos não vira store por declaração visual.

## LIÇÃO 6 — TRADUÇÃO É DERIVAÇÃO DE SEGUNDA ORDEM

Traduções `*_pt.txt` aparecem misturadas com texto extraído italiano, sem tradutor, parent id, parent sha ou language metadata.

Regra:

> EXTRACTION e TRANSLATION são derivações diferentes. Tradução precisa apontar para o derivado de origem e declarar língua de entrada/saída e executor.

## LIÇÃO 7 — CORPUS NÃO É UMA UNIDADE ÚNICA

`C-CORPUS` reúne pelo menos três unidades: obra publicada, pessoa e canal. Algumas saídas são acervo; outras são gates de identidade usados antes de coleta paga.

Regra:

> Antes de criar “um corpus”, declarar a unidade: WORK, PERSON, CHANNEL, DOCUMENT, TRANSCRIPT etc. Gate de identidade não deve ficar escondido num card de corpus.

## LIÇÃO 8 — CORPUS NÃO DEVE NASCER FORA DA ESPINHA SEM DECLARAR PROVENIÊNCIA

Os corpus científicos consomem diretamente OpenAlex/ORCID e gravam JSON no Git, sem SOURCE_ID/RAW/PARENT canônicos da Collection.

Regra:

> Fonte externa usada como corpus precisa declarar se é acquisition própria, external reference ou derivação da Collection. Ausência de RAW/parent não pode ser escondida por chamar o resultado de corpus.

## LIÇÃO 9 — VOCABULÁRIO E DECISÃO SEMÂNTICA NÃO SÃO O MESMO OWNER

`C-PALAVRAS` mistura listas de termos com matcher/classifier que decide CONTENT_TYPE, SPEECH_TYPE, relevância técnica, país do fato e plateia do canal.

Regra:

> Léxico é dado/policy. Classifier é decisão. Termos podem variar por país; o motor deveria tender a CORE. Não duplicar classificador inteiro quando só o léxico muda.

## LIÇÃO 10 — CONTENT TRIAGE JÁ EXISTE, MAS NÃO É CROSS-PLATFORM

Foi provado que `regras/sensor_medir.py` consome transcrições e classifica conteúdo pós-transcrição para YouTube. O GAP anterior fica mais preciso:

```text
POST_TRANSCRIPTION_TRIAGE_EXISTS = YES
PLATFORM_COVERAGE = YOUTUBE_ONLY
CROSS_PLATFORM_POST_TRANSCRIPTION_CONTENT_TRIAGE = NO
```

Regra:

> Não construir outro cérebro por plataforma. Extrair o motor comum e deixar plataforma/dataset como adaptadores/entrada.

## LIÇÃO 11 — SAÍDA SEM CONSUMIDOR É CONHECIMENTO PARADO

No lote foram encontradas cinco saídas sem consumidor conhecido: três de leitores e duas de corpus.

Regra:

> Para toda saída material, registrar produtor, unidade, store e consumidor. Sem consumidor, declarar DEAD_END/UNCONSUMED; não inferir valor por existir em disco.

## LIÇÃO 12 — DATA-DRIVEN DISPATCH ESCAPA DE SCANNER DE IMPORTS

`C-CORPUS` é executado pelo Orquestrador via uma receita que contém o caminho do executor como dado. O mapa leu a receita como consumidor e perdeu a aresta real Orquestrador → Corpus.

Regra:

> Scanner de runtime precisa entender despacho dirigido por registry/recipe/config, não apenas imports literais.

## LIÇÃO 13 — CAMINHO COMPUTADO ESCAPA DO MAPA

`golden_path_pdf.py` usa `with_suffix('.txt')` para ler textos; a aresta real para `C-IT-TEXTO-PESQUISAVEL` não aparece porque o caminho não existe como literal.

Regra:

> Ausência de literal não prova ausência de edge. Paths computados, registries e factories precisam de medição própria.

## LIÇÃO 14 — LINEAGE NÃO PODE SER FILENAME/PATH

A linhagem PDF → texto é parcialmente forte onde existem PARENT_ARTIFACT_ID/PARENT_SHA256; fica perdida nos `.txt` nus. O próprio código recusa “mesmo nome ao lado” como prova.

Regra:

> Path e filename são localização, não identidade canônica. Linhagem exige IDs/hashes/parent links explícitos.

## LIÇÃO 15 — LINHAGEM DE DECISÃO É UM ATIVO

Na rota de voz/ciência, itens classificados carregam a evidência textual exata que levou à decisão (`CONTENT_TYPE_EVIDENCE`).

Regra:

> Além de lineage de artefato, preservar lineage de decisão: input, regra/modelo/versão e evidência que sustentou o rótulo.

## LIÇÃO 16 — TELEMETRIA PODE TER BOM CONTRATO E COBERTURA RUIM

`C-FRONTEIRA-TELEMETRIA` é um componente limpo e CORE; o contrato distingue NOT_RUN, ERROR, REJECTED, REUSED, UNKNOWN e SUCCESS. Porém apenas 3 de 44 executores emitem e os seis cards deste lote têm cobertura zero.

Regra:

> CONTRACT_READY != INSTRUMENTED != OBSERVED. Medir e publicar os três estados separadamente.

## LIÇÃO 17 — TELEMETRIA DE ETAPA NÃO É LINEAGE DE ITEM

A unidade atual de telemetria é etapa/run, sem ITEM_ID/RAW_ID/DERIVED_ID completos. Ela reconcilia contagens, mas não segue o mesmo item ponta a ponta.

Regra:

> Observabilidade de fluxo e lineage por item são capacidades diferentes. Um não substitui o outro.

## LIÇÃO 18 — CARD STATUS NÃO PODE HERDAR PROVA DE UM ÚNICO ARQUIVO

`C-LEITORES` aparece PROVEN embora só parte dos arquivos tenha caller/runtime. Um card multi-responsabilidade pode ficar verde porque uma peça interna correu.

Regra:

> Evidência deve ser atribuída à responsabilidade/subcomponente e só depois agregada ao card. Um arquivo vivo não prova todos os arquivos/responsabilidades do card.

## LIÇÃO 19 — CENSO SEMÂNTICO PRECISA MEDIR O UNIVERSO, NÃO UMA LISTA FIXA

Foram encontrados nove conjuntos de léxico dentro de `C-CORPUS` fora do universo conhecido por `censo_semantico_it.py`.

Regra:

> Um censo que enumera manualmente os objetos que pretende censar pode fechar a conta sobre um universo incompleto. O universo precisa ser descoberto/validado independentemente.

## LIÇÃO 20 — PORTABILIDADE: MOTOR CORE, DADOS DE PAÍS COMO OVERLAY

O lote mostrou um desenho replicável para novos países:

```text
CORE
- reader interface
- orchestration/reconciliation
- corpus contracts
- identity proof mechanics
- lexical matcher/classifier engine
- telemetry contract + writer

COUNTRY OVERLAY
- termos
- recortes cultura × problema
- lugares/regiões
- regras locais de escopo
- fontes/adapters
```

Princípio:

> Novo país troca dados/adapters/policies locais; não copia motor, classifier, reader ou telemetria inteira.

## VEREDITOS PROVISÓRIOS DO LOTE 09

```text
C-ESTRADA-PDF                  KEEP
C-LEITORES                     SPLIT_CANDIDATE
C-IT-TEXTO-PESQUISAVEL        RENAME_CANDIDATE
C-CORPUS                       SPLIT_CANDIDATE
C-PALAVRAS                     RENAME_CANDIDATE + SPLIT_CANDIDATE
C-FRONTEIRA-TELEMETRIA         KEEP
```

## GAPS QUE FICAM ABERTOS

```text
- owner/interface canônico para leitura de documentos
- canonical searchable-text contract/store
- contrato de corpus por unidade
- cross-platform post-transcription triage
- consumer registry / detecção de dead ends
- semantic vocabulary census completo
- lineage item-level na telemetria
- dispatcher/data-driven edges no System Map
- computed-path edges no System Map
```

## PRÓXIMO PASSO

Fechar os 5 componentes declarados restantes no Lote 10; somente depois auditar os 9 nós sintéticos e iniciar consolidação/reforma da Collection.
