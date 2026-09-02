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

   THE CLIENT-SAFE GATE — the law the V2.1 package exists to enforce
   Only CLIENT_SAFE=true may sustain a claim visible to the client. A
   CLIENT_SAFE=false record still belongs to the CORPUS, because a
   transparency panel that cannot say how large the reading is has stopped
   being transparent — so it is counted and never rendered. Every collection
   therefore publishes THREE numbers, not one:
       count · clientSafe · corpus
   and exposes `safeRecords` so no screen has to filter by hand and get it
   wrong somewhere. clientSafe === null means the SOURCE does not declare the
   flag at all (every pre-V2.1 table); that is "not declared", not zero.

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
    /* the package's own REFERENCE_DATE, read first. It is 2026-09-02 and it is
       the ONLY clock: nothing below derives a second one, and every record's
       own REFERENCE_DATE is parsed as data, never promoted to the clock. */
    (RAW.HANDOFF_V21 && (RAW.HANDOFF_V21.REFERENCE_DATE || RAW.HANDOFF_V21.referenceDate)) ||
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
  /* Plain-text form of a narrative field: the approved localized text, or
     nothing. Never the raw research note. */
  const narText = (rec, base) => { const n = narrative(rec, base); return n.state === KNOWLEDGE.CLEAR ? (n.it || n.en) : null; };

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
    /* ── THE CLIENT-SAFE GATE, published on EVERY collection ───────────────
       V2.1 law 1: only CLIENT_SAFE=true may sustain a claim visible to the
       client; CLIENT_SAFE=false lives in the corpus and never closes an
       assertion alone.

       So `records` is the CORPUS — a non-safe record is never silently
       dropped, because dropping it is what stops the transparency panel from
       saying how large the reading actually is — and `safeRecords` is the
       array a view must read. Every screen filtering by hand is how one
       screen eventually forgets.

       clientSafe === null means the SOURCE DOES NOT DECLARE THE FLAG (every
       pre-V2.1 table). That is "not declared", which is a different fact from
       "zero", and a panel must print it as such rather than as a 0. */
    const declares = rec.some((r) => r && typeof r.clientSafe === 'boolean');
    const safeRecords = declares ? rec.filter((r) => r.clientSafe === true) : rec;
    const corpusOnly = declares ? rec.filter((r) => r.clientSafe !== true) : [];
    const c = {
      records: rec,
      safeRecords,
      corpusOnly,
      provenance,
      note: note || '',
      count: rec.length,
      /* count · clientSafe · corpus — the three numbers the panel needs */
      corpus: rec.length,
      clientSafe: declares ? safeRecords.length : null,
      corpusOnlyCount: corpusOnly.length,
      clientSafeState: declares ? 'DECLARED' : 'NOT_DECLARED_BY_SOURCE',
      /* Corpus rows: they keep their facts and lose their prose, so they can
         be counted and cross-referenced and never rendered as a statement. */
      identityOnlyCount: rec.filter((r) => r && r.payloadState === 'CORPUS_FACTS_ONLY').length,
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

  /* ═══════════════════════════════════════════════════════════════════════
     5b · THE V2.1 PACKAGE, READ AS THE CANONICAL SOURCE
     ═══════════════════════════════════════════════════════════════════════
     ITALY_HANDOFF_V21 publishes 26 families under collections[APP_KEY minus
     the "APP." prefix], plus a MANIFEST that states, per family, its LAW, its
     source of truth, its primary key and the counts it must reproduce. The
     manifest is data, so the law travels onto the built collection instead of
     being restated in a comment a view cannot read.

     TWO THINGS THE TRANSPORT ALREADY DID, both on the package's own order:
       · RESEARCH and every *_ORIGINAL_RESEARCH_TEXT are NOT in the browser.
         The approved *_IT / *_EN fields are, which is what makes the narrative
         rule return CLEAR instead of NOT_APPROVED_FOR_DISPLAY on this package.
       · A CLIENT_SAFE=false record travels as identity + QA state ONLY.
         MEASURED here: that holds on 26/26 families — no non-safe record in
         the package carries a single field outside the seven-field stub. So a
         non-safe record can be COUNTED and can never be RENDERED, which is
         exactly the gate, enforced by the transport rather than by a screen.

     WHAT THAT COSTS, stated rather than hidden: where a whole family is
     CLIENT_SAFE=false (opportunities 3/3, relationships 19/19, crossings
     19/19) the package delivers no payload at all. For those, and only for
     those, the adapter merges the SAME RECORD from the lower-precedence
     ITALY_INGEST by primary key — provable identity, not a guess: the ids are
     identical and V2.1's own ORIGIN_LAYER says PREVIOUS_HANDOFF. V2.1 still
     wins every key it carries; the merge only fills what it did not transport. */
  const V21H = RAW.HANDOFF_V21 || null;
  const V21C = (V21H && V21H.collections) || {};
  const V21_MANIFEST = {};
  A(V21H && V21H.MANIFEST).forEach((m) => { if (m && m.family) V21_MANIFEST[m.family] = m; });

  /** The gate itself, as a predicate on a raw V2.1 record. */
  const CS = (r) => !!(r && (r.CLIENT_SAFE === true || r.CLIENT_SAFE === 'true'));
  /** A row the package itself derived is REAL_DERIVED, never CANONICAL fact. */
  const v21prov = (r) => (U(r && r.ORIGIN_LAYER) === 'DERIVED_V2_1' || U(r && r.QA_STATUS) === 'EVIDENCE_DERIVED')
    ? P.REAL_DERIVED : P.CANONICAL;

  /**
   * The spine every V2.1 record shares, normalized once.
   * Adapters spread this and then add their family fields, so the 14 shared
   * columns cannot be spelled three different ways across 26 adapters.
   */
  const v21spine = (r) => ({
    id: S(r.ID),
    entityType: S(r.ENTITY_TYPE),
    qaStatus: S(r.QA_STATUS),
    clientSafe: CS(r),
    /* CLIENT_SAFE / CORPUS_FACTS_ONLY. The transport's rule is that a
       CLIENT_SAFE=false record KEEPS ITS FACTS AND LOSES ITS PROSE, so a
       corpus row can be counted, filtered and cross-referenced by id — and
       has no reviewed sentence to render. Views read safeRecords. */
    payloadState: CS(r) ? 'CLIENT_SAFE' : 'CORPUS_FACTS_ONLY',
    originLayer: S(r.ORIGIN_LAYER),
    claimDomain: S(r.CLAIM_DOMAIN),
    provenanceState: S(r.PROVENANCE_STATE),
    provenanceStrength: S(r.PROVENANCE_STRENGTH),
    provenanceRecoveredVia: S(r.PROVENANCE_RECOVERED_VIA),
    provenanceRecoveredFrom: S(r.PROVENANCE_RECOVERED_FROM),
    sourceIds: A(r.SOURCE_IDS), sourceUrls: A(r.SOURCE_URLS),
    /* One clock: REFERENCE_DATE is parsed, never re-derived. Several rows
       write it as a range or annotate it ('2026-09-03 (campo referencePeriod
       da propria API)'); isoOf takes the head and refuses anything else. */
    recordReferenceDate: isoOf(r.REFERENCE_DATE),
    cropIds: A(r.CROP_IDS), issueIds: A(r.ISSUE_IDS), regionIds: A(r.REGION_IDS),
    geographicScope: S(r.GEOGRAPHIC_SCOPE),
    observationClass: S(r.OBSERVATION_CLASS),
    confidence: S(r.CONFIDENCE),
    evidenceStatus: S(r.EVIDENCE_STATUS),
    evidenceStatusWhy: narrative(r, 'EVIDENCE_STATUS_WHY'),
    /* The three permanent caveats the package attaches to a claim row. They
       are the reason a fact may be shown at all, so they travel with it. */
    whatItIs: narrative(r, 'WHAT_IT_IS'),
    proves: narrative(r, 'WHAT_IT_PROVES'),
    notProves: narrative(r, 'WHAT_IT_DOES_NOT_PROVE'),
    permanentCaveat: narrative(r, 'PERMANENT_CAVEAT'),
    sourceScope: narrative(r, 'SOURCE_SCOPE'),
    provenance: v21prov(r),
    raw: r,
  });

  /**
   * One V2.1 family as a build() candidate.
   *   key        the collections[] key, e.g. 'products.relationships'
   *   adapt      the family adapter
   *   opts.enrichFrom  a lower-precedence table whose rows share the primary
   *                    key; used ONLY to fill what the transport did not carry
   *   opts.validate    defaults to "must have an id"
   */
  const V21 = (key, adapt, opts) => {
    const rows = A(V21C[key]);
    if (!rows.length || typeof adapt !== 'function') return null;
    const o = opts || {};
    let input = rows;
    if (o.enrichFrom) {
      const ix = {};
      A(o.enrichFrom).forEach((r) => { const k = U(r && (r.ID || r.id || r.SIGNAL_ID)); if (k) ix[k] = r; });
      input = rows.map((r) => { const l = ix[U(r.ID)]; return l ? Object.assign({}, l, r) : r; });
    }
    return {
      source: 'HANDOFF_V21 · ' + key,
      precedence: P.CANONICAL,
      rows: input,
      adapt,
      validate: o.validate || ((x) => (!x.id ? 'no ID' : null)),
    };
  };

  /** Put the manifest's own law and declared counts on the collection that won. */
  const v21law = (c, key) => {
    const m = V21_MANIFEST[key];
    if (!m || !c || c.source !== 'HANDOFF_V21 · ' + key) return c;
    return Object.assign(c, {
      v21Family: key,
      law: S(m.law) || null,
      sourceOfTruth: S(m.sourceOfTruth) || null,
      primaryKey: S(m.primaryKey) || null,
      replaces: A(m.replaces),
      declaredTotal: N(m.declaredTotal),
      declaredClientSafe: N(m.declaredSafe),
      /* The files win over the manifest. Where they disagree the collection
         says so instead of publishing the manifest's number. */
      countReconciles: N(m.declaredTotal) === c.count,
      clientSafeReconciles: N(m.declaredSafe) === c.clientSafe,
    });
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
  /* Competitor activities carry no SOURCE_ID, but the platform they were read
     from IS a registered source. Mapping the two observed platforms onto their
     registry ids is a fact about where the row came from, not a guess. */
  const ARCHIVE_PLATFORM_SOURCE = { META_ADS_LIBRARY: 'IT-SRC-META', YOUTUBE: 'IT-SRC-YOUTUBE' };
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
    'PRUNUS PERSICA': 'Peach', CITRUS: 'Citrus', 'HELIANTHUS ANNUUS': 'Sunflower',
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

  /* The upstream intelligence was researched in Portuguese, and the language
     did not stay inside the research notes: OPPORTUNITIES.CROP is "Videira",
     FUTURE_SIGNALS.CROP is "TRIGO e TRIGO DURO", RESISTANCE.CROP_DECLARED is a
     Portuguese sentence. Those are FACT fields that reach the screen, so the
     crop name has to be resolved rather than printed. */
  const CROP_BY_PT = {
    VIDEIRA: 'Grapevine', MILHO: 'Maize', 'MILHO GRÃO': 'Maize', 'MILHO GRAO': 'Maize',
    TRIGO: 'Wheat', 'TRIGO DURO': 'Durum Wheat', ARROZ: 'Rice', SOJA: 'Soybean',
    TOMATE: 'Tomato', OLIVEIRA: 'Olive', OLIVAL: 'Olive', CEVADA: 'Barley',
    BATATA: 'Potato', BETERRABA: 'Sugar Beet', 'MAÇÃ': 'Apple', MACA: 'Apple',
  };

  /**
   * Resolve any crop token, in any of the six vocabularies this package
   * publishes, to the canonical crop the window contract uses.
   *
   *   scope RESOLVED      one canonical crop
   *   scope MULTI         the source really named several ("grano duro e tenero")
   *   scope GENERIC_TERM  a group word; NEVER promoted to a specific crop,
   *                       because "cereali" is not "Wheat" and saying so
   *                       would invent a fact
   *   scope NOT_OBSERVED  nothing was published
   *   scope UNMAPPED      published, but this package has no rule for it
   *
   * The raw token is always carried alongside, so nothing becomes untraceable.
   */
  /* The 20 Italian regions, plus the two autonomous provinces the sources name.
     REGION arrives as free text with Portuguese annotation — "Veneto
     (principal) + Lombardia", "Friuli-Venezia Giulia (sinal) · vale do Pó
     (escala)". The regions are facts; the annotation is a research note. So the
     region names are extracted and the rest is dropped, rather than printing
     the sentence or throwing the fact away with it. */
  const IT_REGIONS = ['Abruzzo', 'Basilicata', 'Calabria', 'Campania', 'Emilia-Romagna', 'Friuli-Venezia Giulia',
    'Lazio', 'Liguria', 'Lombardia', 'Marche', 'Molise', 'Piemonte', 'Puglia', 'Sardegna', 'Sicilia',
    'Toscana', 'Trentino-Alto Adige', 'Trentino', 'Alto Adige', 'Umbria', "Valle d'Aosta", 'Veneto',
    'Bolzano', 'Trento'];
  const regionResolve = (raw) => {
    const t = S(raw);
    if (!t || UNKNOWN_SENTINEL.test(t)) return { names: [], label: null, scope: 'NOT_OBSERVED', raw: t };
    const u = t.toLowerCase();
    const names = IT_REGIONS.filter((r) => u.indexOf(r.toLowerCase()) >= 0);
    /* keep the longer name when one contains another (Trentino-Alto Adige vs Trentino) */
    const kept = names.filter((r) => !names.some((o) => o !== r && o.toLowerCase().indexOf(r.toLowerCase()) >= 0));
    if (kept.length) return { names: kept, label: kept.join(' · '), scope: 'RESOLVED', raw: t };
    if (/\b(itali[ae]|nazionale|nacional)\b/i.test(t)) return { names: [], label: 'Italia', scope: 'NATIONAL', raw: t };
    return { names: [], label: null, scope: 'UNMAPPED', raw: t };
  };

  /* The issue vocabulary leaks Portuguese the same way: "micotoxina /
     Fusarium", "REGULATORIO". A Latin genus is never translated — Fusarium
     stays Fusarium — but a Portuguese common noun in front of it is not a name,
     it is the wrong language. Only declared, unambiguous pairs are mapped. */
  const ISSUE_TERM_IT = {
    micotoxina: 'micotossina', micotoxinas: 'micotossine',
    desoxinivalenol: 'deossinivalenolo', regulatorio: 'REGOLATORIO', 'regulatório': 'REGOLATORIO',
    praga: 'avversità', pragas: 'avversità', 'flavescência dourada': 'Flavescenza dorata',
    piralide: 'Piralide', 'milho': 'mais',
  };
  const ISSUE_TERM_EN = {
    micotoxina: 'mycotoxin', micotoxinas: 'mycotoxins',
    desoxinivalenol: 'deoxynivalenol', regulatorio: 'REGULATORY', 'regulatório': 'REGULATORY',
    praga: 'pest', pragas: 'pests', 'flavescência dourada': 'Flavescence dorée',
  };
  /* Measured: 33 distinct issue strings reach the model, in three vocabularies —
     the canonical window names in English (translated by the interface through
     T.ISSUES), SCREAMING_SNAKE tokens, and six strings the upstream research
     left in Portuguese. Those six are listed here by their exact source text
     rather than guessed at by a rule, so the mapping is auditable line by line.
     Every Latin binomial inside them is carried through untouched. */
  const ISSUE_PHRASE = {
    'Flavescência dourada, via o vetor Scaphoideus titanus': {
      it: 'Flavescenza dorata, tramite il vettore Scaphoideus titanus',
      en: 'Flavescence dorée, through the vector Scaphoideus titanus',
    },
    'Flavescenza dorata (vetor Scaphoideus titanus)': {
      it: 'Flavescenza dorata (vettore Scaphoideus titanus)',
      en: 'Flavescence dorée (vector Scaphoideus titanus)',
    },
    'Piralide (Ostrinia nubilalis) e Diabrotica virgifera virgifera': {
      it: 'Piralide (Ostrinia nubilalis) e Diabrotica virgifera virgifera',
      en: 'European corn borer (Ostrinia nubilalis) and Diabrotica virgifera virgifera',
    },
    'Calendário de vencimento das autorizações': {
      it: 'Calendario di scadenza delle autorizzazioni',
      en: 'Authorisation expiry calendar',
    },
    'micotoxina / Fusarium': { it: 'micotossina / Fusarium', en: 'mycotoxin / Fusarium' },
    'Fusarium / desoxinivalenol': { it: 'Fusarium / deossinivalenolo', en: 'Fusarium / deoxynivalenol' },
    REGULATORIO: { it: 'REGOLATORIO', en: 'REGULATORY' },
  };
  const issueResolve = (raw) => {
    const t = S(raw);
    if (!t || UNKNOWN_SENTINEL.test(t)) return { it: null, en: null, scope: 'NOT_OBSERVED', raw: t };
    const exact = ISSUE_PHRASE[t];
    if (exact) return { it: exact.it, en: exact.en, scope: 'RESOLVED', raw: t };
    const one = (map) => t.split(/\s*([\/·|])\s*/).map((part) => {
      if (/^[\/·|]$/.test(part)) return part;
      const k = part.trim().toLowerCase();
      return map[k] || part.trim();
    }).join(' ').replace(/\s+([\/·|])\s+/g, ' $1 ').replace(/\s+/g, ' ').trim();
    const it = one(ISSUE_TERM_IT), en = one(ISSUE_TERM_EN);
    return { it, en, scope: 'RESOLVED', raw: t };
  };

  /* The canonical crop names, resolving to themselves. This is an IDENTITY, not
     a new mapping: every value here is a name one of the tables above already
     publishes, or a CROP_KEY crop. It exists because the resolver's substring
     pass is not safe on a canonical name — MEASURED, before this table:
       cropResolve('Durum Wheat') -> 'Wheat'   ('WHEAT' is inside 'DURUM WHEAT')
       cropResolve('Sugar Beet' | 'Potato' | 'Sorghum' | 'Triticale') -> UNMAPPED
     Any lookup that hands a canonical crop name back to the resolver — the
     search index, an opportunity whose CROP has been translated into the
     canonical vocabulary — would have silently produced the wrong crop or none.
     Placed FIRST so the exact pass always wins over the substring pass. */
  const CROP_BY_CANON = {};
  CROP_KEY.forEach((r) => { CROP_BY_CANON[U(r.crop)] = r.crop; });
  [CROP_BY_TOKEN, CROP_BY_IT, CROP_BY_LATIN, CROP_BY_PT].forEach((tab) => {
    Object.keys(tab).forEach((k) => { CROP_BY_CANON[U(tab[k])] = tab[k]; });
  });

  const CROP_TABLES = [CROP_BY_CANON, CROP_BY_TOKEN, CROP_BY_IT, CROP_BY_LATIN, CROP_BY_PT];
  const cropResolve = (raw) => {
    const t = S(raw);
    if (!t || UNKNOWN_SENTINEL.test(t)) return { key: null, keys: [], label: null, scope: 'NOT_OBSERVED', raw: t };
    const u = U(t).replace(/[«»"'()]/g, ' ').replace(/\s+/g, ' ').trim();
    for (const tab of CROP_TABLES) if (tab[u]) return { key: tab[u], keys: [tab[u]], label: tab[u], scope: 'RESOLVED', raw: t };
    if (GENERIC_CROP_TERMS[u] || /^(CEREAL|CEREAIS|CEREALI|COLTURE|TRANSVERSAL|TRASVERSALE|ORTICOLE|ORTAGGI|FRUTTA)\b/.test(u)) {
      return { key: null, keys: [], label: null, scope: 'GENERIC_TERM', raw: t };
    }
    /* substring pass, deduplicated by canonical crop, so "grano duro e tenero
       (trigo duro e trigo comum)" comes back as two crops rather than one
       arbitrary winner */
    const hits = new Set();
    for (const tab of CROP_TABLES) {
      for (const k of Object.keys(tab)) if (k.length >= 4 && u.indexOf(k) >= 0) hits.add(tab[k]);
    }
    const keys = [...hits];
    if (keys.length === 1) return { key: keys[0], keys, label: keys[0], scope: 'RESOLVED', raw: t };
    if (keys.length > 1) return { key: null, keys, label: keys.join(' · '), scope: 'MULTI', raw: t };
    if (/\b(TRANSVERSAL|PORTFOLIO|PORTFÓLIO|PORTAFOGLIO)\b/.test(u)) return { key: null, keys: [], label: null, scope: 'GENERIC_TERM', raw: t };
    return { key: null, keys: [], label: null, scope: 'UNMAPPED', raw: t };
  };

  /* ── 6c-bis · THE V2.1 IDENTIFIER VOCABULARIES ───────────────────────────
     V2.1 gives every record CROP_IDS / ISSUE_IDS / REGION_IDS — controlled
     keys, which is the first time this package has had any. They are a SEVENTH
     crop vocabulary, so they are declared here in full rather than matched by
     stripping a prefix: CROP_SOFT_WHEAT is 'Wheat', not 'Soft Wheat', and
     CROP_WHEAT_GENERIC legitimately names two canonical crops.

     Four ids are deliberately absent from the crop table:
       CROP_VEGETABLES  · a group word, like 'orticole'. Never promoted.
       CROP_STONE_FRUIT · a group ('drupacee'), not a species.
       CROP_KIWI · CROP_PEAR — real crops with no canonical window, resolved to
         their own English names exactly as Peach and Citrus already are. */
  const CROP_BY_V21_ID = {
    CROP_APPLE: ['Apple'], CROP_BARLEY: ['Barley'], CROP_CITRUS: ['Citrus'],
    CROP_DURUM_WHEAT: ['Durum Wheat'], CROP_GRAPEVINE: ['Grapevine'],
    CROP_KIWI: ['Kiwi'], CROP_MAIZE: ['Maize'], CROP_OLIVE: ['Olive'],
    CROP_PEACH: ['Peach'], CROP_PEAR: ['Pear'], CROP_POTATO: ['Potato'],
    CROP_RICE: ['Rice'], CROP_SOFT_WHEAT: ['Wheat'], CROP_SOYBEAN: ['Soybean'],
    CROP_SUGAR_BEET: ['Sugar Beet'], CROP_SUNFLOWER: ['Sunflower'],
    CROP_TOMATO: ['Tomato'],
    /* the generic Frumento label again, under its V2.1 key: one row is
       evidence for both wheat crops and the overlap is declared, not hidden */
    CROP_WHEAT_GENERIC: ['Wheat', 'Durum Wheat'],
  };
  const V21_GENERIC_CROP_IDS = { CROP_VEGETABLES: 1, CROP_STONE_FRUIT: 1 };
  const cropsFromV21Ids = (ids) => uniq(A(ids).flatMap((k) => CROP_BY_V21_ID[U(k)] || []));

  /* REGION_IDS. GEO_ITALY and GEO_EU are scopes, not regions, and are kept out
     of the region list so a national fact cannot be filed under a region. */
  const REGION_BY_V21_ID = {};
  IT_REGIONS.forEach((n) => { REGION_BY_V21_ID['REGION_' + fold(n).toUpperCase().replace(/[^A-Z]+/g, '_')] = n; });
  const V21_SCOPE_ID = { GEO_ITALY: 'NATIONAL', GEO_EU: 'EUROPEAN' };
  const regionsFromV21Ids = (ids) => uniq(A(ids).map((k) => REGION_BY_V21_ID[U(k)] || null));
  const scopeFromV21Ids = (ids) => A(ids).map((k) => V21_SCOPE_ID[U(k)]).filter(Boolean)[0] || null;

  /* ISSUE_IDS are deliberately NOT mapped onto the canonical window issue
     names. Only 23 ids exist and several (ISSUE_WEEDS_GENERIC, ISSUE_RUST)
     have no unambiguous canonical partner; authoring the table would be
     authoring most of it, which is the same reason ISSUE_TARGET stays null.
     The ids travel verbatim so a later upstream table can key on them. */

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

  /* The three upstream opportunities are written in the analyst's language, so
     asking the label audit about them needs a translation of the QUESTION, not
     of the answer. These two tables are the only hand-authored joins in the
     model besides CROP_KEY; they are tiny, they are exhaustive (3 records), and
     every link they produce records which row produced it in resolvedThrough.
     Opportunity 003 is deliberately absent: its CROP is 'Portfólio ADAMA Italia
     (transversal, não é uma cultura)', which is a portfolio, not a crop. */
  const oppKey = (v) => fold(String(v || '')).toUpperCase().replace(/\s+/g, ' ').trim();
  const OPP_CROP = {
    VIDEIRA: ['Grapevine'],
    'MILHO GRAO': ['Maize'],
  };

  /* WHY THIS IS GENERATED AND NOT TYPED OUT.
     The declared part is one line per opportunity: the wording the SOURCE
     published, and the canonical window issue it is the same issue as. That is
     the judgement, and it stays hand-authored and auditable.
     The KEYS are then generated by asking issueResolve() for every wording it
     can emit for that source string — the published Portuguese, the Italian and
     the English. A hand-typed key list is what broke this join once already:
     the record was resolved into Italian, the Portuguese key stopped matching,
     and the Opportunity screen printed "verifica etichetta necessaria" over two
     matches the Window screen proved on the same crop and issue — the audited
     claim inverted, on the one mandatory-control case in the package (§10).
     Generating the keys from the resolver means adding a term to ISSUE_PHRASE
     or ISSUE_TERM_* re-keys this table in the same breath, so the two can no
     longer drift apart. */
  const OPP_ISSUE_DECLARED = {
    /* published source wording -> canonical window issue */
    'Flavescência dourada, via o vetor Scaphoideus titanus': 'Flavescenza Dorata',
    'Piralide (Ostrinia nubilalis) e Diabrotica virgifera virgifera': 'European Corn Borer',
    /* IT-OPP-003 ('Calendário de vencimento das autorizações') is deliberately
       absent: an authorisation-expiry calendar is not a crop issue and has no
       unambiguous canonical partner. It stays unmapped rather than guessed. */
  };
  const OPP_ISSUE = {};
  Object.keys(OPP_ISSUE_DECLARED).forEach((src) => {
    const r = issueResolve(src);
    [src, r.it, r.en].forEach((wording) => {
      if (wording) OPP_ISSUE[oppKey(wording)] = OPP_ISSUE_DECLARED[src];
    });
  });

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

  /* THE ISSUE SIDE OF THIS JOIN IS A STRING A RESOLVER MAY REWRITE.
     Both sides of the audit join are therefore registered AND queried under
     every wording issueResolve() can emit for them: the text as published, the
     Italian and the English. MEASURED today: all 14 audit issues and all 21
     window issues emit one single wording each, so this changes no verdict and
     no count — 12 windows verified, 19 with any verdict, before and after. What
     it removes is the failure mode: a later Italianisation of a canonical issue
     name would otherwise unhook the audit from its window silently, which is
     exactly how the Opportunity screen came to deny two matches it could prove.
     The CROP side is deliberately NOT routed through cropResolve: measured,
     cropResolve('Durum Wheat') used to return 'Wheat', and a crop resolver that
     can merge two audit crops would forge a label match instead of missing one.
     Both sides of the crop join already speak the canonical English vocabulary. */
  const issueWordings = (v) => { const r = issueResolve(v); return uniq([S(v), r.it, r.en].map(foldIssue)); };
  const verdictKeysOf = (crop, issue) => uniq(issueWordings(issue).map((i) => U(crop) + '@' + i));
  const verdictIndexPush = (map, crop, issue, product) => {
    verdictKeysOf(crop, issue).forEach((k) => { (map[k] = map[k] || []).push(product); });
  };
  const verdictIndexGet = (map, crop, issue) => {
    for (const k of verdictKeysOf(crop, issue)) if (map[k]) return map[k];
    return [];
  };

  const LV_VERIFIED = A(RAW.LABEL_AUDIT.VERIFIED).filter((t) => A(t).length >= 3).map((t) => ({ crop: S(t[0]), issue: S(t[1]), product: S(t[2]), strength: 'VERIFIED_LABEL_MATCH' }));
  const LV_NOT_FOUND = A(RAW.LABEL_AUDIT.NOT_FOUND).filter((t) => A(t).length >= 3).map((t) => ({ crop: S(t[0]), issue: S(t[1]), product: S(t[2]), strength: 'NO_CONFIRMED_MATCH_CURRENT_READING' }));
  const verifiedByCropIssue = {};
  LV_VERIFIED.forEach((v) => verdictIndexPush(verifiedByCropIssue, v.crop, v.issue, v.product));
  const notFoundByCropIssue = {};
  LV_NOT_FOUND.forEach((v) => verdictIndexPush(notFoundByCropIssue, v.crop, v.issue, v.product));

  /* ═══════════════════════════════════════════════════════════════════════
     7 · FAMILIES
     ═══════════════════════════════════════════════════════════════════════ */

  /* ---- FIELD SIGNALS · the seven observed crop x issue readings ---------
     Built BEFORE the canonical windows because a canonical window joins to it:
     five regional regulatory acts and the only two real field observations in
     the whole package live here, and three of the five have no canonical window
     at all — they are reachable only from their own collection. */
  /* The V2.1 family that holds these seven rows is called `windows`
     (CROP-WINDOWS.json) — the same seven records ITALY_INGEST.CROP_WINDOWS
     carries, under the same field names and the same seven ids. It is NOT the
     29-row canonical window contract, which V2.1 does not supply at all; that
     one keeps its own source below. The 122-row CURRENT-FIELD-SIGNALS.json is
     a THIRD thing (regional phytosanitary bulletins) and gets its own
     collection rather than being poured into this one. */
  const currentFieldSignals = build('currentFieldSignals', [
    V21('windows', (c) => Object.assign(v21spine(c), {
      crop: S(c.CROP),
      cropCanonical: cropResolve(c.CROP).key || cropsFromV21Ids(c.CROP_IDS)[0] || null,
      cropKeys: uniq(cropResolve(c.CROP).keys.concat(cropsFromV21Ids(c.CROP_IDS))),
      region: S(c.REGION),
      regionKeys: regionsFromV21Ids(c.REGION_IDS),
      issue: issueResolve(c.ISSUE).it, issueEn: issueResolve(c.ISSUE).en, issueRaw: S(c.ISSUE),
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
      coverageState: S(c.COVERAGE_STATE),
      /* V2.1 supplies the two dates the old table had no slot for. */
      observationDate: isoOf(c.OBSERVATION_DATE), factDate: isoOf(c.FACT_DATE),
      /* Still declared: the free prose is authored in the analyst's language
         and only the approved *_IT / *_EN variants ever leave this model. */
      languageState: 'PT_ANALYST_SOURCE',
      sourceId: S(c.SOURCE_ID),
    })),
    {
      source: 'ITALY_INGEST.CROP_WINDOWS',
      precedence: P.REAL_SOURCE,
      rows: RAW.IG.CROP_WINDOWS,
      adapt: (c) => ({
        id: c.ID,
        crop: S(c.CROP),
        /* The upstream writes crops in Italian here and in English in the
           canonical contract, so this field IS the join to the canonical window.
           It goes through the resolver rather than through CROP_BY_IT alone:
           the Italian table is the only vocabulary that table knows, and a
           regional act whose CROP is written 'Vitis vinifera' or 'Grapevine'
           would have dropped its regulatory obligation on the floor. Measured
           identical on all 7 rows and on both canonical joins today. */
        cropCanonical: cropResolve(c.CROP).key,
        region: S(c.REGION),
        issue: issueResolve(c.ISSUE).it, issueEn: issueResolve(c.ISSUE).en, issueRaw: S(c.ISSUE),
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
  v21law(currentFieldSignals, 'windows');

  /* ---- FIELD BULLETINS · the 122 regional phytosanitary bulletins --------
     New in V2.1 and new to this model: CURRENT-FIELD-SIGNALS.json, the
     provincial and regional bulletin corpus. 86 of the 122 are client-safe;
     the other 36 travel as identity only.

     LAW, carried per record because it is the one that inverts a reading:
     GEOGRAPHIC_SCOPE NEVER RISES. A PROVINCIAL or AREALE bulletin does not
     represent its region — five provincial documents from Campania are not
     "la Campania" — so regionKeys is published beside the scope and a view
     that wants a regional statement has to read REGION_REPRESENTS first. */
  const fieldBulletins = build('fieldBulletins', [
    V21('fieldSignals', (b) => Object.assign(v21spine(b), {
      title: S(b.BULLETIN_TITLE),
      bulletinNumber: S(b.BULLETIN_NUMBER),
      phenologicalStage: S(b.PHENOLOGICAL_STAGE_DECLARED),
      pestsCited: A(b.PESTS_AND_DISEASES_CITED),
      cropState: S(b.CROP_STATE),
      cropsDeclared: A(b.CROPS_DECLARED),
      cropKeys: cropsFromV21Ids(b.CROP_IDS),
      interventionGuidance: narrative(b, 'INTERVENTION_GUIDANCE'),
      citation: S(b.CITATION),
      /* the four geography fields that say what this document does and does
         not represent; none of them may be summarised away */
      geographyState: S(b.GEOGRAPHY_STATE),
      regionRepresents: S(b.REGION_REPRESENTS),
      geographyEvidence: S(b.GEOGRAPHY_EVIDENCE),
      geographyBatchLabel: S(b.GEOGRAPHY_BATCH_LABEL),
      geographyLaw: S(b.GEOGRAPHY_LAW),
      provinceIds: A(b.PROVINCE_IDS), arealIds: A(b.AREAL_IDS),
      regionKeys: regionsFromV21Ids(b.REGION_IDS),
      geoScopeRises: false,
    })),
  ], 'regional and provincial phytosanitary bulletins; a provincial document never represents its region');
  v21law(fieldBulletins, 'fieldSignals');
  Object.assign(fieldBulletins, {
    scopeCounts: tallyBy(fieldBulletins.safeRecords, (r) => r.geographicScope),
    withGuidance: fieldBulletins.safeRecords.filter((r) => r.interventionGuidance.state === KNOWLEDGE.CLEAR).length,
  });

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
  /* NO V2.1 CANDIDATE, and that is a measured statement about the package,
     not an oversight: V2.1 supplies CROP-WINDOWS.json, which is the 7-row
     field-reading table above, and nothing that carries WINDOW_ID, START_DATE,
     END_DATE or CURRENT_STATUS for the 29 audited windows. The canonical
     contract therefore stays the highest-precedence source for this family. */
  const cropWindows = build('cropWindows', [
    {
      source: 'ITALY_CANONICAL.windows',
      precedence: P.CANONICAL,
      rows: RAW.CANON.windows,
      adapt: (w) => ({
        id: w.WINDOW_ID,
        windowId: w.WINDOW_ID,
        legacyCaseId: w.LEGACY_CASE_ID || null,
        crop: S(w.CROP_NAME),
        issue: issueResolve(w.ISSUE_NAME).it, issueEn: issueResolve(w.ISSUE_NAME).en, issueRaw: S(w.ISSUE_NAME),
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
    w.verifiedProducts = verdictIndexGet(verifiedByCropIssue, w.crop, w.issue).slice();
    w.notFoundProducts = verdictIndexGet(notFoundByCropIssue, w.crop, w.issue).slice();
    w.labelVerdictState = w.verifiedProducts.length ? 'VERIFIED_LABEL_MATCH' : 'NO_CONFIRMED_MATCH_CURRENT_READING';
    w.absenceRule = ABSENCE_RULE_TEXT;
    /* The upstream regulatory reading for this exact crop and region, or null.
       Measured: 2 of 29 windows join (both Flavescenza Dorata). */
    const fs = fieldSignalByCropRegion[U(w.crop) + '@' + U(w.region) + '@' + issueHead(w.issue)] || null;
    /* WHY THIS PROJECTION CARRIES TEXT AND NOT THE NARRATIVE OBJECT.
       A view spreads the whole window record into its props, so anything
       nested under `regulatory` travels with it. A narrative object carries
       BOTH approved languages by design, which was harmless while every one
       of these five fields was NOT_APPROVED_FOR_DISPLAY — measured 5/5 before
       V2.1 — and stopped being harmless the moment V2.1 supplied
       NEXT_IMPORTANT_WINDOW_IT and _EN: the English variant then rode into the
       props of an Italian screen.

       So the projection carries the approved text (Italian first, exactly as
       sources.limitationsText and futureEvents.participationLawText already
       do) plus the knowledge state, and the two-language object stays where it
       belongs — on the field-signal record itself, reachable through
       signalId. Nothing is lost and nothing untranslated can ride along. */
    const nState = (n) => (n && n.state) || KNOWLEDGE.NOT_ESTABLISHED;
    w.regulatory = fs ? {
      id: fs.id, signalId: fs.id, act: fs.regulatoryAct, actState: fs.regulatoryActState,
      regulatoryWindowText: fs.regulatoryWindow.it, regulatoryWindowState: nState(fs.regulatoryWindow),
      monitoringWindowText: fs.monitoringWindow.it, monitoringWindowState: nState(fs.monitoringWindow),
      applicationWindow2026Text: fs.applicationWindow2026.it, applicationWindow2026State: nState(fs.applicationWindow2026),
      nextImportantWindowText: fs.nextImportantWindow.it, nextImportantWindowState: nState(fs.nextImportantWindow),
      preparationWindowText: fs.preparationWindow.it, preparationWindowState: nState(fs.preparationWindow),
      coverageState: fs.coverageState,
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

  /* ---- CROP ECONOMIC WEIGHT ---------------------------------------------
     TWO DIFFERENT FACTS WERE SHARING ONE SLOT, and only one of them is crop
     economic weight.

     ITALY_INGEST.CROPS (17 rows) counts how many LABELS mention a crop. That
     is label-corpus reach and it is explicitly "not a market size" — it now
     lives in its own collection, cropLabelReach, so it is not silently
     overwritten by a table that measures something else.

     V2.1 CROP-ECONOMIC-WEIGHT.json (2978 rows, 13 client-safe) is the real
     economic-weight family: published area and production statistics plus the
     rows Sintonia derived from them. Its LAW is that the two never mix, which
     is why IS_SUMMARY_CLAIM travels per row: a sentence about a set is not the
     set, and the 13 safe rows are summary claims over 2965 atomic rows that
     are not client-safe. */
  const cropEconomicWeight = build('cropEconomicWeight', [
    V21('cropEconomicWeight', (c) => Object.assign(v21spine(c), {
      cropKeys: cropsFromV21Ids(c.CROP_IDS),
      crop: cropsFromV21Ids(c.CROP_IDS)[0] || cropResolve(c.CROP_CODE).key || null,
      cropLiteral: S(c.CROP_LITERAL), cropCode: S(c.CROP_CODE),
      regionKeys: regionsFromV21Ids(c.REGION_IDS),
      geography: S(c.GEOGRAPHY), geographyCode: S(c.GEOGRAPHY_CODE),
      geographyLevel: S(c.GEOGRAPHY_LEVEL),
      year: N(c.YEAR),
      indicator: S(c.INDICATOR),
      value: N(c.VALUE), unit: S(c.UNIT),
      dataset: S(c.DATASET),
      /* THE LAW OF THIS FAMILY, per row: a PUBLISHED value and a value
         DERIVED BY SINTONIA are never mixed. The flag and the formula are the
         row's own; nothing here infers one from the other, and a yield is
         ours, not the statistics office's. */
      isDerivedBySintonia: c.IS_DERIVED_BY_SINTONIA === true,
      derivationFormula: S(c.DERIVATION_FORMULA),
      valueClass: c.IS_DERIVED_BY_SINTONIA === true ? 'DERIVED_BY_SINTONIA' : 'PUBLISHED_BY_SOURCE',
      caveat: narrative(c, 'CAVEAT'),
      /* a sentence about a set is not the set */
      isSummaryClaim: c.IS_SUMMARY_CLAIM === true,
      summaryClaimNote: narrative(c, 'SUMMARY_CLAIM_NOTE'),
      claimDomainReviewed: S(c.CLAIM_DOMAIN_REVIEWED),
    })),
  ], 'published and derived crop economic weight; a summary claim over a set is never the set');
  v21law(cropEconomicWeight, 'cropEconomicWeight');
  Object.assign(cropEconomicWeight, {
    /* the two value classes, counted apart, because the whole law of this
       family is that they never mix */
    publishedRows: cropEconomicWeight.records.filter((r) => r.valueClass === 'PUBLISHED_BY_SOURCE').length,
    derivedRows: cropEconomicWeight.records.filter((r) => r.valueClass === 'DERIVED_BY_SINTONIA').length,
    summaryClaims: cropEconomicWeight.records.filter((r) => r.isSummaryClaim).length,
    indicators: tallyBy(cropEconomicWeight.records, (r) => r.indicator),
    years: uniq(cropEconomicWeight.records.map((r) => r.year)).filter((y) => y !== null).sort(),
    doNotMixNote: 'IS_DERIVED_BY_SINTONIA marks each row; a derived yield is ours, not the statistics office’s',
  });

  /* ---- CROP LABEL REACH · the table the slot above used to hold ---------- */
  const cropLabelReach = build('cropLabelReach', [
    {
      source: 'ITALY_INGEST.CROPS',
      precedence: P.REAL_SOURCE,
      rows: RAW.IG.CROPS,
      adapt: (c) => ({
        id: c.ID,
        crop: S(c.CROP_TERM),
        cropKey: cropResolve(c.CROP_TERM).key,
        productsMentioning: N(c.PRODUCTS_MENTIONING_CROP),
        productsWithUseRow: N(c.PRODUCTS_WITH_USE_ROW_READ),
        distance: S(c.DISTANCE),
        reading: S(c.READING),
        provenance: provOf(c, P.REAL_SOURCE),
        raw: c,
      }),
      validate: (r) => (!r.crop ? 'no crop term' : null),
    },
  ], 'label-corpus reach per crop; not a market size and not an economic weight');

  /* ---- PRODUCTS · regulatory + commercial -------------------------------
     THE MANIFEST'S LAW, and it is the one number in this package most likely
     to be added up wrongly: 163 REGULATORY products and 51 COMMERCIAL catalog
     products ARE NOT 214. They are two universes over the same market.

       · REGULATORY = the Ministero registry, authorisation holder ADAMA.
       · COMMERCIAL = the public adama.com/italia catalogue.
       · Six catalogue products have their authorisation in ANOTHER company's
         name (HOLDER_IS_ADAMA false on 8, of which 2 are not plant protection
         products at all: BUDGE and EXELGROW).
       · Two are systems, not products (IS_SYSTEM_NOT_PRODUCT).
       · Holder is not seller. COMMERCIAL_CONTRACT is UNKNOWN on 51/51 and the
         model never derives it from catalogue presence.

     The two collections stay separate; `products` below is their declared
     JOIN and publishes inRegulatory / inCommercial per entity so the join can
     never be read as a sum. */
  const productsRegulatory = build('productsRegulatory', [
    V21('products.regulatory', (p) => {
      const moa = p.MODE_OF_ACTION_DECLARED && typeof p.MODE_OF_ACTION_DECLARED === 'object' ? p.MODE_OF_ACTION_DECLARED : {};
      return Object.assign(v21spine(p), {
        name: S(p.NAME),
        reg: S(p.REGISTRATION_NUMBER),
        holder: S(p.AUTHORIZATION_HOLDER),
        holderIsAdama: /(^|\s)ADAMA(\s|$)/i.test(S(p.AUTHORIZATION_HOLDER) || ''),
        ai: A(p.ACTIVE_INGREDIENTS),
        form: S(p.FORMULATION),
        regCat: S(p.REGULATORY_CATEGORY),
        line: S(p.LINE),
        status: S(p.STATUS),
        expiry: S(p.EXPIRY),
        expiryISO: isoOf(p.EXPIRY),
        /* the three resistance-code lists, read from the declared MoA object */
        hrac: A(moa.HRAC), frac: A(moa.FRAC), irac: A(moa.IRAC),
        modeOfActionDeclared: Object.keys(moa).length ? moa : null,
        /* CROP_IDS is the registry's own controlled crop key, filled on 112 of
           163. `crops` and `targets` are attached AFTER the label-use rows are
           built, from those rows — a real join, never a guess. */
        crops: cropsFromV21Ids(p.CROP_IDS),
        cropIdCount: A(p.CROP_IDS).length,
        targets: [],
        labelUrl: S(p.LABEL_URL),
        catalogUrl: null, catalogCat: null,
        inPublicCatalogFlag: p.IN_PUBLIC_CATALOG_FLAG === true,
        expiresInDays: daysFrom(isoOf(p.EXPIRY)),
      });
    }, { validate: (r) => (!r.name ? 'no product name' : null) }),
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
  v21law(productsRegulatory, 'products.regulatory');

  const productsCommercial = build('productsCommercial', [
    V21('products.commercial', (p) => Object.assign(v21spine(p), {
      name: S(p.NAME),
      category: S(p.CATEGORY),
      categorySource: S(p.CATEGORY_SOURCE),
      /* MATCHED_REGULATORY_ID is the catalogue's own link to the registry,
         present on 37 of 51. Absence is "no registry match in this reading",
         which the catalogue itself says is not a claim that the product is
         unregistered. */
      regId: S(p.MATCHED_REGULATORY_ID),
      reg: S(p.MATCHED_REGULATORY_ID) || S(p.REGISTRATION_NUMBER_ON_PAGE),
      registrationNumberOnPage: S(p.REGISTRATION_NUMBER_ON_PAGE),
      matchState: S(p.NOT_A_PLANT_PROTECTION_PRODUCT) ? 'OTHER_REGULATORY_REGIME'
        : S(p.MATCHED_REGULATORY_ID) ? 'REGULATORY_MATCH_CONFIRMED'
          : 'REGULATORY_MATCH_NOT_FOUND',
      holder: S(p.AUTHORIZATION_HOLDER),
      /* HOLDER IS NOT SELLER. Both of these are facts the catalogue publishes;
         neither of them is a commercial relationship, and the model never
         turns one into the other. */
      holderIsAdama: p.HOLDER_IS_ADAMA === true,
      holderIsAdamaState: typeof p.HOLDER_IS_ADAMA === 'boolean' ? 'DECLARED' : 'NOT_DECLARED',
      commercialContract: S(p.COMMERCIAL_CONTRACT),
      commercialContractWhy: narrative(p, 'COMMERCIAL_CONTRACT_WHY'),
      /* NOT_A_PLANT_PROTECTION_PRODUCT is not a boolean upstream: when it is
         filled it holds the OTHER registration the product actually sits under
         ("n° 0037584/22 (registro de fertilizante)"). Reading it as a flag
         with === true silently scored both fertilisers as plant protection
         products, so the presence is the flag and the value is published. */
      notAPlantProtectionProduct: !!S(p.NOT_A_PLANT_PROTECTION_PRODUCT),
      otherRegulatoryRegime: S(p.NOT_A_PLANT_PROTECTION_PRODUCT),
      isSystemNotProduct: p.IS_SYSTEM_NOT_PRODUCT === true,
      ai: A(p.ACTIVE_INGREDIENTS),
      line: null, status: null, expiry: null,
      catalogUrl: S(p.PUBLIC_CATALOG_URL),
      catalogStatus: S(p.CATALOG_STATUS),
      catalogEvidence: A(p.CATALOG_EVIDENCE),
      cropsDeclaredOnSite: A(p.CROPS_DECLARED_ON_SITE),
      crops: cropsFromV21Ids(p.CROP_IDS),
      note: null,
    }), { validate: (r) => (!r.name ? 'no product name' : null) }),
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
  ], 'public commercial catalog; a catalog product is not a registry product and the two never sum');
  v21law(productsCommercial, 'products.commercial');
  /* The manifest's own arithmetic, measured here so a screen can state it
     instead of re-deriving it: 8 catalogue products have no ADAMA holder, and
     2 of those are not plant protection products at all (both are registered
     fertilisers). 8 − 2 = the manifest's "six have their authorisation in
     another company's name". Two more are systems, not products. */
  Object.assign(productsCommercial, {
    holderNotAdamaCount: productsCommercial.records.filter((p) => p.holderIsAdamaState === 'DECLARED' && !p.holderIsAdama).length,
    notPlantProtectionCount: productsCommercial.records.filter((p) => p.notAPlantProtectionProduct).length,
    systemNotProductCount: productsCommercial.records.filter((p) => p.isSystemNotProduct).length,
    heldByAnotherCompanyCount: productsCommercial.records.filter((p) => p.holderIsAdamaState === 'DECLARED' && !p.holderIsAdama && !p.notAPlantProtectionProduct).length,
    contractStates: tallyBy(productsCommercial.records, (p) => p.commercialContract),
    doNotSumNote: 'catalog products and registry products are two universes over the same market; they are never added together',
  });

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
      if (verdictIndexGet(verifiedByCropIssue, crop, issue).some((p) => U(p) === U(product))) return 'VERIFIED_LABEL_MATCH';
      if (verdictIndexGet(notFoundByCropIssue, crop, issue).some((p) => U(p) === U(product))) return 'NO_CONFIRMED_MATCH_CURRENT_READING';
      return 'LABEL_CHECK_NEEDED';
    },
  });

  /* Canonical windows indexed by crop + folded issue, so a relationship can name
     the window and the region it was audited against. A label is national — the
     region always comes from the window, never from the label. */
  const windowByCropIssue = {};
  cropWindows.records.forEach((w) => {
    verdictKeysOf(w.crop, w.issue).forEach((k) => { if (!windowByCropIssue[k]) windowByCropIssue[k] = w; });
  });
  const windowFor = (crop, issue) => {
    for (const k of verdictKeysOf(crop, issue)) if (windowByCropIssue[k]) return windowByCropIssue[k];
    return null;
  };

  const relRows = [];
  const relKey = (crop, issue, product) => [U(crop), U(issue), U(product)].join('|');
  const seenRel = {};
  const pushRel = (crop, issue, product, strength, evidence, source, extra) => {
    const k = relKey(crop, issue, product);
    const prev = seenRel[k];
    if (prev && STRENGTH[prev.strength].rank <= STRENGTH[strength].rank) return;
    const w = windowFor(crop, issue);
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
      /* THE QA STATE A RELATIONSHIP INHERITS. A row that calls itself
         client-safe has to be able to say from what, or nobody can tell an
         audited verdict from an unreviewed pairing. The default here is the
         label audit itself; a row built from a V2.1 label-use row overwrites
         both fields with that record's own QA_STATUS. */
      clientSafe: true,
      qaStatus: 'CANONICAL_LABEL_AUDIT',
      qaFrom: 'ITALY_LABEL_VERDICTS',
      linkStrength: null, linkMeans: null, quoteFromLabel: null,
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
  /* The label-use rows are pushed AFTER regulatoryLinks is built, a few lines
     below, so this join reads the normalized collection rather than one
     particular upstream table. That is what lets V2.1 replace the source
     without a second edit here. */

  /* ---- REGULATORY LINKS · the authorised use rows ------------------------
     The only fully-populated relationship table in the package. It is a
     DIFFERENT fact from 'positions assessed by the audit' (19) and from
     'verified matches' (12); a screen that shows this count must say
     'righe d'uso lette dalle etichette', not 'links'. */
  /* V2.1 PRODUCT-RELATIONSHIPS.json replaces this table: 2030 rows against
     219, read INSIDE the authorised label rather than off its header.

     THE THREE LINK STRENGTHS DO NOT SUM, so they are carried per row and
     never totalled into one "matches" number:
       LINHA_DA_TABELA      886 · the label's own use table joins crop and target
       BLOCO_DA_CULTURA     626 · the crop heads a block and the target is inside it
       DECLARACAO_DE_PRODUTO 518 · two separate lists on the product put side by side
     The first two are THE DOCUMENT joining crop and target. The third is US
     doing the joining, which is why the package marks all 518 CLIENT_SAFE=false.

     THE GATE DOES NOT SHRINK THE LAYER. All 2030 rows are carried, 35 label
     crops and 78 label targets reproduce, and the 518 unreviewed rows are
     counted, marked and kept out of every tally that could sustain a claim —
     which is why byCrop, byTarget and byProduct run over safeRecords while
     labelCrops and labelTargets are published for both. */
  const regulatoryLinks = build('regulatoryLinks', [
    V21('products.relationships', (l) => {
      const cropR = cropResolve(l.CROP_ON_LABEL);
      return Object.assign(v21spine(l), {
        crop: S(l.CROP_ON_LABEL),
        cropOnLabel: S(l.CROP_ON_LABEL),
        cropCode: U(l.CROP_ON_LABEL),
        cropKey: cropR.key || cropsFromV21Ids(l.CROP_IDS)[0] || null,
        cropKeys: uniq(cropR.keys.concat(cropsFromV21Ids(l.CROP_IDS))),
        cropScope: cropR.scope,
        /* target keeps the Latin binomial, which is the vocabulary the old
           219-row table used and the one the registry actually writes.
           targetOnLabel is the label's Italian common name beside it. */
        target: S(l.TARGET_AS_WRITTEN) || S(l.TARGET_ON_LABEL),
        targetOnLabel: S(l.TARGET_ON_LABEL),
        targetAsWritten: S(l.TARGET_AS_WRITTEN),
        targetKind: S(l.TARGET_KIND),
        weedGroup: UNK(l.WEED_GROUP),
        product: S(l.PRODUCT_NAME), productKey: U(l.PRODUCT_NAME),
        reg: S(l.REGISTRATION_NUMBER),
        /* THE STRENGTH, PER ROW. Never summed, never averaged, never
           collapsed into a single count of "matches". */
        linkStrength: S(l.LINK_STRENGTH),
        linkStrengthState: S(l.LINK_STRENGTH) ? 'DECLARED' : 'NOT_TRANSPORTED_NOT_CLIENT_SAFE',
        linkIsDocumentJoin: U(l.LINK_STRENGTH) === 'LINHA_DA_TABELA' || U(l.LINK_STRENGTH) === 'BLOCO_DA_CULTURA',
        linkMeans: narrative(l, 'LINK_MEANS'),
        /* the label's own words, quoted, never parsed for a further fact */
        quoteFromLabel: S(l.QUOTE_FROM_LABEL),
        notProves: narrative(l, 'WHAT_IT_DOES_NOT_PROVE'),
        labelUrl: A(l.SOURCE_URLS)[0] || null,
        evidence: S(l.EVIDENCE_STATUS),
        /* absent in V2.1; the old table carried them and they are not invented */
        ai: [], moa: null, moaLabel: null, doses: [], interval: null,
        timing: null, timingState: KNOWLEDGE.NOT_ESTABLISHED,
      });
    }),
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

  v21law(regulatoryLinks, 'products.relationships');
  /* Every tally below runs over safeRecords, never over the corpus: an
     identity-only row has no crop, no target and no product, and counting it
     would publish a link nobody read. */
  const REL_SAFE = regulatoryLinks.safeRecords;
  Object.assign(regulatoryLinks, {
    /* tallied over cropKeys, not cropKey: a generic Frumento row is authorised
       evidence for both wheat keys and must appear under both. The sum is
       therefore larger than the row count by exactly the number of generic
       rows, published as genericRows rather than left to be discovered. */
    byCrop: tallyBy(REL_SAFE, (r) => (r.cropKeys.length ? r.cropKeys : [r.crop])),
    genericRows: REL_SAFE.filter((r) => r.cropKeys.length > 1).length,
    byProduct: tallyBy(REL_SAFE, (r) => r.product),
    byTarget: tallyBy(REL_SAFE, (r) => r.target),
    timingKnownCount: REL_SAFE.filter((r) => r.timing).length,
    /* THE THREE STRENGTHS, SIDE BY SIDE AND NEVER ADDED. A view showing this
       must show three numbers; there is no total to show. */
    byLinkStrength: tallyBy(regulatoryLinks.records, (r) => r.linkStrength),
    linkStrengthsDoNotSum: true,
    documentJoinCount: REL_SAFE.filter((r) => r.linkIsDocumentJoin).length,
    /* The two figures the mission names, measured from the rows rather than
       asserted — over the WHOLE layer, because they describe the label corpus,
       and again over the client-safe part, because that is what may sustain a
       claim. They are two different numbers and both are published. */
    labelCrops: uniq(regulatoryLinks.records.map((r) => r.cropOnLabel)).length,
    labelTargets: uniq(regulatoryLinks.records.map((r) => r.targetOnLabel)).length,
    labelCropsClientSafe: uniq(REL_SAFE.map((r) => r.cropOnLabel)).length,
    labelTargetsClientSafe: uniq(REL_SAFE.map((r) => r.targetOnLabel)).length,
    distinctPairs: uniq(regulatoryLinks.records.map((r) => [r.productKey, r.cropOnLabel, r.targetOnLabel].join('|'))).length,
    productsNamed: uniq(REL_SAFE.map((r) => r.product)).length,
  });

  /* 2 · EVERY label-use row the package carries, one row each.
     A row proves the product is authorised on the crop against that target — a
     real relationship, weaker than a read verdict because the issue
     vocabularies are not the same list: the label names a Latin target, the
     canonical window names an English issue. The row therefore keeps the Latin
     target as its issue and never pretends to be an issue match.

     TWO LAYERS, TWO QUESTIONS, AND THEY ARE NOT THE SAME COUNT.
       regulatoryLinks       every LINE of the document — 2030 rows, because
                             the same crop x target x product is legitimately
                             proved by a row of the use table AND by a block of
                             the crop, and both lines are evidence.
       productRelationships  the DISTINCT relationship — one row per
                             crop x target x product at its strongest. The
                             package's own law is that the three LINK_STRENGTH
                             values do not sum, so a pair proved twice is one
                             relationship, not two.
     Publishing the second as 2030 would be publishing a double count.

     THE GATE, APPLIED WITHOUT DELETING ANYTHING. The 518 CLIENT_SAFE=false
     rows are the DECLARACAO_DE_PRODUTO family: two separate lists on the
     product put side by side by us, not the document joining them. They enter
     this layer only where they are the ONLY thing said about a pair, they are
     marked clientSafe false, their strength is LABEL_CHECK_NEEDED because that
     is exactly what they are, and they can never overwrite an audited verdict
     or answer strengthFor(). */
  const labelRowExtra = (l, safe) => ({
    evidenceKind: 'REGULATORY_USE_ROW',
    target: l.target, targetOnLabel: l.targetOnLabel, targetKind: l.targetKind,
    reg: l.reg, labelUrl: l.labelUrl, moaLabel: null,
    /* the document's own strength for this row, carried and never summed */
    linkStrength: l.linkStrength, linkMeans: l.linkMeans,
    quoteFromLabel: l.quoteFromLabel, notProves: l.notProves,
    labelRowId: l.id,
    clientSafe: safe,
    /* the QA state this relationship inherits, from the record it rests on */
    qaStatus: l.qaStatus, qaFrom: l.id,
    mappingRule: 'CROP_ON_LABEL:' + U(l.cropOnLabel),
    provenance: P.CANONICAL,
  });
  /* client-safe rows first, so an unreviewed pairing can never take a slot a
     read line would have filled */
  regulatoryLinks.records.forEach((l) => {
    if (!l.clientSafe || !l.product || !l.target) return;
    pushRel(l.cropKey || l.crop, l.target, l.product, 'RELATED_PORTFOLIO',
      'Authorised use row read inside the official label', l.labelUrl, labelRowExtra(l, true));
  });
  regulatoryLinks.records.forEach((l) => {
    if (l.clientSafe || !l.product || !l.target) return;
    const crop = l.cropKey || l.crop;
    if (seenRel[relKey(crop, l.target, l.product)]) return;
    pushRel(crop, l.target, l.product, 'LABEL_CHECK_NEEDED',
      'Two lists on the product put side by side; the document does not join them', l.labelUrl,
      labelRowExtra(l, false));
  });

  const productRelationships = coll(relRows, P.CANONICAL,
    'the distinct relationship per crop x target x product, at its strongest: the label audit over the authorised label-use rows; the demo case fixture is not a source',
    { source: 'ITALY_LABEL_VERDICTS + ' + (regulatoryLinks.source || 'ITALY_INGEST.LINKS') });
  Object.assign(productRelationships, {
    auditRows: LV_VERIFIED.length + LV_NOT_FOUND.length,
    labelRows: relRows.length - (LV_VERIFIED.length + LV_NOT_FOUND.length),
    strengthCounts: tallyBy(relRows, (r) => r.strength),
    byLinkStrength: tallyBy(relRows, (r) => r.linkStrength),
    linkStrengthsDoNotSum: true,
    lineLayer: 'regulatoryLinks',
    lineRows: regulatoryLinks.count,
    distinctNote: 'one row per crop x target x product; the line-by-line evidence is collections.regulatoryLinks and the two are never summed',
  });

  /* One row per crop key, for the panel that wants "what is authorised here".
     WHEAT_GENERIC is deliberately counted under both Wheat and Durum Wheat, and
     the overlap is declared on the row rather than resolved silently. */
  const portfolioLinksByCrop = (() => {
    const acc = {};
    regulatoryLinks.safeRecords.forEach((r) => {
      const keys = (r.cropKeys.length ? r.cropKeys : [r.crop]).filter(Boolean);
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

  /* ---- what the label rows say about each registry product --------------
     The old registry table carried `crops` and `targets` inline. V2.1 does
     not: it carries CROP_IDS on 112 of 163 and moves every crop x target
     statement into PRODUCT-RELATIONSHIPS, where each one has its own row, its
     own quote and its own strength.

     So the two fields are rebuilt from those rows, keyed on REGISTRATION_NUMBER
     — a join on the registry's own primary key, not a name match — and the
     crop-id list is merged in beside them. Nothing is inferred: a product with
     no client-safe label row keeps an empty targets list, which is the honest
     answer and the one the absence rule already covers. */
  (() => {
    const byReg = {};
    regulatoryLinks.safeRecords.forEach((l) => {
      if (!l.reg) return;
      const e = byReg[U(l.reg)] = byReg[U(l.reg)] || { crops: [], cropKeys: [], targets: [], rows: 0 };
      e.rows++;
      if (l.cropOnLabel) e.crops.push(l.cropOnLabel);
      l.cropKeys.forEach((k) => e.cropKeys.push(k));
      if (l.target) e.targets.push(l.target);
    });
    productsRegulatory.records.forEach((p) => {
      const e = byReg[U(p.reg)];
      if (!e) return;
      p.labelCrops = uniq(e.crops);
      p.targets = uniq(e.targets);
      p.crops = uniq(p.crops.concat(e.cropKeys));
      p.labelRowCount = e.rows;
    });
  })();

  /* ---- the joined product entity --------------------------------------- */
  const byName = {};
  const addProduct = (name, patch) => {
    const k = U(name);
    if (!k) return;
    byName[k] = Object.assign({ name: String(name).trim(), key: k, regulatory: null, commercial: null, links: [], relationships: [] }, byName[k], patch);
  };
  productsRegulatory.records.forEach((p) => addProduct(p.name, {
    regulatory: p, line: p.line, ai: p.ai, targets: p.targets, crops: p.crops,
    labelUrl: p.labelUrl, status: p.status, expiry: p.expiry,
    holder: p.holder, reg: p.reg, regCat: p.regCat, form: p.form,
    hrac: p.hrac, frac: p.frac, irac: p.irac,
    expiresInDays: p.expiresInDays, provenance: P.REAL_SOURCE,
  }));
  productsCommercial.records.forEach((p) => addProduct(p.name, {
    commercial: p, category: p.category, catalogUrl: p.catalogUrl,
    matchState: p.matchState, provenance: P.REAL_SOURCE,
  }));
  /* Relationships attach to the product entity from the relationship
     collection — never from a case fixture. The full record is kept beside the
     short link so a product page can show the window and the evidence without
     a second lookup. */
  productRelationships.records.forEach((r) => {
    const e = byName[U(r.product)];
    if (e) {
      e.links.push({ crop: r.crop, issue: r.issue, strength: r.strength, evidence: r.evidence, source: r.source, windowId: r.windowId, region: r.region, evidenceKind: r.evidenceKind, labelUrl: r.labelUrl, clientSafe: r.clientSafe !== false, caseId: null });
      e.relationships.push(r);
    }
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
    /* MoA is real for 70 of the 163 registry products. Reading it out of the
       three resistance-code lists turns a field that printed NON OSSERVABILE on
       every product into a real value on the ones that have one — and leaves it
       honestly empty on the rest. */
    const moa = [
      A(e.hrac).length ? 'HRAC ' + A(e.hrac).join('/') : null,
      A(e.frac).length ? 'FRAC ' + A(e.frac).join('/') : null,
      A(e.irac).length ? 'IRAC ' + A(e.irac).join('/') : null,
    ].filter(Boolean);
    const uses = regulatoryLinks.records.filter((r) => r.productKey === k);
    return Object.assign(e, {
      categoryLabel: CATEGORY_OF(e),
      inRegulatory: !!e.regulatory,
      inCommercial: !!e.commercial,
      /* In the catalog but with no registry match: a real state the catalog
         itself declares, not a missing record. */
      catalogOnly: !e.regulatory && !!e.commercial,
      aiList: A(e.ai), aiLabel: A(e.ai).join(' + ') || null,
      moaList: moa, moaLabel: moa.length ? moa.join(' + ') : null,
      registeredUses: uses, registeredUseCount: uses.length,
      verifiedLinks: e.links.filter((l) => l.strength === 'VERIFIED_LABEL_MATCH'),
      relatedLinks: e.links.filter((l) => l.strength === 'RELATED_PORTFOLIO'),
      checkNeededLinks: e.links.filter((l) => l.strength === 'LABEL_CHECK_NEEDED'),
      rejectedLinks: e.links.filter((l) => l.strength === 'NO_CONFIRMED_MATCH_CURRENT_READING'),
      labelAuditDate: S(RAW.LABEL_AUDIT.AUDIT_DATE),
      labelAuditScopeNote: S(RAW.LABEL_AUDIT.SCOPE_NOTE),
      absenceRule: ABSENCE_RULE_TEXT,
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
  /* V2.1 COMPETITOR-ACTIVITIES.json: 577 rows against 503, and the two feeds
     that used to be separate arrive as one family — 414 paid ads with
     COUNTRY_REACHED and 147 organic videos with CHANNEL / VIEWS / PUBLISHED_AT.
     LAW: AD_REACHED_COUNTRY is not AD_TARGETED_COUNTRY, and communication is
     not market share. Both statements travel per record. */
  const competitorActivities = build('competitorActivities', [
    V21('competitors', (a) => {
      const type = S(a.ACTIVITY_TYPE);
      const paid = U(type) === 'PAID' || U(type) === 'PAID_AD';
      const sem = U(a.COUNTRY_SEMANTICS);
      const country = U(a.COUNTRY_REACHED);
      const italyReach = paid && (sem.indexOf('IT') >= 0 || country.indexOf('IT') >= 0);
      const crops = A(a.CROP_TERMS);
      const cropsCanonical = uniq(crops.map((c) => CROP_BY_LATIN[U(c)] || null).filter(Boolean)
        .concat(cropsFromV21Ids(a.CROP_IDS)));
      const generic = crops.filter((c) => GENERIC_CROP_TERMS[U(c)]);
      const issues = A(a.ISSUE_TERMS).filter(Boolean);
      const speciesIssues = issues.filter((i) => /^[A-Z][a-z]/.test(String(i).trim()));
      /* an organic video's own date field is PUBLISHED_AT, an ad's is
         START_DATE; neither is invented from the other */
      const start = isoOf(a.START_DATE) || isoOf(a.PUBLISHED_AT);
      const page = S(a.PAGE) || S(a.CHANNEL);
      return Object.assign(v21spine(a), {
        type, platform: S(a.PLATFORM),
        company: S(a.COMPANY), companyRaw: S(a.COMPANY), companyKey: U(a.COMPANY),
        page, pageId: S(a.PAGE_ID),
        displayName: page || S(a.COMPANY) || S(a.TITLE),
        channelResolved: !!page,
        country: S(a.COUNTRY_REACHED), countrySem: S(a.COUNTRY_SEMANTICS),
        geoClass: italyReach ? 'REACHED_IN_ITALY' : paid ? 'REACH_NOT_RESOLVED' : 'MULTI_COUNTRY_OR_UNRESOLVED',
        italyReach,
        /* §9 · reach is not targeting. The platform's own sentence travels
           with the record so no card can drop it. */
        geoCaveat: S(a.COUNTRY_SEMANTICS),
        startDate: start, endDate: isoOf(a.END_DATE),
        active: S(a.ACTIVE_STATUS), isActive: U(a.ACTIVE_STATUS) === 'ACTIVE',
        media: S(a.MEDIA_TYPE),
        products: A(a.PRODUCTS_PROVED),
        crops, cropsCanonical,
        cropScope: cropsCanonical.length ? 'RESOLVED' : generic.length ? 'GENERIC_TERM' : 'NOT_OBSERVED',
        genericCropTerms: generic,
        issues, issuesObserved: issues,
        issueScope: speciesIssues.length ? 'SPECIES' : issues.length ? 'GENERIC_TERM' : 'NOT_OBSERVED',
        speciesIssues,
        /* the advertiser's own public copy, quoted and never parsed */
        text: S(a.CREATIVE_TEXT) || S(a.DESCRIPTION),
        textExcerpt: S(a.CREATIVE_TEXT) || S(a.DESCRIPTION),
        url: S(a.AD_URL) || S(a.URL),
        /* the organic side of the corpus, which the old table had no slot for */
        channel: S(a.CHANNEL), title: S(a.TITLE),
        views: N(a.VIEWS), commentsCount: N(a.COMMENTS_COUNT),
        caseId: S(a.CASE_ID),
        sourceId: S(a.SOURCE_ID),
        hasDate: !!start,
        dateState: start ? 'OBSERVED' : 'NOT_OBSERVED',
        /* still structurally empty: nothing upstream bridges the advertiser's
           Latin binomial to the canonical window's English issue name */
        relatedWindows: [],
        relatedWindowsState: 'NO_ISSUE_SYNONYM_TABLE_UPSTREAM',
        daysFromRef: daysFrom(start),
        reachIsNotTargeting: true,
        communicationIsNotMarketShare: true,
      });
    }),
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
          /* STRUCTURALLY EMPTY, and that is the finding.
             A window link would need the advertiser's issue term to equal the
             canonical window's ISSUE_NAME. The advertiser writes Latin
             binomials ('Plasmopara viticola') and the window writes English
             issue names ('Downy Mildew'); nothing upstream bridges the two, and
             a shared crop name is not a relationship. Falling back to crop-only
             matching would manufacture 132 links that no evidence supports, so
             this stays empty until an upstream synonym table exists. The
             window-side view of the same question is competitorWindowMoments,
             which counts activities per crop and says so in its label. */
          relatedWindows: [],
          relatedWindowsState: 'NO_ISSUE_SYNONYM_TABLE_UPSTREAM',
          daysFromRef: daysFrom(a.start),
          provenance: provOf(a, P.REAL_SOURCE), raw: a,
        };
      },
      validate: (r) => (!r.id ? 'no id' : !r.company ? 'no company' : null),
    },
  ], 'observed public competitor communication; Italy reach only where the evidence supports it');
  v21law(competitorActivities, 'competitors');

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
  /* A record with no COMPANY is not filed under an empty company: 16 of the
     577 rows are corpus stubs or claim rows that name no advertiser, and an
     '' bucket would publish a seventeenth company that does not exist. */
  competitorActivities.records.forEach((a) => { if (a.companyKey) (compActByCompany[a.companyKey] = compActByCompany[a.companyKey] || []).push(a); });

  /* NO V2.1 CANDIDATE: the package has no companies table. The counter table
     stays ITALY_INGEST's, and the observed totals beside it are recomputed
     from the V2.1 activity corpus, so a divergence between the two is visible
     rather than averaged away. */
  const competitorCompanies = build('competitorCompanies', [
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

  /* NO V2.1 CANDIDATE either: PRODUCTS_PROVED lives on the activity row in
     V2.1, so the per-product table stays ITALY_INGEST's and its context is
     recomputed from the activities that actually name the product. */
  const competitorProducts = build('competitorProducts', [
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
  /* V2.1 MARKET-OBSERVATIONS.json, 157 rows: the 77 price quotes the old table
     had, 13 written market claims over them, and 67 corpus stubs. LAW: a
     PIAZZA price is not a NATIONAL price, and a stopped series keeps its last
     value and looks current. Both are carried per row. */
  const marketObservations = build('marketObservations', [
    V21('market', (m) => {
      const per = String(m.REFERENCE_PERIOD || '').split('..');
      const periodStart = dmyToIso(per[0]);
      const periodEnd = dmyToIso(per[1] || per[0]);
      const seriesKey = U(m.GROUP) + '|' + (m.PRODUCT === null || m.PRODUCT === undefined ? '' : String(m.PRODUCT));
      const cropKey = MARKET_CROP[seriesKey] || MARKET_CROP[U(m.GROUP) + '|*'] || cropsFromV21Ids(m.CROP_IDS)[0] || null;
      const stopped = /^PARADA_EM_(\d{4})$/.exec(U(m.SERIES_STATE));
      return Object.assign(v21spine(m), {
        group: S(m.GROUP), product: S(m.PRODUCT), market: S(m.MARKET),
        priceRaw: S(m.PRICE_RAW), price: N(m.PRICE_NUM), unit: S(m.UNIT), stage: S(m.STAGE),
        referencePeriod: S(m.REFERENCE_PERIOD), publicationDate: S(m.PUBLICATION_DATE),
        publicationDateISO: isoOf(m.PUBLICATION_DATE),
        geography: S(m.GEOGRAPHY),
        cropKey, cropKeys: cropsFromV21Ids(m.CROP_IDS), seriesKey,
        periodStart, periodEnd,
        daysSinceObservation: periodEnd ? daysFrom(periodEnd) : null,
        isCurrentSeries: U(m.SERIES_STATE) === 'CORRENTE',
        stoppedYear: stopped ? Number(stopped[1]) : null,
        hasStage: !!S(m.STAGE),
        hasPublicationDate: !!S(m.PUBLICATION_DATE),
        prevPrice: N(m.PREV_PRICE_NUM), changeVsPrev: N(m.CHANGE_VS_PREV_PCT),
        yearAgoPrice: N(m.YEAR_AGO_PRICE_NUM), changeVsYearAgo: N(m.CHANGE_VS_YEAR_AGO_PCT),
        seriesState: S(m.SERIES_STATE),
        seriesWarning: S(m.SERIES_WARNING),
        /* the warning now has an approved Italian and English variant */
        seriesWarningText: narrative(m, 'SERIES_WARNING'),
        observations: N(m.OBSERVATIONS_IN_SERIES), sourceId: S(m.SOURCE_ID),
        publishedDaysAgo: daysFrom(isoOf(m.PUBLICATION_DATE)),
        /* new in V2.1: which point of the chain the price belongs to, and
           whether the crop behind it was derived rather than published */
        commodityStage: S(m.COMMODITY_STAGE),
        commodityStageLaw: S(m.COMMODITY_STAGE_LAW),
        derivedFromCropId: S(m.DERIVED_FROM_CROP_ID),
        piazzaIsNotNational: true,
        ui: { marketCropKey: cropKey ? MARKET_VIEW_KEY[cropKey] || null : null },
      });
    }),
    {
      source: 'ITALY_INGEST.MARKET',
      precedence: P.REAL_SOURCE,
      rows: RAW.IG.MARKET,
      adapt: (m) => {
        /* REFERENCE_PERIOD is 'dd/mm/yyyy..dd/mm/yyyy' on 77/77 rows. Parsing
           it here means no screen ever has to open a second clock to know how
           old a quote is (§6). */
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
  v21law(marketObservations, 'market');

  /* ---- SCIENCE ---------------------------------------------------------- */
  const scienceRecords = build('scienceRecords', [
    V21('science', (r) => Object.assign(v21spine(r), {
      title: S(r.TITLE), doi: S(r.DOI),
      author: S(r.AUTHOR), orcid: S(r.ORCID), institution: S(r.INSTITUTION),
      publishedAt: S(r.PUBLISHED_AT), date: S(r.PUBLISHED_AT),
      year: S(r.PUBLISHED_AT) ? String(r.PUBLISHED_AT).slice(0, 4) : null,
      venue: S(r.VENUE), materialType: S(r.MATERIAL_TYPE), materialRole: S(r.MATERIAL_ROLE),
      crop: S(r.CROP), cropKeys: cropsFromV21Ids(r.CROP_IDS),
      issue: S(r.ISSUE), countryOfFact: S(r.COUNTRY_OF_FACT),
      url: S(r.SOURCE_URL), sourceId: S(r.SOURCE_ID),
    }), { validate: (r) => (!r.id ? 'no ID' : !r.title ? 'no title' : null) }),
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
  v21law(scienceRecords, 'science');

  /* AFFILIATION_CAVEAT is the source registry's own limitation, restated as a
     value so it can travel with every institution the portal shows. An
     affiliation belongs to the AUTHOR, not to the study: reading it as
     "research done in this region" is the single easiest error on this screen. */
  const AFFILIATION_CAVEAT = 'The affiliation belongs to the author, not to the study.';

  const researchers = build('researchers', [
    V21('researchers', (r) => Object.assign(v21spine(r), {
      name: S(r.PERSON), category: S(r.CATEGORY),
      orcid: /^https?:\/\/orcid\.org\//i.test(S(r.ORCID) || '') ? S(r.ORCID) : null,
      openAlexId: S(r.OPENALEX_ID), openalexId: S(r.OPENALEX_ID),
      institutions: A(r.INSTITUTIONS),
      org: A(r.INSTITUTIONS).join(' · ') || null,
      orgLabel: A(r.INSTITUTIONS).join(' · ') || null,
      affiliationCaveat: AFFILIATION_CAVEAT,
      theme: S(r.THEME), themeKey: S(r.THEME),
      themeLabel: (THEME_UI[U(r.THEME)] || {}).title || null,
      worksInScope: N(r.WORKS_IN_SCOPE),
      lastActivity: S(r.LAST_ACTIVITY),
      daysFromRef: daysFrom(r.LAST_ACTIVITY),
      identityStatus: S(r.IDENTITY_STATUS), identityState: S(r.IDENTITY_STATUS),
      /* ROLE and FACT_REGION are still the analyst's unknown sentence on 60/60
         in V2.1; UNK keeps them out of a filter and out of a column. */
      role: UNK(r.ROLE), factRegion: UNK(r.FACT_REGION),
      sourceId: S(r.SOURCE_ID),
    }), { validate: (r) => (!r.id ? 'no ID' : !r.name ? 'no person' : null) }),
    {
      source: 'ITALY_INGEST.RESEARCHERS',
      precedence: P.REAL_SOURCE,
      rows: RAW.IG.RESEARCHERS,
      adapt: (r) => ({
        id: r.ID, name: S(r.PERSON), category: S(r.CATEGORY),
        /* ORCID is a link only when it is one: 6 of 60 carry the unknown
           sentence in this field instead of a URL. */
        orcid: /^https?:\/\/orcid\.org\//i.test(S(r.ORCID) || '') ? S(r.ORCID) : null,
        openAlexId: S(r.OPENALEX_ID), openalexId: S(r.OPENALEX_ID),
        institutions: A(r.INSTITUTIONS),
        org: A(r.INSTITUTIONS).join(' · ') || null,
        orgLabel: A(r.INSTITUTIONS).join(' · ') || null,
        affiliationCaveat: AFFILIATION_CAVEAT,
        theme: S(r.THEME), themeKey: S(r.THEME),
        themeLabel: (THEME_UI[U(r.THEME)] || {}).title || null,
        /* WORKS_IN_SCOPE counts works INSIDE the monitored query, not a career
           total. The field name says scope so no label can drop it. */
        worksInScope: N(r.WORKS_IN_SCOPE),
        lastActivity: S(r.LAST_ACTIVITY),
        daysFromRef: daysFrom(r.LAST_ACTIVITY),
        /* Identity is stated by the source and never upgraded by the portal.
           ORCID_PRESENT_NOT_RESOLVED_HERE is not a confirmed identity. */
        identityStatus: S(r.IDENTITY_STATUS), identityState: S(r.IDENTITY_STATUS),
        /* ROLE and FACT_REGION are the analyst's unknown sentence on 60/60.
           They resolve to null so the screen renders its own "non noto" and no
           filter is populated with a Portuguese note. */
        role: UNK(r.ROLE), factRegion: UNK(r.FACT_REGION),
        sourceId: S(r.SOURCE_ID),
        provenance: provOf(r, P.REAL_SOURCE), raw: r,
      }),
      validate: (r) => (!r.id ? 'no ID' : !r.name ? 'no person' : null),
    },
  ], 'real researcher identities; identity status is never promoted and the unknown role never leaks');
  v21law(researchers, 'researchers');

  /* NO V2.1 CANDIDATE: the package carries no bibliometric-theme table. */
  const scienceThemes = build('scienceThemes', [
    {
      source: 'ITALY_INGEST.THEMES',
      precedence: P.REAL_SOURCE,
      rows: RAW.IG.THEMES,
      adapt: (t) => {
        const ui = THEME_UI[U(t.THEME)] || {};
        const top = t.INSTITUTIONS_TOP && typeof t.INSTITUTIONS_TOP === 'object' ? t.INSTITUTIONS_TOP : {};
        return {
          id: t.ID, key: t.ID, theme: S(t.THEME),
          /* A controlled display title per token — NOT a translation of the
             token and NOT a scientific claim. The QUERY below is the honest
             definition of what WORKS actually counted. */
          title: ui.title || S(t.THEME),
          query: S(t.QUERY),
          cropToken: ui.cropToken || null, issueToken: ui.issueToken || null,
          cropCanonical: ui.cropToken ? CROP_BY_TOKEN[ui.cropToken] || null : null,
          works: N(t.WORKS), authorsIt: N(t.AUTHORS_IT),
          authorsWithOrcid: N(t.AUTHORS_WITH_ORCID),
          /* A headcount of authors active since 2024. It is not a movement and
             no trend can be derived from it — there is no earlier headcount. */
          authorsActiveSince2024: N(t.AUTHORS_ACTIVE_SINCE_2024),
          institutionsTop: top,
          topInstitutions: Object.keys(top).map((k) => ({ name: k, works: top[k] })),
          affiliationCaveat: AFFILIATION_CAVEAT,
          sourceId: S(t.SOURCE_ID),
          ui: categoryOf(ui.issueType),
          provenance: provOf(t, P.REAL_SOURCE), raw: t,
        };
      },
      validate: (r) => (!r.id ? 'no ID' : null),
    },
  ], 'bibliometric themes; a grouping for navigation, not a scientific conclusion');

  /* Join the two directions of the theme relation. Both are counts over real
     records; neither can create a theme and neither can create a record. */
  scienceThemes.records.forEach((t) => {
    t.recordCount = scienceRecords.records.filter((r) => U(r.crop) === U(t.cropToken) && U(r.issue) === U(t.issueToken)).length;
    t.researcherCount = researchers.records.filter((r) => U(r.theme) === U(t.theme)).length;
  });
  scienceRecords.records.forEach((r) => {
    const t = scienceThemes.records.find((x) => U(x.cropToken) === U(r.crop) && U(x.issueToken) === U(r.issue));
    /* null on the records that match no theme — they must stay reachable
       outside the theme grouping rather than be filed under the nearest one. */
    r.themeKey = t ? t.id : null;
    r.themeTitle = t ? t.title : null;
  });

  /* ---- SCIENCE INSTITUTIONS · derived ----------------------------------
     Two different real sources say "institution" and they do NOT mean the same
     thing, so they are never blended:
       · this collection = the FIRST-AUTHOR affiliation on the 88 ingested
         records (6 distinct);
       · scienceThemes[].institutionsTop = OpenAlex work counts for the whole
         theme query (37 distinct across five themes).
     There is no institution TYPE field in either source, so none is published:
     "University / National research body / Research foundation" was a guess
     made from the first word of a name. */
  const scienceInstitutions = (() => {
    const t = tallyBy(scienceRecords.records, (r) => r.institution);
    const rows = byCountDesc(t).map((name) => ({
      id: 'SCI-INST-' + U(name).replace(/[^A-Z0-9]+/g, '-').slice(0, 40),
      name, recordCount: t[name],
      source: 'FIRST_AUTHOR_AFFILIATION',
      affiliationCaveat: AFFILIATION_CAVEAT,
      provenance: P.REAL_DERIVED,
    }));
    return coll(rows, P.REAL_DERIVED, 'first-author affiliation on the ingested records; affiliation means author, not study, and there is no institution type upstream', { source: 'derived · scienceRecords' });
  })();

  /* ---- PUBLICATIONS FOR A PERSON · the join, measured ---------------------
     WHAT IDENTIFIERS ARE ACTUALLY AVAILABLE. The researchers index carries
     ORCID (54 of 60) and an OpenAlex AUTHOR id (60 of 60). The science records
     carry AUTHOR, ORCID and a DOI — and NO OpenAlex author id at all: measured,
     there is no such key anywhere in ITALY_INGEST.SCIENCE. So an OpenAlex-keyed
     join is not available in this package, however much one would want it, and
     an id-keyed join does not exist either: the two tables have no shared row
     id. ORCID is the only identifier both sides publish.

     WHAT THE JOIN ACTUALLY RETURNS, measured on this package:
       88 science records · 88 carry an ORCID · 7 DISTINCT ORCIDs · 7 distinct
       authors (the records carry the FIRST author only)
       60 researchers · 54 carry an ORCID
       1 researcher is one of those 7 authors: IT-PER-013 Massimo Blandino, 25
       records. A folded-name join finds the same one person and nobody else.
     So this returns [] for 59 of 60 researchers because the package holds no
     publication of theirs — not because a flag is broken. The empty panel must
     be omitted for THAT person; it must never be filled from the theme the
     person happens to sit in, which would list papers they did not write.

     The ORCID is normalized on BOTH sides. It used to be stripped of its
     https://orcid.org/ prefix on the person side only and then compared with
     === against the raw record field: one science record published as a URL, or
     one written without hyphens, and this join would have silently gone to zero
     with nothing on any screen to show it. The normalized value must look like
     an ORCID (15 digits and a check character) or it is not a key at all, so
     the analyst's unknown sentence can never collapse into a match. */
  const orcidKey = (v) => {
    const k = String(v === null || v === undefined ? '' : v).trim()
      .replace(/^https?:\/\/(?:www\.)?orcid\.org\//i, '').replace(/[^0-9Xx]/g, '').toUpperCase();
    return /^[0-9]{15}[0-9X]$/.test(k) ? k : null;
  };
  const worksByOrcid = {};
  scienceRecords.records.forEach((r) => {
    const k = orcidKey(r.orcid);
    if (k) (worksByOrcid[k] = worksByOrcid[k] || []).push(r);
  });
  /* Accepts a person record OR a person id, so a screen that only has the id
     from the route does not have to find the record first and does not have to
     rebuild its own ORCID index to do it. */
  const publicationsForPerson = (person) => {
    const rec = person && typeof person === 'object' ? person
      : (people.records.filter((p) => U(p.id) === U(person))[0]
        || researchers.records.filter((r) => U(r.id) === U(person))[0] || null);
    if (!rec) return [];
    const k = orcidKey(rec.orcid || rec.ORCID);
    return k ? (worksByOrcid[k] || []).slice() : [];
  };

  /* A localized COMMON NAME is a name, not a sentence.
     Two of the 34 GIRE records answer SPECIES_IT with a research note in
     Portuguese instead of an Italian name, because the source card does not
     carry one: IT-RES-019 opens "NAO SEI — a ficha nao traz nome comum
     italiano...", and IT-RES-028 opens with the genus and only then explains
     "...NAO SEI se existe um nome vulgar italiano distinto". The sentinel alone
     catches only the first, since the second begins with a real word.
     So the gate is structural rather than linguistic: a common name is short
     and carries no explanatory clause. When it fails, the field is dropped and
     the view falls back to the botanical name, which is a fact and is never
     translated anyway. Dropping is right — the note is TRUE and useful to a
     researcher, but it is an admission that the Italian name is unknown, and
     printing it would put a Portuguese apology where a species name belongs. */
  const displayName = (v) => {
    const t = S(v);
    if (!t) return '';
    if (UNKNOWN_SENTINEL.test(t)) return '';
    if (t.length > 40) return '';
    if (/\s[—–]\s/.test(t)) return '';
    return t;
  };

  const resistance = build('resistance', [
    V21('resistance', (r) => {
      const cr = cropResolve(r.CROP_DECLARED);
      return Object.assign(v21spine(r), {
        species: S(r.SPECIES), speciesIt: displayName(r.SPECIES_IT), family: S(r.FAMILY),
        mechanism: narrative(r, 'MECHANISM'),
        mechanismStated: !!S(r.MECHANISM) && !UNKNOWN_SENTINEL.test(S(r.MECHANISM)),
        /* CROP_DECLARED is still the source's own sentence; the crop is
           resolved for display and filtering and the sentence never lands on
           a screen unless the package approved a localized variant. */
        crop: cr.label, cropRaw: UNK(r.CROP_DECLARED),
        cropKey: cr.key || cropsFromV21Ids(r.CROP_IDS)[0] || null,
        cropKeys: uniq(cr.keys.concat(cropsFromV21Ids(r.CROP_IDS))),
        cropScope: cr.scope, cropDeclared: narrative(r, 'CROP_DECLARED'),
        cropIsProse: (S(r.CROP_DECLARED) || '').length > 60,
        firstCaseYear: S(r.FIRST_CASE_YEAR),
        regions: A(r.REGIONS), multiple: !!r.MULTIPLE_RESISTANCE,
        multipleResistance: narrative(r, 'MULTIPLE_RESISTANCE'),
        citation: S(r.CITATION), authority: S(r.AUTHORITY),
        url: S(r.SOURCE_URL), sourceId: S(r.SOURCE_ID),
      });
    }, { validate: (r) => (!r.id ? 'no ID' : !r.species ? 'no species' : null) }),
    {
      source: 'ITALY_INGEST.RESISTANCE',
      precedence: P.REAL_SOURCE,
      rows: RAW.IG.RESISTANCE,
      adapt: (r) => ({
        id: r.ID,
        /* A taxonomic name is never truncated, including a parenthetical
           synonym: the synonym is part of the identification. */
        species: S(r.SPECIES), speciesIt: displayName(r.SPECIES_IT), family: S(r.FAMILY),
        mechanism: narrative(r, 'MECHANISM'),
        mechanismStated: !!S(r.MECHANISM) && !UNKNOWN_SENTINEL.test(S(r.MECHANISM)),
        /* CROP_DECLARED is the source's own free sentence, sometimes several
           lines long and once the unknown sentence. It is a quotation of the
           record sheet, not a crop key, so it is exposed as prose with a flag
           and never fed to a crop filter. */
        /* CROP_DECLARED is the source's own Portuguese sentence. The crop is
           resolved for display and filtering; the sentence itself is a research
           note and never reaches the screen. */
        crop: cropResolve(r.CROP_DECLARED).label, cropRaw: UNK(r.CROP_DECLARED),
        cropKey: cropResolve(r.CROP_DECLARED).key, cropKeys: cropResolve(r.CROP_DECLARED).keys,
        cropScope: cropResolve(r.CROP_DECLARED).scope, cropDeclared: null,
        cropIsProse: (S(r.CROP_DECLARED) || '').length > 60,
        firstCaseYear: S(r.FIRST_CASE_YEAR),
        regions: A(r.REGIONS), multiple: !!r.MULTIPLE_RESISTANCE,
        citation: S(r.CITATION), authority: S(r.AUTHORITY),
        url: S(r.SOURCE_URL), sourceId: S(r.SOURCE_ID),
        provenance: provOf(r, P.REAL_SOURCE), raw: r,
      }),
      validate: (r) => (!r.id ? 'no ID' : !r.species ? 'no species' : null),
    },
  ], 'confirmed Italian resistance cases');
  v21law(resistance, 'resistance');

  /* ---- PUBLIC VOICES ----------------------------------------------------
     V2.1 PUBLIC-VOICES.json, 79 rows: 58 identified voices and 21 audience
     comments, 65 client-safe. LAW: A VOICE IS NOT AN INDEPENDENT SOURCE. Four
     people quoted in one article are four voices and ONE document, so
     SOURCE_DOCUMENT_ID travels per row and convergence is counted on it,
     never on the number of people. */
  const publicVoices = build('publicVoices', [
    V21('voices', (v) => Object.assign(v21spine(v), {
      kind: S(v.KIND), voiceKind: S(v.VOICE_KIND),
      voiceId: S(v.VOICE_ID), personId: S(v.PERSON_ID),
      /* the join key for convergence, and the only one that is honest */
      sourceDocumentId: S(v.SOURCE_DOCUMENT_ID),
      person: S(v.PERSON), identityState: S(v.PERSON_IDENTITY_STATE),
      role: UNK(v.ROLE), organization: UNK(v.ORGANIZATION),
      roleEvidence: narrative(v, 'ROLE_EVIDENCE'),
      audienceKind: S(v.AUDIENCE_KIND) || S(v.CHANNEL_AUDIENCE_KIND),
      audienceEvidence: S(v.CHANNEL_AUDIENCE_EVIDENCE),
      platform: S(v.PLATFORM), channel: S(v.CHANNEL), title: S(v.CONTENT_TITLE),
      date: UNK(v.DATE), dateISO: isoOf(v.DATE), dateState: dateStateOf(v.DATE),
      dateRelative: S(v.DATE_RELATIVE), dateNote: S(v.DATE_NOTE),
      crop: S(v.CROP), cropCanonical: cropResolve(v.CROP).key || cropsFromV21Ids(v.CROP_IDS)[0] || null,
      cropKeys: cropsFromV21Ids(v.CROP_IDS),
      issue: S(v.ISSUE), caseId: S(v.CASE_ID),
      region: UNK(v.REGION), countryOfFact: S(v.COUNTRY_OF_FACT),
      /* the original public quote: never translated, never parsed for facts */
      textOriginal: S(v.TEXT_ORIGINAL),
      sourceUrl: S(v.SOURCE_URL), sourceId: S(v.SOURCE_ID),
      daysFromRef: daysFrom(isoOf(v.DATE)),
      voiceIsNotAnIndependentSource: true,
    })),
    {
      source: 'ITALY_INGEST.VOICES',
      precedence: P.REAL_SOURCE,
      rows: RAW.IG.VOICES,
      adapt: (v) => ({
        id: v.ID, kind: S(v.KIND),
        person: S(v.PERSON), identityState: S(v.PERSON_IDENTITY_STATE),
        /* ROLE, ORGANIZATION, REGION and DATE are the analyst's unknown
           sentence on 17/17. Passing them through would put the same Portuguese
           note in four different columns and in four different filters. */
        role: UNK(v.ROLE), organization: UNK(v.ORGANIZATION),
        platform: S(v.PLATFORM), channel: S(v.CHANNEL), title: S(v.CONTENT_TITLE),
        date: UNK(v.DATE), dateISO: isoOf(v.DATE), dateState: dateStateOf(v.DATE),
        dateRelative: S(v.DATE_RELATIVE), dateNote: S(v.DATE_NOTE),
        /* through the resolver, not through CROP_BY_TOKEN alone: VOICES happens
           to write tokens today (VINE, MAIZE, DURUM_WHEAT — 17/17 resolve either
           way), but naming one vocabulary is what left the News crop null on
           records that spell the same crop in Italian. */
        crop: S(v.CROP), cropCanonical: cropResolve(v.CROP).key,
        issue: S(v.ISSUE), caseId: S(v.CASE_ID),
        region: UNK(v.REGION), countryOfFact: S(v.COUNTRY_OF_FACT),
        /* The original public quote is never translated and never parsed for
           facts. It is evidence, shown as published. */
        textOriginal: S(v.TEXT_ORIGINAL),
        proves: narrative(v, 'WHAT_IT_PROVES'),
        notProves: narrative(v, 'WHAT_IT_DOES_NOT_PROVE'),
        sourceUrl: S(v.SOURCE_URL), sourceId: S(v.SOURCE_ID),
        daysFromRef: daysFrom(isoOf(v.DATE)),
        provenance: provOf(v, P.REAL_SOURCE), raw: v,
      }),
      validate: (r) => (!r.id ? 'no ID' : null),
    },
  ], 'real public field voices; identity is never upgraded, the quote is never translated');
  v21law(publicVoices, 'voices');
  Object.assign(publicVoices, {
    /* the only convergence denominator the law allows */
    distinctSourceDocuments: uniq(publicVoices.safeRecords.map((v) => v.sourceDocumentId)).length,
    convergenceCountsDocumentsNotPeople: true,
    kindCounts: tallyBy(publicVoices.safeRecords, (v) => v.entityType),
  });

  const publicChannels = build('publicChannels', [
    V21('channels', (c) => {
      const host = (String(S(c.CHANNEL_URL) || '').match(/^https?:\/\/([^/]+)/i) || [])[1] || '';
      return Object.assign(v21spine(c), {
        name: S(c.CHANNEL), channel: S(c.CHANNEL), url: S(c.CHANNEL_URL),
        host: host || null,
        platform: /youtube\.com$/i.test(host.replace(/^www\./, '')) ? 'YouTube' : null,
        identityState: S(c.IDENTITY_STATE),
        contentTypeExample: S(c.CONTENT_TYPE_EXAMPLE),
        /* these four describe ONE example video, never the channel */
        exampleTitle: S(c.EXAMPLE_TITLE), exampleUrl: S(c.EXAMPLE_URL),
        examplePublishedAt: S(c.EXAMPLE_PUBLISHED_AT),
        examplePublishedISO: isoOf(c.EXAMPLE_PUBLISHED_AT),
        exampleViews: N(c.VIEWS), views: N(c.VIEWS),
        caseId: S(c.CASE_ID),
      });
    }),
    {
      source: 'ITALY_INGEST.CHANNELS',
      precedence: P.REAL_SOURCE,
      rows: RAW.IG.CHANNELS,
      adapt: (c) => {
        /* There is no PLATFORM field upstream. The host of the real channel URL
           is evidence, so reading it is a derivation, not an assumption —
           measured: 30/30 are youtube.com. A URL with any other host resolves
           to null rather than to a guess. */
        const host = (String(S(c.CHANNEL_URL) || '').match(/^https?:\/\/([^/]+)/i) || [])[1] || '';
        return {
          id: c.ID, name: S(c.CHANNEL), channel: S(c.CHANNEL), url: S(c.CHANNEL_URL),
          host: host || null,
          platform: /youtube\.com$/i.test(host.replace(/^www\./, '')) ? 'YouTube' : null,
          /* NOT_PROVED on 30/30: no channel is a proven identity, and no screen
             may present one as a named person. */
          identityState: S(c.IDENTITY_STATE),
          contentTypeExample: S(c.CONTENT_TYPE_EXAMPLE),
          /* These four describe ONE example video, not the channel. The names
             say example so a card cannot label them as channel statistics. */
          exampleTitle: S(c.EXAMPLE_TITLE), exampleUrl: S(c.EXAMPLE_URL),
          examplePublishedAt: S(c.EXAMPLE_PUBLISHED_AT),
          examplePublishedISO: isoOf(c.EXAMPLE_PUBLISHED_AT),
          exampleViews: N(c.VIEWS), views: N(c.VIEWS),
          caseId: S(c.CASE_ID), provenance: provOf(c, P.REAL_SOURCE), raw: c,
        };
      },
      validate: (r) => (!r.id ? 'no ID' : null),
    },
  ], 'real Italian public channels; the example video is labelled as an example, never as the channel');
  v21law(publicChannels, 'channels');

  /* NO V2.1 CANDIDATE: the package has no PEOPLE table; identity and role
     evidence live on the voice record instead. This list stays ITALY_INGEST's. */
  const publicPeople = build('publicPeople', [
    {
      source: 'ITALY_INGEST.PEOPLE',
      precedence: P.REAL_SOURCE,
      rows: RAW.IG.PEOPLE,
      adapt: (p) => ({
        id: p.ID, name: S(p.PERSON), person: S(p.PERSON), category: S(p.CATEGORY),
        org: S(p.ORGANIZATION), organization: S(p.ORGANIZATION),
        institutions: S(p.ORGANIZATION) ? [S(p.ORGANIZATION)] : [],
        role: UNK(p.ROLE),
        /* Knowing WHO someone is and knowing WHAT they do are different facts
           with different evidence. The source states both separately and the
           portal must never merge them into one claim. */
        identityEvidence: S(p.IDENTITY_EVIDENCE), roleEvidence: S(p.ROLE_EVIDENCE),
        law: narrative(p, 'LAW'), country: S(p.COUNTRY),
        provenance: provOf(p, P.REAL_SOURCE), raw: p,
      }),
      validate: (r) => (!r.id ? 'no ID' : !r.name ? 'no person' : null),
    },
  ], 'public people with stated identity evidence; identity evidence and role evidence stay separate');

  /* Presentation labels per CATEGORY. Only categories with at least one record
     are emitted, so an empty chip can never appear. */
  const PERSON_CATEGORY_LABEL = {
    RESEARCHER: 'RESEARCHERS', INSTITUTIONAL_EXPERT: 'INSTITUTIONAL EXPERTS',
    CREATOR: 'INFLUENCERS / CREATORS', COMPANY_PERSON: 'COMPANY PEOPLE',
  };
  const categoryIndex = (records) => {
    const t = tallyBy(records, (r) => r.category);
    return byCountDesc(t).map((k) => ({ key: k, label: PERSON_CATEGORY_LABEL[U(k)] || k, count: t[k] }));
  };
  Object.assign(publicPeople, {
    categories: categoryIndex(publicPeople.records),
    institutions: (() => {
      const t = tallyBy(publicPeople.records, (r) => r.institutions);
      return byCountDesc(t).map((name) => ({ name, people: t[name] }));
    })(),
  });

  /* ---- PEOPLE · the one directory --------------------------------------
     The two upstream lists overlap: 9 of the 15 evidence-bearing PEOPLE records
     are the same human as a RESEARCHERS record under a differently-accented
     spelling. Summing them would publish 75 monitored people where 66 records
     exist. The merge is keyed on the diacritic-folded name and happens once,
     here, so no screen has to know about it.

     One name ('Alberto Alma') legitimately appears twice inside RESEARCHERS
     under two themes and two ids; both rows are kept, because collapsing them
     would silently drop a theme membership. That is why 66 records carry 65
     distinct names, and the difference is published rather than smoothed. */
  const nameKey = (v) => fold(String(v || '')).toLowerCase().trim();
  /* Membership of the bibliometric index, by the researcher's own record id.
     isResearcher answers ONE question — "is this row a row of
     collections.researchers?" — and it is derived from that collection, not
     from any other field and above all not from whether the person happens to
     have a publication in this package. Those are two different facts and a
     screen that conflates them tells the reader that 59 of the 60 people in the
     bibliometric index are not researchers. hasPublications is the second fact,
     published separately, and it is the one a publications panel must be
     guarded on. */
  const researcherIds = {};
  researchers.records.forEach((r) => { if (r.id) researcherIds[U(r.id)] = r; });
  const people = (() => {
    const rows = researchers.records.map((r) => Object.assign({}, r, {
      alsoIds: [], roleCat: PERSON_CATEGORY_LABEL[U(r.category)] || r.category,
      identityEvidence: null, roleEvidence: null,
      isResearcher: !!researcherIds[U(r.id)], researcherId: r.id, isEvidenceRecord: false,
    }));
    const byNorm = {};
    rows.forEach((r) => { (byNorm[nameKey(r.name)] = byNorm[nameKey(r.name)] || []).push(r); });
    publicPeople.records.forEach((p) => {
      const hits = byNorm[nameKey(p.name)];
      if (hits && hits.length) {
        /* Same human: the researcher row keeps its id (so old links resolve)
           and gains the evidence the people table carries. */
        hits.forEach((h) => {
          h.alsoIds = uniq(h.alsoIds.concat([p.id]));
          h.identityEvidence = p.identityEvidence;
          h.roleEvidence = p.roleEvidence;
          h.role = h.role || p.role;
          h.law = p.law;
          h.isEvidenceRecord = true;
          if (!h.institutions.length && p.institutions.length) { h.institutions = p.institutions.slice(); h.orgLabel = h.institutions.join(' · '); h.org = h.orgLabel; }
        });
        return;
      }
      rows.push(Object.assign({}, p, {
        alsoIds: [], roleCat: PERSON_CATEGORY_LABEL[U(p.category)] || p.category,
        orgLabel: p.institutions.join(' · ') || null,
        orcid: null, openalexId: null, theme: null, themeKey: null, themeLabel: null,
        worksInScope: null, lastActivity: null, daysFromRef: null,
        identityState: null, factRegion: null,
        affiliationCaveat: null,
        isResearcher: !!researcherIds[U(p.id)], researcherId: null, isEvidenceRecord: true,
        provenance: P.REAL_SOURCE,
      }));
    });
    /* The publication join, attached once, so no screen has to rebuild its own
       ORCID index and no screen can disagree with this one about who has a
       paper here. hasPublications is NOT isResearcher: measured 60 researchers,
       1 of them with a publication resolvable in this package. */
    rows.forEach((r) => {
      const pubs = publicationsForPerson(r);
      r.publications = pubs;
      r.publicationCount = pubs.length;
      r.hasPublications = pubs.length > 0;
      r.publicationJoin = r.hasPublications ? 'ORCID' : (orcidKey(r.orcid) ? 'ORCID_PRESENT_NO_WORK_IN_THIS_PACKAGE' : 'NO_ORCID');
    });
    const c = coll(rows, P.REAL_DERIVED, 'one people directory: the bibliometric index merged with the evidence-bearing public list, keyed on the diacritic-folded name', { source: 'derived · ITALY_INGEST.RESEARCHERS + .PEOPLE' });
    return Object.assign(c, {
      /* Published so a reader can see the shape of the join instead of guessing
         it from an absent panel. */
      researcherCount: rows.filter((r) => r.isResearcher).length,
      withOrcid: rows.filter((r) => orcidKey(r.orcid)).length,
      withPublications: rows.filter((r) => r.hasPublications).length,
      publicationCount: rows.reduce((n, r) => n + r.publicationCount, 0),
      distinctPublicationAuthors: Object.keys(worksByOrcid).length,
      publicationJoinNote: 'joined on ORCID, the only identifier both tables publish; the science records carry no OpenAlex author id and share no row id with the researcher index',
      publicationAbsenceNote: 'a researcher with no publication here has none IN THIS READING; the 88 ingested records name a first author only, and 7 distinct authors among them',
      categories: (() => {
        const t = tallyBy(rows, (r) => r.roleCat);
        return byCountDesc(t).map((k) => ({ key: k, label: k, count: t[k] }));
      })(),
      institutions: (() => {
        const t = tallyBy(rows, (r) => r.institutions);
        return byCountDesc(t).map((name) => ({ name, researchers: t[name] }));
      })(),
      distinctNames: uniq(rows.map((r) => nameKey(r.name))).length,
      mergedPairs: rows.filter((r) => r.alsoIds.length).length,
      affiliationCaveat: AFFILIATION_CAVEAT,
      /* The theme queries returned non-Italian affiliations too, so this list is
         "people in the monitored themes", not "Italian researchers". */
      scopeNote: 'people in the monitored themes, not a list of Italian researchers',
    });
  })();

  /* ---- SOURCES · EVENTS · NEWS ------------------------------------------ */
  /* V2.1 SOURCES.json, 189 rows: 187 sources and 2 sentinels, 31 of them
     client-safe — the same 31 the registry screen has always shown. The other
     156 are the rest of the reading, counted and never rendered.

     THE RE-KEY IS THE DANGEROUS PART. V2.1 changed the primary key from
     IT-SRC-* to SRC_<HOST>, and 23 collections still cite the old id
     (SCIENCE.SOURCE_ID is 'IT-SRC-OPENALEX' on 88/88). The package says so
     itself in ID_REKEY_NOTE and ships ID_ANTERIOR and ID_ALIASES for exactly
     this. Both are indexed below, so no existing join goes quietly to zero. */
  const sources = build('sources', [
    V21('sources', (s) => {
      const type = S(s.TYPE);
      const group = SOURCE_GROUP[U(type)] || null;
      const freq = S(s.FREQUENCY);
      return Object.assign(v21spine(s), {
        sourceId: S(s.SOURCE_ID) || S(s.ID),
        idAnterior: S(s.ID_ANTERIOR), idAliases: A(s.ID_ALIASES),
        idRekeyNote: S(s.ID_REKEY_NOTE),
        name: S(s.NAME), type,
        role: narrative(s, 'ROLE'), roleText: narText(s, 'ROLE'), roleCode: type,
        group, groupLabel: group ? SOURCE_GROUP_LABEL[group] : null,
        uiGroup: group ? SOURCE_GROUP_LABEL[group] : null,
        country: S(s.COUNTRY), geography: S(s.GEOGRAPHY), url: S(s.URL),
        frequency: freq,
        frequencyKnown: !!(freq && !FREQ_NOT_DECLARED[U(freq)]),
        latestObservation: S(s.LATEST_OBSERVATION),
        latestObservationISO: isoOf(String(S(s.LATEST_OBSERVATION) || '').slice(0, 10)),
        accessStatus: S(s.ACCESS_STATUS),
        limitations: narrative(s, 'LIMITATIONS'), limitationsText: narText(s, 'LIMITATIONS'),
        /* §18 · route metadata is COLLECTION INFRASTRUCTURE. The portal reads
           stored data and never needs the Italian route to render, so these
           are exposed as facts about the reading, never as a runtime
           dependency of the interface. */
        runtimeDependency: S(s.RUNTIME_DEPENDENCY),
        requiresItalianRoute: s.REQUIRES_ITALIAN_ROUTE === true,
        accessEvidence: narrative(s, 'ACCESS_EVIDENCE'),
        accessEvidenceMeasured: S(s.ACCESS_EVIDENCE_MEASURED),
        accessState: S(s.ACCESS_STATE),
        routeEvidenceNote: narrative(s, 'ROUTE_EVIDENCE_NOTE'),
        whatItPublishes: S(s.WHAT_IT_PUBLISHES),
        /* how many records in this reading actually cite the source, as the
           package counted it. The model recounts it below from its own
           collections; publishing both is what makes a divergence visible. */
        citedTimesDeclared: N(s.CITADO_VEZES),
        citedInDeclared: A(s.CITADO_EM),
        isSentinel: U(s.ENTITY_TYPE) === 'SOURCE_SENTINEL',
        ui: { color: SOURCE_TYPE_COLOR[U(type)] || NEUTRAL, order: null },
      });
    }, { validate: (r) => (!r.id ? 'no ID' : null) }),
    {
      source: 'ITALY_INGEST.SOURCES',
      precedence: P.REAL_SOURCE,
      rows: RAW.IG.SOURCES,
      adapt: (s) => {
        const type = S(s.TYPE);
        const group = SOURCE_GROUP[U(type)] || null;
        const freq = S(s.FREQUENCY);
        return {
          id: s.ID || s.SOURCE_ID, sourceId: s.SOURCE_ID || s.ID,
          name: S(s.NAME), type, role: narrative(s, 'ROLE'),
          /* ROLE reads like a short factual descriptor, and it was briefly
             exposed as plain text on that reasoning. Measured, it is Portuguese
             on 23 of 31 rows ("registro nacional de produto e rotulo
             autorizado"), and a short descriptor in the wrong language is still
             the wrong language in front of an Italian client. It goes through
             the same gate as every other narrative field. */
          roleText: narText(s, 'ROLE'),
          roleCode: type,
          /* IG.SOURCES has no GROUP field. The group is derived from TYPE with
             a table written out in full above, so an auditor can reconcile it
             against the 31 records instead of trusting a fuzzy match. */
          group, groupLabel: group ? SOURCE_GROUP_LABEL[group] : null,
          uiGroup: group ? SOURCE_GROUP_LABEL[group] : null,
          country: S(s.COUNTRY), geography: S(s.GEOGRAPHY), url: S(s.URL),
          frequency: freq,
          /* DATED and NO_DATE_FOUND are crawler tokens, not a cadence. The flag
             lets a view print 'non dichiarata' without sniffing strings. */
          frequencyKnown: !!(freq && !FREQ_NOT_DECLARED[U(freq)]),
          latestObservation: S(s.LATEST_OBSERVATION),
          /* Several LATEST_OBSERVATION values are raw python list literals or
             are truncated mid-string. The clean variant is null unless the
             value begins with a real date. */
          latestObservationISO: isoOf(String(S(s.LATEST_OBSERVATION) || '').slice(0, 10)),
          accessStatus: S(s.ACCESS_STATUS), limitations: narrative(s, 'LIMITATIONS'),
          limitationsText: narText(s, 'LIMITATIONS'),
          ui: { color: SOURCE_TYPE_COLOR[U(type)] || NEUTRAL, order: null },
          provenance: provOf(s, P.REAL_SOURCE), raw: s,
        };
      },
      validate: (r) => (!r.id ? 'no ID' : !r.name ? 'no name' : null),
    },
  ], 'traceable source registry; the group is derived from TYPE through a table written out in full');
  v21law(sources, 'sources');

  /* ---- EVENTS · and the double count the manifest warns about ------------
     DECISION, stated once here so no screen has to make it again:
     EVENTS.json (40 rows) IS THE COUNTABLE COLLECTION. FUTURE-EVENTS.json (14
     rows) is a CUT of it — the manifest says loading both counts the same
     event twice — so it is NOT a second collection. It is applied as a
     PROPERTY of these rows: `inFutureCut` per record, `futureCut` as an array,
     and the parsed START_DATE / END_DATE / DATE_PRECISION the cut file adds to
     the 7 client-safe rows it covers. A property cannot be summed into a
     total; a collection can, and that is the whole reason for the choice.

     The model keeps the collection NAME `futureEvents` because every screen
     already reads it, with `events` as the alias it always had. The name is
     legacy; the contents are all 40 events. */
  const V21_FUTURE_CUT = {};
  A(V21C.futureEvents).forEach((e) => { if (e && e.ID) V21_FUTURE_CUT[U(e.ID)] = e; });

  const futureEvents = build('futureEvents', [
    V21('events', (e) => {
      const cut = V21_FUTURE_CUT[U(e.ID)] || null;
      /* the cut file is the only place the dates are parsed out; where it
         does not cover a row the range is split here, never flattened */
      const [rs, re] = isoRange(e.DATE);
      const startDate = (cut && isoOf(cut.START_DATE)) || rs;
      const endDate = (cut && isoOf(cut.END_DATE)) || re;
      const part = e.CONFIRMED_PARTICIPATION && typeof e.CONFIRMED_PARTICIPATION === 'object' && !Array.isArray(e.CONFIRMED_PARTICIPATION)
        ? e.CONFIRMED_PARTICIPATION : {};
      return Object.assign(v21spine(e), {
        name: S(e.EVENT), date: S(e.DATE),
        startDate, endDate, dateEnd: endDate,
        dateState: dateStateOf(e.DATE),
        datePrecision: cut ? S(cut.DATE_PRECISION) : null,
        dateParseState: cut ? S(cut.DATE_PARSE_STATE) : null,
        location: S(e.LOCATION), sector: S(e.SECTOR),
        cropRelevance: UNK(e.CROP_RELEVANCE),
        cropRelevanceList: A(e.CROP_RELEVANCE),
        cropKeys: cropsFromV21Ids(e.CROP_IDS),
        organizer: S(e.ORGANIZER), url: S(e.OFFICIAL_URL),
        exhibitorListState: S(e.EXHIBITOR_LIST_STATE), timeState: S(e.TIME_STATE),
        /* future participation is never inferred from past participation */
        confirmedParticipation: part,
        confirmedParticipationList: Object.keys(part),
        participationLaw: narrative(e, 'PARTICIPATION_LAW'),
        participationLawText: narText(e, 'PARTICIPATION_LAW'),
        note: narrative(e, 'NOTE'),
        /* the cut, as a flag on the row it belongs to */
        inFutureCut: !!cut,
        futureCutSource: cut ? 'FUTURE-EVENTS.json' : null,
        daysFromRef: daysFrom(startDate),
        daysToStart: daysFrom(startDate),
      });
    }),
    {
      source: 'ITALY_INGEST.EVENTS',
      precedence: P.REAL_SOURCE,
      rows: RAW.IG.EVENTS,
      adapt: (e) => {
        /* DATE is either a single ISO date or 'YYYY-MM-DD a YYYY-MM-DD'. A
           single-day event gets endDate === startDate rather than null, so a
           calendar never has to special-case it. */
        const [startDate, endDate] = isoRange(e.DATE);
        const part = e.CONFIRMED_PARTICIPATION && typeof e.CONFIRMED_PARTICIPATION === 'object' && !Array.isArray(e.CONFIRMED_PARTICIPATION)
          ? e.CONFIRMED_PARTICIPATION : {};
        return {
          id: e.ID, name: S(e.EVENT), date: S(e.DATE),
          startDate, endDate, dateEnd: endDate,
          dateState: dateStateOf(e.DATE),
          location: S(e.LOCATION),
          sector: S(e.SECTOR),
          /* CROP_RELEVANCE is one token, not an array; 5 of 18 are the unknown
             sentence and resolve to null. */
          cropRelevance: UNK(e.CROP_RELEVANCE),
          cropRelevanceList: A(e.CROP_RELEVANCE),
          organizer: S(e.ORGANIZER), url: S(e.OFFICIAL_URL),
          exhibitorListState: S(e.EXHIBITOR_LIST_STATE), timeState: S(e.TIME_STATE),
          /* Future participation is never inferred from past participation.
             PARTICIPATION_LAW is the sentence that says so and it travels with
             the record so no card can render the list without it. */
          confirmedParticipation: part,
          confirmedParticipationList: Object.keys(part),
          participationLaw: narrative(e, 'PARTICIPATION_LAW'),
          participationLawText: narText(e, 'PARTICIPATION_LAW'),
          note: narrative(e, 'NOTE'),
          daysFromRef: daysFrom(startDate),
          daysToStart: daysFrom(startDate),
          provenance: provOf(e, P.REAL_SOURCE), raw: e,
        };
      },
      validate: (r) => (!r.id ? 'no ID' : !r.name ? 'no event name' : null),
    },
  ], 'real sector events; a date range is split, never flattened');
  v21law(futureEvents, 'events');
  Object.assign(futureEvents, {
    /* THE DERIVED VIEW, not a second collection: same objects, no copies, and
       nothing here is ever added to the events total. */
    futureCut: futureEvents.records.filter((e) => e.inFutureCut),
    futureCutCount: futureEvents.records.filter((e) => e.inFutureCut).length,
    futureCutSafeCount: futureEvents.safeRecords.filter((e) => e.inFutureCut).length,
    doubleCountWarning: S(V21H && V21H.DOUBLE_COUNT_WARNING),
    countableCollection: 'events',
  });

  const news = build('news', [
    V21('news', (n) => Object.assign(v21spine(n), {
      title: S(n.TITLE), publisher: S(n.PUBLISHER), outlet: S(n.PUBLISHER),
      author: S(n.AUTHOR), date: UNK(n.DATE),
      dateISO: isoOf(n.DATE), dateState: dateStateOf(n.DATE),
      crop: S(n.CROP),
      cropCanonical: cropResolve(n.CROP).key || cropsFromV21Ids(n.CROP_IDS)[0] || null,
      cropScope: cropResolve(n.CROP).scope,
      cropKeys: cropsFromV21Ids(n.CROP_IDS),
      issue: S(n.ISSUE),
      region: UNK(n.REGION),
      /* the badge that separates editorial from company-provided content is
         not optional and is never derived from the publisher's name */
      contentKind: S(n.CONTENT_KIND),
      contentKindMeaning: narrative(n, 'CONTENT_KIND_MEANING'),
      isEditorial: U(n.CONTENT_KIND) === 'EDITORIAL',
      summary: narrative(n, 'SINTONIA_SUMMARY'),
      caveat: narrative(n, 'CAVEAT'),
      url: S(n.SOURCE_URL), daysFromRef: daysFrom(isoOf(n.DATE)),
    }), { validate: (r) => (!r.id ? 'no ID' : !r.title ? 'no title' : null) }),
    {
      source: 'ITALY_INGEST.NEWS',
      precedence: P.REAL_SOURCE,
      rows: RAW.IG.NEWS,
      adapt: (n) => ({
        id: n.ID, title: S(n.TITLE), publisher: S(n.PUBLISHER), outlet: S(n.PUBLISHER),
        author: S(n.AUTHOR), date: UNK(n.DATE),
        dateISO: isoOf(n.DATE), dateState: dateStateOf(n.DATE),
        /* MEASURED: NEWS.CROP is not written in the token vocabulary this field
           used to be keyed on. The 8 items say MAIS, VITE, FRUMENTO x2, SOIA,
           ORTICOLE, CEREAIS — Italian and Portuguese. CROP_BY_TOKEN knows MAIS
           and VITE and nothing else here, so 3 of the 8 lost their canonical
           crop to the wrong table, not to missing data: FRUMENTO is Wheat and
           SOIA is Soybean in CROP_BY_IT, in this same model, one table over.
           Through the resolver they resolve. ORTICOLE and CEREAIS stay null and
           must: they are umbrella words, and cropResolve reports GENERIC_TERM
           rather than promoting them to a crop. */
        crop: S(n.CROP), cropCanonical: cropResolve(n.CROP).key,
        cropScope: cropResolve(n.CROP).scope,
        issue: S(n.ISSUE),
        /* REGION is the unknown sentence on 8/8. Null, so the region filter is
           not populated with a note. */
        region: UNK(n.REGION),
        /* Three of the eight items are company-provided and one is branded
           content. Publishing those beside editorial pieces without the badge
           would be the single most misleading thing on this screen. */
        contentKind: S(n.CONTENT_KIND),
        contentKindMeaning: narrative(n, 'CONTENT_KIND_MEANING'),
        isEditorial: U(n.CONTENT_KIND) === 'EDITORIAL',
        summary: narrative(n, 'SINTONIA_SUMMARY'),
        caveat: narrative(n, 'CAVEAT'),
        url: S(n.SOURCE_URL), daysFromRef: daysFrom(isoOf(n.DATE)),
        provenance: provOf(n, P.REAL_SOURCE), raw: n,
      }),
      validate: (r) => (!r.id ? 'no ID' : !r.title ? 'no title' : null),
    },
  ], 'real news and trade-media records; the content-kind badge is not optional');
  v21law(news, 'news');

  /* ---- SOURCE RESOLUTION · one join key for the whole model -------------
     Every record that names a source names it by ID. The only exception is
     news, which names a PUBLISHER string; that is resolved by EXACT
     case-insensitive name match and left null when it does not match.
     MEASURED: 6 of 8 news items resolve. The two that do not are 'Agronotizie'
     (a casing variant of 'AgroNotizie (Image Line)') and 'Consorzio
     Fitosanitario di Modena' (the registry says 'Provinciale'). Fuzzy-matching
     them would create a link the evidence does not support. */
  /* Every key the registry itself publishes is indexed: the V2.1 primary key,
     the SOURCE_ID the other 23 collections cite, the previous primary key and
     every declared alias. The re-key is therefore invisible to every join in
     this model — which is the point of the package shipping ID_ALIASES. */
  const sourceById = {};
  sources.records.forEach((s) => {
    [s.id, s.sourceId, s.idAnterior].concat(A(s.idAliases)).forEach((k) => {
      const key = U(k);
      if (key && !sourceById[key]) sourceById[key] = s;
    });
  });
  const sourceByName = {};
  sources.records.forEach((s) => { if (s.name) sourceByName[U(s.name)] = s; });
  const sourceNameOf = (id) => { const s = sourceById[U(id)]; return s ? s.name : null; };

  news.records.forEach((n) => {
    const s = sourceByName[U(n.publisher)] || null;
    n.publisherSourceId = s ? s.id : null;
    n.publisherSourceName = s ? s.name : null;
  });

  /* How many ingested records actually name each source. MEASURED: 4 of the 31
     registered sources are cited at all; the other 27 score zero. That zero is
     a fact about the reading, and hiding it would make the registry look like
     coverage it does not have. */
  const backedTally = tallyBy(
    [].concat(
      scienceRecords.records, marketObservations.records, publicVoices.records,
      resistance.records, scienceThemes.records, currentFieldSignals.records, researchers.records
    ),
    (r) => r.sourceId
  );
  sources.records.forEach((s) => {
    s.backedRecords = (backedTally[s.id] || 0) + (s.sourceId && s.sourceId !== s.id ? backedTally[s.sourceId] || 0 : 0);
    s.linkedRecordCount = s.backedRecords;
  });
  Object.assign(sources, {
    groups: (() => {
      const t = tallyBy(sources.records, (r) => r.group);
      return byCountDesc(t).map((k) => ({ key: k, label: SOURCE_GROUP_LABEL[k] || k, count: t[k] }));
    })(),
    accessCounts: tallyBy(sources.records, (r) => r.accessStatus),
    typeCounts: tallyBy(sources.records, (r) => r.type),
    citedCount: sources.records.filter((s) => s.backedRecords > 0).length,
  });

  /* ---- MARKET BY CROP · derived ----------------------------------------
     One row per crop key, so a screen can stop asking "what is the state of
     this market" and start asking "what did we actually observe".

     What is DELIBERATELY absent: there is no verdict, no temperature, no
     trajectory and no confidence. None of them is derivable from a price list
     with four different trade stages and twelve dead series, and inventing one
     is exactly the failure this rebuild exists to remove. hasData=false is the
     most important field on the row. */
  const marketByCrop = (() => {
    const crops = uniq(CROP_KEY.map((r) => r.crop).concat(marketObservations.records.map((m) => m.cropKey)));
    const rows = crops.map((crop) => {
      const recs = marketObservations.records.filter((m) => m.cropKey === crop);
      const current = recs.filter((m) => m.isCurrentSeries);
      const src = recs.length ? sourceById[U(recs[0].sourceId)] : null;
      return {
        id: 'MBC-' + U(crop).replace(/\s+/g, '-'),
        cropKey: crop, cropName: crop,
        marketViewKey: MARKET_VIEW_KEY[crop] || null,
        hasData: recs.length > 0,
        observationCount: recs.length,
        currentCount: current.length,
        stoppedCount: recs.filter((m) => !m.isCurrentSeries).length,
        stoppedYears: uniq(recs.map((m) => m.stoppedYear).filter(Boolean)).sort(),
        /* distinct named trading places, not a coverage claim */
        piazzaCount: uniq(recs.map((m) => m.market)).length,
        piazze: uniq(recs.map((m) => m.market)),
        /* Units are never collapsed: tonnes and €/100kg are not comparable. */
        units: uniq(recs.map((m) => m.unit)),
        stages: uniq(recs.map((m) => m.stage)),
        /* Six olive oil grades are six product definitions of one crop. */
        productDefinitions: uniq(recs.map((m) => m.product)),
        latestPeriodEnd: maxIso(current.map((m) => m.periodEnd)),
        daysSinceLatest: maxIso(current.map((m) => m.periodEnd)) ? daysFrom(maxIso(current.map((m) => m.periodEnd))) : null,
        changeCoverage: {
          vsPrev: recs.filter((m) => m.changeVsPrev !== null).length,
          vsYearAgo: recs.filter((m) => m.changeVsYearAgo !== null).length,
          total: recs.length,
        },
        sourceId: recs.length ? recs[0].sourceId : null,
        sourceName: src ? src.name : null,
        sourceUrl: src ? src.url : null,
        sourceFrequency: src ? src.frequency : null,
        provenance: P.REAL_DERIVED,
      };
    }).sort((a, b) => b.observationCount - a.observationCount || (a.cropKey < b.cropKey ? -1 : 1));
    return coll(rows, P.REAL_DERIVED, 'counts and coverage derived from ingested price observations; no market verdict, temperature or trajectory is derived, because none is derivable', { source: 'derived · marketObservations' });
  })();

  /* ---- MARKET SUMMARIES · a manifest, not the analysis ------------------
     Written market analysis exists upstream for five crops, but only the file
     manifest travels in this package — the bodies do not. Saying "the analysis
     exists and is not loaded" is the honest answer; letting a fixture stand in
     for it is not. */
  /* NO V2.1 CANDIDATE: the package carries no manifest of the written
     analyses, and their bodies still do not travel. */
  const marketSummaries = build('marketSummaries', [
    {
      source: 'ITALY_INGEST.MARKET_SUMMARIES',
      precedence: P.REAL_SOURCE,
      rows: RAW.IG.MARKET_SUMMARIES,
      adapt: (m, i) => ({
        id: 'MSUM-' + U(m.CROP).replace(/[^A-Z0-9]+/g, '-'),
        crop: S(m.CROP), file: S(m.FILE), chars: N(m.CHARS),
        loaded: false,
        note: 'analisi scritta esistente a monte, non caricata in questo pacchetto',
        provenance: P.REAL_SOURCE,
      }),
      validate: (r) => (!r.crop ? 'no crop' : null),
    },
  ], 'manifest of upstream written market analysis; the bodies are not in this package');

  /* ═══════════════════════════════════════════════════════════════════════
     THE REGULATORY FUTURE IS THREE DIFFERENT THINGS, AND THEY ARE NOT
     INTERCHANGEABLE. The package is explicit and the model keeps them apart
     in three collections rather than one:

       regulatoryFuture        the ITALIAN AUTHORISATION EXPIRY calendar —
                               EXPIRY on the 163 registry records. A date the
                               Ministero states about ONE Italian
                               authorisation.
       regulatoryFutureFacts   REGULATORY-FUTURE-FACTS.json, 47 rows, all
                               client-safe — the EUROPEAN approval expiry per
                               ACTIVE SUBSTANCE, read from EUR-Lex.
       regulatoryFutureSignals REGULATORY-FUTURE.json, 28 rows, 6 client-safe —
                               written readings of the European renewal
                               procedure. Draft, discussion and meeting are not
                               a decision.

     FOUR PERMANENT SEMANTICS, encoded as fields so a view cannot get them
     wrong by omission:
       EU APPROVAL EXPIRY  !=  NON-RENEWAL         (isNonRenewal false)
       EU APPROVAL EXPIRY  !=  COMMERCIAL RISK     (isRisk from the record)
       EU FACT             !=  ITALIAN MARKETABILITY (geographyLaw travels)
       FUTURE FACT         !=  OPPORTUNITY         (isOpportunity from the record)
     A date may be presented as a fact with its caveat. It may never become
     ACT NOW: nothing in this section derives a status, a rank or an action. */
  const regulatoryFuture = build('regulatoryFuture', [
    {
      source: 'HANDOFF_V21 · products.regulatory · EXPIRY',
      precedence: P.CANONICAL,
      rows: productsRegulatory.records.filter((p) => p.expiryISO),
      adapt: (p) => ({
        id: 'REGF-' + U(p.id || p.name),
        product: S(p.name), productKey: U(p.name),
        reg: S(p.reg), holder: S(p.holder), status: S(p.status),
        expiry: S(p.expiry), expiryISO: p.expiryISO,
        daysToExpiry: daysFrom(p.expiryISO),
        expired: daysFrom(p.expiryISO) !== null && daysFrom(p.expiryISO) < 0,
        regCat: S(p.regCat), line: S(p.line), labelUrl: S(p.labelUrl),
        clientSafe: p.clientSafe,
        /* an Italian authorisation date is not a European one and says
           nothing about the substance's EU approval */
        scope: 'ITALIAN_AUTHORISATION',
        isOpportunity: false, isRisk: false, isNonRenewal: false,
        provenance: P.CANONICAL, raw: p.raw || p,
      }),
      validate: (r) => (!r.product ? 'no product' : !r.expiryISO ? 'unparseable expiry' : null),
    },
    {
      source: 'ITALY_INGEST.PRODUCTS · expiry',
      precedence: P.REAL_SOURCE,
      rows: A(RAW.IG.PRODUCTS).filter((p) => S(p.expiry)),
      adapt: (p) => ({
        id: 'REGF-' + U(p.id || p.name),
        product: S(p.name), productKey: U(p.name),
        reg: S(p.reg), holder: S(p.holder), status: S(p.status),
        expiry: S(p.expiry), expiryISO: isoOf(p.expiry),
        daysToExpiry: daysFrom(isoOf(p.expiry)),
        expired: daysFrom(isoOf(p.expiry)) !== null && daysFrom(isoOf(p.expiry)) < 0,
        regCat: S(p.regCat), line: S(p.line), labelUrl: S(p.labelUrl),
        scope: 'ITALIAN_AUTHORISATION',
        isOpportunity: false, isRisk: false, isNonRenewal: false,
        provenance: provOf(p, P.REAL_SOURCE), raw: p,
      }),
      validate: (r) => (!r.product ? 'no product' : !r.expiryISO ? 'unparseable expiry' : null),
    },
  ], 'Italian authorisation expiry dates published by the national registry; a date the registry states, never a forecast and never an action');

  /* ---- REGULATORY FUTURE FACTS · 47 dates, all client-safe --------------- */
  const regulatoryFutureFacts = build('regulatoryFutureFacts', [
    V21('regulatoryFutureFacts', (f) => Object.assign(v21spine(f), {
      activeIngredient: S(f.ACTIVE_INGREDIENT),
      activeIngredientId: S(f.ACTIVE_INGREDIENT_ID),
      euState: S(f.EU_STATE),
      euExpirationOfApproval: isoOf(f.EU_EXPIRATION_OF_APPROVAL),
      euExpirationRaw: S(f.EU_EXPIRATION_OF_APPROVAL),
      daysToEuExpiration: daysFrom(isoOf(f.EU_EXPIRATION_OF_APPROVAL)),
      euCelex: S(f.EU_CELEX),
      /* THE FOUR SEMANTICS, from the record, never from a rule here. */
      isOpportunity: f.IS_OPPORTUNITY === true,
      isRisk: f.IS_RISK === true,
      isNonRenewal: false,
      /* NOT_A_CLAIM and GEOGRAPHY_LAW are the package's own interpretation
         rules, and the package wrote them in Portuguese with no _IT variant.
         The SAME two rules are also carried by WHAT_IT_DOES_NOT_PROVE, which
         the package DID approve in Italian and which measures CLEAR on 47/47:
         "LA SCADENZA DELL'APPROVAZIONE NON È UN MANCATO RINNOVO ... NON è
         rischio regolatorio, NON è rischio commerciale, NON è opportunità. E LO
         STATO EUROPEO NON È LA COMMERCIABILITÀ ITALIANA."
         So notProves is the field a card renders, and these two keep the
         Portuguese original for traceability under the *Raw suffix, which
         check PT3 forbids the markup from ever binding. Same law, one language,
         no chance of a Portuguese sentence reaching an Italian screen. */
      notAClaimRaw: S(f.NOT_A_CLAIM),
      geographyLawRaw: S(f.GEOGRAPHY_LAW),
      italianRegistrations: A(f.ITALIAN_REGISTRATIONS),
      italianRegistrationCount: N(f.ITALIAN_REGISTRATION_COUNT),
      commercialCatalogProducts: A(f.COMMERCIAL_CATALOG_PRODUCTS),
      verifiedLabelCrops: A(f.VERIFIED_LABEL_CROPS),
      verifiedLabelCropsState: S(f.VERIFIED_LABEL_CROPS_STATE),
      scope: 'EUROPEAN_APPROVAL',
      /* a fact may be shown with its caveat; it may never be an ACT NOW */
      mayBecomeAnAction: false,
      mayBecomeAnOpportunity: false,
    })),
  ], 'European approval expiry per active substance: a published date with its caveat, never a risk, never a non-renewal and never an opportunity');
  v21law(regulatoryFutureFacts, 'regulatoryFutureFacts');
  Object.assign(regulatoryFutureFacts, {
    opportunityCount: regulatoryFutureFacts.records.filter((f) => f.isOpportunity).length,
    riskCount: regulatoryFutureFacts.records.filter((f) => f.isRisk).length,
    factsAreNotOpportunities: '47 facts are 47 facts; none of them becomes an opportunity by being counted',
  });

  /* ---- REGULATORY FUTURE SIGNALS · 28 written readings, 6 client-safe ---- */
  const regulatoryFutureSignals = build('regulatoryFutureSignals', [
    V21('regulatoryFuture', (r) => Object.assign(v21spine(r), {
      regionKeys: regionsFromV21Ids(r.REGION_IDS),
      scope: 'EUROPEAN_PROCEDURE',
      isOpportunity: false, isRisk: false, isNonRenewal: false,
      extensionIsNotRenewal: 'PRORROGAZIONE NON È RINNOVO: draft, discussion and meeting are not a final decision',
    })),
  ], 'written readings of the European renewal procedure; an extension is not a renewal and a draft is not a decision');
  v21law(regulatoryFutureSignals, 'regulatoryFuture');

  /* ---- ACTIVE INGREDIENTS · the substance as an ENTITY ------------------
     LAW: an active substance is an ENTITY, not a text field on a product.
     Every component of a mixture is its own entity, so a mixture NEVER
     collapses into one mode of action, and an absent FRAC code means the
     substance has no FRAC listing — not that nobody looked. */
  const activeIngredients = build('activeIngredients', [
    V21('activeIngredients', (a) => Object.assign(v21spine(a), {
      name: S(a.NAME), normalizedName: S(a.NORMALIZED_NAME),
      italianRegistrationCount: N(a.ITALIAN_REGISTRATION_COUNT),
      hrac: A(a.HRAC), hracWssa: A(a.HRAC_WSSA), chemicalFamily: S(a.CHEMICAL_FAMILY),
      irac: A(a.IRAC), iracSubgroup: A(a.IRAC_SUBGROUP),
      frac: A(a.FRAC), fracSourceVersion: S(a.FRAC_SOURCE_VERSION),
      fracDocumentSha256: S(a.FRAC_DOCUMENT_SHA256),
      moaState: S(a.MOA_STATE),
      euState: S(a.EU_STATE),
      euDateOfApproval: isoOf(a.EU_DATE_OF_APPROVAL),
      euExpirationOfApproval: isoOf(a.EU_EXPIRATION_OF_APPROVAL),
      euRenewalState: S(a.EU_RENEWAL_STATE),
      euCelex: S(a.EU_CELEX),
      cas: S(a.CAS), cipac: S(a.CIPAC),
      isOpportunity: false, isRisk: false, isNonRenewal: false,
    })),
  ], 'active substances as entities; a mixture never becomes one mode of action and an absent FRAC code is an absent listing');
  v21law(activeIngredients, 'activeIngredients');

  /* ---- PRODUCT x ACTIVE INGREDIENT · one row per COMPONENT --------------
     LAW: a product with two actives makes two rows. Summing rows does not
     count products, so the distinct product count is published beside the
     row count rather than left to be derived by whoever reads it. */
  const productActiveIngredients = build('productActiveIngredients', [
    V21('products.activeIngredients', (r) => Object.assign(v21spine(r), {
      productId: S(r.PRODUCT_ID), product: S(r.PRODUCT_NAME), productKey: U(r.PRODUCT_NAME),
      reg: S(r.REGISTRATION_NUMBER),
      activeIngredientId: S(r.ACTIVE_INGREDIENT_ID),
      activeIngredient: S(r.ACTIVE_INGREDIENT),
      isMixtureComponent: r.IS_MIXTURE_COMPONENT === true,
      componentsInProduct: N(r.COMPONENTS_IN_PRODUCT),
      commercialCatalogProducts: A(r.COMMERCIAL_CATALOG_PRODUCTS),
    })),
  ], 'one row per product component; rows are components, never products');
  v21law(productActiveIngredients, 'products.activeIngredients');
  Object.assign(productActiveIngredients, {
    distinctProducts: uniq(productActiveIngredients.safeRecords.map((r) => r.productKey)).length,
    distinctIngredients: uniq(productActiveIngredients.safeRecords.map((r) => r.activeIngredientId)).length,
    rowsAreNotProducts: 'summing these rows counts components, not products',
  });

  /* ---- FUTURE ----------------------------------------------------------- */
  /* 2 of the 3 rows are CLIENT_SAFE=false and therefore travel as identity
     only. They are the SAME records ITALY_INGEST carries (IT-FUT-001..003,
     ORIGIN_LAYER PREVIOUS_HANDOFF), so the previous handoff fills what the
     transport did not carry and V2.1 still wins every key it does carry. */
  const futureSignals = build('futureSignals', [
    V21('futureSignals', (f) => Object.assign(v21spine(f), {
      id: S(f.ID) || S(f.SIGNAL_ID),
      legacyId: S(f.LEGACY_ID),
      crop: cropResolve(f.CROP).label, cropRaw: S(f.CROP), cropKey: cropResolve(f.CROP).key,
      cropKeys: cropResolve(f.CROP).keys, cropScope: cropResolve(f.CROP).scope,
      issue: issueResolve(f.ISSUE).it, issueEn: issueResolve(f.ISSUE).en, issueRaw: S(f.ISSUE),
      /* REGION is still the analyst's unknown sentence on 2 of 3 */
      region: UNK(f.REGION), regionScope: regionResolve(f.REGION).scope,
      regionKeys: REGION_NAMES.filter((n) => fold(String(UNK(f.REGION) || '')).toLowerCase().indexOf(fold(n).toLowerCase()) >= 0),
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
      evidenceIds: A(f.EVIDENCE_RECORD_IDS),
    }), { enrichFrom: RAW.IG.FUTURE_SIGNALS }),
    {
      source: 'ITALY_INGEST.FUTURE_SIGNALS',
      precedence: P.REAL_SOURCE,
      rows: RAW.IG.FUTURE_SIGNALS,
      adapt: (f) => ({
        id: f.ID || f.SIGNAL_ID, legacyId: S(f.LEGACY_ID),
        /* CROP arrives Portuguese ('MAIS', 'TRIGO e TRIGO DURO'). Resolve it; the
           published token stays as cropRaw so nothing becomes untraceable. */
        crop: (cropResolve(f.CROP).label), cropRaw: S(f.CROP), cropKey: cropResolve(f.CROP).key,
        cropKeys: cropResolve(f.CROP).keys, cropScope: cropResolve(f.CROP).scope,
        issue: issueResolve(f.ISSUE).it, issueEn: issueResolve(f.ISSUE).en, issueRaw: S(f.ISSUE),
        region: regionResolve(f.REGION).label, regionRaw: S(f.REGION), regionScope: regionResolve(f.REGION).scope,
        /* 2 of the 3 REGION values are the analyst's unknown sentence; leaking
           them would put a Portuguese explanation into a region filter. */
        region: UNK(f.REGION),
        regionKeys: REGION_NAMES.filter((n) => fold(String(UNK(f.REGION) || '')).toLowerCase().indexOf(fold(n).toLowerCase()) >= 0),
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
  v21law(futureSignals, 'futureSignals');

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

  /* ═══════════════════════════════════════════════════════════════════════
     THESE ARE NOT OPPORTUNITIES, AND THE PACKAGE FORBIDS CALLING THEM THAT.
     Measured on all three records, and none of it is a judgement made here:
         ENTITY_TYPE      OPPORTUNITY_CANDIDATE
         QA_STATUS        EVIDENCE_DERIVED
         CLIENT_SAFE      false          → collections.opportunities.clientSafe = 0
         CASE_LABEL       «CONVERGENCIA QUE MERECE INVESTIGACAO»
         FORBIDDEN_LABEL  the record telling the interface what it may NOT say
     Nothing rounds that zero up. A regulatory future fact never becomes one of
     these either: 47 facts are 47 facts, and they live in their own collection
     with isOpportunity false on every row.

     All three are CLIENT_SAFE=false, so V2.1 transported identity and QA state
     only — CASE_LABEL, FORBIDDEN_LABEL and the method statement are not in the
     browser copy of the package. They are the SAME records the previous
     handoff carries (identical ids, and V2.1's own ORIGIN_LAYER says
     PREVIOUS_HANDOFF), so the previous handoff fills exactly what the
     transport left out and V2.1 wins every key it does carry. Without that
     merge the radar would show three empty shells and the mandatory label
     would disappear — which would be worse than the leak the transport
     prevents, because the label is the thing that stops the word
     "opportunity" being used. */
  const adaptOpportunity = (o) => {
        const w = windowByLegacyCase[U(o.LEGACY_CASE_ID)] || null;
        const wih = o.WHAT_IS_HAPPENING && typeof o.WHAT_IS_HAPPENING === 'object' ? o.WHAT_IS_HAPPENING : {};
        const wim = o.WHY_IT_MATTERS && typeof o.WHY_IT_MATTERS === 'object' ? o.WHY_IT_MATTERS : {};
        const sci = o.SCIENCE_CONTEXT && typeof o.SCIENCE_CONTEXT === 'object' ? o.SCIENCE_CONTEXT : {};
        const win = o.WINDOW && typeof o.WINDOW === 'object' ? o.WINDOW : {};
        /* The upstream writes crops in the analyst's language. OPP_CROP is a
           declared synonym table, and opportunity 003 is deliberately absent
           from it: its CROP is 'Portfólio ADAMA Italia (transversal, não é uma
           cultura)', which is not a crop and must resolve to an empty list. */
        /* The RESOLVER first, the declared table only as a fallback. OPP_CROP is
           keyed on the Portuguese the source happens to publish today
           ('VIDEIRA'); cropResolve knows that word AND 'Vite', 'Grapevine' and
           'Vitis vinifera', so a record translated into any of the four
           vocabularies still lands on the same canonical crop. Measured
           identical to the old table on all three records today. */
        const cropR = cropResolve(o.CROP);
        const cropKeys = cropR.keys.length ? cropR.keys.slice() : (OPP_CROP[oppKey(o.CROP)] || []);
        /* REGION is free text with Portuguese annotation. Extract the region
           names, keep the published sentence as regionRaw. */
        const regionR = regionResolve(o.REGION);
        const regionText = regionR.label;
        return {
          id: o.ID, legacyCaseId: S(o.LEGACY_CASE_ID),
          title: S(o.TITLE),
          /* CROP arrives Portuguese ("Videira", "Milho grão", and for the
             portfolio-wide case a whole sentence saying it is not a crop at
             all). Resolve it for display; keep the published token as cropRaw. */
          crop: cropResolve(o.CROP).label, cropRaw: S(o.CROP),
          cropScope: cropResolve(o.CROP).scope,
          region: regionText,
          cropKeys,
          /* Regions parsed out of a compound free-text string against the 20
             canonical names; the qualifiers ('principal', 'sinal', 'escala')
             stay in region and are never turned into a fact. */
          regionKeys: REGION_NAMES.filter((n) => fold(String(regionText || '')).toLowerCase().indexOf(fold(n).toLowerCase()) >= 0),
          issue: issueResolve(o.ISSUE).it, issueEn: issueResolve(o.ISSUE).en, issueRaw: S(o.ISSUE),
          regionRaw: regionR.raw, regionNames: regionR.names, regionScope: regionR.scope,
          /* ISSUE_TYPE is the analyst's unknown sentence on one of the three
             records; it must render as not-known, never as a category. */
          issueType: UNK(o.ISSUE_TYPE),
          caseLabel: S(o.CASE_LABEL),
          /* FORBIDDEN_LABEL is the record telling the interface what it is NOT
             allowed to call this. It is rendered, not filtered out. */
          forbiddenLabel: S(o.FORBIDDEN_LABEL),
          whatIsHappening: narrative(o, 'WHAT_IS_HAPPENING'),
          /* WHAT_IS_HAPPENING is a structured object upstream, not prose: its
             document name, dates and freshness are facts and are exposed as
             such. Only CONTENT is analyst prose. */
          happeningState: S(wih.STATE),
          happeningDocument: S(wih.DOCUMENT),
          happeningContent: S(wih.CONTENT),
          observationDate: isoOf(wih.OBSERVATION_DATE),
          happeningPublicationDate: isoOf(wih.PUBLICATION_DATE),
          /* freshnessDays is upstream's own number. It is NOT recomputed here:
             recomputing it would be a second clock disagreeing with the source. */
          freshnessDays: N(wih.FRESHNESS_DAYS),
          observedStage: S(wih.OBSERVED_STAGE),
          happeningSourceId: S(wih.SOURCE_ID),
          happeningSourceResolves: !!sourceById[U(wih.SOURCE_ID)],
          whyItMatters: narrative(o, 'WHY_IT_MATTERS'),
          whyMandatory: typeof wim.MANDATORY === 'boolean' ? wim.MANDATORY : null,
          whyNote: S(wim.NOTE),
          whyRegional: Object.keys(wim).filter((k) => k !== 'MANDATORY' && k !== 'NOTE').map((k) => ({ key: k, text: S(wim[k]) })),
          currentEvidence: narrative(o, 'CURRENT_EVIDENCE'),
          currentEvidenceList: A(o.CURRENT_EVIDENCE),
          marketContext: narrative(o, 'MARKET_CONTEXT'),
          competitorContext: narrative(o, 'COMPETITOR_CONTEXT'),
          scienceContext: narrative(o, 'SCIENCE_CONTEXT'),
          /* SCIENCE_CONTEXT has different keys on every record, so it stays a
             label/value list instead of being forced into fixed fields. */
          scienceContextState: S(sci.STATE),
          scienceContextCounts: Object.keys(sci).filter((k) => k !== 'STATE' && k !== 'SOURCE_ID').map((k) => ({ label: k, value: sci[k] })),
          fieldVoices: narrative(o, 'FIELD_VOICES'),
          /* WHAT_WE_KNOW, WHAT_WE_DO_NOT_KNOW and INTERPRETATIONS are
             Portuguese ARRAYS with no localized variant anywhere in the
             package. They go through the same gate as any other prose: the
             narrative field reports NOT_APPROVED_FOR_DISPLAY, and the list
             keeps its LENGTH — which is a real fact, "there are three things
             we do not know" — while every item is replaced by its knowledge
             state. The count survives; the untranslated sentence cannot reach
             a screen even if a view binds the array by accident. */
          whatWeKnow: narrative(o, 'WHAT_WE_KNOW'),
          whatWeKnowCount: A(o.WHAT_WE_KNOW).length,
          whatWeKnowList: A(o.WHAT_WE_KNOW).map(() => KNOWLEDGE.NOT_APPROVED_FOR_DISPLAY),
          whatWeDoNotKnow: narrative(o, 'WHAT_WE_DO_NOT_KNOW'),
          whatWeDoNotKnowCount: A(o.WHAT_WE_DO_NOT_KNOW).length,
          whatWeDoNotKnowList: A(o.WHAT_WE_DO_NOT_KNOW).map(() => KNOWLEDGE.NOT_APPROVED_FOR_DISPLAY),
          interpretations: narrative(o, 'INTERPRETATIONS'),
          interpretationsCount: A(o.INTERPRETATIONS).length,
          interpretationsList: A(o.INTERPRETATIONS).map(() => KNOWLEDGE.NOT_APPROVED_FOR_DISPLAY),
          adamaProducts: A(o.ADAMA_PRODUCTS),
          adamaActiveSubstance: A(o.ADAMA_ACTIVE_SUBSTANCE),
          /* WINDOW is an object {APPLICATION, MONITORING, NEXT_CYCLE}, already
             split into the three fields below. Stringifying it produced the
             literal "[object Object]" on every screen that showed a field
             case — kept as null so nothing renders rather than nonsense. */
          windowText: null,
          windowApplication: S(win.APPLICATION),
          windowMonitoring: S(win.MONITORING),
          windowNextCycle: S(win.NEXT_CYCLE),
          /* The canonical window is a RELATION, not a promotion: it does not
             make anything else about the opportunity canonical. §7 forbids
             inventing an agronomic state, so status comes from the joined
             canonical window or stays null. */
          canonicalWindow: w, windowId: w ? w.windowId : null,
          status: w ? w.status : null,
          sourceIds: A(o.SOURCE_IDS),
          sourceIdsResolve: A(o.SOURCE_IDS).every((s) => !!sourceById[U(s)]),
          ui: categoryOf(UNK(o.ISSUE_TYPE)),
          provenance: provOf(o, P.REAL_SOURCE), raw: o,
          /* THE MANDATORY LABEL AND WHAT IT FORBIDS, restated as state so a
             view cannot render the card without them. */
          isCandidate: true,
          candidateState: 'DA_VALIDARE',
          mayBeCalledAnOpportunity: false,
          forbiddenLabelReason: 'the record itself names what this may not be called',
        };
  };

  /* An opportunity candidate does NOT have to name a crop. IT-OPP-003 is the
     authorisation-expiry case, which the source itself describes as
     "transversal, não é uma cultura" — portfolio-wide. Requiring a crop
     silently rejected a real record and the radar showed 2 where upstream
     supplied 3. Only the identity is mandatory. */
  const opportunities = build('opportunities', [
    V21('opportunities', (o) => Object.assign(v21spine(o), adaptOpportunity(o), {
      /* the V2.1 spine wins on identity and QA state, which is what makes the
         gate readable: entityType OPPORTUNITY_CANDIDATE, clientSafe false */
      entityType: S(o.ENTITY_TYPE), qaStatus: S(o.QA_STATUS), clientSafe: CS(o),
      payloadState: CS(o) ? 'FULL' : 'IDENTITY_ONLY',
      /* the payload below did not travel in the V2.1 copy and is filled from
         the same record in the previous handoff — declared, not inferred */
      payloadFilledFrom: CS(o) ? null : 'ITALY_INGEST.OPPORTUNITIES · same ID',
      provenance: v21prov(o),
    }), { enrichFrom: RAW.IG.OPPORTUNITIES }),
    {
      source: 'ITALY_INGEST.OPPORTUNITIES',
      precedence: P.REAL_SOURCE,
      rows: RAW.IG.OPPORTUNITIES,
      adapt: adaptOpportunity,
      validate: (r) => (!r.id ? 'no ID' : null),
    },
  ], 'convergences that merit investigation — CANDIDATES, never opportunities; client-safe is 0 by the package’s own rule and nothing rounds it up');
  v21law(opportunities, 'opportunities');
  Object.assign(opportunities, {
    /* published so a transparency panel can state the rule rather than infer
       it from an absence */
    candidateLabel: uniq(opportunities.records.map((o) => o.caseLabel))[0] || null,
    forbiddenLabel: uniq(opportunities.records.map((o) => o.forbiddenLabel))[0] || null,
    mayBeCalledOpportunities: false,
    clientSafeIsZeroByRule: opportunities.clientSafe === 0,
  });

  /* The product links an opportunity asserts, graded by the label audit rather
     than believed. MEASURED: with the raw Portuguese crop and issue all six
     products on opportunity 001 return LABEL_CHECK_NEEDED; through the declared
     crop map they return 2 VERIFIED (EVURE PRO, MAVRIK SMART) and 4 still
     needing a label check. Neither number is invented — the second is simply
     the audit being asked the question in the vocabulary it was written in. */
  opportunities.records.forEach((o) => {
    const cropEN = o.cropKeys[0] || null;
    /* Every wording the resolver can produce is tried, in the order the record
       carries them: resolved Italian, resolved English, published source text.
       OPP_ISSUE is keyed on all three by construction, so this cannot miss
       because a record was translated. */
    const issueEN = [o.issue, o.issueEn, o.issueRaw]
      .map((w) => (w ? OPP_ISSUE[oppKey(w)] : null)).filter(Boolean)[0] || null;
    o.issueKey = issueEN;
    o.productLinks = o.adamaProducts.map((name) => {
      const strength = cropEN && issueEN ? labelVerdicts.verdictFor(cropEN, issueEN, name) : 'LABEL_CHECK_NEEDED';
      return {
        name, product: name, strength,
        strengthRank: STRENGTH[strength].rank,
        /* Names the route the question actually took, so a reader can re-run
           it. The crop now comes from cropResolve and the issue from the
           resolver-generated OPP_ISSUE keys; saying 'OPP_CROP' here would send
           an auditor to a table that is only the fallback. */
        resolvedThrough: cropEN && issueEN ? 'cropResolve:' + cropEN + '/OPP_ISSUE:' + issueEN : 'QUESTION_NOT_RESOLVED',
        inRegistry: !!productByKey[U(name)],
        absenceRule: ABSENCE_RULE_TEXT,
      };
    });
    o.verifiedProductCount = o.productLinks.filter((l) => l.strength === 'VERIFIED_LABEL_MATCH').length;
  });

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

  /* ---- AGROMET ----------------------------------------------------------
     Was empty; V2.1 supplies 44 rows, 14 client-safe. LAW: CLIMATE IS A
     CONDITION. It is not the presence of a disease, not pest incidence and not
     a loss, and any climate x crop x disease crossing is Sintonia's own
     interpretation, never the source's. The caveat travels per row. */
  const agrometConditions = build('agrometConditions', [
    V21('agromet', (a) => Object.assign(v21spine(a), {
      regionKeys: regionsFromV21Ids(a.REGION_IDS),
      cropKeys: cropsFromV21Ids(a.CROP_IDS),
      conditionIsNotIncidence: true,
      crossingWouldBeInterpretation: true,
    })),
  ], 'agrometeorological conditions; a condition is never an incidence, a presence or a loss');
  v21law(agrometConditions, 'agromet');

  /* ---- CLIENT-SAFE CROSSINGS -------------------------------------------
     19 rows, 0 client-safe, and the package is emphatic about why: a crossing
     is the observation that two layers speak about the same CROP_ID, and
     A CROSSING IS NOT AN OPPORTUNITY — a person decides whether it is worth
     anything. All 19 travel as identity only, so the model can count them and
     has nothing to render; RENDERABLE_WITH_METHOD, the supporting id lists and
     the method statement did not cross the transport. That is stated here
     rather than filled in from somewhere else. */
  const clientSafeCrossings = build('clientSafeCrossings', [
    V21('crossings', (c) => Object.assign(v21spine(c), {
      crossingType: S(c.CROSSING_TYPE),
      cropId: S(c.CROP_ID),
      cropKeys: cropsFromV21Ids([c.CROP_ID]),
      /* THE RELATION CARRIES IDS ONLY. Copying the crossed objects in would
         create two owners of one fact, so the supporting records are named and
         never embedded. */
      supportingIds: (c.SUPPORTING_IDS && typeof c.SUPPORTING_IDS === 'object') ? c.SUPPORTING_IDS : null,
      supportingQa: A(c.SUPPORTING_QA),
      allSupportClientSafe: c.ALL_SUPPORT_CLIENT_SAFE === true,
      distinctSourceDocuments: N(c.DISTINCT_SOURCE_DOCUMENTS),
      /* the geography law of a crossing: the crossing claims no geography,
         and provincial supports never stand for their region */
      geographicClaim: S(c.GEOGRAPHIC_CLAIM),
      geographicClaimScope: S(c.GEOGRAPHIC_CLAIM_SCOPE),
      geographicClaimLaw: S(c.GEOGRAPHIC_CLAIM_LAW),
      coverageProvinces: A(c.GEOGRAPHIC_COVERAGE_PROVINCES),
      coverageRegions: A(c.GEOGRAPHIC_COVERAGE_REGIONS),
      supportsThatDoNotRepresentRegion: A(c.SUPPORTS_THAT_DO_NOT_REPRESENT_REGION),
      /* the three lead lists, each with the law that keeps it a lead */
      labelLinkStrengths: (c.LABEL_LINK_STRENGTHS && typeof c.LABEL_LINK_STRENGTHS === 'object') ? c.LABEL_LINK_STRENGTHS : null,
      economicWeightLeads: A(c.ECONOMIC_WEIGHT_LEADS),
      economicWeightLeadsLaw: narrative(c, 'ECONOMIC_WEIGHT_LEADS_LAW'),
      researchLeads: A(c.RESEARCH_LEADS),
      researchLeadsLaw: S(c.RESEARCH_LEADS_LAW),
      invariantsProven: A(c.INVARIANTS_PROVEN),
      invariantsNotApplicable: A(c.INVARIANTS_NOT_APPLICABLE),
      /* the record's own rendering rule: it may appear on screen, but only
         with what it does not prove beside it — never behind a "read more" */
      renderableWithMethod: c.RENDERABLE_WITH_METHOD === true,
      renderRule: S(c.RENDER_RULE),
      whyNotClientSafe: S(c.WHY_NOT_CLIENT_SAFE),
      letsYouAsk: narrative(c, 'WHAT_IT_LETS_YOU_ASK'),
      isOpportunity: false,
      crossingIsNotOpportunity: 'two layers speaking about the same crop is an observation; whether it is worth anything is a person’s decision',
    })),
  ], 'crossings between layers over the same crop; never an opportunity, and none of the 19 is client-safe');
  v21law(clientSafeCrossings, 'crossings');

  /* ---- RELATIONSHIPS · the generic graph -------------------------------
     A crossing exists only when a normalized relationship supports it. Sharing
     a crop name is not a relationship, so nothing is generated here from a
     name match. */
  /* V2.1 RELATIONSHIPS.json is the same 19 crossing ids under a second file
     name, and it is subject to the same law: THE RELATIONS CARRY IDS ONLY.
     Copying the object into the relation would create two owners of one fact,
     so nothing is embedded here. All 19 are CLIENT_SAFE=false, so the LINKS
     map did not travel and the edge lists are empty — counted, not invented. */
  const relationships = build('relationships', [
    V21('relationships', (r) => Object.assign(v21spine(r), {
      crossingType: S(r.CROSSING_TYPE),
      cropId: S(r.CROP_ID),
      from: S(r.ID), fromKind: 'crossing',
      to: S(r.CROP_ID), toKind: 'crop',
      kind: S(r.CROSSING_TYPE) || 'CROSSING',
      evidence: 'declared V2.1 crossing',
      links: r.LINKS && typeof r.LINKS === 'object' ? r.LINKS : null,
      linksState: r.LINKS ? 'DECLARED' : 'NOT_DECLARED',
      linkedIds: r.LINKS && typeof r.LINKS === 'object'
        ? uniq(Object.keys(r.LINKS).flatMap((k) => A(r.LINKS[k]))) : [],
      renderableWithMethod: r.RENDERABLE_WITH_METHOD === true,
      idsOnly: true,
    })),
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
  v21law(relationships, 'relationships');

  /* ---- ARCHIVE · an index over the normalized model --------------------- */
  /* Three rules this index has to obey and did not before.

     1 · SOURCE IS A JOIN KEY, NOT A LABEL. The old `source` column mixed four
         vocabularies — institution names, registry codes, platform names and
         event venues — so no filter and no source cross-link could work against
         it. sourceId is now derived only from a real per-record source field
         (or from the platform, for the two platforms that ARE registered
         sources) and is null where nothing resolves. sourceName is the
         registry's name for that id.
     2 · A CROP COLUMN MUST CONTAIN CROPS. The market rows used to publish the
         price-series code as a crop, injecting twelve non-crop values into the
         crop filter. The code now lives in `series`, and crop is null.
     3 · THE CROP VOCABULARIES ARE NOT ONE VOCABULARY. cropVocab says which of
         the four a value belongs to, so the filter cannot present canonical
         English, screaming-snake tokens, Latin binomials and the advertiser's
         umbrella Italian words as one list of crop keys. Mapping them onto each
         other is upstream normalization work, not a view fix. */
  const arch = [];
  const push = (kind, id, title, rawDate, url, crop, cropVocab, issue, prov, extra) => {
    if (!id) return;
    const iso = isoOf(rawDate);
    const sid = (extra && extra.sourceId) || null;
    arch.push(Object.assign({
      id: kind + ':' + id, recordKey: kind + ':' + id, recordId: id,
      kind, type: kind,
      title: S(title),
      /* the raw upstream string stays for display; dateISO is the parsed value */
      date: S(rawDate), dateISO: iso, dateState: dateStateOf(rawDate),
      daysFromRef: daysFrom(iso),
      url: S(url), crop: S(crop), cropVocab: crop ? cropVocab : null, issue: S(issue),
      sourceId: sid, sourceName: sid ? sourceNameOf(sid) : null,
      /* Explicit relation keys, so the drawer link list and the company/case
         filters stop needing an object graph. Null on every kind that has no
         such relation — no other collection carries a case link. */
      company: null, legacyCaseId: null, competitorProducts: [], series: null, location: null,
      ui: ARCHIVE_UI[kind] || ARCHIVE_UI.DEFAULT,
      /* The ROW is derived — it is an index entry, not an observation. The
         provenance of the record it points at is kept beside it, so a reader
         can still see whether the underlying evidence is canonical or ingested
         without the index inflating the real count. */
      provenance: P.REAL_DERIVED,
      sourceProvenance: prov,
    }, extra || {}));
  };
  scienceRecords.records.forEach((r) => push('SCIENCE', r.id, r.title, r.publishedAt, r.url, r.crop, 'UPPER_CODE', r.issue, r.provenance,
    { sourceId: r.sourceId, institution: r.institution, venue: r.venue }));
  marketObservations.records.forEach((m) => push('MARKET', m.id, [m.product, m.market].filter(Boolean).join(' · '), m.publicationDate, null, null, null, null, m.provenance,
    { sourceId: m.sourceId, series: m.product, market: m.market, cropKey: m.cropKey }));
  competitorActivities.records.forEach((a) => push('COMPETITOR', a.id, [a.displayName, a.type].filter(Boolean).join(' · '), a.startDate, a.url, a.crops[0], CROP_BY_LATIN[U(a.crops[0])] ? 'LATIN' : GENERIC_CROP_TERMS[U(a.crops[0])] ? 'GENERIC_IT' : 'UNMAPPED', a.issues[0], a.provenance,
    { sourceId: ARCHIVE_PLATFORM_SOURCE[U(a.platform)] || null, company: a.company, competitorProducts: a.products, platform: a.platform }));
  publicVoices.records.forEach((v) => push('VOICE', v.id, v.title || v.person, v.date, v.sourceUrl, v.crop, 'UPPER_CODE', v.issue, v.provenance,
    { sourceId: v.sourceId, platform: v.platform }));
  futureEvents.records.forEach((e) => push('EVENT', e.id, e.name, e.date, e.url, null, null, null, e.provenance,
    { sourceId: null, location: e.location, organizer: e.organizer }));
  news.records.forEach((n) => push('NEWS', n.id, n.title, n.date, n.url, n.crop, 'UPPER_CODE', n.issue, n.provenance,
    { sourceId: n.publisherSourceId, publisher: n.publisher }));
  cropWindows.records.forEach((w) => push('WINDOW', w.windowId, [w.issue, w.region].filter(Boolean).join(' · '), w.startDate, null, w.crop, 'CANONICAL', w.issue, w.provenance,
    { sourceId: A(w.sourceIds)[0] || null, legacyCaseId: w.legacyCaseId, region: w.region }));
  resistance.records.forEach((r) => push('RESISTANCE', r.id, r.species, r.firstCaseYear, r.url, r.crop, 'UPPER_CODE', null, r.provenance,
    { sourceId: r.sourceId, authority: r.authority }));

  const archive = coll(arch, P.REAL_DERIVED, 'index over the normalized model; no manufactured rows, and every id is a real record id', { source: 'derived' });
  Object.assign(archive, {
    /* This layer re-indexes records already counted elsewhere. Saying so is
       what stops the provenance panel double-counting the whole package. */
    isIndex: true,
    kinds: tallyBy(arch, (r) => r.kind),
    sourceResolved: arch.filter((r) => r.sourceId).length,
    dateResolved: arch.filter((r) => r.dateISO).length,
    cropResolved: arch.filter((r) => r.crop).length,
    duplicateIds: (() => { const seen = {}; const dup = []; arch.forEach((r) => { if (seen[r.id]) dup.push(r.id); seen[r.id] = 1; }); return dup; })(),
  });

  /* ---- FIELD SALES · optional integration demonstration ----------------
     Outside the external-intelligence core. These records never mutate a core
     object and never contribute to a real count. */
  const fieldMessages = coll(
    A(RAW.DEMO.FIELD_MESSAGES).map((m) => Object.assign({}, m, { provenance: P.SYNTHETIC_DEMO })),
    P.SYNTHETIC_DEMO,
    'optional integration demonstration; never affects core intelligence',
    { source: 'ITALY_DEMO.FIELD_MESSAGES' }
  );

  /* ---- WINDOW PROJECTIONS ----------------------------------------------
     The tallies live on the collection so the four radar status cards, the nav
     counter and the sidebar all read the SAME array. Each screen recomputing
     its own tally off a different source is precisely how eleven cross-screen
     conflicts happened. Nothing here is computed or inferred: these are counts
     of upstream's own CURRENT_STATUS, DATE_STATE and REGION. */
  Object.assign(cropWindows, {
    statusCounts: tallyBy(cropWindows.records, (w) => w.status),
    dateStateCounts: tallyBy(cropWindows.records, (w) => w.dateState),
    regionCounts: tallyBy(cropWindows.records, (w) => w.region),
    cropCounts: tallyBy(cropWindows.records, (w) => w.crop),
    issueTypeCounts: tallyBy(cropWindows.records, (w) => w.issueType),
    withDatesCount: cropWindows.records.filter((w) => w.hasDates).length,
    withVerifiedProductCount: cropWindows.records.filter((w) => w.verifiedProducts.length).length,
    coverageCounts: tallyBy(cropWindows.records, (w) => w.coverageState),
  });

  /* The calendar's row universe. Deliberately a thin re-shape of the canonical
     windows and NOT a second fact store: the moment the calendar owns its own
     rows, it becomes a second source of timing truth.

     What is NOT here: area / hectares. There is no hectare field anywhere in
     the package, so the '~350k ha' figures and the HIGH/MEDIUM scale label they
     drove are removed, not re-derived. */
  const windowCalendarRows = coll(
    cropWindows.records.map((w) => ({
      id: w.windowId, windowId: w.windowId, legacyCaseId: w.legacyCaseId,
      crop: w.crop, region: w.region, issue: w.issue, issueType: w.issueType,
      startDate: w.startDate, endDate: w.endDate, hasDates: w.hasDates,
      windowLabel: w.hasDates ? w.startDate + ' → ' + w.endDate : null,
      status: w.status, canonicalStatus: w.canonicalStatus, statusReason: w.statusReason,
      open: w.open,
      dateState: w.dateState, dateConfidence: w.dateConfidence,
      daysToStart: w.daysToStart, daysToEnd: w.daysToEnd,
      verifiedProducts: w.verifiedProducts, labelVerdictState: w.labelVerdictState,
      absenceRule: w.absenceRule,
      regulatory: w.regulatory, observedStage: w.observedStage,
      coverageState: w.coverageState,
      area: null, areaState: P.NOT_OBSERVABLE,
      ui: w.ui, provenance: P.REAL_DERIVED,
    })),
    P.REAL_DERIVED,
    'one calendar row per canonical window; no hectare figure exists upstream and none is derived',
    { source: 'derived · cropWindows' }
  );

  /* The only defensible per-region number in the product. It is labelled
     "canonical windows" and never "cases" or "opportunities": the legacy fixture
     published exactly these counts under the word "cases", which is how a
     window count came to be read as a pipeline. */
  const windowsByRegion = (() => {
    const t = tallyBy(cropWindows.records, (w) => w.region);
    const rows = REGION_GRID.map((g) => ({
      id: 'WBR-' + U(g.name).replace(/[^A-Z]+/g, '-'),
      region: g.name, name: g.name, short: g.short,
      windows: t[g.name] || 0,
      hasWindows: !!t[g.name],
      ui: { gc: g.gc, gr: g.gr, col: g.col, row: g.row },
      provenance: P.REAL_DERIVED,
    }));
    const c = coll(rows, P.REAL_DERIVED, 'canonical windows per region — NOT cases and NOT opportunities', { source: 'derived · cropWindows' });
    return Object.assign(c, { regionsWithWindows: rows.filter((r) => r.hasWindows).length, totalWindows: cropWindows.count, label: 'finestre canoniche' });
  })();

  /* ---- COMPETITOR x WINDOW ---------------------------------------------
     The window side is canonical and verbatim; the ADAMA side is the label
     audit. The competitor side is the WHOLE corpus for that crop, because there
     is no honest 30-day slice — measured 11 dated records in 30 days across all
     crops. The link is called a correlated crop window and nothing else: not an
     opportunity, not a threat, not a strategy. */
  const competitorWindowMoments = coll(
    cropWindows.records.map((w) => {
      const acts = competitorActivities.records.filter((a) => a.cropsCanonical.indexOf(w.crop) >= 0);
      return {
        id: 'CWM-' + w.windowId, windowId: w.windowId,
        crop: w.crop, issue: w.issue, region: w.region, issueType: w.issueType,
        status: w.status, daysToStart: w.daysToStart, hasDates: w.hasDates,
        itemsObserved: acts.length,
        companiesObserved: uniq(acts.map((a) => a.company)).length,
        companies: uniq(acts.map((a) => a.company)),
        activityIds: acts.map((a) => a.id),
        portfolioVerified: w.verifiedProducts,
        labelVerdictState: w.labelVerdictState,
        absenceRule: w.absenceRule,
        linkLabel: 'FINESTRA COLTURALE CORRELATA',
        ui: w.ui, provenance: P.REAL_DERIVED,
      };
    }),
    P.REAL_DERIVED,
    'canonical window beside the observed competitor corpus for the same crop; a correlated window, never an opportunity',
    { source: 'derived · cropWindows + competitorActivities' }
  );

  /* ---- THE BUSINESS PREPARATION CLOCK ----------------------------------
     A channel purchase lead time is NOT externally observable. These offsets
     are a Sintonia planning rule, and until now the screen printed them as bare
     dates with no label — a reader had no way to tell them apart from an
     agronomic date. They survive here, whole, under their own provenance class,
     so the view can fence and caption them instead of deleting them.

     observable:false is the load-bearing field. */
  const preparation = {
    provenance: 'SINTONIA_INTERPRETATION',
    observable: false,
    basis: 'Regola di pianificazione Sintonia. Non è un fatto osservato e non deriva da alcuna fonte esterna.',
    leadDays: 90,
    ladder: [
      { days: 90, dept: 'MARKET DEVELOPMENT', text: 'Start regional validation' },
      { days: 60, dept: 'MARKETING', text: 'Prepare communication assets' },
      { days: 45, dept: 'SALES / RTV', text: 'Prepare customer conversations' },
      { days: 30, dept: 'SUPPLY', text: 'Review internal readiness' },
      { days: 14, dept: 'SALES / RTV', text: 'Activate field execution' },
    ],
    departments: [
      { dept: 'REGULATORY / PORTFOLIO', fromDays: -210, toDays: -150 },
      { dept: 'SUPPLY', fromDays: -150, toDays: -60 },
      { dept: 'MARKET DEVELOPMENT', fromDays: -180, toDays: -120 },
      { dept: 'MARKETING', fromDays: -120, toDays: -75 },
      { dept: 'TECHNICAL / SCIENCE', fromDays: -60, toDays: -10 },
      { dept: 'SALES / RTV', fromDays: -75, toDays: -25 },
    ].map((d) => Object.assign({}, d, DEPARTMENT_UI[d.dept] || DEPARTMENT_UI.DEFAULT)),
    /* The offsets anchor on a canonical start date. Where there is none there is
       nothing to anchor to, so the block is omitted for that row rather than
       anchored on the reference date. Measured: 5 of 29 windows are omitted. */
    anchorRule: 'offsets apply to windowCalendarRows.startDate; when startDate is null the whole preparation block is omitted for that row',
    omittedWindows: cropWindows.records.filter((w) => !w.startDate).map((w) => w.windowId),
  };

  /* ── 8 · THE COLLECTION SET ─────────────────────────────────────────────
     Every family the receiver is prepared to accept. An empty one is valid. */
  const collections = {
    /* products */
    productsRegulatory, productsCommercial, productRelationships,
    products: productsColl, labelVerdicts, regulatoryLinks, portfolioLinksByCrop,
    activeIngredients, productActiveIngredients,
    /* agronomy */
    cropWindows, currentFieldSignals, fieldBulletins,
    cropEconomicWeight, cropLabelReach,
    windowCalendarRows, windowsByRegion,
    /* market */
    marketObservations, marketByCrop, marketSummaries,
    /* competitor */
    competitorActivities, competitorCompanies, competitorProducts,
    competitorCropDensity, competitorIssueDensity, competitorMatrix,
    competitorWindowMoments, communicationAxis,
    /* science */
    scienceRecords, researchers, scienceThemes, resistance, scienceInstitutions,
    /* voices and people */
    publicVoices, publicChannels, publicPeople, people,
    /* future — three different regulatory clocks, never one */
    regulatoryFuture, regulatoryFutureFacts, regulatoryFutureSignals,
    agrometConditions, futureEvents,
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

  /* Display label per layer. The panel stops carrying its own layer names, which
     is what let a screen call the archive "records" and the window table
     "cases" in the same column. */
  const LAYER_LABEL = {
    productsRegulatory: 'Prodotti · registro', productsCommercial: 'Prodotti · catalogo',
    productRelationships: 'Relazioni prodotto', products: 'Portafoglio',
    labelVerdicts: 'Audit etichette', regulatoryLinks: "Righe d'uso autorizzate",
    portfolioLinksByCrop: "Righe d'uso per coltura",
    activeIngredients: 'Sostanze attive', productActiveIngredients: 'Prodotto × sostanza attiva',
    cropWindows: 'Finestre colturali canoniche', currentFieldSignals: 'Letture di campo e atti regionali',
    fieldBulletins: 'Bollettini fitosanitari',
    cropEconomicWeight: 'Peso economico delle colture',
    cropLabelReach: 'Portata delle etichette per coltura',
    windowCalendarRows: 'Calendario finestre', windowsByRegion: 'Finestre per regione',
    marketObservations: 'Osservazioni di prezzo', marketByCrop: 'Mercato per coltura',
    marketSummaries: 'Analisi di mercato (manifesto)',
    competitorActivities: 'Comunicazione pubblica osservata', competitorCompanies: 'Aziende osservate',
    competitorProducts: 'Prodotti concorrenti citati', competitorCropDensity: 'Densità per coltura',
    competitorIssueDensity: 'Densità per avversità', competitorMatrix: 'Matrice azienda × coltura',
    competitorWindowMoments: 'Finestra × concorrenza', communicationAxis: 'Vocabolario pubblicato',
    scienceRecords: 'Record scientifici', researchers: 'Ricercatori', scienceThemes: 'Temi bibliometrici',
    resistance: 'Casi di resistenza confermati', scienceInstitutions: 'Istituzioni (affiliazione autore)',
    publicVoices: 'Voci pubbliche', publicChannels: 'Canali pubblici', publicPeople: 'Persone con evidenza pubblica',
    people: 'Persone / Ricercatori',
    regulatoryFuture: 'Scadenze di autorizzazione italiane',
    regulatoryFutureFacts: 'Scadenze di approvazione europee (fatti)',
    regulatoryFutureSignals: 'Letture sul rinnovo europeo',
    agrometConditions: 'Condizioni agrometeo',
    futureEvents: 'Eventi di settore', opportunities: 'Convergenze da validare', futureSignals: 'Segnali futuri',
    sources: 'Registro delle fonti', news: 'Stampa tecnica',
    relationships: 'Relazioni dichiarate', clientSafeCrossings: 'Incroci verificati',
    archive: 'Archivio (indice)',
    futureScenarios: 'Scenari di presentazione', opportunityScenarios: 'Casi di presentazione',
    fieldMessages: 'Integrazione Field Sales (dimostrativa)',
  };

  /* real / derived / demo are now three different things, not two.
     REAL_DERIVED is honest work done ON real records — it is neither a raw
     observation nor a demo row, and counting it as "real" inflated the package.
     isIndex marks a layer whose rows re-index records already counted in
     another layer, so a total can be published without double counting. */
  const provenanceSummary = primaryKeys.map((k) => {
    const c = collections[k];
    const cls = (r) => provOf(r, c.provenance);
    const derived = c.records.filter((r) => cls(r) === P.REAL_DERIVED).length;
    const demo = c.records.filter((r) => !!DEMO_CLASSES[cls(r)]).length;
    return {
      layer: k,
      label: LAYER_LABEL[k] || k,
      provenance: c.provenance,
      source: c.source,
      total: c.count,
      real: c.count - derived - demo,
      derived,
      demo,
      isIndex: !!c.isIndex,
      note: c.note,
    };
  });

  const counts = Object.keys(collections).reduce((a, k) => { a[k] = collections[k].count; return a; }, {});
  /* THE GATE, AS A TABLE THE TRANSPARENCY PANEL CAN PRINT.
     Three numbers per layer, never one: how many records the layer holds, how
     many of them may sustain a client-visible claim, and how large the corpus
     behind them is. `clientSafe: null` means the source predates the flag and
     must be printed as "non dichiarato", never as 0. */
  const clientSafeSummary = primaryKeys.map((k) => {
    const c = collections[k];
    return {
      layer: k,
      label: LAYER_LABEL[k] || k,
      count: c.count,
      clientSafe: c.clientSafe,
      corpusOnly: c.corpusOnlyCount || 0,
      corpus: c.corpus,
      state: c.clientSafeState,
      identityOnly: c.identityOnlyCount || 0,
      law: c.law || null,
      v21Family: c.v21Family || null,
      declaredTotal: c.declaredTotal === undefined ? null : c.declaredTotal,
      declaredClientSafe: c.declaredClientSafe === undefined ? null : c.declaredClientSafe,
      countReconciles: c.countReconciles === undefined ? null : c.countReconciles,
      clientSafeReconciles: c.clientSafeReconciles === undefined ? null : c.clientSafeReconciles,
    };
  });
  const clientSafeTotals = clientSafeSummary.reduce((a, r) => ({
    records: a.records + r.count,
    clientSafe: a.clientSafe + (typeof r.clientSafe === 'number' ? r.clientSafe : 0),
    corpusOnly: a.corpusOnly + r.corpusOnly,
    declaredLayers: a.declaredLayers + (r.state === 'DECLARED' ? 1 : 0),
    undeclaredLayers: a.undeclaredLayers + (r.state === 'DECLARED' ? 0 : 1),
  }), { records: 0, clientSafe: 0, corpusOnly: 0, declaredLayers: 0, undeclaredLayers: 0 });
  const totals = provenanceSummary.reduce(
    (a, r) => ({ total: a.total + r.total, real: a.real + r.real, derived: a.derived + r.derived, demo: a.demo + r.demo }),
    { total: 0, real: 0, derived: 0, demo: 0 }
  );
  const provenanceTotals = provenanceSummary.filter((r) => !r.isIndex).reduce(
    (a, r) => ({ real: a.real + r.real, derived: a.derived + r.derived, demo: a.demo + r.demo, indexRows: a.indexRows }),
    { real: 0, derived: 0, demo: 0, indexRows: provenanceSummary.filter((r) => r.isIndex).reduce((s, r) => s + r.total, 0) }
  );

  /* ── JOIN HEALTH · every vocabulary join, measured, not asserted ─────────
     A join in this model is a lookup from one table's wording to another's. The
     failure that matters is SILENT: the wording changes on one side, the lookup
     misses, and a screen prints an absence over a fact it can prove. Nothing
     crashes and no count goes red, so the suite stays green while the sentence
     on screen inverts (§10).

     This is the state of every one of them as a number a check can assert on,
     so the next such drift is caught by arithmetic and not by an auditor
     reading a render. Nothing here is displayed and nothing here is a fact
     about Italian agriculture — it is the model reporting on itself. */
  const joinHealth = (() => {
    const rate = (n, filled) => ({ n, filled, missPct: n ? Math.round(((n - filled) / n) * 1000) / 10 : 0 });
    const oppResolved = opportunities.records.filter((o) => o.cropKeys.length && o.issueKey).length;
    return {
      /* the label audit <-> canonical window join, both sides keyed through
         issueResolve; the crop side stays on the canonical English vocabulary */
      labelAuditToWindow: Object.assign(rate(cropWindows.count, cropWindows.records.filter((w) => w.verifiedProducts.length || w.notFoundProducts.length).length),
        { verified: cropWindows.records.filter((w) => w.verifiedProducts.length).length,
          note: 'a window with no verdict was not audited; it is not a window with no product' }),
      /* the regional regulatory act <-> canonical window join, crop through
         cropResolve and issue through issueResolve on both sides */
      fieldSignalToWindow: Object.assign(rate(cropWindows.count, cropWindows.records.filter((w) => w.regulatory).length),
        { note: 'only 7 regional acts exist upstream and 3 have no canonical window at all' }),
      /* the opportunity -> label audit question, crop through cropResolve and
         issue through the resolver-generated OPP_ISSUE keys */
      opportunityToLabelAudit: Object.assign(rate(opportunities.count, oppResolved),
        { note: 'IT-OPP-003 is portfolio-wide and correctly resolves to no crop and no issue' }),
      /* crop vocabulary resolution per source family */
      cropVocabulary: {
        news: rate(news.count, news.records.filter((r) => r.cropCanonical).length),
        voices: rate(publicVoices.count, publicVoices.records.filter((r) => r.cropCanonical).length),
        fieldSignals: rate(currentFieldSignals.count, currentFieldSignals.records.filter((r) => r.cropCanonical).length),
        marketSeries: rate(marketObservations.count, marketObservations.records.filter((r) => r.cropKey).length),
        competitorActivities: rate(competitorActivities.count, competitorActivities.records.filter((r) => r.crops.length).length),
        note: 'a null here is only a fault when the source named a crop; an umbrella word (colture, cereali, orticole) must stay null',
      },
      /* enum-keyed presentation and grouping tables */
      enums: {
        /* Measured over the sources that DECLARE A TYPE, which after V2.1 is
           the 31 client-safe registry rows: the other 158 are corpus stubs
           that carry an id and a QA state and nothing else, so they have no
           TYPE to group and their absence is not a join coming unhooked. The
           guarantee is unchanged and still exact — every source that names a
           type resolves to a group — only the denominator now says which
           rows were actually asked the question. */
        sourceGroup: rate(sources.records.filter((r) => r.type).length, sources.records.filter((r) => r.group).length),
        personCategory: rate(people.records.length, people.records.filter((r) => PERSON_CATEGORY_LABEL[U(r.category)]).length),
        themeUi: rate(researchers.count, researchers.records.filter((r) => r.themeLabel).length),
        windowStatus: rate(cropWindows.count, cropWindows.records.filter((r) => STATUS_UI[U(r.status)]).length),
        archivePlatform: rate(archive.records.length, archive.records.filter((r) => !r.platform || ARCHIVE_PLATFORM_SOURCE[U(r.platform)]).length),
      },
      /* the ORCID join behind the publications panel */
      publications: {
        people: people.records.length,
        researchers: people.researcherCount,
        withOrcid: people.withOrcid,
        withPublications: people.withPublications,
        scienceRecords: scienceRecords.count,
        distinctAuthorsInScience: Object.keys(worksByOrcid).length,
        note: people.publicationAbsenceNote,
      },
    };
  })();

  /* narrative debt, measured rather than assumed */
  const NARRATIVE_FIELDS = [
    ['publicVoices', publicVoices.records, ['proves', 'notProves']],
    ['news', news.records, ['summary', 'caveat', 'contentKindMeaning']],
    ['futureSignals', futureSignals.records, ['whyWatch', 'observedFacts', 'interpretation', 'nextWindow', 'portfolioConnection', 'whoIsTalking', 'whatChanged']],
    ['opportunities', opportunities.records, ['whatIsHappening', 'whyItMatters', 'currentEvidence', 'whatWeKnow', 'whatWeDoNotKnow', 'interpretations']],
    ['currentFieldSignals', currentFieldSignals.records, ['expectedCycle', 'observedStage', 'regulatoryWindow', 'preparationWindow', 'adamaProductsNote']],
    ['resistance', resistance.records, ['mechanism']],
    ['futureEvents', futureEvents.records, ['note', 'participationLaw']],
    ['sources', sources.records, ['role', 'limitations', 'accessEvidence', 'routeEvidenceNote']],
    /* the families V2.1 added or rewrote */
    ['currentFieldSignals·v21', currentFieldSignals.records, ['nextImportantWindow', 'fieldReportedStage', 'evidenceStatusWhy']],
    ['fieldBulletins', fieldBulletins.records, ['interventionGuidance', 'evidenceStatusWhy']],
    ['regulatoryLinks', regulatoryLinks.records, ['linkMeans', 'notProves', 'evidenceStatusWhy']],
    ['productsRegulatory', productsRegulatory.records, ['evidenceStatusWhy']],
    ['productsCommercial', productsCommercial.records, ['commercialContractWhy']],
    ['activeIngredients', activeIngredients.records, ['notProves']],
    ['productActiveIngredients', productActiveIngredients.records, ['notProves', 'evidenceStatusWhy']],
    ['regulatoryFutureFacts', regulatoryFutureFacts.records, ['proves', 'notProves']],
    ['regulatoryFutureSignals', regulatoryFutureSignals.records, ['whatItIs', 'proves', 'notProves']],
    ['agrometConditions', agrometConditions.records, ['whatItIs', 'proves', 'notProves']],
    ['cropEconomicWeight', cropEconomicWeight.records, ['whatItIs', 'proves', 'notProves', 'summaryClaimNote']],
    ['marketObservations', marketObservations.records, ['evidenceStatusWhy', 'seriesWarningText']],
    ['competitorActivities', competitorActivities.records, ['evidenceStatusWhy']],
    ['publicVoices·v21', publicVoices.records, ['notProves', 'roleEvidence']],
    ['resistance·v21', resistance.records, ['multipleResistance']],
    ['scienceRecords', scienceRecords.records, ['evidenceStatusWhy']],
    ['researchers', researchers.records, ['evidenceStatusWhy']],
    ['publicChannels', publicChannels.records, ['evidenceStatusWhy']],
  ];
  NARRATIVE_FIELDS.forEach(([family, recs, fields]) =>
    fields.forEach((f) => noteNarrative(family, f, recs.filter((r) => r[f] && r[f].state === KNOWLEDGE.NOT_APPROVED_FOR_DISPLAY).length)));

  /* THE OTHER HALF OF THE SAME MEASUREMENT, and the point of the V2.1
     package: how many narrative fields the upstream HAS now localized. Debt
     alone reads like a verdict on the model; published beside the credit it
     reads like what it is — a state of the upstream reading. */
  const narrativeCredit = [];
  NARRATIVE_FIELDS.forEach(([family, recs, fields]) =>
    fields.forEach((f) => {
      const n = recs.filter((r) => r[f] && r[f].state === KNOWLEDGE.CLEAR).length;
      if (n) narrativeCredit.push({ family, field: f, records: n });
    }));
  const narrativeState = {
    clearRecords: narrativeCredit.reduce((a, r) => a + r.records, 0),
    notApprovedRecords: narrativeDebt.reduce((a, r) => a + r.records, 0),
    clearFields: narrativeCredit.length,
    notApprovedFields: narrativeDebt.length,
    credit: narrativeCredit,
    debt: narrativeDebt,
    rule: 'a prose field is shown only when the upstream supplies an approved *_IT / *_EN variant',
  };

  /* ── 9 · SEARCH INDEX ───────────────────────────────────────────────────
     One index over the normalized model, in both languages. A search result
     opens the real entity it names — never a look-alike. */
  const searchIndex = [];
  /* Search terms are the one place where a research note becomes a visible
     fact: a note in the term list makes the record match a word nobody wrote
     about it, and the note text then appears in an autocomplete. TERMS()
     therefore drops the unknown sentence, drops anything longer than a term
     could plausibly be, folds diacritics and lowercases. */
  const TERM_MAX = 80;
  const TERMS = (list) => uniq(
    A(list).flatMap((t) => A(t))
      .map((t) => S(t))
      .filter((t) => t && !UNKNOWN_SENTINEL.test(t) && t.length <= TERM_MAX)
      .map((t) => fold(t).toLowerCase())
  );
  /* A crop is searchable in every vocabulary it is actually published in. Only
     unambiguous pairs are expanded; a group word ('cereali', 'colture',
     'CEREAL') has no unambiguous canonical partner and is indexed verbatim. */
  const cropTerms = (raw) => {
    const out = A(raw).slice();
    A(raw).forEach((c) => {
      /* The registry's own crop CODES first. A code may legitimately name two
         canonical crops — WHEAT_GENERIC is the only label row Durum Wheat has —
         and both have to be findable, so cropsFromCode is used, not cropFromCode. */
      cropsFromCode(c).forEach((k) => out.push(k));
      /* Then the resolver, instead of the three tables this chain used to name
         one by one. That chain omitted CROP_BY_PT and CROP_BY_CODE entirely, so
         a record whose crop the upstream left in Portuguese ('Videira') was
         indexed under that word alone and a search for 'Grapevine' or 'vite'
         did not reach it. A generic umbrella word still contributes nothing —
         cropResolve returns no keys for GENERIC_TERM — so 'cereali' is still
         indexed verbatim and never promoted to a crop. */
      const r = cropResolve(c);
      if (r.scope === 'RESOLVED' || r.scope === 'MULTI') r.keys.forEach((k) => out.push(k));
    });
    return uniq(out);
  };
  const issueTerms = (raw) => A(raw).slice();

  /* Every entry carries the group the results screen buckets on and the extra
     state its destination view needs, so the view is one reduce and one
     dispatcher instead of eight per-kind scans. */
  const idx = (kind, group, id, label, terms, route, meta, routeArgs, provenance) =>
    id && searchIndex.push({
      kind, group, id, label: String(label || id), route: route || kind,
      terms: TERMS(terms),
      meta: meta === undefined ? null : meta,
      routeArgs: routeArgs || null,
      provenance: provenance || P.REAL_SOURCE,
    });

  products.forEach((p) => idx('product', 'PRODUCT', p.name, p.name, [p.name, p.ai, p.categoryLabel, p.line, cropTerms(p.crops)], 'product', p.aiLabel || p.categoryLabel, { productName: p.name }, P.REAL_SOURCE));
  opportunities.records.forEach((o) => idx('case', 'OPPORTUNITY', o.id, o.title || [o.issue, o.region].filter(Boolean).join(' · '), [o.title, o.issue, o.crop, cropTerms(o.cropKeys), o.regionKeys, o.id, o.legacyCaseId], 'case', o.crop, { caseId: o.id }, o.provenance));
  publicVoices.records.forEach((v) => idx('voice', 'FIELD_VOICE', v.id, v.person || v.channel || v.title, [v.person, v.channel, cropTerms([v.crop]), v.issue, v.title, v.organization], 'voices', v.platform, { voiceId: v.id }, v.provenance));
  futureSignals.records.forEach((f) => idx('signal', 'SIGNAL', f.id, [f.issue, f.region].filter(Boolean).join(' · ') || f.id, [f.issue, f.crop, f.region, f.id], 'signal', f.crop, { signalId: f.id }, f.provenance));
  researchers.records.forEach((r) => idx('researcher', 'PEOPLE', r.id, r.name, [r.name, r.institutions, r.theme, r.themeLabel], 'person', r.orgLabel, { personId: r.id }, r.provenance));
  resistance.records.forEach((r) => idx('resistance', 'SCIENCE', r.id, r.species, [r.species, r.speciesIt, cropTerms([r.crop]), r.family], 'gire', r.crop, { gireFocusId: r.id }, r.provenance));
  cropWindows.records.forEach((w) => idx('window', 'WINDOW', w.id, [w.issue, w.region].filter(Boolean).join(' · '), [w.crop, w.issue, w.region, w.id, w.legacyCaseId], 'window', w.crop, { windowId: w.windowId }, w.provenance));
  sources.records.forEach((s) => idx('source', 'SOURCE', s.id, s.name, [s.name, s.type, s.geography, s.country, s.groupLabel], 'source', s.type, { sourceId: s.id }, s.provenance));
  futureEvents.records.forEach((e) => idx('event', 'EVENT', e.id, e.name, [e.name, e.location, e.sector, e.cropRelevance, e.organizer], 'event', e.location, { eventId: e.id }, e.provenance));
  news.records.forEach((n) => idx('news', 'NEWS', n.id, n.title, [n.title, n.publisher, cropTerms([n.crop]), n.issue, n.author], 'news', n.publisher, { newsId: n.id }, n.provenance));
  scienceRecords.records.forEach((r) => idx('science', 'SCIENCE', r.id, r.title, [r.title, r.institution, cropTerms([r.crop]), issueTerms([r.issue]), r.author, r.venue], 'science', r.institution, { sciFocusId: r.id }, r.provenance));
  competitorCompanies.records.forEach((c) => idx('company', 'COMPETITOR', c.name, c.name, [c.name, c.productsProved, c.pages], 'company', null, { fCompany: c.name }, c.provenance));
  competitorActivities.records.forEach((a) => idx('competitor', 'COMPETITOR', a.id, a.displayName, [a.company, a.page, a.products, cropTerms(a.crops), issueTerms(a.issues)], 'cproduct', a.company, { activityId: a.id }, a.provenance));
  marketObservations.records.forEach((m) => idx('market', 'MARKET', m.id, [m.product, m.market].filter(Boolean).join(' · '), [m.product, m.market, m.geography, m.group, m.cropKey], 'market', m.unit, { mCrop: m.ui.marketCropKey }, m.provenance));
  publicChannels.records.forEach((c) => idx('channel', 'FIELD_VOICE', c.id, c.name, [c.name, c.contentTypeExample, c.platform], 'voices', c.platform, { channelId: c.id }, c.provenance));

  /* Demo rows are never pushed: a search result must open a real entity. */

  const search = (query, limit) => {
    const q = fold(String(query || '')).trim().toLowerCase();
    if (q.length < 2) return [];
    const out = searchIndex.filter((e) => fold(e.label).toLowerCase().includes(q) || e.terms.some((t) => t.includes(q)));
    return limit ? out.slice(0, limit) : out;
  };
  /* Group the hits the way the results screen renders them, in one pass. */
  const searchGrouped = (query, limit) => {
    const hits = search(query, limit);
    const order = ['OPPORTUNITY', 'WINDOW', 'PRODUCT', 'SIGNAL', 'FIELD_VOICE', 'SCIENCE', 'PEOPLE', 'COMPETITOR', 'MARKET', 'SOURCE', 'NEWS', 'EVENT'];
    const by = {};
    hits.forEach((h) => { (by[h.group] = by[h.group] || []).push(h); });
    return order.filter((g) => by[g]).map((g) => ({ group: g, count: by[g].length, entries: by[g] }));
  };

  /* ── 10 · VALIDATION REPORT ─────────────────────────────────────────────
     None of the wrong-key bugs this rebuild fixed would have survived a build
     that had to publish what it accepted, what it rejected, and how full each
     contract field actually is. fieldCoverage is measured, not asserted: it is
     produced by counting the built records, so it cannot drift from them. */
  const COVERAGE_FIELDS = {
    cropWindows: ['startDate', 'endDate', 'status', 'dateState', 'region', 'verifiedProducts', 'regulatory', 'sourceIds'],
    currentFieldSignals: ['cropCanonical', 'region', 'regulatoryAct', 'coverageState'],
    marketObservations: ['cropKey', 'periodStart', 'periodEnd', 'stage', 'publicationDate', 'changeVsPrev', 'changeVsYearAgo'],
    competitorActivities: ['startDate', 'page', 'text', 'cropsCanonical', 'issuesObserved'],
    competitorCompanies: ['firstObserved', 'lastObserved', 'pages'],
    competitorProducts: ['activityIds', 'firstSeen'],
    scienceRecords: ['publishedAt', 'doi', 'author', 'orcid', 'institution', 'venue', 'themeKey'],
    researchers: ['orcid', 'openalexId', 'institutions', 'theme', 'lastActivity', 'role', 'factRegion'],
    publicPeople: ['role', 'identityEvidence', 'roleEvidence'],
    sources: ['role', 'group', 'frequency', 'accessStatus', 'limitations', 'latestObservationISO'],
    futureEvents: ['name', 'url', 'startDate', 'organizer', 'cropRelevance'],
    news: ['publisher', 'url', 'dateISO', 'region', 'publisherSourceId'],
    publicChannels: ['url', 'platform', 'exampleTitle'],
    regulatoryLinks: ['cropKey', 'target', 'targetOnLabel', 'linkStrength', 'quoteFromLabel', 'labelUrl', 'timing'],
    regulatoryFuture: ['expiryISO', 'holder', 'status'],
    regulatoryFutureFacts: ['activeIngredient', 'euExpirationOfApproval', 'euCelex', 'italianRegistrations', 'geographyLaw'],
    regulatoryFutureSignals: ['whatItIs', 'proves', 'notProves'],
    activeIngredients: ['normalizedName', 'moaState', 'euState', 'euExpirationOfApproval', 'cas', 'frac', 'hrac', 'irac'],
    productActiveIngredients: ['productKey', 'activeIngredientId', 'componentsInProduct'],
    fieldBulletins: ['title', 'geographyState', 'regionRepresents', 'interventionGuidance', 'citation'],
    cropEconomicWeight: ['cropKeys', 'isSummaryClaim', 'whatItIs', 'observationClass'],
    cropLabelReach: ['crop', 'productsMentioning', 'productsWithUseRow'],
    agrometConditions: ['whatItIs', 'regionKeys', 'observationClass'],
    clientSafeCrossings: ['crossingType', 'cropId'],
    productsCommercial: ['category', 'catalogUrl', 'regId', 'holder', 'commercialContract'],
    productsRegulatory: ['reg', 'holder', 'ai', 'expiryISO', 'labelUrl', 'crops', 'targets'],
    archive: ['dateISO', 'sourceId', 'crop', 'url'],
    opportunities: ['cropKeys', 'issueKey', 'observationDate', 'freshnessDays', 'windowId'],
  };
  const nonEmpty = (v) => !(v === null || v === undefined || v === '' || (Array.isArray(v) && !v.length));
  const validationReport = {
    referenceDate: REFERENCE_DATE,
    families: primaryKeys.map((k) => {
      const c = collections[k];
      const fields = COVERAGE_FIELDS[k] || [];
      const cov = {};
      fields.forEach((f) => { cov[f] = c.records.filter((r) => nonEmpty(r[f])).length; });
      const fam = ingestReport.families.filter((x) => x.family === k)[0] || null;
      return {
        name: k, sourceKey: c.source, received: fam ? (fam.tried || []).reduce((s, t) => s + (t.in || 0), 0) : c.count,
        accepted: c.count, rejected: (c.rejected || []).length, rejections: c.rejected || [],
        fieldCoverage: cov, emptyValid: c.count === 0,
      };
    }),
    /* An id that means two different records is the one failure this index
       cannot recover from, so it is checked rather than assumed. */
    idCollisions: (() => {
      const out = [];
      primaryKeys.forEach((k) => {
        const seen = {};
        collections[k].records.forEach((r) => { if (r && r.id !== undefined) { if (seen[r.id]) out.push({ family: k, id: r.id }); seen[r.id] = 1; } });
      });
      return out;
    })(),
    /* A REAL_* collection must not contain a demo-class record. Empty is the
       only acceptable value here. */
    demoLeaks: primaryKeys.filter((k) => !DEMO_CLASSES[collections[k].provenance])
      .flatMap((k) => collections[k].records.filter((r) => isDemo(r, collections[k].provenance)).map((r) => ({ family: k, id: r && r.id }))),
    narrativeDebt,
  };

  /* ── 11 · PUBLIC CONTRACT ───────────────────────────────────────────── */
  window.ITALY_APP_MODEL = {
    version: '3.2',
    compiled: REFERENCE_DATE,

    /* one clock */
    referenceDate: REFERENCE_DATE, REF, daysFrom, asDate, isoOf, fmtDate,

    /* provenance vocabulary */
    PROVENANCE: P, PRECEDENCE, provOf, isDemo,
    STRENGTH, ABSENCE_RULE,
    KNOWLEDGE, narrative,
    CATEGORY_UI, categoryOf,

    /* presentation tokens — icon, colour, order, grid. No facts live here. */
    UI: {
      CATEGORY: CATEGORY_UI,
      INK, inkOn, NEUTRAL,
      STATUS: STATUS_UI,
      DEPARTMENT: DEPARTMENT_UI,
      SOURCE_TYPE_COLOR,
      ARCHIVE: ARCHIVE_UI,
      REGION_GRID,
      fmtDate,
    },

    /* the declared joins, exported so an auditor can read them without reading
       the code that uses them */
    /* THE RESOLVERS THEMSELVES, exported on purpose. Any caller that reaches
       for a raw table below and keys it on a source string is one translation
       away from a silent miss; these three answer the same question in every
       vocabulary the package publishes and report the scope of the answer
       (RESOLVED / MULTI / GENERIC_TERM / NOT_OBSERVED / UNMAPPED) instead of
       returning a bare null a caller can mistake for "not published". */
    cropResolve, issueResolve, regionResolve, cropsFromCode, orcidKey,

    lookups: {
      CROP_KEY, CROP_BY_CODE, CROP_BY_CANON, CROP_BY_LATIN, CROP_BY_TOKEN, CROP_BY_IT, CROP_BY_PT,
      GENERIC_CROP_TERMS, MARKET_CROP, MARKET_VIEW_KEY, THEME_UI,
      SOURCE_GROUP, SOURCE_GROUP_LABEL, OPP_CROP, OPP_ISSUE, OPP_ISSUE_DECLARED,
      ARCHIVE_PLATFORM_SOURCE, PERSON_CATEGORY_LABEL, LAYER_LABEL,
      /* NOT PROVIDED, deliberately. An ISSUE_TARGET table would map each
         canonical window issue ('Septoria Leaf Blotch') onto the Latin targets
         used by the registry use rows ('Zymoseptoria tritici'). Measured: only
         6 of the 22 window issues have ANY matching target among the 219 use
         rows; the other 16 — including Flavescenza Dorata, European Corn Borer,
         Olive Fruit Fly, Codling Moth, Downy Mildew and every wheat rust — have
         zero. Authoring the table would therefore be authoring most of it, and
         the resulting rows would look like registry evidence while being a
         Sintonia guess. Registry use rows are instead exposed as themselves, in
         collections.regulatoryLinks, keyed by their own Latin target. */
      ISSUE_TARGET: null,
      ISSUE_TARGET_STATE: 'NOT_AUTHORED · 16 of 22 window issues have no matching target in the 219 use rows',
    },

    /* the product law, stated in the contract itself */
    productDefinition: 'EXTERNAL_INTELLIGENCE_CORE',
    coreRequiresPrivateData: false,
    NOT_OBSERVABLE: P.NOT_OBSERVABLE,

    /* ── THE V2.1 PACKAGE, AS THE MODEL RECEIVED IT ─────────────────────
       The build id, the three rules the package states about itself, and the
       per-family manifest. Published so a screen can show WHICH reading it is
       rendering, and so an auditor can check the model against the package
       without opening either. */
    V21: {
      present: !!V21H,
      buildId: S(V21H && V21H.BUILD_ID),
      schemaVersion: S(V21H && V21H.SCHEMA_VERSION),
      builtAt: S(V21H && V21H.BUILT_AT),
      referenceDate: S(V21H && V21H.REFERENCE_DATE),
      clientSafeRule: (V21H && V21H.CLIENT_SAFE_RULE) || null,
      languageRule: (V21H && V21H.LANGUAGE_RULE) || null,
      transportLaw: S(V21H && V21H.TRANSPORT_LAW),
      doubleCountWarning: S(V21H && V21H.DOUBLE_COUNT_WARNING),
      manifest: A(V21H && V21H.MANIFEST),
      families: Object.keys(V21C),
      /* which model collection each V2.1 family became. Two names collide
         with an older meaning and the mapping says so out loud. */
      familyToCollection: {
        'products.regulatory': 'productsRegulatory',
        'products.commercial': 'productsCommercial',
        'products.relationships': 'regulatoryLinks',
        'products.activeIngredients': 'productActiveIngredients',
        activeIngredients: 'activeIngredients',
        regulatoryFutureFacts: 'regulatoryFutureFacts',
        /* NAME COLLISION 1 · V2.1 CROP-WINDOWS.json is the 7-row field
           reading, not the 29-row audited window contract. */
        windows: 'currentFieldSignals',
        fieldSignals: 'fieldBulletins',
        cropEconomicWeight: 'cropEconomicWeight',
        market: 'marketObservations',
        competitors: 'competitorActivities',
        science: 'scienceRecords',
        researchers: 'researchers',
        resistance: 'resistance',
        voices: 'publicVoices',
        channels: 'publicChannels',
        /* NAME COLLISION 2 · V2.1 REGULATORY-FUTURE.json is a set of written
           readings of the European renewal procedure. The model's
           `regulatoryFuture` is the ITALIAN authorisation expiry calendar and
           keeps that name because every screen already reads it. */
        regulatoryFuture: 'regulatoryFutureSignals',
        agromet: 'agrometConditions',
        /* DOUBLE COUNT · EVENTS is the countable collection; FUTURE-EVENTS is
           applied to it as futureEvents.futureCut, never as a second layer. */
        events: 'futureEvents',
        futureEvents: 'futureEvents.futureCut (a view, not a collection)',
        opportunities: 'opportunities',
        futureSignals: 'futureSignals',
        sources: 'sources',
        news: 'news',
        relationships: 'relationships',
        crossings: 'clientSafeCrossings',
      },
      /* V2.1 supplies NO canonical 29-window contract, no companies table, no
         competitor-product table, no bibliometric themes, no people table and
         no market-summary manifest. Those five families keep their existing
         source and are listed here so the absence is a statement, not a gap. */
      notSuppliedByV21: ['cropWindows', 'competitorCompanies', 'competitorProducts',
        'scienceThemes', 'publicPeople', 'marketSummaries', 'cropLabelReach'],
    },

    /* the client-safe gate, as numbers a panel can print */
    clientSafeSummary, clientSafeTotals,
    narrativeState,

    /* data */
    collections, counts, totals, provenanceSummary, provenanceTotals, joinHealth,
    searchIndex, search, searchGrouped, TERMS, cropTerms, issueTerms,
    products, productByKey, findProduct, strengthFor,
    productRelationships,
    labelVerdicts,
    people,
    preparation,
    publicationsForPerson,
    sourceById: (id) => sourceById[U(id)] || null,
    sourceNameOf,

    /* Explicitly-labelled demo configuration (§5). These are invented ADAMA
       business rules, not observations and not colours, so they carry a
       provenance stamp instead of being hardcoded inside a caption. */
    DEMO: {
      provenance: P.SYNTHETIC_DEMO,
      PREP_LEAD_DAYS: preparation.leadDays,
      PLANNING_LADDER: preparation.ladder,
      PLANNING_LEAD_RULE: preparation.departments,
    },

    /* the ingestion boundary, so the receiver can be audited */
    ingest: {
      report: ingestReport,
      narrativeDebt,
      narrativeState,
      v21BuildId: S(V21H && V21H.BUILD_ID),
      v21Families: Object.keys(V21C).length,
      registeredSources: Object.keys(RAW).filter((k) => RAW[k] && (Array.isArray(RAW[k]) ? RAW[k].length : Object.keys(RAW[k]).length)),
      handoffV21Present: !!RAW.HANDOFF_V21,
      families: primaryKeys,
      validationReport,
    },
    validationReport,
  };
})();
