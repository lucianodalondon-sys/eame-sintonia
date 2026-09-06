# AUTOMACAO — desenhada e executavel, nao ligada

    SCHEDULER_ATIVO      = NAO
    COLETA_RECORRENTE    = NAO
    DEPLOY               = NAO
    PIPELINE_EXECUTAVEL  = SIM  (sh v1/pipeline.sh AAAA-MM-DD)

## A esteira, e onde o passo caro fica

| # | passo | custo | roda quando |
|---|---|---|---|
| 1 | CHECK OFFICIAL REGISTRY | baixo | semanal |
| 2 | SNAPSHOT | baixo | semanal |
| 3 | HASH / IDENTITY | quase zero | semanal |
| 4 | DOCUMENT CHECK | baixo | semanal |
| 5 | DOWNLOAD IF NEEDED | **alto** | **so quando o hash muda** |
| 6 | PRESERVE RAW | medio | por evento |
| 7 | READ (texto/geometria) | **alto** | por evento |
| 8 | STRUCTURE (uso, dose) | **alto** | por evento |
| 9 | COMPARE | baixo | semanal |
| 10 | FILTER NOISE | baixo | semanal |
| 11 | CREATE CHANGE EVENTS | baixo | semanal |
| 12 | INTELLIGENCE | baixo | semanal |
| 13 | REVIEW GATE | humano | por excecao |
| 14 | PUBLISH TO TOOL | baixo | semanal |

Os passos 5, 7 e 8 sao os caros, e sao justamente os que **so disparam quando o
hash do documento muda**. Por isso a cadencia real da esteira e por evento, e o
semanal cobre so a varredura.

## Cadencia justificada pela taxa medida

O Ministero declara a data de vigencia de cada etichetta. Dos 163 rotulos, 161
declaram, e delas sai a taxa: **32% dos rotulos sao renovados por ano**, com
idade mediana de 2,1 anos e 49 renovados nos ultimos seis meses.

    32% ao ano sobre 163 rotulos = ~1 rotulo por semana muda

Semanal cobre isso com folga. Diario seria desperdicio: o passo caro nao
dispararia em 6 dias de cada 7. O unico passo que faz sentido diario e a
aritmetica de vencimento, que nao custa nada.

## O que pode rodar sozinho e o que nao pode

**Sozinho, porque o resultado e verificavel por construcao:** localizar o rotulo,
baixar, preservar com sha256, detectar que o documento mudou, extrair texto,
calcular vencimento, montar a fila de revisao, e filtrar ruido de serializacao.

**Com revisao por amostra:** estruturar cultura x alvo (precisao 0,965 / recall
0,870 medidos em 30 de 163 rotulos) e estruturar dose (F1 0,90 medido em 3 de
163, com 13 valores rebaixados pelos fios da tabela).

**Humano por natureza:** decidir se uma mudanca importa para o negocio, e
interpretar regulacao. A esteira entrega o antes e o depois; quem decide o que
isso significa e gente.

## O portao que impede publicar lixo

`v1/pipeline.sh` roda `v1/testes/test_ruido.py` **antes** de montar a ferramenta.
Se qualquer perturbacao inocente fabricar um evento, o pipeline para e nada e
publicado. Foi assim que se descobriu que reindentar o CSV fabricava 2.028
eventos.

## O que falta para ligar de verdade

1. **Ambiente com rede estavel para o host das etichette.** Ele e intermitente:
   a mesma consulta alterna entre a ficha e um erro generico, e foi preciso 2 a 4
   tentativas por registro. Um agendador precisa de retry com sessao nova, que o
   codigo ja faz, mas o custo em tempo precisa ser medido em regime.
2. **Lugar para o RAW.** Hoje os PDFs e os instantaneos vivem no disco da sessao
   e sao ignorados pelo git. Em regime precisam de um bucket com o mesmo
   `sha256` conferido na volta.
3. **Dono da fila de revisao.** A esteira produz `NEEDS_REVIEW`; alguem tem de
   adjudicar. Sem isso a fila cresce e a ferramenta perde a propriedade que a
   torna confiavel.
4. **Decisao sobre janela de retencao** dos 260 MB de instantaneos semanais.

    AUTOMATION_READINESS = PIPELINE_PRONTO_SCHEDULER_NAO_LIGADO
