-- ═══════════════════════════════════════════════════════════════════════
-- PROTÓTIPO DA FASE 10 — E ELE NÃO É UMA MIGRATION.
--
--     NÃO EXECUTADA EM PRODUCAO
--     NAO E MIGRATION · NAO ENTRA NO LIVRO-RAZAO · NAO E APLICADA POR NINGUEM
--
-- Vive em `supabase/ensaios/` de propósito. O aplicador da casa
-- (`motor/cadeia_canonica.sh`) varre `supabase/migrations/*.sql` e mais nada;
-- um ficheiro aqui não pode ser aplicado por engano.
--
--     PROTOTIPO QUE MORA NA PASTA DAS MIGRATIONS E UMA MIGRATION
--     QUE AINDA NAO FOI APLICADA. E ISSO NAO E UM PROTOTIPO.
--
-- O número que a fase 10 vai usar, quando for autorizada: `027`. Medido nas
-- 104 branches remotas, uma a uma, e não assumido.
--
-- O QUE ISTO PROPÕE
-- -----------------
-- Depois da 026 a observação tem estado e a idempotência forward tem índice.
-- Falta a espécie: `unique (raw_asset.storage_path)` continua de pé, e
-- enquanto estiver, duas observações no mesmo endereço são UMA.
--
--     OBSERVAÇÃO   um facto sobre o mundo, com corrida e hora
--     OBJETO       uma cópia guardada, com endereço
--
-- Medido em `provas/a_lei_da_fase_10.py`, caso `C2`:
--
--     C2_A_OBSERVACAO_NOVA_ENTRA = NAO
--     C2_QUEM_A_IMPEDE           = raw_asset_storage_path_key
-- ═══════════════════════════════════════════════════════════════════════

begin;

-- ── PASSO 1 · o endereço deixa de ser identidade da observação ──────────
-- `ACCESS EXCLUSIVE` na tabela inteira. Medido: um escritor a meio de uma
-- transacção põe este DDL à espera, e ele só passa depois do `commit` dele.
-- Numa tabela de 252 linhas a espera é pelo LOCK, nunca pelo tamanho.
alter table public.raw_asset
  drop constraint raw_asset_storage_path_key;

-- ── PASSO 2 · a identidade da TENTATIVA ─────────────────────────────────
-- Sem isto, o `FORWARD_IDENTITY_UNPROVEN` fica sem chave nenhuma: o índice da
-- fase 9 tem predicado `FORWARD_IDENTIFIED`, e uma linha sem prova não o
-- satisfaz. Medido — duplica no retry, e duas sessões simultâneas duplicam-na
-- na mesma.
--
-- SEIS CANDIDATAS, DEZ CENÁRIOS, CADA UMA INSTALADA COMO ÍNDICE A SÉRIO:
--
--     K1 (run, fonte, sha256)              REPROVADA — junta o caso ADAMA
--     K3 (fonte, sha256)                   REPROVADA — apaga a corrida nova
--     K2 (run, fonte, endereço)            passa tudo, e MORRE na fase 11
--     K4 (run, fonte, endereço, sha256)    passa tudo, e MORRE na fase 11
--     K5 (run, fonte, objeto)              REPROVADA — sem objecto, não constrange
--     K6 (run, fonte, objeto, sha256)      APROVADA, com `nulls not distinct`
--
-- K1 morre no contraexemplo que esta casa mediu nos 195 objectos italianos: a
-- ADAMA publicou o MESMO PDF em `media/731` e em `media/6321`. Dois factos
-- sobre o mundo, um conteúdo só.
--
--     O CONTEUDO NAO E O DOCUMENTO. NUNCA FOI.
--
-- ⚠️ E `storage_object_id`, E NAO `storage_path`. As duas separam os mesmos
-- casos hoje. A diferença é a fase 11, que retira o endereço de `raw_asset`:
-- uma chave construída sobre ele nasceria com dívida marcada. O objecto é a
-- espécie certa para responder «que cópia física foi esta».
--
-- ⚠️ `NULLS NOT DISTINCT` NAO E AFINACAO. Uma observação NÃO preservada tem
-- `storage_object_id` nulo, e em Postgres dois nulos são distintos num índice
-- único: a chave deixaria passar TODAS as tentativas não preservadas, em
-- silêncio. Medido — `K6` sem isto reprova exactamente nesse cenário.
create unique index raw_tentativa_sem_prova_idx
  on public.raw_asset (run_id, source_id, storage_object_id, sha256)
  nulls not distinct
  where identity_state = 'FORWARD_IDENTITY_UNPROVEN';

