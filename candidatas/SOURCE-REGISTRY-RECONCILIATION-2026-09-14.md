# RECONCILIAR O REGISTO DE IDENTIDADE — O CENSO, E POR QUE O ATLAS NÃO FOI ESCRITO

**Data:** 2026-09-14 · **Branch:** `claude/italy-agricultural-sources-discovery-dfba81`
· **Prova:** [`build/source-registry-reconciliation/`](../build/source-registry-reconciliation/)
(5 ficheiros CSV)

> **A pergunta:** como reconstruir UM ÚNICO Atlas canónico contendo
> corretamente todos os `SOURCE_ID` já emitidos, sem perder fonte, renomear
> identidade, reescrever história ou criar colisões?
>
> **A resposta:** o censo está feito e fechado — **255 identidades**, com
> proveniência de todas as 255. Mas **cinco números têm duas fontes vivas ao
> mesmo tempo**, e o §16 proíbe publicar um Atlas final nessa condição. O que
> ficou é o censo completo, o plano linha a linha, e a trava que impede o
> problema de voltar.

---

## A DESCOBERTA QUE MUDA O TAMANHO DO TRABALHO

A missão anterior mediu «o registo está partido em quatro branches paralelas».
Medido agora com mais cuidado, **as branches não são paralelas** — e uma delas é
quase o conjunto completo:

| linha | IDs | italianos | relação com `main` |
|---|---|---|---|
| **`italy-source-qualification-v1`** | **254** | **195** | 11 commits à frente, **0 atrás** |
| `main` | 114 | 55 | é a base |
| esta branch (`discovery`) | 114 | 55 | 5 à frente, **0 atrás** |
| `passport-tags-italy-v1` | 71 | 12 | 280 à frente / 245 atrás — divergente |

```
IDS_ONLY_QUALIFICATION = 140      IDS_ONLY_PASSPORT  = 1
IDS_ONLY_MAIN          =   0      IDS_ONLY_CORRENTE  = 0
IDS_ONLY_OUTRAS        =   0      (nada vive só na história)
```

**`qualification` tem 254 dos 255.** A reconciliação não é «fundir quatro
registos»: é **tomar o Atlas da `qualification`, acrescentar 1 identidade
exclusiva da `passport-tags`, e resolver as 5 colisões.**

### A linha de integração, e por que não foi escolhida pelo nome

`main` **existe agora** (não existia quando medi em missões anteriores) e é
`f437ff11`, de 12/09. Mas ela não vence por ser a `default branch`:

- `main` é **antepassada** de `qualification` **e** desta branch, e as duas
  estão **0 commits atrás** dela → integrar em `main` **não perde nada de
  nenhuma das duas**;
- `qualification` traz o registo (254 IDs) e `discovery` traz o trabalho
  funcional das últimas 5 missões;
- `passport-tags` é a única genuinamente divergente (245 commits atrás) — e
  tem **1** identidade exclusiva, que não se perde por ser uma.

**Decisão:** a linha de integração é **`main`**, por ancestralidade — não por
ser default, não por volume. Esta missão **não fez o merge**: o §23 manda não
reescrever branches, e a escrita do Atlas está bloqueada de todo o modo.

---

## O CENSO — 255 IDENTIDADES, TODAS COM PROVENIÊNCIA

```
F  ID_POPULATIONS_FOUND    2 emissores reais, de 7 candidatos medidos
G  GLOBAL_SOURCE_IDS     255
H  IT_SOURCE_IDS         196     (ES 39 · EU 14 · FR 6)
   proveniência          245/245 → 255/255 reconstruída
```

### Quem emite identidade, e quem só a cita

Esta distinção teve de vir primeiro. Um `SOURCE_ID` aparece em **192 ficheiros
só na `main`** — runs, amostras, ledgers, relatórios. Quase todos **citam** uma
identidade que outro emitiu.

