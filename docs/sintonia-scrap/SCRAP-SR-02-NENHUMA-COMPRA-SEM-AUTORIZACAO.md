# SCRAP-SR-02 · NENHUMA COMPRA SEM AUTORIZAÇÃO

> **Pergunta da missão:** existe hoje alguma forma de criar uma execução paga sem
> passar por uma autorização explícita e válida para aquele gasto?
>
> **Resposta medida:** **existia**, e nenhum dos caminhos precisava de autorização
> nenhuma: bastava o token estar presente e o orçamento ter saldo. Agora não
> existe, e o que fecha não é um aviso — é uma guarda no único sítio da árvore que
> cria execução paga.

**Missão:** `SCRAP-SR-02` · **Ramo:** `claude/festive-fermi-1k2mf5`
**Âmbito:** SINTONIA SCRAP, e só ele.
**Gasto desta missão:** `APIFY_REAL_RUNS = 0` · `OTHER_PAID_REAL_RUNS = 0` ·
`PROVIDER_START_POSTS_REAL = 0` · `COST_USD = 0`

---

## A · O QUE SE PERGUNTOU, E O QUE ESTAVA LÁ

Antes desta missão, criar uma execução paga precisava de três coisas, e **nenhuma
delas era uma autorização de gasto**:

| o que a casa exigia | o que isso responde | o que isso **não** responde |
|---|---|---|
| um token no ambiente | *conseguimos pagar?* | *este gasto foi autorizado?* |
| um orçamento com saldo | *quanto se pode gastar?* | *se este gasto foi autorizado* |
| uma rota `ALLOWED`/`CONDICIONAL` | *esta técnica é lícita?* | *se esta compra foi autorizada* |

```
    TOKEN_PRESENT   != SPEND_AUTHORIZED
    CREDENTIAL      != AUTHORIZATION
    BUDGET_PRESENT  != SPEND_AUTHORIZED
    ROUTE_ALLOWED   != SPEND_AUTHORIZED
```

Um orçamento diz **quanto**. Uma autorização diz **se**. A casa tinha o primeiro
e não tinha o segundo — e um teto sem autorização é um limite de crédito sem
dono da decisão.

### A superfície, medida

| medida | valor | como se mediu |
|---|---|---|
| workflows com token Apify | **6** | `grep -rl APIFY_TOKEN .github/workflows/` |
| ficheiros que importam `coletor` | **15** | AST: `Import`/`ImportFrom` |
| ficheiros que chamam a porta paga directamente | **8** | AST: `ct.executar(...)` |
| sítios que **criam** execução paga | **1** | AST: `ast.Call` com `metodo='POST'` |

A última linha é a que decide a arquitetura desta missão, e ela foi medida errada
primeiro: `grep` devolveu **3** — um real, um comentário de teste e uma linha de
docstring. A contagem que vale anda na árvore sintáctica, não no texto.

```
    GREP CONTA TEXTO. AST CONTA CÓDIGO.
```

Os oito que chamam a porta directamente são
`coleta/adaptador_youtube.py` · `coleta/comunicacao_coleta.py` ·
`coleta/instagram_coleta.py` · `regras/sensor_coleta.py` e quatro suites de
prova. Mais os que chegam lá **indirectamente**, por adaptador — e é por isso que
contar chamadores não fecha o buraco: contar **criadores** fecha.

---

## B · ONDE A TRAVA FOI POSTA, E POR QUE NÃO NO ORQUESTRADOR

A FASE 6 pedia `AFTER_TOTAL = 0`: nenhum caminho pago sem autorização. O modo
óbvio era migrar todos os chamadores para o orquestrador canónico e pôr o portão
lá. Isso seria quinze migrações para fechar um buraco — e, enquanto a última não
aterrasse, o buraco continuava aberto.

`coleta/coletor.py` carrega o **único** `metodo='POST'` da árvore. Então:

```
    A TRAVA VIVE ONDE A COMPRA NASCE, NUNCA ONDE ELA SE PEDE.
    SPEND ENFORCEMENT != CANONICAL ORCHESTRATION.
```

Uma guarda nesse sítio fecha **todos** os caminhos de uma vez — directos e
indirectos, presentes e futuros — sem migrar nada. E as duas coisas ficam
separadas de propósito: a orquestração canónica continua a ser uma dívida por
pagar, e passa a ser uma dívida de *arrumação* — já não é o que mantém o buraco
aberto.

