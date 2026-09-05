    /* §7 · ADAMA Product Intelligence — the product as an entity.
       Identity comes from the registry joined to the public catalog (166 products:
       163 registrations + 3 catalog-only). Connections come ONLY from
       AM.collections.productRelationships — the 163-label audit plus the 219
       registry label-use rows. The demo case fixture is not a source here, and
       D.WINDOWS is no longer read: the windows card is a real join against the 29
       canonical crop windows. */
    let pd = null;
    if (AM && s.productId) {
      const e = AM.findProduct(s.productId);
      if (e) {
        /* A label authorisation is NATIONAL. The old row printed the demo case's
           region under every relationship, which invented a regional claim the
           label never makes. Measured: only 15 of 236 relationship rows join to a
           canonical window at all, and 6 crop x issue keys carry more than one
           window in different regions — so no single region is derivable either.
           The line now carries the row's EVIDENCE, localized from the model's own
           English evidence string. Nothing here is a new fact. */
        const EV = {
          VERIFIED_LABEL_MATCH: { it: 'Letto sull\'etichetta ufficiale', en: 'Read on the official label' },
          RELATED_PORTFOLIO: { it: 'Riga d\'uso autorizzata nel registro nazionale', en: 'Authorised use row in the national registry' },
          LABEL_CHECK_NEEDED: { it: 'Etichetta da verificare per questa combinazione', en: 'Label still to be read for this combination' },
          NO_CONFIRMED_MATCH_CURRENT_READING: { it: 'Non trovato in questa lettura delle etichette', en: 'Not found in this label reading' },
        };
        const evLine = (st) => { const x = EV[st]; return x ? (s.lang === 'en' ? x.en : x.it) : ((T.PSTATE && T.PSTATE[st]) || ''); };
        const U0 = (x) => String(x || '').trim().toUpperCase();

        /* Canonical windows indexed by crop x issue. Exact join only — a product
           whose label names Cercospora beticola is NOT evidence about a window on
           a different issue, and a crop-level fallback would manufacture one. */
        const CWR = (AM.collections.cropWindows && AM.collections.cropWindows.records) || [];
        const winIdx = {};
        CWR.forEach((x) => { const k = U0(x.crop) + '|' + U0(x.issue); (winIdx[k] = winIdx[k] || []).push(x); });

        const relRow = (l) => {
          const hit = winIdx[U0(l.crop) + '|' + U0(l.issue)] || [];
          /* One window -> a real destination. Several windows (same crop x issue in
             different regions) or none -> no destination; a relationship must never
             pick a region for the reader. */
          const dest = hit.length === 1 ? hit[0].id : null;
          return { crop: cl(l.crop), issue: il(l.issue), region: evLine(l.strength), go: () => dest && this.openWindow(dest) };
        };
        const byCropIssue = (a, b) => String(a.crop).localeCompare(String(b.crop)) || String(a.issue).localeCompare(String(b.issue));
        const verified = e.verifiedLinks.map(relRow).sort(byCropIssue);
        const related = e.relatedLinks.map(relRow).sort(byCropIssue);
        const checkNeeded = e.checkNeededLinks.map(relRow).sort(byCropIssue);
        const rejected = e.rejectedLinks.map(relRow).sort(byCropIssue);

        /* Windows the product is actually connected to, via its own relationship
           rows. Measured: 9 of 166 products reach a canonical window this way,
           28 window links in total. Status text and colour come from the canonical
           status and the record's presentation block, never from a date guess. */
        const seenW = {};
        const wins = [];
        e.links.forEach((l) => (winIdx[U0(l.crop) + '|' + U0(l.issue)] || []).forEach((x) => {
          if (seenW[x.id]) return; seenW[x.id] = 1;
          wins.push({
            label: il(x.issue) + ' · ' + x.region,
            state: wst(x.canonicalStatus || x.status || 'DATE_UNKNOWN'),
            color: (x.ui && x.ui.status && x.ui.status.color) || '#B1A9A7',
            go: () => this.openWindow(x.id),
          });
        }));
        const winsTop = wins.slice(0, 4);

        /* Resistance documented in Italy for a species this product's label names
           as a target. The old code matched on GENUS only, which would have tied a
           product targeting Amaranthus retroflexus to Amaranthus palmeri resistance
           — a fabricated claim. Genus + species now: 49 of 166 products match,
           against 65 under the genus-only rule. It also read r.SPECIES / r.MECHANISM,
           keys the model no longer exposes, so the card rendered for 0 products.
           MECHANISM is NOT_APPROVED_FOR_DISPLAY on 34/34 records (internal Portuguese
           working notes), so the second line carries the authority and the regions
           where resistance is documented — both plain facts, 34/34 filled. */
        const taxon = (x) => String(x || '').split('—')[0].replace(/\([^)]*\)/g, ' ').replace(/[^A-Za-z ]/g, ' ').trim().split(/\s+/).slice(0, 2).join(' ').toUpperCase();
        const RES = (AM.collections.resistance && AM.collections.resistance.records) || [];
        const resIdx = {};
        RES.forEach((r) => { const k = taxon(r.species); if (k) (resIdx[k] = resIdx[k] || []).push(r); });
        const seenR = {};
        const res = [];
        (e.targets || []).forEach((tg) => (resIdx[taxon(tg)] || []).forEach((r) => {
          if (seenR[r.id]) return; seenR[r.id] = 1;
          /* The species string carries a Portuguese research tail after an em dash on
             the Lolium rows; cut the tail, never the taxon — parentheses stay. */
          const sp = String(r.species || '').split(' — ')[0].trim();
          const reg = (r.regions || []).join(', ');
          res.push({ label: sp, mech: [r.authority, reg].filter(Boolean).join(' · ') });
        }));
        const resTop = res.slice(0, 3);

        pd = {
          name: e.name,
          /* ai is an array on 163/166 (the 3 catalog-only items carry none); the
             markup prints it raw, so join it here. */
          ai: (Array.isArray(e.ai) && e.ai.length) ? e.ai.join(' + ') : T.prodNotObservable,
          category: e.categoryLabel || '—',
          inCommercial: e.inCommercial, commercialL: e.inCommercial ? T.prodInCatalog : T.prodNotInCatalog,
          commercialColor: e.inCommercial ? '#00B152' : '#B1A9A7',
          inRegulatory: e.inRegulatory, regulatoryL: e.inRegulatory ? T.prodRegistered : T.prodNotRegistered,
          regulatoryColor: e.inRegulatory ? '#00B152' : '#B1A9A7',
          verified, hasVerified: verified.length > 0,
          /* RELATED_PORTFOLIO is 217 of 236 rows and is the only class 16 of the 26
             connected products have. It has no card in the markup yet — see the
             report; until that card lands these rows are computed and not shown. */
          related, hasRelated: related.length > 0, relatedCount: related.length,
          checkNeeded, hasCheckNeeded: checkNeeded.length > 0,
          rejected, hasRejected: rejected.length > 0,
          /* Absence of a row is not absence of a product: noRel now means no tier
             produced a row (140 of 166 products), and the rejected card keeps
             t.absenceRule under it. */
          noRel: e.links.length === 0,
          wins: winsTop, hasWins: winsTop.length > 0,
          res: resTop, hasRes: resTop.length > 0,
          goOpps: () => this.radarWith({ fProduct: e.name }),
        };
      }
    }
