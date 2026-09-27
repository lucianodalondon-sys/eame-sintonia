# RELATÓRIO — PARIDADE DE INCREMENTALIDADE EM PRODUÇÃO V1

```
ACTUAL_LLM_MODEL = claude-opus-5   (Opus 5)
DATA             = 2026-09-22
BASE             = cutover-prod-v1 @ 0799f2bb   (o cutover NÃO foi refeito nem desfeito)
```

---

## FASE 0 · O QUE JÁ ESTAVA MEDIDO, CONFERIDO

A causa que o dono localizou está **confirmada em todos os pontos**.

```
CANON  paridade-v1 (de cutover-prod-v1)  0799f2bb  sujo 0
OPS    ops/cutover-prod-v1               e7c72357  sujo 1
```

O «sujo 1» da ops é `data/collection-ledger/italy/logs/runs.log` — o registo que
o agendador escreve de hora a hora. É saída de operação, não alteração de
código.

```
regras/incrementalidade.mjs        md5 fa79d5279b9cbe6c008eace6aa93f936  LAB == OPS
medidas/incrementalidade_prova.mjs md5 aeb2bf4365944e90a751ee34d41adc3f  LAB == OPS
regras/incrementalidade_test.mjs   md5 5fbf5820cbd688b3b99c25e601d846fe  LAB == OPS
coleta/italy_pilot_collect.mjs     md5 8b75611ae443f776c43b31d1683e3eeb  LAB == OPS

hipótese A «código stale»    REFUTADA
hipótese B «peça em falta»   REFUTADA
```

Quem chamava `decidirSobreDetalhe()`, medido com `git grep` sobre a árvore
inteira — três ficheiros, e nenhum deles produz:

```
regras/incrementalidade.mjs        o próprio
regras/incrementalidade_test.mjs   o teste dele
medidas/incrementalidade_prova.mjs a prova dele
```

E `coleta/italy_pilot_collect.mjs` — que é quem bate à porta (`baixar()`, linha
474) e quem escreve `DOCUMENT_CHANGED_IN_PLACE` (linha 511) — tinha **zero**
referências a incrementalidade.

```
ROOT_CAUSE = MISSING_ROUTE
```

> **Não encontrei erro na localização do dono.** Está certa nos quatro pontos:
> md5 idêntico, não é stale, não é peça em falta, e o coletor real não a chama.
> O que acrescentei foi o que a correcção exigia a seguir — ver FASE 9.

---

## FASE 1 · PARIDADE CIRÚRGICA

Só as peças do escopo. **Nenhum diff amplo do repositório foi feito.**

| peça | LAB | OPS | veredicto |
|---|---|---|---|
| `regras/incrementalidade.mjs` | `fa79d5279b9c` | `fa79d5279b9c` | `IDENTICAL` |
| `regras/incrementalidade_test.mjs` | `5fbf5820cbd6` | `5fbf5820cbd6` | `IDENTICAL` |
| `medidas/incrementalidade_prova.mjs` | `aeb2bf436594` | `aeb2bf436594` | `IDENTICAL` |
| `coleta/italy_pilot_collect.mjs` | `8b75611ae443` | `8b75611ae443` | `IDENTICAL` |
| normalização de conteúdo | **não existia** | **não existia** | `ABSENT_BOTH_SIDES` |

```
LAB_OWNER_OF_DECISION      regras/incrementalidade.mjs
OPS_OWNER_OF_DECISION      regras/incrementalidade.mjs        (mesmo ficheiro)

LAB_DECISION_PATH          medidas/incrementalidade_prova.mjs
                             → decidirSobreDetalhe() → SKIP/FETCH/REVALIDATE
OPS_DECISION_PATH          coleta/italy_pilot_collect.mjs:474 baixar()
                             → :502 anterior.filter(mesmo DOCUMENT_ID)
                             → :511 DOCUMENT_CHANGED_IN_PLACE
                           (decidirSobreDetalhe NÃO aparece)

LAB_NORMALIZER             NENHUM
OPS_NORMALIZER             NENHUM

LAB_PRE_FETCH_DECISION     SIM — a prova chama a regra antes de qualquer byte
OPS_PRE_FETCH_DECISION     NÃO — a rede é gasta primeiro

CONTRATO DAS 2 FONTES DO CANÁRIO
  IT-T10-018  myfruit.it                    ACQUISITION HTML_LINK_DISCOVERY
  IT-T10-022  zootecnicainternational.com   ACQUISITION HTML_LINK_DISCOVERY
  UPDATE_BEHAVIOR de ambas: "NAO SEI"   ·   RECOLLECTION: ausente nas duas
```