### A ordem é a prova

```
coleta/coletor.py :: executar
  linha 625   ag.exigir(...)                 ← A AUTORIZAÇÃO
  linha 630   orcamento_financeiro_actual()  ← o gate financeiro
  linha 645   _curl(..., metodo='POST')      ← a compra
```

Ela vem antes da **reserva**, não só antes do POST: reservar saldo para uma
compra que ninguém autorizou já compromete dinheiro por uma decisão que não
existe.

```
    UMA GUARDA LIDA DEPOIS DA COMPRA NÃO É UMA GUARDA. É UMA LEGENDA.
    UMA GUARDA LIDA DEPOIS DA RESERVA JÁ GASTOU O QUE IA RECUSAR.
```

---

## C · A LEI · `leis/autorizacao_de_gasto.py`

**498 linhas. Contrato `AUTORIZACAO_DE_GASTO/v1`.**

Ela **não calcula relevância e não sabe calculá-la.** Verifica quatro coisas:

1. que uma autorização explícita veio junto (ambiente `threading.local`, nunca
   um argumento que se esqueça);
2. que ela é do **PAR exacto** `(SOURCE_ID, PROPOSITO)` que se vai colher;
3. que os tetos declarados nela cobrem **esta** chamada;
4. que o modo é um dos três, e que nenhum se veste de outro.

### Os três modos, e eles não se substituem

| modo | para quê | exige humano | exige fonte |
|---|---|---|---|
| `NORMAL_COLLECTION` | colher fonte **já avaliada** que serve | não¹ | sim |
| `SOURCE_EVALUATION_PROBE` | amostra pequena de fonte **ainda não avaliada** | **sim** | sim |
| `CAPABILITY_TRIAL` | medir se um provider/rota **consegue** | **sim** | não² |

¹ a decisão que o autoriza já é humana por construção: vem do livro de
relevância, que gente escreve.
² um trial mede o provider, não a fonte — fingir uma fonte para um trial seria
fabricar um par que ninguém avaliou. Em troca, exige `ALVO`.

O `PROBE` existe por necessidade lógica, não por conveniência:

```
    UM PORTÃO QUE EXIGE A RESPOSTA PARA DEIXAR FAZER A PERGUNTA
    NÃO É UM PORTÃO. É UM MURO.
```

Sem ele, uma fonte nunca avaliada nunca poderia ser amostrada, e sem amostra
ninguém a avalia. E a outra metade, que é o que o torna seguro:

```
    PROBE != DECISION.
```

Depois de um probe a fonte continua `NAO_AVALIADA` até o dono da relevância
escrever no livro dele. `AUTO_PROMOTION` está na lista `NAO_CRIAR`, e a prova é
estrutural: a lei **não tem nenhuma chamada de escrita** — nem `open`, nem
`dump`, nem `gravar`. Verificado por AST, não por leitura.

### O `TRIAL` desta lei não é o `TRIAL` do executor

`scrap_executor.TRIAL` é um eixo **epistemológico** — «vou medir se consigo, e
não espero resultado» — e o próprio ficheiro dele escreve `TRIAL NÃO AUTORIZA
GASTO`. Continua a não autorizar.

```
    MODO EPISTEMOLÓGICO != AUTORIZAÇÃO DE GASTO.
```

### Dezasseis recusas, cada uma com o seu nome

`SEM_AUTORIZACAO` · `MODO_DESCONHECIDO` · `SOURCE_ID_AUSENTE` ·
`SOURCE_ID_INVALIDO` · `AUTORIZACAO_DE_OUTRA_FONTE` · `PROPOSITO_AUSENTE` ·
`AUTORIZACAO_DE_OUTRO_PROPOSITO` · `RELEVANCE_RESULT_AUSENTE` ·
`RELEVANCE_RESULT_NAO_AUTORIZA` · `RELEVANCE_VERDICT_NAO_AUTORIZA` ·
`AUTORIZACAO_HUMANA_AUSENTE` · `TETO_AUSENTE` · `TETO_ESTOURADO` ·
`TETO_ACIMA_DO_AUTORIZADO` · `ALVO_AUSENTE` · `DONO_DA_RELEVANCIA_AUSENTE`

Um `NOT_RELEVANT` para tudo transformaria várias ausências diferentes num
julgamento que ninguém fez.

