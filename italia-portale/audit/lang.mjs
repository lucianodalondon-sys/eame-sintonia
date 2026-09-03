/* SINTONIA ITALY · LANGUAGE AND VOCABULARY GUARDS
   ---------------------------------------------------------------------------
   Two defects that a naive migration ships silently, both measured on this
   package:

   1 · PORTUGUESE RESEARCH PROSE REACHING THE ITALIAN CLIENT.
       The upstream intelligence was researched in Portuguese. 219/219 label-use
       rows, 17/17 voices, 8/8 news items, 34/34 resistance mechanisms and 31/31
       source limitations carry Portuguese working notes. Worse, it is not only
       narrative fields: OPPORTUNITIES.CROP is "Videira", FUTURE_SIGNALS.CROP is
       "TRIGO e TRIGO DURO", RESISTANCE.CROP_DECLARED is whole Portuguese
       sentences. Those are FACT fields.

   2 · SIX INCOMPATIBLE CROP VOCABULARIES.
       canonical windows say "Grapevine"; ingested crop windows say "VITE";
       opportunities say "Videira"; future signals say "MAIS"; science and voices
       say "VINE" / "DURUM_WHEAT"; competitor activity says "Vitis vinifera" or
       the generic "colture"; news says "CEREAIS". Every cross-collection join on
       a crop name is therefore broken, and every crop dropdown mixes languages.

   These guards do not translate anything. They FAIL the build when untranslated
   research prose or an unresolved vocabulary token reaches a rendered prop.
   --------------------------------------------------------------------------- */

/* Words that exist in Portuguese and not in Italian. Deliberately conservative:
   every entry was checked against the Italian strings actually in this package,
   and ambiguous tokens ("mais" — Italian for maize, "e", "per") are excluded. */
export const PT_MARKERS = [
  'nao', 'não', 'são', 'foi', 'pelo', 'pela', 'pelos', 'pelas', 'então', 'entao',
  'apenas', 'nenhum', 'nenhuma', 'porque', 'dados', 'leitura', 'rótulo', 'rotulo',
  'também', 'tambem', 'uma', 'dos', 'das', 'muito', 'depois', 'agora', 'aqui',
  'antes', 'encontrado', 'encontrada', 'revogada', 'verificado',
  /* 'epoca' SEM acento saiu desta lista: e italiano corrente («epoca di
     applicazione»), e marcava como portuguesa a propria traducao aprovada
     de SRC_SALUTE_GOV_IT. A forma acentuada fica, que essa e so portuguesa.
     Vale aqui a regra que o cabecalho ja declara para 'mais' e 'per':
     token ambiguo nao e marcador, e um marcador que acusa italiano correto
     ensina a ignorar o detector. */
  'coluna', 'época', 'registros', 'milho', 'trigo', 'arroz', 'soja',
  'videira', 'oliveira', 'tomate', 'melao', 'melão', 'cereais', 'ficha', 'atencao',
  'atenção', 'vencimento',
  'transversal', 'convergencia', 'convergência', 'olival', 'alfafa',
  'afiliacao', 'afiliação', 'estudo', 'rotulo autorizado', 'sistema colturale',
  /* Found by opening the portal in a real browser, not by the headless suite:
     the REGION and ISSUE fact fields carry Portuguese annotation too —
     "Veneto (principal) + Lombardia", "vale do Pó (escala)",
     "micotoxina / Fusarium", "REGULATORIO · UE". */
  'principal', 'sinal', 'escala', 'vale do', 'micotoxina', 'micotoxinas',
  'desoxinivalenol', 'regulatorio', 'regulatório', 'praga', 'pragas',
  'colheita', 'lavoura', 'plantio', 'safra',
];
/* Deliberately NOT markers, because they are ordinary Italian too and produced
   false positives when measured against this package's own Italian strings:
   prova · cultura · calendario · mais (Italian for maize) · e · per */
const PT_RE = new RegExp('(^|[^\\p{L}])(' + PT_MARKERS.join('|') + ')([^\\p{L}]|$)', 'iu');

/* English that must not appear when the interface is Italian. Product names,
   company names, Latin binomials and original public quotes are exempt and are
   filtered out by the caller before this runs. */
export const EN_MARKERS = [
  'days left', 'days remaining', 'no content', 'all crops', 'all issues', 'all regions',
  'portfolio check needed', 'label check needed', 'not found', 'unknown', 'unrecognised',
  'real identity', 'demo profile', 'recent activity', 'window open', 'window closed',
  'next cycle', 'act now', 'prepare', 'watch closely', 'needs validation', 'search',
  'loading', 'more', 'single match', 'no confirmed match', 'not yet known',
  'monitoring', 'confirmed exhibitors', 'historical participants', 'no timing match',
  'approaching window', 'in window', 'post window', 'early', 'observed', 'not observed',
  /* 'intelligence' is NOT a marker: it is an ordinary Italian loanword for the
     discipline ('intelligence militare'), and gating on it would fail correct
     Italian copy. */
  'overview', 'insights',
  'monitoring season', 'season start', 'crop or product', 'type like you',
];
const EN_RE = new RegExp('(^|[^\\p{L}])(' + EN_MARKERS.map((m) => m.replace(/ /g, '\\s+')).join('|') + ')([^\\p{L}]|$)', 'iu');

