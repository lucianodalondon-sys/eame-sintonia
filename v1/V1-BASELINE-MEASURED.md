# V1 — BASELINE MEDIDO NA FONTE

Nenhum numero deste documento foi herdado de relatorio do piloto. Todos foram
recontados por `v1/medir_baseline.py`, que abre o CSV oficial, os PDFs no disco e
a geometria versionada, e **reexecuta** o differ, o extrator de dose e o validador
de fios. O script nao le `ENTREGA-FINAL.md`, nao le `AUDITORIA.json` e nao le
`IT-LABEL-INTELLIGENCE.json`.

    PILOT_HEAD = df3a4fd0029e74d16f171e5070b13ec4f3345d64
    V1_BASE    = df3a4fd0029e74d16f171e5070b13ec4f3345d64
    V1_BRANCH  = claude/label-intelligence-v1-italy

    conferido: df3a4fd e ancestral de V1; bdb57cf (sintonia/canonical) NAO e.

## Os numeros

    PRODUCT_UNIVERSE          = 163
    LABEL_DISCOVERED          = 163
    LABEL_DOWNLOADED          = 163
    TEXT_EXTRACTED            = 163
    PRODUCTS_WITH_USE_ROWS    = 128
    AUTHORIZED_USE_PAIRS      = 2.928
    DOSE_ROWS_PROVED          = 480
    DOSE_NEEDS_REVIEW         = 9
    HISTORICAL_SNAPSHOTS      = 60
    DISTINCT_HISTORICAL_DOCS  = 54
    RAW_CHANGES               = 528
    TRUE_CHANGES              = 36
    FALSE_CHANGE_NOISE        = 496   (93,9%)
    PHI_PROVED                = 0
    PHI_NOT_PROVED            = 163

## O que cada numero conta, exatamente

**PRODUCT_UNIVERSE = 163.** Do `PROD_FTS_6_20260831.csv`
(sha256 `13537cd10b9fa59a...`): 17.695 linhas no registro, das quais tem titular
ADAMA e nao estao `Revocato` nem `Scaduto`. Por entidade: ADAMA ITALIA 85,
ADAMA AGAN 35, ADAMA MAKHTESHIM 26, ADAMA DEUTSCHLAND 17.

**LABEL_DISCOVERED = 163.** Produtos com URL oficial de etichetta conhecida.
Vem por reuso de `sintonia/canonical @ bdb57cf`, apontado, nao copiado.

**LABEL_DOWNLOADED = 163.** Arquivos `.pdf` no disco, todos comecando com
`%PDF-`, todos com registro dentro do universo. Zero corrompidos.

**TEXT_EXTRACTED = 163.** `pdftotext` rodado agora sobre cada PDF: 163 com mais
de 200 caracteres, 0 vazios, 0 falhas, 1.583.263 caracteres no total.

> Este total **nao bate** com os 2.793.649 caracteres que o acervo canonico
> registra, e a diferenca nao e erro: sao extratores diferentes sobre os mesmos
> documentos. O numero honesto e "163 rotulos tem texto recuperavel", nao um
> total de caracteres comparavel entre ferramentas.

**AUTHORIZED_USE_PAIRS = 2.928 em 128 produtos.** Reuso de canonical, recontado.
Nao sao todos da mesma forca:

| rota | pares | classe |
|---|---|---|
| GEOMETRIC_TABLE | 1.273 | tabela |
| MERGED_COLUMN_TABLE | 74 | tabela |
| HEADER_CONTINUATION | 640 | inferencia de texto |
| AUTHORISED_USE_LIST | 416 | inferencia de texto |
| INLINE_COLON_HEAD | 325 | inferencia de texto |
| INLINE_STATEMENT | 200 | inferencia de texto |

1.347 vem da geometria da tabela; 1.581 foram montados de prosa ou lista;
1.429 nao preservaram pagina. **Nenhum carrega citacao literal** — os pares nao
gravam a coordenada x e a etichetta tem varias colunas por pagina, entao o
trecho nao e recuperavel. Medido no piloto: 921 tentativas, 913 reprovadas na
conferencia, 5 das 8 restantes ainda erradas.

