# O QUE DA PARA SUBSTITUIR — classificado por prova, nao por promessa

O cliente paga hoje alguem para "coletar rotulos". Ainda nao sabemos qual das
tarefas dentro dessa frase e a que ele paga. Este documento existe para que a
pergunta possa ser feita de forma util: em vez de perguntar "quanto custa?",
mostrar a lista e perguntar **"quais destas voces pagam hoje?"**.

Nenhum valor em dinheiro aparece aqui. Nao sabemos o que ele paga, e inventar
numero de economia seria a mesma doenca que o piloto inteiro tenta evitar.

## A tabela

| tarefa | classificacao | o que sustenta a classificacao |
|---|---|---|
| **localizar o rotulo oficial** de um registro | `FULLY_AUTOMATABLE` | rota provada do numero de registro ate o PDF; apontada ao registro 015275 sem consultar o acervo, devolveu o mesmo documento que o acervo ja tinha |
| **baixar e preservar** | `FULLY_AUTOMATABLE` | 163/163 baixados nesta sessao, com sha256, bytes e hora de captura; 2 falhas de rede recuperadas na repeticao |
| **detectar que a versao mudou** | `FULLY_AUTOMATABLE` | 163/163 conferidos contra hash arquivado; identidade por sha256 confirmada por tres capturas independentes do mesmo PDF |
| **extrair o texto** | `FULLY_AUTOMATABLE` | 163/163 com texto recuperavel, 2.793.649 caracteres; geometria reproduzida byte a byte contra a versionada |
| **acompanhar validade** | `FULLY_AUTOMATABLE` | aritmetica sobre campo oficial; 3, 26 e 64 vencendo em 30, 90 e 180 dias |
| **detectar mudanca no registro** | `FULLY_AUTOMATABLE` | 54 versoes oficiais arquivadas, 34 mudancas reais isoladas de 496 de ruido |
| **montar a fila de revisao** | `FULLY_AUTOMATABLE` | 35 produtos sem tabela lida, listados como divida de leitura |
| **estruturar cultura x alvo** | `AUTOMATABLE_WITH_REVIEW` | 2.928 pares em 128 dos 163; precisao 0,965 e recall 0,870 medidos contra gabarito manual de 30 rotulos — bom, e nao 100% |
| **estruturar dose e n de aplicacoes** | `AUTOMATABLE_WITH_REVIEW` | tabela lida com colunas por geometria; celula mesclada e linha de continuacao ainda exigem conferencia (ver o limite medido no relatorio do extrator) |
| **classificar o tipo da mudanca** | `AUTOMATABLE_WITH_REVIEW` | a maquina separa campo que mudou de ruido de serializacao; decidir que um texto novo e uma restricao nova nao e parsing |
| **decidir o impacto comercial** de uma mudanca | `HUMAN_REQUIRED` | juizo tecnico e de negocio. A esteira entrega antes e depois; quem decide o que isso significa e gente |
| **interpretacao regulatoria** (vencido = fora do mercado?) | `HUMAN_REQUIRED` | 15 produtos estao com validade passada e ainda listados como autorizados. So um humano decide o que fazer com isso |
| **obter rotulo fisico / foto de embalagem** | `NOT_PROVED` | fora de alcance desta rota. Nao foi tentado e nao se promete |
| **diff historico do proprio rotulo** | `NOT_PROVED` | a maquinaria esta pronta e rodou; em 7 dias nenhum dos 163 documentos mudou, entao nao ha diff real para mostrar |

## O resumo que cabe numa frase

Da esteira de nove passos, **sete rodam sozinhos hoje** e foram rodados de
verdade sobre o universo inteiro. Dois precisam de revisao humana por amostragem,
com a taxa de erro medida e publicada. Dois pedacos continuam humanos por
natureza, e um deles — interpretar o que a mudanca significa para o negocio —
provavelmente e o pedaco que o cliente mais valoriza e o que menos deveria querer
automatizar.

## A pergunta para o cliente

> Destas catorze tarefas, quais voces pagam hoje?

As sete primeiras ja estao substituidas nesta branch, com evidencia clicavel.
As duas seguintes estao substituidas com revisao. As ultimas nao estao, e o
piloto diz isso antes de perguntarem.
