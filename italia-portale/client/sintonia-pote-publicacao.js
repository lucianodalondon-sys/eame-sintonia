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
   (?pote=local), nada disto se aplica: devolve null.

   CASCO-HOJE-MINIMO-HONESTO (D97: o casco so mostra o que o pote aprovou)
     · Portafoglio: na tela principal so os cruzamentos que SAO objeto do pote; os outros vao para a aba
       «rifiutati», cada um com o motivo que o pote escreveu. O id de cruzamento leva PROVVISORIO (D119).
     · o carimbo da referencia ADAMA vem da porta (publicado.REFERENCIA_ADAMA): nenhuma data escrita aqui.
     · a Label Intelligence e PRODUTO DE FERRAMENTA (publicado.LABEL_INTELLIGENCE), com a data do snapshot.
     · Radar: «0 opportunita difendibili» conta as OPORTUNIDADE do pote; o exemplo e a sonda da analise.
     · Radar Futuro: so fato sobre o futuro com >= 1 chave de dominio provada; o resto e Agenda.
     · contagens por OBJETO DISTINTO (o mesmo objeto em duas gavetas conta uma vez).
     · BANDEIRAS: o legado (V2.1 + demo + snapshot 07/09, e os 44 ITFC) so volta se o dono as ligar. */
window.SINTONIA_POTE_PUBLICACAO = (function () {
  var NAO_SEI = 'NAO SEI';

  /* BANDEIRAS DO DONO · desligadas por omissao. Ligar uma e decisao do dono, e o legado volta SELADO
     («LEGADO 07/09 · sem janela provada»), nunca como se fosse desta corrida. So `true` liga. Um portao
     de browser que mede a interface do legado liga-as pela pagina (window.SINTONIA_BANDEIRAS), nunca
     pelo endereco: um visitante nao chega ao legado por um link. */
  var BANDEIRAS = { LEGADO_V21_VISIVEL: false, ITFC_LEGADO_VISIVEL: false };
  function bandeira(nome) {
    var W = (typeof window !== 'undefined' && window.SINTONIA_BANDEIRAS) || {};
    return (Object.prototype.hasOwnProperty.call(W, nome) ? W[nome] : BANDEIRAS[nome]) === true;
  }

  /* As chaves que fazem de um fato sobre o futuro um fato de DOMINIO: cultura, praga, substancia,
     produto ou registo. Data e lugar sozinhos fazem Agenda, nao Radar. */
  var DOMINIO = ['CROP_ID', 'ISSUE_ID', 'TARGET_ID', 'ACTIVE_INGREDIENT_ID', 'MOLECULE', 'PRODUCT_ID',
    'ADAMA_PRODUCT_ID', 'REGISTRATION_VERSION', 'T4_REGISTRATION_EVIDENCE_ID', 'AUTHORIZATION_EVIDENCE_ID'];
  function provado(v) { return v !== null && v !== undefined && v !== '' && !/^N[AÃ]O[ _]SEI/.test(String(v)); }
  function chavesDeDominio(o) {
    var C = (o && o.CHAVES) || {};
    return DOMINIO.filter(function (k) { return provado(C[k]); });
  }
  var AMBAR = '#F5B317', BRANCO = '#FFFFFF', CINZA = '#C9C3C1', APAGADO = '#8F8886';

  var L = {
    it: {
      faixa: 'PUBBLICATO PER DECISIONE {D} DEL PROPRIETARIO · {DATA} — corsa {R} della Intelligence. I dati restano EXPERIMENTAL: si leggono come esperimento, non come raccomandazione.',
      corsa: 'corsa', rodada: 'giro', corte: 'copia della Sala', ready: 'elementi READY letti', motor: 'motore',
      gerador: 'generatore del pote', conferir: 'verifica del pote (dal manifesto)', sha: 'SHA256 del pote',
      shaNao: 'NON CORRISPONDE al manifesto', shaSim: 'corrisponde al manifesto', shaCrlf: 'corrisponde al manifesto dopo il solo cambio di fine riga (CRLF nel manifesto, LF nel Git) — nessun altro byte', conteggi: 'conteggi per compartimento: corrispondono al manifesto',
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
      d112T: 'LUOGO SOLO DAL TESTO SCRITTO (D112)', campoT: 'Rete Commerciale di Campo · SIMULATO — la simulazione non è mostrata',
      campoTx: 'Questa vista reggeva su persone e messaggi SIMULATI. Con il pote pubblicato, mostra ciò che il pote scrive:',
      prov: 'ID PROVVISORIO (D119: identità stabile ancora in ricerca)',
      cruzPoteT: 'INCROCI CHE SONO OGGETTO DEL POTE · {N} di {T}', cruzPoteLeg: 'Solo questi hanno la prova che il pote esige. Gli altri restano nella scheda «rifiutati», con il motivo.',
      abaPote: 'NEL POTE', abaRec: 'RIFIUTATI', recCruzT: 'INCROCI RIFIUTATI DAL POTE O ASSENTI · {N}', recCruzLeg: 'Non sono oggetti del pote: non si leggono come risultato. Il motivo è quello che il pote ha scritto.',
      refT: 'referenza ADAMA', refReg: 'registro del', refChk: 'ultima verifica', refNs: 'NON SO — la porta della referenza non ha letto',
      frescor: { FRESCA: 'aggiornata', PODE_ESTAR_DESATUALIZADO: 'PUÒ ESSERE NON AGGIORNATO', AUTORIZACAO_A_CONFIRMAR: 'AUTORIZZAZIONE DA CONFERMARE' },
      refDecl: 'uso dichiarato a livello di prodotto (spettro · DECLARACAO_DE_PRODUTO): da confermare, mai «autorizzato»',
      liT: 'PRODOTTO DI STRUMENTO · {NOME} — non è una corsa della Intelligence',
      liSnap: 'istantanea del registro', liRun: 'esecuzione dello strumento', liSelo: 'sigillo', liN: 'registri',
      liNs: 'NON SO — il prodotto dello strumento non corrisponde al registro pubblicato: le etichette non sono mostrate',
      radarT: '{N} OPPORTUNITÀ DIFENDIBILI IN QUESTA CORSA', radarEx: 'ESEMPIO · perché zero non è un difetto', radarVer: 'la sonda completa è nelle Finestre Colturali',
      agT: 'AGENDA · EVENTI DATATI — non è il Radar Futuro', agLeg: 'Fatti sul futuro senza chiave di dominio provata (coltura, avversità, sostanza, prodotto, registro): solo data e luogo.',
      futT: 'FATTI PRESENTI SUL FUTURO CON CHIAVE DI DOMINIO PROVATA · {N}', futVazio: 'Nessun fatto sul futuro di questa corsa porta una chiave di dominio provata: zero qui non prova assenza nel mondo.',
      selo: 'LEGADO 07/09 · SENZA FINESTRA PROVATA — acceso dal proprietario ({B}); non è di questa corsa',
      fechado: 'NON SO · questa scheda legge il modello precedente (V2.1 + demo), che con il pote pubblicato resta spento ({B} = false). Il pote non ha un oggetto per questa scheda.',
      semPote: 'NON SO · il pote pubblicato non è arrivato (o è stato rifiutato): niente demo e niente istantanea al suo posto.',
      buscaT: 'oggetti del pote'
    },
    en: {
      faixa: 'PUBLISHED BY OWNER DECISION {D} · {DATA} — Intelligence run {R}. The data stay EXPERIMENTAL: read them as an experiment, not as a recommendation.',
      corsa: 'run', rodada: 'round', corte: 'Sala copy', ready: 'READY items read', motor: 'engine',
      gerador: 'pot generator', conferir: 'pot check (from the manifest)', sha: 'pot SHA256',
      shaNao: 'DOES NOT MATCH the manifest', shaSim: 'matches the manifest', shaCrlf: 'matches the manifest after the line-ending change only (CRLF in the manifest, LF in Git) — no other byte', conteggi: 'counts per compartment: match the manifest',
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
      d112T: 'PLACE ONLY FROM THE WRITTEN TEXT (D112)', campoT: 'Field Sales Network · SIMULATED — the simulation is not shown',
      campoTx: 'This view stood on SIMULATED people and messages. With the published pot, it shows what the pot writes:',
      prov: 'PROVISIONAL ID (D119: stable identity still under research)',
      cruzPoteT: 'CROSSINGS THAT ARE POT OBJECTS · {N} of {T}', cruzPoteLeg: 'Only these carry the proof the pot requires. The others stay in the «refused» tab, with the reason.',
      abaPote: 'IN THE POT', abaRec: 'REFUSED', recCruzT: 'CROSSINGS REFUSED BY THE POT OR ABSENT · {N}', recCruzLeg: 'They are not pot objects: do not read them as a result. The reason is the one the pot wrote.',
      refT: 'ADAMA reference', refReg: 'register of', refChk: 'last check', refNs: 'DO NOT KNOW — the reference gateway did not read',
      frescor: { FRESCA: 'fresh', PODE_ESTAR_DESATUALIZADO: 'MAY BE OUT OF DATE', AUTORIZACAO_A_CONFIRMAR: 'AUTHORISATION TO BE CONFIRMED' },
      refDecl: 'use declared at product level (spectrum · DECLARACAO_DE_PRODUTO): to be confirmed, never «authorised»',
      liT: 'TOOL PRODUCT · {NOME} — not an Intelligence run',
      liSnap: 'register snapshot', liRun: 'tool run', liSelo: 'seal', liN: 'records',
      liNs: 'DO NOT KNOW — the tool product does not match the published record: labels are not shown',
      radarT: '{N} DEFENSIBLE OPPORTUNITIES IN THIS RUN', radarEx: 'EXAMPLE · why zero is not a defect', radarVer: 'the full probe is in Crop Windows',
      agT: 'AGENDA · DATED EVENTS — not the Future Radar', agLeg: 'Facts about the future with no proven domain key (crop, pest, substance, product, registration): only date and place.',
      futT: 'PRESENT FACTS ABOUT THE FUTURE WITH A PROVEN DOMAIN KEY · {N}', futVazio: 'No fact about the future in this run carries a proven domain key: zero here does not prove absence in the world.',
      selo: 'LEGACY 07/09 · NO WINDOW PROVEN — switched on by the owner ({B}); not from this run',
      fechado: 'DO NOT KNOW · this page reads the previous model (V2.1 + demo), which stays off with the published pot ({B} = false). The pot has no object for this page.',
      semPote: 'DO NOT KNOW · the published pot did not arrive (or was refused): no demo and no snapshot in its place.',
      buscaT: 'pot objects'
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


  /* ROTULOS · o nome humano de cada CODIGO que a tela mostra como rotulo. O codigo NAO some: vai ao lado
     («tempo del fatto · FACT_TIME»), porque e ele que se procura no pote. Codigo sem entrada aqui passa
     como esta — um rotulo inventado seria pior do que o codigo. */
  var ROTULOS = {
    ACTIVE_INGREDIENT_ID: ['sostanza attiva', 'active ingredient'], ADAMA_PRODUCT_ID: ['prodotto ADAMA', 'ADAMA product'],
    AUTHORIZATION_EVIDENCE_ID: ['prova di autorizzazione', 'authorisation evidence'], COMPANY_ID: ['azienda', 'company'],
    CROP_ID: ['coltura', 'crop'], DATE_OR_STAGE: ['data o fase', 'date or stage'], DOI: ['DOI', 'DOI'],
    FACT_LOCATION: ['luogo del fatto', 'place of the fact'], FACT_TIME: ['tempo del fatto', 'fact time'],
    FACT_TIME_BASIS: ['base del tempo del fatto', 'basis of the fact time'], INSTITUTION_ID: ['istituzione', 'institution'],
    ISSUE_ID: ['avversità', 'issue'], ITENS_LIDOS: ['elementi letti', 'items read'],
    ITENS_QUE_PASSARAM_G0: ['elementi passati da G0', 'items that passed G0'], MARKET_PLACE_ID: ['piazza di mercato', 'market place'],
    MARKET_STAGE: ['fase di mercato', 'market stage'], MOLECULE: ['molecola', 'molecule'],
    OBJETOS_PRODUZIDOS: ['oggetti prodotti', 'objects produced'], PERIOD: ['periodo', 'period'], PRICE: ['prezzo', 'price'],
    PRODUCT_ID: ['prodotto', 'product'], QUOTE_OR_TRANSCRIPT: ['citazione o trascrizione', 'quote or transcript'],
    REGION_ID: ['regione', 'region'], REGISTRATION_VERSION: ['versione della registrazione', 'registration version'],
    RESEARCHER_ORCID: ['ricercatore (ORCID)', 'researcher (ORCID)'], SOURCE_ID: ['fonte', 'source'],
    SPEAKER_ID: ['chi parla', 'speaker'], SPEAKER_ROLE: ['ruolo di chi parla', 'speaker role'],
    STUDY_LOCATION: ['luogo dello studio', 'study location'], STUDY_PERIOD: ['periodo dello studio', 'study period'],
    T4_REGISTRATION_EVIDENCE_ID: ['prova di registrazione', 'registration evidence'], TARGET_ID: ['bersaglio', 'target'],
    TIME_WINDOW: ['finestra temporale', 'time window'], TRIAL_ID: ['prova sperimentale', 'trial'], UNIT: ['unità', 'unit'],
    CROSSING_STATE: ['stato dell\'incrocio', 'crossing state'], CULTURAS_DO_DOCUMENTO_FONTE: ['colture nel documento', 'crops in the document'],
    CULTURAS_QUE_CASAM_COM_O_ROTULO: ['colture che combaciano con l\'etichetta', 'crops matching the label'],
    ENTITY_SOURCE_DO_CROP_ID: ['origine della coltura', 'origin of the crop'], LOCAL_D112: ['luogo (D112)', 'place (D112)'],
    NIVEL: ['livello', 'level'], PILOTO_CROSSING_ID: ['incrocio del pilota', 'pilot crossing'],
    PRODUTOS_ADAMA_COM_A_SUBSTANCIA: ['prodotti ADAMA con la sostanza', 'ADAMA products with the substance'], VIA: ['via', 'route'],
    CROSSING: ['incrocio', 'crossing'], FATO_PRESENTE_SOBRE_O_FUTURO: ['fatto presente sul futuro', 'present fact about the future'],
    RENDIMENTO_DE_FONTE: ['resa della fonte', 'source yield'], SINAL: ['segnale', 'signal'],
    OPORTUNIDADE: ['opportunità', 'opportunity'], FINDING: ['scoperta', 'finding'],
    SOURCE_HEAD: ['origine della corsa', 'run origin'], RESULT_STATE: ['stato della corsa', 'run state'],
    RESULTADO: ['esito', 'outcome'], WINDOW_OPEN_NOW: ['finestra aperta ora', 'window open now'], ACT_NOW: ['agire ora', 'act now'],
    POR_REGIAO_SUSTENTADA: ['per regione sostenuta', 'by supported region'], TEMPORAL_STATE: ['stato temporale', 'temporal state'],
    PAR: ['coppia', 'pair'], ENTITY_SOURCE_NO_READY: ['origine dell\'entità nel READY', 'entity source in READY'],
    LOCATION_SOURCE_NO_READY: ['origine del luogo nel READY', 'location source in READY'],
    LOCAL_POR_ESTADO: ['luogo per stato', 'place by state'], LOCAL_POR_ESTADO_SO_NOVAS: ['luogo per stato (solo le nuove)', 'place by state (new only)'],
    LOCAL_NAO_SUSTENTADO: ['luogo non sostenuto', 'unsupported place'], ITENS_COM_PARES_POR_SECAO: ['elementi con coppie per sezione', 'items with pairs by section'],
    PARES_POR_SECAO: ['coppie per sezione', 'pairs by section'], ITENS: ['elementi', 'items'], FONTES: ['fonti', 'sources'],
    FONTES_CANDIDATAS: ['fonti candidate', 'candidate sources'], UNIVERSO: ['universo', 'universe'],
    COM_CULTURA: ['con coltura', 'with crop'], COM_PRAGA: ['con avversità', 'with pest'],
    COM_PARES_POR_SECAO: ['con coppie per sezione', 'with pairs by section'], COM_PUBLISHED_AT: ['con data di pubblicazione', 'with publication date'],
    PUBLICADAS_ANTES_DE_2026: ['pubblicate prima del 2026', 'published before 2026'], FORA_DE_ITALIA: ['fuori dall\'Italia', 'outside Italy'],
    CROSSINGS: ['incroci', 'crossings'],
    PARTIAL_GRAO_INCOMPATIVEL: ['grana incompatibile', 'incompatible grain'], POSSIBLE_ANSWER_NO: ['no, non è nell\'etichetta letta', 'no, not in the label read'],
    POSSIBLE_ANSWER_YES_A_CONFIRMAR: ['sì, da confermare', 'yes, to be confirmed'], NOT_POSSIBLE: ['non possibile', 'not possible'],
    NO_DEFENSIBLE_ACTION_YET: ['nessuna azione difendibile ancora', 'no defensible action yet'],
    PAR_SO_DOCUMENTO: ['coppia solo nel documento', 'pair only in the document'], TEMPO_NAO_CURRENT: ['tempo non attuale', 'time not current'],
    SEM_MEDICAO: ['senza misura dichiarata', 'no declared measurement'], UNKNOWN_WINDOW: ['finestra sconosciuta', 'unknown window'],
    ANCORADO: ['ancorato (data del fatto provata)', 'anchored (fact date proven)']
  };
  var LG = 'it';
  /* O VALOR que e um codigo leva o nome ao lado; um objeto de contagens vira «nome · CODIGO n». O valor original
     nao muda — so a maneira de o ler. */
  function valor(v) {
    if (typeof v === 'string' && ROTULOS[v]) return rotulo(v, LG);
    if (v && typeof v === 'object' && !Array.isArray(v)) {
      return Object.keys(v).map(function (k) { return rotulo(k, LG) + ' ' + txt(v[k]); }).join(' · ');
    }
    return txt(v);
  }
  function rotulo(k, lang) {
    var r = ROTULOS[k];
    return r ? r[lang === 'en' ? 1 : 0] + ' · ' + k : k;
  }

  function txt(v) {
    if (v === null || v === undefined || v === '') return NAO_SEI;
    if (Array.isArray(v)) return v.length ? v.map(txt).join(' · ') : '—';
    return typeof v === 'string' ? v : (typeof v === 'number' || typeof v === 'boolean') ? String(v) : JSON.stringify(v);
  }
  function ns(v) { return /^N[AÃ]O[ _]SEI/.test(txt(v)); }
  function par(k, v) { return { k: k, v: valor(v), color: ns(v) ? AMBAR : BRANCO }; }
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
    /* So as duas formas que o publicador aceita contam como «confere»; qualquer outra coisa e ambar. */
    var shaModo = pub.SHA256_CONFERENCIA;
    var shaOk = pub.SHA256_CONFERE_COM_O_MANIFESTO === true &&
      (shaModo === 'IGUAL_BYTE_A_BYTE' || shaModo === 'IGUAL_APOS_FIM_DE_LINHA_CRLF');
    var shaTxt = shaModo === 'IGUAL_APOS_FIM_DE_LINHA_CRLF' ? T.shaCrlf : T.shaSim;
    return {
      faixa: T.faixa.replace('{D}', txt(D.ID)).replace('{DATA}', quando(D.DATA)).replace('{R}', txt(pub.RODADA)),
      decisao: '«' + txt(D.TEXTO) + '» — ' + txt(D.ID),
      meta: [
        par(T.rodada, pub.RODADA), par(T.corsa, pote.INTELLIGENCE_RUN_ID), par(T.corte, quando(C.COPIA_DA_SALA_EM)),
        par(T.ready, C.READY), par(T.motor, txt(SH.MOTOR_RAMO) + ' @ ' + txt(SH.MOTOR).slice(0, 8)),
        par(T.gerador, pub.GERADOR_DO_POTE), par(T.conferir, pub.CONFERIR_POTE_DO_DONO),
        { k: T.sha, v: txt(pub.POTE_SHA256).slice(0, 16) + '… · ' + (shaOk ? shaTxt : T.shaNao + ' (' + txt(pub.SHA256_DECLARADO_NO_MANIFESTO).slice(0, 16) + '…) · ' + T.conteggi),
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
    var porEstado = {};
    ESTADOS.forEach(function (E) { porEstado[E.k] = E; });
    function linha(c) {
      var E = porEstado[c.ESTADO_R7] || { k: c.ESTADO_R7, marca: '', it: txt(c.ESTADO_R7), en: txt(c.ESTADO_R7), color: AMBAR, traco: 'dashed' };
      var F = c.FONTE || {}, I = c.INTERPRETACAO || {}, LO = F.LOCAL || {};
      var r = recusa[c.OBJETO_ID];
      var candidata = c.VIA === 'EXTENSAO_DECLARADA';
      var dentro = !!noPote[c.OBJETO_ID];
      return {
        /* O estado vai LITERAL ao lado do nome: e o codigo que a Intelligence escreveu. */
        id: txt(c.OBJETO_ID), prov: T.prov, estado: E.k, estadoNome: E[lang] + ' · ' + txt(c.ESTADO_R7), color: E.color, traco: E.traco,
        marca: E.marca, temMarca: !!E.marca, noPote: dentro,
        via: candidata ? T.viaC : T.viaP, viaCodigo: txt(c.VIA), candidata: candidata,
        viaColor: candidata ? AMBAR : CINZA,
        pote: dentro ? T.nel : (r ? T.rif + ' · ' + txt(r.MOTIVO) + ': ' + txt(r.DETALHE) : T.fuori),
        motivo: dentro ? '' : (r ? txt(r.MOTIVO) : 'AUSENTE_DO_POTE'),
        poteColor: dentro ? BRANCO : AMBAR,
        chaves: [par(T.sost, c.SUBSTANCIA), par(rotulo('SOURCE_ID', lang), c.SOURCE_ID), par(T.colDoc, F.CULTURA_NO_READY),
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
    }
    /* A TELA PRINCIPAL: so o que e objeto do pote (D97). A ordem e a da analise. */
    var principais = C.filter(function (c) { return noPote[c.OBJETO_ID]; }).map(linha);
    /* A ABA «RIFIUTATI»: o resto, agrupado pelo estado que a Intelligence lhe deu, cada um com o motivo. */
    var fora = C.filter(function (c) { return !noPote[c.OBJETO_ID]; });
    var grupos = ESTADOS.map(function (E) {
      var linhas = fora.filter(function (c) { return c.ESTADO_R7 === E.k; }).map(linha);
      return { k: E.k, titulo: E[lang] + ' · ' + E.k + ' · ' + linhas.length, color: E.color, linhas: linhas, tem: linhas.length > 0 };
    });
    var porMotivo = {};
    fora.forEach(function (c) { var r = recusa[c.OBJETO_ID]; var k = r ? txt(r.MOTIVO) : 'AUSENTE_DO_POTE'; porMotivo[k] = (porMotivo[k] || 0) + 1; });
    var porVia = R.POR_VIA || {};
    return {
      titulo: T.cruzPoteT.replace('{N}', String(principais.length)).replace('{T}', txt(R.TOTAL)),
      pergunta: T.cruzQ, legenda: T.cruzLeg, legendaPote: T.cruzPoteLeg,
      principais: principais, temPrincipais: principais.length > 0, nPrincipais: principais.length,
      abaPote: T.abaPote + ' · ' + principais.length, abaRec: T.abaRec + ' · ' + fora.length,
      recTitulo: T.recCruzT.replace('{N}', String(fora.length)), recLegenda: T.recCruzLeg, nRecusados: fora.length,
      recMotivos: Object.keys(porMotivo).map(function (k) { return par(k, porMotivo[k]); }),
      resumo: ESTADOS.map(function (E) { return { k: E.k, n: txt((R.POR_ESTADO || {})[E.k]), nome: E[lang], color: E.color }; }),
      vias: [par(T.viaP, porVia.PILOTO), par(T.viaC, porVia.EXTENSAO_DECLARADA)],
      grupos: grupos
    };
  }

  /* O CARIMBO DA REFERENCIA · as datas sao as da porta (publicado.REFERENCIA_ADAMA); esta funcao so as
     escreve em dd/mm. Porta que nao leu = NAO SEI em ambar, nunca uma data. */
  function ddmm(v) { var m = /^(\d{4})-(\d{2})-(\d{2})/.exec(txt(v)); return m ? m[3] + '/' + m[2] : NAO_SEI; }
  function carimboRef(pub, T) {
    var R = (pub && pub.REFERENCIA_ADAMA) || {};
    if (R.ESTADO !== 'LIDA') return { lida: false, texto: T.refT + ': ' + T.refNs + (R.PORQUE ? ' (' + txt(R.PORQUE) + ')' : ''), color: AMBAR, decl: T.refDecl, frescor: NAO_SEI };
    var f = txt(R.ESTADO_FRESCOR);
    return {
      lida: true, frescor: f,
      texto: T.refT + ': ' + T.refReg + ' ' + ddmm(R.DATA_DA_EDICAO_REGISTRO) + ', ' + T.refChk + ' ' + ddmm(R.ULTIMA_CHECAGEM_OK) +
        ', ' + ((T.frescor || {})[f] || f) + ' · ' + f + ' · ' + txt(R.EDICAO_REGISTRO),
      color: f === 'FRESCA' ? BRANCO : AMBAR, decl: T.refDecl
    };
  }

  /* A LABEL INTELLIGENCE COMO PRODUTO DE FERRAMENTA · registada pelo publicador. So se desenha se o
     payload carregado for o do registo (o mesmo selo); senao NAO SEI. */
  function labelFerramenta(pub, T) {
    var LI = pub && pub.LABEL_INTELLIGENCE;
    if (!LI) return null;
    var W = (typeof window !== 'undefined') ? window : {};
    var carregado = ((W.ITALY_LABEL_INTELLIGENCE || {}).PRODUCED_BY || {}).CONTENT_SHA256;
    var confere = !!carregado && carregado === LI.CONTENT_SHA256;
    var S = LI.SNAPSHOT || {}, N = LI.CONTAGENS || {};
    var dd = /^(\d{4})(\d{2})(\d{2})$/.exec(txt(S.DATA_DATE));
    var R = (pub.REFERENCIA_ADAMA) || {};
    var f = txt(LI.ESTADO_FRESCOR);
    return {
      confere: confere, naoConfere: !confere, ns: T.liNs,
      titulo: T.liT.replace('{NOME}', txt(LI.NOME)),
      meta: [par(T.liSnap, (dd ? dd[3] + '/' + dd[2] : NAO_SEI) + ' · ' + txt(S.DATA_SNAPSHOT_ID)),
        par(T.refChk, LI.EDICAO_E_A_DA_PORTA ? ddmm(LI.ULTIMA_CHECAGEM_OK) : NAO_SEI),
        { k: 'ESTADO_FRESCOR', v: ((T.frescor || {})[f] || f) + ' · ' + f, color: f === 'FRESCA' ? BRANCO : AMBAR },
        par(T.liRun, txt(LI.FERRAMENTA) + ' · ' + txt(LI.RUN)),
        par(T.liSelo, txt(LI.CONTENT_SHA256).slice(0, 16) + '…'),
        par(T.liN, N)],
      decl: T.refDecl, lei: txt(LI.LEI), nProdutos: typeof N.products === 'number' ? N.products : NAO_SEI,
      mesmaEdicao: R.EDICAO_REGISTRO === S.DATA_SNAPSHOT_ID
    };
  }

  /* O RADAR · «0» e contado: as OPORTUNIDADE do compartimento meeting do pote. O exemplo e a sonda da
     analise tal como a Intelligence a julgou (RESULTADO, WINDOW_OPEN_NOW, ACT_NOW). */
  function radar(pub, pote, T) {
    var e = pote.COMPARTIMENTOS.meeting || {};
    var n = (e.OBJETOS || []).filter(function (o) { return o.ESPECIE === 'OPORTUNIDADE'; }).length;
    var J = (((pub.ANALISE || {}).CORTE_VERTICAL) || {}).JULGAMENTO_DA_SONDA || {};
    return {
      n: n, titulo: T.radarT.replace('{N}', String(n)),
      porque: txt(e.PORQUE_VAZIO) + ' — ' + txt(e.PORQUE_TEXTO), temPorque: !!e.PORQUE_VAZIO,
      exTitulo: T.radarEx, pergunta: txt(J.PERGUNTA), temExemplo: !!J.RESULTADO,
      resultado: rotulo('RESULTADO', T.lg) + ': ' + valor(J.RESULTADO),
      juizo: [par(rotulo('WINDOW_OPEN_NOW', T.lg), J.WINDOW_OPEN_NOW), par(rotulo('ACT_NOW', T.lg), J.ACT_NOW),
        par(T.itens, J.ITENS_COM_O_PAR), par(T.apoios, J.APOIOS_VALIDOS), par(T.fora, J.PORQUE_FICARAM_FORA)],
      ver: T.radarVer
    };
  }

  function sonda(pub, T) {
    var S = ((pub.ANALISE || {}).CORTE_VERTICAL) || {}, J = S.JULGAMENTO_DA_SONDA || {}, F = J.PORQUE_FICARAM_FORA || {};
    return {
      titulo: T.sondaT, pergunta: txt(J.PERGUNTA), execucao: txt(J.ESTADO_DA_EXECUCAO),
      juizo: [par(rotulo('RESULTADO', T.lg), J.RESULTADO), par(rotulo('WINDOW_OPEN_NOW', T.lg), J.WINDOW_OPEN_NOW), par(rotulo('ACT_NOW', T.lg), J.ACT_NOW),
        par(T.itens, J.ITENS_COM_O_PAR), par(T.apoios, J.APOIOS_VALIDOS), par(rotulo('POR_REGIAO_SUSTENTADA', T.lg), J.POR_REGIAO_SUSTENTADA),
        par(T.fora, F)],
      itens: (S.ITENS || []).map(function (i) {
        var TE = i.TEMPO || {}, LO = i.LOCAL || {};
        var tr = [].concat(i.TRECHO_NEG || [], i.TRECHO_POS || [], i.TRECHO_CONDICIONAL || []);
        return {
          cab: txt(i.SOURCE_ID) + ' · ' + T.aberta + ' ' + txt(i.ABERTA_AGORA) + ' · ' + T.metodo + ' ' + txt(i.METODO),
          chaves: [par(rotulo('FACT_TIME', T.lg), TE.FACT_TIME), par(rotulo('TEMPORAL_STATE', T.lg), TE.TEMPORAL_STATE), par(T.luogo, txt(LO.FACT_LOCATION) + ' · ' + txt(LO.ESTADO)),
            par(rotulo('PAR', T.lg), txt(i.PAR) + ' · «' + txt(i.PAR_TRECHO) + '»')],
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
      lacPorFalta: Object.keys(porFalta).map(function (k) { return par(k.split(' · ').map(function (x) { return rotulo(x.split(':')[0], T.lg) + (x.indexOf(':') > 0 ? ':' + x.split(':')[1] : ''); }).join(' + '), porFalta[k]); }),
      lacExemplo: lac.length ? txt(lac[0].QUESTION_BLOCKED) + ' — ' + txt(lac[0].WHY_EXISTING_MATERIAL_IS_INSUFFICIENT) : '',
      novasTitulo: T.novasT,
      novas: Object.keys(N).filter(function (k) { return k !== 'SINAIS'; }).map(function (k) { return par(rotulo(k, T.lg), N[k]); }),
      sinaisTitulo: T.sinais + ' · ' + (N.SINAIS || []).length,
      sinais: (N.SINAIS || []).map(function (s) {
        return { cab: txt(s.SOURCE_ID) + ' · ' + txt(s.KIND), chaves: [par(rotulo('FACT_TIME', T.lg), s.FACT_TIME), par(T.idade, s.IDADE_MIN_DIAS), par(T.luogo, s.LOCAL)],
          prova: prova(s.URL, s.PUBLISHED_AT, T) };
      }),
      d112Titulo: T.d112T,
      d112: Object.keys(D).map(function (k) { return par(rotulo(k, T.lg), D[k]); })
    };
  }

  var VAZIOS = {
    cruz: { titulo: '', pergunta: '', legenda: '', legendaPote: '', principais: [], temPrincipais: false, nPrincipais: 0,
      abaPote: '', abaRec: '', recTitulo: '', recLegenda: '', nRecusados: 0, recMotivos: [], resumo: [], vias: [], grupos: [] },
    sonda: { titulo: '', pergunta: '', execucao: '', juizo: [], itens: [] },
    fontes: { lacTitulo: '', lacLegenda: '', lacPorFalta: [], lacExemplo: '', novasTitulo: '', novas: [],
      sinaisTitulo: '', sinais: [], d112Titulo: '', d112: [] },
    radar: { n: 0, titulo: '', porque: '', temPorque: false, exTitulo: '', pergunta: '', temExemplo: false, resultado: '', juizo: [], ver: '' },
    ref: { lida: false, texto: '', color: BRANCO, decl: '', frescor: '' }
  };

  /* A vista da publicacao para UMA rota. `null` = nada a acrescentar (sem publicacao, pote de outra corrida,
     ou rota que o pote nao reclama). */
  function vm(pub, pote, view, lang) {
    if (!pub || !pote || !pote.COMPARTIMENTOS) return null;
    if (pub.INTELLIGENCE_RUN_ID !== pote.INTELLIGENCE_RUN_ID) return null;
    var lg = lang === 'en' ? 'en' : 'it', T = Object.assign({ lg: lg }, L[lg]);
    LG = lg;
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
    v.temRadar = comp === 'meeting'; v.radar = v.temRadar ? radar(pub, pote, T) : VAZIOS.radar;
    v.temRef = comp === 'portfolio'; v.ref = v.temRef ? carimboRef(pub, T) : VAZIOS.ref;
    v.temCampo = comp === 'field';
    v.campo = { titulo: T.campoT, texto: T.campoTx, estado: txt(e.ESTADO) + ' · ' + txt(e.PORQUE_VAZIO), porque: txt(e.PORQUE_TEXTO) };
    return v;
  }

  /* OBJETOS DISTINTOS · o mesmo objeto em duas gavetas (ex.: um fato sobre o futuro que tambem esta no
     Archivio) e UM objeto. Soma de gavetas nunca e contagem. */
  function distintos(pote) {
    var vistos = {};
    Object.keys((pote && pote.COMPARTIMENTOS) || {}).forEach(function (k) {
      (pote.COMPARTIMENTOS[k].OBJETOS || []).forEach(function (o) { vistos[o.OBJETO_ID] = true; });
    });
    return Object.keys(vistos).length;
  }

  /* A BUSCA COM O POTE · procura so nos objetos do pote (um resultado por objeto distinto), no que o pote
     escreve: id, especie, chaves, porque, e a prova (fonte, documento, URL). Devolve a gaveta onde o objeto
     aparece primeiro, na ordem dos doze compartimentos. */
  function busca(pote, q) {
    var dobrar = function (x) { return String(x == null ? '' : x).toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, ''); };
    var Q = dobrar(q).trim();
    if (Q.length < 2 || !pote || !pote.COMPARTIMENTOS) return [];
    var vistos = {}, out = [];
    Object.keys(pote.COMPARTIMENTOS).forEach(function (k) {
      (pote.COMPARTIMENTOS[k].OBJETOS || []).forEach(function (o) {
        if (vistos[o.OBJETO_ID]) return;
        var prov = (o.PROVA || []).map(function (p) { return [p.SOURCE_ID, p.DOCUMENT_ID, p.URL, p.FACT_TIME].join(' '); }).join(' ');
        var palheiro = dobrar([o.OBJETO_ID, o.ESPECIE, JSON.stringify(o.CHAVES || {}), JSON.stringify(o.FORA_DO_CONTRATO || {}), o.PORQUE, prov].join(' '));
        if (palheiro.indexOf(Q) < 0) return;
        vistos[o.OBJETO_ID] = true;
        out.push({ compartimento: k, objeto: o });
      });
    });
    return out;
  }

  return { vm: vm, ESTADOS: ESTADOS, rotulo: rotulo, valor: function (v, lang) { LG = lang === 'en' ? 'en' : 'it'; return valor(v); },
    BANDEIRAS: BANDEIRAS, bandeira: bandeira, DOMINIO: DOMINIO, chavesDeDominio: chavesDeDominio,
    distintos: distintos, busca: busca, carimboRef: function (pub, lang) { return carimboRef(pub, L[lang === 'en' ? 'en' : 'it']); },
    labelFerramenta: function (pub, lang) { var lg = lang === 'en' ? 'en' : 'it'; return labelFerramenta(pub, Object.assign({ lg: lg }, L[lg])); },
    textos: function (lang) { return L[lang === 'en' ? 'en' : 'it']; } };
})();
