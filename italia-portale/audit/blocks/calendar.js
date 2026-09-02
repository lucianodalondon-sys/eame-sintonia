    // ---- crop calendar · rolling canonical timeline · preparation clock
    /* §7 · THE ROW UNIVERSE MOVED. This screen used to draw 40 crop x region rows
       out of the fixture crop calendar (CROP_CAL) — a table of seasonal norms carrying invented hectares,
       per-region day offsets of -14..+7 days and a roll-forward that manufactured a
       2027 occurrence for every window whose 2026 one had passed. The universe is
       now AM.collections.windowCalendarRows: 29 audited windows over 10 crops and 9 regions.
       MEASURED on the reference date 2026-09-02:
         status      6 WINDOW_OPEN · 16 WINDOW_CLOSED · 2 NEXT_CYCLE · 5 DATE_UNKNOWN
         dates       24/29 have START_DATE and END_DATE; 5 have neither
         dateState   24 EXPECTED_NORM · 5 DATE_TO_CONFIRM
         products    12/29 carry a VERIFIED label match (6 distinct product names)
         regulatory  2/29 join a regional act (IT-WIN-0001 Veneto, IT-WIN-0008 Piemonte)
         observed    0/29 — CROP_STAGE and ISSUE_STAGE are null on all 29
       Presentation still owns geometry (month ticks, pixel position, lane width,
       ordering, days-remaining). It no longer owns the agronomic state: every chip
       on this screen is CURRENT_STATUS as upstream published it. */
    const calIT = s.lang !== 'en';
    const LC = (it, en) => calIT ? it : en;
    /* windowCalendarRows is the model's own thin re-shape of the canonical windows,
       built for exactly this screen; cropWindows is the fallback if the projection
       is ever absent. SOURCE_IDS is not carried on the projection, so the two
       drawer lines that report it read it off the canonical record. */
    const calWins = APP0 ? ((APP0.windowCalendarRows && APP0.windowCalendarRows.records) || APP0.cropWindows.records) : [];
    const calSrcIds = {};
    if (APP0) APP0.cropWindows.records.forEach(x => { calSrcIds[x.windowId] = x.sourceIds || []; });

    /* ---- geometry only. Rule 7 explicitly allows all of this. ---- */
    const MIx = (y, m) => (y - 2026) * 12 + m;
    const dIM = (y, m) => new Date(y, m + 1, 0).getDate();
    /* ONE clock. No fallback Date literal: with no model there are no rows to place. */
    const CAL_TODAY = AM ? AM.REF : null;
    const START = s.calStart, HZ = s.calH;
    const posOf = (dt) => (MIx(dt.getFullYear(), dt.getMonth()) + (dt.getDate() - 1) / dIM(dt.getFullYear(), dt.getMonth()) - START) / HZ;
    const addD = (dt, n) => new Date(dt.getFullYear(), dt.getMonth(), dt.getDate() + n);
    const dOf = (iso) => (AM && iso) ? AM.asDate(iso) : null;
    const clipB = (d1, d2) => { const l = posOf(d1), r = posOf(d2); if (r <= 0.002 || l >= 0.998) return null; const cl2 = Math.max(0, l), cr = Math.min(1, r); if (cr - cl2 < 0.0015) return null; return { left: (cl2 * 100).toFixed(2) + '%', width: ((cr - cl2) * 100).toFixed(2) + '%' }; };

    /* ---- THE BUSINESS PREPARATION CLOCK · SINTONIA INTERPRETATION ----------
       The legacy PREP_LEAD constant (90) and the six department offsets were printed as bare dates
       ("prepare from 12 Mar", "REGULATORY / PORTFOLIO 15 Nov -> 13 Jan") with no
       qualifier. When a channel actually buys is NOT observable from outside — no
       source in the canonical set, the ingest or the catalog contains it. The
       feature stays, because an agronomic clock and a business clock are the point
       of the product; what changes is that every consumer now carries the label and
       every offset is anchored on the canonical START_DATE. Rows without a start
       date (5/29 — the projection lists them under preparation.omittedWindows) get
       no preparation bar and no department plan at all.
       The constants now live in AM.preparation, provenance SINTONIA_INTERPRETATION,
       observable false. The view reads them; it does not own them. */
    const PREP = (AM && AM.preparation) || { leadDays: 90, departments: [], basis: '' };
    const CW_LEAD = PREP.leadDays;
    const CW_INTERP = LC('INTERPRETAZIONE SINTONIA', 'SINTONIA INTERPRETATION');
    const CW_INTERP_LONG = LC(
      PREP.basis || 'Regola di pianificazione Sintonia · non è un fatto osservato e non deriva da alcuna fonte esterna',
      'Sintonia planning rule · not an observed fact and not derived from any external source');
    /* Order is presentation: earliest department first, so the plan reads as a ramp. */
    const CW_DEPTS = (PREP.departments || []).slice().sort((a, b) => a.fromDays - b.fromDays);
    const deptName = (k) => L(k === 'SALES / RTV' ? 'FIELD SALES' : k);

    /* ---- canonical vocabulary -> screen labels ---- */
    const wsUI = (r) => (r && r.ui && r.ui.status) || { color: '#978B87', text: '#B1A9A7', rank: 9 };
    const pst = (k) => (T.PSTATE && T.PSTATE[k]) || String(k || '').replace(/_/g, ' ');
    const COV_LAB = {
      FIELD_OBSERVED: LC('OSSERVATO IN CAMPO', 'FIELD OBSERVED'),
      REGULATORY_READ: LC('ATTO NORMATIVO LETTO', 'REGULATORY ACT READ'),
      EXPECTED_NORM_ONLY: LC('SOLO NORMA ATTESA', 'EXPECTED NORM ONLY'),
    };
    /* STATUS_REASON is upstream's own one-line explanation of its own verdict. It
       arrives in English on 29/29 rows and is not a public quote, a source title or
       a product name, so rule 11 asks for an Italian reading of it. The five
       measured strings are mapped exactly; anything new falls through verbatim
       rather than being paraphrased. */
    const REASON_IT = {
      'Reference date 2026-09-02 falls after END_DATE': 'La data di riferimento 2026-09-02 cade dopo END_DATE',
      'Reference date falls inside the expected window · NOT an observation': 'La data di riferimento cade dentro la finestra attesa · NON è un\'osservazione',
      'Reference date falls before START_DATE': 'La data di riferimento cade prima di START_DATE',
      'No biological calendar entry for this issue': 'Nessuna voce di calendario biologico per questa avversità',
      'The 2026 flowering window has passed; next relevant window is the 2027 campaign': 'La finestra di fioritura 2026 è passata; la prossima finestra utile è la campagna 2027',
    };
    const reasonL = (v) => (calIT && REASON_IT[v]) ? REASON_IT[v] : (v || '');
    /* REGULATORY_ACT_STATE is an enum written in the analyst's Portuguese working
       vocabulary (measured 3 values over the 5 upstream regulatory rows). The act
       name itself is an official title and is never translated; the state is. */
    const ACT_STATE_LAB = {
      PRIMARY_SOURCE_READ: LC('fonte primaria letta', 'primary source read'),
      JA_NO_ACERVO: LC('già nell’archivio Sintonia', 'already in the Sintonia archive'),
      CITADO_EM_FONTE_SECUNDARIA: LC('citato in una fonte secondaria', 'cited in a secondary source'),
    };
    const actStateL = (v) => ACT_STATE_LAB[v] || String(v || '').replace(/_/g, ' ').toLowerCase();


    /* ---- one core per canonical window. No second source of timing truth. ---- */
    const coreOf = (r) => {
      const a = dOf(r.startDate), b = dOf(r.endDate);
      return {
        w: r, windowId: r.windowId, crop: r.crop, region: r.region, issue: r.issue,
        a, b, hasDates: !!(a && b),
        status: r.status, statusReason: r.statusReason,
        open: r.status === 'WINDOW_OPEN',
        rank: wsUI(r).rank,
        color: wsUI(r).color, text: wsUI(r).text,
        cat: (r.ui && r.ui.color) || '#8F8886',
        verified: (r.verifiedProducts || []).slice(),
        reg: r.regulatory || null,
      };
    };
    const ALL_CORES = calWins.map(coreOf);

    /* ---- KPI row · the four canonical statuses, plus two context counters ----
       The old five buckets (ACT NOW / ACTIVATE / PREPARE / PLAN / NEXT CYCLE) were
       computed here from a day count, which rule 7 forbids outright, and were also
       arithmetically broken: every closed and every date-unknown window landed on
       day 0 and was reported as ACT NOW (21 of 29). Three of the four honest
       counters are unflattering. That is the picture on 2026-09-02. */
    const CW_BUCKETS = ['WINDOW_OPEN', 'WINDOW_CLOSED', 'NEXT_CYCLE', 'DATE_UNKNOWN'];
    const bucketN = (k) => ALL_CORES.filter(x => x.status === k).length;
    /* The status tone comes off the model's own ui.status token, read from any record
       that carries the status; a bucket upstream never used falls back to neutral. */
    const CW_TONE = {};
    ALL_CORES.forEach(x => { if (!CW_TONE[x.status]) CW_TONE[x.status] = x.color; });
    const calKpis = CW_BUCKETS.map(k => ({
      label: wst(k), n: bucketN(k), color: CW_TONE[k] || '#978B87',
      on: s.calBucket === k, bg: s.calBucket === k ? 'rgba(0,152,69,0.16)' : '#1C1817',
      border: s.calBucket === k ? '#009845' : 'rgba(203,197,195,0.10)',
      go: () => this.setState({ calBucket: s.calBucket === k ? '' : k, calRegion: null }),
    })).concat([
      { label: pst('VERIFIED_LABEL_MATCH'), n: ALL_CORES.filter(x => x.verified.length).length, color: '#00B152', on: false, bg: '#1C1817', border: 'rgba(203,197,195,0.10)', go: () => this.setState({ calBucket: '' }) },
      { label: COV_LAB.EXPECTED_NORM_ONLY, n: calWins.filter(r => r.coverageState === 'EXPECTED_NORM_ONLY').length, color: '#978B87', on: false, bg: '#1C1817', border: 'rgba(203,197,195,0.10)', go: () => this.setState({ calBucket: '' }) },
    ]);
    /* Bound at markup 591 in place of t.cwBucketNote, whose text still describes the
       40-row fixture. See the report: the markup rebind is the requested edit. */
    const calKpiNote = LC(
      'I primi quattro gruppi sono gli stati pubblicati a monte (CURRENT_STATUS), sono disgiunti e sommano a ' + ALL_CORES.length + ' finestre canoniche su ' + [...new Set(ALL_CORES.map(x => x.crop))].length + ' colture e ' + [...new Set(ALL_CORES.map(x => x.region))].length + ' regioni. Il portale non calcola mai lo stato agronomico da un conteggio di giorni. Gli ultimi due sono conteggi di contesto sulle stesse righe.',
      'The first four buckets are the statuses published upstream (CURRENT_STATUS). They are disjoint and sum to ' + ALL_CORES.length + ' canonical windows across ' + [...new Set(ALL_CORES.map(x => x.crop))].length + ' crops and ' + [...new Set(ALL_CORES.map(x => x.region))].length + ' regions. The portal never computes an agronomic state from a day count. The last two are context counts over the same rows.');
    /* Bound at markup 714 in place of t.cwFootNote (see report; needs one added key
       in the props object). The old footnote described lanes that no longer exist. */
    const calFootNote = LC(
      'Ogni stato — finestra aperta, chiusa, prossimo ciclo, data da confermare — è pubblicato a monte e mai calcolato qui. Le date provengono da START_DATE / END_DATE canoniche: ' + calWins.filter(r => r.hasDates).length + ' finestre su ' + calWins.length + ' ne hanno, le altre ' + calWins.filter(r => !r.hasDates).length + ' mostrano DATA DA CONFERMARE e non disegnano alcuna barra. Nessuno stadio colturale è osservato: 0 finestre su ' + calWins.length + ' hanno CROP_STAGE. La preparazione commerciale e il piano dei reparti sono un\'interpretazione Sintonia, non un fatto osservato. Nessuna cifra di ettari, ricavo o domanda compare qui: non è osservabile da fonti esterne.',
      'Every state — window open, closed, next cycle, date to confirm — is published upstream and never computed here. Dates come from the canonical START_DATE / END_DATE: ' + calWins.filter(r => r.hasDates).length + ' of ' + calWins.length + ' windows have them, the other ' + calWins.filter(r => !r.hasDates).length + ' read DATE TO CONFIRM and draw no bar. No crop stage is observed: 0 of ' + calWins.length + ' windows carry CROP_STAGE. Business preparation and the department plan are a Sintonia interpretation, not an observed fact. No hectare, revenue or demand figure appears here: none of it is externally observable.');

    /* ---- day labels · arithmetic on supplied dates only ---- */
    const dayNum = (c) => c.status === 'WINDOW_OPEN' ? c.w.daysToEnd
      : c.status === 'NEXT_CYCLE' ? c.w.daysToStart
        : null;
    /* Days remaining and days-to-open are arithmetic on dates upstream supplied, so
       rule 7 allows them — but the unit has to say WHICH count it is, because the
       same slot serves an open window and a next-cycle one. */
    const dayLab = (c) => {
      const n = dayNum(c);
      if (n == null) return '—';
      return c.status === 'WINDOW_OPEN' ? n + LC(' g rimanenti', ' d left') : n + LC(' g all’apertura', ' d to open');
    };
    /* The preparation anchor. Null whenever the window has no start date. */
    const prepStart = (c) => c.a ? addD(c.a, -CW_LEAD) : null;
    const prepLineOf = (c) => c.a
      ? CW_INTERP + ' · ' + LC('preparazione da', 'preparation from') + ' ' + D.fmt(prepStart(c)) + ' · ' + CW_LEAD + LC('g', 'd')
      : CW_INTERP + ' · ' + LC('nessuna data di inizio, nessun ancoraggio', 'no start date, nothing to anchor on');

    /* ---- MOMENTS · only windows that still lie ahead of the reference date ----
       An already-closed window is not a "next commercial moment". Pool measured:
       6 WINDOW_OPEN + 2 NEXT_CYCLE = 8 rows. */
    const momentPool = ALL_CORES
      .filter(c => (c.status === 'WINDOW_OPEN' || c.status === 'NEXT_CYCLE'))
      .filter(c => !s.calBucket || c.status === s.calBucket)
      .sort((x, y) => (x.rank - y.rank) || ((dayNum(x) == null ? 9e3 : dayNum(x)) - (dayNum(y) == null ? 9e3 : dayNum(y))));
    const calMoments = momentPool.slice(0, 6).map(c => ({
      days: dayLab(c), crop: c.crop, cropL: cl(c.crop), issueL: il(c.issue), region: c.region, issue: c.issue,
      state: wst(c.status), color: c.color, ink: D.inkOn(c.color),
      prepLine: prepLineOf(c),
      /* kept for the un-migrated markup at 601; both strings carry the fence */
      prepFrom: c.a ? D.fmt(prepStart(c)) + ' · ' + CW_INTERP : '—',
      windowFrom: c.a ? D.fmt(c.a) : T.wDateToConfirm,
      go: () => this.setState({ calCrop: c.crop, calRegion: c.windowId, calStart: c.a ? Math.max(-6, Math.min(24, MIx(c.a.getFullYear(), c.a.getMonth()) - 4)) : s.calStart }),
    }));

    /* ---- the selected crop ---- */
    const CROP_ORDER = [];
    ALL_CORES.forEach(c => { if (CROP_ORDER.indexOf(c.crop) < 0) CROP_ORDER.push(c.crop); });
    const calCropKey = CROP_ORDER.indexOf(s.calCrop) >= 0 ? s.calCrop : (CROP_ORDER[0] || s.calCrop);
    const cropCores = ALL_CORES.filter(c => c.crop === calCropKey);
    /* Legend swatch tone: the category of the selected crop's leading window. */
    const calCatColor = (cropCores[0] && cropCores[0].cat) || '#9D1D96';
    /* Market Pulse temperature came from the editorial market fixture, which the
       product law is stripping back to labels. It is not read here any more; the
       four props that consumed it are unbound in the markup, so nothing on screen
       loses a value. */
    const calMarket = null;

    /* ---- one timeline row per canonical window of the selected crop ---- */
    const calRowsAll = cropCores.map(c => {
      const r = c.w;
      const issueB = (c.hasDates ? [clipB(c.a, c.b)] : []).filter(Boolean).map(b => Object.assign({}, b, {
        bg: c.cat, color: D.inkOn(c.cat), fs: '11px', fw: 700, radius: '3px', ink: D.inkOn(c.cat),
        text: il(c.issue),
        title: il(c.issue) + ' · ' + D.fmt(c.a) + ' → ' + D.fmt(c.b) + ' · ' + dst(r.dateState) + ' · ' + wst(c.status),
      }));
      /* The verified-label badge rides the canonical window because that is the only
         span upstream published. Rule 10: it states a LABEL VERDICT, never a spray
         recommendation, and the title says so. 12 of 29 rows carry it. */
      const adamaLabel = c.verified.length ? c.verified.join(' · ') : '';
      const adamaB = (c.verified.length && c.hasDates ? [clipB(c.a, c.b)] : []).filter(Boolean).map(b => Object.assign({}, b, {
        bg: '#FFFFFF', color: '#231F20', fs: '12px', fw: 700, radius: '3px', ink: '#231F20',
        text: adamaLabel + ' · ' + pst('VERIFIED_LABEL_MATCH'),
        title: pst('VERIFIED_LABEL_MATCH') + ' · ' + adamaLabel + ' · ' + LC('verdetto dell\'audit delle etichette per questa coltura × avversità; la barra segue la finestra canonica, non un\'indicazione d\'uso', 'label-audit verdict for this crop × issue; the bar follows the canonical window, not a use instruction'),
      }));
      const prepA = prepStart(c);
      const bizB = (prepA ? [clipB(prepA, c.a)] : []).filter(Boolean).map(b => Object.assign({}, b, {
        bg: '#00783F', color: '#fff', fs: '12px', fw: 700, radius: '3px', ink: '#fff',
        text: LC('PREPARAZIONE', 'PREPARATION') + ' · ' + CW_LEAD + LC('g', 'd') + ' · ' + CW_INTERP,
        title: CW_INTERP_LONG + ' · ' + CW_LEAD + LC('g prima di', 'd before') + ' ' + D.fmt(c.a),
      }));
      const deptRows = (s.calDetail && c.a) ? CW_DEPTS.map(dp => ({
        key: dp.dept === 'SALES / RTV' ? 'FIELD SALES' : dp.dept, dept: deptName(dp.dept), deptLabel: deptName(dp.dept), color: dp.color,
        bars: [clipB(addD(c.a, dp.fromDays), addD(c.a, dp.toDays))].filter(Boolean),
      })).filter(d => d.bars.length) : [];
      const lane = (key, hpx, bars) => (bars && bars.length) ? { key, h: hpx + 'px', bars } : null;
      const lanes = [lane('issue', 16, issueB), lane('adama', 18, adamaB), lane('biz', 18, bizB)].filter(Boolean);
      if (deptRows.length) {
        [['REGULATORY / PORTFOLIO', 'MARKETING', 'TECHNICAL / SCIENCE'], ['MARKET DEVELOPMENT', 'FIELD SALES'], ['SUPPLY']].forEach((grp, gi) => {
          let bars = [];
          deptRows.forEach(d => { if (grp.indexOf(d.key) < 0) return; bars = bars.concat(d.bars.map(b => Object.assign({}, b, { bg: d.color + '66', color: '#fff', ink: '#fff', fs: '10.5px', fw: 700, radius: '3px', text: d.dept + ' · ' + CW_INTERP, title: d.dept + ' · ' + CW_INTERP_LONG }))); });
          const l = lane('dept' + gi, 14, bars); if (l) lanes.push(l);
        });
      }
      /* 16 of 29 windows are already closed, so a row can legitimately have every
         bar outside the current viewport. The floor keeps the row proportions the
         layout was designed around instead of collapsing it to a hairline. */
      const rowH = Math.max(44, lanes.reduce((n, l) => n + parseInt(l.h), 0) + lanes.length * 3 + 8) + 'px';
      const cov = r.coverageState;
      const regLine = c.reg ? c.reg.act + ' · ' + c.reg.sourceId : null;
      return {
        windowId: c.windowId, crop: c.crop, cropL: cl(c.crop), region: c.region, issue: c.issue, issueL: il(c.issue),
        /* HECTARES AND CROP SCALE ARE GONE. There is no area field in any real
           source: 0 hectare-like keys in the ingest, and IG.CROPS carries only
           product-mention counts. The 40 '~Nk ha' figures were attributed on screen
           to ISTAT and no ISTAT area series exists in the package. Left null so an
           un-migrated markup line degrades visibly instead of lying. */
        ha: null, scale: null,
        /* 0 of 29 windows carry an observed crop stage. */
        current: T.cwNotObserved, currentColor: '#8F8886',
        coverage: COV_LAB[cov] || cov, covColor: cov === 'REGULATORY_READ' ? '#F5B317' : '#B1A9A7',
        covBg: 'rgba(151,139,135,0.18)',
        lanes, minH: rowH,
        hasObs: false, obsMark: null,
        /* No dated regulatory SPAN exists upstream — only a dated act. A bar would
           invent a duration, so the act is rendered as text, not as a band. */
        hasMand: false, mandBars: [],
        state: wst(c.status), stateColor: c.color, stateInk: D.inkOn(c.color), stateText: c.text,
        daysLabel: dayLab(c),
        windowFrom: c.a ? D.fmt(c.a) : T.wDateToConfirm, windowTo: c.b ? D.fmt(c.b) : T.wDateToConfirm,
        dateStateL: dst(r.dateState), dateConfidence: r.dateConfidence,
        prepLine: prepLineOf(c), leadDays: CW_LEAD,
        prepFrom: prepA ? D.fmt(prepA) + ' · ' + CW_INTERP : '—',
        adamaLabel,
        matchLabel: c.verified.length ? c.verified.join(' + ') : pst('NO_CONFIRMED_MATCH_CURRENT_READING'),
        matchCount: c.verified.length,
        sourceLine: regLine || LC('nessuna fonte collegata a questa finestra', 'no source linked to this window'),
        /* Market temperature and field-message counts were fixture reads. Neutral
           placeholders until the markup line that names them is removed. */
        marketTemp: '—', marketColor: '#8F8886', fieldCount: 0,
        bg: s.calRegion === c.windowId ? 'rgba(0,152,69,0.08)' : 'transparent',
        open: () => this.setState({ calRegion: c.windowId }),
      };
    });
    const calRows = calRowsAll.filter(r => !s.calBucket || calWins.some(w => w.windowId === r.windowId && w.status === s.calBucket));
    const calEmptyOther = s.calBucket ? ALL_CORES.filter(c => c.crop !== calCropKey && c.status === s.calBucket) : [];
    const calEmptyText = s.calBucket
      ? LC('Nessuna finestra di ' + cl(calCropKey).toUpperCase() + ' è in stato ' + wst(s.calBucket) + '. Le ' + (calRows.length + calEmptyOther.length) + ' righe corrispondenti stanno su altre colture — ' + [...new Set(calEmptyOther.map(c => cl(c.crop)))].join(', ') + '.',
        'No ' + cl(calCropKey).toUpperCase() + ' window is ' + wst(s.calBucket) + '. The ' + (calRows.length + calEmptyOther.length) + ' matching rows sit on other crops — ' + [...new Set(calEmptyOther.map(c => cl(c.crop)))].join(', ') + '.')
      : '';
    const calEmptyGo = () => { const first = calEmptyOther[0]; if (first) this.setState({ calCrop: first.crop, calRegion: null }); };
    const calEmptyCta = calEmptyOther.length ? LC('PASSA A ', 'SWITCH TO ') + cl(calEmptyOther[0].crop).toUpperCase() + ' →' : '';
    const calClearBucket = () => this.setState({ calBucket: '' });
    const calFilterLabel = s.calBucket
      ? calRows.length + '/' + calRowsAll.length + ' · ' + wst(s.calBucket)
      : calRowsAll.length + ' ' + LC('finestre', 'windows');

    /* ---- rolling month header · unchanged geometry ---- */
    const calMonths = (() => { const out = []; for (let mi = Math.floor(START); mi <= Math.ceil(START + HZ); mi++) { const y = 2026 + Math.floor(mi / 12), m = ((mi % 12) + 12) % 12; const l = (mi - START) / HZ; if (l >= 0.999) break; out.push({ label: T.months[m], year: y, isJan: m === 0, yearLabel: String(y), left: (Math.max(0, l) * 100).toFixed(2) + '%', width: ((1 / HZ) * 100).toFixed(2) + '%', color: (y === 2026 && m === 8) ? '#00B152' : '#8F8886' }); } return out; })();
    const calYearMarks = calMonths.filter(m => m.isJan).map(m => ({ left: m.left, label: m.yearLabel }));
    const todayPos = CAL_TODAY ? posOf(CAL_TODAY) : -1;
    const todayInView = todayPos >= 0 && todayPos <= 1;
    const todayLeft = (Math.max(0, Math.min(100, todayPos * 100))).toFixed(2) + '%';
    const calHorizons = [6, 12, 18, 24].map(n => ({ label: n + 'M', on: s.calH === n, bg: s.calH === n ? '#00783F' : 'transparent', border: s.calH === n ? '#009845' : 'rgba(203,197,195,0.2)', color: s.calH === n ? '#fff' : '#B1A9A7', go: () => this.setState({ calH: n }) }));
    const shiftCal = (d) => this.setState({ calStart: Math.max(-6, Math.min(30, s.calStart + d)) });
    /* BACK TO TODAY frames the reference month a third of the way in instead of hard
       against the left edge. With 16 of 29 windows already closed, a viewport that
       starts at today shows an empty timeline for more than half the rows; the
       fixture hid this by manufacturing a 2027 occurrence for every passed window. */
    const calNav = { back: () => shiftCal(-3), fwd: () => shiftCal(3), today: () => this.setState({ calStart: Math.max(-6, Math.round(8 - s.calH / 3)) }),
      onWheel: (e) => { const dx = Math.abs(e.deltaX) > Math.abs(e.deltaY) ? e.deltaX : (e.shiftKey ? e.deltaY : 0); if (!dx) return; shiftCal(dx / 90); },
      onDown: (e) => { this._cd = { x: e.clientX, s: s.calStart, w: e.currentTarget.getBoundingClientRect().width }; },
      onMove: (e) => { if (!this._cd) return; const dm = ((this._cd.x - e.clientX) / this._cd.w) * s.calH; this.setState({ calStart: Math.max(-6, Math.min(30, this._cd.s + dm)) }); },
      onUp: () => { this._cd = null; } };
    const calRangeLabel = (calMonths[0] ? calMonths[0].label + ' ' + calMonths[0].year : '') + ' → ' + (calMonths.length ? calMonths[calMonths.length - 1].label + ' ' + calMonths[calMonths.length - 1].year : '');
    const calModes = [['calendar', T.cwCalendar], ['season', T.cwSeason]].map(m => { const on = s.calMode === m[0]; return { label: m[1], bg: on ? 'rgba(0,152,69,0.25)' : 'transparent', border: on ? '#009845' : 'rgba(203,197,195,0.2)', color: on ? '#fff' : '#B1A9A7', go: () => this.setState({ calMode: m[0] }) }; });

    /* Crop marks drawn to the official ADAMA icon-language rule: thin 1.7px stroke,
       rounded caps and joins, simple shapes, never filled. The BrandWell crop-icon
       library is not part of the integrated design system, so these follow the published
       spec rather than substituting a generic third-party set. Rice and Soybean are new:
       the canonical set carries herbicide windows for both and the fixture rail had
       neither. */
    const CIRC = (cx, cy, r) => 'M' + (cx - r) + ' ' + cy + 'a' + r + ' ' + r + ' 0 1 0 ' + (r * 2) + ' 0a' + r + ' ' + r + ' 0 1 0 ' + (-r * 2) + ' 0';
    const GRAIN = (y) => ['M12 ' + y + 'c-2 0-3.6-1.5-3.6-3.4 2 0 3.6 1.5 3.6 3.4', 'M12 ' + y + 'c2 0 3.6-1.5 3.6-3.4-2 0-3.6 1.5-3.6 3.4'];
    const EAR = ['M12 21.5V11'].concat(GRAIN(19.5), GRAIN(15.8), GRAIN(12.1));
    const CROP_ICON = {
      'Durum Wheat': EAR.concat(['M12 9.6 9.9 5.2', 'M12 9.6V4.4', 'M12 9.6l2.1-4.4']),
      'Wheat': EAR.concat(['M12 11V8.6']),
      'Maize': ['M14.4 20.6c-2.6 0-4.7-2.9-4.7-7.2s2.1-9.3 4.7-9.3 4.7 5 4.7 9.3-2.1 7.2-4.7 7.2z', 'M12.7 8.4v9.6', 'M16.1 8.4v9.6', 'M10.2 11.2C7.3 11.9 5.2 14.4 5.2 17.8c2.9 0 4.9-1.7 5.5-3.9'],
      'Grapevine': [CIRC(9.3, 13.6, 2.4), CIRC(14.7, 13.6, 2.4), CIRC(12, 17.9, 2.4), 'M12 11.1V6.6', 'M12.2 8.3c1.6-2.4 4.2-2.9 6-2.1-.3 2.6-2.6 4.1-5.4 3.6'],
      'Olive': ['M4 19.4c4.1-1 7.9-3.6 10.4-7.1', CIRC(15.6, 8.6, 2.2), CIRC(10.7, 13.4, 2.2), 'M17.2 14.2c2-.6 3.6-2.4 4-4.6-2.2-.2-4.2 1-5 2.8'],
      'Sugar Beet': ['M12 21.2c-3.3-1.6-5.4-4.4-5.4-7.2 0-2.8 2.4-4.7 5.4-4.7s5.4 1.9 5.4 4.7c0 2.8-2.1 5.6-5.4 7.2z', 'M12 9.3V4.2', 'M12 6.9c-1.4-2-3.5-2.7-5.1-2.4.3 2.1 2.2 3.5 4.5 3.3', 'M12 6.9c1.4-2 3.5-2.7 5.1-2.4-.3 2.1-2.2 3.5-4.5 3.3'],
      'Apple': ['M12 7.9C10.9 6.8 9.5 6.4 8.3 6.4 5.8 6.4 4 8.6 4 12c0 4.3 3.3 8.7 5.9 8.7 1 0 1.4-.5 2.1-.5s1.1.5 2.1.5c2.6 0 5.9-4.4 5.9-8.7 0-3.4-1.8-5.6-4.3-5.6-1.2 0-2.6.4-3.7 1.5z', 'M12 7.9V4.3', 'M12.2 6c1.3-2 3.4-2.4 5-2-.3 2-2 3.3-4 3.2'],
      'Tomato': ['M12 21c-3.9 0-7-2.9-7-6.6s3.1-6.4 7-6.4 7 2.7 7 6.4-3.1 6.6-7 6.6z', 'M12 8V5.2', 'M12 8.2 9.1 6', 'M12 8.2 14.9 6'],
      'Rice': ['M12 21.4V12.8', 'M12 12.8c0-3.4 2.3-6.2 5.5-6.9-.4 3.5-2.6 6.2-5.5 6.9', 'M12 12.8C12 10 10 7.8 7.1 7.2c.3 2.9 2.2 5.1 4.9 5.6', 'M12 8.6c0-2 1.1-3.7 2.8-4.5'],
      'Soybean': ['M4.6 12c2.2-2.6 5.1-4 7.4-4s5.2 1.4 7.4 4c-2.2 2.6-5.1 4-7.4 4S6.8 14.6 4.6 12z', CIRC(8.7, 12, 1.25), CIRC(12, 12, 1.25), CIRC(15.3, 12, 1.25), 'M12 16.1v3.6', 'M12 18c1.5-2 3.7-2.5 5.4-2.1-.4 2.1-2.3 3.3-4.3 3.1'],
    };
    const calCropBtns = CROP_ORDER.map(k => {
      const cores = ALL_CORES.filter(x => x.crop === k);
      /* Ordering only: the upstream status tokens carry a rank so a crop rail can be
         sorted. Nothing here decides a state. */
      const best = cores.slice().sort((a, b) => (a.rank - b.rank) || ((dayNum(a) == null ? 9e3 : Math.abs(dayNum(a))) - (dayNum(b) == null ? 9e3 : Math.abs(dayNum(b)))))[0];
      const on = k === calCropKey;
      const openNow = !!(best && best.open);
      /* One axis on the rail: the upstream status. Green when upstream says open,
         otherwise the issue-category tint of the leading window. */
      const accent = openNow ? '#00B152' : (best ? best.cat : '#8F8886');
      const LIFT = { '#9D1D96': '#C46ABE', '#00698F': '#00A0DF', '#009845': '#00B152', '#00B152': '#00B152', '#F5B317': '#F5B317', '#7DB41E': '#93CC23', '#00A0DF': '#5CC3EE', '#8F8886': '#B1A9A7' };
      const ink = LIFT[accent] || accent;
      const sub = best ? (dayNum(best) == null ? wst(best.status) : dayLab(best) + ' · ' + wst(best.status)) : '—';
      const nVer = cores.filter(x => x.verified.length).length;
      return {
        label: cl(k).toUpperCase(), sub, paths: CROP_ICON[k] || CROP_ICON['Wheat'],
        /* The 'n/m observed' form is gone: 0 of 29 windows carry an observed stage.
           What the rail can honestly count is windows and verified label matches. */
        cover: cores.length + ' ' + (cores.length === 1 ? LC('FINESTRA', 'WINDOW') : LC('FINESTRE', 'WINDOWS')) + (nVer ? ' · ' + nVer + ' ' + LC('VERIFICATE', 'VERIFIED') : ''),
        bg: on ? '#00783F' : '#1C1817', border: on ? '#00B152' : 'rgba(203,197,195,0.18)',
        rail: on ? '#fff' : accent, iconColor: on ? '#fff' : ink,
        iconBg: on ? 'rgba(255,255,255,0.18)' : accent + '2E', iconRing: on ? 'rgba(255,255,255,0.40)' : accent + '7A',
        color: on ? '#fff' : '#EDEAE9', subColor: on ? '#fff' : ink, coverColor: on ? '#E3F4EA' : '#9A9391',
        weight: on ? 700 : 600, shadow: on ? '0 6px 18px rgba(0,120,63,0.45)' : 'none',
        go: () => this.setState({ calCrop: k, calRegion: null }),
      };
    });

    /* ---- SEASON VIEW · one card per canonical window of the selected crop ----
       The old cards were the eight fixture phenology stages plus a weed band, none
       of which has an upstream source (CROP_STAGE null 29/29). The section survives
       with real content: the crop's own audited windows, plus one card that states
       the preparation rule as an interpretation. */
    const calSeason = [{
      name: LC('PRE-STAGIONE · ' + CW_INTERP, 'PRE-SEASON · ' + CW_INTERP),
      range: CW_LEAD + LC('g di preparazione prima di ogni finestra con data', 'd of preparation before every dated window'),
      now: false, color: '#009845', bg: 'rgba(0,152,69,0.10)',
    }].concat(cropCores.map(c => ({
      name: il(c.issue).toUpperCase() + ' · ' + c.region,
      range: (c.hasDates ? D.fmt(c.a) + ' → ' + D.fmt(c.b) : T.wDateToConfirm) + ' · ' + wst(c.status),
      now: c.open, color: c.open ? '#00B152' : c.cat, bg: c.open ? 'rgba(0,152,69,0.16)' : 'rgba(255,255,255,0.03)',
    })));

    /* ---- the header strip · five counts that can all be checked against the model ---- */
    const calStrip = [
      { n: calWins.length, label: LC('finestre canoniche', 'canonical windows') },
      { n: calWins.filter(r => r.hasDates).length, label: LC('con date reali', 'with real dates') },
      { n: calWins.filter(r => (r.verifiedProducts || []).length).length, label: LC('con etichetta verificata', 'with a verified label') },
      { n: calWins.filter(r => r.regulatory).length, label: LC('con atto normativo', 'with a regulatory act') },
      { n: calWins.filter(r => r.observedStage).length, label: LC('con stadio osservato', 'with an observed stage') },
    ];

    /* ---- the drawer ----------------------------------------------------------
       Keyed on WINDOW_ID, not on region: a crop can hold several canonical windows
       in one region (Maize x Lombardia holds three), and the old region lookup
       silently showed the first of them. s.calRegion carries the window id. */
    const dw0 = calRowsAll.filter(r => r.windowId === s.calRegion)[0] || null;
    const dwW = dw0 ? calWins.filter(r => r.windowId === dw0.windowId)[0] : null;
    const dwC = dw0 ? cropCores.filter(c => c.windowId === dw0.windowId)[0] : null;
    /* Measured empty on 29/29 windows. Read, not assumed. */
    const dwSrc = dw0 ? (calSrcIds[dw0.windowId] || []) : [];
    const dw = (dw0 && dwW && dwC) ? Object.assign({}, dw0, {
      issueL: il(dwW.issue),
      /* SINTONIA INTERPRETATION, fenced. The offsets anchor on the canonical
         START_DATE and the whole plan is omitted when there is none (5/29 rows). */
      prepLine: prepLineOf(dwC),
      stateCap: LC('STATO A MONTE · CURRENT_STATUS', 'UPSTREAM STATE · CURRENT_STATUS'),
      stateBg: dwC.color,
      owner: (() => {
        if (!dwC.a || !CAL_TODAY) return '—';
        const inNow = CW_DEPTS.filter(dp => addD(dwC.a, dp.fromDays) <= CAL_TODAY && CAL_TODAY <= addD(dwC.a, dp.toDays));
        return inNow.length ? inNow.map(dp => deptName(dp.dept)).join(' + ') + ' · ' + CW_INTERP : '—';
      })(),
      /* 0 of 29 windows carry an observed crop stage; 5 of the 7 upstream field rows
         say so in as many words and neither of the 2 real ones is in a canonical
         region. Nothing is backfilled. */
      current: T.cwNotObserved, currentColor: '#8F8886',
      obsMeta: LC('nessun bollettino di fenologia letto per questa regione', 'no phenology bulletin read for this region'),
      /* Was EXPECTED CYCLE TODAY, computed from the fixture's stage table. What the
         package actually publishes about these dates is their state and confidence. */
      expectedNow: dst(dwW.dateState),
      dateStateL: dst(dwW.dateState), dateConfidenceL: dwW.dateConfidence || '—',
      /* Market temperature was an editorial fixture; the tile now has no value to
         show until its markup is repointed at the label verdict. */
      marketTemp: '—', marketColor: '#8F8886',
      /* Early market signal read 'FIELD REPORTED' on 9 of 29 windows, every one of
         them sourced from the 18 synthetic field messages. Zero real field signals. */
      fieldCount: 0, early: T.cwNotObserved,
      nextWindow: il(dwW.issue) + ' · ' + dw0.windowFrom + ' → ' + dw0.windowTo,
      prods: dwC.verified.map(n => ({ name: n })),
      noProducts: dwC.verified.length === 0,
      noProductsText: pst('NO_CONFIRMED_MATCH_CURRENT_READING') + ' — ' + (AM ? AM.ABSENCE_RULE : ''),
      why: (() => {
        const rows = [];
        rows.push({ t: wst(dwW.status) + ' · ' + reasonL(dwW.statusReason), ok: dwW.status === 'WINDOW_OPEN', warn: dwW.status === 'DATE_UNKNOWN' });
        rows.push({ t: dst(dwW.dateState) + ' · ' + LC('confidenza', 'confidence') + ' ' + (dwW.dateConfidence || 'NONE'), ok: dwW.hasDates, warn: !dwW.hasDates });
        rows.push({ t: dwC.verified.length ? pst('VERIFIED_LABEL_MATCH') + ' · ' + dwC.verified.join(', ') : pst('NO_CONFIRMED_MATCH_CURRENT_READING'), ok: dwC.verified.length > 0, warn: dwC.verified.length === 0 });
        rows.push({ t: (COV_LAB[dwW.coverageState] || dwW.coverageState) + (dwC.reg ? ' · ' + dwC.reg.act : ''), ok: !!dwC.reg, warn: !dwC.reg });
        rows.push({ t: T.cwNotObserved + ' · ' + LC('nessuno stadio colturale osservato in nessuna delle ' + calWins.length + ' finestre', 'no crop stage observed on any of the ' + calWins.length + ' windows'), ok: false, warn: true });
        rows.push({ t: dwSrc.length ? dwSrc.join(', ') : LC('SOURCE_IDS vuoto · nessuna fonte collegata a questa finestra', 'SOURCE_IDS empty · no source linked to this window'), ok: dwSrc.length > 0, warn: dwSrc.length === 0 });
        return rows.map(y => ({ t: y.t, mark: y.ok ? '✓' : y.warn ? '△' : '○', color: y.ok ? '#00B152' : y.warn ? '#F89E18' : '#8F8886' }));
      })(),
      deptPlan: CW_DEPTS.map(dp => ({
        dept: deptName(dp.dept), deptLabel: deptName(dp.dept), color: dp.color,
        range: dwC.a ? D.fmt(addD(dwC.a, dp.fromDays)) + ' → ' + D.fmt(addD(dwC.a, dp.toDays)) : '—',
        brief: () => {},
      })),
      know: [
        LC('Finestra auditata a monte · ', 'Upstream audited window · ') + dwW.windowId,
        wst(dwW.status) + ' · ' + reasonL(dwW.statusReason),
      ].concat(dwW.hasDates ? [dst(dwW.dateState) + ' · ' + dw0.windowFrom + ' → ' + dw0.windowTo] : [])
        .concat(dwC.reg ? [dwC.reg.act + ' · ' + actStateL(dwC.reg.actState)] : [])
        .concat(dwC.verified.length ? [pst('VERIFIED_LABEL_MATCH') + ' · ' + dwC.verified.join(', ')] : []),
      unknown: [
        LC('Stadio fenologico corrente in questa regione', 'Current crop stage in this region'),
        LC('Pressione corrente del parassita o della malattia', 'Current pest or disease pressure'),
        LC('Momento di acquisto del canale — non osservabile da fonti esterne', 'Channel purchase timing — not observable from external sources'),
      ].concat(dwSrc.length ? [] : [LC('Quali fonti sostengono questa finestra (SOURCE_IDS vuoto)', 'Which sources back this window (SOURCE_IDS empty)')]),
      /* SOURCE_IDS is empty on all 29 windows. The drawer used to borrow the demo
         case's source list; saying there is none is the honest answer. */
      sources: dwSrc.length ? dwSrc.slice()
        : dwC.reg ? [dwC.reg.sourceId + ' · ' + dwC.reg.act]
          : [LC('nessuna fonte collegata a questa finestra', 'no source linked to this window')],
      /* The opportunity link is NOT invented here. The model's own join key
         (opportunity LEGACY_CASE_ID 'IT-HERO-00n' against window legacyCaseId
         'IT-OPP-00n') resolves 0 of 3, and the tempting reverse key
         window.legacyCaseId === opportunity.id resolves 3 of which one is a plain id
         collision (IT-WIN-0029 Durum Wheat/Toscana against the national
         authorization-expiry opportunity). Two buttons disappear rather than link
         to the wrong record. */
      hasCase: false, openCase: () => {}, genBrief: () => {},
      goMarket: () => this.go({ view: 'market' }),
      goProduct: () => { if (dwC.verified.length) this.openProduct(dwC.verified[0]); },
    }) : {};
