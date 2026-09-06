/* SINTONIA ITALIA · CHE SAFRA E IL PACCHETTO SUL DISCO
   ---------------------------------------------------------------------------
   `build/ITALY-REALITY-HANDOFF-V2.1/` non e versionato: la catena lo rigenera,
   e in questo repository esiste solo lo ZIP STORICO — che il contratto
   canonico nomina come SAFRA VECCHIA (V21-99226fbb90dcdbc2: 37 casi, senza
   MEETING_SURFACE_RULE). Il portale serve invece V21-69bf448ac934a6d9, 43 casi.

   Tre controlli confrontavano il servito con quello zip e chiamavano
   DIVERGENZA la differenza fra due safre. Il peggiore diceva «6 id declassati
   sono mostrati come verificati» — un'accusa grave, e falsa: quei sei
   appartengono al red team di un'altra safra.

       CONFRONTARE DUE RACCOLTI DIVERSI NON MISURA UNA PERDITA.
       MISURA CHE SONO DUE RACCOLTI DIVERSI.

   Questo modulo dice, con una parola sola, se il pacchetto sul disco puo
   servire da termine di paragone. Chi lo interroga smette di inventare un
   risultato quando la risposta e no.
   --------------------------------------------------------------------------- */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const RAIZ = path.resolve(HERE, '..', '..', '..');
export const PACOTE_DIR = path.join(RAIZ, 'build', 'ITALY-REALITY-HANDOFF-V2.1', 'DESIGN-INGEST');
export const CONTRATO = JSON.parse(fs.readFileSync(path.resolve(HERE, '..', 'CANONICAL-PACKAGE-CONTRACT.json'), 'utf8'));

/**
 * ASSENTE      · non c'e pacchetto sul disco (il caso normale: e ignorato da git)
 * SAFRA_VECCHIA· c'e, ma il suo BUILD_ID e uno di quelli che il contratto nomina come vecchi
 * ESTRANEO     · c'e, e il suo BUILD_ID non e ne il canonico ne uno noto
 * CANONICO     · c'e, ed e la stessa safra che il portale serve
 */
export function statoDelPacchetto() {
  const opp = path.join(PACOTE_DIR, 'OPPORTUNITIES.json');
  const man = path.join(PACOTE_DIR, 'APP-MANIFEST.json');
  if (!fs.existsSync(opp)) return { stato: 'ASSENTE', buildId: null, atteso: CONTRATO.EXPECTED_BUILD_ID, dir: PACOTE_DIR };
  const O = JSON.parse(fs.readFileSync(opp, 'utf8'));
  const buildId = O.BUILD_ID || (fs.existsSync(man) ? JSON.parse(fs.readFileSync(man, 'utf8')).BUILD_ID : null);
  const noto = CONTRATO.STALE_KNOWN_BUILD_IDS[buildId];
  const stato = buildId === CONTRATO.EXPECTED_BUILD_ID ? 'CANONICO' : (noto ? 'SAFRA_VECCHIA' : 'ESTRANEO');
  return { stato, buildId, atteso: CONTRATO.EXPECTED_BUILD_ID, perche: noto || null, dir: PACOTE_DIR, records: O.RECORDS || [] };
}

/** La riga sola, e vera, che un controllo deve stampare quando non puo misurare. */
export function perchePuoiNonMisurare(p) {
  const g = CONTRATO.CANONICAL_GENERATOR || {};
  if (p.stato === 'ASSENTE') {
    return `NON MISURATO: il pacchetto canonico non e nel repository (si genera, non si conserva). `
      + `Genera su ${g.LINHAGEM} @ ${String(g.COMMIT || '').slice(0, 7)} e porta ${p.atteso}.`;
  }
  return `NON MISURATO: sul disco c'e ${p.buildId} (${p.perche || 'safra non riconosciuta'}), `
    + `il portale serve ${p.atteso}. Confrontarli misurerebbe la distanza fra due raccolti, non una perdita. `
    + `Genera su ${g.LINHAGEM} @ ${String(g.COMMIT || '').slice(0, 7)}.`;
}
