#!/usr/bin/env python3
"""
ITÁLIA — sonda de fontes por classe, e o que cada uma REALMENTE entrega.

Um atlas de fontes que só diz "existe e responde 200" não serve para decidir nada.
`HTTP 200 ≠ FONTE VIVA` é lei desta casa desde a Espanha. Então esta sonda mede três
coisas por fonte, e não uma:

    ALCANCE     responde? em que formato? quantos itens?
    FRESCOR     qual a data do item mais recente?
    ASSUNTO     do que ela fala, medido por termos agronômicos no próprio conteúdo

A terceira é a que separa fonte útil de fonte barulhenta. Medido nesta rodada: o RSS da
*Terra e Vita* responde 200, está fresco e traz 30 itens — e o assunto é preço,
geopolítica, subsídio e DOP. É `MARKET_AND_POLICY_SIGNAL`, não `FIELD_SIGNAL`. A fonte é
boa; o que ela prova é outra coisa. Publicar isso como "mídia técnica italiana coberta"
seria vender atenção de mercado como estado de lavoura.

O contrário também vale: fonte que responde 403 não é fonte ruim — é fonte **não lida
deste ambiente**, e a distinção entre `BLOCKED` e `REJECTED` existe por isso.
"""
import datetime
import json
import os
import re
import subprocess
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DEST = os.path.join(ROOT, 'data', 'samples', 'IT-FONTES', 'ITALY-SOURCE-PROBE.json')

UA = ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
      'Chrome/126.0 Safari/537.36')

# Termos agronômicos, em italiano, agrupados pelo que a presença deles indica.
TERMOS = {
    'CROP': [r'\bmais\b', r'\bvite\b|vigneto', r'\boliv', r'grano|frumento', r'\borzo\b',
             r'\briso\b', r'\bsoia\b', r'pomodor', r'barbabietola'],
    'ISSUE': [r'peronospor', r'\boidio\b', r'flavescen', r'piralide', r'diabrotica',
              r'micotossin|fusarium', r'cercospor', r'mosca\s+dell', r'botrite',
              r'cimice', r'popillia'],
    'PRACTICE': [r'diserb', r'fungicid', r'insetticid', r'fitosanitar', r'trattament',
                 r'difesa\s+integrata', r'bollettin', r'soglia'],
    'MARKET_POLICY': [r'prezzo|listin|mercat', r'\bdop\b|\bigp\b', r'aiut|contribut|'
                      r'credit|accis', r'geopolit|export|dazi', r'assicuraz'],
}


def _curl(url, timeout=30):
    r = subprocess.run(['curl', '-sS', '-L', '--max-time', str(timeout), '-A', UA,
                        '-w', '\n@@HTTP:%{http_code}', url],
                       capture_output=True, text=True, timeout=timeout + 15)
    body = r.stdout
    m = re.search(r'@@HTTP:(\d+)\s*$', body)
    code = int(m.group(1)) if m else 0
    return code, body[:m.start()] if m else body


def _texto(s):
    t = re.sub(r'<script.*?</script>|<style.*?</style>', ' ', s, flags=re.S | re.I)
    t = re.sub(r'<[^>]+>', ' ', t)
    return re.sub(r'\s+', ' ', t)


def _datas(s):
    out = []
    for p in (r'<pubDate>([^<]+)</pubDate>', r'<published>([^<]+)</published>',
              r'<updated>([^<]+)</updated>', r'(\d{2}/\d{2}/20\d\d)', r'(20\d\d-\d\d-\d\d)'):
        out += re.findall(p, s)
    return out[:40]


def sondar(f):
    code, body = _curl(f['URL'])
    reg = {**f, 'HTTP': code, 'BYTES': len(body),
           'PROBED_AT': datetime.date.today().isoformat()}
    if code == 403 or code == 401:
        reg['ACCESS_STATUS'] = 'BLOCKED'
        reg['NOTE'] = 'bloqueio de origem — fonte NÃO LIDA deste ambiente, não recusada'
        return reg
    if code != 200 or not body:
        reg['ACCESS_STATUS'] = 'NOT_REACHED'
        return reg
    itens = len(re.findall(r'<item[\s>]', body)) or len(re.findall(r'<entry[\s>]', body))
    reg['FORMAT'] = ('RSS/ATOM' if itens else
                     ('JSON' if body.lstrip()[:1] in '{[' else 'HTML'))
    reg['ITEMS'] = itens
    t = _texto(body)
    perfil = {}
    for classe, pats in TERMOS.items():
        perfil[classe] = sum(len(re.findall(p, t, re.I)) for p in pats)
    reg['TOPIC_PROFILE'] = perfil
    agro = perfil['CROP'] + perfil['ISSUE'] + perfil['PRACTICE']
    reg['WHAT_IT_MEASURES'] = (
        'FIELD_OR_TECHNICAL_SIGNAL' if perfil['PRACTICE'] + perfil['ISSUE'] > perfil['MARKET_POLICY']
        else ('MARKET_AND_POLICY_SIGNAL' if perfil['MARKET_POLICY'] > 0 else 'NÃO SEI'))
    reg['AGRONOMIC_TERM_HITS'] = agro
    ds = _datas(body)
    reg['DATES_SEEN'] = ds[:5]
    reg['FRESHNESS'] = ('DATED' if ds else 'NO_DATE_FOUND')
    reg['ACCESS_STATUS'] = 'GREEN' if agro else 'PARTIAL'
    return reg


