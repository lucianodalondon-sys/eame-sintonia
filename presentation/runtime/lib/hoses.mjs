// Adapters das nove mangueiras canonicas.
//
// Cada mangueira e lida do SEU PROPRIO commit congelado, via `git show`. Nada
// e lido da arvore de trabalho: se o commit nao existir, o build para. Isso
// mantem a proveniencia reproduzivel — PROVENANCE.COMMIT_SHA nao e um rotulo
// escrito a mao, e o commit de onde o byte saiu.
//
// LEI DESTE ARQUIVO
//   1. contagem de linha nunca vira contagem de entidade;
//   2. estado medido na origem nunca e promovido aqui;
//   3. campo ausente vira null, nunca texto inventado.

import { execSync } from 'node:child_process'

const REPO = new URL('../../../', import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, '$1')

export const HOSES = {
  H1: { name: 'TERRITORIAL',        freeze: '11fd7b5', handoff: '4ea268d' },
  H2: { name: 'REGULATORY_DEADLINE', freeze: 'd7b289425c5e436f3ce68e367b8706e11910f43b' },
  H3: { name: 'FORESIGHT',          freeze: 'dc32ce0', extra: '25194e3' },
  H4: { name: 'META',               freeze: 'acfd987', handoff: 'a2fad2d' },
  H5: { name: 'FIELD_HISTORICAL',   freeze: 'HEAD' },
  H6: { name: 'CREATOR_FIELD_VOICE', freeze: '248bd270', deep: 'a509c12' },
  H7: { name: 'SCIENCE_EXPERT',     freeze: 'HEAD' },
  H8: { name: 'PUBLIC_COMM',        freeze: 'c25e44b' },
  H9: { name: 'MULTILINGUAL',       freeze: '1443f643' },
}

/** Le um JSON de um commit congelado. Falha fechado. */
export function readFrozen(commit, path) {
  let buf
  try {
    buf = execSync(`git show ${commit}:${path}`, { cwd: REPO, maxBuffer: 1 << 30 })
  } catch {
    throw new Error(`FAIL_CLOSED · input inexistente: ${commit}:${path}`)
  }
  try {
    return JSON.parse(buf)
  } catch (e) {
    throw new Error(`FAIL_CLOSED · JSON invalido em ${commit}:${path}: ${e.message}`)
  }
}

/** Resolve um ref curto para o SHA completo, para gravar na proveniencia. */
export function fullSha(commit) {
  return execSync(`git rev-parse ${commit}`, { cwd: REPO }).toString().trim()
}

// ── H1 · TERRITORIAL ───────────────────────────────────────────────────────
export function h1() {
  const final = readFrozen(HOSES.H1.freeze, 'data/samples/TERRITORIAL/FINAL.json')
  const corpo = readFrozen(HOSES.H1.freeze, 'data/samples/TERRITORIAL/CORPO-R2.json')
  const m = final.MEDICAO

  // ITEMS sao passagens de documento, nao objetos. A entidade canonica de H1 e
  // o ITEM com corpo analisado; a chave territorial completa e um SUBCONJUNTO
  // dela, e e essa que autoriza um objeto de atencao.
  return {
    raw_rows: final.ITEMS.length + corpo.ITEMS.length,
    canonical_entities: m.UNIQUE_BODY_ANALYZED_ITEMS,
    with_full_key: m.WITH_FULL_TERRITORIAL_CASE_KEY,
    measurement: m,
    sources: final.ACAO_2_FONTES,
    guards: final.ACAO_3_GUARDS_DISPARADOS,
    por_recorte: final.POR_RECORTE,
    captured_at: final.CAPTURED_AT,
    source_id: final.SOURCE_ID,
  }
}

// ── H2 · REGULATORY DEADLINE ───────────────────────────────────────────────
export function h2() {
  const it = readFrozen(HOSES.H2.freeze, 'data/samples/IT-T4-001/IT-T4-001-adama-expiries.json')
  // products_total sao LINHAS do registro nacional. A entidade canonica desta
  // mangueira e o registro em vigor com data futura declarada — o unico
  // recorte que sustenta um REGULATORY_DEADLINE.
  return {
    raw_rows: it.products_total,
    in_force: it.in_force,
    with_future_expiry: it.with_future_expiry,
    canonical_entities: it.adama_in_force_with_future_expiry,
    next_expiries: it.adama_next_expiries,
    captured_at: it.captured_at,
    source_id: it.SOURCE_ID,
    original_language: it.ORIGINAL_LANGUAGE,
  }
}

