# DELTA PARA O KNOW-HOW CANÓNICO — O PAPEL VEM DA EVIDÊNCIA, E A TELA NÃO PROMOVE NADA

```
ORIGEM            C-SYSTEM-MAP-G7-G8-G8B-VISUAL-CLARITY-V1
BRANCH            claude/system-map-g7-g8-visual-clarity-v1
BASE              claude/system-map-g6-dependency-order-v1 @ 4224a234
KNOW_HOW_MEDIDO   claude/sintonia-eame-know-how-v1 @ 338e171a
ÚLTIMA SECÇÃO     §110.9   (medida agora, não herdada)
NÚMERO DESTA      **por atribuir** — ver abaixo
```

> **O NÚMERO CONTINUA A NÃO VIR ESCRITO, E AGORA HÁ PROVA DE QUE ISSO ESTAVA
> CERTO.** O delta do `G6` mediu a linha em `39e685fc` e registou `§108.6` como
> última secção. Medido hoje em `338e171a`: a última é **`§110.9`**. A linha
> andou **duas secções e meia** entre uma missão e a seguinte.
>
> Herdar um número aqui seria escolher uma colisão e deixá-la para quem integrar.

## ⚠️ O DELTA DO `G6` AINDA NÃO ATERROU

Medido em `338e171a`: nenhuma das frases-chave do delta anterior existe no
ficheiro do know-how (`UM CONSUMIDOR ANTES DO PRODUTOR`, `A ORDEM NASCE DA
DEPENDÊNCIA` — zero ocorrências). `handoff/KNOW-HOW-DELTA-ORDEM-POR-DEPENDENCIA.md`
**continua por aplicar**, e este ficheiro **não o substitui nem o reescreve**.

São dois deltas paralelos à espera do mesmo fluxo. Quem integrar aplica os dois,
por ordem de missão, e atribui dois números livres.

Esta missão não tem autorização para escrever na branch do know-how. O que segue
é o delta, no formato dela.

---

## O QUE JÁ LÁ ESTÁ, E NÃO SE REPETE

O know-how já tem os quatro planos, a proibição de promoção entre eles, e
`ANÁLISE ESTÁTICA PROVA CAN DO · SÓ TELEMETRIA PROVA DID DO`. O que falta é o
lado da **tela**: o que acontece a uma lei correcta que nunca chega ao pixel.

---

## A · UMA LEI QUE NÃO ESTÁ LIGADA A UM CAMPO DA TELA SÓ EXISTE PARA QUEM LÊ O CONTRATO

A §20 do contrato de confiança está escrita desde `G1` e diz, em maiúsculas,
*«uma seta verde não pode continuar a significar quatro coisas»*. O backend
cumpria-a: cada aresta publicava `DECLARED · CODE · OBSERVED · PROVEN` desde
então.

Medido nesta árvore, no mesmo dia:

```
612 arestas PROVEN=YES
 47 arestas PROVEN=UNKNOWN
659 arestas desenhadas com o mesmo traço
657 arestas com a dica a dizer «LIGAÇÃO PROVADA»
```

A causa cabe numa linha de JavaScript:

```js
const cls = e.kind === 'expected' ? 'unknown' : '';
```

`kind` separa `expected` (2) de `technical` (657). **Não é a pergunta da prova**,
e nunca foi. A tela perguntava a um campo que não sabe a resposta, e recebia uma
resposta na mesma.

```
    UM CAMPO QUE SEPARA DUAS COISAS
    NÃO RESPONDE POR UMA TERCEIRA.
```

O nome do defeito é este, e é o que fica:

```
    UMA LEI ESCRITA NUM CONTRATO E NÃO LIGADA A UM CAMPO DA TELA
    É UMA LEI QUE SÓ EXISTE PARA QUEM LÊ O CONTRATO.
```

**Consequência de método.** Ao fechar uma reforma de modelo (planos, espécies,
universos), a lista de sítios a actualizar não acaba no gerador: ela acaba no
**último consumidor**. E o consumidor mais perigoso é a interface, porque é o
único que não reprova nada quando fica para trás — ele continua a desenhar.

> Corolário: *«o card precisa de PODER mostrar X»* nunca é o mesmo que *«o card
> mostra X»*. Uma secção de contrato escrita com «poder» não fecha nada.

---

## B · O MESMO DEFEITO PROPAGA-SE PARA AS TRAVESSIAS, E AÍ FABRICA CAMINHO

A função que desenha o «caminho completo» tinha, no seu próprio comentário, a
regra certa: *«sobe e desce a partir da peça, mas NUNCA atravessa uma ligação NÃO
SEI. Atravessar seria transformar "talvez" em "portanto"»*.

