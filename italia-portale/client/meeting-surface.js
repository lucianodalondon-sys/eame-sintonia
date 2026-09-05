/* SINTONIA · MEETING SURFACE — the canonical 43, and one owner for each fact
   ---------------------------------------------------------------------------
   This module PRESENTS. It does not decide. Every value below is copied from
   window.MEETING_INTELLIGENCE, which the engine wrote; nothing here derives a
   status, a window, a product choice or an action.

       IL MOTORE DECIDE. LA SUPERFICIE MOSTRA.

   Two contradictions were seen on a real screen and both were ownership bugs,
   not drawing bugs. They are answered here by construction:

   1 · PRODOTTO PRINCIPALE — UN SOLO PADRONE
       The legacy detail computed the primary as
           c.primary || verified[0]
       (portale.html:2758): a hand-written demo field, falling back to THE FIRST
       ELEMENT OF AN ARRAY. Two blocks reading two different arrays crown two
       different products, and both are right about their own array.

       Here the primary is PRIMARY_MATCH and nothing else. It is resolved by
       PRODUCT_ID inside PORTFOLIO_MATCHES; if the engine did not name one,
       there is NO primary and every match is shown uncrowned.

       MEASURED on the 43: PRIMARY_MATCH is non-null in exactly the 17 cases
       that have exactly ONE portfolio match, and null in all 26 others
       (PRIMARY_MATCH_REASON = SEM_REGRA_DEFENSAVEL_PARA_ESCOLHER). So
       "PRIMARY + N more" is not merely discouraged — the engine never produces
       the shape. Any screen showing it invented it.

   2 · FINESTRA — UN SOLO PADRONE
       window.ITALY_CANONICAL (italy-canonical-windows.js) holds 29 calendar
       windows keyed by LEGACY_CASE_ID (IT-OPP-*), whose CURRENT_STATUS is
       computed against a frozen reference date. It belongs to the 21
       demonstration cases and knows nothing about the canonical pairs — so it
       says "no window" exactly where the engine states a rule.

       This module NEVER reads ITALY_CANONICAL. The window comes from
       WINDOW_DEFINED / WINDOW_OPEN_NOW / WINDOW_TYPE / WINDOW_RULE_STATE and
       the evidence ids beside them.

   3 · LA REGOLA NON E LO STATO
       WINDOW_DEFINED answers "is the rule known?"
       WINDOW_OPEN_NOW answers "is the condition met right now?"
       They are carried, phrased and rendered separately. DEFINED=YES with
       OPEN_NOW=UNKNOWN reads "the rule is known, the state is not yet
       measured" — never "window open".
   --------------------------------------------------------------------------- */
