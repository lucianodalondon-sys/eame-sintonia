/* Sintonia · department Action Brief generator.
   ---------------------------------------------------------------------------
   FACT SOURCE = window.ITALY_APP_MODEL. The legacy case object is accepted only
   as a ROUTING KEY (which canonical window, which product names, which colour).
   No agronomic state, date, stage, label trigger, source, evidence count or
   field observation is ever taken from the demo fixture (PRODUCT LAW §2/§3).

   ONE clock: window.ITALY_APP_MODEL.referenceDate / .REF (PRODUCT LAW §6).
   This file constructs no Date object at all — dates are formatted from the
   model's ISO strings, and every day count is the model's own.
   --------------------------------------------------------------------------- */
(function () {
  const S = (h, lines, bullets) => ({ h, lines: lines.filter(Boolean), bullets: !!bullets });

  /* ── model access ───────────────────────────────────────────────────────── */
  const M = () => (typeof window !== 'undefined' && window.ITALY_APP_MODEL) || null;
  const MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  /* ISO string in, human string out. Deliberately string-only: constructing a
     Date here would be a second truth clock. */
  const fmtISO = (iso) => {
    if (!iso) return null;
    const p = String(iso).split('-');
    return (p.length === 3 && MON[+p[1] - 1]) ? `${p[2]} ${MON[+p[1] - 1]} ${p[0]}` : String(iso);
  };
  const refISO = () => { const m = M(); return (m && m.referenceDate) || null; };
  const refStamp = () => fmtISO(refISO()) || 'REFERENCE DATE NOT AVAILABLE';

  /* The canonical window record for a case. 29/29 legacy cases resolve by
     legacyCaseId; windowId is kept as a second key. */
  const win = (c) => {
    const m = M(); if (!m || !c || !m.collections || !m.collections.cropWindows) return null;
    const R = m.collections.cropWindows.records || [];
    return R.find(r => r.legacyCaseId === c.id)
      || (c.windowId ? R.find(r => r.windowId === c.windowId) : null)
      || null;
  };
  const prod = (name) => { const m = M(); return (m && m.findProduct && name) ? m.findProduct(name) : null; };
  const coll = (k) => { const m = M(); return (m && m.collections && m.collections[k]) || null; };

  /* ── honest states (PRODUCT LAW §1/§3) ──────────────────────────────────── */
  const UNK = 'NON NOTO — not established in the Sintonia model';
  const NOTCONF = 'NON CONFERMATO — not confirmed by an external source in this reading';
  const NOT_OBS = 'NON OSSERVABILE DA FONTI ESTERNE';
  const INTERP = ' — SINTONIA INTERPRETATION';

  const listOf = (arr, cap) => {
    const a = (arr || []).filter(Boolean);
    if (!a.length) return null;
    const n = cap || 8;
    return a.length > n ? `${a.slice(0, n).join(', ')} (+${a.length - n} more on the label record)` : a.join(', ');
  };

  /* ── fact readers ───────────────────────────────────────────────────────── */
  const F = (c) => {
    const W = win(c);
    const m = M();
    const f = {
      W,
      crop: (W && W.crop) || UNK,
      region: (W && W.region) || UNK,
      issue: (W && W.issue) || UNK,
      issueType: (W && W.issueType) || UNK,
      status: (W && W.status) || 'NOT_ESTABLISHED',
      statusReason: (W && W.statusReason) || null,
      from: (W && fmtISO(W.startDate)) || 'DATE NOT ESTABLISHED',
      to: (W && fmtISO(W.endDate)) || 'DATE NOT ESTABLISHED',
      dateState: (W && W.dateState) || UNK,
      dateConfidence: (W && W.dateConfidence) || UNK,
      lastValidated: (W && fmtISO(W.lastValidated)) || UNK,
      windowType: (W && W.windowType) || UNK,
      /* CROP_STAGE / ISSUE_STAGE are null on 29/29 canonical windows: the class
         is the only observed value, and NOT_OBSERVED is a real answer. */
      cropStage: (W && (W.cropStage || W.cropStageClass)) || 'NOT_OBSERVED',
      issueStage: (W && (W.issueStage || W.issueStageClass)) || 'NOT_OBSERVED',
      labelTrigger: (W && W.labelTrigger) || null,
      labelSource: (W && W.labelSource) || null,
      color: (W && W.ui && W.ui.color) || (c && c.category && c.category.color) || '#009845',
      lowIssue: String((W && W.issue) || 'this issue').toLowerCase(),
      lowCrop: String((W && W.crop) || 'this crop').toLowerCase()
    };
    f.windowState = (() => {
      if (!W) return 'WINDOW NOT ESTABLISHED';
      if (W.status === 'WINDOW_CLOSED') return `window closed · ${Math.abs(W.daysToEnd)} days past END_DATE`;
      if (typeof W.daysToStart === 'number' && W.daysToStart > 0) return `${W.daysToStart} days to open`;
      if (typeof W.daysToEnd === 'number') return `${W.daysToEnd} days remaining`;
      return String(W.status || 'WINDOW NOT ESTABLISHED');
    })();
    f.windowOpen = !!(W && W.status !== 'WINDOW_CLOSED' && typeof W.daysToStart === 'number' && W.daysToStart <= 0);
    /* Product names route into the model; the fixture's ai / crops / targets /
       use / moa are never read. */
    const names = (c && (c.products || (c.productObjs || []).map(p => p && p.name))) || [];
    f.products = names.filter(Boolean).map(n => ({ name: n, P: prod(n) }));
    f.primaryName = (c && c.primary) || null;
    f.primary = f.primaryName ? prod(f.primaryName) : null;
    f.moreMatches = Math.max(0, f.products.length - 1);
    f.model = !!m;
    return f;
  };

  const window_ = (f) => [
    `${f.from} → ${f.to} · ${f.windowState} · window type ${f.windowType}`,
    `Date state ${f.dateState} · confidence ${f.dateConfidence} · last validated ${f.lastValidated}`,
    `Crop stage: ${f.cropStage} · issue stage: ${f.issueStage}` + (f.cropStage === 'NOT_OBSERVED' ? ' (no observed stage is recorded for this window — do not assert one)' : ''),
    f.labelTrigger
      ? `Label trigger: ${f.labelTrigger}${f.labelSource ? ` · source ${f.labelSource}` : ''}`
      : 'Label trigger: NON NOTO — no LABEL_TRIGGER is recorded on this window. Read the application timing from the product label record, never from this brief.'
  ];

  const prodLine = (x) => {
    const P = x.P;
    if (!P) return `${x.name} — not present in the Sintonia product model · confirm against the national label record before any use`;
    const ai = (Array.isArray(P.ai) ? P.ai : [P.ai]).filter(Boolean);
    const R = P.regulatory || {};
    /* irac / frac / hrac are arrays in the model and an empty array is truthy,
       so they are normalized before they can print an empty "IRAC ·" group. */
    const code = (v, tag) => { const a = (Array.isArray(v) ? v : [v]).filter(x => x !== null && x !== undefined && String(x).trim() !== ''); return a.length ? `${tag} ${a.join(' + ')}` : null; };
    const moa = [code(R.irac, 'IRAC'), code(R.frac, 'FRAC'), code(R.hrac, 'HRAC')].filter(Boolean).join(' · ');
    return [
      `${P.name} — active substance: ${ai.length ? ai.join(' + ') : UNK}`,
      `label crops: ${listOf(P.crops) || UNK}`,
      `label targets: ${listOf(P.targets, 6) || UNK}`,
      `mode of action: ${moa || UNK}`,
      `authorisation: ${P.status || NOTCONF}`,
      `expiry: ${fmtISO(P.expiry) || UNK}`,
      P.labelUrl ? `label record: ${P.labelUrl}` : `label record: ${UNK}`
    ].join(' · ');
  };
  const prodLines = (f) => f.products.length
    ? f.products.map(prodLine)
    : ['No product is linked to this window in the model — do not name a product until Regulatory / Portfolio confirms one.'];

  /* Every field-message record in this package is SYNTHETIC_DEMO (0 real of 18
     in the model). A demo record may never supply a field observation. */
  const realField = (c) => ((c && c.fieldMessages) || []).filter(m => m && m.demo !== true && m.provenance !== 'SYNTHETIC_DEMO');
  const FIELD_NONE = 'No verified field observation on this case. Every field-message record in this package carries provenance SYNTHETIC_DEMO, so none is printed as intelligence.';
  const fieldLines = (c) => {
    const ms = realField(c);
    return ms.length ? ms.map(m => `${m.person} · ${m.when}: “${m.text}” → ${m.signal}`) : [FIELD_NONE];
  };

  /* Competitor communication is real (REAL_SOURCE corpus) but the model does not
     attribute it to a case, so no per-case count is printed. */
  const compLines = () => {
    const C = coll('competitorActivities');
    if (!C || !C.count) return ['No competitor communication corpus is loaded in this reading.'];
    return [
      `${C.count} competitor communication items observed in the monitored public sources (provenance ${C.provenance}).`,
      'Attribution of those items to this crop × region is NOT established in the model — no per-case competitor count is printed here. Open Competitor Watch to read the corpus.',
      'Observed communication only. REACHED_IN_ITALY is not TARGETED_ITALY, and no strategy, spend or share is inferred.'
    ];
  };

  const sourcesLines = (f) => {
    const W = f.W; const SR = coll('sources'); const out = [];
    out.push(W
      ? `Canonical window ${W.windowId} · provenance ${W.provenance} · date state ${W.dateState} · confidence ${W.dateConfidence} · last validated ${f.lastValidated}.`
      : `No canonical window resolved for this case — every window fact above reads ${NOTCONF}.`);
    out.push((W && (W.sourceIds || []).length)
      ? `Declared sources: ${W.sourceIds.join(', ')}.`
      : 'This window declares no SOURCE_IDS — the per-case source list is NON CONFERMATO.');
    if (SR) out.push(`Source register: ${SR.count} registered public sources (provenance ${SR.provenance}). Per-case connected-observation counts are not established in the model and are not printed.`);
    out.push(`Sintonia reference date ${refStamp()}. All day counts above are measured from that date.`);
    return out;
  };

  const NOT_ESTABLISHED = (what) => `${what}: NON NOTO — no approved Sintonia narrative exists for this case in the model, so nothing is asserted here.`;

  const GEN = {
    'SALES / RTV': (c, f) => ({
      doc: 'FIELD SALES ACTION BRIEF', role: 'Technical Sales Representative', pages: '1–2 pages',
      purpose: 'Help the representative enter customer conversations with the confirmed window and portfolio facts, and with an explicit list of what is not confirmed.',
      sections: [
        S('1 · What is happening', [NOT_ESTABLISHED('Situation narrative'), `Confirmed: ${f.issue} (${f.issueType}) is the issue this ${f.crop} window is registered against, in ${f.region}. Current status ${f.status}${f.statusReason ? ` — ${f.statusReason}` : ''}.`]),
        S('2 · Where', [`${f.region} · ${f.crop}.`, `Adjacent-area guidance: ${UNK}. The model records no adjacent-region list for this window.`]),
        S('3 · Why this matters now' + INTERP, [NOT_ESTABLISHED('Why-now'), `What can be said from the record: the window runs ${f.from} → ${f.to} and is ${f.windowState}.`]),
        S('4 · Current crop / application window', window_(f)),
        S('5 · What ADAMA can offer', prodLines(f), true),
        S('6 · What we know', [
          `Canonical window on file: ${f.W ? f.W.windowId : 'none'} · provenance ${f.W ? f.W.provenance : NOTCONF}.`,
          `Registered ADAMA products linked to this window: ${f.products.length}.`,
          `Observed crop stage: ${f.cropStage}. Observed issue stage: ${f.issueStage}.`
        ], true),
        S('7 · What still needs validation', [
          'Current field pressure — no observed stage is recorded on this window.',
          'Label trigger and application timing — read the label record, not this brief.',
          'Whether the signal extends into adjacent areas — no adjacent-area record exists.',
          'Competitor activity attributable to this crop × region.'
        ], true),
        S('8 · Customer conversation guide' + INTERP, [
          `OPEN — “We are following ${f.lowIssue} on ${f.lowCrop} in ${f.region} and the registered window makes it worth reviewing protection.”`,
          'UNDERSTAND — listen first; do not assert incidence, stage or pressure the customer has not reported. Sintonia has not observed any.',
          f.primary
            ? 'CONNECT — “ADAMA has registered portfolio options that may fit this crop and target. Let us confirm the exact label position and timing for your situation.”'
            : 'CONNECT — “We are checking our portfolio position for this situation and will come back with a confirmed label answer.”',
          f.primary ? `PRODUCT — ${prodLine({ name: f.primaryName, P: f.primary })}. Only verified label facts; never a claim outside the approved label; never an invented efficacy.` : null
        ], true),
        S('9 · Questions to ask the customer' + INTERP, ['What crop stage are you seeing?', 'Have you observed symptoms or captures?', `Has ${f.lowIssue} already been confirmed on your farm?`, 'What was the previous treatment?', 'What field conditions are you seeing?', 'Are you already evaluating a treatment decision?'], true),
        S('10 · Why talk about this now' + INTERP, [
          `The registered window is ${f.windowState}`,
          `A canonical window record exists for this crop × issue × region (${f.W ? f.W.windowId : 'none'})`,
          f.primary ? 'A registered ADAMA portfolio match exists' : 'No portfolio position is confirmed yet',
          `Field pressure: ${f.issueStage} — this is not a pressure claim`
        ], true),
        S('Your objective' + INTERP, ['Open the conversation.', 'Validate what the customer is seeing.', f.primary ? 'Position the relevant ADAMA portfolio strictly within the label.' : 'Do not position a product until Regulatory / Portfolio confirms one.', 'Record what was observed.'], true),
        S('11 · What to report back to Sintonia', ['What did the customer report?', 'Was the issue confirmed?', 'What crop stage?', 'What product are they considering?', 'What competitor was mentioned?', 'Should Sintonia continue monitoring this case?'], true),
        S('12 · Sources / date', sourcesLines(f))
      ]
    }),
    'MARKETING': (c, f) => ({
      doc: 'MARKETING ACTION BRIEF', role: 'Marketing · regional communication', pages: '2 pages',
      purpose: 'Give Marketing the confirmed context, the supportable message territory and the boundaries needed to prepare regional support material.',
      sections: [
        S('Case', [`${f.issue} · ${f.crop} · ${f.region} · status ${f.status}`]),
        S('Audience' + INTERP, [`Growers and dealers in ${f.region} ${f.lowCrop} districts; ADAMA field sales as first relay.`]),
        S('Why now' + INTERP, [NOT_ESTABLISHED('Why-now'), ...window_(f)]),
        S('What the field is saying', fieldLines(c), true),
        S('What official / technical sources are saying', [NOT_ESTABLISHED('Source summary'), ...sourcesLines(f)]),
        S('ADAMA portfolio relevance', prodLines(f), true),
        S('Competitor communication observed', compLines(), true),
        S('Communication opportunity' + INTERP, [`Regional, timing-led technical communication on ${f.lowIssue} in ${f.lowCrop} while the window is ${f.windowState}.`]),
        S('Key message territory' + INTERP, ['Timing and monitoring awareness', 'Label-compliant portfolio fit for the crop × target', 'Regional monitoring as the trigger for attention'], true),
        S('Claims we can support', f.primary
          ? [`${f.primary.name} is registered in Italy — authorisation ${f.primary.status || NOTCONF}, expiry ${fmtISO(f.primary.expiry) || UNK}`, `Its label crops and targets are as printed in the portfolio section above`, `A canonical window exists for ${f.crop} × ${f.issue} in ${f.region}`]
          : ['No confirmed label match — communication must not name a product.'], true),
        S('Claims we must not make', ['Incidence, pressure or “spreading across the region” — no observed stage exists on this window', 'Efficacy, yield or revenue outcomes', 'Anything outside the approved label', 'Competitor strategy, spend or share', 'Any application timing not read from the label record'], true),
        S('Suggested assets' + INTERP, ['Regional sales support card', 'Dealer messaging asset', 'Technical post', 'Dealer support material', 'Field-sales presentation slide', 'Short agronomic video'], true),
        S('Urgency', [`${f.status} · ${f.windowState}`])
      ]
    }),
    'MARKET DEVELOPMENT': (c, f) => ({
      doc: 'MARKET DEVELOPMENT ACTION BRIEF', role: 'Market Development', pages: '1–2 pages',
      purpose: 'Validate the signal, judge regional relevance and decide where to look next.',
      sections: [
        S('What changed', [NOT_ESTABLISHED('Change narrative'), `On the record: window ${f.W ? f.W.windowId : 'none'} last validated ${f.lastValidated}, status ${f.status}${f.statusReason ? ` — ${f.statusReason}` : ''}.`]),
        S('Why this deserves attention' + INTERP, [NOT_ESTABLISHED('Why-now')]),
        S('Regional context', [`${f.region} — ${f.crop}. Regional precision only; no local coordinates.`, `Adjacent-area list: ${UNK}. Regional crop-area weight for this case: ${UNK} in this reading.`]),
        S('Portfolio connection', f.primary
          ? [`Primary: ${prodLine({ name: f.primaryName, P: f.primary })}`, `${f.moreMatches} further product(s) linked to this window.`]
          : ['No confirmed portfolio position — Regulatory / Portfolio check requested.']),
        S('Field voice', fieldLines(c), true),
        S('What needs validation', ['Current pressure and crop stage — both read NOT_OBSERVED on this window', 'Label trigger — not recorded; read the label record', 'Adjacent-area movement — no adjacent-area record exists', 'Competitor activity attributable to this crop × region'], true),
        S('Where to validate next' + INTERP, ['The regional bulletin series that publishes for this crop and region', 'Field colleagues covering the region', 'The national label record for every product listed above'], true),
        S('Who to contact / listen to' + INTERP, ['Regional phytosanitary / advisory service for the region', 'Field sales representatives in the region', 'Producer organisations and technical networks covering the crop'], true),
        S('Competitor context', compLines(), true),
        S('Next 48h / 7 days' + INTERP, ['48h — confirm the signal with the next regional update and one field colleague', '7 days — decide expand / hold; brief Sales and Marketing if confirmed'], true)
      ]
    }),
    'TECHNICAL / SCIENCE': (c, f) => ({
      doc: 'TECHNICAL VALIDATION BRIEF', role: 'Technical / Science', pages: '2–3 pages',
      purpose: 'Validate agronomic pressure and application timing. This is not a sales document.',
      sections: [
        S('Signal under review', [`${f.issue} (${f.issueType}) on ${f.crop} · ${f.region}`, `Scientific / taxonomic name for this issue: ${UNK} on the canonical window record.`]),
        S('Agronomic evidence available', [NOT_ESTABLISHED('Evidence narrative'), ...sourcesLines(f)]),
        S('Crop stage', [`${f.cropStage}${f.cropStage === 'NOT_OBSERVED' ? ' — CROP_STAGE is not recorded on this window; no stage may be asserted downstream.' : ''}`]),
        S('Disease / pest signal', [`${f.issueStage}${f.issueStage === 'NOT_OBSERVED' ? ' — ISSUE_STAGE is not recorded on this window; this is not a low-pressure claim, it is an absence of observation.' : ''}`]),
        S('Official monitoring', ['Per-case official-observation counts are not established in the model and are not printed.', ...sourcesLines(f).slice(0, 2)]),
        S('Scientific context', (() => { const SC = coll('scienceRecords'); const RS = coll('resistance'); return [
          SC ? `Science corpus: ${SC.count} records (provenance ${SC.provenance}). Case-level linkage is not established, so no per-case count is printed. Author affiliation is never treated as field location.` : `Science corpus: ${UNK}.`,
          RS ? `Resistance corpus: ${RS.count} documented mechanisms (provenance ${RS.provenance}) available for the resistance-management argument.` : null
        ]; })()),
        S('Label timing', window_(f).slice(3).concat(prodLines(f)), true),
        S('Field voice', fieldLines(c), true),
        S('What is still unknown', ['Current-season phenology for this region', 'Current pest / disease pressure', 'Label trigger and dose — held only in the label record', 'Whether the signal extends into adjacent areas'], true),
        S('Questions to validate' + INTERP, ['Is the reported stage consistent with the phenology model for the region?', 'Does the signal meet the regional intervention threshold?', 'Does the label window overlap the current stage?', 'Any weather driver that changes timing this week?', 'Is there resistance-management guidance to attach?'], true),
        S('Recommendation format', ['Return: CONFIRMED / NOT CONFIRMED / NEEDS MORE DATA, with date and source.'])
      ]
    }),
    'REGULATORY / PORTFOLIO': (c, f) => ({
      doc: 'REGULATORY & PORTFOLIO CHECK', role: 'Regulatory / Portfolio', pages: '1–2 pages',
      purpose: 'Confirm authorisation and label positioning for the products linked to this case before any field or marketing message.',
      sections: [
        S('Case', [`${f.issue} · ${f.crop} · ${f.region}`]),
        S('Products linked', prodLines(f), true),
        S('Italy authorisation', ['Authorisation status and expiry above are read from the Sintonia product model. Re-confirm current status in the national database (Banca Dati Fitosanitari) via the label record URL for each product before release.']),
        S('Dose · application interval · maximum applications', [`${NOT_OBS.replace('OSSERVABILE DA FONTI ESTERNE', 'DERIVABILE DA SINTONIA')} — read from the current label record. Sintonia never derives dose.`]),
        S('Expiry / regulatory context', ['Confirm authorisation expiry and any pending renewal, restriction or buffer-zone condition.', ...(() => {
          const soon = f.products.filter(x => x.P && x.P.expiry).map(x => `${x.P.name} · expiry ${fmtISO(x.P.expiry)}`);
          return soon.length ? [`Expiries on file: ${soon.join(' · ')}.`] : [`Expiries on file: ${UNK}.`];
        })()]),
        S('Uncertainties', [
          ...(() => { const noAi = f.products.filter(x => !x.P || !(Array.isArray(x.P.ai) ? x.P.ai.filter(Boolean).length : x.P.ai)).map(x => x.name);
            return noAi.length ? [`Active substance not established in the model for: ${noAi.join(', ')}.`] : ['Active substance is established in the model for every product linked to this window.']; })(),
          f.primary ? null : 'No primary product matched — confirm whether any ADAMA position exists for this crop × target.',
          'No LABEL_TRIGGER is recorded on this window, so the application timing shown anywhere downstream must come from the label record only.'
        ], true),
        S('Requires manual confirmation', ['Label target wording vs. observed pest/disease', 'Crop listing (including crop group)', 'Regional or seasonal restrictions', 'Status change alerts subscribed'], true),
        S('Return to', ['Sales, Marketing and Market Development are blocked on this check for product naming.'])
      ]
    }),
    'SUPPLY': (c, f) => ({
      doc: 'SUPPLY READINESS REQUEST', role: 'Supply', pages: '1 page',
      purpose: 'Handoff request — external intelligence cannot know availability. This is not an availability claim.',
      sections: [
        S('Case', [`${f.issue} · ${f.crop} · ${f.region} · ${f.status}`]),
        S('Portfolio products', f.products.length ? f.products.map(x => x.name) : ['No product linked to this window'], true),
        S('Timing', window_(f)),
        S('Why readiness should be reviewed', [
          `The registered window runs ${f.from} → ${f.to} and is ${f.windowState}.`,
          (() => { const n = realField(c).length; return n ? `${n} verified field observation(s) on this case.` : 'No verified field observation supports a demand read on this case, and no demand is implied.'; })(),
          `Demand, orders and grower purchase timing are ${NOT_OBS}.`
        ]),
        S('Request', ['Please review readiness for the region and window above. Sintonia has no view of availability, orders or forecast and makes no claim about any of them.'])
      ]
    })
  };

  const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;');

  function build(dept, c) {
    const g = GEN[dept]; if (!g) return null;
    const f = F(c || {});
    const b = g(c || {}, f);
    b.dept = dept; b.case = c; b.facts = f;
    b.title = `${f.issue} · ${f.crop} · ${f.region}`;
    b.priority = f.status;
    b.accentColor = f.color;
    b.windowFrom = f.from; b.windowTo = f.to; b.windowState = f.windowState;
    b.primary = f.primaryName && f.primary ? f.primary.name : null;
    /* ONE clock (PRODUCT LAW §6). This is the model's reference date, not a
       wall clock, and it is labelled as such wherever it is printed. */
    b.referenceDate = refISO();
    b.generated = `${refStamp()} · Sintonia reference date (not a print timestamp)`;
    b.summary = `${b.doc} — ${b.title}\nFor: ${b.role} · Priority: ${b.priority} · ${b.generated} · Sintonia ADAMA Italy · Demonstration environment\n\n`
      + b.sections.map(s => s.h.toUpperCase() + '\n' + s.lines.map(l => (s.bullets ? '• ' : '') + l).join('\n')).join('\n\n');
    return b;
  }

  function printHtml(b) {
    /* The brief's CSS comes from the local _ds/adama-brandwell package that ships
       with the client folder — no CDN, no network. */
    const base = (typeof document !== 'undefined' && document.baseURI) ? document.baseURI.replace(/[^/]*$/, '') : '';
    const col = b.accentColor || '#009845';
    const showLoop = b.dept === 'SALES / RTV';
    return `<!doctype html><html><head><meta charset="utf-8"><title>${esc(b.doc)} · ${esc(b.title)}</title>
<link rel="stylesheet" href="${base}_ds/adama-brandwell/tokens/typography.css">
<style>@page{size:A4;margin:16mm 16mm 18mm}body{margin:0;font-family:'LL Brown','BrownLL',Arial,sans-serif;color:#231F20;font-size:10.5pt;line-height:1.45}
.top{display:flex;justify-content:space-between;align-items:flex-start;border-bottom:3px solid #009845;padding-bottom:8px;margin-bottom:12px}.brand{font-size:9pt;letter-spacing:.18em;font-weight:700;color:#009845}.brand small{display:block;letter-spacing:.12em;color:#978B87;font-weight:600;margin-top:2px}
.doc{font-size:9pt;letter-spacing:.14em;font-weight:700;color:#978B87;text-align:right}.doc b{display:block;color:#231F20;font-size:9pt;margin-top:2px}
h1{font-size:22pt;line-height:1.05;margin:0 0 6px;letter-spacing:-.01em}.meta{display:flex;gap:18px;flex-wrap:wrap;font-size:9pt;color:#6E6663;margin-bottom:12px}.meta b{color:#231F20}
.pri{display:inline-block;padding:3px 10px;border-radius:999px;background:${col};color:#fff;font-weight:700;font-size:8.5pt;letter-spacing:.08em}.purpose{background:#f4f2f2;border-radius:10px;padding:10px 12px;font-size:10pt;margin-bottom:12px}
h2{font-size:9pt;letter-spacing:.14em;color:${col};margin:12px 0 4px;text-transform:uppercase;page-break-after:avoid}p,li{margin:0 0 3px}ul{margin:0;padding-left:16px}
.loop{margin-top:14px;border:2px solid #009845;border-radius:12px;padding:10px 12px;page-break-inside:avoid}.loop b{color:#009845;letter-spacing:.12em;font-size:9pt}
.foot{margin-top:16px;padding-top:8px;border-top:1px solid #CBC5C3;font-size:8pt;color:#978B87;display:flex;justify-content:space-between}</style></head><body>
<div class="top"><div class="brand">SINTONIA<small>ADAMA ITALY · ACTION BRIEF</small></div><div class="doc">${esc(b.doc)}<b>${esc(b.generated)}</b>Demonstration Environment</div></div>
<h1>${esc(b.title)}</h1>
<div class="meta"><span>FOR: <b>${esc(b.role)}</b></span><span>PRIORITY: <span class="pri">${esc(b.priority)}</span></span><span>Window: <b>${esc(b.windowFrom)} → ${esc(b.windowTo)}</b> · ${esc(b.windowState)}</span>${b.primary ? `<span>Primary portfolio match: <b>${esc(b.primary)}</b></span>` : ''}</div>
<div class="purpose"><b>Purpose · </b>${esc(b.purpose)}</div>
${b.sections.map(s => `<h2>${esc(s.h)}</h2>${s.bullets ? '<ul>' + s.lines.map(l => `<li>${esc(l)}</li>`).join('') + '</ul>' : s.lines.map(l => `<p>${esc(l)}</p>`).join('')}`).join('')}
${showLoop ? `<div class="loop"><b>OSSERVAZIONI DI CAMPO</b><p>Le osservazioni raccolte in campo possono rientrare in Sintonia attraverso l'integrazione opzionale della rete commerciale. Sintonia riceve e classifica; non richiede l'invio di messaggi.</p></div>` : ''}
<div class="foot"><span>Facts read from the Sintonia model at reference date ${esc(b.generated)}. Demonstration only. No availability, order, share or ROI data is implied.</span><span>Listen &gt; Learn &gt; Deliver</span></div>
<script>window.onload=function(){setTimeout(function(){window.print()},400)}</script></body></html>`;
  }

  window.ITALY_BRIEFS = { build, printHtml, departments: Object.keys(GEN) };
})();
