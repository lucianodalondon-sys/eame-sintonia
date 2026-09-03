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


# ── FONTES TRAZIDAS PELA PASSAGEM PARALELA ─────────────────────────────────────
# Seis agentes varreram eixos independentes (social, agromet/modelos, resistencia,
# mercado/distribuicao, concorrente, eventos/regulatorio) com a mesma lei: nada entra
# sem leitura HTTP real. O que segue e o que sobreviveu a verificacao.

FONTES += [

    F('IT-SRCX-028',
      'ARPAE Emilia-Romagna — ERG5 open data, serie horaria por estacao',
      'Arpae — Servizio IdroMeteoClima (SIMC)', 'AGROMET_OPEN_DATA', 'OFFICIAL', 'HIGH',
      'https://dati-simc.arpae.it/opendata/erg5v2/timeseries/',
      regiao='Emilia-Romagna',
      feed='https://dati-simc.arpae.it/opendata/erg5v2/timeseries/<stazione>/<stazione>_<ano>.zip',
      crops=['BARBABIETOLA', 'POMODORO', 'MELO', 'PERO', 'VITE', 'MAIS', 'FRUMENTO'],
      temas=['AGROMETEO', 'TEMPERATURA', 'PIOGGIA', 'UMIDITA', 'GRADI_GIORNO'],
      razao=('e a variavel de entrada dos modelos previsionais que decidem QUANDO tratar — '
             'CERCOPRI/CERCODEP na barbabietola sao alimentados por temperatura, umidade relativa '
             'e chuva. Sem serie horaria, "janela" e calendario; com ela, e modelo. E a regiao e '
             'a mesma de 4 das 37 oportunidades e de toda a serie da cimice.'),
      achada='varredura paralela do eixo agromet/modelos previsionais',
      query='ARPAE ERG5 open data timeseries agrometeo Emilia-Romagna',
      metodo='HTTP + ZIP por estacao e ano', freq='FREQUENT', acesso='GREEN',
      coleta='AUTOMATABLE', monitor='MONITOR_DAILY',
      dedupe='SRC_ARPAE_IT',
      dedupe_means=('mesma agencia; o registro V2.1 aponta para o portal institucional, este aponta '
                    'para o endpoint de dado bruto. Portal e dado sao pontos de coleta diferentes.'),
      prova='wf_agromet-forecast-models.json · HTTP 200 · indice 127.451 B · pacote de estacao 90.399 B'),

    F('IT-SRCX-029',
      'OSMER ARPA FVG — previsioni e stazioni em XML',
      'ARPA FVG — Osservatorio Meteorologico Regionale', 'AGROMET_OPEN_DATA', 'OFFICIAL', 'MEDIUM',
      'https://dev.meteo.fvg.it/',
      regiao='Friuli-Venezia Giulia',
      feed='https://dev.meteo.fvg.it/xml/previsioni/PW<AAAAMMDD>.xml · /xml/stazioni/<COD>.xml',
      crops=['MELO', 'MAIS', 'SOIA', 'VITE'],
      temas=['PREVISIONE', 'STAZIONI', 'AGROMETEO'],
      razao=('FVG e a geografia de OPP_9C600748BB1B (mais x piralide) e OPP_F139E05A9F3A. A rota XML '
             'e datada no proprio nome do arquivo, o que torna a coleta reproduzivel sem raspagem.'),
      achada='varredura paralela do eixo agromet', query='OSMER ARPA FVG xml previsioni stazioni',
      metodo='HTTP + XML', freq='FREQUENT', ultimo='2026-09-03', acesso='GREEN',
      coleta='AUTOMATABLE', monitor='MONITOR_DAILY',
      prova='wf_agromet-forecast-models.json · PW20260903.xml HTTP 200, 52.212 B'),

    F('IT-SRCX-030',
      'Meteotrentino — web service de estacoes e ultimo dato',
      'Provincia Autonoma di Trento', 'AGROMET_OPEN_DATA', 'OFFICIAL', 'MEDIUM',
      'https://dati.meteotrentino.it/service.asmx',
      regiao='Trentino',
      feed='https://dati.meteotrentino.it/service.asmx/listaStazioni · /getLastDataOfMeteoStation?codice=<COD>',
      crops=['MELO', 'VITE'], temas=['AGROMETEO', 'STAZIONI'],
      razao=('Trentino e a geografia de OPP_75C37DED9160 (melo x carpocapsa) e das crop windows de '
             'melo; MELO tem 146 pares de rotulo ADAMA. O servico responde sem chave e publica WSDL.'),
      achada='varredura paralela do eixo agromet', query='dati.meteotrentino.it service asmx listaStazioni',
      metodo='HTTP SOAP/REST', freq='FREQUENT', acesso='GREEN', coleta='AUTOMATABLE',
      monitor='MONITOR_DAILY',
      prova='wf_agromet-forecast-models.json · listaStazioni 73.687 B · WSDL 313.725 B'),

    F('IT-SRCX-031',
      'Open Data Regione Lombardia — sensori meteo (Socrata)',
      'Regione Lombardia', 'AGROMET_OPEN_DATA', 'OFFICIAL', 'MEDIUM',
      'https://www.dati.lombardia.it/resource/nf78-nj6b.json',
      regiao='Lombardia',
      feed='API Socrata, JSON, parametros $limit e $where',
      crops=['MAIS', 'RISO', 'VITE', 'BARBABIETOLA'],
      temas=['AGROMETEO', 'SENSORI'],
      razao=('Lombardia e a geografia de OPP_F6EEF5B32F65 (mais x diabrotica) e OPP_8E210567B01F. '
             'MAIS tem 112 pares de rotulo ADAMA.'),
      achada='varredura paralela do eixo agromet', query='dati.lombardia.it resource sensori meteo json',
      metodo='API Socrata JSON', freq='FREQUENT', acesso='GREEN', coleta='AUTOMATABLE',
      monitor='MONITOR_DAILY',
      prova='wf_agromet-forecast-models.json · duas rotas HTTP 200'),

    F('IT-SRCX-032',
      'Horta s.r.l. — DSS agronomicos (vite.net e familia)',
      'Horta s.r.l., spin-off da Universita Cattolica del Sacro Cuore', 'DSS_COMMERCIAL',
      'TECHNICAL', 'HIGH',
      'https://www.horta-srl.it/',
      regiao='ITALIA',
      crops=['VITE', 'FRUMENTO', 'POMODORO', 'OLIVO', 'MELO'],
      temas=['MODELLI_PREVISIONALI', 'DSS', 'DIFESA_INTEGRATA'],
      razao=('e o maior DSS agronomico comercial italiano e nasceu da MESMA universidade que assina '
             'CERCOPRI/CERCODEP. Quem opera o modelo que decide a janela e um ator do mercado que a '
             'ADAMA precisa enxergar — nao um portal de noticia.'),
      achada='varredura paralela do eixo agromet/modelos',
      query='horta srl vite.net DSS modelli previsionali Italia',
      metodo='HTML + sitemap + WP REST', freq='STATIC', ultimo='2024-10-16', acesso='YELLOW',
      coleta='PARTIAL', monitor='MONITOR_MONTHLY',
      nota=('horta-srl.COM nao alcancado (Recv failure) e vite.net recusou o tunel; horta-srl.IT '
            'responde 200 com 1,07 MB. O canal de noticias esta parado desde 2024-10-16 e o DSS '
            'em si vive atras de login. CANAL PARADO != EMPRESA PARADA.'),
      prova='wf_agromet-forecast-models.json · home 1.079.490 B · wp-json posts, mais recente 2024-10-16'),

    F('IT-SRCX-033',
      'Ri.Nova soc. coop. — a cooperativa de pesquisa dos Gruppi Operativi da Emilia-Romagna',
      'Ri.Nova soc. coop.', 'RESEARCH_COOPERATIVE', 'SCIENTIFIC', 'HIGH',
      'https://www.linkedin.com/company/rinovaricerca',
      regiao='Emilia-Romagna', plataforma='LINKEDIN',
      social={'LINKEDIN': 'https://www.linkedin.com/company/rinovaricerca',
              'YOUTUBE': 'https://www.youtube.com/@rinovaricerche',
              'INSTAGRAM': 'https://www.instagram.com/ri.nova.soc.coop/'},
      crops=['MELO', 'PERO', 'SUSINO', 'PATATA', 'VITE', 'POMODORO'],
      temas=['GRUPPI_OPERATIVI', 'DIFESA', 'MONITORAGGIO', 'RIDUZIONE_INPUT'],
      razao=('e o fio que amarra tres coisas que ja estao neste acervo e pareciam separadas: a nota '
             'tecnica da cimice do Servizio Fitosanitario ER pede que os tecnicos falem com a Ri.Nova '
             'para alimentar a rede de trappole; os projetos que o Agricast narra sao Gruppi Operativi '
             'que ela coordena; e as culturas sao as de OPP_20D89B04F64D, OPP_DA4B5954F72A e '
             'OPP_75C37DED9160. Uma fonte que EXPLICA as outras vale mais que uma fonte a mais.'),
      achada='snowballing duplo: nome impresso no PDF da nota tecnica da cimice, e de novo na varredura social',
      query='Ri.Nova gruppi operativi Emilia-Romagna ricerca',
      metodo='LinkedIn publico + YouTube (feed RSS por channel_id) + Instagram',
      scrap='YES', video='YES', transcricao='YES',
      freq='PERIODIC', acesso='GREEN', coleta='AUTOMATABLE', monitor='MONITOR_MONTHLY',
      prova='wf_social-technical-voices.json · LinkedIn 355.264 B · YouTube 1.350.501 B'),

    F('IT-SRCX-034',
      'Fondazione Agrion — ricerca frutticola e viticola del Piemonte',
      'Fondazione per la ricerca l innovazione e lo sviluppo tecnologico dell agricoltura piemontese',
      'RESEARCH_FOUNDATION', 'SCIENTIFIC', 'HIGH',
      'https://www.linkedin.com/company/fondazione-agrion',
      regiao='Piemonte', plataforma='LINKEDIN',
      social={'LINKEDIN': 'https://www.linkedin.com/company/fondazione-agrion',
              'INSTAGRAM': 'https://www.instagram.com/fondazioneagrion/'},
      crops=['MELO', 'PESCO', 'ACTINIDIA', 'VITE', 'NOCCIOLO'],
      temas=['SPERIMENTAZIONE', 'DIFESA', 'VARIETA'],
      razao=('Piemonte e a geografia de OPP_4C39CCC05EEB (riso x Echinochloa) e de duas crop windows '
             'de vite e mais; e a regiao nao tinha, no acervo, nenhum centro de pesquisa aplicada '
             'proprio — so o servico fitossanitario.'),
      achada='varredura paralela do eixo social/tecnico',
      query='Fondazione Agrion Piemonte ricerca frutticola',
      metodo='LinkedIn publico + Instagram', scrap='YES', freq='PERIODIC', acesso='GREEN',
      coleta='PARTIAL', monitor='MONITOR_MONTHLY',
      prova='wf_social-technical-voices.json · LinkedIn HTTP 200, 290.219 B'),

    F('IT-SRCX-035',
      'CSO Italy — Centro Servizi Ortofrutticoli',
      'CSO Italy', 'MARKET_SERVICE', 'INDUSTRY', 'MEDIUM',
      'https://www.csoservizi.com/',
      regiao='ITALIA',
      social={'LINKEDIN': 'https://it.linkedin.com/company/cso---centro-servizi-ortofrutticoli'},
      crops=['MELO', 'PERO', 'PESCO', 'ACTINIDIA', 'FRAGOLA'],
      temas=['PREVISIONE_PRODUZIONE', 'MERCATO_ORTOFRUTTA', 'SUPERFICI'],
      razao=('publica previsao de producao e superficie das pomacee — o DENOMINADOR das culturas de '
             'quatro oportunidades de melo e pero. Sem denominador, "sinal em melo" nao tem escala.'),
      achada='varredura paralela do eixo social/tecnico', query='CSO Centro Servizi Ortofrutticoli previsione produzione',
      metodo='HTML + LinkedIn publico', freq='PERIODIC', acesso='GREEN', coleta='PARTIAL',
      monitor='MONITOR_MONTHLY',
      nota=('PREVISAO DE PRODUCAO != MERCADO ENDERECAVEL. E denominador de cultura, e so. '
            'HANDLE_NAO_RECONFIRMADO: em 2026-09-03 reli csoservizi.com (200 / 50.746 B) e a '
            'pagina NAO declara nenhum link social. O handle de LinkedIn fica registrado mas '
            'NAO entra em coleta ate ser declarado na casa do dono. Ver FIX-02.'),
      prova='wf_social-technical-voices.json · HTTP 200 (prova de agente, NAO reconfirmada por mim)'),

    F('IT-SRCX-036',
      'YouTube — rota de feed por channel_id (descoberta de video datada, sem chave)',
      'YouTube', 'VIDEO_DISCOVERY_ROUTE', 'MEDIA', 'HIGH',
      'https://www.youtube.com/feeds/videos.xml?channel_id=<ID>',
      regiao='ITALIA', plataforma='YOUTUBE',
      feed='https://www.youtube.com/feeds/videos.xml?channel_id=<ID>',
      crops=['TODAS'], temas=['VIDEO', 'FALA_TECNICA'],
      razao=('a REGRA DE COLETA EXTERNA poe VIDEO/TRANSCRIPT em primeiro lugar, e mede: 15 videos '
             'espanhois deram 705.149 caracteres de fala tecnica. Esta rota lista os videos de um '
             'canal COM DATA, em XML, sem chave e sem raspagem — e resolve a metade da coleta que '
             'esta sessao consegue fazer.'),
      achada='varredura paralela do eixo social; validada em 7 canais italianos',
      query='youtube.com/feeds/videos.xml?channel_id=',
      metodo='HTTP + XML', video='YES', transcricao='PARCIAL', freq='FREQUENT', acesso='GREEN',
      coleta='PARTIAL', monitor='MONITOR_WEEKLY',
      nota=('a METADE que nao funciona daqui: o binario de audio vem de googlevideo.com e a politica '
            'de saida desta sessao devolve HTTP 403. Listar canal, sim; transcrever, so na maquina '
            'que tem a rota. A transcricao em si ja esta provada nesta sessao — 118,7 min de audio '
            'italiano a ~9x tempo real, custo 0 USD, por outra plataforma.'),
      prova='wf_social-technical-voices.json · 7 feeds channel_id HTTP 200, 18 a 39 KB cada'),
]


