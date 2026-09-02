# Fechar o handoff antes da importação — `CAPTURE ≠ REGISTRATION`

`2026-08-30` · **Nada importado.** Nenhuma migration aplicada em produção, catálogo não
importado, handoff não mesclado, Supabase de produção intocado. Tudo em Postgres 16
descartável.

**Veredito: `HANDOFF_READY_TO_IMPORT`** — e READY não autoriza importar.

---

## A · HEAD / branch / push

| | |
|---|---|
| Branch | `claude/sintonia-eame-collection-es` |
| HEAD de entrada | `d07e19b` · árvore limpa |
| Handoff auditado | `origin/claude/adama-es-local-browser` @ `0a799f5` · **não mesclado** |
| Catálogo do handoff | lido do ref para provar ordem. **Ler não é mesclar** — o arquivo não entra nesta branch |

## B · Contrato `CAPTURE` vs `REGISTRATION`

Escrito **antes** da implementação, em `data/samples/CAPTURE-VS-REGISTRATION-CONTRACT-V1.json`.

| papel | o que é | quantas existem |
|---|---|---|
| **REGISTRATION** | a autorização concedida por um Estado | uma por `(pais, registration_id)`, para sempre |
| **CAPTURE** | uma observação dela, numa fonte, num instante | quantas vezes olharmos |

```
IDENTITY KEY   (pais, registration_id)
CAPTURE KEY    (pais, registration_id, fonte, fonte_versao)
```

A chave de captura de 006 era `(pais, registration_id, fonte_versao)` e **omitia `fonte`**:
duas fontes que escrevessem a mesma string de versão se sobrescreveriam em silêncio.
Nenhuma captura de hoje cai nesse caso — todas vêm do MAPA ROPF — mas a trava é sobre o
que pode entrar amanhã. Corrigida na 013.

### CURRENT-AS-OF SELECTION RULE

1. **Elegibilidade** — `capturado_em <= as_of`. Não se responde uma pergunta de abril com
   evidência de agosto.
2. **Ordem** — maior `SOURCE_INSTANT` (`fonte_versao` lida como timestamp): o que o
   registro disse por último. Quando não é um timestamp válido, **não ordena** — cai para
   o desempate em vez de virar palpite.
3. **TIE BREAK 1** — maior `capturado_em`.
4. **TIE BREAK 2** — maior `id`. Os três juntos são totais: empate é impossível.

**SOURCE PRIORITY não existe**, e não foi inventada. Toda captura vem da mesma fonte hoje.
Quando duas fontes convivirem, a seleção continua determinística **e** a linha marca
`conflito_de_fonte = true` com as fontes nomeadas. A ambiguidade fica visível em vez de
resolvida no escuro.

`registro_regulatorio` **continua sendo um log** e ganhou o comentário que diz isso.
`v_product_registered_windows` **continua devolvendo todas as capturas** — é o histórico, e
o histórico não mente.

## C · A regra de `AS_OF_DATE`

Duas capturas do mesmo registro, em datas diferentes, dizendo coisas diferentes
(`supabase/ensaios/CAPTURA-AS-OF-DUAS-CAPTURAS.sql`):

| pergunta | captura usada | `fecha_caducidad` | capturas disponíveis |
|---|---|---|---|
| `as_of 2026-02-01` | **nenhuma** | — | 0 |
| `as_of 2026-04-23` | A · 10/03 | 2027-06-30 | 1 |
| `as_of 2026-06-19` | A · 10/03 | 2027-06-30 | 1 |
| `as_of 2026-06-20` | B · 20/06 | 2026-05-31 | 2 |
| `as_of 2026-08-30` | B · 20/06 | 2026-05-31 | 2 |

`FUTURE_CAPTURE_CANNOT_REWRITE_PAST_STATE`: B está na tabela e a pergunta de abril continua
respondendo abril. E antes da primeira captura **não há linha nenhuma** — ausência de
evidência é ausência de linha, nunca uma linha inventada.

## D · NEPTUNE — antes e depois, medidos na mesma execução

A rodada anterior mediu "3 ocorrências" com uma fixture que mudou desde então. Um número
de antes/depois que só existe em dois relatórios não é prova, então a condição original é
**remontada dentro de uma transação desfeita** e as duas leituras são feitas lado a lado:

| leitura | janelas do NEPTUNE |
|---|---|
| `v_product_registered_windows` (o log) | **3** |
| `f_product_registered_windows` (corrente em `as_of`) | **2** |

