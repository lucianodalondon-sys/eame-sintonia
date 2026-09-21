# RELATÓRIO — C-MICRO-COLLECTION CANÓNICA V1

```
CANONICAL_MICRO_COLLECTION_RESULT = PARTIAL
```

Base: `micro-collection-v1 @ 4fdabf82`. Ramo: `canonical-micro-v1`.
Data: 2026-09-21. Egresso: **IT** em todas as idas à rede.

**A aquisição funcionou e a cadeia não fechou.** 85 documentos italianos reais
foram colhidos, preservados e conferidos byte a byte. **Zero** chegou à Sala, e
a causa está nomeada: a porta canónica só se alcança por *receita*, e os alvos
T5, T7 e T10 não têm nenhuma. Escrever essa receita é o cutover que o HARD STOP
proíbe — fica como a única coisa que falta, e é decisão do dono.

---

## POLÍTICA DE MODELO

```
REQUESTED_MODEL           = claude-opus-5
ACTUAL_LLM_MODEL          = claude-opus-5
MODEL_SELECTION_SUPPORTED = NÃO MEDIDO POR MIM
FABLE_USED                = NO
```

**Ressalva.** `ACTUAL_LLM_MODEL` é o que o ambiente **me declara**, não uma
medição independente. Não tenho chamada que devolva a identidade do modelo a
correr; se o ambiente mentisse, eu repetiria a mentira. É declaração, não prova.

Nenhum LLM foi chamado para contar JSON, comparar hashes, correr testes ou
aplicar regra determinística. Isso foi tudo código, e o código está commitado.

---

## A DIREÇÃO DA INTEGRAÇÃO — CUMPRIDA, E CONFIRMADA POR MEDIÇÃO

```
git merge aquisicao-detalhe-v1        NUNCA EXECUTADO
enxertos ficheiro a ficheiro          4
```

O aviso do briefing confirmou-se em números, no momento em que fui verificar:

| ficheiro | trazê-lo inteiro custaria |
|---|---|
| `coleta/italy_executor.py` | **−52 linhas** — é `admissao_do_curator`, o portão |
| `coleta/italy_pilot_collect.mjs` | **−234 linhas** |
| `regras/motor_de_rota.mjs` | **−42 linhas** |
| `curadoria/italy_contracts_curator.json` | **−527 linhas** (a foto de lá é mais velha) |

Nenhum deles veio inteiro. Os quatro enxertos foram blocos, à mão:

1. `regras/italy_contracts_onboarded.json` — ficheiro novo, 173 fontes, 418 KB
2. o **bloco do laço** de `regras/italy_contracts.mjs` — +130 linhas
3. `FONTES_PERCORRIVEIS` em `coleta/italy_pilot_collect.mjs`
4. `MATCH:"URL"` + `CONTENT_CAPTURE` em `regras/motor_de_rota.mjs`

### O enxerto a mais que apanhei a tempo

Trouxe primeiro o `.mjs` **inteiro**. O diff é textualmente aditivo — 330
inserções, **zero remoções** — e mesmo assim **não é aditivo no comportamento**.
Ele passava também 8 blocos `ACQUISITION` escritos à mão para contratos antigos,
e o despachante de alvos diz:

```js
if (c && c.ACQUISITION) return await alvosDoContrato(...);   // motor declarativo
switch (sourceId) { ... }                                    // os 7 case medidos à mão
```

Dar `ACQUISITION` a esses contratos fá-los **saltar de caminho, calados**.
Medido: `IT-T2-002` (ARPAV) passava de **4 alvos para 29**, e
`test_alvo_estruturado_resolvido` ia de 1 vermelho para 7. O próprio coletor
escreve a invariante que eu estava a quebrar — *«os sete `case` não se tocam, e
por isso nenhuma fonte que já funcionava muda de comportamento»*.

> **Um diff sem remoções ainda pode apagar comportamento.**

Enxertou-se só o laço. **Dos 7 `case`, 0 mudaram de caminho.**

---

## F1 — A PONTE

```
CONTRATOS_ANTES = 14   →   CONTRATOS_DEPOIS = 186
dos 14 originais, em falta: 0
ONBOARDED_IDS = 173        COM BLOCO EXECUTÁVEL = 182 de 186
o motor DESTA linha aceita os 182: 0 recusados
IT-T5-041 continua sem contrato — ramo de índice, declarado, não forçado
PONTE_MATERIALIZADA = EXISTE      PONTE_EM_RUNTIME = NÃO EXISTE
```

