#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DIARIO DAS BUSCAS — cada consulta parte de um GAP MEDIDO, nunca de um tema.

A regra da missao: nao «buscar fontes agricolas da Sicilia», mas «Sicilia +
vite + bollettino fitosanitario + fenologia». A consulta tem de refletir a
materia-prima que falta, senao devolve fonte bonita que nao enche campo.

A COLUNA MAIS UTIL E' A ULTIMA
------------------------------
`VIROU` guarda as buscas que mudaram a RESPOSTA em vez de acrescentarem fonte.
Foram quatro, e valem mais do que as outras dez juntas:
  · a prova GEP e' reservada por lei  -> o gap de ensaio nao e' de fonte
  · o Coeweb fechou em 30/09/2025     -> o acervo aponta para uma rota morta
  · o indice ISMEA quebrou em 01/2025 -> a serie nao se compara com o ano antes
  · nao existe lista de agronomos que publiquem boletim proprio
                                       -> o gap de VOICES nao se enche com
                                          mais canais sociais
"""

BUSCAS = [
 dict(GAP="WINDOWS · FASE FENOLOGICA (CROP_STAGE 0/29)",
      CONSULTA="bollettino fenologico Italia BBCH fase fenologica cultura "
               "regione settimanale",
      DEVOLVEU="boletim nacional de fenologia da Rete Rurale Nazionale, com "
               "BBCH, alimentado por modelo + MeteoHub/CINECA + observadores "
               "voluntarios",
      FONTES="Bollettino Nazionale di Fenologia (RRN)",
      VIROU=""),
 dict(GAP="WINDOWS · FASE FENOLOGICA, ao nivel regional",
      CONSULTA="Veneto vite bollettino fitosanitario fenologia BBCH vitigno "
               "2026",
      DEVOLVEU="boletins viticolos do Servizio Fitosanitario do Veneto, com "
               "BBCH por vitigno e separacao ambiente precoce/tardio; e a "
               "ligacao as janelas obrigatorias da flavescencia dourada",
      FONTES="Bollettini viticoli Veneto · ARPAV bollettino agrometeorologico",
      VIROU=""),
 dict(GAP="WINDOWS · OBSERVACAO DE CAMPO e desvio fenologico por regiao",
      CONSULTA="Marche Abruzzo notiziario agrometeorologico melo pero vite "
               "stadio fenologico ritardo altitudine costa",
      DEVOLVEU="notiziario das Marche com codigo BBCH numerico (melo 75-77, "
               "pero 76-81, vite 79); e o AgroAmbiente do Abruzzo a "
               "quantificar ~2 semanas de atraso acima de 400 m ou a mais de "
               "40 km da costa",
      FONTES="Notiziario Marche · Abruzzo AgroAmbiente",
      VIROU="o desvio fenologico por regiao existe QUANTIFICADO, nao "
            "apenas descrito — e' materia-prima, nao comentario"),
 dict(GAP="MARKET · PRODUCAO, AREA e RENDIMENTO (coluna ausente)",
      CONSULTA="ISTAT coltivazioni superficie produzione resa per regione "
               "provincia dataflow SDMX API",
      DEVOLVEU="dataflow DCSP_COLTIVAZIONI com API SDMX, estimativas mensais "
               "por regiao, provincia e zona altimetrica; e a declaracao de "
               "que arroz vem do Enterisi, tabaco da Agea, beterraba da ABSI",
      FONTES="ISTAT DCSP_COLTIVAZIONI · statistica.regione.emilia-romagna.it",
      VIROU="parte do dado 'oficial' e' de terceiros declarados. A "
            "procedencia tem de viajar com o numero"),
 dict(GAP="PORTFOLIO · INTERVALO DE SEGURANCA (15/219) e maxApp (0/219)",
      CONSULTA="banca dati prodotti fitosanitari tempo di carenza dose "
               "ricerca per intervallo di sicurezza Italia",
      DEVOLVEU="base do Ministero della Salute (~16.500 produtos, atualizacao "
               "diaria, descarga integral) — mas carencia e dose vivem no PDF "
               "do rotulo; e o Fitogest, que permite FILTRAR por tempo di "
               "carenza",
      FONTES="fitosanitari.salute.gov.it · Fitogest · profitosan.it",
      VIROU="o gap de carencia nao e' de fonte, e' de EXTRACAO — o campo "
            "esta dentro de um documento que a casa ja sabe abrir"),
 dict(GAP="FUTURE · PRAGA OU DOENCA EMERGENTE (campo ausente)",
      CONSULTA="servizio fitosanitario nazionale prima segnalazione organismo "
               "nocivo emergenza fitosanitaria sorveglianza Italia",
      DEVOLVEU="protezionedellepiante.it com secoes Emergenze Fitosanitarie, "
               "Sorveglianza e Barriere; Piano Nazionale di Indagine; "
               "laboratorios «Custos Plantis»; Bruno Faraglia a chefiar o "
               "Servizio Fitosanitario Centrale",
      FONTES="protezionedellepiante.it · masaf.gov.it · "
             "salutepianteinlombardia.it · app Fitodetective",
      VIROU=""),
 dict(GAP="MARKET · IMPORTACAO e EXPORTACAO",
      CONSULTA="ISTAT Coeweb commercio estero agroalimentare dati per "
               "provincia esportazione importazione",
      DEVOLVEU="o Coeweb antigo FECHOU em 30/09/2025 e passou para "
               "esploradati.istat.it/coeweb; e a base do ISMEA, reclassificada "
               "por comparto agricola, com 4 vistas e exportacao xls/csv/pdf",
      FONTES="esploradati.istat.it/coeweb · ismeamercati.it commercio estero",
      VIROU="⚠️ O ACERVO APONTA PARA UMA ROTA MORTA. Rota encerrada "
            "devolve pagina, nao erro — a coleta 'funciona' e traz nada"),
 dict(GAP="MARKET · CUSTO DE INSUMO",
      CONSULTA="ISMEA indice prezzi mezzi correnti di produzione "
               "fertilizzanti fitosanitari costi medi di produzione serie",
      DEVOLVEU="indice mensal desde 1984, ~6.000 precos/semana em 600 "
               "referencias, 300 leituras mensais em 12 consorzi agrari; e o "
               "servico separado de custos medios de producao, com registo",
      FONTES="ISMEA indice mezzi correnti · ISMEA monitoraggio costi",
      VIROU="⚠️ A REDE FOI REVISTA EM 01/2025: os indices mensais deixam "
            "de ser comparaveis com o ano anterior, e a base passa a 2020 "
            "em 01/01/2026. A variacao 2024→2025 e' artefacto de metodo"),
 dict(GAP="FUTURE · PIPELINE REGULATORIO (automatico dizia NO_SOURCE)",
      CONSULTA="EFSA rinnovo sostanza attiva scadenza approvazione "
               "regolamento 1107/2009 art. 15 elenco UE 540/2011",
      DEVOLVEU="EU Pesticides Database mais o registo de conclusoes de peer "
               "review da EFSA; e o mecanismo legal que os torna previsao — "
               "pedido de renovacao tres anos antes de expirar",
      FONTES="EU Pesticides Database + EFSA peer review",
      VIROU="⚠️ O PRAZO MUDOU: o pacote Omnibus altera o art. 43 — pedido "
            "de renovacao de AUTORIZACAO passa a ate 9 meses antes de "
            "expirar, 3 meses se a aprovacao for limitada"),
 dict(GAP="SCIENCE · ENSAIO DE CAMPO com resultado",
      CONSULTA="centri di saggio GEP Italia prove di efficacia agrofarmaci "
               "risultati pubblicati",
      DEVOLVEU="seis centros de saggio GEP italianos (Agrea, Sagea, "
               "AgriSearch, Agro Services, Agritec, Repros) — e a informacao "
               "de que os dados das provas de registo sao RESERVADOS, "
               "propriedade de quem as encomenda, e nao sao publicados",
      FONTES="nenhuma como fonte de dado; os seis entram como REDE DE PESSOAS",
      VIROU="⚠️ O ACHADO MAIS DURO: ISTO NAO E' GAP DE FONTE, E' GAP DE "
            "ACESSO. Nenhuma coleta o resolve; resolve-se por contrato. O "
            "divulgavel sao provas demonstrativas regionais e atas"),
 dict(GAP="VOICES · REGIAO, PAPEL e DATA (0/17 em cada)",
      CONSULTA="agronomo libero professionista Italia bollettino tecnico "
               "proprio zona viticola olivicola settimanale con data",
      DEVOLVEU="ARSAC Calabria com 8 areas climaticamente homogeneas e "
               "validade semanal datada; CAAR Liguria com BBCH de olivo, "
               "numeracao progressiva e versao por provincia; LaMMA por "
               "provincia; Agralia como unico privado com boletim proprio",
      FONTES="ARSAC · CAAR Liguria · LaMMA · Agralia · Terre dell'Etruria · "
             "Consorzi Fitosanitari MO e RE",
      VIROU="⚠️ NAO EXISTE ALBO NEM LISTA CENTRAL de agronomos liberais "
            "que publiquem boletim proprio — sao iniciativas por estudio. E "
            "o que enche regiao+papel+data e' o BOLETIM TECNICO ASSINADO, "
            "que e' voz de tecnico institucional, nao de produtor. O gap de "
            "VOICES nao se enche com mais canais sociais"),
 dict(GAP="FUTURE/WINDOWS · serie climatica e anomalia",
      CONSULTA="serie climatica agrometeorologica Italia dati storici "
               "stazioni gradi giorno anomalia regionale scaricabili API",
      DEVOLVEU="SCIA/ISPRA com STAZIONI, SERIE TEMPORALI e ANALISI, incluindo "
               "graus-dia; Arpae ERG5 com «Anomalia della sommatoria gradi "
               "giorno» (limiar 10 °C, media 2001-2020, grelha 5 km, "
               "1961-2023); Arpa Piemonte com series centenarias; Campania "
               "com molha foliar em Excel",
      FONTES="SCIA/ISPRA · Arpae ERG5 · Arpa Piemonte · Campania agrometeo",
      VIROU="o Arpae publica o DESVIO, nao o valor bruto — e' exatamente a "
            "forma que a pergunta pedia, e e' um metodo a copiar"),
 dict(GAP="MARKET · STOCKS / existencias",
      CONSULTA="ISMEA giacenze magazzino cereali vino olio Italia rilevazione "
               "periodica dati regione",
      DEVOLVEU="o ISMEA NAO faz recolha periodica de existencias por regiao. "
               "O que tem e' o censo de estruturas de armazenamento de "
               "cereais (~1.200 centros, >11 Mt, 55% silos / 45% armazem) e a "
               "rede Ismea–Unione Seminativi (23 estacoes, questionario a "
               "peritos, resultados declarados PROVISORIOS)",
      FONTES="Cantina Italia (SIAN) · registo telematico do azeite (AGEA) · "
             "censo de armazenamento · rede Ismea–Unione Seminativi",
      VIROU="⚠️ CAPACIDADE NAO E' EXISTENCIA: um silo vazio de 10.000 t "
            "conta igual a um cheio. E a fonte certa para giacenze por "
            "regiao e' a declaracao obrigatoria no registo telematico, nao "
            "uma recolha de mercado"),
 dict(GAP="COMPETITORS · REGIAO da atividade e PESSOA do concorrente "
          "(automatico dizia NO_SOURCE para pessoa)",
      CONSULTA="Italia agrofarmaci giornate tecniche demo campo Syngenta "
               "Bayer Corteva BASF calendario eventi regione 2026 convegni",
      DEVOLVEU="convegno «Prodotti fitosanitari: le novità» (Bolonha, "
               "19/02/2026, >860 tecnicos) onde as proprias empresas "
               "apresentam produto com substancia ativa e cultura; e o Forum "
               "Fitoiatrico do Condifesa TVB, com tecnicos nomeados por "
               "empresa; mais Giornate Fitopatologiche, Macfrut, Agrea/Soave, "
               "Demo Days",
      FONTES="convegno Emilia-Romagna · Forum Fitoiatrico CondifesaTVB · "
             "AgriEvents · Giornate Fitopatologiche · Syngenta Demo Days",
      VIROU="PESSOA do concorrente passou de NO_SOURCE a STRONG: oito "
            "pessoas nomeadas com empresa. ⚠️ Mas NAO EXISTE calendario "
            "unico nacional de jornadas por regiao — cobertura nacional "
            "custa N rotas. E a ADAMA esta na lista do Forum: ler isto como "
            "'concorrente' obriga a excluir a propria casa"),
]

if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    print(f"BUSCAS DIRIGIDAS = {len(BUSCAS)}")
    viraram = [b for b in BUSCAS if b["VIROU"]]
    print(f"  que mudaram a RESPOSTA (nao so acrescentaram fonte): {len(viraram)}")
    for b in viraram:
        print(f"    · {b['GAP'][:52]}")
