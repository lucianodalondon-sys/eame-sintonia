# PORTÕES DE COLETA — MISSÃO 10B-ES

**Fechar a porta antes de coletar mais.** Data: **2026-08-29** · HEAD inicial:
`3a2659c` · suíte inicial: **202/202**

> **Princípio:** antes de coletar mais, a coleta precisa saber provar qual execução produziu
> o registro, qual origem produziu o conteúdo, se é duplicata, que tipo de vídeo é, qual sua
> originalidade, onde está a evidência e qual parte não sabemos.

---

## A · O QUE CADA PORTÃO EXIGE, E COMO FOI MEDIDO

Todos os estados vêm de `scripts/portao.py`, que **deriva** cada um dos artefatos.
Nenhum foi digitado. `python3 scripts/portao.py --json` reproduz `PORTAO-10B-ES.json`.

| portão | estado | medida |
|---|---|---|
| `RUN_MANIFEST` | **PROVED** | 10 execuções; todo `RUN_ID` citado por registro publicado resolve; 0 órfãos |
| `PIPELINE_DEDUPE` | **PROVED** | RAW 252 = ÚNICOS 252 + DUPLICATAS 0, **e o dedupe é exercido** num caso conhecido |
| `VIDEO_TAXONOMY_APPLIED` | **PROVED** | 252/252 dentro do contrato de 13 tipos |
| `VIDEO_ORIGINALITY` | **PROVED** | 241 UNKNOWN · 9 SYNDICATED · 2 RESHARE — todos explícitos |
| `PAID_RAW_POLICY` | **PROVED** | 9 rotas pagas, 0 com bruto declarado ausente, pipeline lê o bruto |
| `COLLECTION_TIMESTAMPS` | **PROVED** | toda execução pela porta nova tem hora medida; as 8 antigas seguem sem hora **e sem fingir que têm** |

---

## B · AUDIT_TARGET_SHA — a regra que impede a recorrência

O defeito da auditoria anterior: ela leu um branch que continuava recebendo commits. Um
auditor afirmou que a regra não existia em `docs/regras/` e listou 4 arquivos onde havia 5 —
tinha lido antes do commit que a criou.

`scripts/auditoria.py` cria um **worktree `--detach`** num SHA fixo. O auditor lê o snapshot;
o branch pode receber commits sem contaminar nada.

**A auditoria é INVÁLIDA — não "com ressalva" — em quatro casos, todos testados:**

| caso | resultado |
|---|---|
| `AUDIT_TARGET_SHA` não definido antes | inválida |
| snapshot inexistente (leu árvore não congelada) | inválida |
| SHA declarado ≠ SHA real do snapshot | inválida |
| snapshot com alteração não commitada | inválida |

Registro obrigatório: `AUDIT_TARGET_SHA` · `AUDIT_STARTED_AT` · `AUDIT_FINISHED_AT` ·
`AUDITOR_VERSION` · `SCRIPT_VERSION`.

---

## C · RUN MANIFEST — o `RUN_ID` deixa de rotular e passa a resolver

Antes, `RUN_ID` agrupava registros entre si e não resolvia para nada fora do repositório.
Agora fecha a cadeia:

```
CONTENT → RUN_ID → RUN_MANIFEST → INPUT / ACTOR / DATASET / RAW
```

**22 campos por execução.** As 8 execuções passadas entraram com `NOT_PRESERVED` **honesto**
em 5 ou 6 campos cada — `ACTOR_VERSION`, `STARTED_AT`, `FINISHED_AT`, `DATASET_ID` e
`COST_USD` nunca foram capturados e não podem ser reconstruídos.

`NOT_PRESERVED` é **confissão**, não ausência de dado. É diferente de `NÃO SEI`, que é a
fonte não informar.

### O portão foi provado rodando, não afirmado

`scripts/coletor.py` é a porta única das rotas pagas: grava o **RAW antes de normalizar** e
captura da própria plataforma os cinco campos que faltavam. Quatro execuções de verificação
contra a API real.

**E o teste de portão achou dois defeitos meus:**

1. **Dataset vazio virava `NOT_PRESERVED`**, confundindo *"a rota devolveu nada"* com
   *"perdemos o bruto"*. Um array vazio **é** a evidência de que a rota não devolveu nada.
2. **Pior:** o ator devolveu `SUCCEEDED`, `exitCode` limpo e **zero itens**, com
   `statusMessage: "free user run limit reached"`. Uma **cota esgotada que se apresenta como
   sucesso** — exatamente *"nenhum resultado do Actor ≠ nenhum resultado na plataforma"*.
   `SUCCEEDED` com zero itens agora vira **`PARTIAL`** carregando a mensagem da plataforma.