A ponte **não lê** o ficheiro da curadoria em runtime, e isso é deliberado e
testado. O gerador automático fica como **dívida declarada**, não construída.

### As 17 provas, e o cone de dependências que o briefing não previu

Vieram, e correm: **18 corridas** (uma prova foi partida em duas), **14 verdes**,
**4 SKIP com a razão medida escrita no próprio skip**. Nenhuma vermelha.

Os SKIP existem porque três artefactos vivem só na outra linha, e trazê-los era
regressão ou cutover: as 18 pastas de evidência promovida (0 de 18 aqui), o
bloco `ESTADO_04A` do Atlas (0 de 84 fichas), e — até eu o enxertar —
`conferirIdentidade`.

> **SKIP com razão nomeada é a ausência dita em voz alta.**
> Um `assert` apagado seria a mesma ausência dita em silêncio.

E funcionou como prometido: ao enxertar `conferirIdentidade`, a prova que
esperava por ele **destravou-se sozinha e passou**. SKIP 5 → 4.

### Duas leis em conflito, resolvido por escrito

A prova de lá exige `curadoria/` com **zero** código. Aqui `curadoria/` é onde
vive o portão de admissão. Cumpri-la apagava o portão — fica **revogada nesta
linha, com o motivo**. O que **não** se revoga é a razão que lhe deu origem: um
segundo leitor de robots. Essa continua medida, e está **vermelha desde antes
desta missão**:

```
RobotFileParser fora de tests/:
  coleta/scrap_http.py       ← o dono legítimo
  curadoria/descobrir.py     ← 2.º leitor
  curadoria/gate_de_rota.py  ← 3.º leitor
```

Dívida herdada, **não curada aqui**. A prova nova impede que **cresça**.

### As duas fotografias do curator

81 fontes aqui, 77 lá. Nas 9 das 18 que o PASSO-2 tocou, a foto **desta** linha
já carrega o `DEPOIS` (9/9 medido); a de lá ficou no `ANTES`. As outras 9 são
iguais byte a byte. A prova passa a aceitar os **dois estados declarados** e
continua a reprovar um terceiro por registar — não foi afrouxada; caiu a
suposição de que só existe uma fotografia.

---

## F2 — PRÉ-VOO SEM REDE

```
ELIGIBLE_INPUT            = 8       (pela REGRA, no instante do pedido)
SOURCE_ID_RESOLVED        = 7/8     (IT-T5-041 fora, declarado)
CONTRACT_RESOLVED         = 7/8
ROUTE_RESOLVED            = 7/8
CANONICAL_RUNNER_SELECTED = YES     coleta/italy_executor.py
COLLECTION_GATE_USED      = YES     por subprocess, antes de cada lançamento
HARDCODED_SOURCE_LIST_USED = NO
PRODUCTION_OPS_COPY_USED   = NO     C:\eame-sintonia-ops\ nunca tocado
```

O portão continua a morder com 186 contratos em vez de 14:

```
87 READY avaliadas = 77 READY_LEGACY fora + 2 HUMAN_REVIEW fora + 8 dentro
LEGACY_ACEITE = 0
```

*(O painel diz `HUMAN_REVIEW_REQUIRED = 3`; só 2 são recusadas por esse motivo —
a terceira é também `READY_LEGACY` e cai no primeiro. Os dois números são
verdadeiros, com denominadores diferentes.)*

### O ponto que decidia a missão

Antes da ponte, **das 8 elegíveis, 0 tinham contrato**. Depois da ponte tinham 7
— e a CLI continuava a recusá-las:

```
node coleta/italy_pilot_collect.mjs --fonte=IT-T7-033
→ FONTE_DESCONHECIDA: este coletor percorre IT-T3-005, IT-T2-002, …
```

`PILOT_SOURCES` era uma lista **digitada** de 7 fontes *outras*. A ponte chegava
ao motor e morria na CLI. A capacidade passa a ler-se do contrato.

