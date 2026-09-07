/* SINTONIA ITALY · SUPERFICIE VISIVEL
   ---------------------------------------------------------------------------
   A regra desta regua e uma so, e vem da missao que a mandou existir:

       VALUE_EXISTS = YES  e  VISIBLE = NO   ->  NAO ESTA INTEGRADO.

   «Chegou ao motor» nao e integracao. Integracao e o leitor CONSEGUIR VER. Um
   ficheiro que viaja em cada carregamento e que nenhuma linha de codigo le nao
   e inteligencia integrada: e peso, e o peso nao aparece em contagem nenhuma.

   Por isso aqui nao se conta o que EXISTE — conta-se o que uma superficie
   DESENHA, montando o portal de verdade e lendo o que a marcacao consome.

       CONTAR O QUE EXISTE MEDE O PACOTE.
       CONTAR O QUE SE DESENHA MEDE O PRODUTO.

   Cada familia declara TRES numeros e nao dois: quantos o modelo tem, quantos
   a primeira chegada mostra, e quantos ficam ALCANCAVEIS com uma interacao. As
   tres sao diferentes, e confundi-las foi exactamente como este portal chegou
   a ter 44 fichas de Radar Futuro sem porta nenhuma.
   --------------------------------------------------------------------------- */
import { mount, loadData } from './lib/harness.mjs';

const ESC = String.fromCharCode(27);
const C = { g: ESC + '[32m', r: ESC + '[31m', y: ESC + '[33m', d: ESC + '[2m', o: ESC + '[0m' };

/* UMA MONTAGEM POR MEDICAO. `mount()` acumula estado entre chamadas, e uma
   medicao contaminada e pior do que nenhuma: parece um numero. */
const vals = (state) => mount({ state }).instance.renderVals();
const D = loadData();
const AM = D.window.ITALY_APP_MODEL;
const CASA = D.window.ITALY_CASA || {};
const coll = (k) => (AM.collections[k] ? AM.collections[k].records : []);
const n = (k) => coll(k).length;

/* O que o conjunto das fichas chega a NOMEAR, e o que chega a DECLARAR.
   Nao sao a mesma coisa e nao se somam: um material citado por tres fichas
   continua a ser um material, e o universo de uma coppia conta-se por coppia
   e nao por ficha. Contar linhas em vez de entidades inflaria a resposta. */
function alcanceDasFichas() {
  const casos = vals({ view: 'meeting' }).meetingCases.map((c) => c.id);
  const sci = new Set(), voz = new Set();
  const porCoppia = new Map();
  let comSci = 0, comVoz = 0, comLugar = 0;
  for (const id of casos) {
    const b = vals({ view: 'mcase', mCaseId: id }).mcBeyond;
    if (!b) continue;
    if (b.hasSci) comSci++;
    if (b.hasVoice) comVoz++;
    if ((b.sciPlaces || []).some((p) => p.known)) comLugar++;
    for (const r of b.sciRows || []) sci.add(r.title);
    for (const r of b.voiceRows || []) voz.add(r.title);
    if (b.paired) porCoppia.set(b.pair, { sci: b.sciN, voz: b.voiceN });
  }
  let uSci = 0, uVoz = 0;
  for (const v of porCoppia.values()) { uSci += v.sci; uVoz += v.voz; }
  return { casos: casos.length, sciMostrados: sci.size, vozMostrados: voz.size,
    sciAlcancavel: uSci, vozAlcancavel: uVoz, comSci, comVoz, comLugar,
    coppie: porCoppia.size };
}

const F = alcanceDasFichas();
const vMeeting = vals({ view: 'meeting' });
const vFuture = vals({ view: 'future' });
const vScience = vals({ view: 'science' });
const vComp = vals({ view: 'competitors' });
const vPort = vals({ view: 'portfolio' });

const tipoNoArquivo = (t) => coll('archive').filter((r) => (r.type || r.kind) === t).length;
const RF = CASA.RADAR_FUTURO || {};

/* ══ UMA SUPERFICIE SEM ROTA NAO E UMA SUPERFICIE ═════════════════════════════
   Os 44 do Radar Futuro estavam DESENHADOS em `casa.html` — e invisiveis, porque
   nenhuma rota do portal la chegava. Uma regua que contasse so o desenho teria
   dito VISIVEL sobre o defeito exacto que esta missao veio corrigir.

       CONTAR O DESENHO SEM CONTAR A PORTA MEDE UMA SALA MURADA.

   Por isso a rota mede-se: a barra tem de levar a voz, e o numero da voz tem de
   ser o do dono. Sem isso o visivel e ZERO, por mais linhas que a tabela tenha. */
const vozNaBarra = (() => {
  const n0 = RF.RENDERIZAVEIS;
  return (vals({ view: 'meeting' }).navEvidence || [])
    .some((v) => v && v.count === n0 && typeof n0 === 'number');
})();

