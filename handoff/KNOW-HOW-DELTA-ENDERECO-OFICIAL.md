# DELTA PARA O KNOW-HOW CANÓNICO — O ENDEREÇO OFICIAL É O ÚLTIMO PASSO, E NÃO O PRIMEIRO

```
ORIGEM            SYSTEM-MAP-OFFICIAL-DELIVERY-V1
BRANCH            claude/system-map-official-delivery-v1  →  release/canonical
KNOW_HOW_LIDO     claude/sintonia-eame-know-how-v1 @ d64d8124
ÚLTIMA SECÇÃO     §116 · O ÚNICO PROJETO EXISTENTE QUE A PLATAFORMA ACEITA É A FONTE
NÚMERO DESTA      **por atribuir** — ver abaixo
```

> **O NÚMERO NÃO VEM ESCRITO DE PROPÓSITO.** O prompt desta missão apontava a
> linha do know-how em `3703f2d8` (`§115`). Medida no início desta missão: já ia
> em `d64d8124`, com `§116` escrito por **outra missão, duas horas antes**, com
> esta a correr. A linha anda enquanto se escreve nela.
>
> Herdar um número aqui seria escolher uma colisão e deixá-la para quem integrar.
> Quem aplicar isto atribui o número livre no momento em que aplicar.
>
> Esta missão tomou o caminho seguro por concorrência que o próprio pedido
> descreve: **o delta, no formato da casa, sem tocar na branch do know-how e sem
> criar um segundo know-how.**

A **regra** desta missão não fica só aqui nem só no chat: está versionada no dono
que já existia — `system-map/CANONICAL-PUBLICATION.json`, campo
`DEFINICAO_DE_MISSAO_FECHADA`. Este documento é a memória narrativa, não a lei.

---

## O QUE JÁ LÁ ESTÁ, E NÃO SE REPETE

O know-how já tem `ANÁLISE ESTÁTICA PROVA CAN DO · SÓ TELEMETRIA PROVA DID DO`,
já tem `UM SÍTIO ERRADO SEM RESULTADOS NÃO É UMA AUSÊNCIA DE RESULTADOS`, e já
tem `INHERITED RED ≠ NEW DEPLOY REGRESSION`. O que falta é o que acontece
**depois** de tudo isso ficar verde.

---

## A · UMA MISSÃO PODE FICAR VERDE INTEIRA E NÃO ENTREGAR NADA

O `G7`/`G8`/`G8B` fechou com o código aprovado, os portões verdes, vinte ataques
mortos e fotografias do antes e do depois. Durante cinco dias, quem abriu o
endereço que lhe tinham dado viu a **versão anterior**.

Nada do que estava escrito era falso. Faltava um passo que ninguém tinha nomeado.

```
    MISSION DONE   !=  PREVIEW READY
    SYSTEM MAP DONE =  OFFICIAL URL VERIFIED
```

O preview é a bancada da engenharia. Não se entrega uma bancada a quem pediu um
produto.

> **Corolário operacional.** Numa missão cujo produto é uma superfície visível, a
> última linha do plano não é *«os portões passam»*: é *«o endereço que o dono do
> produto guarda devolve o conteúdo novo, e eu fui lá ver»*.

---

## B · O ALIAS NÃO SE ADIVINHA — LÊ-SE DO QUE ELE PRÓPRIO SERVE

A pergunta *«que linha alimenta o endereço oficial?»* tinha três respostas
plausíveis e erradas à mão: `main`, a branch do portal, a branch do mapa.

A resposta certa estava **dentro do que o endereço serve**:
`/system-map/deployment.generated.json` publica `SOURCE_BRANCH`,
`DEPLOYED_COMMIT`, `BUILD_ID` e `BUILD_TIME` do que está no ar.

```
    O ARTEFACTO QUE O ENDEREÇO SERVE SABE DE ONDE VEIO.
    PERGUNTAR-LHE CUSTA UM GET; ADIVINHAR CUSTA UMA MISSÃO.
```

