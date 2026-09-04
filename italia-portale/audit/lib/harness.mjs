/* SINTONIA ITALY · HEADLESS HARNESS
   ---------------------------------------------------------------------------
   Loads the client package's data files and the portal's own logic class into a
   Node sandbox, with no browser and no network, so every check below runs on the
   REAL pipeline instead of on a grep of the source.

   Two levels:
     loadData()  -> window with every ITALY_* global and ITALY_APP_MODEL built
     mount()     -> an instance of the portal's Component class, so renderVals()
                    can be called for any view and any state
   --------------------------------------------------------------------------- */
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
export const CLIENT = path.resolve(HERE, '..', '..', 'client');
export const BASELINE = path.resolve(HERE, '..', '..', 'BASELINE');

/* Load order is the order portale.html uses. support.js and the design-system
   bundle are browser-only and deliberately excluded — nothing in the data
   contract may depend on them. */
export const DATA_FILES = [
  'italy-canonical-windows.js',
  'italy-label-verdicts.js',
  'italy-real-intelligence.js',
  'italy-demo-data.js',
  'italy-briefs.js',
  'italy-market-pulse.js',
  'italy-science-business.js',
  'italy-i18n.js',
  'italy-catalog.js',
  'italy-ingested.js',
  /* The V2.1 package. It must load BEFORE the model, because the model reads
     window.ITALY_HANDOFF_V21 at construction time and a family that arrives
     late is a family that silently kept the fixture. */
  'italy-handoff-v21.js',
  'italy-app-model.js',
  /* The meeting build. The snapshot is the intelligence, the labels turn its
     codes into phrases, and the surface is the adapter that presents them.
     They load AFTER the model because the surface reuses the model's own
     CATEGORY_SURFACE / ON_SURFACE / AREA_UI tokens rather than restyling. */
  'meeting-intelligence-snapshot.js',
  'meeting-labels.js',
  'meeting-surface.js',
];

function makeWindow() {
  const store = {};
  const win = {
    localStorage: {
      getItem: (k) => (k in store ? store[k] : null),
      setItem: (k, v) => { store[k] = String(v); },
      removeItem: (k) => { delete store[k]; },
    },
    location: { href: 'file:///portale.html', hash: '', search: '' },
    navigator: { language: 'it-IT', userAgent: 'sintonia-harness' },
    scrollTo() {},
    addEventListener() {},
    removeEventListener() {},
    matchMedia: () => ({ matches: false, addEventListener() {}, removeEventListener() {} }),
    requestAnimationFrame: (fn) => setTimeout(fn, 0),
    setTimeout, clearTimeout, setInterval, clearInterval,
  };
  win.window = win;
  win.globalThis = win;
  return win;
}

function makeDocument() {
  const el = () => ({
    style: {}, dataset: {}, classList: { add() {}, remove() {}, toggle() {}, contains: () => false },
    setAttribute() {}, getAttribute: () => null, removeAttribute() {},
    appendChild(c) { return c; }, removeChild(c) { return c; },
    querySelector: () => null, querySelectorAll: () => [],
    addEventListener() {}, removeEventListener() {},
    children: [], childNodes: [], textContent: '', innerHTML: '',
  });
  return {
    documentElement: Object.assign(el(), { lang: 'it' }),
    head: el(), body: el(),
    createElement: el, createTextNode: (t) => ({ textContent: t }),
    querySelector: () => null, querySelectorAll: () => [],
    addEventListener() {}, removeEventListener() {},
  };
}

/** Load every data file and build ITALY_APP_MODEL. Returns the sandbox window. */
export function loadData({ dir = CLIENT, files = DATA_FILES, quiet = true } = {}) {
  const win = makeWindow();
  const doc = makeDocument();
  const errors = [];
  const ctx = vm.createContext(Object.assign(win, {
    console: quiet ? { log() {}, warn() {}, error() {}, info() {} } : console,
    document: doc,
  }));
  ctx.window = ctx;
  ctx.globalThis = ctx;
  for (const f of files) {
    const p = path.join(dir, f);
    if (!fs.existsSync(p)) { errors.push({ file: f, error: 'missing' }); continue; }
    try {
      vm.runInContext(fs.readFileSync(p, 'utf8'), ctx, { filename: f });
    } catch (e) {
      errors.push({ file: f, error: e.message });
    }
  }
  ctx.__loadErrors = errors;
  return ctx;
}

