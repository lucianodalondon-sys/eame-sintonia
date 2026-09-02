## head  (portale.html 2776-2825, 50 lines) — §3 · ITALY_APP_MODEL is now the only place this block takes a fact from
MUST STILL DEFINE (later blocks read these): D, ITX, L, LAGO, LDAYS, LMORE, T, arcT, cl, dst, fst, il, obs, p, s, srcL, wst
MAY READ FROM EARLIER BLOCKS: (nothing)

## narrative  (portale.html 2826-2865, 40 lines) — §THE NARRATIVE RULE
MUST STILL DEFINE (later blocks read these): APPWIN_LAB, EITHER, REAL_OPPS, agoLbl, d, daysAgo, narOf
MAY READ FROM EARLIER BLOCKS: ITX, L, LAGO, LDAYS, LMORE, s

## pest  (portale.html 2866-2881, 16 lines) — §4 · the pest/disease/weed tile is decorate()'s job
MUST STILL DEFINE (later blocks read these): appwin, p
MAY READ FROM EARLIER BLOCKS: APPWIN_LAB, EITHER, T, p, s

## products+window+evidence  (portale.html 2882-2954, 73 lines) — §10 · an empty ADAMA_PRODUCTS is NOT "ADAMA has no product"
MUST STILL DEFINE (later blocks read these): A_OPPREAL, fresh, prods, w
MAY READ FROM EARLIER BLOCKS: EITHER, REAL_OPPS, agoLbl, appwin, d, daysAgo, narOf, s

## legacy  (portale.html 2955-2961, 7 lines) — §5 · the 29 legacy presentation cases
MUST STILL DEFINE (later blocks read these): A_OPPSCEN
MAY READ FROM EARLIER BLOCKS: A_OPPREAL, s

## live  (portale.html 2962-2965, 4 lines) — §19 · Live switch
MUST STILL DEFINE (later blocks read these): CASES
MAY READ FROM EARLIER BLOCKS: A_OPPREAL, A_OPPSCEN

## lang  (portale.html 2966-3089, 124 lines) — §27 · The switch set <html lang>
MUST STILL DEFINE (later blocks read these): dataState, dataStateTotals, k, langBtns, note, opts, out, q, uniq
MAY READ FROM EARLIER BLOCKS: EITHER, ITX, T, s

## radarfilter  (portale.html 3090-3159, 70 lines) — ---- radar filtering
MUST STILL DEFINE (later blocks read these): ACTS_DATED, ACT_UNDATED, CA, LV, OPPC, REL, SRC_ACCESS, SRC_GROUP, WIN_REGION, WIN_STATUS, actAge, candL, cnt, filtered, hasFilters, match, oppMayBeCalled, oppSafeDeclared, oppSafeN, recentN, recs, relBy, tally, v, visibleCases
MAY READ FROM EARLIER BLOCKS: CASES, T, d, daysAgo, k, q, s

## reach  (portale.html 3160-3333, 174 lines) — §9 · REACHED_IN_ITALY (414) and the 89 multi-country
MUST STILL DEFINE (later blocks read these): ICO, K, REGION_GRID, goWindows, kpis, n, o, regionTiles
MAY READ FROM EARLIER BLOCKS: ACT_UNDATED, CA, CASES, D, EITHER, LV, OPPC, REL, SRC_ACCESS, SRC_GROUP, T, WIN_REGION, WIN_STATUS, candL, cnt, filtered, il, k, narOf, oppMayBeCalled, oppSafeDeclared, oppSafeN, recentN, relBy, s, tally, wst

## marketpanel  (portale.html 3334-3351, 18 lines) — §8 · the panel publishes its own denominator
MUST STILL DEFINE (later blocks read these): CH, initials, regionRank, regionRankNote
MAY READ FROM EARLIER BLOCKS: T, n, regionTiles, w

## markettemp  (portale.html 3352-3371, 20 lines) — §8/§13 · market "temperature" was an editorial fixture
MUST STILL DEFINE (later blocks read these): EVBY, NOT_ASSESSED, TIMING, absenceRule, noMatchLab, noWindowLead, notEnough
MAY READ FROM EARLIER BLOCKS: EITHER, T, recs, s

