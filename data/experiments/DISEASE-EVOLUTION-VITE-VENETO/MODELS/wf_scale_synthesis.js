export const meta = {
  name: 'outcome-scale-synthesis-26-seasons',
  description: 'Design three independent ordinal outcome scales over all 26 ARPAV seasons, cross-check each against the mechanical lexicon scan, then audit comparability and apply Gate A',
  phases: [
    { title: 'Scale', detail: 'strict / generous / direction-only, independently designed' },
    { title: 'CrossCheck', detail: 'each scale vs the frozen mechanical lexicon scan' },
    { title: 'Gate', detail: 'comparability audit and Gate A, applied literally' },
  ],
}

const ROOT = '/home/user/eame-sintonia/data/experiments/DISEASE-EVOLUTION-VITE-VENETO'
const EVID = `${ROOT}/OBSERVATIONS/verified_evidence.json`
const LEX  = `${ROOT}/OBSERVATIONS/lexicon_scan.json`
const RUNA = `${ROOT}/OBSERVATIONS/independent_run_A.json`

const SCALE_SCHEMA = {
  type: 'object',
  properties: {
    scale_name: { type: 'string' },
    n_levels: { type: 'integer' },
    levels: { type: 'array', items: { type: 'object', properties: {
      code: { type: 'string' }, definition_en: { type: 'string' },
      italian_marker_words: { type: 'array', items: { type: 'string' } } },
      required: ['code','definition_en','italian_marker_words'] } },
    year_assignments: { type: 'array', items: { type: 'object', properties: {
      doc_key: { type: 'string', description: 'e.g. "2000-01" or "2016" exactly as the source document is keyed' },
      vine_season_year: { type: 'integer', description: 'the CALENDAR year of the spring-summer vine season this row describes' },
      level: { type: 'string', description: 'a level code, or NOT_ASSIGNABLE' },
      justifying_quote_it: { type: 'string' },
      matched_marker_words: { type: 'array', items: { type: 'string' } },
      confidence: { type: 'string', enum: ['HIGH','MEDIUM','LOW'] } },
      required: ['doc_key','vine_season_year','level','justifying_quote_it','matched_marker_words','confidence'] } },
    n_assignable: { type: 'integer' },
    n_not_assignable: { type: 'integer' },
    rationale: { type: 'string' },
    self_criticism: { type: 'string', description: 'the strongest argument that YOUR OWN scale is not comparable across 26 seasons spanning two decades and several authors' },
  },
  required: ['scale_name','n_levels','levels','year_assignments','n_assignable','n_not_assignable','rationale','self_criticism'],
}

const XCHECK_SCHEMA = {
  type: 'object',
  properties: {
    scale_name: { type: 'string' },
    n_years_compared: { type: 'integer' },
    agreements: { type: 'integer' },
    disagreements: { type: 'array', items: { type: 'object', properties: {
      doc_key: { type: 'string' }, scale_says: { type: 'string' }, lexicon_says: { type: 'string' },
      who_is_right: { type: 'string', enum: ['SCALE','LEXICON','NEITHER','UNDECIDABLE'] },
      evidence_it: { type: 'string' } },
      required: ['doc_key','scale_says','lexicon_says','who_is_right','evidence_it'] } },
    years_the_scale_over_reached: { type: 'array', items: { type: 'string' },
      description: 'years the scale assigned a level where the source really supports none' },
    robustly_codeable_years: { type: 'array', items: { type: 'string' },
      description: 'doc_keys where the scale and the mechanical scan agree AND the evidence is a direct severity statement about vine peronospora' },
    verdict: { type: 'string' },
  },
  required: ['scale_name','n_years_compared','agreements','disagreements','years_the_scale_over_reached','robustly_codeable_years','verdict'],
}

const GATE_SCHEMA = {
  type: 'object',
  properties: {
    n_documents: { type: 'integer' },
    n_with_any_vine_peronospora_statement: { type: 'integer' },
    n_with_explicit_severity: { type: 'integer' },
    n_mention_only: { type: 'integer' },
    n_no_outcome_at_all: { type: 'integer' },
    n_truly_comparable: { type: 'integer', description: 'the number Gate A is applied to. Same construct, measured the same way, agreed by at least two of the three scales AND not over-reached per the cross-check.' },
    comparable_doc_keys: { type: 'array', items: { type: 'string' } },
    demo_only_doc_keys: { type: 'array', items: { type: 'string' } },
    unusable_doc_keys: { type: 'array', items: { type: 'string' } },
    scale_disagreement_years: { type: 'array', items: { type: 'string' } },
    threats: { type: 'array', items: { type: 'object', properties: {
      threat: { type: 'string' }, severity: { type: 'string', enum: ['FATAL','SERIOUS','MINOR'] },
      evidence: { type: 'string' } }, required: ['threat','severity','evidence'] } },
    document_length_confound: { type: 'string', description: 'documents run 7,166 to 32,553 chars. Quantify whether assigned level correlates with document length. If it does, that is close to fatal.' },
    author_drift: { type: 'string' },
    agrarian_vs_calendar_year_risk: { type: 'string' },
    circularity_check: { type: 'string' },
    recommended_scale: { type: 'string' },
    GATE_A_VERDICT: { type: 'string', enum: ['BACKTEST_CANDIDATE_STRONG','DEMO_ONLY','DESCRIPTION_ONLY','NOT_USABLE_FOR_12M_OUTLOOK'] },
    reasoning: { type: 'string' },
    what_would_change_the_verdict: { type: 'string' },
  },
  required: ['n_documents','n_with_any_vine_peronospora_statement','n_with_explicit_severity','n_mention_only','n_no_outcome_at_all','n_truly_comparable','comparable_doc_keys','demo_only_doc_keys','unusable_doc_keys','scale_disagreement_years','threats','document_length_confound','author_drift','agrarian_vs_calendar_year_risk','circularity_check','recommended_scale','GATE_A_VERDICT','reasoning','what_would_change_the_verdict'],
}

