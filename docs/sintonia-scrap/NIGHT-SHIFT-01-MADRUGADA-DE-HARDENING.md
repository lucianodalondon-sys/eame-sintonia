# NIGHT SHIFT 01 — A MADRUGADA DE HARDENING

> Uma madrugada de máquina sobre o SINTONIA SCRAP, com um objetivo só:
>
> ```
> AMANHÃ NÃO DESCOBRIR PROBLEMAS QUE A MÁQUINA PODIA TER DESCOBERTO SOZINHA HOJE.
> ```
>
> Branch: `claude/sintonia-scrap-night-shift-01` · base `081316fc`
> Nada foi mergeado. A Release Candidate não se moveu.

---

## O QUE ESTA MADRUGADA ENCONTROU

Quatro defeitos técnicos reais, todos **reproduzidos antes de corrigidos**, todos
com sentinela e mutante a vigiá-los. Nenhum deles era visível numa leitura da
árvore: os quatro precisaram de a máquina CORRER.

```
LER A ÁRVORE PROVA QUE A PEÇA EXISTE. SÓ CORRER PROVA QUE A ARESTA EXISTE.
```

---

### DEFEITO 1 · UMA ROTA QUE NÃO CORREU DEVOLVIA UMA OBSERVAÇÃO

O censo executável pôs cada capacidade `READY` a andar pelo caminho real. Duas
responderam uma coisa impossível:

```
instagram.reel.capture   RESULT = ROUTE_NOT_ALLOWED   e 1 objeto
instagram.reel.audio     RESULT = ROUTE_NOT_ALLOWED   e 1 objeto

PROVIDER_USED = None  ·  COST_STATE = NOT_RUN  ·  idas ao mundo = 0
```

Uma rota recusada pela política, que nunca abriu socket nenhum, devolvia um
objeto. Reproduzido: esse objeto era um **esqueleto de REEL** com todos os campos
em `NOT_KNOWN` — e, levado pelo dono da colheita com uma fonte no pedido, virava
**uma unidade de COLHEITA carimbada com `SOURCE_ID = IT-T9-001`**. O contrato de
retorno não tinha um único reparo a fazer: ela era, na forma, uma observação
perfeita de uma fonte real.

```
UMA ROTA QUE NÃO CORREU NÃO OBSERVOU NADA.
UM ESQUELETO COM SOURCE_ID É UMA OBSERVAÇÃO FABRICADA.
```

**Onde o conserto NÃO foi.** Não foi ao `adaptador_instagram`. O esqueleto nasce
lá de propósito: a cadeia de Reel distingue REUSAR de ADQUIRIR, e o portão está
posto onde o socket abre precisamente para não recusar reprocessamento local.

**Onde foi.** Em `coleta/scrap_colheita.py`, que é quem decide o que é COLHEITA.
E o sinal não é o estado de falha — uma rota que colheu dez e depois levou
`RATE_LIMITED` colheu dez de verdade. O sinal é o do dono do custo, que nasce
`NOT_RUN` e só quem corre sobrescreve:

```
NOT_RUN != COST 0. UNKNOWN COST != COST 0.
```

Os objetos não desaparecem: saem por SUPORTE, contados, com a espécie escrita e
com `PORQUE_ZERO_COLHEITA` a dizer o estado e o motivo.

---

### DEFEITO 2 · UMA FALHA QUE SABIA CHEGAVA COMO UMA QUE NÃO SABIA

Num runner sem Chrome, `instagram.profile.discovery` — a única capacidade `WIRED`
que interessa ao objetivo operacional — chegava assim:

```
RESULT              UNKNOWN_ERROR      «não classificado»
NATIVE_REASON       None
RECOVERY_ACTION     None
ROUTER_RECORD.ERRO  «sem Chrome nesta máquina: nenhum Chrome ou Chromium
                     encontrado no PATH nem nos caminhos padrão»
```

A frase sabia exactamente o que tinha acontecido. O ESTADO dizia «ninguém sabe».

```
UMA MENSAGEM QUE SABE E UM ESTADO QUE NÃO SABE VALEM MENOS QUE NENHUM DOS DOIS:
QUEM LÊ POR MÁQUINA LÊ O ESTADO.
```

De manhã, `UNKNOWN_ERROR` sobre Instagram manda alguém depurar o Instagram —
quando o que falta é um navegador.