## competitor  (portale.html 3372-3432, 61 lines) — §9 · REACHED_IN_ITALY (414) is not the same claim
MUST STILL DEFINE (later blocks read these): actDeco, age, ch, ev, hasDate, reached
MAY READ FROM EARLIER BLOCKS: CH, EITHER, EVBY, NOT_ASSESSED, T, TIMING, absenceRule, actAge, agoLbl, cl, il, initials, n, noMatchLab, noWindowLead, notEnough, o, s

## navgroup  (portale.html 3433-3480, 48 lines) — §1 · Core = external intelligence
MUST STILL DEFINE (later blocks read these): allMessages, recentActivity
MAY READ FROM EARLIER BLOCKS: ACTS_DATED, actAge, actDeco, s

## sources  (portale.html 3481-3506, 26 lines) — §8 · 'sources' counts monitored public routes only
MUST STILL DEFINE (later blocks read these): navDef
MAY READ FROM EARLIER BLOCKS: T, k, s

## navbadges  (portale.html 3507-3507, 1 lines) — const navIntegrations = 
MUST STILL DEFINE (later blocks read these): navIntegrations
MAY READ FROM EARLIER BLOCKS: T, allMessages

## accents  (portale.html 3508-3510, 3 lines) — §4 · The green/amber accents
MUST STILL DEFINE (later blocks read these): activeOf, nav, on
MAY READ FROM EARLIER BLOCKS: n, navDef, s

## detail  (portale.html 3511-3548, 38 lines) — §2 · The detail must open the SAME entity the card opened
MUST STILL DEFINE (later blocks read these): csLK, csRec, csScen, csUIK, navIntegrationItems, on
MAY READ FROM EARLIER BLOCKS: K, activeOf, candL, n, narOf, navIntegrations, o, on, s

## opportunity  (portale.html 3549-3600, 52 lines) — §11 · The upstream opportunity feed was researched in Portuguese
MUST STILL DEFINE (later blocks read these): CS_ENUM, csFold, csSafe, csT, x
MAY READ FROM EARLIER BLOCKS: K, L, T, d, k, n, o, on, p, s, v

## crops  (portale.html 3601-3627, 27 lines) — §11 · Six crop vocabularies are measured
MUST STILL DEFINE (later blocks read these): csCropOf, csDate, csEnum, csIssueOf, d, e, raw, t
MAY READ FROM EARLIER BLOCKS: CS_ENUM, T, csFold, csLK, d, s, v, x

## canonwindow  (portale.html 3628-3659, 32 lines) — §13 · The canonical window is a DECLARED relation
MUST STILL DEFINE (later blocks read these): csCropK, csCropTxt, csDay, csIdent, csIssueK, csIssueTxt, csWinRec, d, w
MAY READ FROM EARLIER BLOCKS: T, cl, csCropOf, csFold, csIssueOf, csRec, csSafe, csScen, csT, d, e, il, match, on, s, w, x

## category  (portale.html 3660-3672, 13 lines) — §4 · Category tint
MUST STILL DEFINE (later blocks read these): csCatKey, csRegion, csUI
MAY READ FROM EARLIER BLOCKS: csRec, csSafe, csUIK, csWinRec, s

## days  (portale.html 3673-3682, 10 lines) — §7 · Days remaining, bar width and ordering
MUST STILL DEFINE (later blocks read these): csCat, csD0, csSpan, csStTok, csStatus
MAY READ FROM EARLIER BLOCKS: csUI, csUIK, csWinRec, s

## adama  (portale.html 3683-3758, 76 lines) — §10 · Two real sources, in this order
MUST STILL DEFINE (later blocks read these): cs0, csAlts, csDoc, csEvN, csFresh, csKnowN, csNamed, csObsDate, csPct, csPrimary, csProds, csSciTxt, csSrcRows, csWatchN, moa, p, v
MAY READ FROM EARLIER BLOCKS: REGION_GRID, T, csCat, csCropK, csD0, csDay, csEnum, csFold, csIssueK, csRec, csRegion, csSafe, csScen, csSpan, csStTok, csStatus, csT, csUIK, csWinRec, match, n, on, p, raw, s, srcL, v, x

