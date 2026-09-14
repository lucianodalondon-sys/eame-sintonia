#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FONTES NOVAS — achadas por busca DIRIGIDA AO GAP, nunca por tema.

A regra da missao era clara: nao «buscar fontes agricolas da Sicilia», mas
«Sicilia + vite + bollettino fitosanitario + fenologia». Cada linha daqui
nasceu de um buraco medido em COBERTURA.json, e carrega o buraco no campo
`ALIMENTA` — quem nao souber que necessidade alimenta nao entra.

UMA FONTE, VARIOS USOS
----------------------
`ALIMENTA` e' uma LISTA. A folha SOURCE_TO_TOOL explode essa lista; a folha
NEW_SOURCES nao. Contar a mesma fonte uma vez por ferramenta inflacionaria a
entrega em ~40%.

O QUE FAZ UMA LINHA SER CLASSE A
--------------------------------
Tem de haver as dez coisas: identidade, dono, rota, EXEMPLO REAL visto,
o que produz, que necessidade alimenta, que ferramenta serve, ambito
geografico, potencial de recorrencia e a evidencia de onde isto saiu.
Falta uma -> classe B. Nao ha «A por parecer importante».

E O QUE NAO E' PROVA
--------------------
Nenhuma destas rotas foi aberta por sonda nesta missao. A evidencia e' de
DESCOBERTA (busca dirigida), e esta escrita em `EVIDENCIA`. Rota descrita
por busca != rota lida. Por isso nenhuma linha diz CONFIRMED.
"""

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))
import _territorios as _T          # noqa: E402

BUSCA = "busca dirigida ao gap, 2026-09-14"

# ─────────────────────────────────────────────────────────────────────────────
# GAP 1 · WINDOWS · FASE FENOLOGICA  (CRITICAL — contrato: CROP_STAGE 0/29)
# ─────────────────────────────────────────────────────────────────────────────
FENOLOGIA = [
 dict(
  NOME="Bollettino Nazionale di Fenologia",
  DONO="Rete Rurale Nazionale (RRN) / MASAF",
  URL="https://www.reterurale.it/bollettinofeno",
  PRODUZ="boletim de fenologia com escala BBCH por cultura, cruzando modelo de "
         "simulacao, dados MeteoHub/CINECA e observacao de campo de voluntarios",
  EXEMPLO_REAL="boletim periodico nacional com fase BBCH declarada por cultura",
  ALIMENTA=["WINDOWS · FASE FENOLOGICA DA CULTURA (o que a planta esta a fazer)",
            "WINDOWS · Desvio fenologico por regiao (a mesma cultura adianta/atrasa)",
            "RADAR · ENTRADA: janela de cultura com data e regiao"],
  AMBITO="NACIONAL, com detalhe regional", TERR=["T1", "T2"],
  RECORRENCIA="HIGH — periodicidade declarada",
  CLASSE="A",
  EVIDENCIA=f"{BUSCA}: o proprio sitio descreve a escala BBCH e as tres "
            "entradas (modelo, MeteoHub/CINECA, observadores de campo)",
  LIMITE="parte do dado vem de MODELO. Fase modelada nao e' fase observada, e "
         "o contrato pede observada. Tem de vir com a marca de origem."),
 dict(
  NOME="Bollettini viticoli del Servizio Fitosanitario del Veneto",
  DONO="Regione del Veneto — U.O. Fitosanitario",
  URL="https://www.regione.veneto.it/web/fitosanitario/bollettini-viticoli",
  PRODUZ="fase fenologica BBCH por VITIGNO, separando ambiente precoce de "
         "tardio, mais estado parasitario e indicacoes de defesa",
  EXEMPLO_REAL="pagina «Bollettini fitosanitari 2026» com serie datada da "
               "campanha, incluindo janelas dos tratamentos obrigatorios "
               "contra flavescencia dourada",
  ALIMENTA=["WINDOWS · FASE FENOLOGICA DA CULTURA (o que a planta esta a fazer)",
            "WINDOWS · FASE DO PROBLEMA (em que estadio esta a praga/doenca)",
            "WINDOWS · ATO REGULATORIO regional que abre/fecha a janela",
            "RADAR · ENTRADA: janela de cultura com data e regiao"],
  AMBITO="Veneto", TERR=["T1", "T3"],
  RECORRENCIA="HIGH — semanal na campanha",
  CLASSE="A",
  EVIDENCIA=f"{BUSCA}: separacao precoce/tardio e ligacao a luta obrigatoria "
            "descritas na propria pagina do servico",
  LIMITE="a serie e' sazonal: fora da campanha nao publica."),
 dict(
  NOME="Bollettino agrometeorologico e fitosanitario ARSAC",
  DONO="ARSAC — Azienda Regionale per lo Sviluppo dell'Agricoltura Calabrese",
  URL="https://www.arsacweb.it/bollettino-agrometeorologico-e-fitosanitario-agrumi-olivo-e-vite/",
  PRODUZ="situacao meteorologica E FENOLOGICA de vite, olivo, agrumi e kiwi, "
         "para 8 AREAS CLIMATICAMENTE HOMOGENEAS da regiao, com validade "
         "semanal datada",
  EXEMPLO_REAL="«BOLLETTINO … valido dal 25 agosto al 1 settembre 2026» — e as "
               "8 areas nomeadas: Cosenza Tirrenica, Cosenza Ionica, Piana di "
               "Lamezia e Vibo, Catanzarese, Crotonese, Ionio Reggino-Reggio, "
               "Tirreno Reggino, Locride",
  ALIMENTA=["WINDOWS · FASE FENOLOGICA DA CULTURA (o que a planta esta a fazer)",
            "WINDOWS · Datas de inicio e fim da janela",
            "WINDOWS · Cultura e regiao da janela",
            "VOICES · REGIAO da voz de campo",
            "VOICES · DATA da observacao de campo"],
  AMBITO="Calabria, subdividida em 8 zonas", TERR=["T1", "T2", "T3"],
  RECORRENCIA="HIGH — semanal, com intervalo de validade explicito",
  CLASSE="A",
  EVIDENCIA=f"{BUSCA}: seis titulos datados diferentes da mesma serie "
            "apareceram na busca, de maio a setembro de 2026 — recorrencia "
            "visivel sem abrir o arquivo",
  LIMITE="⚠️ DUAS ROTAS PARA O MESMO DONO: `arsacweb.it` e "
         "`arsac.calabria.it` publicam a mesma serie. E' "
         "SAME_SOURCE_VARIANT_URL, nao duas fontes."),
 dict(
  NOME="Bollettini di viticoltura e di olivicoltura del CAAR",
  DONO="Regione Liguria — CAAR / Servizi Imprese Agricole",
  URL="https://www.agriligurianet.it/it/impresa/assistenza-tecnica-e-centri-serivizio/agrometeo-caar/bollettino-di-olivicoltura.html",
  PRODUZ="andamento fenologico do olivo SEGUNDO A ESCALA BBCH em olivais "
         "representativos da rede regional de monitorizacao, com destaque "
         "para floracao, vingamento e maturacao; serie paralela para vite",
  EXEMPLO_REAL="«Olivo n. 03 – 19 marzo», com versoes separadas por provincia "
               "(GE · IM · SP · SV) — numeracao progressiva mais data",
  ALIMENTA=["WINDOWS · FASE FENOLOGICA DA CULTURA (o que a planta esta a fazer)",
            "WINDOWS · Datas de inicio e fim da janela",
            "WINDOWS · OBSERVACAO DE CAMPO (fase observada, nao esperada)",
            "VOICES · REGIAO da voz de campo",
            "VOICES · DATA da observacao de campo"],
  AMBITO="Liguria, por provincia (GE/IM/SP/SV)", TERR=["T1", "T2", "T3"],
  RECORRENCIA="HIGH — semanal de abril a setembro, mensal de outubro a marco",
  CLASSE="A",
  EVIDENCIA=f"{BUSCA}: a periodicidade dupla (semanal/mensal) e a numeracao "
            "com data estao descritas na propria pagina",
  LIMITE="o dono publica em dois sitios (`agriligurianet.it` e "
         "`sia.regione.liguria.it`). Mesmo dono, rotas diferentes."),
 dict(
  NOME="Bollettino Vite Integrato provinciale",
  DONO="Consorzio LaMMA (Toscana)",
  URL="https://www.lamma.toscana.it/previ/ita/agrometeo/",
  PRODUZ="avaliacao do estado fenologico do vinhedo por PROVINCIA, com a "
         "heterogeneidade dentro da provincia escrita em texto",
  EXEMPLO_REAL="Bollettino Vite Integrato, Provincia di Siena, 16/04/2026: "
               "brotos de 8–10 cm em algumas areas, retoma vegetativa mais "
               "tardia noutras",
  ALIMENTA=["WINDOWS · FASE FENOLOGICA DA CULTURA (o que a planta esta a fazer)",
            "WINDOWS · Desvio fenologico por regiao (a mesma cultura adianta/atrasa)",
            "WINDOWS · Cultura e regiao da janela"],
  AMBITO="Toscana, por provincia", TERR=["T1", "T2"],
  RECORRENCIA="HIGH — serie provincial datada na campanha",
  CLASSE="A",
  EVIDENCIA=f"{BUSCA}: a rota devolveu um boletim com data e medida concreta "
            "(8–10 cm) — exemplo real, nao promessa",
  LIMITE="mede em centimetros de broto, nao em codigo BBCH: precisa de "
         "conversao, e conversao e' interpretacao."),
 dict(
  NOME="Notiziario agrometeorologico e fitosanitario delle Marche",
  DONO="Regione Marche — ASSAM / Servizio Agrometeo",
  URL="https://meteo.regione.marche.it/",
  PRODUZ="notiziario com CODIGO BBCH explicito por cultura",
  EXEMPLO_REAL="melo BBCH 75-77 · pero BBCH 76-81 · vite BBCH 79",
  ALIMENTA=["WINDOWS · FASE FENOLOGICA DA CULTURA (o que a planta esta a fazer)",
            "WINDOWS · OBSERVACAO DE CAMPO (fase observada, nao esperada)"],
  AMBITO="Marche", TERR=["T1", "T2"],
  RECORRENCIA="HIGH — notiziario periodico",
  CLASSE="A",
  EVIDENCIA=f"{BUSCA}: codigos BBCH numericos por cultura lidos no notiziario",
  LIMITE="o ASSAM tem historico de rota atras de login "
         "(`assam-agrometeo.invionews.net` foi controle negativo da missao "
         "anterior). Confirmar qual das rotas e' publica."),
 dict(
  NOME="Bollettini fenologici di uno studio agronomico privato (Agralia)",
  DONO="Agralia Studio Agronomico — Brescia",
  URL="https://www.agralia.it/",
  PRODUZ="boletim periodico proprio para viticultura e olivicultura, cruzando "
         "chuva, temperatura, MOLHA FOLIAR e humidade com observacao direta "
         "em campo, e concluindo em posicionamento de tratamento",
  EXEMPLO_REAL="servico de monitorizacao agrometeorologica descrito com as "
               "quatro variaveis e o cruzamento com observacao direta",
  ALIMENTA=["WINDOWS · FASE FENOLOGICA DA CULTURA (o que a planta esta a fazer)",
            "WINDOWS · OBSERVACAO DE CAMPO (fase observada, nao esperada)",
            "VOICES · PAPEL de quem fala (produtor? tecnico? amador?)",
            "VOICES · Voz de campo com autor identificado"],
  AMBITO="Brescia / Lombardia", TERR=["T1", "T3", "T8"],
  RECORRENCIA="MEDIUM — periodico, mas periodicidade nao declarada",
  CLASSE="B",
  EVIDENCIA=f"{BUSCA}: unico privado que a busca achou a declarar boletim "
            "proprio com observacao de campo",
  LIMITE="⚠️ boletim de CONSULTORIA: provavelmente reservado a clientes. "
         "Fonte de conhecimento, talvez nao de coleta."),
 dict(
  NOME="Notiziario agrofenologico e di difesa (olivo, vite)",
  DONO="Consorzi Fitosanitari Provinciali di Modena e Reggio Emilia",
  URL="https://www.fitosanitario.mo.it/fito3/notiziario-agrofenologico-e-di-difesa-della-coltura-dell-oli",
  PRODUZ="notiziario AGROFENOLOGICO provincial (Modena: ARPO OLIVO) e "
         "boletim antiperonosporico/antioidico da vite (Reggio Emilia)",
  EXEMPLO_REAL="secao «BOLLETTINO ARPO OLIVO» no sitio de Modena; "
               "«bollettino antiperonosporico» em `fitosanitario.re.it`",
  ALIMENTA=["WINDOWS · FASE FENOLOGICA DA CULTURA (o que a planta esta a fazer)",
            "WINDOWS · FASE DO PROBLEMA (em que estadio esta a praga/doenca)",
            "WINDOWS · Janela de monitorizacao (quando ir olhar)"],
  AMBITO="provincias de Modena e Reggio Emilia", TERR=["T1", "T3"],
  RECORRENCIA="HIGH — serie de campanha",
  CLASSE="A",
  EVIDENCIA=f"{BUSCA}: duas rotas provinciais distintas, ambas com secao de "
            "boletim nomeada",
  LIMITE="sao DOIS donos distintos (dois consorzi), nao um."),
 dict(
  NOME="Bollettini agronomici per vite dell'Ufficio Agronomico",
  DONO="Terre dell'Etruria — cooperativa agricola (Toscana)",
  URL="https://www.terretruria.it/agronomi/vite/16-bollettini-agronomici-per-vite/",
  PRODUZ="boletins proprios dos tecnicos da cooperativa, com tabelas de "
         "estrategia de defesa por REGIME de cultivo da vite",
  EXEMPLO_REAL="secao «Bollettini agronomici per vite» assinada pelos "
               "agronomos da cooperativa",
  ALIMENTA=["WINDOWS · FASE DO PROBLEMA (em que estadio esta a praga/doenca)",
            "VOICES · PAPEL de quem fala (produtor? tecnico? amador?)",
            "VOICES · Voz de campo com autor identificado"],
  AMBITO="Toscana costeira (Livorno/Grosseto)", TERR=["T1", "T3", "T8"],
  RECORRENCIA="MEDIUM — declarado como serie, sem periodicidade escrita",
  CLASSE="B",
  EVIDENCIA=f"{BUSCA}: rota com numeracao de serie no proprio caminho",
  LIMITE="cooperativa fala para socios; alcance fora do circulo e' NAO SEI."),
 dict(
  NOME="Calendario fenologico e Forum Fitoiatrico del Condifesa TVB",
  DONO="Condifesa Treviso e Belluno",
  URL="https://www.condifesatvb.it/forum-fitoiatrico/",
  PRODUZ="calendario fenologico da campanha E o Forum Fitoiatrico, onde "
         "tecnicos das empresas de agrofarmacos e do servico fitossanitario "
         "regional falam NOMEADOS, com a sua funcao declarada",
  EXEMPLO_REAL="edicao 2026 com Dario Bond (Assessore Agricoltura Regione "
               "Veneto), referentes da U.O. Fitosanitario regional, e tecnicos "
               "nomeados: Marco Pravisano (Syngenta), Marco Grandin (Bayer), "
               "Giorgio Fioretti (BASF) — mais Upl, Sipcam, Nufarm, Gowan, "
               "Fmc, Diachem, Certis Belchim, CBC Europe, ADAMA, Suterra, "
               "Sumitomo",
  ALIMENTA=["WINDOWS · FASE FENOLOGICA DA CULTURA (o que a planta esta a fazer)",
            "VOICES · PAPEL de quem fala (produtor? tecnico? amador?)",
            "VOICES · REGIAO da voz de campo",
            "VOICES · DATA da observacao de campo",
            "COMPETITORS · PESSOA do concorrente (quem fala por ele)",
            "COMPETITORS · REGIAO da atividade do concorrente",
            "COMPETITORS · CONTEUDO TECNICO do concorrente (nao publicidade)",
            "FIELD_NET · Identidade do tecnico de campo (TSR)"],
  AMBITO="Treviso e Belluno (Veneto)", TERR=["T1", "T3", "T8", "T11"],
  RECORRENCIA="MEDIUM — anual (forum) mais serie de campanha (calendario)",
  CLASSE="A",
  EVIDENCIA=f"{BUSCA}: a lista de participantes com nome, empresa e funcao "
            "apareceu na propria descricao do forum. E' o unico achado da "
            "missao que entrega PESSOA + PAPEL + EMPRESA + REGIAO + DATA "
            "de uma vez",
  LIMITE="a ADAMA esta na lista. Ler isto como «atividade de concorrente» "
         "obriga a excluir a propria casa do calculo."),
]

# ─────────────────────────────────────────────────────────────────────────────
# GAP 2 · MARKET · PRODUCAO / AREA / RENDIMENTO  (CRITICAL — coluna ausente)
# ─────────────────────────────────────────────────────────────────────────────
PRODUCAO = [
 dict(
  NOME="Dataflow DCSP_COLTIVAZIONI (coltivazioni: superficie, produzione, resa)",
  DONO="ISTAT",
  URL="https://esploradati.istat.it/SDMXWS/rest/",
  PRODUZ="superficie, producao colhida e rendimento por cultura, com "
         "estimativas MENSAIS e desagregacao por regiao, provincia e ZONA "
         "ALTIMETRICA",
  EXEMPLO_REAL="dataflow `DCSP_COLTIVAZIONI` servido por API SDMX; partes do "
               "dado chegam de terceiros declarados — arroz do Enterisi, "
               "tabaco da Agea, beterraba da ABSI",
  ALIMENTA=["MARKET · PRODUCAO, AREA e RENDIMENTO por cultura",
            
            "RADAR · ENTRADA: mercado da mesma cultura"],
  AMBITO="NACIONAL com regiao, provincia e altimetria", TERR=["T10"],
  RECORRENCIA="HIGH — estimativas mensais, serie anual consolidada",
  CLASSE="A",
  EVIDENCIA=f"{BUSCA}: nome do dataflow e raiz do servico SDMX identificados; "
            "as tres fontes terceiras estao declaradas pelo ISTAT",
  LIMITE="a zona altimetrica nao e' a regiao agronomica do boletim "
         "fitossanitario. Juntar as duas e' trabalho, nao e' leitura."),
 dict(
  NOME="Statistica agricoltura regionale (superfici e produzioni)",
  DONO="Regione Emilia-Romagna — Servizio Statistica",
  URL="https://statistica.regione.emilia-romagna.it/",
  PRODUZ="serie regionais de superficie e producao, ja recortadas a regiao",
  EXEMPLO_REAL="portal de estatistica regional com secao de agricultura",
  ALIMENTA=["MARKET · PRODUCAO, AREA e RENDIMENTO por cultura"],
  AMBITO="Emilia-Romagna", TERR=["T10"],
  RECORRENCIA="MEDIUM — anual",
  CLASSE="B",
  EVIDENCIA=f"{BUSCA}: rota do servico de estatistica regional",
  LIMITE="uma regiao das vinte. Nao escala por si."),
]

# ─────────────────────────────────────────────────────────────────────────────
# GAP 3 · MARKET · IMPORTACAO/EXPORTACAO  (HIGH)  — e uma ROTA MORTA no acervo
# ─────────────────────────────────────────────────────────────────────────────
COMERCIO = [
 dict(
  NOME="Coeweb — statistiche del commercio estero (nuova sede)",
  DONO="ISTAT",
  URL="https://esploradati.istat.it/coeweb",
  PRODUZ="importacao e exportacao por produto, pais e provincia",
  EXEMPLO_REAL="a plataforma antiga `coeweb.istat.it` foi ENCERRADA em "
               "30/09/2025 e o servico passou para `esploradati.istat.it/coeweb`",
  ALIMENTA=["MARKET · IMPORTACAO e EXPORTACAO"],
  AMBITO="NACIONAL, com provincia", TERR=["T10"],
  RECORRENCIA="HIGH — mensal",
  CLASSE="A",
  EVIDENCIA=f"{BUSCA}: o encerramento e a nova sede estao declarados pelo "
            "proprio ISTAT",
  LIMITE="⚠️ ACHADO DE MANUTENCAO, NAO DE DESCOBERTA: o acervo aponta para a "
         "sede antiga. Quem coletar de `coeweb.istat.it` nao recebe erro "
         "obvio — recebe uma pagina. Ver DEAD_ROUTES."),
 dict(
  NOME="Commercio estero agroalimentare (banca dati)",
  DONO="ISMEA",
  URL="https://www.ismeamercati.it/dati-agroalimentare/commercio-estero",
  PRODUZ="comercio externo agroalimentar RECLASSIFICADO por comparto agricola "
         "(nao por codigo aduaneiro cru), em 4 vistas, com drilldown e "
         "exportacao xls/csv/pdf",
  EXEMPLO_REAL="banca dati com as quatro vistas e a exportacao declaradas",
  ALIMENTA=["MARKET · IMPORTACAO e EXPORTACAO",
            ],
  AMBITO="NACIONAL", TERR=["T10"],
  RECORRENCIA="HIGH — acompanha a serie ISTAT",
  CLASSE="A",
  EVIDENCIA=f"{BUSCA}: a reclassificacao por comparto e' o que a torna "
            "diferente do ISTAT cru — e e' a que serve a pergunta agricola",
  LIMITE="reclassificacao e' decisao do ISMEA. Bom para ler cultura; nao "
         "reconcilia com o ISTAT linha a linha."),
]

# ─────────────────────────────────────────────────────────────────────────────
# GAP 4 · MARKET · CUSTO DE INSUMO (pressao de custo)  (HIGH)
# ─────────────────────────────────────────────────────────────────────────────
CUSTOS = [
 dict(
  NOME="Indice dei prezzi dei mezzi correnti di produzione",
  DONO="ISMEA",
  URL="https://www.ismeamercati.it/",
  PRODUZ="indice mensal do preco dos meios correntes de producao (fertilizante, "
         "fitossanitario, energia, semente), serie desde 1984",
  EXEMPLO_REAL="~6.000 precos por semana para 600 referencias, mais ~300 "
               "leituras mensais em 12 consorzi agrari",
  ALIMENTA=["MARKET · CUSTO DE INSUMO (pressao de custo)", "MARKET · Serie de preco com 3+ pontos (para tendencia)"],
  AMBITO="NACIONAL", TERR=["T10"],
  RECORRENCIA="HIGH — mensal, com recolha semanal por tras",
  CLASSE="A",
  EVIDENCIA=f"{BUSCA}: volumes de recolha e data de inicio da serie "
            "declarados pelo ISMEA",
  LIMITE="⚠️ DESCONTINUIDADE DECLARADA, E E' GRAVE PARA SERIE: a rede de "
         "recolha foi revista a partir de JANEIRO DE 2025, e os indices "
         "mensais deixam de ser comparaveis com o ano anterior. A base muda "
         "para 2020 a partir de 01/01/2026. Comparar 2024 com 2025 sem "
         "saber disto produz uma variacao que nao aconteceu."),
 dict(
  NOME="Monitoraggio dei costi medi di produzione",
  DONO="ISMEA",
  URL="https://www.ismea.it/",
  PRODUZ="custo medio de producao em EUR/tonelada por cluster de empresa",
  EXEMPLO_REAL="servico declarado como complementar ao censo de "
               "armazenamento, para monitorizar margem de rendibilidade",
  ALIMENTA=["MARKET · CUSTO DE INSUMO (pressao de custo)"],
  AMBITO="NACIONAL, por cluster", TERR=["T10"],
  RECORRENCIA="MEDIUM — campanha",
  CLASSE="B",
  EVIDENCIA=f"{BUSCA}: existencia e finalidade declaradas pelo ISMEA",
  LIMITE="⚠️ EXIGE REGISTO. Dado atras de conta nao e' dado aberto, e a "
         "coleta automatica dele e' outra decisao."),
]

# ─────────────────────────────────────────────────────────────────────────────
# GAP 5 · MARKET · STOCKS  (HIGH)  — e a diferenca entre STOCK e CAPACIDADE
# ─────────────────────────────────────────────────────────────────────────────
STOCKS = [
 dict(
  NOME="Cantina Italia — giacenze di vino",
  DONO="MASAF / CREA, via registro telematico SIAN",
  URL="https://www.politicheagricole.it/",
  PRODUZ="existencias declaradas de vinho, por REGIAO, com periodicidade "
         "mensal, a partir da declaracao obrigatoria no registo telematico",
  EXEMPLO_REAL="a referencia normativa para giacenze de vinho por regiao e' a "
               "declaracao no registo telematico (SIAN / Cantina Italia), nao "
               "uma recolha de mercado",
  ALIMENTA=["MARKET · STOCKS / existencias"],
  AMBITO="NACIONAL com regiao", TERR=["T10"],
  RECORRENCIA="HIGH — mensal",
  CLASSE="B",
  EVIDENCIA=f"{BUSCA}: identificado como a fonte oficial correta para "
            "giacenze por regiao — em contraste com o ISMEA, que NAO faz "
            "essa recolha",
  LIMITE="rota exata do ficheiro publicado nao foi fixada nesta missao. "
         "Classe B por isso, e nao por duvida sobre o dono."),
 dict(
  NOME="Registro telematico dell'olio",
  DONO="AGEA / SIAN",
  URL="https://www.sian.it/",
  PRODUZ="existencias declaradas de azeite",
  EXEMPLO_REAL="identificado como o par do Cantina Italia para o azeite",
  ALIMENTA=["MARKET · STOCKS / existencias"],
  AMBITO="NACIONAL", TERR=["T10"],
  RECORRENCIA="HIGH — declaracao periodica obrigatoria",
  CLASSE="B",
  EVIDENCIA=f"{BUSCA}: citado como referencia normativa para existencias de azeite",
  LIMITE="idem: rota publica do agregado nao fixada."),
 dict(
  NOME="Censimento delle strutture di stoccaggio dei cereali",
  DONO="ISMEA, para o Piano cerealicolo nazionale (MASAF)",
  URL="https://www.ismea.it/flex/cm/pages/ServeBLOB.php/L/IT/IDPagina/8829",
  PRODUZ="mapa geografico dos centros de armazenamento e a CAPACIDADE "
         "instalada do setor cerealifero",
  EXEMPLO_REAL="quase 1.200 centros no territorio nacional, para mais de 11 "
               "milhoes de toneladas de potencial — 55% em silos, 45% em armazem",
  ALIMENTA=["MARKET · STOCKS / existencias"],
  AMBITO="NACIONAL, georreferenciado", TERR=["T10"],
  RECORRENCIA="LOW — censo, evento unico",
  CLASSE="B",
  EVIDENCIA=f"{BUSCA}: numeros do censo declarados pelo ISMEA",
  LIMITE="⚠️ ISTO E' CAPACIDADE, NAO EXISTENCIA. Um silo de 10.000 t vazio "
         "conta igual a um cheio. Quem usar isto como stock le' o contrario "
         "do que quer. E e' censo: nao repete."),
 dict(
  NOME="Rete di rilevazione Ismea–Unione Seminativi",
  DONO="ISMEA com a Unione Seminativi",
  URL="https://www.ismea.it/flex/cm/pages/ServeBLOB.php/L/IT/IDPagina/482",
  PRODUZ="informacao quali-quantitativa sobre a campanha EM CURSO, por "
         "questionario a peritos e operadores",
  EXEMPLO_REAL="23 estacoes de levantamento no centro e norte de Italia, nas "
               "provincias mais significativas para a cultura em estudo; "
               "resultados declarados PROVISORIOS e de conjuntura",
  ALIMENTA=["FUTURE · Sinal novo com o que se observou e quem o disse",
            "MARKET · PRODUCAO, AREA e RENDIMENTO por cultura"],
  AMBITO="centro e norte de Italia, 23 pontos", TERR=["T10", "T9"],
  RECORRENCIA="HIGH — periodica na campanha",
  CLASSE="A",
  EVIDENCIA=f"{BUSCA}: o proprio ISMEA declara os resultados como "
            "provisorios e complementares ao oficial (Istat, Agea, Mipaaf)",
  LIMITE="⚠️ E' EXPECTATIVA DE PERITO, nao medicao. Serve a ferramenta de "
         "SINAL; usa-la como producao mede opiniao e chama-lhe colheita."),
]

# ─────────────────────────────────────────────────────────────────────────────
# GAP 6 · PORTFOLIO · CARENCIA / DOSE / ALTERACAO  (CRITICAL)
# ─────────────────────────────────────────────────────────────────────────────
PORTFOLIO = [
 dict(
  NOME="Banca dati dei prodotti fitosanitari",
  DONO="Ministero della Salute",
  URL="https://www.fitosanitari.salute.gov.it/",
  PRODUZ="registo oficial do produto: numero de registo, titular, cultura e "
         "alvo autorizados, com atualizacao diaria e descarga do conjunto "
         "completo (~16.500 produtos)",
  EXEMPLO_REAL="base oficial com atualizacao diaria e ficheiro integral "
               "descarregavel",
  ALIMENTA=["PORTFOLIO · Produto, registo e titular",
            "PORTFOLIO · Cultura e ALVO autorizados por produto",
            "PORTFOLIO · Documento oficial do rotulo (PDF) e a sua data/versao",
            "PORTFOLIO · INTERVALO DE SEGURANCA (PHI) e n.o maximo de aplicacoes",
            "PORTFOLIO · ALTERACAO de autorizacao (o que mudou e quando)",
            "COMPETITORS · REGISTO oficial do produto do concorrente",
            "COMPETITORS · PRODUTO do concorrente na atividade",
            "RADAR · ENTRADA: ligacao produto x problema"],
  AMBITO="NACIONAL", TERR=["T4"],
  RECORRENCIA="HIGH — diaria",
  CLASSE="A",
  EVIDENCIA=f"{BUSCA}: volume e periodicidade declarados; o acervo ja "
            "conhece esta casa (ver memoria: os rotulos so abrem no urllib)",
  LIMITE="⚠️ O QUE FALTA ESTA DENTRO DO PDF: a carencia e a dose maxima NAO "
         "estao na tabela — vivem no ROTULO. Isso explica `interval 15/219 "
         "(7%)` e `maxApp 0/219`. O gap nao e' de fonte: e' de EXTRACAO."),
 dict(
  NOME="Banca dati Fitogest",
  DONO="Image Line Network",
  URL="https://fitogest.imagelinenetwork.com/it/banca-dati-e-portale/",
  PRODUZ="a mesma populacao de produtos, mas PESQUISAVEL POR TEMPO DI "
         "CARENZA — filtro que a base do Ministerio nao oferece",
  EXEMPLO_REAL="portal declara a filtragem por tempo di carenza entre os "
               "criterios de busca",
  ALIMENTA=["PORTFOLIO · INTERVALO DE SEGURANCA (PHI) e n.o maximo de aplicacoes",
            "PORTFOLIO · DOSE autorizada",
            "PORTFOLIO · MECANISMO DE ACAO (FRAC/HRAC/IRAC)"],
  AMBITO="NACIONAL", TERR=["T4"],
  RECORRENCIA="HIGH — segue o registo oficial",
  CLASSE="A",
  EVIDENCIA=f"{BUSCA}: a capacidade de filtrar por carencia e' a razao de "
            "esta linha existir — resolve exatamente o campo que falta",
  LIMITE="⚠️ E' AGREGADOR, nao autoridade. Se divergir do Ministerio, o "
         "Ministerio vence. E a memoria do projeto diz que este dominio "
         "devolve 403 ao WebFetch e abre ao urllib."),
 dict(
  NOME="Convegno «Prodotti fitosanitari: le novità»",
  DONO="Regione Emilia-Romagna — Settore Fitosanitario, com as empresas de "
       "agrofarmacos",
  URL="https://agricoltura.regione.emilia-romagna.it/fitosanitario/incontri-e-convegni/prodotti-fitosanitari-novita-2026",
  PRODUZ="as proprias empresas apresentam, uma a uma, novidade de gama e "
         "EXTENSAO DE USO, com substancia ativa, cultura e alvo nomeados",
  EXEMPLO_REAL="Bologna, 19/02/2026, >860 tecnicos inscritos. Syngenta — "
               "Boxer Evo (diflufenican + prosulfocarb) para girassol, batata "
               "e trigo; Corteva — Fencade (pyroxsulam + mesosulfuron), "
               "graminicida do trigo; BASF — Efficon (dimpropyridaz), uso "
               "excecional art. 53 em fruta, vite e horticolas; Bayer — "
               "Sivanto Prime (flupyradifurone), extensoes de emprego em "
               "Eriosoma lanigerum e psila da pereira",
  ALIMENTA=["PORTFOLIO · ALTERACAO de autorizacao (o que mudou e quando)",
            "PORTFOLIO · AUTORIZACAO EXCECIONAL (art. 53)",
            "PORTFOLIO · Substancia ativa do produto",
            "COMPETITORS · PRODUTO do concorrente na atividade",
            "COMPETITORS · CONTEUDO TECNICO do concorrente (nao publicidade)",
            "COMPETITORS · REGIAO da atividade do concorrente",
            "FUTURE · MUDANCA DE POLITICA em consulta"],
  AMBITO="Emilia-Romagna como sede; o conteudo e' NACIONAL", TERR=["T4", "T9", "T11"],
  RECORRENCIA="MEDIUM — anual, mas com data fixa e programa publicado",
  CLASSE="A",
  EVIDENCIA=f"{BUSCA}: quatro produtos de quatro empresas concorrentes, com "
            "substancia ativa e cultura, lidos no programa do convegno — "
            "mais dois aprofundamentos (Decreto Omnibus para biocontrolo, "
            "por Alessandra Moccia/IBMA; medidas de mitigacao para "
            "artropodes nao alvo, por Maria Rita Rapagnani/Ministero)",
  LIMITE="uma vez por ano. Nao substitui vigilancia continua da base oficial; "
         "serve para ler INTENCAO comercial, que a base nao mostra."),
]

# ─────────────────────────────────────────────────────────────────────────────
# GAP 7 · FUTURE · PRIMEIRA DETECAO E PIPELINE REGULATORIO  (CRITICAL / HIGH)
# ─────────────────────────────────────────────────────────────────────────────
FUTURO = [
 dict(
  NOME="Protezione delle Piante — Emergenze, Sorveglianza, Barriere",
  DONO="Servizio Fitosanitario Nazionale (MASAF)",
  URL="https://www.protezionedellepiante.it/",
  PRODUZ="declaracao oficial de PRIMEIRA DETECAO de organismo nocivo, "
         "vigilancia (Piano Nazionale di Indagine) e barreiras fitossanitarias",
  EXEMPLO_REAL="secoes nomeadas «Emergenze Fitosanitarie», «Sorveglianza», "
               "«Barriere Fitosanitarie»; o Servizio Fitosanitario Centrale e' "
               "chefiado por Bruno Faraglia; laboratorios «Custos Plantis»",
  ALIMENTA=["FUTURE · PRAGA OU DOENCA EMERGENTE (primeira deteccao)",
            "FUTURE · Sinal novo com o que se observou e quem o disse",
            "WINDOWS · ATO REGULATORIO regional que abre/fecha a janela"],
  AMBITO="NACIONAL, com regiao na declaracao", TERR=["T3", "T9"],
  RECORRENCIA="HIGH — por evento, e evento ha sempre",
  CLASSE="A",
  EVIDENCIA=f"{BUSCA}: as tres secoes e o nome do responsavel do servico "
            "central foram lidos na propria estrutura do sitio",
  LIMITE="primeira detecao e' evento raro por definicao. Serie curta, valor "
         "alto — o contrario de um boletim semanal."),
 dict(
  NOME="Salute delle piante in Lombardia · app Fitodetective",
  DONO="Regione Lombardia — Servizio Fitosanitario regionale",
  URL="https://www.salutepianteinlombardia.it/",
  PRODUZ="alerta regional de organismo nocivo e canal de reporte cidadao "
         "(app) que gera observacao georreferenciada",
  EXEMPLO_REAL="portal regional dedicado mais a app Fitodetective",
  ALIMENTA=["FUTURE · PRAGA OU DOENCA EMERGENTE (primeira deteccao)",
            "VOICES · REGIAO da voz de campo"],
  AMBITO="Lombardia", TERR=["T3"],
  RECORRENCIA="MEDIUM — por evento",
  CLASSE="B",
  EVIDENCIA=f"{BUSCA}: portal e app identificados",
  LIMITE="reporte de cidadao nao e' diagnostico. Sem confirmacao do servico, "
         "e' suspeita — e suspeita nao e' primeira detecao."),
 dict(
  NOME="EU Pesticides Database + registo de conclusoes de peer review",
  DONO="Comissao Europeia (DG SANTE) e EFSA",
  URL="https://food.ec.europa.eu/plants/pesticides/eu-pesticides-database_en",
  PRODUZ="substancias ativas aprovadas com DATA DE EXPIRACAO (anexo do Reg. "
         "UE 540/2011) e o estado da avaliacao/renovacao de cada uma",
  EXEMPLO_REAL="Reg. (CE) 1107/2009 art. 15: o pedido de renovacao entra TRES "
               "ANOS antes de expirar — e' esse prazo que torna a base um "
               "sinal de futuro, e nao um registo do presente",
  ALIMENTA=["FUTURE · PIPELINE REGULATORIO (substancia em avaliacao/renovacao)",
            "PORTFOLIO · Substancia ativa do produto",
            "FUTURE · MUDANCA DE POLITICA em consulta"],
  AMBITO="EUROPEU — vale para Italia por via da UE", TERR=["T4", "T9"],
  RECORRENCIA="HIGH — continua",
  CLASSE="A",
  EVIDENCIA=f"{BUSCA}: artigo 15 do 1107/2009 e o anexo do 540/2011 "
            "identificados como o par que da a lista e o prazo",
  LIMITE="⚠️ DUAS COISAS QUE NAO SE MISTURAM: substancia ativa aprovada na UE "
         "≠ produto autorizado em Italia. A mesma substancia pode estar "
         "aprovada e nao ter produto nacional. E ⚠️ O PRAZO MUDOU: o pacote "
         "Omnibus altera o art. 43 — pedido de renovacao de AUTORIZACAO "
         "passa a ate 9 meses antes de expirar (3 meses se a substancia "
         "tiver aprovacao limitada). Quem calcular pela regra antiga erra a "
         "data."),
]

# ─────────────────────────────────────────────────────────────────────────────
# GAP 8 · FUTURE/WINDOWS · SERIE CLIMATICA E ANOMALIA  (HIGH)
# ─────────────────────────────────────────────────────────────────────────────
CLIMA = [
 dict(
  NOME="SCIA — Sistema nazionale per l'elaborazione e diffusione di dati climatici",
  DONO="ISPRA",
  URL="https://scia.isprambiente.it/dati-e-indicatori/",
  PRODUZ="indicadores climaticos por ESTACAO, com descarga de serie temporal "
         "ao passo dia/decada/mes/ano, mais analise interpolada em grelha — "
         "e inclui GRAUS-DIA",
  EXEMPLO_REAL="tres funcoes declaradas: STAZIONI (mapa e metadados), SERIE "
               "TEMPORALI (extrair e descarregar serie por estacao e passo), "
               "ANALISI (distribuicao espacial interpolada, com descarga da "
               "grelha)",
  ALIMENTA=["FUTURE · DESLOCACAO CLIMATICA que muda a pressao de praga",
            "WINDOWS · Desvio fenologico por regiao (a mesma cultura adianta/atrasa)",
            "MARKET · Condicao de cultura / meteo agregado para mercado"],
  AMBITO="NACIONAL — agrega as redes regionais", TERR=["T2"],
  RECORRENCIA="HIGH — serie continua",
  CLASSE="A",
  EVIDENCIA=f"{BUSCA}: as tres funcoes e a presenca de graus-dia entre os "
            "indicadores estao descritas na propria pagina do SCIA",
  LIMITE="descarga por interface, nao API REST documentada. Automatizar "
         "exige trabalho, e esse trabalho nao esta feito."),
 dict(
  NOME="ERG5 e o indicador «Anomalia della sommatoria gradi giorno»",
  DONO="Arpae Emilia-Romagna",
  URL="https://webbook.arpae.it/clima/",
  PRODUZ="o DESVIO da soma termica acumulada face a media de referencia — "
         "exatamente a forma «anomalia», nao o valor bruto",
  EXEMPLO_REAL="«Anomalia della sommatoria gradi giorno per colture "
               "primaverili-estive»: desvio da disponibilidade termica "
               "acumulada desde 1 de janeiro (limiar 10 °C) face a media "
               "2001–2020; rede RIRER, interpolacao PRAGA, grelha 5×5 km, "
               "cobertura 1961–2023",
  ALIMENTA=["FUTURE · DESLOCACAO CLIMATICA que muda a pressao de praga",
            "WINDOWS · Desvio fenologico por regiao (a mesma cultura adianta/atrasa)"],
  AMBITO="Emilia-Romagna, em grelha de 5 km", TERR=["T2"],
  RECORRENCIA="HIGH — semanal (mapas) sobre serie de 1961",
  CLASSE="A",
  EVIDENCIA=f"{BUSCA}: limiar, periodo de referencia, rede, metodo de "
            "interpolacao, resolucao e cobertura todos declarados",
  LIMITE="uma regiao. O metodo e' o modelo a copiar; a cobertura nao e'."),
 dict(
  NOME="Banca Dati Storica meteo-idro-nivologica",
  DONO="Arpa Piemonte",
  URL="https://www.arpa.piemonte.it/dato/banca-dati-storica-dati-giornalieri-mensili",
  PRODUZ="serie diaria e mensal de todas as estacoes da rede regional desde "
         "o inicio dos sensores: temperatura, precipitacao, humidade "
         "relativa, radiacao, vento",
  EXEMPLO_REAL="inclui as Series Centenarias — Torino-centro desde 1753, "
               "Moncalieri desde 1866",
  ALIMENTA=["FUTURE · DESLOCACAO CLIMATICA que muda a pressao de praga",
            "MARKET · Condicao de cultura / meteo agregado para mercado"],
  AMBITO="Piemonte", TERR=["T2"],
  RECORRENCIA="HIGH — diaria",
  CLASSE="A",
  EVIDENCIA=f"{BUSCA}: variaveis e series centenarias declaradas na pagina",
  LIMITE="serie longa nao e' serie homogenea. Comparar 1753 com 2026 exige "
         "correcao que nao vem feita."),
 dict(
  NOME="Rete agrometeorologica regionale (archivio dati)",
  DONO="Regione Campania — Assessorato Agricoltura",
  URL="https://agricoltura.regione.campania.it/meteo/archivio_meteo.html",
  PRODUZ="dado diario de temperatura, humidade e chuva, MAIS parametros "
         "agrometeorologicos: MOLHA FOLIAR e humidade do solo, em Excel",
  EXEMPLO_REAL="descarga declarada em formato Excel, com bagnatura fogliare "
               "entre os parametros",
  ALIMENTA=["WINDOWS · Janela de monitorizacao (quando ir olhar)",
            "FUTURE · DESLOCACAO CLIMATICA que muda a pressao de praga"],
  AMBITO="Campania", TERR=["T2", "T3"],
  RECORRENCIA="HIGH — diaria",
  CLASSE="A",
  EVIDENCIA=f"{BUSCA}: a molha foliar e' o parametro que liga clima a risco "
            "de doenca, e esta declarada como descarregavel",
  LIMITE="Excel por interface. E a memoria do projeto ja registou o mesmo "
         "parametro na ARPAV por API REST sem chave — a ARPAV e' a rota mais "
         "facil para o mesmo tipo de dado."),
]

# ─────────────────────────────────────────────────────────────────────────────
# GAP 9 · SCIENCE · LOCAL, METODO, RESULTADO, ENSAIO DE CAMPO  (HIGH)
# ─────────────────────────────────────────────────────────────────────────────
CIENCIA = [
 dict(
  NOME="Giornate Fitopatologiche — atti e programma",
  DONO="Comitato delle Giornate Fitopatologiche (universidades italianas)",
  URL="https://giornatefitopatologiche.it/",
  PRODUZ="comunicacoes com LOCAL do ensaio, metodo, tese comparada e "
         "resultado de eficacia — a literatura divulgavel de ensaio de campo "
         "italiano",
  EXEMPLO_REAL="edicao 2026, 19–20 de marco, com programa por sessao: "
               "«Agrofarmaci, salute, ambiente» (19/03, 8h45), «Applicazione "
               "dei mezzi di difesa» (10h30), «Difesa dalle malattie» (tarde "
               "de 19 e manha de 20, encerramento as 13h30); inclui "
               "contribuicoes de empresa, ex. Matteo Colombo (European "
               "Precision Application Task Force, por Corteva Italia)",
  ALIMENTA=["SCIENCE · LOCAL DO ESTUDO (onde o ensaio foi feito)",
            "SCIENCE · METODO e RESULTADO medido (eficacia)",
            "SCIENCE · ENSAIO DE CAMPO / trial com resultado",
            "SCIENCE · Cultura e problema do trabalho",
            "COMPETITORS · CONTEUDO TECNICO do concorrente (nao publicidade)"],
  AMBITO="NACIONAL", TERR=["T5", "T11"],
  RECORRENCIA="MEDIUM — bienal/anual, com atas publicadas",
  CLASSE="A",
  EVIDENCIA=f"{BUSCA}: programa datado com sessoes e horas, e um autor de "
            "empresa nomeado com a sua filiacao",
  LIMITE="atas sao evento, nao fluxo. Entre edicoes, silencio."),
 dict(
  NOME="Centri di saggio con certificazione GEP",
  DONO="privados: Agrea (agrea.it), Sagea (sagea.com), AgriSearch "
       "(agrisearch-innovations.com), Agro Services "
       "(agroservicesperimentazione.com), Agritec (agritecsrl.it), "
       "Repros (repros.vi.it)",
  URL="https://www.agrea.it/",
  PRODUZ="ensaio oficial de eficacia e residuos para registo de produto, sob "
         "Good Experimental Practice",
  EXEMPLO_REAL="seis centros de saggio italianos identificados, com "
               "certificacao GEP declarada",
  ALIMENTA=["SCIENCE · ENSAIO DE CAMPO / trial com resultado",
            "COMPETITORS · PESSOA do concorrente (quem fala por ele)"],
  AMBITO="NACIONAL", TERR=["T5", "T8"],
  RECORRENCIA="LOW — para efeito de publicacao",
  CLASSE="REJECT_COMO_FONTE_DE_DADO",
  EVIDENCIA=f"{BUSCA}: a busca estabeleceu que os dados das provas GEP de "
            "registo sao RESERVADOS, propriedade da empresa que as encomenda, "
            "e NAO SAO PUBLICADOS",
  LIMITE="⚠️ ISTO NAO E' UM GAP DE FONTE — E' UM GAP DE ACESSO. Nenhuma "
         "coleta resolve: o dado existe, tem dono, e o dono nao publica. A "
         "via para ter resultado de ensaio e' contratual, nao tecnica. Estes "
         "seis ficam no acervo como REDE DE PESSOAS (T8), nao como fonte de "
         "resultado. O caminho divulgavel e': boletins e provas "
         "demonstrativas dos servicos regionais, atas das Giornate "
         "Fitopatologiche e da AIPP/SIPaV, e a base de rotulos do Ministerio."),
]

# ─────────────────────────────────────────────────────────────────────────────
# GAP 10 · COMPETITORS · REGIAO DA ATIVIDADE  (HIGH — so 2 donos no acervo)
# ─────────────────────────────────────────────────────────────────────────────
CONCORRENTES = [
 dict(
  NOME="AgriEvents — calendario di eventi tecnici regionali",
  DONO="Regione Emilia-Romagna",
  URL="https://agricoltura.regione.emilia-romagna.it/fitosanitario/eventi/",
  PRODUZ="calendario com inscricao dos eventos do Settore Fitosanitario, "
         "onde as empresas apresentam",
  EXEMPLO_REAL="portal usado para inscricao presencial e web nos eventos do "
               "setor; alberga as Giornate Fitopatologiche 2026 e o convegno "
               "de novidades",
  ALIMENTA=["COMPETITORS · REGIAO da atividade do concorrente",
            "COMPETITORS · CONTEUDO TECNICO do concorrente (nao publicidade)"],
  AMBITO="Emilia-Romagna", TERR=["T11", "T8"],
  RECORRENCIA="HIGH — calendario vivo",
  CLASSE="A",
  EVIDENCIA=f"{BUSCA}: o portal e' nomeado como o canal de inscricao dos "
            "eventos do servico fitossanitario regional",
  LIMITE="uma regiao. ⚠️ E A BUSCA ESTABELECEU QUE NAO EXISTE calendario "
         "unico nacional de jornadas demonstrativas regiao a regiao. Para "
         "Bayer, Corteva e BASF, o calendario esta no sitio de cada uma — "
         "ou seja: cobertura nacional de atividade de concorrente exige "
         "vigiar N sitios, nao um."),
 dict(
  NOME="Demo Days e open day de sementes horticolas",
  DONO="Syngenta Italia / Syngenta Vegetable Seeds",
  URL="https://www.syngentavegetables.com/it-it/open-day/demo-days-colture-foglia-e-brassicacee-2026",
  PRODUZ="anuncio de demonstracao em campo, com cultura e data",
  EXEMPLO_REAL="«Demo Days Colture a Foglia e Brassicacee 2026», com registo",
  ALIMENTA=["COMPETITORS · REGIAO da atividade do concorrente",
            "COMPETITORS · PRODUTO do concorrente na atividade",
            "COMPETITORS · CULTURA da atividade do concorrente"],
  AMBITO="NACIONAL, por evento", TERR=["T8", "T11"],
  RECORRENCIA="MEDIUM — sazonal",
  CLASSE="B",
  EVIDENCIA=f"{BUSCA}: evento nomeado com ano e cultura",
  LIMITE="⚠️ EXIGE REGISTO, e e' comunicacao da propria empresa. Isto e' "
         "atividade publica declarada, nao informacao independente."),
 dict(
  NOME="Catalogo annuale di gamma",
  DONO="Syngenta Italia",
  URL="https://www.syngenta.it/catalogo-syngenta-2026-le-persone-al-centro",
  PRODUZ="gama declarada do ano: agrofarmacos, sementes e nutricao",
  EXEMPLO_REAL="«Catalogo Syngenta 2026»",
  ALIMENTA=["COMPETITORS · PRODUTO do concorrente na atividade"],
  AMBITO="NACIONAL", TERR=["T8"],
  RECORRENCIA="MEDIUM — anual",
  CLASSE="B",
  EVIDENCIA=f"{BUSCA}: catalogo do ano identificado",
  LIMITE="material comercial do proprio. Diz o que a empresa quer dizer."),
]

# ─────────────────────────────────────────────────────────────────────────────
# GAP 11 · VOICES · REGIAO, PAPEL E DATA  (CRITICAL x3)
# ─────────────────────────────────────────────────────────────────────────────
# O achado desta busca vira a resposta do avesso, e vale escrever inteiro:
# o gap de VOICES nao se enche com MAIS canais sociais. Enche-se com canais
# onde a REGIAO, o PAPEL e a DATA estao escritos — e isso, em Italia, e' o
# sistema de boletim tecnico assinado, nao a rede social.
VOZES = [
 dict(
  NOME="Federazioni e Ordini dei Dottori Agronomi e Forestali",
  DONO="CONAF e as federacoes regionais",
  URL="https://www.conaf.it/",
  PRODUZ="o ALBO: nome, PAPEL profissional reconhecido e TERRITORIO de "
         "inscricao — os tres campos que faltam as 17 vozes do casco",
  EXEMPLO_REAL="a missao anterior ja mediu uma federacao que vai mais longe "
               "e PRODUZ boletim: `agronomiforestaliumbria.it` publica "
               "boletins fitossanitarios de olivo e vite",
  ALIMENTA=["VOICES · PAPEL de quem fala (produtor? tecnico? amador?)",
            "VOICES · REGIAO da voz de campo",
            "FIELD_NET · Identidade do tecnico de campo (TSR)"],
  AMBITO="NACIONAL, por federacao regional", TERR=["T8"],
  RECORRENCIA="HIGH — o albo e' mantido",
  CLASSE="A",
  EVIDENCIA=f"{BUSCA}: a busca por «agronomo que publica boletim proprio» "
            "devolveu esta conclusao explicita — NAO EXISTE albo nem lista "
            "central de agronomos liberais que publiquem boletim proprio; "
            "sao iniciativas fragmentadas por estudio. O albo da o papel e "
            "o territorio; o boletim, quando existe, e' de cada um",
  LIMITE="⚠️ O ALBO NAO E' UMA FONTE DE OBSERVACAO DE CAMPO. Da o papel e a "
         "regiao de QUEM fala. Nao da o que foi visto nem quando. Serve "
         "para ENRIQUECER uma voz, nao para a criar."),
 dict(
  NOME="Boletim tecnico assinado como portador de regiao+papel+data",
  DONO="padrao observado em: ARSAC (Calabria), CAAR (Liguria), LaMMA "
       "(Toscana), Condifesa TVB (Veneto), Consorzi Fitosanitari (Emilia)",
  URL="https://www.agriligurianet.it/it/impresa/assistenza-tecnica-e-centri-serivizio/agrometeo-caar/bollettino-di-viticoltura.html",
  PRODUZ="o cabecalho padrao que resolve os tres gaps de VOICES ao mesmo "
         "tempo: «nome do boletim – culturas – ZONA homogenea – numero "
         "progressivo – DATA/periodo de validade», assinado por um servico "
         "com PAPEL declarado",
  EXEMPLO_REAL="ARSAC: «valido dal 25 agosto al 1 settembre 2026» + 8 zonas "
               "nomeadas. CAAR: «Olivo n. 03 – 19 marzo», versoes GE/IM/SP/SV",
  ALIMENTA=["VOICES · REGIAO da voz de campo",
            "VOICES · PAPEL de quem fala (produtor? tecnico? amador?)",
            "VOICES · DATA da observacao de campo",
            "VOICES · CANAL com exemplo real e data de publicacao",
            "RADAR · ENTRADA: voz de campo na mesma cultura/problema"],
  AMBITO="regional, replicavel nas 20 regioes", TERR=["T1", "T3", "T8"],
  RECORRENCIA="HIGH — semanal na campanha",
  CLASSE="A",
  EVIDENCIA=f"{BUSCA}: duas series independentes (Calabria e Liguria) com o "
            "MESMO formato de cabecalho — zona + numero + data. Nao e' "
            "excecao de uma regiao: e' o padrao do sistema italiano",
  LIMITE="⚠️ ISTO NAO E' «VOZ DE CAMPO» NO SENTIDO DE AGRICULTOR A FALAR. E' "
         "TECNICO INSTITUCIONAL. Se a ferramenta VOICES quer a palavra de "
         "quem cultiva, isto nao a substitui — enche tres colunas, nao a "
         "quarta. O gap de voz de PRODUTOR com regiao e data continua "
         "aberto, e a busca nao achou fonte recorrente para ele."),
]

# ─────────────────────────────────────────────────────────────────────────────
# ROTAS MORTAS — achado de manutencao que a missao nao procurava
# ─────────────────────────────────────────────────────────────────────────────
ROTAS_MORTAS = [
 dict(ROTA="https://www.coeweb.istat.it/",
      ESTADO="ENCERRADA em 30/09/2025",
      SUBSTITUTA="https://esploradati.istat.it/coeweb",
      PORQUE_IMPORTA="o acervo aponta para ca. Uma rota encerrada raramente "
                     "devolve erro limpo: devolve pagina. Coleta silenciosa "
                     "de nada e' pior do que coleta falhada."),
 dict(ROTA="indice ISMEA dos mezzi correnti — serie mensal",
      ESTADO="QUEBRA DE SERIE a partir de 01/2025 (rede de recolha revista)",
      SUBSTITUTA="mesma rota; mudam as regras de comparacao",
      PORQUE_IMPORTA="o dado nao morreu: a COMPARACAO morreu. Variacao "
                     "2024→2025 lida como real e' um artefacto de metodo. E "
                     "a base muda para 2020 em 01/01/2026."),
]

TODAS = (FENOLOGIA + PRODUCAO + COMERCIO + CUSTOS + STOCKS + PORTFOLIO
         + FUTURO + CLIMA + CIENCIA + CONCORRENTES + VOZES)


def _validar():
    """Nenhum territorio inventado, nenhuma necessidade orfa."""
    from italy_gap_needs import NECESSIDADES
    validas = {f'{n["TOOL"]} · {n["RAW_NEED"]}' for n in NECESSIDADES}
    erros = []
    for f in TODAS:
        for c in f["TERR"]:
            if not _T.valido(c):
                erros.append(f'{f["NOME"][:40]}: territorio {c} nao existe')
        for a in f["ALIMENTA"]:
            if a not in validas:
                erros.append(f'{f["NOME"][:40]}: necessidade orfa «{a}»')
        faltam = [k for k in ("NOME", "DONO", "URL", "PRODUZ", "EXEMPLO_REAL",
                              "ALIMENTA", "AMBITO", "RECORRENCIA", "EVIDENCIA")
                  if not f.get(k)]
        if faltam and f["CLASSE"] == "A":
            erros.append(f'{f["NOME"][:40]}: classe A sem {faltam}')
    return erros


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    erros = _validar()
    print(f"FONTES NOVAS = {len(TODAS)}")
    from collections import Counter
    print("  classe:", dict(Counter(f["CLASSE"] for f in TODAS)))
    print("  ligacoes fonte→necessidade:", sum(len(f["ALIMENTA"]) for f in TODAS))
    print("  necessidades distintas tocadas:",
          len({a for f in TODAS for a in f["ALIMENTA"]}))
    print("  rotas mortas:", len(ROTAS_MORTAS))
    if erros:
        print(f"\n!! {len(erros)} PROBLEMAS:")
        for e in erros:
            print("   ", e)
        sys.exit(1)
    print("\nVALIDACAO OK — nenhum territorio inventado, nenhuma necessidade orfa")