```
    AUSÊNCIA DE AUTORIZAÇÃO CONTINUA A SER AUSÊNCIA DE AUTORIZAÇÃO.
```

### Quatro tetos, e um teto ausente não é um teto infinito

`MAX_PROVIDER_RUNS` · `MAX_START_POSTS` · `MAX_USD` · `MAX_ITEMS`

Falta um → a autorização **não nasce** (`AutorizacaoInvalida` na *construção*,
não no uso: uma autorização mal formada que só rebentasse no momento da compra
seria uma autorização que atravessou todo o código a parecer válida).

Pedir um teto acima do autorizado **recusa** — não rebaixa em silêncio.

### O que esta lei nunca cria

`SOURCE_SCORE` · `RELEVANCE_COMPUTATION` · `ITEM_RELEVANCE` · `AUTO_PROMOTION` ·
`AUTORIZACAO_IMPLICITA_POR_TOKEN` · `AUTORIZACAO_IMPLICITA_POR_ORCAMENTO`

```
    SOURCE_RELEVANCE != COST != ROUTE_POLICY != ITEM_RELEVANCE.
    O SCRAP NÃO JULGA RELEVÂNCIA. ELE OBEDECE A UMA AUTORIZAÇÃO.
```

---

## D · O ERRO QUE ESTA MISSÃO COMETEU E DESFEZ: UM SEGUNDO DONO

A guarda precisa do vocabulário da relevância (`SIM`, `AUTORIZA`, `RESULTADOS`,
o validador de `SOURCE_ID`). O dono desse eixo é `leis/relevancia_da_fonte.py`,
da **SR-01** — que vive noutro ramo (`claude/magical-ptolemy-bonfgd`, `bf07e433`)
e **não** é ancestral deste.

Primeira tentativa: trazer o ficheiro dele para esta árvore. Funcionou, os 46
testes passaram — e estava errado por três razões de uma vez:

1. esta árvore passava a ser um **segundo dono** do mesmo conceito, que é
   exactamente o defeito que o System Map existe para apanhar;
2. quando a SR-01 aterrar, duas cópias do mesmo ficheiro — conflito na melhor
   hipótese, divergência calada na pior;
3. a missão dizia **não construir relevância**, e 553 linhas de lei de
   relevância são relevância, venham de onde vierem.

Quem o apanhou foi o validador do mapa: `P9_CODIGO_DECLARADO` perguntou de que
peça era aquele ficheiro, e a resposta verdadeira — «da SR-01, noutro ramo» — não
é uma coisa que este ramo possa declarar.

```
    DEPENDER DO DONO != SER O DONO.
    COPIAR O DONO PARA DENTRO DE CASA CRIA UM SEGUNDO DONO,
    E O SEGUNDO DONO ENVELHECE CALADO.
```

### O que ficou em vez disso

A dependência é **declarada e fecha por ausência**:

```python
try:
    import relevancia_da_fonte as rf
    DONO_DA_RELEVANCIA = rf.CONTRATO
except ImportError:
    rf = None
    DONO_DA_RELEVANCIA = None
```

Sem o dono, os dois modos que julgam fonte (`NORMAL`, `PROBE`) recusam com
`DONO_DA_RELEVANCIA_AUSENTE` — uma recusa com nome próprio, porque dizer
`RELEVANCE_RESULT_AUSENTE` aqui esconderia um facto de **arquitetura** atrás de
um facto de **dados**, e quem lesse o rasto procuraria a decisão em vez do
ficheiro.

```
    SEM O DONO DA RELEVÂNCIA, NENHUMA COLHEITA COM FONTE É AUTORIZÁVEL.
```

**Fechar por ausência é mais trava, não menos.** E o `CAPABILITY_TRIAL`, que não
julga fonte nenhuma, continua a funcionar — é por isso que as sentinelas desta
casa ainda atravessam a porta paga contra um provider falso.

Estado hoje nesta árvore: `DONO_DA_RELEVANCIA = None`.

### E as provas não copiaram o dono pela janela

Um substituto escrito nos testes com as palavras **verdadeiras** do dono seria a
mesma cópia com outro nome. Então o substituto instalado tem palavras **de
propósito diferentes** (`SERVE_SUB`, `AUTORIZA_SUB`, …):

```
    O QUE SE MEDE AQUI É A LIGAÇÃO, NUNCA A LISTA.
```

