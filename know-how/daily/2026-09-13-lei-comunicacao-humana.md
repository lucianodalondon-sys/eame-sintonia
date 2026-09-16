# DAILY KNOW-HOW — 2026-09-13 — LEI DE COMUNICAÇÃO HUMANA

## DECISÃO DURÁVEL

Luciano, dono do SINTONIA, não precisa falar ou pensar como engenheiro de software para comandar o projeto. O sistema deve traduzir a engenharia para linguagem de decisão humana sem perder precisão técnica.

```text
O DONO NÃO PRECISA APRENDER A FALAR COMO O CÓDIGO.
O SISTEMA PRECISA APRENDER A EXPLICAR O CÓDIGO AO DONO.
```

A partir desta decisão, códigos internos como `E7`, `G4`, `G5`, `B5B`, números de migration e nomes de gates nunca podem ser usados sozinhos como explicação quando orientam uma decisão humana.

Na primeira ocorrência relevante, devem vir acompanhados do significado simples, por exemplo:

```text
E7 (contrato do texto: preserva se o texto é legenda, transcrição, tradução etc.)
G4 (System Map: declara o que cada etapa lê e produz)
029 (atualização do banco que cria a relação de participação na derivação)
```

## POR QUÊ

Foi observado um risco operacional de coordenação: as missões podiam continuar tecnicamente corretas enquanto o dono perdia a visão de:

- onde o projeto estava;
- o que a missão estava fazendo;
- por que aquilo era necessário;
- se aquilo bloqueava ou não o objetivo principal;
- qual decisão vinha a seguir.

Quando isso acontece, uma missão pode sair do rumo não porque a engenharia falhou, mas porque a pessoa que define a direção não recebeu uma explicação utilizável.

```text
CÓDIGO CORRETO + EXPLICAÇÃO INCOMPREENSÍVEL = COORDENAÇÃO INCOMPLETA.
```

## CONTRATO OPERACIONAL

Toda missão relevante deve ter duas camadas.

Primeiro, linguagem simples:

```text
ONDE ESTAMOS?
O QUE VAMOS FAZER?
POR QUE?
O QUE MUDA SE DER CERTO?
O QUE NÃO VAMOS FAZER AGORA?
```

Depois, o contrato técnico completo.

Toda entrega deve terminar com uma camada humana curta:

```text
ONDE ESTAMOS AGORA?
O QUE FOI FEITO?
POR QUE ISSO IMPORTA?
O QUE AINDA FALTA?
HÁ ALGUM RISCO?
QUAL É O PRÓXIMO PASSO MÍNIMO?
```

A simplificação de linguagem nunca autoriza simplificação da prova. Continuam valendo `NÃO SEI`, `PRECISA MEDIR`, `UNKNOWN != NO`, `CAN DO != DID DO` e todas as leis técnicas existentes.

## SYSTEM MAP

A mesma regra deve chegar à interface: códigos internos podem continuar visíveis para rastreabilidade, mas nunca como único rótulo humano. `G5` sozinho não basta; deve ser algo como `G5 — unificar todos os passos do mapa em uma cadeia única`.

O System Map existe justamente para permitir que o dono veja a máquina por fora. Se a interface exige decorar siglas internas para entender o sistema, ela não cumpriu esse objetivo.

## PROVA / ARTEFATOS

Foi criado o owner operacional:

`LEI-DE-COMUNICACAO-HUMANA.md`

na branch:

`claude/lei-comunicacao-humana-v1`

O `CLAUDE.md` dessa branch foi atualizado para exigir leitura da lei e para obrigar a camada `EM PALAVRAS FÁCEIS` no início e `RESUMO PARA O DONO` no fechamento das missões.

A branch funcional não foi movida durante a missão de integração E7 que já estava rodando; isso evita criar drift artificial numa missão paralela. A lei precisa ser integrada na linha funcional quando essa janela fechar.

## CONSEQUÊNCIA

- prompts futuros devem explicar siglas e códigos quando aparecem;
- handoffs e status devem situar o projeto antes do detalhe técnico;
- decisões de prioridade devem ser descritas em termos do efeito prático;
- dúvidas do dono sobre significado interrompem o empilhamento de siglas: primeiro se explica, depois se continua;
- missões não ganham autorização implícita apenas porque um código interno foi citado;
- o System Map deve evoluir para rótulos humanos junto dos identificadores internos.

## FECHAMENTO

1. **O que mudou?** Nasceu uma lei operacional que torna compreensão do dono parte obrigatória da coordenação do SINTONIA.
2. **Por quê?** O projeto pode tecnicamente avançar e ainda assim perder direção se o dono não entender o que os códigos internos significam.
3. **Prova:** `LEI-DE-COMUNICACAO-HUMANA.md` e `CLAUDE.md` na branch `claude/lei-comunicacao-humana-v1`.
4. **O que não mudou?** Nenhuma arquitetura, Collection, SCRAP, System Map, banco, Admission, Intelligence ou LIVE foi alterado por esta decisão.
5. **O que continua desconhecido?** O momento exato em que a branch funcional ficará livre para receber esta lei sem criar drift na missão em andamento.
6. **Risco restante:** agentes em branches antigas não verão automaticamente o novo arquivo até a integração.
7. **Bíblia/contrato precisa mudar?** Não. Esta é uma lei de coordenação/comunicação, não uma mudança semântica da Collection.
8. **Próximo passo mínimo:** quando a missão funcional atual fechar, integrar a branch da lei sem sobrescrever trabalho posterior.

`KNOW_HOW_DELTA = ATUALIZADO`

HARD STOP.
