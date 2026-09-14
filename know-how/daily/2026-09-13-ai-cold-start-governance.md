# DAILY KNOW-HOW — 2026-09-13 — AI COLD START / REPOSITÓRIO AUTOEXPLICATIVO

Este arquivo pertence à trilha canônica `know-how/daily/`. Registra somente o delta durável desta decisão; **não cria um segundo KNOW-HOW** e não substitui `SINTONIA-EAME-KNOW-HOW.md`, Bíblias, contratos, System Map, Git, código, runtime ou provas.

## PRINCÍPIO

O SINTONIA deve ser retomável por qualquer IA, em qualquer aba, conta, agente ou momento, **sem depender da memória de conversas anteriores**.

```text
CHAT MEMORY != PROJECT MEMORY
TAB CONTEXT != SOURCE OF TRUTH
AI REMEMBERS != PROJECT KNOWS
```

A memória durável do projeto precisa estar no Git e nas autoridades/provas canônicas.

A meta é que uma IA que nunca viu o projeto consiga fazer um **cold start** e reconstruir de forma determinística:

```text
O QUE É O SINTONIA
O QUE EXISTE AGORA
COMO DEVE FUNCIONAR
QUEM MANDA EM CADA CONCEITO
COMO AS PARTES SE LIGAM
O QUE JÁ FOI PROVADO
O QUE CONTINUA UNKNOWN
QUAL PARTE ELA ESTÁ AUTORIZADA A ALTERAR
QUAIS PARTES SERÃO AFETADAS
```

## 1 · O REPOSITÓRIO PRECISA SER AUTOEXPLICATIVO

Uma IA nova não deve precisar perguntar a uma aba antiga “o que estava acontecendo?”.

Ela deve conseguir começar por um ponto de entrada canônico e navegar a cadeia:

```text
ENTRYPOINT DE GOVERNANÇA
        ↓
INSTRUÇÕES PERMANENTES
        ↓
REGISTRO DE AUTORIDADES
        ↓
BÍBLIAS / CONTRATOS / DECISÕES / KNOW-HOW
        ↓
SYSTEM MAP MEDIDO
        ↓
CÓDIGO / BANCO / RUNTIME / TESTES / PROVAS
```

O ponto de entrada não substitui os donos reais. Ele roteia até eles.

```text
ONE CONCEPT -> ONE OWNER
ONE OWNER -> MULTIPLE POINTERS
```

## 2 · COLD START NÃO SIGNIFICA LER O REPOSITÓRIO INTEIRO EM TODA MISSÃO

O requisito é **compreensão reconstruível**, não leitura indiscriminada.

Uma IA deve conseguir enxergar a árvore inteira e então aprofundar apenas o caminho relevante à missão.

Fluxo desejado:

```text
ENTENDER O TODO
      ↓
LOCALIZAR O DOMÍNIO
      ↓
LOCALIZAR O OWNER
      ↓
LER AS AUTORIDADES NECESSÁRIAS
      ↓
MEDIR IMPLEMENTAÇÃO E PROVAS REAIS
      ↓
SÓ ENTÃO ALTERAR
```

Collection não exige reler toda a Bíblia de Casco para corrigir um adapter; mas a IA precisa saber que Casco existe, onde está, qual é sua fronteira e se a mudança cruza essa fronteira.

## 3 · PROTOCOLO MÍNIMO DE COLD START

Antes de trabalho estrutural, uma IA nova deve conseguir executar conceitualmente esta sequência:

```text
1. MEDIR GIT
   branch
   HEAD
   worktree
   ancestry relevante

2. LER INSTRUÇÕES PERMANENTES
   AGENTS / CLAUDE / equivalentes vigentes

3. ENTRAR PELA SALA DE CONTROLE / GOVERNANCE ENTRYPOINT
   descobrir owners e autoridades

4. IDENTIFICAR O DOMÍNIO DA MISSÃO
   Governance
   Collection
   Intelligence
   Delivery/Casco
   Evidence/System Map

5. LER AS AUTORIDADES DO DOMÍNIO
   Bíblia
   contratos
   decisões arquiteturais
   Know-how relevante + deltas recentes

6. USAR SYSTEM MAP PARA ENTENDER TOPOLOGIA MEDIDA
   nunca como autoridade arquitetural

7. MEDIR ESTADO REAL
   código
   banco/runtime
   testes
   provas
   artefatos gerados

8. IDENTIFICAR UPSTREAM/DOWNSTREAM
   quem chama
   quem depende
   quem governa
   quem valida

9. CLASSIFICAR
   FATO
   INFERÊNCIA
   HIPÓTESE
   UNKNOWN

10. SÓ ENTÃO IMPLEMENTAR
```

Se uma etapa necessária não puder ser resolvida:

```text
NÃO SEI / PRECISA MEDIR
```

Nunca preencher a lacuna com memória de chat ou suposição.

## 4 · O SYSTEM MAP É A VISÃO NAVEGÁVEL, NÃO A MEMÓRIA ÚNICA

O System Map deve permitir que uma IA ou pessoa veja a cadeia do projeto e navegue entre:

```text
GOVERNANCE PLANE
OPERATIONAL PLANE
EVIDENCE PLANE
```

Mas continua valendo:

```text
SYSTEM MAP != AUTHORITY
SYSTEM MAP != RUNTIME
SYSTEM MAP != KNOW-HOW
SYSTEM MAP != BIBLE
```

Ele deve apontar para os owners e provas, não absorvê-los.

## 5 · TODA PEÇA PRECISA RESPONDER “ONDE ESTOU NA ÁRVORE?”

Ao tocar um card, processo, arquivo ou contrato, a IA deve conseguir descobrir:

```text
QUAL CONCEITO É ESTE?
QUEM É O OWNER?
QUAL DOMÍNIO?
QUAL AUTORIDADE GOVERNA?
O QUE IMPLEMENTA?
QUEM CHAMA?
O QUE ELE CHAMA?
O QUE LÊ?
O QUE ESCREVE?
QUEM CONSOME?
QUAL PROVA EXISTE?
QUAL ESTADO É DECLARED?
QUAL ESTADO É OBSERVED?
```

Se isso não puder ser descoberto, existe uma dívida de governança/observabilidade.

## 6 · ALTERAÇÃO LOCAL PRECISA TER CONTEXTO GLOBAL SUFICIENTE

A IA não precisa conhecer cada linha do SINTONIA para alterar uma peça, mas precisa saber o suficiente para não quebrar a arquitetura ao redor.

Antes de alterar um componente, deve localizar pelo menos:

```text
OWNER
GOVERNING AUTHORITY
UPSTREAM
DOWNSTREAM
CONTRACTS
PROOFS
SYSTEM MAP POSITION
```

Isto preserva:

```text
MODULE EXISTS != EDGE EXISTS != FLOW EXISTS
DECLARED EDGE != OBSERVED EDGE
CAN DO != DID DO
```

## 7 · AUTORIDADE OU MEMÓRIA QUE SÓ EXISTE NUMA ABA É CONHECIMENTO PERDIDO

Qualquer aprendizado durável que mude como outra missão deve trabalhar precisa aterrissar no Git.

```text
IMPORTANT KNOWLEDGE ONLY IN CHAT = GOVERNANCE FAILURE
```

Exemplos:

```text
nova lei
mudança arquitetural
limitação provada
ferramenta canônica/aposentada
erro importante
solução validada
nova fronteira entre domínios
mudança de owner
```

Devem atualizar a autoridade apropriada ou o Know-how canônico.

## 8 · HANDOFF AJUDA A RETOMADA, MAS NÃO PODE SER A ÚNICA PORTA

Handoff serve para contexto operacional e continuidade de missão.

Não pode ser necessário para entender a arquitetura inteira.

```text
HANDOFF = CONTEXTO DE RETOMADA
HANDOFF != CONSTITUIÇÃO
HANDOFF != KNOW-HOW
HANDOFF != CURRENT STATE PROOF
```

Se perder um handoff tornar o projeto incompreensível, a governança falhou.

## 9 · CONSEQUÊNCIA PARA A SALA DE CONTROLE

A futura Sala de Controle / Governance Entrypoint deve ser projetada para cold start.

Uma IA nova deve abrir um único ponto e descobrir pelo menos:

```text
WHAT IS SINTONIA?
CURRENT GIT STATE — como medir, não um número congelado
PROJECT ORDER
DOMAINS
AUTHORITIES
OWNERS
BIBLES
CONTRACTS
KNOW-HOW
DECISIONS
SYSTEM MAP
PROOF PATHS
HISTORICAL / SUPERSEDED / RECOVERY_PENDING
```

A Sala de Controle aponta; não duplica as leis.

## 10 · CONSEQUÊNCIA PARA CARDS

Cards são parte da linguagem de navegação do cold start.

Um card não existe só para ficar bonito no mapa.

Ele precisa permitir responder rapidamente:

```text
O QUE É?
POR QUE EXISTE?
QUEM POSSUI?
QUEM GOVERNA?
COMO SE LIGA?
O QUE FOI DECLARADO?
O QUE FOI OBSERVADO?
QUAL PROVA?
```

Logo, cards, registry, schemas e System Map devem convergir para a mesma semântica — sem que a UI vire fonte de verdade.

## 11 · CRITÉRIO DE QUALIDADE DA GOVERNANÇA

O teste mental passa a ser:

> Se amanhã desaparecerem todas as abas de ChatGPT/Claude e entrar uma IA nova apenas com acesso ao repositório e aos ambientes autorizados, ela consegue reconstruir com segurança o que é o SINTONIA e trabalhar na peça certa sem inventar arquitetura?

Resultado desejado:

```text
YES, FROM REPO + RUNTIME + PROOFS
```

Se a resposta depender de Luciano lembrar uma conversa, de uma aba antiga ou de “alguém saber onde está o arquivo”, o sistema ainda não está governado o suficiente.

## O QUE MUDOU

Foi formalizado o princípio de **AI COLD START / REPOSITÓRIO AUTOEXPLICATIVO** como objetivo de governança do SINTONIA.

## POR QUÊ

O projeto é desenvolvido por múltiplas abas e agentes. Memória conversacional é transitória e não pode determinar arquitetura, estado ou continuidade.

## PROVA / ORIGEM

A necessidade foi demonstrada operacionalmente por autoridades e conhecimentos importantes terem ficado distribuídos em branches e por uma Bíblia anteriormente produzida não estar prontamente encontrável. O delta anterior de cards/governança já formalizou a necessidade de Governance Plane e relações explícitas; este delta define o requisito de retomada por qualquer IA.

## CONSEQUÊNCIA

Governança, Sala de Controle, cards e System Map devem ser avaliados também pela capacidade de **cold start sem memória de chat**.

Nenhuma UI, handoff ou aba pode ser requisito oculto para compreender o sistema.

## O QUE NÃO MUDOU

- nenhuma Bíblia foi alterada;
- nenhum contrato operacional foi alterado;
- nenhum código/runtime foi alterado;
- nenhum System Map foi alterado;
- nenhuma implementação de Collection, Intelligence ou Delivery foi iniciada;
- Git/runtime/provas continuam vencendo memória e narrativa para estado atual.

`KNOW_HOW_DELTA = ATUALIZADO`

HARD STOP.
