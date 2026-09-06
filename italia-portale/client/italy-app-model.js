/* SINTONIA · APPLICATION DATA MODEL — v3
   ===========================================================================
   THE ONE INGESTION BOUNDARY.

       HANDOFF V2.1  ─┐
       CANONICAL      ├─►  INGEST · VALIDATE · NORMALIZE  ─►  ITALY_APP_MODEL  ─►  UI
       REAL SOURCE    │
       DEMO FIXTURE  ─┘

   A view never learns which research mission produced a record. It reads a
   normalized collection and nothing else.

   PRECEDENCE, highest first
     1 CANONICAL       upstream-audited truth (crop windows, the label audit)
     2 REAL_SOURCE     real ingested records from an external source
     3 REAL_DERIVED    computed from real records, never invented
     4 SYNTHETIC_DEMO  explicit demonstration fixtures, always labelled
     5 DEMO_SCENARIO   presentation scenario, never counted as real

   pick() takes the first non-empty candidate in precedence order. When the next
   package supplies a real table it wins automatically, without touching a view.

   PRODUCT LAW
   Sintonia core is EXTERNAL intelligence. Nothing here depends on CRM, orders,
   sell-in, sell-out, stock or private pipeline. What the external world cannot
   reveal resolves to NOT_EXTERNALLY_OBSERVABLE — never a placeholder that
   invites private data.

   THE NARRATIVE RULE — why free prose is suppressed
   Measured on this package: 219/219 label-use rows, 17/17 voices, 8/8 news
   items, 16 crop-window fields and 6 resistance mechanisms carry SINTONIA
   RESEARCH NOTES WRITTEN IN PORTUGUESE. Pointing a view straight at the real
   contract would put internal Portuguese working notes in front of the Italian
   client. So narrative() never returns a raw prose field: it returns the
   approved localized variant (FIELD_IT / FIELD_EN) when the upstream package
   supplies one, and otherwise nothing. Facts — dates, enums, names, URLs,
   numbers, original public quotes — are unaffected.
   =========================================================================== */