const LINHAS = [
  {
    familia: 'OPPORTUNITIES',
    modelo: n('opportunities'),
    rota: '#meeting  ->  ficha (mcase)',
    visivel: vMeeting.meetingCases.length,
    alcancavel: AM.counts.upstreamOpportunities,
    componente: 'sc-for meetingCases · isMcase',
    nota: 'a lei de relevancia ADAMA parte 43 em 13 + 21 + 8 + 1; as duas outras populacoes '
      + 'tem entrada propria no fundo do radar',
  },
  {
    familia: 'FUTURE_RADAR',
    modelo: RF.RENDERIZAVEIS || 0,
    rota: vozNaBarra ? 'menu «Radar Futuro» -> casa.html#radar-futuro' : 'NENHUMA ROTA DO PORTAL',
    visivel: vozNaBarra ? (RF.REGISTRO || []).length : 0,
    alcancavel: vozNaBarra ? (RF.REGISTRO || []).length : 0,
    componente: vozNaBarra ? 'navEvidence «Radar Futuro» -> casa.html ledgerHtml()'
      : 'casa.html ledgerHtml() (desenhado, e sem porta)',
    nota: 'nao esta no pacote V2.1: o dono e italy-casa.js, gerado de '
      + 'IT-FUTURO-HANDOFF-LINHA-B-V1.json. 12 dos 13 campos obrigatorios do cartao NAO viajam '
      + '— o registo mostra estado, accao, portfolio e a CONTAGEM das lacunas',
  },
  {
    familia: 'SIGNAL_ARCHIVE',
    modelo: n('futureSignals'),
    rota: '#future',
    visivel: (vFuture.visibleSignals || []).length,
    alcancavel: (vFuture.visibleSignals || []).length,
    componente: 'sc-for visibleSignals · isSignal',
    nota: 'populacao distinta do Radar Futuro, e agora com rota para ela',
  },
  {
    familia: 'TRANSCRIPTS',
    modelo: n('transcripts'),
    rota: '#meeting -> ficha -> «Voce tecnica»',
    visivel: F.vozMostrados,
    alcancavel: F.vozAlcancavel,
    componente: 'mcBeyond.voiceRows',
    nota: F.comVoz + ' das ' + F.casos + ' fichas tem transcricao para a sua coppia; as outras '
      + 'declaram o silencio. TRANSCRIPT_USED_AS_EVIDENCE = false em 184/184, e a ficha di-lo',
  },
  {
    familia: 'SCIENCE',
    modelo: n('scienceRecords') + n('scienceCorpus'),
    rota: '#science  ·  ficha -> «Scienza»',
    visivel: (vScience.records || []).length + F.sciMostrados,
    alcancavel: (vScience.records || []).length + F.sciAlcancavel,
    componente: 'sc-for records (isScience) · mcBeyond.sciRows',
    nota: '88 publicados no ecra da ciencia, mais o corpus de ' + n('scienceCorpus')
      + ' lido pela ficha; os 88 sao SUBCONJUNTO do corpus e nao um segundo universo',
  },
  {
    familia: 'ADS_TEMPORAL',
    modelo: coll('competitorActivities').filter((r) => r.hasDate).length,
    rota: '#competitors  ·  ficha -> «Concorrenza»',
    visivel: coll('competitorActivities').filter((r) => r.isActive === true).length,
    alcancavel: coll('competitorActivities').filter((r) => r.hasDate).length,
    componente: 'compStrip · feedGroups · mcBeyond (attive / storico)',
    nota: 'NAO e familia do pacote: o tempo do anuncio viaja DENTRO de competitorActivities '
      + '(startDate / endDate / isActive). HISTORICO DE ANUNCIO NAO E ACTIVO, e as duas '
      + 'contagens estao separadas onde aparecem',
  },
  {
    familia: 'FACT_TIME_PLACE',
    modelo: coll('transcripts').filter((r) => r.factCountry).length
      + coll('scienceCorpus').filter((r) => r.countryOfFact).length,
    rota: 'ficha -> «Luogo del fatto» em cada linha',
    visivel: F.comLugar,
    alcancavel: F.comLugar,
    componente: 'mcBeyond.sciPlaces · sciRows[].place · voiceRows[].place',
    nota: 'FACT-TIME-PLACE-V1.json esta declarado FORA em site_v21_ingest.py: a lei nao viaja '
      + 'num agregado, viaja NOS REGISTOS. Aqui mede-se se ela CHEGA AO ECRA — a metade que faltava',
  },
  {
    familia: 'FIELD_SIGNALS',
    modelo: n('currentFieldSignals'),
    rota: '#archive (tipo FIELD_SIGNAL)',
    visivel: tipoNoArquivo('FIELD_SIGNAL'),
    alcancavel: tipoNoArquivo('FIELD_SIGNAL'),
    componente: 'visibleArchive · archiveTypeChips',
    nota: 'nao tem ecra proprio; entra no indice do arquivo com o seu tipo declarado',
  },
  {
    familia: 'COMPETITOR_ACTIVITIES',
    modelo: n('competitorActivities'),
    rota: '#competitors',
    visivel: (vComp.feedGroups || []).reduce((s, g) => s + ((g.items || []).length), 0),
    alcancavel: vComp.compTotal || 0,
    componente: 'sc-for feedGroups/g.items · galleryItems · eventCards',
    nota: 'a primeira pagina mostra 12; o resto abre-se no mesmo ecra',
  },
  {
    familia: 'PRODUCT_RELATIONSHIPS',
    modelo: n('productRelationships'),
    rota: '#portfolio -> produto',
    visivel: 0,
    alcancavel: n('productRelationships'),
    componente: 'pd.verified · pd.checkNeeded · pd.related · pd.rejected (isProduct)',
    nota: 'nenhuma relacao se ve na lista do portfolio; todas se veem na ficha do produto que as tem',
  },
];

