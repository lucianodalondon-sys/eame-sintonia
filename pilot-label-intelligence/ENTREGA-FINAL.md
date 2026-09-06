# ENTREGA FINAL — LABEL INTELLIGENCE PILOT · ITALIA

Gerado de artefatos por `bin/relatorio.py`. Nenhum numero aqui foi digitado a mao.

    LABEL_INTELLIGENCE_PILOT_STATE = ENTREGUE

## O que ja existia, o que foi reusado, o que e novo

    WHAT_ALREADY_EXISTED =
      universo de 163 produtos ADAMA ativos no registro oficial italiano
      163 rotulos oficiais lidos, com texto extraido e geometria versionada
      2,928 pares cultura x alvo, parser it_rotulo_parser/3.4.0
      precisao 0,965 e recall 0,870 medidos contra gabarito manual de 30 rotulos
      tudo em sintonia/canonical @ bdb57cf — NAO tocado por esta missao

    WHAT_WAS_REUSED =
      a leitura cultura x alvo inteira, apontada por commit e caminho
      a geometria versionada dos 163 rotulos
      scripts/pdf_text.py, o extrator sem dependencia da propria casa
      o sistema de selos REAL / DERIVED / DEMO / CONCEPT do portal congelado

    WHAT_WAS_NEWLY_COLLECTED =
      60 instantaneos semanais do registro oficial (54 documentos distintos)
      os 163 PDFs de rotulo, que nao existiam mais em nenhuma ref
      4 rotulos de concorrentes, como medicao de extensibilidade

## Metricas

    TOTAL_ADAMA_PRODUCTS          = 163
    LABELS_DISCOVERED             = 163
    LABELS_DOWNLOADED             = 163
    TEXT_EXTRACTED                = 163   (reuso, conferido item a item)
    LABELS_DEEPLY_STRUCTURED      = 128
    TOTAL_AUTHORIZED_USE_ROWS     = 2,928
    TOTAL_DOSE_ROWS               = 519
    PRODUCTS_WITH_DOSE            = 23

    DEMO_PRODUCTS                 = 15
    DEMO_PRODUCTS_COMPLETE        = 15

    REGISTRY_VERSIONS_ARCHIVED    = 54
    REGISTRY_WINDOW               = 20250714..20260831
    REAL_REGISTRY_CHANGE_EVENTS   = 34
    SERIALIZATION_NOISE_SUPPRESSED= 496 de 528 diferencas de campo (93.9%)

    LABEL_VERSIONS_CHECKED        = 163
    LABEL_DOCUMENTS_CHANGED       = 0
    REAL_LABEL_DIFFS_FOUND        = 0
    CHECK_FAILED                  = 0
    OBSERVATION_WINDOW_DAYS       = 2
    LABEL_RENEWAL_RATE_PER_YEAR   = 0.317   (32% dos rotulos por ano)
    EXPECTED_CHANGES_IN_WINDOW    = 0.28
    MEDIAN_AGE_OF_LABEL_IN_FORCE  = 2.1 anos

    ALERTS_GENERATED              = 70
    ALERTS_BY_TYPE                = {'REGULATORY_CHANGE': 25, 'EXPIRY_PASSED': 15, 'EXPIRY_APPROACHING': 26, 'NEW_LABEL': 4}
    MANUAL_REVIEW_REQUIRED        = 35  (divida de leitura, nao ausencia)

    EXPIRED_BUT_STILL_LISTED      = 15
    EXPIRING_30 / 90 / 180        = 3 / 26 / 64

    COMPETITOR_ROUTE              = SAME_ROUTE_PROVED (4 casos, 4 titulares)
    COMPETITOR_EXTENSION          = FEASIBLE_NOW (nao executada, por escopo)
    AUTOMATION_COVERAGE           = das 14 tarefas classificadas em docs/ROI-SUBSTITUICAO.md,
                                    7 rodam sozinhas, 3 rodam com revisao,
                                    2 continuam humanas, 2 nao estao provadas