**Defeito apanhado na cópia.** O bloco de origem deriva a capacidade só de quem
declara `ACQUISITION`. Mas o despachante tem **duas** portas. Naquele ramo os 7
`case` já tinham `ACQUISITION`, por isso a omissão não aparecia; aqui a cópia
literal media **0 de 7** fontes do piloto percorríveis — a CLI passaria a
recusar tudo o que já funcionava. Fica a **união**.

```
FONTES_PERCORRIVEIS = 181   (174 com ACQUISITION + as 7 do switch)
as 7 do piloto      = 7/7          das 8 elegíveis = 7/8
```

**CAPACIDADE NÃO É APROVAÇÃO.** Das 186 que esta lista percorre, o portão
**recusa 178**.

---

## F3 — EGRESSO

Três medidores independentes, antes de cada ida:

```
ipinfo.io     146.70.182.38  IT  Milan  AS9009 M247 Europe SRL
api.ipify.org 146.70.182.38
ifconfig.co   146.70.182.38  IT  Milan  AS9009
EGRESSO = IT
```

Reconfirmado imediatamente antes de RUN1, RUN1B, RUN1C e RUN2. Nunca variou.

---

## F4 — AS IDAS À REDE

**Quatro passagens, e duas eram para terem sido uma.** As duas primeiras não
trouxeram documento nenhum, por defeitos **nossos** — e cada uma deixou o livro
a acusar a fonte de algo que a fonte não fez. Declaro-o em voz alta porque o
tecto autorizado eram duas corridas.

```
RUN1    19 pedidos   6 observações   DISCOVERY_FAILED 6/6   0 bytes
RUN1B   98 pedidos  85 observações   IDENTITY_FAILED 85/85  0 bytes
RUN1C   98 pedidos  85 observações   ← a colheita a sério
RUN2    98 pedidos  85 observações   ← incrementalidade
TOTAL  313 pedidos          PAID_USD = 0.00
```

### RUN1 — o motor acusava a fonte

Seis de seis: `EMPTY_LIST — o índice não anuncia nenhum alvo que case com
LINK_PATTERN`. Era falso. Os índices anunciavam.

A tabela declara `MATCH: "URL"` e traz padrões que são endereços inteiros
**ancorados** (`^https?://…$`). O motor **não lia `MATCH`** — zero ocorrências da
palavra no ficheiro — e corria o padrão contra o texto da página toda. Um
`^…$` sem flag `m` só casa se o documento inteiro for aquele endereço.

E `conferirAquisicao` dava verde às 182 linhas, porque também nunca olhou para
`MATCH`.

> **Aceitar um campo sem o implementar é pior que recusá-lo:**
> a conferência dá verde e a corrida acusa a fonte.

### RUN1B — a identidade morria antes de descarregar

Já com a descoberta certa, vieram 85 endereços de artigos **reais**. As 85 deram
`IDENTITY_FAILED`, com zero bytes. O motor começava por
`if (spec.STRATEGY !== "FILENAME_CAPTURE") return null;` e devolvia `null`
**calado** para as 174 fontes com bloco de identidade — e os contratos onboarded
declaram `CONTENT_CAPTURE`.

> **`null` não diz porquê.**

### RUN1C — a colheita

```
ELIGIBLE_INPUT 8 · com contrato 7 · visitadas 6 · IT-T7-033 parada no robots
85 observações   79 NEW_DOCUMENT   6 SEMANTIC_ID_CHANGED_SAME_BYTES
85 ficheiros no armazém · 7 987 426 bytes (7,99 MB)
85 sha256 RECALCULADOS a partir do disco  →  85 batem, 0 não batem
0 observações com menos de 2 KB (nenhuma casca)
RAW_PRESERVED_BEFORE_PARSE = True em 85/85
```

Por observação, os campos que o briefing pede:

| campo | estado |
|---|---|
| `SOURCE_ID` | presente, 85/85 |
| `DETAIL_URL` | presente, 85/85 |
| `SHA256` | presente e **reconferido do disco**, 85/85 |
| `STORAGE_PATH` | presente e **o ficheiro existe**, 85/85 |
| `BYTES` | presente, 85/85 |
| `ROBOTS_RESULT` | presente, por visita |
| `OBSERVATION_ID` | **AUSENTE** — nasce na porta, que não correu |
| `RAW_ASSET_ID` | **AUSENTE** — nasce na porta, que não correu |
| `HTTP_STATUS` | **AUSENTE** — o livro guarda o *resultado*, não o código |