Era `release/canonical@9ae641bd`, de 2026-09-09. Nenhuma das três.

> **Corolário.** Um artefacto de deploy que carrega a sua própria procedência
> transforma «qual é a linha de produção?» de investigação em leitura. Quem
> desenha um publicador deve fazê-lo escrever isto mesmo quando ninguém ainda o
> pediu.

---

## C · UM CLONE RASO NÃO DIZ «NÃO SEI» — DIZ UMA RESPOSTA ERRADA

Primeira medição de `git merge-base <producao> <mapa>`: **vazio**.
`git merge-base --is-ancestor`: `NO`. `git rev-list --max-parents=0` devolveu dois
commits-raiz diferentes.

Lido à letra: *duas histórias sem antepassado comum*. Com essa conclusão, a única
integração possível seria copiar ficheiros à mão, e qualquer prova de «não se
perdeu nada» seria impossível de construir.

Era um clone raso. `.git/shallow` existia e `git rev-list --count HEAD` dava
**50**. Depois de `git fetch --unshallow`: base em `1c99a48b`, **70 contra 180**
commits, e um verdadeiro merge de três pontas disponível para conferir ficheiro a
ficheiro.

```
    UM CLONE RASO NÃO FALHA ALTO. ELE RESPONDE.
    E A RESPOSTA TEM A MESMA CARA DE UMA RESPOSTA CERTA.
```

> **Corolário operacional.** Antes de tirar **qualquer** conclusão de topologia de
> Git — ancestralidade, base comum, «estas linhas não se tocam» — confirmar
> `ls .git/shallow` e `git rev-list --count`. Um `merge-base` vazio é uma hipótese
> sobre o disco antes de ser um facto sobre a história.

Isto generaliza a `§112` (*«o que falta é a chave, e não o recurso»*): a mesma
família de erro, noutro andar. **O ambiente responde por si, e a resposta dele
parece uma resposta sobre o mundo.**

---

## D · PROMOVER UMA LINHA DIVERGENTE APAGA TRABALHO QUE NINGUÉM ESTÁ A OLHAR

A pergunta *«posso promover o deployment que já provei?»* responde-se com um diff,
não com uma intuição:

```
ficheiros APAGADOS      15      ficheiros REESCRITOS   139
```

Entre os que desapareciam: dois ficheiros de produto (`italy-label-intelligence.js`,
`italy-label-lexicon.js`), o portão do release da linha de produção, e o contrato
do próprio endereço canónico.

```
    SAFE_TO_PROMOTE_WHOLE_DEPLOYMENT
    NÃO É UMA OPINIÃO SOBRE O QUE EU MUDEI —
    É UM DIFF CONTRA O QUE ESTÁ NO AR.
```

E a integração selectiva tem um dever simétrico que se esquece com facilidade:
**o que a linha de destino tem e a de origem não tem.** Dois ficheiros
(`CANONICAL-PUBLICATION.json`, `portao_da_promocao.py`) teriam sido apagados por
um `git checkout <origem> -- <pasta>/` inocente. Conferido depois, ficheiro a
ficheiro, com merge de três pontas: em tudo o resto a versão de origem era
superconjunto da de destino.

---

## E · UMA DECLARAÇÃO CUJA PORTA NÃO EXISTE NESTA ÁRVORE NÃO É UMA DECLARAÇÃO SOBRE ESTA ÁRVORE

`architecture.declared.json` trazia uma decisão humana — *o dono canónico de
`RUN-MANIFEST.json` é C-PROCEDENCIA, a porta é `regras/proveniencia.py::acrescentar`* —
válida e medida **na árvore onde foi tomada**. Nesta linha a porta não existe, e
três peças escrevem o ficheiro.

Havia duas saídas fáceis e ambas erradas: trazer o código de Coleta (fora do
âmbito, e a missão dizia `COLLECTION_CHANGE = 0`), ou manter a declaração e deixar
o portão vermelho a acusar uma violação que ninguém cometeu — ninguém contornou
nada; a consolidação simplesmente ainda não chegou aqui.