A guarda lê `rf.SIM` — seja `rf.SIM` o que for. A outra metade fecha por AST:
nenhuma palavra de relevância está escrita à mão dentro da lei, e os atributos
`rf.SIM`, `rf.AUTORIZA` e `rf.RESULTADOS` têm de estar lá a ser lidos. O rasto
da prova imprime `RELEVANCE_RESULT = SERVE_SUB`, e essa feiúra é o ponto: vê-se
que é um substituto.

Os dois testes que são **do dono** e não desta lei estão marcados `COM_O_DONO`
(`unittest.skipUnless`). Hoje dizem-no em voz alta em vez de passarem calados;
quando a SR-01 aterrar, acendem-se sozinhos.

---

## E · O QUE NÃO SE QUEBROU

A nova autorização entra **antes** da criação paga. Não substitui nenhuma trava
existente — e todas continuam medidas:

| trava | origem | estado |
|---|---|---|
| orçamento de rede | C10.8A-R | PASS |
| orçamento financeiro | C10.8A-F | vivo, e o gate corre **depois** da guarda |
| um só POST pago | C10.8B | PASS |
| `maxTotalChargeUsd` do lado do provider | C10.8B | PASS |
| exposição financeira `UNKNOWN` | C10.8A-F | PASS (`UNKNOWN` não vira zero) |
| `PostTalvezCriado` | C10.8A-F | PASS |
| zero retentativa paga automática | C10.8B | PASS |
| RAW antes da normalização | C10.8B | PASS |
| evidência RAW entre jobs | C10.8B-R | `SURVIVORS = 0` |

### Seis suites falharam **fechado**, e isso era o esperado

Ao pôr a guarda, seis suites que atravessam a porta paga passaram a recusar.
Fechado é o lado certo para falhar. As causas foram duas, e nenhuma era a
guarda estar errada:

**Três por import circular:** `coletor` → `autorizacao_de_gasto` →
`relevancia_da_fonte` → `admissao` → `preservar_coleta` → de volta a `coletor`.
Resolvido com import tardio dentro de `executar` — o idioma que esse ficheiro já
usa para `social_envelope`.

**Três por autorização que faltava declarar.** Cada uma dessas suites **sempre**
foi um ensaio de capacidade contra um provider falso; o que faltava era dizê-lo.

```
    DECLARAR A AUTORIZAÇÃO QUE O TESTE SEMPRE ASSUMIU NÃO É ENFRAQUECÊ-LO.
    FABRICAR UM ATALHO PARA A GUARDA É QUE SERIA.
```

Não há bandeira, variável de ambiente nem modo de teste que desligue a guarda —
e `test_36_37_a_guarda_nao_tem_porta_de_teste` reprova se alguém acrescentar um.
Em `provas/primeira_rota_paga.py` a autorização declarada tem
`MAX_START_POSTS = 1`, que é **mais** trava do que a prova tinha antes.

### E um sítio onde a lei morde o próprio autor

`provas/nenhuma_compra_sem_autorizacao.py` chamava-se `provas/autorizacao_de_gasto.py`
e **sombreava a lei**: `import autorizacao_de_gasto` dentro do `coletor`
encontrava a prova, não a lei. Renomeado.

```
    UMA PROVA COM O NOME DA LEI SUBSTITUI A LEI QUE IA PROVAR.
```

---

## F · AS PROVAS

### `provas/nenhuma_compra_sem_autorizacao.py` — 363 linhas

`SR02_SPEND_ENFORCEMENT_OFFLINE = PASS`
`POSTS QUE O TRANSPORTE FALSO VIU = 5` · **nenhum saiu para a rede**

O falso é instalado sobre `coletor._curl` — a fronteira do **provider**, e só
ela. Por baixo dele ficam a guarda, os dois orçamentos, o teto do lado do
provider e a trava de retentativa: todos correm a sério.

```
    FAKE SOMENTE O PROVIDER BOUNDARY.
```

### `tests/test_sr02_autorizacao_de_gasto.py`

**49 testes · 47 PASS · 2 skip declarados (`COM_O_DONO`) · 0 FAIL**

- **ataques A1–A44**, os quarenta e quatro presentes e nenhum em falta;
- **7 ataques extra** sem número;
- **mutantes M1–M18** dentro da suite, mais **M19–M22** aplicados à mão à árvore
  para provar que A41–A44 mordem: **`SURVIVORS = 0` nos vinte e dois**.

