# SM-P3 · O G7/G8/G8B CHEGA AO ENDEREÇO OFICIAL

## O ENDEREÇO

```
https://sintonia-eame-preview.vercel.app/system-map/
```

É este, e continua a ser este. Guarde-o. Não muda com commit novo, build nova,
nem com o nome da linha que gerou o mapa.

    O ENDEREÇO É DO PRODUTO. O DEPLOYMENT É DA ENGENHARIA.

**Estado: PUBLICADO E VERIFICADO NO ENDEREÇO OFICIAL.**

---

## O QUE ESTAVA ERRADO

O `G7`/`G8`/`G8B` fechou em `claude/system-map-g7-g8-visual-clarity-v1@85a24528`
com `G7=PASS`, `G8=PASS`, `G8B=PARTIAL`, e foi visto a funcionar — **num
deployment de preview**. O endereço oficial continuou, de 2026-09-09 até
2026-09-14, a servir a versão anterior.

```
PREVIEW READY  !=  MISSION DONE
CAN DO         !=  DID DO
```

Quem só tinha o endereço oficial não viu nada daquele trabalho. Medido antes de
mexer em coisa nenhuma:

| | |
|---|---|
| `/system-map/` no endereço oficial | HTTP 200 · **9.254 B** |
| o mesmo ficheiro na versão aprovada | **12.291 B** |
| `deployment.generated.json` no ar | `SOURCE_BRANCH=release/canonical` · `DEPLOYED_COMMIT=9ae641bd` · `BUILD_TIME=2026-09-09T04:37Z` |

A linha que alimenta o alias **não é** `main` e **não é** a branch do mapa: é
`release/canonical`, a branch de produção do projecto Vercel. Não foi assumido —
foi **lido do artefacto que o próprio endereço serve**.

---

## POR QUE NÃO SE PROMOVEU O DEPLOYMENT INTEIRO

As duas linhas separaram-se em `1c99a48b` — `release/canonical` com +70 commits,
a linha do mapa com +180. Promover `85a24528` inteiro por cima do que o alias
serve daria:

```
ficheiros APAGADOS      15
ficheiros REESCRITOS   139
```

Entre os apagados: `italy-label-intelligence.js`, `italy-label-lexicon.js`,
`.github/workflows/portao-do-release.yml`, `system-map/CANONICAL-PUBLICATION.json`,
`system-map/scripts/portao_da_promocao.py`. Entre os reescritos: `portale.html`,
`casa.html`, `index.html`, `meeting-intelligence-snapshot.json`.

```
SAFE_TO_PROMOTE_WHOLE_DEPLOYMENT = NO
INTEGRATION_METHOD               = SELECTIVE_INTEGRATION
```

É a mesma recusa da `SM-P2`, pelo mesmo motivo, com números novos.

    A ROTA RESPONDER NÃO É A PÁGINA ESTAR INTEIRA.

### ⚠️ O REPOSITÓRIO CHEGOU RASO, E ISSO MENTIU SOBRE A HISTÓRIA

Primeira medição de `git merge-base release/canonical HEAD`: **vazio**, e
`--is-ancestor` a dizer `NO`. Lido à letra, isso é *«duas histórias sem
antepassado comum»* — e uma conclusão dessas mudaria a missão inteira.

Era um clone **raso**. `.git/shallow` existia, `git rev-list --count HEAD` dava
**50** commits, e os «commits-raiz» eram enxertos.

```
    UM CLONE RASO NÃO DIZ «NÃO SEI» — DIZ UMA RESPOSTA ERRADA
    COM A MESMA CARA DE UMA RESPOSTA CERTA.
```

Depois de `git fetch --unshallow`: base em `1c99a48b`, 70 contra 180. Antes de
concluir seja o que for a partir de topologia de Git, confirmar que a história
inteira está no disco.

---

## O QUE ENTROU

**60 ficheiros.** Zero ficheiros do portal fora de `/system-map/` — provado, não
afirmado:

```
$ git diff --name-only 9ae641bd 0f08d7a2 -- italia-portale/ | grep -v client/system-map/
(vazio)
```