A saída certa separa duas coisas que parecem uma:

```
    A DECLARAÇÃO É SOBRE A ÁRVORE. A MEDIÇÃO É SOBRE A ÁRVORE.
    TIRAR A DECLARAÇÃO NÃO PODE TIRAR A MEDIÇÃO —
    E SE TIRAR, FOI SILÊNCIO COMPRADO, NÃO VERDE GANHO.
```

A entrada saiu. `ARTEFACT_MULTIPLE_AUTHORS` continua a publicar o ficheiro e os
três autores no ecrã. As duas provas que exigem a consolidação continuam a correr
e continuam **vermelhas**. E o porquê ficou escrito **dentro do ficheiro**, com o
caminho de volta: *quando a consolidação chegar, a entrada volta palavra por
palavra.*

> **Corolário.** Ao mover uma declaração humana entre linhas, perguntar sempre:
> *a porta que ela nomeia existe aqui?* Se não existe, a declaração está a falar
> de outro sítio — e o teste que a defende também.

---

## F · UM NÚMERO DECLARADO NUM MANIFESTO É UM FACTO SOBRE UMA ÁRVORE

`MEDIDO_VARRE` publica quantos ficheiros cada passo da cadeia varre, e há um
portão que confere o declarado contra a corrida. Nove desses números vinham
medidos na árvore de origem (1499 ficheiros) e a árvore de destino tem 1376.

Nada estava «errado»: estavam **certos noutro sítio**.

```
    UM NÚMERO MEDIDO É UM FACTO SOBRE A ÁRVORE ONDE FOI MEDIDO.
    ATRAVESSAR LINHAS COM ELE É LEVAR A RESPOSTA SEM A PERGUNTA.
```

O mesmo se aplicou a um `PADRAO` de varredura incompleto: declarava três gavetas,
o código greppa sete. A falta era **invisível na árvore de origem** — nenhuma das
quatro que faltavam tinha ficheiros que o grep apanhasse — e apareceu à primeira
corrida na árvore de destino.

> **Corolário.** Uma declaração mais estreita do que o código não falha onde
> nasce. Ela espera pela árvore que a apanha. Integrar entre linhas é, por isso,
> um teste gratuito às declarações que a linha de origem nunca conseguiu exercer.

---

## G · UM SEGUNDO LEITOR DO MANIFESTO NÃO FALHA NO DIA EM QUE É ESCRITO

O portão do release lia a cadeia com o seu próprio parser:
`'\n'.join(c['REGERAR'] + c['VALIDAR'])`. Correcto enquanto cada passo era uma
string. O `G4` deu forma a cada passo, e o `join` sobre objectos não avisa que a
forma mudou — levanta `TypeError`, e **o portão morre antes de medir seja o que
for**.

Um portão que rebenta no arranque não reprova nem aprova: cala-se de uma maneira
que se parece com uma avaria de infraestrutura.

```
    DOIS SÍTIOS COM A LISTA DOS PASSOS SÃO DUAS CADEIAS —
    E A SEGUNDA NÃO FALHA NO DIA EM QUE É ESCRITA.
    FALHA NO DIA EM QUE A PRIMEIRA MUDA DE FORMA.
```

No mesmo repositório, o CI corria **7 dos 20** passos por uma lista escrita à mão:
o mapa que o CI validava não era o mapa que a build publica. A `§113` já dizia
*«um portão que se pode contornar é uma sugestão»*; isto acrescenta o caso pior —
**um portão que já não corre a coisa que diz correr, e continua verde.**

---

## H · A ORDEM DA REGENERAÇÃO NÃO É GOSTO: É UM PONTO FIXO COM DUAS PONTAS

A cadeia tem passos automáticos (`REGERAR`) e três regeneradores **a mão**
(`REGERAR_A_MAO`), fora da rodada por contrato porque o seu carimbo muda a cada
corrida e poria drift no mapa.

