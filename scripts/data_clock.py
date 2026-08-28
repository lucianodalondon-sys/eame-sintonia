#!/usr/bin/env python3
"""
DATA CLOCK — começa a criar histórico próprio.

Não constrói produto, não automatiza nada complexo. Registra, para cada fonte
estruturada que muda, o que é preciso para que a versão de hoje seja recuperável
amanhã: SOURCE · VERSION_DATE · COLLECTION_DATE · SIZE · SHA-256.

Por que importa: medido na MISSÃO 04, o registro francês E-Phy é **FORWARD-ONLY** —
é um retrato do estado atual, sem série. Cada semana não arquivada é história perdida.
O RAIF, ao contrário, já traz 11 safras e não depende disto.

    python3 scripts/data_clock.py
"""
import hashlib, json, os, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'data', 'samples', 'DATA-CLOCK-manifest.json')

# (SOURCE_ID, caminho, data da versão declarada pela fonte, urgência de arquivar)
WATCH = [
    ('FR-T4-001', 'data/raw/FR-T4-001/produits_utf8.csv', '2026-08-25', 'ALTA — FORWARD-ONLY'),
    ('FR-T4-001', 'data/raw/FR-T4-001/usages_des_produits_autorises_utf8.csv', '2026-08-25', 'ALTA — FORWARD-ONLY'),
    ('FR-T4-001', 'data/raw/FR-T4-001/substance_active_utf8.csv', '2026-08-25', 'ALTA — FORWARD-ONLY'),
    ('IT-T4-001', 'data/raw/IT-T4-001/PROD_FTS_6_20260824.csv', '2026-08-24', 'MÉDIA — traz datas de registro e revogação'),
    ('ES-T4-001', 'data/samples/ES-T4-001/ES-T4-002-autorizaciones-excepcionales.json', '2026-08-24', 'ALTA — só as vigentes, sem histórico'),
    ('ES-T3-001', 'data/raw/ES-T3-001/raif_2/2026_RAIF_Vid_Muestreos.xml', '2026-07-06', 'BAIXA — a fonte já publica 11 safras'),
    ('ES-T3-001', 'data/raw/ES-T3-001/raif_1/2026_RAIF_Olivar_Muestreos.xml', '2026-08-19', 'BAIXA — idem'),
    # As duas linhas abaixo são a exceção declarada a D-003: a versão de que um CHANGE
    # EVENT depende deixa de ser dado bruto e passa a ser a prova do evento. Por isso
    # estão em data/samples/, que é versionado.
    ('ES-T4-004', 'data/samples/ES-T4-004-versoes/dc_web_20250528.pdf', '2025-05-28',
     'ARQUIVADA — versão A dos change events'),
    ('ES-T4-004', 'data/samples/ES-T4-004-versoes/dc_web_20260826.pdf', '2026-08-26',
     'ARQUIVADA — versão B dos change events'),
    ('ES-T4-005', 'data/samples/ES-T4-005/ropf_20260829.json.gz', '2026-08-29',
     'ALTA — versão A do registro. STATUS/HOLDER/COMPOSITION/DATE change só existem a partir da B'),
]


def sha256(path, limit=None):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while True:
            b = f.read(1 << 20)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


if __name__ == '__main__':
    today = datetime.date.today().isoformat()
    rows = []
    for sid, rel, version, urgency in WATCH:
        p = os.path.join(ROOT, rel)
        if not os.path.exists(p):
            rows.append({'SOURCE_ID': sid, 'FILE': rel, 'STATUS': 'AUSENTE'})
            continue
        rows.append({'SOURCE_ID': sid, 'FILE': rel,
                     'VERSION_DATE': version, 'COLLECTION_DATE': today,
                     'SIZE_BYTES': os.path.getsize(p), 'SHA256': sha256(p),
                     'ARCHIVING_URGENCY': urgency})
        print(f"{sid:11s} {version}  {rows[-1]['SHA256'][:16]}…  "
              f"{rows[-1]['SIZE_BYTES']:>10,}  {rel.split('/')[-1]}")
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump({'source': 'DATA CLOCK — manifesto de versões das fontes que mudam',
                   'sources': sorted({r['SOURCE_ID'] for r in rows}),
                   'captured_at': today, 'SOURCE_LOCATION': 'FRANCE / SPAIN / ITALY',
                   'FACT_LOCATION': 'n/a — é metadado de coleta',
                   'ORIGINAL_LANGUAGE': 'FR/ES/IT',
                   'note': 'não versiona o conteúdo: registra identidade e data para que a '
                           'versão de hoje seja verificável depois. data/raw não é versionado (D-003).',
                   'files': rows}, f, ensure_ascii=False, indent=2)
    print(f'\ngravado: {OUT}')