**Nada disto era vocabulário novo.** `leis/falhas.py` já tinha o estado certo e
já listava o nome nativo dele; `ferramentas/cdp.py` já tinha a constante. Os dois
donos já concordavam — ninguém os tinha ligado neste caminho. A própria
`falhas.classificar` escreve por extenso quem devia falar: «Quem tem informação
melhor — `apify_pool`, `social_rotas`, `cdp` — deve classificar por conta
própria».

```
FAILURE STATE VEM DO DONO, OU NÃO É FAILURE STATE.
```

E é a mesma costura que `adaptador_youtube` já usava para «não tenho chave».

**Dois defeitos apanhados ao consertar o primeiro, e nenhum é do Instagram:**

1. `social_rotas` escrevia `RECOVERY_ACTION = None` mesmo quando ninguém a
   declarava, e `selar()` deriva-a com `setdefault` — que olha para a PRESENÇA da
   chave, não para o valor. A derivação nunca corria. Valia para qualquer
   adaptador: o ramo de `HTTPError` do YouTube perdia-a da mesma maneira.

   ```
   UMA CHAVE ESCRITA A None NÃO É UMA CHAVE AUSENTE.
   E `setdefault` NÃO SABE A DIFERENÇA.
   ```

2. `EstadoDaApi` só levava NOMES. O estado certo apagava a única linha que dizia
   QUAL ferramenta faltava. Ganhou `DETALHE`, e os três campos não se colapsam:
   `STATE` é canónico, `NATIVE_REASON` é nome de máquina, `DETALHE` é a frase de
   gente — redigida, como tudo o que vai para log.

Depois:

```
RESULT EXECUTOR_UNAVAILABLE · NATIVE_REASON BROWSER_NOT_REACHED
RECOVERY_ACTION NEEDS_HUMAN_FIX · FAILURE_LAYER EXECUTOR
EXECUTOR_HEALTH BROKEN · SOURCE_HEALTH HEALTHY · DEGRADES_SOURCE False
ERRO «…: sem Chrome nesta máquina: nenhum Chrome…»

ROTA CAÍDA NÃO É FONTE CAÍDA. O Instagram não foi acusado de nada.
```

---

### DEFEITO 3 · A PORTA PAGA DEIXAVA PASSAR DOIS AO MESMO TEMPO

O mais sério da madrugada, e o único que envolve dinheiro.

```
autorização para 1 execução   ->  2 corridas pagaram
autorização para 3 execuções  ->  5 corridas pagaram
```

E não só na primitiva. **Pela PORTA PAGA de verdade** — `coletor.executar`
inteiro, com o provider falso por baixo de tudo — com 16 fios e teto 3,
**nasceram 4 POSTs**. Uma compra além do que a pessoa autorizou.

A causa é a distância entre duas linhas que pareciam uma:

```python
if autorizacao.restantes <= 0: recusa
reg['GASTAS'] += 1
```

Entre a pergunta e a resposta cabe outro fio. E `+= 1` também não é atómico — ler,
somar e escrever são três passos, e o interpretador troca de fio entre bytecodes.

```
UMA GUARDA QUE CONFERE E DEPOIS CONSOME DEIXA PASSAR QUEM CHEGAR NO MEIO.
CONFERIR E CONSUMIR TÊM DE SER UM SÓ ACTO.
```

**Por que só apareceu agora.** Com o intervalo de troca normal a corrida é rara —
e rara não é ausente. Encurtá-lo não INVENTA a corrida: ela existe no código ou
não existe. Só a torna visível num segundo em vez de num mês.

```
«NÃO APARECEU» NÃO É «NÃO EXISTE».
```

**O conserto.** Uma trava, ao lado do registo que ela guarda, a cobrir as três
operações sobre o mesmo registo. Não precisa de atravessar processos: `_SELO` é
um `object()` deste processo, e uma autorização reconstruída noutro lado é
recusada como `AUTORIZACAO_FABRICADA` — medido, não presumido.

Depois do conserto, 64 fios × 200 rodadas × várias configurações: **zero furos**.

---

### DEFEITO 4 · DOIS MUTANTES MUTAVAM O SÍTIO ERRADO E CHAMAVAM-SE PROVA

