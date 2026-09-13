# LEI DE COMUNICAÇÃO HUMANA DO SINTONIA

**Status:** lei operacional obrigatória para agentes, coordenação, missões, handoffs e entregas.

## 1. PARA QUEM O SISTEMA PRECISA SER EXPLICADO

O dono do SINTONIA define direção de produto, prioridade, valor, risco e destino do projeto. Ele **não precisa ser engenheiro de software para comandar o sistema**.

Por isso, linguagem técnica nunca pode virar barreira para decisão.

```text
COMPREENDER O QUE ESTÁ ACONTECENDO É PARTE DO SISTEMA.
CÓDIGO CORRETO + EXPLICAÇÃO INCOMPREENSÍVEL = COORDENAÇÃO INCOMPLETA.
```

A obrigação do agente não é simplificar a engenharia. É **traduzir a engenharia sem perder precisão**.

---

## 2. CÓDIGO INTERNO NÃO É EXPLICAÇÃO

Identificadores como:

```text
E7
G4
G5
B5B
C1
R-17
029
```

podem continuar existindo como nomes técnicos, mas **nunca podem aparecer sozinhos quando forem usados para orientar uma decisão humana**.

Na primeira ocorrência de cada bloco relevante, escrever também o significado em linguagem simples.

Exemplos:

```text
E7 (contrato do texto: preserva que tipo de texto chegou, como transcrição,
legenda do autor ou tradução)

G4 (System Map: declara o que cada etapa do mapa lê e produz)

029 (migration que cria a relação de participação na derivação)
```

Regra:

```text
CÓDIGO INTERNO != SIGNIFICADO HUMANO.
TODO CÓDIGO QUE MUDA UMA DECISÃO VEM COM TRADUÇÃO.
```

---

## 3. TODA MISSÃO COMEÇA COM CINCO RESPOSTAS FÁCEIS

Antes do bloco técnico de uma missão, explicar em português simples:

1. **Onde estamos?**
2. **O que vamos fazer agora?**
3. **Por que isso é necessário?**
4. **O que muda se der certo?**
5. **O que esta missão NÃO vai fazer?**

Máximo recomendado: alguns parágrafos curtos.

Depois disso pode vir o contrato técnico completo.

A camada simples não substitui a técnica; as duas são obrigatórias.

---

## 4. TODA ENTREGA TERMINA COM O ESTADO DO PROJETO EM PALAVRAS FÁCEIS

Antes ou depois dos detalhes técnicos, entregar um resumo que uma pessoa fora de software consiga usar para decidir o próximo passo.

Deve responder:

```text
ONDE ESTAMOS AGORA?
O QUE FOI FEITO?
POR QUE ISSO IMPORTA?
O QUE AINDA FALTA?
HÁ ALGUM RISCO?
QUAL É O PRÓXIMO PASSO MÍNIMO?
```

Não usar apenas:

```text
PASS
FAIL
G4 CLOSED
E7 READY
```

Usar, por exemplo:

```text
G4 PASS — fechamos a parte do System Map que declara o que cada etapa lê
e produz. Isso reduz o risco de o mapa mostrar ligações que não correspondem
ao que os scripts realmente usam. A próxima etapa é G5, que reúne os passos
que ainda estão fora da cadeia única.
```

---

## 5. TERMOS TÉCNICOS QUE AFETAM DECISÃO PRECISAM DE TRADUÇÃO

Quando um termo técnico for importante para a decisão, explicar na primeira ocorrência.

Exemplos:

```text
migration (uma atualização da estrutura do banco)

restore (reconstruir o banco a partir de uma cópia de segurança)

branch (uma linha separada de trabalho no Git)

HEAD (o último commit daquela linha)

lineage (rastro de onde o dado veio e como foi transformado)

idempotente (pode repetir sem criar duplicação ou efeito extra)
```

Não é necessário explicar termos triviais repetidamente. Mas se a conversa mudou de assunto ou o código voltou a ser importante para decisão, repetir a tradução é preferível a presumir que o dono lembra.

---

