#!/usr/bin/env python3
"""
REGISTRO DE FONTES ITALIA — o acervo permanente, gerado, nao digitado.

    py scripts/it_fontes.py                # escreve o registro e imprime o placar
    py scripts/it_fontes.py --placar       # so o placar, sem escrever

POR QUE ESTE ARQUIVO EXISTE
-----------------------------
A missao de descoberta pediu um ACERVO PERMANENTE de fontes italianas, nao um
relatorio. Um relatorio envelhece; um registro responde "onde olhar de novo
amanha". Este arquivo e o gerador desse registro.

    FONTE != SINAL.
    Uma fonte boa continua boa no dia em que nao produz sinal nenhum.

O DONO NAO MUDOU, E ISSO E DE PROPOSITO
-----------------------------------------
`docs/fontes/ATLAS-DE-FONTES-EAME.md` ja e o dono da pergunta "que fontes
existem". O pacote V2.1 da Italia ja carrega 189 registros `SOURCE` com IDs
`SRC_*`. Criar um terceiro dono seria criar uma terceira verdade.

    Este arquivo NAO e um segundo dono. Ele e a CAMADA DE DESCOBERTA:
    fontes novas, com o metodo que as achou, prontas para entrar no Atlas
    e no pacote canonico com `DEDUPE_KEY` explicito.

`DEDUPE_AGAINST` guarda o `SRC_*` do pacote V2.1 quando a organizacao ja
esta la por outro canal. Organizacao e CANAL sao coisas diferentes: a mesma
universidade pode ser website, departamento, feed e perfil — e sao unidades
de coleta distintas, que quebram de jeitos diferentes.

O QUE NENHUM CAMPO AQUI PODE SER
----------------------------------
Nenhum campo e preenchido por plausibilidade. `HTTP`, `LATEST_CONTENT` e os
perfis sociais saem de uma leitura real, registrada em
`data/samples/IT-FONTES-V1/IT-FONTES-EVIDENCIA.json`. Campo sem leitura fica
`NAO_SEI` — que e resposta, nao buraco.

    PERFIL SOCIAL SO ENTRA SE A PROPRIA ORGANIZACAO O DECLARA NO SITE DELA.
    Handle achado por busca livre e palpite com cara de dado.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SAIDA = os.path.join(ROOT, 'data', 'samples', 'IT-FONTES-V1')

CAPTURA = '2026-09-03'

# ── VOCABULARIO ────────────────────────────────────────────────────────────────
# Fechado de proposito: um vocabulario aberto vira sinonimo e o placar deixa de
# somar. Os valores espelham o que a missao pediu, nao o que seria comodo.
AUTORIDADE = {'OFFICIAL', 'SCIENTIFIC', 'TECHNICAL', 'INDUSTRY', 'FIELD_VOICE',
              'PUBLIC_VOICE', 'MEDIA', 'COMPETITOR'}
RELEVANCIA = {'HIGH', 'MEDIUM', 'LOW'}
ATUALIZACAO = {'FREQUENT', 'PERIODIC', 'EVENT_DRIVEN', 'STATIC', 'UNKNOWN'}
COLETA = {'AUTOMATABLE', 'PARTIAL', 'MANUAL', 'BLOCKED'}
MONITORAMENTO = {'MONITOR_DAILY', 'MONITOR_WEEKLY', 'MONITOR_MONTHLY',
                 'EVENT_DRIVEN', 'DISCOVERY_ONLY', 'DO_NOT_MONITOR'}

NAO_SEI = 'NAO_SEI'


def F(sid, nome, entidade, tipo, autoridade, relevancia, url, **kw):
    """Uma ficha. Os campos obrigatorios sao posicionais para que esquecer um
    seja um erro de sintaxe, e nao um campo silenciosamente ausente."""
    assert autoridade in AUTORIDADE, autoridade
    assert relevancia in RELEVANCIA, relevancia
    f = {
        'SOURCE_ID': sid,
        'NAME': nome,
        'ENTITY': entidade,
        'SOURCE_TYPE': tipo,
        'AUTHORITY_CLASS': autoridade,
        'RELEVANCE': relevancia,
        'COUNTRY': 'ITALY',
        'REGION': kw.get('regiao', NAO_SEI),
        'LANGUAGE': kw.get('lingua', 'IT'),
        'PRIMARY_URL': url,
        'PLATFORM': kw.get('plataforma', 'WEB'),
        'SOCIAL_PROFILE_URLS': kw.get('social', {}),
        'RSS_API': kw.get('feed', NAO_SEI),
        'CROPS_RELEVANT': kw.get('crops', []),
        'TARGETS_TOPICS_RELEVANT': kw.get('temas', []),
        'ADAMA_RELEVANCE_REASON': kw['razao'],
        'DISCOVERED_FROM': kw.get('achada', NAO_SEI),
        'DISCOVERY_QUERY': kw.get('query', NAO_SEI),
        'COLLECTION_METHOD': kw.get('metodo', NAO_SEI),
        'SINTONIA_SCRAP_SUPPORTED': kw.get('scrap', 'NO'),
        'VIDEO_AVAILABLE': kw.get('video', NAO_SEI),
        'TRANSCRIPTION_RELEVANT': kw.get('transcricao', NAO_SEI),
        'UPDATE_FREQUENCY': kw.get('freq', 'UNKNOWN'),
        'LAST_OBSERVED_CONTENT_DATE': kw.get('ultimo', NAO_SEI),
        'LAST_CHECKED_AT': CAPTURA,
        'ACCESS_STATUS': kw.get('acesso', NAO_SEI),
        'COLLECTABILITY': kw.get('coleta', 'PARTIAL'),
        'PROVENANCE_STATUS': kw.get('proveniencia', 'REAL_SOURCE_PROBED'),
        'MONITORING_RECOMMENDATION': kw.get('monitor', 'DISCOVERY_ONLY'),
        'CLIENT_SAFE': kw.get('client_safe', False),
        'DEDUPE_AGAINST': kw.get('dedupe', None),
        'DEDUPE_MEANS': kw.get('dedupe_means', None),
        'EVIDENCE_PROBE': kw.get('prova', NAO_SEI),
        'NOTES_INTERNAL': kw.get('nota', NAO_SEI),
    }
    assert f['UPDATE_FREQUENCY'] in ATUALIZACAO, f['UPDATE_FREQUENCY']
    assert f['COLLECTABILITY'] in COLETA, f['COLLECTABILITY']
    assert f['MONITORING_RECOMMENDATION'] in MONITORAMENTO, f['MONITORING_RECOMMENDATION']
    return f


# ── AS FONTES ──────────────────────────────────────────────────────────────────
# A ordem e a do radar ADAMA Italia, nao a do alfabeto: primeiro o que observa
# campo nas culturas onde a ADAMA tem rotulo, depois ciencia, rede tecnica,
# mercado, concorrente e midia.
#
# O radar que orientou a busca sai do proprio acervo canonico V2.1 e nao de
# conhecimento generico sobre agricultura italiana:
#   2.030 pares rotulo (produto x cultura x alvo) -> 35 culturas, 78 alvos
#   culturas por peso de rotulo: BARBABIETOLA 239 · FRUMENTO 176 · MELO 146 ·
#   ORZO 131 · MAIS 112 · PATATA 100 · BRASSICACEE 100 · VITE 96 · ...
#   regioes das 37 oportunidades: Emilia-Romagna · Veneto · Lombardia ·
#   Friuli-Venezia Giulia · Piemonte · Puglia · Toscana · Sicilia · Trentino

FONTES = [

    # ═══ A · OFICIAL / FITOSSANITARIO ══════════════════════════════════════════
    F('IT-SRCX-001',
      'Consorzio Fitosanitario Provinciale di Parma',
      'Consorzio Fitosanitario Provinciale di Parma', 'FITOSANITARY_SERVICE',
      'OFFICIAL', 'HIGH',
      'https://www.fitosanitario.pr.it/',
      regiao='Emilia-Romagna (Parma)', feed='https://www.fitosanitario.pr.it/feed/',
      crops=['VITE', 'BARBABIETOLA', 'POMODORO', 'FRUMENTO', 'MAIS'],
      temas=['FLAVESCENZA_DORATA', 'ORGANISMI_DA_QUARANTENA', 'DEROGHE', 'POPILLIA_JAPONICA'],
      razao=('Parma esta na faixa da barbabietola e do pomodoro da industria, as duas '
             'culturas de maior peso de rotulo ADAMA (BARBABIETOLA 239 pares) e alvo das '
             'oportunidades OPP_2BDE8FC566CE e OPP_6E18A133EE14. O consorcio publica '
             'estrategia de intervencao e deroga — que e o gatilho de janela, nao opiniao.'),
      achada='busca composta cultura+problema+regiao, depois verificacao HTTP direta',
      query='bollettino fitosanitario barbabietola cercospora Emilia-Romagna 2026',
      metodo='RSS + HTML', freq='PERIODIC', ultimo='2026-05-29', acesso='GREEN',
      coleta='AUTOMATABLE', monitor='MONITOR_WEEKLY',
      dedupe='SRC_FITOSANITARIO_MO_IT / SRC_FITOSANITARIO_RE_IT sao consorcios IRMAOS, nao este',
      dedupe_means=('o pacote V2.1 ja tem Modena e Reggio Emilia. Parma e Piacenza sao '
                    'consorcios PROVINCIAIS DISTINTOS, com bollettino proprio. Colapsa-los '
                    'perderia a provincia, que e a unidade geografica do sinal.'),
      prova='probe/c1.json#FITOSANITARIO_PR · HTTP 200 · RSS declarado'),

    F('IT-SRCX-002',
      'Consorzio Fitosanitario Provinciale di Piacenza',
      'Consorzio Fitosanitario Provinciale di Piacenza', 'FITOSANITARY_SERVICE',
      'OFFICIAL', 'HIGH',
      'https://www.fitosanitario.pc.it/',
      regiao='Emilia-Romagna (Piacenza)', feed='https://www.fitosanitario.pc.it/feed/',
      crops=['VITE', 'BARBABIETOLA', 'POMODORO', 'MAIS'],
      temas=['FLAVESCENZA_DORATA', 'DISCIPLINARI_PRODUZIONE_INTEGRATA', 'DEROGHE'],
      razao=('Piacenza fecha o quadrante oeste da Emilia-Romagna e e a provincia onde a '
             'Universita Cattolica desenvolveu CERCOPRI/CERCODEP, os modelos de cercospora '
             'da barbabietola adotados pelo servico regional. Fonte de janela, nao de opiniao.'),
      achada='busca composta + verificacao HTTP', query='consorzio fitosanitario provinciale Piacenza bollettino',
      metodo='RSS + HTML', freq='PERIODIC', ultimo='2026-05-27', acesso='GREEN',
      coleta='AUTOMATABLE', monitor='MONITOR_WEEKLY',
      dedupe='SRC_FITOSANITARIO_MO_IT / SRC_FITOSANITARIO_RE_IT (irmaos, nao o mesmo)',
      dedupe_means='mesma familia institucional, provincia diferente, bollettino diferente',
      prova='probe/c2.json#FITOSANITARIO_PC_FEED · HTTP 200 · 10 itens datados'),

    F('IT-SRCX-003',
      'UNIBO BIG — monitoraggio nazionale Halyomorpha halys (rete di trappole)',
      'Universita di Bologna — Big Data & Remote Sensing Lab', 'FIELD_MONITORING_NETWORK',
      'OFFICIAL', 'HIGH',
      'https://big.csr.unibo.it/projects/cimice/monitoring.php',
      regiao='Emilia-Romagna (MO, BO, FC, RA, FE, RE, PC, PR)',
      feed='POST https://big.csr.unibo.it/projects/cimice/php/getChartData.php (chartType=globalMonitoringBasic&returnType=json)',
      crops=['MELO', 'PERO', 'PESCO', 'ACTINIDIA', 'SOIA', 'MAIS', 'POMODORO'],
      temas=['CIMICE_ASIATICA', 'STINK_BUG', 'CATTURE_TRAPPOLE', 'STADI_DI_SVILUPPO'],
      razao=('E a UNICA fonte achada nesta missao que entrega SERIE TEMPORAL NUMERICA de '
             'campo, por provincia e por estadio, com o denominador (trappole ispezionate) '
             'no mesmo registro. Liga-se a OPP_56F19FD9F62B (MELO x ISSUE_STINK_BUG) e ao '
             'tau-fluvalinate, ativo do universo regulatorio ADAMA Italia.'),
      achada='snowballing: citada DENTRO da nota tecnica cimice do Servizio Fitosanitario ER',
      query='(nao veio de busca) — link impresso no PDF Note-tecniche_cimice do Servizio Fitosanitario ER',
      metodo='HTTP POST JSON (API aberta, sem chave)', freq='FREQUENT', ultimo='2026-08-31',
      acesso='GREEN', coleta='AUTOMATABLE', monitor='MONITOR_WEEKLY',
      video='NO', transcricao='NO',
      nota=('n = trappole ispezionate e ele MEXE semana a semana (RA: 13 -> 7 -> 6). '
            'Provincia com n=0 e OBSERVACAO AUSENTE, nunca pressao zero. As parcelas nao '
            'sao amostra aleatoria: e rede de acompanhamento escolhida. Mesma cautela do RAIF.'),
      prova='probe/cimice_globalMonitoringBasic.json · 177 pontos · 2021-03-08 a 2026-08-31'),

    F('IT-SRCX-004',
      'Servizio Fitosanitario Emilia-Romagna — API Plone dos bollettini interprovinciali',
      'Regione Emilia-Romagna', 'FITOSANITARY_BULLETIN_API',
      'OFFICIAL', 'HIGH',
      'https://agricoltura.regione.emilia-romagna.it/++api++/fitosanitario/difesa-sostenibile/bollettini/bollettini-interprovinciali-di-produzione-integrata-e-biologica-2026',
      regiao='Emilia-Romagna (4 areas interprovinciais)',
      feed='Plone REST API (++api++), JSON, sem chave',
      crops=['BARBABIETOLA', 'POMODORO', 'MELO', 'PERO', 'VITE', 'MAIS', 'FRUMENTO', 'CAROTA', 'PATATA'],
      temas=['CERCOSPORA', 'TICCHIOLATURA', 'CIMICE_ASIATICA', 'PERONOSPORA', 'AFIDI',
             'DISERBO', 'DEROGHE', 'SOSTANZE_CANDIDATE_ALLA_SOSTITUZIONE'],
      razao=('O host ja estava no acervo; a ROTA nao. A API devolve os 150 PDFs de 2026 com '
             'titulo e data, o que transforma "abrir a pagina toda semana" em coleta. E o '
             'bollettino e onde a substancia ativa ADAMA aparece por nome, com dose e '
             'numero maximo de intervencoes.'),
      achada='a pagina HTML e um SPA Volto e nao entrega link nenhum; a API estava atras dela',
      query='++api++ sobre a URL do indice de bollettini 2026',
      metodo='REST JSON + download de PDF + scripts/pdf_text.py', freq='FREQUENT',
      ultimo='2026-09-02', acesso='GREEN', coleta='AUTOMATABLE', monitor='MONITOR_WEEKLY',
      dedupe='SRC_AGRICOLTURA_REGIONE_EMILIA_ROMAGNA_IT',
      dedupe_means=('MESMA ORGANIZACAO, CANAL NOVO. O registro V2.1 aponta para o site; este '
                    'aponta para a API que lista os bollettini. Nao sao duas organizacoes, '
                    'sao dois pontos de coleta com falhas diferentes.'),
      prova='probe/er_bollettini_2026.json · 150 arquivos · probe/er_texts.json · 14 PDFs lidos, 2,3 M caracteres'),

    F('IT-SRCX-005',
      'ERSA FVG — bollettini di produzione integrata (melo e demais culturas)',
      'Agenzia regionale per lo sviluppo rurale FVG', 'FITOSANITARY_BULLETIN',
      'OFFICIAL', 'HIGH',
      'http://difesafitosanitaria.ersa.fvg.it/difesa-e-produzione-integrata/difesa-integrata-obbligatoria/bollettini-fitosanitari/melo/bollettini-produzione-integrata-melo-2026',
      regiao='Friuli-Venezia Giulia',
      social={'INSTAGRAM': 'https://www.instagram.com/ersa_fvg_informa/',
              'FACEBOOK': 'https://www.facebook.com/ERSAFVGINFORMA'},
      crops=['MELO', 'VITE', 'MAIS', 'SOIA'],
      temas=['TICCHIOLATURA', 'CARPOCAPSA', 'PIRALIDE', 'DIFESA_INTEGRATA_OBBLIGATORIA'],
      razao=('FVG e a geografia declarada de OPP_9C600748BB1B (MAIS x CORN_BORER) e de '
             'OPP_F139E05A9F3A (POMODORO x POWDERY_MILDEW). O host ja estava no acervo; o '
             'perfil Instagram declarado no proprio site nao estava — e o acervo canonico '
             'nao tem UM perfil Instagram italiano.'),
      achada='verificacao HTTP do host ja registrado + colheita dos perfis que o site declara',
      query='ERSA FVG bollettini produzione integrata melo 2026',
      metodo='HTML + Instagram publico', scrap='YES', freq='PERIODIC', ultimo='2026-04-14',
      acesso='GREEN', coleta='AUTOMATABLE', monitor='MONITOR_WEEKLY',
      dedupe='SRC_DIFESAFITOSANITARIA_ERSA_FVG_IT',
      dedupe_means='mesma organizacao; o que e novo aqui e o CANAL SOCIAL declarado, nao a instituicao',
      prova='probe/c3.json#ERSA_FVG_MELO HTTP 200 · probe/c4.json#ERSA_FVG social declarado'),
]

FONTES += [

    # ═══ B · CIENCIA / PESQUISA ════════════════════════════════════════════════
    F('IT-SRCX-006',
      'Centro di Sperimentazione Laimburg',
      'Provincia Autonoma di Bolzano — Versuchszentrum Laimburg', 'RESEARCH_CENTRE',
      'SCIENTIFIC', 'HIGH',
      'https://www.laimburg.it/it/',
      regiao='Trentino-Alto Adige (Bolzano)',
      crops=['MELO', 'VITE'],
      temas=['AFIDE_LANIGERO', 'TICCHIOLATURA', 'OIDIO', 'DIFESA_SOSTENIBILE', 'RESISTENZA'],
      razao=('MELO e a 3a cultura por peso de rotulo ADAMA (146 pares) e o Alto Adige e o '
             'polo produtor. Laimburg publica 80-100 trabalhos e 150-200 relatorios por ano '
             'sobre justamente melo e vite — e e a instituicao que a rede tecnica local cita.'),
      achada='busca composta cultura+regiao+instituicao', query='consorzio melo Trentino Alto Adige ticchiolatura carpocapsa 2026 Laimburg',
      metodo='HTML + relatorios PDF', freq='PERIODIC', acesso='GREEN', coleta='PARTIAL',
      monitor='MONITOR_MONTHLY',
      nota='a home devolve 2.842 bytes: e pagina de redirecionamento de lingua, nao site vazio',
      prova='probe/c1.json#LAIMBURG HTTP 200'),

    F('IT-SRCX-007',
      'AIPP — Associazione Italiana per la Protezione delle Piante',
      'AIPP', 'SCIENTIFIC_SOCIETY', 'SCIENTIFIC', 'HIGH',
      'https://www.aipp.it/',
      regiao='ITALIA', feed='https://aipp.it/feed/',
      social={'INSTAGRAM': 'https://www.instagram.com/aipp_protezione_piante/',
              'YOUTUBE': 'https://www.youtube.com/channel/UCktJyIUm3qJJpThrTa8nsHQ',
              'FACEBOOK': 'https://www.facebook.com/AippProtezionePiante'},
      crops=['TODAS'], temas=['PROTEZIONE_DELLE_PIANTE', 'RESISTENZA', 'NUOVE_AVVERSITA'],
      razao=('E a sociedade cientifica italiana da PROTECAO DAS PLANTAS — exatamente o negocio '
             'da ADAMA. Tem feed, canal de video e perfil Instagram DECLARADOS NO PROPRIO SITE, '
             'e nenhum deles esta no acervo canonico.'),
      achada='verificacao HTTP do host ja registrado + colheita de perfis declarados',
      query='AIPP associazione italiana protezione piante',
      metodo='RSS + YouTube + Instagram publico', scrap='YES', video='YES', transcricao='YES',
      freq='EVENT_DRIVEN', acesso='GREEN', coleta='AUTOMATABLE', monitor='MONITOR_MONTHLY',
      dedupe='SRC_AIPP_IT', dedupe_means='mesma organizacao; os TRES canais sociais sao novos',
      prova='probe/c3.json#AIPP HTTP 200 · RSS e sociais declarados'),

    F('IT-SRCX-008',
      'Universita Cattolica del Sacro Cuore, Piacenza — autores de CERCOPRI/CERCODEP',
      'UCSC Piacenza', 'UNIVERSITY_GROUP', 'SCIENTIFIC', 'HIGH',
      'https://piacenza.unicatt.it/',
      regiao='Emilia-Romagna (Piacenza)',
      social={'INSTAGRAM': 'https://www.instagram.com/unicatt/'},
      crops=['BARBABIETOLA', 'VITE', 'FRUMENTO'],
      temas=['CERCOSPORA', 'MODELLI_PREVISIONALI', 'EPIDEMIOLOGIA'],
      razao=('CERCOPRI e CERCODEP — os modelos que dizem QUANDO a cercospora da barbabietola '
             'comeca e como a epidemia evolui — saem daqui e sao adotados pelo Servizio '
             'Fitosanitario da Emilia-Romagna. Barbabietola e a 1a cultura por peso de rotulo '
             'ADAMA (239 pares) e o alvo de OPP_2BDE8FC566CE e OPP_9AB924CA36C8. Modelo de '
             'previsao e o unico BETTER TIMING agronomico defensavel que esta missao encontrou.'),
      achada='snowballing a partir do texto da scheda cercospora do Servizio Fitosanitario ER',
      query='Universita Cattolica Piacenza CERCOPRI CERCODEP modello previsionale cercospora barbabietola',
      metodo='HTML', freq='PERIODIC', acesso='GREEN', coleta='MANUAL', monitor='MONITOR_MONTHLY',
      nota=('a URL de departamento (dipartimenti.unicatt.it/diproves e /scienze-delle-produzioni-'
            'vegetali-sostenibili) devolveu 404 nas duas tentativas. A pagina do DEPARTAMENTO '
            'fica NAO_SEI; o campus esta provado. Nao inventar a rota que faltou.'),
      prova='probe/c4.json#UNICATT_PIACENZA HTTP 200 · probe/c1.json#UCSC_DIPROVES HTTP 404'),

    F('IT-SRCX-009',
      'Rete Rurale — Banca dati dei Gruppi Operativi PEI-AGRI',
      'Rete Rurale Nazionale / MASAF', 'RESEARCH_TO_FIELD_REGISTRY', 'OFFICIAL', 'MEDIUM',
      'https://www.innovarurale.it/it/pei-agri/gruppi-operativi/bancadati-go-pei',
      regiao='ITALIA (por regiao)',
      crops=['MELO', 'PERO', 'VITE', 'PATATA', 'POMODORO'],
      temas=['INNOVAZIONE', 'DIFESA', 'RIDUZIONE_INPUT', 'GRUPPI_OPERATIVI'],
      razao=('E o indice nacional dos Gruppi Operativi — o lugar onde pesquisa vira projeto de '
             'campo com produtor e tecnico dentro. E a cadeia SCIENCE -> FIELD que a Espanha '
             'nao conseguiu fechar por nome: aqui a ligacao e DECLARADA pelo proprio projeto.'),
      achada='busca composta consultoria+bollettino, o registro apareceu ao lado',
      query='cimice asiatica monitoraggio strategie innovative gruppo operativo',
      metodo='HTML', freq='PERIODIC', acesso='GREEN', coleta='PARTIAL', monitor='MONITOR_MONTHLY',
      dedupe='SRC_RETERURALE_IT',
      dedupe_means='mesma rede institucional; a BANCA DATI dos GO e um endpoint distinto do portal',
      prova='probe/c1.json#INNOVARURALE_GO HTTP 200'),

    # ═══ C · CAMPO / TECNICO ═══════════════════════════════════════════════════
    F('IT-SRCX-010',
      'Agralia Studio Agronomico (Brescia) — Bollettino Vite',
      'Agralia s.r.l.', 'PRIVATE_AGRONOMIC_ADVISORY', 'TECHNICAL', 'HIGH',
      'https://www.agralia.it/',
      regiao='Lombardia (Brescia)', feed='https://www.agralia.it/feed/',
      social={'INSTAGRAM': 'https://www.instagram.com/agralia.it/',
              'YOUTUBE': 'https://www.youtube.com/@agraliastudio',
              'FACEBOOK': 'https://www.facebook.com/agralia.it'},
      crops=['VITE', 'OLIVO', 'MAIS'],
      temas=['OIDIO', 'PERONOSPORA', 'ROGNA_OLIVO', 'AGGIORNAMENTO_NORMATIVO', 'AGROMETEO'],
      razao=('E a VOZ TECNICA PRIVADA que faltava: um estudio agronomico que publica bollettino '
             'proprio de vite, com serie e com aggiornamento normativo. Nao e orgao publico nem '
             'midia — e quem aconselha o produtor. Lombardia + vite cruza OPP_AF16E6A6B8B3 '
             '(VITE, GEO_ITALY, sinal de 5 dias) e OPP_3F736F0A9467 (VITE x PERONOSPORA).'),
      achada='busca composta por TIPO DE FONTE, nao por cultura',
      query='"studio agronomico" bollettino tecnico settimanale vite mais consulenza agronomica Italia 2026',
      metodo='RSS + Instagram + YouTube', scrap='YES', video='YES', transcricao='YES',
      freq='PERIODIC', ultimo='2026-05-26', acesso='GREEN', coleta='AUTOMATABLE',
      monitor='MONITOR_WEEKLY',
      nota=('feed com 24 itens; o mais recente e de 2026-05-26 — 100 dias. Bollettino de vite '
            'concentrado na estacao. PERIODICO SAZONAL nao e fonte morta.'),
      prova='probe/c1.json#AGRALIA · probe/f1.json#AGRALIA 24 itens, latest 2026-05-26'),

    F('IT-SRCX-011',
      'Agrintesa — cooperativa ortofrutta e vino',
      'Agrintesa Soc. Coop. Agricola', 'COOPERATIVE', 'FIELD_VOICE', 'MEDIUM',
      'https://www.agrintesa.it/',
      regiao='Emilia-Romagna (Faenza / Romagna)', feed='https://www.agrintesa.it/feed/',
      social={'INSTAGRAM': 'https://www.instagram.com/agrintesa_ortofrutta_vino/',
              'YOUTUBE': 'https://www.youtube.com/channel/UCoA303PgO9oOBWgZ3Nl5GvQ',
              'FACEBOOK': 'https://www.facebook.com/Agrintesa'},
      crops=['MELO', 'PERO', 'PESCO', 'ACTINIDIA', 'VITE'],
      temas=['CAMPAGNA', 'QUALITA', 'CIMICE_ASIATICA', 'FILIERA'],
      razao=('Romagna e a area das oportunidades de pomacee (OPP_20D89B04F64D PERO x SCAB, '
             'OPP_DA4B5954F72A MELO x SCAB, ambas Emilia-Romagna) e a mesma onde a rede de '
             'trappole da cimice mede. Cooperativa fala do que colheu — voz de campo agregada.'),
      achada='colheita de perfis declarados em site de cooperativa italiana',
      query='cooperativa ortofrutta Emilia-Romagna melo pero campagna 2026',
      metodo='RSS + Instagram + YouTube', scrap='YES', video='YES', transcricao='YES',
      freq='PERIODIC', acesso='GREEN', coleta='AUTOMATABLE', monitor='MONITOR_MONTHLY',
      prova='probe/c4.json#AGRINTESA HTTP 200 · RSS e 3 sociais declarados'),

    F('IT-SRCX-012',
      'Apofruit Italia — cooperativa ortofrutticola',
      'Apofruit Italia Soc. Coop. Agricola', 'COOPERATIVE', 'FIELD_VOICE', 'MEDIUM',
      'https://www.apofruit.it/',
      regiao='Emilia-Romagna + nacional', feed='https://www.apofruit.it/feed/',
      social={'YOUTUBE': 'https://www.youtube.com/@Apofruit',
              'LINKEDIN': 'https://www.linkedin.com/company/apofruit-italia-soc-coop-agricola',
              'FACEBOOK': 'https://www.facebook.com/apofruit'},
      crops=['MELO', 'PERO', 'PESCO', 'ACTINIDIA', 'FRAGOLA'],
      temas=['CAMPAGNA', 'FILIERA', 'QUALITA'],
      razao=('Uma das maiores OP de fruta da Italia. FRAGOLA (51 pares de rotulo ADAMA) e '
             'pomacee estao no seu perimetro. LinkedIn declarado da acesso a voz tecnica '
             'nominal — a camada que na Espanha foi a unica a resolver pais e papel.'),
      achada='colheita de perfis declarados', query='Apofruit cooperativa ortofrutticola Italia',
      metodo='RSS + LinkedIn publico + YouTube', video='YES', transcricao='YES',
      freq='PERIODIC', acesso='GREEN', coleta='AUTOMATABLE', monitor='MONITOR_MONTHLY',
      prova='probe/c4.json#APOFRUIT HTTP 200'),

    F('IT-SRCX-013',
      'Terremerse — cooperativa multifiliera (cereali, sementi, agrofarmaci)',
      'Terremerse Soc. Coop.', 'COOPERATIVE_DISTRIBUTOR', 'FIELD_VOICE', 'MEDIUM',
      'https://www.terremerse.it/',
      regiao='Emilia-Romagna', feed='https://terremerse.it/feed/',
      social={'YOUTUBE': 'https://www.youtube.com/user/TerremerseCoop',
              'FACEBOOK': 'https://www.facebook.com/Terremerse-108464129240303'},
      crops=['FRUMENTO', 'MAIS', 'SOIA', 'BARBABIETOLA', 'POMODORO'],
      temas=['DISERBO', 'DIFESA', 'SEMENTI', 'MERCATO_CEREALI'],
      razao=('Cooperativa que TAMBEM distribui agrofarmaco — e portanto o lugar onde a decisao '
             'tecnica encosta na decisao de compra, nas culturas de maior peso de rotulo ADAMA '
             '(FRUMENTO 176, MAIS 112, BARBABIETOLA 239). O acervo canonico nao tem nenhuma '
             'fonte de DISTRIBUICAO italiana provada.'),
      achada='colheita de perfis declarados em cooperativas de multifiliera',
      query='cooperativa agricola Emilia-Romagna cereali agrofarmaci distribuzione',
      metodo='RSS + YouTube', video='YES', transcricao='YES', freq='PERIODIC',
      acesso='GREEN', coleta='AUTOMATABLE', monitor='MONITOR_MONTHLY',
      nota='DISTRIBUICAO != VENDA ADAMA. A fonte prova o que ela publica, nunca share de canal.',
      prova='probe/c4.json#TERREMERSE HTTP 200'),

    F('IT-SRCX-014',
      'OI Pomodoro da Industria Nord Italia',
      'Organizzazione Interprofessionale Pomodoro da Industria Nord Italia',
      'INTERPROFESSIONAL_ORGANISATION', 'INDUSTRY', 'HIGH',
      'https://www.oipomodoronorditalia.it/',
      regiao='Emilia-Romagna · Lombardia · Veneto · Piemonte',
      crops=['POMODORO'],
      temas=['CAMPAGNA', 'SUPERFICI', 'PREZZO_DI_RIFERIMENTO', 'RESE'],
      razao=('POMODORO e a cultura de OPP_6E18A133EE14 (confirmada), OPP_314CBAE48A5C, '
             'OPP_EA2AE1EFB775 e OPP_F139E05A9F3A — quatro das 37. A OI e quem publica '
             'superficie contratada e andamento da campanha do Norte, que e o denominador '
             'real da cultura. Sem ela, "pomodoro" e uma palavra sem hectare.'),
      achada='busca por organizacao de produtores da cultura prioritaria',
      query='OI pomodoro da industria nord Italia superficie campagna 2026',
      metodo='HTML', freq='PERIODIC', acesso='GREEN', coleta='PARTIAL', monitor='MONITOR_MONTHLY',
      nota='SUPERFICIE CONTRATADA != MERCADO ENDERECAVEL ADAMA. E denominador de cultura, so isso.',
      prova='probe/c1.json#OI_POMODORO_NORD HTTP 200'),

    F('IT-SRCX-015',
      'Assomela — associazione dei produttori di mele',
      'Assomela s.c.', 'PRODUCER_ORGANISATION', 'INDUSTRY', 'MEDIUM',
      'https://assomela.it/',
      regiao='Trentino-Alto Adige · Veneto · Piemonte · Emilia-Romagna',
      social={'FACEBOOK': 'https://www.facebook.com/assomelasc'},
      crops=['MELO'], temas=['PRODUZIONE', 'PREVISIONE_RACCOLTO', 'MERCATO_MELE'],
      razao=('MELO e a 3a cultura por peso de rotulo ADAMA (146 pares) e a cultura de quatro '
             'oportunidades (OPP_DA4B5954F72A, OPP_75C37DED9160, OPP_56F19FD9F62B, '
             'OPP_E1A1D73F07BF). Assomela publica a previsao de colheita nacional — o '
             'denominador da cultura, nao a venda.'),
      achada='busca por organizacao de produtores da cultura prioritaria',
      query='Assomela produttori mele previsione raccolto Italia',
      metodo='HTML', freq='PERIODIC', acesso='YELLOW', coleta='PARTIAL', monitor='MONITOR_MONTHLY',
      nota=('www.assomela.it reprova o certificado por HOSTNAME MISMATCH; assomela.it sem www '
            'responde 200. Estado da fonte, registrado — a verificacao TLS nao foi desligada.'),
      prova='probe/c1.json#ASSOMELA (SSL hostname mismatch) · probe/c2.json#ASSOMELA2 HTTP 200'),
]

FONTES += [

    # ═══ D · VOZ PUBLICA / AUDIO / VIDEO ═══════════════════════════════════════
    F('IT-SRCX-016',
      'Agricast — il podcast dei Gruppi Operativi (Emilia-Romagna)',
      'Agricast', 'PODCAST', 'TECHNICAL', 'HIGH',
      'https://www.spreaker.com/podcast/agricast--5971526',
      regiao='Emilia-Romagna', plataforma='SPREAKER',
      feed='https://api.spreaker.com/v2/shows/5971526/episodes (JSON, sem chave)',
      crops=['MELO', 'PERO', 'SUSINO', 'PATATA', 'VITE', 'NOCE', 'ORTAGGI'],
      temas=['DIFESA_INNOVATIVA', 'RIDUZIONE_INPUT_CHIMICI', 'ELATERIDI', 'EMERGENZE_FITOSANITARIE',
             'MODELLI_PREVISIONALI', 'RETI_ANTI_INSETTO', 'COSTI_DI_IMPIANTO'],
      razao=('E a fonte de VOZ mais densa que esta missao encontrou, e a unica em que o sinal '
             'esta SO NA FALA: a descricao do episodio tem duas linhas, e a fala tem 12 a 17 mil '
             'caracteres de agronomia italiana com pesquisador, tecnico e produtor no mesmo audio. '
             'Os episodios sao os Gruppi Operativi da Emilia-Romagna — a mesma regiao das '
             'oportunidades de pomacee e da rede de trappole da cimice.'),
      achada='rota de AUDIO buscada depois que a rota de video do YouTube deu 403 na midia',
      query='api.spreaker.com/v2/search?type=shows&q=agricoltura (e q=agricoltura+di+precisione)',
      metodo='API JSON + download mp3 + ffmpeg + faster-whisper small LOCAL',
      scrap='YES', video='NO', transcricao='YES',
      freq='PERIODIC', ultimo='2026-08-31', acesso='GREEN', coleta='AUTOMATABLE',
      monitor='MONITOR_MONTHLY',
      nota=('audio-only: NAO existe legenda para comparar. Todo sinal util deste canal e, por '
            'construcao, TRANSCRIPT_ONLY. Custo de transcricao: 0 USD, ~9x tempo real nesta maquina.'),
      prova='probe/it_audio_transcricoes.json · episodios transcritos com tempo e velocidade medidos'),

    F('IT-SRCX-017',
      'Vita in Campagna — podcast',
      'Edagricole / Vita in Campagna', 'PODCAST', 'MEDIA', 'MEDIUM',
      'https://www.spreaker.com/podcast/vita-in-campagna--6885264',
      regiao='ITALIA', plataforma='SPREAKER',
      feed='https://api.spreaker.com/v2/shows/6885264/episodes',
      crops=['ORTAGGI', 'FRUTTIFERI'], temas=['ONDATE_DI_CALORE', 'ACQUA', 'GESTIONE_PIANTE'],
      razao=('Voz de divulgacao do mesmo grupo editorial tecnico (Edagricole). Serve como '
             'CONTRASTE deliberado: mede quanto do canal de divulgacao e tecnicamente utilizavel '
             'contra o canal de Gruppi Operativi. Sem contraste, "voz util" nao tem denominador.'),
      achada='mesma rota de API por termo de fonte', query='api.spreaker.com search q=consorzio+agrario',
      metodo='API JSON + transcricao local', scrap='YES', transcricao='YES',
      freq='PERIODIC', ultimo='2026-08-25', acesso='GREEN', coleta='AUTOMATABLE',
      monitor='MONITOR_MONTHLY',
      prova='probe/it_audio_transcricoes.json'),

    # ═══ E · MIDIA TECNICA ═════════════════════════════════════════════════════
    F('IT-SRCX-018',
      'FruitJournal',
      'FruitJournal', 'TECHNICAL_MEDIA', 'MEDIA', 'HIGH',
      'https://www.fruitjournal.com/',
      regiao='ITALIA', feed='https://www.fruitjournal.com/feed/',
      crops=['MELO', 'PERO', 'POMODORO', 'ACTINIDIA', 'AGRUMI', 'OLIVO'],
      temas=['DIFESA', 'CIMICE', 'EPPO_ALERT_LIST', 'CAMPAGNA', 'RICERCA'],
      razao=('Publica todo dia sobre as culturas de fruta e horticolas da ADAMA, e cita '
             'instituicoes de pesquisa por nome (Laimburg, CNR). Feed com data em todos os itens: '
             'e das poucas midias italianas com rota de coleta limpa.'),
      achada='busca composta cultura+problema+ano', query='vite peronospora difesa vigneto Italia 2026',
      metodo='RSS', freq='FREQUENT', ultimo='2026-09-03', acesso='GREEN',
      coleta='AUTOMATABLE', monitor='MONITOR_DAILY',
      prova='probe/f1.json#FRUITJOURNAL · 36 itens · latest 2026-09-03 · age 0'),

    F('IT-SRCX-019',
      'VVQ — Vigne, Vini & Qualita (Edagricole)',
      'Edagricole / Tecniche Nuove', 'TECHNICAL_MEDIA', 'MEDIA', 'MEDIUM',
      'https://vigneviniequalita.edagricole.it/',
      regiao='ITALIA', feed='https://vigneviniequalita.edagricole.it/feed/',
      social={'INSTAGRAM': 'https://www.instagram.com/edagricole_official/',
              'YOUTUBE': 'https://www.youtube.com/channel/UCrCabYjtyqdzu1zXo95o7Jw'},
      crops=['VITE'], temas=['PERONOSPORA', 'OIDIO', 'VENDEMMIA', 'DIFESA_VIGNETO'],
      razao=('VITE tem 96 pares de rotulo ADAMA e cinco oportunidades (OPP_AF16E6A6B8B3 e '
             'OPP_3965565ACFCC confirmadas). Revista de cultura unica, com data em todos os itens.'),
      achada='busca composta cultura+problema', query='vite peronospora difesa vigneto Italia 2026',
      metodo='RSS', freq='FREQUENT', ultimo='2026-09-02', acesso='GREEN',
      coleta='AUTOMATABLE', monitor='MONITOR_WEEKLY',
      prova='probe/f1.json#VVQ latest 2026-09-02'),

    F('IT-SRCX-020',
      'Rivista Orticoltura (Edagricole)',
      'Edagricole / Tecniche Nuove', 'TECHNICAL_MEDIA', 'MEDIA', 'MEDIUM',
      'https://rivistaorticoltura.edagricole.it/',
      regiao='ITALIA', feed='https://rivistaorticoltura.edagricole.it/feed/',
      crops=['POMODORO', 'PATATA', 'CIPOLLA', 'CAROTA', 'LATTUGA', 'CUCURBITACEE', 'BRASSICACEE'],
      temas=['DIFESA_ORTICOLE', 'MERCATO', 'CLIMA'],
      razao=('Cobre o bloco horticola inteiro, que soma peso alto de rotulo ADAMA '
             '(PATATA 100 + BRASSICACEE 100 + CAROTA 63 + CUCURBITACEE 58 + CIPOLLA 42 + '
             'POMODORO 44 + LATTUGA 11 = 418 pares) e nao tinha midia dedicada no acervo.'),
      achada='verificacao HTTP a partir do grupo editorial ja conhecido',
      query='rivista orticoltura Edagricole', metodo='RSS', freq='FREQUENT',
      ultimo='2026-09-02', acesso='GREEN', coleta='AUTOMATABLE', monitor='MONITOR_WEEKLY',
      prova='probe/f1.json#RIVORTIC latest 2026-09-02'),

    F('IT-SRCX-021',
      'Olivo e Olio (Edagricole)',
      'Edagricole / Tecniche Nuove', 'TECHNICAL_MEDIA', 'MEDIA', 'MEDIUM',
      'https://olivoeolio.edagricole.it/',
      regiao='ITALIA', feed='https://olivoeolio.edagricole.it/feed/',
      crops=['OLIVO'], temas=['XYLELLA', 'MOSCA_OLEARIA', 'PREZZI_OLIO', 'FILIERA'],
      razao=('OLIVO tem apenas 1 par de rotulo ADAMA lido — mas tem tres oportunidades '
             '(OPP_568684853264, OPP_B19061BA418B, OPP_EE1E2A3869EE) e cinco crop windows. '
             'A assimetria entre 1 par lido e 3 oportunidades e ela propria o achado: e '
             'cobertura de LEITURA de rotulo, nao ausencia de portfolio.'),
      achada='verificacao HTTP a partir do grupo editorial', query='olivo e olio Edagricole rivista',
      metodo='RSS', freq='FREQUENT', ultimo='2026-09-03', acesso='GREEN',
      coleta='AUTOMATABLE', monitor='MONITOR_WEEKLY',
      prova='probe/f1.json#OLIVOEOLIO latest 2026-09-02 · probe/f2.json#OLIVONEWS latest 2026-09-03'),

    F('IT-SRCX-022',
      'Myfruit — web magazine dell ortofrutta',
      'Myfruit', 'TECHNICAL_MEDIA', 'MEDIA', 'MEDIUM',
      'https://www.myfruit.it/',
      regiao='ITALIA',
      social={'YOUTUBE': 'https://www.youtube.com/@myfruitvideo',
              'FACEBOOK': 'https://www.facebook.com/myfruit.webmagazine'},
      crops=['MELO', 'PERO', 'PESCO', 'ACTINIDIA', 'FRAGOLA'],
      temas=['MERCATO_ORTOFRUTTA', 'CAMPAGNA', 'FILIERA'],
      razao=('Canal de video proprio sobre ortofrutta — camada de video italiana, que no acervo '
             'canonico so existe via YouTube generico. Cobre as pomacee das oportunidades.'),
      achada='verificacao HTTP + colheita de canais declarados', query='myfruit web magazine ortofrutta',
      metodo='HTML + YouTube', video='YES', transcricao='YES', freq='FREQUENT',
      acesso='GREEN', coleta='PARTIAL', monitor='MONITOR_WEEKLY',
      nota='o RSS anunciado nao e XML (devolve a home). Coleta por HTML ate achar rota limpa.',
      prova='probe/c3.json#MYFRUIT HTTP 200 · probe/f2.json#MYFRUIT NOT_XML'),

    F('IT-SRCX-023',
      'FreshPlaza Italia',
      'FreshPlaza', 'TECHNICAL_MEDIA', 'MEDIA', 'MEDIUM',
      'https://www.freshplaza.it/',
      regiao='ITALIA + internacional', feed='https://www.freshplaza.it/rss.xml',
      crops=['MELO', 'PERO', 'POMODORO', 'AGRUMI', 'CUCURBITACEE'],
      temas=['MERCATO', 'PREZZI', 'CAMPAGNA', 'LOGISTICA'],
      razao=('Rota de mercado ortofruticola com feed limpo e datado. MARKET_MOMENT e o arquetipo '
             'de tres das nove oportunidades confirmadas (OPP_576D71D702F0, OPP_8EA4F5C0D3F4, '
             'OPP_AF16E6A6B8B3) e o acervo tinha mercado sobretudo por Eurostat/ISMEA, nunca por '
             'noticia de filiera datada.'),
      achada='verificacao de feeds de midia ortofruticola', query='freshplaza italia rss',
      metodo='RSS', freq='FREQUENT', ultimo='2026-09-03', acesso='GREEN',
      coleta='AUTOMATABLE', monitor='MONITOR_DAILY',
      nota='PRECO DE FILIERA != DEMANDA DE AGROFARMACO. Serve para timing de campanha, nao para venda.',
      prova='probe/f2.json#FRESHPLAZA_IT 29 itens latest 2026-09-03'),

    # ═══ F · CONCORRENCIA ══════════════════════════════════════════════════════
    F('IT-SRCX-024',
      'FMC Agro Italia — canais sociais declarados',
      'FMC Agro Italia', 'COMPETITOR_CHANNEL', 'COMPETITOR', 'MEDIUM',
      'https://ag.fmc.com/it',
      regiao='ITALIA',
      social={'INSTAGRAM': 'https://www.instagram.com/fmc_agro_italia/',
              'YOUTUBE': 'https://www.youtube.com/channel/UCWjrNnyRiWOtCM0zKUcsK5A'},
      crops=['VITE', 'MAIS', 'POMODORO', 'FRUMENTO'],
      temas=['COMUNICAZIONE_PRODOTTO', 'CAMPAGNE', 'TECNICA'],
      razao=('O acervo canonico tem o SITE da FMC Italia mas nenhum canal social italiano de '
             'concorrente. Instagram e YouTube DECLARADOS no proprio site italiano — identidade '
             'de conta provada pela empresa, que e exatamente o portao que reprovou a coleta '
             'espanhola de Instagram.'),
      achada='colheita de perfis declarados no site do concorrente', query='FMC Agro Italia sito',
      metodo='Instagram publico + YouTube', scrap='YES', video='YES', transcricao='YES',
      freq='PERIODIC', acesso='GREEN', coleta='AUTOMATABLE', monitor='MONITOR_WEEKLY',
      dedupe='SRC_AG_FMC_COM', dedupe_means='mesma empresa; os canais sociais italianos sao novos',
      nota='PRODUTO DE CONCORRENTE != PRODUTO ADAMA. O canal prova comunicacao, nunca share.',
      prova='probe/c3.json#FMC_IT HTTP 200 · sociais declarados'),

    F('IT-SRCX-025',
      'Certis Belchim Italia',
      'Certis Belchim', 'COMPETITOR_CHANNEL', 'COMPETITOR', 'MEDIUM',
      'https://www.certisbelchim.it/',
      regiao='ITALIA', feed='https://certisbelchim.it/feed/',
      crops=['SOIA', 'BRASSICACEE', 'LEGUMINOSE', 'FLOREALI'],
      temas=['USI_DI_EMERGENZA', 'DEROGHE', 'REGISTRAZIONI'],
      razao=('Concorrente ausente do acervo, e o feed dele publica exatamente USI DI EMERGENZA — '
             'a mesma classe de evento regulatorio que a ADAMA usa (deroga = janela curta e '
             'datada). E competitor signal com data, nao institucional.'),
      achada='busca composta por lista de concorrentes reais no universo italiano',
      query='Nufarm Italia Sipcam Gowan Albaugh Certis Belchim sito italiano prodotti difesa colture',
      metodo='RSS', freq='EVENT_DRIVEN', ultimo='2024-06-25', acesso='GREEN',
      coleta='AUTOMATABLE', monitor='EVENT_DRIVEN',
      nota=('feed com 7 itens, o mais recente de 2024-06-25 (800 dias). FEED PARADO != EMPRESA '
            'PARADA: mede o feed, nao a empresa. Por isso EVENT_DRIVEN e nao WEEKLY.'),
      prova='probe/f1.json#CERTISBELCHIM 7 itens latest 2024-06-25 age 800'),

    F('IT-SRCX-026',
      'Nufarm Italia',
      'Nufarm', 'COMPETITOR_CHANNEL', 'COMPETITOR', 'MEDIUM',
      'https://nufarm.com/it/',
      regiao='ITALIA',
      social={'LINKEDIN': 'https://www.linkedin.com/company/nufarm',
              'FACEBOOK': 'https://www.facebook.com/Nufarm-Italia-2312073685546312'},
      crops=['FRUMENTO', 'MAIS', 'VITE'], temas=['ERBICIDI', 'PORTAFOGLIO'],
      razao=('Nufarm ja aparece no lote congelado de comunicacao publica (3 contas), mas o SITE '
             'italiano nao estava no acervo de fontes. Concorrente direto no bloco de erbicidi, '
             'que e onde a ADAMA Italia tem 26 dos 51 produtos comerciais.'),
      achada='busca por concorrentes presentes no universo italiano', query='Nufarm Italia sito prodotti',
      metodo='HTML + LinkedIn publico', freq='PERIODIC', acesso='GREEN', coleta='PARTIAL',
      monitor='MONITOR_MONTHLY',
      prova='probe/c1.json#NUFARM_IT HTTP 200'),

    F('IT-SRCX-027',
      'Gowan Italia',
      'Gowan Italia', 'COMPETITOR_CHANNEL', 'COMPETITOR', 'MEDIUM',
      'https://www.gowanitalia.it/',
      regiao='ITALIA',
      social={'YOUTUBE': 'https://www.youtube.com/user/GowanItalia',
              'FACEBOOK': 'https://www.facebook.com/gowanitalia'},
      crops=['VITE', 'POMODORO', 'MELO'], temas=['DIFESA_VITE', 'PORTAFOGLIO'],
      razao=('Concorrente italiano ausente do acervo, com comunicacao tecnica ativa sobre difesa '
             'da vite — a cultura de duas oportunidades confirmadas. Canal de video proprio.'),
      achada='busca por concorrentes presentes no universo italiano; confirmado por citacao em AgroNotizie',
      query='Nufarm Italia Sipcam Gowan Albaugh Certis Belchim sito italiano',
      metodo='HTML + YouTube', video='YES', transcricao='YES', freq='PERIODIC',
      acesso='GREEN', coleta='PARTIAL', monitor='MONITOR_MONTHLY',
      prova='probe/c1.json#GOWAN_IT HTTP 200'),
]


# ── REJEICOES ──────────────────────────────────────────────────────────────────
# Uma rejeicao com motivo escrito vale tanto quanto uma fonte: ela impede a
# proxima passagem de gastar o mesmo tempo no mesmo beco.
#
#     REJEITADA POR MOTIVO != NAO ALCANCADA.
#     A primeira e uma decisao. A segunda e um estado da rede.

REJEITADAS = [
    {'NAME': 'image-line.com', 'URL': 'https://www.image-line.com/',
     'REJECTION_CLASS': 'WRONG_ENTITY_SAME_NAME',
     'REASON': ('esta no acervo canonico V2.1 como SRC_IMAGE_LINE_COM, TYPE=TECHNICAL_MEDIA, '
                'ACCESS_STATUS=GREEN e SEM CAMPO NAME. Lido em 2026-09-03: e a FL Studio, '
                'software de producao MUSICAL da Image Line Software (Belgica). A editora '
                'agricola italiana e a Image Line s.r.l., em imagelinenetwork.com. Duas '
                'empresas homonimas. Mesma familia do caso `repilouk` da Espanha, onde o nome '
                'de uma doenca era a marca de outra empresa.'),
     'ACTION': 'CORRIGIR NO ACERVO CANONICO: separar SRC_IMAGE_LINE_COM de SRC_IMAGELINENETWORK_COM',
     'EVIDENCE': 'probe/f2.json#IMAGELINE (feed anuncia FL Studio 2026) · probe/c4.json#IMAGE_LINE_NETWORK'},

    {'NAME': 'sipcamitalia.it / sipcam.it', 'URL': 'https://www.sipcamitalia.it/',
     'REJECTION_CLASS': 'WRONG_ENTITY_FOR_THE_GEOGRAPHY',
     'REASON': ('os dois hosts servem a mesma pagina, intitulada "Sipcam Agro USA". Nao e a '
                'entidade italiana. Registrar isto como concorrente ITALIANO seria inventar '
                'geografia a partir de um nome de dominio.'),
     'ACTION': 'a entidade italiana da Sipcam fica NAO_SEI ate rota provada',
     'EVIDENCE': 'probe/c1.json#SIPCAM_IT e probe/c2.json#SIPCAM_IT2, ambos HTTP 200, mesmo titulo'},

    {'NAME': 'betaitalia.it', 'URL': 'https://www.betaitalia.it/',
     'REJECTION_CLASS': 'WRONG_ENTITY_SAME_NAME',
     'REASON': ('procurada como o centro de pesquisa da bietola (Beta). O host responde '
                '"Beta Italia - Cucina, Casa e Giardinaggio". A busca por nome de instituicao '
                'nao resolve identidade — foi o que se tentou aqui e nao funcionou.'),
     'ACTION': 'centro de pesquisa da barbabietola fica NAO_SEI; procurar por publicacao, nao por dominio',
     'EVIDENCE': 'probe/c1.json#BETA_RICERCA'},

    {'NAME': 'perfis Instagram genericos de "azienda agricola"', 'URL': 'https://www.instagram.com/',
     'REJECTION_CLASS': 'NO_ADAMA_RELEVANCE',
     'REASON': ('a busca `site:instagram.com "azienda agricola" mais soia diserbo` devolveu '
                'sobretudo apicultura, laticinios, horta biologica e agriturismo. Sao contas '
                'reais e agricolas, e nao observam nenhuma cultura, alvo, molecula ou regiao '
                'do radar ADAMA Italia. Volume nao e relevancia.'),
     'ACTION': 'nao entram no acervo; a rota de descoberta social passa por site institucional, nao por busca livre',
     'EVIDENCE': 'busca registrada em 2026-09-03; nenhuma conta promovida'},

    {'NAME': 'canais YouTube de horta e hobby ja presentes no acervo canonico',
     'URL': 'https://www.youtube.com/',
     'REJECTION_CLASS': 'LOW_RELEVANCE_ALREADY_REGISTERED',
     'REASON': ('dos 62 PUBLIC_CHANNEL do pacote V2.1, uma parte relevante e horticultura '
                'domestica (Passione Orto, Orto Da Coltivare, Piccoli Orti Grandi Raccolti, '
                'Your Hobby, Dall Orto alla Tavola) e ha canais que nao sao italianos '
                '(Cornell SIPS, INTA Chubut, Aragon TV, Laderas del Naranco). Nao proponho '
                'apagar: proponho marcar RELEVANCE=LOW e COUNTRY!=IT, para que a contagem '
                'de "62 canais" pare de sugerir 62 canais tecnicos italianos.'),
     'ACTION': 'REVISAR no acervo canonico — nao apagar, reclassificar',
     'EVIDENCE': 'v21/publicChannels.json, 62 registros lidos um a um'},
]

# ── ROTAS QUE NAO ABRIRAM DAQUI ────────────────────────────────────────────────
# Estado da REDE desta sessao, nunca estado do mundo.
NAO_ALCANCADAS = [
    {'HOST': 'googlevideo.com (midia do YouTube)', 'STATE': 'EGRESS_POLICY_403',
     'MEANS': ('a politica de saida desta sessao recusa binario de midia desses hosts. Os '
               'METADADOS do YouTube (lista de videos, titulo, duracao) VOLTARAM normalmente. '
               'Logo: enumerar canal, sim; baixar audio para transcrever, nao — daqui.')},
    {'HOST': 'instagram.com (pagina de perfil)', 'STATE': 'HTTP_302_TO_LOGIN',
     'MEANS': ('a rota de perfil deslogado redireciona. A rota de EMBED de POST devolveu HTTP 200 '
               'com 628 KB. O que falta e o shortcode do post, que a rota do navegador do '
               'Sintonia Scrap obtem — e o Chrome nao passa pelo proxy desta sessao '
               '(ERR_CONNECTION_RESET em todo host, google.com incluido).')},
    {'HOST': 'adama.com · syngenta.it/news · cropscience.bayer.it', 'STATE': 'HTTP_403',
     'MEANS': 'ROUTE_BLOCKED_FOR_AUTOMATION != CATALOG_EMPTY. Ja era conhecido do censo do catalogo.'},
    {'HOST': 'enterisi.it', 'STATE': 'TLS_DH_KEY_TOO_SMALL',
     'MEANS': ('esta GREEN no acervo canonico e hoje nao negocia TLS com cliente moderno. '
               'E estado da fonte, e a verificacao nao foi desligada para contornar.')},
    {'HOST': 'ismea.it · confagricoltura.it · emergenzaxylella.it · cnr ipsp.cnr.it',
     'STATE': 'TLS_CERTIFICATE_VERIFY_FAILED',
     'MEANS': 'idem — cadeia incompleta ou hostname divergente. Registrado, nao contornado.'},
    {'HOST': 'melinda.it · prodottifitosanitari.net · disafa.unito.it · consorziagrari.it',
     'STATE': 'CONNECTION_RESET_BY_PEER',
     'MEANS': 'nao alcancadas daqui. NAO_SEI, nunca RED.'},
]


# ── ESCRITA E PLACAR ───────────────────────────────────────────────────────────
def placar():
    from collections import Counter
    return {
        'SOURCES_QUALIFIED': len(FONTES),
        'BY_RELEVANCE': dict(Counter(f['RELEVANCE'] for f in FONTES)),
        'BY_AUTHORITY': dict(Counter(f['AUTHORITY_CLASS'] for f in FONTES)),
        'BY_COLLECTABILITY': dict(Counter(f['COLLECTABILITY'] for f in FONTES)),
        'BY_MONITORING': dict(Counter(f['MONITORING_RECOMMENDATION'] for f in FONTES)),
        'BY_UPDATE_FREQUENCY': dict(Counter(f['UPDATE_FREQUENCY'] for f in FONTES)),
        'WITH_FEED_OR_API': sum(1 for f in FONTES if f['RSS_API'] != NAO_SEI),
        'WITH_SOCIAL_DECLARED': sum(1 for f in FONTES if f['SOCIAL_PROFILE_URLS']),
        'SOCIAL_PROFILES_DECLARED': sum(len(f['SOCIAL_PROFILE_URLS']) for f in FONTES),
        'SINTONIA_SCRAP_SUPPORTED': sum(1 for f in FONTES if f['SINTONIA_SCRAP_SUPPORTED'] == 'YES'),
        'TRANSCRIPTION_RELEVANT': sum(1 for f in FONTES if f['TRANSCRIPTION_RELEVANT'] == 'YES'),
        'NEW_CHANNEL_OF_REGISTERED_ORG': sum(1 for f in FONTES if f['DEDUPE_AGAINST']),
        'REJECTED': len(REJEITADAS),
        'ROUTES_NOT_REACHED': len(NAO_ALCANCADAS),
    }


def dedupe_check():
    """Nenhum SOURCE_ID repetido, nenhuma PRIMARY_URL repetida. Falhar alto e melhor
    que descobrir duplicata depois, dentro do portal."""
    ids = [f['SOURCE_ID'] for f in FONTES]
    urls = [f['PRIMARY_URL'] for f in FONTES]
    dup_id = {x for x in ids if ids.count(x) > 1}
    dup_url = {x for x in urls if urls.count(x) > 1}
    return {'DUPLICATE_SOURCE_ID': sorted(dup_id), 'DUPLICATE_PRIMARY_URL': sorted(dup_url),
            'DEDUPE': 'PASS' if not dup_id and not dup_url else 'FAIL'}


def escrever():
    os.makedirs(SAIDA, exist_ok=True)
    corpo = {
        'DATASET': 'IT-FONTES-V1',
        'LAYER': 'SOURCE_DISCOVERY_ITALY',
        'COUNTRY': 'IT',
        'SOURCE': ('descoberta propria: buscas compostas em italiano, snowballing a partir de '
                   'documento oficial, e verificacao HTTP direta de cada host. Cada ficha carrega '
                   'DISCOVERY_QUERY, DISCOVERED_FROM e EVIDENCE_PROBE.'),
        'SOURCE_ID': 'IT-FONTES-V1',
        'CAPTURED_AT': CAPTURA,
        'BUILT_AT': CAPTURA,
        'OWNER_OF_THE_QUESTION': 'docs/fontes/ATLAS-DE-FONTES-EAME.md',
        'NOT_A_SECOND_OWNER': ('esta camada e DESCOBERTA. O Atlas continua dono do catalogo, e o '
                               'pacote V2.1 continua dono dos 189 SOURCE canonicos. Cada ficha '
                               'que toca uma organizacao ja registrada traz DEDUPE_AGAINST.'),
        'ENTITY_VS_CHANNEL': ('ORGANIZACAO e CANAL sao unidades diferentes. A mesma instituicao '
                              'pode ser site, feed, perfil e API — e cada uma quebra de um jeito. '
                              'Dedupe une organizacao; nao colapsa canal.'),
        'FIELD_LAW': 'campo sem leitura real fica NAO_SEI; nunca preenchido por plausibilidade',
        'SCOREBOARD': placar(),
        'DEDUPE': dedupe_check(),
        'SOURCES': FONTES,
        'REJECTED': REJEITADAS,
        'ROUTES_NOT_REACHED_FROM_THIS_SESSION': NAO_ALCANCADAS,
    }
    caminho = os.path.join(SAIDA, 'IT-FONTES-DESCOBERTA-V1.json')
    with open(caminho, 'w', encoding='utf-8') as fh:
        json.dump(corpo, fh, ensure_ascii=False, indent=1)
    return caminho


if __name__ == '__main__':
    p = placar()
    d = dedupe_check()
    if '--placar' not in sys.argv:
        caminho = escrever()
        print('escrito: %s' % os.path.relpath(caminho, ROOT))
    print()
    for k, v in p.items():
        print('%-32s %s' % (k, v))
    print('%-32s %s' % ('DEDUPE', d['DEDUPE']))
    if d['DEDUPE'] != 'PASS':
        print('   ids duplicados : %s' % d['DUPLICATE_SOURCE_ID'])
        print('   urls duplicadas: %s' % d['DUPLICATE_PRIMARY_URL'])
        sys.exit(1)
