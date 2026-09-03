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

  /* L'IDENTITA DI UN PRODOTTO NON E LA SUA ORTOGRAFIA.
     Il registro scrive NIMROD 250 EW; il catalogo, per lo stesso prodotto,
     scrive NIMRODR 250 EW — il simbolo ® e arrivato a monte trasformato in una
     lettera R. Altrove il catalogo tiene il simbolo vero (Folpan® Energy), o
     un punto in piu (NICOGAN V.O. contro NICOGAN VO), o due spazi (TAIFUN  MK).
     La chiave di unione era U(nome) — trim e maiuscole — quindi quindici
     prodotti del catalogo non trovavano il proprio numero di registrazione e la
     schermata diceva loro «Non presente in questa lettura del registro»,
     inventando un'assenza che il pacchetto non dichiara.

         IL NOME SI MOSTRA. LA CHIAVE SI UNISCE.
         NON SONO LO STESSO OGGETTO E NON DEVONO ESSERLO.

     PKEY tiene solo lettere e cifre: e stabile davanti a ®, punti e spazi.
     PKEY_ALT aggiunge la sola variante che il difetto misurato richiede — la R
     di troppo dopo il marchio — e nulla di piu, perche ogni variante in piu e
     una fusione possibile fra due prodotti diversi. Misurato sul pacchetto:
     zero collisioni da entrambi i lati, quattordici prodotti ricongiunti. */
  const PKEY = (v) => String(v || '').toUpperCase().replace(/[®™©]/g, '').replace(/[^A-Z0-9]/g, '');
  const PKEY_ALTS = (v) => {
    const out = [];
    const push = (k) => { if (k && out.indexOf(k) < 0) out.push(k); };
    const bases = [PKEY(v)];
    /* un solo record del catalogo finisce con « 0» appeso — GOLTIXR TOP 0 —
       e nel registro non esiste nessun altro nome che quello zero renderebbe
       ambiguo. La variante e ammessa solo per quella forma esatta. */
    if (/\s0$/.test(String(v || ''))) bases.push(PKEY(String(v).replace(/\s0$/, '')));
    for (const b of bases) {
      push(b);
      const m = /^([A-Z]{4,})R([A-Z0-9]*)$/.exec(b);
      if (m) push(m[1] + m[2]);
    }
    return out.slice(1);
  };
  const PKEY_ALT = (v) => PKEY_ALTS(v)[0] || null;
  /* Il nome resta quello commerciale; si ripara solo il segno diventato
     lettera, e soltanto dove il marchio senza la R esiste davvero altrove —
     cosi «NIMRODR» torna «NIMROD®» e nessun nome viene riscritto a intuito. */
  const PNAME_FIX = (name, known) => {
    /* Un solo nome del catalogo finisce con uno zero staccato — «GOLTIXR TOP 0»
       contro «GOLTIX TOP» nel registro. Nessun prodotto si chiama davvero cosi:
       e residuo di lettura, e va tolto prima che il cliente lo legga. */
    const raw = String(name || '').trim().replace(/\s+0$/, '');
    const m = /^([A-Za-z]{4,})R(\b|\s|$)/.exec(raw);
    if (!m) return raw;
    const brand = m[1];
    if (!known || !known.has(PKEY(brand))) return raw;
    return brand + '\u00AE' + raw.slice(m[1].length + 1);
  };

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

  /**
   * One V2.1 family, ready for build().
   *
   * The receiver contract said `adapt: (r) => r` — the upstream would hand over
   * rows already in the shape the views read. It does not, and it should not:
   * the package publishes its OWN canonical contract (SCREAMING_CASE fields,
   * canonical ids, its own clock), and that contract is the reason two research
   * missions can be merged at all. Handing the identity function a V2.1 record
   * put `undefined` in every binding of every screen.
   *
   *     THE PACKAGE PUBLISHES A CONTRACT. THE MODEL PUBLISHES A SHAPE.
   *     THE ADAPTER IS THE SENTENCE THAT TRANSLATES ONE INTO THE OTHER,
   *     AND IT HAS TO BE WRITTEN DOWN SOMEWHERE.
   *
   * It is written here, beside the fixture adapter it replaces, so the two can
   * be read against each other — which is the only way to see that a field
   * stopped being populated rather than never existed.
   */
  const V21 = (family, adapt, validate) => {
    const d = RAW.HANDOFF_V21 && RAW.HANDOFF_V21[family];
    if (!d) return null;
    return {
      source: 'HANDOFF_V21 · ' + family,
      precedence: P.CANONICAL,
      rows: A(d),
      adapt: adapt || ((r) => r),
      validate: validate || null,
    };
  };

  /* ── 5b · THE V2.1 CANONICAL IDENTIFIERS ─────────────────────────────────
     The package speaks in ids, not in names: CROP_SUGAR_BEET, REGION_VENETO,
     ISSUE_DOWNY_MILDEW. That is the whole point of it — an id survives a
     translation, and six vocabularies collapse into one. But an id is not a
     label, and printing it would put SCREAMING_SNAKE on an Italian screen.

     These three tables are the join, written out in full rather than derived by
     string surgery. Twenty crops, twenty-two geographies, twenty-four issues:
     small, closed and countable. Written out, an id the package adds tomorrow
     resolves to null and is VISIBLE as unmapped; derived by de-underscoring, it
     would resolve to a plausible wrong word and be invisible.

         A TABLE THAT DOES NOT KNOW AN ID SAYS SO.
         A RULE THAT GUESSES ONE NEVER DOES.  */
  const CROP_BY_ID = {
    CROP_GRAPEVINE: 'Grapevine', CROP_MAIZE: 'Maize', CROP_OLIVE: 'Olive',
    CROP_SUGAR_BEET: 'Sugar Beet', CROP_APPLE: 'Apple', CROP_TOMATO: 'Tomato',
    CROP_RICE: 'Rice', CROP_SOYBEAN: 'Soybean', CROP_BARLEY: 'Barley',
    CROP_POTATO: 'Potato', CROP_DURUM_WHEAT: 'Durum Wheat',
    /* Both generic and soft wheat land on Wheat, which is the canonical crop
       that owns the window. The overlap with Durum Wheat is the one CROP_KEY
       already declares in its own note; it is not made worse here. */
    CROP_WHEAT_GENERIC: 'Wheat', CROP_SOFT_WHEAT: 'Wheat',
    /* Real crops with NO canonical window in this package. They keep their own
       name — a crop without a window is a fact, not a missing value. */
    CROP_PEACH: 'Peach', CROP_KIWI: 'Kiwi', CROP_PEAR: 'Pear',
    CROP_CITRUS: 'Citrus', CROP_SUNFLOWER: 'Sunflower',
  };
  /* Group words. They are NOT crops and must never be promoted to one: the
     resolver's own GENERIC_TERM rule, restated for the id vocabulary. */
  const CROP_ID_GENERIC = { CROP_STONE_FRUIT: 1, CROP_VEGETABLES: 1 };

  const REGION_BY_ID = {
    REGION_VALLE_D_AOSTA: "Valle d'Aosta", REGION_PIEMONTE: 'Piemonte',
    REGION_LOMBARDIA: 'Lombardia', REGION_TRENTINO_ALTO_ADIGE: 'Trentino-Alto Adige',
    REGION_VENETO: 'Veneto', REGION_FRIULI_VENEZIA_GIULIA: 'Friuli-Venezia Giulia',
    REGION_LIGURIA: 'Liguria', REGION_EMILIA_ROMAGNA: 'Emilia-Romagna',
    REGION_TOSCANA: 'Toscana', REGION_UMBRIA: 'Umbria', REGION_MARCHE: 'Marche',
    REGION_LAZIO: 'Lazio', REGION_ABRUZZO: 'Abruzzo', REGION_MOLISE: 'Molise',
    REGION_CAMPANIA: 'Campania', REGION_PUGLIA: 'Puglia',
    REGION_BASILICATA: 'Basilicata', REGION_CALABRIA: 'Calabria',
    REGION_SICILIA: 'Sicilia', REGION_SARDEGNA: 'Sardegna',
  };
  /* GEO_ITALY and GEO_EU are SCOPES, not regions. Putting them in the region
     table would have added two entries to every region filter and let a
     national fact be counted as a regional one. */
  const SCOPE_BY_ID = { GEO_ITALY: 'NATIONAL', GEO_EU: 'EUROPEAN' };

  /* Issue ids -> the published Italian and English name. Latin binomials are
     the same in both and are written once. */
  const ISSUE_BY_ID = {
    ISSUE_APHIDS: { it: 'Afidi', en: 'Aphids' },
    ISSUE_WEEDS_GENERIC: { it: 'Infestanti', en: 'Weeds' },
    ISSUE_POWDERY_MILDEW: { it: 'Oidio', en: 'Powdery mildew' },
    ISSUE_DOWNY_MILDEW: { it: 'Peronospora', en: 'Downy mildew' },
    ISSUE_RUST: { it: 'Ruggine', en: 'Rust' },
    ISSUE_SCAB: { it: 'Ticchiolatura', en: 'Scab' },
    ISSUE_BOTRYTIS: { it: 'Botrite', en: 'Botrytis' },
    ISSUE_SEPTORIA: { it: 'Septoria', en: 'Septoria' },
    ISSUE_FUSARIUM: { it: 'Fusariosi', en: 'Fusarium head blight' },
    ISSUE_CERCOSPORA: { it: 'Cercospora', en: 'Cercospora' },
    ISSUE_BLAST: { it: 'Brusone', en: 'Rice blast' },
    ISSUE_CODLING_MOTH: { it: 'Carpocapsa', en: 'Codling moth' },
    ISSUE_CORN_BORER: { it: 'Piralide', en: 'European corn borer' },
    ISSUE_DIABROTICA: { it: 'Diabrotica', en: 'Diabrotica' },
    ISSUE_GRAPE_MOTH: { it: 'Tignoletta della vite', en: 'Grape moth' },
    ISSUE_OLIVE_FLY: { it: 'Mosca dell’olivo', en: 'Olive fruit fly' },
    ISSUE_STINK_BUG: { it: 'Cimice asiatica', en: 'Brown marmorated stink bug' },
    ISSUE_TUTA: { it: 'Tuta absoluta', en: 'Tuta absoluta' },
    ISSUE_SCAPHOIDEUS: { it: 'Scaphoideus titanus', en: 'Scaphoideus titanus' },
    ISSUE_FLAVESCENCE: { it: 'Flavescenza dorata', en: 'Flavescence dorée' },
    ISSUE_AMARANTHUS: { it: 'Amaranthus', en: 'Amaranthus' },
    ISSUE_ECHINOCHLOA: { it: 'Echinochloa', en: 'Echinochloa' },
    ISSUE_LOLIUM: { it: 'Lolium', en: 'Lolium' },
    ISSUE_DROUGHT: { it: 'Stress idrico', en: 'Water stress' },
  };

  /* The package's three link strengths, mapped onto the two the portal renders.
     Declared here with the other V2.1 vocabularies because the label-reach
     recount reads it before the relationship family is built — a table used by
     two families belongs to neither of them.

       LINHA_DA_TABELA    crop and target on the SAME ROW of the use table
       BLOCO_DA_CULTURA   target INSIDE the crop's block, joined by «contro»
       DECLARACAO_DE_PRODUTO  two separate lists, joined by US

     The first two are the document doing the joining; the third is us
     approximating, and the package marks exactly those 518 rows
     CLIENT_SAFE=false. 886 + 626 = 1.512 = the package's own COUNT_CLIENT_SAFE,
     so this mapping is its law restated, not a judgement added. */
  /* { HRAC: ['5'], FRAC: ['8'] } -> 'HRAC 5 + FRAC 8'. The registry publishes
     the mode of action as a structure; two families render it, so the wording
     is written once. */
  const moaLabelOf = (moa) => {
    if (!moa || typeof moa !== 'object') return null;
    const parts = Object.keys(moa).map((k) => (A(moa[k]).length ? k + ' ' + A(moa[k]).join('/') : null)).filter(Boolean);
    return parts.length ? parts.join(' + ') : null;
  };

  const V21_LINK_STRENGTH = {
    LINHA_DA_TABELA: 'VERIFIED_LABEL_MATCH',
    BLOCO_DA_CULTURA: 'VERIFIED_LABEL_MATCH',
    DECLARACAO_DE_PRODUTO: 'RELATED_PORTFOLIO',
  };

  /* SRC_ESPLORADATI_ISTAT_IT__DATABROWSER -> 'esploradati.istat.it'. The
     package declares the key IS the host; this reads it back. */
  const hostFromSourceKey = (id) => {
    const t = U(id).replace(/^SRC_/, '').split('__')[0];
    if (!t) return null;
    const host = t.toLowerCase().replace(/_/g, '.');
    /* ONLY IF IT IS ACTUALLY A HOST.
       The key is derived from the URL — except where there was no URL. One
       source is keyed SRC_FONTE_NAO_DECLARADA, and de-underscoring that
       produced 'fonte.nao.declarada', which is not a host: it is the analyst's
       Portuguese note wearing dots. It reached the Sources screen and only the
       browser saw it.

           UNA REGOLA CHE VALE QUASI SEMPRE DEVE DIRE DOVE NON VALE.

       So the derivation is accepted only when the result looks like a domain —
       a label, a dot and a real top-level domain — and the last label is not a
       Portuguese word. Otherwise the source keeps no name at all, which the
       state beside it already says. */
    if (!/^[a-z0-9][a-z0-9.-]*\.[a-z]{2,}$/.test(host)) return null;
    if (/\.(declarada|desconhecida|ausente|indefinida)$/.test(host)) return null;
    return host;
  };

  /* ── THE SOURCE NAME WAS THE ONE FIELD WITHOUT A LANGUAGE GATE ───────────
     Every narrative field on a source is read through narrative() / v21Text(),
     so an untranslated working note comes back as a STATE and never as prose.
     NAME was read with v21S() and handed to the screen unexamined, on the
     reasoning that a name is a proper noun and a proper noun is not translated.

     Measured on this package, that reasoning was wrong 66 times out of 188.
     The analyst wrote the research note where the name goes:

       «Macfrut — site oficial»
       «Ministero della Salute — Banca dati dei prodotti fitosanitari (busca publica)»
       «Il Risicoltore — mensal do Ente Nazionale Risi»
       «Portal institucional ISMEA. Passou de 404 para 200 com a VPN. ...»

     and it rendered verbatim, in BOTH languages, on five screens — the Fonti
     list, the source detail title and its uppercased breadcrumb, the source
     list of an opportunity case, the Future-Radar signal cards and the FONTI
     group of the global search — because all of them read this one field.

         UN NOME PROPRIO NON SI TRADUCE.
         MA UNA NOTA DI RICERCA NON E UN NOME PROPRIO.

     The ingest already withholds the notes its own marker list recognised
     (NAME__PT_ONLY, 28 rows). This is the same law, applied where the model
     can enforce it without waiting for the package to be rebuilt — and it is
     deliberately a SECOND line, not a replacement: if a future package gates
     the field upstream, this gate simply stops finding anything.

     Portuguese only. A token that is also ordinary Italian is excluded and
     named below, for the reason lang.mjs gives for «mais», «per» and «epoca»:
     a marker that accuses correct Italian teaches the reader to ignore the
     detector. Verified against every Italian string this package ships. */
  const NAME_PT_TOKENS = [
    'busca', 'publica', 'oficial', 'nacional', 'mensal', 'semanal',
    'institucional', 'passou', 'devolve', 'jeito', 'raspar', 'majoritariamente',
    'financiamento', 'grupo', 'beterraba', 'setores', 'servico', 'informacao',
    'aplicacao', 'fichas', 'paginas', 'artigos', 'noticias', 'boletim',
    'boletins', 'producao', 'estacoes', 'relatorio', 'relatorios', 'pesquisa',
    'cobertura', 'comunicado', 'comunicados', 'edicao', 'verao', 'levantamento',
    'pomares', 'resolucao', 'fitossanitario', 'fitossanitarios', 'rede',
    'seccao', 'configuracao', 'desconhecida', 'desconhecido', 'entidades',
    'conjuntura', 'trimestral', 'regiao', 'vindima', 'agronomos', 'caminho',
    'repositorio', 'programa', 'atas', 'confirmei', 'confirmado', 'sugerido',
    'anexos', 'baixam', 'aviso do', 'listar', 'antiga', 'antigo',
    /* Collocations. Each word on its own could be Italian or English; the pair
       cannot. «do site» alone would accuse the English «to do site surveys»,
       so it never travels without its Portuguese partner. */
    'mapa do site', 'sitemap oficial', 'do site italiano', 'de eventos',
    'de passagem', 'fichas de produto', 'pagina indice', 'indice do',
    'calendario do', 'cobertura do', 'site do', 'mensal do', 'todos os',
    'lista os', 'lista as', 'e o equivalente', 'seria o', 'area de',
    'rota antiga',
    /* Accented forms. Each is Portuguese on its own — the unaccented Italian
       twin («pagina», «catalogo», «regione», «credito») is NOT in this list. */
    'servi\u00e7o', 'informa\u00e7\u00e3o', 'aplica\u00e7\u00e3o', 'p\u00e1gina', 'p\u00e1ginas',
    'not\u00edcias', 'produ\u00e7\u00e3o', 'esta\u00e7\u00f5es', 'relat\u00f3rios', 'edi\u00e7\u00e3o',
    'ver\u00e3o', 'resolu\u00e7\u00e3o', 'fitossanit\u00e1rios', 'sec\u00e7\u00e3o',
    'configura\u00e7\u00e3o', 'cat\u00e1logo', 'regi\u00e3o', 'pre\u00e7o', 'cr\u00e9dito',
    'n\u00e3o', 's\u00e3o', 'ent\u00e3o',
  ];
  /* ESCLUSI DI PROPOSITO, e detti qui perche una regola che vale quasi sempre
     deve dire dove non vale: «credito», «superficie», «rendimento», «pagina»,
     «catalogo», «preco» (accusa l italiano «precoce»), «pera», «pasta»,
     «ultimo», «alternativo», «principal» e «temporal» sono parole italiane
     normali, o comparivano dentro nomi italiani corretti di questo stesso
     pacchetto. Misurato: aggiungerle avrebbe cancellato nomi giusti. Le forme
     accentate o plurali portoghesi qui sopra coprono gli stessi record senza
     accusare l italiano. */
  const NAME_PT_RE = new RegExp(
    '(^|[^\\p{L}])(' + NAME_PT_TOKENS.map((t) => t.replace(/ /g, '\\s+')).join('|') + ')([^\\p{L}]|$)',
    'iu',
  );
  /* A NAME IS A NOUN PHRASE. A NOTE IS A SENTENCE.
     Language alone does not catch «VALLE D'AOSTA. Pagina 'Avvisi fitosanitari
     per frutticoltori'.» — correct Italian, and still the analyst's note about
     a page rather than the name of a source. What separates the two is not
     vocabulary but SHAPE: a note runs to a full stop and starts again.
     Measured over the 188 shipped names, this rule fires on no correct name,
     including the longest ones («Agenzia Veneta per l'Innovazione nel Settore
     Primario (Veneto Agricoltura) – Bollettino colture erbacee», 103 chars).

     A DIGIT AFTER THE FULL STOP DOES NOT START A SENTENCE. Requiring an
     uppercase LETTER is not a detail: «Allegato A (DDG n. 1613 de 10/03/2026)»
     is an act number, and a version of this rule that accepted «n. 1» as a
     sentence break blanked that correct Italian name. Measured, then fixed. */
  const NAME_IS_PROSE = (t) => /[.!?]\s+\p{Lu}/u.test(t) || (/[.!?]\s*$/.test(t) && t.length > 55);
  /**
   * The NAME a screen is allowed to print, or null.
   * null is not a missing value: it is the measured statement that the upstream
   * text is a research note, and the caller answers it with the key-derived
   * host — the same fallback the withheld-name rows have always used.
   */
  const showableSourceName = (v) => {
    const t = v21S(v);
    if (!t) return null;
    if (NAME_PT_RE.test(t) || NAME_IS_PROSE(t)) return null;
    return t;
  };

  const cropOfId = (id) => CROP_BY_ID[U(id)] || null;
  const cropsOfIds = (ids) => uniq(A(ids).map(cropOfId));
  const cropScopeOfIds = (ids) => {
    const list = A(ids);
    if (!list.length) return 'NOT_OBSERVED';
    if (cropsOfIds(list).length) return cropsOfIds(list).length > 1 ? 'MULTI' : 'RESOLVED';
    return list.some((x) => CROP_ID_GENERIC[U(x)]) ? 'GENERIC_TERM' : 'UNMAPPED';
  };
  const regionOfId = (id) => REGION_BY_ID[U(id)] || null;
  const regionsOfIds = (ids) => uniq(A(ids).map(regionOfId));
  const issueOfId = (id) => ISSUE_BY_ID[U(id)] || null;
  const issuesOfIds = (ids) => A(ids).map(issueOfId).filter(Boolean);

  /* The §8 envelope every V2.1 record carries. Read once, here, so no family
     adapter has to remember the twelve field names. */
  const v21Env = (r, prov) => ({
    qaStatus: S(r.QA_STATUS),
    clientSafe: r.CLIENT_SAFE === true,
    /* LA REGOLA DEL PACCHETTO, IN UN CAMPO SOLO.
       README-FIRST §3, testuale:

           CLIENT_SAFE = true   -> puo sostenere un'affermazione visibile
           CLIENT_SAFE = false  -> vive nel corpus, compare come RESEARCH_LEADS,
                                   e NON sostiene MAI un'affermazione da solo

       Non e «nascondere»: il record resta. E il divieto di farlo CHIUDERE una
       risposta. Il portale legge `publishable`; `clientSafe` e il timbro
       interno e non deve comparire in nessuna schermata. */
    publishable: r.CLIENT_SAFE === true,
    evidenceStatus: S(r.EVIDENCE_STATUS),
    originLayer: S(r.ORIGIN_LAYER),
    sourceIds: A(r.SOURCE_IDS),
    sourceUrls: A(r.SOURCE_URLS),
    cropIds: A(r.CROP_IDS),
    issueIds: A(r.ISSUE_IDS),
    regionIds: A(r.REGION_IDS),
    cropKeys: cropsOfIds(r.CROP_IDS),
    regionKeys: regionsOfIds(r.REGION_IDS),
    geoScope: S(r.GEOGRAPHIC_SCOPE),
    provenance: prov || P.CANONICAL,
    raw: r,
  });

  /* A localized pair the ingest already gated. `__PT_ONLY` is the ingest saying
     "the source wrote this and there is no approved version" — the same third
     state narrative() has always had, arriving as a flag instead of as the
     Portuguese text it stands for. */
  const v21Text = (r, base) => {
    const it = S(r[base + '_IT']), en = S(r[base + '_EN']);
    if (it || en) return { state: KNOWLEDGE.CLEAR, it: it || en, en: en || it };
    if (r[base + '__PT_ONLY']) return { state: KNOWLEDGE.NOT_APPROVED_FOR_DISPLAY, it: null, en: null };
    return { state: KNOWLEDGE.NOT_ESTABLISHED, it: null, en: null };
  };
  /* NOT_ESTABLISHED is the ingest's canonical spelling of the upstream's nine
     ways of writing "não sei". A view asks for a value and gets null, exactly
     as it did when the sentinel arrived as Portuguese prose. */
  const v21S = (v) => { const t = S(v); return t && t !== 'NOT_ESTABLISHED' ? t : null; };
  const v21Known = (v) => S(v) === 'NOT_ESTABLISHED' ? KNOWLEDGE.NOT_ESTABLISHED : (S(v) ? KNOWLEDGE.CLEAR : KNOWLEDGE.NOT_ESTABLISHED);

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
  /* ══ PERCHE ADAMA DEVE INTERESSARSI ═══════════════════════════════════════
     Una scheda che non risponde a questa domanda non e un'opportunita: e una
     notizia agricola. La risposta non si inventa — l'ARCHETIPO e la
     dichiarazione che il motore fa su PERCHE il caso esiste, e le aree che
     instrada dicono chi ne porta la conseguenza.

         INTERESSANTE PER L'AGRICOLTURA != OPPORTUNITA PER ADAMA.

     Misurato sui 37: ognuno ha almeno una conseguenza dichiarata, quindi oggi
     nessun caso va tolto dal radar. La regola resta scritta lo stesso, perche
     il giorno in cui un caso non l'avra si dovra vedere. */
  const RELEVANCE_LABEL = {
    PRODUCT_OPPORTUNITY: ['Opportunita di prodotto', 'Product opportunity'],
    DEVELOPMENT_MARKET_OPPORTUNITY: ['Sviluppo di mercato', 'Market development'],
    PORTFOLIO_GAP: ['Lacuna di portafoglio', 'Portfolio gap'],
    REGULATORY_IMPACT: ['Impatto normativo', 'Regulatory impact'],
    SUPPLY_PREPARATION: ['Preparazione approvvigionamento', 'Supply preparation'],
    MARKETING_COMPETITIVE_RESPONSE: ['Risposta competitiva', 'Competitive response'],
    SCIENCE_TECHNICAL_PREPARATION: ['Preparazione tecnica', 'Technical preparation'],
    VALIDATION_REQUIRED: ['Da validare', 'Validation required'],
  };
  /* Il MOTIVO, in una frase, e derivato dallo stesso fatto della classe: non e
     una seconda opinione, e la stessa detta a parole. */
  const RELEVANCE_WHY = {
    PRODUCT_OPPORTUNITY: ['un prodotto ADAMA ha una corrispondenza verificata su etichetta per questo caso',
      'an ADAMA product has a verified label match for this case'],
    DEVELOPMENT_MARKET_OPPORTUNITY: ['il caso apre una coppia coltura x bersaglio da investigare o posizionare',
      'the case opens a crop x target pair to investigate or position'],
    PORTFOLIO_GAP: ['il portafoglio e coinvolto ma nessun legame di etichetta e confermato in questa lettura',
      'the portfolio is involved but no label link is confirmed in this reading'],
    REGULATORY_IMPACT: ['una scadenza o un cambiamento normativo tocca questo caso',
      'a regulatory deadline or change touches this case'],
    SUPPLY_PREPARATION: ['il motore instrada Approvvigionamento: c\'e una preparazione da valutare',
      'the engine routes Supply: there is a preparation to assess'],
    MARKETING_COMPETITIVE_RESPONSE: ['un movimento di comunicazione della concorrenza chiede una lettura',
      'a competitor communication movement asks for a reading'],
    SCIENCE_TECHNICAL_PREPARATION: ['esiste evidenza scientifica o di resistenza da validare prima di agire',
      'there is scientific or resistance evidence to validate before acting'],
    VALIDATION_REQUIRED: ['il caso e rilevato ma nessuna conseguenza e ancora sostenuta',
      'the case is detected but no consequence is supported yet'],
  };
  /* ── LA PORTATA GEOGRAFICA, DETTA UNA VOLTA SOLA ────────────────────────
     La scheda e il dettaglio derivavano ognuno la propria frase, e dicevano la
     stessa cosa con parole diverse: tredici casi in cui le due schermate non
     coincidevano su DOVE.

         DUE DERIVAZIONI DELLA STESSA COSA SONO DUE COSE. */
  const geographyLabel = (o, lang) => {
    if (!o) return '';
    const en = lang === 'en';
    const named = (o.regionKeys && o.regionKeys.length ? o.regionKeys.join(' · ') : null) || o.region;
    if (named) return named;
    if (o.geoScope === 'NATIONAL') return en ? 'Italy · national scope' : 'Italia · portata nazionale';
    if (o.geoScope === 'EUROPEAN') return en ? 'European Union · European scope' : 'Unione Europea · portata europea';
    return '';
  };

  const adamaRelevance = (o) => {
    if (!o) return [];
    const links = Array.isArray(o.productLinks) ? o.productLinks : [];
    const verified = links.filter((l) => l && l.strength === 'VERIFIED_LABEL_MATCH').length;
    const areas = Array.isArray(o.actionMap) ? o.actionMap : [];
    const a = o.archetype;
    const out = [];
    const add = (k) => { if (out.indexOf(k) < 0) out.push(k); };
    if (a === 'O5_REGULATORY_PREPARATION') add('REGULATORY_IMPACT');
    if (a === 'O4_COMPETITIVE_OPENING') add('MARKETING_COMPETITIVE_RESPONSE');
    if (a === 'O3_RESISTANCE_MOA' || a === 'O6_SCIENCE_TO_FIELD') add('SCIENCE_TECHNICAL_PREPARATION');
    if (a === 'O2_MARKET_MOMENT') add('DEVELOPMENT_MARKET_OPPORTUNITY');
    if (a === 'O1_FIELD_PRESSURE') add(verified ? 'PRODUCT_OPPORTUNITY' : 'DEVELOPMENT_MARKET_OPPORTUNITY');
    if (areas.indexOf('SUPPLY') >= 0) add('SUPPLY_PREPARATION');
    if (areas.indexOf('PORTFOLIO') >= 0 && !verified) add('PORTFOLIO_GAP');
    if (verified) add('PRODUCT_OPPORTUNITY');
    if (!out.length) add('VALIDATION_REQUIRED');
    return out;
  };

  /* ══ INTERNO UTILE != PRONTO PER IL CANALE ════════════════════════════════
     Un caso puo valere molto dentro ADAMA e non poter uscire su un foglio che
     un rivenditore mette in mano a un agricoltore. Le due cose hanno due nomi
     e due prove diverse.

         UN CASO CHE SERVE DENTRO NON E, PER QUESTO, UN MATERIALE DI CAMPO.

     Per RTV si esige cio che un foglio di campo afferma implicitamente: che
     esiste un prodotto con legame VERIFICATO, che coltura e bersaglio sono
     nominati, e che il momento e sostenuto. Misurato: 3 su 37 passano — e i
     motivi dei 34 bloccati sono dichiarati uno per uno, non nascosti. */
  /* ── CHI PUO USCIRE DI CASA ────────────────────────────────────────────
     VENDERE E UNA DECISIONE INTERNA. INVIARE E UN'AFFERMAZIONE PUBBLICA.

     Il verdetto del MOTORE vince quando c'e: lui vede il catalogo pubblico, la
     frase che la fonte ha scritto e i portoni di evidenza, e la scheda no. Il
     righello locale qui sotto resta la RISERVA — per il caso che il motore non
     ha giudicato — e non e stato cancellato perche cancellarlo lascerebbe senza
     risposta ogni scheda che non venga dal pacchetto V2.1.

         UN RIGHELLO DUPLICATO SONO DUE RIGHELLI CHE DIVERGERANNO:
         QUI UNO DECIDE E L'ALTRO ASPETTA. */
  const rtvEligibility = (o) => {
    if (!o) return { ready: false, blockers: ['nessun caso'], from: 'NONE' };
    const raw = o.raw || o;
    const verdict = raw.externalMaterialReady || o.externalMaterialReady;
    if (verdict) {
      const codes = (raw.externalBlockerCodes || o.externalBlockerCodes || []).slice();
      return {
        ready: verdict === 'YES',
        blockers: verdict === 'YES' ? [] : (codes.length ? codes : ['NOT_SALES_READY']),
        from: 'ENGINE'
      };
    }
    const blockers = [];
    const links = Array.isArray(o.productLinks) ? o.productLinks : [];
    if (!links.filter((l) => l && l.strength === 'VERIFIED_LABEL_MATCH').length) blockers.push('NO_VERIFIED_PRODUCT');
    if (!((o.cropKeys || [])[0] || o.crop)) blockers.push('NO_CROP');
    if (!(o.issue || o.issueEn)) blockers.push('NO_TARGET');
    if (!(o.windowStart || o.windowEnd || o.windowState)) blockers.push('NO_WINDOW');
    return { ready: blockers.length === 0, blockers, from: 'SCREEN' };
  };
  const RTV_BLOCKER_LABEL = {
    NO_VERIFIED_PRODUCT: ['nessun prodotto con legame verificato su etichetta', 'no product with a verified label link'],
    NO_CROP: ['la coltura non e risolta', 'the crop is not resolved'],
    NO_TARGET: ['nessun bersaglio agronomico nominato', 'no agronomic target is named'],
    NO_WINDOW: ['nessuna finestra sostenuta', 'no supported window'],
    /* I sei del motore. Le frasi vivono di qua dalla frontiera: oltre passano
       solo i codici, perche il pacchetto V2.1 e stato ricercato in portoghese. */
    NOT_SALES_READY: ['il caso non e commercialmente pronto nemmeno all\u2019interno', 'the case is not commercially ready even internally'],
    EVIDENCE_GATE_OPEN: ['c\u2019e un portone di evidenza aperto sulla stessa affermazione', 'an evidence gate is open on the same claim'],
    RED_TEAM_FINDING: ['il red team ha registrato un\u2019estrapolazione in questo caso', 'the red team recorded an extrapolation on this case'],
    CATALOG_DOES_NOT_DECLARE_CROP: ['l\u2019etichetta copre la coppia, ma la pagina di catalogo del prodotto non dichiara questa coltura', 'the label covers the pair, but the product catalogue page does not declare this crop'],
    WINDOW_IS_ADMINISTRATIVE: ['la finestra mostrata e data di atto, non finestra di applicazione', 'the window shown is an act date, not an application window'],
    NO_SOURCE_SENTENCE: ['non c\u2019e frase della fonte che sostenga la necessita', 'there is no source sentence supporting the need'],
    SOURCE_PRESCRIBES_OTHER_MEANS: ['il bollettino prescrive sostanze nominate, e quella del prodotto ADAMA non e fra loro', 'the bulletin prescribes named substances, and the ADAMA product\u2019s is not among them'],
  };

  /* ── LA CATEGORIA QUANDO ISSUE_TYPE TACE ────────────────────────────────
     ISSUE_TYPE e null su TUTTI E 37 i casi del motore V2.1, quindi categoryOf()
     rispondeva `unknown` trentasette volte e ogni scheda usciva con il gettone
     neutro: marrone, senza linea, senza categoria leggibile a colpo d'occhio.

         UNA SCHEDA SENZA COLORE NON E UNA SCHEDA PRUDENTE.
         E UNA SCHEDA CHE NON HA GUARDATO DOVE IL DATO ERA.

     Il dato c'e, e non e una somiglianza: la CATEGORIA COMMERCIALE del prodotto
     e un fatto del registro fitosanitario, e il manuale assegna a ciascuna la
     propria linea. Un caso i cui prodotti collegati sono TUTTI fungicidi e un
     contesto Disease Control — non per analogia, per dichiarazione.

     Tre guardie, e sono la ragione per cui questo non e un'inferenza:
       · ISSUE_TYPE, quando c'e, vince sempre — questa e solo una riserva;
       · se le categorie dei prodotti NON concordano, resta neutro (1 caso);
       · se nessun prodotto dichiara categoria, resta neutro (16 casi).
     Misurato: 20 casi su 37 recuperano cosi la propria linea. */
  const CAT_BY_PRODUCT_CATEGORY = {
    ERBICIDI: 'weed',        /* Weed Control    · verde  */
    FUNGICIDI: 'disease',    /* Disease Control · blu    */
    INSETTICIDI: 'pest',     /* Pest Control    · viola  */
  };
  const categoryFromProducts = (links, findProductFn) => {
    if (!Array.isArray(links) || !links.length || typeof findProductFn !== 'function') return null;
    const cats = [];
    for (const l of links) {
      const p = findProductFn(l && (l.name || l.product));
      const k = p && CAT_BY_PRODUCT_CATEGORY[String(p.category || '').toUpperCase()];
      if (k && cats.indexOf(k) < 0) cats.push(k);
    }
    /* Una sola categoria dichiarata e una risposta. Due sono una domanda. */
    return cats.length === 1 ? cats[0] : null;
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
    '#00698F': '#fff', '#8F8886': '#fff', '#3A3533': '#fff', '#1C1817': '#fff',
  };
  const inkOn = (fill) => INK[String(fill || '').trim()] || '#fff';

  /* Status tokens. ACT_NOW has a colour but is never DERIVED here: §7 leaves the
     agronomic state to upstream's CURRENT_STATUS. DEFAULT exists so an unknown
     code cannot throw. */
  const STATUS_UI = {
    WINDOW_OPEN: { color: '#00783F', text: '#00B152', rank: 1 },
    WINDOW_CLOSED: { color: '#8F8886', text: '#8F8886', rank: 6 },
    NEXT_CYCLE: { color: '#8F8886', text: '#8F8886', rank: 5 },
    DATE_UNKNOWN: { color: '#6E6663', text: '#B1A9A7', rank: 4 },
    ACT_NOW: { color: '#00783F', text: '#00B152', rank: 0 },
    DEFAULT: { color: '#6E6663', text: '#B1A9A7', rank: 9 },
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
  /* The V2.1 id vocabulary names five crops that have NO canonical window in
     this package — Peach, Kiwi, Pear, Citrus, Sunflower. They are real crops
     and the resolver has to know them, or a card carrying one prints a crop the
     model then calls unresolved. Adding them here is an IDENTITY (each name
     resolves to itself), not a new window and not a new mapping: cropWindows
     still has 29, and a crop without a window remains a fact about the package
     rather than a gap to be filled. */
  Object.keys(CROP_BY_ID).forEach((k) => { CROP_BY_CANON[U(CROP_BY_ID[k])] = CROP_BY_ID[k]; });
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
  const currentFieldSignals = build('currentFieldSignals', [
    V21('currentFieldSignals', (c) => Object.assign(v21Env(c), {
      id: c.ID,
      crop: v21S(c.CROP), cropCanonical: cropsOfIds(c.CROP_IDS)[0] || cropResolve(c.CROP).key,
      region: v21S(c.REGION),
      issue: issueResolve(c.ISSUE).it, issueEn: issueResolve(c.ISSUE).en, issueRaw: v21S(c.ISSUE),
      expectedCycle: v21Text(c, 'EXPECTED_CYCLE'),
      observedStage: v21Text(c, 'OBSERVED_STAGE'),
      fieldReportedStage: v21Text(c, 'FIELD_REPORTED_STAGE'),
      regulatoryWindow: v21Text(c, 'REGULATORY_WINDOW'),
      regulatoryAct: v21S(c.REGULATORY_ACT),
      regulatoryActState: v21S(c.REGULATORY_ACT_STATE),
      monitoringWindow: v21Text(c, 'MONITORING_WINDOW'),
      applicationWindow2026: v21Text(c, 'APPLICATION_WINDOW_2026'),
      nextImportantWindow: v21Text(c, 'NEXT_IMPORTANT_WINDOW'),
      preparationWindow: v21Text(c, 'PREPARATION_WINDOW'),
      adamaProductsNote: v21Text(c, 'ADAMA_PRODUCTS_NOTE'),
      notProves: v21Text(c, 'WHAT_IT_DOES_NOT_PROVE'),
      coverageState: v21S(c.COVERAGE_STATE),
      /* The fixture had to declare PT_ANALYST_SOURCE because its prose was
         Portuguese. The V2.1 rows reach here already gated: what is present is
         approved in both languages, what is not is a state. */
      languageState: 'APPROVED_OR_WITHHELD',
      sourceId: v21S(c.SOURCE_ID),
    }), (r) => (!r.id ? 'no ID' : null)),
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
    /* QUI NON C'E UN GANCIO V2.1, E L'ASSENZA E LA REGOLA.
       Ogni altra famiglia interroga il pacchetto per prima. Questa no, perche
       il pacchetto NON contiene le finestre agronomiche: contiene un file che
       si chiama CROP-WINDOWS.json e che porta le sette letture per coltura x
       avversita (IT-WIN-001..007), le stesse che alimentano
       currentFieldSignals. Le 29 finestre auditate vivono nel contratto
       canonico e in nessun altro posto.

       Il gancio c'era, con l'adattatore identita e senza validazione. Non ha
       mai sostituito nulla solo perche oggi il pacchetto non pubblica quella
       chiave — cioe per una coincidenza, non per una decisione. Il giorno in
       cui un build a monte la pubblicasse, sette righe in forma V2.1 avrebbero
       preso il posto di ventinove finestre normalizzate, e le schermate
       avrebbero mostrato `undefined` al posto delle date.

           UNA PROTEZIONE CHE FUNZIONA PER COINCIDENZA
           NON E UNA PROTEZIONE: E UN RITARDO.

       Togliere il gancio rende la separazione strutturale. Se un giorno il
       pacchetto avesse davvero le finestre canoniche, si aggiunge qui un
       candidato CON il suo adattatore — deliberatamente, non per il nome del
       file. Il controllo W1 misura che questo resti vero. */
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
    /* LABEL REACH, REMEASURED — not copied.

       The fixture published 17 pre-computed rows saying how many products
       mention each crop. The V2.1 package does not ship that table, and it does
       not need to: it ships the 2.030 label pairs the table was a summary OF.
       Counting them here is arithmetic over real rows, which is what
       REAL_DERIVED means; carrying the fixture's 17 forward would have been the
       last factual number in the portal still coming from a fixture.

           A SUMMARY THAT CAN BE RECOUNTED FROM THE ROWS
           SHOULD BE RECOUNTED FROM THE ROWS.

       Measured on this package: 35 crops, which is the crop vocabulary of the
       label corpus itself — not a list anybody typed. */
    (() => {
      const pairs = A(RAW.HANDOFF_V21 && RAW.HANDOFF_V21.productRelationships);
      if (!pairs.length) return null;
      const byCrop = {};
      pairs.forEach((r) => {
        const k = S(r.CROP_ON_LABEL);
        if (!k) return;
        const b = byCrop[k] = byCrop[k] || { crop: k, products: {}, useRows: 0, verified: 0, cropIds: {} };
        if (S(r.PRODUCT_NAME)) b.products[U(r.PRODUCT_NAME)] = 1;
        b.useRows += 1;
        if (V21_LINK_STRENGTH[U(r.LINK_STRENGTH)] === 'VERIFIED_LABEL_MATCH') b.verified += 1;
        A(r.CROP_IDS).forEach((c) => { b.cropIds[c] = 1; });
      });
      return {
        source: 'HANDOFF_V21 · productRelationships · recounted',
        precedence: P.REAL_DERIVED,
        rows: Object.keys(byCrop).sort().map((k) => byCrop[k]),
        adapt: (b) => ({
          id: 'CEW-' + U(b.crop).replace(/[^A-Z0-9]+/g, '-'),
          crop: cropsOfIds(Object.keys(b.cropIds))[0] || b.crop,
          cropOnLabel: b.crop,
          cropKeys: cropsOfIds(Object.keys(b.cropIds)),
          productsMentioning: Object.keys(b.products).length,
          productsWithUseRow: Object.keys(b.products).length,
          useRows: b.useRows, verifiedRows: b.verified,
          /* The fixture's `distance` and `reading` were an editorial gloss on
             the same two numbers. They are not re-invented: a view that wants
             to rank crops has the counts. */
          distance: null, reading: null,
          provenance: P.REAL_DERIVED, raw: b,
        }),
        validate: (r) => (!r.crop ? 'no crop term' : null),
      };
    })(),
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
    V21('productsRegulatory', (p) => Object.assign(v21Env(p), {
      id: p.ID, name: v21S(p.NAME), reg: v21S(p.REGISTRATION_NUMBER),
      holder: v21S(p.AUTHORIZATION_HOLDER), ai: A(p.ACTIVE_INGREDIENTS),
      form: v21S(p.FORMULATION), regCat: v21S(p.REGULATORY_CATEGORY),
      line: v21S(p.LINE), status: v21S(p.STATUS), expiry: v21S(p.EXPIRY),
      /* The registry declares a mode of action as free text; the structured
         HRAC/FRAC/IRAC codes are the active-ingredient layer's job and are
         joined there, not guessed from a sentence here. */
      /* The registry declares the mode of action as a STRUCTURE
         ({ HRAC: ['5'] }), not as a sentence. Passing it straight through put
         the literal '[object Object]' on the action brief. moaLabelOf is the
         same formatter the use rows already use, so the two screens spell a
         mode of action the same way. */
      moaDeclared: moaLabelOf(p.MODE_OF_ACTION_DECLARED),
      moaDeclaredCodes: p.MODE_OF_ACTION_DECLARED || null,
      hrac: [], frac: [], irac: [],
      crops: cropsOfIds(p.CROP_IDS), targets: issuesOfIds(p.ISSUE_IDS).map((i) => i.it),
      labelUrl: v21S(p.LABEL_URL),
      catalogUrl: null,
      catalogCat: null,
      inPublicCatalog: p.IN_PUBLIC_CATALOG_FLAG === true,
      expiresInDays: daysFrom(v21S(p.EXPIRY)),
      evidenceWhy: v21Text(p, 'EVIDENCE_STATUS_WHY'),
    }), (r) => (!r.name ? 'no product name' : null)),
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
    V21('productsCommercial', (p) => Object.assign(v21Env(p), {
      id: p.ID, name: v21S(p.NAME), category: v21S(p.CATEGORY),
      categorySource: v21S(p.CATEGORY_SOURCE),
      /* The catalog and the registry are two universes (§ the catalog law). The
         match state is the package's own verdict and is never upgraded here. */
      matchState: v21S(p.MATCHED_REGULATORY_ID) ? 'REGULATORY_MATCH_CONFIRMED' : 'REGULATORY_MATCH_NOT_FOUND',
      regId: v21S(p.MATCHED_REGULATORY_ID), reg: v21S(p.REGISTRATION_NUMBER_ON_PAGE),
      holder: v21S(p.AUTHORIZATION_HOLDER), holderIsAdama: p.HOLDER_IS_ADAMA,
      ai: A(p.ACTIVE_INGREDIENTS), line: null,
      status: v21S(p.CATALOG_STATUS), expiry: null,
      catalogUrl: v21S(p.PUBLIC_CATALOG_URL),
      cropsDeclared: A(p.CROPS_DECLARED_ON_SITE),
      /* Two records in this catalog are not plant protection products and one
         is a system rather than a product. The flags travel so no portfolio
         count can quietly include them. */
      notAPlantProtectionProduct: p.NOT_A_PLANT_PROTECTION_PRODUCT === true,
      isSystemNotProduct: p.IS_SYSTEM_NOT_PRODUCT === true,
      commercialContract: v21S(p.COMMERCIAL_CONTRACT),
      note: null,
      contractWhy: v21Text(p, 'COMMERCIAL_CONTRACT_WHY'),
    }), (r) => (!r.name ? 'no product name' : null)),
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
  A(RAW.IG.LINKS).forEach((l) => {
    const crop = cropFromCode(l.crop) || S(l.cropTerm) || S(l.crop);
    pushRel(crop, l.target, l.product, 'RELATED_PORTFOLIO', 'Separate declarations on the label, brought together by us', l.labelUrl, {
      evidenceKind: 'REGULATORY_USE_ROW',
      target: S(l.target), reg: S(l.reg), labelUrl: S(l.labelUrl),
      moaLabel: moaLabelOf(l.moa),
      mappingRule: 'CROP_KEY:' + U(l.crop),
      provenance: P.REAL_SOURCE,
    });
  });
  /* THE 2.030 LABEL-USE PAIRS, WHEN THE PACKAGE SUPPLIES THEM.

     The audit read 163 labels and published 236 relationships. The V2.1 label
     reader read the same labels and published 2.030 crop x target pairs, each
     carrying the sentence from the label that joins them. That is not the same
     table measured better: it is the difference between a verdict list and the
     document's own use table.

     The three link strengths are the package's own, and they map onto the two
     the portal already renders WITHOUT loosening either:

       LINHA_DA_TABELA    crop and target on the SAME ROW      -> VERIFIED_LABEL_MATCH
       BLOCO_DA_CULTURA   target inside the crop's block       -> VERIFIED_LABEL_MATCH
       DECLARACAO_DE_PRODUTO  two separate lists, joined by us -> RELATED_PORTFOLIO

     The first two are the DOCUMENT joining crop and target; the third is us
     approximating. Measured, the split is 886 + 626 = 1.512 against the
     package's own COUNT_CLIENT_SAFE of 1.512, and the 518 approximations are
     exactly the rows the package marks CLIENT_SAFE=false. The mapping is not a
     judgement — it is the package's law restated in the portal's vocabulary. */
  const productRelationships = build('productRelationships', [
    V21('productRelationships', (r) => {
      const strength = V21_LINK_STRENGTH[U(r.LINK_STRENGTH)] || 'LABEL_CHECK_NEEDED';
      const crop = cropsOfIds(r.CROP_IDS)[0] || null;
      const issue = issueOfId(A(r.ISSUE_IDS)[0]);
      /* The crop and target AS THE LABEL WRITES THEM stay beside the canonical
         resolution. A label that says 'MAIS_DOLCE' is not the same fact as the
         canonical Maize, and the row has to be able to show both. */
      const w = crop && issue ? windowFor(crop, issue.it) : null;
      return Object.assign(v21Env(r), {
        id: r.ID,
        crop, cropOnLabel: v21S(r.CROP_ON_LABEL),
        issue: issue ? issue.it : null, issueEn: issue ? issue.en : null,
        target: v21S(r.TARGET_ON_LABEL),
        targetAsWritten: v21S(r.TARGET_AS_WRITTEN),
        targetKind: v21S(r.TARGET_KIND), weedGroup: v21S(r.WEED_GROUP),
        product: v21S(r.PRODUCT_NAME), productKey: U(r.PRODUCT_NAME),
        reg: v21S(r.REGISTRATION_NUMBER),
        strength, strengthRank: STRENGTH[strength].rank,
        linkStrengthRaw: v21S(r.LINK_STRENGTH),
        /* The label's own sentence, quoted. It is the evidence, so it is never
           translated and never parsed for another fact. */
        quote: v21S(r.QUOTE_FROM_LABEL),
        evidence: null,
        evidenceKind: 'LABEL_USE_ROW',
        linkMeans: v21Text(r, 'LINK_MEANS'),
        notProves: v21Text(r, 'WHAT_IT_DOES_NOT_PROVE'),
        source: null, labelUrl: A(r.SOURCE_URLS)[0] || null,
        windowId: w ? w.windowId : null,
        legacyCaseId: w ? w.legacyCaseId : null,
        region: w ? w.region : null,
        issueType: w ? w.issueType : null,
        anchor: w ? 'CANONICAL_WINDOW' : 'NO_CANONICAL_WINDOW',
        auditDate: null, auditSource: null,
        absenceRule: ABSENCE_RULE_TEXT,
        moaLabel: null, mappingRule: null,
      });
    }, (r) => (!r.product ? 'no product' : null)),
    {
      source: 'ITALY_LABEL_VERDICTS + ITALY_INGEST.LINKS',
      precedence: P.CANONICAL,
      rows: relRows,
      adapt: (r) => r,
    },
  ], 'product relationships read from official labels; the demo case fixture is not a source');

  /* ---- REGULATORY LINKS · the 219 authorised use rows -------------------
     The only fully-populated relationship table in the package, and the model
     never exposed it. It is a DIFFERENT fact from 'positions assessed by the
     audit' (19) and from 'verified matches' (12); a screen that shows this
     count must say 'righe d'uso lette dalle etichette', not 'links'.

     Its timing column is the analyst's unknown sentence on 219/219 rows, so it
     is routed through the same guard as any other prose: an unread label column
     must render as unknown, never as an application window. */
  /* LA LETTURA PIU PROFONDA DEVE POTER RISPONDERE.
     seenRel — la tabella che strengthFor interroga — veniva riempita soltanto
     dai 19 verdetti dell'audit storico e dai 236 collegamenti del registro. Le
     2.030 duplate d'uso lette dal V2.1 non ci entravano mai, quindi
     strengthFor rispondeva «l'audit ha guardato e non ha trovato» su righe che
     la lettura piu completa aveva trovato: il caso OPP_3F736F0A9467 dichiara
     BADGER su Grapevine x Downy mildew, e la riga Grapevine x Peronospora
     esiste, con la stessa avversita scritta nell'altra lingua.

     pushRel rispetta gia la precedenza, quindi un verdetto piu forte resta al
     suo posto: qui non si allenta niente, si smette solo di rispondere con la
     tabella piu piccola. */
  productRelationships.records.forEach((r) => {
    if (!r.product || !r.crop) return;
    const iss = (r.issue && r.issue.it) || r.issue || r.target || null;
    if (!iss) return;
    pushRel(r.crop, iss, r.product, r.strength, r.evidence, r.source, {
      evidenceKind: r.evidenceKind || 'V21_LABEL_USE_PAIR',
      labelUrl: r.labelUrl, provenance: P.CANONICAL,
    });
  });

  const regulatoryLinks = build('regulatoryLinks', [
    /* The authorised use rows. Same 2.030 pairs, read as the registry's use
       table rather than as a portfolio relationship — a DIFFERENT fact from
       'positions assessed by the audit', and the label above has always said
       so. The count moves from 219 to 2.030 because the reader changed, not
       because the registry did. */
    (() => {
      const pairs = A(RAW.HANDOFF_V21 && RAW.HANDOFF_V21.productRelationships);
      if (!pairs.length) return null;
      return {
        source: 'HANDOFF_V21 · productRelationships · use rows',
        precedence: P.CANONICAL,
        rows: pairs,
        adapt: (l) => ({
          id: l.ID,
          crop: cropsOfIds(l.CROP_IDS)[0] || S(l.CROP_ON_LABEL),
          cropCode: U(l.CROP_ON_LABEL),
          cropKey: cropsOfIds(l.CROP_IDS)[0] || null,
          cropKeys: cropsOfIds(l.CROP_IDS),
          target: S(l.TARGET_ON_LABEL), targetAsWritten: S(l.TARGET_AS_WRITTEN),
          targetKind: S(l.TARGET_KIND), weedGroup: S(l.WEED_GROUP),
          product: S(l.PRODUCT_NAME), productKey: U(l.PRODUCT_NAME),
          reg: S(l.REGISTRATION_NUMBER), ai: [], moa: null, moaLabel: null,
          doses: [], interval: null,
          /* The label's application-timing column was not extracted by this
             reading, and the package says so rather than leaving the field to
             look empty. */
          timing: null, timingState: KNOWLEDGE.NOT_ESTABLISHED,
          labelUrl: A(l.SOURCE_URLS)[0] || null,
          quote: S(l.QUOTE_FROM_LABEL),
          evidence: S(l.EVIDENCE_STATUS),
          provenance: P.CANONICAL, raw: l,
        }),
        validate: (r) => (!r.id ? 'no id' : !r.product ? 'no product' : null),
      };
    })(),
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
    /* tallied over cropKeys, not cropKey: a generic Frumento row is authorised
       evidence for both wheat keys and must appear under both. The sum is
       therefore larger than 219 by exactly the number of generic rows, which is
       published as genericRows below rather than left to be discovered. */
    byCrop: tallyBy(regulatoryLinks.records, (r) => (r.cropKeys.length ? r.cropKeys : [r.crop])),
    genericRows: regulatoryLinks.records.filter((r) => r.cropKeys.length > 1).length,
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

  /* Le fonti che SONO il canale proprio di un concorrente. Dichiarate una per
     una: una nota che cita cropscience.bayer.it parla di Bayer perche quello e
     il sito di Bayer, non perche il nome somigli. */
  const NOTE_OWN_CHANNEL = {
    SRC_CROPSCIENCE_BAYER_IT: 'Bayer',
    SRC_AG_FMC_COM: 'FMC',
    SRC_AGRO_BASF_IT: 'BASF',
    SRC_SYNGENTA_IT: 'Syngenta',
    SRC_CORTEVA_IT: 'Corteva',
  };

  /* ---- the joined product entity --------------------------------------- */
  const byName = {};
  /* i marchi che il registro conosce: servono a PNAME_FIX per non riparare
     un nome a intuito. */
  const KNOWN_BRANDS = new Set();
  productsRegulatory.records.forEach((p) => {
    KNOWN_BRANDS.add(PKEY(p.name));
    const first = String(p.name || '').trim().split(/\s+/)[0];
    if (first) KNOWN_BRANDS.add(PKEY(first));
  });
  const addProduct = (name, patch) => {
    const k0 = PKEY(name);
    if (!k0) return;
    /* Se il prodotto e gia entrato con l'ortografia dell'altra fonte, si unisce
       li: e lo stesso prodotto, scritto due volte in modo diverso. */
    const k = byName[k0] ? k0 : (PKEY_ALTS(name).find((a) => byName[a]) || k0);
    byName[k] = Object.assign({ name: String(name).trim(), key: k, regulatory: null, commercial: null, links: [], relationships: [] }, byName[k], patch);
  };
  productsRegulatory.records.forEach((p) => addProduct(p.name, {
    regulatory: p, line: p.line, ai: p.ai, targets: p.targets, crops: p.crops,
    labelUrl: p.labelUrl, status: p.status, expiry: p.expiry,
    holder: p.holder, reg: p.reg, regCat: p.regCat, form: p.form,
    hrac: p.hrac, frac: p.frac, irac: p.irac,
    expiresInDays: p.expiresInDays, provenance: P.REAL_SOURCE,
  }));
  productsCommercial.records.forEach((p) => {
    /* IL TITOLARE DELL'AUTORIZZAZIONE VIAGGIA ANCHE PER I SOLI-CATALOGO.
       Veniva copiato unicamente dal ramo regolatorio, quindi i prodotti che
       esistono solo nel catalogo arrivavano SENZA titolare — e fra questi ci
       sono i sei cui titolare e SYNGENTA, ALBAUGH o MICROCIDE. Senza quel
       campo la schermata non aveva modo di sapere che non erano di ADAMA.
       Non sovrascrive mai il titolare del registro: quello e la fonte piu
       forte, e vince quando c'e. */
    const prev = byName[PKEY(p.name)] || PKEY_ALTS(p.name).map((a) => byName[a]).find(Boolean);
    addProduct(p.name, Object.assign({
      commercial: p, category: p.category, catalogUrl: p.catalogUrl,
      matchState: p.matchState, provenance: P.REAL_SOURCE,
      /* Il nome mostrato resta quello COMMERCIALE — e come il prodotto si
         chiama sul mercato — con il solo segno diventato lettera rimesso a
         posto: NIMRODR torna NIMROD(R). */
      name: PNAME_FIX(p.name, KNOWN_BRANDS),
    }, (prev && prev.holder) ? {} : { holder: p.holder }));
  });
  /* Relationships attach to the product entity from the relationship
     collection — never from a case fixture. The full record is kept beside the
     short link so a product page can show the window and the evidence without
     a second lookup. */
  productRelationships.records.forEach((r) => {
    const e = byName[U(r.product)];
    if (e) {
      e.links.push({ crop: r.crop, issue: r.issue, strength: r.strength, evidence: r.evidence, source: r.source, windowId: r.windowId, region: r.region, evidenceKind: r.evidenceKind, labelUrl: r.labelUrl, caseId: null });
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
      /* CHI E IL TITOLARE, E COSA IL PORTALE PUO DIRNE.
         Il pacchetto e esplicito su questo punto e va citato per intero:
         «il titolare dell'autorizzazione NON e il venditore. La presenza nel
         catalogo non rivela il contratto, e il contratto non si deduce.»
         COMMERCIAL_CONTRACT e NOT_ESTABLISHED su tutti e 51 i prodotti del
         catalogo — nessuno escluso.

         Quindi l'unico fatto osservabile e: questo prodotto e pubblicato sul
         catalogo pubblico di ADAMA Italia. Su sei di essi il titolare
         dell'autorizzazione e SYNGENTA, ALBAUGH o MICROCIDE, e il portale li
         mostrava sotto «Prodotto ADAMA» — nello stesso sito che elenca
         SYNGENTA fra i concorrenti.

         HOLDER_IS_ADAMA non serve a niente qui: e `undefined` esattamente sui
         sei con titolare esterno e `false` su otto che non hanno titolare
         affatto. La sola lettura affidabile e la stringa del titolare. */
      holderIsExternal: !!(e.holder && !/\bADAMA\b/i.test(String(e.holder))),
      holderIsAdama: e.holder ? /\bADAMA\b/i.test(String(e.holder)) : null,
      /* UN TITOLARE ESTERNO DA SOLO NON PUO FARE UN PRODOTTO ADAMA.
         Il catalogo prova la pubblicazione, non la proprieta. */
      displayAsAdamaProduct: !!e.commercial && !(e.holder && !/\bADAMA\b/i.test(String(e.holder))),
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
  /* La ricerca segue la stessa chiave dell'unione, altrimenti un nome scritto
     con ® non troverebbe il prodotto che quel ® identifica. */
  const findProduct = (name) => productByKey[U(name)] || productByKey[PKEY(name)]
    || PKEY_ALTS(name).map((a) => productByKey[a]).find(Boolean) || null;
  /* LA CHIAVE E INGLESE DA UN LATO E ITALIANA DALL'ALTRO.
     Le righe d'uso portano «Peronospora»; l'opportunita porta «Downy mildew».
     Sono la stessa avversita, e il vocabolario canonico lo dice gia — ma
     strengthFor cercava la riga con la stringa ricevuta e basta, quindi
     rispondeva NO_CONFIRMED_MATCH davanti a una riga che esiste. Non e
     «l'audit ha guardato e non ha trovato»: e non aver guardato nel posto
     giusto, ed e la stessa classe di difetto che teneva vuota la lista
     prodotti sul dettaglio del caso.

         DIRE «NON TROVATO» PERCHE SI E CERCATO NELLA LINGUA SBAGLIATA
         E UN'ASSENZA FABBRICATA, NON MISURATA. */
  const ISSUE_SYNONYMS = (() => {
    const out = {};
    for (const id of Object.keys(ISSUE_BY_ID)) {
      const v = ISSUE_BY_ID[id];
      const forms = uniq([v.it, v.en, id]);
      for (const f of forms) out[U(f)] = forms;
    }
    return out;
  })();
  const strengthFor = (name, crop, issue) => {
    const forms = ISSUE_SYNONYMS[U(issue)] || [issue];
    for (const f of forms) {
      const row = seenRel[relKey(crop, f, name)];
      if (row) return row.strength;
    }
    const e = productByKey[U(name)] || findProductKeyed(name);
    if (e && e.links.some((l) => U(l.crop) === U(crop))) return 'LABEL_CHECK_NEEDED';
    return 'NO_CONFIRMED_MATCH_CURRENT_READING';
  };
  const findProductKeyed = (name) => productByKey[PKEY(name)]
    || PKEY_ALTS(name).map((a) => productByKey[a]).find(Boolean) || null;

  /* ---- COMPETITOR ------------------------------------------------------- */
  const competitorActivities = build('competitorActivities', [
    V21('competitorActivities', (a) => {
      const paid = U(a.ACTIVITY_TYPE) === 'PAID';
      const sem = U(a.COUNTRY_SEMANTICS);
      const italyReach = paid && (sem.indexOf('IT') >= 0 || U(a.COUNTRY_REACHED).indexOf('IT') >= 0);
      const crops = A(a.CROP_TERMS), issues = A(a.ISSUE_TERMS).filter(Boolean);
      const cropsCanonical = cropsOfIds(a.CROP_IDS);
      const generic = crops.filter((c) => GENERIC_CROP_TERMS[U(c)]);
      const speciesIssues = issues.filter((i) => /^[A-Z][a-z]/.test(String(i).trim()));
      const hasDate = !!v21S(a.START_DATE);
      return Object.assign(v21Env(a), {
        id: a.ID,
        /* una nota non e un annuncio: porta il proprio tipo, cosi le schede
           del filtro esauriscono il totale invece di lasciarne sedici fuori. */
        type: v21S(a.ACTIVITY_TYPE) || ((v21S(a.PLATFORM) || v21S(a.COMPANY)) ? null : 'OBSERVATION_NOTE'),
        platform: v21S(a.PLATFORM),
        company: v21S(a.COMPANY) || NOTE_OWN_CHANNEL[U((A(a.SOURCE_IDS) || [])[0])] || null,
        companyRaw: v21S(a.COMPANY), companyKey: U(v21S(a.COMPANY) || NOTE_OWN_CHANNEL[U((A(a.SOURCE_IDS) || [])[0])] || ''),
        page: v21S(a.PAGE), pageId: v21S(a.PAGE_ID),
        displayName: v21S(a.PAGE) || v21S(a.COMPANY),
        channelResolved: !!v21S(a.PAGE),
        country: v21S(a.COUNTRY_REACHED), countrySem: v21S(a.COUNTRY_SEMANTICS),
        geoClass: italyReach ? 'REACHED_IN_ITALY' : paid ? 'REACH_NOT_RESOLVED' : 'MULTI_COUNTRY_OR_UNRESOLVED',
        italyReach, geoCaveat: v21S(a.COUNTRY_SEMANTICS),
        startDate: v21S(a.START_DATE), endDate: v21S(a.END_DATE),
        active: v21S(a.ACTIVE_STATUS), isActive: U(a.ACTIVE_STATUS) === 'ACTIVE',
        media: v21S(a.MEDIA_TYPE), products: A(a.PRODUCTS_PROVED),
        crops, issues, cropsCanonical,
        cropScope: cropsCanonical.length ? 'RESOLVED' : generic.length ? 'GENERIC_TERM' : 'NOT_OBSERVED',
        genericCropTerms: generic, issuesObserved: issues,
        issueScope: speciesIssues.length ? 'SPECIES' : issues.length ? 'GENERIC_TERM' : 'NOT_OBSERVED',
        speciesIssues,
        text: v21S(a.CREATIVE_TEXT), textExcerpt: v21S(a.CREATIVE_TEXT), url: v21S(a.AD_URL),
        hasDate, dateState: hasDate ? 'OBSERVED' : 'NOT_OBSERVED',
        /* Still structurally empty, and for the same reason: the advertiser
           writes a Latin binomial and the window writes an English issue name.
           The V2.1 ISSUE_IDS close that gap only where the package itself
           resolved one, and it resolved none on this collection. */
        relatedWindows: [], relatedWindowsState: 'NO_ISSUE_SYNONYM_TABLE_UPSTREAM',
        daysFromRef: daysFrom(v21S(a.START_DATE)),
        evidenceWhy: v21Text(a, 'EVIDENCE_STATUS_WHY'),
        /* DUE FORME, NON UNA.
           561 record sono ANNUNCI osservati: inserzionista, piattaforma, testo.
           16 sono NOTE DI OSSERVAZIONE: nessuno di quei campi, e al loro posto
           una coppia gia tradotta e approvata di «cosa prova» e «cosa non
           prova». Il modello chiedeva a tutti un COMPANY e ne rifiutava
           sedici — otto dei quali CLIENT_SAFE e con QA approvato, spariti
           senza che nessuna schermata lo dicesse. */
        kind: (v21S(a.ACTIVITY_TYPE) || v21S(a.PLATFORM)) ? 'AD' : 'OBSERVATION_NOTE',
        observationClass: v21S(a.OBSERVATION_CLASS),
        confidence: v21S(a.CONFIDENCE),
        claimDomain: v21S(a.CLAIM_DOMAIN),
        proves: v21Text(a, 'WHAT_IT_PROVES'),
        notProves: v21Text(a, 'WHAT_IT_DOES_NOT_PROVE'),
        /* Il canale di chi parla E il fatto: quando la nota cita il sito
           proprio di un concorrente, l'inserzionista e quel concorrente. La
           tabella e esplicita apposta — nessun nome viene indovinato da una
           stringa, e AgroNotizie resta senza azienda perche e stampa di
           settore, non il canale di nessuno. */
        noteCompany: NOTE_OWN_CHANNEL[U((A(a.SOURCE_IDS) || [])[0])] || null,
      });
    }, (r) => (!r.id ? 'no id'
      /* Una nota non ha inserzionista da dichiarare; un annuncio si. */
      : (r.kind === 'AD' && !r.company) ? 'no company'
      : (r.kind === 'OBSERVATION_NOTE' && !r.proves && !r.notProves) ? 'note with nothing approved to show'
      : null)),
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
    V21('marketObservations', (m) => {
      const per = String(m.REFERENCE_PERIOD || '').split('..');
      const periodStart = dmyToIso(per[0]), periodEnd = dmyToIso(per[1] || per[0]);
      const seriesKey = U(m.GROUP) + '|' + (m.PRODUCT === null || m.PRODUCT === undefined ? '' : String(m.PRODUCT));
      const cropKey = MARKET_CROP[seriesKey] || MARKET_CROP[U(m.GROUP) + '|*'] || cropsOfIds(m.CROP_IDS)[0] || null;
      const stopped = /^PARADA_EM_(\d{4})$/.exec(U(m.SERIES_STATE));
      return Object.assign(v21Env(m), {
        id: m.ID, group: v21S(m.GROUP), product: v21S(m.PRODUCT), market: v21S(m.MARKET),
        priceRaw: v21S(m.PRICE_RAW), price: N(m.PRICE_NUM), unit: v21S(m.UNIT), stage: v21S(m.STAGE),
        referencePeriod: v21S(m.REFERENCE_PERIOD), publicationDate: v21S(m.PUBLICATION_DATE),
        publicationDateISO: isoOf(m.PUBLICATION_DATE), geography: v21S(m.GEOGRAPHY),
        cropKey, seriesKey, periodStart, periodEnd,
        daysSinceObservation: periodEnd ? daysFrom(periodEnd) : null,
        /* UN RECORD DI MERCATO NON E UN'OSSERVAZIONE DI PREZZO.
           Ottanta record su 157 non portano prezzo, ne unita, ne periodo, ne
           stato di serie. `isCurrentSeries` faceva l'ultimo passo sbagliato:
           «stato assente» cadeva su «non corrente», cioe la schermata
           dichiarava FERMA una serie di cui non sa nulla, e stampava «serie
           ferma dal null» perche nemmeno l'anno esisteva.

               NON SAPERE SE UNA SERIE E CORRENTE
               NON E SAPERE CHE E FERMA.

           Tre stati, non due, e un campo che dice se c'e davvero un prezzo. */
        hasPrice: N(m.PRICE_NUM) !== null || !!v21S(m.PRICE_RAW),
        seriesState: U(m.SERIES_STATE) ? (U(m.SERIES_STATE) === 'CORRENTE' ? 'CURRENT' : 'STOPPED') : 'NOT_DECLARED',
        isCurrentSeries: U(m.SERIES_STATE) === 'CORRENTE',
        isStoppedSeries: !!U(m.SERIES_STATE) && U(m.SERIES_STATE) !== 'CORRENTE',
        stoppedYear: stopped ? Number(stopped[1]) : null,
        /* PARADA_EM_2015 is a STATE and a YEAR welded into one token, so it is
           not a closed vocabulary and cannot have a dictionary entry: a series
           that stops in 2027 would print the raw Portuguese. Split at the
           boundary — the state joins the enum table, the year is a number. */
        hasStage: !!v21S(m.STAGE), hasPublicationDate: !!v21S(m.PUBLICATION_DATE),
        prevPrice: N(m.PREV_PRICE_NUM), changeVsPrev: N(m.CHANGE_VS_PREV_PCT),
        yearAgoPrice: N(m.YEAR_AGO_PRICE_NUM), changeVsYearAgo: N(m.CHANGE_VS_YEAR_AGO_PCT),
        /* la riga che assegnava di nuovo seriesState, e che rimetteva `null`
           dove ora c'e NOT_DECLARED, e stata tolta: due assegnazioni dello
           stesso campo nello stesso oggetto, e vinceva la seconda. */
        seriesStateRaw: v21S(m.SERIES_STATE),
        seriesWarning: null,
        seriesWarningText: v21Text(m, 'SERIES_WARNING'),
        /* COMMODITY_STAGE is the R5 distinction: a processed-product price is
           not the crop's market. It travels so no crop panel can average one
           into the other. */
        commodityStage: v21S(m.COMMODITY_STAGE),
        observations: N(m.OBSERVATIONS_IN_SERIES), sourceId: v21S(m.SOURCE_ID),
        publishedDaysAgo: daysFrom(isoOf(m.PUBLICATION_DATE)),
        ui: { marketCropKey: cropKey ? MARKET_VIEW_KEY[cropKey] || null : null },
      });
    }, (r) => (!r.id ? 'no ID' : null)),
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
          /* stessa legge dell'altro adattatore: assenza non e fermata. */
          hasPrice: N(m.PRICE_NUM) !== null || !!v21S(m.PRICE_RAW),
          seriesState: U(m.SERIES_STATE) ? (U(m.SERIES_STATE) === 'CORRENTE' ? 'CURRENT' : 'STOPPED') : 'NOT_DECLARED',
          isCurrentSeries: U(m.SERIES_STATE) === 'CORRENTE',
          isStoppedSeries: !!U(m.SERIES_STATE) && U(m.SERIES_STATE) !== 'CORRENTE',
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
    V21('scienceRecords', (r) => Object.assign(v21Env(r), {
      id: r.ID, title: v21S(r.TITLE), doi: v21S(r.DOI),
      author: v21S(r.AUTHOR), orcid: v21S(r.ORCID), institution: v21S(r.INSTITUTION),
      publishedAt: v21S(r.PUBLISHED_AT), date: v21S(r.PUBLISHED_AT),
      year: v21S(r.PUBLISHED_AT) ? String(r.PUBLISHED_AT).slice(0, 4) : null,
      venue: v21S(r.VENUE), materialType: v21S(r.MATERIAL_TYPE), materialRole: v21S(r.MATERIAL_ROLE),
      crop: v21S(r.CROP), issue: v21S(r.ISSUE), countryOfFact: v21S(r.COUNTRY_OF_FACT),
      url: v21S(r.SOURCE_URL), sourceId: v21S(r.SOURCE_ID),
    }), (r) => (!r.id ? 'no ID' : !r.title ? 'no title' : null)),
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

  /* AFFILIATION_CAVEAT is the source registry's own limitation, restated as a
     value so it can travel with every institution the portal shows. An
     affiliation belongs to the AUTHOR, not to the study: reading it as
     "research done in this region" is the single easiest error on this screen. */
  const AFFILIATION_CAVEAT = 'The affiliation belongs to the author, not to the study.';

  const researchers = build('researchers', [
    V21('researchers', (r) => Object.assign(v21Env(r), {
      id: r.ID, name: v21S(r.PERSON), category: v21S(r.CATEGORY),
      orcid: /^https?:\/\/orcid\.org\//i.test(v21S(r.ORCID) || '') ? v21S(r.ORCID) : null,
      openAlexId: v21S(r.OPENALEX_ID), openalexId: v21S(r.OPENALEX_ID),
      institutions: A(r.INSTITUTIONS),
      org: A(r.INSTITUTIONS).join(' · ') || null,
      orgLabel: A(r.INSTITUTIONS).join(' · ') || null,
      affiliationCaveat: AFFILIATION_CAVEAT,
      theme: v21S(r.THEME), themeKey: v21S(r.THEME),
      themeLabel: (THEME_UI[U(r.THEME)] || {}).title || null,
      worksInScope: N(r.WORKS_IN_SCOPE),
      lastActivity: v21S(r.LAST_ACTIVITY), daysFromRef: daysFrom(v21S(r.LAST_ACTIVITY)),
      identityStatus: v21S(r.IDENTITY_STATUS), identityState: v21S(r.IDENTITY_STATUS),
      role: v21S(r.ROLE), factRegion: v21S(r.FACT_REGION),
      sourceId: v21S(r.SOURCE_ID),
    }), (r) => (!r.id ? 'no ID' : !r.name ? 'no person' : null)),
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

  const scienceThemes = build('scienceThemes', [
    V21('scienceThemes'),
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

  const resistance = build('resistance', [
    V21('resistance', (r) => Object.assign(v21Env(r), {
      id: r.ID,
      species: v21S(r.SPECIES), speciesIt: v21S(r.SPECIES_IT), family: v21S(r.FAMILY),
      mechanism: v21Text(r, 'MECHANISM'),
      mechanismStated: v21Text(r, 'MECHANISM').state === KNOWLEDGE.CLEAR,
      crop: cropsOfIds(r.CROP_IDS)[0] || cropResolve(r.CROP_DECLARED).label,
      cropRaw: v21S(r.CROP_DECLARED),
      cropKey: cropsOfIds(r.CROP_IDS)[0] || cropResolve(r.CROP_DECLARED).key,
      cropKeys: cropsOfIds(r.CROP_IDS).length ? cropsOfIds(r.CROP_IDS) : cropResolve(r.CROP_DECLARED).keys,
      cropScope: cropScopeOfIds(r.CROP_IDS), cropDeclared: null, cropIsProse: false,
      firstCaseYear: v21S(r.FIRST_CASE_YEAR),
      regions: regionsOfIds(r.REGION_IDS).length ? regionsOfIds(r.REGION_IDS) : A(r.REGIONS),
      multiple: v21Text(r, 'MULTIPLE_RESISTANCE').state === KNOWLEDGE.CLEAR,
      multipleText: v21Text(r, 'MULTIPLE_RESISTANCE'),
      citation: v21S(r.CITATION), authority: v21S(r.AUTHORITY),
      url: v21S(r.SOURCE_URL), sourceId: v21S(r.SOURCE_ID),
    }), (r) => (!r.id ? 'no ID' : !r.species ? 'no species' : null)),
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

  /* ---- PUBLIC VOICES ---------------------------------------------------- */
  const publicVoices = build('publicVoices', [
    V21('publicVoices', (v) => Object.assign(v21Env(v), {
      id: v.ID, kind: v21S(v.KIND) || v21S(v.VOICE_KIND),
      person: v21S(v.PERSON), identityState: v21S(v.PERSON_IDENTITY_STATE),
      role: v21S(v.ROLE), organization: v21S(v.ORGANIZATION),
      platform: v21S(v.PLATFORM), channel: v21S(v.CHANNEL), title: v21S(v.CONTENT_TITLE),
      date: v21S(v.DATE), dateISO: isoOf(v21S(v.DATE)), dateState: v21Known(v.DATE),
      dateRelative: v21S(v.DATE_RELATIVE), dateNote: v21S(v.DATE_NOTE),
      crop: v21S(v.CROP), cropCanonical: cropsOfIds(v.CROP_IDS)[0] || cropResolve(v.CROP).key,
      issue: v21S(v.ISSUE), caseId: v21S(v.CASE_ID),
      region: regionsOfIds(v.REGION_IDS)[0] || v21S(v.REGION),
      countryOfFact: v21S(v.COUNTRY_OF_FACT),
      /* The quote as published. Never translated, never parsed for a fact. */
      textOriginal: v21S(v.TEXT_ORIGINAL),
      /* Who is listening is a different fact from who is speaking, and the
         package states it separately. It stays separate here. */
      audienceKind: v21S(v.CHANNEL_AUDIENCE_KIND),
      proves: v21Text(v, 'WHAT_IT_PROVES'),
      notProves: v21Text(v, 'WHAT_IT_DOES_NOT_PROVE'),
      /* SINGOLARE E PLURALE.
         Le 21 voci arrivate dalla stampa di settore non portano SOURCE_URL ne
         SOURCE_ID: portano SOURCE_URLS e SOURCE_IDS, che l'involucro comune
         ha gia letto due righe sopra. Leggendo solo il singolare, quelle voci
         risultavano senza fonte: niente link «apri la fonte» su 21 schede su
         79, e la colonna FONTE vuota nell'archivio, mentre la fonte era li. */
      sourceUrl: v21S(v.SOURCE_URL) || A(v.SOURCE_URLS)[0] || null,
      sourceId: v21S(v.SOURCE_ID) || A(v.SOURCE_IDS)[0] || null,
      daysFromRef: daysFrom(isoOf(v21S(v.DATE))),
    }), (r) => (!r.id ? 'no ID' : null)),
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

  const publicChannels = build('publicChannels', [
    V21('publicChannels', (c) => {
      const host = (String(v21S(c.CHANNEL_URL) || '').match(/^https?:\/\/([^/]+)/i) || [])[1] || '';
      return Object.assign(v21Env(c), {
        id: c.ID, name: v21S(c.CHANNEL), channel: v21S(c.CHANNEL), url: v21S(c.CHANNEL_URL),
        host: host || null,
        platform: /youtube\.com$/i.test(host.replace(/^www\./, '')) ? 'YouTube' : null,
        identityState: v21S(c.IDENTITY_STATE),
        contentTypeExample: v21S(c.CONTENT_TYPE_EXAMPLE),
        exampleTitle: v21S(c.EXAMPLE_TITLE), exampleUrl: v21S(c.EXAMPLE_URL),
        examplePublishedAt: v21S(c.EXAMPLE_PUBLISHED_AT),
        examplePublishedISO: isoOf(v21S(c.EXAMPLE_PUBLISHED_AT)),
        exampleViews: N(c.VIEWS), views: N(c.VIEWS), caseId: v21S(c.CASE_ID),
      });
    }, (r) => (!r.id ? 'no ID' : null)),
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

  const publicPeople = build('publicPeople', [
    V21('publicPeople'),
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
  const sources = build('sources', [
    V21('sources', (s) => {
      const type = v21S(s.TYPE);
      const group = SOURCE_GROUP[U(type)] || null;
      const freq = v21S(s.FREQUENCY);
      return Object.assign(v21Env(s), {
        id: s.ID || s.SOURCE_ID, sourceId: s.SOURCE_ID || s.ID,
        /* A SOURCE WITHOUT A SHOWABLE NAME IS STILL A SOURCE.
           Seventeen of these rows carry a research note where the name should
           be, so the ingest withholds the text — and rejecting them for having
           no name would delete a source that other records CITE, breaking the
           evidence link R1 exists to protect.

           The package's own key note says `ID = SRC_<HOST>, derived from the
           URL`, so the host is recoverable from the identifier itself. That is
           reading the declared key, not inventing a label. The encoding folds
           '-' onto '_', so a hyphenated host comes back with a dot; the value
           is therefore named for what it is — a key-derived label — and the
           state says the real name was withheld.

           AND THE SAME IS TRUE OF A NAME THAT ARRIVED AS A RESEARCH NOTE.
           The ingest withheld the notes ITS marker list recognised; measured,
           it did not recognise this class, so the model asks the question
           again with showableSourceName() before printing anything. A name it
           refuses is not a name that is missing — it is a name that is known
           and not displayable, which is exactly what NOT_APPROVED_FOR_DISPLAY
           has always meant here. The fallback is the one that already existed,
           so no source acquires a second kind of label.

           The last resort is the canonical id, and it stands in ONLY for a
           name THIS gate refused: measured, one row (SRC_DESCONHECIDA, whose
           key is not a host and which has no URL to derive from). A code is
           not prose in any language, and it keeps the row — dropping it would
           delete a source that other records cite, which is the very thing the
           paragraph above refuses to do.

           It deliberately does NOT stand in where the name was already absent
           upstream. SRC_NAO_DECLARADA has no name, no host in its key and no
           URL, and this package has always rejected it for having no name at
           all; giving it a code here would silently re-admit a record on the
           back of a language fix, and the count would stop meaning what it
           meant yesterday. Measured before and after this change: 188. */
        /* IL REGISTRO CONTA FONTI, NON SEGNAPOSTI.
           Il pacchetto porta 189 righe, e due di esse dichiarano
           ENTITY_TYPE: SOURCE_SENTINEL — SRC_NAO_DECLARADA e SRC_DESCONHECIDA.
           Non sono fonti: sono il modo in cui il pacchetto dice «qui non e
           stata dichiarata una fonte». Le fonti reali sono 187.

           La prima veniva gia esclusa, ma solo di rimbalzo, perche non aveva
           un nome; la seconda entrava e portava sullo schermo il proprio id
           portoghese come se fosse un nome. Ora l'esclusione e dichiarata per
           quello che e, e non dipende piu da cosa il portone di lingua abbia
           deciso di trattenere. */
        name: showableSourceName(s.NAME) || hostFromSourceKey(s.ID) || null,
        nameState: showableSourceName(s.NAME) ? KNOWLEDGE.CLEAR
          : (v21S(s.NAME) || s.NAME__PT_ONLY) ? KNOWLEDGE.NOT_APPROVED_FOR_DISPLAY
            : KNOWLEDGE.NOT_ESTABLISHED,
        nameIsKeyDerived: !showableSourceName(s.NAME),
        type,
        role: v21Text(s, 'ROLE'),
        roleText: v21Text(s, 'ROLE').it, roleCode: type,
        group, groupLabel: group ? SOURCE_GROUP_LABEL[group] : null,
        uiGroup: group ? SOURCE_GROUP_LABEL[group] : null,
        country: v21S(s.COUNTRY), geography: v21S(s.GEOGRAPHY), url: v21S(s.URL),
        frequency: freq, frequencyKnown: !!(freq && !FREQ_NOT_DECLARED[U(freq)]),
        latestObservation: v21S(s.LATEST_OBSERVATION),
        latestObservationISO: isoOf(String(v21S(s.LATEST_OBSERVATION) || '').slice(0, 10)),
        accessStatus: v21S(s.ACCESS_STATUS),
        limitations: v21Text(s, 'LIMITATIONS'),
        limitationsText: v21Text(s, 'LIMITATIONS').it,
        /* R2/R3 · the route measurement, when the package carries one. A source
           that needs an Italian route is a fact about the source, not about us. */
        accessEvidence: v21S(s.ACCESS_EVIDENCE),
        accessEvidenceMeasured: s.ACCESS_EVIDENCE_MEASURED === true,
        requiresItalianRoute: s.REQUIRES_ITALIAN_ROUTE === true,
        idAliases: A(s.ID_ALIASES),
        entityType: U(s.ENTITY_TYPE),
        ui: { color: SOURCE_TYPE_COLOR[U(type)] || NEUTRAL, order: null },
      });
    }, (r) => (!r.id ? 'no ID'
      /* i due segnaposto del pacchetto non sono fonti: dicono che una fonte
         non e stata dichiarata. Escluderli per quello che sono, non di
         rimbalzo perche gli manca un nome. */
      : r.entityType === 'SOURCE_SENTINEL' ? 'sentinel, not a source'
      : !r.name ? 'no name' : null)),
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

  const futureEvents = build('futureEvents', [
    V21('futureEvents', (e) => {
      /* The package parses the date itself and says how precisely. A range that
         it could not parse arrives as a state, not as a guessed day. */
      const startDate = v21S(e.START_DATE) || isoRange(v21S(e.DATE))[0];
      const endDate = v21S(e.END_DATE) || isoRange(v21S(e.DATE))[1];
      const part = e.CONFIRMED_PARTICIPATION && typeof e.CONFIRMED_PARTICIPATION === 'object'
        && !Array.isArray(e.CONFIRMED_PARTICIPATION) ? e.CONFIRMED_PARTICIPATION : {};
      return Object.assign(v21Env(e), {
        id: e.ID, name: v21S(e.EVENT), date: v21S(e.DATE),
        startDate, endDate, dateEnd: endDate,
        dateState: v21S(e.DATE_PARSE_STATE) || v21Known(e.DATE),
        datePrecision: v21S(e.DATE_PRECISION),
        location: v21S(e.LOCATION), sector: v21S(e.SECTOR),
        cropRelevance: v21S(e.CROP_RELEVANCE), cropRelevanceList: A(e.CROP_RELEVANCE),
        organizer: v21S(e.ORGANIZER), url: v21S(e.OFFICIAL_URL),
        exhibitorListState: v21S(e.EXHIBITOR_LIST_STATE), timeState: v21S(e.TIME_STATE),
        confirmedParticipation: part, confirmedParticipationList: Object.keys(part),
        participationLaw: v21Text(e, 'PARTICIPATION_LAW'),
        participationLawText: v21Text(e, 'PARTICIPATION_LAW').it,
        note: v21Text(e, 'NOTE'),
        daysFromRef: daysFrom(startDate), daysToStart: daysFrom(startDate),
      });
    }, (r) => (!r.id ? 'no ID' : !r.name ? 'no event name' : null)),
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

  const news = build('news', [
    V21('news', (n) => Object.assign(v21Env(n), {
      id: n.ID, title: v21S(n.TITLE), publisher: v21S(n.PUBLISHER), outlet: v21S(n.PUBLISHER),
      author: v21S(n.AUTHOR), date: v21S(n.DATE),
      dateISO: isoOf(v21S(n.DATE)), dateState: v21Known(n.DATE),
      crop: v21S(n.CROP),
      cropCanonical: cropsOfIds(n.CROP_IDS)[0] || cropResolve(n.CROP).key,
      cropScope: A(n.CROP_IDS).length ? cropScopeOfIds(n.CROP_IDS) : cropResolve(n.CROP).scope,
      issue: v21S(n.ISSUE),
      region: regionsOfIds(n.REGION_IDS)[0] || v21S(n.REGION),
      contentKind: v21S(n.CONTENT_KIND),
      contentKindMeaning: v21Text(n, 'CONTENT_KIND_MEANING'),
      isEditorial: U(n.CONTENT_KIND) === 'EDITORIAL',
      summary: v21Text(n, 'SINTONIA_SUMMARY'),
      caveat: v21Text(n, 'CAVEAT'),
      url: v21S(n.SOURCE_URL), daysFromRef: daysFrom(isoOf(v21S(n.DATE))),
    }), (r) => (!r.id ? 'no ID' : !r.title ? 'no title' : null)),
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

  /* ---- SOURCE RESOLUTION · one join key for the whole model -------------
     Every record that names a source names it by ID. The only exception is
     news, which names a PUBLISHER string; that is resolved by EXACT
     case-insensitive name match and left null when it does not match.
     MEASURED: 6 of 8 news items resolve. The two that do not are 'Agronotizie'
     (a casing variant of 'AgroNotizie (Image Line)') and 'Consorzio
     Fitosanitario di Modena' (the registry says 'Provinciale'). Fuzzy-matching
     them would create a link the evidence does not support. */
  const sourceById = {};
  sources.records.forEach((s) => { sourceById[U(s.id)] = s; if (s.sourceId) sourceById[U(s.sourceId)] = s; });
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
        /* TRE NUMERI, NON UNO.
           `observationCount` contava OGNI record e la schermata lo chiamava
           «righe di prezzo settimanali ingerite»: per il pomodoro diceva 12
           righe di prezzo dove i prezzi sono zero. E `stoppedCount` contava
           tutto cio che non era dichiarato corrente, quindi sommava le serie
           davvero ferme con quelle di cui non si sa nulla, e stampava «serie
           ferma dal null» perche l'anno non c'era.

               UN RECORD DI MERCATO NON E UN'OSSERVAZIONE DI PREZZO.
               E NON SAPERE NON E SAPERE DI NO.

           I record restano tutti: nessuno viene buttato per non avere prezzo. */
        observationCount: recs.length,
        priceCount: recs.filter((m) => m.hasPrice).length,
        hasPrices: recs.some((m) => m.hasPrice),
        currentCount: current.length,
        stoppedCount: recs.filter((m) => m.isStoppedSeries).length,
        undeclaredCount: recs.filter((m) => m.seriesState === 'NOT_DECLARED').length,
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
  const marketSummaries = build('marketSummaries', [
    V21('marketSummaries'),
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

  /* ---- REGULATORY FUTURE · the authorisation expiry calendar ------------
     EXPIRY is present on 163/163 registry records and nothing read it. It is
     the only forward-looking regulatory fact the package actually contains, so
     the slot that used to be empty is now filled from real data rather than
     left waiting for a table that already existed. */
  const regulatoryFuture = build('regulatoryFuture', [
    V21('regulatoryFuture', (r) => Object.assign(v21Env(r), {
      id: r.ID,
      /* This collection is an OBSERVATION about the regulatory future, not the
         product-expiry calendar. It carries no product and no date of its own:
         the dated facts live in regulatoryFutureFacts, which is a different
         table and is counted separately. */
      product: null, productKey: null, reg: null, holder: null,
      status: v21S(r.OBSERVATION_CLASS),
      expiry: null, expiryISO: null, daysToExpiry: null, expired: false,
      regCat: null, line: null, labelUrl: A(r.SOURCE_URLS)[0] || null,
      observationClass: v21S(r.OBSERVATION_CLASS), confidence: v21S(r.CONFIDENCE),
      sourceScope: v21S(r.SOURCE_SCOPE),
      whatItIs: v21Text(r, 'WHAT_IT_IS'),
      proves: v21Text(r, 'WHAT_IT_PROVES'),
      notProves: v21Text(r, 'WHAT_IT_DOES_NOT_PROVE'),
    }), (r) => (!r.id ? 'no ID' : null)),
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
        provenance: provOf(p, P.REAL_SOURCE), raw: p,
      }),
      validate: (r) => (!r.product ? 'no product' : !r.expiryISO ? 'unparseable expiry' : null),
    },
  ], 'authorisation expiry dates published by the national registry; a date the registry states, not a forecast');

  /* ---- FUTURE ----------------------------------------------------------- */
  const futureSignals = build('futureSignals', [
    V21('futureSignals', (f) => Object.assign(v21Env(f), {
      id: f.ID || f.SIGNAL_ID, legacyId: v21S(f.LEGACY_ID),
      crop: cropsOfIds(f.CROP_IDS)[0] || cropResolve(f.CROP).label,
      cropRaw: v21S(f.CROP),
      cropKey: cropsOfIds(f.CROP_IDS)[0] || cropResolve(f.CROP).key,
      cropKeys: cropsOfIds(f.CROP_IDS).length ? cropsOfIds(f.CROP_IDS) : cropResolve(f.CROP).keys,
      cropScope: A(f.CROP_IDS).length ? cropScopeOfIds(f.CROP_IDS) : cropResolve(f.CROP).scope,
      issue: issueResolve(f.ISSUE).it, issueEn: issueResolve(f.ISSUE).en, issueRaw: v21S(f.ISSUE),
      region: regionsOfIds(f.REGION_IDS)[0] || v21S(f.REGION),
      regionRaw: v21S(f.REGION), regionScope: A(f.REGION_IDS).length ? 'RESOLVED' : 'NOT_OBSERVED',
      regionKeys: regionsOfIds(f.REGION_IDS),
      status: null,
      whoIsTalking: v21Text(f, 'WHO_IS_TALKING'),
      whatChanged: v21Text(f, 'WHAT_CHANGED'),
      whyWatch: v21Text(f, 'WHY_WATCH'),
      howWeGotHere: v21Text(f, 'HOW_SINTONIA_GOT_HERE'),
      observedFacts: v21Text(f, 'OBSERVED_FACTS'),
      interpretation: v21Text(f, 'SINTONIA_INTERPRETATION'),
      unknown: v21Text(f, 'UNKNOWN'),
      nextWindow: v21Text(f, 'NEXT_WINDOW'),
      portfolioConnection: v21Text(f, 'PORTFOLIO_CONNECTION'),
      whatWouldPromoteIt: v21Text(f, 'WHAT_WOULD_MAKE_IT_AN_OPPORTUNITY'),
      promotedToRadar: v21S(f.PROMOTED_TO_RADAR),
      evidenceIds: [], confidence: null,
    }), (r) => (!r.id ? 'no ID' : null)),
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

  /* Generated presentation scenarios live OUTSIDE the real feed. They never
     count in real totals, source convergence or emerging-topic metrics. */
  const futureScenarios = coll(
    A(RAW.DEMO.SIGNALS).map((x) => Object.assign({}, x, { provenance: P.DEMO_SCENARIO })),
    P.DEMO_SCENARIO,
    'presentation scenarios; not evidence, never counted as real',
    { source: 'ITALY_DEMO.SIGNALS' }
  );

  /* A narrative slot the upstream simply does not fill. Distinct from prose it
     wrote and we may not show: this one was never written. */
  const NO_NARRATIVE = { state: KNOWLEDGE.NOT_ESTABLISHED, it: null, en: null };

  /* ---- OPPORTUNITIES ---------------------------------------------------- */
  const windowByLegacyCase = {};
  cropWindows.records.forEach((w) => { if (w.legacyCaseId) windowByLegacyCase[U(w.legacyCaseId)] = w; });

  const opportunities = build('opportunities', [
    /* ── THE OPPORTUNITY ENGINE · 37 objects, and what the client is told ──
       The three cards this replaces were written by hand and carried prose for
       evidence. The engine derives 37 from the package itself, collapses 40
       duplicates onto existing cases instead of multiplying them, and lets the
       red team knock 17 out. The 17 never reach this file: the site ingest does
       not ship a rejected opportunity, so no view can render one by mistake.

       THE LABEL THE CLIENT SEES
       All 37 are CLIENT_SAFE=false, and that was not loosened to raise a
       number: an opportunity is OUR reading over third-party facts, and the
       rule that governs our own crossings governs this too. Nine of them pass
       with the method declared beside them; the rest are candidates.

           9   CONVERGENZA VERIFICATA  ·  VERIFIED CONVERGENCE
           28  DA VALIDARE             ·  TO VALIDATE

       The package's own OPPORTUNITY_LABEL_IT says «OPPORTUNITÀ CONFERMATA».
       That wording is not shipped and not used: 'confirmed' is what an engine
       calls a case that cleared its gates, and it is not what a client should
       read next to a card whose evidence is a convergence we drew. The label
       comes from the interface dictionary, in both languages, and nowhere else.

       WHAT NEVER REACHES THE RECORD
       CLIENT_SAFE, RENDERABLE_WITH_METHOD, QA_STATUS (EVIDENCE_DERIVED) and the
       blocking gates are engine bookkeeping. They are read here to CHOOSE the
       label and are then dropped — they are not properties of this object, so
       no binding, no drawer and no debug dump can put them in front of a
       client. What survives is one word: `convergence`.

           A FLAG YOU DELETE CANNOT BE RENDERED BY ACCIDENT. */
    V21('opportunities', (o) => {
      const verified = o.RENDERABLE_WITH_METHOD === true;
      const crop = cropOfId(o.CROP);
      const issue = issueOfId(o.TARGET);
      const region = regionOfId(o.GEOGRAPHY);
      const scope = SCOPE_BY_ID[U(o.GEOGRAPHY)] || null;
      /* The identity the engine deduplicates on, restated as a title: crop,
         target and place. Every part is a resolved proper name, so the line is
         the same fact in both languages and asserts nothing the record does
         not already carry. */
      const title = [crop, issue ? issue.it : null, region || (scope ? null : null)]
        .filter(Boolean).join(' · ') || null;
      const titleEn = [crop, issue ? issue.en : null, region].filter(Boolean).join(' · ') || null;
      return {
        id: o.ID, legacyCaseId: null,
        title, titleEn,
        /* THE ONE STATE THE CLIENT SEES. */
        convergence: verified ? 'VERIFIED_CONVERGENCE' : 'TO_VALIDATE',
        crop, cropRaw: null, cropScope: cropScopeOfIds(o.CROP_IDS),
        cropKeys: crop ? [crop] : cropsOfIds(o.CROP_IDS),
        region, regionRaw: null,
        regionNames: region ? [region] : regionsOfIds(o.REGION_IDS),
        regionKeys: region ? [region] : regionsOfIds(o.REGION_IDS),
        regionScope: region ? 'RESOLVED' : scope ? 'SCOPE_ONLY' : 'NOT_OBSERVED',
        geoScope: scope || v21S(o.GEOGRAPHIC_SCOPE),
        issue: issue ? issue.it : null, issueEn: issue ? issue.en : null, issueRaw: null,
        issueType: null,
        caseLabel: null, forbiddenLabel: null,
        /* The archetype is WHY this is a case at all, as a token the interface
           dictionary translates. Its Portuguese gloss upstream is not shipped. */
        archetype: v21S(o.ARCHETYPE),
        status: v21S(o.STATUS),
        /* The engine's window is the APPLICATION window and is UNKNOWN on 30 of
           37 — because only 2 of 35 label crops declare one. That is not the
           same question as whether the signal is current, which SIGNAL_DATE
           answers separately. Both travel; neither substitutes for the other. */
        windowStart: v21S(o.WINDOW_START), windowEnd: v21S(o.WINDOW_END),
        windowState: v21S(o.WINDOW_STATE),
        daysRemaining: N(o.DAYS_REMAINING),
        signalDate: v21S(o.SIGNAL_DATE), signalAgeDays: N(o.SIGNAL_AGE_DAYS),
        windowText: null, windowApplication: null, windowMonitoring: null, windowNextCycle: null,
        /* The numbers live outside the sentence, so the sentence stays
           translatable. The keys are a closed vocabulary the dictionary names. */
        numbers: o.NUMBERS && typeof o.NUMBERS === 'object'
          ? Object.keys(o.NUMBERS).map((k) => ({ key: k, value: o.NUMBERS[k] })) : [],
        productLinkState: v21S(o.PRODUCT_LINK_STATE),
        adamaProducts: A(o.PRODUCT_RELATIONSHIPS),
        adamaActiveSubstance: [],
        /* ── LA COLONNA COMMERCIALE, DAL MOTORE ─────────────────────────────
           Due domande diverse, e nessuna sostituisce l'altra:
           `opportunityState` risponde «questa lettura si regge?»,
           `commercialPriority` risponde «e un'opportunita commerciale
           difendibile?», e `externalMaterialReady` risponde «puo USCIRE di
           casa?». Il portale teneva un proprio righello per la terza
           (`rtvEligibility`), derivato da cio che la scheda vede; il motore la
           decide con dato che la scheda non ha — catalogo pubblico, frase
           della fonte, portoni di evidenza.

               UN RIGHELLO DUPLICATO SONO DUE RIGHELLI CHE DIVERGERANNO.

           Da qui il verdetto del motore viaggia, e il righello del portale
           resta la RISERVA per il caso che non lo porta. Sono CODICI: le frasi
           vivono nel dizionario di lingua, di qua dalla frontiera. */
        commercialPriority: v21S(o.COMMERCIAL_PRIORITY),
        commercialWhyCodes: A(o.WHY_COMMERCIAL_CODES),
        externalMaterialReady: v21S(o.EXTERNAL_MATERIAL_READY),
        externalBlockerCodes: A(o.EXTERNAL_BLOCKER_CODES),
        caseActiveIngredients: A(o.CASE_ACTIVE_INGREDIENTS),
        needDirection: v21S(o.NEED_DIRECTION),
        needEvidenceId: v21S(o.NEED_EVIDENCE_ID),
        needMethod: v21S(o.NEED_METHOD),
        evidenceIds: A(o.EVIDENCE_IDS),
        evidenceFamilies: A(o.EVIDENCE_FAMILIES),
        evidenceCount: N(o.EVIDENCE_COUNT),
        /* The score ORDERS, it does not prove. Kept so the radar can sort, and
           named so no card can print it as a confidence percentage. */
        sortScore: N(o.OPPORTUNITY_SCORE),
        scoreDimensions: o.SCORE_DIMENSIONS && typeof o.SCORE_DIMENSIONS === 'object'
          ? Object.keys(o.SCORE_DIMENSIONS).map((k) => ({ key: k, value: o.SCORE_DIMENSIONS[k] })) : [],
        /* Who should look at this now. A routing hint, never a task. */
        actionMap: A(o.ACTION_MAP),
        proves: v21Text(o, 'WHAT_IT_PROVES'),
        notProves: v21Text(o, 'WHAT_IT_DOES_NOT_PROVE'),
        /* The prose slots the old three cards filled. The engine writes no
           free prose at all, so they resolve to the not-established state
           rather than to an empty string that would read as a blank panel. */
        whatIsHappening: NO_NARRATIVE, whyItMatters: NO_NARRATIVE,
        currentEvidence: NO_NARRATIVE, marketContext: NO_NARRATIVE,
        competitorContext: NO_NARRATIVE, scienceContext: NO_NARRATIVE,
        fieldVoices: NO_NARRATIVE, whatWeKnow: NO_NARRATIVE,
        whatWeDoNotKnow: NO_NARRATIVE, interpretations: NO_NARRATIVE,
        currentEvidenceList: [], whatWeKnowList: [], whatWeDoNotKnowList: [], interpretationsList: [],
        happeningState: null, happeningDocument: null, happeningContent: null,
        observationDate: null, happeningPublicationDate: null, freshnessDays: null,
        observedStage: null, happeningSourceId: null, happeningSourceResolves: false,
        whyMandatory: null, whyNote: null, whyRegional: [],
        scienceContextState: null, scienceContextCounts: [],
        canonicalWindow: null, windowId: null,
        sourceIds: A(o.SOURCE_IDS),
        sourceIdsResolve: A(o.SOURCE_IDS).every((x) => !!sourceById[U(x)]),
        ui: categoryOf(issue ? issue.en : null),
        provenance: P.REAL_DERIVED,
        /* `raw` is deliberately NOT carried here. On every other family it is
           the audit trail; on this one it is the only place CLIENT_SAFE,
           RENDERABLE_WITH_METHOD and the gate list still exist, and a drawer
           that dumps `raw` would put them on screen. The evidence ids above are
           the audit trail this object needs. */
      };
    }, (r) => (!r.id ? 'no ID' : null)),
    {
      source: 'ITALY_INGEST.OPPORTUNITIES',
      precedence: P.REAL_SOURCE,
      rows: RAW.IG.OPPORTUNITIES,
      adapt: (o) => {
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
          whatWeKnow: narrative(o, 'WHAT_WE_KNOW'),
          whatWeKnowList: A(o.WHAT_WE_KNOW),
          whatWeDoNotKnow: narrative(o, 'WHAT_WE_DO_NOT_KNOW'),
          whatWeDoNotKnowList: A(o.WHAT_WE_DO_NOT_KNOW),
          interpretations: narrative(o, 'INTERPRETATIONS'),
          interpretationsList: A(o.INTERPRETATIONS),
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
        };
      },
      /* An opportunity does NOT have to name a crop. IT-OPP-003 is the
         authorisation-expiry case, which the source itself describes as
         "transversal, não é uma cultura" — portfolio-wide. Requiring a crop
         silently rejected a real record and the radar showed 2 where upstream
         supplied 3. Only the identity is mandatory. */
      validate: (r) => (!r.id ? 'no ID' : null),
    },
  ], 'upstream opportunity intelligence; the real radar feed');

  /* The product links an opportunity asserts, graded by the label audit rather
     than believed. MEASURED: with the raw Portuguese crop and issue all six
     products on opportunity 001 return LABEL_CHECK_NEEDED; through the declared
     crop map they return 2 VERIFIED (EVURE PRO, MAVRIK SMART) and 4 still
     needing a label check. Neither number is invented — the second is simply
     the audit being asked the question in the vocabulary it was written in. */
  /* The engine already asked this question, and asked it of a bigger corpus.
     PRODUCT_LINK_STATE is graded against the 2.030 label pairs; the 12-row
     audit below is what the portal had before those pairs existed. Re-deriving
     the answer from the smaller source would DOWNGRADE a verified link to
     LABEL_CHECK_NEEDED and call that caution.

         WHEN TWO READINGS DISAGREE, THE ONE THAT READ MORE LABELS WINS —
         AND THE RECORD SAYS WHICH ONE ANSWERED. */
  /* PRODUCT_LINK_STATE is a verdict about the OPPORTUNITY, not about each
     product on it. Stamping it onto all twelve products of a case would be the
     aggregate-into-item error: true of the set, asserted of the member.

     So each product is graded against the pair corpus itself, on this case's own
     canonical crop and target. Measured on this package the two answers agree —
     an opportunity's product list IS the product list of its crop x target
     pairs — but they agree because the lookup was done, not because it was
     assumed, and a future case where they diverge will show the divergence
     instead of hiding it. */
  const pairStrengthIndex = {};
  productRelationships.records.forEach((r) => {
    if (!r.crop || !r.issueEn || !r.productKey) return;
    const k = U(r.crop) + '|' + U(r.issueEn);
    const cur = pairStrengthIndex[k] = pairStrengthIndex[k] || {};
    const prev = cur[r.productKey];
    if (!prev || STRENGTH[r.strength].rank < STRENGTH[prev].rank) cur[r.productKey] = r.strength;
  });

  const engineLinks = (o) => {
    o.issueKey = o.issueEn || null;
    const byProduct = (o.crop && o.issueEn && pairStrengthIndex[U(o.crop) + '|' + U(o.issueEn)]) || {};
    o.productLinks = o.adamaProducts.map((name) => {
      const strength = byProduct[U(name)] || 'LABEL_CHECK_NEEDED';
      return {
        name, product: name, strength,
        strengthRank: STRENGTH[strength].rank,
        resolvedThrough: byProduct[U(name)]
          ? 'V21 label use pair · ' + o.crop + ' x ' + o.issueEn
          : 'NO_PAIR_FOR_THIS_CROP_AND_TARGET',
        inRegistry: !!productByKey[U(name)],
        absenceRule: ABSENCE_RULE_TEXT,
      };
    });
    o.verifiedProductCount = o.productLinks.filter((l) => l.strength === 'VERIFIED_LABEL_MATCH').length;
  };

  opportunities.records.forEach((o) => {
    if (o.productLinkState !== undefined && o.productLinkState !== null) { engineLinks(o); return; }
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

  /* ---- AGROMET · CROSSINGS ---------------------------------------------
     No upstream table yet. An empty collection is a valid answer and is
     reported as empty rather than filled with invented rows. */
  const agrometConditions = build('agrometConditions', [
    V21('agrometConditions', (a) => Object.assign(v21Env(a), {
      id: a.ID,
      observationClass: v21S(a.OBSERVATION_CLASS),
      confidence: v21S(a.CONFIDENCE), sourceScope: v21S(a.SOURCE_SCOPE),
      region: regionsOfIds(a.REGION_IDS)[0] || null,
      regions: regionsOfIds(a.REGION_IDS),
      crops: cropsOfIds(a.CROP_IDS),
      whatItIs: v21Text(a, 'WHAT_IT_IS'),
      proves: v21Text(a, 'WHAT_IT_PROVES'),
      notProves: v21Text(a, 'WHAT_IT_DOES_NOT_PROVE'),
    }), (r) => (!r.id ? 'no ID' : null)),
  ], 'agrometeorological observations, each with the scope its own source declares');
  const clientSafeCrossings = build('clientSafeCrossings', [
    V21('clientSafeCrossings', (c) => Object.assign(v21Env(c), {
      id: c.ID, crossingType: v21S(c.CROSSING_TYPE),
      crop: cropOfId(c.CROP_ID), cropId: v21S(c.CROP_ID),
      /* A crossing states its geographic claim and the scope of that claim
         separately, because 'observed in Veneto' and 'true of Italy' are not
         the same sentence. Neither is ever widened here. */
      geographicClaim: v21S(c.GEOGRAPHIC_CLAIM),
      geographicClaimScope: v21S(c.GEOGRAPHIC_CLAIM_SCOPE),
      coverageProvinces: A(c.GEOGRAPHIC_COVERAGE_PROVINCES),
      coverageRegions: A(c.GEOGRAPHIC_COVERAGE_REGIONS),
      supportingIds: A(c.SUPPORTING_IDS),
      allSupportClientSafe: c.ALL_SUPPORT_CLIENT_SAFE === true,
      renderableWithMethod: c.RENDERABLE_WITH_METHOD === true,
      invariantsProven: A(c.INVARIANTS_PROVEN),
      labelLinkStrengths: c.LABEL_LINK_STRENGTHS || null,
      letsYouAsk: v21Text(c, 'WHAT_IT_LETS_YOU_ASK'),
      notProves: v21Text(c, 'WHAT_IT_DOES_NOT_PROVE'),
    }), (r) => (!r.id ? 'no ID' : null)),
  ], 'audited cross-domain crossings; each one carries the method that makes it readable');

  /* ---- THE ACTIVE-SUBSTANCE LAYER · new in V2.1 -------------------------
     A product is a formulation; a substance is what acts. The portal has always
     shown the first and inferred the second from a free-text column. The V2.1
     package makes the substance an ENTITY with its own identity (CAS, CIPAC),
     its own mode-of-action codes (HRAC / FRAC / IRAC) and its own European
     regulatory state — which is what lets an expiry date in Brussels be joined
     to an Italian label without either one pretending to be the other.

         A EUROPEAN APPROVAL STATE IS NOT ITALIAN MARKETABILITY.
         The two facts touch. They are not the same fact, and the collection
         that holds them keeps them in different fields on purpose. */
  const activeIngredients = build('activeIngredients', [
    V21('activeIngredients', (a) => Object.assign(v21Env(a), {
      id: a.ID, name: v21S(a.NAME), normalizedName: v21S(a.NORMALIZED_NAME),
      italianRegistrations: N(a.ITALIAN_REGISTRATION_COUNT),
      hrac: A(a.HRAC), hracWssa: A(a.HRAC_WSSA), chemicalFamily: v21S(a.CHEMICAL_FAMILY),
      irac: A(a.IRAC), iracSubgroup: v21S(a.IRAC_SUBGROUP),
      frac: A(a.FRAC), fracVersion: v21S(a.FRAC_SOURCE_VERSION),
      moaState: v21S(a.MOA_STATE),
      moaLabel: [A(a.HRAC).join('/'), A(a.FRAC).join('/'), A(a.IRAC).join('/')].filter(Boolean).join(' + ') || null,
      euState: v21S(a.EU_STATE),
      euApproval: v21S(a.EU_DATE_OF_APPROVAL),
      euExpiry: v21S(a.EU_EXPIRATION_OF_APPROVAL),
      euExpiryISO: isoOf(v21S(a.EU_EXPIRATION_OF_APPROVAL)),
      daysToEuExpiry: daysFrom(isoOf(v21S(a.EU_EXPIRATION_OF_APPROVAL))),
      euCelex: v21S(a.EU_CELEX), euRenewalState: v21S(a.EU_RENEWAL_STATE),
      cas: v21S(a.CAS), cipac: v21S(a.CIPAC),
      notProves: v21Text(a, 'WHAT_IT_DOES_NOT_PROVE'),
    }), (r) => (!r.id ? 'no ID' : !r.name ? 'no substance name' : null)),
  ], 'active substances as entities, with mode of action and European state');

  const productActiveIngredients = build('productActiveIngredients', [
    V21('productActiveIngredients', (r) => Object.assign(v21Env(r), {
      id: r.ID, productId: v21S(r.PRODUCT_ID), product: v21S(r.PRODUCT_NAME),
      reg: v21S(r.REGISTRATION_NUMBER),
      activeIngredientId: v21S(r.ACTIVE_INGREDIENT_ID),
      activeIngredient: v21S(r.ACTIVE_INGREDIENT),
      isMixtureComponent: r.IS_MIXTURE_COMPONENT === true,
      componentsInProduct: N(r.COMPONENTS_IN_PRODUCT),
      catalogProducts: A(r.COMMERCIAL_CATALOG_PRODUCTS),
      notProves: v21Text(r, 'WHAT_IT_DOES_NOT_PROVE'),
    }), (r) => (!r.id ? 'no ID' : null)),
  ], 'which substance is in which product; a mixture declares how many components it has');

  /* The dated European facts. Separate from regulatoryFuture, which holds the
     OBSERVATIONS about the regulatory future: a date and a reading of a date
     are different rows and must be countable separately. */
  const regulatoryFutureFacts = build('regulatoryFutureFacts', [
    V21('regulatoryFutureFacts', (r) => Object.assign(v21Env(r), {
      id: r.ID,
      activeIngredient: v21S(r.ACTIVE_INGREDIENT),
      activeIngredientId: v21S(r.ACTIVE_INGREDIENT_ID),
      euState: v21S(r.EU_STATE),
      euExpiry: v21S(r.EU_EXPIRATION_OF_APPROVAL),
      euExpiryISO: isoOf(v21S(r.EU_EXPIRATION_OF_APPROVAL)),
      daysToExpiry: daysFrom(isoOf(v21S(r.EU_EXPIRATION_OF_APPROVAL))),
      euCelex: v21S(r.EU_CELEX),
      italianRegistrations: A(r.ITALIAN_REGISTRATIONS),
      italianRegistrationCount: N(r.ITALIAN_REGISTRATION_COUNT),
      catalogProducts: A(r.COMMERCIAL_CATALOG_PRODUCTS),
      verifiedLabelCrops: A(r.VERIFIED_LABEL_CROPS),
      verifiedLabelCropsState: v21S(r.VERIFIED_LABEL_CROPS_STATE),
      /* The package refuses to turn a date into a risk or an opportunity, and
         publishes both refusals as explicit false. Restating them as booleans
         here is what stops a screen deciding for itself. */
      isOpportunity: r.IS_OPPORTUNITY === true,
      isRisk: r.IS_RISK === true,
      proves: v21Text(r, 'WHAT_IT_PROVES'),
      notProves: v21Text(r, 'WHAT_IT_DOES_NOT_PROVE'),
    }), (r) => (!r.id ? 'no ID' : null)),
  ], 'published European approval dates for substances Italian ADAMA labels contain');

  /* The 122 regional bulletins. The seven per-crop readings in
     currentFieldSignals are a SYNTHESIS of these; both are kept, because a
     synthesis that cannot be opened is an assertion. */
  const fieldBulletins = build('fieldBulletins', [
    V21('fieldBulletins', (b) => Object.assign(v21Env(b), {
      id: b.ID, title: v21S(b.BULLETIN_TITLE), number: v21S(b.BULLETIN_NUMBER),
      phenologicalStage: v21S(b.PHENOLOGICAL_STAGE_DECLARED),
      pestsCited: A(b.PESTS_AND_DISEASES_CITED),
      cropState: v21S(b.CROP_STATE), cropsDeclared: A(b.CROPS_DECLARED),
      crops: cropsOfIds(b.CROP_IDS),
      issues: issuesOfIds(b.ISSUE_IDS).map((i) => i.it),
      region: regionsOfIds(b.REGION_IDS)[0] || null,
      regions: regionsOfIds(b.REGION_IDS),
      /* A bulletin covers a province, an areal or a region, and saying which is
         the whole of R1. GEOGRAPHY_STATE is the package's own verdict and is
         never widened: a province is not its region. */
      provinceIds: A(b.PROVINCE_IDS), arealIds: A(b.AREAL_IDS),
      geographyState: v21S(b.GEOGRAPHY_STATE),
      regionRepresents: v21S(b.REGION_REPRESENTS),
      citation: v21S(b.CITATION),
      observationClass: v21S(b.OBSERVATION_CLASS),
      guidance: v21Text(b, 'INTERVENTION_GUIDANCE'),
      date: v21S(b.REFERENCE_DATE), dateISO: isoOf(v21S(b.REFERENCE_DATE)),
      daysFromRef: daysFrom(isoOf(v21S(b.REFERENCE_DATE))),
    }), (r) => (!r.id ? 'no ID' : null)),
  ], 'regional phytosanitary bulletins as read; the geographic scope is the source’s own');

  /* Crop economics by geography and year. NOT the label reach in
     cropEconomicWeight and NOT the price series in marketObservations: a third
     fact, kept apart from both so no screen can add them up. */
  const cropEconomics = build('cropEconomics', [
    V21('cropEconomics', (c) => Object.assign(v21Env(c), {
      id: c.ID, cropLiteral: v21S(c.CROP_LITERAL), cropCode: v21S(c.CROP_CODE),
      crop: cropsOfIds(c.CROP_IDS)[0] || null,
      geography: v21S(c.GEOGRAPHY), geographyCode: v21S(c.GEOGRAPHY_CODE),
      geographyLevel: v21S(c.GEOGRAPHY_LEVEL),
      region: regionsOfIds(c.REGION_IDS)[0] || null,
      year: N(c.YEAR), indicator: v21S(c.INDICATOR),
      value: N(c.VALUE), unit: v21S(c.UNIT),
      isDerived: c.IS_DERIVED_BY_SINTONIA === true,
      derivation: v21S(c.DERIVATION_FORMULA),
      dataset: v21S(c.DATASET), observationClass: v21S(c.OBSERVATION_CLASS),
      caveat: v21Text(c, 'CAVEAT'),
    }), (r) => (!r.id ? 'no ID' : null)),
  ], 'crop area and production by geography and year, as the statistical office publishes it');

  /* ---- RELATIONSHIPS · the generic graph -------------------------------
     A crossing exists only when a normalized relationship supports it. Sharing
     a crop name is not a relationship, so nothing is generated here from a
     name match. */
  const relationships = build('relationships', [
    V21('relationships', (r) => Object.assign(v21Env(r, P.REAL_DERIVED), {
      id: r.ID, crossingType: v21S(r.CROSSING_TYPE),
      crop: cropOfId(r.CROP_ID), cropId: v21S(r.CROP_ID),
      links: A(r.LINKS),
      renderableWithMethod: r.RENDERABLE_WITH_METHOD === true,
      from: r.ID, fromKind: 'crossing',
      to: v21S(r.CROP_ID), toKind: 'crop',
      kind: v21S(r.CROSSING_TYPE), evidence: 'declared LINKS',
    }), (r) => (!r.id ? 'no ID' : null)),
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
  /* UNA RIGA SENZA NOME SEMBRA UN GUASTO, NON UN RECORD.
     Ottanta osservazioni di mercato non hanno ne prodotto ne piazza — sono i
     record senza prezzo — e la riga d'archivio restava del tutto vuota: nessun
     titolo, nessuna fonte. Il lettore vedeva una tabella rotta. Hanno pero una
     coltura, e il fatto che NON portino un prezzo e esso stesso l'informazione
     da mostrare, non da nascondere. */
  marketObservations.records.forEach((m) => push('MARKET', m.id,
    [m.product, m.market].filter(Boolean).join(' · ')
      /* Niente prosa italiana nel modello: la colonna TIPO dice gia
         «Osservazione di mercato» nella lingua giusta. Qui va cio che il
         record HA — la coltura, altrimenti il proprio identificativo, che e
         reale e apre la riga — mai una frase inventata. */
      || m.cropKey || m.id, m.publicationDate, null, null, null, null, m.provenance,
    { sourceId: m.sourceId, series: m.product, market: m.market, cropKey: m.cropKey }));
  competitorActivities.records.forEach((a) => push('COMPETITOR', a.id, [a.displayName, a.type].filter(Boolean).join(' · '), a.startDate, a.url, a.crops[0], CROP_BY_LATIN[U(a.crops[0])] ? 'LATIN' : GENERIC_CROP_TERMS[U(a.crops[0])] ? 'GENERIC_IT' : 'UNMAPPED', a.issues[0], a.provenance,
    { sourceId: ARCHIVE_PLATFORM_SOURCE[U(a.platform)] || null, company: a.company, competitorProducts: a.products, platform: a.platform }));
  publicVoices.records.forEach((v) => push('VOICE', v.id,
    v.title || v.person || v.channel || v.organization
      || (sourceById[U(v.sourceId)] || {}).name
      || v.id, v.date, v.sourceUrl, v.crop, 'UPPER_CODE', v.issue, v.provenance,
    { sourceId: v.sourceId, platform: v.platform }));
  futureEvents.records.forEach((e) => push('EVENT', e.id, e.name, e.date, e.url, null, null, null, e.provenance,
    { sourceId: null, location: e.location, organizer: e.organizer }));
  news.records.forEach((n) => push('NEWS', n.id, n.title, n.date, n.url, n.crop, 'UPPER_CODE', n.issue, n.provenance,
    { sourceId: n.publisherSourceId, publisher: n.publisher }));
  cropWindows.records.forEach((w) => push('WINDOW', w.windowId, [w.issue, w.region].filter(Boolean).join(' · '), w.startDate, null, w.crop, 'CANONICAL', w.issue, w.provenance,
    { sourceId: A(w.sourceIds)[0] || null, legacyCaseId: w.legacyCaseId, region: w.region }));
  resistance.records.forEach((r) => push('RESISTANCE', r.id, r.species, r.firstCaseYear, r.url, r.crop, 'UPPER_CODE', null, r.provenance,
    { sourceId: r.sourceId, authority: r.authority }));
  /* CENTOVENTIDUE BOLLETTINI CHE NESSUNA SCHERMATA APRIVA.
     fieldBulletins esisteva nel modello, contava nel pannello di stato e non
     compariva in nessuna vista, in nessuna riga d'archivio e in nessun indice
     di ricerca: informazione canonica, con regione, data e fonte, impossibile
     da raggiungere. L'archivio e per definizione l'indice sopra il modello, e
     un bollettino ha esattamente la forma che l'archivio indicizza — titolo,
     data, regione, coltura, fonte. Non serviva una schermata nuova: serviva
     smettere di saltarli.

         UN DATO CHE STA NEL MODELLO E NON SI PUO APRIRE
         NON E STATO CONSEGNATO. */
  /* Le SETTE letture di campo (IT-WIN-001..007) sono un universo separato
     dalle 29 finestre canoniche e non devono mai essere confuse con esse — per
     questo entrano con un tipo PROPRIO, FIELD_SIGNAL, e non come WINDOW. */
  currentFieldSignals.records.forEach((w) => push('FIELD_SIGNAL', w.id,
    [w.issue, w.region].filter(Boolean).join(' · ') || w.id,
    w.regulatoryAct || null, A(w.sourceUrls)[0] || null,
    w.cropCanonical || w.crop || null, 'CANONICAL', w.issue || null, w.provenance,
    { sourceId: A(w.sourceIds)[0] || null, region: w.region }));
  fieldBulletins.records.forEach((b) => push('BULLETIN', b.id,
    b.title || [b.number, b.region].filter(Boolean).join(' · ') || b.id,
    b.date, A(b.sourceUrls)[0] || null,
    A(b.crops)[0] || A(b.cropKeys)[0] || null, 'CANONICAL', A(b.issues)[0] || null, b.provenance,
    { sourceId: A(b.sourceIds)[0] || null, region: b.region }));

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
    cropWindows, currentFieldSignals, cropEconomicWeight, fieldBulletins,
    windowCalendarRows, windowsByRegion,
    /* market */
    marketObservations, marketByCrop, marketSummaries, cropEconomics,
    /* competitor */
    competitorActivities, competitorCompanies, competitorProducts,
    competitorCropDensity, competitorIssueDensity, competitorMatrix,
    competitorWindowMoments, communicationAxis,
    /* science */
    scienceRecords, researchers, scienceThemes, resistance, scienceInstitutions,
    /* voices and people */
    publicVoices, publicChannels, publicPeople, people,
    /* future */
    regulatoryFuture, regulatoryFutureFacts, agrometConditions, futureEvents,
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
    cropWindows: 'Finestre colturali canoniche', currentFieldSignals: 'Letture di campo e atti regionali',
    cropEconomicWeight: 'Portata delle etichette per coltura',
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
    regulatoryFuture: 'Scadenze di autorizzazione', agrometConditions: 'Condizioni agrometeo',
    futureEvents: 'Eventi di settore', opportunities: 'Convergenze a monte', futureSignals: 'Segnali futuri',
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
        /* `keyed` is the denominator that matters for an enum table: a row that
           does not carry the key was never a candidate. 158 of the 189 V2.1
           sources declare no TYPE, so measuring the group table against all 189
           would report a broken join every time the upstream adds a source
           without one — which is a different defect, and one this number would
           then hide. */
        sourceGroup: Object.assign(
          rate(sources.count, sources.records.filter((r) => r.group).length),
          { keyed: sources.records.filter((r) => r.type).length }
        ),
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
    ['sources', sources.records, ['role', 'limitations']],
  ];
  NARRATIVE_FIELDS.forEach(([family, recs, fields]) =>
    fields.forEach((f) => noteNarrative(family, f, recs.filter((r) => r[f] && r[f].state === KNOWLEDGE.NOT_APPROVED_FOR_DISPLAY).length)));

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
  /* i bollettini entrano anche nella ricerca: erano l'unica famiglia canonica
     che nessuna query poteva raggiungere. La rotta e l'archivio, che e dove
     ora vivono, con il proprio id gia selezionato. */
  currentFieldSignals.records.forEach((w) => idx('fieldSignal', 'FIELD_SIGNAL', w.id,
    [w.issue, w.region].filter(Boolean).join(' · ') || w.id,
    [w.issue, w.issueEn, w.region, cropTerms([w.cropCanonical || w.crop]), w.id],
    'archive', w.region, { aType: 'FIELD_SIGNAL', archiveQuery: w.id }, w.provenance));
  fieldBulletins.records.forEach((b) => idx('bulletin', 'FIELD_BULLETIN', b.id,
    b.title || b.id,
    [b.title, b.region, A(b.regions), cropTerms(A(b.crops)), A(b.issues), b.number, b.id],
    'archive', b.region, { aType: 'BULLETIN', archiveQuery: b.id }, b.provenance));
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
    regulatoryLinks: ['cropKey', 'target', 'labelUrl', 'timing'],
    regulatoryFuture: ['expiryISO', 'holder', 'status'],
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
    version: '3.1',
    compiled: REFERENCE_DATE,

    /* one clock */
    referenceDate: REFERENCE_DATE, REF, daysFrom, asDate, isoOf, fmtDate,

    /* provenance vocabulary */
    PROVENANCE: P, PRECEDENCE, provOf, isDemo,
    STRENGTH, ABSENCE_RULE,
    KNOWLEDGE, narrative,
    CATEGORY_UI, categoryOf, categoryFromProducts,
    adamaRelevance, geographyLabel, RELEVANCE_LABEL, RELEVANCE_WHY, rtvEligibility, RTV_BLOCKER_LABEL,

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

    /* data */
    collections, counts, totals, provenanceSummary, provenanceTotals, joinHealth,
    searchIndex, search, searchGrouped, TERMS, cropTerms, issueTerms,
    products, productByKey, findProduct, strengthFor,
    productRelationships, activeIngredients, productActiveIngredients,
    regulatoryFutureFacts, fieldBulletins, cropEconomics,
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
      registeredSources: Object.keys(RAW).filter((k) => RAW[k] && (Array.isArray(RAW[k]) ? RAW[k].length : Object.keys(RAW[k]).length)),
      handoffV21Present: !!RAW.HANDOFF_V21,
      families: primaryKeys,
      validationReport,
    },
    validationReport,
  };
})();
