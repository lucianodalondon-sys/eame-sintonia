#!/usr/bin/env python3
"""
FUNDAÇÃO LOCAL FRANCESA — o fechamento, e as cinco condições que ele exige.

    python scripts/adama_fr_fundacao.py            # o veredito
    python scripts/adama_fr_fundacao.py --gravar   # e grava a amostra versionada

O QUE ESTE ARQUIVO DECIDE
---------------------------
Uma coisa só: se a fundação francesa pode ser declarada COMPLETE. E ela só pode
quando as cinco condições abaixo forem verdade ao mesmo tempo:

    E_PHY_EXECUTION              VALID
    CATALOG_ENUMERATION          COMPLETE
    CATALOG_TO_EPHY_CROSSWALK    COMPLETE
    DOCUMENT_TYPING              COMPLETE ou PARTIAL com contagem exata
    RAW_PRESERVATION_GATE_FR     CLOSED

A quarta admite parcial DE PROPÓSITO: há PDF que não se deixa ler, e fingir que
se leu seria pior do que dizer quantos são. Mas "parcial" só vale com número
exato — "alguns" não fecha nada.

    PARTIAL_WITH_EXACT_UNKNOWN_COUNT ≠ PARTIAL

O QUE ESTE ARQUIVO NÃO DECIDE
-------------------------------
Nada sobre comércio. Nenhum estado daqui nasce em resposta de venda:

    CURRENT_AUTHORIZED ≠ AVAILABLE ≠ IN_STOCK ≠ SELLING
                       ≠ COMMERCIAL_PRIORITY ≠ MARKET_SHARE

E nada sobre importação: fechar a fundação local não abre o EAME.
"""
import datetime
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import adama_fr as fr                                            # noqa: E402
import adama_fr_catalogo as cat                                  # noqa: E402
import adama_fr_documentos as doc                                # noqa: E402
import adama_fr_raw as raw                                       # noqa: E402

AMOSTRA = os.path.join(ROOT, 'data', 'samples', 'FR-ADAMA-FUNDACAO-V1.json')
EPHY_MANIFESTO = os.path.join(ROOT, 'data', 'raw', 'FR', 'anses-ephy',
                              'MANIFESTO-EPHY-FR.json')


def _ler(caminho):
    if not os.path.isfile(caminho):
        return None
    with open(caminho, encoding='utf-8') as fh:
        return json.load(fh)


def veredito():
    ephy = _ler(EPHY_MANIFESTO)
    cw = fr.crosswalk()
    dt = doc.medir()
    plano = raw.plano()
    relatorio = _ler(raw.RELATORIO) or {}
    portao = relatorio.get('GATE') or raw.gate(
        RAW_EXPECTED=plano['RAW_EXPECTED'], REMOTE_PRESENT=0, REMOTE_ABSENT=0,
        ORPHANS=0, FAILED=0, CONTENT_HASH_CHECKED=0, SHA_VERIFIED=0,
        HASH_MISMATCH=0)

    condicoes = {
        'E_PHY_EXECUTION': (
            'VALID' if ephy and ephy['POSTCONDITION']['STATE'] == 'OUTPUT_OK'
            else 'INVALID'),
        'CATALOG_ENUMERATION': (
            'COMPLETE' if cw.get('CATALOG_PUBLIC_PRESENTATIONS')
            else 'INCOMPLETE'),
        'CATALOG_TO_EPHY_CROSSWALK': (
            'COMPLETE' if (cw.get('CATALOG_PAGES_WITHOUT_AMM') == 0
                           and cw.get('CATALOG_DISTINCT_AMMS', 0) > 0
                           and cw.get('CATALOG_AMM_NOT_FOUND_IN_EPHY') == 0)
            else 'PARTIAL'),
        'DOCUMENT_TYPING': dt['STATE'],
        'RAW_PRESERVATION_GATE_FR': portao['RAW_PRESERVATION_GATE_FR'],
    }
    faltam = []
    if condicoes['E_PHY_EXECUTION'] != 'VALID':
        faltam.append('E-Phy não foi executado com runtime válido')
    if condicoes['CATALOG_ENUMERATION'] != 'COMPLETE':
        faltam.append('o catálogo não foi enumerado por inteiro')
    if condicoes['CATALOG_TO_EPHY_CROSSWALK'] != 'COMPLETE':
        faltam.append('há ficha sem AMM ou AMM que a autoridade não conhece')
    if condicoes['DOCUMENT_TYPING'] not in ('COMPLETE',
                                            'PARTIAL_WITH_EXACT_UNKNOWN_COUNT'):
        faltam.append('a tipagem de documento não tem contagem exata de desconhecidos')
    if condicoes['RAW_PRESERVATION_GATE_FR'] != 'CLOSED':
        faltam.append('o portão RAW está aberto: %s'
                      % (portao.get('WHY') or '').replace('faltam: ', ''))

    return {
        'FRANCE_LOCAL_FOUNDATION_CAPTURE': 'COMPLETE' if not faltam else 'PARTIAL',
        'EXACT_REASON': faltam or None,
        'CONDITIONS': condicoes,
        'RAW_GATE_DETAIL': portao,
        'DOCUMENT_COVERAGE_LIMITATION': {
            'UNKNOWN_DOCUMENT_TYPE': dt['UNKNOWN_DOCUMENT_TYPE'],
            'OF_DOCUMENTS': dt['DOCUMENTS'],
            'WHY': ('19 PDFs usam fonte com subconjunto sem mapa /ToUnicode e '
                    '2 não têm texto extraível. Decodificar por deslocamento '
                    'seria adivinhar, e texto quase-certo decidindo o TIPO de um '
                    'documento produz rótulo que parece medido e não é'),
        },
    }


