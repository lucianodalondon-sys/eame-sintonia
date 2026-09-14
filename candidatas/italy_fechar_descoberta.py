#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DESCOBERTA DIRIGIDA — as 5 culturas que faltavam e as 2 regioes zeradas.

A missao anterior declarou, ela mesma, o que nao tinha feito: trigo, trigo
duro, milho, soja e tomate nao foram pesquisados — e sao 14 das 29 janelas
canonicas, quase metade. E duas regioes ficaram sem nenhuma fonte regional:
Basilicata e Valle d'Aosta. Isto fecha as duas dividas.

A PALAVRA «MAIS» E' UMA MINA, E JA EXPLODIU UMA VEZ
---------------------------------------------------
Milho em italiano escreve-se «mais». Na missao anterior isso produziu seis
falsos positivos porque as minhas descricoes estao em portugues («vai mais
longe», «mais ~300 leituras»). Aqui a busca foi feita com «mais granoturco»
e as fontes sao confirmadas pelo CONTEUDO (diabrotica, piralide, BBCH do
milho), nunca pela palavra sozinha.

E UMA CORRECAO AO QUE EU MESMO ESCREVI
--------------------------------------
Eu apresentei o Bollettino Nazionale di Fenologia da RRN como fonte de
fenologia «por cultura». A busca desta missao mediu o limite: as culturas
monitorizadas sao PRINCIPALMENTE VITE, OLIVO E ROBINIA. Nao serve soja, nem
milho, nem trigo. A fonte e' boa e continua VALIDATED_STRONG — mas para tres
culturas, nao para dez.
"""

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "candidatas"))
import _territorios as _T          # noqa: E402

B = "busca dirigida ao gap, 2026-09-14 (segunda vaga)"

# ═════════════════════════════════════════════════════════════════════════════
# AS 5 CULTURAS — trigo, trigo duro, milho, soja, tomate
# ═════════════════════════════════════════════════════════════════════════════
CULTURAS = [
 dict(
  NOME="Bollettini colture estensive / seminativi",
  DONO="Regione del Veneto — U.O. Fitosanitario, com a Veneto Agricoltura",
  URL="https://www.regione.veneto.it/web/fitosanitario/bollettini-seminativi",
  PRODUZ="boletim SEMANAL para seminativos (trigo, milho, soja), redigido em "
         "cumprimento do Piano di Azione Nazionale, a partir de modelos "
         "previsionais E de redes de monitorizacao",
  EXEMPLO_REAL="serie 2026 das colture erbacee comeca no N°01 de 18/02/2026, "
               "com cadencia semanal declarada",
  CULTURAS_QUE_NOMEIA=["Wheat", "Durum Wheat", "Maize", "Soybean"],
  ALIMENTA=["WINDOWS · FASE FENOLOGICA DA CULTURA (o que a planta esta a fazer)",
            "WINDOWS · FASE DO PROBLEMA (em que estadio esta a praga/doenca)",
            "WINDOWS · Datas de inicio e fim da janela",
            "WINDOWS · Janela de monitorizacao (quando ir olhar)"],
  AMBITO="Veneto", TERR=["T1", "T3"],
  RECORRENCIA="HIGH — semanal, numerada e datada",
  CLASSE="A", PRIMARIA="PRIMARY",
  GAP_FECHA="CRITICAL — fenologia das arvenses, que nenhuma das 37 cobria",
  EVIDENCIA=f"{B}: numero e data da primeira edicao de 2026 lidos na propria "
            "serie; a colaboracao com a Veneto Agricoltura esta declarada",
  LIMITE="regional. E a serie e' de campanha: comeca em fevereiro."),
 dict(
  NOME="Bollettini interprovinciali di produzione integrata e biologica",
  DONO="Regione Emilia-Romagna — Settore Fitosanitario, com os Consorzi "
       "Fitosanitari Provinciali",
  URL="https://agricoltura.regione.emilia-romagna.it/fitosanitario/difesa-sostenibile/bollettini",
  PRODUZ="SEIS boletins territoriais, redigidos a partir dos Disciplinari "
         "regionais, de modelos previsionais e dos levantamentos de "
         "monitorizacao; publicam tambem as DEROGAS de uso excecional",
  EXEMPLO_REAL="«Bollettino 17 del 04 giugno 2026 — Reggio Emilia» e "
               "«Bollettino 15 del 20 maggio 2026 — Bologna e Ferrara». E uma "
               "derroga datada: contencao de Septoria tritici e S. nodorum em "
               "trigo, uso permitido a partir de 20/03/2026",
  CULTURAS_QUE_NOMEIA=["Wheat", "Durum Wheat", "Maize", "Soybean", "Tomato"],
  ALIMENTA=["WINDOWS · FASE FENOLOGICA DA CULTURA (o que a planta esta a fazer)",
            "WINDOWS · FASE DO PROBLEMA (em que estadio esta a praga/doenca)",
            "WINDOWS · ATO REGULATORIO regional que abre/fecha a janela",
            "WINDOWS · Janela de controlo de infestantes",
            "PORTFOLIO · AUTORIZACAO EXCECIONAL (art. 53)",
            "PORTFOLIO · ALTERACAO de autorizacao (o que mudou e quando)"],
  AMBITO="Emilia-Romagna, em 6 areas interprovinciais", TERR=["T1", "T3", "T4"],
  RECORRENCIA="HIGH — semanal, numerada e datada",
  CLASSE="A", PRIMARIA="PRIMARY",
  GAP_FECHA="CRITICAL — fecha fenologia de arvenses E tomate, e traz a "
            "ALTERACAO DE AUTORIZACAO com data, que e' outro gap critico",
  EVIDENCIA=f"{B}: dois boletins numerados e datados de 2026 e uma derroga "
            "com data de inicio de uso, todos lidos na propria serie",
  LIMITE="a derroga e' REGIONAL: vale na Emilia-Romagna, nao em Italia. "
         "Confundir as duas transforma uma excecao local em regra nacional."),
 dict(
  NOME="Bollettini di difesa integrata — colture erbacee (mais e soia)",
  DONO="ERSA — Agenzia regionale per lo sviluppo rurale del Friuli Venezia Giulia",
  URL="http://difesafitosanitaria.ersa.fvg.it/difesa-e-produzione-integrata/difesa-integrata-obbligatoria/bollettini-fitosanitari/colture-erbacee-orticole/bollettini-2026",
  PRODUZ="boletins SEPARADOS por cultura para milho e soja, segundo as Norme "
         "tecniche do Disciplinare di Produzione Integrata regional; publica "
         "tambem a tabela de correspondencia Baggiolini ↔ BBCH",
  EXEMPLO_REAL="«Boll_09_MAIS_03072026.pdf» diz o milho em levata–enchimento "
               "de cariopses conforme epoca de semeadura e classe varietal, "
               "na escala BBCH 42-70. E «Bollettino difesa integrata soia n. 2 "
               "del 16 febbraio 2026»",
  CULTURAS_QUE_NOMEIA=["Maize", "Soybean", "Wheat"],
  ALIMENTA=["WINDOWS · FASE FENOLOGICA DA CULTURA (o que a planta esta a fazer)",
            "WINDOWS · FASE DO PROBLEMA (em que estadio esta a praga/doenca)",
            "WINDOWS · OBSERVACAO DE CAMPO (fase observada, nao esperada)",
            "WINDOWS · Datas de inicio e fim da janela"],
  AMBITO="Friuli-Venezia Giulia", TERR=["T1", "T3"],
  RECORRENCIA="HIGH — numerada por cultura e datada",
  CLASSE="A", PRIMARIA="PRIMARY",
  GAP_FECHA="CRITICAL — e' a UNICA fonte achada que publica BBCH DE MILHO com "
            "intervalo numerico (42-70) e boletim proprio de SOJA. Fecha "
            "tambem uma regiao FRACA",
  EVIDENCIA=f"{B}: dois ficheiros nomeados com cultura e data no proprio nome, "
            "e o intervalo BBCH citado no corpo",
  LIMITE="⚠️ A tabela Baggiolini↔BBCH publicada refere-se a FRUTEIRAS. Usa-la "
         "para cereais e' extrapolacao, e extrapolacao nao e' medicao."),
 dict(
  NOME="Bollettino Mais",
  DONO="ERSAF Lombardia, com o servico tecnico do Condifesa Lombardia Nord-Est",
  URL="https://www.fitosanitario.regione.lombardia.it/wps/portal/site/sfr",
  PRODUZ="boletim SEMANAL de milho com meteorologia da semana, sintese dos "
         "produtos admitidos, DESENVOLVIMENTO FENOLOGICO da cultura (floracao "
         "e fecundacao) e monitorizacao de diabrotica e piralide com indicacao "
         "de tratamento",
  EXEMPLO_REAL="nota tecnica «Difesa del mais da piralide e diabrotica e "
               "tutela delle api» publicada pelo Servizio Fitosanitario "
               "regionale; o boletim e' descrito como semanal e feito com o "
               "Condifesa Lombardia Nord-Est",
  CULTURAS_QUE_NOMEIA=["Maize"],
  ALIMENTA=["WINDOWS · FASE FENOLOGICA DA CULTURA (o que a planta esta a fazer)",
            "WINDOWS · FASE DO PROBLEMA (em que estadio esta a praga/doenca)",
            "WINDOWS · Janela de monitorizacao (quando ir olhar)",
            "WINDOWS · Produto registado ligado a janela"],
  AMBITO="Lombardia", TERR=["T1", "T3"],
  RECORRENCIA="HIGH — semanal",
  CLASSE="A", PRIMARIA="PRIMARY",
  GAP_FECHA="HIGH — junta fase da cultura com fase da praga E produto admitido "
            "na mesma pagina, que sao tres necessidades diferentes",
  EVIDENCIA=f"{B}: composicao do boletim descrita pelo proprio servico, com o "
            "parceiro tecnico nomeado",
  LIMITE="uma cultura, uma regiao."),
 dict(
  NOME="Bollettino Colture Erbacee",
  DONO="Veneto Agricoltura",
  URL="https://www.venetoagricoltura.org/",
  PRODUZ="boletim de arvenses com aprofundamento de difesa integrada, "
         "incluindo o RESULTADO MEDIDO de ensaios plurianuais",
  EXEMPLO_REAL="«Bollettino Colture Erbacee n°36/2024 del 20.6.24 — DIFESA "
               "INTEGRATA DALLA PIRALIDE». E o achado medido: de ensaios "
               "plurianuais em milho de grao, o tratamento feito no momento de "
               "maxima eficacia melhorou produtividade e micotoxinas em MENOS "
               "DE 50% dos casos; as populacoes mais altas concentram-se "
               "sempre no sudoeste da regiao — Rovigo, Padova e Venezia",
  CULTURAS_QUE_NOMEIA=["Maize", "Soybean", "Wheat"],
  ALIMENTA=["SCIENCE · METODO e RESULTADO medido (eficacia)",
            "SCIENCE · ENSAIO DE CAMPO / trial com resultado",
            "WINDOWS · FASE DO PROBLEMA (em que estadio esta a praga/doenca)",
            "WINDOWS · Desvio fenologico por regiao (a mesma cultura adianta/atrasa)"],
  AMBITO="Veneto, com detalhe sub-regional (provincias)", TERR=["T1", "T3", "T5"],
  RECORRENCIA="HIGH — numerada e datada na campanha",
  CLASSE="A", PRIMARIA="PRIMARY",
  GAP_FECHA="HIGH — e' o achado que mais me surpreendeu: RESULTADO DE ENSAIO "
            "DIVULGADO, com o numero desfavoravel incluido («menos de 50% dos "
            "casos»). Era o gap que as provas GEP nao podem fechar por serem "
            "reservadas. Nao substitui o ensaio de registo, mas e' resultado "
            "medido e publico",
  EVIDENCIA=f"{B}: numero, data e conclusao quantificada lidos no boletim",
  LIMITE="uma cultura e uma regiao por edicao. E o resultado e' de ensaio "
         "DEMONSTRATIVO, nao de registo — sao coisas diferentes."),
 dict(
  NOME="Bollettini fitosanitari — Unita territoriali di monitoraggio (UTM)",
  DONO="Regione Campania — UOS Servizio Fitosanitario e estruturas provinciais",
  URL="https://agricoltura.regione.campania.it/difesa/bollettini/bollettini_2026.html",
  PRODUZ="boletim com dados agrometeorologicos, ESTADO FENOLOGICO e "
         "fitossanitario das culturas LEVANTADOS NAS UTM (unidades "
         "territoriais de monitorizacao), mais conselhos de defesa segundo as "
         "Norme tecniche",
  EXEMPLO_REAL="cadencia declarada: SEMANAL de 1 de marco a 30 de setembro e "
               "MENSAL de 1 de outubro a 28 de fevereiro",
  CULTURAS_QUE_NOMEIA=["Tomato", "Wheat", "Maize"],
  ALIMENTA=["WINDOWS · OBSERVACAO DE CAMPO (fase observada, nao esperada)",
            "WINDOWS · FASE FENOLOGICA DA CULTURA (o que a planta esta a fazer)",
            "WINDOWS · Cultura e regiao da janela",
            "VOICES · REGIAO da voz de campo"],
  AMBITO="Campania, por UTM", TERR=["T1", "T2", "T3"],
  RECORRENCIA="HIGH — semanal na campanha, mensal fora dela",
  CLASSE="A", PRIMARIA="PRIMARY",
  GAP_FECHA="CRITICAL — «levantado na UTM» e' fase OBSERVADA com lugar "
            "declarado, que e' exatamente o `CROP_STAGE 0/29`. E fecha a "
            "Campania, que estava FRACA",
  EVIDENCIA=f"{B}: a dupla cadencia e a origem do dado na UTM estao escritas "
            "na propria pagina da serie",
  LIMITE="a UTM da o lugar do levantamento, nao a coordenada. Regiao sim, "
         "parcela nao."),
 dict(
  NOME="Bollettini di produzione integrata — pomodoro da industria",
  DONO="Consorzi Fitosanitari Provinciali de Reggio Emilia, Modena, Parma e "
       "Piacenza",
  URL="https://www.fitosanitario.re.it/bollettino-singole-colture/",
  PRODUZ="boletim provincial SEMANAL para tomate, construido com o modelo "
         "previsional I.P.I., levantamentos AEROBIOLOGICOS e CAMPOS-ESPIA NAO "
         "TRATADOS; escolhe o principio ativo pela FASE FENOLOGICA",
  EXEMPLO_REAL="a defesa antiperonosporica arranca com base nos boletins "
               "provinciais semanais; medido que a suscetibilidade e' maxima "
               "logo apos o transplante, aumenta a resistencia ate a floracao "
               "e decresce ate a maturacao — e que em Emilia-Romagna os "
               "ataques concentram-se em junho-julho",
  CULTURAS_QUE_NOMEIA=["Tomato"],
  ALIMENTA=["WINDOWS · FASE FENOLOGICA DA CULTURA (o que a planta esta a fazer)",
            "WINDOWS · FASE DO PROBLEMA (em que estadio esta a praga/doenca)",
            "WINDOWS · OBSERVACAO DE CAMPO (fase observada, nao esperada)",
            "PORTFOLIO · MOMENTO DE APLICACAO / fase da cultura na aplicacao"],
  AMBITO="provincias de Reggio Emilia, Modena, Parma e Piacenza",
  TERR=["T1", "T3", "T4"],
  RECORRENCIA="HIGH — semanal na campanha",
  CLASSE="A", PRIMARIA="PRIMARY",
  GAP_FECHA="CRITICAL — fecha o tomate, que tinha 3 janelas e zero fonte. E o "
            "CAMPO-ESPIA NAO TRATADO e' observacao de campo no sentido forte: "
            "parcela deixada sem tratamento para se ver a doenca acontecer",
  EVIDENCIA=f"{B}: as tres entradas do boletim (modelo I.P.I., aerobiologia, "
            "campos-espia) e a curva de suscetibilidade por fase estao "
            "descritas na ficha tecnica regional da peronospora",
  LIMITE="sao QUATRO donos distintos (quatro consorzi), nao um. E a cultura "
         "e' tomate de INDUSTRIA; o de mesa tem norma propria."),
 dict(
  NOME="Bollettino seminativi biologici",
  DONO="AIAB Friuli Venezia Giulia, em colaboracao com a ERSA",
  URL="https://www.aiab.fvg.it/aziende-e-tecnici/",
  PRODUZ="boletim periodico de arvenses em regime BIOLOGICO, a partir de "
         "levantamentos em campo e monitorizacao de AZIENDE CAMPIONE",
  EXEMPLO_REAL="«Bollettino seminativi biologici n. 8/2026 del 24 giugno "
               "2026», cobrindo andamento meteorologico, cereais "
               "outono-invernais, leguminosas de grao e culturas "
               "primavera-verao",
  CULTURAS_QUE_NOMEIA=["Wheat", "Durum Wheat", "Soybean", "Maize"],
  ALIMENTA=["WINDOWS · OBSERVACAO DE CAMPO (fase observada, nao esperada)",
            "WINDOWS · FASE DO PROBLEMA (em que estadio esta a praga/doenca)",
            "VOICES · PAPEL de quem fala (produtor? tecnico? amador?)"],
  AMBITO="Friuli-Venezia Giulia", TERR=["T1", "T3", "T8"],
  RECORRENCIA="HIGH — numerada e datada",
  CLASSE="A", PRIMARIA="PRIMARY",
  GAP_FECHA="HIGH — «rilievi in campo» e «aziende campione» sao observacao "
            "real, e o recorte biologico e' um regime que nenhuma das 37 tinha",
  EVIDENCIA=f"{B}: numero, data e indice de conteudo lidos na propria edicao",
  LIMITE="regime biologico: a janela de produto nao serve o convencional."),
 dict(
  NOME="IrriNet e FERTIRRINET",
  DONO="CER — Canale Emiliano Romagnolo / ANBI, para a Regione Emilia-Romagna",
  URL="https://www.irriframe.it/",
  PRODUZ="conselho de rega e de fertilizacao calculado POR FASE FENOLOGICA, "
         "tipo de solo e meteorologia medida E prevista, para mais, pomodoro, "
         "patata e pero",
  EXEMPLO_REAL="o aplicativo FERTIRRINET dentro do IrriNet e' descrito como "
               "dando conselho de fertilizacao conforme DPI, tendo em conta "
               "cultura, FASE FENOLOGICA, tipo de solo e condicoes meteo "
               "medidas e previstas",
  CULTURAS_QUE_NOMEIA=["Maize", "Tomato", "Apple"],
  ALIMENTA=["WINDOWS · FASE FENOLOGICA DA CULTURA (o que a planta esta a fazer)",
            "WINDOWS · Janela de monitorizacao (quando ir olhar)"],
  AMBITO="Emilia-Romagna, com Irriframe em varias regioes",
  TERR=["T1", "T2"],
  RECORRENCIA="HIGH — diaria/por evento",
  CLASSE="B", PRIMARIA="SECONDARY",
  GAP_FECHA="MEDIUM — traz a fase fenologica como ENTRADA de um modelo, nao "
            "como observacao publicada. Serve para saber que a fase e' "
            "computada, nao para a ler",
  EVIDENCIA=f"{B}: as quatro culturas e a fase fenologica entre as entradas "
            "do modelo estao declaradas",
  LIMITE="⚠️ E' MODELO, e o que o casco precisa e' fase OBSERVADA. Classe B "
         "por isso, nao por duvida sobre o dono."),
]

# ═════════════════════════════════════════════════════════════════════════════
# AS 2 REGIOES ZERADAS — Basilicata e Valle d'Aosta
# ═════════════════════════════════════════════════════════════════════════════
REGIOES_ZERO = [
 dict(
  NOME="SAL — Servizio Agrometeorologico Lucano, e os bollettini do SeDI",
  DONO="ALSIA — Agenzia Lucana di Sviluppo e di Innovazione in Agricoltura, "
       "pela Regione Basilicata",
  URL="https://www.alsia.it/opencms/opencms/Temi/dettaglio/Agrometeorologia/",
  PRODUZ="rede de QUARENTA estacoes agrometeorologicas desde 1996, com "
         "temperatura do ar e do solo, humidade, chuva, vento, radiacao e "
         "MOLHA FOLIAR, mais evapotranspiracao por Blaney-Criddle e "
         "Penman-Monteith; e boletins fitossanitarios POR COMPRENSORIO, "
         "dentro do SeDI (Servizio di Difesa Integrata)",
  EXEMPLO_REAL="tres comprensori com boletim proprio — Metapontino, Alta Valle "
               "d'Agri e Valle del Bradano/Lavellese. Relatorio climatico "
               "mensal «Analisi climatica del mese di gennaio 2026» com "
               "ANOMALIA de temperatura face a 1991-2020 (Copernicus), em "
               "alsia.it/.../Bollettini/gennaio_2026.pdf. Boletim "
               "agrometeorologico semanal apresentado por Emanuele Scalcione, "
               "funcionario da ALSIA responsavel pelo SAL",
  CULTURAS_QUE_NOMEIA=[],
  ALIMENTA=["WINDOWS · OBSERVACAO DE CAMPO (fase observada, nao esperada)",
            "WINDOWS · FASE FENOLOGICA DA CULTURA (o que a planta esta a fazer)",
            "WINDOWS · Janela de monitorizacao (quando ir olhar)",
            "WINDOWS · Desvio fenologico por regiao (a mesma cultura adianta/atrasa)",
            "FUTURE · DESLOCACAO CLIMATICA que muda a pressao de praga",
            "VOICES · PAPEL de quem fala (produtor? tecnico? amador?)"],
  AMBITO="Basilicata, em 3 comprensori, com 40 estacoes", TERR=["T1", "T2", "T3"],
  RECORRENCIA="HIGH — diaria (estacoes), semanal (boletim), mensal (clima)",
  CLASSE="A", PRIMARIA="PRIMARY",
  GAP_FECHA="CRITICAL — a Basilicata tinha ZERO fonte regional. Esta entrega "
            "fenologia, observacao de campo, molha foliar E anomalia "
            "climatica de uma vez, com pessoa nomeada e papel declarado",
  EVIDENCIA=f"{B}: numero de estacoes, ano de inicio, variaveis medidas, as "
            "duas formulas de evapotranspiracao, os tres comprensori, o "
            "relatorio mensal com periodo de referencia e o nome do "
            "responsavel — todos declarados pela ALSIA",
  LIMITE="⚠️ OS BOLETINS PEDEM INSCRICAO nos servicos de consultoria online. "
         "Sao gratuitos, mas atras de conta — e dado atras de conta e' outra "
         "decisao de coleta."),
 dict(
  NOME="Avvisi fitosanitari per viticoltori e per frutticoltori",
  DONO="Regione autonoma Valle d'Aosta — Ufficio servizi fitosanitari "
       "(Assessorato Agricoltura e Risorse naturali)",
  URL="https://www.regione.vda.it/agricoltura/per_gli_agricoltori/fitosanitario/avvisi/viticoltura_i.asp",
  PRODUZ="avisos fitossanitarios de campanha, apoiados numa REDE DE "
         "ARMADILHAS montada cada estacao para as principais pragas, "
         "distribuidos por aviso em pontos estrategicos, gravador telefonico "
         "das cooperativas, web e SMS",
  EXEMPLO_REAL="a pagina dos avisos para viticultores declara ultima "
               "atualizacao em 26/06/2026; existe serie paralela para "
               "fruticultores; e «Schede trattamenti 2026» como guia. O "
               "servico e' reconhecido Servizio Fitosanitario Regionale e "
               "coordenado pelo nacional",
  CULTURAS_QUE_NOMEIA=["Grapevine", "Apple"],
  ALIMENTA=["WINDOWS · FASE DO PROBLEMA (em que estadio esta a praga/doenca)",
            "WINDOWS · Janela de monitorizacao (quando ir olhar)",
            "WINDOWS · ATO REGULATORIO regional que abre/fecha a janela",
            "FUTURE · PRAGA OU DOENCA EMERGENTE (primeira deteccao)"],
  AMBITO="Valle d'Aosta", TERR=["T1", "T3", "T9"],
  RECORRENCIA="MEDIUM — de campanha, por evento de armadilha",
  CLASSE="A", PRIMARIA="PRIMARY",
  GAP_FECHA="CRITICAL — a Valle d'Aosta tinha ZERO fonte regional. E a rede de "
            "armadilhas com servico de previsao e aviso e' fase do problema "
            "medida, nao estimada",
  EVIDENCIA=f"{B}: data de ultima atualizacao na pagina, existencia das duas "
            "series, os quatro canais de distribuicao e o reconhecimento "
            "institucional — todos lidos no sitio da regiao",
  LIMITE="regiao pequena e bilingue (italiano/frances). O aviso por SMS e "
         "gravador telefonico NAO e' coletavel por rota web."),
 dict(
  NOME="Dati di maturazione dell'uva e scelta della data di vendemmia",
  DONO="Institut Agricole Régional (IAR), Aosta — Unita de Analises "
       "Laboratoriais e Unita de Viticultura-Enologia, com o Assessorato "
       "Agricoltura da Regione Valle d'Aosta",
  URL="https://www.iaraosta.it/",
  PRODUZ="tratamento dos dados de MATURACAO DA UVA das vinhas mais "
         "representativas da Valle d'Aosta e do proprio IAR, para escolher a "
         "data de vindima",
  EXEMPLO_REAL="o servico e' descrito como colaboracao entre o IAR e o "
               "Assessorato, com dados das vinhas mais representativas da "
               "regiao; o IAR e' historicamente a casa que criou o mercado "
               "das castas autoctones — fumin, petit rouge, cornalin, prie "
               "blanc, mayolet, vuillermin",
  CULTURAS_QUE_NOMEIA=["Grapevine"],
  ALIMENTA=["WINDOWS · FASE FENOLOGICA DA CULTURA (o que a planta esta a fazer)",
            "WINDOWS · OBSERVACAO DE CAMPO (fase observada, nao esperada)",
            "WINDOWS · Datas de inicio e fim da janela"],
  AMBITO="Valle d'Aosta", TERR=["T1", "T5"],
  RECORRENCIA="MEDIUM — sazonal, na maturacao",
  CLASSE="A", PRIMARIA="PRIMARY",
  GAP_FECHA="HIGH — maturacao medida em vinha representativa e' fase "
            "OBSERVADA, e da a data de inicio da janela de vindima",
  EVIDENCIA=f"{B}: as duas unidades responsaveis, o parceiro institucional e "
            "a origem dos dados estao declarados pelo IAR",
  LIMITE="sazonal e de uma cultura. Serve a vindima, nao a campanha toda."),
 dict(
  NOME="Bollettini AgroAmbiente e Disciplinare di Produzione Integrata",
  DONO="Regione Abruzzo — AgroAmbiente",
  URL="https://agroambiente.regione.abruzzo.it/",
  PRODUZ="boletins periodicos com dados agrometeo e FASES FENOLOGICAS, mais o "
         "DPI regional com o Allegato B por avversita",
  EXEMPLO_REAL="«Bollettino n. 11 del 1 luglio 2026»; e o DPI Abruzzo 2026 "
               "com integracoes ao Allegato B sobre ragnetto rosso e "
               "peronospora em varias culturas",
  CULTURAS_QUE_NOMEIA=["Grapevine", "Olive", "Tomato"],
  ALIMENTA=["WINDOWS · FASE FENOLOGICA DA CULTURA (o que a planta esta a fazer)",
            "WINDOWS · ATO REGULATORIO regional que abre/fecha a janela",
            "WINDOWS · Desvio fenologico por regiao (a mesma cultura adianta/atrasa)"],
  AMBITO="Abruzzo", TERR=["T1", "T2", "T3"],
  RECORRENCIA="HIGH — boletim numerado e datado",
  CLASSE="A", PRIMARIA="PRIMARY",
  GAP_FECHA="HIGH — o Abruzzo estava FRACO (uma fonte). E esta e' a casa que "
            "quantifica o desvio: ~2 semanas de atraso acima de 400 m ou a "
            "mais de 40 km da costa",
  EVIDENCIA=f"{B}: numero e data do boletim, e o conteudo do Allegato B do "
            "DPI 2026",
  LIMITE="regional."),
]

TODAS_NOVAS = CULTURAS + REGIOES_ZERO


def _validar():
    from italy_gap_needs import NECESSIDADES
    validas = {f'{n["TOOL"]} · {n["RAW_NEED"]}' for n in NECESSIDADES}
    erros = []
    for f in TODAS_NOVAS:
        for c in f["TERR"]:
            if not _T.valido(c):
                erros.append(f'{f["NOME"][:36]}: territorio {c} nao existe')
        for a in f["ALIMENTA"]:
            if a not in validas:
                erros.append(f'{f["NOME"][:36]}: necessidade orfa «{a}»')
        if f["CLASSE"] == "A" and not f.get("EXEMPLO_REAL"):
            erros.append(f'{f["NOME"][:36]}: classe A sem exemplo real')
    return erros


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    from collections import Counter
    erros = _validar()
    print(f"FONTES DA SEGUNDA VAGA = {len(TODAS_NOVAS)}")
    print("  classe:", dict(Counter(f["CLASSE"] for f in TODAS_NOVAS)))
    print("  primaria:", dict(Counter(f["PRIMARIA"] for f in TODAS_NOVAS)))
    print("  ligacoes:", sum(len(f["ALIMENTA"]) for f in TODAS_NOVAS))
    cult = Counter()
    for f in TODAS_NOVAS:
        for c in f["CULTURAS_QUE_NOMEIA"]:
            cult[c] += 1
    print("\n  AS 5 CULTURAS QUE FALTAVAM:")
    for c in ("Wheat", "Durum Wheat", "Maize", "Soybean", "Tomato"):
        print(f"    {c:14s} {cult[c]} fontes")
    print("\n  AS 2 REGIOES ZERADAS:")
    for r in ("Basilicata", "Valle d'Aosta"):
        n = sum(1 for f in TODAS_NOVAS if r in f["AMBITO"])
        print(f"    {r:14s} {n} fontes")
    if erros:
        print(f"\n!! {len(erros)} PROBLEMAS:")
        for e in erros:
            print("   ", e)
        sys.exit(1)
    print("\nVALIDACAO OK")
