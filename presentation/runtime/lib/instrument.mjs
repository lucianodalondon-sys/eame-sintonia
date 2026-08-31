// Instrumentacao da SAIDA do casco canonico.
//
// O casco V8 nao tem ponto de entrada de dado: os literais estao escritos
// dentro do index.html. Este modulo troca SOMENTE blocos de dado por leituras
// do bundle real. Nao move um pixel, nao renomeia um componente, nao cria
// card. Cada troca precisa casar EXATAMENTE UMA VEZ — se casar zero ou duas,
// o build para, porque um casco diferente do medido nao pode ser publicado
// em silencio.

/**
 * Acha a INSTRUCAO inteira que comeca em `start` e termina no `;` de topo.
 *
 * Nao basta fechar o colchete: no casco quase todo literal termina em
 * `].map(...)`. Cortar so ate o `]` deixaria um `.map` orfao — foi exatamente
 * assim que a primeira tentativa quebrou. Entao a varredura acompanha ( ) [ ]
 * { } e strings, e so para no ponto e virgula em profundidade zero.
 */
function block(src, start) {
  const i = src.indexOf(start)
  if (i < 0) throw new Error(`FAIL_CLOSED · marcador nao encontrado: ${start.slice(0, 60)}`)
  if (src.indexOf(start, i + 1) >= 0) throw new Error(`FAIL_CLOSED · marcador ambiguo: ${start.slice(0, 60)}`)

  const OPEN = '([{', CLOSE = ')]}'
  let depth = 0, quote = null
  for (let j = i; j < src.length; j++) {
    const ch = src[j]
    if (quote) {
      if (ch === '\\') { j++; continue }
      if (ch === quote) quote = null
      continue
    }
    if (ch === "'" || ch === '"' || ch === '`') { quote = ch; continue }
    if (OPEN.includes(ch)) depth++
    else if (CLOSE.includes(ch)) depth--
    else if (ch === ';' && depth === 0) return { from: i, to: j + 1 }
  }
  throw new Error(`FAIL_CLOSED · instrucao nao termina: ${start.slice(0, 60)}`)
}

function replaceBlock(src, start, replacement, log) {
  const { from, to } = block(src, start)
  log.push({ patch: start.trim().slice(0, 48), bytes_out: to - from, bytes_in: replacement.length })
  return src.slice(0, from) + replacement + src.slice(to)
}

function replaceOnce(src, find, replacement, label, log) {
  const n = src.split(find).length - 1
  if (n !== 1) throw new Error(`FAIL_CLOSED · "${label}" casou ${n}x (esperado 1)`)
  log.push({ patch: label, bytes_out: find.length, bytes_in: replacement.length })
  return src.replace(find, replacement)
}