### A decomposição honesta

Das 3, **uma** vinha da captura antiga e some com a 013. As outras duas eram **duas linhas
de janela da mesma captura** — e a segunda só existia porque o importador criava uma linha
para *"a ficha não publica timing"*.

Essa terceira sai por uma **regra de importação**, não pela 013: só nasce
`registro_uso_janela` quando a fonte publica ao menos um de
`{timing, dose, BBCH, prazo de segurança, nº de aplicações}`. É a mesma lei que a migration
do catálogo já escreve para a janela dela. Com as duas correções, o caso mostra o NEPTUNE
**uma vez**.

Atribuir `3 → 1` a um conserto só daria à 013 crédito que não é dele.

## E · Histórico preservado

```
HISTORY_ROWS        > REGISTROS_DISTINTOS     log 10 linhas / 8 registros
CURRENT_STATE_ROWS  = 1 por registro          0 duplicados no estado corrente
JANELAS_NO_LOG      > JANELAS_CORRENTES       10 / 9
```

As duas coisas ao mesmo tempo. Resolver a duplicação apagando captura teria trocado um
defeito por um pior: o portal pararia de poder responder *"o que o registro dizia em abril"*.

### O defeito que a correção quase introduziu

A primeira versão lia os usos direto da captura corrente. A regressão 06 pegou: inserir uma
captura nova que observou só o cabeçalho do registro fazia o **produto desaparecer** do
caso. Sumir é pior que duplicar, porque duplicar se vê.

O modelo final separa as duas coisas: **o estado vem da captura corrente; os usos vêm da
captura mais recente que de fato observou usos.** Quando as duas não são a mesma, a linha
diz isso em `uses_from_a_different_capture` — em vez de resolver calado.

## F · RT-11 · a origem estrutural de `MALAS HIERBAS`

**Causa medida, no código do coletor:** `ISSUE_RELATIONS` nasce de `_tokens(texto_todo)` —
varredura sobre a **página inteira**. Para cultivo o coletor confere contra o bloco
`Cultivos` que a ADAMA declara; **para alvo esse bloco não existe na fonte**, então nenhuma
linha de alvo tem origem declarada.

### A leitura da rodada passada estava com o denominador errado

Eu disse *"assinatura de menu do site"* contando **25 produtos não-herbicida**. A medição
correta é mais forte: a família de termos de erva daninha aparece em **56 de 56 produtos**.
O termo literal `MALAS HIERBAS` aparece em 46 — os outros 10 têm um termo mais específico
(`Dicotiledóneas, malas hierbas de hoja ancha`) que o absorve em `_colapsar_sobrepostos`.
Todos os 10 são desses. **Um termo presente para todo produto não discrimina produto nenhum.**

O elemento exato da página não é determinável a partir do Git — o HTML bruto não está
versionado. O que está provado é o suficiente para decidir: a origem é varredura de texto,
e o termo cobre 100% do catálogo.

### A correção não é blacklist, é origem

| origem | linhas | pode virar alvo autorizado |
|---|---|---|
| `PAIR_TABLE_ROW` — linha de tabela ancorada que nomeia cultivo **e** agente | **5** | **sim** |
| `PAGE_BODY_TEXT` — varredura de texto | **176** | não |

`scripts/adama_es_import_rules.py`. O mesmo termo entra ou não conforme a **âncora**, nunca
conforme a palavra: `MALAS HIERBAS` numa linha de tabela do TRINITY é alvo legítimo; a mesma
string solta na página do NEPTUNE não é.

**Não copiei o schema de cultivo por simetria.** `DECLARADO/CITADO` existe para cultivo
porque a página *tem* o bloco. Para alvo o bloco não existe — inventar a origem seria pior
que não ter.

## G · RT-6 · BBCH

**Causa medida, no coletor:**

```python
def _bbch(t):
    m = BBCH.search(t or '')                      # só a PRIMEIRA ocorrência
    return (m.group(1), m.group(2) or m.group(1)) # sem separador, TO = FROM
```

Dois defeitos somados: a regex só entende `BBCH 12-29`, e quando não há segundo número o
código **deriva o fim do início**. Num texto que diz *"desde BBCH 00 (semilla seca) hasta
BBCH 07"* isso produz `00–00`.

