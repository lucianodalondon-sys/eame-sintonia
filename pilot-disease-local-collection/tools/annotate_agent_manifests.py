"""Attach red-team corrections to the recon agents' own manifests.

The agents' original claims are NOT edited or deleted — they stay exactly as
written so the record is auditable. A `_red_team_corrections` block is added,
naming what was refuted and what the files actually support.
"""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M = os.path.join(ROOT, 'manifests')


def magic(rel):
    p = os.path.join(ROOT, rel.replace('/', os.sep))
    try:
        with open(p, 'rb') as f:
            head = f.read(64)
    except Exception:
        return 'FILE_MISSING'
    low = head.lstrip().lower()
    if low.startswith(b'<!doctype html') or low.startswith(b'<html'):
        return 'html'
    if head.lstrip()[:1] in (b'{', b'['):
        return 'json'
    return 'other'


CORRECTIONS = {
    'F6-other-pests.manifest.json': {
        'audited_by': 'red-team lens L4-weather-vs-disease, verdict CONFIRMED / BLOCKER, reproduced independently',
        'corrections': [
            {
                'original_claim': 'measured_totals.puglia_xylella_records = 688631',
                'verdict': 'REFUTED — catalogue availability presented as preserved data',
                'what_is_true': ('688,631 is the CKAN API\'s own `total` field, i.e. the size of the '
                                 'REMOTE table. It was never downloaded. Exactly 5 Xylella records '
                                 'exist on disk (3 in puglia-xylella-datastore-sample.json, 2 in '
                                 'puglia-xylella-last-records.json).'),
                'corrected_value': 'PRESERVED = 5 records. DISCOVERED = 688,631 (remote count).',
            },
            {
                'original_claim': 'measured_totals.puglia_xylella_positivo = 5241 / puglia_xylella_negativo = 683390',
                'verdict': 'NOT_PRESERVED — no evidence on disk',
                'what_is_true': ('The file that should carry the split, '
                                 'raw/F6-other-pests/puglia-xylella-year-result-counts.json, is not '
                                 'JSON at all: it is a Liferay HTML block page from dati.puglia.it '
                                 'refusing the request as an attack. The script that produced the '
                                 'numbers printed to stdout and saved nothing.'),
                'corrected_value': 'puglia_xylella_positivo = NOT_PRESERVED. puglia_xylella_negativo = NOT_PRESERVED.',
                'evidence_file': 'raw/F6-other-pests/puglia-xylella-year-result-counts.json',
                'evidence_file_actual_format': magic('raw/F6-other-pests/puglia-xylella-year-result-counts.json'),
                'evidence_file_state': 'COLLECTION_FAILED (WAF block page saved under a .json name)',
            },
            {
                'original_claim': 'measured_totals.unibo_cimice_trap_week_observations_nonzero = 12109',
                'verdict': 'PARTLY_TRUE — off by one against an unstated definition',
                'what_is_true': ('The headline total 19,432 trap-week observations reproduces exactly. '
                                 'The "nonzero" subset is 12,110 under "any life stage > 0"; the '
                                 'manifest\'s 12,109 uses a definition it does not state.'),
                'corrected_value': '19,432 trap-week observations (confirmed). Nonzero definition = NOT_STATED.',
                'scope_note': ('These are Halyomorpha halys INSECT trap catches in Emilia-Romagna. '
                               'Not a disease outcome, and not on vine.'),
            },
        ],
    },
    'F5-annual-reports.json': {
        'audited_by': 'red-team lens L4-weather-vs-disease, verdict CONFIRMED / MINOR, reproduced independently',
        'corrections': [
            {
                'original_claim': ('numeric_evidence_seen_in_text for AIPP-Bilanci-2025-Vite-nord-malattie.pdf: '
                                   '"classi di danno sul territorio: 0% / 1-10% / 11-40% / 41-100%"'),
                'verdict': 'REFUTED — a chart legend read as data',
                'what_is_true': ('"0% / 1-10% / 11-40% / 41-100%" is the four-band LEGEND of a damage-'
                                 'threshold chart (axis labels). The per-disease value itself is a '
                                 'colour inside one of 463 images across 17 slides.'),
                'corrected_value': 'Legend, not a measurement. Veneto vine damage class 2025 = NOT_KNOWN (the deck says the adjective "Assenti o molto contenuti").',
            },
            {
                'original_claim': 'numeric_evidence_seen_in_text: "n. interventi antiperonosporici (17)"',
                'verdict': 'REFUTED — a management action read as a disease value',
                'what_is_true': '17 is the number of ANTI-DOWNY-MILDEW SPRAYS applied, not a disease measurement.',
                'corrected_value': 'Spray count, not disease incidence or severity.',
            },
        ],
    },
    'F2b-vagri-vite.json': {
        'audited_by': 'red-team lens L4-weather-vs-disease, verdict CONFIRMED / MINOR, reproduced independently',
        'corrections': [
            {
                'original_claim': 'Report_sulle_Previsioni_vendemmiali_2025.pdf — Flavescenza dorata pressure "un calo del 45%"',
                'verdict': 'PARTLY_TRUE — a relative number with no anchor',
                'what_is_true': ('The report states pressure fell "del 45% rispetto ai livelli del 2023" '
                                 'but never gives the 2023 baseline, never defines "pressione", names '
                                 'no geography, no sampling method and no sample count. It is a '
                                 'harvest-forecast press document, not a monitoring report.'),
                'corrected_value': 'Not usable as a disease outcome observation. Absolute level, metric and geography = NOT_KNOWN.',
            },
        ],
    },
}

for name, block in CORRECTIONS.items():
    p = os.path.join(M, name)
    if not os.path.exists(p):
        print(f'{name}: NOT FOUND, skipped')
        continue
    d = json.load(open(p, encoding='utf-8'))
    d['_red_team_corrections'] = block
    d['_red_team_note'] = ('The agent\'s original fields above are left exactly as it wrote them, '
                           'on purpose. Where they are wrong, the correction is in '
                           '_red_team_corrections. Read both.')
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    print(f'{name}: {len(block["corrections"])} corrections attached')
