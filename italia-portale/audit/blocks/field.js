    // ---- field sales channel · INTEGRAZIONI · DEMO
    /* §10 · Field Sales is an integration DEMONSTRATION, never intelligence. The pool now
       comes from the model, where every record carries provenance SYNTHETIC_DEMO
       (measured on this package: fieldMessages.count 18, real 0, demo 18). Nothing in this
       block writes to a core collection and no number produced here reaches a core count —
       the only escape hatches are s.extraMessages, which the composer owns, and the
       INTEGRAZIONI nav badge. */
    const fmPool = APP0 ? APP0.fieldMessages.records : [];
    const demoMessages = (s.extraMessages || []).concat(fmPool);
    /* The demo records are authored in English on an Italian-default screen. The
       enumerated labels are a closed, short set (measured distinct values: 8 mtype,
       5 channel, 8 signal, 1 proves, 4 validation), so they get an Italian face here.
       The free agronomic timing phrases stay as authored — they carry stage vocabulary. */
    const FIT = {
      'CUSTOMER QUESTION': 'DOMANDA DEL CLIENTE', 'PRODUCT INTEREST': 'INTERESSE SUL PRODOTTO',
      'FIELD OBSERVATION': 'OSSERVAZIONE DI CAMPO', 'COMPETITOR MENTION': 'CITAZIONE DELLA CONCORRENZA',
      'DEALER / COOPERATIVE SIGNAL': 'SEGNALE DA RIVENDITORE / COOPERATIVA', 'WEED OBSERVATION': 'OSSERVAZIONE INFESTANTI',
      'CROP STAGE': 'STADIO DELLA COLTURA', 'APPLICATION TIMING QUESTION': 'DOMANDA SUL MOMENTO DI APPLICAZIONE',
      'GROWER': 'PRODUTTORE', 'DEALER': 'RIVENDITORE', 'COOPERATIVE': 'COOPERATIVA',
      'TECHNICAL ADVISOR': 'TECNICO DI CAMPO', 'UNKNOWN': 'NON NOTO',
      'Customer questions observed': 'Domande dei clienti osservate', 'Customer questions observed · 3': 'Domande dei clienti osservate · 3',
      'Product interest reported': 'Interesse sul prodotto riportato', 'Local concern reported': 'Preoccupazione locale riportata',
      'Competitor mention observed': 'Citazione della concorrenza osservata', 'Channel question reported': 'Domanda dal canale riportata',
      'Field-reported crop stage': 'Stadio della coltura riportato dal campo', 'Application timing question': 'Domanda sul momento di applicazione',
      'This representative reported this. Nothing more.': 'Questo rappresentante ha riferito questo. Nulla di piu.',
      'Single farm, no measurement. Cannot be read as regional resistance — GIRE is the reference for confirmed cases.': 'Una sola azienda, nessuna misura. Non si puo leggere come resistenza regionale — GIRE e il riferimento per i casi confermati.',
      'Adequately scoped to the visited plots. Valid as a local field-reported stage, not as a regional stage.': 'Circoscritto agli appezzamenti visitati. Valido come stadio locale riportato dal campo, non come stadio regionale.',
      'Scoped to the farms followed by this representative.': 'Circoscritto alle aziende seguite da questo rappresentante.',
      'One dealer, one visit. Not evidence of a competitor campaign.': 'Un rivenditore, una visita. Non e prova di una campagna della concorrenza.'
    };
    const fit = (v) => (s.lang === 'it' && FIT[v]) ? FIT[v] : v;
    /* LAGO covers today / Nd / Nmo / N min but not the hour stamps this fixture also
       writes, so half the rep rows read '2h ago' on the Italian screen. */
    const ago = (v) => s.lang === 'it' ? String(LAGO(v) || '').replace(/(\d+)h ago/, '$1h fa') : v;
    /* The state vocabulary is the inbound flow's own vocabulary, so it reuses the flow
       keys instead of a second, untranslated set. */
    const FS_L = { 'CONNECTED': T.fsFlowLinked, 'CLASSIFIED': T.fsFlowClassified, 'NEEDS VALIDATION': T.fsFlowValidate };
    const fsL = (k) => FS_L[k] || L(k);
    const FS_COLOR = { 'CONNECTED': '#00B152', 'NEW SIGNAL': '#978B87', 'NEEDS VALIDATION': '#009845', 'CLASSIFIED': '#00A0DF' };

    /* §13 · A cross-link is offered only when the target entity really exists in the model.
       Measured on the 18 demo messages: 18/18 crops have a canonical crop window; 10/10
       named products resolve in the ADAMA catalogue; 2 name a company that exists in
       competitorCompanies; but only 3 of the 9 caseIds resolve to a real opportunity
       (IT-OPP-001/002/003 — the other six point at demo cases 004/006/007/009/021), and
       0 of 18 resolve to a real Future Radar signal, because the three real signals are
       Fusarium/mycotoxin on maize, Fusarium/DON on wheat and one regulatory record. */
    const oppOf = (m) => (m.caseId && APP0) ? (APP0.opportunities.records.find(o => o.id === m.caseId || o.legacyCaseId === m.caseId) || null) : null;
    const winOf = (m) => (m.crop && APP0) ? (APP0.cropWindows.records.find(x => x.crop === m.crop) || null) : null;
    const coOf = (m) => (m.competitors || []).find(n => APP0 && APP0.competitorCompanies.records.some(x => x.name === n)) || null;
    const relatedFor = (m) => {
      const out = [];
      const o = oppOf(m); if (o) out.push({ label: (T.lblOpportunities || 'OPPORTUNITA').toUpperCase(), go: () => this.openCase(o.id) });
      const w = winOf(m); if (w) out.push({ label: (T.navWindows || 'Crop Windows').toUpperCase(), go: () => this.openWindow(w.id) });
      if (m.product && AM && AM.findProduct(m.product)) out.push({ label: (T.navPortfolio || 'Portfolio').toUpperCase(), go: () => this.openProduct(m.product) });
      const co = coOf(m); if (co) out.push({ label: (T.navCompetitors || 'Competitor Watch').toUpperCase(), go: () => this.compWith({ fCompany: co }) });
      return out;
    };
    /* The card footer used to promise "Future Radar · issue · region" for any message with
       no case. That destination does not exist for a single one of these records, so the
       footer now names the nearest thing that does exist, and never invents a third. */
    const fmDeco = (m) => {
      const o = oppOf(m), w = winOf(m), rel = relatedFor(m);
      return Object.assign({}, m, {
        productLabel: m.product || (coOf(m) ? fit('COMPETITOR MENTION') + ' · ' + m.competitors.join(', ') : ((T.PSTATE && T.PSTATE.LABEL_CHECK_NEEDED) || 'LABEL CHECK NEEDED')),
        targetLabel: o ? (T.lblOpportunities || 'OPPORTUNITA').toUpperCase() + ' · ' + o.id
          : w ? (T.navWindows || 'Crop Windows').toUpperCase() + ' · ' + il(w.issue) + ' · ' + w.region
            : (T.fsFlowValidate || 'TO VALIDATE'),
        go: () => o ? this.openCase(o.id) : w ? this.openWindow(w.id) : this.go({ view: 'field' }),
        went: rel, hasRelated: rel.length > 0
      });
    };
    /* The five steps are the module's published contract, in the client's language:
       MESSAGGIO IN ARRIVO → RICEVUTO → CLASSIFICATO → COLLEGATO → DA VALIDARE. The
       sub-lines say what the module does NOT do, because that is the part a reader
       assumes wrongly. Colours and tints are presentation only. */
    const IT = s.lang === 'it';
    const inboundFlow = [
      { n: '1', step: T.fsFlowMessageIn || 'INBOUND MESSAGE', what: IT ? 'testo, foto o audio dalla rete di campo' : 'text, photo or audio from the field network', color: '#00B152', tint: 'rgba(0,177,82,0.14)', ring: 'rgba(0,177,82,0.45)' },
      { n: '2', step: T.fsFlowReceived || 'RECEIVED', what: IT ? 'Sintonia riceve. Non invia messaggi da questo modulo.' : 'Sintonia receives. It does not send messages from this module.', color: '#00A0DF', tint: 'rgba(0,160,223,0.14)', ring: 'rgba(0,160,223,0.45)' },
      { n: '3', step: T.fsFlowClassified || 'CLASSIFIED', what: IT ? 'coltura · problema · regione · tipo · canale' : 'crop · issue · region · type · channel', color: '#F5B317', tint: 'rgba(245,179,23,0.12)', ring: 'rgba(245,179,23,0.42)' },
      { n: '4', step: T.fsFlowLinked || 'LINKED', what: IT ? 'solo a finestre, prodotti e aziende che esistono davvero' : 'only to windows, products and companies that really exist', color: '#C77BC3', tint: 'rgba(157,29,150,0.16)', ring: 'rgba(157,29,150,0.45)' },
      { n: '5', step: T.fsFlowValidate || 'TO VALIDATE', what: IT ? 'nessun messaggio diventa evidenza senza validazione' : 'no message becomes evidence without validation', color: '#00B152', tint: 'rgba(0,177,82,0.14)', ring: 'rgba(0,177,82,0.45)' }
    ];
    const fieldMessages = demoMessages.filter(m => !s.fieldState || m.state === s.fieldState)
      .map(fmDeco).map(m => Object.assign({}, m, {
        state: fsL(m.state), color: m.color || FS_COLOR[m.state] || '#978B87',
        mtype: fit(m.mtype || 'FIELD OBSERVATION'), mtypeColor: m.mtypeColor || '#978B87', mtypeText: m.mtypeText || '#B1A9A7',
        channel: fit(m.channel || 'UNKNOWN'), signal: fit(m.signal), when: ago(m.when),
        proves: fit(m.proves || 'This representative reported this. Nothing more.'),
        cropL: cl(m.crop), issueL: il(m.issue), hasValidation: !!m.validation, validation: fit(m.validation || '')
      }));
    /* §10 · The KPI strip used to add FIELD_KPI (the fixture's own tally), a second
       hand-written copy of these
       counts, to the live pool. It is gone: every tile is now counted off the pool the
       screen is actually showing. One number moves a lot — "connected to opportunities"
       read 8 because 8 records carry the state CONNECTED, but only 3 of them name an
       opportunity that exists in the model, so the tile now reads 3. */
    const connectedReal = demoMessages.filter(m => !!oppOf(m)).length;
    const nState = (st) => demoMessages.filter(m => m.state === st).length;
    const fieldKpis = [
      { value: demoMessages.length, label: IT ? 'Messaggi dimostrativi ricevuti' : 'Demonstration messages received', color: '#009845' },
      { value: connectedReal, label: IT ? 'Collegati a un’opportunità reale' : 'Linked to a real opportunity', color: '#009845' },
      { value: nState('NEW SIGNAL'), label: IT ? 'Nuovi segnali' : 'New signals', color: '#978B87' },
      { value: [...new Set(demoMessages.map(m => m.region).filter(Boolean))].length, label: IT ? 'Regioni attive' : 'Regions active', color: '#978B87' },
      { value: [...new Set(demoMessages.map(m => m.product).filter(p => p && AM && AM.findProduct(p)))].length, label: IT ? 'Prodotti ADAMA citati' : 'ADAMA products mentioned', color: '#978B87' },
      { value: nState('NEEDS VALIDATION'), label: T.fsFlowValidate || 'To validate', color: '#009845' }
    ];
    /* The chip row hard-coded three states while the pool holds four (CONNECTED 8,
       NEW SIGNAL 4, NEEDS VALIDATION 3, CLASSIFIED 3), so 3 of 18 messages could not be
       reached by any filter. The row is derived from the pool now. */
    const fStates = [...new Set(demoMessages.map(m => m.state).filter(Boolean))];
    const fieldStateChips = [{ key: '', label: L('ALL'), color: '#fff' }].concat(fStates.map(k => ({ key: k, label: fsL(k), color: FS_COLOR[k] || '#978B87' })))
      .map(f => ({ label: f.label, count: f.key ? demoMessages.filter(m => m.state === f.key).length : demoMessages.length, color: s.fieldState === f.key ? '#fff' : f.color, bg: s.fieldState === f.key ? 'rgba(0,152,69,0.25)' : 'transparent', border: s.fieldState === f.key ? '#009845' : f.color + '66', go: () => this.setState({ fieldState: f.key }) }));
    /* parseField still returns the raw enum in `state`, `issue` and `caseObj` because
       sendComposer branches on them; the localized twins are added alongside, never
       instead. issueL/cropL are bound by the markup and were undefined until now. */
    const parsed0 = this.parseField(s.composerText);
    const parsed = Object.assign({}, parsed0, { issueL: il(parsed0.issue), cropL: cl(parsed0.crop), stateL: fsL(parsed0.state), signalL: fit(parsed0.signal) });
    /* The example texts must still parse, so they carry the crop, region and issue tokens
       parseField matches on. Verified against parseField: both language sets score >= 4. */
    const composerExamples = (IT
      ? ['Due olivicoltori in Puglia chiedono della pressione della mosca dell olive prima del prossimo trattamento.',
        'I rivenditori in Emilia-Romagna dicono che i clienti wheat chiedono opzioni per Septoria in primavera.',
        'Clienti in Lombardia citano materiale Bayer su maize piu del solito questa settimana.']
      : ['Two olive growers in Bari asking about fruit fly pressure before the next treatment.',
        'Dealers in Piacenza say wheat customers are asking about Septoria options for spring.',
        'Customers in Cremona mentioning Bayer maize material more than usual this week.'])
      .map(t => ({ label: t.slice(0, 44) + '…', go: () => this.setState({ composerText: t }) }));
    /* @EXPLICIT_DEMO the seven ADAMA technical sales representatives are the demonstration's
       cast: fabricated people, initial 'D', org '… · DEMO', no phone number, no outbound
       action. They live on this labelled screen and nowhere else, so the row no longer
       opens the core Person detail — that screen is for the real, ORCID-identified people.
       Two of the seven are authored as 'Marco R.' and 'Luca F.', which read like employees
       next to five rows that say DEMO out loud; the label is stamped here so all seven do. */
    const tsrs = /*@EXPLICIT_DEMO Field Sales cast, default-off module, feeds no real count*/ D.TSR.map(t => {
      const mine = demoMessages.filter(m => m.region === t.region);
      return Object.assign({}, t, {
        label: /DEMO/i.test(t.label || '') ? t.label : t.label + ' · DEMO',
        contentCount: mine.length, last: mine[0] ? ago(mine[0].when) : '—',
        hasProfile: false, go: () => {}
      });
    });
    /* §2 · The demo never says a field message was ADDED to an opportunity — it was not,
       nothing here mutates a core record. The panel lists the real opportunities these
       messages point at, and only those: 3 rows, down from 8, because five of the demo
       caseIds name opportunities that do not exist in the model. The evidence chips are
       empty because the real opportunity records carry no evidence tally (measured:
       evidence undefined on 3/3), and the count is stamped DEMO so it cannot be read as
       part of that opportunity's evidence.
       The row identifies the opportunity by its CANONICAL keys (issueKey, cropKeys,
       regionKeys), not by title / issue / crop: those three fields are the analyst's
       Portuguese working text on 3/3 real opportunities ("Videira x Flavescência
       dourada, via o vetor Scaphoideus titanus"), and printing them here would put an
       internal note in front of the Italian client. Where a canonical key is missing —
       IT-OPP-003 has issueKey null and no crop, being a portfolio-wide record — the row
       falls back to the record id and to "non noto", never to the Portuguese. */
    const unk = () => IT ? 'non noto' : 'not known';
    /* The markup paints the row icon with url(...), so the token's asset path is what it
       needs; the model's `icon` is a name. The unknown token has no asset on purpose. */
    const catFor = (o) => { const c = o.ui || (AM ? AM.categoryOf(o.issueType) : null) || {}; return Object.assign({}, c, { icon: c.iconAsset || '' }); };
    const fieldCases = (APP0 ? APP0.opportunities.records : []).filter(o => demoMessages.some(m => oppOf(m) === o))
      .map(o => Object.assign({}, o, {
        category: catFor(o),
        issueL: o.issueKey ? il(o.issueKey) : o.id,
        cropL: (o.cropKeys || []).length ? (o.cropKeys || []).map(cl).join(' · ') : unk(),
        region: (o.regionKeys || []).length ? o.regionKeys.join(' · ') : unk(),
        fieldCount: demoMessages.filter(m => oppOf(m) === o).length + ' · DEMO',
        evChips: [], open: () => this.openCase(o.id)
      }));