| emissor | IDs | versões lidas |
|---|---|---|
| `docs/fontes/ATLAS-DE-FONTES-EAME.md` | 214 | **31** (a história, não as pontas) |
| `candidatas/ITALY-SOURCE-MASTER-V1.json` | 54 | 1 |
| `MASTER-SOURCE-REGISTRY.json` *(nome promissor)* | **0** | 1 |
| `SOURCES.json`, `sources.json`, contratos | 0 | 7 |

O ficheiro chamado literalmente `MASTER-SOURCE-REGISTRY.json` **não emite
nenhuma identidade**. Foi medido por honestidade, não por suspeita.

### A classificação, e a soma fecha

```
MISSING_FROM_CURRENT_ATLAS   181      HISTORICAL_RED            8
SAME_SOURCE_MULTIPLE_IDS      36      SAME_ID_DIFFERENT_SOURCE  5
SAME_ID_SAME_SOURCE           24      ONLY_IN_ONE_BRANCH        1
                                      ───────────────────────────
                                      SOMA                    255  ✓
```

---

## AS 5 COLISÕES VIVAS — E POR QUE NÃO AS RESOLVI

O §7 proíbe escolher sozinho, e a razão está num número: **`IT-T4-001` tem
4.033 citações no repositório.** Renomear a errada faria 4.033 referências
apontarem para outra fonte — em silêncio.

| ID | citações | afirmação A | afirmação B |
|---|---|---|---|
| **`IT-T4-001`** | **4.033** | Ministero della Salute · `dati.salute.gov.it` — **28 versões do Atlas** | ARPAV vendite fitosanitari · `arpa.veneto.it` — 4 versões, em `cool-dijkstra-4agznu` |
| `ES-T4-005` | 426 | MAPA · `mapa.gob.es/es/agricultura` | MAPA · `servicio.mapa.gob.es/regfiweb` |
| `IT-T10-002` | 90 | BMTI — mercado de cereais | OpenStreetMap via Overpass |
| `IT-T10-001` | 30 | ISMEA Mercati | ISTAT distribuzione fitosanitari · ARPAV |
| `IT-T10-003` | 24 | ISTAT commercio estero · **`coeweb` (sede encerrada)** | ISTAT distribuzione fitosanitari |

Cada afirmação está em `COLLISIONS.csv` com data de primeira atribuição, número
de versões que a sustentam, se tem cerca declarada e se tem evidência. **A
decisão é de gente**, e a regra para quem decidir está escrita: dar número novo
à que tem **menos** citações, nunca à que tem mais.

```
Q  LOST_SOURCE_IDS         0
R  UNRESOLVED_COLLISIONS   5     → §16 impede publicar Atlas final
```

---

## O QUE A MISSÃO CONSERTOU DE VERDADE

### A trava contra a sobrescrita silenciosa

Era o pedido central do §19–§20, e é a única mudança de código desta missão.
`scan_sources.py` agora **para** quando duas fichas declaram o mesmo
`SOURCE_ID`, em vez de ficar com a última:

```
SOURCE_ID DUPLICADO NO ATLAS — o mapa nao e gerado com identidade ambigua.
  EU-T4-001 aparece na linha 169 e outra vez na linha 1357
```

**Teste de mutação, com controle de duas faces:**

```
W  SCANNER_DUPLICATE_GUARD   adicionado, e FALHA em vez de escolher
X  MUTATION_TEST             Atlas limpo → passa
                             ID duplicado injetado → REPROVA e nomeia as linhas
                             Atlas restaurado → volta a passar, diff vazio
```

Sem o controle negativo («passa no Atlas limpo»), um scanner que falhasse
sempre também passaria o teste de mutação — e ninguém notaria.

### Doze provas permanentes

`tests/test_source_registry.py`, 12 testes, todos a passar: população não
encolhe, faixa expandida, proveniência rastreável, nenhuma colisão nova, Atlas
sem duplicata, T1–T12 válido, T13 não cresce, índice fecha com o Atlas, e o
master JSON não vira dono.

---

## QUATRO DEFEITOS DO MEU PRÓPRIO LEITOR, APANHADOS ANTES DE PUBLICAR