(function () {
  const SNAP = () => (typeof window !== 'undefined' && window.MEETING_INTELLIGENCE) || null;
  /* ══ LA LEGGE DI RILEVANZA ADAMA, LETTA E MAI RICALCOLATA ═══════════════
     Un caso diventa OPPORTUNITA quando — e solo quando — si riesce a legare
     il fatto a un prodotto ADAMA in modo difendibile: paese, coltura,
     bersaglio, prodotto a catalogo, coltura dichiarata sulla pagina del
     prodotto, bersaglio sull'etichetta ministeriale, autorizzazione viva.

         UN PRODOTTO CHE PUO ESSERE USATO SULLA COLTURA NON E UN PRODOTTO
         CHE RISOLVE IL PROBLEMA.

     La legge ha UN proprietario, e non e questo file: vive in
     `scripts/adama_relevance.py` e il suo verdetto arriva stampato in
     `adama-relevance.js`. Qui si LEGGE. Rivalutarla qui darebbe due leggi con
     lo stesso nome, e la seconda deciderebbe cosa e un'opportunita senza che
     nessuno l'abbia approvata.

         IL VALUTATORE E UNO. IL RESTO TRASPORTA. */
  const REL = () => (typeof window !== 'undefined' && window.ADAMA_RELEVANCE) || null;
  /* Fail-closed: senza verdetto un caso NON e un'opportunita. L'assenza del
     pacchetto non promuove niente — declassa tutto a errore, che si vede. */
  const surfaceOf = (id) => {
    const r = REL();
    const v = r && r.VERDETTI && r.VERDETTI[id];
    return (v && v.SUPERFICIE) || 'ERRORE';
  };
  const verdictOf = (id) => {
    const r = REL();
    return (r && r.VERDETTI && r.VERDETTI[id]) || null;
  };
  const LB = () => (typeof window !== 'undefined' && window.MEETING_LABELS) || null;

  /* ── THE CLIENT-SAFE BOUNDARY ───────────────────────────────────────────
     A previous pass filtered only the top level, so a code sitting inside
         dict -> dict -> list -> dict -> leaf
     walked straight through. The filter is recursive and applies the SAME
     rule at every depth; containers are rebuilt, never mutated in place, so
     an emptied container disappears instead of rendering as an empty box.

         UNA FRONTIERA CHE CONTROLLA SOLO IL PRIMO LIVELLO NON E UNA FRONTIERA. */

  /* Internal bookkeeping: true of the engine's own ledger, never of the case.
     These must not cross even when nested inside evidence or product rows. */
  const BOOKKEEPING = /^(RAW|_|DEBUG|INTERNAL|TRACE|BOOK|SCRATCH)/;
  const BOOKKEEPING_EXACT = new Set([
    'RULE_VERSION', 'ENGINE_VERSION', 'OPPORTUNITY_SCORE', 'TRAIL_STATE',
    'RENDERABLE_WITH_METHOD', 'MISSING_LINKS', 'NEED_AMBIGUITY_CODES',
    'COMMERCIAL_MAGNITUDE_DIMENSIONS', 'GENERATED_AT',
  ]);
  /* Research prose written in Portuguese. It crosses as a DOCUMENT ID plus a
     flag, never as text — see the snapshot's own law. */
  const PT_ONLY = /__PT_ONLY$/;

  const isPlain = (v) => v !== null && typeof v === 'object' && !Array.isArray(v);

  /* Returns undefined for a value that must not cross, so the caller can drop
     the key entirely rather than render an empty slot. */
  function clientSafe(value, key) {
    if (typeof key === 'string' && (PT_ONLY.test(key) || BOOKKEEPING.test(key) || BOOKKEEPING_EXACT.has(key))) return undefined;
    if (Array.isArray(value)) {
      const out = [];
      for (const v of value) { const c = clientSafe(v, null); if (c !== undefined) out.push(c); }
      return out;
    }
    if (isPlain(value)) {
      const out = {};
      let kept = 0;
      for (const k of Object.keys(value)) {
        const c = clientSafe(value[k], k);
        if (c !== undefined) { out[k] = c; kept++; }
      }
      /* An object whose every field was bookkeeping is bookkeeping. Returning
         {} here is what previously produced empty cards on screen. */
      return kept ? out : undefined;
    }
    return value;
  }

  /* ── LABELS ─────────────────────────────────────────────────────────────
     A code with no phrase returns null and the caller omits the row. It NEVER
     falls back to the raw token: falling back is the leak. */
  const lab = (code, lang) => {
    if (code === null || code === undefined || code === '') return null;
    const d = LB();
    return d ? d.get(String(code), lang) : null;
  };
  /* A DISPLAY LIST CARRIES PHRASES, NOT KEYS.
     H4's rule is that any leaf the markup binds will be rendered one day, so a
     shared `token` field turns every list into a possible leak: WHAT_IS_MISSING
     carries OFFICIAL_AREA_NOT_CLIENT_SAFE, which is a reason a case is
     incomplete — not the engine's client-safe ledger — but on screen the reader
     cannot tell the two apart, and should never have to.

     Lists that need a machine hook name it for that purpose, one list at a
     time, so the hook is always deliberate. */
  const labList = (codes, lang) => (codes || []).map((c) => ({ label: lab(c, lang) })).filter((r) => r.label);
  const labListTraced = (codes, lang, field) => (codes || [])
    .map((c) => { const l = lab(c, lang); return l ? { label: l, [field]: c } : null; })
    .filter(Boolean);

  /* A BARE WORD IS NOT A KEY.
     `UNKNOWN` and `PREPARE` are engine values, but standing alone they are also
     English words, and a word that reaches the render surface is a word the
     reader can meet. Every machine value that leaves this module is qualified
     into the full token it actually is — WINDOW_OPEN_NOW_UNKNOWN, not UNKNOWN —
     so it reads as a key to a person and to the language gate alike. */
  const qual = (prefix, v) => (v === null || v === undefined || v === '' ? null : prefix + '_' + v);

  /* ── IL PUNTATORE NON E IL FATTO ─────────────────────────────────────────
     Il motore scrive la propria prosa IT/EN, e in 11 casi su 43 la chiude con
     un rimando ai propri campi:

         «...non dice di intervenire — vedi NEED_DIRECTION e la frase
           originale in NEED_EXCERPT.»

     Quella coda e stata scritta per chi legge il JSON, non per la riunione, e
     mette due chiavi interne su uno schermo italiano. Ma la frase NON puo
     essere riscritta: la prosa e del motore, e inventarne una qui sarebbe il
     difetto peggiore dei due.

     Si toglie il PUNTATORE, non l'affermazione. La frase e completa prima del
     trattone, e le due cose indicate sono gia a schermo, accanto: la direzione
     della fonte come frase tradotta, e l'estratto come il DOCUMENTO che lo
     contiene. Togliere un rimando non toglie un fatto.

         IL MOTORE E FERMO A 55c2674. LA CORREZIONE E DI PRESENTAZIONE.

     La regola e stretta di proposito: solo una coda finale, introdotta da un
     trattone, che contiene un rimando (vedi / see) e nient'altro che chiavi. */
  const POINTER_TAIL = /\s*[—–-]\s*(?:vedi|see|cfr\.?|si veda)\b[^.;]*\b[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+\b[^.;]*\.?\s*$/;
  const dePointer = (text) => {
    if (typeof text !== 'string' || !text) return { text: text || '', pointerRemoved: false };
    const cut = text.replace(POINTER_TAIL, '').trim();
    if (cut === text.trim()) return { text: text.trim(), pointerRemoved: false };
    /* Se togliere la coda lasciasse una frase monca, si preferisce la frase
       intera: un token a schermo e un difetto, una frase rotta e due. */
    if (cut.length < 12) return { text: text.trim(), pointerRemoved: false };
    return { text: /[.!?]$/.test(cut) ? cut : cut + '.', pointerRemoved: true };
  };

  /* ── THE WINDOW · rule and state, separately ────────────────────────── */
  function windowOf(c, lang) {
    const defined = c.WINDOW_DEFINED === 'YES';
    const openNow = c.WINDOW_OPEN_NOW;          /* YES · NO · UNKNOWN */
    const ruleState = c.WINDOW_RULE_STATE || null;
    const type = c.WINDOW_TYPE || null;

    /* THE RULE — is an intervention rule stated at all? */
    const ruleSentence = defined
      ? lab('windowDefinedYes', lang)
      : lab('windowDefinedNo', lang);

    /* THE STATE NOW — a separate question with a separate answer. It is only
       askable once a rule exists; with no rule there is no state to measure,
       and saying "unknown" there would imply a rule that nobody stated. */
    let stateSentence;
    if (!defined) stateSentence = lab('windowOpenNoRule', lang);
    else if (openNow === 'YES') stateSentence = lab('windowOpenYes', lang);
    else if (openNow === 'NO') stateSentence = lab('windowOpenNo', lang);
    else stateSentence = lab('windowOpenUnknown', lang);

    return {
      DEFINED: c.WINDOW_DEFINED || null,
      OPEN_NOW: qual('WINDOW_OPEN_NOW', openNow || 'UNKNOWN'),
      TYPE: type,
      RULE_STATE: ruleState,
      defined, openIsKnown: openNow === 'YES' || openNow === 'NO',
      /* Two sentences, never one. A single line here is how "the rule is
         known" became "the window is open". */
      ruleLabel: lab('lblRule', lang),
      ruleSentence,
      stateLabel: lab('lblStateNow', lang),
      stateSentence,
      typeLabel: lab(type, lang),
      ruleStateLabel: lab(ruleState, lang),
      methodLabel: lab(c.WINDOW_OPEN_NOW_METHOD, lang),
      /* The condition text itself is Portuguese research prose. It crosses as
         the document that carries it — which is true — never as text. */
      conditionDocument: c.WINDOW_EVIDENCE_ID || null,
      conditionWithheld: !!c['WINDOW_CONDITION__PT_ONLY'],
      ruleDocument: c.WINDOW_RULE_EVIDENCE_ID || null,
      isDelegatedToFarm: ruleState === 'RULE_DELEGATED_TO_FARM' || type === 'RULE_DELEGATED_TO_FARM',
      isAdministrativeOnly: ruleState === 'RULE_ADMINISTRATIVE_ONLY',
      /* SOURCE marker for the gate: this object was built from the snapshot
         and from nothing else. */
      OWNER: 'MEETING_INTELLIGENCE',
    };
  }

  /* ── THE PRODUCTS · all of them, and a primary only when named ──────── */
  function productsOf(c, lang) {
    const matches = (c.PORTFOLIO_MATCHES || []).map((m) => ({
      PRODUCT_ID: m.PRODUCT_ID,
      name: m.PRODUCT_NAME,
      registration: m.REGISTRATION_NUMBER || null,
      actives: (m.ACTIVE_INGREDIENTS || []).slice(),
      moa: (m.MODE_OF_ACTION || []).slice(),
      cropFit: lab(m.CROP_FIT, lang),
      targetFit: lab(m.TARGET_FIT, lang), targetFitCode: m.TARGET_FIT,
      regionalFit: lab(m.REGIONAL_FIT, lang), regionalFitCode: m.REGIONAL_FIT,
      regulatoryFit: lab(m.REGULATORY_FIT, lang), regulatoryFitCode: m.REGULATORY_FIT,
      windowFit: m.WINDOW_FIT === 'UNKNOWN' ? lab('UNKNOWN', lang) : lab(m.WINDOW_FIT, lang),
      validation: lab(m.VALIDATION_STATE, lang), validationCode: m.VALIDATION_STATE,
      matchReason: lab(m.MATCH_REASON, lang), matchReasonCode: m.MATCH_REASON,
      restrictions: (m.RESTRICTIONS || []).map((r) => ({
        code: r.CODE, label: lab(r.CODE, lang),
        active: r.ACTIVE_INGREDIENT || null, date: r.DATE || null,
      })),
      evidence: (m.EVIDENCE || []).slice(),
    }));

    /* THE ONLY PLACE A PRIMARY CAN COME FROM.
       Not array[0]. Not render order. Not the best-known brand. Not copy.
       If PRIMARY_MATCH names an id that is not in the match list, there is no
       primary — a dangling name is not a decision. */
    const namedId = c.PRIMARY_MATCH || null;
    const primary = namedId ? (matches.find((m) => m.PRODUCT_ID === namedId) || null) : null;

    return {
      matches,
      count: matches.length,
      primary,
      hasPrimary: !!primary,
      primaryId: primary ? primary.PRODUCT_ID : null,
      primaryReasonCode: c.PRIMARY_MATCH_REASON || null,
      primaryReason: lab(c.PRIMARY_MATCH_REASON, lang),
      /* The sentence the screen shows when the engine crowned nobody. It says
         WHY there is no primary; it does not apologise and it does not pick. */
      noPrimarySentence: matches.length ? lab('lblNoPrimary', lang) : lab('lblNoProducts', lang),
      /* La riga che la SCHEDA stampa. Nomina il prodotto solo se il motore lo
         ha nominato; altrimenti conta. Non c'e nessun ramo che scelga. */
      cardLine: (() => {
        if (primary) return primary.name;
        if (!matches.length) return lab('lblNoProductShort', lang);
        return matches.length + ' ' + lab(matches.length === 1 ? 'lblProductLinked' : 'lblProductsLinked', lang);
      })(),
      allProductsSentence: lab('lblAllProducts', lang),
      OWNER: 'MEETING_INTELLIGENCE',
    };
  }

  /* ── THE ACTION MAP · exactly the engine's departments ──────────────── */
  const DEPT_ORDER = ['MARKET_DEVELOPMENT', 'COMMERCIAL', 'MARKETING', 'TECHNICAL_SCIENTIFIC', 'SUPPLY'];
  function actionsOf(c, lang) {
    const by = c.ACTION_BY_DEPARTMENT || {};
    return DEPT_ORDER.filter((d) => by[d]).map((d) => {
      const a = by[d];
      return {
        DEPARTMENT: d,
        deptLabel: lab(d, lang),
        stateToken: qual('ACTION_STATE', a.ACTION_STATE),
        state: lab(a.ACTION_STATE, lang),
        actionToken: qual('ACTION', a.ACTION),
        action: lab(a.ACTION, lang),
        whyToken: a.WHY_CODE,
        why: lab(a.WHY_CODE, lang),
        dependency: lab(a.DEPENDENCY, lang),
        /* NEXT_TRIGGER arrives as Portuguese research prose. It is a closed
           vocabulary of two, so it is translated by exact value. An
           unrecognised trigger is WITHHELD — printing it would put Portuguese
           on an Italian screen, which is the leak this line exists to stop. */
        nextTrigger: lab(a.NEXT_TRIGGER, lang),
        nextTriggerKnown: !!lab(a.NEXT_TRIGGER, lang),
        evidence: (a.EVIDENCE || []).slice(),
        ui: (window.ITALY_APP_MODEL && window.ITALY_APP_MODEL.areaUI) ? window.ITALY_APP_MODEL.areaUI(d) : null,
      };
    });
  }

  /* ── WHY NOW · the five links, and the one that is missing ──────────── */
  const CHAIN = ['SINAL_ATUAL', 'JANELA_DEFINIDA', 'JANELA_ABERTA_AGORA', 'VINCULO_COM_PORTFOLIO', 'TEMPO_PARA_ACAO'];
  function whyNowOf(c, lang) {
    const chain = c.WHY_NOW_CHAIN || {};
    const links = CHAIN.filter((k) => chain[k]).map((k) => {
      const l = chain[k] || {};
      return {
        KEY: k, label: lab(k, lang), ok: !!l.OK,
        stateLabel: lab(l.OK ? 'lblChainOk' : 'lblChainBroken', lang),
        evidence: (l.EVIDENCE || []).slice(),
        /* FACT can be a date (safe) or an engine code (needs a phrase). */
        factCode: (typeof l.FACT === 'string' && /^[A-Z0-9_]+$/.test(l.FACT)) ? l.FACT : null,
        factLabel: (typeof l.FACT === 'string' && /^[A-Z0-9_]+$/.test(l.FACT)) ? lab(l.FACT, lang) : null,
        factDate: (typeof l.FACT === 'string' && /^\d{4}-\d{2}-\d{2}/.test(l.FACT)) ? l.FACT : null,
      };
    });
    return {
      links,
      codes: labList(c.WHY_NOW_CODES, lang),
      complete: (c.WHY_NOW_CODES || []).indexOf('CADEIA_COMPLETA') >= 0,
      brokenCount: links.filter((l) => !l.ok).length,
      OWNER: 'MEETING_INTELLIGENCE',
    };
  }

  /* ── EVIDENCE · including the evidence that cools the case ──────────── */
  const NEGATIVE_ROLES = { WEAKENS: 1, CLOSES: 1, CONTRADICTS: 1 };
  function evidenceOf(c, lang) {
    const rows = (c.EVIDENCE_ROLES || []).map((e) => ({
      id: e.EVIDENCE_ID,
      family: e.ENTITY_TYPE, familyLabel: lab(e.ENTITY_TYPE, lang),
      roleToken: e.ROLE, role: lab(e.ROLE, lang),
      whyToken: e.WHY_CODE, why: lab(e.WHY_CODE, lang),
      negative: !!NEGATIVE_ROLES[e.ROLE],
    }));
    /* The case may be cooled by a DIRECTION or a RECOMMENDATION rather than by
       an evidence role — on this build that is where the negative intelligence
       actually lives, and it must read as intelligence, not as a defect. */
    const coolingCodes = [];
    if (['NO_ACTION_RECOMMENDED', 'ACTION_SUSPENDED', 'TREATMENT_PROHIBITED', 'WINDOW_CONCLUDED'].indexOf(c.NEED_DIRECTION) >= 0) coolingCodes.push(c.NEED_DIRECTION);
    if (['NOT_NEEDED_DECLARED', 'PROHIBITED_DECLARED', 'SUSPEND_RECOMMENDED', 'CONCLUDED_DECLARED'].indexOf(c.ACTION_RECOMMENDATION_STATE) >= 0) coolingCodes.push(c.ACTION_RECOMMENDATION_STATE);
    return {
      rows,
      count: rows.length,
      negatives: rows.filter((r) => r.negative),
      cooling: labListTraced(coolingCodes, lang, 'coolingToken'),
      hasCooling: coolingCodes.length > 0,
      OWNER: 'MEETING_INTELLIGENCE',
    };
  }

  /* ── ONE CASE ───────────────────────────────────────────────────────── */
  function caseOf(raw, lang) {
    const AM = window.ITALY_APP_MODEL || null;
    const c = clientSafe(raw, null) || {};

    const cropL = lab(c.CROP, lang), targetL = lab(c.TARGET, lang), geoL = lab(c.GEOGRAPHY, lang);
    /* The category drives the card MASS — the visual language of a14b9e1,
       reused, not re-invented. An unclassified case stays neutral. */
    const catKey = (() => {
      const t = c.TARGET || '';
      if (/BOTRYTIS|MILDEW/.test(t)) return 'disease';
      if (/ECHINOCHLOA/.test(t)) return 'weed';
      if (t) return 'pest';
      return 'unknown';
    })();
    const surface = AM && AM.categorySurface ? AM.categorySurface(catKey) : '#564F4D';
    const ONS = (AM && AM.ON_SURFACE) || {};

    const whyC = dePointer(lang === 'en' ? c.WHY_COMMERCIAL_EN : c.WHY_COMMERCIAL_IT);
    const win = windowOf(c, lang);
    const prod = productsOf(c, lang);

    return {
      id: c.ID,
      crop: cropL, target: targetL, geography: geoL,
      cropCode: c.CROP, targetCode: c.TARGET, geoCode: c.GEOGRAPHY,
      /* UNA SCHEDA SENZA TITOLO NON E UNA SCHEDA.
         Un caso su 43 non ha ne coltura ne bersaglio: e una data regolatoria
         europea (O5_REGULATORY_PREPARATION), e l'assenza del bersaglio e un
         FATTO che il motore dichiara — NO_AGRONOMIC_TARGET sta in
         WHAT_IS_MISSING. Il titolo cade allora sull'ARCHETIPO, che e la
         dichiarazione del motore su PERCHE il caso esiste. Non e prosa
         inventata: e l'unica cosa vera che si puo intestare a questa scheda.

         25 casi su 43 non hanno bersaglio: quelli si intestano con la
         coltura, che basta. Solo questo non ha nessuno dei due. */
      title: [cropL, targetL].filter(Boolean).join(' · ') || lab(c.ARCHETYPE, lang) || '',
      titleFromArchetype: !cropL && !targetL,
      hasCategory: catKey !== 'unknown',
      surfaceDark: surface,
      onInk: ONS.ink, onBody: ONS.body, onMuted: ONS.muted,
      onChip: ONS.chip, onChipEdge: ONS.chipEdge,
      onWell: ONS.well, onWellEdge: ONS.wellEdge, onRule: ONS.rule,
      actPill: (AM && AM.ACT_PILL) || { bg: '#1AB963', ink: '#110E0D' },

      statusCode: c.STATUS, status: lab(c.STATUS, lang),
      isActNow: c.STATUS === 'ACT_NOW',
      priorityCode: c.COMMERCIAL_PRIORITY, priority: lab(c.COMMERCIAL_PRIORITY, lang),
      /* VALIDATION_REQUIRED is never hidden and never dressed as validated. */
      publicationCode: c.PUBLICATION_STATE, publication: lab(c.PUBLICATION_STATE, lang),
      isPublishable: c.PUBLICATION_STATE === 'PUBLISHABLE',
      archetypeCode: c.ARCHETYPE, archetype: lab(c.ARCHETYPE, lang),
      scopeLabel: lab(c.GEOGRAPHIC_SCOPE, lang),

      /* WHY COMMERCIAL comes from the engine, in the reader's language.
         The frontend writes no prose of its own here. */
      /* IL MOTORE SCRIVE LA FRASE. QUI NON SE NE SCRIVE NESSUNA.
         Su 3 dei 43 il motore non ha prosa e porta solo il codice
         REGULATORY_BY_NATURE. Allora si mostra il CODICE tradotto — che e
         ancora roba del motore — e si dichiara che la frase manca. Riempire
         quel vuoto con una frase inventata sarebbe l'unico modo di sbagliare. */
      whyCommercial: whyC.text,
      whyCommercialPointerRemoved: whyC.pointerRemoved,
      whyCommercialCodes: labList(c.WHY_COMMERCIAL_CODES, lang),
      whyCommercialFromCodesOnly: !((lang === 'en' ? c.WHY_COMMERCIAL_EN : c.WHY_COMMERCIAL_IT) || '').trim(),
      proves: lang === 'en' ? (c.WHAT_IT_PROVES_EN || '') : (c.WHAT_IT_PROVES_IT || ''),
      doesNotProve: lang === 'en' ? (c.WHAT_IT_DOES_NOT_PROVE_EN || '') : (c.WHAT_IT_DOES_NOT_PROVE_IT || ''),
      commercialDoesNotProve: lang === 'en' ? (c.COMMERCIAL_DOES_NOT_PROVE_EN || '') : (c.COMMERCIAL_DOES_NOT_PROVE_IT || ''),

      whyNow: whyNowOf(c, lang),
      window: win,
      products: prod,
      actions: actionsOf(c, lang),
      evidence: evidenceOf(c, lang),
      missing: labList(c.WHAT_IS_MISSING, lang),

      needDirectionToken: qual('NEED_DIRECTION', c.NEED_DIRECTION), needDirection: lab(c.NEED_DIRECTION, lang),
      needDocument: c.NEED_EVIDENCE_ID || null,
      needExcerptWithheld: !!c['NEED_EXCERPT__PT_ONLY'],
      /* A pest stage and an action recommendation are DIFFERENT OWNERS. The
         screen carries both and concludes neither from the other: a flight can
         be over while the source still recommends continuing. */
      pestStageCode: c.PEST_STAGE_STATE, pestStage: lab(c.PEST_STAGE_STATE, lang),
      pestStageDocument: c.PEST_STAGE_EVIDENCE_ID || null,
      actionRecCode: c.ACTION_RECOMMENDATION_STATE, actionRec: lab(c.ACTION_RECOMMENDATION_STATE, lang),
      actionRecDocument: c.ACTION_RECOMMENDATION_EVIDENCE_ID || null,
      thresholdCode: c.THRESHOLD_STATE, threshold: lab(c.THRESHOLD_STATE, lang),

      signalDate: c.SIGNAL_DATE || null,
      signalCurrency: lab(c.SIGNAL_CURRENCY, lang),
      confidence: lab(c.CONFIDENCE, lang),
      /* UNA FONTE SI CITA PER NOME, NON PER CHIAVE.
         SRC_FITOSANITARIO_MO_IT e una chiave del registro: a schermo e un
         token sfuggito, non una fonte. Il registro del portale risolve tutte
         e 19 le chiavi dei 43 casi in un nome pubblicato — quello e cio che
         il lettore puo verificare. La chiave resta come identita nel DOM.

             CITARE UNA CHIAVE NON E CITARE UNA FONTE. */
      sources: (c.SOURCE_IDS || []).map((id) => {
        const reg = (window.ITALY_APP_MODEL && window.ITALY_APP_MODEL.collections
          && window.ITALY_APP_MODEL.collections.sources
          && window.ITALY_APP_MODEL.collections.sources.records) || [];
        const hit = reg.find((r) => r.id === id);
        return { id, name: (hit && (hit.name || hit.title)) || null };
      }).filter((r) => r.name),
      sourcesUnnamed: (c.SOURCE_IDS || []).filter((id) => {
        const reg = (window.ITALY_APP_MODEL && window.ITALY_APP_MODEL.collections
          && window.ITALY_APP_MODEL.collections.sources
          && window.ITALY_APP_MODEL.collections.sources.records) || [];
        return !reg.find((r) => r.id === id);
      }).length,
      sourceUrls: (c.SOURCE_URLS || []).slice(),
      evidenceCount: c.EVIDENCE_COUNT || 0,
    };
  }

  /* ── COUNTS · from the 43, and from nothing else ────────────────────── */
  function countsOf(cases) {
    const tally = (f) => cases.reduce((a, c) => { const k = f(c); if (k) a[k] = (a[k] || 0) + 1; return a; }, {});
    const byStatus = tally((c) => c.statusCode);
    /* La finestra viaggia come token qualificato (WINDOW_OPEN_NOW_UNKNOWN):
       contare la parola nuda qui darebbe zero su tutte e tre le righe, ed e
       esattamente cosi che un contatore smette di contare senza dirlo. */
    const byWinOpen = tally((c) => c.window.OPEN_NOW);
    const winOpen = (v) => byWinOpen['WINDOW_OPEN_NOW_' + v] || 0;
    return {
      TOTAL: cases.length,
      PUBLISHABLE: cases.filter((c) => c.publicationCode === 'PUBLISHABLE').length,
      VALIDATION_REQUIRED: cases.filter((c) => c.publicationCode === 'VALIDATION_REQUIRED').length,
      ACT_NOW: byStatus.ACT_NOW || 0,
      VALIDATE_NOW: byStatus.VALIDATE_NOW || 0,
      PREPARE: byStatus.FUTURE_PREPARATION || 0,
      WATCH: byStatus.WATCH || 0,
      TO_VALIDATE: byStatus.TO_VALIDATE || 0,
      WINDOW_DEFINED: cases.filter((c) => c.window.DEFINED === 'YES').length,
      WINDOW_OPEN_NOW_YES: winOpen('YES'),
      WINDOW_OPEN_NOW_NO: winOpen('NO'),
      WINDOW_OPEN_NOW_UNKNOWN: winOpen('UNKNOWN'),
      BY_STATUS: byStatus,
    };
  }

  /* ══ LA FRONTIERA COMMERCIALE ═══════════════════════════════════════════
     Il motore trova CASI. Il cliente compra OPPORTUNITA. Non sono lo stesso
     insieme, e questa tabella e l'unico posto dove uno diventa l'altro.

         MOSTRARE COME LA MACCHINA HA TROVATO IL CASO NON E UN PRODOTTO.

     `COMMERCIAL_PRIORITY` e il verdetto del motore su «regge come opportunita
     commerciale?». I tre valori che reggono ricevono lo stato che il cliente
     legge. Il quarto — TO_VALIDATE — dice che NON regge: quel caso non e
     un'opportunita commerciale, e non viene presentato come tale.

     MISURATO sui 43: SALES_READY 5 · STRATEGIC_OPPORTUNITY 8 ·
     COMMERCIAL_WATCH 13 · TO_VALIDATE 17.

     E I DICIASSETTE NON SPARISCONO. Misurato: nessuno di loro esiste in
     un'altra collezione del modello, e due sono testimoni della riunione
     (Umbria, Toscana). Toglierli dalla vista senza dargli una casa sarebbe
     perderli, non ripulirli — quindi restano raggiungibili come SEGNALI, che
     e quello che sono: letture che non hanno ancora un caso commerciale.

         NASCONDERE NON E CANCELLARE.
         L'INTELLIGENZA RESTA; SMETTIAMO SOLO DI CHIAMARLA OPPORTUNITA. */
  const CLIENT_STATE = {
    SALES_READY: 'CLIENT_ACT_NOW',
    STRATEGIC_OPPORTUNITY: 'CLIENT_PREPARE_NOW',
    COMMERCIAL_WATCH: 'CLIENT_MONITOR',
    /* TO_VALIDATE non e mappato di proposito: senza rilevanza commerciale
       difendibile non c'e stato cliente da dargli. */
  };
  const CLIENT_ORDER = ['CLIENT_ACT_NOW', 'CLIENT_PREPARE_NOW', 'CLIENT_MONITOR'];
  const clientStateOf = (c) => CLIENT_STATE[c.priorityCode] || null;

  /* I conteggi che il cliente vede contano SOLO le opportunita commerciali.
     I numeri del motore restano, ma sotto un'altra chiave: chi ne ha bisogno
     sa dove sono, e nessuna schermata li mostra per sbaglio. */
  function commercialCounts(commercial) {
    const by = commercial.reduce((a, c) => {
      const k = c.clientState; if (k) a[k] = (a[k] || 0) + 1; return a;
    }, {});
    return {
      TOTAL: commercial.length,
      CLIENT_ACT_NOW: by.CLIENT_ACT_NOW || 0,
      CLIENT_PREPARE_NOW: by.CLIENT_PREPARE_NOW || 0,
      CLIENT_MONITOR: by.CLIENT_MONITOR || 0,
      BY_CLIENT_STATE: by,
    };
  }

  window.MEETING_SURFACE = {
    /* Exposed so a gate can prove the boundary on a hand-built deep object
       instead of only on data that happens to be clean today. */
    clientSafe,
    /* Exposed for the same reason, one rule further: `scripts/it_casa_dados.py`
       carries the SAME pointer rule into the package it writes, and a gate
       runs both over all 86 engine sentences and requires identical text.
       Two implementations of one rule diverge; a gate that compares them
       cannot let the divergence travel.

           LA REGOLA E UNA. LE IMPLEMENTAZIONI SONO DUE, E SI CONTROLLANO. */
    dePointer,
    available: () => !!SNAP(),
    build: function (lang) {
      const s = SNAP();
      if (!s) return null;
      const L = lang === 'en' ? 'en' : 'it';
      const cases = (s.CASES || []).map((c) => caseOf(c, L));
      cases.forEach((c) => {
        c.clientState = clientStateOf(c);
        const v = verdictOf(c.id);
        c.relevance = v ? v.CLASSE : 'E';
        c.relevanceSurface = surfaceOf(c.id);
        c.relevanceWhy = lab(v && v.PERCHE, L);
        c.adamaProof = (v && v.PROVA) || null;
      });
      /* QUATTRO INSIEMI DISGIUNTI, E LA LORO SOMMA E SEMPRE 43.
         Niente si cancella: un caso che non regge come opportunita resta
         intero e raggiungibile, sotto il nome che gli spetta. Se un caso
         cadesse fuori da tutti e quattro sarebbe sparito senza che nessuno se
         ne accorgesse — per questo `radar` e `signals` non filtrano per
         esclusione ma per superficie dichiarata, e `error` raccoglie il
         resto. */
      const bySurface = (k) => cases.filter((c) => c.relevanceSurface === k);
      const commercial = bySurface('OPPORTUNITA')
        .sort((a, b) => CLIENT_ORDER.indexOf(a.clientState) - CLIENT_ORDER.indexOf(b.clientState));
      const radar = bySurface('RADAR');
      const signals = bySurface('SEGNALI');
      const errored = bySurface('ERRORE');
      return {
        meta: {
          SOURCE_HEAD: s.SOURCE_HEAD, BUILD_ID: s.BUILD_ID,
          MEETING_CUTOFF: s.MEETING_CUTOFF, TOTAL_CASES: s.TOTAL_CASES,
        },
        /* `counts` resta il conteggio del MOTORE — lo leggono i portoni, non
           lo schermo. `commercialCounts` e quello che il cliente vede. */
        counts: countsOf(cases),
        commercialCounts: commercialCounts(commercial),
        commercial,
        radar,
        signals,
        errored,
        relevance: {
          TOTAL: cases.length,
          OPPORTUNITA: commercial.length,
          RADAR: radar.length,
          SEGNALI: signals.length,
          ERRORE: errored.length,
          /* Le tre invarianti che questa legge esiste per garantire. */
          B_AS_OPPORTUNITY: commercial.filter((c) => c.relevance === 'B').length,
          C_AS_OPPORTUNITY: commercial.filter((c) => c.relevance === 'C').length,
          D_AS_OPPORTUNITY: commercial.filter((c) => c.relevance === 'D').length,
          OWNER: (REL() && REL().DONO_DA_LEI) || null,
        },
        cases,
      };
    },
  };
})();