```
PARITY_DIFFERENCES = 0 ficheiros diferentes · 1 rota em falta
```

A paridade de **ficheiros** era perfeita. A paridade de **rota** não existia.
É essa a diferença inteira, e é por isso que a comparação de md5 dava verde.

---

## FASE 2 · ONDE NASCE O FALSO `DOCUMENT_CHANGED_IN_PLACE`

Medido sobre os bytes que as duas corridas do canário já tinham deixado em
disco. **Zero rede.** Medidor: `medidas/paridade_replay.mjs`, saída em
`medidas/PARIDADE-REPLAY-V1.json`.

```
RUN1  OPS_forward-only-live_20260922020109_0d088d   32 detalhes
RUN2  OPS_forward-only-live_20260922020511_8be761   39 detalhes

DOCUMENT_ID nas duas corridas     32
só na RUN2 (artigos novos)         7
bytes em falta                     0

RAW_CHANGED                       32 de 32
NORMALIZED_CHANGED                 0 de 32
VOLATILE_DIFFERENCE               32 de 32
FALSE_DOCUMENT_CHANGED_IN_PLACE   32
mesmo NÚMERO DE BYTES             23 de 32
```

### Uma ocorrência real, com todos os campos

```
DOCUMENT_ID            IT-T10-018:URL:news/annamaria-medici-in-ortofrutta-vince-il-valore-percepito
SOURCE_URL             https://www.myfruit.it/news/annamaria-medici-in-ortofrutta-vince-il-valore-percepito

RUN1_SHA_RAW           609c86e6847e2fc8…      RUN1_BYTES  100970
RUN2_SHA_RAW           0efe46002b550cc8…      RUN2_BYTES  100970

RUN1_NORMALIZED_SHA    (igual)  ─┐
RUN2_NORMALIZED_SHA    (igual)  ─┴─ OLD_NORMALIZED_HASH == NEW_NORMALIZED_HASH

RAW_CHANGED            true
NORMALIZED_CHANGED     false
VISIBLE_TEXT_CHANGED   false
VOLATILE_DIFFERENCE    true
VEREDICTO              VOLATILE_ONLY
```

As **4 linhas** que diferiam, em 1500 linhas idênticas, e mais nada.

### O trecho volátil exato, nomeado

⚠️ **Nada aqui foi generalizado.** Cada trecho foi medido documento a documento
e só entrou na lista depois disso. As contagens são o número de trechos que
diferiram, nos 32 pares.

```
IT-T10-018 · myfruit.it (October CMS)
   179  <input name="_session_key" value="…40 caracteres…">   chave de sessão
    48  <meta property="article:modified_time" content="…">    ← A NOSSA VISITA
    13  <input name="_token" value="…40 caracteres…">          CSRF do formulário
     9  <div class="views">NNN</div>                           ← O CONTADOR DE VISITAS

IT-T10-022 · zootecnicainternational.com (WordPress + tagDiv Newspaper)
   532  <aside class="… zoote-widget">…</aside>                rotador de banners
    25  uid: <hex>  no comentário «Speed booster» do tema      id por pedido
     9  <script id="zoote-tracking">                           a ORDEM dos anúncios
     9  <!-- Parsed with iubenda … in 0.00315 sec. -->          cronómetro do servidor
```

**Dois desses somos nós.** O dono tinha razão: o contador de visitas é causa
real — e não está sozinho.

```
<div class="views">134</div> → 135   ·   604 → 606   ·   6444 → 6448

article:modified_time = 2026-09-22T02:01:41Z   e o nosso CAPTURED_AT = 02:01:42Z
                      = 2026-09-22T02:06:03Z   e o nosso CAPTURED_AT = 02:06:04Z
```