| superfície | ficheiros | porquê |
|---|---:|---|
| `system-map/` · `italia-portale/client/system-map/` | 54 | o produto desta missão |
| `.github/workflows/system-map.yml` · `portao-do-release.yml` | 2 | sem isto o portão do release **morre antes de medir** |
| `data/derivados/*.json` (3) · `regras/LEIA-ANTES-DE-COLETAR.md` | 4 | saídas **declaradas** da cadeia; o `.vercelignore` não as envia ao deploy |

Collection · Intelligence · Sala · banco · migrations · research: **0 ficheiros**.

### A tela aprovada é a tela que está no ar — byte a byte

Medido **no endereço oficial**, depois do deploy, contra `85a24528`:

```
index.html    8dbd7bf8cf0d00f72404283278528b22   IDÊNTICO ao aprovado
map.js        7d48938a5f0d1ff3f4d5e11cae57c6d1   IDÊNTICO ao aprovado
map.css       a90ac72b5d303c28219b78adaa4f3ed7   IDÊNTICO ao aprovado
freshness.js  689628d8006311350e583ad1d8fc7fd6   IDÊNTICO ao aprovado
```

Só `state.generated.json` difere, e **tem de** diferir: ele é o mapa **desta**
árvore, regerado pela cadeia canónica — nunca copiado de outra linha.

    O MAPA É DERIVADO DO REPO. O REPO NÃO É DERIVADO DO MAPA.

---

## O QUE ESTA MISSÃO ENCONTROU PARTIDO, E CONSERTOU

### 1 · O portão do release teria morrido antes de medir

`portao-do-release.yml` tinha o **seu próprio** leitor do manifesto:

```python
print('\n'.join(c['REGERAR'] + c['VALIDAR']))
```

Isso valia enquanto cada passo era uma string. O `G4` deu forma a cada passo
(`{STEP_ID, EXECUTABLE, INPUTS, OUTPUTS}`), e um `join` sobre objectos não avisa
que a forma mudou — levanta `TypeError`, e o portão morre **antes** de medir
seja o que for.

```
    DOIS SITIOS COM A LISTA DOS PASSOS SÃO DUAS CADEIAS.
    A SEGUNDA NÃO FALHA NO DIA EM QUE É ESCRITA.
```

Passa a chamar `correr_a_cadeia.py`, o leitor único do lado Python — o mesmo
manifesto que `publicar_no_deploy.mjs` lê no build.

### 2 · O CI corria 7 dos 20 passos da cadeia

`system-map.yml` tinha os sete passos escritos à mão. A cadeia tem vinte desde o
`G5`. O mapa que o CI validava não era o mapa que a build publica. Passa pelo
mesmo corredor, e os dez portões novos do `G5`/`G6`/`G7` entram no job das regras.

### 3 · Uma varredura declarada a menos do que a real

`CENSO_CARDS_SENSORES` declarava `superficie/ coleta/ guarda/`. O código greppa
**sete** gavetas — junta `motor/ orquestrador/ medidas/ regras/`. A falta só
aparece numa árvore onde o grep acerte numa das quatro que faltavam. Nesta
acerta, em `motor/v21_completude_oportunidade.py`.

### 4 · Nove números declarados que eram de outra árvore

`MEDIDO_VARRE` publica quantos ficheiros cada passo varre. Os números vinham
medidos na árvore do `G7` (1499 ficheiros); esta tem 1376. Remedidos, um a um.

```
    UM NÚMERO DECLARADO QUE NINGUÉM CONFERE É UMA LEMBRANÇA.
    UM NÚMERO CONFERIDO CONTRA OUTRA ÁRVORE É UMA LEMBRANÇA COM PORTÃO.
```

### 5 · A ordem de regeneração não é uma questão de gosto

```
REGERAR  →  REGERAR_A_MAO  →  REGERAR
```

