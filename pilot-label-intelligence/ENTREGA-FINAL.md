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
    TOTAL_DOSE_ROWS               = NOT_PRODUCED
    PRODUCTS_WITH_DOSE            = NOT_PRODUCED

    DEMO_PRODUCTS                 = 15
    DEMO_PRODUCTS_COMPLETE        = 15

    REGISTRY_VERSIONS_ARCHIVED    = 54
    REGISTRY_WINDOW               = 20250714..20260831
    REAL_REGISTRY_CHANGE_EVENTS   = 34
    SERIALIZATION_NOISE_SUPPRESSED= 496 de 528 diferencas de campo (93,9%)

    LABEL_VERSIONS_CHECKED        = 163
    LABEL_DOCUMENTS_CHANGED       = 0
    REAL_LABEL_DIFFS_FOUND        = 0
    CHECK_FAILED                  = 0

    ALERTS_GENERATED              = 70
    ALERTS_BY_TYPE                = {'REGULATORY_CHANGE': 25, 'EXPIRY_PASSED': 15, 'EXPIRY_APPROACHING': 26, 'NEW_LABEL': 4}
    MANUAL_REVIEW_REQUIRED        = 35  (divida de leitura, nao ausencia)

    EXPIRED_BUT_STILL_LISTED      = 15
    EXPIRING_30 / 90 / 180        = 3 / 26 / 64

    COMPETITOR_ROUTE              = SAME_ROUTE_PROVED (4 casos, 4 titulares)
    COMPETITOR_EXTENSION          = FEASIBLE_NOW (nao executada, por escopo)
    AUTOMATION_COVERAGE           = 7 de 9 passos da esteira rodam sozinhos

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
    HISTORICAL LABEL DIFF PROVED    = NAO — 0 rotulos mudaram na janela de 7 dias
    HISTORICAL REGISTRY DIFF PROVED = SIM — 34 eventos reais em 20250714..20260831

## Recomendacao de integracao com o portal

    PORTAL_INTEGRATION_RECOMMENDATION = NAO INTEGRAR AINDA

Tres razoes, nesta ordem:

1. O portal esta congelado por decisao D-007 e esta missao nao o toca.
2. O diff historico do proprio rotulo ainda nao tem caso real. Integrar agora
   levaria para a tela uma capacidade que a janela de observacao nao sustenta.
3. A dose ainda esta em `AUTOMATABLE_WITH_REVIEW`. Antes de virar tela, precisa
   de uma passada humana por amostra.

O que ja pode ir para conversa com o cliente e a demo shadow desta branch, que
existe exatamente para isso: mostrar sem integrar.