`article:modified_time` **não é** a data em que alguém editou o artigo. É a
hora a que nós pedimos a página — um segundo antes do nosso próprio carimbo de
captura, nos dois casos.

E os 9 documentos do zoote-tracking: o **mesmo conjunto** de 11 anúncios, por
outra ordem, em **9 de 9**. Só com essa prova é que a regra entrou.

```
RUN1  15851,15321,13882,15995,15441,15000,15859,16233,17136,680,5840
RUN2  17136,15441,15000,15995,15851,13882,15321,15859,16233,680,5840
```

---

## FASES 3–4 · AS DUAS DEFESAS, AMBAS INSTALADAS

```
1 · PRE-FETCH INCREMENTALITY   regras/incrementalidade.mjs          REUTILIZADA
2 · CONTENT NORMALIZATION      regras/normalizacao_de_conteudo.mjs  NOVA (não v2)
```

**A primeira evita o pedido.** `decidirSobreDetalhe()` corre **acima** de
`baixar()`, dentro do laço dos alvos. Não recebe bytes nem sha — não os pode
receber, porque se os recebesse a rede já teria sido paga.

**A segunda evita a mentira no livro.** Não substitui a primeira: quando ela
fala, a rede já foi gasta. Serve para a revalidação legítima, que existe.

`fetch → comparar → perceber que era igual → dedup` **não foi aceite**, e há uma
prova que o impede de voltar: compara os índices no texto do coletor e reprova
se a decisão cair abaixo do download.

### Revalidação legítima — declarada, e porquê

`KNOWN DOCUMENT + sem razão canónica → SKIP BEFORE FETCH`. Ir outra vez exige
razão de um vocabulário fechado de cinco, e a razão vai escrita no censo da
corrida (`REVISIT_REASONS`).

### Sobre o `normalizador-v2` proibido

```
ADAMA_DESIGN_SYSTEM_MATCH = NOT_APPLICABLE   (esta missão não toca em UI)
NEW_PATTERN_REQUIRED      = YES
```

Medido com `git grep` sobre todos os `.mjs` antes de escrever uma linha: **não
existia normalizador nenhum nesta casa**. `normalizarSias()` é um *parser* de
tabela de precipitação — transforma HTML em observações com chave; outra
pergunta, outra saída. Não há segunda fonte de verdade porque não havia
primeira.

E vive **fora** de `incrementalidade.mjs` por lei declarada naquele ficheiro:
*«esta regra NÃO recebe bytes, NÃO recebe sha e NÃO os pode receber»*. O
normalizador come bytes por definição. Juntá-los apagava a única garantia que
aquela assinatura dá.

---

## FASE 5 · A CORREÇÃO MÍNIMA

```
regras/incrementalidade.mjs          REUTILIZADA, ZERO LINHAS ALTERADAS
regras/normalizacao_de_conteudo.mjs  peça nova (a primeira desta casa)
coleta/italy_pilot_collect.mjs       +211 linhas: a ligação
regras/italy_contracts.mjs           +32 linhas: RECOLLECTION em 7 contratos
```

```
incrementalidade-v2   NÃO criado
normalizador-v2       NÃO criado (não havia v1)
segundo ledger        NÃO criado
segunda fonte de verdade   NÃO criada
```

### Um campo novo, e porquê ele foi preciso

Quando a defesa 2 conclui `VOLATILE_ONLY`, a observação fica `SEEN_AGAIN` e
reutiliza a versão já guardada — não nasce um `v4` para arrumar ruído.
`RAW_SHA256` continua a ser o sha do ficheiro em `RAW_PATH`, e os bytes que
chegaram agora vão em `RECEIVED_RAW_SHA256`.

Isto é obrigatório: `medidas/coorte_da_micro_collection.py` acende
`SHA_MISMATCH` quando o livro aponta para bytes que não batem — *«o que falta
sabe-se que falta; o trocado passa por bom»*. Duas perguntas, dois campos, como
a casa já faz com `MIME_ASSINATURA` (o que eu medi) ≠ `CONTENT_TYPE` (o que ele
disse).

---

## FASES 6–7 · REPLAY OFFLINE E TESTES NEGATIVOS

Nenhuma rede foi tocada antes deste ponto.

