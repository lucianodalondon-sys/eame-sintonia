    // ---- case · opportunity detail
    /* §2 · The detail must open the SAME entity the card opened. The 29 legacy
       presentation cases are a DEMO_SCENARIO collection and they REUSE the real
       ids (measured: demo ids run IT-OPP-001..029, the real ones IT-OPP-001..003),
       so the real collection is searched first and the scenario pool is only
       consulted when the reader explicitly switched scenarios on. An id that
       resolves nowhere reports itself missing; it never opens a neighbour. */
    const csReal = (APP0 ? APP0.opportunities.records : []).find(o => o.id === s.caseId) || null;
    const csScen = (!csReal && s.showScenarios && APP0 && APP0.opportunityScenarios)
      ? /*@EXPLICIT_DEMO labelled scenario mode, default off; it feeds no count, no evidence and no current signal — only this one detail screen, which badges itself through cs.isScenario*/ (APP0.opportunityScenarios.records.find(o => o.id === s.caseId) || null)
      : null;
    const csRec = csReal || csScen;
    const csLK = (AM && AM.lookups) || {};
    const csUIK = (AM && AM.UI) || {};

    /* §11 · The upstream opportunity feed was researched in Portuguese and the
       Portuguese is not confined to prose. Measured on the 3 real records:
       TITLE 3/3, CASE_LABEL 3/3 and FORBIDDEN_LABEL 3/3 are Portuguese, and so
       are IT-OPP-003's CROP and ISSUE, IT-OPP-001's ISSUE clause ('via o vetor'),
       every WHY_IT_MATTERS regional decree string and all 10/10 CURRENT_EVIDENCE,
       WHAT_WE_KNOW, WHAT_WE_DO_NOT_KNOW and INTERPRETATIONS entries. narrative()
       cannot stop the fact fields because they arrive as plain strings, so every
       free-text fact this block renders passes csSafe() first. The marker list
       is audit/lang.mjs plus the words measured in this feed. */
    const CS_PT = /(^|[^\p{L}])(nao|não|são|foi|pelo|pela|então|entao|apenas|nenhum|nenhuma|porque|dados|leitura|rótulo|rotulo|também|tambem|uma|dos|das|muito|depois|antes|revogada|verificado|coluna|época|epoca|registros|milho|trigo|arroz|soja|videira|oliveira|tomate|cereais|ficha|atenção|atencao|cultura|culturas|vencimento|calendário|calendario|transversal|convergencia|convergência|vetor|vetores|dourada|sintomas|tratamentos|ativos|autorizações|autorizacoes)([^\p{L}]|$)/iu;
    const csSafe = (v) => { const x = (v === null || v === undefined) ? '' : String(v).trim(); return (!x || CS_PT.test(x)) ? null : x; };
    const csFold = (v) => String(v === null || v === undefined ? '' : v).normalize('NFD').replace(/[̀-ͯ]/g, '').trim().toUpperCase();

    /* Short interface phrases this screen needs and i18n does not carry yet.
       Wording only: every number and every name printed beside them is read
       from the model. */
    const CS_TX = {
      notACrop: ['Non è una coltura · portafoglio trasversale', 'Not a crop · cross-portfolio'],
      awaiting: ['IN ATTESA DI LOCALIZZAZIONE', 'AWAITING LOCALIZATION'],
      awaitingLong: ['testo non ancora localizzato', 'text not yet localized'],
      notFound: ['CASO NON TROVATO', 'CASE NOT FOUND'],
      noWindow: ['nessuna finestra canonica collegata', 'no canonical window linked'],
      toOpen: ['giorni all’apertura della finestra', 'days until the window opens'],
      closedCycle: ['finestra chiusa · prossimo ciclo', 'window closed · next cycle'],
      evState: ['REGISTRATA · NON PONDERATA', 'RECORDED · NOT SCORED'],
      declaredSources: ['Fonti dichiarate', 'Declared sources'],
      sciWorks: ['lavori scientifici misurati', 'scientific works measured'],
      sciState: ['contesto scientifico', 'science context'],
      noConvergence: ['nessuna misura di convergenza', 'no convergence measure'],
      mandatory: ['Controllo obbligatorio dichiarato da questo record', 'Mandatory control declared by this record'],
      notMandatory: ['Nessun obbligo dichiarato in questo record', 'No obligation declared in this record'],
      recorded: ['elementi registrati', 'items recorded'],
      sourceUnloc: ['descrizione della fonte non ancora localizzata', 'source description not yet localized'],
      ago: ['g fa', 'd ago'],
      appW: ['APPLICAZIONE', 'APPLICATION'],
      monW: ['MONITORAGGIO', 'MONITORING'],
    };
    const csT = (k) => (CS_TX[k] || ['', ''])[s.lang === 'en' ? 1 : 0];
    /* Upstream enums. A code is language-independent, so localizing it changes a
       label and not a fact — the same rule T.WSTATUS already applies. */
    const CS_ENUM = {
      CLOSED_FOR_2026: ['CHIUSA PER IL 2026', 'CLOSED FOR 2026'],
      OPEN_BUT_NARROW: ['APERTA MA STRETTA', 'OPEN BUT NARROW'],
      NOT_APPLICABLE: ['NON APPLICABILE', 'NOT APPLICABLE'],
      OPEN: ['APERTO', 'OPEN'],
      TO_BE_CONFIRMED: ['DA CONFERMARE', 'TO BE CONFIRMED'],
      ANCHORED_BY_SOURCE: ['ANCORATO A UNA FONTE', 'ANCHORED BY SOURCE'],
      CURRENT_SIGNAL: ['SEGNALE CORRENTE', 'CURRENT SIGNAL'],
      MEASURED: ['MISURATO', 'MEASURED'],
    };
    const csEnum = (v) => { const e = CS_ENUM[csFold(v)]; return e ? e[s.lang === 'en' ? 1 : 0] : (v ? String(v).replace(/_/g, ' ') : null); };

    /* §11 · Six crop vocabularies are measured in this package and the
       opportunity feed writes Portuguese. The synonym tables are DECLARED by the
       model (lookups.OPP_CROP, lookups.OPP_ISSUE), never guessed here, and the
       resolution is load-bearing rather than cosmetic: measured with
       ('Grapevine', 'Flavescenza Dorata') MAVRIK SMART and EVURE PRO read
       VERIFIED_LABEL_MATCH, while with the record's own ('Videira', Portuguese
       ISSUE) all six declared products read NO_CONFIRMED_MATCH_CURRENT_READING —
       the screen would state the opposite of the audited label reading (§10). */
    const CS_CANON = ((csLK.CROP_KEY || []).map(x => x.crop));
    const csCropOf = (rec) => {
      if (!rec) return null;
      if (rec.cropKeys && rec.cropKeys.length) return rec.cropKeys[0];
      const raw = csFold(rec.crop);
      const t = (csLK.OPP_CROP || {})[raw];
      if (t && t.length) return t[0];
      return CS_CANON.find(c => csFold(c) === raw) || null;
    };
    const csIssueOf = (rec) => {
      if (!rec) return null;
      const t = (csLK.OPP_ISSUE || {})[csFold(rec.issue)];
      return t || null;
    };

    const CS_MON = T.months || ['GEN', 'FEB', 'MAR', 'APR', 'MAG', 'GIU', 'LUG', 'AGO', 'SET', 'OTT', 'NOV', 'DIC'];
    const csDate = (iso) => { const d = AM ? AM.asDate(iso) : null; return d ? (String(d.getDate()).padStart(2, '0') + ' ' + CS_MON[d.getMonth()]) : null; };
    const csDay = (iso) => { const d = AM ? AM.asDate(iso) : null; return d ? [String(d.getDate()).padStart(2, '0'), String(d.getMonth() + 1).padStart(2, '0'), d.getFullYear()].join('/') : null; };

    /* §13 · The canonical window is a DECLARED relation, not a name match. The
       model joins it on the opportunity's own LEGACY_CASE_ID, which reads
       'IT-HERO-00n' and matches nothing — canonicalWindow measures null on 3/3 —
       while the 29 canonical windows declare LEGACY_CASE_ID = 'IT-OPP-00n', i.e.
       the opportunity id. The fallback below honours that declared edge but
       REFUSES it unless BOTH the canonical crop and the canonical issue agree,
       because the id space collides: window IT-OPP-003 is Durum Wheat x Fusarium
       Head Blight while real IT-OPP-003 is the authorisation-expiry calendar. */
    const csCropK0 = csCropOf(csRec);
    /* A scenario record already carries the canonical vocabulary, so it needs no
       synonym table; a real record only resolves through the declared one. */
    const csIssueK0 = csIssueOf(csRec) || (csScen ? csSafe(csScen.issue) : null);
    const csWinRec = (() => {
      if (!csRec) return null;
      if (csRec.canonicalWindow) return csRec.canonicalWindow;
      const w = (APP0 ? APP0.cropWindows.records : []).find(x => csFold(x.legacyCaseId) === csFold(csRec.id)) || null;
      if (!w || !csCropK0 || !csIssueK0) return null;
      return (csFold(w.crop) === csFold(csCropK0) && csFold(w.issue) === csFold(csIssueK0)) ? w : null;
    })();

    /* Canonical vocabulary first: it is CANONICAL precedence, it is already
       Italian and it is what T.CROPS / T.ISSUES and the label audit key on. */
    const csCropK = (csWinRec && csWinRec.crop) || csCropK0 || null;
    const csIssueK = (csWinRec && csSafe(csWinRec.issue)) || csSafe(csIssueK0) || null;
    const csIssueTxt = csIssueK ? il(csIssueK) : (csSafe(csRec && csRec.issue) || null);
    const csCropTxt = csCropK ? cl(csCropK) : (csRec ? csT('notACrop') : '');
    /* The record's own ISSUE keeps its Latin binomials whole and is never split
       at '(' (§11). It only reaches the screen when it is client-safe: measured,
       IT-OPP-002's survives and IT-OPP-001's and IT-OPP-003's do not. */
    const csIdent = csSafe(csRec && csRec.issue);
    const csRegion = csSafe(csRec && csRec.region) || '';

    /* §4 · Category tint. The classification is a fact and comes from ISSUE_TYPE;
       when a CANONICAL window is linked its ISSUE_TYPE outranks the record's own,
       measured because the opportunity feed writes 'FITOPLASMA' and 'NAO SEI',
       which categoryOf() classifies as unknown, while the two linked windows
       carry 'PEST'. An unclassified record keeps the neutral token and prints no
       category name — never a guess. */
    const csUI = (csWinRec && csWinRec.ui) || (csRec && csRec.ui) || (csUIK.CATEGORY ? csUIK.CATEGORY.unknown : { color: '#8F8886', dark: '#3A3533', soft: '#B1A9A7', label: null, iconAsset: '' });
    /* `key` is deliberately not copied onto the rendered object: it is an
       internal token ('pest' / 'unknown') and a prop-walking language guard
       would read it as visible English. */
    const csCatKey = csUI.key || 'unknown';
    const csCat = { label: csUI.label, color: csUI.color, dark: csUI.dark, soft: csUI.soft, ink: csUI.ink, body: csUI.body, muted: csUI.muted, icon: csUI.iconAsset || '' };

    /* §7 · Days remaining, bar width and ordering may be computed from supplied
       dates; the agronomic state may not. WINDOW_CLOSED here is upstream's own
       CURRENT_STATUS, and the colour tokens are the model's presentation set. */
    const CS_ST = csUIK.STATUS || { DEFAULT: { color: '#978B87', text: '#B1A9A7' } };
    const csStatus = csWinRec ? csWinRec.status : null;
    const csStTok = CS_ST[csStatus] || CS_ST.DATE_UNKNOWN || CS_ST.DEFAULT;
    const csD0 = csWinRec ? csWinRec.daysToStart : null, csD1 = csWinRec ? csWinRec.daysToEnd : null;
    const csSpan = (csD0 !== null && csD1 !== null && csD1 > csD0) ? (csD1 - csD0) : null;
    const csPct = csSpan === null ? 0 : Math.max(0, Math.min(100, Math.round(((0 - csD0) / csSpan) * 100)));

    /* §10 · Two real sources, in this order. ADAMA_PRODUCTS is what the record
       declares (measured 6 / 0 / 0 — only IT-OPP-001 fills it). The label audit
       is the second and it outranks the first: for Maize x European Corn Borer it
       returns COSAYR 200 SC as a VERIFIED_LABEL_MATCH although IT-OPP-002's array
       is empty, so trusting the array alone would print "no confirmed match" over
       an audited match. IT-OPP-002's CURRENT_EVIDENCE claims six products in
       prose; that prose is deliberately NOT parsed to refill the array. */
    const csLinked = (AM && csCropK && csIssueK)
      ? AM.products.filter(p => (p.links || []).some(l => l.crop === csCropK && l.issue === csIssueK)).map(p => p.name)
      : [];
    const csNames = ((csRec && csRec.adamaProducts) || []).slice();
    csLinked.forEach(n => { if (csNames.indexOf(n) < 0) csNames.push(n); });
    const csProds = csNames.map((n) => {
      const p = AM ? AM.findProduct(n) : null;
      const v = (AM && csCropK && csIssueK) ? AM.strengthFor(n, csCropK, csIssueK) : null;
      const moa = p && p.regulatory ? [].concat(p.regulatory.irac || [], p.regulatory.frac || [], p.regulatory.hrac || []).filter(Boolean) : [];
      return {
        name: n, verdict: v,
        ai: p && p.ai && p.ai.length ? p.ai.join(' · ') : (T.ksNotKnown || ''),
        use: v ? ((T.PSTATE && T.PSTATE[v]) || String(v).replace(/_/g, ' ')) : ((T.PSTATE && T.PSTATE.LABEL_CHECK_NEEDED) || ''),
        moa: moa.length ? 'IRAC/FRAC/HRAC ' + moa.join(', ') : (T.ksNotKnown || ''),
        go: () => this.openProduct(n)
      };
    });
    /* A 'primary' has no upstream field at all. It is claimed only where the
       label audit verifies one, and the record's own declaration order breaks
       the tie — never a score invented here. */
    const csPrimary = csProds.find(p => p.verdict === 'VERIFIED_LABEL_MATCH') || null;
    const csAlts = csProds.filter(p => p !== csPrimary);

    /* SOURCE_IDS is the one link the record declares explicitly. Measured 3/3 and
       identical on all three records, so it locates the case but does not
       distinguish it — the resolved titles are shown, no count is implied. */
    const csSrcRows = ((csRec && csRec.sourceIds) || [])
      .map(id => (APP0 ? APP0.sources.records.find(x => x.id === id || x.sourceId === id) : null))
      .filter(Boolean)
      .map(x => ({ id: x.id, name: x.name, type: srcL(x.type) || x.type, groupColor: (csUIK.SOURCE_TYPE_COLOR || {})[csFold(x.type)] || '#978B87', go: () => this.openSource(x.id) }));

    /* SCIENCE_CONTEXT carries different keys per record, so the model exposes it
       as a label/value list. Only the NUMERIC members are shown: IT-OPP-002's
       BRIDGE_TESTED is a Portuguese sentence that explicitly says the bridge was
       NOT proven, and printing it beside two counts would read as a finding. */
    const csSci = ((csRec && csRec.scienceContextCounts) || []).filter(x => typeof x.value === 'number');
    const csSciTxt = csSci.length
      ? csT('sciWorks') + ': ' + csSci.map(x => String(x.label).replace(/_WORKS$/, '').replace(/_/g, ' ') + ' ' + x.value).join(', ')
      : (csRec && csRec.scienceContextState ? csT('sciState') + ': ' + csEnum(csRec.scienceContextState) : null);

    const csKnowN = ((csRec && csRec.whatWeKnowList) || []).length;
    const csWatchN = ((csRec && csRec.whatWeDoNotKnowList) || []).length;
    const csEvN = ((csRec && csRec.currentEvidenceList) || []).length;
    const csFresh = csRec && csRec.freshnessDays !== undefined && csRec.freshnessDays !== null ? csRec.freshnessDays : null;
    const csDoc = csSafe(csRec && csRec.happeningDocument);
    const csObsDate = csRec ? csDay(csRec.observationDate) : null;
    /* regionKeys is the model's own parse of the compound REGION string against
       the 20 canonical names; the qualifiers stay in regionLabel and are never
       promoted to a fact. Measured: 2, 1 and 0 regions on the three records. */
    const csNamed = (csRec && csRec.regionKeys) ? csRec.regionKeys : (csRec ? (csUIK.REGION_GRID || []).filter(r => csFold(csRegion).indexOf(csFold(r.name)) >= 0).map(r => r.name) : []);

    /* cs0 is the routing identity the later blocks read (windows, market, brief).
       It carries the CANONICAL crop key so those lookups resolve, and the whole
       upstream record travels under `raw`, which the language guard skips, so no
       Portuguese fact string can leak into a rendered prop by assignment. */
    const cs0 = {
      id: csRec ? csRec.id : (s.caseId || null),
      found: !!csRec, isScenario: !!csScen,
      crop: csCropK || null, issue: csIssueK || null, region: csRegion,
      canonicalWindow: csWinRec, windowId: csWinRec ? csWinRec.windowId : null,
      status: csStatus, st: csStTok, category: csCat,
      /* Still declared because later blocks read them; there is no upstream
         department, action or timeline field anywhere to fill them with. */
      actions: [], departments: [], tl: [],
      raw: csRec
    };

    const cs = {
      id: cs0.id, hasCase: !!csRec, missingId: csRec ? '' : (s.caseId || ''), isScenario: !!csScen,
      /* the breadcrumb, assembled downstream, reads these three */
      issue: csRec ? (csIssueTxt || csT('awaiting')) : csT('notFound'), crop: csCropTxt, region: csRegion,
      category: csCat, catLabel: csCat.label ? String(L(csCat.label)).toUpperCase() : '',
      st: csStTok, badgeVariant: csCatKey === 'pest' ? 'pest-control' : 'disease-control',
      issueL: csRec ? (csIssueTxt || csT('awaiting')) : csT('notFound'),
      latin: csIdent || '', cropL: csCropTxt, regionLabel: csRegion,
      /* FRESHNESS_DAYS is upstream's own number and it is the age of the SOURCE
         DOCUMENT (measured 17 / 18 / 6), not of an internal edit. The demo's
         `updated` integer, which claimed the second thing, is gone. */
      updatedLabel: csFresh === null ? (T.ksNotKnown || '') : (csFresh + csT('ago')),
      statusLabel: csStatus ? wst(csStatus) : (csRec && csRec.windowApplication ? csEnum(csRec.windowApplication) : ((T.WSTATUS && T.WSTATUS.DATE_UNKNOWN) || '')),
      wsLabel: (csWinRec && csDate(csWinRec.startDate)) || '—',
      weLabel: (csWinRec && csDate(csWinRec.endDate)) || '—',
      /* The record's OWN declared window states are real 3/3 and survive even
         where no canonical window is linked, so the tile is never blank. */
      windowLine: (csRec && csRec.windowApplication)
        ? (csT('appW') + ': ' + csEnum(csRec.windowApplication) + ' · ' + csT('monW') + ': ' + csEnum(csRec.windowMonitoring))
        : csT('noWindow'),
      progressPct: csPct + '%',
      /* CROP_STAGE and ISSUE_STAGE are null on all 29 canonical windows, so both
         classes read NOT_OBSERVED. OBSERVED_STAGE is real on 1 of 3 records. */
      stageL: csWinRec ? obs(csWinRec.cropStageClass) : (T.ksNotKnown || ''),
      signalL: csSafe(csRec && csRec.observedStage) || (csWinRec ? obs(csWinRec.issueStageClass) : (T.ksNotKnown || '')),
      /* LABEL_TRIGGER and LABEL_SOURCE are null on all 29 canonical windows. A
         spray timing that no label record supports is the most consequential
         thing this screen could fabricate, so it states the check instead. */
      label: (T.PSTATE && T.PSTATE.LABEL_CHECK_NEEDED) || 'LABEL CHECK NEEDED',
      bigNumber: (csStatus === 'WINDOW_OPEN' && csD1 !== null) ? csD1 : (csD0 !== null && csD0 > 0 ? csD0 : '—'),
      bigLabel: (csStatus === 'WINDOW_OPEN' && csD1 !== null) ? T.lblPriorityDays : (csD0 !== null && csD0 > 0 ? csT('toOpen') : (csWinRec ? csT('closedCycle') : csT('noWindow'))),

      /* §2 · The five-bar convergence chart and the words Strong / Good /
         Building were hand-typed onto each demo case and then nudged by a
         literal stamped 'REAL_FACT'. Nothing comparable exists upstream, so the
         bars are gone and the tile states what it actually has: CURRENT_EVIDENCE
         entries counted, with no strength score of any kind. */
      evidenceLabel: csT('evState'), evidenceTotal: csEvN, evChips: [], evBars: [],
      source: [csT('declaredSources') + ': ' + csSrcRows.length, csSciTxt, csT('noConvergence')].filter(Boolean).join(' · '),

      /* WHAT_IS_HAPPENING.CONTENT is untranslated analyst prose on 3/3 records
         and stays hidden; the state and the document identity are facts. */
      happening: (csRec && csRec.happeningState) ? (csEnum(csRec.happeningState) + ' · ' + csT('sourceUnloc')) : '',
      hasHappening: !!(csRec && csRec.happeningState),
      hasRealObs: !!(csDoc || csObsDate),
      realObsText: csDoc || '',
      realObsSource: [csObsDate, csFresh === null ? null : (csFresh + csT('ago'))].filter(Boolean).join(' · '),
      /* WHY_IT_MATTERS.NOTE and the Lombardia / Veneto regional decree strings
         are the most actionable content in the package and none of them has an
         approved localization, so none is rendered. MANDATORY is a boolean and
         it survives intact. */
      why: (csRec && csRec.whyMandatory !== null && csRec.whyMandatory !== undefined) ? (csRec.whyMandatory ? csT('mandatory') : csT('notMandatory')) : '',
      hasWhy: !!(csRec && csRec.whyMandatory !== null && csRec.whyMandatory !== undefined),

      matchCount: csProds.length,
      hasPrimary: !!csPrimary, noPrimary: !csPrimary,
      primaryLabel: csPrimary ? csPrimary.name : ((T.PSTATE && T.PSTATE.LABEL_CHECK_NEEDED) || ''),
      primaryAi: csPrimary ? csPrimary.ai : '',
      primaryTargets: csPrimary && csIssueK ? il(csIssueK) : (T.ksNotKnown || ''),
      /* No upstream application field exists for a product inside a case. */
      primaryUse: T.ksNotKnown || '',
      primaryMoa: csPrimary ? csPrimary.moa : (T.ksNotKnown || ''),
      primaryGo: () => csPrimary && this.openProduct(csPrimary.name),
      alternatives: csAlts.map(p => ({ name: p.name, ai: p.ai, use: p.use, moa: p.moa, go: p.go })),
      noAlternatives: csAlts.length === 0 && !!csPrimary,
      /* §10 · Absence in a reading is not absence in the world. */
      absenceRule: T.absenceRule || (AM ? AM.ABSENCE_RULE : ''),

      /* WHAT_WE_KNOW (4/4/3) and WHAT_WE_DO_NOT_KNOW (5/3/3) exist and every
         entry is Portuguese, so the entries cannot be shown. The count is a fact
         and the missing localization is stated rather than quietly dropped. */
      know: csKnowN ? [csKnowN + ' ' + csT('recorded') + ' · ' + csT('awaitingLong')] : [],
      watch: csWatchN ? [csWatchN + ' ' + csT('recorded') + ' · ' + csT('awaitingLong')] : [],
      knowCount: csKnowN, watchCount: csWatchN,

      /* §1 · The department action map, its six GENERATE BRIEF buttons and the
         executive timeline were internal workflow: a static ACTIONS table with
         {crop}/{product} substitution, and four dates built by arithmetic on two
         invented integers. No upstream field exists for any of them. */
      deptChips: [], actions: [], tl: [], origin: '',
      /* Company names, item counts, recency and activity type came out of a
         seeded pseudo-random generator. Deleted: the 503 real competitor
         activities cannot refill this without a crop synonym table that resolves
         'Vitis vinifera' and the generic 'colture', which does not exist yet. */
      competitors: [],
      /* A demonstration inbox must not appear on a real record (§5). */
      fieldMessages: [], fieldCount: 0, noField: false,

      /* §4 · Grid geometry from the model's own coordinate table — no count, no
         colour and no active flag. The highlight is the record's declared
         regionKeys, so the map claims exactly what the record claims. */
      miniMap: (csUIK.REGION_GRID || []).map(r => ({
        name: r.name, gc: r.gc, gr: r.gr,
        fill: csNamed.indexOf(r.name) >= 0 ? csCat.color : 'rgba(255,255,255,0.05)',
        stroke: csNamed.indexOf(r.name) >= 0 ? csCat.color : 'rgba(255,255,255,0.08)',
        go: () => this.radarWith({ fRegion: r.name })
      })),
      /* The hand-authored 'adjacent regions' list was a region claim and a
         recommendation at once. The record names its own areas, in regionLabel. */
      adjacentLabel: '',

      sourceRows: csSrcRows,
      /* No theme in the real science collection declares a case. */
      relatedThemes: [],
      goArchive: () => this.archiveWith({ aCase: cs0.id }),
      goCompetitors: () => this.compWith(csCropK ? { fCrop: csCropK, fIssue: csIssueK || '' } : {}),
      goWindow: () => csWinRec && this.openWindow(csWinRec.windowId)
    };