E atravessava 45.

```js
if (e.kind === 'expected') return;   // apanha 2 de 47
```

Um filtro que exclui 2 quando devia excluir 47 **não é um filtro parcial**: é um
filtro que dá autorização a 45. E cada travessia dessas costura um buraco que a
pessoa devia estar a ver.

```
    UM CAMINHO QUE ATRAVESSA O QUE NÃO ESTÁ PROVADO
    NÃO MOSTRA UM CAMINHO MAIS LONGO: MOSTRA UM CAMINHO FALSO.
```

**Consequência de método.** Quando a mesma pergunta aparece em dois sítios do
código (desenhar a seta · atravessar a seta), ela tem de sair da **mesma
função**. Duas cópias da mesma pergunta divergem, e a que diverge em silêncio é
sempre a que ninguém está a olhar.

---

## C · PAPEL É MEDIÇÃO, E A GAVETA NÃO É UM MEDIDOR

`ROLE` não existia. Atribuí-lo parecia trabalho de arrumação e é trabalho de
medição — e a tentação, em cada peça, é lê-lo no sítio errado:

```
NOME DO FICHEIRO   →   não é papel
GAVETA             →   não é papel  (regras/sensor_coleta.py é um COLETOR)
FICHA (`kind`)     →   é uma AFIRMAÇÃO, e afirmação não é medição
```

O que é medição: *é um manifesto de workflow? está dentro da raiz servida pelo
deploy? corre outra peça por subprocesso? abre ligação de rede? escreve numa
pasta medida? quem lê o que ele escreve?*

E a regra que impede o resto de entrar:

```
    UM PAPEL SEM A REGRA QUE O DECIDIU AO LADO É UM RÓTULO.
```

Cada peça publica `ROLE`, `ROLE_RULE` (qual das nove regras disparou),
`ROLE_PLANE` (`CODE` quando a árvore mediu, `DECLARED` quando só a ficha afirma)
e `ROLE_LIMITATIONS` (o que aquilo **não** prova). Nenhum dos quatro é opcional.

---

## D · DUAS FONTES QUE DISCORDAM NÃO SE FUNDEM: PUBLICAM-SE

Quando a medição diz uma coisa e a ficha diz outra, há três saídas e duas são
armadilhas:

| saída | o que acontece |
|---|---|
| a medição ganha | o mapa arbitra uma decisão humana, calado |
| a ficha ganha | o mapa herda o engano de quem escreveu a ficha |
| **nenhuma ganha** | o papel fica `UNKNOWN` e o conflito sai com os dois lados |

Medido: **15 das 162 peças**. Sete são o mesmo caso (cartões declarados `tela`
que possuem só `*.spec.json`), cinco são provas que a árvore mede a produzir para
outros, três são o contrário.

```
    NÃO SEI HONESTO É MELHOR DO QUE UM PAPEL ARBITRADO —
    E O CONFLITO PUBLICADO É MELHOR DO QUE OS DOIS.
```

**Consequência de método.** Um conflito publicado é a única forma de um
desacordo produzir trabalho. Escondido, ele produz confiança falsa; arbitrado,
produz uma decisão sem dono.

---

## E · MEDIDO E INVISÍVEL VALE O MESMO QUE NÃO MEDIDO

`censo_dos_donos.py` media, desde a missão da observabilidade, 15 conceitos
canónicos e o estado de cada um. **Nove com dono duplicado.** O número existia,
estava num artefacto versionado, era regenerado em cada corrida — e **nunca
tinha aparecido em ecrã nenhum**.

```
    UM NÚMERO QUE NINGUÉM VÊ NÃO ESTÁ A DENUNCIAR NADA.
    ESTÁ A ESPERAR QUE ALGUÉM O PROCURE.
```

A correcção não foi medir outra vez: foi **ler** de quem já media. Recontar teria
criado uma segunda contagem do mesmo universo — e a §5.2 do contrato de confiança
existe por causa de um caso em que isso já aconteceu três vezes com o mesmo nome.

> Corolário: ao fechar uma auditoria, a pergunta final não é *«medi?»*. É *«onde
> é que este número aparece para quem não corre o script?»*.

---

## F · TRÊS CANAIS, PORQUE COR É UM CANAL SÓ

Um estado comunicado só por cor não é comunicado a quem imprime a preto e branco,
a quem tem daltonismo, ou a quem está a olhar para 659 setas ao mesmo tempo. A
ligação sem prova passou a ter:

```
COR      cinzento em vez de tinta
TRAÇO    tracejado curto
MARCA    anel vazado no meio da curva + ponta de seta vazada
PALAVRA  selo com texto no painel: PROVADA · DECLARADA · NÃO SEI
```