/* A ficha do produto e a unica prova de que as relacoes se veem: mede-se, nao
   se afirma. E mede-se em VARIOS produtos, porque o primeiro da lista pode nao
   ter relacao nenhuma — e um zero medido no produto errado nao e um zero da
   familia, e o erro mais facil desta tabela.

       UMA SONDA NUM SO SITIO NAO MEDE UMA FAMILIA. MEDE UM SITIO. */
(() => {
  const itens = ((vPort.port && vPort.port.items) || []).slice(0, 12);
  let melhor = 0, comAlguma = 0, nome = '';
  for (const item of itens) {
    const v = vals({ view: 'product', productId: item.id || item.name });
    const pd = v.pd || {};
    const somam = ['verified', 'checkNeeded', 'related', 'rejected']
      .reduce((acc, k) => acc + ((pd[k] || []).length), 0);
    if (somam > 0) comAlguma++;
    if (somam > melhor) { melhor = somam; nome = item.name || item.id; }
  }
  const linha = LINHAS.find((l) => l.familia === 'PRODUCT_RELATIONSHIPS');
  linha.visivel = melhor;
  linha.nota += ' (sondados ' + itens.length + ' produtos: ' + comAlguma
    + ' mostram relacoes, o maior e ' + nome + ' com ' + melhor + ' linhas)';
})();

/* ── o veredicto ──────────────────────────────────────────────────────────── */
/* A LEI MORA AQUI, E SO AQUI. `checks.mjs` importa esta funcao em vez de
   reimplementar a regra: duas copias da mesma lei divergem a terceira vez que
   alguem mexe numa, e a que diverge em silencio e sempre a que nao falha. */
const estado = (l) => {
  if (!l.modelo) return 'SEM_MATERIA';
  if (!l.visivel && !l.alcancavel) return 'INVISIVEL';
  if (!l.visivel) return 'ALCANCAVEL';
  if (l.alcancavel < l.modelo) return 'VISIVEL_PARCIAL';
  return 'VISIVEL';
};

export function medirSuperficie() {
  return LINHAS.map((l) => Object.assign({ estado: estado(l) }, l));
}
export const INVISIVEIS = LINHAS.filter((l) => estado(l) === 'INVISIVEL').map((l) => l.familia);

/* Importado por `checks.mjs`, esta regua nao imprime tabela nenhuma. */
const DIRECTO = process.argv[1] && process.argv[1].endsWith('superficie-visivel.mjs');
if (!DIRECTO) { /* silencio */ } else {
console.log('');
console.log('  SINTONIA · SUPERFICIE VISIVEL');
console.log('  ' + '-'.repeat(112));
console.log('  ' + 'FAMILY'.padEnd(23) + 'IN_MODEL'.padStart(9) + '  ' + 'VISIBLE'.padStart(8)
  + '  ' + 'REACHABLE'.padStart(9) + '  ' + 'STATUS'.padEnd(17) + 'ROUTE');
console.log('  ' + '-'.repeat(112));
const maus = [];
for (const l of LINHAS) {
  const st = estado(l);
  if (st === 'INVISIVEL') maus.push(l.familia);
  const cor = st === 'INVISIVEL' ? C.r : st === 'VISIVEL' ? C.g : C.y;
  console.log('  ' + l.familia.padEnd(23) + String(l.modelo).padStart(9) + '  '
    + String(l.visivel).padStart(8) + '  ' + String(l.alcancavel).padStart(9) + '  '
    + cor + st.padEnd(17) + C.o + l.rota);
  console.log('  ' + C.d + ' '.repeat(23) + l.componente + C.o);
  console.log('  ' + C.d + ' '.repeat(23) + l.nota + C.o);
}
console.log('  ' + '-'.repeat(112));
console.log('  ' + F.casos + ' fichas · ' + F.coppie + ' coppie distintas · ' + F.comSci
  + ' com ciencia · ' + F.comVoz + ' com voce tecnica · ' + F.comLugar + ' com luogo del fatto');
const ok = maus.length === 0;
console.log('  ' + (ok ? C.g + 'PASS' + C.o : C.r + 'FAIL' + C.o)
  + ' · VALUE_EXISTS=YES com VISIBLE=NO: ' + (ok ? 'nenhuma familia' : maus.join(', ')));
console.log('');
process.exit(ok ? 0 : 1);
}