// ── H3 · FORESIGHT / CADEIA DE IDENTIDADE ──────────────────────────────────
export function h3() {
  const a = readFrozen(HOSES.H3.freeze, 'data/samples/COMPETITOR-THREE-LAYER-AUDIT.json')
  // As 36 tuplas EXISTEM e sao reproduziveis deste commit. Mas todas carregam
  // FINAL_REFRESH_INPUT = NO: sao join preliminar entre branches, nao entrada
  // final. Entram como evidencia com o estado que tem. Nenhuma e promovida.
  const naoFinal = a.PROVADAS.filter(p => p.FINAL_REFRESH_INPUT === 'NO').length
  return {
    raw_rows: a.RESULTADO.CONSERVACAO_TUPLAS.TOTAL,
    canonical_entities: a.RESULTADO.THREE_LAYER_CHAIN_PROVED_TUPLES,
    not_known: a.RESULTADO.THREE_LAYER_CHAIN_NOT_KNOWN_TUPLES,
    rejected: a.RESULTADO.THREE_LAYER_CHAIN_REJECTED_TUPLES,
    resolved: a.ESTADO_DAS_PROVADAS.FINAL_REFRESH_INPUT === 'YES',
    unresolved_reason: a.ESTADO_DAS_PROVADAS.POR_QUE,
    preliminary_count: naoFinal,
    provadas: a.PROVADAS,
    nao_prova: a.O_QUE_ELA_NAO_PROVA,
    captured_at: a.captured_at,
    source_id: a.SOURCE_ID,
  }
}

// ── H4 · META ──────────────────────────────────────────────────────────────
export function h4() {
  const f = readFrozen(HOSES.H4.freeze, 'data/samples/META-EAME/META-HANDOFF-FREEZE-V1.json')
  const s2 = f.snapshot_2
  // ad_observations sao OBSERVACOES. A entidade canonica e o cartao unico.
  // Observacao na Meta nao e movimento competitivo comprovado — a propria
  // mangueira declara isso em exact_limitations.
  return {
    raw_rows: s2.ad_observations,
    canonical_entities: s2.unique_cards,
    ads_represented: s2.ads_represented,
    observations: s2.ad_observations,
    slices_total: s2.slices_total,
    slices_content: s2.slices_content,
    slices_honest_zero: s2.slices_honest_zero,
    limitations: f.exact_limitations,
    cannot_claim: f.cannot_claim,
    captured_at: s2.collection_completed_at,
    source_id: f.artifact,
  }
}

// ── H5 · FIELD HISTORICAL / RAIF ───────────────────────────────────────────
export function h5() {
  // Ledger canonico da coorte — nao o blob de resumo.
  const led = readFrozen(HOSES.H5.freeze, 'data/samples/RAIF-COORTE-REPILO.json')
  const ser = readFrozen(HOSES.H5.freeze, 'data/samples/ES-T3-001-repilo-serie-historica.json')
  return {
    raw_rows: led.readings_total,
    canonical_entities: led.seasons_available,
    readings_total: led.readings_total,
    seasons_available: led.seasons_available,
    season_range: led.season_range,
    seasons_in_summary: ser.seasons,
    readings_in_summary: ser.readings,
    field: led.field,
    field_note: led.field_note,
    finding_scope: led.FINDING_SCOPE,
    finding_max: led.FINDING_MAX,
    cohort_rule: led.cohort_rule,
    provinces: Object.keys(led.cohort_by_province || {}),
    captured_at: led.captured_at,
    source_id: led.SOURCE_ID,
    original_language: led.ORIGINAL_LANGUAGE,
  }
}

// ── H6 · CREATOR / FIELD VOICE ─────────────────────────────────────────────
export function h6() {
  const cap = readFrozen(HOSES.H6.freeze, 'data/samples/CREATOR-MAP-EAME/CREATOR-CAPABILITY-EAME.json')
  const fz = readFrozen(HOSES.H6.freeze, 'data/samples/CREATOR-MAP-EAME/PILOT-FREEZE-STATE.json')
  const byType = cap.LOOKUP_BY_ENTITY_TYPE || {}
  const counts = {}
  for (const [k, v] of Object.entries(byType)) counts[k] = Array.isArray(v) ? v.length : 0
  const entities = Object.values(counts).reduce((a, b) => a + b, 0)
  // PESSOA nao soma com EMPRESA. A propria mangueira declara METRIC_LAW.
  //
  // RAW_ROWS aqui e o numero de LINHAS do artefato no freeze — 12.295. Ele
  // existe para poder ser comparado com CANONICAL_ENTITIES, nunca para ser
  // exibido como "creators". A distancia entre 12.295 e 60 e o proprio ponto.
  const rawRows = Number(
    execSync(`git show ${HOSES.H6.freeze}:data/samples/CREATOR-MAP-EAME/CREATOR-CAPABILITY-EAME.json | wc -l`,
      { cwd: REPO, shell: 'bash', maxBuffer: 1 << 30 }).toString().trim())
  return {
    raw_rows: rawRows,
    canonical_entities: entities,
    by_entity_type: counts,
    person_creator: counts.PERSON_CREATOR || 0,
    farm_business: counts.FARM_BUSINESS || 0,
    person_creator_ready: cap.READINESS_METRICS.PERSON_CREATOR_ACTIVATION_READY,
    farm_business_ready: cap.READINESS_METRICS.FARM_BUSINESS_PARTNER_READY,
    contactable: cap.READINESS_METRICS.MARKETING_CONTACTABLE_ENTITIES_READY,
    metric_law: cap.METRIC_LAW,
    readiness_note: cap.READINESS_METRICS.NOTE,
    freeze_state: fz.STATE,
    captured_at: cap.CAPTURED_AT,
    source_id: cap.SOURCE_ID,
  }
}

