# MISSÃO 02 — REAL_EXAMPLE CAPTURER · RELATÓRIO

```
MISSAO        SOURCE-CURATOR-02-REAL-EXAMPLE-CAPTURER
DATA          2026-09-20
BRANCH        claude/bot-de-fontes-v2-plano
WORKTREE      C:/bot-fontes-v2
INITIAL_HEAD  2f1ecc61372f823648fcf9f10579b6ff6f613b7f
EGRESSO       205.147.30.6 · Milano, IT · AS208172 Proton AG   (medido no início)
```

> **Isto não é coleta.** Não cunha `RUN_ID`, não produz `RAW_OBSERVATION`, não
> entra no ingresso, não toca Admission nem Sala. E **não escreve na fila**:
> `candidatas/FONTES-CANDIDATAS.json` não foi aberto para escrita.
>
> ```
> CAPTURAR != QUALIFICAR != PROMOVER
> REAL_EXAMPLE != FACT — é evidência SOBRE A FONTE, não sobre o mundo.
> ```

---

## FASE 0 · ISOLAMENTO

```
SOURCE_CURATOR_BRANCH  claude/bot-de-fontes-v2-plano
SOURCE_CURATOR_HEAD    2f1ecc61
COORDINATOR_BRANCH     claude/contract-provenance-cutover-v1
COORDINATOR_HEAD       ffea8dbc   (local == origin)
TRUNK_HEAD             606974c3

base vs trunk         0 atrás / 2 à frente
base vs COORDINATOR   12 atrás / 2 à frente   ← DECLARADO, não rebaseado
```

A base está 12 commits atrás do COORDINATOR, e **isso não foi corrigido por
merge nem rebase** (proibido pelo enunciado). Em vez disso, todos os dados
vivos — fila, Atlas derivado — são lidos da ref do COORDINATOR por
`git show <ref>:<path>`, sem checkout e sem tocar na worktree dele. A worktree
`cutover-v2` não foi aberta.

```
ÁREA DE TRABALHO   curadoria/   — pasta nova; a missão ativa não toca nela
                                  (git diff 606974c3..ffea8dbc | grep ^curadoria/ = vazio)
```

---

## FASE 1 · AS 172, RE-MEDIDAS (não aceites por relato)

```
TOTAL_CANDIDATES          241
AUTO_DECIDIBLE            172
POLICY_BLOCKED_LINKEDIN    44
POLICY_BLOCKED_INSTAGRAM   25
                          ---
soma                      241   ✔

bate com o relatório anterior (172 / 44 / 25)?   SIM
```

Por família, medido a partir da URL de cada candidata:

```
HTML_SITE   92      YOUTUBE  60      FACEBOOK  20      LINKEDIN 44      INSTAGRAM 25
```

---

## FASE 2 · `REAL_EXAMPLE` — REUTILIZADO, NÃO INVENTADO

Procurado owner antes de definir. **Existe**, e a régua veio de lá:

```
candidatas/decidir_fila_italia.py::FALTA_O_ITEM
  «endereco proprio do item, tipo, titulo, HTTP, content-type, bytes e data visivel»

data/samples/IT-SOURCE-SAMPLES/<SOURCE_ID>/MANIFEST.json
  o formato que as 140 fontes já registadas atravessaram
```

Criar uma régua nova faria as fontes novas entrarem no Atlas com um critério
diferente das que lá estão. O capturador implementa **essa** régua, mais o
`SHA256` que o `MANIFEST.json` exige.

---

## FASE 3–4 · A CAPACIDADE CONSTRUÍDA

```
curadoria/capturador.py              a captura, por família        (~700 linhas)
curadoria/correr_lote.py             lotes + classificação
curadoria/consolidar.py              junta os lotes, mede o funil
curadoria/manifesto_da_evidencia.py  manifesto verificável dos bytes
curadoria/test_capturador.py         24 testes
curadoria/test_correr_lote.py        11 testes
```

Famílias derivadas do que a fila **tem**, não de uma taxonomia imaginada:

| family | `CAPTURE_STRATEGY` | `REAL_EXAMPLE_METHOD` | `EXPECTED_OUTPUT` |
|---|---|---|---|
| `HTML_SITE` | ler a entrada, achar item interno com data | índice → item (até 3 tentativas) | HTML ou PDF |
| `DIRECT_PDF` | o endereço já é o documento | GET direto | PDF |
| `YOUTUBE` | resolver `externalId` → feed RSS público | 1ª `<entry>` do feed | metadados de vídeo |
| `FACEBOOK` | superfície pública, sem sessão | página, com verificação de título | HTML |
| `LINKEDIN` · `INSTAGRAM` | **não se toca** | — | — |

---

## FASE 8 · EXECUÇÃO — RESULTADO

```
TOTAL_CANDIDATES          241
TARGET_AUTO_DECIDIBLE     172
ATTEMPTED                 172        (100% do alvo)

REAL_EXAMPLE_CAPTURED     125
REAL_EXAMPLE_FAILED        47

PROPOSED_PROMOTE          124
PROPOSED_REJECT             0        ← e é o resultado CORRECTO, ver abaixo
PROPOSED_BLOCK              6
NEEDS_REVIEW               34
UNKNOWN                     6
ENDPOINT_OF_EXISTING_SOURCE 2
                          ---
soma                      172   ✔

LINKEDIN_UNTOUCHED         44        zero pedidos de rede
INSTAGRAM_UNTOUCHED        25        zero pedidos de rede
```

### BY_FAMILY

```
YOUTUBE     60   PROMOTE 60
FACEBOOK    20   PROMOTE 14 · BLOCK 6
HTML_SITE   92   PROMOTE 50 · NEEDS_REVIEW 34 · UNKNOWN 6 · ENDPOINT 2
PDF         (nenhuma candidata era .pdf direto — a família existe e não foi exercitada)
```

### CAPTURE_FAILURE_CLASSES

```
NO_ITEM_FOUND  33    respondeu, e não se achou item próprio
DNS_OR_CONN     7    não se chegou lá deste egresso
WALL            6    muro de login/consentimento
HTTP_ERROR      1    o servidor devolveu erro
```

### `PROPOSED_REJECT = 0` é um resultado, não uma omissão

Nenhum caminho do código devolve `REJECT` por falha de leitura. `REJECT` exige
prova **positiva** de que a fonte não serve, e nesta corrida nenhuma evidência
dessas foi produzida.

```
«NÃO CONSEGUI LER»  !=  «NÃO SERVE»
```

É a mesma lei que, em 14/09, obrigou a revogar 25 recusas nesta casa: elas
assentavam em `HTTP 429`, `THIN_BODY` e `PLATFORM_GENERIC_TITLE` — três factos
sobre o leitor, nenhum sobre a fonte.

---

## FASE 5 · EXPECTED YIELD

```
EXPECTED_YIELD_MEASURED   110
EXPECTED_YIELD_UNKNOWN     62
```

| family | HIGH | MEDIUM | LOW | DORMANT | UNKNOWN |
|---|---|---|---|---|---|
| `YOUTUBE` | 7 | 11 | 24 | 17 | 1 |
| `HTML_SITE` | 15 | 23 | 13 | — | 41 |
| `FACEBOOK` | — | — | — | — | 20 |

O YouTube é a única família com **cadência medida**, porque o feed traz as
datas: mediana do intervalo entre publicações **mais** dias desde o último item.

```
RITMO OBSERVADO   SEMANAL 11 · MENSAL 15 · ESPARSA 12 · RAJADA 21 · sem dados 1
```

> **`DORMANT = 17` é o achado desta fase.** Dezassete canais oficiais italianos
> estão parados há mais de um ano. Sem o eixo da recência, a mediana sozinha
> dava-lhes «cadência alta» — publicaram muito, em rajada, e depois calaram-se.

---

## FASE 7 · ENDPOINT vs SOURCE — os 2 casos revalidados

```
CAND-0006  ersaf.lombardia.it        → ENDPOINT_OF  IT-T1-008
CAND-0017  regione.vda.it            → ENDPOINT_OF  IT-T1-012
```