# ── SEGUNDA LEVA DA PASSAGEM PARALELA ──────────────────────────────────────────
FONTES += [

    F('IT-SRCX-037',
      'Corteva — Mappa Piralide, monitoraggio pubblico della piralide del mais',
      'Corteva Agriscience — Servizio Agronomico Pioneer', 'COMPETITOR_FIELD_SERVICE',
      'COMPETITOR', 'HIGH',
      'https://www.corteva.com/it/prodotti-e-soluzioni/servizi-agronomici/monitoraggio-fitofagi/mappa-piralide.html',
      regiao='Nord Italia (ambienti maidicoli)',
      crops=['MAIS'], temas=['PIRALIDE', 'FINESTRA_DI_TRATTAMENTO', 'MONITORAGGIO'],
      razao=('e a coisa mais desconfortavel que esta missao achou: um CONCORRENTE publica de '
             'graca, datado e assinado, a JANELA DE TRATAMENTO da piralide no mais do norte da '
             'Italia — "Previsione dell insetto al 24 luglio 2026", a cura del Servizio '
             'Agronomico Pioneer, com 200 tecnicos declarados em campo. MAIS tem 112 pares de '
             'rotulo ADAMA e e a cultura de OPP_9C600748BB1B e OPP_8E210567B01F. Isto nao e '
             'pagina institucional: e servico de campo virado comunicacao.'),
      achada='varredura paralela do eixo concorrente, alem da home corporativa',
      query='corteva.com/it servizi agronomici monitoraggio fitofagi mappa piralide',
      metodo='HTML datado', freq='PERIODIC', ultimo='2026-07-24', acesso='GREEN',
      coleta='AUTOMATABLE', monitor='MONITOR_WEEKLY',
      dedupe='SRC_CORTEVA_IT',
      dedupe_means='mesma empresa; o SERVICO de monitoramento e um canal distinto da home',
      nota=('COMUNICACAO DE CONCORRENTE != DADO DE CAMPO NOSSO. O que a pagina prova e que a '
            'Corteva DIZ isso naquela data, e que ela escolhe competir por servico agronomico.'),
      prova='wf_competitor-italian-channels.json#content_evidence · HTTP 200 · 154.569 B'),

    F('IT-SRCX-038',
      'COMPAG — Federazione Nazionale Commercianti Prodotti per l Agricoltura',
      'COMPAG', 'DISTRIBUTION_ASSOCIATION', 'INDUSTRY', 'HIGH',
      'https://www.compag.org/',
      regiao='ITALIA',
      crops=['TODAS'], temas=['DISTRIBUZIONE', 'RIVENDITA', 'NORMATIVA', 'FORMAZIONE'],
      razao=('e a associacao da REVENDA italiana de insumos — a camada que decide o que chega ao '
             'produtor e que estava inteiramente ausente do acervo canonico. Sem ela, "mercado" '
             'na Italia era so preco de commodity.'),
      achada='varredura paralela do eixo mercado/distribuicao',
      query='COMPAG federazione commercianti prodotti agricoltura notizie eventi',
      metodo='HTML', freq='PERIODIC', acesso='GREEN', coleta='PARTIAL', monitor='MONITOR_MONTHLY',
      nota='ASSOCIACAO DE REVENDA != CANAL DA ADAMA. Ela prova o que publica, nunca share.',
      prova='wf_market-distribution.json · compag.org e compag.org/notizie-ed-eventi HTTP 200'),

    F('IT-SRCX-039',
      'CUN — Commissioni Uniche Nazionali, listini ufficiali',
      'Ministero / listinicun.it', 'MARKET_PRICE_OFFICIAL', 'OFFICIAL', 'MEDIUM',
      'https://www.listinicun.it/',
      regiao='ITALIA',
      crops=['FRUMENTO', 'MAIS', 'SOIA'], temas=['PREZZI', 'LISTINI'],
      razao=('preco oficial datado de grano duro, mais e soia — as culturas de tres das nove '
             'confirmadas. O acervo tinha Eurostat e ISMEA; nao tinha o listino nacional que o '
             'proprio setor usa como referencia.'),
      achada='varredura paralela do eixo mercado', query='listini CUN grano duro mais soia 2026',
      metodo='HTML + arquivo de listino datado', freq='FREQUENT', ultimo='2026-08-31',
      acesso='GREEN', coleta='AUTOMATABLE', monitor='MONITOR_WEEKLY',
      nota='PRECO DE COMMODITY != DEMANDA DE AGROFARMACO. Serve para timing de campanha.',
      prova='wf_market-distribution.json · listino Grano Duro de 2026-08-31 baixado'),

    F('IT-SRCX-040',
      'GIRE — Gruppo Italiano Resistenza Erbicidi (host corrente)',
      'CNR — Istituto per la Protezione Sostenibile delle Piante (IPSP)',
      'RESISTANCE_REGISTRY', 'SCIENTIFIC', 'HIGH',
      'http://gire.ipsp.cnr.it/index.php',
      regiao='ITALIA (por regiao)',
      crops=['RISO', 'FRUMENTO', 'MAIS', 'SOIA', 'BARBABIETOLA'],
      temas=['RESISTENZA_ERBICIDI', 'HRAC', 'SCHEDE_SPECIE', 'LINEE_GUIDA_DISERBO'],
      razao=('erbicidi sao 26 dos 51 produtos comerciais da ADAMA Italia, e resistencia e o '
             'mecanismo que aposenta um modo de acao. O GIRE publica ficha por especie e por '
             'regiao — e o acervo canonico aponta para gire.mlib.cnr.it, um host antigo.'),
      achada='varredura paralela do eixo resistencia/ciencia',
      query='GIRE gruppo italiano resistenza erbicidi schede specie Echinochloa',
      metodo='HTML + PDF', freq='PERIODIC', acesso='GREEN', coleta='PARTIAL',
      monitor='MONITOR_MONTHLY',
      dedupe='SRC_GIRE_MLIB_CNR_IT',
      dedupe_means=('MESMA base, HOST NOVO. O registro canonico aponta para gire.mlib.cnr.it; '
                    'gire.ipsp.cnr.it e o endereco corrente, sob o IPSP-CNR. Nao sao duas fontes.'),
      nota=('CONTRADICAO A CARREGAR: o GIRE declara Echinochloa crus-galli resistente a propanil '
            '(HRAC 5 / C2) em Piemonte, Lombardia e Toscana desde 2000; o sumario por pais do '
            'weedscience.org lido em 2026-09-03 mostra a Italia com ZERO no grupo HRAC 5. Dois '
            'registros e duas contagens. Isto e INVESTIGATE, nao um numero a escolher.'),
      prova='wf_resistance-and-science.json#contradiction_to_carry_forward'),
]