Os quatro produziram números que eu ia publicar, e três deles eram alarmes
falsos.

**1 · «36 colisões de identidade» — e eram 5.** O meu separador de blocos
varria as URLs de **toda a prosa** da ficha, e a prosa fala de outras fontes.
Resultado: `recherche-entreprises.api.gouv.fr` — uma API francesa de empresas —
aparecia como rota de fichas espanholas e europeias. Publicar 36 teria alarmado
a casa por nada. Agora os campos saem só da **cerca declarada**.

**2 · 17 identidades quase perdidas.** O Atlas declara
`SOURCE_ID: ES-T7-001..027` — uma **faixa**. O meu leitor apanhava os dois
extremos e perdia 002 a 026. Elas apareciam como «citadas e nunca emitidas», e
um Atlas reconciliado sem elas teria **perdido 17 fontes sem acusar nada**.

**3 · Ler as pontas das branches não basta.** `ES-T4-004` — com 206 citações e
três ficheiros de amostra próprios — aparecia como fantasma. Ele existe em **2
das 31 versões históricas** do Atlas e em nenhuma das pontas. Identidade emitida
e depois retirada **continua gasta**: reatribuí-la quebraria as referências que
ficaram. A população passou a ser lida na história inteira.

**4 · Três formas de declaração, e eu tratava-as como uma.** O Atlas declara
identidade em **ficha** (título + cerca), em **tabela de estado**
(`| SOURCE_ID | camada | origens |`) e **não** declara no preâmbulo, onde
apenas ensina o formato — *«Exemplos: `EU-T4-001`, `IT-T12-001`»*. Ignorar as
tabelas fazia `ES-T8-001`, com **7.634 citações**, parecer um fantasma; contar o
preâmbulo inventava `IT-T12-001`, que não tem ficha nenhuma.

E um quinto, no red team: o **ataque 14 saiu «detetor cego»** porque eu media
buracos de sequência no `IT-T3`, que por acaso é uma sequência completa — o
controle não podia disparar. Corrigido para a população inteira, onde há 4
territórios com buraco.

---

## O QUE ESTE CENSO ACHOU E NINGUÉM PROCURAVA

### 18 identidades em uso e nunca registadas

```
ES-T2-002 · ES-T2-003 · ES-T3-002 · ES-T4-004 (206 citações) · ES-T5-003
ES-T5-004 · ES-T6-001 (65) · ES-T9-002 · EU-T8-001 · EU-T9-001 · FR-T11-001 …
```

São números que o sistema **usa** — com ficheiros de amostra próprios — e que
**nenhum registo jamais declarou em ficha**. Não são perda de reconciliação: são
um buraco anterior a ela. E o número está **gasto**: reatribuí-lo faria as
referências existentes apontarem para a fonte nova.

Dois dos 19 candidatos não eram órfãos e saíram da lista: `IT-T1-024` só aparece
na **minha própria prosa** da missão passada, como exemplo do que *não* alocar; e
`ES-T9-999` é sentinela de um ficheiro de teste.

### A faixa que o mapa não vê

O Atlas declara 23 IDs simples **e uma faixa de 27**. O regex do scanner não
entende `..`, então **as 27 fontes da faixa `ES-T7-001..027` existem no censo e
não no mapa**. Buraco anterior a esta missão, agora medido e declarado — não
corrigido, porque corrigi-lo mudaria a contagem publicada do Índice e isso é
outra decisão.

### O mecanismo de alias já existia

O §8 mandava não inventar mecanismo para «mesma fonte, dois IDs». Não foi
preciso: o Atlas já tem o campo **`DERIVA_DE`**, usado assim —

```
DERIVA_DE:  EU-T5-001 (mesma fonte, mesma rota, recorte próprio)
```

Os **36 pares** de identidade duplicada resolvem-se declarando esse campo, e
**nenhum ID se apaga**.

---

## O PLANO — 273 LINHAS, POR ORDEM DE EXECUÇÃO

