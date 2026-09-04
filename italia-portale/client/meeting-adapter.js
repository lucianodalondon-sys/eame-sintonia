/* SINTONIA · L'ADATTATORE DELLA RIUNIONE — meeting-adapter.js
   ===========================================================================
   LO SNAPSHOT DIVENTA L'UNICA VOCE. IL PORTALE SMETTE DI DEDURRE.

   PERCHE QUESTO FILE ESISTE — un numero, misurato
   ------------------------------------------------
   Il portale costruiva `status` leggendo il pacchetto grezzo da 5,9 MB e
   deducendo. Lo snapshot lo porta gia deciso dal motore. Non coincidevano:

       stato          portale (dedotto)    snapshot (motore)
       ACT_NOW               16                   2
       VALIDATE_NOW           0                   3
       WATCH                  0                  22
       PREPARE_NOW           11        (stato che il canone non ha)
       finestra            null x43        16 definite · 2 aperte ora

   Quattordici schede dicevano AGIRE ORA a una riunione commerciale su casi
   che il motore tiene in OSSERVAZIONE. Non era una svista di copy: erano due
   padroni della stessa frase.

       QUANDO DUE STRATI RISPONDONO ALLA STESSA DOMANDA, QUELLO CHE PARLA
       PIU FORTE NON E QUELLO CHE HA RAGIONE. E QUELLO CHE E PIU VICINO
       ALLO SCHERMO.

   COSA FA — e cosa non fara mai
   ------------------------------
   COPIA. Prende i campi che il motore ha gia deciso e li mette sul record che
   la schermata legge. Poi traduce i codici con `meeting-labels.js`.

   NON calcola stato, priorita, finestra, prodotto, ruolo dell'evidenza, mappa
   delle azioni ne stato di pubblicazione. Se un domani calcolasse qualcosa,
   ci sarebbero di nuovo due padroni — ed e esattamente cio che il gate
   `ACTION_MAP_FROM_ENGINE` e `NO_RAW_BYPASS` esistono per impedire.

       L'ADATTATORE NON HA OPINIONI. HA UNA LISTA DI CAMPI.

   FALLISCE FORTE
   --------------
   Se lo snapshot manca, o se un ID sullo schermo non esiste nello snapshot,
   questo file NON completa in silenzio con il vecchio valore: alza
   `MEETING_ADAPTER.FAULTS`, che i gate leggono. Un adattatore che ripara da
   solo nasconde proprio il difetto che deve rivelare.
   =========================================================================== */
