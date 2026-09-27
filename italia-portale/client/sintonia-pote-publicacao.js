/* POTE PUBLICADO (D114) · a LEITURA do que a publicacao acrescenta ao pote — este ficheiro NAO tem dados.

   O dado vive em `sintonia-pote-publicado.js` (window.SINTONIA_POTE_PUBLICADO), GERADO por
   pacote/publicar_pote_aprovado.py a partir de docs/casco/r7/: o POTE-R7 (que sintonia-pote-casco.js
   ja desenha, compartimento a compartimento) e a ANALISE-R7 da MESMA corrida, que traz o que o pote v2
   nao transporta — os 86 cruzamentos com o estado, a sonda olivo x mosca e o que as 38 novas trouxeram.

   Esta leitura acrescenta, por vista, SO o que ja esta escrito:
     · a faixa da publicacao: quem aprovou, quando, de que corrida, e o que NAO confere;
     · os RECUSADOS do pote naquele compartimento, visiveis, com o motivo;
     · no Portafoglio/Etichette, os 86 cruzamentos, agrupados pelo estado que a Intelligence lhes deu;
     · nas Finestre, a sonda olivo x mosca (NAO e janela instalada);
     · no Registro delle fonti, as lacunas da corrida e o que as 38 novas acrescentaram;
     · na rota «field», o vazio do pote com o PORQUE — a Rete Commerciale simulada nao volta.

   O QUE ESTA LEITURA NAO FAZ (INT-LAW-023 / INT-LAW-280): nao cruza, nao muda estado, nao ordena por
   relevancia (dentro de cada estado a ordem e a da analise), nao completa NAO SEI, nao decide o que e
   fonte candidata (le a VIA que a Intelligence escreveu). Se o pote carregado e de OUTRA corrida
   (?pote=local), nada disto se aplica: devolve null. */