(function () {
  'use strict';

  /* ── 0 · SOURCE REGISTRY ──────────────────────────────────────────────────
     The only place that knows where data physically comes from. A future
     Handoff V2.1 registers here and needs no other change. */
  const RAW = {
    HANDOFF_V21: (typeof window !== 'undefined' && window.ITALY_HANDOFF_V21) || null,
    CANON: (typeof window !== 'undefined' && window.ITALY_CANONICAL) || {},
    LABEL_AUDIT: (typeof window !== 'undefined' && window.ITALY_LABEL_VERDICTS) || {},
    IG: (typeof window !== 'undefined' && window.ITALY_INGEST) || {},
    CATALOG: (typeof window !== 'undefined' && window.ITALY_CATALOG) || {},
    MARKET: (typeof window !== 'undefined' && window.ITALY_MARKET) || {},
    SCIENCE_BIZ: (typeof window !== 'undefined' && window.ITALY_SCIENCE) || {},
    REAL: (typeof window !== 'undefined' && window.ITALY_REAL) || {},
    DEMO: (typeof window !== 'undefined' && window.ITALY_DEMO) || {},
  };

  const P = {
    CANONICAL: 'CANONICAL',
    REAL_SOURCE: 'REAL_SOURCE',
    REAL_DERIVED: 'REAL_DERIVED',
    SYNTHETIC_DEMO: 'SYNTHETIC_DEMO',
    DEMO_SCENARIO: 'DEMO_SCENARIO',
    NOT_OBSERVABLE: 'NOT_EXTERNALLY_OBSERVABLE',
  };
  const PRECEDENCE = [P.CANONICAL, P.REAL_SOURCE, P.REAL_DERIVED, P.SYNTHETIC_DEMO, P.DEMO_SCENARIO];
  const DEMO_CLASSES = { SYNTHETIC_DEMO: 1, DEMO_SCENARIO: 1, DEMO: 1 };

  /* ── 1 · ONE CLOCK ───────────────────────────────────────────────────────
     Every relative date in the application traces to this value. */
  const REFERENCE_DATE =
    (RAW.HANDOFF_V21 && RAW.HANDOFF_V21.referenceDate) ||
    (RAW.CANON.meta && RAW.CANON.meta.referenceDate) ||
    RAW.CANON.referenceDate ||
    '2026-09-02';
  const REF = new Date(REFERENCE_DATE + 'T00:00:00');
  const asDate = (iso) => {
    if (!iso) return null;
    const d = new Date(String(iso).slice(0, 10) + 'T00:00:00');
    return isNaN(d) ? null : d;
  };
  const daysFrom = (iso) => {
    const d = asDate(iso);
    return d ? Math.round((d - REF) / 864e5) : null;
  };

  /* ── 2 · SCALAR NORMALIZERS ──────────────────────────────────────────────── */
  const S = (v) => (v === null || v === undefined || v === '' ? null : String(v).trim());
  const N = (v) => (v === null || v === undefined || v === '' ? null : isNaN(Number(v)) ? null : Number(v));
  const A = (v) => (Array.isArray(v) ? v : v === null || v === undefined || v === '' ? [] : [v]);
  const U = (v) => String(v || '').trim().toUpperCase();
  const uniq = (a) => [...new Set(a.filter(Boolean))];

  /* ── 3 · THE NARRATIVE RULE ──────────────────────────────────────────────
     UNKNOWN_SENTINEL is the upstream's own way of saying "not established".
     It is a fact about the state of knowledge, so it survives — as a state,
     never as its Portuguese explanation. */
  const UNKNOWN_SENTINEL = /^\s*(NAO SEI|N[ÃA]O SEI|NOT KNOWN|UNKNOWN)\b/i;
  const KNOWLEDGE = { CLEAR: 'CLEAR', NOT_ESTABLISHED: 'NOT_ESTABLISHED', NOT_APPROVED_FOR_DISPLAY: 'NOT_APPROVED_FOR_DISPLAY' };

  /**
   * Read a narrative field safely.
   * Returns { state, it, en } — a view renders `it`/`en` only when CLEAR.
   * Raw prose without an approved localized variant is never returned.
   */
  const narrative = (rec, base) => {
    if (!rec) return { state: KNOWLEDGE.NOT_APPROVED_FOR_DISPLAY, it: null, en: null };
    const it = S(rec[base + '_IT']) || S(rec[base + '_it']);
    const en = S(rec[base + '_EN']) || S(rec[base + '_en']);
    const raw = S(rec[base]);
    if (raw && UNKNOWN_SENTINEL.test(raw) && !it && !en) {
      return { state: KNOWLEDGE.NOT_ESTABLISHED, it: null, en: null };
    }
    if (it || en) return { state: KNOWLEDGE.CLEAR, it: it || en, en: en || it };
    return { state: raw ? KNOWLEDGE.NOT_APPROVED_FOR_DISPLAY : KNOWLEDGE.NOT_ESTABLISHED, it: null, en: null };
  };
  /** Count of narrative fields the upstream has not yet localized. Reported, not hidden. */
  const narrativeDebt = [];
  const noteNarrative = (family, field, n) => { if (n) narrativeDebt.push({ family, field, records: n }); };

  /**
   * UNK — the same rule applied to a SCALAR field.
   * narrative() is for prose that has an approved translation slot. UNK() is for
   * a field the view treats as a value (a role, a region, a date, a timing) whose
   * upstream content is the analyst's own "I do not know" sentence. Measured on
   * this package: RESEARCHERS.ROLE 60/60, RESEARCHERS.FACT_REGION 60/60,
   * VOICES.REGION 17/17, NEWS.REGION 8/8 and LINKS.timing 219/219 carry it.
   * Returning the sentence would print a Portuguese working note on an Italian
   * screen AND would populate a filter with a fake value; null lets the view
   * render its own "non noto".
   */
  const UNK = (v) => { const s = S(v); return s && UNKNOWN_SENTINEL.test(s) ? null : s; };

  /**
   * STATE_TOKEN — a knowledge-state field whose upstream value is a CODE
   * followed, sometimes, by the analyst's Portuguese explanation of it
   * ("NAO_ATRIBUIVEL — handle publico pseudonimizado"). The code is the fact
   * and is language-independent; the explanation is a working note written in
   * the research language and has no approved Italian variant, so it is not
   * client content. This returns the code alone, uppercased with underscores,
   * and null when there is none. The view localizes the code.
   */
  const STATE_TOKEN = (v) => {
    const s = S(v); if (!s) return null;
    const head = s.split(/\s*[\u2014\u2013:-]\s+|\s*\u00b7\s*/)[0].trim();
    const code = head.replace(/\s+/g, '_').toUpperCase();
    return /^[A-Z][A-Z0-9_]*$/.test(code) ? code : null;
  };

  /* ── 3b · DATE SHAPES ────────────────────────────────────────────────────
     Four incompatible date shapes are measured in this package: ISO
     (YYYY-MM-DD), ISO timestamps (channels' EXAMPLE_PUBLISHED_AT), the market
     portal's dd/mm/yyyy, and ranges written 'YYYY-MM-DD a YYYY-MM-DD'. Parsing
     belongs here once, not in every screen. A shape that is not one of these
     stays UNKNOWN — a date is never guessed. */
  const ISO_D = /^\d{4}-\d{2}-\d{2}$/;
  const DMY_D = /^(\d{2})\/(\d{2})\/(\d{4})$/;
  const dmyToIso = (v) => { const m = DMY_D.exec(String(v || '').trim()); return m ? m[3] + '-' + m[2] + '-' + m[1] : null; };
  /** ISO date or null. Never throws, never invents. */
  const isoOf = (v) => {
    const s = S(v);
    if (!s || UNKNOWN_SENTINEL.test(s)) return null;
    const head = s.slice(0, 10);
    return ISO_D.test(head) ? head : dmyToIso(s);
  };
  /** Split 'YYYY-MM-DD a YYYY-MM-DD' into two ISO dates; a single date yields [d, d]. */
  const isoRange = (v) => {
    const s = S(v);
    if (!s) return [null, null];
    const parts = s.split(/\s+a\s+/i);
    const a = isoOf(parts[0]);
    const b = parts.length > 1 ? isoOf(parts[1]) : a;
    return [a, b || a];
  };
  /** Classify a raw date string without converting it. */
  const dateStateOf = (raw) => {
    const s = S(raw);
    if (!s) return 'NOT_OBSERVED';
    if (UNKNOWN_SENTINEL.test(s)) return 'UNKNOWN';
    if (/\s+a\s+/i.test(s)) return 'RANGE';
    if (isoOf(s)) return 'EXACT';
    return 'PERIOD';
  };

  /* ── 3c · SMALL SET UTILITIES ───────────────────────────────────────────── */
  const fold = (v) => String(v === null || v === undefined ? '' : v).normalize('NFD').replace(/[̀-ͯ]/g, '');
  const tallyBy = (rows, get) => {
    const m = {};
    (rows || []).forEach((r) => A(get(r)).forEach((v) => { if (v !== null && v !== undefined && v !== '') m[v] = (m[v] || 0) + 1; }));
    return m;
  };
  const minIso = (a) => (a || []).filter(Boolean).slice().sort()[0] || null;
  const maxIso = (a) => { const s = (a || []).filter(Boolean).slice().sort(); return s.length ? s[s.length - 1] : null; };
  const byCountDesc = (map) => Object.keys(map).sort((x, y) => map[y] - map[x] || (x < y ? -1 : 1));

  /* ── 4 · PROVENANCE ──────────────────────────────────────────────────────
     Explicit provenance is primary truth. A record is never called real
     because a property name happened to be absent. */
  const provOf = (r, fallback) => {
    if (!r) return fallback;
    const p = U(r.provenance || r.PROVENANCE || r.prov);
    if (p) {
      for (const k in DEMO_CLASSES) if (p.indexOf(k) >= 0) return P.SYNTHETIC_DEMO;
      return p;
    }
    if (r.isDemo === true || r.demo === true) return P.SYNTHETIC_DEMO;
    return fallback;
  };
  const isDemo = (r, fallback) => !!DEMO_CLASSES[provOf(r, fallback)];

  /* ── 5 · COLLECTION + VALIDATION ─────────────────────────────────────────
     Every family passes through here, so the ingest report is a by-product of
     building the model rather than a separate document that can drift. */
  const ingestReport = { families: [], accepted: 0, rejected: 0, empty: [] };

  const coll = (records, provenance, note, meta) => {
    const rec = (records || []).filter(Boolean);
    const c = {
      records: rec,
      provenance,
      note: note || '',
      count: rec.length,
      demo: rec.filter((r) => isDemo(r, provenance)).length,
      real: rec.filter((r) => !isDemo(r, provenance)).length,
      source: (meta && meta.source) || null,
      rejected: (meta && meta.rejected) || [],
    };
    return c;
  };

  /**
   * Build one family: run each candidate source through its adapter in
   * precedence order and keep the first that yields records. An empty
   * collection is a valid answer — it is never filled with invented rows.
   */
  const build = (family, candidates, note) => {
    const tried = [];
    for (const cand of candidates) {
      if (!cand) continue;
      const { source, precedence, rows, adapt, validate } = cand;
      const input = (rows || []).filter(Boolean);
      if (!input.length) { tried.push({ source, precedence, in: 0, out: 0 }); continue; }
      const out = [];
      const rejected = [];
      for (const raw of input) {
        let rec;
        try { rec = adapt(raw); } catch (e) { rejected.push({ raw: raw && (raw.ID || raw.id), why: 'adapter threw: ' + e.message }); continue; }
        if (!rec) { rejected.push({ raw: raw && (raw.ID || raw.id), why: 'adapter returned nothing' }); continue; }
        const bad = validate ? validate(rec) : null;
        if (bad) { rejected.push({ raw: rec.id, why: bad }); continue; }
        out.push(rec);
      }
      tried.push({ source, precedence, in: input.length, out: out.length, rejected: rejected.length });
      if (out.length) {
        ingestReport.families.push({ family, chosen: source, precedence, accepted: out.length, rejected: rejected.length, tried });
        ingestReport.accepted += out.length;
        ingestReport.rejected += rejected.length;
        return coll(out, precedence, note, { source, rejected });
      }
    }
    ingestReport.families.push({ family, chosen: null, precedence: null, accepted: 0, rejected: 0, tried });
    ingestReport.empty.push(family);
    return coll([], P.REAL_SOURCE, note, { source: null });
  };

  const V21 = (family) => {
    const d = RAW.HANDOFF_V21 && RAW.HANDOFF_V21[family];
    return d ? { source: 'HANDOFF_V21', precedence: P.CANONICAL, rows: A(d), adapt: (r) => r } : null;
  };

  /* ── 6 · PRESENTATION TOKENS ─────────────────────────────────────────────
     Icon, colour, order and grouping only. Physically separated from the fact
     space so no screen can mistake a tint for evidence. The values are the
     ADAMA Brandwell semantics already used by the portal — they are read from
     the fixture's category table only as a colour lookup, never as a
     classification. */
  const CATEGORY_UI = {
    pest: { key: 'pest', label: 'Pest Control', color: '#9D1D96', dark: '#752157', soft: '#C77BC3', ink: '#fff', body: '#EDEAE9', muted: '#C9C3C1', icon: 'pest-control', iconAsset: 'assets/icons/pest-control-white.png', aShape: 'assets/a-pest-2.png', order: 0 },
    disease: { key: 'disease', label: 'Disease Control', color: '#00A0DF', dark: '#00698F', soft: '#5CC3EE', ink: '#1C1817', body: '#FFFFFF', muted: '#F4F2F2', icon: 'disease-control', iconAsset: 'assets/icons/disease-control-white.png', aShape: 'assets/a-disease-2.png', order: 1 },
    weed: { key: 'weed', label: 'Weed Control', color: '#7DB41E', dark: '#00783F', soft: '#93CC23', ink: '#1C1817', body: '#FFFFFF', muted: '#F4F2F2', icon: 'weed-control', iconAsset: 'assets/icons/weed-control-white.png', aShape: '', order: 2 },
    /* label is deliberately null: an unclassified record must hide the category
       chip, not print a guess. */
    unknown: { key: 'unknown', label: null, color: '#8F8886', dark: '#3A3533', soft: '#B1A9A7', ink: '#fff', body: '#EDEAE9', muted: '#B1A9A7', icon: 'connect', iconAsset: '', aShape: '', order: 3 },
  };
  /* The pest / disease / weed split is a FACT that comes from the canonical
     ISSUE_TYPE, never from a colour table. */
  const categoryOf = (issueType) => {
    const t = U(issueType);
    if (!t) return CATEGORY_UI.unknown;
    if (t.indexOf('PEST') >= 0 || t.indexOf('INSECT') >= 0 || t.indexOf('INSETT') >= 0) return CATEGORY_UI.pest;
    if (t.indexOf('DISEASE') >= 0 || t.indexOf('FUNG') >= 0 || t.indexOf('MALATT') >= 0 || t.indexOf('PHYTOPLASMA') >= 0 || t.indexOf('VIRUS') >= 0) return CATEGORY_UI.disease;
    if (t.indexOf('WEED') >= 0 || t.indexOf('INFEST') >= 0 || t.indexOf('HERB') >= 0) return CATEGORY_UI.weed;
    return CATEGORY_UI.unknown;
  };

  /* ── 6b · THE REST OF THE PRESENTATION LAYER ─────────────────────────────
     Every token below is authored here, not read from the fixture. They were
     verified to contain no crop, issue, date, source, count or verdict — only
     ADAMA brand constants, contrast rules and grid coordinates — which is why
     they are allowed to be authored (§4). Moving them out of the fixture is
     what turns a remaining `window.ITALY_DEMO` read into a real defect. */

  /* One ink rule per brand fill: dark ink on light fills, white only on dark. */
  const INK = {
    '#F89E18': '#1C1817', '#00A0DF': '#1C1817', '#978B87': '#1C1817', '#7DB41E': '#1C1817',
    '#F5B317': '#1C1817', '#93CC23': '#1C1817', '#00B152': '#1C1817', '#8F8886': '#1C1817',
    '#B1A9A7': '#1C1817', '#C9C3C1': '#1C1817', '#C77BC3': '#1C1817', '#5CC3EE': '#1C1817',
    '#fff': '#1C1817', '#FFFFFF': '#1C1817',
    '#009845': '#fff', '#00783F': '#fff', '#752157': '#fff', '#9D1D96': '#fff',
    '#00698F': '#fff', '#6E6663': '#fff', '#3A3533': '#fff', '#1C1817': '#fff',
  };
  const inkOn = (fill) => INK[String(fill || '').trim()] || '#fff';

  /* Status tokens. ACT_NOW has a colour but is never DERIVED here: §7 leaves the
     agronomic state to upstream's CURRENT_STATUS. DEFAULT exists so an unknown
     code cannot throw. */
  const STATUS_UI = {
    WINDOW_OPEN: { color: '#00783F', text: '#00B152', rank: 1 },
    WINDOW_CLOSED: { color: '#6E6663', text: '#8F8886', rank: 6 },
    NEXT_CYCLE: { color: '#6E6663', text: '#8F8886', rank: 5 },
    DATE_UNKNOWN: { color: '#978B87', text: '#B1A9A7', rank: 4 },
    ACT_NOW: { color: '#00783F', text: '#00B152', rank: 0 },
    DEFAULT: { color: '#978B87', text: '#B1A9A7', rank: 9 },
  };
  const DEPARTMENT_UI = {
    'MARKET DEVELOPMENT': { color: '#978B87', soft: '#C3BCBA' },
    'SALES / RTV': { color: '#978B87', soft: '#C3BCBA' },
    MARKETING: { color: '#978B87', soft: '#C3BCBA' },
    'TECHNICAL / SCIENCE': { color: '#978B87', soft: '#C3BCBA' },
    'REGULATORY / PORTFOLIO': { color: '#978B87', soft: '#C3BCBA' },
    SUPPLY: { color: '#978B87', soft: '#C3BCBA' },
    DEFAULT: { color: '#978B87', soft: '#C3BCBA' },
  };
  /* The 20 Italian regions with their grid coordinates. Coordinates only — no
     count, no colour, no active flag. Those were the fields that let a layout
     table publish a number. */
  const REGION_GRID = [
    ["Valle d'Aosta", 0, 0], ['Trentino-Alto Adige', 2, 0], ['Friuli-Venezia Giulia', 3, 0],
    ['Piemonte', 0, 1], ['Lombardia', 1, 1], ['Veneto', 2, 1],
    ['Liguria', 0, 2], ['Emilia-Romagna', 1, 2],
    ['Toscana', 1, 3], ['Marche', 2, 3],
    ['Umbria', 1, 4], ['Abruzzo', 2, 4],
    ['Lazio', 1, 5], ['Molise', 2, 5], ['Sardegna', 0, 5],
    ['Campania', 2, 6], ['Puglia', 3, 6],
    ['Basilicata', 2, 7], ['Calabria', 2, 8], ['Sicilia', 1, 9],
  ].map((r) => ({ name: r[0], short: r[0].split(/[\s-]/).map((x) => x[0]).join('').toUpperCase().slice(0, 3), col: r[1], row: r[2], gc: r[1] + 1, gr: r[2] + 1 }));
  const REGION_NAMES = REGION_GRID.map((r) => r.name);

  /* Colour per source TYPE — keyed on the 12 values actually measured in
     ITALY_INGEST.SOURCES, so an unseen type falls to NEUTRAL instead of
     borrowing the meaning of another type. */
  const NEUTRAL = '#8F8886';
  const SOURCE_TYPE_COLOR = {
    OFFICIAL: '#00698F', MARKET: '#F5B317', RESEARCH: '#9D1D96', RESEARCH_INSTITUTION: '#9D1D96',
    TECHNICAL_MEDIA: '#00A0DF', FIELD: '#7DB41E', COOPERATIVE: '#7DB41E', PRODUCER_ORG: '#7DB41E',
    COMPANY: '#978B87', COMPETITOR: '#978B87', PEOPLE: '#C77BC3', ADAMA: '#00B152',
  };
  /* Per-kind archive tokens. Pure layout: the legacy fixture used one constant
     grey for all 448 rows, so nothing informational is lost by authoring these. */
  const ARCHIVE_UI = {
    COMPETITOR: { color: '#978B87', order: 0 },
    SCIENCE: { color: '#9D1D96', order: 1 },
    MARKET: { color: '#F5B317', order: 2 },
    WINDOW: { color: '#00783F', order: 3 },
    EVENT: { color: '#00A0DF', order: 4 },
    VOICE: { color: '#7DB41E', order: 5 },
    NEWS: { color: '#00698F', order: 6 },
    RESISTANCE: { color: '#752157', order: 7 },
    DEFAULT: { color: NEUTRAL, order: 9 },
  };
  /* 'DD Mmm' with the month names the caller supplies. The month array is a
     parameter and not a module global on purpose: a mutable global is how a
     language switch used to silently rewrite dates already rendered. */
  const fmtDate = (value, monthNames) => {
    const iso = isoOf(value);
    if (!iso) return null;
    const MN = Array.isArray(monthNames) && monthNames.length === 12
      ? monthNames : ['Gen', 'Feb', 'Mar', 'Apr', 'Mag', 'Giu', 'Lug', 'Ago', 'Set', 'Ott', 'Nov', 'Dic'];
    return iso.slice(8, 10) + ' ' + MN[Number(iso.slice(5, 7)) - 1];
  };

  /* ── 6c · DECLARED LOOKUPS ───────────────────────────────────────────────
     The package speaks five crop vocabularies and nothing upstream joins them.
     Every join below is written out as a table an auditor can check against the
     measured value sets, because the alternative — each screen doing its own
     string match — is how the same crop ended up with two different counts.
     A term that has no unambiguous canonical partner is left OUT of the table
     and travels verbatim. Guessing here would be inventing a fact. */

  /* canonical window CROP_NAME -> the crop codes used by ITALY_INGEST.LINKS /
     .PRODUCTS. The one judgement call is recorded in `note`. */
  const CROP_KEY = [
    { crop: 'Grapevine', codes: ['GRAPEVINE'], note: null },
    { crop: 'Maize', codes: ['MAIZE'], note: null },
    { crop: 'Olive', codes: ['OLIVE'], note: null },
    { crop: 'Sugar Beet', codes: ['SUGARBEET'], note: null },
    { crop: 'Apple', codes: ['APPLE'], note: null },
    { crop: 'Tomato', codes: ['TOMATO'], note: null },
    { crop: 'Rice', codes: ['RICE'], note: null },
    { crop: 'Soybean', codes: ['SOYBEAN'], note: null },
    { crop: 'Wheat', codes: ['COMMON_WHEAT', 'WHEAT_GENERIC'], note: "WHEAT_GENERIC ('Frumento') is counted for both Wheat and Durum Wheat; the overlap is declared, never hidden." },
    { crop: 'Durum Wheat', codes: ['DURUM_WHEAT', 'WHEAT_GENERIC'], note: 'DURUM_WHEAT has no use row of its own in this reading, so every Durum Wheat row comes from the generic Frumento label.' },
    { crop: 'Barley', codes: ['BARLEY'], note: null },
    { crop: 'Potato', codes: ['POTATO'], note: null },
    { crop: 'Sorghum', codes: ['SORGHUM'], note: null },
    { crop: 'Triticale', codes: ['TRITICALE'], note: null },
  ];
  const CROP_BY_CODE = {};
  CROP_KEY.forEach((r) => r.codes.forEach((c) => { (CROP_BY_CODE[c] = CROP_BY_CODE[c] || []).push(r.crop); }));
  const cropFromCode = (code) => (CROP_BY_CODE[U(code)] || [])[0] || null;
  const cropsFromCode = (code) => (CROP_BY_CODE[U(code)] || []).slice();

  /* Latin binomial -> canonical crop. A taxonomic identity, not an
     interpretation. 'Citrus' and 'Prunus persica' have no canonical window crop
     and are therefore absent: they stay as published. */
  const CROP_BY_LATIN = {
    'VITIS VINIFERA': 'Grapevine', 'ZEA MAYS': 'Maize', 'OLEA EUROPAEA': 'Olive',
    'SOLANUM LYCOPERSICUM': 'Tomato', 'MALUS DOMESTICA': 'Apple', 'TRITICUM AESTIVUM': 'Wheat',
    'ORYZA SATIVA': 'Rice', 'BETA VULGARIS': 'Sugar Beet',
    /* Peach and Citrus are real crops with no canonical window in this package.
       They resolve here because the identity is taxonomic; they simply have no
       CROP_KEY row, which is a gap in the window contract, not in the name. */
    'PRUNUS PERSICA': 'Peach', CITRUS: 'Citrus',
  };
  /* The advertiser's own umbrella words. A generic term is never promoted to a
     crop; it is only recognised so it can be reported as generic. */
  const GENERIC_CROP_TERMS = { COLTURE: 1, CEREALI: 1, FRUTTA: 1, ORTAGGI: 1, ORTICOLE: 1 };

  /* SCREAMING_SNAKE crop tokens used by SCIENCE / VOICES / THEMES. */
  const CROP_BY_TOKEN = {
    VINE: 'Grapevine', GRAPEVINE: 'Grapevine', MAIZE: 'Maize', MAIS: 'Maize',
    OLIVE: 'Olive', OLIVO: 'Olive', DURUM_WHEAT: 'Durum Wheat', COMMON_WHEAT: 'Wheat',
    WHEAT: 'Wheat', TOMATO: 'Tomato', RICE: 'Rice', SUGARBEET: 'Sugar Beet', APPLE: 'Apple',
    SOYBEAN: 'Soybean', BARLEY: 'Barley', VITE: 'Grapevine',
    /* CEREAL / CEREAIS / ORTICOLE deliberately absent: they name a group, not a crop. */
  };

  /* ITALY_INGEST.CROP_WINDOWS writes crops in Italian. */
  const CROP_BY_IT = { VITE: 'Grapevine', OLIVO: 'Olive', MAIS: 'Maize', 'FRUMENTO DURO': 'Durum Wheat', FRUMENTO: 'Wheat', POMODORO: 'Tomato', RISO: 'Rice', MELO: 'Apple', BARBABIETOLA: 'Sugar Beet', ORZO: 'Barley', SOIA: 'Soybean' };

  /* Market series -> crop. The market portal publishes a series code, not a
     crop, so this table is what makes the olive tab six oil grades of one crop
     instead of six crops. Anything unmatched stays null: ORGFOUR|FEED (barley)
     resolves to Barley, which is a real crop but has NO canonical window — that
     is a fact worth showing, not a reason to force it into another bucket. */
  const MARKET_CROP = {
    'OLIVE_OIL|*': 'Olive', 'WINE|*': 'Grapevine',
    'CEREAL|MAI|FEED': 'Maize', 'CEREAL|Feed maize': 'Maize',
    'CEREAL|BLTPAN|PAN': 'Wheat', 'CEREAL|Breadmaking common wheat': 'Wheat',
    'CEREAL|DUR|UNKNOWN': 'Durum Wheat', 'CEREAL|Durum wheat': 'Durum Wheat',
    'CEREAL|ORGFOUR|FEED': 'Barley', 'CEREAL|Feed barley': 'Barley',
  };
  /* The Market Pulse screen addresses crops by its own short key. Only the
     unambiguous ones are mapped; Barley has no key and must route without
     changing the selected crop rather than being forced into a bucket. */
  const MARKET_VIEW_KEY = { Maize: 'maize', 'Durum Wheat': 'durum', Wheat: 'soft', Olive: 'olive', Grapevine: 'wine', Tomato: 'tomato', 'Sugar Beet': 'sugarbeet', Apple: 'apple' };

  /* Bibliometric theme token -> a controlled display title. NOT a translation of
     the token and NOT a scientific conclusion: it is a label for a query. The
     query itself travels with the record so the reader can see what was counted. */
  const THEME_UI = {
    VINE_FLAVESCENCE: { title: 'Flavescenza dorata · vite', cropToken: 'VINE', issueToken: 'FLAVESCENCE', issueType: 'PEST' },
    DURUM_FUSARIUM: { title: 'Fusariosi della spiga · frumento duro', cropToken: 'DURUM_WHEAT', issueToken: 'FUSARIUM', issueType: 'DISEASE' },
    OLIVE_BACTROCERA: { title: 'Mosca delle olive · olivo', cropToken: 'OLIVE', issueToken: 'BACTROCERA', issueType: 'PEST' },
    MAIZE_BORER_DIABROTICA: { title: 'Piralide e diabrotica · mais', cropToken: 'MAIZE', issueToken: 'BORER_DIABROTICA', issueType: 'PEST' },
    WEED_HERBICIDE_RESISTANCE: { title: 'Resistenza agli erbicidi · infestanti', cropToken: null, issueToken: 'HERBICIDE_RESISTANCE', issueType: 'WEED' },
  };

  /* IG.SOURCES.TYPE -> the group the source screen buckets on. IG.SOURCES has
     no GROUP field (measured null 31/31 when the model asked for one), so the
     map is written out literally and reconciles to 31. */
  const SOURCE_GROUP = {
    OFFICIAL: 'OFFICIAL', MARKET: 'MARKET', COMPANY: 'MARKET', COMPETITOR: 'MARKET',
    RESEARCH: 'RESEARCH', RESEARCH_INSTITUTION: 'RESEARCH',
    FIELD: 'FIELD', COOPERATIVE: 'FIELD', PRODUCER_ORG: 'FIELD',
    TECHNICAL_MEDIA: 'TECHNICAL_MEDIA', PEOPLE: 'PEOPLE', ADAMA: 'OWN',
  };
  const SOURCE_GROUP_LABEL = {
    OFFICIAL: 'ENTI PUBBLICI E UFFICIALI', RESEARCH: 'RICERCA E SCIENZA',
    FIELD: 'ORGANIZZAZIONI DI CAMPO', TECHNICAL_MEDIA: 'STAMPA E MEDIA TECNICI',
    MARKET: 'AZIENDE E MERCATO', PEOPLE: 'PERSONE', OWN: 'ADAMA',
  };
  /* FREQUENCY carries two crawler tokens that are not a cadence. Measured:
     DATED 13, NO_DATE_FOUND 3, null 4 — so only 11 of 31 sources declare one. */
  const FREQ_NOT_DECLARED = { DATED: 1, NO_DATE_FOUND: 1 };

  /* ── 6d · THE LABEL AUDIT, READ DIRECTLY ─────────────────────────────────
     The audit is the only evidence that says a product is authorised for a crop
     against an issue. Every negative statement carries ABSENCE_RULE with it, so
     no screen can turn "not found in this reading" into "ADAMA has no product"
     (§10).

     Issue names are folded before comparison because the audit writes
     'Cereal Aphids / BYDV Risk' where the canonical window writes
     'Cereal Aphids · BYDV Risk'. Folding those two separators is a spelling
     normalization, not a synonym table — it invents nothing. Measured: folding
     lifts the audit from 10 to 11 of the 29 windows. */
  const ABSENCE_RULE_TEXT = S(RAW.LABEL_AUDIT.ABSENCE_RULE) || 'Absence in this reading is not absence in the world.';
  const foldIssue = (v) => fold(String(v || '')).toUpperCase().replace(/[·/]/g, '|').replace(/\s*\|\s*/g, '|').replace(/\s+/g, ' ').trim();
  const verdictKey = (crop, issue) => U(crop) + '@' + foldIssue(issue);

  const LV_VERIFIED = A(RAW.LABEL_AUDIT.VERIFIED).filter((t) => A(t).length >= 3).map((t) => ({ crop: S(t[0]), issue: S(t[1]), product: S(t[2]), strength: 'VERIFIED_LABEL_MATCH' }));
  const LV_NOT_FOUND = A(RAW.LABEL_AUDIT.NOT_FOUND).filter((t) => A(t).length >= 3).map((t) => ({ crop: S(t[0]), issue: S(t[1]), product: S(t[2]), strength: 'NO_CONFIRMED_MATCH_CURRENT_READING' }));
  const verifiedByCropIssue = {};
  LV_VERIFIED.forEach((v) => { (verifiedByCropIssue[verdictKey(v.crop, v.issue)] = verifiedByCropIssue[verdictKey(v.crop, v.issue)] || []).push(v.product); });
  const notFoundByCropIssue = {};
  LV_NOT_FOUND.forEach((v) => { (notFoundByCropIssue[verdictKey(v.crop, v.issue)] = notFoundByCropIssue[verdictKey(v.crop, v.issue)] || []).push(v.product); });

  /* ═══════════════════════════════════════════════════════════════════════
     7 · FAMILIES
     ═══════════════════════════════════════════════════════════════════════ */

  /* ---- FIELD SIGNALS · the seven observed crop x issue readings ---------
     Built BEFORE the canonical windows because a canonical window joins to it:
     five regional regulatory acts and the only two real field observations in
     the whole package live here, and three of the five have no canonical window
     at all — they are reachable only from their own collection. */
  const currentFieldSignals = build('currentFieldSignals', [
    V21('currentFieldSignals'),
    {
      source: 'ITALY_INGEST.CROP_WINDOWS',
      precedence: P.REAL_SOURCE,
      rows: RAW.IG.CROP_WINDOWS,
      adapt: (c) => ({
        id: c.ID,
        crop: S(c.CROP),
        /* The upstream writes crops in Italian here and in English in the
           canonical contract. The join is a declared table, not a guess. */
        cropCanonical: CROP_BY_IT[U(c.CROP)] || null,
        region: S(c.REGION),
        issue: S(c.ISSUE),
        /* Free prose fields below are Sintonia research notes upstream. They
           are exposed as knowledge STATES, never as their Portuguese text. */
        expectedCycle: narrative(c, 'EXPECTED_CYCLE'),
        observedStage: narrative(c, 'OBSERVED_STAGE'),
        fieldReportedStage: narrative(c, 'FIELD_REPORTED_STAGE'),
        regulatoryWindow: narrative(c, 'REGULATORY_WINDOW'),
        regulatoryAct: S(c.REGULATORY_ACT),
        regulatoryActState: S(c.REGULATORY_ACT_STATE),
        monitoringWindow: narrative(c, 'MONITORING_WINDOW'),
        applicationWindow2026: narrative(c, 'APPLICATION_WINDOW_2026'),
        nextImportantWindow: narrative(c, 'NEXT_IMPORTANT_WINDOW'),
        preparationWindow: narrative(c, 'PREPARATION_WINDOW'),
        adamaProductsNote: narrative(c, 'ADAMA_PRODUCTS_NOTE'),
        notProves: narrative(c, 'WHAT_IT_DOES_NOT_PROVE'),
        coverageState: S(c.COVERAGE_STATE),
        /* Every free-text field in these 7 records is written in the analyst's
           working language, not in the client's. Declaring that is what stops a
           later view dropping Portuguese prose into an Italian screen. */
        languageState: 'PT_ANALYST_SOURCE',
        sourceId: S(c.SOURCE_ID),
        provenance: provOf(c, P.REAL_SOURCE),
        raw: c,
      }),
      validate: (r) => (!r.id ? 'no ID' : null),
    },
  ], 'observed field readings per crop and issue; the analyst working language is declared, not hidden');

  /* Canonical crop + exact region + the same issue is the only join the two
     tables share. The issue check is not optional: crop+region alone attaches
     the Flavescenza dorata regional act to the Downy Mildew window in Veneto,
     which would publish a regulatory obligation against the wrong disease.
     The upstream writes 'Flavescenza dorata (vetor Scaphoideus titanus)' where
     the canonical contract writes 'Flavescenza Dorata' — dropping a
     parenthetical vector note is a spelling difference, not a synonym, so the
     head of the string is compared and nothing is aliased. */
  const issueHead = (v) => foldIssue(String(v || '').split('(')[0]);
  const fieldSignalByCropRegion = {};
  currentFieldSignals.records.forEach((r) => {
    if (r.cropCanonical && r.region) fieldSignalByCropRegion[U(r.cropCanonical) + '@' + U(r.region) + '@' + issueHead(r.issue)] = r;
  });

  /* ---- CROP WINDOWS · canonical ---------------------------------------- */
  let windowOrder = 0;
  const cropWindows = build('cropWindows', [
    V21('cropWindows'),
    {
      source: 'ITALY_CANONICAL.windows',
      precedence: P.CANONICAL,
      rows: RAW.CANON.windows,
      adapt: (w) => ({
        id: w.WINDOW_ID,
        windowId: w.WINDOW_ID,
        legacyCaseId: w.LEGACY_CASE_ID || null,
        crop: S(w.CROP_NAME),
        issue: S(w.ISSUE_NAME),
        issueType: S(w.ISSUE_TYPE),
        region: S(w.REGION),
        generationOrStage: S(w.GENERATION_OR_STAGE),
        windowType: S(w.WINDOW_TYPE),
        startDate: S(w.START_DATE),
        endDate: S(w.END_DATE),
        dateState: S(w.DATE_STATE),
        dateConfidence: S(w.DATE_CONFIDENCE),
        cropStage: S(w.CROP_STAGE),
        cropStageClass: S(w.CROP_STAGE_CLASS),
        cropStageSource: S(w.CROP_STAGE_SOURCE),
        issueStage: S(w.ISSUE_STAGE),
        issueStageClass: S(w.ISSUE_STAGE_CLASS),
        issueStageSource: S(w.ISSUE_STAGE_SOURCE),
        labelTrigger: S(w.LABEL_TRIGGER),
        labelSource: S(w.LABEL_SOURCE),
        regulatoryTiming: S(w.REGULATORY_TIMING),
        regulatorySource: S(w.REGULATORY_SOURCE),
        productMatches: A(w.PRODUCT_MATCHES),
        /* The agronomic state is upstream's to decide. Presentation may never
           compute ACT NOW / WINDOW OPEN / NEXT CYCLE. */
        status: S(w.CURRENT_STATUS),
        /* canonicalStatus is the same value under the name the product screens
           already ask for. It exists because a view reading an undefined
           property silently degraded every window to DATE TO CONFIRM. */
        canonicalStatus: S(w.CURRENT_STATUS),
        statusReason: S(w.STATUS_REASON),
        lastValidated: S(w.LAST_VALIDATED),
        daysToStart: daysFrom(w.START_DATE),
        daysToEnd: daysFrom(w.END_DATE),
        /* open is upstream's verdict re-stated, never a date comparison. */
        open: U(w.CURRENT_STATUS) === 'WINDOW_OPEN',
        hasDates: !!(S(w.START_DATE) && S(w.END_DATE)),
        /* SOURCE_IDS is measured empty on all 29 canonical windows. Saying so
           is the honest answer; the field stays so a later package lights it up
           without a view change. */
        sourceIds: A(w.SOURCE_IDS),
        sourceState: A(w.SOURCE_IDS).length ? 'TRACEABLE' : P.NOT_OBSERVABLE,
        ui: Object.assign({}, categoryOf(w.ISSUE_TYPE), { categoryKey: categoryOf(w.ISSUE_TYPE).key, order: windowOrder++, status: STATUS_UI[U(w.CURRENT_STATUS)] || STATUS_UI.DEFAULT }),
        provenance: P.CANONICAL,
        raw: w,
      }),
      validate: (r) => (!r.id ? 'no WINDOW_ID' : !r.crop ? 'no crop' : null),
    },
  ], 'canonical audited crop windows; agronomic state comes from upstream');

  /* Two joins onto the canonical window, both declared and both measurable.
     Neither can create a window and neither can change its status. */
  cropWindows.records.forEach((w) => {
    const k = verdictKey(w.crop, w.issue);
    w.verifiedProducts = (verifiedByCropIssue[k] || []).slice();
    w.notFoundProducts = (notFoundByCropIssue[k] || []).slice();
    w.labelVerdictState = w.verifiedProducts.length ? 'VERIFIED_LABEL_MATCH' : 'NO_CONFIRMED_MATCH_CURRENT_READING';
    w.absenceRule = ABSENCE_RULE_TEXT;
    /* The upstream regulatory reading for this exact crop and region, or null.
       Measured: 2 of 29 windows join (both Flavescenza Dorata). */
    const fs = fieldSignalByCropRegion[U(w.crop) + '@' + U(w.region) + '@' + issueHead(w.issue)] || null;
    w.regulatory = fs ? {
      id: fs.id, act: fs.regulatoryAct, actState: fs.regulatoryActState,
      regulatoryWindow: fs.regulatoryWindow, monitoringWindow: fs.monitoringWindow,
      applicationWindow2026: fs.applicationWindow2026, nextImportantWindow: fs.nextImportantWindow,
      preparationWindow: fs.preparationWindow, coverageState: fs.coverageState,
      languageState: fs.languageState, sourceId: fs.sourceId,
    } : null;
    /* OBSERVED_STAGE is a narrative field upstream and is measured
       NOT_ESTABLISHED on 5 of the 7 rows; of the 2 real ones neither belongs to
       a canonical region. So this is null 29/29 today — deliberately, and
       without a placeholder. */
    w.observedStage = fs && fs.observedStage && fs.observedStage.state === KNOWLEDGE.CLEAR ? fs.observedStage : null;
    /* Three honest coverage levels, derived only from what is present. */
    w.coverageState = w.observedStage ? 'FIELD_OBSERVED' : w.regulatory ? 'REGULATORY_READ' : 'EXPECTED_NORM_ONLY';
  });

  /* ---- CROP ECONOMIC WEIGHT --------------------------------------------- */
  const cropEconomicWeight = build('cropEconomicWeight', [
    V21('cropEconomicWeight'),
    {
      source: 'ITALY_INGEST.CROPS',
      precedence: P.REAL_SOURCE,
      rows: RAW.IG.CROPS,
      adapt: (c) => ({
        id: c.ID,
        crop: S(c.CROP_TERM),
        productsMentioning: N(c.PRODUCTS_MENTIONING_CROP),
        productsWithUseRow: N(c.PRODUCTS_WITH_USE_ROW_READ),
        distance: S(c.DISTANCE),
        reading: S(c.READING),
        provenance: provOf(c, P.REAL_SOURCE),
        raw: c,
      }),
      validate: (r) => (!r.crop ? 'no crop term' : null),
    },
  ], 'label-corpus reach per crop; not a market size');

  /* ---- PRODUCTS · regulatory + commercial ------------------------------- */
  const productsRegulatory = build('productsRegulatory', [
    V21('productsRegulatory'),
    {
      source: 'ITALY_INGEST.PRODUCTS',
      precedence: P.REAL_SOURCE,
      rows: RAW.IG.PRODUCTS,
      adapt: (p) => ({
        id: p.id, name: S(p.name), reg: S(p.reg), holder: S(p.holder),
        ai: A(p.ai), form: S(p.form), regCat: S(p.regCat), line: S(p.line),
        status: S(p.status), expiry: S(p.expiry),
        hrac: A(p.hrac), frac: A(p.frac), irac: A(p.irac),
        crops: A(p.crops), targets: A(p.targets),
        labelUrl: S(p.labelUrl), catalogUrl: S(p.catalogUrl), catalogCat: S(p.catalogCat),
        expiresInDays: daysFrom(p.expiry),
        provenance: provOf(p, P.REAL_SOURCE), raw: p,
      }),
      validate: (r) => (!r.name ? 'no product name' : null),
    },
  ], 'official Italian phytosanitary registration records');

  const productsCommercial = build('productsCommercial', [
    V21('productsCommercial'),
    {
      source: 'ITALY_CATALOG.ITEMS',
      precedence: P.REAL_SOURCE,
      rows: RAW.CATALOG.ITEMS || RAW.CATALOG.PRODUCTS,
      adapt: (p) => ({
        id: 'CAT-' + U(p.name), name: S(p.name), category: S(p.category),
        matchState: S(p.matchState), regId: S(p.regId), reg: S(p.reg),
        holder: S(p.holder), ai: A(p.ai), line: S(p.line),
        status: S(p.status), expiry: S(p.expiry), catalogUrl: S(p.catalogUrl),
        note: S(p.note), provenance: P.REAL_SOURCE, raw: p,
      }),
      validate: (r) => (!r.name ? 'no product name' : null),
    },
  ], 'reconstructed public commercial catalog');

  /* ---- PRODUCT RELATIONSHIPS · §19 -------------------------------------
     ONE truth contract, with a declared precedence:

       HANDOFF V2.1 canonical relationship
         > verified label verdict (the 163-label audit)
         > registry label-use row (real, authorises product x crop x target)
         > LABEL_CHECK_NEEDED

     The demo case fixture is NOT a source here. Measured: of the 80 links the
     fixture asserted, 13 were audited VERIFIED, 14 audited NOT_FOUND and 53
     were never audited at all — of those 53, only 4 are corroborated by a
     registry label-use row and 31 name a product absent from the registry.
     Those 31 existed only because a fixture said so. */
  const STRENGTH = {
    VERIFIED_LABEL_MATCH: { key: 'VERIFIED_LABEL_MATCH', rank: 0, color: '#00B152' },
    RELATED_PORTFOLIO: { key: 'RELATED_PORTFOLIO', rank: 1, color: '#5CC3EE' },
    LABEL_CHECK_NEEDED: { key: 'LABEL_CHECK_NEEDED', rank: 2, color: '#F5B317' },
    NO_CONFIRMED_MATCH_CURRENT_READING: { key: 'NO_CONFIRMED_MATCH_CURRENT_READING', rank: 3, color: '#B1A9A7' },
  };
  const ABSENCE_RULE = ABSENCE_RULE_TEXT;

  /* THE AUDIT ITSELF, published as data. No screen should ever hand-maintain a
     portfolio number again: the counts, the audit date, the scope note and the
     absence rule all come from here. */
  const labelVerdicts = coll(
    LV_VERIFIED.concat(LV_NOT_FOUND).map((v, i) => ({
      id: 'LV-' + String(i + 1).padStart(3, '0'),
      crop: v.crop, issue: v.issue, product: v.product,
      strength: v.strength,
      strengthRank: STRENGTH[v.strength].rank,
      verified: v.strength === 'VERIFIED_LABEL_MATCH',
      auditDate: S(RAW.LABEL_AUDIT.AUDIT_DATE),
      auditSource: S(RAW.LABEL_AUDIT.AUDIT_SOURCE),
      absenceRule: ABSENCE_RULE_TEXT,
      provenance: P.CANONICAL,
    })),
    P.CANONICAL,
    'the label audit exactly as the auditor left it; a not-found verdict always travels with the absence rule',
    { source: 'ITALY_LABEL_VERDICTS' }
  );
  Object.assign(labelVerdicts, {
    verified: LV_VERIFIED.map((v) => ({ crop: v.crop, issue: v.issue, product: v.product })),
    notFound: LV_NOT_FOUND.map((v) => ({ crop: v.crop, issue: v.issue, product: v.product })),
    verifiedCount: LV_VERIFIED.length,
    notFoundCount: LV_NOT_FOUND.length,
    assessedCount: LV_VERIFIED.length + LV_NOT_FOUND.length,
    verifiedProducts: uniq(LV_VERIFIED.map((v) => v.product)),
    auditDate: S(RAW.LABEL_AUDIT.AUDIT_DATE),
    auditSource: S(RAW.LABEL_AUDIT.AUDIT_SOURCE),
    scopeNote: S(RAW.LABEL_AUDIT.SCOPE_NOTE),
    absenceRule: ABSENCE_RULE_TEXT,
    STRENGTH,
    /* The audit is keyed crop|issue|product. Asking it about anything else
       returns LABEL_CHECK_NEEDED, which is the scope note stated as a value. */
    verdictFor: (crop, issue, product) => {
      const k = verdictKey(crop, issue);
      if ((verifiedByCropIssue[k] || []).some((p) => U(p) === U(product))) return 'VERIFIED_LABEL_MATCH';
      if ((notFoundByCropIssue[k] || []).some((p) => U(p) === U(product))) return 'NO_CONFIRMED_MATCH_CURRENT_READING';
      return 'LABEL_CHECK_NEEDED';
    },
  });

  /* Canonical windows indexed by crop + folded issue, so a relationship can name
     the window and the region it was audited against. A label is national — the
     region always comes from the window, never from the label. */
  const windowByCropIssue = {};
  cropWindows.records.forEach((w) => { const k = verdictKey(w.crop, w.issue); if (!windowByCropIssue[k]) windowByCropIssue[k] = w; });

  const relRows = [];
  const relKey = (crop, issue, product) => [U(crop), U(issue), U(product)].join('|');
  const seenRel = {};
  const pushRel = (crop, issue, product, strength, evidence, source, extra) => {
    const k = relKey(crop, issue, product);
    const prev = seenRel[k];
    if (prev && STRENGTH[prev.strength].rank <= STRENGTH[strength].rank) return;
    const w = windowByCropIssue[verdictKey(crop, issue)] || null;
    const row = Object.assign({
      id: k, crop: S(crop), issue: S(issue), product: S(product),
      productKey: U(product),
      strength, strengthRank: STRENGTH[strength].rank,
      evidence: S(evidence), source: S(source),
      /* A relationship that lands on a canonical window carries its id, region
         and issue type. Anchor says which of the two happened, so an orphan row
         is visibly an orphan instead of a row with three empty columns. */
      windowId: w ? w.windowId : null,
      legacyCaseId: w ? w.legacyCaseId : null,
      region: w ? w.region : null,
      issueType: w ? w.issueType : null,
      anchor: w ? 'CANONICAL_WINDOW' : 'NO_CANONICAL_WINDOW',
      auditDate: S(RAW.LABEL_AUDIT.AUDIT_DATE),
      auditSource: S(RAW.LABEL_AUDIT.AUDIT_SOURCE),
      absenceRule: ABSENCE_RULE_TEXT,
      target: null, reg: null, labelUrl: null, moaLabel: null, mappingRule: null,
      provenance: P.CANONICAL,
    }, extra || {});
    if (prev) { relRows[relRows.indexOf(prev)] = row; } else { relRows.push(row); }
    seenRel[k] = row;
  };
  /* 1 · the audit's own verdicts */
  LV_VERIFIED.forEach((v) => pushRel(v.crop, v.issue, v.product, 'VERIFIED_LABEL_MATCH', 'Read on the official label', RAW.LABEL_AUDIT.AUDIT_SOURCE, { evidenceKind: 'LABEL_AUDIT' }));
  LV_NOT_FOUND.forEach((v) => pushRel(v.crop, v.issue, v.product, 'NO_CONFIRMED_MATCH_CURRENT_READING', 'Not found in this label reading', RAW.LABEL_AUDIT.AUDIT_SOURCE, { evidenceKind: 'LABEL_AUDIT' }));
  /* 2 · registry label-use rows. A row proves the product is authorised on the
     crop against that target — a real relationship, weaker than a read verdict
     because the issue vocabularies are not the same list: the registry names a
     Latin target, the window names an English issue. The row therefore keeps
     the Latin target as its issue and never pretends to be an issue match. */
  const moaLabelOf = (moa) => {
    if (!moa || typeof moa !== 'object') return null;
    const parts = Object.keys(moa).map((k) => (A(moa[k]).length ? k + ' ' + A(moa[k]).join('/') : null)).filter(Boolean);
    return parts.length ? parts.join(' + ') : null;
  };
  A(RAW.IG.LINKS).forEach((l) => {
    const crop = cropFromCode(l.crop) || S(l.cropTerm) || S(l.crop);
    pushRel(crop, l.target, l.product, 'RELATED_PORTFOLIO', 'Authorised use row in the national registry', l.labelUrl, {
      evidenceKind: 'REGULATORY_USE_ROW',
      target: S(l.target), reg: S(l.reg), labelUrl: S(l.labelUrl),
      moaLabel: moaLabelOf(l.moa),
      mappingRule: 'CROP_KEY:' + U(l.crop),
      provenance: P.REAL_SOURCE,
    });
  });
  const productRelationships = coll(relRows, P.CANONICAL,
    'product relationships from the label audit and the national registry; the demo case fixture is not a source',
    { source: 'ITALY_LABEL_VERDICTS + ITALY_INGEST.LINKS' });

  /* ---- REGULATORY LINKS · the 219 authorised use rows -------------------
     The only fully-populated relationship table in the package, and the model
     never exposed it. It is a DIFFERENT fact from 'positions assessed by the
     audit' (19) and from 'verified matches' (12); a screen that shows this
     count must say 'righe d'uso lette dalle etichette', not 'links'.

     Its timing column is the analyst's unknown sentence on 219/219 rows, so it
     is routed through the same guard as any other prose: an unread label column
     must render as unknown, never as an application window. */
  const regulatoryLinks = build('regulatoryLinks', [
    V21('regulatoryLinks'),
    {
      source: 'ITALY_INGEST.LINKS',
      precedence: P.REAL_SOURCE,
      rows: RAW.IG.LINKS,
      adapt: (l) => ({
        id: l.id,
        crop: S(l.cropTerm) || S(l.crop),
        cropCode: U(l.crop),
        cropKey: cropFromCode(l.crop),
        cropKeys: cropsFromCode(l.crop),
        target: S(l.target),
        product: S(l.product), productKey: U(l.product),
        reg: S(l.reg), ai: A(l.ai), moa: l.moa || null, moaLabel: moaLabelOf(l.moa),
        doses: A(l.doses), interval: S(l.interval),
        /* narrative() would also work here, but timing has no localized slot
           upstream; UNK states the same thing without inventing one. */
        timing: UNK(l.timing),
        timingState: UNK(l.timing) ? KNOWLEDGE.CLEAR : KNOWLEDGE.NOT_ESTABLISHED,
        labelUrl: S(l.labelUrl),
        evidence: S(l.evidence),
        provenance: provOf(l, P.REAL_SOURCE),
        raw: l,
      }),
      validate: (r) => (!r.id ? 'no id' : !r.product ? 'no product' : null),
    },
  ], "authorised use rows read from official labels; MAX_APP is empty on every row and is not carried");

  Object.assign(regulatoryLinks, {
    byCrop: tallyBy(regulatoryLinks.records, (r) => r.cropKey || r.crop),
    byProduct: tallyBy(regulatoryLinks.records, (r) => r.product),
    byTarget: tallyBy(regulatoryLinks.records, (r) => r.target),
    timingKnownCount: regulatoryLinks.records.filter((r) => r.timing).length,
  });

  /* One row per crop key, for the panel that wants "what is authorised here".
     WHEAT_GENERIC is deliberately counted under both Wheat and Durum Wheat, and
     the overlap is declared on the row rather than resolved silently. */
  const portfolioLinksByCrop = (() => {
    const acc = {};
    regulatoryLinks.records.forEach((r) => {
      const keys = r.cropKeys.length ? r.cropKeys : [r.crop];
      keys.forEach((k) => {
        const e = acc[k] = acc[k] || { id: 'PLC-' + U(k), cropKey: k, linkCount: 0, products: [], targets: [], labels: {}, sharedGenericRows: 0, provenance: P.REAL_DERIVED };
        e.linkCount++;
        if (r.product && e.products.indexOf(r.product) < 0) e.products.push(r.product);
        if (r.target && e.targets.indexOf(r.target) < 0) e.targets.push(r.target);
        if (r.product && r.labelUrl && !e.labels[r.product]) e.labels[r.product] = r.labelUrl;
        if (r.cropKeys.length > 1) e.sharedGenericRows++;
      });
    });
    const rows = Object.keys(acc).sort().map((k) => {
      const e = acc[k];
      e.productCount = e.products.length;
      e.note = e.sharedGenericRows
        ? e.sharedGenericRows + " of these rows come from the generic 'Frumento' label and are counted for both wheat keys"
        : null;
      return e;
    });
    return coll(rows, P.REAL_DERIVED, 'authorised use rows grouped by crop key; the generic-wheat overlap is declared, not hidden', { source: 'derived · regulatoryLinks' });
  })();

  /* ---- the joined product entity --------------------------------------- */
  const byName = {};
  const addProduct = (name, patch) => {
    const k = U(name);
    if (!k) return;
    byName[k] = Object.assign({ name: String(name).trim(), key: k, regulatory: null, commercial: null, links: [] }, byName[k], patch);
  };
  productsRegulatory.records.forEach((p) => addProduct(p.name, {
    regulatory: p, line: p.line, ai: p.ai, targets: p.targets, crops: p.crops,
    labelUrl: p.labelUrl, status: p.status, expiry: p.expiry, provenance: P.REAL_SOURCE,
  }));
  productsCommercial.records.forEach((p) => addProduct(p.name, {
    commercial: p, category: p.category, catalogUrl: p.catalogUrl,
    matchState: p.matchState, provenance: P.REAL_SOURCE,
  }));
  /* Relationships attach to the product entity from the relationship
     collection — never from a case fixture. */
  productRelationships.records.forEach((r) => {
    const e = byName[U(r.product)];
    if (e) e.links.push({ crop: r.crop, issue: r.issue, strength: r.strength, evidence: r.evidence, source: r.source });
  });
  const CATEGORY_OF = (e) => {
    const c = U(e.category);
    if (c) return c;
    const line = U(e.line);
    return line === 'HERBICIDA' ? 'ERBICIDI'
      : line === 'FUNGICIDA' ? 'FUNGICIDI'
      : line === 'INSETICIDA' || line === 'INSETTICIDA' ? 'INSETTICIDI'
      : line === 'OUTRA' || line === 'SPECIALE' ? 'SPECIALI' : '';
  };
  const products = Object.keys(byName).sort().map((k) => {
    const e = byName[k];
    return Object.assign(e, {
      categoryLabel: CATEGORY_OF(e),
      inRegulatory: !!e.regulatory,
      inCommercial: !!e.commercial,
      verifiedLinks: e.links.filter((l) => l.strength === 'VERIFIED_LABEL_MATCH'),
      relatedLinks: e.links.filter((l) => l.strength === 'RELATED_PORTFOLIO'),
      checkNeededLinks: e.links.filter((l) => l.strength === 'LABEL_CHECK_NEEDED'),
      rejectedLinks: e.links.filter((l) => l.strength === 'NO_CONFIRMED_MATCH_CURRENT_READING'),
      /* Sales, stock and share are not observable from outside. Saying so is
         the honest answer, not a gap to be filled later by private data. */
      commercialPerformance: P.NOT_OBSERVABLE,
    });
  });
  const productByKey = {};
  products.forEach((p) => { productByKey[p.key] = p; });
  const productsColl = coll(products, P.REAL_SOURCE, 'regulatory registry joined to the public commercial catalog');
  const findProduct = (name) => productByKey[U(name)] || null;
  const strengthFor = (name, crop, issue) => {
    const row = seenRel[relKey(crop, issue, name)];
    if (row) return row.strength;
    const e = productByKey[U(name)];
    if (e && e.links.some((l) => U(l.crop) === U(crop))) return 'LABEL_CHECK_NEEDED';
    return 'NO_CONFIRMED_MATCH_CURRENT_READING';
  };

  /* ---- COMPETITOR ------------------------------------------------------- */
  const competitorActivities = build('competitorActivities', [
    V21('competitorActivities'),
    {
      source: 'ITALY_INGEST.COMP_ACTIVITIES',
      precedence: P.REAL_SOURCE,
      rows: RAW.IG.COMP_ACTIVITIES,
      adapt: (a) => {
        const paid = U(a.type) === 'PAID';
        const sem = U(a.countrySem);
        /* Italy reach is an OBSERVATION, never a targeting claim. Organic,
           multi-country and country-null records are not called observed in
           Italy just because the corpus is an Italian one. */
        const italyReach = paid && (sem.indexOf('IT') >= 0 || U(a.country).indexOf('IT') >= 0);
        /* A crop term resolves ONLY through the botanical identity table. The
           advertiser's own umbrella words (colture, cereali, frutta, ortaggi)
           are recognised so they can be reported as generic — never promoted
           to a crop. Measured: 132 of 503 activities resolve to a crop, 51
           carry only an umbrella word, 320 carry no crop term at all. */
        const cropsCanonical = uniq(A(a.crops).map((c) => CROP_BY_LATIN[U(c)] || null));
        const generic = A(a.crops).filter((c) => GENERIC_CROP_TERMS[U(c)]);
        const issues = A(a.issues).filter(Boolean);
        /* SPECIES only when the advertiser wrote a capitalised Latin genus or
           binomial. Measured: the 14 distinct issue terms split cleanly — the
           species terms are capitalised (Plasmopara viticola, Fusarium,
           Zymoseptoria tritici) and the advertiser's own category words are
           lower-case Italian (insetti, malattie, infestanti, funghi,
           parassiti). Capitalisation is the source's own signal here, not an
           inference about biology. */
        const speciesIssues = issues.filter((i) => /^[A-Z][a-z]/.test(String(i).trim()));
        const hasDate = !!S(a.start);
        return {
          id: a.id, type: S(a.type), platform: S(a.platform),
          company: S(a.company), companyRaw: S(a.companyRaw),
          companyKey: U(a.company),
          page: S(a.page), pageId: S(a.pageId),
          /* The observed page name is a real field; the company name is a
             normalization of it. When no page was observed the card must say
             so rather than borrow the company name silently. */
          displayName: S(a.page) || S(a.company),
          channelResolved: !!S(a.page),
          country: S(a.country), countrySem: S(a.countrySem),
          geoClass: italyReach ? 'REACHED_IN_ITALY' : paid ? 'REACH_NOT_RESOLVED' : 'MULTI_COUNTRY_OR_UNRESOLVED',
          italyReach,
          /* §9 · reach is not targeting. The caveat is the advertiser platform's
             own sentence and travels with the record so no card can drop it. */
          geoCaveat: S(a.countrySem),
          startDate: S(a.start), endDate: S(a.end),
          /* active is an upstream enum (ACTIVE / INACTIVE / NOT_KNOWN / null),
             so it is kept as the enum. Coercing it to a boolean made 89 records
             with no observation read as 'not active'. */
          active: S(a.active),
          isActive: U(a.active) === 'ACTIVE',
          media: S(a.media), products: A(a.products), crops: A(a.crops), issues: issues,
          cropsCanonical,
          cropScope: cropsCanonical.length ? 'RESOLVED' : generic.length ? 'GENERIC_TERM' : 'NOT_OBSERVED',
          genericCropTerms: generic,
          issuesObserved: issues,
          issueScope: speciesIssues.length ? 'SPECIES' : issues.length ? 'GENERIC_TERM' : 'NOT_OBSERVED',
          speciesIssues,
          /* The advertiser's own public copy. Shown as a quoted excerpt and
             never parsed for a crop, an issue, a product or a claim. */
          text: S(a.text), textExcerpt: S(a.text), url: S(a.url),
          hasDate,
          dateState: hasDate ? 'OBSERVED' : 'NOT_OBSERVED',
          daysFromRef: daysFrom(a.start),
          provenance: provOf(a, P.REAL_SOURCE), raw: a,
        };
      },
      validate: (r) => (!r.id ? 'no id' : !r.company ? 'no company' : null),
    },
  ], 'observed public competitor communication; Italy reach only where the evidence supports it');

  /* Recency, computed ONCE against the single reference date. Each screen
     re-deriving its own window is exactly how two screens ended up disagreeing
     about the same week. The undated count is published beside them, because
     17.7% of the corpus can never enter a recency figure at all. */
  const compRecent = (days) => competitorActivities.records.filter((r) => r.daysFromRef !== null && r.daysFromRef <= 0 && r.daysFromRef >= -days);
  Object.assign(competitorActivities, {
    recent30: compRecent(30).length,
    recent7: compRecent(7).length,
    undatedCount: competitorActivities.records.filter((r) => !r.hasDate).length,
    italyReachCount: competitorActivities.records.filter((r) => r.geoClass === 'REACHED_IN_ITALY').length,
    activeCount: competitorActivities.records.filter((r) => r.isActive).length,
    cropResolvedCount: competitorActivities.records.filter((r) => r.cropScope === 'RESOLVED').length,
    cropGenericCount: competitorActivities.records.filter((r) => r.cropScope === 'GENERIC_TERM').length,
    cropNotObservedCount: competitorActivities.records.filter((r) => r.cropScope === 'NOT_OBSERVED').length,
  });

  /* ---- COMPETITOR COMPANIES · merged --------------------------------------
     The upstream table has 14 rows for 11 companies: the paid rows are
     title-case ('Bayer') and the organic rows upper-case ('BAYER'). Summing the
     raw table counts three companies twice. The merge happens once, here, so
     the company strip and the company page cannot disagree. */
  const compActByCompany = {};
  competitorActivities.records.forEach((a) => { (compActByCompany[a.companyKey] = compActByCompany[a.companyKey] || []).push(a); });

  const competitorCompanies = build('competitorCompanies', [
    V21('competitorCompanies'),
    {
      source: 'ITALY_INGEST.COMP_COMPANIES · merged on upper-case name',
      precedence: P.REAL_SOURCE,
      rows: (() => {
        const acc = {};
        A(RAW.IG.COMP_COMPANIES).forEach((c) => {
          const k = U(c.COMPANY);
          const e = acc[k] = acc[k] || { key: k, ids: [], name: null, paid: 0, organic: 0, pages: [], productsProved: [] };
          e.ids.push(S(c.ID));
          /* The display name comes from the ACTIVITY corpus, which is the
             observation; the counter table's upper-case organic row is a
             corpus artefact of how the two feeds were tallied. */
          if (!e.name) e.name = (compActByCompany[k] && compActByCompany[k][0] && compActByCompany[k][0].company) || S(c.COMPANY);
          e.paid += N(c.PAID_ADS_REACHING_IT) || 0;
          e.organic += N(c.ORGANIC_VIDEOS_IN_CORPUS) || 0;
          e.pages = uniq(e.pages.concat(A(c.PAGES)));
          e.productsProved = uniq(e.productsProved.concat(A(c.PRODUCTS_PROVED)));
        });
        return Object.keys(acc).sort((x, y) => (acc[y].paid + acc[y].organic) - (acc[x].paid + acc[x].organic)).map((k) => acc[k]);
      })(),
      adapt: (e) => {
        const acts = compActByCompany[e.key] || [];
        const dates = acts.map((a) => a.startDate).filter(Boolean);
        return {
          id: e.ids[0], mergedIds: e.ids, key: e.key,
          name: e.name, company: e.name,
          paidAdsReachingIt: e.paid,
          organicVideosInCorpus: e.organic,
          organicVideos: e.organic,
          /* observedTotal is the merged counter; observedActivities is the
             count of rows actually in the activity corpus. Publishing both is
             what makes a divergence visible instead of silent. */
          observedTotal: e.paid + e.organic,
          observedActivities: acts.length,
          pages: e.pages,
          pagesObserved: e.pages.length,
          productsProved: e.productsProved,
          firstObserved: minIso(dates), lastObserved: maxIso(dates),
          datedActivities: dates.length,
          observedLast30: acts.filter((a) => a.daysFromRef !== null && a.daysFromRef <= 0 && a.daysFromRef >= -30).length,
          activeAds: acts.filter((a) => a.isActive).length,
          cropsObserved: uniq(acts.flatMap((a) => a.cropsCanonical)),
          provenance: P.REAL_DERIVED,
        };
      },
      validate: (r) => (!r.name ? 'no company name' : null),
    },
  ], 'companies observed in the monitored public communication corpus, merged on upper-case name');

  const competitorProducts = build('competitorProducts', [
    V21('competitorProducts'),
    {
      source: 'ITALY_INGEST.COMP_PRODUCTS',
      precedence: P.REAL_SOURCE,
      rows: RAW.IG.COMP_PRODUCTS,
      adapt: (p) => {
        /* The per-product context is derived from the activities that actually
           name the product, so the count on the company card and the count on
           the product page come from the same array. */
        const acts = competitorActivities.records.filter((a) => a.products.some((x) => U(x) === U(p.PRODUCT)));
        const dates = acts.map((a) => a.startDate).filter(Boolean);
        return {
          id: p.ID, name: S(p.PRODUCT), product: S(p.PRODUCT), company: S(p.COMPANY),
          companyKey: U(p.COMPANY),
          adsReachingIt: N(p.ADS_REACHING_IT), proof: S(p.PROOF),
          activityIds: acts.map((a) => a.id), activityCount: acts.length,
          cropsObserved: uniq(acts.flatMap((a) => a.cropsCanonical)),
          issuesObserved: uniq(acts.flatMap((a) => a.issuesObserved)),
          firstSeen: minIso(dates), lastSeen: maxIso(dates),
          provenance: provOf(p, P.REAL_SOURCE), raw: p,
        };
      },
      validate: (r) => (!r.name ? 'no product name' : null),
    },
  ], 'competitor products named in observed public communication; reach in Italy, never targeting');

  /* Attach the product records to the company rows AFTER both exist, so a
     company with zero proven products is visibly zero rather than absent. */
  competitorCompanies.records.forEach((c) => {
    c.products = competitorProducts.records.filter((p) => p.companyKey === c.key);
    c.productCount = c.products.length;
    c.productState = c.productCount ? 'PRODUCTS_PROVED' : 'NO_PRODUCT_PROVED_CURRENT_READING';
  });

  /* ---- COMPETITOR · derived density and matrix -------------------------
     Every number below is a count of observed items. None of them is a share,
     a level or a verdict: the corpus covers what it covers, and the denominator
     travels with the row so a bar can never be read as a market. */
  const competitorCropDensity = (() => {
    const acc = {};
    competitorActivities.records.forEach((a) => a.cropsCanonical.forEach((c) => {
      const e = acc[c] = acc[c] || { id: 'CCD-' + U(c), crop: c, items: 0, companyKeys: [], provenance: P.REAL_DERIVED };
      e.items++;
      if (e.companyKeys.indexOf(a.companyKey) < 0) e.companyKeys.push(a.companyKey);
    }));
    const rows = Object.keys(acc).map((k) => acc[k]).sort((x, y) => y.items - x.items);
    const max = rows.length ? rows[0].items : 0;
    rows.forEach((r) => { r.companies = r.companyKeys.length; r.sharePct = max ? Math.round((r.items / max) * 100) : 0; });
    const c = coll(rows, P.REAL_DERIVED, 'observed items per resolved crop; sharePct is a bar length relative to the largest row, never a market share', { source: 'derived · competitorActivities' });
    return Object.assign(c, {
      maxItems: max,
      unresolvedItems: competitorActivities.cropNotObservedCount,
      genericItems: competitorActivities.cropGenericCount,
      denominator: competitorActivities.count,
    });
  })();

  const competitorIssueDensity = (() => {
    const acc = {};
    competitorActivities.records.forEach((a) => a.issuesObserved.forEach((i) => {
      const e = acc[i] = acc[i] || { id: 'CID-' + U(i), issue: i, issueScope: a.speciesIssues.indexOf(i) >= 0 ? 'SPECIES' : 'GENERIC_TERM', items: 0, companies: [], provenance: P.REAL_DERIVED };
      e.items++;
      if (e.companies.indexOf(a.company) < 0) e.companies.push(a.company);
    }));
    const rows = Object.keys(acc).map((k) => acc[k]).sort((x, y) => y.items - x.items);
    const c = coll(rows, P.REAL_DERIVED, "issue terms exactly as the advertiser published them; never translated, never truncated", { source: 'derived · competitorActivities' });
    return Object.assign(c, { coveredActivities: competitorActivities.records.filter((a) => a.issuesObserved.length).length, denominator: competitorActivities.count });
  })();

  const competitorMatrix = (() => {
    const columns = competitorCropDensity.records.map((r) => r.crop);
    let maxCell = 0;
    const rows = competitorCompanies.records.map((c) => {
      const acts = compActByCompany[c.key] || [];
      const cells = columns.map((crop) => {
        const n = acts.filter((a) => a.cropsCanonical.indexOf(crop) >= 0).length;
        if (n > maxCell) maxCell = n;
        return { crop, n };
      });
      return { id: 'CMX-' + c.key, company: c.name, companyKey: c.key, cells, total: cells.reduce((s, x) => s + x.n, 0), provenance: P.REAL_DERIVED };
    });
    const c = coll(rows, P.REAL_DERIVED, 'company x crop counts over the observed corpus; the dot ramp is computed from maxCell, never hard-coded', { source: 'derived · competitorActivities' });
    return Object.assign(c, {
      columns, maxCell,
      /* A company with no crop-resolved activity is not an empty row to hide:
         it is a measured fact about what the corpus does and does not say. */
      allZeroCompanies: rows.filter((r) => r.total === 0).map((r) => r.company),
    });
  })();

  /* The communication axis as PUBLISHED, before any canonical resolution: the
     advertiser's own vocabulary with its own counts. It exists so the density
     strip can be honest about mixing species and umbrella words. */
  const communicationAxis = (() => {
    const t = tallyBy(competitorActivities.records, (a) => a.crops);
    const rows = byCountDesc(t).map((k) => ({
      id: 'AXIS-' + U(k), key: k, label: k, count: t[k],
      canonical: CROP_BY_LATIN[U(k)] || null,
      scope: CROP_BY_LATIN[U(k)] ? 'SPECIES' : GENERIC_CROP_TERMS[U(k)] ? 'GENERIC_TERM' : 'UNMAPPED',
      provenance: P.REAL_DERIVED,
    }));
    const c = coll(rows, P.REAL_DERIVED, 'crop terms exactly as the advertiser published them; generic Italian buckets are never merged into a species row', { source: 'derived · competitorActivities' });
    return Object.assign(c, {
      coveredActivities: competitorActivities.records.filter((a) => a.crops.length).length,
      denominator: competitorActivities.count,
    });
  })();

  /* ---- MARKET ----------------------------------------------------------- */
  const marketObservations = build('marketObservations', [
    V21('marketObservations'),
    {
      source: 'ITALY_INGEST.MARKET',
      precedence: P.REAL_SOURCE,
      rows: RAW.IG.MARKET,
      adapt: (m) => {
        /* REFERENCE_PERIOD is 'dd/mm/yyyy..dd/mm/yyyy' on 77/77 rows. Parsing
           it here means no screen ever calls new Date() to know how old a
           quote is (§6). */
        const per = String(m.REFERENCE_PERIOD || '').split('..');
        const periodStart = dmyToIso(per[0]);
        const periodEnd = dmyToIso(per[1] || per[0]);
        /* The crop behind a price series is a declared lookup, never a guess:
           PRODUCT is a series code ('BLTPAN|PAN'), not a crop name. Anything the
           table does not cover stays null and is never attached to a crop. */
        const seriesKey = U(m.GROUP) + '|' + (m.PRODUCT === null || m.PRODUCT === undefined ? '' : String(m.PRODUCT));
        const cropKey = MARKET_CROP[seriesKey] || MARKET_CROP[U(m.GROUP) + '|*'] || null;
        /* SERIES_STATE is either CORRENTE or PARADA_EM_YYYY. A stopped series
           carries a last quote that is NOT today's price; the year is parsed out
           so no view can render one as current. */
        const stopped = /^PARADA_EM_(\d{4})$/.exec(U(m.SERIES_STATE));
        return {
          id: m.ID, group: S(m.GROUP), product: S(m.PRODUCT), market: S(m.MARKET),
          priceRaw: S(m.PRICE_RAW), price: N(m.PRICE_NUM), unit: S(m.UNIT), stage: S(m.STAGE),
          referencePeriod: S(m.REFERENCE_PERIOD), publicationDate: S(m.PUBLICATION_DATE),
          publicationDateISO: isoOf(m.PUBLICATION_DATE),
          geography: S(m.GEOGRAPHY),
          cropKey, seriesKey,
          periodStart, periodEnd,
          daysSinceObservation: periodEnd ? daysFrom(periodEnd) : null,
          isCurrentSeries: U(m.SERIES_STATE) === 'CORRENTE',
          stoppedYear: stopped ? Number(stopped[1]) : null,
          /* STAGE and PUBLICATION_DATE are present on only 40 of 77 rows, and
             the four observed stages are different points in the chain. Rows
             with different stages must never be averaged, so the flag is
             published rather than left for a screen to discover. */
          hasStage: !!S(m.STAGE),
          hasPublicationDate: !!S(m.PUBLICATION_DATE),
          prevPrice: N(m.PREV_PRICE_NUM), changeVsPrev: N(m.CHANGE_VS_PREV_PCT),
          yearAgoPrice: N(m.YEAR_AGO_PRICE_NUM), changeVsYearAgo: N(m.CHANGE_VS_YEAR_AGO_PCT),
          seriesState: S(m.SERIES_STATE), seriesWarning: S(m.SERIES_WARNING),
          observations: N(m.OBSERVATIONS_IN_SERIES), sourceId: S(m.SOURCE_ID),
          publishedDaysAgo: daysFrom(isoOf(m.PUBLICATION_DATE)),
          /* Routing metadata only (§4): the Market Pulse screen addresses crops
             by its own short key. Null where the mapping is not unambiguous. */
          ui: { marketCropKey: cropKey ? MARKET_VIEW_KEY[cropKey] || null : null },
          provenance: provOf(m, P.REAL_SOURCE), raw: m,
        };
      },
      validate: (r) => (!r.id ? 'no ID' : null),
    },
  ], 'real market price observations, each with its own series state; the wine row has no PRODUCT and resolves by GROUP alone');

  /* ---- SCIENCE ---------------------------------------------------------- */
  const scienceRecords = build('scienceRecords', [
    V21('scienceRecords'),
    {
      source: 'ITALY_INGEST.SCIENCE',
      precedence: P.REAL_SOURCE,
      rows: RAW.IG.SCIENCE,
      adapt: (r) => ({
        id: r.ID, title: S(r.TITLE), doi: S(r.DOI),
        author: S(r.AUTHOR), orcid: S(r.ORCID), institution: S(r.INSTITUTION),
        publishedAt: S(r.PUBLISHED_AT), date: S(r.PUBLISHED_AT),
        year: S(r.PUBLISHED_AT) ? String(r.PUBLISHED_AT).slice(0, 4) : null,
        venue: S(r.VENUE), materialType: S(r.MATERIAL_TYPE), materialRole: S(r.MATERIAL_ROLE),
        crop: S(r.CROP), issue: S(r.ISSUE), countryOfFact: S(r.COUNTRY_OF_FACT),
        url: S(r.SOURCE_URL), sourceId: S(r.SOURCE_ID),
        provenance: provOf(r, P.REAL_SOURCE), raw: r,
      }),
      validate: (r) => (!r.id ? 'no ID' : !r.title ? 'no title' : null),
    },
  ], 'real scientific records with a resolvable source');

  const researchers = build('researchers', [
    V21('researchers'),
    {
      source: 'ITALY_INGEST.RESEARCHERS',
      precedence: P.REAL_SOURCE,
      rows: RAW.IG.RESEARCHERS,
      adapt: (r) => ({
        id: r.ID, name: S(r.PERSON), category: S(r.CATEGORY),
        orcid: S(r.ORCID), openAlexId: S(r.OPENALEX_ID),
        org: S(A(r.INSTITUTIONS)[0]) || S(r.INSTITUTIONS),
        institutions: A(r.INSTITUTIONS),
        theme: S(r.THEME), worksInScope: N(r.WORKS_IN_SCOPE),
        lastActivity: S(r.LAST_ACTIVITY),
        /* Identity is stated by the source and never upgraded by the portal. */
        identityStatus: S(r.IDENTITY_STATUS),
        role: S(r.ROLE), factRegion: S(r.FACT_REGION),
        sourceId: S(r.SOURCE_ID),
        provenance: provOf(r, P.REAL_SOURCE), raw: r,
      }),
      validate: (r) => (!r.id ? 'no ID' : !r.name ? 'no person' : null),
    },
  ], 'real researcher identities; identity status is never promoted');

  const scienceThemes = build('scienceThemes', [
    V21('scienceThemes'),
    {
      source: 'ITALY_INGEST.THEMES',
      precedence: P.REAL_SOURCE,
      rows: RAW.IG.THEMES,
      adapt: (t) => ({
        id: t.ID, title: S(t.THEME), query: S(t.QUERY),
        works: N(t.WORKS), authorsIt: N(t.AUTHORS_IT),
        authorsWithOrcid: N(t.AUTHORS_WITH_ORCID), authorsActiveSince2024: N(t.AUTHORS_ACTIVE_SINCE_2024),
        topInstitutions: A(t.INSTITUTIONS_TOP), sourceId: S(t.SOURCE_ID),
        provenance: provOf(t, P.REAL_SOURCE), raw: t,
      }),
      validate: (r) => (!r.id ? 'no ID' : null),
    },
  ], 'bibliometric themes; a grouping for navigation, not a scientific conclusion');

  const resistance = build('resistance', [
    V21('resistance'),
    {
      source: 'ITALY_INGEST.RESISTANCE',
      precedence: P.REAL_SOURCE,
      rows: RAW.IG.RESISTANCE,
      adapt: (r) => ({
        id: r.ID,
        /* A taxonomic name is never truncated, including a parenthetical
           synonym: the synonym is part of the identification. */
        species: S(r.SPECIES), speciesIt: S(r.SPECIES_IT), family: S(r.FAMILY),
        mechanism: narrative(r, 'MECHANISM'),
        mechanismStated: !!S(r.MECHANISM) && !UNKNOWN_SENTINEL.test(S(r.MECHANISM)),
        crop: S(r.CROP_DECLARED), firstCaseYear: S(r.FIRST_CASE_YEAR),
        regions: A(r.REGIONS), multiple: !!r.MULTIPLE_RESISTANCE,
        citation: S(r.CITATION), authority: S(r.AUTHORITY),
        url: S(r.SOURCE_URL), sourceId: S(r.SOURCE_ID),
        provenance: provOf(r, P.REAL_SOURCE), raw: r,
      }),
      validate: (r) => (!r.id ? 'no ID' : !r.species ? 'no species' : null),
    },
  ], 'confirmed Italian resistance cases');

  /* ---- PUBLIC VOICES ---------------------------------------------------- */
  const publicVoices = build('publicVoices', [
    V21('publicVoices'),
    {
      source: 'ITALY_INGEST.VOICES',
      precedence: P.REAL_SOURCE,
      rows: RAW.IG.VOICES,
      adapt: (v) => ({
        id: v.ID, kind: S(v.KIND),
        person: S(v.PERSON), identityState: STATE_TOKEN(v.PERSON_IDENTITY_STATE),
        /* 17/17 of ROLE, ORGANIZATION, DATE and REGION are the analyst's own
           "NAO SEI". Returning the sentence would print a Portuguese working
           note on an Italian screen; null lets the view render its own state. */
        role: UNK(v.ROLE), organization: UNK(v.ORGANIZATION),
        platform: S(v.PLATFORM), channel: S(v.CHANNEL), title: S(v.CONTENT_TITLE),
        date: UNK(v.DATE), dateRelative: S(v.DATE_RELATIVE),
        crop: S(v.CROP), issue: S(v.ISSUE), caseId: S(v.CASE_ID),
        region: UNK(v.REGION), countryOfFact: S(v.COUNTRY_OF_FACT),
        /* The original public quote is never translated and never parsed for
           facts. It is evidence, shown as published. */
        textOriginal: S(v.TEXT_ORIGINAL),
        proves: narrative(v, 'WHAT_IT_PROVES'),
        notProves: narrative(v, 'WHAT_IT_DOES_NOT_PROVE'),
        sourceUrl: S(v.SOURCE_URL), sourceId: S(v.SOURCE_ID),
        daysFromRef: daysFrom(v.DATE),
        provenance: provOf(v, P.REAL_SOURCE), raw: v,
      }),
      validate: (r) => (!r.id ? 'no ID' : null),
    },
  ], 'real public field voices; identity is never upgraded, the quote is never translated');

  const publicChannels = build('publicChannels', [
    V21('publicChannels'),
    {
      source: 'ITALY_INGEST.CHANNELS',
      precedence: P.REAL_SOURCE,
      rows: RAW.IG.CHANNELS,
      adapt: (c) => ({
        id: c.ID, name: S(c.CHANNEL), url: S(c.CHANNEL_URL),
        identityState: STATE_TOKEN(c.IDENTITY_STATE), contentTypeExample: S(c.CONTENT_TYPE_EXAMPLE),
        exampleTitle: S(c.EXAMPLE_TITLE), exampleUrl: S(c.EXAMPLE_URL),
        examplePublishedAt: S(c.EXAMPLE_PUBLISHED_AT), views: N(c.VIEWS),
        caseId: S(c.CASE_ID), provenance: provOf(c, P.REAL_SOURCE), raw: c,
      }),
      validate: (r) => (!r.id ? 'no ID' : null),
    },
  ], 'real Italian public channels');

  const publicPeople = build('publicPeople', [
    V21('publicPeople'),
    {
      source: 'ITALY_INGEST.PEOPLE',
      precedence: P.REAL_SOURCE,
      rows: RAW.IG.PEOPLE,
      adapt: (p) => ({
        id: p.ID, name: S(p.PERSON), category: S(p.CATEGORY),
        org: S(p.ORGANIZATION), role: S(p.ROLE),
        identityEvidence: S(p.IDENTITY_EVIDENCE), roleEvidence: S(p.ROLE_EVIDENCE),
        law: narrative(p, 'LAW'), country: S(p.COUNTRY),
        provenance: provOf(p, P.REAL_SOURCE), raw: p,
      }),
      validate: (r) => (!r.id ? 'no ID' : !r.name ? 'no person' : null),
    },
  ], 'public people with stated identity evidence');

  /* ---- SOURCES · EVENTS · NEWS ------------------------------------------ */
  const sources = build('sources', [
    V21('sources'),
    {
      source: 'ITALY_INGEST.SOURCES',
      precedence: P.REAL_SOURCE,
      rows: RAW.IG.SOURCES,
      adapt: (s) => ({
        id: s.ID || s.SOURCE_ID, sourceId: s.SOURCE_ID || s.ID,
        name: S(s.NAME), type: S(s.TYPE), role: narrative(s, 'ROLE'),
        roleCode: S(s.TYPE),
        country: S(s.COUNTRY), geography: S(s.GEOGRAPHY), url: S(s.URL),
        frequency: S(s.FREQUENCY), latestObservation: S(s.LATEST_OBSERVATION),
        accessStatus: S(s.ACCESS_STATUS), limitations: narrative(s, 'LIMITATIONS'),
        provenance: provOf(s, P.REAL_SOURCE), raw: s,
      }),
      validate: (r) => (!r.id ? 'no ID' : !r.name ? 'no name' : null),
    },
  ], 'traceable source registry');

  const futureEvents = build('futureEvents', [
    V21('futureEvents'),
    {
      source: 'ITALY_INGEST.EVENTS',
      precedence: P.REAL_SOURCE,
      rows: RAW.IG.EVENTS,
      adapt: (e) => ({
        id: e.ID, name: S(e.EVENT), date: S(e.DATE), location: S(e.LOCATION),
        sector: S(e.SECTOR), cropRelevance: A(e.CROP_RELEVANCE),
        organizer: S(e.ORGANIZER), url: S(e.OFFICIAL_URL),
        exhibitorListState: S(e.EXHIBITOR_LIST_STATE), timeState: S(e.TIME_STATE),
        /* Future participation is never inferred from past participation. */
        confirmedParticipation: A(e.CONFIRMED_PARTICIPATION),
        participationLaw: narrative(e, 'PARTICIPATION_LAW'),
        note: narrative(e, 'NOTE'),
        daysFromRef: daysFrom(e.DATE),
        provenance: provOf(e, P.REAL_SOURCE), raw: e,
      }),
      validate: (r) => (!r.id ? 'no ID' : !r.name ? 'no event name' : null),
    },
  ], 'real sector events');

  const news = build('news', [
    V21('news'),
    {
      source: 'ITALY_INGEST.NEWS',
      precedence: P.REAL_SOURCE,
      rows: RAW.IG.NEWS,
      adapt: (n) => ({
        id: n.ID, title: S(n.TITLE), publisher: S(n.PUBLISHER), outlet: S(n.PUBLISHER),
        author: S(n.AUTHOR), date: S(n.DATE),
        crop: S(n.CROP), issue: S(n.ISSUE), region: S(n.REGION),
        contentKind: S(n.CONTENT_KIND),
        contentKindMeaning: narrative(n, 'CONTENT_KIND_MEANING'),
        summary: narrative(n, 'SINTONIA_SUMMARY'),
        caveat: narrative(n, 'CAVEAT'),
        url: S(n.SOURCE_URL), daysFromRef: daysFrom(n.DATE),
        provenance: provOf(n, P.REAL_SOURCE), raw: n,
      }),
      validate: (r) => (!r.id ? 'no ID' : !r.title ? 'no title' : null),
    },
  ], 'real news and trade-media records');

  /* ---- FUTURE ----------------------------------------------------------- */
  const futureSignals = build('futureSignals', [
    V21('futureSignals'),
    {
      source: 'ITALY_INGEST.FUTURE_SIGNALS',
      precedence: P.REAL_SOURCE,
      rows: RAW.IG.FUTURE_SIGNALS,
      adapt: (f) => ({
        id: f.ID || f.SIGNAL_ID, legacyId: S(f.LEGACY_ID),
        /* REGION is 'NAO SEI ...' on 2 of 3 rows: the upstream scope is national
           affiliation, not study region. Null, never the Portuguese sentence. */
        crop: S(f.CROP), issue: S(f.ISSUE), region: UNK(f.REGION),
        status: S(f.STATUS),
        whoIsTalking: narrative(f, 'WHO_IS_TALKING'),
        whatChanged: narrative(f, 'WHAT_CHANGED'),
        whyWatch: narrative(f, 'WHY_WATCH'),
        howWeGotHere: narrative(f, 'HOW_SINTONIA_GOT_HERE'),
        observedFacts: narrative(f, 'OBSERVED_FACTS'),
        interpretation: narrative(f, 'SINTONIA_INTERPRETATION'),
        unknown: narrative(f, 'UNKNOWN'),
        nextWindow: narrative(f, 'NEXT_WINDOW'),
        portfolioConnection: narrative(f, 'PORTFOLIO_CONNECTION'),
        whatWouldPromoteIt: narrative(f, 'WHAT_WOULD_MAKE_IT_AN_OPPORTUNITY'),
        promotedToRadar: S(f.PROMOTED_TO_RADAR),
        sourceIds: A(f.SOURCE_IDS), evidenceIds: A(f.EVIDENCE_RECORD_IDS),
        confidence: S(f.CONFIDENCE),
        provenance: provOf(f, P.REAL_SOURCE), raw: f,
      }),
      validate: (r) => (!r.id ? 'no ID' : null),
    },
  ], 'upstream future signals with traceable evidence links');

  /* Generated presentation scenarios live OUTSIDE the real feed. They never
     count in real totals, source convergence or emerging-topic metrics. */
  const futureScenarios = coll(
    A(RAW.DEMO.SIGNALS).map((x) => Object.assign({}, x, { provenance: P.DEMO_SCENARIO })),
    P.DEMO_SCENARIO,
    'presentation scenarios; not evidence, never counted as real',
    { source: 'ITALY_DEMO.SIGNALS' }
  );

  /* ---- OPPORTUNITIES ---------------------------------------------------- */
  const windowByLegacyCase = {};
  cropWindows.records.forEach((w) => { if (w.legacyCaseId) windowByLegacyCase[U(w.legacyCaseId)] = w; });

  const opportunities = build('opportunities', [
    V21('opportunities'),
    {
      source: 'ITALY_INGEST.OPPORTUNITIES',
      precedence: P.REAL_SOURCE,
      rows: RAW.IG.OPPORTUNITIES,
      adapt: (o) => {
        const w = windowByLegacyCase[U(o.LEGACY_CASE_ID)] || null;
        return {
          id: o.ID, legacyCaseId: S(o.LEGACY_CASE_ID),
          title: S(o.TITLE), crop: S(o.CROP), region: S(o.REGION),
          issue: S(o.ISSUE), issueType: S(o.ISSUE_TYPE),
          caseLabel: S(o.CASE_LABEL), forbiddenLabel: S(o.FORBIDDEN_LABEL),
          whatIsHappening: narrative(o, 'WHAT_IS_HAPPENING'),
          whyItMatters: narrative(o, 'WHY_IT_MATTERS'),
          currentEvidence: narrative(o, 'CURRENT_EVIDENCE'),
          marketContext: narrative(o, 'MARKET_CONTEXT'),
          competitorContext: narrative(o, 'COMPETITOR_CONTEXT'),
          scienceContext: narrative(o, 'SCIENCE_CONTEXT'),
          fieldVoices: narrative(o, 'FIELD_VOICES'),
          whatWeKnow: narrative(o, 'WHAT_WE_KNOW'),
          whatWeDoNotKnow: narrative(o, 'WHAT_WE_DO_NOT_KNOW'),
          interpretations: narrative(o, 'INTERPRETATIONS'),
          adamaProducts: A(o.ADAMA_PRODUCTS),
          adamaActiveSubstance: A(o.ADAMA_ACTIVE_SUBSTANCE),
          windowText: S(o.WINDOW),
          /* The canonical window is a RELATION, not a promotion: it does not
             make anything else about the opportunity canonical. */
          canonicalWindow: w, windowId: w ? w.windowId : null,
          status: w ? w.status : null,
          sourceIds: A(o.SOURCE_IDS),
          ui: categoryOf(o.ISSUE_TYPE),
          provenance: provOf(o, P.REAL_SOURCE), raw: o,
        };
      },
      validate: (r) => (!r.id ? 'no ID' : !r.crop ? 'no crop' : null),
    },
  ], 'upstream opportunity intelligence; the real radar feed');

  /* The 29 legacy presentation cases. Kept ONLY as a labelled scenario mode,
     default off. A canonical window overlapping a case does not make the case
     real, so none of these is ever counted as an opportunity. */
  const opportunityScenarios = coll(
    A(RAW.DEMO.CASES).map((c) => {
      const w = windowByLegacyCase[U(c.id)] || null;
      return Object.assign({}, c, {
        canonicalWindow: w, windowId: w ? w.windowId : null,
        provenance: P.DEMO_SCENARIO, isScenario: true,
      });
    }),
    P.DEMO_SCENARIO,
    'presentation cases over canonical windows; never counted as real opportunities',
    { source: 'ITALY_DEMO.CASES' }
  );

  /* ---- REGULATORY FUTURE · AGROMET · CROSSINGS -------------------------
     No upstream table yet. An empty collection is a valid answer and is
     reported as empty rather than filled with invented rows. */
  const regulatoryFuture = build('regulatoryFuture', [V21('regulatoryFuture')], 'upcoming regulatory change; awaiting an upstream table');
  const agrometConditions = build('agrometConditions', [V21('agrometConditions')], 'agrometeorological conditions; awaiting an upstream table');
  const clientSafeCrossings = build('clientSafeCrossings', [V21('clientSafeCrossings')], 'audited cross-domain crossings; awaiting an upstream table');

  /* ---- RELATIONSHIPS · the generic graph -------------------------------
     A crossing exists only when a normalized relationship supports it. Sharing
     a crop name is not a relationship, so nothing is generated here from a
     name match. */
  const relationships = build('relationships', [
    V21('relationships'),
    {
      source: 'derived · window ↔ opportunity ↔ source',
      precedence: P.REAL_DERIVED,
      rows: opportunities.records.flatMap((o) => {
        const out = [];
        if (o.canonicalWindow) out.push({ from: o.id, fromKind: 'opportunity', to: o.canonicalWindow.windowId, toKind: 'window', kind: 'RELATED_CROP_WINDOW', evidence: 'canonical LEGACY_CASE_ID' });
        (o.sourceIds || []).forEach((sid) => out.push({ from: o.id, fromKind: 'opportunity', to: sid, toKind: 'source', kind: 'CITES_SOURCE', evidence: 'declared SOURCE_IDS' }));
        return out;
      }),
      adapt: (r) => Object.assign({ id: [r.fromKind, r.from, r.kind, r.to].join('|'), provenance: P.REAL_DERIVED }, r),
      validate: (r) => (!r.from || !r.to ? 'incomplete edge' : null),
    },
  ], 'declared relationships only; a shared crop name is never a relationship');

  /* ---- ARCHIVE · an index over the normalized model --------------------- */
  const arch = [];
  const push = (kind, id, title, date, source, url, crop, issue, prov) => {
    if (!id) return;
    arch.push({ id: kind + ':' + id, recordId: id, kind, type: kind, title: S(title), date: S(date), source: S(source), url: S(url), crop: S(crop), issue: S(issue), daysFromRef: daysFrom(date), provenance: prov });
  };
  scienceRecords.records.forEach((r) => push('SCIENCE', r.id, r.title, r.date, r.institution, r.url, r.crop, r.issue, r.provenance));
  marketObservations.records.forEach((m) => push('MARKET', m.id, [m.product, m.market].filter(Boolean).join(' · '), m.publicationDate, m.sourceId, null, m.product, null, m.provenance));
  competitorActivities.records.forEach((a) => push('COMPETITOR', a.id, [a.company, a.type].filter(Boolean).join(' · '), a.startDate, a.platform, a.url, a.crops[0], a.issues[0], a.provenance));
  publicVoices.records.forEach((v) => push('VOICE', v.id, v.title || v.person, v.date, v.platform, v.sourceUrl, v.crop, v.issue, v.provenance));
  futureEvents.records.forEach((e) => push('EVENT', e.id, e.name, e.date, e.location, e.url, null, null, e.provenance));
  news.records.forEach((n) => push('NEWS', n.id, n.title, n.date, n.publisher, n.url, n.crop, n.issue, n.provenance));
  cropWindows.records.forEach((w) => push('WINDOW', w.windowId, [w.issue, w.region].filter(Boolean).join(' · '), w.startDate, 'CANONICAL', null, w.crop, w.issue, w.provenance));
  resistance.records.forEach((r) => push('RESISTANCE', r.id, r.species, r.firstCaseYear, r.authority, r.url, r.crop, null, r.provenance));
  const archive = coll(arch, P.REAL_DERIVED, 'index over the normalized model; no manufactured rows', { source: 'derived' });

  /* ---- FIELD SALES · optional integration demonstration ----------------
     Outside the external-intelligence core. These records never mutate a core
     object and never contribute to a real count. */
  const fieldMessages = coll(
    A(RAW.DEMO.FIELD_MESSAGES).map((m) => Object.assign({}, m, { provenance: P.SYNTHETIC_DEMO })),
    P.SYNTHETIC_DEMO,
    'optional integration demonstration; never affects core intelligence',
    { source: 'ITALY_DEMO.FIELD_MESSAGES' }
  );

  /* ── 8 · THE COLLECTION SET ─────────────────────────────────────────────
     Every family the receiver is prepared to accept. An empty one is valid. */
  const collections = {
    /* products */
    productsRegulatory, productsCommercial, productRelationships,
    products: productsColl,
    /* agronomy */
    cropWindows, currentFieldSignals, cropEconomicWeight,
    /* market */
    marketObservations,
    /* competitor */
    competitorActivities, competitorCompanies, competitorProducts,
    /* science */
    scienceRecords, researchers, scienceThemes, resistance,
    /* voices */
    publicVoices, publicChannels, publicPeople,
    /* future */
    regulatoryFuture, agrometConditions, futureEvents,
    opportunities, futureSignals,
    /* registry */
    sources, events: futureEvents, news,
    /* graph */
    relationships, clientSafeCrossings,
    /* derived */
    archive,
    /* explicitly demonstrative, never real */
    futureScenarios, opportunityScenarios, fieldMessages,
    /* compatibility aliases while the views migrate; same objects, no copies */
    windows: cropWindows, voices: publicVoices, channels: publicChannels,
    regulatory: productsRegulatory, commercial: productsCommercial,
    upstreamOpportunities: opportunities,
  };

  /* Aliases must not be counted twice in provenance or totals. */
  const ALIASES = { windows: 1, voices: 1, channels: 1, regulatory: 1, commercial: 1, upstreamOpportunities: 1, events: 1 };
  const primaryKeys = Object.keys(collections).filter((k) => !ALIASES[k]);

  const provenanceSummary = primaryKeys.map((k) => ({
    layer: k,
    provenance: collections[k].provenance,
    source: collections[k].source,
    total: collections[k].count,
    real: collections[k].real,
    demo: collections[k].demo,
    note: collections[k].note,
  }));

  const counts = Object.keys(collections).reduce((a, k) => { a[k] = collections[k].count; return a; }, {});
  const totals = provenanceSummary.reduce(
    (a, r) => ({ total: a.total + r.total, real: a.real + r.real, demo: a.demo + r.demo }),
    { total: 0, real: 0, demo: 0 }
  );

  /* narrative debt, measured rather than assumed */
  const NARRATIVE_FIELDS = [
    ['publicVoices', publicVoices.records, ['proves', 'notProves']],
    ['news', news.records, ['summary', 'caveat', 'contentKindMeaning']],
    ['futureSignals', futureSignals.records, ['whyWatch', 'observedFacts', 'interpretation', 'nextWindow', 'portfolioConnection', 'whoIsTalking', 'whatChanged']],
    ['opportunities', opportunities.records, ['whatIsHappening', 'whyItMatters', 'currentEvidence', 'whatWeKnow', 'whatWeDoNotKnow', 'interpretations']],
    ['currentFieldSignals', currentFieldSignals.records, ['expectedCycle', 'observedStage', 'regulatoryWindow', 'preparationWindow', 'adamaProductsNote']],
    ['resistance', resistance.records, ['mechanism']],
    ['futureEvents', futureEvents.records, ['note', 'participationLaw']],
    ['sources', sources.records, ['role', 'limitations']],
  ];
  NARRATIVE_FIELDS.forEach(([family, recs, fields]) =>
    fields.forEach((f) => noteNarrative(family, f, recs.filter((r) => r[f] && r[f].state === KNOWLEDGE.NOT_APPROVED_FOR_DISPLAY).length)));

  /* ── 9 · SEARCH INDEX ───────────────────────────────────────────────────
     One index over the normalized model, in both languages. A search result
     opens the real entity it names — never a look-alike. */
  const searchIndex = [];
  const idx = (kind, id, label, terms, route, meta) =>
    id && searchIndex.push({
      kind, id, label: String(label || id), route: route || kind,
      terms: uniq(terms.flatMap((t) => A(t)).filter(Boolean).map((t) => String(t).toLowerCase())),
      meta: meta || null,
    });

  products.forEach((p) => idx('product', p.name, p.name, [p.name, p.ai, p.categoryLabel, p.line, p.crops], 'product', p.categoryLabel));
  opportunities.records.forEach((o) => idx('case', o.id, [o.issue, o.region].filter(Boolean).join(' · '), [o.title, o.issue, o.crop, o.region, o.id, o.legacyCaseId], 'case', o.crop));
  publicVoices.records.forEach((v) => idx('voice', v.id, v.person || v.channel || v.title, [v.person, v.channel, v.crop, v.issue, v.title, v.organization], 'voice', v.platform));
  futureSignals.records.forEach((f) => idx('signal', f.id, [f.issue, f.region].filter(Boolean).join(' · '), [f.issue, f.crop, f.region, f.id], 'signal', f.crop));
  researchers.records.forEach((r) => idx('researcher', r.id, r.name, [r.name, r.org, r.institutions, r.theme], 'person', r.org));
  resistance.records.forEach((r) => idx('resistance', r.id, r.species, [r.species, r.speciesIt, r.crop, r.family], 'science', r.crop));
  cropWindows.records.forEach((w) => idx('window', w.id, [w.issue, w.region].filter(Boolean).join(' · '), [w.crop, w.issue, w.region, w.id], 'window', w.crop));
  sources.records.forEach((s) => idx('source', s.id, s.name, [s.name, s.type, s.geography, s.country], 'source', s.type));
  futureEvents.records.forEach((e) => idx('event', e.id, e.name, [e.name, e.location, e.sector, e.cropRelevance], 'event', e.location));
  news.records.forEach((n) => idx('news', n.id, n.title, [n.title, n.publisher, n.crop, n.issue, n.region], 'news', n.publisher));
  scienceRecords.records.forEach((r) => idx('science', r.id, r.title, [r.title, r.institution, r.crop, r.issue, r.author], 'science', r.institution));
  competitorCompanies.records.forEach((c) => idx('company', c.name, c.name, [c.name, c.productsProved], 'company', null));
  competitorProducts.records.forEach((p) => idx('competitor', p.id, p.name, [p.name, p.company], 'cproduct', p.company));
  marketObservations.records.forEach((m) => idx('market', m.id, [m.product, m.market].filter(Boolean).join(' · '), [m.product, m.market, m.geography, m.group], 'market', m.geography));
  publicChannels.records.forEach((c) => idx('channel', c.id, c.name, [c.name, c.contentTypeExample], 'voice', c.name));

  const search = (query, limit) => {
    const q = String(query || '').trim().toLowerCase();
    if (q.length < 2) return [];
    const out = searchIndex.filter((e) => e.label.toLowerCase().includes(q) || e.terms.some((t) => t.includes(q)));
    return limit ? out.slice(0, limit) : out;
  };

  /* ── 10 · PUBLIC CONTRACT ───────────────────────────────────────────── */
  window.ITALY_APP_MODEL = {
    version: '3.0',
    compiled: REFERENCE_DATE,

    /* one clock */
    referenceDate: REFERENCE_DATE, REF, daysFrom, asDate,

    /* provenance vocabulary */
    PROVENANCE: P, PRECEDENCE, provOf, isDemo,
    STRENGTH, ABSENCE_RULE,
    KNOWLEDGE, narrative,
    CATEGORY_UI, categoryOf,

    /* the product law, stated in the contract itself */
    productDefinition: 'EXTERNAL_INTELLIGENCE_CORE',
    coreRequiresPrivateData: false,
    NOT_OBSERVABLE: P.NOT_OBSERVABLE,

    /* data */
    collections, counts, totals, provenanceSummary,
    searchIndex, search,
    products, productByKey, findProduct, strengthFor,
    productRelationships,

    /* the ingestion boundary, so the receiver can be audited */
    ingest: {
      report: ingestReport,
      narrativeDebt,
      registeredSources: Object.keys(RAW).filter((k) => RAW[k] && (Array.isArray(RAW[k]) ? RAW[k].length : Object.keys(RAW[k]).length)),
      handoffV21Present: !!RAW.HANDOFF_V21,
      families: primaryKeys,
    },
  };
})();
