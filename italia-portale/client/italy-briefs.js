/* Sintonia · department Action Brief generator.
   ---------------------------------------------------------------------------
   FACT SOURCE = window.ITALY_APP_MODEL. The legacy case object is accepted only
   as a ROUTING KEY (which canonical window, which product names, which colour).
   No agronomic state, date, stage, label trigger, source, evidence count or
   field observation is ever taken from the demo fixture (PRODUCT LAW §2/§3).

   ONE clock: window.ITALY_APP_MODEL.referenceDate / .REF (PRODUCT LAW §6).
   This file constructs no Date object at all — dates are formatted from the
   model's ISO strings, and every day count is the model's own.

   PORTFOLIO GRADE (PRODUCT LAW §10/§13). A product is never printed under a
   heading that asserts relevance to this crop × issue unless the model's own
   label audit graded that exact pair VERIFIED_LABEL_MATCH. Everything else is
   printed too — never dropped, never called absent — under a separate
   "da verificare" heading carrying its measured state and AM.ABSENCE_RULE.
   The single source of that grade is AM.strengthFor(name, crop, issue).

   LANGUAGE (PRODUCT LAW §11). The brief renders in the interface language.
   Product names, company names, active substances, Latin binomials, label
   target wording and official source titles stay exactly as published.
   --------------------------------------------------------------------------- */
