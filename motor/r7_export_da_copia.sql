-- RODADA 7 · EXPORT DA COPIA DA SALA — SO LEITURA.
--
-- Corre-se DENTRO de `begin transaction read only` (RUNBOOK-R7.md §2) e com
-- PGOPTIONS=-c default_transaction_read_only=on: duas travas, e nenhuma
-- escrita possivel nesta sessao. Nunca contra a Sala canonica: so a COPIA.
--
-- Le a vista `sala_de_espera_atual` (migration 033: o que a Intelligence le,
-- ultima revisao senao o original) e, pelo RAW_OBSERVATION_ID, o endereco da
-- prova no `raw_asset` (source_url, document_key). Nada e completado aqui: o
-- que for null vai null, e o motor escreve NAO SEI.
--
-- D-GER-2 (diretiva do Intelligence owner, 29/09): a identidade do BYTE da prova
-- (raw_asset.sha256 e storage_path, migration 001) le-se aqui, no mesmo left
-- join. E o do banco ou e NAO SEI: nunca calculado do texto, da URL ou do disco.
--
-- Contrato da saida: SALA_ATUAL_READ_ONLY/v1, lido por
-- motor/motor_das_capacidades.py::entrada_do_export.
select json_build_object(
  'EXPORT',    'SALA_ATUAL_READ_ONLY/v1',
  'SINTETICO', false,
  'CORTE',     now(),
  'ORIGEM',    'copia local da Sala · base ' || current_database(),
  'READ_ONLY', current_setting('transaction_read_only'),
  'LINHAS',    coalesce(json_agg(t order by t.run_id, t.ordem), '[]'::json))
from (
  select a.run_id, a.ordem, a.item_id, a.raw_observation_id, a.universo, a.texto,
         a.source_id, a.source_location, a.source_location_basis,
         a.fact_location, a.fact_location_basis, a.fact_time, a.fact_time_basis,
         a.published_at, a.published_at_basis, a.observed_at,
         a.completude_tempo_lugar, a.janela_declarada, a.tempo_lugar_evidencia,
         a.captured_at, a.admitido_por, a.estagio,
         a.source_declared_evidence_class, a.fato,
         r.source_url         as raw_source_url,
         r.document_key       as raw_document_key,
         r.document_key_basis as raw_document_key_basis,
         r.sha256             as raw_sha256,
         r.storage_path       as raw_storage_path
    from public.sala_de_espera_atual a
    left join public.raw_asset r on r.id = a.raw_observation_id
) t;
