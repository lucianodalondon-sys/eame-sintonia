export const meta = {
  name: 'annate-agrarie-extract-batch2-2000-2013',
  description: 'Extract + adversarially verify vine peronospora/oidio statements from the 14 newly-recovered ARPAV annate agrarie 2000-2013',
  phases: [
    { title: 'Extract', detail: 'one agent per year, literal quotes only' },
    { title: 'Verify', detail: 'adversarial check: verbatim + attached to VINE not potato/tomato' },
  ],
}

const DIR = '/home/user/eame-sintonia/data/experiments/DISEASE-EVOLUTION-VITE-VENETO/NORMALIZED'
const YEARS = ['2000-01','2001-02','2002-03','2003-04','2004-05','2005','2006','2007','2008','2009','2010','2011','2012','2013']

const EXTRACT_SCHEMA = {
  type: 'object',
  properties: {
    year: { type: 'string' },
    vine_season_calendar_year: { type: 'integer', description: 'THE CALENDAR YEAR whose spring-summer vine season the peronospora statements describe. For a document titled "annata agraria 2000-01" the Italian agrarian year runs 1 Nov 2000 to 31 Oct 2001, so the VINE SEASON inside it is spring-summer 2001 -> report 2001. Justify in extractor_notes using dates the document itself gives.' },
    doc_char_count: { type: 'integer' },
    doc_covers_spring: { type: 'boolean' },
    doc_covers_summer: { type: 'boolean' },
    vine_peronospora_statements: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          quote_it: { type: 'string', description: 'VERBATIM Italian sentence(s) copied character-for-character from the file. Never paraphrase, never translate, never fix typos or spacing.' },
          period: { type: 'string', description: 'season/month the statement refers to, as stated in the doc, or UNSTATED' },
          severity_words_it: { type: 'array', items: { type: 'string' }, description: 'the exact Italian words carrying severity/intensity, e.g. leggere, gravità medio-bassa, virulenza importante, pressoché assente, scarsa intensità' },
          scope_words_it: { type: 'array', items: { type: 'string' }, description: 'exact Italian words carrying spatial extent, e.g. tutto il territorio regionale, in diversi areali, localmente, in alta e media collina' },
          subject_is_vine: { type: 'boolean', description: 'true ONLY if the sentence or its immediate context makes VITE/vigneti/uva the host. If the host is potato, tomato, onion, or unstated, set false.' },
          host_evidence_it: { type: 'string', description: 'the exact Italian words proving the host, e.g. "Nei vigneti", "della vite", "su vite"' },
          conditional_on_treatment: { type: 'boolean', description: 'true if severity is stated conditional on spraying, e.g. "nei vigneti regolarmente difesi"' },
        },
        required: ['quote_it','period','severity_words_it','scope_words_it','subject_is_vine','host_evidence_it','conditional_on_treatment'],
      },
    },
    vine_oidio_statements: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          quote_it: { type: 'string' },
          period: { type: 'string' },
          severity_words_it: { type: 'array', items: { type: 'string' } },
          subject_is_vine: { type: 'boolean' },
          host_evidence_it: { type: 'string' },
        },
        required: ['quote_it','period','severity_words_it','subject_is_vine','host_evidence_it'],
      },
    },
    other_host_peronospora_statements: {
      type: 'array',
      items: {
        type: 'object',
        properties: { quote_it: { type: 'string' }, host: { type: 'string' } },
        required: ['quote_it','host'],
      },
      description: 'peronospora sentences whose host is NOT vine (patata, pomodoro, cipolla...). Collect them so they can be proven excluded.',
    },
    no_vine_peronospora_found: { type: 'boolean' },
    extractor_notes: { type: 'string', description: 'anything that makes this year hard to compare with others' },
  },
  required: ['year','vine_season_calendar_year','doc_char_count','doc_covers_spring','doc_covers_summer','vine_peronospora_statements','vine_oidio_statements','other_host_peronospora_statements','no_vine_peronospora_found','extractor_notes'],
}