Confirmam a previsão da missão anterior. `COL-LAW-205`: a fonte é estável, o
endpoint é substituível. A proposta é `DERIVA_DE` na ficha existente, **nunca**
um `SOURCE_ID` novo.

---

## FASE 13 · O QUE A PRÓXIMA MISSÃO RECEBE

`ONBOARDING_FAMILY` dos 124 `PROMOTE`:

| família de onboarding | N | `LIKELY_ROUTE_STRATEGY` | adaptação |
|---|---|---|---|
| `YOUTUBE_FEED` | **60** | `APPLICATION_ROUTE` | **NÃO** — capacidade YouTube já existe em T9 |
| `HTML_PUBLIC` | **37** | `STATIC_ROUTE` | **NÃO** |
| `FACEBOOK_PUBLIC_SURFACE` | 14 | `BROWSER_DISCOVERED_ROUTE` | SIM — exige navegador |
| `PDF_DISCOVERY_PAGE` | 13 | `DISCOVERED_ROUTE` | SIM — ramo de índice |

```
NEXT_ONBOARDING_BATCH_SIZE = 97      (60 YOUTUBE_FEED + 37 HTML_PUBLIC)
```

São os que **não precisam de capacidade nova**: duas famílias de rota, uma
delas já implementada. Os outros 27 precisam de navegador ou de ramo de índice —
trabalho do SCRAP ENGINEER, não deste departamento.

---

## FASE 14 · COBERTURA DOS 124 PROMOTE

Derivada do `TIPO` que a própria fila declarou — **não é opinião, e não é valor
para a Intelligence**, que só se mede depois do gasto.

```
60   competitor-and-sector communication (video)
27   sector-organization / technical-guidance
14   competitor-and-sector communication (social)
10   market / sector-communication
 7   science
 6   regulatory / official-data
```

---

## FASE 11 · FUNIL DO PRÓPRIO CURATOR

```
CANDIDATES_ATTEMPTED      172
REAL_EXAMPLE_CAPTURED     125      72,7%
REAL_EXAMPLE_FAILED        47      27,3%
QUALIFIED (PROMOTE+ENDPOINT) 126   73,3%
NEEDS_HUMAN_OR_REVIEW      40      NEEDS_REVIEW 34 + BLOCK 6
UNKNOWN                     6
```

---

## OS QUATRO DEFEITOS QUE A CORRIDA AO VIVO REVELOU

Nenhum foi encontrado pelos testes. Todos foram encontrados **olhando para a
saída real** — e cada um ganhou um teste que falha se voltar.

### 1 · Uma listagem não é um item

Primeira corrida: 3 `PROMOTE` cujo «item real» era `/notizie` e
`/website/newsdipartimenti/` — **outra listagem**. Isso repetiria exactamente o
defeito da sonda de 14/09 que esta missão existe para corrigir.

```
«O ENDEREÇO RESPONDE» != «A FONTE ENTREGA ISTO»,
e uma LISTAGEM de itens não é um ITEM.
```
→ `parece_item()` + 3 testes.

### 2 · Domínio de plataforma não é domínio de fonte

As 60 candidatas YouTube casavam `youtube.com` contra `IT-T8-001` e saíam todas
como «endpoint da mesma fonte» — 60 organizações italianas distintas declaradas
o mesmo canal.

```
DEDUPLICAR PELO ANFITRIÃO FUNDE TODA A PLATAFORMA NUM SÓ DONO.
```

É o mesmo erro que em 14/09 fundiu três LinkedIn de três donos por todos
redirigirem para `/login`.
→ `chave_social()` = `(anfitrião, handle)`, `COL-LAW-034`. Verificado: **60
channel_ids distintos em 60**.

### 3 · O feed tem uma data que não é do vídeo

O feed do YouTube traz `<title>` e `<published>` **ao nível do feed** — nome do
canal e data de **criação** do canal. Uma leitura global devolvia-os primeiro:
um vídeo de 2026 ficou com data de 2015, e a cadência deu «mediana 0d — DIÁRIA»
por causa do outlier de dez anos. **Duas medidas erradas de uma vez, ambas com
ar de facto.**
→ `_entradas()` lê `<entry>` a `<entry>`.

