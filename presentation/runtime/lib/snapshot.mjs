// Monta o bundle de apresentacao a partir das nove mangueiras congeladas.
//
// O que sai daqui alimenta os receptores que JA existem no casco V8. Nenhum
// card novo, nenhuma hierarquia nova. Onde a mangueira nao tem dado, sai null
// e o casco mostra o vazio que ele ja sabe mostrar.

import { readFrozen, fullSha, HOSES, h1, h2, h3, h4, h5, h6, h7, h8, h9 } from './hoses.mjs'

const LANGS = ['pt', 'en', 'es', 'fr', 'it']
const LAST_LABEL = { pt: 'Ultima evidencia', en: 'Last evidence', es: 'Última evidencia', fr: 'Dernière preuve', it: 'Ultima evidenza' }

/** Representacao textual por idioma, sem fabricar o que nao existe. */
const rep = (byLang) => {
  const out = {}
  for (const l of LANGS) out[l] = byLang[l] ?? null
  return out
}

export function buildSnapshot() {
  const H = { H1: h1(), H2: h2(), H3: h3(), H4: h4(), H5: h5(), H6: h6(), H7: h7(), H8: h8(), H9: h9() }

  const candidatesDoc = readFrozen('HEAD', 'data/refresh-corrected/ATTENTION-CANDIDATES.json')
  const stateMachine = readFrozen('HEAD', 'data/arbitration/ATTENTION-STATE-MACHINE.json')
  const headSha = fullSha('HEAD')

  // ── PROVENIENCIA POR MANGUEIRA ───────────────────────────────────────────
  const PROV = {}
  for (const [id, meta] of Object.entries(HOSES)) {
    PROV[id] = {
      SOURCE_BACKEND: 'GITHUB',
      REPOSITORY: 'lucianodalondon-sys/eame-sintonia',
      COMMIT_SHA: fullSha(meta.freeze === 'HEAD' ? headSha : meta.freeze),
      SOURCE_ID: H[id].source_id ?? null,
      AS_OF_DATE: H[id].captured_at ?? null,
      HOSE: meta.name,
    }
  }

  // ── TIPO E ESTADO ────────────────────────────────────────────────────────
  const TYPE_OF = {
    TERRITORIAL_SLICE: 'case',
    LONGITUDINAL_FIELD_PRESSURE: 'field',
    REGULATORY_DEADLINE: 'reg',
    IDENTITY_CHAIN_CONVERGENCE: 'comp',
  }
  const STATE_OF = {
    ATTENTION_READY: 'ready',
    ATTENTION_CANDIDATE_TEST: 'candidate',
    VALID_EVIDENCE_NOT_ATTENTION_READY: 'valid',
    NEEDS_EVIDENCE: 'needs',
    FORMING: 'forming',
    WATCH: 'watch',
    FUTURE: 'future',
  }
  // Doenca e o unico eixo que a fonte nomeia. Sem nome tecnico da fonte, a
  // linha ADAMA fica 'none' — nunca chutada pela cultura.
  const DISEASE_ISSUES = new Set(['REPILO', 'SEPTORIA', 'FUSARIUM', 'DOWNY_MILDEW', 'FLAVESCENCE'])
  const lineOf = (c) => (c.ISSUE && DISEASE_ISSUES.has(c.ISSUE) ? 'disease' : 'none')

  const HOSE_OF_TYPE = { case: 'H1', reg: 'H2', comp: 'H3', field: 'H5' }

  // ── EVIDENCIA ────────────────────────────────────────────────────────────
  const EVIDENCE = {}
  let evN = 0
  const nextEv = () => 'EV-' + String(++evN).padStart(4, '0')

  const addEvidence = (hose, claim, opts = {}) => {
    const id = nextEv()
    EVIDENCE[id] = {
      hose,
      claim,
      sourceId: opts.sourceId ?? PROV[hose].SOURCE_ID,
      backend: 'GITHUB',
      lang: (opts.lang || 'UNKNOWN').toUpperCase(),
      level: opts.level || 'naomedido',
      // ORIGINAL_TEXT: so entra quando a passagem existe no freeze.
      original: opts.original ?? null,
      // TRADUCAO: nunca fabricada. Ausente permanece ausente.
      translated: opts.translated ?? null,
      commit: PROV[hose].COMMIT_SHA,
      asOf: PROV[hose].AS_OF_DATE,
      note: opts.note ?? null,
      unresolved: opts.unresolved ?? false,
    }
    return id
  }

  // ── OBJETOS DE ATENCAO ───────────────────────────────────────────────────
  const RAW = []
  for (const c of candidatesDoc.CANDIDATES) {
    const type = TYPE_OF[c.TYPE]
    if (!type) continue
    const hose = HOSE_OF_TYPE[type]
    const f = c.FACTS || {}

    // Passagem real do documento, quando o freeze a preservou.
    const passage = Array.isArray(c.PAIR_PASSAGES) && c.PAIR_PASSAGES.length ? c.PAIR_PASSAGES[0] : null
    const srcLang = c.COUNTRY === 'IT' ? 'it' : c.COUNTRY === 'FR' ? 'fr' : c.COUNTRY === 'ES' ? 'es' : 'unknown'

    const evId = addEvidence(hose, c.DERIVATION_RULE || 'Regra de derivacao declarada no freeze.', {
      lang: srcLang,
      level: c.ATTENTION_STATE === 'ATTENTION_CANDIDATE_TEST' ? 'parcial' : 'naoprovado',
      original: passage,
      note: c.JUDGMENT_REQUIRED ? 'JUDGMENT_REQUIRED · ' + c.JUDGMENT_REQUIRED : null,
      unresolved: hose === 'H3' && !H.H3.resolved,
    })

    const meta = []
    if (c.COUNTRY) meta.push('COUNTRY_OF_FACT · ' + c.COUNTRY)
    meta.push('CROP · ' + (c.CROP || 'NOT_KNOWN'))
    meta.push('ISSUE · ' + (c.ISSUE || 'NOT_KNOWN'))
    if (c.SLICE) meta.push('SLICE · ' + c.SLICE)

    // Portoes: medidos, nunca promovidos.
    const gates = []
    if (type === 'case') {
      gates.push(['Fato observado', f.BODY_ITEMS_IN_COUNTRY > 0 ? 'provado' : 'naomedido'])
      gates.push(['Cultura', f.WITH_CROP > 0 ? 'provado' : 'naoprovado'])
      gates.push(['Issue nomeado', f.WITH_ISSUE > 0 ? 'provado' : 'naoprovado'])
      gates.push(['Recorte geografico', f.WITH_LOCALITY > 0 ? 'provado' : 'naoprovado'])
      gates.push(['Resolucao temporal', f.WITH_TIME > 0 ? 'parcial' : 'naoconect'])
      gates.push(['Par cultura x problema', f.WITH_PAIR_PROVEN > 0 ? 'provado' : 'naoprovado'])
      gates.push(['Chave territorial completa', f.WITH_FULL_KEY > 0 ? 'provado' : 'naopronto'])
    } else if (type === 'reg') {
      gates.push(['Data oficial', 'provado'])
      gates.push(['Registro afetado', 'provado'])
      gates.push(['Titular', 'provado'])
      gates.push(['Efeito no rotulo', 'naoprovado'])
      gates.push(['Revisao humana', 'naopronto'])
    } else if (type === 'comp') {
      gates.push(['Marca registrada', 'provado'])
      gates.push(['Registro local', 'provado'])
      gates.push(['Atividade paga observada', 'medido'])
      gates.push(['Concordancia titular', 'provado'])
      gates.push(['Entrada final de refresh', H.H3.resolved ? 'provado' : 'naopronto'])
    } else {
      gates.push(['Serie', 'provado'])
      gates.push(['Linha de base', 'provado'])
      gates.push(['Coorte', 'provado'])
      gates.push(['N por leitura', 'medido'])
      gates.push(['Backtest', 'naopronto'])
    }

    const blockerPt = blockerFor(c, type, H)
    RAW.push({
      id: c.CANDIDATE_ID,
      type, line: lineOf(c), state: STATE_OF[c.ATTENTION_STATE] || 'needs',
      win: 'naosei',
      evidenceId: evId,
      srcLang,
      // Titulo e bloqueador sao TEXTO. Vao por representacao de idioma.
      i18n: {
        title: Object.fromEntries(LANGS.map(l => [l, titleFor(c, type, l)])),
        blocker: Object.fromEntries(LANGS.map(l => [l, blockerFor(c, type, H, l)])),
        last: Object.fromEntries(LANGS.map(l => [l, `${LAST_LABEL[l]} · ${PROV[hose].AS_OF_DATE || '—'}`])),
      },
      title: titleFor(c, type),
      meta,
      gates,
      blocker: blockerPt,
      last: `${LAST_LABEL.pt} · ${PROV[hose].AS_OF_DATE || '—'}`,
      // Campos reais que o receptor F1 passa a exibir quando existem.
      f: {
        COUNTRY_OF_FACT: c.COUNTRY || null,
        REGION_OF_FACT: null,
        CROP: c.CROP || null,
        ISSUE: c.ISSUE || null,
        ISSUE_EVIDENCE_PASSAGE: passage,
        PUBLISHED_AT: PROV[hose].AS_OF_DATE || null,
        SOURCE_ID: PROV[hose].SOURCE_ID || null,
        CANONICAL_ENTITY_ID: c.CANDIDATE_ID,
        ATTENTION_STATE_RAW: c.ATTENTION_STATE,
        CONVERGENCE_CLASS: c.INFERENCES?.CONVERGENCE_CLASS || null,
        ITEMS_WITH_FULL_KEY: Array.isArray(c.ITEMS_WITH_FULL_KEY) ? c.ITEMS_WITH_FULL_KEY.length : null,
      },
      prov: PROV[hose],
    })
  }

  // ── EVIDENCIA ADICIONAL POR MANGUEIRA (receptores de detalhe) ────────────
  // H2 · prazos reais do registro nacional italiano
  const h2Ev = H.H2.next_expiries.slice(0, 5).map(e => addEvidence('H2',
    `Registro ${e.reg} · ${e.product} · vencimento declarado ${e.expiry}.`,
    { lang: 'it', level: 'provado', original: `${e.product} — ${e.actives} — ${e.status} — scadenza ${e.expiry}` }))

  // H3 · tuplas preliminares, marcadas como preliminares
  const h3Ev = H.H3.provadas.slice(0, 5).map(p => addEvidence('H3',
    `${p.META_COMPANY} · ${p.COUNTRY} · ${p.NOME_NORMALIZADO} — concordancia ${p.CONCORDANCIA_DE_TITULAR}.`,
    { lang: 'en', level: 'parcial', unresolved: true,
      note: 'FINAL_REFRESH_INPUT = NO · ' + p.MOTIVO_DO_NAO_FINAL,
      original: `TM ${p.TM_ST13?.[0] || '—'} · registro ${p.REGISTRATION_ID} · titular ${p.REGISTRATION_HOLDER}` }))

  // H5 · leitura da serie historica
  const h5Ev = addEvidence('H5',
    `${H.H5.readings_total} leituras em ${H.H5.seasons_available} safras (${H.H5.season_range?.join('–')}).`,
    { lang: 'es', level: 'medido', original: H.H5.field, note: H.H5.finding_max })

  // H8 · contas publicas identificadas, conteudo nao coletado
  const h8Ev = addEvidence('H8',
    `${H.H8.canonical_entities} contas publicas identificadas como link.`,
    { lang: 'unknown', level: 'medido', note: H.H8.zero_is_not_silence })

  // H7 · nao ha especialista provado
  const h7Ev = addEvidence('H7', 'Pessoa localizada nao e especialista: expertise no issue nao provada.',
    { lang: 'es', level: 'naoprovado', note: H.H7.verdict })

  // H6 · vozes de campo, pessoa separada de empresa
  const h6Ev = addEvidence('H6',
    `${H.H6.person_creator} PERSON_CREATOR e ${H.H6.farm_business} FARM_BUSINESS_ENTITY no indice.`,
    { lang: 'unknown', level: 'medido', note: H.H6.metric_law })

  // H9 · representacao de conteudo nao ligada
  const h9Ev = addEvidence('H9', 'Nenhum registro do acervo declara lingua de origem.',
    { lang: 'unknown', level: 'naomedido', note: H.H9.rule })

  // H4 · observacao Meta
  const h4Ev = addEvidence('H4',
    `${H.H4.canonical_entities} cartoes unicos; ${H.H4.observations} observacoes.`,
    { lang: 'unknown', level: 'medido', note: 'Observacao na Meta nao e movimento competitivo comprovado.' })

  // ── FONTES ───────────────────────────────────────────────────────────────
  const sources = []
  for (const s of H.H1.sources) {
    sources.push({
      name: s.SOURCE_ENTITY_ID,
      role: `SOURCE_ROLE · boletim territorial · ${s.SOURCE_COUNTRY} · SOURCE_ID ${s.SOURCE_ENTITY_ID}`,
      v: s.SOURCE_ROUTE_PROVED === 'YES' ? 'provado' : s.BODY_EXTRACTION_SUCCESS ? 'parcial' : 'naoconect',
      pub: '—', capture: H.H1.captured_at || '—', age: '—', latency: 'NÃO MEDIDA',
      docs: `${s.DOCS_FETCHED ?? '—'} / ${s.DOCS_TRIED ?? '—'}`,
    })
  }
  sources.push({ name: 'IT-T4-001 · registro nacional italiano', role: 'SOURCE_ROLE · registro e prazo · SOURCE_ID ' + H.H2.source_id, v: 'provado', pub: H.H2.captured_at || '—', capture: H.H2.captured_at || '—', age: '—', latency: 'NÃO MEDIDA', docs: `${H.H2.in_force} em vigor` })
  sources.push({ name: 'ES-T3-001 · RAIF Andalucía', role: 'SOURCE_ROLE · serie de campo · SOURCE_ID ' + H.H5.source_id, v: 'medido', pub: H.H5.captured_at || '—', capture: H.H5.captured_at || '—', age: '—', latency: 'NÃO MEDIDA', docs: `${H.H5.readings_total} leituras` })
  sources.push({ name: 'EUIPO · registro de marcas', role: 'SOURCE_ROLE · marca · SOURCE_ID ' + H.H3.source_id, v: H.H3.resolved ? 'provado' : 'revisar', pub: H.H3.captured_at || '—', capture: H.H3.captured_at || '—', age: '—', latency: 'NÃO MEDIDA', docs: `${H.H3.canonical_entities} tuplas preliminares` })
  sources.push({ name: `Contas publicas de concorrente · ${H.H8.canonical_entities} identificadas`, role: 'SOURCE_ROLE · comunicacao publica · CONTENT_COLLECTION_STAGE NOT_STARTED · SOURCE_ID ' + H.H8.source_id, v: 'medido', pub: '—', capture: '—', age: '—', latency: 'NÃO MEDIDA', docs: H.H8.attempted + ' tentadas' })
  sources.push({ name: 'Meta · biblioteca de anuncios', role: 'SOURCE_ROLE · atividade paga observada · SOURCE_ID ' + H.H4.source_id, v: 'medido', pub: H.H4.captured_at || '—', capture: H.H4.captured_at || '—', age: '—', latency: 'NÃO MEDIDA', docs: `${H.H4.canonical_entities} cartoes` })

  // ── VOLUMES (home) ───────────────────────────────────────────────────────
  // Volume nunca e atencao — mas some-lo do portal fazia H4 e H3 parecerem
  // inexistentes. Eles existem, medidos; o que nao existe e objeto de atencao
  // sustentado por eles. Cada linha diz a unidade, para nao virar "numero".
  const volumes = [
    { k: 'Itens com corpo analisado', v: String(H.H1.canonical_entities) },
    { k: 'Fontes conectadas', v: String(sources.length) },
    { k: 'Leituras de campo', v: String(H.H5.readings_total) },
    { k: 'Cartoes unicos na Meta', v: String(H.H4.canonical_entities) },
    { k: 'Observacoes de anuncio', v: String(H.H4.observations) },
    { k: 'Tuplas de concorrente (preliminares)', v: String(H.H3.canonical_entities) },
    { k: 'Tuplas sem cadeia fechada', v: String(H.H3.not_known) },
    { k: 'Registros IT com prazo futuro', v: String(H.H2.canonical_entities) },
    { k: 'Vozes de campo (pessoas)', v: String(H.H6.person_creator) },
  ]

  // ── SERIE DE CAMPO ───────────────────────────────────────────────────────
  const fieldStats = [
    { k: 'Leituras', v: String(H.H5.readings_total), st: 'medido' },
    { k: 'Safras disponiveis', v: String(H.H5.seasons_available), st: 'provado' },
    { k: 'Intervalo', v: (H.H5.season_range || []).join('–') || '—', st: 'provado' },
    { k: 'Linha de base', v: 'RETROSPECTIVA POSSIVEL', st: 'parcial' },
    { k: 'Backtest', v: 'NÃO PRONTO', st: 'naopronto' },
  ]

  // ── VOZES (H6) — pessoa nunca somada com empresa ─────────────────────────
  const voices = [
    { kind: 'ENTITY_KIND · PERSON_CREATOR', k: 'Voz publica relacionada a cultura e regiao', v: 'medido',
      note: H.H6.metric_law, rows: String(H.H6.raw_rows), ents: String(H.H6.person_creator),
      ready: String(H.H6.person_creator_ready) },
    { kind: 'ENTITY_KIND · FARM_BUSINESS_ENTITY', k: 'Negocio agricola ou parceiro publico', v: 'medido',
      note: H.H6.readiness_note, rows: String(H.H6.raw_rows), ents: String(H.H6.farm_business),
      ready: String(H.H6.farm_business_ready) },
  ]

  // ── CADEIA COMPETITIVA (H3) ──────────────────────────────────────────────
  const p0 = H.H3.provadas[0]
  const chain = [
    { step: 'ELO 1', k: 'Marca registrada', v: 'provado', note: p0 ? `${p0.NOME_NORMALIZADO} · ${p0.TM_OFFICE?.[0] || '—'} · ${p0.TM_ST13?.[0] || '—'}` : 'sem tupla' },
    { step: 'ELO 2', k: 'Registro local do produto', v: 'provado', note: p0 ? `registro ${p0.REGISTRATION_ID} · ${p0.REGISTRATION_HOLDER}` : 'sem tupla' },
    { step: 'ELO 3', k: 'Atividade paga observada', v: 'medido', note: p0 ? `${p0.ADS_OBSERVED} anuncios observados em ${p0.COUNTRY}` : 'sem tupla' },
    { step: 'ELO 4', k: 'Entrada final de refresh', v: H.H3.resolved ? 'provado' : 'naopronto', note: H.H3.unresolved_reason },
  ]

  // ── ACERVO · documentos reais, um por linha ──────────────────────────────
  // Sao as passagens que H1 baixou e analisou. Documento nao e objeto de
  // atencao: entra aqui como material bruto, com fonte, captura e pais.
  const itemsFinal = readFrozen(HOSES.H1.freeze, 'data/samples/TERRITORIAL/FINAL.json').ITEMS
  const itemsCorpo = readFrozen(HOSES.H1.freeze, 'data/samples/TERRITORIAL/CORPO-R2.json').ITEMS
  const vistos = new Set()
  const acervoRows = []
  for (const it of [...itemsFinal, ...itemsCorpo]) {
    if (vistos.has(it.ITEM_ID)) continue
    vistos.add(it.ITEM_ID)
    const issue = it.ISSUE && it.ISSUE !== 'NOT_KNOWN' ? it.ISSUE : null
    const crops = Array.isArray(it.CROP) ? it.CROP : it.CROP ? [it.CROP] : []
    acervoRows.push({
      // O titulo e o que a fonte declara; sem titulo, o proprio ITEM_ID.
      title: it.SOURCE_NAME || it.ITEM_ID,
      sub: [it.COUNTRY_OF_FACT || it.SOURCE_COUNTRY || '—',
            crops.length ? crops.join(' / ') : 'CROP NOT_KNOWN',
            issue || 'ISSUE NOT_KNOWN'].join(' · '),
      sourceId: it.SOURCE_ENTITY_ID || '—',
      capture: it.PUBLISHED_AT || it.CAPTURED_AT || '—',
      country: it.COUNTRY_OF_FACT || it.SOURCE_COUNTRY || '—',
      line: issue && DISEASE_ISSUES.has(issue) ? 'DISEASE' : 'SEM LINHA',
      lineColor: issue && DISEASE_ISSUES.has(issue) ? '#00a0df' : 'rgba(255,255,255,.42)',
      lineBorder: issue && DISEASE_ISSUES.has(issue) ? 'rgba(0,160,223,.45)' : 'rgba(151,139,135,.4)',
    })
  }

  // ── ACERVO · H2 · os prazos reais do registro nacional italiano ──────────
  // Registro nao e documento, mas e material do acervo pelo mesmo motivo: e o
  // que a fonte declara, linha a linha, com a fonte e a captura do lado.
  //
  // Entram os 20 proximos vencimentos congelados em IT-T4-001. NAO entram os
  // 155 como alerta: alerta e regua do Radar, e a regua nao muda porque a
  // profundidade aumentou. Aqui e profundidade, e so.
  //
  // Ordenados por data — o mais proximo primeiro, que e a unica ordem util
  // para quem vai ler.
  const proximos = [...(H.H2.next_expiries || [])].sort((a, b) =>
    String(a.expiry).localeCompare(String(b.expiry)))
  for (const e of proximos) {
    acervoRows.push({
      title: `${e.product} · REG ${e.reg}`,
      sub: [`ATIVO ${e.actives}`, `STATUS ${e.status}`, `VENCE ${e.expiry}`].join(' · '),
      sourceId: H.H2.source_id || 'IT-T4-001',
      capture: H.H2.captured_at || '—',
      country: 'IT',
      // Data no futuro nao e linha de produto e nao e cor de alerta: e data.
      line: 'PRAZO',
      lineColor: 'rgba(255,255,255,.62)',
      lineBorder: 'rgba(151,139,135,.55)',
    })
  }

  // ── H7 · CIENCIA / EXPERT ────────────────────────────────────────────────
  // Pessoa encontrada nao e especialista. O artefato mede NOT_REACHED nos dois
  // niveis, entao nenhuma linha aqui pode dizer "especialista". Tambem nao
  // exibimos nome: identidade de pessoa exige tratamento GDPR que nao foi feito.
  const u7 = H.H7.universe || {}
  const experts = [
    { name: `Pesquisadores no universo · ${u7.PESQUISADORES ?? '—'}`,
      org: 'ES-RESEARCHERS-OLIVE', proved: false, v: 'medido',
      relation: 'IDENTIDADE NAO EXPOSTA · tratamento GDPR nao iniciado' },
    { name: `Candidatos por nome · ${H.H7.candidates ?? '—'}`,
      org: 'cruzamento LinkedIn x YouTube x ciencia', proved: false, v: 'naoprovado',
      relation: 'casamento por nome nao prova expertise no issue' },
    { name: `Confirmados por segundo campo · ${H.H7.confirmed_by_second_field}`,
      org: H.H7.state, proved: false, v: 'naoprovado',
      relation: 'ISSUE_EXPERTISE_PROVED = FALSE em 100% do universo' },
  ]

  // ── EAME · camada cross-market, numero real por pais ─────────────────────
  const porPais = (code) => RAW.filter(o => ((o.f && o.f.COUNTRY_OF_FACT) || '').split('/').includes(code))
  const eameLanes = ['ES', 'IT', 'FR'].map(code => {
    const objs = porPais(code)
    return {
      code,
      objects: objs.length,
      candidates: objs.filter(o => o.state === 'candidate').length,
      ready: objs.filter(o => o.state === 'ready').length,
      evidence: objs.filter(o => o.evidenceId).length,
      signals: String(objs.length),
      // Nenhum pais tem relogio agronomico conectado: janela segue nao medida.
      windows: 'NAO MEDIDO',
      freshness: PROV.H1.AS_OF_DATE || '—',
      gaps: code === 'ES' ? 'issue nao nomeado por fonte tecnica em nenhum item'
        : code === 'IT' ? 'par cultura x problema provado em 1 item, segunda leitura ausente'
        : 'chave territorial completa nao fecha em nenhum item',
    }
  })

  // ── RELATORIOS · os freezes que sustentam este snapshot ──────────────────
  const reports = Object.entries(PROV).map(([id, p]) => ({
    kind: 'FREEZE',
    title: `${id} · ${p.HOSE}`,
    v: 'provado',
    fields: [
      { k: 'SOURCE_ID', v: p.SOURCE_ID || '—' },
      { k: 'AS_OF_DATE', v: p.AS_OF_DATE || '—' },
      { k: 'PROVENANCE · COMMIT_SHA', v: p.COMMIT_SHA.slice(0, 12) },
      { k: 'CANONICAL_ENTITIES', v: String(H[id].canonical_entities ?? '—') },
    ],
    note: 'Um freeze nao muda depois de emitido. Correcoes entram como nova versao.',
  }))

  // ── CROSS-MARKET · o unico objeto que atravessa os tres mercados ─────────
  // A cadeia de identidade e cross-market por construcao (ES/IT/FR). O prazo
  // regulatorio nao e: vive so na Italia, e dizer o contrario seria inventar.
  const idchain = RAW.find(o => o.type === 'comp')
  const crossCases = [
    {
      line: '#c04ab8', lineLabel: 'CADEIA DE IDENTIDADE', type: 'comp',
      v: H.H3.resolved ? 'provado' : 'naopronto',
      question: 'A mesma marca de concorrente aparece com registro local e atividade paga observada em mais de um mercado?',
      common: `Unidade comum: tupla (competidor, pais, produto). ${H.H3.canonical_entities} com cadeia fechada, ${H.H3.not_known} sem.`,
      different: 'A concordancia titular fecha por pais. O que nao fecha e a entrada final de refresh, que depende do handoff da Meta.',
      owner: 'Market Development regional — investigacao',
      sequence: 'NAO MEDIDA',
      lanes: [
        { code: 'ES', v: 'parcial' },
        { code: 'IT', v: 'parcial' },
        { code: 'FR', v: 'parcial' },
      ],
    },
    {
      line: '#00a0df', lineLabel: 'PRAZO REGULATORIO', type: 'reg', v: 'parcial',
      question: 'O prazo regulatorio observado toca mais de um mercado?',
      common: `${H.H2.canonical_entities} registros ADAMA em vigor com data futura declarada.`,
      different: 'Medido apenas na Italia. Espanha e Franca nao tiveram o registro nacional lido nesta rodada — ausencia de leitura, nao ausencia de prazo.',
      owner: 'Regulatorio local + coordenacao regional',
      sequence: 'NAO MEDIDA',
      lanes: [
        { code: 'ES', v: 'naosei' },
        { code: 'IT', v: 'provado' },
        { code: 'FR', v: 'naosei' },
      ],
    },
  ]

  // ── MAPA DE ACOES · a acao que muda o estado, e so ela ───────────────────
  // Cada area recebe a acao ligada ao portao que esta segurando de verdade.
  const evPrimeira = Object.keys(EVIDENCE)[0]
  const departments = [
    { name: 'Market Development', kind: 'invest', core: true, state: 'naodeterm', basis: [evPrimeira],
      action: 'Programar a segunda leitura independente dos recortes em teste.',
      why: 'E a unica acao que muda o estado de um objeto hoje: nenhum recorte tem confirmacao independente.',
      time: 'antes do proximo checkpoint · data nao determinada' },
    { name: 'Technical / Science', kind: 'invest', state: 'naodeterm', basis: [evPrimeira],
      action: 'Nomear o issue por fonte tecnica nos itens territoriais.',
      why: `O portao "issue nomeado" esta aberto em ${RAW.filter(o => o.type === 'case').length} recortes de fenomeno.`,
      time: 'sem prazo externo · depende de agenda tecnica' },
    { name: 'Regulatorio', kind: 'invest', state: 'naodeterm', basis: [evPrimeira],
      action: `Confirmar efeito no rotulo dos ${H.H2.canonical_entities} registros com data futura.`,
      why: 'Expiracao declarada nao e retirada de produto — o efeito exige confirmacao.',
      time: 'ligado a data oficial do registro' },
    { name: 'Competitive Intelligence', kind: 'invest', state: 'naodeterm', basis: [evPrimeira],
      action: 'Congelar o handoff canonico da Meta para liberar a entrada final de refresh.',
      why: `${H.H3.canonical_entities} tuplas estao presas em join preliminar por causa disso.`,
      time: 'depende do coordenador da Meta' },
  ]

  // ── COBERTURA ────────────────────────────────────────────────────────────
  const coverage = {}
  for (const id of Object.keys(HOSES)) {
    coverage[id] = {
      loaded: true,
      raw_rows: H[id].raw_rows ?? null,
      canonical_entities: H[id].canonical_entities ?? null,
      commit: PROV[id].COMMIT_SHA,
      as_of: PROV[id].AS_OF_DATE,
    }
  }

  const observations = H.H4.observations + H.H5.readings_total

  return {
    snapshot: {
      SOURCE_BACKEND: 'GITHUB',
      MODE: 'FROZEN_SNAPSHOT',
      NOT_SUPABASE: 'Este bundle nao veio do Supabase. O adapter de snapshot sera trocado depois.',
      GENERATED_FROM_HEAD: headSha,
      LANGS,
      CANONICAL_CASCO_SHA: 'd28f6b5876e2fa28720eb555a8b99a275e56c229ed0ac5c4b07edf89f4e81328',
    },
    RAW, EVIDENCE, sources, volumes, fieldStats, voices, chain, acervoRows, experts, eameLanes, reports, crossCases, departments,
    archived: [],
    coverage,
    stateMachine: stateMachine.ESTADO_MEDIDO_HOJE,
    hoses: H,
    prov: PROV,
    totals: {
      ATTENTION_OBJECTS: RAW.length,
      EVIDENCE: Object.keys(EVIDENCE).length,
      SOURCES: sources.length,
      OBSERVATIONS: observations,
      H3_PRELIMINARY_COUNT: H.H3.preliminary_count,
      H3_PROMOTED_COUNT: RAW.filter(o => o.type === 'comp' && o.state === 'ready').length,
    },
    extraEvidenceIds: { h2Ev, h3Ev, h5Ev, h6Ev, h7Ev, h8Ev, h9Ev, h4Ev },
  }
}

