/* POTE-UNICO · o CARREGADOR e a LEITURA do pote da Intelligence — este ficheiro NAO tem dados.

   O pote (contrato POTE_INTELLIGENCE_CASCO/v2, dono: pacote/pote_intelligence_casco.py) e UM ficheiro
   por corrida da Intelligence, com um compartimento por ferramenta. Vive em `sintonia-pote.js`
   (window.SINTONIA_POTE), GERADO fora do Git (.gitignore) e fora de qualquer deploy (.vercelignore),
   como os .local.js da Sala.

   So se pede com `?pote=local` no endereco. Sem isso nada e pedido — nenhum portao (link-asset percorre
   as vistas e reprova um 404) nem nenhum deploy publico pede um ficheiro que nao existe — e o casco fica
   exatamente como estava: snapshot e demo.

   COM o pote, cada ferramenta desenha o SEU compartimento, e so ele: o snapshot de 07/09 e a demo deixam
   de aparecer nessa vista (precedencia). Compartimento vazio mostra o PORQUE que o pote escreveu.

   O QUE ESTA LEITURA NAO FAZ (INT-LAW-023 / INT-LAW-280): nao cruza, nao ordena por relevancia (a ordem e
   a do pote), nao completa NAO SEI, nao muda especie, nao escolhe compartimento — le VISTAS_DO_CASCO do
   proprio pote. So FILTER, EXPLAIN e RENDER. */
window.SINTONIA_POTE = window.SINTONIA_POTE || null;
/* POTE-V2-UNICO (D97): pedido o pote, a tela so mostra o pote. Se ele nao chegar, cada ferramenta diz
   NAO SEI (pote nao carregado) — o snapshot e a demo NAO voltam para tapar o buraco. */
window.SINTONIA_POTE_PEDIDO = window.SINTONIA_POTE_PEDIDO || false;
(function () {
  try {
    if (!window.SINTONIA_POTE && /[?&]pote=local(?:&|$)/.test(window.location.search)) {
      window.SINTONIA_POTE_PEDIDO = true;
      document.write('<script src="sintonia-pote.js"><\/script>');
    }
  } catch (e) { /* sem location: fica null */ }
})();