(function () {
  'use strict';

  const SNAP = (typeof window !== 'undefined' && window.MEETING_INTELLIGENCE) || null;
  const L = (typeof window !== 'undefined' && window.MEETING_LABELS) || null;
  const FAULTS = [];

  if (!SNAP) { FAULTS.push('SNAPSHOT_ABSENT'); }
  if (!L) { FAULTS.push('LABELS_ABSENT'); }

  const BY_ID = {};
  if (SNAP && Array.isArray(SNAP.CASES)) SNAP.CASES.forEach((c) => { BY_ID[c.ID] = c; });

  const lab = (t, c, lang) => (L ? L.label(t, c, lang) : null);
  const labs = (t, cs, lang) => (L ? L.labels(t, cs, lang) : []);

  /* ── IL RIMANDO PER L'ANALISTA NON E UNA FRASE PER IL CLIENTE ────────────
     Alcune frasi che il motore localizza finiscono con un rimando interno:

         «la fonte che sostiene il caso non dice di intervenire
          — vedi NEED_DIRECTION e la frase originale in NEED_EXCERPT.»

     La prima meta e un fatto, scritto per essere letto. La seconda dice a un
     analista in quale CAMPO guardare, e in riunione e rumore con l'aspetto di
     un errore. Non si riscrive la frase del motore: si taglia la coda che
     nomina campi, e il fatto resta intero.

         TAGLIARE UN RIMANDO NON E CENSURARE UN CONTENUTO:
         IL CONTENUTO E IL CAMPO, E IL CAMPO LO MOSTRIAMO A PARTE.

     `NEED_DIRECTION` viaggia comunque, con la sua etichetta umana, in
     `needDirectionL`. Si taglia solo se la coda contiene davvero un codice —
     una frase senza codici non viene toccata. */
  const CODE_SHAPE = /[A-Z][A-Z0-9]{2,}(?:_[A-Z0-9]+)+/;
  function trimAnalystPointer(text) {
    if (typeof text !== 'string' || !text) return text;
    const i = text.search(/\s[—–-]\s(?:vedi|see|cfr\.?|vedere)\b/i);
    if (i < 0) return text;
    const tail = text.slice(i);
    if (!CODE_SHAPE.test(tail)) return text;
    return text.slice(0, i).replace(/[\s,;:]+$/, '') + '.';
  }

  /* ── I QUATTRO MODI DELLA MAPPA · ordine di lettura, non graduatoria ────
     «Chi agisce ora» viene prima di «chi segue» perche e la domanda che una
     riunione fa per prima, non perche un'area valga piu di un'altra. */
  const ACTION_STATE_ORDER = { ACT: 0, VALIDATE: 1, PREPARE: 2, WATCH: 3, NO_ACTION: 4 };

  /* Il colore di ogni area resta quello che il portale gia usa: l'adattatore
     non introduce una tavolozza nuova. */
  function departmentRows(c, lang) {
    const m = c.ACTION_BY_DEPARTMENT || {};
    return Object.keys(m).map((k) => {
      const d = m[k] || {};
      return {
        department: k,
        departmentL: lab('DEPARTMENT', k, lang) || k,
        actionState: d.ACTION_STATE || null,
        actionStateL: lab('ACTION_STATE', d.ACTION_STATE, lang),
        action: d.ACTION || null,
        actionL: lab('ACTION', d.ACTION, lang),
        whyCode: d.WHY_CODE || null,
        whyL: lab('ACTION_WHY_CODE', d.WHY_CODE, lang),
        dependency: d.DEPENDENCY || null,
        dependencyL: lab('DEPENDENCY', d.DEPENDENCY, lang),
        nextTrigger: d.NEXT_TRIGGER || null,
        nextTriggerL: lab('NEXT_TRIGGER', d.NEXT_TRIGGER, lang),
        evidence: d.EVIDENCE || [],
        rank: ACTION_STATE_ORDER[d.ACTION_STATE] === undefined ? 9 : ACTION_STATE_ORDER[d.ACTION_STATE]
      };
    }).sort((a, b) => a.rank - b.rank);
  }

  /* ── TUTTI I PRODOTTI · §11 · nessun «primario + altri N» ───────────────
     Se il motore non ha una regola difendibile per eleggere un vincitore,
     la schermata non ne elegge uno. Restituiamo la ragione, cosi la tela puo
     DIRLO invece di tacere. */
  function portfolioRows(c, lang) {
    return (c.PORTFOLIO_MATCHES || []).map((p) => ({
      productId: p.PRODUCT_ID,
      name: p.PRODUCT_NAME,
      registration: p.REGISTRATION_NUMBER || null,
      actives: p.ACTIVE_INGREDIENTS || [],
      moa: p.MODE_OF_ACTION || [],
      cropFit: p.CROP_FIT || null,
      cropFitL: lab('CROP_FIT', p.CROP_FIT, lang),
      targetFit: p.TARGET_FIT || null,
      targetFitL: lab('TARGET_FIT', p.TARGET_FIT, lang),
      regionalFit: p.REGIONAL_FIT || null,
      regionalFitL: lab('REGIONAL_FIT', p.REGIONAL_FIT, lang),
      regulatoryFit: p.REGULATORY_FIT || null,
      regulatoryFitL: lab('REGULATORY_FIT', p.REGULATORY_FIT, lang),
      windowFit: p.WINDOW_FIT || null,
      windowFitL: lab('WINDOW_FIT', p.WINDOW_FIT, lang),
      validationState: p.VALIDATION_STATE || null,
      validationStateL: lab('VALIDATION_STATE', p.VALIDATION_STATE, lang),
      matchReason: p.MATCH_REASON || null,
      matchReasonL: lab('MATCH_REASON', p.MATCH_REASON, lang),
      restrictions: (p.RESTRICTIONS || []).map((r) => ({
        code: r.CODE,
        codeL: lab('RESTRICTION_CODE', r.CODE, lang),
        active: r.ACTIVE_INGREDIENT || null,
        date: r.DATE || null,
        evidenceId: r.EVIDENCE_ID || null
      })),
      evidence: p.EVIDENCE || []
    }));
  }

  /* ── PERCHE ORA · i cinque anelli, con il fatto che li regge ──────────── */
  function chainRows(c, lang) {
    const ch = c.WHY_NOW_CHAIN || {};
    return Object.keys(ch).map((k) => {
      const v = ch[k] || {};
      return {
        link: k,
        linkL: lab('CHAIN_LINK', k, lang) || k,
        ok: v.OK === true,
        fact: v.FACT === null || v.FACT === undefined ? null : String(v.FACT),
        /* Un FACT puo essere esso stesso un codice del motore (un tipo di
           finestra, un metodo). Si prova a tradurlo; se non e un codice noto
           resta il fatto grezzo, che e una data o un nome — leggibile. */
        factL: lab('WINDOW_TYPE', v.FACT, lang)
            || lab('WINDOW_OPEN_NOW_METHOD', v.FACT, lang)
            || lab('PRODUCT_LINK_STATE', v.FACT, lang)
            || null,
        evidence: v.EVIDENCE || []
      };
    });
  }

  /* ── LE PROVE · raggruppate per ruolo, l'intelligenza negativa in vista ─
     WEAKENS / CONTRADICTS / CLOSES non si nascondono e non si spostano in
     fondo: §15 le vuole leggibili quanto le altre. */
  const NEGATIVE_ROLES = { WEAKENS: 1, CONTRADICTS: 1, CLOSES: 1 };
  function evidenceRows(c, lang) {
    return (c.EVIDENCE_ROLES || []).map((e) => ({
      evidenceId: e.EVIDENCE_ID,
      entityType: e.ENTITY_TYPE || null,
      familyL: lab('EVIDENCE_FAMILY', e.ENTITY_TYPE, lang),
      role: e.ROLE || null,
      roleL: lab('EVIDENCE_ROLE', e.ROLE, lang),
      whyCode: e.WHY_CODE || null,
      whyL: lab('EVIDENCE_WHY_CODE', e.WHY_CODE, lang),
      negative: !!NEGATIVE_ROLES[e.ROLE]
    }));
  }

  /* ── LA FINESTRA, IN UNA FRASE UMANA ────────────────────────────────────
     Tre fatti distinti che una sola riga non deve fondere: se la condizione
     e dichiarata, di che TIPO e, e se e soddisfatta ORA. Una finestra di cui
     non si conosce lo stato non e una finestra chiusa. */
  function windowView(c, lang) {
    const defined = c.WINDOW_DEFINED === 'YES';
    const open = c.WINDOW_OPEN_NOW;
    return {
      defined: defined,
      definedL: lab('WINDOW_DEFINED', c.WINDOW_DEFINED, lang),
      type: c.WINDOW_TYPE || null,
      typeL: lab('WINDOW_TYPE', c.WINDOW_TYPE, lang),
      ruleState: c.WINDOW_RULE_STATE || null,
      ruleStateL: lab('WINDOW_RULE_STATE', c.WINDOW_RULE_STATE, lang),
      openNow: open || null,
      openNowL: lab('WINDOW_OPEN_NOW', open, lang),
      method: c.WINDOW_OPEN_NOW_METHOD || null,
      methodL: lab('WINDOW_OPEN_NOW_METHOD', c.WINDOW_OPEN_NOW_METHOD, lang),
      /* La condizione originale e prosa di ricerca in portoghese: NON
         attraversa. Si dichiara il documento che la contiene. */
      conditionPtOnly: c.WINDOW_CONDITION__PT_ONLY === true,
      conditionEvidenceId: c.WINDOW_EVIDENCE_ID || null,
      ruleEvidenceId: c.WINDOW_RULE_EVIDENCE_ID || null,
      isAgronomic: c.WINDOW_RULE_STATE !== 'RULE_ADMINISTRATIVE_ONLY',
      isOpenNow: open === 'YES',
      isUnknownNow: open === 'UNKNOWN'
    };
  }

  /* ── IL BRIEF · prima lettura breve, dal codice del motore ──────────── */
  function briefRows(c, lang) {
    return (c.INTELLIGENCE_BRIEF || []).map((b) => ({
      code: b.CODE,
      text: lab('BRIEF_CODE', b.CODE, lang),
      values: b.VALUES || {}
    })).filter((r) => r.text);
  }

  /* ── LA VISTA COMPLETA DI UN CASO ───────────────────────────────────── */
  function view(id, lang) {
    const c = BY_ID[id];
    if (!c) return null;
    const pm = portfolioRows(c, lang);
    return {
      id: c.ID,
      /* stato — dal motore, non dedotto */
      status: c.STATUS,
      statusL: lab('STATUS', c.STATUS, lang),
      statusWhyL: lab('STATUS_WHY', c.STATUS, lang),
      commercialPriority: c.COMMERCIAL_PRIORITY,
      commercialPriorityL: lab('COMMERCIAL_PRIORITY', c.COMMERCIAL_PRIORITY, lang),
      archetype: c.ARCHETYPE,
      archetypeL: lab('ARCHETYPE', c.ARCHETYPE, lang),
      opportunityState: c.OPPORTUNITY_STATE,
      opportunityStateL: lab('OPPORTUNITY_STATE', c.OPPORTUNITY_STATE, lang),

      /* la catraca, visibile — §16: cio che e validato e cio che non lo e */
      publicationState: c.PUBLICATION_STATE,
      publicationStateL: lab('PUBLICATION_STATE', c.PUBLICATION_STATE, lang),
      publicationStateShort: lab('PUBLICATION_STATE_SHORT', c.PUBLICATION_STATE, lang),
      isPublishable: c.PUBLICATION_STATE === 'PUBLISHABLE',
      trailStateL: lab('TRAIL_STATE', c.TRAIL_STATE, lang),

      /* perche e un'opportunita commerciale — testo gia localizzato dal motore */
      whyCommercial: trimAnalystPointer((lang === 'en') ? (c.WHY_COMMERCIAL_EN || null) : (c.WHY_COMMERCIAL_IT || null)),
      whyCommercialCodes: c.WHY_COMMERCIAL_CODES || [],
      whyCommercialL: labs('WHY_COMMERCIAL_CODES', c.WHY_COMMERCIAL_CODES, lang),
      doesNotProve: (lang === 'en') ? (c.COMMERCIAL_DOES_NOT_PROVE_EN || null) : (c.COMMERCIAL_DOES_NOT_PROVE_IT || null),
      proves: (lang === 'en') ? (c.WHAT_IT_PROVES_EN || null) : (c.WHAT_IT_PROVES_IT || null),
      notProves: (lang === 'en') ? (c.WHAT_IT_DOES_NOT_PROVE_EN || null) : (c.WHAT_IT_DOES_NOT_PROVE_IT || null),

      /* perche ora */
      whyNowCodes: c.WHY_NOW_CODES || [],
      whyNowL: labs('WHY_NOW_CODES', c.WHY_NOW_CODES, lang),
      chain: chainRows(c, lang),
      chainComplete: (c.WHY_NOW_CODES || []).indexOf('CADEIA_COMPLETA') >= 0,

      /* la finestra */
      window: windowView(c, lang),

      /* stadio dell'insetto ≠ raccomandazione · §17 D */
      pestStage: c.PEST_STAGE_STATE || null,
      pestStageL: lab('PEST_STAGE_STATE', c.PEST_STAGE_STATE, lang),
      actionRecommendation: c.ACTION_RECOMMENDATION_STATE || null,
      actionRecommendationL: lab('ACTION_RECOMMENDATION_STATE', c.ACTION_RECOMMENDATION_STATE, lang),
      stageVsRecommendationNote: (L && L.STAGE_VS_RECOMMENDATION_NOTE)
        ? L.STAGE_VS_RECOMMENDATION_NOTE[(lang === 'en') ? 'en' : 'it'] : null,
      /* la nota serve solo quando i due DAVVERO divergono */
      stageDivergesFromRecommendation:
        (c.PEST_STAGE_STATE === 'STAGE_ENDED' || c.PEST_STAGE_STATE === 'STAGE_DECLINING')
        && (c.ACTION_RECOMMENDATION_STATE === 'CONTINUE_RECOMMENDED'
            || c.ACTION_RECOMMENDATION_STATE === 'START_RECOMMENDED'),
      threshold: c.THRESHOLD_STATE || null,
      thresholdL: lab('THRESHOLD_STATE', c.THRESHOLD_STATE, lang),

      /* direzione della fonte */
      needDirection: c.NEED_DIRECTION || null,
      needDirectionL: lab('NEED_DIRECTION', c.NEED_DIRECTION, lang),
      needMethodL: lab('NEED_METHOD', c.NEED_METHOD, lang),
      needEvidenceId: c.NEED_EVIDENCE_ID || null,

      /* attualita */
      signalCurrency: c.SIGNAL_CURRENCY || null,
      signalCurrencyL: lab('SIGNAL_CURRENCY', c.SIGNAL_CURRENCY, lang),
      signalDate: c.SIGNAL_DATE || null,
      signalAgeDays: c.SIGNAL_AGE_DAYS === undefined ? null : c.SIGNAL_AGE_DAYS,

      /* che cosa manca ancora */
      whatIsMissing: c.WHAT_IS_MISSING || [],
      whatIsMissingL: labs('WHAT_IS_MISSING', c.WHAT_IS_MISSING, lang),
      externalMaterialReady: c.EXTERNAL_MATERIAL_READY || null,
      externalMaterialReadyL: lab('EXTERNAL_MATERIAL_READY', c.EXTERNAL_MATERIAL_READY, lang),
      externalBlockersL: labs('EXTERNAL_BLOCKER_CODES', c.EXTERNAL_BLOCKER_CODES, lang),

      /* il portafoglio · TUTTI */
      portfolio: pm,
      portfolioCount: pm.length,
      hasPortfolio: pm.length > 0,
      primaryMatch: c.PRIMARY_MATCH || null,
      primaryMatchReason: c.PRIMARY_MATCH_REASON || null,
      primaryMatchReasonL: lab('PRIMARY_MATCH_REASON', c.PRIMARY_MATCH_REASON, lang),
      /* Un principale si mostra come principale SOLO se il motore ha la regola. */
      hasDefensiblePrimary: !!c.PRIMARY_MATCH
        && c.PRIMARY_MATCH_REASON !== 'SEM_REGRA_DEFENSAVEL_PARA_ESCOLHER',

      /* la mappa delle azioni · dal motore */
      departments: departmentRows(c, lang),

      /* le prove */
      evidence: evidenceRows(c, lang),
      evidenceCount: c.EVIDENCE_COUNT === undefined ? null : c.EVIDENCE_COUNT,
      sourceUrls: c.SOURCE_URLS || [],
      brief: briefRows(c, lang),

      /* magnitudine — solo quando difendibile */
      magnitude: c.COMMERCIAL_MAGNITUDE || null,
      magnitudeL: lab('COMMERCIAL_MAGNITUDE', c.COMMERCIAL_MAGNITUDE, lang),
      magnitudeDimensions: c.COMMERCIAL_MAGNITUDE_DIMENSIONS || {},
      timingBasisL: lab('COMMERCIAL_TIMING_BASIS', c.COMMERCIAL_TIMING_BASIS, lang),
      scopeL: lab('GEOGRAPHIC_SCOPE', c.GEOGRAPHIC_SCOPE, lang)
    };
  }

  /* ── L'INNESTO · il motore vince sul dedotto, e si dichiara ─────────────
     I campi canonici sostituiscono quelli che il portale deduceva. I nomi
     originali restano intatti sotto `record.rawDerived`, cosi un gate puo
     provare che la sostituzione e avvenuta e di quanto. */
  const CANON = ['STATUS', 'PUBLICATION_STATE', 'WINDOW_DEFINED', 'WINDOW_OPEN_NOW',
                 'WINDOW_TYPE', 'WINDOW_RULE_STATE', 'COMMERCIAL_PRIORITY'];

  function attach(records) {
    const replaced = [];
    const missing = [];
    (records || []).forEach((r) => {
      const c = BY_ID[r.id];
      if (!c) { missing.push(r.id); return; }
      r.rawDerived = { status: r.status, windowState: r.windowState };
      /* LO SNAPSHOT VINCE. Questa riga e tutta la missione. */
      if (r.status !== c.STATUS) replaced.push({ id: r.id, from: r.status, to: c.STATUS });
      r.status = c.STATUS;
      r.publicationState = c.PUBLICATION_STATE;
      r.windowDefined = c.WINDOW_DEFINED;
      r.windowOpenNow = c.WINDOW_OPEN_NOW;
      r.windowType = c.WINDOW_TYPE;
      r.windowRuleState = c.WINDOW_RULE_STATE;
      r.meeting = c;                     /* il caso canonico, verbatim */
      r.fromSnapshot = true;
    });
    if (missing.length) FAULTS.push('IDS_NOT_IN_SNAPSHOT:' + missing.join(','));
    return { replaced: replaced, missing: missing };
  }

  /* ── I CONTEGGI · calcolati dallo snapshot, mai scritti a mano ─────────
     §19: nessun numero della schermata puo essere una costante. Ognuno di
     questi si ricava contando lo snapshot al momento del disegno. */
  function counts() {
    const C = (SNAP && SNAP.CASES) || [];
    const by = (f) => C.reduce((a, c) => { const k = f(c); if (k != null) a[k] = (a[k] || 0) + 1; return a; }, {});
    const st = by((c) => c.STATUS);
    return {
      total: C.length,
      byStatus: st,
      actNow: st.ACT_NOW || 0,
      validateNow: st.VALIDATE_NOW || 0,
      prepare: st.FUTURE_PREPARATION || 0,
      watch: st.WATCH || 0,
      toValidate: st.TO_VALIDATE || 0,
      byPublication: by((c) => c.PUBLICATION_STATE),
      publishable: C.filter((c) => c.PUBLICATION_STATE === 'PUBLISHABLE').length,
      validationRequired: C.filter((c) => c.PUBLICATION_STATE === 'VALIDATION_REQUIRED').length,
      windowDefined: C.filter((c) => c.WINDOW_DEFINED === 'YES').length,
      windowOpenNow: C.filter((c) => c.WINDOW_OPEN_NOW === 'YES').length,
      withPortfolio: C.filter((c) => (c.PORTFOLIO_MATCHES || []).length > 0).length
    };
  }

  /* ══ L'INNESTO AVVIENE AL CARICAMENTO, NON AL PRIMO DISEGNO ══════════════
     L'innesto viveva solo dentro `M()`, l'accessore del portale. Chiunque
     leggesse `ITALY_APP_MODEL.collections.opportunities.records` senza passare
     di li — il generatore di PDF, un portone, un domani una vista nuova —
     vedeva ancora lo stato DEDOTTO: OSSERVARE sullo schermo e AGIRE ORA nel
     brief stampato, sullo stesso caso, nello stesso minuto.

         SE LA CORREZIONE VIVE IN UN ACCESSORE, VALE SOLO PER CHI PASSA
         DA QUELL'ACCESSORE. UNA VERITA CONDIZIONATA NON E UNA VERITA.

     Questo file si carica DOPO il modello, quindi puo innestare subito: da qui
     in poi non esiste un lettore che veda i record senza lo snapshot. La
     chiamata in `M()` resta come rete — `attach()` e idempotente. */
  var __selfAttached = null;
  if (SNAP && L && typeof window !== 'undefined'
      && window.ITALY_APP_MODEL && window.ITALY_APP_MODEL.collections
      && window.ITALY_APP_MODEL.collections.opportunities) {
    __selfAttached = attach(window.ITALY_APP_MODEL.collections.opportunities.records);
    window.ITALY_APP_MODEL.__meetingAttached = __selfAttached;
  }

  window.MEETING_ADAPTER = {
    OK: !!SNAP && !!L && FAULTS.length === 0,
    ATTACHED_AT_LOAD: __selfAttached,
    FAULTS: FAULTS,
    SOURCE_HEAD: SNAP ? SNAP.SOURCE_HEAD : null,
    BUILD_ID: SNAP ? SNAP.BUILD_ID : null,
    MEETING_CUTOFF: SNAP ? SNAP.MEETING_CUTOFF : null,
    GENERATED_AT: SNAP ? SNAP.GENERATED_AT : null,
    ENGINE_VERSION: SNAP ? SNAP.ENGINE_VERSION : null,
    RULE_VERSION: SNAP ? SNAP.RULE_VERSION : null,
    TOTAL_CASES: SNAP ? SNAP.TOTAL_CASES : null,
    CANON_FIELDS: CANON,
    byId: BY_ID,
    view: view,
    attach: attach,
    counts: counts
  };
})();
