# HANDOFF · DELTA DE KNOW-HOW §108

**Para aplicar em `claude/sintonia-eame-know-how-v1` →
`SINTONIA-EAME-KNOW-HOW.md`, a seguir ao `§107`.**

Este ficheiro vive aqui, e não lá, pela mesma razão do `§107`: esta missão está
presa ao seu ramo (`claude/funny-hypatia-y7ho5s`) e não tem autorização para
escrever na linha do know-how. Quem integrar leva o bloco abaixo tal como está.

**E há uma segunda razão, que é o próprio assunto deste delta.** Escrever aqui um
`SINTONIA-EAME-KNOW-HOW.md` novo criaria a **terceira** versão do know-how — a
par do dono em `claude/sintonia-eame-know-how-v1` e da cópia 50 commits atrasada
em `claude/sintonia-eame-know-how-v1-copy`. Isso é o ataque `RT04`, e o portão
que esta missão construiu reprova-o. Um delta que violasse a lei que ele próprio
descreve não valeria a pena escrever.

```
ORIGEM      C-GOV-01 · CONTROL PLANE E SALA DE CONTROLE
MEDIDO_EM   2026-09-13
BASE        main @ f437ff11 · trabalho em claude/funny-hypatia-y7ho5s
NAO_DUPLICA §107 — ali fica o que se aprendeu sobre testes e contratos;
            aqui fica o que se aprendeu sobre ONDE A AUTORIDADE VIVE
```

---

# §108 · UMA LEI QUE EXISTE NO GIT E NÃO EXISTE NO TEU COMMIT NÃO GOVERNA NADA

## O QUÊ

O SINTONIA passa a distinguir formalmente três planos:

```
CONTROL PLANE      quem manda        governa · referencia · valida · observa
OPERATIONAL PLANE  a máquina         COLETA → ESPERA → INTELIGÊNCIA → ENTREGA
EVIDENCE PLANE     o que comprova    git · código · banco · runtime · testes
```

O Control Plane **não é uma quarta etapa do dado**. Não existe
`DADO → CONTROL PLANE`: nenhum dado o atravessa.

## 108.1 · POR QUÊ

Porque a pergunta *«que lei governa esta peça?»* não tinha resposta, e a razão
não era falta de leis — era que **as leis estavam em ramos diferentes do código
que elas governam**. Medido, e não suposto:

| autoridade | está em `main`? | vive em |
|---|---|---|
| `BIBLIA-CANONICA-DA-COLETA.md` | **não** | `claude/raw-observation-identity-3jbwco` |
| `SINTONIA-EAME-KNOW-HOW.md` | **não** | `claude/sintonia-eame-know-how-v1` |
| `docs/biblia/BIBLIA-DA-ENTREGA-EAME.md` | **não** | `research/delivery-bible-v1` |
| `docs/biblia/BIBLIA-DA-INTELIGENCIA-EAME.md` | **não** | `claude/integration-acervo-portal-v1` |

E `CLAUDE.md`, que **está** em `main`, manda ler a primeira delas.

```
UM AGENTE QUE CLONA O RAMO PADRAO E OBEDECE A CLAUDE.md
E MANDADO CONSULTAR FICHEIROS QUE ALI NAO EXISTEM.
```

Ele não desobedece: **não consegue** obedecer. E o modo de falhar é o pior que
há, porque é silencioso — não há erro, não há aviso, há um ficheiro que não está
lá e um agente que continua a trabalhar sem a lei que devia segui-lo.

Nada disto é perda de dados: o Git tem tudo. É perda de **alcance**. A lei existe
e não chega a quem trabalha.

## 108.2 · O `AGENTS.md` DE `main` NÃO É O `AGENTS.md` DA CASA

O caso mais duro não é uma bíblia ausente — é a lei presente e **velha**. O
`AGENTS.md` da linha funcional tem **262 linhas a mais** do que o de `main`:
carrega a lei da frescura do mapa, a impressão da árvore, um passo `2b` no portão
e três ficheiros que em `main` não existem.

```
O FICHEIRO ESTA LA, ABRE, LE-SE, E ESTA ERRADO.
```

Uma autoridade ausente pelo menos falha alto quando alguém a procura. Uma
autoridade **desatualizada** responde — com a resposta de outro mês.

## 108.3 · A DIFERENÇA ENTRE `DECLARED` E `OBSERVED` VALE PARA O GOVERNO, E NÃO SÓ PARA O DADO

`DECLARED EDGE ≠ OBSERVED EDGE` já era lei para as setas técnicas. Aplicá-la às
relações de governo não exigiu lei nova — exigiu **medir a coisa certa**:

```
QUEM PROVA QUE UMA LEI GOVERNA UMA PECA
E O TEXTO DA LEI A NOMEAR A PECA.

Nao o ficheiro existir.
Nao o mundo mencionar a peca.
Nao estar desenhado no mapa.
```

Das 52 relações declaradas no registo, **35** têm essa prova (ficheiro e linha
dentro da própria autoridade) e **17** não têm. As 17 ficam `expected`, e
`P7_NAO_SEI_VIVE` — que já existia — obriga-as a ficar em NÃO SEI.

## 108.4 · O MEDIDOR COMETEU O ATAQUE QUE FOI ESCRITO PARA APANHAR