// ── H7 · CIENCIA / EXPERT ──────────────────────────────────────────────────
export function h7() {
  const s = readFrozen(HOSES.H7.freeze, 'data/samples/ES-X-VOICE-SCIENCE.json')
  // Pessoa encontrada != especialista. So conta quem tem expertise no ISSUE
  // provada por segundo campo. O artefato mede NOT_REACHED nos dois niveis.
  const conf = s.RESULTADO_POR_PESSOA?.CONFIRMADOS_POR_SEGUNDO_CAMPO
  const confirmados = typeof conf === 'number' ? conf : Array.isArray(conf) ? conf.length : 0
  return {
    raw_rows: s.UNIVERSO?.PESQUISADORES ?? null,
    canonical_entities: 0,        // ISSUE_EXPERTISE_PROVED = 0
    candidates: s.RESULTADO_POR_PESSOA?.CANDIDATOS_POR_NOME ?? null,
    confirmed_by_second_field: confirmados,
    universe: s.UNIVERSO,
    state: s.STATE,
    verdict: s.VEREDITO,
    missing: s.O_QUE_FALTA_E_CONCRETO,
    captured_at: s.captured_at,
    source_id: s.SOURCE_ID,
  }
}

// ── H8 · PUBLIC COMM ───────────────────────────────────────────────────────
export function h8() {
  const c = readFrozen(HOSES.H8.freeze, 'data/samples/COMPETITOR-PUBLIC-COMM/CONTAS-V1.json')
  const accounts = Array.isArray(c.ACCOUNTS) ? c.ACCOUNTS : []
  // Zero conteudo nunca significa silencio: CONTENT_COLLECTION_STAGE segue
  // NOT_STARTED e isso e um estado declarado, nao uma medicao de ausencia.
  return {
    raw_rows: c.ACCOUNTS_ATTEMPTED ?? accounts.length,
    canonical_entities: c.ACCOUNTS_FOUND_AS_LINK ?? accounts.length,
    attempted: c.ACCOUNTS_ATTEMPTED ?? null,
    found_as_link: c.ACCOUNTS_FOUND_AS_LINK ?? null,
    authorized: c.ACCOUNTS_AUTHORIZED_FOR_COLLECTION ?? null,
    by_identity_state: c.BY_IDENTITY_STATE ?? null,
    by_country_scope: c.BY_COUNTRY_SCOPE ?? null,
    content_collection_stage: 'NOT_STARTED',
    zero_is_not_silence: 'CONTENT_COLLECTION_STAGE = NOT_STARTED. Zero conteudo coletado nao e zero conteudo publicado.',
    // As contas em si. Sao contas de EMPRESA: identidade de empresa nao e dado
    // pessoal, e por isso podem ser exibidas — ao contrario de H6 e H7, onde ha
    // gente e o tratamento GDPR nao comecou.
    accounts,
    captured_at: c.captured_at || c.CAPTURED_AT || null,
    source_id: c.SOURCE_ID,
  }
}

// ── H9 · MULTILINGUE ───────────────────────────────────────────────────────
export function h9() {
  // O contrato multilingue vive em documento, nao em dataset. A medicao que
  // importa ja esta no titulo do freeze: nenhum registro do acervo declara
  // lingua de origem. Original preservado; traducao ausente NAO e fabricada.
  const sha = fullSha(HOSES.H9.freeze)
  return {
    raw_rows: null,
    canonical_entities: 0,        // representacoes de conteudo ligadas = 0
    contract_commit: sha,
    source_language_declared_by_sources: 0,
    rule: 'SOURCE_LANGUAGE != DISPLAY_LANGUAGE. Traducao ausente permanece ausente.',
    state: 'CONTENT_REPRESENTATIONS_NOT_WIRED',
  }
}