def amostra():
    ephy = _ler(EPHY_MANIFESTO)
    plano = raw.plano()
    cw = fr.crosswalk()
    return {
        'source': ('ANSES E-Phy (dados abertos via data.gouv.fr, versao 2026-08-25) '
                   '+ catalogo publico ADAMA France, lido com Chrome com janela'),
        'SOURCE_ID': 'FR-T4-001 + FR-ADAMA-CATALOG',
        'captured_at': datetime.date.today().isoformat(),
        'SOURCE_LOCATION': 'FRANCE / EU',
        'FACT_LOCATION': 'FRANCE',
        'ORIGINAL_LANGUAGE': 'fr',
        'layer': 'NATIONAL PRODUCT AUTHORIZATION',
        'ARTEFATO': 'FR-ADAMA-FUNDACAO-V1',
        'COUNTRY': 'FR',
        'O_QUE_ESTE_ARQUIVO_E': (
            'os numeros medidos da fundacao francesa. Os bytes ficam em data/raw '
            '(nao versionado); aqui ficam as contagens, os hashes e as ressalvas.'),
        'FONTES': {'REGULATORIA': fr.FONTE_REGULATORIA,
                   'CATALOGO': fr.FONTE_CATALOGO},
        'EPHY': {
            'DATASET_LAST_UPDATE': ephy['RESOLVED']['DATASET_LAST_UPDATE'],
            'ZIP_SHA256': ephy['ZIP_SHA256'], 'ZIP_BYTES': ephy['ZIP_BYTES'],
            'RECORD_COUNT': ephy['RECORD_COUNT'],
            'INTERPRETER': ephy['INTERPRETER'],
            'FILES': [{'FILE': f['FILE'], 'ROWS': f['ROWS'], 'SHA256': f['SHA256']}
                      for f in ephy['EXTRACTED']],
        },
        'CENSO_REGULATORIO': fr.censo(),
        'CENSO_CATALOGO': {k: v for k, v in cat.medir().items()
                           if k != 'POSTCONDITION'},
        'CROSSWALK': cw,
        'DOCUMENT_TYPING': doc.medir(),
        'RAW': {k: plano[k] for k in (
            'RAW_EXPECTED', 'LOCAL_FILES', 'DUPLICATE_REFERENCES',
            'DISTINCT_STORAGE_KEYS', 'TOTAL_BYTES', 'LARGEST_ASSET_BYTES',
            'BUCKET_LIMIT_BYTES', 'EXCEEDS_BUCKET_LIMIT')},
        # A prova REMOTA, e é ela que fecha o portão. O plano acima mede o
        # disco; isto mede o que voltou do bucket e bateu byte a byte.
        'RAW_VERIFICACAO_REMOTA': verificacao_remota(),
        'VEREDITO': veredito(),
    }


def verificacao_remota():
    """→ os números do último round-trip, ou o motivo de não haver nenhum."""
    r = _ler(raw.RELATORIO)
    if not r:
        return {'STATE': 'NEVER_RUN',
                'WHY': ('nenhum relatório de envio em disco. Presença remota '
                        'não foi medida nem uma vez')}
    return {k: r.get(k) for k in (
        'RAW_EXPECTED', 'REMOTE_PRESENT', 'REMOTE_ABSENT',
        'CONTENT_HASH_CHECKED', 'SHA_VERIFIED', 'HASH_MISMATCH', 'FAILED',
        'ORPHANS', 'UNKNOWN_MUST_VERIFY', 'KEY_COLLISIONS',
        'BYTES_EXPECTED', 'BYTES_VERIFIED_REMOTELY', 'BY_STATE')}


def main():
    a = amostra()
    a['RAW']['KEY_COLLISIONS'] = len(raw.plano()['KEY_COLLISIONS'])
    if '--gravar' in sys.argv:
        os.makedirs(os.path.dirname(AMOSTRA), exist_ok=True)
        with open(AMOSTRA, 'w', encoding='utf-8') as fh:
            json.dump(a, fh, ensure_ascii=False, indent=1)
        print('gravado:', os.path.relpath(AMOSTRA, ROOT),
              os.path.getsize(AMOSTRA), 'bytes')
    v = a['VEREDITO']
    for k, val in v['CONDITIONS'].items():
        print('%-30s : %s' % (k, val))
    print()
    print('%-30s : %s' % ('FRANCE_LOCAL_FOUNDATION_CAPTURE',
                          v['FRANCE_LOCAL_FOUNDATION_CAPTURE']))
    for r in v['EXACT_REASON'] or []:
        print('   motivo exato:', r)
    return 0


if __name__ == '__main__':
    sys.exit(main())
