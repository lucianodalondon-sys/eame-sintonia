"""Injeta no schema canonico o CORPO das views, das RPCs e as politicas de RLS.

O schema JSON continua a autoridade: o SQL sai dele. Este script escreve os
corpos DENTRO do JSON e nao no .sql — editar o SQL a mao criaria uma segunda
verdade que a proxima geracao apagaria sem avisar.

Uso:
    py scripts/supabase_bodies.py --sync
"""
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA = os.path.join(RAIZ, 'data', 'supabase', 'SUPABASE-CANONICAL-SCHEMA.json')


# ── corpo das views ────────────────────────────────────────────────────────
# Regra que atravessa todas: nenhuma view esconde NOT_PROVED / UNKNOWN por join
# interno. Onde pode faltar linha, o join e LEFT.

VIEWS = {

'v_convergence_state': """
SELECT p.proposition_id,
       p.attention_object_id,
       p.proposition_text,
       p.convergence_kind,
       count(DISTINCT l.signal_family)
         FILTER (WHERE l.independence_state = 'INDEPENDENT')          AS independent_family_count,
       count(*) FILTER (WHERE l.independence_state = 'DEPENDENT')     AS dependent_leg_count,
       count(*)                                                       AS leg_count,
       CASE WHEN count(DISTINCT l.signal_family)
                   FILTER (WHERE l.independence_state = 'INDEPENDENT') >= 2
            THEN 'MULTI_SIGNAL' ELSE 'SINGLE_SIGNAL' END              AS convergence_state
  FROM convergence_proposition p
  LEFT JOIN convergence_leg l ON l.proposition_id = p.proposition_id
 GROUP BY p.proposition_id, p.attention_object_id, p.proposition_text, p.convergence_kind
""",

'v_attention_readiness': """
WITH gate AS (
  SELECT o.attention_object_id,
         r.requirement,
         coalesce(r.state, 'NOT_MEASURED'::field_state) AS state
    FROM attention_object o
    CROSS JOIN unnest(ARRAY['VALID_EVIDENCE','OBJECT_SPECIFIC_TRIGGER','TIME_RELEVANCE',
                            'DECISION_QUESTION','DECISION_OWNER']) AS req(requirement)
    LEFT JOIN attention_readiness r
           ON r.attention_object_id = o.attention_object_id
          AND r.requirement = req.requirement
)
SELECT attention_object_id,
       count(*) FILTER (WHERE state = 'PROVED')                       AS proved_gates,
       count(*)                                                       AS total_gates,
       bool_and(state = 'PROVED')                                     AS computed_is_ready,
       array_agg(requirement ORDER BY requirement)
         FILTER (WHERE state <> 'PROVED')                             AS blocking_requirements
  FROM gate
 GROUP BY attention_object_id
""",

'v_attention_feed': """
SELECT o.attention_object_id,
       o.object_type,
       o.country,
       o.attention_state,
       o.decision_question,
       o.decision_owner,
       o.adama_line,
       o.blocker_text,
       o.as_of_date,
       o.last_evidence_at,
       rd.computed_is_ready,
       rd.blocking_requirements,
       rp.language,
       rp.title,
       rp.summary,
       rp.attention_reason
  FROM attention_object o
  LEFT JOIN v_attention_readiness rd ON rd.attention_object_id = o.attention_object_id
  LEFT JOIN attention_object_representation rp ON rp.attention_object_id = o.attention_object_id
 WHERE o.attention_state = 'ATTENTION_READY'
""",

'v_radar': """
SELECT o.attention_object_id,
       o.object_type,
       o.country,
       o.attention_state,
       o.adama_line,
       o.blocker_text,
       o.last_evidence_at,
       rd.blocking_requirements,
       rp.language,
       rp.title
  FROM attention_object o
  LEFT JOIN v_attention_readiness rd ON rd.attention_object_id = o.attention_object_id
  LEFT JOIN attention_object_representation rp ON rp.attention_object_id = o.attention_object_id
""",

'v_object_detail': """
SELECT o.attention_object_id,
       o.object_type,
       o.country,
       o.attention_state,
       o.decision_question,
       o.decision_owner,
       o.as_of_date,
       pc.geo_id                          AS case_geo_id,
       pc.crop_term_id                    AS case_crop_term_id,
       pc.issue_term_id                   AS case_issue_term_id,
       pc.crop_issue_pairing_state,
       rdo.registration_id                AS deadline_registration_id,
       rdo.deadline_date,
       rdo.deadline_kind,
       rdo.status_as_declared_by_source,
       rdo.label_effect_state,
       rdo.max_authorized_action,
       cic.competitor_product_identity_id,
       lfp.series_id
  FROM attention_object o
  LEFT JOIN phenomenon_case pc                    ON pc.attention_object_id  = o.attention_object_id
  LEFT JOIN regulatory_deadline_object rdo        ON rdo.attention_object_id = o.attention_object_id
  LEFT JOIN competitor_identity_chain_object cic  ON cic.attention_object_id = o.attention_object_id
  LEFT JOIN longitudinal_field_pressure_object lfp ON lfp.attention_object_id = o.attention_object_id
""",

'v_evidence_drawer': """
SELECT e.evidence_id,
       e.source_id,
       s.source_name,
       s.source_role,
       e.source_location_country,
       g.country                     AS fact_location_country,
       g.region                      AS fact_location_region,
       e.source_published_at,
       e.captured_at,
       e.evidence_level,
       e.original_text,
       e.source_language,
       e.document_excerpt,
       e.passage_start,
       e.passage_end,
       e.source_url,
       sp.snapshot_id                AS source_snapshot_id,
       sp.original_ref,
       stp.source_backend,
       stp.repository, stp.path, stp.commit_sha, stp.content_hash,
       stp.db_schema, stp.table_or_view, stp.primary_key, stp.snapshot_id AS storage_snapshot_id,
       stp.as_of_date,
       ce.canonical_entity_id,
       ce.original_text              AS canonical_original_text,
       ce.source_language            AS canonical_source_language
  FROM evidence e
  LEFT JOIN source s              ON s.source_id = e.source_id
  LEFT JOIN geo_anchor g          ON g.geo_id = e.fact_location_geo_id
  LEFT JOIN source_provenance sp  ON sp.evidence_id = e.evidence_id
  LEFT JOIN storage_provenance stp ON stp.subject_kind = 'evidence'
                                  AND stp.subject_id = e.evidence_id
  LEFT JOIN content_entity ce     ON ce.evidence_id = e.evidence_id
""",

'v_crop_map_point': """
SELECT o.attention_object_id           AS object_id,
       o.object_type,
       o.attention_state,
       g.country,
       g.region,
       g.locality_text,
       g.geometry,
       g.geo_resolution,
       pc.crop_term_id                 AS crop,
       (g.geo_resolution = 'POINT' AND g.geometry IS NOT NULL) AS is_drawable,
       CASE WHEN g.geo_resolution = 'POINT' AND g.geometry IS NOT NULL THEN NULL
            WHEN g.geo_resolution = 'NOT_KNOWN' THEN 'GEO_RESOLUTION_NOT_KNOWN'
            WHEN g.geometry IS NULL              THEN 'NO_GEOMETRY'
            ELSE 'RESOLUTION_' || g.geo_resolution::text END      AS undrawable_reason
  FROM attention_object o
  LEFT JOIN phenomenon_case pc ON pc.attention_object_id = o.attention_object_id
  LEFT JOIN geo_anchor g       ON g.geo_id = pc.geo_id
""",

'v_object_timeline': """
SELECT ev.event_id,
       ev.attention_object_id,
       ev.event_type,
       ev.event_at,
       ev.event_at_resolution,
       ev.source_id,
       ev.observation_id,
       ev.state_before,
       ev.state_after,
       ev.what_changed,
       ev.signal_family_added,
       ev.gap_reason,
       ev.trigger_id,
       CASE WHEN ev.state_before IS NULL AND ev.state_after IS NULL THEN NULL
            ELSE coalesce(ev.state_before::text, '—') || ' → '
                 || coalesce(ev.state_after::text, '—') END AS state_transition_label
  FROM object_event ev
""",

'v_action_map': """
SELECT a.action_id,
       a.attention_object_id,
       a.department,
       a.action_type,
       a.action_state,
       a.action_text,
       a.why_text,
       a.time_horizon,
       a.is_central_area,
       a.regional_owner,
       count(ae.evidence_id)                                   AS evidence_basis_count,
       array_remove(array_agg(ae.evidence_id), NULL)           AS evidence_basis,
       (a.action_type <> 'BUSINESS_DECISION'
        OR count(ae.evidence_id) > 0)                          AS is_defensible
  FROM action a
  LEFT JOIN action_evidence ae ON ae.action_id = a.action_id
 GROUP BY a.action_id, a.attention_object_id, a.department, a.action_type,
          a.action_state, a.action_text, a.why_text, a.time_horizon,
          a.is_central_area, a.regional_owner
""",

'v_eame_cross_market': """
SELECT r.relation_id,
       r.relation_kind,
       r.dependency_type,
       fo.attention_object_id  AS from_object_id,
       fo.country              AS from_country,
       fo.object_type          AS from_object_type,
       fo.attention_state      AS from_state,
       to_.attention_object_id AS to_object_id,
       to_.country             AS to_country,
       to_.object_type         AS to_object_type,
       to_.attention_state     AS to_state,
       r.evidence_id
  FROM object_relation r
  JOIN attention_object fo  ON fo.attention_object_id = r.from_object_id
  JOIN attention_object to_ ON to_.attention_object_id = r.to_object_id
 WHERE fo.country <> to_.country
""",

'v_source_status': """
SELECT s.source_id,
       s.source_name,
       s.source_role,
       s.country                      AS publication_country,
       s.access_state,
       s.collection_state,
       c.source_status,
       c.latest_source_publication,
       c.latest_capture,
       c.observation_age_days,
       c.pipeline_latency_state,
       c.pipeline_latency_seconds,
       count(sn.snapshot_id)          AS snapshot_count
  FROM source s
  LEFT JOIN source_clock c    ON c.source_id = s.source_id
  LEFT JOIN source_snapshot sn ON sn.source_id = s.source_id
 GROUP BY s.source_id, s.source_name, s.source_role, s.country, s.access_state,
          s.collection_state, c.source_status, c.latest_source_publication,
          c.latest_capture, c.observation_age_days, c.pipeline_latency_state,
          c.pipeline_latency_seconds
""",

'v_issue_expert': """
SELECT p.person_id,
       p.display_name,
       p.country,
       p.identity_proved,
       p.gdpr_treatment_state,
       o.name                         AS organization,
       sp.relation_to_issue_as_declared,
       ie.crop_term_id,
       ie.issue_term_id,
       ie.issue_expertise_state,
       ie.evidence_id
  FROM issue_expertise ie
  JOIN person p            ON p.person_id = ie.person_id
  JOIN scientific_person sp ON sp.person_id = ie.person_id
  LEFT JOIN organization o ON o.organization_id = sp.organization_id
 WHERE ie.issue_expertise_state = 'PROVED'
   AND p.gdpr_treatment_state IN ('CLEARED','IN_REVIEW')
""",

'v_publish_provenance': """
SELECT o.attention_object_id,
       o.country,
       o.object_type,
       pr.publish_run_id,
       pr.pipeline_version,
       pr.schema_version,
       pr.published_at,
       pr.status,
       pr.shadow_validation_passed,
       prf.repository,
       prf.path,
       prf.commit_sha,
       prf.hose_id,
       stp.source_backend,
       stp.as_of_date
  FROM attention_object o
  LEFT JOIN publish_run pr        ON pr.publish_run_id = o.publish_run_id
  LEFT JOIN publish_run_freeze prf ON prf.publish_run_id = pr.publish_run_id
  LEFT JOIN storage_provenance stp ON stp.subject_kind = 'attention_object'
                                  AND stp.subject_id = o.attention_object_id
""",
}