(function () {
  const S = (h, lines, bullets) => ({ h, lines: (lines || []).filter(Boolean), bullets: !!bullets });

  /* ── model access ───────────────────────────────────────────────────────── */
  const M = () => (typeof window !== 'undefined' && window.ITALY_APP_MODEL) || null;

  /* ── interface language ─────────────────────────────────────────────────────
     The portal keeps <html lang> in step with state.lang on EVERY render
     (portale.html §27), and the render that builds this brief runs after that
     sync — so the attribute is a live read of the interface language, not a
     stale one. localStorage is the fallback for a call made outside a render.
     A caller may still pass the language explicitly; that always wins.
     REQUESTED OF THE PORTAL: pass this.state.lang as build()'s 3rd argument, so
     the brief stops inferring what the caller already knows. */
  let LG = 'it';
  const detectLang = () => {
    try {
      const d = typeof document !== 'undefined' && document.documentElement && document.documentElement.lang;
      if (d === 'en' || d === 'it') return d;
    } catch (e) { /* no document */ }
    try {
      if (typeof localStorage !== 'undefined' && localStorage.getItem('sintonia_lang') === 'en') return 'en';
    } catch (e) { /* storage blocked */ }
    return 'it';
  };
  const TX = (it, en) => (LG === 'en' ? en : it);
  /* The shared interface dictionary, used ONLY for vocabulary tables the rest of
     the portal already keys on (crop names, issue names, portfolio-state
     labels) so two screens cannot name the same thing differently. */
  const DICT = (k) => {
    const I = (typeof window !== 'undefined' && window.SINTONIA_I18N) || null;
    const L = I && (I[LG] || I.it);
    return (L && L[k]) || {};
  };

  /* ── dates ──────────────────────────────────────────────────────────────────
     Same month abbreviations the model's own fmtDate() defaults to, so a date
     printed here reads like a date printed anywhere else in the pilot. */
  const MON = {
    it: ['Gen', 'Feb', 'Mar', 'Apr', 'Mag', 'Giu', 'Lug', 'Ago', 'Set', 'Ott', 'Nov', 'Dic'],
    en: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  };
  /* ISO string in, human string out. Deliberately string-only: constructing a
     Date here would be a second truth clock. */
  const fmtISO = (iso) => {
    if (!iso) return null;
    const p = String(iso).split('-');
    const T = MON[LG] || MON.it;
    return (p.length === 3 && T[+p[1] - 1]) ? `${p[2]} ${T[+p[1] - 1]} ${p[0]}` : String(iso);
  };
  const refISO = () => { const m = M(); return (m && m.referenceDate) || null; };
  const refStamp = () => fmtISO(refISO()) || TX('DATA DI RIFERIMENTO NON DISPONIBILE', 'REFERENCE DATE NOT AVAILABLE');

  /* The canonical window record for a case. 29/29 legacy cases resolve by
     legacyCaseId; windowId is kept as a second key. */
  /* I prodotti verificati di un caso senza finestra vivono nei suoi
     `productLinks`, con il verdetto per singolo legame. Leggerli dalla sola
     finestra lasciava vuota la riga su 37 casi su 37. */
  const caseLinks = (c) => {
    /* `c` e la proiezione di instradamento, `c.raw` il record del motore.
       Si legge PRIMA la proiezione — le sue chiavi sono gia canoniche e in
       lingua — e si ricade sul record solo per i campi che la proiezione non
       porta. Il contrario avrebbe fatto entrare il portoghese di lavoro
       dell'analista ("Videira") in un documento italiano. */
    const RAW = (c && c.raw) || {};
    const R = Object.assign({}, RAW, c || {});
    return Array.isArray(R.productLinks) ? R.productLinks : [];
  };
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
  const UNK = () => TX('NON NOTO — non stabilito nel modello Sintonia', 'NON NOTO — not established in the Sintonia model');
  /* Canonical stage codes, in the interface language, with the code kept in
     brackets. The code is what makes the line traceable; printing it bare
     inside an Italian sentence made the document read as unfinished. */
  const STAGE_L = {
    NOT_OBSERVED: ['non osservata (NOT_OBSERVED)', 'not observed (NOT_OBSERVED)'],
    OBSERVED: ['osservata (OBSERVED)', 'observed (OBSERVED)'],
    EXPECTED: ['attesa (EXPECTED)', 'expected (EXPECTED)'],
    REPORTED: ['segnalata (REPORTED)', 'reported (REPORTED)'],
  };
  const STATUS_L = {
    ACT_NOW: ['AGIRE ORA', 'ACT NOW'],
    PREPARE_NOW: ['PREPARARE ORA', 'PREPARE NOW'],
    FUTURE_PREPARATION: ['PREPARAZIONE FUTURA', 'FUTURE PREPARATION'],
    TO_VALIDATE: ['DA VALIDARE', 'TO VALIDATE'],
    WINDOW_OPEN: ['FINESTRA APERTA', 'WINDOW OPEN'],
    WINDOW_CLOSED: ['FINESTRA CHIUSA', 'WINDOW CLOSED'],
    NEXT_CYCLE: ['CICLO SUCCESSIVO', 'NEXT CYCLE'],
    NOT_ESTABLISHED: ['STATO NON STABILITO', 'STATUS NOT ESTABLISHED']
  };
  const statusName = (code) => { const e = STATUS_L[String(code || '').toUpperCase()]; return e ? TX(e[0], e[1]) : String(code || '').replace(/_/g, ' '); };
  const stageL = (code) => { const e = STAGE_L[String(code || '').toUpperCase()]; return e ? TX(e[0], e[1]) : String(code || ''); };
  const NOTCONF = () => TX('NON CONFERMATO — nessuna fonte esterna lo conferma in questa lettura', 'NON CONFERMATO — not confirmed by an external source in this reading');
  const NOT_OBS = 'NON OSSERVABILE DA FONTI ESTERNE';
  const INTERP = () => TX(' — INTERPRETAZIONE SINTONIA', ' — SINTONIA INTERPRETATION');
  /* Model prose that the model publishes in ONE language only. Translating it
     here is drift-unsafe if the upstream wording ever changes, so the Italian
     rendering is keyed on the EXACT English the model publishes today: any
     other value is printed verbatim rather than mistranslated.
     REQUESTED UPSTREAM: publish ABSENCE_RULE and link.evidence bilingually. */
  const IT_OF = {
    'Absence in this reading is not absence in the world.': 'L\'assenza in questa lettura non è assenza nel mondo.',
    'Read on the official label': 'Letto sull\'etichetta ufficiale',
    'Not found in this label reading': 'Non trovato in questa lettura dell\'etichetta',
    'The audit verified the main visible claims, not every portfolio connection in the interface. Anything not explicitly verified remains pending label verification.':
      'L\'audit ha verificato le principali affermazioni visibili, non ogni connessione di portafoglio presente nell\'interfaccia. Tutto ciò che non è stato verificato esplicitamente resta in attesa di verifica dell\'etichetta.',
    /* The 5 distinct STATUS_REASON shapes measured on the 29 canonical windows.
       The first is parametrised by the reference date and is handled by the
       regex below; a shape not listed here prints verbatim. */
    'Reference date falls inside the expected window · NOT an observation': 'La data di riferimento cade dentro la finestra attesa · NON è un\'osservazione',
    'Reference date falls before START_DATE': 'La data di riferimento è precedente a START_DATE',
    'No biological calendar entry for this issue': 'Nessuna voce di calendario biologico per questo problema',
    'The 2026 flowering window has passed; next relevant window is the 2027 campaign':
      'La finestra di fioritura 2026 è passata; la prossima finestra rilevante è la campagna 2027'
  };
  const REF_AFTER = /^Reference date (\d{4}-\d{2}-\d{2}) falls after END_DATE$/;
  const modelProse = (s) => {
    if (LG !== 'it' || !s) return s;
    if (IT_OF[s]) return IT_OF[s];
    const r = REF_AFTER.exec(String(s));
    return r ? `La data di riferimento ${r[1]} è successiva a END_DATE` : s;
  };
  const ABSENCE = () => { const m = M(); return modelProse((m && m.ABSENCE_RULE) || 'Absence in this reading is not absence in the world.'); };

  const listOf = (arr, cap) => {
    const a = (arr || []).filter(Boolean);
    if (!a.length) return null;
    const n = cap || 8;
    return a.length > n
      ? `${a.slice(0, n).join(', ')} ${TX(`(+${a.length - n} altre sulla scheda di etichetta)`, `(+${a.length - n} more on the label record)`)}`
      : a.join(', ');
  };

  /* ── crop vocabulary (PRODUCT LAW §4/§11, finding 4 and 5) ──────────────────
     Two different jobs, both of which used to print a raw token:
       cropName()  a CANONICAL crop name ('Grapevine') -> the label the rest of
                   the portal shows ('Vite'), from the shared CROPS table.
       cropCode()  a LABEL ENUM ('WHEAT_GENERIC') -> that same display label,
                   through the model's own declared CROP_BY_CODE join.
     WHEAT_GENERIC legitimately resolves to two crops; the model declares that
     overlap and so does this line, rather than picking one. A code the model
     does not join is printed unchanged — silently renaming it would invent a
     fact. SUNFLOWER and ALFALFA are the only two of the 17 codes measured on
     the products that CROP_BY_CODE does not carry; their canonical partner is
     stated here and requested upstream (see report). */
  const CODE_LOCAL = { SUNFLOWER: 'Sunflower', ALFALFA: 'Alfalfa' };
  const cropName = (canon) => (canon ? (DICT('CROPS')[canon] || canon) : canon);
  const issueName = (issue) => (issue ? (DICT('ISSUES')[issue] || issue) : issue);
  const cropCode = (code) => {
    const m = M();
    const J = (m && m.lookups && m.lookups.CROP_BY_CODE) || {};
    const hit = J[code] || (CODE_LOCAL[code] ? [CODE_LOCAL[code]] : null);
    return hit ? hit.map(cropName).join(' / ') : String(code);
  };
  const cropCodes = (arr, cap) => listOf((arr || []).map(cropCode), cap);
  /* The four portfolio grades, in the wording the rest of the portal uses. */
  const pstate = (k) => (DICT('PSTATE')[k] || k);

  /* ── fact readers ───────────────────────────────────────────────────────── */
  const F = (c) => {
    const W = win(c);
    const m = M();
    /* ── IL CASO PARLA DI SE, ANCHE SENZA UNA FINESTRA CANONICA ───────────────
       Ogni riga qui sotto leggeva SOLO la finestra canonica, e la finestra si
       cerca per `legacyCaseId`. Quel campo e null su TUTTI E 37 i casi del
       motore V2.1: `W` era null 37/37, e il documento commerciale usciva con
       coltura, problema, regione, stato e date tutti «NON NOTO» — un foglio di
       assenze con un titolo che dichiarava di non sapere niente.

           IL DOCUMENTO DICEVA «NON NOTO» DI COSE CHE IL RECORD SCRIVE.

       Il record porta crop, issue, region, status e — su sette casi — le
       proprie date. Si legge il record quando la finestra non c'e. Non e un
       ripiego inventato: e lo stesso campo che la scheda e il dettaglio
       mostrano, cosi le tre superfici non possono divergere. */
    const R = (c && c.raw) || c || {};
    const rCrop = (R.cropKeys && R.cropKeys[0]) || R.crop || null;
    /* `issueKey` E UNA CHIAVE DI GIUNZIONE, NON UN'ETICHETTA: vale il nome
       inglese con cui si interroga l'audit delle etichette, e leggerlo per
       primo scriveva «Brown marmorated stink bug» dentro un documento
       italiano che ha «Cimice asiatica» nel proprio record.

           UNA CHIAVE SI USA PER CERCARE. UN'ETICHETTA SI LEGGE. */
    const rIssueTxt = (LG === 'en' ? (R.issueEn || R.issue) : (R.issue || R.issueEn)) || null;
    const rIssue = R.issueKey || R.issue || null;
    const f = {
      W,
      cropKey: (W && W.crop) || rCrop || null,
      issueKey: (W && W.issue) || rIssue || null,
      crop: (W && cropName(W.crop)) || (rCrop && cropName(rCrop)) || UNK(),
      /* «NON NOTO» ERA LA RISPOSTA SBAGLIATA A UNA DOMANDA GIUSTA.
         Il record dichiara `geoScope`: NATIONAL, EUROPEAN, PROVINCIAL. Una
         regione nulla su un caso NAZIONALE non e un dato mancante — e la
         portata del caso, ed e scritta. Dirlo «non noto» faceva sembrare rotto
         un caso che si sa benissimo dove sta. */
      region: (W && W.region) || R.region
        || (R.geoScope === 'NATIONAL' ? TX('Italia · portata nazionale', 'Italy · national scope')
          : R.geoScope === 'EUROPEAN' ? TX('Unione Europea · portata europea', 'European Union · European scope')
            : null)
        || UNK(),
      issue: (W && issueName(W.issue)) || rIssueTxt || (rIssue && issueName(rIssue)) || UNK(),
      issueType: (W && W.issueType) || R.issueType || UNK(),
      /* ⚠️ IL FOGLIO DEL RIVENDITORE STAMPAVA IL CODICE DEL MOTORE.
         «Stato attuale ACT_NOW.» — su un PDF che va in mano a un cliente. Il
         codice e giusto (viene dal motore) e la parola no: il portone
         `pdf-gate` PT2 esiste per questo, e non poteva vederlo perche
         `pdfjs-dist` non era installato.

             UN PDF E UNA SUPERFICIE COME LE ALTRE.
             CIO CHE NON PUO STARE SULLO SCHERMO NON PUO STARE NEMMENO LI.

         Il dizionario canonico ha gia la frase nelle due lingue; V21 resta la
         riserva per gli stati che il motore non pubblica. */
      status: (() => {
        const code = (W && W.status) || R.status || null;
        if (!code) return TX('NON STABILITO', 'NOT ESTABLISHED');
        const ml = (typeof window !== 'undefined' && window.MEETING_LABELS)
          ? window.MEETING_LABELS.t('STATUS', code, LG === 'en' ? 'en' : 'it') : '';
        if (ml) return ml;
        return DICT('V21')[code] || TX('NON STABILITO', 'NOT ESTABLISHED');
      })(),
      statusReason: (W && modelProse(W.statusReason)) || null,
      from: (W && fmtISO(W.startDate)) || (R.windowStart && fmtISO(R.windowStart)) || TX('DATA NON STABILITA', 'DATE NOT ESTABLISHED'),
      to: (W && fmtISO(W.endDate)) || (R.windowEnd && fmtISO(R.windowEnd)) || TX('DATA NON STABILITA', 'DATE NOT ESTABLISHED'),
      dateState: (W && W.dateState) || UNK(),
      dateConfidence: (W && W.dateConfidence) || UNK(),
      lastValidated: (W && fmtISO(W.lastValidated)) || UNK(),
      windowType: (W && W.windowType) || UNK(),
      /* CROP_STAGE / ISSUE_STAGE are null on 29/29 canonical windows: the class
         is the only observed value, and NOT_OBSERVED is a real answer. It is
         shown in the interface language with the canonical code beside it —
         printing the bare enum inside an Italian sentence read as unfinished,
         and the code still has to travel so the reader can trace it. */
      /* Measured: CROP_STAGE and ISSUE_STAGE are null on 29/29 canonical
         windows and the CLASS carries the literal string NOT_OBSERVED on all
         29. So the code arrives from the DATA, not from a fallback — a label
         that only localized the fallback never fired. stageL() maps the code
         wherever it comes from, and keeps it in brackets so the reader can
         still trace it. */
      cropStage: (W && (W.cropStage || W.cropStageClass)) || 'NOT_OBSERVED',
      cropStageLabel: stageL((W && (W.cropStage || W.cropStageClass)) || 'NOT_OBSERVED'),
      issueStage: (W && (W.issueStage || W.issueStageClass)) || 'NOT_OBSERVED',
      issueStageLabel: stageL((W && (W.issueStage || W.issueStageClass)) || 'NOT_OBSERVED'),
      labelTrigger: (W && W.labelTrigger) || null,
      labelSource: (W && W.labelSource) || null,
      color: (W && W.ui && W.ui.color) || (c && c.category && c.category.color) || '#009845'
    };
    f.lowIssue = String(f.issueKey ? f.issue : TX('questo problema', 'this issue')).toLowerCase();
    f.lowCrop = String(f.cropKey ? f.crop : TX('questa coltura', 'this crop')).toLowerCase();
    f.windowState = (() => {
      /* Il caso porta il proprio stato di finestra quando la canonica manca:
         sette casi su 37 dichiarano date e giorni residui. */
      if (!W) {
        if (R.daysRemaining !== null && R.daysRemaining !== undefined) return TX(`${R.daysRemaining} giorni rimanenti`, `${R.daysRemaining} days remaining`);
        if (R.windowState) return String(R.windowState);
        return TX('finestra non stabilita', 'WINDOW NOT ESTABLISHED');
      }
      if (W.status === 'WINDOW_CLOSED') return TX(`finestra chiusa · ${Math.abs(W.daysToEnd)} giorni oltre END_DATE`, `window closed · ${Math.abs(W.daysToEnd)} days past END_DATE`);
      if (typeof W.daysToStart === 'number' && W.daysToStart > 0) return TX(`${W.daysToStart} giorni all'apertura`, `${W.daysToStart} days to open`);
      if (typeof W.daysToEnd === 'number') return TX(`${W.daysToEnd} giorni rimanenti`, `${W.daysToEnd} days remaining`);
      return String(W.status || TX('finestra non stabilita', 'WINDOW NOT ESTABLISHED'));
    })();
    f.windowOpen = !!(W && W.status !== 'WINDOW_CLOSED' && typeof W.daysToStart === 'number' && W.daysToStart <= 0);
    /* Product names route into the model; the fixture's ai / crops / targets /
       use / moa are never read. */
    /* I nomi arrivano anche dal record del motore: `adamaProducts` e popolato
       37/37, mentre `c.products` esiste solo sulla forma decorata. */
    const names = (c && (c.products || (c.productObjs || []).map(p => p && p.name)))
      || R.adamaProducts || [];
    f.products = names.filter(Boolean).map(n => ({ name: n, P: prod(n) }));

    /* ── the grade, asked once, for THIS crop × issue ────────────────────────
       AM.strengthFor() is the model's own label-audit answer. With no canonical
       window there is no crop × issue to ask about, so nothing may be graded
       relevant — that is an absence of a question, not a negative answer. */
    const pair = !!(f.cropKey && f.issueKey);
    f.gradePair = pair;
    f.graded = f.products.map((x) => {
      const strength = (pair && m && m.strengthFor) ? m.strengthFor(x.name, f.cropKey, f.issueKey) : null;
      const link = pair && x.P && Array.isArray(x.P.links)
        ? x.P.links.find(l => String(l.crop || '').toUpperCase() === String(f.cropKey).toUpperCase()
          && String(l.issue || '').toUpperCase() === String(f.issueKey).toUpperCase()) || null
        : null;
      return { name: x.name, P: x.P, strength, link };
    });
    /* IL VERDETTO CHE IL MOTORE HA GIA DATO NON SI RICALCOLA.
       `strengthFor` risponde per la coppia coltura × problema; il record porta
       invece il verdetto PER SINGOLO LEGAME, che e piu preciso e che la scheda
       e il dettaglio gia mostrano. Dove esiste, vince — altrimenti le tre
       superfici direbbero cose diverse dello stesso prodotto.

           78 legami VERIFIED e 172 LABEL_CHECK_NEEDED, misurati sui 37 casi. */
    const RL = caseLinks(c);
    if (RL.length) {
      const byName = {}; RL.forEach((l) => { byName[l.name || l.product] = l.strength; });
      f.graded = f.graded.map((g) => (byName[g.name] ? Object.assign({}, g, { strength: byName[g.name] }) : g));
    }
    f.verified = f.graded.filter(g => g.strength === 'VERIFIED_LABEL_MATCH');
    f.unverified = f.graded.filter(g => g.strength !== 'VERIFIED_LABEL_MATCH');
    f.verifiedNames = f.verified.map(g => g.name);
    /* PRODUCT LAW §10 · the model ranks no product above another, so no
       "primary" is asserted. The routing key's own `primary` is read only as a
       fallback for the legacy scenario shape, and only if the grade agrees. */
    f.primaryName = f.verifiedNames[0]
      || ((c && c.primary && f.verifiedNames.indexOf(c.primary) >= 0) ? c.primary : null);
    f.primary = f.primaryName ? prod(f.primaryName) : null;
    f.moreMatches = Math.max(0, f.verified.length - 1);
    f.model = !!m;
    return f;
  };

  const window_ = (f) => [
    TX(`${f.from} → ${f.to} · ${f.windowState} · tipo di finestra ${f.windowType}`,
      `${f.from} → ${f.to} · ${f.windowState} · window type ${f.windowType}`),
    TX(`Stato della data ${f.dateState} · confidenza ${f.dateConfidence} · ultima validazione ${f.lastValidated}`,
      `Date state ${f.dateState} · confidence ${f.dateConfidence} · last validated ${f.lastValidated}`),
    TX(`Fase colturale: ${f.cropStageLabel} · fase del problema: ${f.issueStageLabel}`, `Crop stage: ${f.cropStageLabel} · issue stage: ${f.issueStageLabel}`)
      + (f.cropStage === 'NOT_OBSERVED' ? TX(' (per questa finestra non è registrata alcuna fase osservata — non affermarne una)', ' (no observed stage is recorded for this window — do not assert one)') : ''),
    f.labelTrigger
      ? TX(`Trigger di etichetta: ${f.labelTrigger}${f.labelSource ? ` · fonte ${f.labelSource}` : ''}`, `Label trigger: ${f.labelTrigger}${f.labelSource ? ` · source ${f.labelSource}` : ''}`)
      : TX('Trigger di etichetta: NON NOTO — su questa finestra non è registrato alcun innesco di etichetta. Il momento di applicazione si legge sulla scheda di etichetta del prodotto, mai da questo brief.',
        'Label trigger: NON NOTO — no label trigger is recorded on this window. Read the application timing from the product label record, never from this brief.')
  ];

  /* One product, registry facts only. Crop enums print through cropCode(); the
     active substance, the label target wording and the label URL stay exactly
     as the source publishes them (PRODUCT LAW §11). */
  const prodLine = (x) => {
    const P = x.P;
    if (!P) return TX(`${x.name} — non presente nel modello prodotti Sintonia · verificare sulla banca dati nazionale prima di qualsiasi impiego`,
      `${x.name} — not present in the Sintonia product model · confirm against the national label record before any use`);
    const ai = (Array.isArray(P.ai) ? P.ai : [P.ai]).filter(Boolean);
    const R = P.regulatory || {};
    /* irac / frac / hrac are arrays in the model and an empty array is truthy,
       so they are normalized before they can print an empty "IRAC ·" group. */
    const code = (v, tag) => { const a = (Array.isArray(v) ? v : [v]).filter(y => y !== null && y !== undefined && String(y).trim() !== ''); return a.length ? `${tag} ${a.join(' + ')}` : null; };
    const moa = [code(R.irac, 'IRAC'), code(R.frac, 'FRAC'), code(R.hrac, 'HRAC')].filter(Boolean).join(' · ');
    return [
      TX(`${P.name} — sostanza attiva: ${ai.length ? ai.join(' + ') : UNK()}`, `${P.name} — active substance: ${ai.length ? ai.join(' + ') : UNK()}`),
      TX(`colture di etichetta: ${cropCodes(P.crops) || UNK()}`, `label crops: ${cropCodes(P.crops) || UNK()}`),
      TX(`bersagli di etichetta: ${listOf(P.targets, 6) || UNK()}`, `label targets: ${listOf(P.targets, 6) || UNK()}`),
      TX(`meccanismo d'azione: ${moa || UNK()}`, `mode of action: ${moa || UNK()}`),
      TX(`autorizzazione: ${P.status || NOTCONF()}`, `authorisation: ${P.status || NOTCONF()}`),
      TX(`scadenza: ${fmtISO(P.expiry) || UNK()}`, `expiry: ${fmtISO(P.expiry) || UNK()}`),
      P.labelUrl ? TX(`scheda di etichetta: ${P.labelUrl}`, `label record: ${P.labelUrl}`) : TX(`scheda di etichetta: ${UNK()}`, `label record: ${UNK()}`)
    ].join(' · ');
  };

  /* A graded line always carries its own verdict, so it is safe under any
     heading. Used where one list is the honest shape (label timing, supply). */
  const gradedLine = (g) => {
    const head = g.strength ? pstate(g.strength) : TX('GRADO NON RICHIEDIBILE — nessuna finestra canonica risolta', 'GRADE NOT ASKABLE — no canonical window resolved');
    const ev = g.link && g.link.evidence
      ? ` · ${TX('evidenza', 'evidence')}: ${modelProse(g.link.evidence)}${g.link.source ? ` · ${TX('fonte', 'source')}: ${g.link.source}` : ''}`
      : '';
    return `${head} — ${prodLine(g)}${ev}`;
  };
  const gradedLines = (f) => (f.graded.length
    ? f.graded.map(gradedLine)
    : [TX('Nessun prodotto è collegato a questa finestra nel modello — non nominare un prodotto finché Regolatorio / Portafoglio non ne conferma uno.',
      'No product is linked to this window in the model — do not name a product until Regulatory / Portfolio confirms one.')]);

  /* ── the split (finding: BLOCKER 3, PRODUCT LAW §10 and §13) ────────────────
     Returns 1–2 sections. A verified product is one the model's label audit
     graded VERIFIED_LABEL_MATCH for THIS crop × THIS issue — not one that
     shares an active substance, and not one whose label crop list happens to
     contain the crop name. Everything else is printed with its measured state
     and the absence rule; nothing is dropped and nothing is called absent. */
  const portfolioSections = (f, headVerified) => {
    const out = [];
    const pairLabel = (f.cropKey && f.issueKey) ? `${f.crop} × ${f.issue}` : null;
    if (!f.graded.length) {
      return [S(headVerified, [TX('Nessun prodotto è collegato a questa finestra nel modello — non nominare un prodotto finché Regolatorio / Portafoglio non ne conferma uno.',
        'No product is linked to this window in the model — do not name a product until Regulatory / Portfolio confirms one.')])];
    }
    if (f.verified.length) {
      out.push(S(
        pairLabel ? TX(`${headVerified} · corrispondenza verificata su etichetta per ${pairLabel}`, `${headVerified} · verified label match for ${pairLabel}`) : headVerified,
        f.verified.map(g => {
          const ev = g.link && g.link.evidence
            ? ` · ${TX('evidenza', 'evidence')}: ${modelProse(g.link.evidence)}${g.link.source ? ` · ${TX('fonte', 'source')}: ${g.link.source}` : ''}${g.P && g.P.labelAuditDate ? ` · ${TX('audit di etichetta del', 'label audit of')} ${fmtISO(g.P.labelAuditDate)}` : ''}`
            : '';
          return prodLine(g) + ev;
        }),
        true
      ));
    }
    if (f.unverified.length) {
      const lines = f.unverified.map((g) => {
        const head = g.strength ? pstate(g.strength) : TX('GRADO NON RICHIEDIBILE', 'GRADE NOT ASKABLE');
        /* Say what the label audit DID see for this product, so the reader can
           tell "read and not found" from "never asked" (PRODUCT LAW §10). */
        /* ── UNA CORRISPONDENZA VERIFICATA PER UN'ALTRA COPPIA ─────────────
           Questa riga elenca cio che l'audit registra PER IL PRODOTTO, e le
           coppie elencate sono di altre colture. Su un caso di frumento
           stampava «Pomodoro / Oidio — CORRISPONDENZA VERIFICATA SU ETICHETTA»
           in un documento destinato al rivenditore: vero, correttamente
           circoscritto, e a due centimetri dal nome di un prodotto presentato
           come DA VERIFICARE per QUESTO caso.

               UNA VERITA MESSA ACCANTO ALLA DOMANDA SBAGLIATA SI LEGGE COME
               UNA RISPOSTA A QUELLA DOMANDA.

           Il fatto resta — serve a distinguere «letto e non trovato» da «mai
           chiesto». Cambia che la riga dice, per esteso, che quelle coppie NON
           sono questa, prima di elencarle. */
        const otherPairs = TX('per ALTRE colture × problemi, non per questo caso',
          'for OTHER crops × issues, not for this case');
        const seen = (g.P && Array.isArray(g.P.links) && g.P.links.length)
          ? TX(`in questa lettura l'audit di etichetta registra per questo prodotto ${otherPairs}: ${g.P.links.map(l => `${cropName(l.crop)} / ${issueName(l.issue)} — ${pstate(l.strength)}`).join(' · ')}`,
            `what the label audit records for this product ${otherPairs} in this reading: ${g.P.links.map(l => `${cropName(l.crop)} / ${issueName(l.issue)} — ${pstate(l.strength)}`).join(' · ')}`)
          : TX('l\'audit di etichetta non registra alcun collegamento coltura × problema per questo prodotto in questa lettura', 'the label audit records no crop × issue link at all for this product in this reading');
        return `${head} — ${prodLine(g)} · ${seen}`;
      });
      lines.push(TX(`${ABSENCE()} Questi prodotti non sono dichiarati assenti dal portafoglio: risultano non confermati per ${pairLabel || TX('questa coltura × problema', 'this crop × issue')} in questa lettura, e vanno verificati sulla scheda di etichetta nazionale prima di essere nominati.`,
        `${ABSENCE()} These products are not declared absent from the portfolio: they are unconfirmed for ${pairLabel || 'this crop × issue'} in this reading, and must be checked on the national label record before being named.`));
      const scope = f.unverified.map(g => g.P && g.P.labelAuditScopeNote).filter(Boolean)[0];
      if (scope) lines.push(TX(`Portata dell'audit: ${modelProse(scope)}`, `Audit scope: ${scope}`));
      out.push(S(
        pairLabel
          ? TX(`Da verificare · nessuna corrispondenza confermata per ${pairLabel} in questa lettura`, `To be verified · no confirmed match for ${pairLabel} in this reading`)
          : TX('Da verificare · nessuna finestra canonica risolta, quindi nessun grado di etichetta è richiedibile', 'To be verified · no canonical window resolved, so no label grade can be asked'),
        lines, true
      ));
    }
    return out;
  };

  /* Every field-message record in this package is SYNTHETIC_DEMO (0 real of 18
     in the model). A demo record may never supply a field observation. */
  const realField = (c) => ((c && c.fieldMessages) || []).filter(m => m && m.demo !== true && m.provenance !== 'SYNTHETIC_DEMO');
  const FIELD_NONE = () => TX('Nessuna osservazione di campo verificata su questo caso. Ogni messaggio di campo in questo pacchetto è un record dimostrativo, quindi nessuno viene stampato come intelligence.',
    'No verified field observation on this case. Every field message in this package is a demonstration record, so none is printed as intelligence.');
  const fieldLines = (c) => {
    const ms = realField(c);
    return ms.length ? ms.map(m => `${m.person} · ${m.when}: “${m.text}” → ${m.signal}`) : [FIELD_NONE()];
  };

  /* Competitor communication is real (REAL_SOURCE corpus) but the model does not
     attribute it to a case, so no per-case count is printed. */
  const compLines = () => {
    const C = coll('competitorActivities');
    if (!C || !C.count) return [TX('In questa lettura non è caricato alcun corpus di comunicazione dei concorrenti.', 'No competitor communication corpus is loaded in this reading.')];
    return [
      TX(`${C.count} elementi di comunicazione dei concorrenti osservati nelle fonti pubbliche monitorate (provenienza ${C.provenance}).`,
        `${C.count} competitor communication items observed in the monitored public sources (provenance ${C.provenance}).`),
      TX('L\'attribuzione di quegli elementi a questa coltura × regione NON è stabilita nel modello — qui non viene stampato alcun conteggio per caso. Aprire Concorrenza per leggere il corpus.',
        'Attribution of those items to this crop × region is NOT established in the model — no per-case competitor count is printed here. Open Competitor Watch to read the corpus.'),
      /* LA DISTINZIONE SI SPIEGA, NON SI CITA.
         I due token erano il motore che parlava a se stesso dentro un documento
         destinato al canale commerciale. La frase dice la stessa cosa, e si
         legge senza conoscere il pacchetto canonico. */
      TX('Solo comunicazione osservata. Che un messaggio sia arrivato in Italia non significa che l\'Italia ne fosse il bersaglio, e non si deduce alcuna strategia, spesa o quota.',
        'Observed communication only. That a message reached Italy does not mean Italy was its target, and no strategy, spend or share is inferred.')
    ];
  };

  const sourcesLines = (f) => {
    const W = f.W; const SR = coll('sources'); const out = [];
    out.push(W
      ? TX(`Finestra canonica ${W.windowId} · provenienza ${W.provenance} · stato della data ${W.dateState} · confidenza ${W.dateConfidence} · ultima validazione ${f.lastValidated}.`,
        `Canonical window ${W.windowId} · provenance ${W.provenance} · date state ${W.dateState} · confidence ${W.dateConfidence} · last validated ${f.lastValidated}.`)
      : TX(`Nessuna finestra canonica risolta per questo caso — ogni fatto di finestra qui sopra vale ${NOTCONF()}.`,
        `No canonical window resolved for this case — every window fact above reads ${NOTCONF()}.`));
    out.push((W && (W.sourceIds || []).length)
      ? TX(`Fonti dichiarate: ${W.sourceIds.join(', ')}.`, `Declared sources: ${W.sourceIds.join(', ')}.`)
      /* La frase nominava il campo del motore invece del fatto. Chi legge il
         foglio non ha SOURCE_IDS: ha una domanda, «da dove vem isto?», e la
         risposta onesta e che questa finestra non ne dichiara nessuna. */
      : TX(`Questa finestra non dichiara alcuna fonte — l'elenco delle fonti per questo caso vale ${NOTCONF()}.`,
        `This window declares no source — the per-case source list reads ${NOTCONF()}.`));
    if (SR) out.push(TX(`Registro delle fonti: ${SR.count} fonti pubbliche registrate (provenienza ${SR.provenance}). I conteggi di osservazioni collegate per caso non sono stabiliti nel modello e non vengono stampati.`,
      `Source register: ${SR.count} registered public sources (provenance ${SR.provenance}). Per-case connected-observation counts are not established in the model and are not printed.`));
    out.push(TX(`Data di riferimento Sintonia ${refStamp()}. Tutti i conteggi di giorni qui sopra sono misurati da quella data.`,
      `Sintonia reference date ${refStamp()}. All day counts above are measured from that date.`));
    return out;
  };

  const NOT_ESTABLISHED = (whatIt, whatEn) => TX(
    `${whatIt}: NON NOTO — nel modello non esiste alcuna narrativa Sintonia approvata per questo caso, quindi qui non si afferma nulla.`,
    `${whatEn}: NON NOTO — no approved Sintonia narrative exists for this case in the model, so nothing is asserted here.`);
  const WHYNOW = () => NOT_ESTABLISHED('Perché ora', 'Why-now');

  const GEN = {
    'SALES / RTV': (c, f) => ({
      doc: TX('BRIEF OPERATIVO · VENDITE DI CAMPO', 'FIELD SALES ACTION BRIEF'),
      role: TX('Rappresentante tecnico di vendita', 'Technical Sales Representative'),
      pages: TX('1–2 pagine', '1–2 pages'),
      purpose: TX('Mettere il rappresentante in condizione di aprire la conversazione con il cliente sui fatti confermati della finestra e del portafoglio, e con l\'elenco esplicito di ciò che non è confermato.',
        'Help the representative enter customer conversations with the confirmed window and portfolio facts, and with an explicit list of what is not confirmed.'),
      sections: [
        S(TX('1 · Che cosa sta succedendo', '1 · What is happening'), [NOT_ESTABLISHED('Narrativa della situazione', 'Situation narrative'),
          TX(`Confermato: ${f.issue} (${f.issueType}) è il problema per cui questa finestra su ${f.crop} è registrata, in ${f.region}. Stato attuale ${f.status}${f.statusReason ? ` — ${f.statusReason}` : ''}.`,
            `Confirmed: ${f.issue} (${f.issueType}) is the issue this ${f.crop} window is registered against, in ${f.region}. Current status ${f.status}${f.statusReason ? ` — ${f.statusReason}` : ''}.`)]),
        S(TX('2 · Dove', '2 · Where'), [`${f.region} · ${f.crop}.`,
          TX(`Indicazioni sulle aree limitrofe: ${UNK()}. Il modello non registra alcun elenco di regioni limitrofe per questa finestra.`,
            `Adjacent-area guidance: ${UNK()}. The model records no adjacent-region list for this window.`)]),
        S(TX('3 · Perché conta adesso', '3 · Why this matters now') + INTERP(), [WHYNOW(),
          TX(`Ciò che si può dire dal record: la finestra va da ${f.from} a ${f.to} ed è ${f.windowState}.`,
            `What can be said from the record: the window runs ${f.from} → ${f.to} and is ${f.windowState}.`)]),
        S(TX('4 · Finestra colturale / di applicazione attuale', '4 · Current crop / application window'), window_(f)),
        ...portfolioSections(f, TX('5 · Che cosa ADAMA può offrire', '5 · What ADAMA can offer')),
        S(TX('6 · Che cosa sappiamo', '6 · What we know'), [
          TX(`Finestra canonica in archivio: ${f.W ? f.W.windowId : TX('nessuna', 'none')} · provenienza ${f.W ? f.W.provenance : NOTCONF()}.`,
            `Canonical window on file: ${f.W ? f.W.windowId : 'none'} · provenance ${f.W ? f.W.provenance : NOTCONF()}.`),
          TX(`Prodotti ADAMA registrati collegati a questa finestra: ${f.products.length}, di cui ${f.verified.length} con corrispondenza verificata su etichetta per questa coltura × problema.`,
            `Registered ADAMA products linked to this window: ${f.products.length}, of which ${f.verified.length} carry a verified label match for this crop × issue.`),
          TX(`Fase colturale osservata: ${f.cropStageLabel}. Fase del problema osservata: ${f.issueStageLabel}.`,
            `Observed crop stage: ${f.cropStageLabel}. Observed issue stage: ${f.issueStageLabel}.`)
        ], true),
        S(TX('7 · Che cosa resta da validare', '7 · What still needs validation'), [
          TX('Pressione attuale in campo — su questa finestra non è registrata alcuna fase osservata.', 'Current field pressure — no observed stage is recorded on this window.'),
          TX('Trigger di etichetta e momento di applicazione — si leggono sulla scheda di etichetta, non su questo brief.', 'Label trigger and application timing — read the label record, not this brief.'),
          TX('Se il segnale si estenda alle aree limitrofe — non esiste alcun record di area limitrofa.', 'Whether the signal extends into adjacent areas — no adjacent-area record exists.'),
          TX('Attività dei concorrenti attribuibile a questa coltura × regione.', 'Competitor activity attributable to this crop × region.'),
          f.unverified.length ? TX(`La posizione di etichetta dei ${f.unverified.length} prodotti elencati sotto "Da verificare".`, `The label position of the ${f.unverified.length} products listed under "To be verified".`) : null
        ], true),
        S(TX('8 · Guida alla conversazione con il cliente', '8 · Customer conversation guide') + INTERP(), [
          TX(`APRIRE — «Stiamo seguendo ${f.lowIssue} su ${f.lowCrop} in ${f.region} e la finestra registrata rende utile rivedere la protezione.»`,
            `OPEN — “We are following ${f.lowIssue} on ${f.lowCrop} in ${f.region} and the registered window makes it worth reviewing protection.”`),
          TX('ASCOLTARE — prima ascoltare; non affermare incidenza, fase o pressione che il cliente non abbia riportato. Sintonia non ne ha osservata alcuna.',
            'UNDERSTAND — listen first; do not assert incidence, stage or pressure the customer has not reported. Sintonia has not observed any.'),
          f.verified.length
            ? TX('COLLEGARE — «ADAMA ha opzioni di portafoglio registrate con corrispondenza verificata su etichetta per questa coltura e questo bersaglio. Confermiamo insieme posizione di etichetta e tempistica esatte per la sua situazione.»',
              'CONNECT — “ADAMA has registered portfolio options with a verified label match for this crop and target. Let us confirm the exact label position and timing for your situation.”')
            : TX('COLLEGARE — «Stiamo verificando la nostra posizione di portafoglio per questa situazione e torneremo con una risposta confermata su etichetta.»',
              'CONNECT — “We are checking our portfolio position for this situation and will come back with a confirmed label answer.”'),
          f.verified.length
            ? TX(`PRODOTTO — ${f.verified.map(g => g.name).join(' · ')}. Solo fatti verificati di etichetta; mai un'affermazione fuori dall'etichetta approvata; mai un'efficacia inventata. Non nominare i prodotti elencati sotto "Da verificare".`,
              `PRODUCT — ${f.verified.map(g => g.name).join(' · ')}. Only verified label facts; never a claim outside the approved label; never an invented efficacy. Do not name the products listed under "To be verified".`)
            : null
        ], true),
        S(TX('9 · Domande da fare al cliente', '9 · Questions to ask the customer') + INTERP(), [
          TX('A che fase colturale siete?', 'What crop stage are you seeing?'),
          TX('Avete osservato sintomi o catture?', 'Have you observed symptoms or captures?'),
          TX(`Nella vostra azienda è già stata confermata la presenza di ${f.issue}?`, `Has ${f.lowIssue} already been confirmed on your farm?`),
          TX('Qual è stato il trattamento precedente?', 'What was the previous treatment?'),
          TX('Che condizioni state vedendo in campo?', 'What field conditions are you seeing?'),
          TX('State già valutando una decisione di trattamento?', 'Are you already evaluating a treatment decision?')
        ], true),
        S(TX('10 · Perché parlarne adesso', '10 · Why talk about this now') + INTERP(), [
          TX(`La finestra registrata è ${f.windowState}`, `The registered window is ${f.windowState}`),
          TX(`Esiste un record di finestra canonica per questa coltura × problema × regione (${f.W ? f.W.windowId : TX('nessuno', 'none')})`,
            `A canonical window record exists for this crop × issue × region (${f.W ? f.W.windowId : 'none'})`),
          f.verified.length
            ? TX(`Esistono ${f.verified.length} corrispondenze ADAMA verificate su etichetta`, `${f.verified.length} verified ADAMA label match(es) exist`)
            : TX('Nessuna posizione di portafoglio è ancora confermata', 'No portfolio position is confirmed yet'),
          TX(`Pressione in campo: ${f.issueStage} — questa non è un'affermazione di pressione`, `Field pressure: ${f.issueStage} — this is not a pressure claim`)
        ], true),
        S(TX('Il tuo obiettivo', 'Your objective') + INTERP(), [
          TX('Aprire la conversazione.', 'Open the conversation.'),
          TX('Validare che cosa sta vedendo il cliente.', 'Validate what the customer is seeing.'),
          f.verified.length
            ? TX('Posizionare il portafoglio verificato rigorosamente entro l\'etichetta.', 'Position the verified portfolio strictly within the label.')
            : TX('Non posizionare alcun prodotto finché Regolatorio / Portafoglio non ne conferma uno.', 'Do not position a product until Regulatory / Portfolio confirms one.'),
          TX('Registrare che cosa è stato osservato.', 'Record what was observed.')
        ], true),
        S(TX('11 · Che cosa riportare a Sintonia', '11 · What to report back to Sintonia'), [
          TX('Che cosa ha riportato il cliente?', 'What did the customer report?'),
          TX('Il problema è stato confermato?', 'Was the issue confirmed?'),
          TX('Che fase colturale?', 'What crop stage?'),
          TX('Che prodotto sta valutando?', 'What product are they considering?'),
          TX('Quale concorrente è stato citato?', 'What competitor was mentioned?'),
          TX('Sintonia deve continuare a monitorare questo caso?', 'Should Sintonia continue monitoring this case?')
        ], true),
        S(TX('12 · Fonti / data', '12 · Sources / date'), sourcesLines(f))
      ]
    }),
    'MARKETING': (c, f) => ({
      doc: TX('BRIEF OPERATIVO · MARKETING', 'MARKETING ACTION BRIEF'),
      role: TX('Marketing · comunicazione regionale', 'Marketing · regional communication'),
      pages: TX('2 pagine', '2 pages'),
      purpose: TX('Dare al Marketing il contesto confermato, il territorio di messaggio sostenibile e i limiti necessari per preparare materiale di supporto regionale.',
        'Give Marketing the confirmed context, the supportable message territory and the boundaries needed to prepare regional support material.'),
      sections: [
        S(TX('Caso', 'Case'), [TX(`${f.issue} · ${f.crop} · ${f.region} · stato ${statusName(f.status)}`, `${f.issue} · ${f.crop} · ${f.region} · status ${statusName(f.status)}`)]),
        S(TX('Pubblico', 'Audience') + INTERP(), [TX(`Agricoltori e rivenditori nei distretti di ${f.lowCrop} in ${f.region}; la rete commerciale ADAMA come primo relè.`,
          `Growers and dealers in ${f.region} ${f.lowCrop} districts; ADAMA field sales as first relay.`)]),
        S(TX('Perché ora', 'Why now') + INTERP(), [WHYNOW(), ...window_(f)]),
        S(TX('Che cosa dice il campo', 'What the field is saying'), fieldLines(c), true),
        S(TX('Che cosa dicono le fonti ufficiali / tecniche', 'What official / technical sources are saying'), [NOT_ESTABLISHED('Sintesi delle fonti', 'Source summary'), ...sourcesLines(f)]),
        ...portfolioSections(f, TX('Rilevanza di portafoglio ADAMA', 'ADAMA portfolio relevance')),
        S(TX('Comunicazione dei concorrenti osservata', 'Competitor communication observed'), compLines(), true),
        S(TX('Opportunità di comunicazione', 'Communication opportunity') + INTERP(), [
          TX(`Comunicazione tecnica regionale, guidata dalla tempistica, su ${f.lowIssue} in ${f.lowCrop} mentre la finestra è ${f.windowState}.`,
            `Regional, timing-led technical communication on ${f.lowIssue} in ${f.lowCrop} while the window is ${f.windowState}.`)]),
        S(TX('Territorio di messaggio chiave', 'Key message territory') + INTERP(), [
          TX('Consapevolezza di tempistica e monitoraggio', 'Timing and monitoring awareness'),
          TX('Coerenza di portafoglio conforme all\'etichetta per la coppia coltura × bersaglio', 'Label-compliant portfolio fit for the crop × target'),
          TX('Il monitoraggio regionale come innesco dell\'attenzione', 'Regional monitoring as the trigger for attention')
        ], true),
        /* PRODUCT LAW §10 and finding BLOCKER 3 · this list is derived from the
           SAME grade the portfolio sections are derived from, so the two cannot
           contradict each other on the same page. */
        S(TX('Affermazioni che possiamo sostenere', 'Claims we can support'), f.verified.length ? [
          TX(`${f.verified.map(g => g.name).join(' · ')} — corrispondenza verificata su etichetta per ${f.crop} × ${f.issue}, letta nell'audit delle etichette ufficiali italiane del modello.`,
            `${f.verified.map(g => g.name).join(' · ')} — verified label match for ${f.crop} × ${f.issue}, read in the model's audit of the official Italian labels.`),
          ...f.verified.map(g => TX(`${g.name} è registrato in Italia — autorizzazione ${(g.P && g.P.status) || NOTCONF()}, scadenza ${(g.P && fmtISO(g.P.expiry)) || UNK()}.`,
            `${g.name} is registered in Italy — authorisation ${(g.P && g.P.status) || NOTCONF()}, expiry ${(g.P && fmtISO(g.P.expiry)) || UNK()}.`)),
          TX('Le colture e i bersagli di etichetta di ciascuno sono quelli stampati nella sezione di portafoglio qui sopra.',
            'The label crops and targets of each are as printed in the portfolio section above.'),
          TX(`Esiste una finestra canonica per ${f.crop} × ${f.issue} in ${f.region}.`, `A canonical window exists for ${f.crop} × ${f.issue} in ${f.region}.`),
          f.unverified.length
            ? TX(`La comunicazione non deve nominare i ${f.unverified.length} prodotti elencati sotto "Da verificare": per questa coltura × problema non hanno corrispondenza confermata in questa lettura.`,
              `Communication must not name the ${f.unverified.length} products listed under "To be verified": they have no confirmed match for this crop × issue in this reading.`)
            : null
        ] : [
          TX(`Nessuna corrispondenza di etichetta confermata per ${f.crop} × ${f.issue} in questa lettura — la comunicazione non deve nominare un prodotto.`,
            `No confirmed label match for ${f.crop} × ${f.issue} in this reading — communication must not name a product.`),
          TX(`${ABSENCE()} I prodotti elencati sopra restano nel portafoglio; qui non sono confermati per questa coppia coltura × problema.`,
            `${ABSENCE()} The products listed above remain in the portfolio; they are simply not confirmed here for this crop × issue pair.`)
        ], true),
        S(TX('Affermazioni che non possiamo fare', 'Claims we must not make'), [
          TX('Incidenza, pressione o «si sta diffondendo nella regione» — su questa finestra non esiste alcuna fase osservata',
            'Incidence, pressure or “spreading across the region” — no observed stage exists on this window'),
          TX('Efficacia, resa o risultati economici', 'Efficacy, yield or revenue outcomes'),
          TX('Qualsiasi cosa fuori dall\'etichetta approvata', 'Anything outside the approved label'),
          TX('Strategia, spesa o quota dei concorrenti', 'Competitor strategy, spend or share'),
          TX('Qualsiasi tempistica di applicazione non letta sulla scheda di etichetta', 'Any application timing not read from the label record'),
          TX('Rilevanza di prodotto dedotta da una sostanza attiva condivisa o dalla sola presenza della coltura nell\'elenco di etichetta',
            'Product relevance inferred from a shared active substance, or from the crop merely appearing in the label crop list')
        ], true),
        S(TX('Materiali suggeriti', 'Suggested assets') + INTERP(), [
          TX('Scheda di supporto vendite regionale', 'Regional sales support card'),
          TX('Materiale di messaggio per il rivenditore', 'Dealer messaging asset'),
          TX('Contenuto tecnico', 'Technical post'),
          TX('Materiale di supporto per il rivenditore', 'Dealer support material'),
          TX('Slide di presentazione per la rete commerciale', 'Field-sales presentation slide'),
          TX('Video agronomico breve', 'Short agronomic video')
        ], true),
        S(TX('Urgenza', 'Urgency'), [`${f.status} · ${f.windowState}`])
      ]
    }),
    'MARKET DEVELOPMENT': (c, f) => ({
      doc: TX('BRIEF OPERATIVO · SVILUPPO MERCATO', 'MARKET DEVELOPMENT ACTION BRIEF'),
      role: TX('Sviluppo Mercato', 'Market Development'),
      pages: TX('1–2 pagine', '1–2 pages'),
      purpose: TX('Validare il segnale, giudicare la rilevanza regionale e decidere dove guardare dopo.',
        'Validate the signal, judge regional relevance and decide where to look next.'),
      sections: [
        S(TX('Che cosa è cambiato', 'What changed'), [NOT_ESTABLISHED('Narrativa del cambiamento', 'Change narrative'),
          TX(`Sul record: finestra ${f.W ? f.W.windowId : TX('nessuna', 'none')}, ultima validazione ${f.lastValidated}, stato ${statusName(f.status)}${f.statusReason ? ` — ${f.statusReason}` : ''}.`,
            `On the record: window ${f.W ? f.W.windowId : 'none'} last validated ${f.lastValidated}, status ${f.status}${f.statusReason ? ` — ${f.statusReason}` : ''}.`)]),
        S(TX('Perché merita attenzione', 'Why this deserves attention') + INTERP(), [WHYNOW()]),
        S(TX('Contesto regionale', 'Regional context'), [
          TX(`${f.region} — ${f.crop}. Solo precisione regionale; nessuna coordinata locale.`, `${f.region} — ${f.crop}. Regional precision only; no local coordinates.`),
          TX(`Elenco delle aree limitrofe: ${UNK()}. Peso della superficie colturale regionale per questo caso: ${UNK()} in questa lettura.`,
            `Adjacent-area list: ${UNK()}. Regional crop-area weight for this case: ${UNK()} in this reading.`)]),
        ...portfolioSections(f, TX('Connessione di portafoglio', 'Portfolio connection')),
        S(TX('Voce del campo', 'Field voice'), fieldLines(c), true),
        S(TX('Che cosa va validato', 'What needs validation'), [
          TX('Pressione attuale e fase colturale — su questa finestra entrambe risultano non osservate (NOT_OBSERVED)', 'Current pressure and crop stage — both read not observed (NOT_OBSERVED) on this window'),
          TX('Trigger di etichetta — non registrato; leggere la scheda di etichetta', 'Label trigger — not recorded; read the label record'),
          TX('Movimento nelle aree limitrofe — non esiste alcun record di area limitrofa', 'Adjacent-area movement — no adjacent-area record exists'),
          TX('Attività dei concorrenti attribuibile a questa coltura × regione', 'Competitor activity attributable to this crop × region')
        ], true),
        S(TX('Dove validare dopo', 'Where to validate next') + INTERP(), [
          TX('La serie di bollettini regionali che pubblica per questa coltura e questa regione', 'The regional bulletin series that publishes for this crop and region'),
          TX('I colleghi di campo che coprono la regione', 'Field colleagues covering the region'),
          TX('La scheda di etichetta nazionale di ogni prodotto elencato qui sopra', 'The national label record for every product listed above')
        ], true),
        S(TX('Chi contattare / ascoltare', 'Who to contact / listen to') + INTERP(), [
          TX('Servizio fitosanitario / di consulenza regionale per la regione', 'Regional phytosanitary / advisory service for the region'),
          TX('Rappresentanti di vendita nella regione', 'Field sales representatives in the region'),
          TX('Organizzazioni di produttori e reti tecniche che coprono la coltura', 'Producer organisations and technical networks covering the crop')
        ], true),
        S(TX('Contesto concorrenza', 'Competitor context'), compLines(), true),
        S(TX('Prossime 48 ore / 7 giorni', 'Next 48h / 7 days') + INTERP(), [
          TX('48 ore — confermare il segnale con il prossimo aggiornamento regionale e un collega di campo', '48h — confirm the signal with the next regional update and one field colleague'),
          TX('7 giorni — decidere se estendere o attendere; informare Vendite e Marketing se confermato', '7 days — decide expand / hold; brief Sales and Marketing if confirmed')
        ], true)
      ]
    }),
    'TECHNICAL / SCIENCE': (c, f) => ({
      doc: TX('BRIEF DI VALIDAZIONE TECNICA', 'TECHNICAL VALIDATION BRIEF'),
      role: TX('Tecnico / Scienza', 'Technical / Science'),
      pages: TX('2–3 pagine', '2–3 pages'),
      purpose: TX('Validare la pressione agronomica e il momento di applicazione. Questo non è un documento di vendita.',
        'Validate agronomic pressure and application timing. This is not a sales document.'),
      sections: [
        S(TX('Segnale in esame', 'Signal under review'), [
          `${f.issue} (${f.issueType}) · ${f.crop} · ${f.region}`,
          TX(`Nome scientifico / tassonomico di questo problema: ${UNK()} sul record di finestra canonica.`,
            `Scientific / taxonomic name for this issue: ${UNK()} on the canonical window record.`)]),
        S(TX('Evidenza agronomica disponibile', 'Agronomic evidence available'), [NOT_ESTABLISHED('Narrativa dell\'evidenza', 'Evidence narrative'), ...sourcesLines(f)]),
        S(TX('Fase colturale', 'Crop stage'), [`${f.cropStageLabel}${f.cropStage === 'NOT_OBSERVED'
          ? TX(' — CROP_STAGE non è registrato su questa finestra; nessuna fase può essere affermata a valle.', ' — CROP_STAGE is not recorded on this window; no stage may be asserted downstream.') : ''}`]),
        S(TX('Segnale di malattia / parassita', 'Disease / pest signal'), [`${f.issueStageLabel}${f.issueStage === 'NOT_OBSERVED'
          ? TX(' — ISSUE_STAGE non è registrato su questa finestra; questa non è un\'affermazione di bassa pressione, è un\'assenza di osservazione.', ' — ISSUE_STAGE is not recorded on this window; this is not a low-pressure claim, it is an absence of observation.') : ''}`]),
        S(TX('Monitoraggio ufficiale', 'Official monitoring'), [
          TX('I conteggi di osservazioni ufficiali per caso non sono stabiliti nel modello e non vengono stampati.',
            'Per-case official-observation counts are not established in the model and are not printed.'),
          ...sourcesLines(f).slice(0, 2)]),
        S(TX('Contesto scientifico', 'Scientific context'), (() => { const SC = coll('scienceRecords'); const RS = coll('resistance'); return [
          SC ? TX(`Corpus scientifico: ${SC.count} record (provenienza ${SC.provenance}). Il collegamento a livello di caso non è stabilito, quindi non viene stampato alcun conteggio per caso. L'affiliazione dell'autore non è mai trattata come luogo di campo.`,
            `Science corpus: ${SC.count} records (provenance ${SC.provenance}). Case-level linkage is not established, so no per-case count is printed. Author affiliation is never treated as field location.`)
            : TX(`Corpus scientifico: ${UNK()}.`, `Science corpus: ${UNK()}.`),
          RS ? TX(`Corpus di resistenza: ${RS.count} meccanismi documentati (provenienza ${RS.provenance}) disponibili per l'argomento di gestione della resistenza.`,
            `Resistance corpus: ${RS.count} documented mechanisms (provenance ${RS.provenance}) available for the resistance-management argument.`) : null
        ]; })()),
        /* One list, every line carrying its own grade — a technical reader needs
           to see the unconfirmed ones beside the confirmed ones, not on another
           page, and no heading here asserts relevance. */
        S(TX('Tempistica di etichetta · ogni prodotto con il proprio grado di audit', 'Label timing · every product with its own audit grade'),
          window_(f).slice(3).concat(gradedLines(f)), true),
        S(TX('Voce del campo', 'Field voice'), fieldLines(c), true),
        S(TX('Che cosa resta ignoto', 'What is still unknown'), [
          TX('Fenologia della stagione corrente per questa regione', 'Current-season phenology for this region'),
          TX('Pressione attuale di parassita / malattia', 'Current pest / disease pressure'),
          TX('Trigger di etichetta e dose — custoditi solo sulla scheda di etichetta', 'Label trigger and dose — held only in the label record'),
          TX('Se il segnale si estenda alle aree limitrofe', 'Whether the signal extends into adjacent areas')
        ], true),
        S(TX('Domande da validare', 'Questions to validate') + INTERP(), [
          TX('La fase riportata è coerente con il modello fenologico della regione?', 'Is the reported stage consistent with the phenology model for the region?'),
          TX('Il segnale raggiunge la soglia di intervento regionale?', 'Does the signal meet the regional intervention threshold?'),
          TX('La finestra di etichetta si sovrappone alla fase attuale?', 'Does the label window overlap the current stage?'),
          TX('C\'è un fattore meteorologico che cambia la tempistica questa settimana?', 'Any weather driver that changes timing this week?'),
          TX('C\'è una guida di gestione della resistenza da allegare?', 'Is there resistance-management guidance to attach?')
        ], true),
        S(TX('Formato della risposta', 'Recommendation format'), [
          TX('Restituire: CONFERMATO / NON CONFERMATO / SERVONO ALTRI DATI, con data e fonte.',
            'Return: CONFIRMED / NOT CONFIRMED / NEEDS MORE DATA, with date and source.')])
      ]
    }),
    'REGULATORY / PORTFOLIO': (c, f) => ({
      doc: TX('VERIFICA REGOLATORIA E DI PORTAFOGLIO', 'REGULATORY & PORTFOLIO CHECK'),
      role: TX('Regolatorio / Portafoglio', 'Regulatory / Portfolio'),
      pages: TX('1–2 pagine', '1–2 pages'),
      purpose: TX('Confermare autorizzazione e posizionamento di etichetta dei prodotti collegati a questo caso prima di qualsiasi messaggio di campo o di marketing.',
        'Confirm authorisation and label positioning for the products linked to this case before any field or marketing message.'),
      sections: [
        S(TX('Caso', 'Case'), [`${f.issue} · ${f.crop} · ${f.region}`]),
        ...portfolioSections(f, TX('Prodotti collegati', 'Products linked')),
        S(TX('Autorizzazione Italia', 'Italy authorisation'), [
          TX('Lo stato di autorizzazione e la scadenza qui sopra sono letti dal modello prodotti Sintonia. Riconfermare lo stato attuale nella banca dati nazionale (Banca Dati Fitosanitari) tramite l\'URL della scheda di etichetta di ogni prodotto prima del rilascio.',
            'Authorisation status and expiry above are read from the Sintonia product model. Re-confirm current status in the national database (Banca Dati Fitosanitari) via the label record URL for each product before release.')]),
        S(TX('Dose · intervallo di applicazione · numero massimo di applicazioni', 'Dose · application interval · maximum applications'), [
          TX(`${NOT_OBS.replace('OSSERVABILE DA FONTI ESTERNE', 'DERIVABILE DA SINTONIA')} — si legge sulla scheda di etichetta corrente. Sintonia non deriva mai la dose.`,
            `${NOT_OBS.replace('OSSERVABILE DA FONTI ESTERNE', 'DERIVABILE DA SINTONIA')} — read from the current label record. Sintonia never derives dose.`)]),
        S(TX('Scadenza / contesto regolatorio', 'Expiry / regulatory context'), [
          TX('Confermare la scadenza dell\'autorizzazione e qualsiasi rinnovo, restrizione o condizione di fascia di rispetto in corso.',
            'Confirm authorisation expiry and any pending renewal, restriction or buffer-zone condition.'),
          ...(() => {
            const soon = f.products.filter(x => x.P && x.P.expiry).map(x => TX(`${x.P.name} · scadenza ${fmtISO(x.P.expiry)}`, `${x.P.name} · expiry ${fmtISO(x.P.expiry)}`));
            return soon.length
              ? [TX(`Scadenze in archivio: ${soon.join(' · ')}.`, `Expiries on file: ${soon.join(' · ')}.`)]
              : [TX(`Scadenze in archivio: ${UNK()}.`, `Expiries on file: ${UNK()}.`)];
          })()]),
        S(TX('Incertezze', 'Uncertainties'), [
          ...(() => {
            const noAi = f.products.filter(x => !x.P || !(Array.isArray(x.P.ai) ? x.P.ai.filter(Boolean).length : x.P.ai)).map(x => x.name);
            return noAi.length
              ? [TX(`Sostanza attiva non stabilita nel modello per: ${noAi.join(', ')}.`, `Active substance not established in the model for: ${noAi.join(', ')}.`)]
              : [TX('La sostanza attiva è stabilita nel modello per ogni prodotto collegato a questa finestra.', 'Active substance is established in the model for every product linked to this window.')];
          })(),
          f.unverified.length
            ? TX(`${f.unverified.length} prodotti su ${f.graded.length} non hanno corrispondenza confermata per ${f.crop} × ${f.issue} in questa lettura — confermare manualmente sulla scheda di etichetta se una posizione esista. ${ABSENCE()}`,
              `${f.unverified.length} of ${f.graded.length} products carry no confirmed match for ${f.crop} × ${f.issue} in this reading — confirm manually on the label record whether a position exists. ${ABSENCE()}`)
            : null,
          f.verified.length ? null
            : TX('Nessun prodotto è stato verificato su etichetta per questa coppia coltura × problema — confermare se esista una posizione ADAMA.',
              'No product is verified on the label for this crop × target pair — confirm whether any ADAMA position exists.'),
          TX('Su questa finestra non è registrato alcun innesco di etichetta, quindi la tempistica di applicazione mostrata a valle deve provenire unicamente dalla scheda di etichetta.',
            'No label trigger is recorded on this window, so the application timing shown anywhere downstream must come from the label record only.')
        ], true),
        S(TX('Richiede conferma manuale', 'Requires manual confirmation'), [
          TX('Dicitura del bersaglio di etichetta rispetto al parassita / malattia osservato', 'Label target wording vs. observed pest/disease'),
          TX('Elenco delle colture (incluso il gruppo colturale)', 'Crop listing (including crop group)'),
          TX('Restrizioni regionali o stagionali', 'Regional or seasonal restrictions'),
          TX('Avvisi di cambio di stato sottoscritti', 'Status change alerts subscribed')
        ], true),
        S(TX('Restituire a', 'Return to'), [
          TX('Vendite, Marketing e Sviluppo Mercato sono in attesa di questa verifica per poter nominare un prodotto.',
            'Sales, Marketing and Market Development are blocked on this check for product naming.')])
      ]
    }),
    'SUPPLY': (c, f) => ({
      doc: TX('RICHIESTA DI PRONTEZZA · SUPPLY', 'SUPPLY READINESS REQUEST'),
      role: 'Supply',
      pages: TX('1 pagina', '1 page'),
      purpose: TX('Richiesta di passaggio di consegne — l\'intelligence esterna non può conoscere la disponibilità. Questa non è un\'affermazione di disponibilità.',
        'Handoff request — external intelligence cannot know availability. This is not an availability claim.'),
      sections: [
        S(TX('Caso', 'Case'), [`${f.issue} · ${f.crop} · ${f.region} · ${f.status}`]),
        S(TX('Prodotti di portafoglio · ognuno con il proprio grado di audit di etichetta', 'Portfolio products · each with its own label audit grade'),
          f.graded.length
            ? f.graded.map(g => `${g.name} — ${g.strength ? pstate(g.strength) : TX('GRADO NON RICHIEDIBILE', 'GRADE NOT ASKABLE')}`)
            : [TX('Nessun prodotto collegato a questa finestra', 'No product linked to this window')], true),
        S(TX('Tempistica', 'Timing'), window_(f)),
        S(TX('Perché rivedere la prontezza', 'Why readiness should be reviewed'), [
          TX(`La finestra registrata va da ${f.from} a ${f.to} ed è ${f.windowState}.`, `The registered window runs ${f.from} → ${f.to} and is ${f.windowState}.`),
          (() => { const n = realField(c).length; return n
            ? TX(`${n} osservazioni di campo verificate su questo caso.`, `${n} verified field observation(s) on this case.`)
            : TX('Nessuna osservazione di campo verificata sostiene una lettura di domanda su questo caso, e nessuna domanda è implicata.',
              'No verified field observation supports a demand read on this case, and no demand is implied.'); })(),
          TX(`Domanda, ordini e tempistica di acquisto dell'agricoltore sono ${NOT_OBS}.`, `Demand, orders and grower purchase timing are ${NOT_OBS}.`)
        ]),
        S(TX('Richiesta', 'Request'), [
          TX('Rivedere la prontezza per la regione e la finestra qui sopra. Sintonia non ha alcuna visione di disponibilità, ordini o previsioni e non formula alcuna affermazione su nessuno dei tre.',
            'Please review readiness for the region and window above. Sintonia has no view of availability, orders or forecast and makes no claim about any of them.')])
      ]
    })
  };

  const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;');

  function build(dept, c, lang) {
    const g = GEN[dept]; if (!g) return null;
    LG = (lang === 'it' || lang === 'en') ? lang : detectLang();
    const f = F(c || {});
    const b = g(c || {}, f);
    b.dept = dept; b.case = c; b.facts = f;
    /* PRODUCT LAW §11 and finding 4 · the crop is named with the label the rest
       of the portal shows ('Vite'), so the brief and the case screen cannot
       name the same crop differently. */
    /* Il titolo non dichiara ignoranza quando il record ha i fatti: la
       condizione era «esiste una finestra canonica», e adesso e «esiste un
       nome da scrivere», che e la domanda giusta. */
    b.title = (f.cropKey || f.issueKey)
      ? `${f.issue} · ${f.crop} · ${f.region}`
      /* Presentation only. With no canonical window all three axes are the same
         absence, and printing it three times in a 22pt headline made the
         document unreadable without making it any truer. MEASURED: 0 of 3 real
         opportunities and 0 of 29 scenarios hit this today — IT-OPP-003 is the
         one case with no window, and its own record carries no crop, issue or
         region either, so there is nothing to fall back to. */
      : TX('Caso senza finestra canonica risolta — coltura, problema e regione NON NOTI',
        'Case with no canonical window resolved — crop, issue and region NON NOTI');
    /* UN TOKEN DEL MOTORE NON E UNA PAROLA DA STAMPARE.
       La pillola della priorita scriveva ACT_NOW / FUTURE_PREPARATION /
       NOT_ESTABLISHED dentro un documento destinato al canale commerciale. Lo
       stato e canonico e ha gia un nome nelle due lingue: si usa quello. */
    b.priority = statusName(f.status);
    b.accentColor = f.color;
    b.windowFrom = f.from; b.windowTo = f.to; b.windowState = f.windowState;
    /* PRODUCT LAW §10 · no product is promoted above another; this is the list
       of verified matches, or null when there is none. */
    b.primary = f.verifiedNames.length === 1 ? f.verifiedNames[0] : null;
    b.verifiedNames = f.verifiedNames.slice();
    b.unverifiedCount = f.unverified.length;
    /* The language the document was BUILT in. printHtml() reuses it rather than
       re-detecting, so a switch between screen and print cannot produce a
       half-translated PDF. */
    b.lang = LG;
    /* ONE clock (PRODUCT LAW §6). This is the model's reference date, not a
       wall clock, and it is labelled as such wherever it is printed. */
    b.referenceDate = refISO();
    b.generated = TX(`${refStamp()} · data di riferimento Sintonia (non un timestamp di stampa)`,
      `${refStamp()} · Sintonia reference date (not a print timestamp)`);
    b.summary = `${b.doc} — ${b.title}\n`
      + TX(`Per: ${b.role} · Priorità: ${b.priority} · ${b.generated} · Sintonia ADAMA Italia · Ambiente dimostrativo\n\n`,
        `For: ${b.role} · Priority: ${b.priority} · ${b.generated} · Sintonia ADAMA Italy · Demonstration environment\n\n`)
      + b.sections.map(s => s.h.toUpperCase() + '\n' + s.lines.map(l => (s.bullets ? '• ' : '') + l).join('\n')).join('\n\n');
    return b;
  }

  function printHtml(b) {
    /* The brief's CSS comes from the local _ds/adama-brandwell package that ships
       with the client folder — no CDN, no network. */
    LG = (b && (b.lang === 'it' || b.lang === 'en')) ? b.lang : detectLang();
    const base = (typeof document !== 'undefined' && document.baseURI) ? document.baseURI.replace(/[^/]*$/, '') : '';
    const col = b.accentColor || '#009845';
    const showLoop = b.dept === 'SALES / RTV';
    const verified = (b.verifiedNames || []);
    return `<!doctype html><html lang="${LG}"><head><meta charset="utf-8"><title>${esc(b.doc)} · ${esc(b.title)}</title>
<link rel="stylesheet" href="${base}_ds/adama-brandwell/tokens/typography.css">
<style>@page{size:A4;margin:16mm 16mm 18mm}body{margin:0;font-family:'LL Brown','BrownLL',Arial,sans-serif;color:#231F20;font-size:10.5pt;line-height:1.45}
.top{display:flex;justify-content:space-between;align-items:flex-start;border-bottom:3px solid #009845;padding-bottom:8px;margin-bottom:12px}.brand{font-size:9pt;letter-spacing:.18em;font-weight:700;color:#009845}.brand small{display:block;letter-spacing:.12em;color:#978B87;font-weight:600;margin-top:2px}
.doc{font-size:9pt;letter-spacing:.14em;font-weight:700;color:#978B87;text-align:right}.doc b{display:block;color:#231F20;font-size:9pt;margin-top:2px}
h1{font-size:22pt;line-height:1.05;margin:0 0 6px;letter-spacing:-.01em}.meta{display:flex;gap:18px;flex-wrap:wrap;font-size:9pt;color:#6E6663;margin-bottom:12px}.meta b{color:#231F20}
.pri{display:inline-block;padding:3px 10px;border-radius:999px;background:${col};color:#fff;font-weight:700;font-size:8.5pt;letter-spacing:.08em}.purpose{background:#f4f2f2;border-radius:10px;padding:10px 12px;font-size:10pt;margin-bottom:12px}
h2{font-size:9pt;letter-spacing:.14em;color:${col};margin:12px 0 4px;text-transform:uppercase;page-break-after:avoid}p,li{margin:0 0 3px}ul{margin:0;padding-left:16px}
.loop{margin-top:14px;border:2px solid #009845;border-radius:12px;padding:10px 12px;page-break-inside:avoid}.loop b{color:#009845;letter-spacing:.12em;font-size:9pt}
.foot{margin-top:16px;padding-top:8px;border-top:1px solid #CBC5C3;font-size:8pt;color:#978B87;display:flex;justify-content:space-between}</style></head><body>
<div class="top"><div class="brand">SINTONIA<small>${esc(TX('ADAMA ITALIA · BRIEF OPERATIVO', 'ADAMA ITALY · ACTION BRIEF'))}</small></div><div class="doc">${esc(b.doc)}<b>${esc(b.generated)}</b>${esc(TX('AMBIENTE DIMOSTRATIVO', 'DEMONSTRATION ENVIRONMENT'))}</div></div>
<h1>${esc(b.title)}</h1>
<div class="meta"><span>${esc(TX('PER:', 'FOR:'))} <b>${esc(b.role)}</b></span><span>${esc(TX('PRIORITÀ:', 'PRIORITY:'))} <span class="pri">${esc(b.priority)}</span></span><span>${esc(TX('Finestra:', 'Window:'))} <b>${esc(b.windowFrom)} → ${esc(b.windowTo)}</b> · ${esc(b.windowState)}</span>${verified.length ? `<span>${esc(TX('Corrispondenze verificate su etichetta:', 'Verified label matches:'))} <b>${esc(verified.join(' · '))}</b></span>` : ''}</div>
<div class="purpose"><b>${esc(TX('Scopo · ', 'Purpose · '))}</b>${esc(b.purpose)}</div>
${b.sections.map(s => `<h2>${esc(s.h)}</h2>${s.bullets ? '<ul>' + s.lines.map(l => `<li>${esc(l)}</li>`).join('') + '</ul>' : s.lines.map(l => `<p>${esc(l)}</p>`).join('')}`).join('')}
${showLoop ? `<div class="loop"><b>${esc(TX('OSSERVAZIONI DI CAMPO', 'FIELD OBSERVATIONS'))}</b><p>${esc(TX('Le osservazioni raccolte in campo possono rientrare in Sintonia attraverso l\'integrazione opzionale della rete commerciale. Sintonia riceve e classifica; non richiede l\'invio di messaggi.', 'Observations collected in the field can return into Sintonia through the optional field-sales integration. Sintonia receives and classifies; it requests no message to be sent.'))}</p></div>` : ''}
<div class="foot"><span>${esc(TX(`Fatti letti dal modello Sintonia alla data di riferimento ${b.generated}. Solo dimostrativo. Non è implicato alcun dato di disponibilità, ordini, quota o ROI.`, `Facts read from the Sintonia model at reference date ${b.generated}. Demonstration only. No availability, order, share or ROI data is implied.`))}</span><span>Listen &gt; Learn &gt; Deliver</span></div>
<script>window.onload=function(){setTimeout(function(){window.print()},400)}</script></body></html>`;
  }

  window.ITALY_BRIEFS = { build, printHtml, departments: Object.keys(GEN) };
})();
