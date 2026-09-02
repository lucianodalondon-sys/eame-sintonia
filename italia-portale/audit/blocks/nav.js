    // ---- nav
    /* §1 · Core = external intelligence, so Field Sales inbound stays OUT of the INTELLIGENCE
    group. §5 · it lives in the amber INTEGRAZIONI · DEMO group and its 18 records are read
    from the model's own SYNTHETIC_DEMO collection (provenance 'SYNTHETIC_DEMO', real 0,
    demo 18) instead of the raw inbound fixture — measured field-by-field identical to it on
    all 31 keys, including the 10 caseObj and 2 signalObj joins the case and field screens
    read, so nothing downstream changes shape. */
    const navDemoInbound = (AM && AM.collections.fieldMessages) ? AM.collections.fieldMessages.records : [];
    const allMessages = s.extraMessages.concat(navDemoInbound);

    /* §2 · Every badge in the INTELLIGENCE group is now a count of normalized records.
    Before this block the badges were fixture recounts and four of them were wrong by a wide
    margin: competitors 72 vs 503 real activities, science 36 vs 88, archive 448 vs the
    773-row real index, sources 53 orgs + 39 people = 92 vs a 31-source registry. Three were
    right only by luck — the 29 demo CASES are a 1:1 shadow of the 29 canonical windows, so
    radar and windows keep reading 29, but from the contract instead of the shadow. */
    const navN = (k) => (AM && AM.counts && typeof AM.counts[k] === 'number') ? AM.counts[k] : 0;

    /* §8 · 'sources' counts monitored public routes only (31). The old badge summed 53 demo
    organizations with 39 demo people — and 7 of those people were invented ADAMA Technical
    Sales Representatives, i.e. internal staff, which §1 forbids from the core. People are a
    separate real collection (15 with documented role evidence, 60 OpenAlex researchers) and
    are counted on the Sources screen itself, never folded into this badge.
    §3 · 'market' no longer counts the market-pulse fixture's crop tabs (8 hand-authored
    entries, none carrying a SOURCE_ID). The only real backing is the EU Commission
    Agri-food weekly price observations, so the badge counts those; the fixture's 8 tabs
    included Tomato, Sugar Beet and Apple, for which the real corpus holds zero rows. */
    const navDef = [
      ['radar', T.navRadar, navN('windows')],
      ['future', T.navFuture, navN('futureSignals')],
      ['windows', T.navWindows, navN('windows')],
      ['market', T.navMarket, navN('marketObservations')],
      ['voices', T.navVoices, navN('voices')],
      ['competitors', T.navCompetitors, navN('competitorActivities')],
      ['science', T.navScience, navN('scienceRecords')],
      ['portfolio', T.navPortfolio, navN('products')],
      ['archive', T.navArchive, navN('archive')],
      ['sources', T.navSources, navN('sources')]
    ];
    const navIntegrations = [['field', T.navField, allMessages.length]];
    const activeOf = { radar: 'radar', case: 'radar', brief: 'radar', field: 'field', windows: 'windows', window: 'windows', market: 'market', signal: 'future', future: 'future', competitors: 'competitors', company: 'competitors', event: 'competitors', cproduct: 'competitors', science: 'science', theme: 'science', archive: 'archive', portfolio: 'portfolio', product: 'portfolio', voices: 'voices', sources: 'sources', source: 'sources', person: 'sources', search: '' };
    /* §4 · The green/amber accents, the dot and the active tint are presentation only and stay. */
    const nav = navDef.map(n => { const on = activeOf[s.view] === n[0]; return { label: n[1], count: n[2], go: () => n[0] === 'competitors' ? this.compWith({}) : n[0] === 'radar' ? this.radarWith({ showAll: false }) : this.go({ view: n[0] }), bg: on ? 'rgba(0,152,69,0.13)' : 'transparent', border: on ? 'rgba(0,152,69,0.40)' : 'transparent', dot: on ? '#009845' : 'rgba(151,139,135,0.35)', color: on ? '#fff' : '#9A9391', weight: on ? 600 : 400 }; });
    const navIntegrationItems = navIntegrations.map(n => { const on = activeOf[s.view] === n[0]; return { label: n[1], count: n[2], go: () => this.go({ view: n[0] }), bg: on ? 'rgba(245,179,23,0.13)' : 'transparent', border: on ? 'rgba(245,179,23,0.40)' : 'transparent', dot: on ? '#F5B317' : 'rgba(151,139,135,0.35)', color: on ? '#fff' : '#9A9391', weight: on ? 600 : 400 }; });