## convergence+absence+brief+rows  (portale.html 3759-4257, 499 lines) — §2 · The five-bar convergence chart
MUST STILL DEFINE (later blocks read these): CAL_TODAY, COV_LAB, CW_DEPTS, CW_INTERP, LC, START, a, accent, actStateL, adamaLabel, addD, bars, best, calCatColor, calClearBucket, calCropBtns, calEmptyCta, calEmptyGo, calEmptyText, calFilterLabel, calFootNote, calHorizons, calKpiNote, calKpis, calMarket, calModes, calMoments, calMonths, calNav, calRangeLabel, calRows, calSeason, calStrip, calWins, calYearMarks, cov, cs, deptName, dw0, dwC, dwSrc, dwW, first, ink, l, n, on, out, prepLineOf, pst, r, reasonL, regLine, sub, todayInView, todayLeft, y
MAY READ FROM EARLIER BLOCKS: D, L, REGION_GRID, T, absenceRule, age, cl, cs0, csAlts, csCat, csCatKey, csCropK, csCropTxt, csD0, csDate, csDoc, csEnum, csEvN, csFresh, csIdent, csIssueK, csIssueTxt, csKnowN, csNamed, csObsDate, csPct, csPrimary, csProds, csRec, csRegion, csSafe, csScen, csSciTxt, csSrcRows, csStTok, csStatus, csT, csUIK, csWatchN, csWinRec, d, dst, e, il, k, match, moa, n, o, obs, on, out, p, s, t, v, w, wst, x

## windowscreen  (portale.html 4258-4537, 280 lines) — §9 · Every window on this screen is now AM.collections.cropWindows
MUST STILL DEFINE (later blocks read these): WK, d, dw, e, moa, on, p, pstate, reached, reg, rows, w, wd, winFor, windowBuckets, windowCropChips, wins
MAY READ FROM EARLIER BLOCKS: CAL_TODAY, COV_LAB, CW_DEPTS, CW_INTERP, D, LC, START, T, a, absenceRule, actStateL, addD, calWins, cl, cs, cs0, d, deptName, dst, dw0, dwC, dwSrc, dwW, e, filtered, first, il, k, l, match, moa, n, note, o, on, out, p, prepLineOf, prods, pst, raw, reached, reasonL, s, sub, t, uniq, v, w, wst, x, y

## futurecard  (portale.html 4538-4571, 34 lines) — §18 · A real Future card opens the SAME real entity
MUST STILL DEFINE (later blocks read these): earlyWindows, ev, narState, sg0, sgIsScenario, sgMissing, sgNar, sgSourceRecords, sgSources, sgTrail, srcGo, srcTint, was
MAY READ FROM EARLIER BLOCKS: T, a, ev, n, note, on, raw, s, x

## major7+marketpulse  (portale.html 4572-4692, 121 lines) — §3 · MAJOR 7 · This screen was written against
MUST STILL DEFINE (later blocks read these): F, MK, MK_BY, MK_CROPS, MK_FRESH, MK_LINKS, MK_OBS, MK_SRC, MK_SUMS, MK_TOK, e, held, mkDay, mkFreq, mkIT, mkNotIngested, mkNum, mkPct, mkSpan, mp, on, sg
MAY READ FROM EARLIER BLOCKS: T, a, cl, e, il, k, narState, on, p, r, rows, s, sg0, sgIsScenario, sgNar, sgSourceRecords, sgSources, sgTrail, srcGo, srcTint, t, v, was, x, y

## portfoliopanel+convergencelabel+marketgaps+signaljoin+industry  (portale.html 4693-4957, 265 lines) — §M · The portfolio panel used to list demo case products
MUST STILL DEFINE (later blocks read these): EMPTY, N, a, ageOf, d, g, k, keys, live, max, on, other, rank, ref, rows, srcFreq, tiles, tok, why
MAY READ FROM EARLIER BLOCKS: MK, MK_BY, MK_CROPS, MK_FRESH, MK_LINKS, MK_OBS, MK_SRC, MK_SUMS, MK_TOK, T, a, bars, best, cnt, d, e, first, fresh, il, k, l, match, mkDay, mkFreq, mkIT, mkNotIngested, mkNum, mkPct, mkSpan, mp, n, note, o, on, p, r, rows, s, t, v, w, was, wins, wst, x, y