// O titulo e COMPOSTO por nos a partir de campos estruturados (cultura, issue,
// pais) — nao e citacao de fonte. Por isso pode sair nos cinco idiomas sem
// fabricar traducao de ninguem: o que traduz e a nossa moldura, e CROP/ISSUE
// continuam no vocabulario canonico, sem traducao, em todos eles.
const TITLE_FRAME = {
  reg: {
    pt: 'Prazo regulatorio — registros ADAMA na Italia',
    en: 'Regulatory deadline — ADAMA registrations in Italy',
    es: 'Plazo regulatorio — registros ADAMA en Italia',
    fr: 'Échéance réglementaire — enregistrements ADAMA en Italie',
    it: 'Scadenza regolatoria — registrazioni ADAMA in Italia',
  },
  comp: {
    pt: 'Cadeia de identidade — convergencia marca x registro x atividade',
    en: 'Identity chain — trademark x registration x activity convergence',
    es: 'Cadena de identidad — convergencia marca x registro x actividad',
    fr: 'Chaîne d’identité — convergence marque x enregistrement x activité',
    it: 'Catena di identità — convergenza marchio x registrazione x attività',
  },
  field: {
    pt: 'Pressao longitudinal de campo', en: 'Longitudinal field pressure',
    es: 'Presión longitudinal de campo', fr: 'Pression longitudinale de terrain',
    it: 'Pressione longitudinale di campo',
  },
  case: {
    pt: 'Fenomeno', en: 'Phenomenon', es: 'Fenómeno', fr: 'Phénomène', it: 'Fenomeno',
  },
}
const NOT_NAMED = {
  crop: { pt: 'cultura nao nomeada', en: 'crop not named', es: 'cultivo no nombrado', fr: 'culture non nommée', it: 'coltura non nominata' },
  issue: { pt: 'issue nao nomeado', en: 'issue not named', es: 'problema no nombrado', fr: 'problème non nommé', it: 'problema non nominato' },
}