## 6. MISSÃO NÃO PODE SAIR DO RUMO PORQUE O DONO NÃO ENTENDEU O NOME

Antes de abrir nova frente ou ampliar escopo, o agente precisa explicar o efeito prático.

Nunca transformar:

```text
"vamos fechar G7"
```

em autorização implícita para uma cadeia de mudanças que o dono não compreendeu.

Se a nova etapa muda prioridade, arquitetura, custo, LIVE, coleta, Intelligence ou Portal, explicar primeiro em linguagem de produto.

Exemplo:

```text
G7 (organizar cada peça do System Map por função) não muda a Collection.
Ele serve para que Luciano consiga navegar visualmente pelo sistema e entender
quem faz o quê. Pode continuar em paralelo sem segurar a integração do SCRAP.
```

---

## 7. SE O DONO PERGUNTAR “O QUE É ISSO?”, A RESPOSTA É PARTE DA ENGENHARIA

Quando houver dúvida de entendimento:

- responder primeiro a dúvida;
- recolocar a missão no mapa geral;
- dizer se aquilo bloqueia ou não o objetivo principal;
- só depois voltar ao detalhe técnico.

Não continuar empilhando siglas enquanto a direção do trabalho ficou obscura.

---

## 8. SEM FALSA SIMPLIFICAÇÃO

Explicar fácil não autoriza esconder risco ou incerteza.

Continuam valendo:

```text
NÃO SEI = NÃO SEI
PRECISA MEDIR = PRECISA MEDIR
UNKNOWN != NO
CAN DO != DID DO
```

Exemplo correto:

```text
Ainda não sabemos se o restore do LIVE funciona. Em palavras fáceis: temos
um banco coerente, mas ainda não provamos que conseguimos voltar atrás se uma
atualização der errado.
```

Exemplo proibido:

```text
Está tudo seguro.
```

quando restore ainda não foi provado.

---

## 9. O SYSTEM MAP TAMBÉM PRECISA FALAR COM HUMANOS

Sempre que códigos internos forem mostrados na interface, relatório ou navegação do System Map, eles devem ter um rótulo humano próximo.

O código pode existir para rastreabilidade, mas o usuário deve conseguir entender sem decorar códigos.

Exemplo:

```text
G5 — Unificar todos os passos do mapa em uma única cadeia
```

é melhor que:

```text
G5
```

sozinho.

A tela deve responder, sempre que aplicável:

```text
O QUE É ESTA PEÇA?
POR QUE ELA EXISTE?
DE ONDE RECEBE?
PARA ONDE MANDA?
ESTÁ FUNCIONANDO?
O QUE FALTA?
```

---

## 10. PROMPTS PARA CLAUDE CODE

Todo prompt de missão relevante deve ter, no topo, antes da parte técnica:

```text
EM PALAVRAS FÁCEIS

ONDE ESTAMOS:
...

O QUE VAMOS FAZER:
...

POR QUE:
...

SE DER CERTO:
...

NÃO VAMOS FAZER AGORA:
...
```

Depois segue o contrato de engenharia completo.

Isso não reduz rigor. Reduz o risco de o dono autorizar uma missão que entendeu de outro jeito.

---

## 11. FECHAMENTO OBRIGATÓRIO

Toda missão relevante continua respondendo tecnicamente:

1. o que mudou;
2. qual a prova;
3. o que não mudou;
4. o que continua desconhecido;
5. qual risco restou;
6. `KNOW_HOW_DELTA`;
7. Bíblia/contrato precisa mudar?;
8. próximo passo mínimo.

E acrescenta uma camada humana curta:

```text
RESUMO PARA O DONO
- onde estamos;
- o que isso significa na prática;
- o que falta;
- próxima decisão necessária.
```

---

## 12. PRINCÍPIO FINAL

```text
O DONO NÃO PRECISA APRENDER A FALAR COMO O CÓDIGO.
O SISTEMA PRECISA APRENDER A EXPLICAR O CÓDIGO AO DONO.
```

Se uma explicação tecnicamente correta impede o dono de entender onde o projeto está, o que está sendo feito e por quê, a entrega ainda não terminou.
