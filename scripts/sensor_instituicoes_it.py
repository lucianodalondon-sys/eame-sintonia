#!/usr/bin/env python3
"""
ROTA INSTITUCIONAL — organizações técnicas italianas, com URL VERIFICADA.

    python3 scripts/sensor_instituicoes_it.py verificar
    python3 scripts/sensor_instituicoes_it.py resumo

POR QUE ORGANIZAÇÃO ENTRA NUMA CAMADA DE "SENSOR HUMANO"
---------------------------------------------------------
Porque a missão pede cooperativas, consorzi e serviços técnicos — e porque a Itália
publica boa parte da observação de campo por NOME DE SERVIÇO, não por nome de pessoa.
O bollettino provincial sai assinado pelo serviço; a pessoa que o escreveu não está na
página.

Isso NÃO é licença para colapsar as duas coisas. `ENTITY_KIND` separa `PERSON` de
`ORGANIZATION` em todo registro, e a regra do modelo de identidade continua:

    NAME != HANDLE != PROFILE != PERSON != ORGANIZATION

Uma organização com um bollettino é UM sensor. Se depois a pessoa que o assina aparecer,
ela é OUTRO sensor, com `ORGANIZATION_ID` apontando para esta — e a independência entre
os dois é `SAME_ORGANIZATION`, nunca duas vozes independentes.

O QUE "VERIFICADA" SIGNIFICA AQUI
----------------------------------
A URL foi BUSCADA nesta execução. O que se grava é o que a resposta disse:

    HTTP_STATUS   o código real
    PAGE_TITLE    o <title> que a página devolveu
    ROLE_TERMS    quais termos de papel técnico a página DECLARA no próprio HTML

`FAIL CLOSED`: 200 não é fonte viva (o repositório já mediu 6 rotas com 200 e zero itens),
e 403/000 não é "organização inexistente" — é `FAILED_WITH_REASON` com o código dentro.
Organização que não responde entra no registro com `URL_STATE` falho e **não** é promovida
a Tier A/B.

A LISTA NÃO É UM RANKING
-------------------------
Estas são organizações que a matriz ADAMA torna relevantes por cultura e por região. Não
há score, não há ordem de importância, e nenhuma delas foi escolhida por tamanho.
"""
import json
import os
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.request
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, 'data', 'raw', 'SENSOR-HUMANO-IT')
UA = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
                    '(KHTML, like Gecko) Chrome/126.0 Safari/537.36',
      'Accept-Language': 'it-IT,it;q=0.9'}
PAUSA = 1.0

TERMOS_PAPEL = (
    'servizio fitosanitario', 'fitosanitar', 'difesa integrata', 'produzione integrata',
    'bollettino', 'assistenza tecnica', 'agronom', 'tecnic', 'ricerca', 'sperimentazione',
    'consorzio', 'cooperativa', 'produttori', 'consulenza', 'laboratorio', 'monitoraggio',
    'avversit', 'fitopatolog', 'entomolog', 'viticolt', 'frutticolt', 'olivicolt',
    'cerealicolt', 'campo prova', 'centro di saggio',
)

