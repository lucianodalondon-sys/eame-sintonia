# CONCORRENTES — medido, nao especulado

A pergunta da missao: *"se adicionarmos concorrentes, esta ferramenta passa de
Regulatory Monitor para Portfolio/Competitive Intelligence?"*

Passa. E o custo de coleta da camada de registro e **zero**, porque o dado ja
esta no disco.

## O achado

O registro italiano nao e um registro da ADAMA. Os 54 instantaneos ja baixados
contem o mercado inteiro. Rodando exatamente o mesmo differ **sem o filtro de
titular**, sobre exatamente os mesmos arquivos:

    eventos regulatorios reais, ADAMA        =    34
    eventos regulatorios reais, mercado      = 2.298
    produtos ativos, ADAMA                   =   163  (4,4%)
    produtos ativos, mercado                 = 3.714
    titulares distintos com produto ativo    =   244

Nenhum download novo. Nenhuma rota nova. Uma linha de filtro.

## O que aparece quando o filtro sai

| tipo de evento | mercado | o que e |
|---|---|---|
| `EXPIRY_CHANGED` | 1.438 | prazos de autorizacao se movendo |
| `PRODUCT_ADDED` | 308 | **produto entrando no registro** |
| `STATUS_CHANGED` | 183 | mudanca de estado administrativo |
| `HOLDER_CHANGED` | 166 | **registro trocando de titular** |
| `ACTIVE_INGREDIENT_CHANGED` | 93 | composicao declarada mudou |
| `REVOCATION_*` | 84 | atos de revoga com data |
| `PRODUCT_NAME_CHANGED` | 22 | renomeacao sobre o mesmo registro |

Duas linhas mudam a natureza da ferramenta. **`PRODUCT_ADDED`** e um produto
concorrente entrando no registro — que e o sinal mais cedo que existe de um
lancamento, e chega antes de qualquer comunicacao comercial.
**`HOLDER_CHANGED`** e um registro trocando de dono, que e movimento de
portfolio entre empresas.

Titulares com mais eventos na janela:

    146  SHARDA CROPCHEM        102  SYNGENTA ITALIA
    125  BASF AGRICULTURAL      92   NUFARM ITALIA
    116  GOWAN ITALIA           91   BAYER CROPSCIENCE
                                85   CORTEVA AGRISCIENCE

## Um numero que so aparece com o mercado do lado

A ADAMA tem **4,4% dos produtos ativos** e **1,5% dos eventos** da janela. Ou
seja: nesta janela o portfolio da ADAMA mexeu **menos que o mercado**.

Isso e uma leitura de portfolio que a ferramenta so consegue fazer com o
denominador do mercado presente. Sozinha, ela nunca saberia se 34 eventos e
muito ou pouco.

    SEM CONCORRENTE: "houve 34 mudancas"
    COM CONCORRENTE: "houve 34, e o mercado teve 2.298 — a ADAMA mexeu menos"

## Custo, separado por camada

| camada | custo de estender | por que |
|---|---|---|
| registro (status, validade, titular, ativos, entrada/saida) | **zero** | os 54 instantaneos ja contem os 3.714 produtos |
| rotulo em PDF (uso, dose) | **alto** | ~3.714 fichas x 2,6 tentativas medias no servlet intermitente, mais download e leitura |

O piloto ja provou a rota de rotulo para concorrente com 4 casos reais baixados
da fonte oficial: VALGRAN (Nufarm), ACTELLIC (Syngenta), OLIOCIN (Bayer) e
CURZATE (Corteva), tres deles com tabela de uso.

## Respostas

    COMPETITOR_EXTENSION_VALUE = ALTO NA CAMADA DE REGISTRO, e ja medido:
      2.298 eventos reais disponiveis sem coleta nova, incluindo 308 entradas de
      produto e 166 trocas de titular. E o denominador de mercado, que transforma
      "34 mudancas" em "34 contra 2.298".

    COMPETITOR_COLLECTION_COST = ZERO na camada de registro.
      ALTO na camada de rotulo (PDF), e desnecessario para o valor acima.

    COMPETITOR_V1_RECOMMENDATION = ESTENDER SO A CAMADA DE REGISTRO.
      Ligar o filtro de titular na ferramenta e entregar entrada de produto,
      troca de titular e o denominador de mercado. NAO abrir coleta de rotulo de
      concorrente agora: e o pedaco caro e nao e o que muda a natureza da
      ferramenta.

## O que NAO foi feito, e por que

A extensao **nao foi ligada** nesta versao. A missao manda medir e diz que
ADAMA-first continua prioridade, e ligar o mercado inteiro na tela hoje afogaria
os 34 eventos que interessam ao cliente em 2.298. A medida esta feita e o
caminho esta aberto; a decisao de escopo e de quem opera.

    COMPETITOR_EXTENSION_ENABLED_IN_V1 = NAO