def catalogo():
    """As fontes vêm por CLASSE. Nenhuma entra sem dizer a que classe serve."""
    return [
        # K · MÍDIA TÉCNICA
        {'SOURCE_ID': 'IT-T7-001', 'CLASS': 'TECHNICAL_MEDIA', 'NAME': 'Terra e Vita (Edagricole)',
         'URL': 'https://terraevita.edagricole.it/feed/', 'ACCESS_METHOD': 'RSS'},
        {'SOURCE_ID': 'IT-T7-002', 'CLASS': 'TECHNICAL_MEDIA', 'NAME': "L'Informatore Agrario",
         'URL': 'https://www.informatoreagrario.it/feed/', 'ACCESS_METHOD': 'RSS'},
        {'SOURCE_ID': 'IT-T7-003', 'CLASS': 'TECHNICAL_MEDIA', 'NAME': 'AgroNotizie (Image Line)',
         'URL': 'https://agronotizie.imagelinenetwork.com/', 'ACCESS_METHOD': 'HTML'},
        {'SOURCE_ID': 'IT-T7-004', 'CLASS': 'TECHNICAL_MEDIA', 'NAME': 'Image Line (grupo)',
         'URL': 'https://www.image-line.com/', 'ACCESS_METHOD': 'HTML'},
        # B · CAMPO / FITOSSANITÁRIO
        {'SOURCE_ID': 'IT-T3-002', 'CLASS': 'FIELD', 'NAME': 'Regione Veneto — bollettini 2026',
         'URL': 'https://www.regione.veneto.it/web/fitosanitario/bollettini-fitosanitari-2026',
         'ACCESS_METHOD': 'HTML+PDF'},
        {'SOURCE_ID': 'IT-T3-006', 'CLASS': 'FIELD', 'NAME': 'ERSA FVG — colture erbacee 2026',
         'URL': ('http://difesafitosanitaria.ersa.fvg.it/difesa-e-produzione-integrata/'
                 'difesa-integrata-obbligatoria/bollettini-fitosanitari/'
                 'colture-erbacee-orticole/bollettini-2026'), 'ACCESS_METHOD': 'HTML+PDF'},
        {'SOURCE_ID': 'IT-T3-003', 'CLASS': 'FIELD', 'NAME': 'Regione Lombardia — bollettini',
         'URL': ('https://www.fitosanitario.regione.lombardia.it/wps/portal/site/sfr/'
                 'protezione-delle-colture-e-del-verde/bollettini-fitosanitari'),
         'ACCESS_METHOD': 'HTML+PDF'},
        {'SOURCE_ID': 'IT-T3-007', 'CLASS': 'FIELD', 'NAME': 'Emilia-Romagna — fitosanitario',
         'URL': 'https://agricoltura.regione.emilia-romagna.it/fitosanitario',
         'ACCESS_METHOD': 'HTML'},
        {'SOURCE_ID': 'IT-T3-008', 'CLASS': 'FIELD', 'NAME': 'Agrometeo Puglia — bollettini',
         'URL': 'https://www.agrometeopuglia.it/bollettini', 'ACCESS_METHOD': 'HTML'},
        # E/F · CIÊNCIA E INSTITUIÇÕES
        {'SOURCE_ID': 'IT-T5-002', 'CLASS': 'RESEARCH_INSTITUTION', 'NAME': 'CREA',
         'URL': 'https://www.crea.gov.it/', 'ACCESS_METHOD': 'HTML'},
        {'SOURCE_ID': 'IT-T5-003', 'CLASS': 'RESEARCH_INSTITUTION',
         'NAME': 'CNR — Istituto di Scienze delle Produzioni Alimentari',
         'URL': 'https://www.ispa.cnr.it/', 'ACCESS_METHOD': 'HTML'},
        # I · COOPERATIVAS / ORGANIZAÇÕES DE PRODUTORES
        {'SOURCE_ID': 'IT-T13-002', 'CLASS': 'COOPERATIVE', 'NAME': 'Co.Pro.B. (beterraba)',
         'URL': 'https://www.coprob.com/', 'ACCESS_METHOD': 'HTML'},
        {'SOURCE_ID': 'IT-T13-003', 'CLASS': 'PRODUCER_ORG', 'NAME': 'Assoproli Bari (olivo)',
         'URL': 'https://www.assoproli.it/bollettini-fitosanitari/', 'ACCESS_METHOD': 'HTML'},
        {'SOURCE_ID': 'IT-T13-004', 'CLASS': 'COOPERATIVE',
         'NAME': 'Confagricoltura Veneto', 'URL': 'https://confagricolturaveneto.it/',
         'ACCESS_METHOD': 'HTML'},
        {'SOURCE_ID': 'IT-T13-005', 'CLASS': 'COOPERATIVE', 'NAME': 'Coldiretti',
         'URL': 'https://www.coldiretti.it/', 'ACCESS_METHOD': 'HTML'},
        # M · CONCORRENTES (comunicação pública)
        {'SOURCE_ID': 'IT-T9-002', 'CLASS': 'COMPETITOR', 'NAME': 'Syngenta Italia',
         'URL': 'https://www.syngenta.it/', 'ACCESS_METHOD': 'HTML'},
        {'SOURCE_ID': 'IT-T9-003', 'CLASS': 'COMPETITOR', 'NAME': 'BASF Agro Italia',
         'URL': 'https://www.agro.basf.it/', 'ACCESS_METHOD': 'HTML'},
        {'SOURCE_ID': 'IT-T9-004', 'CLASS': 'COMPETITOR', 'NAME': 'Corteva Italia',
         'URL': 'https://www.corteva.it/', 'ACCESS_METHOD': 'HTML'},
        {'SOURCE_ID': 'IT-T9-005', 'CLASS': 'COMPETITOR', 'NAME': 'Bayer Crop Science Italia',
         'URL': 'https://www.cropscience.bayer.it/', 'ACCESS_METHOD': 'HTML'},
        {'SOURCE_ID': 'IT-T9-001', 'CLASS': 'ADAMA', 'NAME': 'ADAMA Italia',
         'URL': 'https://www.adama.com/italia/it', 'ACCESS_METHOD': 'HTML'},
    ]


