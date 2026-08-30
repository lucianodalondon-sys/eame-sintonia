#!/usr/bin/env python3
"""
CONFIRMAÇÃO REGULATÓRIA DOS PARES — seção 16 da missão.

A ADAMA diz "produto X, cultivo Y, problema Z" na página dela. Isso é CLAIM DO
FABRICANTE. O MAPA diz quem tem registro para o par cultivo × problema. Isso é FATO
REGULATÓRIO. Este arquivo pergunta ao MAPA, par por par, e carimba qual dos dois é.

    python3 scripts/adama_es_confirmacao_mapa.py --build

Uma requisição por par. Não há varredura: só se pergunta o par que a ADAMA declarou.

O QUE ESTE ARQUIVO NÃO FAZ

Não apaga divergência. Se a ADAMA declara e o MAPA não confirma, isso vira
ADAMA_CLAIM_MAPA_NOT_CONFIRMED e FICA — pode ser registro sob outro nome comercial,
alvo declarado por outra via, ou claim que o registro não sustenta. Nomear qual dos
três seria inferir.

Também não casa por nome. O casamento é pelo NÚMERO DE REGISTRO da ficha da ADAMA
contra o NumRegistro do MAPA. Sem número, o par sai AMBIGUOUS, nunca "não confirmado".
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SAMPLES = os.path.join(ROOT, 'data', 'samples')
sys.path.insert(0, HERE)
import adama_es as A          # noqa: E402
import mapa_regfi as M        # noqa: E402

ARTEFATO = os.path.join(SAMPLES, 'ADAMA-ES-PRODUCT-INTELLIGENCE.json')
IDS = os.path.join(SAMPLES, 'ES-MAPA-VOCABULARIO-IDS.json')


def _normaliza_registro(s):
    """"ES-01209" e "01209" e "ES-1209" viram a mesma chave. Só tira notação."""
    s = re.sub(r'[^0-9]', '', str(s or ''))
    return s.lstrip('0') or ''


def confirmar(par, ids, cache):
    """Um par -> um veredito, com a evidência que o produziu."""
    kc, ki = A._chave(par['CROP']), A._chave(par['ISSUE'])
    crop, issue = ids['CROPS'].get(kc), ids['ISSUES'].get(ki)
    base = {
        'PRODUCT_ID': par['PRODUCT_ID'],
        'CROP': par['CROP'], 'ISSUE': par['ISSUE'],
        'REGISTRATION_ID_NA_FICHA': par.get('REGISTRATION_ID', 'NÃO SEI'),
        'SOURCE_URL': par['SOURCE_URL'],
        'ANCHOR': par.get('ANCHOR'),
        'ADAMA_CLAIM': 'MANUFACTURER_TECHNICAL_CLAIM',
    }
    if not crop or not issue:
        return dict(base, ESTADO='AMBIGUOUS',
                    PORQUE=('cultivo ou problema sem id oficial no vocabulario do MAPA; '
                            'perguntar sem id seria perguntar outra coisa'),
                    MAPA_ID_CULTIVO=(crop or {}).get('ID', 'NÃO SEI'),
                    MAPA_ID_PLAGA=(issue or {}).get('ID', 'NÃO SEI'))

    chave = (crop['ID'], issue['ID'])
    if chave not in cache:
        linhas, ts = M.export(idCultivo=crop['ID'], idPlaga=issue['ID'])
        cache[chave] = {'LINHAS': linhas, 'SERVIDOR': ts}
    r = cache[chave]

    reg = _normaliza_registro(par.get('REGISTRATION_ID'))
    titulares = sorted({(l.get('Titular') or '').strip() for l in r['LINHAS']})
    encontrado = None
    if reg:
        for l in r['LINHAS']:
            if _normaliza_registro(l.get('NumRegistro')) == reg:
                encontrado = l
                break

    comum = dict(base,
                 MAPA_ID_CULTIVO=crop['ID'], MAPA_ID_PLAGA=issue['ID'],
                 MAPA_LABEL_CULTIVO=crop['LABEL'], MAPA_LABEL_PLAGA=issue['LABEL'],
                 MAPA_REGISTROS_NO_PAR=len(r['LINHAS']),
                 MAPA_TITULARES_NO_PAR=[t for t in titulares if t][:12],
                 MAPA_SERVIDOR_TIMESTAMP=r['SERVIDOR'],
                 ROTA='POST /regfiweb/Exportaciones/ExportJsonProductos'
                      ' dataDto[idCultivo]+dataDto[idPlaga]')

    if not reg:
        return dict(comum, ESTADO='AMBIGUOUS',
                    PORQUE=('a ficha da ADAMA nao publica numero de registro; casar por '
                            'nome comercial seria fuzzy-match silencioso (secao 15)'))
    if encontrado:
        return dict(comum, ESTADO='ADAMA_CLAIM_MAPA_CONFIRMED',
                    EVIDENCE_LEVEL='REGULATORY_FACT',
                    MAPA_NOME=encontrado.get('Nombre'),
                    MAPA_TITULAR=encontrado.get('Titular'),
                    MAPA_ESTADO=encontrado.get('Estado'),
                    MAPA_FORMULADO=encontrado.get('Formulado'),
                    PORQUE='o numero de registro da ficha esta na lista oficial do par')
    return dict(comum, ESTADO='ADAMA_CLAIM_MAPA_NOT_CONFIRMED',
                EVIDENCE_LEVEL='MANUFACTURER_TECHNICAL_CLAIM',
                PORQUE=('o numero de registro da ficha NAO esta entre os %d registros que '
                        'o MAPA lista para este par' % len(r['LINHAS'])),
                O_QUE_ISTO_NAO_PROVA=(
                    'nao prova que o uso e irregular. Pode ser registro sob outro nome '
                    'comercial, alvo declarado por outra via, ou claim que o registro nao '
                    'sustenta — nomear qual dos tres seria inferir'))


def construir():
    with open(ARTEFATO, encoding='utf-8') as f:
        art = json.load(f)
    with open(IDS, encoding='utf-8') as f:
        ids = json.load(f)
    regs = {p['PRODUCT_ID']: p.get('REGISTRATION_ID')
            for p in art['PRODUCTS'] if p.get('PRODUCT_ID')}

    cache, linhas = {}, []
    for par in art['CROP_ISSUE_RELATIONS']:
        p = dict(par, REGISTRATION_ID=regs.get(par['PRODUCT_ID'], 'NÃO SEI'))
        try:
            linhas.append(confirmar(p, ids, cache))
        except Exception as e:                                   # noqa: BLE001
            linhas.append({'PRODUCT_ID': par['PRODUCT_ID'], 'CROP': par['CROP'],
                           'ISSUE': par['ISSUE'], 'ESTADO': 'NOT_TESTED',
                           'PORQUE': 'a consulta ao MAPA falhou: %s %s'
                                     % (type(e).__name__, str(e)[:160]),
                           'O_QUE_ISTO_NAO_E': 'falha de consulta nao e nao-confirmacao'})

    contagem = {}
    for l in linhas:
        contagem[l['ESTADO']] = contagem.get(l['ESTADO'], 0) + 1

    return {
        'SOURCE_ID': 'ADAMA-ES-CONFIRMACAO-REGULATORIA-DO-PAR',
        'source': 'MAPA ROPF — filtro combinado idCultivo + idPlaga',
        'SOURCE_LOCATION': 'SPAIN', 'FACT_LOCATION': 'SPAIN', 'ORIGINAL_LANGUAGE': 'ES',
        'captured_at': art.get('captured_at'), 'CAPTURE_DATE': art.get('captured_at'),
        'COUNTRY': 'ES', 'ESTADO_DO_REGISTRO': 'CURRENT',
        'DERIVADO_DE': 'data/samples/ADAMA-ES-PRODUCT-INTELLIGENCE.json',
        'PARES_TESTADOS': len(linhas),
        'CONSULTAS_AO_MAPA': len(cache),
        'CONTAGEM_POR_ESTADO': contagem,
        'LEI': ('ADAMA_CLAIM != REGULATORY_FACT. Confirmado significa que o numero de '
                'registro da ficha esta na lista oficial do par. Nao confirmado NAO '
                'significa irregular.'),
        'PORQUE_SAO_POUCOS_PARES': (
            'a ADAMA Espanha quase nao publica tabela cultivo x problema em HTML: das 56 '
            'fichas, 14 tem tabela e o formato dominante e CULTIVO x DOSE, sem coluna de '
            'agente. So se pergunta ao MAPA o par que a ADAMA declarou; derivar par de '
            'lista solta seria cartesiano (secao 8).'),
        'LINHAS': linhas,
    }


if __name__ == '__main__':
    d = construir()
    if '--build' in sys.argv:
        caminho = os.path.join(SAMPLES, 'ADAMA-ES-CONFIRMACAO-REGULATORIA-DO-PAR.json')
        with open(caminho, 'w', encoding='utf-8') as f:
            json.dump(d, f, ensure_ascii=False, indent=1)
        print('%s  %d pares  %s' % (os.path.basename(caminho), d['PARES_TESTADOS'],
                                    d['CONTAGEM_POR_ESTADO']))
    else:
        print(json.dumps(d, ensure_ascii=False, indent=1))