### 4 · Um `400` uniforme acusa o cliente, não a plataforma

As 20 candidatas Facebook devolveram `HTTP 400`. Antes de escrever «superfície
fechada», controlo conhecido-bom:

```
facebook.com/Meta    curl simples            -> 200
facebook.com/Meta    o meu UA completo       -> 400
                     o mesmo UA sem `Safari/537.36` -> 200
```

O defeito era o meu `User-Agent`. Corrigido → 20/20 passaram a responder.
E então um quinto sinal: uma delas devolveu `200` com 326 KB e título
**«Facebook»** — a porta da plataforma, não a fonte. `WALL`, não `PROMOTE`.

```
«NÃO LI» != «NÃO SERVE».   E a gémea:   «LI A PLATAFORMA» != «LI A FONTE».
```

---

## FASE 16 · TESTES

```
curadoria/test_capturador.py    24 testes   OK   exit=0
curadoria/test_correr_lote.py   11 testes   OK   exit=0
                                ---
TOTAL                           35 testes   NEW_FAILURES = 0
```

Cobertura exigida pelo enunciado: candidato válido · endpoint morto · redirect ·
HTML sem conteúdo · PDF direto · índice PDF · YouTube · mesma SOURCE com
endpoint diferente · timeout · UNKNOWN · BLOCK por policy. **Todos presentes.**

A maioria é **negativa**, de propósito:

```
TODA SONDA PRECISA DE UM CASO QUE A FAÇA DIZER «NÃO».
```

A prova mais forte é `test_linkedin_e_instagram_nao_geram_pedido_de_rede`: não
verifica só o veredito — verifica que a lista de pedidos de rede ficou **vazia**.

> **Dois testes reprovaram por defeito do próprio harness**, não do código: o
> mock casava por substring (`exemplo.it/` ganhava de `/doc/rel.pdf`) e os
> fixtures tinham menos de 200 bytes, disparando `EMPTY_BODY` antes da regra sob
> teste. Corrigi o **teste**, não o capturador.
>
> ```
> UM MOCK QUE RESPONDE À PERGUNTA ERRADA
> REPROVA CÓDIGO CERTO, E MANDA-NOS «CONSERTÁ-LO».
> ```

---

## RED TEAM DA PRÓPRIA ENTREGA

```
PASS  REJECT = 0 — nenhuma falha de leitura virou recusa
PASS  todo PROMOTE tem REAL_EXAMPLE_REF                      124/124
PASS  todo PROMOTE tem sha256 de 64 caracteres               124/124
PASS  o ficheiro de prova existe no disco                    124/124
PASS  o sha256 confere com os bytes gravados                 124/124
PASS  nenhuma decisão para LinkedIn/Instagram                  0/69
PASS  172 decisões, e a soma dos estados dá 172
PASS  os 2 endpoints apontam a fontes distintas   IT-T1-008 · IT-T1-012
PASS  60 YouTube com sha256 distintos             (sem colisão de canal)
PASS  manifesto × índice: SHA_DIVERGENTE = 0
```

**Uma falha encontrada e corrigida:** 7 pastas de evidência sobreviviam de uma
corrida anterior ao detetor de muro — provas de candidatas que a regra **final**
classifica como `BLOCK`/`ENDPOINT`. Guardar a amostra de uma fonte bloqueada
deixaria prova a sustentar uma conclusão que já não existe. Removidas; agora as
pastas de evidência são **exactamente** os 124 `PROMOTE`.

---

## ARTEFATOS

```
VERSIONADOS
  curadoria/capturador.py                     a capacidade
  curadoria/correr_lote.py                    lotes + classificação
  curadoria/consolidar.py                     funil
  curadoria/manifesto_da_evidencia.py         manifesto
  curadoria/test_capturador.py                24 testes
  curadoria/test_correr_lote.py               11 testes
  curadoria/SOURCE-CURATOR-DECISIONS-V1.json  172 propostas
  curadoria/REAL-EXAMPLE-INDEX-V1.json        172 fichas
  curadoria/REAL-EXAMPLE-MANIFEST-V1.json     124 provas com sha256
  curadoria/FUNIL-DO-CURATOR-V1.json          telemetria
  curadoria/RELATORIO-MISSAO-02.md            este ficheiro
  curadoria/.gitignore

FORA DO GIT (deliberado)
  curadoria/evidencia/   124 ficheiros · 59,6 MB de material de terceiros
```

