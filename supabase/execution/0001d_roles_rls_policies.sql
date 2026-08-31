-- SINTONIA EAME · EXECUCAO EM PARTES · BLOCO D DE 5 (PAPEIS, RLS E POLITICAS)
--
-- GERADO por scripts/supabase_execution_split.py. Nao editar a mao.
--
-- ORIGEM: supabase/migrations/0001_initial_canonical_schema.sql
-- SHA256 DA ORIGEM: 41ffeb52941718a34a01135e2f76bc4611a2978e049175f90cf4014117e335ec
-- ALVO: xhqebdweltytnghiavew (eame-sintonia-dev)
--
-- PARA QUE: os papeis, o helper allowed_countries(), o RLS ligado em toda tabela e as politicas. O helper vem junto porque toda politica de pais chama ele.
--
-- ORDEM: rode a, b, c, d, e nesta ordem. Cada um abre e fecha a propria
-- transacao: se um falhar, ele volta inteiro e os anteriores ficam de pe.
--
-- O QUE E ANDAIME AQUI: este cabecalho, o BEGIN/COMMIT abaixo e o
-- SET search_path. Foram acrescentados porque cada arquivo roda numa
-- sessao propria. Tudo o que esta entre as duas marcas e fatia LITERAL
-- do arquivo canonico, byte a byte, e a prova de reconstrucao confere.

BEGIN;
SET search_path TO sintonia, public;

-- >>> CORPO CANONICO — FATIA LITERAL DE 0001, NAO EDITAR >>>


-- ── ROW LEVEL SECURITY ────────────────────────────────────────────────
-- Ligado em TODAS as tabelas. Uma tabela sem RLS num projeto Supabase fica
-- legivel pela chave anonima: o padrao seguro e negar e abrir depois.
--
-- Papeis:
--   publisher_role  escreve inteligencia canonica (service role, so no backend)
--   portal_reader   le o que o pais dele autoriza
--   anon            nao le nada de inteligencia
--
-- SERVICE_ROLE_KEY NUNCA vai para o frontend. O portal fala com um servidor,
-- e o servidor fala com o Supabase.

-- Papeis. Criados se nao existirem; NOLOGIN porque quem loga e a aplicacao.
DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'publisher_role')
  THEN CREATE ROLE publisher_role NOLOGIN; END IF;
END $$;  -- escreve inteligencia canonica; so no backend, nunca no browser
DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'portal_reader')
  THEN CREATE ROLE portal_reader NOLOGIN; END IF;
END $$;  -- le o que o pais dele autoriza; escreve APENAS entry_path_event
--   anon: nao le nada de inteligencia (nenhuma policy = nao le nada)

-- Uma politica que lesse um claim de JWT com formato ainda nao decidido seria invencao. Esta funcao e exercitavel hoje via SET, nega por padrao, e troca de implementacao sem mexer nas politicas.
CREATE OR REPLACE FUNCTION allowed_countries() RETURNS char(2)[]
LANGUAGE sql STABLE AS $$
  -- Deny by default. Enquanto o modelo de identidade nao for decidido, a funcao
  -- devolve o que estiver na configuracao de sessao; sem configuracao, vazio.
  -- NAO inventa papel de usuario e NAO le claim de JWT que ainda nao existe.
  SELECT coalesce(
    string_to_array(nullif(current_setting('sintonia.countries', true), ''), ',')::char(2)[],
    ARRAY[]::char(2)[]
  );
$$;

