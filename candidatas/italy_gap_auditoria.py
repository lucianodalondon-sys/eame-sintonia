#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUDITORIA A MAO das 72 necessidades — o sitio onde a maquina para e eu decido.

POR QUE ISTO EXISTE
-------------------
O casamento automatico prova que a fonte FALA do assunto. Nao prova que ela
ENTREGA o campo. Os exemplos que o automatico produziu e que esta auditoria
derruba, medidos em 14/09/2026:

    FASE FENOLOGICA        <- «Données ouvertes du catalogue E-Phy» (registo
                              frances de fitossanitarios)
    VOZ DE CAMPO no Radar  <- «Centro Veterinario San Martino» (clinica
                              veterinaria)
    MECANISMO DE ACAO      <- «Cassandra Tech – Models for change»
    REGISTO do concorrente <- «CELLAR / EU Publications Office»

Nenhuma destas quatro sobrevive a leitura. Se a folha CURRENT_COVERAGE saisse
com o veredito automatico, a casa concluiria que tem fenologia coberta por um
registo frances de produtos.

O VOCABULARIO, E POR QUE TEM CINCO VALORES E NAO TRES
-----------------------------------------------------
    STRONG                 fonte nomeada publica ESTE campo, com recorrencia
    WEAK                   fonte plausivel, mas nao vi o campo COMO CAMPO
    NO                     procurei e nao achei
    STRONG_MAS_TROCA_A_VOZ ha fonte forte e recorrente, mas ela entrega OUTRA
                           coisa que nao a que a ferramenta pede. Enche a
                           coluna e responde a outra pergunta — e' o erro mais
                           caro de todos, porque parece sucesso
    NAO_E_GAP_DE_FONTE     nenhuma fonte externa resolve: e' join, extracao,
                           identidade interna ou dado proprietario da casa