/* English function words that are NOT also Italian words. A marker list only
   catches phrases someone thought of; these catch English prose in general.
   Shared tokens (no · in · a · e · per · non · come · sono) are excluded, and
   the list was measured against all 517 Italian interface strings: zero hits. */
export const EN_FUNCTION = [
  'the', 'and', 'of', 'for', 'with', 'from', 'not', 'is', 'are', 'was', 'were',
  'this', 'that', 'these', 'those', 'when', 'where', 'which', 'who', 'what',
  'only', 'before', 'after', 'each', 'been', 'have', 'has', 'had', 'will',
  'would', 'should', 'must', 'they', 'their', 'there', 'than', 'then', 'into',
  'over', 'under', 'about', 'above', 'below', 'between', 'through', 'during',
  'without', 'within', 'because', 'while', 'until', 'since', 'both', 'other',
  'another', 'every', 'most', 'more', 'less', 'many', 'much', 'such', 'same',
  'own', 'just', 'also', 'still', 'even', 'ever', 'never', 'always', 'often',
  'however', 'therefore', 'above', 'yet', 'here', 'above', 'across', 'against',
];
const EN_FN_RE = new RegExp('(^|[^\\p{L}])(' + EN_FUNCTION.join('|') + ')([^\\p{L}]|$)', 'iu');

/** English prose, not just a known phrase. Used on template text nodes. */
export function looksEnglish(v) {
  if (typeof v !== 'string') return false;
  const t = v.trim();
  if (t.length < 8 || EXEMPT.test(t) || CODEY.test(t)) return false;
  if (!/[A-Za-z]{4}/.test(t)) return false;
  const s = stripCodes(t);
  return EN_RE.test(s) || EN_FN_RE.test(s);
}

/* Strings we must never flag: URLs, ids, Latin binomials, pure numbers, and the
   codes the model deliberately keeps language-independent. */
const EXEMPT = /^(https?:|IT-|EV-|FM-|CAT-|[A-Z]{2,}-\d)|^\d|^[A-Z_]+$|^[A-Z][a-z]+ [a-z]+$/;
const CODEY = /^[A-Z0-9_ ·\/+-]+$/;

/* A SCREAMING_SNAKE token is a canonical code, not prose. The portal shows some
   of them on purpose — "non osservata (NOT_OBSERVED)" is Italian with the code
   kept so the line stays traceable — and matching the English word inside the
   code would fail correct copy. Strip codes before judging the language. */
