# PARA O KNOW-HOW — §91, SCRAP-CV-01

> **Destino:** `SINTONIA-EAME-KNOW-HOW.md`, na branch
> `claude/sintonia-eame-know-how-v1` (@ `318df268`).
>
> **Porquê aqui e não lá.** O know-how vive noutra branch, e esta missão só tem
> autorização para escrever na sua. O texto fica escrito, datado e apontável; quem
> tiver a branch do know-how na mão anexa-o como §91. Um conhecimento que espera
> por uma branch é melhor do que um conhecimento que espera por memória.
>
> **Medido antes de escrever:** nenhuma das doze frases desta secção existe no
> `SINTONIA-EAME-KNOW-HOW.md` @ `318df268`. Contagem por `grep -c -F`, todas a
> zero. Não se acrescenta o que já lá está.

---

# §91 · DUAS LEIS QUE FALAM DO MESMO DÓLAR PRECISAM DE UMA RELAÇÃO, NÃO DE UM MERGE

## 91.1 · A SITUAÇÃO

Duas branches, duas missões, duas leis, cada uma verde sozinha:

```
SR-02      QUEM · POR QUÊ · PARA QUÊ pode gastar     leis/autorizacao_de_gasto.py
C10.8A-F   ATÉ QUANTO esta execução pode gastar      coleta/coletor.py :: OrcamentoFinanceiro
```

As duas passavam. Juntas, deixavam passar o dobro do dinheiro.

```
autorização: max_execucoes = 2 · max_usd = 1.00
duas chamadas com teto_usd = 1.00 cada
EXPOSIÇÃO REPRESENTADA = 2.00
```

    CADA POST GANHAVA O LIMITE INTEIRO OUTRA VEZ.

## 91.2 · A LIÇÃO, E ELA É GERAL

Quando duas leis falam do **mesmo recurso**, a convergência não é dar à primeira
o que a segunda sabe. É escrever a **relação** entre as duas e deixar cada uma
com o seu trabalho.

```
FINANCIAL_BUDGET.AUTHORIZED  <=  AUTORIZACAO.max_usd
```

A guarda recebe um NÚMERO e compara. Nunca soma. Dar-lhe um ledger próprio teria
criado duas peças a contar o mesmo dinheiro, e duas peças que contam o mesmo
divergem na terceira chamada.

    LIMITE HUMANO != LEDGER OPERACIONAL.
    SPEND_AUTHORIZATION != FINANCIAL_BUDGET.

## 91.3 · UM GATE BARATO CORRE PRIMEIRO, E NÃO QUEIMA NADA AO RECUSAR

A conferência de autorização é de graça. A reserva de dinheiro custa saldo. O
POST custa dinheiro. Então a ordem é essa, e o **consumo da unidade autorizada**
acontece no momento do COMPROMISSO — depois do dinheiro reservado, imediatamente
antes do POST.

Na SR-02 a unidade era gasta na conferência, que corre antes do dinheiro: uma
corrida barrada por falta de saldo queimava uma execução autorizada para uma
compra que nunca aconteceu.

    POST QUE NÃO SAIU != POST QUE SAIU.

E vale nos dois sentidos. Quando o teto de acessos recusa — o que acontece
*dentro* do transporte, **depois** do consumo — há prova de que nada foi
comprado, e a unidade volta. Quando o transporte cai **no meio do POST**, não há
prova nenhuma, e ela não volta.

    AUSÊNCIA DE NOTÍCIA NÃO É PROVA DE AUSÊNCIA DE COMPRA.

## 91.4 · UM SELO NÃO CHEGA. O QUE VALE É A IDENTIDADE

`dataclasses.replace(autorizacao, max_execucoes=99)` copia todos os campos de
init — o selo incluído — e devolve um objeto que passa em qualquer validação de
forma. `copy.deepcopy` faz o mesmo, e repõe a contagem a zero de brinde.

    DUAS AUTORIZAÇÕES IGUAIS NÃO SÃO A MESMA AUTORIZAÇÃO.
    COPIAR UMA AUTORIZAÇÃO NÃO É RECEBER UMA AUTORIZAÇÃO.

O que vale é a instância que saiu da porta de concessão, guardada por identidade
(`WeakSet`, `eq=False`). Um direito de gastar não é um valor: é um acontecimento.

## 91.5 · UMA RECUSA QUE PEDE PARA SER REPETIDA NÃO É UMA RECUSA

`GastoRecusado` herdava de `PermissionError`, que herda de `OSError`. Esta casa
tem `except OSError` em toda a parte a apanhar túnel caído. Medido: uma compra
recusada por falta de autorização subia como `TRANSIENT_NETWORK_ERROR`, cuja
recuperação canônica é `WAIT` — isto é, **tenta outra vez**. E a tentativa
seguinte é uma compra.

