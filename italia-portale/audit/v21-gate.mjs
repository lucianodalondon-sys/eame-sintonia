/* SINTONIA ITALIA · O PORTAO DO PACOTE V2.1
   ---------------------------------------------------------------------------
   node audit/v21-gate.mjs

   Duas perguntas sobre o arquivo que o ingest do site gera, feitas ANTES de o
   modelo existir e antes de qualquer tela renderizar:

     1 · sobrou prosa de pesquisa em portugues dentro do que embarcou?
     2 · sobrou token de vocabulario controlado sem rotulo nos dois idiomas?

   POR QUE AQUI, E NAO SO NA REGUA DE RENDER
   ------------------------------------------
   `PT1` ja garante que nenhuma prosa portuguesa chega a um prop renderizado, e
   continua garantindo. Mas ele mede a SAIDA das telas: um campo que nenhuma
   tela le hoje passa por ele calado, e passa a vazar no dia em que alguem
   escrever a tela — ou num `JSON.stringify` de painel de depuracao, que nao e
   tela nenhuma e mostra tudo.

       A REGUA DE RENDER MEDE O QUE SE MOSTRA.
       ESTE PORTAO MEDE O QUE SE CARREGA.

   ENUM NAO E PROSA
   -----------------
   `BLOCO_DA_CULTURA`, `PRAGA_OU_DOENCA` e `ALTA` sao vocabulario controlado
   escrito na lingua de quem construiu o pacote. Nao se traduzem por dicionario:
   traduzem-se por TABELA, e e a tabela que a segunda pergunta cobra. Por isso o
   teste de portugues ignora token sem espaco em maiuscula — e o teste de rotulo
   NAO ignora nenhum.
   --------------------------------------------------------------------------- */
import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { PT_MARKERS } from './lang.mjs';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const CLIENT = path.join(HERE, '..', 'client');

globalThis.window = globalThis.window || {};
await import(path.join(CLIENT, 'italy-handoff-v21.js'));
const H = globalThis.window.ITALY_HANDOFF_V21;
if (!H) { console.error('  window.ITALY_HANDOFF_V21 ausente'); process.exit(1); }

const PT_RE = new RegExp('(^|[^\\p{L}])(' + PT_MARKERS.join('|') + ')([^\\p{L}]|$)', 'iu');
/* Vocabulario controlado: TUDO_ASSIM, sem espaco. Um ID canonico
   (CROP_SUGAR_BEET), um estado (EVIDENCE_DOCUMENTED) ou um enum do pacote
   (BLOCO_DA_CULTURA) tem esta forma; uma frase nao tem. */
const ENUM_RE = /^[A-Z0-9][A-Z0-9_.:+-]*$/;
/* Uma citacao publica original nao se traduz e nao se julga: e a prova. */
const CITACAO = new Set([
  /* MULTIPLE_RESISTANCE riporta il brano della scheda GIRE fra virgolette e lo
     annuncia da sé: «literal: '…'». Il brano scrive «(gruppo B)» e, una virgola
     dopo, «(grupo O)»: un refuso DELLA FONTE. Correggerlo sarebbe riscrivere una
     citazione — falsificare l'evidenza — e contarlo come portoghese spedito
     sarebbe accusare il portale di una colpa che non ha. Il campo entra qui,
     dove stanno gli altri campi di citazione, e non altrove. */
  'MULTIPLE_RESISTANCE', 'MULTIPLE_RESISTANCE_IT', 'MULTIPLE_RESISTANCE_EN',
  'QUOTE_FROM_LABEL', 'CREATIVE_TEXT', 'TEXT_ORIGINAL', 'CITATION',
  'CONTENT_TITLE', 'EXAMPLE_TITLE', 'TITLE', 'BULLETIN_TITLE', 'NAME',
  'PERSON', 'INSTITUTION', 'INSTITUTIONS', 'AUTHOR', 'ORGANIZATION',
  'AUTHORIZATION_HOLDER', 'PUBLISHER', 'EVENT', 'CHANNEL', 'COMPANY', 'PAGE',
  'SPECIES', 'SPECIES_IT', 'FAMILY', 'PRODUCT_NAME', 'ACTIVE_INGREDIENT',
  'ACTIVE_INGREDIENTS', 'PRODUCTS_PROVED', 'CROPS_DECLARED_ON_SITE',
  'PESTS_AND_DISEASES_CITED', 'CROPS_DECLARED', 'MODE_OF_ACTION_DECLARED',
  'DERIVATION_FORMULA', 'GEOGRAPHY_EVIDENCE', 'CATALOG_EVIDENCE',
  'CHANNEL_AUDIENCE_EVIDENCE', 'ROLE_EVIDENCE', 'MARKET', 'LOCATION',
  'ORGANIZER', 'VENUE', 'SECTOR', 'DATE_NOTE', 'DATE_RELATIVE', 'PRICE_RAW',
  'LATEST_OBSERVATION', 'ACCESS_EVIDENCE', 'ITALIAN_REGISTRATIONS',
  'COMMERCIAL_CATALOG_PRODUCTS', 'VERIFIED_LABEL_CROPS', 'PRODUCT_RELATIONSHIPS',
]);