E a lição fina: **o traço já estava ocupado**. A categoria da ligação (`DATA`,
`CONTROL`, `READ`, …) usa o `stroke-dasharray` desde antes. Empilhar a prova no
mesmo canal teria destruído a leitura que já existia.

```
    DOIS EIXOS ORTOGONAIS PRECISAM DE DOIS CANAIS VISUAIS.
    REUTILIZAR O CANAL DO PRIMEIRO APAGA-O PARA PAGAR O SEGUNDO.
```

---

## G · UM FILTRO QUE ARRANCA COM `NÃO SEI` DESLIGADO MENTE POR OMISSÃO

A maioria de quem abre um painel nunca mexe num filtro. O estado por omissão **é**
o painel, para essa pessoa.

```
    O DEFAULT DE UM FILTRO NÃO É UMA CONVENIÊNCIA:
    É A AFIRMAÇÃO QUE O PAINEL FAZ A QUEM NÃO MEXE EM NADA.
```

As quatro classes de prova arrancam ligadas, e há uma guarda que lê o HTML e
reprova se alguma perder o `checked`.

---

## H · ENQUADRAR TUDO NÃO É MOSTRAR TUDO

O mapa abria com um `fit()` sobre o mundo inteiro. Medido a 1600×1000: escala
**0,06** — cada cartão com 17 píxeis de largura. Tecnicamente, tudo estava no
ecrã. Na prática, o que estava no ecrã eram colunas coloridas.

```
    UM PAINEL QUE ABRE ILEGÍVEL OBRIGA TODA A GENTE
    A FAZER ZOOM ANTES DA PRIMEIRA PERGUNTA.
```

A correcção é de câmara, não de conteúdo: nenhum cartão saiu do DOM, nenhum
filtro mudou, o botão de enquadrar continua a mostrar o mundo inteiro. Mudou onde
a câmara pousa.

> Corolário separado, e que merece o seu próprio nome: **arrumação de leitura é
> diferente de arrumação de posição.** A primeira é barata e não altera
> semântica. A segunda é cara e altera — e continua por fazer, de propósito.

---

## I · «CAN DO» MEDIDO CORRECTAMENTE CONTINUA A NÃO SER «DID DO»

O red team desta missão encontrou isto:

```
system-map/tests/test_impressao_da_arvore.py:141
  alvo.write_text(alvo.read_text(...) + "\n<!-- mutacao -->\n", ...)
```

O scanner mede a linha como `WRITES` para `AGENTS.md`. E **não está errado**: a
linha prova que o código consegue escrever ali. O que ela não prova é que escreve
na árvore rastreada — o teste opera sobre um clone.

A tentação é «corrigir o scanner». A resposta certa foi outra: a evidência já
declarava o seu limite (`STATIC_CODE_ANALYSIS · prova CODE`), e a limitação
estava escrita antes de alguém dar por ela.

```
    UMA MEDIÇÃO QUE DECLARA O SEU LIMITE NÃO PRECISA DE SER CORRIGIDA
    QUANDO ALGUÉM A LÊ FORA DELE — PRECISA DE SER LIDA COM O LIMITE.
```

---

## J · UM ATAQUE QUE SOBREVIVE VALE MAIS DO QUE VINTE E TRÊS QUE MORREM

O red team correu 24 ataques. Vinte e três morreram à primeira. O #3 — *«import
tratado como fluxo de dado»* — sobreviveu, e obrigou a uma correcção real.

A regra que promove a ligação de uma ferramenta de `PREPARO` a `DATA` aceitava
`categoria in (CODE, READ)`. Medido: as **únicas duas** ligações que ela promovia
nesta árvore eram as duas de `import`.

```
    UMA REGRA JUSTIFICA-SE COM O CASO QUE A INSPIROU
    E APLICA-SE AO CASO QUE ELA APANHA. OS DOIS PODEM SER DIFERENTES.
```

Ela passa a recusar `CODE`. Hoje promove **zero** ligações, e zero é a resposta
certa: nenhuma leitura dessas está medida.

> Corolário operacional: ao escrever uma regra com uma condição larga
> (`x in (A, B)`), medir **quais** dos membros disparam de facto. Se um membro
> nunca dispara e o outro dispara sempre, a regra não é a que foi escrita.

---

## O QUE ESTE DELTA **NÃO** DIZ

- Não diz que o mapa passou a ser compreensível por toda a gente. Diz que
  **39 de 162** peças continuam sem papel medido, e que a cobertura humana medida
  é **78%**.
- Não diz que o layout ficou arrumado. Não se mexeu no layout.
- Não diz nada sobre a Collection. O mapa observou; não corrigiu.
