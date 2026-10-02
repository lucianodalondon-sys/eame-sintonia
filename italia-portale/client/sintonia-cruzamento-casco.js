/* CRUZAMENTO COMERCIAL → CASCO ORIGINAL. So LEITURA e EXIBICAO: nao classifica, nao cruza, nao completa.

   A classe de cada objeto (OPORTUNIDADE · LEAD · SINAL · GAP) e escrita pela Intelligence
   (FAST-CRUZAMENTO-COMERCIAL/v1, CRUZAMENTO-COMERCIAL.json). O casco nao desenha tela nova: entrega os
   objetos JA no formato dos componentes que existiam antes (fichas do Radar, fichas do Radar Futuro, fichas
   do Portafoglio) e um DETALHE auditavel, aberto so quando o usuario clica.

       OPORTUNIDADE  → Radar delle Opportunita (0 = estado vazio pequeno, dentro do mesmo desenho)
       LEAD, SINAL   → Radar Futuro
       GAP           → Portafoglio

   Sem o envelope (sintonia-cruzamento-publicado.js = null) tudo devolve null e o casco fica como estava.
   Envelope que nao confere (classe desconhecida, contagem que nao bate, sem objetos) = recusa inteira.
   NAO_SEI do ficheiro aparece como «non noto» na ficha e com o texto inteiro no detalhe.            */