-- RLS ligado em TODAS as tabelas. Sem policy, o acesso e negado:
-- o padrao seguro e negar e abrir depois.
ALTER TABLE ontology_term ENABLE ROW LEVEL SECURITY;
ALTER TABLE ontology_term_label ENABLE ROW LEVEL SECURITY;
ALTER TABLE geo_anchor ENABLE ROW LEVEL SECURITY;
ALTER TABLE source ENABLE ROW LEVEL SECURITY;
ALTER TABLE source_snapshot ENABLE ROW LEVEL SECURITY;
ALTER TABLE source_clock ENABLE ROW LEVEL SECURITY;
ALTER TABLE source_provenance ENABLE ROW LEVEL SECURITY;
ALTER TABLE storage_provenance ENABLE ROW LEVEL SECURITY;
ALTER TABLE evidence ENABLE ROW LEVEL SECURITY;
ALTER TABLE content_entity ENABLE ROW LEVEL SECURITY;
ALTER TABLE content_translation ENABLE ROW LEVEL SECURITY;
ALTER TABLE attention_object ENABLE ROW LEVEL SECURITY;
ALTER TABLE attention_object_representation ENABLE ROW LEVEL SECURITY;
ALTER TABLE attention_readiness ENABLE ROW LEVEL SECURITY;
ALTER TABLE attention_object_evidence ENABLE ROW LEVEL SECURITY;
ALTER TABLE attention_object_unknown ENABLE ROW LEVEL SECURITY;
ALTER TABLE object_clock ENABLE ROW LEVEL SECURITY;
ALTER TABLE phenomenon_case ENABLE ROW LEVEL SECURITY;
ALTER TABLE regulatory_deadline_object ENABLE ROW LEVEL SECURITY;
ALTER TABLE competitor_identity_chain_object ENABLE ROW LEVEL SECURITY;
ALTER TABLE longitudinal_field_pressure_object ENABLE ROW LEVEL SECURITY;
ALTER TABLE observation ENABLE ROW LEVEL SECURITY;
ALTER TABLE territorial_observation ENABLE ROW LEVEL SECURITY;
ALTER TABLE registration ENABLE ROW LEVEL SECURITY;
ALTER TABLE registration_deadline ENABLE ROW LEVEL SECURITY;
ALTER TABLE product ENABLE ROW LEVEL SECURITY;
ALTER TABLE organization ENABLE ROW LEVEL SECURITY;
ALTER TABLE trademark_record ENABLE ROW LEVEL SECURITY;
ALTER TABLE competitor_product_identity ENABLE ROW LEVEL SECURITY;
ALTER TABLE observed_paid_activity ENABLE ROW LEVEL SECURITY;
ALTER TABLE company_local_account ENABLE ROW LEVEL SECURITY;
ALTER TABLE company_public_content ENABLE ROW LEVEL SECURITY;
ALTER TABLE field_pressure_series ENABLE ROW LEVEL SECURITY;
ALTER TABLE field_pressure_reading ENABLE ROW LEVEL SECURITY;
ALTER TABLE person ENABLE ROW LEVEL SECURITY;
ALTER TABLE scientific_person ENABLE ROW LEVEL SECURITY;
ALTER TABLE scientific_publication ENABLE ROW LEVEL SECURITY;
ALTER TABLE publication_author ENABLE ROW LEVEL SECURITY;
ALTER TABLE issue_expertise ENABLE ROW LEVEL SECURITY;
ALTER TABLE person_creator ENABLE ROW LEVEL SECURITY;
ALTER TABLE farm_business_entity ENABLE ROW LEVEL SECURITY;
ALTER TABLE creator_content_profile ENABLE ROW LEVEL SECURITY;
ALTER TABLE field_voice_observation ENABLE ROW LEVEL SECURITY;
ALTER TABLE local_adama_portfolio_context ENABLE ROW LEVEL SECURITY;
ALTER TABLE portfolio_product_ref ENABLE ROW LEVEL SECURITY;
ALTER TABLE convergence_proposition ENABLE ROW LEVEL SECURITY;
ALTER TABLE convergence_leg ENABLE ROW LEVEL SECURITY;
ALTER TABLE dependency_edge ENABLE ROW LEVEL SECURITY;
ALTER TABLE object_relation ENABLE ROW LEVEL SECURITY;
ALTER TABLE object_event ENABLE ROW LEVEL SECURITY;
ALTER TABLE action ENABLE ROW LEVEL SECURITY;
ALTER TABLE action_evidence ENABLE ROW LEVEL SECURITY;
ALTER TABLE entry_path_event ENABLE ROW LEVEL SECURITY;
ALTER TABLE publish_run ENABLE ROW LEVEL SECURITY;
ALTER TABLE publish_run_freeze ENABLE ROW LEVEL SECURITY;
ALTER TABLE shadow_validation ENABLE ROW LEVEL SECURITY;
ALTER TABLE ui_alias ENABLE ROW LEVEL SECURITY;

-- 1 · o publisher escreve; e a unica coisa que escreve inteligencia
CREATE POLICY publisher_all ON ontology_term FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON ontology_term_label FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON geo_anchor FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON source FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON source_snapshot FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON source_clock FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON source_provenance FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON storage_provenance FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON evidence FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON content_entity FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON content_translation FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON attention_object FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON attention_object_representation FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON attention_readiness FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON attention_object_evidence FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON attention_object_unknown FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON object_clock FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON phenomenon_case FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON regulatory_deadline_object FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON competitor_identity_chain_object FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON longitudinal_field_pressure_object FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON observation FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON territorial_observation FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON registration FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON registration_deadline FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON product FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON organization FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON trademark_record FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON competitor_product_identity FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON observed_paid_activity FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON company_local_account FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON company_public_content FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON field_pressure_series FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON field_pressure_reading FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON person FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON scientific_person FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON scientific_publication FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON publication_author FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON issue_expertise FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON person_creator FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON farm_business_entity FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON creator_content_profile FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON field_voice_observation FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON local_adama_portfolio_context FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON portfolio_product_ref FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON convergence_proposition FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON convergence_leg FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON dependency_edge FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON object_relation FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON object_event FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON action FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON action_evidence FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON entry_path_event FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON publish_run FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON publish_run_freeze FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON shadow_validation FOR ALL TO publisher_role USING (true) WITH CHECK (true);
CREATE POLICY publisher_all ON ui_alias FOR ALL TO publisher_role USING (true) WITH CHECK (true);