**A árvore de exceções é política, não decoração.** Escolher a classe-base de uma
exceção é escolher quem a vai apanhar, e onde.

E a recusa nova precisou de nome próprio, não de um dos que já havia:

    SALDO ESGOTADO != NINGUÉM AUTORIZOU.

Um sistema que respondesse `FINANCIAL_BUDGET_EXHAUSTED` a uma compra sem
autorização mandaria procurar saldo que já existe, e apagaria a única pergunta
que importa.

## 91.6 · UM IMPORT QUE REESCREVE A PORTA PAGA É UMA DECISÃO QUE NINGUÉM TOMOU

`regras/sensor_coleta.py` faz `coletor._curl = _curl_robusto` **no corpo do
módulo**. Quem importar aquele ficheiro por qualquer razão troca o transporte da
única porta paga da casa, para o processo inteiro.

Duas consequências, e as duas foram medidas, não imaginadas:

1. **Três harnesses que prometem `NETWORK_REAL = 0` deixavam de prometer nada.**
   O fake substituía `subprocess.run`; com o transporte trocado para `urllib`, o
   fake deixava de estar no caminho e o pedido ia mesmo à rede.

        UM FAKE QUE JÁ NÃO ESTÁ NO CAMINHO NÃO É UM FAKE. É UM ADORNO.

2. **A substituição herdou a porta e perdeu as políticas dela.** A porta original
   pedia autorização ao dono da rede antes de cada ida e enviava o POST uma única
   vez, por uma razão escrita em 2026-09-02. A substituição não pedia nada e
   repetia até 4 vezes — para qualquer método.

        REPETIR UM GET É BARATO. REPETIR UM POST É COMPRAR DE NOVO.
        TROCAR O TRANSPORTE NÃO PODE TROCAR QUEM CONTA AS IDAS.

**A generalização:** quando alguém substitui uma peça central «só para mudar o
transporte», o que muda com ela é tudo o que a peça original fazia **antes** de
falar com o mundo. Uma substituição herda a assinatura; não herda as guardas.

## 91.7 · O QUE ESTA MISSÃO REPETIU PELA QUARTA VEZ

Uma sentinela textual mordeu a própria explicação — outra vez.

- A SR-01 procurou `keyword` num ficheiro e achou a defesa da própria lei.
- A SR-02 procurou `def registar` e achou o seu próprio código.
- A SR-02 procurou o endpoint de criação e achou os docstrings dos owners.
- A CV-01 procurou `OrcamentoFinanceiro` na lei da autorização — e achou o
  parágrafo que explica **por que o ledger não é dela**.

E uma quinta, ao contrário: um comentário novo em `scrap_executor.py` continha a
palavra `relevancia` — a explicar que aquele ficheiro **não** julga relevância —
e reprovou a sentinela que proíbe julgamento temático no executor.

    MEDIR O TEXTO DE UMA LEI NÃO É MEDIR O COMPORTAMENTO DELA.
    E UMA DEFESA ESCRITA EM PALAVRAS É INDISTINGUÍVEL DO ATAQUE, PARA UM `grep`.

**A regra prática:** medir o que o módulo **expõe** e o que ele **faz** —
`hasattr`, `inspect.signature`, os módulos realmente importados, a chamada real
com o fake na fronteira. O texto só serve para explicar a medição a quem lê
depois.

## 91.8 · COMO SE MEDE UMA CONVERGÊNCIA SEM HERDAR NÚMEROS

A regressão foi medida numa **worktree isolada** no HEAD da branch de integração,
sem o port, e depois na árvore com o port. Nunca se herdou a contagem de nenhuma
das duas linhagens de origem.

E a comparação foi de **conjuntos de falhas**, nunca de contagens: a suite desta
casa não é idempotente (corridas mutam dados versionados), e um `40` contra um
`42` não diz quais. Duas armadilhas apareceram por causa disso:

- um ficheiro de teste em estilo de script levantava `SystemExit(1)` na
  importação e matava a corrida inteira do pytest com `INTERNALERROR` — medido
  igual com e sem o port, e por isso isolado e medido à parte;
- subtestes cujo identificador **contém o valor medido** aparecem como falhas
  «novas» quando o valor muda, sendo a mesma falha antiga.

    UMA CONTAGEM NÃO DIZ QUAIS. COMPARA-SE O CONJUNTO.

## 91.9 · O QUE FICA POR SABER

- Se a troca de transporte do sensor deve ser **desfeita** em vez de mitigada. A
  razão original dela continua válida; a forma é que não.
- Quatro dos cinco workflows pagos chamam a porta paga pelo próprio pé, e com
  isso passam ao lado do teto de rede, do teto de gasto e do checkpoint que o
  orquestrador instala. Medido, não migrado.
- As 77 fontes continuam `NAO_AVALIADA` para efeito do portão de relevância, e
  esse é o estado honesto delas até alguém as avaliar.
