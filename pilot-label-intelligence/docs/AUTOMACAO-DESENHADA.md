# AUTOMACAO CONTINUA — DESENHADA, NAO LIGADA

`SCHEDULER_ACTIVE = NAO`
`RECURRENT_COLLECTION_ENABLED = NAO`

Este documento descreve como o produto funcionaria em regime. Nada aqui esta ligado nesta
missao, por decisao explicita: a missao pede desenhar, nao ativar.

## A esteira

    SCHEDULER
      -> CHECK OFFICIAL REGISTRY      le a fonte oficial, nao o nosso cache
      -> DETECT DOCUMENT CHANGE       compara document id + sha256 contra o ultimo conhecido
      -> DOWNLOAD                     so quando algo mudou
      -> PRESERVE                     RAW + sha256 + bytes + captured_at + HTTP metadata
      -> PARSE                        PDF -> texto, com estado de falha explicito
      -> STRUCTURE                    texto -> linhas cultura x alvo x dose, com citacao
      -> COMPARE                      versao nova x versao anterior
      -> ALERT                        so quando o diff tem significado regulatorio
      -> HUMAN REVIEW                 onde a maquina nao deve decidir sozinha

## O gargalo que decide a cadencia

Reler 163 PDFs todo dia e desperdicio: um rotulo oficial muda em escala de meses, nao de horas.
A esteira e barata porque o passo 2 e barato. `CHECK` e `DETECT` custam um HEAD/GET pequeno na
ficha oficial; `DOWNLOAD` e `PARSE`, que sao os passos caros, so rodam quando o hash mudou.

## Cadencia proposta

| passo | cadencia | por que |
|---|---|---|
| CHECK OFFICIAL REGISTRY | **semanal** | o dataset oficial e republicado periodicamente, nao continuamente |
| DETECT DOCUMENT CHANGE | **semanal**, junto | mesmo request |
| EXPIRY WATCH | **diario** | e so aritmetica sobre data ja capturada, custa quase nada |
| DOWNLOAD / PRESERVE | **por evento** | so quando DETECT acusa mudanca |
| PARSE / STRUCTURE | **por evento** | so sobre documento novo |
| COMPARE / ALERT | **por evento** | so quando existe versao anterior real |
| HUMAN REVIEW | **por excecao** | so no que a regua marcar |

`EVENT-BASED` domina a esteira. `DAILY` cobre so vencimento. `WEEKLY` cobre so a varredura.

## Onde a maquina pode decidir sozinha

Automatico sem revisao, porque o resultado e verificavel por construcao:

- descobrir que existe rotulo para um registro;
- baixar e preservar (sha256 prova o que foi baixado);
- detectar que o documento mudou (hash e binario, nao interpretativo);
- extrair texto;
- calcular vencimento proximo;
- montar a fila de revisao.

## Onde a revisao humana continua prudente

- **Interpretacao regulatoria.** "Esta mudanca de dose muda o que o cliente pode vender?" e
  juizo tecnico, nao parsing.
- **Promover `TEXT_CHANGE_OTHER` para mudanca de uso.** So um humano decide que uma reformulacao
  de frase e, de fato, uma restricao nova.
- **Linha de uso com citacao ambigua.** Se `SOURCE_QUOTE` nao ancora sozinha, vai para fila.
- **Primeira leitura de um layout de rotulo novo.** Layout novo = parser sem historico.
- **Aquisicao de rotulo fisico.** Fora de alcance de qualquer automacao nossa.

## A regra que a esteira nunca pode quebrar

    PARSER_FAILURE != REGULATORY_ABSENCE

Quando `STRUCTURE` nao acha a tabela de usos, a esteira grava `PARSE_STATE = FAILED` e manda
para `HUMAN REVIEW`. Ela **nunca** grava "produto sem usos autorizados". Um piloto que confunde
os dois entrega ao cliente uma ausencia inventada, que e pior que nao entregar nada.
