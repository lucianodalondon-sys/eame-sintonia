#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DIARIO DAS BUSCAS DESTA MISSAO — com RODADA, para se poder ler saturacao.

SATURACAO NAO E' AUSENCIA
-------------------------
`SATURATION_SIGNAL = YES` quer dizer que ESTA busca, com ESTAS palavras, parou
de devolver fonte forte nova. Nao quer dizer que a fonte nao exista. A missao
1 aprendeu isto na pele: seis regioes ficaram com zero fonte A depois do grafo
de ligacoes, e uma rodada dirigida devolveu ~25 hosts novos, tres deles de
classe A. Zero depois de uma rodada e' sinal de rodada, nao de territorio.
"""

BUSCAS2 = [
 dict(GAP="CROP · trigo e trigo duro (3+3 janelas, zero fonte)",
      CONSULTA="bollettino fitosanitario frumento grano tenero duro fenologia "
               "BBCH difesa integrata regione servizio fitosanitario",
      RODADA="ROUND_1",
      DEVOLVEU="Veneto (seminativi, serie 2026 desde N°01 de 18/02), "
               "Emilia-Romagna (6 boletins interprovinciais, com derroga "
               "datada para Septoria), ERSA FVG (tabela Baggiolini↔BBCH), "
               "Campania (UTM, semanal 1/3–30/9), Fondazione Edmund Mach",
      FONTES="Bollettini seminativi Veneto · Bollettini interprovinciali ER · "
             "ERSA FVG · Bollettini UTM Campania",
      SATURACAO="NO — primeira rodada e ja devolveu 4 fontes fortes",
      VIROU="a derroga regional para Septoria em trigo tem DATA DE INICIO DE "
            "USO (20/03/2026) — e isso e' ALTERACAO DE AUTORIZACAO, outro "
            "gap critico, fechado de lado"),
 dict(GAP="CROP · milho (3 janelas, zero fonte)",
      CONSULTA="bollettino tecnico mais granoturco fenologia diabrotica "
               "piralide monitoraggio regione produzione integrata",
      RODADA="ROUND_1",
      DEVOLVEU="ERSA FVG com «Boll_09_MAIS_03072026.pdf» e o milho declarado "
               "em BBCH 42-70 conforme epoca de semeadura; ERSAF Lombardia "
               "com boletim semanal feito com o Condifesa Lombardia Nord-Est; "
               "Veneto Agricoltura com resultado de ensaio plurianual",
      FONTES="ERSA FVG (mais) · Bollettino Mais ERSAF · Bollettino Colture "
             "Erbacee Veneto Agricoltura",
      SATURACAO="NO",
      VIROU="⚠️ O ACHADO QUE NAO ESPERAVA: a Veneto Agricoltura publica "
            "RESULTADO MEDIDO DE ENSAIO, incluindo o numero desfavoravel — o "
            "tratamento no momento de maxima eficacia melhorou produtividade "
            "e micotoxinas em MENOS DE 50% dos casos. Era o gap que as provas "
            "GEP nao podiam fechar por serem reservadas"),
 dict(GAP="CROP · tomate (3 janelas, zero fonte)",
      CONSULTA="bollettino pomodoro da industria fenologia peronospora "
               "monitoraggio disciplinare produzione integrata",
      RODADA="ROUND_1",
      DEVOLVEU="Consorzi Fitosanitari Provinciali (RE, MO, PR, PC) com boletim "
               "semanal construido com modelo I.P.I., levantamentos "
               "aerobiologicos e CAMPOS-ESPIA NAO TRATADOS; curva de "
               "suscetibilidade por fase; derroga de 25/02/2026 para "
               "fluazaindolizine contra Meloidogyne, uso de 1/3 a 28/6/2026",
      FONTES="Bollettini di produzione integrata — pomodoro (4 consorzi)",
      SATURACAO="NO",
      VIROU="«campo-espia nao tratado» e' observacao de campo no sentido "
            "forte: uma parcela deixada sem tratamento para se ver a doenca "
            "acontecer. Nao e' modelo — e' medicao"),
 dict(GAP="CROP · soja (2 janelas, zero fonte)",
      CONSULTA="bollettino soia fenologia difesa integrata ragnetto rosso "
               "seminativi regione monitoraggio",
      RODADA="ROUND_1",
      DEVOLVEU="ERSA FVG com «Bollettino difesa integrata soia n. 2 del 16 "
               "febbraio 2026»; AIAB FVG com «Bollettino seminativi biologici "
               "n. 8/2026 del 24 giugno 2026», feito com rilievi in campo e "
               "aziende campione em colaboracao com a ERSA",
      FONTES="ERSA FVG (soia) · AIAB FVG (seminativi biologici)",
      SATURACAO="NO",
      VIROU="⚠️ E UMA CORRECAO AO QUE EU ESCREVI: o Bollettino Nazionale di "
            "Fenologia da RRN, que eu apresentei como fonte de fenologia «por "
            "cultura», monitoriza PRINCIPALMENTE VITE, OLIVO E ROBINIA. Nao "
            "serve soja, nem milho, nem trigo. Continua forte — para tres "
            "culturas, nao para dez"),
 dict(GAP="REGIAO · Basilicata (zero fonte regional)",
      CONSULTA="Basilicata ALSIA bollettino agrometeorologico fitosanitario "
               "fenologia servizio fitosanitario regionale",
      RODADA="ROUND_1",
      DEVOLVEU="ALSIA / SAL: 40 estacoes desde 1996 com molha foliar e "
               "evapotranspiracao por Blaney-Criddle e Penman-Monteith; "
               "boletins do SeDI por comprensorio (Metapontino, Alta Valle "
               "d'Agri, Valle del Bradano); relatorio climatico mensal com "
               "anomalia face a 1991-2020; Emanuele Scalcione responsavel",
      FONTES="SAL/SeDI da ALSIA",
      SATURACAO="NO — uma rodada resolveu a regiao",
      VIROU="a regiao que estava a ZERO tinha, desde 1996, uma rede de 40 "
            "estacoes. Zero na matriz nao era ausencia de fonte: era ausencia "
            "de busca dirigida — exatamente o que a missao 1 tinha registado "
            "como regra e que eu nao apliquei a tempo"),
 dict(GAP="REGIAO · Valle d'Aosta (zero fonte regional)",
      CONSULTA="Valle d'Aosta Institut Agricole Régional bollettino viticolo "
               "fitosanitario assistenza tecnica",
      RODADA="ROUND_1",
      DEVOLVEU="Ufficio servizi fitosanitari da Regione autonoma: avisos para "
               "viticultores (atualizado 26/06/2026) e para fruticultores, "
               "rede de armadilhas por estacao, distribuicao por aviso "
               "afixado, gravador telefonico, web e SMS; Institut Agricole "
               "Régional com dados de maturacao da uva das vinhas mais "
               "representativas",
      FONTES="Avvisi fitosanitari VdA · Dati di maturazione do IAR",
      SATURACAO="NO",
      VIROU="parte do servico distribui-se por SMS e gravador telefonico — "
            "canais que NAO sao coletaveis por rota web. A fonte existe e "
            "publica; parte do que publica esta fora do alcance de qualquer "
            "coletor"),
 dict(GAP="VALIDACAO · as 37 rotas nunca abertas",
      CONSULTA="(nao foi busca: foi sonda HTTP com UA de navegador sobre as "
               "37 rotas, mais controles positivos e negativos)",
      RODADA="ROUND_1",
      DEVOLVEU="9 VALIDATED_STRONG · 6 USEFUL · 15 BUT_SECONDARY · 3 BLOCKED · "
               "2 UNKNOWN · 1 BROKEN · 1 WRONG_SOURCE. 8 redirecionaram.",
      FONTES="(validacao, nao descoberta)",
      SATURACAO="N/A",
      VIROU="⚠️ QUATRO DEFEITOS DA MINHA PROPRIA SONDA, apanhados por olhar o "
            "resultado em vez de o publicar: (1) `getaddrinfo failed` local "
            "tratado como fonte morta — tres fontes vivas salvas; (2) filtro "
            "de assunto so' em italiano, que reprovou a base europeia em "
            "ingles; (3) app de JavaScript confundida com pagina morta; "
            "(4) pagina de redirecionamento chamada de quebrada"),
]