Os três ausentes **não foram preenchidos**. Um 200 que ninguém mediu não entra
no relatório, e há uma prova de red team que mata quem o puser lá.

Matéria real, amostra verificada (Consorzio Tutela Aceto Balsamico di Modena,
5 486 caracteres de texto):

> *«Aceto Balsamico di Modena IGP, dal piatto al bicchiere … News Home / News /
> … Storia ABM Territorio Come si produce Autenticità Caratteristiche
> organolettiche Conservazione Visite guidate alle acetaie …»*

---

## F5 — RAW → DERIVED → ADMISSION → SALA

Cada etapa medida e **separada**. Nenhuma foi dada por feita por causa da
anterior.

```
RAW        85 ficheiros preservados, sha256 conferido do disco — em
           data/collection-store/italy/, FORA da tabela raw_asset
DERIVED    NÃO EXECUTADO
ADMISSION  a admissão da FONTE correu (o portão, 8 de 87);
           a admissão do ITEM NÃO EXECUTADA
SALA       BEFORE 46 · AFTER 46 · DELTA 0
```

Acervo canónico (`127.0.0.1:54330/sala_italia`), antes e depois:

```
raw_asset        1072 → 1072        collection_run   369 → 369
storage_object    938 →  938        derived_artifact 758 → 758
sala_de_espera     46 →   46
linhas com SOURCE_ID nosso na Sala: 0
INSERÇÃO_MANUAL = 0 · BYPASS_DA_ADMISSAO = 0
```

### A causa, nomeada

A porta canónica é `orquestrador.correr(...)`, e só se alcança por **receita**.
`pedido/receitas.py` tem **T2, T3, T4, T6 e T9**. As 7 elegíveis são **T5, T7 e
T10**. Medido em runtime:

```
resolver(Pedido(alvo="T7")).da_para_correr = False
correr(..., so_a_porta=True)  →  STATUS = SEM_CAMINHO
```

**Não escrevi receita nenhuma.** Uma receita declara rota operacional e
`filtros_por_omissao` — que fonte um pedido T7 sem filtros vai colher. Isso é
política, e é o cutover que o HARD STOP proíbe.

> **COLHIDO NÃO É ADMITIDO.** 85 documentos estão preservados com sha256
> conferido, e nenhum entrou no acervo. As duas frases são verdadeiras.

---

## F6 — TEMPO, LUGAR, CULTURA

```
FACT_TIME_PROVEN     = 0        FACT_TIME_UNKNOWN     = 85
FACT_LOCATION_PROVEN = 0        FACT_LOCATION_UNKNOWN = 85
CROP_PROVEN          = 0        CROP_UNKNOWN          = 85
```

`FACT_TIME` sai `UNKNOWN` em 85 de 85, **e continua UNKNOWN mesmo quando o
endereço traz um ano lá dentro** — há prova própria disso, e um mutante de red
team que tenta o fallback e morre.

`FACT_LOCATION` e `CROP` **não existem como campo** no livro (0 de 445 linhas).
Não é omissão: é que a cadeia parou antes do `DERIVED`, que é quem os
preencheria. Nada foi inventado para melhorar completude.

`PUBLICATION_TIME ≠ FACT_TIME` · `SOURCE_LOCATION ≠ FACT_LOCATION` — as duas
regras existem em prosa nos 174 contratos, e **não há código nesta linha que as
execute**. Está dito em F-RT como `SEM_GUARDA`.

---

## F7 — A SEGUNDA CORRIDA

```
NEW_OBSERVATIONS        85      REUSED_STORAGE_OBJECTS   2
NEW_CONTENT             83      NEW_STORAGE_OBJECTS     83
REUSED_CONTENT           2      REFETCHED               85  (7,99 MB)
UNCHANGED                2      UNNECESSARY_REFETCHES    2
documentos NOVOS         0      ← a identidade é estável
DOCUMENT_CHANGED_IN_PLACE 83 · SEEN_AGAIN 2
```

A identidade está **certa**: 85 documentos, zero documentos novos. Mas 83 de 85
gravaram bytes novos em ~9 minutos. Fui ver o que mudou, sem rede:

```
374 linhas diferentes em 86 441  =  0,43 %
```

E **todas** são rasto de máquina:

```
-<meta property="article:modified_time" content="2026-09-21T19:26:10+00:00" />
+<meta property="article:modified_time" content="2026-09-21T19:34:54+00:00" />
```

19:26 é a hora da RUN1C. 19:34 é a hora da RUN2. **O site está a carimbar a hora
da nossa visita.** O resto são tokens CSRF, `client_id` de plugin WordPress, e
ids de DOM gerados por render (`tdi_#`, `pum-#`, `view-dom-id-#`).

**Zero linhas de texto editorial mudaram.**

> **`DOCUMENT_CHANGED_IN_PLACE` está a ser disparado pela nossa própria pegada.**
> O livro diz que o documento mudou, e o documento não mudou.

**DESPERDÍCIO.** A 7,86 MB por corrida, uma corrida diária sobre estes 85
documentos guarda ~2,9 GB/ano de páginas que não mudaram. Não há guarda hoje:
ninguém compara o documento **sem o rasto volátil** antes de gravar.

---

## F8 — ROBOTS

```
ROBOTS_ALLOW      6        ROBOTS_DISALLOW     0
ROBOTS_GATE_FAIL  1        ROBOTS_UNREADABLE   0
```

Lido **por visita**, nunca em cache entre corridas — o cache de processo é
limpo antes de cada leitura, e há um mutante de red team que o desliga e morre.

`IT-T7-033` (chianticlassico.com) **não foi visitada em nenhuma das quatro
corridas** porque não se conseguiu **LER** o robots dela.

> **«Não consegui ler» nunca vira «o site proibiu».**
> Uma é uma falha nossa; a outra é uma acusação ao site.

`ROBOTS_GATE_FAIL` também não colhe — não saber se se pode é motivo para parar.
Mas fica com o nome dele.

**O coletor canónico não lê `robots.txt`** — zero ocorrências da palavra em
`coleta/italy_pilot_collect.mjs`, e o livro não tem campo para o veredito. Sem
isto, sete fontes novas eram visitadas sem ninguém bater à porta. **Não se criou
um quarto leitor**: pergunta-se ao dono (`coleta/scrap_http.py`) antes de lançar.

---

## GATES

### G-RT — red team por mutação

```
MORTOS 16 · SOBREVIVERAM 0 · NÃO APLICADOS 0     RED_TEAM_PROVEN = YES
```

Cada mutante confirmado por `git diff` **antes** de a prova correr; ficheiro
reposto sempre. Os 16: legacy a entrar · `HUMAN_REVIEW` a entrar · fonte sem
contrato a ir à rede · bypass do portão · `FACT_TIME` por fallback · homepage
como matéria · paginação e feeds como documentos · `MATCH` desconhecido calado ·
`IDENTITY.STRATEGY` desconhecida calada · identidade a meio · os três do robots ·
o HTTP 200 inventado · a lista de IDs autorizados · o cache de robots.

**A primeira corrida deu 12/2/2, e as quatro falhas eram das minhas provas:**

- 2 âncoras não casaram — uma por `\n` onde o ficheiro é **CRLF**, outra por
  texto errado. *Mutante que não entrou não é mutante morto.*
- 2 mutantes **sobreviveram** porque o fixture usava armadilhas
  (`/news/page/2/`, `/feed/`) que o `LINK_PATTERN` já recusava sozinho: apagar o
  filtro do motor não mudava o resultado.

> **Uma armadilha que o padrão já recusa não prova o filtro.**
> Ela tem de **casar**, para que o filtro seja a única coisa que a barra.

Fixture refeito. Os dois passaram a morrer.

**Três ataques ficam `SEM_GUARDA`, e isso não é sucesso:**

1. **A 2.ª RUN regrava o armazém sem o documento ter mudado** — medido acima.
2. **O hash serve de identidade da versão.**
   `DOCUMENT_VERSION_ID == 'v1_' + RAW_SHA256[:12]` em **85 de 85**, conferido
   aritmeticamente. E `RAW_OBSERVATION_ID` **não existe**: 0 de 445 linhas.
   Defeito **pré-existente** e comum às duas linhas. A missão mandou medir e
   nomear, **não refactorizar** — e não se escreve uma guarda para um defeito que
   se decidiu não corrigir, porque isso deixa o trunk vermelho de propósito.
