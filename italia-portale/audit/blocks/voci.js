    /* §12 · Voci dal Campo — public external human intelligence, distinct from Field Sales.
       Zero RTV / Field Sales demo records reach this screen: the only source is
       AM.collections.voices (ITALY_INGEST.VOICES, measured 17 records, 17 real, 0 demo,
       provenance REAL_SOURCE, 0 rejected). */
    /* §11 §12 · Every helper below is declared INSIDE the `if (AM)` block on purpose.
       A colleague's block already declares `nar` at renderVals top level; re-declaring it
       here at the same scope would be a SyntaxError, so this block shadows instead. */
    let voices = null;
    if (AM) {
      const C = AM.collections.voices;

      /* §2 · The narrative gate. WHAT_IT_PROVES / WHAT_IT_DOES_NOT_PROVE are Portuguese
         Sintonia research notes on 17/17 records — measured state NOT_APPROVED_FOR_DISPLAY
         17/17 for both fields. The old code did `v.proves || ''`, and a narrative object is
         truthy, so every card printed the string "[object Object]" twice. nar() returns text
         only on state CLEAR, which is 0/17 today and will start working the day upstream
         supplies approved *_IT / *_EN prose. */
      const nar = (n) => (n && n.state === 'CLEAR') ? (s.lang === 'en' ? (n.en || n.it) : (n.it || n.en)) : null;

      /* §3 · ITALY_INGEST.VOICES does not leave unknown fields empty — it writes the
         Portuguese working sentinel "NAO SEI" into them. Measured across the 17 records:
         ROLE 17/17 "NAO SEI", ORGANIZATION 17/17 "NAO SEI", REGION 17/17 "NAO SEI",
         DATE 17/17 "NAO SEI", COUNTRY_OF_FACT NOT_KNOWN 15/17. AM's `S()` passes those
         strings through untouched (only narrative() applies UNKNOWN_SENTINEL), so the old
         block rendered "NAO SEI · NAO SEI" as the role line and "NAO SEI" as the region and
         the date on all 17 cards. kn() is the scrubber: a sentinel becomes a real absence. */
      const SENTINEL = /^\s*(N[ÃA]O[\s_]SEI|NOT[\s_]KNOWN|UNKNOWN|N\/?D|NAO[\s_]ATRIBUIVEL)\b/i;
      const kn = (x) => { const t = x == null ? '' : String(x).trim(); return (!t || SENTINEL.test(t)) ? null : t; };

      /* §11 · SCREAMING_SNAKE canonical tokens localized for display only. The crop map is a
         copy of CROP_BY_TOKEN (italy-app-model.js:409-415), which the model builds for exactly
         this vocabulary — "crop tokens used by SCIENCE / VOICES / THEMES" — but does not export;
         it is duplicated here rather than guessed, and should move onto AM. Only the three
         tokens the data actually carries are mapped (VINE 8, MAIZE 8, DURUM_WHEAT 1). The
         issue map translates the token and never sharpens it: FUSARIUM stays the Latin genus
         (§11), FLAVESCENCE does not become "flavescenza dorata", WEED does not become one of
         the specific weed programmes in T.ISSUES. Unmapped tokens render verbatim. */
      const CROP_TOKEN = { VINE: 'Grapevine', GRAPEVINE: 'Grapevine', VITE: 'Grapevine', MAIZE: 'Maize', MAIS: 'Maize', DURUM_WHEAT: 'Durum Wheat', COMMON_WHEAT: 'Wheat', WHEAT: 'Wheat', OLIVE: 'Olive', OLIVO: 'Olive', TOMATO: 'Tomato', RICE: 'Rice', APPLE: 'Apple', SUGARBEET: 'Sugar Beet', SOYBEAN: 'Soybean', BARLEY: 'Barley' };
      const ISSUE_TOKEN = { WEED: { it: 'Infestanti', en: 'Weeds' }, FLAVESCENCE: { it: 'Flavescenza', en: 'Flavescence' }, FUSARIUM: { it: 'Fusarium', en: 'Fusarium' } };
      const cropL = (tok) => { const t = kn(tok); if (!t) return null; return cl(CROP_TOKEN[t] || t); };
      const issueL = (tok) => { const t = kn(tok); if (!t) return null; const viaI18n = il(t); if (viaI18n !== t) return viaI18n; const m = ISSUE_TOKEN[t]; return m ? (s.lang === 'en' ? m.en : m.it) : t; };

      /* §6 §7 · There is no absolute date to work with: DATE is the sentinel on 17/17, so
         AM.daysFrom() returns null on 17/17 and AM.REF cannot position these records. The only
         temporal evidence is YouTube's own relative stamp (DATE_RELATIVE, 17/17 present),
         anchored to the crawl and not to the reference date — hence the "≈" and never a
         computed calendar date. That stamp is the single reason the reader can tell this
         newsroom is not current: measured spread is 1 year (2 records) to 13 years (1 record),
         with 6-7 years old being the mode (7 of 17). Hiding it would be the bigger lie. */
      const UNITS = { year: 365, month: 30, week: 7, day: 1, hour: 1 / 24, minute: 1 / 1440, second: 1 / 86400 };
      const IT_UNIT = { year: ['anno', 'anni'], month: ['mese', 'mesi'], week: ['settimana', 'settimane'], day: ['giorno', 'giorni'], hour: ['ora', 'ore'], minute: ['minuto', 'minuti'], second: ['secondo', 'secondi'] };
      const ageOf = (rel) => {
        const raw = kn(rel);
        if (!raw) return { days: Infinity, label: null, edited: false };
        const edited = /\(edited\)/i.test(raw);
        const m = /(\d+)\s*(year|month|week|day|hour|minute|second)s?\s*ago/i.exec(raw);
        if (!m) return { days: Infinity, label: null, edited: edited };
        const n = parseInt(m[1], 10), unit = m[2].toLowerCase();
        const word = s.lang === 'en' ? (unit + (n === 1 ? '' : 's')) : IT_UNIT[unit][n === 1 ? 0 : 1];
        return { days: n * UNITS[unit], edited: edited, label: s.lang === 'en' ? ('≈ ' + n + ' ' + word + ' ago') : ('≈ ' + n + ' ' + word + ' fa') };
      };
      const dateUnknown = s.lang === 'en' ? 'date not known' : 'data non nota';

      const decoV = (v) => {
        const age = ageOf(v.dateRelative);
        const chan = kn(v.channel);
        /* §12 · ROLE is absent 17/17, so the green line under the handle cannot state a role.
           It states where the sentence was published instead — CHANNEL is real 17/17 — and the
           explicit CANALE / CHANNEL prefix stops a channel name reading as an employer. */
        const roleLine = [kn(v.role), kn(v.organization)].filter(Boolean).join(' · ')
          || (chan ? ((s.lang === 'en' ? 'CHANNEL' : 'CANALE') + ' · ' + chan) : T.vociRoleUnknown);
        /* §2 · nar() first, so approved per-record prose wins the moment it exists. Until then
           the two localized standing caveats already shipped in italy-i18n.js carry the row:
           vociProvesDefault is exactly what a linked public quote proves (SOURCE_URL 17/17),
           and vociNotProvesDefault is the disclaimer this collection most needs, given
           PERSON_IDENTITY_STATE is "not attributable" 17/17 and REGION is unknown 17/17.
           They are collection-level rules, identical on every card — not a per-record finding. */
        const proves = nar(v.proves), notProves = nar(v.notProves);
        return {
          id: v.id,
          /* §11 §12 · The handle is the identity as published and is never upgraded to a name. */
          person: kn(v.person) || chan || T.vociUnknownPerson,
          /* PERSON_IDENTITY_STATE arrives as "NAO_ATRIBUIVEL — handle publico pseudonimizado"
             on 17/17. Only the enum token is carried forward; the Portuguese gloss after the
             em dash is dropped so it cannot leak into any props dump, and no markup binds it
             today anyway. The identity itself is not upgraded: `person` stays the handle. */
          identityState: String(v.identityState || '').split('—')[0].trim(),
          role: kn(v.role) || '', roleLine: roleLine,
          platform: kn(v.platform) === 'YOUTUBE' ? 'YouTube' : (kn(v.platform) || '—'),
          channel: chan || '', hasChannel: !!chan,
          /* §11 · The video title is an official public source title: verbatim, never translated. */
          title: kn(v.title) || '',
          date: age.label || dateUnknown, hasExactDate: false, edited: age.edited, ageDays: age.days,
          crop: cropL(v.crop), hasCrop: !!cropL(v.crop), cropToken: kn(v.crop) || '',
          issue: issueL(v.issue), hasIssue: !!issueL(v.issue), issueToken: kn(v.issue) || '',
          /* §3 §9 · REGION is the sentinel 17/17 and COUNTRY_OF_FACT is NOT_KNOWN on 15/17, so
             no record here may be rendered as observed in a named Italian region. */
          region: T.vociRegionNotStated, hasRegion: false,
          /* §11 · The original public quote, as published, never translated, never parsed. */
          text: kn(v.textOriginal) || '', hasText: !!kn(v.textOriginal),
          proves: proves || T.vociProvesDefault, provesStanding: !proves,
          notProves: notProves || T.vociNotProvesDefault, notProvesStanding: !notProves,
          hasProves: true, hasNotProves: true,
          url: kn(v.sourceUrl) || '', hasUrl: !!kn(v.sourceUrl),
          sourceId: kn(v.sourceId) || '', kind: kn(v.kind) || '',
          firstPerson: v.kind === 'FIRST_PERSON_FIELD_REPORT',
          /* Measured 7/17: the commenting handle IS the channel's own account, i.e. the
             publisher replying under its own video, not an independent grower. */
          isChannelOwner: !!chan && String(v.person || '').toLowerCase().replace(/[^a-z0-9]/g, '') === chan.toLowerCase().replace(/[^a-z0-9]/g, ''),
          provenance: v.provenance || C.provenance,
        };
        /* CASE_ID is deliberately not exported. It is present 17/17 but its three values
           (IT-VINE-FLAVESCENCE, IT-MAIZE-WEED, IT-DURUM_WHEAT-FUSARIUM) are composite crop+issue
           keys; measured against AM.collections.opportunities they resolve 0/17. The old block's
           caseGo/hasCase would have routed the reader to an opportunity that does not exist. */
      };

      const all = C.records.map(decoV).sort((a, b) => a.ageDays - b.ageDays);

      /* §7 · The band split is an ordering over real fields, not an editorial verdict: the two
         most recent voices that are first-person field reports AND not the channel's own
         account. Today that is IT-VOICE-001 (≈1 anno) and IT-VOICE-003 (≈2 anni). Nothing in
         VOICES says "featured", so if the product owner wants that claim gone, set
         hasFeatured:false and put all 17 in `latest` — one line, no markup change. */
      const feat = all.filter(v => v.firstPerson && !v.isChannelOwner).slice(0, 2);
      const featIds = {}; feat.forEach(v => { featIds[v.id] = 1; });
      const rest = all.filter(v => !featIds[v.id]);

      /* Themes = counts of the canonical ISSUE token, over records that really carry one.
         Measured and reconciling to 17: FLAVESCENCE 8, WEED 8, FUSARIUM 1. */
      const themes = {};
      C.records.forEach(v => { const k = kn(v.issue) || kn(v.crop); if (k) themes[k] = (themes[k] || 0) + 1; });
      voices = {
        provenance: C.provenance, count: C.count, real: C.real, demo: C.demo,
        featured: feat, latest: rest,
        hasFeatured: feat.length > 0, hasLatest: rest.length > 0,
        themes: Object.keys(themes).sort((a, b) => themes[b] - themes[a]).slice(0, 6)
          .map(k => ({ label: issueL(k) || cropL(k) || k, n: themes[k] })),
        firstPersonCount: all.filter(v => v.firstPerson).length,
        channelOwnerCount: all.filter(v => v.isChannelOwner).length,
        datedCount: all.filter(v => v.ageDays !== Infinity).length,
        none: all.length === 0
      };
    }