## productintel  (portale.html 4958-5349, 392 lines) — §4 · ADAMA Product Intelligence — TWO UNIVERSES OVER ONE NAME
MUST STILL DEFINE (later blocks read these): PIT, RES, a, aiTxt, cpMarketObj, e, ev, evidence, hit, iso, k, moaNote, n, none, parts, pd, rejected, related, row, sp, stopped, table, uniLaw, v, verified, wins, x
MAY READ FROM EARLIER BLOCKS: D, MK_OBS, MK_SRC, N, T, a, cl, d, e, ev, first, g, held, il, k, keys, l, mkFreq, mkIT, moa, n, note, o, on, other, p, r, reached, reg, rows, s, sub, v, was, why, wins, wst, x

## portafoglio  (portale.html 5350-5529, 180 lines) — §4 · Portafoglio — TWO UNIVERSES, ONE SCREEN, NEVER ONE NUMBER
MUST STILL DEFINE (later blocks read these): cross, declared, facts, flag, items, linked, on, port, shown, universe
MAY READ FROM EARLIER BLOCKS: PIT, REL, T, a, accent, aiTxt, d, e, ev, first, il, l, n, none, note, on, out, p, r, raw, reg, related, row, rows, s, stopped, t, uniLaw, v, verified, was

## voci  (portale.html 5530-5646, 117 lines) — §12 · Voci dal Campo
MUST STILL DEFINE (later blocks read these): C, cropL, decoV, issueL, kn, m, n, nar, proves, raw, t, voices, word
MAY READ FROM EARLIER BLOCKS: D, N, T, a, age, ageOf, cl, d, declared, e, evidence, first, g, il, keys, linked, n, on, raw, rejected, row, s, t, tok, v, was, wins, x

## bands  (portale.html 5647-5673, 27 lines) — §7 · The band split
MUST STILL DEFINE (later blocks read these): all, k, rest, themes
MAY READ FROM EARLIER BLOCKS: C, a, cropL, decoV, first, issueL, k, keys, kn, n, none, s, v, voices

## casefix  (portale.html 5674-5807, 134 lines) — §7 · MEASURED FAILURE, now fixed
MUST STILL DEFINE (later blocks read these): W, b, body, br, dead, kept, w
MAY READ FROM EARLIER BLOCKS: CASES, D, a, accent, cs0, declared, evidence, facts, ink, k, keys, l, live, match, n, o, on, other, out, raw, row, rows, s, table, verified, w, why, winFor, x, y

## fieldsales+fieldkpi  (portale.html 5808-5965, 158 lines) — §10 · Field Sales is an integration DEMONSTRATION
MUST STILL DEFINE (later blocks read these): IT, ago, co, composerExamples, demoMessages, fieldKpis, fieldMessages, fieldStateChips, fit, inboundFlow, o, oppOf, out, parsed, tsrs, w
MAY READ FROM EARLIER BLOCKS: D, F, L, LAGO, N, T, TIMING, a, all, cl, cropL, cross, d, e, evidence, first, g, il, issueL, k, keys, live, m, match, n, nav, o, on, other, out, p, proves, raw, reached, row, rows, s, sub, t, tally, v, w, was, x

## futuretokens+futurefeed  (portale.html 5966-6341, 376 lines) — §7 · PRESENTATION TOKENS. Authored here
MUST STILL DEFINE (later blocks read these): F_ACCENT, F_ICON, F_MUTED, F_SRC_ICON, F_SRC_TINT, F_TEXT, c, cat, d, dd, fSourceOn, fSources, fSrcTypeL, fStatusOn, fStatuses, fieldCases, ids, lab, sigAll, sigCountReal, sigPool, sigTypesOf, sigWL, visibleSignals, w, why
MAY READ FROM EARLIER BLOCKS: EMPTY, IT, L, T, TIMING, a, accent, all, allMessages, b, cl, cropL, d, declared, demoMessages, e, evidence, facts, fit, fst, g, hasDate, il, iso, issueL, items, k, kept, keys, l, live, m, max, n, note, o, on, oppOf, other, out, p, proves, r, raw, ref, reg, regLine, rest, row, rows, s, shown, srcL, t, tally, tiles, w, was, why, wins, x