> **A prova é o sha, não o ficheiro no repositório.** Commitar 59,6 MB de PDFs e
> um MP4 de 12 MB por causa de uma missão de qualificação poria material de
> terceiros na árvore para sempre. O manifesto permite refazer a captura e
> comparar — que é o que o `MANIFEST.json` do Atlas já faz. Na promoção, os
> bytes mudam para `data/samples/IT-SOURCE-SAMPLES/<SOURCE_ID>/`, caminho que só
> existe **quando houver** `SOURCE_ID`.

---

## FASE 12 · O QUE **NÃO** FOI FEITO

```
candidatas/FONTES-CANDIDATAS.json    NÃO aberto para escrita · 0 transições
regras/italy_contracts.mjs           NÃO tocado
coleta/italy_pilot_collect.mjs       NÃO tocado
System Map                           NÃO regenerado
contratos Collection                 NENHUM criado
Big Collection                       NÃO tocada
merge                                NÃO feito
LinkedIn (44) · Instagram (25)       zero pedidos de rede
```

---

# EM PALAVRAS SIMPLES

**1. Quantas o robô examinou.** **172** — todas as que não estão bloqueadas por
regra. Das 241 da fila, 69 são LinkedIn e Instagram e ficaram intocadas: o robô
não lhes enviou um único pedido.

**2. Quantas conseguiu provar que são fontes boas.** **124.** Para cada uma
abriu um documento de verdade, guardou-o e registou a impressão digital. É esse
o degrau que faltava — e era o mesmo degrau para as 241.

**3. Quantas descartou com prova.** **Zero** — e isso está certo. Descartar
exige provar que a fonte **não serve**. Não conseguir ler não é a mesma coisa:
já custou caro a esta casa, quando 25 fontes foram recusadas por motivos que
diziam respeito ao leitor, não a elas.

**4. Quantas bloqueou.** **6** — páginas de Facebook que devolvem um muro em vez
de conteúdo. É falta de capacidade técnica, não juízo sobre a fonte.

**5. Quantas precisam mesmo de gente.** **40**: 34 sites onde o robô entrou mas
não encontrou um documento próprio, e 6 bloqueadas. Mais **6** em que nem se
conseguiu chegar ao servidor — e essas ficam como «não sei», que é honesto.

**6. Quanto cada família tende a produzir.** O YouTube é o único onde deu para
medir o ritmo real, porque a lista de vídeos traz as datas: 11 canais publicam
por semana, 15 por mês, e **17 estão parados há mais de um ano**. Esses últimos
são o achado: pareciam activos porque publicaram muito de uma vez — e depois
calaram-se.

**7. Quantas entram na próxima missão.** **97** — 60 do YouTube e 37 de sites.
São as que não precisam de nada novo: para o YouTube a ligação já existe, e os
sites usam o tipo de caminho mais simples que há. As outras 27 precisam de
navegador ou de um pedaço de programa novo, e isso é de outra equipa.

**E uma nota sobre como isto correu.** O robô encontrou **quatro erros meus** que
os testes não apanharam — só apareceram ao olhar para o resultado verdadeiro.
O mais instrutivo: as 20 páginas do Facebook devolviam erro, e eu quase escrevi
"o Facebook está fechado". Testei primeiro uma página que eu sabia que
funcionava, e ela também dava erro. O problema era como o meu programa se
apresentava ao site. Corrigido, as 20 passaram a responder.

```
ANTES DE CULPAR A FONTE, PROVAR QUE O LEITOR FUNCIONA.
```

---

**HARD STOP.** Nada foi integrado ao registry. Nenhum contrato de Collection foi
criado. A Big Collection não foi tocada. Nenhum merge foi feito.
