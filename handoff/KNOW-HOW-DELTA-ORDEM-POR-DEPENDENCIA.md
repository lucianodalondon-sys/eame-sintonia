# DELTA PARA O KNOW-HOW CANÓNICO — A ORDEM NASCE DA DEPENDÊNCIA

```
ORIGEM            C-SYSTEM-MAP-G6-DEPENDENCY-ORDER-V1
BRANCH            claude/system-map-g6-dependency-order-v1
KNOW_HOW_LIDO     claude/sintonia-eame-know-how-v1 @ 39e685fc
ÚLTIMA SECÇÃO     §108.6
NÚMERO DESTA      **por atribuir** — ver abaixo
```

> **O NÚMERO NÃO VEM ESCRITO DE PROPÓSITO.** A linha do know-how andou duas vezes
> durante esta missão (`4f681db3` → `39e685fc`), e há pelo menos um handoff
> paralelo à espera de aterrar. Herdar um número aqui seria escolher uma colisão
> e deixá-la para quem integrar. Quem aplicar isto atribui o número livre no
> momento em que aplicar.

Esta missão não tem autorização para escrever na branch do know-how. O que segue
é o delta, no formato dela, para ser aplicado pelo fluxo canónico.

---

## O QUE JÁ LÁ ESTÁ, E NÃO SE REPETE

O know-how já tem o **relógio** do ciclo atrasado (§93.1: *«a pergunta é que
árvore media a entrada quando eu a li»*) e já tem o **terceiro relógio a nomear
sem reparar** (§88.4). O que falta é o outro lado: o que se faz depois de nomear.

---

## A · UM CONSUMIDOR ANTES DO PRODUTOR NÃO FALHA

Três passos da cadeia do System Map corriam **antes** do passo que escreve o que
eles leem. A cadeia ficava verde. Os testes ficavam verdes. O validador ficava
verde.

```
    UM CONSUMIDOR ANTES DO PRODUTOR NÃO FALHA:
    ELE RESPONDE DA RODADA PASSADA.
```

Porque o ficheiro **existe**. Ele é o da geração anterior, e abrir um ficheiro
antigo não levanta excepção nenhuma — devolve uma resposta antiga, com ar de
resposta.

É por isso que este defeito não se apanha a correr o sistema. Só se apanha
comparando **o que cada passo declara ler** com **o sítio onde ele corre** — e
isso exige duas coisas anteriores: cada passo declarar as suas entradas, e haver
uma lista só.

> Consequência de método: quando um defeito não produz erro, procurar erro é a
> estratégia errada. Procura-se **discordância entre duas declarações**.

---

## B · A DEPENDÊNCIA DETERMINA A ORDEM; A ORDEM NÃO DETERMINA A DEPENDÊNCIA

Havia duas coisas que podiam discordar: a lista escrita e o que os passos diziam
ler. Discordaram durante meses.

A correcção não é arrumar a lista. É **tirar-lhe a autoridade**: a ordem passa a
sair de um ordenamento topológico sobre as dependências declaradas, com desempate
estável pela posição escrita. A posição escrita deixa de decidir e passa a
desempatar.

```
    DUAS COISAS IGUAIS HOJE NÃO SÃO A MESMA COISA:
    SÓ SE SABE QUAL DELAS MANDA QUANDO ELAS DISCORDAM.
```

E daí sai a forma de o provar: **baralhar a lista escrita** e exigir que a ordem
derivada continue a respeitar todas as arestas. Se a resposta não muda quando a
semente muda, a derivação não estava a derivar — estava a copiar com um passo
extra.

**Se houver ciclo entre as dependências, a derivação rebenta em vez de escolher.**
Escolher seria esconder o ciclo para conseguir ordenar, que é exactamente a
mentira que a lei existe para impedir.

---

## C · DUAS CLASSES DE DEPENDÊNCIA, E A REGRA DE CONVERSÃO ENTRE ELAS

Nem toda leitura é o mesmo tipo de dependência:

| classe | o consumidor pediu | ordena? |
|---|---|---|
| **nomeada** | *aquele* artefacto, pelo nome | **sim** — o produtor corre antes |
| **varredura** | «o que existir na árvore quando eu correr» | **não** — lê a rodada anterior |

A segunda não é uma dependência menor: é uma dependência com **outro contrato
temporal**. E entre as duas há uma fuga barata — tirar o nome e deixar o seletor
apanhar o ficheiro na mesma. A leitura continua explicada, a aresta deixa de
ordenar, e tudo continua verde.

```
    QUERES FRESCO? NOMEIA.
    QUEM NOMEIA NO CÓDIGO, NOMEIA NO CONTRATO.
```

A guarda que fecha isto compara o que o código **nomeia** (literais na árvore
sintáctica) com o que o contrato declara. Nomear no código e declarar varredura é
mentira detectável.

---

## D · UM CICLO ESTRUTURAL PROVA-SE COM UM LAÇO SOBRE SI PRÓPRIO

Ficou um ciclo, e ele não se ordena. Dizer «é estrutural» seria opinião. A prova
cabe numa linha:

> o seletor do censo do congelamento apanha o ficheiro que **o próprio censo do
> congelamento escreve**.

Nenhuma permutação põe um passo antes de si mesmo. Deixa de ser argumento e passa
a ser aritmética.

```
    UM MEDIDOR QUE ESCREVE DENTRO DO QUE MEDE
    NÃO SE ORDENA: CONVERGE.
```

Generalizando: sempre que um sistema mede uma superfície onde ele próprio escreve,
o ciclo é da forma do problema e não da ordem dos passos. O que se exige nesse
caso não é ordem — é **convergência provada**.

---