```
regras/paridade_test.mjs            31 provas   31 passaram   0 falharam
provas/paridade_duas_rodadas.mjs    13 provas   13 passaram   0 falharam
```

**Os dois lados de cada par, todos exigidos:**

| exigido | resultado |
|---|---|
| contador de visitas muda → **não** é change | ok |
| token muda → **não** é change | ok |
| chave de sessão muda → **não** é change | ok |
| `article:modified_time` muda → **não** é change | ok |
| anúncio, uid e cronómetro mudam → **não** é change | ok |
| **palavra real do corpo muda → É change** | ok |
| **título muda → É change** | ok |
| **um só carácter muda → É change** | ok |
| **matéria muda E voláteis mudam → É change** | ok |
| documento novo → `FETCH`, `CONHECIDO=false` | ok |
| conhecido elegível → **não faz fetch** | ok |
| precisa revalidar → pode ir, **pela regra, com razão nomeada** | ok |
| índice → revisita-se sempre | ok |

E a prova de ponta a ponta, que arranca o coletor inteiro numa raiz descartável:

```
        rede  DETAIL_REQUESTS  NEW  SKIPPED  REVALIDATED  CHANGED  SEEN_AGAIN  UNNECESSARY
RUN1     1          1           1      0          0          0          0           0
RUN2     0          0           0      1          0          0          0           0
RUN3     0          0           0      1          0          0          0           0
RUN4     1          1           0      0          1          0          1           0
RUN5     1          1           0      0          1          1          0           0
```

A RUN3 existe por uma razão nomeada: se o salto da RUN2 tivesse ido para o
livro com um resultado fora de `RESULTADOS_COM_DOCUMENTO`, a memória da corrida
seguinte leria «nunca se guardou documento deste endereço» e voltava a
descarregar tudo. **Um salto que se auto-desfaz parece incrementalidade e não
é.** Por isso o salto não é escrito no livro — vai contado no resumo da corrida.

---

## FASE 8 · RED TEAM

`provas/paridade_red_team.mjs` · saída em `provas/PARIDADE-RED-TEAM-V1.json`

**Protocolo cache-safe (§165) traduzido para Node**, porque `__pycache__` não
existe aqui: `NODE_DISABLE_COMPILE_CACHE=1`, `NODE_COMPILE_CACHE` apagado,
**processo novo por ataque**, diff provado por `git diff --stat`, e uma **sonda
que confirma que o mutante CORREU** — não só que o ficheiro mudou.

| # | ataque | mutante correu | morto por |
|---|---|---|---|
| M1 | desligar o pre-fetch skip | sim | `RUN2 NAO BATE A PORTA` |
| M2 | forçar fetch em todo conhecido | sim | `conhecido e elegivel -> NAO FAZ FETCH` |
| M3 | contador altera hash semântico | sim | `contador de visitas muda -> NAO e change` |
| M4 | normalizador apaga mudança real | sim | `uma palavra do corpo muda -> E CHANGE` |
| M5 | todo `CHANGED_IN_PLACE` vira `SEEN_AGAIN` | sim | `uma palavra da materia muda` |
| M6 | desligar normalização | sim | `contador de visitas muda -> NAO e change` |
| M7 | decidir só por `RAW_SHA` | sim | `contador de visitas muda -> NAO e change` |
| M8 | dedup pós-download em vez de skip | sim | `RUN2 NAO BATE A PORTA` |

```
RED_TEAM_SURVIVORS = 0   ·   ÁRVORE LIMPA DEPOIS = sim
```

### O M8 sobreviveu à primeira versão, e isso encontrou um defeito real

Não porque a defesa fosse fraca: **o ataque não tocava em nada que a bancada
pudesse ver.** Ele punha um download extra só no ramo com rede, e a bancada
corre sem rede.

A causa estava no medidor, não no ataque: o contador de idas ao transporte
vivia só dentro de `baixar()`, por isso uma corrida com bytes injectados não
via pedido nenhum. **Um medidor que só conta a rede real não mede uma corrida
sem rede.** Corrigiram-se os dois — e só então o M8 morreu, e morreu pela prova
de comportamento.