| ordem | ação | identidades |
|---|---|---|
| **0** | **NÃO TOCAR** — identidade gasta sem registo | **18** |
| **1** | **BLOQUEADO — decisão de gente** | **5** |
| 2 | declarar `DERIVA_DE` — nenhum ID se apaga | 36 |
| 3 | trazer para o Atlas da linha de integração | 181 |
| 4 | fundir campos pela ordem de confiança | 24 |
| 5 | preservar como gasto (veredito negativo) | 8 |
| 6 | trazer, com a proveniência escrita | 1 |

A ordem importa: **resolver as 5 colisões desbloqueia as outras 250.** Trazer
os 181 ausentes antes disso traria a colisão junto.

### A ordem de confiança, aplicada campo a campo

Nunca «a branch mais nova vence». O peso é da prova:

```
evidência preservada  50   ·  rota declarada  20  ·  ficha do atlas  15
veredito observado    10   ·  dono nomeado     5  ·  data da branch   0
```

Medido: evidência preservada (50) vence ficha do Atlas sem evidência (30).

---

## ENTREGA

```
A  BRANCH        claude/italy-agricultural-sources-discovery-dfba81
B  INITIAL_HEAD  0a30bffe
C  FINAL_HEAD    (o commit desta missão)
D  REMOTE_HEAD   0a30bffe no início — já preservado
E  MAIN_HEAD     f437ff11 · 2026-09-12 · antepassada desta branch e da qualification

F  ID_POPULATIONS_FOUND        2 emissores reais (7 candidatos medidos)
G  GLOBAL_SOURCE_IDS         255
H  IT_SOURCE_IDS             196

I  SAME_ID_SAME_SOURCE        24
J  SAME_ID_DIFFERENT_SOURCE    5     ⚠️ todas VIVAS
K  SAME_SOURCE_MULTIPLE_IDS   36

L  IDS_ONLY_QUALIFICATION    140
M  IDS_ONLY_PASSPORT           1
N  IDS_ONLY_CURRENT_BRANCH     0
O  IDS_ONLY_MAIN               0
P  IDS_ONLY_OTHER              0

Q  LOST_SOURCE_IDS             0
R  UNRESOLVED_COLLISIONS       5

S  ATLAS_BEFORE               23 fichas      T  ATLAS_AFTER   23  (não escrito)
U  IT_ATLAS_BEFORE             2             V  IT_ATLAS_AFTER  2

W  SCANNER_DUPLICATE_GUARD    adicionado — FALHA em vez de escolher a última
X  MUTATION_TEST              passa, com controle de duas faces

Y  INDEX_RESULT               regenerado pelo gerador · 23 → 23 · fecha com o scanner
Z  SYSTEM_MAP_RESULT          MAPA=OK · 102 peças · 354 ligações · peça nova
                              C-REGISTO-IDENTIDADE · P8 corrigido (o teste voltou
                              ao C-TESTES, seu dono) · P9 reprova só por
                              .github/workflows/scrap-social.yml — PRE_EXISTING
AA REGRESSION_RESULT          720 testes (+12 meus) · 36 falhas · 32 nomes
                              distintos, idênticos antes e depois → NEW_FAILURE = 0

AB SOURCE_IDS_CREATED          0
AC COLLECTION_DELTA            0     AD RAW_DELTA   0     AE WAITING_ROOM_DELTA  0
   DERIVED / STRUCTURED / ADMISSION_DELTA   0 · 0 · 0

AK ARTEFATOS   build/source-registry-reconciliation/
               ALL-SOURCE-IDS.csv        1.714 linhas
               BRANCH-COVERAGE.csv         255
               COLLISIONS.csv               15 afirmações sobre 5 IDs
               DUPLICATE-SOURCES.csv        36
               RECONCILIATION-PLAN.csv     273

AF KNOW_HOW_DELTA   ATUALIZAÇÃO NECESSÁRIA — texto final abaixo
```