function titleFor(c, type, lang = 'pt') {
  if (type === 'reg' || type === 'comp') return TITLE_FRAME[type][lang]
  const crop = c.CROP || NOT_NAMED.crop[lang]
  const issue = c.ISSUE || NOT_NAMED.issue[lang]
  return `${TITLE_FRAME[type][lang]} — ${crop} / ${issue} (${c.COUNTRY})`
}

// O bloqueador tem duas partes: a MOLDURA ("Bloqueador: ...") e o MOTIVO.
// A moldura e nossa e vai nos cinco idiomas. O motivo, quando vem citado de um
// freeze (H3, H5), fica na lingua em que foi medido — traduzir uma medicao
// alheia seria inventar. Por isso ele sai marcado.
const BLOCK = {
  frame: { pt: 'Bloqueador', en: 'Blocker', es: 'Bloqueador', fr: 'Bloqueur', it: 'Bloccante' },
  noIssue: {
    pt: 'nenhuma passagem nomeia o issue por fonte tecnica — sem nome, nao ha par cultura x problema.',
    en: 'no passage names the issue via a technical source — with no name there is no crop x issue pair.',
    es: 'ningún pasaje nombra el problema por fuente técnica — sin nombre no hay par cultivo x problema.',
    fr: 'aucun passage ne nomme le problème via une source technique — sans nom, pas de paire culture x problème.',
    it: 'nessun passaggio nomina il problema tramite fonte tecnica — senza nome non c’è coppia coltura x problema.',
  },
  noKey: {
    pt: 'chave territorial completa nao fecha em nenhum item.',
    en: 'the complete territorial key does not close in any item.',
    es: 'la clave territorial completa no cierra en ningún ítem.',
    fr: 'la clé territoriale complète ne se ferme dans aucun élément.',
    it: 'la chiave territoriale completa non chiude in nessun elemento.',
  },
  judgment: {
    pt: 'julgamento humano exigido', en: 'human judgment required',
    es: 'juicio humano exigido', fr: 'jugement humain requis', it: 'giudizio umano richiesto',
  },
  weak: {
    pt: 'convergencia insuficiente para atencao.', en: 'convergence insufficient for attention.',
    es: 'convergencia insuficiente para atención.', fr: 'convergence insuffisante pour l’attention.',
    it: 'convergenza insufficiente per l’attenzione.',
  },
}

function blockerFor(c, type, H, lang = 'pt') {
  const f = c.FACTS || {}
  const p = (motivo) => `${BLOCK.frame[lang]}: ${motivo}`
  // Motivo citado do freeze: marcado como medicao, nao traduzido.
  const citado = (txt) => p(lang === 'pt' ? txt : `${txt}  [PT · MEASURED_AS_IS]`)

  if (type === 'comp' && !H.H3.resolved) return citado(H.H3.unresolved_reason)
  if (type === 'case') {
    if (f.WITH_ISSUE === 0) return p(BLOCK.noIssue[lang])
    if (f.WITH_FULL_KEY === 0) return p(BLOCK.noKey[lang])
  }
  if (type === 'field') return citado(H.H5.finding_max || BLOCK.weak[lang])
  if (c.JUDGMENT_REQUIRED) return citado(`${BLOCK.judgment[lang]} — ${c.JUDGMENT_REQUIRED}`)
  return p(BLOCK.weak[lang])
}