Correr `REGERAR_A_MAO` **depois** deixa `architecture.generated.json` a registar
o SHA antigo dos três derivados, e `P1_SEM_DRIFT` reprova. Correr **só antes**
deixa a matriz a ter lido um `sources.generated.json` de antes da rodada, e a
classe de frescura cai para `EXPECTED_PREVIOUS_CYCLE` — o que faz
`e_sem_a_classe_declarada_volta_a_ser_defeito` reprovar. As duas passagens de
`REGERAR` fecham as duas pontas.

---

## A DECLARAÇÃO QUE NÃO ATRAVESSOU, E PORQUÊ

`CANONICAL_OWNERS` trazia da linha do mapa um dono canónico para
`data/samples/RUN-MANIFEST.json` (C-PROCEDENCIA), com a porta em
`regras/proveniencia.py::acrescentar`.

**Nesta árvore essa porta não existe** — `regras/proveniencia.py` tem `gravar` —
e três peças escrevem o manifesto: `C-ESTRADA-PDF`, `C-ORQUESTRADOR`,
`C-PROCEDENCIA`. A consolidação que torna a decisão verdadeira é código de
**Coleta**, e uma missão de publicação do mapa não mexe em Coleta.

```
    UMA DECISÃO CUJA PORTA NÃO EXISTE NESTA ÁRVORE
    NÃO É UMA DECLARAÇÃO SOBRE ESTA ÁRVORE.
```

A entrada sai. A **medição fica**, e está no ar agora:
`ARTEFACT_MULTIPLE_AUTHORS` publica o ficheiro e os três autores, com
`owner_elected` por ordem alfabética e a frase que diz que isso não é um dono. O
porquê fica escrito em `CANONICAL_OWNERS_NOTA`, dentro do próprio
`architecture.declared.json`, com o caminho de volta: **quando a consolidação
chegar a esta linha, a entrada volta palavra por palavra.**

E as duas provas que exigem a consolidação continuam a correr e continuam
**vermelhas**. É assim que a dívida se vê.

---

## OS PORTÕES, MEDIDOS DOS DOIS LADOS

Baseline = `release/canonical@9ae641bd`, o commit que o alias servia.

| portão | antes | depois | classificação |
|---|---|---|---|
| `SYSTEM MAP CHECK` (P1..P10) | PASS | **PASS** | — |
| `RELEASE · PROVENIENCIA` | — | **PASS** | — |
| `RELEASE · SYSTEM MAP CHECK` | — | **PASS** | — |
| `RELEASE · PORTAL REGRESSION CHECK` | — | **PASS** · 73/73 (2 NON MISURABILI: W2 O1) | — |
| `MAP RULES CHECK` | **FAIL** · 2 | **FAIL** · 3 | vermelho herdado, defeitos remedidos |
| `COLETA CHECK` | **FAIL** | **FAIL** | **PREEXISTING — o mesmo defeito, os mesmos números** |

### `COLETA CHECK` — medido, não presumido

Log do baseline (2026-09-09) e log de hoje, lado a lado:

```
COLETOR_CARIMBA_A_DATA            faltam hoje 31   chao 26   PIOROU
COLETOR_SEPARA_A_FONTE_DO_FATO    faltam hoje 25   chao 20   PIOROU
COLETOR_REGISTA_O_QUE_DESCARTOU   faltam hoje 35   chao 30   PIOROU
PADRAO_DA_COLETA=FAIL
GOLDEN_PATH_PDF=FAILED_PRECONDITION
```

Iguais nos seis valores. `PREEXISTING`, e dito depois de olhar.

    NÃO SE USA «JÁ ESTAVA VERMELHO» SEM MEDIR.

### `MAP RULES CHECK` — o defeito é antigo, o instrumento é que é novo

Antes, 2 falhas: `regua_que_carimba_nao_e_regua_que_mede`,
`E2_receita_continua_com_um_consumidor`. As duas ficam **corrigidas** pelo `G7`.

Depois, 3 falhas, e são **uma só coisa**: `a_decisao_de_dono_esta_declarada`,
`so_a_proveniencia_escreve_o_manifesto`,
`a_porta_do_manifesto_existe_e_e_a_declarada` — a consolidação do RUN-MANIFEST
que vive na outra linha.