FONTES += [
    F('IT-SRCX-041',
      'Ministero della Salute — autorizzazioni in situazioni di emergenza fitosanitaria (art. 53)',
      'Ministero della Salute', 'REGULATORY_EMERGENCY_REGISTER', 'OFFICIAL', 'HIGH',
      'https://www.salute.gov.it/new/it/tema/prodotti-fitosanitari/autorizzazioni-situazioni-emergenza-fitosanitaria-art-53-reg-11072009/',
      regiao='ITALIA (nacional, com deroga regional dentro)',
      crops=['TODAS'], temas=['DEROGA', 'USO_ECCEZIONALE', 'ART_53', 'JANELA_DATADA'],
      razao=('e a FONTE NACIONAL das deroghe que esta missao so tinha achado de segunda mao, '
             'dentro dos bollettini regionais. Uma deroga do art. 53 traz substancia, cultura, '
             'alvo e JANELA COM DATA DE ABERTURA E DE FECHAMENTO — e data futura publicada e a '
             'unica antecipacao que este sistema ja provou. Os PDFs sao datados no proprio nome '
             '("integrazione pubblicazione del 5 agosto 2026").'),
      achada='varredura paralela do eixo eventos/calendario regulatorio',
      query='salute.gov.it autorizzazioni situazioni emergenza fitosanitaria art 53',
      metodo='HTML + PDF datado', freq='PERIODIC', ultimo='2026-08-05', acesso='GREEN',
      coleta='AUTOMATABLE', monitor='MONITOR_MONTHLY',
      dedupe='SRC_SALUTE_GOV_IT · SRC_FITOSANITARI_SALUTE_GOV_IT',
      dedupe_means=('mesmo ministerio, TERCEIRO canal: o registro de produto e uma coisa, a banca '
                    'dati e outra, e o registro de uso excepcional e uma terceira. Cada um quebra '
                    'de um jeito e cada um responde uma pergunta diferente.'),
      nota=('DEROGA != REGISTRO. Ela abre uma janela curta e datada, e fecha. Nao vira '
            'autorizacao de rotulo.'),
      prova='wf_events-and-regulatory-calendar.json#verified_future_dates · PDFs de 05/08/2026 e 08/05/2026 baixados'),

    F('IT-SRCX-042',
      'ARPAV — revoche dei prodotti fitosanitari, tabella delle sostanze',
      'ARPA Veneto', 'REGULATORY_WITHDRAWAL_TABLE', 'OFFICIAL', 'HIGH',
      'https://www.arpa.veneto.it/temi-ambientali/agrometeo/servizi/revoche-fitosanitari',
      regiao='Veneto (tabela de alcance nacional)',
      crops=['TODAS'], temas=['REVOCA', 'SOSTANZE_RITIRATE', 'RISCHIO_DI_PORTAFOGLIO'],
      razao=('e o outro lado do calendario regulatorio, e o que o acervo nao tinha: uma tabela de '
             'substancias REVOGADAS. Sete das nove convergencias confirmadas sao '
             'O5_REGULATORY_PREPARATION — e todas olham para a data de vencimento UE. Revoca '
             'nacional e o evento que chega ANTES dela, e a fala do projeto dos elateridi mostrou '
             'que uma revoca de 2014 ainda define o campo de 2026.'),
      achada='varredura paralela do eixo eventos/calendario regulatorio',
      query='arpa veneto revoche prodotti fitosanitari tabella sostanze',
      metodo='HTML', freq='PERIODIC', acesso='GREEN', coleta='AUTOMATABLE',
      monitor='MONITOR_MONTHLY',
      dedupe='SRC_ARPA_VENETO_IT',
      dedupe_means='mesma agencia; a tabela de revoche e um canal distinto do agrometeo',
      prova='wf_events-and-regulatory-calendar.json · HTTP 200 · 268.631 B'),

    F('IT-SRCX-043',
      'Interpoma — fiera e congresso internacional da maca (Bolzano)',
      'Fiera Bolzano', 'EVENT', 'INDUSTRY', 'MEDIUM',
      'https://www.fierabolzano.it/it/interpoma/',
      regiao='Trentino-Alto Adige (Bolzano)',
      crops=['MELO'], temas=['CONGRESSO', 'MELICOLTURA', 'DATA_FUTURA'],
      razao=('MELO tem 146 pares de rotulo ADAMA e quatro oportunidades. Interpoma e o encontro '
             'internacional da cultura e a data e FUTURA e verificada: 25 a 27 de novembro de '
             '2026, com o programa por dia ja publicado.'),
      achada='varredura paralela do eixo eventos', query='Interpoma 2026 Fiera Bolzano date programma',
      metodo='HTML', freq='EVENT_DRIVEN', ultimo='2026-11-25', acesso='YELLOW',
      coleta='PARTIAL', monitor='EVENT_DRIVEN',
      nota=('a pagina do congresso e a lista de expositores devolvem HTTP 500. A DATA esta '
            'verificada na pagina pai; a LISTA DE EXPOSITORES nao foi verificada e fica NAO_SEI — '
            'e ela e justamente o que diria quais concorrentes estarao la.'),
      prova='wf_events-and-regulatory-calendar.json · pagina pai 200/136.750 B; congresso e expositores 500'),
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

REJEITADAS += [
    {'NAME': 'Open Data Hub Alto Adige — MeteoStation', 'URL': 'https://mobility.api.opendatahub.com/v2/flat/MeteoStation/*/latest?limit=3',
     'REJECTION_CLASS': 'STALE_CONTENT_BEHIND_A_LIVE_ENDPOINT',
     'REASON': ('a API responde HTTP 200 sem autenticacao e parece viva. Os valores mais recentes '
                'devolvidos para a origem SIAG (servico meteo da Provincia di Bolzano) carregam '
                'mvalidtime de 2016-01-26, e a chamada sem filtro devolve series EURAC/HISTALP com '
                'mvalidtime de 2007-12-31. ENDPOINT VIVO != DADO ATUAL.'),
     'ACTION': 'nao registrar como fonte de monitoramento agrometeo; reavaliar se a origem mudar',
     'EVIDENCE': 'wf_agromet-forecast-models.json#freshness_rejection'},
]

# ── ROTAS QUE NAO ABRIRAM DAQUI ────────────────────────────────────────────────
# Estado da REDE desta sessao, nunca estado do mundo.
NAO_ALCANCADAS = [
    {'HOST': 'googlevideo.com (midia do YouTube)', 'STATE': 'EGRESS_POLICY_403',
     'MEANS': ('a politica de saida desta sessao recusa binario de midia desses hosts. Os '
               'METADADOS do YouTube (lista de videos, titulo, duracao) VOLTARAM normalmente. '
               'Logo: enumerar canal, sim; baixar audio para transcrever, nao — daqui.')},
    {'HOST': 'instagram.com (pagina de perfil, UA de navegador)', 'STATE': 'HTTP_302_TO_LOGIN',
     'MEANS': ('a rota de PAGINA de perfil redireciona para login sob UA de navegador. Isto '
               'continua verdadeiro — e NAO e mais o veredito sobre o Instagram. Ver a '
               'correcao em CORRECOES_DESTA_MISSAO: a rota de EMBED abre com outro '
               'User-Agent, e a coleta rodou.')},
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


NAO_ALCANCADAS += [
    {'HOST': 'horta-srl.com · vite.net', 'STATE': 'RECV_FAILURE / CONNECT_TUNNEL_FAILED',
     'MEANS': ('os dois dominios do maior DSS agronomico italiano nao abriram daqui; horta-srl.IT '
               'respondeu 200 com 1,07 MB. A empresa esta registrada por esse host.')},
    {'HOST': 'beratungsring.org · sbr.bz.it', 'STATE': 'SSL_ERROR / CONNECT_TUNNEL_FAILED',
     'MEANS': ('o Sudtiroler Beratungsring e o servico de aconselhamento tecnico do Alto Adige para '
               'maca e vinha — exatamente a voz tecnica que falta no acervo. NAO_SEI, nunca RED.')},
    {'HOST': 'opendata.arpa.piemonte.it · api.arpa.piemonte.it · dext3r.arpae.it · sistemapiemonte.it/agrometeo',
     'STATE': 'CONNECT_TUNNEL_FAILED / RECV_FAILURE',
     'MEANS': 'rotas de dado agromet do Piemonte nao abriram daqui; a rota da Emilia-Romagna abriu'},
    {'HOST': 'betaitalia.eu · betaricerca.it', 'STATE': 'CONNECT_TUNNEL_FAILED',
     'MEANS': ('as duas tentativas restantes de achar a BETA, sociedade de pesquisa da bietola que '
               'faz os ensaios de cercospora com a COPROB, tambem falharam. A instituicao continua '
               'NAO_SEI — e betaitalia.it e outra empresa.')},
    {'HOST': 'instagram.com (pagina de perfil) — segunda medicao', 'STATE': 'HTTP_429_E_HTTP_302',
     'MEANS': ('a passagem paralela mediu 429 em 11 de 12 perfis e UM 200 (disaa_unimi, 625.848 B). '
               'A re-medicao imediata devolveu 302 nos tres perfis testados. A rota nao esta fechada: '
               'esta limitada por taxa e instavel desta saida. Handle DECLARADO pela organizacao '
               'continua provado; o CONTEUDO do perfil fica NAO_SEI.')},
]

REJEITADAS += [
    {'NAME': 'lista de produtos nas paginas de empresa do AgroNotizie',
     'URL': 'https://agronotizie.imagelinenetwork.com/aziende/<slug>/<id>',
     'REJECTION_CLASS': 'SITE_WIDE_LIST_READ_AS_COMPANY_PORTFOLIO',
     'REASON': ('a rota da pagina de empresa responde 200 e parece entregar o portfolio daquela '
                'empresa. Medido: a lista de 32 produtos da pagina da Syngenta e SUBCONJUNTO '
                'ESTRITO da lista de 50 da pagina da ADAMA, sobreposicao 32 de 32, e os mesmos '
                'itens (RIDOMIL GOLD EVO, IKONIK, GEOCLEAN ORTO 2026, D-D SOIL SERRA VII) '
                'aparecem tambem na home do Fitogest. E lista do SITE, nao da empresa.'),
     'ACTION': ('a pagina serve para NOTICIA da empresa, nunca para portfolio. Ler portfolio dali '
                'produziria afirmacao de concorrente que nao existe.'),
     'EVIDENCE': 'wf_competitor-italian-channels.json#TRAP_agronotizie_product_list_is_site_wide'},

    {'NAME': 'certisbelchim.it/eventi e uplcorp.com/it/eventi',
     'URL': 'https://certisbelchim.it/eventi/',
     'REJECTION_CLASS': 'PLACEHOLDER_THEME_CONTENT',
     'REASON': ('a pagina responde 200 com 221 KB e parece uma agenda de eventos. O conteudo e '
                'o tema do WordPress: "0 events found", e os eventos passados sao Trial Field '
                'Days de 2019 (Londerzeel, BE) e 2020 (Fronton, FR) com corpo em lorem ipsum. '
                'A API do proprio site devolve {"events":[],"total":0}.'),
     'ACTION': 'nao registrar como fonte de eventos. 200 com bytes nao e conteudo.',
     'EVIDENCE': 'wf_competitor-italian-channels.json#empty_or_placeholder'},

    {'NAME': 'monitoraggi-corteva.com',
     'URL': 'https://monitoraggi-corteva.com/',
     'REJECTION_CLASS': 'CREDENTIALED_PORTAL',
     'REASON': ('redireciona para /user/login. E portal com credencial, e esta casa nao faz '
                'login, nao passa credencial e nao coleta conteudo nao publico.'),
     'ACTION': ('NAO coletar. Registrado porque saber que EXISTE um portal de monitoramento '
                'fechado da Corteva e informacao — o que nao se pode e entrar nele.'),
     'EVIDENCE': 'wf_competitor-italian-channels.json#empty_or_placeholder'},
]

NAO_ALCANCADAS += [
    {'HOST': 'syngenta.it · cropscience.bayer.it · bayer.it · nufarm.com/it/prodotti',
     'STATE': 'HTTP_403_CLOUDFLARE_OU_MANUTENCAO',
     'MEANS': ('syngenta.it devolve o interstitial "Just a moment..." do Cloudflare; os hosts da '
               'Bayer devolvem "Site Maintenance". nufarm.com/it/ responde 200 e '
               '/it/prodotti/ nao — bloqueio PARCIAL, por caminho. '
               'ROUTE_BLOCKED_FOR_AUTOMATION != CATALOG_EMPTY.')},
    {'HOST': 'uplitalia.it · sariaf.it · sumitomo-chem.it · syngentaseeds.it · hyvido.it',
     'STATE': 'TUNNEL_502 / CONNECTION_RESET',
     'MEANS': 'cinco hosts de concorrente nao abriram daqui. NAO_SEI, nunca RED.'},
    {'HOST': 'albaugh.com/emea/it',
     'STATE': 'SOFT_404',
     'MEANS': ('responde 200 e redireciona para /emea/404. A Albaugh EMEA nao tem versao '
               'italiana — isso e um fato sobre a empresa, e nao uma falha de rota.')},
]


# ═══════════════════════════════════════════════════════════════════════════════
# LOTE 2 — O QUE A VARREDURA PARALELA TROUXE, DEPOIS DE EU CONFERIR NA MAO
# ═══════════════════════════════════════════════════════════════════════════════
# A varredura paralela devolveu 93 fontes e 95 rejeicoes. Nao entrou nada aqui
# por confianca: cada host abaixo foi buscado OUTRA VEZ, por mim, em 2026-09-03,
# e cada handle social foi conferido contra a LEI 6 (o handle precisa estar
# declarado na casa do proprio dono; handle achado em busca livre e palpite).
#
# O que a minha conferencia mudou, e que fica registrado abaixo em REJEITADAS:
#   · anicav.it   — a varredura admitiu como fonte. Devolve 200 com 33.245 B,
#                   mas o titulo e "Security Check Required": e muro de bot.
#   · csoservizi.com — a varredura disse que o LinkedIn do CSO estava declarado
#                   na propria casa. Nao esta: 50.746 B, ZERO link social.
#   · consorziagrariditalia.it — devolveu 500/0 na minha primeira leitura e
#                   200/700.576 na segunda. Fonte INTERMITENTE, e isso importa
#                   para desenhar o monitoramento; entra, com a ressalva escrita.

FONTES += [

    # ═══ A · OFICIAL / DADO PUBLICO ════════════════════════════════════════════
    F('IT-SRCX-044',
      'Arpae Emilia-Romagna — Dext3r, extracao de dados das estacoes agrometeorologicas',
      'Arpae Emilia-Romagna — SIMC', 'AGROMET_STATION_EXTRACTION', 'OFFICIAL', 'MEDIUM',
      'https://simc.arpae.it/dext3r/',
      regiao='Emilia-Romagna',
      crops=['BARBABIETOLA', 'POMODORO', 'FRUMENTO', 'MELO', 'VITE'],
      temas=['DADO_OBSERVADO_POR_ESTACAO', 'REDE_AGROMETEOROLOGICA'],
      razao=('e o par OBSERVADO do ERG5, que ja esta registrado em IT-SRCX-028 e e '
             'INTERPOLADO. A distincao nao e academica: quando uma janela de infeccao '
             'modelada precisa ser defendida diante de um produtor que diz "no meu campo '
             'nao foi assim", o que sustenta a conversa e o dado da estacao fisica, nao '
             'a grade. Mesma aposta de cultura do ERG5 — BARBABIETOLA, 239 pares de rotulo.'),
      achada='varredura paralela do eixo agrometeorologico', query='Arpae Dext3r estazioni agrometeo',
      metodo='GUI HTML (formulario)', freq='FREQUENT', acesso='GREEN',
      coleta='MANUAL', monitor='DISCOVERY_ONLY',
      dedupe='IT-SRCX-028', dedupe_means='mesma casa (Arpae), CANAL DIFERENTE: grade vs estacao',
      nota=('MANUAL e DISCOVERY_ONLY de proposito: e formulario. Enquanto nao houver rota '
            'programatica, nao entra em pipeline diario — e dizer o contrario seria mentir '
            'sobre a periodicidade.'),
      prova='minha leitura 2026-09-03: HTTP 200, 12.288 B, titulo "dext3r", Leaflet + Materialize'),

    F('IT-SRCX-045',
      'CCIAA di Foggia — listino settimanale e Borsa Merci da Capitanata',
      'Camera di Commercio di Foggia', 'MARKET_PRICE_OFFICIAL', 'OFFICIAL', 'HIGH',
      'https://www.fg.camcom.it/servizi/listini-prezzi-e-borsa-merci',
      regiao='Puglia (Capitanata)',
      crops=['FRUMENTO', 'ORZO'],
      temas=['BORSA_MERCI_CEREALICOLA', 'LISTINO_SETTIMANALE', 'PREZZI_OLIVICOLI'],
      razao=('a Capitanata e a maior bacia de trigo duro da Italia e a Puglia esta na lista '
             'de regioes das oportunidades. FRUMENTO carrega 176 linhas de rotulo e ORZO 131, '
             'e aqui elas sao cotadas SEMANA A SEMANA, com arquivo PDF publico de 2021 ate '
             'a semana 33 de 2026. PRECO NAO E DEMANDA DE DEFENSIVO — e o denominador '
             'economico que decide se o produtor gasta ou nao gasta na proxima aplicacao.'),
      achada='varredura paralela do eixo mercado', query='borsa merci Foggia listino grano duro',
      metodo='HTML + PDF', freq='PERIODIC', ultimo='2026-09-02', acesso='GREEN',
      coleta='AUTOMATABLE', monitor='MONITOR_WEEKLY',
      prova=('minha leitura 2026-09-03: HTTP 200, 95.309 B. A varredura extraiu o PDF da '
             'semana 33 (200, 192.860 B) com "Riunione del 02/09/2026" e a linha GRANO DURO '
             'BIOLOGICO 310,00-315,00.')),

    F('IT-SRCX-046',
      'ISTAT — web service SDMX (superficie e producao das culturas, ate o nivel provincial)',
      'ISTAT', 'OFFICIAL_STATISTICS_API', 'OFFICIAL', 'HIGH',
      'https://esploradati.istat.it/SDMXWS/rest/dataflow/IT1/all/latest',
      regiao='ITALIA (nacional, regional e provincial)',
      feed='https://esploradati.istat.it/SDMXWS/rest/data/IT1,101_1015_DF_DCSP_COLTIVAZIONI_10',
      crops=['BARBABIETOLA', 'FRUMENTO', 'ORZO', 'MAIS', 'PATATA', 'POMODORO', 'VITE',
             'MELO', 'SOIA', 'GIRASOLE', 'COLZA', 'RISO'],
      temas=['SUPERFICIE_INVESTITA', 'PRODUZIONE_RACCOLTA', 'PREZZI_AGRICOLI'],
      razao=('a diferenca entre ler uma pagina e TER UMA SERIE. O acervo canonico ja tem o '
             'portal do ISTAT; nao tinha a rota de maquina. Superficie por provincia e o '
             'denominador que falta em toda leitura de sinal de campo: sem hectare, '
             '"pressao em melo na Emilia-Romagna" nao tem escala e nao vira nada.'),
      achada='varredura paralela do eixo mercado', query='ISTAT SDMX REST dataflow coltivazioni',
      metodo='REST SDMX (XML + CSV)', freq='PERIODIC', acesso='GREEN',
      coleta='AUTOMATABLE', monitor='MONITOR_MONTHLY',
      nota=('sdmx.istat.it, o host mais citado, entra em laco de redirecionamento (curl 47). '
            'A rota que responde e esploradati.istat.it/SDMXWS.'),
      prova=('minha leitura 2026-09-03: HTTP 200, 13.619.778 B, application/xml SDMX 2.1. '
             'A varredura leu o CSV do dataflow 101_1015_DF_DCSP_COLTIVAZIONI_10.')),

    F('IT-SRCX-047',
      'EFSA — calendario de reunioes e consultas publicas',
      'European Food Safety Authority', 'REGULATORY_EVENT_CALENDAR', 'OFFICIAL', 'MEDIUM',
      'https://www.efsa.europa.eu/en/calendar',
      regiao='UE / Parma (Emilia-Romagna)', lingua='EN',
      crops=[], temas=['PLENARIA_PLH', 'PANEL_PESTICIDAS', 'PEER_REVIEW_SUBSTANCIA_ATIVA',
                       'CONSULTA_PUBLICA'],
      razao=('a EFSA e quem da a partida no relogio que termina, meses depois, como revoca '
             'italiana com data de fim de venda — as mesmas datas que a ARPAV tabula em '
             'IT-SRCX-042 (methoxyfenozide 30/09/2026, boscalid/pyraclostrobin 25/11/2026). '
             'E os paineis se reunem FISICAMENTE em Parma, dentro da Emilia-Romagna.'),
      achada='varredura paralela do eixo evento', query='EFSA calendar plant health plenary',
      metodo='HTML', freq='PERIODIC', acesso='GREEN', coleta='PARTIAL', monitor='MONITOR_MONTHLY',
      nota=('CAMADA UE != CAMADA NACIONAL. Uma reuniao da EFSA nao e uma autorizacao '
            'italiana e nao pode ser lida como tal.'),
      prova=('minha leitura 2026-09-03: HTTP 200, 96.108 B; /en/calendar redireciona para '
             '/en/events/advanced-search. A varredura leu "Results 1 - 10 of 90" com '
             '"143rd PLH Plenary meeting — 16 September 2026 — Parma, Italy".')),

    F('IT-SRCX-048',
      'BURP — Bollettino Ufficiale della Regione Puglia (atos do Osservatorio Fitosanitario)',
      'Regione Puglia', 'OFFICIAL_GAZETTE_REGIONAL', 'OFFICIAL', 'MEDIUM',
      'https://burp.regione.puglia.it/',
      regiao='Puglia',
      crops=['AGRUMI', 'BRASSICACEE', 'VITE', 'OLIVO'],
      temas=['DEROGHE', 'DETERMINAZIONI_OSSERVATORIO_FITOSANITARIO', 'XYLELLA', 'AREE_DELIMITATE'],
      razao=('e a rota primaria e citavel onde as deroghe da Puglia ganham efeito legal — o '
             'que o FruitJournal (IT-SRCX-018) apenas resume. Puglia e regiao de oportunidade '
             'e as deroghe de junho de 2026 caem sobre AGRUMI 17, BRASSICACEE 100 e VITE 96 '
             'linhas de rotulo. DEROGA E JANELA COM DATA, e nao opiniao.'),
      achada='snowballing a partir do FruitJournal', query='BURP determinazione osservatorio fitosanitario deroga',
      metodo='HTML + PDF', freq='EVENT_DRIVEN', acesso='GREEN', coleta='PARTIAL',
      monitor='EVENT_DRIVEN',
      dedupe='IT-SRCX-018', dedupe_means='o FruitJournal NOTICIA a deroga; o BURP e o ato',
      nota=('LIMITE DECLARADO: os dois atos efetivamente abertos pela varredura eram de '
            'delimitacao de Xylella, e nao as deroghe citadas. A rota esta provada; a '
            'presenca das deroghe especificas nao esta.'),
      prova='minha leitura 2026-09-03: HTTP 200, 194.925 B'),

    F('IT-SRCX-049',
      "CONAF — Consiglio dell'Ordine Nazionale dei Dottori Agronomi e dei Dottori Forestali",
      'CONAF', 'PROFESSIONAL_BODY', 'OFFICIAL', 'MEDIUM',
      'https://www.conaf.it/',
      regiao='ITALIA',
      social={'INSTAGRAM': 'https://www.instagram.com/ordine_agronomi_e_forestali'},
      crops=['TODAS'], temas=['PROFISSAO_AGRONOMICA', 'FORMACAO', 'NORMATIVA'],
      razao=('e o orgao dos agronomos habilitados — a categoria que ASSINA a recomendacao de '
             'tratamento na Italia. Nenhuma venda de defensivo acontece contra o parecer '
             'do agronomo; saber onde essa categoria se informa e onde ela se posiciona e '
             'estrutural, mesmo que nada aqui seja sinal de campo.'),
      achada='varredura paralela do eixo social/tecnico', query='CONAF ordine agronomi social',
      metodo='HTML + Instagram publico', scrap='YES', freq='PERIODIC', acesso='GREEN',
      coleta='PARTIAL', monitor='MONITOR_MONTHLY',
      nota='VOZ PROFISSIONAL != SINAL DE CAMPO. Nao produz observacao datada de praga.',
      prova='minha leitura 2026-09-03: conaf.it HTTP 200, 94.717 B, handle declarado na propria casa'),

    # ═══ B · CIENCIA E RESISTENCIA ═════════════════════════════════════════════
    F('IT-SRCX-050',
      'CNR — Istituto per la Protezione Sostenibile delle Piante (IPSP)',
      'Consiglio Nazionale delle Ricerche — IPSP', 'RESEARCH_INSTITUTION', 'SCIENTIFIC', 'HIGH',
      'http://www.ipsp.cnr.it/',
      regiao='ITALIA (Torino, Legnaro PD, Sesto Fiorentino, Portici, Bari)',
      crops=['RISO', 'FRUMENTO', 'MAIS', 'BARBABIETOLA', 'SOIA', 'VITE'],
      temas=['RESISTENZA_ERBICIDI', 'DIAGNOSTICA_FITOPATOLOGICA', 'PROTEZIONE_DELLE_PIANTE'],
      razao=('e o dono institucional do GIRE, que ja esta registrado em IT-SRCX-040 apenas '
             'como micro-site. Registrar o INSTITUTO e o que permite ver o trabalho antes de '
             'ele virar certificacao: e em Legnaro que se testa se um modo de acao ALS '
             '(MESOSULFURON-METHYL, FLORASULAM, TRIBENURON, NICOSULFURON, IMAZAMOX) ou ACCase '
             '(CLETHODIM, PROPAQUIZAFOP, QUIZALOFOP-P-ETHYL, CLODINAFOP, PINOXADEN) ainda '
             'funciona — e 26 dos 51 produtos comerciais da ADAMA sao herbicidas.'),
      achada='snowballing a partir do GIRE', query='IPSP CNR gruppo di lavoro resistenza erbicidi',
      metodo='HTTP (apenas http://; https falha na verificacao de certificado)',
      freq='PERIODIC', acesso='GREEN', coleta='AUTOMATABLE', monitor='MONITOR_MONTHLY',
      dedupe='IT-SRCX-040', dedupe_means='GIRE e um GRUPO DE TRABALHO do IPSP; instituicao != grupo',
      nota=('https falha na verificacao de certificado neste dominio, com e sem a CA do proxy. '
            'A verificacao TLS NAO foi desligada; a rota usada e http.'),
      prova='minha leitura 2026-09-03: HTTP 200, 80.062 B, titulo "IPSP - Istituto per la Protezione Sostenibile delle Piante"'),

    F('IT-SRCX-051',
      'International Herbicide-Resistant Weed Database (Heap) — linha da Italia',
      'WeedScience.org (Ian Heap)', 'SCIENTIFIC_DATABASE', 'SCIENTIFIC', 'HIGH',
      'https://www.weedscience.org/Pages/CountrySummary.aspx',
      regiao='GLOBAL, com linha por pais', lingua='EN',
      crops=['RISO', 'FRUMENTO', 'MAIS', 'BARBABIETOLA', 'SOIA'],
      temas=['RESISTENZA_ERBICIDI', 'HRAC_SITE_OF_ACTION'],
      razao=('poe NUMERO na exposicao do bloco herbicida da ADAMA. Dos 29 casos italianos '
             'documentados, 23 estao exatamente nos dois grupos onde a ADAMA se concentra: '
             '15 em HRAC 2 (ALS) e 8 em HRAC 1 (ACCase). Mais 4 em HRAC 9 (GLYPHOSATE) e '
             '1 em HRAC 4 (2,4-D / DICAMBA / FLUROXYPYR).'),
      achada='varredura paralela do eixo ciencia', query='herbicide resistance Italy country summary HRAC',
      metodo='HTML', freq='PERIODIC', acesso='GREEN', coleta='PARTIAL', monitor='MONITOR_MONTHLY',
      nota=('CASO DE ERVA RESISTENTE != APLICACAO ADAMA QUE FALHOU. E contagem de casos '
            'publicados, e so isso.'),
      prova=('CONFERIDO POR MIM em 2026-09-03, e nao aceito da varredura: HTTP 200, 58.399 B '
             '(--compressed). Linha 36, Italy: Total 29 | HRAC1 8 | HRAC2 15 | HRAC5 0 | '
             'HRAC22 0 | HRAC9 4 | HRAC3 0 | HRAC4 1 | Other 1. Os grupos somam 29.')),

    F('IT-SRCX-052',
      'PubliCatt — arquivo institucional da Universita Cattolica (entomologia aplicada, Piacenza)',
      'Universita Cattolica del Sacro Cuore', 'INSTITUTIONAL_REPOSITORY', 'SCIENTIFIC', 'HIGH',
      'https://publicatt.unicatt.it/handle/10807/61522',
      regiao='ITALIA (areas peschicolas)',
      crops=['PESCO', 'POMODORO', 'TABACCO'],
      temas=['RESISTENZA_INSETTICIDI', 'MYZUS_PERSICAE', 'KDR', 'MACE', 'NEONICOTINOIDI'],
      razao=('e o mecanismo que fica EMBAIXO do negocio de afideo do pessego. PESCO tem 45 '
             'pares de rotulo e AFIDI e seu maior alvo com 20 deles. A mutacao S431F/MACE '
             'derrota dimetilcarbamatos — isto e, o PIRIMICARB, ativo ADAMA. O par kdr/s-kdr '
             'em frequencia quase total e resistencia a piretroide — LAMBDA-CYHALOTHRIN e '
             'TAU-FLUVALINATE, ativos ADAMA. Sobra o FLONICAMID (IRAC 29).'),
      achada='snowballing a partir de IT-SRCX-008 (UniCatt Piacenza)',
      query='resistenza target-site Myzus persicae pesco Italia',
      metodo='HTML + OAI-PMH', freq='PERIODIC', acesso='GREEN', coleta='AUTOMATABLE',
      monitor='MONITOR_MONTHLY',
      dedupe='IT-SRCX-008', dedupe_means='a mesma universidade; o repositorio e outro canal',
      nota=('MECANISMO DE RESISTENCIA != OPORTUNIDADE COMERCIAL. Isto explica por que um '
            'produto pode falhar; nao diz que alguem vai comprar outro.'),
      prova='minha leitura 2026-09-03: HTTP 200, 65.242 B, titulo "Resistenze target-site in popolazioni italiane dell\'afide verde del pesco"'),

    F('IT-SRCX-053',
      'IRIS AperTO — arquivo institucional da Universita di Torino (malerbologia DISAFA)',
      'Universita degli Studi di Torino', 'INSTITUTIONAL_REPOSITORY', 'SCIENTIFIC', 'HIGH',
      'https://iris.unito.it/simple-search?query=resistenza+erbicidi+riso',
      regiao='Piemonte (Vercellese, Novarese) e areal risicolo padano',
      crops=['RISO', 'MAIS', 'FRUMENTO'],
      temas=['RESISTENZA_ERBICIDI', 'MALERBOLOGIA', 'ECHINOCHLOA', 'ATTI_SIRFI'],
      razao=('Torino DISAFA e o grupo italiano de ciencia das plantas daninhas do arroz, e a '
             'resistencia de daninha em arroz e o mecanismo vivo por tras da oportunidade '
             'RICE x ECHINOCHLOA. O acervo ja tem sirfi.it e giornatefitopatologiche.it, mas '
             'nenhum dos dois serve o texto completo dos atos — este serve, com OAI-PMH, o '
             'que transforma cacada manual de PDF em colheita agendada.'),
      achada='varredura paralela do eixo ciencia', query='resistenza erbicidi riso Echinochloa IRIS unito',
      metodo='HTML + OAI-PMH', freq='PERIODIC', acesso='GREEN', coleta='AUTOMATABLE',
      monitor='MONITOR_MONTHLY',
      prova='minha leitura 2026-09-03: HTTP 200, 47.789 B (rota de busca viva)'),

    F('IT-SRCX-054',
      'CRIS UNIBO — arquivo da pesquisa da Universita di Bologna (patologia vegetal)',
      'Alma Mater Studiorum — Universita di Bologna', 'INSTITUTIONAL_REPOSITORY',
      'SCIENTIFIC', 'HIGH',
      'https://cris.unibo.it/handle/11585/33117',
      regiao='Italia nord-orientale',
      crops=['MELO', 'PERO', 'VITE'],
      temas=['RESISTENZA_FUNGICIDI', 'QOI', 'G143A', 'VENTURIA_INAEQUALIS', 'PLASMOPARA_VITICOLA'],
      razao=('MELO e a 3a cultura da ADAMA por peso de rotulo (146 pares) e ticchiolatura e '
             'a sua doenca definidora. G143A e a mutacao que ANULA a atividade QoI — isto e, '
             'o AZOXYSTROBIN, ativo ADAMA — e foi documentada em pomares exatamente das '
             'regioes onde estao as oportunidades. A conclusao do proprio registro, de que a '
             'estrategia antirresistencia a conteve, e o argumento comercial da quimica '
             'parceira: CAPTAN e FOLPET como ancoras multissitio, DIFENOCONAZOLE e '
             'FLUXAPYROXAD em alternancia.'),
      achada='varredura paralela do eixo ciencia', query='sensibilita Venturia inaequalis strobilurine Italia',
      metodo='HTML + OAI-PMH', freq='PERIODIC', acesso='GREEN', coleta='AUTOMATABLE',
      monitor='MONITOR_MONTHLY',
      dedupe='IT-SRCX-063', dedupe_means='DISTAL e o departamento; CRIS e o repositorio da universidade',
      prova='minha leitura 2026-09-03: HTTP 200, 54.722 B, titulo "Sensibilita di Venturia inaequalis ai fungicidi analoghi delle strobilurine"'),

    F('IT-SRCX-055',
      'Phytopathologia Mediterranea (Mediterranean Phytopathological Union / FUP)',
      'Firenze University Press', 'SCIENTIFIC_JOURNAL', 'SCIENTIFIC', 'HIGH',
      'https://oajournals.fupress.net/index.php/pm',
      regiao='Bacia mediterranea, com trabalhos italianos localizados', lingua='EN',
      feed='https://oajournals.fupress.net/index.php/pm/oai',
      crops=['PESCO', 'ALBICOCCO', 'CILIEGIO', 'LATTUGA', 'VITE', 'ORZO'],
      temas=['SENSIBILITA_AI_FUNGICIDI', 'MONILIA', 'AZOXYSTROBIN', 'TEBUCONAZOLE', 'FLUDIOXONIL'],
      razao=('e o unico canal verificado que publica MEDICAO PRIMARIA italiana de '
             'sensibilidade a fungicida sobre moleculas da propria ADAMA: o trabalho de Cuneo '
             'mede AZOXYSTROBIN, TEBUCONAZOLE e FLUDIOXONIL de uma vez, em fruta de caroco no '
             'Piemonte, contra Monilia — alvo declarado nos rotulos ADAMA de PESCO, ALBICOCCO '
             '(16 pares) e CILIEGIO (27). Com DOI e OAI, e monitoravel, e nao apenas pesquisavel.'),
      achada='varredura paralela do eixo ciencia', query='fungicide resistance Italy Phytopathologia Mediterranea',
      metodo='HTML + OAI-PMH', freq='PERIODIC', acesso='GREEN', coleta='AUTOMATABLE',
      monitor='MONITOR_MONTHLY',
      prova='minha leitura 2026-09-03: HTTP 200, 47.527 B'),

    F('IT-SRCX-056',
      'Bollettino di Zoologia agraria e di Bachicoltura (riviste.unimi.it)',
      'Universita degli Studi di Milano', 'SCIENTIFIC_JOURNAL', 'SCIENTIFIC', 'MEDIUM',
      'https://riviste.unimi.it/index.php/bzab/article/view/27174',
      regiao='ITALIA (areas peschicolas)',
      crops=['PESCO'],
      temas=['RESISTENZA_INSETTICIDI', 'ESTERASI', 'MYZUS_PERSICAE'],
      razao=('da a linha de base METABOLICA para a mesma praga e a mesma cultura do estudo '
             'target-site da UniCatt: superproducao de esterase degrada carbamatos e '
             'piretroides — PIRIMICARB, LAMBDA-CYHALOTHRIN, TAU-FLUVALINATE. Os dois registros '
             'juntos mostram resistencia metabolica ja saturada no pessego italiano tres '
             'decadas antes de as mutacoes de sitio-alvo serem mapeadas.'),
      achada='snowballing a partir do registro da UniCatt', query='resistenza insetticidi Myzus persicae pescheti italiani',
      metodo='HTML + OJS/OAI', freq='STATIC', acesso='GREEN', coleta='AUTOMATABLE',
      monitor='MONITOR_MONTHLY',
      nota='estudo de 1995. VALOR HISTORICO, e nao sinal corrente.',
      prova='minha leitura 2026-09-03: HTTP 200, 27.254 B'),

    F('IT-SRCX-057',
      'Accademia dei Georgofili',
      'Accademia dei Georgofili', 'SCIENTIFIC_ACADEMY', 'SCIENTIFIC', 'MEDIUM',
      'https://www.georgofili.it/',
      regiao='Toscana (Firenze), alcance nacional',
      social={'INSTAGRAM': 'https://www.instagram.com/georgofili'},
      crops=['VITE', 'OLIVO', 'FRUMENTO', 'RISO'],
      temas=['POLITICA_AGRICOLA', 'CONVEGNI', 'DIVULGACAO_CIENTIFICA'],
      razao=('e onde a ciencia agricola italiana e ENQUADRADA para politica publica. Nao '
             'produz sinal de campo, mas produz o vocabulario com que a norma e escrita — e '
             'norma vira janela de rotulo. Toscana e regiao de oportunidade.'),
      achada='varredura paralela do eixo ciencia', query='Accademia dei Georgofili convegni difesa',
      metodo='HTML + Instagram publico', scrap='YES', freq='PERIODIC', acesso='GREEN',
      coleta='PARTIAL', monitor='MONITOR_MONTHLY',
      nota=('a pagina /eventi tinha UM unico item futuro na leitura da varredura. Como '
            'calendario, e fraco; como voz, nao.'),
      prova='minha leitura 2026-09-03: georgofili.it HTTP 200, 52.840 B, handle declarado na propria casa'),

    F('IT-SRCX-058',
      "Georgofili INFO — notiziario dell'Accademia dei Georgofili",
      'Accademia dei Georgofili', 'SCIENTIFIC_NEWSLETTER', 'SCIENTIFIC', 'MEDIUM',
      'https://www.georgofili.info/',
      regiao='Lombardia (risaie lomelline), Piemonte, area do Ticino',
      crops=['RISO'],
      temas=['RESISTENZA_ERBICIDI', 'ECHINOCHLOA', 'EPIGENETICA', 'PROGETTO_EPIRESISTENZE'],
      razao=('e a face publica do projeto Epiresistenze — o unico trabalho italiano verificado '
             'que ataca a resistencia do giavone por EPIGENETICA e nao por genetica de '
             'sitio-alvo. Isso e resistencia que um ensaio do GIRE pode certificar mas que uma '
             'triagem de mutacao NAO ENCONTRA. Cai direto sobre RICE x ECHINOCHLOA, na '
             'Lombardia, regiao de oportunidade. Fato competitivo que viaja junto: o '
             'cofinanciador do projeto e a Corteva, e nao a ADAMA.'),
      achada='snowballing a partir da Accademia dei Georgofili', query='Epiresistenze riso giavone resistenza erbicidi',
      metodo='HTML', freq='FREQUENT', acesso='GREEN', coleta='AUTOMATABLE', monitor='MONITOR_WEEKLY',
      dedupe='IT-SRCX-057', dedupe_means='mesma academia, canal editorial distinto e com outra cadencia',
      prova='minha leitura 2026-09-03: HTTP 200, 43.594 B, "Agricoltura Ambiente Alimenti"'),

    F('IT-SRCX-059',
      'Fondazione Edmund Mach — San Michele all\'Adige',
      'Fondazione Edmund Mach', 'RESEARCH_FOUNDATION', 'SCIENTIFIC', 'HIGH',
      'https://www.fmach.it/',
      regiao='Trentino-Alto Adige',
      social={'INSTAGRAM': 'https://www.instagram.com/fondazionemach'},
      crops=['MELO', 'VITE', 'PICCOLI_FRUTTI'],
      temas=['DIFESA_FITOSANITARIA', 'SPERIMENTAZIONE', 'AGRICOLTURA_DI_MONTAGNA'],
      razao=('e a casa de pesquisa aplicada do Trentino, e Trentino esta na lista de regioes '
             'das oportunidades. MELO (146 pares de rotulo) e VITE (96) sao as duas culturas '
             'em que a FEM publica ensaio e aviso — e o produtor trentino le a FEM antes de '
             'decidir o programa de defesa.'),
      achada='varredura paralela do eixo ciencia/social', query='Fondazione Edmund Mach difesa melo',
      metodo='HTML + Instagram publico', scrap='YES', freq='PERIODIC', acesso='GREEN',
      coleta='PARTIAL', monitor='MONITOR_WEEKLY',
      nota='o handle ja estava no lote social congelado V1; a FICHA da instituicao faltava.',
      prova='minha leitura 2026-09-03: fmach.it HTTP 200, 76.603 B, handle declarado na propria casa'),

    F('IT-SRCX-060',
      'CREA — Consiglio per la ricerca in agricoltura e l\'analisi dell\'economia agraria',
      'CREA', 'RESEARCH_INSTITUTION', 'SCIENTIFIC', 'MEDIUM',
      'https://www.crea.gov.it/',
      regiao='ITALIA',
      social={'INSTAGRAM': 'https://www.instagram.com/crearicerca'},
      crops=['TODAS'], temas=['RICERCA_AGRICOLA_PUBBLICA', 'DIFESA_DELLE_COLTURE', 'ECONOMIA_AGRARIA'],
      razao=('e o instituto publico nacional de pesquisa agricola, e o CREA-DC e o centro de '
             'protecao das plantas. O acervo canonico nao tinha ficha do CREA como '
             'organizacao. Sem ele, toda leitura de ciencia italiana fica dependente de '
             'universidade e de revista, e perde a camada estatal.'),
      achada='varredura paralela do eixo ciencia/social', query='CREA ricerca difesa colture social',
      metodo='HTML + Instagram publico', scrap='YES', freq='PERIODIC', acesso='GREEN',
      coleta='PARTIAL', monitor='MONITOR_MONTHLY',
      prova='minha leitura 2026-09-03: crea.gov.it HTTP 200, 137.116 B, handle declarado na propria casa'),

    F('IT-SRCX-061',
      'DiSAA — Dipartimento di Scienze Agrarie e Ambientali, Universita degli Studi di Milano',
      'Universita degli Studi di Milano', 'UNIVERSITY_DEPARTMENT', 'SCIENTIFIC', 'HIGH',
      'https://www.disaa.unimi.it/it',
      regiao='Lombardia',
      social={'INSTAGRAM': 'https://www.instagram.com/disaa_unimi'},
      crops=['RISO', 'MAIS', 'VITE'],
      temas=['AGRONOMIA', 'DIFESA', 'ENTOMOLOGIA_APPLICATA'],
      razao=('Lombardia e regiao de oportunidade e concentra arroz e milho — RISO liga a '
             'ECHINOCHLOA e MAIS carrega 112 pares de rotulo. O DiSAA e o departamento que '
             'forma e publica sobre essas duas culturas na regiao.'),
      achada='varredura paralela do eixo ciencia/social', query='DiSAA Unimi difesa colture social',
      metodo='HTML + Instagram publico', scrap='YES', freq='PERIODIC', acesso='GREEN',
      coleta='PARTIAL', monitor='MONITOR_MONTHLY',
      nota=('o canal de YouTube que o proprio DiSAA declara no site esta MORTO. Link '
            'declarado pelo dono nao e link vivo — foi conferido.'),
      prova='minha leitura 2026-09-03: disaa.unimi.it HTTP 200, 104.535 B, handle declarado na propria casa'),

    F('IT-SRCX-062',
      'DAFNAE — Dipartimento di Agronomia, Animali, Alimenti, Risorse naturali e Ambiente, Universita di Padova',
      'Universita degli Studi di Padova', 'UNIVERSITY_DEPARTMENT', 'SCIENTIFIC', 'HIGH',
      'https://www.dafnae.unipd.it/',
      regiao='Veneto (Legnaro PD)',
      social={'INSTAGRAM': 'https://www.instagram.com/dafnaeunipd'},
      crops=['MAIS', 'VITE', 'SOIA', 'FRUMENTO'],
      temas=['MALERBOLOGIA', 'ENTOMOLOGIA', 'RESISTENZA_ERBICIDI'],
      razao=('Legnaro e onde ficam Sattin, Scarabel, Loddo e Panozzo — o grupo que faz o teste '
             'de resistencia que decide se um modo de acao ALS ou ACCase ainda vale no '
             'FRUMENTO (176 rotulos) e no MAIS (112). O Veneto e a segunda regiao mais citada '
             'nas oportunidades.'),
      achada='varredura paralela do eixo ciencia/social', query='DAFNAE Unipd malerbologia resistenza',
      metodo='HTML + Instagram publico', scrap='YES', freq='PERIODIC', acesso='GREEN',
      coleta='PARTIAL', monitor='MONITOR_MONTHLY',
      dedupe='IT-SRCX-050', dedupe_means='o IPSP tem sede em Legnaro; departamento e instituto sao donos diferentes',
      prova='minha leitura 2026-09-03: dafnae.unipd.it HTTP 200, 63.697 B, handle declarado na propria casa'),

    F('IT-SRCX-063',
      'DISTAL — Dipartimento di Scienze e Tecnologie Agro-Alimentari, Universita di Bologna',
      'Alma Mater Studiorum — Universita di Bologna', 'UNIVERSITY_DEPARTMENT',
      'SCIENTIFIC', 'MEDIUM',
      'https://distal.unibo.it/it',
      regiao='Emilia-Romagna',
      social={'INSTAGRAM': 'https://www.instagram.com/distal.unibo'},
      crops=['MELO', 'PERO', 'VITE', 'POMODORO'],
      temas=['PATOLOGIA_VEGETALE', 'DIFESA', 'ENTOMOLOGIA'],
      razao=('e o departamento do grupo Brunelli/Collina, autor da medicao de G143A em '
             'Venturia inaequalis, e fica na Emilia-Romagna, a regiao mais pesada do radar. '
             'Registrado como MEDIUM e nao HIGH por uma razao medida: o feed do canal de '
             'YouTube do proprio DISTAL e institucional, e nao tecnico de campo.'),
      achada='varredura paralela do eixo ciencia/social', query='DISTAL Unibo patologia vegetale',
      metodo='HTML + Instagram publico', scrap='YES', freq='PERIODIC', acesso='GREEN',
      coleta='PARTIAL', monitor='MONITOR_MONTHLY',
      prova='minha leitura 2026-09-03: distal.unibo.it HTTP 200, 81.974 B, handle declarado na propria casa'),

    F('IT-SRCX-064',
      'Di3A — Dipartimento di Agricoltura, Alimentazione e Ambiente, Universita di Catania',
      'Universita degli Studi di Catania', 'UNIVERSITY_DEPARTMENT', 'SCIENTIFIC', 'MEDIUM',
      'https://www.di3a.unict.it/',
      regiao='Sicilia',
      social={'INSTAGRAM': 'https://www.instagram.com/di3aunict'},
      crops=['AGRUMI', 'OLIVO', 'VITE', 'POMODORO'],
      temas=['AGRUMICOLTURA', 'DIFESA', 'ENTOMOLOGIA'],
      razao=('a Sicilia esta na lista de regioes das oportunidades e e o unico eixo citricola '
             'serio do radar — AGRUMI carrega 17 pares de rotulo e a deroga pugliese de '
             'dimpropyridaz contra Aonidiella aurantii mostra que o alvo esta vivo. Di3A e o '
             'departamento que publica sobre citros na ilha.'),
      achada='varredura paralela do eixo ciencia/social', query='Di3A Unict agrumi difesa',
      metodo='HTML + Instagram publico', scrap='YES', freq='PERIODIC', acesso='GREEN',
      coleta='PARTIAL', monitor='MONITOR_MONTHLY',
      nota=('o canal de YouTube do Di3A esta vivo mas com ultima publicacao em 2025-07-19: '
            'canal EXISTE nao e canal ATIVO.'),
      prova='minha leitura 2026-09-03: di3a.unict.it HTTP 200, 64.742 B, handle declarado na propria casa'),
]

FONTES += [

    # ═══ C · CAMPO, REDE TECNICA E MERCADO ═════════════════════════════════════
    F('IT-SRCX-065',
      'Societa Agraria di Lombardia — news e "Agricoltura e cultura"',
      'Societa Agraria di Lombardia', 'AGRICULTURAL_SOCIETY', 'TECHNICAL', 'MEDIUM',
      'http://www.agrarialombardia.it/news/',
      regiao='Lombardia (Lomellina, Pavia) e Vercelli',
      crops=['RISO', 'MAIS'],
      temas=['GESTIONE_INFESTANTI_IN_RISAIA', 'RESISTENZA_ERBICIDI', 'DEMO_FARM'],
      razao=('e a ponta lomelina do problema de resistencia no arroz: onde o achado do '
             'Epiresistenze vira dia de campo para o produtor de Pavia, dentro das restricoes '
             'de Natura 2000 que decidem quais herbicidas podem sequer ser usados. E o coracao '
             'da area de arroz que alimenta RICE x ECHINOCHLOA, e e onde a alternancia entre '
             'CLETHODIM, PROPAQUIZAFOP, GLYPHOSATE, PENDIMETHALIN e IMAZAMOX contra giavone '
             'resistente e recomendada — ou nao e.'),
      achada='snowballing a partir do Georgofili INFO', query='Societa Agraria di Lombardia riso infestanti demo',
      metodo='HTML', freq='PERIODIC', acesso='GREEN', coleta='PARTIAL', monitor='MONITOR_MONTHLY',
      prova='minha leitura 2026-09-03: HTTP 200, 86.589 B'),

    F('IT-SRCX-066',
      'Vitenova — consultoria agronomica privada',
      'Vitenova', 'PRIVATE_AGRONOMIC_ADVISORY', 'FIELD_VOICE', 'MEDIUM',
      'https://vitenova.it/',
      regiao='ITALIA (nordeste)',
      social={'INSTAGRAM': 'https://www.instagram.com/vitenova'},
      crops=['VITE'],
      temas=['CONSULENZA_VITICOLA', 'DIFESA_DELLA_VITE'],
      razao=('e voz de campo PAGA por produtor, e nao midia: o consultor que aparece no '
             'vinhedo. VITE tem 96 pares de rotulo. O valor aqui e a mesma coisa que o valor '
             'do Agralia (IT-SRCX-010): quem escreve o que viu na semana, com data.'),
      achada='varredura paralela do eixo social', query='consulenza agronomica vite Instagram Italia',
      metodo='HTML + Instagram publico', scrap='YES', freq='FREQUENT', acesso='GREEN',
      coleta='PARTIAL', monitor='MONITOR_WEEKLY',
      dedupe='IT-SRCX-010', dedupe_means='mesma CLASSE de fonte (consultoria privada), casas diferentes',
      nota=('UMA VOZ NAO E TENDENCIA. Se coincidir com o Agralia, escreve-se CLUSTER NELLE '
            'FONTI MONITORATE, e nunca TREND IN ITALY.'),
      prova='minha leitura 2026-09-03: vitenova.it HTTP 200, 321.021 B, handle declarado na propria casa'),

    F('IT-SRCX-067',
      'Agricolus — plataforma de DSS agronomico (Perugia)',
      'Agricolus s.r.l.', 'DSS_COMMERCIAL', 'INDUSTRY', 'MEDIUM',
      'https://www.agricolus.com/',
      regiao='Umbria (sede), servico nacional',
      social={'INSTAGRAM': 'https://www.instagram.com/agricolus_srl'},
      feed='https://www.agricolus.com/wp-json/wp/v2/posts',
      crops=['VITE', 'OLIVO', 'POMODORO', 'MELO', 'PATATA'],
      temas=['MODELLI_PREVISIONALI', 'DSS', 'USO_SOSTENIBILE'],
      razao=('NAO e feed de janela: a Agricolus nao publica saida de modelo nem API aberta. '
             'O que vale monitorar e o argumento — a peca de 2026-08-05 que amarra uso de DSS '
             'ao contexto normativo, que e como "melhor timing" vira historia de conformidade '
             'sobre VITE (96 pares) e POMODORO (44), exatamente onde os boletins de producao '
             'integrada ja obrigam.'),
      achada='varredura paralela do eixo tecnico', query='Agricolus DSS modelli previsionali',
      metodo='HTML + WP REST + Instagram publico', scrap='YES', freq='PERIODIC',
      ultimo='2026-08-05', acesso='GREEN', coleta='PARTIAL', monitor='MONITOR_MONTHLY',
      dedupe='IT-SRCX-032', dedupe_means='mesma classe da Horta (DSS comercial); empresas distintas',
      nota=('o LinkedIn que a propria Agricolus declara no rodape devolve 404. Link declarado '
            'pelo dono nao e link vivo. api.agricolus.com falha com certificado autoassinado, '
            'e a verificacao TLS NAO foi desligada.'),
      prova='minha leitura 2026-09-03: agricolus.com HTTP 200, 356.152 B, handle declarado na propria casa'),

    F('IT-SRCX-068',
      'APOT — Associazione Produttori Ortofrutticoli Trentini',
      'APOT', 'PRODUCER_ORGANISATION', 'INDUSTRY', 'HIGH',
      'https://www.apot.it/',
      regiao='Trentino-Alto Adige',
      crops=['MELO'],
      temas=['REGISTRO_DI_CAMPAGNA', 'PRODUZIONE_INTEGRATA', 'CERTIFICAZIONI_DI_FILIERA'],
      razao=('a APOT agrupa Melinda, La Trentina e Co.P.A.G. e declara representar cerca de '
             '85% da producao frutica trentina. MELO e a 3a cultura do livro de rotulos da '
             'ADAMA (146 linhas) e o Trentino esta na lista de oportunidades — e o acervo '
             'canonico nao tinha canal nenhum para o corpo que DEFINE A DISCIPLINA DE '
             'PRODUCAO daquela maca. Quem escreve o caderno decide o que pode ser aplicado.'),
      achada='varredura paralela do eixo produtor', query='APOT associazione produttori ortofrutticoli trentini',
      metodo='HTML', freq='PERIODIC', acesso='GREEN', coleta='PARTIAL', monitor='MONITOR_MONTHLY',
      dedupe='IT-SRCX-015', dedupe_means='Assomela e nacional; APOT e a AOP trentina',
      nota='o site ainda carrega marcadores de tema nao substituidos — sinal de manutencao fraca.',
      prova='minha leitura 2026-09-03: HTTP 200, 103.162 B'),

    F('IT-SRCX-069',
      "Consorzi Agrari d'Italia (CAI)",
      "Consorzi Agrari d'Italia", 'COOPERATIVE_DISTRIBUTOR', 'INDUSTRY', 'HIGH',
      'https://www.consorziagrariditalia.it/',
      regiao='ITALIA',
      crops=['FRUMENTO', 'MAIS', 'BARBABIETOLA', 'ORZO', 'SOIA', 'OLIVO'],
      temas=['PRODOTTI_FITOSANITARI', 'AGROFORNITURE', 'LISTINI_CUN', 'GIORNATE_IN_CAMPO'],
      razao=('e a PRATELEIRA, e nao o campo: a maior rede de consorzi agrari da Italia, com '
             'linha declarada de "Prodotti Fitosanitari". As 163 registracoes do Ministero nao '
             'valem nada se nao forem carregadas pela rede que vende ao produtor de FRUMENTO '
             'e MAIS. E ela adota os listini CUN como referencia propria, o que liga preco a '
             'decisao de compra.'),
      achada='varredura paralela do eixo distribuicao', query='Consorzi Agrari d Italia prodotti fitosanitari',
      metodo='HTML', freq='FREQUENT', ultimo='2026-04-13', acesso='INTERMITTENT',
      coleta='PARTIAL', monitor='MONITOR_WEEKLY',
      dedupe='IT-SRCX-039', dedupe_means='o CUN e o listino oficial; o CAI e quem o adota',
      nota=('FONTE INTERMITENTE, medido por mim: primeira leitura 500 com 0 B; segunda leitura, '
            'minutos depois, 200 com 700.576 B. O apex sem www falha o TLS ("unrecognized '
            'name"). Quem monitorar isto precisa de repeticao, ou vai registrar queda que nao houve.'),
      prova='minhas duas leituras 2026-09-03: 500/0 e depois 200/700.576; /prodotti-servizi/prodotti-fitosanitari/ 200/119.439'),

    F('IT-SRCX-070',
      'Associazione Granaria di Milano — listino semanal AGMi',
      'Associazione Granaria di Milano', 'MARKET_PRICE_ASSOCIATION', 'INDUSTRY', 'MEDIUM',
      'https://www.granariamilano.it/',
      regiao='Lombardia (mercado padano)',
      crops=['MAIS', 'FRUMENTO', 'ORZO', 'SOIA', 'RISO'],
      temas=['LISTINO_COMMODITY', 'CONTRATTUALISTICA', 'ARBITRATO'],
      razao=('e o corpo que forma preco e escreve contrato para o comercio de graos do vale '
             'do Po, com listino publico semanal. Lombardia e regiao de oportunidade e este e '
             'o listino de referencia para MAIS (112 linhas de rotulo), FRUMENTO tenero e ORZO '
             'na mesma bacia das oportunidades de milho e cereal.'),
      achada='varredura paralela do eixo mercado', query='Associazione Granaria Milano listino settimanale',
      metodo='HTML + PDF', freq='PERIODIC', ultimo='2026-09-01', acesso='GREEN',
      coleta='PARTIAL', monitor='MONITOR_WEEKLY',
      nota=('LIMITE MEDIDO: o texto do PDF do listino NAO foi extraivel nesta sessao (fontes '
            'embutidas em subconjunto). A data do listino esta provada; os numeros dentro dele, nao.'),
      prova='minha leitura 2026-09-03: HTTP 200, 182.621 B, "Associazione Granaria Milano"'),

    F('IT-SRCX-071',
      'Unione Italiana Vini — Osservatorio del Vino e Il Corriere Vinicolo',
      'Unione Italiana Vini', 'INDUSTRY_ASSOCIATION', 'INDUSTRY', 'MEDIUM',
      'https://www.unioneitalianavini.it/',
      regiao='ITALIA (socios em Veneto, Piemonte, Toscana, Sicilia, Trentino)',
      crops=['VITE'],
      temas=['OSSERVATORIO_DEL_VINO', 'MERCATO_E_EXPORT', 'CORRIERE_VINICOLO'],
      razao=('VITE tem 96 linhas de rotulo e a producao esta em cinco regioes de oportunidade, '
             'mas o acervo so tinha o dominio de dia de campo da UIV, e nao o aparato de '
             'mercado da associacao. O Osservatorio del Vino e o denominador economico do '
             'vinho italiano — o que decide se um viticultor investe no programa de defesa '
             'da safra seguinte.'),
      achada='varredura paralela do eixo mercado', query='Unione Italiana Vini Osservatorio del Vino',
      metodo='HTML', freq='PERIODIC', acesso='GREEN', coleta='PARTIAL', monitor='MONITOR_MONTHLY',
      nota=('a UIV declara apenas LinkedIn e YouTube na propria casa. Nenhum outro handle e '
            'reivindicado aqui, porque nenhum outro foi declarado.'),
      prova='minha leitura 2026-09-03: HTTP 200, 2.457.612 B'),

    # ═══ D · MIDIA TECNICA ═════════════════════════════════════════════════════
    F('IT-SRCX-072',
      'OmniTrattore — secao Agrochimica e Sementi',
      'OmniTrattore', 'TECHNICAL_MEDIA', 'MEDIA', 'MEDIUM',
      'https://www.omnitrattore.it/news/797903/sdhi-dmi-zolfo-ticchiolatura/',
      regiao='ITALIA',
      crops=['MELO', 'RISO'],
      temas=['STRATEGIE_ANTIRESISTENZA', 'SDHI', 'DMI', 'MULTISITO', 'TICCHIOLATURA'],
      razao=('publica conselho de programa antirresistencia de 2026 para MELO no vocabulario '
             'quimico da propria ADAMA: SDHI e o FLUXAPYROXAD, DMI e o DIFENOCONAZOLE e o '
             'TEBUCONAZOLE, e as ancoras multissitio que prescreve sao CAPTAN e FOLPET — '
             'quatro ativos ADAMA em uma unica recomendacao.'),
      achada='varredura paralela do eixo midia', query='SDHI DMI zolfo ticchiolatura antiresistenza melo',
      metodo='HTML (exige --compressed)', freq='FREQUENT', ultimo='2026-07-04', acesso='GREEN',
      coleta='AUTOMATABLE', monitor='MONITOR_WEEKLY',
      nota=('MEDIA e MEDIUM de proposito: e reportagem secundaria de estrategia, e nao '
            'medicao. Nada aqui certifica populacao resistente — so o GIRE certifica.'),
      prova='minha leitura 2026-09-03: HTTP 200, 125.036 B'),

    F('IT-SRCX-073',
      'Agrimpresa — periodico da CIA Emilia-Romagna',
      'CIA Agricoltori Italiani — Emilia-Romagna', 'TECHNICAL_MEDIA', 'MEDIA', 'MEDIUM',
      'https://agrimpresaonline.it/',
      regiao='Emilia-Romagna',
      social={'INSTAGRAM': 'https://www.instagram.com/agrimpresa_magazine'},
      crops=['MELO', 'PERO', 'POMODORO', 'BARBABIETOLA', 'VITE'],
      temas=['ATTUALITA_AGRICOLA_REGIONALE', 'VOCE_DEGLI_AGRICOLTORI'],
      razao=('e a imprensa de uma organizacao de produtores dentro da regiao mais pesada do '
             'radar. Nao e servico fitossanitario e nao emite aviso, mas e onde a queixa do '
             'produtor emiliano vira texto publico — que e o unico lugar onde "o que doi no '
             'campo" aparece antes de virar estatistica.'),
      achada='varredura paralela do eixo social', query='Agrimpresa CIA Emilia-Romagna',
      metodo='HTML + Instagram publico', scrap='YES', freq='FREQUENT', acesso='GREEN',
      coleta='PARTIAL', monitor='MONITOR_WEEKLY',
      nota='VOZ DE ORGANIZACAO != SINAL DE CAMPO VERIFICADO.',
      prova='minha leitura 2026-09-03: agrimpresaonline.it HTTP 200, 189.952 B, handle declarado na propria casa'),

    F('IT-SRCX-074',
      'AgroNotizie — rota de noticias POR EMPRESA (/aziende/<slug>/<id>)',
      'Image Line s.r.l.', 'COMPETITOR_PRESS_FOOTPRINT', 'TECHNICAL', 'MEDIUM',
      'https://agronotizie.imagelinenetwork.com/aziende/syngenta-italia/1196',
      regiao='ITALIA',
      crops=['BARBABIETOLA', 'MAIS', 'VITE', 'POMODORO', 'FRAGOLA', 'CAROTA', 'TABACCO'],
      temas=['PRESENCA_DE_CONCORRENTE_NA_IMPRENSA_TECNICA'],
      razao=('responde a pergunta que o site corporativo nao responde: quanto espaco editorial '
             'cada concorrente ocupa na imprensa tecnica italiana. Existe fluxo por empresa '
             'para todas as majors, inclusive /aziende/adama-italia/1216.'),
      achada='snowballing a partir do Fitogest', query='AgroNotizie aziende elenco slug',
      metodo='HTML', freq='FREQUENT', acesso='GREEN', coleta='PARTIAL', monitor='MONITOR_MONTHLY',
      dedupe='REJEITADA_agronotizie_lista_de_produtos',
      dedupe_means=('MESMO HOST, ROTA DIFERENTE. A lista de PRODUTOS na pagina de empresa foi '
                    'rejeitada (e catalogo do site, nao portfolio da empresa). A rota de '
                    'NOTICIAS por empresa e outra coisa e vale.'),
      nota='PEGADA NA IMPRENSA != PARTICIPACAO DE MERCADO.',
      prova='minha leitura 2026-09-03: HTTP 200, 104.421 B, "Notizie su Syngenta Italia - AgroNotizie"'),

    # ═══ E · CONCORRENTE ═══════════════════════════════════════════════════════
    F('IT-SRCX-075',
      'Corteva Agriscience Italia — canal oficial de WhatsApp',
      'Corteva Agriscience Italia', 'COMPETITOR_SOCIAL_BROADCAST', 'COMPETITOR', 'HIGH',
      'https://www.whatsapp.com/channel/0029VafMuYo9Bb5zNEvf4b3U',
      regiao='ITALIA', plataforma='WHATSAPP',
      crops=['MAIS', 'VITE', 'POMODORO', 'AGRUMI', 'OLIVO', 'CAROTA', 'FRAGOLA'],
      temas=['BROADCAST_TECNICO_AO_PRODUTOR'],
      razao=('e um concorrente falando DIRETO no telefone do produtor italiano, sem passar por '
             'midia nem por distribuidor. O canal esta declarado pela propria Corteva na sua '
             'pagina da Mappa Piralide (LEI 6 satisfeita), e a pagina publica de previa '
             'declara 1.522 seguidores. Canal de broadcast e o formato mais dificil de '
             'observar e o mais proximo da decisao.'),
      achada='snowballing a partir de IT-SRCX-037 (Corteva Mappa Piralide)',
      query='Corteva Italia canale WhatsApp ufficiale',
      metodo='pagina publica de previa (SEM login, SEM entrar no canal)',
      freq='UNKNOWN', acesso='GREEN', coleta='PARTIAL', monitor='MONITOR_WEEKLY',
      dedupe='IT-SRCX-037', dedupe_means='mesma empresa, canal completamente distinto',
      nota=('CONTEUDO DO CANAL NAO FOI COLETADO e nao sera: entrar no canal e conteudo nao '
            'publico. So a previa publica foi lida.'),
      prova='minha leitura 2026-09-03: HTTP 200, 203.629 B, "Corteva Agriscience Italia - WhatsApp channel"'),

    F('IT-SRCX-076',
      'Fitogest (Image Line) — diretorio de empresas produtoras, rota /it/aziende/',
      'Image Line s.r.l.', 'COMPETITOR_CATALOGUE_DIRECTORY', 'TECHNICAL', 'HIGH',
      'https://fitogest.imagelinenetwork.com/it/aziende/',
      regiao='ITALIA',
      crops=['BARBABIETOLA', 'FRUMENTO', 'MELO', 'MAIS', 'PATATA', 'VITE'],
      temas=['CATALOGO_AGROFARMACI_POR_EMPRESA', 'CANAIS_SOCIAIS_DECLARADOS'],
      razao=('e a UNICA rota alcancavel que da a esta casa uma contagem de catalogo italiano '
             'por concorrente — inclusive para as duas majors cujos proprios sites recusam '
             'esta sessao (syngenta.it 403, cropscience.bayer.it 403). Contagem lida direto '
             'das paginas: Syngenta 136, UPL 116, Corteva 93, Bayer 78, Certis Belchim 63, '
             'ADAMA Italia 56.'),
      achada='varredura paralela do eixo concorrente', query='Fitogest aziende catalogo agrofarmaci',
      metodo='HTML', freq='PERIODIC', acesso='GREEN', coleta='AUTOMATABLE', monitor='MONITOR_MONTHLY',
      nota=('OS 56 DO FITOGEST NAO SAO OS 51 COMERCIAIS NEM AS 163 REGISTRACOES. Sao tres '
            'contagens de tres donos diferentes e nao podem ser comparadas como se fossem a '
            'mesma coisa. A rota /aziende/ sem o prefixo /it/ devolve 300.'),
      prova='minha leitura 2026-09-03: HTTP 200, 54.429 B'),

    F('IT-SRCX-077',
      'Fitogest — Syngenta Italia (catalogo de 136 agrofarmaci)',
      'Image Line s.r.l. (sobre Syngenta Italia)', 'COMPETITOR_CATALOGUE_VIA_MEDIA',
      'TECHNICAL', 'HIGH',
      'https://fitogest.imagelinenetwork.com/it/aziende/syngenta-italia/1196',
      regiao='ITALIA',
      crops=['BARBABIETOLA', 'FRUMENTO', 'MAIS', 'VITE', 'POMODORO', 'FRAGOLA', 'CILIEGIO'],
      temas=['CATALOGO_CONCORRENTE', 'COLTURE_E_AVVERSITA_COPERTE'],
      razao=('a Syngenta e o maior concorrente por profundidade de catalogo italiano — 136 '
             'agrofarmaci contra os 56 da ADAMA no MESMO diretorio, que e a unica comparacao '
             'com denominador honesto que esta sessao consegue fazer. E esta e a UNICA rota '
             'pela qual esse catalogo pode ser lido daqui.'),
      achada='snowballing a partir do diretorio Fitogest', query='Fitogest Syngenta Italia catalogo',
      metodo='HTML', freq='PERIODIC', acesso='GREEN', coleta='AUTOMATABLE', monitor='MONITOR_MONTHLY',
      dedupe='IT-SRCX-076', dedupe_means='pagina de empresa dentro do diretorio ja registrado',
      nota='PRODUTO DE CONCORRENTE NAO E PRODUTO ADAMA, e catalogo nao e venda.',
      prova='minha leitura 2026-09-03: HTTP 200, 235.267 B, "Syngenta Italia - Fitogest"'),

    F('IT-SRCX-078',
      'Fitogest — Bayer (catalogo de 78 agrofarmaci), unica rota legivel para a Bayer Italia',
      'Image Line s.r.l. (sobre Bayer)', 'COMPETITOR_CATALOGUE_VIA_MEDIA', 'TECHNICAL', 'HIGH',
      'https://fitogest.imagelinenetwork.com/it/aziende/bayer/1194',
      regiao='ITALIA',
      crops=['FRUMENTO', 'ORZO', 'MELO', 'VITE', 'MAIS', 'PATATA', 'POMODORO'],
      temas=['CATALOGO_CONCORRENTE'],
      razao=('todo o patrimonio web italiano da Bayer recusa esta sessao — cropscience.bayer.it '
             '403, bayer.it 403, bayer.com/it/it 403, os tres servindo "Site Maintenance". '
             'ROUTE_BLOCKED_FOR_AUTOMATION e o estado da fonte, e nao ausencia de conteudo. '
             'Esta pagina e o unico lugar em que o catalogo italiano da Bayer segue legivel.'),
      achada='snowballing a partir do diretorio Fitogest', query='Fitogest Bayer catalogo agrofarmaci',
      metodo='HTML', freq='PERIODIC', acesso='GREEN', coleta='AUTOMATABLE', monitor='MONITOR_MONTHLY',
      dedupe='IT-SRCX-076', dedupe_means='pagina de empresa dentro do diretorio ja registrado',
      prova='minha leitura 2026-09-03: HTTP 200, 166.075 B, "Bayer - Fitogest"'),

    F('IT-SRCX-079',
      'BASF Agricultural Solutions Italia — Bollettini Tecnici Digitali',
      'BASF Italia', 'COMPETITOR_TECHNICAL_BULLETIN', 'COMPETITOR', 'HIGH',
      'https://www.agro.basf.it/it/News/Bollettini-Tecnici-Digitali/',
      regiao='ITALIA',
      crops=['BARBABIETOLA', 'FRUMENTO', 'ORZO', 'MAIS', 'RISO', 'PATATA', 'COLZA', 'SOIA',
             'BRASSICACEE', 'OLIVO', 'AGRUMI', 'VITE'],
      temas=['CAMBI_DI_ETICHETTA', 'AGGIORNAMENTI_REGOLATORI', 'NOVITA_DI_PRODOTTO'],
      razao=('as palavras da propria BASF para este canal sao "cambi di etichetta e gli '
             'aggiornamenti regolatori" — um concorrente TRANSMITINDO MUDANCA DE ROTULO ao '
             'comercio italiano. Mudanca de rotulo do rival e o unico evento de concorrente '
             'que move a posicao da ADAMA sem a ADAMA fazer nada: um uso ganho ou perdido em '
             'BARBABIETOLA (239 pares, a cultura mais pesada) muda a prateleira sozinho.'),
      achada='varredura paralela do eixo concorrente', query='BASF Italia bollettini tecnici digitali cambi di etichetta',
      metodo='HTML', freq='PERIODIC', acesso='GREEN', coleta='AUTOMATABLE', monitor='MONITOR_WEEKLY',
      nota='ROTULO DE CONCORRENTE != ROTULO ADAMA. Cada um tem o seu registro no Ministero.',
      prova='minha leitura 2026-09-03: HTTP 200, 92.546 B, "Info-Tecniche Digitali"'),

    F('IT-SRCX-080',
      'BASF Italia — podcast "Minuti di Riso"',
      'BASF Italia', 'COMPETITOR_PODCAST', 'COMPETITOR', 'MEDIUM',
      'https://www.agro.basf.it/it/Progetti/Minuti-di-Riso/Minuti-di-Riso-2023/',
      regiao='Piemonte / Lombardia (areal risicolo)',
      crops=['RISO'],
      temas=['PODCAST_DI_FILIERA', 'CLEARFIELD', 'PROVISIA', 'DISERBO_DEL_RISO'],
      razao=('um concorrente rodando PODCAST em italiano como canal de cultura. RISO e linha '
             'pequena para a ADAMA (15 pares de rotulo) mas estrategicamente fechada: a BASF '
             'e dona dos sistemas Clearfield e Provisia de tolerancia a herbicida, que e '
             'exatamente o que decide o diserbo do arroz onde a resistencia do giavone ja '
             'esta certificada.'),
      achada='snowballing a partir do site da BASF Italia', query='BASF Minuti di Riso podcast',
      feed='https://api.spreaker.com/v2/shows/5619070/episodes',
      metodo='HTML + API Spreaker', freq='STATIC', ultimo='2023-12-07', acesso='GREEN',
      coleta='AUTOMATABLE', monitor='DO_NOT_MONITOR',
      video='NO', transcricao='ACERVO_HISTORICO',
      nota=('CONGELADO, e isso foi MEDIDO e nao suposto: o programa esta no Spreaker com '
            'show_id 5619070 e o ultimo episodio e de 2023-12-07, intitulado "28 - Arrivederci". '
            'A BASF se despediu do canal. Eu havia escrito PERIODIC lendo a pagina; a API '
            'desmente. Ver FIX-03. Os 28 episodios continuam colhiveis como ACERVO — o que nao '
            'existe e cadencia.'),
      prova=('minha leitura 2026-09-03: pagina HTTP 200 / 195.199 B; API Spreaker '
             'shows/5619070/episodes, ultimo published_at 2023-12-07')),

    F('IT-SRCX-081',
      'BASF Italia — Agrigenius (DSS de vinha)',
      'BASF Italia', 'COMPETITOR_DSS', 'COMPETITOR', 'MEDIUM',
      'https://www.agro.basf.it/it/Soluzioni-digitali/Agrigenius/',
      regiao='ITALIA',
      crops=['VITE'],
      temas=['DSS', 'MODELLI_PERONOSPORA_E_OIDIO'],
      razao=('"Agrigenius Vite — Il tutor per l\'agricoltura" e um concorrente se colocando '
             'ENTRE o produtor e a decisao de pulverizar, sobre VITE, que carrega 96 pares de '
             'rotulo em cinco regioes de oportunidade. Um DSS e objeto competitivo mais duro '
             'que uma pagina de produto, porque captura a decisao e nao apenas a preferencia.'),
      achada='snowballing a partir do site da BASF Italia', query='BASF Agrigenius Vite DSS',
      metodo='HTML', freq='PERIODIC', acesso='GREEN', coleta='PARTIAL', monitor='MONITOR_MONTHLY',
      dedupe='IT-SRCX-032', dedupe_means='mesma classe (DSS); a Horta e independente, a BASF e fabricante',
      nota='a area reservada (/it/Servizi/ssp/) e murada por login e NAO foi acessada.',
      prova='minha leitura 2026-09-03: HTTP 200, 114.742 B, "Agrigenius Vite - Il tutor per l\'agricoltura"'),

    F('IT-SRCX-082',
      'UPL Italia — catalogo de produtos (uplitalia.com)',
      'UPL Italia', 'COMPETITOR_PRODUCT_CATALOGUE', 'COMPETITOR', 'HIGH',
      'https://www.uplitalia.com/it/prodotti',
      regiao='ITALIA',
      crops=['BARBABIETOLA', 'FRUMENTO', 'MELO', 'VITE', 'POMODORO', 'PATATA'],
      temas=['CATALOGO_AGROFARMACI', 'SCHEDE_PRODOTTO'],
      razao=('a UPL e o analogo estrutural mais proximo da ADAMA na Italia — portfolio pesado '
             'em generico e fora de patente — e o Fitogest poe seu catalogo italiano em 116 '
             'agrofarmaci contra 56 da ADAMA. Ler o catalogo da propria UPL, e nao so a '
             'contagem de terceiro, e o que permite comparar cultura a cultura.'),
      achada='varredura paralela do eixo concorrente', query='UPL Italia catalogo prodotti',
      metodo='HTML', freq='PERIODIC', acesso='GREEN', coleta='AUTOMATABLE', monitor='MONITOR_MONTHLY',
      nota=('o briefing registrava a UPL como 500. Nao e o estado da fonte: uplitalia.com '
            'responde 200 com 347 KB. uplitalia.IT, esse sim, nao abre daqui.'),
      prova='minha leitura 2026-09-03: HTTP 200, 347.499 B, "Prodotti | UPL"'),

    F('IT-SRCX-083',
      'Diachem S.p.A. — blog tecnico e Campo Dimostrativo (Caravaggio BG)',
      'Diachem S.p.A.', 'COMPETITOR_FIELD_DAY', 'COMPETITOR', 'HIGH',
      'https://diachemagro.com/blog/',
      regiao='Lombardia (campo de prova em Caravaggio, BG)',
      crops=['POMODORO', 'PATATA', 'BARBABIETOLA', 'FRUMENTO', 'MAIS', 'MELO', 'VITE', 'RISO'],
      temas=['CAMPO_DIMOSTRATIVO', 'DIFESA_E_NUTRIZIONE_POMODORO_E_PATATA', 'CATALOGO_2026'],
      razao=('e a evidencia de DIA DE CAMPO que o eixo de concorrente pedia, e vinda de um '
             'fabricante ITALIANO, e nao de subsidiaria de multinacional. A Diachem abriu o '
             'campo de Caravaggio (Lombardia, regiao de oportunidade) para mostrar '
             '"le strategie applicate per la difesa e la nutrizione di pomodoro e patata da '
             'industria" — que e exatamente onde POMODORO e PATATA (100 pares) se decidem.'),
      achada='varredura paralela do eixo concorrente', query='Diachem campo dimostrativo pomodoro patata',
      metodo='HTML', freq='PERIODIC', ultimo='2026-07-02', acesso='GREEN',
      coleta='AUTOMATABLE', monitor='MONITOR_MONTHLY',
      nota='chimiberg.it redireciona para diachemagro.com — mesma casa, dominio novo.',
      prova='minha leitura 2026-09-03: HTTP 200, 177.585 B, "Blog agricoltura - Diachem"'),

    F('IT-SRCX-084',
      'Sipcam Italia — ficha da entidade no grupo Sipcam Oxon',
      'Sipcam Oxon S.p.A.', 'COMPETITOR_CORPORATE_ENTITY', 'COMPETITOR', 'MEDIUM',
      'https://www.sipcam-oxon.com/en/sipcam-italia',
      regiao='Lombardia (Pero MI, Lodi, Salerano) e Pavia (Mezzana Bigli)', lingua='EN',
      crops=['SOIA', 'BARBABIETOLA', 'FRUMENTO', 'MAIS', 'VITE'],
      temas=['ENTIDADE_ITALIANA_DO_GRUPO', 'SINTESE_DE_SUBSTANCIA_ATIVA_NA_ITALIA'],
      razao=('e a pagina que RESOLVE a armadilha de entidade errada: sipcamitalia.it e '
             'sipcam.it servem, os dois, a Sipcam Agro USA. A entidade italiana real esta '
             'descrita aqui, com planta de sintese de substancia ativa em Mezzana Bigli (PV) '
             '— um concorrente que FABRICA ativo na Italia, e nao apenas formula.'),
      achada='resolucao da rejeicao sipcamitalia.it', query='Sipcam Oxon Sipcam Italia entity',
      metodo='HTML', freq='STATIC', acesso='GREEN', coleta='AUTOMATABLE', monitor='MONITOR_MONTHLY',
      dedupe='REJEITADA_sipcamitalia.it', dedupe_means='a rejeicao continua valida; esta e a entidade certa',
      nota='sipcam-oxon.com/it/ devolve 404: o grupo NAO tem versao italiana do site corporativo.',
      prova='minha leitura 2026-09-03: HTTP 200, 126.227 B, "Sipcam Italia - SIPCAM OXON"'),

    F('IT-SRCX-085',
      'DEKALB Italia (grupo Bayer) — canal de milho em italiano',
      'Bayer / DEKALB', 'COMPETITOR_BRAND_SITE', 'COMPETITOR', 'MEDIUM',
      'https://www.dekalb.it/',
      regiao='Norte da Italia (areal maidicolo)',
      crops=['MAIS'],
      temas=['COLTIVAZIONE_DEL_MAIS', 'IBRIDI_E_AGRONOMIA'],
      razao=('e o unico canal italiano do grupo Bayer que esta sessao conseguiu ler, e MAIS '
             'carrega 112 pares de rotulo. Enquanto cropscience.bayer.it, bayer.it e '
             'bayer.com/it/it devolvem 403, o dekalb.it responde 200 — e e por ele que se '
             've como a Bayer fala com o produtor italiano de milho.'),
      achada='varredura paralela do eixo concorrente', query='DEKALB Italia mais Bayer',
      metodo='HTML', freq='PERIODIC', acesso='GREEN', coleta='AUTOMATABLE', monitor='MONITOR_MONTHLY',
      dedupe='IT-SRCX-078', dedupe_means='mesmo grupo; marca de semente e nao de defensivo',
      nota='SEMENTE NAO E DEFENSIVO. Este canal e agronomia de hibrido, e nao rotulo de fitossanitario.',
      prova='minha leitura 2026-09-03: HTTP 200, 96.539 B, final /index/index.html'),

    F('IT-SRCX-086',
      'CBC (Europe) Biogard — biocontrole italiano, fichas por cultura',
      'CBC (Europe) S.r.l. — divisao Biogard', 'COMPETITOR_PRODUCT_SITE', 'COMPETITOR', 'MEDIUM',
      'https://www.biogard.it/',
      regiao='ITALIA',
      crops=['MELO', 'PERO', 'FRAGOLA', 'VITE', 'POMODORO', 'AGRUMI', 'OLIVO'],
      temas=['CONFUSIONE_SESSUALE', 'MACRORGANISMI', 'NEMATOCIDI_BIOLOGICI', 'MONITORAGGIO'],
      razao=('a arvore de produtos da Biogard cobre confusao sexual, macrorganismos, '
             'nematicidas, acaricidas, fungicidas, inseticidas E monitoramento — e a propria '
             'ADAMA Italia tem 5 armadilhas no catalogo Fitogest. O segmento de feromonio e '
             'armadilha e, portanto, terreno DISPUTADO, e nao um mundo separado do quimico.'),
      achada='varredura paralela do eixo concorrente', query='Biogard CBC Europe biocontrollo colture',
      metodo='HTML', freq='PERIODIC', acesso='GREEN', coleta='AUTOMATABLE', monitor='MONITOR_MONTHLY',
      prova='minha leitura 2026-09-03: HTTP 200, 261.987 B, "Biogard - Biological first"'),

    # ═══ F · EVENTO ════════════════════════════════════════════════════════════
    F('IT-SRCX-087',
      'Veronafiere — calendario Italia 2027',
      'Veronafiere S.p.A.', 'EVENT_CALENDAR_VENUE', 'INDUSTRY', 'MEDIUM',
      'https://www.veronafiere.it/calendario-fiere/calendario-italia-2027/',
      regiao='Veneto (Verona), alcance nacional',
      crops=['VITE', 'OLIVO'],
      temas=['FIERAGRICOLA_TECH', 'VINITALY', 'ENOLITECH', 'SOLEXPO'],
      razao=('o acervo tem os sites dos eventos, mas nao o calendario do OPERADOR DO RECINTO — '
             'que e onde as datas de 2027 aparecem primeiro e todas juntas. Fieragricola TECH '
             '27-28 de janeiro de 2027 e Vinitaly 11-14 de abril de 2027 sao janelas com data '
             'em VITE, cultura de 96 pares de rotulo.'),
      achada='varredura paralela do eixo evento', query='Veronafiere calendario 2027 fiere agricole',
      metodo='HTML', freq='PERIODIC', ultimo='2027-01-27', acesso='GREEN',
      coleta='AUTOMATABLE', monitor='MONITOR_MONTHLY',
      nota=('EVENTO COM DATA FUTURA != SINAL DE CAMPO. E agenda, e serve para planejar '
            'presenca, nao para decidir tratamento. O dominio dedicado fieragricolatech.it '
            'NAO abre daqui — a data vem do calendario do recinto.'),
      prova='minha leitura 2026-09-03: HTTP 200, 119.996 B, "Calendario Italia 2027 - Primo semestre"'),
]

# ── A CULTURA COM A MAIOR ASSIMETRIA DO RADAR, E A FONTE QUE FALA DELA TODA SEMANA ──
# OLIVO tem UM par de rotulo lido em 2.030 e TRES oportunidades. Esta e a fonte que fala
# dessa cultura semanalmente, em video, com data e com nivel de risco por macro-regiao.
# Ela entra no acervo, e ela NAO CRUZA — ver IT-NX-2026-005 em scripts/it_cruzamentos.py.

FONTES += [
    F('IT-SRCX-091',
      "l'OlivoNews — bollettino olivicolo settimanale in video",
      "l'OlivoNews", 'FIELD_BULLETIN_VIDEO', 'MEDIA', 'HIGH',
      'https://olivonews.it/',
      regiao='ITALIA (Nord · Centro · Sud e isole, declarados pelo proprio boletim)',
      feed='https://www.olivonews.it/feed/',
      crops=['OLIVO'],
      temas=['MOSCA_OLEARIA', 'STATO_DI_ALLERTA', 'RECETTIVITA_DELLE_DRUPE', 'INVAIATURA'],
      razao=('OLIVO e a maior assimetria da tabela: UM par de rotulo lido em 2.030 e TRES '
             'oportunidades. Esta fonte publica um bollettino SEMANAL em video, com data, com '
             'nivel de risco por macro-regiao e com as moleculas de intervencao nomeadas. '
             'E o unico lugar do radar em que a cultura de menor leitura de rotulo fala toda '
             'semana — e por isso ela entra mesmo NAO cruzando com o portfolio.'),
      achada='rota de midia auto-hospedada em dominio italiano (varredura paralela), reconferida por mim',
      query='olivonews bollettino olivicolo settimanale',
      metodo='RSS + MP4 auto-hospedado + faster-whisper small LOCAL',
      scrap='YES', video='YES', transcricao='YES',
      freq='FREQUENT', ultimo='2026-08-30', acesso='GREEN', coleta='AUTOMATABLE',
      monitor='MONITOR_WEEKLY',
      nota=('AS MOLECULAS QUE ELE NOMEIA NAO SAO DA ADAMA. acetamiprid, flupyradifurone, '
            'spinosad, caolino calcinato e azadiractina — nenhuma esta entre as 53 '
            'substancias ativas do corpus. O unico rotulo OLIVO da ADAMA e MORAINE (018101) '
            'contra INFESTANTI: um HERBICIDA. A conversa italiana da oliveira e sobre a MOSCA; '
            'o portfolio lido responde por ERVA DANINHA. Isto e posicao de portfolio, e nao '
            'oportunidade — e e exatamente por isso que precisa estar escrito.'),
      prova=('minha leitura 2026-09-03: os tres MP4 semanais respondem 200 com content-type '
             'video/mp4; transcritos localmente, 11.427 caracteres, e o alvo lido e '
             'MOSCA_OLEARIA nos tres.')),
]


# ── A CAMADA DE AUDIO, DEPOIS DE O INSTAGRAM TER FALHADO TRES VEZES ────────────
# Tres lotes de Instagram renderam 5, 2 e 0 sinais so-na-fala. O podcast agronomico e
# o oposto do reel: 20 a 40 minutos, com pesquisador e produtor no mesmo audio, e uma
# descricao de duas linhas — o sinal esta na fala por CONSTRUCAO. Rota permanente em
# scripts/it_audio.py, via API publica do Spreaker, sem chave.

FONTES += [
    F('IT-SRCX-088',
      'Terra di Denari — podcast de cadeia agricola',
      'Terra di Denari', 'PODCAST', 'MEDIA', 'MEDIUM',
      'https://www.spreaker.com/podcast/terra-di-denari--6623075',
      regiao='ITALIA', plataforma='SPREAKER',
      feed='https://api.spreaker.com/v2/shows/6623075/episodes',
      crops=['FRUMENTO', 'VITE', 'OLIVO'],
      temas=['FILIERA_AGRICOLA', 'MERCATO', 'POLITICA_AGRICOLA'],
      razao=('entra pelo FORMATO, e a razao e honesta: 30 minutos de fala e onde cabe a frase '
             'tecnica que um reel de 30 segundos nunca comporta. O acervo mediu isso — 9 '
             'episodios do Agricast deram 130.935 caracteres de agronomia italiana, contra '
             '37.166 de 28 reels.'),
      achada='api.spreaker.com/v2/search?type=shows', query='spreaker search q=terra di denari',
      metodo='API JSON + mp3 + ffmpeg + faster-whisper small LOCAL',
      scrap='YES', video='NO', transcricao='YES',
      freq='PERIODIC', ultimo='2026-07-14', acesso='GREEN', coleta='AUTOMATABLE',
      monitor='MONITOR_MONTHLY',
      dedupe='IT-SRCX-016', dedupe_means='mesma plataforma e mesma rota; programas distintos',
      nota='cadencia irregular: 2 episodios em 90 dias. E canal vivo, e nao canal frequente.',
      prova='API Spreaker shows/6623075/episodes lida por mim em 2026-09-03: 13 episodios, ultimo 2026-07-14'),

    F('IT-SRCX-089',
      'AGRINET4TECH: storie di sostenibilita — podcast por territorio',
      'AGRINET4TECH', 'PODCAST', 'MEDIA', 'HIGH',
      'https://www.spreaker.com/podcast/agrinet4tech--7026131',
      regiao='ITALIA (um territorio nomeado por episodio)', plataforma='SPREAKER',
      feed='https://api.spreaker.com/v2/shows/7026131/episodes',
      crops=['FRAGOLA', 'BASILICO', 'POMODORO', 'MAIS'],
      temas=['AGRICOLTURA_DIGITALE', 'TERRITORIO', 'SOSTENIBILITA'],
      razao=('cada episodio e um LUGAR declarado pelo proprio programa — Metapontino e a '
             'fragola, Ponente Ligure e o basilico, Delta do Po, Piana di Sibari, Bassa '
             'Mantovana, Ringhiera dell Umbria. GEOGRAFIA DECLARADA e exatamente o que falta '
             'na maior parte da voz publica italiana: sinal sem lugar nao cruza com oportunidade, '
             'porque oportunidade tem regiao.'),
      achada='api.spreaker.com/v2/search?type=shows', query='spreaker search q=agrinet4tech',
      metodo='API JSON + mp3 + ffmpeg + faster-whisper small LOCAL',
      scrap='YES', video='NO', transcricao='YES',
      freq='FREQUENT', ultimo='2026-08-02', acesso='GREEN', coleta='AUTOMATABLE',
      monitor='MONITOR_WEEKLY',
      nota=('LUGAR NOMEADO NO TITULO != FATO OBSERVADO NAQUELE LUGAR. O territorio e o tema do '
            'episodio; o que se afirma sobre ele ainda precisa sair da fala.'),
      prova='API Spreaker shows/7026131/episodes lida por mim em 2026-09-03: 11 episodios, 9 na janela de 90 dias'),

    F('IT-SRCX-090',
      'Cia Umbria Agripodcast',
      'CIA Agricoltori Italiani — Umbria', 'PODCAST', 'FIELD_VOICE', 'MEDIUM',
      'https://www.spreaker.com/podcast/cia-umbria-agripodcast--4600385',
      regiao='Umbria', plataforma='SPREAKER',
      feed='https://api.spreaker.com/v2/shows/4600385/episodes',
      crops=['OLIVO', 'VITE', 'TABACCO', 'FRUMENTO'],
      temas=['VOZ_DE_ORGANIZACAO_DE_PRODUTORES', 'ATTUALITA_REGIONALE'],
      razao=('CONTRASTE DELIBERADO, e esta e a razao inteira: a Umbria NAO aparece em nenhuma '
             'das 37 oportunidades do radar. Sem uma regiao de fora no lote, a frase "as fontes '
             'monitoradas falam das regioes da ADAMA" nao tem controle — ela seria verdadeira '
             'por construcao da lista, e nao por medicao.'),
      achada='api.spreaker.com/v2/search?type=shows', query='spreaker search q=cia umbria',
      metodo='API JSON + mp3 + ffmpeg + faster-whisper small LOCAL',
      scrap='YES', video='NO', transcricao='YES',
      freq='PERIODIC', ultimo='2026-07-27', acesso='GREEN', coleta='AUTOMATABLE',
      monitor='MONITOR_MONTHLY',
      dedupe='IT-SRCX-073', dedupe_means='mesma confederacao (CIA), federacao regional diferente e outra midia',
      prova='API Spreaker shows/4600385/episodes lida por mim em 2026-09-03: 18 episodios, ultimo 2026-07-27'),
]

# Programas medidos e DEIXADOS DE FORA — a data e o motivo, e ela fica escrita para que
# ninguem gaste a busca duas vezes.
NAO_ALCANCADAS += [
    {'HOST': ('spreaker: MINUTI DI RISO (5619070) · Lezioni di Vite (5837404) · '
              'La settimana del riso (6634834) · Just Agronomo (6411513)'),
     'STATE': 'CANAL_CONGELADO',
     'MEANS': ('quatro programas italianos de assunto certo e relogio parado: ultimo episodio '
               'em 2023-12-07, 2023, 2025-07-26 e 2024-12-24. Nenhum deles esta morto como '
               'ACERVO — "Peronospora della vite, come e quando intervenire" continua sendo '
               'exatamente o assunto. O que nao existe e cadencia, e cadencia e o que separa '
               'monitoramento de arqueologia.')},
]

# ── O QUE A MINHA CONFERENCIA DERRUBOU ─────────────────────────────────────────
# A varredura paralela admitiu estas duas como fonte. Eu fui ler e nao sustentam.

REJEITADAS += [
    {'NAME': 'ANICAV — Associazione Nazionale Industriali Conserve Alimentari Vegetali',
     'URL': 'https://anicav.it/',
     'REJECTION_CLASS': 'ROUTE_BLOCKED_FOR_AUTOMATION',
     'REASON': ('a varredura paralela leu 81.358 B de conteudo e admitiu a ANICAV como fonte '
                'INDUSTRY/MEDIUM. Eu li duas vezes, em anicav.it e em www.anicav.it: HTTP 200 '
                'com 33.245 B IDENTICOS nos dois hosts, e o titulo e '
                '"Security Check Required". E muro de bot, da mesma familia de anb.it e '
                'bmti.it. HTTP 200 COM BYTES NAO E CONTEUDO.'),
     'ACTION': ('nao registrar como fonte viva. O assunto continua valendo — a ANICAV e o lado '
                'comprador do pomodoro da industria — entao fica em NAO_ALCANCADAS para ser '
                'tentada de outro egresso.'),
     'EVIDENCE': 'minhas duas leituras 2026-09-03: 200/33.245 em ambos os hosts, titulo "Security Check Required"'},

    {'NAME': 'CSO Italy — handle de LinkedIn declarado (IT-SRCX-035)',
     'URL': 'https://it.linkedin.com/company/cso---centro-servizi-ortofrutticoli',
     'REJECTION_CLASS': 'HANDLE_NAO_RECONFIRMADO',
     'REASON': ('o handle esta gravado em IT-SRCX-035 com prova "wf_social-technical-voices.json '
                '· HTTP 200" — ou seja, prova de AGENTE, e nao leitura minha. Fui conferir a LEI '
                '6 na casa do proprio dono: csoservizi.com devolve 200 com 50.746 B e ZERO link '
                'para linkedin, instagram, youtube ou facebook. A varredura relatou 331.929 B '
                'para a mesma pagina; eu nao reproduzo esse tamanho nem esse bloco social.'),
     'ACTION': ('o handle FICA na ficha, porque pode existir; mas passa a carregar a ressalva de '
                'nao reconfirmado, e nao entra no lote de coleta social ate ser declarado na casa '
                'do dono. Ver FIX-02.'),
     'EVIDENCE': 'minha leitura 2026-09-03: csoservizi.com 200 / 50.746 B, grep por linkedin|instagram|youtube|facebook = 0 resultados'},
]

NAO_ALCANCADAS += [
    {'HOST': 'anicav.it · anb.it · bmti.it',
     'STATE': 'MURO_DE_BOT (sgcaptcha / "Security Check Required")',
     'MEANS': ('tres corpos de cadeia — conservas vegetais, bieticultores e a bolsa telematica — '
               'atras de muro de bot. O bmti.it JA ESTAVA registrado no acervo canonico e MUDOU '
               'de estado: quem confiar na ficha antiga vai achar que a rota funciona.')},
    {'HOST': 'beratungsring.org · enterisi.it',
     'STATE': 'TLS_DH_KEY_TOO_SMALL',
     'MEANS': ('o servidor oferece um grupo Diffie-Hellman abaixo do nivel de seguranca do '
               'cliente. A verificacao TLS NAO foi desligada, e nao sera. Estado do servidor, '
               'nao do conteudo — e o Beratungsring e o servico de aconselhamento da maca do '
               'Alto Adige, exatamente a cultura de 146 pares de rotulo.')},
    {'HOST': 'assomela.it (www) · ismea.it · terrepadane.it',
     'STATE': 'TLS_HOSTNAME_MISMATCH / ISSUER_DESCONHECIDO',
     'MEANS': 'certificado invalido para o host, ou emissor nao verificavel. Estado da fonte.'},
    {'HOST': ('consorzioagrarionordest.it · oipomodorocentrosud.it · pomodorodinord.it · '
              'melinda.it · unapa.it · betaricerca.it · fieragricolatech.it · rive-expo.it · '
              'italmopa.it · siagr.it · disafa.unito.it · opendata.arpa.piemonte.it'),
     'STATE': 'TUNEL_502 / CONEXAO_REINICIADA',
     'MEANS': ('doze hosts que nao abriram por este egresso. NAO_SEI, nunca RED. Tres deles '
               'doem: a Melinda e o maior consorcio de maca do Trentino, a Beta Ricerca e a '
               'pesquisa da beterraba (239 pares de rotulo) e a OI Pomodoro Centro Sud e a '
               'contraparte pugliese da OI que ja esta registrada.')},
    {'HOST': 'regione.marche.it/Fitosanitario',
     'STATE': 'CAPTCHA_RADWARE',
     'MEANS': 'devolve 200 com 15.108 B, mas o corpo e a pagina de captcha da Radware.'},
    {'HOST': 'connect.efsa.europa.eu/RM/s/publicconsultations',
     'STATE': 'CERTIFICATE_VERIFY_FAILED',
     'MEANS': ('as consultas publicas da EFSA, com data de encerramento, ficaram fora. O '
               'calendario (IT-SRCX-047) abriu; o Connect nao.')},
]

# ── UMA CONTRADICAO QUE EU NAO RESOLVI ─────────────────────────────────────────
# Duas fontes de autoridade discordam. Escolher uma em silencio seria inventar.

CONTRADICOES_ABERTAS = [
    {'ID': 'IT-CONTRA-001',
     'SUBJECT': 'resistencia a propanil (HRAC 5 / C2) em Echinochloa crus-galli na Italia',
     'FONTE_A': ('GIRE (IT-SRCX-040) declara populacoes resistentes a propanil em Piemonte, '
                 'Lombardia e Toscana desde 2000.'),
     'FONTE_B': ('a base de Heap (IT-SRCX-051) mostra a Italia com ZERO casos sob HRAC 5, '
                 'conferido por mim: linha 36, Italy, coluna "5" = 0.'),
     'O_QUE_ISSO_NAO_E': ('nao e erro de leitura de nenhum dos dois lados: os dois numeros foram '
                          'lidos direto da fonte. E divergencia de CRITERIO DE ADMISSAO entre '
                          'dois registros — o que cada um conta como "caso documentado".'),
     'ESTADO': 'ABERTA. Nao resolvida, nao arbitrada, e nao escondida.',
     'POR_QUE_IMPORTA': ('se alguem publicar "a Italia tem 29 casos de resistencia" tratando a '
                         'tabela de Heap como censo, estara omitindo o propanil que o GIRE '
                         'certifica. Duas contagens, dois donos, dois criterios.')},
]

# ── CORRECOES DESTA MISSAO ─────────────────────────────────────────────────────
# Uma medicao errada que ficou escrita e pior que uma medicao que faltou: ela fecha a
# porta e ninguem volta a tentar. Estas sao as minhas.

CORRECOES_DESTA_MISSAO = [
    {'ID': 'FIX-01',
     'WHAT_I_WROTE': ('que a rota de Instagram do Sintonia Scrap "precisa do navegador" e que, '
                      'sem Chrome, esta sessao nao coletaria Instagram — e que o entregavel '
                      'seria apenas o lote congelado, para rodar depois no runner.'),
     'WHY_I_WROTE_IT': ('medi GET /p/<shortcode>/embed/captioned/ com User-Agent de Chrome '
                        'desktop, recebi HTTP 200 com 625 KB e ZERO ocorrencias de contextJSON, '
                        'e concluí que o bloco so existe depois que o JavaScript roda.'),
     'WHAT_IS_TRUE': ('o User-Agent era a fechadura, nao o navegador. MESMA URL, MESMO minuto:\n'
                      '  UA Chrome desktop ........ HTTP 200 · 625.215 B · contextJSON = 0\n'
                      '  UA facebookexternalhit/1.1  HTTP 200 · 262.551 B · contextJSON = 1\n'
                      'Verificado duas vezes: pela varredura paralela e por mim, na mao.'),
     'WHAT_CHANGED_BECAUSE_OF_IT': ('a coleta de Instagram deixou de ser FUTURE e virou feita: '
                                    '17 de 19 contas do lote congelado, 102 objetos, 30 videos '
                                    'com VIDEO_URL, transcritos LOCALMENTE com o mesmo '
                                    'faster-whisper do instagram_transcrever.py. '
                                    'Rota em scripts/instagram_sem_navegador.py.'),
     'THE_LESSON': ('HTTP 200 COM BYTES NAO E CONTEUDO, e "precisa de navegador" e uma '
                    'conclusao cara: ela encerra a investigacao. O certo era esgotar as '
                    'variantes de cabecalho antes de culpar o JavaScript.'),
     'WHAT_STAYS_TRUE': ('a PAGINA de perfil (nao o embed) continua devolvendo 302 para login '
                         'sob UA de navegador, e o Chrome continua sem atravessar o proxy desta '
                         'sessao. As duas medicoes estavam certas; a conclusao que tirei delas e '
                         'que estava errada.')},

    {'ID': 'FIX-02',
     'WHAT_I_WROTE': ('na ficha IT-SRCX-035 (CSO Italy), que o handle de LinkedIn do CSO estava '
                      'declarado, com prova "wf_social-technical-voices.json - HTTP 200".'),
     'WHY_I_WROTE_IT': ('porque aceitei o relato de um agente da varredura como leitura. O '
                        'campo EVIDENCE_PROBE apontava para o ARQUIVO DE UM AGENTE, e nao para '
                        'uma medicao minha — e eu nao fiz essa distincao na hora de gravar.'),
     'WHAT_IS_TRUE': ('csoservizi.com devolve, para mim, 200 com 50.746 B e NENHUM link para '
                      'linkedin, instagram, youtube ou facebook. A varredura relatou 331.929 B '
                      'para a mesma pagina. Nao reproduzo nem o tamanho nem o bloco social.'),
     'WHAT_CHANGED_BECAUSE_OF_IT': ('o handle continua na ficha, porque pode existir, mas agora '
                                    'carrega HANDLE_NAO_RECONFIRMADO e NAO entra no lote de '
                                    'coleta social. A LEI 6 nao foi satisfeita.'),
     'THE_LESSON': ('PROVA DE AGENTE NAO E PROVA. Das 93 fontes que a varredura trouxe, eu '
                    'reconferi 52 na mao e duas nao sustentaram: esta e a ANICAV. A taxa '
                    'importa menos que o habito — o que entra no acervo permanente precisa '
                    'ter sido lido por quem assina.'),
     'WHAT_STAYS_TRUE': ('o CSO Italy continua fonte valida por outra razao: previsao de '
                         'producao de pomacee, que e denominador de cultura. O que caiu foi o '
                         'CANAL social, e nao a organizacao.')},

    {'ID': 'FIX-03',
     'WHAT_I_WROTE': ('na ficha IT-SRCX-080, que o podcast "Minuti di Riso" da BASF era um canal '
                      'PERIODIC, a monitorar mensalmente.'),
     'WHY_I_WROTE_IT': ('li a PAGINA do projeto no site da BASF, que responde 200 com 195 KB e '
                        'apresenta o podcast no presente. Uma pagina viva nao diz nada sobre a '
                        'cadencia do que ela apresenta.'),
     'WHAT_IS_TRUE': ('o programa esta no Spreaker (show_id 5619070) e o ultimo episodio e de '
                      '2023-12-07, com o titulo "28 - Arrivederci". O canal se despediu ha mais '
                      'de dois anos.'),
     'WHAT_CHANGED_BECAUSE_OF_IT': ('UPDATE_FREQUENCY passou a STATIC e MONITORING a '
                                    'DO_NOT_MONITOR. Os 28 episodios seguem colhiveis como '
                                    'acervo historico sobre Clearfield e Provisia.'),
     'THE_LESSON': ('PAGINA VIVA NAO E CANAL VIVO. A cadencia so se le no relogio de publicacao, '
                    'e o relogio estava a uma chamada de API de distancia. O mesmo erro apanhou '
                    'quatro outros programas nesta mesma varredura — La settimana del riso '
                    '(2025-07-26), Lezioni di Vite (2023), Just Agronomo (2024-12-24) — e todos '
                    'ficaram registrados com a data que os reprova.'),
     'WHAT_STAYS_TRUE': ('a ficha continua valendo como observacao de CONCORRENTE: a BASF fez um '
                         'podcast de arroz em italiano, e isso e um fato sobre a estrategia dela '
                         'mesmo depois de o canal parar.')},

    {'ID': 'FIX-04',
     'WHAT_I_WROTE': ('o regex de NOTTUE no VOCAB_ISSUE_IT era `\\bnottu`, e o de MOSCA_OLEARIA '
                      'era `mosca oleari|bactrocera ole`.'),
     'WHY_I_WROTE_IT': ('escrevi os dois de memoria sobre o italiano escrito, e nao contra fala '
                        'real. `\\bnottu` parecia um prefixo seguro para nottua/nottue.'),
     'WHAT_IS_TRUE': ('`\\bnottu` casa com NOTTURNO e NOTTURNA. Os tres bollettini olivicoli da '
                      'OlivoNews dizem "l\'umidita notturna e in aumento" e "le minime notturne '
                      'di 17-20 gradi", e os tres foram marcados ISSUE=NOTTUE. Noite nao e '
                      'lagarta. E o alvo REAL dos mesmos tres boletins nao era marcado, porque '
                      'em italiano falado diz-se "mosca dell\'olivo", e nao "mosca olearia".'),
     'WHAT_CHANGED_BECAUSE_OF_IT': ('NOTTUE virou `\\bnottua\\b|\\bnottue\\b|\\bnottuid|agrotis|'
                                    'spodoptera|helicoverpa` e MOSCA_OLEARIA ganhou '
                                    '`mosca dell.{0,3}oliv`. Os tres registros foram REMARCADOS '
                                    'sem retranscrever nada: ISSUE saiu de NOTTUE (errado) para '
                                    'MOSCA_OLEARIA (certo).'),
     'THE_LESSON': ('A PALAVRA EXISTE, O SIGNIFICADO NAO — pela terceira vez nesta missao. Antes '
                    'foram LIGA vindo de "obbligatorio", "pomodoro forte" numa degustacao de '
                    'azeite, e "grano saraceno" lido como FRUMENTO. Vocabulario escrito de '
                    'memoria erra; vocabulario testado contra fala real e o unico que vale.'),
     'WHAT_STAYS_TRUE': ('as tres ocorrencias de NOTTUE em IT-CAMPO-SINAIS-VERIFICADOS-V1.json '
                         'NAO sao deste defeito: sao alvos LIDOS do rotulo canonico, e continuam '
                         'certas.')},

    {'ID': 'FIX-05',
     'WHAT_I_WROTE': ('no comentario do VOCAB_MOLECULE_IT, que "a chave e o nome canonico do '
                      'corpus ADAMA Italia (activeIngredients.json, 53 substancias)".'),
     'WHY_I_WROTE_IT': ('porque montei o vocabulario olhando a lista da ADAMA e acrescentei '
                        'moleculas de concorrente pelo caminho, sem voltar para corrigir a frase.'),
     'WHAT_IS_TRUE': ('DEZ das 32 chaves NAO estao entre as 53: ACETAMIPRID, SPINOSAD, '
                      'DELTAMETHRIN, MANCOZEB, PYRACLOSTROBIN, PROPANIL, BENTAZONE, CLOMAZONE, '
                      'CYCLOXYDIM e ETOFENPROX.'),
     'WHAT_CHANGED_BECAUSE_OF_IT': ('o vocabulario NAO encolheu — ser mais largo que o portfolio '
                                    'e o que fez os boletins da OlivoNews entregarem acetamiprid '
                                    'e spinosad, e foi assim que se soube que a ADAMA nao tem '
                                    'chave naquela conversa. O que mudou foi a frase, e entrou '
                                    'MOLECULAS_ADAMA_IT com separar_molecula_por_dono(), que '
                                    'quebra o campo em MOLECULE_ADAMA e MOLECULE_NOT_ADAMA.'),
     'THE_LESSON': ('MOLECULA MARCADA != MOLECULA ADAMA. Um campo MOLECULE cheio parece bom e '
                    'nao diz de quem e — e o campo que parece bom e o que engana.'),
     'WHAT_STAYS_TRUE': ('nenhuma afirmacao publicada por esta missao chamou molecula alheia de '
                         'ADAMA: conferi as dez, uma a uma, e todas aparecem como CITACAO de '
                         'boletim ou dentro de uma frase que diz explicitamente que NAO sao da '
                         'ADAMA. O defeito estava no comentario, e nao no que foi afirmado.')},
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
        'CORRECTIONS_TO_MY_OWN_MEASUREMENTS': len(CORRECOES_DESTA_MISSAO),
        'OPEN_CONTRADICTIONS': len(CONTRADICOES_ABERTAS),
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
        'CORRECTIONS_TO_MY_OWN_MEASUREMENTS': CORRECOES_DESTA_MISSAO,
        'OPEN_CONTRADICTIONS': CONTRADICOES_ABERTAS,
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
