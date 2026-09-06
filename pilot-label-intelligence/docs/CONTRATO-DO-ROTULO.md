# CONTRATO DO ROTULO — modelo canonico do piloto

Este e o contrato de dados do piloto de Label Intelligence. Ele nao substitui e nao toca
nenhum contrato do P0.2, do Passaporte ou do Universal. Vale so dentro de
`pilot-label-intelligence/`.

## 1. As cinco camadas que nunca sao sinonimo

A confusao entre elas e a origem de toda contagem inflada. O piloto separa por construcao:

| estado | significa | prova exigida |
|---|---|---|
| `LABEL_DISCOVERED` | sabemos que existe um rotulo oficial para este registro | URL da ficha oficial + HTTP status |
| `LABEL_DOWNLOADED` | o PDF esta no disco, integro | caminho + sha256 + bytes + captured_at |
| `TEXT_EXTRACTED` | o PDF tem texto recuperavel | caminho do texto + n de caracteres |
| `LABEL_READ` | um humano ou parser percorreu o documento e sabe o que ele diz | secao de usos localizada, com pagina |
| `USE_ROWS_STRUCTURED` | existe pelo menos uma linha cultura x alvo com citacao | >= 1 linha com SOURCE_QUOTE |

Um produto pode estar em `LABEL_DOWNLOADED` e `TEXT_EXTRACTED` e ainda assim ter
`USE_ROWS_STRUCTURED = 0`. Isso nao e defeito de dado: e defeito de leitura, e o piloto
e obrigado a mostrar os dois numeros lado a lado.

## 2. Leis de proveniencia

    LABEL_DOWNLOADED      != LABEL_STRUCTURED
    TEXT_FOUND            != AUTHORIZED_USE_PROVED
    REGISTRATION_ID_SAME  != DOCUMENT_SAME
    CAPTURED_AT           != EFFECTIVE_AT
    EXPIRY                != WITHDRAWAL
    CATALOG_PRESENCE      != MARKET_PRESENCE
    PARSER_FAILURE        != REGULATORY_ABSENCE

A ultima e a mais cara de violar. Quando o parser nao acha a tabela de usos, o campo correto
e `PARSE_STATE = FAILED`, nunca "produto sem usos autorizados".

## 3. Ausencia tem tres nomes

Nao existe campo vazio no piloto. Existe:

- `NOT_PRESENT` — o rotulo oficial nao traz esse campo;
- `NOT_PRESERVED` — o rotulo traz, mas nossa captura nao guardou;
- `NOT_KNOWN` — ainda nao olhamos.

## 4. Registro do produto

    PRODUCT, REGISTRATION_ID, HOLDER, STATUS,
    ACTIVE_INGREDIENTS, FORMULATION, REGULATORY_CATEGORY

## 5. Documento do rotulo

    LABEL_SOURCE, LABEL_DOCUMENT_ID, LABEL_SHA256,
    LABEL_CAPTURED_AT, LABEL_EFFECTIVE_AT, LABEL_VERSION_ID

`LABEL_VERSION_ID` e derivado do sha256 do PDF, nunca da data de captura. Duas capturas do
mesmo arquivo sao **uma** versao.

## 5b. Celula mesclada: herdar e LER, nao inventar

A primeira versao deste contrato dizia que **so cultura** podia ser herdada de
uma linha anterior. A regra nasceu certa — impedir que uma dose vazasse para uma
linha que nao a tem — mas estava larga demais, e a medicao mostrou onde.

Na tabela de usos da etichetta, a celula de **numero maximo de aplicacoes** e
mesclada verticalmente exatamente como a de cultura: no registro 015275 um unico
"1", impresso na altura da terceira das cinco linhas do Pesco, vale para as
cinco. O gabarito construido a mao, lendo os fios da tabela na imagem
renderizada, espalha esse valor pelas cinco linhas — porque e isso que a tabela
diz.

Com a regra antiga, quatro dessas cinco linhas sairiam `NOT_PRESENT`. Isso nao e
prudencia: e afirmar ausencia onde o documento afirma presenca. Medido, a regra
antiga entregava `MAX_APPLICATIONS` correto em 47 de 84 linhas; respeitando a
mescla, 83 de 84.

A regra passa a ser:

> Um valor pode ser herdado de outra linha **quando a mescla da celula for
> estabelecida pela geometria do documento**, nunca por conveniencia do leitor.
> Toda linha que recebe valor herdado marca o campo correspondente:
> `CROP_INHERITED`, `MAX_APPLICATIONS_INHERITED`, e assim por diante.

O que continua proibido, e e o coracao da regra original:

- herdar valor porque a linha ficou vazia e o numero anterior "parece servir";
- herdar dose de uma linha para outra sem mescla geometrica provada;
- apagar a marca de herdado para a tabela ficar mais limpa.

Ler uma celula mesclada e leitura. Preencher uma celula vazia e invencao. A
diferenca esta na geometria, e ela e verificavel.

## 6. Linha de uso autorizado

    CROP, TARGET, TARGET_SCIENTIFIC_NAME,
    DOSE, DOSE_UNIT, APPLICATION_INTERVAL, MAX_APPLICATIONS, PHI,
    APPLICATION_STAGE, BBCH, RESTRICTIONS, NOTES,
    SOURCE_QUOTE, SOURCE_PAGE

`SOURCE_QUOTE` e obrigatorio. Uma linha de uso sem citacao recuperavel no documento oficial
nao entra no piloto — ela vira `PARSE_STATE = UNVERIFIED` e fica fora das contagens.

## 7. Identidade de versao

Comparar por, nesta ordem:

1. `sha256` do PDF — identidade forte;
2. identificador do documento na fonte oficial;
3. data efetiva **quando publicada pela fonte** (nunca inferida);
4. numero de registro;
5. conteudo textual normalizado.

Se so existir uma captura: `VERSION_HISTORY = NO_PREVIOUS_VERSION_PROVED`. Nao se fabrica diff.

## 8. Evento de mudanca

    LABEL_CHANGE_EVENT {
      PRODUCT, OLD_VERSION, NEW_VERSION, CHANGE_DATE,
      CHANGE_TYPE, BEFORE, AFTER, SOURCE
    }

`CHANGE_TYPE` ∈ CROP_ADDED, CROP_REMOVED, TARGET_ADDED, TARGET_REMOVED, DOSE_CHANGED,
PHI_CHANGED, MAX_APPLICATIONS_CHANGED, RESTRICTION_CHANGED, ACTIVE_INGREDIENT_CHANGED,
STATUS_CHANGED, EXPIRY_CHANGED, TEXT_CHANGE_OTHER.

Mudanca de texto sem significado regulatorio provado e `TEXT_CHANGE_OTHER` e **nao** sobe
para impacto de negocio automaticamente.

## 9. Alerta

    ALERT { WHAT_CHANGED, WHEN, SOURCE, OLD, NEW, CONFIDENCE }

Sem mudanca, sem alerta. Um alerta sem `OLD` e `NEW` recuperaveis nao e alerta, e ruido.
