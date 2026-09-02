/* Sintonia · department Action Brief generator (local, from fixtures). Each department gets a different document structure. */
(function () {
  const S = (h, lines, bullets) => ({ h, lines: lines.filter(Boolean), bullets: !!bullets });
  const prodLine = (p) => p ? `${p.name} — ${p.ai} · crops: ${p.crops.join(', ')} · targets: ${p.targets.join(', ')} · ${p.use} · ${p.moa}` : null;
  const window_ = (c) => `${c.wsLabel} → ${c.weLabel} · ${c.windowLine} · crop stage: ${c.stage} · signal: ${c.signal} · label timing: ${c.label}`;
  const fieldLines = (c) => c.fieldMessages.length ? c.fieldMessages.map(m => `${m.person} · ${m.when}: “${m.text}” → ${m.signal}`) : ['No field message on this case yet — field validation requested.'];
  const compLines = (c) => c.competitors.map(k => `${k.company} · ${k.items} recent items · ${k.type} · ${k.topic} · ${k.days}d ago (activity observed only; no strategy or spend inferred)`);
  const sourcesLine = (c) => `${c.source}. Supported by field ${c.evidence.field} · official ${c.evidence.official} · science ${c.evidence.science} · people ${c.evidence.people} · market ${c.evidence.market} connected observations.`;
  const nv = (c) => c.watch.map(w => w);

  const GEN = {
    'SALES / RTV': (c) => ({
      doc: 'FIELD SALES ACTION BRIEF', role: 'Technical Sales Representative', pages: '1–2 pages',
      purpose: 'Help the representative enter customer conversations with the current context and a clear, label-compliant discussion path.',
      sections: [
        S('1 · What is happening', [c.happening]),
        S('2 · Where', [`${c.regionLabel} · ${c.crop}. Validate next in: ${c.adjacent.join(', ')}.`]),
        S('3 · Why this matters now', [c.why]),
        S('4 · Current crop / application window', [window_(c)]),
        S('5 · What ADAMA can offer', c.productObjs.length ? c.productObjs.map(prodLine) : ['No confirmed ADAMA label position yet — do not position a product until Regulatory / Portfolio confirms.'], true),
        S('6 · What we know', c.know, true),
        S('7 · What still needs validation', nv(c), true),
        S('8 · Customer conversation guide', [
          `OPEN — “We are following ${c.issue.toLowerCase()} signals on ${c.crop.toLowerCase()} in ${c.region} and the crop timing makes it worth reviewing protection now.”`,
          'UNDERSTAND — listen first; do not assert incidence the customer has not seen.',
          c.primary ? `CONNECT — “ADAMA has registered portfolio options that may fit this crop and target. Let us confirm the exact label position and field timing for your situation.”` : 'CONNECT — “We are checking our portfolio position for this situation and will come back with a confirmed label answer.”',
          c.primary ? `PRODUCT — ${c.primary}: ${c.primaryAi} · crop fit ${c.crop} · target fit ${c.primaryObj.targets.join(' / ')} · label timing ${c.label}. Only verified label facts; never claims outside the approved label; never invent efficacy.` : null
        ], true),
        S('9 · Questions to ask the customer', ['What crop stage are you seeing?', 'Have you observed symptoms or captures?', `Has ${c.issue.toLowerCase()} already been confirmed on your farm?`, 'What was the previous treatment?', 'What field conditions are you seeing?', 'Are you already evaluating a treatment decision?'], true),
        S('10 · Why talk about this now', [`Current field signal exists (${c.signal.toLowerCase()})`, 'Crop timing is relevant', c.primary ? 'Registered ADAMA portfolio match exists' : 'Portfolio position under confirmation', 'Regional monitoring supports attention', c.fieldMessages.length ? 'Customer questions are being observed by field colleagues' : 'Field voice not yet captured — yours will be the first'], true),
        S('Your objective', ['Open the conversation.', 'Validate what the customer is seeing.', c.primary ? 'Position the relevant ADAMA portfolio within the label.' : 'Do not position a product until confirmed.', 'Return new field intelligence.'], true),
        S('11 · What to report back to Sintonia', ['What did the customer report?', 'Was the issue confirmed?', 'What crop stage?', 'What product are they considering?', 'What competitor was mentioned?', 'Should Sintonia continue monitoring this case?'], true),
        S('12 · Sources / date', [sourcesLine(c)])
      ]
    }),
    'MARKETING': (c) => ({
      doc: 'MARKETING ACTION BRIEF', role: 'Marketing · regional communication', pages: '2 pages',
      purpose: 'Give Marketing the context, the supportable message territory and the boundaries needed to prepare regional support material.',
      sections: [
        S('Case', [`${c.issue} · ${c.crop} · ${c.regionLabel} · status ${c.status}`]),
        S('Audience', [`Growers and dealers in ${c.region} ${c.crop.toLowerCase()} districts; ADAMA field sales as first relay.`]),
        S('Why now', [c.why, window_(c)]),
        S('What the field is saying', fieldLines(c), true),
        S('What official / technical sources are saying', [c.happening, c.source]),
        S('ADAMA portfolio relevance', c.productObjs.length ? c.productObjs.map(prodLine) : ['No confirmed label match — communication must not name a product.'], true),
        S('Competitor communication observed', compLines(c), true),
        S('Communication opportunity', [`Regional, timing-led technical communication on ${c.issue.toLowerCase()} in ${c.crop.toLowerCase()} while the window is ${c.windowOpen ? 'open' : 'approaching'}.`]),
        S('Key message territory', ['Timing and monitoring awareness', 'Label-compliant portfolio fit for the crop × target', 'Regional monitoring as the trigger for attention'], true),
        S('Claims we can support', c.know.concat(c.primary ? [`${c.primary} is registered in Italy for ${c.crop}`] : []), true),
        S('Claims we must not make', ['Incidence increasing “across the region” without official confirmation', 'Efficacy, yield or revenue outcomes', 'Anything outside the approved label', 'Competitor strategy, spend or share'], true),
        S('Suggested assets', ['Regional sales support card', 'WhatsApp asset for dealers', 'Technical post', 'Dealer support material', 'Field-sales presentation slide', 'Short agronomic video'], true),
        S('Urgency', [`${c.status} · ${c.windowLine}`])
      ]
    }),
    'MARKET DEVELOPMENT': (c) => ({
      doc: 'MARKET DEVELOPMENT ACTION BRIEF', role: 'Market Development', pages: '1–2 pages',
      purpose: 'Validate the signal, judge regional relevance and decide where to look next.',
      sections: [
        S('What changed', [c.happening, `Last movement: ${c.updatedLabel}. Originated from Future Radar ${c.origin} days ago.`]),
        S('Why this deserves attention', [c.why]),
        S('Regional context', [`${c.regionLabel} — major ${c.crop.toLowerCase()} area (ISTAT regional scale). Adjacent areas: ${c.adjacent.join(', ')}. Regional precision only; no local coordinates.`]),
        S('Portfolio connection', c.productObjs.length ? [`Primary: ${c.primary} (${c.primaryAi}); ${c.moreMatches} further registered matches.`] : ['No confirmed portfolio position — Regulatory / Portfolio check requested.']),
        S('Field voice', fieldLines(c), true),
        S('What needs validation', nv(c), true),
        S('Where to validate next', c.adjacent.map(a => `${a} — check regional bulletin and field colleagues for the same ${c.issue.toLowerCase()} signal`), true),
        S('Who to contact / listen to', [c.source, 'Field sales representatives in the region', 'Producer organisations and technical networks covering the crop'], true),
        S('Competitor context', compLines(c), true),
        S('Next 48h / 7 days', ['48h — confirm the signal with the next regional update and one field colleague', '7 days — decide expand / hold; brief Sales and Marketing if confirmed'], true)
      ]
    }),
    'TECHNICAL / SCIENCE': (c) => ({
      doc: 'TECHNICAL VALIDATION BRIEF', role: 'Technical / Science', pages: '2–3 pages',
      purpose: 'Validate agronomic pressure and application timing. This is not a sales document.',
      sections: [
        S('Signal under review', [`${c.issue} (${c.latin}) on ${c.crop} · ${c.regionLabel}`]),
        S('Agronomic evidence available', [c.happening, c.source]),
        S('Crop stage', [c.stage]),
        S('Disease / pest signal', [c.signal]),
        S('Official monitoring', [`Regional monitoring reports referenced; ${c.evidence.official} official observations connected.`]),
        S('Scientific context', [`${c.evidence.science} topic-linked scientific records connected to this case. Author affiliation is not treated as field location.`]),
        S('Label timing', [c.label, ...(c.productObjs.map(prodLine))], true),
        S('Field voice (unverified)', fieldLines(c), true),
        S('What is still unknown', nv(c), true),
        S('Questions to validate', ['Is the reported stage consistent with the phenology model for the region?', 'Does the signal meet the regional intervention threshold?', 'Does the label window overlap the current stage?', 'Any weather driver that changes timing this week?', 'Is there resistance-management guidance to attach?'], true),
        S('Recommendation format', ['Return: CONFIRMED / NOT CONFIRMED / NEEDS MORE DATA, with date and source.'])
      ]
    }),
    'REGULATORY / PORTFOLIO': (c) => ({
      doc: 'REGULATORY & PORTFOLIO CHECK', role: 'Regulatory / Portfolio', pages: '1–2 pages',
      purpose: 'Confirm authorisation and label positioning for the products linked to this case before any field or marketing message.',
      sections: [
        S('Case', [`${c.issue} · ${c.crop} · ${c.regionLabel}`]),
        S('Products linked', c.productObjs.length ? c.productObjs.map(p => `${p.name} · active ingredient: ${p.ai} · crop: ${c.crop} · target: ${p.targets.join(' / ')} · label timing: ${p.use} · ${p.moa}`) : ['None linked — portfolio search requested for this crop × target.'], true),
        S('Italy authorisation', ['Confirm current status in the national database (Banca Dati Fitosanitari) for each product on this crop.']),
        S('Dose · application interval · maximum applications', ['Not shown by Sintonia — to be read from the current label record. Sintonia never derives dose.']),
        S('Expiry / regulatory context', ['Confirm authorisation expiry and any pending renewal, restriction or buffer-zone condition.']),
        S('Uncertainties', ['Products flagged “See label record” have unconfirmed active-ingredient data in the demo pack', c.primary ? null : 'No product matched — confirm whether any ADAMA position exists'], true),
        S('Requires manual confirmation', ['Label target wording vs. observed pest/disease', 'Crop listing (including crop group)', 'Regional or seasonal restrictions', 'Status change alerts subscribed'], true),
        S('Return to', ['Sales, Marketing and Market Development are blocked on this check for product naming.'])
      ]
    }),
    'SUPPLY': (c) => ({
      doc: 'SUPPLY READINESS REQUEST', role: 'Supply', pages: '1 page',
      purpose: 'Handoff request — external intelligence cannot know inventory. This is not a stock claim.',
      sections: [
        S('Case', [`${c.issue} · ${c.crop} · ${c.regionLabel} · ${c.status}`]),
        S('Portfolio products', c.productObjs.length ? c.productObjs.map(p => p.name) : ['No confirmed products'], true),
        S('Timing', [window_(c)]),
        S('Why demand should be reviewed', [c.why, c.fieldMessages.length ? `${c.fieldMessages.length} field message(s) report customer interest.` : null]),
        S('Request', ['Please check internal availability and readiness for the region and window above. Sintonia has no view of stock, orders or forecast.'])
      ]
    })
  };

  const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;');
  function build(dept, c) {
    const g = GEN[dept]; if (!g) return null;
    const b = g(c); b.dept = dept; b.case = c; b.title = `${c.issue} · ${c.crop} · ${c.regionLabel}`; b.priority = c.status;
    b.generated = new Date().toLocaleString('en-GB', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' });
    b.summary = `${b.doc} — ${b.title}\nFor: ${b.role} · Priority: ${b.priority} · Generated ${b.generated} · Sintonia ADAMA Italy · Demonstration environment\n\n` + b.sections.map(s => s.h.toUpperCase() + '\n' + s.lines.map(l => (s.bullets ? '• ' : '') + l).join('\n')).join('\n\n');
    return b;
  }
  function printHtml(b) {
    const base = document.baseURI.replace(/[^/]*$/, '');
    const col = b.case.category.color; const showLoop = b.dept === 'SALES / RTV';
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
<div class="top"><div class="brand">SINTONIA<small>ADAMA ITALY · ACTION BRIEF</small></div><div class="doc">${esc(b.doc)}<b>Generated ${esc(b.generated)}</b>Demonstration Environment</div></div>
<h1>${esc(b.title)}</h1>
<div class="meta"><span>FOR: <b>${esc(b.role)}</b></span><span>PRIORITY: <span class="pri">${esc(b.priority)}</span></span><span>Window: <b>${esc(b.case.wsLabel)} → ${esc(b.case.weLabel)}</b> · ${esc(b.case.windowLine)}</span>${b.case.primary ? `<span>Primary portfolio match: <b>${esc(b.case.primary)}</b></span>` : ''}</div>
<div class="purpose"><b>Purpose · </b>${esc(b.purpose)}</div>
${b.sections.map(s => `<h2>${esc(s.h)}</h2>${s.bullets ? '<ul>' + s.lines.map(l => `<li>${esc(l)}</li>`).join('') + '</ul>' : s.lines.map(l => `<p>${esc(l)}</p>`).join('')}`).join('')}
${showLoop ? `<div class="loop"><b>OSSERVAZIONI DI CAMPO</b><p>Le osservazioni raccolte in campo possono rientrare in Sintonia attraverso l'integrazione opzionale della rete commerciale. Sintonia riceve e classifica; non richiede l'invio di messaggi.</p></div>` : ''}
<div class="foot"><span>Illustrative intelligence based on Italian public-source scenarios. Demonstration only. No sales, stock, share or ROI data is implied.</span><span>Listen &gt; Learn &gt; Deliver</span></div>
<script>window.onload=function(){setTimeout(function(){window.print()},400)}</script></body></html>`;
  }
  window.ITALY_BRIEFS = { build, printHtml, departments: Object.keys(GEN) };
})();