**DOSE: 519 linhas distintas em 23 dos 163 rotulos.**

    480  provadas         tem dose e nenhum fio da tabela as contradiz
      9  precisam revisao um fio separa a linha do valor que ela recebeu
     30  sem dose         a linha existe na tabela e a celula de dose esta vazia
    ---
    519

A leitura crua da 848 linhas; 4 etichette imprimem a tabela duas vezes no mesmo
PDF, entao a contagem publicada e a de distintas.

Conferencia por fios sobre as 848: 660 conferidas, 647 confirmadas, 13
contraditas, 122 nao localizadas.

**Por que so 23 de 163.** Nao e falha de parser em 140 produtos. A maioria dos
herbicidas italianos **nao publica tabela**: declara dose em prosa
("alla dose di 1-3 l/ha"). Este leitor le tabela. Os outros ficam
`NO_USE_TABLE_FOUND`, que e estado de leitura.

    DOSE_COVERAGE = 23/163 lidos por tabela
    O RESTO NAO E "produto sem dose"

**HISTORICO: 60 instantaneos, 54 documentos distintos**, janela
`20250714..20260831`. Seis semanas republicaram arquivo identico por sha256 e
nao contam como versao.

**MUDANCAS: 528 brutas, 36 reais.** Comparando so registros presentes nos dois
instantaneos e so campos, sem normalizar da 528 diferencas; normalizando campo
multivalorado da 32. As 496 de diferenca sao a fonte reordenando a lista de
indicacoes de perigo entre publicacoes. Com entrada e saida de produto, os 32
viram 36 eventos: 27 de validade, 4 produtos novos, 3 de estado, 2 de revoga.

> **Este numero mudou de 34 para 36 durante a V1, e a razao esta escrita.** A
> primeira versao aplicava a supressao de oscilacao (`N-03`) a **todos** os
> campos. Com isso ela apagava uma sequencia real de validade da POWERFILM
> (31/03/2026 -> 31/10/2041 -> 31/03/2026): tres leituras oficiais consecutivas,
> todas provadas, viraram zero evento porque a terceira voltava ao valor da
> primeira. Oscilacao so e ruido em **lista multivalorada**, onde a fonte
> reordena os proprios itens; numa data ela pode ser uma prorrogacao seguida de
> retificacao, que e fato. `N-03` foi restrita a campos multivalorados e os dois
> eventos voltaram. Se este documento ainda dissesse 34, ele estaria defendendo
> a versao errada da regra.

**PHI_PROVED = 0.** Por decisao, nao por ausencia. O extrator de carencia do
piloto esta marcado `PROTOTYPE_NOT_SHIPPED`: 2 de 15 rotulos, com a primeira
linha de cada bloco contaminada por coluna vizinha. Nenhum PHI e publicado.

    PHI_NOT_PROVED = 163
    NAO significa que as etichette nao tragam carencia. Significa que nao lemos.

## Reconciliacao com o que a ferramenta publica

Esta medicao **le a fonte e reexecuta os extratores**. A ferramenta publica o
que sobra **depois** da camada de inteligencia. Os dois numeros nao tem de ser
iguais; tem de ser explicados. A reconciliacao e calculada, nao digitada, em
`v1/BASELINE-RAW.json` -> `RECONCILIATION_WITH_PUBLISHED`:

| grandeza | medido aqui (cru) | publicado | delta | mecanismo |
|---|---|---|---|---|
| mudancas reais | 36 | 36 | **0** | mesmo differ, mesma normalizacao. Delta diferente de zero aqui seria **defeito**, nao decisao |
| linhas de dose distintas | 519 | 510 | **9** | filtro de plausibilidade `P-01`..`P-05` |
| rotulos com linha de dose | 23 | 21 | **2** | `P-01`: duas tabelas que o extrator achou onde nao havia (prosa lida como tabela) |

O delta de dose **e** o filtro. Se ele fosse zero, o filtro nao estaria rodando.
O delta de mudanca e zero, e tem de continuar zero.

## O que mudou em relacao ao que o piloto publicou

Nada material. Todos os numeros do piloto reproduziram. As unicas diferencas sao
de contagem de caracteres de texto (extrator diferente, ver acima) e a separacao
nova entre `DOSE_ROWS_PROVED`, `DOSE_NEEDS_REVIEW` e linha sem dose, que o piloto
publicava junta como 519.