Foi acrescentado um campo `MORTE_ESPERADA`: **morrer pela prova errada conta
como `SURVIVOR`**. Sem isso, um mutante abatido por uma prova que nada tem a ver
com ele esconde que a prova a sério ficou calada.

Duas armadilhas deste sistema, fechadas no próprio código:

- o repositório guarda LF e o `git checkout` devolve CRLF; a partir do primeiro
  restauro uma âncora escrita com `\n` deixa de casar. A âncora é procurada nas
  **duas** formas.
- `git status --porcelain` mostra também o índice e diz «sujo» com a árvore
  limpa. A conferência do restauro usa `git diff`.

---

## FASE 9 · REGRESSÃO — E O QUE ELA APANHOU

Base medida numa worktree limpa em `0799f2bb`, e comparada **por nome**, nunca
pelo número.

```
BASE   198 módulos · 4970 testes · 214 FAIL + 31 ERROR = 245
NOVO   198 módulos · 4970 testes · 215 FAIL + 31 ERROR = 246
```

```
NEW_FAILURES  = 0
CURED         = 0
```

A única linha a mais era o ponto fixo do System Map, curado pela FASE 15 e
confirmado depois a verde. Suítes `.mjs` comparadas linha a linha: saída
**idêntica** à da base nas duas que já chegavam vermelhas
(`italy_contract_test.mjs`, `italy_pilot_negativos.mjs` — esta última por uma
data de calendário que passou).

### ⚠️ O ACHADO MAIS PERIGOSO DESTA MISSÃO

Num passo intermédio a regressão acusou **6 falhas novas**, todas em testes que
exigem que a segunda corrida escreva `SEEN_AGAIN` com `RAW_PATH`. Os testes
estavam certos, e apontavam para isto:

```
contratos com o bloco executável RECOLLECTION:  0 de 186
```

`regras/incrementalidade.mjs` lê `RECOLLECTION`, e **recusa-se** a ler
`UPDATE_BEHAVIOR` — que é prosa, com 172 «NÃO SEI» nos 186. Sem `RECOLLECTION`
declarado, tudo cai em `UNKNOWN`, e `UNKNOWN` significa `SKIP`. Consequência: a
**ARPAV**, que republica o **mesmo** endereço `agro_01.pdf` a cada edição,
deixaria de ser revisitada **para sempre**.

```
SALTAR É POUPAR REDE. SALTAR O QUE MUDA É CEGAR A CASA.
```

A correcção não foi mexer nos testes. Foi traduzir, à mão e com a prova citada
dentro de cada declaração, o que cada contrato já dizia em prosa:

| fonte | `UPDATE_BEHAVIOR` | `DETAIL_CONTENT` |
|---|---|---|
| IT-T3-005 | SOBRESCRITA — uma edição por vez | `MUTABLE` |
| IT-T2-002 | SOBRESCRITA (nome do ficheiro é FIXO) | `MUTABLE` |
| IT-T2-004 | SOBRESCRITA — janela móvel na mesma URL | `MUTABLE` |
| IT-T3-002 | ADITIVO — cada edição ganha arquivo próprio | `IMMUTABLE` |
| IT-T3-010 | ADITIVO | `IMMUTABLE` |
| IT-T3-008 | ADITIVO | `IMMUTABLE` |
| IT-T4-001 | ADITIVO por data de arquivo | `IMMUTABLE` |

As 6 falhas desapareceram, e desapareceram pela razão certa: a ARPAV volta a
ser revisitada, agora **com razão nomeada**, e o normalizador impede que a
revisita escreva um `CHANGED_IN_PLACE` falso.

> **DÍVIDA DECLARADA, e é importante.** Restam **179 de 186** contratos sem
> `RECOLLECTION`. Para esses, um detalhe já colhido **não será revisitado**.
> Isto está certo para quem publica cada edição num endereço novo, e está
> **errado** para quem reescreve o mesmo. Antes de qualquer colheita grande,
> esta tradução tem de ser feita fonte a fonte — ou a colheita fica cega às
> fontes que sobrescrevem.

---

## FASES 10–11 · OPS E CANÁRIO

Instalado **só depois** de o replay offline passar. Merge `--no-ff` de
`paridade-v1` para `ops/cutover-prod-v1`, que acrescenta e não reverte.

