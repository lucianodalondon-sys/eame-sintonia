    // ---- crop windows · the canonical audited set ------------------------------
    /* §9 · Every window on this screen is now AM.collections.cropWindows — 29 records,
       provenance CANONICAL, 29/29 real. The old ITALY_DEMO.WINDOWS wrapper (20 reads in this
       block) rebuilt each canonical row with ~20 fields that have no upstream
       equivalent. Measured against the pack: CROP_STAGE null 29/29, ISSUE_STAGE null
       29/29, GENERATION_OR_STAGE null 29/29, LABEL_TRIGGER null 29/29,
       REGULATORY_TIMING null 29/29, PRODUCT_MATCHES empty 29/29, SOURCE_IDS empty
       29/29. So kind, scale, bucket, early, why and readiness are rebuilt from what
       upstream actually states, or dropped. */
    const WROWS = (APP0 && APP0.cropWindows) ? APP0.cropWindows.records : [];
    const wIT = s.lang === 'it';
    const wUNK = wIT ? 'non noto' : 'not known';
    const wNOBS = wIT ? 'NON OSSERVABILE DA FONTI ESTERNE' : 'NOT OBSERVABLE FROM EXTERNAL SOURCES';
    /* ONE clock. Dates are formatted by slicing the supplied ISO strings — no Date
       object is constructed here — and daysToStart / daysToEnd came from AM.REF. */
    const WMON = T.months || ['GEN', 'FEB', 'MAR', 'APR', 'MAG', 'GIU', 'LUG', 'AGO', 'SET', 'OTT', 'NOV', 'DIC'];
    const wDate = (iso) => { const p = String(iso || '').split('-'); return p.length === 3 ? (String(p[2]).padStart(2, '0') + ' ' + (WMON[(+p[1]) - 1] || '')) : null; };
    const wStatusColor = { WINDOW_OPEN: '#009845', NEXT_CYCLE: '#B1A9A7', WINDOW_CLOSED: '#8F8886', DATE_UNKNOWN: '#6E6663' };
    /* LEGACY_CASE_ID is filled 29/29, so the case → window jump survives the switch
       from the fixture id "WIN-001" to the canonical WINDOW_ID "IT-WIN-0001". The old
       call dereferenced the result with no guard and would have thrown on a miss. */
    const winFor = (caseId) => WROWS.find(w => w.legacyCaseId === caseId) || null;
    cs.goWindow = () => { const w = winFor(cs0 && cs0.id); if (w) this.openWindow(w.id); };

    /* §9 · The portfolio verdict is the label audit, joined onto the window upstream:
       record.verifiedProducts, record.notFoundProducts and record.labelVerdictState.
       Measured on the joined set — 12 of 29 windows carry at least one
       VERIFIED_LABEL_MATCH, 7 carry only NOT_FOUND verdicts, 10 were never audited.
       This block derives none of it locally; a first pass here folded the separators
       by hand ("Cereal Aphids · BYDV Risk" vs "Cereal Aphids / BYDV Risk") and got
       the same 12, so the model's join is the one that ships. */
    const wSTR = (AM && AM.STRENGTH) || {};
    const pstate = (k) => (T.PSTATE && T.PSTATE[k]) || String(k || '').replace(/_/g, ' ');
    /* §9 · record.regulatory is the upstream reading for this exact crop, region and
       issue — measured 2 of 29 (IT-WIN-0001 Veneto DDR n. 13645, IT-WIN-0008 Piemonte
       Determinazione Dirigenziale n. 280). Only the act name, its state and its
       source id are rendered; every prose field on those rows is
       NOT_APPROVED_FOR_DISPLAY, so no Portuguese research note can reach the screen. */
    const wActState = (k) => ({ PRIMARY_SOURCE_READ: [wIT ? 'fonte primaria letta' : 'primary source read'], JA_NO_ACERVO: [wIT ? 'presente in archivio' : 'held in the archive'], CITADO_EM_FONTE_SECUNDARIA: [wIT ? 'citato in fonte secondaria' : 'cited in a secondary source'] }[k] || [String(k || '').replace(/_/g, ' ').toLowerCase()])[0];

    const wDeco = (w) => Object.assign({}, w, {
      go: () => this.openWindow(w.id),
      cropL: cl(w.crop), issueL: il(w.issue), statusL: wst(w.status),
      /* open / days / remaining stay on the object because other blocks read them,
         but the STATE is upstream CURRENT_STATUS — presentation only counts days. */
      open: w.open === true,
      days: w.daysToStart, remaining: w.daysToEnd,
      category: Object.assign({}, w.ui, { icon: (w.ui && w.ui.iconAsset) || '' }),
      daysLabel: w.status === 'WINDOW_OPEN' && w.daysToEnd !== null ? w.daysToEnd + ' ' + (T.wDaysRemaining || 'days remaining')
        : w.status === 'NEXT_CYCLE' && w.daysToStart !== null ? w.daysToStart + ' ' + (T.wDaysToOpen || 'days to open')
          : w.status === 'DATE_UNKNOWN' ? (T.wDateToConfirm || 'DATE TO CONFIRM') : wst(w.status),
      daysColor: wStatusColor[w.status] || '#8F8886',
      windowLabel: (w.startDate && w.endDate) ? (wDate(w.startDate) + ' → ' + wDate(w.endDate)) : (T.wDateToConfirm || 'DATE TO CONFIRM'),
      /* was the case fixture's prose ("Vector treatments · mid-June → late July").
         LAST_VALIDATED is filled 29/29 and is the one fact this tile can carry
         without repeating the status line below it. */
      calLabel: w.lastValidated ? ((wIT ? 'Validato ' : 'Validated ') + wDate(w.lastValidated) + ' ' + String(w.lastValidated).slice(0, 4)) : '',
    });

    const wins = WROWS.filter(w => (!s.wCrop || w.crop === s.wCrop) && (!s.wBucket || w.status === s.wBucket)).map(wDeco);
    const wCrops = uniq(WROWS.map(w => w.crop));
    const windowCropChips = [{ v: '', l: (T.cwAllCrops || 'ALL CROPS') }].concat(wCrops.map(c => ({ v: c, l: cl(c).toUpperCase() }))).map(o => { const on = s.wCrop === o.v; return { label: o.l, count: o.v ? WROWS.filter(w => w.crop === o.v).length : WROWS.length, color: on ? '#fff' : '#B1A9A7', bg: on ? 'rgba(0,152,69,0.25)' : 'transparent', border: on ? '#009845' : 'rgba(203,197,195,0.2)', go: () => this.setState({ wCrop: o.v }) }; });
    /* §9 · WK was ITALY_DEMO.WINDOW_KPI. Its six horizon buckets were arithmetically broken:
       ITALY_DEMO.WINDOWS clamped days with Math.max(0, daysToOpen), so all 16 WINDOW_CLOSED
       and all 5 DATE_UNKNOWN rows landed on 0 days and were reported as "NEXT 30
       DAYS" (measured d30 = 21) and prep "ACT NOW" (measured 21). The canonical set
       states four statuses of its own and they are the only buckets left. */
    const wCount = (k) => WROWS.filter(w => w.status === k).length;
    const WK = { total: WROWS.length, open: wCount('WINDOW_OPEN'), closed: wCount('WINDOW_CLOSED'), cycle: wCount('NEXT_CYCLE'), unknown: wCount('DATE_UNKNOWN'), withDates: WROWS.filter(w => w.hasDates).length, verified: WROWS.filter(w => w.labelVerdictState === 'VERIFIED_LABEL_MATCH').length, withRegulatoryAct: WROWS.filter(w => w.regulatory).length };
    const windowBuckets = [['WINDOW_OPEN', WK.open, '#009845'], ['WINDOW_CLOSED', WK.closed, '#8F8886'], ['NEXT_CYCLE', WK.cycle, '#B1A9A7'], ['DATE_UNKNOWN', WK.unknown, '#6E6663']].map(b => { const on = s.wBucket === b[0]; return { label: wst(b[0]), count: b[1], color: b[2], sub: (T.DSTATE && T.DSTATE[b[0] === 'DATE_UNKNOWN' ? 'DATE_TO_CONFIRM' : 'EXPECTED_NORM']) || '', bg: on ? 'rgba(0,152,69,0.15)' : '#1C1817', border: on ? '#009845' : 'rgba(203,197,195,0.10)', go: () => this.setState({ wBucket: on ? '' : b[0] }) }; });

    /* §9 · SINTONIA PLANNING RULE — a business lead time, not an agronomic fact.
       The rungs and the department list were ITALY_DEMO.LADDER / ITALY_DEMO.DEPT reads; they are
       re-declared here as local constants so no fixture supplies them, and they are
       anchored on the canonical START_DATE. ITALY_DEMO.DEPT held one colour pair for all six
       departments (#978B87 / #C3BCBA), so the read bought nothing. */
    const W_DEPT_C = '#978B87', W_DEPT_S = '#C3BCBA';
    const W_LADDER = [[90, 'MARKET DEVELOPMENT', 'Start regional validation', 'Avviare la validazione regionale'], [60, 'MARKETING', 'Prepare communication assets', 'Preparare i materiali di comunicazione'], [45, 'SALES / RTV', 'Prepare customer conversations', 'Preparare le conversazioni con i clienti'], [30, 'SUPPLY', 'Review internal readiness', 'Verificare la prontezza interna'], [14, 'SALES / RTV', 'Activate field execution', 'Attivare l’esecuzione in campo']];
    const wPrep = (w) => {
      const d = w.daysToStart;
      if (d === null || d === undefined) return { label: '—', color: '#6E6663' };
      if (d > 180) return { label: (T.cwPlan || 'PLAN'), color: '#6E6663' };
      if (d > 90) return { label: (T.cwPlan || 'PLAN'), color: '#009845' };
      if (d > 45) return { label: (T.cwPrepare || 'PREPARE'), color: '#009845' };
      if (d >= 0) return { label: (T.cwActivate || 'ACTIVATE'), color: '#009845' };
      /* The 90-day lead ran out before the reference date. Saying so is a planning
         statement; it deliberately avoids ACT NOW / WINDOW OPEN / NEXT CYCLE, which
         are agronomic states and belong to upstream alone. */
      return { label: wIT ? 'ANTICIPO SCADUTO' : 'LEAD TIME ELAPSED', color: '#978B87' };
    };

    /* §9 · EARLY MARKET SIGNAL is emptied, not rebuilt. Measured: 9 of 29 windows read
       "FIELD REPORTED" and every one of them was sourced from the 18 synthetic
       ITALY_DEMO.FIELD_MESSAGES — a field observation supplied by a fixture. The fallback
       counted competitor communications on the crop and printed them as a market
       signal, which is communication density, not pressure. Nothing external replaces
       it, so the card carries no rows. It has no sc-if guard in the markup. */
    const wEarly = { state: (T.cwNotObserved || 'NOT OBSERVED'), color: '#6E6663', text: wIT ? 'Nessun segnale commerciale anticipato è osservabile da fonti pubbliche per questa finestra. I messaggi dal campo appartengono alla dimostrazione Field Sales e non entrano in questo conteggio.' : 'No early commercial signal is observable from public sources for this window. Field messages belong to the Field Sales demonstration and are not counted here.' };

    /* §9 · wd0 resolves by canonical WINDOW_ID with no "|| ITALY_DEMO.WINDOWS[0]" fallback —
       the old fallback silently showed IT-WIN-0001 for any unknown or stale deep link. */
    const wd0 = WROWS.find(w => w.id === s.windowId) || null;
    const wdR = wd0 || { id: null, crop: '—', issue: '—', region: '—', status: 'DATE_UNKNOWN', statusReason: '', dateState: 'DATE_TO_CONFIRM', dateConfidence: 'NONE', cropStageClass: 'NOT_OBSERVED', issueStageClass: 'NOT_OBSERVED', startDate: null, endDate: null, daysToStart: null, daysToEnd: null, hasDates: false, open: false, sourceIds: [], sourceState: 'NOT_EXTERNALLY_OBSERVABLE', verifiedProducts: [], notFoundProducts: [], labelVerdictState: 'LABEL_CHECK_NEEDED', regulatory: null, coverageState: 'EXPECTED_NORM_ONLY', legacyCaseId: null, ui: (AM && AM.CATEGORY_UI) ? AM.CATEGORY_UI.unknown : {} };
    const wdVer = wdR.verifiedProducts || [];
    const wdVerdict = wdR.labelVerdictState || 'LABEL_CHECK_NEEDED';
    const wdReg = wdR.regulatory;
    const wdPrep = wPrep(wdR);
    const wd = Object.assign(wDeco(wdR), {
      /* the case link survives only because LEGACY_CASE_ID is filled 29/29 */
      openCase: () => wdR.legacyCaseId && this.openCase(wdR.legacyCaseId),
      nowRelevant: wdR.status === 'WINDOW_OPEN' && !!wdR.legacyCaseId,
      /* kind was CONFIRMED / SEASONAL / EXPECTED WINDOW, and "CONFIRMED" required an
         observation class of OFFICIAL_OBSERVED_CURRENT or FIELD_REPORTED_CURRENT —
         measured NOT_OBSERVED 29/29, so that branch could never fire. DATE_STATE is
         what upstream actually states (EXPECTED_NORM 24, DATE_TO_CONFIRM 5). */
      kind: (T.DSTATE && T.DSTATE[wdR.dateState]) || wdR.dateState || wUNK,
      /* CROP SCALE was the ~350k ha fixture attributed to ISTAT. There is no area
         field in any real source (zero hectare-like keys in ITALY_INGEST), so it can
         only say "not known" until the markup drops the label. */
      scale: wUNK,
      prepLabel: wdPrep.label, prepColor: wdPrep.color,
      /* four honest reasons instead of six confident ones; every row is an upstream
         value or an explicit absence, and the regulatory row exists for 2 of 29 */
      why: [
        { ok: wdR.status === 'WINDOW_OPEN', warn: wdR.status === 'DATE_UNKNOWN', t: wst(wdR.status) + (wdR.statusReason ? ' · ' + wdR.statusReason : '') },
        { ok: wdR.dateState === 'EXPECTED_NORM', warn: wdR.dateState !== 'EXPECTED_NORM', t: ((T.DSTATE && T.DSTATE[wdR.dateState]) || wdR.dateState || wUNK) + ' · ' + (wIT ? 'affidabilità della data' : 'date confidence') + ' ' + (wdR.dateConfidence || 'NONE') },
        { ok: wdVer.length > 0, warn: !wdVer.length, t: wdVer.length ? (pstate('VERIFIED_LABEL_MATCH') + ' · ' + wdVer.join(', ')) : (pstate(wdVerdict) + ' · ' + (T.absenceRule || wdR.absenceRule || 'Absence in this reading is not absence in the world.')) },
        { warn: true, t: (wIT ? 'Stadio della coltura e stadio dell’avversità' : 'Crop stage and issue stage') + ' · ' + ((T.OBSCLASS && T.OBSCLASS[wdR.cropStageClass]) || wdR.cropStageClass) },
      ].concat(wdReg ? [{ ok: true, t: (wIT ? 'Atto regionale' : 'Regional act') + ' · ' + wdReg.act + ' · ' + wActState(wdReg.actState) + (wdReg.sourceId ? ' · ' + wdReg.sourceId : '') }]
        : [{ warn: true, t: (wIT ? 'Nessuna fonte collegata a questa finestra nella lettura attuale' : 'No source linked to this window in the current reading') }])
        .map(y => ({ t: y.t, mark: y.warn ? '△' : y.ok ? '✓' : '○', color: y.warn ? '#978B87' : y.ok ? '#009845' : '#8F8886' })),
      /* the PORTFOLIO CLOCK tile: label-audit verdicts only, never a case fixture */
      c: {
        primaryLabel: wdVer.length ? wdVer.join(' · ') : pstate(wdVerdict),
        label: (wdVer.length || (wdR.notFoundProducts || []).length) ? pstate(wdVerdict) : (wIT ? 'Nessuna riga di etichetta letta per questa coltura × avversità' : 'No label row read for this crop × issue'),
        matchCount: wdVer.length,
      },
      early: wEarly, fieldMessages: [],
      /* eight rows became four. "Italy authorization: CONFIRMED · demo pack", "Label
         window: CONFIRMED", "Current crop timing" and "Field signal: REPORTED" were
         four fabricated verdicts; the three internal rows were always unknowable and
         now say so instead of "NOT CONNECTED", which implied a missing plug. */
      readiness: [
        { k: wIT ? 'Corrispondenza etichetta' : 'Label match', v: pstate(wdVerdict), color: (wSTR[wdVerdict] || {}).color || '#B1A9A7' },
        { k: wIT ? 'Scorte interne' : 'Internal stock', v: wNOBS, color: '#6E6663' },
        { k: wIT ? 'Materiale marketing' : 'Marketing material', v: wNOBS, color: '#6E6663' },
        { k: wIT ? 'Prontezza commerciale' : 'Sales readiness', v: wNOBS, color: '#6E6663' },
      ],
      /* Only VERIFIED_LABEL_MATCH products are shown. The old list came from the case
         fixture's productObjs and ranked its first entry "PRIMARY MATCH" with no
         verdict behind the word; the role is now the audited strength itself. */
      products: wdVer.map((name) => {
        const e = AM ? AM.findProduct(name) : null;
        const reg = e && e.regulatory;
        /* a resistance-scheme code is meaningless without its scheme name; the old
           card printed a bare "3" next to the word "registered" */
        const moa = reg ? [['IRAC', reg.irac], ['FRAC', reg.frac], ['HRAC', reg.hrac]].filter(x => x[1] && x[1].length).map(x => x[0] + ' ' + x[1].join('/')).join(' · ') : '';
        return {
          name, ai: (e && e.ai && e.ai.length) ? e.ai.join(' + ') : wUNK,
          role: pstate('VERIFIED_LABEL_MATCH'), roleColor: (wSTR.VERIFIED_LABEL_MATCH || {}).color || '#00B152',
          border: (((wdR.ui || {}).color || '#009845') + '88'),
          /* the crop × issue the verdict was actually read against, not a guess */
          targetFit: il(wdR.issue),
          /* GENERATION_OR_STAGE null 29/29 and CROP_STAGE null 29/29 — no stage exists */
          use: wUNK, moa: moa || wUNK,
          go: () => this.openProduct(name),
        };
      }),
      noProducts: wdVer.length === 0,
      ladder: (wdR.daysToStart === null || wdR.daysToStart === undefined) ? [] : W_LADDER.map(l => {
        const reached = wdR.daysToStart <= l[0];
        return { days: l[0], dept: l[1], deptLabel: l[1] === 'SALES / RTV' ? 'FIELD SALES' : l[1], text: wIT ? l[3] : l[2], soft: W_DEPT_S, numColor: reached ? '#fff' : '#8F8886', dot: reached ? W_DEPT_C : 'rgba(255,255,255,0.12)', state: reached ? (wIT ? 'RAGGIUNTO' : 'REACHED') : ((wIT ? 'TRA ' : 'IN ') + (wdR.daysToStart - l[0]) + (wIT ? 'G' : 'D')), stateColor: reached ? '#00B152' : '#8F8886', brief: () => wdR.legacyCaseId && this.openBrief(wdR.legacyCaseId, l[1]) };
      }),
      briefs: [['SALES / RTV', 'PRE-SEASON FIELD SALES BRIEF'], ['MARKETING', 'MARKETING PREPARATION BRIEF'], ['MARKET DEVELOPMENT', 'MARKET DEVELOPMENT PLAN'], ['TECHNICAL / SCIENCE', 'TECHNICAL MONITORING BRIEF'], ['REGULATORY / PORTFOLIO', 'REGULATORY CHECK'], ['SUPPLY', 'SUPPLY READINESS REQUEST']].map(b => ({ label: b[1], color: W_DEPT_C, soft: W_DEPT_S, go: () => wdR.legacyCaseId && this.openBrief(wdR.legacyCaseId, b[0]) })),
      /* ITALY_DEMO.SIGNALS was the 56-record presentation set the model already fences off as
         DEMO_SCENARIO. Real supply is 3 futureSignals for the whole country, and their
         REGION field literally reads "NAO SEI ..." while every prose field is
         NOT_APPROVED_FOR_DISPLAY — there is no honest crop × region join, so the panel
         is empty for all 29 windows and the existing empty state carries it. */
      signals: [], noSignals: true,
      expectedLine: wdR.dateState === 'EXPECTED_NORM' ? (wIT ? 'Date della finestra dal ciclo annuale atteso' : 'Window dates from the expected annual cycle') : (T.wDateToConfirm || 'DATE TO CONFIRM'),
      unknownLine: wIT ? 'Pressione corrente di insetti e malattie' : 'Current-year pest / disease pressure',
    });
    /* §9 · earlyWindows filtered on w.early.state, a state that only the fixture ever
       produced. There is no canonical equivalent — CROP_STAGE_CLASS and
       ISSUE_STAGE_CLASS are NOT_OBSERVED 29/29 — so the component is removed rather
       than invented. It is declared because a later block reads the name; it has no
       binding anywhere in the markup template (verified over lines 51-2374). */
    const earlyWindows = [];