Cada ataque mede **POSTS**, nunca a mensagem de erro. Zero POST é a única prova
— uma recusa que devolve o texto certo e faz o POST não recusou nada.

#### E o sentinela que passava por sorte

A1–A40 contavam `metodo='POST'` escrito **à letra**, e essa não é a afirmação que
a arquitetura desta missão precisa. Medido: `regras/sensor_coleta.py` fala HTTP
com a Apify passando `method=metodo` — uma **variável** — e o sentinela era
**cego** a ele.

A primeira leitura desta missão concluiu «ali não há buraco»: o ficheiro troca o
*transporte* e a corrida continua a nascer em `coletor.executar`, que consulta a
guarda. **Essa conclusão estava errada**, e a secção G conta o resto — o
substituto repetia o POST. O sentinela passava por sorte, e um sentinela que passa
por sorte reprova quando calha.

```
    CONTAR O LITERAL NÃO É CONTAR QUEM CRIA.
    TROCAR O TRANSPORTE != ABRIR UMA SEGUNDA PORTA.
```

Dois ataques novos medem a invariante certa:

- **A41** — só um ficheiro **passa** um endereço `/acts/.../runs` a uma chamada;
- **A42** — quem troca o transporte não cria corrida (e a sentinela exige que
  `regras/sensor_coleta.py` esteja de facto na lista dos que trocam, para medir
  algo que acontece e não uma hipótese).

A primeira versão de A41 media «a string existe no ficheiro» e apanhou
`medidas/portao.py`, que guarda `'POST /acts/{actor}/runs?waitForFinish'` como
**rótulo** de relatório, com `{actor}` nunca formatado. Ele nomeia a porta, não a
abre.

```
    NOMEAR O ENDEREÇO NÃO É PEDI-LO.
```

O critério que ficou é «a string entra numa chamada». E as duas sentinelas foram
verificadas por mutação, não por leitura: **M19** acrescentou uma segunda porta
que pede a criação de corrida → A41 reprovou; **M20** acrescentou um transporte
que também cria → A42 reprovou. Revertidas, as duas voltam a verde.

#### As sete famílias de ataque

| família | mede |
|---|---|
| `NadaSubstituiAutorizacao` | token, orçamento, rota `ALLOWED`, script directo, workflow |
| `OParEExacto` | `SIM` de T3 usado em T9; auth de A usada em B; URL como `SOURCE_ID` |
| `NinguemFabricaAutorizacao` | dicionário/string/`True` como autorização; `apify_pool` não julga relevância |
| `OProbeNaoPromove` | probe sem humano, sem teto; probe não promove |
| `OsTetosMordem` | trial vira recorrente; segundo POST; cap removido; `UNKNOWN` não vira zero |
| `NenhumaPortaLateral` | AST: uma só primitiva; sem porta de teste; ator pago não é policy override |
| `OReusoIndevido` | a autorização não sobrevive ao bloco; sem o dono, recusa |

---

## G · O BURACO QUE FALTAVA: UMA TROCA DE TRANSPORTE LEVA AS LEIS DO TRANSPORTE

Este é o achado mais sério da missão, e ele **não** foi encontrado por mim: uma
linha paralela da mesma missão escreveu-o no know-how, e ao lê-lo verifiquei que
a minha própria conclusão anterior — «ali não havia buraco» — estava errada.

`regras/sensor_coleta.py` faz, **no import**, `coletor._curl = _curl_robusto`. A
troca é legítima: o proxy deste ambiente derruba conexões e o urllib sobrevive
onde o subprocesso não sobrevive. O que ela levava consigo não era.

O `_curl` da casa carrega uma lei de 2026-09-02 escrita na própria docstring:

```python
vezes = 1 if metodo.upper() in ('POST', 'PUT', 'PATCH', 'DELETE') else tentativas
```

O substituto fazia `for n in range(4)` para **qualquer** método. Medido: um POST
que caia no túnel saía **quatro vezes**.

```
    REPETIR UM GET É BARATO. REPETIR UM POST É COMPRAR DE NOVO.
```

Se o POST chegou à Apify e só a *resposta* se perdeu na volta, a retentativa não
reenvia um pedido perdido: acende uma **segunda execução paga**, órfã — sem
`run_id`, sem manifesto, sem custo rastreado, e a gastar. E `maxTotalChargeUsd`
não cobre isto: ele limita **cada** execução, nunca a soma das execuções que
ninguém sabe que existem.

