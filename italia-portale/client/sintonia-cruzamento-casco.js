/* CRUZAMENTO COMERCIAL → CASCO. So LEITURA e EXIBICAO: nao classifica, nao cruza, nao completa.

   A classe de cada objeto (OPORTUNIDADE · LEAD · SINAL · GAP) e escrita pela Intelligence
   (FAST-CRUZAMENTO-COMERCIAL/v1, CRUZAMENTO-COMERCIAL.json da remessa). O casco so a usa para escolher a
   SUPERFICIE que ja existe:

       OPORTUNIDADE  → Radar delle Opportunita (hoje 0, e a tela diz porque)
       SINAL, LEAD   → Radar Futuro (o LEAD com o seu selo, nunca verde de oportunidade)
       GAP           → Portafoglio

   Sem o envelope (Production: sintonia-cruzamento-publicado.js = null) devolve null e o casco fica como estava.
   Envelope que nao confere (classe desconhecida, contagem que nao bate, sem objetos) = recusa inteira: nenhuma
   superficie desenha parte de um cruzamento. NAO SEI do ficheiro aparece como NAO SEI.            */
window.SINTONIA_CRUZAMENTO_CASCO = (function () {
  'use strict';
  var CLASSES = ['OPORTUNIDADE', 'LEAD', 'SINAL', 'GAP'];
  var SUPERFICIE = { meeting: ['OPORTUNIDADE'], radarfuturo: ['SINAL', 'LEAD'], portfolio: ['GAP'] };
  var ROTA = { radar: 'meeting', msignals: 'meeting', mradar: 'meeting' };
  var CAMPOS = ['O_QUE_ACONTECEU', 'CULTURA', 'LOCAL', 'PROBLEMA', 'JANELA', 'PRODUTO_ADAMA', 'AUTORIZACAO_LABEL',
    'POR_QUE_AGORA', 'ACAO_COMERCIAL'];
  var L = {
    it: {
      faixa: 'CRUZAMENTO COMMERCIALE · SPERIMENTALE · RISULTATO MARCATO «NON PER IL CLIENTE» DALLA INTELLIGENCE',
      cls: { OPORTUNIDADE: 'OPPORTUNITÀ', LEAD: 'LEAD · PISTA COMMERCIALE, NON OPPORTUNITÀ', SINAL: 'SEGNALE', GAP: 'GAP DI PORTAFOGLIO' },
      titolo: { meeting: 'Opportunità confermate dal cruzamento commerciale', radarfuturo: 'Segnali e lead del cruzamento commerciale',
        portfolio: 'Gap di portafoglio dal cruzamento commerciale' },
      zeroOpp: '0 opportunità chiuse in questa rimessa.',
      perche: 'Perché 0: il cruzamento ha riclassificato le candidate precedenti — nessuna ha chiuso prodotto ADAMA autorizzato × problema × finestra.',
      vuoto: 'Nessun oggetto di questa classe in questa rimessa.',
      era: 'prima del cruzamento era', campi: { O_QUE_ACONTECEU: 'Cosa è successo', CULTURA: 'Coltura', LOCAL: 'Luogo del fatto',
        PROBLEMA: 'Problema', JANELA: 'Finestra', PRODUTO_ADAMA: 'Prodotto ADAMA', AUTORIZACAO_LABEL: 'Autorizzazione in etichetta',
        POR_QUE_AGORA: 'Perché ora', ACAO_COMERCIAL: 'Azione commerciale' },
      trovato: 'Cosa ha trovato il Sintonia', anello: 'Cosa manca per diventare vendita', cambia: 'Cosa cambierebbe la classe',
      limiti: 'Contro / limiti', fonti: 'Fonti indipendenti', bula: 'Etichette', ia: 'lettura dell’IA',
      evid: 'Evidenze', unDoc: 'UN SOLO DOCUMENTO', verif: 'DA VERIFICARE', rimessa: 'rimessa', generato: 'generato',
      leadSelo: 'LEAD', recusa: 'NON SO · cruzamento rifiutato dal casco:'
    },
    en: {
      faixa: 'COMMERCIAL CROSSING · EXPERIMENTAL · RESULT MARKED «NOT FOR THE CLIENT» BY INTELLIGENCE',
      cls: { OPORTUNIDADE: 'OPPORTUNITY', LEAD: 'LEAD · COMMERCIAL LEAD, NOT AN OPPORTUNITY', SINAL: 'SIGNAL', GAP: 'PORTFOLIO GAP' },
      titolo: { meeting: 'Opportunities confirmed by the commercial crossing', radarfuturo: 'Signals and leads from the commercial crossing',
        portfolio: 'Portfolio gaps from the commercial crossing' },
      zeroOpp: '0 opportunities closed in this batch.',
      perche: 'Why 0: the crossing reclassified the previous candidates — none closed authorised ADAMA product × problem × window.',
      vuoto: 'No object of this class in this batch.',
      era: 'before the crossing it was', campi: { O_QUE_ACONTECEU: 'What happened', CULTURA: 'Crop', LOCAL: 'Place of the fact',
        PROBLEMA: 'Problem', JANELA: 'Window', PRODUTO_ADAMA: 'ADAMA product', AUTORIZACAO_LABEL: 'Label authorisation',
        POR_QUE_AGORA: 'Why now', ACAO_COMERCIAL: 'Commercial action' },
      trovato: 'What Sintonia found', anello: 'What is missing to become a sale', cambia: 'What would change the class',
      limiti: 'Against / limits', fonti: 'Independent sources', bula: 'Labels', ia: 'AI reading',
      evid: 'Evidence', unDoc: 'SINGLE DOCUMENT', verif: 'TO VERIFY', rimessa: 'batch', generato: 'generated',
      leadSelo: 'LEAD', recusa: 'DON’T KNOW · crossing refused by the casco:'
    }
  };
  var COR = { OPORTUNIDADE: '#009845', LEAD: '#F5B317', SINAL: '#8FB8DE', GAP: '#E07B39' };
  function txt(v) { return v === null || v === undefined || v === '' ? 'NAO SEI' : String(v); }
  function eNaoSei(v) { return /^\s*NAO[_ ]SEI/i.test(String(v || '')); }

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

  function cartao(o, T, verificar) {
    var conf = o.CONFERENCIA || {};
    var cam = o.CAMPOS || {};
    return {
      id: txt(o.ID), titulo: txt(o.TITULO), classe: o.CLASSE, rotulo: T.cls[o.CLASSE], cor: COR[o.CLASSE],
      eLead: o.CLASSE === 'LEAD',
      temEra: !!o.CLASSE_ANTES, era: T.era + ' ' + (T.cls[o.CLASSE_ANTES] || txt(o.CLASSE_ANTES)) + (o.CANDIDATA_ANTERIOR ? ' (' + o.CANDIDATA_ANTERIOR + ')' : ''),
      unDoc: conf.CRUZAMENTO_DE_UM_SO_DOCUMENTO === true, unDocL: T.unDoc,
      verif: verificar.indexOf(o.ID) >= 0 || (conf.PALAVRAS_VERIFICAR || []).length > 0, verifL: T.verif,
      anelloL: T.anello, anello: txt(o.ELO_QUE_FALTA),
      campos: CAMPOS.filter(function (k) { return cam[k]; }).map(function (k) {
        var c = cam[k] || {};
        return { l: T.campi[k], v: txt(c.valor), naoSei: eNaoSei(c.valor), temIa: !!c.INTERPRETACAO_DA_IA,
          ia: T.ia + ': ' + txt(c.INTERPRETACAO_DA_IA), fatos: (c.FACT_IDs || []).concat(c.USE_IDs || [], c.FENOLOGIA_IDs || []).join(' · ') };
      }),
      blocos: [[T.trovato, o.O_QUE_O_SINTONIA_ENCONTROU], [T.cambia, o.O_QUE_MUDARIA_A_CLASSE], [T.limiti, o.CONTRA_OU_LIMITE],
        [T.fonti, (o.ORIGEM || {}).FONTES_INDEPENDENTES], [T.bula, (o.AVISO_DE_FRESCOR_DA_BULA || {}).TEXTO]]
        .filter(function (b) { return b[1]; }).map(function (b) { return { l: b[0], v: txt(b[1]) }; }),
      evidL: T.evid + ' (' + (o.EVIDENCIAS || []).length + ')',
      evid: (o.EVIDENCIAS || []).map(function (e) {
        return { trecho: '«' + txt(e.trecho) + '»', url: txt(e.URL), fonte: txt(e.SOURCE_ID) + ' · ' + txt(e.FACT_ID) };
      })
    };
  }

  /* A vista de UMA superficie. null = sem envelope, ou rota que nao e superficie do cruzamento. */
  function vista(env, view, lang) {
    var alvo = ROTA[view] || view;
    if (!env || !SUPERFICIE[alvo]) return null;
    var T = L[lang === 'en' ? 'en' : 'it'];
    var c = env.CRUZAMENTO || {};
    var base = { ativo: true, faixa: T.faixa, titulo: T.titolo[alvo], recusado: false, recusa: '',
      origem: T.rimessa + ' ' + txt(env.REMESSA) + ' · ' + T.generato + ' ' + txt(c.GERADO_EM) + ' · ' + txt(c.MODELO) + ' · sha ' + String(env.CRUZAMENTO_SHA256 || '').slice(0, 12),
      n: 0, cartoes: [], vazio: false, vazioTexto: '', temPorque: false, porque: '', antigas: [] };
    var falhas = conferir(env);
    if (falhas.length) return Object.assign(base, { recusado: true, recusa: T.recusa + ' ' + falhas.slice(0, 5).join(' · ') });
    var verificar = ((c.CONFERENCIA_GLOBAL || {}).OBJETOS_COM_VERIFICAR) || [];
    var objs = c.OBJETOS.filter(function (o) { return SUPERFICIE[alvo].indexOf(o.CLASSE) >= 0; });
    var r = Object.assign(base, { n: objs.length, cartoes: objs.map(function (o) { return cartao(o, T, verificar); }) });
    if (!objs.length) {
      r.vazio = true;
      r.vazioTexto = alvo === 'meeting' ? T.zeroOpp : T.vuoto;
      /* O porque do 0 no Radar: as candidatas que JA FORAM oportunidade e a classe que o cruzamento lhes deu. */
      var ex = c.OBJETOS.filter(function (o) { return o.CLASSE_ANTES === 'OPORTUNIDADE'; });
      if (alvo === 'meeting' && ex.length) {
        r.temPorque = true; r.porque = T.perche;
        r.antigas = ex.map(function (o) { return { id: txt(o.CANDIDATA_ANTERIOR), para: T.cls[o.CLASSE], cor: COR[o.CLASSE],
          titulo: txt(o.TITULO), anello: txt(o.ELO_QUE_FALTA) }; });
      }
    }
    return r;
  }
  /* Quantos objetos a superficie recebe (badge da barra). null = sem envelope valido. */
  function contagem(env, view) {
    var alvo = ROTA[view] || view;
    if (!env || !SUPERFICIE[alvo] || conferir(env).length) return null;
    return env.CRUZAMENTO.OBJETOS.filter(function (o) { return SUPERFICIE[alvo].indexOf(o.CLASSE) >= 0; }).length;
  }
  return { vista: vista, contagem: contagem, conferir: conferir, SUPERFICIE: SUPERFICIE, CLASSES: CLASSES };
})();