3. **`SOURCE_LOCATION` → `FACT_LOCATION` por fallback** — a regra existe em prosa
   nos 174 contratos e não há código que a execute. Não há o que mutar.

### G-ISO — rede real só nas corridas autorizadas

```
G-ISO = PASS
```

md5 de `observations.ndjson` e de `LIFECYCLE-LEDGER-V1.json` **idênticos** antes
e depois do red team e de toda a suíte. Todo coletor invocado em prova usa
lançador injectável ou fake.

**Uma falha minha, declarada.** O primeiro ensaio `--sem-rede` travava o coletor
e deixava a leitura de robots ir à rede na mesma: **7 pedidos de `robots.txt`
saíram de um ensaio que se dizia seco**. Corrigido no mesmo dia; está contado
nos 313.

### G-REG — regressão

```
G-REG = FAIL · NEW_FAILURES = 2
```

Medido contra a base **verdadeira** (worktree limpa em `4fdabf82`), não contra a
memória:

| suíte | antes | depois |
|---|---|---|
| `curadoria/` | 279 OK | **279 OK** |
| `medidas/` | — | **20 OK** (novas) |
| `tests/test_integracao_04a_curator` | — | **18 OK** (4 SKIP, novas) |
| `tests/test_italia_na_porta_canonica` | 22 OK | **22 OK** |
| `tests/test_alvo_estruturado_resolvido` | 1 fail | **1 fail** (o mesmo) |
| `tests/test_source_id` · `test_source_owner_identity` | OK | **OK** |
| `regras/motor_de_rota_test.mjs` | 23 | **45 OK** |
| `regras/italy_contract_test.mjs` | **74 falhas** | **73 falhas** |

O número global desceu, e mesmo assim **há 2 falhas novas**. Comparei por
**nome**, que é a única comparação que vale:

**Falhas novas — as duas causadas pela minha colheita ter entrado no livro do
piloto:**

1. `o piloto cobre exatamente as 7 fontes contratadas — 13`
   A guarda assume que o livro italiano só tem as 7 fontes do piloto. Agora tem
   13. **Acoplamento estrutural**, não defeito de código — mas é real e fica.

2. `toda observacao declara RAW preservado ANTES do parse`
   **A guarda apanhou um defeito verdadeiro.** As 85 observações `IDENTITY_FAILED`
   da RUN1B carregam um `RAW_SHA256` completo de 64 hex — e **nenhum byte**: sem
   `BYTES`, sem `RAW_PATH`, sem `RAW_PRESERVED_BEFORE_PARSE`. O coletor
   descarregou, falhou a identidade, **deitou fora os bytes e guardou o hash**.
   É exatamente o que a secção `PARSER_FAILURE MUST NOT DESTROY CAPTURED_RAW`
   existe para impedir.

**Três falhas desapareceram, e também sou eu** — as guardas leem
`runs.at(-1)`, a última corrida do livro, que agora é minha:
`a segunda rodada criou ZERO documentos novos`, `… ZERO objetos RAW`,
`… marcou SEEN_AGAIN tudo que reviu`.

**Não tornei estas duas verdes.** Apagar as 85 observações do livro seria
falsificar um registo append-only de uma corrida que aconteceu de verdade; e
corrigir o caminho de falha do coletor é mudar o coletor a meio de uma missão de
medição. **A guarda está a dizer a verdade, e a verdade é que o trunk ficou mais
vermelho do que eu o encontrei — em 2 provas, pelas razões acima.**

**Correção a um commit desta missão.** Em `f67ed097` escrevi que o enxerto do
`MATCH` tinha curado um vermelho de base (`348/74 → 349/73`). Errado por duas
vezes: primeiro chamei-lhe «leitura instável», e não era. A suíte lê o **livro
vivo**; eu estava a mudar o livro entre medições. O mecanismo é este, não acaso.

### G-MAP

```
SYSTEM_MAP_CHECK = PASS
```

O validador reprovou primeiro, e com razão: 3 ficheiros de código sem peça.
Declarados como **`C-CORRIDA-CANONICA`** em `Z-MEDIDAS`. Cadeia canónica
`REGERAR` + `VALIDAR` = OK.

---

## DEFEITO NOVO, MEDIDO AO GUARDAR A EVIDÊNCIA