# ── corpo das RPCs ─────────────────────────────────────────────────────────

RPCS = {

'resolve_representation': {
    'returns': """TABLE (
  language language_code,
  title text,
  summary text,
  interpretation text,
  attention_reason text,
  what_we_know text,
  what_we_dont_know text,
  requested_language language_code,
  fallback_used text
)""",
    'body': """
DECLARE
  v_chain language_code[] := ARRAY[p_requested_language, 'en', 'pt'];
  v_lang  language_code;
BEGIN
  -- a cadeia e explicita e curta. Nunca fabricar traducao para preencher.
  FOREACH v_lang IN ARRAY v_chain LOOP
    IF EXISTS (SELECT 1 FROM attention_object_representation r
                WHERE r.attention_object_id = p_entity_id AND r.language = v_lang) THEN
      RETURN QUERY
        SELECT r.language, r.title, r.summary, r.interpretation, r.attention_reason,
               r.what_we_know, r.what_we_dont_know,
               p_requested_language,
               CASE WHEN v_lang = p_requested_language THEN 'NO' ELSE 'YES' END
          FROM attention_object_representation r
         WHERE r.attention_object_id = p_entity_id AND r.language = v_lang;
      RETURN;
    END IF;
  END LOOP;
  -- nenhuma lingua da cadeia existe: dizer isso, nao inventar
  RETURN QUERY SELECT NULL::language_code, NULL::text, NULL::text, NULL::text,
                      NULL::text, NULL::text, NULL::text,
                      p_requested_language, 'NO_REPRESENTATION_AVAILABLE'::text;
END;
""",
},

'get_attention_object': {
    'returns': """TABLE (
  attention_object_id text,
  object_type object_type,
  country char(2),
  attention_state attention_state,
  decision_question text,
  decision_owner department,
  computed_is_ready boolean,
  blocking_requirements text[],
  display_language language_code,
  requested_language language_code,
  fallback_used text,
  title text,
  summary text,
  what_we_dont_know text
)""",
    'body': """
BEGIN
  RETURN QUERY
    SELECT o.attention_object_id, o.object_type, o.country, o.attention_state,
           o.decision_question, o.decision_owner,
           rd.computed_is_ready, rd.blocking_requirements,
           rr.language, rr.requested_language, rr.fallback_used,
           rr.title, rr.summary, rr.what_we_dont_know
      FROM attention_object o
      LEFT JOIN v_attention_readiness rd ON rd.attention_object_id = o.attention_object_id
      LEFT JOIN LATERAL resolve_representation(o.attention_object_id, p_display_language) rr
             ON TRUE
     WHERE o.attention_object_id = p_object_id;
END;
""",
},

'get_attention_feed': {
    'returns': """TABLE (
  attention_object_id text,
  object_type object_type,
  attention_state attention_state,
  blocker_text text,
  display_language language_code,
  requested_language language_code,
  fallback_used text,
  title text,
  empty_reason text
)""",
    'body': """
DECLARE
  v_total int;
BEGIN
  SELECT count(*) INTO v_total
    FROM attention_object o
   WHERE o.country = p_country AND o.attention_state = 'ATTENTION_READY';

  IF v_total = 0 THEN
    -- fila vazia se mostra vazia, COM o motivo. Nunca uma lista muda.
    RETURN QUERY
      SELECT NULL::text, NULL::object_type, NULL::attention_state, NULL::text,
             NULL::language_code, p_display_language, NULL::text, NULL::text,
             coalesce(
               (SELECT 'NO_OBJECT_PASSED_ALL_GATES: ' ||
                       string_agg(DISTINCT req, ', ')
                  FROM attention_object o2
                  JOIN v_attention_readiness rd2
                    ON rd2.attention_object_id = o2.attention_object_id
                  CROSS JOIN LATERAL unnest(rd2.blocking_requirements) AS req
                 WHERE o2.country = p_country),
               'NO_OBJECTS_FOR_COUNTRY');
    RETURN;
  END IF;

  RETURN QUERY
    SELECT o.attention_object_id, o.object_type, o.attention_state, o.blocker_text,
           rr.language, rr.requested_language, rr.fallback_used, rr.title, NULL::text
      FROM attention_object o
      LEFT JOIN LATERAL resolve_representation(o.attention_object_id, p_display_language) rr
             ON TRUE
     WHERE o.country = p_country AND o.attention_state = 'ATTENTION_READY';
END;
""",
},

'get_evidence': {
    'returns': """TABLE (
  evidence_id text,
  source_id text,
  source_backend source_backend,
  repository text,
  path text,
  commit_sha char(40),
  db_schema text,
  table_or_view text,
  primary_key text,
  source_location_country char(2),
  fact_location_country char(2),
  evidence_level evidence_level,
  original_text text,
  source_language language_code,
  translated_text text,
  translation_language language_code,
  translation_provenance text,
  display_language language_code,
  requested_language language_code,
  fallback_used text
)""",
    'body': """
BEGIN
  RETURN QUERY
    SELECT d.evidence_id, d.source_id, d.source_backend,
           d.repository, d.path, d.commit_sha,
           d.db_schema, d.table_or_view, d.primary_key,
           d.source_location_country, d.fact_location_country,
           d.evidence_level,
           -- ORIGINAL_TEXT nunca sofre fallback: vai na lingua da fonte, sempre
           d.original_text, d.source_language,
           t.translated_text, t.translation_language, t.translation_provenance,
           coalesce(t.translation_language, d.source_language) AS display_language,
           p_display_language,
           CASE WHEN t.translation_language IS NULL THEN 'NO_TRANSLATION_ORIGINAL_ONLY'
                WHEN t.translation_language = p_display_language THEN 'NO'
                ELSE 'YES' END
      FROM v_evidence_drawer d
      LEFT JOIN content_translation t
             ON t.canonical_entity_id = d.canonical_entity_id
            AND t.translation_language = p_display_language
     WHERE d.evidence_id = p_evidence_id;
END;
""",
},
}