const VERIFY_SCHEMA = {
  type: 'object',
  properties: {
    year: { type: 'string' },
    vine_season_calendar_year_confirmed: { type: 'integer', description: 'the calendar year of the vine growing season described; verify the extractor got it right from dates in the text' },
    n_checked: { type: 'integer' },
    n_verbatim_ok: { type: 'integer' },
    verbatim_failures: {
      type: 'array',
      items: { type: 'object', properties: { claimed_quote: { type: 'string' }, why: { type: 'string' } }, required: ['claimed_quote','why'] },
    },
    host_misattributions: {
      type: 'array',
      items: { type: 'object', properties: { quote: { type: 'string' }, claimed_host: { type: 'string' }, actual_host: { type: 'string' }, proof_it: { type: 'string' } }, required: ['quote','claimed_host','actual_host','proof_it'] },
    },
    missed_vine_peronospora_quotes: {
      type: 'array',
      items: { type: 'object', properties: { quote_it: { type: 'string' }, why_it_matters: { type: 'string' } }, required: ['quote_it','why_it_matters'] },
    },
    corrected_vine_peronospora_quotes: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          quote_it: { type: 'string' },
          period: { type: 'string' },
          severity_words_it: { type: 'array', items: { type: 'string' } },
          scope_words_it: { type: 'array', items: { type: 'string' } },
          conditional_on_treatment: { type: 'boolean' },
        },
        required: ['quote_it','period','severity_words_it','scope_words_it','conditional_on_treatment'],
      },
      description: 'the FINAL trusted set for this year after removing bad quotes and adding missed ones',
    },
    year_has_usable_severity_signal: { type: 'boolean', description: 'true only if at least one verbatim vine-peronospora statement carries an explicit severity or intensity qualifier (not merely "infections occurred")' },
    year_has_mention_only: { type: 'boolean', description: 'true if peronospora on vine is mentioned but with NO severity/intensity qualifier anywhere' },
    verdict: { type: 'string', enum: ['OK','CORRECTED','REJECTED'] },
    verifier_notes: { type: 'string' },
  },
  required: ['year','vine_season_calendar_year_confirmed','n_checked','n_verbatim_ok','verbatim_failures','host_misattributions','missed_vine_peronospora_quotes','corrected_vine_peronospora_quotes','year_has_usable_severity_signal','year_has_mention_only','verdict','verifier_notes'],
}

const SCALE_SCHEMA = {
  type: 'object',
  properties: {
    scale_name: { type: 'string' },
    n_levels: { type: 'integer' },
    levels: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          code: { type: 'string' },
          definition_en: { type: 'string' },
          italian_marker_words: { type: 'array', items: { type: 'string' } },
        },
        required: ['code','definition_en','italian_marker_words'],
      },
      description: 'THE AUDITABLE MAPPING TABLE. Every Italian phrase that maps to a level must be listed here explicitly. No percentages. Ever.',
    },
    year_assignments: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          year: { type: 'integer' },
          level: { type: 'string', description: 'a level code, or NOT_ASSIGNABLE' },
          justifying_quote_it: { type: 'string' },
          matched_marker_words: { type: 'array', items: { type: 'string' } },
          confidence: { type: 'string', enum: ['HIGH','MEDIUM','LOW'] },
        },
        required: ['year','level','justifying_quote_it','matched_marker_words','confidence'],
      },
    },
    n_assignable: { type: 'integer' },
    n_not_assignable: { type: 'integer' },
    rationale: { type: 'string' },
    self_criticism: { type: 'string', description: 'the strongest argument that YOUR OWN scale is not comparable across years' },
  },
  required: ['scale_name','n_levels','levels','year_assignments','n_assignable','n_not_assignable','rationale','self_criticism'],
}

const CRITIQUE_SCHEMA = {
  type: 'object',
  properties: {
    comparability_verdict: { type: 'string', enum: ['COMPARABLE','PARTIALLY_COMPARABLE','NOT_COMPARABLE'] },
    n_years_truly_comparable: { type: 'integer' },
    comparable_years: { type: 'array', items: { type: 'integer' } },
    demo_only_years: { type: 'array', items: { type: 'integer' } },
    unusable_years: { type: 'array', items: { type: 'integer' } },
    threats: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          threat: { type: 'string' },
          severity: { type: 'string', enum: ['FATAL','SERIOUS','MINOR'] },
          evidence: { type: 'string' },
        },
        required: ['threat','severity','evidence'],
      },
      description: 'e.g. author/style drift, document length drift, treatment confound, spatial-scope drift, absence-of-statement != absence-of-disease',
    },
    circularity_check: { type: 'string', description: 'ARPAV attributes infections to rain. If the outcome class is largely a restatement of the rainfall the document also reports, predicting it from ERA5 rain is circular. State whether the SEVERITY class survives this or not.' },
    recommended_scale: { type: 'string' },
    verdict_on_12m_outlook: { type: 'string', enum: ['BACKTEST_CANDIDATE_STRONG','DEMO_ONLY','DESCRIPTION_ONLY','NOT_USABLE_FOR_12M_OUTLOOK'] },
    reasoning: { type: 'string' },
  },
  required: ['comparability_verdict','n_years_truly_comparable','comparable_years','demo_only_years','unusable_years','threats','circularity_check','recommended_scale','verdict_on_12m_outlook','reasoning'],
}

