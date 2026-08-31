// BUILD DO RUNTIME DE APRESENTACAO
//
//   casco/canonical/deploy-v8-closeout   (INTOCADO, so leitura)
//              |
//              v
//   instrumentacao da saida + bundle real congelado
//              |
//              v
//   presentation/runtime/public/
//
// O casco canonico NUNCA e escrito por este script. Ele e lido, conferido
// contra a testemunha, e o resultado sai noutra pasta com SHA proprio.

import { createHash } from 'node:crypto'
import { gunzipSync } from 'node:zlib'
import { readFileSync, writeFileSync, mkdirSync, rmSync, readdirSync, statSync } from 'node:fs'
import { join, dirname, relative, sep } from 'node:path'
import { fileURLToPath } from 'node:url'

import { instrument } from './lib/instrument.mjs'
import { loadDict, auditDict, emitRuntime, LANGS } from './i18n/ui-i18n.mjs'

const HERE = dirname(fileURLToPath(import.meta.url))
// As entradas vem de vendor/ (ver prepare-inputs.mjs). O canonico continua
// intocado: vendor e copia conferida, e o SHA e reconferido logo abaixo.
const CANON = join(HERE, 'vendor')
const OUT = join(HERE, 'public')

const CANONICAL_CASCO_SHA = 'd28f6b5876e2fa28720eb555a8b99a275e56c229ed0ac5c4b07edf89f4e81328'
const WITNESS_SIBLINGS = {
  'support.js': '8fe7df74405f3c55f49b7249c74ea1397e65d07dea2b1bd3b4a489bec2e28cbe',
  'crop-map.js': 'a55c6011e6aadb014b2617c8f5b302d9d2fb4bbfb1ee3e444cad345bbb1614c8',
}
const sha = (b) => createHash('sha256').update(b).digest('hex')
const walk = (d) => readdirSync(d).flatMap(n => {
  const p = join(d, n); return statSync(p).isDirectory() ? walk(p) : [p]
})

// ── 1 · LER E CONFERIR O CASCO CANONICO ────────────────────────────────────
const canonHtml = gunzipSync(readFileSync(join(CANON, 'deploy-index.html.gz')))
const gotCanon = sha(canonHtml)
if (gotCanon !== CANONICAL_CASCO_SHA) {
  throw new Error(`FAIL_CLOSED · casco canonico divergente\n  esperado ${CANONICAL_CASCO_SHA}\n  obtido   ${gotCanon}`)
}
console.log(`OK  casco canonico conferido · ${gotCanon}`)

// ── 2 · BUNDLE REAL ────────────────────────────────────────────────────────
const snap = JSON.parse(readFileSync(join(CANON, 'snapshot.generated.json'), 'utf8'))

// ── 3 · VALIDAR REFERENCIAS (fail-closed) ──────────────────────────────────
const evIds = new Set(Object.keys(snap.EVIDENCE))
for (const o of snap.RAW) {
  if (o.evidenceId && !evIds.has(o.evidenceId)) {
    throw new Error(`FAIL_CLOSED · objeto ${o.id} aponta para evidencia inexistente: ${o.evidenceId}`)
  }
  if (!o.id || !o.type || !o.state) throw new Error(`FAIL_CLOSED · objeto sem id/tipo/estado: ${JSON.stringify(o).slice(0, 120)}`)
  if (!o.prov || !o.prov.COMMIT_SHA) throw new Error(`FAIL_CLOSED · objeto ${o.id} sem PROVENANCE.COMMIT_SHA`)
}
for (const [id, e] of Object.entries(snap.EVIDENCE)) {
  if (!e.commit) throw new Error(`FAIL_CLOSED · evidencia ${id} sem commit de origem`)
  if (e.translated && !e.original) {
    throw new Error(`FAIL_CLOSED · evidencia ${id} tem traducao sem ORIGINAL_TEXT`)
  }
}
// Nenhuma tupla H3 nao-resolvida pode estar promovida a pronta.
const promovidas = snap.RAW.filter(o => o.type === 'comp' && o.state === 'ready')
if (promovidas.length && !snap.hoses.H3.resolved) {
  throw new Error(`FAIL_CLOSED · H3 nao resolvido mas ${promovidas.length} objeto(s) promovido(s) a ATTENTION_READY`)
}
console.log(`OK  referencias validas · ${snap.RAW.length} objetos · ${evIds.size} evidencias`)

