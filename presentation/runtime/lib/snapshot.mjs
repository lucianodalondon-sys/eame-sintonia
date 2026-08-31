// Monta o bundle de apresentacao a partir das nove mangueiras congeladas.
//
// O que sai daqui alimenta os receptores que JA existem no casco V8. Nenhum
// card novo, nenhuma hierarquia nova. Onde a mangueira nao tem dado, sai null
// e o casco mostra o vazio que ele ja sabe mostrar.

import { readFrozen, fullSha, HOSES, h1, h2, h3, h4, h5, h6, h7, h8, h9 } from './hoses.mjs'

const LANGS = ['pt', 'en', 'es', 'fr', 'it']

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
        title: rep({ pt: titleFor(c, type) }),
        blocker: rep({ pt: blockerPt }),
      },
      title: titleFor(c, type),
      meta,
      gates,
      blocker: blockerPt,
      last: 'Ultima evidencia · ' + (PROV[hose].AS_OF_DATE || '—'),
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
  sources.push({ name: 'Meta · biblioteca de anuncios', role: 'SOURCE_ROLE · atividade paga observada · SOURCE_ID ' + H.H4.source_id, v: 'medido', pub: H.H4.captured_at || '—', capture: H.H4.captured_at || '—', age: '—', latency: 'NÃO MEDIDA', docs: `${H.H4.canonical_entities} cartoes` })

  // ── VOLUMES (home) ───────────────────────────────────────────────────────
  const volumes = [
    { k: 'Itens com corpo analisado', v: String(H.H1.canonical_entities) },
    { k: 'Fontes conectadas', v: String(sources.length) },
    { k: 'Leituras de campo', v: String(H.H5.readings_total) },
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
    RAW, EVIDENCE, sources, volumes, fieldStats, voices, chain,
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

function titleFor(c, type) {
  if (type === 'reg') return 'Prazo regulatorio — registros ADAMA na Italia'
  if (type === 'comp') return 'Cadeia de identidade — convergencia marca x registro x atividade'
  if (type === 'field') return `Pressao longitudinal de campo — ${c.CROP} / ${c.ISSUE} (${c.COUNTRY})`
  return `Fenomeno — ${c.CROP || 'cultura nao nomeada'} / ${c.ISSUE || 'issue nao nomeado'} (${c.COUNTRY})`
}

function blockerFor(c, type, H) {
  if (type === 'comp' && !H.H3.resolved) return 'Bloqueador: ' + H.H3.unresolved_reason
  const f = c.FACTS || {}
  if (type === 'case') {
    if (f.WITH_ISSUE === 0) return 'Bloqueador: nenhuma passagem nomeia o issue por fonte tecnica — sem nome, nao ha par cultura x problema.'
    if (f.WITH_FULL_KEY === 0) return 'Bloqueador: chave territorial completa nao fecha em nenhum item.'
  }
  if (type === 'field') return 'Bloqueador: ' + (H.H5.finding_max || 'leitura da serie exige escopo completo.')
  if (c.JUDGMENT_REQUIRED) return 'Bloqueador: julgamento humano exigido — ' + c.JUDGMENT_REQUIRED
  return 'Bloqueador: convergencia insuficiente para atencao.'
}