# (ORG, URL, TIPO_DECLARADO, REGIÃO, CROPS, POR QUE A ADAMA SE IMPORTA)
CANDIDATAS = [
    # --------------------------------------------- serviços fitossanitários regionais
    ('Servizio Fitosanitario Regione Emilia-Romagna',
     'https://agricoltura.regione.emilia-romagna.it/fitosanitario',
     'PLANT_HEALTH_SERVICE', 'EMILIA-ROMAGNA',
     ['WHEAT', 'MAIZE', 'SUGAR_BEET', 'APPLE', 'STONE_FRUIT', 'VINE', 'POTATO'],
     'publica bollettini de produção integrada vinculantes por área — cruzam crop x target x território'),
    ('Servizio Fitosanitario Regione Veneto',
     'https://www.regione.veneto.it/web/fitosanitario',
     'PLANT_HEALTH_SERVICE', 'VENETO',
     ['VINE', 'MAIZE', 'WHEAT', 'APPLE', 'SUGAR_BEET'],
     'Veneto concentra vinha, milho e cereal; flavescência e cimice asiatica são alvos ADAMA'),
    ('Settore Fitosanitario Regione Piemonte',
     'https://www.regione.piemonte.it/web/temi/agricoltura/servizi-fitosanitari-pan',
     'PLANT_HEALTH_SERVICE', 'PIEMONTE', ['VINE', 'RICE', 'MAIZE', 'APPLE'],
     'flavescência dourada é regulada no Piemonte; arroz e milho concentram-se aqui'),
    ('Servizio Fitosanitario Regione Lombardia',
     'https://www.regione.lombardia.it/wps/portal/istituzionale/HP/servizi-e-informazioni/imprese/imprese-agricole/servizio-fitosanitario',
     'PLANT_HEALTH_SERVICE', 'LOMBARDIA', ['MAIZE', 'RICE', 'WHEAT', 'VINE'],
     'maior área de milho e arroz; diabrótica e micotoxina são alvos com ativo ADAMA'),
    ('ERSA — Agenzia regionale sviluppo rurale FVG',
     'https://www.ersa.fvg.it/', 'PLANT_HEALTH_SERVICE', 'FRIULI-VENEZIA GIULIA',
     ['VINE', 'MAIZE', 'APPLE'],
     'serviço fitossanitário regional do FVG; vinha e milho com flavescência e piralide'),
    ('Servizio Fitosanitario Regione Toscana',
     'https://www.regione.toscana.it/-/servizio-fitosanitario-regionale',
     'PLANT_HEALTH_SERVICE', 'TOSCANA', ['VINE', 'OLIVE', 'WHEAT'],
     'olival e vinha toscanos; mosca da azeitona é alvo com ativo ADAMA'),
    ('Osservatorio Fitosanitario Regione Puglia',
     'https://www.osservatoriofitosanitario.regione.puglia.it/',
     'PLANT_HEALTH_SERVICE', 'PUGLIA', ['OLIVE', 'WHEAT', 'TOMATO', 'VINE'],
     'trigo duro, olival e tomate industrial; a maior concentração de trigo duro italiano'),
    ('Servizio Fitosanitario Regione Campania',
     'https://www.agricoltura.regione.campania.it/fitosanitario/fitosanitario.html',
     'PLANT_HEALTH_SERVICE', 'CAMPANIA', ['TOMATO', 'STONE_FRUIT', 'POTATO'],
     'tomate industrial e fruta de caroço; monilia e requeima são alvos ADAMA'),
    ('Servizio Fitosanitario Regione Marche',
     'https://www.regione.marche.it/Regione-Utile/Agricoltura-Sviluppo-Rurale-e-Pesca/Fitosanitario',
     'PLANT_HEALTH_SERVICE', 'MARCHE', ['WHEAT', 'SUGAR_BEET', 'VINE'],
     'cereal e beterraba nas Marche; fusariose de espiga com ativo ADAMA'),
    ('Servizio Fitosanitario Regione Umbria',
     'https://www.regione.umbria.it/agricoltura/servizio-fitosanitario-regionale',
     'PLANT_HEALTH_SERVICE', 'UMBRIA', ['WHEAT', 'OLIVE', 'VINE'],
     'cereal e olival úmbrios; fusariose e mosca da azeitona'),
    ('Servizio Fitosanitario Regione Sicilia',
     'https://www.regione.sicilia.it/istituzioni/regione/strutture-regionali/assessorato-agricoltura-sviluppo-rurale-pesca-mediterranea/dipartimento-agricoltura/servizio-fitosanitario-regionale',
     'PLANT_HEALTH_SERVICE', 'SICILIA', ['WHEAT', 'OLIVE', 'VINE', 'TOMATO'],
     'trigo duro e vinha sicilianos; Lobesia botrana com ativo ADAMA'),
    ('Servizio Fitosanitario Provincia Autonoma di Trento',
     'https://www.fmach.it/CTT', 'PLANT_HEALTH_SERVICE', 'TRENTINO-ALTO ADIGE',
     ['APPLE', 'VINE'],
     'maçã e vinha do Trentino; carpocapsa, ticchiolatura e diradamento (BREVIS) são ADAMA'),
    ('Centro di Sperimentazione Laimburg',
     'https://www.laimburg.it/it', 'RESEARCH_CENTRE', 'TRENTINO-ALTO ADIGE',
     ['APPLE', 'VINE'],
     'centro de experimentação de Alto Adige — a maior área de maçã da Itália'),
    # ---------------------------------------------------------------- pesquisa pública
    ('CREA — Difesa e Certificazione (CREA-DC)',
     'https://www.crea.gov.it/web/difesa-e-certificazione', 'PUBLIC_RESEARCH', 'LAZIO',
     ['MULTI'], 'centro nacional de defesa das culturas; produz a ciência que antecede o campo'),
    ('CREA — Viticoltura ed Enologia (CREA-VE)',
     'https://www.crea.gov.it/web/viticoltura-e-enologia', 'PUBLIC_RESEARCH', 'VENETO',
     ['VINE'], 'centro nacional de viticultura, sede em Conegliano — peronospora e flavescência'),
    ('CREA — Cerealicoltura e Colture Industriali (CREA-CI)',
     'https://www.crea.gov.it/web/cerealicoltura-e-colture-industriali',
     'PUBLIC_RESEARCH', 'EMILIA-ROMAGNA', ['WHEAT', 'MAIZE'],
     'centro nacional de cereais — septoriose, fusariose e micotoxina'),
    ('CREA — Olivicoltura, Frutticoltura e Agrumicoltura (CREA-OFA)',
     'https://www.crea.gov.it/web/olivicoltura-frutticoltura-e-agrumicoltura',
     'PUBLIC_RESEARCH', 'CALABRIA', ['OLIVE', 'APPLE', 'STONE_FRUIT'],
     'centro nacional de olivicultura e fruticultura'),
    ('CNR — Istituto per la Protezione Sostenibile delle Piante (IPSP)',
     'https://www.ipsp.cnr.it/', 'PUBLIC_RESEARCH', 'PIEMONTE', ['VINE', 'APPLE', 'MULTI'],
     'instituto do CNR de proteção de plantas; flavescência dourada é linha declarada'),
    ('CNR — Istituto di Scienze delle Produzioni Alimentari (ISPA)',
     'https://www.ispa.cnr.it/', 'PUBLIC_RESEARCH', 'PUGLIA', ['WHEAT', 'MAIZE'],
     'referência italiana em micotoxinas de cereal — Fusarium e aflatoxina'),
    ('Fondazione Edmund Mach — Centro Trasferimento Tecnologico',
     'https://www.fmach.it/', 'RESEARCH_CENTRE', 'TRENTINO-ALTO ADIGE',
     ['APPLE', 'VINE'],
     'pesquisa + transferência tecnológica com técnicos de campo em maçã e vinha'),
    ('Fondazione Agrion',
     'https://www.agrion.it/', 'RESEARCH_CENTRE', 'PIEMONTE',
     ['APPLE', 'STONE_FRUIT', 'VINE'],
     'fundação piemontesa de pesquisa aplicada em fruticultura e viticultura'),
    ('ASTRA Innovazione e Sviluppo',
     'https://www.astrainnovazione.it/', 'TRIAL_CENTRE', 'EMILIA-ROMAGNA',
     ['STONE_FRUIT', 'APPLE', 'WHEAT'],
     'centro de saggio da Romagna — ensaio de campo é onde o produto encontra o alvo'),
    ('CRPV — Centro Ricerche Produzioni Vegetali',
     'https://www.crpv.it/', 'TRIAL_CENTRE', 'EMILIA-ROMAGNA',
     ['STONE_FRUIT', 'APPLE', 'VINE', 'WHEAT'],
     'coordena experimentação vegetal na Emília-Romanha'),
    ('Università Cattolica del Sacro Cuore — Piacenza',
     'https://www.unicatt.it/facolta/scienze-agrarie-alimentari-e-ambientali',
     'UNIVERSITY', 'EMILIA-ROMAGNA', ['WHEAT', 'MAIZE', 'VINE'],
     'epidemiologia e modelos de previsão de doença — a ponte SCIENCE -> FIELD'),
    ('Università di Bologna — DISTAL',
     'https://distal.unibo.it/it', 'UNIVERSITY', 'EMILIA-ROMAGNA',
     ['STONE_FRUIT', 'WHEAT', 'VINE'], 'maior departamento agrário italiano'),
    ('Università di Padova — DAFNAE',
     'https://www.dafnae.unipd.it/', 'UNIVERSITY', 'VENETO', ['VINE', 'MAIZE', 'WHEAT'],
     'agronomia e proteção de culturas do Vêneto'),
    ('Università di Milano — DiSAA',
     'https://www.disaa.unimi.it/', 'UNIVERSITY', 'LOMBARDIA', ['VINE', 'MAIZE', 'RICE'],
     'resistência de Plasmopara viticola é linha declarada aqui'),
    ('Università Politecnica delle Marche — D3A',
     'https://www.d3a.univpm.it/', 'UNIVERSITY', 'MARCHE', ['STONE_FRUIT', 'WHEAT'],
     'patologia pós-colheita e defesa de fruta'),
    # ------------------------------------------------- cooperativas e organizações OP
    ('APOT — Associazione Produttori Ortofrutticoli Trentini',
     'https://www.apot.it/', 'PRODUCER_ORGANIZATION', 'TRENTINO-ALTO ADIGE', ['APPLE'],
     'agrega os produtores de maçã do Trentino; assistência técnica própria'),
    ('Consorzio Melinda',
     'https://www.melinda.it/', 'COOPERATIVE', 'TRENTINO-ALTO ADIGE', ['APPLE'],
     'consórcio de maçã do Val di Non com serviço técnico de campo'),
    ('VOG — Consorzio delle cooperative ortofrutticole dell Alto Adige',
     'https://www.vog.it/', 'COOPERATIVE', 'TRENTINO-ALTO ADIGE', ['APPLE'],
     'maior consórcio de maçã do Alto Adige'),
    ('Apofruit Italia',
     'https://www.apofruit.it/', 'COOPERATIVE', 'EMILIA-ROMAGNA',
     ['STONE_FRUIT', 'APPLE'], 'cooperativa de fruta com técnicos de campo em várias regiões'),
    ('COPROB — Italia Zuccheri',
     'https://www.coprob.com/', 'COOPERATIVE', 'EMILIA-ROMAGNA', ['SUGAR_BEET'],
     'único produtor cooperativo de açúcar da Itália — beterraba é o cultivo do GOLTIX'),
    ('Consorzio Agrario dell Emilia',
     'https://www.consorzioagrarioemilia.it/', 'AGRICULTURAL_CONSORTIUM',
     'EMILIA-ROMAGNA', ['WHEAT', 'MAIZE', 'SUGAR_BEET'],
     'consórcio agrário com assistência técnica e distribuição'),
    ('Terremerse',
     'https://www.terremerse.it/', 'COOPERATIVE', 'EMILIA-ROMAGNA',
     ['WHEAT', 'STONE_FRUIT', 'MAIZE'],
     'cooperativa romanhola com divisão agro e técnicos de campo'),
    ('Agrintesa',
     'https://www.agrintesa.it/', 'COOPERATIVE', 'EMILIA-ROMAGNA',
     ['STONE_FRUIT', 'VINE', 'APPLE'], 'cooperativa de fruta e vinha da Romanha'),
    ('Consorzio Fitosanitario Provinciale di Reggio Emilia',
     'https://www.consorziofitoreggio.it/', 'PHYTOSANITARY_CONSORTIUM', 'EMILIA-ROMAGNA',
     ['VINE', 'STONE_FRUIT'],
     'consórcio provincial — o nível territorial onde a observação de campo acontece'),
    ('Consorzio Fitosanitario Provinciale di Modena',
     'https://www.fitosanitariomodena.it/', 'PHYTOSANITARY_CONSORTIUM', 'EMILIA-ROMAGNA',
     ['VINE', 'STONE_FRUIT'], 'consórcio provincial de Modena'),
    ('Confagricoltura',
     'https://www.confagricoltura.it/', 'FARMER_ASSOCIATION', 'LAZIO', ['MULTI'],
     'associação nacional de produtores com estrutura técnica regional'),
    ('Coldiretti',
     'https://www.coldiretti.it/', 'FARMER_ASSOCIATION', 'LAZIO', ['MULTI'],
     'maior associação de produtores italiana'),
    ('CIA — Agricoltori Italiani',
     'https://www.cia.it/', 'FARMER_ASSOCIATION', 'LAZIO', ['MULTI'],
     'associação nacional de agricultores'),
    # ------------------------------------------------------------------ mídia técnica
    ('AgroNotizie — Image Line',
     'https://agronotizie.imagelinenetwork.com/', 'TECHNICAL_MEDIA', 'EMILIA-ROMAGNA',
     ['MULTI'], 'principal veículo técnico agro italiano; publica difesa e agrofarmaci'),
    ('Terra e Vita — Edagricole',
     'https://terraevita.edagricole.it/', 'TECHNICAL_MEDIA', 'EMILIA-ROMAGNA', ['MULTI'],
     'semanário técnico com cobertura de defesa e mercado'),
    ("L'Informatore Agrario",
     'https://www.informatoreagrario.it/', 'TECHNICAL_MEDIA', 'VENETO', ['MULTI'],
     'referência técnica italiana com ensaios comparados de defesa'),
    ('Rivista di Frutticoltura',
     'https://rivistafrutticoltura.edagricole.it/', 'TECHNICAL_MEDIA', 'EMILIA-ROMAGNA',
     ['APPLE', 'STONE_FRUIT'], 'revista técnica de fruticultura'),
    ('Il Corriere Vinicolo — Unione Italiana Vini',
     'https://www.corrierevinicolo.com/', 'TECHNICAL_MEDIA', 'LOMBARDIA', ['VINE'],
     'veículo técnico do setor vitivinícola'),
    # ------------------------------------------- achadas ao corrigir URL, não planejadas
    ('VI.P — Consorzio Cooperative Ortofrutticole Val Venosta',
     'https://www.vip.coop/it/', 'COOPERATIVE', 'TRENTINO-ALTO ADIGE', ['APPLE'],
     'consórcio de maçã do Val Venosta com serviço técnico próprio'),
    ('AIPO — Associazione Interregionale Produttori Olivicoli',
     'https://www.aipoverona.it/', 'PRODUCER_ORGANIZATION', 'VENETO', ['OLIVE'],
     'organização interregional de olivicultores com assistência técnica'),
    ('granoduro.net — DSS de trigo duro',
     'https://www.granoduro.net/', 'DECISION_SUPPORT_SERVICE', 'EMILIA-ROMAGNA',
     ['WHEAT'],
     'sistema de apoio à decisão em trigo duro: publica pressão de doença e janela de '
     'aplicação por território — exatamente o par crop x target x timing da matriz ADAMA'),
]


