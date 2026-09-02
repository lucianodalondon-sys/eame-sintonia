    // ---- brief
    /* §7 · MEASURED FAILURE, now fixed. The screen resolved its case with
    `CASES.find(id) || CASES[1]` over the 29-record demo fixture, so a real
    opportunity id fell through to a DIFFERENT case's document, and any department
    key the generator does not own made build() return null — which then threw on
    `.doc` while listing the sibling briefs. Both the Italian and the English
    "Action brief" screens were dead. The case is resolved BY ID ONLY, from the
    model, with no neighbour fallback; an unresolved id leaves br === null and
    `isBrief` (which already reads `!!br`) hides the screen instead of throwing.

    italy-briefs.js now reads every fact from the model itself and accepts the
    record only as a ROUTING KEY — it reads c.id, c.windowId, c.products /
    c.productObjs[].name, c.primary, c.fieldMessages and c.category, nothing else.
    So this block's whole job is to hand it an honest key. */
    let br = null;
    if (s.view === 'brief' && window.ITALY_BRIEFS && APP0) {
      /* Scenario mode is the ONLY door the 29 legacy presentation cases have onto
      this screen. Default off, never merged into the real pool otherwise. */
      const briefPool = APP0.opportunities.records.concat(s.showScenarios
        ? /*@EXPLICIT_DEMO the 29 legacy presentation cases, provenance DEMO_SCENARIO, reachable only behind the Future Radar scenario switch and never counted as opportunities*/ APP0.opportunityScenarios.records
        : []);
      const bcase = briefPool.filter(o => o.id === s.caseId)[0] || null;
      /* The department catalogue is the generator's own key list, not the demo
      case's invented `actions` array — cs0.actions carried 4-5 rows of fabricated
      what / why / when per case. Which brief templates exist is a document
      catalogue, not a fact about this case. */
      const bdepts = window.ITALY_BRIEFS.departments || [];
      const bdept = bdepts.indexOf(s.briefDept) >= 0 ? s.briefDept : null;

      /* THE ID COLLISION. italy-briefs.js resolves the canonical window with
      `cropWindows.legacyCaseId === c.id`, and those legacyCaseIds are the LEGACY
      case numbering (IT-OPP-001..029, the 29-case fixture) — which the three real
      upstream opportunities happen to reuse. Id equality alone is therefore a
      coincidence, not a relation. The model's own declared synonym tables settle
      it: the window's crop must be in the opportunity's cropKeys and its region in
      the opportunity's regionKeys. MEASURED on the 3 real records — IT-OPP-001
      (Grapevine / Veneto) and IT-OPP-002 (Maize / Friuli-Venezia Giulia) agree on
      both axes; IT-OPP-003 does NOT — it is the national ADAMA authorisation-expiry
      calendar (cropKeys [] by upstream decision, regionKeys []) while window
      IT-OPP-003 is Durum Wheat · Fusarium Head Blight · Toscana. So 1 brief in 3
      would have carried another case's dates, status and stage. Unverified, the id
      does not travel and the document says the window is not established. */
      const winFor = (o) => {
        const w = APP0.cropWindows.records.filter(x => x.legacyCaseId === o.id)[0] || null;
        if (!w) return null;
        return ((o.cropKeys || []).indexOf(w.crop) >= 0 && (o.regionKeys || []).indexOf(w.region) >= 0) ? w : null;
      };

      /* A real opportunity and a legacy case object share nothing but an id, so
      the generator receives one shape. Everything here is either an upstream fact
      or an explicit absence — no date, stage, evidence count, field observation or
      competitor row is manufactured on the way through. */
      const routeCase = (o) => {
        if (o.isScenario) return o;                    // legacy shape; the generator already speaks it
        const W = winFor(o);
        return {
          /* id doubles as the window routing key, so it travels only when the
          join above is evidenced. Blocked, the generator resolves no window and
          prints WINDOW NOT ESTABLISHED — which is the true answer. */
          id: W ? o.id : null, windowId: W ? W.windowId : null,
          /* Declared by the upstream opportunity record itself (6 on IT-OPP-001,
          0 on IT-OPP-002 and IT-OPP-003); the generator resolves each name against
          the regulatory model and prints only registry facts. Ordered by the
          model's own label-audit grade so the verified matches lead — order is
          presentation, the grades and the names are not restated here. */
          products: (o.productLinks && o.productLinks.length
            ? o.productLinks.slice().sort((x, y) => x.strengthRank - y.strengthRank).map(l => l.name)
            : (o.adamaProducts || [])),
          /* Rule 10 · MEASURED on IT-OPP-001: asked in the audit's own vocabulary
          the six TAU-FLUVALINATE products come back 2 VERIFIED_LABEL_MATCH
          (MAVRIK SMART, EVURE PRO) and 4 LABEL_CHECK_NEEDED — never "no product".
          Nothing is hidden and nothing is promoted: the model ranks no product
          above another, so no "primary portfolio match" is asserted. */
          primary: null,
          /* 0 of 18 field-message records in this package are real. */
          fieldMessages: [],
          category: o.ui,
          /* Not read by the generator today. Carried so it can fall back when no
          canonical window resolves, instead of printing three NON NOTO in the
          document title. These are the model's CANONICAL keys, never the raw
          upstream columns: CROP / ISSUE / REGION arrive in the analyst's
          Portuguese ("Videira", "Flavescência dourada …", "Itália (nacional)")
          and must not reach an Italian client. Null when the model resolved no
          key — IT-OPP-003 has cropKeys [] and issueKey null by upstream decision. */
          crop: (o.cropKeys || [])[0] || null, issue: o.issueKey || null,
          region: (o.regionKeys || []).join(' · ') || null,
          issueType: o.issueType || null,
        };
      };

      const b = (bcase && bdept) ? window.ITALY_BRIEFS.build(bdept, routeCase(bcase)) : null;
      if (b) {
        /* Rule 3 · a section with nothing truthful left in it is omitted rather
        than printed as an empty header, and a line that interpolated a value we do
        not have is not a fact. A smaller truthful document beats a padded one. */
        const dead = (l) => !l || /\b(?:null|undefined|NaN)\b/.test(l) || l.indexOf('[object Object]') >= 0;
        const kept = b.sections
          .map(x => Object.assign({}, x, { lines: (x.lines || []).filter(l => !dead(l)) }))
          .filter(x => x.lines.length);
        /* Copy summary, Share and the printed PDF must say exactly what the screen
        says, so the body is re-derived from the kept sections. The generator's own
        header line is reused verbatim rather than restated here, so its wording and
        its single reference-date stamp cannot drift out of sync with this block.
        MEASURED today: 0 lines and 0 sections of 481/180 are dropped — the filter is
        a guard against a future regression, not a live edit. */
        if (kept.length !== b.sections.length || kept.some((x, i) => x.lines.length !== b.sections[i].lines.length)) {
          b.summary = String(b.summary || '').split('\n\n')[0] + '\n\n'
            + kept.map(x => x.h.toUpperCase() + '\n' + x.lines.map(l => (x.bullets ? '• ' : '') + l).join('\n')).join('\n\n');
        }
        b.sections = kept;
        const DEPT_TOK = /*@VISUAL_ONLY department accent and soft ink only; the department list itself comes from ITALY_BRIEFS.departments and no fact is read from this table*/ D.DEPT || {};
        const deptTok = (k) => DEPT_TOK[k] || { color: '#978B87', soft: '#C3BCBA' };
        br = Object.assign(b, {
          accent: deptTok(bdept).color,
          /* The priority pill is the canonical window status, tinted with the
          window's own category token — not the demo case's `st.color`. */
          priColor: b.accentColor || '#8F8886',
          showLoop: bdept === 'SALES / RTV',
          sections: b.sections.map(x => Object.assign({}, x, { hUpper: x.h.toUpperCase() })),
          backToCase: () => this.openCase(bcase.id),
          copyLabel: s.copied ? 'Copied ✓' : 'Copy summary',
          download: () => { const w = window.open('', '_blank'); if (w) { w.document.open(); w.document.write(window.ITALY_BRIEFS.printHtml(b)); w.document.close(); } },
          copy: () => { if (navigator.clipboard) navigator.clipboard.writeText(b.summary).then(() => this.setState({ copied: true })); else this.setState({ copied: true }); },
          share: () => { const body = encodeURIComponent(b.summary.slice(0, 1800)); window.open('mailto:?subject=' + encodeURIComponent(b.doc + ' · ' + b.title) + '&body=' + body, '_self'); },
          /* Sibling briefs: the other templates for the SAME case. build() returns
          null for a key it does not own — that null is what used to throw here —
          so the row is skipped instead of dereferenced. */
          others: bdepts.filter(dp => dp !== bdept).map(dp => {
            const ob = window.ITALY_BRIEFS.build(dp, b.case);
            return ob ? { label: dp === 'SALES / RTV' ? 'SALES / FIELD SALES' : dp, color: deptTok(dp).color, soft: deptTok(dp).soft, doc: ob.doc, go: () => this.openBrief(bcase.id, dp) } : null;
          }).filter(Boolean),
        });
      }
    }
