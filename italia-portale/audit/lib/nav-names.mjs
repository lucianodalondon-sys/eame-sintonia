/* SINTONIA ITALIA · I NOMI DELLE VOCI DI MENU, LETTI DAL DIZIONARIO
   ---------------------------------------------------------------------------
   Sei file di audit portavano gli stessi dieci nomi scritti a mano. Quando
   `navFuture` e `navSources` sono diventati «Archivio segnali V21» e
   «Archivio fonti V21», nessuno dei sei se ne e accorto: hanno smesso di
   trovare le due voci e hanno continuato a dichiarare un risultato.

       UNA TAPPA CHE NON SI TROVA NON E UNA TAPPA CHE FALLISCE.
       E UNA TAPPA CHE NESSUNO GUARDA PIU — e il conto finale non lo dice.

   Misurato al momento della correzione: browser.mjs perdeva 4 schermate,
   browser-deep 4, responsive 8 su 40, mobile 4 su 40 («VACUO: o portao nao
   chegou a medir o que diz medir»).

   Il dizionario e gia sorvegliato — MK3 lega ogni chiave che il markup usa, I5
   prova che l'italiano e italiano — quindi leggerlo qui non toglie una guardia:
   sposta soltanto il nome dove il portale lo tiene davvero.

   `navName()` ESPLODE se una chiave manca, invece di restituire undefined e
   lasciare che il chiamante cerchi «undefined» nella pagina.
   --------------------------------------------------------------------------- */
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const CLIENT = path.resolve(HERE, '..', '..', 'client');

/* DUE DIZIONARI, PERCHE IL PORTALE NE LEGGE DUE. Nove voci vengono da
   `SINTONIA_I18N`; la voce del radar viene da `MEETING_LABELS`, che tiene le
   frasi della superficie della riunione. Chi cerca un nome lo cerca dove il
   portale lo cerca — mai in una terza copia. */
const load = (file) => {
  const ctx = { document: undefined };
  ctx.window = ctx; ctx.globalThis = ctx;
  vm.createContext(ctx);
  vm.runInContext(fs.readFileSync(path.join(CLIENT, file), 'utf8'), ctx, { filename: file });
  return ctx;
};
const I18N_CTX = load('italy-i18n.js');
const LABELS_CTX = load('meeting-labels.js');
export const I18N = I18N_CTX.SINTONIA_I18N;
export const LABELS = LABELS_CTX.MEETING_LABELS;
if (!I18N) throw new Error('nav-names: italy-i18n.js non ha definito SINTONIA_I18N');
if (!LABELS) throw new Error('nav-names: meeting-labels.js non ha definito MEETING_LABELS');

export function navName(lang, key) {
  const v = (I18N[lang] || {})[key] || LABELS.get(key, lang);
  if (!v) throw new Error(`nav-names: nessun dizionario ha la chiave «${key}» in «${lang}»`);
  return v;
}

/* Le dieci voci del menu, nell'ordine in cui la barra le disegna. La voce della
   casa (`casaCurrentOpps`) non e qui: apre una PAGINA, non una vista, e chi
   fa il giro dentro il guscio non deve uscirne. */
export const NAV_KEYS = ['navMeeting', 'navFuture', 'navWindows', 'navMarket', 'navPortfolio',
  'navVoices', 'navCompetitors', 'navScience', 'navArchive', 'navSources'];

/** I dieci nomi in ordine, per una lingua. */
export const navList = (lang) => NAV_KEYS.map((k) => navName(lang, k));

/** La mappa con le chiavi corte che gli audit usano fra loro. */
export const navMap = (lang) => ({
  home: navName(lang, 'navMeeting'), future: navName(lang, 'navFuture'),
  windows: navName(lang, 'navWindows'), market: navName(lang, 'navMarket'),
  portfolio: navName(lang, 'navPortfolio'), voci: navName(lang, 'navVoices'),
  competitor: navName(lang, 'navCompetitors'), science: navName(lang, 'navScience'),
  archive: navName(lang, 'navArchive'), sources: navName(lang, 'navSources'),
  back: lang === 'en' ? 'Back' : 'Indietro',
});