---

## D · PIPELINE DE DEDUPE — a função deixa de ser opcional

A auditoria apontou: o dedupe existia como função testada e **nenhum caminho reprodutível a
invocava**. Um teste unitário da função nunca teria pego isso.

`voz.pipeline_video()` faz **RAW → normaliza → classifica → originalidade → dedupe → saída**,
com `RAW_COUNT`, `DUPLICATE_COUNT` e `UNIQUE_CONTENT_COUNT` sempre explícitos e a relação
duplicata→canônico preservada.

**Os 252 foram regerados pelo pipeline lendo o bruto preservado**, não o normalizado
anterior. A cadeia `RAW → NORMALIZED` é exercida, não afirmada.

O teste é **ponta a ponta** com fixture mínima onde cada linha exerce um caso: id repetido
colapsa · título igual em canal diferente **não** colapsa · sem texto vira `NÃO SEI` e não
`OTHER`.

> **`DUPLICATE_COUNT = 0` nesta camada é verdade e por isso mesmo não prova nada.** Um
> dedupe que não faz nada passaria igual. Por isso o portão **exerce** o dedupe num caso
> conhecido em vez de confiar num zero.

---

## E · TAXONOMIA — 252 de 252

**A primeira versão jogou 169 em `OTHER`** porque `programa` estava no vocabulário de MEDIA
e empatava com CONFERENCE em *"programa de exposiciones científicas"*. Empate virava `OTHER`,
o que **escondia** informação em vez de ordená-la.

Corrigido o vocabulário e trocado o empate silencioso por **precedência declarada**: o
primário sai de uma lista publicada e os demais tipos ficam visíveis em `CONTENT_TYPE_ALL`.
40 vídeos declaram mais de um tipo — a apresentação de um investigador **dentro** de um
congresso é as duas coisas.

| tipo | n |
|---|---:|
| OTHER | 137 |
| CONFERENCE | 46 |
| TECHNICAL_WEBINAR | 20 |
| MEDIA | 15 |
| RESEARCH_TALK | 10 |
| PROMOTIONAL | 10 |
| PRODUCER_VOICE | 8 |
| FIELD_DAY · FIELD_OBSERVATION · COOPERATIVE_CONTENT | 2 cada |

**`OTHER` em 54% não foi maquiado, e nenhum tipo novo foi criado.** São sobretudo vídeos de
produtor explicando manejo — *"Cómo tratar la tuberculosis del olivo"*, *"El cobre en la
prevención del repilo"* — e a taxonomia de 13 tipos não tem destino nomeado para
**explicador de manejo**. Criar um tipo resolveria o número, não a pergunta.

**E 116 desses 137 vêm de canais com papel `NOT_DECLARED`:** a lacuna de taxonomia e a de
identidade são, em grande parte, a mesma população.

`NÃO SEI` continua diferente de `OTHER`: o primeiro é falta de texto, o segundo é texto sem
destino. Nenhum vídeo ficou em `NÃO SEI` — todos os 252 têm título.

---

## F · ORIGINALIDADE — e por que nenhum é `ORIGINAL`

| estado | n |
|---|---:|
| UNKNOWN | 241 |
| SYNDICATED | 9 |
| RESHARE | 2 |

`RESHARE` exige marca textual de republicação. `SYNDICATED` exige o mesmo título em canais
**diferentes**. `ORIGINAL` exigiria prova de autoria que a rota não dá.

**Estar no canal da própria empresa não prova originalidade.** Marcar 241 vídeos como
`ORIGINAL` por ausência de prova de republicação inverteria o ônus: ausência de evidência não
é evidência. `UNKNOWN` é o estado correto, e está **explícito em todos** — nenhuma ausência
silenciosa.

---

## G · RAW EVIDENCE

**8,8 MB de resposta crua preservados em 2,1 MB**, em `data/samples/raw-paid/`.

Para execuções passadas cujo bruto genuinamente não existe: `NOT_PRESERVED`. **Nada foi
reconstruído e chamado de original.**

Para toda rota nova: o `coletor` grava o RAW **antes** da normalização. A cadeia é
`RAW → NORMALIZED → ANALYTICAL`, e o RAW nunca é substituído.

A rota gratuita (OpenAlex, `ES-T5-002`) entra como `NOT_APPLICABLE` — é replicável, o bruto é
cache (D-003), e fingir que foi versionada seria falso.

---

## H · TIMESTAMPS

A hora em que o coletor **gravou** a saída é medida real, mas **não** é a hora da execução.
Vive em `OUTPUT_WRITTEN_AT` e nunca é promovida a `STARTED_AT`.

