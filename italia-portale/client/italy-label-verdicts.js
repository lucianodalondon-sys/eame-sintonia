/* UPSTREAM LABEL VERDICTS · applied 02 September 2026
   Source: Claude Code audit of the 163 official Italian product labels.
   The presentation layer APPLIES these verdicts. It must never research,
   infer or promote a product relationship on its own.

   Semantic rule that governs every NOT_FOUND verdict:
     ABSENCE IN OUR READING  ≠  ABSENCE IN THE WORLD.
   A product missing from this reading is NOT evidence that ADAMA has no product. */
(function () {
  const STRENGTH = {
    VERIFIED_LABEL_MATCH: { label: 'VERIFIED_LABEL_MATCH', color: '#009845', rank: 0 },
    RELATED_PORTFOLIO: { label: 'RELATED_PORTFOLIO', color: '#00783F', rank: 1 },
    LABEL_CHECK_NEEDED: { label: 'LABEL_CHECK_NEEDED', color: '#978B87', rank: 2 },
    NO_CONFIRMED_MATCH_CURRENT_READING: { label: 'NO_CONFIRMED_MATCH_CURRENT_READING', color: '#CBC5C3', rank: 3 }
  };

  /* Verified by the upstream label audit. Key: CROP|ISSUE|PRODUCT */
  const VERIFIED = [
    ['Apple', 'Codling Moth', 'COSAYR 200 SC'],
    ['Maize', 'European Corn Borer', 'COSAYR 200 SC'],
    ['Grapevine', 'Grapevine Moth', 'COSAYR 200 SC'],
    ['Maize', 'Diabrotica', 'FORZA'],
    ['Maize', 'Diabrotica Adults', 'FORZA'],
    ['Wheat', 'Cereal Aphids', 'MAVRIK EW'],
    ['Wheat', 'Cereal Aphids / BYDV Risk', 'MAVRIK EW'],
    ['Wheat', 'Fusarium Head Blight', 'MAXENTIS'],
    ['Durum Wheat', 'Fusarium Head Blight', 'MAXENTIS'],
    ['Wheat', 'Septoria Leaf Blotch', 'MAXENTIS'],
    ['Grapevine', 'Flavescenza Dorata', 'EVURE PRO'],
    ['Grapevine', 'Flavescenza Dorata', 'MAVRIK SMART']
  ];

  /* Explicitly NOT supported by the current label reading.
     These were rendered as verified matches and must be downgraded. */
  const NOT_FOUND = [
    ['Olive', 'Olive Fruit Fly', 'KLARTAN 20 EW'],
    ['Olive', 'Olive Fruit Fly', 'KLARTAN SMART'],
    ['Olive', 'Olive Fruit Fly', 'MAVRIK SMART'],
    ['Sugar Beet', 'Cercospora Leaf Spot', 'MIRADOR TURBO'],
    ['Sugar Beet', 'Cercospora Leaf Spot', 'CUSTODIA ULTRA'],
    ['Grapevine', 'Downy Mildew', 'MIRADOR TURBO'],
    ['Tomato', 'Tomato Leafminer', 'COSAYR 200 SC']
  ];

  const key = (crop, issue, product) => [crop, issue, product].join('|');
  const V = {}; VERIFIED.forEach(r => { V[key(r[0], r[1], r[2])] = 'VERIFIED_LABEL_MATCH'; });
  const N = {}; NOT_FOUND.forEach(r => { N[key(r[0], r[1], r[2])] = 'NO_CONFIRMED_MATCH_CURRENT_READING'; });

  /* Every relationship shown in the UI must resolve through this function.
     The default is LABEL_CHECK_NEEDED — never a promotion. */
  function verdict(crop, issue, product) {
    const k = key(crop, issue, product);
    if (N[k]) return 'NO_CONFIRMED_MATCH_CURRENT_READING';
    if (V[k]) return 'VERIFIED_LABEL_MATCH';
    return 'LABEL_CHECK_NEEDED';
  }

  window.ITALY_LABEL_VERDICTS = {
    AUDIT_DATE: '2026-09-02',
    AUDIT_SOURCE: 'Claude Code reading of 163 official Italian product labels',
    SCOPE_NOTE: 'The audit verified the main visible claims, not every portfolio connection in the interface. Anything not explicitly verified remains pending label verification.',
    ABSENCE_RULE: 'Absence in this reading is not absence in the world.',
    STRENGTH, VERIFIED, NOT_FOUND, verdict,
    verifiedCount: VERIFIED.length, notFoundCount: NOT_FOUND.length
  };
})();
