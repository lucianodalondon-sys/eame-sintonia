    // ---- archive · sources · news · people
    /* §1 §5 · Four screens, one rule: every row is a record the model normalized from a
       public source. This block reads no fixture at all. It replaces ITALY_DEMO.ARCHIVE (448 rows,
       420 of them procedurally generated in italy-demo-data.js 522-538), ITALY_DEMO.SOURCES (53
       hand-written entries), ITALY_DEMO.NEWS and ITALY_DEMO.PEOPLE with, measured today:
         AM.collections.archive        774 rows · real 774 · demo 0 · 0 duplicate ids
         AM.collections.sources         31 rows · the whole listening registry
         AM.collections.news             8 rows
         AM.collections.researchers     60 · publicPeople 15 · 9 name overlaps -> 66 people
       Synthetic archive rows are 0. Nothing below manufactures a row to keep density. */
    const ARX = A_ARCHIVE0;
    const ARSRC = APP0 ? APP0.sources.records : [];
    const ARNEWS = APP0 ? APP0.news.records : [];
    const ARACT = APP0 ? APP0.competitorActivities.records : [];
    const ARVOX = APP0 ? APP0.voices.records : [];
    const ARSCI = APP0 ? APP0.scienceRecords.records : [];
    const ARL = (itText, enText) => (s.lang === 'en' ? enText : itText);
    /* §NARRATIVE · text only when upstream approved it. Named arcNar because a colleague's
       block already declares `nar` at this scope; re-declaring would be a SyntaxError. */
    const arcNar = (n) => (n && n.state === 'CLEAR') ? (s.lang === 'en' ? (n.en || n.it) : (n.it || n.en)) : null;
    /* ITALY_INGEST does not leave unknown fields empty — it writes Portuguese working
       sentinels into them. Measured on my screens: SOURCES.LATEST_OBSERVATION 'None' x4,
       news REGION 'NAO SEI' 8/8, VOICES.DATE 'NAO SEI' 17/17, RESEARCHERS.FACT_REGION
       'NÃO SEI …' 60/60. A sentinel must become a real absence, never a printed string. */
    const ARSENT = /^\s*(N[ÃA]O[\s_]SEI|N[ÃA]O[\s_]APLICAVEL|N[ÃA]O[\s_]CONSULTADA|NOT[\s_]KNOWN|UNKNOWN|NONE|NULL|N\/?D)\b/i;
    const arcKn = (x) => { const v = x == null ? '' : String(x).trim(); return (!v || ARSENT.test(v)) ? null : v; };

    /* §11 · The nine legacy archive types never existed in the data. The real dimension is
       .kind, measured: COMPETITOR 503, SCIENCE 88, MARKET 77, RESISTANCE 34, WINDOW 29,
       EVENT 18, VOICE 17, NEWS 8. Labels are localized here because en.ARCHTYPES in
       italy-i18n.js is measured to be an empty object and it.ARCHTYPES holds only the nine
       dead legacy keys — arcT() would fall through to the raw token on both languages. */
    const ARC_KIND_L = {
      COMPETITOR: ['Attività di concorrente', 'Competitor activity'],
      SCIENCE: ['Pubblicazione scientifica', 'Scientific publication'],
      MARKET: ['Osservazione di mercato', 'Market observation'],
      RESISTANCE: ['Caso di resistenza', 'Resistance case'],
      WINDOW: ['Finestra colturale attesa', 'Expected crop window'],
      EVENT: ['Evento di settore', 'Trade event'],
      VOICE: ['Voce pubblica', 'Public voice'],
      NEWS: ['Articolo di stampa', 'Press article'],
    };
    const arcKindL = (k) => { const p = ARC_KIND_L[k]; return p ? ARL(p[0], p[1]) : arcT(k); };
    const ARC_DS_L = { RANGE: ['periodo', 'range'], PERIOD: ['periodo', 'period'], UNKNOWN: ['data non nota', 'date unknown'], NOT_OBSERVED: ['senza data', 'no date'] };
    /* §7 · Presentation may read a supplied date; it may not invent one. dateISO parses on
       590 of 774 rows. Of the remaining 184, a leading four-digit year is a fact the source
       itself states (22 RESISTANCE first-case years, all wrapped in Portuguese commentary
       that must not reach the client) — everything else prints its dateState token. */
    const arcYear = (raw) => { const m = /^\s*(1[89]\d\d|20\d\d)\b/.exec(arcKn(raw) || ''); return m ? m[1] : null; };
    const arcDateL = (a) => a.dateISO || arcYear(a.date) || ARL((ARC_DS_L[a.dateState] || ARC_DS_L.UNKNOWN)[0], (ARC_DS_L[a.dateState] || ARC_DS_L.UNKNOWN)[1]);

    /* §11 · RESISTANCE.crop is not a crop key: it is a GIRE field note that carries the
       Portuguese reading note with it — e.g. 'Riso (arroz) — "Sistema colturale: riso."'.
       Measured 34/34 like this, and the model tags them 'UPPER_CODE', which they are not.
       Cut at the reading note, drop the Portuguese gloss in brackets, and refuse anything
       still carrying prose punctuation. What survives is short Italian ('riso', 'uliveto',
       'grano duro e tenero'); what does not survives as nothing. */
    const arcResCrop = (raw) => {
      let v = arcKn(raw); if (!v) return null;
      v = v.split(' — ')[0].split(' - ')[0].replace(/\s*\([^)]*\)/g, ' ').replace(/\s+/g, ' ').trim();
      return (!v || v.length > 30 || /["“.:;]/.test(v)) ? null : v;
    };
    /* §11 · The crop values are five mutually unintelligible vocabularies and must never be
       flattened into one list of crop keys. Measured over the 774 rows after the cut above:
       LATIN 132 (Vitis vinifera, Zea mays …, COMPETITOR), UPPER_CODE 113 (VINE /
       DURUM_WHEAT / MAIS …, SCIENCE+VOICE+NEWS), GENERIC_IT 51 (the advertiser's umbrella
       words: colture 29, cereali 19, frutta 3), IT_SOURCE_TEXT 33 (RESISTANCE), CANONICAL 29
       (English canonical names, WINDOW) — 358 rows with a crop and 416 with none at all.
       Mapping one vocabulary onto another is upstream normalization work, not a view fix. */
    const ARC_VOCAB_L = {
      CANONICAL: ['nome canonico', 'canonical name'], UPPER_CODE: ['codice di pacchetto', 'package code'],
      LATIN: ['nome latino', 'Latin name'], GENERIC_IT: ['termine generico dell’inserzionista', 'advertiser umbrella term'],
      IT_SOURCE_TEXT: ['dicitura della fonte', 'source wording'], UNMAPPED: ['non mappato', 'unmapped'],
    };
    /* Upstream — and only upstream — already canonicalizes some rows: competitorActivities
       .cropsCanonical (132/503) and news.cropCanonical (3/8). WINDOW rows are canonical by
       construction. That is 164 rows whose canonical crop is a declared upstream fact; the
       filter honours those and invents no others. */
    const ARCANON = {};
    ARACT.forEach((a) => { const cc = (a.cropsCanonical || [])[0]; if (cc) ARCANON['COMPETITOR:' + a.id] = cc; });
    ARNEWS.forEach((n) => { if (n.cropCanonical) ARCANON['NEWS:' + n.id] = n.cropCanonical; });

    /* §11 · SCIENCE and VOICE carry SCREAMING_SNAKE issue tokens that T.ISSUES does not hold,
       so il() returned them verbatim ('FLAVESCENCE', 'DOWNY_MILDEW'). The token is localized
       and never sharpened — this mirrors the rule the Voci block already set: FUSARIUM and
       SEPTORIA stay the Latin genus, FLAVESCENCE does not become 'flavescenza dorata', WEED
       does not become one of the named weed programmes. Anything unmapped goes through il()
       untouched. */
    const ARC_ISSUE_TOKEN = { FLAVESCENCE: ['Flavescenza', 'Flavescence'], DOWNY_MILDEW: ['Peronospora', 'Downy mildew'], WEED: ['Infestanti', 'Weeds'], FUSARIUM: ['Fusarium', 'Fusarium'], SEPTORIA: ['Septoria', 'Septoria'], REPILO: ['Repilo', 'Repilo'] };
    const arcIssueL = (k) => { const p = ARC_ISSUE_TOKEN[String(k).toUpperCase()]; return p ? ARL(p[0], p[1]) : il(k); };

    /* §2 §11 · The drawer body. The 420 demo summaries were template prose. What reality has
       is an original public text on two kinds only — competitor ad copy (392/503) and the
       transcript line of a public voice (17/17) — and it is quoted verbatim, never
       translated. SCIENCE, MARKET, EVENT, WINDOW, RESISTANCE and all 8 NEWS rows show
       nothing: news SINTONIA_SUMMARY is measured NOT_APPROVED_FOR_DISPLAY 8/8. */
    const ARQUOTE = {};
    ARACT.forEach((a) => { const t2 = arcKn(a.text) || arcKn(a.textExcerpt); if (t2) ARQUOTE['COMPETITOR:' + a.id] = t2; });
    ARVOX.forEach((v) => { const t2 = arcKn(v.textOriginal); if (t2) ARQUOTE['VOICE:' + v.id] = t2; });

    /* One decoration pass over the whole index, so the filter, the sort, the chips, the
       drawer and the source-detail list all read the same derived values. */
    const arcRows = ARX.map((a) => {
      const isRes = a.kind === 'RESISTANCE';
      const cropRaw = isRes ? arcResCrop(a.crop) : arcKn(a.crop);
      const vocab = cropRaw ? (isRes ? 'IT_SOURCE_TEXT' : (a.cropVocab || 'UNMAPPED')) : null;
      const canon = ARCANON[a.id] || (vocab === 'CANONICAL' ? cropRaw : null);
      /* 49 rows resolve to no registry source: 18 EVENT (no SOURCE_ID upstream), 29 WINDOW
         (SOURCE_IDS measured empty on all 29) and 2 NEWS whose publisher string does not
         match a registry NAME. Each falls back to a real field of its own record — the
         event organizer, the publisher as printed, ITALY_CANONICAL for the norm rows —
         never to a guess and never to a fuzzy name match. */
      const srcLabel = a.sourceName || arcKn(a.publisher) || arcKn(a.organizer) || arcKn(a.authority)
        || (a.kind === 'WINDOW' ? 'ITALY_CANONICAL' : '');
      /* §11 · Five of the 34 RESISTANCE titles append a Portuguese reading note to the
         species after an em dash ('Lolium spp. — a ficha especifica que na Italia duas
         especies…') and one writes its synonym list with a Portuguese connector. The note
         is cut at the em dash and the connector is relabelled; the parenthetical synonym
         list is kept in full, because a taxonomic name is never truncated at '('. Every
         other kind's title is publisher- or author-authored and is left exactly as it is. */
      const title = a.kind === 'RESISTANCE'
        ? String(a.title || '').split(' — ')[0].replace(/\bsinonimi na ficha\s*:/i, 'sinonimi:').trim()
        : a.title;
      return Object.assign({}, a, {
        /* The raw crop is overwritten, not merely shadowed: leaving it on the row would hand
           the GIRE reading note to the template layer even though nothing binds it. */
        title: title, crop: cropRaw,
        cropKey: cropRaw, cropVocabUi: vocab, cropCanon: canon,
        cropLbl: cropRaw ? (vocab === 'CANONICAL' ? cl(cropRaw) : cropRaw) : '',
        issueLbl: arcKn(a.issue) ? arcIssueL(a.issue) : '',
        dateLbl: arcDateL(a), kindL: arcKindL(a.kind), srcLabel: srcLabel,
        quote: ARQUOTE[a.id] || '',
      });
    });

    /* §9 · aRegion is gone from this filter. Measured: 29 of 774 rows can carry a region at
       all (the canonical windows); every other family has either the literal 'NAO SEI', or
       a country, or an ad-reach country the package itself flags
       AD_REACHED_COUNTRY != AD_TARGETED_COUNTRY. Filtering 774 rows by a field 745 of them
       cannot have would read as "no record from Veneto", which is false — it is unknown.
       The <select> at markup 2195 must be deleted; until it is, it selects nothing. */
    const aq = s.archiveQuery.trim().toLowerCase();
    const archAll0 = arcRows.filter(a =>
      (!s.aType || a.kind === s.aType)
      && (!s.aCrop || a.cropKey === s.aCrop || a.cropCanon === s.aCrop)
      && (!s.aCompany || a.company === s.aCompany)
      && (!s.aCase || a.legacyCaseId === s.aCase)
      && (!s.aSource || a.sourceId === s.aSource)
      && (!aq || (a.title + ' ' + (a.cropKey || '') + ' ' + (a.issue || '') + ' ' + (a.company || '') + ' ' + a.srcLabel).toLowerCase().includes(aq)));
    /* §6 §7 · The real index has no sort at all — it is in push order, so the first page was
       twenty science papers. Three bands, all arithmetic over supplied dates against
       AM.REF 2026-09-02 and never new Date(): observed captures first, newest first (554 of
       774); then the rows dated after the reference date, soonest first (36 — expected crop
       windows and scheduled trade events, which are forecasts, not captures); then the 184
       rows with no parseable date, grouped by kind. */
    const ARREF = (AM && AM.referenceDate) || '2026-09-02';
    const arcBand = (a) => !a.dateISO ? 2 : (a.dateISO > ARREF ? 1 : 0);
    const archAll = archAll0.slice().sort((x, y) => {
      const bx = arcBand(x), by = arcBand(y); if (bx !== by) return bx - by;
      if (bx === 0) return x.dateISO < y.dateISO ? 1 : x.dateISO > y.dateISO ? -1 : 0;
      if (bx === 1) return x.dateISO < y.dateISO ? -1 : x.dateISO > y.dateISO ? 1 : 0;
      return (x.ui.order - y.ui.order) || String(x.title).localeCompare(String(y.title));
    });
    const PAGE = 20; const pages = Math.max(1, Math.ceil(archAll.length / PAGE)); const page = Math.min(s.archivePage, pages - 1);

    /* §12 · Same five columns, same drawer, same chips. Only what feeds them changed.
       isDemo / sourceL / sourceRoute / the 'DEMONSTRATION RECORD' label are gone: they
       existed only to mark the 420 fabricated rows, and synthetic rows are now 0. The title
       is no longer split on ' · ' and re-translated either — real titles are publisher- and
       author-authored strings (§11). */
    const archDeco = (a) => Object.assign({}, a, {
      open: () => this.setState({ archiveId: a.id }),
      rowBg: s.archiveId === a.id ? 'rgba(0,152,69,0.10)' : 'transparent',
      typeL: a.kindL, typeColor: a.ui.color, cropL: a.cropLbl, issueL: a.issueLbl,
      date: a.dateLbl, sourceL: a.srcLabel, source: a.srcLabel,
      /* ⚠ NOT A REGION. Markup 2210 and 2312 print '{{ a.cropL }} · {{ a.region }}'; a region
         exists on 29 of 774 rows and nowhere else, so the second half of that subtitle now
         carries the ISSUE label — the substitution the analysis prescribed, made from here
         because the block cannot edit markup. Rename both bindings to a.subtitle and this
         slot goes away. Nothing downstream may read this as a geography. */
      region: a.issueLbl, subtitle: [a.cropLbl, a.issueLbl].filter(Boolean).join(' · '),
      /* CONNECTED TO. The green case link is reserved for the 29 rows that really carry
         LEGACY_CASE_ID; company is a relation, not a convergence, so it stays grey; the
         remaining 242 rows read '—' rather than borrowing a link. */
      linkLabel: a.legacyCaseId || a.company || '—',
      linkColor: a.legacyCaseId ? '#00B152' : (a.company ? '#B1A9A7' : '#8F8886'),
    });
    const visibleArchive = archAll.slice(page * PAGE, page * PAGE + PAGE).map(archDeco);

    /* §12 · Nine chips become the eight kinds that exist, counted off the real index and
       coloured from record.ui (§4 presentation metadata). The old line did
       ITALY_DEMO.ARCHIVE.find(a => a.type === t).typeColor unguarded — a latent throw the moment a
       type had no rows, which 'News article' already did. */
    const archiveTypes = ['COMPETITOR', 'SCIENCE', 'MARKET', 'RESISTANCE', 'WINDOW', 'EVENT', 'VOICE', 'NEWS'];
    const archiveTypeChips = archiveTypes.map(t => {
      const on = s.aType === t; const rows = arcRows.filter(a => a.kind === t);
      return { label: arcKindL(t), count: rows.length, color: (rows[0] && rows[0].ui.color) || '#8F8886',
        bg: on ? 'rgba(0,152,69,0.2)' : 'transparent', border: on ? '#009845' : 'rgba(203,197,195,0.16)',
        go: () => this.setState({ aType: on ? '' : t, archivePage: 0 }) };
    });
    /* Offered to the markup so the crop <select> can stop reading the radar's ten demo crop
       names — against this index those match 29 rows. Grouped by vocabulary so the client
       can see that 'Vitis vinifera' and 'VINE' are two packages talking, not one taxonomy. */
    const archiveCropOptions = [{ v: '', l: ARL('Tutte le colture', 'All crops') }].concat(
      ['CANONICAL', 'UPPER_CODE', 'LATIN', 'GENERIC_IT', 'IT_SOURCE_TEXT', 'UNMAPPED'].reduce((out, vk) => {
        const vals = uniq(arcRows.filter(a => a.cropVocabUi === vk).map(a => a.cropKey));
        const lab = ARC_VOCAB_L[vk] ? ARL(ARC_VOCAB_L[vk][0], ARC_VOCAB_L[vk][1]) : vk;
        return out.concat(vals.map(v => ({ v, l: (vk === 'CANONICAL' ? cl(v) : v) + ' · ' + lab })));
      }, []));
    const archiveCompanyOptions = uniq(arcRows.filter(a => a.company).map(a => a.company)).map(v => ({ name: v }));

    /* §12 · The drawer. Three of the six legacy link kinds are deleted because 0 of 774 rows
       back them: ADAMA PRODUCT (the demo attached one to 116 rows by picking the case's
       primary product), FUTURE SIGNAL (assigned by i % 5 === 4) and RESEARCH TOPIC (a
       ITALY_DEMO.SCI_THEMES lookup through the demo case). What is left is measured: SOURCE 725/774,
       COMPETITOR 503/774, OPPORTUNITY 29/774. */
    const dr0 = arcRows.find(a => a.id === s.archiveId || a.recordId === s.archiveId);
    const dr = dr0 ? Object.assign(archDeco(dr0), {
      typeUpper: String(dr0.kindL || dr0.kind).toUpperCase(),
      dateFull: dr0.dateLbl,
      /* Original public text, quoted, never translated (§11). Empty on 365 of 774 rows and
         that emptiness is the honest answer — the drawer is not redesigned to hide it. */
      summary: dr0.quote ? '« ' + dr0.quote + ' »' : '',
      region: '',
      links: [
        dr0.legacyCaseId && { kind: ARL('OPPORTUNITÀ COLLEGATA', 'RELATED OPPORTUNITY'), label: dr0.legacyCaseId, go: () => this.openCase(dr0.legacyCaseId) },
        dr0.company && { kind: ARL('CONCORRENTE', 'COMPETITOR'), label: dr0.company, go: () => this.openCompany(dr0.company) },
        dr0.sourceId && { kind: ARL('FONTE', 'SOURCE'), label: dr0.sourceName || dr0.sourceId, go: () => this.openSource(dr0.sourceId) }
      ].filter(Boolean)
    }) : null;

    // ---- sources
    /* §8 §12 · The eight legacy group chips included 'EVENTS & TRADE FAIRS', which has no
       real source behind it at all. The registry's own groups are seven, measured: FIELD 10,
       MARKET 6, OFFICIAL 5, RESEARCH 4, TECHNICAL_MEDIA 4, OWN 1, PEOPLE 1. The alias table
       keeps the old deep links working (the future-signal screen still routes to
       'NEWS & TRADE MEDIA', and the sources / people links pass 'PEOPLE'). */
    const SRC_GRP_ALIAS = { 'GOVERNMENT & OFFICIAL': 'OFFICIAL', 'RESEARCH & SCIENCE': 'RESEARCH', 'FIELD & PRODUCER ORGANIZATIONS': 'FIELD', 'NEWS & TRADE MEDIA': 'TECHNICAL_MEDIA', 'COMPANIES & MARKET': 'MARKET', 'EVENTS & TRADE FAIRS': 'ALL', 'ADAMA': 'OWN' };
    const srcGrpKey = SRC_GRP_ALIAS[s.sourceGroup] || s.sourceGroup || 'ALL';
    const SRC_GRP_L = { OFFICIAL: ['ENTI PUBBLICI E UFFICIALI', 'GOVERNMENT & OFFICIAL'], RESEARCH: ['RICERCA E SCIENZA', 'RESEARCH & SCIENCE'], FIELD: ['ORGANIZZAZIONI DI CAMPO', 'FIELD ORGANIZATIONS'], TECHNICAL_MEDIA: ['STAMPA E MEDIA TECNICI', 'TRADE & TECHNICAL MEDIA'], MARKET: ['AZIENDE E MERCATO', 'COMPANIES & MARKET'], OWN: ['CANALE ADAMA', 'ADAMA CHANNEL'], PEOPLE: ['PERSONE', 'PEOPLE'], ALL: ['TUTTE LE FONTI', 'ALL SOURCES'] };
    const sgrpL = (k) => { const p = SRC_GRP_L[k]; return p ? ARL(p[0], p[1]) : k; };
    /* §11 · The 12 TYPE tokens the registry actually uses. An unseen token renders verbatim
       rather than borrowing the meaning of a neighbour. */
    const SRC_TYPE_L = { OFFICIAL: ['Autorità pubblica', 'Public authority'], MARKET: ['Osservatorio di mercato', 'Market observatory'], RESEARCH: ['Base dati di ricerca', 'Research database'], RESEARCH_INSTITUTION: ['Istituto di ricerca', 'Research institution'], TECHNICAL_MEDIA: ['Stampa tecnica', 'Technical press'], FIELD: ['Servizio di campo', 'Field service'], COOPERATIVE: ['Cooperativa', 'Cooperative'], PRODUCER_ORG: ['Organizzazione di produttori', 'Producer organization'], COMPANY: ['Canale aziendale', 'Company channel'], COMPETITOR: ['Canale di concorrente', 'Competitor channel'], PEOPLE: ['Piattaforma di persone', 'People platform'], ADAMA: ['Canale ADAMA', 'ADAMA channel'] };
    const stypeL = (k) => { const p = SRC_TYPE_L[k]; return p ? ARL(p[0], p[1]) : (k || ''); };
    /* ACCESS_STATUS is filled 31/31 and is better than the demo's invented health words.
       Measured GREEN 26 · BLOCKED 3 · PARTIAL 1 · NOT_REACHED 1 — and three of the five
       non-green are the ADAMA, Bayer and Syngenta sites. The screen does not hide that. */
    const SRC_ACC_L = { GREEN: ['Aperta', 'Open', '#00B152'], PARTIAL: ['Parziale', 'Partial', '#F5B317'], BLOCKED: ['Bloccata', 'Blocked', '#D0021B'], NOT_REACHED: ['Non raggiunta', 'Not reached', '#978B87'] };
    /* LATEST_OBSERVATION is present 31/31 but 9 records store a raw Python list literal,
       several truncated mid-token. Only a clean date or year-month reaches the template. */
    const srcLast = (x) => x.latestObservationISO || (/^\d{4}(-\d{2}){0,2}$/.test(String(arcKn(x.latestObservation) || '')) ? arcKn(x.latestObservation) : null);
    /* Only 11 of 31 sources declare a human cadence. 13 say 'DATED' and 3 'NO_DATE_FOUND' —
       crawler status tokens, not frequencies — and 4 are null, so 20 rows read NON
       DICHIARATA. The 20px tile on the detail page was designed for a short word and will
       look empty; that is the honest outcome. */
    /* The 6 declared cadences are written in the package's working Portuguese ('semanal',
       'anual + boletins'). A cadence word is not a product, a company, a Latin name, a
       public quote or a source title, so §11 does not protect it — it is localized. An
       unmapped value renders verbatim rather than being guessed at. */
    const SRC_FREQ_L = { continua: ['continua', 'continuous'], semanal: ['settimanale', 'weekly'], anual: ['annuale', 'annual'], irregular: ['irregolare', 'irregular'], 'anual/mensal': ['annuale / mensile', 'annual / monthly'], 'anual + boletins': ['annuale + bollettini', 'annual + bulletins'] };
    const srcFreq = (x) => {
      if (!(x.frequencyKnown && arcKn(x.frequency))) return ARL('non dichiarata', 'not declared');
      const p = SRC_FREQ_L[String(x.frequency).toLowerCase()];
      return p ? ARL(p[0], p[1]) : x.frequency;
    };
    /* ROLE — the old 'WHAT SINTONIA OBTAINS' column — is a Portuguese Sintonia working note
       on 26 of 31 records (state NOT_APPROVED_FOR_DISPLAY) and NOT_ESTABLISHED on the other
       5. Nothing is rendered for the 26 and 'non noto' for the 5. The column is empty on
       31/31 rows today: the markup should drop it. */
    const srcWhat = (x) => arcNar(x.role) || (x.role && x.role.state === 'NOT_ESTABLISHED' ? ARL('non noto', 'not known') : '');
    /* The archive is the only honest 'related' number a source has. Joined on sourceId, the
       key the model added for exactly this: OpenAlex 88, AgriFood 77, Meta 414, YouTube 106,
       GIRE 34, five publishers 1-2 each — and 20 of 31 sources back zero archive rows. That
       is the true state of the registry: two thirds of it is a listening list. */
    const srcCount = arcRows.reduce((a, r) => { if (r.sourceId) a[r.sourceId] = (a[r.sourceId] || 0) + 1; return a; }, {});
    /* The row is BUILT, not spread. The source record carries roleText, limitationsText and
       raw.* — the Portuguese Sintonia working notes behind the two narrative fields — and a
       spread would hand all of them to the template layer even though no binding prints
       them. Nothing internal leaves this function. */
    const srcDeco = (x) => {
      const acc = SRC_ACC_L[x.accessStatus] || ['—', '—', '#8F8886'];
      return {
        id: x.id || '', sourceId: x.sourceId || '', name: x.name || '', url: x.url || '',
        group: x.group || '', accessStatus: x.accessStatus || '', provenance: x.provenance || '',
        go: () => this.openSource(x.sourceId || x.id),
        groupColor: (x.ui && x.ui.color) || '#8F8886',
        type: stypeL(x.type), what: srcWhat(x), freq: srcFreq(x),
        cov: arcKn(x.geography) || '—',
        last: srcLast(x) || ARL('non disponibile', 'not available'),
        related: srcCount[x.sourceId] || 0,
        health: ARL(acc[0], acc[1]), healthShort: ARL(acc[0], acc[1]), healthColor: acc[2]
      };
    };
    const srcAll = ARSRC.map(srcDeco);
    const sourceGroupChips = ['ALL'].concat((APP0 && APP0.sources.groups ? APP0.sources.groups : []).map(g => g.key)).map(g => {
      const on = srcGrpKey === g;
      return { label: sgrpL(g), color: on ? '#fff' : '#B1A9A7', bg: on ? 'rgba(0,152,69,0.25)' : 'transparent',
        border: on ? '#009845' : 'rgba(177,169,167,0.40)', go: () => this.setState({ sourceGroup: g, peopleCat: 'ALL' }) };
    });
    const isPeople = srcGrpKey === 'PEOPLE';
    const isNews = srcGrpKey === 'TECHNICAL_MEDIA' && s.newsFeed !== false;
    const visibleSources = srcAll.filter(x => srcGrpKey === 'ALL' || x.group === srcGrpKey);

    // ---- news
    /* §3 · The TODAY / LAST 7 DAYS / LAST 30 DAYS chips are deleted, not re-pointed.
       Measured against AM.REF 2026-09-02, the newest real item is 126 days old, the set
       spans -126 to -2016 days, and 1 of 8 has no date at all. All three chips read 0 and
       the default 30-day filter emptied the feed. A recency control over 8 records spanning
       five years cannot be made honest. The array stays declared, empty, so the chip row
       simply renders nothing. */
    const newsPeriodChips = [];
    const NEWS_KIND_L = { EDITORIAL: ['Redazionale', 'Editorial'], COMPANY_PROVIDED: ['Fornito dall’azienda', 'Company provided'], BRANDED_CONTENT: ['Contenuto sponsorizzato', 'Branded content'] };
    /* This one gets BETTER with real data and the badge must be visible, not buried: of the
       8 items, 3 are ADAMA Italia publishing about its own products and 1 is Bayer
       (COMPANY_PROVIDED), 1 is BRANDED_CONTENT, only 3 are EDITORIAL. */
    const newsItems = ARNEWS.slice().sort((x, y) => (y.dateISO || '').localeCompare(x.dateISO || '')).map(n => {
      const kindP = NEWS_KIND_L[n.contentKind];
      return Object.assign({}, n, {
        source: n.publisher || '', title: n.title || '',
        date: n.dateISO || ARL((ARC_DS_L[n.dateState] || ARC_DS_L.UNKNOWN)[0], (ARC_DS_L[n.dateState] || ARC_DS_L.UNKNOWN)[1]),
        /* SINTONIA_SUMMARY is a Portuguese research note on 8/8, state
           NOT_APPROVED_FOR_DISPLAY. Nothing is rendered rather than a paraphrase. */
        summary: arcNar(n.summary) || '',
        cropL: n.cropCanonical ? cl(n.cropCanonical) : (arcKn(n.crop) || ''),
        issueL: arcKn(n.issue) ? il(n.issue) : '',
        /* REGION is the literal 'NAO SEI' on 8/8 records. The chip goes empty. */
        region: '',
        /* 'ORIGINATING SOURCE' has no equivalent; CONTENT_KIND_MEANING answers a different
           question and is not repurposed under the old label. */
        originating: '',
        editorial: kindP ? ARL(kindP[0], kindP[1]) : (n.contentKind || ''),
        /* The old CTA asserted that an article supports an opportunity, a crop window or a
           signal. No field carries that. The link now goes where the article really sits:
           its publisher in the source registry, for the 6 of 8 that resolve. */
        cta: n.publisherSourceId ? ARL('FONTE NEL REGISTRO →', 'SOURCE IN REGISTRY →') : '',
        go: () => n.publisherSourceId && this.openSource(n.publisherSourceId)
      });
    });

    // ---- people
    /* §1 §5 · The directory is 66 real people and it is NOT rebuilt here: it is the science
       block's `people`, which merges AM.collections.researchers (60, from the theme-scoped
       OpenAlex query) with AM.collections.publicPeople (15, each carrying its own
       IDENTITY_EVIDENCE and ROLE_EVIDENCE) on the diacritic-folded name — 9 overlaps
       measured, so 66 records and 65 distinct names. Reading it instead of building a second
       one is what keeps the Science screen and the Sources → People directory naming the
       same humans. What is NOT here: the 7 demo ADAMA Technical Sales Representatives (§1
       keeps internal staff out of the external core; they stay on the labelled Field Sales
       screen) and the 18 seeded 'Demo profile · <role>' records. Directory count goes
       39 -> 66, and 18 of the old 39 did not exist. */
    const arcPeople = people;
    const PPL_CAT_L = { RESEARCHERS: ['RICERCATORI NEI TEMI MONITORATI', 'RESEARCHERS IN MONITORED THEMES'], 'INSTITUTIONAL EXPERTS': ['ESPERTI ISTITUZIONALI', 'INSTITUTIONAL EXPERTS'], 'COMPANY PEOPLE': ['PERSONE DI AZIENDA', 'COMPANY PEOPLE'], 'INFLUENCERS / CREATORS': ['CREATOR', 'CREATORS'], ALL: ['TUTTE LE PERSONE', 'ALL PEOPLE'] };
    const pcatL = (k) => { const p = PPL_CAT_L[k]; return p ? ARL(p[0], p[1]) : k; };
    const PPL_CAT_C = { RESEARCHERS: '#9D1D96', 'INSTITUTIONAL EXPERTS': '#00698F', 'COMPANY PEOPLE': '#978B87', 'INFLUENCERS / CREATORS': '#7DB41E' };
    /* The ORCID join from a person to the papers this package actually holds resolves for
       exactly 1 researcher of 60 (Massimo Blandino, 25 works) — measured against the 88
       scienceRecords. The PUBLICATIONS card is shown for that one and omitted for the other
       59: WORKS_IN_SCOPE is a count, not a list, and must not be dressed as one. */
    const pplOrcid = (o) => String(o || '').replace(/^https?:\/\/orcid\.org\//, '').trim();
    const pplWorks = {};
    ARSCI.forEach((r) => { const o = pplOrcid(r.orcid); if (o) (pplWorks[o] = pplWorks[o] || []).push(r); });
    const pplDeco = (p) => Object.assign({}, p, {
      color: PPL_CAT_C[p.roleCat] || '#978B87',
      /* The demo badge said 'real identity' / 'demo profile'. IDENTITY_STATUS is three-valued
         and measured ORCID_PRESENT_NOT_RESOLVED_HERE 54, NO_ORCID_IN_SOURCE 6 — 'real
         identity' overstated an ORCID nobody resolved. The card shows the state itself; the
         15 evidence-bearing records keep the science block's wording. */
      identityLabel: p.identityStateL || p.identityLabel,
      /* No person record carries a platform: the demo read it from a lookup table keyed on
         the invented role ('LinkedIn · field notes', 'YouTube · Instagram'). */
      platform: '—',
      /* FACT_REGION is the literal 'NÃO SEI — a afiliação é do AUTOR, não do estudo' on
         60/60 researchers, and the source's own LIMITATIONS field says the same thing. */
      regionShort: ARL('non osservabile', 'not observable'),
      /* THEME is the scope of the OpenAlex query, not a declared crop, so it is never
         re-badged as one — it appears only where the label says 'tema monitorato'.
         crops [] and issues [] are measured empty on 60/60. */
      cropLabel: '—', issueLabel: '—',
      recentTopic: p.themeLabel ? (ARL('tema monitorato: ', 'monitored theme: ') + p.themeLabel + (p.worksInScope != null ? ' · ' + p.worksInScope + ARL(' opere nel recorte', ' works in scope') : '')) : '',
      /* Person→opportunity and person→signal edges do not exist anywhere upstream; the demo
         built them with CASES.filter(x => x.crop === r.crop). '—', not 0 — the absence of an
         edge in this package is not a measured zero. */
      relatedCount: '—', signalCount: '—', related: [], signals: [],
      /* LAST_ACTIVITY is the date of the last indexed work in the monitored theme, not an
         observation of the person, and it is old: 31 of 60 fall more than 24 months before
         AM.REF 2026-09-02. The list is not filtered to hide that. */
      last: p.lastActivity || ARL('non noto', 'not known'),
      go: () => this.openPerson(p.id)
    });
    /* Five of the nine legacy chips had zero real members — agronomists / engineers,
       technical advisors, field experts, producer voices, and the ADAMA sales reps. The real
       CATEGORY values are four: RESEARCHER 62, INSTITUTIONAL_EXPERT 2, COMPANY_PERSON 1,
       CREATOR 1. A peopleCat with no member (an old deep link into the sales-rep category)
       shows an empty directory rather than silently falling back to everybody. */
    const pplCats = ['ALL'].concat(uniq(arcPeople.map(p => p.roleCat)));
    const pplCatKey = s.peopleCat || 'ALL';
    const peopleCatChips = pplCats.map(c => {
      const on = pplCatKey === c;
      return { label: pcatL(c), count: c === 'ALL' ? arcPeople.length : arcPeople.filter(p => p.roleCat === c).length,
        color: on ? '#fff' : '#B1A9A7', bg: on ? 'rgba(0,152,69,0.25)' : 'transparent',
        border: on ? '#009845' : 'rgba(203,197,195,0.2)', go: () => this.setState({ peopleCat: c }) };
    });
    const visiblePeople = arcPeople.filter(p => pplCatKey === 'ALL' || p.roleCat === pplCatKey).map(pplDeco);

    /* §8 · The KPI strip counted the demo registry: 53 organizations, 39 people (7 of them
       invented ADAMA reps). It now counts the real one — 31 sources, 66 people — through
       the head block's K, which reads AM.collections. The first tile also carries the
       access state, because 5 of the 31 routes are not fully open and 3 of those 5 are
       competitor or ADAMA sites. */
    const sourceKpis = [
      { count: K.orgs, label: ARL('Fonti monitorate · ' + K.routesOpen + ' rotte aperte, ' + K.routesBlocked + ' limitate', 'Sources monitored · ' + K.routesOpen + ' open routes, ' + K.routesBlocked + ' restricted'), color: '#fff', go: () => this.setState({ sourceGroup: 'ALL' }) },
      { count: arcPeople.length, label: ARL('Persone identificate pubblicamente', 'Publicly identified people'), color: '#009845', go: () => this.setState({ sourceGroup: 'PEOPLE' }) },
      { count: K.official, label: ARL('Rotte pubbliche e ufficiali', 'Official / government routes'), color: '#978B87', go: () => this.setState({ sourceGroup: 'OFFICIAL' }) },
      { count: K.research, label: ARL('Ricerca e basi dati scientifiche', 'Research institutions & databases'), color: '#978B87', go: () => this.setState({ sourceGroup: 'RESEARCH' }) },
      { count: K.field, label: ARL('Organizzazioni di campo e produttori', 'Field & producer organizations'), color: '#978B87', go: () => this.setState({ sourceGroup: 'FIELD' }) },
      { count: K.media, label: ARL('Stampa tecnica · ' + K.news + ' articoli reali', 'Trade & technical media · ' + K.news + ' real items'), color: '#009845', go: () => this.setState({ sourceGroup: 'TECHNICAL_MEDIA' }) },
      { count: K.market, label: ARL('Canali di mercato e concorrenti', 'Market / competitor channels'), color: '#978B87', go: () => this.setState({ sourceGroup: 'MARKET' }) }
    ];

    /* §12 · Source detail. CROPS / TOPICS is empty: there is no crop or topic field on the
       registry in any form — it was a pure fixture invention, and it was load-bearing.
       RELATED OPPORTUNITIES is empty too: the only real reverse link names 3 sources, and
       the demo built the rest from cov + topics against demo cases. LATEST CAPTURES, on the
       other hand, is now real — the model gave the archive a sourceId, so the join is an
       id join and not a name match. */
    /* A lookup that misses must not open a different record. The old line ended in
       `|| ITALY_DEMO.SOURCES[0]`, so a stale or wrong sourceId quietly put another
       institution's masthead over this page. An id that does not resolve now says so. */
    const srHit = ARSRC.filter(x => x.sourceId === s.sourceId || x.id === s.sourceId)[0];
    const sr0 = srHit || (s.sourceId ? {} : (ARSRC[0] || {}));
    const srItems = sr0.sourceId ? arcRows.filter(a => a.sourceId && a.sourceId === sr0.sourceId) : [];
    const sr = Object.assign(srcDeco(sr0), {
      name: sr0.name || ARL('Fonte non trovata nel registro', 'Source not found in the registry'),
      group: sgrpL(sr0.group) || '', topics: [], cases: [],
      itemCount: srItems.length,
      items: srItems.slice()
        .sort((x, y) => (y.dateISO || '').localeCompare(x.dateISO || ''))
        .slice(0, 8)
        .map(a => Object.assign(archDeco(a), { open: () => this.archiveWith({ aSource: sr0.sourceId, archiveId: a.id }) })),
      goArchive: () => this.archiveWith({ aSource: sr0.sourceId })
    });

    /* §12 · Person detail. The five-row 'SOURCE HISTORY' is deleted: it generated five dates
       and five sentences out of one integer (lastDays + k * 9 days, against ITALY_DEMO.TODAY, which
       also broke §6). There is exactly ONE real temporal fact about a person — LAST_ACTIVITY
       — and it is already on the header tile. */
    /* Same rule as the source page: a personId that does not resolve does not open somebody
       else's page. Identity is never upgraded and never swapped. */
    const prMiss = { id: '', name: '', label: ARL('Persona non trovata', 'Person not found'), initials: '?', roleCat: '', org: '', identityLabel: '', crops: [], issues: [], related: [], signals: [], messages: [] };
    const prHit = arcPeople.filter(p => p.id === s.personId)[0];
    const pr0 = prHit || (s.personId ? prMiss : (arcPeople[0] || prMiss));
    const prWorks = pplWorks[pplOrcid(pr0.orcid)] || [];
    const pr = Object.assign(pplDeco(pr0), {
      roleCatLabel: pcatL(pr0.roleCat),
      region: ARL('regione non osservabile da fonti esterne', 'region not observable from external sources'),
      /* The publications card is shown only when the ORCID really resolves into this
         package — 1 person of 60. isTsr is permanently false: the Technical Sales
         Representatives are a Field Sales demonstration and never enter this directory. */
      isResearcher: prWorks.length > 0, isTsr: false, messages: [],
      crops: pr0.themeLabel ? [ARL('tema monitorato · ', 'monitored theme · ') + pr0.themeLabel] : [],
      issues: [],
      theme: null, themeTitle: String(pr0.themeLabel || '').toUpperCase(),
      themeRecords: prWorks.slice(0, 4).map(r => ({ year: r.year || '—', descriptor: r.title, institution: r.institution || '', note: r.venue || '' })),
      goTheme: () => {},
      history: []
    });

    // ---- search
    const sgp = (label, color, items) => ({ label, color, count: items.length, items: items.slice(0, 6), empty: items.length === 0 });