**`ITALY-SOURCE-MASTER-V1.json`:** `CAN_RETIRE_AS_IDENTITY_OWNER = NO, ainda
não.** Ele carrega 54 identidades históricas e **1 delas não está em nenhum
Atlas**. Pode ser retirado como dono **depois** de as 54 estarem no Atlas
reconciliado — não antes. Não foi apagado nem alterado.

**Red team:** 20 ataques · **19 OK · 1 SALA_VAZIA** · 0 falhas · 0 detetores
cegos. `SALA_VAZIA` não é aprovação: é o detetor provado sem nada para atacar,
porque o Atlas não foi reescrito.

---

## KNOW_HOW_DELTA — *atualização necessária*

> Não crio cabeça nova. Texto em forma final, número em branco.

### § — O CENSO DE IDENTIDADE LÊ-SE NA HISTÓRIA, E EM TRÊS FORMAS

O §119 escreveu a lei: **aloca-se contra a população inteira, nunca contra o
dono declarado.** Falta a parte de como se lê essa população, e ela tem três
regras que custaram caro em 14/09/2026:

**1 · Na história, não nas pontas.** `ES-T4-004` existe em 2 das 31 versões do
Atlas e em nenhuma ponta de branch. Identidade emitida e depois retirada
**continua gasta**. Ler só o estado atual dá uma população menor que a real, e o
número que falta é exatamente o que vai colidir.

**2 · Em três formas de declaração, e uma não é declaração.** O Atlas declara
identidade em **ficha** (título + cerca de campos) e em **tabela de estado**
(`| SOURCE_ID | camada | origens |`). No **preâmbulo**, onde ensina o formato,
ele **não declara** — *«Exemplos: `EU-T4-001`, `IT-T12-001`»* são documentação.
Medido: ignorar tabelas faz `ES-T8-001`, com 7.634 citações, parecer fantasma;
contar o preâmbulo inventa `IT-T12-001`, que não tem ficha.

**3 · A faixa é população, não dois números.** `SOURCE_ID: ES-T7-001..027` são
**27** identidades. Um censo que apanha só os extremos perde 25, e um Atlas
reconciliado a partir dele perde 25 fontes **sem acusar nada**.

**E separar EMISSOR de CONSUMIDOR vem antes de tudo.** Um `SOURCE_ID` aparece em
192 ficheiros só na `main`; quase todos citam. Tratar um nome de ficheiro de run
como atribuição inventa emissores que nunca existiram.

### § — O CAMPO DE ALIAS JÁ EXISTE, E CHAMA-SE `DERIVA_DE`

Quando a mesma fonte recebeu dois números, não se apaga nenhum e não se inventa
mecanismo: o Atlas já tem o campo, usado assim —

```
DERIVA_DE:  EU-T5-001 (mesma fonte, mesma rota, recorte próprio)
```

Medido: 36 pares de identidade duplicada, todos resolúveis por escrita deste
campo. Antes de propor um mecanismo novo de identidade, procurar o que o
registo já faz.

### § — A TRAVA DE DUPLICATA FALHA, NÃO ESCOLHE

`scan_sources.py` indexava fichas de modo que um `SOURCE_ID` repetido ficava com
a última e perdia a primeira **sem erro** — a colisão aparecia como uma fonte
que desapareceu. A trava correta **para a geração do mapa** e nomeia as duas
linhas.

**E a trava precisa de controle de duas faces:** um scanner que falhasse sempre
passaria o teste de mutação. Provam-se as duas — Atlas limpo passa, Atlas com
duplicata reprova.

### § — UM ALARME FALSO CUSTA A CONFIANÇA DA MEDIÇÃO INTEIRA

O primeiro leitor deste censo produziu **«36 colisões de identidade»**. Eram
**5**. As outras 31 nasciam de o leitor varrer URLs de **toda a prosa** da
ficha — e a prosa de uma ficha fala de outras fontes. Uma API francesa de
empresas aparecia como rota de fichas espanholas.

**Lei:** campo de identidade lê-se só onde o registo o **declara**. Rota citada
em prosa vive noutra coluna, e não decide identidade. Um número alarmante
publicado sem ser olhado gasta mais do que o defeito que ele denuncia.

---

## EM PORTUGUÊS SIMPLES

**Antes existiam 255 nomes de fonte espalhados por dois cadernos, em quatro
cópias diferentes do projeto.**

**Nenhuma gaveta foi escolhida no chute.** Fui ler a história inteira dos
cadernos — 31 versões — e não só o que está em cima da mesa hoje. Descobri de
onde veio **cada um dos 255 nomes**: em que dia, em que gravação, e em que
caderno.

E descobri uma coisa boa que ninguém sabia: **um dos cadernos já tem 254 dos
255 nomes.** O trabalho não é juntar quatro cadernos — é pegar nesse, somar
**um** nome que só existe noutro, e resolver cinco brigas.

**As cinco brigas:** cinco números foram dados a **duas fontes diferentes ao
mesmo tempo.** A pior é um número que aparece **4.033 vezes** no projeto: num
caderno ele é o Ministério da Saúde italiano, noutro é a agência ambiental do
Veneto. Se eu escolher a errada, **4.033 lugares passam a apontar para a fonte
errada — e ninguém vê.** Por isso **não escolhi**. Deixei as duas versões
escritas, com a data de cada uma, para quem decidir.

**Nenhum nome foi perdido. Nenhum nome novo foi criado.**

**E consertei a coisa mais perigosa:** o programa que lê o caderno **agora
para** quando encontra dois nomes iguais. Antes ele ficava com o último e a
outra fonte **desaparecia da lista sem erro nenhum**. Testei de propósito:
duplicei um nome, o programa parou e disse em que duas linhas estava o problema.
Depois devolvi o caderno ao estado original.

**Achei também 18 nomes que o sistema usa e que nunca foram anotados em caderno
nenhum** — um deles aparece em 206 lugares. Não são perda desta arrumação: são
um buraco que já existia. E esses números **estão gastos**: dá-los a outra fonte
faria os 206 lugares apontarem para a coisa errada.

**Quatro vezes o meu próprio leitor me deu número errado, e eu vi antes de
publicar.** A pior: ele dizia **36 brigas** quando eram **5** — porque estava a
ler endereços do texto solto da página em vez de só dos campos declarados. Se eu
tivesse publicado 36, teria assustado a casa por nada.

**De agora em diante, nome novo de fonte só se dá contra este censo de 255.**

---

## VEREDITO

```
VEREDITO = PARTIAL
```

**Por que não PASS.** O §32 exige «colisões resolvidas ou inexistentes» e «Atlas
único atualizado». Há **5 colisões vivas** e o §16 é literal: *«Se houver colisão
sem solução segura: não publicar Atlas "final".»* Resolver uma delas por conta
própria é o único erro irreversível possível nesta missão — 4.033 referências
dependem do `IT-T4-001`.

**Por que não BLOCKED.** Quase tudo o que o PASS pedia está feito e provado:

| exigência | estado |
|---|---|
| todas as populações de ID encontradas | ✓ 2 emissores reais, de 7 medidos |
| proveniência de cada ID conhecida | ✓ **255 de 255** |
| união fechou | ✓ soma = 255 |
| zero perda | ✓ `LOST_SOURCE_IDS = 0` |
| zero `SOURCE_ID` novo | ✓ 0 |
| **scanner falha em duplicata** | ✓ **com teste de mutação de duas faces** |
| Índice regenerado | ✓ 23 → 23, fecha com o scanner |
| System Map regenerado | ✓ 102 peças, P8 corrigido |
| regressão sem falha nova | ✓ 32 nomes idênticos antes e depois |
| Collection intocada | ✓ todos os deltas = 0 |
| colisões resolvidas | ✗ **5 vivas, bloqueadas por desenho** |
| Atlas único atualizado | ✗ **impedido pelo §16** |

**O que desbloqueia, e é pouco:** cinco decisões humanas, uma por colisão, com a
evidência já reunida em `COLLISIONS.csv`. Feitas essas, o plano de 273 linhas
executa-se em ordem — e `qualification` já tem 254 dos 255 nomes prontos.

```
HARD STOP
```