const COMMON = `
SOURCES YOU MUST READ YOURSELF:
  ${EVID}  adversarially-verified verbatim quotes, per source document
  ${LEX}   a frozen MECHANICAL lexicon scan of the same 26 documents (cross-check only, not truth)
  ${RUNA}  AN INDEPENDENT SECOND EXTRACTION of 2014-2025 only, run separately with a different
           schema and different agents. Use it as a replication check. On that overlap it
           rated only 6 seasons comparable (2014, 2016, 2021, 2022, 2024, 2025) where the
           main file reports 8 with explicit severity — so the main file's severity flag
           runs roughly 1.4x optimistic, and you should expect a similar shrinkage on the
           2001-2013 seasons, which have no replication run at all and must therefore carry
           MORE doubt, not less. Where run A and the
           main evidence file disagree about a season, that season is NOT robustly codeable
           and must not be counted as comparable, whichever one you personally find more
           convincing. They already disagree on 2017, 2018 and 2023.
  ${ROOT}/NORMALIZED/annata-agraria-<key>.txt  the raw text of any document you want to re-read

ABSOLUTE RULES:
- NEVER produce a percentage or a numeric severity. "molto elevata" maps to a LEVEL CODE
  through an explicit table, never to "87%".
- A year with no severity statement is NOT_ASSIGNABLE. It is not "LOW". Silence is not mildness.
- Peronospora in these reports also attacks potato, tomato and onion. Only vine-hosted
  statements count.
- RISK IS NOT PRESENCE. This is the pilot's central law and it has already been violated
  once. The 2017 report's ONLY peronospora sentence is "Verso la metà di giugno i vigneti
  erano in prechiusura-grappolo con un rischio basso di infezione di Peronospora" — that is
  a forward-looking infection-RISK category from a weather-driven model, evaluated on one
  date. It is NOT a statement about what the disease did. The main evidence file wrongly
  coded 2017 as carrying a severity signal; the independent run caught it. Audit every other
  season for the same mistake: "rischio", "pericolo", "condizioni favorevoli", "possibili
  infezioni" are risk language, not outcome. Report every one you find.
- Some statements are conditional on spraying ("nei vigneti regolarmente difesi"). That is
  severity UNDER CONTROL, not natural pressure. Say how you handled it.
- DOCUMENT KEYS ARE NOT SEASONS. A file named "2000-01" is internally titled "PERIODO
  GENNAIO-NOVEMBRE 2001": the YYYY-YY key denotes the report for the SECOND year, not an
  agrarian year. Read vine_season_year from the evidence file, which each verifier resolved
  from the printed header. Also: ARPAV published TWO reports for 2005 ("2004-05" and
  "2005"), already collapsed into one season with quotes unioned. There are 26 documents
  but only 25 distinct seasons, 2001-2025. Never count documents as seasons.
- The evidence file has both per_document and per_season. USE per_season.
- Document length runs from 7,166 to 32,553 characters. A longer report mentions more
  diseases regardless of the season. Do not mistake verbosity for severity.
`

const BRIEFS = [
  { key: 'strict', brief: 'STRICT. Assign a level only where the document contains an unambiguous severity qualifier attached to vine peronospora. Prefer NOT_ASSIGNABLE over a guess. Levels: LOW / MEDIUM / HIGH seasonal pressure.' },
  { key: 'generous', brief: 'GENEROUS. Allow scope and treatment-effort language as secondary evidence where direct severity words are missing (repeated sprays, "su tutti gli ambienti vitati", "ha costretto i viticoltori a ripetere i trattamenti"). Levels: LOW / MEDIUM / HIGH. Your mapping table must list exactly which secondary markers you admitted.' },
  { key: 'direction', brief: 'DIRECTION-ONLY. Do not rank absolute severity at all. Place each season only against the typical Veneto season as the documents themselves frame it: ABOVE_NORMAL / NORMAL / BELOW_NORMAL. Deliberately coarser, and it should be more robust to two decades of author drift.' },
]