Este é sobre a máquina de provar, e por isso é o mais insidioso.

**M6** — «a autorização deixa de se gastar» — apontava para
`"    reg['GASTAS'] += 1"`. Esta madrugada escreveu, no mesmo ficheiro, um
comentário que CITA a linha. O texto do comentário contém a âncora como
sub-cadeia. `replace(..., 1)` trocou a PRIMEIRA ocorrência — o comentário — e o
código ficou intacto. O mutante não mudou nada, e o relatório chamou-lhe
SOBREVIVENTE.

```
UM COMENTÁRIO QUE CITA O CÓDIGO ROUBA A ÂNCORA DE QUEM MUTA O CÓDIGO.
```

**O conserto geral**, que é o que interessa: a mutação passou a CONTAR as
ocorrências e a recusar-se a correr quando a âncora não é única —
`ALVO_AMBIGUO`, ruidoso, contado como sobrevivente.

```
UM MUTANTE QUE NÃO MUDA NENHUM NÚMERO NÃO SE CONSEGUE VIGIAR.
E UM QUE MUDA O NÚMERO ERRADO É PIOR: ELE MENTE COM CONFIANÇA.
```

**E o guarda apanhou um segundo no minuto em que nasceu.** **M20** — «o portão
promove o estado da capacidade» — apontava para uma expressão que aparece DUAS
vezes em `scrap_executor.py`, e as duas são ramos de RECUSA, onde a capacidade
nem correu. A lei de que ele fala — `TRIAL PASSADO != CAPACIDADE PROVADA` — é
sobre o caminho que CORREU. Ele nunca lhe tinha tocado, e reportava-se verde.

```
MUTAR O RAMO QUE RECUSA NÃO TESTA A LEI DE QUEM PASSOU.
```

**E, re-ancorado no sítio certo, ele passou a SOBREVIVER de verdade** — com zero
sentinelas. A prova que devia vigiá-lo comparava `CAPABILITY_STATE_BEFORE` com
`CAPABILITY_STATE_AFTER` e mais nada. E o canário é
`bluesky.author.incremental`, que o dono já declara `PROVEN`: sobre ele, «não
promoveu» e «promoveu para PROVEN» são exactamente a mesma linha.

```
UMA SENTINELA QUE VIGIA UM CAMPO CUJO VALOR JÁ É O DA MUTAÇÃO NÃO VIGIA NADA.
```

A pergunta certa não é «os dois são iguais?» — é «o depois é o que o DONO diz?».
A sentinela passou a perguntar isso, e ganhou uma irmã que corre sobre a
identidade do LinkedIn, que está `PARTIAL` — onde uma promoção a `PROVEN` é
visível.

```
UMA PROVA QUE SÓ CORRE ONDE O ERRO É INVISÍVEL NÃO É UMA PROVA.
```

Três defeitos, portanto, na própria máquina de provar: uma âncora roubada por um
comentário, uma âncora ambígua a mutar o ramo errado, e uma sentinela cega por
escolher a única capacidade onde a mutação não mudava nada.

---

## O ENSAIO SCRAP → COLLECTION, CONTRA O ESTADO REAL

A árvore da Collection foi lida onde ela está (`f06b203c`, worktree separado e
**detached**, para nunca mexer na ref de ninguém). Nada foi mergeado. O que
atravessou foi **um ficheiro JSON** — o envelope que o SCRAP escreve.

```
UM ENVELOPE É DADOS. LEVAR DADOS NÃO É MERGEAR CÓDIGO.
```

Antes de correr, dois factos medidos:

```
leis/retorno_da_coleta.py   BYTE A BYTE IGUAL nas duas árvores
coleta/scrap_colheita.py    NÃO EXISTE na árvore da Collection
coleta/scrap_*.py           NENHUM existe lá

CONTRATO IGUAL != ARESTA LIGADA.
```

Com o código DELES sobre os dados NOSSOS:

```
E1  o contrato da Collection aceita o envelope do SCRAP      PASSA
E2  a lei deixa passar a colheita                            PASSA   1 de 1
E3  o ingresso aceita a unidade                              PASSA
E4  o RAW foi preservado                                     PASSA
E5  a fronteira devolve a unidade canónica                   PASSA
E6  a admissão julga a unidade                               PASSA   NAO_SEI · regra=legivel
E7  a unidade leva texto para quem julga                     PARA
E8  o veredito não é uma confissão de ignorância             PARA

FIRST_LOST_EDGE = E7_a_unidade_leva_texto_para_quem_julga
```