window.SINTONIA_POTE_PUBLICACAO = (function () {
  var NAO_SEI = 'NAO SEI';
  var AMBAR = '#F5B317', BRANCO = '#FFFFFF', CINZA = '#C9C3C1', APAGADO = '#8F8886';

  var L = {
    it: {
      faixa: 'PUBBLICATO PER DECISIONE {D} DEL PROPRIETARIO · {DATA} — corsa {R} della Intelligence. I dati restano EXPERIMENTAL: si leggono come esperimento, non come raccomandazione.',
      corsa: 'corsa', rodada: 'giro', corte: 'copia della Sala', ready: 'elementi READY letti', motor: 'motore',
      gerador: 'generatore del pote', conferir: 'verifica del pote (dal manifesto)', sha: 'SHA256 del pote',
      shaNao: 'NON CORRISPONDE al manifesto', shaSim: 'corrisponde al manifesto', conteggi: 'conteggi per compartimento: corrispondono al manifesto',
      analise: 'incroci', rec: 'RIFIUTATI DAL POTE IN QUESTO COMPARTIMENTO', recLeg: 'visibili qui, mai disegnati come oggetti: il pote li ha rifiutati e dice perché',
      cruzT: 'GLI {N} INCROCI DELLA CORSA', cruzQ: 'domanda: «l\'etichetta ADAMA letta autorizza la sostanza citata nella coltura del bollettino?»',
      cruzLeg: '«SÌ» = l\'etichetta letta copre quella sostanza in quella coltura. NON prova uso, raccomandazione di un prodotto ADAMA, luogo né momento.',
      viaP: 'PILOTA', viaC: 'FONTE CANDIDATA · estensione dichiarata', nel: 'NEL POTE: oggetto', rif: 'RIFIUTATO DAL POTE', fuori: 'ASSENTE DAL POTE (né oggetto né rifiuto)',
      sost: 'sostanza', prod: 'prodotti ADAMA con la sostanza', colEt: 'colture in etichetta', colDoc: 'coltura nel documento', ent: 'origine della coltura',
      luogo: 'luogo', interp: 'interpretazione', trecho: 'estratto della fonte (prova)', pub: 'pubblicato', sala: 'chiave della Sala', noUrl: 'URL non navigabile',
      naoE: 'NON È', sondaT: 'SONDA · olivo × mosca dell\'olivo — NON è una finestra installata', itens: 'elementi con la coppia',
      apoios: 'appoggi validi', fora: 'rimasti fuori', aberta: 'aperta ora', metodo: 'metodo',
      lacT: 'LACUNE DELLA CORSA', lacLeg: 'requisiti che bloccano una domanda: il dato manca, non è zero',
      novasT: 'COSA HANNO AGGIUNTO LE 38 NUOVE', sinais: 'segnali datati delle 38 nuove', idade: 'età minima (giorni)',
      d112T: 'LUOGO SOLO DAL TESTO SCRITTO (D112)', campoT: 'RETE COMMERCIALE DI CAMPO · SIMULATO — la simulazione non è mostrata',
      campoTx: 'Questa vista reggeva su persone e messaggi SIMULATI. Con il pote pubblicato, mostra ciò che il pote scrive:'
    },
    en: {
      faixa: 'PUBLISHED BY OWNER DECISION {D} · {DATA} — Intelligence run {R}. The data stay EXPERIMENTAL: read them as an experiment, not as a recommendation.',
      corsa: 'run', rodada: 'round', corte: 'Sala copy', ready: 'READY items read', motor: 'engine',
      gerador: 'pot generator', conferir: 'pot check (from the manifest)', sha: 'pot SHA256',
      shaNao: 'DOES NOT MATCH the manifest', shaSim: 'matches the manifest', conteggi: 'counts per compartment: match the manifest',
      analise: 'crossings', rec: 'REFUSED BY THE POT IN THIS COMPARTMENT', recLeg: 'visible here, never drawn as objects: the pot refused them and says why',
      cruzT: 'THE {N} CROSSINGS OF THE RUN', cruzQ: 'question: «does the ADAMA label read authorise the substance cited in the crop of the bulletin?»',
      cruzLeg: '«YES» = the label read covers that substance on that crop. It does NOT prove use, a recommendation of an ADAMA product, place or moment.',
      viaP: 'PILOT', viaC: 'CANDIDATE SOURCE · declared extension', nel: 'IN THE POT: object', rif: 'REFUSED BY THE POT', fuori: 'ABSENT FROM THE POT (neither object nor refusal)',
      sost: 'substance', prod: 'ADAMA products with the substance', colEt: 'crops on the label', colDoc: 'crop in the document', ent: 'origin of the crop',
      luogo: 'place', interp: 'interpretation', trecho: 'source excerpt (proof)', pub: 'published', sala: 'Sala key', noUrl: 'URL not navigable',
      naoE: 'IS NOT', sondaT: 'PROBE · olive × olive fly — NOT an installed window', itens: 'items with the pair',
      apoios: 'valid supports', fora: 'left out', aberta: 'open now', metodo: 'method',
      lacT: 'GAPS OF THE RUN', lacLeg: 'requirements that block a question: the datum is missing, not zero',
      novasT: 'WHAT THE 38 NEW ITEMS ADDED', sinais: 'dated signals of the 38 new items', idade: 'minimum age (days)',
      d112T: 'PLACE ONLY FROM THE WRITTEN TEXT (D112)', campoT: 'FIELD SALES NETWORK · SIMULATED — the simulation is not shown',
      campoTx: 'This view stood on SIMULATED people and messages. With the published pot, it shows what the pot writes:'
    }
  };

  /* O estado e da Intelligence (ESTADO_R7); aqui so se lhe da nome e cor. «A CONFIRMAR» e a marca
     obrigatoria do sim: amarelo tracejado, nunca o verde da oportunidade. */
  var ESTADOS = [
    { k: 'POSSIBLE_ANSWER_YES_A_CONFIRMAR', marca: 'A CONFIRMAR', it: 'SÌ · DA CONFERMARE', en: 'YES · TO BE CONFIRMED', color: AMBAR, traco: 'dashed' },
    { k: 'POSSIBLE_ANSWER_NO', marca: '', it: 'NO · non è nell\'etichetta letta', en: 'NO · not in the label read', color: CINZA, traco: 'solid' },
    { k: 'PARTIAL_GRAO_INCOMPATIVEL', marca: '', it: 'GRANA INCOMPATIBILE · il pezzo non nomina la coltura', en: 'INCOMPATIBLE GRAIN · the passage does not name the crop', color: '#B1A9A7', traco: 'solid' },
    { k: 'NOT_POSSIBLE', marca: '', it: 'NON POSSIBILE · senza coltura', en: 'NOT POSSIBLE · no crop', color: APAGADO, traco: 'solid' }
  ];

  function txt(v) {
    if (v === null || v === undefined || v === '') return NAO_SEI;
    if (Array.isArray(v)) return v.length ? v.map(txt).join(' · ') : '—';
    return typeof v === 'string' ? v : (typeof v === 'number' || typeof v === 'boolean') ? String(v) : JSON.stringify(v);
  }
  function ns(v) { return /^N[AÃ]O[ _]SEI/.test(txt(v)); }
  function par(k, v) { return { k: k, v: txt(v), color: ns(v) ? AMBAR : BRANCO }; }
  function linkSeguro(u) { return typeof u === 'string' && /^https?:\/\//i.test(u); }
  function prova(url, pub, T) {
    return {
      temUrl: linkSeguro(url), semUrl: !linkSeguro(url), url: linkSeguro(url) ? url : '',
      urlTexto: linkSeguro(url) ? url : (ns(url) ? 'URL ' + NAO_SEI : T.noUrl + ': ' + txt(url)),
      pub: T.pub + ' ' + txt(pub), pubColor: ns(pub) ? AMBAR : CINZA
    };
  }
  /* Data ISO -> dd/mm/aaaa hh:mm UTC, sem inventar: o que nao e ISO passa como esta. */
  function quando(v) {
    var m = /^(\d{4})-(\d{2})-(\d{2})(?:[T ](\d{2}):(\d{2}))?/.exec(txt(v));
    return m ? m[3] + '/' + m[2] + '/' + m[1] + (m[4] ? ' ' + m[4] + ':' + m[5] + ' UTC' : '') : txt(v);
  }

  function cabecalho(pub, pote, T) {
    var D = pub.DECISAO || {}, SH = pote.SOURCE_HEAD || {}, C = pote.CORTE || {};
    var shaOk = pub.SHA256_CONFERE_COM_O_MANIFESTO === true;
    return {
      faixa: T.faixa.replace('{D}', txt(D.ID)).replace('{DATA}', quando(D.DATA)).replace('{R}', txt(pub.RODADA)),
      decisao: '«' + txt(D.TEXTO) + '» — ' + txt(D.ID),
      meta: [
        par(T.rodada, pub.RODADA), par(T.corsa, pote.INTELLIGENCE_RUN_ID), par(T.corte, quando(C.COPIA_DA_SALA_EM)),
        par(T.ready, C.READY), par(T.motor, txt(SH.MOTOR_RAMO) + ' @ ' + txt(SH.MOTOR).slice(0, 8)),
        par(T.gerador, pub.GERADOR_DO_POTE), par(T.conferir, pub.CONFERIR_POTE_DO_DONO),
        { k: T.sha, v: txt(pub.POTE_SHA256).slice(0, 16) + '… · ' + (shaOk ? T.shaSim : T.shaNao + ' (' + txt(pub.SHA256_DECLARADO_NO_MANIFESTO).slice(0, 16) + '…) · ' + T.conteggi),
          color: shaOk ? BRANCO : AMBAR }
      ]
    };
  }

  function recusados(pote, comp, T) {
    var r = (pote.RECUSADOS || []).filter(function (x) { return x.COMPARTIMENTO === comp; });
    return { titulo: T.rec + ' · ' + r.length, legenda: T.recLeg, tem: r.length > 0,
      linhas: r.map(function (x) { return { id: txt(x.OBJETO_ID), motivo: txt(x.MOTIVO), detalhe: txt(x.DETALHE) }; }) };
  }

  function cruzamentos(pub, pote, T, lang) {
    var A = pub.ANALISE || {}, C = A.CROSSINGS || [];
    var noPote = {}, recusa = {};
    ((pote.COMPARTIMENTOS.portfolio || {}).OBJETOS || []).forEach(function (o) { noPote[o.OBJETO_ID] = true; });
    (pote.RECUSADOS || []).forEach(function (r) { if (r.COMPARTIMENTO === 'portfolio') recusa[r.OBJETO_ID] = r; });
    var R = A.CROSSINGS_RESUMO || {};
    var grupos = ESTADOS.map(function (E) {
      var linhas = C.filter(function (c) { return c.ESTADO_R7 === E.k; }).map(function (c) {
        var F = c.FONTE || {}, I = c.INTERPRETACAO || {}, LO = F.LOCAL || {};
        var r = recusa[c.OBJETO_ID];
        var candidata = c.VIA === 'EXTENSAO_DECLARADA';
        return {
          id: txt(c.OBJETO_ID), estado: E.k, estadoNome: E[lang], color: E.color, traco: E.traco,
          marca: E.marca, temMarca: !!E.marca,
          via: candidata ? T.viaC : T.viaP, viaCodigo: txt(c.VIA), candidata: candidata,
          viaColor: candidata ? AMBAR : CINZA,
          pote: noPote[c.OBJETO_ID] ? T.nel : (r ? T.rif + ' · ' + txt(r.MOTIVO) + ': ' + txt(r.DETALHE) : T.fuori),
          poteColor: noPote[c.OBJETO_ID] ? BRANCO : AMBAR,
          chaves: [par(T.sost, c.SUBSTANCIA), par('SOURCE_ID', c.SOURCE_ID), par(T.colDoc, F.CULTURA_NO_READY),
            par(T.ent, I.ENTITY_SOURCE_DA_CULTURA || F.ENTITY_SOURCE_DA_CULTURA),
            par(T.luogo, txt(LO.FACT_LOCATION) + ' · ' + txt(LO.ESTADO)), par(T.colEt, c.CULTURAS_NO_ROTULO)],
          produtos: T.prod + ': ' + txt(c.PRODUTOS_ADAMA),
          interp: T.interp + ': X2 ' + txt(I.X2_CULTURAS_QUE_CASAM) + ' · X3 ' + txt(I.X3_NOMEADA_NO_TROCO_E_A_400) +
            ' · X3w ' + txt(I.X3W_A_400_CARACTERES) + ' · X3h ' + txt(I.X3H_CABECALHO) + ' → ' + txt(I.ESTADO) +
            ' · ' + (lang === 'en' ? 'before' : 'prima') + ' ' + txt(c.ANTES),
          trechos: (F.TROCO_COM_A_SUBSTANCIA || []).map(function (t) { return { t: '«' + txt(t) + '»' }; }),
          prova: prova(c.URL, c.PUBLISHED_AT, T),
          sala: T.sala + ' ' + txt(c.SALA_CHAVE) + ' · RAW_OBSERVATION_ID ' + txt(c.RAW_OBSERVATION_ID),
          naoE: T.naoE + ': ' + txt(c.NAO_E)
        };
      });
      return { k: E.k, titulo: E[lang] + ' · ' + linhas.length, color: E.color, linhas: linhas, tem: linhas.length > 0 };
    });
    var porVia = R.POR_VIA || {};
    return {
      titulo: T.cruzT.replace('{N}', txt(R.TOTAL)), pergunta: T.cruzQ, legenda: T.cruzLeg,
      resumo: ESTADOS.map(function (E) { return { k: E.k, n: txt((R.POR_ESTADO || {})[E.k]), nome: E[lang], color: E.color }; }),
      vias: [par(T.viaP, porVia.PILOTO), par(T.viaC, porVia.EXTENSAO_DECLARADA)],
      grupos: grupos
    };
  }

  function sonda(pub, T) {
    var S = ((pub.ANALISE || {}).CORTE_VERTICAL) || {}, J = S.JULGAMENTO_DA_SONDA || {}, F = J.PORQUE_FICARAM_FORA || {};
    return {
      titulo: T.sondaT, pergunta: txt(J.PERGUNTA), execucao: txt(J.ESTADO_DA_EXECUCAO),
      juizo: [par('RESULTADO', J.RESULTADO), par('WINDOW_OPEN_NOW', J.WINDOW_OPEN_NOW), par('ACT_NOW', J.ACT_NOW),
        par(T.itens, J.ITENS_COM_O_PAR), par(T.apoios, J.APOIOS_VALIDOS), par('POR_REGIAO_SUSTENTADA', J.POR_REGIAO_SUSTENTADA),
        par(T.fora, Object.keys(F).map(function (k) { return k + ' ' + F[k]; }).join(' · '))],
      itens: (S.ITENS || []).map(function (i) {
        var TE = i.TEMPO || {}, LO = i.LOCAL || {};
        var tr = [].concat(i.TRECHO_NEG || [], i.TRECHO_POS || [], i.TRECHO_CONDICIONAL || []);
        return {
          cab: txt(i.SOURCE_ID) + ' · ' + T.aberta + ' ' + txt(i.ABERTA_AGORA) + ' · ' + T.metodo + ' ' + txt(i.METODO),
          chaves: [par('FACT_TIME', TE.FACT_TIME), par('TEMPORAL_STATE', TE.TEMPORAL_STATE), par(T.luogo, txt(LO.FACT_LOCATION) + ' · ' + txt(LO.ESTADO)),
            par('PAR', txt(i.PAR) + ' · «' + txt(i.PAR_TRECHO) + '»')],
          trechos: tr.map(function (t) { return { t: '«' + txt(t) + '»' }; }),
          lei: txt(i.LEI_W || ''), temLei: !!i.LEI_W,
          prova: prova(i.URL, i.PUBLISHED_AT, T), sala: T.sala + ' ' + txt(i.SALA_CHAVE)
        };
      })
    };
  }

  function fontes(pub, pote, T) {
    var A = pub.ANALISE || {}, N = A.O_QUE_AS_38_ACRESCENTARAM || {}, D = A.D112 || {};
    var lac = pote.LACUNAS_SEM_COMPARTIMENTO || [];
    var porFalta = {};
    lac.forEach(function (g) { var k = txt(g.MISSING_FACT_OR_KEY); porFalta[k] = (porFalta[k] || 0) + 1; });
    return {
      lacTitulo: T.lacT + ' · ' + lac.length, lacLegenda: T.lacLeg,
      lacPorFalta: Object.keys(porFalta).map(function (k) { return par(k, porFalta[k]); }),
      lacExemplo: lac.length ? txt(lac[0].QUESTION_BLOCKED) + ' — ' + txt(lac[0].WHY_EXISTING_MATERIAL_IS_INSUFFICIENT) : '',
      novasTitulo: T.novasT,
      novas: Object.keys(N).filter(function (k) { return k !== 'SINAIS'; }).map(function (k) { return par(k, N[k]); }),
      sinaisTitulo: T.sinais + ' · ' + (N.SINAIS || []).length,
      sinais: (N.SINAIS || []).map(function (s) {
        return { cab: txt(s.SOURCE_ID) + ' · ' + txt(s.KIND), chaves: [par('FACT_TIME', s.FACT_TIME), par(T.idade, s.IDADE_MIN_DIAS), par(T.luogo, s.LOCAL)],
          prova: prova(s.URL, s.PUBLISHED_AT, T) };
      }),
      d112Titulo: T.d112T,
      d112: Object.keys(D).map(function (k) { return par(k, D[k]); })
    };
  }

  var VAZIOS = {
    cruz: { titulo: '', pergunta: '', legenda: '', resumo: [], vias: [], grupos: [] },
    sonda: { titulo: '', pergunta: '', execucao: '', juizo: [], itens: [] },
    fontes: { lacTitulo: '', lacLegenda: '', lacPorFalta: [], lacExemplo: '', novasTitulo: '', novas: [],
      sinaisTitulo: '', sinais: [], d112Titulo: '', d112: [] }
  };

  /* A vista da publicacao para UMA rota. `null` = nada a acrescentar (sem publicacao, pote de outra corrida,
     ou rota que o pote nao reclama). */
  function vm(pub, pote, view, lang) {
    if (!pub || !pote || !pote.COMPARTIMENTOS) return null;
    if (pub.INTELLIGENCE_RUN_ID !== pote.INTELLIGENCE_RUN_ID) return null;
    var lg = lang === 'en' ? 'en' : 'it', T = L[lg];
    var LEITOR = (typeof window !== 'undefined' && window.SINTONIA_POTE_CASCO) || null;
    var comp = view === 'field' ? 'field' : (LEITOR ? LEITOR.compartimentoDaVista(pote, view) : null);
    if (!comp) return null;
    var e = pote.COMPARTIMENTOS[comp] || {};
    var v = cabecalho(pub, pote, T);
    v.comp = comp;
    v.rec = recusados(pote, comp, T);
    /* Cada bloco e calculado so na sua vista; nas outras vai a forma VAZIA com as mesmas chaves, para que
       nenhuma ligacao {{ }} escondida resolva para undefined. */
    v.temCruz = comp === 'portfolio'; v.cruz = v.temCruz ? cruzamentos(pub, pote, T, lg) : VAZIOS.cruz;
    v.temSonda = comp === 'windows'; v.sonda = v.temSonda ? sonda(pub, T) : VAZIOS.sonda;
    v.temFontes = comp === 'sources'; v.fontes = v.temFontes ? fontes(pub, pote, T) : VAZIOS.fontes;
    v.temCampo = comp === 'field';
    v.campo = { titulo: T.campoT, texto: T.campoTx, estado: txt(e.ESTADO) + ' · ' + txt(e.PORQUE_VAZIO), porque: txt(e.PORQUE_TEXTO) };
    return v;
  }

  return { vm: vm, ESTADOS: ESTADOS };
})();
