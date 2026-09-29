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

   D151/D152 (dono, 29/09): o CLIENTE ve o casco ORIGINAL. A camada tecnica do pote (esta leitura, a faixa
   EXPERIMENTAL, as provas) vive SO na rota interna #debug-intelligence-pot (o endereco /debug/intelligence-pot
   redireciona para la). As rotas de cliente nao cedem ao pote; so o Radar e o Radar Futuro mostram uma linha LIVE
   (a quantidade do compartimento deles + a corrida + o corte), e o que ja estava la continua, SEPARADO, como
   SNAPSHOT. FATO nao vira SINAL, SINAL nao vira OPORTUNIDADE: o casco nao escolhe compartimento.

   O QUE ESTA LEITURA NAO FAZ (INT-LAW-023 / INT-LAW-280): nao cruza, nao ordena por relevancia (a ordem e
   a do pote), nao completa NAO SEI, nao muda especie, nao escolhe compartimento — le VISTAS_DO_CASCO do
   proprio pote. So FILTER, EXPLAIN e RENDER. */
window.SINTONIA_POTE = window.SINTONIA_POTE || null;
/* POTE-V2-UNICO (D97): pedido o pote, a tela so mostra o pote. Se ele nao chegar, cada ferramenta diz
   NAO SEI (pote nao carregado) — o snapshot e a demo NAO voltam para tapar o buraco. */
window.SINTONIA_POTE_PEDIDO = window.SINTONIA_POTE_PEDIDO || false;
/* D156 · CASCO CONSUMIDOR: o que o publicador diz da ULTIMA ENTREGA da Intelligence. Uma entrega recusada (sha
   errado, ficheiro a faltar, RESULT_STATE nao final, conferencia que reprovou) NAO troca o pote no ar — o ultimo
   pote bom continua —, mas a tela diz que a entrega nova foi recusada e porque. `null` = nada a dizer. */