export function instrument(html) {
  const log = []
  let out = html

  // 1 · bundle real carregado ANTES do runtime do casco
  out = replaceOnce(out,
    '<script src="./support.js"',
    '<script src="./data/sintonia-eame-snapshot.js"></script>\n<script src="./data/ui-i18n.js"></script>\n<script src="./support.js"',
    'inject:snapshot-script', log)

  // 2a · idioma da interface: nasce da preferencia salva, nao fixo em 'pt'
  out = replaceOnce(out,
    "lang: this.props.idiomaInicial || 'pt',",
    "lang: this.props.idiomaInicial || (window.__INIT_LANG__ ? window.__INIT_LANG__() : 'pt'),",
    'i18n:lang-inicial', log)

  // 2b · trocar idioma move as DUAS camadas na mesma acao: conteudo (H9, via
  //      __T__ no RAW) e chrome da interface (via __UI_LANG__).
  out = replaceOnce(out,
    "Object.keys(langs).forEach(k => { setLang[k] = () => this.set({ lang: k, langOpen: false }); });",
    "Object.keys(langs).forEach(k => { setLang[k] = () => { if (window.__UI_LANG__) window.__UI_LANG__(k); this.set({ lang: k, langOpen: false }); }; });",
    'i18n:setLang', log)

  // 2 · objetos de atencao — slots ilustrativos dao lugar aos candidatos reais.
  //     O seletor de pais passa a FILTRAR de verdade: antes ele so trocava o
  //     rotulo do cabecalho, e por isso Italia e Franca pareciam vazias
  //     enquanto os objetos delas ja estavam no bundle.
  out = replaceBlock(out, 'const RAW = [',
    `const RAW = (window.__SINTONIA__.RAW || []).filter(o => {
      var code = { es: 'ES', it: 'IT', fr: 'FR' }[s.country];
      if (!code) return true;                       // camada EAME: nao filtra
      var of = (o.f && o.f.COUNTRY_OF_FACT) || '';
      return of.split('/').indexOf(code) >= 0;      // 'ES/IT/FR' vale nos tres
    }).map(o => Object.assign({}, o, {
      title: __T__(o, 'title', s.lang) || o.title,
      blocker: __T__(o, 'blocker', s.lang) || o.blocker,
      last: __T__(o, 'last', s.lang) || o.last,
      gates: (o.gates || []).map(g => gate(g[0], g[1]))
    }));`, log)

  // 3 · gaveta de evidencia — fixtures dao lugar a evidencia real
  out = replaceBlock(out, 'const EVIDENCE = {',
    'const EVIDENCE = window.__SINTONIA__.EVIDENCE || {};', log)

  // 4 · receptor territorial: passa a exibir o campo real quando ele existe.
  //     Onde a mangueira nao mediu, continua null e o casco mostra o vazio.
  out = replaceOnce(out,
    `      REGION_OF_FACT: null, LOCALITY_OF_FACT: null, CROP: null, ISSUE: null,
      ISSUE_EVIDENCE_PASSAGE: null, PUBLISHED_AT: null, SOURCE_ID: null,`,
    `      REGION_OF_FACT: (o.f && o.f.REGION_OF_FACT) || null, LOCALITY_OF_FACT: null,
      CROP: (o.f && o.f.CROP) || null, ISSUE: (o.f && o.f.ISSUE) || null,
      ISSUE_EVIDENCE_PASSAGE: (o.f && o.f.ISSUE_EVIDENCE_PASSAGE) || null,
      PUBLISHED_AT: (o.f && o.f.PUBLISHED_AT) || null, SOURCE_ID: (o.f && o.f.SOURCE_ID) || null,`,
    'F1:campos-reais', log)

  // 5 · COUNTRY_OF_FACT sai do fato, nao do seletor de pais da barra
  out = replaceOnce(out,
    'OBJECT_ID: o.id, OBJECT_TYPE: TYPES[o.type].code, COUNTRY_OF_FACT: COUNTRY[s.country].name,',
    // O fallback para COUNTRY[s.country].name era eu mesmo repetindo o erro que
    // vim corrigir: quando o objeto NAO declara pais, a tela respondia com o
    // pais do seletor. Seletor e filtro de interface, nunca fato. Sem pais
    // declarado, a resposta e NOT_KNOWN.
    'OBJECT_ID: o.id, OBJECT_TYPE: TYPES[o.type].code,\n      COUNTRY_OF_FACT: (o.f && o.f.COUNTRY_OF_FACT) || \'NOT_KNOWN\',',
    'F1:country-of-fact', log)

  // 5b · OBJECT DETAIL · o casco caia em `|| RAW[0]` quando o tipo pedido nao
  //      existia no pais. Isso nao e um vazio: e o objeto de OUTRO tipo posando
  //      de resposta. Medido no snapshot: ES nao tem `reg`, IT nao tem `field`,
  //      FR nao tem nem `field` nem `reg` — quatro telas mentindo.
  //
  //      Trocado por um objeto EMPTY_VALID declarado. Nenhum campo de outro
  //      objeto entra, e evidenceId fica null: sem objeto, sem gaveta.
  //      O casco nao tinha estado para "nao ha objeto" — so estados de objeto
  //      que existe. Um vazio precisa de nome proprio, senao vira 'ARQUIVADO'
  //      ou 'PRECISA DE EVIDENCIA', que sao outras coisas.
  out = replaceOnce(out,
    "archived:  { label: 'ARQUIVADO', color: T3, border: EARTH, dash: 'dashed' }",
    `archived:  { label: 'ARQUIVADO', color: T3, border: EARTH, dash: 'dashed' },
      empty:     { label: 'EMPTY_VALID · SEM OBJETO', color: T3, border: EARTH, dash: 'dashed' }`,
    'estado:empty-valid', log)

  out = replaceOnce(out,
    'const base = RAW.find(o => o.type === t) || RAW[0];',
    `const base = RAW.find(o => o.type === t) || {
      id: '—', type: t, line: 'none', state: 'empty', win: 'naosei',
      evidenceId: null, gates: [],
      title: 'Nenhum objeto confirmado',
      meta: 'Ainda não há evidência suficiente para descrever um caso deste tipo em ' +
            COUNTRY[s.country].name + '.',
      blocker: 'Não há bloqueador porque não há objeto. Isto é ausência declarada, não tela quebrada: ' +
               'nenhuma evidência deste tipo foi coletada neste país até aqui.',
      last: '—'
    };`,
    'detail:sem-fallback-de-tipo-errado', log)

  // 5c · SELO DE PAIS · 'FUNDAÇÃO COMPLETA' e 'EM COLETA' eram texto fixo no
  //      casco. Nenhum dos tres paises tem objeto promovido (ready = 0 nos
  //      tres), entao 'FUNDAÇÃO COMPLETA' era uma afirmacao que o proprio
  //      snapshot desmente. O selo passa a ser contagem medida, nao adjetivo.
  out = replaceOnce(out, 'const COUNTRY = {',
    `const __LANE__ = function (c) {
      return ((window.__SINTONIA__.eameLanes || []).filter(function (x) { return x.code === c; })[0]) || {};
    };
    const __BADGE__ = function (c) {
      var l = __LANE__(c);
      if (l.objects === undefined) return 'NÃO MEDIDO';
      return l.objects + ' OBJETOS · ' + (l.ready || 0) + ' PROMOVIDOS';
    };
    const COUNTRY = {`, 'country:selo-helper', log)

  for (const [code, marca] of [
    ['ES', "es: { name: 'Espanha', kind: 'PAÍS', badge: 'FUNDAÇÃO COMPLETA',"],
    ['IT', "it: { name: 'Itália', kind: 'PAÍS', badge: 'EM COLETA',"],
    ['FR', "fr: { name: 'França', kind: 'PAÍS', badge: 'EM COLETA',"],
  ]) {
    out = replaceOnce(out, marca,
      marca.replace(/badge: '[^']*',/, `badge: __BADGE__('${code}'),`),
      `country:selo-${code}`, log)
  }

  // 5d · EVIDENCE_ID · o casco amarrava o id da evidencia ao TIPO do objeto,
  //      nao ao objeto. Todo objeto `case` mostrava EV-0001, fosse ele qual
  //      fosse — e um objeto vazio mostrava EV-0001 tambem, evidencia de um
  //      objeto que nem estava na tela.
  //
  //      Passa a ser sempre `base.evidenceId`: a evidencia do objeto aberto,
  //      e null quando nao ha objeto. Onde o casco declarava null, continua
  //      null — nao inventamos evidencia para afirmacao que ninguem provou.
  out = replaceOnce(out,
    `        case: [['fato observado','EV-0001'],['localidade do fato','EV-0001'],['issue nomeado',null]],
        reg: [['data oficial','EV-0002'],['registro afetado','EV-0002'],['efeito no rótulo',null]],
        comp: [['marca localizada','EV-0003'],['atividade paga observada','EV-0004'],['registro local',null]],`,
    `        case: [['fato observado',base.evidenceId],['localidade do fato',base.evidenceId],['issue nomeado',null]],
        reg: [['data oficial',base.evidenceId],['registro afetado',base.evidenceId],['efeito no rótulo',null]],
        comp: [['marca localizada',base.evidenceId],['atividade paga observada',base.evidenceId],['registro local',null]],`,
    'evidencia:do-objeto-nao-do-tipo', log)

  // 5e · mesma lei nas faixas de fundacao. A faixa 4 apontava para EV-0002,
  //      evidencia de OUTRO objeto; vira null. Sub-declarar e honesto,
  //      sobre-declarar nao.
  out = replaceOnce(out,
    "const eid = ['EV-0001', null, null, 'EV-0002', null, null, null][n] || null;",
    "const eid = [base.evidenceId, null, null, null, null, null, null][n] || null;",
    'evidencia:faixas-do-objeto', log)

  // 5f · pernas de convergencia · a perna TERRITORIAL tambem citava EV-0001
  //      fixo. Vira a evidencia do objeto aberto. A perna DEPENDENTE perde o
  //      id fixo e fica null: ela existe para mostrar que UMA fonte repetida
  //      nao vira duas, e para isso nao precisa fingir um id.
  out = replaceOnce(out,
    "        evidenceId: 'EV-0001', independence: 'INDEPENDENT', dependency: null, observedAt: null },",
    "        evidenceId: base.evidenceId, independence: 'INDEPENDENT', dependency: null, observedAt: null },",
    'convergencia:perna-do-objeto', log)

  out = replaceOnce(out,
    "        evidenceId: 'EV-0006', independence: 'DEPENDENT', dependency: 'SOURCE_DEPENDENCY',",
    "        evidenceId: null, independence: 'DEPENDENT', dependency: 'SOURCE_DEPENDENCY',",
    'convergencia:perna-dependente-sem-id-falso', log)

  // 5g · TIMELINE · o casco trazia quatro eventos fixos, os mesmos para todo
  //      objeto: um boletim publicado em 23 ABR, uma captura em 31 AGO, e uma
  //      mudanca de estado FORMING -> ATTENTION_CANDIDATE_TEST. Nenhum objeto
  //      tem esses eventos medidos, e varios nunca estiveram em FORMING.
  //
  //      Passa a ser derivada do objeto aberto, e so entra o que existe:
  //
  //      CAPTURA      · a data em que a mangueira congelou. Medida.
  //      ESTADO       · o estado declarado do objeto. O estado ANTERIOR nao foi
  //                     medido, entao fica NULL — nao inventamos de onde veio.
  //      VAZIO        · so quando um portao do proprio objeto esta aberto. O
  //                     motivo e o nome do portao, nao um texto generico.
  //
  //      PUBLICACAO DA FONTE nao entra: para estes objetos PUBLISHED_AT e igual
  //      a data de captura, ou seja, nao ha data de publicacao propria medida.
  //      Sem evento, sem linha. Vazio na timeline e resposta, nao falha.
  out = replaceBlock(out, 'const TL = [',
    `const TL = (function () {
      var f = base.f || {}, ev = [];
      var quando = f.PUBLISHED_AT || (base.prov && base.prov.AS_OF_DATE) || null;
      if (quando) ev.push({
        k: 'capture', id: 'EVT-' + base.id + '-CAP', type: 'FIRST_CAPTURE', at: quando,
        date: quando, res: 'DATA_EXATA',
        sourceName: 'SINTONIA', sourceId: f.SOURCE_ID || null,
        title: 'Captura congelada pela mangueira',
        changed: 'Documento congelado com proveniencia: commit, fonte e data.',
        before: null, after: null, obs: null
      });
      if (f.ATTENTION_STATE_RAW) ev.push({
        k: 'state', id: 'EVT-' + base.id + '-ST', type: 'STATE_CHANGE', at: quando,
        date: quando || '—', res: quando ? 'DATA_EXATA' : 'NAO_CONHECIDA',
        sourceName: 'SINTONIA', sourceId: f.SOURCE_ID || null,
        title: 'Estado declarado: ' + f.ATTENTION_STATE_RAW,
        changed: 'Estado medido pelos portoes deste objeto.',
        before: null, after: f.ATTENTION_STATE_RAW, obs: null
      });
      (base.gates || []).forEach(function (g, i) {
        // Atencao: quando chega aqui o portao ja passou por gate(), que troca
        // a chave crua ('naoprovado') pelo ROTULO ('NÃO PROVADO'). Comparar com
        // a chave crua nao casa nada — foi o que aconteceu na primeira tentativa
        // e a timeline saiu sem nenhum vazio, como se nao houvesse portao aberto.
        var rotulo = g && (g.k || g[0]), estado = String((g && (g.v || g[1])) || '');
        if (/^N[ÃA]O/i.test(estado)) {
          ev.push({
            k: 'gap', id: 'EVT-' + base.id + '-GAP' + i, type: 'GAP', at: null,
            date: '—', res: 'NAO_CONHECIDA', sourceName: null, sourceId: null,
            title: 'Portao aberto: ' + rotulo,
            changed: 'O intervalo e real e permanece vazio ate este portao fechar.',
            before: null, after: null, obs: null,
            gapReason: String(rotulo).toUpperCase().replace(/[^A-Z0-9]+/g, '_') + '_NOT_PROVEN'
          });
        }
      });
      return ev;
    })();`, log)

  // 5h · MAPA · os pontos jogavam fora o que o objeto sabe e usavam o pais do
  //      seletor como COUNTRY. Cultura e problema iam para null mesmo existindo
  //      no objeto. Agora tudo vem de o.f, e o que falta diz NOT_KNOWN.
  //
  //      GEO_RESOLUTION continua NOT_KNOWN de proposito: ninguem mediu
  //      geometria, e regiao em texto NAO vira ponto no mapa.
  out = replaceOnce(out,
    `      COUNTRY: COUNTRY[s.country].name, REGION: null, LOCALITY_OR_GEOMETRY: null,
      GEO_RESOLUTION: 'NOT_KNOWN', CROP: null, ISSUE: null,`,
    `      COUNTRY: (o.f && o.f.COUNTRY_OF_FACT) || 'NOT_KNOWN',
      REGION: (o.f && o.f.REGION_OF_FACT) || 'NOT_KNOWN',
      LOCALITY_OR_GEOMETRY: null,
      GEO_RESOLUTION: 'NOT_KNOWN',
      CROP: (o.f && o.f.CROP) || 'NOT_KNOWN', ISSUE: (o.f && o.f.ISSUE) || 'NOT_KNOWN',`,
    'mapa:ponto-vem-do-objeto', log)

  // 5i · o filtro do mapa mostrava o pais do seletor como se fosse fato
  //      PROVADO. Filtro e recorte de tela; vira 'FILTRO', nao 'provado'.
  out = replaceOnce(out,
    "{ k: 'PAÍS', v: COUNTRY[s.country].name, v2: 'provado' },",
    "{ k: 'PAÍS (FILTRO DE TELA)', v: COUNTRY[s.country].name, v2: 'naomedido' },",
    'mapa:filtro-nao-e-fato', log)

  // 5j · a ficha do objeto declarava COUNTRY_OF_FACT = pais do seletor, e
  //      marcava 'provado'. Duas mentiras numa linha: a origem e o estado.
  out = replaceOnce(out,
    "FIELD('COUNTRY_OF_FACT', COUNTRY[s.country].name, 'provado'), FIELD('REGION_OF_FACT', null, 'naomedido'),",
    `FIELD('COUNTRY_OF_FACT', (base.f && base.f.COUNTRY_OF_FACT) || 'NOT_KNOWN', (base.f && base.f.COUNTRY_OF_FACT) ? 'provado' : 'naomedido'),
        FIELD('REGION_OF_FACT', (base.f && base.f.REGION_OF_FACT) || null, (base.f && base.f.REGION_OF_FACT) ? 'provado' : 'naomedido'),`,
    'ficha:country-of-fact-do-objeto', log)

  // Esta linha aparece SEIS vezes — um receptor de cada mangueira repete o
  // mesmo erro. O portao de "casou 1x" pegou isso, e foi bom: eu ia corrigir
  // um e deixar cinco. Aqui a contagem esperada e 6, e continua sendo um
  // portao: se o casco mudar e virarem 5 ou 7, o build para.
  {
    const alvo = "FIELD('COUNTRY', COUNTRY[s.country].name, 'provado'),"
    const novo = "FIELD('COUNTRY', (base.f && base.f.COUNTRY_OF_FACT) || 'NOT_KNOWN', " +
                 "(base.f && base.f.COUNTRY_OF_FACT) ? 'provado' : 'naomedido'),"
    const n = out.split(alvo).length - 1
    if (n !== 6) throw new Error(`FAIL_CLOSED · "ficha:country-do-objeto" casou ${n}x (esperado 6)`)
    out = out.split(alvo).join(novo)
    log.push({ patch: 'ficha:country-do-objeto (6x)', bytes_out: alvo.length * 6, bytes_in: novo.length * 6 })
  }

  // 5k · FACT_LOCATION · a proibicao mais direta do contrato, escrita no
  //      casco em uma linha: o lugar do FATO vinha do seletor de pais. Se
  //      alguem trocasse para Franca, o fato "acontecia" na Franca.
  out = replaceOnce(out,
    "{ k: 'FACT_LOCATION', v: COUNTRY[s.country].name, color: T2 },",
    `{ k: 'FACT_LOCATION', v: (base.f && base.f.COUNTRY_OF_FACT) || 'NOT_KNOWN',
          color: (base.f && base.f.COUNTRY_OF_FACT) ? T2 : T3 },`,
    'fato:location-nao-vem-da-tela', log)

  // 5l · COUNTRY_SCOPE de H8 declarado como 'provado' a partir do seletor. O
  //      escopo de uma conta e medido no artefato (LOCAL_COUNTRY_PROVED,
  //      GLOBAL, NOT_KNOWN) e nao tem nada com a tela aberta.
  out = replaceOnce(out,
    "FIELD('COUNTRY_SCOPE', COUNTRY[s.country].name, 'provado'),",
    "FIELD('COUNTRY_SCOPE', null, 'naomedido'),",
    'h8:country-scope-nao-vem-da-tela', log)

  // 5m · RELOGIOS · cinco dos sete vinham com known: true para QUALQUER objeto,
  //      e mostrando travessao como valor. Dizer "conhecido" e mostrar "—" na
  //      mesma linha e a definicao de declarar sem medir.
  //
  //      Cada relogio passa a perguntar se EXISTE medicao correspondente neste
  //      objeto. Nenhuma das medidas abaixo foi coletada nesta rodada:
  //
  //        tempo da observacao   nao ha OBSERVATION_TIME. PUBLISHED_AT e a data
  //                              em que a fonte publicou, e nao serve: publicar
  //                              nao e observar
  //        BBCH na observacao    nao coletado
  //        estagio atual         exige relogio agronomico do pais; nao conectado
  //        uso em rotulo         exige leitura do rotulo registrado; nao feita
  //        janela de aplicacao   nao deriva de estagio nem de prazo
  //        estacao futura        nao medida
  //
  //      Sobra UM que existe de verdade: o prazo regulatorio, e so quando o
  //      objeto aberto e do tipo prazo. As categorias nao se convertem umas nas
  //      outras — prazo nao vira janela de aplicacao.
  out = replaceOnce(out,
    `    const clocks = CLOCKS.map(c => ({
      k: c.k, res: c.res, note: c.note, value: c.value,
      known: !!c.known, unknown: !c.known,`,
    `    const MEDIDO_AQUI = {
      'Prazo regulatório': t === 'reg' && !!base.f && !!base.f.PUBLISHED_AT
    };
    const clocks = CLOCKS.map(c => {
      var medido = !!MEDIDO_AQUI[c.k];
      return {
      k: c.k, res: medido ? c.res : 'NÃO MEDIDA', note: c.note,
      value: medido ? 'REGULATORY_DEADLINE · ' + base.f.PUBLISHED_AT
                    : String(c.value).replace(/ · .*$/, ' · NOT_MEASURED'),
      known: medido, unknown: !medido,`,
    'relogios:so-o-que-foi-medido', log)

  out = replaceOnce(out,
    `      color: c.known ? T2 : T3,
      border: c.known ? 'var(--hair2)' : EARTH,
      dash: c.known ? 'solid' : 'dashed'
    }));`,
    `      color: medido ? T2 : T3,
      border: medido ? 'var(--hair2)' : EARTH,
      dash: medido ? 'solid' : 'dashed'
    };});`,
    'relogios:cor-segue-a-medicao', log)

  // 5n · MOMENTO, COMPARABILIDADE e ASSIMETRIA · os tres eram texto fixo.
  //      O de comparabilidade era o pior: afirmava "comparavel" para area de
  //      cultura e preco de referencia nos tres paises, e nenhuma das duas foi
  //      medida em pais nenhum. A assimetria listava "Objeto — slot 01".
  out = replaceBlock(out, 'const momentum = [',
    'const momentum = window.__SINTONIA__.momentum || [];', log)
  out = replaceBlock(out, 'const comparability = [',
    'const comparability = window.__SINTONIA__.comparability || [];', log)
  out = replaceBlock(out, 'const asymRows = [',
    'const asymRows = window.__SINTONIA__.asymRows || [];', log)

  // 5o · PASSAGEM EXECUTIVA · nomes de tipo e de estado em portugues de gente.
  //
  //      Os codigos canonicos continuam INTACTOS no dado, na evidencia e na
  //      proveniencia — o que muda e a etiqueta que aparece na tela. Quem abre
  //      o portal e diretor, marketing ou regulatorio, e ninguem precisa saber
  //      que existe um tipo chamado LONGITUDINAL_FIELD_PRESSURE para entender
  //      que aquilo e a pressao da doenca no campo ao longo dos anos.
  for (const [de, para] of [
    ["label: 'PHENOMENON CASE'", "label: 'Caso de campo'"],
    ["label: 'REGULATORY DEADLINE'", "label: 'Prazo regulatorio'"],
    ["label: 'COMPETITOR IDENTITY CHAIN'", "label: 'Cadeia de concorrente'"],
    ["label: 'LONGITUDINAL FIELD PRESSURE'", "label: 'Pressao de campo'"],
  ]) out = replaceOnce(out, de, para, 'ux:tipo ' + de.slice(8, 34), log)

  // Os estados diziam o portao em vez de dizer a situacao. "EVIDENCIA VALIDA ·
  // NAO PRONTO" e verdade e nao ajuda ninguem a decidir; "Evidencia observada"
  // diz a mesma coisa e cabe num cartao.
  for (const [de, para] of [
    ["ready:     { label: 'PRONTO PARA ATENÇÃO'", "ready:     { label: 'Pronto para atenção'"],
    ["candidate: { label: 'CANDIDATO EM TESTE'", "candidate: { label: 'Caso emergente'"],
    ["valid:     { label: 'EVIDÊNCIA VÁLIDA · NÃO PRONTO'", "valid:     { label: 'Evidência observada'"],
    ["needs:     { label: 'PRECISA DE EVIDÊNCIA'", "needs:     { label: 'Precisa de evidência'"],
    ["forming:   { label: 'EM FORMAÇÃO'", "forming:   { label: 'Em formação'"],
    ["watch:     { label: 'EM OBSERVAÇÃO'", "watch:     { label: 'Em observação'"],
    ["future:    { label: 'FUTURO'", "future:    { label: 'Futuro'"],
    ["archived:  { label: 'ARQUIVADO'", "archived:  { label: 'Arquivado'"],
    ["empty:     { label: 'EMPTY_VALID · SEM OBJETO'", "empty:     { label: 'Sem objeto deste tipo'"],
  ]) out = replaceOnce(out, de, para, 'ux:estado ' + de.slice(0, 10), log)

  // 5p · CARD COM UMA IDEIA SO · cada cartao do radar carregava a matriz
  //      inteira de portoes: sete linhas de "provado / nao provado" dentro de
  //      um cartao que ja tem titulo, lugar, assunto e estado.
  //
  //      A matriz nao sai do produto: ela continua no DETALHE, que e onde
  //      alguem vai de fato conferir portao por portao. No cartao ela virava
  //      ruido — e o cartao existe para responder O QUE e ONDE em dois
  //      segundos, nao para auditar.
  //
  //      A marcacao e a mesma nos quatro lugares onde o cartao aparece, entao
  //      a troca e 4x e conferida: se o casco mudar, o build para.
  {
    const alvo = '<div style="display:flex;flex-direction:column;gap:5px;padding:12px;' +
      'border-radius:12px;background:rgba(255,255,255,.025);border:1px solid var(--hair2)">\n' +
      '                    <sc-for list="{{ o.gates }}" as="g"'
    const novo = alvo.replace('<div style=', '<div data-ux="portoes-do-cartao" style=')
    const n = out.split(alvo).length - 1
    if (n !== 4) throw new Error(`FAIL_CLOSED · "cartao:portoes" casou ${n}x (esperado 4)`)
    out = out.split(alvo).join(novo)
    log.push({ patch: 'cartao:portoes-fora-do-cartao (4x)', bytes_out: 0, bytes_in: 0 })
  }

  out = replaceOnce(out, '</head>',
    `<style>
  /* PASSAGEM EXECUTIVA · o cartao responde O QUE e ONDE. O detalhe audita. */
  [data-ux="portoes-do-cartao"] { display: none !important; }
</style>
</head>`, 'ux:css', log)

  // 5q · "SINGLE SIGNAL" e o nome do estado no contrato, em ingles, dentro de
  //      uma tela em portugues. O estado nao muda; o rotulo passa a dizer a
  //      mesma coisa em palavra de gente.
  //      Aparece em mais de um lugar, entao a troca e por contagem conferida.
  for (const [de, para, n] of [
    ['SINGLE SIGNAL · 1 FAMÍLIA INDEPENDENTE', 'UM SINAL SÓ · UMA FAMÍLIA INDEPENDENTE', 2],
    // 1x, e nao 2: a troca de cima ja consumiu as duas ocorrencias longas.
    ['SINGLE SIGNAL · 1 FAMÍLIA', 'UM SINAL SÓ', 1],
  ]) {
    const achou = out.split(de).length - 1
    if (achou !== n) throw new Error(`FAIL_CLOSED · "${de}" casou ${achou}x (esperado ${n})`)
    out = out.split(de).join(para)
    log.push({ patch: 'ux:' + de.slice(0, 24), bytes_out: de.length * n, bytes_in: para.length * n })
  }

  // 5r · QUATRO FRASES QUE AINDA FALAVAM EM NOME DE CAMPO
  //
  //      Estas nao podiam ser escondidas como as outras: sao a explicacao, nao
  //      o encanamento. Cada uma protege uma distincao que o produto inteiro
  //      depende de manter. Entao foram REESCRITAS, palavra por palavra, sem
  //      perder a distincao.
  //      A troca acontece em tempo de execucao, junto com o resto da passagem:
  //      algumas dessas frases sao montadas na hora ("4 OBJETO(S) SEM ..."), e
  //      um replace no arquivo nao alcanca o que ainda nao existe.

  // 5s · O QUE SABEMOS / O QUE FALTA · os dois eram lista fixa.
  //
  //      "O que sabemos" tinha duas frases por tipo, iguais para qualquer
  //      objeto. "O que falta" tinha QUATRO itens fixos — os mesmos quatro,
  //      sempre, inclusive para objetos que ja tinham aquele portao fechado.
  //      Era fixture com cara de medicao.
  //
  //      Agora os dois saem dos PORTOES do objeto aberto: portao fechado vira
  //      linha em "sabemos", portao aberto vira linha em "falta", com o estado
  //      real do portao. Objeto sem portao nao inventa nenhum dos dois.
  out = replaceOnce(out,
    "const known = t === 'case' ? ['Fato observado, com fonte, data e localidade do fato.','Recorte geográfico declarado pela própria fonte.'] : (t === 'reg' ? ['Data oficial e registro afetado, pela fonte oficial.','Titular do registro conforme a base oficial.'] : []);",
    `const __fechado__ = function (g) {
      var v = String((g && (g.v || g[1])) || '');
      return !/^N[ÃA]O/i.test(v);
    };
    const known = base.id === '—'
      // Sem objeto: o unico fato que sobra e o recorte do pais, e ele e
      // verdade. Nao ha bullet inventado — se nem isso houvesse, a lista
      // ficaria vazia e o casco desenha o vazio.
      ? [COUNTRY[s.country] ? 'País do recorte: ' + COUNTRY[s.country].name : null,
         RAW.length ? RAW.length + ' objeto(s) de outros tipos neste país' : null].filter(Boolean)
      : (base.gates || []).filter(__fechado__).map(function (g) { return (g.k || g[0]) + '.'; });`,
    'vazio:o-que-sabemos-vem-dos-portoes', log)

  out = replaceOnce(out,
    `    const missing = [
      { v: 'naoprovado', t: 'Issue nomeado por fonte técnica independente.' },
      { v: 'naomedido', t: 'Linha de base e N por leitura.' },
      { v: 'naopronto', t: 'Segunda leitura independente do mesmo fato.' },
      { v: 'naoconect', t: 'Relógio agronômico do país.' }
    ].map(m => ({ tag: ST[m.v].label, color: ST[m.v].color, border: ST[m.v].border, t: m.t }));`,
    `    const missing = (base.id === '—'
      ? [{ v: 'naopronto', t: 'Um objeto deste tipo neste país. Nenhum foi formado — ausência declarada, não falha.' }]
      : (base.gates || []).filter(function (g) { return !__fechado__(g); })
          .map(function (g) {
            // O portao ja vem com o ROTULO no lugar da chave; volta-se a chave
            // para achar a cor, e sem correspondencia usa-se um vazio neutro.
            var rot = String((g && (g.v || g[1])) || '');
            var chave = Object.keys(ST).filter(function (k) { return ST[k].label === rot; })[0] || 'naopronto';
            return { v: chave, t: (g.k || g[0]) + '.' };
          })
    ).map(m => ({ tag: ST[m.v].label, color: ST[m.v].color, border: ST[m.v].border, t: m.t }));`,
    'vazio:o-que-falta-vem-dos-portoes', log)

  // 6 · volumes da home
  out = replaceBlock(out, 'const volumes = [',
    'const volumes = window.__SINTONIA__.volumes || [];', log)

  // 7 · fontes
  out = replaceBlock(out, 'const sources = [',
    `const sources = (window.__SINTONIA__.sources || []).map(x => ({
      name: x.name, role: x.role, status: ST[x.v].label, color: ST[x.v].color,
      border: ST[x.v].border, dash: ST[x.v].dash,
      pub: x.pub, capture: x.capture, age: x.age, latency: x.latency
    }));`, log)

  // 8 · serie de campo
  out = replaceBlock(out, 'const fieldStats = [',
    `const fieldStats = (window.__SINTONIA__.fieldStats || []).map(x => ({
      k: x.k, v: x.v, color: ST[x.st] ? ST[x.st].color : T3
    }));`, log)

  // 9 · vozes de campo — pessoa e empresa nunca somadas
  out = replaceBlock(out, 'const voices = [',
    `const voices = (window.__SINTONIA__.voices || []).map(v => ({
      kind: v.kind, k: v.k, note: v.note,
      state: ST[v.v].label, color: ST[v.v].color, border: ST[v.v].border, dash: ST[v.v].dash,
      fields: [
        { k: 'ENTITY_ID', v: '—' }, { k: 'DISPLAY_NAME', v: '—' },
        { k: 'RELATION_TO_CROP_REGION', v: 'NÃO PROVADA' },
        { k: 'ENTRY_PATH', v: s.entryPath },
        { k: 'GDPR_TREATMENT_STATE', v: 'NOT_STARTED' },
        { k: 'ROW_COUNT / ENTITY_COUNT', v: v.rows + ' / ' + v.ents },
        { k: 'ACTIVATION_READY', v: v.ready },
        { k: 'CONTENT_PROFILE_TYPE', v: 'CREATOR_CONTENT_PROFILE' },
        { k: 'CONTENT_PROFILE_REF', v: '—' }, { k: 'LAST_OBSERVED_AT', v: '—' }
      ]
    }));`, log)

  // 10 · cadeia competitiva
  out = replaceBlock(out, 'const chain = [',
    `const chain = (window.__SINTONIA__.chain || []).map(c => ({
      step: c.step, k: c.k, note: c.note, state: ST[c.v].label,
      color: ST[c.v].color, border: ST[c.v].border, dash: ST[c.v].dash
    }));`, log)

  // 11 · gaveta de evidencia: datas reais da mangueira
  out = replaceOnce(out,
    `        { k: 'SOURCE_PUBLISHED_AT', v: '—', color: T3 },
        { k: 'CAPTURED_AT', v: '—', color: T3 },`,
    `        { k: 'SOURCE_PUBLISHED_AT', v: (ev && ev.asOf) || '—', color: ev && ev.asOf ? T2 : T3 },
        { k: 'CAPTURED_AT', v: (ev && ev.asOf) || '—', color: ev && ev.asOf ? T2 : T3 },`,
    'drawer:datas', log)

  // 12 · gaveta de evidencia: PROVENANCE real, commit incluso.
  //      Cada item passa a poder responder SOURCE, SOURCE_ID, AS_OF_DATE e
  //      FREEZE_COMMIT. Onde a mangueira nao declara, continua travessao.
  out = replaceOnce(out,
    `      ].concat((PROV_ROWS[ev ? ev.backend : 'UNWIRED'] || []).map(p => ({ k: 'PROVENANCE · ' + p[0], v: p[1], color: T3 }))),`,
    `      ].concat((ev ? [
        ['REPOSITORY', 'lucianodalondon-sys/eame-sintonia'],
        ['FREEZE_COMMIT', ev.commit || '—'],
        ['SOURCE_ID', ev.sourceId || '—'],
        ['AS_OF_DATE', ev.asOf || '—'],
        ['HOSE_ID', ev.hose || '—'],
        ['RESOLVED', ev.unresolved ? 'NO · PRELIMINARY' : 'YES'],
        ['NOTE', ev.note || '—']
      ] : (PROV_ROWS.UNWIRED || [])).map(p => ({
        k: 'PROVENANCE · ' + p[0], v: p[1],
        color: p[1] && p[1] !== '—' ? T2 : T3
      }))),`,
    'drawer:provenance-real', log)

  // 13 · ACERVO · as quatro barras cinzas viram os documentos reais.
  //      O casco ja usa <sc-for> em outros pontos; aqui e o mesmo mecanismo e
  //      exatamente a mesma marcacao de linha — mesma grade, mesma fonte,
  //      mesmas cores. So o conteudo deixa de ser barra e passa a ser texto.
  const ROW = (inner) =>
    '<div style="display:grid;grid-template-columns:1fr 130px 116px 96px;gap:14px;align-items:center;' +
    'padding:16px 18px;border-bottom:1px solid var(--hair2)">' + inner + '</div>'

  const oldRows = [...out.matchAll(
    /<div style="display:grid;grid-template-columns:1fr 130px 116px 96px;gap:14px;align-items:center;padding:16px 18px;border-bottom:1px solid var\(--hair2\)">[\s\S]*?<\/div>\n?/g
  )]
  if (oldRows.length !== 4) {
    throw new Error(`FAIL_CLOSED · esperava 4 linhas de acervo no casco, achei ${oldRows.length}`)
  }
  const firstRow = oldRows[0]
  const bloco =
    '<sc-for list="{{ acervoRows }}" as="r" hint-placeholder-count="4">\n' +
    ROW(
      '<span style="display:flex;flex-direction:column;gap:4px;min-width:0">' +
      '<span style="font:500 12px/1.35 var(--font-primary);color:var(--t1);overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{{ r.title }}</span>' +
      '<span style="font:400 10.5px/1.3 var(--font-primary);color:var(--t3);overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{{ r.sub }}</span>' +
      '</span>' +
      '<span style="font:500 11px/1 var(--font-primary);color:var(--t3)">{{ r.sourceId }}</span>' +
      '<span style="font:500 11px/1 var(--font-primary);color:var(--t3)">{{ r.capture }}</span>' +
      '<span style="justify-self:end;font:600 9.5px/1 var(--font-primary);padding:5px 9px;border-radius:9999px;' +
      'border:1px solid {{ r.lineBorder }};color:{{ r.lineColor }}">{{ r.line }}</span>'
    ) +
    '\n</sc-for>\n'

  // remove as tres linhas seguintes e troca a primeira pelo laco
  out = out.replace(oldRows[3][0], '').replace(oldRows[2][0], '').replace(oldRows[1][0], '')
  out = out.replace(firstRow[0], bloco)
  log.push({ patch: 'acervo:documentos-reais', bytes_out: firstRow[0].length, bytes_in: bloco.length })

  // 13b · a nota de rodape do acervo deixa de dizer que o dado ainda nao veio
  out = replaceOnce(out,
    'Paginação preparada — o acervo real entra depois do freeze',
    '{{ acervoNote }}',
    'acervo:nota', log)

  // 13c · lista e nota entram nos valores do template
  out = replaceOnce(out,
    '      acervoOn, acervoColor, setAcervo\n    };',
    `      acervoOn, acervoColor, setAcervo,
      acervoRows: (window.__SINTONIA__.acervoRows || []).filter(r => {
        var code = { es: 'ES', it: 'IT', fr: 'FR' }[s.country];
        return !code || r.country === code;
      }),
      acervoNote: (function () {
        var code = { es: 'ES', it: 'IT', fr: 'FR' }[s.country];
        var n = (window.__SINTONIA__.acervoRows || []).filter(function (r) {
          return !code || r.country === code;
        }).length;
        // "documentos" deixou de servir: a lista tem tres coisas diferentes.
        // Documento analisado foi lido como texto; registro nacional e prazo
        // declarado; cadeia e cruzamento preliminar. Somar os tres num numero
        // so diria que foram lidos do mesmo jeito, e nao foram.
        var meu = (window.__SINTONIA__.acervoRows || []).filter(function (r) {
          return !code || r.country === code;
        });
        var conta = function (l) { return meu.filter(function (r) { return r.line === l; }).length; };
        var prazo = conta('PRAZO'), cadeia = conta('CADEIA'), contas = conta('CONTA');
        var partes = [meu.length + ' linhas',
                      (meu.length - prazo - cadeia - contas) + ' com corpo analisado'];
        if (prazo) partes.push(prazo + ' registros com prazo');
        if (cadeia) partes.push(cadeia + ' cadeias preliminares');
        if (contas) partes.push(contas + ' contas publicas · conteudo NAO coletado');
        return partes.join(' · ') + ' · fonte e captura por linha';
      })()
    };`,
    'acervo:valores', log)

  // 14 · H7 · ciencia/expert. Pessoa encontrada nunca vira especialista aqui:
  //      o gate ISSUE_EXPERTISE_PROVED continua sendo quem decide o rotulo.
  out = replaceBlock(out, 'const EXPERTS = [',
    'const EXPERTS = window.__SINTONIA__.experts || [];', log)

  // 15 · EAME · numeros reais por pais na camada cross-market
  out = replaceBlock(out, "const eameLanes = ['es','it','fr'].map(k => ({",
    `const eameLanes = (window.__SINTONIA__.eameLanes || []).map(x => {
      var k = x.code.toLowerCase();
      return {
        code: x.code, name: COUNTRY[k].name, foundation: COUNTRY[k].badge,
        color: COUNTRY[k].badgeColor, border: COUNTRY[k].badgeBorder,
        freshness: x.freshness, signals: x.signals, windows: x.windows,
        gaps: x.gaps, open: drill(k, 'home'), openCases: drill(k, 'radar')
      };
    });`, log)

  // 16 · RELATORIOS · os freezes que sustentam este snapshot
  out = replaceBlock(out, 'const reports = [',
    `const reports = (window.__SINTONIA__.reports || []).map(r => ({
      kind: r.kind, title: r.title, fields: r.fields, note: r.note,
      state: ST[r.v].label, color: ST[r.v].color, border: ST[r.v].border, dash: ST[r.v].dash
    }));`, log)

  // 17 · casos cross-market · so o que atravessa mercado de verdade
  out = replaceBlock(out, 'const crossCases = [',
    `const crossCases = (window.__SINTONIA__.crossCases || []).map(c => ({
      line: c.line, lineLabel: c.lineLabel, question: c.question,
      common: c.common, different: c.different, owner: c.owner, sequence: c.sequence,
      state: ST[c.v].label, color: ST[c.v].color, border: ST[c.v].border, dash: ST[c.v].dash,
      lanes: c.lanes.map(l => ({ code: l.code, state: ST[l.v].label, color: ST[l.v].color, border: ST[l.v].border, dash: ST[l.v].dash })),
      typeCode: TYPES[c.type].code, typeLabel: TYPES[c.type].label,
      typeRadius: TYPES[c.type].radius, typeStroke: TYPES[c.type].stroke
    }));`, log)

  // 18 · mapa de acoes · a acao ligada ao portao que realmente segura
  out = replaceBlock(out, 'const departments = [',
    'const departments = window.__SINTONIA__.departments || [];', log)

  // 19 · arquivados
  out = replaceBlock(out, 'const archived = [',
    `const archived = (window.__SINTONIA__.archived || []).map(a => Object.assign({}, typeVis(a.type), {
      title: a.title, reason: a.reason, state: a.state, when: a.when
    }));`, log)

  // 20 · DETALHES TECNICOS, FECHADOS POR PADRAO
  //
  // O detalhe do objeto era uma tela de engenharia: EVIDENCE_ID, SOURCE_ID,
  // OBSERVED_AT, INDEPENDENCE_STATE, SIGNAL_FAMILY, CANONICAL_PAYLOAD_TYPE.
  // Tudo verdadeiro, tudo necessario — e nenhum diretor precisa disso aberto.
  //
  // Nada e removido. As linhas ficam no DOM, com o mesmo texto e o mesmo valor,
  // e voltam inteiras num clique. O que muda e o estado inicial.
  //
  // Por que em tempo de execucao e nao no HTML: o casco redesenha a tela a cada
  // troca de estado, entao marcar uma vez no arquivo nao pegaria o que aparece
  // depois. O observador reaplica a marcacao a cada redesenho.
  out = replaceOnce(out, '</body>',
    `<script>
(function () {
  // Nome de maquina: TUDO_MAIUSCULO com underscore, ou codigo tipo EV-0001.
  var MAQUINA = /^([A-Z][A-Z0-9]*_[A-Z0-9_]+|[A-Z]{2,}-\\d{3,}|PROP-\\d+)$/;
  // Rotulo composto: "SIGNAL_FAMILY · TERRITORIAL", "GEO_RESOLUTION · NOT_KNOWN".
  // O nome de campo aparece no meio da frase, entao o teste de igualdade acima
  // nao pega — e era por ai que sobravam cem underscores na tela.
  var COMPOSTO = /[A-Z][A-Z0-9]*_[A-Z0-9_]{2,}/;
  // Nomes de maquina que NAO usam underscore e por isso escapavam:
  // identificador de receptor (R-H1-TERRITORIAL), codigo de mangueira (H2 · ...)
  // e o estado de encanamento UNWIRED.
  var OUTROS = /^(R-H\\d[A-Z0-9-]*|H[1-9] · .+|UNWIRED|PROVENANCE|RECEPTOR_ID|HOSE_ID)$/;
  // Estes ficam: sao a RESPOSTA, nao o encanamento. Esconder "nao sabemos"
  // seria esconder justamente o que o portal existe para dizer.
  var FICAM = /^(NAO SEI|NAO MEDIDO|NOT_KNOWN|NOT_MEASURED|EMPTY_VALID|NAO MEDIDA)$/;

  function linhaDe(el) {
    // sobe ate a linha que contem o rotulo e o valor, sem passar do bloco
    var n = el, i = 0;
    while (n && n.parentElement && i++ < 3) {
      n = n.parentElement;
      if (n.children.length >= 2 && n.children.length <= 4) return n;
    }
    return null;
  }

  function marcar() {
    var w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    var n, alvos = [];
    while ((n = w.nextNode())) {
      var t = (n.nodeValue || '').trim();
      if (t.length < 4 || t.length > 90) continue;
      if (FICAM.test(t)) continue;
      var exato = MAQUINA.test(t) || OUTROS.test(t);
      var dentro = !exato && COMPOSTO.test(t);
      if (!exato && !dentro) continue;
      var p = n.parentElement;
      if (!p || p.tagName === 'SCRIPT' || p.tagName === 'STYLE') continue;
      if (p.closest('[data-ux-tecnico]')) continue;
      // Rotulo composto some sozinho, sem levar a linha inteira junto: o valor
      // ao lado costuma ser a informacao util.
      var alvo = exato ? (linhaDe(p) || p) : p;
      if (alvo && !alvo.hasAttribute('data-ux-tecnico')) alvos.push(alvo);
    }
    alvos.forEach(function (l) { l.setAttribute('data-ux-tecnico', '1'); });
    return alvos.length;
  }

  function botao() {
    if (document.getElementById('ux-tec-btn')) return;
    var b = document.createElement('button');
    b.id = 'ux-tec-btn';
    b.textContent = 'Detalhes técnicos';
    b.onclick = function () {
      var on = document.body.classList.toggle('ux-tecnico-aberto');
      b.textContent = on ? 'Ocultar detalhes técnicos' : 'Detalhes técnicos';
    };
    document.body.appendChild(b);
  }

  // ── ORDEM DA PAGINA ─────────────────────────────────────────────────────
  //
  // O mapa de acoes estava a dezessete mil pixels do topo, depois de tres
  // blocos de receptor. Quem abre o objeto le O QUE e ONDE em dois segundos
  // e depois precisa rolar meia hora para descobrir QUEM DEVE OLHAR.
  //
  // Nada e recriado: o mesmo no do DOM e movido de lugar. O casco redesenha a
  // cada troca de estado, entao a mudanca e reaplicada pelo observador.
  function tituloEl(txt) {
    var t = txt.toLowerCase();
    var els = document.querySelectorAll('*');
    for (var i = 0; i < els.length; i++) {
      var e = els[i];
      if (e.children.length === 0 && e.textContent.trim().toLowerCase() === t) return e;
    }
    return null;
  }

  // A secao e o filho da COLUNA que contem o titulo. A coluna e o ancestral
  // alto com muitos filhos — e assim que a pagina do objeto e montada.
  function secaoDe(el) {
    var n = el;
    while (n && n.parentElement) {
      var p = n.parentElement;
      // Limiar frouxo de proposito: a coluna da Visao Geral tem menos secoes e
      // menos altura que a do objeto, e o criterio apertado a deixava de fora.
      if (p.children.length >= 4 && p.getBoundingClientRect().height > 1200) return n;
      n = p;
    }
    return null;
  }
  function secao(txt) { var e = tituloEl(txt); return e ? secaoDe(e) : null; }

  function ordenar() {
    // 1 · blocos de receptor sao engenharia: vao para os detalhes tecnicos.
    ['Receptor territorial do objeto', 'Receptor de vozes e ativação',
     'Receptor de especialista do problema'].forEach(function (t) {
      var s = secao(t);
      if (s && !s.hasAttribute('data-ux-tecnico')) s.setAttribute('data-ux-tecnico', '1');
    });

    // 2 · o mapa de acoes sobe para logo depois da sintese.
    var acoes = secao('Mapa de ações por área');
    var sintese = secao('Síntese');
    if (acoes && sintese && sintese.parentElement === acoes.parentElement &&
        acoes.previousElementSibling !== sintese) {
      sintese.parentElement.insertBefore(acoes, sintese.nextElementSibling);
    }

    // 3 · a timeline vira faixa: contexto, nao protagonista.
    var tl = secao('Timeline de inteligência do objeto');
    if (tl && !tl.hasAttribute('data-ux-faixa')) tl.setAttribute('data-ux-faixa', '1');

    // 4 · a Visao Geral tambem precisa responder QUEM DEVE OLHAR.
    //
    //     As quatro acoes NAO sao do objeto aberto: elas nascem do conjunto
    //     inteiro — "nomear o issue nos itens territoriais", "confirmar efeito
    //     no rotulo dos 155 registros". Sao acoes do portal. Por isso podem
    //     aparecer na Visao Geral sem inventar nada.
    //
    //     E uma COPIA do mesmo bloco, refeita a cada redesenho para nunca
    //     mostrar um estado velho. Se o bloco original nao existir, nao ha
    //     copia — nada e fabricado para preencher a tela.
    //     Clonar nao dava: o casco so desenha a tela do objeto quando ela esta
    //     aberta, entao na Visao Geral o bloco original nem existe no DOM.
    //     Este e montado a partir de window.__SINTONIA__.departments, que e a
    //     MESMA fonte do outro — e usa os tokens de cor do proprio casco.
    var momento = secao('C · LEITURA DO MOMENTO') || secao('Leitura do momento');
    var deps = (window.__SINTONIA__ && window.__SINTONIA__.departments) || [];
    var antiga = document.getElementById('ux-acoes-na-home');
    if (momento && deps.length && !antiga) {
      var box = document.createElement('div');
      box.id = 'ux-acoes-na-home';
      box.setAttribute('style',
        'background:var(--s1);border:1px solid var(--hair2);border-radius:16px;' +
        'padding:22px 24px;margin:12px 0;');
      var h = '<div style="font:600 11px/1 var(--font-primary);letter-spacing:.12em;' +
        'color:var(--t3);margin-bottom:6px">QUEM DEVE OLHAR</div>' +
        '<div style="font:400 11.5px/1.5 var(--font-primary);color:var(--t3);' +
        'margin-bottom:16px">Uma ação por área, e o estado dela. Área sem ação ' +
        'sustentada aparece como não determinada — o portal não preenche.</div>' +
        '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:12px">';
      deps.forEach(function (d) {
        h += '<div style="border:1px solid var(--hair2);border-radius:12px;padding:14px 16px">' +
          '<div style="font:600 11.5px/1.3 var(--font-primary);color:var(--t1);' +
          'margin-bottom:8px">' + d.name + '</div>' +
          '<div style="font:400 11.5px/1.45 var(--font-primary);color:var(--t2);' +
          'margin-bottom:10px">' + (d.action || '—') + '</div>' +
          '<span style="font:600 9.5px/1 var(--font-primary);letter-spacing:.08em;' +
          'border:1px dashed var(--hair2);border-radius:9999px;padding:5px 9px;' +
          'color:var(--t3)">' + (d.state || '—') + '</span></div>';
      });
      box.innerHTML = h + '</div>';
      momento.parentElement.insertBefore(box, momento.nextElementSibling);
    }
  }

  // ── FRASES QUE EXPLICAM, E POR ISSO NAO PODEM SER ESCONDIDAS ────────────
  //
  // Quatro frases falavam em nome de campo no meio da explicacao. Nao dava
  // para esconder: elas SAO a explicacao, e cada uma protege uma distincao de
  // que o produto inteiro depende. Foram reescritas, sem perder a distincao.
  //
  // A troca e feita aqui e nao no arquivo porque parte delas e montada na hora
  // ("4 OBJETO(S) SEM ...") — um replace no HTML nao alcanca o que ainda nao
  // existe. Trocar texto nao dispara o observador (ele olha childList), entao
  // nao ha laco.
  var FRASES = [
    ['GEO_RESOLUTION = POINT', 'coordenada'],
    ['REGISTRATION_DEADLINE ≠ LOCAL_ADAMA_PORTFOLIO_CONTEXT. Prazo de registro nunca prova resposta ADAMA.',
     'Prazo de registro e resposta da ADAMA são coisas diferentes: a data de um registro nunca prova o que a ADAMA vai fazer.'],
    ['REGISTERED_RESPONSE_STATE permanece NOT_PROVED',
     'a resposta da ADAMA segue não confirmada'],
    ['a soma NÃO se chama CREATORS_READY. Pessoa != empresa,',
     'a soma não pode se chamar "criadores prontos". Pessoa não é empresa,'],
    // Codigo de mangueira dentro da frase. A lei que ela protege — uma fonte
    // repetida nao vira duas famílias — continua dita por inteiro.
    ['Mesma origem publicadora da perna TERRITORIAL (H5 depende de H1).',
     'Mesma origem publicadora da observação territorial: a série de campo depende dela.'],
  ];

  function frases() {
    var w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT), n;
    while ((n = w.nextNode())) {
      // O proprio <script> e um no de texto, e ele contem as frases que estao
      // sendo procuradas. Sem esta linha, a varredura reescrevia o codigo-fonte
      // exibido no DOM e o dicionario passava a apontar cada frase para ela
      // mesma. Nao quebrava nada em execucao — e era sujeira que eu ia deixar.
      var pai = n.parentElement;
      if (!pai || pai.tagName === 'SCRIPT' || pai.tagName === 'STYLE') continue;
      var v = n.nodeValue;
      // Nem toda frase de maquina tem underscore: "H5 depende de H1" nao tem.
      // O filtro barato so serve para nao varrer a pagina inteira a toa.
      if (!v || (v.indexOf('_') < 0 && !/\\bH[1-9]\\b/.test(v))) continue;
      for (var i = 0; i < FRASES.length; i++) {
        if (v.indexOf(FRASES[i][0]) >= 0) v = v.split(FRASES[i][0]).join(FRASES[i][1]);
      }
      if (v !== n.nodeValue) n.nodeValue = v;
    }
  }

  var pendente = null;
  function agenda() {
    clearTimeout(pendente);
    pendente = setTimeout(function () { marcar(); ordenar(); frases(); botao(); }, 120);
  }
  agenda();
  new MutationObserver(agenda).observe(document.body, { childList: true, subtree: true });
})();
</script>
</body>`, 'ux:detalhes-tecnicos', log)

  out = replaceOnce(out, '</style>\n</head>',
    `  /* Fechado por padrao. Nada foi removido: um clique traz tudo de volta. */
  body:not(.ux-tecnico-aberto) [data-ux-tecnico] { display: none !important; }
  #ux-tec-btn {
    position: fixed; right: 18px; bottom: 18px; z-index: 9999;
    font: 600 10.5px/1 var(--font-primary); letter-spacing: .04em;
    color: var(--t2); background: var(--s1);
    border: 1px solid var(--hair2); border-radius: 9999px;
    padding: 9px 14px; cursor: pointer;
  }
  #ux-tec-btn:hover { color: var(--t1); }

  /* TIMELINE COMO FAIXA · ela ocupava dois mil pixels de altura para contar
     tres a cinco marcos. Vira uma tira horizontal que rola de lado; cada marco
     ganha largura fixa e a coluna de cada evento para de esticar a pagina.
     Nenhum evento foi removido — todos continuam ali, lado a lado. */
  /* O atributo style chega NORMALIZADO pelo navegador: "98px 28px", com
     espaco. O seletor sem espaco nao casava nada — a faixa continuava com dois
     mil e oitocentos pixels de altura e eu quase dei por resolvido. */
  [data-ux-faixa] div:has(> [style*="98px 28px"]) {
    flex-direction: row !important;
    gap: 18px; overflow-x: auto; padding-bottom: 10px;
  }
  [data-ux-faixa] [style*="98px 28px"] {
    display: flex !important; flex-direction: column !important;
    flex: 0 0 220px; align-items: flex-start !important;
  }
  [data-ux-faixa] [style*="98px 28px"] > div {
    align-items: flex-start !important; text-align: left !important;
    width: 100%; padding-top: 0 !important;
  }
</style>
</head>`, 'ux:css-tecnico', log)

  return { html: out, log }
}