**Consequência aceita:** as 8 execuções passadas continuam **não** sustentando afirmação de
ordem. `pv.ordem()` devolve `NAO_DIZIVEL` para elas, e há teste que fixa isso.

`X BEFORE Y` só é dizível quando as duas execuções têm hora medida pela plataforma.
**Horário de commit do git não mede ordem de coleta** — mede ordem de escrita.

---

## I · `RESEARCHER_PUBLIC_VOICE_QUEUE_ES` — 20

Critérios, todos derivados do corpus: relevância CROP×ISSUE na âncora · atividade em 2023+ ·
instituição declarada · ORCID presente · **não conflacionado** (teto de organizações
derivado da mediana do quadro, não escolhido a dedo).

**Qual critério realmente filtra:** apenas **13 dos 152** foram recusados, os 13 por
recência. Os outros não peneiraram nada — o corpus já nasceu de consultas de olivar. Eles são
**guarda, não peneira**: o de conflação existe porque foi por ele que a auditoria achou o id
do OpenAlex com 58 organizações.

`PUBLIC_LINKEDIN_STATUS` e `PUBLIC_YOUTUBE_STATUS` = `NOT_TESTED` em todos os 20.
**A missão pediu a fila, não a coleta.**

> **Candidato de cruzamento:** Carlos Agustí-Brisach está nesta fila **e** na camada LinkedIn
> como `RESEARCHER` declarado em Córdoba. Continua **candidato**: o casamento é por nome, e
> nome não decide identidade.

## J · `PUBLIC_TECHNICAL_VOICE_QUEUE_ES` — 20

Papel verificável em campo estruturado declarado. **Alcance não entra em nenhum critério** —
`INFLUENCER = AUTHORITY` não existe no modelo, e ordenar por seguidores o reintroduziria pela
porta dos fundos.

**A cota não foi completada artificialmente:** há 67 elegíveis e a fila de 20 é um recorte por
prioridade. Os 47 restantes continuam disponíveis.

**Viés declarado:** 13 dos 20 vieram da rota de cargo, que pediu Andaluzia em parte das
consultas. A concentração andaluza mede o desenho da consulta, não o território.

---

## K · O QUE DOS 47 CONTINUA ABERTO

Fechados nesta missão: **§5** taxonomia aplicada · **§10** originalidade · **§11** dedupe no
pipeline · **§14** `RUN_ID` que resolve e RAW das rotas pagas.

Seguem abertos, com estado explícito:

| item | por quê continua aberto |
|---|---|
| §6 as 152 fichas sem busca pública tentada | a fila de 20 é o primeiro passo; 132 seguem `NOT_TESTED` |
| §2 LinkedIn Video e Instagram Reels | fora do escopo desta missão por decisão do dono |
| §7 relatório técnico, projeto, publicação institucional, extensão | quatro tipos sem fonte |
| §19 vídeo × concorrente | o cruzamento existe só na camada LinkedIn |
| §17 crosswalk ciência↔voz | exige identificador declarado, não algoritmo de similaridade |
| §9 `ORGANIZATION_ID` / `SAME_AS` entre origens | showcase e perfil da mesma empresa contam como origens independentes |

---

## M · VERIFICAÇÃO ADVERSARIAL — MISSÃO 10C

Os seis portões estavam `PROVED` **por auto-avaliação**. A verificação de terceiro lançada
pela conta anterior contra `a79f434` nunca retornou. A MISSÃO 10C a refez, com uma regra:
**não perguntar se o portão passa — tentar provar que ele NÃO funciona.**

> Para cada portão: **qual é a menor situação em que ele diria `PROVED` com a propriedade
> real quebrada?**

**Alvo congelado:** `0eb9b74195f43439cd8686ede18da5ea35f1b8dd`, worktree `--detach`.

### Resultado da primeira passagem: SEIS DOS SETE FORAM REFUTADOS

