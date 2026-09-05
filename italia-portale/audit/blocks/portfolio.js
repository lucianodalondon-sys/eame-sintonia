    /* §10 · Portafoglio — the commercial catalog and the regulatory universe are
       two DIFFERENT claims about the same name and are never merged into one
       "ADAMA has this product". Measured on this package: 44 catalog items, 163
       registrations, 41 joined by name, 3 catalog-only (BUDGE, EXELGROW,
       PARLEAF — all SPECIALI, matchState REGULATORY_MATCH_NOT_FOUND) and 122
       registry-only. The authorisation holder never contradicts the catalog
       seller here — measured 41/41 identical holders — so nothing is invented to
       reconcile them; only the LINK STATE is published. */
    let port = null;
    if (AM) {
      const isComm = s.portTab === 'commercial';
      const universe = AM.products.filter(p => isComm ? p.inCommercial : p.inRegulatory);
      /* The link between the two tabs is the whole point of having two tabs, so
         it is stated as a number instead of being left to the reader: 41 of 44
         catalog items carry a matched registration, and those same 41 are the
         only registrations proved to be publicly sold. */
      const linked = universe.filter(p => p.inCommercial && p.inRegulatory).length;
      const cats = [...new Set(universe.map(p => p.categoryLabel).filter(Boolean))].sort();
      const shown = universe.filter(p => !s.portCat || p.categoryLabel === s.portCat);
      /* The card badge line is two bare glyphs with no legend anywhere on this
         screen, so the legend is stated in the four audited strength names rather
         than left to be guessed. △ reads 0 on 166/166 products: the rebuilt
         relationship contract produces 12 VERIFIED_LABEL_MATCH rows (6 products),
         217 RELATED_PORTFOLIO rows (19 products), 7 NO_CONFIRMED rows (6 products)
         and zero LABEL_CHECK_NEEDED rows — the amber class only ever existed
         because a demo case named a product. */
      const PS = T.PSTATE || {};
      const legend = '✓ ' + (PS.VERIFIED_LABEL_MATCH || 'VERIFIED_LABEL_MATCH')
        + ' · △ ' + (PS.LABEL_CHECK_NEEDED || 'LABEL_CHECK_NEEDED');
      /* Category tint only. The pest / disease / weed class is a canonical fact
         and already carries its colour in the model, so the hex is read from
         there instead of being re-typed here. SPECIALI is a catalog grouping with
         no canonical issue class, so it keeps the ADAMA accent it has always had,
         and an unclassified product falls to the model's neutral grey rather than
         borrowing the SPECIALI accent as it did before. */
      const CU = AM.CATEGORY_UI || {};
      const TINT = {
        ERBICIDI: (CU.weed || {}).color || '#7DB41E',
        FUNGICIDI: (CU.disease || {}).color || '#00A0DF',
        INSETTICIDI: (CU.pest || {}).color || '#9D1D96',
        SPECIALI: '#F89E18',
      };
      /* The old cap was 60 while port.count reported the unsliced length, so the
         Universo regolatorio tab printed "163/163" over 60 rendered cards. The cap
         now sits above the 166 products the model holds and count reports what is
         actually on screen, so the ratio can no longer be wrong. */
      const items = shown.slice(0, 240);
      port = {
        tabs: [['commercial', T.portCommercialTab], ['regulatory', T.portRegulatoryTab]].map(t => { const on = s.portTab === t[0];
          return { label: t[1], color: on ? '#fff' : '#B1A9A7', bg: on ? 'rgba(0,152,69,0.20)' : 'transparent', border: on ? '#009845' : 'rgba(203,197,195,0.20)', go: () => this.setState({ portTab: t[0], portCat: '' }) }; }),
        note: [
          isComm ? T.portCommercialNote : T.portRegulatoryNote,
          linked + '/' + universe.length + ' → ' + (isComm ? T.prodRegistered : T.prodInCatalog),
          legend,
        ].filter(Boolean).join(' · '),
        cats: [{ v: '', l: T.portAllCats }].concat(cats.map(c => ({ v: c, l: c }))),
        cat: s.portCat, setCat: (ev) => this.setState({ portCat: ev.target.value }),
        count: items.length, total: universe.length,
        items: items.map(p => ({
          name: p.name,
          /* Active substances arrive as an array and were handed to the template
             raw, which printed them comma-jammed. The three catalog-only items
             have no substance list at all because no registration was matched —
             that reason is said out loud instead of leaving the line blank. */
          ai: (p.ai && p.ai.length) ? p.ai.join(' + ')
            : (p.inCommercial && !p.inRegulatory) ? T.prodNotRegistered
            : '—',
          cat: p.categoryLabel || '—',
          verified: p.verifiedLinks.length, check: p.checkNeededLinks.length,
          /* Exposed for the badge line the markup still has to grow: 19 products
             carry a RELATED_PORTFOLIO row and today the card shows them as 0 ✓ · 0 △. */
          related: p.relatedLinks.length, rejected: p.rejectedLinks.length,
          catColor: TINT[p.categoryLabel] || (CU.unknown || {}).color || '#8F8886',
          go: () => this.openProduct(p.name)
        })),
        none: shown.length === 0
      };
    }