window.SINTONIA_POTE_ENTREGA = window.SINTONIA_POTE_ENTREGA || null;
(function () {
  try {
    if (!window.SINTONIA_POTE && /[?&]pote=local(?:&|$)/.test(window.location.search)) {
      window.SINTONIA_POTE_PEDIDO = true;
      document.write('<script src="sintonia-pote.js"><\/script>');
    }
  } catch (e) { /* sem location: fica null */ }
  /* D126 · PORTAL-PUBLICA-SOZINHO: o pote PUBLICADO (sintonia-pote-publicado.js, escrito so na copia que o
     publicador implanta) e lido como o `?pote=local` — pedido, e com a mesma lei. O local vence: quem o pede
     na maquina quer ver o seu. Envelope sem POTE (o `null` do Git) = nada muda. */
  try {
    var PUB = window.SINTONIA_POTE_PUBLICADO;
    if (PUB && typeof PUB === 'object' && PUB.ENTREGA && typeof PUB.ENTREGA === 'object') window.SINTONIA_POTE_ENTREGA = PUB.ENTREGA;
    if (!window.SINTONIA_POTE && !window.SINTONIA_POTE_PEDIDO && PUB && typeof PUB === 'object' && PUB.POTE) {
      window.SINTONIA_POTE = PUB.POTE;
      window.SINTONIA_POTE_PEDIDO = true;
    }
  } catch (e) { /* envelope ilegivel: fica como estava, e o publicador reprova no navegador */ }
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
    'portfolio', 'etichette', 'archive', 'sources', 'field'];
  /* D126 · a rota do casco que NENHUMA vista do pote reclama, mas cujo compartimento o pote traz com o mesmo
     nome e VAZIO pelo porque dele (`field`: CASCO_SEM_CONTRATO_DE_INTELLIGENCE). Com o pote pedido, essa rota
     desenha esse compartimento — o porque do pote — e nao a demo (D97: so a saida da Intelligence).
     Conhecimento do casco (que rota e essa), nao escolha de compartimento para um objeto: o pote nao poe
     objeto nenhum ali. */
  var SO_O_PORQUE = { field: 'field' };
  /* D152 · a rota interna da camada tecnica, e as rotas de cliente que mostram uma linha LIVE. */
  var ROTA_DEBUG = 'debug-intelligence-pot';
  var ROTAS_LIVE = ['meeting', 'radarfuturo'];
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
      assente: 'POTE NON CARICATO', assenteTesto: 'è stato chiesto il pote (?pote=local) ma sintonia-pote.js non è arrivato: niente snapshot, niente demo al suo posto.',
      trecho: 'affermazione (testo della fonte)', raw: 'RAW', live: 'LIVE', liveOgg: 'oggetti in questa corsa',
      liveTaglio: 'aggiornato al taglio della Sala', liveVuoto: 'nessun oggetto LIVE per questo strumento',
      liveNaoSei: 'la corsa LIVE non è leggibile', snapshot: 'SNAPSHOT', snapshotTesto: 'non è la corsa LIVE',
      demo: 'DEMO · corsa di prova', recusada: 'ULTIMA CONSEGNA RIFIUTATA', mantida: 'resta la corsa buona precedente'
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
      assente: 'POT NOT LOADED', assenteTesto: 'the pot was requested (?pote=local) but sintonia-pote.js did not arrive: no snapshot, no demo in its place.',
      trecho: 'claim (source text)', raw: 'RAW', live: 'LIVE', liveOgg: 'objects in this run',
      liveTaglio: 'updated to the Waiting Room cut-off', liveVuoto: 'no LIVE object for this tool',
      liveNaoSei: 'the LIVE run is not readable', snapshot: 'SNAPSHOT', snapshotTesto: 'not the LIVE run',
      demo: 'DEMO · test run', recusada: 'LAST DELIVERY REFUSED', mantida: 'the previous good run stays'
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

  /* O compartimento de uma rota SO_O_PORQUE, se o pote o traz vazio e com o porque. Com objeto dentro, nao:
     o pote nao o deu a vista nenhuma, e o casco nao o desenha por conta propria. */
  function soOPorque(p, view) {
    var c = SO_O_PORQUE[ROTA[view] || view];
    var e = c && p && p.COMPARTIMENTOS ? p.COMPARTIMENTOS[c] : null;
    return e && !(e.OBJETOS || []).length && e.PORQUE_VAZIO ? c : null;
  }

  /* D122/D126 · o CONTADOR de uma voz da navegacao. `null` = o pote nao foi pedido, ou a rota nao e
     ferramenta (sala, painel): o casco conta como contava. Pedido e ausente, ou pote que reprova = NAO SEI
     (o numero do legado nao volta para a barra). Pote valido = quantos objetos o compartimento dessa rota
     traz (so contar: nao filtra, nao pesa), e NAO SEI numa ferramenta que o pote nao le. */
  function contagemDaVista(p, view) {
    var pedido = typeof window !== 'undefined' && window.SINTONIA_POTE_PEDIDO === true;
    if (!p && !pedido) return null;
    /* D152: so o Radar e o Radar Futuro contam a corrida LIVE; as outras vozes contam como o casco original. */
    if (ROTAS_LIVE.indexOf(ROTA[view] || view) < 0) return null;
    if (!p || conferir(p).length) return NAO_SEI;
    var k = compartimentoDaVista(p, view) || soOPorque(p, view);
    if (!k) return NAO_SEI;
    return (p.COMPARTIMENTOS[k].OBJETOS || []).length;
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
        origem: T.origem + ': ITEM_ID ' + txt(p.ITEM_ID) + ' · G0 ' + txt(p.G0) + ' · ' + T.ammessa + ' ' + txt(p.ADMITIDA_POR),
        /* D152 · do objeto ate a prova: o trecho literal e o arquivo original (sha + onde esta). Ausente = NAO SEI. */
        trecho: T.trecho + ': ' + txt(p.TRECHO_DA_AFIRMACAO),
        raw: T.raw + ' sha256 ' + txt(p.RAW_SHA256) + ' · ' + txt(p.RAW_STORAGE_PATH)
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

  /* D156 · a recusa da ultima entrega, dita — nunca escondida, nunca no lugar do pote bom. */
  function recusaDaEntrega(T) {
    var E = typeof window !== 'undefined' ? window.SINTONIA_POTE_ENTREGA : null;
    if (!E || E.ESTADO !== 'RECUSADA') return { temRecusa: false, recusaTexto: '' };
    var mot = (E.MOTIVOS && E.MOTIVOS.length) ? E.MOTIVOS.map(txt).join(' · ') : NAO_SEI;
    return { temRecusa: true, recusaTexto: T.recusada + ' · ' + txt(E.QUANDO) + ' · ' + mot + ' — ' + T.mantida };
  }

  function cabecalho(p, T) {
    return [par(T.corsa, p.INTELLIGENCE_RUN_ID), par(T.head, p.SOURCE_HEAD), par(T.corte, p.CORTE),
      par(T.sint, p.CORRIDA_SINTETICA), par('RESULT_STATE', p.RESULT_STATE)];
  }

  function desenhar(p, k, T) {
    var e = p.COMPARTIMENTOS[k];
    var objs = (e.OBJETOS || []).map(function (o) { return objeto(o, T); });
    return {
      ativo: true, recusado: false, recusa: '', faixa: T.faixa, L: T, temComp: true,
      run: cabecalho(p, T),
      comp: { codigo: k, nome: txt(e.NOME_IT), estado: txt(e.ESTADO), n: objs.length,
        leitura: T.oggetti + ' · ' + txt((e.UNIVERSO || {}).LEITURA),
        recusados: (e.RECUSADOS_AQUI || 0) + ' ' + T.rifiutati, especies: (e.ESPECIES_ADMITIDAS || []).join(' · ') },
      vazio: objs.length === 0, vazioTitulo: NAO_SEI + ' · ' + T.vuoto + ' · ' + txt(e.PORQUE_VAZIO), vazioTexto: txt(e.PORQUE_TEXTO),
      objetos: objs,
      lacunas: (e.LACUNAS || []).map(function (g) { return { t: JSON.stringify(g) }; }), temLacunas: (e.LACUNAS || []).length > 0
    };
  }

  /* D152 · a rota interna #debug-intelligence-pot: TODOS os compartimentos, na ordem do contrato. `null` fora dela.
     Sem pote = NAO SEI (nada foi publicado nem chegou); reprovado = recusa, nada desenhado. */
  function debug(p, view, lang) {
    if (view !== ROTA_DEBUG) return null;
    var T = L[lang === 'en' ? 'en' : 'it'];
    var base = Object.assign({ ativo: true, faixa: T.faixa, L: T, recusado: false, recusa: '', assente: false, assenteTitulo: '',
      assenteTexto: '', run: [], comps: [] }, recusaDaEntrega(T));
    if (!p) return Object.assign(base, { assente: true, assenteTitulo: NAO_SEI + ' · ' + T.assente,
      assenteTexto: T.assenteTesto, run: [par(T.corsa, null)] });
    var falhas = conferir(p);
    if (falhas.length) return Object.assign(base, { recusado: true, recusa: T.rifiuto + ' ' + falhas.slice(0, 6).join(' · ') });
    return Object.assign(base, { run: cabecalho(p, T),
      comps: DOZE.filter(function (k) { return p.COMPARTIMENTOS[k]; }).map(function (k) { return desenhar(p, k, T); }) });
  }

  /* D152 · a linha LIVE de uma rota de cliente (Radar, Radar Futuro): so a QUANTIDADE do compartimento dessa rota,
     a corrida e o corte. Nao desenha objeto nem prova (isso e do debug). `null` = sem pedido, ou rota sem LIVE. */
  function live(p, view, lang) {
    var alvo = ROTA[view] || view;
    var pedido = typeof window !== 'undefined' && window.SINTONIA_POTE_PEDIDO === true;
    if (ROTAS_LIVE.indexOf(alvo) < 0 || (!p && !pedido)) return null;
    var T = L[lang === 'en' ? 'en' : 'it'];
    /* D156 · DEMO e LIVE nunca se confundem: um pote de teste (CORRIDA_SINTETICA = true) diz DEMO na linha. */
    var demo = !!(p && p.CORRIDA_SINTETICA === true);
    /* B3 (criterio do Casco owner): o motivo de uma entrega recusada vive SO no debug, nunca na tela do cliente. */
    var nada = { ativo: true, legivel: false, n: NAO_SEI, rotulo: demo ? T.demo : T.live, eDemo: demo,
      texto: T.liveNaoSei, run: NAO_SEI, quando: NAO_SEI, L: T, snapshot: T.snapshot, snapshotTexto: T.snapshotTesto };
    if (!p) return Object.assign(nada, { texto: T.assente });
    if (conferir(p).length) return nada;
    var k = compartimentoDaVista(p, view);
    if (!k) return nada;
    var e = p.COMPARTIMENTOS[k];
    var n = (e.OBJETOS || []).length;
    var c = p.CORTE;
    return Object.assign(nada, { legivel: true, n: n, run: txt(p.INTELLIGENCE_RUN_ID),
      quando: txt(c && typeof c === 'object' ? c.COPIA_DA_SALA_EM : c),
      texto: n ? T.liveOgg : T.liveVuoto + ' · ' + txt(e.PORQUE_VAZIO) });
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
    if (!k) k = soOPorque(p, view);
    if (!k) return null;
    return desenhar(p, k, T);
  }

  return { CONTRATO: CONTRATO, MARCA: MARCA, conferir: conferir, compartimentoDaVista: compartimentoDaVista, vm: vm,
    serieMedida: serieMedida, contagemDaVista: contagemDaVista, debug: debug, live: live, ROTA_DEBUG: ROTA_DEBUG,
    ROTAS_LIVE: ROTAS_LIVE };
})();
