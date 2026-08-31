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

  // 13 · arquivados
  out = replaceBlock(out, 'const archived = [',
    `const archived = (window.__SINTONIA__.archived || []).map(a => Object.assign({}, typeVis(a.type), {
      title: a.title, reason: a.reason, state: a.state, when: a.when
    }));`, log)

  return { html: out, log }
}