## Substituicao do trabalho manual

    FULLY_AUTOMATABLE       = localizar, baixar, preservar, detectar mudanca de
                              versao, extrair texto, acompanhar validade,
                              detectar mudanca no registro, montar fila de revisao
    AUTOMATABLE_WITH_REVIEW = estruturar cultura x alvo (P 0,965 / R 0,870),
                              estruturar dose, classificar tipo de mudanca
    HUMAN_REQUIRED          = decidir impacto comercial, interpretacao regulatoria
    NOT_PROVED              = rotulo fisico / foto de embalagem,
                              diff historico do proprio rotulo

Detalhe em `docs/ROI-SUBSTITUICAO.md`. Nenhum valor em dinheiro foi estimado.

## Variantes do problema do cliente que ficam cobertas

    A. localizar e baixar PDFs oficiais            COBERTA — provada no universo inteiro
    B. manter a versao vigente atualizada          COBERTA — 163/163 conferidos por hash
    C. transformar rotulo em dado estruturado      COBERTA — 2,928 pares; dose em curso
    D. comparar mudancas de versao                 COBERTA no REGISTRO (34 eventos reais);
                                                   no ROTULO a maquinaria roda, mas em 7 dias nao houve mudanca
    E. acompanhar concorrentes                     MEDIDA — mesma rota, 4 casos provados
    F. fotos / rotulo fisico                       FORA — nao tentada, nao prometida

## Portao para segunda

    LABEL_PILOT_READY_FOR_MONDAY = SIM

      fonte oficial ....................... SIM
      produto reconhecivel ................ SIM
      rotulo real ......................... SIM
      estrutura real ...................... SIM
      evidencia clicavel .................. SIM
      estado de leitura honesto ........... SIM
      busca funcional ..................... SIM
      nenhuma ausencia inventada .......... SIM
      demo visual independente ............ SIM

    VERSION MONITORING READY        = SIM
    HISTORICAL LABEL DIFF PROVED    = NAO — 0 mudaram em 2 dias,
                                      e o esperado pela taxa medida era 0.28
    HISTORICAL REGISTRY DIFF PROVED = SIM — 34 eventos reais em 20250714..20260831

## Recomendacao de integracao com o portal

    PORTAL_INTEGRATION_RECOMMENDATION = NAO INTEGRAR AINDA

Tres razoes, nesta ordem:

1. O portal esta congelado por decisao D-007 e esta missao nao o toca.
2. O diff historico do proprio rotulo ainda nao tem caso real. A taxa medida diz
   que 32% dos rotulos sao renovados por ano — ou seja, o caso vai
   aparecer sozinho em semanas, e ai a capacidade se prova com documento na mao
   em vez de com promessa.
3. A dose ainda esta em `AUTOMATABLE_WITH_REVIEW`. Antes de virar tela, precisa
   de uma passada humana por amostra.

O que ja pode ir para conversa com o cliente e a demo shadow desta branch, que
existe exatamente para isso: mostrar sem integrar.

## O pacote

    PACKAGE_PATH  = pilot-label-intelligence/
    PACKAGE_FILES = 44 arquivos versionados
    PACKAGE_HASH  = bac676dba29bd68c94e1a39e1752019a0d9d08e357a2e9cf18f050fe1b105a22

O hash e o sha256 sobre o caminho e o conteudo de cada arquivo versionado do
piloto, em ordem, exceto este relatorio. Nao cobre os instantaneos do registro
nem os PDFs dos rotulos, que o git ignora de proposito: sao 280 MB e 33 MB
rebaixaveis da fonte oficial, e cada um ja tem o proprio sha256 publicado em
`registry/IT-REGISTRO-VERSOES.json` e `labels/IT-ROTULOS-REVERIFICACAO.json`.

Para conferir:

```bash
python3 pilot-label-intelligence/bin/auditar.py     # 18 checagens, recontadas da fonte
python3 pilot-label-intelligence/bin/relatorio.py   # regera este arquivo e o hash
```

## Ao terminar, para

Nao integrar em nenhum outro sistema.