window.SINTONIA_CRUZAMENTO_CASCO = (function () {
  'use strict';
  var CLASSES = ['OPORTUNIDADE', 'LEAD', 'SINAL', 'GAP'];
  var SUPERFICIE = { meeting: ['OPORTUNIDADE'], radarfuturo: ['LEAD', 'SINAL'], portfolio: ['GAP'] };
  var ROTA = { radar: 'meeting', msignals: 'meeting', mradar: 'meeting' };
  var CAMPOS = ['O_QUE_ACONTECEU', 'CULTURA', 'LOCAL', 'PROBLEMA', 'JANELA', 'PRODUTO_ADAMA', 'AUTORIZACAO_LABEL',
    'POR_QUE_AGORA', 'ACAO_COMERCIAL'];
  var MESES = { it: ['GEN', 'FEB', 'MAR', 'APR', 'MAG', 'GIU', 'LUG', 'AGO', 'SET', 'OTT', 'NOV', 'DIC'],
    en: ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'] };
  var L = {
    it: {
      cls: { OPORTUNIDADE: 'OPPORTUNITÀ', LEAD: 'LEAD', SINAL: 'SEGNALE', GAP: 'LACUNA DI PORTAFOGLIO' },
      grupo: { LEAD: 'LEAD · PISTA COMMERCIALE', SINAL: 'SEGNALI DA SEGUIRE' },
      estado: { LEAD: 'pista commerciale, non ancora opportunità', SINAL: 'da seguire, nessun legame prodotto-uso',
        GAP: 'prodotto ADAMA non trovato', OPORTUNIDADE: 'opportunità confermata' },
      zeroTit: '0 opportunità confermate',
      zeroTxt: 'Nessuna opportunità commerciale ha chiuso prodotto + uso autorizzato + finestra in questa lettura.',
      sper: 'SPERIMENTALE',
      sperTip: 'Lettura sperimentale della Intelligence, non ancora validata per il cliente.',
      naoSei: 'non noto',
      campi: { O_QUE_ACONTECEU: 'Cosa è successo', CULTURA: 'Coltura', LOCAL: 'Luogo del fatto', PROBLEMA: 'Problema',
        JANELA: 'Finestra', PRODUTO_ADAMA: 'Prodotto ADAMA', AUTORIZACAO_LABEL: 'Autorizzazione in etichetta',
        POR_QUE_AGORA: 'Perché ora', ACAO_COMERCIAL: 'Azione commerciale' },
      kWhy: 'PERCHÉ IMPORTA', kMiss: 'COSA MANCA', kWin: 'TEMPISTICA', kNeed: 'BERSAGLIO / NECESSITÀ', kReg: 'REGIONE',
      kProd: 'PRODOTTO TROVATO', kNo: 'NO', kMotivo: 'MOTIVO', kConf: 'COSA MANCA DA CONFERMARE', kCrop: 'COLTURA',
      evidN: 'evidenze', esplora: 'ESPLORA',
      trovato: 'Cosa ha trovato il Sintonia', cambia: 'Cosa cambierebbe la classe', limiti: 'Contro / limiti',
      fonti: 'Fonti indipendenti', bula: 'Etichette', ia: 'lettura dell’IA', evid: 'Evidenze · fonte, documento, estratto',
      unDoc: 'UN SOLO DOCUMENTO', verif: 'DA VERIFICARE', anello: 'Cosa manca per diventare vendita',
      succede: 'Cosa succede', conta: 'Perché conta', azione: 'Cosa si può fare',
      campiL: 'Come è stata costruita questa lettura (campi di lavoro della Intelligence)',
      tec: 'Dettagli tecnici', rimessa: 'lettura', generato: 'generata il', modello: 'modello', era: 'prima era',
      ritorno: { meeting: '← RADAR DELLE OPPORTUNITÀ', radarfuturo: '← RADAR FUTURO', portfolio: '← PORTAFOGLIO' },
      gapTit: 'Lacune di portafoglio',
      gapSub: 'Necessità rilevate per cui non è stato trovato un prodotto ADAMA autorizzato in questa lettura. Il catalogo continua sotto.',
      rfLine: 'lead e segnali della lettura commerciale corrente',
      rfLegend: 'LEAD: pista commerciale con la coltura coperta, ma senza il legame completo prodotto + uso autorizzato + finestra. SEGNALE: fatto da seguire, senza legame con un uso ADAMA. Nessuno dei due è un’opportunità.',
      rifiuto: 'NON SO · la lettura commerciale non ha superato il controllo e non viene mostrata.'
    },
    en: {
      cls: { OPORTUNIDADE: 'OPPORTUNITY', LEAD: 'LEAD', SINAL: 'SIGNAL', GAP: 'PORTFOLIO GAP' },
      grupo: { LEAD: 'LEAD · COMMERCIAL LEAD', SINAL: 'SIGNALS TO FOLLOW' },
      estado: { LEAD: 'commercial lead, not yet an opportunity', SINAL: 'to follow, no product-use link',
        GAP: 'no ADAMA product found', OPORTUNIDADE: 'confirmed opportunity' },
      zeroTit: '0 confirmed opportunities',
      zeroTxt: 'No commercial opportunity closed product + authorised use + window in this reading.',
      sper: 'EXPERIMENTAL',
      sperTip: 'Experimental Intelligence reading, not yet validated for the client.',
      naoSei: 'not known',
      campi: { O_QUE_ACONTECEU: 'What happened', CULTURA: 'Crop', LOCAL: 'Place of the fact', PROBLEMA: 'Problem',
        JANELA: 'Window', PRODUTO_ADAMA: 'ADAMA product', AUTORIZACAO_LABEL: 'Label authorisation',
        POR_QUE_AGORA: 'Why now', ACAO_COMERCIAL: 'Commercial action' },
      kWhy: 'WHY IT MATTERS', kMiss: 'WHAT IS MISSING', kWin: 'TIMING', kNeed: 'TARGET / NEED', kReg: 'REGION',
      kProd: 'PRODUCT FOUND', kNo: 'NO', kMotivo: 'REASON', kConf: 'STILL TO CONFIRM', kCrop: 'CROP',
      evidN: 'evidence', esplora: 'EXPLORE',
      trovato: 'What Sintonia found', cambia: 'What would change the class', limiti: 'Against / limits',
      fonti: 'Independent sources', bula: 'Labels', ia: 'AI reading', evid: 'Evidence · source, document, excerpt',
      unDoc: 'SINGLE DOCUMENT', verif: 'TO VERIFY', anello: 'What is missing to become a sale',
      succede: 'What is happening', conta: 'Why it matters', azione: 'What can be done',
      campiL: 'How this reading was built (Intelligence working fields)',
      tec: 'Technical details', rimessa: 'reading', generato: 'generated', modello: 'model', era: 'previously',
      ritorno: { meeting: '← OPPORTUNITY RADAR', radarfuturo: '← FUTURE RADAR', portfolio: '← PORTFOLIO' },
      gapTit: 'Portfolio gaps',
      gapSub: 'Needs detected for which no authorised ADAMA product was found in this reading. The catalogue continues below.',
      rfLine: 'leads and signals from the current commercial reading',
      rfLegend: 'LEAD: commercial lead with the crop covered, but without the full product + authorised use + window link. SIGNAL: a fact to follow, with no link to an ADAMA use. Neither is an opportunity.',
      rifiuto: 'DON’T KNOW · commercial reading refused:'
    }
  };
  var COR = { OPORTUNIDADE: '#009845', LEAD: '#F5B317', SINAL: '#5CC3EE', GAP: '#E07B39' };
  function T(lang) { return L[lang === 'en' ? 'en' : 'it']; }
  function txt(v) { return v === null || v === undefined || v === '' ? 'NAO_SEI' : String(v); }
  function eNaoSei(v) { return v === null || v === undefined || v === '' || /^\s*NAO[_ ]SEI/i.test(String(v)); }
  /* A ficha e executiva: primeira frase, curta. O texto inteiro fica no detalhe. */
  function curto(v, t, n) {
    if (eNaoSei(v)) return t.naoSei;
    var s = String(v).replace(/\s+/g, ' ').trim();
    var p = s.search(/[.;—](\s|$)/);
    if (p > 12) s = s.slice(0, p);
    n = n || 120;
    return s.length > n ? s.slice(0, n - 1).replace(/\s+\S*$/, '') + '…' : s;
  }
  function val(o, k) { return ((o.CAMPOS || {})[k] || {}).valor; }
  /* Primeira camada: textos que a Intelligence escreveu para o leigo (TITULO_IT, TEXTOS_VISIVEIS_IT).
     Ausentes = o texto antigo. O casco nao traduz nem reescreve. */
  function vis(o, k) { var v = (o.TEXTOS_VISIVEIS_IT || {})[k]; return eNaoSei(v) ? null : v; }
  function tit(o) { return txt(eNaoSei(o.TITULO_IT) ? o.TITULO : o.TITULO_IT); }
  function host(u) { var m = /^https?:\/\/(?:www\.)?([^\/?#]+)/i.exec(String(u || '')); return m ? m[1] : ''; }

  function conferir(env) {
    var f = [];
    var c = env && env.CRUZAMENTO;
    if (!c || typeof c !== 'object') return ['sem CRUZAMENTO'];
    if (!/^[0-9a-f]{64}$/.test(String(env.CRUZAMENTO_SHA256 || ''))) f.push('sem CRUZAMENTO_SHA256');
    if (!Array.isArray(c.OBJETOS) || !c.OBJETOS.length) f.push('sem OBJETOS');
    var n = {};
    (c.OBJETOS || []).forEach(function (o) {
      if (CLASSES.indexOf(o && o.CLASSE) < 0) f.push((o && o.ID) + ': classe desconhecida ' + (o && o.CLASSE));
      else n[o.CLASSE] = (n[o.CLASSE] || 0) + 1;
    });
    var k = c.CONTAGEM || {};
    CLASSES.forEach(function (x) { if ((k[x] || 0) !== (n[x] || 0)) f.push('CONTAGEM ' + x + ' ' + k[x] + ' ≠ ' + (n[x] || 0)); });
    return f;
  }
  function valido(env) { return !!(env && env.CRUZAMENTO) && conferir(env).length === 0; }
  function superficie(view) { var a = ROTA[view] || view; return SUPERFICIE[a] ? a : null; }
  function objetos(env, classes) {
    if (!valido(env)) return [];
    return env.CRUZAMENTO.OBJETOS.filter(function (o) { return classes.indexOf(o.CLASSE) >= 0; });
  }
  function contagem(env, view) {
    var a = superficie(view);
    if (!a || !valido(env)) return null;
    return objetos(env, SUPERFICIE[a]).length;
  }
  /* A data da RODADA, escrita pela Intelligence (REFERENCIA.HOJE; senao GERADO_EM). O casco nao le o
     relogio do navegador: «oggi» = o dia a que esta leitura se refere. */
  function dataDaRodada(env, lang) {
    if (!valido(env)) return null;
    var c = env.CRUZAMENTO;
    var iso = String(((c.REFERENCIA || {}).HOJE) || c.GERADO_EM || '').slice(0, 10);
    var m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(iso);
    if (!m) return null;
    return { iso: iso, rotulo: m[3] + ' ' + MESES[lang === 'en' ? 'en' : 'it'][Number(m[2]) - 1], ano: m[1] };
  }
  function base(o, t) {
    var ev = (o.EVIDENCIAS || []).length;
    return {
      id: txt(o.ID), cruzId: o.ID, cruzClasse: o.CLASSE, classe: o.CLASSE, rotulo: t.cls[o.CLASSE], cor: COR[o.CLASSE],
      titulo: tit(o), crop: curto(val(o, 'CULTURA'), t, 40), region: curto(val(o, 'LOCAL'), t, 44),
      problema: curto(val(o, 'PROBLEMA'), t, 90), janela: curto(val(o, 'JANELA'), t, 90),
      produto: curto(val(o, 'PRODUTO_ADAMA'), t, 90), acao: curto(val(o, 'ACAO_COMERCIAL'), t, 110),
      porque: curto(vis(o, 'PERCHE_CONTA') || val(o, 'O_QUE_ACONTECEU'), t, 130),
      falta: curto(vis(o, 'COSA_MANCA') || o.ELO_QUE_FALTA, t, 130),
      evidN: ev + ' ' + t.evidN, esplora: t.esplora, sper: t.sper, sperTip: t.sperTip
    };
  }
  /* Ficha do Radar Futuro: as mesmas chaves do rfFicha original + as linhas novas (hasCruz). */
  function fichaFuturo(o, lang) {
    var t = T(lang), b = base(o, t), lead = o.CLASSE === 'LEAD';
    return Object.assign(b, {
      acao: t.cls[o.CLASSE], estado: t.estado[o.CLASSE], hasAviso: false, aviso: '',
      classe: b.titulo, hasPode: false, pode: '', hasSensor: false, sensor: '', sensorColor: '#8F8886',
      lacunas: b.evidN,
      acaoBg: lead ? 'rgba(245,179,23,0.14)' : 'rgba(0,160,223,0.14)',
      acaoInk: lead ? '#F5B317' : '#5CC3EE',
      acaoEdge: lead ? 'rgba(245,179,23,0.45)' : 'rgba(0,160,223,0.42)',
      hasCruz: true, kWhy: t.kWhy, kMiss: t.kMiss, kWin: t.kWin, cropRegion: b.crop + ' · ' + b.region
    });
  }
  /* Ficha de lacuna no Portafoglio. */
  function fichaGap(o, lang) {
    var t = T(lang), b = base(o, t);
    return Object.assign(b, { kCrop: t.kCrop, kNeed: t.kNeed, kReg: t.kReg, kProd: t.kProd, kNo: t.kNo,
      kMotivo: t.kMotivo, kConf: t.kConf, motivo: curto(vis(o, 'COSA_MANCA') || o.ELO_QUE_FALTA, t, 120),
      confermare: curto(vis(o, 'AZIONE') || val(o, 'ACAO_COMERCIAL'), t, 120) });
  }
  /* Ficha de OPORTUNIDADE no formato da ficha original do Radar (fascia, icone, titulo, coltura · regione,
     cassa nera do prodotto, ESPLORA). Hoje a Intelligence escreve 0; este caminho existe para o dia em que nao. */
  function fichaRadar(o, lang) {
    var t = T(lang), b = base(o, t), semProd = eNaoSei(val(o, 'PRODUTO_ADAMA'));
    return Object.assign(b, { target: curto(val(o, 'PROBLEMA'), t, 60), geography: b.region, status: t.cls.OPORTUNIDADE,
      publication: t.sper, isActNow: false, notActNow: true, actPill: {},
      cat: { has: true, label: t.cls.OPORTUNIDADE, hasIcon: false, icon: '', ribbon: '#00532A', soft: '#7FD8A6' },
      surfaceDark: '#0B3B22', onChipEdge: 'rgba(0,152,69,0.45)', onRule: '#009845', onInk: '#fff', onBody: '#D8F2E3',
      onMuted: '#9FD6B6', fam: { has: true, n: (o.EVIDENCIAS || []).length }, evid: [{ label: t.evidN, n: (o.EVIDENCIAS || []).length }],
      window: { DEFINED: '', OPEN_NOW: '' }, primaryName: semProd ? '' : b.produto, cardLine: b.produto,
      port: { has: !semProd, name: b.produto, hasMore: false, more: '', hasAi: false, ai: '', isNone: semProd, none: t.naoSei },
      age: { has: false, label: '' } });
  }
  /* O DETALHE: aqui mora a prova (FACT_ID, USE_ID, fonte, trecho, leitura da IA, dados tecnicos). */
  function detalhe(env, id, lang) {
    if (!valido(env)) return null;
    var t = T(lang), c = env.CRUZAMENTO;
    var o = c.OBJETOS.filter(function (x) { return x.ID === id; })[0];
    if (!o) return null;
    var conf = o.CONFERENCIA || {}, cam = o.CAMPOS || {};
    var verificar = ((c.CONFERENCIA_GLOBAL || {}).OBJETOS_COM_VERIFICAR) || [];
    var sup = o.CLASSE === 'OPORTUNIDADE' ? 'meeting' : (o.CLASSE === 'GAP' ? 'portfolio' : 'radarfuturo');
    return {
      id: txt(o.ID), classe: o.CLASSE, rotulo: t.cls[o.CLASSE], cor: COR[o.CLASSE], titulo: tit(o),
      superficie: sup, ritorno: t.ritorno[sup], sper: t.sper, sperTip: t.sperTip,
      cropRegion: curto(val(o, 'CULTURA'), t, 60) + ' · ' + curto(val(o, 'LOCAL'), t, 60),
      temEra: !!o.CLASSE_ANTES && o.CLASSE_ANTES !== o.CLASSE,
      era: t.era + ' ' + (t.cls[o.CLASSE_ANTES] || txt(o.CLASSE_ANTES)) + (o.CANDIDATA_ANTERIOR ? ' (' + o.CANDIDATA_ANTERIOR + ')' : ''),
      unDoc: conf.CRUZAMENTO_DE_UM_SO_DOCUMENTO === true, unDocL: t.unDoc,
      verif: verificar.indexOf(o.ID) >= 0 || (conf.PALAVRAS_VERIFICAR || []).length > 0, verifL: t.verif,
      anelloL: t.anello, anello: txt(vis(o, 'COSA_MANCA') || o.ELO_QUE_FALTA),
      leigo: [[t.succede, vis(o, 'COSA_SUCCEDE')], [t.conta, vis(o, 'PERCHE_CONTA')], [t.azione, vis(o, 'AZIONE')]]
        .filter(function (b) { return b[1]; }).map(function (b) { return { l: b[0], v: String(b[1]) }; }),
      campos: CAMPOS.filter(function (k) { return cam[k]; }).map(function (k) {
        var f = cam[k] || {};
        return { l: t.campi[k], v: eNaoSei(f.valor) ? String(f.valor || '').replace(/^\s*NAO[_ ]SEI\s*—?\s*/i, t.naoSei.toUpperCase() + ' — ') : String(f.valor),
          naoSei: eNaoSei(f.valor), temIa: !!f.INTERPRETACAO_DA_IA, ia: t.ia + ': ' + txt(f.INTERPRETACAO_DA_IA),
          fatos: '' };
      }),
      blocos: [[t.trovato, o.O_QUE_O_SINTONIA_ENCONTROU], [t.cambia, o.O_QUE_MUDARIA_A_CLASSE], [t.limiti, o.CONTRA_OU_LIMITE],
        [t.fonti, (o.ORIGEM || {}).FONTES_INDEPENDENTES], [t.bula, (o.AVISO_DE_FRESCOR_DA_BULA || {}).TEXTO]]
        .filter(function (b) { return b[1]; }).map(function (b) { return { l: b[0], v: txt(b[1]) }; }),
      evidL: t.evid + ' (' + (o.EVIDENCIAS || []).length + ')',
      evid: (o.EVIDENCIAS || []).map(function (e) {
        return { trecho: '«' + txt(e.trecho) + '»', url: txt(e.URL), fonte: host(e.URL) || t.naoSei };
      }),
      camposL: t.campiL, tecL: t.tec,
      tec: t.rimessa + ' ' + txt(env.REMESSA) + ' · ' + t.generato + ' ' + txt(c.GERADO_EM) + ' · ' + t.modello + ' ' + txt(c.MODELO) +
        ' · ' + txt(c.VERSAO) + ' · ' + txt(c.ESTADO) + ' · sha ' + String(env.CRUZAMENTO_SHA256 || '').slice(0, 12) +
        ' · ' + txt(o.ID) + ' · ' + CAMPOS.filter(function (k) { return cam[k]; }).map(function (k) { var f = cam[k];
          return k + ': ' + ((f.FACT_IDs || []).concat(f.USE_IDs || [], f.FENOLOGIA_IDs || []).join(' ') || '-'); }).join(' | ') +
        ' · ' + (o.EVIDENCIAS || []).map(function (e) { return txt(e.SOURCE_ID) + '/' + txt(e.FACT_ID); }).join(' ') +
        (o.DESTINO_FERRAMENTA ? ' · ' + [].concat(o.DESTINO_FERRAMENTA).join(',') : '')
    };
  }
  return { conferir: conferir, valido: valido, superficie: superficie, objetos: objetos, contagem: contagem,
    dataDaRodada: dataDaRodada, fichaFuturo: fichaFuturo, fichaGap: fichaGap, fichaRadar: fichaRadar, detalhe: detalhe, textos: T,
    SUPERFICIE: SUPERFICIE, CLASSES: CLASSES };
})();