```
76 dos 178 ficheiros do armazém italiano passam os 260 caracteres do MAX_PATH
maior caminho: 398 caracteres
pasta do DOCUMENTO mais longa: 212 caracteres, sozinha
```

`nomeDoAlvo` limita o **nome** a 60 caracteres. A pasta do **documento** nasce do
`DOCUMENT_ID` **sem limite**. O git recusou indexá-los até se ligar
`core.longpaths`. Os bytes existem, mas qualquer ferramenta Windows que use a API
antiga não lhes chega. **Não corrigido aqui**: mudar o molde da pasta obriga a
migrar o armazém inteiro.

---

## VEREDITO

```
CANONICAL_MICRO_COLLECTION_RESULT = PARTIAL

ELIGIBLE_INPUT 8 · CONTRACT_RESOLVED 7/8 · VISITADAS 6/7
OBSERVACOES 85 · SHA256 CONFERIDOS DO DISCO 85/85 · BYTES 7,99 MB
MATERIA_REAL_PROVADA 85/85 · CASCAS 0
RAW_PERSISTIDO fora do acervo · DERIVED NÃO EXECUTADO
ADMISSAO_DO_ITEM NÃO EXECUTADA · SALA 46 → 46 · BYPASS 0 · INSERÇÃO MANUAL 0
PEDIDOS 313 · PAID_USD 0.00 · EGRESSO IT · ROTA PAGA 0
G-RT PASS (16/0/0) · G-ISO PASS · G-MAP PASS · G-REG FAIL (NEW_FAILURES=2)
```

**Porquê PARTIAL e não PASS.** A aquisição passou inteira: pela regra, com
contrato, com robots lido por visita, com bytes íntegros e custo zero. A cadeia
canónica não fechou — e não por acaso: **falta a receita para T5, T7 e T10**, e
escrevê-la era o cutover proibido. Além disso o G-REG reprova com 2 falhas novas
que eu próprio provoquei e decidi não maquilhar.

**Porquê não FAIL.** 7/8 não impede PASS por si — a oitava está declarada. O que
impede é a cadeia partida no fim e o G-REG vermelho, e ambos estão nomeados com
o conserto identificado.

---

## O QUE FALTA, POR ORDEM

1. **A receita para T5, T7 e T10.** Sem ela nada chega à Sala. É decisão do dono,
   porque declara política de coleta.
2. **O caminho de falha do coletor.** `IDENTITY_FAILED` descarrega, deita fora os
   bytes e guarda o hash. Ou preserva, ou não regista hash nenhum.
3. **Comparar o documento sem o rasto volátil** antes de gravar. Hoje regravam-se
   83 de 85 por causa de um carimbo que somos nós a provocar.
4. **Desacoplar as guardas do piloto do livro partilhado.** Elas assumem 7 fontes
   e leem `runs.at(-1)`.
5. **O molde da pasta do documento**, que rebenta o MAX_PATH em 76 ficheiros.
6. **`DOCUMENT_VERSION_ID` derivado do hash** e `RAW_OBSERVATION_ID` inexistente —
   dívida pré-existente, das duas linhas.
7. **O terceiro leitor de robots** em `curadoria/`.

---

# EM PALAVRAS SIMPLES

Imagine uma biblioteca que quer recortar notícias de jornais italianos.

**Onde estava a ponte, e o que ela traduz.** Alguém já tinha ido a 173 sites
italianos, à mão, e escrito num caderno: *«neste site, as notícias estão nesta
página, e os links das notícias são assim»*. Esse caderno estava guardado noutra
gaveta do arquivo — outra versão do projeto. A nossa gaveta tinha o **porteiro**
(quem decide que sites podemos visitar), mas não tinha o caderno. A outra gaveta
tinha o caderno, mas não tinha porteiro. **Nunca tinham estado juntos.**

**Foi reutilizada?** Sim, e essa era a parte principal do trabalho. Copiei o
caderno **página a página**, nunca a gaveta inteira — porque juntar as gavetas de
uma vez apagava o porteiro sem dar erro nenhum. A nossa lista de sites que
sabemos visitar passou de **14 para 186**.

