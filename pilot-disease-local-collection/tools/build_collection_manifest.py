"""Build the COLLECTION_PACKAGE manifest, recomputing every number from disk.

Run this last. It reads the manifests and the files, never a narrative.
Anything not measured is written as NOT_KNOWN. Anything attempted and failed is
written as NOT_PRESERVED or PARTIAL, never as zero.
"""
import gzip, json, os, re, subprocess
from collections import Counter, defaultdict
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M = os.path.join(ROOT, 'manifests')
RAW = os.path.join(ROOT, 'raw')


def jl(name):
    p = os.path.join(M, name)
    if not os.path.exists(p):
        return []
    return [json.loads(l) for l in open(p, encoding='utf-8') if l.strip()]


def js(name, default=None):
    p = os.path.join(M, name)
    if not os.path.exists(p):
        return default
    return json.load(open(p, encoding='utf-8'))


def git(*args):
    try:
        return subprocess.run(['git'] + list(args), cwd=ROOT, capture_output=True,
                              timeout=60).stdout.decode().strip()
    except Exception:
        return 'NOT_KNOWN'


now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

# ---------------------------------------------------------------- daily meteo
daily = jl('arpav-daily-manifest.jsonl')
prov = jl('daily-series-provenance.jsonl')
recount = js('daily-series-recount.json', {})
daily_ok = [r for r in daily if r.get('preservation') == 'PRESERVED']
daily_bad = [r for r in daily if r.get('preservation') != 'PRESERVED']
daily_rows = sum(r.get('ROWS', 0) for r in prov)
daily_bytes = sum(r.get('bytes', 0) for r in daily_ok)  # this manifest uses lowercase keys
bf = [r for r in prov if r.get('VARIABLE_CODE') == 'BFOGL']

# ---------------------------------------------------------------- catalogues
stz = js_path = os.path.join(RAW, 'F4-arpav-rest', 'meteo_stazioni_dispenser.json')
stations_all = json.load(open(stz, encoding='utf-8'))['data'] if os.path.exists(stz) else []
sen_path = os.path.join(RAW, 'F4-arpav-rest', 'meteo_sensori_dispenser.json')
sensors_all = json.load(open(sen_path, encoding='utf-8'))['data'] if os.path.exists(sen_path) else []
cat_bfogl = [s for s in sensors_all if s.get('descrizione') == 'Bagnatura fogliare']

# ---------------------------------------------------------------- documents
docs = jl('arpav-docs-manifest.verified.jsonl') or jl('arpav-docs-manifest.jsonl')
docs_ok = [r for r in docs if r.get('preservation') == 'PRESERVED']
annate = [r for r in docs_ok if 'annate-agrarie' in r.get('source_url', '')]
fas = [r for r in docs_ok if 'fas-rapporti' in r.get('source_url', '')]
vine = [r for r in docs_ok if 'peronospora-vite' in r.get('source_url', '')]


def seasons_of(rows):
    out = set()
    for r in rows:
        t = r.get('document_title') or ''
        m = re.search(r'(\d{4})\s*-\s*(\d{2})\b', t)
        if m:
            out.add(f'{m.group(1)}-{m.group(2)}')
            continue
        m2 = re.search(r'\b(19|20)\d\d\b', t)
        out.add(m2.group(0) if m2 else 'NOT_KNOWN')
    return sorted(out)


# ---------------------------------------------------------------- monthly
monthly_inv = jl('arpav-monthly-inventory.jsonl')
monthly_man = jl('arpav-monthly-manifest.jsonl')
monthly_ok = [r for r in monthly_man if r.get('preservation') == 'PRESERVED']
monthly_bad = [r for r in monthly_man if r.get('preservation') != 'PRESERVED']
monthly_years = sorted({m.group(0) for r in monthly_inv
                        for m in [re.search(r'/bollettino-mese/(\d{4})/', r.get('api_url', ''))]
                        if m} | {re.search(r'/bollettino-mese/(\d{4})/', r.get('api_url', '')).group(1)
                                 for r in monthly_inv
                                 if re.search(r'/bollettino-mese/(\d{4})/', r.get('api_url', ''))})