const ptHits = [];
const enums = new Map();

const walk = (v, fam, key, id) => {
  if (typeof v === 'string') {
    if (ENUM_RE.test(v) && !v.includes(' ')) {
      if (!enums.has(v)) enums.set(v, { fam, key, id });
      return;
    }
    if (CITACAO.has(key)) return;
    if (PT_RE.test(v)) ptHits.push({ fam, key, id, text: v.slice(0, 120) });
    return;
  }
  if (Array.isArray(v)) { v.forEach((x) => walk(x, fam, key, id)); return; }
  if (v && typeof v === 'object') {
    for (const k of Object.keys(v)) walk(v[k], fam, k, (v.ID || id));
  }
};

for (const fam of Object.keys(H)) {
  if (!Array.isArray(H[fam])) continue;
  H[fam].forEach((r) => walk(r, fam, null, r.ID));
}

/* ── V2 · O TOKEN QUE VAI A TELA PRECISA DE ROTULO ────────────────────────
   Nem todo texto em maiuscula e um enum a traduzir: AZOXYSTROBIN e o nome de
   uma substancia e CROP_SUGAR_BEET e um id canonico que o modelo resolve pelo
   proprio dicionario. Cobrar rotulo de interface para os dois seria pedir a
   tradução de um nome proprio.

       O QUE PRECISA DE ROTULO E O VOCABULARIO QUE ESTE INGEST INVENTOU
       PARA A TELA — nao todo token que existe no pacote.

   Por isso a lista abaixo e dos CAMPOS cujo valor o portal renderiza como
   estado, e nao de todo campo que contem maiusculas. Cada um deles e um enum
   fechado, medido: se um build futuro acrescentar um valor novo, este teste
   falha no build e nao na tela. */
const CAMPOS_DE_ESTADO = [
  'LINK_STRENGTH', 'TARGET_KIND', 'WEED_GROUP', 'PRODUCT_LINK_STATE',
  'OPPORTUNITY_STATE', 'ARCHETYPE', 'STATUS', 'WINDOW_STATE', 'CONFIDENCE',
  'ACTION_MAP', 'MOA_STATE', 'EU_STATE', 'EU_RENEWAL_STATE', 'CATALOG_STATUS',
  'COMMERCIAL_CONTRACT', 'IDENTITY_STATE', 'IDENTITY_STATUS', 'CROP_STATE',
  'GEOGRAPHY_STATE', 'OBSERVATION_CLASS', 'SERIES_STATE', 'ACTIVE_STATUS',
  'COVERAGE_STATE', 'EXHIBITOR_LIST_STATE', 'TIME_STATE', 'CONTENT_KIND',
  'DATE_PARSE_STATE', 'ACCESS_STATUS', 'CROSSING_TYPE', 'MATERIAL_ROLE',
  'VERIFIED_LABEL_CROPS_STATE', 'GEOGRAPHIC_SCOPE',
];
const i18nSrc = fs.readFileSync(path.join(CLIENT, 'italy-i18n.js'), 'utf8');
const modelSrc = fs.readFileSync(path.join(CLIENT, 'italy-app-model.js'), 'utf8');
const estados = new Map();
const varrer = (v, fam, key, id) => {
  if (typeof v === 'string') {
    if (CAMPOS_DE_ESTADO.includes(key) && /^[A-Z][A-Z0-9_]*$/.test(v) && !estados.has(v)) {
      estados.set(v, { fam, key, id });
    }
    return;
  }
  if (Array.isArray(v)) { v.forEach((x) => varrer(x, fam, key, id)); return; }
  if (v && typeof v === 'object') for (const k of Object.keys(v)) varrer(v[k], fam, k, v.ID || id);
};
for (const fam of Object.keys(H)) {
  if (!Array.isArray(H[fam])) continue;
  H[fam].forEach((r) => varrer(r, fam, null, r.ID));
}
/* Um token COMPOSTO nao e vocabulario: `PARADA_EM_2015` e um estado com um ano
   soldado dentro, e por isso nao pode ter linha de dicionario — uma serie que
   parasse em 2027 imprimiria o portugues cru na tela. O modelo parte os dois no
   adaptador (`seriesState` + `stoppedYear`), e e a PARTICAO que responde por
   ele. A isencao e deliberadamente estreita: um padrao declarado, e a lei que
   o desfaz tem de existir no modelo, senao o token volta a ser cobrado. */