-- ── PASSO 3 · a afirmação de identidade não se reescreve ────────────────
-- Medido: hoje NADA no esquema impede um `update` de promover uma observação
-- sem prova a identificada, nem de lhe trocar a fonte, a chave ou a base da
-- chave. Isso diz, em retrospectiva, que se sabia o que não se sabia.
--
--     UMA OBSERVACAO E UM FACTO SOBRE UM MOMENTO.
--     UM FACTO SOBRE UM MOMENTO NAO MELHORA COM O TEMPO.
--
-- OS CAMPOS CONGELADOS SÃO SETE, e a regra que os escolhe cabe numa frase:
-- **a afirmação de identidade, mais tudo o que as duas chaves de idempotência
-- usam.** Nada mais, porque congelar por medo fecharia o que tem de mudar.
--
--     identity_state  source_id  document_key  document_key_basis   a afirmação
--     run_id  sha256  storage_object_id                             as chaves
--
-- E `storage_path` NAO ESTA NA LISTA. Essa ausência é a prova de coerência do
-- desenho inteiro: ele é ENDEREÇO, e um endereço pode mudar sem que o facto
-- mude. Se ele estivesse aqui, a fase 11 teria de o tirar outra vez.
--
-- O QUE CONTINUA A PODER MUDAR, e tem de poder:
--     attempts · last_attempt_at   a contagem da tentativa
--     preserved · not_preserved_reason   o byte pode chegar depois
--     source_url · media_type · bytes · captured_at   anotações da captura
create or replace function public.a_identidade_da_observacao_nao_se_reescreve()
returns trigger language plpgsql as $$
declare
  mudou text;
begin
  select string_agg(campo, ', ' order by campo) into mudou from (
    select 'identity_state' as campo
      where old.identity_state     is distinct from new.identity_state
    union all select 'source_id'
      where old.source_id          is distinct from new.source_id
    union all select 'document_key'
      where old.document_key       is distinct from new.document_key
    union all select 'document_key_basis'
      where old.document_key_basis is distinct from new.document_key_basis
    union all select 'run_id'
      where old.run_id             is distinct from new.run_id
    union all select 'sha256'
      where old.sha256             is distinct from new.sha256
    union all select 'storage_object_id'
      where old.storage_object_id  is distinct from new.storage_object_id
  ) t;
  if mudou is not null then
    raise exception 'FASE 10: a identidade da observacao % nao se reescreve '
                    '(tentou mudar: %). Uma corrida que PROVE outra coisa '
                    'escreve uma observacao NOVA.', old.id, mudou;
  end if;
  return new;
end $$;

create trigger a_identidade_da_observacao_nao_se_reescreve
  before update on public.raw_asset
  for each row
  execute function public.a_identidade_da_observacao_nao_se_reescreve();

commit;

-- ═══════════════════════════════════════════════════════════════════════
-- O QUE ESTE PROTÓTIPO **NÃO** FAZ, e não é esquecimento
-- -----------------------------------------------------------------------
-- Não toca em `derived_artifact`. A derivação é por CONTEÚDO
-- (`derivacao_e_unica_por_regua` tem `parent_sha256` na chave, não
-- `raw_asset_id`), e continua a ser: derivar duas vezes os mesmos bytes com a
-- mesma régua daria o mesmo ficheiro. A consequência — a segunda observação
-- dos mesmos bytes não tem filhos próprios — está medida e documentada, e não
-- é defeito.
--
-- Não retira `raw_asset.storage_path`. Isso é a fase 11, e nada aqui a
-- antecipa: a chave do passo 2 já não depende dele.
-- ═══════════════════════════════════════════════════════════════════════