-- 2 · o portal le so o pais autorizado. Sem SET, allowed_countries()
--     devolve vazio e nenhuma linha passa.
CREATE POLICY portal_read_country ON geo_anchor FOR SELECT TO portal_reader USING (country = ANY (allowed_countries()));
CREATE POLICY portal_read_country ON source FOR SELECT TO portal_reader USING (country = ANY (allowed_countries()));
CREATE POLICY portal_read_country ON attention_object FOR SELECT TO portal_reader USING (country = ANY (allowed_countries()));
CREATE POLICY portal_read_country ON registration FOR SELECT TO portal_reader USING (country = ANY (allowed_countries()));
CREATE POLICY portal_read_country ON organization FOR SELECT TO portal_reader USING (country = ANY (allowed_countries()));
CREATE POLICY portal_read_country ON competitor_product_identity FOR SELECT TO portal_reader USING (country = ANY (allowed_countries()));
CREATE POLICY portal_read_country ON field_pressure_series FOR SELECT TO portal_reader USING (country = ANY (allowed_countries()));
CREATE POLICY portal_read_country ON person FOR SELECT TO portal_reader USING (country = ANY (allowed_countries()));
CREATE POLICY portal_read_country ON farm_business_entity FOR SELECT TO portal_reader USING (country = ANY (allowed_countries()));
CREATE POLICY portal_read_country ON field_voice_observation FOR SELECT TO portal_reader USING (country = ANY (allowed_countries()));
CREATE POLICY portal_read_country ON local_adama_portfolio_context FOR SELECT TO portal_reader USING (country = ANY (allowed_countries()));
CREATE POLICY portal_read_country ON entry_path_event FOR SELECT TO portal_reader USING (country = ANY (allowed_countries()));

-- 3 · a tabela filha herda o pais da raiz, sem repetir a coluna
CREATE POLICY portal_read_child ON attention_object_representation FOR SELECT TO portal_reader USING (EXISTS (SELECT 1 FROM attention_object o WHERE o.attention_object_id = attention_object_representation.attention_object_id AND o.country = ANY (allowed_countries())));
CREATE POLICY portal_read_child ON attention_readiness FOR SELECT TO portal_reader USING (EXISTS (SELECT 1 FROM attention_object o WHERE o.attention_object_id = attention_readiness.attention_object_id AND o.country = ANY (allowed_countries())));
CREATE POLICY portal_read_child ON attention_object_evidence FOR SELECT TO portal_reader USING (EXISTS (SELECT 1 FROM attention_object o WHERE o.attention_object_id = attention_object_evidence.attention_object_id AND o.country = ANY (allowed_countries())));
CREATE POLICY portal_read_child ON attention_object_unknown FOR SELECT TO portal_reader USING (EXISTS (SELECT 1 FROM attention_object o WHERE o.attention_object_id = attention_object_unknown.attention_object_id AND o.country = ANY (allowed_countries())));
CREATE POLICY portal_read_child ON object_clock FOR SELECT TO portal_reader USING (EXISTS (SELECT 1 FROM attention_object o WHERE o.attention_object_id = object_clock.attention_object_id AND o.country = ANY (allowed_countries())));
CREATE POLICY portal_read_child ON phenomenon_case FOR SELECT TO portal_reader USING (EXISTS (SELECT 1 FROM attention_object o WHERE o.attention_object_id = phenomenon_case.attention_object_id AND o.country = ANY (allowed_countries())));
CREATE POLICY portal_read_child ON regulatory_deadline_object FOR SELECT TO portal_reader USING (EXISTS (SELECT 1 FROM attention_object o WHERE o.attention_object_id = regulatory_deadline_object.attention_object_id AND o.country = ANY (allowed_countries())));
CREATE POLICY portal_read_child ON competitor_identity_chain_object FOR SELECT TO portal_reader USING (EXISTS (SELECT 1 FROM attention_object o WHERE o.attention_object_id = competitor_identity_chain_object.attention_object_id AND o.country = ANY (allowed_countries())));
CREATE POLICY portal_read_child ON longitudinal_field_pressure_object FOR SELECT TO portal_reader USING (EXISTS (SELECT 1 FROM attention_object o WHERE o.attention_object_id = longitudinal_field_pressure_object.attention_object_id AND o.country = ANY (allowed_countries())));
CREATE POLICY portal_read_child ON convergence_proposition FOR SELECT TO portal_reader USING (EXISTS (SELECT 1 FROM attention_object o WHERE o.attention_object_id = convergence_proposition.attention_object_id AND o.country = ANY (allowed_countries())));
CREATE POLICY portal_read_child ON object_event FOR SELECT TO portal_reader USING (EXISTS (SELECT 1 FROM attention_object o WHERE o.attention_object_id = object_event.attention_object_id AND o.country = ANY (allowed_countries())));
CREATE POLICY portal_read_child ON action FOR SELECT TO portal_reader USING (EXISTS (SELECT 1 FROM attention_object o WHERE o.attention_object_id = action.attention_object_id AND o.country = ANY (allowed_countries())));

-- 4 · a UNICA escrita do portal, e nao e inteligencia: rota de entrada
CREATE POLICY portal_write_telemetry ON entry_path_event FOR INSERT TO portal_reader WITH CHECK (true);
-- <<< FIM DO CORPO CANONICO <<<

COMMIT;