O primeiro censo desta missão tinha esta linha:

```python
dentro = caminho if caminho in textos else None   # ← e se a lei nao esta ca?
```

Quando a autoridade **não estava na árvore**, `dentro` ficava `None` e a busca da
prova caía para a árvore inteira. Resultado medido, no primeiro arranque:

```
A-BIBLIA-COLETA  GOVERNS  admissao/admissao.py
  EDGE_STATE = OBSERVED
  PROOF      = system-map/data/architecture.declared.json:...
```

Uma lei que **não existe neste commit**, a governar uma peça real, com prova
tirada de **outro ficheiro qualquer**. É o `RT01` inteiro — *desenhar uma seta
GOVERNS sem referência real* — cometido pelo próprio medidor, na primeira hora.

```
O ATAQUE NAO E HIPOTETICO. ELE E O CAMINHO MAIS CURTO,
E POR ISSO E O QUE SE ANDA SEM QUERER.
```

Uma busca que «alarga o âmbito quando não encontra» parece robustez e é o
contrário: é o medidor a procurar até achar alguma coisa que sirva.

## 108.5 · UM HASH DE SI PRÓPRIO NUNCA CHEGA A PONTO FIXO

A `SALA-DE-CONTROLE-SINTONIA.md` é gerada, e o cartão dela mostrava a impressão
do conteúdo dela — **dentro dela**. Cada corrida media o texto anterior,
gravava-o, e com isso produzia um texto novo para a corrida seguinte medir.

```
A CADEIA NUNCA FECHA. O MAPA ACUSA DRIFT PARA SEMPRE.
```

É primo do `O COMMIT NÃO PODE CONHECER O SEU PRÓPRIO SHA` que a casa já
aprendeu, e apareceu por escrito noutro sítio: usar `git rev-parse HEAD:<path>`
dá o SHA da versão **já commitada**, e esse valor muda sozinho no instante do
commit. `git hash-object` mede o conteúdo que está ali, e dá o mesmo antes e
depois — **a única propriedade que serve a uma prova que atravessa um commit.**

Para o ficheiro que se está a escrever, nem isso serve: ali diz-se, não se mede.

## 108.6 · «NÃO PIOROU» É EXECUTÁVEL; «ESTÁ TUDO CERTO» NÃO É

O portão do Control Plane tinha de acusar seis dívidas que a casa **tem hoje**:
autoridades fora desta árvore, cópias divergentes, documentos que se dizem lei e
não estão no registo. Exigir zero na primeira corrida reprovaria o repositório
inteiro, e a primeira coisa que alguém faria era desligar o portão.

Então o portão separa duas famílias, e a separação é a peça de engenharia:

| | exige | exemplo |
|---|---|---|
| **INTEGRIDADE** | zero, sempre | dois donos para um conceito; um handoff a governar |
| **DÍVIDA** | não piorar | 2 autoridades fora desta árvore; 3 com cópias divergentes |

É o mesmo padrão do `medidas/padrao_da_coleta.py`, e a lição repete-se: **um
portão desligado mede menos que nenhum**, porque dá a sensação de que existe.

## 108.7 · UMA FAIXA DE GOVERNO À DIREITA DA ENTREGA DIZ QUE GOVERNAR VEM DEPOIS DE ENTREGAR

No mapa, uma quinta família colocada na fila cairia à direita da ENTREGA, e o
olho leria `ENTREGA → CONTROL PLANE`. Por isso o plano de governo é uma faixa
**por cima**, e quatro coisas mudam ao mesmo tempo na seta dele — cor fora da
rampa das etapas, traço ponto-e-traço, espessura menor, e **ponta em losango**:

```
UMA PONTA DE SETA DIZ «ENTRA AQUI». GOVERNO NAO ENTRA EM LADO NENHUM.
```

Enquanto a seta de governo acabava na mesma ponta do fluxo, uma linha a descer
sobre `admissao/` continuava a poder ler-se como caminho de dado.

E a faixa **atravessa a largura toda**, e não só a das zonas que contém: as nove
zonas de governo somam 7.370px e a máquina vai a 16.050px. Uma faixa que acabasse
a meio ficaria pousada exatamente por cima da COLETA e de mais nada — a dizer que
o governo é da coleta, que é falso.

## 108.8 · CONSEQUÊNCIA

Autoridades canónicas passam a ter **registo único, dono único, ciclo de vida
explícito e representação no System Map** — e o estado medido de cada uma diz, em
voz alta, se ela chega ou não a quem trabalha nesta árvore.

O que ficou **por fazer**, e é a dívida que este delta entrega à próxima missão:

```
CONTROL_PLANE_ATOMICITY = FAIL
```

Não existe hoje um único commit onde estejam, coerentes ao mesmo tempo:

```
CODE + BIBLES + CONTRACTS + KNOW_HOW + AUTHORITY_REGISTRY + TESTS + PROOFS
```

O registo torna isso **visível e contável**. Não o conserta. Convergir as linhas
é trabalho de integração, precisa de estratégia provada, e não se faz por
`git checkout` de ficheiro entre ramos — que é como se apagam 54 linhas de prova
sem ninguém dar por isso (`§` da lei de trazer ficheiro de outra branch).