const stripCodes = (s) => String(s).replace(/\b[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+\b/g, ' ');

export function isPortuguese(v) {
  if (typeof v !== 'string' || v.length < 12) return false;
  if (EXEMPT.test(v)) return false;
  return PT_RE.test(stripCodes(v));
}
export function isEnglish(v) {
  if (typeof v !== 'string' || v.length < 3) return false;
  const s = stripCodes(v);
  /* A curated marker beats the exemptions. The binomial exemption
     (Capitalized lowercase) was silently swallowing "Window closed" and
     "Label check needed" — measured: recall 2 of 3 on known-English phrases. */
  if (EN_RE.test(s)) return true;
  if (EXEMPT.test(v) || CODEY.test(v)) return false;
  return false;
}

/** Walk a props object and collect every string, with its path. */
export function collectStrings(root, { skipKeys = ['raw', 'ui', 'textOriginal', 'quote', 'url', 'sourceUrl', 'labelUrl', 'catalogUrl', 'href', 'icon', 'color', 'bg', 'border', 'rail', 'tint'], limit = 4000 } = {}) {
  const out = [];
  const seen = new Set();
  const walk = (v, p) => {
    if (out.length >= limit || v === null || v === undefined) return;
    if (typeof v === 'string') { out.push({ path: p, value: v }); return; }
    if (typeof v !== 'object' || seen.has(v)) return;
    seen.add(v);
    if (Array.isArray(v)) { v.slice(0, 60).forEach((x, i) => walk(x, `${p}[${i}]`)); return; }
    for (const k of Object.keys(v)) {
      if (skipKeys.includes(k)) continue;
      if (typeof v[k] === 'function') continue;
      walk(v[k], p ? `${p}.${k}` : k);
    }
  };
  walk(root, '');
  return out;
}

/* ── crop vocabulary ──────────────────────────────────────────────────────
   The canonical crop set is the one the audited window contract uses. Every
   other vocabulary maps onto it. A GENERIC term is never resolved to a
   specific crop: "cereali" is not "Wheat", and saying so would invent a fact. */
export const CANONICAL_CROPS = [
  'Grapevine', 'Maize', 'Olive', 'Sugar Beet', 'Apple', 'Wheat', 'Durum Wheat',
  'Tomato', 'Rice', 'Soybean', 'Barley', 'Sorghum', 'Triticale', 'Potato',
  'Sunflower', 'Citrus', 'Peach',
];
export const CROP_ALIASES = {
  Grapevine: ['vite', 'videira', 'vitis vinifera', 'vine', 'grapevine', 'vigneto', 'uva'],
  Maize: ['mais', 'milho', 'milho grao', 'milho grão', 'zea mays', 'maize', 'mais grano', 'granoturco'],
  Olive: ['olivo', 'oliveira', 'olea europaea', 'olive', 'uliveto', 'olival', 'olivicolo'],
  Wheat: ['frumento', 'frumento tenero', 'trigo', 'triticum aestivum', 'wheat', 'common_wheat', 'wheat_generic', 'grano tenero'],
  'Durum Wheat': ['grano duro', 'frumento duro', 'durum wheat', 'durum_wheat', 'trigo duro', 'triticum durum'],
  Soybean: ['soia', 'soja', 'soybean', 'glycine max'],
  Rice: ['riso', 'arroz', 'rice', 'oryza sativa'],
  Tomato: ['pomodoro', 'tomate', 'tomato', 'solanum lycopersicum'],
  'Sugar Beet': ['barbabietola', 'sugar beet', 'sugarbeet', 'beta vulgaris', 'beterraba'],
  Apple: ['melo', 'apple', 'malus domestica', 'maca', 'maçã'],
  Barley: ['orzo', 'barley', 'cevada', 'hordeum'],
  Sorghum: ['sorgo', 'sorghum'],
  Triticale: ['triticale'],
  Potato: ['patata', 'potato', 'batata', 'solanum tuberosum'],
  Sunflower: ['girasole', 'sunflower', 'helianthus annuus'],
  Citrus: ['citrus', 'agrumi'],
  Peach: ['pesco', 'peach', 'prunus persica'],
  /* The V2.1 id vocabulary names two more real crops the fixture never carried.
     They belong here for the same reason Peach and Citrus already do: they are
     crops, they have no canonical window, and a resolver that does not know a
     crop reports it as UNMAPPED — which reads as a broken join rather than as
     'this crop has no window in this package'. */
  Pear: ['pero', 'pear', 'pyrus communis', 'pera'],
  Kiwi: ['actinidia', 'kiwi', 'actinidia deliciosa', 'actinidia chinensis'],
};
/* Terms that name a GROUP, not a crop. They stay generic, on purpose. */
export const GENERIC_CROP_TERMS = [
  'colture', 'cereali', 'cereais', 'cereal', 'frutta', 'ortaggi', 'orticole',
  'vegetables', 'fruit', 'colture perenni', 'vivaio', 'transversal', 'trasversale',
  'cereali autunno-vernini', 'erba medica', 'alfafa',
];

const norm = (s) => String(s || '').toLowerCase().trim()
  .replace(/[«»"'()]/g, ' ')
  .replace(/\s+/g, ' ')
  .trim();

/** Resolve a crop token to { key, scope }. scope: RESOLVED | GENERIC_TERM | UNMAPPED. */
export function cropKeyOf(token) {
  const t = norm(token);
  if (!t) return { key: null, scope: 'NOT_OBSERVED', raw: token };
  for (const g of GENERIC_CROP_TERMS) if (t === g || t.startsWith(g + ' ')) return { key: null, scope: 'GENERIC_TERM', raw: token };
  for (const [key, alist] of Object.entries(CROP_ALIASES)) {
    for (const a of alist) {
      if (t === a) return { key, scope: 'RESOLVED', raw: token };
    }
  }
  /* Substring match, but only against aliases long enough to be unambiguous.
     A source that writes "grano duro e tenero" really is naming two crops —
     that is MULTI, not an error, and collapsing it to one would lose a fact. */
  const hits = new Set();
  for (const [key, alist] of Object.entries(CROP_ALIASES)) {
    for (const a of alist) if (a.length >= 4 && t.includes(a)) hits.add(key);
  }
  const keys = [...hits];
  if (keys.length === 1) return { key: keys[0], scope: 'RESOLVED', raw: token };
  if (keys.length > 1) return { key: null, keys, scope: 'MULTI', raw: token };
  for (const g of GENERIC_CROP_TERMS) if (t.includes(g)) return { key: null, scope: 'GENERIC_TERM', raw: token };
  return { key: null, scope: 'UNMAPPED', raw: token };
}