const RULES = `
HARD RULES — violating any of these makes your output worthless:
1. Every quote_it MUST be copied character-for-character from the file. Do not paraphrase, translate, normalise whitespace, or fix OCR artefacts. If you are not sure a string is verbatim, re-read the file and copy again.
2. NEVER invent a number, a percentage, or a hectare figure. If the document says "molto elevata", the value is the words "molto elevata", not a number.
3. Peronospora in these documents attacks VINE, POTATO, TOMATO, ONION and other crops. A sentence about "peronospora della patata" is NOT a vine observation. Judge the host from the sentence and its immediate surrounding context, and quote the Italian words that prove it.
4. Absence of a statement is NOT absence of disease. If the document says nothing, say nothing was said.
5. These are ARPAV/Veneto Region agro-meteorological year reports. They are OFFICIAL_OBSERVATION, not modelled risk.
`

phase('Extract')
const perYear = await pipeline(
  YEARS,
  (y) => agent(
    `Read the file ${DIR}/annata-agraria-${y}.txt IN FULL (use Read, it is small — under 16k chars).

This is the ARPAV Veneto "Andamento dell'annata agraria ${y}" report. It is an OLDER report than the 2014-2025 series and may be structured differently, be longer or shorter, or use different terminology.

Your job: extract EVERY statement about PERONOSPORA and about OIDIO, and decide for each one whether the host is VINE.

${RULES}

CRITICAL — WHICH SEASON IS THIS? Documents titled like "annata agraria 2000-01" cover the Italian agrarian year 1 November 2000 to 31 October 2001. The VINE growing season inside that span is spring-summer 2001. Set vine_season_calendar_year accordingly and justify it in extractor_notes from dates the document actually prints. Getting this off by one silently destroys the weather join, so be explicit.

Report doc_char_count as the real character count of the file (wc -c). Report doc_covers_spring / doc_covers_summer based on whether the document actually has narrative for those seasons.

Return the structured object. Nothing else.`,
    { label: `extract:${y}`, phase: 'Extract', schema: EXTRACT_SCHEMA }
  ),
  (ext, y) => {
    if (!ext) return null
    return agent(
      `You are an ADVERSARIAL VERIFIER. Another agent extracted disease statements from ${DIR}/annata-agraria-${y}.txt. Your job is to catch its mistakes, not to agree with it.

Read the file yourself, in full, FIRST. Then check the extraction below.

EXTRACTION UNDER REVIEW:
${JSON.stringify(ext, null, 2)}

Check, in this order:
(a) VERBATIM. For each quote_it, grep the file for a distinctive fragment of it. If the string does not appear character-for-character, it is a verbatim_failure. Be strict: an added or removed word, a changed accent, a "fixed" spacing all count as failures. (Note: the source PDFs contain irregular multi-space runs; a quote that collapsed them is a FAILURE, report it, but you may re-quote it correctly in corrected_vine_peronospora_quotes.)
(b) HOST. For each statement marked subject_is_vine=true, prove the host really is vine from the Italian text. Peronospora on patata/pomodoro/cipolla marked as vine is a host_misattribution — the single most damaging error possible here.
(c) COMPLETENESS. Search the file yourself for: peronospor, Peronospora, peronosporiche, macchie d'olio, oidio, Oidio, oidica, vite, vigneti, uva. Report any VINE peronospora statement the extractor missed.
(d) SEVERITY SIGNAL. Decide honestly whether this year carries an explicit severity/intensity qualifier for vine peronospora, or only a bare mention that infections happened. "infezioni primarie di Peronospora su tutti gli ambienti vitati" is SCOPE, not severity — judge carefully and say which it is in verifier_notes.

${RULES}

Then output corrected_vine_peronospora_quotes: the final trusted set for ${y} (bad quotes removed, missed quotes added, all verbatim).

Return the structured object. Nothing else.`,
      { label: `verify:${y}`, phase: 'Verify', schema: VERIFY_SCHEMA }
    )
  }
)

const verified = perYear.filter(Boolean)
log(`verified ${verified.length}/${YEARS.length} years`)

const _evidenceTable = verified.map(v => ({
  year: v.year,
  verdict: v.verdict,
  usable_severity: v.year_has_usable_severity_signal,
  mention_only: v.year_has_mention_only,
  quotes: v.corrected_vine_peronospora_quotes,
  notes: v.verifier_notes,
}))

return { per_year: verified }
