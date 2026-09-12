# C10.8B-LIVE — A PRIMEIRA ROTA PAGA REAL

`C10_8B_LIVE = PASS_ROUTE_PARTIAL`

> A rota paga correu. Uma vez, com US$0,10 autorizados, um POST, um alvo, e a
> Apify devolveu `SUCCEEDED`. Ela atravessou o caminho canônico inteiro e o
> objeto voltou **sem transcrição**.
>
> ```
> PROVIDER REACHED != CAPABILITY DELIVERED.
> ```

---

## 1 · O QUE FALTAVA NÃO ERA CÓDIGO DE COLETA

A C10.8B parou em `CREDENTIAL_MISSING`. A chave vive nos *Secrets* do GitHub e
só entra num job do workflow.

```
SECRET EXISTS != SECRET REACHES PROCESS.
```

Esta missão mediu a segunda transição, e ela aconteceu:

```
CHECK.CAN   = True
CHECK.STATE = CAN_COLLECT_NOW
READY_TO_SPEND = YES
```

---

## 2 · O CENSO DOS WORKFLOWS

| workflow | secret | caminho de execução | entra pelo executor? | serve? |
|---|---|---|---|---|
| `sintonia-scrap.yml` | **SIM** | `social_scrap.py coletar` | **SIM** | **SIM** |
| `scrap-social.yml` | não | `social_scrap.py` | sim | não — sem credencial |
| `apify-sensores.yml` | SIM | `regras/sensor_coleta.py` | não | não — motor legado |

```
MODULE HAS SECRET != CORRECT FLOW.
```

E um facto que o censo trouxe: **todos** os workflows que recebem
`APIFY_TOKEN_POOL` correm em runner self-hosted Windows. As três corridas
anteriores de `sintonia-scrap.yml` (setembro 3 e 5) ficaram 24 h na fila e foram
canceladas — nenhuma encontrou runner. Hoje, `SINTONIA-EAME-LOCAL-2` pegou o
trabalho em cinco segundos.

---

## 3 · O DISPARADOR NÃO É O MOTOR

O que entrou no workflow foi **uma linha de menu e um ramo**:

```
yt-legenda-paga)
  PYTHONIOENCODING=utf-8 $PY coleta/social_scrap.py coletar yt-legenda-paga ;;
```

```
WORKFLOW_ACTOR_IDS             = 0
WORKFLOW_DIRECT_PROVIDER_CALLS = 0
WORKFLOW_SECOND_RUNTIME        = NO
```

O ator, o alvo, o modo, o motivo e os dois tetos vivem em `FASES_PAGAS`, dentro
de `coleta/social_scrap.py` — Python versionado, que se lê num commit e não se
escolhe num campo de formulário.

```
UM TETO QUE VIVE NO DISPARADOR É UM TETO QUE QUEM DISPARA ESCOLHE.
```

### Um conserto que a construção revelou

A guarda «o ref tem os scripts desta missão?» procurava dez ficheiros em
`scripts/` — uma pasta que está **vazia** desde a reorganização. Ela reprovava
toda a gente, sempre, com a frase de quem despachou contra o ref errado.

```
UMA GUARDA QUE APONTA PARA A MORADA ANTIGA RECUSA A CASA CERTA.
```

---

## 4 · A CORRIDA

```
WORKFLOW      sintonia-scrap.yml · run 34705103759 · job 103583636729
RUNNER        SINTONIA-EAME-LOCAL-2 (self-hosted, Windows)
REF           claude/sintonia-scrap-first-paid-route-c10-8b @ 81b8cdec
SECRET        presente no job · mascarado como *** em todas as linhas do log
RUN_ID        SCRAP-yt-legenda-paga-20260912T162500Z
DURAÇÃO       37 s no passo da fase
```

```
EXECUTOR        scrap_executor.COLLECT      ✔
ROUTER          social_rotas                ✔  ROTA = apify:transcricao · APIFY
ADAPTER         adaptador_youtube           ✔
PROVIDER_OWNER  coleta/coletor.py           ✔  MEDIDA.IMPLEMENTACAO
ACTOR           pintostudio~youtube-transcript-scraper
DIRECT_BYPASS   NO
```

### Os dois tetos

```
FINANCIAL_AUTHORIZED   0.10
PROVIDER_SIDE_CAP      0.10        ≤ autorizado e ≤ saldo
COMMITTED              0.00
ACTUAL_READ            0.00
UNKNOWN                0.00
REMAINING              0.10
COST_STATE             READ_NOT_SETTLED
SETTLED_COST_USD       UNKNOWN

NETWORK_LIMIT          5
NETWORK_USED           3     POST · dataset · key-value store
POSTS_TO_CREATE_RUN    1
POLLS                  0     terminal aos 60 s
```

```
READ COST != SETTLED COST.
```

O provider devolveu `usageTotalUsd = 0`. Isso é o custo **lido**, não o custo
fechado — e esta casa já anunciou US$0,90 e pagou US$5,04 por publicar um
como o outro.

---

## 5 · O QUE VOLTOU, E O QUE NÃO VOLTOU

```
ITEMS               1
TRANSCRIPT_PRESENT  NO
CHARS               None
LANGUAGE            UNKNOWN
TIMESTAMPS          NO
SPECIES             NOT_DECLARED_BY_PROVIDER
```

O objeto existe, aponta para o alvo certo, e não traz texto nos campos que o
adaptador lê — `transcript` e `chars`, medidos nos bytes preservados de uma
corrida anterior do mesmo ator.

E o bruto **não** estava vazio:

```
SCRAP_RAW_CAPTURED_ON_RUNNER   PRESERVED
SCRAP_RAW_BYTES                59.743
SCRAP_RAW_SHA256               00e97ecb8d292da4857355c415b47d6e71ce9d9c11ac702e2067fbb83cab2a38
SCRAP_RAW_READ_BACK            YES   (SHA relido, igual)
SCRAP_RAW_RETURNED_TO_REPO     NO
CANONICAL_FORWARD_PRESERVATION NO
```

Cinquenta e nove mil bytes não são o tamanho de uma resposta vazia.

```
UM OBJETO VAZIO NÃO DIZ SE A FONTE CALOU OU SE O CAMPO MUDOU DE NOME.
```

---

## 6 · E OS BYTES NÃO SOBREVIVERAM AO JOB SEGUINTE

Para separar as duas hipóteses bastava reler o bruto — que já estava pago e
estava na máquina. Uma fase **gratuita** foi escrita para isso: lê o ficheiro,
diz que chaves ele tem, não importa o dono pago, não abre socket.

```
RELER O QUE JÁ SE PAGOU NÃO É PAGAR OUTRA VEZ.
```

O resultado (run 34705389231):

```
RUN_ID_DO_REGISTO=SCRAP-yt-legenda-paga-20260912T162500Z
SEM_BRUTO_DESTA_CORRIDA · gaveta com 11 ficheiro(s)
```

Os onze são os que estão **versionados**. O nosso não estava: `.gitignore`
ignora `data/samples/**/*.gz`, e `actions/checkout` limpa o que o `.gitignore`
ignora. O bruto foi escrito, relido e assinado dentro do mesmo processo — e
apagado pelo checkout do job seguinte.

```
RAW CAPTURADO NO PROCESSO
  != RAW QUE SOBREVIVE AO JOB
  != RAW DEVOLVIDO AO REPOSITÓRIO
  != PRESERVAÇÃO FORWARD CANÔNICA.
```

Quatro estados que cabiam todos na palavra «preservado». O `SHA-256` sobrevive
e não resolve para nenhum ficheiro: é uma impressão digital de uma coisa que já
não existe.

**Não se comprou outra vez.** O que se fez foi o conserto durável: o registo
passa a guardar a **FORMA** do bruto — as chaves de cada item, o tipo, o tamanho
e se está vazio. Da próxima vez a pergunta responde-se no registo, a custo zero.

---

## 7 · COMPARAÇÃO COM O HISTÓRICO

```
SAME_TARGET          SIM · EAkcA_2FDN8
HISTORICAL_RUN       SENSOR-TR-B-3-p3 · mesmo ator · v1.0.57 · SUCCESS
HISTORICAL_CHARS     97.710
NEW_CHARS            0
MATERIAL_DIFFERENCE  SIM — e a causa não foi medida
```

As duas leituras possíveis, e nenhuma delas está provada:

- o **esquema de saída** do ator mudou, como o de entrada já tinha mudado
  (`videoUrls` → `videoUrl`, descoberto por um `HTTP 400`);
- o vídeo deixou de ter legenda pública desde 2026-08-30.

```
ENTRADA PROVADA ONTEM != ENTRADA VÁLIDA HOJE — E A SAÍDA TAMBÉM ENVELHECE.
```

---

## 8 · O ESTADO DA ROTA

```
ROUTE_STATE_BEFORE = POSSIBLE_NOT_PROVED
ROUTE_STATE_AFTER  = PARTIAL
EVIDENCE           = docs/sintonia-scrap/C10-8B-LIVE-PRIMEIRA-ROTA-PAGA.md
POLICY_CHANGED     = NO   (PERMITIDA continua CONDICIONAL · CLASSE continua APIFY)
CAPABILITY_BEFORE  = PROVEN
CAPABILITY_AFTER   = PROVEN
```

`PARTIAL` e não `PROVED`, porque a rota correu e o limite é concreto e medido: o
objeto voltou sem a carga da capacidade. `PARTIAL` e não
`POSSIBLE_NOT_PROVED`, porque já não é verdade que não se saiba se ela corre —
ela correu, de ponta a ponta, sob os dois tetos.

```
PROVIDER REACHED != CAPABILITY DELIVERED.
```

---

## 9 · MEDIDO

```
ATTACKS 33 · POSITIVE_FINDINGS 0
MUTANTS 16 · SURVIVORS 0
PROVIDER_RUNS 1 · START_POSTS 1 · APIFY_NEW_RUNS_APOS 0
MAX_AUTHORIZED_USD 0.10 · MAX_EXPOSURE_USD 0.10
ACTUAL_READ_USD 0.00 · SETTLED_USD UNKNOWN
```

O segredo aparece como `***` em todas as linhas do log, e o registo tem uma
trava que recusa escrever se algo com cara de credencial lá chegar.

## 10 · O QUE NÃO MUDOU

A capacidade continua `PROVEN`. A política continua `CONDICIONAL`, a classe
`APIFY`, a prioridade a mesma, o motivo canônico o mesmo. Os dois tetos, a
taxonomia de falha e o registo estão intocados. Nada fora do SINTONIA SCRAP foi
desenvolvido.

## 11 · O QUE CONTINUA DESCONHECIDO

- **Por que o objeto veio sem transcrição.** As duas hipóteses estão nomeadas e
  nenhuma está medida. Os bytes que responderiam já não existem.
- O custo **liquidado** desta corrida. `usageTotalUsd = 0` é leitura, não conta
  fechada.
- Se `EAkcA_2FDN8` ainda tem legenda pública.

## 12 · RISCO RESTANTE

O bruto de qualquer corrida paga futura continua a morrer no checkout seguinte,
a menos que volte ao repositório ou vá para o dono forward. A forma agora
sobrevive; os bytes não. E uma rota `PARTIAL` é uma rota que corre e gasta —
promovê-la a `PROVED` exige uma corrida que entregue, e essa corrida é dinheiro
que ninguém autorizou ainda.