**O que NÃO se desfez**, conferido: agendador canónico (janela das 20h em
Europe/Rome, a tratar as horas fora da janela como `SKIPPED_OUT_OF_WINDOW`),
`curadoria/collection_gate.py` como dono único da população, lista fixa
continua removida do perfil, rollback e guardas de vazamento intactos.

```
CUTOVER_NAO_VAZA = YES
  CAPABILITY_BLOCK_LEAK  0      HUMAN_REVIEW_LEAK  0
  POLICY_BLOCK_LEAK      0      READY_LEGACY_LEAK  0
```

Presença não é rota — por isso as provas de comportamento correram **na ops**,
não só no laboratório: 31/31 e 13/13.

### Egresso, medido antes e depois, com dois medidores

```
ANTES   ipinfo.io   146.70.182.38  IT  Milan      ifconfig.co  146.70.182.38  IT
DEPOIS  ipinfo.io   146.70.182.38  IT             ifconfig.co  146.70.182.38  IT
ESPERADO = IT   ·   OBTIDO = IT   ·   os dois medidores concordam
```

### As mesmas 2 fontes, duas passagens

`IT-T10-018` e `IT-T10-022`, escolhidas pela mesma regra de sempre
(`--canario-limite 2`, os N primeiros por ordem alfabética dos elegíveis com
contrato — corta o **tamanho** da população, nunca escolhe quais).

```
                        RUN1        RUN2
                    b89c95      a3c3bb
  INDEX_REQUESTS         2           2
  DETAIL_REQUESTS        0           0
  NEW_DOCUMENTS          0           0
  CHANGED_IN_PLACE       0           0
  SEEN_AGAIN             0           0
  SKIPPED_KNOWN         39          39
  REVALIDATED            0           0
  UNNECESSARY_REFETCHES  0           0
  RAW_OBJECTS_CREATED    0           0
  linhas novas no livro  0           0
```

**Comparação com as mesmas duas fontes antes da correcção:**

```
                     ANTES 0d088d   ANTES 8be761   DEPOIS b89c95   DEPOIS a3c3bb
  DETAIL_REQUESTS         32             39              0               0
  CHANGED_IN_PLACE        32             39              0               0
  RAW_OBJECTS_CREATED     32             39              0               0
```

---

## FASES 12–13 · O GATE É O DESPERDÍCIO, NÃO O ZERO

```
UNNECESSARY_REFETCHES = 0        ← o gate
```

**`RUN2_DETAIL_REQUESTS = 0` não foi decretado.** Deu zero, e a razão é
verificável: o índice devolveu 39 endereços nas duas passagens, os 39 já
estavam no livro com documento, e nenhuma das duas fontes declara
`RECOLLECTION` — portanto nenhuma tinha razão canónica para revalidar. Se um
artigo novo tivesse aparecido, teria sido `DETAIL_NEW` e teria sido buscado.

```
REASON de cada pedido da RUN2:  não há pedidos, logo não há razões a justificar.
                                O gate passa por ausência, e diz-se assim.
```

```
FALSE_DOCUMENT_CHANGED_IN_PLACE = 0
```

Nenhum `DOCUMENT_CHANGED_IN_PLACE` foi escrito nas duas passagens, por isso a
exigência de `OLD/NEW_NORMALIZED_HASH` + `MATERIAL_DIFF` não teve a quem se
aplicar. Que ela funciona **quando se aplica** está provado offline, com o livro
inspeccionado linha a linha: `MATERIAL_DIFF=false` no volátil, `true` na matéria
mudada, e hashes normalizados a bater e a divergir nos casos certos.

> **O que esta corrida NÃO prova, e é preciso dizer.** Como `IT-T10-018` e
> `IT-T10-022` têm `UPDATE_BEHAVIOR = "NAO SEI"`, um artigo **editado** num
> endereço já conhecido não seria visto hoje. Antes desta correcção também não
> seria: o coletor chamava *tudo* de `CHANGED_IN_PLACE`, e um detector que
> dispara sempre não detecta nada. A diferença é que agora o silêncio é uma
> decisão declarada, com o nome do que falta — `RECOLLECTION` nessas duas
> fontes — em vez de ruído a passar por notícia.