phase('Scale')
const scaleResults = await pipeline(
  BRIEFS,
  (b) => agent(
    `Design an ORDINAL OUTCOME SCALE for vine peronospora seasonal pressure in Veneto across 25 DISTINCT VINE SEASONS (2001-2025) reconstructed from 26 ARPAV annata-agraria reports.

YOUR BRIEF: ${b.brief}

${COMMON}

Your levels[] array IS the auditable mapping table. Every Italian marker phrase you relied on must appear in it, so a reader can redo your assignment by hand from the table alone.

Finish with self_criticism: the strongest argument that YOUR OWN scale is not comparable across 26 seasons written by different people over two decades. Be genuinely damaging to yourself.

Return the structured object. Nothing else.`,
    { label: `scale:${b.key}`, phase: 'Scale', schema: SCALE_SCHEMA, effort: 'high' }
  ),
  (sc, b) => {
    if (!sc) return null
    return agent(
      `You are cross-checking one ordinal scale against a frozen MECHANICAL lexicon scan of the same documents.

THE SCALE UNDER REVIEW (brief was: ${b.brief}):
${JSON.stringify(sc, null, 2)}

Read ${LEX} for the mechanical scan. Its per-document "mechanical_class" is one of HIGH / MEDIUM / LOW / NO_SEVERITY_MARKER, with a "mechanical_confidence".

The mechanical scan is DUMB ON PURPOSE. It cannot resolve host from context and it will mis-tag some sentences. It is not truth. It is a floor: where a careful reader and a dumb word-counter disagree, that document is not robustly codeable, whichever one is right.

For every document:
- compare the scale's level with the mechanical class
- when they disagree, go read ${ROOT}/NORMALIZED/annata-agraria-<key>.txt and decide who is right, with the Italian evidence
- flag over-reach: any document where the scale assigned a level and the source really supports none

Then list robustly_codeable_years: doc_keys where the scale and the scan agree AND the evidence is a direct severity statement about vine peronospora. That list, not the document count, is what Gate A will be applied to.

Return the structured object. Nothing else.`,
      { label: `xcheck:${b.key}`, phase: 'CrossCheck', schema: XCHECK_SCHEMA, effort: 'high' }
    ).then(x => ({ brief: b.key, scale: sc, xcheck: x }))
  }
)

const all = scaleResults.filter(Boolean)
log(`scales designed and cross-checked: ${all.length}/3`)

phase('Gate')
const gate = await agent(
  `You are the GATE A AUDITOR. You decide whether a backtest of seasonal peronospora pressure in Veneto is honest. Your default is skepticism. A wrong "yes" here poisons every downstream claim, and this pilot is going in front of people on Monday.

THREE SCALES, EACH WITH ITS OWN SELF-CRITICISM AND AN INDEPENDENT MECHANICAL CROSS-CHECK:
${JSON.stringify(all, null, 2)}

${COMMON}

Do this:
1. Count honestly. Documents are not seasons. "Mentions peronospora" is not a comparable season. n_truly_comparable = same construct, measured the same way, agreed by at least two of the three scales, and not flagged as over-reach by the cross-check.
2. Where the three scales DISAGREE on a season, that is direct evidence the season is not robustly codeable. List those.
3. QUANTIFY THE LENGTH CONFOUND. Documents run 7,166 to 32,553 chars. Read the char counts from the lexicon scan file and check whether the assigned level tracks document length. If it does, say so plainly — it is close to fatal.
4. ERA BIAS — quantify this, it may be decisive. The frozen mechanical lexicon scan finds a
   severity marker in only 3 of the 14 documents from 2000-2013, versus 9 of 12 from
   2014-2025. If outcome availability is correlated with era, then the seasons that carry a
   usable outcome are not a random sample of seasons, and a backtest trained on early years
   to predict late ones is comparing two different reporting regimes rather than two
   different epidemics. Say plainly whether this is SERIOUS or FATAL.
   Also cover author drift (the by-line changes across the series) and the document-key
   versus season mapping.
5. CIRCULARITY. These reports explain infections by the rain that caused them. Note for your own reasoning that an independent probe over 34 ERA5 seasons already found antecedent weather explains at most ~23% of the variance in the target season's own rainfall — so the predictors are NOT a disguised copy of the season, but the weather pathway is correspondingly weak. Say what survives.
6. Apply the gate LITERALLY to n_truly_comparable. Do not relax it to save the hypothesis:
     >=8 -> BACKTEST_CANDIDATE_STRONG
     6-7 -> DEMO_ONLY
     3-5 -> DESCRIPTION_ONLY
     <3  -> NOT_USABLE_FOR_12M_OUTLOOK

Return the structured object. Nothing else.`,
  { label: 'gate-a-audit', phase: 'Gate', schema: GATE_SCHEMA, effort: 'high' }
)

return { scales: all, gate }