A cadeia **liga inteira**. O que atravessa vem **sem texto** — e quem julga
responde `NÃO SEI`, que é a resposta CERTA para um item sem conteúdo.

`social_envelope` guarda o texto da observação em `TEXT`; quem julga lê `texto`.
Não há entrada para ele em NENHUM dos dois mapas — nem em
`scrap_colheita.DO_SCRAP_PARA_A_PORTA`, nem em `ingresso.PARA_A_PORTA`. **O texto
existe dos dois lados e não atravessa.**

E ligá-lo são **duas** decisões, não uma:

```
1 · TEXT -> texto           o texto atravessa
2 · CONTENT_TYPE -> ?       para quem julga saber O QUE leu
```

Fazer 1 sem 2 entrega texto de autor e fala reconhecida no MESMO campo,
indistinguíveis — que é exactamente a soma que a casa proíbe:
`CAPTION != TRANSCRIPT`. E a segunda precisa de um campo que o vocabulário da
porta hoje não tem.

```
BLOCKED_BY_HUMAN = VOCABULARIO_DO_TEXTO_NA_PORTA
```

---

## META — MEDIDO, E NÃO HÁ O QUE PORTAR

```
PLATAFORMAS DECLARADAS  BLUESKY · FACEBOOK · INSTAGRAM · LINKEDIN ·
                        MASTODON · TELEGRAM · X · YOUTUBE
META                    não existe como plataforma declarada
THREADS                 não existe como plataforma declarada
FACEBOOK                4 capacidades, todas NOT_IN_V1, FIRST_BREAK = NO_ROUTE
```

A única branch com «meta» no nome — `origin/claude/eame-meta-competitor` — não
tem ancestral comum com esta linha (`git merge-base` devolve vazio) e não tem um
único ficheiro sob `leis/` ou `coleta/`. É outra história, sobre análise de
biblioteca de anúncios.

```
META_INTEGRATION_REHEARSAL = NAO_APLICAVEL
```

Não há linha Meta de coleta para ensaiar, e portanto não há owner antigo a
arrastar. Construir Facebook ou Threads está explicitamente fora desta madrugada.

---

## A SENTINELA REAL, E O QUE ELA NÃO É

Uma operação real, gratuita, permitida, sem binding humano — pelo caminho
canónico, com a conta pública do próprio Bluesky:

```
fase        canario-bluesky
colheita    0
suporte     2
COST_STATE  FREE_ROUTE_BY_POLICY · RESULT OK · ESTADO SUCCESS

porque zero  o pedido não nomeou fonte. O SCRAP observa PLATAFORMAS e a porta
             fala em FONTES; sem o SOURCE_ID vindo do pedido, estas 1
             observações são CANDIDATAS e não observações de uma fonte provada.
```

A máquina foi ao mundo, obedeceu aos portões, preservou o bruto e **recusou-se a
chamar colheita ao que colheu**, porque ninguém lhe disse de quem estava a ouvir.

```
TECHNICAL_SENTINEL != CANONICAL_COLLECTION
```

---

## OS PORTÕES