| portão | contraexemplo construído e rodado |
|---|---|
| **P1** | `RUN_ID` repetido no manifesto: `carregar()` indexa por id e o segundo **sobrescrevia** o primeiro. 11 execuções na lista, 10 carregadas, **uma execução inteira sumindo em silêncio**. E o portão lia **3** artefatos escolhidos a dedo quando **6** publicam `RUN_ID` |
| **P2** | três vídeos **distintos** sem `id` viravam **um**. `EXTERNAL_ID = NÃO SEI` era usado como identidade, todos colapsavam na mesma chave, `RAW 3 = ÚNICOS 1 + DUPLICATAS 2` **fechava a aritmética** e o portão dizia `PROVED` enquanto dois vídeos reais eram contados como duplicata de um registro sem identidade |
| **P3** | classificação silenciosa falsa continua possível: *"El repilo del olivo **en acción**"* → `PRODUCT_DEMO`; *"**Curso** natural del agua"* → `TECHNICAL_WEBINAR`; *"La **clausura** del riego"* → `CONFERENCE`. E os 252 marcados **todos** como `CONFERENCE` passavam |
| **P4** | `ORIGINAL` escrito à mão com evidência *"está no canal da própria empresa"* — a inferência que a lei **proíbe** — era aceito. `ORIGINALITY_EVIDENCE = "NÃO SEI"` contava **como evidência**. E a `MEDIDA` vinha do bloco **declarado** no arquivo: os 252 viravam `ORIGINAL` e o portão seguia imprimindo `{UNKNOWN: 241}` |
| **P5** | o bruto foi **trocado** por outro conteúdo e nada pegou: o portão conferia **existência**, nunca **integridade**, embora o SHA-256 estivesse no relógio de dados. E *"o pipeline lê o bruto"* era `'raw-paid' in ENTRADA` — bastava a **string**, o arquivo podia não existir |
| **P6** | comparação de **string** decidia ordem temporal. `09:00+02:00` (07:00 UTC) contra `08:00Z`: a verdade é `BEFORE`, o sistema respondia **`AFTER`**. O repositório **já mistura os dois formatos**. E a guarda era uma lista de 4 valores proibidos: `STARTED_AT = "desconhecido"` sustentava um `BEFORE` |
| **P0** | sobreviveu aos quatro modos de invalidação. **Limite encontrado:** `validar()` aceitava o **branch vivo** como snapshot — SHA certo e limpo *no momento da checagem*, que só ocorre no fim |

### O que foi corrigido, e o que continua declarado como limite

Cada contraexemplo virou **teste de regressão** em `tests/test_portao.py`.

- **P1** — `pv.runs_duplicados()` denuncia id repetido; o portão **varre** todos os artefatos.
- **P2** — `NÃO SEI` deixa de ser identidade. Sem `EXTERNAL_ID` o registro **nunca colapsa**,
  e `WITHOUT_STRUCTURAL_ID_COUNT` é publicado. **Ausência de identidade não é identidade
  compartilhada.**
- **P3** — distribuição **derivada** dos registros, coerência `CONTENT_TYPE` ⊂
  `CONTENT_TYPE_ALL`, e evidência obrigatória. **LIMITE DECLARADO E NÃO FECHADO:** o
  classificador é lexical; polissemia produz falso positivo e **nenhum portão detecta isso**.
  Por isso todo registro carrega `CONTENT_TYPE_EVIDENCE` — a verificação de verdade é humana.
  Apertar os padrões foi **medido e recusado**: os seis vídeos reais com "curso" são cursos
  de verdade, e a correção quebraria classificação certa para consertar caso sintético.
- **P4** — `ORIGINAL` é **barrado** no artefato publicado; `NÃO SEI` não é evidência;
  distribuição declarada tem de bater com a derivada.
- **P5** — SHA-256 de todo `PRODUCTION_RAW` conferido contra o relógio; `PIPELINE.ENTRADA`
  tem de ser arquivo **existente** dentro de `raw-paid/`.
- **P6** — ordem por **instante com fuso**, nunca string. O que não converte em instante
  falha fechado. Execução legada continua `NAO_DIZIVEL`.
- **P0** — `validar()` exige worktree **destacado**. `auditoria.py/1.1.0`.

> **A lição que atravessa os seis:** cinco dos seis portões verificavam **FORMA** e eram lidos
> como se verificassem **VERDADE**. Contagem que fecha, campo preenchido, valor dentro do
> contrato e string presente são todos satisfeitos por dado falso. Um portão só vale pela
> propriedade que ele **exerce** — e o único que já exercia (o dedupe, que colapsa um caso
> conhecido em vez de confiar num zero) foi também o único cujo defeito estava fora dele,
> na função que ele chamava.

## L · O QUE FOI DELIBERADAMENTE NÃO FEITO

- **Não ataquei os 47.** A missão pediu só o que corrompe ou torna irreprodutível a próxima
  coleta.
- **Não coletei as 152 buscas.** Volume sem critério é o erro já medido duas vezes aqui.
- **Não criei tipo novo de vídeo** para reduzir `OTHER`. Resolveria o número, não a pergunta.
- **Não reconstruí RAW histórico.** Onde não existe, `NOT_PRESERVED`.
- **Não abri França, Itália, portal, design nem plataforma nova.**
- **Não comecei a nova coleta** — o portão manda parar.