---

## FASES 14–15 · KNOW-HOW E MAPA

```
KNOW_HOW_DELTA = §166 · A PEÇA CERTA, NO SÍTIO CERTO, QUE NINGUÉM CHAMA
                 secção NOVA, +10 340 bytes, zero linhas apagadas
```

Número conferido livre neste ficheiro **e em todas as branches** antes de
escrever, como `§165` manda. As oito lições, todas pedidas no briefing e todas
medidas nesta missão:

1. lab PASS não prova ops PASS
2. o cutover testa comportamento, não presença de ficheiros
3. pre-fetch skip ≠ normalização — duas defesas, nenhuma chega sozinha
4. volátil não é `CHANGED_IN_PLACE` — e a nossa visita **é** o volátil
5. alargar uma regra até o vermelho desaparecer é apagar o termómetro
6. a segunda corrida do canário é gate obrigatório antes da Big Collection
7. saltar é poupar rede; saltar o que muda é cegar a casa
8. o ataque que não toca no caminho da bancada não é um ataque

### Mapa

A rota mudou — o coletor passou a importar duas peças que antes não chamava —
portanto o mapa mudou.

```
C-IT-NORMALIZACAO      Z-REGRAS  engine   regras/normalizacao_de_conteudo.mjs
                                          regras/paridade_test.mjs
C-PROVA-PARIDADE       Z-PROVA   proof    provas/paridade_duas_rodadas.mjs
                                          provas/paridade_red_team.mjs
                                          provas/PARIDADE-RED-TEAM-V1.json
C-LASTMILE-MEDIDORES            + medidas/paridade_replay.mjs
                                + medidas/PARIDADE-REPLAY-V1.json
```

O red team mudou de `medidas/` para `provas/` porque a gaveta da peça é uma só
e ele é uma prova, não um medidor — o cartão dos medidores declara «medidores
que só LEEM» e um red team escreve para atacar.

```
SYSTEM_MAP_CHECK = PASS       (laboratório e ops)
IMPRESSAO_DO_CARIMBO = IGUAL
```

---

## CRITÉRIO

```
CANARY_RUN2_INCREMENTAL           = YES
UNNECESSARY_REFETCHES             = 0
FALSE_DOCUMENT_CHANGED_IN_PLACE   = 0
LEAKS                             = 0
NEW_FAILURES                      = 0
RED_TEAM_SURVIVORS                = 0
SYSTEM_MAP_CHECK                  = PASS
ÁRVORE LIMPA                      = sim  (laboratório e ops)
LOCAL == REMOTE                   = ver nota de fecho
```

```
CUTOVER_PROVEN        = YES
BIG_COLLECTION_ALLOWED = YES     ← DECLARADO. NÃO EXECUTADO.
```

⚠️ **E com uma condição que tem de ir junto com a autorização:** a Big
Collection toca fontes muito para além das 7 com `RECOLLECTION` declarado. Para
as outras 179, um documento já colhido não será revisitado. Isso está certo
para quem publica cada edição num endereço novo e **errado** para quem
sobrescreve. A autorização é sobre o comportamento de incrementalidade estar
provado; **não** é um certificado de que as 186 fontes estão bem declaradas.

---

## EM PALAVRAS SIMPLES

**Porque é que a bancada funcionava e a produção não.**
Imagine uma regra escrita num papel pregado na parede: *«antes de ires à loja,
olha primeiro no armário»*. O papel estava pregado na parede da bancada e na
parede da produção, igualzinho, letra por letra. Mas na produção **ninguém
lia** o papel. Na bancada, quem testava lia o papel em voz alta antes de cada
ensaio — e por isso o ensaio dava sempre certo.

**Onde estava a diferença.**
Não estava em nenhum ficheiro. Os ficheiros eram idênticos, e nós conferimos
isso com uma impressão digital de cada um. A diferença era uma **chamada em
falta**: o programa que vai à internet buscar as páginas nunca perguntava à
regra se devia ir. Ele ia, descarregava, e **só depois** perguntava «isto eu já
tinha?». Já tinha gasto a viagem para descobrir que não precisava dela.