## competitorwatch  (portale.html 6342-6486, 145 lines) — §1 · Competitor Watch now reads the model
MUST STILL DEFINE (later blocks read these): CACT, CACTS, CCOS, CDENS, CEVENTS, CISS, CMX, COMPCH, CPRODUCTS, CWM, NODATE, NOTKNOWN, OBS_WINDOW, STCOLOR, STRANK, TX, UPC, cAct, cNar, crops, dLabel, futureSourceKpis, futureStatusChips, monthKey, on, paid, uq, verified, within
MAY READ FROM EARLIER BLOCKS: CH, D, F_ACCENT, F_ICON, F_MUTED, F_SRC_ICON, F_SRC_TINT, F_TEXT, IT, T, a, absenceRule, accent, actDeco, all, b, c, ch, cl, cropL, dd, e, evidence, fSourceOn, fSources, fSrcTypeL, fStatusOn, fStatuses, first, fst, hasDate, il, initials, iso, issueL, k, match, n, none, note, on, out, parsed, r, row, rows, s, sigPool, sigTypesOf, t, tiles, v, verified, was, why, word, wst, x

## companies  (portale.html 6487-6564, 78 lines) — §1 · The 14 upstream company rows are 11 companies
MUST STILL DEFINE (later blocks read these): actsAll, actsOfKey, changed7, compStrip, compTabs, compViews, companies, feedGroups, k2, on, topMoves
MAY READ FROM EARLIER BLOCKS: CACT, CACTS, CCOS, CEVENTS, COMPCH, D, NODATE, NOTKNOWN, OBS_WINDOW, T, TX, UPC, a, all, b, c, cAct, cl, cropL, crops, dLabel, first, hasDate, initials, items, monthKey, n, note, obs, on, paid, rank, rows, s, themes, tiles, uq, within, x, y

## density  (portale.html 6565-6587, 23 lines) — §8 · communication density = density inside monitored public communication
MUST STILL DEFINE (later blocks read these): cropDensity, cropDensityNote, momentByCrop, rk
MAY READ FROM EARLIER BLOCKS: CDENS, CWM, STRANK, TX, a, all, cl, companies, cropL, crops, e, items, m, match, n, on, other, r, row, rows, s, word

## idresolve  (portale.html 6588-6671, 84 lines) — §18 · An id that does not resolve must SAY so
MUST STILL DEFINE (later blocks read these): co, compMoments, confirmed, evDeco, future, matrix, matrixCols, matrixNote, on
MAY READ FROM EARLIER BLOCKS: CMX, NODATE, NOTKNOWN, STCOLOR, TX, UPC, a, actsOfKey, all, b, cAct, cNar, cl, co, companies, cropL, crops, d, dLabel, e, evidence, first, g, hasDate, il, initials, issueL, items, k2, keys, l, m, max, momentByCrop, n, note, on, out, paid, prods, r, rk, row, rows, s, shown, table, themes, was, wst, x

## science+themejoin  (portale.html 6672-6949, 278 lines) — §12 · This block used to be built on four fixtures
MUST STILL DEFINE (later blocks read these): SCI_IDENT, SCI_MROLE, SCI_MTYPE, canon, compCropOptions, compIssueOptions, compPeriodOptions, compTotal, cp, e, evd, eventCards, galleryItems, issueRows, issueRowsNote, k, leadCrop, leadTimes, on, one, sciAbsence, sciAll, sciCat, sciCounts, sciIT, sciL, sciNOTE, sciNar, sciP0, sciPP0, sciR0, sciRes0, sciT0, sciUNK, sciUniq, sciVocab, statuses, upcomingEvents, verified, whatChanged, wins
MAY READ FROM EARLIER BLOCKS: C, CACTS, CDENS, CEVENTS, CISS, CPRODUCTS, L, N, NODATE, T, TX, a, absenceRule, actsAll, adamaLabel, all, b, cAct, cat, cl, companies, confirmed, cropL, crops, dLabel, e, evDeco, evidence, first, g, il, ink, issueL, items, k, l, match, moaNote, n, none, note, o, on, opts, other, paid, pstate, r, raw, related, rows, s, shown, t, table, themes, tok, v, verified, was, why, wins, word, wst, x