| cultura | RAW TEXT | handoff | regra nova |
|---|---|---|---|
| ARROZ | *"Aplicar durante BBCH 12-29."* | 12–29 | **12–29** `FAIXA_COM_TRACO` |
| CEBADA | *"…desde BBCH 00 (semilla seca) hasta BBCH 07…"* | **00–00** | **0–7** `FAIXA_POR_LINGUAGEM:desde…hasta` |
| TRIGO | idem | **00–00** | **0–7** idem |

A regra **nunca deriva o fim a partir do início**. Faixa fechada só com traço ou com
linguagem que ligue duas menções; ponta aberta (*"a partir de BBCH 30"*) vira `APPROXIMATE`
com o texto inteiro; duas menções sem linguagem que as ligue também. Estádio único legítimo
(`BBCH 65–65`) continua possível — mas só com linguagem pontual.

Regressões com os textos **literais** da fonte, mais os casos sem exemplo na fonte
(marcados como tal). **Mutação:** o parser antigo reinstalado produz `(0, 0)` e a regressão
reprova.

## H · RT-10 · CUPROXI FLO — não reconciliado, **modelado**

| hipótese | veredito | evidência |
|---|---|---|
| **A** dois sistemas de identificador | parcial | o ROPF usa as duas formas: 62 numéricas e 34 `ES-nnnnn` entre os 96 vigentes. Não explica este caso |
| **B** um é id interno | **refutada** | a página publica *"Nº de registro: 19232"*, e o mesmo campo casa com o ROPF em **43 dos 56** produtos |
| **C** erro de extração | **refutada** | o texto literal está preservado e diz 19232 |
| **D** entidades distintas com o mesmo nome | **não refutada** | a composição bate exatamente com a do ES-00979 — improvável, mas improvável não é refutado |
| **E** `NÃO SEI` | **é a resposta** | 19232 não está entre os 96 vigentes capturados, e os **92 registros ADAMA cancelados não foram capturados** |

Dois identificadores **tipados**, cada um com sua fonte e sua data:

```
REGISTRATION_ID_PUBLISHED_BY_MANUFACTURER = 19232      página ADAMA · 2026-08-30
REGISTRATION_ID_IN_OFFICIAL_REGISTER      = ES-00979   MAPA ROPF   · 2026-08-29
LINK_BASIS  = NAME_AND_COMPOSITION
LINK_STATE  = PLAUSIBLE_NOT_PROVED
```

`NOME IGUAL ≠ MESMO REGISTRO`. O casamento canônico é **sempre** pelo número do registro
oficial. Nenhuma consulta usa nome comercial como chave.

**O que fecharia:** consultar o ROPF por 19232 **incluindo cancelados** — uma requisição,
não executada nesta rodada.

## I · Ordem final das migrations

Mapeada, não renumerada às cegas:

```
001–007   fundação, identidade, conteúdo, par, camada analítica, regulatório, views
009       semântica de país
010–012   os quatro relógios
013       CAPTURE != REGISTRATION          ← novo, com incompatibilidade provada
014       catálogo público do fabricante   ← o 010 do handoff, renumerado
008       verificação, por último          ← ela confere, não cria
```

A 013 fica **com o motor**, não depois do catálogo: a segunda captura pode chegar de
qualquer fonte, e a trava tem de existir antes. O catálogo é `014` e **não entra nesta
branch** — foi lido do ref para provar a ordem.

A colisão de número era mecânica: as 15 tabelas do catálogo se chamam `catalogo_*` e
nenhuma colide com as quatro do calendário.

## J · Banco do zero

```
MIGRATION_001..007, 009..014 = PASS
008 (verificação, por último) = PASS · 30 tabelas, travas, funções e RLS
FIXTURE_ES = PASS · ENSAIO_CINCO = PASS · ENSAIO_ASOF = PASS
regressoes_calendario.sql = 45/45
regressoes_captura.sql    = 19/19
```

As 45 do calendário agora passam **com as duas camadas juntas** — exatamente o que a rodada
anterior não conseguia. Era o C-7.

A 008 foi estendida para conferir a 013 e testada por mutação: removida
`f_registro_corrente`, ela reprova nomeando a função que sumiu.

## K · Os cinco fixtures