/* ── the portal's own logic, extracted from portale.html ───────────────────── */

export function readPortal(dir = CLIENT) {
  return fs.readFileSync(path.join(dir, 'portale.html'), 'utf8');
}

/* When set, mount() takes the markup+logic from this file instead of
   client/portale.html. Lets an agent validate a candidate rewrite of one block
   without touching the file every other agent is reading. */
export let PORTAL_OVERRIDE = null;
export function usePortal(file) { PORTAL_OVERRIDE = file || null; }

/** The <script data-dc-script> body, plus the 1-indexed line it starts on. */
export function extractLogic(html) {
  const open = html.indexOf('<script type="text/x-dc" data-dc-script');
  if (open < 0) throw new Error('portale.html: no data-dc-script block found');
  const bodyStart = html.indexOf('>', open) + 1;
  const close = html.indexOf('</script>', bodyStart);
  if (close < 0) throw new Error('portale.html: unterminated data-dc-script block');
  return {
    code: html.slice(bodyStart, close),
    startLine: html.slice(0, bodyStart).split('\n').length,
  };
}

/** The markup template that sits between </style> and the logic script. */
export function extractMarkup(html) {
  const a = html.indexOf('</style>');
  const b = html.indexOf('<script type="text/x-dc" data-dc-script');
  return html.slice(a + 8, b);
}

/**
 * Instantiate the portal's Component class against loaded data.
 * Returns { ctx, instance, vals(state) } where vals() runs renderVals() for a
 * given state patch and returns the props object the markup would consume.
 */
export function mount({ dir = CLIENT, state = {}, portalPath = null } = {}) {
  const ctx = loadData({ dir });
  const src = portalPath || PORTAL_OVERRIDE
    ? fs.readFileSync(portalPath || PORTAL_OVERRIDE, 'utf8')
    : readPortal(dir);
  const { code } = extractLogic(src);

  /* Minimal stand-in for the dc-runtime base class. The portal only uses
     this.state / this.setState / lifecycle-free rendering. */
  const shim = `
    class DCLogic {
      constructor() { this.__listeners = []; }
      setState(patch) {
        const next = typeof patch === 'function' ? patch(this.state) : patch;
        this.state = Object.assign({}, this.state, next);
        return this.state;
      }
    }
  `;
  vm.runInContext(shim + '\n' + code + '\nwindow.__Component = Component;', ctx, {
    filename: 'portale.html#dc-script',
  });

  const Component = ctx.__Component;
  const instance = new Component();
  instance.state = Object.assign({}, instance.state, state);

  return {
    ctx,
    instance,
    AM: ctx.ITALY_APP_MODEL,
    /** Run renderVals() for a state patch. Throws are the caller's to handle. */
    vals(patch = {}) {
      instance.state = Object.assign({}, instance.state, patch);
      return instance.renderVals();
    },
    /** Run renderVals() and capture the failure instead of throwing. */
    tryVals(patch = {}) {
      try { return { ok: true, vals: this.vals(patch) }; }
      catch (e) { return { ok: false, error: e.message, stack: (e.stack || '').split('\n').slice(0, 4).join(' | ') }; }
    },
  };
}

/* ── small shared helpers ─────────────────────────────────────────────────── */

export const pct = (n, d) => (d ? Math.round((n / d) * 1000) / 10 : 0);

/** Share of records where a field is null / undefined / '' / []. */
export function nullRate(records, field) {
  const n = records.length;
  if (!n) return { field, n: 0, filled: 0, nullPct: 100 };
  const filled = records.filter((r) => {
    const v = r && r[field];
    if (v === null || v === undefined || v === '') return false;
    if (Array.isArray(v) && v.length === 0) return false;
    return true;
  }).length;
  return { field, n, filled, nullPct: pct(n - filled, n) };
}