def _norm(s):
    s = unicodedata.normalize('NFKD', s or '')
    return ''.join(c for c in s if not unicodedata.combining(c)).lower()


def _fetch(url):
    req = urllib.request.Request(url, headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            return r.getcode(), r.read().decode('utf-8', 'replace'), None
    except urllib.error.HTTPError as e:
        try:
            corpo = e.read().decode('utf-8', 'replace')
        except Exception:                                                # noqa: BLE001
            corpo = ''
        return e.code, corpo, 'HTTP %d' % e.code
    except Exception as e:                                               # noqa: BLE001
        return None, '', type(e).__name__


def verificar():
    os.makedirs(RAW, exist_ok=True)
    saida = []
    for org, url, tipo, reg, crops, porque in CANDIDATAS:
        code, corpo, err = _fetch(url)
        titulo = None
        m = re.search(r'<title[^>]*>(.*?)</title>', corpo or '', re.S | re.I)
        if m:
            titulo = re.sub(r'\s+', ' ', m.group(1)).strip()[:180]
        n = _norm(corpo or '')
        termos = sorted({t for t in TERMOS_PAPEL if _norm(t) in n})
        # 200 NÃO é fonte viva. Uma página que responde e não declara nenhum termo de
        # papel técnico fica DECLARED_ROLE = NOT_DECLARED, não "provavelmente técnica".
        estado = ('VERIFIED' if (code == 200 and corpo) else
                  'FAILED_WITH_REASON')
        saida.append({
            'ORGANIZATION': org, 'INSTITUTION_URL': url,
            'DECLARED_TYPE': tipo, 'REGION': reg, 'CROPS': crops,
            'ADAMA_RELEVANCE_REASON': porque,
            'URL_STATE': estado, 'HTTP_STATUS': code, 'FAILURE_REASON': err,
            'PAGE_TITLE': titulo,
            'PAGE_BYTES': len(corpo or ''),
            'ROLE_TERMS_DECLARED': termos,
            'ROLE_TERMS_COUNT': len(termos),
        })
        print('%-4s %-3d %-56s %s' % (
            code or '---', len(termos), org[:56], (titulo or '')[:44]))
        time.sleep(PAUSA)

    corpo_json = {
        'SOURCE_ID': 'SENSOR-HUMANO-IT/INSTITUTIONS',
        'source': 'páginas institucionais públicas, buscadas nesta execução',
        'SOURCE_LOCATION': 'ITALY', 'FACT_LOCATION': 'ITALY', 'ORIGINAL_LANGUAGE': 'IT',
        'METHOD': 'GET direto; grava HTTP_STATUS, <title> e os termos de papel que a '
                  'própria página declara. 200 não é prova de fonte viva.',
        'CANDIDATES': len(saida),
        'VERIFIED': sum(1 for x in saida if x['URL_STATE'] == 'VERIFIED'),
        'FAILED': sum(1 for x in saida if x['URL_STATE'] != 'VERIFIED'),
        'STATUS_DISTRIBUTION': dict(Counter(str(x['HTTP_STATUS']) for x in saida)),
        'ORGANIZATIONS': saida,
        'CAPTURED_AT': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
    }
    p = os.path.join(RAW, 'institutions-IT.json')
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(corpo_json, f, ensure_ascii=False, indent=1)
    print('\n%d verificadas / %d candidatas -> %s' % (
        corpo_json['VERIFIED'], corpo_json['CANDIDATES'], p))
    return corpo_json


def resumo():
    with open(os.path.join(RAW, 'institutions-IT.json'), encoding='utf-8') as f:
        d = json.load(f)
    print('%d verificadas / %d · status %s' % (
        d['VERIFIED'], d['CANDIDATES'], d['STATUS_DISTRIBUTION']))
    for o in d['ORGANIZATIONS']:
        print('  %-10s %-52s %s' % (o['URL_STATE'][:10], o['ORGANIZATION'][:52],
                                    o['ROLE_TERMS_DECLARED'][:5]))


if __name__ == '__main__':
    {'verificar': verificar,
     'resumo': resumo}[sys.argv[1] if len(sys.argv) > 1 else 'resumo']()