const COMPOSTOS = [
  { re: /^PARADA_EM_\d{4}$/, parteEm: 'seriesState', prova: 'PARADA_EM_' },
];
const semRotulo = [];
for (const [tok, where] of estados) {
  const comp = COMPOSTOS.find((c) => c.re.test(tok));
  if (comp && modelSrc.includes(comp.prova) && modelSrc.includes(comp.parteEm)) continue;
  if (!i18nSrc.includes(tok) && !modelSrc.includes(tok)) semRotulo.push({ tok, ...where });
}

const G = '\x1b[32m', R = '\x1b[31m', X = '\x1b[0m';
const line = (ok, id, title, exp, got) =>
  console.log(`  ${ok ? `${G}PASS${X}` : `${R}FAIL${X}`}  ${id.padEnd(5)} ${title.padEnd(58)} exp ${String(exp).padEnd(6)} got ${got}`);

console.log('');
console.log('  SINTONIA ITALY · V2.1 PACKAGE GATE');
console.log('  ' + '─'.repeat(96));
line(ptHits.length === 0, 'V1', 'No Portuguese research prose was shipped to the browser', 0, ptHits.length);
for (const h of ptHits.slice(0, 12)) console.log(`        ${h.fam}.${h.key} [${h.id}] ${h.text}`);
line(semRotulo.length === 0, 'V2', 'Every shipped state token has a label the portal can render', 0, semRotulo.length);
for (const h of semRotulo.slice(0, 20)) console.log(`        ${h.tok}   (${h.fam}.${h.key})`);
line(!!H.buildId, 'V3', 'The shipped package declares its BUILD_ID', 'set', H.buildId || 'missing');
/* ── V4 · IL PACCHETTO IMBARCATO E PIU VECCHIO DELLA LEGGE CHE LO GOVERNA? ──
   La lista di marcatori in lang.mjs decide quale prosa attraversa il confine,
   quindi e INPUT del file generato quanto lo e il pacchetto V2.1. Misurato il
   2026-09-03: togliere un solo marcatore ambiguo ('epoca', che e italiano
   corrente) ha cambiato 16 famiglie su 26.

   Chi modifica la lista e non rigenera resta con un file che obbedisce a una
   legge abrogata — e nulla si rompe, perche il file e ancora valido. L'unica
   prova che qualcosa non va sarebbe una parola portoghese a schermo, cioe il
   difetto stesso, trovato dal lettore invece che dalla riga.

       SE UN INGRESSO NON LASCIA TRACCIA NELL'ARTEFATTO,
       L'ARTEFATTO NON PUO DIRE DI ESSERE VECCHIO.

   La firma della lista viaggia dentro il file; qui si ricalcola e si confronta. */
const listaAttuale = (() => {
  const src = fs.readFileSync(path.join(HERE, 'lang.mjs'), 'utf8');
  const blocco = src.slice(src.indexOf('export const PT_MARKERS'));
  /* I COMMENTI ESCONO PRIMA DELLE VIRGOLETTE.
     Dentro quel blocco i commenti CITANO i token esclusi di proposito — «'mais'
     e italiano per granoturco» — e leggerli come voci della lista li rimette
     dentro. Le due derivazioni, questa e quella di site_v21_ingest.py, devono
     togliere i commenti allo stesso modo, o la firma non coincidera mai e V4
     chiedera per sempre una rigenerazione che non risolve nulla. */
  const dentro = blocco.slice(blocco.indexOf('['), blocco.indexOf(']'))
    .replace(/\/\*[\s\S]*?\*\//g, ' ')
    .replace(/\/\/[^\n]*/g, ' ');
  return [...dentro.matchAll(/'([^']+)'/g)].map((m) => m[1]);
})();
const assinaturaAtual = crypto.createHash('sha256')
  .update(listaAttuale.join('\n'), 'utf8').digest('hex').slice(0, 16);
const assinaturaOk = H.languageGate === assinaturaAtual;
line(assinaturaOk, 'V4', 'The shipped package was built with the CURRENT language gate',
  assinaturaAtual, H.languageGate || 'not stamped');
if (!assinaturaOk) console.log('        rebuild with: python3 scripts/site_v21_ingest.py');
console.log('  ' + '─'.repeat(96));
console.log(`  state tokens shipped: ${estados.size}`);
console.log('');
process.exit(ptHits.length === 0 && semRotulo.length === 0 && H.buildId && assinaturaOk ? 0 : 1);