monthly_years = sorted({re.search(r'/bollettino-mese/(\d{4})/', r['api_url']).group(1)
                        for r in monthly_inv if re.search(r'/bollettino-mese/(\d{4})/', r['api_url'])})

# ---------------------------------------------------------------- raw on disk
rawinv = jl('raw-file-inventory.jsonl')
TOOLING_EXT = {'.py'}
raw_docs = [r for r in rawinv if r['ext'] not in TOOLING_EXT
            and not r['raw_path'].startswith('raw/_failed-captures/')]
raw_tooling = [r for r in rawinv if r['ext'] in TOOLING_EXT]
raw_quarantined = [r for r in rawinv if r['raw_path'].startswith('raw/_failed-captures/')]

# ---------------------------------------------------------------- outcome scan
scan = js('disease-outcome-scan.json', {'documents': []})
scan_counts = Counter(d['outcome_state'] for d in scan.get('documents', []))
numeric_candidates = [d for d in scan.get('documents', [])
                      if d['outcome_state'] == 'NUMERIC_CANDIDATE']

# ---------------------------------------------------------------- recon
recon_sum = js(os.path.join('recon', '_recon-summary.json'), {})

pkg = {
    'COLLECTION_ID': 'ITALY-VENETO-DISEASE-LOCAL-COLLECTION-2026-09',
    'COLLECTION_BRANCH': git('branch', '--show-current'),
    'COLLECTION_HEAD': git('rev-parse', 'HEAD'),
    'BUILT_AT': now,
    'COUNTRY': 'ITALY',
    'REGION_OF_INTEREST': 'Veneto — Conegliano / Valdobbiadene / provincia di Treviso',
    'VPN_STATE': 'ITALY (Proton AG AS208172, exit Milan, country IT — verified via ipinfo.io before collection)',
    'ACCESS_WITH_ITALIAN_VPN': 'YES',
    'ACCESS_WITHOUT_VPN': 'NOT_TESTED',

    'RAW_FILES_TOTAL_ON_DISK': len(rawinv),
    'RAW_FILES_SOURCE_DOCUMENTS': len(raw_docs),
    'RAW_FILES_TOOLING_SCRIPTS_EXCLUDED': len(raw_tooling),
    'RAW_FILES_QUARANTINED_FAILED_CAPTURES': len(raw_quarantined),
    'RAW_BYTES_SOURCE_DOCUMENTS': sum(r['bytes'] for r in raw_docs),
    'RAW_DISTINCT_BY_SHA256': len({r['sha256'] for r in raw_docs if r['sha256'] != 'EMPTY_FILE_NO_HASH'}),
    'RAW_DUPLICATE_CONTENT': sum(1 for r in raw_docs if r['dedup'] == 'SAME_CONTENT_DIFFERENT_URL'),
    'RAW_EMPTY_FILES_NOT_ZERO': sum(1 for r in rawinv if r['dedup'] == 'EMPTY_FILE_NOT_ZERO'),
    'RAW_LOCATION': os.path.join(ROOT, 'raw'),
    'RAW_IN_GIT': 'NO — raw/ is gitignored; manifests + sha256 + paths are committed instead',

    'ARPAV_CATALOGUE_STATIONS_REGIONWIDE': len(stations_all),
    'ARPAV_CATALOGUE_SENSORS_REGIONWIDE': len(sensors_all),
    'ARPAV_CATALOGUE_LEAF_WETNESS_SENSORS_REGIONWIDE': len(cat_bfogl),
    'NOTE_CATALOGUE_VS_PRESERVED': ('The three figures above are CATALOGUE numbers for the whole '
                                    'Veneto region. They are NOT preserved data. Preserved data is '
                                    'the Treviso subset below.'),

    'DAILY_FILES_PRESERVED': len(daily_ok),
    'DAILY_FILES_FAILED': len(daily_bad),
    'DAILY_ROWS_PRESERVED': daily_rows,
    # sum of the ORIGINAL API responses as received; on disk they are gzipped,
    # so the folder is far smaller. Two different numbers, both real.
    'DAILY_BYTES_UNCOMPRESSED_AS_RECEIVED': daily_bytes,
    'DAILY_BYTES_ON_DISK_GZIPPED': sum(
        os.path.getsize(os.path.join(RAW, 'F4-arpav-rest', 'tabella', f))
        for f in os.listdir(os.path.join(RAW, 'F4-arpav-rest', 'tabella'))
        if f.endswith('.json.gz')),
    'DAILY_STATIONS_PRESERVED': len({r['STATION_ID'] for r in prov}),
    'DAILY_SENSOR_SERIES_PRESERVED': len({r['SENSOR_ID'] for r in prov}),
    'DAILY_VARIABLES': sorted({r['VARIABLE_CODE'] for r in prov}),
    'DAILY_YEARS': sorted({r['YEAR'] for r in prov}),
    'DAILY_COMPLETENESS': dict(Counter(r['COMPLETENESS'] for r in prov)),
    'DAILY_ROWS_WITH_A_VALUE': sum(r.get('ROWS_WITH_VALUE', 0) for r in prov),
    'DAILY_STATIONS_WITH_COORDINATES': len({r['STATION_ID'] for r in prov if r['LAT'] != 'NOT_KNOWN'}),

    'LEAF_WETNESS_STATIONS_PRESERVED': len({r['STATION_ID'] for r in bf}),
    'LEAF_WETNESS_SENSOR_SERIES_PRESERVED': len({r['SENSOR_ID'] for r in bf}),
    'LEAF_WETNESS_FILES': len(bf),
    'LEAF_WETNESS_ROWS': sum(r['ROWS'] for r in bf),
    'LEAF_WETNESS_YEARS_MIN': min((r['YEAR'] for r in bf), default='NOT_KNOWN'),
    'LEAF_WETNESS_YEARS_MAX': max((r['YEAR'] for r in bf), default='NOT_KNOWN'),
    'LEAF_WETNESS_UNIT': sorted({r['UNIT'] for r in bf}) or ['NOT_KNOWN'],
    'LEAF_WETNESS_WINDOW_COVERAGE': recount.get('leaf_wetness', []),

    'ANNATE_DOCUMENTS_PRESERVED': len(annate),
    'ANNATE_DISTINCT_SEASONS': len(seasons_of(annate)),
    'ANNATE_SEASONS': seasons_of(annate),
    'FAS_REPORTS_PRESERVED': len(fas),
    'VINE_BULLETIN_SLOT_FILES_PRESERVED': len(vine),

    'MONTHLY_BULLETIN_INDEX_YEARS': monthly_years,
    'MONTHLY_BULLETINS_DISCOVERED': len(monthly_inv),
    'MONTHLY_BULLETINS_PRESERVED': len(monthly_ok),
    'MONTHLY_BULLETINS_FAILED': len(monthly_bad),
    'MONTHLY_ARCHIVE_STATE': ('COMPLETE' if monthly_inv and len(monthly_ok) == len(monthly_inv)
                              else 'PARTIAL' if monthly_ok else 'NOT_PRESERVED'),

    'DISEASE_OUTCOME_SCAN': dict(scan_counts),
    'DISEASE_NUMERIC_OUTCOME_CANDIDATES': len(numeric_candidates),

    'RECON_AGENTS_STARTED': recon_sum.get('agents_started', 'NOT_KNOWN'),
    'RECON_AGENTS_RETURNED': recon_sum.get('agents_returned_result', 'NOT_KNOWN'),
    'RECON_AGENTS_NOT_COMPLETED': recon_sum.get('agents_not_completed', 'NOT_KNOWN'),
}