Sem o quarto valor, a ferramenta VOICES seria declarada resolvida. Ela nao e':
o que se achou foi o boletim tecnico assinado, que traz regiao, papel e data
— mas a voz e' de tecnico institucional, nao de quem cultiva.
"""

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "candidatas"))

# chave = "TOOL · RAW_NEED"  →  (veredito, quem sustenta, porque)
AUDITORIA = {

 # ═══ WINDOWS ═════════════════════════════════════════════════════════════
 "WINDOWS · Cultura e regiao da janela": (
  "STRONG", "ARSAC (8 zonas) · CAAR Liguria (4 provincias) · LaMMA (provincias) "
  "· Servizio Fitosanitario Veneto",
  "quatro produtores independentes publicam cultura E recorte territorial na "
  "mesma linha. O automatico propunha MASAF e um registo espanhol de pragas: "
  "ambos falam de cultura, nenhum entrega a janela."),

 "WINDOWS · Datas de inicio e fim da janela": (
  "STRONG", "ARSAC · CAAR Liguria",
  "os dois escrevem o intervalo no titulo: «valido dal 25 agosto al 1 "
  "settembre 2026» e «Olivo n. 03 – 19 marzo». Data no titulo e' campo, nao "
  "e' interpretacao."),

 "WINDOWS · FASE FENOLOGICA DA CULTURA (o que a planta esta a fazer)": (
  "STRONG", "Bollettino Nazionale di Fenologia (RRN) · Notiziario Marche · "
  "CAAR Liguria · Bollettini viticoli Veneto",
  "quatro fontes com escala BBCH DECLARADA, e uma delas com o codigo numerico "
  "a vista (melo 75-77, pero 76-81, vite 79). Isto enche o `CROP_STAGE` que o "
  "contrato mede em 0 de 29."),

 "WINDOWS · FASE DO PROBLEMA (em que estadio esta a praga/doenca)": (
  "STRONG", "Bollettini viticoli Veneto (stato parassitario) · Consorzi "
  "Fitosanitari de Modena e Reggio Emilia · ARSAC",
  "boletim fitossanitario tem por oficio dizer em que estadio esta a praga. "
  "E' o campo mais bem servido de toda a ferramenta."),

 "WINDOWS · OBSERVACAO DE CAMPO (fase observada, nao esperada)": (
  "STRONG", "CAAR Liguria (olivais representativos da rede regional de "
  "monitorizacao) · Notiziario Marche · Agralia (observacao direta em campo) "
  "· RRN (observadores voluntarios)",
  "o contrato mede 0 de 29 janelas com fase OBSERVADA, e este era o buraco "
  "central da ferramenta. Ha quatro fontes que observam em campo, e duas "
  "dizem-no por escrito. ⚠️ O RRN mistura observacao com MODELO de simulacao: "
  "tem de entrar com a marca de origem, ou o modelo passa por olho."),

 "WINDOWS · Janela de monitorizacao (quando ir olhar)": (
  "STRONG", "Rete agrometeorologica da Campania (molha foliar) · ARPAV (ja no "
  "acervo, API sem chave) · Bollettini Veneto",
  "molha foliar e' o parametro que abre a janela de risco de doenca, e ha duas "
  "redes regionais a publica-lo em serie diaria."),

 "WINDOWS · Janela de controlo de infestantes": (
  "WEAK", "boletins regionais de cereais, sem fonte dedicada identificada",
  "nao fiz busca dirigida a diserbo. O convegno de Bolonha nomeia herbicidas "
  "novos (Boxer Evo, Fencade) mas isso e' produto, nao janela. Declaro o "
  "buraco em vez de o preencher com o que sobra."),

 "WINDOWS · ATO REGULATORIO regional que abre/fecha a janela": (
  "STRONG", "Bollettini viticoli Veneto (janelas dos tratamentos obrigatorios "
  "contra flavescencia dourada) · protezionedellepiante.it (lotta obbligatoria)",
  "a janela obrigatoria e' publicada com data pelo proprio servico que a "
  "impoe. Fonte e autoridade sao a mesma casa — e' o caso mais forte possivel."),

 "WINDOWS · Produto registado ligado a janela": (
  "WEAK", "Banca dati do Ministero (um lado) + boletins (o outro lado)",
  "ha fonte para cultura+alvo do produto e fonte para cultura+problema da "
  "janela. Nao ha fonte que publique a LIGACAO: essa e' trabalho da casa."),

 "WINDOWS · RASTREABILIDADE: que fonte sustenta esta janela": (
  "NAO_E_GAP_DE_FONTE", "—",
  "as 29 janelas canonicas tem `SOURCE_IDS = []`. Isso nao e' falta de fonte: "
  "e' falta de ESCRITA da procedencia. As fontes desta auditoria existem; "
  "ninguem anotou qual sustentou qual janela. Coletar mais nao conserta."),

 "WINDOWS · Area/hectares da cultura por regiao (escala)": (
  "STRONG", "ISTAT dataflow DCSP_COLTIVAZIONI · Eurostat apro_cpshr (ja no acervo)",
  "superficie por regiao, provincia e zona altimetrica, com API SDMX. ⚠️ zona "
  "altimetrica nao e' a zona agronomica do boletim: juntar as duas e' trabalho."),

 "WINDOWS · Desvio fenologico por regiao (a mesma cultura adianta/atrasa)": (
  "STRONG", "Arpae ERG5 «Anomalia della sommatoria gradi giorno» · SCIA/ISPRA "
  "(graus-dia) · Abruzzo AgroAmbiente · LaMMA",
  "o Arpae publica o DESVIO, nao o valor bruto — e' exatamente a forma que a "
  "pergunta pede (limiar 10 °C, media 2001–2020, grelha 5 km). E o Abruzzo "
  "quantifica o desvio geografico: ~2 semanas de atraso acima de 400 m ou a "
  "mais de 40 km da costa. Isso e' o offset por regiao, escrito."),

 # ═══ MARKET ══════════════════════════════════════════════════════════════
 "MARKET · Preco por cultura e por praca": (
  "STRONG", "Borsa merci / CCIAA (ja no acervo)",
  "o unico campo de MARKET que o casco ja tem cheio. Nao precisa de fonte nova."),

 "MARKET · Serie de preco com 3+ pontos (para tendencia)": (
  "WEAK", "arquivos das borse merci · ISMEA Mercati",
  "o preco de hoje esta resolvido; a SERIE exige percorrer arquivo, e isso "
  "nao foi provado em nenhuma rota. Tendencia com um ponto nao e' tendencia."),

 "MARKET · PRODUCAO, AREA e RENDIMENTO por cultura": (
  "STRONG", "ISTAT DCSP_COLTIVAZIONI (via esploradati.istat.it/SDMXWS/rest/)",
  "a coluna esta AUSENTE no casco, e existe fonte oficial com estimativa "
  "mensal e recorte regional. Gap fechavel sem inventar nada. ⚠️ partes vem "
  "de terceiros declarados: arroz do Enterisi, tabaco da Agea, beterraba da "
  "ABSI — a procedencia tem de viajar com o numero."),

 "MARKET · STOCKS / existencias": (
  "WEAK", "Cantina Italia (SIAN/CREA-MASAF, vinho, mensal por regiao) · "
  "registo telematico do azeite (AGEA/SIAN)",
  "identifiquei o DONO certo e corrigi um erro de partida: o ISMEA NAO faz "
  "recolha periodica de existencias por regiao. O que o ISMEA tem e' o censo "
  "de estruturas de armazenamento — ⚠️ CAPACIDADE, nao existencia. Um silo "
  "vazio de 10.000 t conta igual a um cheio. Fica WEAK porque a rota publica "
  "do agregado nao foi fixada."),

 "MARKET · IMPORTACAO e EXPORTACAO": (
  "STRONG", "esploradati.istat.it/coeweb · ISMEA commercio estero agroalimentare",
  "duas rotas, uma oficial e uma reclassificada por comparto agricola. ⚠️ E "
  "UM ACHADO DE MANUTENCAO: o `coeweb.istat.it` do acervo FECHOU em "
  "30/09/2025. Rota encerrada devolve pagina, nao erro."),

 "MARKET · CUSTO DE INSUMO (pressao de custo)": (
  "STRONG", "ISMEA — indice dei prezzi dei mezzi correnti di produzione",
  "serie desde 1984, ~6.000 precos/semana em 600 referencias, mais 300 "
  "leituras mensais em 12 consorzi agrari. ⚠️ E A DESCONTINUIDADE E' PARTE DA "
  "ENTREGA: a rede foi revista em 01/2025 e os indices mensais deixam de ser "
  "comparaveis com o ano anterior; a base passa a 2020 em 01/01/2026. Ler a "
  "variacao 2024→2025 como real e' ler um artefacto de metodo."),

 "MARKET · CLIMA DE CONFIANCA do produtor": (
  "WEAK", "IRES · ISMEA (inqueritos de conjuntura)",
  "o automatico achou um instituto de investigacao social; nao provei que "
  "publique indice de confianca agricola recorrente. Nao inflaciono."),

 "MARKET · Preco para TOMATE, BETERRABA e MACA": (
  "WEAK", "borse merci provinciais · ISMEA por comparto",
  "sei que ha precos; nao provei QUAL praca publica QUAL destas tres com "
  "recorrencia. Tres culturas nomeadas exigem tres provas, e nao as tenho."),

 "MARKET · Serie de preco de UVA/VINHO viva": (
  "WEAK", "ISMEA comparto vino · consorzi de tutela",
  "os consorzi publicam vindima e medidas de oferta (ex. a instancia do "
  "Prosecco DOC no BUR do Veneto), mas isso e' politica de oferta, nao serie "
  "de preco."),

 "MARKET · Condicao de cultura / meteo agregado para mercado": (
  "STRONG", "SCIA/ISPRA · Arpae · Arpa Piemonte · Campania",
  "quatro redes com serie diaria descarregavel e indicadores de seca e "
  "graus-dia. O automatico propunha uma camada de rotulos NUTS: geometria "
  "nao e' meteorologia."),

 # ═══ PORTFOLIO ═══════════════════════════════════════════════════════════
 "PORTFOLIO · Produto, registo e titular": (
  "STRONG", "Banca dati dei prodotti fitosanitari (Ministero della Salute)",
  "~16.500 produtos, atualizacao diaria, conjunto completo descarregavel. "
  "Autoridade e fonte na mesma casa."),

 "PORTFOLIO · Substancia ativa do produto": (
  "STRONG", "Banca dati do Ministero · EU Pesticides Database",
  "⚠️ E OS DOIS NAO SE MISTURAM: substancia aprovada na UE nao e' produto "
  "autorizado em Italia. A mesma substancia pode estar aprovada sem ter "
  "produto nacional — juntar as duas colunas inventa um portfolio."),

 "PORTFOLIO · Cultura e ALVO autorizados por produto": (
  "STRONG", "Banca dati do Ministero",
  "campo do registo oficial."),

 "PORTFOLIO · DOSE autorizada": (
  "WEAK", "rotulo PDF do Ministero · Fitogest",
  "a dose vive no ROTULO, nao na tabela. O projeto ja sabe abrir esses PDF "
  "(memoria: so abrem no urllib). O trabalho e' de EXTRACAO, e extracao de "
  "PDF de rotulo e' missao propria."),

 "PORTFOLIO · INTERVALO DE SEGURANCA (PHI) e n.o maximo de aplicacoes": (
  "STRONG", "Fitogest (banca dati pesquisavel POR TEMPO DI CARENZA)",
  "o contrato mede `interval` em 15/219 (7%) e `maxApp` em 0/219. O Fitogest "
  "permite FILTRAR por tempo di carenza — se filtra, tem o campo. ⚠️ Mas e' "
  "AGREGADOR: se divergir do Ministerio, o Ministerio vence. E o dominio "
  "devolve 403 ao WebFetch e abre ao urllib (ja na memoria do projeto)."),

 "PORTFOLIO · MOMENTO DE APLICACAO / fase da cultura na aplicacao": (
  "WEAK", "rotulo PDF",
  "mesmo problema da dose: esta no documento, nao no campo."),

 "PORTFOLIO · MECANISMO DE ACAO (FRAC/HRAC/IRAC)": (
  "WEAK", "FRAC · HRAC · IRAC (comites internacionais) · SIRFI (ja no acervo) "
  "· Fitogest",
  "⚠️ O DONO DESTE DADO NAO E' ITALIANO: a classificacao e' dos tres comites "
  "internacionais. A busca da Italia nunca o acharia, e o automatico devolveu "
  "«Cassandra Tech – Models for change», que nao tem nada a ver. Fica WEAK "
  "porque a via italiana (SIRFI, Fitogest) e' de segunda mao."),

 "PORTFOLIO · Documento oficial do rotulo (PDF) e a sua data/versao": (
  "STRONG", "Banca dati do Ministero",
  "o rotulo e' servido pelo registo, e o projeto ja provou que o le."),

 "PORTFOLIO · ALTERACAO de autorizacao (o que mudou e quando)": (
  "STRONG", "Banca dati do Ministero (atualizacao diaria, comparavel entre "
  "dias) · convegno «Prodotti fitosanitari: le novità» · AgroNotizie",
  "o campo esta AUSENTE no casco. Duas vias: comparar o descarregavel diario "
  "consigo mesmo (mudanca calculada, com data exata), ou ler o convegno, que "
  "declara a mudanca com intencao comercial — ex. Bayer/Sivanto Prime, "
  "extensoes de emprego em Eriosoma lanigerum e psila da pereira."),

 "PORTFOLIO · AUTORIZACAO EXCECIONAL (art. 53)": (
  "STRONG", "Ministero (deroghe) · convegno de Bolonha",
  "exemplo real com nome: BASF Efficon (dimpropyridaz), uso excecional art. 53 "
  "em fruta, vite e horticolas, apresentado em 19/02/2026."),

 "PORTFOLIO · Ligacao produto x janela de cultura": (
  "NAO_E_GAP_DE_FONTE", "—",
  "`PRODUCT_MATCHES 0/29`. E' um JOIN entre 219 produtos e 29 janelas, ambos "
  "ja em casa. Nenhum italiano publica esta ligacao — e nem devia."),

 # ═══ SCIENCE ═════════════════════════════════════════════════════════════
 "SCIENCE · Trabalho cientifico com identidade": (
  "STRONG", "OpenAlex (ja no acervo, EU-T5-001)", "campo resolvido."),

 "SCIENCE · Autor e instituicao do trabalho": (
  "STRONG", "OpenAlex", "campo resolvido."),

 "SCIENCE · Cultura e problema do trabalho": (
  "STRONG", "OpenAlex · atas das Giornate Fitopatologiche", "campo resolvido."),

 "SCIENCE · LOCAL DO ESTUDO (onde o ensaio foi feito)": (
  "WEAK", "atas das Giornate Fitopatologiche · Versuchszentrum Laimburg · "
  "CRSFA Locorotondo",
  "as atas declaram o local no corpo do texto, nao como campo. Extrair local "
  "de prosa e' leitura, e leitura nao e' coleta."),

 "SCIENCE · METODO e RESULTADO medido (eficacia)": (
  "WEAK", "atas das Giornate Fitopatologiche · provas demonstrativas regionais",
  "idem: existe, esta em prosa."),

 "SCIENCE · RESISTENCIA documentada (especie, mecanismo, regiao, ano)": (
  "WEAK", "SIRFI (area download, ja no acervo) · GIRE",
  "as duas sociedades italianas de resistencia publicam; nao provei que "
  "publiquem os quatro campos juntos."),

 "SCIENCE · ENSAIO DE CAMPO / trial com resultado": (
  "NO", "nenhuma — e a razao e' legal, nao tecnica",
  "⚠️ O ACHADO MAIS DURO DA MISSAO: os seis centros de saggio GEP italianos "
  "(Agrea, Sagea, AgriSearch, Agro Services, Agritec, Repros) fazem ensaio "
  "oficial de eficacia — e os dados sao RESERVADOS, propriedade da empresa "
  "que os encomenda, e NAO SAO PUBLICADOS. Isto nao e' gap de fonte: e' GAP "
  "DE ACESSO. Nenhuma coleta o resolve; resolve-se por contrato. O que e' "
  "divulgavel sao as provas demonstrativas regionais e as atas — que dao "
  "resultado sem dar o ensaio de registo."),

 "SCIENCE · PROJETO de investigacao (quem financia, quem participa)": (
  "WEAK", "innovarurale / Gruppi Operativi PSR · MASAF · Rete PAC",
  "a base dos grupos operativos existe e tem financiador e parceiros; nao "
  "abri nenhuma rota dela nesta missao."),

 # ═══ COMPETITORS ═════════════════════════════════════════════════════════
 "COMPETITORS · Atividade publica do concorrente, com data": (
  "STRONG", "convegno Emilia-Romagna 19/02/2026 · Giornate Fitopatologiche "
  "19–20/03/2026 · Forum Fitoiatrico CondifesaTVB · Macfrut 21/04/2026 · "
  "Agrea/Soave 16/01/2026 · Demo Days Syngenta",
  "seis eventos datados de 2026 em que empresas concorrentes aparecem com "
  "conteudo tecnico. Nao e' publicidade recolhida: e' agenda publica."),

 "COMPETITORS · CULTURA da atividade do concorrente": (
  "STRONG", "convegno de Bolonha",
  "cada novidade vem com as culturas: Boxer Evo para girassol, batata e trigo; "
  "Efficon para fruta, vite e horticolas; Sivanto Prime para macieira e pereira."),

 "COMPETITORS · PROBLEMA/ALVO da atividade do concorrente": (
  "STRONG", "convegno de Bolonha",
  "alvos nomeados a especie: Eriosoma lanigerum e psila da pereira."),

 "COMPETITORS · PRODUTO do concorrente na atividade": (
  "STRONG", "convegno de Bolonha · catalogos anuais das empresas",
  "quatro produtos de quatro concorrentes, com substancia ativa: Boxer Evo "
  "(diflufenican+prosulfocarb, Syngenta), Fencade (pyroxsulam+mesosulfuron, "
  "Corteva), Efficon (dimpropyridaz, BASF), Sivanto Prime (flupyradifurone, "
  "Bayer)."),

 "COMPETITORS · REGIAO da atividade do concorrente": (
  "WEAK", "AgriEvents (Emilia-Romagna) · Forum Fitoiatrico (Treviso-Belluno) "
  "· sitios de cada empresa",
  "⚠️ DUAS RAZOES PARA NAO DIZER STRONG. Primeira: o local do EVENTO nao e' a "
  "regiao da ATIVIDADE comercial — um convegno em Bolonha apresenta produtos "
  "nacionais. Segunda: a busca estabeleceu que NAO EXISTE calendario unico "
  "nacional de jornadas demonstrativas regiao a regiao; para Bayer, Corteva e "
  "BASF ha que vigiar o sitio de cada uma. Cobertura nacional aqui custa N "
  "rotas, nao uma."),

 "COMPETITORS · REGISTO oficial do produto do concorrente": (
  "STRONG", "Banca dati do Ministero (campo «titolare»)",
  "o registo oficial diz de quem e' cada produto. Fonte neutra, nao "
  "declaracao do concorrente."),

 "COMPETITORS · CONTEUDO TECNICO do concorrente (nao publicidade)": (
  "STRONG", "convegno de Bolonha · Giornate Fitopatologiche · Forum Fitoiatrico",
  "apresentacao tecnica em evento de servico publico ou de sociedade "
  "cientifica e' conteudo tecnico por construcao — ex. Matteo Colombo "
  "(European Precision Application Task Force, por Corteva Italia) nas "
  "Giornate."),

 "COMPETITORS · PESSOA do concorrente (quem fala por ele)": (
  "STRONG", "convegno de Bolonha · Forum Fitoiatrico CondifesaTVB",
  "o automatico dizia NO_SOURCE. A busca dirigida devolveu OITO pessoas "
  "nomeadas com empresa: Mattia Fumagalli (Syngenta), Sara Ciofini (Corteva), "
  "Mirko Valente (BASF), Silvano Locardi (Bayer) no convegno; Marco Pravisano "
  "(Syngenta), Marco Grandin (Bayer), Giorgio Fioretti (BASF) no Forum; mais "
  "Alessandra Moccia (IBMA Global). ⚠️ A ADAMA esta na lista de participantes "
  "do Forum: ler isto como «concorrente» obriga a excluir a propria casa."),

 # ═══ VOICES ══════════════════════════════════════════════════════════════
 "VOICES · Voz de campo com autor identificado": (
  "STRONG", "as 17 vozes que o casco ja tem · canais da missao anterior "
  "(ex. Vito Vitelli, agronomo, 306 videos)",
  "campo cheio. ⚠️ E o automatico propunha «Centro Veterinario San Martino» — "
  "uma clinica veterinaria — como voz de campo. Derrubado."),

 "VOICES · REGIAO da voz de campo": (
  "STRONG_MAS_TROCA_A_VOZ", "ARSAC (8 zonas nomeadas) · CAAR (GE/IM/SP/SV) · "
  "LaMMA (por provincia)",
  "0 de 17 vozes tem regiao. Existe fonte forte e recorrente com regiao "
  "escrita — mas e' BOLETIM TECNICO INSTITUCIONAL, nao agricultor a falar. "
  "Enche a coluna e troca o sujeito. Se a ferramenta quer saber o que o "
  "produtor do Veneto esta a dizer, isto nao responde."),

 "VOICES · PAPEL de quem fala (produtor? tecnico? amador?)": (
  "STRONG", "CONAF e federacoes regionais dos Dottori Agronomi (o albo) · "
  "listas de participantes do Forum Fitoiatrico",
  "0 de 17 tem papel. O albo profissional da nome, papel reconhecido e "
  "territorio de inscricao — os tres de uma vez. ⚠️ Mas ENRIQUECE uma voz "
  "existente; nao cria observacao. E a busca estabeleceu que NAO EXISTE lista "
  "central de agronomos liberais que publiquem boletim proprio: sao "
  "iniciativas por estudio, fragmentadas."),

 "VOICES · DATA da observacao de campo": (
  "STRONG_MAS_TROCA_A_VOZ", "ARSAC · CAAR · LaMMA · Consorzi Fitosanitari",
  "0 de 17 tem data. Os boletins tem data e periodo de validade no proprio "
  "titulo. ⚠️ Mas atencao a duas datas que nao sao a mesma: a data de "
  "PUBLICACAO do post e a data em que se VIU a coisa no campo. Rede social da "
  "a primeira; boletim da as duas."),

 "VOICES · Cultura e problema relatados": (
  "STRONG", "canais e boletins ja no acervo", "campo cheio."),

 "VOICES · CANAL com exemplo real e data de publicacao": (
  "WEAK", "os 196 canais do acervo · 41 canais novos da missao anterior",
  "ha canal e ha rota. NAO HA EXEMPLO GUARDADO: a missao de descoberta "
  "registou explicitamente que nenhum conteudo foi salvo. Sem exemplo, o "
  "campo «exemplo real» continua vazio por construcao."),

 "VOICES · Volume de vozes suficiente para ler um territorio": (
  "NAO_E_GAP_DE_FONTE", "—",
  "e' contagem por regiao, nao topico. A conta esta em SOCIAL_GAPS."),

 # ═══ FUTURE ══════════════════════════════════════════════════════════════
 "FUTURE · Sinal novo com o que se observou e quem o disse": (
  "STRONG", "protezionedellepiante.it · rete Ismea–Unione Seminativi (23 pontos)",
  "a rede do Ismea recolhe por questionario a peritos e declara os resultados "
  "PROVISORIOS e de conjuntura. ⚠️ Isso e' expectativa de perito, nao "
  "medicao — serve a ferramenta de SINAL, e usa-la como producao mede opiniao "
  "e chama-lhe colheita."),

 "FUTURE · PRAGA OU DOENCA EMERGENTE (primeira deteccao)": (
  "STRONG", "protezionedellepiante.it (Emergenze Fitosanitarie · Sorveglianza "
  "· Barriere) · Piano Nazionale di Indagine · salutepianteinlombardia.it · "
  "EPPO (ja no acervo)",
  "o campo esta ausente no casco e existe declaracao oficial de primeira "
  "detecao, com regiao e data, do Servizio Fitosanitario Nazionale — chefiado "
  "por Bruno Faraglia, com laboratorios «Custos Plantis». ⚠️ Evento raro: "
  "serie curta, valor alto — o contrario de um boletim semanal."),

 "FUTURE · PIPELINE REGULATORIO (substancia em avaliacao/renovacao)": (
  "STRONG", "EU Pesticides Database (anexo do Reg. UE 540/2011) · registo de "
  "conclusoes de peer review da EFSA",
  "o automatico dizia NO_SOURCE. E ha fonte, e o mecanismo que a torna "
  "PREVISAO esta na lei: Reg. (CE) 1107/2009 art. 15 — o pedido de renovacao "
  "entra TRES ANOS antes de expirar. A data de expiracao de hoje e' o sinal "
  "de amanha. ⚠️ E O PRAZO MUDOU: o pacote Omnibus altera o art. 43 — pedido "
  "de renovacao de AUTORIZACAO passa a ate 9 meses antes de expirar, ou 3 "
  "meses se a substancia tiver aprovacao limitada. Calcular pela regra antiga "
  "da a data errada."),

 "FUTURE · MUDANCA DE POLITICA em consulta": (
  "WEAK", "CELLAR (ja no acervo) · BUR regionais",
  "⚠️ O CELLAR da o ato ADOTADO, e a pergunta e' sobre o que esta EM "
  "CONSULTA — sao dois estagios diferentes, e confundi-los faz o sistema "
  "avisar depois de a decisao estar tomada. O portal de consultas da UE (Have "
  "Your Say) nao foi pesquisado nesta missao. Achei um exemplo regional real "
  "(a instancia do Prosecco DOC publicada no BUR do Veneto, com prazo de "
  "observacoes aberto), o que mostra que o estagio de consulta E' publicado — "
  "so nao ha rota unica."),

 "FUTURE · DESLOCACAO CLIMATICA que muda a pressao de praga": (
  "STRONG", "SCIA/ISPRA · Arpae ERG5 · Arpa Piemonte (series centenarias) · "
  "Campania",
  "serie longa mais anomalia face a periodo de referencia. ⚠️ Serie longa nao "
  "e' serie homogenea: comparar 1753 com 2026 exige correcao que nao vem feita."),

 "FUTURE · Volume de sinais suficiente para ser um arquivo": (
  "NAO_E_GAP_DE_FONTE", "—", "e' contagem no tempo, nao topico."),

 # ═══ FIELD_NET ═══════════════════════════════════════════════════════════
 "FIELD_NET · Relato da rede comercial, com autor e data": (
  "NAO_E_GAP_DE_FONTE", "—",
  "os 18 registos do casco sao todos `SYNTHETIC_DEMO`. E nenhuma fonte "
  "italiana pode enche-los: o relato da rede comercial da ADAMA e' dado "
  "PROPRIO da casa. Procurar fonte externa para isto e' procurar fora o que "
  "esta dentro. A acao e' de sistema interno, nao de coleta."),

 "FIELD_NET · Identidade do tecnico de campo (TSR)": (
  "WEAK", "CONAF/albo (agronomos em geral) · listas de participantes",
  "o albo identifica agronomos com papel e territorio; nao identifica os "
  "tecnicos de campo DA CASA. Serve para reconhecer terceiros, nao os proprios."),

 # ═══ RADAR ═══════════════════════════════════════════════════════════════
 "RADAR · ENTRADA: janela de cultura com data e regiao": (
  "HERDADO", "= WINDOWS", "herda de WINDOWS. Nao se procura fonte propria."),
 "RADAR · ENTRADA: ligacao produto x problema": (
  "HERDADO", "= PORTFOLIO", "herda de PORTFOLIO."),
 "RADAR · ENTRADA: sinal de concorrente na mesma cultura/problema": (
  "HERDADO", "= COMPETITORS", "herda de COMPETITORS."),
 "RADAR · ENTRADA: voz de campo na mesma cultura/problema": (
  "HERDADO", "= VOICES", "herda de VOICES — incluindo a troca de voz."),
 "RADAR · ENTRADA: mercado da mesma cultura": (
  "HERDADO", "= MARKET", "herda de MARKET."),
 "RADAR · ENTRADA: ciencia da mesma cultura/problema": (
  "HERDADO", "= SCIENCE", "herda de SCIENCE."),

 "RADAR · VOCABULARIO UNICO de cultura entre as camadas": (
  "NAO_E_GAP_DE_FONTE", "EPPO e ISTAT ajudam, mas nao decidem",
  "a memoria do projeto ja registou que o nome da cultura chega em SEIS "
  "vocabularios que nao se falam. Ha catalogos externos que ajudam a mapear; "
  "qual deles MANDA e' decisao da casa, e essa decisao nao se coleta."),

 "RADAR · IDENTIDADE UNICA de caso entre as camadas": (
  "NAO_E_GAP_DE_FONTE", "—",
  "identificador de caso do SINTONIA. Nenhum italiano o publica."),
}


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    from collections import Counter
    from italy_gap_needs import NECESSIDADES
    chaves = {f'{n["TOOL"]} · {n["RAW_NEED"]}' for n in NECESSIDADES}
    faltam = chaves - set(AUDITORIA)
    sobram = set(AUDITORIA) - chaves
    print(f"AUDITADAS = {len(AUDITORIA)} de {len(chaves)} necessidades")
    print("  veredito:", dict(Counter(v[0] for v in AUDITORIA.values())))
    if faltam:
        print(f"\n!! {len(faltam)} NAO AUDITADAS:")
        for f in sorted(faltam):
            print("   ", f)
    if sobram:
        print(f"\n!! {len(sobram)} AUDITADAS QUE NAO EXISTEM:")
        for s in sorted(sobram):
            print("   ", s)
    if faltam or sobram:
        sys.exit(1)
    print("\nCOBERTURA DA AUDITORIA = 72/72. Nenhuma necessidade ficou sem "
          "leitura humana.")


if __name__ == "__main__":
    main()