## E · «O ATRASO EXISTE» E «O ATRASO CUSTA» SÃO DUAS AFIRMAÇÕES

Medido: mexe-se numa fonte, correm-se três passagens, comparam-se os conteúdos
sem o relógio. A 1ª e a 2ª dão o **mesmo** conteúdo.

O atraso **existe** — está provado pelo laço. E **não custa** — porque os
varredores dependem do *conjunto* (que ficheiros existem, de que espécie) e não
do conteúdo que os passos seguintes reescrevem.

```
    MEDIR A PRIMEIRA E PUBLICAR A SEGUNDA É O ERRO DE SEMPRE.
```

E a prova de igualdade precisa de **controlo positivo**: antes de comparar, exigir
que o retrato *veja* a mudança que a fonte mexida provocou. Sem isso, um retrato
partido — que devolvesse sempre o mesmo — passava as comparações todas sem medir
nada.

Corolário separado, e que não se esconde um atrás do outro:

```
SEMANTIC_DETERMINISM = sim     BYTE_DETERMINISM = não (relógio nos artefactos)
```

---

## F · STALE POR CONTRATO NÃO É STALE POR ACIDENTE — MAS SÓ QUANDO O CONTRATO EXISTE

Três regeneradores não são corridos por automação nenhuma. Os artefactos deles
ficam para trás sempre que a árvore anda. Chamar defeito a isso seria acusar o
sistema de cumprir o próprio contrato; chamar-lhe normal sem contrato escrito
seria varrer dívida para debaixo de uma palavra.

A regra que sobrevive às duas tentações: **o atraso é esperado quando a
declaração o explica, e defeito quando não explica.** Basta **um** pedaço de
prova por explicar para a resposta inteira ser defeito — somar explicações
parciais é tratar meia prova como prova.

E prova-se pelos dois lados: tira-se a classe declarada e o mesmo artefacto tem de
voltar a ser defeito no minuto seguinte.

```
    UMA CLASSE QUE NÃO MUDA QUANDO A DECLARAÇÃO MUDA
    NÃO ESTÁ A CLASSIFICAR: ESTÁ A ETIQUETAR.
```

---

## G · UM RAMO QUE NENHUM TESTE ALCANÇA NÃO É REDE DE SEGURANÇA

O classificador tinha um ramo para «o produtor corre depois». A derivação da
ordem impede esse caso, portanto nenhum teste conseguia lá chegar — e uma mutação
que o partisse sobrevivia a tudo.

```
    SE A LEI JÁ IMPEDE O CASO, O RAMO QUE O TRATA
    NÃO PROTEGE NADA: SÓ ADIA A DESCOBERTA.
```

Saiu, com a razão escrita no lugar dele. O sobrevivente de mutação **é** o
detector de código morto: um mutante que ninguém mata está a apontar para uma
linha que ninguém consegue exercitar.

Corolário operacional: quando uma guarda só corre em presença do defeito, ela
nunca corre num repositório saudável. Constrói-se o caso à mão.

---

## H · CONFERIR NÃO É REIMPLEMENTAR

Havia dois runtimes a ler a mesma lista (Python e JavaScript). Derivar a ordem nos
dois seria repetir o algoritmo — e dois algoritmos que se afastem são duas ordens
outra vez. Derivar só num e deixar o outro acreditar no ficheiro seria confiar num
ficheiro que pode mentir.

A saída é assimétrica de propósito: **um deriva, o outro confere**. A conferência
cabe em cinco linhas, não tem opinião e recusa-se a agir quando o ficheiro
contradiz as dependências.

```
    UM VERIFICADOR QUE FALHA DIZ «ESTE FICHEIRO ESTÁ ERRADO».
    UM SEGUNDO ALGORITMO DIZ «EU TENHO OUTRA OPINIÃO».
```

---

## I · O ARNÉS QUE SÓ REPÕE NO `finally` DEIXA O ESTRAGO NOS DIAS MAUS

Regra antiga, defeito novo: ler os originais antes de mutar e repor no `finally`
**não chega**. Se o processo for morto a meio — *timeout*, CI a cortar o job — o
`finally` não corre e a mutação fica no disco de trabalho.

Aconteceu: uma linha de entradas ficou apagada e foi para o `git add`. Só a prova
de IO a apanhou, três corridas depois.

```
    UM ARNÊS QUE SÓ REPÕE QUANDO ACABA BEM
    DEIXA O ESTRAGO EXACTAMENTE NOS DIAS MAUS.
```

O que fecha: o original lê-se no arranque do módulo e há uma guarda **no fim** que
compara o ficheiro com ele. A prova acusa-se a si própria.

---

## J · A CATEGORIA QUE NINGUÉM CORRE É A QUE PODE ESTAR PARTIDA HÁ MESES

O corredor da cadeia anunciava cinco categorias e a tabela dele tinha quatro. A
quinta morria com `KeyError`. Era, precisamente, a categoria dos passos que
nenhuma automação corre.

```
    A CATEGORIA QUE NINGUÉM CORRE
    É A QUE PODE ESTAR PARTIDA HÁ MESES.
```

A guarda que ficou não testa as quatro que se usam: percorre **o vocabulário
declarado** e exige que cada categoria anunciada tenha corredor.

---

## O QUE ISTO NÃO AUTORIZA

- Não autoriza chamar `CURRENT` a um artefacto atrasado.
- Não autoriza declarar varredura uma dependência pedida pelo nome.
- Não autoriza automatizar um regenerador para fechar uma contagem: medido quatro
  vezes, isso troca um número por uma cadeia que nunca mais assenta.
- Não autoriza usar «ciclo atrasado» como nome para *stale* que ninguém explicou.
