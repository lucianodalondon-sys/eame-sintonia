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
    'OBJECT_ID: o.id, OBJECT_TYPE: TYPES[o.type].code,\n      COUNTRY_OF_FACT: (o.f && o.f.COUNTRY_OF_FACT) || COUNTRY[s.country].name,',
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
      title: 'SEM OBJETO DESTE TIPO NESTE PAÍS',
      meta: 'EMPTY_VALID · a mangueira não entregou objeto deste tipo para ' + COUNTRY[s.country].name,
      blocker: 'Não há bloqueador: não há objeto. Ausência declarada, não falha.',
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

  return { html: out, log }
}