// ── 4 · SAIDA LIMPA ────────────────────────────────────────────────────────
rmSync(OUT, { recursive: true, force: true })
mkdirSync(join(OUT, 'data'), { recursive: true })

// ── 5 · ATIVOS: COPIA CONFERIDA DO CANONICO ────────────────────────────────
const emit = (rel, buf, expected) => {
  const got = sha(buf)
  if (expected && got !== expected) {
    throw new Error(`FAIL_CLOSED · SHA-256 divergente em ${rel}\n  esperado ${expected}\n  obtido   ${got}`)
  }
  const dest = join(OUT, rel)
  mkdirSync(dirname(dest), { recursive: true })
  writeFileSync(dest, buf)
}
for (const f of Object.keys(WITNESS_SIBLINGS)) {
  emit(f, readFileSync(join(CANON, f)), WITNESS_SIBLINGS[f])
}
const assetSha = JSON.parse(readFileSync(join(CANON, 'ASSETS-SHA256.json'), 'utf8'))
let nAssets = 0
for (const [rel, meta] of Object.entries(assetSha)) {
  const src = join(CANON, (meta.stored === 'gzip' ? meta.stored_as : rel).split('/').join(sep))
  const raw = readFileSync(src)
  emit(rel, meta.stored === 'gzip' ? gunzipSync(raw) : raw, meta.sha256)
  nAssets++
}
const emitidos = new Set(walk(OUT).map(p => relative(OUT, p).split(sep).join('/')))
const faltando = Object.keys(assetSha).filter(k => !emitidos.has(k))
if (faltando.length) throw new Error(`FAIL_CLOSED · ativos do manifesto que nao sairam: ${faltando.join(', ')}`)
console.log(`OK  ${nAssets} ativos copiados do canonico, byte a byte`)

// ── 6 · BUNDLE + RESOLVEDOR DE IDIOMA ──────────────────────────────────────
//
// Um objeto canonico, varias representacoes. Trocar o idioma NAO cria outro
// objeto: id, estado, datas, evidencia e relacoes sao os mesmos. So o campo
// textual muda — e, quando nao existe representacao no idioma pedido, o
// fallback e DECLARADO, nunca disfarcado de traducao.
const bundleJson = JSON.stringify(snap, null, 1)
writeFileSync(join(OUT, 'data', 'sintonia-eame-snapshot.json'), bundleJson)

const resolver = `
// Resolvedor de representacao textual — H9.
// Ordem: idioma pedido -> EN -> PT -> NO_REPRESENTATION_AVAILABLE.
// A interface sabe que houve fallback: __T_STATE__ registra o que aconteceu.
window.__T_STATE__ = {};
window.__T__ = function (obj, field, lang) {
  var reps = obj && obj.i18n && obj.i18n[field];
  if (!reps) return null;
  var chain = [lang, 'en', 'pt'], used = null, val = null;
  for (var i = 0; i < chain.length; i++) {
    if (chain[i] && reps[chain[i]] != null) { used = chain[i]; val = reps[chain[i]]; break; }
  }
  var key = (obj.id || '?') + '.' + field + '@' + lang;
  if (val == null) {
    window.__T_STATE__[key] = { state: 'NO_REPRESENTATION_AVAILABLE', requested: lang, used: null, fallback: true };
    return null;
  }
  window.__T_STATE__[key] = {
    state: used === lang ? 'REPRESENTATION_IN_REQUESTED_LANGUAGE' : 'TRANSLATION_FALLBACK',
    requested: lang, used: used, fallback: used !== lang
  };
  // Traducao nunca substitui o original em silencio: quando houve fallback, o
  // texto sai marcado com a lingua que realmente esta sendo lida.
  return used === lang ? val : val + '  [' + String(used).toUpperCase() + ' · TRANSLATION_FALLBACK]';
};
`
writeFileSync(join(OUT, 'data', 'sintonia-eame-snapshot.js'),
  'window.__SINTONIA__ = ' + bundleJson + ';\n' + resolver)