| caso | produto | estado | escopo | some ao perguntar por alvo? |
|---|---|---|---|---|
| A · cultura + alvo + janela | POSTSCRIPT 80 · arroz | NOT_KNOWN | ISSUE_LEVEL | não |
| B · nível cultura, sem alvo | ORDAGO CAPS · amendoeira | NOT_KNOWN | **CROP_LEVEL** | não |
| C · validade vencida | NEPTUNE + CUPROXI FLO · olivo | ACTIVE, NOT_KNOWN | ISSUE_LEVEL | não |
| D · temporalidade aproximada | TRINITY · cevada | NOT_KNOWN | ISSUE_LEVEL | não |
| E · dado ausente | TRINITY · centeio | NOT_KNOWN | ISSUE_LEVEL | não |

## L · Red team — as dez hipóteses de §11

| # | hipótese | onde está a regressão | resultado |
|---|---|---|---|
| 1 | segunda captura duplica produto | `regressoes_captura` 06, 07 | derrubada |
| 2 | captura futura altera resposta passada | 03, 03b, 03c, 03d, 03e | derrubada |
| 3 | menu vira issue | `test_adama_es_import_rules` | derrubada |
| 4 | BBCH range encolhe | idem, com mutação | derrubada |
| 5 | nome comercial reconcilia IDs | `test_adama_es_gate` · RT-10 | derrubada |
| 6 | absence vira `NOT_REGISTERED` | `test_adama_es_gate` | derrubada |
| 7 | crop-level desaparece | ensaio dos cinco casos, caso B | derrubada |
| 8 | expiry vira withdrawal | `regressoes_calendario` 16 | derrubada |
| 9 | APPROXIMATE vira data | `regressoes_calendario` 12b | derrubada |
| 10 | history apagado para produzir current | `regressoes_captura` 01, 01b, 09 | derrubada |

## M · Mutações

| mutação | o que reprova |
|---|---|
| parser antigo `search()` + `group(2) or group(1)` reinstalado | produz `(0,0)` e a regressão do BBCH reprova |
| `pode_virar_alvo_autorizado` aceitando `PAGE_BODY_TEXT` | `MALAS HIERBAS` entraria para um fungicida |
| `f_registro_corrente` removida | a 008 reprova nomeando a função |
| captura nova sem usos | pegou o defeito de desaparecimento antes de ele existir em produção |
| 10 mutações do red team do portão | todas pegaram |

## N · ES-CASE-001 — **ABERTA**

Nenhuma das quatro correções a fechou, e foi conferido de propósito.

| | |
|---|---|
| janelas do NEPTUNE no handoff | 0 |
| pares olivo × repilo do NEPTUNE | 0 |
| citações de "floración" | 9 |
| citações que **servem** como evidência | **0** |

As 9 estão em `AMBIGUOUS_TERMS` e são rótulos de **uso** (*"Inhibición floración"*). O PDF
local do NEPTUNE **não foi usado** — ele está fora do fluxo preservado. Nenhuma fenologia
foi inferida.

## O · Estado do RAW gate, recebido da máquina local — só informação

| | |
|---|---|
| `SUPABASE_AUTH_AVAILABLE` | **NO** |
| `MIGRATIONS_APPLIED` · `TABLES` · `RAW_BUCKET_EXISTS` | **NOT_MEASURED** |
| `RAW_ASSETS_EXPECTED` | 196 (138 PDFs + 56 páginas + 2 pacotes) |
| `BYTES_LOCAIS` | 304.482.907 |
| `PROBLEMAS_ANTES_DE_ENVIAR` | 0 — hash de cada arquivo reconferido |

Frente paralela. **Nada nesta rodada dependeu dela**: tudo o que foi corrigido é lógica
provável em banco descartável.

## P · Veredito

```
C-7          RESOLVED
RT-11        RESOLVED
RT-6         RESOLVED
RT-10        MODELADO_SEM_AMBIGUIDADE
ES-CASE-001  OPEN
regressões   574 Python + 45 calendário + 19 captura = todas verdes

HANDOFF_READY_TO_IMPORT
```

**READY não autoriza importar.** Significa que a integração futura não muda o significado —
não que ela aconteceu. Nada foi importado, nada foi aplicado no Supabase, o handoff continua
não mesclado.

Parar aqui era a instrução, e é o que está sendo feito.

## O que continua NÃO SEI

Qual dos dois números o Estado reconhece para o CUPROXI FLO · qual elemento exato da página
gera `malas hierbas` · se o NEPTUNE estava dentro ou fora da janela em agosto · se os 12
produtos só-site têm registro cancelado, de outro titular, ou grafia não alcançada.