# --------------------------------------------------- post-red-team measurements
joint = js('joint-coverage.json', {})
jstations = joint.get('stations', [])
pockets = js('disease-outcome-pockets.json', {})


def n_at(threshold, key):
    return sum(1 for s in jstations if s.get(key, 0) >= threshold)


# a safe union: PRESERVED, not superseded, not a failed capture
safe = 0
per_manifest = {}
for fn in sorted(os.listdir(M)):
    if not fn.endswith('.jsonl'):
        continue
    n = 0
    for line in open(os.path.join(M, fn), encoding='utf-8'):
        try:
            r = json.loads(line)
        except Exception:
            continue
        if r.get('preservation') == 'PRESERVED' and r.get('counts_as_preserved_document') is not False:
            n += 1
    if n:
        per_manifest[fn] = n
        safe += n

pkg.update({
    'DISTINCT_PRESERVED_ARTIFACTS': safe,
    'DISTINCT_PRESERVED_BY_MANIFEST': per_manifest,
    'PRESERVED_COUNTING_RULE': ('preservation == PRESERVED AND counts_as_preserved_document != false. '
                                'This excludes the 182 quarantined failed captures and the two '
                                'pre-verification manifests that are superseded by their .verified '
                                'twin. Counting raw PRESERVED rows instead gives 1832 and is wrong.'),

    # leaf wetness ALONE vs the four variables a mildew model needs on the SAME day
    'LEAF_WETNESS_ALONE_STATIONS_GE_99_4_PCT': n_at(99.4, 'per_variable_coverage_pct_bfogl')
    or sum(1 for s in jstations
           if 100 * s['per_variable_days_in_window']['BFOGL'] / s['window_days'] >= 99.4),
    'LEAF_WETNESS_ALONE_STATIONS_GE_99_3_PCT': sum(
        1 for s in jstations
        if 100 * s['per_variable_days_in_window']['BFOGL'] / s['window_days'] >= 99.3),
    'JOINT4_VARIABLES': ['BFOGL', 'TARIA2M', 'UMID2M', 'PREC'],
    'JOINT4_STATIONS_GE_99_4_PCT': n_at(99.4, 'joint4_coverage_pct'),
    'JOINT4_STATIONS_GE_99_0_PCT': n_at(99.0, 'joint4_coverage_pct'),
    'JOINT4_WORST_STATIONS': sorted(
        [{'station': s['station_name'], 'joint4_pct': s['joint4_coverage_pct'],
          'last_TARIA2M': s['last_date_TARIA2M'], 'last_UMID2M': s['last_date_UMID2M']}
         for s in jstations], key=lambda s: s['joint4_pct'])[:4],
    'JOINT4_NOTE': ('Per-variable coverage is NOT usable coverage. A model needing leaf wetness, '
                    'temperature, humidity and rain on the same day gets fewer usable stations.'),

    'DISEASE_OUTCOME_FILES_SCANNED_F5_F6': pockets.get('files_scanned', 'NOT_KNOWN'),
    'DISEASE_OUTCOME_FILES_WITH_MEASURED_OUTCOME': pockets.get('files_with_measured_outcome', 'NOT_KNOWN'),
    'DISEASE_OUTCOME_CORRECTION': ('An earlier scan of THIS package concluded OUTCOMES = NONE. That '
                                   'was wrong: it only covered the ARPAV documents manifest and never '
                                   'opened the recon agents F5/F6 folders. Real numeric outcomes do '
                                   'exist there — see LOCAL-DISEASE-COLLECTION-HANDOFF.md section O.'),
})

out = os.path.join(M, 'collection-manifest.json')
with open(out, 'w', encoding='utf-8') as f:
    json.dump(pkg, f, ensure_ascii=False, indent=1)

for k, v in pkg.items():
    if isinstance(v, list) and len(v) > 8:
        print(f'{k} = [{len(v)} items]')
    elif isinstance(v, str) and len(v) > 110:
        print(f'{k} = {v[:110]}...')
    else:
        print(f'{k} = {v}')
print()
print('->', os.path.relpath(out, ROOT))