```
    O DEFEITO JÁ CÁ ESTAVA. O QUE CHEGOU FOI O MEDIDOR.
    INHERITED RED  !=  NEW DEPLOY REGRESSION.
```

`NEW_REGRESSIONS = 0`: nada na árvore piorou. `MAP RULES CHECK` não é um dos três
jobs do portão do release, por desenho, e está declarado como vermelho herdado em
`CANONICAL-PUBLICATION.json`.

As outras nove suítes de portões do mapa passam, em CI: `IMPRESSAO`,
`RECONCILIACAO`, `QUATRO_PLANOS`, `TOPOLOGIA_PERSISTIDA`, `IMPRESSAO_VERIFICAVEL`,
`CADEIA_IO`, `UMA_CADEIA_UM_DONO`, `ORDEM_POR_DEPENDENCIA`, `PAPEL_E_LEITURA`,
mais `TESTES_FRESCURA` (49 provas).

---

## A PROVA DEPOIS DO DEPLOY — NO ENDEREÇO OFICIAL, E NÃO NO DEPLOYMENT

```
OFFICIAL_URL_HTTP_STATUS          200
OFFICIAL_URL_SIZE                 12.291 B   (antes: 9.254 B)
OFFICIAL_URL_DEPLOYMENT_ID        dpl_DJh2v8t599ejrZyErxf1DtLwAuVN
OFFICIAL_URL_DEPLOYMENT_GIT_SHA   3ec314ec00d236b05eefafe3c12423ebdbf1786f
OFFICIAL_URL_SOURCE_BRANCH        release/canonical
MAP_BELONGS_TO_DEPLOYED_TREE      true
```

Lido **do alias oficial depois de publicar**, e não do deployment criado.

    DEPLOY CRIADO  !=  ALIAS ACTUALIZADO.
    HTTP 200       !=  CONTEÚDO NOVO.

Sinais exclusivos da versão nova, medidos na resposta do endereço oficial:

| sinal | onde | antes | agora |
|---|---|---:|---:|
| secção «Prova da ligação» | `index.html` | 0 | 1 |
| `OBSERVADA` · `PROVADA` · `DECLARADA` | `index.html` | 0 | 1 · 2 · 1 |
| KPI `kSemProva` (setas sem prova) | `index.html` | 0 | 1 |
| `ROLE` | `map.js` | 0 | 23 |
| `OWNER` | `map.js` | 0 | 7 |

E nos dados publicados: cada nó traz `ROLE`, `ROLE_CONFLICT`, `ROLE_EVIDENCE`,
`ROLE_PLANE`, `OWNER`, `OWNER_CONFLICT`, `OWNER_PLANE`, `PROVEN_PLANE`.

### O que o `G8`/`G8B` prometeu, e está no ar

```
peças 164 · papéis provados 118 · papéis NÃO SEI 41 · papéis em conflito 14
ligações 588 · ligações NÃO SEI 47 · conceitos 15 · com dono duplicado 8
```

Os quatro filtros de «Prova da ligação» estão **`checked` por omissão** no HTML
servido. A seta sem prova é *cinzenta, tracejada e leva um anel no meio* — três
sinais, para o estado não depender só da cor. «Mostrar caminho completo» não
atravessa nenhuma delas. `montante`/`jusante`, «Envia para»/«Recebe de»
continuam lá.

**`G8B` continua `PARTIAL`.** Nada nesta missão o promove, e o layout não foi
tocado.

### O resto do portal, no endereço oficial, depois do deploy

```
/                                   200 · md5 IDÊNTICO ao de antes
/accesso                            200 · md5 IDÊNTICO
/portale                            200 · md5 IDÊNTICO   (1.090.957 B)
/italy-label-intelligence.js        200 · md5 IDÊNTICO   (3.826.118 B)
/italy-label-lexicon.js             200 · md5 IDÊNTICO
/meeting-intelligence-snapshot.json 200 · md5 IDÊNTICO
/casa                               404  — e era 404 ANTES, no mesmo endereço
```