O efeito sobre esta missão é directo e grave: a guarda autoriza **um** POST,
`consumir()` conta **um**, e o transporte emitia até quatro. Bastava um
`import sensor_coleta` em qualquer ponto do processo para isso valer **para toda a
gente**.

```
    UMA LEI QUE MORA DENTRO DE UMA IMPLEMENTAÇÃO VIAJA COM ELA.
```

Consertado: o substituto passou a distinguir o método e a levantar
`PostTalvezCriado` — a excepção que a casa já tinha para «o POST pode ter nascido»
— em vez de acender outra.

### E a metade que NÃO se herda

A diagnose paralela dizia também que o substituto «não reservava nada no teto de
rede». Literalmente verdade, e sem consequência — **medi-o antes de copiar a
reserva para lá, e foi bom tê-lo medido**:

| transporte | sai por | o teto vê? | precisa reservar? |
|---|---|---|---|
| `coletor._curl` | `subprocess` → `curl` | **não** (§80) | **sim**, explicitamente |
| `_curl_robusto` | `urllib.request.urlopen` | **sim** | **não** |

`scrap_http.orcamento_de_rede` cobra exactamente em `urlopen`. Copiar a reserva
para o substituto contava a mesma ida **duas vezes** — medido, `orc.usados = 2`
para um único POST. E um teto que se esgota ao dobro da velocidade recusa coleta
legítima com o nome errado.

```
    O QUE O SUBSTITUTO HERDA É O EFEITO, NÃO A LINHA.
    COPIAR A TRAVA SEM VER ONDE ELA JÁ MORDE COBRA DUAS VEZES.
```

### A sentinela, e a segunda vez que caí no mesmo erro

A1–A44 fecham isto — mas a primeira versão de A43/A44 conferia se a palavra
`'POST'` aparecia no corpo da função. Ela **passava com a lei removida**: a
palavra continuava lá, noutra linha, no `raise PostTalvezCriado`.

Foi exactamente o erro sobre o qual eu tinha acabado de escrever uma lei, cometido
na mesma sessão.

```
    UMA SENTINELA QUE LÊ O TEXTO ENCONTRA A PALAVRA, NÃO A DECISÃO.
```

A versão que ficou mede **comportamento**, num subprocesso — porque importar
`sensor_coleta` troca `coletor._curl` para o processo inteiro, que é precisamente
a coisa medida. Verificada por mutação, com os números à vista:

| mutação | resultado |
|---|---|
| M21 · o substituto volta a repetir qualquer método | `POSTS=4` → reprova |
| M22 · o substituto volta a reservar também | `REDE=2` → reprova |
| revertidas | 49 PASS |

## H · REGRESSÃO — E A BASELINE QUE MENTIU

**`NEW_FAILURES = 0`**, e as falhas são **as mesmas 12, nome por nome**.

| medição | PASS | FAIL |
|---|---|---|
| baseline, no mesmo directório | 97 | 12 |
| depois da missão | 98 | 12 |

O `+1` é a suite nova. As 12 herdadas são as 12 de antes.

### O primeiro número estava errado, e o defeito era do método

A primeira baseline foi medida numa **worktree** em `/tmp`, e deu `95/14`. Duas
das «14» falhavam **por ser uma worktree**:

- `test_c3_youtube_cutover.py` — o caminho da worktree é mais fundo, e o bruto
  escapava do redireccionamento com `../../../../../`;
- `test_portao.py` — a worktree está em **detached HEAD**, e o teste pergunta se
  o alvo é um «branch vivo».

Três corridas de cada lado: determinístico, não intermitente. Medido outra vez
**no mesmo directório, no mesmo ramo, com `git stash`** — e as duas passam.

```
    UMA BASELINE MEDIDA NOUTRO SÍTIO NÃO É A BASELINE.
    UMA WORKTREE MUDA O CAMINHO E A CABEÇA, E ALGUNS TESTES MEDEM OS DOIS.
```

E não se declarou «curei dois testes»: não curei nada. O ambiente da medição é
que estava a mentir.

---

## I · O SYSTEM MAP