window.SINTONIA_POTE_CASCO = (function () {
  var CONTRATO = 'POTE_INTELLIGENCE_CASCO/v2';
  var MARCA = 'EXPERIMENTAL · NAO_PARA_CLIENTE';
  var NAO_SEI = 'NAO SEI';
  var DOZE = ['meeting', 'future', 'windows', 'market', 'voices', 'competitors', 'science',
    'portfolio', 'archive', 'sources', 'field', 'casa'];
  /* Rotas do casco que sao a MESMA vista com outro nome (a rota historica do radar e as duas portas
     por baixo das oportunidades). E conhecimento do casco, nao do pote. */
  var ROTA = { radar: 'meeting', msignals: 'meeting', mradar: 'meeting' };
  /* As rotas que sao ferramenta (as que um compartimento le). Conhecimento do casco. */
  var FERRAMENTAS = ['meeting', 'radarfuturo', 'future', 'windows', 'market', 'voices', 'competitors', 'science',
    'portfolio', 'etichette', 'archive', 'sources'];
  /* Copias de leitura das listas do contrato (dono: pacote/pote_intelligence_casco.py). */
  var ADMITIDA = ['G0_PASSOU', 'FUTURO_POR_DESENHO', 'USO_SEM_TEMPO', 'PONTE_V1'];
  var HONESTOS = ['NAO', 'NAO_TRATAR_AGORA', 'NO_DEFENSIBLE_ACTION_YET'];
  var LUGAR_DA_FONTE = ['SOURCE_LOCATION', 'DOCUMENT_LOCATION', 'PUBLISHER_LOCATION', 'LOCAL_DA_FONTE',
    'LOCAL_DO_DOCUMENTO', 'SEDE_DA_FONTE'];

  var L = {
    it: {
      faixa: 'EXPERIMENTAL · NON PER IL CLIENTE — pote della Intelligence: questa vista mostra SOLO la corsa qui sotto',
      corsa: 'corsa', head: 'SOURCE_HEAD', corte: 'taglio', sint: 'sintetica',
      oggetti: 'oggetti in questa corsa', rifiutati: 'rifiutati dal pote (vedi il pote)',
      vuoto: 'VUOTO', perche: 'perché', contraddice: 'contraddice', incertezza: 'incertezza',
      prova: 'PROVA', fuori: 'fuori contratto — non è una chiave della vista',
      futuro: 'FUTURO · fatto presente sul futuro — NON è un\'opportunità',
      lacune: 'lacune della corsa', noUrl: 'URL non navigabile', rifiuto: 'POTE RIFIUTATO — niente è disegnato:',
      pub: 'pubblicato', racc: 'raccolto', fatto: 'tempo del fatto',
      origem: 'da dove viene (Sala d\'attesa, solo come prova)', ammessa: 'ammessa per',
      senzaTempo: 'tempo del fatto NON ancorato — uso che non richiede tempo', risultato: 'risultato',
      serie: 'SERIE MISURATA', punti: 'punti', unita: 'stessa unità', solto: 'SEGNALE ISOLATO — NON è una variazione di mercato',
      assente: 'POTE NON CARICATO', assenteTesto: 'è stato chiesto il pote (?pote=local) ma sintonia-pote.js non è arrivato: niente snapshot, niente demo al suo posto.'
    },
    en: {
      faixa: 'EXPERIMENTAL · NOT FOR THE CLIENT — Intelligence pot: this view shows ONLY the run below',
      corsa: 'run', head: 'SOURCE_HEAD', corte: 'cut-off', sint: 'synthetic',
      oggetti: 'objects in this run', rifiutati: 'refused by the pot (see the pot)',
      vuoto: 'EMPTY', perche: 'why', contraddice: 'contradicts', incertezza: 'uncertainty',
      prova: 'PROOF', fuori: 'outside the contract — not a key of this view',
      futuro: 'FUTURE · present fact about the future — NOT an opportunity',
      lacune: 'gaps of the run', noUrl: 'URL not navigable', rifiuto: 'POT REFUSED — nothing is drawn:',
      pub: 'published', racc: 'collected', fatto: 'fact time',
      origem: 'where it came from (Waiting Room, only as proof)', ammessa: 'admitted by',
      senzaTempo: 'fact time NOT anchored — use that does not need time', risultato: 'result',
      serie: 'MEASURED SERIES', punti: 'points', unita: 'same unit', solto: 'ISOLATED SIGNAL — NOT a market change',
      assente: 'POT NOT LOADED', assenteTesto: 'the pot was requested (?pote=local) but sintonia-pote.js did not arrive: no snapshot, no demo in its place.'
    }
  };

  /* A cor diz a ESPECIE, e a de futuro nao se confunde com a de oportunidade: verde corporativo so para
     OPORTUNIDADE, azul secundario (tracejado) so para FATO_PRESENTE_SOBRE_O_FUTURO, neutro para o resto.
     Valores do extrato ADAMA (_ds/adama-brandwell/tokens/colors.css). */
  var ESTILO = {
    OPORTUNIDADE: { bg: '#009845', ink: '#FFFFFF', edge: 'rgba(0,152,69,0.55)', traco: 'solid' },
    FATO_PRESENTE_SOBRE_O_FUTURO: { bg: '#00698F', ink: '#FFFFFF', edge: '#00698F', traco: 'dashed' },
    _: { bg: 'transparent', ink: '#C9C3C1', edge: 'rgba(203,197,195,0.22)', traco: 'solid' }
  };

  function txt(v) {
    if (v === null || v === undefined) return NAO_SEI;
    return typeof v === 'string' ? v : JSON.stringify(v);
  }
  function ns(v) { return txt(v) === NAO_SEI; }
  function par(k, v) { return { k: k, v: txt(v), color: ns(v) ? '#F5B317' : '#FFFFFF' }; }

  /* O portao do casco: so o que torna a leitura IMPOSSIVEL ou DESONESTA. A lei inteira e de
     `conferir_pote` em pacote/pote_intelligence_casco.py, que corre antes de o pote nascer. */
  function conferir(p) {
    var v = [];
    if (!p || typeof p !== 'object') return ['o pote nao e objeto'];
    if (p.SCHEMA !== CONTRATO) v.push('SCHEMA ' + txt(p.SCHEMA) + ' nao e ' + CONTRATO);
    if (p.MARCA !== MARCA || p.NAO_PARA_CLIENTE !== true) v.push('pote sem a marca ' + MARCA);
    if (!p.INTELLIGENCE_RUN_ID || ns(p.INTELLIGENCE_RUN_ID)) v.push('pote sem INTELLIGENCE_RUN_ID');
    var C = p.COMPARTIMENTOS;
    if (!C || typeof C !== 'object') return v.concat(['pote sem COMPARTIMENTOS']);
    DOZE.forEach(function (k) {
      var e = C[k];
      if (!e) { v.push('falta o compartimento ' + k); return; }
      var objs = e.OBJETOS || [];
      if (!objs.length && (e.ESTADO !== 'VAZIO' || !e.PORQUE_VAZIO)) v.push(k + ': vazio sem o porque');
      objs.forEach(function (o) {
        var id = k + '/' + o.OBJETO_ID;
        if (o.MARCA !== MARCA || o.NAO_PARA_CLIENTE !== true) v.push(id + ': sem a marca');
        if ((e.ESPECIES_ADMITIDAS || []).indexOf(o.ESPECIE) < 0) v.push(id + ': especie fora do compartimento');
        if (!o.PROVA || !o.PROVA.length) v.push(id + ': sem prova');
        (o.PROVA || []).forEach(function (p) {
          ['URL', 'PUBLISHED_AT'].forEach(function (c) {
            if (!(c in p)) v.push(id + ': prova sem ' + c);
            else if (ns(p[c]) && (!p[c + '_BASE'] || ns(p[c + '_BASE']))) v.push(id + ': ' + c + ' NAO SEI sem a base');
          });
          if (ADMITIDA.indexOf(p.ADMITIDA_POR) < 0) v.push(id + ': prova sem ADMITIDA_POR');
          if (p.ADMITIDA_POR === 'USO_SEM_TEMPO' && o.USO_EXIGE_TEMPO !== false) v.push(id + ': item sem tempo prova uso que exige tempo');
        });
        var honesto = HONESTOS.indexOf(o.RESULTADO) >= 0 && ['SINAL', 'CROSSING', 'FINDING'].indexOf(o.ESPECIE) >= 0;
        if (o.USO_EXIGE_TEMPO === false && o.ESPECIE !== 'RENDIMENTO_DE_FONTE' && !honesto) v.push(id + ': uso sem tempo sem resultado honesto');
        if (LUGAR_DA_FONTE.indexOf(txt(o.LOCATION_SOURCE)) >= 0) v.push(id + ': lugar da fonte como lugar do facto');
        if (k === 'market') {
          var m = o.MERCADO || {};
          if (m.LEITURA !== 'SERIE_MEDIDA' && m.LEITURA !== 'SINAL_SOLTO') v.push(id + ': Polso sem MERCADO.LEITURA');
          if (m.LEITURA === 'SERIE_MEDIDA' && !serieMedida(m.SERIE)) v.push(id + ': sinal solto como SERIE_MEDIDA');
        }
      });
    });
    return v;
  }

  /* P8 · >= 2 pontos, cada um com PERIOD/PRICE/UNIT, todos na mesma unidade, periodos distintos. */
  function serieMedida(s) {
    if (!s || !s.length || s.length < 2) return false;
    var u = {}, per = {};
    for (var i = 0; i < s.length; i++) {
      var q = s[i] || {};
      if (ns(q.PERIOD) || ns(q.PRICE) || ns(q.UNIT) || q.PERIOD === '' || q.PRICE === '' || q.UNIT === '') return false;
      u[txt(q.UNIT)] = 1; per[txt(q.PERIOD)] = 1;
    }
    return Object.keys(u).length === 1 && Object.keys(per).length === s.length;
  }

  function compartimentoDaVista(p, view) {
    var alvo = ROTA[view] || view;
    var C = (p && p.COMPARTIMENTOS) || {};
    for (var i = 0; i < DOZE.length; i++) {
      var e = C[DOZE[i]];
      if (e && (e.VISTAS_DO_CASCO || []).indexOf(alvo) >= 0) return DOZE[i];
    }
    return null;
  }

  function linkSeguro(u) { return typeof u === 'string' && /^https?:\/\//i.test(u); }

  function objeto(o, T) {
    var st = ESTILO[o.ESPECIE] || ESTILO._;
    var chaves = Object.keys(o.CHAVES || {}).map(function (k) { return par(k, o.CHAVES[k]); });
    var fora = Object.keys(o.FORA_DO_CONTRATO || {}).map(function (k) { return par(k, o.FORA_DO_CONTRATO[k]); });
    var provas = (o.PROVA || []).map(function (p) {
      return {
        cadeia: ['ITEM_ID ' + txt(p.ITEM_ID), 'RAW_OBSERVATION_ID ' + txt(p.RAW_OBSERVATION_ID),
          'SOURCE_ID ' + txt(p.SOURCE_ID), 'DOCUMENT_ID ' + txt(p.DOCUMENT_ID)].join(' → '),
        upstream: 'CORRIDA_UPSTREAM ' + txt(p.CORRIDA_UPSTREAM) + ' · INTELLIGENCE_RUN_ID ' + txt(p.INTELLIGENCE_RUN_ID),
        temUrl: linkSeguro(p.URL), semUrl: !linkSeguro(p.URL), url: linkSeguro(p.URL) ? p.URL : '',
        urlTexto: linkSeguro(p.URL) ? p.URL : (ns(p.URL) ? 'URL ' + NAO_SEI + ' · ' + txt(p.URL_BASE) : T.noUrl + ': ' + txt(p.URL)),
        urlColor: ns(p.URL) ? '#F5B317' : '#8F8886',
        datas: T.pub + ' ' + txt(p.PUBLISHED_AT) + (ns(p.PUBLISHED_AT) ? ' (' + txt(p.PUBLISHED_AT_BASE) + ')' : '') +
          ' · ' + T.racc + ' ' + txt(p.COLHIDO_EM) + ' · ' + T.fatto + ' ' + txt(p.FACT_TIME),
        origem: T.origem + ': ITEM_ID ' + txt(p.ITEM_ID) + ' · G0 ' + txt(p.G0) + ' · ' + T.ammessa + ' ' + txt(p.ADMITIDA_POR)
      };
    });
    var m = o.MERCADO || null;
    var mercado = !m ? '' : (m.LEITURA === 'SERIE_MEDIDA'
      ? T.serie + ' · ' + (m.SERIE || []).length + ' ' + T.punti + ' · ' + T.unita + ' ' + txt(m.UNIDADE) + ' · ' +
        (m.SERIE || []).map(function (q) { return txt(q.PERIOD) + ' ' + txt(q.PRICE); }).join(' | ')
      : T.solto + ' · ' + txt(m.PORQUE));
    return {
      id: txt(o.OBJETO_ID), especie: txt(o.ESPECIE), especieDe: txt(o.ESPECIE_DITA_POR),
      eFuturo: o.ESPECIE === 'FATO_PRESENTE_SOBRE_O_FUTURO', aviso: o.ESPECIE === 'FATO_PRESENTE_SOBRE_O_FUTURO' ? T.futuro : '',
      badgeBg: st.bg, badgeInk: st.ink, edge: st.edge, traco: st.traco, marca: txt(o.MARCA),
      chaves: chaves, fora: fora, temFora: fora.length > 0,
      porque: par(T.perche, o.PORQUE), contradiz: par(T.contraddice, o.CONTRADIZ), incerteza: par(T.incertezza, o.INCERTEZA),
      provas: provas,
      temMercado: !!m, mercado: mercado, eSerie: !!m && m.LEITURA === 'SERIE_MEDIDA',
      semTempo: o.USO_EXIGE_TEMPO === false, avisoTempo: o.USO_EXIGE_TEMPO === false ? T.senzaTempo : '',
      resultado: par(T.risultato, o.RESULTADO),
      origens: ['ENTITY_SOURCE', 'LOCATION_SOURCE'].filter(function (c) { return c in o; }).map(function (c) { return par(c, o[c]); })
    };
  }

  /* A vista do pote para UMA rota do casco. `null` = esta rota nao le o pote (sem pote, ou rota que
     nenhum compartimento reclama): o casco desenha o que desenhava. */
  function vm(p, view, lang) {
    var T = L[lang === 'en' ? 'en' : 'it'];
    if (!p) {
      /* Sem pote e sem pedido: o casco fica como estava. Pedido e nao chegou: NAO SEI, sem legado. */
      var pedido = typeof window !== 'undefined' && window.SINTONIA_POTE_PEDIDO === true;
      if (!pedido || FERRAMENTAS.indexOf(ROTA[view] || view) < 0) return null;
      return { ativo: true, recusado: false, recusa: '', faixa: T.faixa, L: T, temComp: false,
        run: [par(T.corsa, null)], comp: {}, vazio: true, vazioTitulo: NAO_SEI + ' · ' + T.assente,
        vazioTexto: T.assenteTesto, objetos: [], lacunas: [], temLacunas: false };
    }
    var falhas = conferir(p);
    if (falhas.length) {
      /* Pote que existe e reprova: nada dele e desenhado, e o legado tambem nao volta como se fosse
         atual — a vista diz porque. So nas rotas que uma ferramenta tem. */
      var alvo = ROTA[view] || view;
      if (FERRAMENTAS.indexOf(alvo) < 0) return null;
      return { ativo: true, recusado: true, recusa: T.rifiuto + ' ' + falhas.slice(0, 6).join(' · '), faixa: T.faixa,
        run: [], comp: {}, temComp: false, vazio: false, objetos: [], lacunas: [], temLacunas: false, L: T };
    }
    var k = compartimentoDaVista(p, view);
    if (!k) return null;
    var e = p.COMPARTIMENTOS[k];
    var objs = (e.OBJETOS || []).map(function (o) { return objeto(o, T); });
    return {
      ativo: true, recusado: false, recusa: '', faixa: T.faixa, L: T, temComp: true,
      run: [par(T.corsa, p.INTELLIGENCE_RUN_ID), par(T.head, p.SOURCE_HEAD), par(T.corte, p.CORTE),
        par(T.sint, p.CORRIDA_SINTETICA), par('RESULT_STATE', p.RESULT_STATE)],
      comp: { codigo: k, nome: txt(e.NOME_IT), estado: txt(e.ESTADO), n: objs.length,
        leitura: T.oggetti + ' · ' + txt((e.UNIVERSO || {}).LEITURA),
        recusados: (e.RECUSADOS_AQUI || 0) + ' ' + T.rifiutati, especies: (e.ESPECIES_ADMITIDAS || []).join(' · ') },
      vazio: objs.length === 0, vazioTitulo: NAO_SEI + ' · ' + T.vuoto + ' · ' + txt(e.PORQUE_VAZIO), vazioTexto: txt(e.PORQUE_TEXTO),
      objetos: objs,
      lacunas: (e.LACUNAS || []).map(function (g) { return { t: JSON.stringify(g) }; }), temLacunas: (e.LACUNAS || []).length > 0
    };
  }

  return { CONTRATO: CONTRATO, MARCA: MARCA, conferir: conferir, compartimentoDaVista: compartimentoDaVista, vm: vm,
    serieMedida: serieMedida };
})();