Correr `REGERAR_A_MAO` **depois** → `architecture.generated.json` regista o SHA
antigo dos três derivados → `P1_SEM_DRIFT` reprova.
Correr **só antes** → a matriz leu um `sources.generated.json` de antes da rodada
→ a classe de frescura cai para `EXPECTED_PREVIOUS_CYCLE` → o portão que exige
que a classe **volte a ser defeito quando se tira o contrato** reprova.

```
REGERAR  →  REGERAR_A_MAO  →  REGERAR
```

```
    UM PONTO FIXO COM DUAS PONTAS NÃO SE ALCANÇA NUMA PASSAGEM.
    E DESCOBRE-SE PELO PORTÃO QUE RECLAMA, NÃO PELA INTUIÇÃO.
```

---

## I · «JÁ ESTAVA VERMELHO» É UMA HIPÓTESE ATÉ SE ABRIR O LOG ANTIGO

`COLETA CHECK` falhou no PR. A tentação: *«está vermelho há dias»*. A medição:
descarregar o log do job do **commit que o alias servia** e comparar valor a valor.

```
COLETOR_CARIMBA_A_DATA            faltam hoje 31   chao 26   PIOROU
COLETOR_SEPARA_A_FONTE_DO_FATO    faltam hoje 25   chao 20   PIOROU
COLETOR_REGISTA_O_QUE_DESCARTOU   faltam hoje 35   chao 30   PIOROU
```

Iguais nos seis números, nos dois logs, com cinco dias de intervalo.
`PREEXISTING` — dito **depois** de olhar.

E o contrário também apareceu, e é o mais interessante: `MAP RULES CHECK` estava
vermelho antes (2 falhas) e continua vermelho depois (3 falhas), mas **não são as
mesmas**. As duas antigas ficaram corrigidas; as três novas são o medidor novo a
ver uma dívida que já cá estava.

```
    O DEFEITO É ANTIGO. O INSTRUMENTO É QUE É NOVO.
    UM PORTÃO QUE FICA MAIS VERMELHO PODE SER UM PORTÃO QUE PASSOU A VER.
```

> **Corolário.** «Vermelho antes, vermelho depois» não fecha a pergunta. A conta
> certa é pelo **nome de cada falha**, não pela cor nem pela contagem.

---

## J · O QUE ESTA SECÇÃO NÃO DIZ, E OS NÚMEROS QUE NÃO SÃO CONSTANTES

Medido na árvore desta missão, **prova histórica e não estado do sistema**:

```
MEDIDO EM release/canonical @ 3ec314ec      (não é constante do sistema)

peças                    164      papéis provados       118
papéis NÃO SEI            41      papéis em conflito     14
ligações                 588      ligações NÃO SEI       47
conceitos canónicos       15      com dono duplicado      8
ficheiros rastreados    1381      cobertos              682
portões do portal      73/73      NON MISURABILI      2 (W2 O1)
```

- Não diz que o mapa ficou correcto: diz que o mapa **desta** árvore está no
  endereço oficial, regerado pela cadeia, com a impressão da árvore a bater.
- Não diz que os portões ficaram todos verdes. `MAP RULES CHECK` e `COLETA CHECK`
  continuam vermelhos, declarados e à vista.
- Não diz `PASS` ao `G8B`. Continua `PARTIAL`, e o layout não foi tocado.
- Não diz que os 15 conflitos de papel ficaram resolvidos. Continuam publicados.
- Não diz nada sobre a Collection. **O mapa observou; não corrigiu.**
- Encontrou, e deixa por fazer: o texto de ajuda do filtro diz *«hoje são 47 de
  659»*, e nesta árvore são **47 de 588**. Um literal escrito à mão numa tela cujo
  trabalho é não deixar números por derivar. Não foi mexido porque a tela é byte a
  byte a que foi aprovada — mas é dívida, e fica nomeada.