**Três coisas que descobri pelo caminho, e as três são a mesma história.** O
caderno dizia *«os links das notícias são assim»*, mas a nossa máquina estava a
procurar o endereço **dentro do texto da página**, em vez de **olhar para os
links**. É como procurar uma morada no meio de um livro em vez de olhar para a
lista telefónica. Depois, a máquina sabia dar nome a um recorte quando o nome
estava no ficheiro, mas não sabia dar-lhe nome a partir do endereço — e ficava
calada, sem dizer porquê. E antes disso a lista de sites que sabíamos visitar
estava **escrita à mão** e tinha nomes de sites diferentes daqueles que o
porteiro autorizava: o porteiro dizia «pode entrar» e a máquina respondia «não
conheço esta pessoa».

Nas duas primeiras tentativas o caderno de bordo escreveu *«este site não tem
notícias nenhumas»*. **Era mentira, e a mentira era nossa** — os sites tinham
notícias; nós é que estávamos a olhar para o sítio errado. Corrigi as três coisas
e pus provas por cima, para não voltar a acontecer calado.

**Quantas notícias foram guardadas de verdade.** **85 notícias italianas reais**,
de 6 sites — fruta, pecuária, universidade de Catânia, vinho de Reggio, vinagre
balsâmico de Modena, e a associação italiana de defensivos agrícolas. Cerca de
8 megabytes. Voltei a calcular a «impressão digital» de cada ficheiro a partir do
disco: **85 em 85 batem certo**. Nenhuma é uma página vazia. Custo: **zero
euros**. A visita foi feita de Itália, como devia.

Um sétimo site ficou de fora e é importante dizer **porquê**: não conseguimos
**ler** o aviso de boas-maneiras dele (o `robots.txt`). Isso **não** quer dizer
que ele nos proibiu — quer dizer que não conseguimos perguntar. Na dúvida, não se
entra. E um oitavo já se sabia de antemão que não tem caderno.

**Quantas chegaram à sala de espera: nenhuma.** E a razão é simples e concreta. A
biblioteca tem uma porta oficial por onde os recortes entram no arquivo, e essa
porta só abre com um **formulário** próprio de cada assunto. Há formulário para
clima, para pragas, para regulação — **não há formulário para os três assuntos
destas 85 notícias**. Escrever esse formulário é decidir *«de agora em diante,
quando pedirem este assunto, vai-se a estes sites»* — e essa é uma decisão sua,
não minha. A missão proibia-me expressamente de a tomar. Então as 85 notícias
estão **guardadas em caixa, seladas e conferidas**, à porta do arquivo. A sala de
espera tinha 46 fichas antes e tem 46 agora. Não entrou nada por nenhuma porta
das traseiras.

**O que mudou na segunda corrida — e é o achado mais útil.** Voltei aos mesmos
85 endereços nove minutos depois. A máquina reconheceu **os mesmos 85
documentos** (isso está certo). Mas achou que **83 tinham mudado** e guardou uma
segunda cópia de tudo. Fui comparar linha a linha: de 86 mil linhas, só 374
mudaram — e **todas** eram o site a escrever «última alteração: 19h34», que é
**a hora em que nós lá fomos**. Mais uns códigos internos de formulário. **Nem
uma palavra de texto mudou.** Ou seja: a máquina está a confundir a nossa própria
pegada com uma notícia nova. Se isto corresse todos os dias, guardávamos cerca de
**3 gigabytes por ano** de páginas idênticas.

**Uma coisa que eu próprio estraguei, e não escondo.** As minhas notas de coleta
entraram no mesmo caderno onde viviam as do projeto-piloto antigo, e isso fez
**duas verificações automáticas passarem a falhar**. Uma delas apanhou um
problema **verdadeiro**: nas tentativas falhadas, a máquina descarregou as
páginas, não conseguiu dar-lhes nome, **deitou fora as páginas e guardou a
impressão digital delas** — ficou com o recibo e perdeu o objeto. Podia ter
apagado as minhas notas para o alarme calar, mas isso era apagar o registo de uma
coisa que aconteceu. **Deixei o alarme a tocar, porque ele tem razão.**

**O que falta antes de isto ir para produção**, por ordem: o formulário dos três
assuntos (sem ele nada entra no arquivo); consertar a máquina para não deitar
fora páginas que já descarregou; e ensiná-la a ignorar o carimbo de hora antes de
decidir que uma notícia mudou. As outras quatro coisas estão na lista acima e
nenhuma impede o próximo passo.