**Se o contador de visitas era mesmo a causa.**
Era — e não estava sozinho. Pegámos nas páginas guardadas das duas visitas e
comparámo-las palavra a palavra. **Das 32 páginas que apareciam nas duas
visitas, 32 tinham mudado por fora e ZERO tinham mudado por dentro.** Em 23
delas nem o tamanho mudou: o mesmo número de letras, tudo igual, só uns códigos
a trocar.

Seis coisas mexiam. Duas delas **somos nós**:

- o contador de visitas da página: `134` passou a `135`, `604` passou a `606`.
  Subiu porque **fomos nós olhar**.
- um carimbo que diz *«modificado às…»* e que traz, na verdade, a hora a que
  **nós** batemos à porta — um segundo antes do nosso próprio relógio.

As outras quatro eram códigos de segurança do site, um anúncio que roda a cada
visita, e um cronómetro do próprio servidor.

**O que foi ligado.**
Duas coisas, e as duas são precisas:

1. **Perguntar antes de ir.** Agora o programa pergunta à regra *«já tenho
   isto?»* **antes** de bater à porta. Se já tem e não há razão escrita para
   voltar, não vai.
2. **Limpar o ruído antes de comparar.** Quando é preciso voltar mesmo — e há
   casos em que é —, o programa tira os seis pedaços que já sabemos que mexem
   sozinhos e só depois compara. Assim deixa de escrever «este documento
   mudou» quando o único que mudou fomos nós.

**Pedidos da 1ª e da 2ª corrida, e quantos eram precisos.**

```
                    ANTES da correcção      DEPOIS da correcção
1ª corrida               32 páginas               0 páginas
2ª corrida               39 páginas               0 páginas
```

Em ambas as corridas de agora, o programa foi buscar **2 listas** (a lista de
notícias de cada um dos dois sites) e **nenhuma página de detalhe**. As 39
páginas que a lista anunciava já estavam todas guardadas em casa.

**Eram precisos?** Nenhum. Zero desperdício. E a lista continua a ser pedida
sempre — é ela que avisa se há notícia nova.

**Se ainda houve página igual descarregada.** Não. Nenhuma. Zero.

**Se conteúdo novo continua a ser detectado.** Sim, e há duas partes nisto, e a
segunda é a ressalva honesta:

- **Notícia nova**: sim, sem dúvida. A lista de cada site é lida em todas as
  corridas, e qualquer endereço que apareça lá e não esteja em casa é buscado.
  Testámos isso.
- **Notícia velha que foi corrigida depois**: hoje **não veríamos**, nestes dois
  sites. Porquê: só voltamos a uma página que já temos se alguém tiver escrito
  no papel da fonte que «esta página é reescrita». Nestes dois sites esse papel
  diz «não sei», e «não sei» não autoriza gastar viagem. **Antes da correcção
  também não víamos** — porque o programa gritava «mudou!» em todas as páginas,
  e um alarme que toca sempre não avisa de nada. A diferença é que agora o
  silêncio tem nome e está escrito.

Encontrámos este risco a sério a meio do trabalho, e ele quase passava
despercebido: há uma fonte italiana, a ARPAV, que **reescreve o mesmo endereço**
a cada boletim novo. Se tivéssemos deixado como estava, essa fonte nunca mais
seria visitada. Seis testes ficaram vermelhos a avisar. Fomos aos papéis dessas
fontes, lemos o que já lá estava escrito em português corrido, e passámos a
escrevê-lo numa forma que o programa consegue ler — sete fontes, uma a uma, com
a prova ao lado. **Faltam 179.**

**Se a Big Collection está autorizada.**
Sim — `BIG_COLLECTION_ALLOWED = YES`. **Declarado, e não executado**, como a
missão manda. Mas com um aviso que não deve ficar de fora da decisão: a Big
Collection vai a muitas mais fontes do que estas sete. Para as outras 179,
ainda não escrevemos no papel se elas reescrevem a mesma morada ou não. O que
está provado é que o mecanismo funciona e já não desperdiça. O que **não** está
provado é que todas as fontes estão bem descritas.

---

```
HARD STOP CUMPRIDO
Big Collection NÃO iniciada · Intelligence não tocada · Portal não tocado
Source Curator não alterado
```