```
SCRAP_NIGHT_BRANCH = claude/sintonia-scrap-night-shift-01
BASE               = 081316fc

SCRAP_ENGINE_STILL_READY       = PASS
READY_CAPABILITIES_TESTED      = 9
READY_CAPABILITIES_BROKEN      = 0
CAPACIDADES PEDIDAS PELA V1    = 3
REQUIRED_V1_CAPABILITY_WITHOUT_REQUEST_PATH = 0
READY_SEM_PEDIDO               = 6   (existe, ninguém pede — não é defeito)

SUPERFÍCIE V1   READY 9 · READY_PENDING_CREDENTIAL 6 · FAIL_CLOSED 12 ·
                NOT_IN_V1 9 · UNKNOWN 0

TECHNICAL_DEFECTS_FOUND = 4 no produto
                        + 3 na máquina de provar (âncoras e sentinela cega)
                        + 3 nas próprias sondas desta madrugada
TECHNICAL_DEFECTS_FIXED = todos os 10

ACTIVE_V1_BYPASSES                   = 0
MANUALLY_TRIGGERABLE_POLICY_BYPASSES = 0
HIDDEN_PAID_FALLBACKS                = 0

PAID_REAL_RUNS      = 0
PAID_REAL_COST_USD  = 0
REAL_FREE_REQUESTS  = 1   (a sentinela técnica acima)

SCRAP_TO_COLLECTION_REHEARSAL = E1–E6 PASSA · E7 PARA
FIRST_LOST_EDGE               = E7_a_unidade_leva_texto_para_quem_julga

CRASH_RETRY          = PASS   não devolve o gasto; cópia recusada
CONCURRENCY          = PASS   0 furos em 64 fios × 200 rodadas
AUTHORIZATION_DOUBLE_SPEND = 0
IDENTITY_COLLISION         = 0
RAW_PRESERVATION     = nenhuma fase da V1 observa bytes e perde o bruto
RETURN_SPECIES       = WRONG_SPECIES_INGRESS = 0
IDENTITY             = PASS   domínio, slug e sha não compram
TIME_GEO_PROVENANCE  = PASS   sem FACT_TIME, sem FACT_LOCATION derivados

ATTACKS   = 56 · SURVIVING_ATTACKS = 0
MUTANTS   = 36 · SURVIVING_MUTANTS = 0

META_INTEGRATION_REHEARSAL       = NAO_APLICAVEL
COLLECTION_INTEGRATION_REHEARSAL = ENSAIADA · liga até à admissão

BLOCKED_BY_HUMAN       = SOURCE_ACCOUNT_BINDING
                         VOCABULARIO_DO_TEXTO_NA_PORTA
BLOCKED_BY_ENVIRONMENT = INSTAGRAM_RUNTIME (sem Chrome neste runner)
BLOCKED_BY_CREDENTIAL  = 6 capacidades READY_PENDING_CREDENTIAL

READY_TO_PLUG_TOMORROW = SIM, para a máquina.
                         NÃO, para a operação — falta uma decisão de gente.
```

---

## AMANHÃ — 3 PASSOS MÁXIMOS

```
PASSO 1 — Luciano decide o SOURCE_ACCOUNT_BINDING: a conta Instagram do
          candidato IT-T9-001 é `bayer_italia`, `syngentaitalia`,
          `basf_global`, ou nenhuma delas.

PASSO 2 — Integrar `claude/sintonia-scrap-night-shift-01` na Release
          Candidate. São 4 defeitos consertados e 0 regressões; a branch
          não mexe em nada fora do SCRAP.

PASSO 3 — Decidir o VOCABULARIO_DO_TEXTO_NA_PORTA: se `TEXT` atravessa
          para `texto`, e com que campo quem julga passa a saber se leu
          legenda de autor ou fala reconhecida.
```

O PASSO 2 não depende de nenhum dos outros dois e pode acontecer primeiro.

---

## SE LUCIANO RESPONDER «SIM» AO SOURCE BINDING

O comando exacto, já preparado, para a primeira colheita útil. Ele **não foi
executado** e não deve ser antes da decisão.

```bash
# 1 · A decisão de relevância entra no livro, pelo dono dela.
#     Sem esta linha a autorização não nasce — e é assim que tem de ser.
python3 leis/relevancia_da_fonte.py --decidir \
    --source-id=IT-T9-001 \
    --proposito=T9 \
    --resultado=SIM \
    --motivo="<o motivo, em palavras de gente>" \
    --evidencia=<ficheiro>:<linha> \
    --metodo=DECISAO_HUMANA

# 2 · A colheita, pelo caminho canónico. O handle é FILTRO, não é a fonte.
python3 orquestrador/orquestrador.py \
    --pedido="colete a janela do Instagram de IT-T9-001" \
    --fase=janela-perfis \
    --fonte=IT-T9-001 \
    --run-id=OP-01-$(date +%Y%m%d-%H%M%S)
```

⚠️ O PASSO 2 corre `instagram.profile.discovery`, que é `LOCAL` e
`DATACENTER_BLOCKED`. **Precisa de uma máquina com Chrome** — não corre neste
runner de nuvem, e a madrugada mediu exactamente isso: sem Chrome ele agora
responde `EXECUTOR_UNAVAILABLE · NEEDS_HUMAN_FIX`, em vez do antigo
`UNKNOWN_ERROR`.