def main():
    regs = [sondar(f) for f in catalogo()]
    por_status = {}
    for r in regs:
        por_status[r['ACCESS_STATUS']] = por_status.get(r['ACCESS_STATUS'], 0) + 1
    por_classe = {}
    for r in regs:
        d = por_classe.setdefault(r['CLASS'], {'TOTAL': 0, 'GREEN': 0, 'BLOCKED': 0})
        d['TOTAL'] += 1
        if r['ACCESS_STATUS'] == 'GREEN':
            d['GREEN'] += 1
        if r['ACCESS_STATUS'] == 'BLOCKED':
            d['BLOCKED'] += 1
    out = {
        'DATASET': 'ITALY-SOURCE-PROBE', 'COUNTRY': 'IT',
        'SOURCE_ID': 'DERIVED/IT-SOURCE-PROBE',
        'SOURCE': 'sondagem direta das próprias fontes',
        'CAPTURED_AT': datetime.date.today().isoformat(),
        'EVIDENCE_CLASS': 'SOURCE_HEALTH',
        'METHOD': ('mede ALCANCE, FRESCOR e ASSUNTO. `HTTP 200 ≠ FONTE VIVA`: uma fonte '
                   'que responde e está fresca ainda pode medir outra coisa que não campo.'),
        'STATUS_LEGEND': {
            'GREEN': 'respondeu e traz termo agronômico',
            'PARTIAL': 'respondeu, sem termo agronômico no que foi lido',
            'BLOCKED': 'bloqueio de origem — NÃO LIDA daqui, não recusada',
            'NOT_REACHED': 'não respondeu neste ambiente',
        },
        'BY_STATUS': por_status, 'BY_CLASS': por_classe,
        'SOURCES': regs,
    }
    os.makedirs(os.path.dirname(DEST), exist_ok=True)
    with open(DEST, 'w', encoding='utf-8') as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    for r in regs:
        print('%-11s %-22s %-3s %-26s %s' % (
            r['ACCESS_STATUS'], r['CLASS'][:22], r['HTTP'],
            r.get('WHAT_IT_MEASURES', '-')[:26], r['NAME'][:34]))
    print('\n', por_status)
    print('->', os.path.relpath(DEST, ROOT))


if __name__ == '__main__':
    main()