# ── RLS ────────────────────────────────────────────────────────────────────

RLS = {
    'PAPEIS': {
        'publisher_role': 'escreve inteligencia canonica; so no backend, nunca no browser',
        'portal_reader': 'le o que o pais dele autoriza; escreve APENAS entry_path_event',
        'anon': 'nao le nada de inteligencia',
    },
    'HELPER': {
        'nome': 'allowed_countries',
        'sql': """
CREATE OR REPLACE FUNCTION allowed_countries() RETURNS char(2)[]
LANGUAGE sql STABLE AS $$
  -- Deny by default. Enquanto o modelo de identidade nao for decidido, a funcao
  -- devolve o que estiver na configuracao de sessao; sem configuracao, vazio.
  -- NAO inventa papel de usuario e NAO le claim de JWT que ainda nao existe.
  SELECT coalesce(
    string_to_array(nullif(current_setting('sintonia.countries', true), ''), ',')::char(2)[],
    ARRAY[]::char(2)[]
  );
$$;""",
        'porque': ('Uma politica que lesse um claim de JWT com formato ainda nao decidido '
                   'seria invencao. Esta funcao e exercitavel hoje via SET, nega por '
                   'padrao, e troca de implementacao sem mexer nas politicas.'),
    },
    'POLITICAS_AGORA': [
        {'nome': 'publisher_all', 'aplica_a': 'TODAS as tabelas', 'papel': 'publisher_role',
         'sql': "FOR ALL TO publisher_role USING (true) WITH CHECK (true)",
         'porque': 'o publisher e a unica coisa que escreve inteligencia canonica'},
        {'nome': 'portal_read_country', 'aplica_a': 'tabelas com coluna country',
         'papel': 'portal_reader',
         'sql': "FOR SELECT TO portal_reader USING (country = ANY (allowed_countries()))",
         'porque': 'isolamento por pais exercitavel; sem configuracao de sessao, nao le nada'},
        {'nome': 'portal_read_child', 'aplica_a': 'tabelas filhas sem country',
         'papel': 'portal_reader',
         'sql': ("FOR SELECT TO portal_reader USING (EXISTS (SELECT 1 FROM attention_object o "
                 "WHERE o.attention_object_id = attention_object_id "
                 "AND o.country = ANY (allowed_countries())))"),
         'porque': 'a filha herda o pais da raiz; nao precisa da coluna'},
        {'nome': 'portal_write_telemetry', 'aplica_a': 'entry_path_event',
         'papel': 'portal_reader',
         'sql': "FOR INSERT TO portal_reader WITH CHECK (true)",
         'porque': 'unica escrita do portal, e nao e inteligencia: e rota de entrada'},
    ],
    'BLOQUEADO_POR_DECISAO_DE_AUTENTICACAO': [
        'como o pais do usuario chega ate o banco (claim de JWT? tabela de membership?)',
        'multi-tenant: a coluna tenant_id nao entra antes de existir cliente multiplo',
        'auditoria de acesso: quem leu o que — entra quando houver usuario real',
    ],
    'REGRA_QUE_NAO_MUDA': ('SERVICE_ROLE_KEY nunca vai para o frontend. O navegador fala '
                           'com um servidor; o servidor fala com o Supabase.'),
}


def sincronizar():
    with open(SCHEMA, encoding='utf-8') as fh:
        d = json.load(fh)

    faltando = [v['name'] for v in d['VIEWS'] if v['name'] not in VIEWS]
    if faltando:
        raise SystemExit('views sem corpo: %s' % faltando)
    sobrando = [n for n in VIEWS if n not in {v['name'] for v in d['VIEWS']}]
    if sobrando:
        raise SystemExit('corpo para view inexistente: %s' % sobrando)

    for v in d['VIEWS']:
        v['body'] = VIEWS[v['name']].strip()
    for r in d['RPCS']:
        if r['name'] not in RPCS:
            raise SystemExit('RPC sem corpo: %s' % r['name'])
        r['returns_sql'] = RPCS[r['name']]['returns'].strip()
        r['body'] = RPCS[r['name']]['body'].strip()
    d['RLS'] = RLS

    with open(SCHEMA, 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(d, fh, ensure_ascii=False, indent=2)
        fh.write('\n')
    return len(d['VIEWS']), len(d['RPCS'])


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    if '--sync' not in sys.argv:
        print('use --sync'); raise SystemExit(1)
    nv, nr = sincronizar()
    print('corpos injetados: %d views, %d RPCs, RLS' % (nv, nr))
