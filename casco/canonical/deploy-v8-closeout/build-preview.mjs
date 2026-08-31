// Build de Preview do CASCO V8 FINAL para a Vercel.
//
// NAO gera casco. NAO edita casco. A unica transformacao aplicada e:
//
//     deploy-index.html.gz  --gunzip-->  public/index.html
//
// Todo o resto e copia byte a byte. Cada byte que sai daqui e conferido por
// SHA-256 contra a testemunha commitada; se um unico byte divergir, o build
// falha e a Vercel nao publica.
//
// A testemunha fica gzipada no repositorio porque o antivirus do ambiente de
// origem prende o .html depois da escrita (ver docs/implementation/V8-RECEPTOR-CLOSEOUT.md).

import { createHash } from 'node:crypto'
import { gunzipSync } from 'node:zlib'
import { readFileSync, writeFileSync, mkdirSync, rmSync, readdirSync, statSync } from 'node:fs'
import { join, dirname, relative, sep } from 'node:path'
import { fileURLToPath } from 'node:url'

const HERE = dirname(fileURLToPath(import.meta.url))
const OUT = join(HERE, 'public')

// SHAs publicados em docs/implementation/V8-RECEPTOR-CLOSEOUT.md secao 1 e 9.
const WITNESS = {
  'index.html': 'd28f6b5876e2fa28720eb555a8b99a275e56c229ed0ac5c4b07edf89f4e81328',
  'support.js': '8fe7df74405f3c55f49b7249c74ea1397e65d07dea2b1bd3b4a489bec2e28cbe',
  'crop-map.js': 'a55c6011e6aadb014b2617c8f5b302d9d2fb4bbfb1ee3e444cad345bbb1614c8',
}

const sha = (buf) => createHash('sha256').update(buf).digest('hex')

const emit = (rel, buf, expected) => {
  const got = sha(buf)
  if (expected && got !== expected) {
    throw new Error(`SHA-256 divergente em ${rel}\n  esperado ${expected}\n  obtido   ${got}`)
  }
  const dest = join(OUT, rel)
  mkdirSync(dirname(dest), { recursive: true })
  writeFileSync(dest, buf)
  return got
}

const walk = (dir) => {
  const out = []
  for (const name of readdirSync(dir)) {
    const p = join(dir, name)
    if (statSync(p).isDirectory()) out.push(...walk(p))
    else out.push(p)
  }
  return out
}

rmSync(OUT, { recursive: true, force: true })
mkdirSync(OUT, { recursive: true })

// 1 · o casco: unica transformacao do build
const index = gunzipSync(readFileSync(join(HERE, 'deploy-index.html.gz')))
emit('index.html', index, WITNESS['index.html'])

// 2 · runtime e componente: copia pura
for (const f of ['support.js', 'crop-map.js']) {
  emit(f, readFileSync(join(HERE, f)), WITNESS[f])
}

// 3 · design system e imagens: copia pura, conferida contra ASSETS-SHA256.json.
//     Ativos com "stored": "gzip" foram guardados comprimidos pelo mesmo motivo do
//     casco — o antivirus do ambiente de origem remove o arquivo depois da escrita.
const assetSha = JSON.parse(readFileSync(join(HERE, 'ASSETS-SHA256.json'), 'utf8'))
let n = 0
for (const [rel, meta] of Object.entries(assetSha)) {
  const src = join(HERE, (meta.stored === 'gzip' ? meta.stored_as : rel).split('/').join(sep))
  const raw = readFileSync(src)
  emit(rel, meta.stored === 'gzip' ? gunzipSync(raw) : raw, meta.sha256)
  n++
}

// nenhum arquivo pode ter entrado de carona nem ficado para tras
const naPasta = ['_ds', 'assets'].flatMap((r) =>
  walk(join(HERE, r)).map((p) => relative(HERE, p).split(sep).join('/').replace(/\.gz$/, '')),
)
const extra = naPasta.filter((k) => !(k in assetSha))
if (extra.length) throw new Error(`ativo fora do manifesto: ${extra.join(', ')}`)
const emitido = new Set(walk(OUT).map((p) => relative(OUT, p).split(sep).join('/')))
const faltando = Object.keys(assetSha).filter((k) => !emitido.has(k))
if (faltando.length) throw new Error(`ativos do manifesto que nao sairam: ${faltando.join(', ')}`)

console.log(`OK  index.html + support.js + crop-map.js + ${n} ativos  ->  public/`)
console.log(`OK  index.html sha256 = ${WITNESS['index.html']}`)