## caption88+gire+taxonomy  (portale.html 6950-7037, 88 lines) — §12 · The one caption this screen cannot ship without
MUST STILL DEFINE (later blocks read these): cropRaw, genus, gireAll, hits, raw, regions, sciActivityNote, sciClear, sciCloseImpact, sciHerbTotal, sciImpact, sciResistance, sciStrategic, sciThemes, sciTop, sciTotal, sciWeed
MAY READ FROM EARLIER BLOCKS: L, W, a, all, b, confirmed, cropL, d, declared, e, first, flag, g, note, o, on, one, out, p, parsed, r, raw, s, sciAll, sciIT, sciL, sciNOTE, sciNar, sciR0, sciRes0, sciT0, sciUniq, sp, universe, was, x

## denominator  (portale.html 7038-8031, 994 lines) — §8 · Never an absolute negative
MUST STILL DEFINE (later blocks read these): (nothing)
MAY READ FROM EARLIER BLOCKS: CASES, D, ICO, IT, K, L, LAGO, N, RES, SCI_IDENT, SCI_MROLE, SCI_MTYPE, T, WK, a, absenceRule, accent, actsAll, adamaLabel, ago, all, arcT, b, body, br, c, calCatColor, calClearBucket, calCropBtns, calEmptyCta, calEmptyGo, calEmptyText, calFilterLabel, calFootNote, calHorizons, calKpiNote, calKpis, calMarket, calModes, calMoments, calMonths, calNav, calRangeLabel, calRows, calSeason, calStrip, calYearMarks, canon, changed7, cl, co, compCropOptions, compIssueOptions, compMoments, compPeriodOptions, compStrip, compTabs, compTotal, compViews, companies, composerExamples, confirmed, cov, cp, cpMarketObj, cropDensity, cropDensityNote, cropL, cropRaw, crops, cross, cs, d, dataState, dataStateTotals, dead, declared, dw, dw0, e, earlyWindows, ev, evd, eventCards, evidence, facts, feedGroups, fieldCases, fieldKpis, fieldMessages, fieldStateChips, filtered, first, future, futureSourceKpis, futureStatusChips, g, galleryItems, genus, gireAll, goWindows, hasFilters, held, hit, hits, ids, il, inboundFlow, initials, issueL, issueRows, issueRowsNote, items, k, kept, keys, kpis, l, lab, langBtns, leadCrop, leadTimes, linked, m, match, matrix, matrixCols, matrixNote, max, mp, n, nar, nav, navIntegrationItems, navIntegrations, none, note, o, obs, on, one, opts, other, out, p, parsed, parts, pd, port, prods, proves, r, raw, reached, recentActivity, recs, regionRank, regionRankNote, regionTiles, regions, related, rest, row, rows, s, sciAbsence, sciActivityNote, sciAll, sciCat, sciClear, sciCloseImpact, sciCounts, sciHerbTotal, sciIT, sciImpact, sciL, sciNOTE, sciP0, sciPP0, sciR0, sciResistance, sciStrategic, sciT0, sciThemes, sciTop, sciTotal, sciUNK, sciUniq, sciVocab, sciWeed, sg, sg0, sgMissing, shown, sigAll, sigCountReal, sigWL, srcFreq, statuses, sub, t, table, tally, themes, todayInView, todayLeft, topMoves, tsrs, uniq, universe, upcomingEvents, v, verified, visibleCases, visibleSignals, voices, w, was, wd, whatChanged, why, windowBuckets, windowCropChips, wins, word, wst, x, y
