# RECONCILIACAO — o que ja existia, antes de coletar qualquer coisa

A missao manda, como primeira lei:

    REUSE_PROVED_EXISTING_READING_BEFORE_NEW_COLLECTION = SIM

Este documento e o resultado dessa lei. Nenhum dos 163 rotulos foi recoletado por
reflexo. O que foi feito de novo esta na secao final, e so o que faltava.

## 1 · A CONTRADICAO DA MISSAO NAO EXISTE

A missao pede para explicar por que os artefatos discordam:

> 163/163 PDFs baixados, todos com texto extraivel
> versus
> apenas 19/163 com pelo menos uma linha cultura x alvo lida

**Eles nao discordam.** Os dois numeros sao publicados **no mesmo campo do mesmo
artefato**, com um aviso explicito contra confundi-los:

> `CRITICAL_COVERAGE_WARNING` em `adama-italy-products.json`:
> "o 100% conta ROTULO BAIXADO, nao USO LIDO. Sao numeros de coisas diferentes e
> o primeiro engana."

Sao duas camadas da mesma esteira, nao duas medicoes do mesmo fato:

| camada | numero | o que conta |
|---|---|---|
| `LABEL_DOWNLOADED` | 163/163 | o PDF chegou integro |
| `TEXT_EXTRACTED` | 163/163 | o PDF tem texto recuperavel |
| `USE_ROWS_STRUCTURED` | 19/163 na data daquele artefato | o parser conseguiu montar par cultura x alvo |

A pergunta `WHY_PREVIOUS_COUNTS_DIFFER` tem, portanto, tres respostas empilhadas —
e nenhuma delas e "alguem errou a conta".

**Primeira: camadas diferentes.** Baixar nao e ler. A propria casa ja escreve isso.

**Segunda: datas diferentes.** O 19/163 nao e o estado atual, e o estado de um
artefato mais antigo. A serie medida:

| data | produtos com par lido | pares |
|---|---|---|
| (artefato inicial) | 19/163 (11,7%) | 49 |
| 2026-09-02 | 102/163 (62,6%) | 2.030 |
| 2026-09-04 | **128/163 (78,5%)** | **2.928** |

O 19 e verdadeiro sobre o passado e falso sobre o presente.

**Terceira: refs diferentes.** A branch desta missao e **rasa** (`git clone` a
profundidade 50) e nao enxerga o acervo. O corpus italiano inteiro vive em
`sintonia/canonical @ bdb57cf`, que existe no remoto entre 54 refs mas nao estava
buscado aqui. Procurar "163 rotulos" no worktree devolve zero — o que nao prova
ausencia, prova clone raso. Uma leitura apressada dessa ausencia teria produzido
exatamente o erro que a missao proibe: chamar falha de instrumento de ausencia de
dado.

## 2 · CENSO — O QUE EXISTE, MEDIDO E NAO CITADO

Tudo abaixo foi conferido abrindo o artefato, nao lendo a afirmacao sobre ele.

    LABELS_DISCOVERED      = 163  — VERIFICADO na fonte oficial (secao 3)
    LABELS_DOWNLOADED      = 163  — VERIFICADO: 163 sha256 distintos em IT-ROTULOS-LEITURA-RUN
    TEXT_EXTRACTED         = 163  — VERIFICADO: TEXT_CHARS > 0 em 163/163, 2.793.649 chars no total
    FULL_LABELS_READ       = 163  — VERIFICADO: READ_STATUS = READ em 163/163
    PRODUCTS_WITH_USE_ROWS = 128  — VERIFICADO: registros distintos em IT-ROTULOS-PARES-V3 (2026-09-04)
    TOTAL_USE_ROWS         = 2928 — VERIFICADO: SUPPORTED_PAIRS == len(PAIRS) == 2928
    UNRESOLVED_PRODUCTS    = 35   — VERIFICADO: 163 - 128, e a lista esta publicada

Qualidade da leitura, medida contra gabarito manual de 30 rotulos (912 pares):

    PRECISION 0,965 · RECALL 0,870 · F1 0,915
    RECALL_INCLUDING_VOCAB_GAP 0,809

O gabarito e o instrumento que impede o numero bonito: 27 falsos positivos e 110
falsos negativos estao contados e publicados.

## 3 · DE ONDE VEM O 163 — RESOLVIDO NA FONTE

O numero 163 nao aparece em nenhum artefato desta branch. Ele foi **rederivado do
zero**, nesta sessao, direto do registro oficial italiano:

    PROD_FTS_6_20260831.csv — Ministero della Salute, dati.salute.gov.it
    sha256 13537cd10b9fa59a719317c1f8d353aaa074aa70566e63c6e1f11d6d6b067859

    17.695 produtos no registro
       602 linhas cujo titular contem ADAMA
       439 com stato_amministrativo Revocato ou Scaduto
    -------
       163 produtos ADAMA ATIVOS   <-- exatamente o universo da missao

Por entidade: ADAMA ITALIA S.R.L. 85 · ADAMA AGAN LTD 35 ·
ADAMA MAKHTESHIM LTD 26 · ADAMA DEUTSCHLAND GMBH 17.

O 163 e, portanto, real e verificavel na fonte — so nao era um numero de rotulos
lidos. E o tamanho do universo.

## 4 · O QUE FOI REPRODUZIDO DE FORMA INDEPENDENTE

Antes de reusar, a rota inteira foi refeita do zero nesta sessao, sem consultar o
codigo da casa, e chegou ao mesmo lugar byte a byte:

| passo | resultado |
|---|---|
| descoberta da rota oficial da etichetta | `EtichettaServlet?id=N`, a mesma URL do acervo |
| PDF do registro 015275 (DURAVIS) | sha256 `c4d8c380...cbec` — **identico** ao capturado em 2026-08-30 |
| geometria via `pdftotext -bbox-layout` | **byte a byte identica** a `geometria/015275.xml.gz` do acervo |

Isso prova duas coisas que o piloto precisa afirmar: a esteira e **reprodutivel**,
e o `sha256` do PDF **serve como identidade de versao**, porque o mesmo documento
baixado por duas partes em datas diferentes da o mesmo hash.

## 5 · O QUE NAO EXISTIA — E VIROU O TRABALHO DESTA MISSAO

Tres buracos, confirmados por varredura em todas as refs alcancaveis:

**a) Dose.** Nenhum script da casa extrai dose, unidade, intervalo ou numero
maximo de aplicacoes. A uniao de todas as chaves dos 2.928 pares publicados nao
contem nenhum campo de dose. O tempo de carencia esta em `SECAO_PROIBIDA` do
parser, isto e, deliberadamente fora. Cultura x alvo esta resolvido; **dose e
trabalho novo**.

**b) Historico de versao do registro.** A propria regua da casa
(`docs/regras/REGUA-DE-CHANGE-EVENT-EAME.md`) classifica `STATUS_CHANGE`,
`HOLDER_CHANGE` e `DATE_CHANGE` como *"POSSIVEL, nao provado — falta uma segunda
versao arquivada do export"*. Faltava o arquivo. Ele existe, e esta descrito em
`registry/ACHADO-ARQUIVO-OFICIAL.md`.

**c) Verificacao de versao do rotulo.** O acervo tem o hash de cada um dos 163
rotulos, mas ninguem havia voltado a fonte para perguntar se o documento ainda e
o mesmo. Esse e o passo `DETECT` da esteira, e ele nunca tinha rodado.