`/casa` está excluído do deploy pelo `.vercelignore` (linha 73), de propósito e
por escrito. Foi medido no deployment anterior antes de se chamar regressão a
isto.

---

## ROLLBACK

Registado **antes** de o alias mudar, e não depois do incidente:

```
ROLLBACK_DEPLOYMENT_ID  dpl_7FEtWcAGocDJHSre9sWKxbb45CvH
ROLLBACK_GIT_SHA        9ae641bd956b307d451a4bf8cec160c9e7f1b813
ROLLBACK_URL            https://sintonia-eame-preview-50bkql7k0-london-creative.vercel.app
```

Medido vivo depois do deploy novo: **HTTP 200, 9.254 B** — continua a servir
exactamente a versão anterior. O caminho de volta existe e está provado.

    ONE RECOVERY PLAN → ONE PROOF.

---

## A LEI QUE FICOU EM GIT

`system-map/CANONICAL-PUBLICATION.json` — o dono que **já existia** — ganha
`DEFINICAO_DE_MISSAO_FECHADA`. Nenhum documento novo foi criado para isto: uma
lei em dois sítios diverge, e a partir daí nenhuma das duas vale.

```
MISSION DONE        !=  PREVIEW READY
SYSTEM MAP DONE      =  OFFICIAL URL VERIFIED
HTTP 200            !=  CONTEÚDO NOVO
DEPLOY CRIADO       !=  ALIAS ACTUALIZADO
DEPLOYMENT URL      !=  OFFICIAL URL
```

Com as condições, os três passos de verificação pós-deploy, e a exigência de
registar alvo de rollback **antes** de mexer no endereço.

---

## O PROCESSO, DAQUI PARA A FRENTE

Não mudou desde a `SM-P2`, e esta missão passou por ele inteiro:

```
commit  →  preview da branch de trabalho
        →  PR para release/canonical
        →  PROVENIENCIA · SYSTEM MAP CHECK · PORTAL REGRESSION CHECK
        →  merge
        →  o mesmo endereço de sempre, com a versão nova
        →  VERIFICAR NO ENDEREÇO OFICIAL          ← o passo que faltava
```

O último passo é o que esta missão acrescenta. Sem ele, a missão anterior fechou
com tudo verde e o dono do produto a ver a versão velha.

---

## O QUE CONTINUA POR MEDIR, E O QUE FICA POR FAZER

- **A dívida do RUN-MANIFEST.** Três escritores, uma porta declarada que não
  existe nesta linha. É trabalho da linha da Coleta; o mapa observou, não
  corrigiu.
- **`MAP RULES CHECK` e `COLETA CHECK` continuam vermelhos.** Declarados, à
  vista, e não escondidos por esta missão.
- **Um literal na tela que o mapa não deriva.** O texto de ajuda do filtro diz
  *«hoje são 47 de 659»*. Nesta árvore são **47 de 588**: o numerador acerta por
  coincidência, o denominador é da árvore do `G7`. Não foi mexido porque
  `index.html` é byte a byte o aprovado — mas é um número escrito à mão numa tela
  cujo trabalho é não deixar números por derivar. Fica para quem tocar na tela.
- **`SYSTEM_MAP_CHECK=UNKNOWN` no artefacto de deploy.** Por desenho: o
  `.vercelignore` não envia a árvore inteira ao contentor, logo a build não
  regenera e não valida. Quem vale é o CI, e o artefacto diz `UNKNOWN` com o
  número exacto ao lado em vez de fingir verde.
- **`G8B` continua `PARTIAL`**, e os 15 conflitos de papel continuam publicados e
  por resolver. Não é trabalho desta missão.

---

## O QUE ESTA MISSÃO NÃO FEZ

Não redesenhou o mapa. Não reposicionou cartões. Não mexeu no layout, nas cores
nem na hierarquia visual. Não resolveu os conflitos de papel. Não promoveu o
`G8B`. Não abriu o `G9`. Não tocou na Collection, na Intelligence, na Sala, no
banco, em migrations, nem em coleta.