const bundleSha = sha(readFileSync(join(OUT, 'data', 'sintonia-eame-snapshot.js')))
console.log(`OK  bundle real gerado · ${(bundleJson.length / 1024).toFixed(0)} KB · sha ${bundleSha.slice(0, 16)}…`)

// ── 7 · INSTRUMENTAR A SAIDA ───────────────────────────────────────────────
// UI CHROME I18N — vocabulario fixo, sem fallback: chave faltando quebra o build.
const dict = loadDict()
const audit = auditDict(dict)
if (audit.faltamObrigatorias.length) {
  throw new Error('FAIL_CLOSED · UI_CHROME_MISSING_KEY obrigatoria: ' + audit.faltamObrigatorias.join(', '))
}
for (const l of LANGS) {
  if (l !== 'pt' && audit.missing[l].length) {
    throw new Error('FAIL_CLOSED · UI_CHROME_MISSING_KEY em ' + l.toUpperCase() + ': ' + audit.missing[l].join(', '))
  }
}
writeFileSync(join(OUT, 'data', 'ui-i18n.js'), emitRuntime(dict))
console.log(`OK  UI chrome i18n · ${audit.total} chaves x 5 idiomas · nenhuma faltando`)

const { html: runtimeHtml, log } = instrument(canonHtml.toString('utf8'))
for (const p of log) console.log(`    patch · ${p.patch}`)
writeFileSync(join(OUT, 'index.html'), runtimeHtml)
const runtimeSha = sha(Buffer.from(runtimeHtml))

// ── 8 · RELATORIO DE COBERTURA ─────────────────────────────────────────────
const rep = {
  CANONICAL_CASCO_SHA, CANONICAL_CASCO_CHANGED: 'NO',
  RUNTIME_INDEX_SHA: runtimeSha,
  REAL_DATA_BUNDLE: 'data/sintonia-eame-snapshot.json',
  REAL_DATA_BUNDLE_SHA: bundleSha,
  SNAPSHOT_SOURCE: 'REAL_FROZEN_DATA',
  SOURCE_BACKEND: 'GITHUB / FROZEN_SNAPSHOT',
  SUPABASE_CONNECTED: 'NO',
  PATCHES_APPLIED: log.length,
  RAW_ROWS_BY_HOSE: {}, CANONICAL_ENTITIES_BY_HOSE: {},
  ...snap.totals,
}
for (const [k, v] of Object.entries(snap.coverage)) {
  rep.RAW_ROWS_BY_HOSE[k] = v.raw_rows
  rep.CANONICAL_ENTITIES_BY_HOSE[k] = v.canonical_entities
}
writeFileSync(join(OUT, 'data', 'coverage-report.json'), JSON.stringify(rep, null, 1))

console.log('\n── COBERTURA ──')
for (const [k, v] of Object.entries(snap.coverage)) {
  console.log(`  ${k} loaded = YES · RAW_ROWS ${v.raw_rows ?? '—'} · CANONICAL_ENTITIES ${v.canonical_entities ?? '—'} · ${v.commit.slice(0, 7)}`)
}
console.log(`\n  ATTENTION_OBJECTS = ${snap.totals.ATTENTION_OBJECTS}`)
console.log(`  EVIDENCE          = ${snap.totals.EVIDENCE}`)
console.log(`  SOURCES           = ${snap.totals.SOURCES}`)
console.log(`  OBSERVATIONS      = ${snap.totals.OBSERVATIONS}`)
console.log(`  H3_PRELIMINARY    = ${snap.totals.H3_PRELIMINARY_COUNT} · PROMOVIDAS = ${snap.totals.H3_PROMOTED_COUNT}`)
console.log(`\nOK  CANONICAL_CASCO_SHA = ${CANONICAL_CASCO_SHA}`)
console.log(`OK  RUNTIME_INDEX_SHA   = ${runtimeSha}`)
console.log('OK  CANONICAL_CASCO_CHANGED = NO')