Cadeia lida de `system-map/scripts/CADEIA-DO-MAPA.json` — **7 passos `REGERAR` +
1 `VALIDAR`**, todos corridos. `SYSTEM_MAP_CHECK = PASS`, 22 provas verdes,
`P9_CODIGO_DECLARADO` e `P5_ARESTA_PROVADA` incluídas.

Declarado:

- peça **`C-AUTORIZACAO-DE-GASTO`** (`Z-REGUAS`, `contract`) → `leis/autorizacao_de_gasto.py`;
- aresta **`C-COLETA-BASE` → `C-AUTORIZACAO-DE-GASTO`** (`CONSULTA`) — e ela passa
  `P5_ARESTA_PROVADA`, ou seja há linha de código que a prova;
- `provas/nenhuma_compra_sem_autorizacao.py` em `C-PROVA-COLETA`.

Uma nota de método: a primeira edição do `architecture.declared.json` foi feita
reserializando o JSON, e produziu **3.618 inserções / 3.590 remoções** para uma
mudança de três itens. Revertida e refeita cirurgicamente: **29 inserções**.

```
    UM DIFF QUE NINGUÉM CONSEGUE LER NÃO FOI REVISTO, FOI ACEITE.
```

Provas do próprio mapa: `test_system_map.py` **PASS**.
`test_impressao_da_arvore.py` **FAIL · 1** — `nenhum_passo_e_engolido_pelo_erro_do_anterior`,
passos sem `if: !cancelled()` em `.github/workflows/system-map.yml`. **Herdada**:
reproduz-se igual na baseline, e esta missão não toca nesse ficheiro.

---

## J · A BÍBLIA

```
BIBLE_CHANGE_REQUIRED_FROM_SR01 = YES
BIBLE_CHANGED_IN_THIS_MISSION   = NO
```

A SR-01 abriu matéria constitucional (relevância da fonte como portão de gasto) e
esta missão acrescenta-lhe a metade da **execução**. As duas juntas pedem lei
escrita. Esta missão foi instruída a não alterar a Bíblia, e não alterou.

O que a Bíblia terá de absorver, quando for a hora:

1. nenhuma execução paga sem autorização explícita para **aquele** gasto;
2. a autorização é do **PAR** `(fonte, propósito)`, nunca da fonte sozinha;
3. os três modos e a proibição de um se vestir de outro;
4. `PROBE != DECISION`;
5. um teto ausente não é um teto infinito;
6. o dono da relevância e o executor do gasto são **peças diferentes**.

---

## K · O QUE FICA POR SABER

- **A orquestração canónica continua por arrumar.** Quinze ficheiros importam o
  `coletor` e oito chamam a porta paga directamente, sem passar pelo
  orquestrador. Já não é o que mantém o buraco aberto — a guarda fecha-o no sítio
  da compra — mas continua a ser dívida.
- **`leis/relevancia_da_fonte.py` não está nesta árvore.** Enquanto a SR-01 não
  aterrar, `NORMAL` e `PROBE` recusam. É o estado correcto e é visível; não é o
  estado final.
- **Dois testes estão em `skip` declarado.** Eles não provam nada hoje, e dizem-no.
- **`test_impressao_da_arvore.py` continua com 1 FAIL herdada** — dela é o
  workflow, não esta missão.
- **Uma linha paralela desta mesma missão existe, com outra implementação.** Ela
  tocou `coleta/scrap_executor.py` e `regras/sensor_coleta.py`, moveu o eixo do
  modo de casa, e encontrou o buraco do transporte que esta linha não encontrou.
  As duas não estão reconciliadas, e isso é dívida explícita, não detalhe.
- **A guarda vale o que vale a invariante «um só criador».** Ela está agora medida
  pelo critério certo (A41, A42) e verificada por mutação, mas continua a ser uma
  afirmação sobre a **forma** do código: um caminho que criasse corrida por
  `subprocess` a chamar `curl`, ou por uma biblioteca HTTP que a árvore hoje não
  usa, escaparia às duas sentinelas. É exactamente o buraco que a `§80` nomeou
  para os tetos, e aqui ele fica **declarado** em vez de suposto fechado.
- **Nenhum gasto real aconteceu**, e portanto nada aqui prova que a guarda deixa
  passar uma compra **verdadeira**. O que está provado é que ela recusa 40
  ataques e que 18 mutantes morrem. `PROVA OFFLINE != PROVA AO VIVO` continua a
  valer, e a autorização histórica de US$ 0,10 **não** foi usada.