Para uma primeira colheita SEM depender de Chrome, o canário do Bluesky serve, e
precisa apenas do passo 1 mais o handle da conta:

```bash
python3 coleta/scrap_colheita.py \
    --run-id=OP-01-$(date +%Y%m%d-%H%M%S) \
    --fonte=IT-T9-001 \
    --handle=<a conta Bluesky decidida> \
    canario-bluesky
```

---

## REGISTADO, E NÃO IMPLEMENTADO

Uma fragilidade medida esta madrugada, fora do escopo do objetivo e por isso
**registada em vez de consertada**:

**Dois testes de outras missões mudam de veredito por causa de uma pasta vazia.**
`tests/test_c10_5d_decisao_instagram.py::test_T10` e
`tests/test_c10_6_crash_retry.py::test_P11` fazem `skipTest` quando
`data/raw/REEL-MIDIA` **não existe**, mas falham quando ela existe e está
**vazia** — com a mensagem «a gaveta veio vazia; a sonda mediria zero por
engano». As duas condições querem dizer a mesma coisa para quem mede «o que já lá
estava não mudou»: não há nada para comparar.

```
UMA GAVETA VAZIA E UMA GAVETA AUSENTE SÃO A MESMA COISA
PARA QUEM MEDE O QUE ELA TINHA.

UM TESTE CUJO VEREDITO DEPENDE DE QUEM CORREU ANTES
NÃO ESTÁ A MEDIR O QUE DIZ.
```

O conserto é uma linha em cada um — `if not os.path.isdir(gaveta) or not
os.listdir(gaveta): self.skipTest(...)` — mas são provas de duas outras missões,
e ninguém pediu para lhes mexer.

---

## EM PORTUGUÊS SIMPLES

**1 · A máquina ficou melhor?**
Ficou. Quatro defeitos reais foram encontrados e consertados, e nenhum deles se
via a ler o código — foi preciso pôr a máquina a correr para os apanhar.

**2 · O que é que se conseguiu quebrar?**
O mais grave: **a porta que autoriza gastar dinheiro deixava passar duas compras
quando só uma estava autorizada.** Com uma autorização para 3, chegaram a passar
5. Isto nunca teria aparecido num teste normal — só aparece quando duas corridas
acontecem exactamente ao mesmo tempo.

Também se quebrou: uma rota que a política RECUSA continuava a produzir uma
«observação» vazia que atravessava o contrato como se fosse material colhido de
uma fonte real.

**3 · O que é que se consertou?**
Os quatro. E cada um ficou com um teste que o vigia e com um «mutante» — um
sabotador automático que parte de propósito aquele conserto para confirmar que
algum teste fica vermelho. Trinta e seis sabotadores, nenhum sobrevive.

**4 · O que ainda impede funcionar amanhã?**
Uma coisa só, e é a mesma de ontem: **ninguém disse à máquina de quem ela vai
ouvir.** Ela está pronta, obedece a todos os portões, vai ao mundo e volta — mas
recusa-se, correctamente, a chamar «colheita» ao que traz enquanto não houver uma
fonte aprovada.

E, para o texto chegar a quem julga do lado da Collection, falta decidir uma
palavra de vocabulário — porque decidi-la sozinho misturaria legenda escrita com
fala reconhecida, e a casa proíbe isso.

**5 · Depende de quem?**
```
de Luciano     a fonte aprovada · o vocabulário do texto na porta
de ambiente    o Instagram precisa de uma máquina com Chrome
de credencial  6 capacidades esperam chave
de código      nada. O que era de código foi feito.
```

**6 · Qual branch integrar?**
`claude/sintonia-scrap-night-shift-01`. Quatro consertos, zero regressões,
System Map verde. Não toca em nada fora do SCRAP.

**7 · Qual o primeiro comando de amanhã?**
Nenhum comando. A primeira coisa é **uma resposta**: a conta do `IT-T9-001`. Sem
ela, qualquer comando devolve — e deve devolver — zero.

---

*Nenhum dólar foi gasto. Nenhum provider pago correu. Uma única ida ao mundo, de
graça, à conta pública do próprio Bluesky, e o que ela trouxe não foi chamado de
colheita.*
