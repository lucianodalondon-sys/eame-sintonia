// PASSO 1 (local, exige Git) — materializa as ENTRADAS do build.
//
// A Vercel nao recebe o repositorio: ela recebe so a pasta de root do projeto.
// Como o build derivado precisa (a) do casco canonico e (b) dos freezes lidos
// por `git show`, este passo copia essas entradas para vendor/ uma unica vez.
//
// vendor/ NAO e uma segunda fonte da verdade: cada byte e conferido contra o
// mesmo SHA do canonico, aqui e de novo no build. Se o canonico mudar e o
// vendor nao, o build quebra — que e o comportamento desejado.

import { createHash } from 'node:crypto'
import { readFileSync, writeFileSync, mkdirSync, rmSync, cpSync } from 'node:fs'
import { join, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'
import { buildSnapshot } from './lib/snapshot.mjs'

const HERE = dirname(fileURLToPath(import.meta.url))
const CANON = join(HERE, '..', '..', 'casco', 'canonical', 'deploy-v8-closeout')
const VENDOR = join(HERE, 'vendor')
const CANONICAL_CASCO_SHA = 'd28f6b5876e2fa28720eb555a8b99a275e56c229ed0ac5c4b07edf89f4e81328'
const sha = (b) => createHash('sha256').update(b).digest('hex')

rmSync(VENDOR, { recursive: true, force: true })
mkdirSync(VENDOR, { recursive: true })

// 1 · casco canonico, ainda gzipado, exatamente como esta no repositorio
for (const f of ['deploy-index.html.gz', 'support.js', 'crop-map.js', 'ASSETS-SHA256.json']) {
  cpSync(join(CANON, f), join(VENDOR, f))
}
cpSync(join(CANON, '_ds'), join(VENDOR, '_ds'), { recursive: true })
cpSync(join(CANON, 'assets'), join(VENDOR, 'assets'), { recursive: true })

// 2 · confere que a copia ainda e o casco medido
const { gunzipSync } = await import('node:zlib')
const got = sha(gunzipSync(readFileSync(join(VENDOR, 'deploy-index.html.gz'))))
if (got !== CANONICAL_CASCO_SHA) {
  throw new Error(`FAIL_CLOSED · vendor divergente do canonico\n  esperado ${CANONICAL_CASCO_SHA}\n  obtido   ${got}`)
}

// 3 · snapshot real, gerado a partir dos commits congelados
const snap = buildSnapshot()
writeFileSync(join(VENDOR, 'snapshot.generated.json'), JSON.stringify(snap, null, 1))

console.log(`OK  vendor pronto · casco ${got.slice(0, 16)}…`)
console.log(`OK  snapshot gerado · ${snap.RAW.length} objetos · ${Object.keys(snap.EVIDENCE).length} evidencias`)
for (const [k, v] of Object.entries(snap.coverage)) {
  console.log(`    ${k} · RAW_ROWS ${v.raw_rows ?? '—'} · CANONICAL_ENTITIES ${v.canonical_entities ?? '—'} · ${v.commit.slice(0, 7)}`)
}
